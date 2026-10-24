"""HİKÂYE ODASI — A01–A06 betikleri (TASARIM §1.3, §6.3, §7.2; [SN2] §4.2 H1–H13). film.py görevi olarak çağrılır:
"python hikaye_odasi.py <alt komut> [seçenekler] --film <film>" (YZ_FILM_GOREV = görev klasörü; rapor yolu ve tur oradan okunur).

Alt komutlar (girdi → çıktı; hepsi <film>/_HIKAYE_ODASI/ altında okur, kapı raporu _RAPOR/'a kapi.py zarfıyla):
  konu-denetim      01_KONU_KARTI.json → _RAPOR/KONU_t<n>.json (şema, kanca ailesi, risk çözümü, telif dönüşümü, süre [1800, 2700]
                    gerekçeli, eksenler farklı, çocuk kahraman/filtre riski); varsayımlar karar defterine (film.py karar ekle)
  butce-bilgisi     _RAPOR/BUT0_FILM.json + ortam → butce_bilgisi.json (yapımcının GIRDI'si; bakiye yoksa "bilinmiyor")
  brifing           konu kartı + DERSLER_AKTIF.md (hikâye) + RE + hikaye_esikleri + filtre listesi → 00_BRIFING.md (+ .sha1),
                    _RAPOR/BRIFING_t<n>.json (7 bölüm, 1.500–4.000 kelime)
  logline           02_oneri_{D,S,E}.md → 02_LOGLINELAR.md (X mimarına "kaçınılacak yollar")
  oneri-denetim     02_oneri_<eksen>.md (```json makine bloğu ya da .json) → _RAPOR/ONERI_t<n>.json: 10 başlık, başlık kalıbı ve ≤ 100 kr,
                    konuşan ≤ 8, ana ≤ 4, örnek replikte filtre/yaş/NE YOK, logline ≤ 35 kelime, çeşitlilik dörtlüsü (BENZER: tur 1'de HATA
                    → yeni eksenle 1 kez; sonra BAYRAK + jüri paketine çeşitlilik notu)
  juri-paketi       öneriler → JURI_PAKETI/Oneri_<k>.md (anonim; eksen silinir) + JURI_ANAHTAR.json (jüriye verilmez)
  juri-topla        03_juri_<rol>.json ×5 → 04_SECIM.json, 04_KULLANICIYA_OZET.md, _RAPOR/JURI_t<n>.json (ölçüt medyanı, ortalama,
                    veto, BIRLESTIR ≤ 0,3, kazanan ≥ 8,0: tur 1'de altıysa HATA → yazar 1 kez yeniden; sonra hedef_alti)
  yapi-denetim      05_YAPI.json → _RAPOR/YAPI_t<n>.json (3 parti × 8 başlık, tek cümle, parti oranı, vuruşlar, parti sonu/doruk/en karanlık
                    yoğunluğu, sahne değeri, kurulum → kullanım, olgu kaynağı, olgu sayısı)
  oyuncu-paketi     en son 06_SENARYO → OYUNCU_PAKETI/<karakter>.md, DIYALOG_PAKETI.md, DEGISEN.json (önceki sürüme göre fark)
  senaryo-denetim   en son 06_SENARYO_v<N>.json → _RAPOR/HIKAYE_Z_v<n>.json (kapı SEMA; Z1/Z2 hikâye ölçüleri ±%15 bant, filtre,
                    NE YOK, kanon, bilgi durumu, sahne sınırı, vaat, ilk replik ekranda, görünüş atfı, taşıdığı) + KUYRUK/YENIDEN_YAZ
  seyirci-topla     ince kısayol: puan_oku.seyirci_topla (D-32) · ilk2dk-topla: puan_oku.ilk2dk_topla
  devir             en son senaryo + HS_KAGIT GEÇ/hedef_alti → HIKAYE.json (kilit) + HIKAYE.md + evren.py --on-kayit
  sahne-sozlesme    HIKAYE.json ↔ planlar (SAHNELER v2 ya da _YONETMEN/PLANLAR) → _RAPOR/SEMA_SOZLESME.json ([SN2] §4.5.3)
  vaat-denetim      [--baslik "<…>"] HIKAYE/senaryo → _RAPOR/SEMA_VAAT_t<n>.json (başlık ≤ 100 kr, kalıp, "kill" BAYRAK, vaat öğesi
                    sahnesi, kapak imgesi ≤ 120 sn, risk sözlü ≤ 180 sn)
  seyirlik-denetim  HIKAYE/senaryo → _RAPOR/Z2_HIKAYE.json (seyirlik an/parti, gösterişsiz aralık, küçük güzel sahne, Short adayı)
Ortak seçenekler: --film <ad|yol> (zorunlu) · --tur N (görev klasörü yoksa) · --json
Kural: 'tahmin' kaynaklı eşikler ilk iki filmde yalnız BAYRAK verir (kalibrasyon; [SN2] §4.7); 'belge' kaynaklılar H/B tablosundaki gibi.
Çıkış kodları: 0 rapor yazıldı (kapı sonucu raporda; film.py okur) · 1 araç/girdi hatası (devirde HIKAYE/evren HATA'sı) ·
               4 ORTAM (YOLLAR.json yok) · bilinmeyen alt komut 1.
"""
import os, re, sys, json, glob, hashlib, random, subprocess
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi, puan_oku, istem_denetim, evren
try: import kuyruk                     # YENIDEN_YAZ sahibi; yoksa maddeler yalnız raporda kalır
except Exception: kuyruk = None

SURUM = "hikaye_odasi 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
HO = "_HIKAYE_ODASI"
EKSENLER_YENI, EKSENLER_DEVAM = ("D", "S", "E", "X"), ("A", "B", "S", "X")
JURI_ROLLERI = ("ilk_kez_izleyen", "youtube_stratejisti", "tur_uzmani", "duygu_elestirmeni", "uretilebilirlik")
YAPI_BASLIKLARI = ("b1_amac_duygu", "b2_vurus_akisi", "b3_kim_nerede", "b4_nesne_yolu", "b5_yalan_niyet_bilgi", "b6_mekan_olgulari",
                   "b7_parti_kancasi", "b8_kaba_plan_ve_risk")
ONERI_BASLIKLARI = ("logline", "başlık", "karakter", "dönem", "parti", "soğuk açılış", "merak", "küçük güzel", "seri kancası",
                    "üretilebilirlik")
BRIFING_BOLUMLERI = ("1. Kanal ve izleyici", "2. Kesin istekler", "3. Üretim sınırları", "4. Ritim iskeleti",
                     "5. Doğrulanmış hikâye dersleri", "6. Teslim şablonu", "7. Konu yorumu")
COCUK_TR = ("çocuk", "kız çocuğu", "oğlan", "bebek", "yavrusu olan kız", "küçük kız", "küçük oğlan")
BASLIK_KALIP = re.compile(r"^(.+?) \| ([A-Z0-9][A-Z0-9 _\-]+) \| Full Movie 4K \d{4}$")
DURUM_ALANLARI = ("mekan", "kostum", "gorunum")
NESNE_ALANLARI = ("kimde", "nerede", "durum", "el")


# --- eşik ve ortak yardımcılar ---------------------------------------------------------------------------------
def E(ad, v=None):
    e = puan_oku.esikler_()
    x = e.get(ad) if hasattr(e, "get") else None
    return v if x is None else x


def kaynak(ad):
    e = puan_oku.esikler_()
    return ((getattr(e, "kayit", {}) or {}).get(ad) or {}).get("kaynak")


def sev(ad, seviye="HATA"):
    """'tahmin' kaynaklı eşik ilk iki filmde HATA vermez, BAYRAK verir."""
    return "BAYRAK" if seviye == "HATA" and kaynak(ad) == "tahmin" else seviye


def bant(deger, sinir, ad, yon="max", seviye="HATA"):
    """Zaman belirsizliği bandı (±zaman_belirsizlik_bandi): sınır içinde GEC, bant içinde BAYRAK, dışında seviye."""
    b = float(E("zaman_belirsizlik_bandi", 0.15))
    if deger is None or sinir is None: return "OLCULEMEDI"
    if yon == "max":
        if deger <= sinir: return "GEC"
        return "BAYRAK" if deger <= sinir * (1 + b) else sev(ad, seviye)
    if deger >= sinir: return "GEC"
    return "BAYRAK" if deger >= sinir * (1 - b) else sev(ad, seviye)


def m(madde, seviye, **k):
    d = {"madde": madde, "seviye": seviye}; d.update({a: b for a, b in k.items() if b is not None}); return d


def oku(film, *p): return ortak.json_oku(os.path.join(film, *p))


def metin_oku(p):
    try:
        with open(p, encoding="utf-8-sig") as f: return f.read()
    except OSError: return None


