# A07d · hikaye-yazari·dar_degisiklik — Dar hikâye değişikliği (H15)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A07d Kâğıt plan eleştirisi: KRİTİK 0; ORTA ≤ {{esik:kopukluk_orta_max_parti}}/parti.
Kilitli hikâyede, bir plan ya da sahne üretilemiyor ya da kapıdan geçmiyor. Sahneyi sadeleştir, böl ya da kes; hikâyenin geri kalanını koru.

Bu görev bir **merdiven basamağıdır** (§1.5): önceki turların kapı raporu ve maddeleri GIRDI'dedir; çıktın `CIKTI/rapor.json`.

## GIRDI
- `GIRDI/` — ilgili sahnenin hikâye kaydı, başarısız kapı maddesi, komşu sahnelerin giriş/çıkış durumu

## Yap
1. Seçenekler sırasıyla: sadeleştir (eylemi YZ'nin çekebileceği adımlara indir) → böl → ekran dışına taşı → kes.
2. Anahtar olguyu taşıyan bilgi başka sahneye taşınıyorsa nereye taşındığını yaz.
3. Komşu sahnelerin giriş/çıkış durumu bozulmamalı (sahne sınırında durum eşitliği).
4. Telaffuz testi (A10b) yüzündeysen: geçmeyen adı {{esik:ad_hece_max_ana}} heceyi aşmayan, öbür adlardan en az {{esik:ad_duzenleme_uzaklik_min}} harf uzak yeni bir adla değiştir; her yerde aynı.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `degisiklik{sahne, tur: sadelestir|bol|ekran_disi|kes, yeni_metin, tasinan_olgular[]}`

## Bitirmeden
- Yalnız ilgili sahne değişti.
- Anahtar olgu kaybolmadı.
- Bütçe: H15 parti-turu sayacından düşer (film.py sayar).

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
