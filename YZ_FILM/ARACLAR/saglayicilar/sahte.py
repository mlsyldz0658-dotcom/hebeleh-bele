"""SAHTE sağlayıcı — ağ ve kredi kullanmadan, testler için yer tutucu görsel/video/ses/müzik üretir.
Görsel: sahne numarası yazan düz renkli kare (PIL). Video: o görselden 8 sn'lik sessiz/sesli klip (ffmpeg).
Ses: replik uzunluğunda bip (kelime sayısına göre süre). Müzik: alçak sesli akor.
"""
import os, subprocess, wave
import numpy as np
from PIL import Image, ImageDraw
from saglayicilar import Saglayici

SR = 44100


def wav_yaz(path, a, sr=SR):
    a = np.clip(a, -1, 1); a = (a * 32767).astype("<i2")
    ch = 1 if a.ndim == 1 else a.shape[1]
    with wave.open(path, "wb") as w:
        w.setnchannels(ch); w.setsampwidth(2); w.setframerate(sr); w.writeframes(a.tobytes())


class Sahte(Saglayici):
    ad = "sahte"
    turler = ("gorsel", "video", "ses", "muzik")
    kredili = False

    def gorsel(self, film, sahne, cikti):
        n = sahne["no"]; renk = ((n * 67) % 200 + 30, (n * 131) % 200 + 30, (n * 29) % 200 + 30)
        im = Image.new("RGB", (1280, 720), renk); d = ImageDraw.Draw(im)
        d.text((40, 40), f"SAHTE {n:03d}", fill=(255, 255, 255))
        d.text((40, 80), (sahne.get("gorsel_istem") or "")[:120], fill=(255, 255, 255))
        im.save(cikti, quality=90)

    def video(self, film, sahne, gorsel, cikti, sure=8):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-i", gorsel,
                        "-f", "lavfi", "-i", f"sine=frequency=220:sample_rate={SR}",
                        "-t", str(sure), "-vf", "scale=640:360,format=yuv420p", "-r", "24",
                        "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", "-af", "volume=0.05", "-shortest", cikti],
                       check=True)

    def ses(self, film, metin, ses_id, cikti):
        sure = max(0.6, 0.38 * len(metin.split()))
        t = np.arange(int(sure * SR)) / SR
        wav_yaz(cikti, 0.3 * np.sin(2 * np.pi * 330 * t) * np.minimum(1, np.minimum(t, sure - t) * 20))
        return sure

    def muzik(self, film, sure, cikti):
        t = np.arange(int(sure * SR)) / SR
        a = sum(np.sin(2 * np.pi * f * t) for f in (146.8, 174.6, 220.0)) * 0.05
        wav_yaz(cikti, np.stack([a, a], 1))
