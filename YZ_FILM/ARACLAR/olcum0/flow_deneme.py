"""FLOW DENEME — Ö0-b: Flow/Omni'nin günlük UYARISIZ kapasitesi (merdivenli protokol) + istem biçimi A/B'leri için çekim
(TASARIM §1.2 Ö0-b, D-04, D-05, D-13, D-15, §10.4; §9 adım 9).

GÜVENLİK (pazarlıksız):
  - Her gönderim Memmet v2 blok yolundan gider (memmet.py'nin Memmet sınıfı; sayfaya dokunan her işlem Memmet.dokun'dan; varsayılan ve
    TEK kip `elle`: GÖNDER'e kullanıcı basar). Her klip için bütçe noktası (kredi.butk, BUTK) ve kredi defteri satırı GÖNDERİMDEN ÖNCE.
  - İLK Flow uyarısında (Memmet çıkış 7, FLOW_KILIDI.json ya da FLOW_UYARILARI.jsonl'de ölçüm başladıktan sonraki bir satır) ve doğrulama
    (reCAPTCHA) görülünce Ö0-b BÜTÜNÜYLE KAPANIR: yeniden deneme, sayfa yenileme, başka hesap yok; o gün ve sonraki 7 gün (o0b_uyari_sonrasi_ara_gun)
    Flow ölçümü yok. Kapasite = uyarıdan önceki en yüksek uyarısız günün video sayısı (alt sınır, en çok 20); uyarısız gün yoksa "ölçülemedi".
  - Hiçbir şey uyarıyı ya da politika reddini kasıtlı tetiklemez: istemler filtre taramasından HATA'sız (fikstur_denetim), yedek istem yok,
    reddedilen klip yeniden gönderilmez; yalnız KENDİLİĞİNDEN gelen ret kaydedilir (kredi etkisi bakiyeden).
  - Merdiven yalnız uyarısız ve TAM biten günden sonra bir basamak çıkar (10 → 15 → 20, hat_esikleri o0b_gun_tavanlari); takvim günü başına
    bir ölçüm günü; o gün hesaptan başka video gitmişse ölçüm günü açılmaz.
  - Klipler <veri>/BILGI/OLCUM0/O0b_klipler/ altında saklanır (Ö0-2 / Ö0-b·V3 değerlendirmesi bunlarla; yeniden çekim yok).

Kullanım (film.py olcum0 calis b … ile ya da doğrudan):
  python flow_deneme.py durum [--json]                        ölçümün durumu ve sıradaki adım (hiçbir şey değiştirmez)
  python flow_deneme.py denetle-fikstur [<dosya>] [--b3-kok <B3>]   fikstür denetimi (fikstur/fikstur_denetim.py; salt okur)
  python flow_deneme.py hazirla --b3-kok <B3 klasörü> [--fikstur <yol>]
        fikstürü denetler (şablon reddedilir), ölçüm klasörünü kurar (<veri>/BILGI/OLCUM0/O0b_FILM/), B3 karelerini SHA1 ile kopyalar
  python flow_deneme.py gun [--bakiye N] [--kuru]             bugünün merdiven basamağını açar ve Memmet'le (elle) gönderir; uzun sürer
        (GÖNDER'leri kullanıcı basar). --kuru: hiçbir şey göndermeden bugünün planını yazar. Bakiye verilmezse Memmet salt okur (--bakiye).
  python flow_deneme.py kare-olc                               zincir karesi kalitesi (keskinlik oranı) indirilen kliplerde
  python flow_deneme.py kapat [--neden <metin>] [--beyan <N>]  Ö0-b'yi elle kapatır (sonuç o ana kadarki uyarısız günlerden).
        --beyan N: KULLANICI KARARI — merdiven bırakılır, günlük kapasite kullanıcının beyanından (N video/gün) alınır
        (ölçüm değil; kapasite_kaynagi "kullanici_beyani"). Uyarı kayıtlıysa beyan alınmaz. Flow uyarısında durma kuralı değişmez.
  python flow_deneme.py rapor                                  O0b.json özetini ve OLCUM0.json'u yeniden yazar
  python flow_deneme.py memmet-blok <film> --blok <id> --onizleme <imza> --mod elle    (iç: Memmet'in Ö0-b sarmalayıcısı)
Çıkış kodları: 0 tamam · 1 HATA · 2 KULLANICI (fiziksel iş / ön koşul) · 4 ORTAM (bulut, şablon fikstür) · 5 BÜTÇE ·
               7 KISIT (Flow uyarısı: Ö0-b kapandı) · 8 BEKLE (yarın / 7 gün / toplanacak klip).
"""
import os, sys, re, json, time, math, shutil, hashlib, datetime, statistics, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for _p in (ARACLAR, HERE, os.path.join(HERE, "fikstur")):
    if _p not in sys.path: sys.path.insert(0, _p)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import ortak, ortak_o0 as o0, fikstur_denetim as fd

SURUM = "flow_deneme 1.0"
BITTI, HATA, KULLANICI, ORTAM, BUTCE, KISIT, BEKLE = 0, 1, 2, 4, 5, 7, 8
FILM_AD = "O0B_OLCUM"
KREDI_TAVAN = 540                       # TASARIM §1.2 Ö0-b: ≤ 540 kr (45 × 12)
VARSAYILAN_KARAR = {"istem_bicimi": "aralik", "bekleme": "holds still", "son_kare_ref": "yok", "zincir_kare": "dogal_1280x720"}
ETKENLER = {"istem_bicimi": ("aralik", "sira"), "bekleme": ("holds still", "holds the pose, breathing"),
            "son_kare_ref": ("var", "yok"), "zincir_kare": ("dogal_1280x720", "1376x774_kirp3")}
UYARI_KODLARI = ("olagandisi", "kilitli", "dogrulama")      # Memmet _memmet_cikis.json kodu → Ö0-b kapanır
BAKIYE_TAZE_SN = 2 * 3600


class Dur(Exception):
    def __init__(self, msg, kod=HATA, **ek): super().__init__(msg); self.kod = kod; self.ek = ek


# ---------------------------------------------------------------- yollar ve durum
def film_yolu(): return os.path.join(o0.kok(), "O0b_FILM")
def klip_kok(): return os.path.join(o0.kok(), "O0b_klipler")
def hesap(): return ortak.yollar()["hesap"]
def _tarih(t): return time.strftime("%Y-%m-%d", time.localtime(t))
def saat(): return time.time()            # testler yamalar (tek saat noktası)
def _simdi(s): return saat() if s is None else float(s)
def _sha1(yol): return fd._sha1(yol)


def tavanlar(): return list(o0.esik("o0b_gun_tavanlari", [10, 15, 20]))
def ara_gun(): return int(o0.esik("o0b_uyari_sonrasi_ara_gun", 7))
def ab_min(): return int(o0.esik("ab_kol_min_ornek", 12))
def kredi_klip(): return int(o0.esik("kredi_klip_720p", 12) or 12)
def guvenlik_payi(): return float(o0.esik("guvenlik_payi", 0.1) or 0.0)


