"""BÜYÜTÜCÜ — 720p'den yayın görüntüsüne (TASARIM D-29, §6.5 `buyut.py`, §5.6 `buyutme` zinciri: yz_buyutucu · lanczos · sahte).

YZBuyutucu: Real-ESRGAN türü 2× büyütücü (kod BSD-3; ağırlık lisansı KUR3'te doğrulanır), ayrı CUDA ortamında (YOLLAR ortamlar.buyutme)
`motor_kosucu.py realesrgan` ile. Lanczos: ffmpeg lanczos + ince gren (yedek yol; her zaman hazır, ffmpeg varsa).
Büyütücü yüzü değiştiremez: buyut.py her çıktıda yüz bölgesini yeniden ölçer (SFace); geçmezse o plan Lanczos'a düşer.
"""
import os, sys, shutil
ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
from saglayicilar import Saglayici, Kisitlandi
from saglayicilar.yerel_ses import YerelMotor


class YZBuyutucu(YerelMotor):
    ad, motor, ortam_adi = "yz_buyutucu", "realesrgan", "buyutme"
    turler = ("buyutme",)
    zaman_asimi = 6 * 3600

    def buyut(self, film, giris, cikti, olcek=2):
        y = self.kos({"giris": giris, "cikti": cikti, "olcek": olcek})
        return {"motor": self.ad, "yz": True, "sure_sn": y.get("sure_sn")}


class Lanczos(Saglayici):
    ad = "lanczos"
    turler = ("buyutme",)
    kredili = False
    ortam = "her_ikisi"
    elle = False
    gren = 4

    def hazir(self):
        return (True, "") if shutil.which("ffmpeg") else (False, "ffmpeg yok")

    def buyut(self, film, giris, cikti, olcek=2):
        import kurgu_ortak as ko
        if not shutil.which("ffmpeg"): raise Kisitlandi("ffmpeg yok", kod="hazir_degil")
        ko.ffmpeg("-i", giris, "-vf", f"scale=iw*{olcek}:ih*{olcek}:flags=lanczos,noise=alls={self.gren}:allf=t,format=yuv420p",
                  "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-c:a", "copy", cikti)
        return {"motor": self.ad, "yz": False}
