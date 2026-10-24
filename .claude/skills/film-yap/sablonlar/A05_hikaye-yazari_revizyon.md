# A05 · hikaye-yazari·revizyon — Revizyon

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A05 Yapı ve senaryo: yapi-denetim ve senaryo-denetim HATA 0 olmalı (Z1/Z2 hikâye ölçüleri, filtre, NE YOK, bilgi durumu).
Seyirci ya da denetim bulgularını kapatan revizyonu yaz. Bulgu yönlendirmesinde sana gelen maddeleri madde madde kapat; gelmeyene dokunma.

## GIRDI
- `GIRDI/` — güncel senaryo/yapı, `BULGU_YONLENDIRME` maddeleri, seyirci kararı özeti (sayılar ve alıntılar)

## Yap
1. Her maddeye bir karar: kapatıldı (nasıl, hangi sahne/replik) · kısmen · kapatılmadı (neden).
2. Kapanış oranı hedefi {{esik:revizyon_madde_kapanis}}; kapatılamayanı gerekçelendir.
3. Düzelttiğin yerin dışında metni değiştirme (salınımı önle: önceki turda iyi olan puan düşmemeli).
4. Kilit sonrasıysan (A07 ve sonrası) yalnız dar değişiklik yapılır; bu kip değil.

## CIKTI
- Yazılması gereken dosyalar ISTEM.md'de listelidir (A05'te `CIKTI/05_YAPI.json`, A06'da `CIKTI/rapor.json`).
- `CIKTI/rapor.json` — şema `denetci_rapor_v1`; `maddeler[]` her bulgu için karar ve değişen yer; ek `degisen_sahneler[]`
- `CIKTI/DEGISIKLIK.md` — sahne sahne ne değişti; son satır `OZET | kapatilan: <n> | kismen: <n> | acik: <n>`

## Bitirmeden
- Her maddenin kararı var.
- Değişmeyen sahneler aynen kaldı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
