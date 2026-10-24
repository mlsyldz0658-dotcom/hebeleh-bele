"""KALİTE DENETİM --final — dışa aktarılmış yayın dosyasının son denetimi ve yayın doğrulaması (TASARIM §1.3 A17, §7.2 S8 + YAYIN,
[SM2] §4.7.8 S8.1–S8.2, [KU2] §4.5.8 YAYIN_DOGRULAMA, KR12).

kalite_denetim.py "--final" kipini bu modüle yönlendirir (bağlantı satırı: paylaşılan istek). Doğrudan:
  python kalite_denetim_final.py --final [--dosya YAYIN/<FILM>_4K.mp4] [--master YAYIN/ses_master.wav] [--tur N] --film <film>
Ölçümler (ffmpeg/ffprobe; sayılar eşik dosyalarından: final_lufs ±final_lufs_tolerans, true_peak_max_dbtp, mutlak_sessizlik_*,
mux_ofset_max_kare, mux_korelasyon_min, mux_pencere, yayin_sure_tolerans_kare):
  S8.1  dışa aktarılan dosyada bütünleşik yükseklik −14 ±1 LUFS ve gerçek tepe ≤ −1 dBTP (ebur128 peak=true)            H
  sure  dosya süresi = KURGU_PLANI çizelgesi ± 1 kare                                                                 H
  siyah / donma / sessizlik: KURGU_PLANI'nda planlanmamış siyah (blackdetect) ve donma (freezedetect) 0; planlanmamış mutlak
        sessizlik (silencedetect −50 dB, 0,3 sn) mutlak_sessizlik_max_sn'den uzun 0 ve sayısı ≤ mutlak_sessizlik_film_max       H
  mux   ses_master.wav varsa 40 × 10 sn pencerede çapraz korelasyon: her pencerede ofset ≤ 1 kare ve tepe ≥ 0,9               H
  S8.2  kullanıcı CapCut'ta sesle oynadıysa (TASLAK_FARK geri_uretilemeyen) yeniden karıştırma yok: mux türü dogrusal_kazanc     H
  biçim 2160p ve KURGU_PLANI fps'i (değilse BAYRAK: dışa aktarım ayarı)
Mux kararı ([KU2] §4.5.8): yükseklik/tepe tutmuyorsa ve kanıt varsa `son_miks.py --mux <tur>` (PR-9, tek miks kodu) BİR KEZ çalışır,
  sonra yeniden ölçülür (sonuç YAYIN/<FILM>_4K_MUX.mp4; kullanıcının dosyası değişmez). Tür: kullanıcı ses düzenlemesi varsa
  dogrusal_kazanc, yoksa ve korelasyon kanıtı varsa master_stem; kanıt yoksa mux yapılmaz → HATA + "A16n" önerisi. son_miks yoksa HATA.
Çıktı: YAYIN/YAYIN_DOGRULAMA.json (sonuc, hazir_degil_nedeni) · kapı raporu _RAPOR/S8_FINAL_t<n>.json (kapı S8, kapsam FINAL).
ffmpeg yoksa ya da dosya medya değilse (sahte deneme) ölçümler ÖLÇÜLEMEDİ (= BAYRAK; geçmiş sayılmaz).
Kodda: olc_yukseklik(p) → {lufs, tepe_dbtp, lra} · araliklar(p) → {siyah, donma, sessizlik} · sure_fps(p) · mux_korelasyon(a, b, fps)
Çıkış kodları: 0 rapor yazıldı (kapı sonucu raporda) · 1 film/girdi yok · 4 ORTAM (YOLLAR.json yok) · kullanım 4.
"""
import os, re, sys, glob, json, shutil, datetime, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi

SURUM = "kalite_denetim_final 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
VARSAYILAN = {"final_lufs": -14.0, "final_lufs_tolerans": 1.0, "true_peak_max_dbtp": -1.0, "mutlak_sessizlik_db": -50,
              "mutlak_sessizlik_max_sn": 1.0, "mutlak_sessizlik_film_max": 2, "mux_ofset_max_kare": 1, "mux_korelasyon_min": 0.9,
              "mux_pencere": {"adet": 40, "sure_sn": 10}, "yayin_sure_tolerans_kare": 1}
