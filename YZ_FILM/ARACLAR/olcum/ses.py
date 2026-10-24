"""OLCUM/SES — ses sinyali ölçüleri (TASARIM §6.5 `olcum/` paketi, §6.6, §7.2 S1–S8; [SM2] §4.6.2).

Kodda:
  from olcum import ses as O
  x, sr = O.oku(yol)                      wav → float32 dizi (n,) ya da (n, k), 48 kHz'e yeniden örneklenir (ffmpeg varsa her biçim)
  O.yaz(yol, x, sr=48000)                 16-bit PCM wav (atomik)
  O.lufs(x, sr)                           bütünleşik yükseklik (BS.1770-4, mutlak −70 ve göreli −10 kapı); 0,4 sn'den kısa sinyalde
                                          en yüksek anlık değer (S4.3). pyloudnorm (MIT) kuruluysa o, yoksa aynı formülün yerel numpy hâli
  O.anlik_max(x, sr) · O.kisa_sureli(x, sr) → [(t, LUFS)] · O.lra(x, sr)
  O.gercek_tepe(x, sr) → dBTP (4× aşırı örnekleme) · O.ornek_tepe(x) → dBFS · O.kirpilma(x) → örnek sayısı
  O.sessizlikler(x, sr, esik_db=-50, en_az_sn=0.3) → [(bas, bit)] (ffmpeg silencedetect gibi örnek genliği)
  O.bosluklar(x, sr, esik_db=-60, pencere_sn=0.1) → [(bas, bit)] (S5.2: 100 ms pencerede RMS)
  O.f0(x, sr) → {medyan_hz, p10_hz, p90_hz, sesli_oran} · O.yarim_ton(f1, f2)
  O.gomme(x, sr) → vektör (yedek yöntem: log-mel ortalama + F0; gerçek konuşmacı gömmesi P1, ayrı model) · O.benzerlik(a, b)
  O.zarf(x, sr) · O.zarf_gecikme_ms(a, b, sr) · O.onsetler(x, sr) · O.bpm(x, sr) · O.kroma(x, sr) → (12, T) · O.ton(x, sr)
  O.kroma_benzerlik(sablon, aday) · O.wer(referans, hipotez) · O.spektral_genislik · O.dinamik_aralik · O.stereo_genislik
  O.mono_fark_lu(x, sr) · O.faz_korelasyonu(x) · O.mos_tahmin(yol) (lisans doğrulanmadıysa ÖLÇÜLEMEDİ)
  O.kontrol(film=None) → ses ortamı kartı (A10a; eksik ortam yalnız kendi basamağını kapatır)
Komut satırı:
  python olcum/ses.py --kontrol [--film <film>]     → <film>/_RAPOR/S_KURULUM.json (film verilirse) + özet
  python olcum/ses.py --olc <wav> [--json]          → yükseklik, tepe, LRA, sessizlik, F0 özeti
Kural: ÖLÇÜLEMEDİ asla GEÇ değildir; ölçemeyen işlev None ya da {"olculemedi": true, "neden"} döndürür.
Çıkış kodları: 0 tamam · 1 dosya okunamadı · 4 kullanım.
"""
import os, sys, json, wave, math, shutil, subprocess, importlib, importlib.util, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import numpy as np
import ortak

SURUM = "olcum.ses 1.0"
SR = 48000
_EPS = 1e-12


# --- dosya ----------------------------------------------------------------------------------------------------------
def _pcm_oku(yol):
    with wave.open(yol, "rb") as w:
        k, g, sr, n = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
        ham = w.readframes(n)
    if g == 2: a = np.frombuffer(ham, "<i2").astype(np.float32) / 32768.0
    elif g == 4: a = np.frombuffer(ham, "<i4").astype(np.float32) / 2147483648.0
    elif g == 1: a = (np.frombuffer(ham, np.uint8).astype(np.float32) - 128.0) / 128.0
    elif g == 3:
        b = np.frombuffer(ham, np.uint8).reshape(-1, 3).astype(np.int32)
        a = ((b[:, 0] | (b[:, 1] << 8) | (b[:, 2] << 16)) << 8 >> 8).astype(np.float32) / 8388608.0
    else: raise ValueError(f"desteklenmeyen örnek genişliği: {g}")
    return (a.reshape(-1, k) if k > 1 else a), sr


def yeniden_ornekle(x, sr, hedef=SR):
    if sr == hedef or len(x) == 0: return x
    n = int(round(len(x) * hedef / sr)); t = np.linspace(0, len(x) - 1, n)
    if x.ndim == 1: return np.interp(t, np.arange(len(x)), x).astype(np.float32)
    return np.stack([np.interp(t, np.arange(len(x)), x[:, i]) for i in range(x.shape[1])], 1).astype(np.float32)


