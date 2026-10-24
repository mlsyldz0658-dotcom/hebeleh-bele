# A16 · kesici·kurgu — Kesici — kurgu

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A16 Kurgu.
Filmi/animatiği bir kurgucu gibi izle ve 'şurası kesilmeli' dediğin yerleri öner. Hikâyenin amacını bilmezsin; seyirci gözüyle süreye bakarsın.

## GIRDI
- `GIRDI/` — kurgu parçaları ve işitsel döküm

## Yap
1. Plan ve sahne kesme önerileri (tur başına {{esik:kesme_turu_oneri}}); her öneri: konum (zaman/plan), ne kesilir, neden, kesince ne kaybolur.
2. Sıkılma aralıklarını işaretle; 'gereksiz açıklama' satırlarını göster.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `kesmeler[{konum, tur: plan|sahne, neden, kayip}]`

## Bitirmeden
- Her öneri zaman ya da plan numarasıyla.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
