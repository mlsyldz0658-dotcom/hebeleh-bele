"""SES_SAHTE — ses türlerinin test sağlayıcısı (yalnız test kipi, D-41): tts, asr, muzik, dinleyici, ses_donustur ve paylaşılan ses
kataloğu. Ağ ve kredi yok; 48 kHz. Her ürettiği dosyanın yanına `<dosya>.sahte.json` (söylenen metin, kelime zamanları, sözlü içerik)
yazar; sahte ASR onu okur. Gerçek bir filmin zincirinde bulunursa film.py HATA verir (TASARIM §5.6).

Hata enjeksiyonu (bozuk girdi testleri; [SM2] §4.7.10): <film>/_KASET/SES_SAHTE.json ya da YZ_FILM_SES_SAHTE ortam değişkeni:
  {"asr": {"degistir": {"Kestra": "Kestrel"}, "konusma_yok": false},
   "tts": {"tepe_normal": false, "hata": ["R0002"]},
   "muzik": {"vokal": [1], "motifsiz": false},
   "dinleyici": {"cevap": "A", "guven": 0.7}}            (dinleyici anahtarı yoksa Kisitlandi("anahtar"): ÖLÇÜLEMEDİ)
"""
import os, json, hashlib, math
import numpy as np
from saglayicilar import Saglayici, Kisitlandi

SR = 48000
KATALOG = [  # sahte paylaşılan ses kütüphanesi ([D-EL] alanları)
    {"voice_id": "sahte_k1", "name": "Northern Ember", "gender": "female", "age": "middle_aged", "accent": "british", "f0": 185,
     "notice_period": 90, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "husky"},
    {"voice_id": "sahte_k2", "name": "Bright Lark", "gender": "female", "age": "young", "accent": "american", "f0": 240,
     "notice_period": 60, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "bright"},
    {"voice_id": "sahte_k3", "name": "Low Hearth", "gender": "female", "age": "middle_aged", "accent": "british", "f0": 170,
     "notice_period": 10, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "low"},
    {"voice_id": "sahte_k4", "name": "Quiet Moss", "gender": "female", "age": "middle_aged", "accent": "british", "f0": 200,
     "notice_period": 120, "voice_restricted": True, "preview": True, "language": "en", "descriptive": "soft"},
    {"voice_id": "sahte_e1", "name": "Deep Harbor", "gender": "male", "age": "middle_aged", "accent": "british", "f0": 98,
     "notice_period": 90, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "deep"},
    {"voice_id": "sahte_e2", "name": "Calm Stone", "gender": "male", "age": "middle_aged", "accent": "british", "f0": 112,
     "notice_period": 45, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "calm"},
    {"voice_id": "sahte_e3", "name": "Young Reed", "gender": "male", "age": "young", "accent": "american", "f0": 135,
     "notice_period": 30, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "clear"},
    {"voice_id": "sahte_e4", "name": "Gravel Road", "gender": "male", "age": "old", "accent": "british", "f0": 92,
     "notice_period": 365, "voice_restricted": False, "preview": False, "language": "en", "descriptive": "gravelly"},
    {"voice_id": "sahte_tel_k", "name": "Telaffuz Kadın", "gender": "female", "age": "middle_aged", "accent": "american", "f0": 205,
     "notice_period": 365, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "neutral"},
    {"voice_id": "sahte_tel_e", "name": "Telaffuz Erkek", "gender": "male", "age": "middle_aged", "accent": "american", "f0": 118,
     "notice_period": 365, "voice_restricted": False, "preview": True, "language": "en", "descriptive": "neutral"},
]


def ayar(film):
    p = os.environ.get("YZ_FILM_SES_SAHTE") or (os.path.join(film, "_KASET", "SES_SAHTE.json") if film else "")
    try:
        with open(p, encoding="utf-8") as f: return json.load(f)
    except (OSError, ValueError): return {}


def _yaz(yol, x):
    from olcum import ses as O
    O.yaz(yol, x)


