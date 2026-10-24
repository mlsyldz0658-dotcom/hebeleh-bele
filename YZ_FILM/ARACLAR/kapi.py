"""KAPI — bütün kapıların ortak rapor zarfı, sonuç birleştirme ve denetim (TASARIM §5.7, §7.1, §7.2, §6.1).

Kullanım:
  python kapi.py --denetle <rapor.json> [<rapor.json> ...]   zarfı ve sonucu denetler (HATA varsa çıkış 1)
  python kapi.py --ozet <film>/_RAPOR [--kapi G1]            klasördeki kapı raporlarının sonuçlarını listeler
Kodda:
  import kapi
  yol, r = kapi.kaydet("<film>/_RAPOR", "G1", "P1_B2", olcumler, tur=1, asama="A11", gorev="A11-G1-007",
                       girdi_imza="c3d4e5", arac_surum="kare_denetim 1.0", birimler=[201, 202, 214])
  kapi.oku(yol) → sözlük (bozuksa RaporHatasi) · kapi.dogrula(r) → hata listesi · kapi.son_sonuc(klasor, "G1", "P1_B2")
Kurallar:
  - Rapor yolu `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json`; `_t<tur>` yalnız tur_dosyada=True ise eklenir (HS_* gibi turlu kapılar).
  - Sonuç kodları (veri/ADLAR.json `sonuc_kodlari.kapi`): GEC · KISMI · HATA · BAYRAK · OLCULEMEDI. Gelen eş adlar çevrilir
    (GEÇ→GEC, KAL/H→HATA, B/UYARI→BAYRAK, ÖLÇÜLEMEDİ→OLCULEMEDI). **ÖLÇÜLEMEDİ her zaman BAYRAK sayılır, asla GEÇ değildir**;
    raporun kendi sonucu hiçbir zaman OLCULEMEDI olmaz. Hiç ölçüm yoksa sonuç BAYRAK'tır (ölçülmemiş kapı geçmiş sayılmaz).
  - Ölçüm: {madde, plan?|birim?, seviye: GEC|BAYRAK|HATA|OLCULEMEDI, olcu?, esik?, oneri?, kanit?, neden?}. plan/birim yoksa ölçüm
    film düzeyidir. Birimin sonucu ölçümlerinin en kötüsüdür (HATA > BAYRAK > GEC).
  - Kapı sonucu: film düzeyinde HATA ya da bütün birimler HATA → HATA · bir kısmı HATA → KISMI · HATA yok, BAYRAK var → BAYRAK · → GEC.
  - Yazım `ortak.atomik_yaz` ile; yazmadan önce dogrula() — biçim hatası RaporHatasi'dır, yarım ya da bozuk rapor yazılmaz.
Çıkış kodları: 0 tamam · 1 rapor HATA'lı ya da bozuk · 2 dosya/klasör yok · 4 kullanım hatası.
"""
import os, sys, re, json, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kapi 1.0"
RAPOR_SURUM = 1
SONUCLAR = ("GEC", "KISMI", "HATA", "BAYRAK", "OLCULEMEDI")
RAPOR_SONUCLARI = ("GEC", "KISMI", "HATA", "BAYRAK")          # raporun kendisi OLCULEMEDI olamaz
MADDE_SEVIYELERI = ("GEC", "BAYRAK", "HATA", "OLCULEMEDI")
ESDEGER = {"GEÇ": "GEC", "GECTI": "GEC", "GEÇTİ": "GEC", "OK": "GEC", "KAL": "HATA", "KALDI": "HATA", "H": "HATA",
           "B": "BAYRAK", "UYARI": "BAYRAK", "ÖLÇÜLEMEDİ": "OLCULEMEDI", "OLCULEMEDİ": "OLCULEMEDI", "KISMİ": "KISMI"}
_SIRA = {"GEC": 0, "BAYRAK": 1, "KISMI": 2, "HATA": 3}        # en_kotu() için
ZARF_ALANLARI = ("asama", "gorev", "girdi_imza", "arac_surum", "esik_surum", "sonuc", "zaman", "ortam")  # ADLAR plan_alanlari.uretim_zarfi
KAPSAM_DESEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.\-]*")
FILM_BIRIMI = "_film"


