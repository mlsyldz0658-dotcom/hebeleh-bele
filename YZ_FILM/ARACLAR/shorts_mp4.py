"""SHORTS MP4 — 3 Short (9:16) + fragman, doğrudan MP4 (TASARIM §6.7 shorts_mp4.py, §1.3 A17, D-26, EÇ6; [SM2] S7.9).

film.py görevi olarak ("<arac> <args> --film <film>"):
  python shorts_mp4.py [--boyut 1080x1920] [--kaynak YAYIN/<FILM>_4K.mp4] --film <film>
Pencereler: YAYIN/PAKET.json "shorts" ve "fragman" (yayin-paketcisi; zamanlar KURGU_PLANI çizelgesinden) → yoksa PAKET_TASLAK.json →
  yoksa yayin_paketi.taslak() (HIKAYE short_adaylari + vuruşlar). Short: 30–60 sn, dikey 9:16 (orta kırpma), ilk 2 sn kanca metni
  üstte, son 3 sn filme bağlantı metni altta. Fragman: 30–60 sn, dikey kesitten (KESIT/kesit_v<N>.mp4; yoksa yayın dosyası), 16:9.
Ses: son_miks.py varsa `son_miks.py --shorts --dosya <mp4> --film <film>` (tek miks kodu, PR-9); yoksa ölçülen yüksekliğe göre TEK
  doğrusal kazanç + tepe sınırlayıcı (−14 LUFS hedef; dinamik işlem yok). Sonra yeniden ölçülür: S7.9 −14 ±1 LUFS, ≤ −1 dBTP (H).
Çıktı: YAYIN/SHORTS/short_<n>.mp4 · YAYIN/FRAGMAN/fragman.mp4 · YAYIN/SHORTS/SHORTS.json (pencere, ölçüm, metin) ·
  kapı raporu _RAPOR/YAYIN_SHORTS.json (kapı YAYIN, kapsam SHORTS; bilgi, aşama kapısı değil).
ffmpeg yoksa ya da kaynak medya değilse (sahte deneme) dosya üretilmez, ölçümler ÖLÇÜLEMEDİ (= BAYRAK).
Çıkış kodları: 0 tamam (sonuç raporda) · 1 film yok · 4 ORTAM (YOLLAR.json yok) · kullanım 4.
"""
import os, re, sys, glob, json, shutil, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi
import kalite_denetim_final as kdf
import yayin_paketi as yp

SURUM = "shorts_mp4 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
KANCA_SN, BAGLANTI_SN = 2, 3
HEDEF_TEPE_DBTP = -1.5          # [SM2] S7.2 kodlama öncesi hedef (tahmin; AAC tepeyi artırabilir)


def gorev_id(): return os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None


def plan(film):
    for ad in ("PAKET.json", "PAKET_TASLAK.json"):
        p = ortak.json_oku(os.path.join(film, "YAYIN", ad))
        if isinstance(p, dict) and (p.get("shorts") or p.get("fragman")): return p, ad
    return yp.taslak(film), "yayin_paketi.taslak"


def kaynak_dosya(film, verilen=None):
    if verilen: return verilen if os.path.isabs(verilen) else os.path.join(film, verilen)
    yd = ortak.json_oku(os.path.join(film, "YAYIN", "YAYIN_DOGRULAMA.json"), {}) or {}
    if yd.get("dosya") and os.path.isfile(os.path.join(film, yd["dosya"])): return os.path.join(film, yd["dosya"])
    return kdf.yayin_dosyasi(film)


