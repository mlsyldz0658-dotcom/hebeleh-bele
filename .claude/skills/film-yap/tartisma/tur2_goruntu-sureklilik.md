# Tur 2 — Görüntü ve süreklilik uzmanı: itirazlar, çakışmalar, revize nihai öneri

Hazırlayan: görüntü-süreklilik uzmanı (Claude Opus 5.5). Tarih: 23.10.2026. Durum: TAMAM (2. tur).

**Bu turda okunanlar:**
- `tartisma/` altındaki yedi tur 1 dosyasının tamamı (kendi dosyam dahil).
- Benden önce yazılmış `tur2_yonetmen.md`, `tur2_kurgucu.md`, `tur2_senarist.md`, `tur2_ses-muzik.md`. Bana yöneltilen itirazları cevaplamak ve aynı alan adlarını kullanmak için okundu.
- Yeniden açılan dayanaklar: `arastirma/02_sureklilik.md` §2.3 ve §6.2, `ritim_esikleri.json` (anahtarlar betikle listelendi), `HAFIZA_YEDEGI/gemini-ajan-gorsel.md`, `.claude/agents/sureklilik-denetcisi.md`, `saglayicilar/__init__.py`.

**Dosya kısaltmaları:** `[GS1]` benim tur 1 dosyam · `[YN1]`/`[YN2]` yönetmen tur 1/tur 2 · `[KU1]`/`[KU2]` kurgucu · `[SN1]`/`[SN2]` senarist ·
`[SM1]`/`[SM2]` ses-müzik · `[UM]` üretim mühendisi · `[CM]` Claude Code mimarisi.

**Kaynak kısaltmaları (tur 1 ile aynı):** `02§6.2` = `arastirma/02_sureklilik.md` bölüm 6.2 · `01§B4` = `arastirma/01_film_hatlari.md` ·
`03§A2` = `arastirma/03_ses_ve_claude_code.md` · `ZAN§3.7` = `ZANAAT.md` · `RE:anahtar` = `ritim_esikleri.json` · `BK§4.1` = `BILGI_KURALLARI.md` ·
`DERS` = `FILMLE ILGILI CLAUDE/03_DERSLER.md` · `HAT` = `01_URETIM_HATTI.md` · `FK` = `YZ_FILM/BILGI/FLOW_KESIF.md` · `YR` = `YAPIM_REHBERI.md` ·
`H/<ad>` = `HAFIZA_YEDEGI/<ad>.md`.

**Sayı etiketleri:** kaynaklı sayının yanında kaynağı yazar · **(hesap)** = kaynaktaki sayılardan türetildi ·
**(tahmin)** = kaynağı yok; kalibrasyon partisinde (§4.9.4) ve ders defteriyle ayarlanacak başlangıç değeri.

**Adım kodlarım:** tur 1'deki `A1–A17` bu turda **`GS1–GS17`** oldu, çünkü [CM]'nin hat aşamaları `A00–A18` adını taşıyor.
Kapı adları değişmedi: **K0** (kâğıt süreklilik), **KART**, **G1** (başlangıç karesi), **G1Z** (zincir karesi), **K1Ö** (başlangıç kareleri dizisi),
**V1** (teknik video), **V2** (klip içi), **V3** (bitiş durumu), **K1** (kurgu sırası geçişi). [KU2] kendi adımlarını `KR0–KR12` yaptı; çakışma kalmadı.

