"""YEREL SES — ayrı sanal ortamda koşan yerel ses ve dudak motorları (TASARIM §6.6 `saglayicilar/` ses sınıfları, §2.2, D-36, D-37).

Sınıflar (ADLAR saglayici_turleri adlarıyla): OpenVoice, Chatterbox, RVC (ses_donustur) · Roformer, Demucs (ayristirma) ·
MuseTalk (dudak). ASR (faster_whisper) ana ortamdadır: saglayicilar/asr_whisper.py (tek sınıf; burada kopyası yok). Wav2Lip, LatentSync, Seed-VC YAZILMAZ (ADLAR saglayici_dislanan; lisans/kalite).
Sözleşme: motor, YOLLAR.json "ortamlar.<ortam>" ile verilen ayrı Python'da `motor_kosucu.py <motor> <istek.json>` olarak koşar;
istek ve yanıt JSON'dur, ses dosyası diskten. Ortam yoksa hazir() False ve çağrı Kisitlandi("hazir_degil") → zincir sıradakine geçer.
Ana ortamda kurulu hafif paketler (audio-separator, faster-whisper) varsa ayrı ortam gerekmez (ortam_adi None).
Hiçbiri kredi harcamaz; hiçbiri ağa çıkmaz (modeller KUR2/KUR3'te bir kez indirilir, sonra HF_HUB_OFFLINE=1).
"""
import os, sys, json, subprocess, tempfile, importlib.util
ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
from saglayicilar import Saglayici, Kisitlandi
import ortak

KOSUCU = os.path.join(ARACLAR, "motor_kosucu.py")
DISLANAN = ("wav2lip", "latentsync", "fal_latentsync", "seed_vc", "seed-vc")


def ortam_python(ad):
    try: v = (ortak.yollar().get("ortamlar") or {}).get(ad)
    except ortak.YolYok: return None
    if not v: return None
    return v if os.path.isfile(v) else (os.path.join(v, "Scripts", "python.exe") if os.name == "nt" else os.path.join(v, "bin", "python"))


class YerelMotor(Saglayici):
    ad = ""
    motor = ""
    ortam_adi = None          # YOLLAR ortamlar anahtarı; None → ana ortam
    ana_paket = None          # ana ortamda bulunursa ayrı ortam gerekmez
    kredili = False
    ortam = "yerel"
    elle = False
    zaman_asimi = 3600

    def python(self):
        if self.ana_paket and importlib.util.find_spec(self.ana_paket): return sys.executable
        return ortam_python(self.ortam_adi) if self.ortam_adi else None

    def hazir(self):
        if any(d in (self.ad + self.motor).lower() for d in DISLANAN): return False, "dışlanan motor"
        p = self.python()
        if not p or not os.path.exists(p): return False, f"{self.ad}: ortam kurulu değil (KUR2/KUR3, YOLLAR ortamlar.{self.ortam_adi})"
        return True, ""

    def kos(self, istek):
        ok, neden = self.hazir()
        if not ok: raise Kisitlandi(neden, kod="hazir_degil")
        with tempfile.TemporaryDirectory(prefix="yz_motor_") as d:
            g = os.path.join(d, "istek.json"); c = os.path.join(d, "yanit.json")
            istek = dict(istek, yanit=c)
            with open(g, "w", encoding="utf-8") as f: json.dump(istek, f, ensure_ascii=False)
            env = dict(os.environ, HF_HUB_OFFLINE="1", PYTHONIOENCODING="utf-8")
            r = subprocess.run([self.python(), KOSUCU, self.motor, g], capture_output=True, text=True, timeout=self.zaman_asimi, env=env)
            y = ortak.json_oku(c, {}) or {}
        if r.returncode == 3: raise Kisitlandi(y.get("neden") or "GPU belleği yetmedi", kod="hazir_degil")
        if r.returncode or y.get("hata"):
            raise Kisitlandi(f"{self.ad}: {y.get('hata') or (r.stderr or '')[-300:]}", kod="hazir_degil")
        return y


class _Donusturucu(YerelMotor):
    turler = ("ses_donustur",)
    ortam_adi = "ses_donustur"

    def ses_donustur(self, film, giris_wav, karakter, cikti, f0_yt=0, replik=None, referans=None):
        y = self.kos({"giris": giris_wav, "cikti": cikti, "karakter": karakter, "f0_yt": f0_yt, "referans": referans})
        return {"benzerlik": y.get("benzerlik"), "wer_artis": y.get("wer_artis"), "motor": self.ad}


class OpenVoice(_Donusturucu):
    ad, motor = "openvoice", "openvoice"


class Chatterbox(_Donusturucu):
    ad, motor = "chatterbox", "chatterbox"


class RVC(_Donusturucu):
    ad, motor = "rvc", "rvc"

    def egit(self, film, karakter, veri_klasoru, cikti):
        """RVC eğitimi yalnız izinle (FILM_AYAR izinler.rvc_egitim) ve TTS sağlayıcısının koşulları eğitime izin veriyorsa (§2.2 madde 4)."""
        return self.kos({"is": "egit", "karakter": karakter, "veri": veri_klasoru, "cikti": cikti})


class Roformer(YerelMotor):
    ad, motor, ana_paket, ortam_adi = "roformer", "roformer", "audio_separator", "ses_donustur"
    turler = ("ayristirma",)

    def ayristir(self, film, klip, cikti_dir, ad=None):
        y = self.kos({"giris": klip, "cikti_dir": cikti_dir, "ad": ad})
        return {"konusma": y["konusma"], "diger": y["diger"]}


class Demucs(Roformer):
    ad, motor, ana_paket = "demucs", "demucs", "demucs"


class MuseTalk(YerelMotor):
    """MuseTalk 1.5 (kod MIT; model "any purpose"): ağız bölgesini 256 px'te yeniden üretir. Çıktı yeni dosyadır ve V2 kimlik + S3'ten
    yeniden geçmek zorundadır (TASARIM §2.2 madde 5). 4 GB kartta fp16; GPU belleği yetmezse 3 → Kisitlandi (8 BEKLE)."""
    ad, motor, ortam_adi = "musetalk", "musetalk", "musetalk"
    turler = ("dudak",)
    zaman_asimi = 4 * 3600

    def dudak(self, film, klip, ses_wav, pencere, cikti):
        y = self.kos({"klip": klip, "ses": ses_wav, "pencere": pencere, "cikti": cikti, "fp16": True})
        return {"sure_sn": y.get("sure_sn"), "motor": self.ad}
