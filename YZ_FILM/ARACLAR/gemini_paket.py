"""GEMİNİ PAKET — Gemini uygulamasına (ajan) kullanıcının taşıyacağı toplu görsel/kart/kapak paketleri (TASARIM §6.5, D-16, D-19; [GS2] GS3, GS7).

Kullanım (film.py calis çağırır):
  python gemini_paket.py --kartlar --film <film>                     _KARTLAR/KART_ISTEMLERI.json → kart paketi (kart başına 3 aday)
  python gemini_paket.py --basamak <k> --aday <n> --film <film>      SAHNELER.json → basamak ≥ k, G1'i GEÇMEMİŞ ve ebeveyni hazır planlar
        (ebeveyni G1 GEÇ ya da aynı pakette önce üretilen); plan başına n aday (D-16: 2); basamak 1'de kapak adayları da pakete girer
  python gemini_paket.py --kapak --film <film>                       yalnız kapak adayları (YAYIN/KAPAK_SPEC.json)
  python gemini_paket.py --ikinci-goz --parti <n> --film <film>      görsel "ikinci göz" YALNIZ API ile (gemini_api açıksa); kullanıcıya
        paket verilmez (D-19, İ-6) → _RAPOR/IKINCI_GOZ_P<n>.json (bulgular yalnız BAYRAK; anahtar yoksa ÖLÇÜLEMEDİ)
  Seçenek: --yeniden (adayı olan planları da pakete al) · --plan-max N (varsayılan gemini_paket_plan_max = 30)
Çıktı: <gemini_paket>/<FILM>_<KART|GORSEL_B<k>|KAPAK>_<tur>_<NN>/ {GOREV.txt, ISTEMLER.txt, REFERANSLAR/ ya da REFERANSLAR.zip (> 10 ek),
  PAKET.json}; film kopyası <film>/GELENLER/_PAKETLER/<paket>.json (gemini_al eşlemesi için). <gemini_paket> = ortak.yollar()["gemini_paket"]
  (Masaüstü\\GEMINI GORSEL ISTEM). Gemini'den dönen ZIP'in adı GOREV.txt'de yazılıdır (<paket>.zip) → kullanıcı <film>/GELENLER/'e koyar.
Kurallar: içe alma bu aracın işi değildir (gemini_al → yalnız _ADAYLAR/); düzeltme görselleri kullanıcıya paket olarak GİTMEZ (D-16,
  İ-13; gorsel_duzeltme zinciri); 16:9 1376×768 istenir (kartlar dikey/yatay serbest, uzun kenar ≥ 1376); referans istemdeki sırayla.
Çıkış kodları: 0 tamam (paket yazıldı ya da paketlenecek iş yok) · 1 girdi HATA'sı · 2 girdi yok · 4 kullanım/ortam.
"""
import os, sys, re, json, shutil, zipfile, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "gemini_paket 1.0"
GOREV_METNI = """TASK FOR THE GEMINI IMAGE AGENT
Create every image listed in ISTEMLER.txt, one image per block, in the order given.
Rules:
- Use exactly the FILE NAME written in each block.
- Use the listed REFERENCE IMAGES (in REFERANSLAR) for identity, costume and location. A reference may also be an image you created
  earlier in this batch (its FILE NAME is given); create that one first.
- {bicim}
- Photorealistic film stills. No text, no letters, no logos, no watermarks, no borders, no collage unless the block asks for a sheet.
- When two blocks share a prompt (a and b), make two genuinely different takes (pose detail, framing) of the same description.
- Return ALL images in ONE ZIP file named exactly: {zip_adi}
"""


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def paket_kok():
    k = ortak.yollar().get("gemini_paket")
    if not k: raise ortak.YolYok("YOLLAR.json'da gemini_paket yolu yok (python kurulum.py --yollar)")
    return k


def _film_ad(kok): return (ortak.json_oku(os.path.join(kok, "HAZIRLIK.json"), {}) or {}).get("film") or os.path.basename(kok)


def _sira_no(kok, on_ek):
    d = paket_kok(); n = 1
    while os.path.exists(os.path.join(d, f"{on_ek}_{n:02d}")) or os.path.exists(os.path.join(kok, "GELENLER", "_PAKETLER", f"{on_ek}_{n:02d}.json")): n += 1
    return n


