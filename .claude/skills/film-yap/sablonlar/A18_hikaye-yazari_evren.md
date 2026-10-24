# A18 · hikaye-yazari·evren — Evren taslağı (film sonu)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A18 Kapanış ve öğrenme: ders korkulukları HATA 0.
Film bittiğinde evrene girecek kalıcı bilgileri taslak olarak yaz: karakterlerin son durumu, yeni mekânlar, nesneler, açık seri soruları.

## GIRDI
- `GIRDI/` — HIKAYE özeti, son karakter durumları, kanon özeti

## Yap
1. Yalnız filmde gerçekten olanı yaz; tahmin yok.
2. Kanonla çelişen madde varsa ayrı listede (`celiski[]`) göster; kendin çözme.
3. Açık seri soruları en çok {{esik:seri_sorusu_max}}.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `evren{karakterler{}, mekanlar{}, nesneler{}, seri_sorulari[], celiski[]}`

## Bitirmeden
- Her madde film içinden kanıtlı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
