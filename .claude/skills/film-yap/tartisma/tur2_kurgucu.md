# TUR 2 — KURGUCU UZMANI: itirazlar, çakışmalar, revize nihai öneri

Hazırlayan: kurgucu uzmanı (Claude Opus 5.5). Tarih: 23.10.2026. Durum: TAMAM (2. tur).

**Bu turda okunanlar:**
- `tartisma/` altındaki yedi tur 1 dosyasının tamamı (kendi dosyam dahil).
- Bu turda benden önce yazılmış `tur2_senarist.md` ve `tur2_yonetmen.md`. Uzlaşmaları izlemek ve aynı alan adlarını kullanmak için okundu.
- Dayanak belgeler: `ZANAAT.md` (tamamı), `ritim_esikleri.json` (bütün anahtarlar betikle listelendi), `BILGI_KURALLARI.md` §5.1–5.3 ve §8,
  `KARARLAR.md`, `03_DERSLER.md`, `HAFIZA_YEDEGI/` içinden `capcut-elle-duzenleme`, `kurgu-izleme-denetimi`, `uretim-hatti-v2`, `proje-b2`.
- Mevcut kod: `capcut_film.py`, `izleme_paketi.py`, `puan_oku.py`, `film.py`, `kurgu_koprusu/hareket.py`.

**Dosya kısaltmaları:** `[KU1]` benim tur 1 dosyam · `[YN1]`/`[YN2]` yönetmen tur 1/tur 2 · `[SN1]`/`[SN2]` senarist tur 1/tur 2 ·
`[GS]` görüntü-süreklilik · `[SM]` ses-müzik · `[UM]` üretim mühendisi · `[CM]` Claude Code mimarisi.

**Kaynak kısaltmaları (tur 1 ile aynı):** `ZN` ZANAAT.md · `RE` ritim_esikleri.json (anahtar adıyla) · `BK` BILGI_KURALLARI.md ·
`AR1/AR2/AR3` araştırma 01/02/03 · `DR` 03_DERSLER.md · `UH` 01_URETIM_HATTI.md · `KR` KARARLAR.md · `H/<ad>` HAFIZA_YEDEGI notu ·
`CA` = bu oturumda yüklenen `claude-api` becerisi (model tablosu 06.10.2026 önbelleği).

**Adım kodlarım:** tur 1'deki `K0–K12` bu turda **`KR0–KR12`** oldu. [GS]'nin `K0` (kâğıt süreklilik) ve `K1` (geçiş denetimi) kapılarıyla karışmasın diye.

**Sayı etiketleri:** kaynaklı sayının yanında kaynağı yazar · **(hesap)** = kaynaktaki sayılardan türetildi ·
**(tahmin)** = kaynağı yok; ilk filmde ölçülüp ders defteriyle ayarlanacak başlangıç değeri.

### Bu turun özü (5 satır)
1. **Tek gerçek `KURGU_PLANI.json`, tek ölçü tek kod.** Zamana bağlı her ölçü tek kütüphanededir (`zaman_cizelgesi.py`). Ses sinyalini ses araçları, çizelge aritmetiğini kurgu ölçer; kendi Z3 #44–47 ölçümümü geri çekiyorum.
2. **Habersiz seyirci tek ajandır** (`habersiz-seyirci`, `animatik` ve `kurgu` kipleri). Filmi baştan sona, parça parça, aşamalı girdiyle izler. Ona kopukluk adayı, `ekranda_bilgi` ya da özet verilmez. Tur 1'deki `kurgu-seyircisi`, `ONCEKI_OZET` ve "previously" önerilerimi geri çekiyorum.
3. **Kare zinciri Z1 (kesme anındaki gerçek kare) varsayılandır.** Z1 kaynağının çıkış noktası kurguda kilitlidir. Çıplak `devam` dikişi örtü planıyla kapatılır.
4. **Kullanıcı CapCut'ta düzenlediyse taslak sıfırdan kurulmaz** (BK §5.3.3). Kullanıcının taslağı klonlanır, yalnız bizim kanallarımız yamanır, kaynağına hiç yazılmaz. Yayın dosyasının sesi ancak aynı çizelgeden geldiği **ölçülürse** değiştirilir.
5. **Kredili her yeniden çekim önce 0 kredi merdiveninden geçer** ve bunu kuyruk kodla zorlar. Kurgu turlarına ayrılmış bir kredi dilimi vardır. Uzmanların yeniden çekim payları RE ile uzlaştırıldı.

---

## 1. Diğer önerilere itirazlarım (dosya + madde + neden + önerim)

★ işaretli üç madde en önemli itirazlarımdır. Her maddede kendi alanıma (animatik, kurgu izleme, kırpma, J/L, kuyruk, CapCut) etkisi yazılıdır.

### ★ İ-1 · [GS] A10, A16, §3.4, §8.3 — Makinenin bulduğu kopukluk adaylarının habersiz seyirciye verilmesi
- **Ne yazılmış:**
  - A10: "BAYRAK'lar animatikteki habersiz seyircinin dikkatine 'kopukluk adayı' olarak gider."
  - A16: "Bulgular yan yana kare çiftiyle kurgu izleme denetimine kopukluk adayı olarak verilir."
  - §3.4: "`habersiz-seyirci` … K1-ön/K1 kare çiftlerini kopukluk adayı olarak görür."
- **Neden yanlış:**
  1. **Habersizliği bozar.** Seyirciye "şu geçişe bak" demek yönlendirmedir. [SN1] §4 yasaklar listesi: "seyirciye 'şuna dikkat et' ipucu verilmez". ZN §7.3'ün bütün yöntemi seyircinin yalnız ekranda olanı görmesine dayanır.
  2. **İki bağımsız kanıtı bir kanıta indirir.** Seyirci, makinenin işaretlediği çifti zaten "bulur". Hangi kopukluğun gerçekten seyirciyi kopardığı artık ölçülemez. [GS]'nin kendi kalibrasyon kuralı (§7.9, "kaçırma ≤ %10"), seyirci bulgusunun makineden **bağımsız** etiket olmasına muhtaçtır.
  3. **Yanlış alarmı kuyruğa taşır.** [GS] B5 yanlış alarm oranını ≤ %30 kabul ediyor. Seyirci bu adayları KRİTİK yazarsa KRİTİK kuyrukta kalamayacağı için kredi harcanır.
  4. **Puanı bozar.** İşaretli çift sayısı akıcılık puanını aşağı çeker. Turlar arası puan karşılaştırması bir paket özelliğine bağlanır.
- **Önerim:**
  - K1-ön ve K1 bulguları kurgucuya ve süreklilik hakemine gider, seyirciye gitmez ([KU1] D7).
  - Seyirci paketi **her** kesmeyi zaten üçlü pencereyle gösterir: önceki planın son karesi, bu planın kareleri, sonraki planın ilk karesi. Bütün dikişler eşit gösterilir; hiçbiri işaretlenmez.
  - `bulgu_yonlendir` modülünün K1 eşleme adımı iki kaynağı **sonradan** eşler (§2.2):
    - Seyirci kopukluğu (±1 plan) ile K1 bulgusu aynı geçişi gösteriyorsa bulgu `dogrulanmis` olur, önceliği artar.
    - Yalnız K1'de olan BAYRAK kurgucunun 0 kredi listesine girer.
    - Yalnız seyircide olan bulgu, ders defterine "makine kaçırdı" (`kacirma`) etiketiyle yazılır. Bu, [GS] §8.7 kalibrasyonunun beklediği veridir.

### ★ İ-2 · [UM] M06 ve C9 · [SM] E1, R9, D6 · [CM] film-not — Yayın dosyasının ve kullanıcı düzenlemesinin zaman çizelgesi tek kaynaktan kanıtlanmıyor
- **Ne yazılmış:**
  - [UM] M06: "CapCut katmanlı taslak + renk cilası + ffmpeg master render → `FINAL/film.mp4`". C9: "ffmpeg ana kayıt + CapCut taslağı (isteğe bağlı düzenleme)".
  - [SM] E1: "dışa aktarılan videonun sesi video yeniden kodlanmadan master ile değiştirilir". R9: "`son_miks.py` taslağı `taslak_fark.py` ile okur, … kesimleri master'a uygular". D6: "dosyalar yerinde güncellenir, taslak yeniden kurulmaz".
  - [CM] `film-not`: "taslak yeniden kurulmaz (dosyalar yerinde değişir)"; "Bitince yine CapCut'ta aynı projede göreceksin".
  - Kendi [KU1] §8.7'm: kullanıcı yalnız kırptı, sildi ya da taşıdıysa yeni sürüm `v<N+1>` sıfırdan kurulur.
- **Neden:**
  1. **Kayıtlı kullanıcı kararı:** KR (satır 48) "Bitmiş mp4 yerine CapCut projesi … Kullanıcı önce CapCut'ta görür, dışa aktarmayı kendisi yapar." BK §8 #18 de aynı. [UM] C9'un ffmpeg "ana kaydı" bu kararı değiştirir. Kesin karar 1 yalnız soruları kaldırır, teslim biçimini değiştirmez.
  2. **Mux kayması:** Master üretildikten sonra kullanıcı CapCut'ta bir planı 0,4 sn kısaltırsa, dışa aktarımın görüntüsü ile master sesi o noktadan sonra 0,4 sn kayar. Bu, B2'deki "seslerde kayma, dudakla gitmiyor" şikâyetinin aynısıdır (H/proje-b2). [SM] R9 "kesimleri master'a uygular" diyor, ama uygulamanın tamamlandığını gösteren bir **ölçü** yok.
  3. **"Dosyalar yerinde değişir" iki kurala çarpar:** DR "kullanıcının taslağının bağlı olduğu dosyalara dokunma" ve BK §5.3.8 "her sürüm yeni klasöre derlenir". Bir medya dosyası yerinde ezilirse o dosyaya bağlı eski sürüm taslakları da sessizce değişir.
  4. **Kendi önerim de yanlıştı:** Kullanıcı düzenlemesinden sonra sıfırdan yeni sürüm kurmak BK §5.3.3'e ve H/uretim-hatti-v2'ye aykırıdır. Bu not (son değişiklik 15.10 22:11 UTC), "projeyi yeniden kur" diyen H/capcut-elle-duzenleme'den (15.10 15:27 UTC) daha yenidir. Önerimi geri çekiyorum.
- **Önerim** (ayrıntı §4.2 KR10–KR12, §4.5.7–4.5.8):
  - **Teslim biçimi KR'deki gibidir:** CapCut taslağı verilir, dışa aktarmayı kullanıcı yapar. `kurgu_render.py`'nin ffmpeg çıktısı ölçüm ve yedek içindir, "ana kayıt" değildir. Kullanıcı kurulumda `yayin_kaynagi: master` seçerse ffmpeg çıktısı yayın dosyası olur. Bu bir kurulum ayarıdır, film başına soru değildir.
  - **Kullanıcı taslağı düzenlediyse taslak sıfırdan kurulmaz.** Kullanıcının taslağı temel alınır:
    1. Taslak salt okunur incelenir.
    2. Kararları `KURGU_PLANI`'na kilitli işlenir.
    3. Taslak **klonlanır**. Kurgu köprüsündeki `clone_project` bunun emsalidir: "Never writes source" (`kurgu_koprusu/hareket.py`).
    4. Klonda yalnız bizim kanallarımız yamanır. Klipler kanalına ve kullanıcının eklediği her şeye dokunulmaz.
    5. Yeni medya yeni dosya adıyla bağlanır; eski dosya ezilmez.
    6. Öz denetim yapılır. Yama doğrulanamazsa kullanıcının kararlarıyla yeni adla bir taslak kurulur. Kullanıcıya bilgi verilir, soru sorulmaz.
  - **`son_miks --mux` yalnız "aynı çizelge" kanıtıyla çalışır:**
    - Dışa aktarımın süresi, kilitli `KURGU_PLANI` toplamına ±1 kare eşittir.
    - Dışa aktarımın sesi ile master miks arasında çapraz korelasyon ofseti 0 ±1 karedir ve tepe korelasyonu ≥ 0,9'dur (tahmin).
    - Kanıt yoksa önce KR11 çalışır (fark → kilit → stemler yeniden). Mux ondan sonra yapılır.

### ★ İ-3 · [UM] C1 ve U05 · [GS] B7 · [SM] §8.3 · [YN2] Ö9 · [KU1] B12 — Yeniden çekim payları RE'yi aşıyor, kurgu turlarına kredi ayrılmamış, "önce 0 kredi" kodla zorlanmıyor
- **Ne yazılmış:**
  - [UM] C1: bütçe kapısında pay 0,30, RE hedefi 0,20. U05 "mini bütçe kapısı". Plan başına en çok 2 yeniden çekim.
  - [GS] B7: süreklilik kaynaklı yeniden çekim ≤ %15 klip.
  - [SM] §8.3: ses kaynaklı yeniden çekim ≈ 190 × %15 ≈ 29 klip, yani ≈ %7 (tahmin).
  - [YN2] Ö9: plan dili kök nedenli ≤ %5 (GS'nin %15'inin içinde sayılabilir).
  - [KU1] B12: kurgu aşamasında ≤ %8.
- **Neden:**
  1. **Paylar toplanınca RE'yi aşar:** %15 + %7 + %8 = %30 (hesap). Bu, RE `kredi_yeniden_deneme_payi` = 0,20'nin üstündedir. Her uzman kendi payını "%20'nin içinde" sanıyor.
  2. **Kuyruk tek ve teknik kapılar önce çalışır.** Video dalgalarında V1/V2/V3 tekrarları payı bitirirse, kurgu izleme turunda KRİTİK için kredi kalmaz. Hat bekler, taslak kullanıcıya gecikir. Oysa kurgu KRİTİK'leri hikâyenin anlaşılmasını bozan maddelerdir.
  3. **"Önce 0 kredi" kodda yok.** Kuyruğu besleyen her kapı (G1, V1–V3, S2, kurgu) doğrudan kredili çözüm yazabiliyor. Kırpmayla atlanabilecek bir kusur (V1/V2 kusuru kullanılan pencerenin dışındaysa), ekran dışı replikle çözülecek bir dudak sorunu ya da sıra değişikliğiyle kapanacak bir konum kopukluğu kredi harcatabilir. B2'deki ≈ %37'lik yeniden çekimin bir kısmı böyle çözülebilirdi ([KU1] §1.3; oran tahmin).
- **Önerim** (§2.5, §4.5.5):
  - **Tek bütçe tablosu** `URETIM_ONIZLEME.json`'da durur, `kredi.py` ([UM]) hesaplar. Kapı payı 0,30'dur ([UM], ilk film). Payın içindeki alt dilimler (hepsi tahmin):
    - görüntü, süreklilik ve plan dili: 0,15
    - ses: 0,07
    - kurgu: 0,08
    - RE 0,20 **hedef** olarak kalır; gerçekleşeni ders defteri ölçer ([UM] C1 ile aynı fikir).
  - Dilimler arası aktarma yalnız KRİTİK madde için ve hat denetçisi notuyla yapılır.
  - **0 kredi kuralı:** `cozum` alanı `yeniden_cek` ya da `yeni_plan` olan madde, `sifir_kredi.denendi: true` ve gerekçesi yazılı değilse kuyruğa girmez. 0 kredi denemesini `kurgucu` yapar (`sifir_kredi` kipi, §4.3). `kuyruk.py` bu kuralı zorlar ve testi vardır.
  - Plan başına toplam yeniden çekim ≤ 2'dir (teknik ve kurgu birlikte; [UM] ile aynı). Aşılırsa yönetmen planı değiştirir.

### İ-4 · [UM] V07 — Animatikte "taslak TTS (AI84, ucuz)", "geçici müzik", süre "±%5"
- **Neden:**
  1. Animatik sesi taslak değildir. [SM] B1'de aynı TTS dosyaları Yol B'de son ses olarak kullanılır ve ikinci kez ücretlenmez. "Taslak" denirse ses seçimi animatikten sonraya kayar. O zaman animatikte ölçülen replik süreleri son sesle uyuşmaz ve T1 çizelgesi boşa gider.
  2. Render süresinde ±%5 sapma bir hata payı değil, kod hatasıdır. Render süresi çizelge toplamına ±1 kare eşit olmalıdır. Plan süresinin plandan sapması ayrı bir ölçüdür: T0 ↔ T1 sapma raporu, plan başına ±%25 BAYRAK (tahmin).
- **Önerim:** Animatik sesi, ses kadrosu seçildikten sonraki [SM] B1 TTS'idir. Müzik [SM] B2'de üretilmişse gerçek ipucu çalar, değilse `GECICI` etiketiyle geçici müzik çalar. Render süresi = T1 toplamı ±1 kare (HATA).

### İ-5 · [SN2] §2.4 kural 1 — "Betik, seyircinin cümlesinden ilgili `anahtar_olgu`'yu bulur"
- **Neden:** "Kadının yavruyu nereden bildiğini anlamadım" cümlesini `o07`'ye ya da `kur_duduk`'a deterministik bir betik güvenilir biçimde eşleyemez. Bu bir anlam işidir. Yanlış eşleme bulguyu yanlış sahibe gönderir: yazar yerine yönetmene ya da tersine.
- **Önerim:**
  - Eşlemeyi kör `ozet-eslestirici` yapar. Bunun için yeni bir kip eklenir: `bulgu`. Her kopukluk için çıktı `{eslesen: {tur, id} | null, alinti}` olur.
  - Sahibi bundan sonra **betik** seçer: [SN2]'nin tablosunu, bu eşlemeyi, `HIKAYE.json`'u ve plan alanlarını kullanır.
  - Eşleşme yoksa bulgu kurgucuya gider ([SN2] ile aynı yedek).

