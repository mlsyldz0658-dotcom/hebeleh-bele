"""YENİ FİLM — FILMLER altında boş bir film klasörü kurar (klasörler, .bat dosyaları, örnek SAHNELER.json).
Kullanım: python yeni_film.py FILM_ADI     (YENI_FILM.bat sorar)
SAHNELER.json'u Claude doldurur; karakter görselleri 01_KARAKTERLER'e konur.
"""
import os, sys, json, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)

HEAD = "@echo off\r\nchcp 65001 >nul\r\n"
PY = '"%~dp0..\\..\\ARACLAR\\{}" "%~dp0."'
BATS = {
    "KONTROL.bat": HEAD + "python " + PY.format("kontrol.py") + "\r\npause\r\n",
    "MEMMET_GIRIS.bat": HEAD + "echo Memmet Chrome'u acilacak. Flow'a bir kez Google hesabinla giris yap.\r\npython " + PY.format("memmet.py") + " --giris\r\npause\r\n",
    "MEMMET_BASLAT.bat": HEAD + "echo Memmet calisiyor: gorseller, videolar, seslendirme, CapCut projesi. Memmet Chrome penceresine dokunma.\r\npython " + PY.format("memmet.py") + "\r\npause\r\n",
    "MEMMET_SADECE_GORSEL.bat": HEAD + "python " + PY.format("memmet.py") + " --asama gorsel --kurgu-yok\r\npause\r\n",
    "MEMMET_SADECE_VIDEO.bat": HEAD + "python " + PY.format("memmet.py") + " --asama video\r\npause\r\n",
    "CAPCUT_PROJESI_OLUSTUR.bat": HEAD + "echo CapCut'i kapat, sonra bir tusa bas.\r\npause >nul\r\npython " + PY.format("seslendir.py") +
        "\r\nif errorlevel 1 goto hata\r\npython " + PY.format("capcut_film.py") + "\r\nif errorlevel 1 goto hata\r\necho TAMAM. CapCut'i ac; proje en ustte.\r\npause\r\nexit /b\r\n:hata\r\necho HATA OLDU. Ekran goruntusunu Claude'a gonder.\r\npause\r\n",
    "NOTLARI_OKU.bat": HEAD + "python " + PY.format("notlari_oku.py") + "\r\npause\r\n",
    "FILM_HATTI.bat": HEAD + "echo Film hatti calisiyor. Kredi harcayan asamadan once onay sorar.\r\npython " + PY.format("film.py") + "\r\npause\r\n",
    "FILM_DENEME_SAHTE.bat": HEAD + "echo Kredisiz deneme: sahte gorsel/video/ses ile hatti dener.\r\npython " + PY.format("film.py") + " --saglayici sahte\r\npause\r\n",
}
SABLON = {
    "film": "", "baslik": "Kanca cümlesi | SERİ ADI | Full Movie 4K 2026", "altyazi_dili": None,
    "karakterler": {"ornek_karakter": {"ref": "01_KARAKTERLER/ornek_karakter.jpg", "ses": None, "ses_adi": None}},
    "sahneler": [{"no": 1, "parti": 1, "referans": ["ornek_karakter"], "amac": "", "duygu": "",
                  "gorsel_istem": "İngilizce görsel istemi", "gorsel_istem_yedek": "",
                  "hareket_istem": "İngilizce hareket istemi", "hareket_istem_yedek": "",
                  "replik": {"karakter": "ornek_karakter", "metin": "Line.", "cumleler": [{"en": "Line.", "tr": "Replik."}]}}],
}


def kur(ad):
    ad = re.sub(r"[^A-Za-z0-9_\-]", "_", ad.strip().upper())
    d = os.path.join(ROOT, "FILMLER", ad)
    if os.path.exists(os.path.join(d, "SAHNELER.json")): print("Bu film zaten var:", d); return d
    for k in ("01_KARAKTERLER", "GELENLER"): os.makedirs(os.path.join(d, k), exist_ok=True)
    for b, icerik in BATS.items(): open(os.path.join(d, b), "w", encoding="ascii", newline="").write(icerik)
    s = dict(SABLON); s["film"] = ad
    json.dump(s, open(os.path.join(d, "SAHNELER.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(d, "DUZELT.txt"), "w", encoding="utf-8").write("")
    print("Film klasörü hazır:", d); return d


if __name__ == "__main__":
    kur(sys.argv[1] if len(sys.argv) > 1 else input("Film adı: "))
