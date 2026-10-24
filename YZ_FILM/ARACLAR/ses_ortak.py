"""SES ORTAK — yerel ses hazırlığı araçlarının (ses_sec, ses_kiyas, seslendir, muzik_uret, ses_katmani, son_miks) paylaştığı küçük işler
(TASARIM §6.6, §5.6, §7.2 S1–S7; [SM2] §4.6).

Kodda:
  import ses_ortak as so
  so.esik("s1_wer_max") → değer (eşik dosyalarında varsa o; yoksa aşağıdaki kaynaklı varsayılan; ses_esikleri.json'a taşınacak)
  so.film_coz(ad_ya_da_yol) · so.sahte_mi(film, saglayici=None) · so.gorev(asama=None) → {id, tur_no, asama, rapor}
  so.rapor(film, "S1", "FILM", olcumler, asama="A10c", birimler=[...], ek={...}) → (yol, rapor)   (kapi.py zarfı; görev raporu yolu)
  so.zincir("tts"|"asr"|"muzik"|"ses_donustur"|"dinleyici", film, kip=None, saglayici=None) → [sağlayıcı nesnesi]
  so.saglayici("ai84") · so.sahneler(film) · so.replikler(film) → [{id, plan, karakter, metin, teslim, cumleler, pencere_sn, ...}]
  so.karakter_sesi(film, kar) → {"voice_id", "kaynak"} · so.kredi_onay(film, madde, kredi, dilim) → 0|5 · so.gonderim(...)
  so.yaz_ekle(film, maddeler, asama) (kuyruk.py YENIDEN_YAZ; reddedilen madde rapora not düşer)
Sağlayıcı adları: FILM_AYAR.json → saglayicilar.<tür> (liste ya da {kip: liste}); test kipinde (--saglayici sahte ya da HAZIRLIK.json
  saglayici: sahte) zincir yalnız `sahte`tır (D-41). Ses türlerinde `sahte` = saglayicilar/ses_sahte.py (48 kHz, hata enjeksiyonlu).
"""
import os, sys, json, hashlib, importlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi

SR = 48000
BITTI, HATA, KULLANICI, ORTAM, BUTCE, KISIT, BEKLE = 0, 1, 2, 4, 5, 7, 8
KISIT_KOD = {"olagandisi": KISIT, "dogrulama": KISIT, "giris": KISIT, "kilitli": KISIT}

