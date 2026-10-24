# PLAN DİLİ — yönetmenin plan yazım rehberi (SAHNELER v2 `zanaat`; TASARIM §5.1, D-13, KK2)

İçindekiler: §1 Ne yazılır, ne yazılmaz · §2 Sözlükler · §3 Atomik eylem zinciri · §4 Durum ve zincir · §5 Kroki ve kurulum ·
§6 Karşılıklı çekim ve 180° · §7 Konuşma, tepki, ekleme · §8 Altı örnek · §9 Kontrol listesi

Bu dosya açıklama ve örnektir. Sayılar eşik dosyalarındadır (anahtar adıyla anılır; görev şablonu güncel değeri basar). Denetimi kod yapar:
`plan_sema` (şema, sahiplik), `plan_denetim` (Y01–Y60), `kroki.py --sahne`, `dunya_defteri` (K0). İstemi kod derler (`istem_derle --hareket`);
yönetmen İngilizce istem YAZMAZ, yalnız `zanaat` alanlarını doldurur. Elle istem yalnız `zanaat.istem_elle` ile ve oran
`plan_istem_elle_oran_max` içinde.

## §1 Ne yazılır, ne yazılmaz
| Yazar | Alan |
|---|---|
| yönetmen (`yonetmen·plan`) | `zanaat`: `kod`, `sahne_grubu`, `plan_tipi`, `klip_sn`, `kamera`, `kadrajdakiler`, `baslangic_durumu`, `eylem_zinciri`, `bitis_durumu: "derlenir"`, `oyunculuk.dis_ifade/isaretler/siddet`, `zincir`, `kesme`, `ekran_disi_ses`, `ekranda_bilgi`, `yasaklar`, `risk_uretim`; plan kökünde `no`, `sira`, `parti`, `referans`, `kullanim`, `amac`, `duygu` |
| senarist | `replik.{metin, teslim}`, `oyunculuk.ic_durum/alt_metin` (yönetmen kopyalar, değiştirmez) |
| ses tasarımcısı | `zanaat.ses`, `sahne_gruplari.<S>.ses` |
| yalnız kod | `_derlenir` (kadraj konumu, bakışın kadraja düşüşü, ışık yönü, ekran yönü, replik zamanı, açık parmak, `sure_sn`…), `gorsel_istem`, `hareket_istem`, `uretim`, `denetim` |
`_derlenir`'e ya da istem alanlarına yazmak HATA'dır (plan_sema). Kadraj solu/sağı, "left third" gibi kadraja göre konumları kod krokiden
hesaplar; yönetmen olgu yazar (kim nerede, neye bakıyor, hangi elinde ne var).

## §2 Sözlükler (değer yalnız bunlardan seçilir; dışı Y07 HATA)
- `YZ_FILM/ARACLAR/veri/plan_sozlukleri.json`: `kadraj` (EG G OG O OY Y CY D OU IK), `aci`, `hareket_tipi` (güven: yüksek/orta/düşük),
  `poz`, `yuz_acisi` (on, 3/4, profil, sirt, gorunmez), `el_sekli` (serbest, acik_avuc, yumruk, kiskac, uc_parmak, tutus_tam, isaret),
  `el_yer`, `govde` (sag_el, sol_el, sag_kol, sol_kol, iki_el, bas, cene, gozler, agiz, kaslar, omuzlar, tum_beden, ayaklar, kuyruk), `yon`, `hiz`.
- `veri/fiil_sozlugu.json`: fiiller, türü (`fiziksel`, `mikro`, `konusma`, `ses_vurusu`), zorunlu alanları (ör. `uzanir`: govde + hedef + olcu;
  `kavrar`: govde + el_sekli + hedef), `beklenen_hiz` ve dünya defterine etkisi (`etki_sablonu`). Ölçüler `_olcu` (hafif, belirgin, bir_adim,
  iki_yavas_adim, yarim_tur …, `12cm`, `30_derece`).
