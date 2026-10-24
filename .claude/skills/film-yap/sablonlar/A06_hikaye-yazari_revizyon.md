# A06 · hikaye-yazari·revizyon — Revizyon

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A06 Kâğıt seyirci: kapı GENEL medyan ≥ {{esik:seyirci_kapi_genel_min}}, KRİTİK {{esik:kopukluk_kritik_max}}; hedef GENEL ≥ {{esik:seyirci_genel_esik}}.
Seyirci ya da denetim bulgularını kapatan revizyonu yaz. Bulgu yönlendirmesinde sana gelen maddeleri madde madde kapat; gelmeyene dokunma.

## GIRDI
- `GIRDI/06_SENARYO_v<N>.json` — güncel (son) senaryo; `GIRDI/05_YAPI.json` — yapı
- `GIRDI/BULGU_YONLENDIRME_KAGIT_t<n>.json` — sana gelen maddeler; `GIRDI/SEYIRCI_KARAR_KAGIT_t<n>.json` — seyirci kararı özeti (sayılar ve alıntılar)

## Yap
1. Her maddeye bir karar: kapatıldı (nasıl, hangi sahne/replik) · kısmen · kapatılmadı (neden).
2. Kapanış oranı hedefi {{esik:revizyon_madde_kapanis}}; kapatılamayanı gerekçelendir.
3. Düzelttiğin yerin dışında metni değiştirme (salınımı önle: önceki turda iyi olan puan düşmemeli).
4. Kilit sonrasıysan (A07 ve sonrası) yalnız dar değişiklik yapılır; bu kip değil.

## CIKTI
- `CIKTI/senaryo.json` — revize senaryonun TAMAMI (06_SENARYO şeması; değişmeyen sahneler aynen); betik
  `_HIKAYE_ODASI/06_SENARYO_v1<tur>.json` olarak taşır
- `CIKTI/rapor.json` — şema `denetci_rapor_v1`; `maddeler[]` her bulgu için karar ve değişen yer; ek `degisen_sahneler[]` ve
  `ozet: "kapatilan: <n> | kismen: <n> | acik: <n>"` (betik `_HIKAYE_ODASI/DEGISIKLIK_v<tur>.json` olarak taşır)

## Bitirmeden
- Her maddenin kararı var.
- Değişmeyen sahneler aynen kaldı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