def metin_yaz(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: f.write(s); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def kelime(s): return len(re.findall(r"[0-9A-Za-zÇĞİÖŞÜçğıöşü']+", s or ""))


def son_senaryo(film):
    """(N, yol, veri) — en büyük sürüm numaralı 06_SENARYO_v<N>.json."""
    ad = []
    for p in glob.glob(os.path.join(film, HO, "06_SENARYO_v*.json")):
        mm = re.search(r"_v(\d+)\.json$", p)
        if mm: ad.append((int(mm.group(1)), os.path.getmtime(p), p))
    for n, _, p in sorted(ad, reverse=True):
        j = ortak.json_oku(p)
        if isinstance(j, dict): return n, p, j
    return None, None, None


def baglam(o, asama, kapi_kod, varsayilan_rapor):
    g = puan_oku.gorev_baglami(o.get("--tur"), asama)
    yol = os.path.join(o["film"], g["rapor"]) if g.get("rapor") else os.path.join(o["film"], varsayilan_rapor.format(tur=g["tur_no"]))
    return g, yol


def yaz(o, g, yol, kapi_kod, olc, girdi, kapsam="FILM", ek=None, sonuc=None):
    yol, r = puan_oku.kapi_yaz(o["film"], kapi_kod, kapsam, olc, g["tur_no"], g["asama"], g["id"], girdi, arac=SURUM, ek=ek, yol=yol,
                               sonuc=sonuc)
    print(f"{kapi_kod}: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r.get('bayraklar') or [])} → "
          f"{os.path.relpath(yol, o['film'])}")
    return r


def filtre_bul(metin):
    return istem_denetim.bul(metin, istem_denetim.FILTRE_KELIMELERI) + istem_denetim.YAS_IFADESI.findall(metin or "")


def ne_yok(film):
    try: return evren.ne_yok_kelimeleri(film=film)
    except Exception: return []


# --- A01 --------------------------------------------------------------------------------------------------------
def konu_denetim(o):
    film = o["film"]; g, yol = baglam(o, "A01", "KONU", "_RAPOR/KONU_t{tur}.json")
    kk = oku(film, HO, "01_KONU_KARTI.json"); olc = []
    if not isinstance(kk, dict):
        return yaz(o, g, yol, "KONU", [m("konu_karti_yok", "HATA", neden="01_KONU_KARTI.json yok ya da bozuk")], [])
    for a in ("konu_ham", "seri", "tur", "kanca_ailesi", "vaat_imgesi", "riskler", "sure", "eksenler"):
        if a not in kk: olc.append(m("sema", "HATA", alan=a, neden="zorunlu alan yok"))
    seri = kk.get("seri") or {}
    if seri and seri.get("durum") not in ("yeni", "devam"): olc.append(m("seri_durum", "HATA", olcu=seri.get("durum")))
    if seri.get("durum") == "devam":
        s = evren.seri_normal(seri.get("evren"))
        if not s or s not in evren.seriler(): olc.append(m("seri_evren_yok", "HATA", olcu=seri.get("evren")))
    aileler = E("konu_kanca_aileleri", [])
    ka = kk.get("kanca_ailesi") or {}
    if ka.get("birincil") not in aileler: olc.append(m("kanca_ailesi", "HATA", olcu=ka.get("birincil"), esik=aileler))
    if ka.get("ikincil") and ka["ikincil"] not in aileler: olc.append(m("kanca_ailesi_ikincil", "BAYRAK", olcu=ka["ikincil"]))
    turler = set()
    for i, r in enumerate(kk.get("riskler") or []):
        if not isinstance(r, dict): olc.append(m("risk_sema", "HATA", olcu=i)); continue
        turler.add(r.get("tur"))
        if not (r.get("cozum") or "").strip(): olc.append(m("risk_cozumsuz", "HATA", olcu=r.get("tur"), neden=r.get("aciklama")))
        if r.get("tur") == "telif" and r.get("seviye") == "yuksek" and not (r.get("donusum") or "").strip():
            olc.append(m("telif_donusum_yok", "HATA"))
    ham = (kk.get("konu_ham") or "").lower()
    if (any(w in ham for w in COCUK_TR) or filtre_bul(kk.get("vaat_imgesi"))) and "filtre" not in turler:
        olc.append(m("filtre_riski_tanimsiz", "HATA", neden="çocuk/küçük sinyali var ama 'filtre' riski ve çözümü yok"))
    if filtre_bul(kk.get("vaat_imgesi")): olc.append(m("vaat_imgesi_filtre", "HATA", olcu=filtre_bul(kk.get("vaat_imgesi"))))
    sure = kk.get("sure") or {}; aralik = E("film_sure_aralik_sn", [1800, 2700]); sn = sure.get("film_sure_hedef_sn")
    if not isinstance(sn, (int, float)) or not (aralik[0] <= sn <= aralik[1]):
        olc.append(m("sure_aralik", "HATA", olcu=sn, esik=aralik))
    if not (sure.get("gerekce") or "").strip(): olc.append(m("sure_gerekcesiz", "HATA"))
    but0 = oku(film, "_RAPOR", "BUT0_FILM.json") or {}
    ust = but0.get("ust_sinir_sn") or (but0.get("secim") or {}).get("ust_sinir_sn")
    if isinstance(ust, (int, float)) and isinstance(sn, (int, float)) and sn > ust:
        olc.append(m("sure_but0_ustu", "HATA", olcu=sn, esik=ust, neden="BUT0 üst sınırı"))
    ek = kk.get("eksenler") or {}
    beklenen = EKSENLER_DEVAM if seri.get("durum") == "devam" else EKSENLER_YENI
    eksik = [x for x in beklenen if x not in ek]
    if eksik: olc.append(m("eksen_eksik", "HATA", olcu=eksik, esik=list(beklenen)))
    cumleler = [str(v).strip().lower() for k, v in ek.items() if k != "X" and v]
    if len(set(cumleler)) != len(cumleler): olc.append(m("eksen_ayni", "HATA", neden="eksen motor cümleleri birbirinden farklı olmalı"))
    for v in kk.get("varsayimlar") or []:
        if isinstance(v, dict) and v.get("karar"): _karar_ekle(film, v, "A01")
    if not olc: olc.append(m("konu_karti", "GEC"))
    return yaz(o, g, yol, "KONU", olc, [f"{HO}/01_KONU_KARTI.json"])


def _karar_ekle(film, v, asama):
    """Varsayımı KARAR_DEFTERI'ne film.py karar ekle ile yazar (sahibi film.py); aynı karar ikinci kez yazılmaz."""
    metin = " — ".join(x for x in (v.get("karar"), v.get("neden"), v.get("yanlissa_maliyet") or v.get("yanlissa_maliyeti")) if x)
    defter = metin_oku(os.path.join(film, "KARAR_DEFTERI.md")) or ""
    if v.get("karar") in defter: return
    subprocess.run([sys.executable, os.path.join(HERE, "film.py"), "karar", "ekle", metin, "--asama", asama,
                    "--kaynak", "betik:hikaye_odasi", "--tur", "karar", "--film", film], capture_output=True, text=True, timeout=120)


def butce_bilgisi(o):
    film = o["film"]; b = oku(film, "_RAPOR", "BUT0_FILM.json") or {}
    r = {"_uretim": {"arac_surum": SURUM, "zaman": kapi.simdi()}, "bakiye": b.get("bakiye"),
         "kaynak": "BUT0_FILM.json" if b else "bilinmiyor", "ust_sinir_sn": b.get("ust_sinir_sn"),
         "secilen_sn": b.get("sure_sn"), "ortam": kapi.ortam(),
         "not": "bakiye bilinmiyorsa süre Ö0-b yokken 1800 sn (D-05)" if not b.get("bakiye") else None}
    ortak.atomik_yaz(os.path.join(film, HO, "butce_bilgisi.json"), r)
    print(json.dumps(r, ensure_ascii=False)); return None


# --- A02 brifing ------------------------------------------------------------------------------------------------
def _dersler():
    try: p = os.path.join(ortak.yollar()["veri_kok"], "BILGI", "DERSLER_AKTIF.md")
    except ortak.YolYok: return []
    s = metin_oku(p) or ""
    return [x.strip() for x in s.splitlines() if x.strip().startswith(("-", "*")) and "hikaye" in x.lower()]


def _sayi(ad, v="?"):
    x = E(ad)
    return v if x is None else (", ".join(map(str, x)) if isinstance(x, (list, tuple)) else x)


def brifing_metni(film, kk):
    sure = (kk.get("sure") or {}).get("film_sure_hedef_sn") or E("film_sure_hedef_sn", 2400)
    dk = round(sure / 60)
    filtre = ", ".join(istem_denetim.FILTRE_KELIMELERI)
    ny = ne_yok(film)
    dersler = _dersler()
    yonl = " ".join(f"{k}: {v}." for k, v in (kk.get("eksenler") or {}).items() if k != "X")
    istekler = kk.get("kesin_istekler") or []
    s = [f"# Brifing — {kk.get('konu_ham', '')}", "",
         "Bu brifing dört hikâye mimarına aynı metin olarak verilir (sha1 kaydı ayrı dosyada). Eksen satırı brifinge değil, her mimarın "
         "kendi görev istemine yazılır. Bu belgedeki sayılar eşik dosyalarından basılır; elle değiştirilmez.", "",
         "## " + BRIFING_BOLUMLERI[0], "",
         "Kanal İngilizce konuşulan, uzun biçimli (30–45 dakika) yapay zekâ filmleri yayınlar. İzleyici YouTube'da başlığa ve kapağa bakıp "
         "girer; ilk iki dakikada başlıkta verilen sözün tutulup tutulmadığına karar verir. Kazanan filmlerde ortak örüntü şudur: insan ile "
         "yaratık arasındaki bağ, bu bağı yasaklayan bir karşı güç, saklama ve dramatik ironi. İzleyici anlatıcı istemez; hikâyeyi "
         "görüntüden ve kısa repliklerden kurar. Kanalın imzaları: yavru yaratık aşırı şirin, yetişkini heybetli; küçük güzel sahneler "
         "(bir yemeğin paylaşılması, ilk dokunuş, uyuyakalan yaratığın nefesi yerine 'dinlenen' yaratık) her partide en az bir kez; "
         "seri kancası jenerikten önce. İzleyicinin büyük bölümü telefondan izler: kapak küçük boyutta okunmalı, yüzler ve yaratık "
         "ilk bakışta seçilmelidir. Filmin tamamı tek oturuşta izlenebilir bir 'Full Movie' bütünlüğü taşır; ana soru filmin içinde kapanır.", "",
         "## " + BRIFING_BOLUMLERI[1], "",
         f"- Konu (kullanıcının sözü, aynen): {kk.get('konu_ham', '')}",
         f"- Tür: {kk.get('tur', '—')}; kanca ailesi: {(kk.get('kanca_ailesi') or {}).get('birincil', '—')}"
         + (f" (+ {(kk.get('kanca_ailesi') or {}).get('ikincil')})" if (kk.get('kanca_ailesi') or {}).get('ikincil') else ""),
         f"- Hedef süre: {sure} sn (≈ {dk} dk); üç parti, her biri filmin %30–35'i.",
         f"- Vaat imgesi (kapakta görülecek tek kare; filmde ekranda olmalı): {kk.get('vaat_imgesi', '—')}",
         "- Dil İngilizce; anlatıcı yok; altyazı ayrı dosya. Kullanıcının kesin istekleri: " + ("; ".join(istekler) if istekler else "yok."),
         "- Kalıcı kanal imzaları: insan + yaratık aynı karede kapak; ilk 120 sn içinde vaat imgesi; seri kancası en çok "
         f"{_sayi('seri_kancasi_max_sn')} sn.", "",
         "## " + BRIFING_BOLUMLERI[2], "",
         "Video üretimi Flow'da 8 saniyelik kliplerle yapılır. Bu yüzden hikâye baştan klibe uygun yazılır:",
         f"- Bir klipte tek konuşan (RE konusan_karede_max {_sayi('konusan_karede_max')}); bir karede en çok "
         f"{_sayi('referans_max')} karakter referansı.",
         f"- Replik bloğu 8 sn'de en çok {_sayi('replik_max_kelime_8sn')} kelime, 10 sn'de en çok {_sayi('replik_max_kelime')}; "
         f"{_sayi('ekran_disi_tasima_kelime_esigi')} kelimeden uzun blok ekran dışına bölünebilir diye işaretlenir.",
         f"- Film boyunca konuşan karakter en çok {_sayi('konusan_karakter_max')}; ana karakter en çok {_sayi('ana_karakter_max')} "
         "(yaratık hariç).",
         f"- Filtre kelimeleri replikte ve ekran metninde HİÇ geçmez (replik Veo istemine girer): {filtre}. Yaş ifadesi yazılmaz "
         "('young', '12-year-old'). Güvenli karşılıklar: 'Get some sleep' → 'Rest now'; 'Easy, little one' → 'Easy now. I won't hurt you.'; "
         "'treasure chest' → 'the iron box'. Çocuk kahraman yazılmaz: yetişkine çevrilir ya da yalnız dolaylı anlatılır.",
         "- NE YOK kuralı: dönemde olmayan nesne, malzeme ve söz yazılmaz. Evrenden gelen liste: " + (", ".join(ny) if ny else "(henüz yok)") + ".",
         "- Flow'da zayıf işler: kalabalık savaş, su altı, hızlı dövüş, ekranda okunacak yazı. Bunlar siluet, ses, tepki ve ekleme "
         "planlarıyla çözülür. Kişinin konuşurken el işi yapması aynı satırda yazılmaz; eylem ayrı satırdadır.",
         f"- Mekân sayısı en çok {_sayi('mekan_toplam_max')}, tekrar eden mekân en çok {_sayi('mekan_tekrar_eden_max')}; karakter başına "
         f"kostüm varyantı en çok {_sayi('kostum_varyant_max_karakter')}.", "",
         "## " + BRIFING_BOLUMLERI[3], "",
         f"- Film süresi [{_sayi('film_sure_aralik_sn')}] sn; parti oranı [{_sayi('parti_sure_oran_aralik')}]; vuruşlar RE "
         f"vurus_oranlari ± {_sayi('vurus_oran_tolerans')}.",
         f"- İlk merak sorusu en geç {_sayi('ilk_merak_max_sn')} sn'de; vaat imgesi en geç {_sayi('vaat_imgesi_max_sn')} sn; kahramanın adı "
         f"sözle en geç {_sayi('kahraman_adi_max_sn')} sn; risk sözle en geç {_sayi('risk_sozlu_max_sn')} sn.",
         f"- Parti sonu yoğunluğu ≥ {_sayi('parti_sonu_yogunluk_min')}, doruk ≥ {_sayi('doruk_yogunluk_min')}, en karanlık an ≥ "
         f"{_sayi('en_karanlik_yogunluk_min')}. Her parti açık bir merak sorusuyla biter; sonraki parti ilk "
         f"{_sayi('parti_basi_kanca_donus_max_sn')} sn'de kancaya döner.",
         f"- Merak olayları arası en çok {_sayi('merak_olay_aralik_max_sn')} sn; kurulum kullanımdan en az "
         f"{_sayi('kurulum_kullanim_min_sn')} sn önce; parti başına en az {_sayi('ironi_parti_min')} dramatik ironi.",
         f"- Sahne süresi en çok {_sayi('sahne_max_sn')} sn; 40 dk'da {_sayi('sahne_sayisi_40dk')} sahne (süreyle oranlanır); "
         f"her sahnede sahne değeri değişir (başı ≠ sonu).",
         "- Bu maddelerin hepsini makine denetler (senaryo-denetim); hikâye aşamasında zaman tahminidir, ±%15 bant içindeki sapma BAYRAK'tır.", "",
         "## " + BRIFING_BOLUMLERI[4], ""]
    s += dersler or ["- Henüz doğrulanmış hikâye dersi yok. İlk filmde dersler kâğıt seyircisinden ve kurgu seyircisinden gelecek."]
    s += ["- Seyirci kahramanın neyi kaybedebileceğini ilk üç dakikada bilmelidir; bilmeyen seyirci ilgisini kaybeder (ZANAAT §1.4).",
          "- Bilgi taşıyan replikte çatışma olmalıdır; 'bildiğin gibi' repliği yazılmaz (ZANAAT §4.5).", "",
          "## " + BRIFING_BOLUMLERI[5], "",
          "Her mimar tek dosya teslim eder: `CIKTI/oneri.md`. Dosya şu 10 başlığı bu sırayla, '## <no>. <ad>' biçiminde taşır; "
          "her başlık dolu olmalıdır (makine arar):",
          "1. Logline — EN (en çok 35 kelime), logline_tr ve 3 cümlelik ozet_tr (kullanıcıya bilgi özeti için).",
          "2. Başlık adayları — üç aday, kalıp 'Kanca cümlesi | SERİ ADI | Full Movie 4K 2026', her biri en çok 100 karakter; kanca cümlesi "
          "özne + güçlü geçmiş zaman fiili + yasak ya da bedel nesnesi + karşı güç taşır. Kapak imgesi: filmde olan tek kare.",
          "3. Karakterler — en çok 4 ana, en çok 8 konuşan. Her biri için istek, korku, yara, sır, yay (baş → son); görsel ayırt edici "
          "(hikâyeye bağlı öğeler işaretli); ses karakteri; ad ve telaffuz (ana karakter adı en çok 2 hece, adlar birbirine benzemez).",
          "4. Dönem, 3–5 evren kuralı, NE YOK listesi.",
          "5. Üç partinin tek cümlelik savunması ('P1'de … ile biter') ve vuruş listesi.",
          "6. Soğuk açılış (ilk 30 sn, an an) ve ilk iki dakika.",
          "7. Merak soruları (en az 8), kurulum → kullanım (en az 5), parti başına en az bir ironi.",
          "8. Parti başına en az bir küçük güzel sahne.",
          "9. Seri kancası ve sonraki filmin tek cümlelik tohumu.",
          "10. Üretilebilirlik — riskli sahneler ve çözümü; tekrar eden ve toplam mekân sayısı; kostüm değişimleri; konuşan sayısı.",
          "Dosyanın sonunda bir ```json bloğu bulunur (makine alanları): {\"eksen\", \"logline_en\", \"logline_tr\", \"ozet_tr\", "
          "\"baslik_adaylari\": [3], \"kapak_imgesi\", \"karakterler\": [{\"id\", \"ad\", \"rol\", \"ana\": bool, \"konusur\": bool}], "
          "\"cesitlilik\": {\"kahraman_tipi\", \"cekirdek_iliski\", \"doruk_mekanizmasi\", \"ana_mekan\"}, \"ornek_replikler\": [..], "
          "\"ne_yok\": [..]}. Uzunluk 2.500–5.000 kelime. Önerin başka mimarların önerisini okumaz; bonus (X) mimarı yalnız loglineları "
          "'kaçınılacak yollar' olarak görür.", "",
          "## " + BRIFING_BOLUMLERI[6], "",
          (kk.get("konu_yorumu") or (f"Yapımcının yorumu: konu '{kk.get('konu_ham', '')}' {kk.get('tur', '')} türünde, "
                                     f"{(kk.get('kanca_ailesi') or {}).get('birincil', '')} kanca ailesiyle yazılır. {yonl}").strip()), ""]
    for r in kk.get("riskler") or []:
        if isinstance(r, dict): s.append(f"- Risk ({r.get('tur')}): {r.get('aciklama')} → çözüm: {r.get('cozum')}")
    return "\n".join(s) + "\n"


def brifing(o):
    film = o["film"]; g, yol = baglam(o, "A02", "BRIFING", "_RAPOR/BRIFING_t{tur}.json")
    kk = oku(film, HO, "01_KONU_KARTI.json")
    if not isinstance(kk, dict): return yaz(o, g, yol, "BRIFING", [m("konu_karti_yok", "HATA")], [])
    md = brifing_metni(film, kk); p = os.path.join(film, HO, "00_BRIFING.md"); metin_yaz(p, md)
    sha = hashlib.sha1(md.encode("utf-8")).hexdigest(); metin_yaz(p + ".sha1", sha + "\n")
    olc = []
    bolum = [b for b in BRIFING_BOLUMLERI if ("## " + b) in md]
    if len(bolum) != E("brifing_bolum_sayisi", 7): olc.append(m("brifing_bolum", "HATA", olcu=len(bolum), esik=E("brifing_bolum_sayisi", 7)))
    if "Filtre kelimeleri" not in md or not all(k in md for k in istem_denetim.FILTRE_KELIMELERI):
        olc.append(m("filtre_listesi", "HATA", neden="filtre listesi istem_denetim.FILTRE_KELIMELERI ile aynı değil"))
    w = kelime(md); a = E("brifing_kelime_aralik", [1500, 4000])
    olc.append(m("brifing_kelime", "GEC" if a[0] <= w <= a[1] else sev("brifing_kelime_aralik", "HATA"), olcu=w, esik=a))
    return yaz(o, g, yol, "BRIFING", olc, [f"{HO}/01_KONU_KARTI.json"], ek={"sha1": sha, "kelime": w})


# --- A03 öneriler -----------------------------------------------------------------------------------------------
def oneri_oku(film, eksen):
    md = metin_oku(os.path.join(film, HO, f"02_oneri_{eksen}.md"))
    js = oku(film, HO, f"02_oneri_{eksen}.json")
    if not isinstance(js, dict) and md:
        bl = re.findall(r"```json\s*(\{.*?\})\s*```", md, re.S)
        for b in reversed(bl):
            try: js = json.loads(b); break
            except ValueError: continue
    return md, js if isinstance(js, dict) else None


def oneri_eksenleri(film):
    return [e for e in ("D", "S", "E", "X", "A", "B") if os.path.isfile(os.path.join(film, HO, f"02_oneri_{e}.md"))]


def logline(o):
    film = o["film"]; s = ["# Loglineler (kaçınılacak yollar; metinler okunmaz)", ""]
    for e in oneri_eksenleri(film):
        if e == "X": continue
        _, js = oneri_oku(film, e)
        if js and js.get("logline_en"): s.append(f"- {js['logline_en']}")
    metin_yaz(os.path.join(film, HO, "02_LOGLINELAR.md"), "\n".join(s) + "\n"); print("\n".join(s)); return None


def _basliklar(md):
    hs = [x.strip().lower() for x in re.findall(r"^#{2,3}\s*(.+)$", md or "", re.M)]
    bulunan = []
    for i, ad in enumerate(ONERI_BASLIKLARI, 1):
        if any(h.startswith(f"{i}.") or h.startswith(f"{i})") or ad in h for h in hs): bulunan.append(i)
    return bulunan


def oneri_denetim(o):
    film = o["film"]; g, yol = baglam(o, "A03", "ONERI", "_RAPOR/ONERI_t{tur}.json")
    olc, girdi, dortlu = [], [], {}
    ny = ne_yok(film); eksenler = oneri_eksenleri(film)
    if len(eksenler) < 4: olc.append(m("oneri_sayisi", "HATA", olcu=eksenler, esik=4))
    for e in eksenler:
        md, js = oneri_oku(film, e); girdi.append(f"{HO}/02_oneri_{e}.md")
        b = _basliklar(md); n = E("oneri_baslik_sayisi", 10)
        if len(b) < n: olc.append(m("baslik_eksik", "HATA", birim=e, olcu=[i for i in range(1, n + 1) if i not in b]))
        if not js: olc.append(m("makine_blogu_yok", "HATA", birim=e)); continue
        for bas in js.get("baslik_adaylari") or []:
            if len(bas) > E("baslik_karakter_max", 100): olc.append(m("baslik_uzun", "HATA", birim=e, olcu=len(bas), esik=E("baslik_karakter_max", 100)))
            if not BASLIK_KALIP.match(bas): olc.append(m("baslik_kalip", "BAYRAK", birim=e, olcu=bas))
            elif len(BASLIK_KALIP.match(bas).group(1)) > E("kanca_cumlesi_karakter_max", 60):
                olc.append(m("kanca_cumlesi_uzun", sev("kanca_cumlesi_karakter_max", "BAYRAK"), birim=e, olcu=bas))
        if len(js.get("baslik_adaylari") or []) < 3: olc.append(m("baslik_adayi_sayisi", "HATA", birim=e, olcu=len(js.get("baslik_adaylari") or [])))
        kar = [k for k in js.get("karakterler") or [] if isinstance(k, dict)]
        konusan = [k for k in kar if k.get("konusur", True) and k.get("rol") != "yaratik"]
        if len(konusan) > E("oneri_konusan_max", 8): olc.append(m("konusan_fazla", "HATA", birim=e, olcu=len(konusan)))
        ana = [k for k in kar if k.get("ana") and k.get("rol") != "yaratik"]
        if len(ana) > E("ana_karakter_max", 4): olc.append(m("ana_karakter_fazla", "BAYRAK", birim=e, olcu=len(ana)))
        olc += [dict(x, birim=e) for x in ad_kurallari(kar)]
        for r in js.get("ornek_replikler") or []:
            f = filtre_bul(r)
            if f: olc.append(m("replik_filtre", "HATA", birim=e, olcu=f, neden=r[:80]))
            n2 = istem_denetim.bul(r, ny)
            if n2: olc.append(m("replik_ne_yok", "HATA", birim=e, olcu=n2))
        if kelime(js.get("logline_en")) > E("logline_kelime_max", 35):
            olc.append(m("logline_uzun", sev("logline_kelime_max", "BAYRAK"), birim=e, olcu=kelime(js.get("logline_en"))))
        w = kelime(md); a = E("oneri_kelime_aralik", [2500, 5000])
        if not a[0] <= w <= a[1]: olc.append(m("oneri_kelime", sev("oneri_kelime_aralik", "BAYRAK"), birim=e, olcu=w, esik=a))
        c = js.get("cesitlilik") or {}
        dortlu[e] = tuple(str(c.get(k, "")).strip().lower() for k in ("kahraman_tipi", "cekirdek_iliski", "doruk_mekanizmasi", "ana_mekan"))
    benzer = []
    ek = [e for e in dortlu if e != "X"]
    for i in range(len(ek)):
        for j in range(i + 1, len(ek)):
            a, b = dortlu[ek[i]], dortlu[ek[j]]
            if sum(1 for x, y in zip(a, b) if x and x == y) >= E("oneri_benzerlik_esigi", 3): benzer.append((ek[i], ek[j]))
    for a, b in benzer:
        olc.append(m("BENZER", "HATA" if g["tur_no"] == 1 and g.get("merdiven") is None else "BAYRAK", birim=b, olcu=[a, b],
                     oneri=f"{b} yeni eksenle 1 kez yeniden yazılır" if g["tur_no"] == 1 else "çeşitlilik BAYRAK'ı jüri paketine"))
    if benzer and (g["tur_no"] > 1 or g.get("merdiven") is not None):
        ortak.atomik_yaz(os.path.join(film, HO, "CESITLILIK_BAYRAGI.json"), {"benzer": benzer})
    return yaz(o, g, yol, "ONERI", olc, girdi, ek={"benzer": benzer}, sonuc=None) if olc else \
        yaz(o, g, yol, "ONERI", [m("oneriler", "GEC")], girdi)


def duzenleme(a, b):
    a, b = a.lower(), b.lower(); d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, y in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (x != y))
    return d[len(b)]