### İ-6 · [CM] A16 geçme şartı "kesici önerilerinin ≥ %50'si uygulandı" · [SN2] H11 "kesme adaylarının en az yarısı uygulanır"
- **Neden:** Kesme simülasyonu yeni HATA gösterirse o kesme uygulanmamalıdır. Örnekler: kurulum kaybı (Z1 #29), dondurulmuş durum zıplaması (Y58), tepe öncesi nefes çukurunun kaybı (Z2 #38). Oranın paydası bütün öneriler olursa zararlı bir kesmenin uygulanması zorunlu hâle gelebilir.
- **Önerim:** Oran = uygulanan / (simülasyondan HATA'sız geçen öneriler). Simülasyonda HATA veren öneriler gerekçesiyle raporlanır, paydaya girmez. RE `kesme_turu_oneri`'nin açıklamasına bu tanım yazılır. Kâğıttaki kesme turu için de aynı tanım önerilir.

### İ-7 · [CM] §5.8 kör paket "kadraj (düz sözle)" · [KU1] §5.4 (kendime)
- **Neden:** Animatik ve kurgu kiplerinde görüntü kadrajı zaten gösterir. "Yakın plan", "omuz üstü" gibi bir etiket yönetmen sözlüğüdür ve dikkati yönlendirir. Kâğıt ve plan kiplerinde (görüntü yok) düz sözle kadraj verilmesi ise doğrudur.
- **Önerim:** İzleme kiplerinde kadraj etiketi verilmez. Plan numarası kalır, çünkü kopukluğu plana bağlamak için gerekir. Plan tipi, kurulum, kesme tipi ve amaç verilmez.

### İ-8 · [SM] §5.5 `muzik_listesi.giris {plan, ofset_sn}` ve D4
- **Neden:** `ofset_sn` planın klip saatine göre yazılırsa kırpma değişince (`kullanim.bas`) müzik yanlış ana kayar. Kesme ya da sıra değişince plan numarası aynı kalsa da çizelgedeki anı değişir.
- **Önerim:**
  - Müziğin giriş, çıkış ve vuruş noktaları **olay** olarak yazılır: `kesme:<sira>`, `adim:<plan>.a2`, `replik_sonu:R0123`, `plan_basi:<plan>`. Ofset olaydan sonraki saniyedir.
  - Olayın çizelgedeki anını `zaman_cizelgesi` çözer. Her kurgu değişikliğinden sonra müzik yerleşimi kendiliğinden yeniden çözülür ve S6 yeniden ölçülür.
  - [SM]'nin `olay` alanı zaten var. Değişiklik yalnız "anı `KURGU_PLANI`'ndan çöz" kuralıdır.

### İ-9 · Aynı ölçünün birden çok araçta hesaplanması · [SM] S3.6, S3.8 · [KU1] `kurgu_denetim` Z3 #44–47 · [YN1] `plan_denetim --dokum` Z0 #1–3, #8 · [SN1]/[SN2] `senaryo-denetim` zaman ölçüleri · [GS] V1 ve [SM] S2.1 replik penceresi sessizliği
- **Neden:** İki kod aynı ölçüye iki ayrı sonuç verir; hangi raporun doğru olduğu tartışma konusu olur. [KU1] §9.2-2'de de yazmıştım; bu turda somut bir sahiplik tablosu öneriyorum (§2.2).
- **Önerim:**
  - **Zamana bağlı her ölçü tek kütüphanededir:** `zaman_cizelgesi.py` (Z0 #1–3, #5, #7–10; Z1'in zaman ölçüleri; Z2 #35–39). Hikâye odası (TH çizelgesi, ±%15 belirsizlik bandıyla), yönetmen (T0) ve kurgu (T1–T3) aynı fonksiyonları içe alır.
  - **Ses sinyali ölçüleri** (LUFS, dudak ofseti, ağız açıklığı, ASR, müzik kaplaması) ses araçlarındadır. `kurgu_denetim` yalnız raporlarını okur ve Z3 kararını birleştirir. Tur 1'deki kendi Z3 #44–47 ölçümümü geri çekiyorum.
  - **Çizelge aritmetiği** `kurgu_denetim`'dedir: senkron formülü, cevap boşluğu, bölünmüş klipte atlanan aralığın bir sözle kesişmesi, J/L sınırları, ağzı oynayan yüzün üstüne başka replik binmesi. Bu yüzden [SM] S3.6 ve S3.8 buraya taşınır. S3.5'te ağız dizisi ses aracından gelir; replik aralığıyla kesişimini kurgu hesaplar.
  - Replik penceresinde sessizlik tek yerde ölçülür: [SM] S2.1 ([SM] §9.2'nin kendi önerisi).

### İ-10 · [CM] §3.3 "`KURGU/son_capcut_projesi.json` diye bir dosya yok"
- **Yanlış:** `capcut_film.py` bu dosyayı yazıyor. İçinde proje adı, süre, sahne başına `bas/sure/dosya` ve `benim_yazilarim` var.
- **Doğru eleştiri:** Dosya plan değil `no` sırasıyla yazılıyor ve kırpma bilgisi taşımıyor.
- **Önerim:** Dosya kalır. `KURGU_PLANI` segment eşlemesiyle genişler (§4.5.8). Bölüm zamanlarını yayın paketçisi `KURGU_PLANI`'ndan alır.

### İ-11 · [YN2] Y54 "örtülü devam ≥ 1,0 sn" (kabul; süre kuralı eksik)
- **Neden:** Örtünün gizlemesi gereken şey, A'nın kullanılan bitiş tutması (≥ 0,5 sn, RE `bitis_tutma_sn`) ile B'nin ölçülen durağan başlangıcıdır (0,3–1,0 sn, ZN §2.2). Bu ikisinin toplamı 1,0 sn'yi aşabilir. Ayrıca örtü planının nereden geleceği yazılmamış.
- **Önerim:**
  - Örtü süresi ≥ max(1,0; A'nın kullanılan tutma süresi + B'nin ölçülen durağanlık süresi) (formül tahmin).
  - Örtü önce mevcut tepki ya da ekleme kliplerinin kullanılmayan penceresinden seçilir (0 kredi, merdiven #6). Bulunmazsa yönetmen planlar.
  - Y55'i (Z1 kaynağında kesme bitiş tutmasının içinde) aynen kabul ediyorum. Bu kural `eylem_kesme`'deki %60–70 kuralıyla çelişmez, çünkü `devam` ayrı bir geçiş türüdür.

---

## 2. Çakışmalar ve önerdiğim çözüm (alan adları, aşama sırası, sorumluluk sınırları)

### 2.1 Alan ve dosya adları

| Kavram | Öneriler | Çözüm | Gerekçe |
|---|---|---|---|
| Kurgunun tek kaynağı | [KU1] `KURGU/KURGU_PLANI.json` · [UM] M01 · [CM] `KURGU_PLANI_vN` · [YN2] kabul | `KURGU/KURGU_PLANI.json` + her sürüm `KURGU/surumler/KURGU_PLANI_<T>_v<N>.json` | BK §5.3.8 "her sürüm yeni klasöre" |
| Planlanan kırpma | [KU1] `zanaat.sure_sn`, `kesme.nokta_sn` · [YN2] İ-5 | **Tek yazılan alan `kullanim{bas,sure}`** (SAHNELER, yönetmen). `sure_sn` ve `kesme_nokta_sn` `_derlenir`'e hesaplanır. Ölçülen kırpma yalnız `KURGU_PLANI`'nda durur | Kendi alanlarımı geri çekiyorum |
| Kesme | ZN `{tip, nokta_sn, ses_tasma_sn}` · [YN2] `zanaat.kesme {tip, ses_tasma_sn}` | Planlanan: `zanaat.kesme`. Gerçekleşen: `KURGU_PLANI.planlar[].kesme_cikis {tip, adim: "a2", adim_orani}` | Adıma kalıcı kimlikle bağlanır ([YN2] Ç-12) |
| `parti` | [YN1] üretim bloğu · [KU1], [UM], [CM], [YN2], [SN2] hikâye partisi | `parti` = hikâye partisi (1–3); `uretim_blogu` = 20'lik gönderim bloğu (betik); `gemini_paketi` = 30; `izleme_parcasi` = 240–300 sn | Çoğunluk; BK §8 #14 kapanır |
| Seyirci ajanı | [KU1] `kurgu-seyircisi` · [SN2] İ14 · [CM] kipler | **`habersiz-seyirci`**; kipler `kagit · plan · ilk2dk · animatik · kurgu`. İzleme kiplerinin gövde metni benim | Kipler arası puan aynı cetvelle kıyaslanır |
| Özet eşleştirici | [KU1] `ozet-eslestirici` (sonnet) · [SN2] (opus, kör) | `ozet-eslestirici`, opus/high, kör; **yeni kip `bulgu`** (İ-5) | Model kuralı (H/ajan-opus-yuksek) |
| Seyircinin anlaması gereken olgular | [KU1] `ANAHTAR_OLGULAR_P<p>` · [SN2] `anahtar_olgular[]` | `HIKAYE.json → anahtar_olgular[]` (`hikaye_partisi`, `kritik`, `ekranda`) | Senarist alanı |
| Ad maskeleme | [KU1] `etiket_anonim`, `takma_adlar` · [SN2] `maske` | Karakter kartında `maske: {etiket_anonim_en, takma_adlar[]}`. Tek kod: `kor_paket.py` | Kâğıt ve izleme aynı maskeleme kodunu kullanır |
| Ayna yasağı | [KU1] `kurgu.ayna_yasak` · [YN2] İ-10 | `_derlenir.ayna_yasak` (kod hesaplar; elde nesne, `asimetrik` öğe, yazı varsa `true`) | Ayna eldeki nesneyi öbür ele geçirir; bu bir defter zıplamasıdır |
| Vaat imgesi, zincir kaynağı | [KU1] `kurgu.vaat_imgesi`, `kurgu.zincir_kaynagi` | `zanaat.vaat_imgesi` (yönetmen, HIKAYE vaat sözleşmesinden), `uretim.zincir.kaynak` ([GS] yazar) | [YN2] eşleme tablosu |
| `kurgu` alt nesnesi | [KU1] 4 alan | Yalnız `kirpma_onceligi` (`eylem` / `replik` / `tepki_tepesi` / `durgun`) | Kalanların sahibi başka |
| Diyalog kaydı | [SM] `SESLER/diyalog.json` v2 · [KU1] `KURGU_PLANI.diyalog[]` (metin + LUFS + yerleşim) | **Alan başına sahip:** `diyalog.json` v2 (ses) = replik varlığı (kaynak klip, kelime zamanları, dosya, `altyazi_metin`, ölçülen LUFS). `KURGU_PLANI.diyalog[]` (kurgu) = yalnız yerleşim (`replik` kimliği, `cizelge_bas`, `jl`, `ekran_disi`, `uzerindeki_planlar`) | Aynı metin ve ölçü iki yerde tutulmaz |
| Ambiyans, efekt, müzik yerleşimi | [KU1] `KURGU_PLANI` içinde · [SM] `KURGU/ses_parcalari.json`, `MUZIK/` | **Ses dosyalarında.** Her biri `_uretim.girdi_imza` ile hangi `KURGU_PLANI` sürümünden çözüldüğünü yazar; sürüm değişince bayat olur | Tek sahip |
| Bütçe | [KU1] `BUTCE.json` · [UM] `URETIM_ONIZLEME.json` | `URETIM_ONIZLEME.json → kredi.flow.dilimler`; `BUTCE.json` önerimi geri çekiyorum | Tek dosya |
| Kuyruklar | [UM] `KUYRUK/YENIDEN_URET.json` · [GS] `_RAPOR/YENIDEN_URET.json` · [CM] film kökü | Yer orkestratör sahibinin kararıdır. Önerim [UM]'nin `KUYRUK/`'u. **Şema tektir**: [UM] tabanı + benim alanlarım (§4.5.5) | Raporla kuyruk ayrılır |
| Rapor klasörü, çıkış kodu, ajan devri | [KU1] `_RAPOR/`, kod 4, `AJAN_ISLERI.json` · [UM] kod 3 · [CM] `_GOREV/`, `RAPORLAR/` · [SN2] `_RAPOR/` | `_RAPOR/` (çoğunluk ve mevcut kod); **çıkış 3 = ajan işi** ([UM]); görev devri [CM]'nin görev defteri (`_GOREV/<id>/`). Kendi kod 4'ümü ve `AJAN_ISLERI.json`'umu geri çekiyorum | Tek protokol |
| Kök neden sözlüğü | [KU1] §5.6 · [SN2] ekleri | `YZ_FILM/ARACLAR/veri/kok_neden.json`: [KU1] sözlüğü + [SN2] hikâye satırları (`bilgi_eksik`, `motivasyon_belirsiz`, `bilgi_durumu_ihlali`, `kanon_ihlali`, `ad_karisik`) + [SM] ses satırları | Bulgu yönlendirmesi ve ders defteri aynı sözlükle sayar |
| Ders defteri biçimi | beş ayrı biçim | [UM] ve [CM]'nin ortak biçimi (tek olay tek kayıt, terfi kuralı). Ben yalnız kurgu `kategori` değerlerini ve bağlam alanlarını eklerim (§4.8-e) | [YN2] Ç-20 ile aynı |

### 2.2 Araç ve ölçü sahipliği (İ-9'un tablosu)

| Ölçü ya da iş | Tek araç | Sahibi | Kullananlar |
|---|---|---|---|
| Zamana bağlı ölçüler: süre, parti oranı, vuruş, ASL, sahne süresi, tepki ve J/L oranı, ad/risk/merak/kurulum zamanları, duygu eğrisi | `zaman_cizelgesi.py` (kütüphane + CLI) | kurgu | hikâye odası (TH), yönetmen (`plan_denetim` T0), kurgu (T1–T3) |
| Komşuluk ölçüleri: aynı tip art arda, ölçek sıçraması, 180°, bakış, durum zinciri, dondurulmuş durum (Y58) | `plan_denetim.py`, `dunya_defteri.py`, `kroki.py` | yönetmen / süreklilik | `kurgu_denetim` içe alır ve `KURGU_PLANI` sırasıyla çağırır |
| Kırpma önerisi, adım eşleme, Z1 çıkış noktası önerisi | `kirp_oner.py` | kurgu | [GS] `kare_zinciri.py` (kareyi seçer), yönetmen (`sure_carpani` dersi) |
| Zincir karesinin çıkarılması | `kare_zinciri.py --cikar` | görüntü | kurgu kilitler (`kullanim_kilit: zincir`) |
| Animatik ve önizleme görüntüsü, ses mux'u | `kurgu_render.py` | kurgu | — |
| Ses stemleri (diyalog, efekt, ambiyans, müzik), son miks | `diyalog_esitle`, `ses_katmani`, `muzik --yerlestir`, `son_miks` | ses | `kurgu_render` stemleri alır |
| Diyalog yerleşimi (senkron formülü), cevap boşluğu, S3.6, J/L sınırları, ağzı oynayan yüze replik kesişimi | `kurgu_denetim.py` | kurgu | ses (`ses-denetcisi` raporu okur) |
| Ağız açıklığı dizisi, dudak ofseti, konuşan yüz kimliği | `dudak_denetim.py` | ses | `kurgu_denetim` dizileri okur |
| LUFS, kaplama, sessizlik, final ölçüsü | ses araçları + `kalite_denetim.py --final` | ses (final ortak) | kurgu Z3 kararında okur |
| İzleme kipinde kör paket | `kor_paket.py` içinde `izleme` modülü | kurgu (içerik), [CM] (çatı ve maskeleme) | `habersiz-seyirci`, `kesici` |
| Seyirci puanlarının birleştirilmesi | `puan_oku.py` v2 / `seyirci_topla` (tek kod) | ortak ([SN2] çatı) | bütün kipler |
| Bulgu yönlendirmesi | `bulgu_yonlendir` modülü ([SN2] `hikaye_odasi.py bulgu-sinifla` ile aynı kod) | senarist (çatı); her uzman kendi kök neden satırları | kurgu, yönetmen, süreklilik, ses |
| Kuyruk, öncelik, zincir etkisi, 0 kredi kuralı | `kuyruk.py` | kurgu | bütün kapılar yazar |
| Fiyat, bakiye, bütçe kapısı, dilimler | `kredi.py` | üretim | `kuyruk.py` sorar |
| CapCut taslağı, fark, yama, not | `capcut_film.py`, `taslak_fark.py`, `capcut_yama.py`, `notlari_oku.py` | kurgu | ses (parça listesi verir) |
| Dünya durumu defteri | `dunya_defteri.py` | süreklilik ([YN2] Ç-5) | kurgu kesme simülasyonu |

### 2.3 Aşama sırası (kurgu çevresi) ve kod eşlemesi
```
[YN2] Y4 birleştir + dünya defteri (K0) + Z0  →  [KU] KR0 T0 çizelgesi (zaman_cizelgesi --asama kagit)
 → [YN2] Y5–Y6 plan eleştirisi + plan seyircisi → [SM] A4–A7 ses kâğıtta → [YN2] Y7–Y8 istem + kamera ağacı
 → [GS] kart + başlangıç görselleri + G1 (+ devam planları için planlanmış görsel, Z2 bitiş görselleri)
     └─ P1'in G1'i bitince: [KU] KR3a P1 animatik ön turu (kapı değil; dersler P2/P3 planlarına)
 → [SM] A1–A3 ses kadrosu (animatikten önce bitmiş olmalı) → [SM] B1 replik süre kapısı (TTS)
 → [KU] KR1 T1 çizelgesi → KR2 animatik render ([SM] B2 stemleriyle) → KR3 animatik izleme ⟲ KR4 düzeltme + kesme turu
 → animatik ONAYLI → [UM] V09 kesin bütçe → [UM]/[GS] video dalgaları (Z1; [KU] KR5 çıkış kilidi) → V1/V2/V3
     └─ P1'in videoları bitince: [KU] KR8a P1 kurgu ön turu (kapı değil; dersler P2/P3 video dalgalarına)
 → [SM] C1–C3 ses → [KU] KR6 kaba kurgu T2 → KR7 ses katmanı + Z3 kararı → KR8 kurgu izleme ⟲ KR9 düzeltme / kesme / yeniden çekim
 → KR10 CapCut taslağı → (KR11 kullanıcı notu ya da düzenlemesi ⟲) → KR12 teslim
```

| Benim kodum | [CM] | [UM] | Ortam |
|---|---|---|---|
| KR0 T0 kâğıt çizelgesi | A07c | K10 | bulut / yerel |
| KR1–KR4 animatik (T1, render, izleme, düzeltme) | A12 | V07–V08 | yerel (bulutta yalnız `sahte`) |
| KR3a P1 animatik ön turu | A12 içinde | V08 içinde | yerel |
| KR5 zincir çıkış kilidi | A14 | U01, U04 | yerel |
| KR6–KR7 kaba kurgu ve Z3 | A16 | M01–M03 | yerel |
| KR8–KR9 kurgu izleme, düzeltme, kesme, yeniden çekim | A16 (+ A14) | M04–M05, U05 | yerel |
| KR8a P1 kurgu ön turu | A16 içinde | M04 içinde | yerel |
| KR10 CapCut | A16 sonu | M06 | yerel |
| KR11 kullanıcı notu | `film-not` | `NOTLARI_OKU.bat` | yerel |
| KR12 teslim | A17 başı | M07 | yerel |

**Ön turlar neden var?** B2'de Parti 1 ayrı olarak v7'den v11'e kadar düzeltildi ve dersleri sonraki partilere aktarıldı (H/proje-b2). Bütün film bitmeden yakalanan bir sistematik hata (ör. bir kurulumun hep kadraj dışında kalması), P2 ve P3'ün görsel emeğini ve video kredisini korur. Ön tur kapı değildir; geçme şartı yoktur. Değeri ilk iki filmde ölçülür: tek başına yakaladığı ve sonraki partilerde önlenen bulgu sayısı. Değer yoksa kaldırılır (açık soru 11).

### 2.4 Sorumluluk sınırları

| Konu | Tek sahibi | Kurgucunun yetkisi | Değişiklik yolu |
|---|---|---|---|
| Kırpma, sahne içi sıra, J/L, ekran dışına taşıma, kart zamanı, hız, ayna, yeniden kadraj, plan kesme (sahne içinde) | kurgucu (`KURGU_PLANI`) | doğrudan; sınırlar §4.7 | işlem listesi → `kurgu_uygula.py` |
| Plan metni, kadraj, eylem zinciri, yeni plan | yönetmen | gereksinimi yazar: `yeni_plan_iste.gereksinim` (ne ve neden) | `YENIDEN_YAZ` → yönetmen `onarim` kipi |
| Replik kelimeleri, ekran dışı köprü replik içeriği, sahne silme, birleştirme ve sahneler arası sıra | `hikaye-yazari` | kelime değiştirmeyen bölme ve taşıma serbest (kayıt düşülür); diğerleri için istek yazar | `replik_degisiklik_istegi`, `sahne_degisiklik_istegi` → [SN2] H15 |
| Kesici'nin sahne kesme önerisi | `hikaye-yazari` (sahne listesinin sahibi) | simülasyondan geçen öneriyi istek olarak iletir | onaylanırsa kanondan düşer ([SN2] H14) |
| Ses yolu, seviye, stemler, müzik seçimi | ses | olay tabanlı yerleşim girdisini verir; ölçüm raporunu okur | `ses-denetcisi` |
| Zincir karesinin seçimi | görüntü (`kare_zinciri.py`) | çıkış noktasını önerir ve kilitler | — |
| Fiziksel durum | betik (`dunya_defteri.py`) | kesme ve sıra değişikliği dondurulmuş durumla denetlenir | — |
| Kullanıcının CapCut kararı | kullanıcı | kilitli; hiçbir araç geri almaz | kullanıcının kendisi |

### 2.5 Yeniden çekim bütçesi (İ-3'ün tablosu)

| Dilim | Pay (temel kredinin oranı) | 40 dk film için (hesap) | Kaynak |
|---|---|---|---|
| Temel | 405 klip × 12 kredi = 4.860 | — | ZN §2.6, RE `kredi_klip_720p` |
| Görüntü, süreklilik, plan dili (G1 sonrası video tekrarları, V1/V2/V3) | 0,15 | ≈ 729 kredi ≈ 61 klip | [GS] B7 (tahmin) |
| Ses (S2 metin ve ses kapısı) | 0,07 | ≈ 340 kredi ≈ 28 klip | [SM] §8.3 (tahmin) |
| Kurgu (kurgu izleme bulguları, bağlayıcı plan) | 0,08 | ≈ 389 kredi ≈ 32 klip | [KU1] B12 (tahmin) |
| **Kapı payı toplamı** | **0,30** | **≈ 1.458 kredi** | [UM] C1 |
| RE hedefi (ders defteri izler) | 0,20 | ≈ 972 kredi | RE `kredi_yeniden_deneme_payi` |

- Kurgu dilimi plan başına en çok 2 yeniden çekimi kapsar ([UM] ile ortak sayaç).
- Kurgu dilimine teknik tekrar yalnız KRİTİK madde için ve hat denetçisi notuyla girer.
- Bütçe biterse kalan maddeler 0 kredi çözümüne düşer. KRİTİK için o da yoksa hat durur ve "X kredi gerekiyor" bildirimi gider. Bu bir soru değildir. Kalite kısılmaz (kesin karar 6).

### 2.6 Seyirci akışı: dört kipte tek model (uzlaşılan biçim)
1. **Tek ajan, tek rapor şeması:** `habersiz-seyirci`. Şemanın tabanı [SN2] §4.5.6'dır (o da [KU1] §5.3'ten türedi). İzleme kiplerinin ek alanları §4.5.3'tedir.
2. **Her turda 3 yeni örnek.** Birbirlerini okumazlar. `memory:` alanı ve `CLAUDE.md` okuma yoktur (`omitClaudeMd: true`, [CM]).
3. **Aşamalı girdi:** Seyirci filmi baştan sona sırayla izler. Önce yalnız P0 (0–120 sn) görünür. Her `izleme_parcasi` raporu yazılınca betik sonraki parçayı GIRDI'ye kopyalar ve ana Claude aynı örneği SendMessage ile sürdürür ([SN2] İ6, [CM] §2.2 #4). İlerisi teknik olarak okunamaz ([CM] `erisim_kapisi`).
4. **İlk 2 dakika testi ayrıdır:** başlık ve kapak imgesi tarifi + ilk 120 sn, 3 yeni seyirci ([SN2] H12 biçimi).
5. **Verilmeyenler:** `ekranda_bilgi`, `seyirci_ogrenir`, amaç, vuruş, merak defteri, kopukluk adayları (İ-1), önceki tur raporları, önceki film özeti ([SN2] İ2), plan tipi, kadraj etiketi (İ-7).
6. **Birleştirme:** `ozet-eslestirici` (kör) özetleri `anahtar_olgular` ile, açık soruları `MERAK_DEFTERI` ile karşılaştırır ve kopuklukları kimliklere eşler (İ-5). Betik medyanı alır, KRİTİK'leri birleştirir ve yönlendirir.
7. **Tek seyircinin KRİTİK'i** yalnız bağımsız bir hakem tarafından ve kanıtla geçersiz sayılabilir. Görsel bulgularda hakem `sureklilik-denetcisi`, hikâye ve akış bulgularında `yapimci` (doktor kipi) olur. Kanıt, paketteki sayfa, kare ya da satır ve zaman kodudur; betik kanıtın seyircinin paketinde, kopukluk anından önce ve maskesiz olduğunu doğrular ([SN2] H11 uyarlaması). **Kurgucu kendi kesimini aklayamaz.** Tur 1'deki "kurgucu kare kanıtıyla geçersiz sayar" kuralımı geri çekiyorum.

---

## 3. Diğerlerinden kabul edip kendi önerime kattıklarım

| Kaynak | Kabul ettiğim | Önerimdeki yeri |
|---|---|---|
| [CM] §2.0, §5.2–5.3, K-3, K-6 | Görev defteri (`film.py sonraki/basla/bitir`), `_GOREV/<id>/GIRDI` ve `CIKTI`, şablondan üretilen istem, `erisim_kapisi`, SubagentStop doğrulaması (≤ 2 düzeltme) | §4.3, §4.4; kurgucunun `kurgu_uygula --kuru` denetimi SubagentStop'ta |
| [CM] §3.1 | Ajanlarda Bash yok; `memory:` yok; kör rollerde `omitClaudeMd`; dönüş ≤ 5 satır; önce başlıkları yaz, bölüm bölüm doldur | §4.3 (kurgucu ve kesici) |
| [CM] §2.2 #4, [SN2] İ6 | Aynı tur içinde aynı seyircinin filmi bölüm bölüm izlemesi; aşamalı girdi | §2.6, §4.2 KR3, KR8 |
| [CM] §2.3 | Değerlendiricinin yarım işi sıfırdan yapılır, yazarınki devam ettirilir | §4.2 KR3 |
| [CM] `kesici` kör, `omitClaudeMd` | Kesiciye `ekranda_bilgi` verilmez; bağımlılıkları simülasyon yakalar. Tur 1 açık soru 8'imi bu yönde kapatıyorum | §4.3 |
| [UM] §2.0 | Çıktı zarfı ve girdi imzası; kredili çıktı asla silinmez, `bayat` işaretlenir; çıkış kodu 3 = ajan | §4.5.1 `_uretim` |
| [UM] §2.1, T4 | Video aşamasının girdi imzası animatik raporlarının imzasını içerir (animatik geçmeden video kodla başlamaz) | §4.8 (a), test 9 |
| [UM] C1, §5.7 | Kapı payı 0,30 (ilk film), RE 0,20 hedef; `KREDI_DEFTERI`; plan başına ≤ 2 yeniden çekim | §2.5 |
| [UM] hat-denetçisi | Yeniden çekim kuyruğu 30 klibi aşarsa ajan bakar | §4.2 KR9 |
| [UM] §6.4 | `kaset` sağlayıcısı (kayıtlı ajan çıktıları) ile ağsız uçtan uca test | §4.6.3 |
| [SN2] §2.4 | Kök nedene göre bulgu yönlendirmesi; hikâye bulgusu yazara, plan bulgusu yönetmene | §4.2 KR4, KR9 (İ-5 değişikliğiyle) |
| [SN2] H15 #2 | **Ekran dışı köprü replik** (Yol B TTS, Flow kredisi 0) | 0 kredi merdiveni #4 (§4.5.5) |
| [SN2] H12 | İlk 2 dk testinde seyirci başlığı ve kapak imgesi tarifini görerek girer | §4.2 KR3, KR8 |
| [SN2] H11 | KRİTİK geçersiz sayma hakemi ve betik kanıt doğrulaması | §2.6 madde 7 |
| [SN2] İ2 | Kapı seyircisine önceki film özeti verilmez | §4.8 (f); "previously" önerimi geri çektim |
| [SN2] §2.3 | Sahne silme ve birleştirme yazarın kararıdır | §2.4 |
| [YN2] İ-2 | Z1 varsayılan; her plana planlanmış görsel (animatik ve yedek) | §4.8 (d) |
| [YN2] İ-5, İ-10 | Tek kırpma alanı; `_derlenir.ayna_yasak` | §2.1 |
| [YN2] İ-11 | **Durum dondurma** (`uretim.durum_dondu`); kurgu sırası değişince Y58 | 0 kredi merdiveni #2 yalnız `etki`siz planlar; §4.7 |
| [YN2] Y54, Y55 | Örtülü devam; Z1 kaynağında kesme bitiş tutmasının içinde | §4.7 (İ-11 eklemesiyle) |
| [YN2] `plan_dili.py` | Animatik eylem şeridinin Türkçe metni aynı derleyiciden (`gorunur_tarif(dil="tr")`) | §4.2 KR2 |
| [YN2] adım kimliği `a1…a3`, `fiil_sozlugu.sure_carpani` | Kesme ve efekt adıma kimlikle bağlanır; ölçülen adım süreleri çarpanı kalibre eder | §4.5.1, §4.8 (e) |
| [GS] A15, R5 | Zincir karesi kesme çevresinden en durgun ve keskin kare; zincirli planlar arasına tepki/ekleme | §4.2 KR5 |
| [GS] A13–A14 | V1/V2 kusurlarının zaman damgası, V3 kesme anı karesi; kusur kullanılan pencerenin dışındaysa kırpma | `kirp_oner` girdileri |
| [GS] "ÖLÇÜLEMEDİ asla GEÇ değildir" | `kirp_oner` hareket başlangıcını bulamazsa güven düşer ve plan kurgucuya gider; sessizce geçmez | §4.6.2 |
| [SM] B2, §8.2 (a) | **İşitsel döküm** (konuşanın adı yok; "ekran dışı: daha önce duyduğun boğuk erkek sesi"); "ekran dışı sesi kime ait sandın?" sorusu | §4.5.4 |
| [SM] §8.2 (a) | Kurgu turunda döküm plandan değil **son miksten** (ASR): müzik bir repliği bastırdıysa seyirci onu "duymaz" | §4.5.4 |
| [SM] §6.1 | Klipler kanalı her zaman sessiz; tek "geçici akor" kaldırılır; 48 kHz | §4.6 `capcut_film` |
| [SM] S0.3 | Ses tanıtım kuralı: ekran dışı ses, karakter önce ekranda konuştuysa | merdiven #3 ve #4 şartı |
| [SM] §5.4 | `diyalog.json` v2; `altyazi_metin` = duyulan söz | §2.1, §4.8 (ses) |
| CA | Opus 5.5 bağlam penceresi 1M token, en çok 128K çıktı | §4.9 R4 (tek seyircinin bütün filmi izleyebilmesi) |

**Geri çektiklerim:** `kurgu-seyircisi` ajanı · `ONCEKI_OZET.md` · "önceki filmin seyirci özeti → previously" · `kurgucu`'da `memory: project` ve Bash ·
`ozet-eslestirici`'de Sonnet · `zanaat.sure_sn` ve `kesme.nokta_sn` · `kurgu.{ayna_yasak, vaat_imgesi, zincir_kaynagi}` · `BUTCE.json` ·
çıkış kodu 4 ve `_RAPOR/AJAN_ISLERI.json` · kurgucunun tek seyircinin KRİTİK'ini geçersiz sayması · `/film-yap uret` alt komutu
(kredi kapısı [CM] ve [UM]'deki gibi `film.py`'de; `disable-model-invocation`'lı beceriyi Claude açamaz) · `KURGU_PLANI` içindeki
`ambiyans/efektler/muzik` dizileri · Z3 #44–47'yi kendim ölçmem · kullanıcı düzenlemesinden sonra sıfırdan yeni sürüm kurmak.

---

## 4. REVİZE NİHAİ ÖNERİM

Bu bölüm tur 1 dosyamın yerine geçer ve kendi başına okunabilir. Tur 1'den farklı olan yerler **(değişti)** ya da **(yeni)** diye işaretlidir.

---

### 4.1 Alanımın hedefi ve başarı ölçütü (sayılarla)

**Hedef (tek cümle):** Kâğıttaki plan listesini **video kredisi harcanmadan önce** gerçek süreli bir animatik filmle, **kullanıcıya gösterilmeden önce** de kurgulanmış filmle, filmi baştan sona izleyen üç habersiz seyirciden geçirmek; ZANAAT'ın süre, ritim ve duygu eşiklerini dört zaman çizelgesinde aynı kodla ölçmek; kopuklukları önce 0 kredili kurgu çözümleriyle, yetmezse kurguya ayrılmış bütçeyle kapatmak; sonunda kullanıcıya boşluksuz, katmanlı, sürümlü bir CapCut taslağı ve bu taslağın dışa aktarımını doğrulayan bir yayın denetimi vermek.

**Bugünkü kodda alanımın durumu** (tur 1'de okundu, bu turda yeniden doğrulandı):
1. `capcut_film.py` her klibi `source_timerange=(0, L)` ile tam boy koyuyor; `kullanim{bas,sure}` hiçbir yerde uygulanmıyor. ZN §7.1'de "gereksiz uzun" notunun ilk kök nedeni budur.
2. `capcut_film.py` ortam sesini plan başına (her replikli klibin kendi ayrıştırılmış zemini) koyuyor. Klip geçişinde zemin değişiyor (DR: kapı sahnesi dersi).
3. Replik sesi klibin kendi aralığına kırpılıyor (`ln = min(..., us(t0)+L-st)`); L kesme yapılamıyor.
4. `izleme_paketi.py` kareleri tam klipten alıyor ve duyulan repliği konuşanın adıyla yazıyor (`MARA: "..."`). Seyirci adı ekranda duymadan öğreniyor.
5. `puan_oku.py` ortalama alıyor ve 3 ölçüt okuyor. ZN §7.2.10 ve §7.3 **medyan** ve **6 ölçüt** istiyor.
6. Animatik, kurgu kapısı, yeniden çekim kuyruğu ve taslak farkı kodda yok.

**Başarı ölçütleri**

| # | Ölçüt | Hedef | Kaynak |
|---|---|---|---|
| B1 | Animatik habersiz seyirci (3 yeni seyirci, bütün film) | GENEL medyan ≥ 8; hiçbir ölçüt medyanı < 7; KRİTİK 0; ORTA ≤ 3/parti; özet eşleşmesi ≥ 0,80/parti | RE `seyirci_*`, `kopukluk_*`, `ozet_eslesme_min`; ZN §7.3 |
| B2 | İlk 2 dk testi (animatik ve kurgu; başlık + kapak imgesi tarifiyle) | 3/3 "devam ederdim" | RE `ilk2dk_devam_evet_min`; [SN2] H12 biçimi **(değişti)** |
| B3 | Kurgu izleme (kare paketi, bütün film) | B1 ile aynı eşikler; ≤ 3 tur (+ koşullu kurtarma, §4.2 KR9) | RE `kurgu_tur_max` |
| B4 | Zaman çizelgesi kapıları T0–T3 | HATA 0; geri gidiş yok (Tk'de geçen ölçü Tk+1'de HATA olamaz; kullanıcı kararından doğan HATA BAYRAK'a döner) | ZN §6.2 |
| B5 | Film süresi | 1800–2700 sn (kart + jenerik dahil); dolgu yok | RE `film_sure_aralik_sn`, ZN §2.5.5 |
| B6 | ASL | film 4,2–5,2 sn; ilk 120 sn ≤ 4,0; ilk 30 sn ≤ 3,5; parti hedefi ±0,6 | RE `asl_*`, `ilk120_asl_max_sn`, `ilk30_asl_max_sn` |
| B7 | Diyalog sahnesinde tepki planı / J-L kesme oranı | ≥ %25 / ≥ %30 | RE `tepki_orani_min`, `jl_kesme_orani_min` |
| B8 | Görünen konuşanın replik yerleşimi (senkron formülü) | formülden fark 0 ±1 kare (24 fps). Ölçülen dudak ofseti [SM] S3.1'de: repliklerin ≥ %95'i ≤ 42 ms | [KU1] §5.1; [SM] B1 |
| B9 | Dudağı oynayan yüzün üstüne başkasının repliği | 0 | H/video-istem-kurali, BK §5.1.8 |
| B10 | CapCut taslağı | boşluk 0; eksik medya 0; taslak ↔ `KURGU_PLANI` farkı 0; kullanıcı düzenlemesinden sonra Klipler kanalı ve kullanıcının eklediği öğeler değişmemiş (özet eşit) **(değişti)** | H/capcut-elle-duzenleme, BK §5.3.3 |
| B11 | Kesme turu | animatikte ve kurguda yapılır; uygulama oranı ≥ 0,5 (payda: simülasyondan HATA'sız geçen öneriler; İ-6); kesilen plana video kredisi harcanmaz | RE `kesme_turu_oneri`; ZN §7.2.9 |
| B12 | Kurgu kaynaklı yeniden çekim | ≤ temel kredinin %8'i (tahmin; kurgu dilimi, §2.5); 0 kredi kuralını atlayan kuyruk maddesi 0 **(yeni)** | İ-3 |
| B13 | Kullanıcı notu | notların %100'ü `NOT_CEVAPLARI.md`'de bir kararla kapanır; kullanıcı kararı aynen uygulanır; kullanıcının kaynak taslağına yazma 0 | BK §5.3.3; [KU1] B13 |
| B14 | Yayın dosyası **(yeni)** | "aynı çizelge" kanıtı olmadan ses değiştirme 0; final −14 ±1 LUFS, ≤ −1 dBTP ([SM] ölçer); siyah kare, donma, planlanmamış sessizlik 0 | İ-2; RE `final_lufs`, `true_peak_max_dbtp` |
| B15 | Habersizlik **(yeni)** | seyirci ve kesici paketinde yasak alan (amaç, `ekranda_bilgi`, kopukluk adayı, kadraj etiketi, plan tipi) 0; ad ilk kez sözle söylenmeden pakette maskesiz geçmez | İ-1, İ-7; ZN §7.3; [SN2] maske |

**Ölçeği göstermek için:** B2'de animatik atlanmıştı (H/proje-b2) ve 50'den fazla yeniden çekim olmuştu (`04_KIM_NE_YAPTI.md`). İlk taslaktaki 134 video klibine oranla bu ≈ %37'dir (hesap). B12'nin %8 hedefi, kopuklukların çoğunun animatikte, yani kredisiz yakalanacağı varsayımına dayanır (tahmin). Gerçek oran ilk filmde ölçülür ve ders defterine yazılır.

---

### 4.2 Aşama aşama süreç: girdi → iş → çıktı → geçme şartı → kim

**Temel ilke: tek veri yapısı, dört zaman çizelgesi.**
- `SAHNELER.json` **neyin üretileceğini** söyler, `KURGU_PLANI.json` **neyin nasıl kullanıldığını** söyler. Ölçülen her şey (gerçek kırpma, J/L, kullanıcının CapCut kararı) `KURGU_PLANI`'na yazılır. `SAHNELER.json`'da yalnız yönetmenin planı kalır.
- Aynı çizelge dört kez, her seferinde daha gerçek verilerle kurulur ve **aynı kodla** (`zaman_cizelgesi.py`) ölçülür. Hikâye odasının TH çizelgesi (sahne hedef süreleriyle, ±%15 bant, [SN1] §7) de aynı kütüphaneyi kullanır.

| Çizelge | Ne zaman | Plan süresi nereden gelir | Ses nereden gelir |
|---|---|---|---|
| **T0 kâğıt** | yönetmen Y4'te `SAHNELER.json` birleşince | `_derlenir.sure_sn` (= `kullanim.sure`); diyalogda ZN §2.3 formülü | yok (formül) |
| **T1 animatik** | G1 ve [SM] B1 bitince | T0 + TTS ile ölçülen gerçek replik süreleri | [SM] B1 TTS (seçilmiş evren sesi) |
| **T2 kurgu** | videolar V1/V2/V3'ten ve ses C1–C2'den geçince | `kirp_oner.py`'nin ölçtüğü kırpma | [SM] Yol A dönüşmüş Veo sesi ya da Yol B TTS |
| **T3 kullanıcı** | kullanıcı CapCut'ta değişiklik yaparsa | kullanıcının kırpması (kilitli) | aynı |

Görev türleri [CM]'nin görev defterindeki gibidir: **betik** (`film.py` alt komutu), **ajan** (`_GOREV/<id>/`), **kullanıcı eylemi** (yalnız fiziksel iş).

#### KR0 — Kâğıt zaman çizelgesi (T0)
- **Girdi:** `SAHNELER.json` (zanaat alanları, `_derlenir.sure_sn`, `zanaat.kesme`, eylem adımları `a1…a3`), `HIKAYE.json` (vuruşlar, duygu haritası, `anahtar_olgular`, `MERAK_DEFTERI`, `KURULUMLAR`, vaat sözleşmesi), RE.
- **İş:** `zaman_cizelgesi.py --asama kagit`:
  - Planları `sira` ile dizer. Kartları (başlık, yer/zaman), seri kancasını ve jeneriği ekler.
  - Planlanan J/L'yi `zanaat.kesme.ses_tasma_sn`'den uygular. Diyalog süresi ZN §2.3 formülüyle gelir.
  - Olay listesini çıkarır: her ad, risk, merak, kurulum, vaat ve vuruş olayının saniyesi.
  - Zamana bağlı ölçüleri hesaplar (§4.7.1 T0 sütunu).
- **Çıktı:** `KURGU/surumler/KURGU_PLANI_T0.json`, `_RAPOR/ZAMAN_T0.json`, `_RAPOR/OLAYLAR_T0.json`, `_RAPOR/EGRI_T0.png` (hedef eğri ile plan eğrisi aynı grafikte).
- **Geçme:** zamana bağlı HATA 0. BAYRAK'lar bulgu yönlendirmesiyle (§2.4 [SN2]) yönetmene ya da yazara gider; revizyonu metni yazan yapar (YR §1).
- **Kim:** betik. Yönetmen aşamasının Y4 adımı içinde çağrılır ([YN2] §2.3).

#### KR1 — Animatik çizelgesi (T1)
- **Girdi:** T0; [SM] B1 çıktıları (`_RAPOR/S2a_replik_sure.json`, `SESLER/diyalog.json` animatik kayıtları: TTS dosyası, kelime zamanları); G1 GEÇ görsel listesi; Z2 bitiş görselleri ve `devam` planlarının planlanmış görselleri.
- **İş:** `zaman_cizelgesi.py --asama animatik`:
  - Formül süresini gerçek TTS süresiyle değiştirir. Sığmayan replik zaten [SM] B1'in HATA'sıdır ve yönetmene ya da yazara döner.
  - Cevap boşluğunu (RE `cevap_boslugu_sn` 0,2–0,6) ve J/L'yi gerçek sesle yerleştirir. Ölçüleri yeniden hesaplar.
  - Plan süresinin T0'dan sapmasını yazar.
- **Çıktı:** `KURGU_PLANI_T1.json`, `_RAPOR/ZAMAN_T1.json`, `_RAPOR/SAPMA_T1.json`.
- **Geçme:** T0 ile aynı; geri gidiş yok. Plan başına ±%25'ten büyük sapma BAYRAK'tır (tahmin).
- **Kim:** betik.

#### KR2 — Animatik render (video kredisi yok)
- **Girdi:** T1; `SIRALI_GORSEL/` (yalnız G1 GEÇ); bitiş görselleri; ses stemleri ([SM] B2: `ses_katmani --animatik`, hazırsa `muzik --uret`, `son_miks --animatik`); evren kart şablonları; eylem şeridi metinleri (`plan_dili.gorunur_tarif(dil="tr")`, [YN2]).
- **İş:** `kurgu_render.py --animatik`:
  - Her plan kendi `sure`'si kadar ekranda kalır.
  - Durağan kareye `hareket_tipi`'nden türetilen yavaş hareket uygulanır: `yavas_ileri` %8 yakınlaşma, `yavas_geri` %8 uzaklaşma, `yavas_pan` %2–4 kayma, `sabit` %2 "nefes" (kurgu köprüsü V5 varsayılanları).
  - **(yeni)** Bitiş görseli olan planda (Z2 ya da `devam`), son adımın bitişinde 0,5 sn'lik çapraz geçişle bitiş görseline geçilir (süre tahmin). Seyirci eylemin sonucunu görür ([GS] §8.3).
  - Eylem şeridi kadrajın altında, adımın saniyesinde, ayırt edici italik yazıyla çıkar. Yalnız görünür eylem yazılır; amaç, risk, vuruş yazılmaz.
  - Kartlar bindirilir. Yazılar PIL ile şeffaf PNG olarak çizilir (Windows'ta `drawtext` font yolu sorunu yaşanmaz).
  - Ses stemleri mux edilir. Karışımın −14 LUFS'u [SM] `son_miks`'tedir.
  - Görseli eksik plan yer tutucuyla (gri kare + plan numarası + şerit) gösterilir.
  - Plan başına önbellek tutulur; girdisi değişmeyen parça yeniden kodlanmaz.
- **Çıktı:** `ANIMATIK/animatik_v<N>.mp4` ve parti dosyaları. İsteğe bağlı aynı içerikte CapCut taslağı "YZ <FILM> ANIMATIK v<N>" (yalnız `--onayli` modda ya da kullanıcı isterse).
- **Geçme:** süre = T1 toplamı ±1 kare (HATA, İ-4). `kalite_denetim.py`: planlanmamış siyah ya da sessizlik 0. Yer tutucu oranı ≤ %10 (tahmin); üstündeyse animatik izletilmez, görsel aşamasına dönülür.
- **Kim:** betik.

#### KR3 — Animatik izleme turu (tur n)
- **Girdi:** KR2 çıktıları; işitsel döküm ([SM] B2 `ANIMATIK/ISITSEL_DOKUM.md`); `HIKAYE.json → anahtar_olgular`, `MERAK_DEFTERI`; karakter maskeleri.
- **İş:**
  1. **Paket** — `kor_paket.py --kip animatik --tur n`:
     - Parçalar: `P0` (0–120 sn), sonra sahne sınırından kesilen `izleme_parcasi`'lar (240–300 sn).
     - Sayfa: 6 plan × 1 kare. Bitiş görseli varsa ikinci kare eklenir. Her karenin altında eylem şeridi.
     - `IZLE.md`: zaman kodu, plan numarası, süre, duyulan (işitsel döküm biçimiyle), efekt, müzik ve sessizlik satırı (§4.5.4).
  2. **Seyirciler:** 3 yeni `habersiz-seyirci` (kip `animatik`), paralel. Aşamalı girdiyle filmi baştan sona izler. Her parça sonunda parça raporu, her parti sonunda parti puanı, film sonunda genel puan yazar.
  3. **İlk 2 dk testi:** 3 yeni seyirci (kip `ilk2dk`; başlık + kapak imgesi tarifi + P0).
  4. **Eşleştirme:** her seyirci için `ozet-eslestirici` (kipler `ozet` ve `bulgu`).
  5. **Toplama** — betik `seyirci_topla`: medyanlar, KRİTİK birleştirme (aynı plan ±1), özet eşleşmesi, ilgi ↔ duygu haritası korelasyonu, ortak sıkılma anları, bulgu yönlendirmesi.
- **Çıktı:** `_RAPOR/SEYIRCI/animatik_t<n>/s<k>_rapor.md/.json`, `s<k>_eslesme.json`, `_RAPOR/SEYIRCI_KARAR_T1_t<n>.json`, `_RAPOR/BULGU_YONLENDIRME_T1_t<n>.json`.
- **Geçme:** B1 + B2.
- **Kim:** betik + ajanlar (görev defterinde paralel grup). Yarım kalan seyirci görevi sıfırdan, yeni örnekle yeniden yapılır ([CM] §2.3).

#### KR3a — P1 animatik ön turu (yeni; kapı değil)
- **Ne zaman:** P1'in G1'i ve P1 replik TTS'leri bitince, P2/P3 görselleri üretilmeden önce.
- **İş:** KR2 + KR3, yalnız P0 + P1 için, 3 seyirciyle. İlk 2 dk testi de burada bir kez koşar.
- **Çıktı:** aynı biçimde `animatik_on_P1`. Bulgular sahiplerine gider (P1 düzeltilir). Kök neden kalıpları yönetmen ve yazara **ders adayı** olarak verilir (P2/P3 planları yazılmadan ya da görselleri üretilmeden önce).
- **Geçme:** yok (öğrenme turu). Tur sayısına sayılmaz.
- **Değerinin ölçümü:** ön turun tek başına yakaladığı ve P2/P3'te önlenen bulgu sayısı ders defterine yazılır. İki filmde değer yoksa ön tur kaldırılır.

#### KR4 — Animatik düzeltmesi ve kesme turu
- **Girdi:** `SEYIRCI_KARAR_T1_t<n>`, `BULGU_YONLENDIRME_T1_t<n>`, T1, [GS] K1-ön raporu (kurgucu için; seyirci görmez, İ-1), dondurulmuş durumlar (`uretim.durum_dondu`, görsel üretilince yazılır, [YN2] İ-11).
- **İş:**
  1. **Yönlendirme:**
     - Kurgu kök nedenleri `kurgucu` (`duzelt` kipi) → işlem listesi `KURGU/KURGU_KARARLARI_T1_t<n>.json`.
     - Yönetmen kök nedenleri → `YENIDEN_YAZ` (plan; görseli 0 kredi yeniden üretilir, G1).
     - Hikâye kök nedenleri → [SN2] H15 (dar değişiklik; önce 0 kredili basamaklar).
     - Süreklilik bulguları → [GS] (görsel düzeltme, 0 kredi).
     - Ses bulguları → [SM] (replik süresi, ses seçimi, ses tanıtım kuralı).
  2. **Kesme turu (yalnız tur 1):** kör `kesici` ajanı en çok 10 plan + 2 sahne önerir. Girdisi kör paket + seyircilerin ortak sıkılma anları + medyan ilgi eğrisidir. `kurgu_denetim --kesme-simule` her öneriyi çizelgeden çıkarır ve Z0/Z1/Z2 + Y58'i (dondurulmuş durumla) yeniden koşar. Simülasyondan HATA'sız geçenlerin ≥ %50'si uygulanır (İ-6). Plan kesmelerini kurgucu uygular; sahne kesmeleri yazara istek olarak gider (§2.4).
  3. **İşlem listesi denetimi:** `kurgu_uygula.py --kuru` SubagentStop kancasında çalışır ([CM] K-6). HATA varsa ajana geri döner (≤ 2 kez). Geçerse betik `--uygula` ile yeni `KURGU_PLANI_T1` sürümünü yazar.
  4. **Yalnız değişenler yeniden:** değişen planların görselleri (0 kredi) ve G1 → KR1–KR3. Render önbelleği yalnız değişen parçaları kodlar.
- **Çıktı:** `KURGU_KARARLARI_T1_t<n>.json`, `YENIDEN_YAZ` maddeleri, `KESME_ONERI_T1.json`, `_RAPOR/KESME_SIMULE_T1.json`, yeni `KURGU_PLANI_T1`.
- **Geçme:**
  - B1 + B2 sağlanınca `FILM_DURUM`'a `animatik: ONAYLI` ve imzası yazılır. Video aşamasının girdi imzası bu raporun imzasını içerir ([UM] T4); animatik geçmeden video kodla başlamaz.
  - Tur sınırı 3'tür (tahmin; [UM] aynı).
  - 3 turda geçmezse **kurtarma:** `yapimci` (doktor kipi, yeni örnek) yapısal teşhis yazar, sahipler uygular, en çok 2 ek tur yapılır (tahmin).
  - Yine geçmezse **DUR** ve engel bildirimi (soru değil). Video aşaması kapalı kalır (kesin karar 6; [SN2] İ10 ile aynı ruh). `--onayli` modda animatik kullanıcıya gösterilir; tam otomatikte dosya hazır tutulur, kullanıcı beklenmez.
- **Kim:** `kurgucu`, `kesici`, sahipler (yönetmen, yazar, görüntü, ses), betikler.

#### KR5 — Kare zinciri çıkış noktası (video dalgalarının içinde)
- **Girdi:** `zanaat.zincir.gecis_turu: devam` olan A→B çifti; A'nın videosu (V1/V2/V3 GEÇ); [YN2] Y55.
- **İş:**
  1. `kirp_oner.py --zincir A`, A için çıkış penceresini önerir: son adımın ölçülen bitişi + ≥ 0,2 sn ile `klip_sn − 0,5` arası (Y55). Pencerede hareket enerjisinin en düşük olduğu bölge işaretlenir.
  2. `kare_zinciri.py --cikar` ([GS] A15) bu pencereden en keskin ve en durgun kareyi seçer.
  3. Kurgu A'nın `kullanim.bas + sure` değerini o kareye **kilitler** (`kullanim_kilit: "zincir"`). B'nin başlangıç görseli bu kare olur ve G1-zincir'den geçer.
  4. **Dikiş:** B doğrudan bitişikse (`dogal_durak: true`) B'nin `kullanim.bas` değeri, B'de hareketin ölçülen yeniden başlama anı − 0,1 sn olur. Değilse araya örtü planı girer; süresi İ-11 formülüyle hesaplanır.
- **Çıktı:** `SIRALI_GORSEL/<B>.jpg` ([GS]), `KURGU_PLANI`'nda A'nın kilidi, `_RAPOR/ZINCIR_P<n>.json` ([GS]).
- **Geçme:** zincir derinliği ≤ 2 (A2 §2.3); kilit kaydı var; örtü kuralı sağlanıyor.
- **Kim:** betik (`film.py` video dalgası çağırır).
- **Not:** A yeniden çekilirse B de yeniden çekilmek zorundadır. Kuyruk bu maliyeti `zincir_etkisi` ile önceden gösterir.

#### KR6 — Kaba kurgu (T2)
- **Girdi:** bütün videolar ve V1/V2/V3 raporları (kusurların zaman damgalarıyla); `SESLER/diyalog.json` v2 ([SM] C1–C2: Yol A dönüşmüş ses ya da Yol B TTS, kelime zamanları); T1; `SAHNELER.json`; dondurulmuş durumlar.
- **İş:** `plan_kurgu.py`:
  1. Her plan için `kirp_oner` (§4.6.2): `kullanim` + `guven` + `gerekce`.
  2. Diyalog **senkron formülüyle** yerleşir. Ekran dışı replikler (kaynak klipten L taşması ya da TTS) ve J/L, Y31 ek koşullarıyla (§4.7.3) yerleşir. Kartlar eklenir.
  3. `zaman_cizelgesi --asama kurgu`: T2 ölçüleri ve `SAPMA_T2` (T1 ↔ T2).
  4. Ses stemleri bu sürümün imzasıyla yeniden üretilir: `ses_katmani`, `diyalog_esitle`, `muzik --yerlestir` (olay çözümüyle, İ-8), `son_miks` ([SM] D1–D5).
  5. `kurgu_render.py --onizleme` (720p + miks; plan önbellekli; parti başına dosya).
- **Çıktı:** `KURGU_PLANI_T2_v<N>.json`, `KURGU/onizleme_v<N>.mp4`, `_RAPOR/ZAMAN_T2_v<N>.json`, `_RAPOR/SAPMA_T2.json`, `KURGU/KIRP_INCELE.md`.
- **Geçme:** KR7 Z3 kararı; geri gidiş yok. Güveni < 0,6 olan kırpmalara (tahmin) `kurgucu` (`kirp_incele` kipi) karelerle bakar.
- **Kim:** betikler + `kurgucu`.

#### KR7 — Z3 kurgu kapısı
- **Girdi:** KR6 çıktıları; [SM] S3–S7 raporları (dudak, diyalog seviyesi, ambiyans/efekt, müzik, miks); [GS] K1 raporu.
- **İş:** `kurgu_denetim.py`:
  - Çizelge aritmetiği: senkron formülü, cevap boşluğu, bölünmüş klipte atlanan aralığın bir sözle kesişmesi (S3.6), J/L sınırları ve Y31 ek koşulları, ağzı oynayan yüzün üstüne başkasının repliği (ağız dizisi [SM]'den), Y54/Y55, kullanım pencereleri (Z3 #41–43).
  - Komşuluk ölçüleri yeni sırayla ve dondurulmuş durumla (Z0 #11, #12, #16–18; Y58).
  - T2 zaman ölçüleri.
  - [SM] raporlarının birleştirilmesi (Z3 #44–47); kurgu bunları kendisi ölçmez (İ-9).
- **Çıktı:** `_RAPOR/Z3_v<N>.json`.
- **Geçme:** HATA 0.
- **Kim:** betik.

#### KR8 — Kurgu izleme turu (tur n ≤ 3)
- **Girdi:** önizleme, `KURGU_PLANI`, **son miksten** çıkarılmış işitsel döküm ([SM] §8.2 (a): ASR + ölçülen olaylar).
- **İş:** KR3 ile aynı akış, farkları:
  - Paket `kor_paket.py --kip kurgu`: sayfada 6 plan × 3 kare. Kareler **kırpılmış pencereden** alınır: baş + 0,15 sn, orta, son − 0,15 sn. Ardışık planlar alt alta dizildiği için üçlü pencere korunur: önceki satırın son karesi → bu satırın ilk karesi. Sayfanın en üstünde önceki sayfanın son karesi küçük olarak durur.
  - "Duyulan" satırı son miksin ASR'sidir. ASR ↔ `altyazi_metin` WER'i > 0,30 olan replik (S7.6 HATA eşiği) "(anlaşılmayan konuşma)" diye yazılır: müzik bastırdıysa seyirci o repliği duymaz.
  - **Her tur bütün film, 3 yeni seyirciyle izlenir.** Bunun iki nedeni var: (1) geri gidiş (geçen bir partinin kesme sonrası bozulması) ancak tam izlemede görülür; (2) önceki partilerin bilgisi özetle değil izlemeyle gelmelidir ([SN2] İ2'nin film içi karşılığı). Tur 1'deki "yalnız geçemeyen partiler + önceki seyirci özeti" önerimi geri çekiyorum.
- **Çıktı:** `_RAPOR/SEYIRCI/kurgu_t<n>/…`, `_RAPOR/SEYIRCI_KARAR_T2_t<n>.json`, `_RAPOR/BULGU_YONLENDIRME_T2_t<n>.json`.
- **Geçme:** B3 + B2.
- **Kim:** betik + ajanlar.

#### KR8a — P1 kurgu ön turu (yeni; kapı değil)
- **Ne zaman:** P1'in videoları ve sesi bitince, P2/P3 video dalgalarından önce.
- **İş:** KR6–KR8, yalnız P0 + P1, 3 seyirci.
- **Çıktı:** dersler P2/P3 dalgalarına (yönetmen: plan dili; görüntü: G1 eşikleri; ses: yol kuralı). P1'in kendi düzeltmesi KR9 ile yapılır.
- **Geçme:** yok. Değeri KR3a gibi ölçülür.

#### KR9 — Kurgu düzeltmesi, kesme turu ve yeniden çekim kuyruğu
- **Girdi:** `SEYIRCI_KARAR_T2_t<n>`, `BULGU_YONLENDIRME_T2_t<n>`, Z3, K1, V raporları, `URETIM_ONIZLEME.json` (dilimler).
- **İş:**
  1. `kurgucu` (`duzelt` kipi) kendi kök nedenlerini ve sahibi bulunamayan bulguları **0 kredi merdiveninden** geçirir (§4.5.5) → `KURGU_KARARLARI_T2_t<n>.json` → SubagentStop'ta `kurgu_uygula --kuru` → betik `--uygula`.
  2. Diğer sahiplerin **kredili** önerileri kuyruğa girmeden önce `kurgucu` (`sifir_kredi` kipi) bakar: kırpma, J/L, ekran dışı köprü replik, alternatif çekim, örtü planı yeterli mi? Sonuç maddeye `sifir_kredi` alanı olarak yazılır (İ-3).
  3. Tur 1'in sonunda kesme turu yapılır (KR4'teki gibi).
  4. `kuyruk.py --topla --onizleme`: `YENIDEN_URET` (öncelik, zincir etkisi, dilim) ve güncel `URETIM_ONIZLEME`.
  5. Kredili madde varsa video aşaması görev olarak açılır (`film.py`; Memmet; Flow uyarısında DUR; bot atlatma YOK) → V1/V2/V3 → değişen planlar için KR6 (efekt ve müzik yeniden yerleşir; DR "yeni çekilen planlar efektsiz kalıyordu") → KR7 → yeni KR8 turu.
  6. Kuyruk 30 klibi aşarsa hat denetçisi bakar ([UM]; sayı tahmin).
- **Çıktı:** `KURGU_KARARLARI_T2_t<n>.json`, `YENIDEN_URET` maddeleri, `URETIM_ONIZLEME.md`, yeni `KURGU_PLANI` sürümü.
- **Geçme:**
  - KRİTİK madde kuyrukta kalmaz.
  - Kurgu dilimi biterse kalan maddeler 0 kredi çözümüne düşer. KRİTİK için o da yoksa hat DURUR ve "X kredi gerekiyor" bildirimi gider. KRİTİK'li taslak kullanıcıya verilmez.
  - 3 turda B3 sağlanmazsa **koşullu kurtarma:** son turda GENEL medyan ≥ 0,5 arttıysa ve kalan KRİTİK'lerin 0 kredi ya da bütçeli çözümü varsa en çok 2 ek tur yapılır (tahmin).
  - O da yetmezse en iyi medyanlı sürüm taslak yapılır ve eksikler raporda açıkça yazılır (BK §7.13 "yüzüne vur"). [SN2] bu maddeye itiraz etmedi.
- **Kim:** `kurgucu`, `kesici`, sahipler, betikler.

#### KR10 — CapCut taslağı
- **Girdi:** son `KURGU_PLANI`; [SM] ses parça listesi (`KURGU/ses_parcalari.json`) ve müzik yerleşimi; altyazı için `diyalog.json` v2 `altyazi_metin`.
- **İş:** `capcut_film.py` sürümlü bir taslak kurar: "YZ <FILM> v<N>".
  - Sürüm klasörü `KURGU/surumler/v<N>/`: kırpma ve 1080p türevleri bu klasöre sürüm adıyla yazılır. Eski sürüm taslakları bozulmaz (DR; BK §5.3.8).
  - Kanallar: Klipler (kırpılmış, **sessiz**), Bantlar, Kartlar, Altyazi, Diyalog (replik replik), Efekt, Ambiyans (sahne parçaları), Muzik (ipucu parçaları), NOTLAR.
  - Segment ↔ plan eşlemesi `KURGU/son_capcut_projesi.json` v2'ye yazılır (§4.5.8).
- **Çıktı:** CapCut taslağı, `son_capcut_projesi.json`, `KURGU/altyazi_en.srt`.
- **Geçme:** yeni kurulan taslakta `taslak_fark.py --oz-denetim` farkı 0; boşluk 0; eksik medya 0; süre = `KURGU_PLANI` ±1 kare.
- **Kim:** betik. Ana Claude kullanıcıya tek mesajla "taslak hazır" der; soru sormaz.

#### KR11 — Kullanıcı notu ya da düzenlemesi (isteğe bağlı döngü)
- **Tetik:** kullanıcının "değiştirdim / not bıraktım" demesi ([CM] `film-not`). Kullanıcı yalnız soru sorduysa dosyaya dokunulmaz ([CM] `film-durum`; BK §7.1).
- **İş:**
  1. **CapCut kapalı mı?** Değilse kullanıcı eylemi: "CapCut'ı kapat." Bitiş CapCut süreci kapanınca kendiliğinden algılanır.
  2. `taslak_fark.py` (salt okunur; `draft_content.json` + `Timelines/` kopyası + birleşik klip içi) ve `notlari_oku.py` (notu segment eşlemesiyle plana bağlar).
  3. `kurgucu` (`not` kipi): `TASLAK_FARK` + `NOTLARIM` → işlem listesi (kullanıcı kararları `kaynak: kullanici`, kilitli) + `NOT_CEVAPLARI.md`. Ses notları [SM] kuyruğuna, hikâye notları yazara bulgu yönlendirmesiyle gider.
  4. `kurgu_uygula` → `kurgu_denetim --hepsi`: kurulum (Z1), dondurulmuş durum (Y58; kullanıcı kararında BAYRAK), senkron, dudak ([SM]), ambiyans/efekt/müzik yeniden yerleşimi ([SM]).
  5. **Taslak karar ağacı** (§4.5.7):
     - Fark yoksa → KR10 yeni sürüm.
     - Fark varsa → `capcut_yama.py`: kullanıcının taslağı klonlanır, klonda yalnız bizim kanallarımız yamanır, öz denetim yapılır. Başarısızsa kullanıcının kararlarıyla yeni adla taslak kurulur.
  6. **Kullanıcı kesmesi yeni KRİTİK doğurursa** (ör. kurulum taşıyan planı kesti; DR "miğferin inişi"):
     - Kullanıcının kararı geri alınmaz.
     - Köprü yalnız bizim kanallarla kurulabiliyorsa (ekran dışı köprü replik, yer kartı) klonda uygulanır.
     - Köprü Klipler'e plan eklemeyi gerektiriyorsa kullanıcının taslağına dokunulmaz; ayrı bir "öneri taslağı" kurulur.
     - Kullanıcıya her iki durumda bir cümleyle bilgi verilir (soru değil).
- **Çıktı:** `KURGU/TASLAK_FARK.json`, `KURGU/NOTLARIM.json`, `KURGU/NOT_CEVAPLARI.md`, `_RAPOR/YAMA_v<N>.json`, klon ya da yeni sürüm taslak.
- **Geçme:** B10 + B13.
- **Kim:** betikler + `kurgucu` + kullanıcı eylemi (yalnız CapCut'ı kapatmak).

#### KR12 — Teslim (kurgu payı)
- **İş:**
  1. NOTLAR kanalı olmayan **yayın taslağı** kurulur (kullanıcının klonu söz konusuysa klonun NOTLAR'sız kopyası; BK §5.3.10).
  2. Kullanıcı eylemi: CapCut'tan 4K 24 fps dışa aktarıp `YAYIN/` klasörüne koymak (BK §8 #8). Bitiş, dosya gelince algılanır.
  3. `kalite_denetim.py --final` + **yayın doğrulaması** (§4.5.8): süre, ses çapraz korelasyonu, siyah kare, donma, sessizlik. Kanıt varsa ve ölçüm gerektiriyorsa `son_miks --mux` çalışır ve sonra yeniden ölçülür. Kanıt yoksa KR11'e dönülür (İ-2).
  4. `yayin_kaynagi: master` kurulum ayarı seçiliyse `kurgu_render.py --yayin` aynı denetimlerle yayın dosyasını kendisi üretir. Bu durumda kullanıcı eylemi yoktur.
  5. Bölüm zamanları: `KURGU_PLANI`'ndaki parti ve vuruş sınırları + `HIKAYE.json → bolum_adlari` → yayın paketçisi. Short pencereleri de `KURGU_PLANI` çizelgesinden alınır.
  6. Kurgu dersleri deftere işlenir (§4.8-e).
- **Geçme:** B14.
- **Kim:** betik + kullanıcı eylemi (dışa aktarım) + ana Claude (bilgi mesajı).

---

### 4.3 Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı)

**Ortak kurallar** ([CM] §3.1; kullanıcının kuralı H/ajan-opus-yuksek):
- Bütün ajanlar `model: opus` (= `claude-opus-5-5`) ve `effort: high`. Opus 5.5'te effort varsayılanı `medium` olduğu için açıkça yazılır (CA).
- `memory:` alanı yoktur. Bash yoktur. Okuma ve yazma, `erisim_kapisi` kancasıyla görev klasörüne bağlanır.
- Deterministik her iş betiktedir. Ajan `KURGU_PLANI`'nı **elle düzenlemez** (makine sahipli dosya); bir işlem listesi yazar, betik doğrulayıp uygular (AR3 B4: plan → doğrula → uygula).
- Dönüş ≤ 5 satırdır: çıktı yolu + `OZET` satırı.

| Ajan | Model / araçlar | Görev | Okur (GIRDI kopyası) | Çıktı |
|---|---|---|---|---|
| **`kurgucu`** (yeni; yazar rolü) | opus·high · Read, Write, Edit, Glob, Grep | Kipler: `duzelt` (bulgu → işlem listesi), `kirp_incele` (güveni düşük kırpmalara karelerle bakar), `sifir_kredi` (kredili maddeden önce 0 kredi çözümü var mı), `not` (kullanıcı notu + taslak farkı). Yeniden çekim **gereksinimini** tarif eder, istem yazmaz | `KURGU_PLANI` dilimi, `SEYIRCI_KARAR`, ilgili seyirci JSON'ları, `BULGU_YONLENDIRME`, `_RAPOR/Z3_*`, `K1_*`, `V2V3_*`, `S3_*` özetleri, `SAHNELER.json` dilimi (kurgucu habersiz değildir), `HIKAYE.json` olay listesi, ZN §2–§5, RE, `URETIM_ONIZLEME` dilimleri, `DERSLER_AKTIF.md` (kurgu satırları), `NOTLARIM`, `TASLAK_FARK` | `CIKTI/KURGU_KARARLARI.json` (§4.5.6), `CIKTI/sifir_kredi.json`, `CIKTI/NOT_CEVAPLARI.md`; görevin `tasima` alanı `KURGU/`'ya taşır |
| **`kesici`** (yeni; kör rol) | opus·high · Read, Write · `omitClaudeMd: true` | Tek soru: "Hangi 10 planı ya da 2 sahneyi atarsak film daha iyi olur?" (ZN §7.2.9). Her öneri için gerekçe, beklenen kazanç (sn) ve "seyirci olarak neyi kaybedebilirim" notu | Yalnız GIRDI: kurgu (ya da animatik) kipinin sayfaları ve `IZLE.md`'si + `KESME_GIRDI.md` (plan süreleri, seyircilerin ortak sıkılma anları, medyan ilgi eğrisi). `ekranda_bilgi`, amaç, kurulum listesi **yok** | `CIKTI/KESME_ONERI.json` |
| `habersiz-seyirci` (sahibi senarist; **izleme kiplerinin gövdesi benim**) | opus·high · Read, Write · `omitClaudeMd: true` | Kip `animatik` ve `kurgu`: filmi baştan sona, parça parça izler; 6 ölçüt; kopukluklar plan numarasıyla; sıkıldığı anlar; dakika başına ilgi; açık sorular; parti özetleri; ekran dışı sesler kime aitti | Yalnız GIRDI: o ana kadar açılmış parça klasörleri | `CIKTI/rapor.md` + `rapor.json` (§4.5.3) |
| `ozet-eslestirici` (ortak; **`bulgu` kipi benim önerim**) | opus·high · Read, Write · `omitClaudeMd: true` | Kip `ozet`: seyirci özeti ↔ `anahtar_olgular` (`bulundu / kismen / yok` + alıntı). Kip `bulgu`: her kopukluk ve açık soru için `{eslesen: {tur, id} ya da null, alinti}` | Seyirci JSON'u, `anahtar_olgular`, `KURULUMLAR` (kimlik + ad), `MERAK_DEFTERI`, karakter maske listesi | `CIKTI/eslesme.json` |
| Hakem (başka uzmanların ajanları) | — | Tek seyircinin KRİTİK'ini kanıtla geçersiz saymak: görselde `sureklilik-denetcisi` (hakem kipi), hikâye ve akışta `yapimci` (doktor kipi) | kopukluk, ilgili sayfa ve kare, seyircinin paketindeki satır | `KRITIK_RED_<kip>_t<n>.json`; betik kanıtı doğrular |

**`kurgucu.md` (önerilen frontmatter ve çekirdek kurallar)**
```markdown
---
name: kurgucu
description: Filmin kurgucusu. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; seyirci,
  kesici, Z3 ve kullanıcı notu bulgularını kurgu işlem listesine çevirir (kırpma, sıra, J/L, ekran dışı replik, kart,
  plan kesme), kredili yeniden çekimden önce 0 kredi çözümlerini dener ve güveni düşük kırpmalara karelerle bakar.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 80
---
Sen filmin kurgucususun. Önce GOREV.json'u oku (kip: duzelt | kirp_incele | sifir_kredi | not).
Kural sırası Murch'ündür: duygu > hikâye > ritim > göz izi > 2B > 3B (ZN §3.4).
1. Önce 0 kredi merdiveni (GIRDI/MERDIVEN.md). Kredili çözümü ancak merdiven tükenince ve gerekçesiyle öner.
2. KURGU_PLANI'nı değiştirme. İşlem listesini CIKTI/KURGU_KARARLARI.json'a yaz; doğrulamayı sistem yapar,
   hata gelirse aynı listeyi düzelt.
3. kaynak: kullanici olan kırpma ve sırayı asla geri alma; yarattığı açığı köprüyle kapat.
4. Dudağı oynayan karakterin üstüne başkasının repliğini koyma. Görünen konuşanın sesini klip zamanından kaydırma.
5. Durumu değiştiren (etkisi olan) planın sahne içi sırasını değiştirme; dondurulmuş durum zıplar.
6. Her işleme kok_neden (veri/kok_neden.json) ve bulgu kimliği yaz.
7. Bir seyircinin KRİTİK'ini geçersiz sayamazsın; bu hakemin işidir.
Son satır: OZET | islem: 14 | sifir_kredi: 11 | yeniden_cek: 2 | yeni_plan: 1 | kredi_tahmini: 36
```

**`habersiz-seyirci` izleme kiplerinin gövde metni (senaristin ajan dosyasına kip bölümü olarak girer)**
```markdown
## Kip: animatik
Kareler planların durağan başlangıç kareleridir; altındaki italik yazı o planda görünen hareketi anlatır.
Hareketin kareden okunamaması kusur değildir. Kim, nerede, ne oldu, neden: bunlar anlaşılmıyorsa kusurdur.
## Kip: kurgu
Her satır bir plandır (baş, orta, son kare). Bir plandan ötekine geçerken "nereden çıktı" dediğin her yer
bir kopukluktur (ZN §7.3 akıcılık sorusu). Hiçbir geçiş sana ayrıca işaretlenmez; hepsini aynı gözle izle.
## İki kipte ortak
- Yalnız GIRDI'deki parça klasörlerini sırayla aç. Bir parçayı bitirince o parçanın raporunu yaz ve dur;
  sonraki parça sana ayrıca verilecek.
- Adını ekranda duymadığın ya da yazıda görmediğin karakteri adıyla anma; "kürk yakalı kadın" gibi tarif et.
- "Duyulan" satırı o anda duyduğun tek şeydir. "(anlaşılmayan konuşma)" yazıyorsa o sözü duymadın.
- Puanla (1–10, cömert olma): anlasilirlik, akicilik, merak, duygu, ritim, ilk30.
  Her dakika için ilgi (1–10). Kopukluklar KRITIK/ORTA/KUCUK, plan numarası ve zaman koduyla.
```

---

### 4.4 Beceri (skill) tarif adımları — kendi alanım

**Yer:** `.claude/skills/film-yap/reference/KURGU.md` (≤ 300 satır; başında içindekiler; SKILL.md'den tek seviye bağlantı; AR3 B4).
- Ana Claude bu dosyayı ancak `film.py sonraki` çıktısının `oku` alanı gösterdiğinde ya da takıldığında açar ([CM] §4.3). Asıl iş görev defterindedir.
- Ajanların talimatları `sablonlar/A12_kurgucu_duzelt.md`, `A16_kurgucu_not.md`, `A16_kesici.md` gibi şablonlardan betikle üretilir. Sayılar şablona RE'den basılır; ajana sabit sayı yazılmaz ([CM] K-15).
- Kredili yeniden çekim için ayrı alt komut yoktur. Kredi kapısı `film.py`'dedir (`kuyruk.py` + `kredi.py`).

**Ana Claude için en üst kurallar** (sıkıştırmadan sonra geri gelen ilk bölüme girer):
1. Animatik geçmeden video kredisi harcanmaz (kod zorlar; sen de zorlama).
2. Kopuk taslak kullanıcıya gösterilmez: KRİTİK = 0 olmadan KR10 çalışmaz.
3. Kullanıcının CapCut kararı aynen uygulanır; onun taslağına yazılmaz.
4. Seyirciye paketten başka hiçbir şey verme: ipucu, kopukluk adayı, özet, "şuna dikkat et" YOK.
5. Her kurgu değişikliğinden sonra dudak ve senkron denetimi çalışır.
6. Flow uyarısında DUR; atlatma yok.

**Görev zincirleri** (`film.py sonraki` bunları sırayla verir; ana Claude yalnız dağıtır)

| Zincir | Görevler (tür) | Geçme şartı | Geçmezse |
|---|---|---|---|
| **A. Animatik turu** (KR1–KR4) | `zaman_cizelgesi --asama animatik` (betik) → `kurgu_render --animatik` (betik) → `kor_paket --kip animatik --tur n` (betik) → 3 × `habersiz-seyirci` animatik + 3 × `ilk2dk` (ajan, paralel grup; parça başına SendMessage, sonraki parçayı betik açar) → 6 × `ozet-eslestirici` (ajan) → `seyirci_topla` (betik) | B1 + B2 | `kurgucu duzelt` (+ tur 1'de `kesici` → `kesme-simule`) → sahiplerin görevleri → `kurgu_uygula` → zincirin başına (yalnız değişenler) |
| **B. Kaba kurgu** (KR6–KR7) | `plan_kurgu` → ses görevleri ([SM] D1–D5) → `kurgu_render --onizleme` → `kurgu_denetim` (hepsi betik) | Z3 HATA 0 | `kurgucu kirp_incele` (güveni düşük kırpmalar) → B yeniden |
| **C. Kurgu izleme** (KR8–KR9) | A'nın izleme adımları, kip `kurgu`, işitsel döküm son miksten | B3 + B2 | `kurgucu duzelt` → `kurgucu sifir_kredi` (her kredili maddede) → `kuyruk --topla --onizleme` → D |
| **D. Bütçe ve video** | `kredi.py --dilim kurgu` (betik) → video görevi (kullanıcı eylemi: VIDEO_*.bat; Memmet) → V1/V2/V3 (betik + kör gözlemci) → B | dilimde yer var; Flow uyarısı yok | dilim yetmezse 0 kredi çözümü; KRİTİK'te DUR + "X kredi" bildirimi; Flow uyarısında DUR |
| **E. CapCut** (KR10) | `capcut_film` → `taslak_fark --oz-denetim` (betik) | fark 0, boşluk 0, eksik medya 0 | betik hatası → `FILM_KAYIT` + bildirim |
| **F. Kullanıcı notu** (KR11) | (CapCut açıksa kullanıcı eylemi) → `taslak_fark`, `notlari_oku` (betik) → `kurgucu not` (ajan) → `kurgu_uygula` → `kurgu_denetim --hepsi` → `capcut_yama` → `taslak_fark --oz-denetim` | B10 + B13 | yama doğrulanamazsa yedek akış: kullanıcının kararlarıyla yeni adla taslak |
| **G. Teslim** (KR12) | yayın taslağı (betik) → dışa aktarım (kullanıcı eylemi; algılama `YAYIN/*.mp4`) → `kalite_denetim --final` + yayın doğrulaması → gerekirse `son_miks --mux` | B14 | kanıt yoksa F zinciri |

**Kullanıcıya giden mesaj kalıpları** (soru yok; bilgi ya da fiziksel iş):
- "Animatik 2. turda 8/8/9 aldı, kurgu bitince videoya geçiyorum."
- "Taslak hazır: CapCut'ı kapatıp aç; 'YZ <FILM> v3' en üstte. İstersen izleyip not bırak, istersen doğrudan dışa aktar."
- "Notlarını aldım: 6 not → 5 düzeltme, 1 bilgi. Düzeltilmiş taslak: '<senin taslağın> · v4'. Kendi taslağına dokunmadım."
- "P2 için 3 klibin yeniden çekilmesi gerekiyor: 36 kredi. Hesapta yeterli kredi yok; yüklenince kendim devam ederim."

**Değerlendirme senaryoları** (beceri testi, AR3 B4):
1. Animatik GEÇMEDİ iken "videoları üret" → video görevi açılmaz; nedeni bir cümleyle söylenir.
2. Seyirci görevinin istemine kopukluk adayı ya da `ekranda_bilgi` sızarsa → `test_kor_paket` kırmızı.
3. Kullanıcı "CapCut'ta 3 plan sildim, kontrol et" → F zinciri; kullanıcının kaynak taslağının özeti değişmemiş.
4. Kredili yeniden çekim önerisinde `sifir_kredi` alanı yok → `kuyruk.py` reddeder.

---

### 4.5 Veri şeması / plan alanları (JSON örneğiyle)

Zaman birimi saniyedir. Bütün `cizelge_bas` ve `sure` değerleri 1/24 sn'ye yuvarlanır (24 fps, UH §8). Her çıktı [UM]'nin `_uretim` zarfını taşır.
Örnekler [YN2] §4.5.12'deki S12 "Kapıdaki kaptan" sahnesinin 121–124. planlarıyla tutarlıdır.

#### 4.5.1 `KURGU/KURGU_PLANI.json` (kurgunun tek kaynağı) **(değişti)**
```json
{
 "_sahip": "kurgu", "_surum": 7,
 "_uretim": {"asama": "KR6", "girdi_imza": "4be1c0d27a91", "arac": "plan_kurgu.py 1.0",
             "esik_surum": "ritim@1.0+ogrenilen@7", "sonuc": "GEC", "zaman": "2026-11-02T21:14:05+03:00"},
 "film": "EMBERFALL_F2", "cizelge": "T2", "kurgu_surumu": 7, "fps": 24,
 "girdi_imzalari": {"SAHNELER.json": "a1b2c3d4", "SIRALI_VIDEO": "9f8e7d6c", "SESLER/diyalog.json": "77aa01ce"},
 "planlar": [
  {"sira": 121, "plan": 121, "parti": 1, "sahne_grubu": "S12", "izleme_parcasi": 6,
   "goruntu": {"tur": "video", "dosya": "SIRALI_VIDEO/121.mp4", "dosya_ozet": "c41e09a2", "klip_sn": 8.0,
               "kaynak_klip": null,
               "kullanim": {"bas": 0.625, "sure": 3.583}, "kullanim_kaynak": "otomatik", "kullanim_kilit": null,
               "guven": 0.86,
               "gerekce": "a1 (cene_kaldirir) ölçülen başı 0,72 sn; ilk kelime 2,04; L kesme 4,21'de; replik klipte 5,31'de bitiyor",
               "hiz": 1.0, "ayna": false, "kadraj_kirpma": null},
   "cizelge_bas": 412.0, "sure": 3.583,
   "kesme_giris": {"tip": "eylem"}, "kesme_cikis": {"tip": "L", "adim": "a2", "adim_orani": null},
   "durum_ozet": {"bas": "d41f09", "bit": "77c0a1"}},
  {"sira": 122, "plan": 122, "parti": 1, "sahne_grubu": "S12", "izleme_parcasi": 6,
   "goruntu": {"tur": "video", "dosya": "SIRALI_VIDEO/122.mp4", "dosya_ozet": "0b77e3f1", "klip_sn": 8.0,
               "kaynak_klip": null,
               "kullanim": {"bas": 0.708, "sure": 2.833}, "kullanim_kaynak": "otomatik", "kullanim_kilit": null,
               "guven": 0.74, "gerekce": "tepki: a1 bakış kayması tepesi 1,9 sn'de; ağız kapalı (ağız dizisi std 0,01)",
               "hiz": 1.0, "ayna": false, "kadraj_kirpma": null},
   "cizelge_bas": 415.583, "sure": 2.833,
   "kesme_giris": {"tip": "L"}, "kesme_cikis": {"tip": "duz"},
   "durum_ozet": {"bas": "77c0a1", "bit": "8e21d0"}}
 ],
 "diyalog": [
  {"replik": "R0042", "parca": 0, "plan": 121, "kaynak": "SESLER/diyalog.json#121",
   "klip_zamani": {"bas": 2.04, "bit": 5.31},
   "cizelge_bas": 413.417, "sure": 3.27,
   "gorunen_konusan": true, "ekran_disi": false,
   "jl": {"tip": "L", "tasma_sn": 1.10, "uzerindeki_planlar": [122]}}
 ],
 "kartlar": [
  {"tur": "yer_zaman", "metin": "The Cabin — Night", "cizelge_bas": 405.208, "sure": 3.0, "ust_uste": true,
   "sablon": "EVREN/EMBERFALL/sablonlar/yer_karti.json"}
 ],
 "karartmalar": [],
 "kullanici_kilitleri": [],
 "olcumler": {"toplam_sn": 2412.583, "asl": 4.71, "asl_ilk120": 3.82, "asl_ilk30": 3.29,
              "jl_orani_diyalog": 0.34, "tepki_orani_diyalog": 0.27}
}
```
**Kurallar:**
- `sure = kullanim.sure / hiz`. Çizelgede boşluk yoktur: `planlar[i+1].cizelge_bas = planlar[i].cizelge_bas + planlar[i].sure`. Tek istisna planlı karartmadır (`karartmalar[]`).
- `goruntu.tur`: `gorsel` (T1: durağan kare + hareket) · `video` (T2/T3) · `kart` · `siyah` · `yer_tutucu` (görsel + yavaş zoom; DR'deki filtre çözümü).
- `kullanim_kaynak`: `plan` (T0/T1) · `otomatik` (`kirp_oner`) · `kurgucu` · `kullanici`. `kullanici` olan değer hiçbir otomatik araçla değişmez.
- `kullanim_kilit`: `zincir` (KR5) ya da `kullanici`.
- **Senkron kuralı** (görünen konuşan): `diyalog.cizelge_bas = plan.cizelge_bas + (klip_zamani.bas − kullanim.bas) / hiz`. Fark > 1 kare ise HATA. Örnekte: 412,0 + (2,04 − 0,625) = 413,415 → 413,417 (kare yuvarlaması).
- **Senkron korumalı klip bölme:** Aynı klipten iki plan çıkıyorsa (`kaynak_klip`) ve replik aradaki planın üstünden sürüyorsa: `parca2.kullanim.bas = parca1.kullanim.bas + parca1.sure + aradaki_planlarin_suresi`. Böylece konuşana dönülünce dudak ile ses aynı anda olur. Replik sürmüyorsa ZN §2.2'deki ≥ 0,4 sn atlama kuralı geçerlidir. [YN2] Y39 bu formülü içerir.
- **L örneğinin denetimi (Y31 ve ekleri, §4.7.3):** görüntü 3,583 + taşma 1,10 = 4,68 ≥ formül 3,95 ✓ · ekranda konuşulan kısım 2,04 → 4,208 = 2,17 sn ≥ 1,0 ✓ · replik klipte 5,31'de bitiyor ≤ 8,0 − 0,3 ✓ · üzerine binilen plan 122: 2,833 ≥ 1,10 + 0,5 ✓, 122'de ağız kapalı ✓.
- `durum_ozet`: planın `uretim.durum_dondu` özetleri. Sıra ya da kesme değişince yeni komşular bu özetlerle karşılaştırılır (Y58).
- `diyalog[]` yalnız yerleşimdir. Metin, kelime zamanları, dosya ve ölçülen seviye `SESLER/diyalog.json` v2'dedir ([SM] sahibi).
- Ambiyans, efekt ve müzik yerleşimi `KURGU_PLANI`'nda **yoktur**. [SM]'nin dosyalarında durur ve hangi `KURGU_PLANI` sürümünden çözüldüklerini `_uretim.girdi_imza` ile yazar.

#### 4.5.2 `SAHNELER.json`'da kurgunun okuduğu alanlar
Kurgu bu dosyaya yalnız kendi küçük alt nesnesini yazar; gerisini okur.

| Alan | Sahibi | Kurgu ne için okur |
|---|---|---|
| `kullanim{bas,sure}` | yönetmen | planlanan kırpma; T0/T1 süresi; sapma raporu |
| `_derlenir.sure_sn`, `_derlenir.kesme_nokta_sn` | kod | T0 |
| `zanaat.kesme {tip, ses_tasma_sn}` | yönetmen | planlanan J/L |
| `zanaat.plan_tipi`, `zanaat.eylem_zinciri[] {id, bas, bit, fiil, tur}` | yönetmen | kırpma önceliği; adım eşleme; eylem kesmesi %60–70 |
| `zanaat.zincir {gecis_turu, dogal_durak, bitis_sabitle}` | yönetmen | KR5; Y54/Y55 |
| `zanaat.ekran_disi_ses`, `zanaat.kaynak_klip` | yönetmen | ekran dışı replik; senkron korumalı bölme |
| `zanaat.vaat_imgesi` | yönetmen (HIKAYE vaat sözleşmesinden) | ≤ 120 sn denetimi; kuyruk konum ağırlığı |
| `_derlenir.ayna_yasak`, `_derlenir.agiz_gorunur` | kod | merdiven #7; B9 |
| `uretim.durum_dondu`, `uretim.zincir` | betik | Y58; zincir kilidi |
| `kurgu.kirpma_onceligi` | **kurgu** (varsayılan `plan_tipi`'nden) | `kirp_oner` |

Film düzeyinde `HIKAYE.json`'dan okunanlar: `anahtar_olgular[]`, karakter `maske`, `vuruslar`, `duygu_haritasi`, `MERAK_DEFTERI`, `KURULUMLAR`, `bolum_adlari`, `baslik.secilen` ve kapak imgesi tarifi (ilk 2 dk paketi için).

#### 4.5.3 Seyirci raporu: izleme kiplerinin ek alanları
Taban [SN2] §4.5.6'dır. İzleme kipleri şu alanları ekler ya da biçimini belirler:
```json
{"kip": "kurgu", "tur": 1, "seyirci": 2, "bolum": "P1", "parca": 3,
 "puanlar": {"anlasilirlik": 8, "akicilik": 7, "merak": 8, "duygu": 7, "ritim": 6, "ilk30": 9, "GENEL": 7},
 "parca_puanlari": [{"parca": 1, "GENEL": 8}, {"parca": 2, "GENEL": 7}, {"parca": 3, "GENEL": 6}],
 "kopukluklar": [{"konum": {"sahne": "S05", "plan": 41, "onceki_plan": 40, "zaman": "01:01"}, "tur": "KRITIK",
                  "neden": "Kadın kapıdaydı, sonraki karede masanın yanında; nasıl geldiğini görmedim",
                  "oneri": "arada yürüdüğünü gösteren bir plan"}],
 "sikilma": [{"bas": "07:40", "bit": "08:30", "neden": "aynı tartışma ikinci kez"}],
 "ilgi": [{"konum": {"zaman_bas": "00:00", "zaman_bit": "01:00"}, "puan": 9},
          {"konum": {"zaman_bas": "01:00", "zaman_bit": "02:00"}, "puan": 7}],
 "acik_sorular": ["Kardaki ışık neydi?"],
 "ozet_parti": "Üç cümle.",
 "karakterler": [{"ad_ya_da_tarif": "Mara", "kim": "avcı kadın", "adi_nereden": "R0004"}],
 "kahraman_ne_kaybedebilir": "Yavruyu ve köydeki yerini",
 "ekran_disi_sesler": [{"plan": 122, "kime_ait_sandim": "kapıdaki kadın"}],
 "anlasilmayan_konusmalar": [{"plan": 214, "etki": "ne dediğini anlamadım; sonraki sahnede neden kaçtıklarını kaçırdım"}],
 "devam": true}
```
- `ilgi` izleme kiplerinde **dakika başınadır** (duygu haritası dakika başına olduğu için); kâğıtta sahne başınadır. Şema aynıdır: `{konum, puan}`.
- `parca_puanlari`, uzun izlemede dikkat dağılmasını izler (R16).
- `anlasilmayan_konusmalar`, son miksteki maskelemenin seyirciye etkisini kaydeder ([SM] S7.6 ile eşlenir).

#### 4.5.4 İzleme paketi (`kor_paket.py` izleme modülü)
- **Klasör:** `_GOREV/<id>/GIRDI/` altında parça başına klasör: `P0/`, `P1_1/`, `P1_2/` … Bir sonraki parçayı, önceki parçanın raporu yazılınca betik kopyalar (aşamalı girdi).
- **Sayfa (`sayfa_NN.jpg`, ≈ 1200 × 1600 px):**
  - Kurgu kipinde 6 plan × 3 kare (baş + 0,15 sn, orta, son − 0,15 sn; kırpılmış pencereden).
  - Animatik kipinde 6 plan × 1 kare (+ varsa bitiş görseli) ve altında eylem şeridi.
  - Kareler 400 × 225 px'tir; sol üstte zaman kodu ve plan numarası yazar. Sayfanın en üstünde önceki sayfanın son karesi küçük olarak durur.
- **Bağlam bütçesi:** sayfa başına ≈ 1,6 bin görüntü tokeni (tahmin; ilk çalıştırmada `count_tokens` ile ölçülür). 495 planlık film ≈ 83 sayfa ≈ 133 bin token, `IZLE.md` metni ≈ 40–60 bin token (tahmin). Seyirci başına toplam ≈ 0,2 M token eder. Opus 5.5 bağlamı 1M olduğu için (CA) tek örnek bütün filmi izleyebilir. Claude Code alt ajanında da 1M bağlamın geçerli olduğu doğrulanmalıdır (açık soru 5).
- **`IZLE.md` satırı** (işitsel döküm biçimi, [SM] B2):
  ```
  ## Sayfa 03 (sayfa_03.jpg)
  - [06:52.0] #121 · 3,6 sn
    duyulan [ekranda, kadrajdaki kadın]: "It's late, Captain. What do you want?" · efekt: rüzgâr, meşale çıtırtısı · müzik: yok
  - [06:55.6] #122 · 2,8 sn
    duyulan [ekran dışı, az önce duyduğun kadın sesi]: "…What do you want?" · müzik: alçak telli, gerilimli giriyor
  - [06:58.4] #123 · 4,1 sn
    duyulan [ekranda, kadrajdaki adam]: (anlaşılmayan konuşma)
  ```
- **Duyulan metin:** Animatikte TTS metnidir. Kurguda son miksin ASR'sidir; ASR ↔ `altyazi_metin` WER'i > 0,30 ise "(anlaşılmayan konuşma)" yazılır ([SM] S7.6).
- **Ad maskeleme:** konuşan etiketi ve görsel tarif, karakterin adı ilk kez sözle ya da yazıyla verilene kadar `maske.etiket_anonim_en` ile yazılır. `takma_adlar` (unvan, akrabalık) da aynı kurala uyar. Replik metni olduğu gibi kalır; seyirci repliği duyuyorsa adı ondan öğrenir.
- **Pakette olmayanlar:** amaç, duygu, risk, vuruş, merak/kurulum kimlikleri, `ekranda_bilgi`, `seyirci_ogrenir`, plan tipi, kadraj etiketi, kesme tipi, kopukluk adayları, önceki tur raporları, önceki film özeti.
- **İlk 2 dk paketi:** başlık (`HIKAYE.baslik.secilen`) + kapak imgesi tarifi + P0. Soru: "30 sn'den sonra kalır mıydın? 2. dakikanın sonunda devam eder miydin? Neden? Başlıkta ve kapakta vaat edileni gördün mü?" ([SN2] H12).
- **`KESME_GIRDI.md`** (kesici için): kurgu ya da animatik sayfaları + plan sırası ve süreleri + seyircilerin ortak sıkılma anları (≥ 2 seyirci; RE `sikilma_ortak_isaret_min`) + medyan ilgi eğrisi. `ekranda_bilgi` ve amaç yoktur.

#### 4.5.5 0 kredi merdiveni, yeniden çekim maddesi, bütçe dilimi **(değişti)**

**0 kredi merdiveni** (kurgucu her kopuklukta yukarıdan aşağı dener; `sifir_kredi` kipinde de aynı sıra). `KK` satırları kredilidir:

| # | Çözüm | Ne zaman | Koşul |
|---|---|---|---|
| 1 | Kırp / uzat | ölü süre, geç giriş, uzun plan, eylem görünmedi, kusur pencere dışında | güvenli pencere `[0,5 ; klip_sn − 0,5]` (ZN §2.2); zincir kilidi yoksa |
| 2 | Sahne içi sıra | konum planı geç, bakış → ekleme sırası | **yalnız `etki`siz planlar** (tepki, ekleme); Y58 dondurulmuş denetim temiz; 180° ve kurulum yeniden denetlenir |
| 3 | J/L, ekran dışına taşıma (mevcut replik) | "kim konuşuyor", konuşma kopuk | üzerine binilen planda ağız kapalı (B9); ses tanıtım kuralı ([SM] S0.3); Y31 ekleri |
| 4 | **Ekran dışı köprü replik** (yeni; [SN2] H15-2) | bilgi ekrana çıkmamış, görüntü var | içeriği yazar yazar (dar değişiklik), Yol B TTS (Flow kredisi 0); konuşan daha önce ekranda konuşmuş; sahne başına ≤ 1 (tahmin) |
| 5 | Alternatif çekim | çekimde kusur var | `ALTERNATIFLER/` içinde V1/V2/V3'ten geçen başka sonuç |
| 6 | Mevcut klipten bölme ya da örtü planı | tepki/ekleme eksik; çıplak `devam` dikişi | aynı sahnenin kullanılmayan klip penceresi; örtü süresi İ-11 formülüyle |
| 7 | Ayna | 180° ya da bakış ters | `_derlenir.ayna_yasak = false` |
| 8 | Yeniden kadraj | ölçek sıçraması | dijital yakınlaştırma ≤ %10 (tahmin; 720p kaynak, kesin karar 6) |
| 9 | Hız | eylem uzun | 0,90–1,15× (tahmin); yalnız diyalogsuz plan |
| 10 | Kart / efekt ipucu | "nerede", "nereden geldi" | yer kartı; efekt isteği [SM]'ye (ör. önceden duyulan kapı gıcırtısı) |
| 11 | Planı kes | bilgi taşımayan plan | `--kesme-simule` yeni HATA göstermiyor |
| 12 | Yer tutucu (görsel + yavaş zoom) | filtre reddi (DR: bebek yüzü) | ilk 120 sn, parti sonu ve dorukta kullanılmaz (tahmin) |
| KK1 | **Yeniden çekim** (aynı plan; CORRECTION ya da Z2 bitiş sabitleme) | kusur görüntünün içinde | kurgu dilimi + plan başına ≤ 2 |
| KK2 | **Bağlayıcı yeni plan** | hikâye adımı ekranda yok, hikâyede var | yönetmen yazar; G1; `--onayli` modda yalnız bilgi |
| KK3 | **Yeni sahne** | bilgi hikâyede yok | yalnız KRİTİK; yazar + yönetmen ([SN2] H15-5) |

**`YENIDEN_URET` maddesi** ([UM] §5.4 tabanı + kurgu alanları; bütün kapılar aynı şemayla yazar):
```json
{"id": "YU-T2-1-007", "plan": 41, "tur": "video", "kaynak_kapi": "KI", "kaynak_rapor": "_RAPOR/SEYIRCI_KARAR_T2_t1.json",
 "kok_neden": "nesne_zipladi", "seviye": "KRITIK", "seyirci_sayisi": 2, "dogrulanmis": true,
 "konum_agirligi": 1.5, "oncelik": 6.75,
 "cozum": "yeniden_cek",
 "duzeltme": "CORRECTION: the lantern stays in Mara's RIGHT hand for the whole shot; her LEFT hand is empty.",
 "sifir_kredi": {"denendi": true, "basamaklar": [1, 5, 6], "gerekce": "kusur 1,1 sn'de başlıyor; kusursuz pencere 0,6 sn < eylem planı alt sınırı 3,0 sn"},
 "plan_metni_sahibi": "yonetmen", "zincir_etkisi": [42],
 "dilim": "kurgu", "kredi_tahmini": 24,
 "deneme": 1, "deneme_max": 2, "durum": "bekliyor", "karar_veren": null}
```
- `kaynak_kapi`: `G1`, `V1`, `V2`, `V3`, `K1`, `S2`, `Z3`, `KI` (kurgu izleme), `AI` (animatik izleme), `NOT` (kullanıcı).
- `oncelik = seviye_puanı × konum_agirligi × (1 + 0,5 × (seyirci_sayisi − 1)) × (dogrulanmis ? 1,25 : 1)`.
  - Seviye puanı: KRİTİK 3, ORTA 2. KÜÇÜK kuyruğa girmez.
  - `konum_agirligi`: ilk 120 sn, parti sonunun son 30 sn'si, doruk ya da vaat imgesi için 1,5; diğerleri 1,0.
  - Formül ve katsayılar tahmindir.
- Sıra: önce bütün KRİTİK'ler, sonra ORTA'lar `oncelik / kredi_tahmini` büyükten küçüğe.
- `zincir_etkisi`: KR5 kilidi yüzünden yeniden çekilmesi gereken sonraki planlar. Maliyete eklenir.
- **0 kredi kuralı:** `cozum` ∈ {`yeniden_cek`, `z2_bitis`, `yeni_plan`, `yeni_sahne`} olan madde `sifir_kredi.denendi = true` ve dolu `gerekce` olmadan reddedilir. Teknik kapılarda (V1/V2) kusur kullanılan pencerenin dışındaysa betik `cozum: kirp` yazar, kuyruğa madde açmaz.

**Bütçe dilimi** (`URETIM_ONIZLEME.json → kredi.flow.dilimler`; [UM] `kredi.py` yazar):
```json
"dilimler": {"goruntu": {"oran": 0.15, "ayrilan": 729, "harcanan": 312},
             "ses":     {"oran": 0.07, "ayrilan": 340, "harcanan": 48},
             "kurgu":   {"oran": 0.08, "ayrilan": 389, "harcanan": 96},
             "aktarim": [{"kimden": "goruntu", "kime": "kurgu", "kredi": 24, "madde": "YU-T2-1-007", "neden": "KRITIK", "hat_denetcisi": "_RAPOR/HAT_DENETIM_2.md"}]}
```

#### 4.5.6 `KURGU/KURGU_KARARLARI_<T>_t<n>.json` (kurgucunun işlem listesi)
```json
{"asama": "T2", "tur": 1, "kip": "duzelt",
 "islemler": [
  {"op": "kirp", "plan": 41, "bas": 0.917, "sure": 5.083, "kok_neden": "olu_sure", "bulgu": "s2:k3"},
  {"op": "jl", "replik": "R0087", "tip": "L", "tasma_sn": 1.2, "kok_neden": "diyalog_kopuk", "bulgu": "s1:k5"},
  {"op": "sira", "sahne_grubu": "S05", "yeni_sira": [44, 43, 45], "kok_neden": "konum_plani_gec", "bulgu": "Z0#konum"},
  {"op": "ekran_disi", "replik": "R0090", "uzerine_plan": 91, "kok_neden": "konusan_belirsiz", "bulgu": "s3:k2"},
  {"op": "kopru_replik_iste", "araya": [40, 41], "bilgi": "o07", "konusan": "voss",
   "kok_neden": "bilgi_ekranda_yok", "bulgu": "s1:k1,s2:k1", "sahip": "hikaye-yazari"},
  {"op": "ortu", "araya": [70, 71], "kaynak_plan": 68, "kullanim": {"bas": 4.1, "sure": 1.5},
   "kok_neden": "devam_dikisi", "bulgu": "K1#70-71"},
  {"op": "kes", "plan": 63, "kok_neden": "bilgisiz_uzun", "bulgu": "kesici:4", "simule": "_RAPOR/KESME_SIMULE_T2.json#4"},
  {"op": "kart", "kart_tur": "yer_zaman", "metin": "The Warden's House", "plan": 40, "kok_neden": "mekan_belirsiz", "bulgu": "s1:k1"},
  {"op": "yeniden_cek", "plan": 52, "istek": "nesne sağ elde kalmalı", "kok_neden": "nesne_zipladi", "bulgu": "s1:k4,s2:k1",
   "sifir_kredi": {"basamaklar": [1, 5], "gerekce": "kusur penceresi kullanılabilir süreyi 1,2 sn'ye düşürüyor"}},
  {"op": "yeni_plan_iste", "araya": [40, 41], "gereksinim": "Mara kapıdan masaya yürür; OG; ekran yönü soldan sağa; 3 sn; sessiz",
   "kok_neden": "hikaye_adimi_ekranda_yok", "bulgu": "s1:k1,s2:k1,s3:k2", "sahip": "yonetmen"}
 ]}
```
- İşlem türleri: `kirp`, `uzat`, `sira`, `jl`, `ekran_disi`, `kopru_replik_iste`, `ortu`, `alternatif`, `bol`, `ayna`, `kadraj`, `hiz`, `kart`, `efekt_iste`, `kes`, `kes_sahne_iste`, `yer_tutucu`, `yeniden_cek`, `yeni_plan_iste`.
- `kurgu_uygula.py --kuru` her işlemi doğrular: kilitli alan, dondurulmuş durum, Y31 ekleri, B9, senkron, pencere sınırları. `*_iste` işlemleri ilgili sahibin kuyruğuna (`YENIDEN_YAZ`, H15), `yeniden_cek` işlemi `YENIDEN_URET`'e aktarılır.
- `kok_neden` değerleri `veri/kok_neden.json`'dan gelir. Bu dosyada her kök nedenin sahibi yazar (§2.1). Ders defteri bu sözlükle sayar.

#### 4.5.7 `TASLAK_FARK.json`, yama raporu ve taslak karar ağacı **(değişti)**
```json
{"taslak": "YZ EMBERFALL_F2 v3", "kaynak_ozet": "e3b0c442", "okuma": "salt_okunur", "sifreli": false,
 "klipler": [
  {"plan": 41, "degisim": "kirpildi", "eski": {"bas": 0.625, "sure": 5.583}, "yeni": {"bas": 1.083, "sure": 4.208}},
  {"plan": 63, "degisim": "silindi"},
  {"plan": 70, "degisim": "tasindi", "eski_sira": 52, "yeni_sira": 47}],
 "bosluklar": [{"bas": 241.208, "sure": 0.792}],
 "kayan_kanallar": ["Diyalog", "Ambiyans"],
 "kullanici_ogeleri": [{"tur": "yazi", "segment_id": "…"}, {"tur": "renk_ayari", "segmentler": "20-31"}],
 "kullanici_ses_duzenlemesi": [{"kanal": "Muzik", "degisim": "seviye -3 dB"}],
 "kullanici_yazilari": 3}
```
**Karar ağacı:**
1. **Fark yok** → KR10 yeni sürüm (`v<N+1>`), yeni sürüm klasörü. Eski taslak ve klasörü bozulmaz.
2. **Fark var, taslak okunur** → `capcut_yama.py`:
   - Kullanıcının taslağı **klonlanır**. Kaynak hiçbir zaman yazılmaz (`clone_project` emsali). Klonun adı: "<kullanıcının proje adı> · v<N+1>".
   - Kullanıcının kararları `KURGU_PLANI`'na `kaynak: kullanici` ve kilitli olarak işlenmiştir (KR11-3). Klonda yalnız **bizim kanallarımız** bu plana göre yeniden yerleşir: Diyalog, Efekt, Ambiyans, Muzik, Altyazi, Kartlar, NOTLAR.
   - Klipler kanalına ve `kullanici_ogeleri`'ne dokunulmaz.
   - Yeni medya (yer tutucunun yerine gelen klip, yeniden çekim) **yeni dosya adıyla** bağlanır (`121_t2.mp4`). Eski dosya ezilmez (DR).
   - `kullanici_ses_duzenlemesi` varsa ilgili kanalın kullanıcı ayarı korunur; yalnız segment konumları kayar.
   - Öz denetim (`taslak_fark --oz-denetim` klon üzerinde): klondaki Klipler özeti = kaynaktaki Klipler özeti; kullanıcı öğeleri aynı; bizim kanallar `KURGU_PLANI` ile ±1 kare; boşluk 0; eksik medya 0.
3. **Yama doğrulanamazsa** → klon silinmez, `_ESKI/`'ye taşınır. Kullanıcının kararlarıyla `KURGU_PLANI`'ndan yeni adla bir taslak kurulur: "YZ <FILM> v<N+1> (senin düzenlemenle)". Taşınamayan öğeler (renk ayarı, kendi yazısı) kullanıcıya bir cümleyle söylenir.
4. **Taslak şifreliyse** → okunamaz, yama yapılmaz. Yedek yol kullanıcıya bir cümleyle söylenir: notları CapCut'ta altyazı olarak dışa aktarmak ya da sürümü sabitlemek (açık soru 2).
5. **Kullanıcı kesmesinin köprüsü** Klipler'e plan eklemeyi gerektiriyorsa → kullanıcının taslağına dokunulmaz, ayrı "öneri taslağı" kurulur (KR11-6).

**Neden klon?** BK §5.3.3 ("taslak yeniden kurulmaz") kullanıcının düzenlemelerinin korunmasını ister. Klon bütün düzenlemeleri korur. DR ("bağlı olduğu dosyalara dokunma") ve şifreleme ya da bozulma riski ise kaynağa yazmayı yasaklar. Kaynak, kullanıcının kendi yedeği olarak olduğu gibi kalır. [CM]'nin "aynı projede göreceksin" ifadesinden tek fark, klonun yeni bir adla listenin en üstünde durmasıdır (§4.9.2'de ekip kararına sundum).

**`_RAPOR/YAMA_v<N>.json`:** `{kaynak, kaynak_ozet_once, kaynak_ozet_sonra (eşit olmalı), klon, klipler_ozet_esit, kullanici_ogeleri_esit, bizim_kanallar_degisen_segment, bosluk, eksik_medya, sonuc}`.
**`NOT_CEVAPLARI.md` satırı:** `[06:52] #121 · NOT: "ses geç geliyor" → YAPILAN: J kesme 0,4 sn (KK-T3-2) · dudak denetimi GEÇ`.

#### 4.5.8 `son_capcut_projesi.json` v2 ve yayın doğrulaması **(yeni)**
```json
{"proje": "YZ EMBERFALL_F2 v3", "klasor": "…/com.lveditor.draft/YZ EMBERFALL_F2 v3",
 "kurgu_plani_surumu": 7, "kurgu_plani_imza": "4be1c0d27a91", "sure_sn": 2412.583, "fps": 24,
 "segmentler": [
  {"kanal": "Klipler", "segment_id": "9a1f…", "plan": 121, "sira": 121, "bas": 412.0, "sure": 3.583,
   "kaynak": "KURGU/surumler/v3/klipler/121.mp4", "kaynak_aralik": {"bas": 0.625, "sure": 3.583}},
  {"kanal": "Diyalog", "segment_id": "c07e…", "replik": "R0042", "bas": 413.417, "sure": 3.27}],
 "benim_yazilarim": ["…"], "notlar_kanali": true}
```
`notlari_oku.py` notu `segment_id` → plan eşlemesiyle bağlar. Aynı klipten iki plan çıktığında da doğru planı bulur.

**`_RAPOR/YAYIN_DOGRULAMA.json`** (KR12):
```json
{"dosya": "YAYIN/EMBERFALL_F2_4K.mp4", "kaynak": "capcut_disa_aktarim", "kurgu_plani_surumu": 7,
 "sure": {"olculen": 2412.58, "beklenen": 2412.583, "fark_kare": 0},
 "ses_korelasyon": {"pencere": "60 sn'de bir 10 sn, 40 pencere", "ofset_kare": {"min": 0, "max": 0}, "tepe_min": 0.95},
 "taslak_fark_bos": true, "kullanici_ses_duzenlemesi": false,
 "mux": {"tur": "master_stem", "yapildi": true, "sonra_lufs": -14.1, "sonra_tepe_dbtp": -1.3},
 "kalite": {"siyah": 0, "donma": 0, "plansiz_sessizlik": 0}, "sonuc": "GEC"}
```
- **Pencereli korelasyon:** Tek bir ofset kısmi kaymayı gizleyebilir (bir planın kısaltılması yalnız sonrasını kaydırır). Bu yüzden 40 pencerenin hepsinde ofset 0 ±1 kare olmalıdır.
- **Mux türleri:**
  - `master_stem`: kullanıcı ses düzenlemesi yoksa ve çizelge kanıtı varsa, master stemlerinin miksi konur.
  - `dogrusal_kazanc`: kullanıcı CapCut'ta sesle oynadıysa, onun miksi korunur. Yalnız tek doğrusal kazanç ve gerçek tepe sınırlayıcısı uygulanır ([SM] D5 yöntemi). Böylece kullanıcının göreli denge kararı korunur, yayın seviyesi tutar ([SM] R9'un ölçülebilir hâli).
  - Kanıt yoksa ikisi de yapılmaz; KR11'e dönülür.

#### 4.5.9 `_RAPOR/SEYIRCI_KARAR_<T>_t<n>.json` (izleme kipleri; `seyirci_topla` üretir)
```json
{"kip": "kurgu", "cizelge": "T2", "tur": 2, "kurgu_plani_surumu": 7, "seyirci": 3,
 "partiler": {
  "P1": {"medyan": {"anlasilirlik": 8, "akicilik": 8, "merak": 8, "duygu": 7, "ritim": 7, "ilk30": 9, "GENEL": 8},
         "kritik": 0, "orta": 2, "ozet_eslesme_medyan": 0.83, "gecti": true,
         "onceki_tura_gore": {"GENEL": 0.0, "geri_gidis": false}}},
 "ilk2dk": {"evet": 3, "gecti": true},
 "kritik_gecersiz_sayilan": [{"plan": 214, "seyirci": 3, "hakem": "sureklilik-denetcisi",
                               "kanit": {"sayfa": "P2_1/sayfa_04.jpg", "plan": 213, "zaman": "17:02"}, "betik_dogruladi": true}],
 "ortak_sikilma": [["07:40", "08:30"]],
 "ilgi_korelasyon": 0.58, "dusuk_ilgi_dakikalari": [23],
 "parca_konum_yanliligi": {"egim": -0.08, "bayrak": false},
 "k1_eslesme": {"dogrulanmis": 3, "yalniz_seyirci": 2, "yalniz_makine": 5},
 "anlasilmayan_konusma": 1,
 "karar": "GECMEDI", "neden": ["P2 akicilik 6 < 7"], "en_iyi_surum": 6}
```
- **KRİTİK birleştirme:** Aynı plan (±1) için verilen KRİTİK'ler birleştirilir. İki ya da daha çok seyircinin KRİTİK'i geçersiz sayılamaz. Tek seyircininkini yalnız hakem, kanıtla geçersiz sayabilir (§2.6 madde 7).
- **`parca_konum_yanliligi`:** parça puanlarının izleme sırasına göre eğimi. Eğim sistematik olarak negatifse uzun izlemede dikkat dağılıyor demektir (R16; eşik tahmin).
- **`geri_gidis`:** önceki turda geçen bir partinin bu turda geçmemesi. Varsa önce o partiye etki eden değişiklikler incelenir.

---

### 4.6 Yazılması / değişmesi gereken kod (araç, ne yapar, girdi/çıktı, öncelik)

**Öncelik:** **P0** = ilk film kurgu kapılarından geçemez · **P1** = ilk taslaktan önce hazır olmalı ya da geçici yolu var · **P2** = sonra.
Bütün araçlar mevcut stilde yazılır: başta Türkçe kullanım metni, `sys.stdout.reconfigure`, `_RAPOR/` raporu, [UM] çıkış kodları, `--saglayici sahte` ile ağsız çalışma, `atomik_yaz`, `_uretim` zarfı.

#### 4.6.1 Araçlar

| Araç | Durum | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|---|
| `zaman_cizelgesi.py` | yeni (kütüphane + CLI) | TH/T0/T1/T2/T3 çizelgesini kurar. Olay listesini çıkarır, zamana bağlı bütün ölçüleri hesaplar, eğri grafiğini çizer, sapma raporu yazar, müzik ve kart olaylarının anını çözer (İ-8). **Hikâye odası ve yönetmen kapıları da bu fonksiyonları içe alır** (İ-9) | SAHNELER, HIKAYE, diyalog.json, KURGU_PLANI → `KURGU_PLANI_<T>.json`, `ZAMAN_<T>.json`, `OLAYLAR_<T>.json`, `EGRI_<T>.png`, `SAPMA_<T>.json` | P0 |
| `kirp_oner.py` | yeni | Klipten `kullanim` önerir; adımları eşler; `--zincir` modunda Y55 çıkış penceresini verir (§4.6.2) | klip, plan, kelime zamanları, V1/V2/V3 kusur anları, ağız dizisi → `goruntu.kullanim/guven/gerekce`, `KIRP_INCELE.md`, ölçülen adım süreleri | P0 |
| `plan_kurgu.py` | yeni (belgede var, pakette yok) | T2'yi kurar: kırpma, senkron kuralıyla diyalog, ekran dışı replik, J/L (Y31 ekleriyle), kartlar, örtü planları; ses görevlerini sürüm imzasıyla tetikler | SAHNELER, videolar, diyalog.json v2, T1 → `KURGU_PLANI_T2_v<N>.json` | P0 |
| `kurgu_uygula.py` | yeni | İşlem listesini doğrular (`--kuru`, SubagentStop'ta) ve uygular (`--uygula`). Kilitli alanlara dokunmaz. `*_iste` ve `yeniden_cek` işlemlerini ilgili kuyruğa aktarır | KURGU_KARARLARI + KURGU_PLANI → yeni KURGU_PLANI sürümü + fark raporu | P0 |
| `kurgu_denetim.py` | yeni | Z3 kararı: çizelge aritmetiği, Y31 ekleri, Y54/Y55, B9 kesişimi, komşuluk ölçüleri (yeni sırayla, dondurulmuş durumla; `plan_denetim` ve `dunya_defteri` içe alınır), ses raporlarının birleştirilmesi. Modlar: `--kesme-simule`, `--hepsi` | KURGU_PLANI + raporlar → `_RAPOR/Z3_v<N>.json`, `KESME_SIMULE_<T>.json` | P0 |
| `kurgu_render.py` | yeni (`animatik.py` bunu `--animatik` ile çağırır) | Görüntü montajı: animatik (kare + Ken Burns + eylem şeridi + bitiş görseline geçiş + kartlar), önizleme (kırpılmış klipler), yayın (`--yayin`; çözünürlük ve kodlayıcı ayardan). [SM] stemlerini mux eder. Plan başına önbellek | KURGU_PLANI + medya + stemler → `ANIMATIK/…mp4`, `KURGU/onizleme_v<N>.mp4`, `YAYIN/<film>_master.mp4` | P0 |
| `kor_paket.py` → `izleme` modülü | değişir ([CM] çatısı; `izleme_paketi.py` buraya taşınır) | Animatik, kurgu, ilk 2 dk ve kesici paketleri; aşamalı parça klasörleri; işitsel döküm satırları; ad maskeleme ([CM]/[SN2] ortak kodu); sayfa düzeni | KURGU_PLANI, medya, ISITSEL_DOKUM, HIKAYE → `_GOREV/<id>/GIRDI/…` | P0 |
| `puan_oku.py` v2 / `seyirci_topla` | değişir (ortak) | Medyan, 6 ölçüt, KRİTİK birleştirme, hakem kanıt doğrulaması; izleme kipi ekleri: parça puanları, dakika ilgi korelasyonu, konum yanlılığı, geri gidiş, K1 eşlemesi. Eski OZET biçimini okur | seyirci + eşleştirici JSON → `SEYIRCI_KARAR_<T>_t<n>.json` | P0 |
| `bulgu_yonlendir` modülü | yeni (ortak; [SN2] `bulgu-sinifla` ile tek kod) | Eşleştiricinin kimlik eşlemesi + [SN2] tablosu + K1 eşlemesi → sahip, kök neden, merdiven önerisi | → `BULGU_YONLENDIRME_<T>_t<n>.json` | P0 |
| `kuyruk.py` | yeni | Bütün kapıların maddelerini birleştirir, tekrarları ayıklar, önceliği ve zincir etkisini hesaplar, **0 kredi kuralını** ve dilimi zorlar (`kredi.py` ile). Eski klibi `SIRALI_VIDEO/_ESKI/NNN_t<k>.mp4`'e **taşır**, silmez (BK §6.5.4) | kapı raporları, KURGU_KARARLARI, URETIM_ONIZLEME → `YENIDEN_URET`, `URETIM_ONIZLEME.md` | P0 |
| `capcut_film.py` | değişir | `KURGU_PLANI`'ndan sürümlü taslak; `source_timerange` = `kullanim`; sürüm klasörü; Klipler sessiz; Diyalog replik replik (J/L ile); Ambiyans sahne parçaları ve Efekt ([SM] parça listesi); Muzik ipucu parçaları; Kartlar; Altyazi (`altyazi_metin`); NOTLAR (sıra, plan, amaç, duygu, hedef yoğunluk); `--yayin` modunda NOTLAR yok; 48 kHz; tek "geçici akor" kalkar | KURGU_PLANI + ses dosyaları → taslak + `son_capcut_projesi.json` v2 | P0 |
| `taslak_fark.py` | yeni (belgede var, pakette yok) | Taslağı salt okunur inceler (`draft_content.json` + `Timelines/` + birleşik klip içi): kırpılan, silinen, taşınan, eklenen klipler; boşluklar; kayan kanallar; kullanıcı öğeleri; kullanıcı ses düzenlemesi; şifreli taslağı tanıyıp durur. `--oz-denetim` yeni ya da klonlanmış taslakta farkın 0 olduğunu denetler | taslak + son_capcut_projesi + KURGU_PLANI → `TASLAK_FARK.json` | P0 |
| `capcut_yama.py` | yeni | Kullanıcının taslağını klonlar (kaynağa yazmaz), klonda yalnız bizim kanallarımızı yeni plana göre yeniden yerleştirir, yeni medyayı yeni dosya adıyla bağlar, öz denetimi çağırır | taslak + KURGU_PLANI → klon + `_RAPOR/YAMA_v<N>.json` | P1 (yedek yolu var: yeni adla kurmak) |
| `notlari_oku.py` | değişir | Notu `segment_id` → plan eşlemesiyle bağlar; çıktıya sıra ve plan no eklenir; `NOTLARIM.json` | — | P1 |
| `kalite_denetim.py --final` + yayın doğrulaması | değişir (ses ve görüntüyle ortak dosya) | Süre, pencereli ses korelasyonu, mux türü kararı, siyah/donma/sessizlik | dışa aktarım + master miks → `YAYIN_DOGRULAMA.json` | P1 |
| `film.py` | değişir ([UM]/[CM] ile) | KR aşamaları, ön turlar, görev üretimi (görev defteri), animatik imzasının video imzasına bağlanması, döngü sayaçları, `--durum --kurgu` özeti (tur, parti sonuçları, dilim) | — | P0 |
| `saglayicilar/sahte.py` | değişir | Sahte video: `eylem_zinciri` adım pencerelerinde hareket eden kutu ([YN2] ile ortak), `replik_zaman` penceresinde ton; sahte ağız dizisi; sahte CapCut taslak fikstürü (kullanıcı kırpması, silme, taşıma, kendi yazısı) | — | P0 |
| `testler/test_kurgu.py` | yeni | §4.6.3 | `ORNEK_3_SAHNE` + zanaat alanlı 12 planlık `ORNEK_12_PLAN` | P0 |
| `ders_defteri.py` kurgu kayıtları | [UM] aracına ek | Kurgu kategorileri ve bağlam alanları (§4.8-e) | — | P1 |
| OTIO dışa aktarma (`kurgu_render.py --otio`) | yeni | CapCut'a yedek: DaVinci/Premiere için `.otio` (AR1 D, Apache-2.0) | KURGU_PLANI → `.otio` | P2 |

**Geri çektiklerim:** ayrı `seyirci_api.py` (başsız mod [UM]/[CM]'nin `claude_api` sağlayıcısına girer); ayrı `izleme_paketi.py` (`kor_paket.py`'nin modülü olur).

**Kurulum eklentileri** (`KURULUM.bat`): `pyloudnorm` (MIT), `stable-ts` (MIT), `scenedetect` (BSD-3), `opencv-python` (Apache-2.0). MediaPipe sürümü görüntü uzmanıyla birlikte sabitlenir.

#### 4.6.2 Ana algoritmalar

**`kirp_oner.py`** (eşikler kalibre edilene kadar tahmindir)
1. **Hareket enerjisi:** klip 24 fps'te, 160 × 90 gri. `E(t) = ort|f(t) − f(t−1)|`, 0,25 sn medyanla düzleştirilir.
   - Taban, ilk 0,5 sn'nin medyanıdır (klip durağan başlar, ZN §2.2).
   - Kamera hareketliyse (`hareket_tipi ≠ sabit`) enerji yalnız özne kutusunda ölçülür. Kutu [GS] `olcum/` paketinden gelir.
   - Başlangıç: `E > taban + 3·MAD` koşulunun ≥ 0,2 sn sürdüğü ilk an. Bitiş: koşulun son sağlandığı an.
2. **Güvenli pencere:** `[0,5 ; klip_sn − 0,5]` aralığı; ilk V1/V2/V3 kusurundan 0,1 sn öncesiyle ve klip içi kesmeden (PySceneDetect) önceki bölümle kesiştirilir.
3. **Adım eşleme (yeni):** planlanan adımlar (`a1…a3`, saniyeleriyle) ölçülen hareket bölütlerine sırayı koruyarak eşlenir. Ölçülen bölüt sayısı adım sayısından azsa (Veo bir adımı atladı) BAYRAK verilir. Ölçülen adım süreleri ders defterine gider (`fiil_sozlugu.sure_carpani` adayı, [YN2]).
4. **Kırpma önceliğine göre:**
   - `replik`: konuşmadan önce adım varsa `bas` = ölçülen adım başı − 0,1. Yoksa `bas` = ilk kelime − 0,4 (RE `diyalog_giris_payi_sn`). Çıkış L değilse son kelime + 0,3 (RE `replik_sonu_kesme_sn` içinde). L ise planlanan taşmayla Y31 eklerine göre.
   - `eylem`: `bas` = hareket başı − 0,1 (geç gir). Çıkış eylem kesmesiyse son adımın %60–70'inde, değilse son adım bitişi + 0,5 sn tutmada. Ölü süre ≤ 0,6 sn.
   - `tepki_tepesi`: 1,5–4 sn'lik pencere mikro hareketin tepesini ortalar. Ağız dizisinde hareket varsa BAYRAK verilir, çünkü üstüne ekran dışı replik konamaz.
   - `durgun` (kuruluş, geçiş): sarsıntısı en az pencere; süre plan tipinin hedefidir.
5. **`--zincir` (KR5):** son adımın ölçülen bitişi + 0,2 ≤ çıkış ≤ `klip_sn − 0,5`; aralıkta enerjinin en düşük olduğu bölge.
6. **Güven:** bütün işaretler tutarlıysa 1. Hareket başlangıcı bulunamazsa, duyulan kelime planlananın %70'inin altındaysa ya da kusur pencereyi daraltıyorsa düşer. Ölçülemezse güven 0 olur ve plan kurgucuya gider (asla sessiz geçiş yok). < 0,6 ise `kurgucu` bakar.

**`zaman_cizelgesi.py` eğri ölçüleri** (tur 1 ile aynı; şimdi ortak kütüphane)
- Plan yoğunluğu saniye dizisine açılır: `y(t)`, `tür(t)`. Hedef eğri film süresine oranla gerilir: `hedef(t) = harita[⌊t · 2400 / L / 60⌋]` (RE `duygu_haritasi_40dk`).
- Ölçüler:
  - Sapma: `|y − hedef| > 2` olan kesintisiz bölüm > 60 sn ise BAYRAK.
  - 3 dk pencerede tepe: 10 sn adımla kayan 180 sn pencerede `max y ≥ 6`.
  - Düz çizgi: tür aynı ve `max − min ≤ 2` olan bölüm > 180 sn ise BAYRAK.
  - Tepe öncesi çukur: tepe ≥ 8 ise (ilk 30 sn hariç) `[t−120, t−60]` aralığında `min ≤ tepe − 2`.
  - Kademe: `ASL[t−30, t] ≤ 0,75 · ASL[t−90, t−30]`. Tepeden sonraki 20 sn içinde ≥ 5 sn'lik bir plan olmalı (20 sn tahmin).
  - Dakika başına baskın tür üç dakika üst üste aynıysa BAYRAK.
- Hikâye düzeyinde (TH) aynı fonksiyonlar sahne hedef süreleriyle ve ±%15 belirsizlik bandıyla çalışır ([SN1] §7).

**`kurgu_render.py`**
- Her plan ayrı parça olarak işlenir ve önbelleğe girer (`KURGU/_onbellek/seg_<özet>.mp4`); sonra concat ile birleştirilir.
- Durağan karede `zoompan` kullanılır. Yazılar PIL ile şeffaf PNG olarak çizilip bindirilir.
- Ses: [SM] stemleri (`diyalog`, `efekt`, `ambiyans`, `muzik`) ya da miks mux edilir. Render kendisi miks yapmaz (İ-9).
- `--yayin`: çözünürlük ve kodlayıcı `FILM_AYAR.json`'dan okunur (KR'de 4K 24 fps). Donanım kodlayıcısının varlığı açık sorudur.

**`capcut_yama.py`**
1. Kaynak taslak `clone_project` emsaliyle klonlanır (yeni kimlikler, iç yollar yeniden bağlanır, kaynak yazılmaz).
2. Klonun Klipler segmentleri `son_capcut_projesi.json` v2 `segment_id`'leriyle plana eşlenir; eşlenemeyen segment kullanıcı öğesidir.
3. Bizim kanal segmentleri silinip `KURGU_PLANI` (kullanıcı kararları kilitli) ve [SM] parça listesinden yeniden yerleştirilir. Kullanıcının ses kanalı ayarı (seviye) varsa korunur.
4. `taslak_fark --oz-denetim` klon üzerinde çalışır; sonuç `YAMA_v<N>.json`'a yazılır.

**`kurgu_denetim.py --kesme-simule`**
- Her öneri çizelgeden çıkarılır. Z0/Z1/Z2 zaman ölçüleri, Z1 #29–32 (kurulum → kullanım), Y58 (dondurulmuş durumla yeni komşular) ve 180°/bakış yeniden koşar.
- HATA getiren öneri `reddedildi` olur, gerekçesi yazılır ve uygulama oranının paydasına girmez (İ-6).
- Sahne kesme önerileri simülasyondan geçerse yazara istek olarak gider.

#### 4.6.3 Testler (`testler/test_kurgu.py`; ağ ve kredi yok; `sahte` + `kaset` sağlayıcıları)
1. **T0 çizelgesi:** toplam süre, ASL, J/L oranı ve eğri sapması sentetik plana göre beklenen değeri verir.
2. **Tek ölçü tek kod (yeni):** `hikaye_odasi senaryo-denetim`, `plan_denetim` ve `zaman_cizelgesi` aynı girdide aynı zaman ölçüsünü verir; üçü de aynı fonksiyonu içe alır.
3. **Animatik:** render süresi = T1 ±1 kare; eylem şeridi yalnız görünür adımlardan; pakette amaç ve `ekranda_bilgi` yok.
4. **Kırpma:** sahte videoda (hareketli kutu) `kirp_oner` hareket başlangıcını ±2 kare bulur; önizleme süresi = Σ kullanım; atlanan adım BAYRAK verir.
5. **Senkron ve J/L:** bölünmüş klipte 2. parçanın `bas` değeri doğru; kaydırılmış diyalog HATA; Y31 ekleri (ekranda konuşulan kısım < 1,0 sn, taşmanın üstündeki plan çok kısa) HATA.
6. **Paket sızıntısı (yeni):** ad maskesi; kopukluk adayı yok; izleme kiplerinde kadraj etiketi yok; kesici paketinde `ekranda_bilgi` yok; P1 raporu yazılmadan P2 klasörü GIRDI'de yok.
7. **Puan:** {6, 8, 9} → 8; iki seyircinin KRİTİK'i geçersiz sayılamaz; hakem kanıtını betik doğrulamazsa KRİTİK kalır; kurgucunun imzaladığı geçersiz sayma reddedilir.
8. **Kuyruk:** `sifir_kredi` alanı yoksa ret; dilim yetmezse ORTA → 0 kredi; KRİTİK sığmazsa çıkış 5 ([UM] bütçe kodu); zincir etkisi maliyette; plan başına 3. yeniden çekim reddedilir.
9. **Kapı:** animatik `ONAYLI` imzası yoksa video görevi açılmaz ([UM] T4 ile ortak).
10. **Kesme turu:** kurulum götüren kesme HATA verir ve paydaya girmez; oran doğru hesaplanır.
11. **Dondurma:** etkisi olan planın sahne içi sırası değişince Y58 HATA; etkisiz plan serbest.
12. **Taslak farkı:** fikstür taslakta kırpma, silme ve taşıma bulunur; kullanıcı kırpması kilitlenir, sonraki `kirp_oner` ona dokunmaz.
13. **Yama (yeni):** kaynak taslağın özeti değişmez; klonda Klipler özeti kaynağınkine eşit; Diyalog yeni sıraya kayar; boşluk 0.
14. **Yayın doğrulaması (yeni):** 0,4 sn kaydırılmış dışa aktarım → bir pencerede ofset ≠ 0 → mux reddedilir; kullanıcı ses düzenlemesi varsa yalnız doğrusal kazanç uygulanır.
15. **Müzik olayı (yeni):** kırpmadan sonra müzik giriş anı olayla birlikte kayar.
16. **Örtü (yeni):** formülün altındaki örtü süresi BAYRAK verir.

---

### 4.7 Makinenin denetleyeceği eşikler (kaynağıyla)

**Kodlar:** **H** = HATA (geçmez) · **B** = BAYRAK (ajan bakar) · **●** bu çizelgede ölçülür · **↻** yalnız kesme ya da sıra değişikliğinden sonra yeniden ölçülür · **—** yok.
**T3 kuralı:** Kullanıcının kararı aynen uygulanır. Kullanıcının kendi kırpması ya da sırası yüzünden doğan HATA, BAYRAK'a döner ve öneriyle bildirilir; karar geri alınmaz.
**(değişti)** "Ölçen" sütunu her ölçünün **tek** aracını gösterir (İ-9).

#### 4.7.1 ZANAAT eşikleri: hangi çizelgede, hangi araçla

| ZN # | Ölçü | Eşik (RE anahtarı) | T0 | T1 | T2 | T3 | Ölçen | Sonuç |
|---|---|---|---|---|---|---|---|---|
| 1 | Toplam süre (kart + jenerik dahil) | 1800–2700 sn (`film_sure_aralik_sn`) | ● | ● | ● | ● | `zaman_cizelgesi` | H |
| 2 | Parti süresi / film | 0,30–0,35 (`parti_sure_oran_aralik`) | ● | ● | ● | ● | `zaman_cizelgesi` | B |
| 3 | Vuruş zamanı | oran ±0,04 (`vurus_oranlari`, `vurus_oran_tolerans`) | ● | ● | ● | ● | `zaman_cizelgesi` | B |
| 4 | Plan süresi / tip | `plan_sure_aralik_sn` | ● | ● (diyalog) | ● | ● | `zaman_cizelgesi` | H (T3'te B) |
| 5 | Diyalog süresi ≥ formül; L kesmede görüntü + taşma ≥ formül ([YN2] Y31) | ZN §2.3 | ● formül | ● TTS | ● ölçülen | ↻ | `zaman_cizelgesi` | H |
| 7 | ASL film / parti / ilk 120 / ilk 30 | 4,2–5,2 / ±0,6 / ≤ 4,0 / ≤ 3,5 (`asl_*`) | ● | ● | ● | ● | `zaman_cizelgesi` | B |
| 8 | Sahne süresi | ≤ 180 sn (`sahne_max_sn`) | ● | ● | ● | ● | `zaman_cizelgesi` | H |
| 9 | Diyalog sahnesinde tepki oranı | ≥ 0,25 (`tepki_orani_min`) | ● | ↻ | ↻ | ↻ | `zaman_cizelgesi` | B |
| 10 | Diyalog sahnesinde J/L oranı | ≥ 0,30 (`jl_kesme_orani_min`) | ● plan | ● gerçek | ● gerçek | ● | `zaman_cizelgesi` | B |
| 11 | Aynı plan tipi art arda | ≤ 4 (`ayni_plan_tipi_ardisik_max`) | ● | ↻ | ↻ | ↻ | `plan_denetim` (içe alınır) | B |
| 12 | Ölçek sıçraması | ≥ 2 kademe ya da ≥ 30° (`olcek_kademe_min_fark`, `aci_min_fark_derece`) | ● | ↻ | ↻ | ↻ | `plan_denetim` + `kroki` | H (T3'te B) |
| 16–18 | Durum zinciri, 180°, bakış | ZN §6.2; yeni komşular **dondurulmuş durumla** ([YN2] Y58) | ● | ↻ | ↻ | ↻ | `dunya_defteri` + `kroki` | H (T3'te B) |
| 21 | İlk eylem / ilk merak sorusu | ≤ 5 sn / ≤ 20 sn (`ilk_eylem_max_sn`, `ilk_merak_max_sn`) | ● | ● | ● ölçülen hareket başı | ● | `zaman_cizelgesi` | H |
| 22 | Başlık kartı | 45–120 sn, ≤ 6 sn (`baslik_karti_*`) | ● | ● | ● | ● | `zaman_cizelgesi` | B |
| 23 | Ana karakter adı | ≤ 120 sn (`kahraman_adi_max_sn`) | ● | ● | ● duyulan metin | ↻ | `zaman_cizelgesi` | H |
| 24 | Risk sözle; parti başında tazeleme | ≤ 180 sn; ≤ 60 sn (`risk_sozlu_max_sn`, `parti_basi_risk_tazeleme_max_sn`) | ● | ● | ● | ↻ | `zaman_cizelgesi` | H |
| 25–28 | Merak olay aralığı, açık soru sayısı, soru ömrü, parti sonu sorusu | ZN §4.3 (`merak_*`, `acik_soru_aralik`, `soru_omru_max_sn`) | ● | ● | ● | ↻ | `zaman_cizelgesi` | B / H (#28) |
| 29–32 | Kurulum → kullanım; hatırlatma | ≥ 20 sn; > 600 sn'de hatırlatma (`kurulum_kullanim_min_sn`, `hatirlatma_esigi_sn`) | ● | ↻ | ↻ | ↻ | `zaman_cizelgesi` (her kesmeden sonra; DR "kullanıcının kestiği plan bilgiyi götürür") | H |
| §1.4 | İlk 30 sn manzara; vaat imgesi; parti başı kanca dönüşü; seri kancası; jenerik | ≤ 1 plan ve ≤ 3 sn; ≤ 120 sn; ≤ 20 sn; ≤ 20 sn; ≤ 60 sn | ● | ● | ● | ● | `zaman_cizelgesi` | B |
| 35–39 | Duygu eğrisi: sapma, 3 dk tepe, düz çizgi, çukur; parti sonu / doruk / en karanlık | ±2 ve 60 sn; ≥ 6; ≤ 180 sn; ≥ 2 puan; ≥ 8 / ≥ 9 / ≥ 6 (`yogunluk_*`, `pencere_*`, `duz_cizgi_max_sn`, `tepe_oncesi_*`, `*_yogunluk_min`) | ● | ● | ● | ● | `zaman_cizelgesi` | B / H (#39) |
| 2.5.2 | Kademe | tepeye giden 30 sn'de ASL ≥ %25 düşer (`tepe_oncesi_asl_dusus_min`) | ● | ● | ● | ● | `zaman_cizelgesi` | B |
| 40 | Müzik kaplama; müziksiz ve müzikli en uzun blok | %40–65; ≤ 240 / ≤ 300 sn (`muzik_*`) | — | ● | ● | ● | **ses** (`muzik.py` S6.4) | B |
| 41–42 | `kullanim.bas`; `bas + sure` | ≥ 0,3; ≤ klip_sn − 0,5 (`kullanim_*`) | ● plan | — | ● | ● | `kurgu_denetim` | B |
| 43 | Ölü süre | ≤ 0,6 sn (`olu_sure_max_sn`) | — | — | ● | ● | `kurgu_denetim` (`kirp_oner` ölçüsü) | B |
| 44 | Replik seviyesi | hedef ±1 LU (`diyalog_lufs`, `diyalog_lufs_tolerans`) | — | ● TTS | ● | — | **ses** (`diyalog_esitle` S4) | H |
| 45 | Sahne içi ambiyans farkı; ambiyans boşluğu | ≤ 3 LU; 0 (`ambiyans_sahne_ici_fark_max_lu`) | — | ● | ● | ● | **ses** (`ses_katmani` S5) | H |
| 46 | Diyalog altında müzik | ≥ 12 dB aşağı (`muzik_diyalog_alti_min_db`) | — | ● | ● | ● | **ses** (`muzik.py` S6.2) | H |
| 47 | Son karışım; gerçek tepe | −14 ±1 LUFS; ≤ −1 dBTP (`final_lufs*`, `true_peak_max_dbtp`) | — | ● | ● | ● dışa aktarılan dosya | **ses** (`son_miks` S7) + `kalite_denetim --final` | H |
| 49 | Kurgu izleme (habersiz seyirci) | ZN §7.3; §4.7.2 | — | ● animatik | ● kurgu | ↻ büyük değişiklikte | seyirci + `seyirci_topla` | H |
| — | Senkron (görünen konuşanın yerleşimi) | ≤ 1 kare (`senkron_tolerans_kare`) | — | — | ● | ● | `kurgu_denetim` | H |
| — | Dudak ofseti (ölçülen) | ≥ %95 replik ≤ 42 ms; hiçbiri > 125 ms | — | — | ● | ● | **ses** (`dudak_denetim` S3.1) | H/B |
| — | Ağzı oynayan yüzün üstüne başkasının repliği (B9) | 0 | — | — | ● | ● | `kurgu_denetim` (ağız dizisi sesten) | H |
| — | Cevap boşluğu ([SM] S3.8'den taşındı) | 0,2–0,6 sn (`cevap_boslugu_sn`) | — | ● | ● | ● | `kurgu_denetim` | B |
| — | Bölünmüş klipte atlanan aralık bir sözle kesişiyor ([SM] S3.6'dan taşındı) | 0 | ● plan | — | ● | ● | `kurgu_denetim` | H |
| — | Örtülü devam; Z1 kesmesi bitiş tutmasının içinde | [YN2] Y54 + İ-11 formülü; Y55 | ● plan | ● | ● | ● | `kurgu_denetim` | B; H |
| — | CapCut boşluğu, eksik medya | 0 | — | — | — | ● | `taslak_fark` | H |
| — | Geri gidiş | Tk'de geçen ölçü Tk+1'de HATA olamaz | — | ● | ● | ● | `zaman_cizelgesi` (rapor karşılaştırması) | H |
| — | Render süresi (animatik, önizleme) | çizelge toplamı ±1 kare | — | ● | ● | — | `kurgu_render` | H |

#### 4.7.2 Seyirciden gelen ölçüler (animatik ve kurgu)

| Ölçü | Eşik | Kaynak |
|---|---|---|
| Seyirci sayısı; birleştirme | 3 yeni seyirci, bütün film, aşamalı girdi; medyan | RE `seyirci_sayisi`, `seyirci_karar`; [SN2] İ6 |
| GENEL medyan; hiçbir ölçüt medyanı | ≥ 8; ≥ 7 | RE `seyirci_genel_esik`, `seyirci_olcut_min` |
| Ölçüt hedefleri | anlaşılırlık 8, akıcılık 8, merak 8, duygu 7, ritim 7, ilk30 8 | RE `seyirci_olcut_hedef` |
| KRİTİK / ORTA (parti başına) | 0 / ≤ 3 | RE `kopukluk_kritik_max`, `kopukluk_orta_max_parti` |
| Tek seyircinin KRİTİK'inin geçersiz sayılması | yalnız hakem, kanıtla; betik doğrular | §2.6 madde 7 |
| Özet eşleşmesi | ≥ 0,80/parti (kısmen = 0,5; tahmin) | RE `ozet_eslesme_min` |
| Ortak sıkılma → kesme turu | ≥ 2 seyirci | RE `sikilma_ortak_isaret_min` |
| İlk 2 dk devam (başlık + kapak tarifiyle) | 3/3 | RE `ilk2dk_devam_evet_min`; [SN2] H12 |
| Tur sayısı | animatik 3 (+ kurtarma 2); kurgu 3 (+ koşullu 2); ön turlar sayılmaz | RE `kurgu_tur_max`; ekler tahmin |
| Kesme turu | 10 plan + 2 sahne öneri; simülasyondan geçenlerin ≥ %50'si uygulanır | RE `kesme_turu_oneri`; İ-6 |
| İlgi eğrisi ↔ hedef eğri | Spearman ≥ 0,5; medyan ilgisi ≤ 4 olan dakika kesme turuna girer | tahmin |
| Parça konum yanlılığı | parça başına GENEL eğimi < −0,15 ise BAYRAK (uzun izlemede dikkat dağılması) | tahmin |
| Anlaşılmayan konuşma | KRİTİK sayılmaz ama [SM] S7.6 ile eşlenir; seyirci bundan kopukluk yazdıysa sahibi ses olur | [SM] §8.2 (a) |
| Defterde açık olup seyircide olmayan soru | hedef 0; BAYRAK → yazar | ZN §7.3 ek çıktı 4 |
| K1 eşlemesi | `yalniz_seyirci` bulgular ders defterine `kacirma` etiketiyle | İ-1; [GS] §8.7 |

#### 4.7.3 Bu belgenin önerdiği yeni eşikler (`ritim_esikleri.json`'a eklenecek; her anahtarda `deger`, `aciklama`, `kaynak`, `etiket`)

| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `izleme_parcasi_sn` | [240, 300] | — | BK §3.8, H/kurgu-izleme-denetimi ("~4–5 dk") |
| `izleme_kare_plan` | kurgu 3, animatik 1 (+ bitiş görseli) | — | ZN §7.3, BK §3.8 |
| `izleme_sayfa_plan` | 6 | — | tahmin |
| `animatik_tur_max`, `animatik_kurtarma_tur` | 3, 2 | — | tahmin ([UM] 3) |
| `kurgu_kurtarma_tur`, `kurgu_kurtarma_kosul_genel_artis` | 2, 0,5 | — | tahmin |
| `animatik_yer_tutucu_max_oran` | 0,10 | H | tahmin |
| `animatik_bitis_gecis_sn` | 0,5 | — | tahmin |
| `ken_burns_zoom`, `ken_burns_kayma` | 0,08, 0,02 | — | kurgu köprüsü V5 varsayılanı (`KULLANIM.txt`) |
| `render_sure_tolerans_kare` | 1 | H | (hesap) çizelge 1/24 sn'ye yuvarlı |
| `sapma_plan_oran_max` | 0,25 (T0↔T1, T1↔T2) | B | tahmin |
| `senkron_tolerans_kare` | 1 (24 fps) | H | AR3 öneri 4 (mühendislik tercihi) |
| `l_kesme_gorunen_konusma_min_sn` | 1,0 | H | tahmin; seyirci kimin konuştuğunu görmeli (ZN §4.1 "Kim?") |
| `l_kesme_klip_ses_son_pay_sn` | 0,3 (replik klipte `klip_sn − 0,3`'ten önce bitmeli) | H | tahmin; taşan ses aynı klipten gelir |
| `l_kesme_alici_plan_ek_sn` | 0,5 (üzerine binilen plan ≥ taşma + 0,5) | H | RE `diyalog_cikis_payi_sn` |
| `j_kesme_klip_kosulu` | sonraki klipte konuşma başı ≥ J öne alma (ses klipte var) | H | (hesap) senkron kuralı |
| `ortu_min_sn` + formül | max(1,0; A tutma + B durağanlık) | B | [YN2] Y54 + İ-11; tahmin |
| `zincir_cikis_tutma_ic_min_sn` | 0,2 | H | [YN2] Y55; tahmin |
| `zincir_derinlik_max` | 2 | H | AR2 §2.3 |
| `kirp_guven_min` | 0,6 | B | tahmin |
| `kirp_hareket_mad_k`, `kirp_hareket_sure_sn` | 3, 0,2 | — | tahmin |
| `hiz_aralik_diyalogsuz` | [0,90, 1,15] | H | tahmin |
| `yeniden_kadraj_max` | 0,10 | H | tahmin |
| `tepe_sonrasi_uzun_plan_pencere_sn` | 20 | B | tahmin |
| `kesme_uygulama_payda` | "simulasyon_temiz" | — | İ-6 |
| `yeniden_pay_dilim` | {goruntu 0,15, ses 0,07, kurgu 0,08} | — | tahmin; toplam [UM] C1 0,30 |
| `plan_basi_yeniden_cekim_max` | 2 (teknik + kurgu birlikte) | H | [UM] |
| `oncelik_konum_agirligi`, `oncelik_dogrulanmis_carpan` | 1,5, 1,25 | — | tahmin |
| `ilgi_korelasyon_min`, `ilgi_dusuk_esik` | 0,5, 4 | B | tahmin |
| `ozet_kismen_agirlik` | 0,5 | — | tahmin |
| `parca_konum_egim_bayrak` | −0,15 GENEL/parça | B | tahmin |
| `anlasilmayan_konusma_wer` | 0,30 | — | [SM] S7.6 H eşiği |
| `kopru_replik_sahne_max` | 1 | B | tahmin ([SN2] H15) |
| `mux_ofset_max_kare`, `mux_korelasyon_min`, `mux_pencere` | 1, 0,9, 40 × 10 sn | H | tahmin |
| `yayin_sure_tolerans_kare` | 1 | H | (hesap) |

**Kalibrasyon kuralı:** "Tahmin" işaretli her eşik ilk iki filmde ölçülür. Ders defteri eşik ↔ seyirci puanı ↔ kullanıcı notu ilişkisini kaydeder. Bir değer ancak [UM] §7.4 terfi kuralıyla (≥ 3 kayıt ve ≥ 2 film, ya da tek filmde ≥ 5) ve [GS] §7.9 korkuluklarıyla değiştirilir. Güvenlik kuralları (Flow'da dur, gizli bilgi, silme yasağı) öğrenmeyle gevşetilemez. ZN'deki sayıların çoğu da test edilmemiş türetmelerdir (ZN §2.6 kendi hesabı); kurgu turları bu sayıları doğrulayacak ilk veri kaynağıdır.

---

### 4.8 Kesin kararların kendi alanımda uygulanışı

#### 4.8.1 Karar 2 — Atomik eylem zinciri
Kurgu açısından atomik zincirin en büyük kazancı şudur: kesme noktası artık tahmin edilmez, plandan **hesaplanır** ve videoda **ölçülür**.
1. **Kesme eylemin üstünde:** `kesme.tip: eylem` ise A son adımın %60–70'inde biter; B aynı adımın devamıyla başlar (ZN §3.4). B'nin başlangıç durumu A'nın bitiş durumudur (ZN §3.7). `kirp_oner` planlanan adım saniyelerini klipte ölçülen hareket bölütlerine eşler ve kesmeyi oraya koyar. Adıma kalıcı kimlikle (`a2`) bağlanır.
2. **Ölçülen adım ≠ planlanan adım:** ölçülen bölüt sayısı adım sayısından azsa (Veo bir adımı atladıysa) BAYRAK verilir. Kurgucu önce eksik adımın başka bir planda görünüp görünmediğine bakar (ekleme köprüsü, ZN §3.5). Görünmüyorsa 0 kredi merdiveni, sonra yeniden çekim. Planlanan ve ölçülen adım süreleri ders defterine gider ve `fiil_sozlugu.sure_carpani`'yı kalibre eder ([YN2]).
3. **Efekt, ölçülen adım anına oturur:** Efekti [SM] yerleştirir; kurgu ona klip zamanı ↔ çizelge zamanı eşlemesini (`KURGU_PLANI`) verir. Yeniden çekilen planda efekt ve müzik kendiliğinden yeniden yerleşir (DR "yeni çekilen planlar efektsiz kalıyordu").
4. **Konuşmalı planda adım replikten önce gelir** (ZN §3.7, P087 örneği). `kirp_oner` replik penceresiyle bir fiziksel adımın çakıştığını ölçerse BAYRAK verir (konuşurken nesneyle uğraşmak dudağı bozar, ZN §2.3).
5. **Animatikte eylem şeridi = zincirin kendisi:** Şerit metni `plan_dili.gorunur_tarif(dil="tr")` ile Flow'a giden istemle aynı kaynaktan çıkar ([YN2]). Zincirde mantık boşluğu varsa (kapı açılmadan içeri girmek gibi) seyirci animatikte görür.
6. **Senkron kuralı:** görünen konuşanın sesi her zaman klip zamanına bağlı yerleşir. Bu yüzden J/L, klip bölme ve kırpma dudak kaymasına yol açamaz. B2'deki "seslerde kayma" bu kuralın bozulmasından çıkmıştı (H/proje-b2).

#### 4.8.2 Karar 3 — Altı özellik

**(a) Videodan önce animatik film + habersiz seyirci**
- Animatik T1 çizelgesiyle **gerçek sürelerde** kurulur. Ses, seçilmiş evren sesiyle üretilmiş TTS'tir (İ-4). Seyirci ritmi tahminle değil gerçek süreyle yargılar; "gereksiz uzun" notu kredi harcanmadan yakalanır.
- Diyalog, J/L, ambiyans, müzik ve kartlar son kurguyla aynı kodla yerleşir (`zaman_cizelgesi` + [SM] stemleri). Animatikte geçen ses ve ritim kuralları T2'de geri gidemez.
- Kesme turu animatikte de yapılır; kesilen plana video kredisi harcanmaz (B11). B2'de animatik atlanmış, 50'den fazla yeniden çekim olmuştu ve "B1'de video kredisini animatik onayı olmadan yakmak sonradan yamaya yol açtı" (H/proje-b2).
- **Animatik geçmeden video aşaması başlamaz.** Bu bir beceri cümlesi değil, koddur: video görevinin girdi imzası animatik kararının imzasını içerir ([UM] T4; test 9).
- Habersizlik dört katmanla korunur: (1) seyirciye yalnız betiğin ürettiği paket verilir; (2) araç yalnız Read ve Write'tır, okuma görev klasörüne kancayla bağlıdır ([CM] K-3); (3) aşamalı girdiyle ilerisi okunamaz; (4) pakette kopukluk adayı, `ekranda_bilgi`, özet ve ad yoktur (İ-1, İ-7).
- **(yeni)** P1 ön turu, P2/P3 görselleri üretilmeden dersleri taşır (KR3a).

**(b) Dünya durumu defteri + otomatik zıplama denetimi**
- Defterin sahibi süreklilik uzmanıdır ([YN2] Ç-5). Kurgu defteri **tüketir**: kurgucu, kesici ya da kullanıcı çizelgede bir planı kesip yer değiştirdiğinde zıplama denetimi **yeni sırayla ve dondurulmuş durumlarla** yeniden koşar (Y58). Örnek: "anahtar A'dan B'ye geçti" bilgisini taşıyan plan kesilirse sonraki planda anahtar açıklamasız B'nin elinde kalır. Kesme simülasyonu bunu HATA olarak yakalar; kesici "bu plan gereksiz" dese bile kesme uygulanmaz.
- Dondurma yüzünden durumu değiştiren planların sahne içi sırası değiştirilemez (merdiven #2 yalnız `etki`siz planlar). Bu, kurgunun seçeneğini daraltır ama doğrudur: o planların görüntüsü eski komşularının durumuyla üretilmiştir.

**(c) Referansla otomatik yüz kontrolü**
- V2'nin kare kare kimlik dizisi kırpma penceresini daraltır: yüz kaymasının başladığı andan önceki bölüm kullanılır (ZN §2.2 d). Kalan pencere plan tipinin alt sınırından kısaysa madde 0 kredi merdiveninden geçer, sonra kuyruğa girer.
- Seyirci "bu aynı kişi mi?" derse kurgucu önce V2 sayılarına bakar. Sayılar yüz kaymasını doğrulamıyorsa sorun kostüm ya da ışık olabilir; madde süreklilik uzmanına gider.
- Sesin karşılığı [SM] S3.4'tür (ağzı oynayan yüzün kimliği = replik karakteri). Kurgu, L/J ve ekran dışı yerleşimde bu sonucu okur.

**(d) Kare zinciri (son kare → sonraki klibin başlangıcı)**
- **Z1 varsayılandır** ([YN2] İ-2, [GS]). [UM] C5'in `bitis_karesi` (Bitir yuvası) varsayılanına kurgu açısından ek bir gerekçeyle itiraz ediyorum: Bitir karesine klibin **son karesinde** ulaşılır (8,0 sn). Bu an güvenli pencerenin dışındadır (RE `kullanim_son_pay_sn` 0,5; ZN §2.2 "son 0,5–1,0 sn'de morf riski"). Seyircinin gördüğü kesme anındaki kare ise Bitir karesi değildir. Yani Bitir'le kurulan dikiş, seyircinin gördüğü yerde garanti edilmez. Z1'de B'nin başlangıç karesi, A'nın **kurguda kullanılan** son karesinin ta kendisidir.
- **Kilit:** Z1 kaynağı A'nın çıkış noktası kurguda değiştirilemez (`kullanim_kilit: zincir`). Kurgucu yalnız B'nin başını kırpabilir (≥ 0,3 sn). A yeniden çekilirse B de çekilir; kuyruk bunu `zincir_etkisi` ile önceden gösterir.
- **Dikiş:** Veo klibinin başındaki durağanlık ile A'nın bitiş tutması yan yana gelince "takılma" görülür. Doğal durak yoksa araya bir örtü planı girer (Y54; süresi İ-11 formülüyle); örtü önce mevcut kliplerden (0 kredi) aranır.
- **Dalgalar:** `devam` ile bağlı planlar aynı Memmet partisinde gönderilemez. Kredi değişmez, süre biraz uzar; tempo kuralları her dalgada aynıdır (DR).

**(e) Kendi kendine öğrenen ders defteri (kurgu payı)**
Biçim [UM]/[CM]'nin ortak biçimidir: tek olay tek kayıt, terfi kuralı, korkuluklar. Kurgu şu `kategori` değerlerini ve bağlam alanlarını ekler:
1. **Kök neden sayımı** (`veri/kok_neden.json`): hangi kopukluk türü, kaç kez, hangi aşamada (T1 mi T2 mi) yakalandı. Hikâye kök nedenli bulguların animatikte mi kurguda mı ilk göründüğü, hikâye odasının "gecikmeli karnesi"dir ([SN1] §1.3).
2. **Düzeltmenin işe yarayıp yaramadığı:** düzeltilen madde sonraki turda yeniden işaretlendiyse çözüm `duzelmedi` diye kaydedilir ([UM] `sonuc` alanı). Merdivenin hangi basamağının hangi soruna yettiği böyle öğrenilir.
3. **Ölçü ↔ puan ilişkisi:** ASL, J/L oranı, ölü süre ve eğri sapması ile seyirci ritim/akıcılık medyanı. Tahmin eşikler (§4.7.3) bununla kalibre edilir.
4. **Kipler arası puan farkı:** kâğıt → plan → animatik → kurgu GENEL farkları ([SN2] §4.8.3 (a)). Animatikteki durağan karelerin ritim puanını aşağı çekip çekmediği (R13) burada görülür.
5. **Veo zaman sapması:** plan tipine ve fiile göre planlanan ve ölçülen adım süresi (`sure_carpani`).
6. **Gerçek yeniden çekim oranı** ve dilim başına harcanan kredi (B12'nin %8 tahmini burada sınanır).
7. **Ön turların değeri:** P1 ön turunun tek başına yakaladığı ve P2/P3'te önlenen bulgular.
8. **K1 eşlemesi:** makinenin kaçırdığı, seyircinin yakaladığı geçişler ([GS] kalibrasyonuna veri).

**(f) Kalıcı seri evreni kütüphanesi (kurgu varlıkları)**
- Kurgunun koyduğu ve sonraki filmde yeniden kullandığı varlıklar: başlık, yer/zaman kartı ve jenerik **şablonları** (font, renk, konum, süre), renk cilası ayarı, CapCut kanal düzeni. Yer: `EVREN/<SERI>/sablonlar/`; yazan `evren.py`.
- Başkalarının varlıklarını kurgu okur: karakter `maske` (hikâye), karakterin ölçülen konuşma hızı ve ses profili ([SM]), mekân ambiyans zemini ([SM]), leitmotifler ([SM]).
- **(değişti)** Önceki filmin seyirci özeti kapı seyircisine verilmez ([SN2] İ2). Kurgu seyircisinin özetleri yalnız `IZLEYICI_OZETI.md`'yi besler; onu da yalnız medyana girmeyen "dönen seyirci" okur.
- Kurgu dersleri seri boyunca birikir (e).

#### 4.8.3 Karar 4 — Ses ve dudak uyumu (kurgunun koşulları)
Ses yolunu ses uzmanı seçer. Kurgu [SM]'nin ana yolunu (Yol A: Veo konuşur, ses ayrılır, karakterin evren sesine dönüştürülür; ağzı görünmeyen replikte Yol B TTS) destekler, çünkü:
- Zamanlama Veo'dan gelir; dudak bozulmaz ve senkron kuralı doğrudan uygulanır.
- L kesme ayrılmış ses kanalıyla serbestçe yapılır; taşan ses aynı klipten gelir (`l_kesme_klip_ses_son_pay_sn`).
- Dönüşümün hedef sesi TTS sesiyle aynı olduğu için ekran dışı TTS satırları ve **animatikteki TTS** son filmle aynı tınıda çıkar. Animatik seyircisinin duyduğu sesin rengi son filmde değişmez.

Hangi yol seçilirse seçilsin kurgunun koşulları şunlardır:
1. Her replik ayrı dosyadır ve kelime zamanları bilinir (`diyalog.json` v2). J/L, ekran dışı replik ve altyazı bunsuz yapılamaz.
2. Görünen konuşanın sesi klip zamanına bağlıdır (senkron kuralı).
3. Klipte kaynağı olmayan ekran dışı replik için aynı hedef sesle TTS kullanılır (ses tanıtım kuralına uyarak).
4. Altyazı **duyulan** metinden yapılır (`altyazi_metin`; [SM] §5.4).
5. Her kurgu değişikliğinden sonra dudak denetimi çalışır (BK §5.1.9).

#### 4.8.4 Karar 1, 5 ve 6
- **Karar 1 (yalnız konu sorulur):** Kurguda yaratıcı soru sorulmaz. Kullanıcıya giden her mesaj bilgidir: "taslak hazır", "X kredi gerekiyor", "Flow uyarı verdi, durdum". Kullanıcının elinin değmesi gereken yerler yalnız fiziksel işlerdir: kredi yüklemek, Flow girişi/doğrulaması, CapCut'ı kapatmak (yama için), dışa aktarmak (KR'deki karar; `yayin_kaynagi: master` seçilirse bu da kalkar). Onay noktaları yalnız `--onayli` modda devreye girer. [CM] `soru_kapisi` kancası kurgu mesajlarında da geçerlidir.
- **Karar 5 (Memmet seri üretim aracı değil):** Yeniden çekim kuyruğu küçük listelerle Memmet'e gider. Tempo kuralları aynıdır (BK §6.2.6); kullanıcı başındaysa `--mod elle` kullanılır. Uyarıda kuyruk `flow_durdu` olur; yeniden deneme yapılmaz, atlatma hiç yapılmaz. Kurgu Flow'u hızlandıran hiçbir şey önermez. Zincir dalgaları gönderimi seyrekleştirir. 0 kredi kuralı gönderim sayısını azaltır.
- **Karar 6 (kaliteden ödün yok):**
  - Bütçe yetmediğinde model, çözünürlük ya da plan sayısı düşürülmez; hat bekler (H/proje-b2). Yazılmış film bütçe için kısaltılmaz ([SN2] §2.5).
  - Seyirci her turda bütün filmi izler; tasarruf için yalnız değişen partiler izletilmez (KR8).
  - Yer tutucu ve dijital yakınlaştırma sınırlıdır (§4.5.5).
  - 3 turda (ve kurtarmada) geçemeyen film "geçti" diye sunulmaz; eksikleri yazılı olarak verilir.

---

### 4.9 Riskler, kalan çakışmalar, açık sorular

#### 4.9.1 Riskler ve önlemler

| # | Risk | Önlem |
|---|---|---|
| R1 | **Kare paketi izlemek değildir.** Seyirci hareketi görmez, sesi duymaz; ritim ve duygu puanı gerçek izleyiciden sapabilir. Tutma verisi de yok (BK §1.8.5) | Ses ve hareket kuralları makinede (Z3, senkron, B9, [SM] S3–S7). Duyulanlar pakete işitsel döküm olarak, kurguda son miksten girer. Kullanıcı notları ve yayın sonrası veriler ders defterinde puanlarla karşılaştırılır |
| R2 | **Animatik ≠ son film.** Veo zamanlaması plandan sapar; animatikten geçen sahne kurguda düşebilir | T1↔T2 sapma raporu, geri gidiş yasağı, kurgu izleme turu, P1 kurgu ön turu |
| R3 | **Seyirci maliyeti ve kullanım sınırı.** Tam izleme: seyirci başına ≈ 0,2 M token (§4.5.4; tahmin) → tur başına ≈ 0,6 M + ilk 2 dk ve eşleştirici. En kötü durumda (3 + 2 animatik, 3 + 2 kurgu turu, 2 ön tur) ≈ 6–7 M token (tahmin). EMBERFALL'da kullanım sınırı dolmuştu (YR §1) | Görev defteri ve dosya tabanlı devam ([CM]); yarım seyirci sıfırdan; başsız modda [UM]'nin Batches yolu (%50). Kesin karar 6 gereği seyirci sayısı ve tam izleme kısılmaz |
| R4 | **Tek seyirci örneğinin bağlamı.** Bütün film ≈ 0,2 M token; Opus 5.5 bağlamı 1M (CA), ama Claude Code alt ajanının bağlam sınırı ve otomatik sıkıştırma davranışı doğrulanmadı | İlk filmden önce `count_tokens` ile paket ölçülür ve tek bir sahte uzun izleme çalıştırılır (açık soru 5). Sıkıştırma olursa o seyirci görevi geçersiz sayılır ve sayfa yoğunluğu değil parça sayısı ayarlanır |
| R5 | **Kamera hareketli klipte hareket başlangıcı yanlış bulunur** (push-in ilk kareden enerji üretir) | Özne kutusunda ölçüm; olmazsa planlanan zaman + düşük güven → kurgucu |
| R6 | **Senkron kuralının kalitesi ses ayrıştırmaya bağlı** (demucs/RoFormer artığı, AR3 A3) | Ses uzmanının alanı; kurgu yalnız yerleşimi garanti eder |
| R7 | **Zincir dalgaları süreyi uzatır**; yeniden çekimde zincir zinciri tetikler | Derinlik ≤ 2; kuyruk zincir maliyetini önceden gösterir; örtü planları zinciri kısa tutar |
| R8 | **CapCut uyumluluğu:** pycapcut 0.0.3'te hız, ayna, ses sönümü ve seviye anahtar karesi doğrulanmadı; mevcut taslağı okuyup klonda segment taşıma yeteneği doğrulanmadı; yeni CapCut taslağı şifreleyebilir | Desteklenmeyen özellik önizlemede ffmpeg ile yapılır, taslakta yaklaşık hâli kurulur ve NOTLAR'a yazılır. Yama için önce kurgu köprüsünün `clone_project` kodu denenir; çalışmazsa yedek yol "yeni adla kur"dur. İlk kullanımda gerçek CapCut'ta 1 dakikalık deneme taslağı açılır |
| R9 | **Otomatik araç kullanıcı kararını ezebilir** | `kaynak: kullanici` kilidi; kaynak taslağa hiç yazılmaz; yama klonda; test 12–13 |
| R10 | **Bütçe tahmini zayıf.** ZN'deki 405 klip türetilmiş bir değer; B2'de yeniden çekim ≈ %37 | Animatik ve kâğıt kapılarıyla oranın düşmesi beklenir (tahmin). Dilimler ve 0 kredi kuralı; her kredili adımdan önce `URETIM_ONIZLEME`. Kredi yetmezse hat bekler |
| R11 | **İşlemci render süresi.** 40 dk'lık önizleme her turda yeniden render edilir | Plan başına önbellek; parti başına render. Tam render süresi bilinmiyor (tahmin 15–40 dk); ilk filmde ölçülür. 4K yayın render'ı yalnız `yayin_kaynagi: master`'da |
| R12 | **Ad maskeleme sezgisi kaçırabilir** ("Father", unvan, takma ad) | `maske.takma_adlar`; testler; seyirci raporunda `adi_nereden` alanı |
| R13 | **Durağan kare animatiği yavaş hissettirir**; ritim puanı aşağı yanlı çıkabilir | Seyirci kip metninde not; T1 ve T2 ritim puanları ders defterinde karşılaştırılır; gerekirse T1 ritim eşiği kalibre edilir |
| R14 | **Kesme mekanik olarak temiz ama duygusal olarak zararlı olabilir** (bir `duygu_tutma` planını kesmek) | Z2 (#35–39) simülasyona dahil; kesme sonrası turda seyirci duyguyu yeniden puanlar |
| R15 | **API modunda anahtar güvenliği** | Anahtar yalnız ortam değişkeninde ya da `AYARLAR/`'da; loglanmaz; `paketle.py` sızıntı taraması (BK §6.5) |
| R16 | **(yeni) Uzun izlemede konum yanlılığı:** sonraki parçalar sistematik olarak düşük puan alabilir (AR1 C, LongStoryEval) | Parça puanları ve `parca_konum_yanliligi` eğimi; iki filmde doğrulanırsa parça arası "ara" talimatı ya da parti başına ayrı örnek denenir (ölçüyle karar) |
| R17 | **(yeni) Dondurma kurgunun sıra seçeneğini daraltır** | Kabul edilen bedel; örtü, J/L ve köprü replik daha çok kullanılır |
| R18 | **(yeni) Ön turlar maliyet ekler, değeri belirsiz** | Değeri ders defteriyle ölçülür; iki filmde yoksa kaldırılır |
| R19 | **(yeni) Pencereli korelasyon yanlış red verebilir** (CapCut AAC kodlaması, kullanıcının sesle oynaması) | Kullanıcı ses düzenlemesi varsa `dogrusal_kazanc` yolu; eşikler ilk filmde ölçülür |

#### 4.9.2 Kalan çakışmalar (ekip kararı gereken)
1. **Kare zinciri varsayılanı:** [UM] C5 hâlâ `bitis_karesi` diyor; [YN2], [GS] ve ben Z1 diyoruz (§4.8.2 d'de kurgu gerekçesi). [UM]'nin görüşü gerekli; dalga süresi [UM]'nin 13 saatlik hesabına eklenmeli.
2. **Yayın kaynağı:** [UM] C9 ffmpeg ana kaydı; KR satır 48 CapCut dışa aktarımı. Önerim: varsayılan KR, `yayin_kaynagi: master` kurulum ayarı (İ-2).
3. **"Aynı projede" ↔ klon:** [CM] `film-not` kullanıcının aynı projede görmesini istiyor; ben kaynağa yazmayıp klonluyorum (§4.5.7). Kullanıcının deneyimindeki tek fark proje adıdır. Ekip kabul etmezse kaynağa yazma ancak yedekleme + öz denetim + şifre kontrolüyle ve pycapcut'ın yetenekleri doğrulandıktan sonra düşünülebilir.
4. **S3.6 ve S3.8'in kurguya taşınması** (İ-9): [SM]'nin kabulü gerekli.
5. **Yeniden çekim dilimleri** (İ-3): [UM], [GS] ve [SM]'nin onayı gerekli; sayılar tahmin.
6. **Kesme oranının paydası** (İ-6): RE açıklaması ve [SN2] H11 için senaristin onayı gerekli.
7. **`ozet-eslestirici` `bulgu` kipi** (İ-5): [SN2]'nin bulgu yönlendirme betiği bu eşlemeyi girdi olarak almalı.
8. **Kuyruk dosyasının yeri** (`KUYRUK/` mı film kökü mü) ve rapor klasörü (`_RAPOR/` mı `RAPORLAR/` mı): orkestratör sahiplerinin ([UM], [CM]) tek kararı. Ben `_RAPOR/` ve `KUYRUK/` yazdım.

#### 4.9.3 Açık sorular
1. **Kurgu turu sınırı sonrası:** RE `kurgu_tur_max = 3`'ten sonra koşullu 2 ek tur (GENEL ≥ 0,5 arttıysa) kabul mü? (tahmin; ekip kararı)
2. **CapCut şifrelemesi:** Kullanıcının CapCut sürümü taslakları şifreliyor mu? Şifreliyorsa `taslak_fark`, `notlari_oku` ve yama çalışmaz. Kullanıcının bilgisayarında bir kez denenmeli.
3. **pycapcut 0.0.3 yetenekleri:** hız, ayna, ses sönümü, seviye anahtar karesi; mevcut taslağı okuma ve klonda segment taşıma. Gerçek taslakta doğrulanmalı.
4. **Flow klibinin durağan başlangıcı** gerçekte kaç saniye (ZN §2.2: 0,3–1,0)? İlk 20 klipte ölçülüp `kullanim_bas_varsayilan_sn` ve örtü formülü kalibre edilmeli.
5. **Claude Code alt ajanının bağlamı:** Bir seyirci örneği ≈ 0,2 M token'lık paketi (≈ 83 sayfa) tek oturumda okuyabiliyor mu, otomatik sıkıştırma tetikleniyor mu? Sayfa başına görüntü tokeni `count_tokens` ile ölçülmeli.
6. **API modu:** Kullanıcının Anthropic API anahtarı var mı? Yoksa yalnız ajan modu (abonelik) kullanılır.
7. **Animatikte müzik:** [SM] B2 müziği animatikten önce hazır olacak mı? Olmayacaksa ZN #40 ve müzik giriş/çıkış kuralları T2'ye kalır.
8. **Plan numaraları seyirciye görünsün mü?** Kopukluğu plana bağlamak için gerekli; yanlılık riskini düşük görüyorum. Alternatif: yalnız zaman kodu verilir, makine plana çevirir.
9. **Kodlayıcı:** Kullanıcının ffmpeg'i NVENC (RTX 3050 Ti) destekliyor mu? 4K yayın render'ının süresi buna bağlı.
10. **Dışa aktarım çözünürlüğü:** 720p kaynaktan 4K dışa aktarım (BK §8 #8) kalite getirir mi, yoksa 1080p yeter mi? Yayın uzmanıyla birlikte; karar KR'de kayıtlı (4K).
11. **Ön turlar:** P1 animatik ve P1 kurgu ön turları ilk iki filmde ölçülecek değeri gösterecek mi? Göstermezse kaldırılır.

#### 4.9.4 Belgelere önerdiğim düzeltmeler
- **ZN §6.2** "`RAPORLAR/<kapi>_<parti>.json`" → "`_RAPOR/`" (mevcut kod ve çoğunluk; orkestratör kararıyla kesinleşir).
- **ZN §7.3 girdi listesi:** "`ekranda_bilgi`" ve "önceki filmlerin izleyici özeti" çıkarılır ([SN2] İ2, [CM] Ç-2). Kurgu aşamasının kare paketi tarifi §4.5.4 biçimiyle güncellenir. Kesme turu cümlesine "simülasyondan HATA'sız geçen önerilerin" eklenir (İ-6).
- **ZN §2.6:** "Bütçe yetmezse … film kısaltılır" → "Bütçe yetmezse süre hikâye yazılmadan önce seçilir; yazılmış film kısaltılmaz" ([SN2] §2.5; [KU1] D1).
- **ZN §5.1:** ambiyans kaynağı "demucs ile ayrılmış Flow ortamı" çıkarılır; yatak yalnız gerçek kayıttan ([SM] §9.2).
- **ZN §3.7:** "takes two slow steps" → "walks two slow steps" ([YN1]).
- **RE `kesme_turu_oneri.aciklama`:** payda tanımı (İ-6).
- **BK §5.3.3'e uygulama notu** (kuralın kendisi kullanıcınındır, değişmez): "Taslak yeniden kurulmaz" şöyle uygulanır: kullanıcının taslağı temel alınır, kaynak taslağa yazılmaz, klonda yalnız sistemin kanalları yamanır, yeni medya yeni dosya adıyla bağlanır (§4.5.7). Bu not ekip onayıyla eklenir (§4.9.2 madde 3).

---
*Bu belge kurgucu uzmanının 2. tur önerisidir. Tur 1 dosyamın yerine §4 geçer. (tahmin) işaretli sayılar §4.7.3'teki kalibrasyon kuralıyla ilk iki filmde ayarlanacaktır.*
