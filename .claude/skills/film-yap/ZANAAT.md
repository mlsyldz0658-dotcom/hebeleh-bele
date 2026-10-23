# FİLM ZANAATI SİSTEMİ
Hikâye odası, yönetmen ve kurgu ajanları için ortak kural kitabı. Hedef, filmi baştan planlı, ölçülebilir ve denetlenebilir yapmak.
Makinenin denetleyeceği eşikler: `ritim_esikleri.json` (bu belgedeki her sayı orada bir anahtarla durur; çelişki olursa JSON geçerlidir: sayıda `ritim_esikleri.json`, **şemada `semalar/plan_v2.json` (TASARIM §5.1)** geçerlidir).

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
| 1 | 6 | merak | | 14 | 5 | merak | | 28 | 5 | ofke |
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
3. Her büyük yerel tepeden (≥ 8; soğuk açılış hariç) önceki 60–120 sn içinde en az 2 puanlık bir **nefes çukuru** olur. Kontrast olmadan tepe hissedilmez.
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
Bütçe yetmezse **süre hikâye yazılmadan önce seçilir; yazılmış film kısaltılmaz** (planlar da uzatılmaz). 30 dk seçeneği: ≈ 370 plan ≈ 305 klip ≈ 4.400 kredi.
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
  [0.0–3.0] Mara walks two slow steps forward toward the table.
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
`Static medium-wide shot. 0-3s: Mara walks two slow steps toward the table. 3-5.5s: she extends her empty left arm toward the iron key and stops, fingers just above it. She holds still. The lantern stays lit in her right hand. Sound: creaking floorboards, wind outside. No music.`

**Konuşmalı plan örneği (tek adım + replik):**
```
P087  kadraj: OY   sure_sn: 7.0 (1,5 sn adım + 12 kelime, 2 cümle → 0,4+4,8+0,25+0,5 ≈ 5,95; adım konuşmadan önce)
baslangic_durumu: Bram seated left third, facing frame right, both hands around a clay cup.
eylem_zinciri:  [0.0–1.5] Bram lowers the cup onto the table with both hands.
replik (1.5–6.5): Bram says: "They will burn the whole street. And they will start with us."
bitis_durumu:   Cup on the table, Bram's hands flat beside it, eyes on Voss (off-screen, frame right).
```

---

## 4. Bilgi yönetimi
Anlatıcı yoktur. Seyircinin bildiği her şey ekranda görülen ya da duyulan bir plandan gelir. **"Amaç" alanı ekranda yoktur**; habersiz seyirci denetçisi yalnız görünen ve duyulan alanları okur.

### 4.1 Üç temel soru (her sahne)
| Soru | Nerede cevaplanır | Eşik |
|---|---|---|
| **Kim?** | Ad sözle söylenir (hitap ya da üçüncü kişi), yüz yakın planda görünür | Ana karakterin adı ilk göründüğü andan sonra ≤ 2 sahne içinde ve film başından ≤ 120 sn'de; yan karakter ilk replikten önce ya da hemen sonra |
| **Nerede?** | Konum planı (§3.2) ya da yer kartı ya da replik | Sahnenin ilk 3 planında; mekân değişince ≤ 10 sn'de |
| **Neyi riske atıyor?** | Replikle açıkça söylenir + bir görüntüyle (tehdit edilen kişi/nesne) | Film başından ≤ 180 sn'de; her parti başında ilk 60 sn'de tazelenir; her sahnenin `risk` alanı dolu |

Kural: Büyük sır ya da dünya kuralı **hem görüntüyle hem bir replikle** verilir (YAPIM_REHBERI §5).

### 4.2 Kurulum → kullanım tablosu (`KURULUMLAR` film alanı)
Her nesne, beceri, kural ya da ilişki kullanılmadan önce kurulur ("öteki yumurta" ve "kömür diski" hataları).

| id | Ne | Kurulum planı | Nasıl (görsel + sözlü) | Hatırlatma | Kullanım planı | Ödeme |
|---|---|---|---|---|---|---|
| `kur_anahtar` | Demir anahtar | P042 | D ekleme + "Only the warden has one." | P190 (ekleme) | P402 | Kapı açılır, kaçış |
| `kur_kural_ates` | Ateş yasak | P006 | Muhafız sobayı söndürür + replik | P150 (replik) | P330 | Ember'in alevi herkesi ele verir |

