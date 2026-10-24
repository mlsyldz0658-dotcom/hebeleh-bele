"""EVREN — seri evreni kütüphanesi <evren>/ (TASARIM §5.4, §6.3, D-42). <evren>/ altına YALNIZ bu araç yazar.

Kullanım:
  python evren.py --on-kayit --film <film> [--seri SERI]     A06 kilidi (hikaye_odasi.py devir çağırır): seri adı, karakter kimlikleri,
        adlar, kostüm ve mekân kimlikleri kilitlenir; yoksa evren.json, hikaye.json, karakterler/<id>/{karakter,hikaye}.json ve
        mekanlar/<id>/mekan.json açılır. Var olan kimlik başka adla gelirse HATA (1); hiçbir dosya silinmez, değişen dosyanın eski hâli
        <ad>_v<n>.json olarak kalır. Aynı film için yeniden çalıştırmak bir şey değiştirmez.
  python evren.py ne_yok_kelimeleri [--seri SERI | --film <film>] [--json]
        NE YOK kelimeleri (EN, küçük harf): hikaye.json ne_yok_hikaye[].kelimeler_en + dunya.json gorsel_ne_yok + karakter yasakları;
        --film verilirse filmin HIKAYE/senaryo/konu kartındaki ne_yok listeleri de eklenir (evren yoksa yalnız onlar).
  python evren.py ozet [--seri SERI] [--json]               evren dizini: seri adları, filmler, karakterler, açık seri soruları
        (A01 yapımcısının GIRDI'si; görüntü dosyası yok, yalnız metin).
  Kodda: import evren; evren.ne_yok_kelimeleri(seri=None, film=None) → [kelime] · evren.ozet(seri=None) → sözlük ·
         evren.on_kayit(film, seri=None) → (rapor, kod)
Yol: ortak.yollar()["evren_kok"] (YOLLAR.json; varsayılan <veri>/EVREN). Seri adı A–Z, 0–9 ve _ (büyük harf).
  python evren.py --kilitle --film <film> [--seri SERI]      A10d: KART_SECIM + KART_KAPISI → kartlar evrene sürümle kopyalanır ve
        kilitlenir (SHA1, kimlik bankası); HATA'lı aday ve adı içeren kimlik_en reddedilir (ayrıntı: evren_kilit.py)
  python evren.py --kilit-dogrula [--seri SERI | --film <film>]   kilitli dosyaların SHA1'i (değişmişse 1: hat durur)
  python evren.py --surum-ac --karakter <id> [--seri SERI | --film <film>]   kilitli karakterde yeni sürüm
  python evren.py --film-sonu --film <film> · --yedekle (--film <film> | --seri SERI) · --yedek-dogrula (...)   A18/A00 (ayrıntı:
        evren_film_sonu.py; yedek yalnız KOPYA, AYARLAR girmez, /MIR ve /MOVE yok)
  Kodda: evren.ses_kaydet(film, karakter, kayit) → <evren>/<SERI>/karakterler/<id>/ses.json (sürümlü; eski hâli ses_v<n>.json)
Henüz yok (TASARIM §6.3, sonraki PR'lar): --kur, --bagla, --spec-dogrula, --disa-aktar, --ice-al, hikaye-kaydet --dogrula,
  izleyici-ozeti. Çağrılırsa 4 (ORTAM) ile "henüz yok" der.
Çıkış kodları: 0 tamam · 1 HATA (kimlik çakışması, HIKAYE.json yok ya da bozuk) · 4 ORTAM (yol yok, komut henüz yok).
"""
import os, sys, re, json, glob, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "evren 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
SERI_DESEN = re.compile(r"[A-Z0-9][A-Z0-9_]{1,40}")
KIMLIK_DESEN = re.compile(r"[a-z0-9][a-z0-9_]{0,40}")
SONRAKI = ("--kur", "--bagla", "--spec-dogrula", "--disa-aktar", "--ice-al", "hikaye-kaydet", "izleyici-ozeti")
FILM_SONU = ("--film-sonu", "--yedekle", "--yedek-dogrula")      # A18/A00: evren_film_sonu.py'ye yönlendirilir


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def evren_kok():
    y = ortak.yollar()
    return y.get("evren_kok") or os.path.join(y["veri_kok"], "EVREN")


