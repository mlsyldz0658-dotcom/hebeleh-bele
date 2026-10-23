# FİLM ZANAATI SİSTEMİ
Hikâye odası, yönetmen ve kurgu ajanları için ortak kural kitabı. Hedef, filmi baştan planlı, ölçülebilir ve denetlenebilir yapmak.
Makinenin denetleyeceği eşikler: `ritim_esikleri.json` (bu belgedeki her sayı orada bir anahtarla durur; çelişki olursa JSON geçerlidir).

**Okuma sırası:** §0 kısıtlar → §1 duygu haritası (hikâye odası) → §2–3 süre ve plan dili (yönetmen) → §4 bilgi yönetimi (hikâye odası ve yönetmen) → §5 ses (kurgu) → §6 denetim (bütün kapılar) → §7 8/10 planı.

---

## 0. Değişmez kısıtlar (her öneri bunlara uyar)

| # | Kısıt | Zanaata etkisi |
|---|---|---|
| K1 | Her plan ayrı üretilen ≤ 8–10 sn klip, **başlangıç karesi görselinden** | Plan içi eylem 2–3 adımı geçmez; uzun hareket birden çok plana bölünür |
| K2 | Klipte **tek kişi konuşur**, replik ≤ 20 kelime | Diyalog = karşılıklı çekim + tepki planı; uzun konuşma bölünür |
| K3 | Karede ≤ 2 karakter referansı | Kalabalık = siluet, el, gölge, sırt; üçüncü kişinin yüzü yok |
| K4 | İki konuşan aynı karede olmaz | İkili plan yalnız sessiz anlar için; omuz üstü planda öndeki kişi sırtı dönük, ağzı görünmez, sessiz |
| K5 | Kurguda kırpma serbest (`kullanim {bas, sure}`) | 8 sn klipten 1,5–7 sn'lik plan çıkar; bir klipten 2 plan çıkabilir |
| K6 | Anlatıcı yok | Bilgi yalnız replik, görüntü, ekleme planı ve yer/zaman kartıyla verilir |
| K7 | Müzik ayrı katman; video isteminde `No music.` | Müzik kurguda yerleşir; klip sesi yalnız ortam ve efekttir |
| K8 | Film 3 parti; kredi harcayan iş en sonda | Ritim ve bilgi denetimi **kâğıt üstünde**, video üretilmeden önce yapılır |
| K9 | Filtre: kan, gore, ölü beden, küçük ve yaş sözcükleri yasak (`03_DERSLER.md`) | Şiddet tepkiyle, gölgeyle, sonrasıyla anlatılır |

**Kısıtı avantaja çeviren 3 araç** (en çok bunlar kullanılır):
1. **Ekran dışı replik:** A'nın sesi (TTS ayrı katman) sürerken B'nin sessiz tepki planı gösterilir. Kurala uyar, çünkü klipte görünen kimse konuşmuyor. Diyalogu "kopuk" olmaktan çıkaran ana araç budur.
2. **J/L kesme:** Sonraki planın sesi 0,3–0,8 sn önce başlar (J) ya da önceki planın sesi 0,3–0,8 sn taşar (L). Sesler ayrı katmanda olduğu için maliyeti yoktur.
3. **Klibi ikiye bölmek:** Konuşma klibi `0,5–3,8` ve `4,2–7,5` diye iki plana ayrılır, araya tepki planı girer. Daha çok plan elde edilir, kredi artmaz.

---

## 1. Duygu haritası

### 1.1 Tanımlar
- **yogunluk (1–10):** Seyircinin o dakikadaki duygusal kapılma derecesi. Tempo değildir: en karanlık an 7 olabilir ama yavaş kesilir.
- **duygu türü (sabit sözlük):** `merak`, `gerilim`, `korku`, `saskinlik`, `sefkat`, `mizah`, `huzun`, `umut`, `zafer`, `ofke`, `huzur`. Plan alanı `hedef_duygu` bu sözlükten seçilir. Geçiş `korku>sefkat` gibi yazılır.
- **Vuruş:** Hikâyenin yönünü değiştiren olay. Her vuruşta **bir şey kaybedilir ya da kazanılır** ve seyirci bunu ekranda görür.

