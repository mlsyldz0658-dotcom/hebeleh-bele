"""KURGU ORTAK — video sonrası ses ve kurgu araçlarının (PR-12; TASARIM §9 adım 16) paylaştığı küçük yardımcılar.

Kodda:
  import kurgu_ortak as ko
  kok, argv = ko.film_ve_arg(sys.argv[1:])      film klasörü: ilk konumsal argüman (eski .bat/film.py v1) ya da --film <ad|yol>
  ko.saglayici_adi(argv)                         --saglayici <ad> | YZ_FILM_SAGLAYICI | None (gerçek zincir)
  ko.kare(x) · ko.KARE · ko.FPS                  1/24 sn'ye yuvarlama (bütün çizelge değerleri)
  ko.wav_oku(p) → (mono float32, sr) · ko.wav_yaz(p, a, sr=48000) · ko.yeniden_ornekle(a, sr, hedef)
  ko.lufs(a, sr) (BS.1770-4, kapılı; pyloudnorm varsa onu kullanır) · ko.kisa_max_lufs · ko.gercek_tepe_dbtp · ko.tepe_dbfs
  ko.zarf(a, sr, hz=100) · ko.ofset(x, y, max_kayma) → (kayma, korelasyon) · ko.f0_medyan(a, sr)
  ko.kareler_gri(video, w, h) (ffmpeg borusu; opencv gerekmez) · ko.video_sesi(video, sr) · ko.sure(video)
  ko.sahne_planlari(kok) → {no: plan} · ko.kurgu_plani(kok) → (yol, plan) · ko.kurgu_plani_yaz(kok, plan, cizelge)
  ko.diyalog_oku(kok) / ko.diyalog_yaz(kok, d) · ko.sha1(p) · ko.sahte_klip(...) (testler ve sahte sağlayıcı için)
Kurallar: yollar yalnız ortak.yollar() ve film klasöründen; yazım ortak.atomik_yaz; kapı raporları plan_ortak.rapor_yaz (kapi.py zarfı).
Ölçülemeyen her değer None döner; araçlar onu ÖLÇÜLEMEDİ (= BAYRAK) yazar, asla GEÇ değil.
"""
import os, sys, json, math, wave, glob, shutil, hashlib, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, plan_ortak as po

FPS = 24
KARE = 1.0 / FPS
SR = 48000
BITTI, HATA, KULLANICI, AJAN, ORTAM, BUTCE, KAPI, KISIT, BEKLE = range(9)
SESSIZ_DB = -120.0


# --- argümanlar ----------------------------------------------------------------------------------------------------
def film_ve_arg(argv):
    """(film_kok, kalan_argv). Film: --film <ad|yol> ya da ilk konumsal klasör (film.py v1 ve .bat'lar böyle çağırır).
    Film sahte açıldıysa (HAZIRLIK.json saglayici: sahte; film.py yeni --saglayici sahte) argv'ye --saglayici sahte eklenir."""
    kok, argv = _film_ve_arg(list(argv))
    if "--saglayici" not in argv and (ortak.json_oku(os.path.join(kok, "HAZIRLIK.json"), {}) or {}).get("saglayici") == "sahte":
        argv += ["--saglayici", "sahte"]
    return kok, argv


def _film_ve_arg(argv):
    if "--film" in argv:
        i = argv.index("--film"); f = argv[i + 1] if i + 1 < len(argv) else None
        del argv[i:i + 2]
        return po.film_kok(f), argv
    for i, a in enumerate(argv):
        if not a.startswith("--") and os.path.isdir(a):
            del argv[i]
            return os.path.abspath(a), argv
    env = os.environ.get("YZ_FILM_FILM")
    if env and os.path.isdir(env): return os.path.abspath(env), argv
    return po.film_kok(None), argv


def secenek(argv, ad, vars=None): return po.arg_al(argv, ad, vars)
def bayrak(argv, ad): return ad in argv


def saglayici_adi(argv):
    return secenek(argv, "--saglayici") or os.environ.get("YZ_FILM_SAGLAYICI") or None


def film_ayar():
    try: return ortak.json_oku(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {}) or {}
    except ortak.YolYok: return {}


