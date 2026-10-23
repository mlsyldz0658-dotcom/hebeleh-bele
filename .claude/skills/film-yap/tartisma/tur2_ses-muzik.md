# Tur 2 — Ses ve Müzik Uzmanı: itirazlar, çakışmalar, revize nihai öneri

Hazırlayan: ses-muzik uzmanı (Claude Opus 5.5). Tarih: 23.10.2026.
Bu turda okunanlar: `tartisma/` altındaki yedi tur 1 dosyasının **tamamı** (kendi dosyam dahil), o sırada klasörde bulunan iki tur 2 dosyası
(`tur2_senarist.md`, `tur2_yonetmen.md`; alan adlarını onlarla uzlaştırmak için), `ZANAAT.md` §0, §2, §5, §6.1, `ritim_esikleri.json`
(ses anahtarları betikle listelendi), `BILGI_KURALLARI.md` §4.2, §4.5, §5, §6.4, §8, `03_DERSLER.md` "Ses" bölümü, `arastirma/03` (A ve öneriler),
`FILMLE ILGILI CLAUDE/02_ARACLAR.md`, `07_OPENMONTAGE_VE_EK_ARACLAR.md` ve mevcut kod (`seslendir.py`, `capcut_film.py`, `film.py`, `ai84.py`,
`izleme_paketi.py`, `saglayicilar/__init__.py`).

**Uzman kısaltmaları:** `[YÖN]` = `tur1_yonetmen.md` · `[SEN]` = `tur1_senarist.md` · `[KUR]` = `tur1_kurgucu.md` · `[GÖR]` = `tur1_goruntu-sureklilik.md` ·
`[ÜRE]` = `tur1_uretim-muhendisi.md` · `[MİM]` = `tur1_claude-code-mimari.md` · `[SM1]` = benim tur 1 dosyam (`tur1_ses-muzik.md`) ·
`[YÖN2]` = `tur2_yonetmen.md` · `[SEN2]` = `tur2_senarist.md`.
**Kaynak kısaltmaları:** `Z` ZANAAT.md · `RE:<anahtar>` ritim_esikleri.json · `BK` BILGI_KURALLARI.md · `A1/A2/A3` arastirma/01–03 · `D` 03_DERSLER.md ·
`H/<ad>` HAFIZA_YEDEGI notu · `AR` 02_ARACLAR.md.
**Bu turda açılıp doğrulanan dış kaynaklar** (23.10.2026, `raw.githubusercontent.com` üzerinden indirildi ve okundu):
- `[D-MT]` MuseTalk README (`TMElyralab/MuseTalk`): "tested … on an NVIDIA GeForce RTX 3050 Ti Laptop GPU with 4GB VRAM. In fp16 mode, generating an 8-second
  video takes approximately 5 minutes"; Python 3.10 + torch 2.0.1 önerilir; kod MIT, model "available for any purpose, even commercially".
- `[D-AS]` ACE-Step 1.5 README: lisans MIT; "runs locally with less than 4GB of VRAM"; ≤ 6 GB katmanı = 2B turbo, LM kapalı, INT8 + tam CPU offload;
  **Python 3.11–3.12** ister; 2B modellerde "Refer audio" ve "Cover" var; BPM, ton/mod, ölçü denetimi ve sesten BPM/ton çıkarma ("Audio Understanding") var.
- `[D-RVC]` RVC WebUI README ve LICENSE: MIT; ön eğitim VCTK (≈ 50 saat); güncel dal **Python 3.12**; "fast training, even on poor graphics cards".
- `[D-EL]` ElevenLabs Python SDK `reference.md`: `voices.get_shared` süzgeçleri `gender, age, accent, language, locale, search, use_cases, descriptives,
  featured, min_notice_period_days, sort`; TTS'te `seed`, `previous_text`, `next_text`, `pronunciation_dictionary_locators`; ayrıca `text_to_voice.design`
  (ses tasarımı), `pronunciation_dictionaries`, `music.compose` var. **Bunların AI84 üzerinden geçip geçmediği bilinmiyor** (§4.9 açık soru).
- `[D-FF]` FFmpeg `doc/filters.texi`, `loudnorm` → `linear`: "If any of these conditions aren't met, normalization mode will revert to dynamic."

**Sayı etiketleri:** kaynağı olan sayının yanında kaynağı yazar · **(hesap)** kaynaktaki sayılardan türetildi · **(tahmin)** kaynağı yok, ilk filmde ölçülüp
ayarlanacak · **(bellekten)** bildiğim ama bu oturumda açılıp doğrulanmayan bilgi · **[arama]** A3'teki doğrulanmamış arama bilgisi.

**Değişmeyen kısıt:** Claude ses DUYAMAZ. Bu alandaki her yargı ölçümle ya da ölçümün yazıya dökülmüş hâliyle verilir.

### Bu turun özü (6 satır)
1. **Ses/dudak ana yolu değişmedi, kanıtı güçlendi:** Veo konuşur, ses yerelde karakterin evren sesine dönüştürülür. Yeni bulgu: MuseTalk 1.5 kullanıcının
   kartıyla **aynı kartta** (RTX 3050 Ti 4 GB) denenmiş [D-MT]. Yani TTS + dudak senkronu yedeği dolar değil **zaman** ister (≈ 5 dk / 8 sn klip).
2. **En önemli üç itirazım:** (★1) kurgu planında ikinci bir ses yazarı ve ikinci bir miks kodu; (★2) animatikte "taslak/geçici" ses;
   (★3) Veo ses dizesinde aksan yok. Dönüştürücü tınıyı değiştirir, aksanı ve vurguyu Veo'dan taşır (bellekten); dizede aksan yoksa iki yol farklı aksanla konuşur.
3. **Ajan sayısını dörtten bire indiriyorum:** `ses-tasarimcisi` (kipler: `kadro`, `tasarim`, `muzik`). `ses-denetcisi` kalkar; yerine deterministik
   **ses merdiveni** (`ses_karar.py`) gelir. Replik metnine dokunan tek yargı ("Veo'nun söylediği kabul mü?") metnin sahibine, `hikaye-yazari`'na gider.
4. **Alan adları ekiple uzlaştı:** `zanaat.ses` (sahibi ses), `zanaat.ekran_disi_ses` (yönetmen), `_derlenir.{agiz_gorunur, dinleyen_agiz, seviye, ton_fiili_en}`
   (kod), `replik.teslim` (senarist), `replik.veo_metin` (ses), efekt ↔ adım bağı `adim: "a1"`. Ses kimliği `EVREN/<SERI>/karakterler/<id>/ses.json`.
5. **Metin kapısı videonun içine taşındı:** Veo konuşmadıysa, adı yanlış okuduysa ya da `tasidigi` öğesi eksikse bu, kurguda değil **indirildiği anda**
   bulunur ve aynı dalgada yeniden çekime girer ([MİM] A14).
6. **Müzik:** leitmotif notaları ajan tarafından yazılır (MIDI). MIDI CC0/MIT örneklerle çalınır. ACE-Step 1.5 bu motifi "Cover/Refer audio" ile orkestralar [D-AS].
   Sağlayıcı zincirinde elle iş isteyen `gemini_elle` yoktur.

---

## 1. Diğer önerilere itirazlarım (dosya + madde + neden + önerim)

★ işaretli üç madde en önemli itirazlarımdır.

### ★ İ-1 · [KUR] §5.1 `KURGU_PLANI.json` → `ambiyans[]`, `efektler[]`, `muzik[]`; §6.1 `kurgu_render.py` ses bölümü; §9.2-4 "Z3 #44–47 ölçümü bende"
- **Ne yazılmış:**
  - Kurgu planı ses katmanlarını da taşıyor: sahne zemini, efekt ve müzik girdileri kurgu planının içinde.
  - `kurgu_render.py` dört katmanı kendisi kuruyor: "Son karışım ffmpeg `loudnorm` çift geçişle −14 LUFS / −1 dBTP'ye çekilir."
  - Z3 #44–47 (replik seviyesi, ambiyans, müzik altı, final) ölçümünü `kurgu_denetim.py` yapsın deniyor; düzeltmeyi ses yapsın.
- **Neden yanlış:**
  1. **İki yazar, bir dosya.** Ambiyans, efekt ve müzik yerleşimini ses araçları (`ses_katmani.py`, `muzik.py`) hesaplıyor. Kurgu planına da yazılırsa aynı olgu iki yerde
     tutulur ([YÖN] §5.2, [MİM] §2.2 "tek yazar"). Erişim kancası da ([MİM] K-3) bu dosyada iki sahibi ayıramaz.
  2. **İki miks kodu, iki sonuç.** Animatik ve önizleme bir kodla, son miks başka bir kodla yapılırsa S4–S7 kapılarının ölçtüğü ile seyircinin "duyduğu"
     (işitsel döküm) farklı sese dayanır. Kurgucunun kendi "geri gidiş yasağı" (T1'de geçen ölçü T2'de HATA olamaz) bu farkla anlamsızlaşır.
  3. **`loudnorm` doğrusal kalmayabilir.** FFmpeg belgesi açıkça yazıyor: hedef LRA kaynaktan düşükse ya da kazanç gerçek tepeyi aşırıyorsa
     `linear` mod **dinamik moda döner** [D-FF]. Dinamik mod sıkıştırma yapar; diyalog ile müzik arasındaki ≥ 12 dB farkı (RE:muzik_diyalog_alti_min_db)
     ve fısıltı ile bağırma arasındaki 7 dB'lik planlı farkı (RE:diyalog_lufs) bozabilir. Bunu kimse fark etmez, çünkü sonuç yine −14 LUFS ölçülür.
  4. **Aynı ölçünün iki kodu.** Kurgucu tur 1'de kendisi de "aynı ölçünün iki ayrı kodla hesaplanmasına izin verilmemeli" diyor ([KUR] §9.2-2).
- **Önerim:**
  - `KURGU_PLANI.json` görüntü kurgusunun tek kaynağı kalır: `planlar`, `kartlar` ve senkron kuralıyla hesaplanan `diyalog[]` yerleşimi ([KUR] §5.1 formülü aynen).
    `diyalog[]` metin ve ölçü **taşımaz**; replik kimliğiyle `SESLER/diyalog.json`'a başvurur.
  - Ses katmanlarının zaman çizelgesi ayrı bir dosyadadır: **`KURGU/SES_CIZELGESI.json`** (sahibi ses araçları). Dosya hangi kurgu planı sürümünden
    üretildiğini imzasıyla yazar. Kurgu planı değişince yalnız etkilenen sahneler yeniden üretilir.
  - **Tek miks kütüphanesi `son_miks.py`.** Animatik, önizleme, son miks ve Shorts aynı işlevi çağırır. `kurgu_render.py` sesi kendisi karıştırmaz.
    Yöntem: ölçülmüş **tek doğrusal kazanç** + 4× aşırı örneklemeli gerçek tepe sınırlayıcı + yeniden ölçüm (§4.6). `loudnorm` yalnız ölçüm için kullanılır.
  - **Ses ölçüleri tek yerde:** `olcum/ses.py` (görüntü uzmanının `olcum/` paketine eklenir, aynı `sahte` arka uçla). S4–S7 raporlarını ses araçları yazar.
    `kurgu_denetim.py` bu raporları **okur** ve Z3 özetine koyar; aynı ölçüyü yeniden hesaplamaz.

### ★ İ-2 · [ÜRE] §2.2 V07 ve §8.3-a ("animatikte taslak TTS"), §9.2 C7 ("sessiz animatik de savunulabilir"); [MİM] §2.1 A12 ("geçici ses"); [KUR] K1 ("onay … sorusuyla")
- **Neden yanlış:**
  1. Animatiğin varlık nedeni **gerçek süreleri** video kredisinden önce ölçmektir (kesin karar 3a). Replik süresi sese bağlıdır: yavaş ve boğuk bir ses aynı repliği hızlı
     bir sesten belirgin biçimde uzun söyler (tahmin; ölçüsü S2.13'te). "Taslak" ya da "geçici" sesle ölçülen süre, son sesin süresi değildir.
     Kurgucunun T1 → T2 sapma raporu bu yüzden boşuna büyür.
  2. Ağzı görünmeyen repliklerde (ekran dışı, sırt dönük, köprü replik) animatikteki TTS **son sestir** (Yol B). Taslak sesle üretilirse ikinci kez ücretlenir.
  3. Seyirciye giden işitsel döküm ("ekran dışı: daha önce duyduğun boğuk erkek sesi") **seçilmiş seslerin ölçülen benzerliğinden** üretilir (İ-9).
     Taslak sesle "kim konuştu belli değil" kopukluğu ölçülemez.
  4. Sessiz animatik, J/L kesmeyi, ekran dışı repliği, ambiyans köprüsünü ve müzik giriş-çıkışını ("kopuk" hissinin ses araçları, Z §0, §5.5) hiç sınamaz.
  5. [KUR] K1'deki "onay sorusu" kesin karar 1 ile çelişir. AI84 harcaması bütçe kapısıyla açılır, soruyla değil.
- **Önerim:**
  - **Ses kadrosu animatikten önce biter** (§4.2 SB1–SB2). Animatikte her replik seçilmiş son sesle, önbellekli olarak okunur. Aynı metin ikinci kez ücretlenmez.
  - Animatik müziği gerçek ipucu müziğidir (ACE-Step ya da MIDI). Yalnız üretim başarısız olursa `GECICI` işaretli yedek çalar ve S6 maddeleri o ipucunda BAYRAK olur.
  - AI84 harcaması `FILM_AYAR.json → butce` sınırıyla kendiliğinden açılır. Kullanıcıya soru sorulmaz.

### ★ İ-3 · [YÖN2] §4.5.11 `konusur` şablonu ve §4.8.3 örneği · [SEN2] §2.1 ve §4.8.4-3 ("Veo dizesi ≤ 10 kelime, yaş yok") · [SM1] S0.4–S0.5 (öz eleştiri)
- **Ne yazılmış:** Konuşan klipte istem kalıbı `Mara says coldly, in a low, warm, slightly husky female voice: "…"`. Dizenin şartı yalnız "≤ 10 kelime, yaş sözcüğü yok".
  Benim tur 1 örneğim de aynıydı ve **aksan içermiyordu**.
- **Neden eksik:**
  1. Ses dönüştürücüler (RVC, OpenVoice) konuşanın **tınısını** değiştirir. Söz içeriğini, vurguyu, ritmi ve **aksanı** kaynak sesten taşır (bellekten; kıyasta ölçülecek, §4.2 SB3).
     Yol A'da aksanı Veo belirler, Yol B'de seçilen ElevenLabs sesi belirler.
  2. Dizede aksan yoksa Veo her klipte aksanı yeniden seçer. Aynı karakter bir planda İngiliz, bir sonrakinde Amerikan aksanıyla konuşabilir. Seyirci bunu "sesi değişti" diye
     duyar. Bu, kullanıcının yaşadığı sorunun (A3 A2) dönüştürmeden sonra da kalan parçasıdır.
  3. Aksan yalnız tını benzerliğiyle (S2.9) ölçülmez. Konuşmacı gömmesi aksan değişse de yüksek kalabilir (tahmin).
- **Önerim:**
  - Karakterin ses profilinde `aksan`, **seçilen sesin ElevenLabs `accent` etiketiyle aynı** olmak zorundadır. Bu süzgeç paylaşılan ses aramasında var [D-EL].
    Kadro seçimi de bu süzgeçle yapılır (S1.7).
  - `veo_ses_tarifi` sabit sırayla dört öğe taşır: **perde/tını + cinsiyet + aksan** (+ isteğe bağlı tempo). Örnek: `in a low, husky female voice with a northern English accent`
    (12 kelime). Sınır 10'dan **12 kelimeye** çıkar (tahmin). Hareket istemi bütçesi Y46 (≤ 75 kelime, [YÖN2]) içinde kalır.
  - Ölçüm: S1.7 (seçimde aksan etiketi), S2.16 (videoda aksan tutarlılığı, BAYRAK). Aksan sınıflayıcısı lisansı netleşene kadar bu ölçüyü isteğe bağlı
    `dinleyici` sağlayıcısı (ses girdisi kabul eden bir model) yapar. O yoksa madde "ölçülemedi" olur ve ilk filmde elle dinleme notlarıyla ders defterine girer (§4.9).
  - Konuşan figüranlarda da aynı kural geçerlidir. Bölge ya da halk aynıysa aksan ailesi aynıdır (dünya kuralı, [SEN2] evren `hikaye.json`).

### İ-4 · [ÜRE] §8.4 otomatik karar ağacı ("WER aşılırsa bir yeniden çekim, sonra `tts_dudak`") ve §5.6 `KAYIT` (`dudak: musetalk (bulut ya da Colab) · fal_latentsync`)
- **Neden yanlış ya da eksik:**
  1. Ağaç yalnız metin hatasını görüyor. Dönüşüm kalitesi düşükse (metalik ses, fısıltı), ağız kurguda zaten görünmüyorsa ya da Veo'nun sapması anlamı bozmuyorsa
     **0 kredili** çözümler var: kabul (metnin sahibi onaylarsa), Yol B'ye geçiş, L taşmasıyla ekran dışı. Bunlar atlanıp doğrudan kredi harcanıyor.
  2. `musetalk` "bulut ya da Colab" yazılmış. Oysa MuseTalk README kullanıcının kartıyla aynı kartta, 4 GB'ta, fp16'da 8 sn'lik videonun ≈ 5 dk'da üretildiğini söylüyor [D-MT].
     Yedek yol **yerel ve 0 dolardır**. Bedeli zamandır.
  3. `fal_latentsync`: LatentSync yüz tespiti için InsightFace kullanıyor. InsightFace modelleri ticari olmayan araştırma içindir (A3 A1). Barındırılan bir servisin bunu nasıl
     çözdüğü bilinmiyor. YouTube'da para kazanan bir kanal için lisans riski var.
  4. "Kredi maliyeti yoktur" cümlesi tur 1'deki bilgiyle yanlıştı (bulut dudak senkronu dolar ister). Yeni bilgiyle (yerel MuseTalk) **doğru** hâle geliyor (§3'te kabul).
- **Önerim:**
  - Karar ağacı yerine **hata türüne göre ses merdiveni** (§4.8.3, `ses_karar.py`). Kaliteyi düşürmeyen 0 kredili basamaklar önce denenir.
    Flow kredisi harcayan tek basamak yeniden çekimdir (en çok 2 deneme; normal kuyruk ve bütçe kapısı). `ai84_vc` AI84 kredisi harcar ve tavanlıdır.
    Kalite önceliği (kesin karar 6) şunu getirir: metin hatasında önce yeniden çekim, sonra yerel dudak senkronu.
  - `KAYIT` → `dudak: ["musetalk", "sahte"]` (yerel, ayrı sanal ortam). `fal_latentsync` **çıkarılır**. Ücretli sync.so yalnız `usd` bütçesi > 0 ise ve ticari kullanım
    koşulları okunduktan sonra eklenebilir (P2).
  - Dudak senkronu çıkan her klip görüntü uzmanının V2 kimlik denetiminden **yeniden geçer** ([GÖR] §8.9). Ağız bölgesi yeniden üretildiği için bu şarttır (S2.15).

### İ-5 · [MİM] §3.2 ve §8 Karar 4 madde 2 (`ses.yontem` alanını A08'de `ses-tasarimcisi` yazar) · [SEN2] §2.3 (`ses-kadrocusu`, `ses-denetcisi` beklentisi)
- **Neden:**
  1. Yol (Veo + dönüştürme mi, TTS mi) **ağzın görünüp görünmediğinden** çıkar. Ağız görünürlüğü kadraj, yüz açısı ve ekran dışı sesten kodla hesaplanır
     (`_derlenir.agiz_gorunur`, [YÖN2] İ-9). Ajanın serbestçe yazdığı yol ikinci bir kopya olur ve geometriyle çelişebilir.
  2. [SEN2] iki ses ajanı varsayıyor. [MİM] tek ajan öneriyor. Benim tur 1'imde dört ajan vardı. Mimari ölçütüne göre ([MİM] Ç-10) yeni ajan yalnız ayrı bir dosyanın
     sahibi ya da ayrı kör girdili değerlendirici olduğunda açılır. Ses kadrosu, ses tasarımı ve müzik aynı rolün üç işidir. Ses denetimi ise ölçüm ve tablo işidir.
- **Önerim:**
  - Tek ajan `ses-tasarimcisi`, üç kip: `kadro`, `tasarim`, `muzik`. Her kip ayrı görev ve yeni örnektir. Revizyonu aynı kipin aynı örneği yapar (§4.3).
  - `zanaat.ses.diyalog.yol` **kodla** önerilir (`ses_plani.py --taslak`). Ajan yalnız `yol_neden` yazarak değiştirebilir. Gerekçesiz değişiklik S0.1 HATA'sıdır.
  - Çalışma sırasında yol değişirse (yedek yola düşme) bu bilgi `SAHNELER.json`'a değil `SESLER/diyalog.json → replikler.<id>.yol_gercek` alanına yazılır.
  - `ses-denetcisi` kalkar. HATA → eylem eşlemesi deterministik **ses merdiveni**dir (`ses_karar.py`). Metne dokunan tek gri karar ("Veo'nun söylediği kabul mü?")
    metnin sahibi `hikaye-yazari`'nın yeni bir kipine (`replik_kabul`) gider (§2.4).

### İ-6 · [ÜRE] §5.10 `ai84_kredi_tavan_film: 60000`, `"muzik": ["acestep", "gemini_elle"]`; §7.1 `fiyat.ai84.vc ≈ 2.000 kredi/sn`; §2.2 V04 "2 aday"
- **Neden:**
  1. Tavan sürekli harcamayı (animatik TTS ≈ 13–16 bin, değişiklikler, seçim) karşılar. Ama serinin başında **bir kez** gereken ses bankası (RVC kazanırsa ana karakter başına
     ≈ 9 bin, hesap §4.8.3) aynı tavana girerse ilk film tavanı aşar ve hat sebepsiz durur.
  2. `gemini_elle` müzik sağlayıcısı kullanıcıya elle iş çıkarır. [ÜRE]'nin kendi M2 listesinde (kaçınılmaz 4 el işi) bu iş yok. Kesin karar 1 ile de çelişir.
  3. Voice Changer fiyatı tahmin. Oysa `ai84.py`'de ücretsiz bir `estimate()` çağrısı var (`/v1/estimate-credit-cost`). Tahmin ölçüyle değiştirilebilir.
  4. "2 aday, karakterin kendi repliğiyle" (BK 5.1.7) kullanıcı seçimine göre yazılmıştı. Kullanıcı seçmediği için seçim ölçüye dayanır. Ölçü için ücretsiz önizlemelerle ön eleme
     ve 4 adaylık okuma gerekir (§4.2 SB2).
- **Önerim:**
  - `butce.ai84_kredi_tavan_film: 60000` kalır. Yeni anahtar `butce.ai84_seri_kurulum_tavan: 40000` eklenir (ses bankası, seri başına bir kez, tahmin).
  - Müzik zinciri: `["acestep", "midi_ornek", "sahte"]`. `midi_ornek` her zaman çalışan, lisansı temiz yedektir (§4.8.4).
  - Kurulumda (`SB0`) `ai84.estimate(...)` bir kez çağrılır. Gerçek birim fiyat `FILM_AYAR.json → fiyat_olcum`'a yazılır (anahtar içermez).

### İ-7 · [GÖR] §7.5 V1 "replik penceresinde `silencedetect=n=-50dB:d=1.0` → B" · [MİM] §2.1 A14 "her indirmede … metin kapısı"
- **Kabul:** Metin kapısının **indirme anında** çalışması doğru. Konuşma yoksa ya da ad yanlışsa yeniden çekim aynı dalgaya girer, kurgu beklenmez.
- **İtiraz:** `silencedetect` konuşmanın kanıtı değildir. Veo klibinde rüzgâr, ateş ya da adım sesi −50 dB'in üstündedir; ortada hiç söz olmadan sessizlik bulunmaz.
  Hata sessizce "geçti" olur.
- **Önerim:** V1'deki madde kalabilir (ucuz ön işaret). Asıl karar S2.1'dedir: ayrıştırılmış konuşma kanalında VAD + ASR, replik penceresi ±1 sn içinde
  (pencere RE değil, [KUR] `whisper_pencere_pay_sn` önerisi, tahmin). Aynı geçişte S2.2–S2.5 de çalışır (§4.2 SC1).

### İ-8 · [GÖR] §5.3 `mekan.json → "ambiyans": "IC_ODA_AHSAP"` · [ÜRE] §5.9 `kimlik.json → "ses": {...}` ve `mekanlar/<id>/ambiyans.wav` · [KUR] §8.8 (ses profili ve mekân zemini "kurgu varlığı")
- **Neden:** Ses kimliği ve mekân sesi görüntünün ya da kurgunun dosyasında durursa iki sahip olur. Ses aracı evrene yazarken görüntü dosyasını açmak zorunda kalır.
- **Önerim:** [SEN2] §2.7 ve [YÖN2] Ç-14 ile aynı: sahip başına ayrı dosya.
  `EVREN/<SERI>/karakterler/<id>/ses.json` (+ `ses/` klasörü), `EVREN/<SERI>/mekanlar/<id>/ses.json`, `EVREN/<SERI>/nesneler/<id>/ses.json`, `EVREN/<SERI>/muzik/`.
  `mekan.json` ve `karakter.json` yalnız `ses_ref` yolunu tutar. Hepsini `evren.py` yazar ([MİM] makine sahipli).

### İ-9 · [MİM] §5.8 kör paket "replik metni ve kimin söylediği (ses yönü)" · [KUR] §5.4 `IZLE.md` "KALIN SESLİ ERKEK"
- **Kabul:** Kurgucunun biçimi doğru yönde: ekran dışı sesi adla değil sesin tarifiyle vermek.
- **Eksik:** Tarifin kaynağı yazılmamış. Ajan "kalın sesli" diye kendi uydurursa iki benzer sesi farklı, iki farklı sesi benzer anlatabilir. Gerçek seyircinin kafa karışıklığı ölçülemez.
- **Önerim:** Her karakterin `ses_etiketi_tr` alanı (ör. "kalın, boğuk erkek sesi") ses kadrosunda yazılır. **Ölçüme bağlıdır:** gömme benzerliği ≥ 0,60 olan iki karakter
  (S1.5 sınırı) aynı etiketi alır. Böylece seyirci gerçekten karışacaksa pakette de karışır. Kurgu turunda "duyulan" satırı plandan değil **son miksten** çıkar:
  ASR o repliği anlaşılır duymadıysa satır `(anlaşılmayan konuşma)` olur (S7.6, ARIS kör döküm ilkesi, A1 B4).

