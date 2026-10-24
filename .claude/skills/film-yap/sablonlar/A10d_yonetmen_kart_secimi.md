# A10d · yonetmen·kart_secimi — Kart seçimi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A10d Kartlar: KART HATA 0; tarif revizyonu küresel bütçeden.
Kart kapısından geçen ya da en iyi teknik adayları arasından her karakter/mekân görünümü için kartı seç.

GOREV.json `merdiven` alanı doluysa bu bir **merdiven basamağıdır** (§1.5): raporu ve maddeleri GIRDI'den oku; ISTEM.md'deki dosya listesi esastır.

## GIRDI
- `GIRDI/` — aday kartlar, `KART_KAPISI` raporu, kör gözlem raporları, kart tarifi (KART_SPEC)

## Yap
1. Önce HATA'sız adaylar; aralarında kimlik tutarlılığı ve tarife sadakat.
2. Bütün adaylar HATA'lıysa (tarif revizyonu bütçesi doldu): en iyi teknik adayı seç ve BAYRAK yaz.

## CIKTI
- `CIKTI/KART_SECIM.json` — `{secimler{<kart_id>: {aday, gerekce, bayrak}}}`
- Merdiven turunda `CIKTI/rapor.json`

## Bitirmeden
- Her kartın bir seçimi var.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
