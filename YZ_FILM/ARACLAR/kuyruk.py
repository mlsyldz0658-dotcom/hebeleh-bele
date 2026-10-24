"""KUYRUK — yeniden üretim (YENIDEN_URET) ve yeniden yazım (YENIDEN_YAZ) kuyrukları (TASARIM §5.7, D-31, §1.5, §6.1).

Kullanım:
  python kuyruk.py --film <film> --topla                     _RAPOR/ altındaki kapı raporlarının "kuyruk" önerilerini ekler
  python kuyruk.py --film <film> --ekle <maddeler.json> [--kaynak-kapi KI] [--kaynak-rapor _RAPOR/SEYIRCI_KARAR_T2_t1.json] [--kapi-tur 1]
  python kuyruk.py --film <film> --yaz-ekle <maddeler.json> --asama A07c      YENIDEN_YAZ (kâğıt) maddeleri
  python kuyruk.py --film <film> --listele                   açık maddeler öncelik sırasıyla
  python kuyruk.py --film <film> --durum <id> <durum> [--karar-veren <ad>] [--is-kimligi <k>]
  python kuyruk.py --film <film> --merdiven-md               KURGU/MERDIVEN.md (0 kredi merdiveni + maddeye özel basamaklar)
  <film>: film klasörünün yolu ya da yalnız adı (adı verilirse <veri>/FILMLER/<ad>, ortak.yollar()).
  --sahneler <SAHNELER.json>: zincir etkisi için (verilmezse <film>/SAHNELER.json varsa o okunur).
Kurallar:
  - Dosyalar <film>/KUYRUK/YENIDEN_URET.json ve YENIDEN_YAZ.json: {_surum, _uretim, maddeler, soylar, reddedilenler, toplanan}.
  - **0 kredi kuralı** (D-31): cozum ∈ {yeniden_cek, bitis_sabit, yeni_plan, yeni_sahne} olan madde sifir_kredi.denendi = true ve
    dolu sifir_kredi.gerekce olmadan REDDEDİLİR. cozum = kirp olan madde kuyruğa girmez (kusur kullanılan pencerenin dışında; kurgu kırpar).
  - **Soy sayacı** (§1.5, D-31): plan soyu başına toplam üretim denemesi ≤ 3 (ilk üretim + 2 yeniden çekim; bölmeden doğan planlar soyun
    sayacını taşır: madde "soy" alanı, yoksa plan). Sayaç görsel ve video için ayrıdır; ses yeniden çekimi Flow videosudur, video sayacına
    yazılır. Aynı soyun açık maddesi varsa yeni madde o çekime katılır, deneme harcamaz. Tavan dolunca madde reddedilir ve merdiven sürer:
    ilk kez → yonetmen·onarim (planı değiştirir), yine → durdu (kurgucu·sifir_kredi zorunlu çözüm; örtü, yer tutucu, kesme).
  - Öncelik: seviye_puanı × konum_agirligi × (1 + 0,5 × (seyirci_sayisi − 1)) × (dogrulanmis ? oncelik_dogrulanmis_carpan : 1);
    seviye_puanı KRITIK/HATA 3, ORTA/BAYRAK 2; KÜÇÜK kuyruğa girmez. Katsayılar esikler.py'den (oncelik_konum_agirligi,
    oncelik_dogrulanmis_carpan). Sıra: önce KRITIK/HATA, sonra ORTA/BAYRAK; her grupta oncelik / kredi_tahmini büyükten küçüğe.
  - Tekrar: aynı tur + plan + kok_neden'li açık madde birleşir (seviye, seyirci sayısı, ağırlık en yükseği; kaynaklar eklenir).
  - kok_neden veri/kok_neden.json'da olmalı (es_anlamlar çevrilir); kaynak_kapi veri/ADLAR.json kuyruk_kaynak_kapilari'nda.
  - Durum "gonderildi" olunca eski klip/görsel <film>/_ESKI/'ye taşınır (silinmez).
Çıkış kodları: 0 tamam · 1 program hatası ya da bozuk kuyruk dosyası · 2 girdi/film klasörü yok · 3 en az bir madde reddedildi · 4 kullanım.
"""
import os, sys, re, json, shutil, hashlib
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")   # StringIO stdout'ta yok
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi

SURUM = "kuyruk 1.0"
URET, YAZ = "YENIDEN_URET", "YENIDEN_YAZ"
KREDILI = ("yeniden_cek", "bitis_sabit", "yeni_plan", "yeni_sahne")      # D-31
COZUMLER = KREDILI + ("kirp",)
COZUM_ESDEGER = {"z2_bitis": "bitis_sabit"}                              # [KU2] §4.5.5 adı
TURLER = ("gorsel", "video", "ses", "kart")      # kart: karakter/mekân kartı düzeltmesi (A10d KART_DUZELTME); plan yerine kart_id
SEVIYE_PUANI = {"KRITIK": 3, "HATA": 3, "ORTA": 2, "BAYRAK": 2}
SEVIYE_ESDEGER = {"KRİTİK": "KRITIK", "H": "HATA", "B": "BAYRAK", "KÜÇÜK": "KUCUK", "KUCUK": "KUCUK"}
SOY_MAX = 3                     # §1.5 "Plan soyu başına üretim denemesi 3"; D-31 "toplam deneme ≤ 3" (eşik dosyasında anahtar yok)
DURUMLAR = ("bekliyor", "gonderildi", "tamam", "iptal")
ACIK = ("bekliyor",)
YAZ_DURUMLAR = ("bekliyor", "tamam", "iptal")
DILIM = {"G1": "goruntu", "G1Z": "goruntu", "V1": "goruntu", "V2": "goruntu", "V3": "goruntu", "K1": "goruntu", "KESIT": "goruntu", "KART": "goruntu",
         "S2": "ses", "S2m": "ses", "S3": "ses", "Z3": "kurgu", "AI": "kurgu", "KI": "kurgu", "NOT": "kurgu"}