def durum_oku():
    d = o0.oku("b")
    return d if d else {}


def durum_yaz(d):
    """O0b.json + OLCUM0.O0b. Kapanmadan önce olculen_gunluk_kapasite ve olculemedi ANAHTARLARI yazılmaz (olcek.kapasite kuralı)."""
    if d.get("durum") != "kapandi":
        d.pop("olculen_gunluk_kapasite", None); d.pop("olculemedi", None)
    return o0.yaz("b", d, arac=SURUM)


# ---------------------------------------------------------------- ön koşullar ve uyarı denetimi
def on_kosul():
    """TASARIM §1.2 Ö0-b ön koşulu: §9 adım 2 bitti (veri kökü emniyeti + memmet3 birleşti + Ö0-a). [eksik neden] listesi."""
    n = []; v = ortak.yollar()["veri_kok"]
    r = ortak.json_oku(os.path.join(v, "_ESKI", "EMNIYET_RAPORU.json"), None)
    if not isinstance(r, dict): n.append("veri kökü emniyeti yapılmadı (kurulum.py --veri-emniyet; EMNIYET_RAPORU.json yok)")
    elif r.get("kalan_giris_noktasi"): n.append("yamasız Memmet'e giden giriş noktası var (EMNIYET_RAPORU.json kalan_giris_noktasi)")
    if o0.durum("a") not in o0.BITMIS:
        n.append("ilk yerel oturum (memmet3 aktarımı + Ö0-a) bitmedi: O0a.json yok — Ö0-b memmet3 birleşmeden başlamaz")
    return n


def uyari_bul(d, simdi=None, kok=None):
    """Ölçüm başladıktan sonra hesapta bir uyarı ya da kilit var mı? (sözlük | None). Salt okur."""
    import flow_yuk
    kok = kok or hesap(); bas = float(d.get("baslangic_epoch") or 0)
    k = flow_yuk.kilit_durumu(kok=kok, simdi=simdi)
    if k.get("kilitli"):
        return {"kaynak": "FLOW_KILIDI", "neden": k.get("neden"), "zaman_epoch": k.get("son_uyari") or k.get("zaman")}
    for u in flow_yuk.uyarilar_oku(kok):
        if bas and u["zaman_epoch"] >= bas - 1:
            return {"kaynak": "FLOW_UYARILARI", "neden": "olagandisi", "zaman_epoch": u["zaman_epoch"]}
    return None


def yakin_uyari(simdi=None, kok=None):
    """Ölçüm başlamadan önce: son ara_gun gün içinde uyarı varsa onun zamanı (epoch), yoksa None."""
    import flow_yuk
    s = _simdi(simdi); z = [u["zaman_epoch"] for u in flow_yuk.uyarilar_oku(kok or hesap()) if u["zaman_epoch"] > s - ara_gun() * 86400]
    return max(z) if z else None


# ---------------------------------------------------------------- fikstür
def fikstur_yukle(yol=None, b3_kok=None):
    kaynak = "verilen"
    if not yol: yol, kaynak = fd.varsayilan_yol()
    if not yol or not os.path.isfile(yol):
        raise Dur("Ö0-b istem fikstürü yok (olcum0/fikstur/O0b_istemler_v1.json). İlk yerel oturumda B3 karelerinden yazılır "
                  "(olcum0/BENIOKU.md).", KULLANICI)
    try: doc = fd.oku(yol)
    except ValueError as e: raise Dur(f"fikstür JSON bozuk: {e}")
    if doc.get("sablon") is not False:
        raise Dur("Bu dosya ŞABLON (sablon: true): gerçek ölçümde kullanılamaz.", ORTAM)
    B = fd.denetle(doc, b3_kok=b3_kok, tavanlar=tavanlar(), ab_min=ab_min())
    if fd.hata_var(B):
        raise Dur("Fikstür denetimden geçmedi: " + "; ".join(f"{b.get('id', '-')} {b['neden']}" for b in B if b["seviye"] == "HATA")[:600])
    return doc, yol, kaynak, B


# ---------------------------------------------------------------- hazırlık
def hazirla(b3_kok, fikstur=None, simdi=None):
    d = durum_oku()
    if d.get("durum") in ("suruyor", "kapandi"): raise Dur(f"Ö0-b zaten {d['durum']}: yeniden kurulmaz.", BITTI)
    eksik = on_kosul()
    if eksik: raise Dur("Ö0-b başlayamaz: " + "; ".join(eksik), KULLANICI)
    if not b3_kok or not os.path.isdir(b3_kok): raise Dur("B3 klasörü yok (--b3-kok).", KULLANICI)
    doc, yol, kaynak, B = fikstur_yukle(fikstur, b3_kok)
    film = film_yolu()
    if os.path.exists(os.path.join(film, "SAHNELER.json")): raise Dur("Ölçüm klasörü zaten var (O0b_FILM): silinmez; durum bozuk.", HATA)
    for k in ("SIRALI_GORSEL", "SIRALI_VIDEO", "KUNYE", "_RAPOR"): os.makedirs(os.path.join(film, k), exist_ok=True)
    os.makedirs(klip_kok(), exist_ok=True)
    istem = {}; planlar = []
    for i, it in enumerate(doc["istemler"], 1):
        istem[it["id"]] = {"no": i, "gun": it["gun"], "deney": it["deney"], "kollar": it["kollar"], "durum": "bekliyor"}
        if it.get("kare"):
            src = os.path.join(b3_kok, it["kare"]); hedef = os.path.join(film, "SIRALI_GORSEL", "_B3", f"{i:03d}.jpg")
            os.makedirs(os.path.dirname(hedef), exist_ok=True); shutil.copyfile(src, hedef)
            if not _sha1(hedef).startswith(it["kare_sha1"]): raise Dur(f"{it['id']}: kopyalanan B3 karesinin SHA1'i tutmuyor.")
        planlar.append(_plan(i, it))
    ortak.atomik_yaz(os.path.join(film, "SAHNELER.json"), {"_surum": 2, "film": FILM_AD, "olcum0": "Ö0-b", "karakterler": {},
                                                           "sahneler": planlar})
    ortak.atomik_yaz(os.path.join(film, "HAZIRLIK.json"), {"film": FILM_AD, "saglayici": "flow", "olcum0": "Ö0-b",
                                                           "not": "Ö0-b ölçüm klasörü; film değildir (TASARIM §1.2)"})
    s = _simdi(simdi)
    d = {"durum": "hazir", "fikstur": {"yol": yol, "kaynak": kaynak, "surum": doc.get("fikstur_surum"), "sha1": _sha1(yol),
                                       "sayi": len(doc["istemler"]), "bayrak": [b["neden"] for b in B if b["seviye"] == "BAYRAK"]},
         "b3_kok": os.path.abspath(b3_kok), "film": film, "klipler": klip_kok(), "tavanlar": tavanlar(), "kredi_klip": kredi_klip(),
         "kredi_tavan": KREDI_TAVAN, "hazirlik": o0.zaman(s), "istemler": istem, "gunler": [], "uyari": None}
    durum_yaz(d)
    o0.deneme("b", "hazirlik", {"istem": len(istem), "fikstur": doc.get("fikstur_surum")}, "hazir",
              "fikstür HATA'sız; B3 kareleri SHA1 ile kopyalandı")
    return d


