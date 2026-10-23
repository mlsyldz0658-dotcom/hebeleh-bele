"""SAĞLAYICILAR — görsel / video / ses / müzik üreten servislerin ortak arayüzü.

Her sağlayıcı bir sınıftır; hangi işleri yaptığını `turler` söyler. İki çeşit sağlayıcı var:
  tek tek : sahne sahne çağrılır  → gorsel(film, sahne, cikti) · video(film, sahne, gorsel, cikti)
                                     ses(film, metin, ses_id, cikti) · muzik(film, sure, cikti)
  toplu   : bütün aşamayı kendisi yürütür (Memmet/Flow gibi) → toplu(film, tur, sahneler)
Sağlayıcı kısıt/uyarı alırsa `Kisitlandi` fırlatır; zincirdeki sıradaki sağlayıcıya geçilir.
Bot tespitini atlatmaya çalışan sağlayıcı YAZILMAZ: uyarıda o sağlayıcı durur, başka servise geçilir ya da hat durur.
Anahtarlar yalnız AYARLAR/ klasöründen ya da ortam değişkeninden okunur; asla yazdırılmaz.
"""
import os, importlib

ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AYARLAR = os.path.join(os.path.dirname(ARACLAR), "AYARLAR")
TURLER = ("gorsel", "video", "ses", "muzik")
# ad → modül.Sınıf. Yeni sağlayıcı (Veo/Kling/kie.ai API, müzik servisi) buraya bir satırla eklenir.
KAYIT = {
    "sahte": "saglayicilar.sahte.Sahte",
    "flow": "saglayicilar.flow.Flow",
    "ai84": "saglayicilar.ai84_ses.AI84Ses",
}


class Kisitlandi(Exception):
    """Sağlayıcı bu iş için kullanılamaz (uyarı, kredi bitti, anahtar yok). Sıradakine geçilir."""


class Saglayici:
    ad = ""
    turler = ()          # bu sağlayıcının yaptığı işler
    toplu_mu = False     # True: aşamanın tamamını toplu() ile kendisi yürütür
    kredili = True       # True: para/kredi harcar → onaylı modda kullanıcıya sorulur

    def hazir(self):
        """(hazır_mı, neden). Anahtar/program eksikse False döner; zincir onu atlar."""
        return True, ""

    def anahtar(self, dosya, ortam):
        """Anahtarı ortam değişkeninden ya da AYARLAR/<dosya> ilk satırından okur. Yoksa None."""
        if os.environ.get(ortam): return os.environ[ortam].strip()
        p = os.path.join(AYARLAR, dosya)
        if os.path.exists(p):
            s = open(p, encoding="utf-8-sig").read().strip()
            if s: return s.splitlines()[0].strip()
        return None


def yukle(ad):
    if ad not in KAYIT: raise ValueError(f"Bilinmeyen sağlayıcı: {ad} (bilinenler: {', '.join(KAYIT)})")
    mod, sinif = KAYIT[ad].rsplit(".", 1)
    return getattr(importlib.import_module(mod), sinif)()


def zincir(tur, adlar, log=print):
    """Bu iş türünü yapabilen ve hazır olan sağlayıcılar, verilen sırayla."""
    out = []
    for ad in adlar:
        s = yukle(ad)
        if tur not in s.turler: continue
        ok, neden = s.hazir()
        if ok: out.append(s)
        else: log(f"   [{ad}] {tur} için hazır değil: {neden}")
    return out
