# reference/yonetmen.md — harita, plan, birleştirme, eleştiri (A07a–A07e, A09; bilgi, kural taşımaz)

İçindekiler: §1 Akış · §2 Yönetmenin kipleri · §3 Harita · §4 Plan dosyası · §5 Birleştirme ve K0 · §6 Eleştiri turu · §7 İstem derleme

Plan dilinin kendisi (sözlükler, atomik zincir, örnekler, kontrol listesi): `PLAN_DILI.md`.

## §1 Akış
| Aşama | Çıktı | Kim | Denetim |
|---|---|---|---|
| A07a | `_YONETMEN/HARITA_P<n>.json`, `KART_ISTEGI.json`, `_KARTLAR/KART_SPEC.json` | `yonetmen·harita` × parti ∥ `kart-tasarimcisi` | `plan_denetim --harita`, `kroki.py --denetle`, `evren.py --spec-dogrula` |
| A07b | `_YONETMEN/PLANLAR/G<k>.json` (sahne grubu başına) | `yonetmen·plan` × sahne grubu (paralel) | `plan_sema` + `plan_denetim --sahne` + `kroki.py --sahne` (SubagentStop kancasında) |
| A07c | `SAHNELER.json`, `DUNYA_DEFTERI.json`, `KURGU_PLANI_T0`, BUT1 | betikler | K0, Z0, Z1/Z2 (T0), BUT1 |
| A07d | eleştiri raporları, `K0_HAKEM.md` | `plan-elestirmeni`, `uretilebilirlik-denetcisi·plan`, `sureklilik-denetcisi·kagit` | KRİTİK 0, ORTA ≤ `kopukluk_orta_max_parti` |
| A07e | plan seyircisi raporları | `habersiz-seyirci·plan` | HS_PLAN (seyirci kapısı) |
| A09 | `hareket_istem`, `KAMERA_AGACI.json`, `KAGIT_TAMAM.json` | betikler; HATA'da `yonetmen·onarim` | ISTEM |

## §2 Yönetmenin kipleri
`harita` (parti haritası ve kurulumlar) · `plan` (bir sahne grubunun bütün planları) · `onarim` (denetim maddelerine dar düzeltme) ·
`kart_secimi` (A10d en iyi teknik aday) · `ders` (film sonu ders önerisi). Yönetmen istem yazmaz; istem kodla derlenir.

## §3 Harita
Parti başına: sahne grupları (mekân, zaman, sahne tipi, süre hedefi `sure_hedef_sn`, plan hedefi, kalıp), eksen ve kamera tarafı, ışık,
yasaklar, giriş/çıkış durumu (HIKAYE.json'a bağ), canlı arka plan, kamera kurulumları (KAM<n>). `kroki.py --karsilikli` karşılıklı çekim
önerilerini önceden GIRDI'ye koyar; harita geçince `kroki.py --ciz` A07b'nin kroki PNG'lerini üretir.

## §4 Plan dosyası
Bir sahne grubunun planları; her planda `zanaat` zorunludur (v2). A07b görevine gelen GIRDI: sözleşme (harita satırı), kroki PNG + kurulumlar,
EKRAN metni + replik kimlikleri, önceki sahnenin `cikis_durumu` (paralel görevlerde sözleşmeden), aynı mekân ve zamanda süren ardışık sahne
çiftinde önceki sahnenin son 2 planının çözülmüş bitişi (bu çift sırayla koşar), `PLAN_DILI.md`, sözlükler, `DERSLER.md`.

## §5 Birleştirme ve K0
`plan_birlestir` planları ve ses kayıtlarını `SAHNELER.json`'a (`_surum: 2`) yazar, karakter ref/ses alanlarını evrenden doldurur, kartı
`01_KARAKTERLER/`'e kopyalar. `dunya_defteri --derle --denetle` başlangıç + adım etkilerinden her planın bitişini çözer ve sıçramaları arar:
nesne ışınlanması, el değişimi, kostüm/görünüm değişimi, sonraki klibe taşınmayan durum, gerekçesiz duygu sıçraması (`duygu_sicramasi_gerekcesiz`).
HATA → `KUYRUK/YENIDEN_YAZ.json` → aynı sahnenin yönetmeni (`onarim`); iki sahnenin ucu uyuşmuyorsa madde yalnız o iki sahneye gider.

## §6 Eleştiri turu (A07d)
Çekim listesi (`CEKIM_LISTESI_P<n>.md`) okunur; üç bakış: plan eleştirmeni (kör; seyirlik, ritim, anlatım), üretilebilirlik (atomik zincir,
el/parmak, YZ'nin yapamayacağı eylem), süreklilik (K0 BAYRAK'larının hakemliği). Kalan KRİTİK → `yonetmen·onarim` 1 kez → `dar_degisiklik` →
plan `durdu`. ORTA'lar `hedef_alti` ile sürer.

## §7 İstem derleme (A09)
`istem_derle --hareket` her planın EN hareket istemini `zanaat`'tan derler: kamera cümlesi + saniyeli adımlar ("0.5-3s: …") + konuşma (ad +
ton fiili + Veo ses tarifi + replik) + bekleme ("holds still") + `flow_sound`. `istem_denetim` ISTEM kapısını uygular (filtre, yaş, yasak
sonuç fiili, çıplak left/right, kelime sınırları `plan_hareket_istem_kelime_max`, `plan_adim_cumle_kelime_max`). Elle istem oranı
≤ `plan_istem_elle_oran_max`. `kamera_agaci` görsel üretim basamaklarını (ana kare → aynı kurulumdaki planlar) çıkarır.