def _plan(no, it):
    """Ölçüm klasörünün SAHNELER v2 planı. Başlangıç karesi gün açılırken SIRALI_GORSEL/NNN.jpg'ye konur (G1 kaydı onunla)."""
    return {"no": no, "sira": no, "sahne": it["gun"], "hareket_istem": it["istem"],
            "zanaat": {"klip_sn": 8, "eylem_zinciri": [{"id": f"a{j + 1}", "tur": "fiziksel", "bas": a["bas"], "bit": a["bit"],
                                                         "metin": a["metin"]} for j, a in enumerate(it.get("adimlar") or [])],
                       "kadrajdakiler": ["kisi"] * int(it.get("kisi_sayisi") or 0)},
            "uretim": {"saglayici": "flow", "istem_bicimi": it["kollar"]["istem_bicimi"], "zincir": {"yontem": "bagimsiz"}},
            "olcum0": {"olcum": "Ö0-b", "id": it["id"], "deney": it["deney"], "kollar": it["kollar"], "zincir": it.get("zincir")}}


# ---------------------------------------------------------------- merdiven
def uyarisiz_gunler(d): return [g for g in d.get("gunler") or [] if g.get("durum") == "bitti" and g.get("uyarisiz")]


def basamak(d):
    """Bugün açılacak basamak (1..): son tam ve uyarısız günün basamağı + 1; o yoksa son günün basamağı ya da 1."""
    tam = [g["basamak"] for g in uyarisiz_gunler(d) if g.get("tam")]
    return (max(tam) + 1) if tam else 1


def kapasite(d):
    """(değer | None, olculemedi). Uyarısız günlerin en yüksek gönderim sayısı; en çok merdivenin tepesi."""
    u = [int(g.get("gonderilen") or 0) for g in uyarisiz_gunler(d)]
    u = [x for x in u if x > 0]
    if not u: return None, True
    return min(max(u), max(d.get("tavanlar") or tavanlar())), False


def _isler(film):
    return ((ortak.json_oku(os.path.join(film, "MEMMET_DURUM.json"), {}) or {}).get("isler") or {})


def _sureler(film):
    p = os.path.join(film, "MEMMET_KAYIT.txt"); out = {}
    if not os.path.exists(p): return out
    with open(p, encoding="utf-8", errors="replace") as f:
        for s in f:
            m = re.search(r"\b(\d{3}) video: KAYDED[İI]LD[İI] \((\d+) sn\)", s)
            if m: out[int(m.group(1))] = int(m.group(2))
    return out


def bakiye_al(d, kosucu, bakiye=None, simdi=None, zorla=False):
    """(bakiye | None, kod). Verilen > taze FLOW_BAKIYE.json (≤ 2 sa, bugün; zorla=True ise kullanılmaz) > Memmet --bakiye (salt okuma)."""
    if bakiye is not None: return int(bakiye), 0
    s = _simdi(simdi); p = os.path.join(hesap(), "FLOW_BAKIYE.json"); b = ortak.json_oku(p, {}) or {}
    try: t = time.mktime(time.strptime(str(b.get("zaman")), "%Y-%m-%d %H:%M:%S"))
    except (TypeError, ValueError): t = 0
    if not zorla and isinstance(b.get("bakiye"), int) and s - t <= BAKIYE_TAZE_SN and _tarih(t) == _tarih(s): return b["bakiye"], 0
    kod = kosucu([os.path.join(ARACLAR, "memmet.py"), film_yolu(), "--bakiye", "--mod", "elle"])
    if kod != 0: return None, kod
    b = ortak.json_oku(p, {}) or {}
    return (b.get("bakiye") if isinstance(b.get("bakiye"), int) else None), 0


def _gun_karesi(d, it_id, no, it, g1z_fn, kare_al):
    """Planın başlangıç karesini SIRALI_GORSEL/NNN.jpg'ye koyar ve G1 kaydını döndürür; konamazsa (None, neden)."""
    film = film_yolu(); hedef = os.path.join(film, "SIRALI_GORSEL", f"{no:03d}.jpg"); b3 = os.path.join(film, "SIRALI_GORSEL", "_B3", f"{no:03d}.jpg")
    kol = it["kollar"]
    if it["deney"] == "ab" or kol.get("son_kare_ref") == "yok":
        shutil.copyfile(b3, hedef); sha = _sha1(hedef)
        return {"sonuc": "GEC", "sha1": sha, "kaynak": "B3 eski iki tur denetimi (Ö0-b fikstürü, TASARIM §1.2)", "olcum0": True}, None
    z = it.get("zincir") or {}; kay = d["istemler"].get(z.get("kaynak")) or {}
    klip = os.path.join(klip_kok(), f"{z.get('kaynak')}.mp4")
    if kay.get("durum") != "indirildi" or not os.path.isfile(klip): return None, f"zincir kaynağı {z.get('kaynak')} indirilmedi"
    gec = os.path.join(film, "_RAPOR", "O0b_zincir"); os.makedirs(gec, exist_ok=True)
    try:
        ham = kare_al(klip, float(z["kare_sn"]), os.path.join(gec, f"{no:03d}_ham.jpg"))
        a_ilk = kare_al(klip, 0.0, os.path.join(gec, f"{no:03d}_kaynak_ilk.jpg"))
        if kol.get("zincir_kare") == "1376x774_kirp3": ham = _kirp(ham, os.path.join(gec, f"{no:03d}_kirp.jpg"))
    except Exception as e: return None, f"zincir karesi çıkarılamadı ({str(e)[:80]}): ölçülemedi"
    planli = b3 if os.path.isfile(b3) else None
    try:
        p = (ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {})
        bp = next(x for x in p.get("sahneler") or [] if x.get("no") == no)
        olc = g1z_fn(film, bp, ham, planli, a_ilk, 1)
    except Exception as e: return None, f"G1Z koşamadı ({str(e)[:80]}): ölçülemedi"
    kotu = [m for m in olc if m.get("seviye") != "GEC"]
    if kotu: return None, "G1Z GEÇ değil (" + ", ".join(f"{m['madde']}:{m['seviye']}" for m in kotu) + "); ÖLÇÜLEMEDİ asla GEÇ değildir"
    shutil.copyfile(ham, hedef); sha = _sha1(hedef)
    return {"sonuc": "GEC", "sha1": sha, "kaynak": "G1Z (kare_zinciri.g1z; Ö0-b zincir karesi)", "olcum": olc, "olcum0": True}, None