def seri_normal(s):
    if not s: return None
    s = re.sub(r"[^A-Z0-9_]", "_", str(s).strip().upper().replace(" ", "_")).strip("_")
    return s if SERI_DESEN.fullmatch(s or "") else None


def seri_yolu(seri, *p): return os.path.join(evren_kok(), seri, *p)


def seriler():
    k = evren_kok()
    if not os.path.isdir(k): return []
    return sorted(d for d in os.listdir(k) if SERI_DESEN.fullmatch(d) and os.path.isfile(os.path.join(k, d, "evren.json")))


def _oku(p, v=None): return ortak.json_oku(p, v)


def _surumlu_yaz(p, veri):
    """Değişiklik varsa eski dosyayı <ad>_v<n>.json olarak bırakır (silme yok), yenisini atomik yazar. Değişti mi döner."""
    eski = _oku(p)
    if eski == veri: return False
    if eski is not None:
        kok, uz = os.path.splitext(p); n = 1
        while os.path.exists(f"{kok}_v{n}{uz}"): n += 1
        os.replace(p, f"{kok}_v{n}{uz}")
    ortak.atomik_yaz(p, veri)
    return True


# --- film tarafı ------------------------------------------------------------------------------------------------
def film_hikaye(film):
    """Filmin kilitli HIKAYE.json'u; yoksa en son 06_SENARYO_v<N>.json (A05/A06 sırasında)."""
    h = _oku(os.path.join(film, "HIKAYE.json"))
    if isinstance(h, dict): return h
    adaylar = []
    for p in glob.glob(os.path.join(film, "_HIKAYE_ODASI", "06_SENARYO_v*.json")):
        m = re.search(r"_v(\d+)\.json$", p)
        if m: adaylar.append((int(m.group(1)), os.path.getmtime(p), p))
    for _, _, p in sorted(adaylar, reverse=True):
        h = _oku(p)
        if isinstance(h, dict): return h
    return None


def film_serisi(film, hikaye=None):
    h = hikaye if hikaye is not None else (film_hikaye(film) or {})
    for aday in (h.get("evren"), (_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}).get("seri"),
                 ((_oku(os.path.join(film, "_HIKAYE_ODASI", "01_KONU_KARTI.json"), {}) or {}).get("seri") or {}).get("evren"),
                 (_oku(os.path.join(film, "_HIKAYE_ODASI", "04_SECIM.json"), {}) or {}).get("seri_adi")):
        s = seri_normal(aday)
        if s: return s
    return None


def _kelimeler(liste):
    out = []
    for x in liste or []:
        if isinstance(x, str): out.append(x)
        elif isinstance(x, dict):
            out += [k for k in (x.get("kelimeler_en") or []) if isinstance(k, str)]
            if isinstance(x.get("oge_en"), str): out.append(x["oge_en"])
    return out


def ne_yok_kelimeleri(seri=None, film=None):
    """Küçük harfli, tekrarsız, sıralı NE YOK kelimeleri."""
    k = []
    if film and not seri: seri = film_serisi(film)
    if seri and os.path.isdir(seri_yolu(seri)):
        h = _oku(seri_yolu(seri, "hikaye.json"), {}) or {}
        k += _kelimeler(h.get("ne_yok_hikaye"))
        d = _oku(seri_yolu(seri, "dunya.json"), {}) or {}
        k += _kelimeler(d.get("gorsel_ne_yok") or d.get("ne_yok"))
        for p in glob.glob(seri_yolu(seri, "karakterler", "*", "karakter.json")):
            k += [x for x in ((_oku(p, {}) or {}).get("yasak") or []) if isinstance(x, str)]
    if film:
        h = film_hikaye(film) or {}
        k += _kelimeler(h.get("ne_yok") or h.get("ne_yok_hikaye"))
        for kar in (h.get("karakterler") or {}).values():
            if isinstance(kar, dict): k += [x for x in (kar.get("yasak") or []) if isinstance(x, str)]
        kk = _oku(os.path.join(film, "_HIKAYE_ODASI", "01_KONU_KARTI.json"), {}) or {}
        k += _kelimeler(kk.get("ne_yok"))
    return sorted({x.strip().lower() for x in k if x and x.strip()})


