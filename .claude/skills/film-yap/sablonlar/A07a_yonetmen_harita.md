# A07a · yonetmen·harita — Parti haritası

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A07a Harita, kroki, kart tarifleri: plan_denetim --harita, kroki --denetle HATA 0 olmalı.
Bir hikâye partisinin yönetmen haritasını çiz: sahne grupları, mekân krokileri, eksen ve kamera tarafı, ışık ve kamera kurulumları (KAM<n>).

GOREV.json `merdiven` alanı doluysa bu bir **merdiven basamağıdır** (§1.5): raporu ve maddeleri GIRDI'den oku; ISTEM.md'deki dosya listesi esastır.

## GIRDI
- `GIRDI/HIKAYE.json` dilimi (bu parti)
- `GIRDI/KROKI_ONERI.json` — `kroki.py --karsilikli` karşılıklı çekim önerileri
- `GIRDI/` evren mekânları ve önceki kroki sürümleri
- `GIRDI/DERSLER.md` (varsa)
- Plan dili: PLAN_DILI.md §5–§6

## Yap
1. Her sahne grubu: mekân, zaman, sahne tipi, süre hedefi, plan hedefi, kalıp, eksen [A, B], kamera tarafı, ışık, yasaklar, giriş/çıkış durumu, canlı arka plan.
2. Kurulumlar: `KAM<n>: {konum, yon_derece, yukseklik_m, lens_mm, ebeveyn}`; ağaç derinliği ≤ {{esik:plan_agac_derinlik_max}}; bütün kurulumlar eksenin aynı tarafında.
3. Sahne süresi ≤ {{esik:sahne_max_sn}} sn; > {{esik:sahne_yeniden_konum_sn}} sn sahnede yeniden konumlandırma planı.
4. Merdiven turundaysan: harita denetimi maddelerini kapatan yeni sürüm (yalnız ilgili gruplar).

## CIKTI
- `CIKTI/HARITA.json` — şema `plan_v2` (harita bölümü)
- Merdiven turunda `CIKTI/rapor.json`

## Bitirmeden
- Her grup HIKAYE'deki bir sahneye bağlı.
- Kurulumlar krokide.
- Giriş/çıkış durumları HIKAYE ile aynı.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
