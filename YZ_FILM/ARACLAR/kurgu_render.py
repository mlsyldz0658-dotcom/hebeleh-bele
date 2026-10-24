"""KURGU RENDER — görüntü montajı: animatik ve izle-dinle bilgi paketi (TASARIM §6.7, A12, D-24; [KU2] KR2, §4.6.2).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"):
  python kurgu_render.py --animatik [--tur N] [--boyut 1280x720] --film <film>
      KURGU/surumler/KURGU_PLANI_T1_v<N>.json → ANIMATIK/animatik_v<N>.mp4 (+ ANIMATIK/ISITSEL_DOKUM.md, _RAPOR/RENDER_ANIMATIK_v<N>.json)
  python kurgu_render.py --bilgi-paketi [--kip animatik|kesit] --film <film>
      BILGI_PAKETI/<kip>/: video, işitsel döküm, ses kadrosu örnekleri, ana tema, (dinleyici yoksa) motor örnekleri, OKU_BENI.txt;
      bildirim.py "bilgi_paketi" olayı (Telegram/masaüstü). Hat beklemez (D-24).
  python kurgu_render.py --onizleme [--tur N] [--boyut 1280x720] --film <film>       A16
      son KURGU_PLANI_T2 + KURGU/SES_CIZELGESI.json stemleri (son_miks.onizle) → KURGU/onizleme_v<N>.mp4, _RAPOR/RENDER_ONIZLEME_v<N>.json
  python kurgu_render.py --kesit [--tur N] [--boyut 1920x1080] --film <film>          A14a
      BLOK_PLANI.json kesit planları (T2 girdisi varsa o) → KESIT/KURGU_PLANI_KESIT_v<N>.json + KESIT/kesit_v<N>.mp4
      (ses: KURGU/SES_CIZELGESI_KESIT.json, yoksa SES_CIZELGESI.json), _RAPOR/RENDER_KESIT_v<N>.json
  python kurgu_render.py --yayin [--boyut 1920x1080] --film <film>   yayin_kaynagi: master → YAYIN/<film>_master.mp4 (AAC 320k),
      _RAPOR/RENDER_YAYIN.json (S8 ölçümü son_miks --olc ile ayrıca)
  T2 render: plan başına kare sayısı çizelge konumlarından (toplam = çizelge sonu); video planı kullanim penceresinden (bas, hiz, ayna,
  kadraj_kirpma), videosuz plan durağan görsel ya da yer tutucu (+ BAYRAK video_yok), karartmalar siyah; kartlar üstte; plan önbelleği.
  --otio: P2 → 4.
Animatik ([KU2] KR2):
  - Her plan kendi `sure`'si kadar (kare sayısı tamsayı; toplam = T1 toplamı) ekranda kalır. Durağan kareye hareket: ileri %8 yakınlaşma,
    geri %8 uzaklaşma, pan %2–4 kayma, sabit %2 "nefes" (RE ken_burns_zoom, ken_burns_kayma).
  - Bitiş görseli olan planda son RE animatik_bitis_gecis_sn (0,5 sn) çapraz geçişle bitiş görseline geçilir.
  - Eylem şeridi kadrajın altında, adımın saniyesinde, italik; yalnız görünür eylem, adsız (T1'den). Kartlar PIL ile şeffaf PNG.
  - Görseli eksik plan yer tutucuyla (gri kare + plan numarası + şerit). Plan başına önbellek: KURGU/_onbellek/seg_<özet>.mp4.
  - Ses: son_miks --animatik çıktısı (ANIMATIK/ses_miks_v<N>.wav, yoksa ANIMATIK/ses_*.wav'ın en yenisi) mux edilir; render miks
    yapmaz. Ses yoksa sessiz iz + BAYRAK (ses_yok).
  - Kapı: süre = T1 toplamı ± RE render_sure_tolerans_kare (HATA → çıkış 1). Yer tutucu oranı rapora yazılır (kapıyı seyirci_topla
    ve animatik_imza uygular: tur 1'de ≤ RE animatik_tur1_yer_tutucu_max_oran izletilir, kapı yalnız bütün kareler G1 GEÇ iken açılır).
Çıkış kodları: 0 BİTTİ · 1 HATA (girdi yok, süre tutmadı, ffmpeg) · 4 ORTAM (kip yok, ffmpeg yok).
"""
import os, sys, re, json, glob, shutil, hashlib, subprocess, argparse, tempfile
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import zaman_cizelgesi_t1 as t1

SURUM = "kurgu_render 1.0"
SEG_SURUM = "seg3"
FPS = t1.FPS


class RenderHatasi(Exception):
    pass


def ffmpeg_var(): return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def kos(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise RenderHatasi("ffmpeg: " + (r.stderr or "").strip()[-400:])
    return r


def kare_say(yol):
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets", "-show_entries", "stream=nb_read_packets",
                        "-of", "csv=p=0", yol], capture_output=True, text=True)
    try: return int(r.stdout.strip().split(",")[0])
    except ValueError: return None


def sure_ol(yol):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", yol], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return None


# --- çizimler (PIL) ------------------------------------------------------------------------------------------------
def _font(boy, italik=False):
    import kor_paket_izleme as kpi
    return kpi._font(boy, italik)


