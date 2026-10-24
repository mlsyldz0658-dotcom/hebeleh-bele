"""CAPCUT DENEME — Ö0-d: pycapcut ile taslak okuma, klon, segment taşıma; taslak şifrelemesi (TASARIM §1.2 Ö0-d, D-30, R11).

1 dk'lık deneme taslağı ("YZ_O0D_DENEME") kurulur; kullanıcı CapCut'ı iki kez açıp kapatır (fiziksel iş, soru değil):
  python capcut_deneme.py durum [--json]
  python capcut_deneme.py hazirla      CapCut KAPALIYKEN: 60 sn'lik deneme videosu (ffmpeg) + 6 segmentlik taslak (pycapcut)
        → kullanıcı: CapCut'ı aç, "YZ_O0D_DENEME" taslağını aç, 10 sn bekle, CapCut'ı kapat, "tamam" yaz
  python capcut_deneme.py olc          taslağı SALT OKUR (capcut_taslak.oku): şifreli mi, okunuyor mu; okunuyorsa klonlar (capcut_yama.klonla;
        kaynak HİÇ yazılmaz, özeti önce = sonra) ve klonda son segmenti 1 sn kaydırır
        → kullanıcı: CapCut'ı aç, "YZ_O0D_DENEME · klon" taslağını aç, 10 sn bekle, kapat, "tamam" yaz
  python capcut_deneme.py dogrula      klonu CapCut açıp kapadıktan sonra okur: kaydırma duruyor mu, şifrelendi mi → O0d.json kararı
Kararlar (O0d.json üst düzey; capcut_yama.bayrak_acik "klon" okur):
  sifreli true | false · okuma calisiyor | calismiyor · segment_tasima calisiyor | calismiyor · klon calisiyor | calismiyor
  yayin_kaynagi capcut (klon çalışıyor ve şifresiz) | master · not_yolu yama | yeni_adla_kur  (TASARIM §1.2: şifreliyse ya da klon
  çalışmıyorsa yayin_kaynagi: master ve not yolu "yeni adla kur")
Deneme taslakları silinmez (kalıcı silme yok); kullanıcı isterse CapCut'tan kendisi siler.
Çıkış kodları: 0 tamam · 1 HATA · 2 KULLANICI (CapCut açık, fiziksel iş bekleniyor, pycapcut yok) · 4 ORTAM (bulut).
"""
import os, sys, json, time, shutil, hashlib, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for _p in (ARACLAR, HERE):
    if _p not in sys.path: sys.path.insert(0, _p)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import ortak, ortak_o0 as o0

SURUM = "capcut_deneme 1.0"
BITTI, HATA, KULLANICI, ORTAM = 0, 1, 2, 4
AD = "YZ_O0D_DENEME"; KLON = AD + " · klon"
SEGMENT, SEGMENT_SN = 6, 10.0
KAYDIR_SN = 1.0
US = 1_000_000


class Dur(Exception):
    def __init__(self, msg, kod=HATA): super().__init__(msg); self.kod = kod


def taslak_kok(): return ortak.yollar()["capcut_taslak"]
def is_kok(): return os.path.join(o0.kok(), "O0d")


def durum_oku():
    d = o0.oku("d")
    return d if d else {"durum": "hazir", "adim": None}


def yaz(d): return o0.yaz("d", d, arac=SURUM)


def capcut_acik():
    """CapCut çalışıyor mu (yalnız Windows; tasklist). Bilinmiyorsa None."""
    if os.name != "nt": return None
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq CapCut.exe", "/NH"], capture_output=True, text=True, timeout=20)
        return "capcut.exe" in (r.stdout or "").lower()
    except Exception: return None


def _ozet(klasor):
    """Taslak klasörünün içerik özeti (draft_content dosyaları; salt okunur)."""
    import capcut_taslak as ct
    p = ct.icerik_yolu(klasor)
    if not os.path.isfile(p): return None
    with open(p, "rb") as f: return hashlib.sha1(f.read()).hexdigest()


def medya_uret(hedef):
    """60 sn'lik deneme videosu (renk çubukları + 440 Hz). ffmpeg."""
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=24",
                    "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000", "-t", str(SEGMENT * SEGMENT_SN), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", hedef], check=True)
    return hedef


def model(medya):
    segs = [{"segment_id": f"o0d-{i}", "yol": medya, "bas": i * SEGMENT_SN, "sure": SEGMENT_SN, "kaynak_bas": i * SEGMENT_SN,
             "kaynak_sure": SEGMENT_SN, "ses": 0.0} for i in range(SEGMENT)]
    return {"ad": AD, "fps": 24, "sure_us": int(SEGMENT * SEGMENT_SN * US), "kanallar": {"Klipler": segs}}


