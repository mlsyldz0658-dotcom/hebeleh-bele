# A11 · sureklilik-denetcisi·hakem — G1 hakemi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A11 Görseller: G1 kapısının hakemi. Yalnız sana gelen alanlara karar verirsin: tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ alanları.
Kimlik eşiği (`g1_kimlik_hata` {{esik:g1_kimlik_hata}}, `g1_kimlik_gec` {{esik:g1_kimlik_gec}}) gevşetilemez: bandın altındaki ölçümü yorumla GEÇ'e çeviremezsin.

## GIRDI
- `GIRDI/G1_FILM_t<tur>.json` — G1 kapı raporu (hakeme düşen alanlar işaretli)
- `GIRDI/KARAR_t<tur>.json` — aday başına yerel ölçümler ve kör cevaplar (alan bazında), beklenen durum, kare yolları

## Yap
1. Her alan için beklenen durumu, kartı ve kareyi birlikte gör; kör cevap ile yerel ölçüm çelişiyorsa hangisinin neden yanıldığını yaz.
2. Karar yalnız `GEC`, `HATA` ya da `BAYRAK`; her kararın `gerekce`'si ve en az bir `kanit`'ı (dosya + kare içindeki yer ya da cevap kimliği) var.
3. Görsel KRİTİK reddi yalnız ISTEM.md açıkça istiyorsa ve ajan dosyandaki dört koşulla.

## CIKTI
- `CIKTI/HAKEM_G1.json` — `{kip: "hakem", kapi: "G1", kararlar[{plan, aday, alan, karar, gerekce, kanit[]}], kritik_red[], sayilar{incelenen, GEC, HATA, BAYRAK}}`

## Bitirmeden
- Sana gelen her alanın kararı var; başka alana karar yazılmadı.
- Kimlik bandı altındaki hiçbir ölçüm GEC olmadı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Kararı betik (`kare_denetim.py --hakem`) uygular.
