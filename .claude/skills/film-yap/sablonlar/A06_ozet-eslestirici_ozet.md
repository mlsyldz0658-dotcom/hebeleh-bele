# A06 · ozet-eslestirici·ozet — Özet eşleştirici

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A06 Kâğıt seyirci, ilk 2 dk, kilit.
Bir seyircinin özetini/raporunu, anahtar olgu listesiyle kör eşleştir: seyirci her olguyu anlamış mı? Hikâyeyi bilmezsin; yalnız iki metni kıyaslarsın.

## GIRDI
- `GIRDI/` — bir seyircinin raporu (özet ve cevaplar)
- `GIRDI/ESLESTIRICI/ANAHTAR.json` — kimlikli olgular ve sorular (yalnız eşleştirme anahtarı)

## Yap
1. Her olgu için karar: bulundu (seyirci açıkça söylüyor) · kismen (yarım ya da belirsiz) · yok. Kanıt olarak seyircinin cümlesini AYNEN alıntıla.
2. Kısmen ağırlığı {{esik:ozet_kismen_agirlik}}; sen yalnız kararı yaz, oranı betik hesaplar.
3. Seyircinin yanlış anladığı yerleri `yanlis_anlamalar`'a yaz.

## CIKTI
- `CIKTI/rapor.json` — şema `ozet_eslesme_v1`

## Bitirmeden
- Her olgunun kararı var.
- Kanıtlar seyirci metninden birebir.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
