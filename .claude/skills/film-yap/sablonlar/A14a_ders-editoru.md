# A14a · ders-editoru — Ders editörü

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A14a Dikey kesit: teknik kapılar HATA 0, kesit seyircisinde KRİTİK 0; PILOT kararları yazılır.
Ham ders kayıtlarından aday kurallar ve ders özetleri yaz. Yalnız yeni dosya yazarsın; var olan kuralı değiştirmezsin.

## GIRDI
- `GIRDI/` — ham ders kayıtları (kapı hatası, kullanıcı notu, gerçek seyirci), mevcut öğrenilen kurallar

## Yap
1. Aday kural: tetik (hangi kapı, hangi belirti), kural, kanıt sayısı, kaynak; yalnız sıkılaştırır, hiçbir güvenlik sınırını gevşetmez.
2. PILOT kapsamında: istem biçimi, take değeri, canlı bekleme, ses yolu kararlarını kanıtla yaz ({{esik:take_ikinci_secim_min_oran}}, {{esik:canli_bekleme_ab_fark_max}}).
3. Tek olaydan genel kural çıkarma; kanıt az ise `deneme` durumunda öner.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `aday_kurallar[{id, tetik, kural, kanit, kaynak, durum: aday|deneme}]`

## Bitirmeden
- Hiçbir aday kural gevşetmiyor.
- Her kuralın kanıtı var.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