### Bu turun özü (6 satır)
1. **Kare zinciri kullanıcının (d) kararıyla aynen kurulur:** `devam` geçişinde başlangıç, önceki klibin **kurguda kullanılan kesme anındaki gerçek karesidir** (Z1). Teknik son kare (`ffmpeg -sseof`) ve "Bitir varsayılanı" hiçbir yerde kullanılmaz. [YN2] ve [KU2] aynı noktada; [UM] ve [CM] düzeltilmeli.
2. **Her plan 2 aday, her aday tam G1:** yerel ölçüm + kör gözlem + kod kararı. "Yalnız riskli plana 2 aday" ve "yalnız BAYRAK'a kör gözlem" kesin karar 6'ya aykırı. Hakem yalnız tek kaynaklı BAYRAK'ı çözer; HATA'yı GEÇ'e çeviremez. İki turda düzelmeyen planı yönetmen değiştirir.
3. **Durum yalnız olgudur** ([YN2] İ-1'i kabul ediyorum): kadraj konumu, sıra, bakış ve ışık yönü `kroki.py` ile `_derlenir`'e hesaplanır. Defteri tek araç (`dunya_defteri.py`) tutar; sahibi benim, çözüm kurallarının şartnamesi [YN2] §4.5.13.
4. **Kör gözlem gerçekten kör olur:** ajanın adı [CM]'nin `kare-tarifcisi`'si; sorular iki aşamalıdır (önce serbest envanter, sonra gözlemcinin kendi kişi kimlikleri üzerinden **görüntü koordinatında** hedefli sorular). Anatomik sol/sağı ve kişi eşlemesini kod yapar.
5. **Kartlar plan yazımıyla paralel üretilir ve istem derlemeden önce kilitlenir.** Kimlik dizesi ad içermez; ad değişirse kart bayatlamaz. Kroki yönetmenindir; ben plakaların görselini ve "görünmesi gereken öğeler" denetimini üstlenirim.
6. **Düzeltme görselleri kullanıcıya paket olarak gitmez** (kullanıcının 18.10 kuralı): ücretli API izni varsa API, yoksa Memmet/Flow; görsel günü video gününden ayrıdır. Gemini yalnız "ikinci göz" olarak bulgu verir, onay vermez.

---

## 1. Diğer önerilere itirazlarım (dosya + madde + neden + önerim)

★ işaretli üç madde en önemli itirazlarımdır.

### ★ İ-1 · [UM] §2.2 V05, §2.3 U04, §5.5 `zincir.yontem`, §8.3-d tablosu ve §9.2 C5 · [CM] §8 Karar 3 (d) `son_kare.py` · [YN1] §8.2-d Mod A · 02§2.3 — Kare zincirinin "Bitir varsayılanı" ve "teknik son kare" ile kurulması
- **Ne yazılmış:**
  - [UM]: `devam`'da `bitis_karesi` varsayılan (N+1'in planlanmış görseli N'nin Bitir yuvasına konur), `son_kare` yedek. "`zincir.yontem = son_kare` olan planlar V05'te üretilmez." U04: "önceki klibin son karesi çıkarılır → **hızlı G1**". `zincir.py`: `ffmpeg -sseof -0.1 … -frames:v 1`.
  - [CM]: `son_kare.py` (`ffmpeg -sseof`, AR2 §2.3).
  - [YN1]: Mod A varsayılan (bu öneri [YN2] İ-2'de geri çekildi).
  - 02§2.3 aynı `-sseof -0.1` komutunu öneriyor; yukarıdaki önerilerin kaynağı bu.
- **Neden yanlış:**
  1. **Kesin karar 3(d) sözcüğü sözcüğüne:** "kare zinciri (son kare → sonraki klibin başlangıcı)". Bitir varsayılanı bunun tersidir: sonraki klibin planlanmış başlangıcı öncekinin sonuna dayatılır. Karar tartışılmaz; tartışılan yalnız nasıl en iyi uygulanacağıdır.
  2. **Teknik son kare güvenli pencerenin dışındadır.** Veo klibinin son 0,5–1,0 sn'sinde kayma ve morf riski var (ZAN§2.2); RE `kullanim_son_pay_sn` = 0,5. Kurguda kullanılan son kare o değildir. Zincir seyircinin hiç görmediği bir kareden kurulursa dikiş seyircinin gördüğü yerde garanti edilmez ([KU2] §4.8 (d) aynı gerekçeyi kurgu açısından veriyor). 02§2.3'teki komut ZAN§2.2 ile çelişiyor; 02 içinde düzeltilmeli.
  3. **Bitir karesine klibin 8,0 sn'sinde ulaşılır.** Kesme anı ise [YN2] Y55'e göre "son adım bitişi + ≥ 0,2 sn" ile "klip_sn − 0,5" arasındadır. Bitir'le kurulan dikiş bu anda tutmayabilir.
  4. **"Hızlı G1" kesin karar 6 ile çelişir.** Zincir karesi de kimlik, kişi sayısı ve bitiş durumu ölçümünden geçer (G1Z). Hız ancak ölçüm atlanarak elde edilir.
  5. **Planlanmış görsel üretilmezse** animatikte delik kalır ve zincir karesi G1Z'den geçemezse düşülecek yedek olmaz ([YN2] İ-2 ile aynı).
  6. [UM]'nin gerekçesi (paralel üretim) kalite değil **süredir**. Kesin karar 6 bu takası açıkça belirliyor.
- **Önerim** (ayrıntı §2.5 ve §4.8.6):
  - `devam` → **Z1**: önceki klibin, [KU2] `kirp_oner.py --zincir` penceresinden (Y55) `kare_zinciri.py --cikar` ile seçilen en durgun, en keskin, kimliği en yüksek **gerçek** kare. G1Z'den geçer.
  - **Z2** (Bitir) hedefli kullanılır ([YN2] Y56): önceki klipte durum değiştiren fiziksel adım varsa ve yeniden çekimde V3 tutmadıysa. Konuşmalı planda yok.
  - **Her plana planlanmış görsel üretilir** (Z1 planları dahil); animatikte ve yedek olarak kullanılır.
  - Teknik son kare hiçbir araçta kullanılmaz. `zincir.py` ve `son_kare.py` önerileri `kare_zinciri.py`'ye birleşir.
  - Süre bedeli **akış içi dalga** ile küçültülür: Z1 ardılı, kaynağı V1 + V2 + V3 + G1Z'den geçer geçmez gönderim kuyruğuna girer; bütün dalganın bitmesi beklenmez (DAG yalnız sıra içindir, hız için değil, 01§B6).
  - [UM] U03 ve §8.2'deki "klibin son karesi ↔ `bitis_durumu`" karşılaştırması da **kesme anındaki kareyle** yapılır (V3).

### ★ İ-2 · [UM] §2.2 V05 "`risk` işaretli planlara 2 aday" ve §9.1 R6 "önce yerel ölçümlerle süz, yalnız BAYRAK'lar VLM'e" · 02§6.2 G1 #8 — Aday sayısının ve kör gözlemin örneklemeye indirilmesi
- **Ne yazılmış:**
  - [UM] V05: yalnız `risk` işaretli planlara 2 aday; diğerlerine 1.
  - [UM] R6: yerel ölçüm temiz derse görüntü-dil modeline (VLM) gidilmez; yalnız BAYRAK'lar gider. Dayanağı 02§5 ve 02§6.2 G1 #8 ("VLM son söz: BAYRAK'ların hepsi + her planda bir kez `yasaklar`").
- **Neden yanlış:**
  1. **Rol tanımı ve kesin karar 6:** "2 aday + kör denetim + kod karar"; "tasarruf için kaliteden ödün verilmez". Aday görsel 0 Flow kredisidir.
  2. **Hangi planın riskli olduğu önceden bilinmiyor.** B3'te denetimsiz karelerin 21/44'ü bozuktu: yanlış kişi, ters el, yasak ışık (DERS). Bu hatalar sıradan planlarda çıktı.
  3. **Yerel ölçüm ters eli tek başına yakalayamaz.** 02§6.2 G1 #5 kendisi yazıyor: "güvenilirlik orta olduğu için tek başına HATA verilmez". OWLv2 küçük nesneyi (anahtar, yüzük) kaçırabilir ([GS1] R4), MediaPipe el ataması sırtı dönük kişide tersine döner (02§4). Yerel ölçüm "temiz" dediğinde kör gözlem yoksa ters el hiç yakalanmaz. Kesin karar 2'nin "hangi el" şartı bu kapıya bağlıdır.
  4. Yasak öğe, yazı ve filigran, anatomi bozukluğu ve fazladan ışık kaynağı yerel ölçümle ölçülmez.
  5. **Tek aday düzeltme yükünü artırır.** Başarısız tek adayın yeniden üretimi Flow'a ya da ücretli API'ye gider (kullanıcı kuralı gereği paket olmaz, İ-13). İki aday ilk turda geçme oranını yükseltir (ViMax, 01§A3) ve düzeltme gönderimini azaltır.
- **Önerim:**
  - Her plan (Z1 planlarının planlanmış görseli ve Z2 bitiş görselleri dahil) 2 aday.
  - Yerel ölçümde açık HATA alan aday elenir. Kalan **her aday** kör gözlemden geçer.
  - Maliyet açıkça yazılır: film başına ≈ 2.000 görsel, ≈ 3 milyon girdi tokeni (tahmin, §4.1.4).
  - **Daraltma yalnız soru düzeyinde yapılabilir:** bir alan için yerel ölçümün kaçırma oranı ≥ 30 etiketli örnekte ≤ %10 çıkarsa o alanın kör sorusu kaldırılabilir (02§7 hedefi; `ders-editoru` terfisi). Kimlik, el–nesne, kişi sayısı ve yasak öğe soruları hiçbir koşulda kaldırılmaz. Aday hiçbir koşulda atlanmaz.

### ★ İ-3 · [CM] §2.1 A11 "G1 HATA 0; en çok 2 tur (UH §5), **sonra hakem kararı**" ve §3.2 `sureklilik-denetcisi` "karar + CORRECTION cümlesi" — G1'in iki turdan sonra hakemle kapanması
- **Neden yanlış:**
  1. Kaynak 02§6.2 şöyle der: "En çok 2 tur, sonra **insana**." Kesin karar 1 insan kararını kaldırıyor. Yerine hakemin "geç" demesi, iki kaynağın HATA dediği karenin videoya gitmesi demektir. Oysa "bozuk görsel videoya gitmez" kuralı vardır (H/uretim-hatti-v2, BK §7.6 #6) ve başarı ölçütüm B1 bunu %100 ister.
  2. İki CORRECTION turundan sonra sorun zar değil **plandadır** ([YN1] Y8). Bunun çaresi plan değişikliğidir, hakem kararı değildir.
  3. Hakemin CORRECTION cümlesi yazması elle istem yazmaktır. Cümle alan farkından şablonla üretilir (`duzeltme.py`); kaynağı değişmeyen bir istemin her turda farklı yazılması ders defterinin "hangi düzeltme işe yaradı" sayımını da bozar.
- **Önerim:**
  - **Kaçış merdiveni:** tur 1–2 şablonlu CORRECTION → `sureklilik-denetcisi kacis` kök nedeni yazar → `yonetmen onarim` planı değiştirir ([YN2] Y9-b: açı ya da kadraj değişikliği, sorunlu eli kadraj dışına alma, eylemi eklemeye bölme, üçüncü kişiyi siluet yapma, kurulum değişikliği) → plan GS5'ten (K0) yeniden geçer → yine geçmezse plan `durdu` olur ve kullanıcıya **bilgi** verilir (soru sorulmaz).
  - **Hakemin yetkisi kodla sınırlıdır:** hakem yalnız tek kaynaklı BAYRAK'ı ve `ÖLÇÜLEMEDİ` alanını GEÇ ya da HATA'ya çevirir. İki kaynağın HATA dediği alan hakeme gitmez. Hakem dosyasında böyle bir alan için GEÇ yazılırsa `kare_denetim.py --karar` reddeder (test, §4.6.3).

### İ-4 · [CM] §5.9 `kare-tarifcisi` soru formu · [YN1] §6.1 `durum_sorulari()` örneği — Kör sorularda anatomik sol/sağ, parmak sayısı ve beklentiyi sızdıran kişi tarifi
- **Ne yazılmış:**
  - [CM] q2: "Which hand of the woman on the left holds the lantern? left / right / none / not visible".
  - [CM] q6: "How many fingers of her left hand are extended? 0 … 5".
  - [YN1]: "Which hand holds the lantern? A) left B) right".
- **Neden yanlış:**
  1. Görüntü-dil modelleri kişinin anatomik sol ve sağını sık karıştırır ([GS1] R2). Kişi kameraya dönük mü sırtı mı dönük, cevabın anlamı ona göre tersine döner.
  2. "The woman on the left" beklenen kişiyi ve konumunu söyler; gözlemci artık kör değildir. Kişi yanlış yerdeyse ya da hiç yoksa soru cevabı yönlendirir.
  3. Parmak sayımı modeller için zayıftır ([GS1] §9 R2). Tek başına HATA kaynağı yapılamaz.
- **Önerim** (biçim §4.5.7):
  - **İki aşamalı form:** önce serbest envanter. Gözlemci gördüğü her kişiye kendi kimliğini verir (`p1`, `p2` …) ve her birinin görüntüdeki üçte birini, yüz yönünü, **görüntünün solundaki ve sağındaki eli** ayrı ayrı yazar. Sonra hedefli sorular bu `p` kimlikleri üzerinden ve görüntü koordinatında sorulur ("the hand on the IMAGE-LEFT side of p1").
  - `p` kimliği ↔ karakter eşlemesini kod yapar (SFace yüz kutusu ve üçte bir konumu). Görüntü sol/sağını karakterin kendi sol/sağına `kadrajdakiler[].yuz_acisi` ile kod çevirir: kameraya dönük ya da 3/4'te görüntünün solundaki el karakterin sağıdır; sırtı dönükte tersidir; profilde kritik el "belirsiz" sayılır ve hakeme gider.
  - Kritik sorular aynı görevde iki kez, seçenek sırası karıştırılarak sorulur. İki cevap uyuşmazsa alan "belirsiz" olur.
  - Açık parmak sayısı yalnız D/Y kadrajda ve el yüksekliği kare yüksekliğinin ≥ %15'i ise sorulur (tahmin). Sonuç en çok BAYRAK'tır.
  - Soru metninde ad, kostüm, rol ve beklenen konum geçmez. Sorular `kor.py` ile [YN2]'nin `_derlenir.gorunmesi_gerekenler` alanından üretilir ([YN2] Ç-17 bu sahipliği bana verdi).

### İ-5 · [CM] §2.1 A09 → A10 · [UM] §2.1 K09 → §2.2 V01–V03 — Görsel istemin kartlar kilitlenmeden derlenmesi
- **Neden:** `gorsel_istem` kimlik dizesini, kostüm tarifini ve referans görsellerini evrendeki **kilitli** karttan alır. Kart kapısı iki karakteri ayırmak için tarifi değiştirebilir ([GS1] A4, ölçüt B11) ya da yeni bir varyant kartı açabilir. Kartlardan önce derlenen istemler bayatlar. Sonra sessizce eski kimlik dizesiyle görsel üretilebilir.
- **Önerim:**
  - Kart işi, [YN2] Y2'nin `KART_ISTEGI.json` dosyası çıkar çıkmaz yönetmenin plan yazımıyla **paralel** başlar. Kart işi 0 krediliktir, hattı geciktirmez.
  - `istem_derle --gorsel`'in girdi imzası kilitli kart sürümlerini içerir. Kilit değişirse istem `bayat` olur ve o planın G1 kaydı geçersizleşir ([UM] §2.0 zarf ve imza mekanizması).
  - Sıra: kart kilidi → [YN2] Y7 istem derleme → Y8 kamera ağacı → GS7 adaylar. [YN2]'nin sırası buna zaten uyuyor; [CM] ve [UM] tabloları düzeltilmeli.

### İ-6 · [UM] §5.6 `vlm: … gemini_api` ("çapraz model") · [CM] Ç-11 ve S-4 — Gemini'nin ürettiği görseli Gemini'nin onaylaması
- **Neden:** Kartları ve başlangıç görsellerini Gemini üretir (H/gemini-ajan-gorsel). 01§B4: "hiçbir model kendi çıktısını onaylamaz". Gemini denetçi olursa kendi görselini onaylar. Öte yandan aynı not, Gemini ajanının video paketini denetlerken bizim kaçırdığımız 3 hatayı bulduğunu yazıyor: sopaya asılı boş eldiven, verilmiş eldivenin hâlâ elde olması, yanlış kişinin omuz üstü. Yani Gemini **bulgu kaynağı** olarak değerlidir, **onay kaynağı** olarak değildir.
- **Önerim:**
  - `vlm` sağlayıcı zinciri Claude'dur: `claude_code` (görev defteri), `claude_api` (başsız), `sahte`.
  - Gemini yalnız **ikinci göz** adımıdır: parti başına bir paket (GORSELLER + REFERANSLAR + AKIS + SUREKLILIK, aynı nottaki biçim). Bulduğu her şey BAYRAK olarak hakeme gider; hiçbir şeye GEÇ demez.
  - Varsayılan açık: kullanıcının 18.10'daki "Gemini'yi zorla" isteği (aynı not). `FILM_AYAR.json → ikinci_goz` ile kapatılabilir. Kullanıcının fiziksel işi parti başına bir paket artar; bu [UM] M2 sayımına girer.

### İ-7 · [YN2] §4.8.2-d tablosu ve kendi [GS1] §2.0 ile A15 (öz eleştiri) — "1280×720 → 1376×768 Lanczos"
- **Neden:** 1376 / 768 = 1,792; 1280 / 720 = 1,778 (hesap). Bu büyütme en-boy oranını yaklaşık %0,8 bozar: yüzler ve nesneler yatayda gerilir. SFace ve DINOv2 ölçümleri ve Veo'nun ilk karesi bundan etkilenir. 1376×768, Gemini çıktısının "16:9" kırpımıdır (H/gemini-ajan-gorsel); gerçek 16:9 değildir.
- **Önerim:**
  - Zincir karesi en-boy oranı korunarak kullanılır. **Varsayılan:** doğal 1280×720, yeniden örnekleme yok.
  - Kalibrasyon partisinde ikinci seçenek ölçülür: 1376×774 Lanczos + üstten ve alttan 3 px kırpma → 1376×768.
  - G1'in en-boy denetimi "16:9 ±%1, kısa kenar ≥ 720 px" olur. 1376×768 de 1280×720 de geçer.

### İ-8 · [YN2] §4.2 Y8 · [UM] §9.1 R2 — Kamera ağacı basamakları kullanıcının paket turlarını çoğaltıyor
- **Ne yazılmış:** "Her basamak G1'den geçmeden sonraki basamağın paketi verilmez" (plaka → ana kare → türev → `devam` planlanmış görselleri).
- **Kabul:** Türev, ebeveynini referans alır; ebeveyndeki hata türevlere yayılmamalıdır.
- **Eksik:** Paket turu sayısı ≈ 3 parti × 3 basamak + kart turu ≈ 10–12 kullanıcı eylemine çıkar (tahmin), her turda G1 beklemesiyle. Kesin karar 1 fiziksel işi yasaklamaz, ama [UM] M2 ölçütünü etkiler.
- **Önerim:**
  - Basamaklar sahne grubu değil **parti** düzeyinde toplanır: bir partinin bütün ana kareleri tek ya da birkaç 30'luk pakette gider.
  - Birbirine bağlı olmayan basamaklar aynı kullanıcı turunda birleşir: P2'nin 1. basamağı P1'in 2. basamağıyla aynı paket turunda verilebilir.
  - Türevin referansları için kalibrasyon partisinde A/B ölçülür: (A) ebeveyn + kadrajdaki karakter kartları (≤ 2), (B) ebeveyn + yalnız `kimlik_demiri` olan karakterin kartı. Toplam ≤ 3 görsel (tahmin). RE `referans_max` = 2 karakter referansı içindir; karakter dışı referansın sınırı ölçülmedi ([YN1] açık soru 4).
  - Kurulumda ücretli `vertex_gorsel` açılırsa basamaklar kullanıcısız akar.

### İ-9 · [KU2] §4.5.5 0 kredi merdiveni #7 Ayna, #8 Yeniden kadraj, #12 Yer tutucu — Görüntüyü değiştiren 0 kredi çözümlerinden sonra yeniden ölçüm yok
- **Neden:**
  - Ayna yüz asimetrisini çevirir (SFace benzerliği değişir), kadraj sırasını ve ekran yönünü tersine döndürür (K1 ve 180° yeniden).
  - Yeniden kadraj yüzü kenara itebilir ya da ikinci kişiyi keserek "kaybolma" üretebilir.
  - Yer tutucu görsel G1'den geçmemiş olabilir.
- **Önerim:**
  - Bu üç işlemin çıktısı kurgu planına girmeden önce `video_denetim.py --klip --islem <ayna|kadraj>` (V2 kimlik + ekran yönü) ve `--gecis` (K1 + dondurulmuş olgular, [YN2] Y58) yeniden koşar.
  - Yer tutucu yalnız `denetim.G1.sonuc = GEC` olan görselden yapılır.
  - Ayna yalnız `_derlenir.ayna_yasak = false` iken ve **bir kez** yapılır (işaret dosyası; DERS "düzeltme araçları bir kez uygulanmalı").

### İ-10 · [SM1] §5.4 S3.4 ve §9.2 "yüz kontrolü" satırı · [SM2] S1.12, S2.15 — V2'den beklenen yüz çıktısı ve dudak senkronu sonrası denetim tanımsız
- **Neden:**
  - V2 0,5 sn arayla 17 kare ölçer. Dudak denetimi (S3) 24 fps ağız dizisi ister. Ağzı oynayan yüzün kimliğini (S3.4) seyrek örnekten eşlemek ağzı yanlış kişiye bağlayabilir.
  - `tts_dudak` çıktısının "V2'den yeniden geçmesi" isteniyor, ama hangi ölçünün değiştiği yazılmamış. Ağız çevresi yeniden üretilir; SFace bütün yüze bakar ve küçük bozulmayı kaçırabilir.
- **Önerim:**
  - V2, `_derlenir.replik_zaman` ve `ekran_disi_ses` pencerelerinde **kare kare yüz izi** çıkarır: YuNet kutusu + SFace kimliği + MediaPipe Face Landmarker `jawOpen`, tek geçişte (`olcum/kimlik.py`). Dosya: `_RAPOR/V2_P<n>/NNN_yuz.jsonl`. `dudak_denetim.py` (ses) bunu okur, yüzü ikinci kez aramaz ([SM1] §9.2'nin "tek geçiş" önerisi).
  - `video_denetim.py --dudak`: `tts_dudak` klibinde aynı kare için özgün ↔ yeni karşılaştırma. SFace bantları (§4.7.3) + alt yüz kırpıntısında DINOv2 ≥ 0,80 (tahmin, B) + kişi ve yüz sayısının değişmemesi (H).
  - MediaPipe ana ortamda **tek sürüm** olur. Python 3.10 Windows tekerleği kalibrasyon partisinde doğrulanır. OpenMontage kendi ortamında 0.10.14'te kalır ([KU1] D12, [SM1] R10).

### İ-11 · [UM] §5.9 `KUTUPHANE/<SERI>/` ve §5.8 `KUTUPHANE/DERSLER/` · [SM1] `EVREN/SESLER/`, `EVREN/MEKANLAR/` · kendi [GS1] §5.1 `EVREN/<SERI>/DERSLER.jsonl` (öz eleştiri) — Kütüphane ve ders defterinin yeri
- **Önerim:**
  - Çoğunluğun düzeni: `EVREN/<SERI>/` ve **sahip başına ayrı dosya** ([SN2] §2.7, [YN2] Ç-14, [SM2] Ç-11). Yalnız `evren.py` yazar ([CM] "makine sahipli").
  - Ders defteri tek yerde ve tek biçimdedir: [UM]/[CM]'nin ortak biçimi (bir olay bir kayıt), `YZ_FILM/BILGI/DERS_DEFTERI/` altında. Her kayıtta `seri` ve `alan` vardır; seriye özel dersler süzgeçle ayrılır. Kendi `EVREN/<SERI>/DERSLER.jsonl` önerimi geri çekiyorum.
  - `KALIBRASYON.json` (karakter başına kimlik eşikleri) evrende kalır, çünkü bir yüze bağlıdır.

### İ-12 · [SN2] İ9 — Hikâyeye bağlı görünüş öğesi kadro ayrışmasını engellediğinde
- **Kabul:** Hikâyeye bağlı öğe (`hikaye_baglayici: true`) kilitlidir; yalnız `hikaye-yazari`nın isteğiyle değişir.
- **Eksik:** İki karakterin hikâyeye bağlı öğeleri birbirine benziyorsa (ör. iki kızıl saçlı kardeş) kart tasarımcısı hiçbir şeyi değiştiremez. SFace ayrışma eşiği (B11) ve seyircinin karıştırma riski kalır.
- **Önerim:**
  - `kart_denetim.py --karar` bu durumu `HATA: ayrisma_kilitli` diye raporlar.
  - `kart-tasarimcisi` önce hikâyeye bağlı olmayan öğeleri ayrıştırır: siluet, kostüm rengi, aksesuar.
  - Yine < 0,363 sağlanmazsa iki yol vardır: senariste `gorunus_degisiklik_istegi` gider ([SN2] H15 dar değişiklik) ya da senarist çifti `bilincli_benzerlik` diye işaretler. İkinci yolda o çiftte fark payı yerine kostüm ve aksesuar denetimi yapılır; seyircinin ayırt etmesi için ayırt edici aksesuar ya da replik hikâyenin işidir.

### İ-13 · [UM] §5.6 `gorsel: … flow_gorsel (Memmet, yalnız düzeltmeler)` ve §7.2 `flow.gorsel_sonrasi_video` — Düzeltme görsellerinin hacmi ve yolu tanımsız
- **Neden:**
  - Kullanıcı kuralı (H/gemini-ajan-gorsel, 18.10 akşam): düzeltme ve yeniden üretim görselleri kullanıcıya **paket olarak verilmez**; Memmet ile Flow'da yapılır.
  - Film başına G1 düzeltme hacmi ≈ 120 plan × 2 aday ≈ 240 görsel (tahmin; ilk tur geçme hedefi %70'ten, B6).
  - Flow'da görsel gönderimi de uyarı alıyor; yoğun görsel turundan sonra hesap işaretlendi (DERS). [UM]'nin "aynı gün > 20 görsel → o gün video yok" kuralıyla bu hacim yaklaşık 12 ayrı Flow görsel günü eder (hesap: 240 / 20).
- **Önerim:**
  - `gorsel_duzeltme` sağlayıcı zinciri: `vertex_gorsel` (kurulumda dolar izni varsa; ≈ 240 × 0,134 $ ≈ 32 $/film, hesap, fiyat 06_SERVISLER) → `flow_gorsel` (Memmet, x2 çıktı, mümkünse `--mod elle`, tempo 17.10 değerleri, görsel günü ≠ video günü, günlük tavan [UM] ayarı) → **asla kullanıcı paketi**.
  - Düzeltme kuyruğu basamak sonunda toplu işlenir; her CORRECTION için ayrı oturum açılmaz.
  - Asıl çare ilk tur kalitesidir: K0 + derlenmiş istem + kamera ağacı + 2 aday (B6 ≥ %70).
  - Ücretsiz yolda takvim uzar. Bu, `URETIM_ONIZLEME.md`'ye sayıyla yazılır ([UM]'nin "dürüst sonuç" ilkesi).

---

## 2. Çakışmalar ve önerdiğim çözüm (alan adları, aşama sırası, sorumluluk sınırları)

### 2.1 Alan, ajan ve dosya adları

| Kavram | Öneriler | Çözüm | Gerekçe |
|---|---|---|---|
| Kör gözlem ajanı | [GS1] `kor-gozlemci` · [CM] `kare-tarifcisi` · [UM] `vlm-denetci` | **`kare-tarifcisi`**; işin adı "kör gözlem" kalır | [CM] kadrosu, erişim rolleri ve `omitClaudeMd` bu adla yazılı; yeniden yazmak gereksiz |
| Kart yazarı | [GS1] `kart-tasarimcisi` · [CM] A10'da tanımsız · [UM] V01 "ana Claude" | **`kart-tasarimcisi`** (yazar ajan; Bash yok; denetim SubagentStop'ta) | [CM] Ç-10 ölçütü (a): `KART_SPEC.json` ve evrendeki görsel tarif alanlarının tek sahibi. Ana Claude içerik üretmez ([CM] §3.1-1) |
| Kart sanat seçimi | [GS1] `yonetmen` · [YN2] `kart_secimi` kipi | `yonetmen` `kart_secimi` kipi | aynı |
| Defter aracı ve dosyası | [GS1] `sureklilik_defteri.py` · [YN1] `durum_defteri.py` · [UM] `dunya_defteri.py` · [CM] `DUNYA_DURUMU.json` | **`dunya_defteri.py` → `DUNYA_DEFTERI.json`** (film kökü); sahibi ben; çözüm kurallarının şartnamesi [YN2] §4.5.13 | [YN2] Ç-5 |
| Plan alt nesnesi | [GS1] `sureklilik` | **Kalkar.** Niyet `zanaat`'ta, kod hesabı `_derlenir`'de, yürütme `uretim`'de, kapı sonucu `denetim`'de | [YN2] Ç-1 |
| Durum nesnesi | [GS1] `kadrajdakiler[]` içinde `konum`, `yon`, el hâli `gorunmuyor` | [YN2] §4.5.7 (yalnız olgu) + benim eklediğim `gorunum.sac` (örgülü, çözük, ıslak gibi kalıcı saç durumu) | [YN2] İ-1 |
| Eller | [GS1] `eller.*.hal` birleşik dizgeler | `eller.{sag,sol}.{tutar, yer, sekil}`; açık parmak `_derlenir.acik_parmak` | [YN2] İ-13 |
| Geçiş türü | [GS1] 3 değer · [YN1] 6 değer | [YN1]'in 6 değeri. Benim **Z0/Z1/Z2** adlarım yöntem adı olarak kalır: Z0 = `baslangic ∈ {kart, ana_kare, turev}`, Z1 = `baslangic: son_kare`, Z2 = `bitis_sabitle: true` | [YN2] Ç-7 |
| Mekân kamera açıları | [GS1] `mekan.json → kamera_konumlari` · [YN1] `kurulumlar` | Geometri `kroki.json → plakalar.<id>` (yönetmen); görsel, özet ve banka `mekan.json → plakalar.<id>` (ben); film düzeyi `kurulumlar.K<n>` (yönetmen) | [YN2] Ç-13 |
| Kroki | [GS1] `mekan.json` | `EVREN/<SERI>/mekanlar/<id>/kroki.json`, yalnız yönetmen yazar | [YN2] İ-3 |
| Stil eki | [YN1] film düzeyi · [GS1] `dunya.json` | `EVREN/<SERI>/dunya.json → stil_eki` (ben); içinde ışık ifadesi yasak | [YN2] Ç-15; BK §8 #12 |
| Kostüm kimliği | [SN1] `sera_k1_pelerin` · [YN2] örnekte `mara_k1` · [GS1] `k1` | Karakter kapsamlı `k1`, `k1_yirtik`; dışarıdan başvuru `mara/k1`; dosya adı `kart_k1_v2.jpg` | [SN2] §2.1 kabul etti |
| Kimlik dizesi | [GS1] `kimlik_en` adla başlıyordu | `kimlik_en` **ad içermez** (yalnız görünüş). Derleyici `Mara — {kimlik_en}` yazar. Ad değişince kart bayatlamaz, yalnız istem yeniden derlenir | [SM2] İ-10'un "ad değişirse kartlar bayatlar" sorununu çözer |
| Rapor klasörü | `_RAPOR/` · `RAPORLAR/` | **`_RAPOR/`** | çoğunluk ve mevcut kod ([SN2], [KU2], [SM2]) |
| Kuyruk | [GS1] `_RAPOR/YENIDEN_URET.json` · [UM] `KUYRUK/` | **`KUYRUK/YENIDEN_URET.json`**, tek şema ([UM] tabanı + [KU2] alanları + benim `alan`, `beklenen`, `olculen`, `gozlenen`, `aday` alanlarım) | [KU2] §2.1 |
| Ajan devri | [GS1] çıkış 2 + `_AJAN_ISLERI/` | [CM] görev defteri (`_GOREV/<id>/GOREV.json, GIRDI, CIKTI`); `film.py` çıkış 3 = ajan işi ([UM]). Benim araçlarım iş tanımı yazar, çıkış kodu tanımlamaz | tek protokol |
| Görüntü-dil sağlayıcı türü | [GS1] `gozlemci` · [UM] `vlm` | **`vlm`**: `claude_code`, `claude_api`, `sahte`. Gemini bu zincirde yok (İ-6) | [UM] §5.6 adı |
| Ders defteri | beş biçim | [UM]/[CM] ortak biçimi, `YZ_FILM/BILGI/DERS_DEFTERI/`; benim alanım kategori ve ölçü alanlarını ekler | İ-11 |
| Eşik dosyası | [GS1] `sureklilik_esikleri.json` | Kalır; [SN2]'nin ortak yükleyicisi `esikler.py` birleştirir ve aynı anahtar iki dosyada geçerse HATA verir | [SN2], [SM2] Ç-14 |
| Evrendeki ses alanları | [GS1] `mekan.json → ambiyans`, `karakter.json → ses_ref` | `mekan.json` ve `karakter.json` yalnız `ses_ref` yolunu tutar; içerik `ses.json`'da | [SM2] İ-8 |
| `kesme_ayni_mekan` sınıfı | [GS1] | Kodla türetilir: `eylem_kesme ∪ kurulum_donusu ∪ araya_kesme ∪ zaman_atlama` | [YN2] Ç-7 |
| Adım kodları | [GS1] `A1–A17` | `GS1–GS17` | [CM] `A00–A18` ile çakışmasın |

### 2.2 Araç ve ölçü sahipliği (benim alanımın çevresi)

| İş | Tek araç | Sahibi | Kullananlar |
|---|---|---|---|
| Dünya durumu defteri, K0, dondurma, "gözlenen" sütunu | `dunya_defteri.py` | görüntü-süreklilik | yönetmen (Y11–Y16, Y57, Y58), kurgu (kesme simülasyonu), ses (hava, ateş, karakter görünümü alanları) |
| Geometri (kadraj konumu ve sırası, görüş hattı, bakış, ışık ve ekran yönünün kadrajdaki karşılığı, ayna yasağı, görünmesi gerekenler) | `kroki.py` (kütüphane + CLI) | yönetmen | `dunya_defteri`, `istem_derle --gorsel`, `kart_denetim` (plaka) |
| Görsel istem, kart istemi, bitiş görseli istemi | `istem_derle.py --gorsel / --kart / --bitis` | görüntü-süreklilik | — |
| Hareket istemi | `istem_derle.py --hareket` | yönetmen | — |
| Kör soru üretimi, anonim görev klasörü, cevap okuma, kişi eşleme, sol/sağ çevirisi, karşılaştırma | `kor.py` | görüntü-süreklilik | [CM] görev defteri ve `erisim_kapisi` (teslim); yönetmen `_derlenir.gorunmesi_gerekenler` |
| Kart kapısı ve banka üretimi | `kart_denetim.py` | görüntü-süreklilik | `yonetmen kart_secimi` |
| G1, G1Z, kapak adayları | `kare_denetim.py` (`--serbest` kapak için) | görüntü-süreklilik | yayın |
| CORRECTION şablonları ve küçük düzeltmeler | `duzeltme.py` | görüntü-süreklilik | ses (ses şablonları ayrı bölüm, [SM2] §4.5.11) |
| Zincir planı ve zincir karesi | `kare_zinciri.py --plan / --cikar` | görüntü-süreklilik | kurgu `kirp_oner.py --zincir` (pencere önerisi) ve kilit |
| V1 | `kalite_denetim.py --klip` | görüntü-süreklilik (final bölümü ses ve kurgu ortak) | kurgu (`kirp_oner` kusur damgalarını okur) |
| K1Ö, V2, V3, dudak sonrası V2, K1 | `video_denetim.py --onceden / --klip / --dudak / --gecis` | görüntü-süreklilik | ses (yüz izi), kurgu (K1 bulguları) |
| Ölçüm arka uçları | `olcum/` paketi | görüntü-süreklilik (`ses.py`, `dudak.py` ses uzmanının) | herkes |
| Evren yazımı | `evren.py` | görüntü-süreklilik (çatı) | hikâye, ses, yönetmen, kurgu kendi alt komutlarıyla |
| Gemini paketleri | `gemini_paket.py`, `gemini_al.py` | araç üretim mühendisinin; paket içeriği ve içe alma kuralı benim | — |
| Yeniden üretim kuyruğu | `kuyruk.py` | kurgu | bütün kapılar aynı şemayla yazar |
| Ders kaydı | `ders_defteri.py` | üretim mühendisi | görüntü kategorileri benim |

### 2.3 Aşama sırası (benim alanımın çevresi; diğer uzmanların kodlarıyla)

```
[SN2] H13 hikâye kilidi
 → [YN2] Y0 brifing → Y1+Y2 harita, kroki, plakalar, KART_ISTEGI.json
      ║ [GS] GS1 evren bağla → GS2 kart tarifleri (kart-tasarimcisi)
      ║      → [SM2] SB1 telaffuz testi (yerel; ad değişirse yalnız istem yeniden derlenir)
      ║      → GS3 kart adayları (plakalar dahil) → GS4 kart kapısı + yonetmen kart_secimi + kilit
 → [YN2] Y3 sahne grubu planları → Y4 birleştir + [GS] GS5 dunya_defteri (K0) + kroki + Z0 + [KU2] KR0 (T0)
 → [YN2] Y5 kâğıt denetimi (sureklilik-denetcisi kagit kipi dahil) → Y6 plan seyircisi → [SM2] ses kâğıtta
 → [YN2] Y7 istem derleme (--hareket ∥ [GS] GS6 --gorsel; kart kilidi şart) → Y8 kamera ağacı
 → [GS] GS7 adaylar (basamak 1: kart/ana kare → basamak 2: türev → basamak 3: devam planlanmış + Z2 bitiş görselleri)
        her basamakta GS8 G1 → GS9 CORRECTION (≤ 2 tur → kaçış) → parti sonunda GS10 K1Ö (+ ikinci göz)
 → [KU2] KR1–KR4 animatik ⟲ (yalnız G1'li kareler)  → [UM] V09 kesin bütçe
 → [GS] GS11 zincir ve dalga planı → GS12 video şartları ([UM] U01) → GS13 V1 → GS14 V2+V3 → GS15 Z1 karesi + G1Z ([KU2] KR5 kilidi)
 → [SM2] ses (C) → [KU2] KR6 kaba kurgu → [GS] GS16 K1 (kurgu sırası; kurgucuya ve hakeme) → [KU2] KR8 kurgu izleme ⟲
 → [GS] GS17 ders defteri + evren güncelleme
```

### 2.4 Sorumluluk sınırları

| Konu | Tek sahibi | Benim yetkim | Değişiklik yolu |
|---|---|---|---|
| Hikâyeye bağlı görünüş öğesi (`hikaye_baglayici`) | senarist | okur, kart kapısında denetler | `gorunus_degisiklik_istegi` → [SN2] H15 |
| Diğer görsel tarif, kostüm varyantı kartı, plaka görseli, nesne ölçek kartı | `kart-tasarimcisi` (tarif) + `kart_denetim.py` (teknik eleme) + `yonetmen kart_secimi` (sanat seçimi) | kapı benim | kart kapısı raporu → aynı yazar |
| Kroki, plakaların geometrisi, kurulumlar | yönetmen | okurum; plakada "görünmesi gerekenler" denetimi benim | `KART_ISTEGI.json`, yeni kroki sürümü |
| Plan olguları (durum, adım, `etki`) | yönetmen | K0 HATA'sını yazarım | `KUYRUK/YENIDEN_YAZ.json` → aynı yönetmen örneği |
| Defterin çözümü ve zıplama hükmü | betik (`dunya_defteri.py`) | sahibi | — |
| `gorsel_istem` | betik (`istem_derle --gorsel`) | sahibi | Elle yazılmaz; kaynak alan düzeltilir |
| G1 kararı | betik + hakem (yalnız BAYRAK ve ÖLÇÜLEMEDİ) | sahibi | — |
| Plan değişikliği (G1 kaçışı, V3 kaçışı) | `yonetmen onarim` | kök nedeni `sureklilik-denetcisi kacis` yazar | `ONARIM_<tur>.json` |
| Kesme noktası | kurgucu (`kirp_oner.py`) | Z1 karesini pencereden ben seçerim | kurgucu kilitler (`kullanim_kilit: zincir`) |
| Video yeniden çekim kararı ve dilim | `kuyruk.py` (kurgu) + `kredi.py` (üretim) | madde yazarım; 0 kredi denemesi yazılı olmadan madde açmam | KU2 merdiveni |
| Ses yolu, dudak ölçümü | ses | yüz izini veririm; `tts_dudak` sonrası V2'yi koşarım | — |

### 2.5 Kare zinciri: uzlaşılan karar tablosu ([YN2] §4.8.2-d ve [KU2] §4.8-d ile aynı; benim eklerim **kalın**)

| `zanaat.zincir.gecis_turu` | Başlangıç karesi | Bitir (Z2) | Denetim | Yedek |
|---|---|---|---|---|
| `devam` | **Z1:** önceki klibin [KU2] penceresinden (Y55) seçilen gerçek kare; **en-boy korunur, 1280×720 doğal** | Önceki klipte durum değiştiren fiziksel adım varsa önerilir (Y56); kaynağı bu planın G1'li planlanmış görseli. Konuşmalı planda yok | **G1Z** + Z1 dikişi DINOv2 ≥ 0,80 (K1); derinlik ≤ 2 | Bu planın G1'li planlanmış görseli (`yedege_dustu`) |
| `eylem_kesme` | Kurulumun ana karesinden türev (Z0) | Yalnız kritik bitiş + `risk_uretim = yuksek` ya da V3 başarısızlığında `NNN_son.jpg` (≤ %10 plan, Y42) | G1, V3 | CORRECTION |
| `kurulum_donusu` | O kurulumun ana karesinden türev (Z0) | — | G1; K1 ana kareye DINOv2 ≥ 0,70 | CORRECTION |
| `araya_kesme` | Kurulumun ana karesinden türev (Z0) | — | G1 | CORRECTION |
| `zaman_atlama` | Ana kare + gerekçeli fark (Z0) | — | G1; K0 fark gerekçesi | CORRECTION |
| `yeni_sahne` | Plaka + karakter kartları (Z0, `kart`) | — | G1 | CORRECTION |

- Z1 kaynağı olan klip V1 + V2 + V3'ten geçmeden ve zincir karesi G1Z'den geçmeden ardıl plan gönderilmez.
- Doğrudan bitişik `devam` yalnız `dogal_durak: true` ise; değilse araya örtü planı girer ([YN2] Y54, süresi [KU2] İ-11 formülüyle).
- Derinlik 3'te **yeniden demirleme:** zincir karesi + kart sayfası referansıyla temiz görsel üretilir; G1'den ve zincir karesine DINOv2 ≥ 0,90 (tahmin) şartından geçer.
- **Z1 başlangıç + Z2 Bitir aynı klipte** morf riskini artırır mı, ölçülmedi ([YN2] açık soru 4). Kalibrasyon partisinde ölçülene kadar aynı klipte birlikte kullanım BAYRAK'tır; morf ölçüsü (V2 DINOv2 sıçraması) bu kliplerde sıkı izlenir.

---

## 3. Diğerlerinden kabul edip kendi önerime kattıklarım

| Kaynak | Kabul ettiğim | Önerimdeki yeri |
|---|---|---|
| [YN2] İ-1 | Durum yalnız olgudur; kadraj konumu, sırası, bakış, ışık ve ekran yönü `kroki.py` ile `_derlenir`'e hesaplanır | §4.5.5, §4.7.1, GS5, GS6, GS8 |
| [YN2] İ-3, Ç-13, Ç-14 | Kroki yönetmenin; plaka geometrisi krokide, plaka görseli `mekan.json`'da; kart tasarımcısı koordinat yazmaz | §4.5.3, GS2, GS4 |
| [YN2] İ-6, §4.5.8 | Adım şeması: kalıcı `id` (`a1…`), sözlükten fiil, karakterin kendi sağı/solu, `etki`. Benim tur 1 örneğim (`bas: 0.0`, `walk`, `kadraj_sagina`) yanlıştı | §4.5.5 örneği |
| [YN2] İ-10 | `_derlenir.ayna_yasak` kodla hesaplanır; G1 ve kurgu bu tek alanı okur | GS9, §4.7.8 |
| [YN2] İ-11 | **Durum dondurma:** görsel seçildiği anda çözülmüş durumlar özetiyle dondurulur; kurgu sırası değişince denetim dondurulmuş durumla yapılır (Y58) | GS8 adım 5, §4.5.6 |
| [YN2] §4.5.13 | `dunya_defteri.py` şartnamesi (miras, fark, etki katlama, araya kesme, geri dönüş zaman çizgisi, klip bölme, dondurma, derleme yönü, geriye uyumluluk) | GS5 |
| [YN2] Y44, Y54, Y55, Y56, Y57, Y58, Y60 | Kimlik demiri, örtülü devam, Z1 kesme penceresi, Z2 politikası, hikâye uçları ⊆ sözleşme, dondurulmuş olgu eşitliği, plakaların görüş konisini kapsaması | §4.7 |
| [YN2] Y8 | Kamera ağacı ve basamaklı görsel üretimi (İ-8 eklemeleriyle) | GS7 |
| [YN2] `gizli_arkasinda`, `_derlenir.gorunmesi_gerekenler`, `yuz_acisi` | Kör soruların kaynağı ve sol/sağ çevirisinin girdisi | §4.5.7 |
| [KU2] İ-1 | **K1Ö ve K1 bulguları seyirciye verilmez**; kurgucuya ve hakeme gider; seyirci bulgusuyla sonradan eşlenir. Yalnız seyircinin yakaladığı geçiş `kacirma` etiketiyle ders defterine yazılır | GS10, GS16, B20 |
| [KU2] KR5, §2.2 | `kirp_oner.py --zincir` pencereyi önerir, `kare_zinciri.py --cikar` kareyi seçer, kurgucu çıkışı kilitler | GS15 |
| [KU2] İ-3, §2.5 | Yeniden çekim dilimleri: görüntü + süreklilik + plan dili 0,15 (≈ 729 kredi, hesap); plan başına ≤ 2 yeniden çekim (ortak sayaç) | B7, GS14 |
| [KU2] §4.5.5 | Kuyruğa yazılan kredili maddede `sifir_kredi.denendi` ve gerekçe şart; V1/V2 kusuru kullanılan pencerenin dışındaysa `cozum: kirp`, madde açılmaz | GS13, GS14 |
| [KU2] §2.6 madde 7 | Tek seyircinin görsel KRİTİK'ini geçersiz saymanın hakemi `sureklilik-denetcisi` | §4.3.2 |
| [KU2] §6.2 / [KU1] §9.2-3 | V1/V2 raporları kusurların zaman damgasını verir | GS13, GS14 |
| [SN2] İ9 | `ayirt_edici[].hikaye_baglayici` (İ-12 eklemesiyle); `bilincli_benzerlik` | §4.5.2, GS2, GS4 |
| [SN2] İ13 | Tekrar eden mekân ≤ 6, toplam ≤ 10 (BAYRAK); kostüm varyantı karakter başına ≤ 2 ([SN1] §7.2) | §4.1.4 ölçek |
| [SN2] §2.7 | Evren düzeni: sahip başına ayrı dosya; `DURUM_SON.json` fiziksel bitiş durumudur ve benim | §4.5.1 |
| [SN2] ortak yükleyici `esikler.py` | Eşik dosyalarının çakışma denetimi | §4.6 |
| [SM2] İ-7 | V1'de replik penceresi sessizliği ölçülmez; tek yer S2.1 ([KU2] İ-9 ile aynı) | §4.7.6 |
| [SM2] İ-8 | Evrende ses içeriği `ses.json`'da; görüntü dosyaları yalnız `ses_ref` tutar | §4.5.2, §4.5.3 |
| [SM2] S2.15, §3 [GÖR] satırı | `tts_dudak` çıktısı V2'den yeniden geçer; ses ölçüleri `olcum/` paketine `ses.py` ve `dudak.py` olarak girer | GS14, §4.6 |
| [SM2] ses CORRECTION şablonları | `duzeltme.py`'nin şablon dosyasında ayrı bölüm; aynı alan için cümle eklenmez, değiştirilir | §4.5.8 |
| [UM] §2.0 | Çıktı zarfı ve girdi imzası; kredili çıktı asla silinmez, `bayat` işaretlenir; ortam algılama (bulutta yalnız `sahte` ölçüm) | GS6, §4.6 |
| [UM] §5.6 | `Kisitlandi` kodları; `vlm` sağlayıcı türü; `kaset` sağlayıcısıyla ağsız test | §4.6 |
| [UM] §5.8 | Ders defterinin ham kayıt biçimi, terfi eşiği, korkuluklar (eşik gevşetme yalnız kalibrasyon kanıtıyla) | §4.5.11, §4.8.7 |
| [UM] §7.2 `flow.gorsel_sonrasi_video` | Yoğun görsel günü video yapılmaz (İ-13 eklemesiyle) | GS9, GS12 |
| [UM] §6.4 T18 | `mara.jpg` ↔ `mara` kartı ≥ eşik; `voss.jpg` ↔ `mara` kartı < 0,363 testi | §4.6.3 |
| [UM] §7.4 kalibrasyon notu | B3'ün 44 etiketli görseli: yalnız etiket JSON'u depoya girer, görseller yerelde kalır | GS0 |
| [CM] §2.0, §5.2, K-3, K-6 | Görev defteri, `_GOREV/<id>/{GOREV.json, ISTEM.md, GIRDI, CIKTI}`, şablondan istem, `erisim_kapisi` (kör rol yalnız GIRDI okur), SubagentStop doğrulaması (≤ 2 düzeltme) | §4.3, §4.4 |
| [CM] §3.1 | Ajanlarda Bash yok; `memory:` yok; kör rolde `omitClaudeMd: true`; dönüş ≤ 5 satır; önce başlıkları yaz, bölüm bölüm doldur; bütün ajanlar `opus` + `effort: high` | §4.3 |
| [CM] §5.6 | Ders adayı terfisi `ders-editoru`'dadır; `SubagentStart` kancası rol derslerini yazar ve denetçi ajanlara ekler, kör rollere eklemez | §4.8.7 |

**Geri çektiklerim:** `kor-gozlemci` adı · plan düzeyinde `sureklilik` alt nesnesi · durumda kadraj bilgisi (`konum`, `yon`, `kadraj_sirasi`, `hareket_yonu`, el hâli `gorunmuyor`) ·
`eller.*.hal` birleşik dizgeleri · `kesme_ayni_mekan` sınıfının elle yazılması · krokinin kart tasarımcısınca yazılması ve `mekan.json` içindeki kroki ·
`kamera_konumlari` · K1Ö ve K1 kare çiftlerinin seyirciye verilmesi · ajan işi için çıkış kodu 2 ve `_AJAN_ISLERI/` · kör gözlemcide ajan dosyasına gömülü kanca
(yerine [CM] `erisim_kapisi`) · `kart-tasarimcisi`'nde Bash · `gozlemci` sağlayıcı adı · `EVREN/<SERI>/DERSLER.jsonl` · `mekan.json → ambiyans` ·
V1'de replik penceresi sessizliği · 1280×720 → 1376×768 Lanczos büyütmesi · `sureklilik_defteri.py` adı · `kimlik_en` içinde karakter adı ·
tur 1 §5.5'teki hatalı adım örneği.

---
## 4. REVİZE NİHAİ ÖNERİM

Bu bölüm tur 1 dosyamın yerine geçer ve kendi başına okunabilir. Tur 1'den farklı yerler **(değişti)** ya da **(yeni)** diye işaretlidir.
Kapsam: kartlar ve seri kütüphanesi, başlangıç karesi üretimi ve seçimi, otomatik yüz ve görünüm denetimi, dünya durumu defteri ve zıplama denetimi,
CORRECTION döngüsü, Veo/Flow kısıtları, kare zinciri, video sonrası teknik denetim.

---

### 4.1 Alanımın hedefi ve başarı ölçütü (sayılarla)

#### 4.1.1 Hedef (tek cümle)
Seyirci 30–45 dakika boyunca **hiçbir karakterin yüzünün, kostümünün, elindeki nesnenin, mekânın ya da ışığın "kendiliğinden" değiştiğini görmesin.**
Her değişiklik dünya durumu defterinde yazılı ve ekranda görünen bir eylemle olsun. Bunun bedeli video kredisiyle değil, kâğıtta ve 0 kredili görsel aşamasında ödensin.

#### 4.1.2 Neden bu alan kritik (kaynaklı)
- YZ sinema filmlerinde izleyicinin **tek büyük eleştirisi** karakter tutarsızlığı: "appearance of the characters keep changing" (803 beğeni) (BK§1.4).
- B3'te video öncesi elle yapılan görsel denetim **44 başlangıç karesinin 21'inde** hata buldu: yanlış kişi, ters el, yasak ışık (DERS). Denetimsiz karelerin yaklaşık **%48'i** bozuktu.
- B2'de yaklaşık 134 videonun üstüne **50'den fazla yeniden çekim** yapıldı, yani yaklaşık **%37** (hesap; H/proje-b2). Örnekler arasında "B22K'de Bram'a benzemeyen adam" gibi süreklilik hataları var.
- Veo API'de referans görseller, başlangıç ve bitiş karesiyle **aynı istekte kullanılamaz** (02§2.1, `google-genai` `types.py`). Video modeli kimliği yalnız başlangıç karesinden alır. Bu yüzden **başlangıç karesi kapısı (G1) bütün hattın en kritik kapısıdır.**

#### 4.1.3 Başarı ölçütleri

| # | Ölçüt | Hedef | Kaynak / not |
|---|---|---|---|
| B1 | Videoya giden başlangıç karelerinden G1 (ya da G1Z) kaydı GEÇ olan ve dosya özeti (SHA1) kayıtla eşleşenlerin oranı | **%100** (kod zorlar; elle konan kare de kapıdan geçer) | "Bozuk görsel videoya gitmez" (H/uretim-hatti-v2) |
| B2 | Kurgu izleme denetiminde **görsel kaynaklı** KRİTİK kopukluk (yüz değişti, nesne zıpladı, kişi kayboldu, ışık zıpladı) | parti başına **0** | RE:kopukluk_kritik_max = 0 |
| B3 | Görsel kaynaklı ORTA kopukluk | parti başına ≤ 1 (genel sınır bütün türler için ≤ 3) | RE:kopukluk_orta_max_parti = 3; ≤ 1 bu alanın payı (tahmin) |
| B4 | G1 kaçırma oranı (bozuk kareye GEÇ), etiketli kalibrasyon setinde | **≤ %10** | 02§7 |
| B5 | G1 yanlış alarm oranı (sağlam kareye HATA) | ≤ %30 (bedeli yalnız yeni aday görsel) | (tahmin) |
| B6 | Planların G1'i ilk turda geçme / 2 CORRECTION turu içinde geçme oranı | ≥ %70 / ≥ %95 | (tahmin); B3'te denetimsiz sağlam oran 23/44 = %52 (hesap) |
| B7 | Görüntü, süreklilik ve plan dili kaynaklı video yeniden çekimi **(değişti)** | **≤ %15 klip**; kredi dilimi 0,15 × 4.860 ≈ 729 kredi ≈ 61 klip | [KU2] §2.5 dilim tablosu (hesap; oranlar tahmin); B2'de bütün nedenlerle ≈ %37 |
| B8 | K0 kâğıt üstü süreklilik kapısı | **0 HATA** olmadan görsel üretimi başlamaz | ZAN§7.2 #1, 02§6.2 |
| B9 | Dünya durumu defterinin kapsadığı plan oranı (çözülmüş başlangıç ve bitiş durumu) | **%100** | ZAN§3.7 |
| B10 | Kart kapısı: aynı karakterin kart görünümleri arasında SFace kosinüsü | her çift ≥ 0,45 | (tahmin); 0,363 resmî "aynı kişi" eşiği (02§1.1) |
| B11 | Kart kapısı: iki farklı karakter arasında SFace kosinüsü | **< 0,363** (hedef < 0,25); `bilincli_benzerlik` çiftleri hariç | 0,363 resmî (02§1.1); 0,25 (tahmin) |
| B12 | V1: kullanılan pencerede siyah kare, donma, klip içi istenmeyen kesme | **0** | 02§6.2 V1 |
| B13 | V2: kullanılan pencerede kimlik HATA'sı | **0** (BAYRAK'lar hakem onaylı) | 02§6.2 V2 |
| B14 | Z1 kaynağı olan kliplerde V3 bitiş durumu uyumu | **%100** (uymayan klipten zincir kurulmaz) | Kesin karar 2 ve 3d |
| B15 | Z1 zincir derinliği | **≤ 2**, sonra yeniden demirleme | 02§2.3 |
| B16 | İkinci ve sonraki filmlerde ana karakterlerin kütüphaneden gelen kilitli kartla üretilme oranı | **%100** (hikâye gereği varyant hariç) | Kesin karar 3f |
| B17 | Ders defterinin etkisi: aynı kök nedenle tekrar eden G1 hatası, ders kaydından sonraki 100 planda | önceki 100 plana göre **en az %50 az** | (tahmin); kesin karar 3e |
| B18 **(yeni)** | Kör gözlem kapsamı: yerel ölçümden açık HATA almadan G1'e giren her aday ve her klibin V3 karesi | **%100** | Kesin karar 6; İ-2 |
| B19 **(yeni)** | Z1 dikişi: kaynağın kullanılan son karesi ↔ ardılın ilk kullanılan karesi, DINOv2 kosinüsü ≥ 0,80 | geçişlerin ≥ %90'ı | 02§6.2 K1 eşiği; oran (tahmin) ([YN2] Ö8) |
| B20 **(yeni)** | Makinenin kaçırdığı görsel kopukluk: kurgu seyircisinin bulduğu ama K1Ö/K1/V2'nin bulmadığı geçişlerin oranı | ≤ %10 | 02§7 hedefinin geçiş düzeyi; ölçüm [KU2] İ-1 eşlemesiyle |
| B21 **(yeni)** | Kullanıcıya verilen düzeltme ya da yeniden üretim görseli paketi | **0** | Kullanıcı kuralı (H/gemini-ajan-gorsel, 18.10) |

#### 4.1.4 Ölçek (40 dk film için yaklaşık iş yükü) **(değişti)**
- ≈ 495 plan, ≈ 405 klip (ZAN§2.6). Klip bölmede `kaynak_klip` planının kendi görseli yoktur; başlangıç karesi sayısı ≈ klip sayısıdır.
- **G1 adayları:** 405 planlanmış görsel × 2 aday = 810; Z2 bitiş görselleri ≤ %10 plan ([YN2] Y42) ≈ ≤ 50 × 2 = 100; CORRECTION ≈ %30 plan × 2 aday × ≈ 1,2 tur ≈ 290 → **≈ 1.200 görsel** (hesap; oranlar tahmin).
- **Kartlar:** konuşan karakter ≤ 8 (RE:konusan_karakter_max) × (1 ana + ≤ 2 varyant, [SN1] §7.2) + mekân ≤ 10 ([SN2] İ13) × 2–4 plaka + 10–20 nesne ≈ **60–90 kart × 3 aday ≈ 180–270 görsel** (tahmin).
- **Kör gözlemin göreceği görsel:** G1 ≈ 1.200 + kart ≈ 230 + V3 ≈ 470 (405 klip + %15 yeniden çekim) + G1Z ≈ 100 + K1 BAYRAK soruları ≈ 50 ≈ **2.050 görsel** (tahmin).
- **Token:** 1376×768 görsel ≈ (1376 × 768) / 750 ≈ 1.409 token; 1280×720 ≈ 1.229 token (hesap). Film başına ≈ **3 milyon girdi tokeni** (tahmin).
- **Ajan görevi:** görev başına ≤ 12 görsel (tahmin) → ≈ **175 `kare-tarifcisi` görevi** (tahmin). [CM] §7'nin toplam ajan çağrısı tahminine (≈ 350–450) bu sayı eklenmeli; kullanım sınırı riski §4.9.1 R9'da.

---

### 4.2 Aşama aşama süreç: girdi → iş → çıktı dosyası → geçme şartı → kim yapar

**Yürütme biçimi (bütün adımlar için):** Ajan işleri [CM]'nin görev defterinden geçer: `film.py sonraki` → ana Claude ajanı `GOREV.json` yoluyla başlatır →
SubagentStop kancası çıktıyı doğrular → `film.py bitir`. Betik işleri `film.py` görevi olarak çalışır. Kullanıcının fiziksel işi (Gemini paketi taşıma)
`kullanici_eylemi` görevidir; bitişi dosyadan algılanır. Ana Claude puan vermez, içerik yazmaz, kare yargılamaz.
**Ortam:** `bulut` = Claude Code web (kâğıt + `sahte` ölçüm); `yerel` = kullanıcının Windows'u (görseller, ölçüm modelleri, Flow).

#### 4.2.0 Veo/Flow kısıt matrisi (bütün adımlar buna uyar) **(değişti)**

| Kısıt | Kaynak | Bu alana etkisi |
|---|---|---|
| Veo API: `reference_images` ile `image` (başlangıç) ya da `last_frame` (bitiş) **aynı istekte olmaz**; `image` + `last_frame` birlikte olur | 02§2.1 (`types.py` docstring) | Kimlik başlangıç karesine "pişirilir". Karakterli planda referanslı video modu yok; referans yalnız **görsel** üretiminde verilir. Z2 (başlangıç + bitiş) API'de de yapılabilir |
| Veo API: `image` ile `video` (uzatma) birlikte verilemez | 02§2.1 | Extend ile yeni başlangıç karesi aynı anda olmaz |
| Flow "İçerik öğeleri" iki referansla karakteri kaydırıyor (saç, yaş, yara izi) | FK, BK§6.3 | Karakterli planda yalnız **Kareler** modu (başlangıç [+ bitiş] karesi) |
| Kare başına ≤ 2 karakter referansı; 3'te yüzler karışıyor | KARARLAR, CLAUDE_ICIN, RE:referans_max | Görsel isteğinde karakter başına **tek birleşik kart sayfası**, en çok 2 karakter; karakter dışı referansın (ebeveyn kare, plaka) sınırı ölçülmedi → kalibrasyon partisi |
| Flow "Bitir" (bitiş karesi) çalışıyor, yumuşak geçiş veriyor | FK, H/proje-b2 (16.10) | Z2 hedefli kullanılır |
| Klibin ilk 0,3–1,0 sn'si durağan; son 0,5–1,0 sn'de kayma ve morf riski | ZAN§2.2, RE:kullanim_bas_varsayilan_sn = 0,5, RE:kullanim_son_pay_sn = 0,5 | Zincir karesi ve denetim örnekleri güvenli pencereden alınır; **teknik son kare kullanılmaz** (İ-1) |
| Veo bazen klip içinde kendiliğinden kesme yapıyor | 02§3 | V1'de PySceneDetect |
| Tek model (Omni); Lite ↔ Omni geçişi uyarı getiriyor | BK§8 #3, DERS | Düzeltme için model değiştirilmez |
| Görsel gönderimleri de "olağan dışı" uyarısı alıyor; yoğun görsel turundan sonra hesap işaretlendi | DERS, H/gemini-ajan-gorsel | Toplu görseller Gemini paketinde; Flow'da görsel düzeltmesi sınırlı ve video gününden ayrı **(değişti, İ-13)** |
| Düzeltme ve yeniden üretim görselleri kullanıcıya paket olarak verilmez **(yeni)** | H/gemini-ajan-gorsel (kullanıcı kuralı, 18.10) | `gorsel_duzeltme` zinciri: ücretli API ya da Memmet/Flow |
| Memmet, `SIRALI_GORSEL/` içinde jpg görürse Flow'da görsel üretmez, doğrudan video gönderir **(yeni)** | H/gemini-ajan-gorsel | İçe alma asla doğrudan `SIRALI_GORSEL/`'e yazmaz; yalnız G1 seçimi oraya konur |
| `seed` aynı girdiyle tutarlı sonuç verir (API) | 02§2.1 | Seçilen görselin ve videonun tohumu (varsa) kaydedilir |
| Gemini başlangıç görseli 1376×768 (en-boy 1,792); video 1280×720 (1,778) **(değişti)** | BK§4.1.12, FK; oranlar (hesap) | Zincir karesi en-boy korunarak kullanılır (İ-7); G1 en-boy denetimi 16:9 ±%1 |

#### 4.2.1 Akış şeması (kredi harcayanlar en sonda)
```
[kâğıt]   GS1 evren bağla → GS2 kart tarifleri ║ (yönetmen Y1–Y4) → GS5 defter + K0 → (Y5–Y6, ses kâğıtta) → GS6 görsel istem
[0 kredi] GS3 kart adayları → GS4 kart kapısı + kilit → GS7 adaylar (basamaklı) → GS8 G1 → GS9 CORRECTION (≤ 2 tur → kaçış)
          → GS10 K1Ö + ikinci göz → (animatik + habersiz seyirci: kurgucunun) → GS11 zincir ve dalga planı
[kredi]   GS12 video (akış içi dalgalar) → GS13 V1 → GS14 V2 + V3 → GS15 Z1 karesi + G1Z → (ardıl dalgaya)
[kurgu]   GS16 K1 (kurgu sırasıyla) → GS17 ders defteri + evren güncelleme
[seri başı] GS0 kalibrasyon (ilk filmin P1'i içinde, bir kez)
```

**Orkestratör kodlarıyla eşleme** (kodlar orkestratörün; [CM] / [UM]):
GS1 → A10 başı / V01 · GS2–GS4 → A10 / V01–V03 · GS5 → A07c / K07 + K10 · GS6 → A09 / K09 · GS7–GS10 → A11 / V05–V06 ·
GS11 → A13–A14 arası / V09 ile U01 arası · GS12–GS15 → A14 / U01–U04 · GS16 → A16 / M03–M04 · GS17 → A18 / S01–S02.

#### 4.2.2 Adımlar

**GS0 — Kalibrasyon (yeni; seri başında bir kez, ilk filmin P1'i içinde)**
- **Girdi:** B3'ün etiketli 44 başlangıç karesi (21 bozuk; görseller kullanıcının diskinde, etiket JSON'u depoda, [UM] §7.4); ilk filmin P1'inden seçilen 20 zor plan (iki kişi, el–nesne, yaratık, düşük ışık, profil, sırt, Z1 derinlik 1–2, Z2).
- **İş:** (1) G1 eşikleri etiketli sette kaçırma ≤ %10 olacak biçimde başlatılır. (2) Ölçülür ve karar defterine yazılır: Z1 karesi 1280×720 doğal ↔ 1376×768 (İ-7); Z1 + Z2 aynı klipte morf (§2.5); türev referansı A ↔ B (İ-8); kör görev boyu 12 ↔ 20 görsel (doğruluk düşmüyorsa büyütülür); MediaPipe yaw işaretinin bakış yönüne çevrimi (02§4); YuNet skor eşiği 0,9'un doğrulanması; MediaPipe'ın Python 3.10 Windows tekerleği.
- **Çıktı:** `EVREN/<SERI>/KALIBRASYON.json`, `_RAPOR/KALIBRASYON_<tarih>.json`, `KARAR_DEFTERI.md` satırları.
- **Geçme şartı:** her ölçümün kararı ve gerekçesi yazılı. P1 planları zaten üretileceği için ek kredi yalnız karşılaştırma klipleridir: ≈ 10 klip × 12 = 120 kredi (hesap; klip sayısı tahmin). Bu harcama [UM] hat denetçisinin notuyla görüntü dilimine yazılır.
- **Kim:** betik + `kare-tarifcisi` + `sureklilik-denetcisi` (hakem). **Ortam:** yerel.

**GS1 — Seri evrenini yükle ya da kur**
- **Girdi:** `AYARLAR/FILM_AYAR.json → evren_kok` (Windows'ta `C:\Users\Soysal\Desktop\YZ_FILM\EVREN`); seri kararı (`proje.json → seri`); `EVREN/<SERI>/` (varsa).
- **İş:** Seri yoksa iskelet kurulur (`evren.json`, boş `dunya.json` şablonu). Varsa kilitli kartlar, kimlik bankaları, `KALIBRASYON.json` ve önceki filmin `DURUM_SON.json`'u filme **sürümle bağlanır** (kopya değil). Geriye uyum: `01_KARAKTERLER/<id>.jpg` birleşik kart sayfasının ön görünümünden `evren.py --disa-aktar` ile **kopyalanır** (Windows'ta sembolik bağ yönetici yetkisi ister, [UM] §5.9). Mevcut `SAHNELER.json → karakterler.<id>.ref` şeması bozulmaz.
- **Çıktı:** `<film>/EVREN_BAG.json` (`{seri, karakter: {id: surum}, mekan: {...}, nesne: {...}, durum_son: "DURUM_SON.json@<surum>"}`).
- **Geçme şartı:** bağlanan her dosyanın SHA1'i kayıtla aynı. Değilse hat durur: kart elle değişmiş demektir; kullanıcıya bilgi verilir, `evren.py --surum-ac` yeni sürüm açar.
- **Kim:** betik `evren.py --bagla`. **Ortam:** bulut (JSON) / yerel (görseller).

**GS2 — Kart tarifleri** **(değişti)**
- **Girdi (GIRDI dilimi, [CM] `dilim.py`):**
  - `HIKAYE.json` karakter bölümü: görünür ayırt ediciler, kostüm varyantları, ölçek ([SN2] `karakterler.<id>`)
  - `EVREN/<SERI>/karakterler/<id>/hikaye.json` (varsa): hikâyeye bağlı görünüş öğeleri, `maske`
  - [YN2] `KART_ISTEGI.json`: plaka açıları ve her plakada görünmesi gereken öğeler (`kroki.py` hesabı), kostüm durum varyantları, ölçek isteyen nesneler
  - `dunya.json` (çağ, kumaş, palet, görsel NE YOK listesi, stil eki), kilitli kart listesi, revizyonda `KART_KAPISI.json`
- **İş:**
  - Karakter: `kimlik_en` **bir kez** yazılır, sonra her istemde kelimesi kelimesine tekrarlanır (01§B3). Ad içermez; ≤ 45 kelime (tahmin); yaş rakamı yok. `asimetrik[]` (yara tarafı, örgü tarafı, tek eldiven; ayna yasağının girdisi, ZAN§3.3). `ayirt_edici[]` her öğe için `hikaye_baglayici` ile. Kostüm varyantları (karakter başına ≤ 2), türetilenler `turetildigi` alanıyla. `boy_m`, `goz_yuksekligi_m`, `baskin_el` (hikâyede yazılıysa). Yaratıkta evreler; boy benzetmeyle verilir ("baby/little/young" yazılmaz, DERS filtresi).
  - **Kadro ayrışması:** her karakter siluetten, saç renginden ve kostüm renginden ayırt edilebilir olmalı. Hikâyeye bağlı öğeye dokunulmaz (İ-12).
  - Mekân: `tarif_en`, `notr_durum` (kapı kapalı, ateş sönük; görsel üretici referanstaki nesneleri kopyalıyor, DERS), plaka istekleri `KART_ISTEGI`'nden. **Koordinat yazılmaz.**
  - Nesne: ölçek kartı tarifi (yanında el ya da kaşık, DERS).
  - Kilitli kart yeniden tasarlanmaz; yalnız eksik varyant istenir.
- **Çıktı:** `_KARTLAR/KART_SPEC.json` + `OZET | karakter: 5 | varyant: 4 | mekan: 6 | plaka: 17 | nesne: 11`.
- **Geçme şartı (SubagentStop → `evren.py --spec-dogrula`):** şema geçerli; `kimlik_en` kelime sınırı; filtre ve NE YOK kelimesi yok (`evren.py ne_yok_kelimeleri()`, `hikaye.json` ∪ `dunya.json`, [SN2] §2.7); hikâyeye bağlı öğeler hikâyedekiyle aynı; `KART_ISTEGI`'ndeki her istek karşılanmış. En çok 2 düzeltme, sonra görev `gecersiz`.
- **Kim:** ajan `kart-tasarimcisi`; betik. **Ortam:** bulut. Yönetmenin plan yazımıyla (Y3) **paralel**.

**GS3 — Kart adayları (0 kredi)**
- **Girdi:** `KART_SPEC.json` → `istem_derle.py --kart` → `_KARTLAR/KART_ISTEMLERI.json`; onaylı ana kart (varyantlar için referans, YR A6).
- **İş:** Her kart için **3 aday** (YR A6). Açık gri düz fon.
  - Karakter: **birleşik kart sayfası** = tam boy önden + 3/4 + 2×2 yüz paneli (önden, 3/4 sol, 3/4 sağ, profil) + tam boy arka görünüm (omuz üstü ve arkadan planlar için; "Wren'in saçı koyu çıktı" dersi, BK§4.1.5).
  - Plaka: boş, kişisiz, nötr durum, kroki açısından.
  - Nesne: ölçekli.
  - Gerçekçilik ekleri: insanlara `real costume test photo on ARRI Alexa`; yaratıklara `real animal photography, nature documentary, Weta Workshop practical creature, NOT cartoon, NOT Pixar, NOT plush` (YR A6).
- **Çıktı:** `_KARTLAR/adaylar/<tur>_<id>_<varyant>_<a|b|c>.jpg` (film klasöründe; kilitlenen evrene taşınır).
- **Geçme şartı:** her kart için 3 dosya; uzun kenar ≥ 1376 px.
- **Kim:** sağlayıcı zinciri `gorsel`: `gemini_paket` (büyük toplu paket; kullanıcı taşır) → `gemini_al.py`; kurulumda izin varsa `vertex_gorsel`; testte `sahte`. **Ortam:** yerel (paket bulutta hazırlanabilir).

**GS4 — Kart kapısı, seçim ve kilit (kesin karar 3c ve 3f)** **(değişti)**
- **İş (sırayla):**
  1. Yerel ölçüm (`kart_denetim.py --yerel`): YuNet yüz sayısı = beklenen görünüm sayısı (fazlası HATA); görünümler arası SFace öz tutarlılığı; kadrodaki öteki kilitli karakterlere benzerlik (< 0,363); CLIP "fotoğraf mı, çizim/3B mi"; fon düzlüğü. Plakada: kişi ya da yüz bulunmaması (YuNet + OWLv2 "person").
  2. Kör gözlem (`--kor-gorev` → `kare-tarifcisi`): kart tarifi görülmeden yapılandırılmış döküm. Saç rengi ve biçimi, kostüm parçaları, renkler, iz ve aksesuarın **görüntüdeki** tarafı, çağ dışı öğe (fermuar, modern mont). Plakada görülen öğeler ve görüntüdeki üçte birleri.
  3. Kod karşılaştırır (`--karar`): tarif ↔ gözlem alan alan; NE YOK ihlali HATA; hikâyeye bağlı öğe uyuşmazlığı HATA; plakada `kroki.py`'nin hesapladığı `gorunen[]` öğeleri beklenen üçte birde değilse HATA (iki kaynak) ya da BAYRAK (tek kaynak); iki karakter < 0,363 sağlanamıyor ve fark yalnız hikâyeye bağlı öğedeyse `HATA: ayrisma_kilitli` (İ-12).
  4. Geçen adaylar arasından **sanat seçimi** `yonetmen` `kart_secimi` kipinde yapılır (tür ve ton uyumu; gerekçeli `KART_SECIM.json`). Kod yalnız teknik eleme yapar.
  5. Seçilen kart `evren.py --kilitle` ile kilitlenir: dosya özetleri; kimlik bankası (`.npz`: her görünümün SFace 128 boyutlu vektörü; insan olmayanda DINOv2 kırpıntı vektörleri; plakada DINOv2 kişisiz vektör); karakter başına kalibrasyon başlangıcı.
- **Döngü:** hiçbir aday temiz değilse aynı tarif + CORRECTION ile 3 yeni aday (en çok 2 tur; `gorsel_duzeltme` zinciri, kullanıcı paketi yok). Sonra `kart-tasarimcisi` tarifi değiştirir; hikâyeye bağlı öğe gerekiyorsa senariste `gorunus_degisiklik_istegi` gider.
- **Çıktı:** `EVREN/<SERI>/karakterler/<id>/karakter.json` + kart, yüz, arka dosyaları, banka; `mekanlar/<id>/mekan.json` + plakalar; `nesneler/<id>/nesne.json`; `_RAPOR/KART_KAPISI.json`.
- **Geçme şartı:** her kart kilitli; kadro çiftleri < 0,363 (`bilincli_benzerlik` hariç).
- **Kim:** betik + `kare-tarifcisi` + `yonetmen kart_secimi` + BAYRAK'ta `sureklilik-denetcisi` (hakem). `--onayli` modda kart sayfaları kullanıcıya **bilgi** olarak gösterilir. **Ortam:** yerel.

**GS5 — Dünya durumu defteri ve kâğıt üstü süreklilik kapısı K0 (kesin karar 3b)** **(değişti)**
- **Girdi:** `SAHNELER.json` ([YN2] Y4 `plan_birlestir` çıktısı), sahne sözleşmeleri, `HIKAYE.json` sahne uçları ve `bilgi` katmanı, `EVREN_BAG.json → DURUM_SON`, kroki ve kurulumlar (`kroki.py` kütüphane olarak), kilitli kart listesi.
- **İş (`dunya_defteri.py --derle --denetle`):**
  - [YN2] §4.5.13 çözüm kuralları: `miras` ve gerekçeli `fark`; `etki` katlama; araya kesme yalnız kendi öznesini değiştirir; geri dönüş ayrı zaman çizgisi; klip bölme ara anı; dondurma; derleme tek yönlü; `zanaat`'sız eski planlar eski kurallarla.
  - Olay çıkarma: bitiş − başlangıç farkı olaylara çevrilir (§4.5.6 sözlüğü) ve her olayın bir `etki`li adımı ya da `zaman_atlama` kartı olduğu denetlenir.
  - Sahne sınırında kalıcı özellikler taşınır: yara, kir, ıslaklık, kostüm hasarı, saç durumu, taşınan nesne.
  - `kroki.py` ile görüş hattı (kaybolma), kadraj sırası, 180°, bakış, ışığın kadrajdaki yönü hesaplanır ve `_derlenir`'e yazılır.
  - Kart kapsamı: plandaki her karakter, kostüm varyantı, nesne ve plaka için kilitli kart (ya da açık kart isteği) olmalı.
  - Ses için gereken alanlar ([SM1] §5.8: hava, rüzgâr, gün saati, ateş, nesne durumu, karakter görünümü, kalabalık, `zaman_surekli`) defterden okunabilir hâle getirilir; ses aracı salt okur.
- **Çıktı:** `DUNYA_DEFTERI.json` (§4.5.6), `_RAPOR/K0_SUREKLILIK.json`, HATA varsa `KUYRUK/YENIDEN_YAZ.json` (`{plan, madde, yazar: "yonetmen", sahne}`).
- **Geçme şartı:** **0 HATA** (§4.7.1). BAYRAK'ları `sureklilik-denetcisi` kâğıt kipinde tek tek kapatır ([YN2] Y5 içinde).
- **Kim:** betik; HATA'yı **planı yazan yönetmen örneği** düzeltir (YR altın kural 4). **Ortam:** bulut.

**GS6 — Görsel istemini durumdan derle (kesin karar 2: başlangıç durumu = başlangıç karesi)**
- **Girdi:** çözülmüş `_derlenir.baslangic_durumu`, `zanaat.kadrajdakiler`, `_derlenir` (kadraj konumu, bakış ve ışık yönü, görünmesi gerekenler, dinleyen ağız), kilitli kart dizeleri, plaka ve kamera ağacı ebeveyni, `dunya.json → stil_eki`, onaylı ders istem ekleri.
- **İş (`istem_derle.py --gorsel`):** `gorsel_istem` elle yazılmaz. Sıra: `[kadraj + açı + lens]` + `[her karakter: ad — kimlik_en (aynen) + kostüm tarifi + _derlenir kadraj üçte biri + yüz yönü ve bakış + poz + iki elin ayrı ayrı tutar/yer/şekil hâli]` + `[nesneler: kimde, hangi elde, durumu, kadrajdaki yeri]` + `[mekân tarifi + plakanın gördüğü öğeler + mekân öğesi durumları]` + `[ışık: tek ana kaynak, kadrajdaki yönü, gün saati]` + `[yasaklar: "no other people", "no fire" …]` + `[konuşan ya da dinleyen için "mouth closed"]` + `[stil eki]` (BK§4.1.1; 01§B3).
  - Anlık görüntü kuralı: istemde süren eylem fiili yok (ViMax, 02§2.3). Poz durağan anlatılır ("left arm extended toward the key, fingers 10 cm above it").
  - Kadrajda görünmeyen el `_derlenir.gorunmesi_gerekenler`'de yoksa "hidden behind …" ifadesi açıkça yazılır.
  - Aynı modül `--bitis` ile Z2 bitiş görseli istemini `bitis_durumu`ndan, `--kart` ile kart istemlerini derler.
  - Referans seçimi: kadrajdaki karakterlerin kart sayfaları (≤ 2) + kamera ağacı ebeveyni (plaka, ana kare ya da türev ebeveyni) → `uretim.gorsel.referanslar`. Ebeveynle birlikte toplam ≤ 3 görsel (tahmin; GS0'da ölçülür).
- **Çıktı:** `SAHNELER.json → gorsel_istem`, `gorsel_istem_yedek`, `uretim.gorsel.referanslar`; `_RAPOR/ISTEM_DERLEME.txt` ([YN2] ile ortak).
- **Geçme şartı:** `istem_denetim.py` 0 HATA; kimlik dizesi birebir geçiyor; süren eylem fiili yok; görünen her karakterin iki eli tarifli; çıplak `left/right` yok ([YN2] Y47); girdi imzası kilitli kart sürümlerini içeriyor (İ-5).
- **Kim:** betik. **Ortam:** bulut.

**GS7 — Başlangıç karesi adayları (2 aday, 0 kredi; kamera ağacı basamakları)** **(değişti)**
- **Girdi:** [YN2] `KAMERA_AGACI.json`, derlenmiş istemler, referanslar.
- **İş:** Görsel üretim üç basamaktır. Bir basamağın paketi, önceki basamaktaki ebeveynler G1'den geçince hazırlanır:
  - **Basamak 1:** `baslangic ∈ {kart, ana_kare}` (yeni sahne başları ve kurulumların ana kareleri).
  - **Basamak 2:** `baslangic = turev` (aynı kurulumun sonraki planları; `kurulum_donusu`, `araya_kesme`, `zaman_atlama`).
  - **Basamak 3:** Z1 planlarının **planlanmış görselleri** (animatik ve yedek için) ve Z2 bitiş görselleri (`NNN_son`).
  - Her plan için **2 aday** (`NNN_a`, `NNN_b`; ViMax, 01§A3). Paketler parti düzeyinde toplanır; birbirine bağlı olmayan basamaklar aynı kullanıcı turunda verilir (İ-8).
- **Çıktı:** `SIRALI_GORSEL/_ADAYLAR/NNN_a.jpg`, `NNN_b.jpg` + yan dosya `.json` (sağlayıcı, model, tohum, tarih, istem özeti).
- **Geçme şartı:** her plan için 2 dosya; en-boy 16:9 ±%1, kısa kenar ≥ 720 px. İçe alma `SIRALI_GORSEL/NNN.jpg`'e **asla** yazmaz (Memmet orada jpg görünce görsel üretmez).
- **Kim:** sağlayıcı zinciri `gorsel`: `gemini_paket` (30 planlık, `gemini_paket.py --basamak k --aday 2`) → `gemini_al.py`; izin varsa `vertex_gorsel`; testte `sahte`. Kullanıcı yalnız büyük toplu paketi taşır. **Ortam:** yerel.

**GS8 — G1: başlangıç karesi kapısı (en kritik kapı)** **(değişti)**
- **Girdi:** adaylar, `DUNYA_DEFTERI.json` (beklenen olgular), `_derlenir`, evren bankaları ve `KALIBRASYON.json`, `zanaat.yasaklar` ve sahne yasakları.
- **İş:**
  1. **Yerel ölçüm** (`kare_denetim.py --yerel`; CPU ya da 4 GB GPU):
     - teknik: en-boy, çözünürlük, keskinlik (Laplacian varyansı)
     - yüz sayısı ve kimlik: YuNet + SFace; çok yüzde kadro bankasıyla Macar eşlemesi (`scipy.optimize.linear_sum_assignment`) ve fark payı
     - kadraj sırası ve üçte bir ↔ `_derlenir.kadraj_sirasi`, `kadraj_konumu`
     - bakış: MediaPipe Face Landmarker yaw ↔ `_derlenir.bakis_kadrajda`
     - ağız: `jawOpen` (konuşan planın başlangıcında ve `dinleyen_agiz = kapali` kişilerde)
     - el–nesne: MediaPipe Pose bilekleri + OWLv2 nesne kutusu; Hand Landmarker ikinci görüş; el çevresi büyütülmüş kırpıntıda ikinci arama (küçük nesne)
     - açık parmak: yalnız D/Y kadrajda ve büyük elde
     - insan olmayan karakter ve nesne: OWLv2 kırpıntısı + DINOv2; ölçek (yakındaki insan yüz kutusuna oran)
     - mekân: kişiler maskelenmiş DINOv2 ↔ ebeveyn (plaka ya da ana kare)
     - ışık: Lab ortalaması, yanak parlaklık oranı; stil: CLIP fotoğraf/çizim
     - Açık HATA alan aday kör gözleme gitmeden elenir.
  2. **Kör gözlem** (`kare_denetim.py --kor-gorev` → `kor.py` → görev defteri → `kare-tarifcisi`, görev başına ≤ 12 görsel, görseller anonim `g01.jpg…` ve karışık sırada): iki aşamalı soru formu (§4.5.7). Kritik alanlar iki kez, seçenek sırası karıştırılarak sorulur.
  3. **Kod karar** (`kare_denetim.py --karar`): beklenen ↔ yerel ↔ kör, alan alan (§4.7.3). `p` kimliği ↔ karakter eşlemesi SFace kutusu ve üçte bir konumuyla; görüntü sol/sağı → karakterin kendi sol/sağı `yuz_acisi` ile. İki kaynak aynı hatayı görüyorsa HATA; tek kaynak görüyorsa BAYRAK; ölçülemeyen alan BAYRAK. Geçen adaylardan sabit sırayla biri seçilir: (1) BAYRAK sayısı az, (2) en düşük kimlik fark payı yüksek, (3) mekân benzerliği yüksek, (4) keskinlik yüksek.
  4. **Hakem** (yalnız BAYRAK ve ÖLÇÜLEMEDİ): `sureklilik-denetcisi` kareyi, kartı ve beklenen durumu birlikte görür; GEÇ ya da HATA der, gerekçe zorunlu. İki kaynaklı HATA hakeme gitmez (İ-3).
  5. **Kayıt:** seçilen kare `SIRALI_GORSEL/NNN.jpg`'e konur. SHA1 `SAHNELER.json → denetim.G1` ve `uretim.gorsel`'e yazılır. `dunya_defteri.py --dondur NNN` çözülmüş başlangıç ve bitiş durumunu dondurur ([YN2] İ-11). Kör gözlemin bulguları `DUNYA_DEFTERI.json → gozlenen`'e yazılır ([UM] "planlanan / gözlenen" sütunu).
- **Çıktı:** `_RAPOR/G1_P<n>_B<k>.json` (aday başına ölçüm, gözlem, karar, seçilenin SHA1'i), elenenler `SIRALI_GORSEL/ALTERNATIFLER/` (silinmez), düzeltilecekler `KUYRUK/YENIDEN_URET.json` (`tur: gorsel`, `kaynak_kapi: G1`).
- **Geçme şartı:** planın en az bir adayı GEÇ. `film.py` video aşaması G1 kaydı GEÇ olmayan ya da SHA1'i uyuşmayan planı göndermez.
- **Kim:** betik + `kare-tarifcisi` + gerektiğinde `sureklilik-denetcisi`. **Ortam:** yerel; karar mantığı bulutta `sahte` ölçümle test edilir.

**GS9 — CORRECTION döngüsü (en çok 2 tur) ve kaçış** **(değişti)**
- **Girdi:** `KUYRUK/YENIDEN_URET.json` maddeleri (`plan, aday, alan, beklenen, olculen, gozlenen`).
- **İş:**
  1. **Küçük düzeltme bir kez**, yeniden üretim yapmadan: yatay ayna (yalnız kadraj sırası ya da bakış ters ve `_derlenir.ayna_yasak = false`), kenardan kırpma (her kenarda ≤ %10, tahmin), renk ve parlaklık eşleme (ışık farkı küçükse). İşlem işaret dosyasına yazılır, ikinci kez uygulanmaz (DERS). Düzeltilen kare G1'den yeniden geçer.
  2. Değilse `duzeltme.py` alan farkından **şablonla** CORRECTION cümlesi üretir (§4.5.8). Aynı alan için cümle eklenmez, değiştirilir (istem şişmez). Yanlış kişi hatasında o karakterin kart sayfası ilk referans olur.
  3. 2 yeni aday üretilir → GS8. Sağlayıcı zinciri `gorsel_duzeltme`: `vertex_gorsel` (kurulumda dolar izni varsa) → `flow_gorsel` (Memmet, x2 çıktı, tempo 17.10 değerleri, görsel günü ≠ video günü) → **asla kullanıcı paketi** (İ-13). Düzeltmeler basamak sonunda toplu işlenir.
  4. 2 turda geçmezse **kaçış**: `sureklilik-denetcisi kacis` kök nedeni yazar → `yonetmen onarim` planı değiştirir ([YN2] Y9-b) → plan GS5'ten yeniden geçer → yine geçmezse plan `durdu` olur ve kullanıcıya bilgi verilir (soru değil). Bozuk kare hiçbir koşulda videoya gitmez.
- **Çıktı:** güncel istemler, `_RAPOR/DUZELTME_KAYDI.jsonl`, `_RAPOR/ISARET/NNN.json`, kaçışta `30_YONETMEN/ONARIM_<tur>.json`.
- **Geçme şartı:** kuyruk boş ya da kalan her plan için yazılı yönetmen kararı var.
- **Kim:** betik `duzeltme.py`; Memmet (Flow görsel düzeltmesi; bot atlatma yok, uyarıda dur); kaçışta ajanlar. **Ortam:** yerel.

**GS10 — K1Ö: başlangıç kareleri dizisinde ön geçiş denetimi + ikinci göz** **(değişti)**
- **Girdi:** seçilmiş `SIRALI_GORSEL/NNN.jpg` dizisi, sahne grupları, kurulumlar ve ana kareler.
- **İş (`video_denetim.py --onceden`):** aynı sahne grubundaki ardışık karelerde Lab ΔE ve parlaklık farkı; kurulum dönüşünde o kurulumun ana karesine DINOv2 (ViMax kamera ağacı, 01§A3); kostüm gömmesi (gövde kırpıntısı DINOv2) sahne içinde sabit mi; Z1 planının planlanmış görseli ↔ kaynak planın bitiş görseli (planlı dikiş).
  - **İkinci göz (yeni):** parti sonunda Gemini paketi (GORSELLER + REFERANSLAR + AKIS + SUREKLILIK; H/gemini-ajan-gorsel biçimi). Bulgular yalnız BAYRAK olarak hakeme gider (İ-6).
- **Çıktı:** `_RAPOR/K1ON_P<n>.json` + kare çiftleri `_RAPOR/K1ON_P<n>/cift_NNN_MMM.jpg`; `_RAPOR/IKINCI_GOZ_P<n>.json`.
- **Geçme şartı:** HATA yok. HATA'lı kare GS9'a döner. BAYRAK'lar **kurgucuya ve hakeme** gider, **seyirciye gitmez** ([KU2] İ-1). Animatik seyircisinin görsel bulgularıyla sonradan eşlenir (`bulgu_yonlendir`).
- **Kim:** betik; ikinci göz için kullanıcı paketi taşır. **Ortam:** yerel.

**(Animatik + habersiz seyirci: kurgucunun alanı, [KU2] KR1–KR4.)** Bu alanın katkısı: yalnız G1'den geçmiş kareler; Z2 planlarında başlangıç ve bitiş görselleri arasında çapraz geçiş; seyircinin görsel bulguları `bulgu_yonlendir` üzerinden GS9 kuyruğuna.

**GS11 — Zincir ve dalga planı (kesin karar 3d)** **(değişti)**
- **Girdi:** `zanaat.zincir` (niyet: `gecis_turu`, `onceki_plan`, `baslangic`, `ebeveyn`, `dogal_durak`, `bitis_sabitle`), G1 sonuçları, `_derlenir.kesme_nokta_sn`.
- **İş (`kare_zinciri.py --plan`):** her plan için yöntem (§2.5): **Z0** (G1 karesi), **Z1** (`baslangic: son_kare`), **Z2** (`bitis_sabitle`: Bitir yuvasına sonraki `devam` planının G1'li planlanmış görseli ya da G1'li `NNN_son`).
  - Derinlik: Z1 zinciri ≤ 2; 3. halkada yeniden demirleme.
  - **Akış içi dalgalar:** dalga 1 = Z1 olmayan bütün planlar, zincir başları kuyruğun başında; ardıl plan, kaynağı V1 + V2 + V3 + G1Z'den geçer geçmez kuyruğa girer. Bütün dalganın bitmesi beklenmez. DAG yalnız sırayı belirler, gönderim hızını değil (01§B6); Memmet temposu değişmez.
- **Çıktı:** `uretim.zincir` alanları, `_RAPOR/ZINCIR_PLANI.json`.
- **Geçme şartı:** döngü yok; Z1 kaynağı aynı kurulumda; derinlik ≤ 2; her Z1 kaynağında Y55 penceresi tanımlı; konuşmalı planda Z2 yok (Y56).
- **Kim:** betik. **Ortam:** bulut / yerel.

**GS12 — Video üretimi (kredi; [UM] U01 aşaması) — bu alanın şartları**
- Her gönderimden önce: `denetim.G1.sonuc = GEC` ve dosya SHA1'i kayıtla aynı; Z1 planında kaynak klip V1 + V2 + V3 GEÇ ve zincir karesi G1Z GEÇ; Z2 planında bitiş görseli G1 GEÇ; aynı gün Flow'a yoğun görsel düzeltmesi gönderildiyse video başlamaz ([UM] `flow.gorsel_sonrasi_video`).
- Memmet dalga dalga gönderir (Kareler modu, Omni, 720p, 8 sn). Tempo, uyarıda durma ve reCAPTCHA davranışına bu alan dokunmaz. Olağan dışı uyarısında DUR (BK§6.2).
- **Çıktı:** `SIRALI_VIDEO/NNN.mp4`, `KUNYE/NNN.json` ([UM]).
- **Kim:** `flow` sağlayıcısı (Memmet; bot atlatma yok) ya da izinliyse resmî API. **Ortam:** yerel.

**GS13 — V1: teknik video denetimi** **(değişti)**
- **İş (`kalite_denetim.py --klip`):** `ffprobe` bütünlük ve süre; ffmpeg `blackdetect`, `freezedetect`, `blurdetect`; PySceneDetect `ContentDetector` ile klip içi istenmeyen kesme; ardışık kare ortalama mutlak farkıyla titreme (VBench yöntemi, 02§1.2). Her kusur **zaman damgasıyla** yazılır (`kusurlar[{bas, bit, tur}]`; [KU2] `kirp_oner` girdisi). Replik penceresinde sessizlik **ölçülmez**; tek yeri [SM2] S2.1.
- **Çıktı:** `_RAPOR/V1_P<n>.json`.
- **Geçme şartı:** kullanılacak pencerede 0 HATA. Kusur pencerenin dışındaysa `cozum: kirp` yazılır, kuyruğa madde açılmaz ([KU2] 0 kredi kuralı). Kusur içerideyse önce 0 kredi merdiveni ([KU2] §4.5.5), sonra `KUYRUK/YENIDEN_URET.json` (`kaynak_kapi: V1`).
- **Kim:** betik. **Ortam:** yerel (ffmpeg bulutta da var; test bulutta).

**GS14 — V2 klip içi süreklilik + V3 bitiş durumu** **(değişti)**
- **Girdi:** klip, onaylı başlangıç karesi, `_derlenir.bitis_durumu`, bankalar, `_derlenir.replik_zaman`, `zanaat.ekran_disi_ses`.
- **İş (`video_denetim.py --klip`):**
  - **V2:** 0,5 sn arayla 17 kare (02§6.2): kimlik (SFace / DINOv2), yüz ve kişi sayısı (`kadraja_girer` / `kadrajdan_cikar` adımları dışında değişim HATA), ardışık kare DINOv2 sıçraması (morf, nesne belirmesi), kişi kutusunun x hareketi ↔ `_derlenir.ekran_yonu`, video ilk karesi ↔ onaylı başlangıç karesi sadakati.
  - **Yüz izi (yeni):** replik ve ekran dışı ses pencerelerinde 24 fps YuNet kutusu + SFace kimliği + `jawOpen`, tek geçişte → `_RAPOR/V2_P<n>/NNN_yuz.jsonl`. Ses uzmanının `dudak_denetim.py`'si bu dosyayı okur (İ-10).
  - **V3 (atomik zincirin denetimi):** kesme anındaki kare (`_derlenir.kesme_nokta_sn`; KURGU_PLANI'nda gerçek kesim varsa o) kör gözleme verilir; gözlem `_derlenir.bitis_durumu`'nun kritik olgularıyla karşılaştırılır (nesne kimde ve hangi elde, kişi var mı, kapı ve ateş durumu). Ek ölçüler: her adım penceresinde kare farkı enerjisinin tepesi ([YN2] §4.7.8), adım bitişinde MediaPipe Pose (ör. `uzanir` → dirsek açısı), son 0,5 sn'de durma.
  - **`--dudak` kipi (yeni):** `tts_dudak` çıktısı aynı kareler üzerinde özgün klible karşılaştırılır (§4.7.6).
- **Çıktı:** `_RAPOR/V2V3_P<n>.json`, kare şeritleri `_RAPOR/V2V3_P<n>/NNN_serit.jpg` (hakem için), yüz izi dosyaları; gözlenen bitiş `DUNYA_DEFTERI.json → gozlenen`.
- **Geçme şartı:** kullanılacak pencerede V2 HATA yok; V3 bitiş durumu uyuyor. Uymuyorsa sırayla: (a) daha erken bir kare durumu karşılıyorsa `kullanim` kısaltılır (kurgucu, merdiven #1); (b) yeniden çekim **Z2 bitiş sabitlemesiyle** (bitiş görseli derlenir ve G1'den geçer); (c) iki denemeden sonra yönetmen planı böler. Plan başına en çok 2 yeniden çekim (teknik ve kurgu ortak sayaç).
- **Kim:** betik + `kare-tarifcisi` (V3 karesi) + BAYRAK'ta `sureklilik-denetcisi` (şeridi görerek). **Ortam:** yerel.

**GS15 — Zincir karesini çıkar (Z1) ve G1Z** **(değişti)**
- **Girdi:** V1 + V2 + V3'ten geçmiş kaynak klip A; [KU2] `kirp_oner.py --zincir A` penceresi (son adımın ölçülen bitişi + ≥ 0,2 sn ile `klip_sn − 0,5` arası, [YN2] Y55).
- **İş (`kare_zinciri.py --cikar`):** pencerede her kare puanlanır: keskinlik (Laplacian varyansı) yüksek, hareket enerjisi düşük (bitiş durumunun "tutulduğu" an, RE:bitis_tutma_sn = 0,5), kimlik benzerliği yüksek. En iyi kare tam çözünürlükte çıkarılır, **en-boy korunur** (varsayılan 1280×720; İ-7). Üretken düzeltme yok.
  - **G1Z:** kimlik bantları (§4.7.3); keskinlik; V3 gözlemi aynı kare ya da ±0,2 sn içinde var; defter garantisi (A'nın bitiş olguları = B'nin başlangıç olguları); B'nin G1'li planlanmış görseline DINOv2 (düşükse BAYRAK; planlı ile gerçek arasındaki fark ders defterine).
  - Kurgucu A'nın çıkışını o kareye kilitler (`kullanim_kilit: zincir`).
- **Çıktı:** `SIRALI_GORSEL/NNN.jpg` (B'nin zincir karesi; B'nin planlanmış görseli `_ADAYLAR/NNN_plan.jpg` olarak saklanır), `_RAPOR/ZINCIR_P<n>.json`, `uretim.zincir.{kaynak, kesim_sn, derinlik}`.
- **Geçme şartı:** G1Z GEÇ. Tutmazsa B **Z0'a düşer** (G1'li planlanmış görsel; `yedege_dustu: true`) ve ders defterine yazılır. Derinlik 3'te yeniden demirleme (§2.5).
- **Kim:** betik + kurgucunun kilidi. **Ortam:** yerel.

**GS16 — K1: kurgu sırasıyla geçiş denetimi** **(değişti)**
- **Girdi:** `KURGU/KURGU_PLANI.json` (gerçek `kullanim` değerleri), klipler, dondurulmuş durumlar.
- **İş (`video_denetim.py --gecis`):** A planının son kullanılan karesi ↔ B planının ilk kullanılan karesi.
  - `devam`: DINOv2 ve parlaklık (B19).
  - `eylem_kesme`, `araya_kesme`, `zaman_atlama` (eski adıyla aynı mekânda kesme): Lab ΔE ve parlaklık.
  - `kurulum_donusu`: o kurulumun ana karesine DINOv2.
  - İki karede kimlik; yeni komşu çiftlerde dondurulmuş olgu eşitliği (`dunya_defteri.py --komsuluk`, [YN2] Y58).
- **Çıktı:** `_RAPOR/K1_P<n>.json` + kare çiftleri.
- **Geçme şartı:** HATA yok. Bulgular **kurgucuya ve hakeme** gider, seyirciye gitmez. Seyirci kopukluğuyla aynı geçişi gösteren bulgu `dogrulanmis` olur; yalnız seyircide olan bulgu `kacirma` etiketiyle ders defterine yazılır (B20).
- **Kim:** betik; düzeltme kararı kurgucu ve yönetmen. **Ortam:** yerel.

**GS17 — Ders defteri ve evren güncelleme (kesin karar 3e ve 3f)**
- **Girdi:** bütün kapı raporları, sonradan bulunan hatalar (V2/V3, K1, kurgu seyircisi, kullanıcı notu), CORRECTION kayıtları, defterin son durumu.
- **İş:**
  - Her kapı kararı `ders_defteri.kaydet()` ile ([UM] ortak biçim) "sonra ne oldu" bilgisine bağlanır: `kacirma`, `yanlis_alarm`, `dogru`. [YN2] `plan_ozellik.py` her olaya plan özellik vektörünü ekler.
  - Eşikler korkuluklar içinde kalibre edilir (§4.7.10) → `KALIBRASYON.json`.
  - Tekrarlayan kök neden kural adayı olur; `sureklilik-denetcisi ders` kipi tek cümleye çevirir; terfi `ders-editoru` ile yapılır ([CM]).
  - `evren.py --film-sonu`: `DURUM_SON.json` (defterin son olguları), yeni varyant kartları, onaylı ana kareler (`ana_kareler/<isik>/<K>.jpg`), güncel bankalar.
- **Çıktı:** `YZ_FILM/BILGI/DERS_DEFTERI/` kayıtları, `EVREN/<SERI>/DURUM_SON.json`, `KALIBRASYON.json`.
- **Geçme şartı:** her yeni kural "deneme" durumundadır; kalıcılaşması ölçüme bağlıdır (§4.8.7).
- **Kim:** betik; kural dili `sureklilik-denetcisi`; terfi `ders-editoru`. **Ortam:** herhangi.

**Yayın tarafına küçük katkı:** kapak adayları `kare_denetim.py --serbest` ile kimlik ölçümünden ve kör gözlemden (el, yazı, anatomi) geçer.

---
### 4.3 Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) — yalnız kendi alanım

**İlkeler:**
- Ölçülebilen her şey betikte. Ajan yalnız **görme** (kör gözlem), **anlam** (defterdeki mantık hatası, hakemlik) ve **tasarım** (kart tarifi) işlerinde.
- "Hiçbir model kendi çıktısını onaylamaz" (01§B4): görselleri Gemini ve Veo üretir, Claude denetler; Gemini yalnız ikinci göz bulgusu verir (İ-6).
- Her ajan çağrısı yeni örnektir (yazar ajanın aynı oturumdaki revizyonu hariç, [CM] §2.2-3). Ajanlar birbirinin çıktısını okumaz.
- Bütün ajanlar `model: opus` (claude-opus-5-5), `effort: high`; `fallbackModel` ve `memory:` tanımlanmaz; **Bash yoktur** ([CM] §3.1).
- Okuma ve yazma [CM] `erisim_kapisi` kancasıyla görev klasörüne bağlıdır. Ajan dönüşü ≤ 5 satırdır: çıktı yolu + `OZET` satırı.

#### 4.3.1 `kare-tarifcisi` (yeni; [CM] adı) — görüntüyü beklentiyi bilmeden yazıya döken göz

| Alan | Değer |
|---|---|
| Rol (erisim.json) | `kor`: okuma yalnız `{gorev}/GOREV.json`, `ISTEM.md`, `GIRDI/**`; yazma yalnız `{gorev}/CIKTI/**` |
| Araçlar | `Read, Write` |
| Görev | `GIRDI/SORULAR.json`'daki iki aşamalı formu cevaplar: (1) serbest envanter: kişiler (`p1…`), her kişinin üçte biri, yüz yönü, poz, **görüntünün solundaki ve sağındaki el** ayrı ayrı, kıyafet ve saç, nesneler ve yerleri, ışık kaynakları, gün saati, hava, yazı/logo/filigran, anatomi bozukluğu, fotoğraf mı çizim mi; (2) hedefli sorular `p` kimlikleri üzerinden, sol/sağ her zaman görüntü koordinatında. Emin değilse "cannot tell" seçer, tahmin etmez |
| Okuyacağı | Yalnız `GIRDI/` (anonim `g01.jpg…`, plan numarası yok) ve `SORULAR.json`. Plan, istem, defter, kart, karakter adı **verilmez** |
| Çıktısı | `CIKTI/CEVAP_gNN.json` (§4.5.7). Son satır: `OZET \| gorsel: 12 \| belirsiz_alan: 3` |
| Görev boyu | ≤ 12 görsel (tahmin; GS0'da 12 ↔ 20 ölçülür) |
| Neden ajan | ARIS yöntemi: denetçi beklenen değeri görmeden yazıya döker, karşılaştırmayı deterministik kod yapar (01§B4). "Listeye bakıp karar veren" denetçi onaylama eğilimindedir |

```markdown
---
name: kare-tarifcisi
description: Görüntüyü beklentiyi bilmeden yazıya döken kör gözlemci. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; GIRDI'deki anonim görsellere SORULAR.json'a göre cevap yazar. Her görev yeni örnektir.
tools: Read, Write
model: opus
effort: high
maxTurns: 40
omitClaudeMd: true
---
Sen bir görüntü tarifçisisin. Bu görsellerin ne olması gerektiğini bilmiyorsun ve tahmin etmeye çalışma.
1. GOREV.json'u oku. CIKTI/CEVAP_<gNN>.json dosyalarını hemen boş şablonla oluştur; her görseli bitirdikçe doldur.
2. Her görsel için ÖNCE envanteri yaz: gördüğün her kişiye p1, p2… adı ver; sol ve sağ her zaman GÖRÜNTÜNÜN sol ve sağıdır.
3. SONRA hedefli soruları cevapla. Bir soru sana bir şey söylüyor gibi görünse bile yalnız görüntüde gördüğünü yaz.
4. Emin değilsen "cannot tell" seç. Parmak saymakta zorlanırsan "cannot tell" seç.
5. Son satır: OZET | gorsel: <n> | belirsiz_alan: <n>. Ana oturuma yalnız CIKTI yolunu ve OZET satırını dön.
```

#### 4.3.2 `sureklilik-denetcisi` (var; baştan yazılır) — defterin anlam bekçisi ve hakem

| Alan | Değer |
|---|---|
| Model | `opus`, effort high (mevcut taslak `sonnet`; hakemlik yargı işidir, H/ajan-opus-yuksek) |
| Rol | `denetci` ([CM]): okuma `{gorev}/**` + `.claude/skills/film-yap/*.md`; yazma `{gorev}/CIKTI/**` |
| Araçlar | `Read, Write` |
| Kipler | **kagit** ([YN2] Y5): K0 BAYRAK'larını kapatır; betiğin göremediği anlam hatalarını bulur (fener söndü ama sahnede ışık kaynağı kalmadı; nesne kurulmadan kullanıldı; kostüm hasarı unutuldu). **hakem:** G1, G1Z, V2, V3, K1Ö, K1'deki tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ alanlarını, beklenen durumu, kartı ve kareyi (ya da kare şeridini) **birlikte** görerek GEÇ/HATA'ya çevirir; tek seyircinin görsel KRİTİK'ini kanıtla geçersiz sayabilir ([KU2] §2.6-7); iki kaynaklı HATA'yı göremez. **kacis:** iki CORRECTION turunda geçmeyen planın kök nedenini ve yönetmene öneriyi yazar. **ders:** kural adaylarını tek cümleye çevirir |
| Okuyacağı | GIRDI dilimi: ilgili `DUNYA_DEFTERI` parçası, `_RAPOR/K0_*`, `G1_*`, `V2V3_*` parçaları, kareler ve şeritler, ilgili `karakter.json` ve kart sayfaları, `dunya.json`, `ZANAAT.md` §3.3 ve §3.7, `03_DERSLER.md` |
| Çıktısı | `CIKTI/HAKEM_<kapi>.json`: `[{plan, alan, karar: GEC/HATA, gerekce, kanit}]`; kâğıt kipinde `CIKTI/K0_HAKEM.md`; kaçışta `CIKTI/KACIS.json`. Son satır `OZET \| incelenen: 14 \| GEC: 9 \| HATA: 5` |
| Sınır | İlk gözlemi yapmaz (önyargı). Yalnız betik ile kör gözlem anlaşamayınca ya da ölçüm yapılamayınca karar verir. CORRECTION cümlesi yazmaz (şablon `duzeltme.py`'de) |

#### 4.3.3 `kart-tasarimcisi` (yeni; yazar) — seri kütüphanesinin görsel tarifçisi

| Alan | Değer |
|---|---|
| Rol | `yazar` ([CM]): okuma `{gorev}/**` + film-yap beceri dosyaları; yazma `{gorev}/CIKTI/**`; çıktıyı evrene `evren.py` taşır |
| Araçlar | `Read, Write, Edit, Glob, Grep` (Bash yok; doğrulama SubagentStop'ta `evren.py --spec-dogrula`) |
| Görev | GS2: karakter `kimlik_en` (ad yok), `asimetrik`, `ayirt_edici` (hikâyeye bağlı olanlara dokunmaz), kostüm ve durum varyantları (≤ 2), yaratık evreleri ve ölçek benzetmesi, mekân tarifi ve nötr durum, nesne ölçek kartı. Kadro ayrışmasını sağlar; kart kapısı benzerlik bildirirse yalnız serbest öğeleri ayrıştırır |
| Okuyacağı | GIRDI: `HIKAYE.json` karakter dilimi, `karakterler/<id>/hikaye.json`, `KART_ISTEGI.json`, `dunya.json`, kilitli kart listesi, revizyonda `KART_KAPISI.json`; `BILGI_KURALLARI.md` §4.1, `03_DERSLER.md`, `KARARLAR.md` (kapak kalıbı: insan + yaratık aynı karede) |
| Çıktısı | `CIKTI/KART_SPEC.json`; hikâyeye bağlı öğe gerekiyorsa `CIKTI/GORUNUS_DEGISIKLIK_ISTEGI.json`. Son satır `OZET \| karakter: 5 \| varyant: 4 \| mekan: 6 \| plaka: 17 \| nesne: 11` |
| Neden ayrı ajan | [CM] Ç-10 ölçütü (a): ayrı dosyanın (`KART_SPEC.json`, evrendeki görsel tarif alanları) tek sahibi. Yönetmen yalnız seçer; seçen ile tarif eden aynı olursa kart seçimi kendi tasarımını onaylamaya döner |

#### 4.3.4 Kullandığım ama bu alana ait olmayan ajanlar
- `yonetmen` ([YN2]): `kart_secimi` (GS4), `onarim` (GS9 kaçışı, GS14 bölme), planın yazarı (K0 HATA'larını düzeltir).
- `kurgucu` ([KU2]): K1Ö/K1 bulgularını 0 kredi merdiveninde işler; Z1 çıkışını kilitler.
- `habersiz-seyirci` ([SN2]/[KU2]): animatik ve kurgu kipleri; **K1Ö/K1 adayları verilmez**.
- `ders-editoru` ([CM]): kural terfisi.
- `hat-denetcisi` ([UM]): GS0 karşılaştırma klipleri ve dilim aktarımlarında not.

#### 4.3.5 Gözetimsiz çalışma
`--tam-otomatik` modda ana Claude açık değilse kör gözlem görevi `vlm` sağlayıcısının `claude_api` arka ucuna gider (model `claude-opus-5-5`; anahtar `ANTHROPIC_API_KEY` ya da `AYARLAR/anthropic_anahtar.txt`; asla yazdırılmaz). Aynı `ISTEM.md` şablonu ve aynı `GIRDI/` kullanılır. Testte `sahte` arka uç yan dosyadaki gerçeği döndürür. API ücretlidir; fiyat bu belgede yazılmadı, kurulumda `claude-api` başvurusundan okunur.

---

### 4.4 Beceri (skill) tarif adımları — kendi alanım

**Yer:** `.claude/skills/film-yap/reference/goruntu_sureklilik.md` (≤ 300 satır, başında içindekiler; 03§B4). SKILL.md'den "kart, görsel, G1, zincir, video denetimi" satırıyla tek seviye bağlanır. Ana Claude bu adımları kendisi yürütmez: `film.py sonraki` ne görev verirse onu dağıtır ([CM] döngüsü). Bu dosya, görevlerin ne yaptığını ve takılınca ne yapılacağını anlatır.

#### 4.4.1 En üstte duracak 7 kural (sıkıştırmadan sonra da ilk 5.000 tokende kalsın, 03§B4)
1. **G1 (ya da G1Z) GEÇ kaydı ve SHA1 eşleşmesi olmayan hiçbir kare videoya gitmez.** Elle kare koymak kapıyı atlatmaz.
2. Kör gözlemciye plan, istem, defter, kart ya da ad verilmez. Yalnız `GIRDI/`.
3. `gorsel_istem` elle yazılmaz; `istem_derle.py --gorsel` durumdan derler. Hata istemde görünüyorsa kaynağı (durum ya da kart alanı) düzeltilir.
4. CORRECTION en çok 2 tur; sonra yönetmen planı değiştirir. Hakem HATA'yı GEÇ'e çeviremez. Bozuk kareyle "idare etme" yok (kesin karar 6).
5. Düzeltme ve yeniden üretim görselleri kullanıcıya paket olarak verilmez (ücretli API ya da Memmet/Flow).
6. Flow'da "olağan dışı etkinlik"te, reCAPTCHA'da, kredi bitince DUR. Görsel düzeltmeleri Flow'a hızlı ve yoğun gönderilmez; görsel günü video günü değildir.
7. Kart, görsel ve video asla silinmez; `ALTERNATIFLER/`, `_ADAYLAR/` ya da `_ESKI/` altına taşınır (BK§6.5).

#### 4.4.2 Görev listesi (`film.py sonraki`'nin bu alandaki görevleri; kopyala, işaretle)
```
GÖRÜNTÜ VE SÜREKLİLİK — <film>
- [ ] T0  (betik) evren.py --bagla                          → EVREN_BAG.json; SHA1'ler eşleşti
- [ ] T1  (ajan)  kart-tasarimcisi                          → KART_SPEC.json; SubagentStop: evren.py --spec-dogrula
- [ ] T2  (kullanıcı) kart paketi (gemini_paket --kartlar)  → GELENLER/*.zip görülünce gemini_al → _KARTLAR/adaylar/
- [ ] T3  (betik) kart_denetim --yerel → (ajan) kare-tarifcisi × N → (betik) kart_denetim --karar
          → (ajan) yonetmen kart_secimi → (betik) evren.py --kilitle
- [ ] T4  (betik) dunya_defteri.py --derle --denetle        → K0 = 0 HATA; BAYRAK'lar sureklilik-denetcisi kagit
- [ ] T5  (betik) istem_derle --gorsel → istem_denetim      → 0 HATA
- [ ] T6  (kullanıcı) basamak k paketi (gemini_paket --basamak k --aday 2) → _ADAYLAR/
- [ ] T7  (betik) kare_denetim --yerel → (ajan) kare-tarifcisi × N → (betik) --karar → (ajan) hakem (yalnız BAYRAK) → (betik) --karar --hakem
          → seçim + SHA1 + dondurma; basamak k+1 için T6'ya
- [ ] T8  (betik) duzeltme.py → gorsel_duzeltme zinciri → T7 (≤ 2 tur) → kaçış: sureklilik-denetcisi kacis → yonetmen onarim → T4
- [ ] T9  (betik) video_denetim --onceden; (kullanıcı) ikinci göz paketi → K1Ö raporu kurgucuya ve hakeme
- [ ] T10 (betik) kare_zinciri --plan                       → ZINCIR_PLANI; akış içi dalgalar
- [ ] T11 video dalgaları: kalite_denetim --klip (V1) → video_denetim --klip (V2 + yüz izi) → kare-tarifcisi (V3)
          → --karar → kirp_oner --zincir (kurgu) → kare_zinciri --cikar (G1Z) → ardıl kuyruğa
- [ ] T12 (betik) video_denetim --gecis (K1)                → kurgucuya ve hakeme; seyirci bulgusuyla eşleme
- [ ] T13 (betik) ders_defteri.kaydet / --derle → evren.py --film-sonu
```

#### 4.4.3 Takılınca ne yapılır

| Durum | Ne olur |
|---|---|
| `evren.py --bagla` SHA1 uyuşmazlığı | Hat durur; kullanıcıya bilgi: "Mara'nın kartı elle değişmiş görünüyor; yeni sürüm açıldı" (soru değil). `evren.py --surum-ac` |
| Kart kapısı 2 turda geçmedi | `kart-tasarimcisi` tarifi ayrıştırır; hikâyeye bağlı öğe gerekiyorsa `GORUNUS_DEGISIKLIK_ISTEGI` senariste |
| K0 HATA | `YENIDEN_YAZ` → sahneyi yazan yönetmen örneği |
| G1 iki turda geçmedi | Kaçış merdiveni (GS9-4) |
| Kör gözlem ajanı bozuk JSON döndü | SubagentStop en çok 2 düzeltme ister; sonra görev `gecersiz`, **yeni örnekle** yeniden (değerlendirici yarım işi sıfırdan yapılır, [CM] §2.3) |
| Ölçüm modeli kurulu değil | Sonuç `ÖLÇÜLEMEDİ` → BAYRAK → hakem. Hiçbir zaman sessizce GEÇ değil. `kurulum.py --kontrol` raporu kullanıcıya bilgi olarak verilir |
| Flow uyarısı, reCAPTCHA, kredi bitti | Memmet durur ([UM] `Kisitlandi`); bu alan hiçbir otomatik yeniden deneme yazmaz |
| Z1 dalgasında ana Claude kapalı | V3 kör gözlemi `vlm: claude_api` ile sürer; anahtar yoksa ardıllar bir sonraki oturumu bekler (bilgi mesajı) |

#### 4.4.4 Durma kuralları (bu alanda ana Claude kullanıcıya **bilgi** verir; soru sormaz)
- Flow uyarısı, reCAPTCHA ya da kredi bitmesi; atlatma yok.
- Bütçe sınırı (`URETIM_ONIZLEME.json`) yeniden üretimle aşılacaksa.
- Bir plan kaçıştan sonra da G1'i geçemiyorsa: plan numarası, 4 adayın küçük resmi ve kök neden tek mesajla bildirilir; ekip yine bir yol önerir.
- Kart kilidi değişecekse (ör. kullanıcı kendiliğinden itiraz etti): seri kütüphanesi değişikliği geriye dönük etkiler; yeni sürüm açılır.

#### 4.4.5 Değerlendirme senaryoları (beceri tetiklenmesi ve davranış testi, 03 öneri 12)
1. "Parti 2'nin görsellerini denetle" → T7 çalışır; kör gözlem paketinde plan numarası, ad ve istem yoktur.
2. "Mara'nın eldiveni yanlış elde, düzelt" → kaynak durum alanı ve CORRECTION şablonu; elle istem yazılmaz.
3. "Yeni filme başla, aynı seri" → T0 kilitli kartları bağlar, yeniden tasarım istenmez.
4. "Videoları üret" G1'i geçmemiş plan varken → o plan gönderilmez ve nedeni söylenir.
5. **(yeni)** Z1 kaynağı V3'ten geçmedi → ardıl plan G1'li planlanmış görsele düşer, ders kaydı yazılır.
6. **(yeni)** Hakem dosyasında iki kaynaklı HATA alanına GEÇ yazılmış → `kare_denetim --karar` reddeder.

---

### 4.5 Veri şeması / plan alanları (JSON örneğiyle)

İlke: mevcut `SAHNELER.json` alanları (`no, parti, referans, gorsel_istem, hareket_istem, amac, duygu, replik, kullanim, bitis_karesi, motor`) değişmez; eski dosyalar çalışmaya devam eder.
Plan alanlarının sahipliği [YN2] §4.5.2 tablosundadır. Bu alan **yazdığı** plan alanları: `gorsel_istem*` (`istem_derle --gorsel`), `uretim.gorsel`, `uretim.zincir`, `uretim.durum_dondu` (`dunya_defteri --dondur`), `denetim.{G1, G1Z, V1, V2, V3, K1}`. **Okuduğu** alanlar: `zanaat.*` ve `_derlenir.*`.

#### 4.5.1 Seri evreni klasörü (`<evren_kok>/<SERI>/`) **(değişti; sahip başına ayrı dosya)**
```
EMBERFALL/
  evren.json            seri adı, sürüm, bağlı filmler                                (evren.py)
  dunya.json            stil eki, palet, kumaş, gerçekçilik ekleri, görsel NE YOK      (görüntü)
  hikaye.json           dönem, kurallar, hikâye NE YOK, kanon, ad sözlüğü              (hikâye, [SN2])
  karakterler/mara/     karakter.json · kart_k1_v2.jpg (birleşik sayfa) · yuz_v2.jpg · arka_k1_v2.jpg
                        banka_v2.npz (SFace/DINOv2 vektörleri) · eski/                 (görüntü)
                        hikaye.json (maske, hikâyeye bağlı görünüş, yay)               (hikâye)
                        ses.json + ses/ (banka, dönüşüm modeli)                         (ses, [SM2])
  karakterler/ember/    karakter.json · kart_evre1_v1.jpg · olcek_evre1_v1.jpg · banka_v1.npz
  mekanlar/mara_kulubesi/
                        kroki.json · kurulumlar.json                                   (yönetmen, [YN2])
                        mekan.json · plaka_ic_guneye_v1.jpg … · ana_kareler/<isik>/<K>.jpg
                        durum_ocak_yanik_ic_guneye.jpg                                 (görüntü)
                        ses.json                                                       (ses)
  nesneler/demir_anahtar/ nesne.json · kart_olcekli.jpg (görüntü) · ses.json (ses)
  EKRAN_YONU.json       seri boyunca coğrafya yönü                                     (yönetmen)
  muzik/                leitmotifler                                                   (ses)
  sablonlar/            kart, jenerik, CapCut düzeni                                   (kurgu)
  DURUM_SON.json        son filmin fiziksel bitiş durumu (sonraki filmin başlangıcı)    (görüntü)
  KALIBRASYON.json      karakter ve kapı başına ayarlanmış eşikler ve geçmişi           (görüntü)
  IZLEYICI_OZETI.md     (betik, [SN2])
```
Kök `AYARLAR/FILM_AYAR.json → evren_kok`; kullanıcının mevcut yolları bozulmaz. Bütün dosyaları yalnız `evren.py` yazar (alt komutlarla, sahip başına). Git'e yalnız JSON'lar girer; görseller, `.npz` ve sesler yerelde kalır ve D'ye yedeklenir ([UM] §5.9). Ders defteri evrende değil, `YZ_FILM/BILGI/DERS_DEFTERI/` altındadır (İ-11).

#### 4.5.2 `karakter.json` (insan) **(değişti)**
```json
{
 "id": "mara", "seri": "EMBERFALL", "tur": "insan", "surum": 2, "durum": "kilitli",
 "kimlik_en": "an adult woman with one long dark-auburn braid over her LEFT shoulder, pale weathered skin, a thin pale scar through her RIGHT eyebrow, grey-green eyes",
 "asimetrik": ["braid over LEFT shoulder", "scar through RIGHT eyebrow"],
 "ayirt_edici": [
  {"oge": "dark-auburn braid", "tur": "sac", "hikaye_baglayici": true},
  {"oge": "cream fleece collar", "tur": "kostum", "hikaye_baglayici": false},
  {"oge": "long shearling coat silhouette", "tur": "siluet", "hikaye_baglayici": false}
 ],
 "bilincli_benzerlik": [],
 "kostumler": {
  "k1": {"tarif_en": "dark-brown shearling coat with cream fleece collar and cuffs, brown leather gloves, olive wool trousers, tall worn leather boots",
         "kart": "kart_k1_v2.jpg", "arka": "arka_k1_v2.jpg"},
  "k1_yirtik": {"turetildigi": "k1", "fark_en": "the left coat sleeve torn open at the forearm",
                "kart": "kart_k1_yirtik_v1.jpg", "olay_plani": 118}
 },
 "varsayilan_kostum": "k1",
 "yasak": ["zipper", "modern jacket", "makeup", "jewelry"],
 "boy_m": 1.70, "goz_yuksekligi_m": 1.58, "baskin_el": "sag",
 "kartlar": {"sayfa": "kart_k1_v2.jpg", "yuz": "yuz_v2.jpg", "arka": "arka_k1_v2.jpg"},
 "olcum": {"yontem": "sface", "banka": "banka_v2.npz", "gorunum_sayisi": 6,
           "esik_gec": 0.45, "esik_hata": 0.363, "fark_payi_min": 0.05,
           "kalibrasyon_ref": "../../KALIBRASYON.json#mara"},
 "hikaye_ref": "hikaye.json", "ses_ref": "ses.json",
 "hash": {"kart_k1_v2.jpg": "3f9a…", "yuz_v2.jpg": "b71c…", "banka_v2.npz": "90de…"},
 "gecmis": [{"surum": 1, "tarih": "2026-10-13", "neden": "pilot"},
            {"surum": 2, "tarih": "2026-10-24", "neden": "yara izi tarifi ve yüz paneli eklendi"}]
}
```
- `kimlik_en` **ad içermez**. Derleyici istemde `Mara — {kimlik_en}` yazar (§2.1). Sayılar (`boy_m` vb.) örnektir.
- İnsan olmayan karakter farkı: `"tur": "yaratik"`, `"olcum": {"yontem": "dinov2", "bulucu_sorgu": "a dark grey dragon with glowing orange cracks", "esik_bayrak": 0.5}`, `"evreler": {"evre1": {"olcek": {"boy_cm": 40, "benzetme": "house cat size"}, "kart": "kart_evre1_v1.jpg", "olcek_karti": "olcek_evre1_v1.jpg"}}`. "baby/little/young" yazılmaz (DERS).

#### 4.5.3 `mekan.json` **(değişti: kroki yok, ambiyans yok)**
```json
{
 "id": "mara_kulubesi", "surum": 1, "kroki_ref": "kroki.json@1",
 "tarif_en": "a cramped log cabin interior, rough plank floor, low smoke-blackened beams",
 "notr_durum": {"kapi": "kapali", "ocak_atesi": "sonuk", "pencere_kepenk": "kapali"},
 "plakalar": {
  "ic_guneye": {"gorsel": "plaka_ic_guneye_v1.jpg", "sha1": "51ab…", "durum": "kilitli", "banka": "plaka_ic_guneye_v1.npz",
                "gorunen_denetim": {"kapi": "orta", "pencere": "sol_ucte_bir"}},
  "dis_guneybati": {"gorsel": "plaka_dis_guneybati_v1.jpg", "sha1": "77c0…", "durum": "kilitli"}
 },
 "durum_gorselleri": {"ocak_atesi=yanik@ic_guneye": "durum_ocak_yanik_ic_guneye.jpg"},
 "ana_kareler": {"gece_mesale": {"K1": "ana_kareler/gece_mesale/K1.jpg", "K3": "ana_kareler/gece_mesale/K3.jpg"}},
 "ses_ref": "ses.json"
}
```
- Plakaların konumu ve yönü `kroki.json → plakalar.<id>`'dedir (yönetmen). `gorunen_denetim`, `kroki.py`'nin hesapladığı "görünmesi gereken öğeler"in kart kapısındaki sonucudur.
- Plakalar **boş ve nötr durumdadır** (kişi yok, ateş sönük, kapı kapalı), çünkü görsel üretici referanstaki nesneleri kopyalıyor (DERS). Durum istemle ve gerekirse `durum_gorselleri` ile verilir.

#### 4.5.4 `nesne.json`
```json
{"id": "demir_anahtar", "tarif_en": "a hand-forged black iron key, finger-length, with a ring bow",
 "boy_cm": 9, "olcek_karti": "kart_olcekli.jpg", "olcek_kart_tarifi": "held between a thumb and index finger for scale",
 "bulucu_sorgu": "an iron key", "asimetrik": false, "kurulum_plani": 42, "ses_ref": "ses.json"}
```

#### 4.5.5 Plan alanları: bu alanın okuduğu ve yazdığı kısım **(değişti)**
Durum nesnesi [YN2] §4.5.7 biçimindedir (yalnız olgu). Benim eklediğim tek alan `gorunum.sac` (kalıcı saç durumu). Örnek: [YN2] §4.8.2-d'deki S07 zinciri, plan 071.
```json
{
 "no": 71, "sira": 71, "parti": 1, "referans": ["mara"],
 "gorsel_istem": "(istem_derle --gorsel)", "hareket_istem": "(istem_derle --hareket)",
 "kullanim": {"bas": 0.6, "sure": 4.6},
 "zanaat": {
  "kod": "S07-P11", "sahne_grubu": "S07", "plan_tipi": "eylem", "klip_sn": 8, "kaynak_klip": null,
  "kamera": {"kurulum": "K3", "kadraj": "OG", "aci": "goz_hizasi", "hareket_tipi": "sabit"},
  "eksen_gecis": false,
  "kadrajdakiler": [{"id": "mara", "olcek": "OG", "yuz_acisi": "3/4", "konusur": false, "kimlik_demiri": false}],
  "baslangic_durumu": "miras",
  "eylem_zinciri": [
   {"id": "a1", "bas": 0.5, "bit": 2.0, "ozne": "mara", "tur": "mikro", "fiil": "bakis_kaydirir", "hedef": "kapi",
    "etki": {"mara.bakis.hedef": "kapi"}},
   {"id": "a2", "bas": 2.0, "bit": 5.0, "ozne": "mara", "tur": "fiziksel", "fiil": "yurur", "hedef": "M1", "olcu": "iki_yavas_adim",
    "etki": {"mara.isaret": "M1"}}
  ],
  "bitis_durumu": "derlenir",
  "zincir": {"gecis_turu": "devam", "onceki_plan": 70, "baslangic": "son_kare", "ebeveyn": "070@kesme",
             "dogal_durak": true, "bitis_sabitle": false},
  "kesme": {"tip": "eylem", "ses_tasma_sn": 0.0},
  "yasaklar": ["ucuncu_kisi", "ikinci_isik_kaynagi"],
  "ekranda_bilgi": "Mara pencereden gelen sesi duyup kapıya yürüyor.",
  "risk_uretim": "dusuk"
 },
 "_derlenir": {
  "baslangic_durumu": {"karakterler": {"mara": {"isaret": "M3b", "poz": "ayakta", "yuz_yonu": "bati", "bakis": {"hedef": "pencere"},
                       "kostum": "k1", "gorunum": {"kir": 1, "islak": false, "yaralar": [], "sac": "orgulu"},
                       "eller": {"sag": {"tutar": "fener", "yer": "kalca_hizasi", "sekil": "tutus_tam"},
                                 "sol": {"tutar": null, "yer": "yanda", "sekil": "serbest"}}}},
                       "nesneler": {"fener": {"kimde": "mara", "el": "sag", "durum": "yanik"}},
                       "mekan_durumu": {"kapi": "kapali", "ocak_atesi": "yanik"}},
  "kadraj_konumu": {"mara": "orta"}, "kadraj_sirasi": ["mara"], "bakis_kadrajda": {"mara": "kadraj_solu"},
  "isik_kadrajda": {"ana": "sag (ocak)"}, "ekran_yonu": "sagdan_sola", "ayna_yasak": true,
  "gorunmesi_gerekenler": {"kisiler": ["mara"], "eller": ["mara.sag", "mara.sol"], "nesneler": ["fener"]},
  "kesme_nokta_sn": 5.2, "dinleyen_agiz": null, "acik_parmak": {"mara.sag": 0, "mara.sol": null}
 },
 "uretim": {
  "gorsel": {"saglayici": "gemini_paket", "basamak": 3, "aday": "b", "tur": 1, "sha1": "9c1e…",
             "referanslar": ["EVREN:karakterler/mara/kart_k1_v2.jpg", "SIRALI_GORSEL/070.jpg"], "tohum": null},
  "zincir": {"dalga": 2, "kaynak": "SIRALI_VIDEO/070.mp4@6.6", "kesim_sn": 6.6, "derinlik": 1,
             "yedek": "SIRALI_GORSEL/_ADAYLAR/071_plan.jpg", "yedege_dustu": false},
  "durum_dondu": {"bas_ozet": "c41f…", "bit_ozet": "9a07…", "zaman": "2026-10-30T21:12"}
 },
 "denetim": {"G1": {"sonuc": "GEC", "sha1": "9c1e…", "rapor": "_RAPOR/G1_P1_B3.json#071"},
             "G1Z": {"sonuc": "GEC", "sha1": "e04b…", "rapor": "_RAPOR/ZINCIR_P1.json#071"},
             "V1": null, "V2": null, "V3": null, "K1": null}
}
```
- Plan 071 Z1 planıdır: G1 kaydı planlanmış görselindir (animatik ve yedek); video başlangıcı G1Z kaydındaki zincir karesidir. Memmet video aşamasında hangisinin kullanılacağını `uretim.zincir.yedege_dustu`'dan okur.
- `_derlenir` alanlarını yalnız kod yazar ([YN2] §4.5.10); elle yazılırsa `plan_sema.py` HATA verir.

#### 4.5.6 `DUNYA_DEFTERI.json` **(değişti)**
```json
{
 "film": "EMBERFALL_F2", "evren": "EMBERFALL", "surum": 3, "girdi_imza": "5d2e…",
 "baslangic": {"kaynak": "EVREN/EMBERFALL/DURUM_SON.json@4",
               "karakterler": {"mara": {"kostum": "k1", "gorunum": {"kir": 1, "islak": false, "yaralar": [], "sac": "orgulu"}}},
               "nesneler": {"fener": {"kimde": "mara", "el": "sag", "durum": "yanik"}, "demir_anahtar": {"nerede": "masa"}},
               "zaman": {"gun": 1, "gun_saati": "gece", "hava": "kar", "ruzgar": 1}},
 "zaman_cizgileri": {"ana": {"planlar": [1, 2, 3]}, "gecmis_1": {"planlar": [140, 141], "sure_sn": 14}},
 "planlar": {
  "070": {"kaynak": "miras", "bas": {"...": "durum nesnesi"}, "bit": {"...": "durum nesnesi"},
          "bas_ozet": "c41f…", "bit_ozet": "9a07…", "olaylar": ["o112"]}
 },
 "olaylar": [
  {"id": "o112", "plan": 70, "adim": "a1", "tur": "yer_degis", "kim": "mara", "deger": "M3b"},
  {"id": "o140", "plan": 118, "adim": "a2", "tur": "kostum_degis", "kim": "mara", "deger": "k1_yirtik"},
  {"id": "o151", "plan": 131, "tur": "zaman_atla", "deger": {"gun_saati": "sabah"}, "gosterim": "yer_zaman_karti"}
 ],
 "sahne_uclari": {"S07": {"giris": {"...": "sözleşme"}, "cikis": {"...": "sözleşme"}, "hikaye_alt_kume": true}},
 "hikaye": {"kaynak": "HIKAYE.json#bilgi", "salt_okunur": true},
 "ses_alanlari": {"S07": {"hava": "kar", "ruzgar": 1, "ates": {"ocak_atesi": "yanik"}, "kalabalik": "yok", "zaman_surekli_onceki": true}},
 "gozlenen": {"071": {"G1": {"rapor": "_RAPOR/G1_P1_B3.json#071", "uyum": true},
                      "V3": {"rapor": "_RAPOR/V2V3_P1.json#071", "uyum": false, "fark": {"fener.el": {"beklenen": "sag", "gozlenen": "sol"}}}}},
 "dondurulmus": {"071": {"bas_ozet": "c41f…", "bit_ozet": "9a07…"}}
}
```
**Olay türleri (sabit sözlük):** `nesne_al`, `nesne_birak`, `nesne_ver` (el değiştirme), `nesne_el_degis` (aynı kişide el değişimi), `nesne_durum` (yanar, söner, kırılır), `kostum_degis`, `kostum_durum` (kapüşon indi), `gorunum_degis` (kir, ıslaklık, yara, saç), `giris`, `cikis`, `yer_degis`, `mekan_durum`, `isik_degis`, `zaman_atla`.
Her olayın `eylem_zinciri`nde `etki`si olan bir adımı, `zaman_atla` için ekranda bir kartı ya da geçişi olmak zorundadır (K0.4).

#### 4.5.7 Kör gözlem: `SORULAR.json` ve `CEVAP_gNN.json` **(değişti: iki aşamalı form)**
```json
{
 "is_id": "G1_P1_B3_07", "gorseller": ["g01.jpg", "g02.jpg", "g03.jpg"],
 "envanter": {
  "alanlar": ["kisiler", "nesneler", "isik_kaynaklari", "gun_saati", "hava", "yazi_logo", "anatomi", "stil"],
  "kisi_alanlari": ["p_kimligi", "ucte_bir", "yuz_yonu", "poz", "yuz_gorunur", "el_goruntu_solu", "el_goruntu_sagi", "kiyafet", "sac"]
 },
 "hedefli": {
  "g01.jpg": [
   {"k": "q1", "soru": "How many people (any visible face or body, including background) are in the image?", "secenek": ["0", "1", "2", "3 or more"]},
   {"k": "q2", "soru": "For EACH person you listed, what does the hand on the IMAGE-LEFT side of that person hold?", "secenek": ["a lit lantern", "a key", "nothing, open hand", "not visible", "cannot tell"], "kisi_basina": true},
   {"k": "q2b", "tekrar_of": "q2", "secenek_karisik": true},
   {"k": "q3", "soru": "Is there any open flame or glowing light source other than one carried by a person?", "secenek": ["yes", "no", "cannot tell"]},
   {"k": "q4", "soru": "Which part of the image shows a closed wooden door?", "secenek": ["left third", "middle", "right third", "no door visible"]}
  ]
 }
}
```
```json
{
 "gorsel": "g01.jpg",
 "kisiler": [{"p": "p1", "ucte_bir": "orta", "yuz_yonu": "kadraj_solu", "poz": "standing", "yuz_gorunur": true,
              "el_goruntu_solu": "empty, fingers relaxed", "el_goruntu_sagi": "holds a lit lantern at hip height",
              "kiyafet": "dark-brown shearling coat, cream collar, leather gloves", "sac": "long dark-auburn braid"}],
 "nesneler": [{"ad": "lantern", "yer": "middle, held by p1"}],
 "isik_kaynaklari": [{"tur": "lantern", "yer": "middle"}, {"tur": "fireplace glow", "yer": "right third"}],
 "gun_saati": "night", "hava": "not visible", "yazi_logo": "none", "anatomi": "none", "stil": "photograph",
 "cevaplar": {"q1": "1", "q2": {"p1": "nothing, open hand"}, "q2b": {"p1": "nothing, open hand"}, "q3": "yes", "q4": "middle"},
 "belirsiz": []
}
```
- Sorular `kor.py` ile `_derlenir.gorunmesi_gerekenler`'den, durum olgularından ve yasaklardan üretilir. Seçenekler beklenen değeri ve yanlış değerleri birlikte içerir, sırası her görsel için karıştırılır. Metinde ad, kostüm ve rol yoktur.
- **Kod çevirisi:** `p` kimliği karaktere SFace kutusu ve üçte bir konumuyla eşlenir. Görüntünün solundaki el, kameraya dönük ya da 3/4 kişide (`yuz_acisi` `on` ya da `3/4`) kişinin **sağ** elidir; sırtı dönükte (`sirt`) soludur; profilde kritik el sorusu "belirsiz" sayılır ve hakeme gider (02§4 MediaPipe ayna uyarısı).
- Yukarıdaki örnek plan 071'in `a` adayıdır (`b` adayı geçti, §4.5.9). p1 = Mara, yüz kadraj soluna (3/4) dönük. Görüntünün sağındaki el = Mara'nın sol eli → fener **sol** elde gözlendi; beklenen **sağ**. Yerel ölçüm de solu buldu → HATA `nesne_el`.

#### 4.5.8 `KUYRUK/YENIDEN_URET.json` maddesi ve CORRECTION şablonları **(değişti: ortak şema)**
[UM] §5.4 tabanı + [KU2] §4.5.5 alanları + bu alanın alanları (`alan`, `beklenen`, `olculen`, `gozlenen`, `aday`):
```json
{"id": "YU-G1-P1-B2-014", "plan": 57, "tur": "gorsel", "kaynak_kapi": "G1", "kaynak_rapor": "_RAPOR/G1_P1_B2.json#057",
 "kok_neden": "nesne_el", "seviye": "HATA", "alan": "nesne_el", "aday": ["a", "b"],
 "beklenen": {"fener": "sag"}, "olculen": {"yerel": "sol", "guven": 0.71}, "gozlenen": {"kor": "sol", "tutarli": true},
 "cozum": "yeniden_uret",
 "duzeltme": "CORRECTION: the lit lantern is in Mara's RIGHT hand at hip height; her LEFT hand is empty, fingers relaxed.",
 "sifir_kredi": {"denendi": true, "basamaklar": ["ayna"], "gerekce": "_derlenir.ayna_yasak = true (elde nesne)"},
 "saglayici_zinciri": "gorsel_duzeltme", "deneme": 1, "deneme_max": 2, "durum": "bekliyor", "karar_veren": null}
```
- `tur: gorsel` ve `tur: kart` maddeleri 0 Flow kredisidir; yine de 0 kredi alanı doldurulur (küçük düzeltme denendi mi).
- `tur: video` maddeleri [KU2] dilim kurallarına uyar (`dilim: goruntu`, `zincir_etkisi`).

| Alan | CORRECTION şablonu (EN, istemin sonuna; aynı alan için tek cümle, değiştirilir) |
|---|---|
| `fazla_kisi` | `CORRECTION: exactly {n} people in frame: {adlar}. No other people, faces or figures anywhere, including the background.` |
| `yanlis_kisi` | `CORRECTION: the person on the {ucte_bir} is {ad} — {kimlik_en}.` (+ o karakterin kart sayfası ilk referans) |
| `nesne_el` | `CORRECTION: the {nesne} is in {ad}'s {EL} hand; {iyelik} {OBUR_EL} hand is {el_sekli_en}.` |
| `bakis` | `CORRECTION: {ad} faces toward frame {yon}, eyes on the {hedef}.` |
| `isik` | `CORRECTION: the only light source is the {kaynak} on frame {yon}; no fire, no candles, no other glow.` |
| `yasak_oge` | `CORRECTION: remove {oge}; there is no {oge} in this scene.` |
| `kostum` | `CORRECTION: {ad} wears {kostum_tarif_en}.` |
| `olcek` | `CORRECTION: {yaratik} is the size of {benzetme}, reaching {ad}'s {vucut_noktasi}.` (+ ölçek kartı referansı) |
| `stil` | `CORRECTION: photorealistic film still, real photography, NOT illustration, NOT 3D render, NOT plush.` |
| `mekan` | `CORRECTION: the {oge} is on the {kadraj_yeri} of the frame, as in the location reference.` |
| `agiz` **(yeni)** | `CORRECTION: {ad}'s mouth is closed, lips together.` |
| ses şablonları | [SM2] §4.5.11'deki satırlar aynı dosyanın `ses` bölümünde |
Çıplak `left/right` yazılmaz; her zaman `{ad}'s RIGHT hand` ya da `frame left` biçimindedir ([YN2] Y47).

#### 4.5.9 `_RAPOR/G1_P<n>_B<k>.json` (aday başına)
```json
{"no": 71, "aday": "b", "sha1": "9c1e…", "karar": "GEC", "secildi": true,
 "yerel": {"yuz_sayisi": 1, "kimlik": {"mara": {"benzerlik": 0.58, "fark_payi": 0.21}},
           "kadraj_sirasi": ["mara"], "ucte_bir": {"mara": "orta"}, "yaw": {"mara": -34},
           "el_nesne": {"fener": "sag", "guven": 0.71}, "jaw_open": {"mara": 0.04},
           "mekan_dinov2": 0.66, "lab_dE_sahne": 4.2, "stil_clip_foto": 0.93, "keskinlik_oran": 1.08},
 "kor": {"is_id": "G1_P1_B3_07", "gorsel": "g02.jpg", "tutarli": true, "p_eslesme": {"p1": "mara"}},
 "alanlar": [{"alan": "nesne_el", "beklenen": "sag", "yerel": "sag", "kor": "sag", "sonuc": "uyum"}],
 "bayrak": [], "hata": [], "olculemedi": [],
 "esik_surum": "sureklilik@1.0+kalibrasyon@3"}
```

#### 4.5.10 `uretim.zincir` ve `_RAPOR/ZINCIR_PLANI.json`
```json
{"dalgalar": {"1": {"planlar": [40, 41, 42, 44, 46], "zincir_baslari_once": [41, 44]}, "2": [43, 45], "3": [47]},
 "plan": {"43": {"yontem": "Z1", "kaynak": 41, "derinlik": 1, "pencere": [5.4, 7.5], "kesim_sn": 5.6,
                 "yedek": "_ADAYLAR/043_plan.jpg"},
          "45": {"yontem": "Z1", "kaynak": 44, "derinlik": 1, "yedek": "_ADAYLAR/045_plan.jpg"},
          "47": {"yontem": "Z1", "kaynak": 43, "derinlik": 2},
          "44": {"yontem": "Z2", "bitis_gorseli": "045 planının G1'li planlanmış görseli (sha1 7a2c…; GS15'te _ADAYLAR/045_plan.jpg'e taşınır)",
                 "neden": "Y56: sol elde anahtar el değiştiriyor, sonraki plan devam"}}}
```

#### 4.5.11 Ders defteri kaydı ([UM] ham kayıt biçimi; bu alanın kategorileri)
```json
{"id": "D-20261030-221540-a1b2", "zaman": "2026-10-30T22:15:40+03:00", "film": "EMBERFALL_F2", "seri": "EMBERFALL", "alan": "goruntu",
 "olay": "kapi_hatasi", "asama": "GS14", "kapi": "V3", "madde": "V3.nesne_el", "plan": 41, "kategori": "ters_el",
 "belirti": "kesme anında fener sol elde; G1 sağ el GEÇ demişti",
 "olcum": {"g1_el_nesne_guven": 0.48, "kor_tutarli": true},
 "baglam": {"kadraj": "OG", "iki_el_ayni_yarida": true, "plan_ozellik": "…([YN2] plan_ozellik.py)"},
 "sinif": "kacirma", "kanit": ["_RAPOR/G1_P1_B2.json#041", "_RAPOR/V2V3_P1.json#041"],
 "eylem": "yeniden_cekim:z2_bitis", "sonuc": null}
```
Görüntü kategorileri: `yuz_kaymasi`, `yanlis_kisi`, `fazla_kisi`, `kaybolma`, `ters_el`, `nesne_ziplama`, `isik_ziplama`, `kostum_ziplama`, `olcek`, `yasak_oge`, `stil`, `morf`, `kesme_ici`, `zincir_dikis`, `plaka_oge`.

#### 4.5.12 `sureklilik_esikleri.json` (biçim)
```json
{"g1.kimlik_gec": {"deger": 0.45, "etiket": "tahmin", "kaynak": "02§6.2", "aciklama": "SFace üst bant; 0,363 resmî alt bant"},
 "g1.kimlik_hata": {"deger": 0.363, "etiket": "kaynakli", "kaynak": "02§1.1 OpenCV", "gevsetilemez": true},
 "kor.gorev_gorsel_max": {"deger": 12, "etiket": "tahmin", "kaynak": "GS0'da ölçülür"}}
```
`esikler.py` ([SN2]) bu dosyayı `ritim_esikleri.json`, `hat_esikleri.json`, `ses_esikleri.json` ile birleştirir; aynı anahtar iki dosyada geçerse HATA verir. Karakter başına ayarlanan değerler `EVREN/<SERI>/KALIBRASYON.json`'dadır.

---
### 4.6 Yazılması / değişmesi gereken kod (araç adı, ne yapar, girdi/çıktı, öncelik)

**Öncelik:** **P0** = bulutta, ağsız ve kredisiz test edilebilen karar mantığı (önce bu) · **P1** = kullanıcının Windows'unda yerel modellerle ölçüm, ilk gerçek filmden önce · **P2** = iyileştirme.
**Stil:** her araçta başta Türkçe kullanım belgesi; `python <araç>.py` tek başına yardımı basar; Python 3.10 (3.11+ özelliği yok, [UM] R8); her JSON atomik yazılır ([UM] `ortak.atomik_yaz`); çıktı zarfı ve girdi imzası ([UM] §5.3); çıkış kodları orkestratör tablosundan; eşikler koda gömülmez, `esikler.py` ile okunur. Ajan işi çıkış koduyla değil görev defteri kaydıyla devredilir.

#### 4.6.1 Yeni araçlar

| Araç | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|
| `dunya_defteri.py` | [YN2] §4.5.13 çözüm kuralları (miras, fark, etki katlama, araya kesme, geri dönüş zaman çizgisi, klip bölme, dondurma) + K0 kuralları (§4.7.1). `--derle`, `--denetle`, `--dondur <no>`, `--komsuluk <KURGU_PLANI>` (Y58), `--gozlenen <rapor>`. `kroki.py`'yi kütüphane olarak içe alır. Ses alanlarını açar | `SAHNELER.json`, sözleşmeler, `HIKAYE.json`, `EVREN_BAG.json`, kroki → `DUNYA_DEFTERI.json`, `_RAPOR/K0_SUREKLILIK.json`, `KUYRUK/YENIDEN_YAZ.json` | **P0** (saf Python) |
| `istem_derle.py --gorsel / --kart / --bitis` | Görsel istem (anlık görüntü), kart istemleri, Z2 bitiş görseli istemi; referans seçimi; istem özeti; girdi imzası kilitli kart sürümlerini içerir. `--hareket` modülü yönetmenin | `SAHNELER.json`, defter, evren → `SAHNELER.json` alanları, `_KARTLAR/KART_ISTEMLERI.json` | **P0** |
| `evren.py` | Seri kütüphanesinin tek yazarı: `--kur`, `--bagla`, `--spec-dogrula`, `--kilitle`, `--surum-ac`, `--film-sonu`, `--disa-aktar` (`01_KARAKTERLER/`), `--ice-al` (EMBERFALL ve B1–B3 kartları), `ne_yok_kelimeleri()`; hikâye, ses, kroki ve kurgu alt komutları (`kaydet --alan hikaye\|ses\|kroki\|sablon`) o uzmanların şemasıyla. Kilitli dosyalarda SHA1 denetimi | `KART_SPEC.json`, kartlar → `EVREN/<SERI>/…`, `EVREN_BAG.json` | **P0** |
| `kor.py` (modül + CLI) | Kör görev hazırlar: görselleri anonimleştirir ve karıştırır, iki aşamalı `SORULAR.json` üretir (`_derlenir.gorunmesi_gerekenler`, olgular, yasaklar), kritik soruları karışık sırayla ikiler, [CM] görev defterine `GOREV.json` + `GIRDI/` yazar. Cevapları okur; `p` ↔ karakter eşler; görüntü sol/sağ → anatomik sol/sağ çevirir; beklenenle alan alan karşılaştırır | adaylar, beklenen → `_GOREV/<id>/`, karşılaştırma sonucu | **P0** |
| `kare_denetim.py` | G1 ve G1Z: `--yerel`, `--kor-gorev`, `--karar` (kural tablosu, seçim sırası, iki kaynaklı HATA'yı hakeme göndermeme), `--hakem` (hakem kararlarını işler; iki kaynaklı alana GEÇ'i reddeder), `--serbest` (kapak). Seçileni `SIRALI_GORSEL/NNN.jpg`'e koyar, SHA1'i ve dondurmayı yazar | `_ADAYLAR/`, defter, evren → `_RAPOR/G1_*.json`, `KUYRUK/YENIDEN_URET.json` | **P0** karar (sahte ölçümle) / **P1** ölçüm |
| `kart_denetim.py` | Kart kapısı: yüz sayısı, öz tutarlılık, kadro ayrışması, stil, fon, plaka "görünmesi gerekenler"; kör görev; karar; `ayrisma_kilitli`; banka üretimi | kart adayları → `_RAPOR/KART_KAPISI.json`, `banka_vN.npz` | **P0** karar / **P1** ölçüm |
| `duzeltme.py` | CORRECTION şablonları (görüntü + ses bölümü), tek seferlik küçük düzeltmeler (ayna yalnız `ayna_yasak = false`, kenar kırpma, renk eşleme) ve işaret dosyası; tur sayacı; kaçış kaydı; `gorsel_duzeltme` zincirine iş verir | `KUYRUK/YENIDEN_URET.json` → istemler, `_RAPOR/ISARET/`, `DUZELTME_KAYDI.jsonl` | **P0** |
| `kare_zinciri.py` | `--plan`: Z0/Z1/Z2, akış içi dalgalar, derinlik, yeniden demirleme. `--cikar`: [KU2] penceresinden en iyi kareyi en-boy koruyarak çıkarır, G1Z kaydı yazar, `uretim.zincir`'i doldurur | `SAHNELER.json`, raporlar, klipler → `ZINCIR_PLANI.json`, `SIRALI_GORSEL/NNN.jpg` | **P0** plan / **P1** çıkarma |
| `kalite_denetim.py --klip` | V1: ffprobe, `blackdetect`, `freezedetect`, `blurdetect`, PySceneDetect, titreme; kusur zaman damgaları; pencere dışı kusurda `cozum: kirp`. Final bölümü (LUFS, son kalite) ses ve kurgu uzmanlarıyla ortak dosyada | klip → `_RAPOR/V1_P<n>.json` | **P0** (ffmpeg bulutta da var) |
| `video_denetim.py` | `--onceden` (K1Ö), `--klip` (V2 + yüz izi + V3 kör görev), `--dudak` (`tts_dudak` sonrası), `--islem <ayna\|kadraj>` (0 kredi işlemleri sonrası), `--gecis` (K1). Hakem için kare şeritleri ve çiftleri | klipler, kareler, defter → `_RAPOR/K1ON_*`, `V2V3_*`, `V2_P<n>/NNN_yuz.jsonl`, `K1_*` | **P1** (karar mantığı **P0**) |
| `olcum/` paketi | Tek arayüz `olc(gorsel, beklenen) → dict`, her arka ucun `sahte` hâli: `kimlik.py` (YuNet + SFace, kadro bankası, Macar eşlemesi, yüz izi), `gorunum.py` (DINOv2-small, CLIP (`kontrol.py` ile aynı model), OWLv2 nesne bulucu, maskeli benzerlik), `poz.py` (MediaPipe Pose/Hand/Face: bilek–nesne, parmak açıklığı, yaw, `jawOpen`), `isik.py` (Lab, parlaklık, yanak oranı), `teknik.py` (keskinlik, en-boy). Ses uzmanının `ses.py` ve `dudak.py`'si aynı pakete girer | — | **P1** (`sahte` arka uç **P0**) |
| `saglayicilar/vlm_*.py` | `vlm` türü: `claude_code` (görev defteri), `claude_api` (başsız; anahtar `AYARLAR/` ya da ortam değişkeni, asla yazdırılmaz), `sahte` (yan dosyadaki gerçeği döndürür; hata enjeksiyonu) | — | **P0** (`sahte`, `claude_code`) / **P1** (`claude_api`) |
| `saglayicilar/` `gorsel_duzeltme` zinciri | `flow_gorsel` (Memmet ile Flow görseli; x2 çıktı; günlük tavan; video günü kilidi), `vertex_gorsel` (ücretli API, onaylı kurulum ayarı) | — | **P1** (`flow_gorsel`) / **P2** (`vertex_gorsel`) |
| `gemini_paket.py` / `gemini_al.py` (araç [UM]'nin) | Benim içerik payım: `--aday 2`, `--basamak k`, `--kartlar`, `--ikinci-goz`; 10'dan fazla ek dosyada `REFERANSLAR.zip`; içe alırken `_ADAYLAR/`'a koyar, **`SIRALI_GORSEL/`'e doğrudan koymaz** | `SAHNELER.json` → paket; ZIP → `_ADAYLAR/` | **P1** |

#### 4.6.2 Değişecek mevcut dosyalar

| Dosya | Değişiklik | Öncelik |
|---|---|---|
| `film.py` | [UM] `ASAMALAR` kaydına GS0–GS17 satırları (girdi ve çıktı imzaları; kredili aşamanın imzası G1/G1Z kayıtlarını içerir). Video gönderiminde G1 GEÇ + SHA1; Z1 planında kaynak V1/V2/V3 + G1Z şartı | **P0** |
| `istem_denetim.py` | Ek kurallar: kimlik dizesi birebir geçiyor mu; `gorsel_istem`'de süren eylem fiili; görünen her karakterin iki eli tarifli mi; aynı alan için birden çok CORRECTION; karakter referansı ≤ 2 (ebeveyn ve plaka ayrı sayılır); çıplak `left/right` ([YN2] ile ortak) | **P0** |
| `saglayicilar/sahte.py` | `gorsel` iki aday üretir ve yan dosyaya "gerçeği" yazar (kim nerede, hangi el); hata enjeksiyonu (`SAHTE_HATA=ayna,fazla_kisi,ters_el`); sahte video ([KU2] hareket eden kutu) ve sahte yüz izi | **P0** |
| `saglayicilar/__init__.py` | `TURLER`'e `vlm`, `gorsel_duzeltme` ([UM] listesiyle birlikte) | **P0** |
| `kontrol.py` | Gelen görselleri `_ADAYLAR/`'a koyar (G1 seçsin); CLIP yükleyicisi `olcum/gorunum.py` ile ortak | **P1** |
| `memmet.py` | Video gönderiminde başlangıç karesini G1 ya da G1Z kaydından okur ve SHA1'i doğrular; Z2 için `bitis_karesi` alanı (sonraki planın no'su ya da `NNN_son`); Z1 planını kaynak hazır olmadan kuyruğa almaz; görsel düzeltmede x2 çıktı. **Tempo, uyarıda durma ve reCAPTCHA davranışına dokunulmaz** ([UM] S1–S6 düzeltmeleri ayrıca) | **P1** |
| `kurulum.py` + `requirements.txt` | `opencv-python` (YuNet ve SFace `FaceDetectorYN` / `FaceRecognizerSF`), `mediapipe` (ana ortamda tek sürüm; cp310 Windows tekerleği GS0'da doğrulanır; OpenMontage kendi ortamında 0.10.14), `scenedetect==0.7.2`, torch CPU + `transformers` (DINOv2-small, OWLv2-base, CLIP). Model dosyaları bir kez indirilir (YuNet/SFace ONNX opencv_zoo'dan, MediaPipe `.task`), sonra `HF_HUB_OFFLINE=1`. Yalnız izinli lisanslar (R13) | **P1** |
| `.claude/agents/sureklilik-denetcisi.md` | Baştan yazılır: kipler (kagit / hakem / kacis / ders), `model: opus`, `effort: high`, `tools: Read, Write`, çıktı biçimleri (§4.3.2) | **P0** |
| `.claude/agents/kare-tarifcisi.md`, `kart-tasarimcisi.md` | Yeni (§4.3.1, §4.3.3) | **P0** |
| `.claude/agents/istem-muhendisi.md` | Kaldırılır: görsel CORRECTION `duzeltme.py`'ye, plan onarımı `yonetmen onarim` kipine ([YN2], [CM] ile aynı karar) | P1 |
| `.claude/kurallar/erisim.json` ([CM]) | `kare-tarifcisi` → `kor` rolü; `kart-tasarimcisi` → `yazar`; `sureklilik-denetcisi` → `denetci` | **P0** |

#### 4.6.3 Testler (`sahte` ve `kaset` sağlayıcılarla; ağ ve kredi yok)

| Test | Ne kanıtlar | Öncelik |
|---|---|---|
| `test_sureklilik.py` | K0: el değiştirme etkisiz → HATA; kaybolma → HATA; 180° → HATA; kalıcı yara sahne sınırında kayboldu → HATA; gün saati geri gitti → HATA; kart kapsamı eksik → HATA; dondurulmuş durumla sıra değişimi → HATA (Y58); açı değişiminde kadraj konumu değişti → HATA **yok** ([YN2] İ-1) | **P0** |
| `test_g1_karar.py` | Aynalanmış kare → kadraj sırası HATA (02§7); fazla yüz → HATA; tek kaynaklı ters el → BAYRAK → hakem; iki aday da HATA → CORRECTION; ölçüm modeli yok → ÖLÇÜLEMEDİ (asla GEÇ); hakem iki kaynaklı HATA'ya GEÇ yazdı → reddedilir; G1'siz kare video aşamasına gönderilmez; SHA1 uyuşmazlığı → gönderilmez | **P0** |
| `test_kor_paket.py` | `GIRDI/`'de plan numarası, karakter adı, istem, kostüm tarifi yok; görsel adları anonim; kritik soru ikilenmiş ve seçenekleri karışık; sol/sağ çevirisi (`on`, `3/4`, `sirt`, `profil`) doğru | **P0** |
| `test_v1.py` | ffmpeg ile sentetik klip: 1 sn siyah → HATA; 1,5 sn donma → HATA; ortada sert kesme → HATA (PySceneDetect kuruluysa; yoksa atlanır); kusur pencere dışında → `cozum: kirp`, kuyruk maddesi yok | **P0** |
| `test_zincir.py` | Akış içi dalgalar; derinlik 3 → yeniden demirleme; kaynak V3 HATA → ardıl Z0'a düşer; teknik son kare hiçbir yolda seçilmez; zincir karesinin en-boyu korunur | **P0** |
| `test_kart.py` | Kadro çifti ≥ 0,363 → HATA; yalnız hikâyeye bağlı öğe farkı → `ayrisma_kilitli`; plaka görünen öğe eksik → HATA; [UM] T18 (`mara.jpg` ↔ `mara` ≥ eşik, `voss.jpg` ↔ `mara` < 0,363; model dosyası yoksa atlanır) | **P0** |
| `test_evren.py` | Kilitli dosyanın SHA1'i değişti → durdu; sürüm açma; `kimlik_en`'de ad yok; sahip dışı alana yazma reddi | **P0** |

---

### 4.7 Makinenin denetleyeceği eşikler (kaynağıyla)

**Kodlar:** **H** = HATA (aday elenir ya da plan geçmez), **B** = BAYRAK (ikinci kaynak ya da hakem bakar).
**Ölçülemedi kuralı (kesin karar 6):** bir ölçüm yapılamazsa (model kurulu değil, yüz çok küçük, sırt dönük, kroki eksik) sonuç `ÖLÇÜLEMEDİ` ya da `HESAPLANAMADI` olur ve en az **B** sayılır; kâğıtta kroki eksikse **H** ([YN2]). Hiçbir zaman sessizce GEÇ sayılmaz.
"(tahmin)" yazan değerler başlangıç değeridir; GS0 kalibrasyonu ve §4.7.10 korkuluklarıyla ayarlanır.

#### 4.7.1 K0 — kâğıt üstü süreklilik (`dunya_defteri.py`; kredi yok, ağ yok) **(değişti)**

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| K0.1 | `bitis[N]` ≡ `baslangic[N+1]` (yalnız olgular; `yeni_sahne` ve `zaman_atlama` hariç) | eşit | H | ZAN Z0 #16; [YN2] Y11 |
| K0.2 | Gerekçesiz `fark` | 0 | H | [YN2] Y12 |
| K0.3 | Sahnenin son planı ≠ sözleşme çıkışı; hikâye uçları ⊄ sözleşme | 0 | H | [YN2] Y13, Y57 |
| K0.4 | Her olgu değişiminin `etki`li bir adımı ya da `zaman_atla` kartı var | var | H | Kesin karar 2 |
| K0.5 | Durumu değiştirmeyen fiziksel adım (mikro adımlar hariç) | — | B | [GS1] |
| K0.6 | Nesnenin `kimde` ya da `el` alanının etkisiz değişmesi | 0 | H | [YN2] Y15–Y16; 02§6.2'de el B idi, kesin karar 2 gereği H |
| K0.7 | Kaybolma: görüş konisinde, görüş hattı açık ve `gizli_arkasinda` olmayan kişi `kadrajdakiler`'de yok; ya da listede olup geometriye göre kadraj dışı | 0 | H (hesap) | [YN2] Y14; 02§6.2 |
| K0.8 | Kalıcı özelliğin (yara, kir, ıslaklık, kostüm hasarı, saç durumu, taşınan nesne) olaysız kaybolması, sahne sınırları dahil | 0 | H | DERS ("kim nerede / nesnenin yolu"); [GS1] |
| K0.9 | Gün saatinin geri gitmesi (geri dönüş ayrı zaman çizgisinde, ≤ 20 sn) | 0 | H | [GS1]; RE:geri_donus_max_sn = 20 |
| K0.10 | Işığın kadrajdaki yönü sahnenin ana kaynağından hesaplanana uymuyor ve `isik_degisimi` yok | 0 | H (hesap) | [YN2] Y23; 02§6.2 |
| K0.11 | 180° (kurulum sahnenin `kamera_tarafi`'nda değil, `eksen_gecis` yok); karşılıklı tekli planlarda bakışlar zıt değil | 0 | H (hesap) | [YN2] Y17–Y18; ZAN Z0 #17–18 |
| K0.12 | Karakter referansı | ≤ 2 | H | RE:referans_max = 2; [YN2] Y45 |
| K0.13 | Z1 zincir derinliği | ≤ 2 | H | 02§2.3; [YN2] Y40 |
| K0.14 | Kurulum kullanımdan önce | evet | H | 02§6.2, ZAN§4.2 |
| K0.15 | **(yeni)** Kart kapsamı: plandaki her karakter, kostüm varyantı, nesne ve plaka için kilitli kart ya da açık kart isteği | var | H | GS2 |
| K0.16 | Görünen ya da görünmeyen her karakterin iki elinin olgusu (`tutar`, `yer`, `sekil`) yazılı | evet | H | Kesin karar 2 |
| K0.17 | **(yeni)** Kurgu sonrası yeni komşu çiftlerde dondurulmuş olgu eşitliği | eşit | H (kullanıcının CapCut kararında B) | [YN2] Y58, İ-11 |
| K0.18 | Kimlik demiri: her karakterin sahnedeki ilk görünüşü ≥ OY ve yüz `on` ya da `3/4` | evet | B | [YN2] Y44 |
| K0.19 | **(yeni)** Kimliği yalnız sırttan ya da profilden taşıyan plan oranı (sahne grubu başına) | ≤ %30 | B | (tahmin); [GS1] §8.5 |

#### 4.7.2 Kart kapısı **(değişti)**

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Birleşik sayfada bulunan yüz sayısı | = beklenen görünüm sayısı | H | [GS1] |
| Aynı karakterin görünümleri arası SFace kosinüsü | < 0,363 H · 0,363–0,45 B · ≥ 0,45 geç | H/B | 0,363 OpenCV resmî (02§1.1); 0,45 (tahmin) |
| İki farklı karakter arası SFace kosinüsü (`bilincli_benzerlik` hariç) | ≥ 0,363 H · 0,25–0,363 B | H/B | 0,363 resmî; 0,25 (tahmin) |
| Ayrışma yalnız hikâyeye bağlı öğeler yüzünden sağlanamıyor | — | H (`ayrisma_kilitli` → senarist) | İ-12 |
| CLIP "photograph" olasılığı (karşı sınıflar: illustration, 3D render, plush toy, cartoon) | < 0,5 → kör gözleme; kör de "çizim" derse H | B/H | YR A6 dersi; 0,5 (tahmin) |
| Kör gözlemde NE YOK listesindeki öğe (fermuar, modern mont …) | 0 | H | YR §5, BK§2.9 |
| Kör gözlem ↔ tarifteki zorunlu öğeler (saç rengi ve biçimi, kostüm parçaları, asimetrik iz tarafı) | hepsi uyumlu | H | [GS1] |
| Hikâyeye bağlı öğe ↔ kör gözlem | uyumlu | H | [SN2] İ9 |
| **(yeni)** Plakada kişi ya da yüz | 0 | H | DERS (referanstaki nesne ve kişi kopyalanıyor) |
| **(yeni)** Plakada `kroki.py`'nin hesapladığı görünmesi gereken öğeler, beklenen üçte birde | hepsi | H (yerel + kör) / B (tek kaynak) | [YN2] Y60, R5 |
| **(yeni)** Plaka nötr durumda (ateş sönük, kapı kapalı) | evet | H | DERS |
| Aday sayısı / tur | 3 aday / ≤ 2 tur | — | YR A6; HAT §5 |

#### 4.7.3 G1 — başlangıç karesi **(değişti)**

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| En-boy ve çözünürlük | 16:9 ±%1, kısa kenar ≥ 720 px | H | İ-7 (hesap) |
| Yüz ölçülebilirliği | YuNet skoru ≥ 0,9 ve yüz kutusu ≥ 48 px yükseklik; değilse ÖLÇÜLEMEDİ | B | 0,9 OpenCV örnek betiği varsayılanı (**GS0'da doğrulanır**); 48 px (tahmin) |
| Kimlik (insan) | ≥ 0,45 geç · 0,363–0,45 B · < 0,363 H (karakter başına `KALIBRASYON.json` bandı varsa o) | H/B | 02§6.2 (0,363 resmî, 0,45 tahmin) |
| Kimlik fark payı (beklenen − kadrodaki en yakın öteki) | ≥ 0,05 | B | (tahmin); "B22K'de Bram'a benzemeyen adam" (H/proje-b2) |
| Bulunan yüz sayısı > kadrajdaki görünür yüzlü insan sayısı | 0 fazla | H | 02§6.2 |
| Eksik yüz | — | B (sırt dönük olabilir) | 02§6.2 |
| Arka plandaki küçük yüz (kutu < kare yüksekliğinin %4'ü) | sayılmaz; kör gözlem "kişi" derse B | B | (tahmin) |
| Kadraj sırası (yüz ve kişi kutularının x sırası) | = `_derlenir.kadraj_sirasi` | H | 02§6.2; [YN2] §4.7.8 |
| Kadraj üçte biri | = `_derlenir.kadraj_konumu` | karşılıklı çekimde H, diğerlerinde B | ZAN§3.3 |
| Bakış (MediaPipe yaw) | \|yaw\| > 15° ve işaret `_derlenir.bakis_kadrajda` ile ters | H | 02§6.2; 15° (tahmin); işaret kuralı GS0'da doğrulanır (02§4) |
| Nesne hangi elde | yerel (Pose bileği + OWLv2) ve kör ikisi de ters → H; biri ters → B | H/B | 02§6.2 (tek başına H verilmez) |
| **(yeni)** Ağız (konuşan planın başlangıcı; `_derlenir.dinleyen_agiz = kapali` kişiler) | `jawOpen` ≤ 0,15 | B | (tahmin); [SM1] S0.2, [YN2] Y35 |
| **(yeni)** Konuşan yüz | yüz yüksekliği ≥ kare yüksekliğinin %12'si; \|yaw\| ≤ 45° | B | (tahmin); [YN2] Y32 |
| **(yeni)** Açık parmak (yalnız D/Y kadraj ve el ≥ kare yüksekliğinin %15'i) | kör ↔ `_derlenir.acik_parmak` | B (asla tek başına H) | Kesin karar 2; parmak sayımı zayıf (İ-4) |
| İnsan olmayan karakter ya da nesne: DINOv2 kırpıntı kosinüsü | < 0,5 | B | 02§6.2 (tahmin) |
| Yaratık ölçeği (kutu yüksekliği / yakındaki insan yüz kutusu, karttaki orana göre) | ± %35 | B | (tahmin); "minik çizme" dersi (DERS) |
| Mekân benzerliği (kişiler maskeli DINOv2 ↔ kamera ağacı ebeveyni) | < 0,60 | B | (tahmin) |
| Işık yönü (yanak parlaklık oranı > 1,25 olan taraf ≠ `_derlenir.isik_kadrajda`) | — | B | 02§6.2 (tahmin) |
| Sahne içi renk (Lab ΔE, sahne grubunun ilk onaylı karesine) | > 10 | B | 02§6.2 K1 değeri (tahmin) |
| Stil (CLIP "photograph") | < 0,5 ve kör "çizim" | H | YR A6 (tahmin) |
| Yazı, logo, filigran (kör gözlem, iki soru) | 0 | H | 02§5 `yasaklar` |
| Anatomi bozukluğu (fazla uzuv, kaynaşık parmak, bozuk yüz) | iki tekrarda da var → H; birinde → B | H/B | 02§5 |
| Plan ve sahne yasakları (`ucuncu_kisi`, `ikinci_isik_kaynagi` …) | 0 | H | 02§6.1 |
| Keskinlik (Laplacian varyansı / parti medyanı) | < 0,5 | B | (tahmin) |
| Kritik alanlarda kör gözlemin iki cevabı uyuşmuyor | — | B (alan "belirsiz") | [GS1] |
| Aday sayısı / CORRECTION turu | 2 aday / ≤ 2 tur, sonra kaçış | — | 01§A3 (ViMax); HAT §5; İ-3 |

#### 4.7.4 G1Z — zincir karesi **(yeni)**

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Arama penceresi | [YN2] Y55: son adımın ölçülen bitişi + ≥ 0,2 sn ile `klip_sn − 0,5` arası | — | RE:kullanim_son_pay_sn = 0,5; 0,2 (tahmin) |
| En-boy | korunur (1280×720 doğal; GS0 seçeneği 1376×768 yalnız oran korunarak) | H (bozulmuşsa) | İ-7 |
| Kimlik | §4.7.3 bantları | H/B | 02§6.2 |
| Keskinlik | ≥ 0,6 × A'nın ilk kullanılan karesinin keskinliği | B | (tahmin) |
| V3 gözlemi aynı kare ya da ±0,2 sn içinde | var ve uyumlu | H | Kesin karar 2 ve 3d |
| Kişi sayısı | = A'nın bitişindeki görünür kişi sayısı | H | 02§6.2 |
| B'nin G1'li planlanmış görseline DINOv2 | < 0,70 | B (fark ders defterine) | (tahmin) |

#### 4.7.5 K1Ö (başlangıç kareleri dizisi) ve K1 (kurgu sırası)

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| `devam` dikişi (Z1): DINOv2 kosinüsü | < 0,80 | H | 02§6.2 (tahmin); B19 |
| `devam` dikişi: ortalama parlaklık farkı | > 12/255 | B | 02§6.2 (tahmin) |
| `eylem_kesme`, `araya_kesme`, `zaman_atlama` (aynı mekân): Lab ΔE / parlaklık farkı | > 10 / > 20/255 (`isik_degisimi` yoksa) | B | 02§6.2 (tahmin) |
| `kurulum_donusu`: o kurulumun ana karesine DINOv2 | < 0,70 | B → kör soru ("kapı hâlâ görüntünün solunda mı") | 02§6.2 (tahmin) |
| Kostüm (gövde kırpıntısı DINOv2) sahne içinde | önceki plana < 0,6 | B | (tahmin) |
| Geçişin iki yanında kimlik | §4.7.3 bantları | H/B | 02§6.2 |
| Dondurulmuş olgu eşitliği (K1) | eşit | H (kullanıcı kararında B) | [YN2] Y58 |
| Bulguların yönü | kurgucu + hakem; seyirciye **verilmez** | — | [KU2] İ-1 |

#### 4.7.6 V1 — teknik video **(değişti)**

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| `ffprobe` süre (8 sn klip) | ≥ 7,5 sn, video akışı var | H | 02§6.2 (kesik indirme dersi, DERS) |
| Çözünürlük | 1280×720 | H | 720p kararı (BK§8 #1) |
| `blackdetect=d=0.1:pic_th=0.98:pix_th=0.10` | kullanılan pencerede 0 aralık (planlı karartma hariç) | H | 02§6.2; `pic_th` 0,98 ffmpeg varsayılanı, `d` 2,0'dan kısaltıldı |
| `freezedetect=n=-60dB:d=1.0` | kamera sabit değilse ya da özne hareketi bekleniyorsa 0 | H | 02§6.2; `n` varsayılan, `d` kısaltıldı |
| PySceneDetect `ContentDetector(threshold=27)` klip içi kesme | 0 | H (kesme pencere dışındaysa `cozum: kirp`) | 02§3 (27 = varsayılan) |
| Titreme (ardışık kare MAE) | > 3 × klip medyanı ve > 8 (0–255) | B | 02§6.2, VBench yöntemi (tahmin) |
| `blurdetect` ortalaması | > 1,5 × klip medyanı | B | 02§6.2 (tahmin) |
| Kusur zaman damgası | her kusur `{bas, bit, tur}` ile | — | [KU2] |
| ~~Replik penceresinde `silencedetect`~~ | **kaldırıldı**; tek yeri [SM2] S2.1 | — | [SM2] İ-7, [KU2] İ-9 |

#### 4.7.7 V2 — klip içi süreklilik ve dudak sonrası **(değişti)**

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Örnekleme | 0,5 sn arayla 17 kare; replik ve ekran dışı ses pencerelerinde ayrıca 24 fps yüz izi | — | 02§6.2; İ-10 |
| Kimlik kayması | ilk kareye göre > 0,15 düşüş **ve** < 0,363 | H | 02§6.2 (0,363 resmî, 0,15 tahmin) |
| Yüz ya da kişi sayısının `kadraja_girer` / `kadrajdan_cikar` adımları dışında değişmesi | 0 | H | 02§6.2 |
| Ardışık kare DINOv2 sıçraması | klip medyanından > 0,15 düşük | B → kör gözlem | 02§6.2 (tahmin) |
| Ekran yönü (kişi kutusu x merkezi ilk → son) | işaret = `_derlenir.ekran_yonu` | H | 02§6.2, ZAN§3.3 |
| İlk kare sadakati (video ilk karesi ↔ onaylı başlangıç ya da zincir karesi, DINOv2) | < 0,85 | B | 02§6.2 (tahmin) |
| **(yeni)** `tts_dudak` sonrası: aynı karede SFace (özgün ↔ yeni) | §4.7.3 bantları | H/B | [SM2] S2.15 |
| **(yeni)** `tts_dudak` sonrası: alt yüz kırpıntısı DINOv2 (özgün ↔ yeni) | < 0,80 | B | (tahmin) |
| **(yeni)** `tts_dudak` sonrası: yüz ya da kişi sayısı değişimi | 0 | H | 02§6.2 |
| **(yeni)** Ayna ya da yeniden kadraj sonrası (0 kredi merdiveni) | kimlik bantları + ekran yönü + K1 yeniden | H/B | İ-9 |

#### 4.7.8 V3 — bitiş durumu (atomik zincirin videoda denetimi)

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Kesme anındaki karenin kör gözlemi ↔ `_derlenir.bitis_durumu` kritik olguları (nesne kimde ve hangi elde, kişi var mı, kapı ve ateş durumu) | hepsi uyumlu | H | Kesin karar 2 |
| Adım penceresinde kare farkı enerjisinin tepesi | sapma ≤ 1,0 sn | B | [YN2] §4.7.8 (tahmin) |
| Adımın bitişinde Pose ölçümü (ör. `uzanir` → dirsek açısı) | > 140° | B | (tahmin) |
| Bitişte durma: son 0,5 sn'de ardışık kare MAE ortalaması | ≤ klip medyanının %50'si | B | [YN2]; yöntem 02§1.2 (tahmin) |
| Z1 kaynağı olacak klipte V3 | GEÇ şart | H (zincir kurulmaz, ardıl Z0'a düşer) | Kesin karar 3d |
| Plan başına yeniden çekim | ≤ 2 (teknik ve kurgu ortak sayaç), sonra yönetmen böler | — | [UM], [KU2] |

#### 4.7.9 Zincir, düzeltme ve sağlayıcı kuralları

| Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Bitiş tutma süresi | 0,5 sn | — | RE:bitis_tutma_sn |
| Z1 derinliği | ≤ 2, 3. halkada yeniden demirleme | H | 02§2.3 |
| Yeniden demirlenen kare ↔ zincir karesi DINOv2 | ≥ 0,90 | H | (tahmin) |
| Z1 + Z2 aynı klipte | GS0 ölçümüne kadar | B | [YN2] açık soru 4 |
| Küçük düzeltme: kenar kırpma | her kenarda ≤ %10, bir kez | — | (tahmin); DERS ("bir kez") |
| Ayna | yalnız `_derlenir.ayna_yasak = false`, bir kez | — | ZAN§3.3; [YN2] İ-10; DERS |
| Düzeltme görseli kullanıcı paketi | 0 | H (yasak) | H/gemini-ajan-gorsel |
| Flow görsel düzeltmesi yapılan günde video | yok | — | [UM] §7.2 `flow.gorsel_sonrasi_video`; DERS |
| Kör görev boyu | ≤ 12 görsel | — | (tahmin; GS0'da ölçülür) |

#### 4.7.10 Kalibrasyon korkulukları (ders defteri eşikleri böyle değiştirir)

| Kural | Değer | Kaynak |
|---|---|---|
| Hedef kaçırma oranı (kapı/alan başına) | ≤ %10 | 02§7 |
| Bir kalibrasyonda eşik adımı | ≤ 0,03 (kosinüs), ≤ %10 (oran eşikleri) | (tahmin) |
| SFace HATA eşiği | **0,363'ün altına inemez** (yalnız yükselebilir) | 02§1.1 resmî değer |
| Kalibrasyon için en az etiketli örnek | ≥ 30 / kapı-alan | (tahmin) |
| Etiket kaynağı | hakem kararı, sonradan V2/V3/K1/kurgu seyircisi bulgusu (`kacirma` eşlemesi), kullanıcı notu; B3'ün etiketli 44 karesi (21 bozuk) başlangıç seti | DERS, 02§7, [KU2] İ-1 |
| Kör soru daraltma | yalnız yerel ölçümün kaçırması ≥ 30 örnekte ≤ %10 kanıtlanan alanda; kimlik, el–nesne, kişi sayısı ve yasak öğe soruları hiçbir zaman kaldırılmaz; aday hiçbir zaman atlanmaz | İ-2 |
| Hakemin yetkisi | yalnız tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ; iki kaynaklı HATA'ya GEÇ yazamaz (kod zorlar) | İ-3 |
| Güvenlik kuralları (Flow'da dur, filtre kelimeleri, referans ≤ 2, kullanıcı paketi yasağı) | öğrenmeyle **gevşetilemez** | BK§6.2, DERS; [UM] §5.8 korkulukları |

---

### 4.8 Kesin kararların kendi alanımda uygulanışı

#### 4.8.1 Karar 1 — Kullanıcıya yalnız konu sorulur
- Bu alandaki bütün kararları ekip verir: karakterin görünüşü (`kart-tasarimcisi` tarif eder, kart kapısı teknik eler, `yonetmen kart_secimi` sanat seçimi yapar), varyantlar, hangi adayın seçileceği (kod), CORRECTION (kod + hakem), plan değişikliği (yönetmen), eşik kalibrasyonu (ders defteri). Kararlar `KARAR_DEFTERI.md`'ye "karar — neden — yanlışsa maliyeti" biçiminde yazılır.
- Eskiden kullanıcı onayı olan "karakter görünüşü" ve "mekân kartları" (BK§7.3) varsayılan akıştan çıkar; yalnız `--onayli` modda **bilgi** olarak gösterilir.
- Kullanıcıya kalan **işletme** dokunuşları (karar değil) dürüstçe söylenir: (a) büyük toplu Gemini paketlerini taşımak (kart, basamaklar, ikinci göz; ≈ 10–13 tur/film, tahmin); (b) Flow için Memmet'in yarı otomatik modunda GÖNDER'e basmak ya da reCAPTCHA çözmek; (c) durma bildirimleri. **Düzeltme görselleri için paket istenmez.** (a)'yı sıfırlamak isteyen için `vertex_gorsel` kurulum ayarıdır, film başına soru değildir.

#### 4.8.2 Karar 2 — Atomik eylem zinciri

| Kuralın parçası | Bu alanda nasıl uygulanır | Denetleyen |
|---|---|---|
| Başlangıç durumu = başlangıç karesi | `gorsel_istem` yalnız çözülmüş `baslangic_durumu` ve `_derlenir`'den derlenir. Kare durumun **her olgusuna** karşı ölçülür: kim, hangi işarette, yüz yönü ve bakış, poz, iki elin tutar/yer/şekil hâli, nesneler, mekân öğesi durumları, ışık | G1 (yerel + kör + kod) |
| Görsel istemde sonuç ya da süren eylem yok | Anlık görüntü kuralı; poz durağan anlatılır ("left arm extended toward the key, fingers 10 cm above it") | `istem_denetim.py` |
| Hangi el, hangi yön, kaç parmak açık | `eller.{sag,sol}.{tutar, yer, sekil}` → sözlükten sabit İngilizce ifade. Görselde Pose bileği + OWLv2 + Hand Landmarker + kör gözlem (görüntü koordinatında; anatomik çeviri kodda). Açık parmak yalnız büyük elde ve en çok BAYRAK | G1, V3 |
| Bitiş durumu = sonraki klibin başlangıcı | Kâğıtta defter zorunlu kılar (K0.1). Videoda V3 kesme anındaki kareyi `bitis_durumu`na karşı ölçer. `devam`'da Z1 bunu **piksel düzeyinde** sağlar; dondurma kurgu sonrası komşulukta korur (K0.17) | K0, V3, G1Z, K1 |
| Klip başına 2–3 adım | Adım sayısı yönetmenin kapısında ([YN2] Y01). Bu alan her adımın penceresinde enerji tepesine ve bitişinde Pose'a bakar | V3 (B) |
| Eylem tamamlanmazsa | Önce daha erken bir kare durumu karşılıyorsa kırpma; sonra yeniden üretimde Z2 (bitiş durumu görseli derlenir, G1'den geçer, Bitir yuvasına konur; Veo'da bitiş karesi referans görsellerle birlikte verilemediği için kimlik yine bu iki karede pişmiş olur, 02§2.1); iki denemeden sonra yönetmen böler | `duzeltme.py`, `kuyruk.py` |

#### 4.8.3 Karar 3a — Videodan önce animatik + habersiz seyirci
- Animatik yalnız **G1'den geçmiş** karelerle kurulur; Z1 planları için G1'li planlanmış görsel, Z2 planları için başlangıç ve bitiş görselleri arasında çapraz geçiş. Seyirci bozuk kareye değil hikâyeye puan verir; eylemin sonucunu görür.
- K1Ö bulguları **seyirciye verilmez** (habersizliği bozar, iki bağımsız kanıtı teke indirir; [KU2] İ-1). Kurgucuya ve hakeme gider; seyircinin görsel bulgularıyla **sonradan** eşlenir. Seyircinin görsel bulguları `bulgu_yonlendir` üzerinden GS9 kuyruğuna gelir.
- Animatik geçmeden video kodla başlamaz ([UM] U01 girdi imzası).

#### 4.8.4 Karar 3b — Dünya durumu defteri + otomatik zıplama denetimi
- Defteri **makine tutar** (`dunya_defteri.py`; sahibi bu alan). Yönetmen yalnız sözleşme, `miras` / `fark` ve `etki` yazar; hikâye uçları ve `bilgi` katmanı senaristtendir.
- **Durum yalnız olgudur;** kadraj bilgisi `_derlenir`'dedir. Açı değişimi yanlış zıplama üretmez ([YN2] İ-1).
- Zıplama beş yerde aranır: kâğıtta (K0), başlangıç karelerinde (G1 + K1Ö), zincir karesinde (G1Z), klip içinde (V2), kurgu geçişinde (K1, dondurulmuş olgularla).
- "Planlanan / gözlenen" iki sütun ([UM]): G1 ve V3'ün kör gözlem sonuçları plan durumunun yanına yazılır; fark kuyruğa ve ders defterine gider.
- Defter filmden filme taşınır: film sonu olguları `EVREN/<SERI>/DURUM_SON.json` olur ve sonraki filmin başlangıcıdır (B3 sonunda "Bram sürgün kostüm 2" gibi, H/proje-b3).

#### 4.8.5 Karar 3c — Referansla otomatik yüz kontrolü
- **İnsan:** OpenCV YuNet + SFace (Apache-2.0, ticari kanal için uygun; InsightFace modelleri ticari olmayan lisanslı olduğu için ana hatta yok, 02§0). Karakter başına **çok görünümlü banka** (yüz panelinin 4 görünümü + tam boy kartın 2 yüzü). Karar: görünümlere en yüksek benzerlik + kadrodaki ötekilere fark payı + çok yüzlü karede Macar eşlemesi. Karakter başına bant `KALIBRASYON.json`'da (sakal, koyu ışık gibi sistematik düşük benzerlik).
- **İnsan olmayan:** OWLv2 ile bul, DINOv2 ile karttaki kırpıntılara karşılaştır, ölçeği insan yüzüne oranla ölç; renk ve iz gibi öznitelikleri kör gözlem yazar.
- **Yüz görünmüyorsa** (sırt, kask, uzak plan): gövde ve saç kırpıntısı DINOv2 ↔ **arka görünüm kartı** + kör gözlem; sonuç en iyi ihtimalle BAYRAK. Bu yüzden kimlik demiri ([YN2] Y44) ve K0.19 uyarısı var.
- **Uygulandığı noktalar:** kart kapısı (ayrışma), G1, G1Z, V2 (0,5 sn + replik penceresinde kare kare), K1, `tts_dudak` sonrası, kapak adayları.
- **Yüz–ses bağı:** V2 yüz izi ses uzmanının "ağzı oynayan yüzün kimliği = replik karakteri" ölçüsünün ([SM1] S3.4) girdisidir.

#### 4.8.6 Karar 3d — Kare zinciri
- **Z1 (son kare → sonraki klibin başlangıcı)** `devam` geçişinin varsayılan ve zorunlu yöntemidir. "Son kare" teknik son kare değil, **kurguda kullanılan son kare**dir (kesme penceresi, Y55). Pencereden en keskin, en durgun, kimliği en yüksek kare seçilir; en-boy korunur; üretken modelle "temizlenmez" (kimliği değiştirebilir).
- Zincir karesi G1Z'den geçer; tutmazsa plan sessizce bozulmaz: G1'li planlanmış görsele düşer (`yedege_dustu`) ve ders defterine yazılır.
- Kalite birikimine karşı derinlik ≤ 2 ve yeniden demirleme. Doğal durak yoksa örtülü devam ([YN2] Y54).
- Seri bağımlılık süreyi uzatır; çözüm hız değil **sıra**: akış içi dalgalar. Flow temposu zaten darboğaz olduğu için ([UM] §1.3, ≈ 13 saat, hesap) ek gecikme sınırlıdır. Bedel kalite değil süredir (kesin karar 6).
- Z1 kaynağının V3 kör gözlemi video sırasında gerekir; gözetimsiz modda `vlm: claude_api` ile sürer (§4.3.5).

#### 4.8.7 Karar 3e — Kendi kendine öğrenen ders defteri
1. **Kayıt:** her kapı kararı (ölçü, değer, karar) ve sonradan olanlar (V2/V3/G1Z/K1/kurgu seyircisi/kullanıcı notu aynı planda bir şey buldu mu) [UM] ortak biçimiyle yazılır. Sınıflar: `kacirma`, `yanlis_alarm`, `dogru`. K1 ↔ seyirci eşlemesi kaçırma etiketinin bağımsız kaynağıdır ([KU2] İ-1).
2. **Kalibrasyon:** ≥ 30 etiketli örnek biriken her kapı/alan için eşik, kaçırma ≤ %10 olacak biçimde korkuluklar içinde ayarlanır (§4.7.10). Karakter başına kimlik bantları `KALIBRASYON.json`'a yazılır.
3. **Kural adayı:** aynı kök neden ≥ 3 kez ve ≥ 2 sahne grubunda görülürse aday olur (tahmin; [UM] terfi eşiği ≥ 3 kayıt ve ≥ 2 film ya da tek filmde ≥ 5 ile birlikte). Türler: (a) **önleyici istem eki** (ör. nesne taşıyan her planda "her OTHER hand is empty"); (b) **eşik**; (c) **plan uyarısı** yönetmene ("iki el aynı yarıda ve nesne var → ekleme planına böl"); (d) **soru daraltma** (§4.7.10 şartlarıyla).
4. **Deneme:** kural sonraki 40 uygun planın yarısına uygulanır (tek/çift plan numarası, tahmin); hata oranı karşılaştırılır. Düşürüyorsa kalıcı, düşürmüyorsa geri alınır. Karar `Ruling: <karar> — <neden> — <yanlışsa maliyeti>` biçiminde yazılır (03§B6).
5. **Sınır:** güvenlik ve kullanıcı kuralları öğrenmeyle gevşetilemez. Kural metnini `sureklilik-denetcisi ders` kipi yazar, terfiyi `ders-editoru` yapar ([CM]); rol dersleri `SubagentStart` kancasıyla denetçi ve yazar ajanlara eklenir, **`kare-tarifcisi`'ne eklenmez** (kör kalmalı).

#### 4.8.8 Karar 3f — Kalıcı seri evreni kütüphanesi
- Karakter, kostüm, mekân plakası, nesne kartları, kimlik dizeleri, yüz bankaları, kalibrasyonlar, onaylı ana kareler ve son dünya durumu `EVREN/<SERI>/` altında, **sahip başına ayrı dosyada** tutulur (§4.5.1). Ses ve hikâye içeriği kendi dosyalarındadır; görüntü dosyaları yalnız yol tutar.
- Kilitli kart **değişmez**; değişiklik yeni sürümdür (`surum`, `gecmis`). Film hangi sürümü kullandığını `EVREN_BAG.json`'da saklar. SHA1 uyuşmazlığı hattı durdurur.
- Varyantlar (kostüm 2, yırtık kol, büyümüş yaratık) her zaman **onaylı karttan referansla** türetilir (YR A6) ve kart kapısından geçer; öz tutarlılık ana karta göre ölçülür.
- Eski filmlerin kartları (EMBERFALL, B1–B3) `evren.py --ice-al` ile alınır; yüz paneli ve arka görünüm eksikse yalnız bunlar üretilir, onaylı görünüş korunur.
- `kimlik_en` ad içermediği için ad değişikliği kartı bayatlatmaz.

#### 4.8.9 Karar 4 — Ses ve dudak uyumu (bu alanın görüntü tarafındaki payı)
- Karar ses uzmanınındır. Ana yol "Veo konuşur + yerel ses dönüştürme" görüntüye ikinci bir model dokundurmaz; G1 ve V2 kimlik ölçümleri geçerli kalır. Bu alan bu yolu destekler.
- Yedek `tts_dudak` ağız bölgesini yeniden üretir: çıkan klip **V2'den yeniden geçer** (`video_denetim --dudak`; §4.7.7).
- Konuşmalı planların başlangıç karesi şunları sağlar: ağız kapalı ve görünür (`jawOpen` ≤ 0,15, tahmin), `yuz_acisi` `on` ya da `3/4`, \|yaw\| ≤ 45°, yüz yüksekliği karenin ≥ %12'si (tahmin; [YN2] Y32). Dinleyen kişilerde de ağız kapalı. Konuşmalı planda Z2 yok ([YN2] Y56).
- V2 replik penceresinde kare kare yüz izini (`jawOpen` dahil) ses uzmanına verir; dudak denetimi yüzü ikinci kez aramaz.

#### 4.8.10 Karar 5 — Memmet seri üretim aracı değil; bot atlatma yok
- Bu alanın Flow'a etkisi yalnız **daha az ve daha doğru gönderim**dir: G1 bozuk kareyi videoya göndermez, yeniden çekim azalır.
- Görsel düzeltmeleri Flow'da yapılacaksa: x2 çıktıyla gönderim yarıya iner, tempo `MEMMET_AYAR.json` (17.10) değerlerinde kalır, kullanıcı başındaysa `--mod elle`, görsel günü video günü değildir, günlük tavan ayardadır (değeri kaynakta yok; ders defteri kullanıcının hesabına göre yalnız **yavaşlatma** yönünde ayarlar).
- Uyarıda, reCAPTCHA'da, kredi bitince DUR. Hazır sonuçlar `memmet_topla.py` ile yeni gönderim yapmadan toplanır. Bu alan hiçbir otomatik yeniden deneme yazmaz. Z1 dalgaları gönderimi sıraya sokar, hızlandırmaz.

#### 4.8.11 Karar 6 — Hiçbir iş üstün körü yapılmaz
- Her plan 2 aday; her aday tam kapı; örnekleme yok ("her 5 kareden 1'ine bak" yok). Kör gözlem her adayda ve her V3 karesinde yapılır, kritik alanlar iki kez sorulur.
- Eksik araç ya da model "geçti" sayılmaz; `ÖLÇÜLEMEDİ` → hakem.
- Bozuk kare ya da klip "idare eder" diye kullanılmaz; hakem HATA'yı geçiremez; 2 turda düzelmeyen planı yönetmen değiştirir.
- Tasarruf için aday ya da soru azaltılmaz. Kör gözlem maliyeti (≈ 3 milyon girdi tokeni/film, ≈ 175 görev, tahmin) baştan söylenir. Z1'in süre bedeli kabul edilir.

---

### 4.9 Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

#### 4.9.1 Riskler ve önlemler

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | SFace'in 0,363 eşiği gerçek fotoğraflar için verilmiş; sinematik YZ karelerinde (profil, karanlık, sakal) benzerlik düşebilir (02§1.1) | Yanlış alarm ya da kaçırma | Üç bantlı karar + fark payı + karakter başına kalibrasyon; GS0 kalibrasyonu (B3 44 kare + P1'den 20 zor plan) |
| R2 | Görüntü-dil modelleri sol/sağ eli ve parmak sayısını sık karıştırır | Ters el kaçar ya da yanlış alarm | Görüntü koordinatında iki aşamalı form, anatomik çeviri kodda, kritik alan iki kez karışık sırayla, yerel Pose ile çapraz kontrol, anlaşmazlık hakeme; parmak en çok B |
| R3 | MediaPipe el ataması girdiyi ayna kabul ediyor; sırtı dönük kişide el tersine döner (02§4) | Ters el ölçümü hatalı | Birincil ölçüm Pose bilekleri; `yuz_acisi` ile çeviri; sırtta kritik el ÖLÇÜLEMEDİ → hakem |
| R4 | OWLv2 küçük nesneleri 1376 px karede kaçırabilir | El–nesne ölçülemez | El çevresi büyütülmüş kırpıntıda ikinci arama; yine yoksa kör gözlem + hakem; yönetmene: kritik küçük nesne → ekleme planı (ZAN§3.5) |
| R5 | Z1'de 720p sıkıştırma birikir; Veo'nun ilk 0,3–1,0 sn durağanlığı dikişte takılma verir | Zincirli planda kalite ya da akış düşer | Derinlik ≤ 2 + yeniden demirleme; örtülü devam (Y54); GS0'da derinlik 0/1/2 kliplerinin bulanıklık ve V2 ölçüleri karşılaştırılır, gerekirse derinlik 1'e iner |
| R6 | Görsel düzeltme hacmi (≈ 240 görsel/film, tahmin) Flow'da uyarı riskini artırır; ücretsiz yolda takvim uzar | Hat durur ya da gecikir | `gorsel_duzeltme` zinciri (API önce, izin varsa), görsel günü ≠ video günü, basamak sonunda toplu; asıl çare ilk tur kalitesi (B6); takvim `URETIM_ONIZLEME`'de dürüstçe |
| R7 | Kullanıcının paket taşıma işi (kart + basamaklar + ikinci göz ≈ 10–13 tur, tahmin) "yalnız konu" hedefiyle gerilim yaratır | Kullanıcı yorulur | Parti düzeyinde birleşik paketler (İ-8); bitiş dosyadan algılanır; `vertex_gorsel` kurulum seçeneği |
| R8 | Windows/Python 3.10 kurulum ağırlığı: son cp310 Windows torch tekerleği 2.9.1, onnxruntime ≤ 1.23.2 (02§6.3); `transformers` ve `mediapipe` sürüm uyumu bu belgede doğrulanmadı | Kurulum kırılır | `kurulum.py` sürümleri sabitler ve kendini sınar; ölçüm modülü eksikse ÖLÇÜLEMEDİ; 4 GB GPU'da DINOv2-small/OWLv2-base (sığması tahmin), yoksa CPU; Windows + 3.10 CI ([UM] §6.4) |
| R9 | Kör gözlemin token ve görev yükü (≈ 3 milyon girdi tokeni, ≈ 175 görev/film, tahmin); Claude Code kullanım sınırı | Hat yarıda kalır | Görev defteri kaldığı yerden sürer; yerel ölçüm açık HATA'ları önceden eler; GS0'da görev boyu 20'ye çıkarılabiliyor mu ölçülür; gözetimsiz mod `claude_api` |
| R10 | Z1 dalgasında V3 kör gözlemi ana Claude'u gerektirir | Gece üretiminde ardıllar bekler | `vlm: claude_api` (anahtar varsa); yoksa ardıllar sonraki oturuma kalır ve kullanıcıya bilgi verilir |
| R11 | Görsel üretici kroki geometrisine birebir uymaz | Geometri denetimi aşırı katı olur | Geometriden yalnız sol/sağ sırası, üçte bir ve "görünmesi gereken öğeler" denetlenir; açı ve derinlik ölçülmez; plakalar krokiden istenir ([YN2] R5) |
| R12 | Aşırı katı kapılar çok aday reddeder | Zaman ve Flow görsel yükü | Yanlış alarm hedefi ≤ %30; aday 0 kredidir; kalibrasyonla gevşer (güvenlik dışı eşiklerde) |
| R13 | Ticari olmayan lisanslı araçların hatta sızması (InsightFace modelleri, pyiqa, DOVER, CoTracker; 02§0) | Kanal için hukuki risk | `kurulum.py` yalnız izinli listeyi kurar: OpenCV/opencv_zoo (Apache-2.0), MediaPipe (Apache-2.0), DINOv2 (Apache-2.0), OWLv2 (`transformers`, Apache-2.0), CLIP (MIT), PySceneDetect (BSD-3) |
| R14 | Kilitli kartın kullanıcı tarafından elle değişmesi | Seri içi tutarsızlık | SHA1 denetimi hattı durdurur, sürüm açtırır |
| R15 | **(yeni)** Kamera ağacında ebeveyn yeniden üretilince çocuklar bayatlar | Basamak tekrarları | [YN2] `bayat` yayılımı; ana kare G1'i sıkı tutulur; düzeltmeler basamak sonunda toplu |
| R16 | **(yeni)** Gemini ikinci gözü beklenen listeyi görür (kör değil), onaylama eğilimi taşır | Yanlış güven | Yalnız bulgu kaynağıdır, hiçbir şeye GEÇ demez (İ-6) |

#### 4.9.2 Diğer uzmanlarla kalan çakışma noktaları
1. **[UM]:** `devam`'da `bitis_karesi` varsayılanı ve V05'te `son_kare` planlarına görsel üretilmemesi (İ-1); risk planına sınırlı 2 aday ve BAYRAK'a sınırlı VLM (İ-2); düzeltme görsellerinin yolu (İ-13). [YN2] ve [KU2] Z1'de birleşti; [UM]'nin onayı ve 13 saatlik süre hesabına Z1 akış içi dalga etkisinin eklenmesi gerekli.
2. **[CM]:** G1'in hakemle kapanması (İ-3); soru formu (İ-4); A09 → A10 sırası (İ-5); `kart-tasarimcisi` kadroya eklenmeli (15 + 1 ajan); toplam ajan çağrısı tahminine ≈ 175 `kare-tarifcisi` görevi eklenmeli.
3. **[YN2]:** Z1 + Z2 aynı klipte (GS0'a kadar BAYRAK); türev referans sayısı (İ-8); örnekteki "1280×720 → 1376×768" (İ-7); `kostum` değerinin karakter kapsamlı yazımı (`k1`, `mara_k1` değil).
4. **[KU2]:** 0 kredi merdiveninde ayna, yeniden kadraj ve yer tutucu sonrası yeniden ölçüm (İ-9).
5. **[SM2]:** yüz izi dosyasının biçimi ve `tts_dudak` sonrası V2 eşikleri (İ-10).
6. **[SN2]:** `ayrisma_kilitli` durumunda karar yolu (İ-12).
7. **Orkestratör:** GS kodlarının `ASAMALAR` kaydına yerleşmesi; `vlm` ve `gorsel_duzeltme` sağlayıcı türleri.

#### 4.9.3 Açık sorular
1. **Görsel üretim ve düzeltme sağlayıcısının varsayılanı:** Gemini paketi (0 kredi, kullanıcı ZIP taşır) + Flow düzeltmesi mi, yoksa ücretli görsel API'si (tek kaynaklı fiyat Vertex Gemini görsel ≈ 0,134 $/görsel; film başına ≈ 1.400–1.500 görsel ≈ 190–200 $, hesap) mı? Bir kurulum ayarıdır; film başına sorulmaz.
2. **Karakter dışı referans sınırı:** "≤ 2 referans" karakter sayısı içindir; ebeveyn kare ve plakayla toplam 3 görsel yüz karışması yapar mı? (GS0 A/B.)
3. 1280×720 zincir karesi Flow'da başlangıç karesi olarak kaliteyi ne kadar düşürür; 1376×768'e oran korunarak büyütmek fark eder mi? (GS0.)
4. Flow Extend "son 24 kare" (02§2.2, doğrulanmadı) Z1'e alternatif olabilir mi, model değiştirme uyarısı getirir mi? Denenmeden kullanılmaz.
5. Kör gözlemin varsayılan yürütücüsü: Claude Code alt ajanı (abonelik) mı, `claude_api` (gözetimsiz, ücretli) mi? İkisi de sağlayıcı olarak tasarlandı.
6. `EVREN/` görselleri yalnız kullanıcının diskinde kalırsa bulut oturumu kartları göremez; kart kapısı ve G1 yalnız yerelde koşar (karar mantığı bulutta `sahte` ile test edilir). Uygun mu?
7. B3'ün etiketli 44 karesi (`D:\YZ_FILM_ARSIV`) kalibrasyon başlangıç seti olarak kullanılabilir mi? Yerel oturumun etiket JSON'unu depoya alması gerekir.
8. Kart biçimi çelişkisi (BK§8 #19): açık gri fonlu birleşik sayfa önerildi (onaylı kartlar ve Gemini ajanı bu biçimle iyi sonuç verdi; B3'te 29 kart tek seferde). Yeşil fon (Seedance biçimi) ile ölçülü karşılaştırma yapılmadı.
9. Gemini ajanı çıktılarında görünür filigran olup olmadığı belgelerde yok. Kör gözlem `yazi_logo` alanında yakalar; çıkarsa kırpma politikası gerekir.
10. Flow'da günlük görsel tavanı ve görsel → video bekleme süresi için kaynakta sayı yok. Varsayılanı [UM] koyar; ders defteri yalnız yavaşlatma yönünde ayarlar.

#### 4.9.4 Kalibrasyon partisinde (GS0) ölçülecekler — özet
| Soru | Seçenekler | Karar ölçüsü |
|---|---|---|
| G1 eşikleri | 0,45 / karakter başına bant | B3 44 kare + P1 20 plan; kaçırma ≤ %10 |
| Zincir karesi biçimi | 1280×720 doğal ↔ 1376×768 oran korunarak | G1Z kimlik, V2 ilk kare sadakati, K1 dikiş |
| Z1 + Z2 aynı klipte | var ↔ yok | V2 morf sıçraması, V3 uyumu |
| Türev referansı | (A) ebeveyn + ≤ 2 kart ↔ (B) ebeveyn + kimlik demiri kartı | G1 kimlik ve yanlış kişi oranı |
| Kör görev boyu | 12 ↔ 20 görsel | etiketli sette doğruluk farkı |
| Zincir derinliği | 0 / 1 / 2 | bulanıklık, V2 ölçüleri |
| MediaPipe | Python 3.10 Windows tekerleği, yaw işareti, `jawOpen` | test görselleri |
Ek kredi yalnız karşılaştırma klipleridir (≈ 120 kredi, hesap; klip sayısı tahmin).
