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
4. Son tur koşulu: GENEL artışı {{esik:kurgu_kurtarma_kosul_genel_artis}} altındaysa kurtarma turu açılmaz.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `kararlar[{madde, tur: kirp|sira|kes|lj|tepki|yeniden_cek, plan, zaman, deger}]`

## Bitirmeden
- Her karar bir bulguya bağlı.
- Kullanıcının kilitli kurgu kararlarına dokunulmadı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
