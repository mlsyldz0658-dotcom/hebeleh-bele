"""KAPAK — kapak adaylarının kör paketi, HS_KAPAK kapısı ve seçimi (A11), yayın kapak dosyaları (A17) (TASARIM §1.3 A11/A17, §7.2 HS_KAPAK).

Kullanım (film.py calis çağırır):
  python kapak.py --sec --film <film> [--tur N]   A11: YAYIN/_KAPAK_ADAYLAR/kapak_NN.jpg + kare-tarifcisi·kapak (_RAPOR/KAPAK/gozlem_t<tur>.json)
        + habersiz-seyirci·kapak ikili karşılaştırmaları (_RAPOR/KAPAK/seyirci_t<tur>.json) + yerel okunurluk (168×94'te yüz bulunuyor mu)
        → _RAPOR/KAPAK_t<tur>.json (HS_KAPAK kapısı), YAYIN/KAPAK_SIRALAMA.json
  python kapak.py --film <film>                     A17: sıralamanın (ya da YAYIN/KAPAK_SECIM.json'un) ilk üç adayından YAYIN/kapak_<n>.jpg
        (1280×720, JPEG ≤ 2 MB; YouTube kapak boyutu)
  python kapak.py --kor-paketi --film <film> [--tur N]   kör paketi (kare_denetim --karar sonunda kendiliğinden çağrılır)
  Kodda: import kapak · kapak.kor_paketi(film, tur) · kapak.sec(film, tur) → (kod, rapor) · kapak.siralama(ciftler, adaylar) · kapak.final(film)
Kör paket: _KOR_PAKET/kapak_t<tur>/1/ (kare-tarifcisi·kapak: g01.jpg …, SORULAR.json) ve _KOR_PAKET/kapak_t<tur>/SEYIRCI/ (habersiz-seyirci·kapak:
  küçük boy önizlemeler 336×188 ve 168×94, CIFTLER.json; ad, istem, plan yok). ANAHTAR.json GIRDI'ye girmez.
Kapı (§7.2): aday sayısı ≥ kapak_aday_min (8) yoksa HATA; 168×94'te yüz seçilemiyor HATA (ölçülemezse ÖLÇÜLEMEDİ = BAYRAK); kör gözlemde
  yazı/logo ya da anatomi bozukluğu HATA; kimlik (kahramanın bankasına SFace < 0,363) HATA; insan + yaratık birlikte değil BAYRAK.
  Kazanan: HATA'sız adaylar arasında ikili karşılaştırma galibiyet oranı (eşitlikte kör gözlem bayrak sayısı, sonra aday no).
Çıkış kodları: 0 tamam (kapı sonucu raporda) · 1 program hatası · 2 aday yok · 4 kullanım.
"""
import os, sys, re, json, glob, shutil, itertools
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kapak 1.0"
SIRA = {"GEC": 0, "BAYRAK": 1, "HATA": 2}
SEYIRCI_SORU = ("Her satırdaki iki küçük resimden YouTube'da hangisine tıklardın? CIFTLER.json'daki her çift için CIKTI/rapor.json'a "
                "{\"ciftler\": [{\"a\": \"g01\", \"b\": \"g02\", \"secim\": \"a\" | \"b\", \"neden\": \"…\"}]} yaz.")


def _adaylar(kok): return sorted(glob.glob(os.path.join(kok, "YAYIN", "_KAPAK_ADAYLAR", "kapak_*.jpg")))


def kor_paketi(kok, tur=1):
    import kor
    from PIL import Image
    ad = _adaylar(kok)
    if not ad: return 2
    r = kor.paket_kur(kok, "kapak", tur, [{"anahtar": os.path.splitext(os.path.basename(p))[0], "gorsel": p, "baglam": {}} for p in ad], grup_sayisi=1)
    sd = os.path.join(r["klasor"], "SEYIRCI"); os.makedirs(sd, exist_ok=True)
    an = r["anahtar"]["gruplar"]["1"]
    for g, v in an.items():
        im = Image.open(os.path.join(kok, v["gorsel"])).convert("RGB")
        for (w, h), ek in (((336, 188), ""), ((168, 94), "_kucuk")):
            im.resize((w, h), Image.LANCZOS).save(os.path.join(sd, g.replace(".jpg", f"{ek}.jpg")), "JPEG", quality=90)
    gs = sorted(an)
    ciftler = [{"a": a[:-4], "b": b[:-4]} for a, b in itertools.combinations(gs, 2)]
    if len(ciftler) > 30:                                 # 12 adayda 66 çift: her aday ≈ 5 karşılaştırma alacak biçimde döngüsel seçim
        n = len(gs); sec_ = {tuple(sorted((i, (i + k) % n))) for k in (1, 2, 3) for i in range(n)}
        ciftler = [{"a": gs[a][:-4], "b": gs[b][:-4]} for a, b in sorted(sec_)]
    ortak.atomik_yaz(os.path.join(sd, "CIFTLER.json"), {"_surum": 1, "soru": SEYIRCI_SORU, "ciftler": ciftler})
    return 0


