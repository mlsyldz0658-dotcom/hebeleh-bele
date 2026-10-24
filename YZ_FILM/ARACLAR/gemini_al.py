"""GEMİNİ AL — Gemini'den dönen ZIP'i güvenle açar, görselleri YALNIZ aday klasörlerine alır (TASARIM §6.5, D-16; [GS2] GS3, GS7).

Kullanım (film.py calis çağırır):
  python gemini_al.py --film <film> [--zip <yol|klasör>]                  görsel + kapak adayları: GELENLER/*GORSEL*.zip, *KAPAK*.zip
  python gemini_al.py --kartlar --film <film> [--zip <yol|klasör>]        kart adayları: GELENLER/*KART*.zip → kart kör paketi hazırlanır
  python gemini_al.py --sahte-uret [--kartlar] --film <film>              TEST/simülasyon: ZIP yerine paket manifestlerinden sahte adaylar
        üretir (yan dosyada "gercek" ölçüm değerleri; SAHTE_HATA=ayna,fazla_kisi,ters_el,yazi,cizim,kimlik hata enjeksiyonu)
Nereye: görsel → SIRALI_GORSEL/_ADAYLAR/NNN_<aday>.jpg (+ .json yan dosya) — SIRALI_GORSEL/NNN.jpg'e ASLA yazılmaz (Memmet orada jpg görünce
  görsel üretmez; seçimi G1 yapar) · kapak → YAYIN/_KAPAK_ADAYLAR/kapak_NN.jpg · kart → _KARTLAR/adaylar/<kart_id>_<aday>.jpg.
Denetim: ZIP yalnız resim uzantıları (.jpg .jpeg .png .webp) ve dosya adının kendisiyle açılır (klasör yolu, '..' yok sayılır; zip-slip yok);
  dosya başına ≤ 40 MB. Görsel/kapak 16:9 ±%1; sapma ≤ %20 ise ortadan 16:9 kırpılır (kirpildi: true), değilse ya da kısa kenar < 720 →
  _ADAYLAR/_REDDEDILEN/. Kart uzun kenarı ≥ 1376. Beklenmeyen ad → _ADAYLAR/_ESLESMEYEN/. Var olan aday _ESKI/'ye taşınır (silinmez).
  İşlenen ZIP GELENLER/_ISLENDI/'ye taşınır. Rapor _RAPOR/GEMINI_AL_<tur>_t<n>.json (alınan, reddedilen, eksik, eşleşmeyen).
Çıkış kodları: 0 tamam (eksik varsa raporda BAYRAK) · 1 hiçbir şey alınamadı / ZIP bozuk · 2 ZIP yok (kullanıcı işi) · 4 kullanım.
"""
import os, sys, re, io, json, glob, shutil, zipfile, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "gemini_al 1.0"
UZANTI = (".jpg", ".jpeg", ".png", ".webp")
MAX_BAYT = 40 * 1024 * 1024
HEDEF = 16 / 9


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def manifestler(kok, tur):
    out = []
    for p in sorted(glob.glob(os.path.join(kok, "GELENLER", "_PAKETLER", "*.json"))):
        m = ortak.json_oku(p, {}) or {}
        if (tur == "kart") == (m.get("tur") == "kart"): out.append(m)
    return out


def _beklenen(kok, tur):
    b = {}
    for m in manifestler(kok, tur):
        for dosya, v in (m.get("beklenen") or {}).items(): b[dosya.lower()] = dict(v, paket=m.get("paket"), dosya=dosya)
    return b


def _esle(ad, bek):
    k = os.path.basename(ad).lower(); kok_ad = os.path.splitext(k)[0]
    if k in bek: return bek[k]
    for dosya, v in bek.items():
        if os.path.splitext(dosya)[0] == kok_ad: return v
    m = re.match(r"^(\d{3,})[ _-]*([a-z])\b", kok_ad)
    if m:
        d = "%03d_%s.jpg" % (int(m.group(1)), m.group(2))
        if d in bek: return bek[d]
    m = re.match(r"^(kapak[_ -]?\d+)", kok_ad)
    if m:
        d = re.sub(r"[ -]", "_", m.group(1))
        d = "kapak_%02d.jpg" % int(re.sub(r"\D", "", d))
        if d in bek: return bek[d]
    return None


def _hedef(kok, v):
    if v["tur"] == "kart": return os.path.join(kok, "_KARTLAR", "adaylar", v["dosya"])
    if v["tur"] == "kapak": return os.path.join(kok, "YAYIN", "_KAPAK_ADAYLAR", v["dosya"])
    return os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", v["dosya"])


