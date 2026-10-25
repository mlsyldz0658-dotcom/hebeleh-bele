"""ORTAK Ö0 — ölçüm turu Ö0'ın ortak yazıcısı ve okuyucusu (TASARIM §1.2, §6.1 `olcum0/`).

Dosyalar (<veri>/BILGI/OLCUM0/):
  O0<harf>.json   bir ölçümün ayrıntısı. Kararı veren anahtarlar ÜST DÜZEYDEdir (okuyan araçlar düz okur):
                  O0b {durum, olculen_gunluk_kapasite*, olculemedi*, uretim_sn_720p, …}   (* yalnız durum "kapandi" olunca yazılır)
                  O0d {klon, sifreli, okuma, yayin_kaynagi, not_yolu}                       (capcut_yama.bayrak_acik: klon)
                  O0e {gemini_katman, video_girisi, ses_girisi, gorsel_uygun, gemini_api_paket, uc_aday_teslim}
                                                                                            (saglayicilar/gemini_api.o0e, olcek)
  OLCUM0.json     özet: {"_surum", "_uretim", "O0b": {...}, "O0d": {...}, "O0e": {...}, "denemeler": [...]} — olcek.py, kredi.py ve
                  plan_dili.py bunu okur (olcek._bolum: OLCUM0["O0b"]; plan_dili: üst düzey "canli_bekleme"). Bölüm, O0<harf>.json'un
                  karar anahtarlarının kopyasıdır. "denemeler": her deneme {olcum, deneme, olcu, karar, gerekce, zaman} (§1.2: "her deneme:
                  ölçüm, karar, gerekçe").
Kural: Ö0-b sürerken OLCUM0.O0b'de `olculen_gunluk_kapasite` ANAHTARI YOKTUR (olcek.kapasite anahtarın varlığını "Ö0-b yapıldı" sayar;
  ölçüm bitmeden BUT0 "Ö0-b yok → 1800 sn" demeli). Kapanınca değer (int) ya da None + olculemedi: true yazılır.
Durum: durum(harf) → "yok" | "hazir" | "suruyor" | "bitti" | "kapandi". Durum alanı olmayan eski/başka araç dosyası "bitti" sayılır.
Yazım atomiktir (ortak.atomik_yaz); OLCUM0.json okuma-değiştirme-yazma kısa bir kilit dosyasıyla (OLCUM0.kilit) yapılır.
Kodda: import ortak_o0 as o0; o0.kok() · o0.oku("b") · o0.yaz("b", veri, ozet={...}) · o0.deneme("b", ad, olcu, karar, gerekce)
       o0.durum("b") · o0.ozet_oku() · o0.ortam() · o0.zaman()
Anahtar dosyaları (AYARLAR/*_anahtar.txt, telegram_bot.txt) bu modül tarafından hiçbir zaman açılmaz.
"""
import os, sys, json, time, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for _p in (ARACLAR, HERE):
    if _p not in sys.path: sys.path.insert(0, _p)
import ortak

SURUM = "ortak_o0 1.0"
HARFLER = "abcdefgh"
BITMIS = ("bitti", "kapandi")
# OLCUM0.json bölümüne kopyalanan karar anahtarları (okuyan araçların beklediği adlar; yenisi eklenebilir, ad değişmez)
OZET_ANAHTAR = {
    "b": ("durum", "olculen_gunluk_kapasite", "olculemedi", "uretim_sn_720p", "politika_reddi_kredi", "on_kararlar", "klip_sayisi",
          "kapanis_nedeni", "olcum_yasak_bitis", "kapasite_kaynagi"),
    "d": ("durum", "klon", "sifreli", "okuma", "segment_tasima", "yayin_kaynagi", "not_yolu"),
    "e": ("durum", "gemini_katman", "video_girisi", "ses_girisi", "gorsel_uygun", "gemini_api_paket", "uc_aday_teslim",
          "gorsel_kota_gozlenen"),
}
KILIT_SN = 30


def zaman(t=None):
    t = time.time() if t is None else float(t)
    return datetime.datetime.fromtimestamp(t).astimezone().isoformat(timespec="seconds")