SESSIZLIK_MIN_SN = 0.3          # [SM2] S7.4 silencedetect d=0,3 (tahmin)
SIYAH_MIN_SN, DONMA_MIN_SN = 0.5, 2.0   # blackdetect / freezedetect alt süresi (tahmin; ölçüm aracı ayarı, kapı eşiği değil)
DURAGAN_TURLER = ("gorsel", "kart", "siyah", "yer_tutucu")
SES_KANALLARI = ("ses", "diyalog", "efekt", "ambiyans", "muzik", "audio", "volume")


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def esik(ad):
    try:
        import esikler
        v = esikler.yukle()[ad]
        if v is not None: return v
    except Exception: pass
    return VARSAYILAN[ad]


def gorev_baglami(tur=None):
    g = ortak.json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV") or "", "GOREV.json"), {}) or {}
    return {"id": g.get("id"), "tur_no": int(tur or g.get("tur_no") or 1), "asama": g.get("asama") or "A17", "rapor": g.get("rapor")}


def ffmpeg_var(): return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


# --- ölçüm araçları ---------------------------------------------------------------------------------------------------
def sure_fps(p):
    """{sure, fps, genislik, yukseklik, ses} ya da None (medya değil)."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,avg_frame_rate",
                        "-of", "json", p], capture_output=True, text=True)
    if r.returncode != 0: return None
    try: j = json.loads(r.stdout)
    except ValueError: return None
    v = next((s for s in j.get("streams") or [] if s.get("codec_type") == "video"), None)
    a = any(s.get("codec_type") == "audio" for s in j.get("streams") or [])
    try: sure = float((j.get("format") or {}).get("duration"))
    except (TypeError, ValueError): return None
    fps = None
    if v and v.get("avg_frame_rate") and "/" in v["avg_frame_rate"]:
        n, d = v["avg_frame_rate"].split("/")
        fps = round(float(n) / float(d), 3) if float(d) else None
    return {"sure": sure, "fps": fps, "genislik": (v or {}).get("width"), "yukseklik": (v or {}).get("height"), "ses": a,
            "video": v is not None}


def olc_yukseklik(p):
    """ebur128 (peak=true): {lufs, tepe_dbtp, lra} ya da None."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", p, "-map", "0:a:0", "-filter:a", "ebur128=peak=true",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = r.stderr[r.stderr.rfind("Summary:"):] if "Summary:" in r.stderr else ""
    i = re.search(r"I:\s*(-?[\d.]+|-inf)\s*LUFS", m); t = re.search(r"Peak:\s*(-?[\d.]+|-inf)\s*dBFS", m)
    l = re.search(r"LRA:\s*(-?[\d.]+)\s*LU", m)
    if not i: return None
    f = lambda x: -120.0 if x.group(1) == "-inf" else float(x.group(1))
    return {"lufs": f(i), "tepe_dbtp": f(t) if t else None, "lra": float(l.group(1)) if l else None}


def araliklar(p, sessizlik_db=-50, video=True):
    """Siyah, donma ve mutlak sessizlik aralıkları: {siyah: [(bas, bit)], donma: [...], sessizlik: [...]}."""
    k = ["ffmpeg", "-hide_banner", "-nostats", "-i", p]
    if video: k += ["-map", "0:v:0", "-vf", f"blackdetect=d={SIYAH_MIN_SN}:pix_th=0.10,freezedetect=n=-60dB:d={DONMA_MIN_SN}"]
    k += ["-map", "0:a:0?", "-af", f"silencedetect=n={sessizlik_db}dB:d={SESSIZLIK_MIN_SN}", "-f", "null", "-"]
    r = subprocess.run(k, capture_output=True, text=True); e = r.stderr
    siyah = [(float(a), float(b)) for a, b in re.findall(r"black_start:\s*([\d.]+)\s+black_end:\s*([\d.]+)", e)]
    sure = (sure_fps(p) or {}).get("sure") or 0.0

    def ciftle(bas_desen, bit_desen):
        b = [float(x) for x in re.findall(bas_desen, e)]; s = [float(x) for x in re.findall(bit_desen, e)]
        return [(x, s[i] if i < len(s) else sure) for i, x in enumerate(b)]
    return {"siyah": siyah, "donma": ciftle(r"freeze_start:\s*([\d.]+)", r"freeze_end:\s*([\d.]+)"),
            "sessizlik": ciftle(r"silence_start:\s*(-?[\d.]+)", r"silence_end:\s*([\d.]+)")}