def hece(ad): return max(1, len(re.findall(r"[aeiouyAEIOUYıİöÖüÜ]+", ad or "")))


def ad_kurallari(kar):
    out = []; adlar = [(k.get("id"), k.get("ad")) for k in kar if k.get("ad")]
    for kid, ad in adlar:
        k = next((x for x in kar if x.get("id") == kid), {})
        if k.get("ana") and hece(ad) > E("ad_hece_max_ana", 2): out.append(m("ad_hece", sev("ad_hece_max_ana", "BAYRAK"), olcu=ad))
    for i in range(len(adlar)):
        for j in range(i + 1, len(adlar)):
            a, b = adlar[i][1], adlar[j][1]
            if a[:1].lower() == b[:1].lower() or duzenleme(a, b) < E("ad_duzenleme_uzaklik_min", 3):
                out.append(m("ad_ayrisma", sev("ad_duzenleme_uzaklik_min", "BAYRAK"), olcu=[a, b]))
    return out


# --- A04 jüri ---------------------------------------------------------------------------------------------------
def juri_paketi(o):
    film = o["film"]; eks = [e for e in oneri_eksenleri(film)]
    rnd = random.Random(int(hashlib.sha1(("|".join(eks) + film).encode()).hexdigest()[:8], 16)); sira = list(eks); rnd.shuffle(sira)
    anahtar, kl = {}, os.path.join(film, HO, "JURI_PAKETI")
    for k, e in enumerate(sira, 1):
        md, _ = oneri_oku(film, e)
        md = re.sub(r"```json.*?```", "", md or "", flags=re.S)
        md = re.sub(r"(?im)^.*\beksen\b.*$", "", md)
        metin_yaz(os.path.join(kl, f"Oneri_{k}.md"), f"# Öneri {k}\n\n" + md.strip() + "\n")
        anahtar[str(k)] = e
    cb = oku(film, HO, "CESITLILIK_BAYRAGI.json")
    if cb: metin_yaz(os.path.join(kl, "CESITLILIK_NOTU.md"), "Not: önerilerden bazıları birbirine benziyor (çeşitlilik BAYRAK'ı).\n")
    ortak.atomik_yaz(os.path.join(film, HO, "JURI_ANAHTAR.json"), {"anahtar": anahtar, "_not": "jüriye verilmez"})
    print(json.dumps({"oneriler": len(anahtar)}, ensure_ascii=False)); return None


