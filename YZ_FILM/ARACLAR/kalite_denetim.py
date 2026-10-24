"""KALİTE DENETİM — V1 teknik klip kapısı (--klip); final yayın denetimi kalite_denetim_final.py'de (--final) (TASARIM §6.5, §7.2 V1, D-31).

Kullanım:
  python kalite_denetim.py --klip [<plan,…>] [--blok B03] --film <film>
        her indirilen klipte: ffprobe (süre, boyut, fps, ses), blackdetect d=0.1 pic_th=0.98 pix_th=0.10, freezedetect n=-60dB d=1.0,
        blurdetect, sahne kesmesi (PySceneDetect ContentDetector(27); kurulu değilse ffmpeg scdet yedeği), titreme (kare parlaklığı MAE).
        → _RAPOR/V1_<blok|FILM>.json (kuyruk önerileri), KUNYE/NNN.json kapilar.V1 {sonuc, rapor, kirp}
  python kalite_denetim.py --final …      kalite_denetim_final.py'ye geçer (PR-13)
Kodda: import kalite_denetim; kalite_denetim.klip_denetle(film, [121, 122], blok="B03") (memmet.py blok sonunda çağırır) · klip_olc(yol)
Kurallar:
  - Süre < 7,5 sn → HATA "kesik_indirme" (yeni gönderim değil: memmet_topla ile yeniden indirme).
  - Kusur planın kullanılan penceresinin (kullanim{bas, sure}; yoksa bütün klip) DIŞINDAYSA: cozum "kirp", kuyruğa madde açılmaz (D-31).
  - İçindeyse: siyah / donma / istenmeyen kesme HATA (yeniden çekim önerisi), bulanıklık ve titreme BAYRAK.
  - ffmpeg yoksa ÖLÇÜLEMEDİ (= BAYRAK; asla GEÇ değil).
Eşikler (tahmin; ilk iki filmde ölçülür): v1_sure_min_sn 7,5 · v1_bulaniklik_max 8,0 · v1_titreme_mae_max 6,0 · v1_scdet_esik 10.
Çıkış kodları: 0 rapor yazıldı · 1 girdi yok · 4 kullanım.
"""
import os, sys, re, json, shutil, subprocess, tempfile, statistics
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kalite_denetim 1.0 (V1)"
VARSAYILAN = {"v1_sure_min_sn": 7.5, "v1_bulaniklik_max": 8.0, "v1_titreme_mae_max": 6.0, "v1_scdet_esik": 10.0, "v1_kesme_kenar_sn": 0.2}
KOK_TEKNIK = ("teknik_kusur", "kesme_ici")      # kok_neden.json'da "teknik_kusur" yoksa "kesme_ici" (paylaşılan istek)


class Olculemedi(Exception): pass


def esik(ad):
    try:
        import esikler; v = esikler.yukle().get(ad)
        return VARSAYILAN[ad] if v is None else v
    except Exception: return VARSAYILAN[ad]


def _ffmpeg():
    if not (shutil.which("ffmpeg") and shutil.which("ffprobe")): raise Olculemedi("ffmpeg/ffprobe yok (KUR1)")


def probe(yol):
    _ffmpeg()
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
                        "-of", "json", yol], capture_output=True, text=True)
    if r.returncode != 0: raise Olculemedi(f"ffprobe okuyamadı: {r.stderr.strip()[:120]}")
    d = json.loads(r.stdout or "{}"); v = next((s for s in d.get("streams") or [] if s.get("codec_type") == "video"), {})
    fr = str(v.get("r_frame_rate") or "0/1").split("/"); fps = float(fr[0]) / float(fr[1] or 1) if len(fr) == 2 and float(fr[1] or 0) else 0.0
    return {"sure": float((d.get("format") or {}).get("duration") or 0), "genislik": v.get("width"), "yukseklik": v.get("height"),
            "fps": round(fps, 3), "ses": any(s.get("codec_type") == "audio" for s in d.get("streams") or [])}


def _araliklar(metin, bas_k, bit_k, sure):
    bas = [float(x) for x in re.findall(bas_k + r"\s*:?\s*([0-9.]+)", metin)]
    bit = [float(x) for x in re.findall(bit_k + r"\s*:?\s*([0-9.]+)", metin)]
    return [(round(b, 3), round(bit[i] if i < len(bit) else sure, 3)) for i, b in enumerate(bas)]