# Eşik dosyalarında henüz olmayan ses hazırlığı eşikleri ([SM2] §4.7.2–4.7.8). Değerler ve kaynakları buradadır; veri/ses_esikleri.json'a
# aynı adla taşınınca dosyadaki değer kullanılır (paylaşılan istek). Hepsi "tahmin" etiketlidir (kalibrasyon §4.7.9).
ESIK = {
    "s1_notice_min_gun": (30, "tahmin", "[SM2] S1.1; [D-EL] min_notice_period_days"),
    "s1_wer_max": (0.05, "tahmin", "[SM2] S1.3"),
    "s1_kararlilik_min": (0.80, "tahmin", "[SM2] S1.4"),
    "s1_kadro_benzerlik_max": (0.60, "tahmin", "[SM2] S1.5"),
    "s1_kadro_f0_fark_min_yt": (2.0, "tahmin", "[SM2] S1.5"),
    "s1_perde_bant_hz": ({"erkek": [100, 140], "kadin": [165, 225]}, "tahmin", "[SM2] S1.6; genel fonetik (bellekten)"),
    "s1_secim_fark_min": (0.03, "tahmin", "[SM2] S1.8; TASARIM A10c"),
    "s1_agirliklar": ({"profil": 0.25, "ayirt": 0.20, "kalite": 0.20, "kararlilik": 0.15, "duygu": 0.10, "bildirim": 0.10},
                      "tahmin", "[SM2] S1.8"),
    "s1_aday_oku_max": (4, "tahmin", "[SM2] SB2 adım 3"),
    "s1_etiket_ortak_benzerlik": (0.60, "tahmin", "[SM2] SB2 adım 6; İ-9"),
    "s1_veo_ham_benzerlik_max": (0.60, "tahmin", "[SM2] S1.10"),
    "telaffuz_replik_sayisi": (3, "belge", "[SM2] SB1"),
    "motor_kiyas_ozel_min": (4, "tahmin", "TASARIM Ö0-c (fısıltı ve bağırma her biri ≥ 4)"),
    "ses_dogallik_mos_min": (3.5, "tahmin", "TASARIM §7.2 S (ses_dogallik_mos_min B; değer tahmin)"),
    "tts_esneme_max": (0.08, "tahmin", "[SM2] S2.12"),
    "ornek_tepe_max_dbfs": (-0.1, "tahmin", "[SM2] S2.14"),
    "ambiyans_bosluk_dbfs": (-60.0, "tahmin", "[SM2] S5.2"),
    "yumusatma_ms": ([10, 20], "tahmin", "[SM2] S5.10"),
    "efekt_varsayilan_db": (-6.0, "tahmin", "[SM2] S5.6 bandının ortası"),
    "muzik_aday_sayisi": (3, "belge", "[SM2] SB5; TASARIM §4.8.4"),
    "muzik_kroma_min": (0.6, "tahmin", "[SM2] S6.7"),
    "muzik_bpm_tolerans": (0.03, "tahmin", "[SM2] S6.10"),
    "muzik_kelime_guven_min": (0.5, "tahmin", "[SM2] S6.1/S5.9"),
    "miks_sessizlik_sn": (0.3, "tahmin", "[SM2] S7.4 d=0,3"),
    "miks_tepe_hedef_dbtp": (-1.5, "tahmin", "[SM2] S7.2 kodlama öncesi pay"),
    "miks_lra_max": (14.0, "tahmin", "[SM2] S7.3"),
    "miks_mono_fark_max_lu": (3.0, "tahmin", "[SM2] S7.5"),
    "miks_wer_bant": ([0.15, 0.30], "tahmin", "[SM2] S7.6"),
    "miks_ayni_stem_lufs_fark_max": (0.1, "tahmin", "[SM2] B15 (tek miks kodu)"),
}
_E = None


def esikler_():
    global _E
    if _E is None:
        try:
            import esikler; _E = esikler.yukle()
        except Exception: _E = {}
    return _E


def esik(ad):
    v = esikler_().get(ad) if hasattr(esikler_(), "get") else None
    if v is not None: return v
    if ad in ESIK: return ESIK[ad][0]
    raise KeyError(f"eşik yok: {ad}")


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")
def sha1(yol, n=12):
    h = hashlib.sha1()
    with open(yol, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()[:n]
def ozet(*parca, n=12): return hashlib.sha1("|".join(str(p) for p in parca).encode("utf-8")).hexdigest()[:n]


# --- film ve görev ---------------------------------------------------------------------------------------------------
def film_coz(f):
    if not f: raise ValueError("--film gerekli")
    if os.path.isdir(f): return os.path.abspath(f)
    p = os.path.join(ortak.yollar()["filmler"], f)
    if os.path.isdir(p): return p
    raise ValueError(f"film klasörü yok: {f}")


def meta(film): return ortak.json_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}


def sahte_mi(film, saglayici=None):
    return saglayici in ("sahte", "kaset") or meta(film).get("saglayici") == "sahte"


def gorev(asama=None, tur=None):
    g = ortak.json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV") or "", "GOREV.json"), {}) or {}
    return {"id": g.get("id"), "tur_no": int(tur or g.get("tur_no") or 1), "asama": g.get("asama") or asama, "rapor": g.get("rapor")}


