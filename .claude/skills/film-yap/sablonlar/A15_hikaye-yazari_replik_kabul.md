# A15 · hikaye-yazari·replik_kabul — Replik kabulü (gri bant)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A15 Ses: S2 HATA 0; merdiven tükenirse açık rapor.
Dönüştürülmüş seste repliğin anlaşılırlığı gri bantta. Söylenen metin ile yazılan metin farkı anlamı bozuyor mu, karar ver.

## GIRDI
- `GIRDI/` — replik metni, ASR dökümü, WER, sahne bağlamı (kısa)

## Yap
1. WER gri bandı {{esik:replik_wer_gri_bant}}. Anlamı taşıyan kelime (ad, olgu, sayı) kaybolduysa RED; bağlaç/ünlem farkıysa KABUL.
2. RED'de en kısa düzeltmeyi öner: yeniden çekim, TTS yolu ya da ekran dışı taşıma.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `kararlar[{replik, karar: KABUL|RED, neden, oneri}]`

## Bitirmeden
- Her repliğe tek karar.
- Gerekçe kelime düzeyinde.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
