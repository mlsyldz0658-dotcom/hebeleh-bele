# 03 — Ses / Dudak / Müzik ve Claude Code Beceri-Ajan Araştırması

Tarih: 23 Ekim 2026. Kaynaklar o gün açılıp okundu. GitHub sayfaları `raw.githubusercontent.com` üzerinden
(README/LICENSE dosyasının kendisi), Claude Code belgeleri `code.claude.com/docs/en/*.md` ve
`platform.claude.com` üzerinden okundu. Bu ortamdan `huggingface.co`, `elevenlabs.io`, `deepmind.google`,
`sync.so` sayfaları açılamadı. Bunlardan alınan bilgiler **[arama]** etiketiyle yazıldı: arama sonucunda
göründü ama sayfa açılıp doğrulanamadı. Kullanmadan önce bir kez bakılmalı.

Depoda bulunan ve öneriyi etkileyen bilgiler:
- Kullanıcının yerel ekran kartı **RTX 3050 Ti, 4 GB** (`FILMLE ILGILI CLAUDE/HAFIZA_YEDEGI/yz-dizi-demolari.md`).
  Bu kart çoğu dudak senkronu modelini yerelde çalıştırmaya yetmez.
- `YZ_FILM/ARACLAR/ai84.py` dosyasında **`voice_change()` (ElevenLabs Voice Changer) zaten yazılı**.
  KARARLAR.md'ye göre 13 Ekim'de servis bakımdaydı. Tahmini fiyatı saniyede ≈2.000 kredi. TTS ise karakter başına 1 kredi.
- Kalan kredi ≈649 bin (13 Ekim). Bu, Voice Changer ile yalnızca ≈325 sn (≈5,4 dk) konuşma eder.
  35 dakikalık bir filmde ≈10-15 dk diyalog olduğu düşünülürse **AI84 Voice Changer bütçeye sığmaz.**
- Şimdiki hat (`seslendir.py`): faster-whisper (small.en) → demucs htdemucs (iki kanal) → ElevenLabs v4 TTS → süreye sığdırma.

---

## A) Ses, dudak senkronu, müzik

### A1. Dudak senkronu (lip-sync) araçları

| Araç | Kalite / yöntem | Lisans (ticari YouTube?) | Donanım | Windows | Not | Kaynak |
|---|---|---|---|---|---|---|
| **LatentSync 1.5 / 1.6** (ByteDance) | Gizil difüzyon. Whisper ses gömmeleri kullanır. 1.6 sürümü 512×512'de eğitildi ve bulanıklığı azaltır. Yüz 256×256'ya hizalanıp işlenir. Video 25 fps'e, ses 16 kHz'e çevrilir. | Kod **Apache-2.0**. ⚠️ Yüz tespiti için `insightface` (`FaceAnalysis`, `landmark_2d_106`) kullanıyor. **InsightFace modelleri yalnızca ticari olmayan araştırma içindir.** Ticari kullanımda bu dedektörün değiştirilmesi gerekir. Ağırlık lisansı HF sayfasında, bu ortamdan açılamadı. | En az VRAM: **8 GB (1.5)**, **18 GB (1.6)** | Resmî kurulum betiği Linux için (`setup_env.sh`). Windows yolu README'de yok. | Kalite olarak en iyi açık seçenek. 4 GB kartta çalışmaz. Bulutta (fal) ucuz. | https://github.com/bytedance/LatentSync (README "Inference", `requirements.txt`, `latentsync/utils/face_detector.py`) · InsightFace lisansı: https://github.com/deepinsight/insightface#license |
| **MuseTalk 1.5** (Tencent Music) | Gizil uzayda tek adımlı inpainting. 256×256 yüz bölgesi. V100'de 30 fps+ (gerçek zamanlı). | Kod **MIT**. README: "model ... available for any purpose, even commercially". Diğer bileşenler (whisper, ft-mse-vae, dwpose, S3FD) kendi lisanslarına bağlı. | VRAM README'de yazmıyor. Python 3.10, CUDA 11.7/11.8, torch 2.0.1. | **Evet**, README'de Windows komutları var. | Ticari açıdan en temiz yerel seçenek. Kalitesi LatentSync'ten biraz düşük, ağız bölgesi 256 px. | https://github.com/TMElyralab/MuseTalk (README "Disclaimer/License", "Windows Environment") |
| **Wav2Lip** | Eski (2020). Düşük çözünürlüklü ağız. | ❌ README: "**any form of commercial use is strictly prohibited**" (LRS2 veri seti). Ticari sürümü sync.so. | Hafif | — | YouTube kanalı için kullanılamaz. | https://github.com/Rudrabha/Wav2Lip (README "Disclaimer", "License and Citation") |
| **video-retalking** (OpenTalker) | Wav2Lip türevi, yüz iyileştirmeli. | Kod Apache-2.0, ama alt modeller farklı lisanslı. README "intellectual property declaration"a uyulmasını şart koşuyor. | torch 1.9 / CUDA 11.1 (eski) | Zor | Bakımsız, eski bağımlılıklar. Önermiyorum. | https://github.com/OpenTalker/video-retalking |
| **InfiniteTalk** (MeiGen) | Wan tabanlı, sesle sürülen **video-to-video dublaj**. Baş, yüz ve beden hareketini de yeniden üretir. 480p/720p. | Model **Apache-2.0**. "We claim no rights over your generated contents". | Ağır (Wan 14B sınıfı). "very low VRAM" modu ve nicemli model var. Wan2GP entegrasyonu düşük VRAM'e yönelik. | Wan2GP üzerinden | 8 sn klipte sahneyi baştan üretir, Veo görüntüsünden sapabilir. Yalnız yakın plan konuşmalarda yedek olarak düşünülebilir. | https://github.com/MeiGen-AI/InfiniteTalk (README "License", "Run with very low VRAM") |
| **LivePortrait** | Portre canlandırma. Dudak senkronu aracı değil, ifade aktarımı yapar. | Kod MIT. InsightFace modelleri ticari değil. Ticari kullanımda dedektör değiştirilmeli (LICENSE notu). | — | — | Bizim işimize doğrudan uymuyor. | https://github.com/KwaiVGI/LivePortrait (LICENSE sonu) |
| **sync.so lipsync-2 / 2-pro** (ticari API, Wav2Lip ekibi) | Kapalı model, açık kaynaklılardan daha kaliteli olduğu söyleniyor. | Ticari kullanım ücretli plana bağlı. | Bulut | — | **[arama]** lipsync-2-pro ≈0,067-0,083 $/sn → 8 sn klip ≈0,55-0,67 $. Aylık 3 ücretsiz, 20 sn'lik deneme. | https://sync.so/pricing · https://sync.so/docs/models **[arama]** |
| **LatentSync on fal.ai** | Barındırılan LatentSync | fal kullanım koşulları | Bulut | — | **[arama]** 40 sn'ye kadar sabit 0,20 $. 8 sn klip ≈0,20 $. 50 klip ≈10 $. | https://fal.ai/models/fal-ai/latentsync **[arama]** |