def izin(ad):
    """FILM_AYAR.json izinler.<ad> (yalnız kullanıcının kendi izin panelinden; varsayılan kapalı)."""
    return bool((film_ayar().get("izinler") or {}).get(ad))


# --- zaman ---------------------------------------------------------------------------------------------------------
def kare(x):
    return None if x is None else round(round(float(x) * FPS) / FPS, 3)


def kare_farki(a, b): return abs(float(a) - float(b)) * FPS


def zaman_kodu(sn):
    sn = max(0.0, float(sn)); return f"{int(sn // 60):02d}:{sn % 60:04.1f}"


def srt_zaman(x):
    h, m = int(x // 3600), int(x % 3600 // 60); s = x % 60
    ms = int(round((s % 1) * 1000))
    if ms == 1000: s, ms = s + 1, 0
    return f"{h:02}:{m:02}:{int(s):02},{ms:03}"


# --- dosya ---------------------------------------------------------------------------------------------------------
def sha1(p, n=12):
    h = hashlib.sha1()
    try:
        with open(p, "rb") as f:
            for blok in iter(lambda: f.read(1 << 20), b""): h.update(blok)
    except OSError: return None
    return h.hexdigest()[:n]


def klasor_ozeti(klasor):
    """Klasördeki bütün dosyaların göreli yol + sha1 özeti (taslak kaynağının değişmediğini kanıtlamak için)."""
    h = hashlib.sha1()
    for kok, _, dosyalar in sorted(os.walk(klasor)):
        for d in sorted(dosyalar):
            p = os.path.join(kok, d)
            h.update(os.path.relpath(p, klasor).replace(os.sep, "/").encode()); h.update((sha1(p, 40) or "").encode())
    return h.hexdigest()[:12]


def goreli(kok, p):
    try: return os.path.relpath(p, kok).replace(os.sep, "/")
    except ValueError: return p


def mutlak(kok, p):
    if not p: return None
    return p if os.path.isabs(p) else os.path.join(kok, p.replace("/", os.sep))


def eskiye_tasi(kok, p):
    """Kalıcı silme yok: dosya/klasör <film>/_ESKI/<ad>_<n>'e taşınır. Yeni yolu döndürür."""
    hedef_k = os.path.join(kok, "_ESKI"); os.makedirs(hedef_k, exist_ok=True)
    ad = os.path.basename(os.path.normpath(p)); hedef = os.path.join(hedef_k, ad); n = 1
    while os.path.exists(hedef): hedef = os.path.join(hedef_k, f"{ad}_{n}"); n += 1
    shutil.move(p, hedef)
    return hedef


# --- ses (wave + numpy; soundfile gerekmez) ------------------------------------------------------------------------
def wav_oku(p, mono=True):
    with wave.open(p, "rb") as w:
        ch, sw, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        raw = w.readframes(n)
    if sw == 2: a = np.frombuffer(raw, "<i2").astype(np.float32) / 32768.0
    elif sw == 4: a = np.frombuffer(raw, "<i4").astype(np.float32) / 2147483648.0
    elif sw == 3:
        b = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(np.int32)
        v = b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16); v = np.where(v >= 1 << 23, v - (1 << 24), v)
        a = v.astype(np.float32) / float(1 << 23)
    elif sw == 1: a = (np.frombuffer(raw, np.uint8).astype(np.float32) - 128) / 128.0
    else: raise ValueError(f"desteklenmeyen örnek genişliği: {sw}")
    a = a.reshape(-1, ch) if ch > 1 else a
    if mono and a.ndim > 1: a = a.mean(axis=1)
    return a.astype(np.float32), sr


def wav_yaz(p, a, sr=SR):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    a = np.clip(np.asarray(a, np.float32), -1.0, 1.0)
    ch = 1 if a.ndim == 1 else a.shape[1]
    tmp = p + ".tmp.wav"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes((a * 32767).astype("<i2").tobytes())
    os.replace(tmp, p)
    return p


def yeniden_ornekle(a, sr, hedef=SR):
    if sr == hedef or len(a) == 0: return np.asarray(a, np.float32)
    n = int(round(len(a) * hedef / sr))
    return np.interp(np.linspace(0, len(a) - 1, n), np.arange(len(a)), a).astype(np.float32)


