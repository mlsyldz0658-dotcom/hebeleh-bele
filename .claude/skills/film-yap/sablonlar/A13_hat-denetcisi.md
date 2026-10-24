# A13 · hat-denetcisi — Hat denetçisi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A13 Kesin bütçe BUT2: HAT kapısı GİT/GİTME.
Hattın sürmeye hazır olup olmadığına GİT/GİTME kararı ver (kapsam GOREV.json `persona`'da: BUT2, pilot, kuyruk, dilim).

GOREV.json `merdiven` alanı doluysa bu bir **merdiven basamağıdır** (§1.5): raporu ve maddeleri GIRDI'den oku; ISTEM.md'deki dosya listesi esastır.

## GIRDI
- `GIRDI/` — URETIM_ONIZLEME, BUT2 raporu, kuyruk özeti, OLCUM0 özeti, son kapı raporları

## Yap
1. GİTME yalnız somut kapatma koşuluyla: kim, neyi, hangi eşiğe getirince GİT olur.
2. Kuyruk {{esik:hat_denetcisi_kuyruk_esigi}} klibi aştıysa kök neden taraması (aynı kök neden ≥ {{esik:kesit_sistematik_plan_min}} planda = sistematik).
3. Döngü taraması: aynı görev ≥ 3 kez yinelendiyse o madde `durdu` önerilir.
4. Güvenlik ya da bütçe nedenli GİTME fiziksel iş bekler; başka yol önerme.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`) (`sonuc: GIT|GITME`); ek alan `kapatma_kosullari[{sahip, kosul, esik}]`

## Bitirmeden
- GİTME'nin her nedeni bir kapatma koşuluna bağlı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