DILIMLER = ("goruntu", "ses", "kurgu")
ILK_SN = 120                    # konum ağırlığı: ilk 120 sn ([KU2] §4.5.5)
MERDIVEN_ONARIM, MERDIVEN_DURDU = "yonetmen·onarim", "durdu"
YAZ_ID = re.compile(r"A[0-9]{2}[a-z]?")
SAHNE_ID = re.compile(r"S[0-9]{2,}")


class KuyrukHatasi(Exception):
    pass


# --- sözlükler ve eşikler ---------------------------------------------------------------------------------------
_KOK = None
def kok_sozluk():
    global _KOK
    if _KOK is None:
        _KOK = ortak.json_oku(os.path.join(HERE, "veri", "kok_neden.json"), {}) or {}
    return _KOK


def kok_neden_normal(k):
    """Kök neden kodunu sözlükteki adına çevirir (es_anlamlar); bilinmiyorsa None."""
    d = kok_sozluk(); kn = d.get("kok_nedenler") or {}
    if k in kn: return k
    k2 = (d.get("es_anlamlar") or {}).get(k)
    return k2 if k2 in kn else None


def kaynak_kapilari(): return set(kapi.adlar().get("kuyruk_kaynak_kapilari") or [])
def ajanlar(): return {k for k in (kapi.adlar().get("ajanlar") or {}) if not k.startswith("_")}


_E = None
def esik(E=None):
    """oncelik katsayıları ve soy tavanı. E verilirse o kullanılır (testler); yoksa esikler.yukle() bir kez."""
    global _E
    if E is None:
        if _E is None:
            import esikler; _E = esikler.yukle()
        E = _E
    return {"konum": float(E.get("oncelik_konum_agirligi", 1.5)), "dogrulanmis": float(E.get("oncelik_dogrulanmis_carpan", 1.25)),
            "soy_max": min(int(E.get("plan_soyu_deneme_max", SOY_MAX)), SOY_MAX)}   # tavan yalnız sıkılaşır


# --- yol ve dosya -------------------------------------------------------------------------------------------------
def film_klasoru(film):
    if os.path.isdir(film): return os.path.abspath(film)
    if os.sep in film or "/" in film: raise KuyrukHatasi(f"film klasörü yok: {film}")
    yol = os.path.join(ortak.yollar()["filmler"], film)
    if not os.path.isdir(yol): raise KuyrukHatasi(f"film klasörü yok: {yol}")
    return yol


def kuyruk_yolu(film_kok, ad=URET): return os.path.join(film_kok, "KUYRUK", ad + ".json")


def _bos(): return {"_surum": 1, "_uretim": {}, "maddeler": [], "soylar": {}, "reddedilenler": [], "toplanan": {}, "sayac": {}}


def oku(film_kok, ad=URET):
    """Kuyruk dosyası (yoksa boş). Zarfsız eski biçim (yalnız madde listesi) de okunur. Bozuksa KuyrukHatasi."""
    yol = kuyruk_yolu(film_kok, ad)
    if not os.path.exists(yol): return _bos()
    try:
        with open(yol, encoding="utf-8-sig") as f: v = json.load(f)
    except (OSError, ValueError) as e: raise KuyrukHatasi(f"kuyruk dosyası okunamadı: {yol} ({e})")
    q = _bos()
    if isinstance(v, list): q["maddeler"] = v
    elif isinstance(v, dict) and isinstance(v.get("maddeler", []), list): q.update(v)
    else: raise KuyrukHatasi(f"kuyruk dosyası biçimsiz: {yol}")
    for a, t in (("soylar", dict), ("reddedilenler", list), ("toplanan", dict), ("sayac", dict)):
        if not isinstance(q.get(a), t): q[a] = t()
    return q


def _yaz(film_kok, ad, q, asama=None):
    acik = [m for m in q["maddeler"] if m.get("durum") in ACIK]
    q["_surum"] = 1
    q["_uretim"] = {"asama": asama or (q.get("_uretim") or {}).get("asama"), "gorev": None, "girdi_imza": None, "arac_surum": SURUM,
                    "esik_surum": None, "sonuc": "BAYRAK" if acik else "GEC", "zaman": kapi.simdi(), "ortam": kapi.ortam()}
    ortak.atomik_yaz(kuyruk_yolu(film_kok, ad), q)


# --- öncelik, denetim -----------------------------------------------------------------------------------------
def seviye_normal(s):
    if not isinstance(s, str): return None
    k = s.strip().upper(); return SEVIYE_ESDEGER.get(k, SEVIYE_ESDEGER.get(s.strip(), k))


def konum_agirligi(m, E=None):
    """Madde verdiyse o; değilse konum_onemli (ilk 120 sn, parti sonu, doruk, vaat imgesi) ya da zaman_sn < 120 → eşik değeri; yoksa 1,0."""
    if isinstance(m.get("konum_agirligi"), (int, float)) and not isinstance(m.get("konum_agirligi"), bool):
        return float(m["konum_agirligi"])
    z = m.get("zaman_sn")
    if m.get("konum_onemli") or (isinstance(z, (int, float)) and 0 <= z < ILK_SN): return esik(E)["konum"]
    return 1.0


def oncelik_hesapla(m, E=None):
    """seviye_puanı × konum_agirligi × (1 + 0,5 × (seyirci_sayisi − 1)) × (dogrulanmis ? çarpan : 1); 4 haneye yuvarlanır."""
    k = esik(E)
    puan = SEVIYE_PUANI.get(seviye_normal(m.get("seviye")), 0)
    n = m.get("seyirci_sayisi") or 1
    n = max(1, int(n)) if isinstance(n, (int, float)) else 1
    o = puan * konum_agirligi(m, E) * (1 + 0.5 * (n - 1)) * (k["dogrulanmis"] if m.get("dogrulanmis") is True else 1.0)
    return round(o, 4)


