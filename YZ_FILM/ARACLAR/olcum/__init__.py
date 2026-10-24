"""ÖLÇÜM — görüntü ölçüm paketi: tek arayüz olc(gorsel, beklenen) → sözlük (TASARIM §6.5, D-16, [GS2] §4.6.1).

Kodda:
  import olcum
  y = olcum.olc("SIRALI_GORSEL/_ADAYLAR/071_a.jpg", beklenen={...}, arka=None)   # arka: "sahte" | "gercek" | None (kendiliğinden)
  y["yuz_sayisi"], y["kimlik"]["mara"]["benzerlik"], y["olculemedi"] → {alan: neden}
  olcum.esik("g1_kimlik_hata") → 0.363 (veri/sureklilik_esikleri.json; okunamazsa yerleşik değer)
  olcum.arka_sec(film) → "sahte" ya da "gercek"
Arka uçlar (her biri ayrı modül; kurulu değilse alanı ÖLÇÜLEMEDİ yazar, asla GEÇ uydurmaz):
  teknik  (PIL + numpy; her yerde): en-boy, çözünürlük, keskinlik (Laplacian varyansı), parlaklık
  isik    (numpy): Lab ortalaması, ΔE, yanak parlaklık oranı → ışığın kadrajdaki yönü
  kimlik  (opencv FaceDetectorYN/FaceRecognizerSF = YuNet + SFace; Apache-2.0): yüzler, 128 boyutlu vektör, kadro bankasıyla Macar
          eşlemesi (scipy varsa linear_sum_assignment, yoksa küçük kadroda tam arama), fark payı, kadraj sırası ve üçte bir
  gorunum (torch + transformers, yerel önbellekten, HF_HUB_OFFLINE): DINOv2-small, CLIP "photograph" olasılığı, OWLv2 nesne kutusu
  poz     (mediapipe Face/Pose Landmarker .task dosyaları): yaw, jawOpen, bilek–nesne; yoksa YuNet noktalarından yaklaşık yaw (BAYRAK düzeyi)
Sahte arka uç (test ve --saglayici sahte): görselin yan dosyasındaki ("<gorsel>.json" → "gercek") değerleri döndürür; yan dosyada olmayan
  alan ÖLÇÜLEMEDİ'dir. Gerçek ve sahte çıktı aynı şemadadır.
Model dosyaları: YZ_FILM_MODELLER ortam değişkeni ya da <onbellek>/modeller/ (ortak.yollar()["onbellek"]); indirme kurulumun işidir.
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import ortak

SURUM = "olcum 1.0"
ALANLAR = ("teknik", "isik", "kimlik", "gorunum", "poz")
VARSAYILAN = {
    "g1_en_boy_tolerans": 0.01, "g1_kisa_kenar_min": 720, "g1_yunet_skor_min": 0.9, "g1_yuz_min_px": 48, "g1_arka_yuz_oran_max": 0.04,
    "g1_kimlik_gec": 0.45, "g1_kimlik_hata": 0.363, "g1_kimlik_fark_payi_min": 0.05, "g1_yaw_max_derece": 15, "g1_jaw_open_max": 0.15,
    "g1_konusan_yuz_oran_min": 0.12, "g1_konusan_yaw_max": 45, "g1_parmak_el_oran_min": 0.15, "g1_yaratik_dinov2_min": 0.5,
    "g1_olcek_tolerans": 0.35, "g1_mekan_dinov2_min": 0.6, "g1_isik_yanak_oran_min": 1.25, "g1_lab_de_max": 10,
    "g1_stil_clip_foto_min": 0.5, "g1_keskinlik_oran_min": 0.5, "g1_aday_sayisi": 2, "g1_duzeltme_tur_max": 2,
    "kart_oz_tutarlilik_gec": 0.45, "kart_kadro_ayrisma_hata": 0.363, "kart_kadro_ayrisma_hedef": 0.25, "kart_aday_sayisi": 3,
    "kart_tur_max": 2, "kart_uzun_kenar_min": 1376, "kart_gorunum_sayisi": 6, "kart_fon_std_max": 18, "kart_yaratik_isaret_min": 3,
    "kor_gorev_gorsel_max": 12, "duzeltme_kirpma_kenar_max_oran": 0.1, "duzeltme_renk_de_max": 15, "gemini_paket_plan_max": 30,
    "gemini_ek_dosya_max": 10, "kapak_aday_max": 12, "kapak_aday_min": 8, "kapak_kucuk_okunurluk": [168, 94],
    "ifade_uyum_min_oran": 0.85, "animatik_tur1_yer_tutucu_max_oran": 0.15, "referans_max": 2,
}
_E = {}
GEVSETILEMEZ_TABAN = {"g1_kimlik_hata": 0.363, "kart_kadro_ayrisma_hata": 0.363}


def esik(ad):
    """Eşik değeri (esikler.yukle; yoksa yerleşik). Kimlik HATA sınırı hiçbir koşulda 0,363'ün altına inmez."""
    if not _E:
        try:
            import esikler
            E = esikler.yukle(); _E.update({k: E[k] for k in VARSAYILAN if k in E}); _E["_kaynak"] = "esikler"
        except Exception as e:
            _E["_kaynak"] = f"yerlesik ({e.__class__.__name__})"
    v = _E.get(ad, VARSAYILAN.get(ad))
    if ad == "g1_kimlik_hata" and isinstance(v, (int, float)): v = max(v, GEVSETILEMEZ_TABAN[ad])
    if ad == "kart_kadro_ayrisma_hata" and isinstance(v, (int, float)): v = min(v, GEVSETILEMEZ_TABAN[ad])
    return v