def _eskiye(kok, yol):
    d = os.path.join(kok, "_ESKI", os.path.relpath(os.path.dirname(yol), kok)); os.makedirs(d, exist_ok=True)
    k, u = os.path.splitext(os.path.basename(yol)); n = 1
    while os.path.exists(os.path.join(d, f"{k}_v{n}{u}")): n += 1
    shutil.move(yol, os.path.join(d, f"{k}_v{n}{u}"))
    yan = os.path.splitext(yol)[0] + ".json"
    if os.path.isfile(yan): shutil.move(yan, os.path.join(d, f"{k}_v{n}.json"))


def isle(kok, ad, veri, v, rap):
    """Tek görsel: denetim + (gerekirse) 16:9 kırpma + hedefe atomik yazım."""
    from PIL import Image
    import olcum
    try:
        im = Image.open(io.BytesIO(veri)); im.load(); im = im.convert("RGB")
    except Exception as e:
        rap["reddedilen"].append({"dosya": ad, "neden": f"görsel açılamadı ({e.__class__.__name__})"}); return
    W, H = im.size; kirp = False
    if v["tur"] == "kart":
        if max(W, H) < int(olcum.esik("kart_uzun_kenar_min") or 1376):
            return _red(kok, ad, im, rap, f"kart uzun kenarı {max(W, H)} < 1376")
    else:
        sap = abs(W / float(H) - HEDEF) / HEDEF
        if sap > float(olcum.esik("g1_en_boy_tolerans") or 0.01):
            if sap > 0.20: return _red(kok, ad, im, rap, f"en-boy {W}x{H}: 16:9'dan %{round(sap * 100)} sapma (kırpılamaz)")
            if W / float(H) > HEDEF: nw = int(round(H * HEDEF)); x0 = (W - nw) // 2; im = im.crop((x0, 0, x0 + nw, H))
            else: nh = int(round(W / HEDEF)); y0 = (H - nh) // 2; im = im.crop((0, y0, W, y0 + nh))
            kirp = True; W, H = im.size
        if min(W, H) < int(olcum.esik("g1_kisa_kenar_min") or 720):
            return _red(kok, ad, im, rap, f"kısa kenar {min(W, H)} < 720")
    hedef = _hedef(kok, v); os.makedirs(os.path.dirname(hedef), exist_ok=True)
    if os.path.isfile(hedef): _eskiye(kok, hedef)
    tmp = hedef + ".tmp.jpg"; im.save(tmp, "JPEG", quality=95); os.replace(tmp, hedef)
    yan = {"saglayici": v.get("saglayici", "gemini_paket"), "paket": v.get("paket"), "kaynak_dosya": ad, "tarih": simdi(),
           "kirpildi": kirp, "boyut": [W, H], "istem_ozeti": v.get("istem_ozeti"), "tur": v["tur"]}
    for k in ("plan", "aday", "kart_id", "kapak"):
        if v.get(k) is not None: yan[k] = v[k]
    if v.get("gercek") is not None: yan["gercek"] = v["gercek"]
    ortak.atomik_yaz(os.path.splitext(hedef)[0] + ".json", yan)
    rap["alinan"].append({"dosya": ad, "hedef": os.path.relpath(hedef, kok).replace(os.sep, "/"), "kirpildi": kirp})


def _red(kok, ad, im, rap, neden):
    d = os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "_REDDEDILEN"); os.makedirs(d, exist_ok=True)
    im.save(os.path.join(d, re.sub(r"[^A-Za-z0-9_.-]", "_", os.path.splitext(os.path.basename(ad))[0]) + ".jpg"), "JPEG", quality=90)
    rap["reddedilen"].append({"dosya": ad, "neden": neden})


def _kaynaklar(kok, tur, zip_yol=None):
    if zip_yol: return [zip_yol]
    desen = ["*KART*.zip"] if tur == "kart" else ["*GORSEL*.zip", "*KAPAK*.zip"]
    out = []
    for d in desen: out += glob.glob(os.path.join(kok, "GELENLER", d))
    return sorted(set(out))


def _dosyalari_oku(kaynak):
    """[(ad, bayt)] — klasör ya da ZIP; yalnız resim, yalnız dosya adı (zip-slip yok)."""
    out = []
    if os.path.isdir(kaynak):
        for kok_, _, ds in os.walk(kaynak):
            for d in ds:
                if d.lower().endswith(UZANTI) and os.path.getsize(os.path.join(kok_, d)) <= MAX_BAYT:
                    with open(os.path.join(kok_, d), "rb") as f: out.append((d, f.read()))
        return out
    with zipfile.ZipFile(kaynak) as z:
        for zi in z.infolist():
            ad = os.path.basename(zi.filename.replace("\\", "/"))
            if zi.is_dir() or not ad or not ad.lower().endswith(UZANTI) or zi.file_size > MAX_BAYT: continue
            if ad.startswith(("._", "__MACOSX")): continue
            out.append((ad, z.read(zi)))
    return out


