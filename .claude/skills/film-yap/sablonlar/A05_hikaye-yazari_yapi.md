# A05 · hikaye-yazari·yapi — Yapı

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A05 Yapı ve senaryo: yapi-denetim ve senaryo-denetim HATA 0 olmalı (Z1/Z2 hikâye ölçüleri, filtre, NE YOK, bilgi durumu).
Kazanan öneriden filmin yapısını kur: üç parti, vuruşlar, sahne listesi, bilgi ve merak sırası.

## GIRDI
- `GIRDI/04_SECIM.json` — kazanan, `mutlaka_duzelt`, `calinmaya_deger`
- `GIRDI/02_oneri_<eksen>.md` — kazanan öneri
- `GIRDI/DERSLER.md` (varsa)

## Yap
1. Yapı {{esik:yapi_baslik_sayisi}} başlık: vuruşlar, partiler (her parti tek cümle), sahne listesi, karakter yayları, kurulum→kullanım, merak soruları, ironi, seyirlik anlar.
2. Sahne sayısı 40 dk için {{esik:sahne_sayisi_40dk}} aralığında (süreye göre orantıla); her sahnede değer değişir.
3. Kahramanın adı ilk {{esik:ad_ilk_gorunus_max_sahne}} sahnede duyulur; risk {{esik:risk_sozlu_max_sn}} sn içinde sözle kurulur.
4. Parti sonu kancası ve en az {{esik:parti_sonu_acik_soru_min}} açık soru; kullanılmayan kurulum {{esik:kurulum_kullanilmayan_max}}.
5. Film alanları: bölüm adı ≤ {{esik:bolum_sayisi_max}}; short adayı parti başına ≥ {{esik:short_aday_parti_min}}; anahtar olgu parti başına {{esik:anahtar_olgu_parti}}; parti sonu yoğunluğu (son parti dışı) ≥ {{esik:parti_sonu_yogunluk_min}}; doruk yoğunluğu ≥ {{esik:doruk_yogunluk_min}}, en karanlık an ≥ {{esik:en_karanlik_yogunluk_min}}; her parti filmin {{esik:parti_sure_oran_aralik}} oranında.
6. Revizyon turundaysan: `mutlaka_duzelt` maddelerini ve yapı denetimi raporunu madde madde kapat.

## CIKTI
- `CIKTI/05_YAPI.json` — `{partiler[], vuruslar[], sahneler[{id, parti, ozet, deger_degisimi, mekan, karakterler, bilgi_durumu}], kurulumlar[], merak[], ironi[], seyirlik_anlar[]}`

## Bitirmeden
- Her sahnenin değer değişimi yazılı.
- Kurulumların hepsi bir kullanımla eşleşiyor.
- Sayılar eşiklerin içinde.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