def juri_oku(film):
    out, hatalar = {}, []
    olcutler = E("juri_olcutleri", [])
    for rol in JURI_ROLLERI:
        p = os.path.join(film, HO, f"03_juri_{rol}.json"); j = ortak.json_oku(p)
        if not isinstance(j, dict) or not isinstance(j.get("oneriler"), dict):
            hatalar.append(m("juri_sema", "BAYRAK", birim=rol, neden="rapor yok ya da şemaya uymuyor")); continue
        ok = True
        for no, x in j["oneriler"].items():
            pu = (x or {}).get("puan") or {}; ge = (x or {}).get("gerekce") or {}
            eks = [k for k in olcutler if not isinstance(pu.get(k), (int, float)) or not 1 <= pu[k] <= 10]
            if eks: hatalar.append(m("juri_puan_eksik", "BAYRAK", birim=rol, olcu={no: eks})); ok = False
            if not ge: hatalar.append(m("juri_gerekce_yok", "BAYRAK", birim=rol, olcu=no))
        if ok: out[rol] = j
    return out, hatalar


def juri_topla(o):
    film = o["film"]; g, yol = baglam(o, "A04", "JURI", "_RAPOR/JURI_t{tur}.json")
    juri, olc = juri_oku(film)
    anahtar = (oku(film, HO, "JURI_ANAHTAR.json") or {}).get("anahtar") or {}
    girdi = [f"{HO}/03_juri_{r}.json" for r in JURI_ROLLERI]
    if len(juri) < E("juri_gecerli_min", 3):
        olc.append(m("juri_gecerli", "HATA", olcu=len(juri), esik=E("juri_gecerli_min", 3)))
        return yaz(o, g, yol, "JURI", olc, girdi)
    olcutler = E("juri_olcutleri", []); nolar = sorted({n for j in juri.values() for n in j["oneriler"]}, key=lambda x: int(x) if x.isdigit() else 99)
    puan, med, veto = {}, {}, {}
    for n in nolar:
        med[n] = {k: puan_oku.medyan([j["oneriler"][n]["puan"][k] for j in juri.values() if n in j["oneriler"]]) for k in olcutler}
        vs = [k for k in med[n].values() if k is not None]
        puan[n] = round(sum(vs) / len(vs), 3) if vs else 0
        vt = [j["oneriler"][n].get("veto") for j in juri.values() if n in j["oneriler"] and j["oneriler"][n].get("veto")]
        if (med[n].get("uretilebilirlik") or 10) < E("juri_veto_uretilebilirlik", 5): vt.append("uretilebilirlik medyanı < eşik")
        if vt: veto[n] = vt
    sira = sorted(nolar, key=lambda n: (-puan[n], n)); aday = [n for n in sira if n not in veto]
    kazanan = aday[0] if aday else None
    esik = E("juri_kazanan_min", 8.0)
    birlestir = len(aday) >= 2 and puan[aday[0]] - puan[aday[1]] <= E("juri_beraberlik_fark", 0.3)
    ilk_tur = g["tur_no"] == 1 and g.get("merdiven") is None
    if kazanan is None: olc.append(m("hepsi_vetolu", "HATA", olcu=veto))
    elif puan[kazanan] < esik:
        olc.append(m("kazanan_esik_alti", "HATA" if ilk_tur else "BAYRAK", olcu=puan[kazanan], esik=esik,
                     oneri="kazanan yazar 'mutlaka düzelt' maddeleriyle 1 kez yeniden yazar" if ilk_tur else "hedef_alti ile devam"))
    for n, v in veto.items(): olc.append(m("veto", "BAYRAK", birim=f"Oneri_{n}", olcu=v))
    mutlaka = sorted({x for j in juri.values() for x in (j["oneriler"].get(kazanan) or {}).get("mutlaka_duzelt") or []}) if kazanan else []
    calin = sorted({x for j in juri.values() for n in nolar if n != kazanan for x in (j["oneriler"].get(n) or {}).get("calinmaya_deger") or []})
    secim = {"_uretim": {"asama": "A04", "gorev": g["id"], "arac_surum": SURUM}, "tur": g["tur_no"],
             "kazanan_oneri": kazanan, "kazanan_eksen": anahtar.get(kazanan), "puanlar": puan, "medyanlar": med, "siralama": sira,
             "veto": veto, "birlestir": birlestir, "birlestirilecek": anahtar.get(aday[1]) if birlestir else None,
             "ikinci_eksen": anahtar.get(aday[1]) if len(aday) > 1 else None, "mutlaka_duzelt": mutlaka, "calinmaya_deger": calin,
             "hedef_alti": bool(kazanan and puan[kazanan] < esik), "esik": esik}
    if kazanan:
        _, js = oneri_oku(film, anahtar.get(kazanan, ""))
        js = js or {}
        bas = (js.get("baslik_adaylari") or [None])[0]
        mm = BASLIK_KALIP.match(bas or "")
        secim["seri_adi"] = evren.seri_normal(mm.group(2)) if mm else None
        secim["baslik_adaylari"] = js.get("baslik_adaylari") or []
        metin_yaz(os.path.join(film, HO, "04_KULLANICIYA_OZET.md"),
                  f"# Seçilen hikâye\n\n{js.get('logline_tr') or ''}\n\n{js.get('ozet_tr') or ''}\n\n"
                  f"Jüri puanı: {puan[kazanan]:.1f} / 10 (5 bağımsız jüri, medyan)." + (" Eşiğin altında başladı; ekip düzeltiyor." if secim["hedef_alti"] else "") + "\n")
    ortak.atomik_yaz(os.path.join(film, HO, "04_SECIM.json"), secim)
    if not olc: olc.append(m("juri", "GEC", olcu=puan.get(kazanan)))
    return yaz(o, g, yol, "JURI", olc, girdi, ek={"kazanan": kazanan, "puan": puan.get(kazanan)})


