# A16 · habersiz-seyirci·kurgu — Habersiz seyirci — kurgu (film ya da dikey kesit)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A16 Kurgu.
Bu filmi hiç bilmiyorsun. Yalnız GIRDI'deki paketi, persona satırındaki kişi gibi izle/oku ve dürüstçe raporla. Sana verilmeyen bir şeyi tahmin etme; anlamadığını 'anlamadım' diye yaz.

## GIRDI
- `GIRDI/<bölüm>/` — film parçalarının kareleri ve işitsel dökümü; persona satırı
- `GIRDI/IZLE.md`

## Yap
1. Parça parça izle; her parçanın GENEL puanını `parca_puanlari`'na yaz. YZ görüntü kusurlarını hikâyeyi bozuyorsa kopukluk olarak yaz.
2. Puanlar 1–10: anlasilirlik, akicilik, merak, duygu, ritim, ilk30 ve GENEL.
3. Kopukluk: bir sahneden ötekine geçişte ya da bir planda 'bu nereden çıktı' dediğin her yer; KRITIK (hikâyeyi kaybettim) / ORTA (takıldım).
4. Sıkılma aralıkları, en ilgi çeken anlar, aklında kalan açık sorular, kahramanın ne kaybedebileceği, karakterleri nasıl tanıdığın (adını duymadığın karakteri adıyla anma; tarifle an).
5. Devam eder miydin (`devam`), olasılığı (`devam_olasiligi`), kapatacağın an (`kapatma_ani`).

## CIKTI
- Aşamalı okumada her bölüm için `CIKTI/rapor_<bölüm>.md`; son satırı: `OZET | anlasilirlik: <n> | akicilik: <n> | merak: <n> | duygu: <n> | ritim: <n> | ilk30: <n> | GENEL: <n> | KRITIK: <n> | ORTA: <n>`. Bölümü bitirince DUR; sonrakini sistem verir.
- En son `CIKTI/rapor.json` — şema `seyirci_rapor_v2` (`kip: "kurgu"`)

## Bitirmeden
- Rapordaki her karakter adı paketten duyulmuş/okunmuş.
- Puanların hepsi 1–10.
- OZET satırı tam biçimde.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