def sifir_kredi_denetle(m):
    """0 kredi kuralı: kredili çözümde sifir_kredi.denendi true ve gerekce dolu olmalı. Red nedeni ya da None."""
    cz = COZUM_ESDEGER.get(m.get("cozum"), m.get("cozum"))
    if cz not in KREDILI: return None
    sk = m.get("sifir_kredi")
    if not isinstance(sk, dict) or sk.get("denendi") is not True:
        return f"0 kredi kuralı: cozum {cz} için sifir_kredi.denendi true değil (önce kurgucu·sifir_kredi)"
    if not (isinstance(sk.get("gerekce"), str) and sk["gerekce"].strip()):
        return f"0 kredi kuralı: cozum {cz} için sifir_kredi.gerekce boş"
    return None


def madde_denetle(m):
    """YENIDEN_URET maddesinin biçim hataları (liste). 0 kredi kuralı dahil."""
    if not isinstance(m, dict): return ["madde sözlük değil"]
    h = []
    p = m.get("plan")
    if m.get("tur") == "kart":
        if not (isinstance(m.get("kart_id"), str) and m["kart_id"].strip()): h.append(f"kart maddesinde kart_id gerekli: {m.get('kart_id')!r}")
        if p is not None and not (isinstance(p, int) and not isinstance(p, bool) and p > 0): h.append(f"plan pozitif tamsayı olmalı: {p!r}")
    elif not (isinstance(p, int) and not isinstance(p, bool) and p > 0): h.append(f"plan pozitif tamsayı olmalı: {p!r}")
    s = m.get("soy")
    if s is not None and not (isinstance(s, int) and not isinstance(s, bool) and s > 0): h.append(f"soy pozitif tamsayı olmalı: {s!r}")
    if m.get("tur") not in TURLER: h.append(f"tur geçersiz: {m.get('tur')!r} ({'|'.join(TURLER)})")
    if m.get("kaynak_kapi") not in kaynak_kapilari(): h.append(f"kaynak_kapi geçersiz: {m.get('kaynak_kapi')!r}")
    if kok_neden_normal(m.get("kok_neden")) is None: h.append(f"kok_neden veri/kok_neden.json'da yok: {m.get('kok_neden')!r}")
    sv = seviye_normal(m.get("seviye"))
    if sv == "KUCUK": h.append("KÜÇÜK seviye kuyruğa girmez")
    elif sv not in SEVIYE_PUANI: h.append(f"seviye geçersiz: {m.get('seviye')!r} (KRITIK|ORTA|HATA|BAYRAK)")
    cz = COZUM_ESDEGER.get(m.get("cozum"), m.get("cozum"))
    if cz not in COZUMLER: h.append(f"cozum geçersiz: {m.get('cozum')!r} ({'|'.join(COZUMLER)})")
    for a in ("seyirci_sayisi", "kredi_tahmini"):
        v = m.get(a)
        if v is not None and not (isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0): h.append(f"{a} negatif olmayan sayı olmalı")
    if "dogrulanmis" in m and not isinstance(m["dogrulanmis"], bool): h.append("dogrulanmis true/false olmalı")
    z = m.get("zincir_etkisi")
    if z is not None and not (isinstance(z, list) and all(isinstance(x, int) and not isinstance(x, bool) for x in z)):
        h.append("zincir_etkisi plan numarası listesi olmalı")
    if m.get("dilim") is not None and m["dilim"] not in DILIMLER: h.append(f"dilim geçersiz: {m['dilim']!r}")
    r = sifir_kredi_denetle(m)
    if r: h.append(r)
    return h


def sirala(maddeler):
    """Önce KRITIK/HATA, sonra ORTA/BAYRAK; grupta oncelik / kredi_tahmini büyükten küçüğe (kredi yoksa oncelik); eşitlikte id."""
    def anahtar(m):
        grup = 0 if SEVIYE_PUANI.get(seviye_normal(m.get("seviye")), 0) >= 3 else 1
        kr = m.get("kredi_tahmini")
        oran = (m.get("oncelik") or 0) / kr if isinstance(kr, (int, float)) and kr > 0 else (m.get("oncelik") or 0)
        return (grup, -oran, str(m.get("id")))
    return sorted(maddeler, key=anahtar)


def zincir_etkisi(plan_no, sahneler):
    """SAHNELER.json v2'de uretim.zincir.kaynak'ı (yontem bagimsiz değil; kare_zinciri.py yazar) bu plana bağlı sonraki planlar,
    geçişli (KR5 kilidi: kaynak yeniden çekilirse onlar da çekilir). sahneler: sözlük ya da yol."""
    if isinstance(sahneler, str): sahneler = ortak.json_oku(sahneler, {})
    planlar = (sahneler.get("sahneler") or []) if isinstance(sahneler, dict) else []
    ebeveyn = {}
    for p in planlar:
        if not isinstance(p, dict) or not isinstance(p.get("no"), int): continue
        uz = ((p.get("uretim") or {}).get("zincir") or {})
        if uz.get("kaynak") is not None and uz.get("yontem") not in (None, "bagimsiz"):
            ebeveyn[p["no"]] = uz["kaynak"]
    out, sinir = [], [plan_no]
    while sinir:
        cocuk = sorted(n for n, e in ebeveyn.items() if e in sinir and n not in out and n != plan_no)
        out += cocuk; sinir = cocuk
    return out


def _sayac_kovasi(tur): return tur if tur in ("gorsel", "kart") else "video"     # kart soyu ayrı sayılır


