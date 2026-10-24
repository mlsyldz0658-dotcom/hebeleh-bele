# A12 · kurgucu·duzelt — Kurgu düzeltmesi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A12 Animatik: seyirci kapısı; render = T1 ± {{esik:render_sure_tolerans_kare}} kare; yer tutucu ≤ {{esik:animatik_yer_tutucu_max_oran}}.
Seyirci ve Z3 bulgularını kurgu kararlarına çevir: kırp, sırala, kes, L/J, tepki ekle; kredili işleri kuyruğa öner.

## GIRDI
- `GIRDI/` — seyirci kararı (medyanlar, birleşik kopukluklar, sıkılma aralıkları), Z3 raporu, güncel KURGU_PLANI özeti, kesici önerileri (tur 1)

## Yap
1. Önce 0 kredi: kırpma, sıra, kesme tipi, L/J ({{esik:l_kesme_aralik_sn}} / {{esik:j_kesme_aralik_sn}}), tepki/ekleme, sahne kesme.
2. Tur başına öneri tavanı: {{esik:kesme_turu_oneri}}.
3. Kredili madde (yeniden çekim) yalnız 0 kredi çözüm yoksa; dilim payından düşer.
4. Her karar iki alan taşır: `bulgu` — kapattığı bulgunun kimliği (seyirci/Z3/kesici raporundaki madde kimliği, ör. `Z3:diyalog_kopuk:S04` ya da `kesici:K03`) ve `kok_neden` — kök neden sözlüğünden bir değer (kurgu alanında ör. `olu_sure`, `gec_giris`, `uzun_plan`, `bilgisiz_uzun`, `ritim_tekduze`, `diyalog_kopuk`, `konusan_belirsiz`, `senkron_kaydi`, `dudak_ustune_replik`, `muzik_yanlis_yer`). Bulgusu ya da kök nedeni olmayan karar yazılmaz; kurgu_uygula onu HATA ile reddeder.
5. Son tur koşulu: GENEL artışı {{esik:kurgu_kurtarma_kosul_genel_artis}} altındaysa kurtarma turu açılmaz.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `kararlar[{madde, bulgu, kok_neden, tur: kirp|sira|kes|lj|tepki|yeniden_cek, plan, zaman, deger}]`

## Bitirmeden
- Her kararda `bulgu` (bulgu kimliği) ve `kok_neden` dolu; her karar bir bulguya bağlı.
- Kullanıcının kilitli kurgu kararlarına dokunulmadı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