def db(x): return 20 * math.log10(max(float(x), 1e-12))
def kazanc(db_): return 10 ** (db_ / 20.0)


def _biquad(a, b, x):
    try:
        from scipy.signal import lfilter
        return lfilter(b, a, x)
    except Exception: pass
    y = np.zeros(len(x)); x1 = x2 = y1 = y2 = 0.0
    b0, b1, b2 = b; _, a1, a2 = a
    xs = x.tolist()
    for i, xv in enumerate(xs):
        yv = b0 * xv + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, xv, y1, yv; y[i] = yv
    return y


def _k_agirlik(x, sr):
    """BS.1770 K-ağırlığı (ön raf + RLB yüksek geçiren), çift doğrusal dönüşümle her örnekleme hızında."""
    f0, G, Q = 1681.974450955533, 3.999843853973347, 0.7071752369554196
    K = math.tan(math.pi * f0 / sr); Vh = 10 ** (G / 20); Vb = Vh ** 0.4996667741545416
    a0 = 1 + K / Q + K * K
    b = [(Vh + Vb * K / Q + K * K) / a0, 2 * (K * K - Vh) / a0, (Vh - Vb * K / Q + K * K) / a0]
    a = [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    y = _biquad(a, b, x)
    f0, Q = 38.13547087602444, 0.5003270373238773
    K = math.tan(math.pi * f0 / sr); a0 = 1 + K / Q + K * K
    a = [1.0, 2 * (K * K - 1) / a0, (1 - K / Q + K * K) / a0]
    return _biquad(a, [1.0, -2.0, 1.0], y)


def lufs(a, sr):
    """Bütünleşik yükseklik (LUFS), BS.1770-4: 400 ms blok, %75 bindirme, −70 LUFS mutlak ve −10 LU göreli kapı.
    pyloudnorm (MIT) kuruluysa onu kullanır. Çok kısa ya da sessiz girdi → SESSIZ_DB."""
    a = np.asarray(a, np.float64)
    if a.ndim > 1: a = a.mean(axis=1)
    if len(a) < int(0.4 * sr) or not np.any(a): return SESSIZ_DB
    try:
        import pyloudnorm
        v = pyloudnorm.Meter(sr).integrated_loudness(a)
        return SESSIZ_DB if not np.isfinite(v) else float(v)
    except Exception: pass
    y = _k_agirlik(a, sr); blok, adim = int(0.4 * sr), int(0.1 * sr)
    kare_ort = np.array([np.mean(y[i:i + blok] ** 2) for i in range(0, len(y) - blok + 1, adim)])
    l = -0.691 + 10 * np.log10(np.maximum(kare_ort, 1e-20))
    k = kare_ort[l > -70]
    if not len(k): return SESSIZ_DB
    goreli = -0.691 + 10 * math.log10(np.mean(k)) - 10
    k = kare_ort[(l > -70) & (l > goreli)]
    return float(-0.691 + 10 * math.log10(np.mean(k))) if len(k) else SESSIZ_DB


def kisa_max_lufs(a, sr):
    """0,4 sn'den kısa replik için en yüksek anlık (400 ms) yükseklik (S4.3)."""
    a = np.asarray(a, np.float64)
    if a.ndim > 1: a = a.mean(axis=1)
    if not np.any(a): return SESSIZ_DB
    y = _k_agirlik(a, sr); blok = int(0.4 * sr)
    if len(y) <= blok: return float(-0.691 + 10 * math.log10(max(np.mean(y ** 2), 1e-20)))
    c = np.cumsum(np.concatenate([[0.0], y ** 2])); m = (c[blok:] - c[:-blok]) / blok
    return float(-0.691 + 10 * math.log10(max(m.max(), 1e-20)))


def replik_lufs(a, sr):
    return kisa_max_lufs(a, sr) if len(a) < 0.4 * sr * 1.5 else lufs(a, sr)


def tepe_dbfs(a): return db(np.max(np.abs(a))) if len(a) else SESSIZ_DB


def gercek_tepe_dbtp(a, sr):
    """4× aşırı örneklemeyle gerçek tepe (FFT yeniden örnekleme; uzun girdide 10 sn'lik parçalar)."""
    a = np.asarray(a, np.float64)
    if a.ndim > 1: a = a.mean(axis=1)
    if not len(a): return SESSIZ_DB
    tepe, n = 0.0, int(10 * sr)
    for i in range(0, len(a), n):
        p = a[i:i + n]; L = len(p)
        if L < 4: tepe = max(tepe, float(np.max(np.abs(p)))); continue
        F = np.fft.rfft(p); G = np.zeros(4 * L // 2 + 1, complex); G[:len(F)] = F
        tepe = max(tepe, float(np.max(np.abs(np.fft.irfft(G, 4 * L) * 4))))
    return db(tepe)


def zarf(a, sr, hz=100):
    a = np.asarray(a, np.float64)
    if a.ndim > 1: a = a.mean(axis=1)
    n = max(1, int(sr / hz)); m = len(a) // n
    if m == 0: return np.zeros(0)
    return np.sqrt(np.mean(a[:m * n].reshape(m, n) ** 2, axis=1))


def ofset(x, y, max_kayma):
    """y'nin x'e göre gecikmesi (örnek sayısı; + = y geç) ve normalize korelasyon. Ölçülemezse (None, 0)."""
    x = np.asarray(x, np.float64); y = np.asarray(y, np.float64)
    n = min(len(x), len(y))
    if n < 4: return None, 0.0
    x = x[:n] - x[:n].mean(); y = y[:n] - y[:n].mean()
    if not np.any(x) or not np.any(y): return None, 0.0
    en_iyi, en_k = 0, -2.0
    for k in range(-max_kayma, max_kayma + 1):
        a, b = (x[:n - k], y[k:]) if k >= 0 else (x[-k:], y[:n + k])
        if len(a) < 4: continue
        s = float(np.sqrt(np.sum(a * a) * np.sum(b * b)))
        c = float(np.sum(a * b) / s) if s else 0.0
        if c > en_k: en_iyi, en_k = k, c
    return en_iyi, en_k


def f0_medyan(a, sr, alt=60.0, ust=400.0):
    """Özilinti ile F0 medyanı (Hz); sesli çerçeve yoksa None. Yalnız kaydırma büyüklüğü için (S2.7)."""
    a = np.asarray(a, np.float64); n = int(0.04 * sr); deger = []
    for i in range(0, len(a) - n, n):
        p = a[i:i + n] - a[i:i + n].mean()
        if np.sqrt(np.mean(p * p)) < 0.01: continue
        r = np.correlate(p, p, "full")[n - 1:]; lo, hi = int(sr / ust), min(int(sr / alt), n - 1)
        if hi <= lo: continue
        k = lo + int(np.argmax(r[lo:hi]))
        if r[k] > 0.3 * r[0]: deger.append(sr / k)
    return float(np.median(deger)) if deger else None


def yarim_ton(f_hedef, f_kaynak):
    if not f_hedef or not f_kaynak: return None
    return int(round(12 * math.log2(f_hedef / f_kaynak)))


def yumusat(a, sr, ms=15):
    """Parça başı ve sonunda tık önleyici rampa (S5.10: 10–20 ms)."""
    a = np.array(a, np.float32); n = min(int(sr * ms / 1000), len(a) // 2)
    if n > 0:
        r = np.linspace(0, 1, n, dtype=np.float32); a[:n] *= r; a[-n:] *= r[::-1]
    return a


def stem_ekle(stem, parca, sr, bas_sn, kazanc_=1.0):
    i = int(round(bas_sn * sr))
    if i < 0: parca = parca[-i:]; i = 0
    j = min(len(stem), i + len(parca))
    if j > i: stem[i:j] += parca[:j - i] * kazanc_
    return stem


def pencere(a, sr, bas, bit):
    i, j = max(0, int(bas * sr)), max(0, int(bit * sr)); return a[i:j]


# --- ffmpeg --------------------------------------------------------------------------------------------------------
def ffmpeg_var(): return shutil.which("ffmpeg") is not None and shutil.which("ffprobe") is not None


def sure(p):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                           capture_output=True, text=True, timeout=60)
        return float(r.stdout.strip())
    except Exception: return None


def kareler_gri(p, w=160, h=90, fps=FPS, bas=None, sure_=None):
    """Videoyu fps'te w×h gri kareler dizisine çevirir: ndarray (n, h, w) uint8. ffmpeg yoksa ya da okunamazsa None."""
    if not ffmpeg_var() or not os.path.exists(p): return None
    k = ["ffmpeg", "-v", "error"] + (["-ss", str(bas)] if bas else []) + ["-i", p] + (["-t", str(sure_)] if sure_ else []) + \
        ["-vf", f"fps={fps},scale={w}:{h}:flags=area,format=gray", "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    r = subprocess.run(k, capture_output=True, timeout=600)
    if r.returncode or not r.stdout: return None
    v = np.frombuffer(r.stdout, np.uint8); n = len(v) // (w * h)
    return v[:n * w * h].reshape(n, h, w)


def kare_rgb(p, t, w=320, h=180):
    if not ffmpeg_var(): return None
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t):.3f}", "-i", p, "-frames:v", "1", "-vf", f"scale={w}:{h}",
                        "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True, timeout=120)
    if r.returncode or len(r.stdout) < w * h * 3: return None
    return np.frombuffer(r.stdout[:w * h * 3], np.uint8).reshape(h, w, 3)


def video_sesi(p, sr=SR):
    """Klibin sesi (mono float32). Ses yoksa ya da okunamazsa None."""
    if not ffmpeg_var() or not os.path.exists(p): return None
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-vn", "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                       capture_output=True, timeout=600)
    if r.returncode or not r.stdout: return None
    return np.frombuffer(r.stdout, "<i2").astype(np.float32) / 32768.0


