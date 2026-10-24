# A18a · yayin-paketcisi·izleme — Yayın sonrası izleme

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A18a Yayın sonrası analiz: veri yoksa ölçülemedi.
Yayın sonrası verileri (48 sa, 7 gün, 28 gün) yorumla ve ders kaydı öner. Veri yoksa 'ölçülemedi'.

## GIRDI
- `GIRDI/` — YAYIN_ANALIZ özeti (gösterim, tıklama oranı, ortalama izleme, tutma eğrisi), panel puanları

## Yap
1. Tutma eğrisindeki düşüşleri zaman koduyla filmdeki anlara eşle.
2. Panel puanı ile gerçek seyirci arasındaki ilişkiyi yaz (kanıt sayısıyla).

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `dersler[{zaman, gozlem, oneri, kaynak: gercek_seyirci}]`

## Bitirmeden
- Veri yoksa sonuc OLCULEMEDI.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