def _birim(m): return ("kart", m.get("kart_id")) if m.get("tur") == "kart" else ("plan", m.get("plan"))


def _yeni_id(q, kaynak_kapi, kapi_tur):
    kod = re.sub(r"[^A-Z0-9]", "", str(kaynak_kapi).upper()) or "X"
    anah = f"{kod}-{int(kapi_tur)}"
    n = int(q["sayac"].get(anah, 0)) + 1; q["sayac"][anah] = n
    return f"YU-{anah}-{n:03d}"


# --- ekleme ------------------------------------------------------------------------------------------------------
def _sonuc(): return {"eklenen": [], "birlesen": [], "kirp": [], "reddedilen": [], "merdiven": []}


def _ekle_bir(q, m, sonuc, kaynak_kapi, kaynak_rapor, kapi_tur, sahneler, E):
    m = dict(m)
    if kaynak_kapi and not m.get("kaynak_kapi"): m["kaynak_kapi"] = kaynak_kapi
    if kaynak_rapor and not m.get("kaynak_rapor"): m["kaynak_rapor"] = kaynak_rapor
    h = madde_denetle(m)
    if h:
        red = {"madde": m, "neden": h, "zaman": kapi.simdi()}
        q["reddedilenler"].append(red); sonuc["reddedilen"].append(red); return
    m["cozum"] = COZUM_ESDEGER.get(m["cozum"], m["cozum"])
    m["kok_neden"] = kok_neden_normal(m["kok_neden"]); m["seviye"] = seviye_normal(m["seviye"])
    if m["cozum"] == "kirp":                                    # kuyruğa girmez (D-31)
        sonuc["kirp"].append(m); return
    m.setdefault("soy", m["kart_id"] if m["tur"] == "kart" else m["plan"])
    m.setdefault("seyirci_sayisi", 1); m.setdefault("dogrulanmis", False)
    m["konum_agirligi"] = konum_agirligi(m, E)
    m["dilim"] = m.get("dilim") or DILIM.get(m["kaynak_kapi"], "kurgu")
    m.setdefault("plan_metni_sahibi", "yonetmen")
    zin = set(m.get("zincir_etkisi") or [])
    if sahneler and m["tur"] != "kart": zin |= set(zincir_etkisi(m["plan"], sahneler))
    m["zincir_etkisi"] = sorted(zin)
    k = esik(E)
    # tekrar: aynı tur + plan + kok_neden açık madde
    for e in q["maddeler"]:
        if e.get("durum") in ACIK and e.get("tur") == m["tur"] and _birim(e) == _birim(m) and e.get("kok_neden") == m["kok_neden"]:
            if SEVIYE_PUANI[m["seviye"]] > SEVIYE_PUANI.get(e.get("seviye"), 0): e["seviye"] = m["seviye"]
            e["seyirci_sayisi"] = max(e.get("seyirci_sayisi") or 1, m["seyirci_sayisi"])
            e["dogrulanmis"] = bool(e.get("dogrulanmis")) or m["dogrulanmis"]
            e["konum_agirligi"] = max(e.get("konum_agirligi") or 1.0, m["konum_agirligi"])
            e["zincir_etkisi"] = sorted(set(e.get("zincir_etkisi") or []) | zin)
            if isinstance(m.get("kredi_tahmini"), (int, float)):
                e["kredi_tahmini"] = max(e.get("kredi_tahmini") or 0, m["kredi_tahmini"])
            if not e.get("duzeltme") and m.get("duzeltme"): e["duzeltme"] = m["duzeltme"]
            e.setdefault("kaynaklar", [{"kaynak_kapi": e.get("kaynak_kapi"), "kaynak_rapor": e.get("kaynak_rapor")}])
            kay = {"kaynak_kapi": m.get("kaynak_kapi"), "kaynak_rapor": m.get("kaynak_rapor")}
            if kay not in e["kaynaklar"]: e["kaynaklar"].append(kay)
            e["oncelik"] = oncelik_hesapla(e, E)
            sonuc["birlesen"].append(e["id"]); return
    # soy sayacı
    kova = _sayac_kovasi(m["tur"]); sk = f"{kova}:{m['soy']}"
    rec = q["soylar"].setdefault(sk, {"deneme": 1, "merdiven": None, "maddeler": []})
    ortak_cekim = next((e for e in q["maddeler"] if e.get("durum") in ACIK and e.get("soy") == m["soy"]
                        and _sayac_kovasi(e.get("tur")) == kova), None)
    if ortak_cekim is not None:
        deneme = ortak_cekim.get("deneme") or rec["deneme"]; m["ayni_cekim"] = ortak_cekim["id"]
    else:
        verilen = m.get("deneme") if isinstance(m.get("deneme"), int) and not isinstance(m.get("deneme"), bool) else 0
        deneme = max(int(rec["deneme"]) + 1, verilen)
    if deneme > k["soy_max"]:
        basamak = MERDIVEN_ONARIM if rec.get("merdiven") is None else MERDIVEN_DURDU
        rec["merdiven"] = basamak
        is_ = {"soy": m["soy"], "tur": kova, "plan": m.get("plan"), "basamak": basamak, "deneme_yapilan": rec["deneme"],
               "gorev": "yonetmen·onarim" if basamak == MERDIVEN_ONARIM else "kurgucu·sifir_kredi", "kok_neden": m["kok_neden"]}
        red = {"madde": m, "neden": [f"soy tavanı: soy {m['soy']} ({kova}) {rec['deneme']}/{k['soy_max']} deneme kullandı"],
               "merdiven": basamak, "zaman": kapi.simdi()}
        q["reddedilenler"].append(red); sonuc["reddedilen"].append(red); sonuc["merdiven"].append(is_); return
    rec["deneme"] = max(int(rec["deneme"]), deneme)
    m["deneme"] = deneme; m["deneme_max"] = k["soy_max"]
    m.setdefault("is_kimligi", None); m["durum"] = "bekliyor"; m.setdefault("karar_veren", None)
    m["oncelik"] = oncelik_hesapla(m, E)
    m["id"] = _yeni_id(q, m["kaynak_kapi"], m.pop("kapi_tur", kapi_tur))
    rec["maddeler"].append(m["id"])
    q["maddeler"].append(m); sonuc["eklenen"].append(m["id"])


