# Şeytanın avukatı: tur 2 tasarımına itirazlar

> **Rol:** Tasarımı çürütmeye çalışan eleştirmen (iş akışının bu adımı). Bu belge bir karar değildir, tur 3'e girdi olarak yazıldı.
> **Tarih:** 23.10.2026 · **Dil:** Türkçe
> **Güvenlik:** Hiçbir öneri bir güvenlik kuralını gevşetmez. "Uyarıda dur", "bot tespiti atlatılmaz", "anahtar yazılmaz" ve "kalıcı silme yok"
> kuralları aynen geçerlidir.

## Okuma kapsamı

| Kapsam | Dosyalar |
|---|---|
| Baştan sona okundu | [CM2], [UM2], [GS2] |
| Seçili bölümler ve arama (grep) ile okundu | [SM2] §1–4.2, §4.6, §4.8.3–4.9 · [KU2] §1–4.3, §4.9 · [SN2] §1–2, §4.1–4.2 · [YN2] §1–2, §4.8–4.9 |
| Yalnız aramayla tarandı | Tur 1 dosyaları |
| Dayanak belgeler | BK, ZN, RE (anahtarlar bu oturumda sayıldı), AR1–AR3, YR, PA, SV, DR, H/olagandisi-dur, H/proje-b2, H/uretim-hatti-v2 |
| Okunan kod | `YZ_FILM/ARACLAR/memmet.py`, `film.py`, `saglayicilar/flow.py`, `puan_oku.py`, `izleme_paketi.py` |

Okumadığım bölümlerde bir sorun çözülmüş olabilir. Öyleyse ilgili madde düşer.

## Kısaltmalar

`§` numaraları ilgili dosyanın kendi başlık numaralarıdır. Dosya yolları `.claude/skills/film-yap/` köküne görelidir. Aksi yazılıysa depo köküne görelidir.

| Kısaltma | Dosya |
|---|---|
| [CM2] | `tartisma/tur2_claude-code-mimari.md` |
| [UM2] | `tartisma/tur2_uretim-muhendisi.md` |
| [GS2] | `tartisma/tur2_goruntu-sureklilik.md` |
| [SM2] | `tartisma/tur2_ses-muzik.md` |
| [KU2] | `tartisma/tur2_kurgucu.md` |
| [SN2] | `tartisma/tur2_senarist.md` |
| [YN2] | `tartisma/tur2_yonetmen.md` |
| BK | `BILGI_KURALLARI.md` |
| ZN | `ZANAAT.md` |
| RE | `ritim_esikleri.json` |
| AR1, AR2, AR3 | `arastirma/01_film_hatlari.md`, `02_sureklilik.md`, `03_ses_ve_claude_code.md` |
| YR | `YZ_FILM/BILGI/YAPIM_REHBERI.md` (depo kökünden) |
| PA, SV, DR | `FILMLE ILGILI CLAUDE/05_PROJELER_VE_ARSIV.md`, `06_SERVISLER_VE_MALIYET.md`, `03_DERSLER.md` (depo kökünden) |
| H/<ad> | `FILMLE ILGILI CLAUDE/HAFIZA_YEDEGI/<ad>.md` (depo kökünden) |

## Etiketler

- **(tahmin — benim):** Bu belgedeki kendi kaba hesabım. Kaynağı yok, ölçülmesi gerekir.
- **(bellekten, doğrulanmalı):** Bu oturumda kaynağını açmadığım bilgi.
- Tasarım belgelerinin kendi "(tahmin)" ve "[tahmin]" etiketleri olduğu gibi aktarılır.

Maddelerin önem dereceleri:

| Derece | Anlamı |
|---|---|
| **KRİTİK** | Düzeltilmezse ilk film büyük olasılıkla bitmez ya da bir kesin karar çiğnenir. |
| **ORTA** | Kaliteyi, takvimi ya da kullanıcının güvenini ciddi biçimde bozar. |
| **KÜÇÜK** | Yerel bir kusurdur, düzeltmesi ucuzdur. |

---

## 0. Hüküm

Tasarım ayrıntıda titiz. Her uzman kendi kapısını, şemasını ve testini yazmış. Ama bütün yapı ölçülmemiş dört varsayıma dayanıyor:

1. **Flow kapasitesi.** Tek bir Flow hesabının bir film için ≈527 video ve ≈116–240 görsel gönderimini kaldıracağı varsayılıyor. B3'te ise video aşaması ilk gönderimlerde işaretlendi ve ≈137 klip çekilemeden kaldı.
2. **Claude kullanım sınırı.** Sınırın ≈350–550 Opus·high görevi ve en kötü durumda ≈6–7M tokenlik seyirci turlarını taşıyacağı varsayılıyor. EMBERFALL'da sınır zaten dolmuştu.
3. **Omni ve ses dönüştürme.** Omni'nin saniyeli adımlara uyacağı ve Veo sesinin 4 GB kartta yerel dönüştürücüyle yeterli kalitede çevrileceği varsayılıyor. İkisi için de "ölçülecek" yazılmış.
4. **Claude Code davranışları.** 11 davranışın belgede yazıldığı gibi işleyeceği varsayılıyor. Hiçbiri sınanmadı.

Pilot dalga bu varsayımları ancak kâğıt, kart, G1 ve animatik bittikten sonra ölçüyor. O zamana kadar ≈120 satırlık P0 kodu yazılmış olacak.

İki sorun daha var:

- "Kullanıcıya yalnız konu sorulur" sözü, kullanıcıya iş yüklenerek tutuluyor: ≈527 GÖNDER, 18–24 paket, `DEVAM.bat` ve "kurulum ayarı" adı altında kararlar.
- 8/10 kapısı geçmişte hiç tutturulmadı. Kullanıcının "süper" dediği B2 P1 7/10'du.

Bu hâliyle en olası sonuç şudur: ilk film video aşamasında Flow kısıtına, kâğıt ya da animatik kapısında DUR'a veya kullanım sınırına takılır.

**Önerim:**
1. Kod yazmadan önce 1–2 haftalık bir "Aşama 0" ölçüm turu yapılsın (§10).
2. Puan kapıları ilk iki filmde gölge kipte çalışsın: puanlar ölçülsün ama hattı durdurmasın.

---

## 1. En kritik 5 madde

**K-1 · Flow kapasitesi ölçülmemiş ve tek hesaba bağlı**
- **Neden öldürücü:** Bir film ≈527 video ve ≈116–240 görsel gönderimi istiyor. B3'te video aşaması ilk gönderimlerde işaretlendi. Ücretli yedek kapalı ve fiyatı bilinmiyor.
- **İlk adım:** B3'ün hazır kareleriyle 3 ayrı günde kapasite ölçülsün. Takvim bu ölçümden türetilsin. Hesap değiştirmek açıkça yasaklansın.

**K-2 · "Yalnız konu" sözü fiziksel iş ve gizli kararlarla delinmiş**
- **Neden öldürücü:** Kullanıcıdan ≈527 GÖNDER, 18–24 paket ve `DEVAM.bat` bekleniyor. DUR'dan sonra "yeni konu yaz ya da devam de" deniyor. `GECE_IZNI.bat` da kılık değiştirmiş bir soru. Q9 ile İ-9 arasındaki çelişki çözülmemiş.
- **İlk adım:** Tek bir "kullanıcı sözleşmesi" kartı yazılsın. El işi için ölçülebilir bir bütçe konsun. DUR'dan sonra ne olacağına ekip karar versin.

**K-3 · Claude kullanım ve token bütçesi yok**
- **Neden öldürücü:** Film 350–550 opus·high görev istiyor, en kötü durumda ≈650–700 (tahmin — benim). Seyirci turları ≈6–7M, kör gözlem ≈3M token tutuyor. Sınır dolunca hat da Z1 ardılları da durur.
- **İlk adım:** Her görevin kullanımı kaydedilsin. Film için bir token bütçesi ve devre kesici konsun. Sonnet ile Opus etiketli sette ölçülerek kıyaslansın.

**K-4 · Temeller ölçülmeden ≈120 satırlık P0 kodu yazılıyor, pilot çok geç geliyor**
- **Neden öldürücü:** Doğrulanmamış temeller: saniyeli adım uyumu, ses dönüştürme, 11 Claude Code davranışı, CapCut ve Gemini kotası.
- **İlk adım:** Aşama 0'da 6 ölçüm denemesi yapılsın, ardından devam ya da dur kararı verilsin.

**K-5 · Kapılar kalibre değil; DUR riski ve tavansız döngüler var**
- **Neden öldürücü:** RE'deki 148 anahtarın hiçbirinin kaynağı yok. 8/10 eşiği hiç tutturulmadı. Kart tarifi, H15 ve H12'den sonrası tavansız. Her turda yeni seyirciyle ölçmek, metin iyileşmese de şansla geçirebilir.
- **İlk adım:** Gölge kip, küresel tur bütçesi ve seyirci güvenilirliği ölçümü.

**Altıncı KRİTİK madde (K-6):** Depodaki `memmet.py` bugün "olağan dışı" uyarısını görünce bekliyor ve uyarı kaybolunca kendiliğinden devam ediyor. Tasarım bunu biliyor ([UM2] S1), ama düzeltmeyi memmet3'ün depoya gelmesine bağlamış.

---

## 2. KRİTİK maddeler

### K-1 · Flow kapasitesi ölçülmemiş ve tek hesaba bağlı; takvim ve "kendiliğinden bitiş" buna dayanıyor

**İddia.** Video ve görsel hacmi tek bir Flow hesabının kaldıracağı varsayımıyla planlanmış. Eldeki tek kanıt bunun tersini gösteriyor, yedek yol da kapalı.

**Kanıt:**

*Tasarımın istediği hacim:*
- [UM2] §4.1.3 "Ölçek, maliyet ve takvim":
  - 405 klip ve ≈527 gönderim (405 × 1,3).
  - "≈ 12,9 saat (gece temposu; 2 gece)", "video süresi FK, 720p'de doğrulanmadı".
  - ≈116 görsel düzeltme gönderimi, "tavan 20/gün" [tahmin].
- [GS2] İ-13 ve R6: ≈240 düzeltme görseli. Günde 20 tavanla bu ≈12 ayrı Flow görsel günü eder.
- [GS2] §4.9.3 #10: "Flow'da günlük görsel tavanı ve görsel → video bekleme süresi için kaynakta sayı yok."

*Geçmişte yaşananlar:*
- PA "Bölüm 3 — YARIM KALDI": "Kalan: P1–P3 videoları (≈137 klip …). Flow hesabının video tarafı 19.10 gecesi işaretli kaldı."
- H/olagandisi-dur, 19.10 notu: Aynı akşam ≈40 görsel gönderildikten sonra yarı otomatik modda bile 3 gönderimde uyarı geldi. Ardından yavaş tempoda da her video ≈30 sn içinde uyarı aldı. DR "Google Flow ve olağan dışı etkinlik" bölümü aynı dersi yazıyor.
- Gündüz modunda 15–20 dk'da bir uyarı geldi (BK §6.2 #7).
- B2: 134 videonun 126'sı yaklaşık bir günde ve iki hesapla çekildi: önce "başkası da kullanıyor" denen ortak hesap, 16.10 öğlenden sonra kullanıcının kendi Ultra hesabı (H/proje-b2). Kendi hesap ≈2–3 gün sonra, 19.10 gecesi video tarafında işaretlendi (H/olagandisi-dur).
- Bir film B2'nin ≈4 katı video gönderimi istiyor: 527 / 134 ≈ 3,9 (hesap — benim).

*Plan sayısı tek bir nokta tahmini:*
- ZN §2.6: 495 plan / 405 klip.
- BK §3 #5 (CLAUDE_ICIN'den): "Film (35–40 dk) ≈ 250–300 klip".
- B2'den doğrusal ölçekleme: 198 plan / 12:14 → 40 dk ≈ 650 plan ≈ 440 klip (tahmin — benim).
- Kullanıcının "süper" dediği P1 v11'de ortalama plan süresi ≈3,3 sn (BK §3 #5 ve #9). Bu, ZN'nin hedeflediği ortalama plan süresinden (ASL 4,2–5,2 sn, ZN §7.1) hızlı. Ritim seyirciye göre hızlanırsa klip sayısı artar.