def _sahne_kesmeleri(yol, kare_meta):
    try:
        from scenedetect import detect, ContentDetector          # PySceneDetect (BSD-3)
        sahneler = detect(yol, ContentDetector(threshold=27))
        return [round(s[0].get_seconds(), 3) for s in sahneler[1:]], "pyscenedetect"
    except ImportError:
        return [t for t, s in kare_meta.get("scd", []) if s >= esik("v1_scdet_esik")], "ffmpeg_scdet (yedek)"


def klip_olc(yol):
    """Klibin V1 ölçümleri (sözlük). ffmpeg yoksa Olculemedi."""
    pr = probe(yol); sure = pr["sure"]
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", yol, "-vf",
                        "blackdetect=d=0.1:pic_th=0.98:pix_th=0.10,freezedetect=n=-60dB:d=1.0", "-an", "-f", "null", "-"],
                       capture_output=True, text=True, errors="replace")
    siyah = _araliklar(r.stderr, "black_start", "black_end", sure)
    donma = _araliklar(r.stderr, r"lavfi\.freezedetect\.freeze_start", r"lavfi\.freezedetect\.freeze_end", sure)
    d = tempfile.mkdtemp(prefix="v1_"); meta = os.path.join(d, "m.txt")
    try:
        subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-loglevel", "error", "-i", yol, "-vf",
                        f"signalstats,blurdetect,scdet=threshold={esik('v1_scdet_esik')},metadata=mode=print:file={meta.replace(os.sep, '/')}",
                        "-an", "-f", "null", "-"], capture_output=True, text=True)
        km = {"yavg": [], "blur": [], "scd": []}; t = 0.0
        if os.path.exists(meta):
            for satir in open(meta, encoding="utf-8", errors="replace"):
                m = re.search(r"pts_time:([0-9.]+)", satir)
                if m: t = float(m.group(1)); continue
                if satir.startswith("lavfi.signalstats.YAVG="): km["yavg"].append(float(satir.split("=")[1]))
                elif satir.startswith("lavfi.blur="): km["blur"].append(float(satir.split("=")[1]))
                elif satir.startswith("lavfi.scd.score="): km["scd"].append((round(t, 3), float(satir.split("=")[1])))
    finally: shutil.rmtree(d, ignore_errors=True)
    kes, kaynak = _sahne_kesmeleri(yol, km)
    y = km["yavg"]; titreme = round(statistics.mean(abs(y[i] - y[i - 1]) for i in range(1, len(y))), 3) if len(y) > 1 else 0.0
    return dict(pr, siyah=siyah, donma=donma, kesmeler=kes, kesme_kaynagi=kaynak,
                bulaniklik=round(statistics.median(km["blur"]), 3) if km["blur"] else None, titreme_mae=titreme)


def pencere(p, sure):
    k = p.get("kullanim") or {}
    if isinstance(k.get("bas"), (int, float)) and isinstance(k.get("sure"), (int, float)): return float(k["bas"]), float(k["bas"]) + float(k["sure"])
    return 0.0, sure


def _kesisir(a, b, w): return a < w[1] and b > w[0]


def degerlendir(no, p, o):
    """(ölçümler, kirp listesi)."""
    out, kirp = [], []
    def m(madde, seviye, **k): out.append(dict({"madde": madde, "plan": no, "seviye": seviye}, **k))
    if o["sure"] < esik("v1_sure_min_sn"):
        m("kesik_indirme", "HATA", olcu=o["sure"], esik=esik("v1_sure_min_sn"), oneri="memmet_topla ile yeniden indir (yeni gönderim yok)")
    w = pencere(p, o["sure"]); kenar = esik("v1_kesme_kenar_sn")
    for ad, liste in (("siyah", o["siyah"]), ("donma", o["donma"])):
        for a, b in liste:
            if _kesisir(a, b, w): m(ad, "HATA", olcu=[a, b], pencere=list(w), kok_neden=None, cozum="yeniden_cek")
            else: kirp.append({"kusur": ad, "aralik": [a, b]}); m(ad, "GEC", olcu=[a, b], cozum="kirp", pencere=list(w))
    for t in o["kesmeler"]:
        if w[0] + kenar < t < w[1] - kenar: m("istenmeyen_kesme", "HATA", olcu=t, pencere=list(w), cozum="yeniden_cek", kaynak=o["kesme_kaynagi"])
        else: kirp.append({"kusur": "kesme", "an": t}); m("istenmeyen_kesme", "GEC", olcu=t, cozum="kirp")
    if o["bulaniklik"] is not None and o["bulaniklik"] > esik("v1_bulaniklik_max"):
        m("bulaniklik", "BAYRAK", olcu=o["bulaniklik"], esik=esik("v1_bulaniklik_max"))
    if o["titreme_mae"] > esik("v1_titreme_mae_max"): m("titreme", "BAYRAK", olcu=o["titreme_mae"], esik=esik("v1_titreme_mae_max"))
    if not out or all(x["seviye"] == "GEC" for x in out): m("teknik", "GEC", olcu={"sure": o["sure"], "boyut": [o["genislik"], o["yukseklik"]]})
    return out, kirp