def rapor(film, kapi_kodu, kapsam, olcumler, asama=None, birimler=None, ek=None, arac=None, tur=None, girdi_imza=None,
          kuyruk=None, gorev_raporu=True):
    """Kapı raporunu kurar ve yazar. Görevin kendi rapor yolu (GOREV.json) bu kapınınsa oraya; yoksa _RAPOR/<KAPI>_<kapsam>.json."""
    g = gorev(asama, tur)
    r = kapi.rapor_kur(kapi_kodu, kapsam, olcumler, tur=g["tur_no"], asama=g["asama"] or asama, gorev=g["id"], arac_surum=arac,
                       birimler=list(birimler or []), ek=ek, girdi_imza=girdi_imza, kuyruk=kuyruk)
    h = kapi.dogrula(r)
    if h: raise kapi.RaporHatasi(h)
    if gorev_raporu and g.get("rapor") and os.path.basename(g["rapor"]).startswith(kapi_kodu + "_"):
        yol = os.path.join(film, g["rapor"])
    else:
        yol = kapi.rapor_yolu(os.path.join(film, "_RAPOR"), kapi_kodu, kapsam)
    ortak.atomik_yaz(yol, r)
    return yol, r


def m(madde, seviye, plan=None, birim=None, **k):
    o = {"madde": madde, "seviye": seviye}
    if plan is not None: o["plan"] = plan
    if birim is not None: o["birim"] = birim
    o.update({a: v for a, v in k.items() if v is not None})
    return o


def yaz_ekle(film, maddeler, asama):
    if not maddeler: return {"eklenen": [], "reddedilen": []}
    try:
        import kuyruk
        return kuyruk.yaz_ekle(film, maddeler, asama)
    except Exception as e:
        return {"eklenen": [], "reddedilen": [{"madde": x, "neden": [str(e)[:120]]} for x in maddeler]}


# --- sağlayıcılar ----------------------------------------------------------------------------------------------------
YEREL_KAYIT = {
    "sahte": "saglayicilar.ses_sahte.SesSahte",
    "ai84": "saglayicilar.ai84_tts.AI84Tts",
    "faster_whisper": "saglayicilar.asr_whisper.FasterWhisper",
    "midi_ornek": "saglayicilar.midi_ornek.MidiOrnek",
    "acestep": "saglayicilar.acestep.AceStep",
    "kutuphane": "saglayicilar.kutuphane.Kutuphane",
    "gemini_muzik_paketi": "saglayicilar.gemini_muzik_paketi.GeminiMuzikPaketi",
}
VARSAYILAN_ZINCIR = {"tts": ["ai84"], "asr": ["faster_whisper"], "ses_donustur": ["openvoice", "chatterbox"], "dinleyici": ["gemini_api"],
                     "muzik": {"animatik": ["acestep", "midi_ornek"], "yayin": ["acestep", "kutuphane"]}}


def saglayici(ad):
    """Ses türlerinde bu dilimin sınıfları önce; yoksa saglayicilar.KAYIT. Bulunamazsa None (kurulu değil)."""
    yol = YEREL_KAYIT.get(ad)
    try:
        if yol is None:
            import saglayicilar as sg
            yol = sg.KAYIT.get(ad)
            if yol is None:
                try: importlib.import_module(f"saglayicilar.{ad}")
                except ImportError: return None
                mod = importlib.import_module(f"saglayicilar.{ad}")
                sinif = next((v for k, v in vars(mod).items() if isinstance(v, type) and getattr(v, "ad", None) == ad), None)
                return sinif() if sinif else None
        mod, sinif = yol.rsplit(".", 1)
        return getattr(importlib.import_module(mod), sinif)()
    except ImportError: return None


def ayar(film=None):
    try: p = os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json")
    except ortak.YolYok: return {}
    return ortak.json_oku(p, {}) or {}


def zincir_adlari(tur, film=None, kip=None, saglayici_=None):
    if film is not None and sahte_mi(film, saglayici_): return ["sahte"]
    if saglayici_: return [saglayici_]
    z = (ayar(film).get("saglayicilar") or {}).get(tur, VARSAYILAN_ZINCIR.get(tur, []))
    if tur == "tts" and not z: z = (ayar(film).get("saglayicilar") or {}).get("ses", ["ai84"])
    if isinstance(z, dict): z = z.get(kip or "yayin") or VARSAYILAN_ZINCIR.get(tur, {}).get(kip or "yayin", [])
    return list(z)