def _kirp(src, hedef):
    from PIL import Image
    im = Image.open(src).convert("RGB").resize((1376, 774), Image.LANCZOS).crop((0, 3, 1376, 771))
    im.save(hedef, "JPEG", quality=95); return hedef


def _kare_al(klip, t, hedef):
    import video_denetim
    return video_denetim.kare_cikar(klip, t, hedef)


def _g1z(film, bp, kare, planli, a_ilk, derinlik):
    import kare_zinciri
    return kare_zinciri.g1z(film, bp, kare, planli, a_ilk, derinlik)


def _onizleme_yaz(film, bakiye, harcanan):
    kullanilir = int(math.floor(bakiye * (1 - guvenlik_payi()) + 1e-9))
    on = {"_surum": 1, "_uretim": {"asama": "Ö0-b", "arac_surum": SURUM, "zaman": o0.zaman()}, "taslak": False, "olcum0": "Ö0-b",
          "butce": {"ana": KREDI_TAVAN, "taban": KREDI_TAVAN, "dilimler": {}, "take": 0, "toplam": KREDI_TAVAN, "bakiye": bakiye,
                    "kullanilabilir": kullanilir, "harcanan_once": harcanan, "tavan": KREDI_TAVAN,
                    "not": "Ö0-b ölçüm harcaması (≤ 540 kr; BUT0 olcum0 kalemi)"}}
    ortak.atomik_yaz(os.path.join(film, "URETIM_ONIZLEME.json"), on)
    import blok_plani
    return blok_plani.onizleme_imza(film), kullanilir


def yetki_imzasi(g):
    return hashlib.sha1(json.dumps([g.get("blok"), g.get("planlar"), g.get("tarih"), g.get("basamak")], ensure_ascii=False).encode()).hexdigest()[:16]


def harcanan(film):
    import kredi
    return kredi.defter_ozet(film)["birim"].get("flow", {}).get("harcanan", 0)


def gun(kosucu=None, bakiye=None, kuru=False, simdi=None, g1z_fn=None, kare_al=None, kok=None, keskinlik=None):
    """Bugünün merdiven basamağı. (kod, rapor sözlüğü)."""
    kosucu = kosucu or varsayilan_kosucu; g1z_fn = g1z_fn or _g1z; kare_al = kare_al or _kare_al
    ctx = {"kosucu": kosucu, "kare_al": kare_al, "kok": kok, "keskinlik": keskinlik}
    s = _simdi(simdi); bugun = _tarih(s); d = durum_oku()
    if not d: raise Dur("Ö0-b hazırlanmadı: önce 'flow_deneme.py hazirla --b3-kok <B3 klasörü>'.", KULLANICI)
    if d.get("durum") == "kapandi": return BITTI, {"kullaniciya": "Ö0-b kapandı; yeni ölçüm günü açılmaz.", "sonuc": _ozet(d)}
    u = uyari_bul(d, s, kok)
    if u and d.get("durum") == "hazir":                                       # ölçüm başlamadan kilit: başlatılmaz (kapanmaz)
        raise Dur("Flow kilidi var: Ö0-b başlamaz. Kilit kalktıktan sonra da 7 gün beklenir.", BEKLE)
    if u: return kapat(d, f"uyarı ({u['kaynak']})", uyari=u, simdi=s)
    if d.get("durum") == "hazir":
        y = yakin_uyari(s, kok)
        if y: raise Dur(f"Son {ara_gun()} günde Flow uyarısı var: Ö0-b en erken {_tarih(y + ara_gun() * 86400)} başlar.", BEKLE)
    eksik = on_kosul()
    if eksik: raise Dur("Ö0-b sürmez: " + "; ".join(eksik), KULLANICI)
    G = d["gunler"]; acik = G[-1] if G and G[-1]["durum"] != "bitti" else None
    if acik and acik["tarih"] != bugun:                                       # dünkü yarım gün: kapanır (tam değil)
        _topla(d, acik, None, {"kod": "yenile"}); acik.update(durum="bitti", tam=False, uyarisiz=True); acik = None; durum_yaz(d)
    if not acik and G and G[-1]["tarih"] == bugun:
        raise Dur("Bugünün ölçüm günü bitti. Sıradaki basamak yarın.", BEKLE)
    L = acik["basamak"] if acik else basamak(d)
    T = d.get("tavanlar") or tavanlar()
    if L > len(T): return kapat(d, "merdiven tamamlandı", simdi=s)
    import flow_yuk
    bugun_video = [r for r in flow_yuk.yuk_oku(hesap()) if r.get("tur") == "video" and _tarih(flow_yuk._satir_zaman(r) or 0) == bugun]
    yabanci = [r for r in bugun_video if r.get("film") != FILM_AD]
    if yabanci: raise Dur(f"Bugün bu Flow hesabından {len(yabanci)} başka video gitti: ölçüm günü yarın açılır (sayım karışmasın).", BEKLE)
    tavan = T[L - 1]; bugun_gonderilen = len(bugun_video)
    aday = [(k, v) for k, v in sorted(d["istemler"].items(), key=lambda x: x[1]["no"]) if v["gun"] == L and v["durum"] == "bekliyor"]
    doc = fd.oku(d["fikstur"]["yol"])
    if _sha1(d["fikstur"]["yol"]) != d["fikstur"]["sha1"]: raise Dur("Fikstür hazırlıktan sonra değişti: ölçüm sürmez (yeni sürüm = yeni Ö0-b değil).")
    F = {it["id"]: it for it in doc["istemler"]}
    film = film_yolu(); S = ortak.json_oku(os.path.join(film, "SAHNELER.json")); P = {p["no"]: p for p in S["sahneler"]}
    secilen, atlanan = [], []
    for k, v in aday:
        if len(secilen) + bugun_gonderilen >= tavan: break
        g1, neden = _gun_karesi(d, k, v["no"], F[k], g1z_fn, kare_al)
        if g1 is None: v.update(durum="atlandi", neden=neden); atlanan.append({"id": k, "neden": neden}); continue
        P[v["no"]].setdefault("denetim", {})["G1"] = g1; secilen.append(v["no"])
    if kuru and secilen:
        kk = d.get("kredi_klip") or kredi_klip()
        return BITTI, {"kuru": True, "basamak": L, "tavan": tavan, "planlar": secilen, "atlanan": atlanan, "kredi": len(secilen) * kk}
    ortak.atomik_yaz(os.path.join(film, "SAHNELER.json"), S)
    if not secilen:
        if acik:                                                              # gönderilecek kalmadı (ör. toplama sonrası): gün kapanır
            _topla(d, acik, None, {"kod": "yenile"}); acik.update(durum="bitti", tam=True, uyarisiz=True)
        elif atlanan or not aday:
            G.append({"sira": len(G) + 1, "basamak": L, "tavan": tavan, "tarih": bugun, "blok": None, "planlar": [], "gonderilen": 0,
                      "durum": "bitti", "uyarisiz": True, "tam": True, "atlanan": atlanan, "not": "gönderilecek istem yok"})
        durum_yaz(d)
        return gun_sonu_karari(d, s)
    kk = d.get("kredi_klip") or kredi_klip(); harc = harcanan(film)
    if harc + len(secilen) * kk > KREDI_TAVAN: raise Dur(f"Ö0-b kredi tavanı {KREDI_TAVAN} aşılır (harcanan {harc}).", BUTCE)
    once_b = _mtime(os.path.join(film, "_memmet_cikis.json")); b, kod = bakiye_al(d, kosucu, bakiye, s)
    if kod: return _cikis_isle(d, None, kod, s, ctx, cikis_once=once_b)
    if b is None: raise Dur("Flow bakiyesi okunamadı: '--bakiye N' ile ver (Flow'da sağ üstte yazan kredi).", KULLANICI)
    imza, kullanilir = _onizleme_yaz(film, b, harc)
    if len(secilen) * kk > kullanilir:
        raise Dur(f"Bakiye yetmiyor: {len(secilen) * kk} kredi gerekiyor, kullanılabilir {kullanilir}. Kredi yükleyince 'devam' yaz.", BUTCE)
    if acik is None:
        acik = {"sira": len(G) + 1, "basamak": L, "tavan": tavan, "tarih": bugun, "planlar": [], "kosular": [], "gonderilen": 0,
                "indirilen": 0, "red": [], "hata": [], "zaman_asimi": [], "durum": "acik", "uyarisiz": None, "tam": None,
                "bakiye_once": b, "atlanan": []}
        G.append(acik)
    acik["atlanan"] = (acik.get("atlanan") or []) + atlanan
    blok = f"O0B-G{acik['sira']}-{len(acik['kosular']) + 1}"
    acik.update(blok=blok, planlar=sorted(set(acik["planlar"]) | set(secilen)))
    BP = ortak.json_oku(os.path.join(film, "BLOK_PLANI.json"), {}) or {"_surum": 1, "bloklar": [], "olcum0": "Ö0-b"}
    BP["bloklar"] = [x for x in BP.get("bloklar") or [] if x.get("id") != blok] + [
        {"id": blok, "no": len(BP.get("bloklar") or []) + 1, "tur": "video", "saglayici": "flow", "planlar": secilen, "ayrinti": {}}]
    BP["onizleme_imza"] = imza
    ortak.atomik_yaz(os.path.join(film, "BLOK_PLANI.json"), BP)
    if d["durum"] == "hazir": d.update(durum="suruyor", baslangic=o0.zaman(s), baslangic_epoch=s)
    yetki = {"olcum0": "Ö0-b", "blok": blok, "planlar": secilen, "tarih": bugun, "basamak": L, "tavan": tavan, "kip": "elle"}
    yetki["imza"] = yetki_imzasi(yetki); acik["yetki"] = yetki["imza"]
    ortak.atomik_yaz(os.path.join(film, "O0B_OLCUM.json"), yetki)
    durum_yaz(d)
    print(f"Ö0-b gün {acik['sira']} (basamak {L}, tavan {tavan}): {len(secilen)} istem. Memmet Chrome'da istemleri hazırlayacak; "
          "her birinde GÖNDER'e (Oluşturmaya başla) sen bas. Flow bir uyarı gösterirse hiçbir şeye basma.", flush=True)
    once = _mtime(os.path.join(film, "_memmet_cikis.json"))
    kod = kosucu([os.path.abspath(__file__), "memmet-blok", film, "--blok", blok, "--onizleme", imza, "--mod", "elle"])
    return _cikis_isle(d, acik, kod, s, ctx, cikis_once=once)


