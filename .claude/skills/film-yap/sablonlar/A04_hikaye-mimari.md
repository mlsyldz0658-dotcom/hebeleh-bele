# A04 · hikaye-mimari — Hikâye önerisi (10 başlık)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A04 Kör jüri: kazanan medyanı hedefi {{esik:juri_kazanan_min}}.
Brifingten, GOREV.json `persona` alanındaki EKSENE göre özgün bir film önerisi yaz (D: duygu · S: seyirlik/gerilim · E: evren/gizem · X: bilinçli olarak öbür üçünden kaçınan yol).

Bu görev bir **merdiven basamağıdır** (§1.5): önceki turların kapı raporu ve maddeleri GIRDI'dedir; çıktın `CIKTI/rapor.json`.

## GIRDI
- `GIRDI/00_BRIFING.md` — konu kartı, dersler, ritim ilkeleri
- X ekseninde: `GIRDI/LOGLINELAR.md` — öbür önerilerin loglineları (kaçınılacak yollar)

## Yap
1. Öneri tam {{esik:oneri_baslik_sayisi}} başlık taşır, `## <n>. <ad>` biçiminde ve bu sırayla: 1 Logline · 2 Başlık adayları ve kapak imgesi · 3 Karakterler · 4 Dönem, evren kuralları, NE YOK · 5 Üç parti · 6 Soğuk açılış ve ilk 2 dakika · 7 Merak, kurulum ve ironi · 8 Küçük güzel sahneler · 9 Seri kancası · 10 Üretilebilirlik.
2. Logline ≤ {{esik:logline_kelime_max}} kelime; başlık ≤ {{esik:baslik_karakter_max}} karakter, kanca cümlesi ≤ {{esik:kanca_cumlesi_karakter_max}} karakter.
3. Ana karakter ≤ {{esik:ana_karakter_max}}, konuşan karakter ≤ {{esik:oneri_konusan_max}}; ana karakter adı ≤ {{esik:ad_hece_max_ana}} hece; bir karede ≤ {{esik:referans_max}} karakter referansı.
4. Uzunluk {{esik:oneri_kelime_aralik}} kelime aralığında.
5. Seyirlik anlar parti başına en az {{esik:seyirlik_an_parti_min}}; dramatik ironi parti başına en az {{esik:ironi_parti_min}}; küçük güzel sahne parti başına en az {{esik:kucuk_guzel_sahne_parti_min}}.
6. Merak sorusu en az {{esik:merak_sorusu_min}}, kurulum → kullanım en az {{esik:kurulum_min}}; karşı gücün yasağı ilk {{esik:risk_sozlu_max_sn}} sn içinde sözle; kapak imgesi ilk {{esik:kapak_imgesi_max_sn}} sn içinde ekranda.
7. Seri kancası ≤ {{esik:seri_kancasi_max_sn}} sn; açık seri sorusu ≤ {{esik:seri_sorusu_max}}.
8. Üretilebilirlik: kalabalık, su, karmaşık el işi ve hızlı kamera azaltılır; mekân ≤ {{esik:mekan_toplam_max}}; kostüm varyantı karakter başına ≤ {{esik:kostum_varyant_max_karakter}}.
9. Örnek replik en çok {{esik:ornek_replik_max}}, her biri ≤ {{esik:replik_max_kelime_8sn}} kelime; filtre kelimesi, yaş ifadesi ve NE YOK kelimesi yok.

## CIKTI
- `CIKTI/oneri.md` — 10 başlık, başlıklar `## 1. Logline` biçiminde; son satır `OZET | eksen: <eksen> | konusan: <n> | kelime: <n>`
- Merdiven turunda ayrıca `CIKTI/rapor.json` (yazılması gereken dosyalar ISTEM.md'de listelidir)

## Bitirmeden
- {{esik:oneri_baslik_sayisi}} başlığın hepsi var ve sırası doğru.
- Sayı sınırları tuttu.
- X ekseninde öbür loglinelara benzemiyor.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