### İ-10 · [SEN2] §4.8.4-5 "kilitten önce TTS + ASR doğrulaması (yerelde)" ve §2.3 "`veo_metin`'i ses kadrocusu yazar"
- **Sıra sorunu:** Hikâye kilidi (H13) bulutta da olabilir. TTS ise AI84 anahtarı gerektirir ve yalnız yerelde çalışır. Ayrıca adlar görüntü kimlik dizelerine de girer
  ([GÖR] `kimlik_en` "Mara, an adult woman…"). Ad, kartlar üretildikten sonra değişirse kartlar ve istemler bayatlar.
- **Önerim:** Telaffuz testi **yereldeki ilk iştir** ve kart üretiminden önce koşar (§4.2 SB1; kart üretimi zaten yerel). Geçmeyen ad H15 dar değişikliğiyle hikâyeye döner.
  Bu noktada henüz görsel ve kredi yoktur.
- **`veo_metin` varsayılanı:** `metin` ile aynıdır. Okunuşa göre yazım ("Kess-tra") istemde ters tepebilir; Veo heceleri ayrı okuyabilir (tahmin). Bu yüzden önceden yazılmaz.
  Yalnız Veo bir adı videoda yanlış okuduğunda (S2.3) o ad için `veo_metin` kuralı yazılır ve **sonraki** klipler için ders defterine girer (`istem_kalibi`).
  Altyazı her zaman `metin`'den ya da duyulan metinden gelir.

### İ-11 · [ÜRE] §8.4 `veo_dogal` · [MİM] §8 Karar 4 `veo_ham`
- **Neden:** Veo'nun dönüştürülmemiş sesi, karakterin sesinin klipten klibe değişmesi demektir (A3 A2). Kapsamı yazılmazsa kolay yol diye yayılır.
- **Önerim:** `veo_ham` yalnız şu durumda serbesttir: `rol: figuran` olan, filmde **tek repliği** olan (tahmin) ve sesi kadrodaki ana karakterlerin merkezine ≥ 0,60 benzemeyen
  (S1.5) karakter. Bu ses de S2 metin kapısından ve S4 seviye eşitlemesinden geçer. Yaratık sesi hiçbir zaman `veo_ham` değildir; evren kitinden gelir (§4.8.2-c).

### İ-12 · [KUR] §5.1 `diyalog[].metin_duyulan`, `lufs_olculen` · [SM1] §5.4 `altyazi_metin` (öz eleştiri)
- **Neden:** Duyulan metin, ölçülen seviye ve dosya yolu hem kurgu planında hem `SESLER/diyalog.json`'da tutulursa ayrışır.
- **Önerim:** Tek kaynak `SESLER/diyalog.json → replikler.<replik_id>.duyulan_metin` (benim `altyazi_metin` adımı geri çekiyorum). Kurgu planı yalnız replik kimliğini,
  cümle aralığını ve çizelge zamanını tutar. Altyazı (`KURGU/altyazi_en.srt`) bu kaynaktan üretilir.

---

## 2. Çakışmalar ve önerdiğim çözüm (alan adları, aşama sırası, sorumluluk sınırları)

### 2.1 Alan adları ve yerleri

| # | Çakışma | Taraflar | Önerdiğim çözüm |
|---|---|---|---|
| Ç-1 | Replik tonu | [SEN2] `replik.teslim` (5 değer) · [YÖN2] `replik.ton_fiili` (EN serbest dize) · [SM1] `ton_fiili` + `seviye` + `etiketler` | **Tek yazılan alan `replik.teslim`** (sahibi senarist). Değeri `veri/plan_sozlukleri.json → teslim` sözlüğündendir. Sözlük her değer için `en_fiil`, `seviye` (4 LUFS sınıfı, RE:diyalog_lufs) ve `tts_etiket` taşır. `_derlenir.ton_fiili_en` ve `_derlenir.seviye` kodla türetilir. Ses, gerekçeyle `zanaat.ses.diyalog.seviye_ozel` yazabilir. Sözlük 5 değerle başlar; oyunculuk inceliği için (acı, yalvaran, sert) genişletilebilir, her yeni değerin 4 sınıftan birine eşlenmesi şarttır (§4.5.2) |
| Ç-2 | Ses alt nesnesi | [SM1] `zanaat.ses` · [YÖN] üst düzey `ses` · [YÖN2] `zanaat.ses` · [MİM] `35_SES/SES_Sxx.json` ayrı dosya | Ajan **`35_SES/SES_<S>.json`** yazar (sahne grubu dilimi). `plan_birlestir.py` bunu `SAHNELER.json → zanaat.ses` ve `sahne_gruplari.<S>.ses` alanlarına taşır. İkisi aynı içeriktir; yazılabilen tek yer ajan çıktısıdır ([MİM] §2.2-2) |
| Ç-3 | Ses yolu | [SM1] `ses.diyalog.yol: A/B/L_tasma/Y2` · [YÖN] `replik_kaynagi` · [ÜRE] `ses.yol: veo_donustur/tts_dudak/veo_dogal/ai84_vc` · [MİM] `ses.yontem: veo_donustur/tts_dudak/veo_ham` | Planlanan yol `zanaat.ses.diyalog.yol ∈ {veo_donustur, tts, veo_ham}`. Gerçekleşen yol `SESLER/diyalog.json → yol_gercek ∈ {veo_donustur, tts, tts_dudak, ai84_vc, veo_ham}`. L/J taşması yol değildir: `zanaat.ekran_disi_ses.kaynak = "plan:<no>"` aynı ses dosyasını kullanır. Harf kodlarımı (A/B/Y2) bırakıyorum; adlar kendini açıklıyor |
| Ç-4 | Ağız görünürlüğü, dinleyen ağız | [SM1] `ses.diyalog.agiz_gorunur`, `dinleyen_agiz` · [YÖN2] `_derlenir` | `_derlenir.agiz_gorunur ∈ {tam, kismi, yok}` ve `_derlenir.dinleyen_agiz ∈ {kapali, serbest}` kodla hesaplanır ([YÖN2] İ-9). Ses okur, yazmaz. Kurguda ölçülen gerçek görünürlük S3.7 raporundadır |
| Ç-5 | Ekran dışı ses | [SM1] üst düzey · [YÖN2] `zanaat.ekran_disi_ses = {replik, karakter, kaynak: "plan:<no>"\|"tts", bas_sn, sure_sn}` | [YÖN2] biçimi. `kaynak: "tts"` yalnız ses tanıtım kuralı geçince (S0.3 = Y59; tek fonksiyon `ses_tanitim_kurali()`, kodu ses kütüphanesinde, `plan_denetim` çağırır) |
| Ç-6 | Efekt ↔ adım | [SM1] `adim: 0` (dizin) · [YÖN2] `adim: "a1"` | **`adim: "a1"`** kalıcı kimlik. Dizin kayması böylece biter |
| Ç-7 | Replik süre ölçümü | [SM1] `replik_zaman.tts_sn` · [YÖN2] `zanaat.ses.tts_sn` · [KUR] `SESLER/replik_olcum.json` | Ölçüm bir kez yazılır: `SESLER/diyalog.json → replikler.<id>.tts.{sure_sn, kelime_sn, kelimeler[]}`. `_derlenir.replik_tts_sn` buradan derlenir. Kurgucunun T1'i bu dosyayı okur; `replik_olcum.json` ayrıca yazılmaz |
| Ç-8 | Ses tarifi | [SEN] `ses_tarifi_en` (yaş içeriyordu) · [SEN2] `ses_karakteri` (TR, serbest) · [SM1] `veo_ses_tarifi` | Hikâye `karakterler.<id>.ses_karakteri` (TR, serbest) yazar. Kadro kipi bunu yapılandırılmış profile, `veo_ses_tarifi`'ne (EN, ≤ 12 kelime, aksanlı, İ-3) ve `ses_etiketi_tr`'ye (İ-9) çevirir |
| Ç-9 | Telaffuz | [SEN2] `ad_telaffuz` · [SEN] evren `sozluk.adlar.telaffuz` · [SM1] ses profilinde `telaffuz` | **Tek kaynak hikâyenin `ad_telaffuz`** (evren `hikaye.json → sozluk.adlar`). Ses profilinde kopya tutulmaz. Test sonucu `ses.json → telaffuz_testi` alanına yazılır |
| Ç-10 | Müzik ipucu planda mı? | [ZN] §6.1 `ses.muzik_ipucu` · [SM1] plan ve liste ikisinde · [KUR] `KURGU_PLANI.muzik[]` | İpucu listesi tek kaynaktır: `MUZIK/muzik_listesi.json` (giriş ve çıkış olayı plan + adım kimliğiyle). Plandaki `muzik_ipucu` kaldırılır; görüntüleme için `_derlenir.muzik_ipucu` hesaplanır. Zaman çizelgesindeki yeri `SES_CIZELGESI.json`'dadır (İ-1) |
| Ç-11 | Ses kimliği evrende nerede | [SM1] `EVREN/SESLER/<k>/` · [ÜRE] `KUTUPHANE/<SERI>/sesler.json` + `kimlik.json.ses` · [GÖR] `karakterler/<id>/` + `ses_ref` · [SEN2] `karakterler/<id>/ses.json + banka` | **`EVREN/<SERI>/karakterler/<id>/ses.json` + `ses/`** (çoğunluk). Kök `FILM_AYAR.json → evren_kok`. `KUTUPHANE/` adı kullanılmaz |
| Ç-12 | Efekt kütüphanesi | [SM1] `SES_KUTUPHANESI/DIZIN.json` · AR (62 CC0 efekt + zeminler, lisanslar `LISANS.txt`'te) | Kullanıcının mevcut `SES_KUTUPHANESI\` klasörü yerinde kalır (yol ayardan). Seriden bağımsızdır. `DIZIN.json` bu klasörde durur. `LISANS.txt` ilk dizinlemede okunur |
| Ç-13 | Rapor klasörü, çıkış kodları | [MİM] `RAPORLAR/` · [SEN2], [KUR], [ÜRE], [SM1] `_RAPOR/` · çıkış kodları ajan işi 2/3/4 | Benim araçlarım ikisini de ayardan okur. Ben `_RAPOR/` ve [ÜRE] 0–7 tablosunu destekliyorum. Karar orkestratör sahibinindir ([YÖN2] Ç-21 ile aynı tutum) |
| Ç-14 | Eşik dosyası | [SEN2] ortak yükleyici `esikler.py` · [ÜRE] `hat_esikleri.json` · [GÖR] `sureklilik_esikleri.json` | Yeni ses eşikleri **`ses_esikleri.json`**'da durur. RE'deki mevcut ses anahtarları (`diyalog_lufs`, `final_lufs` …) orada kalır, kopyalanmaz. `esikler.py` iki dosyada aynı anahtarı görürse HATA verir ([SEN2] önerisi) |
| Ç-15 | Sağlayıcı türleri | Mevcut `TURLER = (gorsel, video, ses, muzik)` · [ÜRE] `(llm, vlm, gorsel, video, tts, ses_donustur, dudak, muzik)` | [ÜRE] listesi + **`ayristirma`**, **`asr`**, **`dinleyici`** (isteğe bağlı). Mevcut `ses` türü `tts`'nin eski adı olarak bir sürüm boyunca tanınır |

### 2.2 Dosya sahipliği (ses tarafı)

| Dosya | Sahibi (yazan) | Okuyanlar |
|---|---|---|
| `35_SES/SES_PROFILLERI.json` | `ses-tasarimcisi` kadro kipi | `ses_sec.py`, `istem_derle --hareket`, kör paket |
| `35_SES/SES_<S>.json` | `ses-tasarimcisi` tasarım kipi (taslağı `ses_plani.py` hazırlar) | `plan_birlestir.py` → `zanaat.ses` |
| `35_SES/muzik_listesi.json` → `MUZIK/muzik_listesi.json` | `ses-tasarimcisi` müzik kipi | `muzik.py`, kurgucu (salt okunur) |
| `SESLER/diyalog.json` (v2) | `seslendir.py`, `ses_donustur.py`, `ses_karar.py` | `plan_kurgu.py`, `capcut_film.py`, kör paket, kurgucu |
| `KURGU/SES_CIZELGESI.json` | `ses_katmani.py`, `muzik.py --yerlestir` | `kurgu_render.py`, `capcut_film.py`, `kurgu_denetim.py` |
| `KURGU/STEMS/*.wav`, `YAYIN/ses_master.wav` | `son_miks.py` | kurgu, yayın |
| `_RAPOR/S0…S8_*.json` | ses araçları | `kurgu_denetim.py`, `kuyruk.py`, ders defteri |
| `EVREN/<SERI>/karakterler/<id>/ses.json`, `mekanlar/<id>/ses.json`, `nesneler/<id>/ses.json`, `muzik/` | `evren.py` (ses araçlarının çağrısıyla) | herkes |
| `SES_KUTUPHANESI/DIZIN.json` | `ses_kutuphanesi.py` | ses araçları |

### 2.3 Aşama sırası ([MİM] A-kodlarıyla; ayrıntı §4.2)
```
[SEN2] H13 kilit ─► SA1 ses profilleri (bulut olur) ─────────────────────────────┐
[YÖN2] Y0–Y6 plan + defter + plan seyircisi ─► SA2 ses tasarımı ─► SA3 müzik planı ─► SA4 S0 kâğıt kapısı (A08)
                                              └─► A09 istem derleme (veo_ses_tarifi, veo_metin, flow_sound burada istemlere girer)
─── yerel ───────────────────────────────────────────────────────────────────────────────────────────
SB0 kurulum ölçümü ─► SB1 telaffuz testi ─► [GÖR] A10 kartlar  ║  SB2 ses seçimi ─► SB3 motor kıyası (seri başında bir kez)
                                                                ║  SB4 eksik efekt temini (CC0)
[GÖR] görseller + G1 ─► SB5 animatik sesi (seçilmiş seslerle TTS, yatak, efekt, gerçek müzik, işitsel döküm) ─► [KUR] animatik seyircisi ⟲
[ÜRE] bütçe ─► A14 video dalgaları ─► her indirmede SC1 metin kapısı ─► (yeniden çekim aynı dalgaya)
A15 SD1 dönüşüm / TTS / yedek merdiveni (S2)
A16 [KUR] kaba kurgu T2 ─► SE1 dudak (S3) ─► SE2 diyalog eşitleme (S4) ─► SE3 ambiyans + efekt (S5) ─► SE4 müzik (S6) ─► SE5 miks (S7) ─► kurgu seyircisi ⟲
     (her kurgu değişikliğinde SE6: yalnız etkilenen sahnelerde SE1–SE5)
A17 SF1 yayın sesi (S8) ─► A18 SF2 ders defteri + evren
```
- **SA1 neden H13'ten hemen sonra:** `veo_ses_tarifi` istem derlemesinde (A09) gerekir. Profil seçimden önce yazılır. Seçim profile uymak zorundadır (aksan, perde, S1.6–S1.7).
  Seçimde profil değişirse istem derlemesi yeniden koşar. Bu kâğıt işidir, kredi harcamaz.
- **SA2 neden plan seyircisinden sonra:** `flow_sound` istemlerin içine girer ve tasarım bitmiş eylem zincirine (adım kimliklerine) bakar. [YÖN2] §2.3 ile aynı yer.
- **SB1 neden kartlardan önce:** İ-10.

### 2.4 Sorumluluk sınırları

| Konu | Karar veren | Ses ne yapar |
|---|---|---|
| Replik metni (kelimeler), `teslim`, `tasidigi`, ad ve `ad_telaffuz` | `hikaye-yazari` | Okur. Telaffuz testi ve S2.4 (`tasidigi` duyuldu mu) ölçer |
| Veo'nun söylediği metin senaryodan **gri bantta** saptı (WER 0,10–0,25, `tasidigi` tam, ad doğru) | **`hikaye-yazari` `replik_kabul` kipi** (yeni örnek; yalnız ilgili replik, senaryo metni, duyulan metin ve `tasidigi`) | Paketi hazırlar. Kabulde `duyulan_metin` altyazıya geçer; retle repliği yeniden çekime yazar |
| Kadraj, ekran dışı ses, J/L niyeti, konuşma adımının zamanı | yönetmen | `_derlenir` alanlarını okur |
| J/L'nin gerçek uygulanışı, kırpma, sıra, diyalog yerleşimi (senkron kuralı) | kurgucu (`plan_kurgu.py`, `kurgu_uygula.py`) | Ses dosyalarını ve kelime zamanlarını verir. Kurgu her değiştiğinde S3'ü koşar |
| Ses kaynaklı kurgu çözümü (ağzı görünmesin diye kırpma, repliği ekran dışına taşıma) | kurgucu (0 kredi merdiveni, [KUR] §5.5 #3) | `ses_karar.py` öneriyi kurgucunun kuyruğuna yazar |
| Flow'da yeniden çekim | `kuyruk.py` + bütçe kapısı ([KUR], [ÜRE]) | `YENIDEN_URET.json`'a `kaynak_kapi: "S2"` maddesi ve şablonla üretilmiş CORRECTION cümlesi yazar |
| Ses kaynaklı plan değişikliği (repliği tepki planının üstüne taşı, kadraj değiştir) | yönetmen onarım kipi | Gereksinimi yazar ("ne ve neden"), "nasıl" yönetmenindir |
| Yüz kimliği, ağız noktaları | görüntü (`olcum/kimlik.py`, `olcum/poz.py`, tek MediaPipe sürümü) | S3.4–S3.7 için bu modülleri çağırır; kendi kopyasını kurmaz |
| Dünya durumu defteri | süreklilik (`dunya_defteri.py`) | Yatak katmanları ve sürekli nesne sesleri için okur (S0.11) |
| Efekt, ambiyans, müzik, miks, seviye | ses | — |
| Yayın paketi, kapak, Content ID ön kontrolünün yüklenmesi | yayın (onaylı yükleme) | `ses_master.wav`, `KAYNAK_KAYDI.json` ve S8 raporunu verir |

### 2.5 Ders defteri (ortak biçime uyum)
- Biçim [ÜRE] §5.8 ve [MİM] §5.6: tek olay tek kayıt; ortak `ders_defteri.kaydet(...)`; terfi kuralı; korkuluklar. Benim ayrı `ses_kurallari.json` önerimi geri çekiyorum.
  Yer ve dosya adı defter sahibinin kararıdır.
- **Ses kategorileri** (`kategori` sözlüğüne eklenir): `veo_konusmadi`, `veo_metin_sapti`, `ad_yanlis_okundu`, `yanlis_kisi_konustu`, `dinleyen_konustu`,
  `donusum_metalik`, `ses_kimligi_dusuk`, `aksan_kaydi`, `dudak_kayma`, `seviye_zipladi`, `ambiyans_zipladi`, `efekt_eksik`, `yatakta_soz`, `muzik_maskeledi`,
  `muzik_motifsiz`, `vokal_sizdi`, `lisans_belirsiz`.
- **Kural türü eki:** [ÜRE]'nin izinli `tur` listesine **`yol_kurali`** (ör. "fısıltı + ağız tam görünür değil → `tts`") ve **`kara_liste`** (kütüphane dosyası ya da paylaşılan ses)
  eklenmeli. Telaffuz düzeltmesi mevcut `istem_kalibi` türüne girer.
- `rol_etiketi: ["ses-tasarimcisi"]` olan dersler kancayla ajana verilir ([MİM] K-7b).

---

## 3. Diğerlerinden kabul edip kendi önerime kattıklarım

**[YÖN] / [YÖN2] yönetmen**
- `zanaat` alt nesnesi, alan başına sahiplik, `_derlenir` (kod yazar). Benim `ses.diyalog.agiz_gorunur` ve `dinleyen_agiz` alanlarım `_derlenir`'e taşındı.
- `zanaat.ekran_disi_ses = {replik, karakter, kaynak, bas_sn, sure_sn}`; `kaynak: "tts"` yalnız ses tanıtım kuralıyla (Y59).
- Adım kalıcı kimliği `a1…a3`; konuşma adımı `{"tur": "konusma", "replik": "R0121", "cumleler": [0, 1]}`.
- Konuşan yüz şartları: O/OY/Y, \|yaw\| ≤ 45°, başlangıç karesinde yüz ≥ kare yüksekliğinin %12'si (Y32; [GÖR] §8.9). Bu, dudak ölçümümün (S3.7) ön koşuludur.
- Fiziksel adım konuşmadan ≥ 0,2 sn önce biter (Y02b). Benim S0.9'umla (efekt ilk sözden ≥ 150 ms uzak) birlikte çalışır.
- Konuşmalı planda Bitir karesi yok (Y56). Bitiş karesinin dudak davranışına etkisi ölçülmeden ses yolu bu klipleri riske atmaz.
- Z1 (gerçek son kare) varsayılanı: ses için anlamı, `devam` geçişlerinde ambiyansın çapraz geçişsiz sürmesidir (S0.10).
- Sahne grubu = hikâye sahnesi (1:1). Yatak sahne grubu başına tektir; sınırlar hikâyeyle aynı olur.

**[SEN] / [SEN2] senarist**
- `tasidigi` alanı. Veo'nun sapmış metni `tasidigi` öğelerinden birini kaybettiyse kabul **yoktur** (S2.4).
- `ses_karakteri` (TR, serbest) hikâyenin, Veo dizesi sesin. Benim tur 1 örneğimde de yaş sözcüğü yoktu; [SEN]'in "early 30s" örneği düzeltildi.
- Telaffuz-güvenli ad kuralları (2 hece, ayrışan adlar; tahmin eşikleri onların) ve `ad_telaffuz`.
- Replik bloğunda tek teslim (dönüştürücüler ton geçişinde zorlanır, A3 A2).
- **0 kredili köprü replik** (H15): kilitten sonra bilgi eksiği Yol B (`tts`) ile ekran dışından kapatılabilir. Ses tarafındaki şart: köprünün altındaki planda
  görünen herkesin ağzı **ölçülerek** kapalıdır (S3.5) ve ses tanıtım kuralı geçer.
- Habersiz seyircide ad maskeleme ve `maske.etiket_anonim_en`. İşitsel dökümde de aynı maskeleme kodu kullanılır (`kor_paket.py`).

**[KUR] kurgucu**
- **Senkron kuralı:** görünen konuşanın sesi her zaman klip zamanına bağlıdır; `diyalog.cizelge_bas = plan.cizelge_bas + (klip_zamani.bas − kullanim.bas) / hiz`.
  Senkron korumalı klip bölme formülü. Yol A'nın dudak güvencesi bu kuralla kurguda da korunur.
- Dört zaman çizelgesi (T0 kâğıt, T1 animatik, T2 kaba kurgu, T3 CapCut). Ses kapılarım hangi çizelgede ne ölçtüğünü bu adlarla yazıyor (§4.7).
- CapCut kanalları: Klipler, Bantlar, Kartlar, Altyazi, Diyalog, Efekt, Ambiyans, Muzik, NOTLAR. Ekim: **Klipler kanalının sesi her zaman kapalıdır** (§4.6).
- Kullanıcının CapCut kararı aynen uygulanır. `TASLAK_FARK.json → geri_uretilemeyen` içinde elle ses ayarı varsa son miks bu ayarı uygular ya da yalnız ölçer (§4.2 SF1).
- Kök neden sözlüğündeki `ambiyans_zipladi`, `seviye_zipladi`, `dudak_ustune_replik`, `muzik_yanlis_yer` kayıtları ses kuyruğuna gelir.
- Kullanıcının ses ve müzik notlarını kurgucu sınıflar ve ses kuyruğuna verir ([KUR] §9.4-10).

**[GÖR] görüntü-süreklilik**
- `olcum/` paketi (tek arayüz `olc(...) → dict`, her arka ucun `sahte` hâli). Ses ölçüleri aynı pakete `olcum/ses.py` ve `olcum/dudak.py` olarak girer.
- "Ölçülemedi asla GEÇ değildir" kuralı ses kapılarında da geçerli (ör. yüz çok küçükse S3 `ÖLÇÜLEMEDİ` → BAYRAK).
- Dudak senkronu çıkan klibin V2'den yeniden geçmesi (S2.15).
- Konuşan planın başlangıç karesinde ağzın kapalı ve görünür olması.

**[ÜRE] üretim mühendisi**
- Çıktı zarfı, imza, `bayat` işareti, kalıcı silme yok. Yeniden çekilen planın eski efekt yerleşimi `bayat` olur ve yeniden kurulur (D "yeni çekilen planlar efektsiz kalıyordu").
- `Kisitlandi.kod` ve yedeğe yalnız izinle geçiş. Ses sağlayıcılarında da aynı: AI84 kredisi biterse (`kredi_bitti`) hat durur, kalite düşürülmez.
- **İlk filmin P1'inde iki yol kıyası** (§8.4): kabul ediyorum, artık kredisiz ve dolarsız. MuseTalk yerelde çalıştığı için ([D-MT]) 20 replik iki yolla işlenir.
  Kıyas önce arşiv klipleriyle (seri başında), sonra yeni filmin ilk 20 repliğiyle yapılır (§4.2 SB3).
- "Dürüst sonuç" ([ÜRE] §8.5): insansız video için resmî API (Vertex Veo) gerekebilir. Ses tarafı buna hazırdır: Yol A sağlayıcıdan bağımsızdır.
  Flow ile Veo API'nin sesi farklı olsa da dönüştürücü ikisini aynı evren sesine çevirir.
- `.gitignore`: ses dosyaları, banka ve modeller git'e girmez; yalnız JSON'lar girer.

**[MİM] Claude Code mimarisi**
- Görev defteri, `_GOREV/<id>/{GOREV.json, ISTEM.md, GIRDI, CIKTI}`, şablondan istem, ajanlarda Bash yok, denetim SubagentStop kancasında.
  Ses betiklerini ajan değil `film.py` görevleri çalıştırır.
- Tek ses ajanı (`ses-tasarimcisi`; kipli). `muzik-supervizoru` taslağı kalkar.
- `omitClaudeMd` kör roller içindir; ses ajanı kör değildir.
- Kör pakette ses ipucu "duyulan" olarak verilir; `ekranda_bilgi` verilmez.

---

## 4. REVİZE NİHAİ ÖNERİM

Bu bölüm tur 1 biçimindeki dokuz başlıkla, tur 1'i okumadan anlaşılacak biçimde yazıldı. Tur 1'den değişen yerler **(değişti)** ya da **(yeni)** diye işaretli.

### 4.1 Alanımın hedefi ve başarı ölçütü (sayılarla)

#### 4.1.1 Hedef
Seyirci 30–45 dakika boyunca bir kez bile şunları dememeli: "dudak tutmuyor", "bu ses kimin?", "sesi değişti", "aksanı değişti", "ses kesildi ya da zıpladı",
"müzik konuşmayı bastırıyor". Her karakter **filmden filme aynı sesle ve aynı aksanla** konuşmalı (seri evreni). Müzik **yasal olarak kullanılabilir**, sözsüz ve
karaktere bağlı (leitmotif) olmalı. Film YouTube'da **−14 LUFS**'ta temiz çalmalı. Bütün bunlar kullanıcıya soru sorulmadan, ölçülerek ve kayıt altında yapılmalı
(kesin karar 1 ve 6).

#### 4.1.2 Ses/dudak kararı (kesin karar 4) — kısa hâl (gerekçe ve hesap §4.8.3)
**"Veo konuşur, sesi biz sabitleriz."**
1. **Ana yol `veo_donustur` (ağzı görünen replik):** Flow/Veo klibi repliği kendisi söyler. İstemde replik, `teslim` fiili ve karakterin sabit **aksanlı** Veo ses dizesi bulunur.
   Konuşma ayrıştırılır, senaryoya hizalanır, metin kapısından geçer ve karakterin evren sesine **yerel ses dönüştürücüyle** çevrilir. Dudak, zamanlama ve oyunculuk
   Veo'dan gelir. Görüntüye dokunulmaz.
2. **`tts` (ağzı görünmeyen replik):** ekran dışı, sırt dönük, uzak plan, köprü replik. Aynı evren sesiyle ElevenLabs v4 TTS (AI84) kullanılır. Animatikte üretilen dosya son sestir.
3. **Yedekler hata türüne göre bir merdivendir** (`ses_karar.py`, §4.8.3). Kaliteyi düşürmeyen 0 kredili basamaklar önce gelir: metnin sahibinin kabulü, motor değişimi,
   ağzı zaten görünmeyen planda TTS. Sonra Flow'da yeniden çekim (en çok 2, normal kuyruk). Sonra **yerel** dudak senkronu `tts_dudak` (MuseTalk 1.5, 4 GB'ta ≈ 5 dk / 8 sn klip [D-MT]).
   Dönüşüm kalitesi sorununda tek kritik replik için bütçe izin verirse `ai84_vc` kullanılır. En son kurguda ekran dışına taşıma ya da yönetmenin plan değişikliği gelir.
   Wav2Lip ve ticari olmayan lisanslı modeller **asla** kullanılmaz.
4. Dönüştürme motoru varsayımla değil, **arşivdeki gerçek Veo klipleriyle kredisiz kıyas** ile seçilir. Kıyas ilk filmin ilk 20 repliğinde yeniden yapılır.
5. **Müzik:** leitmotifin kimliği **notalarıyla** (MIDI) evrende saklanır. İpuçları yerelde ACE-Step 1.5 (MIT) ile üretilir. Motifli ipucu bu motifin çalınmış hâlini
   "Cover/Refer audio" girdisi olarak alır [D-AS]. Motif testini geçemeyen ipucu MIDI + lisansı temiz örneklerle çalınır. Lisansı belgelenmemiş hiçbir parça kullanılmaz.

#### 4.1.3 Başarı ölçütleri

| # | Ölçüt | Hedef | Ölçen | Kaynak |
|---|---|---|---|---|
| B1 | Dudak ofseti (ağzı görünen replik, kurgu sonrası) | Repliklerin ≥ %95'i \|ofset\| ≤ 42 ms (24 fps'te 1 kare); hiçbiri > 125 ms | `dudak_denetim.py` | 1 kare (hesap); %95 (tahmin); 125 ms ITU-R BT.1359 "ses geride" fark edilme eşiği (bellekten); [KUR] `senkron_tolerans_kare` 1 |
| B2 | Başkasının repliği altında oynayan dudak | 0 | `dudak_denetim.py` | BK 5.1.8, Z §0 K4 |
| B3 | Ses kimliği: her son replik ↔ karakterin evren ses merkezi | %100 replik ≥ eşik (başlangıç 0,70) | `olcum/ses.py` (konuşmacı gömmesi) | eşik (tahmin), §4.7.9 kalibrasyon |
| B4 | Kadro ayırt ediciliği | Karakterler arası benzerlik ≤ 0,60; aynı cinsiyette F0 medyanı farkı ≥ 2 yarım ton | `ses_sec.py` | (tahmin) |
| B5 | **(yeni)** Aksan tutarlılığı | Seçilen sesin aksan etiketi = profil aksanı (%100); videoda aksan sınıfı tutarsız replik 0 (ölçülebildiği ölçüde) | `ses_sec.py`; `dinleyici` ya da aksan sınıflayıcısı | İ-3; [D-EL] `accent` süzgeci |
| B6 | Altyazı = duyulan söz | Altyazı `duyulan_metin`'den; adlar %100 doğru; son miksteki ASR ↔ altyazı WER ≤ 0,15 / replik | `son_miks.py` + ASR | WER eşiği (tahmin); müziğin konuşmayı maskelemesinin ölçüsü |
| B7 | Diyalog seviyesi | fısıltı −24 · yumuşak −21,5 · normal −19,5 · bağırma −17 LUFS, ±1 LU, %100 | `diyalog_esitle.py` | RE:diyalog_lufs, RE:diyalog_lufs_tolerans |
| B8 | Ambiyans | Sahne grubu içinde tek yatak; boşluk 0; ardışık planlar farkı ≤ 3 LU; diyalogdan 12–18 dB aşağı | `ses_katmani.py` | RE:ambiyans_sahne_ici_fark_max_lu, RE:ambiyans_diyalog_alti_db; D (kapı sahnesi) |
| B9 | Efekt | Her fiziksel adıma ≥ 1 efekt (sessiz işaretliler hariç); yeniden çekilen planda güncel efekt %100 | `ses_plani.py`, `ses_katmani.py` | Z §5.1; D |
| B10 | Müzik yerleşimi | Kaplama %40–65; müziksiz blok ≤ 240 sn; müzikli blok ≤ 300 sn; diyalog altında ≥ 12 dB aşağı | `muzik.py` | RE:muzik_kaplama_oran, RE:muziksiz_blok_max_sn, RE:muzikli_blok_max_sn, RE:muzik_diyalog_alti_min_db |
| B11 | Leitmotif | Doruğa kadar ≥ 3 dönüş, **ses analiziyle doğrulanmış** | `muzik.py` (kroma benzerliği) | RE:leitmotif_donus_min; yöntem (tahmin) |
| B12 | Müzik lisansı | Her parçanın kaynak kaydı %100; söz/vokal 0; elle iş isteyen sağlayıcı 0 | `muzik.py` | BK 4.5; [ÜRE] M2 |
| B13 | Sessizlik | Mutlak sessizlik ≤ 2/film, her biri ≤ 1 sn ve yalnız planlı yerde | `son_miks.py` | RE:mutlak_sessizlik_* |
| B14 | Final karışım | −14 ±1 LUFS; gerçek tepe ≤ −1 dBTP; LRA ≤ 14 LU; mono toplam farkı ≤ 3 LU | `son_miks.py` | RE:final_lufs, RE:true_peak_max_dbtp; LRA ve mono (tahmin) |
| B15 | **(yeni)** Tek miks kodu | Animatik, önizleme, final ve Shorts aynı `son_miks` işlevinden; T1'de geçen ses ölçüsü T2'de HATA olamaz | yapısal test + [KUR] geri gidiş yasağı | İ-1 |
| B16 | Seyirci | Kurgu izleme raporunda ses kaynaklı KRİTİK = 0 ("kim konuştu belli değil", "ses kesildi") | habersiz seyirci + `kor_paket` işitsel dökümü | RE:kopukluk_kritik_max |
| B17 | **(değişti)** Maliyet | Ana yolda dolar 0. AI84: film başına ≈ 25–30 bin kredi; seri başında bir kez ≤ 36 bin (yalnız RVC kazanırsa); kritik replik yedeği ≤ 20 bin. Ses kaynaklı Flow yeniden çekimi %20'lik payın içinde | `film.py` / `kredi.py` önizleme | hesap §4.8.3; RE:kredi_yeniden_deneme_payi |