# --- A05 yapı ---------------------------------------------------------------------------------------------------
def sahne_listesi(h): return [s for s in h.get("sahneler") or [] if isinstance(s, dict) and s.get("id")]


def parti_sahneleri(h, pid):
    return [s for s in sahne_listesi(h) if s.get("hikaye_partisi") == pid]


def yapi_denetim(o):
    film = o["film"]; g, yol = baglam(o, "A05", "YAPI", "_RAPOR/YAPI_t{tur}.json")
    y = oku(film, HO, "05_YAPI.json"); olc = []
    if not isinstance(y, dict): return yaz(o, g, yol, "YAPI", [m("yapi_yok", "HATA")], [])
    partiler = [p for p in y.get("partiler") or [] if isinstance(p, dict)]
    if len(partiler) != E("parti_sayisi", 3): olc.append(m("parti_sayisi", "HATA", olcu=len(partiler), esik=E("parti_sayisi", 3)))
    film_sn = y.get("film_sure_hedef_sn") or sum(p.get("sure_hedef_sn") or 0 for p in partiler) or None
    oran = E("parti_sure_oran_aralik", [0.30, 0.35])
    for i, p in enumerate(partiler, 1):
        pid = p.get("id") or f"P{i}"
        bos = [b for b in YAPI_BASLIKLARI if not p.get(b)]
        if bos: olc.append(m("parti_baslik", "HATA", birim=pid, olcu=bos))
        tc = (p.get("tek_cumle") or "").strip()
        if not tc: olc.append(m("parti_tek_cumle", "HATA", birim=pid))
        elif not re.match(rf"^{pid}'?[dt][ea]\b", tc) or "biter" not in tc: olc.append(m("parti_tek_cumle_kalip", "BAYRAK", birim=pid, olcu=tc))
        if film_sn and p.get("sure_hedef_sn"):
            r = p["sure_hedef_sn"] / film_sn
            if not (oran[0] - 0.005 <= r <= oran[1] + 0.005): olc.append(m("parti_oran", "BAYRAK", birim=pid, olcu=round(r, 3), esik=oran))
        kanca = p.get("b7_parti_kancasi") or {}
        if i < len(partiler) and (kanca.get("yogunluk") or 0) < E("parti_sonu_yogunluk_min", 8):
            olc.append(m("parti_sonu_yogunluk", "HATA", birim=pid, olcu=kanca.get("yogunluk"), esik=E("parti_sonu_yogunluk_min", 8)))
        no = len([x for x in y.get("anahtar_olgular") or [] if isinstance(x, dict) and x.get("hikaye_partisi") == pid])
        a = E("anahtar_olgu_parti", [8, 12])
        if not a[0] <= no <= a[1]: olc.append(m("anahtar_olgu_parti", sev("anahtar_olgu_parti", "BAYRAK"), birim=pid, olcu=no, esik=a))
    sahneler = sahne_listesi(y)
    for s in sahneler:
        sd = s.get("sahne_degeri") or {}
        if not sd.get("bas") or sd.get("bas") == sd.get("son"):
            olc.append(m("sahne_degeri", "HATA", birim=s["id"], olcu=sd))
    vur = {s.get("vurus"): s for s in sahneler if s.get("vurus")}
    if "doruk" in vur and (vur["doruk"].get("yogunluk") or 0) < E("doruk_yogunluk_min", 9):
        olc.append(m("doruk_yogunluk", "HATA", birim=vur["doruk"]["id"], olcu=vur["doruk"].get("yogunluk")))
    if "en_karanlik" in vur and (vur["en_karanlik"].get("yogunluk") or 0) < E("en_karanlik_yogunluk_min", 6):
        olc.append(m("en_karanlik_yogunluk", "HATA", birim=vur["en_karanlik"]["id"], olcu=vur["en_karanlik"].get("yogunluk")))
    for v in ("doruk", "en_karanlik"):
        if v not in vur: olc.append(m(f"vurus_{v}_yok", "BAYRAK"))
    olc += vurus_denetle(y, sahneler, film_sn)
    sira = {s["id"]: i for i, s in enumerate(sahneler)}
    olc += kurulum_denetle(y, sira, None)
    for x in y.get("anahtar_olgular") or []:
        if isinstance(x, dict) and not x.get("ekranda"): olc.append(m("olgu_kaynaksiz", "HATA", birim=x.get("id")))
    if not olc: olc.append(m("yapi", "GEC"))
    return yaz(o, g, yol, "YAPI", olc, [f"{HO}/05_YAPI.json"])


def zaman_cizelgesi(h):
    """{sahne_id: (bas_sn, sure_sn)} — hedef_sure_sn ile replik süresinin büyüğü (ZN §2.3: kelime / konusma_hizi + cümle arası)."""
    hiz = float(E("konusma_hizi_kelime_sn", 2.5)); ara = float(E("cumle_arasi_sn", 0.25))
    rep = {}
    for r in h.get("replikler") or []:
        if isinstance(r, dict):
            n = kelime(r.get("metin")); c = max(1, len(re.findall(r"[.!?]+", r.get("metin") or "")))
            rep[r.get("sahne")] = rep.get(r.get("sahne"), 0) + n / hiz + ara * (c - 1) + 0.6
    out, t = {}, 0.0
    for s in sahne_listesi(h):
        d = max(float(s.get("hedef_sure_sn") or 0), rep.get(s["id"], 0) + 2.0)
        out[s["id"]] = (t, d); t += d
    return out


def vurus_denetle(h, sahneler, film_sn):
    out = []; vo = E("vurus_oranlari", {}) or {}; tol = E("vurus_oran_tolerans", 0.04)
    zc = zaman_cizelgesi(h); toplam = sum(d for _, d in zc.values()) or film_sn
    if not toplam: return out
    for s in sahneler:
        v = s.get("vurus")
        if v in vo and s["id"] in zc:
            r = zc[s["id"]][0] / toplam
            if abs(r - vo[v]) > tol and not (zc[s["id"]][0] <= vo[v] * toplam <= zc[s["id"]][0] + zc[s["id"]][1]):
                out.append(m("vurus_konumu", "BAYRAK", birim=s["id"], olcu=round(r, 3), esik=vo[v], vurus=v))
    return out


