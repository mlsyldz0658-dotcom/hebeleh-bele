# A14 · yonetmen·onarim — Plan onarımı

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A14 Video blokları: her klip V1 + V2 + V3 GEÇ; plan soyu başına toplam deneme 3.
Denetim, eleştiri ya da üretim kapısından dönen maddeleri DAR biçimde onar: yalnız ilgili planların `zanaat` alanları.

Bu görev bir **merdiven basamağıdır** (§1.5): önceki turların kapı raporu ve maddeleri GIRDI'dedir; çıktın `CIKTI/rapor.json`.

## GIRDI
- `GIRDI/MADDELER.json` — kapı maddeleri (YENIDEN_YAZ / kuyruk / eleştiri), ilgili planlar ve komşuları, kapı raporu

## Yap
1. Her madde için bir onarım: eylemi böl, adımı sadeleştir, kurulumu değiştir, ekleme/tepki planı ekle, elle istem (`istem_elle`, oran ≤ {{esik:plan_istem_elle_oran_max}}).
2. Onarım komşu planın başlangıç/bitiş durumunu bozmamalı; bozuyorsa komşuyu da aynı onarıma kat ve yaz.
3. Filtre reddi kipinde (`istem_elle` gerekmeden): dolaylı anlatım, kadraj dışı eylem, ekleme planı.
4. Onaramadığın madde: `oneri: durdu` (merdiven kurgucuya geçer).

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `onarimlar[{madde, plan, ne_degisti, yeni_zanaat}]` (yeni_zanaat yalnız değişen alanlar)

## Bitirmeden
- Her maddenin bir kararı var.
- `_derlenir`'e yazılmadı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