def hazirla(yazici=None, medya_fn=None, acik_fn=None):
    """Deneme taslağını kurar. yazici(m, kok) → (klasör, içerik); varsayılan capcut_taslak.yaz(…, sahte=False) (pycapcut)."""
    import capcut_taslak as ct
    d = durum_oku()
    if d.get("adim") not in (None, "hazirla"): raise Dur(f"Ö0-d zaten başladı (adım: {d['adim']}).", BITTI)
    if (acik_fn or capcut_acik)(): raise Dur("CapCut açık: önce CapCut'ı kapat, sonra 'tamam' yaz.", KULLANICI)
    yazici = yazici or (lambda m, k: ct.yaz(m, k, sahte=False))
    medya = (medya_fn or medya_uret)(os.path.join(is_kok(), "deneme_60sn.mp4"))
    try: klasor, _ = yazici(model(medya), taslak_kok())
    except ImportError as e:
        d.update(durum="suruyor", okuma="calismiyor", pycapcut="yok", neden=f"pycapcut kurulu değil ({e.__class__.__name__})")
        yaz(d); raise Dur("pycapcut kurulu değil (KURULUM.bat ile kurulur); Ö0-d sonra yapılır.", KULLANICI)
    d.update(durum="suruyor", adim="kullanici_1", taslak=klasor, ozet_yazilan=_ozet(klasor), hazirlik=o0.zaman())
    yaz(d)
    return d


def _segmentler(klasor):
    import capcut_taslak as ct
    o = ct.oku(klasor)
    if o["sifreli"]: return None, True
    if not o["icerik"]: return None, False
    return o["icerik"], False


def olc():
    import capcut_taslak as ct, capcut_yama as cy
    d = durum_oku()
    if d.get("adim") != "kullanici_1": raise Dur("Önce 'capcut_deneme.py hazirla' ve CapCut'ı bir kez açıp kapatman gerekiyor.", KULLANICI)
    if capcut_acik(): raise Dur("CapCut hâlâ açık: kapat, sonra 'tamam' yaz.", KULLANICI)
    kaynak = d["taslak"]; once = _ozet(kaynak)
    d["capcut_yeniden_yazdi"] = None if once is None else (once != d.get("ozet_yazilan"))
    ic, sifreli = _segmentler(kaynak)
    d["sifreli"] = bool(sifreli)
    if sifreli or ic is None:
        d.update(okuma="calismiyor", klon="calismiyor", segment_tasima="calismiyor", adim="bitti")
        return _karar(d, "taslak şifreli" if sifreli else "taslak okunamadı")
    kl = [s for s in ct.segmentler(ic) if s["tur"] == "video"]
    d["okuma"] = "calisiyor" if len(kl) == SEGMENT else "calismiyor"; d["okunan_segment"] = len(kl)
    hedef = os.path.join(os.path.dirname(kaynak), KLON); n = 2
    while os.path.exists(hedef): hedef = os.path.join(os.path.dirname(kaynak), f"{KLON} ({n})"); n += 1
    try:
        cy.klonla(kaynak, hedef)
        yol = ct.icerik_yolu(hedef); kic = ortak.json_oku(yol)
        son = max((s for t in kic.get("tracks") or [] if t.get("type") == "video" for s in t.get("segments") or []),
                  key=lambda s: (s.get("target_timerange") or {}).get("start", 0))
        son["target_timerange"]["start"] = int(son["target_timerange"]["start"] + KAYDIR_SN * US)
        ortak.atomik_yaz(yol, kic)
        d.update(klon_taslak=hedef, kaydirilan=son.get("id"), kaydirilan_bas_us=son["target_timerange"]["start"])
        kic2, s2 = _segmentler(hedef)
        ok = (not s2 and kic2 is not None and any(s["segment_id"] == son.get("id") and abs(s["bas"] * US - son["target_timerange"]["start"]) < 1000
                                                   for s in ct.segmentler(kic2)))
        d["segment_tasima"] = "calisiyor" if ok else "calismiyor"
    except Exception as e:
        d.update(segment_tasima="calismiyor", klon="calismiyor", klon_hata=str(e)[:160])
    d["kaynak_degismedi"] = _ozet(kaynak) == once
    if not d["kaynak_degismedi"]: d.update(klon="calismiyor", klon_hata="kaynak taslak değişti (olmamalı)")
    if d.get("klon") == "calismiyor" or d["segment_tasima"] != "calisiyor" or d["okuma"] != "calisiyor":
        d["klon"] = "calismiyor"; d["adim"] = "bitti"
        return _karar(d, "okuma/klon/segment taşıma çalışmadı")
    d["adim"] = "kullanici_2"; yaz(d)
    return d