### 1.2 Üç parti × vuruşlar (40 dk hedef; Save the Cat oranları 3 partiye uyarlandı)

| Parti | Süre | Perde karşılığı | Vuruşlar (dakika) | Parti sonu |
|---|---|---|---|---|
| **P1 KURULUŞ** | 0:00–13:00 | 1. perde + 2A başı | 0:00 soğuk açılış · 0:20 ilk kanca sorusu · 1:15 başlık kartı · 2:00 kahramanla bağ ("kediyi kurtar": bedeli olan küçük bir iyilik) · 3:00 dünya kuralı ve risk (sözlü) · 5:00 **tetikleyici olay** (%12) · 6–9 tereddüt, karşı güç görünür · 10:00 **1. perde dönüşü** (kahraman geri dönülmez seçim yapar, %25) | 12:30–13:00 **kanca 1**: yeni tehdit ya da sır, yoğunluk ≥ 8 |
| **P2 YÜZLEŞME** | 13:00–26:30 | 2A + 2B | 13:00 kancanın sonucu (ilk 20 sn içinde) · 14–19 "vaadin eğlencesi": tür neyi vaat ettiyse o (ejderhayla uçuş, kaçış, keşif) + B hikâyesi (bağ/ilişki) · 20:00 **orta nokta dönüşü** (%50; sahte zafer ya da sahte yenilgi, saat başlar) · 21–25 kötüler yaklaşır, ekip çatlar · 24:00 sessiz yakınlık anı (fırtına öncesi nefes) | 26:00–26:30 **kanca 2**: ihanet / kayıp / büyük sır, yoğunluk ≥ 9 |
| **P3 ÇÖZÜM** | 26:30–40:00 | 2B sonu + 3. perde | 27:00 kaybın yası · 29:30 **en karanlık an** (%75; her şey kaybedilmiş görünür) · 31:00 içgörü, 3. perde kararı (kurulan bir şey hatırlanır) · 32–35 doruğa yürüyüş, son plan kurulur ve bozulur · 36:00 **doruk** (%90, yoğunluk 10) · 37:00 bedel ve kazanç · 38:00 kapanış imgesi (açılış imgesinin aynası) | 38:40 **seri kancası** (jenerikten ÖNCE, ≤ 20 sn) → 39:00 jenerik ≤ 60 sn |

**Kural:** Süre 30–45 dk arasında değişirse vuruşlar **oranla** taşınır (ör. 30 dk filmde orta nokta 15:00). Oran sapması ±%4'ten fazlaysa denetim BAYRAK verir.

### 1.3 Dakika dakika hedef eğri (40 dk)

| dk | yoğ. | tür | | dk | yoğ. | tür | | dk | yoğ. | tür |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 8 | gerilim | | 13 | 8 | saskinlik | | 27 | 6 | huzun |
| 1 | 6 | merak | | 14 | 5 | merak | | 28 | 5 | huzun |
| 2 | 5 | sefkat | | 15 | 5 | mizah | | 29 | 7 | huzun (en karanlık) |
| 3 | 5 | merak | | 16 | 6 | merak | | 30 | 6 | huzun>umut |
| 4 | 6 | gerilim | | 17 | 6 | gerilim | | 31 | 6 | umut |
| 5 | 7 | saskinlik | | 18 | 5 | sefkat | | 32 | 6 | gerilim |
| 6 | 5 | korku | | 19 | 7 | gerilim | | 33 | 7 | gerilim |
| 7 | 6 | gerilim | | 20 | 8 | saskinlik (orta n.) | | 34 | 8 | korku |
| 8 | 5 | sefkat | | 21 | 6 | umut | | 35 | 9 | gerilim |
| 9 | 6 | merak | | 22 | 6 | gerilim | | 36 | 10 | zafer (doruk) |
| 10 | 7 | umut (1. perde d.) | | 23 | 7 | gerilim | | 37 | 8 | sefkat |
| 11 | 5 | mizah | | 24 | 5 | sefkat | | 38 | 5 | huzur |
| 12 | 7 | gerilim | | 25 | 7 | korku | | 39 | 7 | merak (seri kancası) |
| | | | | 26 | 9 | saskinlik (ihanet) | | | | |