*Yedek yol kapalı:*
- [UM2] §4.5.12: `"video_yedek_izinli": []`, `"usd_tavan_film": 0`.
- [UM2] Q4: Vertex Veo fiyatı bilinmiyor.
- [UM2] C7 ve BK §6.4: kie.ai "gri abonelik havuzu" şüphesi taşıyor.
- [UM2] §4.8.5 bunu kendisi söylüyor: "İnsansız tam otomatik video üretimi için doğru yol resmî API'dir (Vertex Veo). Flow aboneliği bir insan arayüzüdür."

*Hesap değiştirme yasağı yazılı değil:*
- BK §6.2 #8 hesap işaretlenince "bekle, ikinci hesap ya da kie.ai API" diyor.
- H/olagandisi-dur başka bir kanalın başka bir hesapla Memmet'i uyarısız çalıştırdığını yazıyor.
- Tasarımın hiçbir yerinde "işaretli hesabın yerine başka hesapla devam edilmez" kuralı yok. Okuduğum bölümlerde yalnız "uyarıda dur" kuralı var.

**Neden çürütür.** 12,9 saatlik Flow süresi ve 2–3 haftalık takvim, hesabın işaretlenmeyeceği varsayımına dayanıyor. B3'te işaretlenme, bir filmin ihtiyacının çok küçük bir kısmında geldi. Hesap haftalarca işaretli kalırsa film kâğıtta biter ama videoda durur. Hat bu durumu "BEKLE" olarak gösterir, ama ne kadar bekleneceğini kimse bilmez. "Takvimin darboğazı" Flow ise bu bilgi tasarımın en zayıf sayısıdır.