def _mtime(p):
    try: return os.path.getmtime(p)
    except OSError: return None


def _cikis_isle(d, acik, kod, s, ctx, cikis_once=None):
    """Memmet çıkışını işler. acik None: bakiye okuması. _memmet_cikis.json yalnız bu koşudan sonra yazıldıysa okunur (bayat dosya yok)."""
    film = film_yolu(); cy = os.path.join(film, "_memmet_cikis.json"); m = _mtime(cy)
    c = (ortak.json_oku(cy, {}) or {}) if (m is not None and (cikis_once is None or m > cikis_once) and kod != 0) else {}
    if acik is not None: _topla(d, acik, kod, c)
    u = uyari_bul(d, None, ctx.get("kok"))
    ckod = c.get("kod")
    if kod == KISIT or u or (kod != 0 and ckod in UYARI_KODLARI):
        if acik is not None: acik.update(durum="bitti", uyarisiz=False, tam=False)
        u = u or {"kaynak": f"memmet çıkış {kod} ({ckod})", "neden": ckod or "olagandisi", "zaman_epoch": _simdi(s)}
        return kapat(d, f"uyarı ({u['kaynak']})", uyari=u, simdi=s)
    if kod == 0 and acik is not None:
        acik.update(durum="bitti", uyarisiz=True, tam=True)
        if acik.get("red"):                                         # kendiliğinden ret: kredi etkisi için gün sonu bakiyesi
            durum_yaz(d)
            once = _mtime(cy); b, k2 = bakiye_al(d, ctx["kosucu"], None, zorla=True)
            if k2: return _cikis_isle(d, None, k2, s, ctx, cikis_once=once)
            acik["bakiye_sonra"] = b
        try: kare_olc(d, kare_al=ctx.get("kare_al"), keskinlik=ctx.get("keskinlik"))
        except Exception as e: d["zincir_karesi"] = {"olculemedi": True, "hata": str(e)[:120]}
        durum_yaz(d)
        return gun_sonu_karari(d, s)
    durum_yaz(d)
    if kod == 8:
        raise Dur("Bazı klipler zaman aşımına uğradı: yeniden gönderilmez, önce toplanır "
                  f"(python memmet_topla.py --film \"{film}\"). Sonra 'flow_deneme.py gun' aynı gün sürer.", BEKLE)
    if kod == 5: raise Dur(f"Bütçe noktası onay vermedi: {c.get('mesaj')}", BUTCE)
    if kod == 4: raise Dur(f"Memmet göndermedi (ortam/imza): {c.get('mesaj')}", ORTAM)
    raise Dur(f"Memmet durdu ({ckod}): {c.get('mesaj') or 'ayrıntı MEMMET_KAYIT.txt'}. Sorunu giderince aynı gün 'flow_deneme.py gun' "
              "kalan istemlerle sürer; gönderilmiş istem yeniden gönderilmez.", KULLANICI if kod == 2 else HATA)