def ozet(seri=None):
    out = {"evren_kok": evren_kok(), "seriler": []}
    for s in ([seri] if seri else seriler()):
        e = _oku(seri_yolu(s, "evren.json"), {}) or {}
        h = _oku(seri_yolu(s, "hikaye.json"), {}) or {}
        kar = []
        for p in sorted(glob.glob(seri_yolu(s, "karakterler", "*", "karakter.json"))):
            c = _oku(p, {}) or {}
            kar.append({"id": c.get("id"), "ad": c.get("ad"), "tur": c.get("tur"), "durum": c.get("durum")})
        out["seriler"].append({
            "seri": s, "surum": e.get("surum"), "filmler": e.get("filmler") or [], "kilit": e.get("kilit_durumu"),
            "donem": h.get("donem"), "karakterler": kar,
            "acik_seri_sorulari": [q.get("soru") for q in h.get("seri_sorulari") or [] if q.get("durum") == "acik"],
            "baslik_gecmisi": [b.get("baslik") for b in h.get("baslik_gecmisi") or []]})
    return out


def ozet_md(o):
    if not o["seriler"]: return "Evren kütüphanesi boş (kayıtlı seri yok). Yeni seri açılır.\n"
    s = ["# Evren özeti", ""]
    for x in o["seriler"]:
        s.append(f"## {x['seri']} (sürüm {x['surum']}, {len(x['filmler'])} film)")
        if x["donem"]: s.append(f"- Dönem: {json.dumps(x['donem'], ensure_ascii=False)}")
        s.append("- Karakterler: " + (", ".join(f"{c['ad'] or c['id']} ({c['durum']})" for c in x["karakterler"]) or "—"))
        s.append("- Açık seri soruları: " + ("; ".join(q for q in x["acik_seri_sorulari"] if q) or "—"))
        if x["baslik_gecmisi"]: s.append("- Başlıklar: " + "; ".join(x["baslik_gecmisi"]))
        s.append("")
    return "\n".join(s) + "\n"


# --- ön kayıt ---------------------------------------------------------------------------------------------------
def _kimlikler(h):
    kar = {}
    for kid, k in (h.get("karakterler") or {}).items():
        if not isinstance(k, dict): continue
        kost = k.get("kostum") or {}
        kar[kid] = {"ad": k.get("ad") or kid, "tur": "yaratik" if k.get("rol") == "yaratik" else k.get("tur", "insan"),
                    "kostumler": sorted(set(kost.get("varyantlar") or ([kost["varsayilan"]] if kost.get("varsayilan") else []))),
                    "varsayilan_kostum": kost.get("varsayilan"), "ad_telaffuz": k.get("ad_telaffuz")}
    mek = [m.get("id") for m in h.get("mekanlar") or [] if isinstance(m, dict) and m.get("id")]
    return kar, mek


