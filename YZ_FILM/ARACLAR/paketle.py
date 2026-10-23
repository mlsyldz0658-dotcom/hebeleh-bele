"""PAKETLE — YZ_FILM'i başka bilgisayara taşınabilir zip yapar. Gizli ve ağır dosyalar girmez.
Kullanım: python paketle.py [hedef_klasor]   (varsayılan: Masaüstü)
Girer : BASLA_BURADAN.txt, KURULUM.bat, 00_BENI_OKU.txt, ARACLAR (programlar), BILGI,
        AYARLAR (yalnız boş şablonlar), FILMLER/ORNEK_3_SAHNE (örnek film: sahne listesi + karakter görselleri)
Girmez: anahtarlar, Memmet Chrome profili (Google oturumu), film çıktıları, önbellekler
Sonunda zip'in içinde anahtarların geçmediğini tarar.
"""
import os, sys, json, zipfile, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)   # ROOT: depodaki YZ_FILM (paketlenen)
sys.path.insert(0, HERE)
import ortak
VERI = ortak.yollar()                  # örnek film ve gizli anahtar taraması veri kökünden (YOLLAR.json)

KOK = ["BASLA_BURADAN.txt", "KURULUM.bat", "00_BENI_OKU.txt"]
ATLA_KLASOR = {"__pycache__", "memmet_profil"}
ATLA_ON = ("_",)                       # ARACLAR içindeki _deneme.png gibi geçici dosyalar
ORNEK_KAYNAK = os.path.join(VERI["filmler"], "MEMMET_TEST")
PILOT = os.path.join(VERI["filmler"], "EMBERFALL_PILOT", "SAHNELER.json")
AYAR_OKU = ("BU KLASÖR GİZLİDİR. Paylaşma.\n\n"
            "ai84_anahtar.txt   → AI84.pro API anahtarını İLK SATIRA yapıştır (seslendirme)\n"
            "telegram_bot.txt   → Telegram bot anahtarını İLK SATIRA yapıştır (isteğe bağlı). Sonra:\n"
            "                     python ARACLAR\\memmet.py --telegram-test\n"
            "memmet_profil\\     → MEMMET_GIRIS.bat ile Google'a girince kendiliğinden oluşur\n"
            "MEMMET_AYAR.json   → isteğe bağlı; Memmet temposunu yalnız YAVAŞLATABİLİR (hızlı değer yok sayılır)\n")


def main(hedef):
    ad = f"YZ_FILM_PAKET_{time.strftime('%Y-%m-%d')}.zip"; zp = os.path.join(hedef, ad)
    n = 0
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        def ekle(src, arc):
            nonlocal n; z.write(src, "YZ_FILM/" + arc.replace("\\", "/")); n += 1
        for f in KOK:
            if os.path.exists(os.path.join(ROOT, f)): ekle(os.path.join(ROOT, f), f)
        for top in ("ARACLAR", "BILGI"):
            for dp, dns, fns in os.walk(os.path.join(ROOT, top)):
                dns[:] = [d for d in dns if d not in ATLA_KLASOR]
                for f in fns:
                    if f.endswith((".pyc", ".part")) or (top == "ARACLAR" and f.startswith(ATLA_ON)) or f == "MEMMET_AYAR.json": continue
                    p = os.path.join(dp, f); ekle(p, os.path.relpath(p, ROOT))
        # AYARLAR: yalnız boş şablonlar
        z.writestr("YZ_FILM/AYARLAR/OKU_BENI.txt", AYAR_OKU)
        z.writestr("YZ_FILM/AYARLAR/ai84_anahtar.txt", ""); z.writestr("YZ_FILM/AYARLAR/telegram_bot.txt", "")
        # örnek film
        if os.path.exists(os.path.join(ORNEK_KAYNAK, "SAHNELER.json")):
            s = json.load(open(os.path.join(ORNEK_KAYNAK, "SAHNELER.json"), encoding="utf-8")); s["film"] = "ORNEK_3_SAHNE"
            base = "YZ_FILM/FILMLER/ORNEK_3_SAHNE/"
            z.writestr(base + "SAHNELER.json", json.dumps(s, ensure_ascii=False, indent=1))
            for f in os.listdir(os.path.join(ORNEK_KAYNAK, "01_KARAKTERLER")):
                z.write(os.path.join(ORNEK_KAYNAK, "01_KARAKTERLER", f), base + "01_KARAKTERLER/" + f)
            # film .bat'ları pakete girmez: mutlak yol içerirler, alan bilgisayarda yeni_film.batlar() ile yeniden yazılır
            z.writestr(base + "GELENLER/BURAYA_FLOW_ZIPLERI.txt", "Elle indirdiğin Flow zip'lerini buraya at, KONTROL.bat'a bas.\n")
            z.writestr(base + "DUZELT.txt", "")
        if os.path.exists(PILOT): z.write(PILOT, "YZ_FILM/BILGI/ORNEK_SAHNELER_EMBERFALL_PILOT_20sahne.json")
    # güvenlik taraması: anahtarlar zip'te geçiyor mu?
    gizli = []
    for f in [os.path.join(k, a) for k in (os.path.join(ROOT, "AYARLAR"), VERI["ayarlar"]) for a in ("ai84_anahtar.txt", "telegram_bot.txt")]:
        p = f
        if os.path.exists(p): gizli += [l.strip() for l in open(p, encoding="utf-8-sig") if len(l.strip()) >= 20]
    sizinti, profil = [], False
    with zipfile.ZipFile(zp) as z:
        for i in z.infolist():
            if "memmet_profil" in i.filename: profil = True
            if i.file_size < 5_000_000:
                data = z.read(i.filename)
                if any(g.encode() in data for g in gizli): sizinti.append(i.filename)
    boyut = os.path.getsize(zp) / 1e6
    print(f"PAKET: {zp}\n  {n + 6} dosya · {boyut:.1f} MB")
    if sizinti or profil:
        os.remove(zp); print("!! GÜVENLİK: anahtar ya da Google profili pakete girmiş, paket SİLİNDİ:", sizinti, "profil" if profil else ""); sys.exit(1)
    print("  Güvenlik taraması temiz: anahtar ve Google oturumu pakette yok.")
    return zp


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.expanduser("~"), "Desktop"))
