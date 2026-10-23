"""YZ_FILM KURULUM — yeni bir bilgisayarda her şeyi hazırlar ve sonunda kendini test eder.
KURULUM.bat çalıştırır. Birden fazla kez çalıştırmak güvenlidir (kurulu olanı atlar).
"""
import os, sys, subprocess, shutil, glob, importlib.util, json
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
KD = os.path.join(HERE, "kurulum_dosyalari"); AYARLAR = os.path.join(ROOT, "AYARLAR")
SONUC = []


def baslik(t): print("\n" + "=" * 64 + f"\n {t}\n" + "=" * 64, flush=True)
def ok(t): SONUC.append(("✅", t)); print("  ✅", t, flush=True)
def uyari(t): SONUC.append(("⚠️", t)); print("  ⚠️ ", t, flush=True)
def hata(t): SONUC.append(("❌", t)); print("  ❌", t, flush=True)
def var(m): return importlib.util.find_spec(m) is not None


def pip(*args):
    """pip; sertifika sorunu olan bilgisayarlarda (antivirüs vb.) Windows sertifika deposuyla tekrar dener."""
    base = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
    r = subprocess.run(base + list(args))
    if r.returncode == 0: return True
    print("  (pip başarısız; Windows sertifika deposuyla tekrar deneniyor)")
    whl = glob.glob(os.path.join(KD, "truststore-*.whl"))
    if whl and not var("truststore"): subprocess.run(base + ["--no-index", whl[0]])
    return subprocess.run(base + ["--use-feature=truststore"] + list(args)).returncode == 0


def main():
    baslik("1/7 Python")
    v = sys.version_info
    if v < (3, 10): hata(f"Python {v.major}.{v.minor} eski. Python 3.10 ya da 3.11 kur (python.org), 'Add to PATH' işaretle."); return
    ok(f"Python {v.major}.{v.minor}.{v.micro}")
    if v >= (3, 13): uyari("Python 3.13+ ile bazı kütüphaneler sorun çıkarabilir; sorun olursa 3.10/3.11 kur.")

    baslik("2/7 PyTorch (yapay zekâ altyapısı, büyük indirme ~2-3 GB)")
    if var("torch"): ok("torch zaten kurulu")
    else:
        nvidia = shutil.which("nvidia-smi") is not None
        print("  NVIDIA ekran kartı:", "var → CUDA sürümü kuruluyor" if nvidia else "yok → işlemci sürümü kuruluyor")
        idx = "https://download.pytorch.org/whl/cu124" if nvidia else "https://download.pytorch.org/whl/cpu"
        (ok if pip("torch", "torchaudio", "--index-url", idx) else hata)("torch kurulumu")

    baslik("3/7 Diğer kütüphaneler")
    (ok if pip("-r", os.path.join(KD, "requirements.txt")) else hata)("requirements.txt")

    baslik("4/7 ffmpeg (video/ses işleme)")
    if shutil.which("ffmpeg") and shutil.which("ffprobe"): ok("ffmpeg bulundu")
    else:
        print("  ffmpeg yok; winget ile kurulmaya çalışılıyor...")
        subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg", "--accept-package-agreements", "--accept-source-agreements"])
        if shutil.which("ffmpeg"): ok("ffmpeg kuruldu")
        else: uyari("ffmpeg kuruldu ama görünmüyor olabilir: bu pencereyi kapat, KURULUM.bat'ı yeniden çalıştır. "
                    "Olmazsa https://www.gyan.dev/ffmpeg/builds/ adresinden indirip bin klasörünü PATH'e ekle.")

    baslik("5/7 Programlar: Chrome ve CapCut")
    sys.path.insert(0, HERE)
    import memmet
    c = memmet.chrome_bul()
    (ok if os.path.exists(c) else hata)(f"Google Chrome: {c if os.path.exists(c) else 'BULUNAMADI — google.com/chrome adresinden kur'}")
    capcut = os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft")
    (ok if os.path.isdir(capcut) else uyari)("CapCut masaüstü: " + ("bulundu" if os.path.isdir(capcut) else
        "proje klasörü yok — CapCut'ı (capcut.com) kur, bir kez açıp boş bir proje oluştur, kapat"))

    baslik("6/7 Yapay zekâ modelleri (ilk sefer indirilir)")
    try:
        from transformers import CLIPModel, CLIPProcessor
        CLIPModel.from_pretrained("openai/clip-vit-base-patch16"); CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16")
        ok("CLIP (görsel eşleştirme)")
    except Exception as e: hata(f"CLIP indirilemedi: {str(e)[:120]}")
    try:
        from faster_whisper import WhisperModel
        WhisperModel("small.en", device="cpu", compute_type="int8"); ok("Whisper small.en (konuşma tespiti)")
    except Exception as e: hata(f"Whisper indirilemedi: {str(e)[:120]}")
    try:
        from demucs.pretrained import get_model
        get_model("htdemucs"); ok("Demucs htdemucs (ses ayırma)")
    except Exception as e: hata(f"Demucs modeli indirilemedi: {str(e)[:120]}")

    baslik("7/7 Ayarlar ve hesaplar")
    os.makedirs(AYARLAR, exist_ok=True)
    for ad, aciklama in (("ai84_anahtar.txt", "AI84.pro (ElevenLabs) API anahtarı — seslendirme için"),
                         ("telegram_bot.txt", "Telegram bot anahtarı — telefon bildirimi için (isteğe bağlı)")):
        p = os.path.join(AYARLAR, ad)
        if not os.path.exists(p): open(p, "w", encoding="utf-8").close()
        dolu = bool(open(p, encoding="utf-8-sig").read().strip())
        (ok if dolu else uyari)(f"{ad}: " + ("dolu" if dolu else f"BOŞ — {aciklama}. BASLA_BURADAN.txt'deki adımlara bak"))
    prof = os.path.join(AYARLAR, "memmet_profil")
    (ok if os.path.isdir(prof) else uyari)("Memmet Google girişi: " + ("profil var" if os.path.isdir(prof) else
        "henüz yok — bir filmin klasöründe MEMMET_GIRIS.bat'ı çalıştırıp Flow'a giriş yap"))

    baslik("SONUÇ")
    for i, t in SONUC: print(" ", i, t)
    hatalar = [t for i, t in SONUC if i == "❌"]
    print("\n" + ("KURULUM TAMAM. Sıradaki adım: BASLA_BURADAN.txt → 'İLK KULLANIM'." if not hatalar else
                  f"{len(hatalar)} sorun var. Yukarıdaki ❌ satırlarını düzeltip KURULUM.bat'ı tekrar çalıştır."))


if __name__ == "__main__":
    main()
