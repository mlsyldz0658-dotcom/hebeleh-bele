"""JENERİK — kapanış jeneriği görüntüsü (TASARIM §6.7 jenerik.py, §1.3 A17; RE jenerik_max_sn ≤ 60 sn).

film.py görevi olarak ("<arac> <args> --film <film>"):
  python jenerik.py [--boyut 3840x2160] [--sure 40] --film <film>
Metin (öncelik sırasıyla): YAYIN/JENERIK_METNI.json (yayin-paketcisi; {"satirlar": [{"tur": "baslik|bolum|isim|not", "metin": ...}]})
  → yoksa HIKAYE.json (başlık ekran adı, karakterler) + MUZIK/KAYNAK_KAYDI.json (müzik künyesi) + SESLER (ses kadrosu) + YZ beyanı.
Şablon: <evren>/<SERI>/sablonlar/jenerik.json (font, renkler, oranlar, süre; evren.py --film-sonu ilk filmin şablonunu evrene ekler)
  yoksa varsayılan şablon. Kurgunun sonraki filmde yeniden kullandığı varlıktır.
Çıktı: YAYIN/JENERIK/jenerik.png (uzun künye görseli) · YAYIN/JENERIK/jenerik.mp4 (aşağıdan yukarı kayan, 24 fps, sessiz; ses
  son_miks'in işi: jenerik ana temayla çalar) · YAYIN/JENERIK/jenerik.json (satırlar, süre, şablon; capcut_film'in taslak parçası).
Süre ≤ jenerik_max_sn (eşik dosyası; aşan istek kırpılır ve not düşülür).
Pillow yoksa yalnız jenerik.json (görüntü ÖLÇÜLEMEDİ notu); ffmpeg yoksa mp4 yok (not). İkisi de çıkış 0'dır; eksik jenerik.json'da yazar.
Çıkış kodları: 0 tamam · 1 film yok · 4 ORTAM (YOLLAR.json yok) · kullanım 4.
"""
import os, sys, json, glob, shutil, datetime, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "jenerik 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
SABLON = {"font": None, "renk": "#E8E2D0", "vurgu": "#C9A45C", "arka": "#000000", "baslik_oran": 0.060, "bolum_oran": 0.030,
          "satir_oran": 0.036, "not_oran": 0.026, "aralik_oran": 0.55, "sure_sn": 40, "fps": 24}
FONT_ADAYLARI = ("C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/arial.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                 "/usr/share/fonts/dejavu/DejaVuSans.ttf", "/Library/Fonts/Georgia.ttf")


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def esik(ad, v):
    try:
        import esikler
        x = esikler.yukle()[ad]
        return v if x is None else x
    except Exception: return v


def sablon(film):
    s = dict(SABLON); kaynak = "varsayilan"
    try:
        import evren
        seri = evren.film_serisi(film)
        p = evren.seri_yolu(seri, "sablonlar", "jenerik.json") if seri else None
        j = ortak.json_oku(p) if p else None
        if isinstance(j, dict): s.update({k: v for k, v in j.items() if k in SABLON}); kaynak = "evren"
    except Exception: pass
    return s, kaynak


def satirlar(film):
    j = ortak.json_oku(os.path.join(film, "YAYIN", "JENERIK_METNI.json"))
    if isinstance(j, dict) and j.get("satirlar"): return [x for x in j["satirlar"] if isinstance(x, dict) and x.get("metin")], "yayin-paketcisi"
    h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    s = []
    b = h.get("baslik")
    ad = (b.get("ekran") or str(b.get("secilen") or "").split("|")[0].strip()) if isinstance(b, dict) else \
        (b.split("|")[0].strip() if isinstance(b, str) else None)
    if ad: s.append({"tur": "baslik", "metin": ad})
    if h.get("evren"): s.append({"tur": "not", "metin": f"A {str(h['evren']).replace('_', ' ').title()} story"})
    kar = h.get("karakterler") or {}
    kar = kar.values() if isinstance(kar, dict) else kar
    isimler = [k.get("ad") for k in kar if isinstance(k, dict) and k.get("ad") and k.get("rol") != "figuran"]
    if isimler: s += [{"tur": "bolum", "metin": "Characters"}] + [{"tur": "isim", "metin": x} for x in isimler]
    kk = ortak.json_oku(os.path.join(film, "MUZIK", "KAYNAK_KAYDI.json"), {}) or {}
    muz = kk.get("kayitlar") if isinstance(kk, dict) else kk
    muz = [x for x in (muz or []) if isinstance(x, dict)]
    if muz:
        s.append({"tur": "bolum", "metin": "Music"})
        for x in muz[:12]:
            parca = " · ".join(str(v) for v in (x.get("baslik") or x.get("motif"), x.get("model") or x.get("kaynak"), x.get("lisans")) if v)
            if parca: s.append({"tur": "isim", "metin": parca})
    s += [{"tur": "bolum", "metin": "Made with"},
          {"tur": "isim", "metin": "AI-generated images, video and voices"},
          {"tur": "not", "metin": "This film contains realistic synthetic content."}]
    return s, "otomatik"


def renk(h):
    h = str(h).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) if len(h) == 6 else (230, 226, 208)


def font(ImageFont, yol, boyut):
    for p in [yol] + list(FONT_ADAYLARI):
        if p and os.path.isfile(p):
            try: return ImageFont.truetype(p, boyut)
            except OSError: pass
    try: return ImageFont.load_default(size=boyut)
    except TypeError: return ImageFont.load_default()