def siralama(ciftler, adaylar):
    """İkili seçimlerden galibiyet oranı: {g: oran}."""
    kaz = {a: 0 for a in adaylar}; mac = {a: 0 for a in adaylar}
    for c in ciftler or []:
        a, b, s = c.get("a"), c.get("b"), str(c.get("secim") or "").lower()
        if a not in kaz or b not in kaz or s not in ("a", "b", a, b): continue
        w = a if s in ("a", a) else b
        kaz[w] += 1; mac[a] += 1; mac[b] += 1
    return {a: (kaz[a] / mac[a] if mac[a] else None) for a in adaylar}


def okunurluk(yol, olcu=(168, 94)):
    """Küçük boyda yüz seçilebiliyor mu: görsel olcu'ya indirilip 4× büyütülür, YuNet yüz arar. (bool|None, neden)."""
    from PIL import Image
    from olcum import kimlik
    ok, neden = kimlik.hazir()
    if not ok: return None, neden
    im = Image.open(yol).convert("RGB").resize(tuple(olcu), Image.LANCZOS).resize((olcu[0] * 4, olcu[1] * 4), Image.BICUBIC)
    import numpy as np
    arr = np.asarray(im)[:, :, ::-1].copy()
    return bool(kimlik.yuzler(arr, vektor=False)), ""


def sec(kok, tur=1):
    import kor, olcum
    import plan_ortak as po
    ad = _adaylar(kok)
    if not ad: print("!! kapak adayı yok (YAYIN/_KAPAK_ADAYLAR)", flush=True); return 2, None
    an = (kor.anahtar_oku(kok, "kapak", tur).get("gruplar") or {}).get("1") or {}
    g_of = {v["anahtar"]: g[:-4] for g, v in an.items()}
    cev = kor.cevaplari_oku(os.path.join(kok, "_RAPOR", "KAPAK", f"gozlem_t{tur}.json"))
    sey = ortak.json_oku(os.path.join(kok, "_RAPOR", "KAPAK", f"seyirci_t{tur}.json"), {}) or {}
    oran = siralama(sey.get("ciftler"), sorted(g_of.values()))
    olc, adaylar_d = [], {}
    if len(ad) < int(olcum.esik("kapak_aday_min") or 8):
        olc.append(po.m("kapak_aday_sayisi", "HATA", None, olcu=len(ad), esik=olcum.esik("kapak_aday_min")))
    if not sey.get("ciftler"): olc.append(po.m("seyirci_ikili", "OLCULEMEDI", None, neden="habersiz-seyirci·kapak cevabı yok"))
    o = olcum.esik("kapak_kucuk_okunurluk") or [168, 94]
    for p in ad:
        k = os.path.splitext(os.path.basename(p))[0]; g = g_of.get(k); al = []
        try: okn, neden = okunurluk(p, o)
        except Exception as e: okn, neden = None, f"{e.__class__.__name__}"
        if okn is False: al.append(po.m("okunurluk", "HATA", None, birim=k, esik=f"{o[0]}x{o[1]}", neden="küçük boyda yüz seçilmiyor"))
        elif okn is None: al.append(po.m("okunurluk", "OLCULEMEDI", None, birim=k, neden=neden))
        c = cev.get(f"{g}.jpg") if g else None
        if c is None: al.append(po.m("kor_gozlem", "OLCULEMEDI", None, birim=k, neden="kare-tarifcisi·kapak cevabı yok"))
        else:
            ks = kor.karsilastir(an.get(f"{g}.jpg", {}).get("sorular") or {}, c)
            for r in ks:
                if r["alan"] in ("yazi_logo", "anatomi") and r["sonuc"] == "uyumsuz": al.append(po.m(r["alan"], "HATA", None, birim=k, kor=r["kor"]))
                elif r["alan"] in ("yazi_logo", "anatomi") and r["sonuc"] == "belirsiz": al.append(po.m(r["alan"], "BAYRAK", None, birim=k, kor=r["kor"]))
                elif r["alan"] == "kapak_kalip" and r["sonuc"] != "uyum": al.append(po.m("kapak_kalip", "BAYRAK", None, birim=k, kor=r["kor"]))
            if str(c.get("stil") or "photograph").lower().find("photo") < 0: al.append(po.m("stil", "BAYRAK", None, birim=k, kor=c.get("stil")))
        olc += al
        sev = max((SIRA["BAYRAK" if a["seviye"] == "OLCULEMEDI" else a["seviye"]] for a in al), default=0)
        adaylar_d[k] = {"gorsel": os.path.relpath(p, kok).replace(os.sep, "/"), "kor_ad": g, "karar": [s for s, v in SIRA.items() if v == sev][0],
                        "galibiyet_orani": oran.get(g) if g else None, "bayrak": sum(1 for a in al if a["seviye"] != "HATA")}
    sira = sorted(adaylar_d, key=lambda k: (adaylar_d[k]["karar"] == "HATA", -(adaylar_d[k]["galibiyet_orani"] or 0), adaylar_d[k]["bayrak"], k))
    kazanan = next((k for k in sira if adaylar_d[k]["karar"] != "HATA"), None)
    if kazanan is None: olc.append(po.m("kapak_kazanan", "HATA", None, neden="HATA'sız kapak adayı yok"))
    ortak.atomik_yaz(os.path.join(kok, "YAYIN", "KAPAK_SIRALAMA.json"), {"_surum": 1, "tur": tur, "kazanan": kazanan, "sira": sira, "adaylar": adaylar_d})
    yol, r = po.rapor_yaz(kok, "HS_KAPAK", "KAPAK", olc, asama="A11", arac=SURUM, tur=tur, birimler=sorted(adaylar_d),
                          varsayilan=f"_RAPOR/KAPAK_t{tur}.json", ek={"kazanan": kazanan, "sira": sira})
    po.yaz_ozet(r, "HS_KAPAK")
    return 0, r