def model_klasoru():
    if os.environ.get("YZ_FILM_MODELLER"): return os.environ["YZ_FILM_MODELLER"]
    try: return os.path.join(ortak.yollar()["onbellek"], "modeller")
    except Exception: return os.path.join(os.path.expanduser("~"), ".cache", "yz_film", "modeller")


def arka_sec(film=None):
    a = os.environ.get("YZ_FILM_OLCUM")
    if a in ("sahte", "gercek"): return a
    if film:
        h = ortak.json_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}
        if h.get("saglayici") == "sahte": return "sahte"
    return "gercek"


def yan_dosya(gorsel): return os.path.splitext(gorsel)[0] + ".json"


def ucte_bir(x_merkez, genislik):
    r = x_merkez / float(genislik or 1)
    return "sol" if r < 1 / 3 else ("orta" if r < 2 / 3 else "sag")


def ucte_bir_normal(s):
    """_derlenir.kadraj_konumu ('sag_ucte_bir', 'kadraj_solu', 'orta') ve kör cevapları ('left third') → sol | orta | sag | None."""
    if not s: return None
    t = str(s).lower()
    if "sol" in t or "left" in t: return "sol"
    if "sag" in t or "sağ" in t or "right" in t: return "sag"
    if "orta" in t or "middle" in t or "center" in t or "centre" in t: return "orta"
    return None


def _sahte(gorsel, beklenen):
    yan = ortak.json_oku(yan_dosya(gorsel), {}) or {}
    g = dict(yan.get("gercek") or {})
    out = {"arka": "sahte", "gorsel": gorsel, "olculemedi": {}}
    for k, v in g.items(): out[k] = v
    if "teknik" not in out:
        from olcum import teknik
        out["teknik"] = teknik.olc(gorsel)
    zorunlu = ("yuz_sayisi", "kimlik", "kadraj_sirasi")
    for k in zorunlu:
        if k not in out: out["olculemedi"][k] = "sahte yan dosyada yok"
    for k, v in (g.get("olculemedi") or {}).items(): out["olculemedi"][k] = v
    return out


def olc(gorsel, beklenen=None, arka=None, banka=None, film=None):
    """Tek görselin bütün yerel ölçümleri. beklenen: {karakterler: [id], insan: [id], yaratik: [id], nesneler: [{id, sorgu}],
    ebeveyn: <yol>, sahne_ilk: <yol>, yuz_acisi: {id: on|3/4|profil|sirt|gorunmez}}. banka: {id: [[128 sayı], …]} ya da .npz yolları.
    Dönüş: teknik, isik, yuzler, yuz_sayisi, kimlik, eslesme, kadraj_sirasi, ucte_bir, yaw, jaw_open, el_nesne, mekan_dinov2,
    yaratik_dinov2, stil_clip_foto, lab_de_sahne, olculemedi {alan: neden}."""
    beklenen = beklenen or {}
    arka = arka or arka_sec(film)
    if arka == "sahte": return _sahte(gorsel, beklenen)
    from olcum import teknik, isik, kimlik, gorunum, poz
    out = {"arka": "gercek", "gorsel": gorsel, "olculemedi": {}}
    out["teknik"] = teknik.olc(gorsel)
    out["isik"] = isik.olc(gorsel)
    for mod, ad in ((kimlik, "kimlik"), (gorunum, "gorunum"), (poz, "poz")):
        try: mod.olc_ekle(gorsel, beklenen, banka, out)
        except Exception as e:                    # bir arka ucun çökmesi ölçümü durdurmaz; alan ÖLÇÜLEMEDİ olur
            out["olculemedi"][ad] = f"{e.__class__.__name__}: {str(e)[:160]}"
    try: isik.yuz_isigi_ekle(gorsel, out)
    except Exception as e: out["olculemedi"]["isik_yon"] = f"{e.__class__.__name__}"
    if beklenen.get("sahne_ilk") and os.path.isfile(beklenen["sahne_ilk"]):
        out["lab_de_sahne"] = round(isik.delta_e(gorsel, beklenen["sahne_ilk"]), 2)
    return out


def durum():
    """Kurulu arka uçlar (kurulum ve A10a raporu için)."""
    from olcum import kimlik, gorunum, poz
    return {"kimlik": kimlik.hazir(), "gorunum": gorunum.hazir(), "poz": poz.hazir(), "model_klasoru": model_klasoru()}