**8 sn klip için süre:** Repolar saniye başına süre vermiyor. MuseTalk V100'de "30 fps+" diyor. 8 sn × 25 fps = 200 kare, yani GPU'da birkaç saniye ile birkaç dakika arası sürer. LatentSync difüzyon olduğu için `inference_steps` 20-50 arasında. Daha yavaştır, adım sayısı arttıkça süre uzar (README). 4 GB kartta ikisi de pratik değil. Seçenekler bulut (fal/Replicate/RunPod) veya Colab.

**Dudak denetimi aracı:** SyncNet "sync confidence" ve ses-görüntü kayması (offset) ölçer, CPU ortamı da var
(https://github.com/joonson/syncnet_python, README "CPU only"). Depoda LICENSE dosyası bulunamadı, bu yüzden lisansı belirsiz.
Ancak yalnızca ölçüm için kullanılacak, çıktıya girmiyor. LatentSync de veri filtrelemede "sync confidence < 3" eşiğini kullanıyor
ve `eval/eval_sync_conf.py` betiği veriyor (https://github.com/bytedance/LatentSync, README "Evaluation").
→ `dudak_denetim.py` için önerilen ölçüt: **SyncNet offset ≈ 0 kare ve confidence ≥ 3**. Bunun altındaki klip yeniden üretim kuyruğuna girer.

### A2. Üç yolun karşılaştırması

**(1) Veo'nun kendi sesini tutmak (ses tarifi istemde sabit)**
- Artı: Dudak **kusursuz**, çünkü ses ve görüntü aynı modelden geliyor. Ek maliyet ve işlem yok. Ses ile ortam aynı akustikte.
- Eksi: Veo her klipte sesi yeniden icat ediyor, aynı karakter klipten klibe farklı tınlıyor (kullanıcının yaşadığı sorun bu).
  Google'ın istem rehberi her karakterin "appearance, voice, action, dialogue" tarifinin ayrıntılı verilmesini öneriyor.
  Replicate rehberi karakter tarifinin her istemde **aynen** tekrar edilmesini öneriyor **[arama]**. Bunlar tutarlılığı artırır, garanti etmez.
  Replik metni de bazen değişiyor (kelime atlama veya ekleme).
- Kaynak: https://deepmind.google/models/veo/prompt-guide/ **[arama]** · https://replicate.com/blog/using-and-prompting-veo-3 **[arama]**

**(2) TTS + dudak senkronu (LatentSync/MuseTalk/sync.so)**
- Artı: Ses tamamen sabit (ElevenLabs v4 karakter sesi). Metin senaryoyla birebir aynı. TTS ucuz (1 kredi/karakter).
- Eksi: Görüntüye ikinci bir model dokunuyor. Ağız bölgesinde bulanıklık, diş veya renk kayması, yan profilde hata olabiliyor.
  Yerel GPU yetmediği için bulut gerekiyor (klip başı ≈0,20 $ fal-LatentSync, ≈0,6 $ sync.so-pro **[arama]**).
  Ticari açık seçenekte lisans dikkat istiyor: MuseTalk temiz, LatentSync'in InsightFace bağımlılığı sorunlu, Wav2Lip yasak.
  TTS ile Veo'nun mimik ve duygusu uyuşmayabilir (Veo bağırırken TTS sakin kalabilir).

**(3) Veo sesine ses dönüştürme (speech-to-speech / voice conversion)**
- Fikir: demucs ile Veo'nun konuşmasını ayır → karakterin sabit sesine **dönüştür** → ortamla yeniden karıştır.
  Zamanlama, vurgu ve duygu Veo'dan geldiği için **dudak bozulmaz**. Görüntüye hiç dokunulmaz.
- ElevenLabs Voice Changer: SDK belgesi "Transform audio from one voice to another. Maintain full control over emotion,
  timing and delivery" diyor. Model `eleven_multilingual_sts_v2`, `remove_background_noise` ve `seed` parametreleri var
  (https://github.com/elevenlabs/elevenlabs-python/blob/main/reference.md, `speech_to_speech.convert`).
  `ai84.py` içindeki `voice_change()` aynı işi yapıyor ama **AI84 tahmini fiyatı ≈2.000 kredi/sn**, yani bütçeye uymaz.
  Doğrudan ElevenLabs aboneliğinde fiyat farklı olabilir, kontrol edilmeli.
- Açık kaynak dönüştürücüler:
  - **OpenVoice V2**: MIT, "Free for commercial use" (https://github.com/myshell-ai/OpenVoice, README "License").
    Ton rengi dönüştürücü (tone color converter) hafif. Sıfır atış, kısa referans sesle çalışıyor.
  - **Seed-VC**: Sıfır atış ses dönüştürme, eğitim gerektirmiyor. Python 3.10, Windows destekli. Kod **GPL-3.0** (https://github.com/Plachtaa/seed-vc, README ve LICENSE).
    GPL kodu dağıtırsak bizi bağlar. Yalnız çalıştırıp çıktı (ses) kullanmak dağıtım sayılmaz, ama ağırlık lisansı README'de belirtilmemiş.
  - **RVC WebUI**: MIT (https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI). Karakter başına model **eğitimi** gerekiyor
    (≈10 dk temiz ses). Ses örneği olarak karakterin ElevenLabs TTS çıktıları kullanılabilir. Eğitildikten sonra çıktı en tutarlısı olur.
  - **Chatterbox** (Resemble AI): MIT, `example_vc.py` ile ses dönüştürme var. Her çıktıya **görünmez Perth filigranı** gömüyor (https://github.com/resemble-ai/chatterbox, README).
- Artı: Dudak, duygu ve zamanlama korunur. Sabit ses elde edilir. Yerelde (CPU veya 4 GB) çalışabilir, kredi harcamaz.
- Eksi: Veo replik metnini değiştirmişse değişiklik kalır (whisper ile metin karşılaştırması şart). demucs artığı ve
  dönüştürücü artefaktları (metalik ses) çıkabilir. Fısıltı ve bağırmada sıfır atış modeller zorlanır.

**Değerlendirme:** Dudak sorununu kökten çözen yol (3). (2) yalnızca Veo'nun repliği bozduğu veya hiç konuşturmadığı
klipler için yedek olmalı. (1) ise (3)'ün ön koşulu: Veo'ya karakterin cinsiyet, yaş ve perde tarifi sabit verilirse dönüştürücü daha az zorlanır.

### A3. Diyalog seviyesi, ambiyans, ayrıştırma

- **pyloudnorm** (MIT): ITU-R BS.1770-4 ölçer, `Meter(rate).integrated_loudness()`, `normalize.loudness()` ve `normalize.peak()`
  (https://github.com/csteinmetz1/pyloudnorm). Kısa cümlelerde (0,4 sn'den kısa) entegre ölçüm yapılamaz.
  Bu yüzden cümleleri sahne bazında birleştirip ölçmek ya da kısa olanları komşusunun kazancıyla eşitlemek gerekir.
- **ffmpeg** `loudnorm` (EBU R128, tek veya çift geçiş, IL/LRA/TP hedefi), `ebur128` (ölçüm), `sidechaincompress` (diyalog gelince müzik ve ortamı kısma, ducking),
  `acrossfade`/`afade`/`aloop` (ambiyans döngüsü) (https://github.com/FFmpeg/FFmpeg/blob/master/doc/filters.texi).
- Hedefler (03_DERSLER.md): YouTube son miks **-14 LUFS**, Shorts da -14. Repliklerin 9 dB oynaması sorunu
  **replik başına** eşitleme ile çözülür. Önerim: replikler kendi aralarında ±1 LU'ya, son miks -14 LUFS ve gerçek tepe ≤ -1 dBTP olsun
  (bu bir mühendislik tercihi, kaynaktan alınmış bir standart değil).
- **Ambiyans sürekliliği:** demucs'un "ortam" kanalı klipten klibe değişiyor (dersler: kapı sahnesi). Çözüm: sahne başına
  **tek sürekli zemin** (CC0 kütüphane veya ElevenLabs `text_to_sound_effects.convert(..., loop=True)`; `loop` yalnız
  `eleven_text_to_sound_v2` modelinde var, https://github.com/elevenlabs/elevenlabs-python/blob/main/reference.md). Plan geçişlerinde 0,3-0,5 sn `acrossfade` yapılmalı.
  Klibin kendi ortamı yalnız ani olaylar (adım, kapı) için düşük seviyede bırakılmalı.
- **Ayrıştırma:** demucs README: "**this repository is not maintained anymore**", fork: https://github.com/adefossez/demucs
  (https://github.com/facebookresearch/demucs). `htdemucs_ft` daha iyi ama 4 kat yavaş. Hybrid Transformer modelinde segment en fazla 7,8 sn.
  Alternatif: **python-audio-separator** (MIT, BS-RoFormer / MelBand-RoFormer, CPU'da çalışıyor; https://github.com/nomadkaraoke/python-audio-separator).
  ElevenLabs `audio_isolation.convert` (Voice Isolator) de bir seçenek, ama ücretli.

### A4. Altyazı ve kelime zamanlama

- **WhisperX** (BSD-2): faster-whisper arka ucu, **wav2vec2 forced alignment ile kelime düzeyi zaman**, pyannote ile konuşmacı ayırma.
  large-v2 için 8 GB'tan az GPU, CPU da destekleniyor, Windows için CUDA 12.8 talimatı var (https://github.com/m-bain/whisperX).
- **stable-ts** (MIT): **`model.align(audio, metin)`** ile **bilinen metni** sese hizalıyor. CLI karşılığı `stable-ts audio.mp3 --align text.txt`.
  VAD ve sessizlik bastırma da var (https://github.com/jianfch/stable-ts, "Alignment"). Senaryodaki replik metni elimizde olduğu için
  altyazıda tanıma değil **hizalama** kullanmak doğru: yazım hatası olmaz, karakter adları doğru çıkar.
- **faster-whisper** (MIT): `word_timestamps=True` (https://github.com/SYSTRAN/faster-whisper). Hatta zaten var.
- ElevenLabs `forced_alignment.create` (ücretli API) da var (elevenlabs-python reference.md).
- whisper-timestamped **AGPL-3.0** (https://github.com/linto-ai/whisper-timestamped). Kullanılmasın.

### A5. Açık kaynak müzik üretimi

| Model | Lisans | Ticari YouTube | Donanım | Kaynak |
|---|---|---|---|---|
| **ACE-Step 1.5** | **MIT** | Evet (lisans açısından) | 2B turbo ≤6 GB'ta (INT8 + CPU offload, LM kapalı). XL için ≥12 GB. 10 sn - 10 dk süre, BPM ve ton kontrolü. **Windows taşınabilir paketi ve `.bat` dosyaları var.** | https://github.com/ace-step/ACE-Step-1.5 |
| ACE-Step (v1) | Apache-2.0 | Evet | `--cpu_offload` | https://github.com/ace-step/ACE-Step |
| **YuE2** | Kod Apache-2.0. Ağırlıklar **CC BY-NC 4.0 + ek içerik üretici izni**. README: "Personal users, content creators... free to ... **monetize generated outputs**". Şirketler için lisans gerekli. | Bireysel üretici olarak evet (MODEL_LICENSE okunmalı) | Ağır | https://github.com/multimodal-art-projection/YuE |
| **MusicGen** (audiocraft) | Kod MIT, **ağırlıklar CC-BY-NC 4.0** | ❌ | — | https://github.com/facebookresearch/audiocraft (README "License") |
| Stable Audio Open (stable-audio-tools) | Kod MIT. Ağırlık lisansı HF'de, açılamadı. | Belirsiz | — | https://github.com/Stability-AI/stable-audio-tools |
| ElevenLabs Music | Ticari API. `music.compose` ve **`music.video_to_music`** var. AI84 aracılığıyla sunulup sunulmadığı bilinmiyor. | Plan koşuluna bağlı | Bulut | https://github.com/elevenlabs/elevenlabs-python/blob/main/reference.md |

Not: digitalsamba/claude-code-video-toolkit de müzik için ACE-Step kullanıyor (`tools/music_gen.py --preset ... --duration`),
https://github.com/digitalsamba/claude-code-video-toolkit.

### A6. TTS (yedek ve yerel seçenek)
- F5-TTS: kod MIT, **önceden eğitilmiş modeller CC-BY-NC** (Emilia veri seti), ticari değil (https://github.com/SWivid/F5-TTS, "License").
- CosyVoice: Apache-2.0 (https://github.com/FunAudioLLM/CosyVoice).
- Chatterbox: MIT, filigranlı (yukarıda).

---

## B) Claude Code beceri (skill) ve ajan (subagent) örnekleri

### B1. Resmî belgeler (okundu)
- Skills (Claude Code): https://code.claude.com/docs/en/skills.md
- Subagents: https://code.claude.com/docs/en/sub-agents.md
- Hooks: https://code.claude.com/docs/en/hooks.md
- Skill yazım en iyi uygulamaları: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Agent Skills genel bakış: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview.md
- Anthropic örnek repo: https://github.com/anthropics/skills (`skills/skill-creator`, `slack-gif-creator`, `algorithmic-art`, `webapp-testing`, `pptx`, `template/`)
- Anthropic resmî eklenti örneği (aşamalı komut ve ajanlar): https://github.com/anthropics/claude-code/tree/main/plugins/feature-dev

### B2. SKILL.md frontmatter alanları (skills.md "Frontmatter reference")
- `name`: en fazla 64 karakter; küçük harf, rakam ve tire. "anthropic" ve "claude" kelimeleri yasak (best-practices).
- `description`: **önerilir**. Claude bu metne bakarak beceriyi seçer. Agent Skills spesifikasyonunda en fazla 1.024 karakter.
  Claude Code listesinde `description + when_to_use` birlikte **1.536 karakterde kesilir**, bu yüzden "ana kullanım ilk cümlede" olmalı.
- `when_to_use`: tetikleyici ifadeler ve örnek istekler.
- `argument-hint`, `arguments`: `$ARGUMENTS`, `$0`, `$isim` yer tutucuları.
- `disable-model-invocation: true`: yalnız `/isim` ile çalışır (kredi harcayan aşamalar için doğru seçim).
- `user-invocable: false`: yalnız Claude kullanır (arka plan bilgisi).
- `allowed-tools`: o turda izin sormadan kullanılacak araçlar (ör. `Bash(python YZ_FILM/ARACLAR/film.py *)`). Bir sonraki mesajda izin düşer.
- `disallowed-tools`, `model`, `effort`, `context: fork` + `agent` (alt ajanda çalıştır), `background`, `hooks`, `paths` (dosya globuna göre etkinleşme), `shell` (`powershell` Windows için).
- Yer tutucular: `${CLAUDE_SKILL_DIR}` (beceri klasörü, betik çağırmak için), `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_SESSION_ID}`.
- Dinamik bağlam: `` !`komut` `` beceri yüklenmeden önce çalışır ve çıktısı metne gömülür. Örneğin `` !`python YZ_FILM/ARACLAR/film.py FILM --durum` `` ile durum doğrudan beceriye girer.

### B3. description nasıl yazılır (doğru anda tetiklensin)
- **Üçüncü şahıs** ("Processes Excel files…"; "I can…" ya da "You can…" değil) (best-practices "Writing effective descriptions").
- **Ne yaptığı + ne zaman kullanılacağı** ve kullanıcının doğal olarak söyleyeceği anahtar kelimeler
  (skills.md "Skill not triggering": "description includes keywords users would naturally say").
- Anthropic `skill-creator`: Claude becerileri **az tetikleme eğiliminde**, bu yüzden açıklama biraz "ısrarcı" yazılmalı
  ("Make sure to use this skill whenever the user mentions…"). Basit tek adımlı istekler beceri tetiklemez, karmaşık ve çok adımlı olanlar tetikler
  (https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md).
- obra/superpowers `writing-skills`: açıklama yalnız **"Use when…" ile başlayan tetikleme koşulunu** söylemeli.
  **İş akışını özetlememeli**, çünkü ajan özeti okuyup beceriyi açmadan onu uygular
  (https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md).
- Türkçe kullanıcı için açıklamaya **hem Türkçe hem İngilizce** tetikleyiciler yazılmalı ("film yap, senaryo, sahne, kurgu, seslendir, film, scene…").
- Çok sık tetikleniyorsa açıklama daraltılır ya da `disable-model-invocation: true` yapılır (skills.md "Skill triggers too often").

### B4. Gövde, ek dosyalar, betikler
- SKILL.md **500 satırın altında** kalmalı. Ayrıntılar `reference.md` ve `examples.md` gibi dosyalara gider. Bu dosyalara SKILL.md'den **tek seviye** bağlantı verilir,
  ne zaman okunacakları yazılır. 100 satırı aşan referans dosyasının başına içindekiler konur (best-practices "Progressive disclosure", "Avoid deeply nested references").
- `scripts/` içindeki betikler **çalıştırılır, okunmaz**. `webapp-testing` örneği: "Always run scripts with `--help` first… use as black-box scripts" (https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md).
- Deterministik işler betiğe yazılır, Claude'a doğrulama kodu ürettirilmez (best-practices "Prefer scripts for deterministic operations", "Solve, don't defer").
- **Plan → doğrula → uygula** kalıbı: önce ara bir plan dosyası (JSON), sonra doğrulama betiği, sonra uygulama (best-practices "Create verifiable intermediate outputs").
  Bizde: `SAHNELER.json` → `istem_denetim.py` → kredi harcayan üretim.
- Uzun iş akışlarında Claude'un kopyalayıp işaretleyeceği bir **kontrol listesi** ve geri besleme döngüsü ("doğrula → düzelt → tekrar") verilir (best-practices "Workflows and feedback loops").
- Yollarda her zaman `/` kullanılır, Windows'ta da (best-practices "Avoid Windows-style paths").
- Tarihe bağlı bilgi yazılmaz. Eski yöntemler "Eski kalıplar" bölümünde tutulur.
- Gerekli paketler listelenir. "Kurulu varsayma" (best-practices "Avoid assuming tools are installed").
- Beceri içeriği çağrıldığında bağlama bir kez girer. Sıkıştırmadan (compaction) sonra **yalnız ilk 5.000 token** yeniden eklenir.
  → **En önemli kurallar SKILL.md'nin en üstüne** yazılmalı. Her seferinde uyulması gereken kurallar ise **hook**'a taşınmalı (skills.md "Skill content lifecycle", "Claude stops following a skill").
- Değerlendirme: en az 3 senaryo, Haiku, Sonnet ve Opus ile denenmeli (best-practices checklist). `skill-creator` içinde açıklama optimizasyon döngüsü var (`run_loop.py`, %60/%40 eğitim/test ayrımı).

### B5. Ajan (subagent) tanımı en iyi uygulamaları (sub-agents.md)
- Zorunlu alanlar `name` ve `description`. `description` "Claude ne zaman bu ajana devretmeli" sorusunu yanıtlar.
  Kendiliğinden devretmeyi artırmak için **"use proactively"** ifadesi eklenir. Tüm ajan açıklamalarının toplamı 15.000 token'ı geçerse uyarı verilir.
- `tools`: en az yetki. Okuma yapan denetçiler `Read, Grep, Glob` ile sınırlanır. Örnek `code-reviewer` ajanında Edit ve Write yok.
  `disallowedTools` ile çıkarma yapılır. Habersiz seyirci gibi "bilmemesi gereken" ajanlarda **araç ve dosya erişimi kısıtlanır**, okuyacağı dosya istemde açıkça verilir.
- `model`: `sonnet`/`opus`/`haiku`, tam kimlik (`claude-opus-5-5`) ya da `inherit`. Yaratıcı ve yargı gerektiren işlerde opus, mekanik işlerde haiku veya sonnet kullanılır.
- `effort`, `maxTurns` (sınıra gelince çıktı "partial" işaretlenir ve devam ettirilebilir), `skills` (beceriyi ajana önceden yükler), `memory: project` (`.claude/agent-memory/<ad>/`, ders birikimi),
  `isolation: worktree`, `hooks`, `permissionMode`, `color`, `background`.
- Alt ajan sohbet geçmişini **görmez**. Ona gereken her şey devretme mesajında veya ajan gövdesinde olmalı.
  superpowers: "They should never inherit your session's context… you construct exactly what they need" (https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md).
- Zincirleme: bir ajanın çıktısı ana oturum üzerinden sonrakine verilir. Ajan en fazla 3 katman iç içe ajan açabilir.
- Gövde kalıbı (resmî örnekler): rol cümlesi → "When invoked:" adımları → kontrol listesi → **çıktı biçimi** (öncelik sıralı: kritik/uyarı/öneri).
  Örnek: https://github.com/anthropics/claude-code/blob/main/plugins/feature-dev/agents/code-explorer.md (`tools`, `model: sonnet`, `color`).
- Beceri ile ajan ayrımı: sık soru-cevap gerektiren ve bağlamı ortak aşamalar **ana oturumda beceri** olur. Uzun çıktı üreten,
  araç kısıtlaması isteyen ve kendi içinde kapalı işler (seyirci puanı, süreklilik denetimi) **ajan** olur (sub-agents.md "Choose between subagents and main conversation").

### B6. Uzun işlerde durum dosyası ve kaldığı yerden devam
- **superpowers SDD defteri (ledger)**: "Conversation memory does not survive compaction… controllers that lost their place have
  re-dispatched entire completed task sequences — the single most expensive failure observed. Track progress in a ledger file".
  Defterin ilk satırı kimliğini yazar. Sıkıştırmadan sonra hafızaya değil **deftere ve `git log`'a** güvenilir. Kararlar
  `Ruling: <karar> — <neden> — <yanlışsa maliyeti>` biçiminde kaydedilir. Yalnızca 4 durumda durulur: geri alınamaz işlem, güvenlik, dış yan etki (yayın/push), çaresiz plan.
  (https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md)
- **OpenMontage checkpoint protokolü**: aşama manifestosu (YAML) ve aşama başına "director" becerisi (Markdown) vardır. Python yalnız araç ve kalıcılık sağlar.
  Akış `get_next_stage()` → aşama becerisi → öz-denetim (en fazla 2 tur) → `checkpoint_<aşama>.json` (şemayla doğrulanır, eskisi `history/` klasörüne arşivlenir)
  → `human_approval_default` doğruysa `awaiting_human` durumuna geçer. Karar günlüğü ve maliyet anlık görüntüsü de tutulur.
  (https://github.com/calesthio/OpenMontage/blob/main/AGENT_GUIDE.md, https://github.com/calesthio/OpenMontage/blob/main/skills/meta/checkpoint-protocol.md)
- **claude-code-video-toolkit**: `projects/*/project.json` dosyasında aşama (`planning → assets → review → audio → editing → rendering → complete`), sahne durumları
  ve oturum geçmişi tutulur. `/video` komutu projeleri tarar, **niyeti (plan) gerçek dosyalarla uzlaştırır**, sağlığı (ready/blocked/stale) hesaplar ve devam etmeyi önerir.
  Her projeye ayrı bir `CLAUDE.md` üretir. (https://github.com/digitalsamba/claude-code-video-toolkit, `.claude/commands/video.md`)
- **Hook ile hatırlatma**: `SessionStart` olayı `startup|resume|clear|compact` eşleyicileri alır. `additionalContext` (en fazla 10.000 karakter) ile
  sıkıştırmadan sonra `FILM_DURUM.json` özeti yeniden bağlama eklenebilir (hooks.md, eşleyici tablosu ve "additionalContext").
- Bizdeki `film.py` zaten `FILM_DURUM.json` ve `--durum` desteğine sahip. Becerinin ilk işi bu çıktıyı `` !`…` `` ile almak olmalı.

### B7. İncelenen diğer örnek koleksiyonlar
- Remotion resmî becerileri (video): https://github.com/remotion-dev/skills (`/remotion-create`, `/remotion-render`, `/remotion-captions`: görev başına küçük beceriler, bir de "hepsini kapsayan" best-practices becerisi).
- digitalsamba video toolkit becerileri (elevenlabs, ffmpeg, acestep, ltx2…): https://github.com/digitalsamba/claude-code-video-toolkit (örnek `ffmpeg` description: "Use for… Triggers include converting GIF to MP4…").
- Ajan koleksiyonları: https://github.com/VoltAgent/awesome-claude-code-subagents, https://github.com/wshobson/agents. Beceri listeleri: https://github.com/travisvn/awesome-claude-skills, https://github.com/ComposioHQ/awesome-claude-skills, https://github.com/hesreallyhim/awesome-claude-code.
  Bunlar çoğunlukla yazılım odaklı. Medya üretimi için en yararlı ikisi OpenMontage ve video-toolkit.

---

## Önerilerim

### Dudak / ses için önerilen yol
1. **Ana yol = (3) ses dönüştürme.** Veo konuşmayı kendisi üretsin. İstemde karakterin **ses tarifi** (cinsiyet, yaş, perde, aksan, tempo) her klipte aynen tekrarlansın.
   Sonra `demucs` ya da `audio-separator` (BS-RoFormer) ile konuşma ayrılsın, karakterin ElevenLabs referans sesiyle **yerel ses dönüştürücüden** geçirilsin
   (önce **OpenVoice V2**, MIT, hafif; tutarlılık yetmezse karakter başına **RVC** modeli, ElevenLabs TTS çıktılarıyla eğitilir). Ortamla yeniden karıştırılsın.
   Dudak, duygu ve zamanlama korunur. Kredi harcanmaz. → `seslendir.py` içine `--yontem donustur|tts` seçeneği.
2. **Metin kapısı:** whisper (veya stable-ts) ile Veo'nun söylediği metin senaryoyla karşılaştırılsın. Kelime hata oranı (WER) eşiği aşılırsa (ör. > %15) o klip:
   a) önce Flow'da yeniden çekim kuyruğuna, b) yeniden çekim de tutmazsa **TTS + bulut dudak senkronu** yedeğine düşsün
   (MuseTalk 1.5, lisansı temiz, Windows destekli. Bulutta LatentSync ≈0,20 $/klip **[arama]**. LatentSync yerelde kullanılacaksa InsightFace dedektörü değiştirilmeli). **Wav2Lip asla kullanılmasın.**
3. **ElevenLabs Voice Changer** yalnız ana sahnelerdeki kritik repliklerde ve kullanıcı onayıyla kullanılsın. AI84 fiyatıyla (≈2.000 kredi/sn) tüm film için kullanılamaz.
4. **`dudak_denetim.py`:** SyncNet offset ve confidence ölçsün (CPU). Eşik offset 0 ±1 kare, confidence ≥ 3. Altındakiler yeniden üretim kuyruğuna girsin.
5. **Seviye:** pyloudnorm ile replik başına eşitleme (±1 LU), ffmpeg `loudnorm` çift geçişle son miks **-14 LUFS / ≤ -1 dBTP**, müzik ve ambiyans için `sidechaincompress` ducking.
6. **Ambiyans:** sahne başına tek sürekli zemin (CC0 veya ElevenLabs SFX `loop=True`), plan geçişlerinde 0,3-0,5 sn çapraz geçiş. Klip ortamı yalnız ani olaylar için kalsın.
7. **Altyazı:** senaryo metni elimizde olduğu için **stable-ts `align()`** (MIT) ya da WhisperX hizalaması kullanılsın. Tanıma yapılmasın. whisper-timestamped (AGPL) kullanılmasın.
8. **Müzik:** **ACE-Step 1.5** (MIT, ≤6 GB modu, Windows paketi). 4 GB'ta yavaş olabilir, olmazsa Colab veya bulut. YuE2 bireysel üretici izniyle olabilir (MODEL_LICENSE okunmalı).
   MusicGen ve Stable Audio Open ticari açıdan uygun değil ya da belirsiz. Gemini ile elle üretim yedek olarak kalsın.
   `gemini_muzik.py` yerine bir `muzik` sağlayıcı arayüzü: `aceStep | elevenlabs | elle | sahte`.

### Skill / ajan yazım kuralları (bu depo için)
1. `name` küçük harf ve tireli olmalı (`film-yap`). "claude" ve "anthropic" kelimeleri yasak.
2. `description` üçüncü şahıs ve "Use when…/… istendiğinde kullanılır" biçiminde olmalı. **Ne zaman** kullanılacağını söylemeli, iş akışını özetlememeli.
   Türkçe ve İngilizce tetikleyiciler ilk cümlede olmalı ("film yap, yeni film, senaryo, sahneler, kurgu, seslendir, devam et"). `description + when_to_use` 1.536 karakteri geçmemeli, spesifikasyona göre description en fazla 1.024 karakter.
3. Kredi harcayan aşamalar (video, ses, müzik, yayın) **ayrı beceri** olmalı ve `disable-model-invocation: true` taşımalı. Yalnız kullanıcı `/film-yap uret` yazınca çalışmalı.
4. SKILL.md 500 satırın altında kalmalı. **En üstte**: Flow uyarısında dur, gizli bilgi yazma, kredi onayı. Ayrıntılar `reference/*.md` dosyalarında, tek seviye bağlantıyla.
5. Durum `` !`python YZ_FILM/ARACLAR/film.py <film> --durum` `` ile becerinin içine gömülsün. Claude hafızasına değil `FILM_DURUM.json`'a ve `git log`'a güvensin.
   Kararlar `KARAR_DEFTERI.md` dosyasına "karar — neden — yanlışsa maliyeti" biçiminde yazılsın.
6. Betikler `${CLAUDE_SKILL_DIR}` / `${CLAUDE_PROJECT_DIR}` ile çağrılsın, önce `--help` denensin, kaynakları okunmasın. Deterministik denetimler betikte olsun (istem_denetim, kalite_denetim, dudak_denetim).
7. `allowed-tools` yalnız dar komutlar için verilsin (ör. `Bash(python YZ_FILM/ARACLAR/film.py *)`). Geniş `Bash` izni verilmesin.
8. Her aşamada **plan → doğrula → uygula** ve en fazla 2 öz-denetim turu (OpenMontage) olsun. Sonra uyarıyla geçilsin ya da insan onayı (`awaiting_human`) beklensin.
9. Ajanlar: tek iş ve en az araç. Habersiz seyirci ve denetçilerde `tools: Read, Glob` (+ rapor için `Write`), okuyacağı dosya istemde açıkça verilmeli. Her çağrı **yeni örnek** olmalı (bağlam taşımaz).
   Yaratıcı ve yargı işlerinde `model: opus`, mekanik işlerde `haiku`/`sonnet`. Dersler biriken denetçilerde `memory: project` kullanılmalı.
10. Ajan gövdesi şu sırayla yazılmalı: rol → "Çağrıldığında" adımları → kontrol listesi → **makinece okunabilir çıktı** (JSON veya sabit başlıklı rapor, `KRİTİK/ORTA/KÜÇÜK`). Böylece `puan_oku.py` gibi betikler puanı ayrıştırabilir.
11. Her zaman uyulması gereken kurallar (ör. `AYARLAR/` dosyalarına yazmama, Flow uyarısında durma) beceri metninde değil **hook**'ta olmalı (PreToolUse). Sıkıştırmadan sonra durum özeti `SessionStart` + `compact` hook'uyla `additionalContext` olarak geri getirilmeli.
12. Her beceri için en az 3 değerlendirme senaryosu yazılmalı (ör. "yeni film başlat", "kaldığı yerden devam", "sadece sesi yeniden yap"). Tetiklenme `skill-creator` açıklama döngüsüyle ölçülmeli.