def gorsel_kur(s, sab, gen, yuk, hedef):
    """Uzun künye görseli (genişlik = video genişliği). Görsel yüksekliğini döndürür."""
    from PIL import Image, ImageDraw, ImageFont
    olc = {"baslik": sab["baslik_oran"], "bolum": sab["bolum_oran"], "isim": sab["satir_oran"], "not": sab["not_oran"]}
    parca = []
    for x in s:
        f = font(ImageFont, sab.get("font"), max(10, int(yuk * olc.get(x.get("tur"), sab["satir_oran"]))))
        bosluk = int(yuk * olc.get(x.get("tur"), sab["satir_oran"]) * (2.2 if x.get("tur") in ("bolum", "baslik") else sab["aralik_oran"]))
        parca.append((x, f, bosluk))
    olcu = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    yuks = []
    for x, f, b in parca:
        kutu = olcu.textbbox((0, 0), x["metin"], font=f); yuks.append(kutu[3] - kutu[1])
    toplam = sum(yuks) + sum(b for _, _, b in parca) + yuk // 4
    img = Image.new("RGB", (gen, max(yuk, toplam)), renk(sab["arka"])); d = ImageDraw.Draw(img); y = yuk // 8
    for (x, f, b), hh in zip(parca, yuks):
        if x.get("tur") in ("bolum",): y += b // 2
        kutu = d.textbbox((0, 0), x["metin"], font=f); w = kutu[2] - kutu[0]
        d.text(((gen - w) // 2 - kutu[0], y - kutu[1]), x["metin"], font=f,
               fill=renk(sab["vurgu"] if x.get("tur") in ("bolum", "baslik") else sab["renk"]))
        y += hh + (b if x.get("tur") != "bolum" else b // 2)
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    img.save(hedef + ".tmp.png"); os.replace(hedef + ".tmp.png", hedef)
    return img.size[1]


def video_kur(png, gen, yuk, sure, fps, arka, hedef):
    tmp = hedef[:-4] + ".tmp.mp4"
    fc = (f"color=c=0x{str(arka).lstrip('#')}:s={gen}x{yuk}:r={fps}:d={sure}[bg];"
          f"[bg][0:v]overlay=x=0:y='H-(t/{sure})*(H+h)':shortest=1,format=yuv420p[v]")
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-loop", "1", "-framerate", str(fps), "-i", png,
                        "-filter_complex", fc, "-map", "[v]", "-t", str(sure), "-r", str(fps), "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "18", "-an", tmp], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(tmp): return r.stderr.strip()[-300:] or f"ffmpeg çıkış {r.returncode}"
    os.replace(tmp, hedef); return None


def uret(film, boyut=None, sure=None):
    sab, sab_kaynak = sablon(film); s, metin_kaynak = satirlar(film)
    gen, yuk = (int(x) for x in (boyut or "3840x2160").lower().split("x"))
    mx = float(esik("jenerik_max_sn", 60)); istenen = float(sure or sab.get("sure_sn") or 40)
    sure = min(istenen, mx); notlar = []
    if istenen > mx: notlar.append(f"istenen {istenen} sn > jenerik_max_sn {mx}; {mx} sn'ye kırpıldı")
    kl = os.path.join(film, "YAYIN", "JENERIK"); png, mp4 = os.path.join(kl, "jenerik.png"), os.path.join(kl, "jenerik.mp4")
    durum = {"png": None, "mp4": None}
    try:
        gorsel_kur(s, sab, gen, yuk, png); durum["png"] = "YAYIN/JENERIK/jenerik.png"
    except ImportError: notlar.append("Pillow yok: görsel üretilemedi (ÖLÇÜLEMEDİ; KUR1)")
    if durum["png"]:
        if not shutil.which("ffmpeg"): notlar.append("ffmpeg yok: video üretilemedi")
        else:
            e = video_kur(png, gen, yuk, sure, int(sab.get("fps") or 24), sab["arka"], mp4)
            if e: notlar.append(f"video üretilemedi: {e}")
            else: durum["mp4"] = "YAYIN/JENERIK/jenerik.mp4"
    j = {"_surum": 1, "_uretim": {"asama": "A17", "gorev": os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None,
                                  "arac_surum": SURUM, "zaman": simdi(), "sonuc": "GEC" if durum["mp4"] else "BAYRAK",
                                  "ortam": "yerel" if os.name == "nt" else "bulut"},
         "satirlar": s, "metin_kaynagi": metin_kaynak, "sure_sn": sure, "boyut": [gen, yuk], "fps": int(sab.get("fps") or 24),
         "sablon": sab, "sablon_kaynagi": sab_kaynak, "dosyalar": durum, "notlar": notlar,
         "taslak_parcasi": {"kanal": "Klipler", "dosya": durum["mp4"], "sure": sure, "konum": "film_sonu",
                            "ses": "ana tema (son_miks)"}}
    ortak.atomik_yaz(os.path.join(kl, "jenerik.json"), j)
    print(f"Jenerik: {len(s)} satır, {sure:g} sn" + (f" → {durum['mp4']}" if durum["mp4"] else "") + ("" if not notlar else " · " + "; ".join(notlar)))
    return j


def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def main(a):
    if "-h" in a or "--help" in a: print(__doc__); return BITTI
    try:
        f = _arg(a, "--film")
        film = (os.path.abspath(f) if f and os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)) if f else None
        if not film or not os.path.isdir(film): print("!! --film <film> gerekli (klasör yok)"); return HATA
        b = _arg(a, "--boyut")
        if b and not (b.lower().count("x") == 1 and all(x.isdigit() for x in b.lower().split("x"))): print("!! --boyut GENxYUK"); return ORTAM
        uret(film, b, _arg(a, "--sure")); return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