def dogrula():
    import capcut_taslak as ct
    d = durum_oku()
    if d.get("adim") != "kullanici_2": raise Dur("Önce 'capcut_deneme.py olc' ve klonu CapCut'ta bir kez açıp kapatman gerekiyor.", KULLANICI)
    if capcut_acik(): raise Dur("CapCut hâlâ açık: kapat, sonra 'tamam' yaz.", KULLANICI)
    ic, sifreli = _segmentler(d["klon_taslak"])
    if sifreli:
        d.update(sifreli=True, klon="calismiyor", neden_klon="CapCut klonu açınca şifreledi")
    elif ic is None: d.update(klon="calismiyor", neden_klon="klon CapCut'tan sonra okunamadı")
    else:
        ss = {s["segment_id"]: s for s in ct.segmentler(ic)}; s = ss.get(d.get("kaydirilan"))
        tutuyor = s is not None and abs(s["bas"] * US - d["kaydirilan_bas_us"]) < 1000
        d["klon"] = "calisiyor" if tutuyor and len([x for x in ss.values() if x["tur"] == "video"]) == SEGMENT else "calismiyor"
        if d["klon"] != "calisiyor": d["neden_klon"] = "kaydırma ya da segment sayısı CapCut'tan sonra tutmuyor"
    rm = ortak.json_oku(os.path.join(os.path.dirname(d["klon_taslak"]), "root_meta_info.json"), None)
    d["capcut_listede"] = None if not isinstance(rm, dict) else (os.path.basename(d["klon_taslak"]) in json.dumps(rm, ensure_ascii=False))
    d["adim"] = "bitti"
    return _karar(d, d.get("neden_klon") or "klon CapCut'ta açıldı, kaydırma korundu")


def _karar(d, gerekce):
    iyi = d.get("klon") == "calisiyor" and not d.get("sifreli")
    d.update(durum="bitti", yayin_kaynagi="capcut" if iyi else "master", not_yolu="yama" if iyi else "yeni_adla_kur", bitis=o0.zaman())
    yaz(d)
    for ad in ("sifreli", "okuma", "segment_tasima", "klon"):
        o0.deneme("d", ad, d.get(ad), d.get(ad), gerekce)
    o0.deneme("d", "yayin_kaynagi", d["yayin_kaynagi"], d["yayin_kaynagi"],
              "klon çalışıyor ve şifresiz → CapCut dışa aktarımı; değilse master ve 'yeni adla kur' (TASARIM §1.2)")
    return d


def durum_metni():
    d = durum_oku()
    son = {None: "hazirla", "hazirla": "hazirla", "kullanici_1": "olc", "kullanici_2": "dogrula", "bitti": None}.get(d.get("adim"))
    kul = {"kullanici_1": f"CapCut'ı aç, '{AD}' taslağını aç, 10 saniye bekle, CapCut'ı kapat ve 'tamam' yaz.",
           "kullanici_2": f"CapCut'ı aç, '{KLON}' taslağını aç, 10 saniye bekle, CapCut'ı kapat ve 'tamam' yaz."}.get(d.get("adim"))
    return {"durum": o0.durum("d"), "adim": d.get("adim"), "sonraki": son, "kullaniciya": kul,
            "karar": {k: d.get(k) for k in ("klon", "sifreli", "yayin_kaynagi", "not_yolu") if k in d}}


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    k = argv[0]
    try:
        if k == "durum": print(json.dumps(durum_metni(), ensure_ascii=False)); return 0
        if o0.ortam() == "bulut": print("Ö0-d yalnız kullanıcının bilgisayarında yapılır."); return ORTAM
        if k in ("hazirla", "olc", "dogrula"):
            {"hazirla": hazirla, "olc": olc, "dogrula": dogrula}[k]()
            r = durum_metni(); print(r["kullaniciya"] or json.dumps(r["karar"], ensure_ascii=False)); return 0
    except Dur as e: print(str(e)); return e.kod
    except ortak.YolYok as e: print(str(e)); return ORTAM
    print(__doc__); return ORTAM


if __name__ == "__main__":
    sys.exit(main())
