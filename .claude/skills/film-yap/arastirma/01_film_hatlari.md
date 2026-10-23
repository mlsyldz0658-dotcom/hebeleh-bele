# 01 — Çok ajanlı / LLM yönetimli YZ film hatları: araştırma

Tarih: 23 Ekim 2026. Hazırlayan: Claude (araştırma ajanı).
Amaç: GitHub'daki ve makalelerdeki senaryo → storyboard → plan listesi → video → kurgu hatlarını
incelemek, bizim hatta (Flow/Veo + Nano Banana + ElevenLabs/AI84 + CapCut/pycapcut, Python 3.10,
Windows) alınabilecek **fikir ve kodları** çıkarmak.

## Nasıl doğrulandı (önce bunu okuyun)

- **Yıldız, son push tarihi, lisans**: GitHub arama API'sinden (MCP `search_repositories`) okundu.
  "Son push" = `pushed_at` (son commit için yaklaşık değer). Yıldızlar 23.10.2026 tarihlidir.
- **README içeriği**: depo sayfası açılıp (WebFetch) okundu. WebFetch sayfayı küçük bir modelle
  özetler. Bu yüzden ayrıntılar "README'de yazdığı kadarıyla" geçerlidir, kod satır satır okunmadı.
- **arXiv sayfaları açılamadı** (bu oturumun ağ kuralı arxiv.org'u engelliyor). Makale iddiaları
  web arama özetlerinden alındı ve **"(makale; arama özeti)"** diye işaretlendi. Kesin değildir.
- `lisans: yok` = depoda lisans dosyası yok. Bu durumda kodu kopyalamak hukuken serbest değildir.
  Yalnızca fikir alınır.
- Bot tespitini atlatan, insan taklidi yapan ya da Flow kısıtlarını aşmaya yarayan hiçbir araç
  önerilmedi.

## Kısa sonuç

Bizim hat, açık kaynaktaki çoğu hattan **daha olgun bir kalite döngüsüne** sahip: habersiz seyirci,
süreklilik listesi, dudak denetimi, LUFS gibi parçalar başka hiçbir projede bir arada yok. Açık
kaynak projelerin neredeyse hepsi **ücretli API anahtarıyla** (Seedance, Kling, Veo API, GPT Image,
MiniMax, FAL) çalışıyor. Hiçbiri Flow aboneliğini kullanmıyor. Bu, OpenMontage'da gördüğümüz durumun
aynısı. Bu yüzden **hiçbiri hattımızın yerine geçmiyor**. Alınacak değer çoğunlukla **şema, kalite
kapısı ve iş akışı fikirlerinde**. Doğrudan kullanılabilecek kod az: PySceneDetect, OpenTimelineIO ve
izinli lisanslı birkaç küçük denetim betiği.

---

## A. Akademik "film ajanı" projeleri (istenen liste)

### A1. FilmAgent → bugün **VideoClaw** (HITsz-TMG)
- **Adres:** https://github.com/HITsz-TMG/VideoClaw (`github.com/HITsz-TMG/FilmAgent` bu depoya
  yönleniyor; depo 29.08.2024'te açılmış. Yeniden adlandırma olduğu yönlendirmeden çıkarıldı, README
  bunu açıkça söylemiyor.)
- **Yıldız / son push / lisans:** ~1.870 / 26.08.2026 / MIT
- **Ne yapıyor (README):** Fikirden filme giden aşamalı hat. Senaryo (çok sahneli, diyaloglu,
  devamı yazılabilir), karakter/sahne tasarımı, plan plan storyboard (kamera, aksiyon, referans),
  plan başına referans görsel, video (ilk kare / ilk+son kare / referans modu), kurgu. Her aşamanın
  çıktısını insan görüp düzeltebiliyor. Çıktıda `storyboard.json` var, alan listesi README'de yok.
  Sağlayıcılar: OpenAI, Gemini, DeepSeek, DashScope, ARK, Kling. Varsayılan ayar DashScope ve ARK
  anahtarı istiyor.
- **FilmAgent makalesi (makale; arama özeti):** arXiv 2501.12909, SIGGRAPH Asia 2024. Rol ajanları
  (yönetmen, senarist, oyuncular, görüntü yönetmeni) üç aşamada çalışıyor: fikir, senaryo, kamera.
  İki işbirliği yöntemi var:
  - **Critique-Correct-Verify** (eleştir → düzelt → doğrula): yönetmen senaristi eleştirir,
    oyuncular repliği karakter profiline göre denetler.
  - **Debate-Judge** (tartış → hakem): kamera seçimleri tartışılır, bir hakem karar verir.
  GPT-4o kullanan çok ajanlı düzenin tek ajanlı o1'i geçtiği bildiriliyor. İnsan puanı 3,98/5.
  Orijinal sürüm Unity 3B sahnelerde çekim yapıyordu.
- **Bizim için:** **Fikir.** CCV döngüsü bizim "hikâye odası → habersiz seyirci → v2" döngümüzün
  aynısı. Ekleyeceğimiz şey **oyuncu ajanı**: her karakter yalnız kendi repliklerini kendi karakter
  kartına göre denetler ("Mara bunu böyle söylemez"). Debate-Judge kamera ve plan tartışmasında
  kullanılabilir.
- **Windows / Py3.10:** install.bat var, Python 3.9+, Node 18+. **Ücretli API:** evet.

