"""SAĞLAYICILAR — görsel / video / ses / müzik üreten servislerin ortak arayüzü.

Her sağlayıcı bir sınıftır; hangi işleri yaptığını `turler` söyler. İki çeşit sağlayıcı var:
  tek tek : sahne sahne çağrılır  → gorsel(film, sahne, cikti) · video(film, sahne, gorsel, cikti)
                                     ses(film, metin, ses_id, cikti) · muzik(film, sure, cikti)
  toplu   : bütün aşamayı kendisi yürütür (Memmet/Flow gibi) → toplu(film, tur, sahneler)
Sağlayıcı kullanılamazsa `Kisitlandi(mesaj, kod=...)` fırlatır. Sıradaki sağlayıcıya YALNIZ `GECILEBILIR` kodlarda geçilir
(anahtar yok, ağ, kota, kredi). `olagandisi` (Flow uyarısı), `dogrulama`, `giris` ve kodu bilinmeyen kısıt hattı DURDURUR:
uyarıdan sonra başka servise ya da hesaba geçmek bot tespitini atlatmanın bir biçimidir (kapalı başarısız).
Bot tespitini atlatmaya çalışan sağlayıcı YAZILMAZ.
Anahtarlar yalnız AYARLAR/ klasöründen ya da ortam değişkeninden okunur; asla yazdırılmaz.
"""
import os, sys, importlib

ARACLAR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import ortak


def ayarlar_klasoru(): return ortak.yollar()["ayarlar"]     # <veri>/AYARLAR; YOLLAR.json yoksa ortak.YolYok
# v1 hattının işleri (gorsel, video, ses, muzik) + v2 dilimlerinin türleri (ADLAR saglayici_turleri adlarıyla).
TURLER = ("gorsel", "video", "ses", "muzik", "tts", "asr", "ses_donustur", "ayristirma", "dudak", "buyutme", "izleyici", "dinleyici")
# ad → modül.Sınıf. Yeni sağlayıcı (Veo/Vertex API, müzik servisi) buraya bir satırla eklenir. ADLAR saglayici_dislanan'daki
# servisler ve modeller (ör. Wav2Lip, Seed-VC) YAZILMAZ. Test sağlayıcıları (sahte*, kaset) gerçek zincirde atlanır (D-41).
KAYIT = {
    # test / sahte
    "sahte": "saglayicilar.sahte.Sahte",
    "kaset": "saglayicilar.kaset.Kaset",
    "ses_sahte": "saglayicilar.ses_sahte.SesSahte",
    "sahte_kurgu": "saglayicilar.sahte_kurgu.SahteKurgu",
    "sahte_izleyici": "saglayicilar.izleyici.SahteIzleyici",
    "sahte_dinleyici": "saglayicilar.dinleyici.SahteDinleyici",
    # görsel / video
    "flow": "saglayicilar.flow.Flow",
    "gemini_api": "saglayicilar.gemini_api.GeminiAPI",
    # izleme / dinleme (ikinci göz; yalnız BAYRAK)
    "izleyici": "saglayicilar.izleyici.Izleyici",
    "dinleyici": "saglayicilar.dinleyici.Dinleyici",
    # ses: tts (v1 ses() de AI84Tts'te), asr, dönüştürme, ayrıştırma, dudak
    "ai84": "saglayicilar.ai84_tts.AI84Tts",
    "faster_whisper": "saglayicilar.asr_whisper.FasterWhisper",   # ana ortamda + stable-ts hizalaması (yerel_ses.FasterWhisper değil)
    "openvoice": "saglayicilar.yerel_ses.OpenVoice",
    "chatterbox": "saglayicilar.yerel_ses.Chatterbox",
    "rvc": "saglayicilar.yerel_ses.RVC",
    "roformer": "saglayicilar.yerel_ses.Roformer",
    "demucs": "saglayicilar.yerel_ses.Demucs",
    "musetalk": "saglayicilar.yerel_ses.MuseTalk",
    # müzik
    "acestep": "saglayicilar.acestep.AceStep",
    "kutuphane": "saglayicilar.kutuphane.Kutuphane",
    "gemini_muzik_paketi": "saglayicilar.gemini_muzik_paketi.GeminiMuzikPaketi",
    "midi_ornek": "saglayicilar.midi_ornek.MidiOrnek",
    # büyütme
    "yz_buyutucu": "saglayicilar.buyutucu.YZBuyutucu",
    "lanczos": "saglayicilar.buyutucu.Lanczos",
}


GECILEBILIR = ("anahtar", "ag", "kota", "kredi", "hazir_degil")   # bunlarda sıradaki sağlayıcı denenebilir


class Kisitlandi(Exception):
    """Sağlayıcı bu iş için kullanılamaz. kod GECILEBILIR içindeyse sıradakine geçilir; değilse hat durur."""
    def __init__(self, msg="", kod="bilinmeyen"):
        super().__init__(msg); self.kod = kod

    @property
    def gecilebilir(self): return self.kod in GECILEBILIR


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
        try: p = os.path.join(ayarlar_klasoru(), dosya)
        except ortak.YolYok: return None
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