class RaporHatasi(Exception):
    def __init__(self, hatalar, yol=None):
        self.hatalar = list(hatalar) if isinstance(hatalar, (list, tuple)) else [str(hatalar)]
        super().__init__((f"{yol}: " if yol else "") + "; ".join(self.hatalar))


_ADLAR = None
def adlar():
    global _ADLAR
    if _ADLAR is None:
        _ADLAR = ortak.json_oku(os.path.join(HERE, "veri", "ADLAR.json"), {}) or {}
    return _ADLAR


def kapi_kodlari(): return {k for k in (adlar().get("kapilar") or {}) if not k.startswith("_")}
def asama_kodlari(): return set(adlar().get("asamalar") or {})


def ortam():
    """Raporun yazıldığı ortam: YZ_FILM_ORTAM ya da işletim sistemine göre (üretim yalnız Windows'ta; D-12)."""
    f = getattr(ortak, "ortam", None)
    if callable(f):
        try: return f()
        except Exception: pass
    return os.environ.get("YZ_FILM_ORTAM") or ("yerel" if os.name == "nt" else "bulut")


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


# --- sonuç kodları ----------------------------------------------------------------------------------------------
def sonuc_normal(s):
    """Sonuç kodunu ADLAR biçimine çevirir; bilinmeyen kod ValueError."""
    if not isinstance(s, str): raise ValueError(f"sonuç kodu metin değil: {s!r}")
    k = s.strip().upper()
    k = ESDEGER.get(k, ESDEGER.get(s.strip(), k))
    if k not in SONUCLAR: raise ValueError(f"bilinmeyen sonuç kodu: {s!r} ({'|'.join(SONUCLAR)})")
    return k


def madde_sonucu(s):
    """Tek ölçümün kapıdaki etkisi: GEC | BAYRAK | HATA. ÖLÇÜLEMEDİ → BAYRAK (asla GEC)."""
    k = sonuc_normal(s)
    if k == "OLCULEMEDI": return "BAYRAK"
    if k == "KISMI": return "HATA"
    return k


def en_kotu(sonuclar):
    """Aynı birim için birden çok sonucun en kötüsü (HATA > KISMI > BAYRAK > GEC). Boş liste → BAYRAK (ölçülmedi)."""
    ks = [sonuc_normal(s) for s in sonuclar]
    if not ks: return "BAYRAK"
    ks = ["BAYRAK" if k == "OLCULEMEDI" else k for k in ks]
    return max(ks, key=_SIRA.__getitem__)


def birlestir(sonuclar):
    """Farklı kapsamların (alt raporların) sonuçlarını tek kapı sonucuna birleştirir.
    Hepsi HATA → HATA · HATA/KISMI var ama hepsi değil → KISMI · BAYRAK/ÖLÇÜLEMEDİ var → BAYRAK · hepsi GEC → GEC · boş → BAYRAK."""
    ks = [sonuc_normal(s) for s in sonuclar]
    if not ks: return "BAYRAK"
    if all(k == "HATA" for k in ks): return "HATA"
    if any(k in ("HATA", "KISMI") for k in ks): return "KISMI"
    if any(k in ("BAYRAK", "OLCULEMEDI") for k in ks): return "BAYRAK"
    return "GEC"


def gecti_mi(sonuc):
    """Yalnız GEC geçer (sıra kuralı 1: kredili aşamadan önceki kapılar GEÇ olmalı). BAYRAK ve ÖLÇÜLEMEDİ geçmiş sayılmaz."""
    return sonuc_normal(sonuc) == "GEC"


def engelsiz_mi(sonuc):
    """HATA yok mu (GEC ya da BAYRAK)? BAYRAK'ta hat sürer, sahibi ya da hakem bakar (§7.1)."""
    return sonuc_normal(sonuc) in ("GEC", "BAYRAK")


# --- rapor kurma ------------------------------------------------------------------------------------------------
def _birim(o):
    if o.get("plan") is not None: return o["plan"]
    if o.get("birim") is not None: return o["birim"]
    return FILM_BIRIMI