def ekle(film_kok, maddeler, kaynak_kapi=None, kaynak_rapor=None, kapi_tur=1, sahneler=None, E=None, asama=None):
    """YENIDEN_URET'e madde ekler (denetim, 0 kredi kuralı, tekrar, soy sayacı, öncelik). Dosyayı yazar.
    Dönüş: {eklenen: [id], birlesen: [id], kirp: [madde], reddedilen: [{madde, neden, merdiven?}], merdiven: [{soy, tur, plan, basamak, gorev}]}."""
    q = oku(film_kok, URET); s = _sonuc()
    if sahneler is None:
        p = os.path.join(film_kok, "SAHNELER.json")
        if os.path.exists(p): sahneler = ortak.json_oku(p, None)
    for m in maddeler: _ekle_bir(q, m, s, kaynak_kapi, kaynak_rapor, kapi_tur, sahneler, E)
    q["maddeler"] = sirala(q["maddeler"])
    _yaz(film_kok, URET, q, asama)
    return s


def _sha(yol):
    with open(yol, "rb") as f: return hashlib.sha1(f.read()).hexdigest()[:12]


def topla(film_kok, rapor_klasoru=None, sahneler=None, E=None, asama=None):
    """_RAPOR/ altındaki geçerli kapı raporlarının "kuyruk" listelerini ekler (kaynak_kapi = raporun kapısı, kaynak_rapor = yolu).
    Aynı içerikteki rapor ikinci kez toplanmaz (KUYRUK dosyasındaki "toplanan" kaydı). Dönüş ekle() ile aynı."""
    rk = rapor_klasoru or os.path.join(film_kok, "_RAPOR")
    q = oku(film_kok, URET); s = _sonuc(); kk = kaynak_kapilari()
    if sahneler is None:
        p = os.path.join(film_kok, "SAHNELER.json")
        if os.path.exists(p): sahneler = ortak.json_oku(p, None)
    for yol, r in kapi.raporlar(rk):
        if not r.get("kuyruk") or r["kapi"] not in kk: continue
        goreli = os.path.relpath(yol, film_kok).replace(os.sep, "/"); imza = _sha(yol)
        if q["toplanan"].get(goreli) == imza: continue
        for m in r["kuyruk"]: _ekle_bir(q, m, s, r["kapi"], goreli, r.get("tur", 1), sahneler, E)
        q["toplanan"][goreli] = imza
    q["maddeler"] = sirala(q["maddeler"])
    _yaz(film_kok, URET, q, asama)
    return s


# --- durum ve eski klip ------------------------------------------------------------------------------------------
def eski_klip_tasi(film_kok, madde):
    """Yeniden üretilecek planın eski çıktısını <film>/_ESKI/<klasör>/NNN_d<deneme-1>.<uzantı>'ya taşır (silmez). Yol ya da None."""
    if madde.get("tur") == "kart": return None              # kart sürümlerini kart_denetim/_KARTLAR tutar; taşınacak klip yok
    klasor, uzantilar = ("SIRALI_GORSEL", (".jpg", ".png", ".jpeg")) if madde.get("tur") == "gorsel" else ("SIRALI_VIDEO", (".mp4",))
    for uz in uzantilar:
        kaynak = os.path.join(film_kok, klasor, f"{int(madde['plan']):03d}{uz}")
        if not os.path.exists(kaynak): continue
        hedef_kl = os.path.join(film_kok, "_ESKI", klasor); os.makedirs(hedef_kl, exist_ok=True)
        temel = f"{int(madde['plan']):03d}_d{max(1, int(madde.get('deneme') or 2) - 1)}"
        hedef = os.path.join(hedef_kl, temel + uz); i = 2
        while os.path.exists(hedef): hedef = os.path.join(hedef_kl, f"{temel}_{i}{uz}"); i += 1
        shutil.move(kaynak, hedef)
        return hedef
    return None


def durum_degistir(film_kok, madde_id, durum, karar_veren=None, is_kimligi=None, ad=URET):
    """Madde durumunu değiştirir. YENIDEN_URET'te gonderildi → eski klip _ESKI/'ye; iptal (gönderilmeden) → soyun denemesi geri verilir
    (aynı denemeyi paylaşan başka açık madde yoksa). Değişen maddeyi döndürür."""
    izinli = DURUMLAR if ad == URET else YAZ_DURUMLAR
    if durum not in izinli: raise KuyrukHatasi(f"durum geçersiz: {durum!r} ({'|'.join(izinli)})")
    q = oku(film_kok, ad)
    m = next((x for x in q["maddeler"] if x.get("id") == madde_id), None)
    if m is None: raise KuyrukHatasi(f"madde yok: {madde_id}")
    eski = m.get("durum")
    if ad == URET and durum == "gonderildi" and eski == "bekliyor":
        t = eski_klip_tasi(film_kok, m)
        if t: m["eski_cikti"] = os.path.relpath(t, film_kok).replace(os.sep, "/")
    if ad == URET and durum == "iptal" and eski == "bekliyor":
        kova = _sayac_kovasi(m.get("tur")); rec = q["soylar"].get(f"{kova}:{m.get('soy')}")
        paylasan = [x for x in q["maddeler"] if x is not m and x.get("soy") == m.get("soy") and _sayac_kovasi(x.get("tur")) == kova
                    and x.get("deneme") == m.get("deneme") and x.get("durum") in ("bekliyor", "gonderildi", "tamam")]
        if rec and not paylasan and rec.get("deneme") == m.get("deneme"): rec["deneme"] = max(1, int(rec["deneme"]) - 1)
    m["durum"] = durum
    if karar_veren is not None: m["karar_veren"] = karar_veren
    if is_kimligi is not None: m["is_kimligi"] = is_kimligi
    _yaz(film_kok, ad, q)
    return m