def kurulum_denetle(h, sira, zc):
    out = []
    for k in h.get("KURULUMLAR") or []:
        if not isinstance(k, dict): continue
        a, b = k.get("kurulum"), k.get("kullanim")
        if a not in sira: out.append(m("kurulum_yok", "HATA", birim=k.get("id"), olcu=a)); continue
        if not b: out.append(m("kurulum_kullanilmadi", "BAYRAK", birim=k.get("id"))); continue
        if b not in sira or sira[b] < sira[a]: out.append(m("kurulum_sirasi", "HATA", birim=k.get("id"), olcu=[a, b])); continue
        if zc and b in zc and a in zc:
            fark = zc[b][0] - zc[a][0]
            if fark < E("kurulum_kullanim_min_sn", 20): out.append(m("kurulum_kullanim_yakin", "BAYRAK", birim=k.get("id"), olcu=round(fark)))
            if fark > E("hatirlatma_esigi_sn", 600) and not k.get("hatirlatma"):
                out.append(m("hatirlatma_yok", "BAYRAK", birim=k.get("id"), olcu=round(fark)))
    return out


# --- A05 oyuncu paketi ------------------------------------------------------------------------------------------
def oyuncu_paketi(o):
    film = o["film"]; n, p, h = son_senaryo(film)
    if not h: print("!! senaryo yok"); return HATA
    kl = os.path.join(film, HO, "OYUNCU_PAKETI"); sahne = {s["id"]: s for s in sahne_listesi(h)}
    onceki = ortak.json_oku(os.path.join(film, HO, f"06_SENARYO_v{n - 1}.json")) if n and n > 1 else None
    eski = {r.get("id"): r.get("metin") for r in (onceki or {}).get("replikler") or [] if isinstance(r, dict)}
    reps = [r for r in h.get("replikler") or [] if isinstance(r, dict)]
    degisen = sorted({r.get("karakter") for r in reps if eski.get(r.get("id")) != r.get("metin")}) if onceki else None
    for kid, k in (h.get("karakterler") or {}).items():
        if not isinstance(k, dict) or k.get("konusmaz"): continue
        s = [f"# Oyuncu kartı — {k.get('ad', kid)}", "", f"- Bildikleri (başta): {', '.join(k.get('bildikleri_bas') or []) or '—'}",
             f"- İstek: {k.get('istek', '—')} · Korku: {k.get('korku', '—')} · Sır: {k.get('sir', '—')}",
             f"- Konuşma tarzı: {k.get('konusma_tarzi', '—')}", "", "## Replikler (her birinin önündeki ekran olayı ve önceki replik)", ""]
        onc = None
        for r in reps:
            if r.get("karakter") == kid:
                ek = ((sahne.get(r.get("sahne")) or {}).get("ekran") or {}).get("gorulen") or []
                s += [f"### {r.get('id')} ({r.get('sahne')}, {r.get('teslim', 'normal')})", f"Önceki ekran olayı: {ek[-1] if ek else '—'}",
                      f"Önceki replik: {onc or '—'}", f"Replik: \"{r.get('metin')}\"", ""]
            onc = f"{r.get('karakter')}: \"{r.get('metin')}\""
        metin_yaz(os.path.join(kl, f"{kid}.md"), "\n".join(s) + "\n")
    metin_yaz(os.path.join(kl, "DIYALOG_PAKETI.md"), "# Bütün replikler\n\n" + "\n".join(
        f"- {r.get('id')} {r.get('karakter')} ({r.get('teslim', 'normal')}): {r.get('metin')}" for r in reps) +
        f"\n\nDönem: {json.dumps(h.get('donem'), ensure_ascii=False)}\nNE YOK: {', '.join(ne_yok(film)) or '—'}\n")
    ortak.atomik_yaz(os.path.join(kl, "DEGISEN.json"), {"surum": n, "degisen_karakterler": degisen})
    print(json.dumps({"surum": n, "degisen": degisen}, ensure_ascii=False)); return None


# --- A05 senaryo denetimi ---------------------------------------------------------------------------------------
def _durum_esit(c, g, atlama):
    """Sahne sınırı: çıkış ↔ giriş farkları."""
    fark = []
    for vid, v in ((c or {}).get("varliklar") or {}).items():
        w = ((g or {}).get("varliklar") or {}).get(vid)
        if not isinstance(w, dict) or not isinstance(v, dict): continue
        for a in DURUM_ALANLARI:
            if a in v and a in w and v[a] != w[a] and not (a == "mekan" and atlama): fark.append(f"{vid}.{a}: {v[a]} → {w[a]}")
    for nid, v in ((c or {}).get("nesneler") or {}).items():
        w = ((g or {}).get("nesneler") or {}).get(nid)
        if not isinstance(w, dict) or not isinstance(v, dict): continue
        for a in NESNE_ALANLARI:
            if a in v and a in w and v[a] != w[a]: fark.append(f"{nid}.{a}: {v[a]} → {w[a]}")
    return fark


def senaryo_olcumleri(film, h):
    olc = []; sahneler = sahne_listesi(h); zc = zaman_cizelgesi(h); sira = {s["id"]: i for i, s in enumerate(sahneler)}
    kar = {k: v for k, v in (h.get("karakterler") or {}).items() if isinstance(v, dict)}
    reps = [r for r in h.get("replikler") or [] if isinstance(r, dict)]
    ny = ne_yok(film); toplam = sum(d for _, d in zc.values())
    if not sahneler: return [m("sahne_yok", "HATA")], zc
    a = E("film_sure_aralik_sn", [1800, 2700])
    s1 = bant(toplam, a[0], "film_sure_aralik_sn", "min"); s2 = bant(toplam, a[1], "film_sure_aralik_sn", "max")
    olc.append(m("film_suresi", s1 if s1 != "GEC" else s2, olcu=round(toplam), esik=a))
    oran = toplam / 2400.0
    ss = E("sahne_sayisi_40dk", [45, 55]); ar = [round(ss[0] * oran), round(ss[1] * oran)]
    if not ar[0] <= len(sahneler) <= ar[1]: olc.append(m("sahne_sayisi", "BAYRAK", olcu=len(sahneler), esik=ar))
    rk = E("replik_toplam_kelime_40dk", [2100, 2600]); top_k = sum(kelime(r.get("metin")) for r in reps)
    if not round(rk[0] * oran) <= top_k <= round(rk[1] * oran): olc.append(m("replik_toplam_kelime", "BAYRAK", olcu=top_k,
                                                                           esik=[round(rk[0] * oran), round(rk[1] * oran)]))
    for s in sahneler:
        d = zc[s["id"]][1]; sv = bant(d, E("sahne_max_sn", 180), "sahne_max_sn")
        if sv != "GEC": olc.append(m("sahne_suresi", sv, sahne=s["id"], birim=s["id"], olcu=round(d), esik=E("sahne_max_sn", 180)))
        sd = s.get("sahne_degeri") or {}
        if not sd.get("bas") or sd.get("bas") == sd.get("son"): olc.append(m("sahne_degeri", "HATA", birim=s["id"]))
        ek = s.get("ekran") or {}
        gor = " ".join(ek.get("gorulen") or [])
        f = filtre_bul(gor)
        if f: olc.append(m("ekran_filtre", "HATA", birim=s["id"], olcu=f))
        n2 = istem_denetim.bul(gor, ny)
        if n2: olc.append(m("ekran_ne_yok", "HATA", birim=s["id"], olcu=n2))
        ic = istem_denetim.bul(gor, istem_denetim.IC_DURUM_FIILLERI)
        if ic: olc.append(m("ic_durum_fiili", "BAYRAK", birim=s["id"], olcu=ic))
        ys = istem_denetim.bul(gor, list(E("yasak_sonuc_fiilleri", [])))
        if ys: olc.append(m("sonuc_fiili", "BAYRAK", birim=s["id"], olcu=ys))
    # sahne sınırı
    for i in range(len(sahneler) - 1):
        a_, b_ = sahneler[i], sahneler[i + 1]
        atl = str((b_.get("zaman") or {}).get("atlama") or "yok") != "yok"
        fark = _durum_esit(a_.get("cikis_durumu"), b_.get("giris_durumu"), atl)
        if fark and not atl and not b_.get("sinir_olayi"):
            olc.append(m("sahne_siniri", "HATA", birim=b_["id"], olcu=fark[:5], neden=f"{a_['id']} çıkışı ≠ {b_['id']} girişi"))
    # replikler
    ilk = {}; onceki = None; ard = 0; bilen = {kid: set(k.get("bildikleri_bas") or []) | {f"ad:{kid}"} for kid, k in kar.items()}
    sahne_rep = {}
    for r in reps: sahne_rep.setdefault(r.get("sahne"), []).append(r)
    kon = set()
    for s in sahneler:
        varlik = set(((s.get("giris_durumu") or {}).get("varliklar") or {}).keys())
        yeni_ad = set()
        for r in sahne_rep.get(s["id"], []):
            rid = r.get("id"); kid = r.get("karakter")
            olc += [dict(x, birim=rid) for x in istem_denetim.replik_denetle(r.get("metin"), 8, ny)]
            if kid not in kar: olc.append(m("replik_karakter_tanimsiz", "HATA", birim=rid, olcu=kid)); continue
            kon.add(kid)
            if not r.get("tasidigi"): olc.append(m("replik_tasidigi", "HATA", birim=rid))
            if kid not in ilk:
                ilk[kid] = rid
                ekran_disi = rid in ((s.get("ekran") or {}).get("ekran_disi") or []) or r.get("ekran_disi")
                if (ekran_disi or not r.get("ilk_replik")) and not (kar[kid].get("gizemli_ses") and r.get("merak")):
                    olc.append(m("ilk_replik_ekranda", "HATA", birim=rid, olcu=kid))
            ard = ard + 1 if kid == onceki else 1; onceki = kid
            if ard > E("monolog_ardisik_plan_max", 3): olc.append(m("ardisik_blok", "BAYRAK", birim=rid, olcu=ard))
            ga = r.get("gorunus_atfi")
            if ga:
                hb = [x.get("oge") for kk in kar.values() for x in kk.get("gorsel_ayirt_edici") or []
                      if isinstance(x, dict) and x.get("hikaye_baglayici")]
                if ga not in hb: olc.append(m("gorunus_atfi", "HATA", birim=rid, olcu=ga))
            for ad in r.get("ad_soyler") or []:
                if ad not in bilen.get(kid, set()) and f"ad:{ad}" not in bilen.get(kid, set()) and ad != kid:
                    olc.append(m("bilgi_durumu", "HATA", birim=rid, olcu=f"{kid} → {ad}", neden="karakter bu adı bilmiyor"))
                for v in varlik | {kid}:
                    if v in bilen: bilen[v].add(f"ad:{ad}")
                if ad not in yeni_ad: yeni_ad.add(ad)
        for b in s.get("bilgi_degisimi") or []:
            if isinstance(b, dict) and b.get("kim") in bilen and b.get("ogrenir"): bilen[b["kim"]].add(b["ogrenir"])
        if len(yeni_ad) > E("sahne_yeni_ad_max", 2): olc.append(m("sahne_yeni_ad", "BAYRAK", birim=s["id"], olcu=len(yeni_ad)))
    if len(kon) > E("konusan_karakter_max", 8): olc.append(m("konusan_sayisi", "BAYRAK", olcu=len(kon)))
    # kanon (evren)
    seri = evren.film_serisi(film, h)
    if seri:
        for kid in kon:
            c = ortak.json_oku(evren.seri_yolu(seri, "karakterler", kid, "hikaye.json"), {}) or {}
            if c.get("durum") == "olu": olc.append(m("kanon", "HATA", birim=kid, neden="evrende ölü karakter konuşuyor"))
    # anahtar olgular
    rid = {r.get("id") for r in reps}
    for x in h.get("anahtar_olgular") or []:
        if not isinstance(x, dict): continue
        kay = [e for e in x.get("ekranda") or [] if e in sira or e in rid]
        if x.get("kritik") and not kay: olc.append(m("kritik_olgu_kaynaksiz", "HATA", birim=x.get("id")))
    # merak, vaat, ad, risk
    acik_bas = [zc[s["id"]][0] for s in sahneler if s.get("merak_ac")]
    if acik_bas:
        sv = bant(min(acik_bas), E("ilk_merak_max_sn", 20), "ilk_merak_max_sn")
        if sv != "GEC": olc.append(m("ilk_merak", sv, olcu=round(min(acik_bas)), esik=E("ilk_merak_max_sn", 20)))
    else: olc.append(m("merak_yok", "HATA"))
    olc += vaat_olcumleri(h, zc, sira)
    kahraman = next((kid for kid, k in kar.items() if k.get("rol") == "kahraman"), None)
    if kahraman:
        t = next((zc[r["sahne"]][0] for r in reps if kahraman in (r.get("ad_soyler") or []) and r.get("sahne") in zc), None)
        sv = bant(t, E("kahraman_adi_max_sn", 120), "kahraman_adi_max_sn") if t is not None else "HATA"
        if sv != "GEC": olc.append(m("kahraman_adi", sv, olcu=None if t is None else round(t), esik=E("kahraman_adi_max_sn", 120)))
    # parti sonu açık soru
    md = {q.get("id"): q for q in h.get("MERAK_DEFTERI") or [] if isinstance(q, dict)}
    for p in h.get("partiler") or []:
        ps = parti_sahneleri(h, p.get("id"))
        if not ps: continue
        son = sira[ps[-1]["id"]]
        acik = [q for q in md.values() if q.get("ac") in sira and sira[q["ac"]] <= son and (q.get("kapat") not in sira or sira[q["kapat"]] > son)]
        if len(acik) < E("parti_sonu_acik_soru_min", 1): olc.append(m("parti_sonu_acik_soru", "HATA", birim=p.get("id")))
    olc += kurulum_denetle(h, sira, zc)
    seri_q = [q for q in md.values() if q.get("tur") == "seri" and not q.get("kapat")]
    if len(seri_q) > E("seri_sorusu_max", 2): olc.append(m("seri_sorusu", "BAYRAK", olcu=len(seri_q)))
    return olc, zc


