# A06 · ozet-eslestirici·bulgu — Bulgu eşleştirici

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A06 Kâğıt seyirci, ilk 2 dk, kilit.
Bir seyircinin her kopukluğunu ve her açık sorusunu anahtardaki bir kimlikle eşle: bu kopukluk hangi olgunun, merakın ya da kurulumun seyirciye ulaşmamasından doğmuş? Hikâyeyi bilmezsin; yalnız iki metni kıyaslarsın. Kök neden tahmini yapma; yalnız eşle.

## GIRDI
- `GIRDI/` — bir seyircinin raporu (kopukluklar ve açık sorular)
- `GIRDI/ESLESTIRICI/ANAHTAR.json` — kimlikli olgular, meraklar ve kurulumlar (yalnız eşleştirme anahtarı)

## Yap
1. Seyirci raporundaki her kopukluk ve her açık soru için bir bulgu: `kaynak` (`kopukluk:<sıra>` ya da `acik_soru:<sıra>`, sıfırdan), seyircinin cümlesi AYNEN `alinti`'da.
2. `eslesen`: `{tur: anahtar_olgu|merak|kurulum, id}`; anahtarda karşılığı yoksa `null` (yeni bulgu; betik hikâyede arar).
3. `konum` seyircinin yazdığı konumdur (`{sahne, plan}`); yazmadıysa `{}`.

## CIKTI
- `CIKTI/rapor.json` — `{kip: "bulgu", seyirci, bulgular[{kaynak, bulgu, konum, eslesen, alinti}]}`
- `CIKTI/rapor.md` — bulgu başına bir satır; son satır `OZET | bulgu: <n> | eslesen: <n> | eslesmeyen: <n>`

## Bitirmeden
- Raporun her kopukluğu ve her açık sorusu bir bulgu olarak yazıldı.
- Alıntılar seyirci metninden birebir.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
