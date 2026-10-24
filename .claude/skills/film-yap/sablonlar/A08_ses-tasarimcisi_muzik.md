# A08 · ses-tasarimcisi·muzik — Müzik planı

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A08 Ses tasarımı ve müzik planı: S0 HATA 0 olmalı.
Filmin müzik planını yaz: nerede müzik var, nerede yok, leitmotifler (özgün notalar), her ipucunun duygusu ve üretim istemi.

## GIRDI
- `GIRDI/` — duygu ve enerji eğrisi (T0), sahne grubu listesi, evren leitmotifleri (varsa)

## Yap
1. Kaplama oranı {{esik:muzik_kaplama_oran}}; müziksiz blok ≤ {{esik:muziksiz_blok_max_sn}} sn, müzikli blok ≤ {{esik:muzikli_blok_max_sn}} sn.
2. Soğuk açılış {{esik:soguk_acilis_muziksiz_sn}} sn ve en karanlık an {{esik:en_karanlik_muziksiz_sn}} sn müziksiz.
3. Leitmotif en az {{esik:leitmotif_nota_min}} nota; dönüş ≥ {{esik:leitmotif_donus_min}}; BPM {{esik:muzik_bpm_aralik}}.
4. İstem "{{esik:muzik_istem_zorunlu_ifade}}" içerir; sanatçı/stil taklidi yok ({{esik:muzik_istem_yasak_ifadeler}}).

## CIKTI
- `CIKTI/muzik_listesi.json` — `{ipuclari[{id, bas_sahne, bit_sahne, duygu, bpm, motif, istem, giris_sn, cikis_sn}], leitmotifler[{ad, notalar, anlam}]}`

## Bitirmeden
- Müziksiz zorunlu anlar boş.
- İstemlerde yasak ifade yok.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