def on_kayit(film, seri=None):
    """(rapor, kod). Kimlik çakışmasında hiçbir dosya yazılmaz."""
    film = os.path.abspath(film)
    h = _oku(os.path.join(film, "HIKAYE.json"))
    if not isinstance(h, dict): return {"sonuc": "HATA", "hatalar": ["HIKAYE.json yok ya da bozuk"]}, HATA
    seri = seri_normal(seri) or film_serisi(film, h)
    if not seri: return {"sonuc": "HATA", "hatalar": ["seri adı yok (HIKAYE.json evren, HAZIRLIK seri ya da 04_SECIM seri_adi)"]}, HATA
    film_ad = (_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}).get("film") or os.path.basename(film)
    kar, mek = _kimlikler(h)
    hatalar = [f"karakter kimliği geçersiz: {k!r}" for k in kar if not KIMLIK_DESEN.fullmatch(k)]
    hatalar += [f"mekân kimliği geçersiz: {m!r}" for m in mek if not KIMLIK_DESEN.fullmatch(m)]
    for kid, k in kar.items():
        var = _oku(seri_yolu(seri, "karakterler", kid, "karakter.json"))
        if isinstance(var, dict) and var.get("ad") and var["ad"] != k["ad"]:
            hatalar.append(f"karakter '{kid}' evrende '{var['ad']}' adıyla kayıtlı; bu film '{k['ad']}' diyor (kimlik çakışması)")
        if isinstance(var, dict) and var.get("durum") == "olu" and kid in {r.get("karakter") for r in h.get("replikler") or []}:
            hatalar.append(f"karakter '{kid}' evren kanonunda ölü ama bu filmde konuşuyor (kanon ihlali)")
    if hatalar: return {"sonuc": "HATA", "seri": seri, "hatalar": hatalar}, HATA
    degisen = []
    e = _oku(seri_yolu(seri, "evren.json")) or {"seri": seri, "surum": 0, "filmler": [], "kilit_durumu": "on_kayit", "on_kayit": {}}
    e = json.loads(json.dumps(e))
    kayit = {"karakterler": {k: {"ad": v["ad"], "kostumler": v["kostumler"]} for k, v in kar.items()}, "mekanlar": mek}
    onceki = (e.get("on_kayit") or {}).get(film_ad) or {}
    if {k: v for k, v in onceki.items() if k != "zaman"} != kayit:
        e.setdefault("on_kayit", {})[film_ad] = dict(kayit, zaman=simdi())
        if film_ad not in e["filmler"]: e["filmler"].append(film_ad)
        e["surum"] = int(e.get("surum") or 0) + 1
        e["_uretim"] = {"arac_surum": SURUM, "zaman": simdi()}
        if _surumlu_yaz(seri_yolu(seri, "evren.json"), e): degisen.append("evren.json")
    hp = seri_yolu(seri, "hikaye.json")
    hs = _oku(hp) or {"seri": seri, "surum": 0, "donem": None, "kurallar": [], "ne_yok_hikaye": [], "kanon": [], "seri_sorulari": [],
                      "baslik_gecmisi": [], "sozluk": {"adlar": {}, "guvenli_karsilik": {}}, "degisiklik_gunlugu": []}
    hs2 = json.loads(json.dumps(hs))
    if not hs2.get("donem") and h.get("donem"): hs2["donem"] = h["donem"]
    for n in h.get("ne_yok") or []:
        if n not in hs2["ne_yok_hikaye"]: hs2["ne_yok_hikaye"].append(n)
    adlar = hs2.setdefault("sozluk", {}).setdefault("adlar", {})
    for v in kar.values():
        if v["ad"] not in adlar: adlar[v["ad"]] = {"telaffuz": v["ad_telaffuz"], "tts_dogrulandi": False}
    if hs2 != hs:
        hs2["surum"] = int(hs.get("surum") or 0) + 1
        hs2.setdefault("degisiklik_gunlugu", []).append({"surum": hs2["surum"], "tarih": simdi()[:10], "film": film_ad, "ozet": "ön kayıt"})
        if _surumlu_yaz(hp, hs2): degisen.append("hikaye.json")
    for kid, v in kar.items():
        kp = seri_yolu(seri, "karakterler", kid, "karakter.json"); var = _oku(kp) or {}
        yeni = dict(var) if var else {"id": kid, "seri": seri, "tur": v["tur"], "surum": 0, "durum": "on_kayit", "gecmis": []}
        yeni["ad"] = v["ad"]
        yeni["kostum_kimlikleri"] = sorted(set(var.get("kostum_kimlikleri") or []) | set(v["kostumler"]))
        if v["varsayilan_kostum"] and not yeni.get("varsayilan_kostum"): yeni["varsayilan_kostum"] = v["varsayilan_kostum"]
        if yeni != var:
            if var: yeni["surum"] = int(var.get("surum") or 0)
            if _surumlu_yaz(kp, yeni): degisen.append(f"karakterler/{kid}/karakter.json")
        hk = seri_yolu(seri, "karakterler", kid, "hikaye.json")
        if not os.path.exists(hk):
            k = (h.get("karakterler") or {}).get(kid) or {}
            ortak.atomik_yaz(hk, {"id": kid, "durum": "yasiyor", "yay_gecmisi": [], "bildikleri": list(k.get("bildikleri_bas") or []),
                                  "konusma_tarzi": k.get("konusma_tarzi"), "maske": k.get("maske"), "ses_karakteri": k.get("ses_karakteri"),
                                  "hikaye_baglayici_gorunus": [g.get("oge") for g in k.get("gorsel_ayirt_edici") or []
                                                               if isinstance(g, dict) and g.get("hikaye_baglayici")],
                                  "ilk_film": film_ad})
            degisen.append(f"karakterler/{kid}/hikaye.json")
    for m in h.get("mekanlar") or []:
        if not isinstance(m, dict) or not m.get("id"): continue
        mp = seri_yolu(seri, "mekanlar", m["id"], "mekan.json")
        if not os.path.exists(mp):
            ortak.atomik_yaz(mp, {"id": m["id"], "seri": seri, "durum": "on_kayit", "hikaye_olgulari": m.get("hikaye_olgulari") or [],
                                  "isik_hikaye": m.get("isik_hikaye"), "ilk_film": film_ad})
            degisen.append(f"mekanlar/{m['id']}/mekan.json")
    return {"sonuc": "GEC", "seri": seri, "film": film_ad, "karakterler": sorted(kar), "mekanlar": mek, "degisen": degisen}, BITTI