def al(kok, tur="gorsel", zip_yol=None, tur_no=1):
    bek = _beklenen(kok, tur)
    kaynaklar = _kaynaklar(kok, tur, zip_yol)
    if not kaynaklar:
        print("Gemini ZIP'i henüz GELENLER'de yok.", flush=True); return 2, None
    rap = {"_surum": 1, "zaman": simdi(), "arac_surum": SURUM, "tur": tur, "kaynaklar": [], "alinan": [], "reddedilen": [], "eslesmeyen": [], "eksik": []}
    for k in kaynaklar:
        try: dosyalar = _dosyalari_oku(k)
        except (zipfile.BadZipFile, OSError) as e:
            rap["reddedilen"].append({"dosya": os.path.basename(k), "neden": f"ZIP bozuk ({e.__class__.__name__})"}); continue
        rap["kaynaklar"].append(os.path.basename(k))
        for ad, veri in dosyalar:
            v = _esle(ad, bek)
            if v is None:
                d = os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "_ESLESMEYEN"); os.makedirs(d, exist_ok=True)
                with open(os.path.join(d, re.sub(r"[^A-Za-z0-9_.-]", "_", ad)), "wb") as f: f.write(veri)
                rap["eslesmeyen"].append(ad); continue
            isle(kok, ad, veri, v, rap)
        if not zip_yol and os.path.isfile(k):
            hd = os.path.join(kok, "GELENLER", "_ISLENDI"); os.makedirs(hd, exist_ok=True)
            hedef = os.path.join(hd, os.path.basename(k)); n = 1
            while os.path.exists(hedef): hedef = os.path.join(hd, f"{os.path.splitext(os.path.basename(k))[0]}_{n}.zip"); n += 1
            shutil.move(k, hedef)
    alinan = {os.path.basename(a["hedef"]).lower() for a in rap["alinan"]}
    for dosya, v in bek.items():
        if not os.path.isfile(_hedef(kok, v)) and dosya not in alinan: rap["eksik"].append(v["dosya"])
    ortak.atomik_yaz(os.path.join(kok, "_RAPOR", f"GEMINI_AL_{tur.upper()}_t{tur_no}.json"), rap)
    print(f"Gemini içe alma ({tur}): alınan {len(rap['alinan'])} · reddedilen {len(rap['reddedilen'])} · eşleşmeyen "
          f"{len(rap['eslesmeyen'])} · eksik {len(rap['eksik'])}", flush=True)
    if tur == "kart" and rap["alinan"]:
        import kart_denetim
        kart_denetim.kor_gorev(kok, tur_no)
    return (0 if rap["alinan"] else 1), rap


# --- sahte üretim (test ve simülasyon) -----------------------------------------------------------------------
def sahte_gercek(kok, no, hata=()):
    """Planın beklenen değerlerinden 'gerçek' ölçüm (sahte arka uç bunu döndürür); hata enjeksiyonu."""
    import kare_denetim as kd, istem_derle_gorsel as idg
    S = ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
    P = {p.get("no"): p for p in S.get("sahneler") or []}; b = kd.beklenen(kok, P[no], S, idg.Evren(kok))
    sira = list(b["kadraj_sirasi"]) or list(b["gorunur_yuz"])
    g = {"yuz_sayisi": len(b["gorunur_yuz"]), "kimlik": {k: {"benzerlik": 0.62, "fark_payi": 0.2} for k in b["gorunur_yuz"]},
         "kadraj_sirasi": sira, "ucte_bir": {k: b["kadraj_konumu"].get(k) or "orta" for k in b["gorunur_yuz"]},
         "yaw": {}, "yaw_guven": "yuksek", "jaw_open": {k: 0.03 for k in b["agiz_kapali"]}, "stil_clip_foto": 0.93,
         "el_nesne": {n: {"el": el, "guven": 0.8} for kid, e in b["eller"].items() for el, n in e.items() if n},
         "yaratik_dinov2": {y: 0.7 for y in b["yaratik_ids"]}, "kor_hata": []}
    if b.get("ebeveyn"): g["mekan_dinov2"] = 0.75
    for h in hata:
        if h == "ayna": g["kadraj_sirasi"] = list(reversed(sira))
        elif h == "fazla_kisi": g["yuz_sayisi"] += 1; g["kor_hata"].append("fazla_kisi")
        elif h == "ters_el": g["kor_hata"].append("ters_el")
        elif h == "ters_el_iki":
            g["kor_hata"].append("ters_el"); g["el_nesne"] = {n: {"el": "sol" if v["el"] == "sag" else "sag", "guven": 0.8} for n, v in g["el_nesne"].items()}
        elif h == "kimlik_bayrak": g["kimlik"] = {k: {"benzerlik": 0.40, "fark_payi": 0.1} for k in g["kimlik"]}
        elif h == "kimlik": g["kimlik"] = {k: {"benzerlik": 0.2, "fark_payi": -0.1} for k in g["kimlik"]}
        elif h == "yazi": g["kor_hata"].append("yazi")
        elif h == "cizim": g["stil_clip_foto"] = 0.2; g["kor_hata"].append("cizim")
        elif h == "olculemedi":
            g = {"olculemedi": {"yuz_sayisi": "model yok", "kimlik": "model yok", "kadraj_sirasi": "model yok"}, "kor_hata": []}
    return g