**Eğri kuralları (makine denetler):**
1. Herhangi bir 3 dakikalık pencerede en az bir tepe ≥ 6 olur.
2. Yoğunluğun ±1 aralığında ve aynı türde kaldığı süre ≤ 180 sn ("düz çizgi yasağı").
3. Her büyük tepeden (≥ 8) önceki 60–120 sn içinde en az 2 puanlık bir **nefes çukuru** olur. Kontrast olmadan tepe hissedilmez.
4. Duygu türü her 2–3 dakikada değişir. Ardışık 3 dakika aynı tür olamaz.
5. Planların `yogunluk` değerleri zaman çizelgesine dizilince haritadan en çok ±2 sapar. Sapma 60 sn'den uzun sürerse BAYRAK.
6. Parti sonu ≥ 8, doruk ≥ 9, en karanlık an yoğunluğu ≥ 6 (hüzün düz ve sıkıcı olmamalı).

### 1.4 Seyircinin YouTube'da bıraktığı anlar ve önlemler

| Bırakma anı | Neden | Önlem (ölçülebilir) |
|---|---|---|
| **0–30 sn** (en büyük kayıp) | Vaat görülmedi; yavaş manzara; kim olduğu belli değil | İlk plan hareketli ve insanlı/yaratıklı; ilk 5 sn'de bir **eylem**, ilk 20 sn'de bir **soru** açılır; ilk 30 sn'de manzara planı ≤ 1 tane ve ≤ 3 sn; ilk 30 sn'de ASL ≤ 3,5 sn; başlık kartı 30 sn'den önce gelmez |
| **30 sn–2 dk** | Kapakta ve başlıkta verilen vaat (insan+yaratık bağı, ihanet) gecikti | Kapaktaki/başlıktaki ana imge **2:00'dan önce** ekranda görünür; kahraman adı 2:00'dan önce sözle söylenir; ilk 2 dk'da ASL ≤ 4 sn; başlık kartı 0:45–2:00 arasında, ≤ 6 sn |
| **Her ~90 sn** | Yeni bilgi yok, sahne kendini tekrar ediyor | Her ≤ 90 sn'de bir `merak_ac` ya da `merak_kapat` ya da vuruş; diyalog sahnesinde her ≤ 60 sn'de yeni bilgi; sahne ≤ 180 sn |
| **Orta bölüm çöküşü (%40–70)** | "Ortadaki sarkma": risk sabit kaldı | Orta noktada (20:00) saat başlar (süre sınırı ya da yaklaşan tehdit sözle konur); 21–26 arasında her 2 dk'da risk artar |
| **Parti geçişleri (13:00, 26:30)** | Bir şey "bitmiş" gibi hissedilir | Parti sonu cevapsız bir soruyla biter; sonraki parti ilk 20 sn'de o soruya döner; parti başında sakin kuruluş planı yasak |
| **YZ hatası anı** | Yüz değişimi, nesne zıplaması, kaybolan karakter | Süreklilik kapıları (G1/V2/K1, `arastirma/02_sureklilik.md` §6) + §3.7 bitiş/başlangıç durumu zinciri |
| **Ses zıplaması** | Replik seviyesi 9 dB oynar; ambiyans kesilir | §5: LUFS eşitleme, sahne içi tek ambiyans zemini |
| **Jenerik başı** | "Film bitti" | Seri kancası jenerikten önce; jenerik ≤ 60 sn; son 20 sn uç ekran (sonraki film) |