- `veri/ifade_sozlugu.json`: `dis_ifade.{bas, bit}` değerleri (notr, dikkatli, kontrollu_sakin, gizli_endise, korku, ofke, sefkat, kararlilik …)
  ve duygu → ifade eşlemesi. İnsanlı her planda dış ifade zorunludur.
- `veri/efekt_sozlugu.json`: fiil → efekt kategorisi (ses tasarımcısının işi; yönetmen yalnız fiili doğru seçer).

## §3 Atomik eylem zinciri (KK2)
YZ'ye sonuç söylenmez ("anahtarı alır" YOK); görünen fiziksel adımlar sırayla ve saniyeli yazılır.
1. Adım: `{id: a1.., bas, bit, ozne, tur, fiil, govde, yon|hedef, olcu, el_sekli, hiz, etki: {}}`. Tek adım = tek fiil, tek özne.
2. Adım sayısı `plan_adim_min`–`eylem_adim_max`; konuşmalı planda fiziksel adım ≤ `eylem_adim_konusmali_max` ve konuşmadan en az
   `plan_konusma_adim_arasi_min_sn` önce biter. Adım süresi ≥ `eylem_adim_min_sn` (mikro adımda `eylem_adim_mikro_min_sn`).
3. İlk adım en erken `plan_ilk_adim_min_sn`'de başlar; son adım `klip_sn − plan_son_adim_pay_sn`'de biter (son pay: bekleme, "holds still").
4. Adımlar örtüşmez; aynı anda durum değiştiren adım atan özne ≤ `plan_es_zamanli_ozne_max`.
5. Sağ/sol HER ZAMAN karakterin kendi sağı/soludur (`sag_el`, `sol_el`, `yon: saga`). Kadraja göre yön yalnız `kadraja_girer`/`kadrajdan_cikar`.
6. Eller daima tarif edilir: her elin `{tutar, yer, sekil}` durumu başlangıçta bellidir; `kavrar`'da `el_sekli` zorunludur (kıskaç = 2 açık parmak).
7. Yasak sonuç fiilleri (`yasak_sonuc_fiilleri`: take, grab, pick up, get, use, fix, prepare, fight, search; tarifsiz open) ve iç durum fiilleri
   (realizes, decides, remembers, knows) yazılmaz; fiil sözlüğünde zaten yoktur.
8. Bir eylem adım tavanına sığmıyorsa plan BÖLÜNÜR; bağ `kesme.tip: eylem` ve sonraki planın `zincir.gecis_turu: eylem_kesme`'siyle kurulur.
9. Klip başına tek kamera hareketi (`kamera_hareketi_klip_max`); kamera ve özne aynı yöne gider ya da biri durağandır. Düşük güvenli hareketler
   (`dusuk_guven_hareketler`) yalnız doruk planında ve yedek istemle.

## §4 Durum ve zincir (dünya defteri)
- `baslangic_durumu`: `"miras"` (önceki planın çözülmüş bitişi; varsayılan) ya da açık olgu nesnesi (yalnız sahne başında ya da zaman atlamasında).
  Başlangıç durumu = başlangıç karesi: o karede görünecek her şey (konum, poz, bakış, iki el, nesnelerin kimde/nerede/durumu, kostüm).
- `bitis_durumu: "derlenir"`: dünya defteri başlangıç + adımların `etki`sinden hesaplar. Bitiş = sonraki klibin başlangıç karesi.
- Olgu alanları: karakter `{mekan, isaret, poz, yuz_yonu, bakis{hedef}, kostum, kostum_durumu, gorunum, eller{sag,sol}, ifade, duygu}`;
  nesne `{kimde, el, durum}` ya da `{nerede, durum}`. Durumda kadraj konumu YOK (kod hesaplar).
- K0 sıçrama denetimi: nesne ışınlanması (masadaki anahtar bir sonraki planda elde), el değişimi (sağ elindeki fener sol elde), kostüm/görünüm
  değişimi (kapüşon gerekçesiz inik), sonraki klibe taşınmayan durum (bitişte oturan, başlangıçta ayakta). Gerekçe yalnız bir adımın `etki`sidir.