def ffmpeg(*args, timeout=3600):
    r = subprocess.run(["ffmpeg", "-v", "error", "-y"] + [str(a) for a in args], capture_output=True, text=True, timeout=timeout)
    if r.returncode: raise RuntimeError("ffmpeg: " + (r.stderr or "")[-400:])


def sahte_klip(yol, sure_=8.0, w=320, h=180, kutu=(), ton=(), sr=SR, ton_hz=220.0, gurultu=0.0, renk=60):
    """Test/sahte klip: kutu=[(bas, bit), …] aralıklarında soldan sağa kayan beyaz kutu (öncesinde durağan);
    ton=[(bas, bit), …] aralıklarında konuşma benzeri genlik kipli ton. ffmpeg ile mp4 (rawvideo borusu)."""
    n = int(round(sure_ * FPS)); kareler = np.full((n, h, w, 3), renk, np.uint8)
    bw, bh = max(8, w // 10), max(8, h // 5); y0 = h // 2 - bh // 2
    for i in range(n):
        t = i / FPS; x = 10
        for (a, b) in kutu:
            if t >= b: x += int((w - bw - 20) * 0.5)
            elif t >= a: x += int((w - bw - 20) * 0.5 * (t - a) / max(b - a, 1e-6))
        x = min(x, w - bw - 1)
        kareler[i, y0:y0 + bh, x:x + bw] = 235
    tmp_v = yol + ".v.raw"; tmp_a = yol + ".a.wav"
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    kareler.tofile(tmp_v)
    t = np.arange(int(sure_ * sr)) / sr; a = np.zeros_like(t)
    for (b0, b1) in ton:
        m = (t >= b0) & (t < b1)
        zarf_ = 0.5 + 0.3 * np.sin(2 * np.pi * 2.3 * t[m]) + 0.2 * np.sin(2 * np.pi * 5.9 * t[m] + 1.0)   # hece benzeri, dönemsiz
        a[m] += 0.25 * np.sin(2 * np.pi * ton_hz * t[m]) * np.clip(zarf_, 0.05, 1.0)
    if gurultu: a += gurultu * np.random.default_rng(1).standard_normal(len(a))
    wav_yaz(tmp_a, a, sr)
    try:
        ffmpeg("-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", FPS, "-i", tmp_v, "-i", tmp_a,
               "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-g", "1", "-c:a", "aac", "-b:a", "128k",
               "-shortest", yol)
    finally:
        for f in (tmp_v, tmp_a):
            if os.path.exists(f): os.remove(f)        # yalnız bu fonksiyonun yazdığı geçici dosyalar
    return yol


# --- film dosyaları ------------------------------------------------------------------------------------------------
def sahneler(kok): return ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}