def yan_yaz(yol, **k):
    with open(yol + ".sahte.json", "w", encoding="utf-8") as f: json.dump(k, f, ensure_ascii=False)


def yan_oku(yol):
    try:
        with open(yol + ".sahte.json", encoding="utf-8") as f: return json.load(f)
    except (OSError, ValueError): return None


def _h(s): return int(hashlib.md5(str(s).encode()).hexdigest()[:8], 16)


def ses_ozellik(voice_id):
    v = next((x for x in KATALOG if x["voice_id"] == voice_id), None)
    h = _h(voice_id)
    f0 = v["f0"] if v else 90 + h % 160
    tini = [0.6 + ((h >> (4 * k)) & 15) / 25.0 for k in range(8)]
    return f0, tini


def konusma(metin, voice_id, teslim="normal", hiz=2.5, sr=SR):
    """Ses kimliğine bağlı perde ve tınıda, hece zarflı konuşma benzeri sinyal + kelime zamanları."""
    kel = [w for w in metin.replace("—", " ").split() if w.strip()]
    sure = max(0.6, len(kel) / hiz + 0.3)
    t = np.arange(int(sure * sr)) / sr
    f0, tini = ses_ozellik(voice_id)
    vib = 1 + 0.03 * np.sin(2 * np.pi * 3.1 * t)
    faz = 2 * np.pi * np.cumsum(f0 * vib) / sr
    y = sum(a * np.sin((k + 1) * faz) / (k + 1) ** 0.7 for k, a in enumerate(tini))
    hece = 0.55 + 0.45 * np.abs(np.sin(np.pi * 4.0 * t))
    if teslim == "fisilti": y = np.random.default_rng(_h(metin)).normal(0, 1, len(t)) * 0.4 + 0.2 * y; g = 0.05
    elif teslim == "bagirma": g = 0.5
    else: g = 0.2
    zarf = np.minimum(1, np.minimum(t / 0.03, (sure - t) / 0.05))
    x = (g * y * hece * zarf / (np.max(np.abs(y)) + 1e-9)).astype(np.float32)
    adim = (sure - 0.3) / max(1, len(kel))
    kz = [{"w": w, "bas": round(0.15 + i * adim, 3), "bit": round(0.15 + (i + 0.9) * adim, 3)} for i, w in enumerate(kel)]
    return x, kz