**YouTube bölüm (chapter) adları** merak cümlesi olur ("The Egg That Should Not Exist"), sahne betimi olmaz. Bölüm sınırları parti ve vuruş sınırlarına denk gelir; ≤ 8 bölüm.

---

## 2. Sahne ve plan süreleri

### 2.1 Plan tipine göre süre (kurguda kullanılan süre, `sure_sn`)

| `plan_tipi` | Aralık (sn) | Ortalama hedef | Not |
|---|---|---|---|
| `kurulus` (geniş mekân) | 2,5–4,0 | 3,5 | İlk kez görülen mekân ≤ 5; ilk 2 dk'da ≤ 3 |
| `diyalog` (konuşan görünür) | 2,5–8,0 | 6,2 | §2.3 formülüyle hesaplanır, keyfî değil |
| `tepki` (dinleyen; ses ekran dışından sürebilir) | 1,5–4,0 | 3,0 | Diyalog sahnesinde planların ≥ %25'i |
| `ekleme` (el, nesne, detay, makro) | 1,0–2,5 | 2,0 | Kurulum ve kullanım bilgisini taşır |
| `aksiyon` | 1,5–4,0 | 3,0 | Hızlı sahnede 1,5–2,5 |
| `eylem` (sessiz eylem zinciri: yürü, ara, aç) | 3,0–7,0 | 5,5 | Gerilim ve keşif |
| `duygu_tutma` (sessiz yakın, büyük an) | 4,0–8,0 | 7,0 | Film başına ≤ 25; ardışık 2 tane olmaz |
| `gecis` (manzara, zaman geçişi) | 2,0–3,0 | 2,5 | Kullanıcı notu "gereksiz uzun" → 3 sn tavan |
| `kart` (başlık, yer/zaman yazısı) | 2,5–6,0 | 3,0 | Yer/zaman kartı başka planın üstüne binebilir |

### 2.2 8–10 sn klip ne zaman, nasıl kırpılır
- **Baş:** Flow klibinin ilk 0,3–1,0 sn'si genellikle durağandır (başlangıç karesi). `kullanim.bas` varsayılanı **0,5 sn**. Kesme "eylem üstünde" olacaksa bas, ilk adımın başladığı ana kaydırılır.
- **Son:** Son 0,5–1,0 sn'de kayma, morf ve donma riski artar. 8 sn klipte **güvenli pencere 0,5–7,5 sn**.
- **Kırpma zorunlu:** (a) plan tipinin üst sınırı aşılıyorsa; (b) replik bittikten 0,6 sn sonra hâlâ yeni bilgi yoksa; (c) eylem zincirinin son adımı bittiyse ve bitiş durumu 0,5 sn tutulduysa; (d) V1/V2 kapısı klip içinde kusur bulduysa (kusurdan önceki parça kullanılır).
- **Klibi bölme:** Kullanılabilir süresi ≥ 6 sn olan konuşma ya da eylem klibi, arada bir tepki ya da ekleme planıyla iki plana bölünebilir. Bölünen parçalar arasında ≥ 0,4 sn atlanır, yoksa sıçrama hissedilir.
- **Temel kural:** "Geç gir, erken çık." Plan, eylemin ortasından girer ve sonuç görünür görünmez çıkar.

### 2.3 Diyalog planı hesabı
```
sure_sn = 0,4 (giriş) + kelime / 2,5 + 0,25 × (cümle sayısı − 1) + 0,5 (çıkış ya da tepki)
```
| Kelime | Cümle | sure_sn | Klip |
|---|---|---|---|
| 5 | 1 | 2,9 | 8 sn |
| 10 | 2 | 5,2 | 8 sn |
| 15 | 2 | 7,2 | 8 sn (sınırda) |
| 16 | 2 | 7,6 | 8 sn tavanı |
| 20 | 3 | 9,4 | **10 sn klip gerekir** |