def sahne_planlari(kok, s=None):
    s = s if s is not None else sahneler(kok)
    return {p.get("no"): p for p in s.get("sahneler") or [] if isinstance(p, dict)}


def zanaat(p): return p.get("zanaat") or {}


def kirpma_onceligi(p):
    k = (p.get("kurgu") or {}).get("kirpma_onceligi")
    if k: return k
    t = zanaat(p).get("plan_tipi") or ""
    return {"diyalog": "replik", "eylem": "eylem", "aksiyon": "eylem", "ekleme": "eylem", "tepki": "tepki_tepesi",
            "duygu_tutma": "tepki_tepesi", "kurulus": "durgun", "gecis": "durgun", "kart": "durgun"}.get(t, "eylem")


def klip_yolu(kok, no, dosya=None):
    if dosya: return mutlak(kok, dosya)
    for ad in (f"{int(no):03d}.mp4", f"{no}.mp4"):
        p = os.path.join(kok, "SIRALI_VIDEO", ad)
        if os.path.exists(p): return p
    return os.path.join(kok, "SIRALI_VIDEO", f"{int(no):03d}.mp4")


def surum_klasoru(kok): return os.path.join(kok, "KURGU", "surumler")


def kurgu_plani(kok, cizelge=None):
    """(yol, plan) — en yüksek sürümlü KURGU_PLANI_<T>_v<N>.json (cizelge verilirse yalnız o); yoksa KURGU/KURGU_PLANI.json."""
    aday = []
    for p in glob.glob(os.path.join(surum_klasoru(kok), "KURGU_PLANI_*_v*.json")):
        ad = os.path.basename(p)[len("KURGU_PLANI_"):-5]
        t, _, n = ad.rpartition("_v")
        if n.isdigit() and (cizelge is None or t == cizelge): aday.append((int(n), t, p))
    if aday:
        _, _, p = max(aday); return p, ortak.json_oku(p, {}) or {}
    p = os.path.join(kok, "KURGU", "KURGU_PLANI.json")
    v = ortak.json_oku(p)
    if isinstance(v, dict) and (cizelge is None or v.get("cizelge") == cizelge): return p, v
    return None, None


