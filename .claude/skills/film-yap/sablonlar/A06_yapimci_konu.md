# A06 · yapimci·konu — Konu kartı

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A06 Kâğıt seyirci: kapı GENEL medyan ≥ {{esik:seyirci_kapi_genel_min}}, KRİTİK {{esik:kopukluk_kritik_max}}; hedef GENEL ≥ {{esik:seyirci_genel_esik}}.
Kullanıcının tek cümlesini üretilebilir bir film konusuna çevir: konu kartı ve varsayımlar. Kullanıcıya soru sorulmaz; belirsizlikte en makul varsayımı yaz ve gerekçesini ver.

Bu görev bir **merdiven basamağıdır** (§1.5): önceki turların kapı raporu ve maddeleri GIRDI'dedir; çıktın `CIKTI/rapor.json`.

## GIRDI
- `GIRDI/00_KONU.md` — kullanıcının cümlesi ve konuyla gelen kesin istekler
- `GIRDI/EVREN_OZET.md` (varsa) — seri evreninin özeti; `GIRDI/OLCUM0.json` (varsa) — ölçüm sonuçları

## Yap
1. Kullanıcının cümlesindeki her öğeyi koru; kesin istekleri `kesin_istekler` listesine aynen yaz.
2. Kanca ailesini seç: {{esik:konu_kanca_aileleri}}. Birden çok aile uyuyorsa en güçlü dramatik riski vereni seç, ötekini varsayımda an.
3. Kahramanı, ne kaybedebileceğini (somut, görünür), karşı gücü ve seri bağını tek satırlarla yaz.
4. Üretim riski: çocuk kahraman, kalabalık, su/ateş yoğun sahne gibi YZ videoda zor öğeleri işaretle; çocuk kahraman varsa dolaylı ya da yetişkin yorumunu öner ve bunu varsayım olarak yaz (kullanıcıya sorma).
5. Süre önerisi yazma: süreyi BUT0 (`kredi.py but0`) seçer.
6. Merdiven turundaysan (GOREV.json `merdiven` dolu): önceki konu kartını ve KONU raporunu GIRDI'den oku; YENİ bir eksenle yeniden yorumla (ör. çocuk kahraman → yetişkin ya da dolaylı anlatım) ve neyi neden değiştirdiğini `degisiklik` alanına yaz.

## CIKTI
- `CIKTI/01_KONU_KARTI.json` — `{konu, kanca_ailesi, kahraman, kaybedebilecegi, karsi_guc, mekan_dunya, ton, seri_bagi, kesin_istekler[], uretim_riskleri[], varsayimlar[], degisiklik}`
- `CIKTI/01_VARSAYIMLAR.md` — her varsayım: varsayım — neden — yanlışsa maliyeti; son satır `OZET | varsayim: <n> | risk: <n>`
- Merdiven turunda ayrıca `CIKTI/rapor.json` (yazılması gereken dosya listesi ISTEM.md'nin başındadır; liste esastır)

## Bitirmeden
- Kullanıcının cümlesinden hiçbir öğe düşmedi.
- Yaş ve filtre sözcüğü yok (istemlere gidecek kelimeler).
- Varsayımların her birinin 'yanlışsa maliyeti' yazılı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