- 8 sn klipte replik ≤ **16 kelime**, 10 sn klipte ≤ 20.
- Duygusal ağır replikte konuşma hızı 2,0 kelime/sn alınır (fısıltı, yas).
- Replik ≥ 12 kelimeyse cümlenin bir kısmı **ekran dışından** tepki planına taşınabilir (L kesme). Böylece konuşan plan kısalır.
- Konuşma sırasında en çok **1 fiziksel adım** olur. Konuşan ve aynı anda nesneyle uğraşan karakter Flow'da dudakları bozar.

### 2.4 Sahne süresi ve plan sayısı

| Sahne tipi | Süre (sn) | Plan sayısı | ASL (sn) | Kural |
|---|---|---|---|---|
| Soğuk açılış | 30–75 | 10–20 | ≤ 3,5 | Soru ≤ 20 sn |
| Diyalog / çatışma | 45–150 | 10–24 | 4,5–6,0 | ≤ 60 sn'de yeni bilgi; ≥ %25 tepki |
| Gerilim / keşif | 40–120 | 8–18 | 5,0–6,5 | Her 15–20 sn'de yeni ayrıntı (ses, gölge, nesne) |
| Aksiyon / kaçış | 30–90 | 12–30 | 2,5–3,5 | Ekran yönü sabit |
| Duygusal / yakınlık | 45–120 | 7–14 | 6,0–8,0 | En çok 2 `duygu_tutma` |
| Geçiş / montaj | 10–30 | 3–8 | 2,5–3,5 | Bilgi taşımayan geçiş ≤ 15 sn |
| Doruk | 90–180 | 25–45 | 3,0–4,0 | Kesme hızı tepeye doğru artar, zirvede bir uzun plan |

- Hiçbir sahne **180 sn**'yi aşmaz. Aşıyorsa ortasına bir vuruş konur ya da sahne bölünür.
- Film ≈ 45–55 sahne, sahne başına ortalama ≈ 10 plan.

### 2.5 Tempo kuralları
1. **ASL (ortalama plan süresi):** Film geneli 4,2–5,2 sn. P1 ≈ 4,7, P2 ≈ 5,0, P3 ≈ 4,4. İlk 2 dk ≤ 4,0.
2. **Kademe:** Duygu tepesine giden 30 sn'de ASL en az %25 düşer. Tepeden sonra bir uzun plan (≥ 5 sn) seyirciye nefes aldırır.
3. **Tekrar yasağı:** Aynı plan tipi art arda ≤ 4 kez (diyalog-tepki dönüşümü hariç). Aynı kamera konumu art arda 2 kez.
4. **Ölçek sıçraması:** Art arda iki plan aynı ölçekte ve aynı açıdaysa → HATA (atlamalı kesme). Fark ≥ 2 ölçek kademesi ya da ≥ 30° açı.
5. **Dolgu yasağı:** Süreye ulaşmak için plan uzatılmaz, manzara eklenmez. Hikâye 34 dakikada bitiyorsa film 34 dakikadır.

### 2.6 40 dk film için hedef plan sayısı ve dağılımı

| `plan_tipi` | Plan | Ort. sn | Toplam sn | Pay |
|---|---|---|---|---|
| diyalog | 190 | 6,2 | 1178 | %38 |
| tepki | 90 | 3,0 | 270 | %18 |
| eylem | 60 | 5,5 | 330 | %12 |
| aksiyon | 55 | 3,0 | 165 | %11 |
| ekleme | 45 | 2,0 | 90 | %9 |
| kurulus + gecis | 30 | 3,5 | 105 | %6 |
| duygu_tutma | 25 | 7,0 | 175 | %5 |
| **Planlar toplamı** | **495** | **4,67** | **2313 (38:33)** | |
| kart + seri kancası + jenerik | — | — | ≈ 90 | |
| **Film** | | | **≈ 40:00** | |