def rapor_kur(kapi, kapsam, olcumler, tur=1, asama=None, gorev=None, girdi_imza=None, arac_surum=None, esik_surum=None,
              ortam_adi=None, birim="plan", birimler=None, kuyruk=None, ek=None, zaman=None):
    """Ölçümlerden zarflı rapor sözlüğü kurar (yazmaz). birimler: değerlendirilen bütün birimler (ölçümü olmayanlar GEC sayılır).
    kuyruk: kuyruk.py'nin toplayacağı YENIDEN_URET madde önerileri (id'siz). ek: rapora eklenecek kapıya özel alanlar."""
    olcumler = list(olcumler or [])
    hatalar, bayraklar, durum, olc_birim = [], [], {}, set()
    for i, o in enumerate(olcumler):
        if not isinstance(o, dict): raise RaporHatasi([f"ölçüm {i}: sözlük değil"])
        if not o.get("madde"): raise RaporHatasi([f"ölçüm {i}: 'madde' yok"])
        ham = sonuc_normal(o.get("seviye", ""))
        if ham not in MADDE_SEVIYELERI: raise RaporHatasi([f"ölçüm {i} ({o['madde']}): seviye {ham} ölçümde kullanılmaz"])
        etki = madde_sonucu(ham); b = _birim(o)
        durum.setdefault(b, []).append(etki)
        if ham == "OLCULEMEDI": olc_birim.add(b)
        if etki == "GEC": continue
        kayit = {k: v for k, v in o.items() if k != "seviye"}
        kayit["seviye"] = etki
        if ham == "OLCULEMEDI": kayit["olculemedi"] = True
        (hatalar if etki == "HATA" else bayraklar).append(kayit)
    for b in birimler or []: durum.setdefault(b, [])
    birim_sonuc = {b: (en_kotu(s) if s else "GEC") for b, s in durum.items()}
    film_hata = birim_sonuc.pop(FILM_BIRIMI, None)
    bs = list(birim_sonuc.values())
    if not bs and film_hata is None: sonuc = "BAYRAK"                     # ölçüm yok: geçmiş sayılmaz
    elif film_hata == "HATA" or (bs and all(s == "HATA" for s in bs)): sonuc = "HATA"
    elif any(s == "HATA" for s in bs): sonuc = "KISMI"
    elif film_hata == "BAYRAK" or any(s == "BAYRAK" for s in bs): sonuc = "BAYRAK"
    else: sonuc = "GEC"
    olc_birim.discard(FILM_BIRIMI)
    ozet = {birim: len(bs), "gec": sum(s == "GEC" for s in bs), "bayrak": sum(s == "BAYRAK" for s in bs),
            "hata": sum(s == "HATA" for s in bs), "olculemedi": len(olc_birim)}
    if film_hata is not None: ozet["film"] = film_hata
    if esik_surum is None:
        try:
            import esikler; esik_surum = esikler.SURUM
        except Exception: esik_surum = None
    r = {"_surum": RAPOR_SURUM,
         "_uretim": {"asama": asama, "gorev": gorev, "girdi_imza": girdi_imza, "arac_surum": arac_surum or SURUM,
                     "esik_surum": esik_surum, "sonuc": sonuc, "zaman": zaman or simdi(), "ortam": ortam_adi or ortam()},
         "kapi": kapi, "kapsam": kapsam, "tur": tur, "sonuc": sonuc, "ozet": ozet, "hatalar": hatalar, "bayraklar": bayraklar}
    if kuyruk is not None: r["kuyruk"] = list(kuyruk)
    for k, v in (ek or {}).items():
        if k in r: raise RaporHatasi([f"ek alan zarf alanını eziyor: {k}"])
        r[k] = v
    return r