### A2. MovieAgent (showlab, NUS)
- **Adres:** https://github.com/showlab/MovieAgent
- **Yıldız / son push / lisans:** ~370 / 26.03.2025 / **yok**
- **Ne yapıyor:** Senaryo özeti (`script_synopsis.json`) ve karakter bankasından (fotoğraf ve ses
  dosyası) çok sahneli, çok planlı uzun video üretiyor. "Hiyerarşik CoT planlama" kullanıyor:
  yönetmen, senarist, storyboard sanatçısı ve mekân sorumlusu ajanları sahneyi, kamerayı ve
  sinematografiyi kurguluyor. LLM GPT-4o, görsel ROICtrl/StoryDiffusion, video SVD/HunyuanVideo-I2V.
  Kurulum conda, Python 3.8, CUDA 12.1. Yerel GPU şart.
- **Bizim için:** **Fikir.** Planlama **film → sahne → plan** diye üç katmanlı ve her katman bir
  öncekinin çıktısını alıyor. Bizdeki "parti → plan" yapısının üstüne bir **sahne (mekân + zaman)
  katmanı** eklemek süreklilik listesini sadeleştirir. Kod lisanssız, alınmaz.
- **Windows / Py3.10:** uygun değil (GPU modelleri, Py3.8). **Ücretli API:** GPT-4o.

### A3. ViMax (HKUDS)
- **Adres:** https://github.com/HKUDS/ViMax
- **Yıldız / son push / lisans:** ~12.700 / 30.09.2026 / MIT
- **Ne yapıyor:** "Yönetmen, senarist, yapımcı, video üretici bir arada." Dört akış var: Idea2Video,
  Script2Video, Novel2Video, AutoCameo. Ara çıktılar: hikâye, karakterler, senaryo, storyboard,
  planlar, film. **README'de doğrulanan önemli özellik:** her anahtar kare için **2 aday paralel
  üretiliyor ve görüntü anlayan sohbet modeli birini seçiyor** (`num_candidates: 1` ile kapanıyor,
  maliyeti artırdığı belirtiliyor). Ayarlar YAML (`configs/*.yaml`), anahtarlar ortam
  değişkeninden (`VIMAX_LLM_API_KEY`). Örnek sağlayıcılar: OpenRouter, Nano Banana, **Veo API**.
- **Bizim için:** **Fikir + kısmen kod deseni (MIT).** (1) *Aday üret, görüntü modeli seçsin* fikri
  görsel aşamamıza çok uygun, çünkü Gemini ajanında görsel kredisi yok. (2) LLM / görsel / video
  bloklarının `model, base_url, api_key, class_path` ile tanımlandığı YAML yapısı sağlayıcı
  soyutlamamız (`AYARLAR/`) için iyi bir örnek.
- **Windows / Py3.10:** Windows destekli ama **Python 3.12** (uv). Doğrudan kurulmaz, desen alınır.
  **Ücretli API:** evet (LLM, görsel, video).

### A4. Anim-Director ve AniMaker (HITsz-TMG)
- **Adres:** https://github.com/HITsz-TMG/Anim-Director (iki proje aynı depoda)
- **Yıldız / son push / lisans:** ~263 / 07.01.2026 / **yok**
- **Ne yapıyor:** Anim-Director (SIGGRAPH Asia 2024) LMM tabanlı animasyon ajanı. AniMaker
  (arXiv 2506.10540, SIGGRAPH Asia 2025) çok ajanlı uzun animasyon üretiyor.
- **AniMaker (makale; arama özeti):** Dört ajan var: Director (storyboard), Photography (klip
  üretimi), **Reviewer** (adayları puanlar), Post-Production (birleştirme).
  - **MCTS-Gen:** klip adaylarının arasında Monte Carlo ağaç araması benzeri bir yöntemle
    "umut vaat eden" adayları genişletip kaynak tasarrufu yapıyor.
  - **AniEval:** her klibi **komşu klipleriyle birlikte** değerlendiriyor: hikâye tutarlılığı,
    eylemin tamamlanması, animasyona özgü kalite.
- **Bizim için:** **Fikir.** (1) AniEval'in "klibi önceki ve sonraki planla birlikte yargıla" ilkesi
  bizim **kurgu izleme denetimi** ve **görsel süreklilik denetimi** için doğrudan uygulanabilir. Tek
  kare değil, üçlü pencere (n-1, n, n+1) gösterilir. (2) MCTS-Gen'in sade hâli: önce ucuz aday
  (görsel), sadece kazanan videoya gider. Bu bizim "kredi en sonda" kuralımızla uyumlu.
- **Windows / Py3.10:** belirsiz (Jupyter). **Ücretli API:** README açılışında belirtilmemiş
  (doğrulanamadı).

### A5. Mora (lichao-sun)
- **Adres:** https://github.com/lichao-sun/Mora
- **Yıldız / son push / lisans:** ~1.590 / 10.10.2024 / **yok**
- **Ne yapıyor:** "Sora'ya benzeyen" çok ajanlı genel video üretimi (metin→görsel→video, uzatma,
  düzenleme). README çelişkili: bir yerde "kod yayınlandı", başka yerde "yakında" yazıyor.
- **Bizim için:** Değeri düşük ve eski. Alınacak bir şey yok.

