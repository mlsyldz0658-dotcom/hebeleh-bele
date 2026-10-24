# A05 · hikaye-yazari·senaryo — Senaryo

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A05 Yapı ve senaryo: yapi-denetim ve senaryo-denetim HATA 0 olmalı (Z1/Z2 hikâye ölçüleri, filtre, NE YOK, bilgi durumu).
Yapıdan tam senaryoyu yaz: sahneler, EKRAN tarifleri (seyircinin göreceği), replikler (R kimlikli), bilgi durumu ve anahtar olgular.

## GIRDI
- `GIRDI/05_YAPI.json`
- `GIRDI/DERSLER.md` (varsa)
- `GIRDI/` oyuncu ve diyalog editörü raporları (revizyon turunda)

## Yap
1. Her sahne: EKRAN bloğu (yalnız görünen ve duyulan; iç durum yok), replikler, giriş/çıkış durumu, bilgi durumu.
2. Replik: İngilizce, 8 sn'lik bir klipte ≤ {{esik:replik_max_kelime_8sn}} kelime (genel tavan {{esik:replik_max_kelime}}); konuşan karakter ≤ {{esik:konusan_karakter_max}}; filtre ve yaş sözcüğü yok.
3. Toplam replik kelimesi 40 dk için {{esik:replik_toplam_kelime_40dk}} (süreye göre orantıla).
4. İlk replik ekranda görünen kişiden gelir; her replik taşıdığı bilgiyi (`tasidigi`) belirtir.
5. Anahtar olgular parti başına {{esik:anahtar_olgu_parti}}; `kritik` işaretli olanlar seyircinin mutlaka anlaması gerekenlerdir.
6. NE YOK öğeleri ve evren kanonu korunur.
7. ≥ {{esik:ekran_disi_tasima_kelime_esigi}} kelimelik blok `ekran_disi_uygun` işaretlenir; aynı karakter art arda en çok 3 blok; kahramanın adı ilk {{esik:kahraman_adi_max_sn}} sn içinde duyulur.
8. Seyirlik an parti başına ≥ {{esik:seyirlik_an_parti_min}}; gösterişsiz en uzun aralık ≤ {{esik:gosterisiz_aralik_max_sn}} sn; ekran dışı köprü replik sahne başına ≤ {{esik:kopru_replik_sahne_max}}.

## CIKTI
- `CIKTI/senaryo.json` — `{sahneler[{id, parti, ekran, replikler[{id, karakter, metin, teslim, tasidigi}], giris_durumu, cikis_durumu, bilgi_durumu}], anahtar_olgular[{id, metin, hikaye_partisi, kritik}], karakterler{}}`

## Bitirmeden
- EKRAN bloklarında iç durum fiili yok.
- Replik kimlikleri benzersiz.
- Kelime sınırları tuttu.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
