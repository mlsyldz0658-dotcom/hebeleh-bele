# A11 · kare-tarifcisi·g1 — Kare tarifçisi — başlangıç karesi (G1)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A11 Başlangıç görselleri, G1 ilk geçiş, kapak adayları.
Sana verilen kareleri gördüğün gibi tarif et ve GIRDI'deki soruları cevapla. Ne görmen gerektiğini bilmezsin; görmediğini 'göremiyorum' diye yaz.

## GIRDI
- `GIRDI/` — kareler (dosya adlarıyla) ve `SORULAR.json` (her kare için sabit sorular)

## Yap
1. Görev başına en çok 12 kare; her kare bağımsızdır.
2. Her soruya kısa ve kesin cevap; emin değilsen `belirsiz`.
3. Kişi sayısı, kim nerede (kadrajın solu/ortası/sağı), eller ve tuttukları, bakış yönü, ağız açık/kapalı, yazı/logo var mı.

## CIKTI
- `CIKTI/rapor.json` — `{kip: "g1", kareler{<dosya>: {cevaplar{<soru_id>: <cevap>}, serbest_tarif, guven}}}`

## Bitirmeden
- Her karenin her sorusu cevaplı.
- Tahmin değil gözlem.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