def final(kok, adet=3):
    from PIL import Image
    s = ortak.json_oku(os.path.join(kok, "YAYIN", "KAPAK_SECIM.json"), {}) or {}
    sr = ortak.json_oku(os.path.join(kok, "YAYIN", "KAPAK_SIRALAMA.json"), {}) or {}
    secim = [x for x in (s.get("sira") or ([s["secim"]] if s.get("secim") else [])) if x] or \
        [k for k in sr.get("sira") or [] if (sr.get("adaylar") or {}).get(k, {}).get("karar") != "HATA"]
    if not secim: print("!! kapak sıralaması yok (önce A11 kapak.py --sec)", flush=True); return 2, []
    out = []
    for i, k in enumerate(secim[:adet], 1):
        p = os.path.join(kok, "YAYIN", "_KAPAK_ADAYLAR", f"{k}.jpg")
        if not os.path.isfile(p): continue
        im = Image.open(p).convert("RGB"); W, H = im.size
        hedef_oran = 16 / 9
        if W / float(H) > hedef_oran: nw = int(H * hedef_oran); im = im.crop(((W - nw) // 2, 0, (W - nw) // 2 + nw, H))
        elif W / float(H) < hedef_oran: nh = int(W / hedef_oran); im = im.crop((0, (H - nh) // 2, W, (H - nh) // 2 + nh))
        im = im.resize((1280, 720), Image.LANCZOS)
        hedef = os.path.join(kok, "YAYIN", f"kapak_{i}.jpg")
        if os.path.isfile(hedef):
            d = os.path.join(kok, "_ESKI", "YAYIN"); os.makedirs(d, exist_ok=True); n = 1
            while os.path.exists(os.path.join(d, f"kapak_{i}_v{n}.jpg")): n += 1
            shutil.move(hedef, os.path.join(d, f"kapak_{i}_v{n}.jpg"))
        for q in (95, 90, 85, 80, 70):
            im.save(hedef + ".tmp", "JPEG", quality=q, optimize=True)
            if os.path.getsize(hedef + ".tmp") <= 2 * 1024 * 1024: break
        os.replace(hedef + ".tmp", hedef); out.append(os.path.relpath(hedef, kok).replace(os.sep, "/"))
    ortak.atomik_yaz(os.path.join(kok, "YAYIN", "KAPAK_DOSYALARI.json"), {"_surum": 1, "dosyalar": out, "kaynak": secim[:adet]})
    print("kapak dosyaları:", ", ".join(out), flush=True)
    return 0, out


def main(argv):
    if argv and argv[0] in ("-h", "--help"): print(__doc__); return 4
    import plan_ortak as po
    kok = po.film_kok(po.arg_al(argv, "--film")); tur = po.tur_no(argv)
    try:
        if "--kor-paketi" in argv: return kor_paketi(kok, tur)
        if "--sec" in argv: return sec(kok, tur)[0]
        return final(kok)[0]
    except ortak.YolYok as e: print("!!", e); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
