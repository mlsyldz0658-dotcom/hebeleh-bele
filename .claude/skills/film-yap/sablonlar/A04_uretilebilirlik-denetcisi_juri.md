# A04 · uretilebilirlik-denetcisi·juri — Üretilebilirlik jürisi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A04 Kör jüri: kazanan medyanı hedefi {{esik:juri_kazanan_min}}.
Anonim önerileri YZ video üretimi gözüyle puanla: Flow/Veo'nun güvenle çekebileceği eylemler, karakter ve mekân sayısı, süreklilik yükü.

## GIRDI
- `GIRDI/JURI_PAKETI/Oneri_<k>.md`
- `GIRDI/OLCUTLER.md`

## Yap
1. Her öneride `uretilebilirlik` ve `sureklilik_yuku` ölçütlerini kanıtla puanla; öbür ölçütleri de 1–10 ver ({{esik:juri_olcutleri}}).
2. Riskli öğeleri listele: kalabalık, su/ateş yoğunluğu, ince el işi, hızlı kamera, çok kostüm (karakter başına ≤ {{esik:kostum_varyant_max_karakter}}).
3. Üretilebilirlik medyanı {{esik:juri_veto_uretilebilirlik}} altına düşecek öneriyi veto et ve gerekçesini yaz.
4. Kredi hesabı yapma (kredi.py yapar).

## CIKTI
- `CIKTI/rapor.json` — şema `juri_v1` (`rol: "uretilebilirlik"`)

## Bitirmeden
- Her risk bir sahne ya da eylemle somut.
- Kredi sayısı yazmadın.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
