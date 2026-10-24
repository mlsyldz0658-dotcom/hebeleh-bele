"""AI84_TTS — ElevenLabs v4 (AI84 aracı) TTS sağlayıcısı, `tts` türü (TASARIM §5.6, §2.2; [SM2] §4.6.3). 48 kHz mono wav yazar.
Önbellek: <film>/SESLER/_tts_onbellek/<ses|model|metin|tohum özeti>.mp3 — aynı cümle iki kez ücretlenmez.
Anahtar dosyası yalnız VARLIĞI ve boyutuyla denetlenir (içerik okunmaz; okumayı ai84.py ilk istekte yapar). Anahtar yoksa
`Kisitlandi(kod="anahtar")` (geçilebilir) — süreç ölmez. Ağ/iş hatası `Kisitlandi(kod="ag")`.
AI84 tohum (seed) ve previous_text/next_text alanlarını geçiriyorsa ai84.tts'e eklenmeleri paylaşılan istektir; o zamana kadar bu alanlar
önbellek anahtarına girer ama gönderilmez (kayıtta `gecirilmedi`).
"""
import os, hashlib, subprocess, shutil
from saglayicilar import Saglayici, Kisitlandi

SR = 48000


def anahtar_yolu():
    if os.environ.get("AI84_KEY_FILE"): return os.environ["AI84_KEY_FILE"]
    import ortak
    return os.path.join(ortak.yollar()["ayarlar"], "ai84_anahtar.txt")


class AI84Tts(Saglayici):
    ad = "ai84"
    turler = ("tts", "ses", "katalog")
    kredili = True
    elle = False
    ortam = "her_ikisi"
    model = "eleven_v4"
    lisans = "aracı hizmet (ElevenLabs tabanlı; kullanici_hizmeti)"

    def hazir(self):
        try: p = anahtar_yolu()
        except Exception as e: return False, str(e)[:120]
        try: dolu = os.path.getsize(p) > 0
        except OSError: dolu = False
        if not dolu: return False, "AI84 anahtar dosyası yok ya da boş (anahtar_yok)"
        if not shutil.which("ffmpeg"): return False, "ffmpeg yok"
        return True, ""

    def birim_fiyat(self): return 1          # kredi/harf (BK §6.4; fiyat_olcum ile güncellenir)

    def tahmin(self, metin): return len(metin or "")

    def onbellek_anahtari(self, metin, ses_id, seed=None):
        return hashlib.md5(f"{ses_id}|{self.model}|{metin}|{seed}".encode()).hexdigest()[:16]

    def onbellek(self, film, metin, ses_id, seed=None):
        return os.path.join(film, "SESLER", "_tts_onbellek", self.onbellek_anahtari(metin, ses_id, seed) + ".mp3")

    def tts(self, film, metin, ses_id, cikti, seed=None, onceki=None, sonraki=None, teslim="normal", replik=None):
        if not ses_id: raise Kisitlandi("karakterin sesi (voice_id) tanımlı değil", kod="hazir_degil")
        ok, neden = self.hazir()
        if not ok: raise Kisitlandi(neden, kod="anahtar")
        import ai84
        mp3 = self.onbellek(film, metin, ses_id, seed); os.makedirs(os.path.dirname(mp3), exist_ok=True)
        kredi = 0
        if not os.path.exists(mp3):
            try: kredi = ai84.tts(metin, ses_id, mp3 + ".tmp", model_id=self.model) or self.tahmin(metin)
            except ai84.AI84Error as e: raise Kisitlandi(str(e)[:120], kod="anahtar" if "anahtar" in str(e) else "ag") from None
            os.replace(mp3 + ".tmp", mp3)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", str(SR), "-ac", "1", cikti], check=True)
        from olcum import ses as O
        x, _ = O.oku(cikti)
        return {"sure_sn": round(len(x) / SR, 3), "kredi": kredi, "kelimeler": None, "onbellek": os.path.basename(mp3),
                "gecirilmedi": [k for k, v in (("seed", seed), ("onceki", onceki), ("sonraki", sonraki)) if v]}

    def onbellekte_mi(self, film, metin, ses_id, seed=None): return os.path.exists(self.onbellek(film, metin, ses_id, seed))

    def ses(self, film, metin, ses_id, cikti): return self.tts(film, metin, ses_id, cikti)["sure_sn"]

    def voices(self, **f):
        """Paylaşılan ses araması ([D-EL] süzgeçleri; geçmeyen süzgeç yerelde uygulanır). Sayfalar gezilir (≤ 5 sayfa)."""
        import ai84
        out = []
        for sayfa in range(5):
            try: v = ai84._req("GET", "/v1/shared-voices", params={"page_size": 30, "page": sayfa, **{k: x for k, x in f.items() if x}})
            except ai84.AI84Error as e: raise Kisitlandi(str(e)[:120], kod="ag") from None
            out += v.get("voices") or []
            if not v.get("has_more"): break
        return [{"voice_id": x.get("voice_id"), "name": x.get("name"), "gender": x.get("gender"), "age": x.get("age"),
                 "accent": x.get("accent"), "language": x.get("language"), "notice_period": x.get("notice_period"),
                 "voice_restricted": bool(x.get("voice_restricted") or x.get("is_restricted")),
                 "preview": bool(x.get("preview_url")), "preview_url": x.get("preview_url"),
                 "descriptive": x.get("descriptive"), "use_case": x.get("use_case")} for x in out]

    def onizleme(self, voice_id, cikti, metin=None, url=None):
        """Ücretsiz önizleme sesi (paylaşılan sesin preview_url'i; kredi yok)."""
        if not url: return None
        import ai84
        mp3 = cikti + ".mp3"; ai84._download(url, mp3)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ar", str(SR), "-ac", "1", cikti], check=True)
        return {"sure_sn": None, "kredi": 0}
