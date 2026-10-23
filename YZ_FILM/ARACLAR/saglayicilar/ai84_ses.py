"""AI84 (ElevenLabs v4) ses sağlayıcısı — ai84.py istemcisini kullanır. Önbellekli: aynı cümle iki kez ücretlenmez.
Anahtar AYARLAR/ai84_anahtar.txt ya da AI84_KEY_FILE ortam değişkenindeki dosyada; burada okunmaz/yazdırılmaz.
"""
import os, shutil, hashlib, subprocess
from saglayicilar import Saglayici, Kisitlandi, AYARLAR


class AI84Ses(Saglayici):
    ad = "ai84"
    turler = ("ses",)

    def hazir(self):
        p = os.environ.get("AI84_KEY_FILE") or os.path.join(AYARLAR, "ai84_anahtar.txt")
        if not (os.path.exists(p) and open(p, encoding="utf-8-sig").read().strip()):
            return False, "AYARLAR/ai84_anahtar.txt boş"
        return True, ""

    def ses(self, film, metin, ses_id, cikti):
        if not ses_id: raise Kisitlandi("karakterin sesi (voice_id) tanımlı değil", kod="hazir_degil")
        import ai84
        on = os.path.join(film, "SESLER", "_tts_onbellek"); os.makedirs(on, exist_ok=True)
        mp3 = os.path.join(on, hashlib.md5(f"{ses_id}|eleven_v4|{metin}".encode()).hexdigest()[:16] + ".mp3")
        try:
            if not os.path.exists(mp3): ai84.tts(metin, ses_id, mp3, model_id="eleven_v4")
        except ai84.AI84Error as e:
            raise Kisitlandi(str(e)[:120], kod="ag") from None
        if cikti.endswith(".mp3"): shutil.copy2(mp3, cikti)
        else: subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", "44100", "-ac", "1", cikti], check=True)
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cikti],
                           capture_output=True, text=True)
        return float(r.stdout or 0)