def acik_maddeler(film_kok, ad=URET):
    q = oku(film_kok, ad)
    acik = [m for m in q["maddeler"] if m.get("durum") in ACIK]
    return sirala(acik) if ad == URET else acik


# --- YENIDEN_YAZ -------------------------------------------------------------------------------------------------
def yaz_madde_denetle(m):
    """YENIDEN_YAZ maddesi {konum, kapi, madde, kok_neden, yazar, oneri, tur} biçim hataları."""
    if not isinstance(m, dict): return ["madde sözlük değil"]
    h = []; k = m.get("konum")
    if not isinstance(k, dict) or not (k.get("sahne") or k.get("plan")): h.append("konum {sahne?, plan?} olmalı (en az biri)")
    else:
        if k.get("sahne") is not None and not (isinstance(k["sahne"], str) and SAHNE_ID.fullmatch(k["sahne"])): h.append(f"konum.sahne geçersiz: {k['sahne']!r}")
        if k.get("plan") is not None and not (isinstance(k["plan"], int) and not isinstance(k["plan"], bool) and k["plan"] > 0):
            h.append(f"konum.plan geçersiz: {k['plan']!r}")
    if m.get("kapi") not in kapi.kapi_kodlari(): h.append(f"kapi bilinmiyor: {m.get('kapi')!r}")
    if not (isinstance(m.get("madde"), str) and m["madde"].strip()): h.append("madde boş")
    kn = kok_neden_normal(m.get("kok_neden"))
    if kn is None: h.append(f"kok_neden veri/kok_neden.json'da yok: {m.get('kok_neden')!r}")
    yazar = m.get("yazar") or (kok_sozluk()["kok_nedenler"][kn].get("sahip") if kn else None)
    if yazar not in ajanlar(): h.append(f"yazar bir ajan olmalı: {yazar!r}")
    if not (isinstance(m.get("oneri"), str) and m["oneri"].strip()): h.append("oneri boş")
    t = m.get("tur", 1)
    if not (isinstance(t, int) and not isinstance(t, bool) and t >= 1): h.append(f"tur ≥ 1 olmalı: {t!r}")
    return h


def yaz_ekle(film_kok, maddeler, asama):
    """YENIDEN_YAZ'a kâğıt maddeleri ekler (id YY-<asama>-NNN). yazar verilmezse kök nedenin sahibi. Dönüş ekle() biçiminde."""
    if not (isinstance(asama, str) and YAZ_ID.fullmatch(asama)): raise KuyrukHatasi(f"aşama geçersiz: {asama!r}")
    q = oku(film_kok, YAZ); s = _sonuc()
    for m in maddeler:
        h = yaz_madde_denetle(m)
        if h:
            red = {"madde": m, "neden": h, "zaman": kapi.simdi()}; q["reddedilenler"].append(red); s["reddedilen"].append(red); continue
        kn = kok_neden_normal(m["kok_neden"])
        yeni = {"id": None, "konum": dict(m["konum"]), "kapi": m["kapi"], "madde": m["madde"], "kok_neden": kn,
                "yazar": m.get("yazar") or kok_sozluk()["kok_nedenler"][kn]["sahip"], "oneri": m["oneri"],
                "tur": m.get("tur", 1), "durum": "bekliyor"}
        es = next((e for e in q["maddeler"] if e.get("durum") in ACIK and e.get("konum") == yeni["konum"] and e.get("kapi") == yeni["kapi"]
                   and e.get("madde") == yeni["madde"] and e.get("kok_neden") == kn), None)
        if es is not None: s["birlesen"].append(es["id"]); continue
        n = int(q["sayac"].get(asama, 0)) + 1; q["sayac"][asama] = n
        yeni["id"] = f"YY-{asama}-{n:03d}"
        q["maddeler"].append(yeni); s["eklenen"].append(yeni["id"])
    _yaz(film_kok, YAZ, q, asama)
    return s


