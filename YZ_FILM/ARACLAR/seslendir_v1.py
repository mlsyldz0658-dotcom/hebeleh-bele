"""SESLENDİR v1 (ESKİ; yalnız v1 SAHNELER.json filmleri için, seslendir.py yönlendirir) — replikli sahnelerde Flow'un konuşmasını sabit karakter sesiyle değiştirir.

Kullanım: python seslendir.py <film_klasoru>
Her replikli sahne (SIRALI_VIDEO/NNN.mp4) için:
  1. whisper: Flow'un konuştuğu saniyeleri cümle cümle bulur
  2. demucs: klibin sesini "konuşma" ve "ortam" (rüzgâr, ateş, adım) olarak ayırır
  3. AI84/ElevenLabs v4: her cümleyi karakterin sabit sesiyle üretir (önbellekli, aynı cümle iki kez ücretlenmez)
  4. cümleyi Flow'un konuştuğu süreye sığdırır (perde korunur)
Çıktı: SESLER/NNN_ortam.wav, SESLER/NNN_c{j}.wav, SESLER/diyalog.json, KURGU/altyazi_<dil>.srt (sahne başına zamanlar)
Karakterin sesi tanımlı değilse ya da TTS başarısız olursa o cümlede Flow'un kendi sesi kullanılır (raporda yazar).
UYARI: bu eski yolun bilinen kusurları TASARIM §6.6 / [SM2] §4.6.1'de yazılıdır (tepe normalleştirme, atempo, kelime sayısıyla
bölme, sessiz oransal yayma, sessizce Flow sesine düşme, 44,1 kHz). v2 filmleri seslendir.py --animatik / --parti ile çalışır.
"""
import os, sys, re, json, hashlib, subprocess, shutil
import ortak   # SAHNELER.json v2 koruması
import numpy as np, soundfile as sf
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("HF_HUB_OFFLINE", "1")
SR = 44100


def run(*a): subprocess.run([str(x) for x in a], check=True)
def log(*a): print(*a, flush=True)
def words(s): return re.findall(r"[A-Za-z0-9']+", s)


def sentences(rep):
    if rep.get("cumleler"): return rep["cumleler"]
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+", rep["metin"]) if p.strip()]
    return [{"en": p, "tr": ""} for p in parts]