def _pcm(p, sr=4000):
    import numpy as np
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-i", p, "-map", "0:a:0", "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
                       capture_output=True)
    if r.returncode != 0: return None
    return np.frombuffer(r.stdout, dtype=np.float32).astype(np.float64)


def mux_korelasyon(a_yol, b_yol, fps, pencere=None, sr=4000, arama_sn=0.5):
    """Yayın dosyası (a) ↔ master (b): pencere başına {bas, ofset_kare, tepe}. numpy yoksa None."""
    try: import numpy as np
    except ImportError: return None
    a, b = _pcm(a_yol, sr), _pcm(b_yol, sr)
    if a is None or b is None: return None
    pencere = pencere or esik("mux_pencere"); adet = int(pencere.get("adet", 40)); w = int(float(pencere.get("sure_sn", 10)) * sr)
    n = min(len(a), len(b)); L = int(arama_sn * sr)
    if n < w + 2 * L: w = max(sr, n - 2 * L)
    if n < w + 2 * L or w <= 0: return []
    baslar = [L + int(i * (n - w - 2 * L) / max(1, adet - 1)) for i in range(adet)] if adet > 1 else [L]
    out = []
    for s in sorted(set(baslar)):
        x = a[s:s + w]; y = b[s - L:s + w + L]
        if x.std() < 1e-6 or y.std() < 1e-6: out.append({"bas": round(s / sr, 2), "atlandi": "sessiz"}); continue
        x = (x - x.mean()) / (x.std() * len(x))
        m = len(y) + len(x)
        c = np.fft.irfft(np.fft.rfft(y, m) * np.conj(np.fft.rfft(x, m)), m)[:len(y) - len(x) + 1]
        yy = np.concatenate([[0.0], np.cumsum(y * y)]); ym = np.concatenate([[0.0], np.cumsum(y)])
        k = np.arange(len(c)); nw = len(x)
        var = (yy[k + nw] - yy[k]) / nw - ((ym[k + nw] - ym[k]) / nw) ** 2
        cc = c / np.sqrt(np.maximum(var, 1e-12)) / 1.0
        i = int(np.argmax(cc)); lag = (i - L) / sr
        out.append({"bas": round(s / sr, 2), "ofset_kare": int(round(lag * (fps or 24))), "tepe": round(float(cc[i]), 3)})
    return out


# --- film bilgisi ---------------------------------------------------------------------------------------------------------
def kurgu_plani(film):
    for p in (os.path.join(film, "KURGU", "KURGU_PLANI.json"),):
        k = ortak.json_oku(p)
        if isinstance(k, dict): return k
    return None


def beklenen_sure(kp):
    if not kp: return None
    t = (kp.get("olcumler") or {}).get("toplam_sn")
    if isinstance(t, (int, float)) and t > 0: return float(t)
    son = [float(x.get("cizelge_bas") or 0) + float(x.get("sure") or 0) for alan in ("planlar", "kartlar", "karartmalar")
           for x in kp.get(alan) or [] if isinstance(x, dict)]
    return max(son) if son else None


