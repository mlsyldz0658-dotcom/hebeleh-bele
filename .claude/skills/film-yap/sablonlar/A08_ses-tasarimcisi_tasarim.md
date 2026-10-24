# A08 · ses-tasarimcisi·tasarim — Ses tasarımı (sahne grubu)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A08 Ses tasarımı ve müzik planı: S0 HATA 0 olmalı.
Bir sahne grubunun ses planını yaz: yatak (ambiyans), efekt olayları, plan başına flow_sound, sessizlikler.

GOREV.json `merdiven` alanı doluysa bu bir **merdiven basamağıdır** (§1.5): raporu ve maddeleri GIRDI'den oku; ISTEM.md'deki dosya listesi esastır.

## GIRDI
- `GIRDI/` — sahne grubunun planları (eylem adımları, mekân, zaman), `ses_plani --taslak` önerileri, ses kütüphanesi dizini

## Yap
1. Yatak: grup başına ≤ {{esik:yatak_sahne_grubu_max}}; seviye diyalogun {{esik:ambiyans_diyalog_alti_db}} dB altı.
2. Efekt: her fiziksel adım için kategori (`efekt_sozlugu`), an (adımın bas/orta/bit ± {{esik:efekt_an_pay_sn}} sn), malzeme; söze ≥ {{esik:efekt_soz_uzaklik_min_ms}} ms.
3. flow_sound: "Sound: … No music." ≤ {{esik:flow_sound_kelime_max}} kelime; müzik sözcüğü yok.
4. Merdiven turundaysan: S0 maddelerini kapatan dar düzeltme; kapatamazsan kod varsayılanı (tek yatak, efektsiz) kabul et ve BAYRAK yaz.

## CIKTI
- `CIKTI/SES.json` — `{grup, yatak{}, planlar{<no>: {efektler[], flow_sound, sessizlik, dis_katman_db}}}`
- Merdiven turunda `CIKTI/rapor.json`

## Bitirmeden
- Her plana flow_sound yazıldı.
- Efekt anları adımlarla eşleşiyor.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