**Düzeltme:**
1. **Aşama 0'da kapasite ölçümü (S0-b, §10).**
   - Ne ile: B3'ün G1'den geçmiş hazır P1 kareleri (PA: "Parti 1'in 44 başlangıç görseli üretildi ve 2 tur denetimden geçti").
   - Nasıl: 3 ayrı günde, `elle` modda, 17.10 temposunda (BK §6.2 #6), günde en çok 20 video (tahmin — benim). Her gün ilk uyarıda durulur.
   - Ne ölçülür: uyarısız gönderim sayısı/gün ve uyarıdan sonra hesabın açılma süresi.
   - Bunlar B3'ün zaten çekilecek klipleridir. Kredi film dışına harcanmaz.
2. **Takvimi ölçümden türet.**
   - `gun_sayisi = ceil(gonderim / olculen_gunluk)` hesaplansın ve `URETIM_ONIZLEME`'ye aralık olarak yazılsın.
   - Film süresi [SN2] §2.5'in karar kuralına bütçe gibi kapasite de katılarak seçilsin. Ölçülen kapasite günde 30 videonun altındaysa ilk film 30 dk yazılsın (eşik tahmin — benim). 30 dk, RE `film_sure_aralik_sn`'nin alt sınırıdır.
3. **Yedek yolun fiyatını ölç.** Kullanıcının Google Cloud hesabı varsa Vertex Veo'nun fiyatı ve kotası Aşama 0'da tek bir klipte ölçülsün. Fiyatı bilinmeyen yedek, "dürüst sonuç" diye sunulamaz.
4. **Korkuluk olarak yaz:** "İşaretli hesabın yerine başka bir Google/Flow hesabıyla devam edilmez; ortak ya da aile hesabı kullanılmaz."
   - Önerim, BK §6.2 #8'deki "ikinci hesap" seçeneğinin kısıtı atlatmanın bir biçimi sayılması. Kullanıcı bunun tersine karar verirse, karar yazılı politika olarak kaydedilsin.
   - Kodda: `memmet.py` ve `film.py`, Flow profili ya da hesap kimliği değişince yeni hesabı `FLOW_KILIDI` ile kilitlesin. Kilidi yalnız kullanıcı `UYARI_GECTI.bat` ile, İ-8 şartlarıyla kaldırabilsin.

### K-2 · "Kullanıcıya yalnız konu sorulur" sözü fiziksel iş ve "kurulum ayarı" adı altında kararlarla tutuluyor

**İddia.** Karar 1 harfiyen korunuyor ama ruhu delinmiş. Kullanıcıya soru sorulmuyor, onun yerine haftalarca operatörlük yaptırılıyor ve kararlar "bilgi" kılığına sokuluyor.

**Kanıt:**

*Kullanıcıya yüklenen iş:*
- [UM2] §4.1.2 M2 "sabit liste": Google girişi ve reCAPTCHA, ≈18–24 Gemini paketi [tahmin], `elle` modda "≈ 527 kez" GÖNDER [hesap], CapCut'tan dışa aktarma, yükleme onayı. Kısıt durumunda ayrıca "elle 1 video denemesi" ve `UYARI_GECTI.bat`. "Kurulumda bir kez": KURULUM.bat, Python 3.12 kurulumu, git, Telegram anahtarı, kurulum ayarları.
- [GS2] R7: kart, kamera ağacı basamakları ve ikinci göz için ≈10–13 paket turu [tahmin]. Bu sayı [UM2]'nin 18–24'üyle tutmuyor.
- [GS2] İ-6: Gemini "ikinci göz" varsayılan olarak açık, yani her partide kullanıcıya bir paket daha düşüyor.
- [CM2] K-23 ve R-2: Kullanım sınırı dolunca hattı `DEVAM.bat` sürdürür ("Claude kendi kendine uyanamaz").
- [SM2] §1 (İ-3 içinde): `dinleyici` yoksa madde "ölçülemedi" olur ve "ilk filmde elle dinleme notlarıyla ders defterine girer". Kimin dinleyeceği yazılmamış, bu iş M2 listesinde de yok.

*En ağır yol varsayılan:*
- [UM2] §4.5.12'deki varsayılanlar `"flow": {"mod": "elle", "gece_izni": false}` ve `"usd_tavan_film": 0`. Kullanıcıya en çok elle işi yükleyen yol varsayılan olmuş.

*Kılık değiştirmiş sorular:*
- [UM2] Q9 ("Kullanıcıya kurulumda bir kez dürüstçe sorulur") ile [CM2] İ-9 ("Kurulum soru sormaz … `GECE_IZNI.bat` … bilgi") çelişiyor. [CM2] §4.9.2'de Ç-5 olarak hâlâ açık.
- [CM2] İ-9: "kullanıcı .bat'a basmazsa hat varsayılanla sürer". Bu, biçimi değiştirilmiş bir sorudur.
- [SN2] §2.6 adım 5: DUR olunca "Kullanıcı kendi isteğiyle yeni bir konu yazar ya da 'bu hâliyle devam' der". "Bu bir soru değildir" deniyor, ama hat kullanıcının cevabını bekliyor.

*Belgeler kendi içinde de çelişik:*
- DR "Araç/işleyiş" ve BK §7 #8 "Kullanıcıya elle iş çıkarılmaz" diyor.
- BK §6.3 #9 ise "büyük toplu paketler"e izin veriyor.
- BK §6.2 #10 ("Kredi ya da para harcatan onaylara … kullanıcı basar") ile `gece_izni`'nin aynı şey sayılıp sayılmayacağı [UM2] Q9'da açık soru olarak duruyor.

**Neden çürütür.** Kullanıcı "konuyu söyle, film gelsin" bekliyor. Tasarım ise 2–3 hafta boyunca bilgisayar başında GÖNDER'e basan, paket taşıyan ve `DEVAM.bat`'a basan bir operatör varsayıyor. Kullanıcı bunu baştan bilmezse güven ilk haftada kaybolur. BK §7 #14'e göre en büyük kızgınlık sebebi kopuk taslak göstermek; burada sebep gizli iş olur. Gerçekte ikinci bir kullanıcı arayüzü tasarlanmış ama adı konmamış.

**Düzeltme:**
1. **Tek bir "kullanıcı sözleşmesi" kartı** yazılsın: `BASLA_BURADAN.txt` ve kurulum sonu ekranı.
   - İçeriği: "Senden istenecek işler şunlar, ilk filmde yaklaşık şu kadar: GÖNDER ≈ X kez, paket ≈ Y, DEVAM ≈ Z." Sayılar Aşama 0 ölçümünden gelir.
   - Bu kart soru değil, bilgidir. Karar 1 "konu dışında karar sorusu yok" diye yorumlanıyorsa bu yorum karta açıkça yazılsın.
2. **Kurulumdaki izin ekranına tek karar.** Gece izni, dolar tavanı, CC0 indirme izni ve ikinci göz için kurulumda tek ve son bir ekran olacak mı, hiç olmayacak mı? Tur 3'te tek karar sahibi bunu kesinleştirsin. Bugün iki uzmanın iki ayrı yorumu var.
3. **M2'yi sayıya çevir:** "İlk filmde kullanıcının el işi ≤ N saat". N, BK §1.1 profilindeki "haftada 20+ saat"ten türetilsin. Film sonu raporunda gerçek süre ölçülsün.
4. **Paket yükünü sıfırlayabilecek tek ölçüm:** Gemini API (AI Studio) ile toplu görsel üretiminin kotası ve maliyeti ([UM2] Q16, Q13) Aşama 0'da tek bir pakette denensin (S0-e).
5. **DUR'dan sonra ekip varsayılanı yazılsın:**
   - Konu kartı en çok bir kez yeniden yorumlanır (`yapimci` `konu` kipi, yeni eksen).
   - Yine DUR olursa `EN_IYI` sürüm "yüzüne vur" raporuyla (BK §7 #13) kâğıt ürün olarak teslim edilir: senaryo ve animatik. Videoya geçilmez.
   - Kullanıcıya "ne yapayım?" diye sorulmaz.
6. **"Elle dinleme" işi** ya M2 listesine yazılsın ya da tasarımdan çıkarılsın (bkz. O-7).

### K-3 · Claude kullanım sınırı ve token bütçesi hiç hesaplanmamış; "kısılmaz" deniyor

**İddia.** Takvimi Flow değil Claude belirleyebilir. Buna rağmen tasarımda token ya da kullanım sayısı yok, yalnız görev sayısı var. Tüketimi sınırlayan bir mekanizma da yok.

**Kanıt:**

*Riski tasarım kendisi yazmış:*
- [CM2] §4.9.1 R-2: "≈ 350–550 Opus görevi (tahmin); Claude kendi kendine uyanamaz → Hat günlerce bekler".
- [UM2] R1 ve Q12: "Abonelik kullanım sınırı 350–550 çağrıya yetiyor mu? — İlk filmde ölçülür."
- [UM2] §4.1.3 takvimine göre kâğıt evresinin darboğazı "Claude kullanım sınırı".

*Token yükü:*
- [KU2] R3: Seyirci başına ≈0,2M token, en kötü durumda ≈6–7M token [tahmin]. "EMBERFALL'da kullanım sınırı dolmuştu."
- YR §1, altın kural 3 bunu doğruluyor: "EMBERFALL'da sınır doldu, ajanlar yarıda kesildi".
- [GS2] §4.1.4: Yalnız `kare-tarifcisi` için ≈2.050 görsel, ≈3M girdi tokeni ve ≈175 görev [tahmin]. Çıktı tokenleri ve çok turlu yeniden okuma bu sayıya dahil değil.

*Görev sayısı en kötü durumu kapsamıyor:*
- [UM2] §4.3.6 tablosu animatik (A12) için 20–35, kurgu (A16) için 20–35 çağrı sayıyor.
- [KU2] KR4/KR9'un en kötü durumu: 5'er tur × (3 seyirci + 3 ilk 2 dk + 6 eşleştirici + kurgucu + tur 1'de kesici) ≈ 65–70'er çağrı (tahmin — benim).
- Kâğıtta en kötü durum ≈10 tur × ≈7–8 görev ≈ 70–80 çağrı (tahmin — benim).
- Bunlar eklenince en kötü durum ≈650–700 görevi bulur (tahmin — benim).

*Model seçimi ve tavan:*
- [CM2] §4.3.1 #4: 21 ajanın hepsi `opus` + `effort: high`. §4.3.2: "Kesin karar 6 gereği kısılmaz".
- Kullanıcının kendi kuralı farklı. BK §7 #2: "Önemli işlerde ajanlar Opus + effort high … Basit dönüştürme işleri Sonnet ya da betikle yapılır". YR §1 #5 de süreklilik, üretilebilirlik ve istem işleri için Sonnet önermişti.
- [CM2] K-10: Stop kancasının "8 ardışık devam tavanı" araç çağrısında sıfırlanıyor. Bu, boş Stop döngüsünü sınırlar ama bütün film sürüşünün tüketimine tavan koymaz.
- [CM2] İ-12: Ana bağlama ≈1.400–2.200 araç çağrısı ekleniyor ve bağlam birkaç kez sıkıştırılıyor (tahmin).

*Kaba dolar karşılığı (API yolu):*
- Fiyat: claude-api becerisindeki Opus 5.5 fiyatı, girdi $4/M, çıktı $20/M.
- Hesap: 350–550 görev × (20–60K girdi + 5–30K çıktı) ≈ 63–462 $/film (tahmin — benim). Çok turlu yeniden okuma ve önbellek indirimi hesaba katılmadı.
- Karşılaştırma: BK §1.1 profilinde "ayda 50–150 $" yazıyor. Bağlamdan bunu bütçe olarak okudum; doğrulanmalı.

**Neden çürütür.** Abonelikte sınır dolunca hat durur ve kullanıcı `DEVAM.bat`'a basana kadar bekler (K-2). Z1 ardılları V3 kör gözlemini, yani Claude'u beklediği için Flow oturumu da boşa döner ([GS2] R10). Bu sayılar bilinmeden ne "2–3 hafta" takviminin ne de "tam otomatik" iddiasının dayanağı var. "Kısılmaz" demek ölçümün yerini tutmaz (O-14).

**Düzeltme:**
1. **Kullanımı kaydet.** Görev zarfına `kullanim: {girdi, cikti, onbellek_okuma, sure_sn, model, effort}` alanı eklensin, `film.py` film başına toplamı tutsun. P0, küçük bir iş. Claude Code'un alt ajan sonucunda bu bilgiyi verip vermediği Aşama 0'da doğrulansın (S0-a); ben bilmiyorum.
2. **Film token bütçesi ve devre kesici.** Her aşamaya bir tavan konsun (kâğıt ≤ X, animatik ≤ Y …). Tavan aşılınca hat DUR'a geçmesin, "BEKLE + projeksiyon raporu" versin. Stop kancası devam etmeden önce bu bütçeye baksın.
3. **Ölçülmüş model seçimi.** Etiketli küçük bir sette (B3'ün 44 karesi ve 20 sahte görev) şu üç yapılandırma kıyaslansın: Sonnet 5.5, Opus 5.5 `medium`, Opus 5.5 `high`. Kıyaslanacak roller: `kare-tarifcisi`, `ozet-eslestirici`, `oyuncu`, `diyalog-editoru`.
   - Fark ölçülemiyorsa ucuz yapılandırma kalite kaybı sayılmaz ve karar 6 çiğnenmiş olmaz.
   - Fark varsa Opus·high kalır.
4. **Kısmi izlemeyi A/B ile dene.** [KU2] KR8'de her tur bütün filmi baştan izletiyor. Bunun yerine değişen partiler, son turda da bir tam tur izletilebilir. Kalite farkı animatikte ölçülerek karar verilsin.
5. **Erken projeksiyon.** İlk 30–50 görevin gerçek tüketimi ölçülsün, kalan aşamaların projeksiyonu kullanıcıya bilgi olarak gösterilsin.
   - Projeksiyon abonelik penceresine sığmıyorsa hat bunu söylesin. Kullanıcıya soru sorulmaz.
   - Abonelik türünün Opus kullanımını sınırlayabileceğini düşünüyorum (bellekten, doğrulanmalı).

### K-4 · ≈120 satırlık P0 kodu ölçülmemiş temellere dayanıyor; pilot dalga (A14a) çok geç

**İddia.** Tasarımın en pahalı yazılım işi, en geç öğrenilecek bilgiye bağlı. Temeller tutmazsa P0 modüllerinin bir kısmı baştan yazılır.

**Kanıt:**
- **Atomik zincir:** [YN2] §4.9 R1: "Flow ya da Omni saniyeli adımlara ('0.5-3s:') uymayabilir; ölçülmedi." Karar 2'nin bütün ölçü düzeni bu uyuma dayanıyor: V3, `etki` alanı ve dünya defteri.
- **Ses yolu:**
  - [SM2] §4.8.3 tablosunda ana ses yolu `veo_donustur` için "4 GB kartta: çalışabilir; kıyasla ölçülecek" yazıyor.
  - Dönüştürücünün aksanı Veo'dan taşıdığı bilgisi "bellekten" ([SM2] öz 2).
  - RVC ancak hukuki durum netleşirse kullanılabilir ([SM2] §4.8.3).
  - ACE-Step için "3050 Ti'de süre ölçülecek", "ağırlık sayfası bu oturumda açılmadı" ([SM2] §4.8.4).
- **Claude Code:**
  - [CM2] §4.9.4 "Uygulamadan önce bir kez doğrulanacak" 11 davranış sayıyor: fork'un kapatılması, arka plan bildirimiyle uyanma, SubagentStop `block` ile aşamalı devam, `onFailure`, `env`'in kancalara geçmesi, Windows'ta Git Bash ile kanca çalıştırma, `claude --continue "devam"` ve diğerleri.
  - Habersizlik ve erişim kancalarının hepsi bu davranışlara dayanıyor.
  - [CM2] Claude Code belgelerini WebFetch ile okumuş (giriş bölümü). AR1 "Nasıl doğrulandı" bölümünün kendi notuna göre "WebFetch sayfayı küçük bir modelle özetler"; yani alıntılar bile özet olabilir.
- **Kalibrasyon:**
  - [GS2] GS0 kalibrasyonu B3'ün 44 karesine dayanıyor, ama etiket JSON'u henüz yok ([GS2] §4.9.3 #7, [UM2] Q11).
  - 1280×720 zincir karesinin Flow'da kaliteyi ne kadar düşürdüğü bilinmiyor ([GS2] §4.9.3 #3).
- **CapCut:** [KU2] R8: pycapcut ve CapCut'ın taslağı şifrelemesi doğrulanmadı.
- **Fiyat ve süre:** [UM2] Q2, Q3, Q13, Q15, Q16 açık: politika reddinin kredi yakıp yakmadığı, 10 sn klibin fiyatı, Gemini'nin plan başına 3 aday verip veremediği, 720p üretim süresi, Gemini kotası.
- **Sıralama:**
  - Pilot dalga ilk filmin A14a aşamasında ([UM2] öz 4). Yani kâğıt (1–3 gün), kartlar (1–2), G1 (4–7) ve animatik (1–2) bittikten sonra ([UM2] §4.1.3).
  - O zamana kadar ≈120 P0 tablo satırı yazılmış olur (bu oturumdaki grep sayımı; aynı modül birden çok satırda geçebilir): CM 17, GS 26, KU 15, SN 9, SM 23, UM 12, YN 21.

**Neden çürütür.** Varsayımlar tutmazsa üç zincirleme sonuç doğar:
- **Saniyeli adım uyumu kötü çıkarsa:** [YN2]'nin kendi yedeği "adım sayısı 2'ye iner ve Z2 oranı artırılır" diyor. Bu da V3'ü, dünya defterinin girdisini, Flow yükünü (Z2 bitiş görselleri) ve kredi payını değiştirir.
- **Ses dönüştürme 4 GB'ta yetersiz çıkarsa:** Ana yol `tts_dudak` olur. 190 diyalog planı × ≈5 dk ≈ 16 saat GPU süresi demek (tahmin — benim; birim süre [SM2] D-MT). Üstelik bu yolda ağız bölgesi 256 px'te yeniden üretilir.
- **Kanca davranışlarından biri tutmazsa:** Habersizlik güvencesi sessizce kalkar ([CM2] R-6).

**Düzeltme.** Yazılımdan önce 6 ölçüm denemesi (spike) yapılsın. Toplam ≈1–2 hafta sürer (tahmin — benim). Ayrıntılar §10.1'de:

| Deneme | Ne ölçülür |
|---|---|
| S0-a | Claude Code: 11 davranış, Windows'ta |
| S0-b | Flow ve Omni: kapasite, adım uyumu, 720p süresi, red kredisi, Z1 kalitesi |
| S0-c | Ses: arşiv kliplerinde ses dönüştürme, MuseTalk kurulumu |
| S0-d | CapCut: klon ve şifreleme |
| S0-e | Gemini: paket ve kota |
| S0-f | Token: gerçek kullanım |

Her deneme "devam / dur" kararını gerekçesiyle `_RAPOR/ASAMA0.json`'a yazar. P0 listesi bu sonuçlara göre yeniden sıralanır.

### K-5 · Kapılar kalibre edilmemiş, 8/10 hiç tutturulmadı, bazı döngülerin tavanı yok; yeni seyirciyle tekrar ölçmek şansla geçirir

**İddia.** Hattın "kalite" dediği şey, kaynağı olmayan ve geçmişte hiç tutturulmamış eşiklere bağlı. Bu eşikler ya hattı sürekli durdurur (DUR) ya da çoklu deneme yoluyla şansla geçilir. İkisi de kaliteyi ölçmez.

**Kanıt:**

*Eşiklerin kaynağı yok:*
- RE'deki 148 anahtarın hiçbirinde kaynak ya da "tahmin" alanı yok, yalnız `deger` ve `aciklama` var (bu oturumda sayıldı).
- Örnekler: `seyirci_genel_esik` 8 ("GENEL medyan geçme eşiği"), `kagit_tur_max` 4, `ozet_eslesme_min` 0,8, `klip_bolme_oran_hedef` 0,18.
- Uzmanlar "[kaynak: RE …]" yazınca kaynaksız sayı kaynaklı görünüyor. Örnekler: [SN2] §4.1 S1, [UM2] M7, [UM2] §4.1.3.

*Eşik geçmişte hiç tutturulmadı:*
- ZN §7.3 geçme koşulu: GENEL medyan ≥ 8, hiçbir ölçüt < 7, KRİTİK 0, özet ≥ %80. ZN §7.2 #2: ilk 2 dakikada 3 seyircinin 3'ü de "evet" demeli.
- B2 P1 puanları sırasıyla v7 6, v8 5, v9 6, v10 6,5, v11 7. Kullanıcı v11'i "süper" buldu (BK §3 #9, BK §8 #20).
- B3 kâğıt puanları 6/8/7 (PA).
- Yani kullanıcının beğendiği sonuç bu kapıdan geçemezdi. [SN2] R12 bunu kendisi yazıyor: "Hikâye kapısı hiç geçmeyebilir".

*Çok sayıda kapı, her birinin kendi DUR'u:*
- Yaklaşık 35 kapı var: Z0–Z3, K0, KART, G1, G1Z/ZK, K1Ö, V1–V3, K1, S0–S8, HS_*, B0–B2/BK, HAT, PILOT.
- DUR örnekleri:
  - [SN2] §2.6: 10 kâğıt turu → DUR.
  - [KU2] KR4: animatik 3 + 2 tur → DUR, video kapalı kalır.
  - [GS2] GS9: plan `durdu` olur.
  - [KU2] KR9 ve §2.5: "KRİTİK için o da yoksa hat DURUR".

*Kurallar yalnız sıkılaşabiliyor:*
- [GS2] §4.7.10: SFace HATA eşiği "0,363'ün altına inemez (yalnız yükselebilir)".
- [UM2] §4.5.12: "Makine yalnız sıkılaştırabilir".
- Bu bir mandal gibi çalışır: her film kuralları biraz daha sıkılaştırır, geri gevşetecek yol yoktur. Zamanla DUR olasılığı artar.

*Kalibrasyon için yeterli veri yok:*
- [GS2] §4.7.10 kalibrasyon için "≥ 30 / kapı-alan" etiketli örnek istiyor (tahmin).
- Başlangıç seti B3'ün 44 karesi, bunların 21'i bozuk.
- Bu yüzden çoğu kapı-alan çiftinde ilk filmde kalibrasyon mümkün değil (hesap — benim).

*Tavansız döngüler (§7 tablosu):*
1. **[GS2] GS4:** Kartta 2 CORRECTION turundan sonra "kart-tasarimcisi tarifi değiştirir". Kaç kez değiştirebileceği yazılı değil.
2. **[SN2] H15:** Kaç kez tetiklenebileceğine tavan yok. "Hikâyeye geri dönüş en çok 1 kez (tahmin)" yalnız karnede (§4.1.3), kapı değil.
3. **[SN2] H12:** "üçüncü bir sürüm … (en çok 2 tur)" yazıyor, sonrası tanımsız.
4. **[YN2] Y9-c bölme:** Bölünen planın yeni planlarında deneme sayacının sıfırdan başlayıp başlamadığı yazılı değil.
5. **[CM2] K-10:** Stop devamı fiilen sınırsız (K-3).
6. **Flow uyarıları:** Her yeni uyarı yeni bir `UYARI_GECTI` döngüsü açar. Uyarı sayısına tavan yok.

*Çoklu deneme etkisi:*
- Her turda **yeni** 3 seyirci kullanılıyor (ZN §7.3) ve kâğıtta en çok 10 tur var.
- Metin hiç iyileşmese bile, tek turda şansla geçme olasılığı p ise 10 turda geçme olasılığı 1 − (1 − p)^10 olur. p = 0,2 için bu ≈ %89 eder (hesap; p tahmin — benim). Bu durumda kapı kaliteyi değil sabrı ödüllendirir.
- Tersine p ≈ 0 ise döngü 10 tur boyunca token yakar ([KU2] R3).
- Seyirci puanlarının gürültüsü hiç ölçülmemiş. ZN §7.2 #10 bunu kendisi söylüyor: "Puanlar gürültülüdür".

**Düzeltme:**
1. **İlk iki filmde gölge kip.**
   - Puan kapıları (GENEL ≥ 8 ve ilk 2 dk'da 3/3) yalnız ölçülür ve kaydedilir.
   - Hattı yalnız ölçülebilir olgular durdurur: KRİTİK kopukluk = 0, özet eşleşmesi ≥ 0,8 ve şema, filtre ya da kimlik HATA'sı = 0.
   - Puan için geçici kural: "medyan ≥ 7; iki tur üst üste iyileşme yoksa turlar biter".
2. **Seyirci güvenilirliğini ölç.**
   - Aynı metin 5 bağımsız seyirciye iki kez okutulsun; metin olarak B2 P1 v11 ve B3 kâğıdı kullanılsın.
   - Puanların standart sapması ölçülsün.
   - Sapma ≥ 1 ise (eşik tahmin — benim) tek turun sonucu karar verdirmesin. İyileşme, turlar arası medyan farkıyla ve aynı seyirci havuzunun ikinci ölçümüyle değerlendirilsin.
3. **RE'ye zorunlu `kaynak` alanı.** Değerler `olcum | belge | tahmin` olsun. `esikler.py` kaynaksız anahtarı "tahmin" diye raporlasın. "[kaynak: RE]" yazımı yasaklansın, RE'deki değerin asıl dayanağı yazılsın.
4. **Film başına küresel geri dönüş bütçesi** (değerler tahmin — benim):
   - H15 en çok 2.
   - Kart tarifi revizyonu en çok 2.
   - Plan başına toplam deneme en çok 3. Bölmeler de bu sayıya dahildir; sayaç planın soyuna bağlı tutulur.
   - Animatik ve kurgu turlarının toplamı en çok 8.
   - Bütçe dolunca hat "en iyi sürüm + yüzüne vur raporu" ile sonuçlansın.
5. **Kalibrasyon iki yönlü olsun.**
   - Ders defteri bir eşiği sıkılaştırmadan önce, aynı kalibrasyon setinde yanlış alarm oranını da ölçsün. Oran %30'u aşıyorsa sıkılaştırma reddedilsin ([GS2] R12 hedefi).
   - Güvenlik eşikleri (Flow temposu, uyarıda dur) bu kuralın dışında kalır ve gevşetilemez.

### K-6 · Depodaki kod bugün karar 5'i çiğniyor; düzeltme memmet3'ün gelişine bağlanmış

**İddia.** Karar 5'in yazılımdaki tek uygulaması Memmet. Depodaki sürüm bu kuralı çiğniyor ve tasarım düzeltmeyi belirsiz bir tarihe bağlamış.

**Kanıt:**

*`memmet.py` (bu oturumda okundu):*
- `DOGRULAMA_KELIMELERI` listesinde "olağandışı etkinlik", "olağan dışı etkinlik" ve "unusual activity" var (satır 58). Yani uyarı metni bir doğrulama (reCAPTCHA) gibi işleniyor.
- `kontrol_noktasi()` (satır 167–176) bu metni görünce 15 sn aralıkla 12 saate kadar bekliyor. Metin kaybolunca "Doğrulama çözüldü, devam." yazıp kendiliğinden devam ediyor.
- Bu, BK §6.2 #1'deki "Otomatik yeniden başlatma yok" kuralını ve H/olagandisi-dur'daki "KESİN durur (mola/devam yok)" kuralını çiğniyor.
- Docstring ise "DURUR" diyor. `saglayicilar/flow.py` docstring'i de "DURUR (çıkış kodu 2)" diyor.

*`film.py`:*
- Docstring ve satır 121–122: `Kisitlandi` gelince "sıradaki sağlayıcı"ya otomatik geçiyor.
- `onay()` `input()` kullanıyor ([UM2] S7).

*[UM2] §4.6.1'in kendi bulguları:*
- S1b: Bir sonuç kartında "olağan" yazısı görülünce plan yeniden gönderiliyor.
- S2: Eski `.bat`'lar bütün kapıları atlıyor.
- S3: Varsayılan 360p ve 4–12 sn tempo.
- S6: memmet3 gece modunda uyarıda 5 kez sayfayı yenileyip deniyor (H/olagandisi-dur, 19.10 notu).
- S14–S15: Mola yeniden başlatmada sıfırlanıyor.

*Düzeltmenin zamanlaması:*
- [UM2] S6: "P0, ilk iş: memmet3 … depoya alınır, 5 deneme davranışı silinir, sonra S1–S5, S14–S15".
- Ama memmet3'ün depoya gelişi [UM2] Q6'ya bağlı ("Yereldeki Claude Code oturumu … kopyalar"). Ne tarihi ne sorumlusu yazılı.

*"İnsan taklidi" çerçevesi:*
- Memmet docstring'i "İnsan temposunda çalışır (rastgele bekleme, partiler arası mola)" diyor.
- [UM2] §4.8.5 ise "Rastgele bekleme insan taklidi için değil yük sınırlamak içindir" diyor.
- Kod ve kullanıcının göreceği metin hâlâ ilk çerçeveyi taşıyor.

**Neden çürütür.** Kullanıcı bugün `MEMMET_BASLAT.bat`'a basarsa Memmet uyarıda bekleyip kendiliğinden devam edebilir. Sağlayıcı zincirinde başka sağlayıcı tanımlıysa hat ona da geçebilir. Bu tasarımın en sert kuralıdır ve şu an yalnız belgede yaşıyor.

**Düzeltme:**
1. **memmet3'ü beklemeden bağımsız acil yama** (küçük PR):
   - Ayrı bir `OLAGANDISI_KELIMELERI` listesi tanımlansın. Uyarı görüldüğü anda `Durdur(kod="olagandisi")` çağrılsın ve `FLOW_KILIDI.json` yazılsın.
   - `HATA_KELIMELERI`'nden "olağan" ve "unusual" çıkarılsın.
   - `film.py`'de `Kisitlandi(olagandisi)` sonrası başka sağlayıcıya geçiş kapatılsın.
   - Eski `.bat`'lar `_ESKI/` klasörüne taşınsın; silinmesin.
2. **Docstring'ler düzeltilsin.** "İnsan temposu" ifadesi kalksın, yerine "yük sınırı" yazılsın.
3. **memmet3 aktarımı takvime girsin.** Bu iş bir "kurulum işi" olarak sahibi ve tarihiyle takvime yazılsın. memmet3 geldiğinde aynı yama ve T10 testi ona da uygulansın. T10, uyarı metni içeren HTML fikstürüyle çalışan testtir.
4. **Korkuluk testi CI'da zorunlu olsun.** Test, "olağan dışı" metni içeren fikstürde hiçbir yeni gönderim yapılmadığını kanıtlasın. [UM2] M8 bunu zaten tanımlıyor; test yamayla birlikte gelsin.

---

## 3. ORTA maddeler

### O-1 · Bütünleştirici yok; her uzman "nihai karar benim" diyor

- **Kanıt:**
  - [CM2] §4.9.2 Ç-1: "Tur 3 yoksa bu belge karardır" (klasör adları için).
  - [UM2] §2.2 "Ad ve dosya kararları" ve §2.3 "Kapı ad alanı".
  - [YN2] `30_YONETMEN/`, [SM2] `35_SES/`; [CM2] ise `_YONETMEN/`, `_SES/` diyor.
  - §5'te 20 açık çelişki var.
- **Neden önemli:** Kod yazılırken her PR farklı bir adı "doğru" sayar. Şema tutarsızlığı en çok sahte uçtan uca testte ortaya çıkar, o da geç kalmış olur.
- **Düzeltme:**
  - Tur 3'te tek bir bütünleştirici seçilsin. Bu bir ajan rolü ya da bu belgeleri okuyan tek bir karar oturumu olabilir.
  - Bütün adlar tek dosyada toplansın: `veri/ADLAR.json`. Kapsamı: klasör, ajan, kapı, plan alanı, sağlayıcı türü, `.bat` adları.
  - `test_adlar.py` belgelerde ve kodda geçen her adın `ADLAR.json`'da olup olmadığını denetlesin.

### O-2 · Sahipsiz işler

- **Kanıt:** §6 tablosu.
  - Renk eşleme (`renk_cila.py`), dikey Short çıktısı (`shorts_mp4.py`) ve jenerik üretimi (`jenerik.py`): CLAUDE.md bunları eksik araç olarak sayıyor. Bu üç dosya adı tur 2 dosyalarının hiçbirinde geçmiyor (grep: 0).
  - B2'nin ilk taslağı "renk cilalı" idi (H/proje-b2).
  - Kapak görselinin üretimi de sahipsiz.
- **Düzeltme:** Her işe bir sahip uzman, bir dosya adı ve bir P-önceliği atansın (§6).

### O-3 · Windows kurulumu teknik bilgisi az bir kullanıcı için fazla karmaşık

- **Kanıt:**
  - [UM2] §4.6.4'e göre kurulacaklar: ana Python 3.10, ayrıca `py -3.12`, dört ayrı sanal ortam, OpenMontage ve modeller.
    - Sanal ortamlar: `venv_rvc` (3.12), `venv_openvoice`, `venv_musetalk` (3.10 + torch 2.0.1), `venv_acestep` (3.11–3.12).
    - OpenMontage `mediapipe==0.10.14` sürümünde sabit kalmalı (BK §7 #11).
    - Modeller: YuNet, SFace, DINOv2, OWLv2, MuseTalk, ACE-Step, ayrıştırma ve ASR modelleri.
  - [GS2] R8: cp310 için son Windows torch tekerleği 2.9.1, onnxruntime ≤ 1.23.2. "`transformers` ve `mediapipe` sürüm uyumu bu belgede doğrulanmadı."
  - Disk: C'de ≥ 20 GB boş yer isteniyor [tahmin].
  - MuseTalk README'si Windows yönergesi veriyor ve 3050 Ti Laptop 4 GB'ta test edildiğini yazıyor. Ama mmcv'yi `mim install "mmcv==2.0.1"` ile kuruyor; mmcv'nin Windows'ta kurulumu kırılgandır (bellekten, doğrulanmalı).
  - FluidSynth ve SF2 ses fontları ayrıca kuruluyor ([SM2] §4.8.4).
  - Ana ortamda torch'un CPU mu CUDA mı olacağına kimse karar vermemiş ([GS2] R8).
- **Düzeltme:** Kurulum kademeli olsun:
  - **K1:** kâğıt + Flow + G1 (ana ortam, CPU torch).
  - **K2:** yalnız kazanan ses dönüştürme motoru (tek sanal ortam).
  - **K3:** MuseTalk ve ACE-Step, yalnız gerektiğinde.

  Her kademe bir "çalışıyor / çalışmıyor" kartı yazsın; eksik kademe yalnız kendi basamağını kapatsın. Bu ilke [UM2] R7'de hat için zaten var, aynı ilke kuruluma da uygulansın.

  Disk ihtiyacı kurulum raporunda ölçülerek verilsin. Model ve pip önbellekleri C'de bilinen tek bir klasörde toplansın (yolu `YOLLAR.json`'dan) ve boyutları raporda gösterilsin:
  - D harici bir USB disk ve "çalışırken kullanılmaz" kuralı var (BK §8 #21), bu yüzden önbellek D'ye taşınmaz.
  - Önbelleği temizlemek kullanıcının işidir, çünkü kalıcı silme Claude'a yasak (BK §6.5 #4).

### O-4 · Bulut/yerel ayrımı kullanıcıya git yüklüyor; kancalar bulutta uygulanmayabilir

- **Kanıt:**
  - [CM2] İ-2 ve R-12, D/settings alıntısıyla: "none of a repository's `.claude/settings.json` permission rules, hooks, or `env` apply" (bulutta proje iş parçacığı için).
  - [UM2] §4.5.14 `esitle`.
  - [UM2] R8: "kullanıcı git bilmiyor".
  - [UM2] R13: `--ff-only` çekişiyle çakışma.
  - [CM2] R-1: Claude yanlış klasörde açılabilir.
- **Düzeltme:**
  - İlk iki filmde her şey yerel çalışsın; bulut yalnız geliştirmede kullanılsın. `esitle` P2'ye alınsın.
  - Tek kök seçeneği tur 3'te bir kez daha tartışılsın: `.claude/` kullanıcının alıştığı klasörde (`Desktop\YZ_FILM`) durursa R-1 ve iki kök sorunu birlikte kalkar mı?

### O-5 · Lisans zinciri eksik ve dağınık

- **Kanıt:**
  - [GS2] R13'teki izinli liste iyi.
  - Ama kie.ai'ye uygulanan "gri havuz" şüphesi AI84 için tartışılmamış; AI84 de bir aracı ([SM2] R1; SV'ye göre kriptoyla alınmış).
  - RVC'nin ElevenLabs çıktısıyla eğitilmesinin hukuki durumu belirsiz ([SM2] §4.8.3).
  - ACE-Step'in "ağırlık sayfası bu oturumda açılmadı" ([SM2] §4.8.4).
  - FluidSynth'in LGPL olduğu ve SF2 fontlarının lisansı "bellekten" yazılmış ([SM2] §4.8.4).
  - MuseTalk'ın alt bileşenleri "kendi lisanslarıyla" geliyor ([SM2] §4.8.3).
  - BS-RoFormer ağırlıklarının lisansı belirsiz (bellekten, doğrulanmalı).
- **Düzeltme:**
  - `veri/LISANSLAR.json` dosyası açılsın. Her bileşen için tutulsun: sürüm, kod lisansı, ağırlık lisansı, kaynak bağlantısı, doğrulama tarihi, "ticari YouTube: evet / hayır / bilinmiyor".
  - `kurulum.py` "bilinmiyor" olan bileşeni ana hatta kurmasın; yalnız `--deneme` kipinde kursun.
  - Yayın paketine bir künye eklensin.

### O-6 · Karar 2 ve 3'ün bazı parçaları yalnız BAYRAK düzeyinde kalıyor, yani eksik uygulanıyor

- **Kanıt:**
  - [GS2] §4.7.3 G1 tablosu: "Açık parmak … B (asla tek başına H)". Karar 2 "kaç parmak açık" bilgisini açıkça istiyor.
  - Aynı tablo: "İnsan olmayan karakter … DINOv2 kırpıntı kosinüsü < 0,5 → B". Oysa serinin ana karakterlerinden biri bir ejderha (PA: Ember). Karar 3(c)'nin en önemli karakter için uygulanışı en zayıf hâlinde.
  - [GS2] §2.5: Z1 (gerçek son kare) yalnız `devam` geçişinde kullanılıyor; diğer geçişlerde başlangıç karesi "kurulumun ana karesinden türev". [UM2] §4.5.9'daki örnek JSON'da `"son_kare": 61` / 405 klip, yani ≈ %15 (örnek değer).
  - AR2 §2.3 #2, `kesme_ayni_mekan` için "son kare **referans** olarak Gemini görsel ajanına verilir" öneriyordu. Bu önerinin tur 2'de neden düştüğünü okuduğum bölümlerde bulamadım.
  - Ders terfisi ≥ 2 film istiyor ([UM2] §4.5.11). Bu yüzden ilk film hiçbir şey öğrenmeden üretilir.
- **Düzeltme:**
  - (a) Parmak sayımı ve yaratık kimliği için H'ye yükselme yolu tanımlansın. Kalibrasyon setinde ölçülen doğruluk ≥ %90 olursa bu ölçüler tek başına H verebilsin. Bugün böyle bir yol yok.
  - (b) Yaratık için DINOv2'ye ek olarak kart görünümlerinden kurulmuş bir "yaratık kimlik bankası" ve kör gözlemde iki soruluk tutarlılık denetimi eklensin.
  - (c) `eylem_kesme` geçişinde önceki klibin gerçek son karesi GS0'da A/B ile denensin. Kare başlangıç karesi olarak değil, **referans** olarak verilsin. Düşürülecekse gerekçesi karar defterine yazılsın.
  - (d) İlk filmde "deneme" durumundaki dersler aynı filmin sonraki partisine uygulanabilsin, yalnız sıkılaştırma yönünde.

### O-7 · Sesin ve müziğin hiçbir kulağı yok

- **Kanıt:**
  - [CM2] R-8: "Ajanlar ses duyamaz".
  - [SM2] `ses-tasarimcisi`: "Sesi duyamaz; yolu kod önerir" ([CM2] §4.3.2).
  - `dinleyici` isteğe bağlı ve tanımlı değil: [UM2] §4.5.12 `"dinleyici": []`, [SM2] §4.9.3 #10 "Gemini API anahtarı tanımlı değil".
  - Eskiden ses seçimini kullanıcı yapıyordu (BK §5.1 #7).
  - Kullanıcının en büyük iki ses şikâyeti öznel algıya dayanıyor: "ses klipten klibe değişiyor" ve "dudakla gitmiyor".
- **Düzeltme:**
  - `dinleyici` varsayılan olarak açık olsun (ses girdisi alan bir model; maliyet Aşama 0'da ölçülür).
  - `dinleyici` yoksa `ses-tasarimcisi`'nin seçimi kullanıcıya 30 sn'lik bir dinleme dosyasıyla bilgi olarak gösterilsin. [CM2] S-5 seçilen sesleri zaten son özette göstermeyi öneriyor. Kullanıcı itiraz ederse `film-not` ile eder.

### O-8 · Aynı model yazıyor ve yargılıyor; seyirci yalnız kare paketi görüyor; puanın YouTube ile ilişkisi bilinmiyor

- **Kanıt:**
  - [CM2] R-7: ARIS "hiçbir model kendi çıktısını onaylamaz".
  - ZN §7.3: 3 seyircinin üçü de Opus.
  - [KU2] R1: "Kare paketi izlemek değildir … Tutma verisi de yok".
  - [SN2] §4.1.3: Kâğıt ile kurgu puanı arasındaki fark yalnız karnede izleniyor, kapı değil.
  - B1'in YouTube sonucu ≈671 izlenme (PA). Bu sonucun seyirci puanıyla karşılaştırması hiçbir yerde yok.
- **Düzeltme:**
  - Seyircilerden en az biri farklı bir model ailesinden olsun. Gemini tasarımda zaten "ikinci göz" olarak var, seyirci olarak da kıyaslanabilir. Bu mümkün değilse en azından farklı bir sistem istemi ve effort kullanılsın.
  - İlk üç filmde YouTube Studio tutma verisi ile seyirci puanı arasındaki ilişki ölçülsün. İlişki yoksa puan kapısı kalksın, yalnız olgusal kapılar (KRİTİK kopukluk, özet eşleşmesi) kalsın.

### O-9 · Animatik G1'den sonra geliyor; bu pahalı bir sıra

- **Kanıt:**
  - [UM2] §4.1.3: A11 (başlangıç görselleri ve G1) 4–7 gün sürüyor, animatik (A12) 1–2 gün sonra geliyor.
  - [GS2] §4.8.3: "Animatik yalnız **G1'den geçmiş** karelerle kurulur".
  - [KU2] KR4: Hikâye bulgusu H15'e, oradan yönetmene, oradan da görselin yeniden üretimine gidiyor. Bu üretim 0 kredi ama Flow görsel yükü getiriyor (K-1).
- **Düzeltme:**
  - Animatiğin 1. turu ilk aday karelerle kurulsun: G1'den önce, yalnız kimlik HATA'sı elenmiş kareler. Kareler seyirciye "taslak" etiketiyle verilsin.
  - Böylece hikâye ve ritim bulguları G1 düzeltme turlarından önce gelir ve animatikte kesilecek planlar için düzeltme görseli üretilmez.
  - Taslak karenin seyirci puanını ne kadar düşürdüğü bir kez ölçülsün.

### O-10 · Ölçek ve takvim sayıları uzmanlar arasında tutarsız

- **Kanıt:**
  - Görsel düzeltme: [UM2] "116 gönderim / 6 gün", [GS2] "240 görsel / 12 gün". Biri gönderim, biri görsel sayıyor; ikiye çıktıyla yarıya inip inmediği belirsiz.
  - Gece: [UM2] §4.1.3 "2 gece" diyor, ama [UM2] §4.5.12'de `gece_izni: false` varsayılan.
  - 12,9 saat: 360p'de ≈40 sn'lik video süresine dayanıyor; 720p'de doğrulanmadı ([UM2] Q15).
  - Paket: [UM2] 18–24, [GS2] 10–13.
  - Ajan görevi: [CM1] 350–450, [UM2] 350–550. [GS2]'ye göre ≈175 `kare-tarifcisi` görevi bunlara ayrıca eklenmeli.
- **Neden önemli:** Varsayılan `elle` modda 527 GÖNDER ancak kullanıcının bilgisayar başında olduğu saatlerde yapılabilir. Görsel günleri de 12'ye çıkarsa takvim 3–6 haftaya uzayabilir (tahmin — benim).
- **Düzeltme:** Bütün bu sayıları aynı girdilerden tek bir araç hesaplasın: `olcek.py` ya da `kredi.py`'nin önizleme kısmı. Belgelerde sayı yerine "olcek.py çıktısı" yazılsın. Takvim varsayılan ayarlarla yeniden hesaplansın.

### O-11 · Disk sınırı ve silme yasağı birlikte düşünülmemiş

- **Kanıt:**
  - BK §6.5 #4: "Kalıcı silme Claude'a yasak".
  - BK §7 #10: Ara klasörler `robocopy /E /MOVE` ile D'ye taşınıyor.
  - [UM2] §4.6.4: "C'de ≥ 20 GB [tahmin]".
  - Hacim: her plana 2 aday, ≈1.200 G1 görseli ([GS2] §4.1.4), 405 klip ve yeniden çekimler, render önbellekleri, 4 sanal ortam ve modeller.
  - DR "Araç/işleyiş": "C diski dolar: biten işleri D'ye taşı; pip önbelleği 13 GB birikmişti."
  - BK §8 #21: D harici USB'dir, çalışma C'de yapılır.
- **Düzeltme:**
  - Kurulumda ve her aşama sonunda disk ölçülsün (`shutil.disk_usage`). Boş yer eşiğin altına düşünce kullanıcıya "BEKLE + `ARSIVLE.bat`" bilgisi verilsin.
  - Bitmiş partilerin eski sürümleri ve yeniden üretilebilir ara dosyalar (render önbelleği, eski 1080p türevleri) BK §7 #10 kuralıyla D arşivine taşınsın. Açık iş C'de kalır.
  - Belgelerdeki disk tahmini ölçülmüş bir değerle değiştirilsin. pip ve model önbelleklerinin boyutu da bu ölçüme girsin.

### O-12 · Gözetimsiz ve gece üretimi Claude'un uyanık olmasına bağlı

- **Kanıt:**
  - [GS2] R10: Z1 ardılları V3 kör gözlemini bekliyor. `claude_api` anahtarı yoksa sonraki oturuma kalıyor.
  - [UM2] §4.5.12: `usd_tavan_film: 0`, yani `claude_api` fiilen kapalı.
  - [CM2] §4.9.4 #2 (arka plan bildirimiyle uyanma) ve #11 (`claude --continue`) doğrulanmadı; ayrıca [CM2] R-5.
- **Düzeltme:**
  - Yedek planlama yazılsın: Bir Flow oturumuna girecek blokların bütün ön koşulları oturumdan önce hazır olsun.
  - Z1 ardılları aynı oturuma değil sonraki oturuma planlansın; V3'ü iki oturum arasında Claude işlesin.
  - Bedeli takvimdir. [UM2]'nin uygunluk kuyruğuyla bu yedeğin farkı S0-b'de ölçülsün.

### O-13 · YouTube yayın kuralları tasarımda yok

- **Kanıt:** Aşağıdaki iki konu tur 2 dosyalarında hiç geçmiyor (grep: "synthetic|altered|inauthentic|beyan" → 0):
  - YouTube'un gerçekçi görünen değiştirilmiş ya da sentetik içerik için yükleme sırasında beyan istemesi.
  - YPP'nin "özgün olmayan (inauthentic) içerik" politikası.

  İkisini de bellekten yazıyorum, doğrulanmalı. Kanal tamamen YZ ile üretiliyor ve anlatıcısız (BK §1.1). YPP eşiği de bir hedef (BK §1.1 #4).
- **Düzeltme:**
  - Yayın paketine bir "YZ beyanı" alanı ve bir politika kontrol listesi eklensin.
  - `yayin-paketcisi`'nin sahibi güncel politikayı resmî sayfadan okuyup `BILGI/YOUTUBE_POLITIKA.md`'ye kaynağıyla yazsın.

### O-14 · Karar 6 "ölçmeden kısma" yasağına dönüştürülmüş

- **Kanıt:** Karar 6 şu gerekçelerle anılıyor:
  - [CM2] §4.3.2: "Kesin karar 6 gereği kısılmaz" (ajan çağrısı bütçesi).
  - [KU2] R3: "Kesin karar 6 gereği seyirci sayısı ve tam izleme kısılmaz".
  - [GS2] öz 2: "'Yalnız riskli plana 2 aday' ve 'yalnız BAYRAK'a kör gözlem' kesin karar 6'ya aykırı".
- **Neden önemli:** Karar 6 "tasarruf için kaliteden ödün verilmez" diyor. Kalitede ölçülebilir fark yaratmayan harcamayı zorunlu kılmıyor. Ölçmeden "kısılmaz" demek de, ölçmeden "kısalım" demek de kanıtsızdır. Bugünkü yorumun bedelini K-1 (Flow yükü) ve K-3 (token) ödüyor.
- **Düzeltme:** Bir "karar 6 testi" tanımlansın:
  - Kısma ancak etiketli sette kalite farkı gürültü bandının içinde kalırsa yapılabilsin.
  - Karar defterine "ölçüm — fark — karar" yazılsın.
  - Aksi hâlde pahalı yol kalır.
  - Test şu kararlar için koşsun: model seçimi, aday sayısı, tam ya da kısmi izleme, ikinci göz.

### O-15 · Kanca komutları çıplak `python` çağırıyor; kullanıcının makinesinde bunun güvenilmez olduğuna dair bir ders var

- **Kanıt:**
  - [CM2] §4.6 settings.json: Bütün kancalar `"command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/…\""` biçiminde. Güvenlik kancalarında `"onFailure": "block"` var.
  - H/uretim-hatti-v2: ".bat'lar tam Python310 yolu kullansın". [UM2] S12 aynı dersi yineliyor.
  - [UM2] §4.6.4 ses ortamları için `py -3.12` kurulumunu istiyor. Bu kurulum PATH'teki `python`'u değiştirebilir (bellekten, doğrulanmalı).
- **Neden önemli:** `python` bulunamaz ya da yanlış sürüme giderse `erisim_kapisi` kapalı başarısız olur. Bu durumda bütün Read/Write çağrıları engellenir ve hat görünürde sebepsiz durur.
- **Düzeltme:**
  - Kanca komutunu kurulum `settings.local.json`'a mutlak Python yoluyla yazsın; yol `YOLLAR.json → python.ana`'dan gelsin. [CM2] K-13 bu dosyayı zaten üretiyor.
  - Kurulum testi kancaları gerçek bir araç çağrısıyla bir kez çalıştırsın (S0-a).

---

## 4. KÜÇÜK maddeler

**S-1 · `os.replace` Windows'ta kilitlenebilir**
- **Kanıt:** [UM2] S8 atomik yazımı `atomik_yaz()` ile çözüyor. Ama Windows'ta hedef dosya başka bir süreçte (antivirüs, Dropbox, editör) açıksa `os.replace` PermissionError verebilir (bellekten, doğrulanmalı).
- **Düzeltme:** `atomik_yaz()` kısa beklemeyle 3 kez yeniden denesin. Hata `FILM_KAYIT`'a yazılsın.

**S-2 · Kanca soğuk başlangıcı zaman yiyor**
- **Kanıt:** 11 kanca olayına bağlı 12 Python betiği var ([CM2] §4.6). Her ajanın her Read/Write çağrısında `erisim_kapisi` çalışıyor. Hedef "≤ 2 sn" ([CM2] R-3), Windows'ta doğrulanmadı ([CM2] §4.9.4 #8). Film başına ek gecikme 1–4 saat olabilir (tahmin — benim; ≈10–16 bin çağrı × 0,3–1 sn).
- **Düzeltme:** Kancalar tek bir `kanca.py` altında alt komutlar olarak birleşsin, içe aktarmalar tembel yapılsın. Gecikme S0-a'da ölçülsün.

**S-3 · Karar sorusunu metin kalıbıyla yakalamak kırılgan**
- **Kanıt:** [CM2] K-10 (a) ve §4.5.10 karar sorusunu metin kalıbıyla yakalıyor. Türkçe ek yapısı yüzünden hem yanlış pozitif hem kaçırma olur.
- **Düzeltme:** Önce kayıt ve uyarı (`kararlar/soru`), sonra engelleme gelsin. 50 örnek mesajlık bir test seti hazırlansın.

**S-4 · Ad tutarsızlıkları sürüyor**
- **Kanıt:**
  - Sağlayıcı türü: [GS2] `vlm`, [UM2] §4.5.12 `"gozlemci"`.
  - Ajan adı: [CM2] `kor-gozlemci` ile `kare-tarifcisi`'yi birleştirdi, ama [UM2] §4.3.5 hâlâ `kor-gozlemci` diyor.
  - Zincir yöntemlerinin `Z0/Z1/Z2` adları ZN'deki Z0–Z3 kapı adlarıyla çakışıyor. [UM2] İ-4 bu çakışmaya itiraz etti, [GS2] §2.5 hâlâ Z0/Z1/Z2 yazıyor.
- **Düzeltme:** `ADLAR.json` (O-1).

**S-5 · En düşük sürüm iki farklı sayı, sürüm sabitleme yok**
- **Kanıt:**
  - En düşük Claude Code sürümü [CM2] §4.7'de ≥ 2.1.302, [UM2] §4.6.4'te ≥ 2.1.271.
  - Sürüm sabitleme ya da otomatik güncellemeyi kapatma yok. Yeni bir sürüm davranışı değiştirirse güvence sessizce kalkar ([CM2] R-6).
- **Düzeltme:** Tek bir sayı belirlensin. Kurulumda sürüm kaydedilsin ve kanca nabzında sürüm tutulsun. Güncellemeden sonra `test_kancalar.py` çalışsın. Otomatik güncellemeyi kapatan ayarın adı bellekten `DISABLE_AUTOUPDATER`, doğrulanmalı.

**S-6 · YouTube yükleme onayı karar 1 ile gerilimli**
- **Kanıt:** M2'de "isteğe bağlı yükleme onayı" var. Ayrıca OAuth kurulumu teknik bilgisi az bir kullanıcı için zor ([UM2] Q8).
- **Düzeltme:** Varsayılan "yükleme yok" olsun; çıktı `YAYIN/` klasörü ve metinlerdir. Yükleme P2'ye alınsın.

**S-7 · Reklam yazılımı geçmişi Telegram anahtarını riskli kılıyor**
- **Kanıt:** BK §6.5 #3 reklam yazılımından sonra AI84 ve Telegram anahtarlarının yenilenmesini öneriyor. Tasarım ise Telegram'ı varsayılan açık kullanıyor ([UM2] §4.5.12).
- **Düzeltme:** Kurulum raporu anahtar dosyasının tarihine baksın. Dosya temizlik tarihinden eskiyse bilgi versin. İçerik okunmaz, yazdırılmaz.

**S-8 · Git Windows'ta isteğe bağlı olmayabilir**
- **Kanıt:** [UM2] Q7 "git yoksa yalnız yerel" diyor. Oysa Claude Code'un Windows'ta Git Bash istediğini düşünüyorum (bellekten, doğrulanmalı). [CM2] R-10 kanca komutunu da Git Bash'e bağlıyor.
- **Düzeltme:** Git kurulum ön koşulu olarak denetlensin. Yoksa kurulum raporu tek cümleyle ne yapılacağını söylesin.

**S-9 · `DEVAM.bat` iki ayrı biçimde tanımlanmış**
- **Kanıt:** [UM2] §4.6.3'te `DEVAM.bat` = `film.py calis`, [CM2] K-23'te `claude --continue "devam"` (doğrulanacak).
- **Düzeltme:** Tek bir tanım seçilsin. Önerim [CM2] biçimi; doğrulanamazsa `FILM_SETI.bat` ve "devam" talimatı.

**S-10 · Puan ortalamayla toplanıyor, konuşan adı habersiz pakete sızıyor**
- **Kanıt:**
  - `puan_oku.py` "ORTALAMA'ların ortalaması"nı alıyor (satır 5, 37); ZN §7.2 #10 ise medyan istiyor.
  - `izleme_paketi.py` satır 40 konuşanın adını `kim.upper()` ile habersiz pakete yazıyor. Ad ekranda kurulmadan seyirciye sızar ([SM2] İ-9).
- **Düzeltme:** Medyana geçilsin. Konuşan adı yerine ekranda kurulmuş tanım yazılsın ("ad henüz kurulmadıysa: 'yaşlı adam'").

---

## 5. Uzmanlar arası çözülmemiş çelişkiler

| # | Konu | Bir taraf | Öbür taraf | Önerim |
|---|---|---|---|---|
| Ç1 | Klasör adları | [YN2] `30_YONETMEN/`; [SM2] Ç-2 `35_SES/`; [GS2] GS9 çıktısı `30_YONETMEN/ONARIM_<tur>.json` | [CM2] İ-7, Ç-1: `_YONETMEN/`, `_SES/` | `ADLAR.json`, tek karar sahibi |
| Ç2 | `memmet-bakimci` yetkisi | [UM2] §4.3.3: `Read, Edit, Write`, `memmet.py`'ye yazar | [CM2] İ-3: yalnız `CIKTI/memmet_yama.diff` yazar, korkuluk testinden geçer | [CM2] biçimi; karar 5'e en yakın olan bu |
| Ç3 | Derslerin ajana verilişi | [UM2] §4.5.11, [GS2] §4.8.7, [SN2] §2.8 (SubagentStart kancası ya da brifing) | [CM2] İ-5: yalnız GIRDI'de, imzaya girer | GIRDI; öbür üç belge güncellensin |
| Ç4 | Ders defterinin yeri | [UM2] `YZ_FILM/BILGI/DERSLER/ham/<zaman>_<film>_<olay>.json` | [GS2] `YZ_FILM/BILGI/DERS_DEFTERI/`; [SN2] `BILGI/DERS_DEFTERI.jsonl` | Olay başına dosya ([UM2]), tek yer |
| Ç5 | Aşamalı okuma | [SN2] İ6, [KU2] §2.6: SendMessage | [CM2] İ-4: SubagentStop `block` | S0-a ölçsün; kazanan birincil olsun |
| Ç6 | Repliğin ton alanı | [YN2] İ-12: tek alan `replik.ton_fiili` (serbest İngilizce dize); `teslim` alanı kaldırıldı | [SN2] `replik.teslim` (5 değer); [SM2] Ç-1 ve §4.9.2 #2: `teslim` yazılır, `_derlenir.ton_fiili_en` ve `seviye` türetilir | [SM2] önerisi: sözlüklü `teslim`; seviye ve TTS etiketi aynı sözlükten türer |
| Ç7 | Z1 karesinin boyutu | [YN2] §4.8.2(d): "1280×720 → 1376×768 Lanczos" | [GS2] İ-7: 1280×720 doğal; büyütme yalnız oran korunarak ve GS0'da | [GS2]; S0-b'de ölçülsün |
| Ç8 | Kurulumda soru | [UM2] Q9: "kurulumda bir kez sorulur" | [CM2] İ-9: soru yok, `GECE_IZNI.bat` bilgisi | K-2 #2: tur 3 kararı |
| Ç9 | `DEVAM.bat` | [UM2] §4.6.3: `film.py calis` | [CM2] K-23: `claude --continue "devam"` | S-9 |
| Ç10 | En düşük sürüm | [UM2] §4.6.4: ≥ 2.1.271 | [CM2] §4.7: ≥ 2.1.302 | S-5 |
| Ç11 | Gözlem sağlayıcısının adı | [GS2] `vlm` | [UM2] §4.5.12 `gozlemci` | `ADLAR.json` |
| Ç12 | Kör gözlemci ajanın adı | [UM2] §4.3.5 `kor-gozlemci` | [CM2] §4.3.2 `kare-tarifcisi` | `kare-tarifcisi` |
| Ç13 | Düzeltme görseli hacmi | [UM2] ≈116 gönderim / ≈6 gün | [GS2] ≈240 görsel / ≈12 gün | O-10, `olcek.py` |
| Ç14 | Kullanıcı paketi sayısı | [UM2] 18–24 | [GS2] R7: 10–13 | O-10 |
| Ç15 | Gece varsayımı | [UM2] §4.1.3: "2 gece" | [UM2] §4.5.12: `gece_izni: false` | Takvim varsayılanla hesaplansın |
| Ç16 | KRİTİK reddinin dört şartı | [SN2] §4.3 ve [KU2] §4.3: doktor/hakem reddi | [CM2] İ-8, Ç-4: dört şart, kabul bekleniyor | Tur 3; S16 betikle kanıt |
| Ç17 | Z0/Z1/Z2 adları | [GS2] §2.5: zincir yöntemleri | [UM2] İ-4: ZN'deki Z0–Z3 kapılarıyla çakışıyor | Kodda `bagimsiz/son_kare/bitis_sabit` |
| Ç18 | Kadro sayısı | [GS2] §4.9.2 #2: "15 + 1 ajan" | [CM2] §4.3.2: 21 ajan | [CM2] |
| Ç19 | Toplam ajan görevi | [CM1] 350–450; [UM2] 350–550 | [GS2]: +175 `kare-tarifcisi` eklenmeli | K-3: ölçüm |
| Ç20 | 40 dk için klip sayısı | ZN §2.6: 405 | BK §3 #5 (CLAUDE_ICIN): 250–300 | Aralık olarak verilsin (K-1) |

---

## 6. Sahipsiz işler

| # | İş | Kanıt | Önerilen sahip |
|---|---|---|---|
| 1 | Renk eşleme (`renk_cila.py`) | CLAUDE.md eksik araçlar listesi; tur 2'de dosya adı geçmiyor (grep 0); B2 taslağı "renk cilalı" idi (H/proje-b2); [KU2] §4.8.2'de yalnız "renk cilası ayarı" şablonu var | Kurgucu (araç) + görüntü (ΔE ölçüsü [GS2]'de hazır) |
| 2 | Dikey Short MP4 (`shorts_mp4.py`) | Dosya adı geçmiyor; [KU2] yalnız pencereleri seçiyor; BK §3 #10: 9:16, 30–60 sn, ilk 2 sn kanca | Kurgucu |
| 3 | Jenerik görüntüsü (`jenerik.py`) | Dosya adı geçmiyor; metni `yayin-paketcisi` yazıyor ([CM2] §4.3.2) | Kurgucu |
| 4 | Kapak görselinin üretimi | [CM2] A17'de yalnız `kare-tarifcisi` (kapak adaylarının denetimi) ve `juri-uyesi` (seçim) var; görseli kimin ürettiği yazılı değil | Görüntü (üretim) + yayın (kalıp) |
| 5 | YouTube YZ beyanı ve politika denetimi | Tur 2'de hiç geçmiyor (O-13) | Yayın |
| 6 | memmet3'ün depoya aktarımı | [UM2] S6, Q6: "yerel Claude kopyalar"; tarih ve sorumlu yok | Üretim |
| 7 | B3'ün 44 karesinin etiket JSON'u | [GS2] §4.9.3 #7, [UM2] Q11 | Görüntü |
| 8 | Ana ortamda torch CPU/CUDA kararı | [GS2] R8 | Üretim (kurulum) |
| 9 | Kullanıcı belgelerinin içeriği ve testi | [UM2] §4.6.3: `BASLA_BURADAN.txt` "yeniden yazılır"; içerik ve kabul ölçütü yok | Üretim + K-2 kartı |
| 10 | Token ve kullanım ölçümü | Hiçbir uzman alanına almamış (K-3) | Claude Code mimarisi |
| 11 | Flow kapasite ölçümü | [UM2] Q14: "17–19.10 kayıtları okunur"; ölçüm planı yok | Üretim (S0-b) |
| 12 | Lisans defteri | Bilgiler dağınık (O-5) | Üretim |
| 13 | Gemini kotası | [UM2] Q16: "kurulumda küçük denemeyle"; sahibi yok | Görüntü (S0-e) |
| 14 | Kurulum izin kartı (karar 1'in yorumu) | Ç8 açık | Tur 3 bütünleştiricisi |
| 15 | "Elle dinleme notları" | [SM2] İ-3: M2 listesinde yok, kimin yapacağı yazılmamış | Ses (ya da çıkarılsın) |
| 16 | `durdu` planın filmdeki karşılığı | [GS2] GS9: "plan `durdu` olur ve kullanıcıya bilgi verilir"; filmde bu planın yerine ne geleceği tanımsız | Kurgucu (0 kredi çözümü zorunlu) |

---

## 7. Döngü tavanı denetimi

Soru: Her kalite döngüsünün bir üst sınırı var mı, ve sınır dolunca ne oluyor?

| Döngü | Tavan | Kanıt | Açık kalan yol | Önerim |
|---|---|---|---|---|
| Kâğıt seyirci | 4 normal + 2 doktor + 4 ikinci öneri = 10 tur, sonra DUR | [SN2] §2.6, S8 | DUR'dan sonrası kullanıcıya kalıyor (K-2) | K-2 #5; küresel bütçe |
| İlk 2 dk testi | 3/3 şartı; üçüncü sürüm en çok 2 tur | [SN2] H12 | Sonrası tanımsız | Tavan + "en iyi sürüm" |
| H15 dar değişiklik | Yok; "en çok 1 kez (tahmin)" yalnız karnede | [SN2] H15, §4.1.3 | Her animatik ve kurgu turu yeniden tetikleyebilir | Film başına ≤ 2 (tahmin — benim) |
| Kart (GS4) | 2 CORRECTION turu, sonra tarif değişir; tarif değişikliğinin tavanı yok | [GS2] GS4 | Tarif → aday → kapı → tarif | Tarif revizyonu ≤ 2; sonra `kart_secimi` en iyi teknik adayı seçer |
| Kart tarifi (GS2) | "En çok 2 düzeltme, sonra görev `gecersiz`" | [GS2] GS2 | `gecersiz`'den sonra ne olacağı yazılı değil | `gecersiz` → yönetmen ya da senarist |
| G1 (GS9) | 2 tur → kaçış → yönetmen onarımı → GS5'ten yeniden → `durdu` | [GS2] GS9 | `durdu` planın filmde karşılığı tanımsız | §6 #16 |
| Video yeniden çekimi | Plan başına en çok 2 | [SM2] §4.8.3; [KU2] §2.5 | Bölmeden sonraki sayaç belirsiz ([YN2] Y9-c) | Sayaç planın soyuna bağlı, toplam ≤ 3 |
| Animatik | 3 + 2 tur → DUR (video kapalı) | [KU2] KR4 | Var | Tamam; küresel bütçeye bağlansın |
| Kurgu | 3 + koşullu 2 tur → teslim; KRİTİK + kredi yok → DUR | [KU2] KR9, §2.5 | Kredi beklemesinin süresi tanımsız | Bekleme bilgisi + projeksiyon |
| SubagentStop düzeltmesi | ≤ 2 | [KU2] KR4 #3; [GS2] GS2 | Var | Tamam |
| Stop kancası devamı | 8 ardışık; araç çağrısında sıfırlanıyor | [CM2] K-10 | Toplam tüketime tavan yok | Film token bütçesi (K-3) |
| Flow uyarısı → `UYARI_GECTI` | Kullanıcıya bağlı | [UM2] İ-8 | Her uyarı yeni bir döngü; sayı sınırsız | Aynı hafta içinde ≥ 2 uyarı → o hafta Flow kapalı (tahmin — benim) |
| Ders defterinin sıkılaştırması | Yalnız sıkılaştırır | [UM2] §4.5.12; [GS2] §4.7.10 | Mandal etkisi | K-5 #5 |
| Kesme turu | Yalnız 1. turda | [KU2] KR4 | Var | Tamam |

---

## 8. Kesin kararların uygulanışı

| Karar | Durum | Kanıt | Eksik ya da ihlal | Madde |
|---|---|---|---|---|
| 1. Yalnız konu sorulur | Kısmen | [UM2] M1/M2; [CM2] İ-9; [SN2] §2.6 | Fiziksel iş, DUR'dan sonra kullanıcı kararı, "kurulum ayarı" | K-2 |
| 2. Atomik eylem zinciri | Büyük ölçüde | [YN2] §4.8.1 | Parmak sayısı yalnız B; saniyeli uyum ölçülmedi | O-6, K-4 |
| 3a. Videodan önce animatik + seyirci | Var | [UM2] §4.8.3 (T4 imzası) | Animatik G1'den sonra geliyor (pahalı sıra) | O-9 |
| 3b. Dünya defteri + zıplama denetimi | Var | [GS2] GS5, [YN2] §4.5.13 | — | — |
| 3c. Referansla yüz kontrolü | Kısmen | [GS2] §4.7.3 | Yaratık yalnız B; SFace sinematik karede ölçülmedi | O-6, §9 |
| 3d. Kare zinciri | Kısmen | [GS2] §2.5; [UM2] §4.5.9 örneği | Yalnız `devam` geçişinde (≈ %15) | O-6 |
| 3e. Kendi kendine öğrenen ders defteri | Var ama yavaş ve mandallı | [UM2] §4.5.11 | Terfi ≥ 2 film; yalnız sıkılaştırır | K-5, O-6 |
| 3f. Kalıcı seri evreni | Var | [UM2] §4.8.3 (f), [GS2] §4.5.1 | — | — |
| 4. Ses ve dudak: en iyi yol | Seçildi, ölçülmedi | [SM2] §4.8.3 | "kıyasla ölçülecek" | K-4 |
| 5. Memmet seri üretim aracı değil; uyarıda dur | Tasarımda var, kodda ihlal | `memmet.py` satır 58, 167–176; [UM2] S1/S1b/S6 | Hesap değiştirme yasağı yazılı değil | K-6, K-1 |
| 6. Üstün körü iş yok | Aşırı yorum riski | [CM2] §4.3.2; [KU2] R3; [GS2] öz 2 | Ölçmeden "kısılmaz" deniyor | O-14 |

---

## 9. Kanıtsız ya da çelişkili sayılar

| Sayı | Nerede | Sorun | Önerim |
|---|---|---|---|
| RE'deki 148 anahtar | RE | Kaynak ya da "tahmin" etiketi yok; "[kaynak: RE]" atfı döngüsel | Zorunlu `kaynak` alanı (K-5 #3) |
| GENEL ≥ 8; ilk 2 dk 3/3 | ZN §7.3, §7.2 #2; [SN2] S1, S5 | Geçmişte hiç tutturulmadı; kullanıcının "süper" dediği sonuç 7 idi | Gölge kip (K-5 #1) |
| 495 plan / 405 klip | ZN §2.6 | BK §3 #5: 250–300 klip; B2'den ölçekleme ≈650 plan / ≈440 klip (tahmin — benim) | Aralık olarak verilsin |
| Kapı payı 0,30 | [KU2] §2.5; [UM2] §4.1.3 | B2'deki gerçek oran ≈ %37 ([UM2] M7); V3 daha sıkı | Pilotta ölçülsün; aralık |
| 12,9 saat Flow süresi | [UM2] §4.1.3 | 360p'de ≈40 sn'ye dayanıyor; 720p doğrulanmadı ([UM2] Q15) | S0-b |
| 20 görsel/gün; görselden videoya 12 saat | [UM2] §4.5.12; [GS2] §4.9.3 #10 | Tek bir olaydan (≈40 görsel) türetilmiş | S0-b |
| 350–550 görev | [UM2] §4.3.6; [CM2] R-2 | Token karşılığı yok; en kötü durum dahil değil | K-3 |
| 2–3 hafta takvim | [UM2] öz 6 | Gece modu varsayımına dayanıyor; varsayılan `elle` | Ölçümden türetilsin; 3–6 hafta olabilir (tahmin — benim) |
| Claude Code sürüm numaraları ve davranışları | [CM2] §4.7, §4.9.4 | WebFetch özetinden; Windows'ta sınanmadı | S0-a |
| SFace 0,363 / 0,45 | AR2 §6.2; [GS2] R1, §4.7.10 | 0,363 gerçek fotoğraflar için resmî eşik; 0,45 tahmin; sinematik YZ karede ölçülmedi; HATA eşiği "0,363'ün altına inemez" | GS0; karakter başına bant düşük benzerlikli karakterde (sakal, kask, karanlık) kalıcı HATA üretiyorsa bu bir tasarım bulgusu olarak raporlansın |
| ≈3M token (kör gözlem) | [GS2] §4.1.4 | Yalnız görsel girdisi; çıktı ve yeniden okuma yok | K-3 #1 |
| MuseTalk ≈5 dk / 8 sn klip | [SM2] D-MT | README'de Gradio demosu, Windows + 3050 Ti Laptop 4 GB, fp16 (bu oturumda README notunda okundu); hattın kendi akışında ölçülmedi | S0-c |
| Kör görev boyu ≤ 12 görsel | [CM2] §4.3.2; [GS2] | Tahmin; GS0 ölçecek | Tamam |
| AI84 ses dönüştürme ≈2.000 kredi/sn | BK §6.4; [SM2] §4.8.3 | "tahmini"; `estimate` ile ölçülecek | Tamam (işaretli) |
| Film token maliyeti ≈63–462 $ (API yolu) | Bu belge, K-3 | Benim kaba hesabım | S0-f ile değiştirilsin |

---

## 10. Önerilen yol: önce ölç, sonra yaz

### 10.1 Aşama 0: ölçüm denemeleri

Süre ≈1–2 hafta (tahmin — benim). Flow ölçümü ayrı günlere yayılmak zorunda olduğu için en uzun kalem odur.

| Deneme | Ne ölçülür | Kredi / para | Devam ya da dur ölçütü (önerim) |
|---|---|---|---|
| S0-a Claude Code (Windows) | [CM2] §4.9.4'teki 11 davranış; kanca süresi (S-2); `claude --continue`; alt ajan sonucundan kullanım bilgisinin okunması; mutlak Python yoluyla kanca (O-15) | 0 | Habersizlik ve "uyarıda dur" kancaları tutmazsa mimari sadeleşir: kanca yerine betik kapısı |
| S0-b Flow / Omni | 3 ayrı günde ≤ 20 video/gün, `elle` mod, 17.10 temposu. Ölçülenler: uyarısız gönderim sayısı; `aralik` ve `sira` istem biçimlerinde V3 tutma oranı; 720p üretim süresi; politika reddinin kredi yakıp yakmadığı; 1280×720 Z1 karesinin kalitesi | B3'ün kalanından 10–40 klip ≈ 120–480 kredi (12 kr/klip; hesap). Bu klipler B3'ün zaten çekeceği kliplerdir | Uyarısız günlük kapasite < 30 → ilk film 30 dk ve takvim yeniden hesaplanır. V3 tutma < %60 → adım sayısı 2'ye iner ve Z2 planı devreye girer (iki eşik de tahmin — benim) |
| S0-c Ses | Arşivdeki Veo klipleriyle OpenVoice V2 ve Chatterbox dönüşümü; MuseTalk 1.5 kurulumu ve 1 klip; ACE-Step süresi | 0 | Dönüşüm kalitesini kimin yargılayacağı (O-7) çözülmeden ana yol kilitlenmesin; çözülemezse ana yol `tts` + seçici `tts_dudak` |
| S0-d CapCut | pycapcut ile klon, segment taşıma, taslak şifreleme | 0 | Taslak şifreleniyorsa yayın kaynağı `master` (ffmpeg) olur |
| S0-e Gemini | 1 paket; plan başına 3 aday; AI Studio kotası ve fiyatı | 0 ya da küçük bir dolar tutarı | Kota yetiyorsa paketler API'ye geçer; yetmiyorsa M2 sayısı kesinleşir (K-2) |
| S0-f Token | Gerçek kullanımla 1 kâğıt turu (3 seyirci + eşleştirici) ve 1 `kare-tarifcisi` görevi; Sonnet ve Opus kıyası (K-3 #3) | Abonelik | Projeksiyon abonelik penceresine sığmazsa model ve kip kararı verilir (O-14 testi) |

Çıktı `_RAPOR/ASAMA0.json` olur: her deneme için ölçüm, karar ve gerekçe. P0 listesi bu rapora göre yeniden yazılır.

### 10.2 İlk film (en küçük çalışan sürüm)

- **Süre:** 30 dk. Bu RE'nin alt sınırı ve [SN2] §2.5'teki karar kuralına uyuyor. Kapasite ölçümü izin veriyorsa 40 dk.
- **Altı özelliğin her biri asgari ama gerçek hâliyle bulunur:**
  - (a) Animatik ve 3 seyirci. İlk tur G1'den önceki aday karelerle yapılır (O-9).
  - (b) `dunya_defteri.py` ve K0.
  - (c) İnsanlar için SFace, yaratıklar için DINOv2 (yaratıkta sonuç B).
  - (d) Z1, yalnız `devam` geçişinde.
  - (e) Olay başına ders kaydı; terfi yok, ama aynı filmde sıkılaştırma yönünde "deneme" ders uygulanabilir (O-6 d).
  - (f) EVREN kaydı.
- **Kapılar:** Hattı yalnız olgusal kapılar durdurur: şema, filtre, kimlik HATA'sı, KRİTİK kopukluk ve özet eşleşmesi. Puan kapıları gölgede çalışır (K-5 #1).
- **Diğer ayarlar:**
  - Memmet `elle` modda ve acil yamayla (K-6) çalışır.
  - Bulut kapalıdır (O-4).
  - Yalnız 1. kademe kurulum yapılır (O-3).
  - Kullanıcı sözleşmesi kartı yazılır (K-2).
- **Kod:** P0'lar bu sürüme göre yeniden süzülür; geri kalanı P1 ya da P2 olur.

### 10.3 Genişleme

İlk iki filmin ölçümleriyle şunlar ayarlanır: eşikler, model ve effort, aday sayısı, gece izni, Z1'in kapsamı ve dinleyici. Her genişleme "karar 6 testi"nden geçer (O-14).

---

## 11. Tur 3'te karara bağlanması gerekenler

1. **Karar 1'in yorumu:** Kurulumda tek bir izin ekranı olacak mı, hiç olmayacak mı (Ç8)? DUR'dan sonra ekip varsayılanı ne olacak (K-2 #5)?
2. **Hesap değiştirme yasağı:** Açıkça yazılacak mı (K-1 #4)?
3. **Ad sözlüğü:** `ADLAR.json`'un sahibi ve Ç1–Ç20'nin tek tek kararı.
4. **`memmet-bakimci` yetkisi** (Ç2) ve memmet3 aktarımının sahibi ile tarihi (§6 #6).
5. **Aşamalı okuma mekanizması** (Ç5): S0-a'nın sonucuna bağlanması.
6. **KRİTİK reddi şartları** (Ç16).
7. **Puan kapıları:** İlk iki filmde gölge kipte çalışacaklar mı (K-5 #1)?
8. **Model seçimi:** Her yerde Opus·high mı, ölçüme dayalı mı (K-3 #3, O-14)?
9. **Animatiğin yeri:** G1'den önce mi, sonra mı (O-9)?
10. **Bulut:** İlk filmde bulut modu kapalı olacak mı (O-4)?
11. **İlk filmin süresi:** 30 dk mı, 40 dk mı? Kapasite ölçümüne bağlanacak mı (K-1 #2)?
12. **Dinleyici:** Varsayılan açık mı olacak, yoksa kullanıcıya dinleme dosyası mı gösterilecek (O-7)?
13. **Aşama 0:** P0 kodundan önce yapılacak mı (K-4, §10.1)?

---

*Bu belgenin sınırları:*
- [SM2], [KU2], [SN2] ve [YN2]'nin okumadığım bölümlerinde bazı maddeler çözülmüş olabilir.
- "(tahmin — benim)" işaretli bütün sayılar kaba hesaptır ve ölçümle değiştirilmelidir.
- "(bellekten, doğrulanmalı)" işaretli bilgilerin kaynağı bu oturumda açılmadı.
