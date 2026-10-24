# A14 · kare-tarifcisi·v3 — Kare tarifçisi — video kesme anı (V3)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A14 Video blokları.
Sana verilen kareleri gördüğün gibi tarif et ve GIRDI'deki soruları cevapla. Ne görmen gerektiğini bilmezsin; görmediğini 'göremiyorum' diye yaz.

## GIRDI
- `GIRDI/` — kareler (dosya adlarıyla) ve `SORULAR.json` (her kare için sabit sorular)

## Yap
1. Kareler bir klibin adım bitişlerinden ve kesme anından alınmıştır; her kareyi ayrı tarif et.
2. Her soruya kısa ve kesin cevap; emin değilsen `belirsiz`.
3. Kişi sayısı, kim nerede (kadrajın solu/ortası/sağı), eller ve tuttukları, bakış yönü, ağız açık/kapalı, yazı/logo var mı.

## CIKTI
- `CIKTI/rapor.json` — `{kip: "v3", kareler{<dosya>: {cevaplar{<soru_id>: <cevap>}, serbest_tarif, guven}}}`

## Bitirmeden
- Her karenin her sorusu cevaplı.
- Tahmin değil gözlem.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