def _topla(d, g, kod, c):
    film = film_yolu(); isler = _isler(film); sure = _sureler(film); no_id = {v["no"]: k for k, v in d["istemler"].items()}
    g["kosular"].append({"blok": g["blok"], "cikis": kod, "kod": c.get("kod"), "zaman": o0.zaman()})
    gonderilen = set(); kirmizi = []
    for is_k, j in isler.items():
        if str(j.get("blok") or "").split("-")[:2] != g["blok"].split("-")[:2] or j.get("tur") != "video": continue
        no = int(j["plan"]); k = no_id.get(no)
        if k is None: continue
        v = d["istemler"][k]; dur = j.get("durum")
        if dur != "iade": gonderilen.add(no)
        if dur == "indirildi":
            src = os.path.join(film, "SIRALI_VIDEO", f"{no:03d}.mp4"); hedef = os.path.join(klip_kok(), f"{k}.mp4")
            if os.path.isfile(src) and not os.path.isfile(hedef):
                os.makedirs(klip_kok(), exist_ok=True); shutil.copy2(src, hedef)
            v.update(durum="indirildi", klip=os.path.relpath(hedef, o0.kok()).replace(os.sep, "/"), uretim_sn=sure.get(no), is_kimligi=is_k)
            ortak.atomik_yaz(os.path.join(klip_kok(), f"{k}.json"),
                             {"id": k, "plan": no, "kollar": v["kollar"], "deney": v["deney"], "is": is_k, "uretim_sn": sure.get(no),
                              "sha1": _sha1(hedef) if os.path.isfile(hedef) else None, "gun": g["sira"], "basamak": g["basamak"]})
        elif dur in ("filtre_red", "hata", "zaman_asimi", "gonderildi"):
            v.update(durum=dur, is_kimligi=is_k)
            if dur == "filtre_red": kirmizi.append(k)
    g["gonderilen"] = len(gonderilen)
    g["indirilen"] = sum(1 for n in gonderilen if d["istemler"][no_id[n]]["durum"] == "indirildi")
    g["red"] = sorted(set(g.get("red") or []) | set(kirmizi))
    g["hata"] = sorted(no_id[n] for n in gonderilen if d["istemler"][no_id[n]]["durum"] == "hata")
    g["zaman_asimi"] = sorted(no_id[n] for n in gonderilen if d["istemler"][no_id[n]]["durum"] in ("zaman_asimi", "gonderildi"))


def gun_sonu_karari(d, s):
    """Gün bitti (uyarısız): merdiven tepesine ulaşıldıysa ya da istem kalmadıysa kapanır; değilse yarın bir basamak yukarı."""
    T = d.get("tavanlar") or tavanlar(); L = basamak(d)
    kalan = [k for k, v in d["istemler"].items() if v["durum"] == "bekliyor"]
    if L > len(T) or not kalan: return kapat(d, "merdiven tamamlandı" if L > len(T) else "istem kalmadı", simdi=s)
    g = d["gunler"][-1]
    o0.deneme("b", f"gun_{g['sira']}", {"basamak": g["basamak"], "gonderilen": g.get("gonderilen"), "red": len(g.get("red") or [])},
              "uyarisiz", "gün uyarısız bitti; merdiven " + ("bir basamak çıkar" if g.get("tam") else "aynı basamakta kalır (gün tam değil)"))
    durum_yaz(d)
    return BITTI, {"kullaniciya": f"Bugünkü ölçüm uyarısız bitti ({g.get('gonderilen')} video). Yarın {T[L - 1]} videoluk gün açılır.",
                   "sonuc": _ozet(d)}


# ---------------------------------------------------------------- değerlendirme ve kapanış
def on_kararlar(d):
    """A/B kol sayıları (indirilmiş klipler). Değerlendirme Ö0-b·V3'te; burada yalnız 'ölçülebilir mi' kararı (TASARIM §1.2)."""
    n = ab_min(); out = {}
    ind = [v for v in d["istemler"].values() if v["durum"] == "indirildi"]
    for etk, degler in ETKENLER.items():
        if etk in ("istem_bicimi", "bekleme"): liste = [v for v in ind if v["deney"] == "ab"]
        elif etk == "son_kare_ref": liste = [v for v in ind if v["deney"] == "zincir"]
        else: liste = [v for v in ind if v["deney"] == "zincir" and v["kollar"].get("son_kare_ref") == "var"]
        say = {x: sum(1 for v in liste if v["kollar"].get(etk) == x) for x in degler}
        ok = min(say.values()) >= n
        out[etk] = {"kollar": say, "karar": "kayitli_v3_bekliyor" if ok else "olculemedi_varsayilan", "varsayilan": VARSAYILAN_KARAR[etk],
                    "gerekce": (f"kol başına ≥ {n} klip; karar Ö0-b·V3'te, A14a doğrular" if ok
                                else f"kol başına < {n} klip → ölçülemedi → varsayılan '{VARSAYILAN_KARAR[etk]}' (A14a doğrular)")}
    return out


def politika_reddi(d):
    """Kendiliğinden gelen retlerin kredi etkisi: yakti | yakmadi | olculemedi | ret_yok (gün başı/sonu bakiyesinden)."""
    toplam = sum(len(g.get("red") or []) for g in d.get("gunler") or [])
    if not toplam: return {"ret": 0, "kredi_etkisi": "ret_yok"}
    kk = d.get("kredi_klip") or kredi_klip(); sonuc = []
    for g in d["gunler"]:
        r = len(g.get("red") or [])
        if not r: continue
        bo, bs = g.get("bakiye_once"), g.get("bakiye_sonra")
        if not isinstance(bo, int) or not isinstance(bs, int): sonuc.append("olculemedi"); continue
        harc = bo - bs; tum = kk * g.get("gonderilen", 0); kabul = kk * (g.get("gonderilen", 0) - r)
        sonuc.append("yakti" if abs(harc - tum) <= kk / 2 else ("yakmadi" if abs(harc - kabul) <= kk / 2 else "olculemedi"))
    e = sonuc[0] if len(set(sonuc)) == 1 else "olculemedi"
    return {"ret": toplam, "kredi_etkisi": e, "gunler": sonuc, "not": "yalnız kendiliğinden gelen ret (kasıtlı tetikleme yok, §10.4)"}