class SesSahte(Saglayici):
    ad = "sahte"
    turler = ("tts", "ses", "asr", "muzik", "dinleyici", "ses_donustur", "katalog")
    kredili = False
    elle = False
    ortam = "her_ikisi"
    model = "ses_sahte 1.0"
    lisans = "test"

    def birim_fiyat(self): return 0

    # --- tts ---
    def tts(self, film, metin, ses_id, cikti, seed=None, onceki=None, sonraki=None, teslim="normal", replik=None):
        a = ayar(film).get("tts") or {}
        if replik and replik in (a.get("hata") or []): raise Kisitlandi("sahte TTS hatası (enjekte)", kod="ag")
        x, kz = konusma(metin, ses_id or "yok", teslim)
        if a.get("tepe_normal"): x = x / (np.max(np.abs(x)) + 1e-9) * 0.6
        _yaz(cikti, x); yan_yaz(cikti, metin=metin, kelimeler=kz, ses=ses_id)
        return {"sure_sn": round(len(x) / SR, 3), "kredi": 0, "kelimeler": kz}

    def ses(self, film, metin, ses_id, cikti):
        return self.tts(film, metin, ses_id, cikti)["sure_sn"]

    # --- asr ---
    def asr(self, film, wav, bilinen_metin=None):
        a = ayar(film).get("asr") or {}
        y = yan_oku(wav) or {}
        if a.get("konusma_yok") or not y: return {"metin": "", "kelimeler": [], "guven": 0.0}
        kel = []
        for k in y.get("kelimeler") or []:
            w = k["w"]; cek = w.strip(".,!?;:\"'")
            for eski, yeni in (a.get("degistir") or {}).items():
                if cek.lower() == eski.lower(): w = w.replace(cek, yeni)
            kel.append(dict(k, w=w, guven=k.get("guven", 0.95)))
        return {"metin": " ".join(k["w"] for k in kel), "kelimeler": kel, "guven": 0.95 if kel else 0.0}

    # --- katalog (AI84 paylaşılan ses benzeri) ---
    def voices(self, **f):
        out = [dict(v) for v in KATALOG if not v["voice_id"].startswith("sahte_tel")]
        if f.get("gender"): out = [v for v in out if v["gender"] == f["gender"]] or out
        return out

    def onizleme(self, voice_id, cikti, metin="Hello there. This is how I sound when I speak to you.", **_):
        v = next((x for x in KATALOG if x["voice_id"] == voice_id), {})
        if v and not v.get("preview"): return None
        return self.tts(None, metin, voice_id, cikti)

    # --- müzik ---
    def muzik(self, film, ipucu, cikti_dir, aday=3, referans_wav=None, motif=None):
        from saglayicilar import midi_ornek as M
        a = ayar(film).get("muzik") or {}
        os.makedirs(cikti_dir, exist_ok=True)
        ton, bpm = ipucu.get("ton") or (motif or {}).get("ton") or "D minor", ipucu.get("bpm") or (motif or {}).get("bpm") or 72
        hedef = float(ipucu.get("hedef_sure_sn") or 20); out = []
        for i in range(int(aday)):
            y = M.eslik(ton, bpm, hedef, genlik=0.06 + 0.01 * i)
            if motif and motif.get("notalar") and not a.get("motifsiz"):
                mel = M.sentez(motif["notalar"], bpm, tini="yayli", genlik=0.18)
                rep = np.tile(np.concatenate([mel, np.zeros(len(mel) // 3, np.float32)]), 1 + int(len(y) / max(1, len(mel))))[:len(y)]
                y = y + np.stack([rep, rep], 1)
            elif not motif:
                rng = np.random.default_rng(_h(ipucu.get("id", "")) + i)
                notalar = [[n, 1.0] for n in rng.choice(["D4", "F4", "A4", "C5", "E4", "G4"], 8)]
                mel = M.sentez(notalar, bpm, genlik=0.12)[:len(y)]
                y[:len(mel)] += np.stack([mel, mel], 1)
            p = os.path.join(cikti_dir, f"{ipucu['id']}_sahte{i + 1}.wav")
            _yaz(p, y)
            vokal = (i + 1) in (a.get("vokal") or [])
            yan_yaz(p, metin="la la love" if vokal else "", kelimeler=[{"w": w, "bas": 1.0 + j, "bit": 1.5 + j, "guven": 0.9}
                                                                   for j, w in enumerate(["la", "la", "love"])] if vokal else [])
            out.append(p)
        return out

    # --- dinleyici ---
    def dinleyici(self, film, wav, soru, secenekler):
        a = ayar(film).get("dinleyici")
        if not a: raise Kisitlandi("sahte dinleyici: anahtar yok", kod="anahtar")
        return {"cevap": a.get("cevap", secenekler[0] if secenekler else None), "guven": a.get("guven", 0.6)}

    # --- ses dönüştürme (motor kıyası için taklit) ---
    def ses_donustur(self, film, giris_wav, karakter, cikti, f0_yt=0, hedef_ses=None):
        from olcum import ses as O
        x, sr = O.oku(giris_wav)
        y = yan_oku(giris_wav) or {}
        z, kz = konusma(y.get("metin") or "speech", hedef_ses or karakter or "hedef", y.get("teslim", "normal"))
        n = min(len(z), len(O.mono(x))); z = z[:n] * (np.sqrt(np.mean(O.mono(x)[:n] ** 2)) / (np.sqrt(np.mean(z ** 2)) + 1e-9))
        O.yaz(cikti, z); yan_yaz(cikti, metin=y.get("metin", ""), kelimeler=y.get("kelimeler") or kz, ses=hedef_ses)
        return {"gecikme_ms": 0.0, "benzerlik": None}