| Parti | Süre | Plan | ASL | Diyalog planı | Sahne |
|---|---|---|---|---|---|
| P1 | 0:00–13:00 | 165 | 4,7 | 65 | 16–18 |
| P2 | 13:00–26:30 | 160 | 5,0 | 68 | 15–17 |
| P3 | 26:30–40:00 | 170 | 4,4 | 57 | 15–18 |

**Klip ve kredi:** Klip bölme (§2.2) sayesinde ≈ %18 plan başka bir planın klibinden çıkar: **≈ 405 klip**. 720p Omni (12 kredi): ≈ 4.860 kredi + %20 yeniden deneme = **≈ 5.800 kredi**.
Bütçe yetmezse planlar uzatılmaz, **film kısaltılır**: 30 dk ≈ 370 plan ≈ 305 klip ≈ 4.400 kredi.
Toplam replik: ≈ 2.100–2.600 kelime (≈ 55–65 kelime/dk; anlatıcısız görsel film için uygun).

---

## 3. Plan dili

### 3.1 Ölçek sözlüğü (`kadraj` alanı)
`EG` çok geniş · `G` geniş (tam boy + mekân) · `OG` orta geniş (diz üstü) · `O` orta (bel) · `OY` orta yakın (göğüs) · `Y` yakın (yüz) · `CY` çok yakın (göz, ağız) · `D` detay/ekleme (el, nesne) · `OU` omuz üstü · `IK` ikili (iki kişi, sessiz an).
Kademe sırası: EG=1, G=2, OG=3, O=4, OY=5, Y=6, CY=7 (D ve OU kademe dışıdır; D her zaman "farklı" sayılır).

### 3.2 Kadraj sıralaması (sahne kalıpları)
| Kalıp | Sıra | Ne zaman |
|---|---|---|
| **Klasik giriş** | G (kuruluş) → O → OY/Y karşılıklı → D ekleme → Y tepki | Yeni mekân, yeni sahne |
| **Geç giriş** | D/Y (ayrıntı) → O → G (konum sonradan açılır) | Gerilim, gizem, soğuk açılış |
| **Yükselen diyalog** | OY↔OY → Y↔Y → CY (tek, en sert cümlede) | Çatışma tırmanırken ölçek daralır |
| **Açılan sonuç** | Y → G (kahraman yalnız, büyük mekânda) | Kayıp, yalnızlık, en karanlık an |
| **Yeniden konumlandırma** | Sahne > 90 sn ise ortada bir G/OG | Seyirci "kim nerede" bilgisini tazeler |

Her sahnenin ilk 3 planından biri **konum planı** olur (G, OG ya da IK). Kim nerede duruyor ve mekânın yönleri görünür. İstisna: "geç giriş" kalıbında konum planı en geç 5. plandadır.

### 3.3 Karşılıklı çekim ve 180° kuralı
- Her diyalog sahnesinde `eksen = [A, B]` tanımlanır. Kamera hep aynı taraftadır (`kamera_tarafi: "A"`).
- **A kadrajın sol üçte birinde, kadraj sağına bakar. B sağ üçte birde, kadraj soluna bakar.** Bu, görsel istemine açıkça yazılır: `"on the left third of frame, looking toward frame right"`.
- Eksen yalnız şu yollarla geçilir: (a) karakter kadraj içinde yürüyerek tarafını değiştirir (plan `eksen_gecis: true`); (b) eksenin tam üstünden nötr plan (karakter kameraya ya da kameradan uzağa yürür); (c) yeni sahne.
- Başlangıç görseli ters yöne bakıyorsa yatay ayna (`ayna`) uygulanır. Asimetrik ayrıntı (yara, tek eldiven, yazı, saç ayrımı) varsa ayna yasaktır, görsel yeniden üretilir.
- **Bakış çizgisi:** A'nın bakış yüksekliği B'nin göz hizasıyla eşleşir. Ayakta olan oturana bakıyorsa aşağı bakar, oturan yukarı bakar (`bakis: "kadraj_sagi_asagi"`).
- **Ekran yönü:** Yolculuk ve kovalamaca boyunca hareket hep aynı yönde olur (ör. `soldan_saga` = hedefe doğru). Geri dönüş ters yöndedir. Yön değişimi ekranda gösterilir (karakter döner).

