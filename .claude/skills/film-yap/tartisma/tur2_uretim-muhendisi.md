# Tur 2 — Üretim Mühendisi: itirazlar, çakışmalar, revize nihai öneri

Hazırlayan: üretim-mühendisi uzmanı (Claude Opus 5.5). Tarih: 23.10.2026.

**Bu turda okunanlar**
- `tartisma/` altındaki yedi tur 1 dosyasının tamamı (kendi dosyam dahil).
- Benden önce yazılmış dört tur 2 dosyası: senarist, yönetmen, kurgucu, ses-müzik. Benim alanıma yöneltilen itirazları cevaplamak ve
  aynı alan adlarını kullanmak için okundu. Görüntü-süreklilik ve Claude Code mimarisi tur 2 dosyaları bu yazım sırasında klasörde yoktu.
- Dayanak belgeler: `BILGI_KURALLARI.md` §6 ve §8 (21 çelişki), `ritim_esikleri.json` (anahtarlar betikle listelendi), `ZANAAT.md` §2.6,
  `03_DERSLER.md`.
- Mevcut kod yeniden okundu: `film.py`, `saglayicilar/` (4 dosya), `memmet.py` (başlık, `kontrol_noktasi`, `istemler`, `asama`, `calis`,
  `kurgu`), `yeni_film.py`, `testler/test_film.py`.

**Dosya kısaltmaları:** `[CM]` Claude Code mimarisi tur 1 · `[GS]` görüntü-süreklilik tur 1 · `[KU1]/[KU2]` kurgucu tur 1/2 ·
`[SN1]/[SN2]` senarist tur 1/2 · `[SM1]/[SM2]` ses-müzik tur 1/2 · `[YN1]/[YN2]` yönetmen tur 1/2 · `[UM1]` benim tur 1 dosyam.

**Kaynak kısaltmaları:** `BK` BILGI_KURALLARI · `ZN` ZANAAT · `RE` ritim_esikleri.json (anahtar adıyla) · `A1/A2/A3` araştırma 01/02/03 ·
`DR` 03_DERSLER · `FK` FLOW_KESIF · `YR` YAPIM_REHBERI · `KR` KARARLAR · `CI` CLAUDE_ICIN · `H/<ad>` HAFIZA_YEDEGI notu ·
`D/hooks` vb. [CM]'nin belgeden doğruladığı Claude Code bilgisi.

**Etiketler:** **[kaynak: X]** belgeden · **[hesap]** benim aritmetiğim (girdileri yazılı) · **[tahmin]** kaynağı olmayan başlangıç
değeri, ders defteriyle ayarlanır · **[doğrulanmadı]** denenmeden yazılan bilgi.

### Bu turun özü (6 satır)
1. **Tek protokol:** iş birimi [CM]'nin görev defteridir (`_GOREV/<id>/`). Dışarıya karşı tek çıkış kodu tablosu benimdir (0–8; **8 BEKLE**
   yeni). Alt araçların kendi kodları (ör. `3 = eşik altı`) içeride kalır ve `film.py` onları eşler. Aşama kodları [CM]'nin A-kodlarıdır;
   nihai sıra ve her uzmanın kodlarıyla eşleme §2.1'de.
2. **Kare zinciri Z1 (gerçek kesme karesi) varsayılandır;** tur 1'deki `bitis_karesi` varsayılanımı geri çekiyorum. Bunu katı dalgalarla
   değil **uygunluk kuyruğuyla** uyguluyorum: zorunlu Flow molalarının içinde V2/V3 ve zincir karesi işlenir, ek bekleme olmaz.
3. **Flow yükü hesap düzeyinde sayılır** (`FLOW_YUK.jsonl`, `FLOW_TEMPO.json`). Görsel düzeltmeleri, video ve yeniden başlatmalar aynı
   sayaçtan geçer. Memmet'i yeniden açmak molayı kısaltamaz.
4. **Pilot dalga:** ilk filmde P1'den kapsamayla seçilmiş 20–30 gerçek plan önce üretilir. Eşik kalibrasyonu, istem biçimi, ses yolu
   kıyası ve fiyat ölçümü tek seferde yapılır. Ek kredi yoktur; planlar filmin kendisidir.
5. **İki kök:** Windows'ta Claude Code depo kökünde açılır (`.claude/` yüklensin). Kullanıcının verisi `Desktop\YZ_FILM`'de kalır,
   yol `YOLLAR.json`'dan okunur. Bulut ile yerel arasında kâğıt çıktıları yalnız `film.py esitle` ile, beyaz listeyle taşınır.
6. **Dürüst takvim:** 40 dk'lık film ≈ 6.320 Flow kredisi, ≈ 13 saat Flow süresi, ≈ 116 Flow görsel düzeltme gönderimi (≈ 6 görsel günü)
   ve ≈ 350–550 Opus ajan çağrısı ister [hesap, tahmin]. Toplam takvim ≈ 2–3 haftadır [tahmin].

---

## 1. Diğer önerilere itirazlarım (dosya + madde + neden + önerim)

★ işaretli üç madde en önemli itirazlarımdır. Hepsi doğrudan benim alanıma dokunur: hat protokolü, Flow kısıtı, gizlilik ve taşıma.

### ★ İ-1 · [GS] §3.5 ve §6 · [CM] §5.3 ve K-2 · [SN1] §6 · [KU1] §6.1 · `puan_oku.py` — Üç ajan devri protokolü, dört anlamda kullanılan çıkış kodları
- **Ne yazılmış:**
  - [GS] §3.5: "`film.py` … `_AJAN_ISLERI/<is_id>.json` yazar ve **çıkış kodu 2** ile 'AJAN İŞİ BEKLİYOR' der." [GS] §6 başı: "çıkış kodu 0 bitti / 2 durdu (ajan ya da kullanıcı işi) / 1 hata". Kör gözlem görevleri ayrıca `_KOR_GOREV/<is_id>/` altında.
  - [SN1] §6: `metin` sağlayıcısı `GOREV_<asama>.md` yazar ve çıkış 2 ile durur. [SN1]/[SN2] `hikaye_odasi.py`: "0 geçti · **3 eşik altı** · 2 girdi eksik · 1 hata".
  - [KU1] §6.1: "**çıkış kodu 4 = ajan işi bekleniyor** (`_RAPOR/AJAN_ISLERI.json`)".
  - [CM] §5.3: `film.py sonraki` görev listesi verir; çıkış kodu tanımlanmamış.
  - [UM1] §2.0: 0–7 tablosu, **3 = AJAN**.
- **Neden sorun:**
  1. `.bat` dosyaları ve Telegram mesajı çıkış koduna göre konuşur. `2` hem "Claude'un ajan işi var" hem "Flow doğrulama istiyor, sen çöz"
     anlamına gelirse kullanıcıya yanlış talimat gider. Kötü durumda **ACİL** bir kısıt "ajan işi" diye susturulur.
  2. Alt araçlardaki `3 = eşik altı` anlamı `film.py` düzeyindeki `3 = ajan işi` ile çakışır. Bir betik bir başkasının kodunu geçirirse
     hat yanlış dala sapar.
  3. [KU2] (§2.1 son satırlar) ve [SN2] (§3 "geri çektiklerim") kendi protokollerini geri çekti; [YN2] Ç-21 ve [SM2] Ç-13 benim tablomu
     destekliyor. [GS]'nin protokolü hâlâ açık.
- **Önerim:**
  - **İş birimi** [CM]'nin görevidir: `_GOREV/<id>/{GOREV.json, ISTEM.md, GIRDI/, CIKTI/}`. Komutlar `film.py sonraki | basla | bitir | kurtar`.
    [GS]'nin `_AJAN_ISLERI/` ve `_KOR_GOREV/` klasörleri bu görevin `GIRDI/`'si olur. Soru formunu [GS]'nin `kor.py` modülü üretir,
    görevi `film.py` kurar.
  - **Dış çıkış kodu tablosu tektir** (§4.2.0). `0 BİTTİ · 1 HATA · 2 KULLANICI · 3 AJAN · 4 ORTAM · 5 BÜTÇE · 6 KAPI · 7 KISIT · 8 BEKLE`.
    **8 BEKLE yenidir:** Flow molası, görsel→video beklemesi, GPU işi sürüyor. Kullanıcıdan bir şey istenmez; yalnız "en erken şu saatte" yazılır.
  - **Alt araç kodları içeride kalır** ve yalnız `film.py` onları okur. Eşleme tablosu §2.6'da (`3 eşik altı` → tur sayacı; tur dolduysa `6 KAPI`).

### ★ İ-2 · [GS] A9 ve §8.10 · [YN2] Y8 · BK §6.3 #4, #9 — Flow görsel yükü hesap düzeyinde sayılmıyor
- **Ne yazılmış:**
  - [GS] A9: CORRECTION turunda 2 yeni aday üretilir, en çok 2 tur. Yeniden üretim sağlayıcısı Flow görseli (Memmet). §8.10: "Günlük görsel
    gönderim tavanı ve görsel→video bekleme süresi ayar dosyasındadır (değerleri kaynakta yok)."
  - BK §6.3 #9: düzeltme görselleri kullanıcıya paket olarak **verilmez**, Memmet ile Flow'da yapılır [kaynak: H/gemini-ajan-gorsel].
  - DR satır 5: "Aynı akşam ~40 görsel gönderdikten sonra video tarafı tamamen işaretlendi … Yoğun görsel turundan hemen sonra videoya başlama."
- **Hesap (Flow görsel düzeltme yükü):**
  - Denetimsiz üretimde sağlam başlangıç karesi oranı B3'te 23/44 = %52'ydi [kaynak: DR, GS §1.2].
  - Plan başına 2 aday Gemini paketinde (0 Flow) üretilirse en az birinin sağlam olma olasılığı 1 − 0,48² ≈ 0,77 [hesap; adayların
    bağımsız olduğu varsayımı tahmin]. Yani ≈ 405 × 0,23 ≈ 93 plan düzeltmeye kalır.
  - Flow ayarlarındaki x2 çıktıyla bir gönderim 2 aday verir [kaynak: GS A7, FK]. İkinci tura ≈ %25 [tahmin] kalır: ≈ 23 plan.
  - Toplam ≈ 116 Flow görsel gönderimi [hesap]. Bu, DR'deki işaretlenme olayındaki sayının ≈ 3 katıdır.
- **Neden sorun:**
  1. Hiçbir öneride **hesap düzeyinde** (filmler arası) bir gönderim sayacı yok. Flow hesabı filmi değil hesabı işaretler.
  2. Görsel→video beklemesinin değeri yok, sahibi de yok ([GS] §9.3 soru 10 bunu açıkça soruyor).
  3. Mevcut `memmet.py`'de mola sayacı (`sonraki_mola`) yalnız bellekte. Memmet kapanıp yeniden açılınca mola sıfırlanır. Yani yeniden başlatmak,
     kimse istemeden **tempoyu hızlandırır**. Bu, kesin karar 5'in (tempo, bot tespiti) sessiz ihlalidir.
- **Önerim:**
  - **`FLOW_YUK.jsonl`** (veri kökünde, hesap başına, yalnız eklenir): her Flow gönderimi `{zaman, hesap, film, tur: gorsel|video, plan, mod}`.
  - **`FLOW_TEMPO.json`**: sonraki izinli gönderim zamanı, ara mola ve blok molası sayaçları. Memmet her gönderimden önce buna bakar;
    yeniden açılsa da kalan molayı bekler.
  - **Günlük Flow görsel tavanı 20** [tahmin: DR'deki ~40'ın yarısı]. Görsel gönderilen günden sonra video için en az **12 saat** beklenir
    [tahmin]. "Görsel günü" ile "video günü" ayrılır.
  - Görsel düzeltme gönderimleri de kullanıcı başındayken `elle` modda gider (BK §6.1).
  - Makine bu sınırları **yalnız sıkılaştırabilir**. Gevşetmek kurulum ayarıdır (`FILM_AYAR.json → flow`), yani kullanıcının açık kararıdır.
  - Kurulumda dürüstçe söylenir: düzeltme görselleri Flow'da ≈ 6 görsel günü sürer [hesap: 116 / 20]. Ücretli `vertex_gorsel` yolu
    ≈ 116 × 2 × 0,134 $ ≈ 31 $ ile bunu birkaç saate indirir [hesap; fiyat: GS ve 06_SERVISLER]. Varsayılan dolar tavanı 0'dır.
  - Ek kaldıraç (açık soru Q13): Gemini paketinde aday sayısı 3 olursa düzeltmeye kalan plan ≈ 405 × 0,48³ ≈ 45'e iner ve Flow görsel
    günleri ≈ 3'e düşer [hesap; paket başına 90 görselin Gemini ajanında çalışıp çalışmadığı doğrulanmadı].

### ★ İ-3 · [CM] §5.7, `.claude/settings.json` deny listesi, K-4, R-1, S-1 — Erişim ve git politikası iki kökü ve bulut gerçeğini görmüyor
- **Ne yazılmış:**
  - `deny`: `Read(./YZ_FILM/AYARLAR/ai84_anahtar.txt)`, `…/telegram_bot.txt`, `…/kie_anahtar.txt`, `…/memmet_profil/**`, `Bash(git push *)`.
  - S-1: "Önerim: üretimin tamamı kullanıcının Windows'unda yürüsün, bulut yalnız geliştirme ve sahte test için kullanılsın."
  - R-1: `.claude/` depo kökünde, kullanıcının klasörü ise `Desktop\YZ_FILM`. Önerilen çözüm: `GUNCELLE.bat` `.claude/`'u oraya kopyalar.
- **Neden sorun:**
  1. **Anahtar listesi eksik ve yanlış yerde.** Yeni anahtarlar (Anthropic API, Freesound [SM2 SB4], YouTube OAuth, Vertex) listede yok.
     Windows'ta gerçek `AYARLAR` klasörü `C:\Users\Soysal\Desktop\YZ_FILM\AYARLAR`'dır ve kalmalıdır (CLAUDE.md: "yolları bozma").
     Depoya göreli kural o klasörü korumaz.
  2. **`git push` yasağı taşıma yolunu kapatır.** Görev tanımı açık: "bulut oturumunda yalnız kâğıt aşamaları ve 'sahte' sağlayıcı çalışır".
     Kâğıt çıktısı yerele ancak git ile gider.
  3. **`.claude/`'u veri klasörüne kopyalamak** iki kopya yaratır (depo ve masaüstü). Hangi `film.py`'nin çalıştığı belirsizleşir;
     güncelleme yarım kalırsa ajanlar, kancalar ve betikler farklı sürümlerde çalışır.
- **Önerim (ayrıntı §4.5.12–4.5.14):**
  - **İki kök.** Windows'ta depo bir kez klonlanır (öneri `C:\Users\Soysal\Desktop\YZ_FILM_SET`) ve Claude Code **orada** açılır.
    `.claude/`, `CLAUDE.md`, `YZ_FILM/ARACLAR` buradan çalışır. Veri kökü `C:\Users\Soysal\Desktop\YZ_FILM` yerinde kalır:
    `AYARLAR`, `FILMLER`, `SES_KUTUPHANESI`, `EVREN` medyası, Memmet Chrome profili. Bağlantıyı `AYARLAR/YOLLAR.json` kurar.
    Bulutta iki kök aynı klasördür (`<depo>/YZ_FILM`).
  - **`erisim_kapisi` veri kökünü `YOLLAR.json`'dan çözer** ve `<veri_kok>/AYARLAR/**` ile `<depo>/YZ_FILM/AYARLAR/**`'ı **desenle** reddeder.
    İstisnalar: `*.ornek.json`, `OKU_BENI.txt`. Anahtarları yalnız betikler okur; ana Claude ayarı `film.py goster ayar` ile maskeli görür.
  - **Push yalnız `film.py esitle --gonder` ile** yapılır: beyaz listedeki kâğıt dosyaları, ayarlı dal, anahtar taraması (M13). Çıplak
    `git push` yasağı kalır. İzin kuralı `Bash(python .claude/bin/film.py *)` bunu zaten kapsar.
  - **Git yoksa** (açık soru Q7) yerel tek kök çalışma varsayılandır. [CM] S-1'in "her şey yerelde" önerisi böylece seçeneklerden biri olur.

### İ-4 · [YN2] İ-2 · [KU2] öz 3 · [GS] A11 — Z1'i kabul ediyorum; katı dalgaları ve "Z0/Z1/Z2" adlarını değil
- **Kabul:** `devam` geçişinde varsayılan, önceki klibin kesme anındaki **gerçek karesidir** (Z1). Her plana planlanmış görsel de üretilir
  (animatik ve yedek). Tur 1'deki `bitis_karesi` varsayılanımı geri çekiyorum. Gerekçe: kesin karar 3(d) bunu sözcüğü sözcüğüne söylüyor,
  bedeli kalite değil süre ([YN2] İ-2).
- **İtiraz 1 (uygulama biçimi):** [GS] A11'deki "dalga 1 → dalga 2 → dalga 3" katı sırası, dalga 1'in **hepsi** bitmeden dalga 2'yi başlatmaz.
  `elle` modda bu, kullanıcının dalga başına ayrı oturuma çağrılması demektir. Gece modunda ise Flow oturumu boşta bekler.