- `zincir`: `gecis_turu` (yeni_sahne, eylem_kesme, ortulu_devam, zaman_atlama …), `onceki_plan`, `baslangic` (ana_kare | son_kare), `ebeveyn`
  (kamera kurulumu), `dogal_durak`, `bitis_sabitle` (bitiş karesinin görselle sabitlenmesi; v1 `bitis_karesi` karşılığı). Zincir derinliği
  ≤ `zincir_derinlik_max`.

## §5 Kroki ve kurulum
- Harita (`yonetmen·harita`): mekânın kroki noktaları, eksen, kamera tarafı (pusula yönü), ışık kaynakları ve **kamera kurulumları**
  `KAM<n>: {konum: [x, y] m, yon_derece, yukseklik_m, lens_mm, ebeveyn}`. `kroki.py --karsilikli` karşılıklı çekim kurulum önerilerini GIRDI'ye koyar.
- Plan yalnız haritadaki bir kurulumu seçer (`kamera.kurulum: KAM3`). Kurulum ağacı derinliği ≤ `plan_agac_derinlik_max`; ana kareler
  (`_derlenir.ana_kareler`) her kurulumun ilk görseli olur, aynı kurulumdaki sonraki planlar onu referans alır.
- `kroki.py --sahne` kurulum ile karakter konumlarından kadraj üçte birini, bakışın kadraja düşüşünü, kamera tarafını ve eksen ihlalini hesaplar;
  yönetmen bunları yazmaz, denetimde HATA görürse kurulumu ya da konumu düzeltir.

## §6 Karşılıklı çekim ve 180°
- Diyalog sahne grubunda `eksen: [A, B]` ve `kamera_tarafi` haritada yazılır; bütün kurulumlar eksenin aynı tarafındadır.
- Eksen yalnız şu yollarla geçilir: karakter kadraj içinde yürüyerek tarafını değiştirir; eksen üstünden nötr plan; yeni sahne.
- Bakış çizgisi: ayakta olan oturana aşağı, oturan yukarı bakar (durumda `bakis.hedef` + poz yeter; kadraja düşüşü kod hesaplar).
- Ardışık iki planda ölçek farkı ≥ `olcek_kademe_min_fark` ya da açı farkı ≥ `aci_min_fark_derece`; aynı kurulum ardışık ≤ `ayni_kamera_konumu_ardisik_max`.
- Kalıplar (ZANAAT §3.2): klasik giriş, geç giriş, yükselen diyalog, açılan sonuç, yeniden konumlandırma. İlk birkaç plandan biri konum planıdır
  (`konum_plani`: G, OG, IK, EG; sıra ≤ `sahne_konum_plani_max_sira`).

## §7 Konuşma, tepki, ekleme
- Konuşma bir adımdır: `{tur: "konusma", fiil: "konusur", replik: "R0042", cumleler: [0, 1]}`. Metin HIKAYE.json'daki repliktir, kelimesi kelimesine.
  Konuşan karede tek kişi konuşur (`konusan_karede_max`); konuşanın yüzü `on` ya da `3/4`, yüz oranı ≥ `plan_konusan_yuz_oran_min`.
- Ekran dışı ses varken görünen herkes dinler ("listens silently, mouth closed"; kod yazar): `zanaat.ekran_disi_ses` doldurulur.
- Tepki planı: tek mikro adım (yutkunur, bakis_kaydirir, kas_catar) + dış ifade geçişi; diyalog sahnesinde oran ≥ `tepki_orani_min`.
- Ekleme (D): tek el, tek nesne; riskli eylemler (kavrama, kilit açma) eklemeye bölünür. Kurulumu olan nesne en az bir eklemeyle gösterilir.

