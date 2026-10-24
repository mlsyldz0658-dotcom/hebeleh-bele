# A17 · yayin-paketcisi·kapak — Kapak seçimi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A17 Yayın: paket doğrulama HATA 0.
Kapak adayları arasından son seçimi gerekçeleriyle yaz (kullanıcıya bilgi; onay istenmez).

## GIRDI
- `GIRDI/` — kapak adayları, kör gözlem ve seyirci ikili karşılaştırma raporları, başlık

## Yap
1. Kusurlu adayları ele; ikili karşılaştırma kazananını başlıkla birlikte değerlendir.
2. Küçük boyut okunurluğu ({{esik:kapak_kucuk_okunurluk}}).

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `secim{aday, gerekce, yedek}`

## Bitirmeden
- Seçilen aday kusurlu listesinde değil.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