### 4.2 Aşama aşama süreç: girdi → iş → çıktı dosyası → geçme şartı → kim yapar

**Yerleşim:** v2 sırası (BK §7.6) korunur: hikâye → seyirci → yönetmen → **ses (kâğıtta)** → kartlar → görseller → **animatik** → video → **katmanlı kurgu** → yayın.
Ses işleri altı bloğa ayrılır. A-kodları [MİM] aşama tablosudur. Her blokta "Kim" sütunu: **B** betik (`film.py` görevi), **A** ajan, **AC** ana Claude, **K** kullanıcı.

```
SA KÂĞIT (bulut olur, kredi yok): SA1 ses profilleri → SA2 ses tasarımı → SA3 müzik planı → SA4 S0 kâğıt kapısı      [A08; A09 istem derlemeden önce]
SB YEREL HAZIRLIK (Flow yok):    SB0 kurulum ölçümü → SB1 telaffuz testi → SB2 ses seçimi → SB3 motor kıyası → SB4 eksik efekt
                                 → SB5 animatik sesi (+ gerçek müzik, işitsel döküm)                                    [A10, A12]
SC VİDEO SIRASINDA:              SC1 her indirmede metin kapısı (S2 ön)                                                  [A14]
SD VİDEO SONRASI:                SD1 dönüşüm / TTS / merdiven (S2)                                                       [A15]
SE KURGU (T2, T3):               SE1 dudak (S3) → SE2 diyalog (S4) → SE3 ambiyans + efekt (S5) → SE4 müzik (S6) → SE5 miks (S7) → SE6 değişiklik  [A16]
SF YAYIN VE ÖĞRENME:             SF1 yayın sesi (S8) → SF2 ders defteri + evren                                          [A17, A18]
```
Klasörler: kâğıt çıktıları `35_SES/`, ses dosyaları `SESLER/`, müzik `MUZIK/`, zaman çizelgesi ve stemler `KURGU/`, raporlar `_RAPOR/` (klasör adları ayardan),
kalıcı kütüphane `EVREN/<SERI>/`, seriden bağımsız efekt kütüphanesi `SES_KUTUPHANESI/`. Her kapı `_RAPOR/<kapi>_<parti|dalga>.json` yazar. Biçim
Z §6.2 + [ÜRE] zarfı: `{kapi, sonuc, girdi_imza, esik_surum, hatalar:[{madde, plan|replik, olcu, esik, seviye, oneri}], ozet}`.

#### SA — Kâğıt bloğu (kredi yok; bulutta da çalışır)

**SA1. Ses profilleri** (hikâye kilidinden hemen sonra; yönetmenle paralel) **(değişti)**
- **Girdi:** `HIKAYE.json → karakterler` (`ses_karakteri`, `ad`, `ad_telaffuz`, `rol`, `konusmaz`), evren `hikaye.json` (bölge, halk, sözlük), varsa
  `EVREN/<SERI>/karakterler/*/ses.json`, rol etiketli dersler.
- **İş (`ses-tasarimcisi`, kip `kadro`):** Konuşan her karakter için yapılandırılmış profil yazılır: cinsiyet, yaş bandı (yalnız arama süzgeci; Veo dizesine girmez), **aksan**
  (ElevenLabs aksan sözlüğünden), perde, tını etiketleri, tempo, enerji. Ayrıca:
  - `veo_ses_tarifi`: EN, ≤ 12 kelime, sıra **tını/perde + cinsiyet + aksan** (İ-3). Filtre ve yaş sözcüğü yoktur.
  - `etiket_ailesi`: karakterin kullanabileceği TTS ton etiketleri.
  - `ses_etiketi_tr` taslağı: seyirci dökümü için; ölçümden sonra kesinleşir (SB2).
  - Halk ya da bölge aynıysa aksan ailesi aynıdır. Figüran için `veo_ham` adaylığı işaretlenir (İ-11).
  - Evrende kayıtlı karakter yeniden profillenmez.
- **Çıktı:** `35_SES/SES_PROFILLERI.json`, `35_SES/SES_KADROSU.md` (`Ruling: karar — neden — yanlışsa maliyeti` satırları).
- **Geçme şartı:** profil tam; S0.5 (dize kuralları); aynı cinsiyet ve yaş bandındaki karakterlerin perde ya da tını etiketleri ayrışır (B). Denetim SubagentStop kancasında.
- **Kim:** A (`ses-tasarimcisi` kadro) → B (`ses_plani.py --profil-denetle`). En çok 2 düzeltme turu.

**SA2. Ses tasarımı** (yönetmen planı, dünya defteri ve plan seyircisinden sonra) **(değişti)**
- **Girdi:** `SAHNELER.json` dilimi (`zanaat.eylem_zinciri` adım kimlikleriyle, `kadrajdakiler`, `ekran_disi_ses`, `kesme`, `_derlenir.{agiz_gorunur, dinleyen_agiz,
  replik_zaman, seviye}`), `sahne_gruplari.<S>` (`mekan`, `zaman{gun_saati, hava, atlama}`, `isik`), `DUNYA_DEFTERI.json` (mekân durumu, nesne durumu, karakter
  görünümü), `EVREN/<SERI>/mekanlar/*/ses.json`, `nesneler/*/ses.json`, `SES_KUTUPHANESI/DIZIN.json`, ses dersleri.
- **İş:**
  1. `ses_plani.py --taslak` taslağı kodla doldurur ve görevin GIRDI'sine koyar:
     - **yol:** `_derlenir.agiz_gorunur` tam/kısmi → `veo_donustur`; yok → `tts`; figüran kuralı → `veo_ham`; ders defterindeki `yol_kurali` kayıtları uygulanır.
     - **efekt olayları:** her fiziksel adım (`a1…`) için fiil → efekt sözlüğü (`veri/efekt_sozlugu.json`, fiil sözlüğü kimlikleriyle). Malzeme mekândan (zemin),
       kostüm kartından (kumaş) ve nesne kartından gelir. Olayın anı fiile göre seçilir (ör. `kavrar` → adımın sonu, temas anı; `yurur` → adım boyunca yayılır).
     - **yatak:** sahne grubu başına tek dosya. Mekânın varsayılan yatağına gün saati, hava ve mekân durumu katmanları eklenir (ör. ocak yanıksa ateş çıtırtısı).
     - **flow_sound:** `Sound: <en belirgin 2–3 olay>, <yatak tek ifade>. No music.` (≤ 12 kelime).
     - **sessizlik önerileri:** vuruş alanlarından (`vurus`: ifşa, şok, en karanlık, doruk, soğuk açılış).
  2. `ses-tasarimcisi` (kip `tasarim`) taslağı plan plan inceler. Yanlış fiil eşleşmesini ve eksik temas sesini düzeltir, sessizlikleri yerleştirir
     (Z §5.3, RE:vurgu_sessizlik_sn), yaratık sesini evren kitinden seçer, içeriden dışarı bakan planlarda dış katman kazancını yazar. Kurgucuya J/L köprüsü önerir
     (yalnız öneri). Eksik efekt listesini yazar.
- **Çıktı:** `35_SES/SES_<S>.json` (sahne grubu başına), `35_SES/SES_TASARIMI.md`, `35_SES/EKSIK_EFEKTLER.json`. `plan_birlestir.py` bunları `zanaat.ses` ve
  `sahne_gruplari.<S>.ses` alanlarına taşır.
- **Geçme şartı:** sahne diliminde S0 HATA = 0 (SubagentStop), en çok 2 tur.
- **Kim:** B taslak → A (`ses-tasarimcisi` tasarım; sahne grubu başına yeni örnek, paralel olabilir) → B.

**SA3. Müzik planı ve leitmotif**
- **Girdi:** `HIKAYE.json → duygu_haritasi, vuruslar`, planların `hedef_duygu`, `yogunluk`, `vurus`, `zanaat.ses.sessizlik`, T0 zaman çizelgesi ([KUR] K0),
  `EVREN/<SERI>/muzik/leitmotifler.json`, Z §1.3 ve §5.3–5.4.
- **İş (`ses-tasarimcisi`, kip `muzik`):**
  - **Leitmotifler:** evrendeki motif kullanılır. Yeni karakter ya da tema için motif **notalarıyla** yazılır (perde + süre listesi, ton/mod, BPM, ölçü,
    enstrüman, dönüşümler: sade / tehdit / zafer).
  - **İpucu listesi:** her ipucunun giriş ve çıkış **olayı** (plan + adım kimliği ya da replik sonu; cümle ortasında asla), türü (`tema` / `doku` / `aksiyon`),
    motifi ve dönüşümü, vuruş noktaları, seviye, sağlayıcı ve İngilizce istemi (sanatçı ya da film adı yok, "no vocals").
- **Çıktı:** `35_SES/muzik_listesi.json` → `MUZIK/muzik_listesi.json`, `35_SES/MUZIK_PLANI.md`. Yeni motifler `EVREN/<SERI>/muzik/` için **aday** kayıttır.
- **Geçme şartı:** `muzik.py --kagit` (S0.14–S0.18) HATA = 0.
- **Kim:** A (`ses-tasarimcisi` müzik) → B.

**SA4. Kâğıt ses kapısı S0 (bütün film)**
- **İş:** `ses_plani.py --denetle` film geneli maddeleri çalıştırır: sahne grupları arası yatak sürekliliği, mutlak sessizlik sayısı, müzik kaplaması, leitmotif dönüşleri,
  ses tanıtım kuralı (Y59 ile aynı fonksiyon).
- **Çıktı:** `_RAPOR/S0_ses_kagit.json`, HATA varsa `YENIDEN_YAZ.json` (yazan kipe geri; yönetmen ya da hikâye alanıysa onlara).
- **Geçme şartı:** HATA = 0. Ardından A09 istem derlemesi (`istem_derle --hareket`) `veo_ses_tarifi`, `teslim` fiili, `veo_metin` ve `flow_sound` öğelerini istemlere koyar.
  `istem_denetim.py` S0.4–S0.6'yı derlenmiş istemde yeniden denetler.
- **Kim:** B.

#### SB — Yerel hazırlık bloğu (Flow kredisi yok)

**SB0. Kurulum ölçümü** (yerel hazırlık aşamasının içinde, her film başında hızlı; ilk kurulumda tam) **(yeni)**
- **İş:** `ses_olcum.py --kontrol` şunları denetler. Kurulu olduğunu varsaymaz; sürümleri ve çalıştığını sınar:
  - ana ortam: ffmpeg, pyloudnorm, faster-whisper, stable-ts, python-audio-separator, MediaPipe (görüntü uzmanının sabitlediği sürüm).
  - **ayrı sanal ortamlar:** `venv_rvc` (Python 3.12 [D-RVC]), `venv_openvoice`, `venv_musetalk` (Python 3.10 + torch 2.0.1 [D-MT]), `venv_acestep` (Python 3.11–3.12 [D-AS]).
    Kullanıcının ana Python 3.10 ortamı bozulmaz. Köprü, mevcut `om_kopru.py` kalıbıyla kurulur (AR).
  - MIDI çalıcı (FluidSynth) ve örnek kütüphanesi.
  - `ai84.credits()` ve ücretsiz `ai84.estimate(...)` ile TTS ve Voice Changer birim fiyatları.
  - GPU kuralı: 4 GB kartta aynı anda **tek** ağır model koşar (tahmin; kuyruk betikte).
- **Çıktı:** `_RAPOR/S_KURULUM.json`, `AYARLAR/FILM_AYAR.json → fiyat_olcum` (anahtar içermez).
- **Geçme şartı:** Eksik ortam **yalnız kendi basamağını kapatır** ve bunu raporda açıkça yazar. Örnek: MuseTalk yoksa merdivende `tts_dudak` basamağı "kapalı" görünür.
  Hiçbir eksik sessizce "geçti" sayılmaz.
- **Kim:** B. Kurulum `KURULUM.bat` ile yapılır; kullanıcıya soru sorulmaz.

**SB1. Telaffuz testi** (yereldeki ilk iş; kart üretiminden önce) **(yeni)**
- **Girdi:** adlar ve `ad_telaffuz` (evren `hikaye.json → sozluk.adlar`), adı içeren gerçek replikler.
- **İş:** `ses_sec.py --telaffuz`: her ad için adı içeren 3 replik, ayarda sabit iki genel sesle (bir kadın, bir erkek) okunur. faster-whisper ile geri tanınır.
  Yazılış ya da fonetik karşılık (ör. Metaphone, bellekten) karşılaştırılır. Geçmezse alternatif yazımlar denenir.
- **Çıktı:** `_RAPOR/S1a_telaffuz.json`.
- **Geçme şartı:** her ad GEÇ (S1.2). Geçmeyen ad, öneriyle `YENIDEN_YAZ.json` üzerinden `hikaye-yazari`'na gider (H15 dar değişiklik, İ-10).
- **Kim:** B. **Maliyet:** ≈ 10 ad × 3 replik × 60 harf ≈ 1,8 bin kredi (tahmin).

**SB2. Ses seçimi (AI84 paylaşılan ses kütüphanesinden, otomatik)** **(değişti)**
- **Girdi:** `SES_PROFILLERI.json`, karakterin hikâyedeki en karakteristik 3 repliği (normal, duygusal, fısıltı ya da bağırma).
- **İş (`ses_sec.py`):**
  1. `--ara`: paylaşılan ses araması. Süzgeçler: `language=en`, `gender`, `age`, `accent` (profilden), `use_cases`, `descriptives`, `min_notice_period_days`
     (≥ 30 gün, tahmin), `sort` [D-EL]. AI84 bir süzgeci geçirmiyorsa sonuç yerelde süzülür. `voice_restricted` sesler elenir (BK 6.4).
     Aynı seride başka bir karakterin kullandığı ses elenir.
  2. `--olc`: ücretsiz önizleme sesleri ölçülür: F0 medyanı ve aralığı, konuşma hızı, konuşmacı gömmesi. Kadro ayırt ediciliği burada ön elenir.
  3. `--oku`: en iyi 4 aday karakterin 3 repliğini okur (önbellekli, sabit `seed`; AI84 geçiriyorsa).
  4. `--puanla`: profil uyumu, aksan etiketi, ayırt edicilik, ASR ile anlaşılırlık ve ad telaffuzu, 3 replik arası kararlılık, duygu aralığı (S1.8 formülü).
  5. **Seçim:** puan farkı ≥ 0,03 ise (tahmin) en yüksek aday kendiliğinden seçilir. Fark küçükse `ses-tasarimcisi` (kadro kipi, yeni örnek) ölçüleri ve ses meta verisini
     okuyup seçer ve gerekçesini yazar. Claude sesi duymaz; seçim yalnız sayıya ve tarife dayanır.
  6. `--sec`: `evren.py` ile `EVREN/<SERI>/karakterler/<id>/ses.json` yazılır. `ses_etiketi_tr` kesinleşir: benzerliği ≥ 0,60 olan iki karakter aynı etiketi alır (İ-9).
  7. Figüran `veo_ham` adayıysa seçim yapılmaz; kural S1.10'a göre denetlenir.
- **Çıktı:** evren `ses.json`, `_RAPOR/S1_ses_secim.json`, `35_SES/SES_SECIM.html` (dinlemek isteyen için; **onay kapısı değildir**, kesin karar 1).
- **Geçme şartı:** S1.1–S1.7, S1.9.
- **Kim:** B (+ yakın puanda A kadro). **Maliyet:** 6 karakter × 4 aday × 3 replik × ≈ 70 harf ≈ 5 bin kredi (hesap; karakter sayısı tahmin).

**SB3. Dönüştürme motoru kıyası** (serinin başında bir kez; yeni motor çıkınca yeniden) **(değişti)**
- **Girdi:** arşivdeki gerçek Flow konuşma klipleri (B2/B3 `SIRALI_VIDEO`, yol `FILM_AYAR.json → yollar.arsiv_klipler`; ≥ 20 replik, fısıltı ve bağırma dahil),
  pilot karakterin seçilmiş sesi.
- **İş (`ses_kiyas.py`):** Hedef referans, SB2 ve animatik TTS'lerinden kesilen ≈ 60 sn'dir (ek kredi yok). Adaylar:
  - OpenVoice V2 (MIT; referansla, eğitimsiz).
  - RVC (MIT). Karakter başına ≈ 10 dk ses bankası ile eğitilir (A3). **Yalnız** ElevenLabs/AI84 koşulları TTS çıktısıyla model eğitimine izin veriyorsa denenir (§4.9 açık soru).
    Pilot banka ≈ 9 bin kredi (hesap §4.8.3).
  - Chatterbox VC (MIT; çıktıya görünmez filigran gömer, A3).
  - Mevcut "TTS'i Veo süresine sığdırma" yöntemi (kıyasta çıta olarak).
  - `tts_dudak`: TTS + MuseTalk 1.5, yerel, fp16 [D-MT].
  - Seed-VC kod lisansı GPL-3.0 ve ağırlık lisansı belirsiz (A3). Netleşene kadar kıyasa girmez.
- **Ölçütler:** hedefe benzerlik; zarf gecikmesi; ASR WER artışı; F0 izinin korunması; fısıltı ve bağırma başarısı; dudak ofseti (S3); `tts_dudak` için görüntü uzmanının
  V2 kimlik ölçüsü ve klip başına süre.
- **Çıktı:** `_RAPOR/S1b_motor_kiyas.json`; `FILM_AYAR.json → saglayicilar.ses_donustur` sırası ve merdivendeki `tts_dudak` basamağının açık ya da kapalı olduğu.
- **Doğrulama:** İlk filmin P1'inin ilk 20 repliği aynı kıyasla bir kez daha işlenir. Bu yeni Veo klipleriyle yapılır ve kredi gerektirmez ([ÜRE] §8.4).
  Sonuç ders defterine `saglayici_notu` olarak yazılır.
- **RVC kazanırsa:** yalnız ana karakterler (≤ 4, RE ve [SEN2]) için banka ve eğitim yapılır. Eğitim arka planda ve gece koşar. Harcama `ai84_seri_kurulum_tavan`'dan düşer.
- **Kim:** B; motor sırası kararını kodun puan tablosu verir, AC `KARAR_DEFTERI.md`'ye yazar.

**SB4. Eksik efekt temini**
- **İş:** `ses_kutuphanesi.py --dizinle` (ilk çalıştırmada): mevcut 62 CC0 efekt ve yatak (AR) dizinlenir. `LISANS.txt` okunur. LUFS, süre, döngüye uygunluk, olay içeriği ve
  anlaşılır söz (ASR) ölçülür. `--eksik --indir`: Freesound API'de **yalnız CC0** arama yapılır (anahtar `AYARLAR/`'da). Lisans, kaynak adresi ve tarih kaydedilir.
  İndirme izni kullanıcıdan **kurulumda bir kez** alınır (`FILM_AYAR.json → indirme_izni.cc0_efekt`); film başına soru sorulmaz.
