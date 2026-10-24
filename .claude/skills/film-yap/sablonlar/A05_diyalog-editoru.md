# A05 · diyalog-editoru — Diyalog editörü

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A05 Yapı ve senaryo: yapi-denetim ve senaryo-denetim HATA 0 olmalı (Z1/Z2 hikâye ölçüleri, filtre, NE YOK, bilgi durumu).
Senaryonun bütün diyaloğunu ritim, uzunluk, tekrar ve anlaşılırlık açısından denetle. İçerik yazmazsın; madde verirsin.

## GIRDI
- `GIRDI/` — senaryo replikleri (R kimlikli), sahne özetleri

## Yap
1. Uzun replik (8 sn klipte > {{esik:replik_max_kelime_8sn}} kelime), tekrar eden bilgi (> {{esik:bilgi_tekrar_max}}), aynı konuşmanın ikinci kez geçmesi, monolog (ardışık > {{esik:monolog_ardisik_plan_max}} plan) maddelerini çıkar.
2. Her maddeye seviye: KRITIK (anlam kaybı), ORTA (ritim), BILGI.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`)

## Bitirmeden
- Her madde replik kimliğiyle.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
