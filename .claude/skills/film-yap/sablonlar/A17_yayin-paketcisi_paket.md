# A17 · yayin-paketcisi·paket — Yayın paketi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A17 Yayın: paket doğrulama HATA 0.
YouTube yayın paketini yaz: başlık, açıklama, bölümler, etiketler, YZ beyanı, Shorts ve fragman listesi. Kanal teşhisine dayan.

## GIRDI
- `GIRDI/` — HIKAYE özeti, KURGU_PLANI özeti (bölüm zamanları), KANAL_TESHIS.md (varsa), kapak adayları

## Yap
1. Başlık ≤ {{esik:baslik_karakter_max}} karakter; kanca cümlesi ≤ {{esik:kanca_cumlesi_karakter_max}} karakter.
2. Bölümler ≤ {{esik:bolum_sayisi_max}}; ilk bölüm 00:00.
3. YZ beyanı alanı dolu.
4. Short adayı parti başına ≥ {{esik:short_aday_parti_min}}; her biri zaman aralığıyla.

## CIKTI
- `CIKTI/PAKET.json` — `{baslik, aciklama, bolumler[{zaman, ad}], etiketler[], yz_beyani, shorts[{bas, bit, baslik}], fragman{bas, bit}}`

## Bitirmeden
- Başlık sınırı tuttu.
- Bölüm zamanları KURGU_PLANI ile uyumlu.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