def _ref_dosya(ref, kok, ev, ayni_paket):
    """Referans kimliği → (dosya yolu ya da None, pakette görünecek ad)."""
    import kare_denetim as kd
    if ref.startswith("kart:"):
        kid, rest = ref.split(":", 1)[1].split("/", 1) if "/" in ref else (ref.split(":", 1)[1].split("@")[0], "")
        kost = rest.split("@")[0] or None
        return ev.kart_yolu(kid.split("@")[0], kost), None
    if ref.startswith("plaka:"):
        mid, pid = (ref.split(":", 1)[1].split("@")[0].split("/") + [""])[:2]
        return ev.plaka_yolu(mid, pid), None
    if ref.startswith("plan:"):
        no = int(float(ref.split(":", 1)[1].split("@")[0]))
        if no in ayni_paket: return None, ayni_paket[no]
        p = os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % no)
        return (p if os.path.isfile(p) else None), None
    return None, None


def _ebeveyn_plan(plan, P):
    """Planın görsel ebeveyni olan plan numarası (ana_kare/turev → aynı kurulumun ana kare planı; son_kare → önceki plan)."""
    z = plan.get("zanaat") or {}; zn = z.get("zincir") or {}; bas = zn.get("baslangic") or "ana_kare"
    if bas == "son_kare": return zn.get("onceki_plan")
    if bas in ("kart", "ana_kare") and not str(zn.get("ebeveyn") or "").startswith(("KAM", "ana_kare")): return None
    kur = str(zn.get("ebeveyn") or (z.get("kamera") or {}).get("kurulum") or "").split("@")[0].replace("ana_kare:", "")
    if not kur or kur.startswith("plaka:"): return None
    for q in sorted(P.values(), key=lambda p: float(p.get("sira", p.get("no", 0)) or 0)):
        qz = q.get("zanaat") or {}
        if q.get("no") != plan.get("no") and qz.get("sahne_grubu") == z.get("sahne_grubu") and (qz.get("kamera") or {}).get("kurulum") == kur \
                and ((qz.get("zincir") or {}).get("baslangic") in ("ana_kare", "kart")):
            return q.get("no")
    return None


def _yaz_paket(kok, on_ek, tur_adi, bloklar, refler, tur_no, bicim, beklenen):
    import olcum
    n = _sira_no(kok, on_ek); ad = f"{on_ek}_{n:02d}"
    d = os.path.join(paket_kok(), ad); os.makedirs(d, exist_ok=True)
    zip_adi = f"{ad}.zip"
    with open(os.path.join(d, "GOREV.txt"), "w", encoding="utf-8") as f: f.write(GOREV_METNI.format(bicim=bicim, zip_adi=zip_adi))
    with open(os.path.join(d, "ISTEMLER.txt"), "w", encoding="utf-8") as f:
        for b in bloklar:
            f.write(f"=== {b['blok']} ===\nFILE NAME: {b['dosya']}\nREFERENCE IMAGES: {', '.join(b['referans']) or 'none'}\nPROMPT: {b['istem']}\n\n")
    rd = os.path.join(d, "REFERANSLAR"); os.makedirs(rd, exist_ok=True)
    for ad_r, yol in refler.items(): shutil.copyfile(yol, os.path.join(rd, ad_r))
    if len(refler) > int(olcum.esik("gemini_ek_dosya_max") or 10):
        with zipfile.ZipFile(os.path.join(d, "REFERANSLAR.zip"), "w", zipfile.ZIP_DEFLATED) as z:
            for ad_r in sorted(refler): z.write(os.path.join(rd, ad_r), ad_r)
        eski = os.path.join(d, "_REFERANSLAR_KLASOR")
        shutil.move(rd, eski)                         # silinmez; kullanıcıya yalnız ZIP verilir
    man = {"_surum": 1, "paket": ad, "tur": tur_adi, "film_tur": tur_no, "zip_adi": zip_adi, "klasor": d, "olusturma": simdi(),
           "arac_surum": SURUM, "beklenen": beklenen, "referans_sayisi": len(refler), "referanslar_zip": len(refler) > int(olcum.esik("gemini_ek_dosya_max") or 10)}
    ortak.atomik_yaz(os.path.join(d, "PAKET.json"), man)
    ortak.atomik_yaz(os.path.join(kok, "GELENLER", "_PAKETLER", f"{ad}.json"), man)
    return man