def _kok():
    try:
        import kuyruk
        return next((k for k in KOK_TEKNIK if kuyruk.kok_neden_normal(k)), "kesme_ici")
    except Exception: return "kesme_ici"


def _kuyruk(olc):
    kn = _kok(); out = []
    for m in olc:
        if m["seviye"] != "HATA" or m.get("cozum") != "yeniden_cek": continue
        out.append({"plan": m["plan"], "tur": "video", "seviye": "HATA", "kok_neden": kn, "cozum": "yeniden_cek", "dilim": "goruntu",
                    "sifir_kredi": {"denendi": True, "gerekce": f"V1 {m['madde']} kullanılan pencerenin içinde (ölçüm); kırpma pencereyi bozar"},
                    "kanit": {"madde": m["madde"], "olcu": m.get("olcu")}})
    return out


def klip_denetle(film, nolar=None, blok=None, tur=1, gorev=None):
    """V1: indirilmiş klipler. Raporu döndürür ve KUNYE kapilar.V1'i yazar."""
    import kapi
    film = os.path.abspath(film); doc = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    pl = {int(p["no"]): p for p in doc.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
    if nolar is None:
        nolar = sorted(int(os.path.basename(x)[:3]) for x in __import__("glob").glob(os.path.join(film, "SIRALI_VIDEO", "[0-9][0-9][0-9].mp4")))
    olc, birim, kirp = [], [], {}
    for no in sorted(int(n) for n in nolar):
        yol = os.path.join(film, "SIRALI_VIDEO", f"{no:03d}.mp4")
        if not os.path.exists(yol): continue
        birim.append(no)
        try: o = klip_olc(yol)
        except Olculemedi as e: olc.append({"madde": "V1", "plan": no, "seviye": "OLCULEMEDI", "neden": str(e)}); continue
        x, k = degerlendir(no, pl.get(no) or {}, o); olc += x; kirp[no] = k
    asama = "A14a" if str(blok or "").startswith("KESIT") else "A14"
    yol, r = kapi.kaydet(os.path.join(film, "_RAPOR"), "V1", str(blok or "FILM"), olc, tur=tur, asama=asama, gorev=gorev,
                         arac_surum=SURUM, birimler=birim, kuyruk=_kuyruk(olc))
    rel = os.path.relpath(yol, film).replace(os.sep, "/")
    for no in birim:
        p = os.path.join(film, "KUNYE", f"{no:03d}.json"); kk = ortak.json_oku(p, None)
        if not isinstance(kk, dict): continue
        s = kapi.en_kotu([kapi.madde_sonucu(m["seviye"]) for m in olc if m.get("plan") == no] or ["GEC"])
        kk.setdefault("kapilar", {})["V1"] = {"sonuc": s, "rapor": rel, "kirp": kirp.get(no) or []}; ortak.atomik_yaz(p, kk)
    return r


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    if "--final" in argv:
        try: import kalite_denetim_final
        except ImportError: print("Final denetim (kalite_denetim_final.py) henüz yok (PR-13)."); return 4
        return kalite_denetim_final.main(argv)
    if "--klip" not in argv: print(__doc__); return 4
    film = argv[argv.index("--film") + 1] if "--film" in argv else None
    if not film or not os.path.isdir(film): print("film klasörü yok (--film)"); return 1
    blok = argv[argv.index("--blok") + 1] if "--blok" in argv else None
    i = argv.index("--klip"); nolar = None
    if i + 1 < len(argv) and re.fullmatch(r"[0-9][0-9,]*", argv[i + 1]): nolar = [int(x) for x in argv[i + 1].split(",") if x]
    elif blok:
        import blok_plani
        try: nolar = [int(n) for n in blok_plani.blok_bul(film, blok)[1].get("planlar") or []]
        except ValueError as e: print(e); return 1
    r = klip_denetle(film, nolar, blok=blok, gorev=os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None)
    print(f"V1: {r['sonuc']} · {r['ozet']}"); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