def sonraki_surum(kok):
    n = 0
    for p in glob.glob(os.path.join(surum_klasoru(kok), "KURGU_PLANI_*_v*.json")):
        s = os.path.basename(p)[:-5].rpartition("_v")[2]
        if s.isdigit(): n = max(n, int(s))
    _, kp = kurgu_plani(kok)
    if kp: n = max(n, int(kp.get("kurgu_surumu") or kp.get("_surum") or 0))
    return n + 1


def kurgu_plani_yaz(kok, plan, cizelge="T2"):
    """Yeni sürüm: KURGU/surumler/KURGU_PLANI_<T>_v<N>.json + KURGU/KURGU_PLANI.json (son sürümün kopyası). Eski sürüm bozulmaz."""
    n = int(plan.get("kurgu_surumu") or sonraki_surum(kok))
    plan["kurgu_surumu"] = n; plan["_surum"] = n; plan["cizelge"] = cizelge
    yol = os.path.join(surum_klasoru(kok), f"KURGU_PLANI_{cizelge}_v{n}.json")
    ortak.atomik_yaz(yol, plan); ortak.atomik_yaz(os.path.join(kok, "KURGU", "KURGU_PLANI.json"), plan)
    return yol


def plan_imza(plan):
    return po.imza({k: plan.get(k) for k in ("planlar", "diyalog", "kartlar", "karartmalar")})


def plan_bul(kp, no):
    return next((x for x in kp.get("planlar") or [] if x.get("plan") == no), None)


def plan_sonu(x): return float(x["cizelge_bas"]) + float(x["sure"])


def plan_at(kp, t):
    """Çizelgede t anındaki plan girdisi."""
    for x in kp.get("planlar") or []:
        if float(x["cizelge_bas"]) - 1e-6 <= t < plan_sonu(x) - 1e-6: return x
    return None