def paket_kart(kok, tur_no=1):
    ki = ortak.json_oku(os.path.join(kok, "_KARTLAR", "KART_ISTEMLERI.json"))
    if not isinstance(ki, dict): print("!! _KARTLAR/KART_ISTEMLERI.json yok (önce istem_derle --kart)", flush=True); return 2, []
    bl, bek = [], {}
    for k in ki.get("kartlar") or []:
        for a, dosya in zip(k.get("adaylar") or [], k.get("dosyalar") or []):
            bl.append({"blok": dosya[:-4], "dosya": dosya, "referans": [], "istem": k["istem"]})
            bek[dosya] = {"tur": "kart", "kart_id": k["kart_id"], "aday": a}
    if not bl: print("paketlenecek kart yok (hepsi kilitli)", flush=True); return 0, []
    on = f"{_film_ad(kok)}_KART_t{tur_no}"
    m = _yaz_paket(kok, on, "kart", bl, {}, tur_no, "Character sheets: a wide 16:9 sheet, long edge at least 1376 px.", bek)
    print(f"kart paketi: {m['klasor']} ({len(bl)} görsel)", flush=True)
    return 0, [m]


def _kapak_bloklari(kok, ev):
    ks = ortak.json_oku(os.path.join(kok, "YAYIN", "KAPAK_SPEC.json"), {}) or {}
    var = os.path.join(kok, "YAYIN", "_KAPAK_ADAYLAR")
    bl, refs, bek = [], {}, {}
    for k in ks.get("adaylar") or []:
        if os.path.isfile(os.path.join(var, k["dosya"])): continue
        rr = []
        for r in k.get("referanslar") or []:
            yol = ev.kart_yolu(r.split(":", 1)[1].split("/")[0].split("@")[0])
            if yol and os.path.isfile(yol):
                ad = f"R_{os.path.basename(yol)}"; refs[ad] = yol; rr.append(ad)
        bl.append({"blok": k["no"], "dosya": k["dosya"], "referans": rr, "istem": k["istem"]})
        bek[k["dosya"]] = {"tur": "kapak", "kapak": k["no"]}
    return bl, refs, bek


def paket_gorsel(kok, basamak=1, aday=2, tur_no=1, yeniden=False, plan_max=None, kapak=True):
    import olcum, istem_derle_gorsel as idg, kare_denetim as kd
    S = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(S, dict): print("!! SAHNELER.json yok", flush=True); return 2, []
    P = {p.get("no"): p for p in S.get("sahneler") or []}
    ev = idg.Evren(kok); A = kd.adaylar(kok)
    plan_max = plan_max or int(olcum.esik("gemini_paket_plan_max") or 30)
    harfler = [chr(ord("a") + i) for i in range(aday)]
    adaylar_p = []
    for p in sorted(P.values(), key=lambda p: float(p.get("sira", p.get("no", 0)) or 0)):
        if not p.get("gorsel_istem"): continue
        if ((p.get("denetim") or {}).get("G1") or {}).get("sonuc") == "GEC": continue
        if int(((p.get("uretim") or {}).get("gorsel") or {}).get("basamak") or idg.basamak(p)) < basamak: continue
        if not yeniden and len(A.get(p["no"]) or []) >= aday: continue
        adaylar_p.append(p)
    secili, ertelenen = {}, []
    for p in adaylar_p:
        eb = _ebeveyn_plan(p, P)
        hazir = eb is None or kd.video_hazir(kok, eb)[0] or ((P.get(eb) or {}).get("denetim") or {}).get("G1", {}).get("sonuc") == "GEC" \
            or eb in secili
        if hazir: secili[p["no"]] = p
        else: ertelenen.append({"plan": p["no"], "ebeveyn": eb, "neden": "ebeveyn G1'den geçmedi ve bu pakette değil"})
    nolar = list(secili)
    paketler = []
    on = f"{_film_ad(kok)}_GORSEL_B{basamak}_t{tur_no}"
    for i in range(0, max(len(nolar), 1 if kapak else 0), plan_max):
        parca = nolar[i:i + plan_max]
        bl, refs, bek, ayni = [], {}, {}, {}
        for no in parca:
            p = secili[no]
            for h in harfler: ayni.setdefault(no, f"%03d_{harfler[0]}.jpg" % no)
            rr = []
            for r in ((p.get("uretim") or {}).get("gorsel") or {}).get("referanslar") or []:
                yol, ic = _ref_dosya(r, kok, ev, {k: v for k, v in ayni.items() if k != no})
                if ic: rr.append(ic); continue
                if yol and os.path.isfile(yol):
                    ad = "R_" + re.sub(r"[^A-Za-z0-9_.-]", "_", r.replace(":", "_").replace("/", "_").split("@")[0]) + os.path.splitext(yol)[1].lower()
                    refs[ad] = yol; rr.append(ad)
            eb = _ebeveyn_plan(p, P)
            if eb in ayni and ayni[eb] not in rr and eb != no: rr.append(ayni[eb])
            for h in harfler:
                dosya = "%03d_%s.jpg" % (no, h)
                bl.append({"blok": dosya[:-4], "dosya": dosya, "referans": rr, "istem": p["gorsel_istem"]
                           + ("" if h == harfler[0] else f" (take {h}: a different take of the same moment)")})
                bek[dosya] = {"tur": "gorsel", "plan": no, "aday": h, "istem_ozeti": ((p.get("_derlenir") or {}).get("gorsel_istem_ozeti"))}
        if kapak and basamak == 1 and i == 0:
            kb, kr, kbek = _kapak_bloklari(kok, ev); bl += kb; refs.update(kr); bek.update(kbek)
        if not bl: continue
        paketler.append(_yaz_paket(kok, on, "gorsel", bl, refs, tur_no,
                                   "Every image is 16:9 landscape, 1376x768 pixels (never portrait, never square).", bek))
    if ertelenen:
        ortak.atomik_yaz(os.path.join(kok, "_RAPOR", "G1", f"PAKET_ERTELENEN_B{basamak}_t{tur_no}.json"), {"ertelenen": ertelenen})
    print(f"görsel paketleri: {len(paketler)} · plan {len(nolar)} · ertelenen {len(ertelenen)}", flush=True)
    for m in paketler: print("  ", m["klasor"], flush=True)
    return 0, paketler