def planli_araliklar(kp, tur):
    """tur: siyah | donma | sessizlik → [(bas, bit)] KURGU_PLANI'nda planlanmış olanlar."""
    if not kp: return []
    out = [(float(k.get("cizelge_bas") or 0), float(k.get("cizelge_bas") or 0) + float(k.get("sure") or 0))
           for k in kp.get("karartmalar") or [] if isinstance(k, dict)]
    if tur == "sessizlik":
        out += [(float(s.get("cizelge_bas") or 0), float(s.get("cizelge_bas") or 0) + float(s.get("sure") or 0))
                for s in kp.get("sessizlikler") or [] if isinstance(s, dict)]
    for p in kp.get("planlar") or []:
        t = ((p.get("goruntu") or {}).get("tur"))
        if (tur == "siyah" and t == "siyah") or (tur == "donma" and t in DURAGAN_TURLER):
            out.append((float(p.get("cizelge_bas") or 0), float(p.get("cizelge_bas") or 0) + float(p.get("sure") or 0)))
    if tur == "donma":
        out += [(float(k.get("cizelge_bas") or 0), float(k.get("cizelge_bas") or 0) + float(k.get("sure") or 0))
                for k in kp.get("kartlar") or [] if isinstance(k, dict) and not k.get("ust_uste")]
    return out


def planli_mi(ar, planli, pay=0.1):
    bas, bit = ar; uz = max(1e-6, bit - bas); kapsanan = 0.0
    for a, b in planli: kapsanan += max(0.0, min(bit, b + pay) - max(bas, a - pay))
    return kapsanan / uz >= 0.8


def kullanici_ses_duzenlemesi(film):
    t = ortak.json_oku(os.path.join(film, "KURGU", "TASLAK_FARK.json"), {}) or {}
    for g in t.get("geri_uretilemeyen") or []:
        metin = json.dumps(g, ensure_ascii=False).lower() if not isinstance(g, str) else g.lower()
        if any(k in metin for k in SES_KANALLARI): return True
    return bool(t.get("kullanici_ses_duzenlemesi"))


def yayin_dosyasi(film, verilen=None):
    if verilen: return verilen if os.path.isabs(verilen) else os.path.join(film, verilen)
    adaylar = [p for p in glob.glob(os.path.join(film, "YAYIN", "*_4K.mp4"))]
    return max(adaylar, key=os.path.getmtime) if adaylar else None


def master_dosyasi(film, verilen=None):
    if verilen: return verilen if os.path.isabs(verilen) else os.path.join(film, verilen)
    for p in (os.path.join(film, "YAYIN", "ses_master.wav"), os.path.join(film, "KURGU", "ses_master.wav")):
        if os.path.isfile(p): return p
    return None


# --- denetim ---------------------------------------------------------------------------------------------------------------
def m(madde, seviye, **k): return dict({"madde": madde, "seviye": seviye}, **k)


def ses_olcumleri(y):
    hedef, tol, tepe = esik("final_lufs"), esik("final_lufs_tolerans"), esik("true_peak_max_dbtp")
    if y is None: return [m("S8.1_lufs", "OLCULEMEDI", neden="ses ölçülemedi (ses akışı yok ya da ffmpeg yok)")]
    o = [m("S8.1_lufs", "GEC" if abs(y["lufs"] - hedef) <= tol else "HATA", olcu=round(y["lufs"], 2), esik=[hedef - tol, hedef + tol])]
    if y.get("tepe_dbtp") is None: o.append(m("S8.1_tepe", "OLCULEMEDI", neden="gerçek tepe okunamadı"))
    else: o.append(m("S8.1_tepe", "GEC" if y["tepe_dbtp"] <= tepe else "HATA", olcu=round(y["tepe_dbtp"], 2), esik=tepe))
    return o