# --- komut satırı ------------------------------------------------------------------------------------------------
# --- ses (A08/S1: ses_sec çağırır) --------------------------------------------------------------------------------
def ses_kaydet(film, karakter, kayit, seri=None):
    """Karakterin ses kaydını (voice_id, ayarlar, etiket …; anahtar yok) <evren>/<SERI>/karakterler/<id>/ses.json'a yazar.
    Sürümlü: içerik değişirse eski hâli ses_v<n>.json olarak kalır (silme yok) ve surum bir artar; aynı kayıt bir şey değiştirmez.
    Seri bulunamazsa ya da kimlik geçersizse ValueError (çağıran BAYRAK yazar). Dönüş: (yol, değişti_mi)."""
    seri = seri_normal(seri) or film_serisi(film)
    if not seri: raise ValueError("filmin evren serisi yok (HIKAYE.json evren / HAZIRLIK seri)")
    if not (isinstance(karakter, str) and KIMLIK_DESEN.fullmatch(karakter)): raise ValueError(f"karakter kimliği geçersiz: {karakter!r}")
    if not isinstance(kayit, dict): raise ValueError("ses kaydı sözlük olmalı")
    p = seri_yolu(seri, "karakterler", karakter, "ses.json"); eski = _oku(p) or {}
    govde = {k: v for k, v in kayit.items() if k not in ("surum", "zaman", "film", "id", "seri")}
    if {k: v for k, v in eski.items() if k not in ("surum", "zaman", "film", "id", "seri")} == govde: return p, False
    yeni = dict(govde, id=karakter, seri=seri, film=os.path.basename(os.path.normpath(film)), surum=int(eski.get("surum") or 0) + 1,
                zaman=simdi())
    return p, _surumlu_yaz(p, yeni)


def _arg(a, ad, v=None):
    return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def _film_yolu(f):
    if not f: return None
    if os.path.isdir(f): return os.path.abspath(f)
    return os.path.join(ortak.yollar()["filmler"], f)


def main(a):
    if not a or a[0] in ("-h", "--help"): print(__doc__); return BITTI
    try:
        if any(x in ("--kilitle", "--kilit-dogrula", "--surum-ac") for x in a):      # kart kilidi (PR-8): evren_kilit.py
            import evren_kilit
            return evren_kilit.ana(a)
        if any(x in FILM_SONU for x in a):
            import evren_film_sonu
            return evren_film_sonu.main(a)
        if a[0] in SONRAKI or any(x in SONRAKI for x in a if x.startswith("--")):
            print(f"!! {next(x for x in a if x in SONRAKI)} henüz yok (TASARIM §6.3; sonraki PR). İşlem yapılmadı."); return ORTAM
        jm = "--json" in a; film = _film_yolu(_arg(a, "--film")); seri = seri_normal(_arg(a, "--seri"))
        if "--on-kayit" in a or a[0] in ("on-kayit", "--on-kayit"):
            if not film: print("!! --film gerekli"); return HATA
            r, kod = on_kayit(film, seri)
            print(json.dumps(r, ensure_ascii=False, indent=None if jm else 1)); return kod
        if a[0] in ("ne_yok_kelimeleri", "ne-yok-kelimeleri", "--ne-yok"):
            k = ne_yok_kelimeleri(seri, film)
            print(json.dumps(k, ensure_ascii=False) if jm else ("\n".join(k) or "(NE YOK listesi boş)")); return BITTI
        if a[0] in ("ozet", "--ozet"):
            o = ozet(seri); print(json.dumps(o, ensure_ascii=False, indent=1) if jm else ozet_md(o), end="" if not jm else "\n")
            return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM
    print(__doc__); return HATA


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