def yazi_png(metin, gen, yuk, ust, hedef):
    """Saydam katman: metin üstte (kanca) ya da altta (bağlantı). Pillow yoksa None."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import jenerik
    except ImportError: return None
    img = Image.new("RGBA", (gen, yuk), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    f = jenerik.font(ImageFont, None, max(10, int(gen * 0.065)))
    satirlar, satir = [], ""
    for k in str(metin).split():
        aday = (satir + " " + k).strip()
        if d.textbbox((0, 0), aday, font=f)[2] > gen * 0.86 and satir: satirlar.append(satir); satir = k
        else: satir = aday
    if satir: satirlar.append(satir)
    hh = [d.textbbox((0, 0), s, font=f) for s in satirlar]; top = sum(b[3] - b[1] for b in hh) + 12 * len(hh)
    y = int(yuk * 0.12) if ust else int(yuk * 0.82) - top
    for s, b in zip(satirlar, hh):
        w = b[2] - b[0]; x = (gen - w) // 2 - b[0]
        d.rectangle((x - 18, y - 10, x + w + 18, y + (b[3] - b[1]) + 14), fill=(0, 0, 0, 150))
        d.text((x, y - b[1]), s, font=f, fill=(255, 255, 255, 255)); y += (b[3] - b[1]) + 12
    img.save(hedef); return hedef


def kes(kaynak, bas, sure, hedef, gen, yuk, dikey, katmanlar):
    """Bir pencereyi keser; dikeyse 9:16 orta kırpma. katmanlar: [(png, t0, t1)]."""
    vf = (f"crop='min(iw,ih*9/16)':ih,scale={gen}:{yuk}" if dikey else f"scale={gen}:{yuk}:force_original_aspect_ratio=decrease,"
          f"pad={gen}:{yuk}:(ow-iw)/2:(oh-ih)/2") + ",setsar=1"
    girdi = ["-ss", f"{bas:.3f}", "-t", f"{sure:.3f}", "-i", kaynak]
    fc = f"[0:v]{vf}[v0]"; son = "v0"
    for i, (png, t0, t1) in enumerate(katmanlar):
        girdi += ["-i", png]
        fc += f";[{son}][{i + 1}:v]overlay=0:0:enable='between(t,{t0},{t1})'[v{i + 1}]"; son = f"v{i + 1}"
    fc += f";[{son}]format=yuv420p[vo]"
    tmp = hedef[:-4] + ".tmp.mp4"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *girdi, "-filter_complex", fc, "-map", "[vo]", "-map", "0:a:0?",
                        "-r", "24", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
                        tmp], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(tmp): return r.stderr.strip()[-300:] or f"ffmpeg çıkış {r.returncode}"
    os.replace(tmp, hedef); return None


def ses_ayarla(film, p):
    """(yöntem, hata). son_miks varsa onu çağırır; yoksa tek doğrusal kazanç + sınırlayıcı (yalnız ses yeniden kodlanır)."""
    sm = os.path.join(HERE, "son_miks.py")
    if os.path.isfile(sm):
        r = subprocess.run([sys.executable, sm, "--shorts", "--dosya", p, "--film", film], capture_output=True, text=True)
        return ("son_miks", None) if r.returncode == 0 else ("son_miks", f"son_miks --shorts çıkış {r.returncode}")
    y = kdf.olc_yukseklik(p)
    if not y or y["lufs"] <= -70: return "dogrusal_kazanc", "ses ölçülemedi (sessiz ya da yok)"
    kazanc = kdf.esik("final_lufs") - y["lufs"]
    limit = 10 ** (HEDEF_TEPE_DBTP / 20)
    tmp = p[:-4] + ".ses.mp4"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", "-i", p, "-map", "0:v:0", "-map", "0:a:0", "-c:v", "copy",
                        "-af", f"volume={kazanc:.2f}dB,alimiter=limit={limit:.4f}:attack=1:release=50:level=disabled",
                        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", tmp], capture_output=True, text=True)
    if r.returncode != 0: return "dogrusal_kazanc", r.stderr.strip()[-200:]
    os.replace(tmp, p); return "dogrusal_kazanc", None


def uret(film, boyut=None, kaynak=None):
    p, kaynak_plan = plan(film); src = kaynak_dosya(film, kaynak)
    gen, yuk = (int(x) for x in (boyut or "1080x1920").lower().split("x"))
    o, kayit = [], {"_surum": 1, "plan_kaynagi": kaynak_plan, "kaynak": os.path.relpath(src, film).replace("\\", "/") if src else None,
                    "shorts": [], "fragman": None}
    medya = bool(src and os.path.isfile(src) and kdf.ffmpeg_var() and (kdf.sure_fps(src) or {}).get("video"))
    if not medya:
        o.append({"madde": "shorts", "seviye": "OLCULEMEDI", "neden": "kaynak video yok, medya değil ya da ffmpeg yok (sahte deneme?)"})
    ks = os.path.join(film, "YAYIN", "SHORTS"); os.makedirs(ks, exist_ok=True)
    sure_src = (kdf.sure_fps(src) or {}).get("sure") if medya else None
    for i, s in enumerate((p.get("shorts") or [])[:yp.SHORT_ADET], 1):
        bas = yp.zaman_sn(s.get("bas")) or 0.0; bit = yp.zaman_sn(s.get("bit")) or bas
        if sure_src: bit = min(bit, sure_src)
        d = bit - bas; ad = f"short_{i}"
        k = {"ad": ad, "bas": bas, "bit": bit, "sure": round(d, 3), "kanca_metni": s.get("kanca_metni"), "baglanti_metni": s.get("baglanti_metni")}
        if not yp.SHORT_SURE[0] <= d <= yp.SHORT_SURE[1]:
            o.append({"madde": "short_sure", "birim": ad, "seviye": "HATA", "olcu": round(d, 2), "esik": list(yp.SHORT_SURE)})
        if medya:
            kat = []
            if s.get("kanca_metni"):
                png = yazi_png(s["kanca_metni"], gen, yuk, True, os.path.join(ks, f"{ad}_kanca.png"))
                if png: kat.append((png, 0, KANCA_SN))
            if s.get("baglanti_metni"):
                png = yazi_png(s["baglanti_metni"], gen, yuk, False, os.path.join(ks, f"{ad}_baglanti.png"))
                if png: kat.append((png, max(0, round(d - BAGLANTI_SN, 2)), round(d, 2)))
            if (s.get("kanca_metni") or s.get("baglanti_metni")) and not kat:
                o.append({"madde": "short_metin", "birim": ad, "seviye": "BAYRAK", "neden": "Pillow yok: metin bindirilemedi"})
            hedef = os.path.join(ks, ad + ".mp4"); e = kes(src, bas, d, hedef, gen, yuk, True, kat)
            if e: o.append({"madde": "short_uretim", "birim": ad, "seviye": "HATA", "neden": e})
            else:
                k["dosya"] = os.path.relpath(hedef, film).replace("\\", "/")
                k["ses_yontemi"], he = ses_ayarla(film, hedef)
                if he: o.append({"madde": "short_ses", "birim": ad, "seviye": "HATA", "neden": he})
                y = kdf.olc_yukseklik(hedef); k["ses"] = y
                for x in kdf.ses_olcumleri(y): o.append(dict(x, madde=x["madde"].replace("S8.1", "S7.9"), birim=ad))
        kayit["shorts"].append(k)
    if len(kayit["shorts"]) < yp.SHORT_ADET:
        o.append({"madde": "short_sayisi", "seviye": "BAYRAK", "olcu": len(kayit["shorts"]), "esik": yp.SHORT_ADET})
    fr = p.get("fragman")
    if fr:
        fsrc = os.path.join(film, fr["kaynak"]) if fr.get("kaynak") and os.path.isfile(os.path.join(film, fr["kaynak"])) else src
        bas = yp.zaman_sn(fr.get("bas")) or 0.0; bit = yp.zaman_sn(fr.get("bit")) or bas
        fs = (kdf.sure_fps(fsrc) or {}).get("sure") if medya and fsrc else None
        if fs: bit = min(bit, fs)
        k = {"kaynak": os.path.relpath(fsrc, film).replace("\\", "/") if fsrc else None, "bas": bas, "bit": bit, "sure": round(bit - bas, 3)}
        if not yp.SHORT_SURE[0] <= bit - bas <= yp.SHORT_SURE[1]:
            o.append({"madde": "fragman_sure", "seviye": "BAYRAK", "olcu": round(bit - bas, 2), "esik": list(yp.SHORT_SURE)})
        if medya and fsrc:
            hedef = os.path.join(film, "YAYIN", "FRAGMAN", "fragman.mp4"); os.makedirs(os.path.dirname(hedef), exist_ok=True)
            e = kes(fsrc, bas, bit - bas, hedef, yuk, gen, False, [])        # yatay: genişlik/yükseklik yer değiştirir
            if e: o.append({"madde": "fragman_uretim", "seviye": "HATA", "neden": e})
            else:
                k["dosya"] = os.path.relpath(hedef, film).replace("\\", "/"); k["ses_yontemi"], he = ses_ayarla(film, hedef)
                if he: o.append({"madde": "fragman_ses", "seviye": "HATA", "neden": he})
                k["ses"] = kdf.olc_yukseklik(hedef)
                for x in kdf.ses_olcumleri(k["ses"]): o.append(dict(x, madde=x["madde"].replace("S8.1", "S7.9"), birim="fragman"))
        kayit["fragman"] = k
    else:
        o.append({"madde": "fragman", "seviye": "BAYRAK", "neden": "fragman planı yok"})
    r = kapi.rapor_kur("YAYIN", "SHORTS", o, tur=1, asama="A17", gorev=gorev_id(), arac_surum=SURUM, birim="dosya")
    h = kapi.dogrula(r)
    if h: raise kapi.RaporHatasi(h)
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", "YAYIN_SHORTS.json"), r)
    kayit["_uretim"] = r["_uretim"]; kayit["sonuc"] = r["sonuc"]
    ortak.atomik_yaz(os.path.join(ks, "SHORTS.json"), {"_surum": 1, "_uretim": kayit.pop("_uretim"), **kayit})
    print(f"Shorts: {sum(1 for k in kayit['shorts'] if k.get('dosya'))}/{len(kayit['shorts'])} dosya"
          + (" + fragman" if (kayit["fragman"] or {}).get("dosya") else "") + f" · {r['sonuc']}")
    return kayit, r


def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def main(a):
    if "-h" in a or "--help" in a: print(__doc__); return BITTI
    try:
        f = _arg(a, "--film")
        film = (os.path.abspath(f) if f and os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)) if f else None
        if not film or not os.path.isdir(film): print("!! --film <film> gerekli (klasör yok)"); return HATA
        b = _arg(a, "--boyut")
        if b and not re.fullmatch(r"\d+x\d+", b.lower()): print("!! --boyut GENxYUK"); return ORTAM
        uret(film, b, _arg(a, "--kaynak")); return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
