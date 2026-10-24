# A10c · ses-tasarimcisi·kadro — Ses kadrosu

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A10c Ses seçimi: puan farkı çok yakınsa karar sende.
Konuşan her karakter için ses profili ve Veo'nun okuyacağı tek satırlık ses tarifini yaz; kadro birbirinden ayrışsın.

Bu görev bir **merdiven basamağıdır** (§1.5): önceki turların kapı raporu ve maddeleri GIRDI'dedir; çıktın `CIKTI/rapor.json`.

## GIRDI
- `GIRDI/HIKAYE.json` dilimi — karakterler (`ses_karakteri`, `ad_telaffuz`)
- `GIRDI/` evren ses kayıtları (varsa)

## Yap
1. Profil alanları: {{esik:ses_profil_alanlari}}.
2. `veo_ses_tarifi` ≤ {{esik:veo_ses_tarifi_kelime_max}} kelime, sıra: tını + cinsiyet + aksan ("in a low, husky female voice with a northern English accent"); yaş sözcüğü ve filtre sözcüğü yok; aksan bilinmiyorsa "neutral".
3. Aynı yaş bandındaki iki karakter tını ya da perdeyle belirgin ayrışır.
4. A10c'de (yakın puan) adaylar arasında karar ver: gerekçe ölçü sırasıyla (benzerlik, doğallık, ayrışma).

## CIKTI
- A06s: `CIKTI/SES_PROFILLERI.json` — `{karakterler{<id>: {cinsiyet, yas_bandi, aksan, perde, tini, veo_ses_tarifi, ayrisma_notu}}}`
- Merdiven/A10c turunda `CIKTI/rapor.json` (dosya listesi ISTEM.md'de)

## Bitirmeden
- Her tarif kelime sınırında.
- Yaş sözcüğü yok.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
