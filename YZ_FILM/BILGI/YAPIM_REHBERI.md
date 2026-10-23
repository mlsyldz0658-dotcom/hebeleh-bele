# YAPIM REHBERİ — Ajanlarla fikirden yayına YZ video üretimi

Bu rehber, EMBERFALL dizisini üretirken (Ekim 2026) gerçekten uyguladığımız süreci anlatır. İki okuru var:
- **Sistemi kullanan kişi:** Hangi aşamada ne olduğunu, nerede onay vereceğini bilsin.
- **Yeni bir Claude oturumu:** Bu süreci, kullanıcının KONUSUNA ve FORMATINA uyarlayarak yürütsün. Konu dizi, belgesel, çocuk masalı, Shorts ya da tanıtım filmi olabilir.

Önce `CLAUDE_ICIN.md`'yi (araçlar ve SAHNELER.json şeması), sonra bu rehberi oku. EMBERFALL'ın gerçek dosyaları `BILGI\ORNEK_EMBERFALL\` klasöründe örnek olarak duruyor.

---

## 1. Temel fikir: neden ajanlar?

Tek bir zihin (tek Claude) hikâyeyi yazarken kendi hatalarını göremez. Bu yüzden bir **film ekibi** kurulur:
- **Yönetmen (ana Claude oturumu):** Kullanıcıyla konuşur, ajanlara iş verir, sonuçları birleştirir, son kararı verir. Kendisi puan vermez; tarafsız kalır.
- **Yaratıcı ajanlar:** Fikir üretirler (mimarlar, senarist).
- **Eleştirmen ajanlar:** Bağımsız denetlerler (jüri ve denetçiler).
- **Uygulayıcı ajanlar:** Fikirleri üretim diline çevirirler (istem mühendisi, müzik süpervizörü).

**Altın kurallar:**
1. **Bağımsızlık:** Aynı işi yapan ajanlar birbirinin çıktısını OKUMAZ (talimatta açıkça yazılır). Böylece gerçekten farklı fikirler ve gerçekten bağımsız puanlar çıkar.
2. **Ortak ölçüt:** Bütün jüri aynı puan tablosunu kullanır, her puanı gerekçelendirir ve sona makinenin okuyacağı tek satırlık bir ÖZET yazar.
3. **Her şey dosyaya:** Ajan çıktıları, kararlar ve durum dosyalara yazılır. Sohbet dolar ya da kullanım sınırı gelir; dosyalar kalır. (EMBERFALL'da sınır doldu, ajanlar yarıda kesildi, ama dosyalarını yazmışlardı ve iş kaybolmadı.)
4. **Revizyonu aynı yazar yapar:** Denetim sonuçlarını yeni bir ajana değil, metni yazan ajana geri gönder (SendMessage). Metni bildiği için daha tutarlı düzeltir.
5. **Model seçimi:**
   | Model | İşler |
   |---|---|
   | **Opus** | Yaratıcılık ve yargı: mimar, senarist, seyirci, duygu ve ritim |
   | **Sonnet** | Titiz ve uzun kontrol: süreklilik, üretilebilirlik, istem mühendisi, müzik, YouTube stratejisi |
   | **Basit betik** | Mekanik kontrol: JSON şeması, kelime sayısı, referans dosyası var mı? Bu iş için ajana bile gerek yok |
6. **Kullanıcının onay noktaları az ve net:** EMBERFALL'da yalnızca karakter görünüşleri, sesler ve CapCut kurgusu onaylatıldı. Gerisine ekip karar verdi; kullanıcı "sana güveniyorum" dedi. Her projede bu noktaları baştan kullanıcıyla belirle.

---

## 2. Aşamalar

| # | Aşama | Kim | Çıktı | Kullanıcı |
|---|---|---|---|---|
| A0 | Proje kararları | Yönetmen + kullanıcı (sohbet) | `BILGI\<PROJE>_KARARLARI.md` | Tartışır, onaylar |
| A1 | Ortak brifing | Yönetmen | `_HIKAYE_ODASI\00_BRIFING.md` | — |
| A2 | Hikâye odası | 3-4 mimar (Opus, paralel) | `oneri_A..D.md` | — |
| A3 | Jüri | 5 bağımsız jüri (paralel) | `juri_1..5.md` | — |
| A4 | Birleştirme | Birleştirme yazarı (Opus) | `oneri_FINAL.md` | — |
| A5 | Denetim turu | 3 denetçi → aynı yazar v2 | `denetim_*.md`, `oneri_FINAL_v2.md` | Brifingi okur |
| A6 | Görsel geliştirme | Yönetmen (+ Gemini/ChatGPT) | `KONSEPT\`, `01_KARAKTERLER\` | **Karakterleri onaylar** |
| A7 | Ses seçimi | Yönetmen (AI84 adayları) | Kararlar dosyasına voice_id'ler | **Sesleri seçer** |
| A8 | Bölüm çekim listesi | Senarist → 3 denetçi → senarist v2 | `_BOLUM1\B1_cekim_listesi_v2.md` | — |
| A9 | Üretim dosyası | İstem mühendisi + müzik süpervizörü + betik kontrol | `SAHNELER.json` | — |
| A10 | Üretim | Memmet → Veo/Lyria → seslendirme → CapCut | `SIRALI_*`, CapCut projesi | Başlatır, bekler |
| A11 | Kurgu döngüsü | Kullanıcı notları → yönetmen düzeltir | `KURGU\NOTLARIM.txt` | **CapCut'ta izler, not yazar** |
| A12 | Yayın | Yönetmen (+ YouTube paketi) | Kapak, başlık, açıklama, altyazı | Yükler |

### A0 — Proje kararları (en önemli adım)
Kullanıcıyla sohbet ederek şunları netleştir ve dosyaya yaz:
- **Format:** Tek film / dizi / Shorts; süre; bölüm yapısı (sert açılış ve cliffhanger gibi)
- **Anlatım:** Anlatıcılı mı, diyaloglu mu?
- **Ton:** Duygu yelpazesi
- **Kullanıcının imzası:** EMBERFALL'da "yavru yaratıklar aşırı şirin, yetişkinler heybetli" idi
- **Netlik kuralı:** EMBERFALL'da "bağlamlar güçlü olmalı; seyirci her an kim, nerede, neyi riske atıyor bilmeli; gereksiz uzatma yok"
- **Bütçe ve araçlar:** Flow kredisi, Google Cloud, ses servisi
- **Onay noktaları**
- **Kullanıcının bilmediği kavramlar:** Cold open, cliffhanger, leitmotif gibi; kibarca açıkla

**Eksikleri "yüzüne vur":** Kullanıcının atladığı şeyleri açıkça söyle. EMBERFALL'da örneğin: bütün sezon belli değildi, dünya ve dönem tanımsızdı, yaratık büyüme aşamaları, anlatıcısız formatta bilgiyi kimin vereceği, sabit 8 saniyelik klip ritmi.

### A1 — Ortak brifing
Bütün mimarlara AYNI belge verilir. İçinde şunlar olur:
- (1) Kanal ve izleyici, **araştırma verisi** (hangi kalıplar tutuyor, sayılarla)
- (2) Kullanıcının kesin istekleri
- (3) **ÜRETİM SINIRLARI:** Bunlara uymayan fikir çekilemez; mimar baştan bilmeli. Bkz. bölüm 5.
- (4) Teslim belgesinin başlıkları

Örnek: `ORNEK_EMBERFALL\00_BRIFING.md`.

### A2 — Hikâye odası
3 ya da 4 mimar aynı brifingle, **farklı tonlarda** ve paralel çalışır. EMBERFALL'da tonlar dram ve hüzün, macera ve aksiyon, gizem ve sırlar ile **bonus "beni şaşırt"** idi. Bonus ajana ton verilmez; en özgün fikir genelde ondan çıkar.

Konuya göre ton örnekleri:
| Konu | Tonlar |
|---|---|
| Belgesel | Merak ve keşif / dram ve insan hikâyesi / gizem ve dedektiflik / bonus |
| Çocuk masalı | Komik / dokunaklı / macera / bonus |
| Tanıtım filmi | Duygusal / esprili / epik / bonus |

### A3 — Jüri
5 bağımsız rol aynı puan tablosuyla çalışır (örnek: `ORNEK_EMBERFALL\00_JURI_TABLOSU.md`; 10 ölçüt × 1-10 puan, gerekçe şart, en sonda `OZET | A: .. | B: .. | SIRALAMA: ..` satırı).

| Jüri üyesi | Model | Neye bakar |
|---|---|---|
| İlk kez izleyen seyirci | Opus | Merak, anlaşılırlık, "bir bölüm daha" isteği |
| YouTube stratejisti | Sonnet | Araştırma verisine dayanarak tıklanma ve kanca |
| Tür uzmanı | Opus | Özgünlük, klişe; tür ölçütleri (ör. yaratık tasarımı) |
| Duygu ve karakter eleştirmeni | Opus | Bağlanılırlık, duyguların hak edilip edilmediği |
| **Üretilebilirlik denetçisi** | Sonnet | Kâğıtta iyi ama çekilemez fikri yakalar; referans sayısı, kredi |

Konuya göre "tür uzmanını" değiştir: belgeselde konu uzmanı ve doğruluk denetçisi, çocuk masalında çocuk gelişimi ve pedagoji, reklamda marka ve satış.

Puanları topla. EMBERFALL'da iki öneri berabere kaldı (420/420) ve jüri "birleştirin" dedi.

### A4 — Birleştirme
Bir yazar ajan bütün önerileri ve bütün jüri raporlarını okur; kazanan(lar)ı **organik olarak** birleştirir (yamalı bohça olmamalı). Jürilerin "çalınmaya değer" ve "mutlaka düzelt" maddelerini uygular. Belgenin başına iki bölüm ekler: **birleştirme kararları** ve **kullanıcıya 1 sayfalık sade brifing**.

### A5 — Denetim turu
Birleşik metni **önceki puanları bilmeyen**, sıfırdan okuyan 3 denetçi inceler: seyirci, duygu, üretim. Raporları aynı birleştirme yazarına gönderilir; v2'nin başına "v2 değişiklikleri" tablosu yazılır.

EMBERFALL'dan iki ders:
- Üretim denetçisi aşırı temkinli olabilir. Pilot testlerindeki **kanıtla** düzelt: "insan + yaratık iki referansla sorunsuz çıktı".
- Kredi sınırını bu aşamada sabitle.

### A6 — Görsel geliştirme
1. **Konsept görseller** (3-4 ana kare, Google Cloud Gemini): Kullanıcı dünyayı gözünde canlandırsın.
2. **Karakter referans adayları:** Her karakter için 3 aday. Biçim: düz açık gri fon, aynı karakter iki kez (önden ve 3/4), tam boy.
3. **Ders (önemli):** Gemini yaratıkları çizgi film ve peluş gibi çizdi. İstemlere şunlar eklenince gerçekçi oldu:
   - "real animal photography, nature documentary, Weta Workshop practical creature, NOT cartoon, NOT Pixar, NOT plush"
   - İnsanlar için: "real costume test photo on ARRI Alexa"

   Kullanıcı ChatGPT ile çizdirmeyi seçti; istemler `KARAKTER_ADAYLARI\CHATGPT_ISTEMLERI.txt` biçiminde verilir.
4. **Varyant referanslar:** Onaylı referanstan Gemini'ye **referans görsel vererek** üretilir. Örnekler: atkısız yavru (atkı hikâyede sonra geliyordu), zincirli anne, sezon ilerleyince büyümüş yaratık, kostüm 2. Böylece aynı karakter kalır.
5. **Kullanıcı onayı.**

### A7 — Ses seçimi
AI84 ortak ses kütüphanesinde (`ai84.voices(...)`) karakter tarifine göre ara. Her karakter için 2 aday bul, **karakterin kendi repliğiyle** okut, kullanıcıya gönder, seçimi kararlar dosyasına voice_id ile yaz. Anlatıcı varsa (prolog ya da belgesel sesi) onu da aynı yöntemle seç.

### A8 — Bölüm çekim listesi
1. **Çekim listesi biçimi:** Yönetmen ortak bir biçim dosyası yazar (`ORNEK_EMBERFALL\00_CEKIM_LISTESI_BICIMI.md`). Her çekimde şu alanlar olur: motor, kullanım saniyesi, mekân, ışık, referanslar, kostüm, kamera, görsel (EN), hareket (EN), replik + TR, anlatıcı, ekran yazısı, duygu, amaç, müzik ipucu, süreklilik notu.
2. **Senarist (Opus):** Bölümü çekim çekim yazar.
3. **3 denetçi (paralel):**
   - **Duygu ve ritim editörü (Opus):** Süreler, tempo, replikler, müzik.
   - **İlk kez izleyen seyirci (Opus):** **Sezon belgesini OKUMAZ**; yalnızca ekranda görünen ve duyulan alanları okur (görsel, hareket, replik, anlatıcı, ekran yazısı). "Amaç" alanı ekranda yoktur. Bu sayede "bilgi sadece kâğıtta kalmış" hatası yakalanır. EMBERFALL'da babanın adı ancak 84. çekimde geçiyordu; bu yöntemle bulundu.
   - **Süreklilik ve kural denetçisi (Sonnet):** Kostüm, eşya, ışık, referans dosyası eşleşmesi, dünya kuralları, kural ihlalleri.
4. **Senarist v2:** Bütün maddeleri uygular, gerekçesiz madde bırakmaz.

### A9 — Üretim dosyası
- **İstem mühendisi (Sonnet):** Çekim listesini `SAHNELER.json`'a çevirir. Yaptıkları:
  - Görsel istemi: kamera, karakter adı ve 2-4 görsel çapası, mekân, kısa stil ön eki
  - Hareket istemi: tek hareket, `Sound: ...`, replik biçimi `X says: "..."`
  - Her sahne için yedek istemler
  - Parti bölümü: 20'şer çekim, blok sınırından
  - Kırpma: `kullanim{bas,sure}`
  - Bitince kendi Python kontrolünü çalıştırır
- **Müzik süpervizörü (Sonnet):**
  - Ipuçlarından Lyria istemlerini yazar.
  - **Leitmotif** kurar: her karakter ya da tema için tutarlı enstrüman ve tempo.
  - Sessizliğin müzikten güçlü olduğu yerleri işaretler.
  - Sanatçı ve film adı kullanmaz.
  - Çıktı: `muzik_listesi.json`
- **Yönetmen:** Müzik parçalarını sahnelere bağlar (çekim aralıklarından) ve **mekanik doğrulama betiğini** çalıştırır. Kontrol edilenler:
  - Referans dosyaları var mı?
  - Konuşan herkesin sesi atanmış mı?
  - Replikler ≤20 kelime mi?
  - Kırpma geçerli mi?
  - Kare başına ≤2 referans mı?

### A10 — Üretim
`MEMMET_BASLAT.bat` zinciri: Memmet (Flow görsel + video) → google_uret veo → google_uret muzik → seslendir → capcut_film. Telegram bildirim gönderir.
- **İlk 4 görseli** ve sonra **referans kontrol sayfasını** (her küçük resmin üstünde beklenen karakter yazılı) gözle kontrol et.
- Memmet başka bir sanal masaüstündeyken de çalışır; Chrome yavaşlatmasın diye özel bayraklarla açılır.

### A11 — Kurgu döngüsü
Kullanıcı CapCut'ta izler. Sarı NOTLAR kanalında her sahnenin amacı ve duygusu yazar. Beğenmediği yere yazı ekleyip not bırakır. Sonra:
`notlari_oku.py` → notlar sahne numarasıyla listelenir → yönetmen düzeltir:
- İstem ya da replik değiştir
- `SIRALI_*\NNN` dosyasını sil, Memmet'i tekrar çalıştır
- Ya da `DUZELT.txt` komutları

Ardından CapCut projesi yeniden oluşturulur.

### A12 — Yayın (seyirciye çıkış)
Şimdilik ELLE yapılıyor. Kontrol listesi:
1. CapCut'ta **NOTLAR kanalını sil** → dışa aktar (1080p, ya da Shorts için 1080x1920).
2. **Kapak:** Araştırmadaki kazanan kalıp (fotogerçekçi sinema karesi, insan ve yaratık aynı karede, film afişi gibi logo, kalabalık yazı yok). Gemini ile 3-4 aday üret, kullanıcı seçsin.
3. **Başlık:** `[duygusal kanca cümlesi] | SERİ ADI | Episode N` (ya da Full Movie 4K 2026).
4. **Açıklama:** 2-3 cümlelik kanca, bölüm zaman damgaları, seri oynatma listesi bağlantısı, YZ ile üretildiği notu (izleyici bunu kabul ediyor, saklamaya gerek yok).
5. **Altyazı:** `KURGU\altyazi_en.srt` YouTube'a yüklenir.
6. **Uç ekran** (sonraki bölüm) ve **sabit yorum** ("Part 2'de ne olsun?").
7. **Oynatma listesi** (dizi ise).

---

## 3. Konuya ve formata uyarlama

Altyapı (Memmet, KONTROL, seslendirme, CapCut) aynı kalır. Değişen şey brifing, ajanların tonları ve rolleri ve SAHNELER alanları.

| Format | Brifingte değişen | Ajanlarda değişen | SAHNELER / üretimde değişen |
|---|---|---|---|
| **Dizi / film** (EMBERFALL) | Sezon yapısı, sert açılış, cliffhanger, karakter yayları | Bu rehberdeki gibi | Replikler (tek konuşan), kısa prolog anlatıcısı, yer ve zaman kartları |
| **Anlatıcılı belgesel / hikâye** | Doğruluk, kaynak, anlatı akışı | Tür uzmanı yerine konu uzmanı ve **doğruluk denetçisi**; senarist anlatı metnini cümle cümle görüntüye bağlar | Her sahnede `anlatici` alanı; replik az ya da hiç; görüntüler anlatıyı birebir göstermeli |
| **Çocuk masalı** | Yaş grubu, mesaj, korkutucu öğe sınırı | Tür uzmanı yerine çocuk gelişimi ve pedagoji uzmanı | Yumuşak ışık, kısa sahneler, sıcak anlatıcı sesi, kan ve şiddet kesinlikle yok |
| **Shorts (dikey)** | 30-60 sn, ilk 2 sn kanca, döngü sonu | Ritim editörü çok kısa kesmeler ister | `"en_boy": "9:16"` (Memmet ve CapCut destekler), 10-20 çekim, sinema bandı yok |
| **Tanıtım / reklam** | Marka, ürün, harekete geçirici çağrı | Tür uzmanı yerine marka ve satış uzmanı | Ürün görselleri referans olarak verilir, son karede logo |

**Bu sistemin zayıf olduğu işler** (kullanıcıya dürüstçe söyle):
- Gerçek kişinin konuştuğu avatar videoları
- Gerçek görüntü (stok video) kurguları
- Ritme senkron müzik klipleri
- Ekran kaydı ya da eğitim videoları

---

## 4. Ajan talimat şablonları
`{...}` alanlarını konuya göre doldur. EMBERFALL'daki tam hâlleri `ORNEK_EMBERFALL\` belgelerinin üretildiği talimatlarla aynı yapıda.

**Mimar:**
> Sen bir {dizi yaratıcısı / belgesel yazarı / masal yazarı}sın. Önce `{BRIFING}` dosyasını oku; kullanıcı istekleri ve ÜRETİM SINIRLARI kesindir. SENİN TONUN: {ton tarifi}. Brifingin teslim başlıklarının hepsini yaz (Türkçe; görsel tarifler ve diyaloglar İngilizce). Belgeyi `{DOSYA}` dosyasına kaydet. Klasördeki diğer önerileri OKUMA. Bana 5 satırlık özet dön.

**Bonus mimar:**
> ...SENİN TONUN: serbest, "beni şaşırt". Diğer ekipler klasik yollara gidecek; sen beklenmedik bir açı bul. Ama kesin istekler ve üretim sınırları geçerli: sürpriz, çekilemez ya da anlaşılmaz olmamalı.

**Jüri üyesi:**
> Rolün: {rol}. {Rolün bakış açısı}. Brifingi ve puan tablosunu oku, sonra bütün önerileri oku. Başka jüri dosyalarını OKUMA. Tablodaki biçimle değerlendir. Her puan gerekçeli olsun, sona OZET satırını koy. `{DOSYA}` dosyasına kaydet. 4 satır dön: sıralama, en güçlü parça, en büyük risk.

**Birleştirme yazarı:**
> Önerileri ve jüri raporlarını oku. Kazananları organik olarak birleştir; jürilerin "çalınmaya değer" ve "mutlaka düzelt" maddelerini uygula. Başa iki bölüm ekle: BİRLEŞTİRME KARARLARI ve KULLANICIYA 1 SAYFALIK BRİFİNG. Sonra revizyon için: "denetim raporlarındaki bütün zorunlu maddeleri uygula, başa v2 DEĞİŞİKLİKLERİ tablosunu koy, uygulamadığın maddenin gerekçesini yaz".

**Senarist:**
> Çekim listesi biçimini ve sezon belgesini oku. Bölümü çekim çekim yaz; her alan dolu olsun. Kurallar: {çekim sayısı ve kredi sınırı}, sert açılış ilk 60 sn'de, {format kuralları}. Başa özet tablo koy. 5 satır dön: sayılar, açılış, kapanış, bilinçli sapmalar, emin olmadığın noktalar.

**Seyirci denetçisi (çekim listesi):**
> Bu dünyayı HİÇ bilmiyorsun. Sezon belgesini OKUMA. Yalnız ekranda görülen ve duyulan alanlara göre kafanda filmi kur. "Bu kim, neredeyiz, neden" dediğin her çekimi yaz. Her madde için somut düzeltme öner (ör. "Ç034'e şu repliği ekle").

**Süreklilik denetçisi:**
> Kural ihlallerini (kare başına referans, tek konuşan, kelime sınırı, kan, bir klipte iki görüntü), sürekliliği (kostüm, eşya, ışık, varyant referans geçişleri) ve dünya kurallarını (NE YOK listesi, renk kuralı) çekim çekim kontrol et. Hepsini tablo hâlinde yaz.

**İstem mühendisi ve müzik süpervizörü:** `ORNEK_EMBERFALL\SAHNELER.json` ile `muzik_plani.md` çıktı örneğidir. Şema `CLAUDE_ICIN.md`'de.

---

## 5. Üretim sınırları ve öğrenilen dersler (her brifinge girer)

- **Karakter ve konuşma:**
  - Bir karede en fazla 2 adlı karakter (yaratık dahil). Üçüncü kişi el, gölge ya da siluet olarak görünür ve referansı verilmez.
  - Referans YALNIZCA kadrajda görünen karaktere verilir. 3 referans birden verilince Flow yüzleri karıştırır.
  - Her klipte tek konuşan; replik ≤20 kelime (8 sn).
- **Klip ve kadraj:**
  - Bir 8 saniyelik klipte tek bir görüntü olur; iki görüntü gerekiyorsa çekim ikiye bölünür.
  - Video **görselden** (Kareler modu) üretilir. Görselsiz "İçerik öğeleri" modu karakteri kaydırır.
  - Art arda benzeyen çekimler farklılaştırılır (geniş/yakın, önden/arkadan); hem eşleştirme belirsizliği azalır hem film zenginleşir.
  - Arkadan ya da omuz üstü görülen karakterin bile saç ve kıyafet çapası istemde yazılmalı. Yoksa Flow kendi kafasına göre çizer (EMBERFALL Ç032: Wren'in saçı koyu çıktı).
- **İçerik:**
  - Kan, gore, ölü bedeni anlatan kelimeler yok. Şiddet tepkiyle, gölgeyle ve sonrasıyla anlatılır. Riskli sahnelere yumuşatılmış yedek istem yazılır.
  - Dünya kuralları NET olmalı: çağ, kumaş, renk paleti, **NE YOK listesi** (fermuar, modern mont...). Pilotta "zırhlı askerler + modern montlu kadın" uyumsuzluğu bundan çıkmıştı.
- **Netlik:**
  - Adlar ve ilişkiler erken ve sözle verilmeli.
  - Büyük sır görüntünün yanında bir replikle de söylenmeli.
  - Dünya kuralları ekranda anlatılmalı.
- **Kredi, süre ve ritim:**
  - Flow 360p 8 sn = 6 kredi, 720p = 12 kredi, görsel = 0 kredi. 12-15 dk'lık bölüm ≈ 105-110 çekim ≈ 650 kredi. Yeniden denemeler için %20 pay bırak.
  - Doruk sahneler Google Veo (1080p, sesli, Google Cloud ile dolar ödenir).
  - Süre dolgu çekimle şişirilmez; ritim gerektiriyorsa bölüm kısa kalır.
- **Süreç:** Kullanım sınırı ve uzun işler için: ajanlar dosyaya yazsın, yönetmen `00_DURUM.md` dosyasını güncel tutsun.

---

## 6. Örnek dosyalar (`BILGI\ORNEK_EMBERFALL\`)
| Dosya | Ne |
|---|---|
| `00_BRIFING.md` | Mimar brifingi |
| `00_JURI_TABLOSU.md` | Jüri puan tablosu |
| `oneri_FINAL_v2.md` | Birleştirilmiş ve denetlenmiş sezon belgesi |
| `00_CEKIM_LISTESI_BICIMI.md` | Çekim listesi biçimi |
| `B1_cekim_listesi_v2.md` | 109 çekimlik bölüm listesi |
| `muzik_plani.md` | Leitmotifler ve müzik ipuçları |
| `SAHNELER.json` | Üretime giren son dosya |
| `EMBERFALL_KARARLARI.md` | Proje kararları dosyası örneği |
