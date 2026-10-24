"""YENİ FİLM — FILMLER altında boş bir film klasörü kurar (klasörler, .bat dosyaları, örnek SAHNELER.json).
Kullanım: python yeni_film.py FILM_ADI
.bat'lar bat_yenile.py'den gelir (DEVAM, DURDUR, KONTROL, NOTLARI_OKU, FILM_DENEME_SAHTE; mutlak yollu, ASCII + CRLF).
Eski MEMMET_BASLAT / MEMMET_SADECE_* / CAPCUT_PROJESI_OLUSTUR / FILM_HATTI .bat'ları emekli (kapıları atlıyorlardı); üretilmez.
MEMMET_GIRIS.bat da üretilmez: Flow girişi depo kökündeki FLOW_GIRIS.bat'tadır.
SAHNELER.json'u Claude doldurur; karakter görselleri 01_KARAKTERLER'e konur.
"""
import os, sys, json, re
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import ortak, bat_yenile

# Film klasörüne yazılan .bat'lar (adlar veri/ADLAR.json "bat.film_klasoru"); içerikleri bat_yenile.py üretir.
BATS = {"DEVAM.bat": "Claude Code'da filmi sürdürür", "DURDUR.bat": "set yeni iş başlatmaz",
        "KONTROL.bat": "film klasörünü denetler", "NOTLARI_OKU.bat": "CapCut notlarını okur",
        "FILM_DENEME_SAHTE.bat": "kredisiz sahte deneme"}


def batlar(python=None, araclar=None):
    """Film klasörünün .bat'ları {ad: içerik}. Python ve betik MUTLAK yolla (bat_yenile.py; göreli ..\\..\\ARACLAR yok).
    Flow girişi film klasöründe değil, depo kökündeki FLOW_GIRIS.bat'tadır (eski MEMMET_GIRIS.bat üretilmez)."""
    hepsi = bat_yenile.film_batlari(python, araclar)
    return {ad: hepsi[ad] for ad in BATS}


def bat_yaz(yol, icerik):
    """ASCII + CRLF (yol ASCII dışı harf içeriyorsa UTF-8; başta chcp 65001 var). bat_yenile.bat_yaz."""
    return bat_yenile.bat_yaz(yol, icerik)


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
    if len(sys.argv) < 2: print(__doc__); sys.exit(4)        # film adı sorulmaz (KK1); film.py yeni ad verir
    kur(sys.argv[1])