- **Önerim:** **Uygunluk kuyruğu** (§4.2.4). Her 20'lik blok, o an uygun olan planlarla hikâye sırasına göre doldurulur. Kaynağı V1+V2+V3'ten
  ve G1-zincirden geçmiş `son_kare` planı bir sonraki bloğa girer. Zorunlu Flow molaları (8 gönderimde 3–6 dk, 2 blokta 15–30 dk
  [kaynak: BK §6.2 #6]) bu işlemler için kullanılır. DAG yalnız sırayı belirler, hızı değil [kaynak: A1 B6].
- **İtiraz 2 (adlandırma):** "Z0 / Z1 / Z2" zincir yöntemleri ZN §6.2'deki **Z0–Z3 kapı** adlarıyla çakışır. `_RAPOR/Z1_P2.json` bugün
  "bilgi kapısı, parti 2" demektir. **Kodda** değerler `bagimsiz | son_kare | bitis_sabit` olur. "Z1" yalnız ZN kapısının adıdır.

### İ-5 · [UM1] §3.5 (öz eleştiri) · [CM] §7 — Ajan çağrısı tahminim yanlıştı
- [UM1] 90–190 çağrı demişti. Diğer uzmanların tur 2 sayılarıyla yeniden hesap (§4.3.4): **≈ 350–550** [tahmin]. En büyük kalem kör gözlemdir
  (≈ 1.050 aday görsel ÷ ≤ 12 görsel/çağrı ≈ 90 çağrı yalnız G1 için [hesap; görev boyu GS tahmini]).
- **Sonuç:** Kullanım sınırı artık bir köşe riski değil, takvimin belirleyicisidir (R1). Önlemler: her şey dosyada; [CM]'nin `StopFailure`
  kancası Telegram'a "sınır doldu" yazar; paralel ajan tavanı ≤ 5 [kaynak: YN2, tahmin]; başsız yürütme isteğe bağlı (İ-6).

### İ-6 · [GS] §3.5 `gozlemci/claude_api` · [KU1] `seyirci_api.py` · [SN1] `saglayicilar/claude_api.py` · [CM] K-23 `claude -p` — Dört ayrı başsız yürütme yolu
- **Neden sorun:** Aynı ajan işi dört ayrı kodla API'ye gider. İstem, girdi ve çıktı sözleşmesi dört yerde ayrışır. Habersizlik ve şema
  denetimi bir yolda olup ötekinde olmayabilir.
- **Önerim:** Tek yürütücü `film.py yurut --basliksiz <gorev_id>` ve tek `saglayicilar/claude_api.py`.
  - Aynı `ISTEM.md` ve aynı `GIRDI/` dosyaları kullanılır; çıktı aynı `CIKTI/`'ye yazılır ve aynı `bitir` doğrulamasından geçer.
  - Kör rollerde modele yalnız `GIRDI/` içeriği gider. Bu, habersizliğin en sağlam biçimidir ([KU1] gerekçesi).
  - Model `claude-opus-5-5`, effort `high` (CLAUDE.md). Varsayılan **kapalı**. Açılması için `butce.usd_tavan_film > 0` gerekir ve önizlemede
    maliyet satırı yazılır.

### İ-7 · [CM] §5.6 · [GS] §5.11 ve §8.7 · [YN1] Y11 · [SM1] §5.9 · [KU1] §8.5 — Ders defterinin beş biçimi ve beş yeri
- **Durum:** [YN2] Ç-20, [KU2] §2.1 ve [SM2] §2.5 "[UM] ve [CM]'nin ortak biçimi kullanılsın, yer defter sahibinin kararı" diyor.
  Ama [CM]'nin biçimi tek bir `DERS_DEFTERI.jsonl`'a satır eklemedir, benimki olay başına dosyadır.
- **Neden tek JSONL olmaz:**
  1. Bulut ve yerel aynı dosyanın sonuna ekleyince `git pull` birleştirmede çakışır (iki taraf aynı yere ekledi).
  2. Elektrik ya da Ctrl+C yazımı yarıda keserse son satır bozulur ve dosyanın tamamı okunamaz hâle gelebilir.
- **Önerim (karar, §4.5.11):** Olay başına bir dosya: `YZ_FILM/BILGI/DERSLER/ham/<zaman>_<film>_<olay>.json`. `DERS_DEFTERI.jsonl` bunlardan
  **türetilen** dizin dosyasıdır ve git'e girmez. Kategori sözlüğü tektir: [KU2]'nin önerdiği `veri/kok_neden.json` (kurgu + hikâye + ses +
  süreklilik satırları). [GS]'nin kural denemesi (yeni kuralı uygun planların yarısına uygulayıp karşılaştırmak) `deneme` durumu olarak
  kabul edildi. Seriye özel kalibrasyon `EVREN/<SERI>/KALIBRASYON.json`'da kalır ([GS]).

### İ-8 · [CM] K-4 `UYARI_GECTI.bat` · [UM1] §5.6 · BK §6.2 #8–#9 — Uyarıdan sonra yeniden başlama üç ayrı biçimde
- **Ne yazılmış:**
  - [CM]: Flow kilidi yalnız kullanıcının `UYARI_GECTI.bat`'ıyla kalkar; gün değişince yeniden sorulur.
  - [UM1]: "O gün Flow'a yeniden başlatma yok."
  - BK §6.2 #8: hesap işaretlenirse önce kullanıcı Flow'da **elle 1 video** denesin. #9: kullanıcının "zorla bugün" kararı kalıcı değildir;
    yeni günde tekrar sorulur (varsayılan 30 dk).
- **Neden:** Benim kuralım kaynaktan daha katıydı ve kullanıcının kendi kararını yok sayıyordu. [CM]'ninki elle 1 video şartını taşımıyordu.
- **Önerim (karar):**
  - Makine **asla** kendiliğinden yeniden başlatmaz, tempoyu hızlandırmaz, uyarı metnini görmezden gelmez.
  - `UYARI_GECTI.bat` kilidi yalnız iki şartla kaldırır: (1) kullanıcı Flow'da elle 1 video denediğini ve başarılı olduğunu işaretler
    (BK §6.2 #8); (2) uyarıdan bu yana ≥ 30 dk geçmiştir (BK §6.2 #9).
  - Karar yalnız o takvim günü geçerlidir. O günün kalanında gönderim arası ×1,5 yavaşlar [tahmin].
  - Ertesi gün ilk blok, `gece_izni` olsa bile `elle` modda gider [tahmin]. Bu kural yalnız sıkılaştırır.

### İ-9 · [SM2] SB0 · [GS] §6.1 `olcum/` · [SM2] [D-MT] — 4 GB GPU ve üç Python sürümünü yöneten kimse yok
- **Durum:** Yerelde en az dokuz ağır model ailesi çalışacak: DINOv2, OWLv2, CLIP, MediaPipe, BS-RoFormer, faster-whisper, RVC, MuseTalk,
  ACE-Step. Üç Python ortamı gerekiyor: ana 3.10, RVC ve ACE-Step 3.11–3.12 [kaynak: SM2 D-RVC, D-AS], MuseTalk 3.10 + torch 2.0.1
  [kaynak: SM2 D-MT]. [SM2]: "4 GB kartta aynı anda tek ağır model koşar (tahmin; kuyruk betikte)". Ama bu betiği kimse sahiplenmemiş.
- **Neden sorun:** İki ağır iş aynı anda 4 GB'a yüklenirse biri bellek hatasıyla düşer. "ÖLÇÜLEMEDİ" sayısı yapay olarak artar ve
  hakem ajanına gereksiz iş gider. MuseTalk tek 8 sn klip için ≈ 5 dk sürer [kaynak: SM2 D-MT]. Kuyruk olmazsa bir yedek yol saatlerce GPU'yu tutar.
- **Önerim:** `yerel_is.py` (yerel ağır iş kuyruğu) + `GPU.kilit`. Ağır işler sırayla, CPU işleri paralel koşar. Python 3.12 kurulumu
  kullanıcının **tek seferlik kurulum işi** listesine girer (M2). `kurulum.py` her ortamı sınar; eksik ortam yalnız kendi basamağını kapatır
  ([SM2] SB0 ile aynı ilke).

### İ-10 · [CM] A13 "Klip × 12 × 1,2" ve `maliyet.py` · [KU1] `BUTCE.json` · [SN2] §2.5 — Bütçenin tek yeri
- [KU2] `BUTCE.json`'u geri çekti ve `URETIM_ONIZLEME.json → kredi.flow.dilimler`'i önerdi. [SN2] süreyi yazımdan önce bütçeye göre seçiyor.
  [CM] hâlâ pay 0,20 ve ayrı bir `maliyet.py` yazıyor.
- **Önerim:** Tek araç **`kredi.py`**, tek dosya `URETIM_ONIZLEME.json`. Kapı payı 0,30 (ilk film); RE'deki 0,20 **hedef** olarak kalır ve
  ders defteri gerçekleşeni ölçer. Dilimler [KU2]'deki gibi: görüntü/süreklilik/plan dili 0,15 · ses 0,07 · kurgu 0,08 [tahmin].
  Bütçe üç noktada ölçülür (B0, B1, B2; §2.5). Hiçbirinde film kısaltılmaz.

### İ-11 · [YN2] Y8 kamera ağacı · [GS] A7 — Görsel paketleri sıralı turlara bölünüyor; kullanıcı el işi artıyor
- **Durum:** Görsel üretimi dört basamaklı: plakalar → ana kareler → türevler → `devam` planlanmış görselleri. "Her basamak G1'den geçmeden
  sonraki basamağın paketi verilmez." Her plan için 2 aday var.
- **İtiraz değil, maliyet bildirimi:** Bu sıra doğrudur (hata bir ana karede yakalanır, 10 türeve yayılmaz). Ama kullanıcının Gemini paket
  taşıma sayısını ≈ 14'ten ≈ 18–24'e çıkarır [tahmin] ve her basamak arasında bir G1 bekleyişi ekler.
- **Önerim:** `gemini_paket.py` paketleri basamak içinde 30'luk doldurur ve basamaklar arasında **önceden hazırlar**. Kullanıcıya her paket
  için tek cümle ve Telegram mesajı gider. ZIP `GELENLER/`'e düşünce algılama kendiliğinden olur ([CM] `algilama: dosya_var`).
  Sayı M2 ölçütünde izlenir.

---

## 2. Çakışmalar ve önerdiğim çözüm (alan adları, aşama sırası, sorumluluk sınırları)

Orkestratörün (`film.py`), sağlayıcıların, bütçenin ve hat protokolünün sahibi olarak aşağıdaki kararları **nihai öneri** olarak yazıyorum.
İçerik kuralları (ne denetlenir) her zaman alanın sahibinindir. Ben yalnız sırayı, adı, dosyayı ve geçiş protokolünü sabitliyorum.

### 2.1 Nihai aşama listesi ve kod eşlemesi
Aşama kodları [CM]'nin A-kodlarıdır; [SN2] ve [KU2] bunları zaten dış kod olarak kullanıyor. Uzmanların iç adım kodları (H, Y, KR, SA–SF)
alt adım ve şablon adı olarak kalır. Ortam: **B** = bulutta da çalışır, **Y** = yalnız yerelde. Kredi: — yok · AI84 · Flow · $ (yalnız izinliyse).

| Kod | Aşama | [CM] | [UM1] | [SN2] | [YN2] | [SM2] | [KU2] | [GS] | Ortam | Kredi |
|---|---|---|---|---|---|---|---|---|---|---|
| A00 | Hazırlık + konu (tek soru) | A00 | H0, K01 | H0 | — | — | — | — | B/Y | — |
| A01 | Konu kartı, proje kararları, **B0 süre/bütçe** | A01 | K02 | H1 | — | — | — | — | B/Y | — |
| A02 | Brifing (betik, sha1 sabit) | A02 | K02 | H2 | — | — | — | — | B/Y | — |
| A03 | 4 mimar önerisi + öneri denetimi | A03 | K03 | H3–H4 | — | — | — | — | B/Y | — |
| A04 | 5 kör jüri + betikle seçim | A04 | K03 | H5–H6 | — | — | — | — | B/Y | — |
| A05 | Yapı, senaryo, oyuncu/diyalog, hikâye makine denetimi | A05 | K04 | H7–H10 | — | — | (TH çizelgesi) | — | B/Y | — |
| A06 | Kâğıt seyirci (aşamalı), ilk 2 dk, **hikâye kilidi** | A06 | K05 | H11–H13 | — | — | — | — | B/Y | — |
| A06s | Ses profilleri (A07 ile paralel) | — | — | — | — | SA1 | — | — | B/Y | — |
| A07a | Yönetmen brifingi + parti haritaları (sözleşme, kroki, kurulum) | A07a | K06 | — | Y0–Y2 | — | — | — | B/Y | — |
| A07b | Sahne grubu planları (paralel ≤ 5) | A07b | K06 | — | Y3 | — | — | — | B/Y | — |
| A07c | Birleştirme, dünya defteri (K0), Z0, T0 çizelgesi, **B1 ön bütçe** | A07c | K07, K12 | — | Y4 | — | KR0 | A5 | B/Y | — |
| A07d | Kâğıt plan denetimi (eleştirmen ∥ üretilebilirlik ∥ süreklilik) | A07d | K10 | — | Y5 | — | — | A5 hakem | B/Y | — |
| A07e | Plan seyircisi | A07d | K11 | — | Y6 | — | — | — | B/Y | — |
| A08 | Ses kâğıtta: tasarım, müzik planı, S0 | A08 | K08 | — | — | SA2–SA4 | — | — | B/Y | — |
| A09 | İstem derleme, istem denetimi, kamera ağacı, kart tarifleri | A09 | K09 | — | Y7–Y8 | — | — | A2, A6 | B/Y | — |
| **—** | **KÂĞIT SONU:** bulutta `esitle --gonder`, çıkış 4 ORTAM | | | | | | | | | |
| A10a | Yerel kurulum ölçümü (ortamlar, modeller, fiyat ölçümü) | — | H0 | — | — | SB0 | — | (kurulum) | Y | — |
| A10b | Telaffuz testi (kartlardan önce) | — | — | — | — | SB1 | — | — | Y | AI84 |
| A10c | Ses seçimi, motor kıyası (seri başında), efekt temini | — | V04 | — | — | SB2–SB4 | — | — | Y | AI84 |
| A10d | Evren bağlama, kart adayları, kart kapısı, seçim, kilit | A10 | V01–V03 | — | (kart seçimi) | — | — | A1, A3, A4 | Y | — |
| A11 | Başlangıç görselleri (ağaç sırası, 2 aday), G1, CORRECTION, K1-ön | A11 | V05–V06 | — | Y8 | — | — | A7–A10 | Y | (Flow görsel 0 kredi) |
| A12 | Animatik: ses, T1, render, seyirci, düzeltme + kesme turu, P1 ön turu | A12 | V07–V08 | (H15 dönüşü) | (Y9-a) | SB5 | KR1–KR4, KR3a | — | Y | AI84 |
| A13 | **B2 kesin bütçe**, üretim önizlemesi, hat denetçisi | A13 | V09 | — | — | — | — | — | Y | — |
| A14a | **Pilot dalga** (ilk filmde; 20–30 gerçek P1 planı) | — | (yeni) | — | (YN1 R1) | (SB3 doğrulama) | (KU1 Q4) | (R1 kalibrasyon) | Y | Flow |
| A14 | Video blokları: uygunluk kuyruğu, V1 + metin kapısı her indirmede; blok arasında V2/V3, zincir karesi | A14 | U01–U05 | — | (Y9-c) | SC1 | KR5 | A11–A15 | Y | Flow |
| A15 | Ses: dönüşüm / TTS / ses merdiveni | A15 | M02 | — | — | SD1 | — | — | Y | (AI84) |
| A16 | Kurgu: T2, ses katmanları (S3–S7), Z3, kurgu seyircisi, düzeltme/kesme/yeniden çekim, P1 ön turu, CapCut taslağı | A16 | M01–M06 | (H15) | (Y9-d) | SE1–SE6 | KR6–KR10, KR8a | A16 | Y | (Flow, kuyruktan) |
| A16n | Kullanıcı notu ya da CapCut düzenlemesi (isteğe bağlı döngü) | film-not | NOTLARI_OKU | — | — | SE6 | KR11 | — | Y | — |
| A17 | Yayın: teslim, yayın sesi (S8), final kalite, jenerik, kapak, YouTube paketi, 3 Short, altyazı; yükleme onaylı | A17 | M07, Y01–Y06 | (başlık seçimi) | — | SF1 | KR12 | — | Y | — |
| A18 | Kapanış: ders derleme, evren güncellemesi, film sonu raporu, arşiv | A18 | S01–S04 | H14 | Y10 | SF2 | — | A17 | B/Y (arşiv Y) | — |

**Sıranın dört sabit kuralı** (kod zorlar, belge değil):
1. Kredi harcayan hiçbir aşama, bütün kâğıt ve varlık kapıları **aynı girdi imzasıyla** `GEC` olmadan başlamaz (A14'ün girdi imzası A06, A07c–e,
   A08, A09, A11, A12 raporlarının imzalarını içerir). Bu, B1'deki "animatik onayı olmadan video" hatasının kod karşılığıdır [kaynak: H/proje-b2, BK §8 #16].
2. Telaffuz testi (A10b) kartlardan (A10d) önce koşar: ad değişirse kimlik dizeleri ve istemler bayatlar ([SM2] İ-10).
3. Ses kadrosu (A10c) animatikten önce biter: animatik sesi taslak değil son sestir ([KU2] İ-4, [SM2] İ-2).
4. A14a pilotu ilk filmde atlanamaz. Sonraki filmlerde yalnız seri, sağlayıcı, model ya da istem biçimi değişince koşar.

### 2.2 Ad ve dosya kararları

| Konu | Öneriler | Karar | Gerekçe |
|---|---|---|---|
| Ajan devri | [GS] çıkış 2 + `_AJAN_ISLERI/` · [KU1] çıkış 4 · [SN1] `GOREV_<asama>.md` · [CM] görev defteri | **[CM] görev defteri** `_GOREV/<id>/` + `film.py sonraki/basla/bitir/kurtar` | İ-1; [KU2], [SN2], [YN2] kabul etti |
| Çıkış kodları | 2/3/4 karışık | **0–8 tablosu** (§4.2.0) | İ-1 |
| Rapor klasörü | `_RAPOR/` (kod, [KU2], [SN2], [SM2]) · `RAPORLAR/` ([CM], ZN) | **`_RAPOR/`** | Çoğunluk + mevcut kod; ZN §6.2 metni düzeltilir |
| Kuyruklar | `KUYRUK/` ([UM1]) · `_RAPOR/YENIDEN_URET.json` ([GS]) · film kökü ([CM]) | **`KUYRUK/YENIDEN_URET.json`**, **`KUYRUK/YENIDEN_YAZ.json`** | Rapor ile iş ayrılır; [KU2] kabul etti |
| Seri kütüphanesi | `KUTUPHANE/` ([UM1]) · `EVREN/` (5 uzman) | **`EVREN/<SERI>/`**; kök `YOLLAR.json → evren_kok` | Çoğunluk; benim adımı geri çekiyorum |
| Dünya defteri | `dunya_defteri.py` · `durum_defteri.py` · `sureklilik_defteri.py` · `DUNYA_DURUMU.json` | **`dunya_defteri.py` → `DUNYA_DEFTERI.json`**, sahibi süreklilik; durum çözüm kuralları yönetmenin | [YN2] Ç-5 |
| Plan `parti` | 20'lik blok ([YN1]) · hikâye partisi (çoğunluk) | **`parti` = hikâye partisi (1–3)**; **`uretim.uretim_blogu`** = 20'lik gönderim bloğu, betik hesaplar; `gemini_paketi` = 30; `izleme_parcasi` = 240–300 sn | BK §8 #14; [YN2] Ç-8 kabul etti. Memmet `parti`'yi artık okumaz (§4.6) |
| Zincir yöntemi | `bitis_karesi`/`son_kare` ([UM1]) · Z0/Z1/Z2 ([GS], [YN2]) | Niyet `zanaat.zincir` (yönetmen). Yürütme `uretim.zincir.yontem ∈ {bagimsiz, son_kare, bitis_sabit}` (`kare_zinciri.py` yazar) | İ-4; ad çakışması kalkar |
| Bütçe | `BUTCE.json` · `maliyet.py` · `kredi.py` | **`kredi.py` → `URETIM_ONIZLEME.json`** (dilimlerle) | İ-10 |
| Kredi ve yük defterleri | — | Film başına **`KREDI_DEFTERI.jsonl`**; hesap başına **`FLOW_YUK.jsonl`**, **`FLOW_TEMPO.json`**, **`HESAP_DURUMU.json`** (veri kökünde) | İ-2 |
| Eşik dosyaları | `ritim_esikleri` · `hat_esikleri` · `sureklilik_esikleri` · `hikaye_esikleri` · `ses_esikleri` | Hepsi kalır; **ortak yükleyici `esikler.py`** ([SN2]) aynı anahtarı iki dosyada görürse HATA verir. Öğrenilen kurallar `KURALLAR_OGRENILEN.json` ile korkuluk içinde ezilir | Tek değer, tek yer |
| Ders defteri | beş biçim | **Olay başına dosya** `BILGI/DERSLER/ham/`; kategori = `veri/kok_neden.json` | İ-7 |
| Karar defteri | `KARAR_DEFTERI.md` ([CM]) | Kayıtlar olay başına `kararlar/<zaman>.json`; `KARAR_DEFTERI.md` betikle türetilir | İ-7 ile aynı gerekçe (iki makine) |
| Sağlayıcı türleri | mevcut `(gorsel, video, ses, muzik)` · [UM1] 8 tür · [SM2] + `ayristirma`, `asr`, `dinleyici` · [GS] `gozlemci` | `llm, gozlemci, gorsel, video, tts, ses_donustur, ayristirma, asr, dudak, muzik, dinleyici`. `ses` bir sürüm boyunca `tts`'nin eski adıdır; `vlm` adımı [GS]'nin `gozlemci`'siyle değiştiriyorum | §4.5.8 |
| Ders terfi ajanı | `ders-katibi` ([UM1]) · `ders-editoru` ([CM]) | **`ders-editoru`** | [CM] adı; [YN2] Y10 aynı adı kullanıyor |
| Ayar dosyaları | `FILM_AYAR.json` + `ses_butce` ([SM1]) · `butce.json` ([CM]) | **Tek `FILM_AYAR.json`**, `butce` altında hepsi (`ai84_kredi_tavan_film`, `ai84_seri_kurulum_tavan` [SM2] dahil); yollar **`YOLLAR.json`** | §4.5.12 |
| Görev defteri git'e girer mi | — | **Girmez.** `_GOREV/`, `FILM_DURUM.json`, `FILM.kilit` makineye özeldir. Karşı taraf durumu zarflardan yeniden kurar (`film.py kurtar --yeniden-kur`) | Durum çıktılardan türetilir (§4.2.1) |

### 2.3 Kapı ad alanı (rapor dosya adları çakışmasın)
Bütün raporlar `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json` adını taşır. Kapsam `P1..P3` (parti), `B07` (blok), `D1` (dalga) ya da `FILM`'dir.

| Ad | Kapı | Sahibi | Not |
|---|---|---|---|
| `Z0`–`Z3` | ZN §6.2 zanaat kapıları | ZN; araçlar yönetmen/kurgu | "Z1" yalnız bu anlamda |
| `K0`, `K1ON`, `K1` | kâğıt süreklilik, video öncesi geçiş, kurgu geçişi | süreklilik | `K1-ön` dosya adında `K1ON` |
| `KART`, `G1`, `V1`, `V2`, `V3`, `ZK` | kart kapısı, başlangıç karesi, teknik video, klip içi, bitiş durumu, zincir karesi (G1-zincir) | süreklilik | `ZK` yeni ad (eski "G1-zincir") |
| `S0`–`S8` | ses kapıları | ses | [SM2] adları aynen |
| `HS_KAGIT`, `HS_PLAN`, `HS_ILK2DK`, `HS_ANIMATIK`, `HS_KURGU` | habersiz seyirci kapıları | hikâye / kurgu | **[UM1]'deki `S1a/S1b/S2/S3` adlarımı geri çekiyorum**: ses kapılarıyla çakışıyordu |
| `ISTEM`, `SEMA`, `PLAN`, `KROKI` | istem denetimi, şema, plan dili (Y kuralları), kroki | yönetmen / görüntü | Y01–Y59 madde kodudur, kapı adı değil |
| `B0`, `B1`, `B2`, `BK` | bütçe noktaları, kuyruk mini kapısı | üretim | §2.5 |
| `HAT` | hat denetçisi | üretim | §4.3.3 |
| `PILOT` | pilot dalga raporu | üretim | §4.2.4 |

### 2.4 Sorumluluk sınırları (benim alanım ve komşuları)

| Konu | Tek sahibi | Benim yaptığım | Ötekinin yaptığı |
|---|---|---|---|
| Aşama sırası, durum, imza, kilit, DUR, ortam, çıkış kodu | üretim (`film.py`, `ortak.py`) | hepsi | — |
| Görev defteri, kancalar, beceri metinleri | Claude Code mimarisi | görev türlerini ve geçme şartlarını aşama kaydından üretirim | `GOREV.json` biçimi, `erisim_kapisi`, `ajan_bitti`, `soru_kapisi`, SKILL.md |
| Sağlayıcı arayüzü, kısıt kodları, Memmet, `memmet_topla`, Flow tempo ve yük | üretim | hepsi | Görüntü uzmanı Memmet'e sha denetimi ve `NNN_son.jpg` ister; kabul (§4.6) |
| Fiyat, bakiye, bütçe noktaları, dilimler | üretim (`kredi.py`) | hesap ve kapı | `kuyruk.py` (kurgu) her kredili maddeyi bana sorar |
| Yeniden üretim kuyruğu, öncelik, 0 kredi kuralı | kurgu (`kuyruk.py`) | şema, `is_kimligi`, çift harcama denetimi | öncelik formülü, `sifir_kredi` kuralı |
| Video blok planı (uygunluk kuyruğu) | üretim (`blok_plani.py`) | hangi plan hangi blokta | Zincir karesini `kare_zinciri.py` (görüntü) çıkarır; çıkış noktasını `kirp_oner.py` (kurgu) önerir ve kilitler |
| Pilot dalga seçimi ve raporu | üretim | seçim, rapor çatısı | Her uzman kendi ölçüsünü rapora yazar |
| Yerel ağır iş kuyruğu, GPU kilidi | üretim (`yerel_is.py`) | sıra ve kilit | Ölçüm arka uçları görüntü ve ses uzmanlarında |
| Ders defteri çatısı | üretim (`ders_defteri.py`) | `kaydet()`, derleme, korkuluklu uygulama | Kategori satırları her uzmandan; terfi kararı `ders-editoru` |
| Bulut ↔ yerel taşıma | üretim (`film.py esitle`) | beyaz liste, çakışma kuralı | — |
| Bildirimler | üretim (`bildirim.py`) | Telegram, tekrar engeli, maskeleme | Mesaj metinlerini her aşamanın kaydı verir |

### 2.5 Bütçe noktaları
| Nokta | Ne zaman | Girdi | Karar | Geçmezse |
|---|---|---|---|---|
| **B0** | A01 (yazımdan önce) | Bakiye (`HESAP_DURUMU.json`, son Memmet okuması) ya da yok; tavanlar | [1800, 2700] sn içinde bütçeye sığan en uzun süre hikâyenin **üst sınırı** olur [kaynak: SN2 §2.5]. Formül: kredi ≈ 0,169 × süre_sn × 12 × 1,30 [hesap: 405 klip / 2400 sn; RE `kredi_klip_720p`; kapı payı] | Bakiye bilinmiyorsa (bulut) hedef 2400 sn, varsayım deftere yazılır. 30 dk bile sığmıyorsa hikâye 30 dk yazılır ve kullanıcıya **bilgi** verilir |
| **B1** | A07c (plan sayısı kesinleşince) | Klip sayısı, model, birim fiyat, pay ve dilimler | Tahmin ≤ tavan | **5 BÜTÇE** ile durur. Film **kısaltılmaz** (kilitten sonra) [kaynak: KU1 D1, SN2 §2.5] |
| **B2** | A13 (video öncesi) | Bütün kapı raporları, bakiye (Flow menüsünden salt okuma), AI84 bakiyesi, `usd` | Tahmin ≤ bakiye × 0,9 [tahmin] ve ≤ tavan; hat denetçisi `GIT` | 5 BÜTÇE ya da 6 KAPI |
| **BK** | Her kredili kuyruk maddesinden önce | Dilim kalanı, madde maliyeti, zincir etkisi | `kuyruk.py` sorar, `kredi.py` cevaplar | Madde 0 kredi çözümüne düşer; KRİTİK ise 5 BÜTÇE |

### 2.6 Alt araç çıkış kodlarının eşlenmesi
| Alt araç kodu | Anlamı (alt araçta) | `film.py` ne yapar | Dış kod |
|---|---|---|---|
| 0 | geçti | Zarfı yazar, aşamayı `tamam` sayar | sıradaki işe göre |
| 1 | program hatası | İz `FILM_KAYIT.txt`'ye, ders kaydı `arac_hatasi` | 1 |
| 2 | girdi eksik / durdu | Eksik girdi kullanıcınınsa (ZIP gelmedi) | 2 |
|  |  | Eksik girdi bir önceki aşamanınsa (bayat) | o aşamaya döner |
| 3 | eşik altı (`puan_oku`, `hikaye_odasi`) | Tur sayacı +1; tur < tavan ise yazar görevini yeniden kuyruğa koyar | 3 |
|  |  | Tur = tavan ise | 6 |
| Memmet `_memmet_cikis.json → kod` | `olagandisi` · `dogrulama` · `kredi_bitti` · `arayuz` · `dur` | Kısıt tablosu §4.5.8 | 7 · 2 · 5 · 3 (`memmet-bakimci`) · 2 |

### 2.7 Bulut ↔ yerel iş bölümü (uzlaşılan)
| İş | Bulut | Yerel |
|---|---|---|
| A00–A09 kâğıt aşamaları, bütün ajanlar, deterministik kapılar, B0 (bakiyesiz) ve B1 | evet | evet |
| Kod geliştirme ve testler (`sahte`, `kaset`) | evet | evet |
| A10–A18: AI84, Flow, Gemini paketleri, görsel ve video ölçümleri, animatik, kurgu, CapCut, Telegram | hayır (çıkış 4) | evet |
| Taşıma | `film.py esitle --gonder` (commit + push, beyaz liste) | `GUNCELLE.bat` = `git pull --ff-only` + `film.py esitle --al` |

---

## 3. Diğerlerinden kabul edip kendi önerime kattıklarım

| Kaynak | Kabul ettiğim | Revize önerimdeki yeri |
|---|---|---|
| [CM] §2.0, §5.2–5.4 | Görev defteri: `_GOREV/<id>/{GOREV.json, ISTEM.md, GIRDI/, CIKTI/}`, `sonraki/basla/bitir/kurtar`, paralel grup, `tasima`, betiğin şablondan doldurduğu istem | §4.2.0, §4.5.2 |
| [CM] §2.3 | Değerlendiricinin yarım işi sıfırdan, yazarınki devam ettirilir; kredili işte gönderim kaydı gönderimden **önce** yazılır; kör yeniden gönderim yasak | §4.2.1 |
| [CM] K-3…K-10 | Kancalar: `erisim_kapisi`, `komut_kapisi`, `oturum_basi`, `ajan_bitti` (SubagentStop doğrulaması ≤ 2), `ajan_sonrasi`, `soru_kapisi`, `devam_kapisi`, `hata_kaydi` (StopFailure), `model_degisti` | §4.4.3 (benim eklerim: iki kök, Flow kilidi, tempo, esitle) |
| [CM] K-1 | `.claude/bin/film.py` sarmalayıcısı: aynı komut metni iki düzende çalışır | §4.6.2 |
| [CM] K-9 | `devam_kapisi`: çalıştırılabilir görev varken durma engellenir (8 ardışık tavanı). **Tur 1'deki "tur başına en çok 6 aşama" kuralımı geri çekiyorum**: bağlamı kanca, sıkıştırma ve ≤ 5 satırlık ajan dönüşü korur | §4.4.2 |
| [CM] §3.1 | Ajanlarda Bash yok; `memory:` yok; `fallbackModel` yok; kör rollerde `omitClaudeMd`; ajan dönüşü ≤ 5 satır. `memmet-bakimci` de Bash'siz: testleri SubagentStop kancası koşar | §4.3 |
| [CM] `UYARI_GECTI.bat`, Flow kilidi | Kilidi yalnız kullanıcı kaldırır; BK §6.2 #8–#9 şartlarıyla (İ-8) | §4.5.8 |
| [CM] R-5, §9.4 | `claude --version` ≥ 2.1.271 kurulumda denetlenir; Windows'ta kanca komutu ve `!` komutunun `python` bulması bir kez sınanır | §4.6.4 |
| [GS] A12, §4.1 kural 1 | Videoya giden her başlangıç karesinin G1 kaydı ve sha1'i eşleşmeli; elle konmuş kare de kapıdan geçer. `is_kimligi` bu sha'yı içerir; Memmet yüklemeden önce sha'yı yeniden doğrular | §4.5.7, §4.6.1 S2 |
| [GS] §7 başı | **"ÖLÇÜLEMEDİ asla GEÇ değildir"** bütün kapıların ortak kuralı olur (eksik model, yüz çok küçük, süreç düştü) | §4.7.3 |
| [GS] §8.7 | Kural denemesi: yeni kural uygun planların yarısına uygulanır, hata oranı karşılaştırılır | §4.5.11 `deneme` durumu |
| [GS] R1 | Kalibrasyon partisi fikri. Ayrı 240 kredilik deneme yerine **pilot dalga** olarak (gerçek P1 planları) | §4.2.4 |
| [GS] A15 | Zincir karesi G1-zincirden (yeni adı `ZK`) geçemezse plan planlanmış görsele düşer, ders kaydı yazılır | §4.2.4 |
| [YN2] İ-1 | Durum yalnız **olgudur**. Tur 1'deki `DUNYA_DEFTERI` örneğimde `kadraj` alanı vardı; kaldırıldı | §4.5.10 |
| [YN2] İ-2 | Z1 varsayılanı; her plana planlanmış görsel | §4.2.4 |
| [YN2] İ-4 | Yönetmen işi parti başına tek çağrı değil: harita görevi + sahne grubu başına plan görevi | §2.1 A07a–b |
| [YN2] İ-11 | **Durum dondurma** (`uretim.durum_dondu`): görsel üretildiği anda çözülmüş durum özeti `plan_imza`'ya girer; sonradan değişirse görsel `bayat` olur | §4.5.7 |
| [YN2] İ-13 | Eller `eller: {sag: {tutar, yer, sekil}, sol: {…}}`; açık parmak sayısı `sekil`'den türer. Tur 1'deki `govde: {el, parmak, acik}` önerimi geri çekiyorum | §4.8.2 |
| [YN2] Ç-6 | Zincir niyeti `zanaat.zincir` (yönetmen), yürütme `uretim.zincir` (`kare_zinciri.py`) | §4.5.7 |
| [YN1] R1 | İstem biçimi (`aralik` "0.5-3s:" / `sira` "First… then…") ilk partide ölçülür → pilot dalgada | §4.2.4 |
| [KU2] İ-2 | **Teslim biçimi KR'deki gibi:** CapCut taslağı verilir, dışa aktarmayı kullanıcı yapar. Tur 1'deki "`FINAL/film.mp4` ffmpeg ana kaydı" önerimi geri çekiyorum. ffmpeg çıktısı ölçüm ve yedektir; `yayin_kaynagi: master` yalnız kurulum ayarıyla | §4.2.5 |
| [KU2] İ-3, §2.5 | Kapı payı 0,30 içinde dilimler 0,15 / 0,07 / 0,08; 0 kredi kuralını `kuyruk.py` zorlar; plan başına toplam yeniden çekim ≤ 2 | §4.5.9, §4.7.1 |
| [KU2] İ-4, [SM2] İ-2 | Animatik sesi **son sestir** (seçilmiş sesle TTS, önbellekli); render süresi = T1 toplamı ±1 kare. Tur 1'deki "taslak TTS" ve "±%5" ifadelerimi geri çekiyorum | §4.2.3 A12 |
| [KU2] KR3a, KR8a | P1 ön turları (kapı değil) | §4.2.3–4.2.4 |
| [SN2] İ2 | Plan seyircisine `ekranda_bilgi` verilmez. Tur 1'deki K11 girdi tanımımı düzeltiyorum | §2.1 A07e |
| [SN2] İ4 | Hikâye odası 4 mimar + 5 kör jüri + betikle seçim; çağrı bütçesi 40–75 | §4.3.4 |
| [SN2] İ12 | Ana Claude brifing yazmaz | §4.2.2 A02 |
| [SN2] §2.5 | Süre yazımdan önce bütçeye göre seçilir (B0); yazılmış film kısaltılmaz | §2.5 |
| [SN2] §2.6, İ10 | Hikâye kapısı tükenirse bayraklı devam yok: merdiven, sonra **6 KAPI** | §4.2.2 A06 |
| [SN2] `esikler.py` | Ortak eşik yükleyicisi; aynı anahtar iki dosyada → HATA | §4.7 |
| [SM2] İ-4 | Ses karar ağacı yerine **ses merdiveni** (`ses_karar.py`). Dudak sağlayıcısı `musetalk` **yerel** (4 GB'ta denenmiş [kaynak: SM2 D-MT]); `fal_latentsync` çıkarıldı | §4.5.8 |
| [SM2] İ-6 | `butce.ai84_seri_kurulum_tavan: 40000` ayrı; müzikte `gemini_elle` yok (`["acestep", "midi_ornek", "sahte"]`); AI84 birim fiyatı ücretsiz `ai84.estimate()` ile ölçülür | §4.5.12, §4.7.1 |
| [SM2] Ç-15 | Sağlayıcı türlerine `ayristirma`, `asr`, `dinleyici` | §4.5.8 |
| [SM2] SC1 | Metin kapısı her indirmede (kurguda değil); ses kaynaklı yeniden çekim aynı gecenin sonraki bloğuna girer | §4.2.4 |
| [SM2] SB0 | Eksik ortam yalnız kendi basamağını kapatır; sessizce "geçti" sayılmaz | §4.2.3 A10a |

**Geri çektiklerim (tur 1'den):** `bitis_karesi` varsayılanı · `KUTUPHANE/` adı · `S1a/S1b/S2/S3` seyirci kapı adları · `vlm` sağlayıcı türü
adı · `ders-katibi` adı · K11'de `ekranda_bilgi` · hikâye odasında 3 mimar ve "hakem senarist" · `FINAL/film.mp4` ana kaydı · animatikte
"taslak TTS" ve "±%5" · "tur başına en çok 6 aşama" · `govde.{el, parmak, acik}` · `DUNYA_DEFTERI` örneğindeki `kadraj` alanı · `dudak: fal_latentsync` ·
`muzik: gemini_elle` · ajan çağrısı tahmini 90–190 · "uyarı günü yeniden başlatma yok" (yerine İ-8'deki şartlı kural).

---

## 4. REVİZE NİHAİ ÖNERİM

Bu bölüm tur 1 dosyamın yerine geçer ve tek başına okunabilir. Tur 1'den farklı yerler **(değişti)** ya da **(yeni)** diye işaretlidir.

### 4.1 Alanımın hedefi ve başarı ölçütü (sayılarla)

#### 4.1.1 Hedef
Konu cümlesinden YouTube paketine giden hattı **tek bir durum makinesi** olarak kurmak:
1. Her aşamanın girdisi, çıktısı, geçme şartı, ortamı ve kredi türü **kodda tek bir aşama kaydında** tanımlıdır. Belgeler (`hat/ASAMALAR.md`)
   bu kayıttan üretilir, elle yazılmaz.
2. Kâğıt kapıları önce çalışır. Kredi harcayan iş, bütün kapıların **aynı girdi imzasıyla** geçtiği kanıtlanmadan başlayamaz.
3. Kesilen iş (elektrik, Ctrl+C, bağlam sıkıştırması, kullanım sınırı, Flow uyarısı) kaldığı yerden sürer. Yapılan iş tekrarlanmaz, kredi iki kez harcanmaz.
4. Sağlayıcı kısıtlanınca hat **durur**. Kısıtı atlatmaya hiçbir zaman çalışmaz. Yedeğe geçiş yalnız izinliyse, eşit ya da daha iyi kaliteyle
   ve sahne grubu sınırında olur.
5. **(değişti)** İş birimi [CM]'nin görevidir. Yargı gerektiren iş ajandadır; ölçülebilen her iş betiktedir; sırayı `film.py` verir; dağıtımı ana Claude yapar.
6. Her hata, red, yeniden çekim, kullanıcı notu ve seyirci bulgusu ders defterine otomatik yazılır. Defter sonraki çalıştırmada doğrulayıcıları
   **yalnız korkuluklar içinde** sıkılaştırır.
7. **(yeni)** Flow hesabının yükü filmden bağımsız, hesap düzeyinde sayılır. Hiçbir yol (yeniden başlatma, yeni film, yeniden çekim) tempoyu hızlandıramaz.

#### 4.1.2 Başarı ölçütleri
| # | Ölçüt | Hedef | Nasıl ölçülür |
|---|---|---|---|
| M1 | Kullanıcıya sorulan karar sorusu | **1** (konu); konu ilk mesajdaysa 0 | `input()` yalnız `yeni --konu` yolunda (T17, AST taraması); [CM] `soru_kapisi` sayacı |
| M2 | Kullanıcının el işi **(değişti)** | Yalnız kodda sabit listedeki türler (aşağıda) | `kim: kullanici` görevleri bu listenin dışına çıkamaz (T16). Sayılar film sonu raporunda |
| M3 | Kapısız kredi harcaması | **0** | Kredili görevin girdi imzası kapı raporlarının imzalarını içerir; uyuşmazsa sağlayıcı çağrılmaz (T4) |
| M4 | Çift harcama (aynı işin iki kez gönderilmesi) | **0** (planlı yeniden çekim hariç) | `KREDI_DEFTERI.jsonl`'da aynı `is_kimligi` için ikinci `gonderildi` yok (T3) |
| M5 | Kesintiden sonra devam **(değişti)** | 30 rastgele kesme noktasında %100 tamamlanma; biten görevin yeniden çalışması 0 [kaynak: CM M3] | T2, T19 |
| M6 | Kredi tahmini doğruluğu | İlk filmde gerçek/tahmin ∈ [0,90; 1,15]; sonra [0,95; 1,10] [tahmin] | Film sonu raporu |
| M7 | Yeniden çekim oranı | Hedef ≤ %20 [kaynak: RE `kredi_yeniden_deneme_payi`]; kapı payı %30, dilimlerle (§4.7.1). B2'de ≈ %37 idi [hesap: 50+ / 134; kaynak: 04_KIM_NE_YAPTI, H/proje-b2] | `KREDI_DEFTERI` |
| M8 | Flow uyarısından sonra yeni gönderim | **0**; uyarı görüldükten sonra en geç bir kontrol döngüsünde (≤ 10 sn) durulur | HTML fikstürüyle Memmet testi (T10) |
| M9 | Uçtan uca sahte test | `ORNEK_3_SAHNE_TAM` ≤ 5 dk; takım ≤ 10 dk; **Windows + Python 3.10'da yeşil** | CI |
| M10 | Ders defterine otomatik kayıt | Listelenen olay türlerinin %100'ü | T12 |
| M11 | Bulutta kredili sağlayıcı çağrısı | **0** | Ortam algılama (T9) |
| M12 | Her klibin künyesi | %100 | `KUNYE/NNN.json` sayısı = video sayısı |
| M13 | Gizli bilgi sızıntısı (log, Telegram, commit, ajan bağlamı) | **0** | Anahtar deseni taraması; `esitle` ve `paketle.py` tarar (T11, T25) |
| M14 | **(yeni)** Flow günlük görsel tavanı, görsel→video beklemesi ya da kalan molanın yeniden başlatmayla kısalması | **0** ihlal | `FLOW_YUK.jsonl` + `FLOW_TEMPO.json` (T21, T22) |
| M15 | **(yeni)** Yerel kuyruğun sebep olduğu GPU bellek hatası | **0** | `yerel_is.py` kaydı (T26) |
| M16 | **(yeni)** Bulut ↔ yerel taşımada sessiz üzerine yazma ya da kayıp | **0** | `esitle` çakışma raporu (T24) |
| M17 | **(yeni)** İlk filmde pilot raporu ve ondan çıkan kararların deftere yazılması | %100 | `_RAPOR/PILOT_FILM.json`, `kararlar/` |

**M2'nin sabit listesi (değişti).** Film sırasında kullanıcının yapacağı işler yalnız şunlardır:
1. Google girişi ve reCAPTCHA çözümü (Claude çözmez) [kaynak: BK §6.2 #3].
2. Gemini paketlerini taşımak: ≈ 18–24 paket [tahmin; kart paketleri + kamera ağacı basamakları, İ-11].
3. Video oturumunu başlatmak (`VIDEO_*.bat`). `elle` modda GÖNDER'e basmak: ≈ 527 kez [hesap: 405 × 1,3].
4. CapCut'tan dışa aktarmak [kaynak: KR, BK §8 #18].
5. YouTube yükleme onayı (isteğe bağlı).

Yalnız kısıt ya da bütçe durumunda: Flow'da elle 1 video denemesi ve `UYARI_GECTI.bat` (İ-8); kredi yükleme.
Kurulumda bir kez: `KURULUM.bat`, Python 3.12 kurulumu (ses ortamları için), git (yalnız bulut modu), Telegram anahtarı, kurulum ayarları (§4.5.12).

#### 4.1.3 Ölçek, maliyet ve takvim (40 dk film)
| Kalem | Değer | Etiket |
|---|---|---|
| Plan / klip | ≈ 495 / ≈ 405 | [kaynak: ZN §2.6; RE `klip_bolme_oran_hedef` 0,18] |
| Flow video kredisi | 405 × 12 = 4.860 taban; kapı payı 0,30 ile **6.318** | [hesap; RE `kredi_klip_720p`] |
| Pay dilimleri | görüntü/süreklilik/plan dili ≈ 729 · ses ≈ 340 · kurgu ≈ 389 | [hesap; oranlar KU2, tahmin] |
| Hesap kapasitesi | Ultra 10.000 kredi + günde 50 bedava | [kaynak: BK §6.4] |
| Flow video süresi | ≈ 527 gönderim, ≈ **12,9 saat** (gece temposu; 2 gece) | [hesap: tur 1 §1.3; tempo BK §6.2 #6; video süresi FK, 720p'de doğrulanmadı] |
| Flow görsel düzeltme | ≈ 116 gönderim → ≈ **6 görsel günü** (tavan 20/gün) | [hesap, İ-2; tavan tahmin] |
| AI84 | Film başına ≈ 20–30 bin; seri başında ses bankası (yalnız RVC kazanırsa) ≤ 4 × ≈ 9 bin | [kaynak: SM2 hesapları, tahmin] |
| Ajan çağrısı | ≈ **350–550** (Opus, high) | [tahmin, §4.3.4] |

| Evre | Takvim | Darboğaz |
|---|---|---|
| Kâğıt (A00–A09) | 1–3 gün | Claude kullanım sınırı |
| Yerel hazırlık ve kartlar (A10) | 1–2 gün | Kullanıcının paket taşıması, kart G1 turları |
| Başlangıç görselleri ve G1 (A11) | 4–7 gün | Gemini paket turları + Flow görsel tavanı |
| Animatik (A12) | 1–2 gün | Seyirci turları, render |
| Pilot + video (A14a–A14) | 3–4 gün | Görsel→video beklemesi, 2 gece Flow, pilot kalibrasyonu |
| Ses, kurgu, yayın (A15–A17) | 2–4 gün | Yerel GPU kuyruğu, kurgu seyirci turları |
| **Toplam** | **≈ 2–3 hafta** [tahmin] | İlk filmden sonra ders defteriyle ölçülür |

Bu takvim kullanıcıya kurulumda **dürüstçe** söylenir. Hızlandırmanın yolları dolarla açılır ve kurulum ayarıdır, film başına soru değildir:
`vertex_gorsel` (düzeltme görselleri), `veo_vertex` (video; fiyat bilinmiyor), `claude_api` başsız yürütme.

### 4.2 Aşama aşama süreç: girdi → iş → çıktı → geçme şartı → kim

#### 4.2.0 Mimari ve dış protokol (değişti)
```
Kullanıcı ──(yalnız konu)──► ana Claude (set amiri, film-yap becerisi)
                                │ 1) python .claude/bin/film.py sonraki        → görev listesi + çıkış kodu
                                │ 2) python .claude/bin/film.py basla <id,…>
                                │ 3) tür = ajan    → Agent(<ajan>, "Görevin: …/GOREV.json")  (paralel grup tek mesajda)
                                │    tür = betik   → python .claude/bin/film.py calis <id>  (film.py betiği ve sağlayıcıyı kendisi çağırır)
                                │    tür = kullanici / bekle / kisit / ortam / butce → tek cümle, tur biter
                                │ 4) SubagentStop kancası çıktıyı doğrular → film.py bitir <id>   (en çok 2 düzeltme)
                                └ 5) PostToolUse kancası "sıradaki: …" ekler → 1'e dön
```
- **`film.py`** = aşama kaydı + görev üretici + deterministik kapılar + sağlayıcı çağrıları. Claude API'yi varsayılan olarak çağırmaz.
- **Ana Claude** içerik üretmez, puan vermez, plan dosyası yazmaz ([CM] §3.1).
- **Başsız yürütme (isteğe bağlı):** `film.py yurut --basliksiz` aynı görevleri `saglayicilar/claude_api.py` ile yürütür (İ-6).

**Dış çıkış kodları** (`film.py sonraki` ve `film.py calis` ikisi de döner; `.bat` ve Telegram buna göre konuşur):

| Kod | Ad | Anlamı | Ana Claude ne yapar | Telegram |
|---|---|---|---|---|
| 0 | BİTTİ | İstenen aşamalar tamam | Film sonu özetini iletir | BİLGİ |
| 1 | HATA | Program hatası (`FILM_KAYIT.txt`) | Kayıttaki nedeni sade Türkçe söyler; `film-gelistir` gerekiyorsa bunu söyler | ACİL |
| 2 | KULLANICI | Kullanıcının fiziksel işi (M2 listesi) | Görevdeki tek cümleyi aynen iletir; tur biter | BİLGİ (+ 6 saatte 1 hatırlatma) |
| 3 | AJAN | Ajan işi var | Görevleri dağıtır | — |
| 4 | ORTAM | Bu iş bu ortamda yapılamaz (bulutta Flow gibi) | `esitle --gonder`, "bilgisayarında `GUNCELLE.bat`, sonra `DEVAM.bat`" | — (bulutta Telegram kapalı) |
| 5 | BÜTÇE | Bütçe noktası geçmedi | `URETIM_ONIZLEME.md`'nin 3 satırlık özeti | ACİL |
| 6 | KAPI | Kapı tur tavanını aştı, merdiven tükendi | En iyi sürüm, en düşük 3 ölçüt, öneriler; **soru değil, engel bildirimi** | ACİL |
| 7 | KISIT | Sağlayıcı kısıtlandı, izinli yedek yok | `hat/KISITLAR.md`'deki açıklama ve kalan yollar | ACİL |
| 8 | BEKLE **(yeni)** | Zamana bağlı bekleme (Flow molası, görsel→video, GPU işi) | "En erken şu saatte sürer" der; `.bat` açık kalıyorsa kendisi sürer | yalnız 1 saatten uzunsa BİLGİ |

#### 4.2.1 Durum, devam, kilit
- **Durum çıktılardan türetilir.** Her çıktı bir **zarf** taşır: JSON'da `_uretim`, başka dosyada yanında `<dosya>.imza.json`.
  Zarf: `{asama, gorev, girdi_imza, arac_surum, esik_surum, sonuc, zaman, ortam}`. Bir aşama ancak üç koşulla "tamam"dır: çıktı var,
  zarftaki `girdi_imza` şimdiki girdilerin imzasına eşit, sonuç `GEC`.
- `FILM_DURUM.json` yalnız önbellektir; `_GOREV/` görev defteri ve `FILM.kilit` makineye özeldir ve git'e girmez. Bulutta ya da yerelde
  `film.py kurtar --yeniden-kur` görev defterini zarflardan yeniden kurar. İki ortamın `film.py ozet` çıktısı aynıdır.
- **Kredili çıktılar** girdi değişince asla kendiliğinden geçersiz sayılmaz ve asla silinmez. Plan bazında `bayat` işaretlenir ve
  `KUYRUK/YENIDEN_URET.json`'a girer. Yeniden üretim de bütçe noktasından (BK) geçer. Eski dosya `_ESKI/`'ye taşınır [kaynak: H/is-bitince-d-arsiv].
- **Gönderim kaydı gönderimden önce yazılır.** Kesilmeden sonra önce `memmet_topla.py` çalışır ve Flow projesinde `data-media-id` ile arar;
  **yeni gönderim yapmaz** [kaynak: BK §6.2 #4, §6.3 #2]. Bulunamayan iş `kayip` işaretlenir ve kuyruktan, BK noktasından geçerek
  **bir kez** yeniden gönderilir. Kör yeniden gönderim yoktur ([CM] §2.3).
- **Kilitler:**
  - `FILM.kilit` `{pid, makine, ortam, zaman}`: aynı filmde ikinci bir `film.py`.
  - **(yeni)** `<veri_kok>/FLOW.kilit`: aynı Flow hesabında ikinci bir Memmet (iki film aynı anda Flow'a gidemez).
  - Kilit iki koşuldan biriyle bayattır: süreç yok ya da 30 dk güncellenmedi [tahmin].
  - `FLOW_KILIDI.json` (uyarı kilidi) ayrıdır ve yalnız `UYARI_GECTI.bat` ile kalkar (İ-8).
- **`DUR` dosyası:** `DURDUR.bat` yazar. `film.py` ve Memmet her döngüde bakar; elindeki indirmeyi bitirir, yeni gönderim yapmaz, çıkış 2.
- **Atomik yazım:** her JSON önce `x.tmp`'ye yazılır, sonra `os.replace`. Ekleme kayıtları (`KREDI_DEFTERI.jsonl`, `FLOW_YUK.jsonl`) satır
  başına `fsync` ile yazılır; okuyucu bozuk son satırı atlar ve uyarır.
- **Ortam algılama:** Windows ise `yerel`; diğer her durumda `bulut`, meğer ki `FILM_AYAR.json → ortam: "yerel"`. Bulutta yalnız `sahte`,
  `kaset` ve `claude_code` sağlayıcıları açıktır.

#### 4.2.2 Kâğıt evresi (kredi yok; bulutta da çalışır)
İçerik kuralları sahip uzmanlarındır; burada girdi, çıktı ve hat açısından geçme şartı yazılıdır.

| Kod | Girdi → İş | Çıktı | Geçme şartı | Kim |
|---|---|---|---|---|
| A00 | Makine durumu + kullanıcı mesajı → hazırlık denetimi (disk, kilit, ortam, Python, `claude --version`); konu yoksa **tek soru** | `00_KONU.md`, `FILMLER/_AKTIF.json`, `_RAPOR/HAZIRLIK.json` | Konu boş değil. Disk ve kilit dışındaki eksikler yalnız kendi aşamasını engeller | ana Claude + betik |
| A01 | Konu + evren dizini + kanal kararları + `hikaye` dersleri → konu kartı, proje kararları, **B0** | `_HIKAYE_ODASI/01_KONU_KARTI.json`, `PROJE_KARARLARI.md`, `kararlar/` | Şema; süre ∈ [1800, 2700] ve ≤ B0 üst sınırı | ajan `yapimci` + betik `kredi.py --sure-sec` |
| A02 | Kalıp bölümler + konu yorumu → brifing | `_HIKAYE_ODASI/00_BRIFING.md` (+ sha1) | Bütün A03 görevlerinde aynı sha1 | betik |
| A03 | Brifing + eksen → 3 paralel öneri + bonus, öneri denetimi | `02_oneri_*.md` | [SN2] H4 | ajan `hikaye-mimari` ×4 + betik |
| A04 | Anonim öneriler → 5 kör jüri → medyanla seçim | `03_juri_*.json`, `04_SECIM.json` | [SN2] H6 | ajan `juri-uyesi` ×5 + betik |
| A05 | Seçim → yapı, senaryo, oyuncu ve diyalog denetimi, hikâye makine denetimi | `05_YAPI.json`, `06_SENARYO_vN.json` | HATA 0 ([SN2] H10) | ajan `hikaye-yazari`, `oyuncu`, `diyalog-editoru` + betik |
| A06 | Senaryo → aşamalı kâğıt seyirci + ilk 2 dk + kilit | `_RAPOR/HS_KAGIT_FILM_tN.json`, `HS_ILK2DK_FILM.json`, `HIKAYE.json` | RE `seyirci_*` eşikleri; tur ≤ 4, sonra [SN2] merdiveni; tükenirse **6 KAPI** | ajan `habersiz-seyirci` ×3, `ozet-eslestirici` + betik |
| A06s | `HIKAYE.json` karakterleri → ses profilleri (A07 ile paralel) | `35_SES/SES_PROFILLERI.json` | [SM2] SA1 | ajan `ses-tasarimcisi` (kadro kipi) |
| A07a | `HIKAYE.json` + evren → yönetmen brifingi, 3 parti haritası (paralel) | `30_YONETMEN/HARITA_P*.json`, krokiler | [YN2] Y1–Y2; kroki HATA 0 | betik + ajan `yonetmen` (harita kipi) ×3 |
| A07b | Sahne grubu dilimi → planlar (paralel ≤ 5) | `30_YONETMEN/PLANLAR/S*.json` | SubagentStop'ta `plan_denetim --sahne` HATA 0, ≤ 2 düzeltme | ajan `yonetmen` (plan kipi), sahne başına yeni örnek |
| A07c | Planlar → birleştirme, dünya defteri (K0), Z0, T0, **B1** | `SAHNELER.json`, `DUNYA_DEFTERI.json`, `_RAPOR/K0_FILM.json`, `Z0_P*.json`, `URETIM_ONIZLEME.json` (taslak) | HATA 0; B1 geçer, yoksa **5 BÜTÇE** | betik (`plan_birlestir`, `dunya_defteri`, `plan_denetim`, `zaman_cizelgesi`, `kredi.py`) |
| A07d | Çekim listesi + kör paket → eleştirmen ∥ üretilebilirlik ∥ süreklilik (kâğıt) | `_RAPOR/PLAN_ELESTIRI_P*.json` vb. | KRİTİK 0, ORTA ≤ 3/parti; ≤ 2 tur | ajanlar |
| A07e | Plan kör paketi (**`ekranda_bilgi` yok**) → 3 seyirci | `_RAPOR/HS_PLAN_P*_tN.json` | RE `seyirci_*`; ≤ 2 tur [tahmin] | ajan `habersiz-seyirci` ×3 + eşleştirici + betik |
| A08 | Planlar + defter → ses tasarımı, müzik planı, S0 | `35_SES/SES_S*.json`, `MUZIK/muzik_listesi.json`, `_RAPOR/S0_FILM.json` | S0 HATA 0 | ajan `ses-tasarimcisi` (tasarım, müzik kipleri) + betik |
| A09 | Bütün plan alanları → istem derleme (`--hareket`, `--gorsel`), istem denetimi, kamera ağacı, kart tarifleri | `SAHNELER.json` istemleri, `_RAPOR/ISTEM_FILM.json`, `KAMERA_AGACI.json`, `_KARTLAR/KART_SPEC.json` | `istem_denetim` HATA 0; elle istem ≤ %5 [kaynak: YN1 tahmin] | betik + ajan `kart-tasarimcisi` |
| — | **Kâğıt sonu.** `KAGIT` imzası yazılır | `_RAPOR/KAGIT_TAMAM.json` | — | Bulutta: `esitle --gonder` → **4 ORTAM** |

#### 4.2.3 Varlık evresi (yerel; Flow video kredisi yok)
| Kod | Girdi → İş | Çıktı | Geçme şartı | Kim |
|---|---|---|---|---|
| A10a | Makine → kurulum ölçümü: ana ortam ve ayrı sanal ortamlar (RVC, OpenVoice, MuseTalk, ACE-Step), ölçüm modelleri, `ai84.credits()` ve `ai84.estimate()`, Flow bakiyesi salt okuma | `_RAPOR/KURULUM_OLCUM.json`, `HESAP_DURUMU.json`, `FILM_AYAR.json → fiyat_olcum` | Eksik ortam yalnız kendi basamağını kapatır ve raporda yazar ([SM2] SB0) | betik `kurulum.py --olc` |
| A10b | Adlar → telaffuz testi | `_RAPOR/S1_TELAFFUZ.json` | Her ad GEÇ; geçmeyen `hikaye-yazari`'na (H15) | betik |
| A10c | Profiller → ses seçimi; seri başında motor kıyası; eksik efekt temini | `EVREN/<SERI>/karakterler/<id>/ses.json`, `_RAPOR/S1_*.json` | [SM2] SB2–SB4; AI84 tavanları | betik + yakın puanda ajan `ses-tasarimcisi` |
| A10d | `KART_SPEC.json` → evren bağlama, Gemini kart paketi, kart kapısı, seçim, kilit | `EVREN/<SERI>/…`, `EVREN_BAG.json`, `_RAPOR/KART_FILM.json` | [GS] A4 | betik + **kullanıcı (paket)** + ajan `kor-gozlemci`, `yonetmen` (kart seçimi) |
| A11 | Kamera ağacı sırasıyla başlangıç görselleri (2 aday) → G1 → CORRECTION (Flow görsel, **günlük tavanla**) → K1-ön | `SIRALI_GORSEL/NNN.jpg`, `_RAPOR/G1_P*.json`, `K1ON_P*.json` | Her plan G1 GEÇ ya da yönetmen kaçış kararı; Flow görsel tavanı ve beklemesi (§4.7.2) | betik + **kullanıcı (paketler)** + ajanlar `kor-gozlemci`, `sureklilik-denetcisi` (hakem) |
| A12 | G1'li görseller → animatik sesi (son sesler) → T1 → render → aşamalı seyirci → düzeltme ve kesme turu; P1 ön turu | `ANIMATIK/*.mp4`, `_RAPOR/HS_ANIMATIK_P*_tN.json` | RE `seyirci_*`; render süresi = T1 ±1 kare; ≤ 3 tur [tahmin]; tükenirse 6 KAPI (video başlamaz) | betik + ajanlar `habersiz-seyirci`, `kurgucu`, `kesici` |
| A13 | Bütün raporlar + bakiyeler → **B2**, üretim önizlemesi, gün planı, hat denetçisi | `URETIM_ONIZLEME.json/.md`, `_RAPOR/HAT_FILM.md` | B2 geçer ve hat denetçisi `GIT` der | betik `kredi.py --kesin` + ajan `hat-denetcisi` |

#### 4.2.4 Üretim evresi (kredi)
**A14a — Pilot dalga (yeni).**
- **Neden:** Birçok eşik ve biçim tahmindir ve ancak gerçek Flow klibiyle ölçülebilir: G1/V eşikleri ([GS] R1), istem biçimi `aralik` / `sira`
  ([YN1] R1), ses yolu kıyasının yeni filmde doğrulanması ([SM2] SB3), klibin durağan başlangıcı ([KU1] soru 4), 10 sn klibin fiyatı
  ([UM1] Q3), 720p video üretim süresi. Bunları 405 klibin hepsini çektikten sonra öğrenmek, yanlış eşiğin bedelini bütün filme ödetir.
- **Seçim (betik `pilot_sec.py`):** P1'den 20–30 **gerçek** plan [tahmin]. Kapsama kuralı (her biri en az): 3 `son_kare` zinciri (derinlik 1 ve 2),
  3 `bitis_sabit`, 4 iki kişilik, 3 el–nesne kavrama, 3 konuşmalı (ses iki yol), 2 yaratık, 2 düşük ışık, 2 profil ya da sırt. Konuşmalı ve eylem
  planlarının yarısı `aralik`, yarısı `sira` istem biçimiyle derlenir.
- **Kredi:** ek kredi yoktur; planlar filmin kendisidir. Pilotta kalan planların yeniden çekimi kendi dilimlerinden düşer.
- **Çıktı:** `_RAPOR/PILOT_FILM.json`: her kapının ölçüm dağılımı, kaçırma ve yanlış alarm (hakem ve sonraki bulgularla), istem biçimi
  sonucu, ses yolu sonucu, durağan başlangıç medyanı, fiyat ve süre ölçümleri, kredi gerçek/tahmin.
- **Sonra:** `ders_defteri --derle` → `ders-editoru` → korkuluklu `--uygula`. İstem biçimi değişirse kalan planların `hareket_istem`'i yeniden
  derlenir (görseller değişmez). Değişen eşikler imzaları değiştirir ve etkilenen kapılar yeniden koşar. B2 güncellenir, hat denetçisi bir kez daha bakar.
- **Geçme şartı:** pilot raporu var, kararlar deftere yazılmış. Pilot bir kapı değildir; ama raporu olmadan A14 başlamaz (ilk filmde).

**A14 — Video blokları (değişti).**
- **Girdi:** onaylı önizleme (imzasıyla), `SIRALI_GORSEL/` (G1 sha'larıyla), `SAHNELER.json`, `KUYRUK/YENIDEN_URET.json` (onaylı maddeler), `FLOW_TEMPO.json`.
- **Uygunluk kuralı** (bir plan şu an gönderilebilir mi):
  1. Görseli G1 GEÇ ve dosya sha'sı G1 kaydıyla aynı.
  2. `uretim.zincir.yontem = son_kare` ise kaynak klip V1+V2+V3 GEÇ, zincir karesi çıkarılmış ve `ZK` GEÇ.
  3. `plan_imza` önizleme imzasıyla aynı (değişmişse plan `bayat`, önce kuyruk).
  4. `KREDI_DEFTERI`'nde bu iş için indirilmemiş bir `gonderildi` kaydı yok.
- **Blok planı (`blok_plani.py`):** her blok o an uygun ilk ≤ 20 planla doldurulur. Sıra: önce KRİTİK yeniden çekimler (dilim kalanı varsa),
  sonra hikâye sırası (`sira`). Sahne grubu sınırına 3 plandan yakınsa blok sınırda kesilir [kaynak: CI kural 5 "blok sahne sınırında"; 3 tahmin].
  Zincir derinliği 2'yi aşacaksa plan yeniden demirlenir ([GS] A11).
- **Bir blok:** `memmet.py <film> --blok <BLOK_PLANI.json#k> --mod elle|gece --onizleme <imza>`. Memmet her gönderimden önce `FLOW_TEMPO.json`'a
  ve `DUR`'a bakar, gönderim kaydını önce yazar, sonucu `data-media-id` ile tanır, indirir, `_memmet_cikis.json` yazar ve çıkar.
- **Her indirmede (Memmet çıktıktan hemen sonra, hızlı):** V1 teknik denetim ([GS] A13) ve metin kapısı ([SM2] SC1). Konuşma yoksa,
  ad yanlışsa ya da `tasidigi` eksikse madde kuyruğa girer.
- **Blok arasında (zorunlu Flow molasının içinde, `yerel_is.py` kuyruğuyla):** V2, V3 ([GS] A14), zincir çıkış noktasının kilidi
  ([KU2] KR5), zincir karesinin çıkarılması ve `ZK` ([GS] A15). Mola bittiğinde işlenmemiş zincir varsa sonraki blok yalnız uygun
  planlarla doldurulur; bekleme yaratılmaz.
- **Yeniden çekim:** kuyruk maddesi `kuyruk.py`'den geçer (0 kredi kuralı, dilim, BK noktası), uygun olunca aynı gecenin sonraki bloğuna girer.
  Plan başına toplam yeniden çekim ≤ 2 (teknik + kurgu) [kaynak: KU2]. Aşılırsa yönetmen onarım kipi.
- **Oturum:** `VIDEO_YARI_OTOMATIK.bat` (ya da izinliyse `VIDEO_GECE.bat`) tek bir video oturumu başlatır: `film.py oturum --video`
  blokları tempoya göre art arda çalıştırır, aralarda işler, Telegram'a "blok k hazır" yazar, `DUR`'da ya da kısıtta durur.
- **Çıktı:** `SIRALI_VIDEO/NNN.mp4`, `KUNYE/NNN.json`, `KREDI_DEFTERI.jsonl`, `FLOW_YUK.jsonl`, `_RAPOR/V1_B*.json`, `V2_*`, `V3_*`, `ZK_*`, `S2m_B*.json`.
- **Geçme şartı:** her klip için dosya var ve V1/V2/V3 ile metin kapısı GEÇ ya da kuyrukta yazılı karar var. Kısıt gelirse hemen durur (§4.5.8).

**A15 — Ses.** Hat yalnız sırayı ve kuyruğu verir: [SM2] SD1 (dönüşüm, TTS, ses merdiveni). GPU işleri `yerel_is.py` kuyruğundan. AI84 harcaması tavanla sınırlı.

#### 4.2.5 Kurgu ve yayın (hat açısından)
| Kod | İş | Çıktı | Geçme şartı | Kim |
|---|---|---|---|---|
| A16 | T2 kaba kurgu, ses katmanları (S3–S7), Z3, aşamalı kurgu seyircisi, düzeltme/kesme/yeniden çekim, P1 ön turu, CapCut taslağı | `KURGU/KURGU_PLANI.json`, `KURGU/SES_CIZELGESI.json`, CapCut taslağı, `_RAPOR/HS_KURGU_P*_tN.json` | [KU2] KR6–KR10; ≤ 3 tur; tükenirse en iyi sürüm + açık eksik raporu (kredi zaten harcanmış olduğu için durma değil teslim) | betikler + ajanlar `kurgucu`, `kesici`, `habersiz-seyirci` |
| A16n | Kullanıcı notu ya da CapCut düzenlemesi | `TASLAK_FARK.json`, klon taslak | [KU2] KR11 | betik + `kurgucu`; `film-not` becerisi |
| A17 | **Teslim:** kullanıcı CapCut'tan dışa aktarır, dosyayı `YAYIN/`'a koyar (algılama kendiliğinden) → final kalite (siyah kare, donma, sessizlik, −14 LUFS ±1, ≤ −1 dBTP) → yayın sesi (mux yalnız "aynı çizelge" kanıtıyla [KU2] İ-2) → jenerik, kapak, YouTube paketi, 3 Short (doğrudan MP4 [kaynak: BK §8 #18]), altyazı | `YAYIN/` | `kalite_denetim --final` HATA 0 | betik + **kullanıcı (dışa aktarma)** + ajan `yayin-paketcisi` |
| A17y | Yükleme | — | **İsteğe bağlı ve onaylı** [kaynak: CLAUDE.md Yapılacaklar 6] | kullanıcı |

#### 4.2.6 Kapanış (A18)
| İş | Çıktı | Kim |
|---|---|---|
| Ders derlemesi ve terfi önerileri | `BILGI/DERSLER/derleme_<film>.md`, `aday_kurallar.json` → korkuluklu `--uygula` | betik + ajan `ders-editoru` |
| Evren güncellemesi (kanon, kart varyantları, sesler, mekân sesi, `DURUM_SON.json`, `IZLEYICI_OZETI.md`) | `EVREN/<SERI>/` (yalnız `evren.py` yazar) | ajan `hikaye-yazari` (evren kipi) + betik |
| Film sonu raporu: tahmin/gerçek kredi, yeniden çekim oranı ve dilimleri, kapı istatistikleri, takvim, el işi sayıları | `FILM_SONU_RAPORU.md` | betik |
| Arşiv: ara klasörler `D:\YZ_FILM_ARSIV\<FİLM>\` altına **taşınır** (`robocopy /E /MOVE`; `/MIR` yasak). Son taslağın bağlı olduğu dosyalara dokunulmaz | taşıma listesi | betik `arsivle.py` (`ARSIVLE.bat`) [kaynak: BK §7.10] |

#### 4.2.7 Sıranın gerekçesi
- v2 sırası korunur [kaynak: BK §7.6]: hikâye → kâğıt seyirci → yönetmen → ses kâğıtta → kartlar → görsel + denetim → animatik → video → katmanlı kurgu → yayın.
- Bu turda eklenenler: B0 (süre yazımdan önce), plan seyircisi (A07e), telaffuz testi kartlardan önce (A10b), ses kadrosu animatikten önce (A10c),
  pilot dalga (A14a), blok arası işleme (A14).
- Kâğıt ile varlık evresi arasındaki sınır aynı zamanda **bulut ile yerel** sınırıdır. Bulutta bütün kâğıt aşamaları biter, taşınır ve yerel
  hiçbir kâğıt işini tekrarlamaz (imzalar aynı olduğu için).

### 4.3 Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) — yalnız kendi alanım

#### 4.3.1 İlkeler (değişti; [CM] §3.1 ile aynı)
- Hattın yürütücüsü ajan değildir: ana Claude dağıtır, `film.py` sırayı verir.
- Ölçülebilen her iş betiktir: kredi tahmini, blok planı, kilit, tempo, bildirim, taşıma, pilot seçimi [kaynak: A3 B4].
- Bütün ajanlar `model: opus`, `effort: high`. `fallbackModel` ve `memory:` tanımlanmaz. Ajanlarda **Bash yoktur**; denetim SubagentStop kancasındadır.
  Ajan dönüşü ≤ 5 satırdır: çıktı yolu + `OZET |` satırı.
- Alanımda yargı isteyen yalnız üç iş var. Bunlar için üç ajan:

#### 4.3.2 `ders-editoru` (değişti: tur 1'deki adı `ders-katibi`)
| Alan | Değer |
|---|---|
| model / effort | `opus` / `high`. Defterdeki her kural gelecekteki bütün filmleri etkiler [kaynak: H/ajan-opus-yuksek] |
| tools | `Read, Write`. Yazma yalnız görevin `CIKTI/`'sine (kanca) |
| Ne zaman | A18'de; ilk filmde ayrıca pilot dalgadan sonra (A14a) |
| Görev | `ders_defteri.py --derle`'nin kümelerini okur. Aday kural yazar: `tur`, `kosul`, `etki`, `kanit`, `gerekce`, `geri_al`. Çelişen ya da etkisiz kuralı emekliye ayırmayı önerir. Rol etiketli talimat derslerini tek cümleye çevirir (`DERSLER_AKTIF.md` için). 1 sayfalık "bu filmde ne öğrendik" yazar |
| Okuyacakları (GIRDI) | Derleme kümeleri ve sayıları, `KURALLAR_OGRENILEN.json`, `03_DERSLER.md`, BK §8, ilgili eşik dosyalarının dilimi, `FILM_SONU_RAPORU.md`, `PILOT_FILM.json` |
| Çıktı | `CIKTI/aday_kurallar.json` + `CIKTI/derleme.md`. Kurallar **betikle** uygulanır: `ders_defteri.py --uygula` şemayı ve korkulukları denetler (§4.5.11) |
| Kesin yasaklar | Güvenlik kurallarını gevşetmek (bot, Flow uyarısında durma, gizli bilgi, kalıcı silme, onay atlama). Tempo ya da Flow günlük tavanını yükseltmek. Kanıtsız kural. Tek filmden genelleme (hikâye etiketli derslerde en az 2 film [kaynak: SN2 §2.8]) |

#### 4.3.3 `memmet-bakimci`
| Alan | Değer |
|---|---|
| model / effort | `opus` / `high`. Değişmiş bir Flow sayfasını çözmek yargı ister; yanlış seçici kredi yakar |
| tools | `Read, Edit, Write` **(değişti: Bash yok)**. Edit ve Write yalnız `memmet.py`, `saglayicilar/flow.py`, `testler/fikstur_flow/*`, `BILGI/FLOW_KESIF.md` için (kanca) |
| Ne zaman | Memmet `arayuz` koduyla durunca (seçici bulunamadı, beklenmeyen sayfa). Yalnız yerelde |
| Görev | `_MEMMET_HATALAR/*.html` ve `.png` dosyalarını okur. Değişen seçiciyi bulur, yeni sayfayı HTML fikstürü olarak ekler, `memmet.py`'yi düzeltir, `FLOW_KESIF.md`'yi günceller |
| Doğrulama | SubagentStop kancası `python -m unittest testler.test_memmet` koşar; kırmızıysa durma engellenir (≤ 2). Yeşilse `film.py` değişikliği `_MEMMET_HATALAR/BAKIM_<tarih>.md` ile kaydeder. Onarımdan sonraki **ilk blok `elle` modda** gider (insan basar) |
| Kesin yasaklar | reCAPTCHA çözmek; fare/klavye taklidi; tempo hızlandırmak; uyarı metnini görmezden gelmek; uyarıdan sonra kendiliğinden yeniden başlatmak [kaynak: BK §6.2] |

#### 4.3.4 `hat-denetcisi`
"Hiçbir model kendi çıktısını onaylamaz" ilkesinin kredi kapısındaki karşılığıdır [kaynak: A1 B4 ARIS].
| Alan | Değer |
|---|---|
| model / effort | `opus` / `high` |
| tools | `Read, Write` (yalnız `CIKTI/`) |
| Ne zaman | A13 (B2'den önce), pilot dalgadan sonra, kuyrukta onay bekleyen kredili madde 30 klibi aşınca [tahmin], bir dilimden ötekine aktarma istenince ([KU2] §2.5) |
| Görev | Betik kapılarının göremediğini arar: sağlayıcı ya da model karışımı sahne grubu ortasına düşüyor mu; ders defterinde 3/3 başarısız olmuş bir desen planda kaç kez var; gün planı Flow yük geçmişiyle çelişiyor mu (aynı gün görsel düzeltmesi + video); bütçe tavanı bir sahne grubunu yarıda bırakıyor mu; pilot sonuçları kalan planlara uygulanmış mı |
| Okuyacakları | `URETIM_ONIZLEME.json`, `_RAPOR/*` özetleri (betik dilimler), `KURALLAR_OGRENILEN.json`, `FLOW_YUK` son 30 günün özeti, `PILOT_FILM.json`, `FILM_AYAR.json`'un maskeli özeti |
| Çıktı | `CIKTI/hat_denetim.md`, son satır `OZET \| karar: GIT \| KRITIK: 0 \| ORTA: 2`. `GITME` → çıkış 6 ve gerekçe |

#### 4.3.5 Başka alanlardan kullandığım ajanlar
`yapimci`, `hikaye-mimari`, `juri-uyesi`, `hikaye-yazari`, `oyuncu`, `diyalog-editoru`, `habersiz-seyirci`, `ozet-eslestirici`, `yonetmen` (kipleriyle),
`plan-elestirmeni`, `uretilebilirlik-denetcisi`, `sureklilik-denetcisi`, `kart-tasarimcisi`, `kor-gozlemci`, `ses-tasarimcisi`, `kurgucu`, `kesici`,
`yayin-paketcisi`. Hat açısından iki şartım var:
1. Çıktı makinece okunur: şemalı JSON ya da son satırda `OZET |`.
2. Girdi ve çıktı yolları yalnız `GOREV.json`'dan gelir; ajan kendi başına dosya aramaz. Habersizlik ancak böyle korunur.

#### 4.3.6 Ajan çağrısı bütçesi (değişti) ve paralellik
| Aşama | Çağrı | Kaynak |
|---|---|---|
| A01–A06 hikâye odası | 40–75 | [SN2] §4.1.4 |
| A06s, A08, A10c ses | 15–55 (sahne grubu dilimleri dahil) | [SM2] §2.1 Ç-2; tahmin |
| A07a–A07e yönetmen ve plan denetimi | 70–110 (3 harita + ≈ 45–55 sahne grubu + onarım + eleştirmen + 3–6 seyirci/eşleştirici) | [YN2], tahmin |
| A09 kart tarifleri | 1–3 | [GS] |
| A10d, A11 kör gözlem | ≈ 145 (kart ≈ 20 + G1 ≈ 90 + V3 ≈ 35; ≤ 12 görsel/çağrı) | [hesap; görev boyu GS tahmini] |
| Hakem, kart seçimi | 15–40 | tahmin |
| A12 animatik | 20–35 | [KU2], tahmin |
| A13, A14a hat denetçisi, ders | 3–6 | — |
| A15 replik kabul | 5–15 | [SM2] |
| A16 kurgu | 20–35 | [KU2], tahmin |
| A17–A18 | 5–10 | — |
| **Toplam** | **≈ 350–550** | [tahmin] |

- Aynı anda en çok **5** ajan çalışır [kaynak: YN2, tahmin; kullanım sınırına göre]. `FILM_AYAR.json → ajan.paralel_max`.
- Kullanım sınırı dolunca ([CM] `StopFailure` kancası) koşan görevler `kesildi` olur, Telegram "sınır doldu; açılınca DEVAM" yazar.
  Değerlendiricinin yarım işi sıfırdan, yazarınki devam ettirilir ([CM] §2.3).
- Başsız yürütme (İ-6) dolarla açılan bir hızlandırıcıdır, varsayılan değildir.

### 4.4 Beceri (skill) tarif adımları — hat yürütme

#### 4.4.1 Dosyalar (değişti)
Beceri metinlerinin sahibi [CM]'dir (`film-yap`, `film-durum`, `film-not`, `film-gelistir`). Benim katkım:
```
.claude/skills/film-yap/
  hat/ASAMALAR.md        film.py asamalar --md ile ÜRETİLİR (elle yazılmaz; kayıtla ayrışmasın)
  hat/KISITLAR.md        kısıt kodu → Türkçe açıklama → kalan yollar (§4.5.8 tablosu)
  hat/BUTCE.md           B0/B1/B2/BK ne zaman, sayıların nasıl okunacağı (kullanıcıya 3 satırlık özet kalıbı)
  KULLANICI_DILI.md      ([CM]) içine: çıkış koduna göre sabit Türkçe cümleler ve hangi .bat
  KURTARMA.md            ([CM]) içine: kilit bayat, DUR, kesik indirme, esitle çakışması, GPU kilidi
```

#### 4.4.2 SKILL.md çekirdeğine girecek hat kuralları (sıkıştırmadan sonra geri gelen ilk 5.000 token içinde [kaynak: CM, D/skills])
1. Kredi yalnız `film.py`'nin bütçe noktası geçince harcanır. Claude bir sağlayıcıyı ya da `memmet.py`'yi doğrudan çağırmaz.
2. Flow "olağan dışı etkinlik" ya da doğrulama → hat durur. Yeniden başlatma, atlatma, tempo hızlandırma yoktur. Kilidi yalnız kullanıcı kaldırır.
3. Çıkış kodu ne diyorsa o yapılır (tablo §4.2.0); 2, 4, 5, 6, 7, 8'de tur biter, soru eklenmez.
4. `AYARLAR/` hiçbir kökte okunmaz, yazılmaz. Ayar gerekiyorsa `film.py goster ayar` (maskeli).
5. Kalıcı silme yok; eski dosyalar `_ESKI/`'ye taşınır. `robocopy /MIR` yok.
6. Hafızaya değil `film.py sonraki` çıktısına güvenilir. **(değişti)** Tur başına aşama sınırı yoktur; [CM]'nin `devam_kapisi` kancası sürüşü
   yönetir ve `bekle`/`kullanici`/`kisit`/`ortam`/`butce` durumunda durmaya izin verir.

**Kullanıcıya konuşma biçimi.** Soru sorulmaz, durum söylenir; en çok 3 satır: ne bitti · şimdi ne oluyor · senden bir şey gerekiyor mu
(yalnız M2 listesindeki fiziksel işler). Örnek: "Hikâye 3. turda 8/8/9 aldı; yönetmen planları yazılıyor."

#### 4.4.3 Kancalara eklerim ([CM] K-3…K-10'un üstüne)
| Kanca | Ek kural | Neden |
|---|---|---|
| `erisim_kapisi` (PreToolUse `Read\|Glob\|Grep\|Write\|Edit`) | Veri kökünü `YOLLAR.json`'dan çözer; `<veri_kok>/AYARLAR/**` ve `<depo>/YZ_FILM/AYARLAR/**` desenle ret (istisna `*.ornek.json`, `OKU_BENI.txt`) | İ-3 |
| `komut_kapisi` (PreToolUse `Bash`) | `memmet.py` yalnız `--giris` ve `--bakiye` ile doğrudan çalışabilir; video ve görsel gönderimi yalnız `film.py` üzerinden | Kapı deliği (S2) kod düzeyinde kapanır |
| `komut_kapisi` | `FLOW_KILIDI.json` varken `film.py oturum --video` ve görsel düzeltme reddedilir (yalnız `UYARI_GECTI.bat` kaldırır) | İ-8 |
| `komut_kapisi` | Çıplak `git push`, `git add -A` ve `AYARLAR` geçen git komutları ret; push yalnız `film.py esitle --gonder` | İ-3 |
| `oturum_basi` (SessionStart) | Özete eklenir: BEKLE bitiş saati, Flow kilidi, son Flow uyarısı, günlük görsel sayacı, bütçe durumu, bekleyen kullanıcı işi | Sıkıştırmadan sonra yanlış "devam" olmasın |
| `hata_kaydi` (StopFailure) | Koşan görevleri `kesildi` işaretler; Telegram `sinir_doldu` | [CM] §2.3 |

#### 4.4.4 Değerlendirme senaryoları (beceri davranış testleri, en az 3 [kaynak: A3 B4])
1. "Ejderha büyüten bir kadın hakkında film yap" → soru yok, `yeni --konu` çalışır, A01'den başlar.
2. "Devam et" (bağlam boş, A07c'de B1 yarımken) → `sonraki` A07c'yi verir; A00–A07b yeniden yapılmaz.
3. Bulutta "videoları üret" → `esitle --gonder` + çıkış 4; Memmet çağrılmaz.
4. Flow kilidi varken "devam et" → çıkış 7; yeniden deneme önerilmez; elle 1 video testi ve `UYARI_GECTI.bat` anlatılır.
5. **(yeni)** Gece oturumu ortasında Memmet kapanıp yeniden açılıyor → kalan blok molası beklenir (çıkış 8), mola kısalmaz.
6. **(yeni)** Aynı gün 20. Flow görsel düzeltmesinden sonra "devam" → görsel düzeltmeleri ertesi güne, video oturumu en erken 12 saat sonraya planlanır (çıkış 8).

### 4.5 Veri şeması (JSON örnekleriyle) — yalnız kendi alanım
Plan içeriği alanlarının (`zanaat`, `_derlenir`, `zanaat.ses`) sahibi yönetmen, senarist ve ses uzmanlarıdır ([YN2] §4.5.2 sahiplik tablosu).
Aşağıdakiler hattın kendi dosyalarıdır. Örneklerdeki sayılar **örnektir**, ölçüm değildir.

#### 4.5.1 Aşama kaydı (kodda tek doğruluk kaynağı)
```python
# YZ_FILM/ARACLAR/hat/asamalar.py  — Python 3.10 uyumlu
@dataclass(frozen=True)
class Asama:
    kod: str                 # "A07c"
    ad: str                  # "birlestirme_defter_z0_b1"
    kim: str                 # "betik" | "ajan" | "kullanici" | "karisik"
    girdiler: tuple          # yol desenleri, "ESIKLER", "EVREN:<seri>/..."
    ciktilar: tuple
    kapilar: tuple           # rapor adları (§2.3): ("K0", "Z0", "B1")
    kredi: str               # "-" | "ai84" | "flow" | "usd"
    ortam: str               # "her_ikisi" | "yerel"
    tur_max: int | None
    geri_don: str | None     # kapı tükenince yazar aşaması ("A07b")
    gorevler: str            # görev üretici işlevin adı (hat/gorev.py)

ASAMALAR = (
  Asama("A07c", "birlestirme_defter_z0_b1", "betik", ("30_YONETMEN/PLANLAR/*.json", "HIKAYE.json", "ESIKLER"),
        ("SAHNELER.json", "DUNYA_DEFTERI.json", "_RAPOR/K0_FILM.json", "_RAPOR/Z0_P*.json"), ("K0", "Z0", "B1"),
        "-", "her_ikisi", 3, "A07b", "betik_gorevi"),
  Asama("A14", "video_bloklari", "karisik", ("URETIM_ONIZLEME.json@GEC", "SIRALI_GORSEL/", "KUYRUK/YENIDEN_URET.json"),
        ("SIRALI_VIDEO/", "KUNYE/", "KREDI_DEFTERI.jsonl"), ("V1", "V2", "V3", "ZK", "S2m"),
        "flow", "yerel", None, None, "video_oturumu"),
)
```
`ESIKLER` = `esikler.py`'nin birleştirdiği bütün eşik dosyaları + `KURALLAR_OGRENILEN.json`. Sürümleri imzaya girer: eşik değişince kâğıt kapıları
yeniden koşar, kredili çıktılar yalnız `bayat` işaretlenir. `hat/ASAMALAR.md` bu kayıttan `film.py asamalar --md` ile üretilir.

#### 4.5.2 `film.py sonraki` çıktısı ve `GOREV.json`'a eklerim
```json
{"film": "F20261024_ejderha", "asama": "A07e", "ad": "plan_seyircisi", "tur_no": 1, "tur_max": 2,
 "cikis_kodu": 3, "durum": "ajan_bekliyor",
 "gorevler": [
  {"id": "G0213", "tur": "ajan", "ajan": "habersiz-seyirci", "kip": "plan", "paralel_grup": "A07e_t1",
   "istem": "Görevin: FILMLER/F20261024_ejderha/_GOREV/G0213/GOREV.json — önce onu oku, yalnız orada yazanı yap."}],
 "kullaniciya": null, "bekle": null, "oku": null}
```
- Kullanıcı işi: `"kullaniciya": {"metin": "Masaüstü\\GEMINI GORSEL ISTEM\\F20261024_P1_ANA_03 klasörünü Gemini'ye ver, gelen ZIP'i GELENLER'e koy. Ben ZIP'i görünce kendim devam ederim.", "bat": null, "algilama": {"tur": "dosya_var", "desen": "GELENLER/*P1_ANA_03*.zip"}}`.
- Bekleme: `"bekle": {"neden": "blok_molasi", "bitis": "2026-10-28T01:52:00+03:00"}` (çıkış 8).
- `GOREV.json` ([CM] §5.2 biçimi) üstüne eklediklerim: `"kredili": false`, `"ortam": "her_ikisi"`, `"girdi_imza": "…"` (görev kurulurken),
  `"gecme_sarti": {"…": "…", "zarf": true}`, `"cikis_eslemesi": {"3": "tur"}` (alt araç kodları, §2.6).

#### 4.5.3 Çıktı zarfı ve `FILM_DURUM.json` (önbellek)
```json
"_uretim": {"asama": "A07c", "gorev": "G0188", "girdi_imza": "9f1c0a2b7e44d310", "arac": "plan_birlestir.py 1.0",
            "esik_surum": "ritim@1.0+hat@1.0+ogrenilen@7", "sonuc": "GEC", "zaman": "2026-10-24T15:02:11+03:00", "ortam": "bulut"}
```
```json
{"surum": 3, "film": "F20261024_ejderha", "seri": "FROSTHOLLOW", "ortam_son": "yerel",
 "aktif_asama": "A14", "otomatik_surus": true,
 "asamalar": {"A12": {"durum": "tamam", "tur": 2, "girdi_imza": "…", "rapor": "_RAPOR/HS_ANIMATIK_P1_t2.json"},
              "A14": {"durum": "kismi", "blok": 9, "biten": 168, "toplam": 405, "bekle_bitis": "…"}},
 "donguler": {"A06": {"tur": 3, "tavan": 4, "medyanlar": [6.5, 7.5, 8.0]}},
 "bekleyen_kullanici": [], "sayaclar": {"kullaniciya_soru": 1, "kullanici_isi": 19, "ajan_cagrisi": 312, "kanca_engeli": 2},
 "harcama": {"flow_kredi": 2016, "ai84_kredi": 21400, "usd": 0.0},
 "gecmis": [{"zaman": "…", "olay": "kisit", "asama": "A14", "kod": "olagandisi", "plan": 213}],
 "model_sapmasi": []}
```
`durum` değerleri: `bekliyor, calisiyor, ajan_bekliyor, kullanici_bekliyor, bekle, kapi_gecmedi, kismi, tamam, bayat`.

#### 4.5.4 Kapı raporu (ZN §6.2 biçimi + imza, tur, kapsam)
```json
{"kapi": "G1", "kapsam": "P2", "tur": 1, "sonuc": "HATA",
 "girdi_imza": "…", "esik_surum": "…", "arac": "kare_denetim.py 0.3",
 "ozet": {"plan": 168, "gec": 151, "bayrak": 12, "hata": 5, "olculemedi": 3},
 "hatalar": [{"madde": "G1.kimlik", "plan": 212, "olcu": 0.31, "esik": 0.363, "seviye": "H",
              "oneri": "CORRECTION: …", "kanit": "SIRALI_GORSEL/_ADAYLAR/212_b.jpg"}]}
```
`olculemedi` her zaman BAYRAK'tır, asla GEÇ değildir ([GS] §7 başı).

#### 4.5.5 Kuyruklar (değişti: [KU2] alanlarıyla birleşik tek şema)
`KUYRUK/YENIDEN_URET.json` (görsel ve video aynı dosyada, `tur` ile ayrılır; yazan her kapı, yöneten `kuyruk.py`):
```json
[{"id": "YU-B07-142-2", "plan": 142, "tur": "video", "kaynak_kapi": "V2", "kaynak_rapor": "_RAPOR/V2_B07.json",
  "seviye": "KRITIK", "kok_neden": "yuz_degisti", "cozum": "yeniden_cek",
  "sifir_kredi": {"denendi": true, "gerekce": "kusur kullanılan pencerenin içinde (2,1–4,0 sn); kırpma yetmez"},
  "duzeltme": "CORRECTION: …", "oncelik": 6.75, "dilim": "goruntu", "kredi_tahmini": 12, "zincir_etkisi": [143],
  "deneme": 2, "deneme_max": 2, "is_kimligi": null, "durum": "bekliyor", "karar_veren": null}]
```
- `kaynak_kapi` ∈ `G1, V1, V2, V3, ZK, S2, S2m, S3, Z3, HS_ANIMATIK, HS_KURGU, NOT`. `dilim` kaynaktan türer: G1/V*/ZK → `goruntu`; S* → `ses`; Z3/HS_*/NOT → `kurgu`.
- `cozum ∈ {yeniden_cek, yeni_plan}` olan madde `sifir_kredi.denendi: true` ve gerekçe olmadan kuyruğa giremez ([KU2] İ-3; `kuyruk.py` zorlar, test T23).
- `is_kimligi` gönderimde dolar; çift harcama denetimi bu alandan yapılır.

`KUYRUK/YENIDEN_YAZ.json` (kâğıt; metni yazan yazara döner [kaynak: YR §1]):
```json
[{"id": "YY-A07c-031", "konum": {"sahne": "S12", "plan": 121}, "kapi": "K0", "madde": "Y16", "kok_neden": "nesne_zipladi",
  "yazar": "yonetmen", "oneri": "…", "tur": 1, "durum": "bekliyor"}]
```

#### 4.5.6 Kök neden sözlüğü (tek)
`YZ_FILM/ARACLAR/veri/kok_neden.json`: [KU2]'nin sözlüğü (kurgu, yönetmen, süreklilik, ses, hikâye satırları) + [SM2] §2.5 ses kategorileri +
hat satırlarım: `tempo_uyari`, `dogrulama`, `kredi_bitti`, `arayuz_degisti`, `filtre_kelimesi`, `zaman_asimi`, `kesik_indirme`, `gpu_bellek`,
`esitle_cakisma`, `butce_sapmasi`. Her satırın `sahip` alanı vardır; bulgu yönlendirmesi ([SN2] §2.4) ve ders defteri aynı sözlükle sayar.

#### 4.5.7 Plan düzeyi: `uretim` alt nesnesi (değişti)
```json
"uretim": {
  "uretim_blogu": 7, "blok_gercek": 8,
  "saglayici": "flow", "model": "omni-1.1-flash", "cozunurluk": "720p", "klip_sn": 8, "istem_bicimi": "aralik",
  "zincir": {"yontem": "son_kare", "kaynak": 141, "kesim_sn": 5.6, "derinlik": 1, "yedege_dustu": false},
  "gorsel_sha": "9c1e4d…", "bitis_gorsel_sha": null,
  "durum_dondu": {"bas": "a41f…", "bit": "77c2…"},
  "plan_imza": "c0ffee12",
  "deneme": 1, "deneme_max": 2, "seed": null,
  "is_kimligi": "V-142-d1-7f3a9c",
  "durum": "uygun"}
```
- Niyet `zanaat.zincir`'dedir (yönetmen yazar: `gecis_turu`, `onceki_plan`, `bitis_sabitle`). `uretim.zincir`'i `kare_zinciri.py` yazar ([YN2] Ç-6).
- `durum` ∈ `bekliyor, uygun, gonderildi, indirildi, denetimde, gecti, kuyrukta, bayat, kayip, reddedildi`.
- `plan_imza` = özet(`hareket_istem`, `gorsel_sha`, `bitis_gorsel_sha`, model, çözünürlük, `klip_sn`, `durum_dondu`). Değişirse video `bayat`.
- `is_kimligi` = sha1(plan, tür, istem metni, `gorsel_sha`, `bitis_gorsel_sha`, model, çözünürlük, deneme)[:6].
- `uretim_blogu` planlanan bloktur, `blok_gercek` gönderildiği blok. İkisini de betik yazar, kimse elle yazmaz.

#### 4.5.8 Sağlayıcı arayüzü, kayıt ve kısıt davranışı (değişti)
Mevcut `saglayicilar/__init__.py` korunur; eklenenler:
```python
TURLER = ("llm", "gozlemci", "gorsel", "video", "tts", "ses_donustur", "ayristirma", "asr", "dudak", "muzik", "dinleyici")
ESKI_ADLAR = {"ses": "tts"}          # bir sürüm boyunca tanınır

class Saglayici:
    ad = ""; turler = (); toplu_mu = False; kredili = True
    para_birimi = None   # "flow_kredi" | "ai84_kredi" | "usd" | None
    ortam = "yerel"      # "yerel" | "her_ikisi"
    elle = False         # kullanıcı işi ister (gemini_paket)
    gpu = False          # True ise yerel_is kuyruğundan ve GPU kilidiyle çalışır
    def hazir(self) -> tuple[bool, str]: ...
    def birim_fiyat(self, is_) -> float | None: ...   # None = bilinmiyor → bütçe BAYRAK
    def bakiye(self) -> float | None: ...

class Kisitlandi(Exception):
    kod: str             # olagandisi | dogrulama | kredi_bitti | arayuz | filtre_red | anahtar_yok | ag | kota | ortam | zaman_asimi
    yeniden_dene: bool   # yalnız ag/kota için True
    plan: int | None
```

| Tür | Zincir (öncelik sırasıyla) | Not |
|---|---|---|
| llm | `claude_code` (görev defteri, çıkış 3) · `claude_api` (başsız; usd) · `kaset` (testler) | İ-6 |
| gozlemci | `claude_code` · `claude_api` · `sahte` | [GS] adı; `vlm` kalktı |
| gorsel | `gemini_paket` (ilk adaylar; elle-toplu) · `vertex_gorsel` ($; izinliyse düzeltmede önce) · `flow_gorsel` (Memmet; yalnız düzeltme; günlük tavan) · `sahte` | BK §6.3 #4, #9 |
| video | `flow` (Memmet; `elle`/`gece`) · `veo_vertex` ($; izin) · `kie` (varsayılan kapalı) · `sahte` · `sahte_bozuk` | kie: "gri abonelik havuzu" şüphesi [kaynak: BK §6.4] |
| tts | `ai84` · `sahte` | |
| ses_donustur | `rvc` · `openvoice` · `ai84_vc` (AI84; yalnız kritik replik) · `sahte` | Sıra motor kıyasından ([SM2] SB3) |
| ayristirma | `roformer` · `demucs` · `sahte` | [SM2] |
| asr | `faster_whisper` (+ stable-ts hizalama) · `sahte` | [SM2] |
| dudak | `musetalk` (yerel; 4 GB'ta ≈ 5 dk / 8 sn klip [kaynak: SM2 D-MT]) · `sahte` | Wav2Lip yasak [kaynak: A3 A1]; `fal_latentsync` çıkarıldı ([SM2] İ-4) |
| muzik | `acestep` · `midi_ornek` · `sahte` | `gemini_elle` yok ([SM2] İ-6) |
| dinleyici | (isteğe bağlı, ses girdili model API) | Anahtar yoksa atlanır |

**Kısıt davranış tablosu** (`hat/KISITLAR.md`'ye girer):
| Kod | Örnek | Hattın davranışı | Dış kod | Ders kaydı | Telegram |
|---|---|---|---|---|---|
| `olagandisi` | "Olağan dışı etkinlikler tespit ettik" (sayfada **ya da tek bir sonuç kartında**) | Memmet o anda durur. Bekleyen indirmeler yeni gönderimsiz toplanır. `FLOW_KILIDI.json` yazılır. İzinli yedek varsa yalnız **sonraki sahne grubundan** itibaren geçilir; yoksa durur. Kilidi yalnız `UYARI_GECTI.bat` kaldırır (İ-8 şartları) | 7 | evet | ACİL |
| `dogrulama` | reCAPTCHA, giriş istendi | Dur. Çözen kullanıcıdır; devamı kullanıcı `VIDEO_*.bat` ile başlatır [kaynak: BK §8 #7] | 2 | evet | ACİL |
| `kredi_bitti` | Gönder düğmesi pasif, "yetersiz kredi" | Dur; B2 yeniden hesaplanır | 5 | evet | ACİL |
| `arayuz` | Seçici yok, beklenmeyen sayfa | Dur; HTML+PNG kaydı; `memmet-bakimci` görevi; onarımdan sonra ilk blok `elle` | 3 → 2 | evet | ACİL |
| `filtre_red` | Politika reddi | **Aynı istem yeniden gönderilmez**; doğrudan yedek istem. Yedek de reddedilirse plan `reddedildi`, yönetmen onarım kipi | — | evet (kelime adayı) | toplu özet |
| `anahtar_yok` | Boş anahtar dosyası | Sağlayıcı zincirde atlanır | — | hayır | gerekiyorsa |
| `ag` / `kota` | Bağlantı koptu, 429 | Üstel bekleme, en çok 3 deneme. Dosya ffprobe ile doğrulanmadan iş tamam sayılmaz | — / 1 | 3. denemede | 3. denemede |
| `zaman_asimi` | Sonuç 360 sn'de gelmedi | Önce **topla** (iş geç bitmiş olabilir). Bulunamazsa `kayip` → kuyruk → BK → bir kez yeniden | — | evet | hayır |

**Yedeğe geçişin şartları (hepsi birden):** `FILM_AYAR.json → video_yedek_izinli` listesinde olmak · `usd` bütçesinin yetmesi · aynı ya da daha iyi
çözünürlük · sahne grubu sınırında başlamak · hat denetçisi notu.

#### 4.5.9 Kredi defteri, künye, üretim önizlemesi (değişti: dilimler ve gün planı)
`KREDI_DEFTERI.jsonl` (film başına, yalnız eklenir; her satır `fsync`):
```json
{"zaman":"2026-10-28T01:12:40+03:00","is":"V-142-d1-7f3a9c","plan":142,"tur":"video","saglayici":"flow","model":"omni-1.1-flash","cozunurluk":"720p","klip_sn":8,"deneme":1,"dilim":"taban","olay":"gonderildi","tahmini":12}
{"zaman":"2026-10-28T01:13:31+03:00","is":"V-142-d1-7f3a9c","olay":"indirildi","dosya":"SIRALI_VIDEO/142.mp4","sure_sn":8.0,"sha":"…","gercek":null}
```
`KUNYE/142.json`: `{plan, video, baslangic, bitis, istem_sha, saglayici, model, istem_bicimi, deneme, is, flow_medya_id, kapilar: {V1, V2, V3, ZK, S2m}, plan_imza, bayat}`.

`URETIM_ONIZLEME.json` (örnek):
```json
{"girdi_imza": "…",
 "kapilar": {"Z0":"GEC","K0":"GEC","HS_KAGIT":"GEC(8,8,9)","HS_PLAN":"GEC","S0":"GEC","ISTEM":"GEC","G1":"GEC","HS_ANIMATIK":"GEC(8,8,8)"},
 "plan": 495, "klip": 405, "zincir": {"bagimsiz": 312, "son_kare": 61, "bitis_sabit": 32},
 "kredi": {"flow": {"birim": 12, "taban": 4860, "pay": 0.30, "dilimler": {"goruntu": 729, "ses": 340, "kurgu": 389}, "toplam": 6318,
                    "bakiye": 9420, "bakiye_kaynagi": "flow_menu", "bakiye_zamani": "2026-10-27T20:02:00+03:00",
                    "sinir": 8478, "sonuc": "GEC"},
           "ai84": {"film_tahmin": 24000, "tavan": 60000, "seri_kurulum": {"tahmin": 0, "tavan": 40000}, "bakiye": 610000, "sonuc": "GEC"},
           "usd": {"toplam": 0.0, "tavan": 0.0, "sonuc": "GEC"}},
 "gun_plani": {"flow_gorsel_gunleri": ["2026-10-24", "2026-10-25"],
               "video_oturumlari": [{"tarih": "2026-10-27", "en_erken": "21:00", "pilot": true}, {"tarih": "2026-10-28", "en_erken": "20:00"}],
               "flow_sure_saat": 12.9},
 "pilot": {"planlar": [3, 7, 12, 41, 42], "durum": "bekliyor"},
 "uyarilar": ["Bugün Flow'a 12 görsel gönderildi; video en erken yarın 08:40."],
 "hat_denetcisi": "_RAPOR/HAT_FILM.md", "karar": "GEC"}
```
`sinir` = bakiye × (1 − güvenlik payı 0,10) [tahmin]. `URETIM_ONIZLEME.md` aynı bilginin 1 sayfalık Türkçe özetidir.

#### 4.5.10 Flow yük ve tempo dosyaları, blok planı, Memmet çıkışı (yeni)
Hesap düzeyindeki dosyalar veri kökündedir (`<veri_kok>/HESAP/`), filmden bağımsızdır ve git'e girmez.
`FLOW_YUK.jsonl` (yalnız eklenir):
```json
{"zaman":"2026-10-24T22:41:05+03:00","hesap":"ultra_1","film":"F20261024_ejderha","tur":"gorsel","plan":212,"mod":"elle","cikti_sayisi":2}
```
`FLOW_TEMPO.json`:
```json
{"hesap": "ultra_1", "mod": "gece", "son_gonderim": "2026-10-28T01:12:40+03:00", "sonraki_izinli": "2026-10-28T01:13:05+03:00",
 "ara_mola": {"her": 8, "sayac": 5, "bitis": null}, "blok_mola": {"her": 2, "sayac": 1, "bitis": null},
 "gunluk": {"tarih": "2026-10-28", "gorsel": 0, "video": 112}, "son_gorsel_gonderimi": "2026-10-25T23:10:00+03:00",
 "yavaslatma_carpani": 1.0, "son_uyari": "2026-10-19T00:57:00+03:00"}
```
`FLOW_KILIDI.json` (yalnız uyarıda var):
```json
{"neden": "olagandisi", "zaman": "2026-10-28T02:31:00+03:00", "film": "F20261024_ejderha", "plan": 213, "topla_yapildi": true,
 "kaldirma": {"elle_1_video_basarili": false, "en_erken": "2026-10-28T03:01:00+03:00", "gecerli_gun": null}}
```
`FILMLER/<film>/BLOK_PLANI.json`:
```json
{"onizleme_imza": "…", "bloklar": [{"no": 8, "planlar": [151, 152, 153], "durum": "gonderiliyor", "baslangic": "…"}],
 "uygun_bekleyen": [160, 161], "bagimli_bekleyen": {"143": "kaynak 141: V3 sırada"}}
```
`FILMLER/<film>/_memmet_cikis.json` (Memmet her çıkışta yazar; flow.py okur):
```json
{"kod": "tamam", "blok": 8, "gonderilen": [151, 152], "indirilen": [151, 152], "bekleyen": [], "reddedilen": [],
 "bakiye_okunan": 9408, "zaman": "…"}
```
**Dünya defteri notu (değişti):** `DUNYA_DEFTERI.json`'ın şeması süreklilik uzmanınındır. Tur 1 örneğimdeki `kadraj` alanı kaldırıldı:
durum yalnız olgudur ([YN2] İ-1). Benim şartım yalnız zarf, imza ve "planlanan / gözlenen" ayrımının korunmasıdır.

#### 4.5.11 Ders defteri (kendi kendine öğrenen; otomatik kayıt biçimi) (değişti)
**Ham kayıt** (olay başına bir dosya): `YZ_FILM/BILGI/DERSLER/ham/20261028-011540_F20261024_V2-142.json`
```json
{"id": "D-20261028-011540-a1b2", "zaman": "2026-10-28T01:15:40+03:00", "film": "F20261024_ejderha", "seri": "FROSTHOLLOW", "ortam": "yerel",
 "olay": "kapi_hatasi", "asama": "A14", "kapi": "V2", "madde": "V2.kimlik_kaymasi", "plan": 142,
 "kategori": "yuz_degisti", "rol_etiketi": ["sureklilik-denetcisi", "yonetmen"],
 "belirti": "SFace 0.29 (kart mara@2), ilk kareye göre -0.21",
 "olcum": {"sface": 0.29, "esik": 0.363},
 "baglam": {"plan_tipi": "aksiyon", "hareket_tipi": "yörünge", "kadraj": "OY", "referans": ["mara"], "isik": "gece",
            "saglayici": "flow", "model": "omni-1.1-flash", "istem_bicimi": "aralik", "zincir": "son_kare", "derinlik": 1},
 "kanit": ["_RAPOR/V2_B07.json#142", "SIRALI_VIDEO/142.mp4"],
 "eylem": "yeniden_cekim:yedek_istem", "sonuc": null, "maliyet": {"flow_kredi": 12}}
```
- `olay` sözlüğü: `kapi_hatasi, kapi_bayragi_dogrulandi, saglayici_red, saglayici_kisit, yeniden_cekim, kullanici_notu, seyirci_bulgusu,
  butce_sapmasi, arac_hatasi, yanlis_alarm, kacirma, pilot_olcumu`.
- `kategori` = `veri/kok_neden.json` (§4.5.6). Yeni kategoriyi yalnız `ders-editoru` önerebilir; betik ekler.
- `baglam` alanını yönetmenin `plan_ozellik.py`'si doldurur ([YN2] Ç-20).
- **`sonuc` sonradan kendiliğinden dolar:** aynı planın sonraki denemesi kapıdan geçerse `duzeldi`, geçmezse `duzelmedi`, plan değiştiyse `plan_degisti`.
- **Kim yazar:** her kapı betiği, Memmet, sağlayıcılar, `notlari_oku.py`, `seyirci_karar` ortak `ders_defteri.kaydet(...)` işlevini çağırır.
  Kayıt yazılamazsa iş durmaz; uyarı loglanır.
- `DERS_DEFTERI.jsonl` ham kayıtlardan türetilen dizindir, git'e girmez.

**Öğrenilmiş kurallar:** `YZ_FILM/BILGI/DERSLER/KURALLAR_OGRENILEN.json`
```json
{"surum": 8, "kurallar": [
 {"id": "OK-0003", "tur": "filtre_kelimesi", "kapsam": "hareket_istem", "deger": "cradle", "etki": "UYARI→HATA",
  "destek": 4, "karsi": 0, "film_sayisi": 2, "kanit": ["D-…"], "durum": "aktif", "gerekce": "…", "geri_al": "kelimeyi listeden çıkar"},
 {"id": "OK-0011", "tur": "istem_eki", "kosul": {"kadraj": "OU"}, "deger": "the foreground person seen from behind keeps {SAC} and {KOSTUM}",
  "durum": "deneme", "deneme": {"grup": "cift_plan_no", "hedef_plan": 40, "uygulanan": 12, "hata_oran_once": 0.18, "hata_oran_sonra": null}},
 {"id": "OK-0014", "tur": "flow_tavan", "anahtar": "flow.gorsel_gunluk_tavan", "deger": 15, "eski": 20, "yon": "dusur", "durum": "aktif"}]}
```
- **İzinli `tur` değerleri:** `filtre_kelimesi, yasak_fiil, risk_desen, esik, tempo (yalnız yavaşlat), flow_tavan (yalnız düşür), kredi_payi,
  sure_tahmini, istem_kalibi, istem_eki, plan_kurali, yasak_kalip, yol_kurali, kara_liste, saglayici_notu`.
- **Yaşam döngüsü:** `aday → deneme → aktif → pasif`. Deneme: uygun planların yarısına uygulanır (plan numarası tek/çift), hata oranları karşılaştırılır
  [kaynak: GS §8.7; plan sayısı tahmin].
- **Terfi eşiği** [tahmin]: destek ≥ 3 ve ≥ 2 filmde (ya da tek filmde ≥ 5); hikâye etiketli derslerde en az 2 film [kaynak: SN2 §2.8]; önerilen
  eylemin başarısı ≥ 2/3. **Emeklilik:** karşı kanıt ≥ destek → `pasif`.
- **Korkuluklar** (`--uygula` reddeder): tempo hızlandırma; Flow tavanını yükseltme; bot, uyarı, gizli bilgi, onay ya da silme ile ilgili
  herhangi bir kural; etiketli kalibrasyon kanıtı (kaçırma ≤ %10 [kaynak: A2 §7]) olmadan bir eşiği gevşetmek; SFace HATA eşiğini 0,363'ün altına
  indirmek [kaynak: GS §7.9].
- Her kural ham kayıtlara bağlıdır. Kural değişince `surum` artar, doğrulayıcı imzaları değişir, kâğıt kapıları yeniden koşar.
- Rol etiketli talimat dersleri `DERSLER_AKTIF.md`'ye girer ve [CM]'nin `SubagentStart` kancasıyla ilgili ajana verilir. Kör rollere ders verilmez.

#### 4.5.12 Ayar dosyaları (değişti: iki kök)
- **`<depo>/YOLLAR.json`** (git'e girmez; `YOLLAR.ornek.json` girer). Gizli değil, makineye özel. `.claude/bin/film.py` kökleri buradan bulur;
  yoksa `YZ_FILM_VERI` ortam değişkeni; o da yoksa bulut düzeni (`<depo>/YZ_FILM`).
```json
{"depo_kok": "C:\\Users\\Soysal\\Desktop\\YZ_FILM_SET", "veri_kok": "C:\\Users\\Soysal\\Desktop\\YZ_FILM",
 "evren_kok": "C:\\Users\\Soysal\\Desktop\\YZ_FILM\\EVREN", "arsiv": "D:\\YZ_FILM_ARSIV",
 "gemini_paket": "C:\\Users\\Soysal\\Desktop\\GEMINI GORSEL ISTEM",
 "capcut_taslak": "%LOCALAPPDATA%\\CapCut\\User Data\\Projects\\com.lveditor.draft",
 "ses_kutuphanesi": "C:\\Users\\Soysal\\Desktop\\YZ_FILM\\SES_KUTUPHANESI",
 "openmontage": "C:\\Users\\Soysal\\Desktop\\YZ_FILM\\OpenMontage",
 "arsiv_klipler": "D:\\YZ_FILM_ARSIV\\PROJE_B2\\PROJE_B2\\SIRALI_VIDEO",
 "python": {"ana": "py -3.10", "py312": "py -3.12"},
 "ortamlar": {"rvc": "…\\venv_rvc\\Scripts\\python.exe", "openvoice": "…", "musetalk": "…", "acestep": "…"}}
```
- **`<veri_kok>/AYARLAR/FILM_AYAR.json`** (gizli değil, makineye özel; git'e `FILM_AYAR.ornek.json` girer):
```json
{"ortam": "otomatik", "mod": "tam_otomatik",
 "saglayicilar": {"llm": ["claude_code"], "gozlemci": ["claude_code"], "gorsel": ["gemini_paket", "flow_gorsel"],
                  "video": ["flow"], "video_yedek_izinli": [], "tts": ["ai84"], "ses_donustur": ["rvc", "openvoice"],
                  "ayristirma": ["roformer", "demucs"], "asr": ["faster_whisper"], "dudak": ["musetalk"],
                  "muzik": ["acestep", "midi_ornek"], "dinleyici": []},
 "flow": {"mod": "elle", "gece_izni": false, "model": "omni-1.1-flash", "cozunurluk": "720p",
          "gorsel_gunluk_tavan": 20, "gorsel_sonrasi_video_saat": 12},
 "butce": {"flow_kredi_tavan_film": null, "guvenlik_payi": 0.10, "ai84_kredi_tavan_film": 60000,
           "ai84_seri_kurulum_tavan": 40000, "usd_tavan_film": 0},
 "ajan": {"paralel_max": 5},
 "bildirim": {"telegram": true},
 "yayin_kaynagi": "capcut",
 "indirme_izni": {"cc0_efekt": false},
 "fiyat_olcum": {}}
```
- Varsayılanlar kullanıcıya soru sormadan güvenli çalışır: Flow tavanı `null` = okunan bakiye; dolar tavanı 0 = ücretli yedek kapalı; gece modu kapalı;
  Flow görsel tavanı 20.
- Bu ayarları **açmak ya da gevşetmek kurulum kararıdır**, film başına soru değildir. Makine yalnız sıkılaştırabilir (§4.5.11 korkulukları).
- Anahtar dosyaları (`ai84_anahtar.txt`, `telegram_bot.txt`, `kie_anahtar.txt`, `anthropic_anahtar.txt`, `freesound_anahtar.txt`, YouTube OAuth)
  yalnız `<veri_kok>/AYARLAR/`'da durur. Depodaki `YZ_FILM/AYARLAR/` anahtar dosyaları boş kalır (CLAUDE.md Kurallar).

#### 4.5.13 Bildirim olayları (Telegram) (değişti)
Ortak `bildirim.py` tek yerdir; Memmet ve `film.py` aynı işlevi çağırır. Anahtar `AYARLAR/telegram_bot.txt` (1. satır bot, 2. satır sohbet numarası)
ya da `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID`. Mesaja anahtar, yol içindeki kullanıcı adı ya da URL imzası yazılmaz; gönderilmeden önce maskelenir (T11).

| Olay | Seviye | Örnek metin | Tekrar kuralı |
|---|---|---|---|
| `kisit_olagandisi` | ACİL | "[EJDERHA] Flow 'olağan dışı etkinlik' dedi. Memmet durdu, 212/405 video hazır. Flow'da elle 1 video dene; olursa en erken 03:01'de UYARI_GECTI.bat." | olay başına 1 |
| `dogrulama` | ACİL | "Flow doğrulama istiyor. Memmet penceresinde sen çöz, sonra VIDEO_YARI_OTOMATIK.bat." | 30 dk'da 1 [tahmin] |
| `kullanici_isi` | BİLGİ | "Gemini paketi P1_ANA_03 hazır: … (ZIP'i GELENLER'e koy, gerisini ben yaparım)" | iş başına 1, 6 saat sonra 1 hatırlatma |
| `blok_hazir` **(yeni)** | BİLGİ | "Blok 8/27 hazır (20 plan). Memmet penceresinde sırayla GÖNDER'e bas." (yalnız `elle` mod) | blok başına 1 |
| `butce` | ACİL | "Video için 6.318 kredi gerekiyor, hesapta 4.900 var. Film kısaltılmadı, hat bekliyor." | olay başına 1 |
| `kapi_tukendi` | ACİL | "Animatik 3 turda 7/8/7 aldı; video başlamadı. En zayıf: ritim. Ayrıntı: _RAPOR/…" | olay başına 1 |
| `asama_bitti` | BİLGİ | "Animatik P2 seyirci: 8/8/9 — geçti." | yalnız önemli aşamalar (A06, A12, A14a, A14 bitişi, A16, A17) |
| `oturum_ozeti` | BİLGİ | "Gece özeti: 186 klip, 2.232 kredi, 21 yeniden çekim; sonraki oturum en erken yarın 20:00." | oturum başına 1 |
| `sinir_doldu` **(yeni)** | BİLGİ | "Claude kullanım sınırı doldu; açılınca DEVAM yazman yeterli, iş dosyada." | 6 saatte 1 |
| `hata` | ACİL | "film.py hata verdi (A14). Kayıt: FILM_KAYIT.txt." | 30 dk'da 1 |

- Aynı `(olay, film, asama)` 30 dk içinde ikinci kez gönderilmez; saatte en çok 12 mesaj [tahmin]. Gerekçe: "Telegram tekrar mesajları" sorunu [kaynak: H/uretim-hatti-v2].
- Bulutta Telegram kapalıdır; anahtar bulutta yoktur, mesaj yalnız loga yazılır.
- İsteğe bağlı (P3): kayıtlı sohbetten gelen `/durum` ve `/dur`. `/dur` yalnız `DUR` dosyası yazar.

#### 4.5.14 Bulut ↔ yerel taşıma: `film.py esitle` (yeni)
| Yön | Komut | Ne yapar |
|---|---|---|
| bulut → git | `film.py esitle --gonder` | Beyaz listedeki dosyaları ekler, anahtar deseni taraması yapar, ayarlı dala commit ve push eder |
| git → yerel | `GUNCELLE.bat` = `git pull --ff-only` + `film.py esitle --al` | Depodaki kâğıt dosyalarını veri kökündeki film klasörüne kopyalar |
| yerel → git (isteğe bağlı) | `film.py esitle --gonder` | Yerelde biten kâğıt aşamalarını bulut oturumuna taşır |

- **Beyaz liste** (film klasörü içinde, yalnız metin): `00_KONU.md`, `PROJE_KARARLARI.md`, `kararlar/*.json`, `_HIKAYE_ODASI/**/*.{md,json}`,
  `30_YONETMEN/**/*.json`, `35_SES/**/*.json`, `SAHNELER.json`, `HIKAYE.json`, `DUNYA_DEFTERI.json`, `MUZIK/muzik_listesi.json`, `_KARTLAR/*.json`,
  `KUYRUK/*.json`, `_RAPOR/*.{json,md}`, `URETIM_ONIZLEME.json`. Film dışında: `EVREN/<SERI>/**/*.json`, `BILGI/DERSLER/ham/*.json`, `KURALLAR_OGRENILEN.json`.
- **Asla taşınmaz:** `AYARLAR/`, bütün görsel/ses/video, `_GOREV/`, `FILM_DURUM.json`, kilitler, `KREDI_DEFTERI.jsonl`, `HESAP/`.
- **Çakışma kuralı:** hedefte dosya varsa ve zarf imzaları farklıysa hedefteki **daha sonraki bir aşamanın girdisiyse dokunulmaz** ve çakışma raporu yazılır.
  Aksi hâlde eski dosya `_ESKI/esitle_<zaman>/`'a taşınır, yenisi konur. Sessiz üzerine yazma yoktur (M16, T24).

#### 4.5.15 Yerel ağır iş kuyruğu ve GPU kilidi (yeni)
`<veri_kok>/YEREL_IS/kuyruk.jsonl` + `GPU.kilit`:
```json
{"id": "YI-142-V2", "film": "F20261024_ejderha", "komut": "video_denetim.py --klip 142", "ortam": "ana", "gpu": true,
 "oncelik": 1, "durum": "bekliyor", "deneme": 0, "neden": "blok_arasi_zincir"}
```
- Aynı anda tek `gpu: true` iş [kaynak: SM2 SB0 kuralı, tahmin]; CPU işleri paralel (en çok çekirdek − 2 [tahmin]).
- Öncelik: (1) blok arası zincir işleri (sonraki bloğu besler) > (2) V2/V3 > (3) ses (ayrıştırma, dönüşüm) > (4) müzik, dudak senkronu.
- Bellek hatasıyla düşen iş bir kez yeniden denenir; yine düşerse `OLCULEMEDI` (BAYRAK) olur ve ders kaydı `gpu_bellek` yazılır.
- Ağır modeller ayrı sanal ortamlarda koşar (`YOLLAR.json → ortamlar`); ana Python 3.10 ortamı bozulmaz ([SM2] SB0, mevcut `om_kopru.py` kalıbı).

### 4.6 Yazılması / değişmesi gereken kod (araç, ne yapar, girdi/çıktı, öncelik)

#### 4.6.1 Mevcut kodda bulduğum somut sorunlar (önce bunlar; bu turda yeniden okundu)
| # | Yer | Sorun | Neden önemli | Düzeltme |
|---|---|---|---|---|
| S1 | `memmet.py` `DOGRULAMA_KELIMELERI` + `kontrol_noktasi()` | "olağan dışı etkinlik" ve "unusual activity" **doğrulama** sayılıyor. Memmet 12 saate kadar bekliyor; metin kaybolunca **kendiliğinden devam ediyor** | Kesin kural ihlali [kaynak: BK §6.2 #1] | Ayrı `OLAGANDISI_KELIMELERI`; bulunduğu anda `Durdur(kod="olagandisi")` + `FLOW_KILIDI.json`. reCAPTCHA da durur (§4.5.8) |
| S1b **(yeni)** | `memmet.py` `HATA_KELIMELERI` ("olağan", "unusual") + `asama()` | **Tek bir sonuç kartında** "olağan dışı" yazısı görülünce bu bir "Flow reddetti/hata" sayılıyor ve plan `kuyruk.append(s)` ile **yeniden gönderiliyor** | Uyarıdan sonra yeni gönderim: M8 ve kesin karar 5 ihlali | Kart düzeyindeki uyarı metni de `olagandisi` kısıtıdır; "olağan"/"unusual" `HATA_KELIMELERI`'nden çıkar |
| S2 | `yeni_film.py` → `MEMMET_BASLAT.bat`, `MEMMET_SADECE_VIDEO.bat`, `FILM_HATTI.bat`; `memmet.py calis()` → `kurgu()` | Memmet doğrudan çalıştırılınca **bütün kapıları atlıyor**, video kredisi harcıyor, sonra seslendirme ve CapCut zincirini kendisi kuruyor | M3 kodla sağlanmalı | Memmet gönderimi yalnız `--blok … --onizleme <imza>` ile; imza `URETIM_ONIZLEME.json` ile uyuşmazsa reddeder. Her planın G1 sha'sını yüklemeden önce doğrular ([GS] A12). Eski `.bat`'lar kalkar; `kurgu()` zinciri kalkar; `komut_kapisi` doğrudan çağrıyı reddeder (§4.4.3) |
| S3 | `memmet.py` `VARSAYILAN` | `video_cozunurluk: "360p"`; gönderim arası 4–12 sn; ara mola yok; 2–3 partide 5–15 dk | 720p kesin karar [kaynak: BK §8 #1]; 17.10 tempo [kaynak: BK §8 #6] | 720p; gece 12–30 sn, gündüz 6–15, aynı anda 2, 8 gönderimde 3–6 dk, 2 blokta 15–30 dk |
| S4 | `memmet.py istemler()` | `[ana, ana, yedek]`: politika reddinden sonra **aynı istem bir kez daha** gönderiliyor | Gönderim sayısını ve kredi riskini boşuna artırır (reddin kredi harcayıp harcamadığı bilinmiyor, Q2) | `filtre_red` → doğrudan yedek; aynı istemle ikinci deneme yalnız teknik hatada |
| S5 | `memmet.py asama()` zaman aşımı dalı | Zaman aşımında sonuç kontrol edilmeden `kuyruk.append(s)` | İlk iş geç bitebilir → **çift harcama** | Önce `kutu_bul` + `memmet_topla` ile ara; bulunamazsa `kayip` → kuyruk → BK → bir kez |
| S6 | Depodaki `memmet.py` | Bu sürüm **eski**. Kullanıcıdaki memmet3'te `--mod elle\|gece`, `--tek-tek`, `flow-prompt-box`, `/asb/` adresi, "Bitir" yuvası doğrulaması, 720p var; ama gece modunda uyarıda 5 kez sayfa yenileyip **deniyor** [kaynak: BK §8 #5] | Depodaki sürüme yapılan düzeltme çalışan sürümü ezer ya da tersine memmet3 gelince 5 deneme geri gelir | **P0, ilk iş:** memmet3 (ve D arşivindeki B2/B3 betikleri) depoya alınır, 5 deneme davranışı silinir, sonra S1–S5, S14–S15 |
| S7 | `film.py onay()` | `input()` kullanıyor. Claude Code'un Bash aracında stdin yok → EOF → hep `Durdur` | Ajanla yürütülen hatta kredili aşama hiç geçemez; ya da `--tam-otomatik` bütün güvenceyi kaldırır | `onay()` kalkar; yerine bütçe noktaları ve kullanıcının çift tıkladığı `VIDEO_*.bat` |
| S8 | `film.py kaydet()` ve `json.dump(open(…,"w"))` her yerde | Atomik değil, kilit yok | Elektrik kesilince durum bozulur; iki süreç çift harcama yapabilir | `atomik_yaz()`, `FILM.kilit`, `FLOW.kilit`, `DUR` |
| S9 | `film.py imza()` | Aşama düzeyinde imza; bir planın istemi değişince video yeniden üretilmiyor | Düzeltilen plan eski videoyla kalır, sessizce yanlış kurgulanır | Plan bazında `plan_imza` + `bayat` + kuyruk (§4.5.7) |
| S10 | `ai84.py` başlangıcı | Anahtar yoksa **içe aktarırken `SystemExit`** | Bulutta ya da testte `import ai84` süreci öldürür | Anahtar ilk çağrıda okunur; yoksa `AI84Error("anahtar_yok")` |
| S11 | `istem_denetim.py` | Sabit listeler; 8 sn klipte replik sınırı 20 kelime; öğrenilen kurallar okunmuyor; replik metni taranmıyor ([SN1] §6) | ZN/RE: 8 sn'de ≤ 16 [kaynak: RE `replik_max_kelime_8sn`] | Eşikler `esikler.py`'den; rapor §4.5.4 biçiminde; replik ve `veo_ses_tarifi` de taranır |
| S12 | `yeni_film.py` `.bat`'ları | `python` çağırıyor | ".bat'lar tam Python yolu kullansın" [kaynak: H/uretim-hatti-v2] | `py -3.10` (yoksa `python`); depo yolu `.bat` kurulurken mutlak yazılır |
| S13 | `saglayicilar/flow.py` | Memmet çıkış 2 → tek tür `Kisitlandi` | Hat "olağan dışı" ile "giriş yapılmamış"ı ayıramıyor | `_memmet_cikis.json` okunur → `Kisitlandi(kod=…)` |
| S14 **(yeni)** | `memmet.py calis()` | `sonraki_mola` ve son gönderim zamanı yalnız bellekte | Memmet kapanıp açılınca mola sıfırlanır: **istemeden tempo hızlanır** | `FLOW_TEMPO.json` (§4.5.10); Memmet açılışta kalan molayı bekler (T21) |
| S15 **(yeni)** | `memmet.py calis()` partiler döngüsü | Mola "2–3 partide bir" sayılıyor ve `parti` 20'lik blok varsayılıyor | Yeni şemada `parti` = hikâye partisi (≈ 165 plan). Memmet değişmeden yeni `SAHNELER.json` görürse 165 planlık "parti"lerde blok molası neredeyse hiç olmaz: **tempo hızlanır** | Memmet `parti` okumayı bırakır; yalnız `film.py`'nin verdiği `BLOK_PLANI`'yla çalışır. Yeni şema, Memmet blok moduna geçmeden kullanılamaz (sürüm alanı + test T31) |

#### 4.6.2 Yeni ya da yeniden yazılacak araçlar (benim alanım)
| Öncelik | Araç | Ne yapar | Girdi → Çıktı |
|---|---|---|---|
| P0 | `memmet.py` (memmet3 tabanlı) | S1–S6, S14–S15; `--blok` ve `--onizleme`; `--bakiye` (Flow menüsünden salt okuma [doğrulanmadı: FK "kredi bilgisi menünün altında"]); `KREDI_DEFTERI` ve `FLOW_YUK` yazımı; `_memmet_cikis.json`; `--mod elle` (insan basar) ve `gece` (yalnız `gece_izni`) | `BLOK_PLANI` + görseller → videolar |
| P0 | `memmet_topla.py` | Yeni gönderim yapmadan biten sonuçları indirir; `KREDI_DEFTERI` ile eşleştirir | Flow projesi → `SIRALI_VIDEO` |
| P0 | `ARACLAR/film.py` v2 + `.claude/bin/film.py` ([CM] K-1) | Aşama kaydı, görev üretimi ([CM] ile), `sonraki/basla/calis/bitir/kurtar/ozet/goster/yeni/asamalar/esitle/oturum/yurut`, çıkış kodları, zarf ve imza, kilitler, DUR, ortam algılama. Mevcut `test_film.py` bozulmaz | film klasörü → görevler, durum |
| P0 | `ortak.py` | `atomik_yaz`, `jsonl_ekle(fsync)`, `imza`, `kilit`, `ortam`, `yollar` (iki kök), `maskele`, `ffprobe_sure` | — |
| P0 | `saglayicilar/` genişletme | Türler, `Kisitlandi.kod`, `birim_fiyat`, `bakiye`, `elle`, `gpu`, `ortam`; `claude_code`, `kaset`, `sahte_bozuk` | — |
| P0 | `flow_yuk.py` | `FLOW_YUK`, `FLOW_TEMPO`, `FLOW_KILIDI` kütüphanesi: `izinli_mi(tur)`, `bekle_bitis()`, `gonderim_kaydet()`, günlük tavan, görsel→video beklemesi, `UYARI_GECTI` şartları | hesap dosyaları |
| P0 | `kredi.py` | B0 (`--sure-sec`), B1, B2 (`--kesin`), BK (`kuyruk.py` sorar), dilimler, gün planı, `URETIM_ONIZLEME.json/.md`, `KREDI_DEFTERI` yardımcıları, AI84 `estimate()` ile birim fiyat | plan + bakiyeler → önizleme |
| P0 | `bildirim.py` | Telegram + Windows balonu + ses; tekrar engeli; maskeleme; bulutta sessiz | olay → mesaj |
| P0 | `ders_defteri.py` | `kaydet()`, `--derle`, `--uygula` (korkuluklar, deneme), `kurallar()` | olaylar → `BILGI/DERSLER/` |
| P0 | `esikler.py` ([SN2]) | Bütün eşik dosyalarını ve öğrenilen kuralları birleştirir; çift anahtar → HATA; sürüm özeti | → doğrulayıcılara sözlük |
| P0 | `blok_plani.py` | Uygunluk kuralı, blok doldurma, sahne sınırı, yeniden çekimlerin yerleştirilmesi, derinlik ve yeniden demirleme isteği | SAHNELER + raporlar + kuyruk → `BLOK_PLANI.json` |
| P1 | `film.py esitle` | Beyaz liste, anahtar taraması, çakışma kuralı (§4.5.14) | depo ↔ veri kökü |
| P1 | `yerel_is.py` | Ağır iş kuyruğu ve GPU kilidi (§4.5.15); film.py blok aralarında besler | iş → sonuç + kayıt |
| P1 | `pilot_sec.py` + pilot raporu çatısı | Kapsama kuralıyla pilot planları seçer; uzmanların ölçülerini `PILOT_FILM.json`'da toplar | SAHNELER → pilot listesi, rapor |
| P1 | `kapi.py` (ortak çatı) | Kapı raporu yazıcı (§4.5.4), `OLCULEMEDI`'nin BAYRAK sayılması, kuyruk maddesi üretimi, ders kaydı. Kural içerikleri uzmanlarda | — |
| P1 | `saglayicilar/gemini_paket.py` sarmalayıcısı | Paket içeriği görüntü uzmanının `gemini_paket.py`'sinde; ben sağlayıcı arayüzünü, basamaklı paket kuyruğunu ve `kullanici_isi` görevini yazarım | paket → `GELENLER/` algılama |
| P1 | `saglayicilar/veo_vertex.py` | Resmî Veo API: başlangıç karesi, `last_frame`, `seed`, `duration_seconds`, `resolution` [kaynak: A2 §2.1]. Fiyat ayardan | — |
| P2 | `saglayicilar/claude_api.py` + `film.py yurut --basliksiz` | Başsız yürütme (İ-6); `claude-opus-5-5`, effort high; şema doğrulaması; maliyet satırı | görev → `CIKTI/` |
| P2 | `saglayicilar/vertex_gorsel.py` | Ücretli düzeltme görseli (≈ 0,134 $/görsel [kaynak: GS, 06_SERVISLER]); `usd_tavan` > 0 ise | — |
| P2 | `arsivle.py` | `robocopy /E /MOVE`; taşınan listesi; son taslağın bağlı olduğu dosyaları atlar | → `D:\YZ_FILM_ARSIV\<FİLM>\` |
| P3 | Telegram gelen komutlar; `kie` sağlayıcısı (yalnız kullanıcı izni gelirse) | — | — |

#### 4.6.3 Windows ve `.bat` kullanımı (değişti)
**İlkeler**
- Her `.bat` ASCII ve CRLF'dir; ilk satırları `chcp 65001 >nul` ve `cd /d "%~dp0"`. Python `py -3.10`, launcher yoksa `python`.
- Türkçe mesajı `.bat` yazmaz, **Python yazar**. `.bat` yalnız çalıştırır ve `pause` ile bekler.
- Her `.bat` tek iş yapar ve çift tıklamak güvenlidir (kilit, kaldığı yerden devam).
- Film klasörü veri kökünde olduğu için `.bat` depodaki `.claude\bin\film.py`'yi **mutlak yolla** çağırır. Yol `yeni_film.py` tarafından yazılır;
  depo taşınırsa `GUNCELLE.bat` `.bat`'ları yeniden üretir (`film.py bat-yenile`).

| Dosya | Yer | Ne yapar |
|---|---|---|
| `KURULUM.bat` | depo kökü | `kurulum.py`: paketler, ayrı ortamlar, modeller, `YOLLAR.json`, testler (§4.6.4) |
| `GUNCELLE.bat` | depo kökü | `git pull --ff-only` + `film.py esitle --al` + `bat-yenile`; git yoksa ne yapılacağını yazar |
| `FLOW_GIRIS.bat` | depo kökü | Memmet Chrome'unda Google girişi (eski `MEMMET_GIRIS.bat`; hesap düzeyinde) |
| `UYARI_GECTI.bat` **(yeni)** | depo kökü | Flow kilidini İ-8 şartlarıyla kaldırır; şart yoksa nedenini yazar |
| `TELEGRAM_TEST.bat` | depo kökü | Deneme mesajı |
| `DEVAM.bat` | film | `film.py calis`: bir sonraki ajan, kullanıcı ya da bekleme işine kadar yürür; Claude yoksa ne yapılacağını yazar |
| `DURUM.bat` | film | `film.py ozet --kullanici`: Türkçe tablo, sıradaki iş, BEKLE bitişi |
| `DURDUR.bat` | film | `DUR` dosyası yazar |
| `VIDEO_YARI_OTOMATIK.bat` | film | `film.py oturum --video --mod elle` (Memmet hazırlar, GÖNDER'e kullanıcı basar) |
| `VIDEO_GECE.bat` | film | `--mod gece`; yalnız `gece_izni: true` ise kurulur |
| `VIDEO_TOPLA.bat` | film | `memmet_topla.py`: gönderimsiz toplar |
| `NOTLARI_OKU.bat` | film | CapCut notları → `film-not` akışı + ders kaydı |
| `ARSIVLE.bat` | film | `arsivle.py` |
| `FILM_DENEME_SAHTE.bat` | film | Bütün hat sahte ve kaset sağlayıcılarla (kredisiz) |

- **Kaldırılanlar:** `MEMMET_BASLAT.bat`, `MEMMET_SADECE_GORSEL.bat`, `MEMMET_SADECE_VIDEO.bat`, `CAPCUT_PROJESI_OLUSTUR.bat`, `FILM_HATTI.bat` (kapı
  deliği ve `input()` onayı, S2 ve S7). `KONTROL.bat` elle indirme yolu için kalır; çıktısını `SIRALI_GORSEL/_ADAYLAR/`'a koyar ([GS] §6.2).
- `GEMINI_AL.bat` gerekmez: ZIP `GELENLER/`'e düşünce algılama kendiliğinden ([CM] `algilama: dosya_var`).
- Kullanıcı belgesi `BASLA_BURADAN.txt` yeniden yazılır. Ana mesajı: "Claude'u YZ_FILM_SET klasöründe aç ve konuyu söyle. Senden istenen her iş
  Telegram'a ve ekrana tek cümle olarak gelir; hangi `.bat`'a basacağın orada yazar."

#### 4.6.4 Kurulum (`kurulum.py` ekleri)
- **Python:** ana 3.10 (var). `py -3.12` aranır; yoksa kurulum raporu bunu kullanıcının tek seferlik işi olarak yazar ve ses ortamlarının basamakları
  kapalı görünür ([SM2] SB0 ilkesi).
- **Ayrı sanal ortamlar:** `venv_rvc` (3.12), `venv_openvoice`, `venv_musetalk` (3.10 + torch 2.0.1), `venv_acestep` (3.11–3.12) [kaynak: SM2 D-*].
- **Ana ortam paketleri:** `scenedetect==0.7.2` [kaynak: GS], `pyloudnorm`, `stable-ts`, `faster-whisper`, `audio-separator`, `jsonschema` [kaynak: SN1],
  `mediapipe` (sürüm görüntü uzmanıyla; OpenMontage'ın kendi ortamındaki 0.10.14'e dokunulmaz [kaynak: BK §7.11]).
- **Modeller:** YuNet ve SFace (opencv_zoo, Apache-2.0), MediaPipe `.task`, DINOv2-small, OWLv2-base [kaynak: GS §6.2]. İlk indirmeden sonra
  `HF_HUB_OFFLINE=1`.
- **Denetimler:** `git` var mı (yoksa yalnız yerel tek kök); C'de ≥ 20 GB boş yer [tahmin]; `claude --version` ≥ 2.1.271 [kaynak: CM R-5];
  kanca komutu ve `!` komutunun Windows'ta `python` bulması [kaynak: CM §9.4].
- **`YOLLAR.json`:** `Desktop\YZ_FILM` varsa veri kökü odur (soru sorulmaz); yoksa kurulur. `HESAP/` ve `YEREL_IS/` klasörleri açılır.
- **Sonunda:** `python -m unittest discover -s YZ_FILM/ARACLAR/testler` çalışır ve sonucu rapora yazar.

#### 4.6.5 Testler (sahte ve kaset sağlayıcılarla, ağsız ve kredisiz)
İki örnek film olur. Mevcut `ORNEK_3_SAHNE` geriye uyumluluk için olduğu gibi kalır. Yeni `ORNEK_3_SAHNE_TAM` kâğıt çıktılarıyla gelir; ajan görevleri
`kaset` sağlayıcısının kayıtlı yanıtlarıyla ([CM]'nin "sahte ajan" dosyaları) geçer.

| # | Test | Neyi kanıtlar |
|---|---|---|
| T1 | Uçtan uca (`kaset` + `sahte`): A00 → A18 | Bütün aşamalar sırayla; çıkış 0; her çıktıda zarf |
| T2 | Her aşamanın ortasında kesme (`kes_sonra=N`) | Yalnız eksikler yapılır (M5) |
| T3 | `gonderildi` sonrası kesme | Önce toplama; yeni gönderim 0 (M4) |
| T4 | HS_ANIMATIK geçtikten sonra `SAHNELER.json` değişir | A14 reddeder; sağlayıcı çağrısı 0 (M3) |
| T5 | Bakiye < tahmin | Çıkış 5; sağlayıcı çağrısı 0 |
| T6 | `sahte_bozuk` 2. planda `olagandisi` atar | Çıkış 7; `FLOW_KILIDI.json`; izinli yedek yalnız sonraki sahne grubundan; Telegram taklidine ACİL; ders kaydı |
| T7 | Aynı filmde iki süreç; aynı hesapta iki film | İkincisi `FILM.kilit` / `FLOW.kilit` ile reddedilir |
| T8 | `DUR` dosyası | Elindeki iş biter; yeni gönderim 0; çıkış 2 |
| T9 | Bulutta kredili sağlayıcı | Çıkış 4 (M11) |
| T10 | Memmet sayfa durumu (HTML fikstürleri: sayfada olağan dışı, **tek kartta olağan dışı**, reCAPTCHA, kredi bitti, değişmiş arayüz) | Doğru kod; "olağan dışı"dan sonra gönder işlevi çağrılmaz (M8, S1b) |
| T11 | Gizli bilgi | Telegram ve log maskeli; depodaki anahtar dosyaları boş; anahtar deseni taraması (M13) |
| T12 | Ders defteri | Her olay türü kayıt üretir; `--uygula` tempo hızlandırmayı, Flow tavanı yükseltmeyi ve kanıtsız eşik gevşetmeyi reddeder; `deneme` durumu |
| T13 | Kredi hesabı | 405 × 12 × 1,3 = 6.318; dilimler 729/340/389; B0 formülü (2400 sn → ≈ 6.320) |
| T14 | Zincir | Derinlik > 2 → yeniden demirleme; kaynak V3 HATA → plan `bagimsiz`a düşer (planlanmış görsel) |
| T15 | `.bat` biçimi | ASCII, CRLF, `cd /d`; kodda "Soysal" yolu yok (yalnız `*.ornek.json`'da) |
| T16 | `sonraki` sözleşmesi | Her aşama geçerli görev listesi ve çıkış kodu döner; `kim: kullanici` yalnız M2 listesinde |
| T17 | `input()` taraması (AST) | Yalnız `yeni --konu` yolunda (M1) |
| T18 | Yüz kontrolü (model yoksa atlanır) | `mara.jpg` ↔ `mara` kartı ≥ eşik; `voss.jpg` ↔ `mara` < 0,363 |
| T19 **(yeni)** | Görev defteri: 30 rastgele kesme noktası (ajan ortası, betik ortası, paralel grubun yarısı) | %100 tamamlanma; biten görevin yeniden çalışması 0 [kaynak: CM K-18] |
| T20 **(yeni)** | Uygunluk kuyruğu | `son_kare` planı kaynağı V3 + ZK geçmeden bloğa girmez; geçince sonraki bloğa girer; boşta bekleme yok |
| T21 **(yeni)** | Tempo kalıcılığı | Memmet blok molasının ortasında kapatılıp açılır → kalan mola beklenir; gönderim arası alt sınırın altına inmez |
| T22 **(yeni)** | Flow yük | Günlük 20. görselden sonra görsel düzeltmesi ertesi güne; görsel günü + 12 saat dolmadan video oturumu çıkış 8 |
| T23 **(yeni)** | Kuyruk ve bütçe | `sifir_kredi.denendi` olmayan `yeniden_cek` reddedilir; dilim bitince ORTA madde 0 krediye düşer, KRİTİK → çıkış 5 |
| T24 **(yeni)** | `esitle` | Beyaz liste dışı dosya taşınmaz; daha yeni hedef dosya ezilmez, çakışma raporu yazılır; eski dosya `_ESKI/`'ye |
| T25 **(yeni)** | `erisim_kapisi` iki kök | Veri kökündeki `AYARLAR/` okuma ve Bash ile kopyalama reddedilir; `*.ornek.json` açılır |
| T26 **(yeni)** | `yerel_is.py` | Aynı anda tek GPU işi; düşen iş bir kez yeniden, sonra `OLCULEMEDI` |
| T27 **(yeni)** | Pilot seçimi | Kapsama kuralı sağlanır; seçilen planlar P1'den ve gerçek planlardır |
| T28 **(yeni)** | `UYARI_GECTI` | Elle 1 video işareti ya da 30 dk yoksa ret; geçerlilik o takvim günü; o gün tempo ×1,5 |
| T29 **(yeni)** | Alt araç kodu eşlemesi | `puan_oku` 3 → tur sayacı; tavanda 6 |
| T30 **(yeni)** | Kısıtın Memmet → `flow.py` → `film.py` zinciri | `_memmet_cikis.json` kodları doğru dış koda eşlenir |
| T31 **(yeni)** | Şema sürümü | Yeni `SAHNELER.json` (`parti` = hikâye partisi) eski Memmet döngüsüyle çalıştırılamaz (S15) |

- **CI:** GitHub Actions `windows-latest` + Python **3.10** + ffmpeg; aynı takım `ubuntu` + 3.13'te de koşar. Bulutta 3.10 olmadığı için Windows uyumu
  ancak böyle kanıtlanır. 3.11+ özellikleri (`tomllib`, `ExceptionGroup`, `datetime.UTC`) yasak.
- Süre hedefi: T1 ≤ 5 dk; takım ≤ 10 dk (M9).

#### 4.6.6 PR sırası (CLAUDE.md: "küçük, anlamlı commit'ler; her büyük parça ayrı PR")
| PR | İçerik |
|---|---|
| 1 | **Güvenlik:** memmet3'ü depoya al; S1, S1b, S3–S6, S14, S15, S10, S12, S13; `flow_yuk.py`; eski `.bat`'ları kaldır; T10, T21, T31 |
| 2 | Çekirdek: `film.py` v2 + `.claude/bin/film.py` + `ortak.py` + aşama kaydı + sağlayıcı arayüzü + `kaset`/`sahte` + T1–T9, T16, T17, T19, T29, T30 |
| 3 | `kredi.py`, `bildirim.py`, `ders_defteri.py`, `esikler.py` + T5, T11–T13, T23 |
| 4 | Kancalara eklerim ([CM] PR'ıyla birlikte) + iki kök + `esitle` + T24, T25 |
| 5 | `kapi.py` çatısı + uzmanların kâğıt kapıları (zanaat, süreklilik, hikâye, ses) |
| 6 | Görsel tarafı: kütüphane, Gemini paket sarmalayıcısı, G1 ile bağlantı, `yerel_is.py` + T26 |
| 7 | Video: `blok_plani.py`, `memmet_topla`, `pilot_sec.py`, zincir bağlantısı + T14, T20, T22, T27, T28 |
| 8 | Kurgu ve ses araçlarıyla bağlantı, `veo_vertex` |
| 9 | Yayın, `arsivle.py`, `BASLA_BURADAN.txt`, `.bat`'lar, CI, başsız yürütme |

### 4.7 Makinenin denetleyeceği eşikler (kaynağıyla)
Zanaat, hikâye, süreklilik ve ses eşikleri o uzmanların dosyalarındadır. Aşağıdakiler hattın kendi eşikleridir ve **`hat_esikleri.json`**'da,
`ritim_esikleri.json` biçiminde (`{deger, aciklama, kaynak}`) durur. Hepsini `esikler.py` yükler; öğrenilen kurallar yalnız korkuluklar içinde ezer.

#### 4.7.1 Kredi ve bütçe
| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `fiyat.flow.omni_720p_8sn` | 12 kredi | — | FK, H/ucuz-erisim (gerçek test); BK §6.4 |
| `fiyat.flow.omni_360p_8sn` | 6 | — | aynı |
| `fiyat.flow.lite_720p_8sn` | 5 (kullanılmaz: tek model) | — | BK §8 #3 |
| `fiyat.flow.omni_720p_10sn` | **bilinmiyor** → bütçe BAYRAK; pilotta ölçülür | B | [doğrulanmadı] |
| `fiyat.ai84.tts` | 1 kredi/harf; kurulumda `estimate()` ile doğrulanır | — | BK §6.4; [SM2] İ-6 |
| `fiyat.ai84.vc` | ≈ 2.000 kredi/sn → `estimate()` ile ölçülür | — | BK §6.4 (tahmin aracı) |
| `fiyat.vertex.gorsel` | ≈ 0,134 $/görsel | — | 06_SERVISLER (GS) |
| `fiyat.vertex.veo` | **bilinmiyor** | B | — |
| `pay.kapi` | 0,30 (ilk film); sonra öğrenilen değer | — | [tahmin]; B2 ≈ 0,37 [hesap] ile RE 0,20 arası |
| `pay.hedef` | 0,20 | ders kaydı | RE `kredi_yeniden_deneme_payi` |
| `pay.dilim` | görüntü 0,15 · ses 0,07 · kurgu 0,08 | BK | [kaynak: KU2 §2.5, tahmin] |
| `plan_basi_yeniden_max` | 2 (teknik + kurgu, ortak sayaç) | yönetmen onarımı | [kaynak: KU2, UM1; tahmin] |
| `butce.guvenlik_payi` | bakiyenin %10'u harcanmaz | 5 | [tahmin] |
| `butce.sahne_grubu_butunlugu` | Kalan bakiye bir sahne grubunu bitirmeye yetmiyorsa o grup başlatılmaz | 5 | [tahmin]; yarım sahne sağlayıcı karışımı riski |
| `butce.b0_formul` | kredi ≈ 0,169 × süre_sn × 12 × (1 + `pay.kapi`) | — | [hesap: 405 klip / 2400 sn] |
| `kredi_tahmin_sapma` | gerçek/tahmin ∉ [0,90; 1,15] → ders kaydı `butce_sapmasi` | B | [tahmin] |
| `ai84.tavan_film` / `ai84.seri_kurulum_tavan` | 60.000 / 40.000 | 5 | [kaynak: SM2 İ-6] |
| `usd_tavan_film` | 0 (ücretli yollar kapalı) | — | varsayılan |

#### 4.7.2 Flow, Memmet, tempo ve yük
| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `flow.olagandisi_tolerans` | 0: ilk uyarıda (sayfada ya da tek kartta) dur | 7 | BK §6.2 #1; S1b |
| `flow.uyari_kaldirma` | Elle 1 video başarılı + ≥ 30 dk; yalnız o takvim günü | — | BK §6.2 #8–#9 |
| `flow.uyari_gunu_yavaslatma` | gönderim arası ×1,5 | — | [tahmin] |
| `flow.uyari_ertesi_ilk_blok` | `elle` | — | [tahmin] |
| `flow.dogrulama` | dur; devamı kullanıcı başlatır | 2 | BK §8 #7 |
| `flow.model_tek` | bir filmde tek model (Omni 1.1 Flash) | H | BK §8 #3; DR |
| `flow.gece.gonderim_arasi_sn` / `flow.gunduz.gonderim_arasi_sn` | 12–30 / 6–15 | — | BK §6.2 #6 (17.10) |
| `flow.ayni_anda` | 2 | — | aynı |
| `flow.ara_mola` | her 8 gönderimde 3–6 dk | — | aynı |
| `flow.blok_mola` | 2 blokta bir 15–30 dk | — | aynı |
| `flow.blok_boyu` | 20; sahne sınırına ≤ 3 plan kala sınırda kes | — | CI kural 5; 3 [tahmin] |
| `flow.tempo_yon` | yalnız yavaşlatılabilir | korkuluk | kesin karar 5 |
| `flow.tempo_kalici` | molalar ve son gönderim zamanı `FLOW_TEMPO.json`'da; yeniden başlatma kısaltamaz | korkuluk | S14 |
| `flow.gorsel_gunluk_tavan` | 20; makine yalnız düşürür, yükseltme kurulum ayarı | 8 | [tahmin]; DR "~40 görselden sonra işaretlendi" |
| `flow.gorsel_sonrasi_video_saat` | 12 | 8 | [tahmin]; DR |
| `flow.zaman_asimi_sn` | görsel 180, video 360; aşılırsa önce topla | — | `memmet.py` VARSAYILAN |
| `flow.deneme` | 1 ana + 1 yedek istem; teknik hatada +1 | — | [tahmin]; S4 |
| `flow.indirme_butunluk` | ffprobe süresi ≥ 7,5 sn (8 sn klip) | H → yeniden indir | A2 §6.2 V1; DR (kesik indirme) |

#### 4.7.3 Hat, devam ve kapılar
| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `kapi.olculemedi` | Her zaman BAYRAK, asla GEÇ | — | [kaynak: GS §7] |
| `tur_max.kagit_seyirci` | 4, sonra [SN2] merdiveni | 6 | RE `kagit_tur_max`; SN2 §2.6 |
| `tur_max.plan_seyirci` | 2 | 6 | [tahmin; YN2 Ö14] |
| `tur_max.animatik` | 3 | 6 | [tahmin; KU2] |
| `tur_max.kurgu_seyirci` | 3 | teslim + eksik raporu | RE `kurgu_tur_max`; KU2 |
| `tur_max.kagit_kapilari` | 3 (yazara dönüş) | 6 | [tahmin] |
| `tur_max.g1_duzeltme` | 2 → yönetmen kaçışı | — | 01_URETIM_HATTI §5 |
| `tur_max.ajan_sema_duzeltme` | 2 (SubagentStop); değerlendiricide 0 (yeni örnek) | — | [kaynak: CM]; ZN §7.3 |
| `seyirci.*` | GENEL medyanı ≥ 8, ölçüt medyanı ≥ 7, KRİTİK 0, ORTA ≤ 3/parti, özet ≥ 0,8, ilk 2 dk 3/3 | kapı | RE `seyirci_*`, `kopukluk_*`, `ozet_eslesme_min`, `ilk2dk_devam_evet_min` |
| `zincir.derinlik_max` | 2, sonra temiz görselle yeniden demirleme | H | A2 §2.3 (öneri, ölçülmedi) |
| `pilot.plan_sayisi` | 20–30, kapsama kuralı §4.2.4 | — | [tahmin] |
| `ajan.paralel_max` | 5 | — | [tahmin; YN2] |
| `kor_gozlem.gorsel_cagri_max` | 12 | — | [tahmin; GS] |
| `render.sure_sapma` | T1 toplamı ±1 kare | H | [kaynak: KU2 İ-4] |
| `gpu.eszamanli_agir_is` | 1 | — | [tahmin; SM2 SB0] |
| `kilit.bayat_dk` | 30 | — | [tahmin] |
| `disk.c_bos_min_gb` | 20 | 2 | [tahmin]; film başına 5–8 GB [kaynak: BASLA_BURADAN] |
| `bildirim.tekrar_dk` / `bildirim.saat_max` | 30 / 12 | — | [tahmin]; H/uretim-hatti-v2 |
| `hat_denetcisi.kuyruk_esigi` | > 30 klip | ajan çağrılır | [tahmin] |

#### 4.7.4 Ders defteri
| Anahtar | Değer | Kaynak |
|---|---|---|
| `ders.terfi_destek_min` | ≥ 3 kayıt ve ≥ 2 film (ya da tek filmde ≥ 5); hikâye etiketlilerde ≥ 2 film | [tahmin]; SN2 §2.8 |
| `ders.terfi_basari_min` | önerilen eylemin başarısı ≥ 2/3 | [tahmin] |
| `ders.deneme` | uygun planların yarısı (tek/çift plan no), karşılaştırma en az 20 planlık [tahmin] | GS §8.7 |
| `ders.emeklilik` | karşı kanıt ≥ destek → `pasif` | [tahmin] |
| `ders.esik_gevsetme` | yalnız etiketli kalibrasyonla, kaçırma ≤ %10 | A2 §7 |
| `ders.sface_alt_sinir` | 0,363'ün altına inemez | GS §7.9 |
| `ders.yasak_turler` | bot, uyarı, gizli bilgi, onay, silme; tempo hızlandırma; Flow tavanı yükseltme | kesin karar 5; CLAUDE.md Kurallar |

**Kalibrasyon notu.** [tahmin] değerleri pilot dalgada ve ilk iki filmde ders defteriyle ayarlanır. Etiketli setler: B3'ün 44 görseli (21 bozuk)
[kaynak: GS, A2 §7], B2'nin dudak örnekleri [kaynak: SM1 §7.9]. Depoya yalnız etiket JSON'ları girer; görseller kullanıcının diskinde kalır.

### 4.8 Kesin kararların kendi alanımda uygulanışı

#### 4.8.1 Karar 1 — Kullanıcıya yalnız konu sorulur
- `film.py yeni --konu "…"` tek giriştir. Film adını, süreyi (B0), seri kararını ve bütün seçimleri ekip verir; kararlar `kararlar/`'a
  "karar — neden — yanlışsa maliyeti" biçiminde yazılır.
- `input()` yalnız `yeni --konu` yolundadır (T17). `onay()` kalkar (S7). [CM]'nin `soru_kapisi` kancası karar sorusunu yakalar.
- Kullanıcıya kalan işler **karar değil fiziksel iştir** ve kodda sabit bir listedir (M2): giriş/reCAPTCHA, Gemini paketleri, video oturumu ve
  `elle` modda GÖNDER, CapCut'tan dışa aktarma, yükleme onayı. Her biri ekrana ve Telegram'a tek cümleyle gelir; bitişi dosyadan algılanır.
- Bütçe tavanı, gece izni, ücretli API izni ve Flow tavanları **kurulum ayarıdır**. Varsayılanlar soru sormadan güvenli çalışır (§4.5.12).

#### 4.8.2 Karar 2 — Atomik eylem zinciri
- Zincirin yazımı yönetmenin, istem derlemesi kodundur ([YN2], [GS]). Benim katkım hattadır:
  - `plan_imza` `hareket_istem`'i ve `durum_dondu`'yu içerir; zincir değişirse video `bayat` olur ve kuyruktan geçer.
  - Eller [YN2] Ç-4 biçimindedir (`eller.sag/sol.{tutar, yer, sekil}`); açık parmak sayısı `sekil`'den türer. Tur 1'deki `govde.{el, parmak, acik}`
    önerim kalktı.
  - İstem biçimi (`aralik` "0.5-3s:" ya da `sira` "First… then…") **pilot dalgada ölçülür** ([YN1] R1) ve `uretim.istem_bicimi`'ne yazılır.
  - V3'te (bitiş durumu) tutmayan klip kuyruğa girer; [YN2] Y9-c sırası uygulanır (önce kırpma, sonra `bitis_sabit` ile yeniden çekim, sonra bölme).
  - Ders defteri hangi fiil, adım ve kamera birleşimlerinin bozulduğunu sayar; `risk_desen` ve `istem_eki` kuralları bundan doğar.

#### 4.8.3 Karar 3 — Altı özellik
| Özellik | Hattaki uygulanışı |
|---|---|
| (a) Videodan önce animatik + habersiz seyirci | A14'ün girdi imzası `HS_ANIMATIK` raporlarının imzasını içerir; animatik geçmeden video **kodla** başlayamaz (T4). Animatik sesi son sestir (A10c animatikten önce biter) |
| (b) Dünya durumu defteri + zıplama denetimi | Defteri `dunya_defteri.py` kurar (sahibi süreklilik). Hat zarfı, imzayı, durum dondurmayı ve HATA'ların kuyruğa ve ders defterine akışını sağlar. `esitle` defteri buluttan yerele taşır |
| (c) Referansla otomatik yüz kontrolü | Ölçüm görüntü uzmanının; hat `yerel_is.py` ile GPU'yu sıraya koyar. `OLCULEMEDI` asla GEÇ değildir. Eşikler pilotta kalibre edilir (T18) |
| (d) Kare zinciri | **Z1 varsayılan** (`uretim.zincir.yontem = son_kare`). Uygunluk kuyruğu + blok arası işleme (§4.2.4). Derinlik ≤ 2; `ZK` geçmezse planlanmış görsele düşer |
| (e) Kendi kendine öğrenen ders defteri | Olay başına kayıt; derleme; `ders-editoru`; korkuluklu uygulama; `deneme` durumu; pilot dalga öğrenmeyi ilk filmin başına çeker (§4.5.11) |
| (f) Kalıcı seri evreni kütüphanesi | `EVREN/<SERI>/`; yalnız `evren.py` yazar ([CM] makine sahipli). Git'e yalnız JSON'lar girer; görsel, `.npy`, ses ve modeller yerelde kalır ve D'ye yedeklenir. Yeni film aynı seriden başlarsa A01 evreni okur, A10d kartları `id@sürüm` ile yeniden kullanır |

#### 4.8.4 Karar 4 — Ses ve dudak uyumu (hattın tarafı; seçim ses uzmanında)
- Ana yol "Veo konuşur, ses yerelde karakterin evren sesine dönüştürülür", yedek "TTS + dudak senkronu" ([SM2]). Hat bunu sağlayıcı türleri
  (`ayristirma`, `asr`, `ses_donustur`, `dudak`) ve kapılarla yürütür.
- Karar ağacı yerine [SM2]'nin **ses merdiveni** (`ses_karar.py`) kullanılır; Flow kredisi harcayan tek basamak yeniden çekimdir ve kuyruktan,
  `ses` diliminden geçer.
- MuseTalk yerel ve 4 GB'ta denenmiş [kaynak: SM2 D-MT]; klip başına ≈ 5 dk sürdüğü için `yerel_is.py` kuyruğunda en düşük öncelikte, gece koşar.
- Metin kapısı her indirmede koşar (S2m); ses kaynaklı yeniden çekim aynı gecenin sonraki bloğuna girer.
- Yol kıyası seri başında arşiv klipleriyle, ilk filmde ise **pilot dalganın** konuşmalı planlarıyla doğrulanır. Ek Flow kredisi gerekmez.

#### 4.8.5 Karar 5 — Memmet seri üretim aracı değildir; bot tespiti atlatılmaz
- Memmet'in görevi **doğruluktur**: doğru referans, doğru istem, doğru plan, sonucun kimlikten tanınması, NNN künyesi, çift harcamanın önlenmesi,
  G1 sha'sının doğrulanması. Hız onun işi değildir.
- `elle` modu kullanıcı başındayken varsayılandır [kaynak: BK §6.1]. `gece` modu yalnız kurulumda verilmiş `gece_izni` ile açılır ve 17.10 temposuyla
  çalışır. Makine o tempoyu yalnız yavaşlatabilir.
- Uyarıda o anda durulur (S1, S1b). Makine yeniden başlatmaz; kilidi yalnız kullanıcı İ-8 şartlarıyla kaldırır.
- **Yük hesap düzeyinde sayılır** (`FLOW_YUK`, `FLOW_TEMPO`): görsel düzeltmeleri, video ve yeniden çekim aynı sayaçtan geçer; yeniden başlatma molayı kısaltmaz.
- Rastgele bekleme insan taklidi için değil yük sınırlamak içindir; fare/klavye taklidi, reCAPTCHA çözme ve uyarı metnini yok sayma yoktur.
- **Dürüst sonuç:** İnsansız tam otomatik video üretimi için doğru yol resmî API'dir (Vertex Veo). Flow aboneliği bir insan arayüzüdür. 40 dk'lık filmin
  ≈ 13 saatlik Flow süresi ya `elle` modda kullanıcının başında olmasını ya da açık `gece_izni`ni gerektirir. Bu, kullanıcıya kurulumda bir kez söylenir (Q9).

#### 4.8.6 Karar 6 — Hiçbir iş üstün körü yapılmaz
- Çözünürlük, model, plan sayısı ve aday sayısı **kendiliğinden düşürülmez**. Bütçe yetmezse hat durur (5) ve sayıları söyler [kaynak: H/proje-b2].
- Kapı atlatılamaz: kredili görevin imzası kapı raporlarını içerir; `--zorla` bayrağı yoktur; tur tavanı aşılınca kâğıt tarafında hat durur (6).
  Kurgu tarafında (kredi zaten harcanmışken) en iyi sürüm açık eksik raporuyla teslim edilir ([KU2]).
- `ÖLÇÜLEMEDİ` hiçbir zaman GEÇ değildir.
- Pilot dalga bir tasarruf değil, kalite yatırımıdır: yanlış eşik ve yanlış istem biçimi 405 klibe yayılmadan yakalanır.
- Dolgu yasağı [kaynak: ZN §2.5]: kredi tahmini planlanan klip sayısıyla yapılır; süre doldurmak için klip eklenmez.

### 4.9 Riskler, kalan çakışmalar, açık sorular

#### 4.9.1 Riskler
| # | Risk | Olasılık / etki | Önlem |
|---|---|---|---|
| R1 | Claude kullanım sınırı: ≈ 350–550 Opus çağrısı [tahmin] | Yüksek / orta | Her şey dosyada; `StopFailure` → Telegram; paralel ≤ 5; başsız yürütme isteğe bağlı (dolarla) |
| R2 | Kullanıcı el işi: ≈ 18–24 Gemini paketi, `elle` modda ≈ 527 GÖNDER, dışa aktarma | Yüksek / orta | Tek cümle + Telegram + kendiliğinden algılama; gece izni ve ücretli yollar kurulumda dürüstçe sunulur; sayılar film sonu raporunda |
| R3 | Flow hesabının işaretlenmesi; tek sağlayıcı bağımlılığı [kaynak: 05_PROJELER: B3 video aşamasında kaldı] | Orta-yüksek / yüksek | Hesap düzeyinde yük defteri, tempo kalıcılığı, görsel/video ayrı günler, uyarıda dur, izinli yedek sahne grubu sınırında |
| R4 | Flow görsel düzeltme takvimi (≈ 6 görsel günü [hesap]) | Yüksek / orta | 2 aday ilk geçiş; Q13 (3 aday); `vertex_gorsel` (≈ 31 $); Q16 |
| R5 | Depodaki `memmet.py` eski; kullanıcıdaki memmet3 ile ayrışma (S6) | Yüksek / yüksek | PR 1'in ilk işi memmet3'ü depoya almak ve 5 deneme davranışını silmek |
| R6 | Yeni şema eski Memmet'le çalışırsa tempo hızlanır (S15) | Orta / yüksek | Şema sürüm alanı; Memmet blok modu olmadan yeni şemayı reddeder (T31) |
| R7 | 4 GB GPU, üç Python sürümü, ayrı sanal ortamlar | Orta / orta | `yerel_is.py` + GPU kilidi; eksik ortam yalnız kendi basamağını kapatır; kurulum testleri |
| R8 | Bulut ↔ yerel çakışması; kullanıcı git bilmiyor | Orta / düşük | Durum zarflardan türetilir; görev defteri makineye özel; olay başına dosya; `esitle` çakışma kuralı; git yoksa yalnız yerel |
| R9 | Python 3.10 uyumu bulutta sınanamaz (bulut 3.13) | Yüksek / orta | Windows + 3.10 CI; 3.11+ özellikleri yasak |
| R10 | Sağlayıcılar arası görünüm farkı (Omni ↔ Veo API) | Orta / orta | Geçiş yalnız sahne grubu sınırında; ilk geçişte ölçüm [doğrulanmadı] |
| R11 | Habersizlik sızıntısı | Düşük / yüksek | Girdiyi betik hazırlar; [CM] `erisim_kapisi`; her tur yeni örnek |
| R12 | Yanlış öğrenilen kural hattı gereksiz sıkılaştırır | Orta / orta | Terfi eşiği, `deneme` durumu, `geri_al`, emeklilik, sürüm imzası; gevşetme yalnız kalibrasyonla |
| R13 | `memmet-bakimci`'nin yerel düzeltmesi ile `GUNCELLE.bat`'ın `--ff-only` çekişi çakışır | Düşük / orta | Onarım yerel bir dalda kaydedilir ve raporlanır; çekiş başarısızsa `GUNCELLE.bat` durur ve nedenini yazar; birleştirme `film-gelistir` işidir |
| R14 | Pilot, henüz kalibre edilmemiş eşiklerle üretilir | Orta / düşük | Pilot klipleri de bütün kapılardan geçer; eşik değişince pilot klipleri 0 krediyle yeniden değerlendirilir, yalnız gerçekten bozuk olanlar kuyruğa girer |

#### 4.9.2 Kalan çakışmalar
| # | Konu | Taraf | Durum ve önerim |
|---|---|---|---|
| C1 | Ajan devri protokolü ve çıkış kodu 2 | [GS] | İ-1. [GS]'nin tur 2'sinde `_AJAN_ISLERI/` → `_GOREV/` geçişini bekliyorum |
| C2 | Flow görsel düzeltmesinin günlük tavanı ve görsel→video beklemesi | [GS] | İ-2. Değerler tahmin; [GS] başka bir dayanak gösterirse onun değeri alınır, yön kuralı ("makine yalnız sıkılaştırır") kalır |
| C3 | Erişim deny listesi, `git push`, S-1 | [CM] | İ-3. [CM] tur 2'de iki kökü kabul ederse kancaya eklerim §4.4.3'teki gibi girer |
| C4 | Ders defteri tek JSONL mi, olay başına dosya mı | [CM] | İ-7. Olay başına dosya + türetilen dizin |
| C5 | Aşama kodları | herkes | §2.1'deki A-kodları ve eşleme tablosu; her uzman kendi satırını doğrulamalı |
| C6 | `yayin_kaynagi: master` seçeneğinde mux kanıtı | [KU2], [SM2] | [KU2] İ-2'deki "aynı çizelge" kanıtı kabul; ayrıntı ikisinin |
| C7 | `kie.ai` | kullanıcı | Varsayılan kapalı; BK §6.4 "gri abonelik havuzu" şüphesi |

#### 4.9.3 Açık sorular
| # | Soru | Neden önemli | Nasıl kapanır |
|---|---|---|---|
| Q1 | Flow kredi bakiyesi ayar menüsünden güvenilir okunabiliyor mu? | B0 ve B2'nin bakiyesi | `memmet.py --bakiye` ile tek okuma (gönderim yok) |
| Q2 | Flow politika reddi kredi harcıyor mu? | Deneme politikası ve tahmin | Pilotta `KREDI_DEFTERI` + bakiye farkı |
| Q3 | Omni 720p 10 sn klibin fiyatı? | 17–20 kelimelik replikler | Pilotta bir 10 sn plan |
| Q4 | Vertex Veo fiyatı, kullanıcının Google Cloud hesabı, dolar tavanı | Yedek sağlayıcı | Kurulumda bir kez |
| Q5 | kie.ai kullanılabilir mi? | Gri abonelik şüphesi [kaynak: BK §6.4] | Varsayılan kapalı; kullanıcı kararı |
| Q6 | memmet3 ve B2/B3 betikleri depoya nasıl gelecek? | Çalışan son sürümden başlamak | Yereldeki Claude Code oturumu `C:\…\YZ_FILM\ARACLAR` ve D arşivinden kopyalar (`AYARLAR` hariç) |
| Q7 | Windows'ta git kurulu mu? | Bulut ↔ yerel taşıma | `kurulum.py` denetler; yoksa yalnız yerel tek kök |
| Q8 | YouTube yükleme yapılacak mı (OAuth)? | A17y | Yayın uzmanı; isteğe bağlı ve onaylı |
| Q9 | Gece izni kalıcı verilecek mi, yoksa resmî API mi? BK §6.2 #10 ("kredi harcatan onaylara kullanıcı basar") ile kurulumdaki izin aynı şey sayılır mı? | İnsansız üretim | Kullanıcıya **kurulumda bir kez** dürüstçe sorulur; film başına soru değil |
| Q10 | Bulut oturumunda Telegram istenir mi? | Bulut bildirimleri | Ortam sırrı; varsayılan kapalı |
| Q11 | B3'ün 44 etiketli görseli depoya alınabilir mi (yalnız etiket JSON'u)? | Eşik kalibrasyonu | Yerel oturum |
| Q12 | Abonelik kullanım sınırı 350–550 çağrıya yetiyor mu? | R1, takvim | İlk filmde ölçülür; başsız yürütme yedek |
| Q13 | Gemini ajanı 30 planlık pakette plan başına 3 aday üretebiliyor mu? | Flow düzeltme günlerini ≈ 6'dan ≈ 3'e indirir [hesap] | Bir pakette denenir; [GS] ile |
| Q14 | Günlük Flow görsel tavanı (20) için daha iyi bir dayanak var mı? | R3, R4 | 17–19.10 Memmet kayıtları ve `H/olagandisi-dur` ayrıntısı okunur |
| Q15 | 720p video üretim süresi kaç saniye? (360p ≈ 40 sn [kaynak: FK]) | 13 saat tahmini | Pilotta ölçülür |
| Q16 | Gemini API (AI Studio) görsel üretiminin ücretsiz kotası düzeltme görsellerini Flow'a yük bindirmeden yapabilir mi? | R4 | [doğrulanmadı]; kurulumda küçük denemeyle |

---

### Kısa özet (5 satır)
1. Hat tek bir durum makinesidir: iş birimi [CM]'nin görevidir, dış protokol benim 0–8 çıkış kodlarımdır (8 BEKLE yeni), aşama kodları A00–A18'dir.
   Durum zarflardan türetilir; kilit, DUR ve atomik yazım vardır; kredili hiçbir iş kapıların imzası olmadan başlamaz.
2. Kare zinciri Z1 varsayılandır ve uygunluk kuyruğuyla uygulanır: zorunlu Flow molalarının içinde V2/V3 ve zincir karesi işlenir, ek bekleme yoktur.
3. Flow yükü hesap düzeyinde sayılır (`FLOW_YUK`, `FLOW_TEMPO`); uyarıda durulur, kilidi yalnız kullanıcı kaldırır; yeniden başlatma ve yeni şema
   tempoyu hızlandıramaz. Mevcut Memmet'te bunu çiğneyen iki yeni kusur bulundu (S1b kartta uyarıda yeniden gönderim, S14–S15 mola sıfırlanması).
4. İlk filmde 20–30 gerçek planlık pilot dalga eşikleri, istem biçimini ve ses yolunu ölçer; ders defteri olay başına dosyadır ve yalnız korkuluk içinde sıkılaştırır.
5. 40 dk film ≈ 6.320 kredi, ≈ 13 saat Flow, ≈ 6 görsel günü, ≈ 350–550 ajan çağrısı ve ≈ 2–3 hafta takvim ister [hesap, tahmin]; iki kök ve
   `esitle` ile bulut kâğıdı, yerel üretimi yapar; testler 31 senaryodur ve Windows + Python 3.10 CI şarttır.