- **Çıktı:** `SES_KUTUPHANESI/<kategori>/…wav`, güncel `DIZIN.json`.
- **Geçme şartı:** planlanan her efekt bir dosyaya çözülür. CC0 (ya da açıkça ticari izinli) olmayan dosya kullanılmaz.
- **Kim:** B.

**SB5. Animatik sesi** (görseller G1'den geçince, animatik aşamasının içinde; çizelge T1) **(değişti)**
- **Girdi:** T1 çizelgesi ([KUR]), seçilmiş sesler, SA çıktıları, `SES_KUTUPHANESI`.
- **İş:**
  1. `seslendir.py --animatik`: bütün replikler **seçilmiş son sesle** okunur. Önbellek kullanılır; AI84 geçiriyorsa `previous_text/next_text` [D-EL] eklenir.
     Kelime zamanları stable-ts ile hizalanır. Gerçek süreler `SESLER/diyalog.json → replikler.<id>.tts` alanına yazılır. Süre kapısı S2.13 çalışır.
  2. `muzik.py --uret`: ipucu başına 3 aday üretilir (ACE-Step 2B turbo; motifli ipucunda motifin MIDI çalınışı "Cover/Refer audio" girdisi olur).
     Her aday ölçülür: BPM, ton, vokal yok, motif kroma benzerliği, kırpılma. En iyisi seçilir ve `MUZIK/KAYNAK_KAYDI.json`'a yazılır.
     Motif testini geçemeyen ipucunda ya da ACE-Step yoksa `midi_ornek` kullanılır.
  3. `ses_katmani.py --cizelge T1`: yataklar ve efektler **planlanan** anlara yerleştirilir → `KURGU/SES_CIZELGESI_T1.json`.
  4. `son_miks.py --animatik`: stemler toplanır, −14 LUFS önizleme yapılır (tek miks kodu, B15).
  5. **İşitsel döküm:** `kor_paket.py` animatik kipinde `isitsel_dokum()` işlevini çağırır. Her plan için "duyulan" satırı yazılır: konuşanın adı **yazılmaz**;
     "kadrajdaki kadın konuşuyor", "ekran dışı: kalın, boğuk erkek sesi" ya da "ekran dışı: daha önce duymadığın bir ses" yazılır. Efekt, müzik türü ve sessizlikler eklenir.
     Etiketler `ses_etiketi_tr`'den gelir; ad maskelemesi [SEN2] koduyla aynıdır.
- **Çıktı:** `SESLER/TTS/…`, `MUZIK/secilen/*.wav`, `MUZIK/KAYNAK_KAYDI.json`, `KURGU/SES_CIZELGESI_T1.json`, `ANIMATIK/ses_*.wav`, kör pakete işitsel döküm.
- **Geçme şartı:** sığmayan replik 0 (sığmayan yönetmene ya da hikâyeye `YENIDEN_YAZ` olarak döner: bölme, ekran dışına taşıma, 10 sn klip). S5, S6 ve S7'nin T1'de
  ölçülebilen maddeleri. Vokal 0 ve lisans kaydı tam.
- **Kim:** B. **Maliyet:** ilk tur ≈ 13–16 bin kredi (hesap §4.8.3); sonraki turlarda yalnız değişen replikler.

#### SC — Video sırasında

**SC1. Metin kapısı, her indirmede** (A14 içinde; dalga dalga) **(değişti: kurgu aşamasından buraya taşındı)**
- **Girdi:** az önce inen `SIRALI_VIDEO/NNN.mp4` (konuşma adımı olan plan), `_derlenir.replik_zaman`, replik metni, `tasidigi`, adlar.
- **İş (`ses_donustur.py --ayristir --hizala NNN`):**
  1. Ses 48 kHz'e alınır. BS-RoFormer (python-audio-separator, MIT; yedek demucs) ile konuşma ve diğer olarak ayrılır.
  2. Replik penceresi ±1 sn içinde VAD + serbest ASR ("Veo gerçekte ne söyledi") ve stable-ts hizalaması (bilinen metin zamanları) yapılır.
  3. WER hesaplanır. Sayılar ve kesme işaretleri normalleştirilir; adlar `ad_telaffuz` eşlemesiyle karşılaştırılır. Ad doğruluğu ölçülür. `tasidigi` olan replikte
     değişen ya da eksik içerik kelimesi işaretlenir.
  4. **Hızlı konuşan yüz denetimi:** replik penceresinin %25, %50 ve %75 karelerinde her yüzün ağız açıklığı ve kimliği ölçülür (`olcum/dudak.py`, `olcum/kimlik.py`).
     Ağzı en çok oynayan yüz replik karakteri değilse HATA verilir (dinleyen konuştu).
  5. Veo konuşma hızı ölçülür.
- **Çıktı:** `SESLER/ayrik/NNN_{konusma,diger}.wav`, `SESLER/hizalama/NNN.json`, `_RAPOR/S2m_D<dalga>.json`; gerekiyorsa `YENIDEN_URET.json` maddesi
  (`kaynak_kapi: "S2"`, şablonla CORRECTION) ya da `hikaye-yazari` `replik_kabul` görevi.
- **Geçme şartı:** S2.1–S2.6. Yeniden çekim **aynı dalgaya** girer; Memmet'in temposu ve "uyarıda DUR" kuralı aynen geçerlidir.
- **Kim:** B (+ gri bantta A `hikaye-yazari` replik_kabul). Betik Flow'a dokunmaz; yalnız inen dosyayı okur.

#### SD — Video sonrası (parti parti)

**SD1. Dönüşüm, TTS ve ses merdiveni** (A15) **(değişti)**
- **Girdi:** SC1 çıktıları, evren sesleri (model, merkez, F0 istatistiği, referans), önbellekteki TTS.
- **İş (`seslendir.py --parti N`, yönlendirici):**
  - `veo_donustur`: konuşma kanalı **yalnız hizalanmış söz pencerelerinde** (±0,1 sn) dönüştürücüye girer; dışı susturulur, yaratık sesi ya da gürültü insan sesine çevrilmez.
    F0 kaydırması hesaplanır (`12·log2(F0_hedef / F0_kaynak)` yarım ton, yuvarlanır). Motor zinciri sırayla denenir.
  - `tts`: önbellekteki TTS alınır; gerekirse ±%8'e kadar esnetilir (fazlası yeniden okutulur).
  - `veo_ham`: yalnız seviye eşitlenir.
  - Her sonuç S2.7–S2.12 ile ölçülür. Başarısız replik `ses_karar.py`'ye gider (merdiven §4.8.3).
- **Çıktı:** `SESLER/donusum/<replik>.wav`, `SESLER/tts/…`, `SESLER/diyalog.json` v2, `_RAPOR/S2_P<n>.json`.
- **Geçme şartı:** S2 HATA = 0 ya da her HATA için merdivende yazılı bir karar.
- **Kim:** B.

#### SE — Kurgu (T2, T3; parti parti)

**SE1. Dudak denetimi (S3)** — kurgu planının **her** değişiminden sonra, taslak verilmeden önce (BK 5.1.9)
- **Girdi:** `KURGU_PLANI.json` (`kullanim`, `kaynak_klip`, `diyalog[]` yerleşimi), `SESLER/diyalog.json`, klipler.
- **İş (`dudak_denetim.py`):** Plan penceresinde MediaPipe yüz noktalarından ağız açıklığı dizisi çıkarılır (blendshape `jawOpen`, bellekten). Son diyalog sesinin zarfıyla
  korelasyonla ofset ve güven hesaplanır. Konuşan yüzün kimliği replik karakteri mi? Ekran dışı replik ya da köprü replik sırasında kadrajdaki ağız oynuyor mu?
  Bölünmüş klipte atlanan aralık bir sözün ortasına denk geliyor mu? İsteğe bağlı ikinci görüş SyncNet (yalnız ölçüm). Ağız dizisi kurgucunun B9 denetimine de verilir.
- **Çıktı:** `_RAPOR/S3_dudak_P<n>.json`.
- **Geçme şartı:** S3. Yol A'da dudak ve ses aynı klipten geldiği için ofset yalnız dönüşüm gecikmesinden (S2.8) ve **yerleşimden** doğar. S3 asıl olarak kurgu yerleşim
  hatasını ve yanlış konuşanı yakalar.
- **Kim:** B. Yerleşim hatası `kurgu_uygula.py` düzeltmesine, konuşma hatası merdivene gider.

**SE2. Diyalog eşitleme ve mekân akustiği (S4)**
- **İş (`diyalog_esitle.py`):** her replik K-ağırlıklı ölçülür; 0,4 sn'den kısa replikte kısa süreli en yüksek değer kullanılır (A3 A3). Hedef LUFS'a **tek kazanç** verilir
  (tepe normalleştirme yok). Mekânın oda yanıtı eklenir (boyuttan sentetik, pyroomacoustics MIT, bellekten). Plan ölçeğine göre uzaklık uygulanır (geniş plan daha yankılı).
  Aynı karakterin `veo_donustur` ve `tts` replikleri arasında tını eşleme EQ'su yapılır.
- **Çıktı:** `SESLER/esit/…`, `_RAPOR/S4_diyalog_P<n>.json`. **Geçme şartı:** S4. **Kim:** B.

**SE3. Ambiyans ve efekt (S5)** **(değişti: çıktı `SES_CIZELGESI.json`)**
- **İş (`ses_katmani.py --cizelge T2`):**
  - Sahne grubu başına tek yatak; döngü, çapraz geçiş ve ses köprüsüyle yerleşir (RE:ambiyans_capraz_gecis_sn, RE:ses_koprusu_sn). `devam` geçişinde yatak kesintisiz sürer.
  - Efekt olayları önce **klibin kendi efekt sesindeki** başlangıç anına oturtulur. Veo adım ve kapı seslerini görüntüyle senkron üretir; bu ses zaman referansıdır.
    Temizse klibin kendi sesi kapılı biçimde kullanılır, değilse kütüphane efekti o ana konur.
  - Yaratık sesi her zaman evren kitinden gelir. Zamanı yine Veo'nun o penceredeki ses başlangıcından alınır.
  - Nesne sürekli sesleri (yanan fener) dünya defterinden **çalışma anında türetilir**; plana yazılmaz.
  - Yeniden çekilen ya da yeniden kırpılan plan klip özetinden (SHA-1) tanınır ve efekti yeniden kurulur.
- **Çıktı:** `KURGU/SES_CIZELGESI.json` (ambiyans, efekt), `KURGU/STEMS/{ambiyans,efekt}.wav`, `_RAPOR/S5_P<n>.json`. **Geçme şartı:** S5. **Kim:** B.

**SE4. Müzik yerleşimi (S6)**
- **İş (`muzik.py --yerlestir`):** parça ölçü (bar) sınırından kesilir. Vuruş noktası ilgili olaya ±1 kare oturtulur; en çok ±%3 esnetme yapılır. Sığmazsa ipucu yeniden üretilir
  (yerel, 0 kredi). Giriş 1–3 sn, çıkış 2–4 sn olur. Diyalog pencerelerinde otomatik kısma yapılır (diyalogdan ≥ 12 dB aşağı). Planlı müziksiz yerler boşaltılır.
  Leitmotifin varlığı sesten ölçülür.
- **Çıktı:** `SES_CIZELGESI.json → muzik[]`, `KURGU/STEMS/muzik.wav`, `_RAPOR/S6_P<n>.json`.
- **Geçme şartı:** S6. Başarısız ipucu müzik kipinin aynı örneğine döner (revizyonu aynı yazar yapar). **Kim:** B (+ A müzik).

**SE5. Miks (S7)**
- **İş (`son_miks.py`):** dört stem (diyalog, efekt, ambiyans, müzik) toplanır. Bütünleşik ses ölçülür; **tek doğrusal kazanç** + 4× aşırı örneklemeli gerçek tepe sınırlayıcı
  uygulanır; yeniden ölçülür. LRA, mono uyumluluk, planlanmamış sessizlik ve kırpılma ölçülür. ASR ile her replik son miksten yeniden tanınır (B6).
  `kurgu_render.py` önizleme için bu işlevi çağırır (İ-1).
- **Çıktı:** `KURGU/STEMS/*.wav`, `KURGU/onizleme_ses.wav`, `_RAPOR/S7_P<n>.json`; kurgu seyircisinin paketi için son miksten çıkarılmış işitsel döküm.
- **Geçme şartı:** S7. **Kim:** B.

**SE6. Kurgu değişince** (kurgucu düzeltmesi, kesme turu, yeniden çekim, kullanıcının CapCut düzenlemesi)
- **İş:** yalnız etkilenen planlarda ve sahne gruplarında SE1–SE5 yeniden çalışır. Kullanıcının kararı kilitlidir ([KUR] `kaynak: kullanici`). Taslak yeniden kurulup
  kurulmayacağı kurgucunun karar ağacına göredir ([KUR] §8.7).
- **Kim:** B.

#### SF — Yayın ve öğrenme

**SF1. Yayın sesi (S8)**
- **İş (`son_miks.py --final`):**
  - Son video ffmpeg ana kaydıysa ses master'ı **video yeniden kodlanmadan** yerleştirilir (mux).
  - Kullanıcı CapCut'tan dışa aktardıysa: `TASLAK_FARK.json → geri_uretilemeyen` içinde elle ses ayarı yoksa master yerleştirilir. Varsa kullanıcının sesi **korunur**;
    dışa aktarılan ses yalnız ölçülür, gerekirse tek doğrusal kazanç ve tepe sınırlayıcı uygulanır, yeniden karıştırılmaz (BK 5.3.3).
  - Shorts için stemlerden ayrı miks yapılır: diyalog öne, müzik geri, −14 LUFS, mono denetimi.
  - Jenerik ve seri kancası ana temayla çalar.
  - `KAYNAK_KAYDI.json` yayın paketine konur. Content ID ön kontrolü yayın uzmanının **onaylı ve isteğe bağlı** özel yükleme adımındadır.
- **Çıktı:** `YAYIN/<film>_final.mp4` sesi, `YAYIN/shorts_*.mp4` sesleri, `_RAPOR/S8_yayin_ses.json`. **Geçme şartı:** S8. **Kim:** B.

**SF2. Ders defteri ve evren güncellemesi**
- **İş:** S0–S8 raporları ve merdiven kararları ortak `ders_defteri.kaydet()` ile kaydedilir (§2.5). Yeni sesler, motifler, mekân yatakları, yaratık kitleri ve nesne imza sesleri
  `evren.py` ile evrene yazılır. Eşik kalibrasyonu için ölçüm dağılımları saklanır.
- **Kim:** B + `ders-editoru` (terfi). AC kuralları `KARAR_DEFTERI.md`'ye yazar.

### 4.3 Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) **(değişti)**

İlkeler: tek iş, en az araç, makinece okunur çıktı, her görev yeni örnek (yalnız aynı kipin revizyonu `SendMessage` ile aynı örnekte). Ölçüm ve ses işleme **betikte**
(A3 B4). Claude duyamadığı için hiçbir ajandan "dinle ve karar ver" istenmez; ajan ölçüm JSON'larını ve meta veriyi okur. Ajanlarda Bash yoktur; denetim SubagentStop kancasındadır ([MİM]).

#### 4.3.1 `ses-tasarimcisi` (tek ses ajanı; mevcut `muzik-supervizoru.md` taslağının yerine)

| Alan | Değer |
|---|---|
| model / efor | `opus` (`claude-opus-5-5`), `effort: high` (kullanıcı kuralı H/ajan-opus-yuksek; mevcut taslak `sonnet` idi) |
| araçlar | `Read, Write, Edit, Glob, Grep` (yazar rolü, [MİM] §5.7); okuma ve yazma görev klasörüne bağlıdır |
| kipler | `kadro` · `tasarim` · `muzik` (her biri ayrı şablon ve ayrı GIRDI dilimi) |
| `kadro` görevi | SA1 profiller, `veo_ses_tarifi`, `etiket_ailesi`, `ses_etiketi_tr` taslağı; SB2'de yakın puanlı adaylardan gerekçeli seçim |
| `kadro` okur | `HIKAYE.json` karakter dilimi, evren `hikaye.json` (bölge/halk, sözlük), mevcut evren `ses.json`'ları, `_RAPOR/S1_ses_secim.json` (seçimde), §4.5.3 şeması, ses dersleri |
| `tasarim` görevi | SA2: taslağı inceler ve düzeltir; sessizlik, yaratık sesi, dış katman, J/L önerisi, eksik efekt |
| `tasarim` okur | sahne grubu dilimi (`SAHNELER` + defter + mekân/nesne `ses.json` + `DIZIN.json` özeti), taslak `SES_<S>.taslak.json`, Z §5, ses eşikleri, ses dersleri |
| `muzik` görevi | SA3: leitmotif notaları, ipucu listesi; S6 HATA'larında revizyon |
| `muzik` okur | duygu haritası, vuruşlar, plan dilimi (yoğunluk, hedef duygu, vuruş, sessizlik), T0/T1 çizelgesi, `leitmotifler.json`, Z §1.3, §5.3–5.4, müzik eşikleri |
| çıktısı | `CIKTI/SES_PROFILLERI.json` + `SES_KADROSU.md` · `CIKTI/SES_<S>.json` + `EKSIK_EFEKTLER.json` · `CIKTI/muzik_listesi.json` + `MUZIK_PLANI.md`; betik `35_SES/`'e taşır |
| dönüş | ≤ 5 satır: çıktı yolu + `OZET | …` (ör. `OZET | sahne: S12 | efekt: 23 | eksik: 2 | sessizlik: 3 | S0_HATA: 0`) |

**Gövdenin en üstünde duracak kurallar** (sıkıştırmadan sonra da görünsün):
1. Sesi duyamazsın. Karar yalnız ölçüye, meta veriye ve yazılı kurallara dayanır. "Kulakla bakılır" yazmazsın.
2. `veo_ses_tarifi`: ≤ 12 kelime; tını/perde + cinsiyet + aksan; yaş ve filtre sözcüğü yok. Aksan seçilen sesin aksan etiketiyle aynıdır.
3. `flow_sound`: "Sound:" ile başlar, "No music." ile biter, ≤ 12 kelime, müzik/şarkı/vokal sözcüğü yok.
4. Ambiyans için müzik modeli (Lyria vb.) kullanılmaz; yatak gerçek CC0 kayıttır (BK 5.1.2). Klibin kendi ortam sesi yatak olmaz.
5. Yolu sen seçmezsin; kod önerir. Değiştireceksen `yol_neden` yazarsın.
6. Müzik sözsüzdür; istemde sanatçı ya da film adı yazılmaz; leitmotif notalarla yazılır.
7. Replik metnine, `teslim`'e, kadraja, eylem zincirine dokunmazsın. Gerekiyorsa `istekler` listesine yazarsın (sahibine gider).
8. Kullanıcıya soru yoktur.

#### 4.3.2 Başka uzmanın sahip olduğu, ses akışında görev alan ajanlar
- **`hikaye-yazari` — `replik_kabul` kipi** (önerim; sahibi senarist): Veo'nun söylediği metin gri banttaysa (S2.2) karar verir. Yeni örnektir. Yalnız senaryo metni, duyulan metin,
  `tasidigi`, önceki ve sonraki replik GIRDI'ye konur. Çıktı: `{karar: kabul|ret, gerekce}`. Kabulde `duyulan_metin` altyazıya geçer.
  Ret ya da `tasidigi` kaybı → yeniden çekim ([SEN2] İ8 ile aynı sonuç). Sesi duymasına gerek yoktur; ASR metni yeterlidir.
- **`kurgucu`:** ses kaynaklı kurgu çözümlerini uygular (ağzı görünmeyen kırpma, ekran dışına taşıma, J/L).
- **`yonetmen` (onarım kipi):** ses kaynaklı plan değişikliği (repliği tepki planının üstüne taşıma, kadraj değişikliği).
- **`habersiz-seyirci`:** işitsel dökümü okur, sesi bilmez. Ona ad değil ses etiketi verilir.
- **`ders-editoru`:** ses dersleri dahil terfi kararları.

#### 4.3.3 Ajan olmayan işler (bilinçli olarak betikte)
Ses seçimi ölçümü, telaffuz testi, motor kıyası, ayrıştırma, hizalama, metin kapısı, dönüşüm, merdiven kararları (`ses_karar.py`), LUFS, dudak ölçümü, ambiyans ve efekt
yerleşimi, müzik üretimi ve yerleşimi, miks, işitsel döküm. Hepsi deterministik ya da model çalıştıran betiktir (A3 B4).
**İsteğe bağlı `dinleyici` sağlayıcısı** (ajan değil): ses girdisi kabul eden bir model API'si (ör. Gemini). Yalnız BAYRAK durumlarında seçenekli sorulara cevap verir
("Bu ses A) İngiliz B) Amerikan C) İskoç aksanlı mı?"). Anahtar yoksa atlanır, madde "ölçülemedi" olur. Ana hat buna bağlı değildir.
"Hiçbir model kendi çıktısını onaylamaz" ilkesine uyar (A1 B4).

### 4.4 Beceri (skill) tarif adımları — kendi alanım **(değişti)**

**Yer:** `film-yap` becerisinin altında tek seviye bağlantılı başvuru dosyası `reference/ses.md` (≤ 300 satır, başta içindekiler; A3 B4). Ana Claude bu dosyayı yalnız
`film.py sonraki` bir ses görevi verdiğinde ya da takıldığında okur. Ses aşamaları ayrı beceri değildir; `film.py`'nin görev defterinde aşamadır ([MİM] §4).
Ses ajanının istemleri `sablonlar/A08_ses-tasarimcisi_{kadro,tasarim,muzik}.md` şablonlarından betikle üretilir. Sayılar şablona eşik dosyasından basılır.

#### 4.4.1 `reference/ses.md`'nin ilk 40 satırı (kurallar)
1. Ses kararları ölçüyle verilir. Ana Claude ses dosyası açmaz ve "dinledim" demez.
2. Ambiyans için müzik modeli yok; yatak CC0 kayıttır. Klibin ortam sesi yatak değildir; yalnız kapılı efekttir.
3. Replikler tepe değerine göre değil, LUFS'a göre eşitlenir. Bütün miksler `son_miks.py`'dendir.
4. Wav2Lip ve ticari olmayan lisanslı model (MusicGen ağırlıkları, InsightFace modelleri, F5-TTS hazır modelleri) kullanılmaz (A3). Seed-VC lisansı netleşmeden kullanılmaz.
5. Müzik sözsüzdür; kaynak kaydı olmayan parça yayına girmez; elle müzik üretimi yoktur.
6. Dudakları oynayan karakterin üstüne başkasının repliği konmaz (BK 5.1.8).
7. Ses kaynaklı yeniden çekim normal kuyruktan gider. Flow uyarısında DUR kuralı aynen geçerlidir (kesin karar 5). Ses betikleri Flow'a hiçbir şey göndermez.
8. Anahtarlar yalnız betiklerce `AYARLAR/`'dan okunur. Ana Claude ve ajanlar okumaz (kanca zorlar).
9. Kullanıcıya soru yoktur. `SES_SECIM.html` ve animatik bilgi içindir, onay kapısı değildir. CC0 indirme izni kurulumda bir kez alınır.
10. Bir ölçüm yapılamıyorsa sonuç `ÖLÇÜLEMEDİ` olur ve BAYRAK sayılır; asla GEÇ değildir.

#### 4.4.2 Ses görevleri (görev defterinde; ana Claude yalnız `film.py sonraki` ne derse onu yürütür)

| Görev | Tür | Ne çalışır | Ortam | Kredi |
|---|---|---|---|---|
| SA1 | ajan | `ses-tasarimcisi` kadro → SubagentStop: `ses_plani.py --profil-denetle` | bulut/yerel | yok |
| SA2 | betik + ajan (sahne grubu başına, paralel) | `ses_plani.py --taslak S<k>` → `ses-tasarimcisi` tasarım → SubagentStop: `ses_plani.py --denetle S<k>` | bulut/yerel | yok |
| SA3 | ajan | `ses-tasarimcisi` müzik → SubagentStop: `muzik.py --kagit` | bulut/yerel | yok |
| SA4 | betik | `ses_plani.py --denetle --tum` → (A09) `istem_derle --hareket`, `istem_denetim.py` | bulut/yerel | yok |
| SB0 | betik | `ses_olcum.py --kontrol` | yerel | yok (`estimate` ücretsiz) |
| SB1 | betik | `ses_sec.py --telaffuz` | yerel | AI84 ≈ 1,8 bin |
| SB2 | betik (+ ajan) | `ses_sec.py --ara --olc --oku --puanla` → (yakın puanda) `ses-tasarimcisi` kadro → `ses_sec.py --sec` | yerel | AI84 ≈ 5 bin |
| SB3 | betik | `ses_kiyas.py` (seri başında) ; RVC seçilirse `ses_sec.py --banka`, `ses_donustur.py --egit` | yerel | AI84 0–36 bin, bir kez |
| SB4 | betik | `ses_kutuphanesi.py --dizinle --eksik --indir` | yerel | yok |
| SB5 | betik | `seslendir.py --animatik` ; `muzik.py --uret` ; `ses_katmani.py --cizelge T1` ; `son_miks.py --animatik` ; `kor_paket.py --animatik` | yerel | AI84 ≈ 13–16 bin |
| SC1 | betik (+ ajan) | `ses_donustur.py --ayristir --hizala NNN` (indirme sonrası kancası) → gri bantta `hikaye-yazari` replik_kabul | yerel | yok (yeniden çekim kuyruğa) |
| SD1 | betik | `seslendir.py --parti N` → `ses_karar.py` | yerel | merdivene göre |
| SE1–SE5 | betik | `dudak_denetim.py` → `diyalog_esitle.py` → `ses_katmani.py --cizelge T2` → `muzik.py --yerlestir` → `son_miks.py` | yerel | yok |
| SE6 | betik | aynı zincir, yalnız etkilenenler | yerel | yok |
| SF1 | betik | `son_miks.py --final` ; `son_miks.py --shorts` | yerel | yok |
| SF2 | betik + ajan | `ders_defteri.py` ; `evren.py --film-sonu` ; `ders-editoru` | herhangi | yok |

#### 4.4.3 Geri besleme döngüsü ve durma koşulları
- Her kapı: **ölç → rapor → karar (merdiven ya da sahibi) → düzelt → yeniden ölç**. Kâğıtta en çok 2 öz-denetim turu (SubagentStop, [MİM]); kurguda en çok 3 tur (RE:kurgu_tur_max).
- Eşiğe ulaşılamazsa susulmaz: eksik açıkça raporlanır (BK §7.13 "yüzüne vur"). Hangi replik, hangi ölçü, neden, hangi basamak denendi, kalan seçenek ve maliyeti yazılır.
- Hat yalnız şu durumlarda durur: AI84 kredisi ya da bütçe tavanı (çıkış BÜTÇE), Flow uyarısı (yeniden çekim kuyruğu durur), lisansı belirsiz bir kaynağın kullanılması
  gerekiyorsa, kurgu turu tavanı doldu ve KRİTİK kaldıysa.
- Kullanıcıya giden ses mesajları bilgi cümlesidir. Örnek: "Ses kadrosu seçildi: 6 karakter, en yakın iki ses arası benzerlik 0,52."

#### 4.4.4 Değerlendirme senaryoları (beceri testi, A3 B4: en az 3)
1. **Yeni seride ilk film:** SA1 → SB3 kıyası dahil bütün ses görevleri sahte sağlayıcılarla sırayla çıkar; animatik sesi seçilmiş seslerle kurulur.
2. **Evrendeki karakterlerle ikinci film:** SA1 karakterleri yeniden profillemez, SB2 seçim yapmaz, SB3 koşmaz; yalnız yeni karakter seçilir.
3. **Yalnız müziği yeniden yap:** SA3 ve SE4 çalışır, diyalog dosyalarına dokunulmaz, miks yeniden yapılır.
4. **Kullanıcı CapCut'ta 5 plan sildi ve müzik kanalını −3 dB yaptı:** SE6 yalnız etkilenen sahnelerde koşar; SF1 kullanıcının müzik ayarını korur.
5. **Veo bir adı yanlış okudu:** SC1 HATA → CORRECTION'lı yeniden çekim; `istem_kalibi` dersi sonraki kliplere uygulanır.

### 4.5 Veri şeması / plan alanları (JSON örneğiyle) **(değişti)**

**Uyumluluk:** Mevcut alanlar (`karakterler.<id>.ses` = voice_id, `ses_adi`, `replik {karakter, metin, cumleler}`) değişmez; betik bunları evrenden doldurur.
Eski filmler çalışmaya devam eder. Bütün hatta ses örnekleme hızı **48 kHz**'tir (bugünkü kod 44,1 kHz kullanıyor; video sesinde 48 kHz yaygındır, bellekten).

#### 4.5.1 Ses alanlarının sahipliği (alan başına; [YÖN2] §4.5.2 tablosuna eklenir)

| Alan | Sahibi | Yazan |
|---|---|---|
| `replik.teslim`, `replik.tasidigi` | senarist | `hikaye-yazari` |
| `replik.veo_metin` | ses | `ses_plani.py` (yalnız S2.3 dersinden sonra; varsayılan `null` = `metin`) |
| `zanaat.ses.{diyalog.yol, diyalog.yol_neden, diyalog.seviye_ozel, efektler[], flow_sound, sessizlik, dis_katman_db}` | ses | taslak `ses_plani.py`, düzeltme `ses-tasarimcisi` tasarım |
| `sahne_gruplari.<S>.ses` | ses | aynı |
| `_derlenir.{agiz_gorunur, dinleyen_agiz, seviye, ton_fiili_en, replik_zaman, replik_tts_sn, muzik_ipucu}` | kod | `plan_birlestir.py`, `kroki.py`, `ses_plani.py` |
| `karakterler.<id>.ses`, `ses_adi` (eski alanlar) | betik | evrenden derlenir |

#### 4.5.2 `teslim` sözlüğü (`veri/plan_sozlukleri.json → teslim`; tek kaynak)

| `teslim` | `en_fiil` (istemde) | `seviye` (RE:diyalog_lufs sınıfı) | `tts_etiket` | Not |
|---|---|---|---|---|
| `fisilti` | whispers | fisilti (−24) | `whispers` (tahmin; v4 etiket listesi doğrulanmadı) | konuşma hızı 2,0 k/sn (RE:konusma_hizi_agir_kelime_sn) |
| `yumusak` | says quietly | yumusak (−21,5) | `softly` (tahmin) | |
| `normal` | says | normal (−19,5) | — | |
| `soguk` | says coldly | normal (−19,5) | `coldly` (tahmin) | |
| `bagirma` | shouts | bagirma (−17) | `shouting` (tahmin) | |
| (genişletme) `aci`, `yalvaran`, `sert` … | says bitterly / pleads / says firmly | dört sınıftan biri **zorunlu** | sözlükte | yeni değer sözlüğe test ile eklenir |

`_derlenir.ton_fiili_en` ve `_derlenir.seviye` bu tablodan gelir. Ses yalnız gerekçeyle `zanaat.ses.diyalog.seviye_ozel` yazar (ör. "fısıltı ama karşıdakinin
duyması gereken mesafe").

#### 4.5.2b Konuşan plan istem kalıbı (yönetmenin `--hareket` modülü derler; içerik sesin)
`{Ad} {ton_fiili_en}, {veo_ses_tarifi}: "{veo_metin|metin}"` → `Mara says coldly, in a low, husky female voice with a northern English accent: "It's late, Captain. What do you want?"`
Tek kişili kadrajda özne yazılmaz ([YÖN2] kuralı): `Says coldly, in a low, husky female voice with a northern English accent: "…"`.

#### 4.5.3 Plan düzeyi: `SAHNELER.json → sahneler[i]` (S12 örneği, [YÖN2] §4.5.12 ile aynı planlar; yalnız ses ilgili alanlar)
```json
[
 {"no": 121, "sira": 121, "parti": 1, "referans": ["mara", "voss"],
  "replik": {"id": "R0121", "karakter": "mara", "metin": "It's late, Captain. What do you want?",
             "cumleler": [{"en": "It's late, Captain.", "tr": "Saat geç oldu, Kaptan."}, {"en": "What do you want?", "tr": "Ne istiyorsun?"}],
             "teslim": "soguk", "tasidigi": ["o03"], "veo_metin": null},
  "zanaat": {
   "plan_tipi": "diyalog", "kamera": {"kurulum": "K2", "kadraj": "OU"},
   "eylem_zinciri": [
    {"id": "a1", "bas": 0.5, "bit": 1.8, "ozne": "mara", "tur": "mikro", "fiil": "cene_kaldirir", "govde": "bas", "olcu": "hafif"},
    {"id": "a2", "bas": 2.0, "bit": 5.4, "ozne": "mara", "tur": "konusma", "fiil": "konusur", "replik": "R0121", "cumleler": [0, 1]}],
   "ekran_disi_ses": null,
   "kesme": {"tip": "L", "ses_tasma_sn": 1.2},
   "ses": {
    "diyalog": {"yol": "veo_donustur", "yol_neden": null, "seviye_ozel": null},
    "efektler": [],
    "flow_sound": "Sound: torch flame crackling, wind over snow. No music.",
    "sessizlik": null,
    "dis_katman_db": null}},
  "_derlenir": {"agiz_gorunur": "tam", "dinleyen_agiz": "kapali", "seviye": "normal", "ton_fiili_en": "says coldly",
                "replik_zaman": {"bas": 2.0, "bit": 5.4}, "replik_tts_sn": 3.2, "muzik_ipucu": "M06"}},

 {"no": 122, "sira": 122, "parti": 1, "referans": ["voss"], "replik": null,
  "zanaat": {
   "plan_tipi": "tepki", "kamera": {"kurulum": "K5", "kadraj": "Y"},
   "eylem_zinciri": [
    {"id": "a1", "bas": 0.5, "bit": 2.0, "ozne": "voss", "tur": "mikro", "fiil": "bakis_kaydirir", "hedef": "ocak_atesi"},
    {"id": "a2", "bas": 2.0, "bit": 3.5, "ozne": "voss", "tur": "mikro", "fiil": "cene_sikar"}],
   "ekran_disi_ses": {"replik": "R0121", "karakter": "mara", "kaynak": "plan:121", "bas_sn": 0.0, "sure_sn": 1.2},
   "ses": {
    "diyalog": null,
    "efektler": [],
    "flow_sound": "Sound: wind, torch flame crackling. No music.",
    "sessizlik": {"tip": "muziksiz", "bas_sn": 1.2, "sure_sn": 1.6, "neden": "sok_sonrasi"},
    "dis_katman_db": null}},
  "_derlenir": {"agiz_gorunur": "yok", "dinleyen_agiz": "kapali"}},

 {"no": 124, "sira": 124, "parti": 1, "referans": ["mara"], "replik": null,
  "zanaat": {
   "plan_tipi": "ekleme", "kamera": {"kurulum": "K6", "kadraj": "D"},
   "eylem_zinciri": [
    {"id": "a1", "bas": 0.5, "bit": 2.5, "ozne": "mara", "tur": "fiziksel", "fiil": "el_kaydirir", "govde": "sol_el", "yon": "asagi", "hedef": "surgu", "olcu": "15cm"},
    {"id": "a2", "bas": 2.5, "bit": 4.0, "ozne": "mara", "tur": "fiziksel", "fiil": "kavrar", "govde": "sol_el", "el_sekli": "kiskac", "hedef": "surgu"}],
   "ekran_disi_ses": {"replik": "R0123", "karakter": "voss", "kaynak": "plan:123", "bas_sn": 0.0, "sure_sn": 1.0},
   "ses": {
    "diyalog": null,
    "efektler": [
     {"id": "E124a", "adim": "a1", "kategori": "el_surtunme", "malzeme": "ahsap", "an": "yayil", "kaynak_tercih": "kutuphane",
      "yedek": "SES_KUTUPHANESI/efekt/el_ahsap_kayma_01.wav", "seviye_db_diyaloga_gore": -14},
     {"id": "E124b", "adim": "a2", "kategori": "metal_temas", "malzeme": "demir", "an": "son", "kaynak_tercih": "klip",
      "yedek": "EVREN/EMBERFALL/nesneler/surgu/ses/temas_01.wav", "seviye_db_diyaloga_gore": -9}],
    "flow_sound": "Sound: hand sliding on wood, soft iron click, muffled wind outside. No music.",
    "sessizlik": null,
    "dis_katman_db": {"dis_ruzgar_kar": 4}}},
  "_derlenir": {"agiz_gorunur": "yok", "dinleyen_agiz": "kapali"}}
]
```

| Alan | Değerler | Not |
|---|---|---|
| `ses.diyalog.yol` | `veo_donustur` · `tts` · `veo_ham` | Konuşma adımı olan planda dolu; diğerlerinde `null`. Ekran dışı taşma yol değildir (`ekran_disi_ses.kaynak`) |
| `ses.efektler[].an` | `bas` · `son` (temas anı) · `yayil` (adım boyunca, ör. adım sesleri) · `ofset:<sn>` | Fiilden önerilir |
| `ses.efektler[].kaynak_tercih` | `klip` (Veo'nun kapılı sesi; zaman referansı her durumda klip) · `kutuphane` · `kit` (yaratık, evren) | `klip` seçilse de `yedek` zorunlu |
| `ses.flow_sound` | "Sound:" … "No music." arası ≤ 12 kelime | Efekt listesinden derlenir; müzik sözcüğü yok |
| `ses.sessizlik` | `{tip: muziksiz\|mutlak, bas_sn, sure_sn, neden}` | Z §5.3, RE:vurgu_sessizlik_sn |
| `ses.dis_katman_db` | `{katman_adı: dB}` | İçeriden dışarı bakan plan (Z §5.2) |
| `fiziksel` adımı olup efekti olmayan | `efektler[]` içinde `{adim, sessiz_adim: true, neden}` | S0.7 |

#### 4.5.4 Sahne grubu: `SAHNELER.json → sahne_gruplari.<S>.ses`
```json
"S12": {"ses": {
  "yatak": {"dosya": "SES_KUTUPHANESI/yatak/DIS_ruzgar_kar_03.wav", "seviye_lufs": -34.0, "dongu": true,
            "katmanlar": [
             {"ad": "mesale_alev", "dosya": "SES_KUTUPHANESI/yatak/ATES_mesale_01.wav", "kazanc_db": -6, "kaynak": "defter:nesneler.mesale.durum=yanik"},
             {"ad": "ic_ocak", "dosya": "SES_KUTUPHANESI/yatak/IC_ocak_02.wav", "kazanc_db": -14, "kaynak": "defter:mekan_durumu.ocak_atesi=yanik"}]},
  "oda_yaniti": "EVREN/EMBERFALL/mekanlar/mara_kulubesi/ses/oda_ir.wav",
  "gecis": {"capraz_sn": 0.8, "one_alma_sn": 0.5, "zaman_surekli_onceki": false},
  "kalabalik": null}}
```
`katmanlar[].kaynak` hangi defter olgusundan türediğini yazar. Defter değişirse (meşale söndü) S0.11 katmanın kalkmasını ister. Bu, ses zıplamasının kâğıttaki denetimidir.

#### 4.5.5 Karakter sesi: `35_SES/SES_PROFILLERI.json` ve kalıcı `EVREN/<SERI>/karakterler/<id>/ses.json`
```json
{
 "karakter": "mara", "seri": "EMBERFALL", "surum": 1, "durum": "kilitli", "tur": "insan",
 "profil": {"cinsiyet": "kadin", "yas_bandi": "orta", "aksan": "british", "aksan_ayrinti": "northern_english",
            "perde": "orta_dusuk", "tini": ["low", "husky"], "tempo": "olculu", "enerji": "sakin_kararli",
            "kaynak": "HIKAYE.json karakterler.mara.ses_karakteri"},
 "veo_ses_tarifi": "in a low, husky female voice with a northern English accent",
 "ses_etiketi_tr": "alçak, boğuk kadın sesi",
 "etiket_ailesi": ["whispers", "softly", "firmly"],
 "secim": {"saglayici": "ai84", "voice_id": "<voice_id>", "ses_adi": "<paylaşılan sesin adı>", "kaynak": "paylasilan",
           "accent_etiketi": "british", "notice_period_gun": 90, "model": "eleven_v4", "ayarlar": null, "seed": null,
           "tarih": "2026-10-24", "puan": 0.82, "karar_veren": "kod (fark ≥ 0,03)",
           "adaylar": [{"voice_id": "<…>", "puan": 0.77, "elenme": "kadro ayırt ediciliği: voss ile 0,66"}]},
 "ad_okuma": {"Mara": "GEC", "Voss": "GEC"},
 "olcum": {"f0_medyan_hz": 182.0, "f0_p10_p90_hz": [150.0, 241.0], "hiz_kelime_sn": 2.4,
           "merkez": "ses/merkez.npy", "benzerlik_esigi": 0.70},
 "donusum": {"motor": "openvoice", "referans": "ses/referans_60sn.wav", "model": null, "dogrulama_benzerlik": 0.78},
 "banka": null,
 "filmler": ["EMBERFALL_F2"],
 "lisans_notu": "Paylaşılan ses; sahibi kaldırabilir. Sigorta: referans kayıt + (RVC seçildiyse) banka ve model."
}
```
- `ayarlar` ve `seed`, AI84'ün bunları ilettiği ilk kurulumda sınanınca doldurulur. `null` = bilinmiyor; uydurulmaz.
- RVC seçilirse: `"banka": {"klasor": "ses/banka/", "sure_sn": 610, "cumle": 140, "ai84_kredi": 9100}`, `"donusum": {"motor": "rvc", "model": "ses/rvc/mara_v1.pth", …}`.
- **Yaratık** (`tur: yaratik`): `"kit": {"evre1": {"nefes": [...], "cigirma": [...], "homurtu": [...]}, "evre2": {...}}`. Kaynak CC0 hayvan kayıtlarıdır; katmanlanır,
  perde ve formant kaydırılır. Her dosyanın lisansı kayıtlıdır. Yaratık hiçbir zaman dönüştürücüye ya da `veo_ham`'a girmez.
- Figüran `veo_ham` ise yalnız `{"karakter": "nobetci_1", "rol": "figuran", "yol": "veo_ham", "kural": "tek replik; ana karakterlere benzerlik < 0,60"}` yazılır.

#### 4.5.6 Mekân ve nesne sesi: `EVREN/<SERI>/mekanlar/<id>/ses.json`, `nesneler/<id>/ses.json`
```json
{"mekan": "mara_kulubesi", "surum": 1,
 "zemin_malzemesi": {"ic": "ahsap_tahta", "dis": "kar"},
 "oda": {"boyut_m": [5, 4, 2.6], "emilim": 0.35, "oda_ir": "ses/oda_ir.wav"},
 "varsayilan_yatak": {"ic": "SES_KUTUPHANESI/yatak/IC_ODA_ahsap_01.wav", "dis": "SES_KUTUPHANESI/yatak/DIS_ruzgar_kar_03.wav"},
 "katman_kurallari": [{"kosul": "mekan_durumu.ocak_atesi=yanik", "katman": "SES_KUTUPHANESI/yatak/IC_ocak_02.wav", "kazanc_db": -12}],
 "imza_sesleri": {"kapi_acilis": "ses/kapi_gicirti_01.wav"}}
```
```json
{"nesne": "surgu", "malzeme": "demir", "imza": {"kayma": "ses/kayma_01.wav", "temas": "ses/temas_01.wav"}}
```
Oda boyutu yönetmenin krokisinden (`kroki.json → sinir`, duvarlar) hesaplanır; ayrıca yazılmaz. Aynı ev ikinci filmde aynı akustikle duyulur (kesin karar 3f).

#### 4.5.7 `SESLER/diyalog.json` sürüm 2 (replik kimliğine göre; tek kaynak)
```json
{
 "surum": 2, "ornekleme_hz": 48000,
 "replikler": {
  "R0121": {
   "karakter": "mara", "kaynak_plan": 121, "yol_plan": "veo_donustur", "yol_gercek": "veo_donustur",
   "senaryo_metin": "It's late, Captain. What do you want?", "veo_metin_istem": null,
   "duyulan_metin": "It's late, Captain. What do you want?",
   "tts": {"dosya": "SESLER/tts/R0121_6f2a.wav", "sure_sn": 3.2, "kelime_sn": 2.2, "kredi": 37},
   "metin_kapisi": {"wer": 0.0, "ad_dogru": true, "tasidigi_degisen_kelime": [], "konusan_yuz": "mara",
                    "hiz_kelime_sn": 2.3, "aksan": "olculemedi", "sonuc": "GEC", "rapor": "_RAPOR/S2m_D1.json#R0121"},
   "kelimeler": [{"w": "It's", "bas": 2.05, "bit": 2.21}, {"w": "late", "bas": 2.21, "bit": 2.52}],
   "klip_zamani": {"bas": 2.05, "bit": 5.31},
   "dosya": "SESLER/donusum/R0121.wav",
   "donusum": {"motor": "openvoice", "f0_kaydirma_yt": -1, "zarf_gecikme_ms": 6, "benzerlik": 0.79, "asr_wer_sonra": 0.0},
   "seviye": "normal", "olculen_lufs": -19.7, "kazanc_db": 0.2, "oda": "mara_kulubesi", "uzaklik": "orta",
   "merdiven": [],
   "denetim": {"S2": "GEC", "S3": "GEC", "S4": "GEC"}
  }
 },
 "_eski": {"121": {"ortam": null, "cumleler": [{"dosya": "…", "bas": 2.05, "sure": 1.1, "en": "It's late, Captain.", "tr": "…", "kaynak": "sabit ses"}]}}
}
```
- Kural: altyazı her zaman **`duyulan_metin`**'den üretilir (`veo_donustur`'da kabul edilmiş Veo metni, `tts`'te senaryo metni).
- `merdiven[]`: denenen her basamak `{basamak, sonuc, olcu, tarih}`; ders defteri buradan beslenir.
- `_eski` bölümü `capcut_film.py` ve `izleme_paketi.py`'nin eski okuyucuları için **bir sürüm boyunca** yazılır, sonra kaldırılır.

#### 4.5.8 `KURGU/SES_CIZELGESI.json` (ses katmanlarının zaman çizelgesi; sahibi ses araçları) **(yeni)**
```json
{
 "surum": 1, "cizelge": "T2", "fps": 24,
 "kurgu_plani": {"dosya": "KURGU/surumler/KURGU_PLANI_T2_v3.json", "imza": "9f8e7d6c"},
 "ambiyans": [{"sahne_grubu": "S12", "dosya": "SES_KUTUPHANESI/yatak/DIS_ruzgar_kar_03.wav", "cizelge_bas": 410.9, "sure": 95.4,
               "capraz_giris_sn": 0.8, "one_alma_sn": 0.5, "katmanlar": ["mesale_alev", "ic_ocak"], "plan_kazanc": {"124": {"dis_ruzgar_kar": 4}}}],
 "efektler": [{"id": "E124b", "plan": 124, "adim": "a2", "kaynak": "klip", "dosya": "SESLER/klip_efekt/124_a2.wav",
               "cizelge_bas": 431.25, "zaman_kaynagi": "klip_onset", "klip_ozet": "3c9a1f0b22de", "seviye_db": -9}],
 "muzik": [{"ipucu": "M06", "dosya": "MUZIK/secilen/M06_b.wav", "cizelge_bas": 402.0, "sure": 74.0, "giris_sn": 2.0, "cikis_sn": 3.0,
            "kisma": [{"bas": 412.9, "bit": 416.2, "db": -14}], "gecici": false}],
 "sessizlik": [{"tip": "muziksiz", "plan": 122, "cizelge_bas": 418.0, "sure": 1.6, "neden": "sok_sonrasi"}]
}
```
Kurgu planının imzası değişince betik yalnız değişen sahne gruplarını yeniden üretir. `klip_ozet` güncel klibin özetiyle uyuşmazsa efekt `bayat` olur (S5.7).

#### 4.5.9 Müzik: `MUZIK/muzik_listesi.json`, `EVREN/<SERI>/muzik/leitmotifler.json`, `MUZIK/KAYNAK_KAYDI.json`
```json
{
 "film": "EMBERFALL_F2", "kaplama_hedef": [0.40, 0.65],
 "ipuclari": [
  {"id": "M06", "tur": "tema", "motif": "LM_MARA", "donusum": "sade",
   "giris": {"olay": "replik_sonu", "replik": "R0118", "ofset_sn": 0.3, "rampa_sn": 2.0},
   "cikis": {"olay": "sahne_sonu", "sahne_grubu": "S12", "rampa_sn": 3.0, "tasma_sn": 1.5},
   "hit": [{"olay": "adim_basi", "plan": 126, "adim": "a1", "tur": "guclu_vurus"}],
   "hedef_sure_sn": 74, "duygu": "sefkat>gerilim", "yogunluk": [5, 7],
   "seviye": {"diyalogsuz_lufs": -18.0, "diyalog_alti_db": 14},
   "saglayici": ["acestep", "midi_ornek"], "aday": 3,
   "istem_en": "Intimate orchestral underscore, solo wooden flute melody over soft strings, D dorian, 72 BPM, 3/4, tender then uneasy, no vocals, no choir.",
   "secilen": null, "olcum": null}
 ]
}
```
```json
{"LM_MARA": {
  "karakter": "mara", "enstruman": "solo wooden flute", "ton": "D dorian", "bpm": 72, "olcu": "3/4",
  "notalar": [["D5", 1.0], ["F5", 0.5], ["E5", 0.5], ["C5", 1.0], ["D5", 2.0]],
  "donusumler": {"sade": {"enstruman": "solo flute"}, "tehdit": {"enstruman": "low strings", "ton": "D minor", "bpm": 60},
                 "zafer": {"enstruman": "full orchestra", "bpm": 84}},
  "motif_midi": "muzik/LM_MARA.mid", "referans_wav": "muzik/LM_MARA_ref.wav", "kroma_sablon": "muzik/LM_MARA_kroma.npy",
  "yazan": "ses-tasarimcisi muzik (görev G0123)", "ilk_film": "EMBERFALL_F2",
  "kullanim": [{"film": "EMBERFALL_F2", "ipucu": ["M02", "M06", "M19", "M31"]}]}}
```
`notalar`: perde + vuruş cinsinden süre. Motif ajanın kendi yazdığı özgün ezgidir; MIDI'yi `muzik.py` üretir. Bu, Content ID için de en temiz kaynaktır (§4.8.4).
`KAYNAK_KAYDI.json`: seçilen her dosya için `{dosya, saglayici, model, model_surum, lisans, lisans_kaynagi, istem, tohum, referans_motif, tarih, sha1}`.

#### 4.5.10 Efekt kütüphanesi dizini: `SES_KUTUPHANESI/DIZIN.json`
```json
{"yatak/DIS_ruzgar_kar_03.wav": {"kategori": "yatak", "etiketler": ["dis", "ruzgar", "kar", "gece"], "sure_sn": 184.0,
  "lufs": -31.2, "tepe_dbfs": -9.8, "dongu_uygun": true, "olay_icerir": false, "anlasilir_soz": false,
  "lisans": "CC0", "lisans_kaynagi": "LISANS.txt", "kaynak_url": null, "indirme_tarihi": null, "kara_liste": false}}
```

#### 4.5.11 Rapor, merdiven ve yeniden çekim kaydı
```json
{"kapi": "S2m", "dalga": 1, "sonuc": "HATA", "girdi_imza": "…", "esik_surum": "ses@1.0+ogrenilen@3",
 "hatalar": [{"madde": "S2.3", "replik": "R0140", "plan": 140, "olcu": {"ad_yazilan": "Kestra", "ad_duyulan": "Kestrel"},
              "esik": "ad doğru", "seviye": "H", "oneri": "yeniden_cek"}],
 "ozet": "OZET | replik: 24 | gec: 21 | gri: 2 | HATA: 1"}
```
`YENIDEN_URET.json` maddesi (kuyruk biçimi [KUR] §5.5 ve [ÜRE] §5.4 ile aynı):
```json
{"id": "YU-S2-1-003", "plan": 140, "kaynak_kapi": "S2", "tur": "video", "seviye": "KRITIK", "cozum": "yeniden_cek",
 "duzeltme": "CORRECTION: say the name exactly as \"Kess-tra\".", "deneme": 1, "deneme_max": 2, "kredi_tahmini": 12, "durum": "bekliyor"}
```
**Ses CORRECTION şablonları** (`duzeltme.py`'nin şablon dosyasına eklenir; aynı alan için cümle eklenmez, değiştirilir, [GÖR]):

| Kök neden | Şablon |
|---|---|
| `veo_konusmadi` | `CORRECTION: {Ad} speaks the line aloud, lips moving clearly: "{veo_metin\|metin}"` |
| `veo_metin_sapti` | `CORRECTION: {Ad} says the line exactly, word for word: "{metin}"` |
| `ad_yanlis_okundu` | `CORRECTION: say the name exactly as "{okunus_yazimi}".` (+ `replik.veo_metin` ders kuralı) |
| `yanlis_kisi_konustu`, `dinleyen_konustu` | `CORRECTION: only {Ad} speaks; {Diger} listens silently, mouth closed.` |
| `aksan_kaydi` | `CORRECTION: {Ad} speaks {veo_ses_tarifi}.` |

#### 4.5.12 Ders defteri kaydı (ortak biçim, [ÜRE] §5.8)
```json
{"id": "D-20261030-221540-c3d4", "film": "EMBERFALL_F2", "seri": "EMBERFALL", "olay": "kapi_hatasi",
 "asama": "A15", "kapi": "S2", "madde": "S2.9", "replik": "R0201", "plan": 201, "kategori": "donusum_metalik",
 "belirti": "openvoice benzerlik 0,58; teslim fisilti", "olcum": {"benzerlik": 0.58, "esik": 0.70},
 "baglam": {"teslim": "fisilti", "agiz_gorunur": "kismi", "motor": "openvoice", "kadraj": "OY"},
 "kanit": ["_RAPOR/S2_P2.json#R0201"], "eylem": "merdiven:yol_degistir_tts", "sonuc": "duzeldi",
 "rol_etiketi": ["ses-tasarimcisi"]}
```
Aynı `(kategori, baglam)` kümesi terfi eşiğini geçince bir `yol_kurali` doğar: `{"tur": "yol_kurali", "kosul": {"teslim": "fisilti", "agiz_gorunur": "kismi"}, "etki": "yol=tts"}`.
`ses_plani.py --taslak` bu kuralı sonraki partide uygular.

#### 4.5.13 `AYARLAR/FILM_AYAR.json` ses ekleri (anahtar içermez; git'e `FILM_AYAR.ornek.json` girer)
```json
{"saglayicilar": {"tts": ["ai84", "sahte"], "ses_donustur": ["openvoice", "rvc", "sahte"], "ayristirma": ["roformer", "demucs", "sahte"],
                  "asr": ["faster_whisper", "sahte"], "dudak": ["musetalk", "sahte"], "muzik": ["acestep", "midi_ornek", "sahte"],
                  "dinleyici": []},
 "butce": {"ai84_kredi_tavan_film": 60000, "ai84_seri_kurulum_tavan": 40000, "ai84_vc_tavan_film": 20000, "usd_tavan_film": 0},
 "fiyat_olcum": {"ai84_tts_harf": null, "ai84_vc_sn": null, "tarih": null},
 "indirme_izni": {"cc0_efekt": true},
 "yollar": {"evren_kok": "C:/Users/Soysal/Desktop/YZ_FILM/EVREN", "ses_kutuphanesi": "C:/Users/Soysal/Desktop/YZ_FILM/SES_KUTUPHANESI",
            "arsiv_klipler": "D:/YZ_FILM_ARSIV/PROJE_B2/PROJE_B2/SIRALI_VIDEO"},
 "ortamlar": {"rvc": "<venv_rvc python yolu>", "openvoice": "<…>", "musetalk": "<…>", "acestep": "<…>"},
 "ses": {"telaffuz_sesleri": {"kadin": "<voice_id>", "erkek": "<voice_id>"}, "notice_min_gun": 30, "gpu_tek_agir_model": true}}
```
Yollar [ÜRE] §5.10'daki `YOLLAR.json`'a taşınırsa ses araçları oradan okur; kullanıcının mevcut Windows yolları değişmez.

### 4.6 Yazılması / değişmesi gereken kod (araç adı, ne yapar, girdi/çıktı, öncelik)

Öncelik: **P0** = serinin ilk filminin ses aşamasından önce şart (karar mantığı bulutta `sahte` ile test edilir) · **P1** = ilk film sırasında · **P2** = sonra.
Bütün araçlar mevcut stilde: Türkçe kullanım metni, `sys.stdout.reconfigure`, `_RAPOR/` raporu, çıktı zarfı ve imza ([ÜRE]), atomik yazım, ağsız `--saglayici sahte`.
Ağır modeller ayrı sanal ortamlarda koşar; ana Python 3.10 ortamına yalnız hafif ölçüm kitaplıkları girer.

#### 4.6.1 Mevcut koddaki somut ses kusurları (satırlar bu turda yeniden okundu; düzeltilmeden yeni film yapılmamalı)

| Dosya:satır | Kusur | Sonucu | Düzeltme |
|---|---|---|---|
| `seslendir.py:104` | Her cümle **tepe** değerine göre ölçekleniyor (`a / max * 0.6`) | Tepe aynı, yükseklik farklı → D'deki "replik seviyeleri 9 dB oynuyordu" dersinin muhtemel kaynağı | LUFS eşitleme (`diyalog_esitle.py`) |
| `seslendir.py:67-71` | TTS Veo'nun konuşma süresine `atempo` 0,8–1,3 ile esnetiliyor | Toplam süre tutar, heceler dudağa oturmaz (H/proje-b2 "seslerde kayma, dudakla gitmiyor") | Ağzı görünen replikte `veo_donustur`; `tts`'te en çok ±%8 (tahmin) |
| `seslendir.py:85-91` | Cümleler whisper kelimelerine **kelime sayısıyla** bölünüyor | Veo bir kelime ekler ya da atlarsa sonraki bütün cümleler kayar | stable-ts ile bilinen metne hizalama + WER kapısı |
| `seslendir.py:92-93` | Whisper konuşma duymazsa cümleler klibe "orantılı yayılıyor" | Sessiz hata: ses rastgele saniyeye konur | Konuşma yoksa HATA → yeniden çekim kuyruğu (S2.1) |
| `seslendir.py:101-103` | TTS başarısızsa sessizce Flow'un sesi kullanılıyor | Aynı karakter iki farklı sesle konuşur; raporda yalnız bir satır | Merdiven kararı; sessiz geri dönüş yok |
| `seslendir.py:17`, `capcut_film.py:25` | 44,1 kHz | Her geçişte yeniden örnekleme | 48 kHz |
| `seslendir.py:54` | demucs `htdemucs` | Depo bakımsız (A3 A3); ayrıştırma zayıfsa dönüştürücü artefakt üretir | BS-RoFormer (python-audio-separator, MIT), yedek demucs |
| `capcut_film.py:116` | Ortam kanalı her replikli klibin **kendi** ayrıştırılmış ortamı (0,8) | Planlar arası ambiyans zıplaması (D: kapı sahnesi) | Sahne grubu başına tek yatak (`SES_CIZELGESI.json`) |
| `capcut_film.py:113` | Repliksiz kliplerin kendi sesi tam seviyede (`volume=1.0`) | Veo'nun kendi müziği ve ortamı sızar; "No music" katman ayrımı bozulur | Klipler kanalı **her zaman sessiz**; efekt kapılı olarak ayrı kanalda |
| `capcut_film.py:46-58,126` | Bütün filme tek "geçici akor" (0,45), kısma yok | Müzik diyaloğun altına inmiyor; leitmotif yok | İpucu yerleşimi + kısma (`SES_CIZELGESI.json → muzik[]`) |
| `film.py:156-170` | Gerçek ses yolu yalnız ilk sağlayıcı `ai84` ise; sahte yolda cümleler 0,8 sn'den başlayıp art arda diziliyor | `sahte` testi gerçek yolun mantığını hiç denemiyor | Yönlendirici her sağlayıcıda aynı mantıkla çalışır; `sahte` yalnız sesi üretir |
| `film.py:175-181` | Müzik = toplam süre kadar tek dosya | İpucu, motif, sessizlik kavramı yok | Müzik aşaması ipucu listesiyle |
| `izleme_paketi.py:37-40` | "duyulan: KİM: …" konuşanın adını yazıyor | Seyirci adı ekrandan önce öğrenir; ekran dışı replikte "kim konuştu" kopukluğu yakalanamaz | `isitsel_dokum()` (ses etiketi + ad maskeleme) |
| `ai84.py:10-11` | Anahtar yoksa **içe aktarırken** `SystemExit` ([ÜRE] S10) | Bulutta ya da testte `import ai84` süreci öldürür | Anahtar ilk çağrıda okunur; yoksa `AI84Error("anahtar_yok")` |

#### 4.6.2 Araçlar

| Araç | Yeni / değişir | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|---|
| `olcum/ses.py` | yeni ([GÖR] `olcum/` paketine) | LUFS (pyloudnorm, MIT; kısa replikte kısa süreli ölçüm), gerçek tepe (ffmpeg `ebur128=peak=true`), LRA, F0 (librosa pyin, bellekten ISC), konuşmacı gömmesi (yalnız ölçüm; model lisansı kurulum raporuna yazılır), WER (jiwer, bellekten Apache-2.0), VAD, olay başlangıcı (onset), zarf çapraz korelasyonu, kroma benzerliği, BPM/ton (ACE-Step "Audio Understanding" ya da librosa) | wav → sayı/JSON | P0 (`sahte` arka uç) / P1 (gerçek) |
| `olcum/dudak.py` | yeni | Plan penceresinde yüz başına ağız açıklığı dizisi (MediaPipe Face Landmarker, görüntüyle aynı sürüm), ses zarfıyla ofset ve güven | klip + pencere → dizi, ofset | P0 (sahte) / P1 |
| `ses_plani.py` | yeni | `--profil-denetle`; `--taslak S<k>` (yol önerisi, efekt olayları, yatak ve katmanlar, `flow_sound`, sessizlik önerileri); `--denetle [S<k>\|--tum]` (S0); `ses_tanitim_kurali()` (Y59 da çağırır); `veo_metin` ders kuralını uygular | `SAHNELER`, defter, evren, DIZIN → `35_SES/SES_<S>.taslak.json`, `_RAPOR/S0_*` | P0 |
| `ses_sec.py` | yeni | `--telaffuz`, `--ara` ([D-EL] süzgeçleri; AI84 geçirmiyorsa yerelde süzme), `--olc`, `--oku`, `--puanla`, `--sec` (evren.py ile), `--banka`; `SES_SECIM.html` | profiller → evren `ses.json`, `_RAPOR/S1*` | P0 |
| `ses_kiyas.py` | yeni | Motorları arşiv ve ilk film klipleriyle kör kıyaslar; `tts_dudak` dahil; motor sırasını ve basamak açıklığını yazar | klipler + karakter → `_RAPOR/S1b_motor_kiyas.json` | P0 (seri başında) |
| `ses_donustur.py` | yeni | `--ayristir` (RoFormer/demucs), `--hizala` (stable-ts align + serbest ASR, WER, ad, `tasidigi`, hızlı konuşan yüz), `--donustur` (motor sağlayıcısı, F0 kaydırma, söz penceresi kapısı, gecikme/benzerlik), `--egit` (RVC, ayrı ortam) | klip + metin + evren sesi → `SESLER/ayrik`, `hizalama`, `donusum` | P0 |
| `ses_karar.py` | **yeni** | Ses merdiveni (§4.8.3): HATA türü → sıradaki basamak; 0 kredili basamaklar önce; kuyruğa `kaynak_kapi: S2` maddesi; kurgucuya ve yönetmene istek; `hikaye-yazari` replik_kabul görevi; `merdiven[]` kaydı ve ders kaydı | S2/S3 raporları + `diyalog.json` → kararlar | P0 |
| `seslendir.py` | değişir (yönlendirici) | `--animatik` (bütün replikler TTS, süre kapısı), `--parti N` (yol başına yönlendirme); `diyalog.json` v2; §4.6.1 kusurlarını kaldırır | `SAHNELER`, klipler → `SESLER/*`, `_RAPOR/S2*` | P0 |
| `ses_kutuphanesi.py` | yeni | `--dizinle` (62 efekt + yataklar, `LISANS.txt`, ölçüm, anlaşılır söz taraması); `--eksik --indir` (Freesound, yalnız CC0, lisans kaydı); kara liste | `SES_KUTUPHANESI/` → `DIZIN.json` | Dizinleme P0, indirme P1 |
| `diyalog_esitle.py` | yeniden yazılır | Replik başına LUFS hedefi (teslim → seviye), oda yanıtı, uzaklık, `veo_donustur` ↔ `tts` tını eşleme | `diyalog.json` → `SESLER/esit/*`, `_RAPOR/S4_*` | P0 |
| `ses_katmani.py` | yeniden yazılır | `--cizelge T1\|T2`: sahne grubu yatağı (döngü, çapraz geçiş, öne alma, dış katman), efektleri klibin kendi ses başlangıcına oturtma (yoksa kütüphane), kapılı klip efekti, yaratık kiti, defterden nesne sesleri, klip özetiyle yeniden çekim tespiti | kurgu planı → `KURGU/SES_CIZELGESI.json`, stemler, `_RAPOR/S5_*` | P0 |
| `muzik.py` | yeni (`gemini_muzik.py` yazılmaz) | `--kagit` (S0 müzik maddeleri); `--uret` (sağlayıcı zinciri; motif MIDI → çalınmış referans → ACE-Step Cover/Refer; aday ölçümü); `--yerlestir` (bar kesimi, vuruş hizası, rampalar, kısma, sesten leitmotif doğrulama); `--midi` (motif MIDI ve referans çalma) | `muzik_listesi.json` → `MUZIK/secilen/*`, `KAYNAK_KAYDI.json`, `SES_CIZELGESI.json → muzik[]`, `_RAPOR/S6_*` | P0 (`midi_ornek`, `sahte`); P1 (`acestep`) |
| `dudak_denetim.py` | yeniden yazılır | S3: ofset/güven, konuşan yüz kimliği, ekran dışı ve köprü replikte oynayan dudak, bölünmüş klipte söz kesişimi; SyncNet isteğe bağlı; ağız dizisini kurgucunun B9 denetimine verir | kurgu planı, `diyalog.json`, klipler → `_RAPOR/S3_*` | P0 |
| `son_miks.py` | yeni (**tek miks kodu**) | Stem toplama, kısma, tek doğrusal kazanç + 4× aşırı örneklemeli tepe sınırlayıcı, yeniden ölçüm, LRA, mono, planlanmamış sessizlik, ASR ile anlaşılırlık; `--animatik`, `--onizleme` (kurgu_render çağırır), `--final` (mux ya da yalnız ölçüm, §4.2 SF1), `--shorts` | stemler → `YAYIN/ses_master.wav`, `_RAPOR/S7_*`, `S8_*` | P0 |
| `isitsel_dokum` (işlev; `kor_paket.py` içinden çağrılır) | yeni | Plan başına "duyulan" satırı: ad yerine `ses_etiketi_tr`, ad maskeleme ([SEN2] kodu), efekt, müzik türü, sessizlik; kurgu kipinde son miksten ASR ile | `diyalog.json`, `SES_CIZELGESI.json` → paket satırları | P1 (seyirci uzmanlarıyla ortak) |
| `capcut_film.py` | değişir | Kanallar: Klipler (**sesi kapalı**, kırpılmış), Diyalog (replik parçaları), Efekt, Ambiyans (sahne parçaları), Muzik (ipucu parçaları); geçici akor yalnız müzik yoksa ve adı `GECICI`; okuduğu yer `KURGU_PLANI` + `SES_CIZELGESI` | → CapCut taslağı | P0 |
| `kurgu_render.py` ([KUR]) | değişir | Sesi kendisi karıştırmaz; `son_miks.onizle(...)` çağırır | — | P0 |
| `film.py` ([ÜRE]/[MİM]) | değişir | Ses aşamaları ve görevleri (§4.4.2); indirme sonrası SC1 kancası; AI84 bütçe kapısı (`ai84_kredi_tavan_film`, `ai84_seri_kurulum_tavan`, `ai84_vc_tavan_film`); imzalara `zanaat.ses`, evren ses dosyaları ve `ses_esikleri.json` sürümü girer | — | P0 |
| `saglayicilar/` | değişir | Türler §4.6.3; yeni sınıflar `openvoice.py`, `rvc.py`, `roformer.py`, `faster_whisper.py`, `musetalk.py`, `acestep.py`, `midi_ornek.py`; `sahte` hepsini taklit eder | — | P0 (openvoice, roformer, faster_whisper, midi_ornek, sahte); P1 (rvc, acestep, musetalk); P2 (ai84_vc, dinleyici) |
| `istem_denetim.py` | değişir | Konuşan planda `veo_ses_tarifi` birebir; dize kuralları (≤ 12 kelime, aksan öğesi, yaş/filtre yok); `flow_sound` kuralları; replik metni filtre taraması ([SEN] önerisi) | `SAHNELER.json` → rapor | P0 |
| `ai84.py` | değişir | Tembel anahtar okuma (S10); `voices()` sayfalama ve süzgeç geçirme; `estimate()` sarmalayıcısı | — | P0 |
| `ses_esikleri.json` | yeni | §4.7'deki yeni anahtarlar (`deger`, `aciklama`, `kaynak`, `etiket: kaynakli\|tahmin`); `esikler.py` ile yüklenir | — | P0 |
| `veri/efekt_sozlugu.json` | yeni | Fiil sözlüğü kimliği → efekt kategorisi, an kuralı, malzeme kaynağı | — | P0 |
| `testler/test_ses.py` | yeni | §4.7.10 bozuk girdi testleri + `ORNEK_3_SAHNE` uçtan uca ses akışı (`sahte`; ağ ve kredi yok) | — | P0 |

#### 4.6.3 Sağlayıcı arayüzü (ses türleri)
```python
TURLER = ("llm", "vlm", "gorsel", "video", "tts", "ses_donustur", "ayristirma", "asr", "dudak", "muzik", "dinleyici")
# "ses" → "tts" eski ad olarak bir sürüm boyunca tanınır.
tts(film, metin, ses_id, cikti, seed=None, onceki=None, sonraki=None) -> {"sure_sn", "kredi"}
ses_donustur(film, giris_wav, karakter, cikti, f0_yt) -> {"gecikme_ms", "benzerlik"}
ayristir(film, klip, cikti_dir) -> {"konusma": yol, "diger": yol}
asr(film, wav, bilinen_metin=None) -> {"metin", "kelimeler": [...], "guven"}
dudak(film, klip, ses_wav, pencere, cikti) -> {"sure_sn"}          # yerel MuseTalk; çıktı V2'ye gider
muzik(film, ipucu, cikti_dir, aday, referans_wav=None) -> [aday_yolu, ...]
dinleyici(film, wav, soru, secenekler) -> {"cevap", "guven"}        # isteğe bağlı; yoksa Kisitlandi("anahtar_yok")
```
Her sınıf `hazir()`, `birim_fiyat()`, `ortam` (`yerel` / `her_ikisi`), `kredili`, `elle = False` taşır ([ÜRE] §5.6). `elle = True` olan müzik sağlayıcısı zincire konamaz (İ-6).

#### 4.6.4 Kurulum
- `kurulum.py` ana ortama: `pyloudnorm`, `stable-ts`, `faster-whisper`, `audio-separator`, `jiwer`, `librosa` (lisanslar kurulum raporuna).
- Ayrı ortamlar (`kurulum.py --ses-ortamlari`, `om_kopru.py` kalıbı): `venv_openvoice`, `venv_rvc` (Python 3.12, [D-RVC]), `venv_musetalk` (Python 3.10 + torch 2.0.1, [D-MT]),
  `venv_acestep` (Python 3.11–3.12, [D-AS]). Kullanıcının bilgisayarına `py` ile ikinci Python sürümünün kurulması gerekebilir; kurulum bunu kendisi yapar ve yazar.
- Model dosyaları bir kez indirilir; sonra `HF_HUB_OFFLINE=1`.
- Kullanıcıya yeni `.bat` gerekmez. Ses aşamaları `film.py`'nin görevleridir.

#### 4.6.5 PR sırası (ses parçası; [ÜRE] §6.5 sırasına uyar)
1. `ai84.py` tembel anahtar, `olcum/ses.py` + `olcum/dudak.py` (sahte arka uç), `ses_esikleri.json`, `test_ses.py` iskeleti.
2. `ses_plani.py`, `veri/efekt_sozlugu.json`, `istem_denetim.py` ekleri (kâğıt kapısı S0; bulutta test edilir).
3. `ses_sec.py`, `ses_kiyas.py`, `ses_kutuphanesi.py --dizinle`.
4. `seslendir.py` yönlendirici, `ses_donustur.py`, `ses_karar.py`, SC1 kancası.
5. `diyalog_esitle.py`, `ses_katmani.py`, `muzik.py`, `dudak_denetim.py`, `son_miks.py`, `capcut_film.py` kanalları, `kurgu_render.py` çağrısı.
6. `isitsel_dokum`, ders defteri ses kategorileri, ACE-Step ve MuseTalk sağlayıcıları.

### 4.7 Makinenin denetleyeceği eşikler (kaynağıyla) **(değişti)**

Kodlar Z §6.2 ile aynı: **H** = HATA (geçmez), **B** = BAYRAK (merdiven ya da sahibi bakar). **Ölçülemedi** asla GEÇ değildir; B sayılır ([GÖR] kuralı).
Yeni eşikler `ses_esikleri.json`'a girer. `RE:` olanlar zaten `ritim_esikleri.json`'da ve oradan okunur. **(tahmin)** olanlar §4.7.9'daki kalibrasyonla ayarlanır.
"Çizelge" sütunu ölçünün hangi zaman çizelgesinde yapıldığını söyler ([KUR] T0 kâğıt · T1 animatik · T2 kaba kurgu · T3 kullanıcının CapCut düzenlemesi · V = video indirmesi).

#### 4.7.1 S0 — Kâğıt ses kapısı (`ses_plani.py --denetle`, `istem_denetim.py`; kredi yok)

| # | Ölçü | Eşik | Sonuç | Çizelge | Kaynak |
|---|---|---|---|---|---|
| S0.1 | Konuşma adımı olan planda `ses.diyalog.yol` dolu; `_derlenir.agiz_gorunur` ile tutarlı (tam/kısmi → `veo_donustur`, yok → `tts`); aykırılıkta `yol_neden` + ders kuralı kaynağı | çelişki 0 | H | T0 | §4.1.2 karar; [YÖN2] İ-9 |
| S0.2 | `ekran_disi_ses` varken `_derlenir.dinleyen_agiz = kapali` | var | H | T0 | Y35 ([YÖN2]) — **tek fonksiyon**, ses raporu sonucu okur |
| S0.3 | Ses tanıtım kuralı: `kaynak: "tts"` olan ekran dışı ses, karakter daha önce ekranda konuşurken duyulduktan sonra (`gizem_sesi: true` hariç) | ihlal 0 | B | T0 | Y59 ile aynı fonksiyon (`ses_tanitim_kurali()`); Z §4.1'den türetildi (tahmin) |
| S0.4 | Konuşan planın derlenmiş hareket isteminde `veo_ses_tarifi` birebir | %100 | H | T0 | A1 B3 ("bir kez yaz, kelimesi kelimesine tekrarla") |
| S0.5 | `veo_ses_tarifi`: ≤ 12 kelime; tını/perde + cinsiyet + aksan öğeleri var; filtre ve yaş sözcüğü 0 | evet | H | T0 | İ-3; D; `istem_denetim.py` listeleri; 12 (tahmin) |
| S0.6 | `flow_sound`: "Sound:" ile başlar, "No music." ile biter, arası ≤ 12 kelime; müzik/şarkı/vokal sözcüğü ve filtre kelimesi 0 | evet | H | T0 | BK 4.2.1, BK §8 #11; 12 (tahmin) |
| S0.7 | Her `fiziksel` adım için ≥ 1 efekt olayı ya da gerekçeli `sessiz_adim` | %100 | H | T0 | Z §5.1 |
| S0.8 | Efekt `an`'ı kendi adım penceresinde `[bas, bit + 0,3]` | evet | B | T0 | (tahmin) |
| S0.9 | Ani efekt ilk söz başlangıcına ≥ 150 ms uzak (bilinçli şok hariç) | evet | B | T0 | (tahmin); Y02b ile birlikte |
| S0.10 | Sahne grubu başına tek yatak; aynı mekân ve kesintisiz zamandaki (`zaman.atlama: yok`) ardışık sahne gruplarında aynı yatak; `devam` geçişinde çapraz geçiş yok | 1; aynı; yok | H | T0 | Z §5.2; D |
| S0.11 | Yatak katmanları ↔ sahne `zaman` ve dünya defteri (hava, gün saati, ateş/ışık kaynağı durumu); her katmanın `kaynak` olgusu defterde doğru | çelişki 0 | H | T0 | kesin karar 3b |
| S0.12 | Mutlak sessizlik sayısı / süresi | ≤ 2 / ≤ 1 sn | H | T0 | RE:mutlak_sessizlik_film_max, RE:mutlak_sessizlik_max_sn |
| S0.13 | Planlı sessizlik: ifşa öncesi ve şok sonrası `[0,8; 3,0]` sn; en karanlık anda 10–40 sn müziksiz; soğuk açılışın ilk 3–5 sn'si müziksiz | var | B | T0 | RE:vurgu_sessizlik_sn; Z §5.3 |
| S0.14 | Müzik kaplama; en uzun müziksiz / müzikli blok | %40–65; ≤ 240 / ≤ 300 sn | B | T0 | RE:muzik_kaplama_oran, RE:muziksiz_blok_max_sn, RE:muzikli_blok_max_sn |
| S0.15 | Müzik girişi bir olaya bağlı (kesme, adım başı, bakış, replik sonu); replik penceresinin ortasında giriş | olay var; 0 | H | T0 | Z §5.4 |
| S0.16 | Ardışık iki ipucunda aynı duygu türü | 0 | B | T0 | Z §5.4 |
| S0.17 | Leitmotif: P1'de sade ilk sunum, doruğa kadar dönüş, doruğunda tam | var; ≥ 3; var | B | T0 | RE:leitmotif_donus_min; Z §5.4 |
| S0.18 | Müzik isteminde sanatçı/film adı; "no vocals" ifadesi; motifli ipucunda `notalar` dolu | 0; var; var | H | T0 | BK 4.5 |
| S0.19 | Konuşan her karakterin evren ses kaydı ya da `veo_ham` figüran kuralı var | %100 | H | T0 (SB2 sonrası) | §4.5.5 |
| S0.20 | Uydurma ad geçen replikte telaffuz testi GEÇ | %100 | H | T0 (SB1 sonrası) | İ-10 |
| S0.21 | Replik bloğunda tek teslim; `teslim: fisilti` ve `agiz_gorunur: tam` olan planlar ders kuralı varsa uyarılır | evet | B | T0 | A3 A2 (dönüştürücü fısıltıda zorlanır) |

#### 4.7.2 S1 — Telaffuz, ses seçimi ve dönüştürme motoru (`ses_sec.py`, `ses_kiyas.py`)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S1.1 | Aday: İngilizce, `voice_restricted` değil, önizleme var, bildirim süresi (`notice_period`) | evet; ≥ 30 gün | H; B | BK 6.4; [D-EL] `min_notice_period_days`; 30 (tahmin) |
| S1.2 | Ad okuma: adı içeren 3 replikte ASR ad doğru (yazım ya da fonetik eşleşme) | hata 0 | H | (tahmin) |
| S1.3 | TTS anlaşılırlığı (ASR WER) | ≤ 0,05 | H | (tahmin) |
| S1.4 | Kararlılık: aynı sesin 3 repliği arası gömme benzerliği | ≥ 0,80 | B | (tahmin) |
| S1.5 | Kadro ayırt ediciliği: iki karakter merkezi arası benzerlik; aynı cinsiyette F0 medyanı farkı | ≤ 0,60; ≥ 2 yarım ton | H | (tahmin) |
| S1.6 | Perde bandı (F0 medyanı). Erkek: düşük < 100, orta 100–140, yüksek > 140 Hz. Kadın: düşük < 165, orta 165–225, yüksek > 225 Hz | profil bandında | B | bant sınırları (tahmin; genel fonetik bilgisi, bellekten) |
| S1.7 | Aksan etiketi = profil aksanı | eşit | H | İ-3; [D-EL] |
| S1.8 | Seçim puanı = 0,25 profil uyumu + 0,20 ayırt edicilik + 0,20 kalite (S1.2–S1.3) + 0,15 kararlılık + 0,10 duygu aralığı (3 replik arası LUFS ve F0 yayılımı) + 0,10 bildirim süresi | en yüksek; fark < 0,03 ise ajan seçer | — | ağırlıklar ve 0,03 (tahmin) |
| S1.9 | Aynı seride bir ses iki karaktere verilmez | 0 | H | seri evreni kuralı |
| S1.10 | `veo_ham` figüran: filmde tek replik; ana karakter merkezlerine benzerlik | 1; < 0,60 | H | İ-11 (tahmin) |
| S1.11 | Motor kıyası (eğitime girmemiş cümleler): hedef benzerlik; zarf gecikmesi; ASR WER artışı | ≥ 0,70; ≤ 20 ms; ≤ 0,05 | H | (tahmin) |
| S1.12 | `tts_dudak` kıyası: V2 kimlik (görüntü eşikleri) ve S3 ofset | görüntü uzmanının V2 bandı; S3.1 | H | [GÖR] §7.6; [D-MT] |

#### 4.7.3 S2 — Replik kapısı (S2.1–S2.6 indirmede `ses_donustur.py --hizala`; S2.7+ dönüşümde)

| # | Ölçü | Eşik | Sonuç | Çizelge | Kaynak |
|---|---|---|---|---|---|
| S2.1 | Konuşma bulundu: ayrık konuşma kanalında VAD + ASR, replik penceresi ±1 sn içinde ≥ 1 kelime | var | H | V | §4.6.1 (`seslendir.py:92-93` sessiz hatası); İ-7 |
| S2.2 | Veo metni ↔ senaryo WER | ≤ 0,10 GEÇ · 0,10–0,25 gri (replik_kabul) · > 0,25 H | H/B | V | A3 "WER eşiği aşılırsa (ör. > %15)"; bantlar (tahmin) |
| S2.3 | Adlar doğru söylendi | evet | H | V | Z §4.1 (ad sözle verilir) |
| S2.4 | `tasidigi` olan replikte değişen/eksik içerik kelimesi | 0 → GEÇ; > 0 → replik_kabul (WER ne olursa olsun) | B | V | [SEN2] İ8 |
| S2.5 | Ağzı en çok oynayan yüz = replik karakteri (3 kare hızlı denetim) | evet | H | V | kesin karar 3c; [YÖN] Y29 |
| S2.6 | Veo konuşma hızı | 1,8–3,2 kelime/sn | B | V | RE:konusma_hizi_kelime_sn (2,5) ve RE:konusma_hizi_agir_kelime_sn (2,0) çevresi; bant (tahmin) |
| S2.7 | F0 kaydırma büyüklüğü | \|Δ\| ≤ 6 yarım ton | B | V/SD | (tahmin; büyük kaydırma dönüştürücüde artefakt yapar, bellekten) |
| S2.8 | Dönüşmüş ses ↔ Veo konuşması zarf gecikmesi | \|gecikme\| ≤ 20 ms | H | SD | (tahmin; bir karenin yarısından az) |
| S2.9 | Dönüşmüş ses ↔ karakter merkezi benzerliği | ≥ 0,70 | H | SD | (tahmin) |
| S2.10 | Dönüşüm sonrası ASR WER artışı | ≤ 0,05 | B | SD | (tahmin) |
| S2.11 | Aynı karakterin `veo_donustur` ↔ `tts` replikleri arası benzerlik | ≥ 0,75 | B | SD | (tahmin) |
| S2.12 | `tts` zaman esnetmesi | ≤ ±%8 | H | SD | (tahmin) |
| S2.13 | Gerçek replik süresi (TTS) + 0,4 + 0,25·(cümle−1) + 0,5 ≤ planın kullanılabilir penceresi (L taşması dahil) | evet | H | T1 | Z §2.3; RE:diyalog_giris_payi_sn, RE:diyalog_cikis_payi_sn |
| S2.14 | Örnek tepe | < −0,1 dBFS | H | SD | (tahmin) |
| S2.15 | `tts_dudak` çıktısı görüntünün V2 kimlik denetimini ve S3'ü geçer | evet | H | SD | [GÖR] §8.9 |
| S2.16 | Aksan tutarlılığı (`dinleyici` ya da sınıflayıcı varsa) | profil aksanı | B (yoksa "ölçülemedi") | SD | İ-3 |

#### 4.7.4 S3 — Dudak denetimi (`dudak_denetim.py`; kurgu planının her değişiminden sonra)

| # | Ölçü | Eşik | Sonuç | Çizelge | Kaynak |
|---|---|---|---|---|---|
| S3.1 | Ağız açıklığı ↔ ses zarfı ofseti | \|ofset\| ≤ 42 ms GEÇ · 42–125 ms B · > 125 ms H | H/B | T2, T3 | 42 ms = 1 kare @ 24 fps (hesap); 125 ms ITU-R BT.1359 (bellekten, doğrulanmalı); [KUR] `senkron_tolerans_kare` |
| S3.2 | Korelasyon güveni | ≥ 0,3 | B | T2, T3 | (tahmin) |
| S3.3 | İsteğe bağlı SyncNet: ofset; güven | 0 ±1 kare; ≥ 3 | B | T2 | A3 A1 (LatentSync "sync confidence < 3" filtresi) |
| S3.4 | Ağzı oynayan yüzün kimliği = replik karakteri | evet | H | T2, T3 | kesin karar 3c |
| S3.5 | Ekran dışı ya da köprü replik sırasında kadrajdaki yüzlerin ağız açıklığı standart sapması | ≤ 0,05 (blendshape birimi) | H | T2, T3 | BK 5.1.8; sayı (tahmin) |
| S3.6 | Bölünmüş klipte atlanan aralık bir sözle kesişiyor | 0 | H | T2 | D; RE:klip_bolme_atlama_min_sn; [KUR] senkron korumalı formül |
| S3.7 | Kurguda ağız gerçekten görünüyor mu (yüz ≥ kare yüksekliğinin %8'i ve ağız noktaları bulundu) ↔ planlanan yol | uyumlu | B | T2 | %8 ölçülebilirlik alt sınırı (tahmin); planlama şartı %12 Y32 |
| S3.8 | Karşılıklı konuşmada cevap boşluğu | 0,2–0,6 sn | B | T1, T2 | RE:cevap_boslugu_sn |

#### 4.7.5 S4 — Diyalog seviyesi (`diyalog_esitle.py`)

| # | Ölçü | Eşik | Sonuç | Çizelge | Kaynak |
|---|---|---|---|---|---|
| S4.1 | Replik yüksekliği (sınıf `teslim`'den) | fısıltı −24 · yumuşak −21,5 · normal −19,5 · bağırma −17 LUFS, ±1 LU | H | T1, T2 | RE:diyalog_lufs, RE:diyalog_lufs_tolerans |
| S4.2 | Aynı sahne + aynı karakter + aynı sınıf replikler arası fark | ≤ 1 LU | H | T2 | RE toleransından türetildi |
| S4.3 | Ölçüm yöntemi: 0,4 sn'den kısa replikte bütünleşik ölçüm yok, en yüksek anlık (400 ms) değer | — | — | — | A3 A3 |
| S4.4 | `veo_donustur` ↔ `tts` uzun dönem ortalama spektrum farkı (1/3 oktav, 100 Hz–8 kHz) | ≤ 3 dB | B | T2 | (tahmin) |
| S4.5 | Aynı mekândaki replikler aynı oda yanıtıyla | evet | H | T2 | Z §5.2'nin diyaloğa uygulanması |

#### 4.7.6 S5 — Ambiyans ve efekt (`ses_katmani.py`)

| # | Ölçü | Eşik | Sonuç | Çizelge | Kaynak |
|---|---|---|---|---|---|
| S5.1 | Sahne grubu içinde yatak dosyası sayısı | 1 | H | T1, T2 | Z §5.2; D |
| S5.2 | Ambiyans boşluğu (100 ms pencerede < −60 dBFS; planlı mutlak sessizlik hariç) | 0 | H | T1, T2 | Z §6.2 #45; −60 (tahmin) |
| S5.3 | Ardışık planların ambiyans kısa süreli yükseklik farkı | ≤ 3 LU | H | T1, T2 | RE:ambiyans_sahne_ici_fark_max_lu |
| S5.4 | Ambiyans diyalogun altında | 12–18 dB | H | T1, T2 | RE:ambiyans_diyalog_alti_db |
| S5.5 | Sahne geçişinde çapraz geçiş; yeni yatağın öne alınması | 0,5–1,0 sn; 0,3–1,0 sn | B | T1, T2 | RE:ambiyans_capraz_gecis_sn, RE:ses_koprusu_sn |
| S5.6 | Efekt diyalogun altında (şok planı hariç) | 3–10 dB | B | T2 | RE:efekt_diyalog_alti_db |
| S5.7 | Efekt kaydının `klip_ozet`'i = güncel klibin özeti | %100 | H | T2, T3 | D ("yeni çekilen planlar efektsiz kalıyordu") |
| S5.8 | Kapılı klip efekti kullanılan pencerede anlaşılır söz ya da müzik sızıntısı | 0 | H | T2 | Z §5.2; yöntem (tahmin) |
| S5.9 | Yatakta anlaşılır söz (ASR kelime güveni ≥ 0,5) | 0 | H | dizinleme | BK 5.1.2 (Lyria mırıltısı dersi); güven sınırı (tahmin) |
| S5.10 | Her ses parçasının başı ve sonunda yumuşatma (tık önleme) | 10–20 ms | B | T1, T2 | (tahmin) |
| S5.11 | Zincirlenmiş (`devam`) iki klibin sınırında aynı kategoriden iki olay ±100 ms içinde | 0 (biri atılır) | B | T2 | (tahmin) |

#### 4.7.7 S6 — Müzik (`muzik.py`)

| # | Ölçü | Eşik | Sonuç | Çizelge | Kaynak |
|---|---|---|---|---|---|
| S6.1 | Parçada söz/vokal (ASR anlaşılır kelime; vokal ayrıştırma enerjisi) | 0 | H | T1 | BK 4.5.2 ("sözsüz") |
| S6.2 | Diyalog sırasında müzik diyalogun altında | ≥ 12 dB | H | T1, T2 | RE:muzik_diyalog_alti_min_db |
| S6.3 | Diyalogsuz bölümde müzik yüksekliği | −20…−16 LUFS | B | T1, T2 | RE:muzik_diyalogsuz_lufs |
| S6.4 | Kaplama ve blok süreleri (ölçülen stemden) | S0.14 ile aynı | B | T1, T2 | RE |
| S6.5 | Giriş / çıkış rampası (şok hariç) | 1–3 sn / 2–4 sn | B | T1, T2 | RE:muzik_giris_sn, RE:muzik_cikis_sn |
| S6.6 | Vuruş noktası hizası; zaman esnetme; kesim bar sınırında | ±42 ms; ≤ ±%3; ±50 ms | B | T2 | (tahmin) |
| S6.7 | Tema ipucunda motif kroma benzerliği; ölçülen leitmotif dönüş sayısı (doruğa kadar) | ≥ 0,6; ≥ 3 | B | T1, T2 | RE:leitmotif_donus_min; benzerlik (tahmin) |
| S6.8 | Kaynak kaydı tam ve sağlayıcı lisansı izinli listede; sağlayıcı `elle = False` | evet | H | T1 | B12 |
| S6.9 | Kırpılma; parça içinde ani kesik | 0 | H | T1 | — |
| S6.10 | Adayın ölçülen BPM ve tonu ↔ istem | BPM ±%3; ton aynı | B | T1 | [D-AS] "Audio Understanding"; tolerans (tahmin) |

#### 4.7.8 S7/S8 — Miks ve yayın (`son_miks.py`)

| # | Ölçü | Eşik | Sonuç | Çizelge | Kaynak |
|---|---|---|---|---|---|
| S7.1 | Bütünleşik yükseklik | −14 ±1 LUFS | H | T1, T2, final | RE:final_lufs, RE:final_lufs_tolerans |
| S7.2 | Gerçek tepe | ≤ −1 dBTP (kodlama öncesi hedef −1,5) | H | T1, T2, final | RE:true_peak_max_dbtp; −1,5 payı (tahmin; AAC kodlaması tepeyi artırabilir, bellekten) |
| S7.3 | Yükseklik aralığı (LRA) | ≤ 14 LU | B | T2 | (tahmin) |
| S7.4 | Planlanmamış mutlak sessizlik (`silencedetect n=-50dB d=0.3`) | 0 | H | T1, T2 | RE:mutlak_sessizlik_db; d=0,3 (tahmin) |
| S7.5 | Mono toplamda yükseklik farkı; ortalama faz korelasyonu | ≤ 3 LU; ≥ 0 | B | T2 | (tahmin) |
| S7.6 | Son miksteki her replik için ASR ↔ altyazı WER | ≤ 0,15 GEÇ · 0,15–0,30 B · > 0,30 H | H/B | T2 | (tahmin); müziğin/ambiyansın maskelemesinin ölçüsü |
| S7.7 | Kırpılma | 0 | H | T1, T2 | — |
| S7.8 | Kazanç doğrusal mı (sınırlayıcı dışında dinamik işlem yok) | evet | H | T1, T2, final | İ-1; [D-FF] |
| S7.9 | Shorts: yükseklik; gerçek tepe | −14 ±1 LUFS; ≤ −1 dBTP | H | Shorts | D ("Shorts −21 LUFS çıkmıştı") |
| S8.1 | Dışa aktarılmış son dosyada S7.1–S7.2 yeniden | geçer | H | final | — |
| S8.2 | Kullanıcının CapCut ses ayarı varsa korunmuş (yeniden karıştırılmamış) | evet | H | T3/final | BK 5.3.3; [KUR] §8.7 |

#### 4.7.9 Kalibrasyon (eşik uydurmamak için)
- **Dudak (S3.1–S3.2):** B2 arşivinde kullanıcının "seslerde kayma, dudakla gitmiyor" dediği taslak (H/proje-b2) olumsuz örnektir; kabul edilip yayınlanan son kurgu olumlu örnektir.
  Eşik, kaçırma ≤ %10 olacak biçimde seçilir (A2 §7 kuralı).
- **Benzerlik (S1.5, S2.9, S2.11):** referans kayıtta eğitime ya da referansa girmeyen cümlelerin merkeze benzerlik dağılımı → 5. yüzdelik "aynı kişi" alt sınırı;
  kadrodaki öteki seslerin dağılımı → üst sınır.
- **WER (S2.2):** B2/B3 arşiv klipleri senaryo metniyle hizalanır; Veo'nun tipik sapma dağılımı çıkarılır. Bu oran bugün bilinmiyor.
- **Aksan (S1.7, S2.16):** ilk filmde ölçülemeyen her replik "ölçülemedi" olarak işaretlenir. Kullanıcı notunda "aksan değişti" gelirse ders defterine `aksan_kaydi` kaydı düşer.
- Kalibre edilen değerler `ses_esikleri.json`'a kanıt bağlantısıyla, ders defterinin korkulukları içinde yazılır (gevşetme yalnız etiketli kanıtla; [ÜRE] §5.8).

#### 4.7.10 Bozuk girdi testleri (`testler/test_ses.py`; `sahte` sağlayıcı; ağ ve kredi yok)

| Enjekte edilen bozukluk | Beklenen |
|---|---|
| Bir repliği kurguda 200 ms kaydır | S3.1 HATA → `kurgu_uygula` önerisi |
| Ekran dışı replik sırasında ağız açıklığı dizisi oynuyor (sahte dizi) | S3.5 HATA |
| Tepeye göre normalize edilmiş, tepe faktörü farklı iki replik | S4.1 HATA |
| Bir sahne grubunda iki ayrı yatak | S0.10 ve S5.1 HATA |
| Yeniden çekim taklidi: klip değişti, efekt kaydı eski özetli | S5.7 HATA, efekt yeniden kurulur |
| Miksin ortasına 1,5 sn dijital sessizlik | S7.4 HATA |
| Sahte ASR müzik parçasında kelime bildiriyor | S6.1 HATA, aday elenir |
| −20 LUFS miks | `son_miks` düzeltir → S7.1 GEÇ; S7.8 doğrusal |
| Tema ipucunda motifsiz aday (sahte müzik sağlayıcısı) | S6.7 BAYRAK → `midi_ornek` yedeği → GEÇ |
| Sahte Veo klibinde konuşma yok | S2.1 HATA → `YENIDEN_URET.json`'da `kaynak_kapi: S2`, CORRECTION şablonu |
| Sahte ASR adı "Kestrel" duyuyor | S2.3 HATA → yeniden çekim; ikinci kez → `istem_kalibi` ders adayı |
| WER 0,18, `tasidigi` boş | gri bant → `replik_kabul` görevi üretilir |
| WER 0,05 ama `tasidigi` kelimesi eksik | S2.4 → `replik_kabul` görevi (otomatik kabul yok) |
| `veo_ses_tarifi` 14 kelime ya da aksansız | S0.5 HATA |
| `flow_sound` "No music." ile bitmiyor | S0.6 HATA |
| `muzik` zincirinde `elle = True` sağlayıcı | S6.8 HATA (zincire konamaz) |
| AI84 anahtarı yok, `import ai84` | süreç ölmez; `Kisitlandi("anahtar_yok")` |
| `kurgu_render` önizlemesi ile `son_miks` final aynı stemlerden farklı LUFS veriyor | B15 yapısal test HATA |

### 4.8 Kesin kararların (atomik zincir + 6 özellik + ses kararı) kendi alanımda uygulanışı

#### 4.8.1 Atomik eylem zinciri (kesin karar 2) → ses
1. **Her fiziksel adım bir efekt olayıdır.** Adım `{id: "a1", fiil, govde, hedef, el_sekli, …}` → `efektler[{adim: "a1", …}]`. Fiil sözlüğü kategoriyi ve anı verir; malzeme
   dünyadan gelir: zemin mekânın `ses.json`'undan, kumaş kostüm kartından, nesne malzemesi nesnenin `ses.json`'undan.
   - "Kalemi al" örneği (yürü → sağ kolu uzat → başparmak + işaretle kavra): `a1 yurur` → zemin malzemesinde adım sesleri, adım boyunca yayılır (`an: yayil`);
     `a2 uzanir` → kumaş hışırtısı (`an: bas`); `a3 kavrar` → kalemin masaya sürtünmesi, **temas anında** (`an: son`).
   - Bitiş durumunun tutulduğu süre ("holds still") yeni efekt almaz; yalnız yatak duyulur. Hareketsizlik böyle okunur.
   - Mikro adımlar (çene sıkma, bakış) efekt zorunluluğu taşımaz.
2. **Flow'un `Sound:` cümlesi aynı listeden derlenir.** Veo görüntüyle senkron efekt üretir; biz o efekti ya kapılayarak kullanırız ya da kütüphane efektini **onun başlangıç anına** koyarız.
   Klibin sesi her durumda zaman referansıdır.
3. **Konuşmalı planda en çok 1 fiziksel adım vardır ve konuşmadan önce biter** (Z §2.3; Y02, Y02b). Adımın ani efekti ilk sözden ≥ 150 ms önce biter (S0.9); konuşmayı örtmez.
4. **Bitiş durumu = sonraki başlangıç → ses durumu da taşınır.** Bitişte "yanık fener sağ elde" varsa sonraki planlarda fener cızırtısı vardır; "zincirli" karakterin her
   adımına zincir şıngırtısı eklenir. Bu sesler dünya defterinden çalışma anında türetilir (plana yazılmaz). Nesne zıplamasının ses karşılığı böyle önlenir.
5. **Eylem üstünde kesme** (`kesme.tip: eylem`): iki plana yayılan ses olayı (kapının açılışı) klibe değil `SES_CIZELGESI.json`'a yerleşir; ses kesmenin üstünden akar ve kesmeyi örter.
6. **Konuşma da bir adımdır** (`tur: konusma`, `replik`, `cumleler`). Replik penceresi (`_derlenir.replik_zaman`) metin kapısının ve dudak denetiminin arama penceresidir
   (D: "aynı klip iki plana bölününce" dersi).

#### 4.8.2 Altı özellik
**(a) Videodan önce animatik + habersiz seyirci.**
- Animatik **seçilmiş son seslerle** kurulur (İ-2). Gerçek replik süreleri plana geri döner; süre kapısı (S2.13) video kredisinden önce çalışır. Kâğıttaki `kelime / 2,5` tahmini
  yerine o sesin gerçek hızı kullanılır.
- Animatikte gerçek ipucu müziği çalar; J/L, ekran dışı replik, ambiyans köprüsü ve müzik giriş-çıkışı ilk kez burada sınanır.
- Seyirci ajanı duyamaz. Ona **işitsel döküm** verilir. Konuşanın adı yazılmaz; ölçülmüş ses etiketi yazılır (İ-9). Seyirciye "ekran dışı sesi kime ait sandın?" sorulur;
  yanlışsa "kim konuştu belli değil" kopukluğu doğar. Kâğıttaki karşılığı ses tanıtım kuralıdır (S0.3).
- Kurgu izleme turunda döküm **plandan değil son miksten** çıkar (ASR + ölçülen olaylar). Müzik bir repliği bastırdıysa seyirci o repliği "duymaz" (S7.6); kâğıtta var diye
  seyirciye ulaştı sayılmaz (ARIS kör döküm ilkesi, A1 B4).

**(b) Dünya durumu defteri + otomatik zıplama denetimi.**
- Ses ayrı bir defter tutmaz; süreklilik uzmanının `DUNYA_DEFTERI.json`'unu ve sahne grubunun `zaman` alanını okur. Yatak katmanları (hava, gün saati, ateş, kalabalık) ve sürekli
  nesne sesleri (fener, zincir) **defterden türetilir**; her katmanın `kaynak` olgusu kayıtlıdır.
- Zıplama iki katta denetlenir: kâğıtta S0.10–S0.11 (yatak defterle çelişiyor mu; aynı mekân ve kesintisiz zamanda yatak değişti mi), seste S5.1–S5.3 (ölçülen seviye
  zıplaması, boşluk). `devam` geçişinde yatak çapraz geçiş yapmaz, kesintisiz sürer.

**(c) Referansla otomatik yüz kontrolü → sesin karşılığı: referansla otomatik ses kontrolü.**
- Her son replik karakterin evren ses merkeziyle karşılaştırılır (S2.9). Bu, yüzdeki SFace karşılaştırmasının ses tarafıdır.
- **Yüz–ses bağı:** ağzı oynayan yüzün kimliği (görüntünün `olcum/kimlik.py`'si) replik karakteri olmalıdır. Bu hem indirmede (S2.5) hem kurguda (S3.4) ölçülür.
  "Doğru ses, yanlış ağız" ve "doğru ağız, yanlış ses" ikisi de yakalanır.
- **Aksan** kimliğin parçasıdır (B5, S1.7, S2.16).
- Yaratık sesi evren kitinden gelir. Veo'nun her klipte yeniden icat ettiği yaratık sesi içerik olarak kullanılmaz, yalnız zaman referansıdır.

**(d) Kare zinciri (son kare → sonraki klibin başlangıcı) → ses zinciri.**
- `devam` geçişinde ambiyans aynı yatakla kesintisiz sürer; çapraz geçiş yapılmaz (S0.10).
- Zincirlenmiş iki klibin sınırında aynı olayın iki kez duyulması önlenir: sınırın iki yanında ±100 ms içinde aynı kategoriden iki olay varsa biri atılır (S5.11).
- Klibin ilk 0,3–1,0 sn'si durağandır (Z §2.2); Veo'nun bu kısımdaki ses başlangıcı ham kullanılmaz. Her parça 10–20 ms yumuşatılır (S5.10).
- Konuşmalı planda Bitir karesi kullanılmaz ([YÖN2] Y56). Zorlanmış bitiş karesinin dudak davranışına etkisi ölçülene kadar ses yolu bu riski almaz.

**(e) Kendi kendine öğrenen ders defteri.**
- Ortak biçim ve ortak `ders_defteri.kaydet()` kullanılır (§2.5). Kaynaklar: S0–S8 raporları ve `SESLER/diyalog.json → merdiven[]`.
- Ses dersleri dört biçimde uygulanır:
  - **`yol_kurali`** (ör. "fısıltı + ağız kısmen görünür → `tts`"): `ses_plani.py --taslak` sonraki partide uygular.
  - **`istem_kalibi`** (ör. "Veo 'Kestra'yı yanlış okuyor → `veo_metin` okunuş yazımı"): `istem_derle --hareket` uygular.
  - **`kara_liste`** (ör. "IC_ODA_02 yatağında uzak mırıltı var", "paylaşılan ses X kaldırıldı"): `DIZIN.json` ve `ses_sec.py` uygular.
  - **`esik`**: ölçüm dağılımları saklanır; eşik yalnız korkuluk içinde ve kanıtla değişir.
- Ses dersleri kâğıt aşamasında uygulanır (BK §7.5): kural, sonraki filmin değil sonraki **partinin** taslağına girer.

**(f) Kalıcı seri evreni kütüphanesi.**

| Evren yeri | İçerik | Neden |
|---|---|---|
| `karakterler/<id>/ses.json` + `ses/` | profil (aksan dahil), `veo_ses_tarifi`, `ses_etiketi_tr`, seçim (voice_id, bildirim süresi), ölçümler, gömme merkezi, referans kayıt; RVC seçildiyse banka ve model | Karakter filmden filme aynı ses ve aynı aksanla konuşur. **Ses sigortası:** paylaşılan ses kaldırılsa bile referans (ve varsa model) kimliği korur |
| `karakterler/<yaratik>/ses.json` + kit | evreye göre ses kiti (CC0 hayvan kayıtlarından katmanlı, perde/formant kaydırmalı) | Yaratık her filmde aynı "sesle" ötüşür |
| `mekanlar/<id>/ses.json` | zemin malzemesi, oda yanıtı, varsayılan yataklar, katman kuralları, imza sesleri | Aynı ev ikinci filmde aynı akustikle duyulur |
| `nesneler/<id>/ses.json` | imza sesleri (sürgü, anahtar, kılıç) | Kurulum → kullanım zincirinde nesne sesle de tanınır |
| `muzik/leitmotifler.json` + MIDI + referans çalım + kroma şablonu | motif notaları, dönüşümler, kullanım geçmişi; ana tema ve jenerik müziği | Seri boyunca aynı tema döner; motif ölçülebilir |

#### 4.8.3 Kesin karar 4 — ses ve dudak uyumu: gerekçe, merdiven ve hesap **(değişti)**

**Seçenekler (kullanıcının donanımı: RTX 3050 Ti 4 GB, Python 3.10; hesaplar: Flow, AI84)**

| Yol | Dudak | Ses tutarlılığı | Metin | Oyunculuk | 4 GB kartta | Maliyet (film) | Lisans | Karar |
|---|---|---|---|---|---|---|---|---|
| 1. Veo sesi olduğu gibi (`veo_ham`) | kusursuz | zayıf: her klipte ses yeniden icat ediliyor (A3 A2) | bazen kelime ekleyip atlıyor | iyi | gerekmez | 0 | Flow | Yalnız tek replikli figüran (İ-11); ana yolun ham maddesi |
| 2. TTS + süreye sığdırma (bugünkü `seslendir.py`) | zayıf (H/proje-b2 "dudakla gitmiyor") | tam | tam | TTS'nin; yüzle uyuşmayabilir | gerekmez | ≈ 13–16 bin kredi | AI84 koşulları | Yalnız ağzı görünmeyen replikte (`tts`) |
| 3. TTS + yerel dudak senkronu (MuseTalk 1.5) (`tts_dudak`) | iyi; ama ağız bölgesi 256 px'te yeniden üretilir (A3) | tam | tam | TTS'nin | **çalışır:** 8 sn klip ≈ 5 dk, fp16 [D-MT] | 0 $; zaman | kod MIT, model "any purpose, even commercially"; alt bileşenler kendi lisanslarıyla [D-MT] | Yedek (merdivenin geç basamağı); çıktı V2'den geçer |
| 4. Veo sesi + AI84 Voice Changer (`ai84_vc`) | kusursuz | iyi | Veo'nun | korunur | gerekmez | 840–1.040 sn × ≈ 2.000 kredi/sn (tahmin; `estimate` ile ölçülecek) ≈ 1,7–2,1 milyon kredi = bakiyenin (≈ 649 bin, 13.10) 2,6–3,2 katı | AI84 koşulları | Tüm film için HAYIR; tek kritik replik, tavan 20 bin |
| **5. Veo sesi + yerel ses dönüştürme** (`veo_donustur`; OpenVoice V2 / RVC / Chatterbox) | **kusursuz** (zamanlama Veo'nun) | **iyi–çok iyi** | Veo'nun → metin kapısı (S2.2–S2.4) | **korunur** (fısıltı/bağırmada zayıflayabilir) | çalışabilir; kıyasla ölçülecek (A3: "yerelde CPU veya 4 GB") | 0 $; ek kredi yok (referans mevcut TTS'ten) | OpenVoice MIT, RVC MIT [D-RVC], Chatterbox MIT (filigranlı) | **ANA YOL** |

Diyalog süresi: Z §2.6 toplam replik 2.100–2.600 kelime ÷ 2,5 kelime/sn (RE:konusma_hizi_kelime_sn) = 840–1.040 sn (hesap). Diyalog planı: 190 (RE:hedef_plan_dagilimi_40dk).

**Neden 5. yol:**
1. Seyircinin tek büyük şikâyeti karakter görünüşünün değişmesi (BK 1.4, 803 beğeni). Ağız bölgesini yeniden üreten her model yüz kapısının koruduğu şeyi bozma riski taşır.
   Ana yol görüntüye dokunmaz; G1/V2 kimlik ölçümleri geçerli kalır ([GÖR] §8.9).
2. Kullanıcının yaşadığı iki sorun ("ses klipten klibe değişiyor" ve "ses dudakla gitmiyor") aynı anda çözülür: dudak Veo'nun, ses evrenin.
3. Oyunculuk yüzle uyumlu kalır: Veo bağırırken ses de bağırır.
4. Dolar harcaması yoktur; AI84 kredisi küçüktür.
5. Ağzı görünmeyen repliklerdeki TTS ile aynı tınıya oturur, çünkü dönüştürücünün hedefi o TTS sesidir.
6. **(yeni)** Sağlayıcıdan bağımsızdır. Flow kısıtlanır da resmî Veo API'sine geçilirse ([ÜRE] §8.5) iki sağlayıcının sesi farklı olsa bile ikisi aynı evren sesine çevrilir.

**Ön koşullar (ana yolu güçlendiren üretim kuralları):**
- Konuşan her klipte istem `{Ad} {ton_fiili_en}, {veo_ses_tarifi}: "…"` biçimindedir; dize **aksanı** içerir ve birebir tekrarlanır (S0.4–S0.5, İ-3).
  Veo'nun ürettiği ses hedefe ne kadar yakınsa dönüştürücü o kadar az zorlanır (A3 A2).
- Replik bloğunda tek teslim vardır (S0.21). Konuşurken fiziksel adım yoktur (Y02). Konuşan yüz okunur ölçektedir (Y32). Dinleyenin ağzı kapalıdır (Y35).
- Dönüştürücüye yalnız hizalanmış söz pencereleri girer. Aynı klipteki yaratık sesi ya da gürültü insan sesine çevrilmez.

**Ses merdiveni (`ses_karar.py`; hata türüne göre; her basamak ölçülür, geçmezse sonrakine geçilir)**

| Hata (kapı) | 1. basamak | 2. basamak | 3. basamak | 4. basamak | Son |
|---|---|---|---|---|---|
| Veo konuşmadı, yanlış kişi ya da dinleyen konuştu (S2.1, S2.5) | Flow'da yeniden çekim, CORRECTION şablonu (kredi; en çok 2; aynı dalga) | `tts_dudak` (yerel; ağzı kapalı klibe TTS ile ağız) → V2 + S3 | Kurgucu: repliği ekran dışına taşıma (tepki planının üstü, L taşma; ses tanıtım kuralı) → `tts` | Yönetmen onarım: plan değişikliği | Açık rapor |
| Metin gri bantta ya da `tasidigi` kelimesi değişti (S2.2, S2.4) | `hikaye-yazari` replik_kabul (0 kredi): kabul → `duyulan_metin` altyazıya | Ret → yeniden çekim, "word for word" CORRECTION (en çok 2) | `tts_dudak` | Yönetmen onarım | Açık rapor |
| Ad yanlış (S2.3) | Yeniden çekim, ad CORRECTION + `veo_metin` (en çok 2); `istem_kalibi` ders adayı | `tts_dudak` | Ekran dışına taşıma → `tts` | — | Açık rapor |
| Dönüşüm kalitesi (S2.8–S2.10; ör. fısıltıda metalik) | Motor zincirinde sonraki motor (0) | Kurguda ağız görünmüyorsa (S3.7) → `tts` (0) | `ai84_vc` (tavan içinde; `estimate` ile önce hesap) | `tts_dudak` | Teslim değişikliğiyle yeniden çekim (`teslim` değişikliği `hikaye-yazari`'na istek) |
| Aksan kayması (S2.16, BAYRAK) | Ağız görünmüyorsa `tts` (0) | Yeniden çekim, aksan CORRECTION | `ai84_vc` | — | Ders kaydı |
| Dudak ofseti (S3.1) | Yerleşim hatasıysa `kurgu_uygula` düzeltmesi (0) | `tts_dudak` çıktısıysa yeniden işleme (0) | Yeniden çekim | — | Açık rapor |
| Ekran dışı replikte dinleyen ağzı oynuyor (S3.5) | Kurgucu: başka kırpma penceresi ya da aynı sahnenin başka tepki planı (0) | Yeniden çekim, "listens silently, mouth closed" CORRECTION | — | — | Açık rapor |
| Seviye, ambiyans, müzik, miks (S4–S7) | Otomatik yeniden işleme (0) | Müzik kipine revizyon (0) | — | — | Açık rapor |

- **Kalite önceliği (kesin karar 6):** Metin ve konuşan hatalarında önce yeniden çekim gelir, çünkü kendi Veo performansı yapay ağızdan iyidir. 0 kredili basamaklar yalnız
  kaliteyi düşürmediği durumda öne alınır: metnin sahibinin kabulü, ağzı zaten görünmeyen planda TTS.
- Yeniden çekimler `YENIDEN_URET.json`'a `kaynak_kapi: "S2"` ile girer. `kuyruk.py` bütçe kapısından ve Memmet'in tempo kurallarından geçer; Flow uyarısında DUR.
- 2 yeniden çekimden sonra aynı plan için üçüncü deneme yapılmaz ([YÖN] Y8 ile aynı mantık).

**Maliyet hesabı (AI84; TTS 1 kredi/harf, BK 6.4; kelime başına ≈ 6 harf (tahmin; [ÜRE] §7.1 ile aynı varsayım))**

| Kalem | Hesap | Kredi |
|---|---|---|
| Telaffuz testi | ≈ 10 ad × 3 replik × 60 harf | ≈ 1,8 bin (tahmin) |
| Ses seçimi | 6 karakter × 4 aday × 3 replik × ≈ 70 harf | ≈ 5 bin |
| Animatik TTS (bütün replikler) | 2.100–2.600 kelime × 6 harf | ≈ 12,6–15,6 bin |
| Animatik turlarında değişen replikler | ≈ %40 bir kez yeniden okunur (tahmin) | ≈ 5–6 bin |
| `tts` son sesleri | animatikle aynı metin → önbellek | 0 |
| OpenVoice referansı | mevcut TTS'ten kesilir | 0 |
| **Film başına** | | **≈ 25–30 bin** (tavan 60 bin) |
| RVC pilot bankası (seri başında; yalnız koşullar izin verirse) | 10 dk × 150 kelime/dk × 6 harf | ≈ 9 bin |
| RVC kazanırsa kalan ana karakterler (≤ 3) | 3 × 9 bin | ≈ 27 bin |
| **Seri kurulumu (bir kez)** | | **0–36 bin** (tavan 40 bin) |
| `ai84_vc` (kritik replik) | `estimate` ile ölçülür | ≤ 20 bin (tavan) |
| **İlk film, en kötü durum** | 30 + 36 + 20 | **≈ 86 bin** (bakiyenin ≈ %13'ü; ≈ 649 bin, 13.10, BK 6.4) |

- **Flow tarafı:** ses kaynaklı yeniden çekim = 190 diyalog planı × Veo sapma oranı. Oran bilinmiyor (SB3 ve ilk dalgada ölçülür). %15 varsayılırsa (tahmin)
  ≈ 29 klip × 12 kredi ≈ 340 kredi (hesap); RE:kredi_yeniden_deneme_payi'nin (%20; 4.860 × 0,2 ≈ 970 kredi, Z §2.6) içinde kalır.
- **Zaman tarafı:** `tts_dudak`'a düşen her 8 sn'lik klip ≈ 5 dk [D-MT]. Diyalog planlarının %10'u düşerse (tahmin) ≈ 19 klip ≈ 1,6 saat (hesap); gece koşar.

**Motor seçimi ölçüyle:** SB3 kıyası (arşiv klipleri + ilk filmin ilk 20 repliği). "TTS süreye sığdırma" kıyasa çıta olarak girer; ana yolun daha iyi olduğu sayıyla görülür.
RVC'nin ElevenLabs çıktısıyla eğitimi hukuken netleşmeden RVC denenmez; o durumda OpenVoice V2 (referansla, eğitimsiz) ve Chatterbox kıyaslanır.

#### 4.8.4 Müzik kaynağı kararı (lisans ve leitmotif) **(değişti)**

| Kaynak | Ticari YouTube lisansı | Leitmotif denetimi | Otomasyon | Donanım | Karar |
|---|---|---|---|---|---|
| **ACE-Step 1.5** (2B turbo) | MIT (depo) [D-AS]; ağırlık sayfası bu oturumda açılmadı | **"Cover" ve "Refer audio"** ile motif çalınışı girdi olur; BPM, ton, ölçü denetimi; sesten BPM/ton çıkarma [D-AS] | tam; Python API | "< 4 GB VRAM" iddiası; ≤ 6 GB katmanı INT8 + tam CPU offload; Python 3.11–3.12 (ayrı ortam) [D-AS]; 3050 Ti'de süre ölçülecek | **ANA üretici** (tema, doku, aksiyon) |
| **`midi_ornek`**: motif MIDI + örnek kütüphanesiyle çalma | MIDI çalıcı FluidSynth LGPL, yalnız çalıştırılır (bellekten); örnekler CC0 ya da MIT olmalı (ör. VSCO 2 CE, FluidR3_GM; ikisi de bellekten, doğrulanmalı) | **tam**: motif notası notasına döner | tam | CPU | **Motif omurgası** + her zaman çalışan yedek |
| ElevenLabs Music | SDK'da `music.compose` var [D-EL]; AI84'te var mı bilinmiyor; plan koşulları okunmadı | istemle | API | bulut | P2: koşullar okununca |
| Lyria / Gemini API | Google koşulları okunmadı | istemle | API | bulut, dolar | P2 |
| Gemini uygulamasında elle (B2'de FM01–FM34) | Google koşulları | zayıf | **elle iş** → kesin karar 1, [ÜRE] M2 ile çelişir | — | **HAYIR** (İ-6) |
| YuE2 | bireysel üretici para kazanabilir, şirket lisansı ayrı (A3) | — | — | ağır | HAYIR: sözlü şarkıya odaklı (bellekten); bize sözsüz alt müzik lazım |
| MusicGen | ağırlıklar CC-BY-NC (A3) | — | — | — | HAYIR |
| Stable Audio Open | ağırlık lisansı belirsiz (A3) | — | — | — | HAYIR (netleşene kadar) |

**Karar:**
1. Leitmotifin kimliği **sembolik** tutulur: motif, `muzik` kipinde ajanın yazdığı **özgün notalardır** (perde + süre listesi). `muzik.py` MIDI'yi üretir ve referans olarak çalar.
   "Aynı tema döndü mü?" sorusu böylece ölçülebilir (kroma şablonu, S6.7). Ezgi özgün olduğu için Content ID riski en düşük kaynak budur.
2. İpuçları ACE-Step 1.5 ile yerelde üretilir (aday başına 3). Motifli ipucunda motifin çalınmış hâli "Cover/Refer audio" girdisidir. İstemde enstrüman, ton ve tempo yazar.
3. `tema` ipucu 3 adayda da motif testini geçemezse (S6.7) o ipucu `midi_ornek` ile yapılır (her zaman yasal, her zaman motifli). `doku` ve `aksiyon` ipuçlarında motif şartı yok.
4. Her seçilen dosyanın kaynak kaydı tutulur (model, sürüm, lisans, istem, tohum, referans motif, tarih, SHA-1). ACE-Step README'si "stilistik benzerlik yüzünden istemeden
   telif ihlali" riskini kendisi yazıyor [D-AS]. Bu yüzden kayıt, Content ID itirazının kanıtıdır. Yayından önce isteğe bağlı ön kontrol yayın uzmanının onaylı adımıdır.
5. Lyria/Gemini **ambiyans için hiçbir zaman** kullanılmaz (BK 5.1.2). Müzik için de koşulları okunmadan ana yol olmaz.

#### 4.8.5 Diğer kesin kararlar
- **Karar 1 (yalnız konu sorulur):** ses seçimi, müzik, efekt indirme, yol ve yedek kararları ekiptedir; ölçüyle ve `KARAR_DEFTERI.md`'de gerekçeyle verilir.
  `SES_SECIM.html` ve animatik bilgi içindir. CC0 indirme izni kurulumda bir kez alınır (BK 5.1.4'teki "indirme kullanıcı onayıyla" kuralı bu biçime çevrilir).
  AI84 harcaması bütçe kapısıyla açılır; soru sorulmaz (İ-2).
- **Karar 5 (Memmet, bot tespiti):** ses betikleri Flow'a hiçbir gönderim yapmaz. SC1 yalnız inen dosyayı okur. Ses kaynaklı yeniden çekimler normal kuyruktan gider; Memmet'in
  tempo ayarları ve "olağan dışı uyarısında DUR" kuralı aynen geçerlidir. Merdiven, yeniden çekim sayısını azaltacak biçimde kuruludur: sesi bozuk ama dudağı doğru klip
  yeniden çekilmez, dönüştürülür.
- **Karar 6 (üstün körü iş yok):** sessiz geri dönüşler kaldırıldı (§4.6.1). Her replik ölçülür. Motor kıyası yapılmadan motor seçilmez. Lisansı belgelenmemiş müzik ya da
  efekt kullanılmaz. Ucuz diye Wav2Lip ya da ticari olmayan model kullanılmaz. Tek miks kodu, önizlemenin finalle aynı sesi vermesini garanti eder. "Ölçülemedi" GEÇ sayılmaz.

### 4.9 Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

#### 4.9.1 Riskler ve önlemler

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | ElevenLabs/AI84 koşulları: TTS çıktısıyla dönüştürme modeli eğitmek ve paylaşılan sesi bir aracı üzerinden ticari kullanmak izinli mi bilinmiyor; AI84 kriptoyla alınmış bir aracı (06_SERVISLER) | Seri sesi hukuken kırılgan olabilir | Eğitim gerektirmeyen OpenVoice V2 (yalnız referans) önce; RVC yalnız koşullar okununca; ElevenLabs'ta Voice Design var [D-EL] (AI84'te var mı açık soru) → kendi tasarladığımız ses; bildirim süresi uzun sesler (S1.1) |
| R2 | **(yeni)** Aksan kayması: dönüştürücü aksanı Veo'dan taşır | "Sesi değişti" | Aksanlı `veo_ses_tarifi` (İ-3), S1.7, S2.16, ağız görünmüyorsa `tts`, ders kaydı |
| R3 | Dönüştürücü Veo'nun gürültülü konuşma kanalında, fısıltıda ve bağırmada metalik ses üretebilir | S2'de çok replik kalır | Motor kıyası, söz penceresi kapısı, BS-RoFormer ayrıştırma, merdiven, `yol_kurali` dersi |
| R4 | 4 GB kart: ACE-Step (offload), MuseTalk (≈ 5 dk/klip), RVC eğitimi, ayrıştırma aynı anda koşarsa bellek yetmez ya da süre uzar | Süre | Aynı anda tek ağır model; gece kuyruğu; SB0 ölçümü; süreler ilk filmde ders defterine |
| R5 | **(yeni)** Çok sayıda Python sürümü ve ortam (3.10 ana, 3.11–3.12 ACE-Step, 3.12 RVC, 3.10 + torch 2.0.1 MuseTalk) | Kurulum kırılır, disk dolar | Ayrı sanal ortamlar; `kurulum.py` sınar ve raporlar; eksik ortam yalnız kendi basamağını kapatır; disk denetimi ([ÜRE] H0) |
| R6 | Veo'nun metin sapma ve hiç konuşmama oranı bilinmiyor | Yeniden çekim kredisi | SB3 + ilk dalgada ölçülür; bütçe önizlemesine yazılır |
| R7 | Omuz üstü ya da iki kişilik karede Veo dinleyeni konuşturabilir | Yanlış ağız | S2.5 indirmede; S3.4–S3.5 kurguda; istemde "listens silently, mouth closed" (Y35) |
| R8 | ACE-Step orkestra gerçekçiliği ve motif sadakati belirsiz; MIDI çalımı "maket" gibi duyulabilir; YZ müziğine yanlış Content ID talebi | Müzik kalitesi / yayın | Aday başına 3 üretim + ölçüm; özgün motif; kaynak kaydı; isteğe bağlı yayın öncesi kontrol |
| R9 | CC0 kütüphanesi ince (62 efekt + yataklar, AR); 45–55 sahnelik filme yetmeyebilir | Tekrar eden yataklar | SB4 eksik efekt temini; aynı yatağın aynı filmde farklı mekânda kullanılmaması (B) |
| R10 | Kullanıcı CapCut'ta sesle oynarsa master yerleştirmesi bu kararı ezer | Kullanıcının kararı kaybolur | SF1: elle ses ayarı varsa yeniden karıştırma yok, yalnız ölçüm ve tek kazanç (S8.2) |
| R11 | MediaPipe sürümü (OpenMontage 0.10.14 sabit; ana hat için görüntü uzmanı sabitliyor) | Ağız ölçümü kırılır | Tek sürüm görüntüyle ortak; OpenMontage kendi ortamında |
| R12 | Kısa replikte (< 1,5 sn, tahmin) konuşmacı gömmesi güvenilmez | Yanlış HATA | Kısa replik aynı sahnedeki komşularıyla birleştirilip ölçülür |
| R13 | Ölçüm modellerinin lisansı (konuşmacı gömmesi modelinin veri seti; SyncNet'te lisans dosyası yok, A3) | Hukuki belirsizlik | Yalnız ölçüm; çıktıya girmez; lisans notu kurulum raporunda |
| R14 | **(yeni)** MuseTalk ağız bölgesini 256 px'te üretir (A3); yakın planda bulanıklık | Görüntü kalitesi | Merdivenin geç basamağı; V2 + S3 zorunlu (S2.15); tutmazsa yönetmen onarımı |
| R15 | **(yeni)** AI84 süzgeçleri, `seed`, `previous_text/next_text` iletmeyebilir | Ses seçimi ve tutarlılık zayıflar | Yerelde süzme; önbellekteki dosya tek kaynak (aynı replik yeniden okutulmaz); ilk kurulumda sınanır |
| R16 | Paylaşılan ses kütüphaneden kaldırılabilir | Seri sesi kaybolur | Bildirim süresi süzgeci; referans kayıt; RVC seçildiyse model |

#### 4.9.2 Kalan çakışmalar (ekip ya da sahibinin kararı gerekiyor)
1. **`hikaye-yazari` `replik_kabul` kipi** (senarist): gri bantta Veo'nun metnini kabul ya da ret yetkisi metnin sahibinde olsun (İ-5, §4.3.2).
2. **`teslim` tek alan** (senarist + yönetmen): [SEN2] `teslim`'i, [YÖN2] `ton_fiili`'ni yazıyor. Önerim: `teslim` yazılır, `ton_fiili_en` ve `seviye` türetilir; sözlük genişletilebilir (Ç-1).
3. **`KURGU_PLANI` ↔ `SES_CIZELGESI` ayrımı ve tek miks kodu** (kurgucu): ★İ-1.
4. **Ders defteri ekleri** (defter sahibi): ses kategorileri, `yol_kurali` ve `kara_liste` türleri (§2.5).
5. **`olcum/ses.py`, `olcum/dudak.py`** görüntünün `olcum/` paketine girer; MediaPipe tek sürüm (görüntü).
6. **`veo_ses_tarifi` 12 kelime** ve hareket istemi bütçesi Y46 (yönetmen).
7. **Bütçe anahtarları** `ai84_seri_kurulum_tavan`, `ai84_vc_tavan_film` ve müzik zincirinde `gemini_elle`'nin olmaması (üretim, İ-6).
8. **Rapor klasörü ve çıkış kodları** (orkestratör): araçlarım ayardan okur.
9. **SC1'in indirme sonrası kancası** (üretim/orkestratör): Memmet'in indirme döngüsüne dokunmadan, `film.py`'nin dalga görevinde ayrı süreç olarak.

#### 4.9.3 Açık sorular (cevabı bilinmiyor; uydurulmadı)
1. Flow'da (Omni 1.1 Flash) ses referansı ya da sabit ses özelliği var mı? Repoda bilgi yok. Varsa ana yolun ham maddesi çok iyileşir.
2. AI84: paylaşılan ses aramasında hangi süzgeçler iletiliyor; `eleven_v4` için `voice_settings`, `seed`, `previous_text/next_text`, telaffuz sözlüğü, Voice Design ve müzik
   servisi var mı? (ElevenLabs SDK'da var [D-EL]; MEMORY.md'ye göre AI84'te ses efekti servisi yok.) İlk kurulumda küçük denemelerle ölçülür.
3. ElevenLabs/AI84 koşulları: TTS çıktısının dönüştürme modeli eğitmekte ve referans olarak kullanılması; paylaşılan seslerin aracı üzerinden ticari kullanımı; ses sahibince kaldırılınca ne olur?
4. Gemini/Lyria ve ElevenLabs Music'in para kazanılan YouTube videosunda kullanım koşulları.
5. ACE-Step 1.5'in 3050 Ti'de ipucu başına süresi ve "Cover" ile motif sadakati (README özelliği doğruladı; kalite ölçülmedi).
6. RVC eğitiminin 4 GB'ta süresi (README "poor graphics cards" diyor, süre vermiyor).
7. Veo'nun ses biçimi (örnekleme hızı, kanal sayısı): arşivdeki bir klipte `ffprobe` ile bakılacak.
8. Veo'nun metin sapma ve konuşmama oranı (SB3 + ilk dalga).
9. `pycapcut` ses parçalarında seviye anahtar karesi destekliyor mu? Destekliyorsa müzik kısması CapCut'ta canlı kalır; yoksa kısma dosyaya işlenir ([KUR] açık soru 3 ile aynı).
10. Lisansı temiz, yerelde çalışan bir aksan sınıflayıcısı var mı? Yoksa `dinleyici` için hangi API kullanılacak? Hatta Gemini API anahtarı tanımlı değil ([SEN] Q2).
11. Örnek kütüphanesinin (SF2/SFZ) seçimi ve lisansının belgeyle doğrulanması.
12. ElevenLabs v4 ton etiketlerinin tam listesi (`teslim` sözlüğündeki `tts_etiket` sütunu tahmin).
13. Konuşmalı planda Bitir karesinin dudağa etkisi ([YÖN2] açık soru 3; ölçülene kadar kullanılmıyor).
14. Kullanıcının `SES_KUTUPHANESI` klasörünün gerçek içeriği (`LISANS.txt` var, AR); ilk dizinlemede belli olur.

---
*Bu belge ses-muzik uzmanının 2. tur önerisidir. Sayıların kaynağı satırlarında yazılıdır. **(tahmin)** ve **(bellekten)** işaretli değerler §4.7.9 kalibrasyonuyla ilk
filmde ölçülecek ya da kurulumda doğrulanacaktır.*
