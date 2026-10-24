# A14a · habersiz-seyirci·ilk2dk — Habersiz seyirci — ilk 2 dakika

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A14a Dikey kesit.
Bu filmi hiç bilmiyorsun. Yalnız GIRDI'deki paketi, persona satırındaki kişi gibi izle/oku ve dürüstçe raporla. Sana verilmeyen bir şeyi tahmin etme; anlamadığını 'anlamadım' diye yaz.

## GIRDI
- `GIRDI/ILK2DK_<sürüm>.md` (ya da medya) — filmin ilk 2 dakikası, kapak ve başlıkla birlikte; persona satırı

## Yap
1. YouTube'da tıklayıp ilk 2 dakikayı izleyen biri ol: kalır mısın? `ilk2dk_devam` ve `kapatma_ani` alanlarını mutlaka doldur; `surum` alanına GIRDI'deki sürüm harfini yaz.
2. Puanlar 1–10: anlasilirlik, akicilik, merak, duygu, ritim, ilk30 ve GENEL.
3. Kopukluk: bir sahneden ötekine geçişte ya da bir planda 'bu nereden çıktı' dediğin her yer; KRITIK (hikâyeyi kaybettim) / ORTA (takıldım).
4. Sıkılma aralıkları, en ilgi çeken anlar, aklında kalan açık sorular, kahramanın ne kaybedebileceği, karakterleri nasıl tanıdığın (adını duymadığın karakteri adıyla anma; tarifle an).
5. Devam eder miydin (`devam`), olasılığı (`devam_olasiligi`), kapatacağın an (`kapatma_ani`).

## CIKTI
- Aşamalı okumada her bölüm için `CIKTI/rapor_<bölüm>.md`; son satırı: `OZET | anlasilirlik: <n> | akicilik: <n> | merak: <n> | duygu: <n> | ritim: <n> | ilk30: <n> | GENEL: <n> | KRITIK: <n> | ORTA: <n>`. Bölümü bitirince DUR; sonrakini sistem verir.
- En son `CIKTI/rapor.json` — şema `seyirci_rapor_v2` (`kip: "ilk2dk"`)

## Bitirmeden
- Rapordaki her karakter adı paketten duyulmuş/okunmuş.
- Puanların hepsi 1–10.
- OZET satırı tam biçimde.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