def kare_olc(d, kare_al=None, keskinlik=None):
    """Zincir karesi kalitesi: indirilen ab kliplerinde Y55 penceresinden kare (doğal 1280×720 ve 1376×774 + 3 px kırpma) ve
    keskinliğin klibin ilk karesine oranı. Ölçülemezse kayıt 'olculemedi'."""
    kare_al = kare_al or _kare_al
    if keskinlik is None:
        from olcum import teknik
        keskinlik = lambda y: teknik.keskinlik(teknik.gri(y))
    gec = os.path.join(film_yolu(), "_RAPOR", "O0b_kare"); os.makedirs(gec, exist_ok=True)
    doc = fd.oku(d["fikstur"]["yol"]); F = {it["id"]: it for it in doc["istemler"]}
    dog, kir = [], []
    for k, v in d["istemler"].items():
        if v["durum"] != "indirildi" or v["deney"] != "ab": continue
        klip = os.path.join(o0.kok(), v["klip"]); son = max(float(a["bit"]) for a in F[k]["adimlar"])
        t = round((son + 0.2 + 7.5) / 2, 2)
        try:
            ilk = keskinlik(kare_al(klip, 0.0, os.path.join(gec, f"{k}_ilk.jpg")))
            ham = kare_al(klip, t, os.path.join(gec, f"{k}_zincir.jpg"))
            if ilk > 0:
                dog.append(keskinlik(ham) / ilk); kir.append(keskinlik(_kirp(ham, os.path.join(gec, f"{k}_kirp.jpg"))) / ilk)
        except Exception: continue
    z = {"n": len(dog), "olculemedi": not dog, "olcu": "keskinlik(zincir karesi) / keskinlik(ilk kare)",
         "dogal_1280x720": round(statistics.median(dog), 3) if dog else None, "1376x774_kirp3": round(statistics.median(kir), 3) if kir else None}
    d["zincir_karesi"] = z
    return z


def _ozet(d):
    return {k: d.get(k) for k in ("durum", "olculen_gunluk_kapasite", "olculemedi", "kapanis_nedeni", "uretim_sn_720p", "klip_sayisi")
            if k in d}


def kapat(d, neden, uyari=None, simdi=None, beyan=None):
    """Ö0-b'yi kapatır (geri açılmaz). (kod, rapor). Uyarıyla kapandıysa 7 (KISIT).
    beyan: kullanıcının kararıyla merdiven bırakıldı; kapasite = beyan (video/gün). Uyarıyla ya da uyarı kayıtlıyken beyan alınmaz."""
    s = _simdi(simdi)
    if beyan is not None and (uyari or d.get("uyari") or any(g.get("uyarisiz") is False for g in d.get("gunler") or [])):
        raise Dur("Flow uyarısı kayıtlı: kapasite beyanı alınmaz (ölçüm sonucu geçerli).", KISIT)
    for g in d.get("gunler") or []:
        if g.get("durum") != "bitti": g.update(durum="bitti", uyarisiz=uyari is None and g.get("uyarisiz") is not False, tam=False)
    kap, olm = kapasite(d)
    if beyan is not None:
        if int(beyan) < 1: raise Dur("--beyan en az 1 olmalı.", HATA)
        kap, olm = int(beyan), False
        d.update(kapasite_kaynagi="kullanici_beyani", olculen_alt_sinir=kapasite(d)[0])
    sureler = [v["uretim_sn"] for v in d["istemler"].values() if isinstance(v.get("uretim_sn"), int)]
    d.update(durum="kapandi", kapanis=o0.zaman(s), kapanis_nedeni=neden, uyari=uyari, olculen_gunluk_kapasite=kap, olculemedi=olm,
             uretim_sn_720p=int(statistics.median(sureler)) if sureler else None,
             klip_sayisi=sum(1 for v in d["istemler"].values() if v["durum"] == "indirildi"),
             on_kararlar=on_kararlar(d), politika_reddi=politika_reddi(d))
    d["politika_reddi_kredi"] = d["politika_reddi"]["kredi_etkisi"]
    if uyari:
        z = float(uyari.get("zaman_epoch") or s)
        d["olcum_yasak_bitis"] = _tarih(z + ara_gun() * 86400)
    o0.yaz("b", d, arac=SURUM)
    o0.deneme("b", "kapasite", {"olculen_gunluk_kapasite": kap, "uyarisiz_gun": len(uyarisiz_gunler(d))},
              "olculemedi" if olm else (f"{kap}/gün (kullanıcı beyanı)" if beyan is not None else f"{kap}/gün (alt sınır)"),
              f"{neden}; " + ("kullanıcı kararı: merdiven bırakıldı, kapasite beyandan" if beyan is not None else "uyarısız gün yok → ilk film 1800 sn (D-05)" if olm else
                              ("alt sınır < 20 → ilk film 1800 sn (D-05)" if kap < max(d.get("tavanlar") or [20]) else "merdivenin tepesi uyarısız")))
    o0.deneme("b", "uretim_sn_720p", {"medyan": d["uretim_sn_720p"], "n": len(sureler)}, d["uretim_sn_720p"] or "olculemedi",
              "gönderimden indirmeye (Memmet kaydı)")
    o0.deneme("b", "politika_reddi", d["politika_reddi"], d["politika_reddi_kredi"], "yalnız kendiliğinden gelen ret")
    for etk, v in d["on_kararlar"].items(): o0.deneme("b", f"ab_{etk}", v["kollar"], v["karar"], v["gerekce"])
    if uyari:
        msg = ("Flow uyarı verdi: GÖNDER'e basma, sayfayı yenileme, başka hesap deneme. Ö0-b burada kapandı (yeniden denenmez). "
               f"Ölçülen uyarısız kapasite: {kap if not olm else 'ölçülemedi'}. {d['olcum_yasak_bitis']} tarihine kadar Flow ölçümü yok.")
        print(msg, flush=True)
        return KISIT, {"kullaniciya": msg, "sonuc": _ozet(d)}
    msg = (f"Ö0-b bitti ({neden}). Günlük kapasite kullanıcı beyanından: {kap} video/gün (ölçüm değil; Flow uyarısında yine durulur)."
           if beyan is not None else f"Ö0-b bitti ({neden}). Günlük uyarısız kapasite (alt sınır): {kap if not olm else 'ölçülemedi'}.")
    print(msg, flush=True)
    return BITTI, {"kullaniciya": msg, "sonuc": _ozet(d)}


def rapor():
    d = durum_oku()
    if not d: raise Dur("Ö0-b hazırlanmadı.", KULLANICI)
    if d.get("durum") == "kapandi":
        d.update(on_kararlar=on_kararlar(d), politika_reddi=politika_reddi(d)); d["politika_reddi_kredi"] = d["politika_reddi"]["kredi_etkisi"]
        o0.yaz("b", d, arac=SURUM)
    else: durum_yaz(d)
    return BITTI, _ozet(d)


def durum_metni(d=None):
    d = durum_oku() if d is None else d
    if not d:
        eksik = on_kosul()
        return {"durum": "yok", "sonraki": "hazirla" if not eksik else None, "on_kosul_eksik": eksik,
                "kullaniciya": "Ö0-b henüz hazırlanmadı." + (" Önce: " + "; ".join(eksik) if eksik else "")}
    out = {"durum": d["durum"], "gun": len(d.get("gunler") or []), "basamak": basamak(d) if d["durum"] != "kapandi" else None,
           "klip": sum(1 for v in d["istemler"].values() if v["durum"] == "indirildi")}
    if d["durum"] == "kapandi": out.update(_ozet(d)); out["sonraki"] = None
    else:
        G = d.get("gunler") or []
        out["sonraki"] = "gun"
        if G and G[-1]["tarih"] == _tarih(saat()) and G[-1]["durum"] == "bitti": out["sonraki"] = "yarin"
    return out