def dogrula(r):
    """Zarf ve sonuç denetimi; hata listesi döndürür (boş = geçerli)."""
    h = []
    if not isinstance(r, dict): return ["rapor sözlük değil"]
    if "surum" in r: h.append("alt çizgisiz 'surum' geçersiz; '_surum' kullan")
    if not (isinstance(r.get("_surum"), int) and not isinstance(r.get("_surum"), bool) and r["_surum"] >= 1):
        h.append("_surum yok ya da geçersiz")
    u = r.get("_uretim")
    if not isinstance(u, dict): h.append("_uretim zarfı yok"); u = {}
    for a in ZARF_ALANLARI:
        if a not in u: h.append(f"_uretim.{a} yok")
    for a in ("arac_surum", "zaman", "ortam"):
        if a in u and not (isinstance(u[a], str) and u[a].strip()): h.append(f"_uretim.{a} boş")
    if u.get("asama") is not None and u["asama"] not in asama_kodlari(): h.append(f"_uretim.asama bilinmiyor: {u['asama']!r}")
    kod = r.get("kapi")
    if kod not in kapi_kodlari(): h.append(f"kapi bilinmiyor (veri/ADLAR.json kapilar): {kod!r}")
    kp = r.get("kapsam")
    if not (isinstance(kp, str) and KAPSAM_DESEN.fullmatch(kp)): h.append(f"kapsam geçersiz: {kp!r}")
    t = r.get("tur")
    if not (isinstance(t, int) and not isinstance(t, bool) and t >= 1): h.append(f"tur ≥ 1 tamsayı olmalı: {t!r}")
    s = r.get("sonuc")
    if s not in RAPOR_SONUCLARI: h.append(f"sonuc geçersiz: {s!r} ({'|'.join(RAPOR_SONUCLARI)}; ÖLÇÜLEMEDİ → BAYRAK)")
    if u.get("sonuc") is not None and u.get("sonuc") != s: h.append("_uretim.sonuc ile sonuc farklı")
    oz = r.get("ozet")
    if not isinstance(oz, dict): h.append("ozet yok")
    else:
        for a in ("gec", "bayrak", "hata", "olculemedi"):
            if not (isinstance(oz.get(a), int) and oz[a] >= 0): h.append(f"ozet.{a} yok ya da negatif")
    hl, bl = r.get("hatalar"), r.get("bayraklar", [])
    if not isinstance(hl, list): h.append("hatalar listesi yok"); hl = []
    if not isinstance(bl, list): h.append("bayraklar liste değil"); bl = []
    for i, m in enumerate(hl):
        if not (isinstance(m, dict) and m.get("madde")): h.append(f"hatalar[{i}]: madde yok"); continue
        if m.get("seviye") != "HATA": h.append(f"hatalar[{i}]: seviye HATA olmalı ({m.get('seviye')!r})")
    for i, m in enumerate(bl):
        if not (isinstance(m, dict) and m.get("madde")): h.append(f"bayraklar[{i}]: madde yok"); continue
        if m.get("seviye") != "BAYRAK": h.append(f"bayraklar[{i}]: seviye BAYRAK olmalı ({m.get('seviye')!r})")
    if s in RAPOR_SONUCLARI:
        if hl and s not in ("HATA", "KISMI"): h.append(f"HATA maddesi var ama sonuc {s}")
        if s in ("HATA", "KISMI") and not hl: h.append(f"sonuc {s} ama hatalar boş")
        if s == "GEC" and (bl or (isinstance(oz, dict) and oz.get("olculemedi"))):
            h.append("BAYRAK ya da ÖLÇÜLEMEDİ varken sonuc GEC olamaz")
    if "kuyruk" in r and not isinstance(r["kuyruk"], list): h.append("kuyruk liste değil")
    return h


# --- yol, yazma, okuma ------------------------------------------------------------------------------------------
def dosya_adi(kapi, kapsam, tur=None):
    if not KAPSAM_DESEN.fullmatch(str(kapsam)): raise RaporHatasi([f"kapsam geçersiz: {kapsam!r}"])
    return f"{kapi}_{kapsam}" + (f"_t{int(tur)}" if tur is not None else "") + ".json"


def rapor_yolu(rapor_klasoru, kapi, kapsam, tur=None):
    """`<_RAPOR>/<KAPI>_<kapsam>[_t<tur>].json` (tur verilirse son ek)."""
    return os.path.join(rapor_klasoru, dosya_adi(kapi, kapsam, tur))


