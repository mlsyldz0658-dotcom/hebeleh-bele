# ORNEK_3_SAHNE_ZANAAT kaseti (A07a–A07c)

Kaydedilmiş ajan çıktıları; `saglayicilar/kaset.py` oynatır (TASARIM §6.10). Betikler GERÇEK koşar.

- `AJAN/A07a_YH/hepsi/HARITA.json` — yonetmen·harita (P1; `_YONETMEN/HARITA_P1.json` ile aynı)
- `AJAN/A07a_KT/hepsi/KART_SPEC.json` — kart-tasarimcisi
- `AJAN/A07b_YP/<i>/plan.json` — yonetmen·plan, sahne grubu G<i> (G1 = S01, G2 = S02, G3 = S03; `_YONETMEN/PLANLAR/S0<i>.json` ile aynı)

Planlar değişirse kaset de güncellenir (`test_sureklilik.KasetA07.test_kaset_planlarla_ayni`).
