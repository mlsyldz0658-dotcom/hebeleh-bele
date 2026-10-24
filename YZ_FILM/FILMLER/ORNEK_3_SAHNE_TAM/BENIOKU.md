# ORNEK_3_SAHNE_TAM — kâğıt sonuna kadar örnek film (A00–A09)

Uydurma örnek (gerçek proje değildir). TASARIM §9 adım 10 (PR-7) ve §6.10 `test_uctan_uca_tam` içindir.

- `_KASET/`: A06s–A09 kayıtları. A00–A06 kayıtları `../ORNEK_3_SAHNE/_KASET/`'tedir; test ikisini birleştirir (aynı hikâye: FROSTHOLLOW,
  12 hikâye sahnesi = 12 sahne grubu, 33 plan). Düzen `saglayicilar/kaset.py` belgesindeki gibidir.
  - `AJAN/`: ses-tasarimcisi (kadro, tasarım × 12, müzik), yönetmen (harita × 3, plan × 12), kart-tasarımcısı, plan eleştirisi × 9,
    plan seyircisi (kâğıt seyircisinin 2. tur kayıtlarından).
  - `BETIK/`: henüz depoda olmayan ya da bu adımın sahibi olmadığı betiklerin çıktıları (kroki, plan_denetim, plan_birlestir,
    dunya_defteri, zaman_cizelgesi, cekim_listesi, kredi but1, kor_paket plan, istem_derle, kamera_agaci). `dunya_defteri` ve
    `istem_derle` kayıtları bu araçların gerçek çıktısıdır (kayıt anı: 24.10.2026); diğerleri asgari örnektir.
- Kök dosyalar (`HIKAYE.json`, `SAHNELER.json`, `DUNYA_DEFTERI.json`, `_SES/`, `MUZIK/muzik_listesi.json`, `KAMERA_AGACI.json`,
  `KAGIT_TAMAM.json`): zincirin kâğıt sonundaki çıktılarının anlık görüntüsü; `test_ses` bunları temiz fikstür olarak kullanır.
  Ses ve müzik alanları gerçek `ses_plani.py` / `muzik.py` çıktısıdır.
