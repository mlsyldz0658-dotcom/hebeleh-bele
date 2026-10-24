# A03 · hikaye-mimari — Hikâye önerisi (10 başlık)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A03 Dört öneri: D, S, E eksenleri paralel; X yalnız öbürlerinin loglinelarını görür.
Brifingten, GOREV.json `persona` alanındaki EKSENE göre özgün bir film önerisi yaz (D: duygu · S: seyirlik/gerilim · E: evren/gizem · X: bilinçli olarak öbür üçünden kaçınan yol).

GOREV.json `merdiven` alanı doluysa bu bir **merdiven basamağıdır** (§1.5): raporu ve maddeleri GIRDI'den oku; ISTEM.md'deki dosya listesi esastır.

## GIRDI
- `GIRDI/00_BRIFING.md` — konu kartı, dersler, ritim ilkeleri
- X ekseninde: `GIRDI/LOGLINELAR.md` — öbür önerilerin loglineları (kaçınılacak yollar)

## Yap
1. Öneri tam {{esik:oneri_baslik_sayisi}} başlık taşır: 1 Logline · 2 Başlık · 3 Kanca (ilk 30 sn) · 4 Üç parti · 5 Karakterler · 6 Mekânlar · 7 Seyirlik anlar · 8 Üretilebilirlik · 9 Seri kancası · 10 NE YOK.
2. Logline ≤ {{esik:logline_kelime_max}} kelime; başlık ≤ {{esik:baslik_karakter_max}} karakter; konuşan karakter ≤ {{esik:oneri_konusan_max}}.
3. Uzunluk {{esik:oneri_kelime_aralik}} kelime aralığında.
4. Seyirlik anlar parti başına en az {{esik:seyirlik_an_parti_min}}; her biri görünür bir eylemle tarif edilir.
5. Üretilebilirlik: kalabalık, su, karmaşık el işi ve hızlı kamera azaltılır; ana karakter ≤ {{esik:ana_karakter_max}}, mekân ≤ {{esik:mekan_toplam_max}}.
6. NE YOK: filmde hiç görünmeyecek öğeler (evrende olmayan teknoloji, yasak öğe).

## CIKTI
- `CIKTI/oneri.md` — 10 başlık, başlıklar `## 1. Logline` biçiminde; son satır `OZET | eksen: <eksen> | konusan: <n> | kelime: <n>`
- Merdiven turunda ayrıca `CIKTI/rapor.json` (yazılması gereken dosyalar ISTEM.md'de listelidir)

## Bitirmeden
- 10 başlığın hepsi var ve sırası doğru.
- Sayı sınırları tuttu.
- X ekseninde öbür loglinelara benzemiyor.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