def ikinci_goz(kok, parti, tur_no=1):
    """Parti sonu görsel ikinci göz: YALNIZ gemini_api açıksa; değilse ÖLÇÜLEMEDİ (BAYRAK) + açıklama. Kullanıcı paketi yok."""
    import plan_ortak as po
    from saglayicilar import gemini_api as ga
    acik, neden = ga.izin_karari("gozlemci")
    S = ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
    karel = [p for p in S.get("sahneler") or [] if str(p.get("parti")) == str(parti)
             and os.path.isfile(os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % p.get("no", 0)))]
    olc = []
    if not acik:
        olc.append(po.m("ikinci_goz", "OLCULEMEDI", None, neden=neden))
    else:
        try:
            s = ga.GeminiAPI()
            sonuc = s.gozlem([os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % p["no"]) for p in karel][:30],
                             "These are consecutive film frames. List continuity errors (object changed hands, costume change, extra person, "
                             "lighting jump) as JSON: {\"bulgular\": [{\"kare\": <index from 1>, \"tur\": \"...\", \"aciklama\": \"...\"}]}")
            for b in (sonuc.get("bulgular") or []):
                i = int(b.get("kare") or 0) - 1
                olc.append(po.m("ikinci_goz", "BAYRAK", karel[i]["no"] if 0 <= i < len(karel) else None, olcu=b.get("tur"),
                                neden=b.get("aciklama"), kaynak="gemini_api"))
        except Exception as e:
            olc.append(po.m("ikinci_goz", "OLCULEMEDI", None, neden=f"{e.__class__.__name__}: {str(e)[:160]}"))
    yol, r = po.rapor_yaz(kok, "K1ON", f"IKINCI_GOZ_P{parti}", olc, asama="A11", arac=SURUM, varsayilan=f"_RAPOR/IKINCI_GOZ_P{parti}.json",
                          birimler=[p["no"] for p in karel])
    return 0, r


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 4
    import plan_ortak as po
    kok = po.film_kok(po.arg_al(argv, "--film")); tur = po.tur_no(argv)
    try:
        if "--kartlar" in argv: return paket_kart(kok, tur)[0]
        if "--ikinci-goz" in argv: return ikinci_goz(kok, po.arg_al(argv, "--parti", "1"), tur)[0]
        if "--kapak" in argv:
            import istem_derle_gorsel as idg
            bl, refs, bek = _kapak_bloklari(kok, idg.Evren(kok))
            if not bl: print("paketlenecek kapak yok"); return 0
            m = _yaz_paket(kok, f"{_film_ad(kok)}_KAPAK_t{tur}", "kapak", bl, refs, tur, "Every image is 16:9 landscape, 1376x768 pixels.", bek)
            print(m["klasor"]); return 0
        if "--basamak" in argv:
            pm = po.arg_al(argv, "--plan-max")
            return paket_gorsel(kok, int(po.arg_al(argv, "--basamak", "1")), int(po.arg_al(argv, "--aday", "2")), tur,
                                yeniden="--yeniden" in argv, plan_max=int(pm) if pm else None)[0]
    except ortak.YolYok as e: print("!!", e); return 4
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
