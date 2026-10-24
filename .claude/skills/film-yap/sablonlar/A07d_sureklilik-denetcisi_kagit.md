# A07d · sureklilik-denetcisi·kagit — Süreklilik — kâğıt hakemi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A07d Kâğıt plan eleştirisi: KRİTİK 0; ORTA ≤ {{esik:kopukluk_orta_max_parti}}/parti.
Dünya defterinin (K0) BAYRAK'larını ve çekim listesini hakem gözüyle incele: gerçek süreklilik hatası mı, gerekçeli değişim mi.

## GIRDI
- `GIRDI/K0_BAYRAKLAR.json`
- `GIRDI/CEKIM_LISTESI.md`
- `GIRDI/DURUMLAR/` — ilgili planların çözülmüş başlangıç/bitiş durumları

## Yap
1. Her BAYRAK için karar: HATA (nesne ışınlandı, el değişti, kostüm gerekçesiz değişti, durum taşınmadı) · GEC (bir adım gerekçeliyor) · BELIRSIZ.
2. HATA'da en küçük onarımı öner (hangi plana hangi adım).

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek dosya `CIKTI/K0_HAKEM.md` — son satır `OZET | hata: <n> | gec: <n> | belirsiz: <n>`

## Bitirmeden
- Her bayrağın kararı var.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
