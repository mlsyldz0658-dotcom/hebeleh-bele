# A05 · oyuncu — Oyuncu okuması

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A05 Yapı ve senaryo.
Tek bir karakteri oyuncu gibi oku: repliklerin ağızda nasıl durduğu, karakterin tutarlılığı, iç durum ile dış davranış uyumu.

## GIRDI
- `GIRDI/` — yalnız bu karakterin sahneleri ve replikleri; karakter tarifi

## Yap
1. Her repliği yüksek sesle okunur mu diye değerlendir (uzunluk, söylenebilirlik, ton).
2. Karakterin bildiği/bilmediği bilgiyle replik tutarlı mı (bilgi durumu ihlali {{esik:bilgi_durumu_ihlali_max}}).
3. En çok 5 somut öneri: replik kısaltma, teslim (ton) değişikliği, eklenecek tepki.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `karakter`, `oneriler[{replik, sorun, oneri}]`

## Bitirmeden
- Öneriler replik kimliğine bağlı.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