def denetle(film, dosya, master=None, mux_yapildi=None):
    """(ölçümler, yayın doğrulama sözlüğü)."""
    kp = kurgu_plani(film); o = []
    dv = {"dosya": os.path.relpath(dosya, film).replace("\\", "/") if dosya else None, "kaynak": "capcut_disa_aktarim",
          "kurgu_plani_surumu": (kp or {}).get("kurgu_surumu") or (kp or {}).get("_surum")}
    if not dosya or not os.path.isfile(dosya):
        o.append(m("yayin_dosyasi", "HATA", neden="YAYIN/<FILM>_4K.mp4 yok", oneri="CapCut'tan 4K 24 fps dışa aktar"))
        return o, dv
    if not ffmpeg_var():
        o.append(m("olcum", "OLCULEMEDI", neden="ffmpeg/ffprobe yok (KUR1)")); return o, dv
    b = sure_fps(dosya)
    if not b or not b.get("video"):
        o.append(m("olcum", "OLCULEMEDI", neden="dosya medya olarak açılamadı (sahte deneme ya da bozuk dışa aktarım)")); return o, dv
    fps = (kp or {}).get("fps") or b["fps"] or 24
    bek = beklenen_sure(kp)
    if bek is None: o.append(m("sure", "OLCULEMEDI", neden="KURGU/KURGU_PLANI.json yok; çizelge süresi bilinmiyor"))
    else:
        fk = int(round(abs(b["sure"] - bek) * fps)); tol = esik("yayin_sure_tolerans_kare")
        o.append(m("sure", "GEC" if fk <= tol else "HATA", olcu=fk, esik=tol, kanit=f"ölçülen {b['sure']:.3f} sn, çizelge {bek:.3f} sn"))
    dv["sure"] = {"olculen": round(b["sure"], 3), "beklenen": bek, "fark_kare": None if bek is None else int(round(abs(b["sure"] - bek) * fps))}
    if (b.get("yukseklik") or 0) < 2160: o.append(m("cozunurluk", "BAYRAK", olcu=b.get("yukseklik"), esik=2160, oneri="4K dışa aktar"))
    if b.get("fps") and abs(b["fps"] - fps) > 0.01: o.append(m("fps", "BAYRAK", olcu=b["fps"], esik=fps))
    ar = araliklar(dosya, esik("mutlak_sessizlik_db"), video=True) if b["ses"] else dict(araliklar(dosya, video=True), sessizlik=[])
    kal = {}
    for tur in ("siyah", "donma"):
        pl = planli_araliklar(kp, tur); kal[tur] = [x for x in ar[tur] if not planli_mi(x, pl)]
        o.append(m(tur, "HATA" if kal[tur] else "GEC", olcu=len(kal[tur]), esik=0,
                   kanit=[f"{a:.2f}–{c:.2f}" for a, c in kal[tur][:10]] or None))
    pl = planli_araliklar(kp, "sessizlik")
    ses_kal = [x for x in ar["sessizlik"] if not planli_mi(x, pl)]
    uzun = [x for x in ses_kal if x[1] - x[0] > esik("mutlak_sessizlik_max_sn")]
    kal["sessizlik"] = ses_kal
    o.append(m("sessizlik_uzun", "HATA" if uzun else "GEC", olcu=len(uzun), esik=0, kanit=[f"{a:.2f}–{c:.2f}" for a, c in uzun[:10]] or None))
    o.append(m("sessizlik_sayisi", "HATA" if len(ses_kal) > esik("mutlak_sessizlik_film_max") else "GEC", olcu=len(ses_kal),
               esik=esik("mutlak_sessizlik_film_max")))
    dv["kalite"] = {"siyah": len(kal["siyah"]), "donma": len(kal["donma"]), "plansiz_sessizlik": len(ses_kal)}
    y = olc_yukseklik(dosya) if b["ses"] else None
    if not b["ses"]: o.append(m("ses_akisi", "HATA", neden="yayın dosyasında ses yok"))
    o += ses_olcumleri(y)
    dv["ses"] = y
    kses = kullanici_ses_duzenlemesi(film); dv["kullanici_ses_duzenlemesi"] = kses
    dv["taslak_fark_bos"] = not os.path.isfile(os.path.join(film, "KURGU", "TASLAK_FARK.json")) or not \
        (ortak.json_oku(os.path.join(film, "KURGU", "TASLAK_FARK.json"), {}) or {}).get("farklar")
    korel = None
    if master and os.path.isfile(master) and b["ses"]:
        korel = mux_korelasyon(dosya, master, fps)
        if korel is None: o.append(m("mux_korelasyon", "OLCULEMEDI", neden="numpy yok ya da master çözülemedi"))
        else:
            olc = [k for k in korel if "ofset_kare" in k]
            if not olc: o.append(m("mux_korelasyon", "OLCULEMEDI", neden="bütün pencereler sessiz"))
            else:
                mo = max(abs(k["ofset_kare"]) for k in olc); tp = min(k["tepe"] for k in olc)
                kotu = [k for k in olc if abs(k["ofset_kare"]) > esik("mux_ofset_max_kare") or k["tepe"] < esik("mux_korelasyon_min")]
                o.append(m("mux_korelasyon", "HATA" if kotu else "GEC", olcu={"ofset_max_kare": mo, "tepe_min": tp},
                           esik={"ofset_max_kare": esik("mux_ofset_max_kare"), "tepe_min": esik("mux_korelasyon_min")},
                           kanit=[f"{k['bas']} sn: ofset {k['ofset_kare']} kare, tepe {k['tepe']}" for k in kotu[:10]] or None))
                dv["ses_korelasyon"] = {"pencere": f"{len(korel)} pencere × {esik('mux_pencere').get('sure_sn')} sn",
                                        "ofset_kare": {"min": min(k["ofset_kare"] for k in olc), "max": max(k["ofset_kare"] for k in olc)},
                                        "tepe_min": tp, "atlanan": len(korel) - len(olc)}
    else:
        o.append(m("mux_korelasyon", "OLCULEMEDI", neden="ses_master.wav yok (son_miks --final); çizelge kanıtı kurulamadı"))
    dv["_korelasyon_gec"] = bool(korel) and not any(x["madde"] == "mux_korelasyon" and x["seviye"] != "GEC" for x in o)
    if mux_yapildi: o.append(m("S8.2_kullanici_sesi", "GEC" if (not kses or mux_yapildi == "dogrusal_kazanc") else "HATA",
                               olcu=mux_yapildi, neden="kullanıcı ses ayarı korunmalı (yeniden karıştırma yok)" if kses else None))
    return o, dv