def yaz(rapor_klasoru, r, tur_dosyada=False):
    """Raporu denetler ve atomik yazar; yolu döndürür. Geçersizse RaporHatasi (dosya yazılmaz)."""
    h = dogrula(r)
    if h: raise RaporHatasi(h)
    yol = rapor_yolu(rapor_klasoru, r["kapi"], r["kapsam"], r["tur"] if tur_dosyada else None)
    ortak.atomik_yaz(yol, r)
    return yol


def kaydet(rapor_klasoru, kapi, kapsam, olcumler, tur_dosyada=False, **kw):
    """rapor_kur + yaz. (yol, rapor)."""
    r = rapor_kur(kapi, kapsam, olcumler, **kw)
    return yaz(rapor_klasoru, r, tur_dosyada=tur_dosyada), r


def oku(yol):
    """Raporu okur ve denetler; yoksa, bozuksa ya da zarfı geçersizse RaporHatasi."""
    try:
        with open(yol, encoding="utf-8-sig") as f: r = json.load(f)
    except OSError as e: raise RaporHatasi([f"okunamadı ({e.__class__.__name__})"], yol)
    except ValueError as e: raise RaporHatasi([f"JSON bozuk ({e})"], yol)
    h = dogrula(r)
    if h: raise RaporHatasi(h, yol)
    return r


def raporlar(rapor_klasoru, kapi=None):
    """Klasördeki geçerli kapı raporları: [(yol, rapor)] (ad sırasıyla). Kapı raporu olmayan ya da bozuk dosyalar atlanır."""
    out = []
    if not os.path.isdir(rapor_klasoru): return out
    for ad in sorted(os.listdir(rapor_klasoru)):
        if not ad.endswith(".json"): continue
        yol = os.path.join(rapor_klasoru, ad)
        r = ortak.json_oku(yol)
        if not isinstance(r, dict) or "kapi" not in r or (kapi and r.get("kapi") != kapi): continue
        if dogrula(r): continue
        out.append((yol, r))
    return out


def son_sonuc(rapor_klasoru, kapi, kapsam=None, girdi_imza=None):
    """Bir kapının en son raporunun sonucu (yoksa None). kapsam ve girdi_imza verilirse yalnız eşleşen raporlar sayılır
    (sıra kuralı 1: aynı girdi imzasıyla GEÇ). En son = en büyük tur, eşitse en yeni zaman."""
    aday = [r for _, r in raporlar(rapor_klasoru, kapi)
            if (kapsam is None or r.get("kapsam") == kapsam)
            and (girdi_imza is None or r["_uretim"].get("girdi_imza") == girdi_imza)]
    if not aday: return None
    return max(aday, key=lambda r: (r.get("tur", 0), r["_uretim"].get("zaman") or ""))["sonuc"]


def main(argv):
    if len(argv) >= 2 and argv[0] == "--denetle":
        kod = 0
        for yol in argv[1:]:
            if not os.path.exists(yol): print(f"!! {yol}: dosya yok"); kod = max(kod, 2); continue
            try: r = oku(yol)
            except RaporHatasi as e:
                print(f"HATA {yol}"); [print("   -", x) for x in e.hatalar]; kod = max(kod, 1); continue
            print(f"GEÇERLİ {os.path.basename(yol)}: {r['kapi']} {r['kapsam']} t{r['tur']} → {r['sonuc']}")
        return kod
    if len(argv) >= 2 and argv[0] == "--ozet":
        klasor = argv[1]; kapi = None
        if len(argv) == 4 and argv[2] == "--kapi": kapi = argv[3]
        elif len(argv) != 2: print(__doc__); return 4
        if not os.path.isdir(klasor): print(f"!! klasör yok: {klasor}"); return 2
        rs = raporlar(klasor, kapi)
        for yol, r in rs:
            oz = r["ozet"]
            print(f"{os.path.basename(yol)}: {r['sonuc']} · geç {oz['gec']} · bayrak {oz['bayrak']} · hata {oz['hata']} · "
                  f"ölçülemedi {oz['olculemedi']}")
        print(f"Toplam {len(rs)} rapor; birleşik sonuç: {birlestir([r['sonuc'] for _, r in rs]) if rs else '—'}")
        return 0
    print(__doc__)
    return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