## §8 Altı örnek (alanlar kısaltılmıştır; `kadrajdakiler` ve `oyunculuk` her insanlı planda vardır)
**Ö1 — Yürü ve uzan (P041; anahtar masada, Mara kapıda; eylem kesmeyle P042'ye bağlanır)**
```json
{"plan_tipi": "eylem", "klip_sn": 8, "kamera": {"kurulum": "KAM1", "kadraj": "OG", "aci": "goz_hizasi", "hareket_tipi": "sabit", "odak": "mara"},
 "baslangic_durumu": {"karakterler": {"mara": {"isaret": "kapi_esigi", "poz": "ayakta", "bakis": {"hedef": "masa"},
   "eller": {"sag": {"tutar": "fener", "yer": "kalca_hizasi", "sekil": "tutus_tam"}, "sol": {"tutar": null, "yer": "yanda", "sekil": "serbest"}}}},
   "nesneler": {"anahtar": {"nerede": "masa", "durum": "duruyor"}, "fener": {"kimde": "mara", "el": "sag", "durum": "yanik"}}},
 "eylem_zinciri": [
  {"id": "a1", "bas": 0.5, "bit": 3.5, "ozne": "mara", "tur": "fiziksel", "fiil": "yurur", "olcu": "iki_yavas_adim", "hedef": "masa", "hiz": "yavas", "etki": {}},
  {"id": "a2", "bas": 3.8, "bit": 6.5, "ozne": "mara", "tur": "fiziksel", "fiil": "uzanir", "govde": "sol_kol", "hedef": "anahtar", "olcu": "10cm", "hiz": "normal", "etki": {}}],
 "bitis_durumu": "derlenir", "kesme": {"tip": "eylem", "ses_tasma_sn": 0}}
```
**Ö2 — Ekleme: kıskaçla kavra ve kaldır (P042; başlangıç P041'in çözülmüş bitişi)**
```json
{"plan_tipi": "ekleme", "klip_sn": 8, "kamera": {"kurulum": "KAM4", "kadraj": "D", "hareket_tipi": "yavas_ileri", "odak": "anahtar"},
 "baslangic_durumu": "miras", "zincir": {"gecis_turu": "eylem_kesme", "onceki_plan": 41, "baslangic": "ana_kare"},
 "eylem_zinciri": [
  {"id": "a1", "bas": 0.5, "bit": 2.5, "ozne": "mara", "tur": "fiziksel", "fiil": "kavrar", "govde": "sol_el", "el_sekli": "kiskac", "hedef": "anahtar", "etki": {}},
  {"id": "a2", "bas": 2.8, "bit": 5.0, "ozne": "mara", "tur": "fiziksel", "fiil": "kaldirir", "govde": "sol_el", "olcu": "5cm", "etki": {}}]}
```
**Ö3 — Konuşmalı plan: bir mikro adım + replik (S12-P02)**
```json
{"plan_tipi": "diyalog", "klip_sn": 8, "kamera": {"kurulum": "KAM3", "kadraj": "OY", "hareket_tipi": "sabit", "odak": "mara"},
 "kadrajdakiler": [{"id": "mara", "olcek": "OY", "yuz_acisi": "3/4", "konusur": true, "kimlik_demiri": true}],
 "eylem_zinciri": [
  {"id": "a1", "bas": 0.6, "bit": 1.6, "ozne": "mara", "tur": "mikro", "fiil": "cene_kaldirir", "govde": "cene", "olcu": "hafif", "hiz": "yavas", "etki": {}},
  {"id": "a2", "bas": 2.0, "bit": 5.3, "ozne": "mara", "tur": "konusma", "fiil": "konusur", "replik": "R0042", "cumleler": [0, 1], "etki": {}}],
 "oyunculuk": {"mara": {"dis_ifade": {"bas": "kontrollu_sakin", "bit": "gizli_endise"}, "isaretler": ["cene_sikili"], "siddet": 2}},
 "kesme": {"tip": "L", "ses_tasma_sn": 1.1}}
```
**Ö4 — Tepki: ekran dışı ses, tek mikro adım (karşı plan; eksenin aynı tarafı)**
```json
{"plan_tipi": "tepki", "klip_sn": 8, "kamera": {"kurulum": "KAM5", "kadraj": "Y", "hareket_tipi": "sabit", "odak": "voss"},
 "kadrajdakiler": [{"id": "voss", "olcek": "Y", "yuz_acisi": "3/4", "konusur": false, "kimlik_demiri": true}],
 "ekran_disi_ses": {"kim": "mara", "replik": "R0043"},
 "eylem_zinciri": [{"id": "a1", "bas": 2.5, "bit": 4.0, "ozne": "voss", "tur": "mikro", "fiil": "yutkunur", "govde": "agiz", "olcu": "hafif", "etki": {}},
                   {"id": "a2", "bas": 4.5, "bit": 6.5, "ozne": "voss", "tur": "mikro", "fiil": "bakis_kaydirir", "govde": "gozler", "yon": "asagi", "etki": {}}],
 "oyunculuk": {"voss": {"dis_ifade": {"bas": "sert", "bit": "huzun"}, "siddet": 2}}}
```
**Ö5 — İki kişi, nesne verme (el değişimi açıkça; durum değiştiren özne tek)**
```json
{"plan_tipi": "eylem", "klip_sn": 8, "kamera": {"kurulum": "KAM2", "kadraj": "IK", "hareket_tipi": "sabit"},
 "eylem_zinciri": [
  {"id": "a1", "bas": 0.5, "bit": 3.0, "ozne": "mara", "tur": "fiziksel", "fiil": "verir", "govde": "sag_el", "hedef": "voss", "etki": {}},
  {"id": "a2", "bas": 3.5, "bit": 5.5, "ozne": "voss", "tur": "fiziksel", "fiil": "el_degistirir", "govde": "sol_el", "etki": {}}]}
```
(`verir` sonunda fener Voss'un elindedir — hangi eli `etki` yazar; `el_degistirir` onu öbür eline geçirir. Bir sonraki planın başlangıcı bunu taşır.)
**Ö6 — Görünüm değişimi gerekçeli: kapüşonu indir, sonra kadrajdan çık (sahne sonu)**
```json
{"plan_tipi": "eylem", "klip_sn": 8, "kamera": {"kurulum": "KAM1", "kadraj": "O", "hareket_tipi": "yavas_geri"},
 "eylem_zinciri": [
  {"id": "a1", "bas": 0.5, "bit": 2.5, "ozne": "mara", "tur": "fiziksel", "fiil": "kapusonu_indirir", "govde": "iki_el", "etki": {}},
  {"id": "a2", "bas": 3.0, "bit": 6.5, "ozne": "mara", "tur": "fiziksel", "fiil": "kadrajdan_cikar", "yon": "kadraj_sagi", "hiz": "normal", "etki": {}}],
 "zincir": {"gecis_turu": "yeni_sahne", "dogal_durak": true}}
```
(Kapüşonun inik olması sonraki sahnelere taşınır; inişi gösteren adım olmadan inik kapüşon K0 HATA'sıdır.)

## §9 Kontrol listesi (plan dosyasını bitirmeden önce)
1. Her plan bir haritadaki kurulumu kullanıyor; kadraj ve hareket sözlükte; tek kamera hareketi.
2. Başlangıç durumu ya `miras` ya da kareyi baştan sona tarif eden olgu; iki el ve her nesnenin kimde/nerede olduğu belli.
3. Adım sayısı, süreler, ilk ve son pay eşiklerin içinde; adımlar örtüşmüyor; her adım tek fiil ve sözlükte; zorunlu alanları dolu.
4. Sağ/sol karakterin kendisine göre; kadraja göre konum yazılmadı.
5. Konuşan karede tek konuşan; replik kimliği HIKAYE.json'da; metin değişmedi; dinleyen konuşmuyor.
6. Önceki planın bitişi bu planın başlangıcı; görünüm/kostüm/nesne değişimi bir adımla gerekçeli.
7. Eksenin aynı tarafı; ardışık planlarda ölçek ya da açı farkı yeterli; konum planı sahnenin başında.
8. `_derlenir`, `gorsel_istem`, `hareket_istem`, `uretim`, `denetim` alanlarına hiçbir şey yazılmadı.