def oku(yol, sr=SR):
    """wav (ya da ffmpeg varsa her ses/video dosyası) → (float32 dizi, sr)."""
    try: x, s = _pcm_oku(yol)
    except (wave.Error, EOFError, ValueError):
        if not shutil.which("ffmpeg"): raise
        r = subprocess.run(["ffmpeg", "-v", "error", "-i", yol, "-vn", "-f", "f32le", "-acodec", "pcm_f32le", "-ar", str(sr), "-"],
                           capture_output=True, check=True)
        x = np.frombuffer(r.stdout, "<f4").astype(np.float32); s = sr
        k = _kanal_say(yol)
        if k > 1: x = x[: len(x) // k * k].reshape(-1, k)
    return (yeniden_ornekle(x, s, sr) if sr else x), (sr or s)


def _kanal_say(yol):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=channels", "-of", "csv=p=0", yol],
                           capture_output=True, text=True)
        return int((r.stdout or "1").strip().splitlines()[0])
    except Exception: return 1


def yaz(yol, x, sr=SR):
    x = np.asarray(x, dtype=np.float32)
    a = (np.clip(x, -1.0, 1.0) * 32767.0).round().astype("<i2")
    k = 1 if a.ndim == 1 else a.shape[1]
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    tmp = yol + ".tmp"
    with wave.open(tmp, "wb") as w:
        w.setnchannels(k); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.tobytes())
    os.replace(tmp, yol)
    return yol


def sure(x, sr=SR): return len(x) / float(sr)
def mono(x): return x if x.ndim == 1 else x.mean(axis=1)
def stereo(x): return np.stack([x, x], 1) if x.ndim == 1 else (x if x.shape[1] == 2 else np.stack([x[:, 0], x[:, -1]], 1))
def db(v): return 20.0 * math.log10(max(float(v), _EPS))
def kazanc(db_): return 10.0 ** (db_ / 20.0)


# --- K ağırlığı ve yükseklik (BS.1770-4) --------------------------------------------------------------------------------
def _biquad(fs):
    if fs == 48000:
        return ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585],
                [1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])
    G, Q, fc = 3.99984385397, 0.7071752369554193, 1681.9744509555319          # libebur128 sabitleri
    A = 10 ** (G / 40.0); w = 2 * math.pi * fc / fs; al = math.sin(w) / (2 * Q); c = math.cos(w); sA = math.sqrt(A)
    b1 = [A * ((A + 1) + (A - 1) * c + 2 * sA * al), -2 * A * ((A - 1) + (A + 1) * c), A * ((A + 1) + (A - 1) * c - 2 * sA * al)]
    a1 = [(A + 1) - (A - 1) * c + 2 * sA * al, 2 * ((A - 1) - (A + 1) * c), (A + 1) - (A - 1) * c - 2 * sA * al]
    Q2, fc2 = 0.5003270373253953, 38.13547087613982
    w = 2 * math.pi * fc2 / fs; al = math.sin(w) / (2 * Q2); c = math.cos(w)
    b2 = [(1 + c) / 2, -(1 + c), (1 + c) / 2]; a2 = [1 + al, -2 * c, 1 - al]
    return [v / a1[0] for v in b1], [v / a1[0] for v in a1], [v / a2[0] for v in b2], [v / a2[0] for v in a2]


_H = {}


