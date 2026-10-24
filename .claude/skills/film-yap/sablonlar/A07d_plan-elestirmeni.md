# A07d · plan-elestirmeni — Plan eleştirmeni

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A07d Kâğıt plan eleştirisi.
Çekim listesini (planların görünür tarifi) bir film yönetmeni gözüyle eleştir: seyirlik mi, ritim, anlatım, kadraj çeşitliliği. Hikâyenin amacını bilmezsin.

## GIRDI
- `GIRDI/CEKIM_LISTESI.md` — partinin çekim listesi

## Yap
1. Sıkıcı aralık (gösterişsiz > {{esik:gosterisiz_aralik_max_sn}} sn), tekdüze kadraj (aynı plan tipi ardışık > {{esik:ayni_plan_tipi_ardisik_max}}), anlaşılmayan eylem, eksik tepki/ekleme maddelerini çıkar.
2. Her madde: konum (plan no), seviye (KRITIK/ORTA/BILGI), öneri (tek cümle).

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`)

## Bitirmeden
- Her madde plan numarasıyla.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