### A6. StoryAgent (MBZUAI vd., ICLR 2025)
- **Makale:** arXiv 2411.04925 (makale; arama özeti). Ajanlar: Agent Manager, Story Designer,
  Storyboard Generator, video üretici, değerlendirme. Kahramanın tutarlılığını LoRA tabanlı I2V ile
  sağlıyor.
- **GitHub:** **Resmî depo bulunamadı (doğrulanamadı).** "MM-StoryAgent" farklı bir projedir (A8).
- **Bizim için:** Yalnız fikir: "Agent Manager" bizim `film.py` orkestratörünün karşılığı.

### A7. DreamFactory (Xie vd., 2024)
- **Makale:** arXiv 2408.11788 (makale; arama özeti). Çok ajanlı, uzun ve çok sahneli video. "Key
  Frames Iteration Design" ve CoT kullanıyor. İki ölçüt öneriyor: **Cross-Scene Face Distance**
  (sahneler arası yüz mesafesi) ve **Cross-Scene Style Consistency** (sahneler arası stil
  tutarlılığı).
- **GitHub:** **Depo bulunamadı.** Makale "kabulden sonra yayınlanacak" diyor, yayınlanıp
  yayınlanmadığı doğrulanamadı.
- **Bizim için:** **Fikir:** *Sahneler arası yüz mesafesi*, karakter kartına göre yüz benzerliği
  ölçüsü olarak görsel süreklilik kapısında kullanılabilir (yerel bir yüz gömme modeliyle). Kod yok.

### A8. MM-StoryAgent (X-PLUG / Alibaba)
- **Adres:** https://github.com/X-PLUG/MM_StoryAgent
- **Yıldız / son push / lisans:** ~309 / 23.08.2024 / Apache-2.0
- **Ne yapıyor:** Anlatımlı masal kitabı videosu üretiyor (görsel, konuşma, efekt, müzik). Hikâye
  yazarı çok turlu bir soru-cevapla (`qa_outline_story_writer`, `max_conv_turns`) taslağı
  geliştiriyor. **Hikâyeyi GPT-4 üç rubrikle puanlıyor** (Attractiveness / Warmth / Education) ve
  çok ajanlı yazımı tek istemle karşılaştırıyor (4,65'e karşı 4,47). YAML ayar: her ajan için
  `tool`, `cfg`, `params`.
- **Bizim için:** **Fikir.** "Soru soran ajan + yazan ajan" ile taslak çıkarma (outline) brifing
  aşamasına uyar. Puan rubriği bizim için fazla basit. Bizimki daha iyi.
- **Ücretli API:** README'de belirtilmemiş.

### A9. VideoStudio (ECCV 2024) ve VideoDirectorGPT (COLM 2024)
- **VideoStudio:** https://github.com/FuchenUSTC/VideoStudio, ~33 yıldız / 05.07.2024 /
  Apache-2.0. LLM, istemi sahne sahne bir senaryoya çeviriyor: olay, ön ve arka plan varlıkları,
  kamera hareketi. Yinelenen varlıklar için referans görsel üretip her sahneyi bu görsellerle
  koşullandırıyor. Kendi difüzyon modeli var (GPU).
- **VideoDirectorGPT:** https://github.com/HL-hanlin/VideoDirectorGPT, ~183 yıldız, **lisans yok,
  kod yok** (README "Code coming soon", sadece görseller). Plan şeması: sahne açıklaması, sahne
  başına varlık ve arka plan listesi, kare kare kutu yerleşimi, **tutarlılık grupları** (aynı
  varlık hangi sahnelerde tekrar ediyor).
- **Bizim için:** **Fikir:** "tutarlılık grubu" kavramı. `SAHNELER.json`'da her varlığın (karakter,
  nesne, mekân) geçtiği planların listesi otomatik çıkarılırsa süreklilik denetçisi o planları yan
  yana karşılaştırabilir.

### A10. StoryDiffusion ve AniDoc (model projeleri, hat değil)
- **StoryDiffusion:** https://github.com/HVision-NKU/StoryDiffusion, ~6.490 / 26.09.2024 /
  Apache-2.0. Tutarlı karakterli görsel dizisi üreten bir difüzyon yöntemi. Yerel GPU şart. Biz
  Nano Banana kullandığımız için **gereksiz**.
- **AniDoc:** https://github.com/robbyant-research/AniDoc, ~573 / 15.04.2025 / Apache-2.0. Çizgi
  animasyon **renklendirme** modeli. Bizim fotogerçekçi hattımızla **ilgisi yok**.
- **MovieDreamer:** https://github.com/aim-uofa/MovieDreamer, ~325 / 10.08.2024 / lisans yok.
  Model araştırması. İlgisiz.

---

## B. 2026'nın pratik "senaryodan filme" platformları

Bu projeler akademik olanlardan çok daha popüler, çoğu Çin kısa dizi (短剧) pazarı için yazılmış.
Hepsi ücretli API ile çalışıyor.