def mux_gerekli(o): return any(x["madde"] in ("S8.1_lufs", "S8.1_tepe") and x["seviye"] == "HATA" for x in o)


def mux_karari(dv):
    """(tür, neden). Kanıt yoksa (None, neden)."""
    if dv.get("kullanici_ses_duzenlemesi"): return "dogrusal_kazanc", "kullanıcı CapCut'ta sesle oynadı: onun miksi korunur, tek kazanç"
    if dv.get("_korelasyon_gec"): return "master_stem", "çizelge kanıtı var (40 pencere ofset ≤ 1 kare)"
    return None, "mux kanıtı yok (master korelasyonu geçmedi ya da ölçülemedi)"


def son_miks_modulu():
    try:
        import son_miks
        return son_miks
    except Exception: return None


def dogrusal_kazanc(video, cikti, sm=None):
    """Tek doğrusal kazanç + gerçek tepe sınırlayıcı (son_miks.miksle; B15 tek miks kodu); görüntü kopyalanır. Hata metni ya da None."""
    sm = sm or son_miks_modulu()
    if sm is None: return "son_miks.py (PR-9) yok ya da açılamadı"
    import tempfile
    try:
        with tempfile.TemporaryDirectory(prefix="yz_kazanc_") as d:
            x, _ = sm.O.oku(video); y, _ = sm.miksle([(sm.O.stereo(x), 0.0)])
            wav = sm.O.yaz(os.path.join(d, "ses.wav"), y); sm.mux(video, wav, cikti)
        return None
    except Exception as e: return f"son_miks kazancı uygulanamadı: {e.__class__.__name__}: {e}"