def toplam_sure(kp):
    ps = kp.get("planlar") or []
    return round(max([plan_sonu(x) for x in ps] or [0.0]), 3)


def klip_zamanina(x, t):
    """Çizelge anı t → planın klibindeki an."""
    g = x["goruntu"]; return float(g["kullanim"]["bas"]) + (t - float(x["cizelge_bas"])) * float(g.get("hiz") or 1.0)


def cizelge_zamanina(x, klip_t):
    g = x["goruntu"]; return float(x["cizelge_bas"]) + (klip_t - float(g["kullanim"]["bas"])) / float(g.get("hiz") or 1.0)


def diyalog_oku(kok):
    d = ortak.json_oku(os.path.join(kok, "SESLER", "diyalog.json"), {}) or {}
    if not isinstance(d.get("replikler"), dict): d["replikler"] = {}
    return d


def diyalog_yaz(kok, d):
    d.setdefault("surum", 2); d.setdefault("ornekleme_hz", SR)
    ortak.atomik_yaz(os.path.join(kok, "SESLER", "diyalog.json"), d)


def replik_dosyasi(kok, r, tercih=("esit", "dosya")):
    """Replik için kullanılacak ses dosyası: eşitlenmiş > dönüşmüş/son > tts."""
    for a in tercih:
        p = r.get("dosya_esit") if a == "esit" else r.get(a)
        if p and os.path.exists(mutlak(kok, p)): return mutlak(kok, p)
    t = (r.get("tts") or {}).get("dosya")
    if t and os.path.exists(mutlak(kok, t)): return mutlak(kok, t)
    return None


def ses_cizelgesi(kok): return ortak.json_oku(os.path.join(kok, "KURGU", "SES_CIZELGESI.json"), {}) or {}


def ses_cizelgesi_yaz(kok, d, kp_yol, kp):
    st = dict(d.get("stemler") or {})
    for ad in ("diyalog", "efekt", "ambiyans", "muzik"):
        if os.path.exists(stem_yolu(kok, ad)): st[ad] = goreli(kok, stem_yolu(kok, ad))
    d["stemler"] = st; d.setdefault("stem_kazanc_db", {a: 0.0 for a in st})
    d.update(surum=1, cizelge=kp.get("cizelge", "T2"), fps=FPS,
             kurgu_plani={"dosya": goreli(kok, kp_yol) if kp_yol else None, "imza": plan_imza(kp), "surum": kp.get("kurgu_surumu")})
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "SES_CIZELGESI.json"), d)


def stem_yolu(kok, ad): return os.path.join(kok, "KURGU", "STEMS", f"{ad}.wav")


def rapor_klasoru(kok): return os.path.join(kok, "_RAPOR")


def son_rapor(kok, kapi_kodu):
    """_RAPOR/'daki o kapının en yeni geçerli raporu (yol, rapor) ya da (None, None)."""
    import kapi
    rs = kapi.raporlar(rapor_klasoru(kok), kapi_kodu)
    if not rs: return None, None
    return max(rs, key=lambda x: (x[1]["_uretim"].get("zaman") or "", x[0]))


def kapsam_surum(kp): return f"v{int((kp or {}).get('kurgu_surumu') or 1)}"


def rapor(kok, kapi_kodu, kapsam, olcumler, asama, arac, birimler=None, ek=None, kuyruk=None, girdi_imza=None):
    yol, r = po.rapor_yaz(kok, kapi_kodu, kapsam, olcumler, asama=asama, arac=arac, birimler=birimler, ek=ek, kuyruk=kuyruk,
                          varsayilan=os.path.join("_RAPOR", f"{kapi_kodu}_{kapsam}.json"), girdi_imza=girdi_imza)
    po.yaz_ozet(r, os.path.basename(yol))
    return yol, r


def m(madde, seviye, plan=None, **ek): return po.m(madde, seviye, plan, **ek)


def esik(ad, vars=None):
    v = po.esik().get(ad)
    return vars if v is None else v


def olc_seviye(deger, gec_max, bayrak_max=None):
    """|değer| ≤ gec_max → GEC; ≤ bayrak_max → BAYRAK; aksi HATA; değer None → OLCULEMEDI."""
    if deger is None: return "OLCULEMEDI"
    d = abs(deger)
    if d <= gec_max: return "GEC"
    if bayrak_max is not None and d <= bayrak_max: return "BAYRAK"
    return "HATA"


