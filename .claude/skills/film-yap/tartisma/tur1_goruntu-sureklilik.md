# Tur 1 — goruntu-sureklilik uzmanı

Tarih: 23 Ekim 2026. Yazan: görüntü ve süreklilik uzmanı (Claude, Opus 5.5).
Kapsam: kartlar ve seri kütüphanesi, başlangıç karesi üretimi ve seçimi, otomatik yüz/görünüm kontrolü,
dünya durumu defteri ve zıplama denetimi, CORRECTION döngüsü, Veo/Flow kısıtları, video sonrası teknik denetim.
Diğer uzmanların tur 1 dosyaları okunmadı.

**Kaynak kısaltmaları:** `02§6.2` = `arastirma/02_sureklilik.md` bölüm 6.2 · `01§B4` = `arastirma/01_film_hatlari.md` ·
`03§A2` = `arastirma/03_ses_ve_claude_code.md` · `ZAN§3.7` = `ZANAAT.md` · `RE:anahtar` = `ritim_esikleri.json` anahtarı ·
`BK§4.1` = `BILGI_KURALLARI.md` · `DERS` = `FILMLE ILGILI CLAUDE/03_DERSLER.md` · `HAT` = `01_URETIM_HATTI.md` ·
`FK` = `YZ_FILM/BILGI/FLOW_KESIF.md` · `YR` = `YAPIM_REHBERI.md` · `H/<ad>` = `HAFIZA_YEDEGI/<ad>.md`.
Kaynağı olmayan her sayı **(tahmin)** diye işaretlidir. Bu sayılar §7.9'daki kalibrasyonla ayarlanır.

---

## 1. Alanımın hedefi ve başarı ölçütü (sayılarla)

### 1.1 Hedef (tek cümle)
Seyirci 30–45 dakika boyunca **hiçbir karakterin yüzünün, kostümünün, elindeki nesnenin, mekânın ya da ışığın
"kendiliğinden" değiştiğini görmesin.** Her değişiklik dünya durumu defterinde yazılı ve ekranda görünen bir
eylemle olsun. Bunun bedeli video kredisiyle değil, kâğıtta ve 0 kredili görsel aşamasında ödensin.

### 1.2 Neden bu alan kritik (kaynaklı)
- YZ sinema filmlerinde izleyicinin **tek büyük eleştirisi** karakter tutarsızlığı: "appearance of the characters keep changing" (803 beğeni) (BK§1.4).
- B3'te video öncesi elle yapılan görsel denetim **44 başlangıç karesinin 21'inde** hata buldu: yanlış kişi, ters el, yasak ışık (DERS). Yani denetimsiz karelerin yaklaşık **%48'i bozuktu**.
- B2'de yaklaşık 134 videonun üstüne **50'den fazla yeniden çekim** yapıldı, yani yaklaşık **%37** (H/proje-b2, `06_SERVISLER_VE_MALIYET.md`). Nedenler belgelerde tek tek sayılmıyor; örnekler arasında "B22K'de Bram'a benzemeyen adam" gibi süreklilik hataları var (H/proje-b2).
- Veo API'de referans görseller, başlangıç karesi ve bitiş karesiyle **aynı istekte kullanılamaz** (02§2.1, `google-genai` `types.py`). Video modeli kimliği yalnız başlangıç karesinden alır. Bu yüzden **başlangıç karesi kapısı (G1) bütün hattın en kritik kapısıdır.**

### 1.3 Başarı ölçütleri

| # | Ölçüt | Hedef | Kaynak / not |
|---|---|---|---|
| B1 | Videoya giden başlangıç karelerinden G1 kaydı olan ve dosya özeti (hash) G1 kaydıyla eşleşenlerin oranı | **%100** (kod zorlar; istisna yok) | "Bozuk görsel videoya gitmez" (H/uretim-hatti-v2) |
| B2 | Kurgu izleme denetiminde **görsel kaynaklı** KRİTİK kopukluk (yüz değişti, nesne zıpladı, kişi kayboldu, ışık zıpladı) | parti başına **0** | `RE:kopukluk_kritik_max` = 0 |
| B3 | Kurgu izleme denetiminde görsel kaynaklı ORTA kopukluk | parti başına **≤ 1** (genel sınır ≤ 3 bütün türler için) | `RE:kopukluk_orta_max_parti` = 3; ≤ 1 bu alanın payı (tahmin) |
| B4 | G1 kapısının kaçırma oranı (bozuk kareyi GEÇ demesi), etiketli kalibrasyon setinde | **≤ %10** | 02§7 |
| B5 | G1 yanlış alarm oranı (sağlam kareye HATA demesi) | ≤ %30 (bedeli yalnız yeni bir aday görsel, kredi yok) | (tahmin) |
| B6 | Planların G1'i ilk turda geçme oranı / 2 CORRECTION turu içinde geçme oranı | ≥ %70 / ≥ %95 | (tahmin). B3'te denetimsiz üretimde sağlam kare oranı: 23/44 = %52 |
| B7 | Süreklilik nedeniyle yeniden çekilen video oranı | **≤ %15** klip (B2'de bütün nedenlerle ≈ %37) | Kredi payı `RE:kredi_yeniden_deneme_payi` = 0,2; ≤ %15 bu alanın payı (tahmin) |
| B8 | Kâğıt üstü süreklilik kapısı (K0) | **0 HATA** olmadan görsel üretimi başlamaz | ZAN§7.2 madde 1, 02§6.2 |
| B9 | Dünya durumu defterinin kapsadığı plan oranı (`baslangic_durumu` + `bitis_durumu` dolu) | **%100** | ZAN§3.7 (KESİN KURAL) |
| B10 | Kart kapısı: aynı karakterin kart görünümleri arasında SFace kosinüsü | ≥ 0,45 her çift | (tahmin); 0,363 resmî "aynı kişi" eşiği (02§1.1) |
| B11 | Kart kapısı: iki farklı karakter arasındaki SFace kosinüsü | **< 0,363** her çift (makine bile karıştırmamalı); hedef < 0,25 | 0,363 resmî (02§1.1); 0,25 (tahmin) |
| B12 | Teknik video kapısı (V1): kullanılan pencerede siyah kare / donma / klip içi istenmeyen kesme | **0** | 02§6.2 V1 |
| B13 | Klip içi kimlik (V2): kullanılan penceredeki örnek karelerde kimlik HATA'sı | **0** (BAYRAK'lar hakem onaylı) | 02§6.2 V2 |
| B14 | Kare zinciri (Z1) kaynağı olan kliplerde bitiş durumu uyumu (V3) | **%100** (uymayan klipten zincir kurulmaz) | Kesin karar 2 ve 3d |
| B15 | Kare zinciri derinliği | **≤ 2** nesil, sonra temiz görselle yeniden demirleme | 02§2.3 (öneri) |
| B16 | İkinci ve sonraki filmlerde ana karakterlerin kütüphaneden gelen kilitli kartla üretilme oranı | **%100** (hikâye gereği varyant hariç) | Kesin karar 3f |
| B17 | Ders defterinin kalibrasyon etkisi: aynı kök nedenle tekrar eden G1 hatası, ders kaydından sonraki 100 planda | önceki 100 plana göre **en az %50 az** | (tahmin); kesin karar 3e |

### 1.4 Ölçek (40 dk film için yaklaşık iş yükü)
- ≈ 495 plan, ≈ 405 klip (ZAN§2.6). Klip bölme nedeniyle başlangıç karesi sayısı ≈ klip sayısıdır: **≈ 405 kare × 2 aday ≈ 810 aday görsel**, artı CORRECTION turları (≈ %30 × 2 aday ≈ 240) (tahmin).
- Kart sayısı: ≤ 8 konuşan karakter (`RE:konusan_karakter_max`), kostüm varyantları, ≤ 6 mekân (`hikaye-mimari.md`) × 3–4 kamera konumu, 10–20 nesne. **≈ 60–100 kart × 3 aday** (tahmin).
- Kör gözlemci görüntü çağrısı: ≈ 1.100–1.400 görsel (G1 + V3 + kart). Görsel başına ≈ 1.500 girdi tokeni ile **≈ 2 milyon girdi tokeni / film** (tahmin; 1376×768 görsel ≈ (en × boy) / 750 hesabıyla).

---

## 2. Aşama aşama süreç: her adım için girdi → iş → çıktı dosyası → geçme şartı → kim yapar (ajan/betik/ana Claude)

### 2.0 Önce: Veo/Flow kısıt matrisi (bütün adımlar buna uyar)

| Kısıt | Kaynak | Bu alana etkisi |
|---|---|---|
| Veo API: `reference_images` ile `image` (başlangıç) ya da `last_frame` (bitiş) **aynı istekte olmaz** | 02§2.1 (`types.py` docstring) | Kimlik başlangıç karesine "pişirilir". Karakterli planda referanslı video modu kullanılmaz. Referans yalnız **görsel** üretiminde verilir |
| Veo API: `image` ile `video` (uzatma) birlikte verilemez | 02§2.1 | Uzatma (Extend) ile yeni başlangıç karesi aynı anda olmaz. Extend yalnız aynı plan içi devam için düşünülür |
| `last_frame` yalnız görselden videoya modunda | 02§2.1 | Bitiş karesi sabitleme (Z2) Flow "Bitir" yuvasıyla ya da API `last_frame` ile yapılır |
| Flow "İçerik öğeleri" iki referansla karakteri kaydırıyor (saç, yaş, yara izi) | FK, BK§6.3 | Karakterli planda yalnız **Kareler** modu (başlangıç [+ bitiş] karesi) |
| Kare başına ≤ 2 karakter referansı; 3 referansta yüzler karışıyor | KARARLAR, CLAUDE_ICIN, `RE:referans_max` | Görsel isteğinde karakter başına **tek birleşik kart sayfası**; en çok 2 karakter |
| Flow "Bitir" (bitiş karesi) çalışıyor, yumuşak geçiş veriyor | FK, H/proje-b2 (16.10 doğrulandı) | Eylemin tamamlanmadığı klipte düzeltme yolu: bitiş karesi sabitleme |
| Flow Extend son 24 kareyi dikkate alıyor | 02§2.2 **doğrulanmadı** | Ana yola konmaz; pilotta denenir |
| Klibin ilk 0,3–1,0 sn'si durağan; son 0,5–1,0 sn'de kayma/morf riski; güvenli pencere 0,5–7,5 sn | ZAN§2.2, `RE:kullanim_bas_varsayilan_sn`, `RE:kullanim_son_pay_sn` | Zincir karesi ve denetim örnekleri güvenli pencereden alınır |
| Veo bazen klip içinde kendiliğinden kesme yapıyor | 02§3 | V1'de PySceneDetect ile aranır |
| Tek model (Omni); Lite↔Omni geçişi uyarı getiriyor | BK§8 #3, DERS | Düzeltme için model değiştirilmez |
| Görsel gönderimleri de "olağan dışı" uyarısı alıyor; yoğun görsel turundan hemen sonra video tarafı işaretlendi | DERS, H/gemini-ajan-gorsel | Toplu görsel Gemini ajanında; Flow'da görsel düzeltme sayısı sınırlı ve videodan ayrı güne/oturuma |
| `seed` aynı girdiyle tutarlı sonuç verir (API) | 02§2.1 | Seçilen görselin/videonun tohumu (varsa) kaydedilir |
| Başlangıç görseli 1376×768, video 1280×720 (720p) | BK§4.1.12, FK | Zincir karesi 1280×720'den 1376×768'e Lanczos ile büyütülür (üretken düzeltme yok) |

### 2.1 Aşama haritası (film.py aşama sırasıyla; kredi harcayanlar en sonda)

```
[kâğıt]  A1 evren → A2 kart_spec → A5 defter(K0) → A6 gorsel_istem_derle
[0 kredi] A3 kart_uret → A4 kart_kapisi → A7 gorsel_aday(2) → A8 G1 → A9 CORRECTION(≤2 tur) → A10 on_gecis(K1-ön)
          → (animatik + habersiz seyirci: başka uzman) → A11 zincir_plani
[kredi]  A12 video (dalga dalga) → A13 V1 → A14 V2+V3 → A15 zincir karesi → (sonraki dalga)
[kurgu]  A16 K1 geçiş (kurgu sırasıyla) → A17 ders defteri + evren güncelle
```

### 2.2 Adımlar

