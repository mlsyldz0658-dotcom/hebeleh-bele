# A16n · kurgucu·not — Kullanıcı notu

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A16n Kullanıcı notu: notların %100'ü bir kararla kapanır; kullanıcının taslağı değişmez.
Kullanıcının notlarını ve CapCut düzenlemelerini kurgu kararlarına çevir. Kullanıcının kendi kurgu kararı aynen ve kilitli uygulanır.

## GIRDI
- `GIRDI/NOTLARIM.json`, `GIRDI/TASLAK_FARK.json` — kullanıcının notları ve taslak farkı
- `GIRDI/` güncel KURGU_PLANI özeti

## Yap
1. Her not bir karara kapanır: uygulandı · kısmen (neden) · uygulanamadı (neden + alternatif).
2. Kullanıcının taslağına yazılmaz; kararlar klon taslağa uygulanır.
3. Ses/sahne isteği kesin istektir; sahibini yaz (hikaye-yazari, yonetmen, ses-tasarimcisi).

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `notlar[{no, karar, uygulama, sahip}]`
- `CIKTI/NOT_CEVAPLARI.md` — kullanıcıya bilgi (soru yok); son satır `OZET | not: <n> | uygulandi: <n> | kismen: <n>`

## Bitirmeden
- Notların %100'ü bir kararla kapandı.
- Cevaplarda soru cümlesi yok.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
