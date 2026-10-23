"""YENİ FİLM — FILMLER altında boş bir film klasörü kurar (klasörler, .bat dosyaları, örnek SAHNELER.json).
Kullanım: python yeni_film.py FILM_ADI
Eski MEMMET_BASLAT / MEMMET_SADECE_* / CAPCUT_PROJESI_OLUSTUR / FILM_HATTI .bat'ları emekli (kapıları atlıyorlardı); üretilmez.
SAHNELER.json'u Claude doldurur; karakter görselleri 01_KARAKTERLER'e konur.
"""
import os, sys, json, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak

HEAD = "@echo off\r\nchcp 65001 >nul\r\n"


def batlar(python=None, araclar=None):
    """Film klasörünün .bat'ları. Python ve betik MUTLAK yolla çağrılır (göreli ..\\..\\ARACLAR yok); yollar YOLLAR.json'dan."""
    if python is None or araclar is None:
        y = ortak.yollar(); python = python or y["python"]["ana"]; araclar = araclar or y["araclar"]
    py = lambda betik: f'"{python}" "{os.path.join(araclar, betik)}" "%~dp0."'
    return {
        "KONTROL.bat": HEAD + py("kontrol.py") + "\r\npause\r\n",
        "MEMMET_GIRIS.bat": HEAD + "echo Memmet Chrome'u acilacak. Flow'a bir kez Google hesabinla giris yap.\r\n" + py("memmet.py") + " --giris\r\npause\r\n",
        "NOTLARI_OKU.bat": HEAD + py("notlari_oku.py") + "\r\npause\r\n",
        "FILM_DENEME_SAHTE.bat": HEAD + "echo Kredisiz deneme: sahte gorsel/video/ses ile hatti dener.\r\n" + py("film.py") + " --saglayici sahte\r\npause\r\n",
    }


def bat_yaz(yol, icerik):
    """ASCII + CRLF; yol ASCII dışı harf içeriyorsa (ör. kullanıcı adı) UTF-8 (başta chcp 65001 var)."""
    try: b = icerik.encode("ascii")
    except UnicodeEncodeError: b = icerik.encode("utf-8")
    with open(yol, "wb") as f: f.write(b)
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
    d = os.path.join(ortak.yollar()["filmler"], ad)
    if os.path.exists(os.path.join(d, "SAHNELER.json")): print("Bu film zaten var:", d); return d
    for k in ("01_KARAKTERLER", "GELENLER"): os.makedirs(os.path.join(d, k), exist_ok=True)
    for b, icerik in batlar().items(): bat_yaz(os.path.join(d, b), icerik)
    s = dict(SABLON); s["film"] = ad
    json.dump(s, open(os.path.join(d, "SAHNELER.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(os.path.join(d, "DUZELT.txt"), "w", encoding="utf-8").write("")
    print("Film klasörü hazır:", d); return d


if __name__ == "__main__":
    kur(sys.argv[1] if len(sys.argv) > 1 else input("Film adı: "))