class Voicer:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.plan = ortak.sahneler_oku(self.root, "seslendir.py")
        self.ses = os.path.join(self.root, "SESLER"); self.cache = os.path.join(self.ses, "_tts_onbellek")
        self.tmp = os.path.join(self.ses, "_gecici")
        for d in (self.ses, self.cache, self.tmp, os.path.join(self.root, "KURGU")): os.makedirs(d, exist_ok=True)
        self._wm = None

    def load(self, p, ch=1):
        o = os.path.join(self.tmp, "yukle.wav"); run("ffmpeg", "-v", "error", "-y", "-i", p, "-ar", SR, "-ac", ch, o)
        return sf.read(o, dtype="float32")[0]

    def whisper(self, wav):
        if self._wm is None:
            from faster_whisper import WhisperModel
            self._wm = WhisperModel("small.en", device="cpu", compute_type="int8")
        segs, _ = self._wm.transcribe(wav, word_timestamps=True, language="en", vad_filter=True)
        return [(w.start, w.end, w.word.strip()) for s in segs for w in s.words]

    def separate(self, clip, n):
        out_dir = os.path.join(self.tmp, "demucs")
        st = os.path.join(self.tmp, f"{n:03d}.wav"); run("ffmpeg", "-v", "error", "-y", "-i", clip, "-vn", "-ac", 2, "-ar", SR, st)
        run(sys.executable, "-m", "demucs", "--two-stems=vocals", "-n", "htdemucs", "-o", out_dir, st)
        d = os.path.join(out_dir, "htdemucs", f"{n:03d}")
        return os.path.join(d, "no_vocals.wav"), os.path.join(d, "vocals.wav")

    def tts(self, text, voice):
        import ai84
        key = hashlib.md5(f"{voice}|eleven_v4|{text}".encode()).hexdigest()[:16]
        mp3 = os.path.join(self.cache, key + ".mp3")
        if not os.path.exists(mp3):
            ai84.tts(text, voice, mp3, model_id="eleven_v4")
        a = self.load(mp3); nz = np.where(np.abs(a) > 0.01)[0]
        return a[max(0, nz[0] - 300):nz[-1] + 1500] if len(nz) else a

    def fit(self, a, target):
        ratio = max(0.8, min(1.3, (len(a) / SR) / max(0.3, target)))
        if abs(ratio - 1) < 0.02: return a
        i, o = os.path.join(self.tmp, "fit_i.wav"), os.path.join(self.tmp, "fit_o.wav")
        sf.write(i, a, SR); run("ffmpeg", "-v", "error", "-y", "-i", i, "-af", f"atempo={ratio:.4f}", o)
        return sf.read(o, dtype="float32")[0]

    def scene(self, s):
        n = s["no"]; rep = s["replik"]; clip = os.path.join(self.root, "SIRALI_VIDEO", f"{n:03d}.mp4")
        if not os.path.exists(clip): log(f"  {n:03d}: video yok, atlandı"); return None
        sents = sentences(rep); voice = (self.plan["karakterler"].get(rep["karakter"]) or {}).get("ses")
        bed, voc = self.separate(clip, n)
        shutil.copy2(bed, os.path.join(self.ses, f"{n:03d}_ortam.wav"))
        w = self.whisper(voc)
        if not w: w = self.whisper(clip)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", clip],
                                   capture_output=True, text=True).stdout)
        # cümleleri whisper kelimelerine kelime sayısıyla böl; whisper hiç duymadıysa klibe orantılı yay
        spans, i = [], 0
        for j, c in enumerate(sents):
            k = len(words(c["en"]))
            if w:
                part = w[i:i + k] if j < len(sents) - 1 else w[i:]
                part = part or w[-1:]
                spans.append((part[0][0], part[-1][1])); i += k
            else:
                a0 = 0.8 + (dur - 1.6) * j / len(sents); spans.append((a0, a0 + (dur - 1.6) / len(sents) * 0.85))
        flowv = self.load(voc)
        out = []
        for j, (c, (t0, t1)) in enumerate(zip(sents, spans)):
            src = "sabit ses"
            try:
                if not voice: raise RuntimeError("karakterin sesi tanımlı değil")
                a = self.fit(self.tts(c["en"], voice), t1 - t0)
            except Exception as e:
                src = f"Flow sesi ({str(e)[:60]})"
                t0 = max(0, t0 - 0.08); a = flowv[int(t0 * SR):int((t1 + 0.12) * SR)]
            a = a / (np.max(np.abs(a)) + 1e-9) * 0.6
            p = os.path.join(self.ses, f"{n:03d}_c{j}.wav"); sf.write(p, a, SR)
            out.append({"dosya": os.path.basename(p), "bas": round(float(t0), 3), "sure": round(len(a) / SR, 3),
                        "en": c["en"], "tr": c.get("tr", ""), "kaynak": src})
            log(f"  {n:03d}.{j} [{t0:5.2f}s] {src:12} | {c['en']}")
        return {"ortam": f"{n:03d}_ortam.wav", "cumleler": out}

    def run(self):
        res = {}
        for s in self.plan["sahneler"]:
            if s.get("replik"):
                r = self.scene(s)
                if r: res[str(s["no"])] = r
        json.dump(res, open(os.path.join(self.ses, "diyalog.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        shutil.rmtree(self.tmp, ignore_errors=True)
        log(f"\nSESLENDİRME BİTTİ: {len(res)} sahne. Ayrıntı: SESLER\\diyalog.json")
        return res


if __name__ == "__main__":
    Voicer(sys.argv[1] if len(sys.argv) > 1 else os.getcwd()).run()