**Eşikler:**
- Kurulum, kullanımdan **en az 20 sn** önce gelir (aynı sahnede kurup kullanmak "kolaylık" gibi görünür).
- Kurulum ile kullanım arası **> 600 sn** ise arada en az bir hatırlatma planı olur.
- Doruktaki her çözüm (P3) **P1 ya da P2'de kurulmuş** bir şeyle gelir. Yeni beceri ya da yeni nesneyle çözüm = HATA ("deus ex machina").
- Kurulan her şey kullanılır ya da seri kancasına bağlanır (Çehov'un silahı). Kullanılmayan kurulum = BAYRAK.
- Plan alanları: `kurulum: ["kur_anahtar"]`, `kullanim: ["kur_anahtar"]`. Makine sırayı denetler.

### 4.3 Merak soruları defteri (`MERAK_DEFTERI` film alanı)
| id | Soru (seyircinin aklındaki) | Açan plan | Kapatan plan | Tür | Ömür |
|---|---|---|---|---|---|
| `m01` | Kar altındaki ışık ne? | P002 | P014 | kısa | ≤ 2 dk |
| `m02` | Bram yumurtayı neden saklıyor? | P020 | P210 | orta | ≤ 15 dk |
| `m03` | Lucan, Bram'ın kardeşi mi? | P120 | P330 | büyük | ≤ 1 parti |
| `m99` | Ember'in annesi yaşıyor mu? | P480 | (seri) | seri | sonraki film |

**Eşikler:**
- Her an **en az 1, en çok 5** açık soru bulunur. 6. soru açılmadan önce biri kapanır.
- Yeni soru ya da kapanış aralığı ≤ **90 sn** (§1.4).
- Kısa sorular ≤ 2 dk, orta sorular ≤ 15 dk, büyük sorular ≤ 1 parti içinde kapanır. Kapanmayan soru yalnız `seri` türünde kalabilir; film başına ≤ 2.
- **Cevap = yeni soru:** Büyük bir soru kapanırken aynı planda ya da ≤ 30 sn içinde yeni bir soru açılır.
- Her parti sonu (12:30–13:00, 26:00–26:30) açık bir soruyla biter (kanca).
- Plan alanları: `merak_ac: ["m02"]`, `merak_kapat: ["m01"]`.

### 4.4 Dramatik ironi
Seyirci karakterden **fazla** bilir. Bu, gerilim üretir (Hitchcock'un masa altındaki bombası). Anlatıcısız filmde en ucuz gerilim aracıdır.
- Kurulum: seyirci tehdidi bir planda görür (ör. Kestra kapının dışında dinliyor). Karakter görmez.
- Sürdürme: kurbanın sahnesine tehdidin 1–2 hatırlatma planı kesilir (tepki, ekleme, gölge).
- Çözülme: karakter öğrenir. Tepki planı zorunludur.
- **Eşik:** Parti başına en az 1 ironi zinciri (`ironi: {id, seyirci_bilir_plan, karakter_ogrenir_plan}`). Seyircinin bilip karakterin bilmediği süre 30–300 sn.

### 4.5 Bilgi verme yasakları
- "Bildiğin gibi" repliği yasak: karakterler ikisinin de bildiği şeyi birbirine anlatmaz. Bilgi taşıyan replikte **çatışma** olur (biri istemez, biri saklar, biri yanlış anlar).
- Aynı bilgi ikinci kez yalnız yeni bir anlamla verilir (hatırlatma ≠ tekrar). Aynı bilginin üçüncü kez verilmesi = BAYRAK.
- Bir sahnede ≤ 2 yeni ad. Film başına konuşan karakter ≤ 8.
- Geri dönüşler soluk ton ya da flaşla işaretlenir (`03_DERSLER.md`) ve ≤ 20 sn sürer.

---

## 5. Ses ve müzik ritmi

### 5.1 Katmanlar ve seviyeler
| Katman | Kaynak | Hedef seviye |
|---|---|---|
| Diyalog | TTS (AI84/ElevenLabs), whisper ile dudak anına oturtulur | fısıltı −24 · yumuşak −21,5 · normal −19,5 · bağırma −17 LUFS (replik başına) |
| Ambiyans (ortam zemini) | Sahne başına **tek sürekli** dosya; yatak yalnız gerçek kayıttan (CC0 banka) | Diyalogdan 12–18 dB aşağı |
| Efekt (adım, kapı, kanat) | Eylem zincirinin her adımına bir efekt | Diyalogdan 3–10 dB aşağı; şok anında diyalog seviyesine çıkabilir |
| Müzik | Ayrı katman (Gemini/Lyria), leitmotifli | Diyalog altında: diyalogdan ≥ 12 dB aşağı (otomatik kısma). Diyalogsuz bölümde −20…−16 LUFS |
| **Final karışım** | | Bütünleşik **−14 LUFS**, tepe ≤ −1 dBTP (YouTube ve Shorts) |

### 5.2 Ambiyans sürekliliği
- Ambiyans **plan değil sahne** katmanıdır. Sahne boyunca tek dosya, kesintisiz çalar. Planlar arası zıplama yasaktır (kapı sahnesi dersi).
- Sahne içinde ardışık planların ambiyans seviyesi farkı ≤ 3 LU.
- Sahne geçişinde ambiyanslar 0,5–1,0 sn çapraz geçer. Yeni sahnenin ambiyansı görüntüden 0,3–1,0 sn **önce** başlar (ses köprüsü, J kesme).
- İç mekândan dışarı bakan planda dış ses arttırılır, mekân ambiyansı değişmez.
- Yeniden çekilen her planda efekt yerleşimi yeniden yapılır (`03_DERSLER.md`).

### 5.3 Sessizliğin yeri
"Sessizlik" = müzik ve diyalog yok, **ambiyans var**. Mutlak sessizlik (< −50 dB) yalnız ≤ 1 sn, film başına ≤ 2 kez, en büyük şokta kullanılır.

| Yer | Süre | Neden |
|---|---|---|
| Büyük ifşadan hemen önce | 0,8–2 sn | Seyirci nefesini tutar |
| Şok repliğinden sonra (tepki planı) | 1–3 sn | Duygu yüzde okunur |
| En karanlık an | 10–40 sn müziksiz | Hüzün süslenmez |
| Doruktan hemen önce | 1–2 sn | Patlamadan önce çekilme |
| Soğuk açılışın ilk 3–5 sn'si | ambiyans + efekt | Müzik değil dünya duyulur |

### 5.4 Müzik giriş ve çıkış
- Müzik filmin **%40–65**'ini kaplar. Müziksiz bölüm en çok 4 dk, müzikli bölüm en çok 5 dk kesintisiz sürer.
- **Giriş** bir olayla olur: kesme, eylem başlangıcı, bakış, karar repliğinden sonra. Diyalog cümlesinin ortasında girmez. Giriş 1–3 sn yükselir; şokta ani girer.
- **Çıkış** ifşadan önceki sessizliğe ya da bir sahne sonuna denk gelir. Çıkış 2–4 sn sürer. Müzik bir sahne kesmesiyle birlikte bitmez; ses köprüsü olarak 1–2 sn taşar.
- Müzik ipucu duygu türü değişince değişir (§1.3). Ardışık iki ipucu aynı türde olamaz.
- **Leitmotif:** Her ana karakter ya da tema için sabit enstrüman + tempo (ör. Ember = tahta flüt, 70 BPM). Leitmotif ilk kez P1'de sade çalınır, doruğa kadar en az 3 kez döner, doruğunda tam orkestrayla çalar.
- Müzik istemlerinde sanatçı ve film adı yazılmaz. Video isteminde her zaman `No music.` yazılır.

### 5.5 Diyalog ritmi
- Karşılıklı konuşmada cevap boşluğu 0,2–0,6 sn. Çatışma büyüdükçe kısalır; şaşkınlıkta 1–2 sn'ye uzar ve tepki planı kullanılır.
- Bir karakter art arda iki plan boyunca konuşabilir (iki ayrı klip). Üçüncü plan bir tepki ya da cevap olur. Monolog > 3 plan = BAYRAK.
- Her diyalog sahnesinde planların ≥ %30'unda J ya da L kesme olur. Gerisi düz kesmedir. Bu, "kopuk" hissini azaltan ses aracıdır.

---

## 6. Ölçülebilir denetim listesi ve plan alanları

### 6.1 Önerilen plan alanları (SAHNELER.json; tümü isteğe bağlı, eski dosyalar çalışmaya devam eder)
> **Eski öneri; geçerli şema `semalar/plan_v2.json`** (TASARIM §5.1). Bu bölümün ilk sürümündeki alan tablosu kaldırıldı; aşağıdaki tablo o
> alanların v2'deki yerini ve yazanını gösterir (TASARIM §5.1 kural 8, "v1/ZN/AR2 → v2 eşleme"). Çelişkide şema geçerlidir.

Mevcut alanlar (`no`, `parti`, `referans`, `gorsel_istem`, `hareket_istem`, `amac`, `duygu`, `replik`, `kullanim`) değişmez. `hareket_istem` ve `gorsel_istem`, plan alanlarından **kodla derlenir**.

| ZN §6.1 / AR2 §6.1 alanı | v2'deki yeri | Yazan |
|---|---|---|
| `kadraj` | `zanaat.kamera.kadraj` | yönetmen |
| `sure_sn` | `_derlenir.sure_sn` (`kullanim.sure`'den) | kod |
| `kamera_tarafi` (`A`/`B`), `eksen_gecis` | sahne düzeyinde `sahne_gruplari.<S>.{eksen, kamera_tarafi}` (pusula yönü, harita); plan düzeyinde `_derlenir.kamera_tarafi` (`kroki.py`, kurulum konumundan); eksen geçişi kurulumun eksene göre yerinden | yönetmen (harita) / kod |
| `bakis` | durum nesnesinde `bakis.hedef` (olgu); kadraja düşüşü `_derlenir.bakis_kadrajda` | yönetmen / kod |
| `vurus`, `hedef_duygu`, `yogunluk`, `merak_ac/kapat`, `kurulum`, `kullanim_bilgi`, `ironi`, dramatik `risk` | `HIKAYE.json` (sahne ve olay düzeyi, R/olay kimliğiyle); `zaman_cizelgesi` T0'da plana `_derlenir.hikaye` olarak eşlenir | hikâye odası / kod |
| `ekranda_bilgi` | `zanaat.ekranda_bilgi` | yönetmen |
| `baslangic_durumu`, `bitis_durumu` | `zanaat.baslangic_durumu` (`miras` ya da olgu); `bitis_durumu` `derlenir` (dünya defteri) | yönetmen / kod |
| `eylem_zinciri` | `zanaat.eylem_zinciri` (D-13 adım şeması; konuşma bir adımdır) | yönetmen |
| `kesme`, `ekran_disi_ses` | `zanaat.kesme`, `zanaat.ekran_disi_ses` | yönetmen → kurgu |
| `replik_zaman` | `_derlenir.replik_zaman` | kod |
| `ses` | `zanaat.ses`, `sahne_gruplari.<S>.ses` | ses tasarımcısı |
| AR2 `sureklilik.{gecis_turu, onceki_plan}` | `zanaat.zincir` | yönetmen |
| AR2 `sureklilik.{kamera_konumu, plan_olcegi, kamera_acisi, kamera_hareketi}` | `zanaat.kamera.{kurulum, kadraj, aci, hareket_tipi}` | yönetmen |
| AR2 `sureklilik.{kadrajdakiler, nesneler, kadraj_sirasi}` | `zanaat.kadrajdakiler`, durum nesnesi (kural 6), `_derlenir.kadraj_sirasi` | yönetmen / kod |
| AR2 `sureklilik.{isik, isik_degisimi, yasaklar}` | `sahne_gruplari.<S>.isik`, `zanaat.yasaklar` | yönetmen |
| AR2 `sureklilik.{uretim, denetim}` | plan kökünde `uretim`, `denetim` | betikler, kapılar |

Tabloda olmayan eski alanlardan `sahne_grubu`, `plan_tipi`, `klip_sn` `zanaat` altında, `hareket_tipi` `zanaat.kamera` altında aynı adla durur; tam liste şemadadır.

**Sahne düzeyi alanlar** (`sahne_gruplari.<id>`): `sahne_tipi` (§2.4), `sahne_degeri {bas, son}` (§7.2), `risk`, `eksen`, `ambiyans`.

**Film düzeyi alanlar:** `duygu_haritasi` (dakika → `{yogunluk, tur}`), `vuruslar` (ad → dakika), `MERAK_DEFTERI`, `KURULUMLAR`, `IRONILER`, `eksenler` (sahne grubu → `[A, B]`), `leitmotifler`.

### 6.2 Denetim listesi (kapı → ölçü → eşik → sonuç)
Kodlar: **H** = HATA (geçmez, yeniden yazılır ya da üretilir), **B** = BAYRAK (ajan ya da insan bakar).

**Z0: Kâğıt üstü ritim kapısı** (`film.py`, SAHNELER.json üretildikten hemen sonra; kredi yok, ağ yok)
| # | Ölçü | Eşik | Sonuç |
|---|---|---|---|
| 1 | Toplam `sure_sn` + kart + jenerik | 1800–2700 sn | H |
| 2 | Parti süresi | 720–840 sn (40 dk film için); oranla | B |
| 3 | Vuruş zamanı / film süresi | §1.2 oranı ±%4 | B |
| 4 | Plan `sure_sn` / `plan_tipi` aralığı | §2.1 tablosu | H |
| 5 | Diyalog süresi ≥ §2.3 formülü; L/J taşması görünen süreden düşülür: `sure_sn ≥ formül − ses_tasma_sn` | eksikse | H |
| 6 | Replik kelime sayısı | ≤ 16 (8 sn) / ≤ 20 (10 sn) | H |
| 7 | ASL film / parti / ilk 120 sn / ilk 30 sn | 4,2–5,2 / §2.6 ±0,6 / ≤ 4,0 / ≤ 3,5 | B |
| 8 | Sahne süresi | ≤ 180 sn | H |
| 9 | Diyalog sahnesinde tepki planı oranı | ≥ %25 | B |
| 10 | Diyalog sahnesinde J/L kesme oranı | ≥ %30 | B |
| 11 | Aynı `plan_tipi` art arda | ≤ 4 | B |
| 12 | Ardışık planlarda ölçek farkı (aynı açı) | ≥ 2 kademe | H |
| 13 | `eylem_zinciri` adım sayısı / konuşmalı planda | ≤ 3 / ≤ 1 | H |
| 14 | Adım süresi; örtüşme | fiziksel adım ≥ 1,5 sn; `mikro` ve `ses_vurusu` adımı ≥ `eylem_adim_mikro_min_sn`; örtüşme yok | H |
| 15 | Yasak sonuç fiilleri `hareket_istem` içinde (§3.7) | 0 | H |
| 16 | `bitis_durumu`[N] ≡ `baslangic_durumu`[N+1] (nesne kimde/el, konum, poz) | `yeni_sahne` dışında eşit | H |
| 17 | 180°: aynı sahnede taraf değişimi eksen geçişi olmadan. Kamera tarafı yönetmen yazmaz; `kroki.py` kurulum konumundan `_derlenir.kamera_tarafi`'na hesaplar, denetim bu değerle yapılır | 0 | H |
| 18 | Karşılıklı planlarda bakışlar birbirine dönük | evet | H |
| 19 | `referans` sayısı; aynı karede konuşan sayısı | ≤ 2; ≤ 1 | H |
| 20 | Yasak kelimeler (filtre listesi, `03_DERSLER.md`) | 0 | H |

**Z1: Bilgi kapısı** (kâğıt üstü)
| # | Ölçü | Eşik | Sonuç |
|---|---|---|---|
| 21 | İlk eylem / ilk merak sorusu zamanı | ≤ 5 sn / ≤ 20 sn | H |
| 22 | Başlık kartı zamanı ve süresi | 45–120 sn, ≤ 6 sn | B |
| 23 | Ana karakter adının söylenmesi | ≤ 120 sn ve ilk görünüşten ≤ 2 sahne | H |
| 24 | Riskin sözle söylenmesi; parti başında tazelenmesi | ≤ 180 sn; parti başından ≤ 60 sn | H |
| 25 | Merak olayları arası en uzun boşluk | ≤ 90 sn | B |
| 26 | Aynı anda açık soru sayısı | 1–5 | B |
| 27 | Soru ömrü (kısa/orta/büyük) | ≤ 120 / 900 sn / 1 parti | B |
| 28 | Parti sonu açık soru | ≥ 1 | H |
| 29 | Kullanım öncesi kurulum; kurulum→kullanım arası | var; ≥ 20 sn | H |
| 30 | Kurulum→kullanım > 600 sn ise hatırlatma | var | B |
| 31 | Doruk çözümü P1/P2'de kurulmuş mu | evet | H |
| 32 | Kullanılmayan kurulum | 0 (seri hariç) | B |
| 33 | Parti başına ironi zinciri | ≥ 1 | B |
| 34 | Sahne başına yeni ad; konuşan karakter | ≤ 2; ≤ 8 | B |

**Z2: Duygu kapısı** (kâğıt üstü)
| # | Ölçü | Eşik | Sonuç |
|---|---|---|---|
| 35 | Plan yoğunluk dizisi ↔ `duygu_haritasi` | ±2; sapma ≤ 60 sn | B |
| 36 | 3 dk pencerede tepe | ≥ 6 | B |
| 37 | Düz çizgi (±1, aynı tür) | ≤ 180 sn | B |
| 38 | Tepe (≥ 8) öncesi çukur | 60–120 sn içinde ≥ 2 puan düşüş | B |
| 39 | Parti sonu / doruk / en karanlık an yoğunluğu | ≥ 8 / ≥ 9 / ≥ 6 | H |
| 40 | Müzik kaplama oranı; müziksiz ve müzikli en uzun blok | %40–65; ≤ 240 sn ve ≤ 300 sn | B |

**Z3: Kurgu kapısı** (kurgu taslağından, kredi yok; `plan_kurgu.py` sonrası)
| # | Ölçü | Eşik | Sonuç |
|---|---|---|---|
| 41 | `kullanim.bas` | ≥ 0,3 sn | B |
| 42 | `kullanim.bas + sure` | ≤ klip_sn − 0,5 | B |
| 43 | Replik sonrası ölü süre | ≤ 0,6 sn | B |
| 44 | Diyalog seviyeleri | hedef ±1 LU | H |
| 45 | Sahne içi ambiyans farkı; ambiyans boşluğu | ≤ 3 LU; 0 | H |
| 46 | Müzik diyalog altında | ≥ 12 dB aşağı | H |
| 47 | Final karışım; gerçek tepe | −14 ±1 LUFS; ≤ −1 dBTP | H |
| 48 | Süreklilik kapıları G1/V1/V2/K1 | `arastirma/02_sureklilik.md` §6.2 eşikleri | — |
| 49 | Kurgu izleme denetimi (habersiz seyirci, kare paketi) | §7.3 | H |

Her kapı `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json` yazar: `{kapi, sonuc, hatalar:[{madde, plan, olcu, esik, oneri}]}`. HATA varsa `YENIDEN_YAZ.json` (kâğıt) ya da `YENIDEN_URET.json` (görsel/video) kuyruğu çıkar.

---

## 7. Habersiz seyirci puanını 8/10'a çıkarmak

### 7.1 Teşhis: önceki 5–7/10 neden?
| Belirti (rapor, kullanıcı notu) | Kök neden | Bu belgedeki önlem |
|---|---|---|
| "Gereksiz uzun" | 8 sn klip olduğu gibi kullanıldı; manzara ve geçiş uzun; diyalog sahnesinde yeni bilgi yok | §2.1 süre tavanları, §2.2 kırpma, §2.5 dolgu yasağı, ASL 4,2–5,2, sahne ≤ 180 sn, 60 sn'de yeni bilgi |
| "Kopuk" | Karakter kaybolup belirdi; nesne zıpladı; ambiyans kesildi; replikler düz kesmeyle dizildi | §3.7 bitiş = başlangıç zinciri, §3.4 eylem üstünde kesme, §5.2 tek ambiyans, J/L ≥ %30, tepki ≥ %25 |
| "Bu kim, neden" (B1: babanın adı 84. çekimde) | Bilgi "amaç" alanında kaldı, ekrana çıkmadı | §4.1 ad ≤ 120 sn, risk ≤ 180 sn, `ekranda_bilgi` alanı |
| Kurulmadan kullanılan nesne | Kurulum listesi yoktu | §4.2 tablo + Z1 #29–32 |
| Merak düşük, "bir bölüm daha" isteği zayıf | Soru açılıp kapanma ritmi yoktu; parti sonları yumuşak | §4.3 defter, ≤ 90 sn kuralı, parti sonu ≥ 8 |
| Duygu "hak edilmemiş" | Bağ sahnesi kısa; tepki planı az; müzik her yerde | §1.2 bağ vuruşu 2:00, §3.5 tepki, §5.3 sessizlik, müzik ≤ %65 |

### 7.2 Somut önlemler (öncelik sırasıyla)
1. **Kâğıt üstü kapılar önce.** Z0–Z2 sıfır HATA ile geçmeden görsel üretimine geçilmez. Kopuklukların çoğu kâğıtta görülür ve kredisi yoktur.
2. **İlk 2 dakika ayrı cilalanır.** Soğuk açılış en az 2 versiyon (A/B) yazılır. Habersiz seyirci yalnız ilk 2 dakikayı okur ve "devam eder miydin? (evet/hayır + neden)" sorusunu cevaplar. 3 seyircinin 3'ü de "evet" demeden ilerlenmez.
3. **Her parti tek cümleyle savunulur.** "P2'de [kahraman] [hedef] için [engel]le karşılaşır ve [kayıp]la biter." Bu cümle yazılamıyorsa parti yeniden yapılandırılır.
4. **Sahne değeri kuralı.** Her sahne bir değeri tersine çevirir (güven → ihanet, güvende → tehlikede). `sahne_degeri: {bas, son}` aynıysa sahne ya kesilir ya başka sahneyle birleştirilir. Bu kural "gereksiz uzun" sorununu kökten çözer.
5. **Oyuncu denetimi.** Her konuşan karakter için bir ajan yalnız o karakterin repliklerini kendi kartına (bildiği, bilmediği, istediği, konuşma tarzı) göre okur. Ad, motivasyon ve "bildiğin gibi" hatalarını yakalar.
6. **Tepki ve ses köprüsü zorunluluğu.** Diyalog sahnelerinde tepki ≥ %25 ve J/L ≥ %30 değilse kurguya geçilmez.
7. **Atomik eylem zinciri + durum zinciri.** Bütün planların başlangıç ve bitiş durumu makineyle karşılaştırılır (Z0 #16). Flow'un "kendi kafasına göre" eylemi azalır, kesmeler eylem üstüne oturur.
8. **Kurgu izleme denetimi parti parti.** §7.3 yöntemi; KRİTİK kopukluk sıfırlanmadan sonraki partiye geçilmez.
9. **Kesme turu.** Kurgu bitince tek bir "kesici" ajan yalnız şu soruyu cevaplar: "Hangi 10 planı ya da 2 sahneyi atarsak film daha iyi olur?" Simülasyondan HATA'sız geçen önerilerin en az yarısı uygulanır. Her kesmeden sonra Z1 kurulum denetimi yeniden çalışır (kullanıcının kestiği planın bir bilgiyi de götürmesi dersi).
10. **Puanlar gürültülüdür, eğilim önemlidir.** Karar 3 seyircinin **medyanıyla** verilir. Tek seyircinin 9'u başarı sayılmaz.

### 7.3 Habersiz seyirci yöntemi (kâğıt ve kurgu, aynı ölçüt)
- **Girdi:** Yalnız ekranda olanlar: replikler (EN), görsel tarifi, yer/zaman kartları. Kurgu aşamasında bunlara izleme paketi eklenir ([KU2] §4.5.4): sayfa başına 6 plan × 3 kare (baş + 0,15 sn, orta, son − 0,15 sn; kırpılmış pencereden; animatikte plan başına 1 kare + eylem şeridi), her karede zaman kodu ve plan numarası, sayfanın üstünde önceki sayfanın son karesi; yanında `IZLE.md` işitsel dökümü (zaman kodu, plan no, süre, duyulan [konuşanın adı yok; ad sözle verilene kadar anonim etiket], efekt, müzik, sessizlik). `amac`, `risk`, `vurus`, `ekranda_bilgi`, önceki filmlerin özeti ve merak defteri **verilmez**.
- **3 bağımsız seyirci** (Opus, birbirini okumaz). Her biri 6 ölçütü 1–10 puanlar:

| Ölçüt | Soru | Hedef (medyan) |
|---|---|---|
| Anlaşılırlık | Her an kim, nerede, neyi riske atıyor biliyor muydum? | ≥ 8 |
| Akıcılık (kopukluk yok) | Bir plandan ötekine geçerken "nereden çıktı" dedim mi? | ≥ 8 |
| Merak | Sonrasını öğrenmek istedim mi? Parti sonunda durabilir miydim? | ≥ 8 |
| Duygu | Kahraman için endişelendim mi? Duygular hak edilmiş miydi? | ≥ 7 |
| Ritim | Sıkıldığım ya da hızlı geçtiğim an oldu mu (zaman koduyla)? | ≥ 7 |
| İlk 30 sn | İlk 30 sn'den sonra devam eder miydim? | ≥ 8 |

- **Ek çıktılar (makine karşılaştırır):**
  1. 3 cümlelik parti özeti + karakter adları + "kahraman neyi kaybedebilir?" cevabı. Hikâye odasının özetiyle anlamsal eşleşme ≥ %80 olmalı. Altındaysa bilgi ekrana çıkmamıştır.
  2. Kopukluk listesi: `{plan, tur: KRITIK/ORTA/KUCUK, neden, oneri}`. Eşik: parti başına KRİTİK = 0, ORTA ≤ 3.
  3. "Sıkıldığım anlar" zaman kodları. 2 seyircinin işaretlediği her an kesme turuna girer.
  4. Seyircinin aklındaki açık sorular. Merak defteriyle karşılaştırılır: defterde olup seyircide olmayan soru = ekranda açılmamış.
  5. Sonda tek satır: `OZET | anlasilirlik: 8 | akicilik: 7 | merak: 8 | duygu: 7 | ritim: 7 | ilk30: 9 | GENEL: 8`.
- **Geçme koşulu:** GENEL medyan ≥ 8, hiçbir ölçütün medyanı < 7, KRİTİK = 0, özet eşleşmesi ≥ %80.
- **Döngü:** Her tur aynı yazar (hikâye odası / yönetmen) düzeltir. Kâğıtta en çok 4 tur, kurguda en çok 3 tur. Eşiğe ulaşılmazsa kullanıcıya en düşük 3 ölçüt ve öneriler raporlanır. Her turda **yeni** seyirci ajanları kullanılır (önceki metni bilen seyirci habersiz değildir).

### 7.4 Ajan görev özeti
| Ajan | Bu belgeden sorumlu olduğu bölümler | Kapı |
|---|---|---|
| Hikâye odası | §1 duygu haritası ve vuruşlar, §4 bilgi yönetimi, `hedef_duygu`, `yogunluk`, `merak_*`, `kurulum`, `ironi`, `risk` | Z1, Z2 + kâğıt seyirci |
| Yönetmen | §2 süreler, §3 plan dili ve eylem zinciri, `plan_tipi`, `kadraj`, `kesme`, `*_durumu`, `eylem_zinciri` | Z0 + G1 |
| Müzik süpervizörü | §5, `ses` alanı, leitmotifler | Z2 #40 |
| Kurgu | §2.2 kırpma, §3.4 kesme, §5 karışım, kesme turu | Z3 + kurgu seyircisi |