def bilgi(*a): print(*a, flush=True)


# --- sağlayıcılar --------------------------------------------------------------------------------------------------
# saglayicilar/__init__.py KAYIT'ında henüz olmayan adlar (paylasilan_istekler: KAYIT satırları); KAYIT'taki ad her zaman önce gelir.
YEREL_KAYIT = {"openvoice": "saglayicilar.yerel_ses.OpenVoice", "chatterbox": "saglayicilar.yerel_ses.Chatterbox",
               "rvc": "saglayicilar.yerel_ses.RVC", "roformer": "saglayicilar.yerel_ses.Roformer",
               "demucs": "saglayicilar.yerel_ses.Demucs", "faster_whisper": "saglayicilar.yerel_ses.FasterWhisper",
               "musetalk": "saglayicilar.yerel_ses.MuseTalk", "yz_buyutucu": "saglayicilar.buyutucu.YZBuyutucu",
               "lanczos": "saglayicilar.buyutucu.Lanczos", "sahte_kurgu": "saglayicilar.sahte_kurgu.SahteKurgu"}
TEST_SAGLAYICILARI = ("sahte", "kaset", "sahte_bozuk")
TUR_YONTEM = {"ayristirma": "ayristir", "asr": "asr", "ses_donustur": "ses_donustur", "dudak": "dudak", "buyutme": "buyut",
              "agiz": "agiz_dizisi", "yuz_kimligi": "yuz_kimligi", "dinleyici": "dinleyici"}


def _yukle(ad):
    import importlib, saglayicilar
    if ad == "sahte": ad = "sahte_kurgu"
    yol = YEREL_KAYIT.get(ad) if ad in YEREL_KAYIT else saglayicilar.KAYIT.get(ad)
    if not yol: return None
    mod, sinif = yol.rsplit(".", 1)
    return getattr(importlib.import_module(mod), sinif)()


def zincir(tur, argv=(), log=None):
    """Bu tür için hazır sağlayıcılar (sırayla). --saglayici sahte → yalnız sahte. Dışlananlar (ADLAR saglayici_dislanan) hiç yüklenmez.
    Zincir: FILM_AYAR.json saglayici_zinciri.<tur> ya da ADLAR saglayici_turleri.<tur>; test sağlayıcıları gerçek zincirde atlanır."""
    import kapi
    ad = saglayici_adi(list(argv))
    dis = set(kapi.adlar().get("saglayici_dislanan") or [])
    if ad: adlar = [ad]
    else:
        adlar = ((film_ayar().get("saglayici_zinciri") or {}).get(tur) or (kapi.adlar().get("saglayici_turleri") or {}).get(tur)
                 or [])
        adlar = [a for a in adlar if a not in TEST_SAGLAYICILARI]
    out, yontem = [], TUR_YONTEM.get(tur, tur)
    for a in adlar:
        if a in dis: continue
        try: s = _yukle(a)
        except Exception as e:
            if log: log(f"   [{a}] yüklenemedi: {e.__class__.__name__}")
            continue
        if s is None or not hasattr(s, yontem): continue
        if tur not in getattr(s, "turler", ()) and not (tur in ("agiz", "yuz_kimligi") and hasattr(s, yontem)): continue
        ok, neden = s.hazir()
        if ok: out.append(s)
        elif log: log(f"   [{a}] {tur} için hazır değil: {neden}")
    return out


def cagir(tur, argv, *a, **k):
    """Zincirdeki ilk başarılı sağlayıcının sonucu: (sonuc, saglayici_adi). Yalnız GECILEBILIR kodlarda sıradakine geçilir;
    hiçbiri yoksa (None, None) — çağıran ÖLÇÜLEMEDİ yazar."""
    from saglayicilar import Kisitlandi
    for s in zincir(tur, argv):
        try: return getattr(s, TUR_YONTEM.get(tur, tur))(*a, **k), s.ad
        except Kisitlandi as e:
            if not e.gecilebilir: raise
    return None, None