def _yanit(n, fs, sos):
    """İki kutuplu süzgeç(ler)in rfft ızgarasındaki frekans yanıtı (önbellekli)."""
    k = (n, fs, len(sos))
    if k not in _H:
        z = np.exp(-1j * np.pi * np.arange(n // 2 + 1) / (n // 2)); H = np.ones(n // 2 + 1, dtype=complex)
        for b, a in sos: H *= (b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)
        if len(_H) > 8: _H.clear()
        _H[k] = H
    return _H[k]


def _iir_fft(x, sos, fs):
    """Süzgeçleri frekans yanıtıyla uygular (numpy; scipy gerekmez). Kuyruk sönümü ≪ 1 sn; bloklar 1 sn ön payla."""
    blok, on = 30 * fs, fs
    out = np.empty(len(x), dtype=np.float64)
    for s in range(0, len(x), blok):
        p0 = max(0, s - on); seg = x[p0:s + blok].astype(np.float64)
        n = 1 << int(math.ceil(math.log2(len(seg) + fs // 2)))
        y = np.fft.irfft(np.fft.rfft(seg, n) * _yanit(n, fs, sos), n)[:len(seg)]
        out[s:s + blok] = y[s - p0:]
    return out


def k_agirlik(x, fs=SR):
    b1, a1, b2, a2 = _biquad(fs); sos = ((b1, a1), (b2, a2))
    ch = [x] if x.ndim == 1 else [x[:, i] for i in range(x.shape[1])]
    return [_iir_fft(c, sos, fs) for c in ch]


def _blok_guc(y, fs, pencere=0.4, adim=0.1):
    """Kanal başına K ağırlıklı sinyallerden pencere ortalama kare toplamı (kanal ağırlığı 1: mono/stereo)."""
    n, h = int(pencere * fs), int(adim * fs)
    if len(y[0]) < n: return np.array([sum(float(np.mean(c ** 2)) if len(c) else 0.0 for c in y)])
    kum = [np.concatenate([[0.0], np.cumsum(c ** 2)]) for c in y]
    bas = np.arange(0, len(y[0]) - n + 1, h)
    return sum((k[bas + n] - k[bas]) / n for k in kum)


def _lk(z): return -0.691 + 10.0 * np.log10(np.maximum(z, _EPS))


def _pyln():
    try: return importlib.import_module("pyloudnorm")
    except Exception: return None


def lufs(x, sr=SR):
    """Bütünleşik yükseklik (LUFS). Sessiz sinyal → -inf yerine -70. 0,4 sn'den kısa: anlık en yüksek (S4.3)."""
    x = np.asarray(x, dtype=np.float32)
    if len(x) == 0: return -70.0
    if len(x) < int(0.4 * sr): return anlik_max(x, sr)
    pl = _pyln()
    if pl is not None:
        try:
            v = float(pl.Meter(sr).integrated_loudness(x.astype(np.float64)))
            return v if math.isfinite(v) else -70.0
        except Exception: pass
    z = _blok_guc(k_agirlik(x, sr), sr)
    l = _lk(z); z1 = z[l > -70.0]
    if not len(z1): return -70.0
    g = _lk(np.mean(z1)) - 10.0
    z2 = z[(l > -70.0) & (l > g)]
    return float(_lk(np.mean(z2))) if len(z2) else -70.0


def anlik_max(x, sr=SR):
    z = _blok_guc(k_agirlik(np.asarray(x, dtype=np.float32), sr), sr, 0.4, 0.1)
    return float(max(-70.0, float(np.max(_lk(z))))) if len(z) else -70.0


def kisa_sureli(x, sr=SR, adim=1.0):
    z = _blok_guc(k_agirlik(np.asarray(x, dtype=np.float32), sr), sr, 3.0, adim)
    return [(round(i * adim, 3), float(v)) for i, v in enumerate(_lk(z))]


def lra(x, sr=SR):
    """Yükseklik aralığı (EBU Tech 3342: 3 sn pencere, −70 mutlak, −20 göreli kapı; P95 − P10)."""
    z = _blok_guc(k_agirlik(np.asarray(x, dtype=np.float32), sr), sr, 3.0, 0.1)
    l = _lk(z); z1 = z[l > -70.0]
    if len(z1) < 2: return 0.0
    g = _lk(np.mean(z1)) - 20.0; l2 = l[(l > -70.0) & (l > g)]
    return float(np.percentile(l2, 95) - np.percentile(l2, 10)) if len(l2) > 1 else 0.0


def ornek_tepe(x): return db(np.max(np.abs(x))) if len(x) else -120.0
def kirpilma(x, esik=0.9999): return int(np.sum(np.abs(np.asarray(x)) >= esik))


def asiri_ornekle(c, kat=4, blok=1 << 16, pay=256):
    """Tek kanalı FFT ile kat× aşırı örnekler (bloklu, kenar paylı)."""
    out = []
    for s in range(0, len(c), blok):
        p0, p1 = max(0, s - pay), min(len(c), s + blok + pay)
        seg = c[p0:p1].astype(np.float64); n = len(seg)
        if n < 2: out.append(np.repeat(seg, kat)); continue
        X = np.fft.rfft(seg); Y = np.zeros(n * kat // 2 + 1, dtype=complex); Y[:len(X)] = X
        y = np.fft.irfft(Y, n * kat) * kat
        out.append(y[(s - p0) * kat:(s - p0 + min(blok, len(c) - s)) * kat])
    return np.concatenate(out) if out else np.zeros(0)


def gercek_tepe(x, sr=SR):
    x = np.asarray(x, dtype=np.float32)
    if not len(x): return -120.0
    ch = [x] if x.ndim == 1 else [x[:, i] for i in range(x.shape[1])]
    return db(max(float(np.max(np.abs(asiri_ornekle(c)))) for c in ch))


def _cerceve_max(x, sr, cerceve_sn):
    m = np.abs(mono(x)) if x.ndim == 1 else np.max(np.abs(x), axis=1)
    n = max(1, int(cerceve_sn * sr)); k = len(m) // n
    return (m[:k * n].reshape(k, n).max(axis=1) if k else np.zeros(0)), n


def _araliklar(maske, adim_sn, en_az_sn):
    out, bas = [], None
    for i, v in enumerate(list(maske) + [False]):
        if v and bas is None: bas = i
        elif not v and bas is not None:
            if (i - bas) * adim_sn >= en_az_sn - 1e-9: out.append((round(bas * adim_sn, 3), round(i * adim_sn, 3)))
            bas = None
    return out


def sessizlikler(x, sr=SR, esik_db=-50.0, en_az_sn=0.3):
    """Örnek genliği esik_db altında kalan en az en_az_sn'lik aralıklar (S7.4; ffmpeg silencedetect n/d anlamı)."""
    m, n = _cerceve_max(np.asarray(x), sr, 0.01)
    return _araliklar(m < kazanc(esik_db), n / sr, en_az_sn)


def bosluklar(x, sr=SR, esik_db=-60.0, pencere_sn=0.1):
    """100 ms pencerede RMS esik_db altı (S5.2 ambiyans boşluğu)."""
    c = mono(np.asarray(x, dtype=np.float32)); n = int(pencere_sn * sr); k = len(c) // n
    if not k: return []
    rms = np.sqrt(np.mean(c[:k * n].reshape(k, n) ** 2, axis=1))
    return _araliklar(rms < kazanc(esik_db), pencere_sn, pencere_sn)


def yumusatma(x, sr=SR, ms=15):
    """Baş ve sona ms milisaniyelik doğrusal rampa (S5.10 tık önleme)."""
    x = np.array(x, dtype=np.float32); n = min(len(x) // 2, int(ms * sr / 1000))
    if n <= 0: return x
    r = np.linspace(0, 1, n, dtype=np.float32)
    if x.ndim == 1: x[:n] *= r; x[-n:] *= r[::-1]
    else: x[:n] *= r[:, None]; x[-n:] *= r[::-1][:, None]
    return x


def rampa_sn(x, sr=SR, bas=True):
    """Sinyalin başında (ya da sonunda) zarfın tepe seviyesinin −20 dB'inden −3 dB'ine çıkış süresi (S6.5)."""
    z = zarf(x, sr, 100); z = z if bas else z[::-1]
    if not len(z) or z.max() <= 0: return 0.0
    t = z.max(); i1 = int(np.argmax(z >= t * kazanc(-20))); i2 = int(np.argmax(z >= t * kazanc(-3)))
    return max(0.0, (i2 - i1) / 100.0)


# --- konuşma ölçüleri ---------------------------------------------------------------------------------------------------
def f0_dizisi(x, sr=SR, fmin=60.0, fmax=500.0, cerceve=0.04, adim=0.01):
    """Özilinti (YIN benzeri fark işlevi) ile çerçeve başına F0 (Hz; sessiz çerçeve 0)."""
    c = mono(np.asarray(x, dtype=np.float32)); n, h = int(cerceve * sr), int(adim * sr)
    if len(c) < n: return np.zeros(0)
    kmin, kmax = int(sr / fmax), min(int(sr / fmin), n - 1)
    idx = np.arange(0, len(c) - n, h)
    F = np.lib.stride_tricks.sliding_window_view(c, n)[idx] if len(idx) else np.zeros((0, n))
    enerji = np.sqrt(np.mean(F ** 2, axis=1)); esik = max(1e-4, float(np.percentile(enerji, 90)) * 0.1 if len(enerji) else 1e-4)
    S = np.fft.rfft(F, 2 * n); ac = np.fft.irfft(S * np.conj(S), 2 * n)[:, :n]
    cs = np.cumsum(F ** 2, axis=1); top = cs[:, -1:]
    bas = cs[:, ::-1]                                                  # Σ_{j < n-τ} x_j²
    son = top - np.concatenate([np.zeros((len(F), 1)), cs[:, :-1]], axis=1)   # Σ_{j ≥ τ} x_j²
    d = np.maximum(bas + son - 2 * ac, 0)                              # YIN fark işlevi d(τ)
    cm = d[:, 1:] / (np.cumsum(d[:, 1:], axis=1) / np.arange(1, n) + _EPS)
    out = np.zeros(len(F))
    for i in range(len(F)):
        if enerji[i] < esik: continue
        seg = cm[i, kmin - 1:kmax - 1]
        if not len(seg): continue
        alt = np.where(seg < 0.15)[0]
        j = int(alt[0]) if len(alt) else int(np.argmin(seg))
        while j + 1 < len(seg) and seg[j + 1] < seg[j]: j += 1          # eşiğin altındaki ilk çukurun dibi
        if seg[j] >= 0.35: continue
        p = 0.0
        if 0 < j < len(seg) - 1:
            a, b, c2 = seg[j - 1], seg[j], seg[j + 1]; dd = a - 2 * b + c2
            p = 0.5 * (a - c2) / dd if dd > 0 else 0.0
        out[i] = sr / (j + kmin + p)
    return out


def f0(x, sr=SR):
    d = f0_dizisi(x, sr); v = d[d > 0]
    if len(v) < 3: return {"medyan_hz": None, "p10_hz": None, "p90_hz": None, "sesli_oran": round(len(v) / max(1, len(d)), 3)}
    return {"medyan_hz": round(float(np.median(v)), 1), "p10_hz": round(float(np.percentile(v, 10)), 1),
            "p90_hz": round(float(np.percentile(v, 90)), 1), "sesli_oran": round(len(v) / len(d), 3)}


def yarim_ton(f1, f2):
    if not f1 or not f2: return None
    return 12.0 * math.log2(float(f2) / float(f1))


def _mel(f): return 2595.0 * np.log10(1 + f / 700.0)


def mel_spektrum(x, sr=SR, bant=24, n=1024, h=480):
    c = mono(np.asarray(x, dtype=np.float32))
    if len(c) < n: c = np.pad(c, (0, n - len(c)))
    F = np.lib.stride_tricks.sliding_window_view(c, n)[::h] * np.hanning(n)
    P = np.abs(np.fft.rfft(F, axis=1)) ** 2; fr = np.fft.rfftfreq(n, 1.0 / sr)
    kenar = 700 * (10 ** (np.linspace(_mel(80.0), _mel(7600.0), bant + 2) / 2595.0) - 1)
    M = np.zeros((bant, len(fr)))
    for i in range(bant):
        a, b, c2 = kenar[i], kenar[i + 1], kenar[i + 2]
        M[i] = np.clip(np.minimum((fr - a) / (b - a + _EPS), (c2 - fr) / (c2 - b + _EPS)), 0, None)
    return np.log(P @ M.T + 1e-10), np.sqrt(np.mean(F ** 2, axis=1))


def gomme(x, sr=SR):
    """Konuşmacı gömmesi (YEDEK yöntem: sesli çerçevelerin log-mel ortalaması ve sapması + F0 medyanı; ölçek bağımsız).
    Gerçek konuşmacı modeli (P1, lisansı kurulum raporunda) gelene kadar eşikler BAYRAK düzeyinde kullanılır."""
    L, e = mel_spektrum(x, sr)
    if not len(L): return np.zeros(49)
    m = e > max(1e-4, float(np.percentile(e, 50)) * 0.5); L = L[m] if m.sum() >= 3 else L
    L = L - L.mean(axis=1, keepdims=True)                              # kazanç bağımsız
    f = f0(x, sr)["medyan_hz"] or 0.0
    v = np.concatenate([L.mean(axis=0), L.std(axis=0), [math.log2(f / 100.0) if f else 0.0]])
    return v / (np.linalg.norm(v) + _EPS)


GOMME_YONTEMI = "logmel_yedek"


def benzerlik(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    if not len(a) or not len(b): return None
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + _EPS))


def zarf(x, sr=SR, hz=1000):
    c = np.abs(mono(np.asarray(x, dtype=np.float32))); n = max(1, sr // hz); k = len(c) // n
    if not k: return np.zeros(0)
    z = c[:k * n].reshape(k, n).mean(axis=1)
    w = max(1, hz // 100); return np.convolve(z, np.ones(w) / w, mode="same")


def zarf_gecikme_ms(a, b, sr=SR, en_cok_ms=200):
    """b'nin a'ya göre gecikmesi (ms; pozitif = b geç). Zarf çapraz ilintisi, 1 kHz çözünürlük."""
    za, zb = zarf(a, sr), zarf(b, sr)
    n = min(len(za), len(zb))
    if n < 10: return None
    za, zb = za[:n] - za[:n].mean(), zb[:n] - zb[:n].mean()
    m = 1 << int(math.ceil(math.log2(2 * n)))
    cc = np.fft.irfft(np.fft.rfft(zb, m) * np.conj(np.fft.rfft(za, m)), m)
    lag = np.concatenate([cc[-en_cok_ms:], cc[:en_cok_ms + 1]])
    return float(int(np.argmax(lag)) - en_cok_ms)


def onset_gucu(x, sr=SR, n=1024, h=512):
    c = mono(np.asarray(x, dtype=np.float32))
    if len(c) < n * 2: return np.zeros(0), h / sr
    F = np.lib.stride_tricks.sliding_window_view(c, n)[::h] * np.hanning(n)
    S = np.log1p(np.abs(np.fft.rfft(F, axis=1)) * 10)
    return np.concatenate([[0.0], np.maximum(0, np.diff(S, axis=0)).sum(axis=1)]), h / sr


def onsetler(x, sr=SR):
    o, dt = onset_gucu(x, sr)
    if not len(o): return []
    esik = o.mean() + 1.5 * o.std(); out = []
    for i in range(1, len(o) - 1):
        if o[i] > esik and o[i] >= o[i - 1] and o[i] >= o[i + 1] and (not out or i * dt - out[-1] > 0.08): out.append(round(i * dt, 3))
    return out


def bpm(x, sr=SR, aralik=(40, 200)):
    o, dt = onset_gucu(x, sr)
    if len(o) < 32: return None
    o = o - o.mean(); ac = np.correlate(o, o, "full")[len(o) - 1:]
    gec = np.arange(len(ac)) * dt; m = (gec >= 60.0 / aralik[1]) & (gec <= 60.0 / aralik[0])
    if not m.any() or ac[m].max() <= 0: return None
    return round(60.0 / gec[m][int(np.argmax(ac[m]))], 1)


NOTALAR = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def kroma(x, sr=SR, n=4096, h=2048):
    """(12, T) kroma; her çerçeve normalize. Frekans 55–4000 Hz."""
    c = mono(np.asarray(x, dtype=np.float32))
    if len(c) < n: c = np.pad(c, (0, n - len(c)))
    F = np.lib.stride_tricks.sliding_window_view(c, n)[::h] * np.hanning(n)
    P = np.abs(np.fft.rfft(F, axis=1)); fr = np.fft.rfftfreq(n, 1.0 / sr)
    m = (fr >= 55) & (fr <= 4000); pc = np.mod(np.round(12 * np.log2(fr[m] / 440.0)) + 9, 12).astype(int)
    C = np.zeros((12, len(F)))
    for k in range(12): C[k] = P[:, m][:, pc == k].sum(axis=1)
    return C / (np.linalg.norm(C, axis=0, keepdims=True) + _EPS)


def kroma_benzerlik(sablon, aday):
    """Şablon kroma dizisini adayın üzerinde kaydırır; en iyi ortalama kosinüs (0–1). Şablon adaydan uzunsa yer değiştirir."""
    S, A = np.asarray(sablon), np.asarray(aday)
    if S.size == 0 or A.size == 0: return None
    if S.shape[1] > A.shape[1]: S, A = A, S
    L = S.shape[1]; en = 0.0
    for i in range(0, A.shape[1] - L + 1):
        en = max(en, float(np.mean(np.sum(S * A[:, i:i + L], axis=0))))
    return round(en, 3)


_MAJ = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
_MIN = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
KIP_AILE = {"major": "major", "ionian": "major", "lydian": "major", "mixolydian": "major", "minor": "minor", "aeolian": "minor",
            "dorian": "minor", "phrygian": "minor", "locrian": "minor"}


def ton(x, sr=SR):
    """Krumhansl profilleriyle ton: {'kok': 'D', 'kip': 'minor', 'guven': r}."""
    p = kroma(x, sr).mean(axis=1)
    en = (None, None, -2.0)
    for k in range(12):
        for kip, prof in (("major", _MAJ), ("minor", _MIN)):
            r = float(np.corrcoef(p, np.roll(prof, k))[0, 1])
            if r > en[2]: en = (NOTALAR[k], kip, r)
    return {"kok": en[0], "kip": en[1], "guven": round(en[2], 3)}


def ton_coz(metin):
    """'D dorian', 'A minor', 'F# major' → {'kok', 'kip'} (kip ailesi: major/minor)."""
    if not metin: return None
    p = str(metin).replace("♯", "#").replace("♭", "b").split()
    if not p: return None
    kok = p[0][:1].upper() + p[0][1:]
    duz = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}
    kok = duz.get(kok, kok)
    if kok not in NOTALAR: return None
    return {"kok": kok, "kip": KIP_AILE.get((p[1] if len(p) > 1 else "major").lower(), "major")}


def ton_ayni(a, b):
    """İki ton aynı mı? Göreli eşler (C major ↔ A minor) aynı perde sınıfı kümesi olduğu için kabul edilir."""
    if not a or not b: return None
    if a["kok"] == b["kok"] and a["kip"] == b["kip"]: return True
    ia, ib = NOTALAR.index(a["kok"]), NOTALAR.index(b["kok"])
    if a["kip"] == "major" and b["kip"] == "minor": return (ia - ib) % 12 == 3
    if a["kip"] == "minor" and b["kip"] == "major": return (ib - ia) % 12 == 3
    return False


# --- metin --------------------------------------------------------------------------------------------------------------
def kelimeler(s):
    import re
    return [w for w in re.findall(r"[a-z0-9']+", (s or "").lower().replace("’", "'")) if w.strip("'")]


def wer(referans, hipotez):
    """Kelime hata oranı (Levenshtein / referans kelime sayısı). jiwer kuruluysa onunla aynı sonucu verir."""
    r, h = kelimeler(referans), kelimeler(hipotez)
    if not r: return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        onceki, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            gecici = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, onceki + (r[i - 1] != h[j - 1]))
            onceki = gecici
    return round(d[len(h)] / len(r), 4)


# --- müzik kalitesi (yerel ölçüler; D-25) -------------------------------------------------------------------------------
def spektral_genislik(x, sr=SR):
    """Ortalama spektrumda en yüksek seviyenin −30 dB'ine kadar uzanan bant (Hz)."""
    c = mono(np.asarray(x, dtype=np.float32))
    if len(c) < 2048: return 0.0
    F = np.lib.stride_tricks.sliding_window_view(c, 2048)[::1024] * np.hanning(2048)
    P = np.mean(np.abs(np.fft.rfft(F, axis=1)) ** 2, axis=0); fr = np.fft.rfftfreq(2048, 1.0 / sr)
    ust = fr[P >= P.max() * 1e-3]
    return round(float(ust.max() - ust.min()), 1) if len(ust) else 0.0


def dinamik_aralik(x, sr=SR):
    k = [v for _, v in kisa_sureli(x, sr, 0.5) if v > -70]
    return round(float(np.percentile(k, 95) - np.percentile(k, 10)), 2) if len(k) > 2 else 0.0


def stereo_genislik(x):
    if x.ndim == 1 or x.shape[1] < 2: return 0.0
    m, s = (x[:, 0] + x[:, 1]) / 2, (x[:, 0] - x[:, 1]) / 2
    return round(float(np.sqrt(np.mean(s ** 2)) / (np.sqrt(np.mean(m ** 2)) + _EPS)), 3)


def faz_korelasyonu(x):
    if x.ndim == 1 or x.shape[1] < 2: return 1.0
    a, b = x[:, 0].astype(np.float64), x[:, 1].astype(np.float64)
    d = math.sqrt(float(np.sum(a * a) * np.sum(b * b)))
    return round(float(np.sum(a * b) / d), 3) if d > 0 else 1.0


def mono_fark_lu(x, sr=SR):
    if x.ndim == 1: return 0.0
    return round(abs(lufs(x, sr) - lufs(np.stack([mono(x)] * 2, 1), sr)), 2)


# --- doğallık (MOS) --------------------------------------------------------------------------------------------------
def lisans(bilesen):
    d = ortak.json_oku(os.path.join(ARACLAR, "veri", "LISANSLAR.json"), {}) or {}
    return (d.get("bilesenler") or {}).get(bilesen) or {}


def lisans_dogrulandi(bilesen, ticari=True):
    l = lisans(bilesen)
    if l.get("dogrulama") not in ("dogrulandi", "dogrulandı", "belge"): return False
    return (l.get("ticari_youtube") == "evet") if ticari else True


def mos_tahmin(yol):
    """Doğallık puanı (UTMOS türü). Kod ve ağırlık lisansı LISANSLAR.json'da doğrulanmadıysa kullanılmaz → ÖLÇÜLEMEDİ (K-3)."""
    if not lisans_dogrulandi("mos_tahmincisi", ticari=False):
        return {"olculemedi": True, "neden": "MOS tahmincisinin lisansı doğrulanmadı (LISANSLAR.json mos_tahmincisi); dinleyici kör ikili ya da izle-dinle"}
    try:
        py = (ortak.yollar().get("ortamlar") or {}).get("mos")
    except ortak.YolYok: py = None
    kopru = os.path.join(ARACLAR, "kopru", "mos_kopru.py")
    if not (py and os.path.exists(py) and os.path.exists(kopru)):
        return {"olculemedi": True, "neden": "MOS ortamı kurulu değil (KUR2; YOLLAR.json ortamlar.mos)"}
    r = subprocess.run([py, kopru, yol], capture_output=True, text=True, timeout=600)
    try: return {"mos": float(json.loads(r.stdout)["mos"])}
    except Exception: return {"olculemedi": True, "neden": f"MOS köprüsü sonuç vermedi ({(r.stderr or '')[:80]})"}


# --- kurulum kartı (A10a) ------------------------------------------------------------------------------------------------
MODULLER = {"pyloudnorm": "lufs (yoksa yerel BS.1770)", "faster_whisper": "asr", "stable_whisper": "hizalama", "audio_separator": "ayristirma",
            "jiwer": "wer (yoksa yerel)", "librosa": "f0/bpm (yoksa yerel)", "mido": "midi (yoksa yerel yazıcı)", "soundfile": "eski seslendir"}


def _modul_var(ad):
    try: return importlib.util.find_spec(ad) is not None
    except Exception: return False


def kontrol(film=None):
    """Ses ortamı kartı: modüller, ikililer, ayrı ortamlar, lisans kapıları → basamak açık/kapalı (eksik yalnız kendini kapatır)."""
    try: y = ortak.yollar()
    except ortak.YolYok: y = {}
    ortam = y.get("ortamlar") or {}
    mod = {m: _modul_var(m) for m in MODULLER}
    ikili = {b: bool(shutil.which(b)) for b in ("ffmpeg", "ffprobe", "fluidsynth")}
    kutup = y.get("ses_kutuphanesi") or ""
    sf2 = sorted(f for f in (os.listdir(os.path.join(kutup, "SF2")) if os.path.isdir(os.path.join(kutup, "SF2")) else []) if f.lower().endswith(".sf2"))
    ayri = {k: bool(v and os.path.exists(v)) for k, v in ortam.items()}
    try:
        from saglayicilar import ai84_tts
        ai84_hazir = ai84_tts.AI84Tts().hazir()
    except Exception as e: ai84_hazir = (False, str(e)[:80])
    mos = {"acik": lisans_dogrulandi("mos_tahmincisi", ticari=False)}
    b = {"tts": {"acik": bool(ai84_hazir[0]), "neden": ai84_hazir[1] or None},
         "asr": {"acik": mod["faster_whisper"], "neden": None if mod["faster_whisper"] else "faster-whisper kurulu değil (KUR1)"},
         "ayristirma": {"acik": mod["audio_separator"], "neden": None if mod["audio_separator"] else "audio-separator kurulu değil (KUR1)"},
         "ses_donustur": {"acik": ayri.get("ses_donustur", False), "neden": None if ayri.get("ses_donustur") else "KUR2 ortamı yok"},
         "tts_dudak": {"acik": ayri.get("musetalk", False), "neden": None if ayri.get("musetalk") else "KUR3 MuseTalk ortamı yok"},
         "acestep": {"acik": ayri.get("acestep", False), "neden": None if ayri.get("acestep") else "KUR3 ACE-Step ortamı yok"},
         "midi_ornek": {"acik": True, "cal": "fluidsynth+sf2" if (ikili["fluidsynth"] and sf2) else "ic_sentez",
                        "neden": None if (ikili["fluidsynth"] and sf2) else "FluidSynth/SF2 yok: iç sentez (yalnız animatik)"},
         "lufs": {"acik": True, "yontem": "pyloudnorm" if mod["pyloudnorm"] else "yerel_bs1770"},
         "mos": {"acik": mos["acik"], "neden": None if mos["acik"] else "MOS lisansı doğrulanmadı → ÖLÇÜLEMEDİ"},
         "miks": {"acik": ikili["ffmpeg"], "neden": None if ikili["ffmpeg"] else "ffmpeg yok (mux ve video sesi okunamaz)"}}
    kart = {"_surum": 1, "_uretim": {"asama": "A10a", "gorev": os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None,
                                    "arac_surum": SURUM, "zaman": datetime.datetime.now().astimezone().isoformat(timespec="seconds")},
            "moduller": mod, "ikililer": ikili, "sf2": sf2, "ayri_ortamlar": ayri, "basamaklar": b,
            "kapali": sorted(k for k, v in b.items() if not v["acik"])}
    if film:
        ortak.atomik_yaz(os.path.join(film, "_RAPOR", "S_KURULUM.json"), kart)
    return kart


def olc(yol):
    x, sr = oku(yol)
    return {"dosya": yol, "sure_sn": round(sure(x, sr), 3), "lufs": round(lufs(x, sr), 2), "gercek_tepe_dbtp": round(gercek_tepe(x, sr), 2),
            "ornek_tepe_dbfs": round(ornek_tepe(x), 2), "lra": round(lra(x, sr), 2), "kirpilma": kirpilma(x),
            "sessizlik_50db_03sn": sessizlikler(x, sr), "f0": f0(x, sr)}


def main(argv):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if argv[:1] == ["--kontrol"]:
        film = argv[argv.index("--film") + 1] if "--film" in argv else None
        k = kontrol(film)
        for ad, v in k["basamaklar"].items(): print(f"  {ad:13} {'AÇIK ' if v['acik'] else 'KAPALI'} {v.get('neden') or v.get('yontem') or v.get('cal') or ''}")
        return 0
    if argv[:1] == ["--olc"] and len(argv) >= 2:
        try: r = olc(argv[1])
        except Exception as e: print(f"!! okunamadı: {e}"); return 1
        print(json.dumps(r, ensure_ascii=False, indent=1)); return 0
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