# --- MERDIVEN.md --------------------------------------------------------------------------------------------------
MERDIVEN = [  # [KU2] §4.5.5 0 kredi merdiveni (kurgucu yukarıdan aşağı dener)
    (1, "Kırp / uzat", "ölü süre, geç giriş, uzun plan, eylem görünmedi, kusur pencere dışında", "güvenli pencere [0,5 ; klip_sn − 0,5]; zincir kilidi yoksa"),
    (2, "Sahne içi sıra", "konum planı geç, bakış → ekleme sırası", "yalnız etki'siz planlar (tepki, ekleme); Y58 temiz; 180° ve kurulum yeniden denetlenir"),
    (3, "J/L, ekran dışına taşıma (mevcut replik)", "kim konuşuyor, konuşma kopuk", "üzerine binilen planda ağız kapalı (B9); ses tanıtım kuralı (S0.3)"),
    (4, "Ekran dışı köprü replik", "bilgi ekrana çıkmamış, görüntü var", "yazar yazar (dar değişiklik), TTS (Flow kredisi 0); konuşan önce ekranda konuşmuş; sahne başına ≤ 1"),
    (5, "Alternatif çekim", "çekimde kusur var", "ALTERNATIFLER/ içinde V1/V2/V3'ten geçen başka sonuç"),
    (6, "Mevcut klipten bölme ya da örtü planı", "tepki/ekleme eksik; çıplak devam dikişi", "aynı sahnenin kullanılmayan klip penceresi"),
    (7, "Ayna", "180° ya da bakış ters", "_derlenir.ayna_yasak = false"),
    (8, "Yeniden kadraj", "ölçek sıçraması", "dijital yakınlaştırma ≤ %10"),
    (9, "Hız", "eylem uzun", "0,90–1,15×; yalnız diyalogsuz plan"),
    (10, "Kart / efekt ipucu", "nerede, nereden geldi", "yer kartı; efekt isteği ses tasarımcısına"),
    (11, "Planı kes", "bilgi taşımayan plan", "--kesme-simule yeni HATA göstermiyor"),
    (12, "Yer tutucu (görsel + yavaş zoom)", "filtre reddi", "ilk 120 sn, parti sonu ve dorukta kullanılmaz"),
]
KREDILI_BASAMAK = [
    ("KK1", "Yeniden çekim (aynı plan; CORRECTION ya da bitiş sabitleme)", "kusur görüntünün içinde", "kurgu dilimi + soy toplamı ≤ 3"),
    ("KK2", "Bağlayıcı yeni plan", "hikâye adımı ekranda yok, hikâyede var", "yönetmen yazar; G1"),
    ("KK3", "Yeni sahne", "bilgi hikâyede yok", "yalnız KRİTİK; yazar + yönetmen"),
]
BASAMAK = {  # kök neden → önce denenecek basamaklar ("Ne zaman" sütunundan)
    "olu_sure": [1], "gec_giris": [1], "uzun_plan": [1, 9], "bilgisiz_uzun": [11, 9, 1], "ritim_tekduze": [1, 2],
    "diyalog_kopuk": [3], "konusan_belirsiz": [3, 2], "senkron_kaydi": [1, 3], "dudak_ustune_replik": [3],
    "konum_plani_gec": [2], "mekan_belirsiz": [10, 2], "olcek_sicramasi": [8, 2], "eksen_180": [7, 2], "bakis": [7, 2],
    "ekran_yonu": [7], "hikaye_adimi_ekranda_yok": [4, 10], "bilgi_ekranda_yok": [4, 10], "bilgi_eksik": [4, 10],
    "devam_dikisi": [6, 1], "filtre_kelimesi": [12], "kurulum_yok": [4, 10],
}
ALAN_BASAMAK = {"sureklilik": [1, 5, 6], "ses": [3, 5], "kurgu": [1, 2, 3], "yonetmen": [2, 7, 8], "hikaye": [4, 10, 11], "hat": [5, 12]}


def basamaklar(kok_neden):
    kn = kok_neden_normal(kok_neden)
    if kn in BASAMAK: return BASAMAK[kn]
    alan = ((kok_sozluk().get("kok_nedenler") or {}).get(kn) or {}).get("alan")
    return ALAN_BASAMAK.get(alan, [1, 5, 6])


def merdiven_md(film_kok, cikti=None):
    """KURGU/MERDIVEN.md'yi yazar: 0 kredi merdiveni, kredili basamaklar, açık maddeye özel basamaklar, durdu soylar. Yolu döndürür."""
    q = oku(film_kok, URET)
    s = ["# MERDİVEN — 0 kredi çözümleri (kuyruk.py --merdiven-md)", "",
         "Kural: önce 0 kredi merdiveni, yukarıdan aşağı. Kredili çözüm (KK) ancak merdiven tükenince ve `sifir_kredi.gerekce` ile "
         "(D-31: gerekçesiz kredili madde kuyruğa girmez).", "", "## 0 kredi merdiveni", "",
         "| # | Çözüm | Ne zaman | Koşul |", "|---|---|---|---|"]
    s += [f"| {n} | {c} | {z} | {k} |" for n, c, z, k in MERDIVEN]
    s += ["", "## Kredili basamaklar", "", "| # | Çözüm | Ne zaman | Koşul |", "|---|---|---|---|"]
    s += [f"| {n} | {c} | {z} | {k} |" for n, c, z, k in KREDILI_BASAMAK]
    acik = sirala([m for m in q["maddeler"] if m.get("durum") in ACIK])
    s += ["", "## Açık maddeler ve önce denenecek basamaklar", ""]
    if not acik: s.append("Açık madde yok.")
    for m in acik:
        denenen = (m.get("sifir_kredi") or {}).get("basamaklar") or []
        kalan = [b for b in basamaklar(m.get("kok_neden")) if b not in denenen]
        s.append(f"- **{m['id']}** · {' '.join(map(str, _birim(m)))} · {m.get('tur')} · {m.get('seviye')} · `{m.get('kok_neden')}` · öncelik {m.get('oncelik')} · "
                 f"deneme {m.get('deneme')}/{m.get('deneme_max')} · çözüm {m.get('cozum')}")
        s.append(f"  - önerilen basamaklar: {', '.join(map(str, basamaklar(m.get('kok_neden'))))}; denenen: "
                 f"{', '.join(map(str, denenen)) or '—'}; denenmemiş: {', '.join(map(str, kalan)) or '—'}")
        if m.get("zincir_etkisi"): s.append(f"  - zincir etkisi (yeniden çekilirse): {', '.join(map(str, m['zincir_etkisi']))}")
    durdu = [(k, v) for k, v in sorted(q["soylar"].items()) if v.get("merdiven")]
    s += ["", "## Tavanı dolan soylar", ""]
    if not durdu: s.append("Yok.")
    for k, v in durdu:
        ne = ("yonetmen·onarim planı değiştirir" if v["merdiven"] == MERDIVEN_ONARIM
              else "plan durdu → kurgucu·sifir_kredi zorunlu çözüm (örtü, yer tutucu, kesme)")
        s.append(f"- soy `{k}` · {v['deneme']} deneme · {ne}")
    yol = cikti or os.path.join(film_kok, "KURGU", "MERDIVEN.md")
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: f.write("\n".join(s) + "\n")
    os.replace(tmp, yol)
    return yol