def zincir(tur, film=None, kip=None, saglayici_=None, log=None, hazir_olmayan=None):
    """Hazır sağlayıcılar (sırayla). Hazır olmayanların nedeni hazir_olmayan listesine eklenir (raporda açıkça yazılır)."""
    out = []
    for ad in zincir_adlari(tur, film, kip, saglayici_):
        s = saglayici(ad)
        if s is None or tur not in getattr(s, "turler", ()):
            if hazir_olmayan is not None: hazir_olmayan.append({"saglayici": ad, "neden": "kurulu değil ya da bu türü yapmıyor"})
            continue
        try: ok, neden = s.hazir()
        except Exception as e: ok, neden = False, str(e)[:120]
        if ok: out.append(s)
        else:
            if hazir_olmayan is not None: hazir_olmayan.append({"saglayici": ad, "neden": neden})
            if log: log(f"   [{ad}] {tur} için hazır değil: {neden}")
    return out


def kisit_kodu(e):
    """Kisitlandi → çıkış kodu: olağan dışı/doğrulama 7 (hat durur, geçiş yok); geçilebilir kodlar None (sıradakine geç)."""
    if getattr(e, "gecilebilir", False): return None
    return KISIT_KOD.get(getattr(e, "kod", ""), KISIT)


# --- SAHNELER / HIKAYE -----------------------------------------------------------------------------------------------
def sahneler(film):
    return ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}


def hikaye(film):
    return ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}


def _cumleler(metin):
    import re
    return [p.strip() for p in re.split(r"(?<=[.!?…])\s+", metin or "") if p.strip()]


def teslim_sinifi(teslim):
    """Replik teslimi → seviye sınıfı (fisilti|yumusak|normal|bagirma). veri/plan_sozlukleri.json → teslim sözlüğü varsa oradan."""
    sz = (ortak.json_oku(os.path.join(HERE, "veri", "plan_sozlukleri.json"), {}) or {}).get("teslim") or {}
    t = sz.get(teslim) if isinstance(sz, dict) else None
    if isinstance(t, dict) and t.get("seviye") in ("fisilti", "yumusak", "normal", "bagirma"): return t["seviye"]
    s = (teslim or "normal").lower()
    if any(k in s for k in ("fisil", "whisper")): return "fisilti"
    if any(k in s for k in ("bagir", "hayki", "shout", "cigl")): return "bagirma"
    if any(k in s for k in ("yumusak", "sefkat", "soft", "hafif", "yorgun")): return "yumusak"
    return "normal"


def replikler(film):
    """SAHNELER v2'deki konuşmalı planların replikleri (HIKAYE.json replikleri teslim ve tr ile birleştirilir).
    pencere_sn: planın kullanılabilir süresi (_derlenir.sure_sn ya da kullanim.sure) + L taşması (zanaat.kesme.ses_tasma_sn)."""
    S = sahneler(film); H = {r.get("id"): r for r in (hikaye(film).get("replikler") or []) if isinstance(r, dict)}
    out = []
    for p in S.get("sahneler") or []:
        r = p.get("replik")
        if not isinstance(r, dict) or not r.get("metin"): continue
        h = H.get(r.get("id")) or {}
        z = p.get("zanaat") or {}; d = p.get("_derlenir") or {}; ku = p.get("kullanim") or {}
        sure = d.get("sure_sn") or ku.get("sure") or z.get("klip_sn") or 8
        tasma = ((z.get("kesme") or {}).get("ses_tasma_sn") or 0) if isinstance(z.get("kesme"), dict) else 0
        cum = [c.get("en") for c in (r.get("cumleler") or []) if isinstance(c, dict) and c.get("en")] or _cumleler(r["metin"])
        out.append({"id": r.get("id") or f"P{p.get('no')}", "plan": p.get("no"), "sahne_grubu": z.get("sahne_grubu"),
                    "karakter": r.get("karakter") or h.get("karakter"), "metin": r["metin"],
                    "teslim": r.get("teslim") or h.get("teslim") or "normal", "cumleler": cum,
                    "tr": [c.get("tr", "") for c in (r.get("cumleler") or []) if isinstance(c, dict)] or [h.get("tr", "")],
                    "yol": (((z.get("ses") or {}).get("diyalog") or {}).get("yol")) or "tts",
                    "pencere_sn": round(float(sure) + float(tasma or 0), 3), "replik_zaman": (d.get("replik_zaman") or {}).get(r.get("id")),
                    "kullanim": ku, "seviye_ozel": (((z.get("ses") or {}).get("diyalog") or {}).get("seviye_ozel"))})
    return out