### 3.4 Kesme noktaları (Murch'ün altı kuralı bu hatta)
Murch sıralaması: duygu %51 > hikâye %23 > ritim %10 > göz izi %7 > 2B düzlem %5 > 3B uzay %4. Sıralama aynı kalır; uygulaması şöyledir:

| `kesme.tip` | Kural | Ölçü |
|---|---|---|
| `eylem` (eylem üstünde) | Kesme, eylem zincirinin bir adımının ortasında olur (adımın %60–70'i); sonraki plan aynı adımın devamıyla başlar | Önceki planın `bitis_durumu` = sonrakinin `baslangic_durumu` |
| `replik_sonu` | Son kelimeden 0,2–0,5 sn sonra kesilir | Whisper bitiş zamanı + 0,2–0,5 |
| `L` | Konuşanın sesi sürer, görüntü dinleyene geçer | Taşma 0,3–2,5 sn |
| `J` | Sonraki planın sesi önce başlar | Öne alma 0,3–0,8 sn |
| `tepki` | Önemli cümleden sonra dinleyenin yüzü gösterilir | Cümle bitişi + 0–0,3 sn |
| `bakis` (göz izi) | Karakter bir şeye bakar → kesme → bakılan şey (ekleme) | Bakış en az 0,5 sn tutulur |
| `eslesme` | Şekil, hareket ya da ses benzerliğiyle sahne geçişi | Sahne geçişlerinin ≥ %15'i |
| `sert` | Şok için ses ve görüntü birlikte kesilir | Parti başına ≤ 4 |

**Göz izi:** Ardışık iki planda dikkat merkezi (konuşan yüz, hareket eden el) kadrajın aynı üçte birinde olur. Bilinçli istisna: karşılıklı çekimde iki yüz zıt üçte birlerdedir.
**Yasak:** Klibin ilk 0,3 sn'sinde kesme (durağan kare); hareket bitmişken bekleyerek kesme ("ölü süre" > 0,6 sn).

### 3.5 Tepki ve ekleme planları
- **Tepki planı** her önemli bilgiden sonra gelir. Seyirci duyguyu yüzden okur ("Kuleshov etkisi"). Diyalog sahnesinde planların ≥ %25'i tepkidir. Tepki klibinin hareket istemi: `"listens silently, mouth closed"` + tek mikro hareket (kaş, yutkunma, bakış kaçırma).
- **Ekleme planı** üç iş görür: (1) **kurulum** (nesneyi göster), (2) **kullanım** (nesnenin işe yaradığını göster), (3) **atlama köprüsü** (iki plan arası zaman ya da konum farkını gizler). Kurulumu olan her nesne en az bir kez ekleme planıyla gösterilir.
- Ekleme planı Flow'da en güvenli plan tipidir (tek el, tek nesne, makro). Riskli eylemler (kavrama, kilit açma) eklemeye bölünür.

### 3.6 8 sn klibe uygun hareket tipleri (`hareket_tipi`)
| Tip | Güvenilirlik | Kullanım |
|---|---|---|
| `sabit` + özne hareketi | yüksek | Diyalog, tepki, ekleme |
| `yavas_ileri` (push-in) | yüksek | Fark ediş, karar, gerilim |
| `yavas_geri` (pull-out) | yüksek | Yalnızlık, mekânı açma |
| `yavas_pan` / `tilt_acilis` | yüksek | Mekân, ölçek ifşası (yaratığın boyu) |
| `takip_yan` (yürüyüşe paralel) | orta | Yolculuk; ekran yönü korunur |
| `omuz_kamera` (hafif el kamerası) | orta | Kaçış, panik |
| `odak_kaydirma` | orta | Bilginin ön plandan arka plana geçmesi |
| `yörünge` (orbit) | düşük | Yüz kayması riski; yalnız doruk, yedek istemle |
| `hizli_hareket` (whip pan, crash zoom) | düşük | Kullanma; kurguda sert kesmeyle yapılır |

Kural: klip başına **tek kamera hareketi** olur. Kamera hareketi ve özne eylemi aynı yöne gider ya da biri durağandır.

### 3.7 Atomik eylem zinciri (KESİN KURAL)
YZ'ye sonuç söylenmez ("kalemi alır"); fiziksel adımlar sırayla, saniyeli yazılır.

**Yazım biçimi:**
1. `baslangic_durumu`: başlangıç karesiyle **birebir** aynı anlık görüntü. Konum (kadraj üçte biri), poz, bakış yönü, her nesnenin kimde ve hangi elde olduğu ve durumu (yanık, kapalı).
2. `eylem_zinciri`: **en çok 3 adım** (konuşmalı planda en çok 1). Her adım `[bas–bit sn] özne + tek fiil + yön/hedef + vücut parçası`. Adım ≥ 1,5 sn olur. Adımlar örtüşmez.
3. `bitis_durumu`: son adımdan sonraki anlık görüntü, baslangic_durumu ile aynı alanlarla. Son 0,5 sn'de bu durum **tutulur** ("holds still").
4. Sonraki planın `baslangic_durumu` = bu planın `bitis_durumu` (açı değişse de olgular aynı). Tek istisna `gecis_turu: yeni_sahne`.
5. Bir eylem 3 adıma sığmıyorsa plan bölünür; bağlantı `kesme.tip: eylem` ile yapılır.

**Yasak fiiller (sonuç fiilleri):** take, grab, pick up, get, use, fix, prepare, fight, search, open (açma biçimi yazılmadan). Bunların yerine fiziksel adımlar yazılır.

**Örnek: "Mara masadaki anahtarı alır" (2 plan)**
```
P041  kadraj: OG   hareket_tipi: sabit   sure_sn: 6.0   kesme: eylem@5.6
baslangic_durumu: Mara stands at the doorway, left third, facing frame right; lit lantern in her
                  right hand at hip height; left hand empty; iron key lies on the table, right third.
eylem_zinciri:
  [0.0–3.0] Mara takes two slow steps forward toward the table.
  [3.0–5.5] She stops at the table edge and extends her empty left arm toward the key.
bitis_durumu:     Mara at the table edge, left arm extended, fingers 10 cm above the key; lantern
                  still in right hand; eyes on the key.

P042  kadraj: D (makro)   hareket_tipi: yavas_ileri   sure_sn: 2.5   kesme: tepki
baslangic_durumu: (P041 bitis_durumu) Her left fingers 10 cm above the iron key on worn wood.
eylem_zinciri:
  [0.0–1.5] Her thumb and index finger lower onto the key and close around it.
  [1.5–2.5] She lifts the key 5 cm off the table and holds still.
bitis_durumu:     Key pinched between left thumb and index finger, 5 cm above the table.
```
**Derlenen hareket_istem (EN, Flow'a giden):**
`Static medium-wide shot. 0-3s: Mara takes two slow steps toward the table. 3-5.5s: she extends her empty left arm toward the iron key and stops, fingers just above it. She holds still. The lantern stays lit in her right hand. Sound: creaking floorboards, wind outside. No music.`

**Konuşmalı plan örneği (tek adım + replik):**
```
P087  kadraj: OY   sure_sn: 5.6 (12 kelime, 2 cümle)
baslangic_durumu: Bram seated left third, facing frame right, both hands around a clay cup.
eylem_zinciri:  [0.0–1.5] Bram lowers the cup onto the table with both hands.
replik (1.5–5.4): Bram says: "They will burn the whole street. And they will start with us."
bitis_durumu:   Cup on the table, Bram's hands flat beside it, eyes on Voss (off-screen, frame right).
```
