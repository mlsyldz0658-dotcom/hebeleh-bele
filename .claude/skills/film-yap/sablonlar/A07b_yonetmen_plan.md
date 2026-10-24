# A07b · yonetmen·plan — Sahne grubu planları (atomik eylem zinciri)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A07b Sahne grubu planları: plan_sema + plan_denetim --sahne + kroki --sahne HATA 0 (SubagentStop kancasında).
Bir sahne grubunun bütün planlarını SAHNELER v2 `zanaat` alanlarıyla yaz. YZ'ye sonuç söylenmez: her plan saniyeli, sıralı fiziksel adımlardır; başlangıç durumu = başlangıç karesi, bitiş durumu = sonraki klibin başlangıcı.

## GIRDI
- `GIRDI/` dilim dosyası (`dilim.py`: `_YONETMEN/DILIM/G<i>.json`) — sözleşme (sahne değeri, vuruş, giriş/çıkış durumu, bilgi değişimi), harita satırı (kurulumlar, eksen, kamera tarafı, kalıp, plan hedefi, yasaklar), önceki sahnenin bitişi (`bagimli` grupta çözülmüş son 2 plan)
- `GIRDI/` kroki PNG'si ve kurulumlar; sahnenin EKRAN metni ve replik kimlikleri
- `GIRDI/DERSLER.md` (varsa) · sözlükler · PLAN_DILI.md

## Yap
1. Plan sayısı grup hedefine yakın (± {{esik:plan_sayisi_tolerans_oran}}); ilk {{esik:sahne_konum_plani_max_sira}} plandan biri konum planı.
2. Adım sayısı {{esik:plan_adim_min}}–{{esik:eylem_adim_max}} (konuşmalı planda fiziksel ≤ {{esik:eylem_adim_konusmali_max}}); adım ≥ {{esik:eylem_adim_min_sn}} sn (mikro ≥ {{esik:eylem_adim_mikro_min_sn}}); ilk adım ≥ {{esik:plan_ilk_adim_min_sn}} sn; son adım klip sonundan {{esik:plan_son_adim_pay_sn}} sn önce biter.
3. Fiil yalnız fiil sözlüğünden; sağ/sol karakterin kendisine göre; iki elin durumu her başlangıçta belli; `kavrar`'da el şekli zorunlu.
4. Klip başına tek kamera hareketi; ardışık planlarda ölçek farkı ≥ {{esik:olcek_kademe_min_fark}} kademe ya da açı farkı ≥ {{esik:aci_min_fark_derece}}°; aynı kurulum ardışık ≤ {{esik:ayni_kamera_konumu_ardisik_max}}.
5. Konuşan karede tek konuşan; replik metni EKRAN'daki R kimliğiyle kelimesi kelimesine; diyalog sahnesinde tepki oranı ≥ {{esik:tepki_orani_min}}.
6. İnsanlı her planda dış ifade (`oyunculuk.dis_ifade`) ifade sözlüğünden.
7. `_derlenir`, `gorsel_istem`, `hareket_istem`, `uretim`, `denetim` alanlarına YAZMA (kod üretir).

## CIKTI
- `CIKTI/plan.json` — şema `plan_v2` (sahne grubu plan dosyası); SubagentStop kancası `plan_sema` + `plan_denetim --sahne` + `kroki.py --sahne` koşar, HATA'da en çok 2 düzeltme döner

## Bitirmeden
- PLAN_DILI.md §9 kontrol listesinin 8 maddesi.
- İlk planın başlangıcı dilimdeki önceki bitişle aynı; son planın bitişi sözleşmedeki çıkış durumu.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