def metin_png(yol, w, h, metin, konum="alt", italik=True, kutu=True):
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    f = _font(max(10, h // 24), italik)
    satirlar = _sar(metin, f, int(w * 0.9), d)
    lh = int(max(12, h // 24) * 1.35); top_h = lh * len(satirlar)
    y = h - top_h - h // 20 if konum == "alt" else (h - top_h) // 2 if konum == "orta" else h // 12
    if kutu: d.rectangle([int(w * 0.04), y - 6, int(w * 0.96), y + top_h + 6], fill=(0, 0, 0, 150))
    for s in satirlar:
        tw = d.textlength(s, font=f)
        d.text(((w - tw) / 2, y), s, fill=(255, 255, 255, 255), font=f); y += lh
    im.save(yol)


def _sar(metin, f, gen, d):
    kel = str(metin or "").split(); out, cur = [], ""
    for k in kel:
        aday = (cur + " " + k).strip()
        if d.textlength(aday, font=f) <= gen or not cur: cur = aday
        else: out.append(cur); cur = k
    if cur: out.append(cur)
    return out[:3] or [""]


def yer_tutucu_png(yol, w, h, no, serit=""):
    import kor_paket_izleme as kpi
    kpi.yer_tutucu_gorsel(no, w, h, None).save(yol)


def kart_png(yol, w, h, metin):
    from PIL import Image
    yazi = yol + ".yazi.png"
    metin_png(yazi, w, h, metin, konum="orta", italik=False, kutu=False)
    a = Image.new("RGBA", (w, h), (0, 0, 0, 255)); a.alpha_composite(Image.open(yazi)); a.convert("RGB").save(yol)


# --- segment -----------------------------------------------------------------------------------------------------
def hareket_filtresi(hk, n, w, h):
    z = float(t1.E("ken_burns_zoom") or 0.08); k = float(t1.E("ken_burns_kayma") or 0.02)
    if hk == "ileri": zf = "1+%.4f*on/%d" % (z, max(1, n - 1)); xf, yf = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif hk == "geri": zf = "%.4f-%.4f*on/%d" % (1 + z, z, max(1, n - 1)); xf, yf = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif hk == "pan": zf = "%.4f" % (1 + 2 * k); xf, yf = "(iw-iw/zoom)*on/%d" % max(1, n - 1), "ih/2-(ih/zoom/2)"
    else: zf = "1+0.02*on/%d" % max(1, n - 1); xf, yf = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    return "scale=%d:%d,zoompan=z='%s':x='%s':y='%s':d=%d:s=%dx%d:fps=%d" % (w * 2, h * 2, zf, xf, yf, n, w, h, FPS)


def segment_anahtari(film, p, w, h, kartlar):
    g = p.get("goruntu") or {}
    oz = {"v": SEG_SURUM, "w": w, "h": h, "kare": p["kare"], "tur": g.get("tur"), "hk": g.get("hareket"), "metin": g.get("metin"),
          "dosya": t1.sha(os.path.join(film, g["dosya"])) if g.get("dosya") else None,
          "bitis": t1.sha(os.path.join(film, g["bitis_dosya"])) if g.get("bitis_dosya") else None,
          "serit": p.get("serit"), "kart": kartlar, "plan": p.get("plan") if g.get("tur") == "yer_tutucu" else None,
          "ayna": g.get("ayna"), "kadraj": g.get("kadraj_kirpma"), "gecis": t1.E("animatik_bitis_gecis_sn"),
          "kb": [t1.E("ken_burns_zoom"), t1.E("ken_burns_kayma")]}
    return hashlib.sha1(json.dumps(oz, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]


def segment_yap(film, p, w, h, kartlar, cikti, gecici):
    g = p.get("goruntu") or {}; n = int(p["kare"]); tur = g.get("tur")
    os.makedirs(gecici, exist_ok=True)
    girdi = os.path.join(gecici, "ana.png")
    if tur == "gorsel" and g.get("dosya") and os.path.isfile(os.path.join(film, g["dosya"])):
        from PIL import Image
        im = Image.open(os.path.join(film, g["dosya"])).convert("RGB").resize((w, h))
        if g.get("ayna"): im = im.transpose(Image.FLIP_LEFT_RIGHT)
        im.save(girdi)
    elif tur == "kart": kart_png(girdi, w, h, g.get("metin") or "")
    elif tur == "siyah":
        from PIL import Image
        Image.new("RGB", (w, h), (0, 0, 0)).save(girdi)
    else: yer_tutucu_png(girdi, w, h, p.get("plan"))
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", girdi]
    hk = "sabit_kart" if tur in ("kart", "siyah") else g.get("hareket") or "nefes"
    ana = ("scale=%d:%d,loop=loop=%d:size=1:start=0,setpts=N/%d/TB,fps=%d" % (w, h, n - 1, FPS, FPS)) if hk == "sabit_kart" \
        else hareket_filtresi(hk, n, w, h)
    fc = ["[0:v]%s,format=yuv420p,trim=end_frame=%d,setpts=PTS-STARTPTS[v0]" % (ana, n)]
    son = "v0"; idx = 1
    gecis = float(t1.E("animatik_bitis_gecis_sn") or 0.5)
    gk = min(int(round(gecis * FPS)), max(1, n // 2))
    if g.get("bitis_dosya") and os.path.isfile(os.path.join(film, g["bitis_dosya"])) and n > gk + 1:
        from PIL import Image
        b = os.path.join(gecici, "bitis.png"); Image.open(os.path.join(film, g["bitis_dosya"])).convert("RGB").resize((w, h)).save(b)
        cmd += ["-i", b]
        fc.append("[1:v]scale=%d:%d,loop=loop=%d:size=1:start=0,setpts=N/%d/TB,fps=%d,format=yuv420p,trim=end_frame=%d,setpts=PTS-STARTPTS[b]"
                  % (w, h, gk - 1, FPS, FPS, gk))
        # ffmpeg 7.0 setpts'tan sonra kare hızını 1/0 (bilinmiyor) bırakır; xfade sabit kare hızı ister → iki girişe de fps.
        fc.append("[%s]fps=%d[xa];[b]fps=%d[xb];[xa][xb]xfade=transition=fade:duration=%.4f:offset=%.4f[v1]"
                  % (son, FPS, FPS, gk / FPS, (n - gk) / FPS))
        son = "v1"; idx = 2
    katman = []
    for j, s in enumerate(p.get("serit") or []):
        y = os.path.join(gecici, "serit_%d.png" % j); metin_png(y, w, h, s["metin"]); katman.append((y, s["bas"], s["bit"]))
    for j, k in enumerate(kartlar):
        y = os.path.join(gecici, "kart_%d.png" % j); metin_png(y, w, h, k["metin"], konum="ust", italik=False)
        katman.append((y, k["bas"], k["bit"]))
    for j, (y, a, bt) in enumerate(katman):
        cmd += ["-i", y]
        fc.append("[%s][%d:v]overlay=0:0:enable='between(t,%.4f,%.4f)'[o%d]" % (son, idx, a, bt, j)); son = "o%d" % j; idx += 1
    cmd += ["-filter_complex", ";".join(fc), "-map", "[%s]" % son, "-frames:v", str(n), "-r", str(FPS), "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", "-pix_fmt", "yuv420p", "-video_track_timescale", "%d" % (FPS * 512),
            cikti + ".tmp.mp4"]
    kos(cmd)
    os.replace(cikti + ".tmp.mp4", cikti)


def plan_kartlari(plan, p):
    """Bu plana düşen üst üste kartlar (plan içi saniyeyle)."""
    out = []
    a0, a1 = float(p["cizelge_bas"]), float(p["cizelge_bas"]) + float(p["sure"])
    for k in plan.get("kartlar") or []:
        if not k.get("ust_uste", True) or k.get("cizelge_bas") is None: continue
        b0 = float(k["cizelge_bas"]); b1 = b0 + float(k.get("sure") or 3.0)
        if b1 <= a0 or b0 >= a1: continue
        out.append({"metin": k.get("metin") or "", "bas": round(max(0.0, b0 - a0), 4), "bit": round(min(a1, b1) - a0, 4)})
    return out


def _alt_modul(ad):
    """Alt aracı yükler; alt araç içe aktarılırken stdout'u yeniden yapılandırıyorsa (StringIO altında) gerçek stdout'la yükler."""
    import importlib
    if ad in sys.modules: return sys.modules[ad]
    o = sys.stdout
    try:
        if not hasattr(o, "reconfigure"): sys.stdout = sys.__stdout__
        return importlib.import_module(ad)
    finally: sys.stdout = o


def miks_al(film, cizelgeler, cikti, kip, tur, asama):
    """Ses: tek miks kodu son_miks.onizle (B15; render kendisi karıştırmaz). cizelgeler: denenecek SES_CIZELGESI yolları (film köküne göre).
    → (wav|None, kaynak açıklaması). Çizelge yoksa ya da stemsizse var olan miks dosyası (cikti) kullanılır."""
    for c in cizelgeler:
        if not os.path.isfile(os.path.join(film, c)): continue
        try:
            sm = _alt_modul("son_miks")
            os.makedirs(os.path.dirname(cikti), exist_ok=True)
            yol, _, _ = sm.onizle(film, c, cikti, kip, tur=tur, asama=asama)
            return yol, "son_miks.onizle(%s)" % c
        except FileNotFoundError:
            continue
    return (cikti, "var olan miks") if os.path.isfile(cikti) else (None, None)


def ses_bul(film, tur):
    for ad in ("ses_miks_v%d.wav" % tur, "ses_v%d.wav" % tur, "ses_miks.wav"):
        p = os.path.join(film, "ANIMATIK", ad)
        if os.path.isfile(p): return p
    ss = sorted(glob.glob(os.path.join(film, "ANIMATIK", "ses_*.wav")), key=os.path.getmtime)
    return ss[-1] if ss else None


def animatik(film, tur=1, boyut=(1280, 720), gorev=None):
    film = os.path.abspath(film)
    if not ffmpeg_var(): raise OrtamHatasi("ffmpeg/ffprobe yok (KUR1).")
    plan, pyol, n = t1.plan_oku(film, "T1", tur)
    if plan is None: raise RenderHatasi("KURGU_PLANI_T1_v%d.json yok (önce zaman_cizelgesi --asama animatik)." % tur)
    t1.yeniden_zamanla(plan)
    w, h = boyut; onb = os.path.join(film, "KURGU", "_onbellek"); os.makedirs(onb, exist_ok=True)
    gd = tempfile.mkdtemp(prefix="yz_render_")          # işlem içi ara dosyalar (PNG katmanları, liste); üretim verisi değildir
    liste, isabet, yeni = [], 0, 0
    try:
        for p in plan.get("planlar") or []:
            kartlar = plan_kartlari(plan, p)
            seg = os.path.join(onb, "seg_%s.mp4" % segment_anahtari(film, p, w, h, kartlar))
            if os.path.isfile(seg) and kare_say(seg) == p["kare"]: isabet += 1
            else: segment_yap(film, p, w, h, kartlar, seg, os.path.join(gd, "p%s" % p["plan"])); yeni += 1
            liste.append(seg)
        lst = os.path.join(gd, "liste.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for s in liste: f.write("file '%s'\n" % s.replace("\\", "/").replace("'", "'\\''"))
        os.makedirs(os.path.join(film, "ANIMATIK"), exist_ok=True)
        video = os.path.join(gd, "video.mp4")
        kos(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
        toplam = plan["toplam_kare"]; sure = toplam / FPS
        ses = ses_bul(film, n)
        if not ses:                                    # son_miks --animatik koşmamışsa aynı işlevle (son_miks.onizle) burada
            ses, _ = miks_al(film, ["KURGU/SES_CIZELGESI_T1.json"], os.path.join(film, "ANIMATIK", "ses_animatik_v%d.wav" % n),
                             "ANIMATIK", n, "A12")
        hedef = os.path.join(film, "ANIMATIK", "animatik_v%d.mp4" % n)
        if ses:
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", video, "-i", ses, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                   "-af", "apad", "-t", "%.4f" % sure, "-c:a", "aac", "-b:a", "160k", hedef + ".tmp.mp4"]
        else:
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", video, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a",
                   "-c:v", "copy", "-t", "%.4f" % sure, "-c:a", "aac", "-b:a", "96k", hedef + ".tmp.mp4"]
        kos(cmd); os.replace(hedef + ".tmp.mp4", hedef)
    finally:
        shutil.rmtree(gd, ignore_errors=True)
    olc = kare_say(hedef); tol = int(t1.E("render_sure_tolerans_kare") or 1)
    fark = None if olc is None else abs(olc - toplam)
    import kor_paket_izleme as kpi
    dokum = kpi.isitsel_dokum_yaz(film, plan, "animatik")
    o = t1.olcumler(plan)
    hatalar, bayraklar = [], []
    if fark is None or fark > tol: hatalar.append({"madde": "render_sure", "olcu": olc, "beklenen": toplam, "esik": tol})
    if not ses: bayraklar.append({"madde": "ses_yok", "neden": "son_miks --animatik çıktısı yok (ANIMATIK/ses_miks_v%d.wav); sessiz iz" % n})
    esik_yt = t1.E("animatik_tur1_yer_tutucu_max_oran" if n == 1 else "animatik_yer_tutucu_max_oran") or 0.10
    if o["yer_tutucu_orani"] > esik_yt:
        bayraklar.append({"madde": "yer_tutucu_fazla", "olcu": o["yer_tutucu_orani"], "esik": esik_yt,
                          "neden": "izletilmez; görsel aşamasına dönülür (kapıyı seyirci_topla uygular)"})
    elif o["yer_tutucu_planlar"]:
        bayraklar.append({"madde": "yer_tutucu", "olcu": o["yer_tutucu_orani"], "planlar": o["yer_tutucu_planlar"][:50]})
    sonuc = "HATA" if hatalar else ("BAYRAK" if bayraklar else "GEC")
    rapor = {"_surum": 1, "_uretim": {"asama": "A12", "gorev": gorev, "girdi_imza": t1.sha(pyol), "arac_surum": SURUM,
                                      "esik_surum": t1._esik_surum(), "sonuc": sonuc, "zaman": t1.simdi(), "ortam": t1.ortam()},
             "dosya": os.path.relpath(hedef, film).replace("\\", "/"), "kurgu_plani": os.path.relpath(pyol, film).replace("\\", "/"),
             "kurgu_plani_imza": t1.sha(pyol), "video_imza": t1.sha(hedef), "boyut": [w, h], "fps": FPS,
             "kare_beklenen": toplam, "kare_olculen": olc, "fark_kare": fark, "tolerans_kare": tol, "sure_sn": round(toplam / FPS, 4),
             "yer_tutucu_orani": o["yer_tutucu_orani"], "yer_tutucu_planlar": o["yer_tutucu_planlar"], "g1_tamam": o["g1_tamam"],
             "ses": {"kaynak": os.path.relpath(ses, film).replace("\\", "/") if ses else None, "durum": "miks" if ses else "sessiz"},
             "isitsel_dokum": os.path.relpath(dokum, film).replace("\\", "/"),
             "onbellek": {"isabet": isabet, "yeni": yeni}, "sonuc": sonuc, "hatalar": hatalar, "bayraklar": bayraklar}
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", "RENDER_ANIMATIK_v%d.json" % n), rapor)
    return rapor


class OrtamHatasi(Exception):
    pass


# --- T2 render: önizleme (A16), dikey kesit (A14a), yayın master'ı (yayin_kaynagi: master) ------------------------------
# kip → (klasör, video adı, ses çizelgeleri (sırayla), son_miks kipi, miks çıktısı, aşama, rapor adı)
T2_KIP = {"onizleme": ("KURGU", "onizleme_v{n}.mp4", ("KURGU/SES_CIZELGESI.json",), "ONIZLEME", "KURGU/ses_onizleme_v{n}.wav", "A16",
                       "RENDER_ONIZLEME_v{n}.json"),
          "kesit": ("KESIT", "kesit_v{n}.mp4", ("KURGU/SES_CIZELGESI_KESIT.json", "KURGU/SES_CIZELGESI.json"), "KESIT",
                    "KESIT/ses_kesit_v{n}.wav", "A14a", "RENDER_KESIT_v{n}.json"),
          "yayin": ("YAYIN", "{film}_master.mp4", ("KURGU/SES_CIZELGESI.json",), "FINAL", "YAYIN/ses_master.wav", "A17",
                    "RENDER_YAYIN.json")}
T2_BOYUT = {"onizleme": (1280, 720), "kesit": (1920, 1080), "yayin": (1920, 1080)}


def _k(t): return int(round(float(t) * FPS))


def t2_kareleri(plan):
    """Planların kare sayıları çizelge konumlarından (toplam = çizelge sonu, birikmiş yuvarlama yok) ve araya giren karartmalar.
    → [(plan_girdisi, kare, karartma_kare)]"""
    ps = sorted([x for x in plan.get("planlar") or [] if isinstance(x, dict)], key=lambda x: float(x.get("cizelge_bas") or 0))
    out = []
    for i, x in enumerate(ps):
        bas = _k(x["cizelge_bas"]); son = _k(float(x["cizelge_bas"]) + float(x["sure"]))
        sonraki = _k(ps[i + 1]["cizelge_bas"]) if i + 1 < len(ps) else son
        out.append((x, max(1, son - bas), max(0, sonraki - son)))
    return out


def video_segment(film, x, n, w, h, kartlar, cikti, gecici):
    """Video plan: klibin kullanim penceresi (bas, hiz, ayna, kadraj_kirpma) n kare; klip kısaysa son kare tutulur."""
    g = x.get("goruntu") or {}; ku = g.get("kullanim") or {}; hiz = float(g.get("hiz") or 1.0)
    os.makedirs(gecici, exist_ok=True)
    zf = float(g.get("kadraj_kirpma") or 1.0)
    vf = "setpts=(PTS-STARTPTS)/%.6f,fps=%d,scale=%d:%d:force_original_aspect_ratio=decrease,pad=%d:%d:(ow-iw)/2:(oh-ih)/2,setsar=1" \
         % (hiz, FPS, w, h, w, h)
    if zf > 1.0001: vf += ",scale=%d:%d,crop=%d:%d" % (int(round(w * zf / 2)) * 2, int(round(h * zf / 2)) * 2, w, h)
    if g.get("ayna"): vf += ",hflip"
    vf += ",tpad=stop_mode=clone:stop_duration=%.3f,format=yuv420p,trim=end_frame=%d,setpts=PTS-STARTPTS" % (n / FPS + 1.0, n)
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "%.4f" % float(ku.get("bas") or 0), "-i", os.path.join(film, g["dosya"])]
    fc = ["[0:v]%s[v0]" % vf]; son = "v0"
    for j, k in enumerate(kartlar):
        y = os.path.join(gecici, "kart_%d.png" % j); metin_png(y, w, h, k["metin"], konum="ust", italik=False)
        cmd += ["-i", y]
        fc.append("[%s][%d:v]overlay=0:0:enable='between(t,%.4f,%.4f)'[o%d]" % (son, j + 1, k["bas"], k["bit"], j)); son = "o%d" % j
    cmd += ["-filter_complex", ";".join(fc), "-map", "[%s]" % son, "-frames:v", str(n), "-r", str(FPS), "-an",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p", "-video_track_timescale", "%d" % (FPS * 512),
            cikti + ".tmp.mp4"]
    kos(cmd)
    os.replace(cikti + ".tmp.mp4", cikti)


def _t2_girdi(film, x, n):
    """T2 plan girdisi → segment_yap'ın anladığı biçim (video dışı planlar: durağan görsel / yer tutucu / kart / siyah)."""
    g = x.get("goruntu") or {}; tur = g.get("tur")
    if tur == "kart": gg = {"tur": "kart", "metin": g.get("metin") or x.get("metin") or ""}
    elif tur == "siyah": gg = {"tur": "siyah"}
    elif g.get("dosya") and os.path.splitext(g["dosya"])[1].lower() in (".png", ".jpg", ".jpeg", ".webp") \
            and os.path.isfile(os.path.join(film, g["dosya"])):
        gg = {"tur": "gorsel", "dosya": g["dosya"], "hareket": "nefes", "ayna": g.get("ayna")}
    else: gg = {"tur": "yer_tutucu"}
    return {"plan": x.get("plan"), "kare": n, "goruntu": gg, "serit": []}


def t2_segment_anahtari(film, x, n, w, h, kartlar):
    g = x.get("goruntu") or {}
    oz = {"v": SEG_SURUM + "t2", "w": w, "h": h, "kare": n, "tur": g.get("tur"), "kullanim": g.get("kullanim"), "hiz": g.get("hiz"),
          "ayna": g.get("ayna"), "kadraj": g.get("kadraj_kirpma"), "metin": g.get("metin"), "kart": kartlar,
          "dosya": t1.sha(os.path.join(film, g["dosya"])) if g.get("dosya") and os.path.isfile(os.path.join(film, g["dosya"])) else None,
          "plan": x.get("plan")}
    return hashlib.sha1(json.dumps(oz, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:20]


def kesit_plani(film, tur=1):
    """A14a: dikey kesit çizelgesi → KESIT/KURGU_PLANI_KESIT_v<tur>.json. Planlar BLOK_PLANI.json kesit.planlar'dan (yoksa KESIT-* blokları);
    T2 varsa o planların T2 girdileri (kırpma ve kurgucu kararlarıyla), yoksa SAHNELER kullanim penceresi. Çizelge boşluksuz, 1/24 sn."""
    ko = _alt_modul("kurgu_ortak")
    bp = ortak.json_oku(os.path.join(film, "BLOK_PLANI.json"), {}) or {}
    nolar = [int(n) for n in ((bp.get("kesit") or {}).get("planlar") or [])]
    if not nolar:
        nolar = [int(n) for b in bp.get("bloklar") or [] if str(b.get("id", "")).startswith("KESIT") for n in b.get("planlar") or []]
    if not nolar: raise RenderHatasi("dikey kesit planı yok (BLOK_PLANI.json kesit.planlar; önce blok_plani --kesit).")
    pl = ko.sahne_planlari(film)
    _, t2 = ko.kurgu_plani(film, "T2")
    t2d = {x.get("plan"): x for x in (t2 or {}).get("planlar") or []}
    planlar = []
    for p in sorted((pl[n] for n in set(nolar) if n in pl), key=lambda p: (float(p.get("sira", p["no"]) or 0), p["no"])):
        no = p["no"]
        if no in t2d: x = json.loads(json.dumps(t2d[no]))
        else:
            z = p.get("zanaat") or {}; k = p.get("kullanim") or {}
            sure = float(k.get("sure") or (p.get("_derlenir") or {}).get("sure_sn") or z.get("klip_sn") or 8)
            klip = ko.klip_yolu(film, z.get("kaynak_klip") or no)
            var = os.path.isfile(klip)
            x = {"sira": p.get("sira", no), "plan": no, "parti": p.get("parti"), "sahne_grubu": z.get("sahne_grubu"),
                 "goruntu": {"tur": "video" if var else "yer_tutucu", "dosya": ko.goreli(film, klip) if var else None,
                             "kullanim": {"bas": float(k.get("bas") or 0), "sure": sure}, "hiz": 1.0, "ayna": False, "kadraj_kirpma": None},
                 "sure": sure}
        planlar.append(x)
    t = 0.0
    for x in planlar:
        x["cizelge_bas"] = ko.kare(t); x["sure"] = ko.kare(float(x["goruntu"]["kullanim"]["sure"]) / float(x["goruntu"].get("hiz") or 1.0))
        t = x["cizelge_bas"] + x["sure"]
    kp = {"_sahip": "kurgu", "_surum": 1, "film": os.path.basename(film), "cizelge": "KESIT", "fps": FPS, "kurgu_surumu": int(tur),
          "planlar": planlar, "kartlar": [], "karartmalar": [], "kaynak_t2": bool(t2),
          "_uretim": {"asama": "A14a", "gorev": None, "girdi_imza": t1.sha(os.path.join(film, "BLOK_PLANI.json")), "arac_surum": SURUM,
                      "esik_surum": t1._esik_surum(), "sonuc": "GEC", "zaman": t1.simdi(), "ortam": t1.ortam()}}
    yol = os.path.join(film, "KESIT", "KURGU_PLANI_KESIT_v%d.json" % int(tur))
    ortak.atomik_yaz(yol, kp)
    return kp, yol


def t2_render(film, kip, tur=1, boyut=None, gorev=None):
    """KURGU_PLANI_T2 (kesitte KURGU_PLANI_KESIT) + SES_CIZELGESI stemleri (son_miks.onizle) → video. Kapı: süre = çizelge ±
    render_sure_tolerans_kare (HATA → 1)."""
    ko = _alt_modul("kurgu_ortak")
    film = os.path.abspath(film)
    if not ffmpeg_var(): raise OrtamHatasi("ffmpeg/ffprobe yok (KUR1).")
    klasor, vad, cizelgeler, skip, miks, asama, rad = T2_KIP[kip]
    if kip == "kesit": plan, pyol = kesit_plani(film, tur)
    else:
        pyol, plan = ko.kurgu_plani(film, "T2")
        if not plan: raise RenderHatasi("KURGU_PLANI_T2 yok (önce plan_kurgu.py).")
    if not plan.get("planlar"): raise RenderHatasi("çizelgede plan yok: %s" % os.path.relpath(pyol, film))
    w, h = boyut or T2_BOYUT[kip]
    n_ad = int(tur)
    onb = os.path.join(film, "KURGU", "_onbellek"); os.makedirs(onb, exist_ok=True)
    gd = tempfile.mkdtemp(prefix="yz_render_")          # işlem içi ara dosyalar; üretim verisi değildir
    liste, isabet, yeni, eksik = [], 0, 0, []
    kareler = t2_kareleri(plan); toplam = sum(n + k for _, n, k in kareler)
    hedef = os.path.join(film, klasor, vad.format(n=n_ad, film=os.path.basename(film)))
    try:
        for x, n, kar in kareler:
            g = x.get("goruntu") or {}
            kartlar = plan_kartlari(plan, x)
            seg = os.path.join(onb, "seg_%s.mp4" % t2_segment_anahtari(film, x, n, w, h, kartlar))
            if os.path.isfile(seg) and kare_say(seg) == n: isabet += 1
            else:
                if g.get("tur") == "video" and g.get("dosya") and os.path.isfile(os.path.join(film, g["dosya"])):
                    video_segment(film, x, n, w, h, kartlar, seg, os.path.join(gd, "p%s" % x.get("plan")))
                else:
                    if g.get("tur") == "video": eksik.append(x.get("plan"))
                    segment_yap(film, _t2_girdi(film, x, n), w, h, kartlar, seg, os.path.join(gd, "p%s" % x.get("plan")))
                yeni += 1
            liste.append(seg)
            if kar:
                sk = os.path.join(onb, "seg_siyah_%dx%d_%d.mp4" % (w, h, kar))
                if not (os.path.isfile(sk) and kare_say(sk) == kar):
                    segment_yap(film, {"plan": "karartma", "kare": kar, "goruntu": {"tur": "siyah"}, "serit": []}, w, h, [], sk,
                                os.path.join(gd, "k%s" % x.get("plan")))
                liste.append(sk)
        lst = os.path.join(gd, "liste.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for s_ in liste: f.write("file '%s'\n" % s_.replace("\\", "/").replace("'", "'\\''"))
        video = os.path.join(gd, "video.mp4")
        kos(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])
        sure = toplam / FPS
        ses, ses_kaynak = miks_al(film, cizelgeler, os.path.join(film, miks.format(n=n_ad)), skip, n_ad, asama)
        os.makedirs(os.path.dirname(hedef), exist_ok=True)
        br = "320k" if kip == "yayin" else "192k"
        if ses:
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", video, "-i", ses, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                   "-af", "apad", "-t", "%.4f" % sure, "-c:a", "aac", "-b:a", br, "-ar", "48000", hedef + ".tmp.mp4"]
        else:
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", video, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-map", "0:v", "-map", "1:a",
                   "-c:v", "copy", "-t", "%.4f" % sure, "-c:a", "aac", "-b:a", "96k", hedef + ".tmp.mp4"]
        kos(cmd); os.replace(hedef + ".tmp.mp4", hedef)
    finally:
        shutil.rmtree(gd, ignore_errors=True)
    olc = kare_say(hedef); tol = int(t1.E("render_sure_tolerans_kare") or 1)
    fark = None if olc is None else abs(olc - toplam)
    hatalar, bayraklar = [], []
    if fark is None or fark > tol: hatalar.append({"madde": "render_sure", "olcu": olc, "beklenen": toplam, "esik": tol})
    if not ses: bayraklar.append({"madde": "ses_yok", "neden": "SES_CIZELGESI stemleri ya da miks yok (ses_katmani, son_miks); sessiz iz"})
    if eksik: bayraklar.append({"madde": "video_yok", "planlar": eksik[:50], "neden": "klip dosyası yok; durağan görsel/yer tutucu kondu"})
    sonuc = "HATA" if hatalar else ("BAYRAK" if bayraklar else "GEC")
    rapor = {"_surum": 1, "_uretim": {"asama": asama, "gorev": gorev, "girdi_imza": t1.sha(pyol), "arac_surum": SURUM,
                                      "esik_surum": t1._esik_surum(), "sonuc": sonuc, "zaman": t1.simdi(), "ortam": t1.ortam()},
             "kip": kip, "dosya": os.path.relpath(hedef, film).replace("\\", "/"), "kurgu_plani": os.path.relpath(pyol, film).replace("\\", "/"),
             "kurgu_plani_imza": t1.sha(pyol), "video_imza": t1.sha(hedef), "boyut": [w, h], "fps": FPS,
             "kare_beklenen": toplam, "kare_olculen": olc, "fark_kare": fark, "tolerans_kare": tol, "sure_sn": round(toplam / FPS, 4),
             "ses": {"kaynak": os.path.relpath(ses, film).replace("\\", "/") if ses else None, "miks": ses_kaynak,
                     "stemler": (ortak.json_oku(os.path.join(film, next((c for c in cizelgeler if os.path.isfile(os.path.join(film, c))),
                                                                       cizelgeler[0])), {}) or {}).get("stemler")},
             "onbellek": {"isabet": isabet, "yeni": yeni}, "sonuc": sonuc, "hatalar": hatalar, "bayraklar": bayraklar}
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", rad.format(n=n_ad)), rapor)
    return rapor


# --- izle-dinle bilgi paketi (D-24) ---------------------------------------------------------------------------------
OKU_BENI = """Bu klasör filmin {ne} hâlidir; yalnız bilgi içindir, bir şey yapman gerekmez.

- {video}: filmin {ne} hâli. İzlemek istersen çift tıkla.
- ISITSEL_DOKUM.md: her planda duyulanların yazılı dökümü.
- SES_KADROSU: karakter seslerinden birer örnek.
- MUZIK: ana temanın örneği (yoksa müzik henüz üretilemedi).
{motor}
Beğenmediğin bir şey olursa Claude'a yazman yeter (ör. "şu sahne kopuk", "bu ses olmamış"). Not bırakmazsan ekip devam ediyor.
"""


def bilgi_paketi(film, kip="animatik", gorev=None):
    film = os.path.abspath(film)
    if kip == "animatik":
        vs = sorted(glob.glob(os.path.join(film, "ANIMATIK", "animatik_v*.mp4")), key=lambda x: int(re.search(r"_v(\d+)\.mp4$", x).group(1)))
        dok = os.path.join(film, "ANIMATIK", "ISITSEL_DOKUM.md")
    elif kip == "kesit":
        vs = sorted(glob.glob(os.path.join(film, "KESIT", "kesit_v*.mp4")), key=lambda x: int(re.search(r"_v(\d+)\.mp4$", x).group(1)))
        dok = os.path.join(film, "KURGU", "ISITSEL_DOKUM.md")
    else: raise RenderHatasi("bilgi paketi kipi: animatik | kesit")
    if not vs: raise RenderHatasi("%s videosu yok." % kip)
    hedef = os.path.join(film, "BILGI_PAKETI", kip)
    if os.path.isdir(hedef):
        import kor_paket as kp
        e = os.path.join(film, "BILGI_PAKETI", "_ESKI"); os.makedirs(e, exist_ok=True)
        import time
        shutil.move(hedef, os.path.join(e, "%s_%s" % (kip, time.strftime("%Y%m%d_%H%M%S"))))
    os.makedirs(os.path.join(hedef, "SES_KADROSU"), exist_ok=True); os.makedirs(os.path.join(hedef, "MUZIK"), exist_ok=True)
    video = os.path.basename(vs[-1]); shutil.copy2(vs[-1], os.path.join(hedef, video))
    icerik = {"video": video, "ses_kadrosu": [], "muzik": None, "motor_ornekleri": []}
    if os.path.isfile(dok): shutil.copy2(dok, os.path.join(hedef, "ISITSEL_DOKUM.md")); icerik["isitsel_dokum"] = True
    d = ortak.json_oku(os.path.join(film, "SESLER", "diyalog.json"), {}) or {}
    gorulen = set()
    for rid, v in sorted((d.get("replikler") or {}).items()) if isinstance(d.get("replikler"), dict) else []:
        k = (v or {}).get("karakter"); dosya = (((v or {}).get("tts") or {}).get("dosya")) or (v or {}).get("dosya")
        if not k or k in gorulen or not dosya or not os.path.isfile(os.path.join(film, dosya)): continue
        gorulen.add(k); ad = "%s%s" % (k, os.path.splitext(dosya)[1])
        shutil.copy2(os.path.join(film, dosya), os.path.join(hedef, "SES_KADROSU", ad)); icerik["ses_kadrosu"].append(ad)
    tema = None
    ml = ortak.json_oku(os.path.join(film, "MUZIK", "muzik_listesi.json"), {}) or {}
    for ip in ml.get("ipuclari") or []:
        if ip.get("tur") == "tema" and ip.get("secilen") and os.path.isfile(os.path.join(film, str(ip["secilen"]))):
            tema = os.path.join(film, ip["secilen"]); break
    if not tema:
        ms = sorted(glob.glob(os.path.join(film, "MUZIK", "secilen", "*.wav")))
        tema = ms[0] if ms else None
    if tema: shutil.copy2(tema, os.path.join(hedef, "MUZIK", os.path.basename(tema))); icerik["muzik"] = os.path.basename(tema)
    dinleyici_var = _dinleyici_olcu(film, kip)
    motor = ""
    if not dinleyici_var:
        try: o0 = os.path.join(ortak.yollar()["veri_kok"], "BILGI", "OLCUM0", "O0c_ornekler")
        except ortak.YolYok: o0 = None
        if o0 and os.path.isdir(o0):
            os.makedirs(os.path.join(hedef, "MOTOR_ORNEKLERI"), exist_ok=True)
            for f in sorted(os.listdir(o0))[:20]:
                if f.lower().endswith((".wav", ".mp3")):
                    shutil.copy2(os.path.join(o0, f), os.path.join(hedef, "MOTOR_ORNEKLERI", f)); icerik["motor_ornekleri"].append(f)
        motor = ("- MOTOR_ORNEKLERI: 'kulak' (dinleyici) bu filmi dinleyemedi; ses dönüştürme motorlarının örnekleri burada.\n"
                 if icerik["motor_ornekleri"] else "- 'Kulak' (dinleyici) bu filmi dinleyemedi; sesi senin kulağın denetler.\n")
    ne = "animatik (taslak)" if kip == "animatik" else "ilk dakikaları (dikey kesit)"
    with open(os.path.join(hedef, "OKU_BENI.txt"), "w", encoding="utf-8") as f: f.write(OKU_BENI.format(ne=ne, video=video, motor=motor))
    ortak.atomik_yaz(os.path.join(hedef, "PAKET.json"), {"_surum": 1, "_uretim": {"asama": "A12" if kip == "animatik" else "A14a",
                     "gorev": gorev, "girdi_imza": t1.sha(vs[-1]), "arac_surum": SURUM, "esik_surum": None, "sonuc": "GEC",
                     "zaman": t1.simdi(), "ortam": t1.ortam()}, "kip": kip, "icerik": icerik, "dinleyici": dinleyici_var})
    try:
        import bildirim
        metin = ("Animatik hazır. İzle-dinle paketi: %s. Not bırakırsan işlerim; bırakmazsan devam ediyorum." if kip == "animatik" else
                 "Filmin ilk dakikaları yayın kalitesinde hazır: %s. Kalan videolar bundan sonra çekilecek.") % hedef
        bildirim.gonder("bilgi_paketi", metin, film=film, dosya=os.path.join(hedef, video), anahtar=kip)
    except Exception: pass
    return {"klasor": os.path.relpath(hedef, film).replace("\\", "/"), "icerik": icerik}


def _dinleyici_olcu(film, kip):
    for p in glob.glob(os.path.join(film, "_RAPOR", "SEYIRCI", "%s_t*" % ("animatik" if kip == "animatik" else "kesit"), "dinleyici_rapor.json")):
        if (ortak.json_oku(p, {}) or {}).get("durum") == "olculdu": return True
    return False


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kurgu render.")
    ap.add_argument("--animatik", action="store_true"); ap.add_argument("--bilgi-paketi", action="store_true")
    ap.add_argument("--onizleme", action="store_true"); ap.add_argument("--kesit", action="store_true")
    ap.add_argument("--yayin", action="store_true"); ap.add_argument("--otio", action="store_true")
    ap.add_argument("--kip", default="animatik"); ap.add_argument("--tur", type=int); ap.add_argument("--boyut")
    ap.add_argument("--film"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film): print("!! --film <film klasörü> gerekli."); return 1
    g = t1.gorev_baglami(o.tur)
    try:
        if o.animatik:
            w, h = (int(x) for x in (o.boyut or "1280x720").lower().split("x"))
            r = animatik(film, g["tur"], (w, h), g["id"])
            print(json.dumps({k: r[k] for k in ("dosya", "kare_beklenen", "kare_olculen", "yer_tutucu_orani", "sonuc")}, ensure_ascii=False))
            return 1 if r["sonuc"] == "HATA" else 0
        if o.bilgi_paketi:
            print(json.dumps(bilgi_paketi(film, o.kip, g["id"]), ensure_ascii=False)); return 0
        if o.onizleme or o.kesit or o.yayin:
            kip = "onizleme" if o.onizleme else "kesit" if o.kesit else "yayin"
            boyut = tuple(int(x) for x in o.boyut.lower().split("x")) if o.boyut else None
            r = t2_render(film, kip, g["tur"], boyut, g["id"])
            print(json.dumps({k: r[k] for k in ("dosya", "kare_beklenen", "kare_olculen", "sonuc")}, ensure_ascii=False))
            return 1 if r["sonuc"] == "HATA" else 0
        if o.otio:
            print("OTIO dışa aktarımı P2'dir; bu sürümde yok."); return 4
    except OrtamHatasi as e: print("!! " + str(e)); return 4
    except RenderHatasi as e: print("!! " + str(e)); return 1
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main())