### B1. ArcReel — **en yakın akraba**
- **Adres:** https://github.com/ArcReel/ArcReel
- **Yıldız / son push / lisans:** ~5.670 / 22.10.2026 / **AGPL-3.0** (ek koşullar NOTICE'te)
- **Ne yapıyor:** Romanı veya senaryoyu karakter / sahne / nesne varlıklarına, bölüm senaryosuna,
  storyboard karelerine, video kliplerine, seslendirmeye ve **剪映 (Jianying) taslağına** çeviren,
  kendi sunucunda çalışan bir stüdyo. Her aşamayı ajan yürütür ya da insan düzeltir. **Maliyeti
  üretimden önce ve sonra gösteriyor.**
- **Doğrulanan bağımlılıklar (pyproject.toml):** `claude-agent-sdk`, `anthropic`,
  **`pyjianyingdraft>=0.3.0`**, `google-genai`, `instructor`, `jsonschema`, `mcp`. Python **>=3.12**.
  README, CapCut (uluslararası) uyumluluğunun doğrulanmadığını söylüyor.
- **Bizim için:** **Fikir.** (1) Claude Agent SDK ile aşama yürüten bir orkestratörün çalışan
  örneği. (2) Üretim öncesi maliyet önizleme. (3) Karakter, sahne ve nesne **varlık kütüphanesi**
  (bizdeki "kartlar"). AGPL olduğu için kod kopyalanmamalı. Hattımız bunu dağıtırsa tüm kodu
  AGPL'ye çevirmek gerekir.
- **Windows / Py3.10:** yalnız Docker Compose. Py3.12. **Uygun değil.** **Ücretli API:** evet.

### B2. drama-skills (zenstory-ai) — **en çok fikir alınacak yer**
- **Adres:** https://github.com/zenstory-ai/drama-skills
- **Yıldız / son push / lisans:** ~3.240 / 20.10.2026 / **MIT**
- **Ne yapıyor:** Claude Code ve Codex için 11 skill: analiz, uyarlama, yazım, varlıklar, görsel
  istemleri, storyboard, video istemleri, **produce**, edit, **review**.
- **README'den doğrulanan önemli kurallar:**
  - Her bölümde **beş yetkili belge** var: senaryo, görsel tasarım, storyboard, görsel istemleri,
    video istemleri (ve kurguda bir kesim listesi). Her belge yalnız kendi kararlarının sahibi.
  - `creator_markdown_check.py` **belgeler arası çapraz kontrol** yapıyor. Örnekler: anahtar kare
    isteminde adı geçen bir karakter görsel dayanakta yoksa ve "kadraj dışı" diye işaretlenmemişse
    rapor ediyor. Storyboard'daki plan süresi video istemindeki süreden farklıysa rapor ediyor.
  - **Başlangıç ve bitiş durumu kuralı:** storyboard her planın başlangıcını ve bitişini yazar.
    Video istemi **yalnız bu iki durum arasındaki hareketi** anlatır ve kabul edilmiş süreyi
    değiştiremez.
  - **Dondurulmuş anahtar kare:** planın başlangıç karesi tek bir görsel olarak çizilir ve her kare
    kendi görsel dayanağını belirtir.
  - **Produce aşaması:** her görsel, video, ses ve müzik işi önce dosya olarak önizlenir (adet,
    içerik, referans, parametre, çıktı, adaptör). **Açık onay gelmeden ücretli API çağrılmaz.**
  - Storyboard alanları: plan no/başlık, kamera hareketi, başlangıç, bitiş, görsel dayanak, kaynak
    alıntısı, ses, süre, anahtar kare istemi, kadraj dışı notlar.
- **Bizim için:** **Fikir + küçük kod (MIT).** Çapraz kontrol betiğinin mantığı, bizdeki
  `kontrol.py` ve istem doğrulayıcı için birebir uygun. Python 3.9+ ve ffmpeg yeterli, GPU yok.
  Skill'ler Çince ama mantık dilden bağımsız.
- **Ücretli API:** yazım ajanın kendi modeliyle, medya üretimi isteğe bağlı adaptörlerle yapılıyor.

### B3. DirectorSKILL
- **Adres:** https://github.com/wuwangzhang1216/DirectorSKILL
- **Yıldız / son push / lisans:** ~256 / 31.08.2026 / MIT
- **Ne yapıyor:** Claude Code için yönetmen skill'i: plan listesi, anahtar kare ve video istemleri,
  yönetmen stili katmanları.
- **README'den doğrulanan kurallar:**
  - Plan listesi sütunları: hikâyedeki işlev, boyut, lens, açı, kamera, **blocking (başlangıç →
    hareket → bitiş)**, ışık yönü, **süreklilik çapaları**, **risk**.
  - "Video modeli çoğunlukla durağan karenin karar verdiğini canlandırır. Kareyi düzeltmek videoyu
    yeniden denemekten ucuzdur."
  - "Kimlik dizeleri, ışık yönü, ekran yönü ve dönem kilitleri **bir kez yazılır ve kelimesi
    kelimesine tekrarlanır**."
  - Süreklilik geometrisi: aksiyon ekseni, 30° kuralı, ekran yönü, bakış eşleşmesi. Bir
    **Continuity Bible** şeması var: karakter, mekân, nesne, plan.
  - Dört istem biçimi: S1 yalnız hareket, S2 tam tarif, S3 kare çifti, S4 zaman damgalı çoklu plan.
- **Bizim için:** **Fikir.** Bizim "sabit stil son eki" kuralımızın genişletilmiş hâli. Karakter
  kimlik dizesi + ışık yönü + ekran yönü ayrı alanlar olarak `SAHNELER.json`'a eklenir, istem bu
  alanlardan **kodla birleştirilir**, ajan elle yazmaz.

### B4. ARIS-Movie-Director
- **Adres:** https://github.com/wanshuiyin/ARIS-Movie-Director
- **Yıldız / son push / lisans:** ~73 / 17.10.2026 / MIT
- **Ne yapıyor:** Bulanık bir hikâyeden çapraz modelle denetlenmiş görsel film/çizgi roman üretiyor
  (henüz video yok).
- **README'den doğrulanan denetim yöntemi (`panel_gate`):**
  - Üç denetçi var: anlatı denetçisi + iki görsel denetçi (Gemini ve Codex).
  - Görsel denetçiler **beklenen değeri görmeden** görüntüyü yazıya döker (kör transkripsiyon).
  - Ardından **deterministik bir karşılaştırma** beklenen ile gözleneni karşılaştırır ve KEEP ya da
    RETRY kararını bu karşılaştırma verir.
  - "Hiçbir model kendi çıktısını onaylamaz." Panel başına en fazla 4 deneme var.
  - **Kredi harcamayan ön kapı** (`p0_proof`) üretimden önce çalışır.
  - Her deneme, denetim ve karar bir "research-wiki" grafiğine düğüm olarak yazılır ve şema
    (`jsonschema`) ile doğrulanır.
- **Bizim için:** **Fikir (en değerlilerinden).** Görsel süreklilik denetimimiz şu an "denetçi
  listeye bakıp karar veriyor". Daha güvenilir sürümü şöyle: denetçi **listeyi görmeden** kareyi
  yapılandırılmış biçimde tarif eder (kadrajdaki kişiler, eldivenin hangi elde olduğu, bakış yönü,
  ateş/ışık var mı). Python bu tarifi süreklilik listesiyle **deterministik olarak** karşılaştırır.
  Görseli Gemini ürettiyse Claude denetler, Claude ürettiyse Gemini.
- **Windows / Py3.10:** Python kısmı bağımsız ve basit. Gerisi Codex CLI istiyor, **uygun değil.**

### B5. story-shot-agent (PenShot)
- **Adres:** https://github.com/neopen/story-shot-agent
- **Yıldız / son push / lisans:** ~229 / 17.10.2026 / MIT
- **Ne yapıyor:** Senaryoyu Sora/Veo/Kling için plan parçalarına ve istemlere bölüyor (LangGraph +
  LlamaIndex). Ajan zinciri: senaryo ayrıştırma → plan → video bölütleme → istem dönüştürme →
  **kalite denetimi** → **süreklilik bekçisi** → yardımcı üretim → **çıktı düzeltici** (parça
  sırasını onarır).
- **Doğrulanan JSON şeması:** `fragments[]` → `fragment_id, prompt, negative_prompt,
  main_character, duration, model, style, requires_special_attention, audio{...}`. `audio` içinde
  `voice_character, emotion, stability, speed, duration_seconds, previous_audio_id, scene_context`
  gibi alanlar var.
- **Bizim için:** **Fikir.** (1) `requires_special_attention` bayrağı bizdeki "riskli plan"ın
  karşılığı ve `SAHNELER.json`'a `risk` alanı olarak eklenebilir. (2) Sesteki `previous_audio_id`
  ve `emotion` alanları ElevenLabs çağrılarında önceki repliğe bağlam vermek için kullanılabilir.
  Süreklilik doğrulayıcısı README'de hâlâ "yol haritası" maddesi.
- **Windows / Py3.10:** Python 3.10+ rozeti var. **Ücretli API:** Qwen/DeepSeek/OpenAI (Ollama
  seçeneği var).

### B6. forge-film
- **Adres:** https://github.com/F-R-L/forge-film
- **Yıldız / son push / lisans:** ~539 / 26.03.2026 / MIT
- **Ne yapıyor:** LLM hikâyeyi sahnelerin **bağımlılık grafiğine (DAG)** derliyor. Bağımsız
  sahneler paralel üretiliyor. Kritik Yol Yöntemi (CPM) en uzun zinciri önceliklendiriyor. B sahnesi
  A'ya bağlıysa A'nın **son karesi** B'nin I2V başlangıcı oluyor ve renk histogramla eşleniyor.
  `mock` sağlayıcıyla **anahtarsız 20 test** var. Python 3.11+.
- **Bizim için:** **Fikir.** "Son kare → sonraki planın başlangıç karesi" bağımlılığı ve histogram
  renk eşleme `renk_cila.py`'ye uygun. `mock` sağlayıcı fikri bizim `sahte` sağlayıcımızla aynı.
  **Uyarı:** Flow'da paralel gönderim "olağan dışı etkinlik" uyarısı getirir (03_DERSLER). DAG bizde
  yalnız **sıra ve öncelik** için kullanılır, hız için değil.

### B7. Büyük platformlar (kısaca, alınacak az şey var)
| Proje | Adres | Yıldız / son push / lisans | Not |
|---|---|---|---|
| Toonflow | https://github.com/HBAI-Ltd/Toonflow-app | ~18.980 / 20.10.2026 / MIT | TypeScript/Bun, Windows kurulumu var. Senaryo→storyboard→varlık→video. QA ajanı yok, CapCut dışa aktarma yok. |
| waoowaoo | https://github.com/waooAI/waoowaoo | ~14.660 / 21.09.2026 / Elastic 2.0 (README) | Next.js + Temporal + MySQL. "Kaynak açık" ama OSI lisansı değil. |
| dramaclaw | https://github.com/dramaclaw/dramaclaw | ~6.410 / 22.10.2026 / Elastic 2.0 (README) | **Her aşama bağımsız, atlanabilir ve kontrol noktasından devam edebilen asenkron iş.** Fountain senaryo girişi. Senaryo için "denetle-onar" döngüsü. Py3.11+, Windows'ta yalnız Docker/WSL2. |
| FireRed-OpenStoryline | https://github.com/FireRedTeam/FireRed-OpenStoryline | ~3.550 / 31.07.2026 / Apache-2.0 | Kurgu ajanı: klip anlama, müzik önerisi ve **vuruşa senkron kesme**, sohbetle düzeltme. Bir kurgu biçimini **"Style Skill" olarak kaydedip** tekrar kullanabiliyor. Windows elle kurulum, Py3.11. |
| OmniChar | https://github.com/omnichar/OmniChar | ~565 / 16.10.2026 / GPL-3.0 | `.char`: yüz fotoğrafları, kimlik parmak izi, **kilitli tarif**, ses örneği tek dosyada. Nano Banana Pro'ya veriliyor. Biçim ayrıntısı README'de yok. |

---

## C. Hikâye kalitesi değerlendirme (LLM-as-judge) kaynakları

| Kaynak | Adres | Durum | Alınacak |
|---|---|---|---|
| HANNA | https://github.com/dig-team/hanna-benchmark-asg | ~39 yıldız, MIT | Hikâye için **6 insan ölçütü**: Relevance (konuya bağlılık), Coherence (tutarlılık), Empathy (empati), Surprise (şaşırtma), Engagement (sürükleyicilik), Complexity (karmaşıklık). LLM ve insan puanları CSV olarak var. |
| LongStoryEval (ACL 2025) | https://github.com/DingyiYang/LongStoryEval | ~10 yıldız, lisans belirtilmemiş | Kitap uzunluğunda hikâyede üç yargı yöntemi karşılaştırılıyor: toplama, artımlı güncelleme, **özet tabanlı** (bölüm özetleri üzerinden). 8 üst ölçüt (listesi README'de yok). |
| Agents' Room (DeepMind, ICLR 2025) | https://github.com/google-deepmind/tell_me_a_story | ~52 yıldız (lisans okunamadı) | Anlatı kuramına göre ayrılmış uzman ajanlar ve **merkezî orkestratör + ortak karalama defteri (scratchpad)** (makale; arama özeti). Uzun hikâye değerlendirme çerçevesi. |
| Dramatron (DeepMind) | https://github.com/google-deepmind/dramatron | ~1.135 / 16.07.2024 / Apache-2.0 | **Logline'dan hiyerarşik üretim**: karakterler → olay noktaları → mekân tarifleri → diyalog. Colab defteri, LLM'i kendin bağlıyorsun. |
| WritingBench | https://github.com/X-PLUG/WritingBench | ~203 yıldız | Genel yazım kıyaslaması. Bizim için ikincil. |
| DOC | https://github.com/yangkevin2/doc-story-generation | ~161 yıldız | Ayrıntılı taslakla (outline) uzun hikâye kontrolü. Eski (2022–23). |

**Bizim habersiz seyircimizle karşılaştırma:** Bizim 03_DERSLER'deki bulgumuz ("puanlar gürültülü,
eğilim önemli") bu alandaki çalışmalarla uyumlu. Ekleyeceğimiz iki şey: (1) **sabit, adlandırılmış
ölçütler** (HANNA'nın 6 ölçütü, bizim "anlaşılırlık / merak / duygu" üçlümüzün genişletilmiş hâli),
(2) 30–45 dk'lık film için tüm metni değil **parti özetlerini** okutan özet tabanlı bir
değerlendirme. LongStoryEval, uzun metinde yargıcın dikkatinin dağıldığını gösteren işlerden biri.

---

## D. Doğrudan kullanılabilecek araç ve kütüphaneler (kod)

| Araç | Adres | Yıldız / son push / lisans | Nerede kullanırız | Win / Py3.10 |
|---|---|---|---|---|
| **PySceneDetect** | https://github.com/Breakthrough/PySceneDetect | ~5.280 / 22.10.2026 / BSD-3 | `kalite_denetim.py`: Flow klibinin içinde **istenmeyen kesme ya da sahne geçişi** var mı (Veo bazen klip içinde kesme yapar). Plan sınırı doğrulaması. | Evet (pip, OpenCV) |
| **OpenTimelineIO** | https://github.com/AcademySoftwareFoundation/OpenTimelineIO | ~2.030 / 22.10.2026 / Apache-2.0 | CapCut taslağına ek olarak **yedek dışa aktarma** (.otio → DaVinci Resolve / Premiere). Tek sağlayıcıya (CapCut) bağımlılığı azaltır. | Evet (pip) |
| pyJianYingDraft | (ArcReel'in bağımlılığı, `pyjianyingdraft>=0.3.0`) | — | Biz zaten `pycapcut` kullanıyoruz. İkisinin ilişkisi bu araştırmada **doğrulanamadı**. | — |
| VBench | https://github.com/Vchitect/VBench | ~1.830 / 21.08.2026 / Apache-2.0 | Video kalite ölçütleri (öznenin tutarlılığı, hareket düzgünlüğü vb.). GPU ve ağır modeller gerekiyor. **Şimdilik önerilmez.** Belki ileride tek ölçüt (subject consistency) alınır. | Zor |
| OpenClap | https://github.com/jbilcke-hf/OpenClap-Format | ~119 / 02.06.2024 / lisans yok | YZ yapımı için dosya biçimi (sıkıştırılmış YAML akışı). Taslak aşamasında ve terk edilmiş görünüyor. **Kullanmayın**, `SAHNELER.json` yeterli. | — |

---

## E. OpenMontage ile karşılaştırma

| Ölçüt | OpenMontage (denendi) | ViMax | ArcReel | drama-skills | **Bizim hat** |
|---|---|---|---|---|---|
| Flow aboneliğini kullanır mı | Hayır | Hayır (Veo API) | Hayır | Hayır | **Evet (Memmet)** |
| CapCut/Jianying taslağı | Hayır | Hayır | Jianying (pyJianYingDraft) | Hayır (ffmpeg) | **Evet (pycapcut)** |
| Anahtar kare adayı + VLM seçimi | Hayır | **Evet (2 aday)** | ? | Hayır | Hayır → **eklenmeli** |
| Belgeler arası deterministik kontrol | Kısmen | ? | jsonschema | **Evet** | Kısmen → **genişletilmeli** |
| Ücretli işten önce maliyet önizleme | Hayır | Hayır | **Evet** | **Evet** | Kısmen (onay noktaları) |
| Kör / çapraz model görsel denetimi | Hayır | Hayır | Hayır | Hayır | Tek denetçi → **ARIS gibi yapılmalı** |
| Habersiz seyirci / kurgu izleme | Hayır | Hayır | Hayır | review skill | **Evet (bizde var)** |
| Dudak denetimi, LUFS | visual_qa | Hayır | Hayır | Ses yüksekliği | **Evet** |
| Python 3.10 / Windows yerel | Ayrı venv | 3.12 | Docker, 3.12 | 3.9+ | **Evet** |

---

## Bizim hatta uygulanacak en değerli 5 fikir

### 1. Plan başına "başlangıç / bitiş durumu" + süreklilik çapaları + deterministik çapraz kontrol
*(Kaynak: drama-skills `creator_markdown_check.py` ve başlangıç/bitiş kuralı, DirectorSKILL
"bir kez yaz, kelimesi kelimesine tekrarla", VideoDirectorGPT tutarlılık grupları)*
- **Aşama:** Yönetmen (3. adım) çıktısı ve `film.py`'deki kâğıt üstü kalite kapısı. Kredi harcamaz.
- **Nasıl:**
  - `SAHNELER.json`'daki her plana isteğe bağlı alanlar eklenir (mevcut şema bozulmaz):
    `baslangic_durumu`, `bitis_durumu`, `kadrajda: [..]`, `kadraj_disi: [..]`,
    `nesneler: {eldiven: "mara_sol_el"}`, `isik_yonu`, `ekran_yonu`, `sure`, `risk`.
  - Karakter kimlik dizesi `karakterler.<ad>.kimlik` alanında **bir kez** yazılır. `gorsel_istem`
    bu alanlardan kodla birleştirilir.
  - Yeni `sureklilik_kontrol.py` (ya da `kontrol.py`'ye bir alt komut) şunları raporlar:
    - istemde adı geçen karakter `kadrajda`'da yok veya `referans`'ta yok;
    - planın `bitis_durumu` sonraki planın `baslangic_durumu` ile çelişiyor (nesne el
      değiştirmiş, karakter kaybolmuş);
    - bir nesne kurulmadan kullanılmış (03_DERSLER: "öteki yumurta");
    - `hareket_istem` başlangıç/bitiş dışında bir eylem anlatıyor veya süre 8–10 sn'yi aşıyor.
  - Çıktı: `RAPOR_SUREKLILIK.md` + `YENIDEN_YAZ.json` kuyruğu.

### 2. Görselde "2 aday üret, kör denetle, kod karar versin"
*(Kaynak: ViMax 2 aday + VLM seçimi, ARIS-Movie-Director kör transkripsiyon + deterministik fark +
"model kendi işini onaylamaz", AniMaker Reviewer)*
- **Aşama:** 4. adım (Gemini ajanı görsel paketi) ve 5. adım (görsel süreklilik denetimi).
- **Nasıl:**
  - `gemini_paket.py` paketlerinde `risk` işaretli planlar için **2 aday** istenir (Gemini ajanında
    Flow kredisi yok).
  - Denetçi (Claude görüntü modeli, `claude-opus-5-5`) her adayı **süreklilik listesini görmeden**
    sabit bir JSON biçiminde tarif eder: `{kisiler:[..], kisi_sayisi, eldiven_eli, bakis_yonu,
    ates_var, isik_yonu, fazladan_nesne:[..]}`.
  - Python bu tarifi 1. maddedeki alanlarla karşılaştırır ve sonuca göre seçer: ADAY_A / ADAY_B /
    YENİDEN ÜRET ("CORRECTION:" cümlesiyle).
  - Gemini'nin ürettiğini Gemini onaylamaz. En fazla 2 tur (bizdeki mevcut kural).
  - Bu, B3'te 44 karede 21 bozuk kareyi yakalayan denetimi **tekrar edilebilir ve ölçülebilir**
    hâle getirir.

### 3. Hikâye odasında rol ajanları: oyuncu denetimi + tartış/hakem + sabit ölçütlü seyirci jürisi
*(Kaynak: FilmAgent Critique-Correct-Verify ve Debate-Judge, HANNA 6 ölçütü, LongStoryEval özet
tabanlı yargı, Agents' Room orkestratör + scratchpad)*
- **Aşama:** 1–2. adım (hikâye odası, habersiz seyirci), CLAUDE.md'deki 2. görev.
- **Nasıl:**
  - **Oyuncu ajanları:** v1 senaryodan sonra her konuşan karakter için bir ajan yalnız kendi
    repliklerini kendi kartına (kişilik, konuşma tarzı, bildiği/bilmediği) göre denetler ve
    düzeltme önerir. Yönetmen ajanı önerileri birleştirir ve doğrular (CCV).
  - **A/B önerisi:** kullanıcı onaylı modda değilse iki savunucu ajan A ve B'yi savunur, bir hakem
    ajan gerekçeli karar verir.
  - **Habersiz seyirci jürisi:** 3 bağımsız seyirci, her biri 1–10 arası puan verir. Ölçütler:
    anlaşılırlık, tutarlılık, merak/sürükleyicilik, duygu/empati, şaşırtma, ilk 30 sn. Karar
    **medyan** ile verilir (03_DERSLER: puanlar gürültülü). Eşik 8/10 ve en fazla N tur.
  - 30–45 dk'lık film için seyirciye bütün metin değil, **parti özetleri + o partinin tam metni**
    verilir (özet tabanlı yargı).
  - Ortak `ODA_DEFTERI.md` (scratchpad) her ajanın kararını yazar. `film.py` durum dosyası buna
    bağlanır.

### 4. Kredi harcamadan önce "üretim önizlemesi" ve onaylı iş kuyruğu
*(Kaynak: drama-skills produce önizlemesi, ArcReel maliyet takibi, dramaclaw kontrol noktalı
asenkron işler, ARIS `p0_proof` kredi harcamayan ön kapı)*
- **Aşama:** `film.py` orkestratöründe 6. adımdan (Flow video) ve ücretli seslendirmeden hemen önce.
- **Nasıl:**
  - Her kredi harcayan aşamadan önce `URETIM_ONIZLEME.md` / `.json` üretilir: plan sayısı, model
    (Omni Flash, 12 kredi/plan), toplam kredi, ElevenLabs karakter sayısı, önbellekte olan ve
    olmayan replikler, referans dosyaları ve **1. maddenin kapısı geçildi mi**.
  - `--onayli` modda kullanıcı `.bat` ile onaylar. `--tam-otomatik` modda önizleme yine yazılır ve
    bütçe sınırı (`AYARLAR/butce.json`) aşılırsa durur.
  - İş kuyruğu kontrol noktalı olur: biten plan bir daha gönderilmez (`memmet_topla.py` ile
    uyumlu). Flow uyarısında kuyruk durur, atlatma yapılmaz.

### 5. Kurgu denetiminde "komşu planlarla birlikte yargı" + otomatik kesme ve süreklilik ölçümü
*(Kaynak: AniMaker AniEval komşu klip değerlendirmesi, DreamFactory sahneler arası yüz/stil
tutarlılığı, forge-film son kare → başlangıç + histogram renk eşleme, PySceneDetect)*
- **Aşama:** 7. adım (kurgu izleme denetimi) ve 8. adım (`kalite_denetim.py`).
- **Nasıl:**
  - `izleme_paketi.py` her plan için **üçlü pencere** (önceki planın son karesi, bu planın 3
    karesi, sonraki planın ilk karesi) üretir. Kurgu denetçisi "bu geçiş kopuk mu?" sorusunu bu
    pencereye göre cevaplar. Sonuç plan başına `KOPUK / ORTA / TAMAM` olur.
  - `kalite_denetim.py`'ye PySceneDetect eklenir: Flow klibinin içinde beklenmeyen kesme varsa
    plan "yeniden çek / kırp" kuyruğuna girer.
  - Ardışık iki planın ortak karakterinde renk histogramı farkı ölçülür (ffmpeg/numpy). Eşik
    aşılırsa `renk_cila.py` o plana hedefli eşleme uygular. Yüz benzerliği ölçüsü sonraya kalır
    (ek model gerekir).
  - Sonuçlar, mevcut kural gibi yeniden üretim kuyruğuna (`YENIDEN_URET.json`) yazılır.

---

### Doğrulanamayanlar (özet)
- StoryAgent ve DreamFactory için resmî GitHub deposu bulunamadı.
- arXiv sayfaları bu oturumda açılamadı. FilmAgent, AniMaker, MAViS, StoryAgent, DreamFactory ve
  Agents' Room ayrıntıları arama özetlerine dayanıyor.
- MAViS (arXiv 2508.08487): "3E: Explore–Examine–Enhance" döngüsü ve "Script Writing Guidelines"
  (senaryoyu üretici modellerin yapabildiklerine uydurma) ilkesi var. Kodu bulunamadı, ayrıntılar
  okunamadı.
- FilmAgent → VideoClaw yeniden adlandırması yönlendirmeden çıkarıldı.
- pycapcut ile pyJianYingDraft'ın ilişkisi doğrulanmadı.
- Anim-Director/AniMaker'ın API gereksinimi ve tell_me_a_story'nin lisansı okunamadı.
- Hiçbir deponun kodu satır satır incelenmedi. README'ler okundu, ArcReel'in bağımlılık listesi de
  doğrudan pyproject.toml'dan okundu.