def vaat_olcumleri(h, zc, sira, baslik=None):
    olc = []
    for v in h.get("vaat_sozlesmesi") or []:
        if not isinstance(v, dict): continue
        s = v.get("sahne")
        if s not in sira: olc.append(m("vaat_sahnesi_yok", "HATA", olcu=v.get("oge"))); continue
        if v.get("oge") == "kapak_imgesi":
            sv = bant(zc[s][0], E("vaat_imgesi_max_sn", 120), "vaat_imgesi_max_sn")
            if sv != "GEC": olc.append(m("vaat_imgesi", sv, olcu=round(zc[s][0]), esik=E("vaat_imgesi_max_sn", 120)))
        if v.get("sozlu"):
            sv = bant(zc[s][0], E("risk_sozlu_max_sn", 180), "risk_sozlu_max_sn")
            if sv != "GEC": olc.append(m("risk_sozlu", sv, olcu=round(zc[s][0]), esik=E("risk_sozlu_max_sn", 180)))
    if not any((v or {}).get("oge") == "kapak_imgesi" for v in h.get("vaat_sozlesmesi") or []):
        olc.append(m("kapak_imgesi_baglanmamis", "HATA"))
    b = baslik or ((h.get("baslik") or {}).get("secilen") if isinstance(h.get("baslik"), dict) else h.get("baslik"))
    if b:
        if len(b) > E("baslik_karakter_max", 100): olc.append(m("baslik_uzun", "HATA", olcu=len(b)))
        if not BASLIK_KALIP.match(b): olc.append(m("baslik_kalip", "BAYRAK", olcu=b))
        if re.search(r"\bkill", b, re.I): olc.append(m("baslik_kill", "BAYRAK", olcu=b))
    return olc


def senaryo_denetim(o):
    film = o["film"]; g, yol = baglam(o, "A05", "SEMA", "_RAPOR/HIKAYE_Z_v{tur}.json")
    n, p, h = son_senaryo(film)
    if not h: return yaz(o, g, yol, "SEMA", [m("senaryo_yok", "HATA")], [])
    olc, zc = senaryo_olcumleri(film, h)
    hatalar = [x for x in olc if x["seviye"] == "HATA" and (x.get("birim") or x.get("sahne"))]
    if hatalar:
        try:
            kmap = {"bilgi_durumu": "bilgi_durumu_ihlali", "kanon": "kanon_ihlali", "kurulum_sirasi": "kurulum_yok",
                    "kurulum_yok": "kurulum_yok", "kritik_olgu_kaynaksiz": "bilgi_ekranda_yok"}
            rs = {r.get("id"): r.get("sahne") for r in h.get("replikler") or [] if isinstance(r, dict)}
            md = []
            for x in hatalar:
                b = x.get("birim") or x.get("sahne"); sah = b if re.fullmatch(r"S\d{2,}", str(b)) else rs.get(b)
                if sah: md.append({"konum": {"sahne": sah}, "kapi": "SEMA", "madde": x["madde"], "kok_neden": kmap.get(x["madde"], "bilgi_eksik"),
                                   "yazar": "hikaye-yazari", "oneri": x.get("oneri") or x.get("neden") or x["madde"], "tur": g["tur_no"]})
            if md and kuyruk: kuyruk.yaz_ekle(film, md, "A05")
        except Exception as e:                     # kuyruk yazılamazsa rapor yine yazılır; madde raporda kalır
            print(f"   (YENIDEN_YAZ yazılamadı: {e.__class__.__name__}: {e})", file=sys.stderr)
    if not olc: olc.append(m("senaryo", "GEC"))
    return yaz(o, g, yol, "SEMA", olc, [os.path.relpath(p, film)], ek={"senaryo_surum": n, "film_sure_tahmin_sn": round(sum(d for _, d in zc.values()))})


# --- A06 --------------------------------------------------------------------------------------------------------
def seyirci_topla_k(o):
    g = puan_oku.gorev_baglami(o.get("--tur"), "A06")
    r = puan_oku.seyirci_topla(o["film"], o.get("--kip") or "kagit", g["tur_no"], g["id"], g.get("merdiven"),
                               os.path.join(o["film"], g["rapor"]) if g.get("rapor") else None, g.get("asama"))
    print(json.dumps({"sonuc": r["sonuc"], "medyan": r["medyan"], "neden": r["neden"]}, ensure_ascii=False)); return None


def ilk2dk_topla_k(o):
    g = puan_oku.gorev_baglami(o.get("--tur"), "A06")
    r = puan_oku.ilk2dk_topla(o["film"], o.get("--kip") or "kagit", g["tur_no"], g["id"],
                              os.path.join(o["film"], g["rapor"]) if g.get("rapor") else None)
    print(r["sonuc"]); return None


def _son_hs(film):
    rs = []
    for p in glob.glob(os.path.join(film, "_RAPOR", "HS_KAGIT_FILM_t*.json")):
        mm = re.search(r"_t(\d+)\.json$", p)
        j = ortak.json_oku(p)
        if mm and isinstance(j, dict): rs.append((int(mm.group(1)), j))
    return max(rs, key=lambda x: x[0]) if rs else (None, None)


def hikaye_md(h):
    s = [f"# {((h.get('baslik') or {}).get('secilen') if isinstance(h.get('baslik'), dict) else h.get('baslik')) or h.get('logline', '')}", "",
         f"Logline: {h.get('logline', '')}", f"Evren: {h.get('evren')} · süre hedefi: {h.get('film_sure_hedef_sn')} sn · sürüm {h.get('_surum')}", ""]
    for p in h.get("partiler") or []:
        s += [f"## {p.get('id')}", "", p.get("tek_cumle") or "", ""]
        for sc in parti_sahneleri(h, p.get("id")):
            s.append(f"### {sc['id']} — {sc.get('mekan', '')} ({sc.get('hedef_sure_sn', '?')} sn)")
            for x in (sc.get("ekran") or {}).get("gorulen") or []: s.append(f"- {x}")
            for r in h.get("replikler") or []:
                if isinstance(r, dict) and r.get("sahne") == sc["id"]:
                    ad = ((h.get("karakterler") or {}).get(r.get("karakter")) or {}).get("ad", r.get("karakter"))
                    s.append(f"  - {ad.upper()}: \"{r.get('metin')}\"")
            s.append("")
    return "\n".join(s) + "\n"