def sahte_uret(kok, tur="gorsel", hata_plan=None):
    """Manifestlerdeki her beklenen dosyayı sahte görselle üretir (ağ yok). hata_plan {no: ["ayna", …]} ya da SAHTE_HATA ortam değişkeni
    ("ayna" bütün planlara; "071:ayna,ters_el;072:fazla_kisi" plan başına)."""
    from PIL import Image, ImageDraw
    bek = _beklenen(kok, tur)
    if not bek: print("!! paket manifesti yok (önce gemini_paket)", flush=True); return 2, None
    hp = dict(hata_plan or {})
    env = os.environ.get("SAHTE_HATA", "")
    for parca in [p for p in env.split(";") if p]:
        if ":" in parca: n, hs = parca.split(":", 1); hp[int(n)] = [h for h in hs.split(",") if h]
        else: hp["*"] = [h for h in parca.split(",") if h]
    rap = {"_surum": 1, "zaman": simdi(), "arac_surum": SURUM + " sahte", "tur": tur, "kaynaklar": ["sahte"], "alinan": [], "reddedilen": [],
           "eslesmeyen": [], "eksik": []}
    for dosya, v in sorted(bek.items()):
        W, H = (1376, 768)
        no = v.get("plan") or 0
        renk = ((no * 67) % 200 + 30, (no * 131) % 200 + 30, (no * 29) % 200 + 30)
        im = Image.new("RGB", (W, H), renk); d = ImageDraw.Draw(im)
        if v["tur"] != "kart":
            for i in range(0, W, 40): d.line([(i, 0), (i, H)], fill=(255 - renk[0], 200, 120), width=2)
        else: im = Image.new("RGB", (W, H), (200, 200, 200)); d = ImageDraw.Draw(im); d.rectangle([500, 150, 876, 700], fill=(90, 70, 60))
        d.text((40, 40), f"SAHTE {v['dosya']}", fill=(255, 255, 255))
        if v["tur"] == "gorsel":
            hs = hp.get(no) or hp.get(str(no)) or hp.get("*") or []
            if "aday" in v and isinstance(hs, dict): hs = hs.get(v["aday"], [])
            v = dict(v, gercek=sahte_gercek(kok, no, hs), saglayici="sahte")
        elif v["tur"] == "kart":
            kid = str(v.get("kart_id") or "")
            g = {"yuz_sayisi": 6, "oz_tutarlilik_min": 0.61, "stil_clip_foto": 0.92, "kadro_benzerlik": {}} if kid.startswith("karakter_") \
                else ({"yuz_sayisi": 0, "stil_clip_foto": 0.9} if kid.startswith("mekan_") else {"stil_clip_foto": 0.9})
            hs = hp.get(kid) or hp.get("*") or []
            if "kimlik" in hs: g["oz_tutarlilik_min"] = 0.2
            for h in hs:
                if h.startswith("benzer="): o, sim = h.split("=", 1)[1].split("@"); g["kadro_benzerlik"][o] = float(sim)
            if "kisi" in hs: g["yuz_sayisi"] = 1
            if "gorunen_yok" in hs: g["plaka_gorunen_yerel"] = {o: None for o in (v.get("gorunen_idler") or [])}
            g["kor_hata"] = [h for h in hs if h in ("yazi", "cizim", "eksik_oge", "gorunen_yok", "fazla_kisi")]
            v = dict(v, gercek=g, saglayici="sahte")
        else: v = dict(v, saglayici="sahte")
        b = io.BytesIO(); im.save(b, "JPEG", quality=90)
        isle(kok, dosya, b.getvalue(), v, rap)
    ortak.atomik_yaz(os.path.join(kok, "_RAPOR", f"GEMINI_AL_{tur.upper()}_sahte.json"), rap)
    if tur == "kart":
        import kart_denetim
        kart_denetim.kor_gorev(kok, 1)
    return 0, rap


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 4
    import plan_ortak as po
    kok = po.film_kok(po.arg_al(argv, "--film")); tur_no = po.tur_no(argv)
    tur = "kart" if "--kartlar" in argv else "gorsel"
    try:
        if "--sahte-uret" in argv: return sahte_uret(kok, tur)[0]
        return al(kok, tur, po.arg_al(argv, "--zip"), tur_no)[0]
    except ortak.YolYok as e: print("!!", e); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