**A1 — Seri evrenini yükle ya da kur**
- Girdi: `AYARLAR/FILM_AYAR.json` → `evren_kok` (Windows'ta `C:\Users\Soysal\Desktop\YZ_FILM\EVREN`), seri adı (hikâye odasından), `EVREN/<SERI>/DURUM_SON.json` (önceki filmin bitiş durumu, varsa).
- İş: Seri yoksa boş iskelet kurulur. Varsa kilitli kartlar, kimlik dizeleri, yüz bankaları ve bir önceki filmin son dünya durumu film klasörüne **bağlanır** (kopya değil, sürüm numarasıyla referans). Geriye uyum için `01_KARAKTERLER/<id>.jpg` dosyaları birleşik kart sayfasından üretilir (mevcut `SAHNELER.json` → `karakterler.<id>.ref` şeması bozulmaz).
- Çıktı: `<film>/EVREN_BAG.json` (`{seri, karakter: {id: surum}, mekan: {...}, nesne: {...}, baslangic_durumu_kaynagi}`).
- Geçme şartı: Bağlanan her kartın dosya özeti `karakter.json` → `hash` ile aynı (kart sessizce değişmemiş).
- Kim: betik `evren.py --bagla` (film.py `evren` aşaması).

**A2 — Kart ihtiyacı ve kart tarifleri**
- Girdi: hikâye v2, yönetmenin kart listesi ve plan listesi (`baslangic_durumu`, kostüm/durum değişimleri), `EVREN/<SERI>/dunya.json` (çağ, kumaş, palet, NE YOK listesi), `EVREN_BAG.json`.
- İş: Gereken her karakter, kostüm/durum varyantı (yırtık kol, kirli yüz, büyümüş yaratık), mekân (her kamera konumu için boş "plaka"), nesne (ölçekli: yanında el ya da kaşık, DERS) için tarif yazılır. Her karakter için **kimlik dizesi** (`kimlik_en`) **bir kez** yazılır, sonra her istemde kelimesi kelimesine tekrarlanır (01§B3). Asimetrik ayrıntılar (yara, örgü tarafı, tek eldiven) `asimetrik` listesine yazılır (ayna düzeltmesini yasaklar, ZAN§3.3). Mekân için kroki koordinatları ve kamera konumları yazılır (§5.3). Mevcut kilitli kart varsa yeniden tasarlanmaz, yalnız eksik varyant istenir.
- Çıktı: `_KARTLAR/KART_SPEC.json` + kart istemleri `_KARTLAR/KART_ISTEMLERI.json`.
- Geçme şartı (betik): şema geçerli; `kimlik_en` ≤ 45 kelime (tahmin) ve yasak kelime yok (filtre listesi + NE YOK); her plandaki her `kadrajdakiler.id` ve `nesneler.id` için kart var; mekân kartları "nötr durumda" (kapı kapalı, ateş sönük gibi; durum istemde verilir, çünkü görsel üretici karttaki nesneleri kopyalıyor, DERS).
- Kim: ajan `kart-tasarimcisi` (yazar) → betik `evren.py --spec-dogrula`.

**A3 — Kart adaylarını üret (0 kredi)**
- Girdi: `KART_ISTEMLERI.json`, onaylı ana kart (varyantlar için referans, YR A6).
- İş: Her kart için **3 aday** (YR A6). Biçim: açık gri düz fon. Karakter için **birleşik kart sayfası**: tam boy önden + 3/4 (mevcut format) + 2×2 yüz paneli (önden, 3/4 sol, 3/4 sağ, profil) + tam boy arka görünüm (omuz üstü ve arkadan planlar için; "Wren'in saçı koyu çıktı" dersi, BK§4.1.5). Gerçekçilik ekleri: insanlara `real costume test photo on ARRI Alexa`, yaratıklara `real animal photography, nature documentary, Weta Workshop practical creature, NOT cartoon, NOT Pixar, NOT plush` (YR A6).
- Çıktı: `EVREN/<SERI>/<tur>/<id>/adaylar/<id>_<varyant>_<a|b|c>.jpg`.
- Geçme şartı: her kart için 3 dosya geldi, çözünürlük ≥ 1376 px genişlik.
- Kim: sağlayıcı zinciri `kart_gorsel`: varsayılan **Gemini ajanı paketi** (`gemini_paket.py --kartlar`, büyük toplu paket kullanıcıya verilebilir, H/gemini-ajan-gorsel) → `gemini_al.py`. Alternatif: Gemini/Vertex görsel API (ücretli, onaylı). Testte `sahte`.

**A4 — Kart kapısı ve seçim (kesin karar 3c ve 3f)**
- Girdi: kart adayları, `KART_SPEC.json`, oyuncu kadrosunun öteki kilitli kartları.
- İş (sırayla):
  1. Yerel ölçüm (`kart_denetim.py`): YuNet yüz sayısı (birleşik sayfada beklenen yüz sayısı kadar, fazlası HATA); görünümler arası SFace öz tutarlılığı (≥ 0,45, tahmin); kadrodaki öteki karakterlere benzerlik (< 0,363, resmî eşik: makine iki karakteri karıştırmamalı); CLIP sıfır atış "fotoğraf mı, çizim/3B mi" sınaması (yaratıkların peluş çıkması dersi, YR A6); fon düzlüğü (fon piksellerinin standart sapması, tahmin eşik).
  2. Kör gözlemci (`kor-gozlemci`): kartı **tarifi görmeden** yapılandırılmış olarak yazar (saç rengi ve biçimi, kostüm parçaları, renkler, yara/iz tarafı, aksesuar, çağ dışı öğe: fermuar, modern mont).
  3. Kod karşılaştırır (`kart_denetim.py --karar`): tarif ↔ gözlem alan alan; NE YOK ihlali HATA.
  4. Geçen adaylar arasından **yaratıcı seçim** `yonetmen` ajanında (tür ve ton uyumu; görünüş bir sanat kararıdır). Kod yalnız teknik eleme yapar.
  5. Seçilen kart **kilitlenir**: dosya özeti, yüz bankası (`.npz`: her görünümün SFace 128 boyutlu vektörü; insan olmayan için DINOv2 kırpıntı vektörleri), karakter başına kalibrasyon başlangıcı yazılır.
- Çıktı: `EVREN/<SERI>/karakterler/<id>/karakter.json` (+ kart, yüz, arka dosyaları, banka), `_RAPOR/KART_KAPISI.json`.
- Geçme şartı: her kart için en az 1 aday bütün HATA'lardan temiz. Değilse aynı tarif + CORRECTION ile yeni 3 aday (en çok 2 tur), sonra `kart-tasarimcisi` tarifi değiştirir (ör. iki karakter çok benziyorsa saç rengi/yüz biçimi ayrıştırılır).
- Kim: betik + ajan `kor-gozlemci` + ajan `yonetmen` (seçim). `--onayli` modda kullanıcıya kart sayfası gösterilir (isteğe bağlı; kesin karar 1 gereği varsayılan değil).

**A5 — Dünya durumu defterini derle ve kâğıt üstü süreklilik kapısı (K0) (kesin karar 3b)**
- Girdi: yönetmen planı (her planda `baslangic_durumu`, `eylem_zinciri`, `bitis_durumu`, `sureklilik` alanları), `EVREN_BAG.json` → önceki filmin son durumu, mekân krokileri.
- İş: `sureklilik_defteri.py` her planın başlangıç durumunu **önceki planın bitişinden hesaplar** ve yönetmenin yazdığıyla karşılaştırır. Bitiş − başlangıç farkından olayları çıkarır (nesne el değiştirdi, kapı açıldı, fener söndü, kostüm kirlendi) ve her olayın `eylem_zinciri`nde bir fiziksel adımı olduğunu doğrular. Sahne sınırlarında kalıcı özellikleri (yara, kir, ıslaklık, kostüm hasarı, taşınan nesne) taşır. Kroki koordinatlarından ve kamera konumundan **beklenen kadraj sırasını** (soldan sağa) hesaplar ve plandaki `kadraj_sirasi` ile karşılaştırır. 180°, bakış, ışık ve referans kurallarını denetler (§7 K0 tablosu).
- Çıktı: `<film>/DUNYA_DEFTERI.json` (olaylar + her planın hesaplanmış önce/sonra anlık durumu), `_RAPOR/K0_SUREKLILIK.json`, HATA varsa `_RAPOR/YENIDEN_YAZ.json` (kâğıt).
- Geçme şartı: **0 HATA.** BAYRAK'lar `sureklilik-denetcisi` tarafından tek tek kapatılır (gerekçeli "kabul" ya da düzeltme önerisi).
- Kim: betik `sureklilik_defteri.py` → HATA'yı **planı yazan yönetmen** düzeltir (YR altın kural 4) → ajan `sureklilik-denetcisi` (BAYRAK hakemi, anlamsal kontroller: "fener söndü ama sonraki sahnede ışık kaynağı ne?").

**A6 — Görsel istemini durumdan derle**
- Girdi: `DUNYA_DEFTERI.json`, `SAHNELER.json` planları, kart kimlik dizeleri, mekân kamera konumu, `dunya.json` stil eki.
- İş: `gorsel_istem` elle yazılmaz, **`baslangic_durumu`ndan kodla derlenir** (kesin karar 2: başlangıç durumu = başlangıç karesi). Sıra: `[kadraj + kamera açısı] + [her karakter: kimlik dizesi (aynen) + kostüm tarifi + kadraj üçte biri + yön/bakış + poz + iki elin ayrı ayrı durumu ve parmak hâli] + [nesneler: kimde, hangi elde, durumu, kadrajdaki yeri] + [mekân tarifi + kamera konumunun gördüğü duvar ve öğeler] + [ışık: tek ana kaynak, yönü, gün saati] + [plan yasakları: "no other people", "no fire" vb.] + [sabit stil eki]` (BK§4.1.1; 01§B3). Anlık görüntü kuralı: istemde süren eylem fiili yok (ViMax, 02§2.3: "kareler anlık görüntü olmalı"). Referans seçimi: kadrajdaki karakterlerin kart sayfaları (≤ 2) + gerekiyorsa mekân plakası ya da kaynak planın onaylı karesi.
- Çıktı: `SAHNELER.json` → `gorsel_istem`, `gorsel_istem_yedek`, `sureklilik.referans_gorseller`.
- Geçme şartı: `istem_denetim.py` 0 HATA; kimlik dizesi istemde birebir geçiyor; süren eylem fiili (`-ing` biçimli hareket fiilleri listesi: walking, reaching, running…) yok; her `kadrajdakiler` öğesinin iki eli de tarif edilmiş (görünmüyorsa "hands not visible" açıkça).
- Kim: betik `istem_derle.py --gorsel`. Şablonların bakımı istem mühendisiyle ortak (§9).

**A7 — Başlangıç karesi adayları (2 aday, 0 kredi) (rol tanımı: "2 aday + kör denetim + kod karar")**
- Girdi: derlenmiş istemler, referans görselleri.
- İş: Her plan için **2 aday** (ViMax, 01§A3). Gemini ajanı paketinde her blokta `FILE NAME: NNN_a` / `NNN_b`. Flow'da düzeltme gerekiyorsa tek gönderimde "x2" çıktı ayarı (FK: ayarlarda x1–x4 var) → gönderim sayısı yarıya iner. `devam` geçişli planlar için de aday üretilir: animatikte yer tutucu ve zincir karesi tutmazsa yedek olarak.
- Çıktı: `SIRALI_GORSEL/_ADAYLAR/NNN_a.jpg`, `NNN_b.jpg` (+ varsa `.json` yan dosyası: sağlayıcı, model, tohum, tarih).
- Geçme şartı: her plan için 2 dosya; 1376×768'e kırpılmış (BK§4.1.12).
- Kim: sağlayıcı zinciri `gorsel`: Gemini ajanı paketi (30 planlık, `gemini_paket.py --aday 2`) → `gemini_al.py`; testte `sahte`.

**A8 — G1: başlangıç karesi kapısı (en kritik kapı)**
- Girdi: adaylar, `DUNYA_DEFTERI.json` (beklenen durum), evren bankaları, `sureklilik.yasaklar`.
- İş:
  1. **Yerel ölçüm** (`kare_denetim.py --yerel`, CPU/4 GB GPU): teknik (boyut, bulanıklık), yüz sayısı ve kimlik (YuNet + SFace; birden çok yüzde kadro bankasıyla eşleme ve fark payı), kadraj sırası ve üçte biri, bakış yönü (MediaPipe Face Landmarker yaw), el–nesne eşleşmesi (MediaPipe Pose bilekleri + OWLv2 nesne kutusu; Hand Landmarker ikinci görüş), insan olmayan karakter/nesne kimliği ve ölçeği (OWLv2 kırpıntı + DINOv2), mekân benzerliği (kişi bölgeleri maskelenmiş DINOv2 ↔ mekân plakası), ışık (Lab ortalaması, yanak parlaklık oranı), stil (CLIP fotoğraf/çizim). Açık HATA'lı aday kör gözlemciye gitmeden elenir.
  2. **Kör gözlem** (`kare_denetim.py --kor-gorev` → ajan `kor-gozlemci`): beklenen değerleri görmeden sabit soru setini cevaplar (§5.6). Kritik alanlar (kişi sayısı, kim nerede, nesne hangi elde, ateş/ışık kaynağı) **iki kez, seçenek sırası karıştırılarak** sorulur. İki cevap uyuşmazsa alan "belirsiz" olur.
  3. **Kod karar** (`kare_denetim.py --karar`): beklenen ↔ ölçülen ↔ gözlenen alan alan karşılaştırılır (§7 G1 tablosu). İki kaynak (yerel + kör) aynı hatayı görüyorsa HATA. Tek kaynak görüyorsa BAYRAK. Geçen adaylardan sabit sıralamayla biri seçilir: (1) BAYRAK sayısı az, (2) en düşük kimlik fark payı yüksek, (3) mekân benzerliği yüksek, (4) keskinlik yüksek.
  4. BAYRAK kalan tek aday varsa **hakem**: `sureklilik-denetcisi` kareyi, kartı ve beklenen durumu birlikte görerek GEÇ/HATA der (gerekçe zorunlu).
- Çıktı: `SIRALI_GORSEL/NNN.jpg` (yalnız seçilen), `_RAPOR/G1_P<n>.json` (aday başına ölçümler, gözlem, karar, seçilen dosyanın SHA1'i), elenenler `ALTERNATIFLER/` (silinmez), `_RAPOR/YENIDEN_URET.json` (düzeltilecekler).
- Geçme şartı: planın en az bir adayı GEÇ. `film.py` video aşaması, G1 kaydı GEÇ olmayan ya da dosya özeti kayıtla uyuşmayan planı **göndermez** (elle konmuş görsel de kapıdan geçmek zorunda).
- Kim: betik + ajan `kor-gozlemci` + gerekirse ajan `sureklilik-denetcisi`. Ana Claude yalnız ajan işlerini dağıtır.

**A9 — CORRECTION döngüsü (en çok 2 tur)**
- Girdi: `YENIDEN_URET.json` (plan, aday, alan, beklenen, gözlenen).
- İş:
  1. Küçük düzeltme mümkünse **bir kez** uygulanır, yeniden üretim yapılmaz: yatay ayna (yalnız kadraj sırası/bakış ters ve `asimetrik` listesi boşsa), kenardan kırpma (fazla kişi kenarda ve kırpma her kenarda ≤ %10, tahmin), renk/parlaklık eşleme (ışık farkı küçükse; `renk_cila` ile ortak yöntem). Uygulanan işlem **işaret dosyasına** yazılır, ikinci kez uygulanmaz (DERS: "düzeltme araçları bir kez uygulanmalı"). Düzeltilen kare G1'den yeniden geçer.
  2. Değilse `duzeltme.py` alan farkından **şablonla** CORRECTION cümlesi üretir (§5.7) ve istemin sonuna ekler. Örnek: `CORRECTION: the lantern is in Mara's RIGHT hand; her LEFT hand is empty, palm open.` Yanlış kişi hatasında o karakterin kart sayfası ilk referans yapılır.
  3. 2 yeni aday üretilir → A8. En çok **2 tur** (HAT §5).
  4. 2 turda geçmezse kaçış: `sureklilik-denetcisi` kök nedeni yazar, **yönetmen planı değiştirir** (sorunlu eli kadraj dışına al, açıyı değiştir, planı ikiye böl, nesneyi ekleme planına taşı, ZAN§3.5). Değişen plan K0'dan yeniden geçer. Bozuk kare hiçbir durumda videoya gitmez.
- Çıktı: güncel istemler, `_RAPOR/DUZELTME_KAYDI.jsonl`, `_RAPOR/ISARET/NNN.json`.
- Geçme şartı: kuyruk boş ya da kalan her plan için yönetmen kararı yazılı.
- Kim: betik `duzeltme.py`; yeniden üretim sağlayıcısı: Flow görseli (Memmet; kullanıcı başındaysa `--mod elle`, tempo 17.10 değerleri) ya da görsel API'si (onaylı). Kullanıcıya düzeltme paketi **verilmez** (H/gemini-ajan-gorsel). Kaçışta ajan `sureklilik-denetcisi` + ajan `yonetmen`.

**A10 — Başlangıç kareleri dizisinde ön geçiş denetimi (K1-ön, video öncesi)**
- Girdi: seçilmiş `SIRALI_GORSEL/NNN.jpg` dizisi, `sahne_gruplari`, kamera konumları.
- İş: Aynı sahne grubundaki ardışık karelerde Lab renk farkı ve parlaklık farkı; aynı kamera konumuna dönen karelerin o konumun ilk onaylı karesine DINOv2 benzerliği (ViMax kamera ağacı, 01§A3); kostüm gömmesi (gövde kırpıntısı DINOv2) sahne içinde sabit mi. Kopukluk adayları yan yana kare çiftleri olarak animatik izleme paketine eklenir.
- Çıktı: `_RAPOR/K1ON_P<n>.json`, `_RAPOR/K1ON_P<n>/cift_NNN_MMM.jpg`.
- Geçme şartı: HATA yok (eşikler §7 K1). BAYRAK'lar animatikteki habersiz seyircinin dikkatine "kopukluk adayı" olarak gider.
- Kim: betik `video_denetim.py --onceden` (aynı ölçüm kodu, girdisi kare).

**(Animatik + habersiz seyirci: animatik uzmanının alanı.)** Bu alanın katkısı: G1'den geçmiş kareler ve, eylemle durumu değişen planlarda, bitiş durumu görselleri (A11 Z2). Seyircinin görsel kopukluk bulguları A9 kuyruğuna girer.

**A11 — Zincir ve dalga planı (kesin karar 3d)**
- Girdi: `sureklilik.gecis_turu`, `zincir`, `bitis_sabitle` alanları, G1 sonuçları.
- İş: Her plan için video başlangıç karesinin kaynağı belirlenir:
  - **Z0 bağımsız:** `yeni_sahne` ve `kesme_ayni_mekan` planları. Başlangıç = G1'den geçmiş kare. Açı değişen kesmede yeni kare, kaynak planın **onaylı başlangıç karesinden** ve defterden türetilir (kamera ağacı). Videonun bitmesi beklenmez.
  - **Z1 son kare zinciri:** `devam` planları (aynı kamera konumu, aynı eylemin sürmesi; arada ekleme/tepki planı olabilir). Başlangıç = kaynak klibin **son kullanılan karesi** (A15). Kaynak klip V1+V2+V3'ten geçmeden bu plan gönderilmez.
  - **Z2 bitiş karesi sabitleme:** Eylem sonunda nesne yer değiştiriyor, karakter kadrajdan çıkıyor ya da bitiş durumu kritikse (`bitis_sabitle: true`). Planın bitiş durumundan ayrı bir görsel derlenir, G1'den geçer, Flow "Bitir" yuvasına konur. Mevcut `bitis_karesi` alanıyla uyumlu.
  - Derinlik kuralı: Z1 en çok 2 nesil zincirlenir. 3. nesilde **yeniden demirleme**: zincir karesi + kart sayfası referansıyla temiz yeni görsel üretilir, G1'den ve zincir karesine DINOv2 ≥ 0,90 (tahmin) benzerlik şartından geçer.
  - Dalgalar: dalga 1 = Z0/Z2 planları ve zincir başları; dalga 2 = derinlik-1 Z1; dalga 3 = derinlik-2 Z1. DAG yalnız sıra içindir, hız için değil (paralel Flow gönderimi uyarı getirir, 01§B6).
- Çıktı: `_RAPOR/ZINCIR_PLANI.json` (plan → kaynak, yöntem, derinlik, dalga).
- Geçme şartı: döngü yok; her Z1 planının kaynağı aynı `kamera_konumu`nda; derinlik ≤ 2.
- Kim: betik `kare_zinciri.py --plan`.

**A12 — Video üretimi (kredi) — bu alanın şartları**
- Girdi: `ZINCIR_PLANI.json`, G1 kayıtları, `SIRALI_GORSEL/NNN.jpg` (+ `NNN_son.jpg` Z2 için).
- İş: Memmet dalga dalga gönderir (Kareler modu, Omni, 720p, 8 sn). Video aşaması **her gönderimden önce** G1 kaydını ve dosya özetini doğrular. Olağan dışı uyarısında DUR (BK§6.2). Aynı gün içinde Flow'a yoğun görsel düzeltmesi gönderildiyse video aşaması `FILM_AYAR.json` → `gorsel_sonrasi_bekleme_saat` kadar bekler (DERS dersi; süre kaynakta yok, varsayılan değer kullanıcının hesabına göre ders defterinden ayarlanır).
- Çıktı: `SIRALI_VIDEO/NNN.mp4`, `uretim` kaydı (sağlayıcı, model, tohum, deneme no).
- Geçme şartı: indirme bütün (ffprobe), G1 özeti eşleşti.
- Kim: sağlayıcı `flow` (Memmet; bot atlatma yok) ya da API sağlayıcısı (Veo/kie.ai, onaylı).

**A13 — V1: teknik video denetimi**
- Girdi: `SIRALI_VIDEO/NNN.mp4`, planın `kullanim` ve `replik_zaman` alanları.
- İş: `ffprobe` bütünlük ve süre; ffmpeg `blackdetect`, `freezedetect`, `silencedetect` (replik penceresinde), `blurdetect`; PySceneDetect `ContentDetector` ile klip içi istenmeyen kesme; ardışık kare ortalama mutlak farkıyla titreme (VBench yöntemi, 02§1.2).
- Çıktı: `_RAPOR/V1_P<n>.json`; HATA'lar `YENIDEN_URET.json` (video) kuyruğuna; kesme kusurdan önceyse "kırp" önerisi (`kullanim` alanı, ZAN§2.2 d).
- Geçme şartı: kullanılacak pencerede (`kullanim.bas` … `bas+sure`) 0 HATA.
- Kim: betik `kalite_denetim.py --klip` (kurgu sonrası LUFS/final denetimi ses ve kurgu uzmanlarıyla ortak dosya).

**A14 — V2 klip içi süreklilik + V3 bitiş durumu**
- Girdi: klip, onaylı başlangıç karesi, defterdeki bitiş durumu, bankalar.
- İş:
  - **V2:** 0,5 sn arayla 17 kare (02§6.2). Her karede kimlik (SFace / DINOv2), yüz/kişi sayısı (`giris_cikis` dışında değişim HATA), ardışık kare DINOv2 sıçraması (morf/nesne belirme), kişi kutusunun x hareketi ↔ `hareket_yonu`, video ilk karesi ↔ onaylı başlangıç karesi sadakati.
  - **V3 (atomik zincirin denetimi):** planlanan kesme noktasındaki kare (`kesme.nokta_sn` ya da `kullanim.bas+sure`) kör gözlemciye verilir; gözlem `bitis_durumu` ile karşılaştırılır (nesne hangi elde, kapı açık mı, karakter nerede). Ayrıca eylem zincirinin her adımının bitiş saniyesinde birer kare MediaPipe Pose ile ölçülür ("sol kol uzandı mı").
- Çıktı: `_RAPOR/V2V3_P<n>.json`, kare şeritleri `_RAPOR/V2V3_P<n>/NNN_serit.jpg` (hakem için).
- Geçme şartı: kullanılacak pencerede V2 HATA yok; V3 bitiş durumu uyuyor. Uymuyorsa: (a) daha erken bir kare durumu karşılıyorsa `kullanim` kısaltılır; (b) eylem tamamlanmadıysa yeniden üretim **Z2 bitiş sabitlemesiyle** yapılır (bitiş durumu görseli derlenir, G1'den geçer, "Bitir" yuvasına konur); (c) iki deneme sonra yönetmen planı böler.
- Kim: betik `video_denetim.py --klip` + ajan `kor-gozlemci` (V3 karesi) + BAYRAK'ta ajan `sureklilik-denetcisi` (şeridi görerek).

**A15 — Zincir karesini çıkar (Z1)**
- Girdi: V1+V2+V3'ten geçmiş kaynak klip, kesme noktası.
- İş: Kesme noktası çevresindeki pencerede (`[kesim−0,5, kesim+0,3] ∩ [0,5, klip−0,5]`, tahmin) her kare puanlanır: keskinlik (Laplacian varyansı) yüksek, hareket enerjisi düşük (bitiş durumunun "tutulduğu" an, `RE:bitis_tutma_sn` = 0,5), kimlik benzerliği yüksek. En iyi kare tam çözünürlükte çıkarılır, Lanczos ile 1376×768'e büyütülür (üretken düzeltme yok). Kare **G1-zincir** kapısından geçer: kimlik + V3 gözlemi zaten var + kaynak plan bitiş durumu = hedef plan başlangıç durumu (defter garantisi). Hedef planın `kullanim.bas` değeri, klibin durağan başlangıcı tepki/ekleme planıyla örtüldüğü için varsayılan 0,5'te kalır; doğrudan bitişik kurguda hareketin yeniden başladığı an ölçülür.
- Çıktı: `SIRALI_GORSEL/NNN.jpg` (zincir karesi; plan adayı `_ADAYLAR/NNN_plan.jpg` olarak saklanır), `_RAPOR/ZINCIR_P<n>.json`.
- Geçme şartı: G1-zincir GEÇ. Tutmazsa plan **Z0'a düşer** (planlanmış aday kare) ve ders defterine yazılır.
- Kim: betik `kare_zinciri.py --cikar`.

**A16 — K1: kurgu sırasıyla geçiş denetimi**
- Girdi: kurgu planı (`plan_kurgu.py` çıktısı, gerçek `kullanim` değerleriyle), klipler.
- İş: A planının son kullanılan karesi ↔ B planının ilk kullanılan karesi. `devam`: DINOv2 ve parlaklık; `kesme_ayni_mekan`: Lab renk farkı, parlaklık; aynı kamera konumuna dönüş: o konumun ilk karesine benzerlik; kimlik her iki karede. Bulgular yan yana kare çiftiyle **kurgu izleme denetimine kopukluk adayı** olarak verilir (AniEval'in "komşu planlarla birlikte yargı" ilkesi, 01§A4).
- Çıktı: `_RAPOR/K1_P<n>.json`, kare çiftleri.
- Geçme şartı: HATA yok; BAYRAK'lar kurgu seyircisine gitti.
- Kim: betik `video_denetim.py --gecis`; düzeltme kararı kurgu/yönetmen.

**A17 — Ders defteri ve evren güncelleme (kesin karar 3e ve 3f)**
- Girdi: bütün kapı raporları, sonradan bulunan hatalar (V2, kurgu seyircisi, kullanıcı notu), CORRECTION kayıtları, filmin son defter durumu.
- İş: Her kapı kararı "sonradan ne oldu" bilgisiyle eşleşir (kaçırma mı, yanlış alarm mı). Eşikler korkuluklar içinde yeniden ayarlanır (§7.9, §8.7). Tekrarlayan kök neden kural adayı olur. Filmin son dünya durumu ve yeni varyant kartlar evrene yazılır.
- Çıktı: `EVREN/<SERI>/DERSLER.jsonl`, `YZ_FILM/BILGI/DERS_DEFTERI.jsonl` (seriler arası), `EVREN/<SERI>/DURUM_SON.json`, `EVREN/<SERI>/KALIBRASYON.json`.
- Geçme şartı: her yeni kural adayı "deneme" durumunda; kalıcılaşması ölçüme bağlı (§8.7).
- Kim: betik `ders_defteri.py`; kural adaylarının dilini ajan `sureklilik-denetcisi` yazar; ana Claude onaylar ve kaydeder.

---

## 3. Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) — yalnız kendi alanın

İlke: ölçülebilen her şey betikte. Ajan yalnız **görme** (kör gözlem), **anlam** (defterdeki mantık hatası) ve
**sanat** (kart seçimi) işlerinde. "Hiçbir model kendi çıktısını onaylamaz" (01§B4): görselleri Gemini/Veo üretir,
Claude denetler. Her ajan çağrısı yeni örnektir. Ajanlar birbirinin çıktısını okumaz (YR altın kural 1).
Kullanıcının kuralı gereği yargı işlerinde `model: opus`, `effort: high` (H/ajan-opus-yuksek).

### 3.1 `kor-gozlemci` (YENİ) — görüntüyü beklentiyi bilmeden yazıya döken göz
| Alan | Değer |
|---|---|
| Model | `opus` (görüntü doğruluğu hatanın kaynağı olacak kadar önemli), effort high |
| Araçlar | `Read, Write` (yalnız). `Glob`/`Grep` yok: başka dosya aramasın. Ajan tanımına `PreToolUse` hook'u: `Read` yalnız `_KOR_GOREV/<is_id>/` altındaki dosyalara izinli (03§B5: bilmemesi gereken ajanda erişim kısıtlanır) |
| Görev | Her görsel için `SORULAR.json`'daki sabit soru setini cevaplar: önce serbest envanter (kişiler, yerleri, yönleri, iki elin ayrı ayrı durumu, nesneler, ışık kaynakları, gün saati, hava, yazı/logo/filigran, anatomi bozukluğu, fotoğraf mı çizim mi), sonra seçenekli hedefli sorular. Sol/sağ her zaman **görüntü koordinatında** sorulur ("görüntünün solundaki el"); kişinin kendi sol/sağına çeviriyi kod yapar (yüz yönünden). Emin değilse "belirsiz" seçer, tahmin etmez |
| Okuyacağı dosyalar | Yalnız `_KOR_GOREV/<is_id>/SORULAR.json` ve aynı klasördeki görseller (adları anonim: `g01.jpg`…; plan numarası yok). **SAHNELER.json, defter, kartlar, istemler YOK** |
| Çıktısı | `_KOR_GOREV/<is_id>/CEVAP_<gNN>.json` (§5.6 biçimi). Son satırda makine özeti: `OZET | gorsel: 12 | belirsiz_alan: 3` |
| Parti büyüklüğü | Çağrı başına ≤ 12 görsel (dikkat dağılmasın; tahmin) |
| Neden ajan | ARIS-Movie-Director yöntemi: denetçi beklenen değeri görmeden yazıya döker, karşılaştırmayı deterministik kod yapar (01§B4). Bugünkü "listeye bakıp karar veren denetçi" onaylama eğilimindedir |

### 3.2 `sureklilik-denetcisi` (VAR, GÜNCELLENECEK) — defterin anlam bekçisi ve hakem
| Alan | Değer |
|---|---|
| Model | `opus` (bugün `sonnet`; hakemlik yargı işi, H/ajan-opus-yuksek), effort high |
| Araçlar | `Read, Write, Glob, Grep` |
| Görev (modlar) | **kagit:** K0'ın BAYRAK'larını kapatır ve betiğin göremediği anlam hatalarını bulur (fener söndü ama sahnede ışık kaynağı kalmadı; nesne kurulmadan kullanıldı; kostüm hasarı sonraki sahnede unutuldu). **hakem:** G1/V2/V3'te tek kaynaklı BAYRAK'ları beklenen durumu, kartı, kareyi ya da kare şeridini **birlikte** görerek GEÇ/HATA'ya çevirir; gerekçe zorunlu. **kacis:** 2 CORRECTION turunda geçmeyen planın kök nedenini ve yönetmene plan değişikliği önerisini yazar. **ders:** ders defterindeki kural adaylarını tek cümlelik kurala çevirir |
| Okuyacağı dosyalar | `DUNYA_DEFTERI.json`, `_RAPOR/K0_*.json`, `_RAPOR/G1_*.json`, `_RAPOR/V2V3_*.json`, ilgili kareler ve şeritler, `EVREN/<SERI>/*/karakter.json`, `dunya.json`, `ZANAAT.md` §3.3 ve §3.7, `03_DERSLER.md` |
| Çıktısı | `_RAPOR/HAKEM_<kapi>_P<n>.json`: `[{plan, alan, karar: GEC/HATA, gerekce, duzeltme?}]`; kâğıt modunda `_RAPOR/K0_HAKEM.md`; son satır `OZET | incelenen: 14 | GEC: 9 | HATA: 5` |
| Sınır | Kör gözlemcinin yerine geçmez; ilk gözlemi o yapmaz (önyargı). Yalnız betik ve kör gözlem anlaşamayınca karar verir |

### 3.3 `kart-tasarimcisi` (YENİ) — seri kütüphanesinin tarifçisi
| Alan | Değer |
|---|---|
| Model | `opus` (görünüş tasarımı kanalın tek büyük eleştirisinin kaynağı), effort high |
| Araçlar | `Read, Write, Glob, Grep, Bash(python YZ_FILM/ARACLAR/evren.py *)` |
| Görev | Hikâye v2 ve yönetmen kart listesinden kart tariflerini yazar: kimlik dizesi (bir kez, ≤ 45 kelime, yaş rakamı yok), kostüm ve durum varyantları, asimetrik ayrıntılar, yaratık ölçeği, mekân krokisi koordinatları ve kamera konumları, nesne ölçek kartları. **Kadro ayrışması**: her karakter siluetinden, saç renginden ve kostüm renginden ayırt edilebilir olmalı (seyirci için netlik + makinenin yüz ayrımı). Kart kapısı iki karakteri benzer bulursa tarifleri ayrıştırır |
| Okuyacağı dosyalar | Hikâye v2, yönetmen kart listesi, `EVREN/<SERI>/` (kilitli kartlar: yeniden tasarlamaz), `dunya.json`, `BILGI_KURALLARI.md` §4.1, `03_DERSLER.md`, `KARARLAR.md` (kapak kalıbı: insan + yaratık aynı karede, kart buna uygun olmalı) |
| Çıktısı | `_KARTLAR/KART_SPEC.json`, `_KARTLAR/KART_ISTEMLERI.json`; `evren.py --spec-dogrula` HATA'sız. Son satır `OZET | karakter: 5 | varyant: 4 | mekan: 6 | nesne: 11` |

### 3.4 Kullandığım ama bu alana ait olmayan ajanlar
- `yonetmen` (başka uzman): `baslangic_durumu`/`eylem_zinciri`/`bitis_durumu` yazarı; K0 HATA'larını düzelten "aynı yazar"; kart adayları arasında sanat seçimi; 2 tur sonra plan değişikliği.
- `habersiz-seyirci` (başka uzman): animatik ve kurgu izlemede K1-ön/K1 kare çiftlerini kopukluk adayı olarak görür.
- `istem-muhendisi` (başka uzman): `YENIDEN_URET.json` CORRECTION modundaki bugünkü elle işi `duzeltme.py`'ye devreder; şablon bakımında ortak.

### 3.5 Ajan iş devri (film.py ↔ ana Claude)
`film.py` bir ajan işine geldiğinde `_AJAN_ISLERI/<is_id>.json` yazar (`{ajan, girdi_klasoru, beklenen_ciktilar[], sonraki_komut}`) ve **çıkış kodu 2** ile "AJAN İŞİ BEKLİYOR: kor-gozlemci × 9" der. Beceri bu durumda işleri dağıtır, çıktıları doğrular, `film.py`'yi yeniden çalıştırır.
Gözetimsiz modda (`--tam-otomatik`, ana Claude yok) aynı iş `gozlemci` sağlayıcısına gider: `claude_api` (anahtar `AYARLAR/` ya da ortam değişkeni, model `claude-opus-5-5`) ya da testte `sahte`. Böylece gözlem de sağlayıcı soyutlamasının parçası olur.

---

## 4. Beceri (skill) tarif adımları — kendi alanın

Öneri: `film-yap` becerisinin altında tek seviyeli bir başvuru dosyası `reference/goruntu_sureklilik.md` (≤ 300 satır,
başında içindekiler; 03§B4). SKILL.md'den "kart, görsel, G1, video denetimi aşamasındaysan oku" diye bağlanır.
Kredi harcatan adımlar (video) ayrı ve `disable-model-invocation: true` olan alt becerideki kurallara uyar (03 öneri 3).
Betikler kara kutu gibi çağrılır, önce `--help` (03§B4). Yollar `/` ile yazılır.

### 4.1 En üstte duracak 6 kural (sıkıştırmadan sonra da ilk 5.000 tokende kalsın, 03§B4)
1. **G1 GEÇ kaydı ve dosya özeti eşleşmeyen hiçbir kare videoya gitmez.** Elle kare koymak kapıyı atlatmaz.
2. Kör gözlemciye plan, istem, defter ya da kart **verilmez**. Yalnız `_KOR_GOREV/<is_id>/`.
3. `gorsel_istem` elle yazılmaz; `istem_derle.py` durumdan derler. Elle düzeltme gerekiyorsa kaynağı (durum alanı) düzelt.
4. CORRECTION en çok 2 tur; sonra yönetmen planı değiştirir. Bozuk kareyle "idare etme" yok (kesin karar 6).
5. Flow'da "olağan dışı etkinlik"te DUR. Görsel düzeltmeleri Flow'a toplu, hızlı gönderilmez; tempo `MEMMET_AYAR.json` (17.10 değerleri).
6. Kart, görsel ve video asla silinmez; `ALTERNATIFLER/` ya da `_ADAYLAR/` altına taşınır (kalıcı silme yasak, BK§6.5).

### 4.2 Tarif (her adımın sonunda `python YZ_FILM/ARACLAR/film.py <film> --durum` ile durum doğrulanır)

```
Görüntü ve süreklilik ilerleme listesi (kopyala, işaretle):
- [ ] T0 evren bağlandı (EVREN_BAG.json)
- [ ] T1 kart tarifleri doğrulandı
- [ ] T2 kart adayları geldi
- [ ] T3 kart kapısı geçti, kartlar kilitli
- [ ] T4 K0 = 0 HATA, BAYRAK'lar kapandı
- [ ] T5 görsel istemleri derlendi, istem_denetim 0 HATA
- [ ] T6 parti P adayları geldi (2/plan)
- [ ] T7 G1 kapısı tamam (her plan GEÇ ya da yönetmen kararı)
- [ ] T8 K1-ön tamam, animatiğe verildi
- [ ] T9 zincir/dalga planı
- [ ] T10 dalga N: V1 → V2+V3 → zincir kareleri
- [ ] T11 K1 kurgu geçişleri → kurgu seyircisine
- [ ] T12 ders defteri + evren güncel
```

| # | Adım | Komut / eylem | Geçme şartı | Geçmezse |
|---|---|---|---|---|
| T0 | Evreni bağla | `python YZ_FILM/ARACLAR/evren.py <SERI> --bagla <film>` | çıkış 0, özetler eşleşti | Özet uyuşmazlığı: kart elle değişmiş → kullanıcıya söyle, yeni sürüm aç (`--surum-ac`) |
| T1 | Kart tarifleri | `kart-tasarimcisi` ajanını çağır (girdi: hikâye v2, kart listesi). Sonra `evren.py <SERI> --spec-dogrula <film>` | 0 HATA | Aynı ajana rapor geri gider (YR altın kural 4) |
| T2 | Kart adayları | `python YZ_FILM/ARACLAR/gemini_paket.py <film> --kartlar --aday 3` → (sağlayıcı) → `gemini_al.py <film> <zip>` | her kart 3 aday | Eksik kartlar için paket yeniden |
| T3 | Kart kapısı | `kart_denetim.py <film> --yerel` → `--kor-gorev` (çıkış 2: ajan işleri) → `kor-gozlemci` × N → `kart_denetim.py <film> --karar` → geçenler arasından `yonetmen` seçer → `evren.py <SERI> --kilitle <id>` | her kart için ≥ 1 temiz aday; kadro çiftleri < 0,363 | 2 tur CORRECTION; sonra `kart-tasarimcisi` tarifi ayrıştırır |
| T4 | K0 defter | `python YZ_FILM/ARACLAR/sureklilik_defteri.py <film> --derle --denetle` | 0 HATA | HATA listesi yönetmene; BAYRAK'lar `sureklilik-denetcisi` (kagit modu) |
| T5 | İstem derle | `istem_derle.py <film> --gorsel` → `istem_denetim.py <film>` | 0 HATA | Kaynak durum alanını düzelt, yeniden derle |
| T6 | Aday üret | `gemini_paket.py <film> --parti P --aday 2` → `gemini_al.py` | plan başına 2 aday | — |
| T7 | G1 | `kare_denetim.py <film> --parti P --yerel` → `--kor-gorev` → `kor-gozlemci` × N (her biri yeni örnek, ≤ 12 görsel) → `--karar` → BAYRAK varsa `sureklilik-denetcisi` (hakem) → `--karar --hakem` | her plan GEÇ | `duzeltme.py <film> --parti P` → yeni 2 aday → T7 (en çok 2 tur) → `sureklilik-denetcisi` (kacis) → `yonetmen` → T4'ten |
| T8 | K1-ön | `video_denetim.py <film> --onceden --parti P` | HATA yok | HATA'lı kare G1'e geri; BAYRAK'lar animatik paketine |
| T9 | Zincir planı | `kare_zinciri.py <film> --plan` | döngü yok, derinlik ≤ 2 | Yönetmenle `gecis_turu` düzelt |
| T10 | Video dalgaları | `film.py <film> --asama video --dalga 1` (kredi onayı) → `kalite_denetim.py <film> --klip --dalga 1` → `video_denetim.py <film> --klip --dalga 1` → `--kor-gorev` (V3) → `kor-gozlemci` → `--karar` → `kare_zinciri.py <film> --cikar --dalga 1` → dalga 2 … | dalgadaki her klip V1/V2/V3 GEÇ | V3 tutmadı → Z2 bitiş sabitlemesiyle yeniden (`duzeltme.py --video`), 2 denemeden sonra yönetmen böler |
| T11 | K1 | `plan_kurgu.py` sonrası `video_denetim.py <film> --gecis --parti P` | HATA yok | Kurgu/yönetmen: kırp, ekleme planı, yeniden çekim |
| T12 | Ders + evren | `ders_defteri.py <film> --guncelle` → `evren.py <SERI> --film-sonu <film>` | kayıt yazıldı | — |

### 4.3 Durma kuralları (bu alanda ana Claude kullanıcıya döner)
- Flow uyarısı, reCAPTCHA ya da kredi bitmesi (Memmet çıkış 2) — atlatma yok.
- Bütçe sınırı (`AYARLAR/butce.json`) yeniden üretimle aşılacaksa.
- Bir plan kaçış adımından (yönetmen değişikliği) sonra da G1'i geçemiyorsa: plan numarası, 4 adayın yan yana küçük resmi ve kök neden tek mesajla bildirilir (kullanıcıdan karar değil, bilgi; ekip yine de bir yol önerir).
- Kart kilidi değişecekse (ör. kullanıcı karakterin görünüşüne itiraz etti) — seri kütüphanesi değişikliği geriye dönük etkiler, sürüm açılır.

### 4.4 Değerlendirme senaryoları (beceri tetiklenmesi ve davranış testi, 03 öneri 12)
1. "Parti 2'nin görsellerini denetle" → T7 (G1 kapısı) çalışır, kör gözlemciye plan verilmez.
2. "Mara'nın eldiveni yanlış elde, düzelt" → kaynak durum alanı ve CORRECTION; elle istem yazılmaz.
3. "Yeni filme başla, aynı seri" → T0 kilitli kartları bağlar, yeniden tasarım istemez.
4. "Videoları üret" G1'i geçmemiş plan varken → video aşaması o planı göndermez ve nedenini söyler.

---

## 5. Veri şeması / plan alanları (JSON örneğiyle)

İlke: mevcut `SAHNELER.json` alanları (`no, parti, referans, gorsel_istem, hareket_istem, amac, duygu, replik, kullanim, bitis_karesi, motor`) **değişmez**; eski dosyalar çalışmaya devam eder. Yeni alanlar isteğe bağlıdır.
**Tek doğruluk kaynağı önerisi:** Durum (`baslangic_durumu`, `bitis_durumu`) ZANAAT §6.1'deki gibi `zanaat` alt nesnesinde durur; 02§6.1'deki `sureklilik.kadrajdakiler` ve `sureklilik.nesneler` alanları **ayrıca tutulmaz**, `baslangic_durumu.kadrajdakiler`'den okunur. `sureklilik` alt nesnesi yalnız kamera/eksen/zincir/üretim/denetim bilgisini taşır. (Yönetmen uzmanıyla uzlaşılacak, §9.)

### 5.1 Seri evreni klasörü (`<evren_kok>/<SERI>/`)
```
EMBERFALL/
  evren.json            seri adı, sürüm, bağlı filmler
  dunya.json            çağ, kumaş, renk paleti, NE_YOK listesi, sabit stil eki, gerçekçilik ekleri
  karakterler/mara/     karakter.json · kart_k1_v2.jpg (birleşik sayfa) · yuz_v2.jpg · arka_k1_v2.jpg
                        banka_v2.npz (SFace/DINOv2 vektörleri) · adaylar/ · eski/
  karakterler/ember/    karakter.json · kart_evre1_v1.jpg · olcek_evre1_v1.jpg · banka_v1.npz
  mekanlar/magara_agzi/ mekan.json · plaka_K1.jpg … plaka_K4.jpg · durum_ates_yanik_K2.jpg
  nesneler/fener/       nesne.json · kart_olcekli.jpg
  DURUM_SON.json        son filmin bitiş dünya durumu (sonraki filmin başlangıcı)
  KALIBRASYON.json      karakter/kapı başına ayarlanmış eşikler ve geçmişi
  DERSLER.jsonl         seriye özel dersler
```
Yol `AYARLAR/FILM_AYAR.json` → `"evren_kok"`; kullanıcının mevcut yolları bozulmaz.

### 5.2 `karakter.json` (insan)
```json
{
 "id": "mara", "seri": "EMBERFALL", "tur": "insan", "surum": 2, "durum": "kilitli",
 "ekran_adi": "Mara",
 "kimlik_en": "Mara, an adult woman with one long dark-auburn braid over her LEFT shoulder, pale weathered skin, a thin pale scar through her RIGHT eyebrow, grey-green eyes",
 "asimetrik": ["braid over LEFT shoulder", "scar through RIGHT eyebrow"],
 "kostumler": {
  "k1": {"tarif_en": "dark-brown shearling coat with cream fleece collar and cuffs, brown leather gloves, olive wool trousers, tall worn leather boots",
         "kart": "kart_k1_v2.jpg", "arka": "arka_k1_v2.jpg"},
  "k1_yirtik": {"turetildigi": "k1", "fark_en": "the left coat sleeve torn open at the forearm",
                "kart": "kart_k1_yirtik_v1.jpg", "olay": "S14 kayalık düşüşü"}
 },
 "varsayilan_kostum": "k1",
 "yasak": ["zipper", "modern jacket", "makeup", "jewelry"],
 "kartlar": {"sayfa": "kart_k1_v2.jpg", "yuz": "yuz_v2.jpg", "arka": "arka_k1_v2.jpg"},
 "olcum": {
  "yontem": "sface",
  "banka": "banka_v2.npz",
  "gorunum_sayisi": 6,
  "esik_gec": 0.45, "esik_hata": 0.363, "fark_payi_min": 0.05,
  "kalibrasyon": {"ornek": 0, "son": null}
 },
 "ayirt_edici": {"siluet": "uzun kürk yakalı manto", "renk": "koyu kahve + krem", "sac": "kızıl-kahve tek örgü"},
 "ses_ref": "karakterler/mara/ses.json",
 "hash": {"kart_k1_v2.jpg": "3f9a…", "yuz_v2.jpg": "b71c…"},
 "gecmis": [{"surum": 1, "tarih": "2026-10-13", "neden": "pilot"},
            {"surum": 2, "tarih": "2026-10-24", "neden": "yara izi tarifi eklendi, yüz paneli eklendi"}]
}
```
İnsan olmayan karakter farkı: `"tur": "yaratik"`, `"olcum": {"yontem": "dinov2", "bulucu_sorgu": "a dark grey dragon with glowing orange cracks", "esik_bayrak": 0.5}`,
`"evreler": {"evre1": {"olcek": {"boy_cm": 40, "benzetme": "house cat size"}, "kart": "kart_evre1_v1.jpg", "olcek_karti": "olcek_evre1_v1.jpg"}}`.
(Yaratık tarifinde "baby/little/young" yazılmaz; boy benzetmeyle verilir, `03_DERSLER.md` filtresi.)

### 5.3 `mekan.json` (kroki koordinatlı; beklenen kadraj sırası buradan hesaplanır)
```json
{
 "id": "kulube_ic", "tur": "ic", "surum": 1,
 "tarif_en": "a cramped log cabin interior, rough plank floor, low smoke-blackened beams",
 "kroki": {"birim": "m", "noktalar": {"kapi": [0.0, 4.0], "ocak": [3.5, 2.0], "pencere": [-3.0, 2.0], "masa": [1.0, 1.5]}},
 "kamera_konumlari": {
  "K1": {"konum": [0.0, -1.0], "yon_derece": 90, "plaka": "plaka_K1.jpg",
         "gorunen": {"kapi": "orta", "ocak": "sag_kenar", "pencere": "sol_kenar"}},
  "K2": {"konum": [-2.0, 2.0], "yon_derece": 0, "plaka": "plaka_K2.jpg",
         "gorunen": {"ocak": "orta", "masa": "sol_ucte_bir"}}
 },
 "notr_durum": {"kapi": "kapali", "ocak": "sonuk", "pencere_kepenk": "kapali"},
 "durum_gorselleri": {"ocak=yanik@K2": "durum_ocak_yanik_K2.jpg"},
 "isik_varsayilan": {"ana_kaynak": "pencere", "renk_sicakligi": "soguk", "gun_saati": "gunduz"},
 "ambiyans": "IC_ODA_AHSAP"
}
```
Plakalar **boş ve nötr durumdadır** (kişi yok, ateş sönük, kapı kapalı), çünkü görsel üretici referanstaki nesneleri kopyalıyor (DERS). Durum (ateş yanıyor) istemle ve gerekirse `durum_gorselleri` ile verilir.

### 5.4 `nesne.json`
```json
{"id": "demir_anahtar", "tarif_en": "a hand-forged black iron key, finger-length, with a ring bow",
 "boy_cm": 9, "olcek_karti": "kart_olcekli.jpg", "olcek_kart_tarifi": "held between a thumb and index finger for scale",
 "bulucu_sorgu": "an iron key", "asimetrik": false, "kurulum_plani": 42}
```

### 5.5 Plan alanları (SAHNELER.json → `sahneler[i]`)
```json
{
 "no": 41, "parti": 1, "referans": ["mara"],
 "gorsel_istem": "(istem_derle.py derler)", "hareket_istem": "(yönetmen/istem derler)",
 "zanaat": {
  "plan_tipi": "eylem", "kadraj": "OG", "sure_sn": 6.0, "klip_sn": 8,
  "kesme": {"tip": "eylem", "nokta_sn": 5.6},
  "baslangic_durumu": {
   "kadrajdakiler": [
    {"id": "mara", "kostum": "k1", "konum": "sol_ucte_bir", "yer": "kapi_esigi",
     "yon": "kadraj_sagi", "bakis": "demir_anahtar", "poz": "ayakta",
     "eller": {"sag": {"tutar": "fener", "hal": "kavramis_kalca_hizasi"},
               "sol": {"tutar": null, "hal": "acik_avuc_yanda"}},
     "gorunum": {"kir": 1, "islak": false, "yaralar": []}}
   ],
   "kadraj_disi_ama_mekanda": [],
   "nesneler": [
    {"id": "fener", "kimde": "mara", "el": "sag", "durum": "yanik"},
    {"id": "demir_anahtar", "yer": "masa", "kadraj_konum": "sag_ucte_bir", "durum": "masada"}
   ],
   "mekan": {"id": "kulube_ic", "kamera_konumu": "K1", "durumlar": {"kapi": "acik", "ocak": "sonuk"}},
   "isik": {"ana_kaynak": "fener", "yon": "kadraj_solu", "gun_saati": "gece"}
  },
  "eylem_zinciri": [
   {"bas": 0.0, "bit": 3.0, "ozne": "mara", "fiil": "walk", "hedef": "masa", "govde": "iki_adim", "yon": "kadraj_sagina"},
   {"bas": 3.0, "bit": 5.5, "ozne": "mara", "fiil": "extend_arm", "hedef": "demir_anahtar", "govde": "sol_kol"}
  ],
  "bitis_durumu": {
   "kadrajdakiler": [
    {"id": "mara", "konum": "orta", "yer": "masa_yani", "yon": "kadraj_sagi", "bakis": "demir_anahtar", "poz": "ayakta_egilmis",
     "eller": {"sag": {"tutar": "fener", "hal": "kavramis_kalca_hizasi"},
               "sol": {"tutar": null, "hal": "uzanmis_parmaklar_anahtarin_10cm_ustunde"}}}
   ],
   "nesneler": [{"id": "fener", "kimde": "mara", "el": "sag", "durum": "yanik"},
                {"id": "demir_anahtar", "yer": "masa", "durum": "masada"}]
  }
 },
 "sureklilik": {
  "sahne_grubu": "S07", "gecis_turu": "yeni_sahne",
  "kamera_konumu": "S07_K1", "kamera_tarafi": "A", "eksen_gecis": false,
  "kadraj_sirasi": ["mara"], "giris_cikis": {}, "hareket_yonu": "soldan_saga",
  "yuz_gorunur": {"mara": true},
  "zincir": null, "bitis_sabitle": false,
  "yasaklar": ["ucuncu_kisi", "ikinci_isik_kaynagi", "yazi"],
  "referans_gorseller": ["EVREN:mara/kart_k1_v2.jpg", "EVREN:kulube_ic/plaka_K1.jpg"],
  "uretim": {"gorsel": {"saglayici": "gemini_ajan", "aday": "b", "tur": 1, "sha1": "9c1e…"},
             "video": {"saglayici": "flow", "model": "omni", "seed": null, "deneme": 1}},
  "denetim": {"G1": {"sonuc": "GEC", "rapor": "_RAPOR/G1_P1.json"}, "V1": null, "V2": null, "V3": null, "K1": null}
 }
}
```
El hâli sözlüğü (`eller.*.hal`, kesin karar 2 "kaç parmak açık"): `acik_avuc_yanda`, `yumruk`, `kavramis_<yer>`, `basparmak_isaret_kiskac`, `uzanmis_parmaklar_<hedef>`, `isaret_parmagi_uzanmis`, `gorunmuyor`. Her biri `istem_derle.py` sözlüğünde sabit bir İngilizce ifadeye çevrilir (ör. `basparmak_isaret_kiskac` → "pinched between thumb and index finger, other fingers curled").
Zincirli plan örneği: `"gecis_turu": "devam", "zincir": {"kaynak_plan": 41, "yontem": "Z1_son_kare", "derinlik": 1, "kesim_sn": 5.6}`.
Bitiş sabitlemeli plan: `"bitis_sabitle": true` → `SIRALI_GORSEL/NNN_son.jpg` derlenir ve G1'den geçer.

### 5.6 Kör gözlem: `SORULAR.json` ve `CEVAP_gNN.json`
```json
{
 "is_id": "G1_P1_03", "gorseller": ["g01.jpg", "g02.jpg"],
 "envanter": ["kisiler", "eller", "nesneler", "isik_kaynaklari", "gun_saati", "yazi_logo", "anatomi", "stil"],
 "hedefli": {
  "g01.jpg": [
   {"k": "q1", "soru": "How many people (any visible face or body) are in the image?", "secenek": ["0", "1", "2", "3 or more"]},
   {"k": "q2", "soru": "Where is a lit lantern?", "secenek": ["held in the hand on the IMAGE-LEFT side of a person", "held in the hand on the IMAGE-RIGHT side of a person", "standing on a surface", "not visible", "cannot tell"]},
   {"k": "q2b", "tekrar_of": "q2", "secenek_karisik": true},
   {"k": "q3", "soru": "Which part of the image shows an open doorway?", "secenek": ["left third", "middle", "right third", "no doorway visible"]}
  ]
 }
}
```
```json
{
 "gorsel": "g01.jpg",
 "kisiler": [{"p": 1, "ucte_bir": "sol", "yuz_yonu": "kadraj_sagi", "poz": "standing", "yuz_gorunur": true,
              "el_goruntu_solu": "holds a lit lantern at hip height", "el_goruntu_sagi": "empty, open palm",
              "kiyafet": "dark-brown shearling coat, cream collar, gloves", "sac": "long dark-auburn braid"}],
 "nesneler": [{"ad": "iron key", "yer": "on a wooden table, right third"}],
 "isik_kaynaklari": [{"tur": "lantern", "yer": "left third"}],
 "gun_saati": "night", "yazi_logo": "none", "anatomi": "none", "stil": "photograph",
 "cevaplar": {"q1": "1", "q2": "held in the hand on the IMAGE-LEFT side of a person", "q2b": "held in the hand on the IMAGE-LEFT side of a person", "q3": "middle"},
 "belirsiz": []
}
```
Çeviri kodda: kişi kameraya dönükse (`yuz_yonu` kamera ya da 3/4) görüntünün solundaki el kişinin **sağ** elidir; sırtı dönükse ters. Sırt dönük ve el seçimi kritikse alan "belirsiz" sayılır ve hakeme gider (02§4 MediaPipe ayna uyarısı).

### 5.7 `YENIDEN_URET.json` ve CORRECTION şablonları
```json
[
 {"no": 41, "kapi": "G1", "tur": 1, "alan": "nesne_el", "beklenen": {"fener": "sag"}, "olculen": {"yerel": "sol"}, "gozlenen": {"kor": "sol"},
  "seviye": "HATA", "eylem": "yeniden_uret",
  "duzeltme": "CORRECTION: the lit lantern is in Mara's RIGHT hand at hip height; her LEFT hand is empty, palm open."},
 {"no": 57, "kapi": "G1", "tur": 1, "alan": "kadraj_sirasi", "beklenen": ["mara", "voss"], "olculen": {"yerel": ["voss", "mara"]},
  "seviye": "HATA", "eylem": "ayna", "not": "asimetrik ayrıntı yok, tek seferlik ayna; işaret dosyası yazıldı"}
]
```
| Alan | CORRECTION şablonu (EN, istemin sonuna) |
|---|---|
| `fazla_kisi` | `CORRECTION: exactly {n} people in frame: {adlar}. No other people, faces or figures anywhere, including the background.` |
| `yanlis_kisi` | `CORRECTION: the person on the {ucte_bir} is {kimlik_en}.` (+ o karakterin kart sayfası ilk referans) |
| `nesne_el` | `CORRECTION: the {nesne} is in {ad}'s {EL} hand; {iyelik} {OBUR_EL} hand is {hal_en}.` |
| `bakis` | `CORRECTION: {ad} faces frame {yon}, eyes on the {hedef}.` |
| `isik` | `CORRECTION: the only light source is the {kaynak} on frame {yon}; no fire, no candles, no other glow.` |
| `yasak_oge` | `CORRECTION: remove {oge}; there is no {oge} in this scene.` |
| `kostum` | `CORRECTION: {ad} wears {kostum_tarif_en}.` |
| `olcek` | `CORRECTION: {yaratik} is the size of {benzetme}, reaching {ad}'s {vucut_noktasi}.` (+ ölçek kartı referansı) |
| `stil` | `CORRECTION: photorealistic film still, real photography, NOT illustration, NOT 3D render, NOT plush.` |
| `mekan` | `CORRECTION: the {oge} is on the {kadraj_yeri} of the frame, as in the location reference.` |

### 5.8 `DUNYA_DEFTERI.json`
```json
{
 "film": "EMBERFALL_F2", "evren": "EMBERFALL", "surum": 3,
 "baslangic": {
  "karakterler": {"mara": {"kostum": "k1", "kir": 1, "yaralar": [], "sac": "orgulu", "yer": {"mekan": "kulube_ic", "nokta": "kapi_esigi"}}},
  "nesneler": {"fener": {"kimde": "mara", "el": "sag", "durum": "yanik"}, "demir_anahtar": {"mekan": "kulube_ic", "nokta": "masa"}},
  "mekanlar": {"kulube_ic": {"kapi": "acik", "ocak": "sonuk"}},
  "zaman": {"gun": 1, "gun_saati": "gece", "hava": "kar"}
 },
 "olaylar": [
  {"plan": 42, "adim": 1, "tur": "nesne_al", "nesne": "demir_anahtar", "kim": "mara", "el": "sol", "kaynak": "masa"},
  {"plan": 57, "adim": 2, "tur": "mekan_durum", "mekan": "kulube_ic", "alan": "ocak", "deger": "yanik"},
  {"plan": 120, "tur": "kostum_degis", "kim": "mara", "kostum": "k1_yirtik", "neden_plan": 118},
  {"plan": 131, "tur": "zaman_atla", "gun_saati": "sabah", "gosterim": "yer_zaman_karti"}
 ],
 "anlik": {"42": {"once_sha1": "…", "sonra_sha1": "…"}}
}
```
Olay türleri (sabit sözlük): `nesne_al`, `nesne_birak`, `nesne_ver` (el değiştirme), `nesne_durum` (yanar/söner/kırılır), `kostum_degis`, `gorunum_degis` (kir, ıslaklık, yara), `giris`, `cikis`, `yer_degis`, `mekan_durum`, `isik_degis`, `zaman_atla`. Her olayın `eylem_zinciri`nde karşılık gelen adımı ya da `zaman_atla` için ekranda bir kartı/geçişi olmak zorunda.

### 5.9 `G1_P<n>.json` (aday başına)
```json
{"no": 41, "aday": "b", "sha1": "9c1e…", "karar": "GEC", "secildi": true,
 "yerel": {"yuz_sayisi": 1, "kimlik": {"mara": {"benzerlik": 0.58, "fark_payi": 0.21}},
           "kadraj_sirasi": ["mara"], "ucte_bir": {"mara": "sol"}, "yaw": {"mara": 34},
           "el_nesne": {"fener": "sag", "guven": 0.71}, "mekan_dinov2": 0.66, "lab_dE_sahne": 4.2,
           "stil_clip_foto": 0.93, "keskinlik_oran": 1.08},
 "kor": {"is_id": "G1_P1_03", "gorsel": "g02.jpg", "tutarli": true},
 "alanlar": [{"alan": "nesne_el", "beklenen": "sag", "yerel": "sag", "kor": "sag", "sonuc": "uyum"}],
 "bayrak": [], "hata": []}
```

### 5.10 `ZINCIR_PLANI.json`
```json
{"dalgalar": {"1": [40, 41, 44, 45], "2": [43, 46], "3": [47]},
 "plan": {"43": {"yontem": "Z1_son_kare", "kaynak": 41, "derinlik": 1, "kesim_sn": 5.6, "aday_yedek": "_ADAYLAR/043_plan.jpg"},
          "47": {"yontem": "Z1_son_kare", "kaynak": 43, "derinlik": 2},
          "44": {"yontem": "Z2_bitis", "bitis_gorseli": "SIRALI_GORSEL/044_son.jpg"}}}
```

### 5.11 Ders kaydı (`DERSLER.jsonl`, satır başına bir kayıt)
```json
{"t": "2026-10-30", "film": "EMBERFALL_F2", "plan": 41, "kapi": "G1", "alan": "nesne_el",
 "olcu": {"yerel_guven": 0.48}, "karar": "GEC", "sonra": {"bulan": "V3", "sorun": "fener sol elde"},
 "sinif": "kacirma", "kok_neden": "iki el de kadrajın aynı yarısında, Pose bileği yanlış eşledi",
 "duzeltme": "CORRECTION nesne_el şablonu", "ise_yaradi": true, "kural_adayi": "el_nesne_guven<0.6 ise kör gözlem şart"}
```

---

## 6. Yazılması/değişmesi gereken kod (araç adı, ne yapar, girdi/çıktı, öncelik)

Öncelik: **P0** = bulutta, ağsız ve kredisiz test edilebilen karar mantığı (önce bu). **P1** = kullanıcının Windows'unda yerel modellerle ölçüm. **P2** = iyileştirme.
Mevcut stil korunur: her araçta başta Türkçe kullanım belgesi, `python <araç>.py` tek başına yardımı basar, çıkış kodu 0 bitti / 2 durdu (ajan ya da kullanıcı işi) / 1 hata.
Eşikler koda gömülmez: `.claude/skills/film-yap/sureklilik_esikleri.json` (`ritim_esikleri.json` biçiminde, ek olarak `kaynak` ve `etiket: kaynakli|tahmin` alanı). Karakter başına ayarlanan değerler `EVREN/<SERI>/KALIBRASYON.json`'da.

### 6.1 Yeni araçlar

| Araç | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|
| `sureklilik_defteri.py` | Dünya durumu defterini derler; bitiş→başlangıç zincirini, olay↔eylem adımı karşılığını, kalıcı özellikleri, zamanı, 180°/bakış/ışık/referans kurallarını denetler (K0). Krokiden beklenen kadraj sırasını hesaplar (P1 alt özelliği) | `SAHNELER.json`, `EVREN_BAG.json`, mekân krokileri → `DUNYA_DEFTERI.json`, `_RAPOR/K0_SUREKLILIK.json`, `_RAPOR/YENIDEN_YAZ.json` | **P0** (saf Python) |
| `istem_derle.py --gorsel` | `gorsel_istem`'i `baslangic_durumu` + kimlik dizesi + mekân + ışık + yasaklar + stil ekinden derler; `NNN_son` bitiş görseli istemini `bitis_durumu`ndan derler; referans görsellerini seçer | `SAHNELER.json`, defter, evren → `SAHNELER.json` alanları | **P0** |
| `evren.py` | Seri kütüphanesi: `--kur`, `--bagla`, `--spec-dogrula`, `--kilitle`, `--surum-ac`, `--film-sonu`, `--disa-aktar` (geriye uyum: `01_KARAKTERLER/<id>.jpg`). Kilitli dosyalarda özet denetimi | `KART_SPEC.json`, kartlar → `EVREN/<SERI>/…`, `EVREN_BAG.json` | **P0** |
| `kor.py` (modül) | Kör görev hazırlar (görselleri anonimleştirir, `SORULAR.json` üretir, kritik soruları karışık sırayla ikiler), cevapları okur, görüntü-sol/sağ → anatomik sol/sağ çevirir, beklenenle alan alan karşılaştırır | aday görseller, beklenen durum → `_KOR_GOREV/<is_id>/`, karşılaştırma sonucu | **P0** |
| `kare_denetim.py` | G1: `--yerel` (ölçüm modülleri), `--kor-gorev`, `--karar` (kural tablosu + seçim sıralaması), `--hakem` (hakem kararlarını işler). Seçilen kareyi `SIRALI_GORSEL/NNN.jpg`'ye koyar, SHA1'i rapora yazar | `_ADAYLAR/`, defter, evren → `_RAPOR/G1_P<n>.json`, `YENIDEN_URET.json` | **P0** karar mantığı (sahte ölçümle) / **P1** gerçek ölçüm |
| `duzeltme.py` | CORRECTION şablonları; tek seferlik küçük düzeltmeler (ayna, kenar kırpma, renk eşleme) ve işaret dosyası; tur sayacı; 2 turdan sonra kaçış kaydı. Aynı alan için CORRECTION cümlesi **eklenmez, değiştirilir** (istem turdan tura şişmesin) | `YENIDEN_URET.json` → istemler, `_RAPOR/ISARET/`, `DUZELTME_KAYDI.jsonl` | **P0** |
| `kart_denetim.py` | Kart kapısı: yüz sayısı, görünüm öz tutarlılığı, kadro ayrışması, stil, fon; kör görev; karar; banka üretimi | kart adayları → `_RAPOR/KART_KAPISI.json`, `banka_vN.npz` | **P0** karar / **P1** ölçüm |
| `kare_zinciri.py` | `--plan`: Z0/Z1/Z2 ve dalgalar, derinlik, yeniden demirleme kararı. `--cikar`: kesme penceresinden en iyi kareyi seçer, büyütür, G1-zincir kaydı yazar | `SAHNELER.json`, G1/V raporları, klipler → `ZINCIR_PLANI.json`, `SIRALI_GORSEL/NNN.jpg` | **P0** plan / **P1** çıkarma |
| `kalite_denetim.py --klip` | V1: ffprobe, `blackdetect`, `freezedetect`, `silencedetect`, `blurdetect`, PySceneDetect, titreme. (Final karışım LUFS bölümü ses/kurgu uzmanlarıyla ortak dosyada) | klip → `_RAPOR/V1_P<n>.json` | **P0** (ffmpeg bulutta da var) |
| `video_denetim.py` | `--onceden` (K1-ön, kare dizisi), `--klip` (V2 + V3 kör görev), `--gecis` (K1, kurgu sırası). Hakem için kare şeritleri ve kare çiftleri üretir | klipler, kareler, defter → `_RAPOR/K1ON_*`, `V2V3_*`, `K1_*` | **P1** (karar mantığı P0) |
| `olcum/` paketi | Ölçüm arka uçları, hepsi tek arayüzle (`olc(gorsel, beklenen) → dict`) ve `sahte` arka ucuyla: `kimlik.py` (YuNet+SFace, kadro bankası, `scipy.optimize.linear_sum_assignment` ile eşleme), `gorunum.py` (DINOv2-small, CLIP (kontrol.py'deki modelle aynı), OWLv2 nesne bulucu, maskeli yama benzerliği), `poz.py` (MediaPipe Pose/Hand/Face: bilek–nesne, parmak açıklığı, yaw), `isik.py` (Lab, parlaklık, yanak oranı), `teknik.py` (keskinlik, boyut) | — | **P1** (`sahte` arka uç **P0**) |
| `gemini_paket.py` / `gemini_al.py` | (belgede var, pakette yok) Yeniden yazılır: `--aday N`, `--kartlar`, `FILE NAME: NNN_a`, > 10 ek dosyada `REFERANSLAR.zip`, kart sayfaları tek dosya; içe alırken `_ADAYLAR/`'a koyar, **SIRALI_GORSEL'e doğrudan koymaz** | `SAHNELER.json` → paket klasörü; ZIP → `_ADAYLAR/` | **P0** |
| `ders_defteri.py` | Kapı kararlarını sonradan bulunanlarla eşler, kaçırma/yanlış alarm sayar, korkuluklu kalibrasyon önerir, kural adaylarını ve deneme sonuçlarını izler | raporlar → `DERSLER.jsonl`, `KALIBRASYON.json` | **P1** (öteki uzmanlarla ortak olabilir) |
| `saglayicilar/gozlemci_*.py` | Yeni sağlayıcı türü `gozlemci`: `claude_ajan` (dosya devri + çıkış 2), `claude_api` (gözetimsiz mod; anahtar `AYARLAR/claude_anahtar.txt` ya da ortam değişkeni, asla yazdırılmaz), `sahte` (yan dosyadaki gerçeği döndürür) | — | **P0** (`sahte`, `claude_ajan`) / **P1** (`claude_api`) |
| `saglayicilar/gemini_ajan.py` | Toplu görsel sağlayıcısı: paketi hazırlar, ZIP gelene kadar `Durdur` ("paket hazır: …") | — | **P0** |
| `saglayicilar/vertex_gorsel.py` | Ücretli görsel API'si (≈ 0,134 $/görsel, `06_SERVISLER_VE_MALIYET.md`), onaylı; düzeltme turlarında Flow görsel yükünü azaltmak için | — | **P2** |
| `testler/test_sureklilik.py` | K0: el değiştirme olaysız → HATA; kaybolma → HATA; 180° → HATA; kalıcı yara sahne sınırında kayboldu → HATA; zaman geri gitti → HATA | ORNEK_3_SAHNE + sentetik planlar | **P0** |
| `testler/test_g1_karar.py` | `sahte` ölçüm + `sahte` gözlemci: aynalanmış kare → kadraj sırası HATA (02§7); fazla yüz → HATA; tek kaynaklı ters el → BAYRAK → hakem; iki aday da HATA → CORRECTION; ölçüm modeli yok → "ÖLÇÜLEMEDİ" (asla GEÇ değil); G1'siz kare video aşamasına gönderilmez | — | **P0** |
| `testler/test_v1.py` | ffmpeg ile sentetik klip: 1 sn siyah ekle → HATA; 1,5 sn donma → HATA; ortada sert kesme → HATA (PySceneDetect kuruluysa; yoksa test atlanır) | — | **P0** |
| `testler/test_zincir.py` | dalga planı, derinlik 3 → yeniden demirleme, kaynak V3 HATA → Z0'a düşme | — | **P0** |

### 6.2 Değişecek mevcut dosyalar

| Dosya | Değişiklik | Öncelik |
|---|---|---|
| `film.py` | Yeni aşamalar ve sırası: `evren → kart_spec → kart_uret → kart_kapisi → defter(K0) → gorsel_derle → istem_denetim → gorsel(2 aday) → g1 → on_gecis → [animatik] → zincir_plani → video(dalga) → v1 → v2v3 → zincir_cikar → [ses, muzik, kurgu] → gecis(K1) → ders`. Video aşaması G1 GEÇ + SHA1 eşleşmesi olmayan planı göndermez. Ajan devri (`_AJAN_ISLERI/`, çıkış 2). `imza()` G1 kayıtlarını da kapsar | **P0** |
| `istem_denetim.py` | Ek kurallar: kimlik dizesi birebir geçiyor mu; `gorsel_istem`'de süren eylem fiili; her görünen karakterin iki eli tarif edilmiş mi; aynı alan için birden çok CORRECTION; referans sayısını karakter kartı olarak say (mekân plakası ayrı) | **P0** |
| `saglayicilar/sahte.py` | `gorsel` iki aday üretir ve yan dosyaya "gerçek" yazar (kim nerede, hangi el); test için hata enjeksiyonu (`SAHTE_HATA=ayna,fazla_kisi`) | **P0** |
| `kontrol.py` | Gelen görselleri `SIRALI_GORSEL/`'e değil `_ADAYLAR/`'a koyar (G1 seçsin); CLIP yükleyicisi `olcum/gorunum.py` ile ortak | **P1** |
| `memmet.py` | Video gönderiminde başlangıç karesini G1 kaydından okur ve özeti doğrular; Z2 için `SIRALI_GORSEL/NNN_son.jpg`'i "Bitir" yuvasına koyar (mevcut `bitis_karesi` sahne numarası da çalışmaya devam eder); düzeltme görsellerinde x2 çıktı. **Tempo, uyarıda durma ve reCAPTCHA davranışına dokunulmaz** | **P1** |
| `kurulum.py` + `requirements.txt` | `mediapipe` (cp310 Windows wheel'i olan sürüm sabitlenir; OpenMontage kendi venv'inde 0.10.14'te kalır), `scenedetect==0.7.2`; model dosyaları (YuNet/SFace ONNX opencv_zoo'dan, MediaPipe `.task` dosyaları, DINOv2-small, OWLv2-base) bir kez indirilir, sonra `HF_HUB_OFFLINE=1` | **P1** |
| `.claude/agents/sureklilik-denetcisi.md` | Modlar (kagit/hakem/kacis/ders), `model: opus`, çıktı biçimleri §3.2 | **P0** |
| `.claude/agents/kor-gozlemci.md`, `kart-tasarimcisi.md` | Yeni (§3.1, §3.3); `kor-gozlemci`'ye okuma kısıtlayan hook | **P0** |
| `.claude/agents/istem-muhendisi.md` | "CORRECTION modu" bölümü `duzeltme.py`'ye devredilir (başka uzmanla uzlaşılacak) | P1 |

---

## 7. Makinenin denetleyeceği eşikler (kaynağıyla)

Kodlar: **H** = HATA (aday elenir / plan geçmez), **B** = BAYRAK (hakem ya da ikinci kaynak bakar).
**Ölçülemedi kuralı (kesin karar 6):** Bir ölçüm yapılamazsa (model kurulu değil, yüz çok küçük, sırt dönük) sonuç `ÖLÇÜLEMEDİ` olur ve **B** sayılır. Hiçbir zaman sessizce GEÇ sayılmaz.
"Kaynak" sütununda (tahmin) yazan değerler başlangıç değeridir ve §7.9'daki kalibrasyonla ayarlanır.

### 7.1 K0 — kâğıt üstü süreklilik (kredi yok, ağ yok)
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| `bitis_durumu`[N] ≡ `baslangic_durumu`[N+1] (kim, nerede, nesne kimde/hangi elde/durumu, poz) | `yeni_sahne` dışında eşit | H | ZAN Z0#16, ZAN§3.7 |
| Durum farkının `eylem_zinciri`nde karşılığı (olay ↔ adım) | her olayın bir adımı var | H | kesin karar 2 (bu belge) |
| Durumu değiştirmeyen eylem adımı | — | B | bu belge |
| Nesne sahibinin açıklamasız değişmesi | 0 | H | 02§6.2 K0 |
| Nesnenin **elinin** açıklamasız değişmesi | 0 | **H** (02'de B; kesin karar 2 "hangi el" gereği yükseltildi) | 02§6.2 + kesin karar 2 |
| Kadrajdaki karakter sonraki planda ne kadrajda ne `kadraj_disi_ama_mekanda` ne `giris_cikis`'te | 0 | H | 02§6.2 |
| Aynı sahne grubunda `kamera_tarafi` değişimi `eksen_gecis` olmadan | 0 | H | ZAN§3.3, Z0#17 |
| Karşılıklı planlarda bakışlar birbirine dönük | evet | H | ZAN Z0#18 |
| Krokiden hesaplanan soldan sağa sıra ↔ plandaki `kadraj_sirasi` | eşit | H | bu belge (geometri) |
| Işık mekân/sahneden farklı ve `isik_degisimi` boş | 0 | H | 02§6.2 |
| Kalıcı özelliğin (yara, kir, ıslaklık, kostüm hasarı, taşınan nesne) olaysız kaybolması | 0 | H | DERS ("kim nerede / nesnenin yolu"), bu belge |
| Gün saatinin geri gitmesi (geri dönüş işareti yok) | 0 | H | bu belge; geri dönüş ≤ 20 sn `RE:geri_donus_max_sn` |
| Karakter referansı | ≤ 2 | H | `RE:referans_max` |
| Z1 zincir derinliği | ≤ 2 | H | 02§6.2 |
| Kurulum kullanımdan önce | evet | H | 02§6.2, ZAN§4.2 |
| Her görünen karakterin iki elinin durumu yazılmış (`gorunmuyor` dahil) | evet | H | kesin karar 2 |

### 7.2 Kart kapısı
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Birleşik sayfada bulunan yüz sayısı | = beklenen görünüm sayısı | H | bu belge |
| Aynı karakterin görünümleri arası SFace kosinüsü | < 0,363 H · 0,363–0,45 B · ≥ 0,45 geç | H/B | 0,363 OpenCV resmî (02§1.1); 0,45 (tahmin) |
| İki farklı karakter arası SFace kosinüsü | ≥ 0,363 H · 0,25–0,363 B | H/B | 0,363 resmî; 0,25 (tahmin) |
| CLIP "photograph" olasılığı (karşı sınıflar: illustration, 3D render, plush toy, cartoon) | < 0,5 → kör gözleme; kör de "çizim" derse H | B/H | YR A6 dersi; 0,5 (tahmin) |
| Kör gözlemde NE YOK listesindeki öğe (fermuar, modern mont…) | 0 | H | YR §5, BK§2.9 |
| Kör gözlemde tarifteki zorunlu öğelerin (saç rengi/biçimi, kostüm parçaları, asimetrik iz tarafı) uyumu | hepsi | H | bu belge |
| Aday sayısı / tur | 3 aday, ≤ 2 tur | — | YR A6; HAT §5 |

### 7.3 G1 — başlangıç karesi
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Çözünürlük ve en-boy | 1376×768 (kırpma sonrası), 16:9 | H | BK§4.1.12 |
| Yüz ölçülebilirliği | YuNet skoru ≥ 0,9 ve yüz kutusu ≥ 48 px yükseklik; değilse ÖLÇÜLEMEDİ | B | 0,9 OpenCV örnek betiği varsayılanı (**doğrulanmalı**); 48 px (tahmin) |
| Kimlik (insan) | ≥ 0,45 geç · 0,363–0,45 B · < 0,363 H | H/B | 02§6.2 (0,363 resmî, 0,45 tahmin) |
| Kimlik fark payı (beklenen − kadrodaki en yakın öteki) | ≥ 0,05 | B | (tahmin); "B22K'de Bram'a benzemeyen adam" dersi (H/proje-b2) |
| Bulunan yüz sayısı > kadrajdaki görünür yüzlü insan sayısı | 0 fazla | H | 02§6.2 |
| Eksik yüz | — | B (sırt dönük olabilir) | 02§6.2 |
| Arka plandaki küçük yüz (kutu < kare yüksekliğinin %4'ü) | sayılmaz; kör gözlem "kişi" derse B | B | (tahmin) |
| Kadraj sırası (yüz/kişi kutularının x sırası) | = `kadraj_sirasi` | H | 02§6.2 |
| Kadraj üçte biri (karşılıklı çekimde A sol, B sağ üçte bir) | beklenen üçte bir | karşılıklı çekimde H, diğerlerinde B | ZAN§3.3 |
| Bakış (MediaPipe yaw) | \|yaw\| > 15° ve işaret `yon` ile ters | H | 02§6.2; 15° (tahmin); işaret kuralı bir test görseliyle bir kez doğrulanır (02§4) |
| Nesne hangi elde | yerel (Pose bileği + OWLv2) ve kör gözlem ikisi de ters → H; biri ters → B | H/B | 02§6.2 (tek başına H verilmez) |
| İnsan olmayan karakter/nesne DINOv2 kırpıntı kosinüsü | < 0,5 | B | 02§6.2 (tahmin) |
| Yaratık ölçeği (kutu yüksekliği / yakındaki insan yüz kutusu, karttaki orana göre) | ± %35 | B | (tahmin); "minik çizme" dersi (DERS) |
| Mekân benzerliği (kişiler maskeli DINOv2 ↔ kamera konumu plakası) | < 0,60 | B | (tahmin) |
| Işık yönü (yanak parlaklık oranı > 1,25 olan taraf ≠ `isik.yon`) | — | B | 02§6.2 (tahmin) |
| Sahne içi renk (Lab ΔE, sahne grubunun ilk onaylı karesine) | > 10 | B | 02§6.2 K1 değeri (tahmin) |
| Stil (CLIP "photograph") | < 0,5 ve kör "çizim" | H | YR A6 dersi (tahmin) |
| Yazı / logo / filigran (kör gözlem, iki soru) | 0 | H | 02§5 `yasaklar` |
| Anatomi bozukluğu (fazla uzuv, kaynaşık parmak, bozuk yüz; kör gözlem) | iki tekrarda da var → H; birinde → B | H/B | 02§5; parmak sayımı modeller için zayıf (§9) |
| Plan yasakları (`ucuncu_kisi`, `ikinci_isik_kaynagi`, `acik_kapi`…) | 0 | H | 02§6.1 |
| Keskinlik (Laplacian varyansı / parti medyanı) | < 0,5 | B | (tahmin) |
| Kritik alanlarda kör gözlemin iki cevabı uyuşmuyor | — | B (alan "belirsiz") | bu belge |
| Aday sayısı / CORRECTION turu | 2 aday / ≤ 2 tur | — | 01§A3 (ViMax); HAT §5 |

### 7.4 K1-ön (başlangıç kareleri) ve K1 (kurgu sırası)
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| `devam` geçişi: DINOv2 kosinüsü | < 0,80 | H | 02§6.2 (tahmin) |
| `devam` geçişi: ortalama parlaklık farkı | > 12/255 | B | 02§6.2 (tahmin) |
| `kesme_ayni_mekan`: Lab ΔE / parlaklık farkı | > 10 / > 20/255 (`isik_degisimi` yoksa) | B | 02§6.2 (tahmin) |
| Aynı kamera konumuna dönüş: o konumun ilk onaylı karesine DINOv2 | < 0,70 | B → kör gözlem ("kapı hâlâ solda mı") | 02§6.2 (tahmin) |
| Kostüm (gövde kırpıntısı DINOv2) sahne içinde | önceki plana < 0,6 | B | (tahmin) |
| Geçişin iki yanında kimlik | §7.3 bantları | H/B | 02§6.2 |

### 7.5 V1 — teknik video
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| `ffprobe` süre (8 sn klip) | ≥ 7,5 sn, video akışı var | H | 02§6.2 (kesik indirme dersi, DERS) |
| Çözünürlük | 1280×720 | H | 720p kararı (BK§8 #1) |
| `blackdetect=d=0.1:pic_th=0.98:pix_th=0.10` | kullanılan pencerede 0 aralık (planlı karartma hariç) | H | 02§6.2; `pic_th` 0,98 ffmpeg varsayılanı, `d` 2,0'dan kısaltıldı |
| `freezedetect=n=-60dB:d=1.0` | kamera sabit değilse ya da özne hareketi bekleniyorsa 0 | H | 02§6.2; `n` varsayılan, `d` kısaltıldı |
| PySceneDetect `ContentDetector(threshold=27)` klip içi kesme | 0 | H (kesme kullanılan pencerenin dışındaysa kırp) | 02§3 (27 = varsayılan) |
| Titreme (ardışık kare MAE) | > 3 × klip medyanı ve > 8 (0–255) | B | 02§6.2, VBench yöntemi (tahmin) |
| Replik penceresinde `silencedetect=n=-50dB:d=1.0` | 0 | B (dudak/ses uzmanına) | 02§6.2 |
| `blurdetect` ortalaması | > 1,5 × klip medyanı | B | 02§6.2 (tahmin) |

### 7.6 V2 — klip içi süreklilik
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Örnekleme | 0,5 sn arayla 17 kare | — | 02§6.2 |
| Kimlik kayması | ilk kareye göre > 0,15 düşüş **ve** < 0,363 | H | 02§6.2 (0,363 resmî, 0,15 tahmin) |
| Yüz/kişi sayısının `giris_cikis` dışında değişmesi | 0 | H | 02§6.2 |
| Ardışık kare DINOv2 sıçraması | klip medyanından > 0,15 düşük | B → kör gözlem | 02§6.2 (tahmin) |
| Ekran yönü (kişi kutusu x merkezi ilk → son) | işaret = `hareket_yonu` | H | 02§6.2, ZAN§3.3 |
| İlk kare sadakati (video ilk karesi ↔ onaylı başlangıç karesi DINOv2) | < 0,85 | B | 02§6.2 (tahmin) |

### 7.7 V3 — bitiş durumu (atomik zincirin videoda denetimi)
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Kesme noktasındaki karenin kör gözlemi ↔ `bitis_durumu` kritik alanları (nesne kimde/hangi elde, kişi var/yok, kapı/ateş durumu) | hepsi uyumlu | H | kesin karar 2 (bu belge) |
| Her adımın `bit` saniyesindeki Pose ölçümü (ör. `extend_arm` → dirsek açısı) | > 140° | B | (tahmin) |
| Z1 kaynağı olacak klipte V3 | GEÇ şart | H (zincir kurulmaz, Z0'a düşer) | kesin karar 3d |

### 7.8 Zincir ve düzeltme
| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Zincir karesi arama penceresi | `[kesim − 0,5, kesim + 0,3] ∩ [0,5, klip − 0,5]` | — | güvenli pencere `RE:kullanim_bas_varsayilan_sn`, `RE:kullanim_son_pay_sn`; genişlik (tahmin) |
| Bitiş tutma süresi | 0,5 sn | — | `RE:bitis_tutma_sn` |
| Derinlik | ≤ 2, 3. nesilde yeniden demirleme | H | 02§2.3 |
| Yeniden demirlenen kare ↔ zincir karesi DINOv2 | ≥ 0,90 | H | (tahmin) |
| Küçük düzeltme: kenar kırpma | her kenarda ≤ %10, bir kez | — | (tahmin); DERS ("bir kez") |
| Ayna | yalnız `asimetrik` listesi boşsa, bir kez | — | ZAN§3.3; DERS |

### 7.9 Kalibrasyon korkulukları (ders defteri eşikleri böyle değiştirir)
| Kural | Değer | Kaynak |
|---|---|---|
| Hedef kaçırma oranı (kapı/alan başına) | ≤ %10 | 02§7 |
| Bir kalibrasyonda eşik adımı | ≤ 0,03 (kosinüs), ≤ %10 (oran eşikleri) | (tahmin) |
| SFace HATA eşiği | **0,363'ün altına inemez** (yalnız yükselebilir) | 02§1.1 resmî değer |
| Kalibrasyon için en az etiketli örnek | ≥ 30 / kapı-alan | (tahmin) |
| Etiket kaynağı | hakem kararı, sonradan V2/V3/kurgu seyircisi bulgusu, kullanıcı notu; B3'ün etiketli 44 karesi (21 bozuk) başlangıç seti | DERS, 02§7 |
| Güvenlik kuralları (Flow'da dur, filtre kelimeleri, referans ≤ 2) | öğrenmeyle **gevşetilemez** | BK§6.2, DERS |

---

## 8. Kesin kararların (atomik zincir + 6 özellik + gerekiyorsa ses kararı) kendi alanımda uygulanışı

### 8.1 Karar 1 — Kullanıcıya yalnız konu sorulur
- Bu alandaki bütün kararları ekip verir: karakterin görünüşü (`kart-tasarimcisi` tarif eder, kart kapısı teknik eler, `yonetmen` sanat seçimi yapar), varyantlar, hangi adayın seçileceği (kod), CORRECTION (kod + hakem), plan değişikliği (yönetmen), eşik kalibrasyonu (ders defteri).
- Eskiden kullanıcı onayı olan "karakter görünüşü" ve "mekân kartları" (BK§7.3) varsayılan akıştan çıkar. Yalnız `--onayli` modda gösterilir.
- Kullanıcıya kalan **işletme** (karar değil) dokunuşları dürüstçe söylenmeli: (a) Gemini ajanı paketi seçilirse ZIP'i taşımak; (b) Flow için Memmet'in yarı otomatik modunda gönder'e basmak ya da reCAPTCHA'yı çözmek; (c) durma bildirimleri. (a)'yı sıfırlamak isteyen için `vertex_gorsel` (ücretli) sağlayıcısı önerilir (§9 açık soru 1).

### 8.2 Karar 2 — Atomik eylem zinciri
| Kuralın parçası | Bu alanda nasıl uygulanır | Denetleyen |
|---|---|---|
| Başlangıç durumu = başlangıç karesi | `gorsel_istem` yalnız `baslangic_durumu`ndan derlenir (`istem_derle.py`). Kare, durumun **her alanına** karşı ölçülür (kim, nerede, yön, poz, iki elin durumu, nesneler, mekân durumu, ışık) | G1 (yerel + kör + kod) |
| Görsel istemde sonuç ya da süren eylem yok | Anlık görüntü kuralı: süren eylem fiili listesi `gorsel_istem`'de yasak; poz durağan anlatılır ("left arm extended toward the key, fingers 10 cm above it") | `istem_denetim.py` |
| Hangi el, hangi yön, kaç parmak açık | `eller.sag/sol.tutar` + `hal` sözlüğü (§5.5) → sabit İngilizce ifade. Görselde Pose bileği + OWLv2 + Hand Landmarker (parmak açıklığı) + kör gözlem | G1, V3 |
| Bitiş durumu = sonraki klibin başlangıcı | Kâğıtta defter zorunlu kılar (K0). Videoda V3 kesme noktasındaki kareyi `bitis_durumu`na karşı ölçer. `devam` geçişinde Z1 bunu **piksel düzeyinde** garanti eder | K0, V3, Z1 |
| Klip başına 2–3 adım | Adım sayısı yönetmen kapısında (Z0#13). Bu alan her adımın bitişinde Pose örneğiyle "adım gerçekleşti mi" bakar | V3 (B) |
| Eylem tamamlanmazsa | Yeniden üretimde Z2: bitiş durumu görseli derlenir, G1'den geçer, "Bitir" yuvasına konur. Veo'da bitiş karesi referans görsellerle birlikte verilemediği için kimlik yine bu iki karede pişmiş olur (02§2.1) | `duzeltme.py --video` |

### 8.3 Karar 3a — Videodan önce animatik + habersiz seyirci
- Animatik yalnız **G1'den geçmiş** karelerle kurulur. Böylece seyirci bozuk kareye değil hikâyeye puan verir.
- Bitiş durumu kritik planlarda (Z2) bitiş görseli de animatiğe girer. Seyirci eylemin sonucunu görür ("anahtar eline geçti mi?"), kâğıtta kalan adım ekrana çıkar.
- K1-ön kare çiftleri animatik izleme paketine "kopukluk adayı" diye eklenir. Seyircinin görsel bulguları A9 kuyruğuna, hikâye bulguları yönetmene gider.

### 8.4 Karar 3b — Dünya durumu defteri + otomatik zıplama denetimi
- Defteri **makine tutar**: yönetmen yalnız plan durumlarını yazar. `sureklilik_defteri.py` olayları çıkarır, anlık durumları hesaplar ve tutarsızlığı HATA sayar (K0).
- Zıplama dört yerde aranır: kâğıtta (K0), başlangıç karelerinde (G1 alanları + K1-ön), klip içinde (V2), kurgu geçişinde (K1).
- Defter filmden filme taşınır: film sonu durumu `EVREN/<SERI>/DURUM_SON.json` olur ve sonraki filmin başlangıcıdır (B3 sonunda "Bram sürgün kostüm 2" gibi, H/proje-b3).

### 8.5 Karar 3c — Referansla otomatik yüz kontrolü
- İnsan: OpenCV YuNet + SFace (Apache-2.0, ticari kanal için uygun; InsightFace modelleri "non-commercial" olduğu için ana hatta yok, 02§0). Karakter başına **çok görünümlü banka** (yüz panelinin 4 görünümü + tam boy kartın 2 yüzü). Karar: görünümlere en yüksek benzerlik + kadrodaki ötekilere fark payı + çok yüzlü karede eşleme algoritması.
- İnsan olmayan: OWLv2 ile bul, DINOv2 ile karttaki kırpıntılara karşılaştır, ölçeği insan yüzüne oranla ölç. Kör gözlem renk/iz gibi öznitelikleri yazar.
- Yüz görünmüyorsa (sırt, kask, uzak plan): gövde/saç kırpıntısı DINOv2 ↔ **arka görünüm kartı** + kör gözlem. Sonuç en iyi ihtimalle B (hakem). Bu yüzden yönetmene "kimliği yalnız sırttan taşıyan plan" sayısını azaltma uyarısı gider.
- Uygulandığı noktalar: kart kapısı (ayrışma), G1, V2 (her 0,5 sn), Z1 zincir karesi, K1.

### 8.6 Karar 3d — Kare zinciri
- **Z1 (son kare → sonraki klibin başlangıcı)** `devam` geçişlerinin zorunlu yöntemidir. "Son kare" teknik son kare değil, **kurguda kullanılan son kare**dir (kesme noktası). Güvenli pencereden en keskin, en durgun, kimliği en yüksek kare seçilir.
- Kalite birikimi riskine karşı derinlik ≤ 2 ve yeniden demirleme. Zincir karesi yalnız boyutlandırılır, üretken modelle "temizlenmez" (kimliği değiştirebilir).
- Seri bağımlılık üretimi yavaşlatır. Çözüm hız değil sıra: dalga planı. Flow temposu zaten yavaş (BK§6.2.6) olduğu için ek gecikme dalga sayısıyla (≤ 3) sınırlıdır.
- Açı değişen kesmede (`kesme_ayni_mekan`) video beklenmez: yeni kare, kaynak planın onaylı başlangıç karesinden ve defterden türetilir (kamera ağacı). Videonun bitişi gerçekten öngörülemiyorsa (duman, dağılan nesneler) yönetmen `son_kare_referans: true` der ve o plan sonraki dalgaya kayar. O zaman yeni açı görseli Flow'da değil API sağlayıcısında üretilir, çünkü Flow'da görsel ile videoyu aynı oturumda karıştırmak uyarı riski taşır (DERS).
- Z1 karesi tutmazsa (G1-zincir H) plan sessizce bozulmaz: planlanmış aday kareye (Z0) düşer ve ders defterine yazılır.

### 8.7 Karar 3e — Kendi kendine öğrenen ders defteri
1. **Kayıt:** her kapı kararı (ölçü, değer, karar) ve sonradan olanlar (V2/V3/K1/kurgu seyircisi/kullanıcı notu aynı planda bir şey buldu mu) `DERSLER.jsonl`'e yazılır. Sınıflar: `kacirma`, `yanlis_alarm`, `dogru`.
2. **Kalibrasyon:** ≥ 30 etiketli örnek biriken her kapı/alan için eşik, kaçırma ≤ %10 olacak biçimde korkuluklar içinde ayarlanır (§7.9). Karakter başına kimlik eşikleri `KALIBRASYON.json`'a yazılır, çünkü bazı yüzler (sakal, koyu ışık) sistematik olarak düşük benzerlik verir.
3. **Kural adayı:** aynı kök neden ≥ 3 kez ve ≥ 2 sahne grubunda görülürse (tahmin) aday olur. Üç tür kural vardır: (a) **önleyici istem eki**: ilgili plan türlerine CORRECTION cümlesi baştan eklenir (ör. nesne taşıyan her planda "her OTHER hand is empty"); (b) **eşik**: (2)'deki gibi; (c) **plan uyarısı**: yönetmene "iki el aynı yarıda ve nesne var → ekleme planına böl" uyarısı.
4. **Deneme:** kural sonraki 40 uygun planın yarısına uygulanır (tek/çift plan numarası, tahmin). Hata oranı karşılaştırılır. Düşürüyorsa kalıcı olur, düşürmüyorsa geri alınır. Karar ve gerekçe `Ruling: <karar> — <neden> — <yanlışsa maliyeti>` biçiminde yazılır (03§B6).
5. **Sınır:** güvenlik ve kullanıcı kuralları öğrenmeyle gevşetilemez. Kural metni `sureklilik-denetcisi` tarafından yazılır, ana Claude kaydeder. Seriye özel dersler `EVREN/<SERI>/DERSLER.jsonl`'de, genel olanlar `YZ_FILM/BILGI/DERS_DEFTERI.jsonl`'de durur.

### 8.8 Karar 3f — Kalıcı seri evreni kütüphanesi
- Karakter, kostüm, mekân, nesne kartları, kimlik dizeleri, yüz bankaları, kalibrasyonlar ve son dünya durumu `EVREN/<SERI>/` altında tutulur. Ses kimliği için bir yer tutucu bırakılır (`ses_ref`), içeriği ses uzmanınındır.
- Kilitli kart **değişmez**. Değişiklik yeni sürümdür (`surum`, `gecmis`). Film hangi sürümü kullandığını `EVREN_BAG.json`'da saklar. Dosya özeti uyuşmazlığı (kart elle değişmiş) hattı durdurur.
- Varyantlar (kostüm 2, yırtık kol, büyümüş yaratık) her zaman **onaylı karttan referansla** türetilir (YR A6). Türetilen varyant da kart kapısından geçer ve öz tutarlılık ana karta göre ölçülür.
- Eski filmlerin kartları (EMBERFALL, B1–B3) `evren.py --ice-al` ile kütüphaneye alınır. Yüz paneli ve arka görünüm eksikse yalnız bunlar üretilir, onaylı görünüş korunur.

### 8.9 Karar 4 — Ses/dudak uyumu (bu alanın görüntü tarafındaki görüşü)
- Karar ses uzmanınındır. Görüntü tarafından gerekçe: **Veo'nun kendi konuşması + ses dönüştürme** yolu görüntüye ikinci bir model dokundurmaz. Bu yüzden G1/V2 kimlik ölçümleri geçerli kalır. TTS + dudak senkronu yolu ağız bölgesini yeniden üretir; bu yol seçilirse çıkan klip **V2'den yeniden geçmek zorundadır** (kimlik ve ağız çevresi bozulması).
- Hangi yol seçilirse seçilsin konuşmalı planların başlangıç karesi şunları sağlamalı: ağız kapalı ve görünür (donuk açık ağız yok), `yuz_gorunur: true`, \|yaw\| ≤ 45° (tahmin), yüz yüksekliği karenin ≥ %12'si (tahmin). Bunlar dudak senkronu yedeğinin çalışabilmesi için gerekir. Konuşma sırasında en çok 1 fiziksel adım (ZAN§2.3).

### 8.10 Karar 5 — Memmet seri üretim aracı değil; bot atlatma yok
- Bu alanın Flow'a etkisi yalnız **daha az ve daha doğru gönderim**dir: G1 bozuk kareyi videoya göndermez, yeniden çekim azalır.
- Görsel düzeltmeleri Flow'da yapılacaksa: x2 çıktıyla gönderim sayısı yarıya iner, tempo `MEMMET_AYAR.json` (17.10) değerlerinde kalır, kullanıcı başındaysa `--mod elle`. Günlük görsel gönderim tavanı ve görsel→video bekleme süresi ayar dosyasındadır (değerleri kaynakta yok; ders defteri kullanıcının hesabına göre ayarlar).
- Uyarıda, reCAPTCHA'da, kredi bitince DUR. Hazır sonuçlar `memmet_topla.py` ile yeni gönderim yapmadan toplanır. Bu alan hiçbir otomatik yeniden deneme yazmaz.

### 8.11 Karar 6 — Hiçbir iş üstün körü yapılmaz
- Her aday tam kapıdan geçer. Örnekleme ("her 5 kareden 1'ine bak") yok. Kör gözlem her adayda yapılır, kritik alanlar iki kez sorulur.
- Eksik araç ya da model "geçti" sayılmaz, `ÖLÇÜLEMEDİ` → hakem olur (§7 başı).
- Bozuk kare ya da klip "idare eder" diye kullanılmaz. 2 turda düzelmeyen planı yönetmen değiştirir.
- Tasarruf için aday sayısı azaltılmaz. Kör gözlem maliyeti (≈ 2 milyon token/film, tahmin) kabul edilir ve kullanıcıya baştan söylenir.

---

## 9. Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

### 9.1 Riskler ve önlemler
| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | SFace'in 0,363 eşiği gerçek fotoğraflar için verilmiş; sinematik YZ karelerinde (yan profil, karanlık, sakal) benzerlik düşebilir (02§1.1) | Yanlış alarm ya da kaçırma | Üç bantlı karar + fark payı + karakter başına kalibrasyon (§8.7). İlk filmden önce **kalibrasyon partisi**: zor durumları kapsayan 20 plan (iki kişi, el–nesne, yaratık, düşük ışık, profil, sırt, Z1 derinlik 1–2, Z2). Maliyet ≈ 20 × 12 = 240 kredi + %20 pay (sayı tahmin) |
| R2 | Görüntü-dil modelleri sol/sağ eli ve parmak sayısını sık karıştırır | Ters el kaçar ya da yanlış alarm | Soru görüntü koordinatında, anatomik çeviri kodda; kritik alan iki kez karışık sırayla; yerel Pose ölçümüyle çapraz kontrol; anlaşmazlık hakeme. Parmak sayımı güvenilmez kabul edilir: anatomi en iyi ihtimalle B'dir, kesin güvence değildir |
| R3 | MediaPipe handedness girdiyi ayna kabul ediyor; sırt dönük karakterde el ataması tersine döner (02§4) | Ters el ölçümü hatalı | Birincil ölçüm Pose bilekleri (kişinin kendi sol/sağı), handedness ikinci görüş; sırt dönükse ÖLÇÜLEMEDİ → hakem |
| R4 | OWLv2 küçük nesneleri (anahtar, yüzük) 1376 px karede kaçırabilir | El–nesne ölçülemez | El çevresinden büyütülmüş kırpıntıda ikinci arama; yine yoksa kör gözlem + hakem. Yönetmene: kritik küçük nesne → ekleme planı (ZAN§3.5) |
| R5 | Z1'de 720p sıkıştırma birikir; Veo'nun ilk 0,3–1,0 sn'lik durağanlığı bitişikte takılma hissi verir (ZAN§2.2) | Zincirli planlarda kalite düşer ya da hareket "takılır" | Derinlik ≤ 2 + yeniden demirleme; Z1 planları arasına tepki/ekleme planı; pilotta derinlik 0/1/2 kliplerin bulanıklık ve V2 ölçüleri karşılaştırılır, gerekirse derinlik 1'e iner |
| R6 | Dalga sırasında görsel üretimi ile video üretiminin Flow'da karışması hesabı işaretletebilir (DERS) | Video aşaması durur | Dalga içi yeni açı görselleri Flow'da değil API sağlayıcısında; Flow'da görsel düzeltme ile video ayrı oturum/gün; bekleme ayarı |
| R7 | Gemini ajanı paketi kullanıcı eli gerektiriyor; "yalnız konu" hedefiyle gerilim | Kullanıcıya iş kalır | Sağlayıcı zincirinde ücretli görsel API'si seçeneği; varsayılanın ne olacağı kullanıcı bütçesine bağlı (açık soru 1) |
| R8 | Windows/Python 3.10 kurulum ağırlığı: son cp310 Windows torch wheel'i 2.9.1, onnxruntime ≤ 1.23.2 (02§6.3); `transformers==5.19.0` ile torch 2.9.1 uyumu ve mediapipe'in cp310 wheel'i bu belgede doğrulanmadı | Kurulum kırılır | `kurulum.py` sürümleri sabitler ve kendi kendini sınar; ölçüm modülü eksikse ÖLÇÜLEMEDİ (sessiz geçiş yok); 4 GB GPU'da DINOv2-small/OWLv2-base (sığması tahmin), yoksa CPU |
| R9 | Kör gözlemin token ve süre maliyeti (≈ 2 milyon girdi tokeni/film, tahmin); Claude Code kullanım sınırı | Hat yarıda kalır | İş dosyaya yazılır, çıkış 2 ile kaldığı yerden devam; ≤ 12 görsel/çağrı; yerel ölçüm açık HATA'ları önceden eler |
| R10 | Yönetmenin ≈ 495 plan için tam durum yazması çok büyük iş; hata kaynağı olur | K0 gürültüsü, yazım yorgunluğu | `baslangic_durumu: "miras"` (önceki bitişten aynen) ve **yalnız değişen alanları** yazma (delta); defter tam durumu kendisi açar |
| R11 | Görsel üretici kroki geometrisine birebir uymaz | Geometri denetimi aşırı katı olur | Geometriden yalnız sol/sağ sırası ve "görünür öğeler" denetlenir; açı/derinlik ölçülmez |
| R12 | Aşırı katı kapılar çok aday reddeder | Zaman kaybı, Flow görsel yükü | Yanlış alarm hedefi ≤ %30; bedeli 0 kredi; kalibrasyonla gevşer (güvenlik dışı eşiklerde) |
| R13 | Ticari olmayan lisanslı araçların hatta sızması (InsightFace modelleri, pyiqa, DOVER, CoTracker; 02§0) | Kanal için hukuki risk | `kurulum.py` yalnız izinli listeyi kurar: OpenCV/opencv_zoo (Apache-2.0), MediaPipe (Apache-2.0), DINOv2 (Apache-2.0), OWLv2 (`transformers`, Apache-2.0), CLIP (MIT), PySceneDetect (BSD-3) |
| R14 | Kilitli kartın kullanıcı tarafından elle değişmesi | Seri içi tutarsızlık | Dosya özeti denetimi hattı durdurur, sürüm açtırır |

### 9.2 Diğer uzmanlarla çakışabilecek noktalar
| Uzman | Çakışma | Önerim |
|---|---|---|
| Yönetmen | Durum alanlarının yeri (`zanaat.baslangic_durumu` mı, `sureklilik.kadrajdakiler` mı); ZAN Z0#16 (bitiş ≡ başlangıç) ile K0'ın aynı işi yapması; mekân krokisi ve kamera konumlarını kimin yazdığı; 2 tur sonrası plan değişikliği | Tek kaynak: durum `zanaat` altında, kod tek yerde (`sureklilik_defteri.py`, Z0 onu çağırır). Kroki koordinatlarını `kart-tasarimcisi` yönetmenin parti haritasından `mekan.json`'a çevirir; plan başına kamera konumunu yönetmen seçer |
| İstem mühendisi | `gorsel_istem` artık kodla derleniyor; `istem-muhendisi.md`'deki CORRECTION modu `duzeltme.py`'ye geçiyor | Görsel istem şablonu ve sözlükler (el hâli, kadraj) ortak bakım; `hareket_istem` derlemesi onlarda |
| Animatik | Animatikte yalnız G1'li kareler; Z2 bitiş görselleri; K1-ön kare çiftleri; seyirci bulgularının yönlendirilmesi | Animatik aşaması G1'den sonra, zincir planından önce |
| Kurgu | Z1 karesini `kullanim`/kesme noktası belirler; V1/V3 çaresi olarak kırpma; K1 `plan_kurgu.py` sonrası; kurgu sonrası kesim değişirse Z1 karesi eski kesim noktasından alınmış olabilir | Kesim, Z1 kaynağının bitişini değiştiriyorsa `kare_zinciri.py` uyarır (zincirli planın yeniden çekimi gerekebilir). Kesim kararı kurgunun, uyarı benim |
| Ses | Replik penceresinde sessizlik (V1 B); dudak senkronu yolunda V2'nin yeniden çalışması; konuşmalı planlarda yüz görünürlüğü şartları; evrende `ses_ref` | §8.9; ses kararını onlar verir |
| Orkestratör (film.py) | Aşama sırası, ajan devri (çıkış 2 + `_AJAN_ISLERI/`), yeni sağlayıcı türü `gozlemci` | Protokol tek ve ortak olmalı; öteki aşamaların ajan devirleri de aynı biçimi kullanmalı |
| Hikâye odası | Kadro ayrışması kuralı (iki karakter makine için de ayırt edilebilir olmalı) hikâyeyle çakışabilir (ikizler, kılık değiştirme) | Bilinçli benzerlik `karakter.json` → `bilincli_benzerlik: ["id"]` ile işaretlenir; o çiftte fark payı yerine kostüm/aksesuar denetimi |
| Yayın | Kapak kartlardan üretilir; kapak adaylarında da kimlik tutmalı | Kapak adayları da kimlik ölçümünden geçebilir (`kare_denetim.py --serbest`) |

### 9.3 Açık sorular
1. **Görsel üretim sağlayıcısının varsayılanı:** Gemini ajanı paketi (0 kredi, kullanıcı ZIP taşır) mı, görsel API'si (ücretli, tam otomatik; repo kaynaklı fiyat yalnız Vertex Gemini 3 Pro Image ≈ 0,134 $/görsel, film başına ≈ 1.100–1.400 görsel) mı?
2. **"≤ 2 referans" kuralı** karakter sayısı mı, görsel sayısı mı? 2 karakter kartı + 1 mekân plakası Gemini'de yüz karışması yapar mı? Pilotta A/B denenmeli.
3. 1280×720 zincir karesi Flow'da başlangıç karesi olarak kaliteyi ne kadar düşürür? (ölçülmedi)
4. Flow Extend "son 24 kare" (02§2.2, doğrulanmadı) Z1'e alternatif olabilir mi, model değiştirme uyarısı getirir mi?
5. Kör gözlem Claude Code alt ajanıyla mı (abonelik) yoksa Claude API ile mi (`--tam-otomatik`) yapılacak? İkisi de sağlayıcı olarak tasarlandı; varsayılan?
6. `EVREN/` görselleri git'e (LFS) girecek mi, yoksa yalnız kullanıcının diskinde mi kalacak? Bulut oturumu kartları göremezse kart kapısı ve G1 yalnız yerelde koşar.
7. B3'ün etiketli 44 karesi (`D:\YZ_FILM_ARSIV`) kalibrasyon başlangıç seti olarak kullanılabilir mi?
8. Kart biçimi çelişkisi (BK§8 #19): açık gri fonlu birleşik sayfa önerildi, çünkü onaylı kartlar ve Gemini ajanı bu biçimle iyi sonuç verdi (B3'te 29 kart tek seferde). Yeşil fon (Seedance biçimi) ile ölçülü karşılaştırma yapılmadı.
9. Gemini ajanı çıktılarında görünür filigran olup olmadığı belgelerde yok. Kör gözlem `yazi_logo` alanında yakalar; çıkarsa kırpma politikası gerekir.
10. Görsel→video bekleme süresi ve günlük Flow görsel tavanı için kaynakta sayı yok. Varsayılanı kim, hangi kanıtla koyacak?
