# A07d · uretilebilirlik-denetcisi·plan — Üretilebilirlik — plan

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A07d Kâğıt plan eleştirisi: KRİTİK 0; ORTA ≤ {{esik:kopukluk_orta_max_parti}}/parti.
Planları YZ video üretimi gözüyle denetle: atomik zincir çekilebilir mi, eller ve parmaklar tarifli mi, eylem 8–10 sn klibe sığıyor mu.

## GIRDI
- `GIRDI/CEKIM_LISTESI.md`
- `GIRDI/PLANLAR/` — partinin plan dosyaları (zanaat)

## Yap
1. Riskli eylem: ince el işi, iki kişinin aynı anda durum değiştirmesi, hızlı hareket, düşük güvenli kamera ({{esik:dusuk_guven_hareketler}}).
2. Sonuç fiili ya da iç durum fiili ({{esik:yasak_sonuc_fiilleri}}) tarif yerine geçmiş mi.
3. Elin tuttuğu nesne ve parmak şekli eksik mi; eylem adım tavanını aşıyor mu ({{esik:eylem_adim_max}}).
4. Kredi hesabı yapma.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`)

## Bitirmeden
- Her madde plan no + adım kimliğiyle.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