def son_miks_mux(film, dosya, tur):
    """(yeni dosya, hata). master_stem: son_miks --final --mux (stemlerden master); dogrusal_kazanc: kullanıcının miksi + tek kazanç."""
    hedef = re.sub(r"_4K\.mp4$", "_4K_MUX.mp4", dosya) if dosya.endswith("_4K.mp4") else dosya[:-4] + "_MUX.mp4"
    if tur == "dogrusal_kazanc":
        e = dogrusal_kazanc(dosya, hedef)
        return (None, e) if e else (hedef, None)
    p = os.path.join(HERE, "son_miks.py")
    if not os.path.isfile(p): return None, "son_miks.py (PR-9) henüz yok"
    r = subprocess.run([sys.executable, p, "--final", "--film", film, "--mux", dosya, "--cikti", hedef], capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(hedef): return None, f"son_miks --final --mux çıkış {r.returncode}"
    return hedef, None


def final(film, dosya=None, master=None, g=None):
    g = g or gorev_baglami(); dosya = yayin_dosyasi(film, dosya); master = master_dosyasi(film, master)
    o, dv = denetle(film, dosya, master)
    dv["mux"] = {"tur": None, "yapildi": False, "gerekli": mux_gerekli(o)}
    if dv["mux"]["gerekli"]:
        tur, neden = mux_karari(dv); dv["mux"].update(tur=tur, neden=neden)
        if tur is None:
            o.append(m("mux_kaniti", "HATA", neden=neden, oneri="A16n: taslak farkı ve ses düzenlemesi incelenir (KR11)"))
        else:
            yeni, hata = son_miks_mux(film, dosya, tur)
            if hata: o.append(m("mux", "HATA", neden=hata, oneri="CapCut dışa aktarımını −14 LUFS hedefiyle yinele ya da son_miks kur"))
            else:
                o2, dv2 = denetle(film, yeni, master, mux_yapildi=tur)
                dv2["mux"] = dict(dv["mux"], yapildi=True, kaynak=dv["dosya"],
                                  sonra_lufs=(dv2.get("ses") or {}).get("lufs"), sonra_tepe_dbtp=(dv2.get("ses") or {}).get("tepe_dbtp"))
                o, dv = o2, dv2
    dv.pop("_korelasyon_gec", None)
    r = kapi.rapor_kur("S8", "FINAL", o, tur=g["tur_no"], asama=g["asama"], gorev=g["id"], arac_surum=SURUM)
    h = kapi.dogrula(r)
    if h: raise kapi.RaporHatasi(h)
    yol = os.path.join(film, g["rapor"]) if g.get("rapor") else os.path.join(film, "_RAPOR", f"S8_FINAL_t{g['tur_no']}.json")
    ortak.atomik_yaz(yol, r)
    dv.update({"_surum": 1, "_uretim": r["_uretim"], "sonuc": "HATA" if r["sonuc"] in ("HATA", "KISMI") else r["sonuc"],
               "hazir_degil_nedeni": "; ".join(f"{x['madde']}" + (f" ({x.get('neden')})" if x.get("neden") else "")
                                               for x in r["hatalar"]) or None,
               "rapor": os.path.relpath(yol, film).replace("\\", "/")})
    ortak.atomik_yaz(os.path.join(film, "YAYIN", "YAYIN_DOGRULAMA.json"), {"_surum": 1, "_uretim": dv.pop("_uretim"), **dv})
    print(f"S8 FINAL: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r['bayraklar'])} → {os.path.relpath(yol, film)}")
    return yol, r


def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def main(a):
    if "--final" not in a: print(__doc__); return ORTAM
    try:
        f = _arg(a, "--film")
        film = (os.path.abspath(f) if f and os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)) if f else None
        if not film or not os.path.isdir(film): print("!! --film <film> gerekli (klasör yok)"); return HATA
        final(film, _arg(a, "--dosya"), _arg(a, "--master"), gorev_baglami(_arg(a, "--tur")))
        return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