def ortam():
    """yerel | bulut (film.py ortam() ile aynı sıra: YZ_FILM_ORTAM → FILM_AYAR.json "ortam" → Windows ise yerel)."""
    v = os.environ.get("YZ_FILM_ORTAM")
    if v in ("yerel", "bulut"): return v
    try: a = ortak.json_oku(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {}) or {}
    except ortak.YolYok: a = {}
    if isinstance(a, dict) and a.get("ortam") in ("yerel", "bulut"): return a["ortam"]
    return "yerel" if os.name == "nt" else "bulut"


def kok():
    k = os.path.join(ortak.yollar()["veri_kok"], "BILGI", "OLCUM0"); os.makedirs(k, exist_ok=True); return k


def yol(harf): return os.path.join(kok(), f"O0{harf}.json")


def oku(harf):
    d = ortak.json_oku(yol(harf), {})
    return d if isinstance(d, dict) else {}


def ozet_yolu(): return os.path.join(kok(), "OLCUM0.json")


def ozet_oku():
    d = ortak.json_oku(ozet_yolu(), {})
    return d if isinstance(d, dict) else {}


def durum(harf):
    """yok | hazir | suruyor | bitti | kapandi (Ö0-g: <veri>/BILGI/KANAL_TESHIS.md da bitmiş sayılır)."""
    p = yol(harf)
    if not os.path.exists(p):
        if harf == "g":
            try:
                if os.path.exists(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "KANAL_TESHIS.md")): return "bitti"
            except ortak.YolYok: pass
        return "yok"
    d = oku(harf)
    return d.get("durum") if d.get("durum") in ("hazir", "suruyor", "bitti", "kapandi") else "bitti"


class _Kilit:
    def __init__(self, p): self.p = p; self.alindi = False

    def __enter__(self):
        bas = time.time()
        while True:
            try:
                fd = os.open(self.p, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, str(os.getpid()).encode()); os.close(fd)
                self.alindi = True; return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.p) > KILIT_SN:            # bayat kilit (çökmüş yazıcı)
                        os.replace(self.p, self.p + ".bayat"); continue
                except OSError: pass
                if time.time() - bas > KILIT_SN: raise RuntimeError("OLCUM0.kilit alınamadı")
                time.sleep(0.05)

    def __exit__(self, *a):
        if self.alindi:
            try: os.remove(self.p)
            except OSError: pass


def _ozet_guncelle(f):
    with _Kilit(os.path.join(kok(), "OLCUM0.kilit")):
        d = ozet_oku()
        d.setdefault("_surum", 1); d.setdefault("denemeler", [])
        f(d)
        d["_uretim"] = {"arac_surum": SURUM, "zaman": zaman(), "ortam": ortam()}
        ortak.atomik_yaz(ozet_yolu(), d)
        return d


def yaz(harf, veri, ozet=None, arac=None):
    """O0<harf>.json'u yazar ve OLCUM0.json'daki "O0<harf>" bölümünü günceller. ozet verilmezse OZET_ANAHTAR'daki anahtarlar
    veriden kopyalanır (verinin içinde olmayan anahtar bölüme girmez — ör. süren Ö0-b'de olculen_gunluk_kapasite)."""
    if harf not in HARFLER: raise ValueError(f"Ö0 harfi {harf!r}")
    v = dict(veri); v["_surum"] = 1
    v["_uretim"] = {"olcum": f"Ö0-{harf}", "arac_surum": arac or SURUM, "zaman": zaman(), "ortam": ortam()}
    ortak.atomik_yaz(yol(harf), v)
    if ozet is None: ozet = {k: v[k] for k in OZET_ANAHTAR.get(harf, ("durum",)) if k in v}
    _ozet_guncelle(lambda d: d.__setitem__(f"O0{harf}", dict(ozet)))
    return v


def deneme(harf, ad, olcu, karar, gerekce, ek=None):
    """OLCUM0.json "denemeler" listesine bir satır (ölçüm, karar, gerekçe)."""
    s = {"olcum": f"Ö0-{harf}", "deneme": ad, "olcu": olcu, "karar": karar, "gerekce": gerekce, "zaman": zaman()}
    if ek: s.update(ek)
    _ozet_guncelle(lambda d: d["denemeler"].append(s))
    return s


def esik(ad, varsayilan=None):
    """hat_esikleri/ritim_esikleri değeri (esikler.py); okunamazsa varsayılan."""
    try:
        import esikler
        v = esikler.yukle().get(ad)
        return varsayilan if v is None else v
    except Exception: return varsayilan