def devir(o):
    film = o["film"]; n, p, h = son_senaryo(film)
    if not h: print("!! senaryo yok; devir yapılamadı"); return HATA
    tur, hs = _son_hs(film)
    if not hs or hs.get("sonuc") not in ("GEC", "BAYRAK", "KISMI"):
        print("!! HS_KAGIT kapısı sağlanmadan kilit yok"); return HATA
    eksik = [a for a in ("karakterler", "sahneler", "replikler", "anahtar_olgular", "partiler") if not h.get(a)]
    if eksik: print("!! HIKAYE şeması eksik: " + ", ".join(eksik)); return HATA
    g = puan_oku.gorev_baglami(o.get("--tur"), "A06")
    h = json.loads(json.dumps(h))
    seri = evren.film_serisi(film, h)
    karar = ortak.json_oku(os.path.join(film, "_RAPOR", f"SEYIRCI_KARAR_KAGIT_t{tur}.json"), {}) or {}
    h.update({"_sahip": "hikaye-yazari", "_surum": f"v{n}", "kilit": True, "evren": seri,
              "_uretim": {"asama": "A06", "gorev": g["id"], "girdi_imza": puan_oku.dosya_imza(film, [os.path.relpath(p, film)]),
                          "arac_surum": SURUM, "esik_surum": getattr(__import__("esikler"), "SURUM", None), "sonuc": hs.get("sonuc"),
                          "zaman": kapi.simdi(), "ortam": kapi.ortam()},
              "seyirci_kagit": {"tur": tur, "sonuc": hs.get("sonuc"), "medyan": karar.get("medyan"), "hedef_alti": bool(karar.get("hedef_alti"))},
              "ilk2dk_surum": ((karar.get("ilk2dk") or {}).get("secilen"))})
    ortak.atomik_yaz(os.path.join(film, "HIKAYE.json"), h)
    metin_yaz(os.path.join(film, "HIKAYE.md"), hikaye_md(h))
    r, kod = evren.on_kayit(film, seri)
    print(json.dumps({"hikaye": f"v{n}", "evren": r}, ensure_ascii=False))
    return None if kod == 0 else HATA


def _planlar(film):
    out = []
    s = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    if int(s.get("_surum", 1) or 1) >= 2: out += [x for x in s.get("sahneler") or [] if isinstance(x, dict)]
    for p in sorted(glob.glob(os.path.join(film, "_YONETMEN", "PLANLAR", "*.json"))):
        j = ortak.json_oku(p, {}) or {}
        out += [x for x in (j.get("planlar") or j.get("sahneler") or []) if isinstance(x, dict)]
    return sorted(out, key=lambda x: (x.get("sira") if x.get("sira") is not None else x.get("no") or 0))


def sahne_sozlesme(o):
    film = o["film"]; g, yol = baglam(o, "A07c", "SEMA", "_RAPOR/SEMA_SOZLESME.json")
    h = oku(film, "HIKAYE.json")
    if not isinstance(h, dict): return yaz(o, g, yol, "SEMA", [m("hikaye_yok", "HATA")], [], kapsam="SOZLESME")
    planlar = _planlar(film); olc = []
    gr = {}
    for pl in planlar:
        sg = ((pl.get("zanaat") or {}).get("sahne_grubu") or pl.get("sahne") or "")
        gr.setdefault(re.sub(r"[a-z]$", "", sg), []).append(pl)
    hs = {s["id"]: s for s in sahne_listesi(h)}
    for sg in gr:
        if sg not in hs: olc.append(m("sahne_hikayede_yok", "HATA", birim=sg))
    rep = {r.get("id"): r for r in h.get("replikler") or [] if isinstance(r, dict)}
    for sid, s in hs.items():
        pls = gr.get(sid)
        if not pls: olc.append(m("sahne_plansiz", "HATA", birim=sid)); continue
        sure = sum(float((pl.get("_derlenir") or {}).get("sure_sn") or (pl.get("kullanim") or {}).get("sure")
                         or (pl.get("zanaat") or {}).get("klip_sn") or 0) for pl in pls)
        hd = s.get("hedef_sure_sn")
        if hd and abs(sure - hd) / hd > E("yonetmen_sahne_sure_sapma", 0.2):
            olc.append(m("sahne_sure_sapma", "BAYRAK", birim=sid, olcu=round(sure, 1), esik=hd))
        for f, kok in ((_durum_esit(s.get("giris_durumu"), (pls[0].get("zanaat") or {}).get("baslangic_durumu"), False), "giris"),
                       (_durum_esit(s.get("cikis_durumu"), (pls[-1].get("zanaat") or {}).get("bitis_durumu"), False), "cikis")):
            if f: olc.append(m(f"sahne_{kok}_durumu", "HATA", birim=sid, olcu=f[:5]))
        metin = {}
        for pl in pls:
            r = pl.get("replik") or {}
            if r.get("id"): metin.setdefault(r["id"], []).append(r.get("metin") or "")
        for rid, parcalar in metin.items():
            asil = (rep.get(rid) or {}).get("metin")
            if asil is None: olc.append(m("replik_hikayede_yok", "HATA", birim=sid, olcu=rid))
            elif " ".join(x.strip() for x in parcalar) != asil.strip(): olc.append(m("replik_birebir_degil", "HATA", birim=sid, olcu=rid))
        eb = " ".join(json.dumps((pl.get("zanaat") or {}).get("ekranda_bilgi"), ensure_ascii=False) for pl in pls)
        for x in h.get("anahtar_olgular") or []:
            if isinstance(x, dict) and x.get("kritik") and sid in (x.get("ekranda") or []) and x.get("id") not in eb:
                olc.append(m("kritik_olgu_planda_yok", "HATA", birim=sid, olcu=x.get("id")))
    if not olc: olc.append(m("sozlesme", "GEC"))
    return yaz(o, g, yol, "SEMA", olc, ["HIKAYE.json"], kapsam="SOZLESME")


def _hikaye_ya_da_senaryo(film):
    h = oku(film, "HIKAYE.json")
    return h if isinstance(h, dict) else son_senaryo(film)[2]


def vaat_denetim(o):
    film = o["film"]; g, yol = baglam(o, "A06", "SEMA", "_RAPOR/SEMA_VAAT_t{tur}.json")
    h = _hikaye_ya_da_senaryo(film)
    if not h: return yaz(o, g, yol, "SEMA", [m("hikaye_yok", "HATA")], [], kapsam="VAAT")
    zc = zaman_cizelgesi(h); sira = {s["id"]: i for i, s in enumerate(sahne_listesi(h))}
    olc = vaat_olcumleri(h, zc, sira, o.get("--baslik")) or [m("vaat", "GEC")]
    return yaz(o, g, yol, "SEMA", olc, ["HIKAYE.json"], kapsam="VAAT")


def seyirlik_denetim(o):
    film = o["film"]; g, yol = baglam(o, "A06", "Z2", "_RAPOR/Z2_HIKAYE.json")
    h = _hikaye_ya_da_senaryo(film)
    if not h: return yaz(o, g, yol, "Z2", [m("hikaye_yok", "HATA")], [], kapsam="HIKAYE")
    zc = zaman_cizelgesi(h); olc = []
    for p in h.get("partiler") or []:
        ps = parti_sahneleri(h, p.get("id"))
        sey = [s for s in ps if s.get("seyirlik") or s.get("vitrin")]
        if len(sey) < E("seyirlik_an_parti_min", 2): olc.append(m("seyirlik_an", "BAYRAK", birim=p.get("id"), olcu=len(sey)))
        if not [s for s in ps if s.get("kucuk_guzel")] and E("kucuk_guzel_sahne_parti_min", 1):
            olc.append(m("kucuk_guzel_sahne", "BAYRAK", birim=p.get("id")))
        sh = [x for x in h.get("short_adaylari") or [] if isinstance(x, dict) and set(x.get("sahneler") or []) & {s["id"] for s in ps}]
        if len(sh) < E("short_aday_parti_min", 1): olc.append(m("short_adayi", "BAYRAK", birim=p.get("id")))
    son = 0.0
    for s in sahne_listesi(h):
        if s.get("seyirlik") or s.get("vitrin"):
            if zc[s["id"]][0] - son > E("gosterisiz_aralik_max_sn", 360):
                olc.append(m("gosterisiz_aralik", "BAYRAK", birim=s["id"], olcu=round(zc[s["id"]][0] - son)))
            son = zc[s["id"]][0] + zc[s["id"]][1]
    if not olc: olc.append(m("seyirlik", "GEC"))
    return yaz(o, g, yol, "Z2", olc, ["HIKAYE.json"], kapsam="HIKAYE")


KOMUTLAR = {"konu-denetim": konu_denetim, "butce-bilgisi": butce_bilgisi, "brifing": brifing, "logline": logline,
            "oneri-denetim": oneri_denetim, "juri-paketi": juri_paketi, "juri-topla": juri_topla, "yapi-denetim": yapi_denetim,
            "oyuncu-paketi": oyuncu_paketi, "senaryo-denetim": senaryo_denetim, "seyirci-topla": seyirci_topla_k,
            "ilk2dk-topla": ilk2dk_topla_k, "devir": devir, "sahne-sozlesme": sahne_sozlesme, "vaat-denetim": vaat_denetim,
            "seyirlik-denetim": seyirlik_denetim}


def main(a):
    if not a or a[0] not in KOMUTLAR: print(__doc__); return HATA if a else BITTI
    o = {"komut": a[0]}
    for k in ("--film", "--tur", "--kip", "--baslik"):
        if k in a and a.index(k) + 1 < len(a): o[k] = a[a.index(k) + 1]
    if not o.get("--film"): print("!! --film gerekli"); return HATA
    try:
        f = o["--film"]
        o["film"] = os.path.abspath(f) if os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)
        r = KOMUTLAR[a[0]](o)
    except ortak.YolYok as e:
        print("!!", e); return ORTAM
    return r if isinstance(r, int) else BITTI


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