def ozet_md(film_kok):
    """URETIM_ONIZLEME.md'ye eklenecek kısa kuyruk özeti (metin; dosyayı kredi.py/olcek.py yazar)."""
    acik = acik_maddeler(film_kok)
    kr = sum(m.get("kredi_tahmini") or 0 for m in acik)
    dil = {}
    for m in acik: dil[m.get("dilim")] = dil.get(m.get("dilim"), 0) + (m.get("kredi_tahmini") or 0)
    krit = sum(1 for m in acik if SEVIYE_PUANI.get(m.get("seviye"), 0) >= 3)
    return (f"Kuyruk: {len(acik)} açık madde (KRİTİK/HATA {krit}) · kredi tahmini {kr:g} · "
            + " · ".join(f"{d} {v:g}" for d, v in sorted(dil.items(), key=lambda x: str(x[0]))))


# --- komut satırı ----------------------------------------------------------------------------------------------------
def _yazdir(s):
    for i in s["eklenen"]: print(f"EKLENDİ {i}")
    for i in s["birlesen"]: print(f"BİRLEŞTİ {i}")
    for m in s["kirp"]: print(f"KIRP plan {m.get('plan')} ({m.get('kok_neden')}): kuyruğa girmedi, kurgu kırpar")
    for r in s["reddedilen"]:
        m = r["madde"] if isinstance(r["madde"], dict) else {}
        print(f"REDDEDİLDİ plan {m.get('plan')} ({m.get('kok_neden')}): " + "; ".join(r["neden"]))
    for g in s["merdiven"]: print(f"MERDİVEN soy {g['soy']} ({g['tur']}): {g['basamak']} → görev {g['gorev']}")
    print(f"Toplam: eklenen {len(s['eklenen'])} · birleşen {len(s['birlesen'])} · kırp {len(s['kirp'])} · reddedilen {len(s['reddedilen'])}")
    return 3 if s["reddedilen"] else 0


def _maddeler_oku(yol):
    v = ortak.json_oku(yol)
    if isinstance(v, dict): v = v.get("maddeler", v.get("kuyruk"))
    if not isinstance(v, list): raise KuyrukHatasi(f"madde listesi okunamadı: {yol}")
    return v


def main(argv):
    a = {"--film": None, "--ekle": None, "--yaz-ekle": None, "--asama": None, "--kaynak-kapi": None, "--kaynak-rapor": None,
         "--kapi-tur": "1", "--sahneler": None, "--karar-veren": None, "--is-kimligi": None}
    bayrak = {"--topla": False, "--listele": False, "--merdiven-md": False}
    durum = None; i = 0
    while i < len(argv):
        x = argv[i]
        if x in bayrak: bayrak[x] = True; i += 1
        elif x == "--durum" and i + 2 < len(argv): durum = (argv[i + 1], argv[i + 2]); i += 3
        elif x in a and i + 1 < len(argv): a[x] = argv[i + 1]; i += 2
        else: print(__doc__); return 4
    islem = [k for k, v in bayrak.items() if v] + [k for k in ("--ekle", "--yaz-ekle") if a[k]] + (["--durum"] if durum else [])
    if not a["--film"] or len(islem) != 1: print(__doc__); return 4
    try:
        film = film_klasoru(a["--film"])
    except (KuyrukHatasi, ortak.YolYok) as e: print("!!", e); return 2
    sah = a["--sahneler"]
    if sah and not os.path.exists(sah): print(f"!! SAHNELER yok: {sah}"); return 2
    sah = ortak.json_oku(sah) if sah else None
    try:
        if bayrak["--topla"]: return _yazdir(topla(film, sahneler=sah))
        if a["--ekle"]:
            if not os.path.exists(a["--ekle"]): print(f"!! dosya yok: {a['--ekle']}"); return 2
            return _yazdir(ekle(film, _maddeler_oku(a["--ekle"]), a["--kaynak-kapi"], a["--kaynak-rapor"], int(a["--kapi-tur"]), sah))
        if a["--yaz-ekle"]:
            if not os.path.exists(a["--yaz-ekle"]): print(f"!! dosya yok: {a['--yaz-ekle']}"); return 2
            if not a["--asama"]: print("!! --asama gerekli (ör. A07c)"); return 4
            return _yazdir(yaz_ekle(film, _maddeler_oku(a["--yaz-ekle"]), a["--asama"]))
        if bayrak["--listele"]:
            for m in acik_maddeler(film):
                print(f"{m['id']} · {' '.join(map(str, _birim(m)))} · {m['tur']} · {m['seviye']} · {m['kok_neden']} · öncelik {m['oncelik']} · "
                      f"kredi {m.get('kredi_tahmini')} · deneme {m['deneme']}/{m['deneme_max']}")
            for m in acik_maddeler(film, YAZ): print(f"{m['id']} · {m['konum']} · {m['kapi']}:{m['madde']} → {m['yazar']}")
            print(ozet_md(film)); return 0
        if durum:
            ad = YAZ if durum[0].startswith("YY-") else URET
            m = durum_degistir(film, durum[0], durum[1], a["--karar-veren"], a["--is-kimligi"], ad)
            print(f"{m['id']} → {m['durum']}" + (f" (eski çıktı: {m['eski_cikti']})" if m.get("eski_cikti") else "")); return 0
        if bayrak["--merdiven-md"]: print(merdiven_md(film)); return 0
    except KuyrukHatasi as e: print("!!", e); return 1
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