# ---------------------------------------------------------------- Memmet sarmalayıcısı (iç komut)
def olcum_memmet_sinifi(memmet):
    """memmet.Memmet'ten türeyen Ö0-b sınıfı. YALNIZ blok_dogrula değişir (sayfaya dokunmaz): film animatiği yerine Ö0-b yetkisi
    (O0B_OLCUM.json + O0b.json günü) aranır. Sayfa işlemleri, uyarı/doğrulama durdurmaları, tempo, BUTK, kredi defteri aynen Memmet'indir."""
    import blok_plani

    class O0bMemmet(memmet.Memmet):
        def blok_dogrula(self):
            D = memmet.Durdur
            if os.path.normcase(os.path.abspath(self.root)) != os.path.normcase(os.path.abspath(film_yolu())):
                raise D("Ö0-b sarmalayıcısı yalnız <veri>/BILGI/OLCUM0/O0b_FILM klasöründe çalışır.", kod="ortam")
            if self.A["kip"] != "elle": raise D("Ö0-b yalnız elle kipinde ölçer (GÖNDER'e kullanıcı basar).", kod="ortam")
            if self.A.get("video_cozunurluk") != "720p": raise D("Ö0-b 720p ölçer (MEMMET_AYAR video_cozunurluk 720p değil).", kod="ortam")
            sag = str((ortak.json_oku(os.path.join(self.root, "HAZIRLIK.json"), {}) or {}).get("saglayici") or "").lower()
            if sag in ("sahte", "kaset"): raise D(f"'{sag}' deneme klasörü: Flow'a gerçek gönderim yapılmaz.", kod="ortam")
            d = durum_oku(); y = ortak.json_oku(os.path.join(self.root, "O0B_OLCUM.json"), {}) or {}
            g = (d.get("gunler") or [None])[-1] or {}
            if d.get("durum") != "suruyor" or d.get("uyari"): raise D("Ö0-b sürmüyor (kapandı ya da uyarı var): gönderim yok.", kod="kilitli")
            if y.get("olcum0") != "Ö0-b" or y.get("imza") != yetki_imzasi(y) or g.get("yetki") != y.get("imza") or g.get("durum") == "bitti":
                raise D("Ö0-b gün yetkisi yok ya da tutmuyor (flow_deneme.py gun açar). Hiçbir şey gönderilmedi.", kod="imza")
            if y.get("tarih") != _tarih(saat()): raise D("Ö0-b gün yetkisi bugüne ait değil.", kod="imza")
            if uyari_bul(d): raise D("Hesapta Flow uyarısı/kilidi var: Ö0-b gönderim yapmaz.", kod="kilitli")
            try: BP, b = blok_plani.blok_bul(self.root, self.args["blok"])
            except ValueError as e: raise D(str(e), kod="imza")
            if str(b.get("id")) != y.get("blok") or sorted(int(n) for n in b.get("planlar") or []) != sorted(y.get("planlar") or []):
                raise D("Blok Ö0-b gün yetkisiyle aynı değil.", kod="imza")
            imza = blok_plani.onizleme_imza(self.root)
            if not imza or self.args.get("onizleme") != imza or BP.get("onizleme_imza") != imza:
                raise D("Ö0-b bütçe imzası tutmuyor (URETIM_ONIZLEME). Hiçbir şey gönderilmedi.", kod="imza")
            if (b.get("saglayici") or "flow") != "flow": raise D("Blok Flow'a değil.", kod="ortam")
            if len(b.get("planlar") or []) > blok_plani.BLOK_MAX: raise D("Blok 20 plandan büyük.", kod="imza")
            self.blok, self.blok_id = b, str(b["id"]); self.blok_nolar = {int(n) for n in b.get("planlar") or []}
            self.planlar = {int(p["no"]): p for p in self.plan.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
            return b

    return O0bMemmet


def memmet_blok(argv):
    """İç komut: memmet.main'i Ö0-b sınıfıyla koşar (çıkış kodları ve durdurma işleyişi memmet.main'indir)."""
    if "--mod" in argv and argv[argv.index("--mod") + 1] != "elle": print("Ö0-b yalnız elle kipinde."); return ORTAM
    if "--mod" not in argv: argv = list(argv) + ["--mod", "elle"]
    import memmet
    memmet.Memmet = olcum_memmet_sinifi(memmet)
    try: memmet.main(list(argv))
    except SystemExit as e: return int(e.code or 0) if not isinstance(e.code, str) else 1
    return 0


def varsayilan_kosucu(argv):
    return subprocess.run([sys.executable] + list(argv)).returncode


# ---------------------------------------------------------------- komut satırı
def _arg(argv, ad, vars_=None):
    return argv[argv.index(ad) + 1] if ad in argv and argv.index(ad) + 1 < len(argv) else vars_


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    k = argv[0]
    try:
        if k == "memmet-blok": return memmet_blok(argv[1:])
        if k == "durum":
            r = durum_metni(); print(json.dumps(r, ensure_ascii=False, indent=None if "--json" in argv else 1)); return 0
        if k == "denetle-fikstur": return fd.main(argv[1:])
        if o0.ortam() == "bulut":
            print("Ö0-b yalnız kullanıcının bilgisayarında yapılır (Flow, Memmet)."); return ORTAM
        if k == "hazirla":
            d = hazirla(_arg(argv, "--b3-kok"), _arg(argv, "--fikstur"))
            print(f"Ö0-b hazır: {len(d['istemler'])} istem. Sıradaki: 'flow_deneme.py gun' (bugün {d['tavanlar'][0]} video)."); return 0
        if k == "gun":
            b = _arg(argv, "--bakiye")
            kod, r = gun(bakiye=int(b) if b is not None else None, kuru="--kuru" in argv)
            print(json.dumps(r, ensure_ascii=False)); return kod
        if k == "kare-olc":
            d = durum_oku(); z = kare_olc(d); o0.yaz("b", d, arac=SURUM); print(json.dumps(z, ensure_ascii=False)); return 0
        if k == "kapat":
            d = durum_oku()
            if not d or d.get("durum") == "kapandi": print("Kapatılacak süren Ö0-b yok."); return 0
            b = _arg(argv, "--beyan")
            kod, r = kapat(d, _arg(argv, "--neden", "kullanıcı kararı" if b else "elle kapatıldı"),
                           beyan=int(b) if b is not None else None); return kod
        if k == "rapor":
            kod, r = rapor(); print(json.dumps(r, ensure_ascii=False)); return kod
    except Dur as e:
        print(str(e), flush=True); return e.kod
    except ortak.YolYok as e:
        print(str(e)); return ORTAM
    print(__doc__); return ORTAM


if __name__ == "__main__":
    sys.exit(main())