def evren_kok(film=None):
    try: y = ortak.yollar(); return y.get("evren_kok") or os.path.join(y["veri_kok"], "EVREN")
    except ortak.YolYok: return None


def seri(film):
    h = hikaye(film); e = h.get("evren")
    return (e.get("seri") if isinstance(e, dict) else e) or meta(film).get("seri")


def evren_ses_yolu(film, kar):
    """Kalıcı evren ses.json yolu (<evren>/<SERI>/karakterler/<id>/ses.json) ve film içi aşama kopyası (_SES/evren_ses/<id>/ses.json)."""
    kok, s = evren_kok(film), seri(film)
    kalici = os.path.join(kok, s, "karakterler", kar, "ses.json") if (kok and s) else None
    return kalici, os.path.join(film, "_SES", "evren_ses", kar, "ses.json")


def karakter_sesi(film, kar):
    """Seçilmiş ses: SAHNELER karakterler.<id>.ses → film içi aşama kopyası → kalıcı evren ses.json. Yoksa {voice_id: None}."""
    k = ((sahneler(film).get("karakterler") or {}).get(kar) or {})
    if k.get("ses") and not str(k["ses"]).startswith("<"): return {"voice_id": k["ses"], "kaynak": "SAHNELER"}
    for p, kaynak in zip(evren_ses_yolu(film, kar)[::-1], ("film_asama", "evren")):
        j = ortak.json_oku(p, None) if p else None
        v = ((j or {}).get("secim") or {}).get("voice_id")
        if v: return {"voice_id": v, "kaynak": kaynak, "seed": (j.get("secim") or {}).get("seed"), "model": (j.get("secim") or {}).get("model")}
    return {"voice_id": None, "kaynak": None}


# --- kredi (BUTK) ----------------------------------------------------------------------------------------------------
def kredi_onay(film, madde, kredi, dilim="film", saglayici_="ai84"):
    """AI84 bütçe noktası (kredi.butk). 0 onay · 5 BÜTÇE. Kredisiz sağlayıcıda çağrılmaz."""
    import kredi as K
    _, kod = K.butk(film, madde, int(kredi), birim="ai84", dilim=dilim, saglayici=saglayici_)
    return kod


def gonderim(film, madde, kredi, is_kimligi, dilim="film", saglayici_="ai84"):
    """Gönderim kaydı GÖNDERİMDEN ÖNCE (kesilirse kör yeniden gönderim olmaz; önce önbellek toplanır)."""
    import kredi as K
    return K.defter_ekle(film, "gonderim", int(kredi), birim="ai84", dilim=dilim, madde=madde, saglayici=saglayici_, is_kimligi=is_kimligi)


def gonderilmis(film, is_kimligi):
    import kredi as K
    return any(s.get("olay") == "gonderim" and s.get("is_kimligi") == is_kimligi for s in K.defter_oku(film)[0])


def arg(argv, ad, v=None):
    return argv[argv.index(ad) + 1] if ad in argv and argv.index(ad) + 1 < len(argv) else v
