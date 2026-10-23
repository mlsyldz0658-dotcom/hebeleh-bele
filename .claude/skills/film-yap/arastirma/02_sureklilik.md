# 02 — YZ videoda süreklilik ve karakter tutarlılığı (araştırma)

Tarih: 23 Ekim 2026. Hazırlayan: Claude (araştırma ajanı).
Kapsam: Flow/Veo'da 8–10 sn'lik "Kareler" (başlangıç karesi → video) klipleriyle 30–45 dk film üreten
hattımızda **karakter tutarsızlığı, nesne zıplaması, karakterin kaybolup belirmesi, ters el, bakış yönü,
ışık/ambiyans zıplaması** sorunlarını makineyle yakalamak (`FILMLE ILGILI CLAUDE/03_DERSLER.md`).

## 0. Nasıl doğrulandı (dürüstlük notu)

- **GitHub depoları**: hepsi GitHub arama API'siyle tek tek açıldı. Lisans, son push tarihi ve yıldız
  sayısı bu sorgudan geliyor (23.10.2026). README'ler `raw.githubusercontent.com` üzerinden indirilip okundu.
- **PyPI**: paket sürümü, `requires_python` ve Windows wheel varlığı PyPI JSON API'sinden alındı.
- **Veo API parametreleri**: Google'ın resmî `google-genai` Python SDK'sının `types.py` kaynağından okundu
  (ai.google.dev bu ortamdan açılamadı).
- **Flow "Extend / Jump to"**: support.google.com bu ortamdan açılamadı. Bilgi yalnız arama
  sonucu özetinden geliyor, o yüzden **"doğrulanmadı"** diye işaretlendi.
- **Eşik değerleri**: kaynağı olanlar (OpenCV SFace, ffmpeg varsayılanları, VBench yöntemi) belirtildi.
  Kalanlar **başlangıç tahmini** ve kendi verimizle ayarlanmalı (bkz. §7 Kalibrasyon).

**Ticari kullanım uyarısı:** Para kazanan bir YouTube kanalı ticari kullanım sayılır. Bu yüzden
"yalnız ticari olmayan araştırma" lisanslı modeller (InsightFace hazır modelleri, pyiqa, DOVER, CoTracker)
**ana hatta kullanılmamalı**. Yalnızca deneme ya da kalibrasyon için kullanılabilirler.

---

## 1. Karakter tutarlılığı ve otomatik kimlik denetimi

### 1.1 Yüz benzerliği (kare ↔ karakter kartı)

| Aday | Adres | Lisans | Son etkinlik | Ne yapar | Win / Py3.10 / CPU | Hatta nereye takılır | Ücretli API |
|---|---|---|---|---|---|---|---|
| **OpenCV YuNet + SFace** (`FaceDetectorYN`, `FaceRecognizerSF`) | github.com/opencv/opencv_zoo (models/face_recognition_sface) | Apache-2.0 (model klasörü: "All files in this directory are licensed under Apache 2.0") | opencv-python 5.0.0.93, 2.7.2026 | Yüz bulur, 5 nokta hizalar, 128-boyutlu özellik çıkarır, kosinüs/L2 eşleşme yapar | **Evet**: `opencv-python` abi3 win_amd64 wheel, CPU'da hızlı, ek bağımlılık yok | **Kapı G1 (görsel kimlik)** ve **Kapı V2 (video kimlik)**: her başlangıç karesindeki her yüz → kart yüzü | Hayır |
| **InsightFace** (ArcFace, buffalo_l, antelopev2) | github.com/deepinsight/insightface | Kod MIT. **Modeller: "for non-commercial research only"** (python-package README) | push 19.10.2026, 30k★, PyPI 2.1 (3.10.2026) | En güçlü açık yüz tanıma (ArcFace) | pip ile kurulur, onnxruntime ile CPU'da çalışır. Ancak onnxruntime'ın son cp310 Windows wheel'i **1.23.2**, sabitlenmeli | Yalnız kalibrasyon / karşılaştırma. **Ticari kanalda ana denetçi olamaz** | Hayır |
| **deepface** | github.com/serengil/deepface | MIT ("License types will be inherited" uyarısıyla: her modelin kendi lisansı geçerli) | push 22.10.2026, 23.6k★, PyPI 0.0.103 | VGG-Face, FaceNet, ArcFace, SFace, GhostFaceNet, Buffalo_L için tek `DeepFace.verify()` arayüzü. Çok sayıda dedektör seçeneği var | py≥3.8, CPU'da çalışır | Hızlı deneme ve model karşılaştırma. Ana hatta SFace'i doğrudan OpenCV'den kullanmak daha az bağımlılık getirir | Hayır |
| face_recognition (dlib) | github.com/ageitgey/face_recognition | MIT | PyPI son sürüm 2020 | dlib tabanlı yüz eşleme | Windows'ta dlib derlemesi zahmetli | **Önerilmez** | Hayır |
| facenet-pytorch | github.com/timesler/facenet-pytorch | MIT | push 16.9.2025, PyPI 2.6.0 (2024) | MTCNN + InceptionResnet (VGGFace2) | torch gerektirir | Yedek seçenek | Hayır |

**Doğrulanmış eşik (OpenCV resmî öğreticisi, `dnn_face.markdown`):** SFace için iki yüz,
kosinüs ≥ **0.363** ya da NormL2 ≤ **1.128** ise aynı kişi sayılır. Bu eşik gerçek fotoğraflar
için verilmiş. Sinematik YZ görsellerinde (yan profil, karanlık, sakal, kask) benzerlik düşebilir.
Bu yüzden §6'daki üç bantlı karar kullanılmalı.

**Sınır:** Ember (ejderha) gibi insan olmayan karakterlerde yüz modeli çalışmaz. Onlar için §1.2'deki
genel görüntü gömmesi (DINOv2) ve görüntü-dil modeli (VLM) denetimi gerekir.

### 1.2 Genel görüntü benzerliği (kostüm, nesne, mekân, insan olmayan karakter)

| Aday | Adres | Lisans | Son etkinlik | Ne yapar | Win / CPU | Hatta nereye takılır |
|---|---|---|---|---|---|---|
| **DINOv2** | github.com/facebookresearch/dinov2 (ayrıca `transformers` içinde `dinov2`) | Apache-2.0 | push 6.10.2026, 13.4k★ | Kendi kendine öğrenen görsel gömme. Nesne ve doku kimliğine duyarlı. VBench `subject_consistency` bunu kullanıyor | torch CPU ile çalışır (dinov2-small veya base) | Kostüm/ejderha/nesne kırpıntısı ↔ kart kırpıntısı; klip içi kare-kare morf/belirme tespiti; plan sonu ↔ sonraki plan başı mekân benzerliği |
| DINOv3 | github.com/facebookresearch/dinov3 | Özel "DINOv3 License" (Apache değil, şartlar okunmalı) | push 15.7.2026 | DINOv2'nin halefi | Ağır | Lisans netleşmeden önerilmez |
| **OpenAI CLIP** / **OpenCLIP** | github.com/openai/CLIP, github.com/mlfoundations/open_clip | MIT / MIT-benzeri (NOASSERTION, LICENSE metni MIT izinli) | push 25.3.2026 / 30.9.2026 | Görüntü-metin benzerliği | CPU'da çalışır, open-clip-torch 3.3.0 py≥3.9 | "Kare istemle uyumlu mu", "sahne gece mi" gibi metin sorguları; VBench `background_consistency` CLIP kullanıyor |

**VBench yöntemi (kaynak kodu okundu: `vbench/subject_consistency.py`, `temporal_flickering.py`):**
- Öznel tutarlılık: her kare DINO ile gömülür. Önceki kareyle ve ilk kareyle kosinüs benzerliği alınıp ortalanır.
- Titreme: ardışık kareler arası ortalama mutlak fark (MAE) alınır, skor `(255 − ort.MAE)/255` olarak hesaplanır.
- Bu iki yöntem **ağır VBench kurulumu olmadan** 30–40 satır Python ile yeniden yazılabilir. Önerilen yol bu.

### 1.3 Üretim tarafı (referansla tutarlılık) — ne öğrenilir, ne alınmaz

| Aday | Adres | Lisans | Son etkinlik | Not |
|---|---|---|---|---|
| IP-Adapter | github.com/tencent-ailab/IP-Adapter | Apache-2.0 | 2024-06 | Görüntü referansıyla SD üretimi. GPU ister, Flow/Gemini görsel hattımızın yerine geçmez |
| InstantID | github.com/instantX-research/InstantID | Apache-2.0 (yüz modeli InsightFace → ticari sorun) | 2024-07 | Kimlik koruyan görsel üretimi. GPU ister |
| StoryDiffusion | github.com/HVision-NKU/StoryDiffusion | Apache-2.0 | 2024-09 | Hikâye boyunca tutarlı karakter. GPU ister |
| ConsisID | github.com/PKU-YuanGroup/ConsisID | Apache-2.0 | 2026-04 | Kimlik koruyan metinden-videoya. GPU ister |
| HoloCine | github.com/yihao-meng/HoloCine | Other (NOASSERTION) | 2025-11 | Wan 2.2 tabanlı çok planlı tutarlı uzun video. Büyük GPU ister |

**Sonuç:** Bunlar yerel GPU ister ve Flow aboneliği yerine geçmez. Hatta **alınmaz**. Bizim için
tutarlılık iki yerden gelir: (a) iyi seçilmiş başlangıç karesi (referanslı Gemini/Flow görseli),
(b) **üretim sonrası denetim + yeniden üretim kuyruğu**.

### 1.4 Ajan tabanlı film hatları (yöntem ödünç almak için)

| Aday | Adres | Lisans | Son etkinlik | Bizim için alınacak fikir |
|---|---|---|---|---|
| **ViMax** | github.com/HKUDS/ViMax | MIT | push 30.9.2026, 12.7k★ | Kod okundu: `agents/best_image_selector.py` → VLM ile **N aday görselden en tutarlısını seçme**. Ölçütler: Character Consistency (cinsiyet, yaş, yüz, saç, beden), Spatial Consistency ("A soldaysa tersine dönmemeli"). `agents/storyboard_artist.py` → her planı **ilk kare / son kare / hareket** üçlüsüne ayırma; ögeleri kadrajda konumuyla tarif etme ("solda, sağa bakıyor"); karakterlere adla değil görünür özellikle atıf. `agents/camera_image_generator.py` → **kamera konumu ağacı**: aynı kamera konumundaki planlar aynı başlangıç karesi soyundan üretilir; PySceneDetect ile istenmeyen kesme ayıklanır. `reference_image_selector.py` → referans olarak karakter kartlarının yanında **önceki planların karelerini** de seçme |
| VideoDirectorGPT | github.com/HL-hanlin/VideoDirectorGPT | lisans dosyası yok | 2024-08 | Plan şeması: sahne başına varlık listesi, kare kare kutu yerleşimi, **"tutarlılık grupları"** (aynı varlık = aynı gömme) |
| DreamRunner | github.com/wz0919/DreamRunner | lisans dosyası yok | 2025-06 | LLM ile hiyerarşik hikâye → plan → hareket planı |
| MovieAgent | github.com/showlab/MovieAgent | lisans yok | 2025-03 | Çok ajanlı CoT plan (senaryo → plan → kamera) |

ViMax istemleri MIT lisanslı. Yapıları uyarlanabilir (İngilizce istemleri birebir kopyalamak yerine kendi
kurallarımızla yeniden yazmak daha temiz olur).

### 1.5 Kimlik ve tutarlılık kıyas setleri (metrik tarifi için)

| Aday | Adres | Lisans | Son etkinlik | Ne öğretir |
|---|---|---|---|---|
| ViStoryBench | github.com/ViStoryBench/vistorybench | Apache-2.0 | 2026-05 | CIDS skoru: GroundingDINO ile karakteri bul → yüz/gövde gömmesiyle referansla karşılaştır; ayrıca "kopyala-yapıştır" cezası (referansın birebir kopyası da kötü). CSD stil skoru |
| OpenS2V-Nexus | github.com/PKU-YuanGroup/OpenS2V-Nexus | Apache-2.0 | 2026-05 | Özneden videoya değerlendirme. Yüz için CurricularFace (glint360k r101) kullanılıyor |
| VBench / VBench-2.0 | github.com/Vchitect/VBench | Apache-2.0 | 2026-08 | `Human_Anatomy`, `Human_Identity`, `Human_Clothes` boyutları kendi videolarımızda çalışır. **Ancak CUDA + flash-attention + mmcv ister → Windows/CPU'da pratik değil** |
| EvalCrafter | github.com/evalcrafter/EvalCrafter | lisans yok | 2024-10 | 17 metrik (RAFT ile warp hatası, yüz tutarlılığı) |

---

## 2. Klipler arası geçiş: son kare → ilk kare, extend, ilk/son kare

### 2.1 Veo API (resmî SDK kaynağından doğrulandı: `googleapis/python-genai`, `types.py`)

- `GenerateVideosSource.image` = başlangıç karesi. `video` = **uzatma (extension)** girdisi.
  "image" ile "video" birlikte verilemez.
- `GenerateVideosConfig.last_frame` = **bitiş karesi** ("Only supported for image to video use cases").
- `reference_images` (tip `ASSET`: karakter/nesne/sahne; `STYLE`: estetik): docstring'e göre
  **"The image, video, or last_frame field are not supported"**. Yani referans görseller ile başlangıç ya da
  bitiş karesi **aynı istekte birlikte kullanılamaz**. (Veo 2 için en çok 3 ASSET ya da 1 STYLE yazıyor.)
  → **Sonuç:** Kimlik başlangıç karesinin içinde "pişmiş" olmalı. Kimliği ilk görsel taşır, video modeli
  onu korumaya çalışır. Bu da **başlangıç karesi denetimini (Kapı G1) en kritik kapı yapıyor**.
- `seed`: aynı girdiyle aynı tohum tutarlı sonuç verir. Yeniden üretimde tohumu kaydetmek yararlı
  (Flow arayüzünde bu ayar görünmeyebilir).
- `negative_prompt`, `duration_seconds`, `resolution` (720p/1080p), `aspect_ratio` (16:9, 9:16) var.

### 2.2 Flow (Scenebuilder) — **doğrulanmadı, yalnız arama özeti**

- "Extend": Flow, kesintisiz devam için üretimin **son 24 karesini** dikkate alıyor (Flow SSS özeti).
  "Jump to": önceki planın bağlamını koruyarak yeni plana geçiyor. Yalnız Veo ile üretilmiş videolarda çalışıyor.
- Hatta kullanımı: **aynı plan içindeki devam eden eylem** için Extend, açı değişen kesme için Jump to ya da
  yeni başlangıç karesi. Memmet'e ekleneceği zaman arayüz yeniden kontrol edilmeli. Model değiştirme
  uyarısına dikkat (03_DERSLER: tek model, uyarıda dur).

### 2.3 Zincirleme yöntemi (öneri)

Her plan geçişi önceden üç türden birine ayrılır (plan alanı `gecis_turu`):
1. **`devam`** (aynı eylem, aynı açı): önceki klibin **kurguda kullanılan kesme anındaki karesi** (teknik son kare
   `-sseof` kullanılmaz; TASARIM D-15) bir sonraki klibin **başlangıç karesi** olur, ya da Flow Extend kullanılır. Risk: her nesilde kalite düşer
   (720p sıkıştırma birikir). En çok 2 zincir, sonra temiz bir görselle "yeniden demirle".
2. **`kesme_ayni_mekan`** (açı değişir): son kare **referans** olarak Gemini görsel ajanına verilir. Yeni açıdan
   başlangıç görseli üretilir (karakter kartı + mekân kartı + "önceki planın son karesi" = en çok 2 kart
   kuralına dikkat: karakter kartı + son kare). ViMax'in "kamera ağacı" mantığı: aynı kamera konumuna
   dönen planlar, o konumun ilk onaylı görselinden türetilir.
3. **`yeni_sahne`**: bağımsız başlangıç karesi. Süreklilik yalnız kostüm, nesne ve ışık listesinden denetlenir.

İsteğe bağlı **bitiş karesi** (`last_frame`): nesnenin bir yerden ötekine taşındığı, karakterin kadrajdan
çıktığı planlarda başlangıç ve bitiş durumunu sabitlemek için kullanılır. ViMax'in ilk/son kare ayrıştırma
istemi: "kareler anlık görüntü olmalı, devam eden eylem içermemeli" kuralı alınmalı.

### 2.4 Plan listesi ve süreklilik formatları

- Profesyonel script supervisor kayıtlarında (arama sonuçları, ScreenSkills iş tanımı) şunlar her çekim için
  tutuluyor: sahne/kurulum/çekim no, **ekran yönü (screen direction)**, plan ölçeği, oyuncu hareketi,
  **bakış çizgisi (eyeline)**, lens/odak, kamera hareketi, kostüm/aksesuar/replik notları.
  Tek bir standart form yok. Alan listesi §6'da bu kalemlerden derlendi.
- **OpenTimelineIO** (github.com/AcademySoftwareFoundation/OpenTimelineIO, Apache-2.0, push 22.10.2026,
  PyPI 0.18.1, Windows wheel var): kurgu zaman çizelgesi değişim formatı. `plan_kurgu.py` çıktısını OTIO'ya
  da yazmak, kurgu sonrası "hangi plan hangi sırada, ne kadar" bilgisini denetçilere vermeyi kolaylaştırır.
  İsteğe bağlı; CapCut doğrudan OTIO okumaz.

---

## 3. Otomatik video kalite denetimi

| Aday | Adres | Lisans | Son etkinlik | Ne yapar | Win / CPU | Kapı |
|---|---|---|---|---|---|---|
| **ffmpeg filtreleri** `blackdetect`, `freezedetect`, `silencedetect`, `scdet`, `blurdetect`, `blockdetect`, `ebur128` | FFmpeg `doc/filters.texi` (okundu) | LGPL/GPL (ikili) | — | Siyah kare, donma, sessizlik, sahne değişimi, bulanıklık, blok bozulması, LUFS | **Evet**, hatta zaten var | **Kapı V1 (teknik)** = `kalite_denetim.py` |
| **PySceneDetect** | github.com/Breakthrough/PySceneDetect | BSD-3-Clause | push 22.10.2026, PyPI 0.7.2 (12.10.2026), py≥3.10, saf Python wheel | `ContentDetector` (varsayılan eşik 27), `AdaptiveDetector` (hızlı kamera), `ThresholdDetector` (karartma) | **Evet**, CPU, OpenCV | Kapı V1: **8 sn'lik klip içinde istenmeyen kesme** (Veo bazen kendiliğinden kesme koyar) + kurgu sonrası plan sınırlarını doğrulama |
| TransNetV2 | github.com/soCzech/TransNetV2 | MIT | push 2023-12; `transnetv2-pytorch` 1.0.5 (2025-06), py≥3.10 | Yapay sinir ağıyla plan sınırı tespiti (yumuşak geçişlerde daha iyi) | torch CPU, yavaş ama olur | PySceneDetect'e ikinci görüş. Şart değil |
| **MediaPipe** Hand/Face Landmarker | github.com/google-ai-edge/mediapipe | Apache-2.0 | push 22.10.2026, PyPI 1.1.1 `py3-none-win_amd64` | El 21 nokta + **handedness** (sol/sağ). Yüz 478 nokta + `facial_transformation_matrixes` (baş pozu) | **Evet**, CPU'da hızlı | Kapı G1/V2: **ters el, el sayısı, bakış/baş yönü, ışık yönü** (§4) |
| VBench-2.0 `Human_Anatomy` (ViTDetector) | github.com/Vchitect/VBench (VBench-2.0/) | Apache-2.0 | 2026-08 | Bozuk el/yüz/gövde anomalisi tespiti | CUDA, flash-attn, mmcv → **Windows/CPU'da pratik değil** | Yalnız bulut/GPU varsa. Yerine VLM kullanılır |
| DOVER / DOVER-Mobile | github.com/VQAssessment/DOVER | **S-Lab License (yalnız ticari olmayan)** | 2024-08 | Estetik + teknik video kalite puanı, Mobile CPU'da ~1.4 sn/video | CPU olur | Ticari kanal için **önerilmez** |
| pyiqa (IQA-PyTorch) | github.com/chaofengc/IQA-PyTorch | **PolyForm Noncommercial 1.0.0** | 2026-10 | MUSIQ, NIQE, CLIP-IQA vb. görüntü kalite metrikleri | CPU olur | Ticari kanal için **önerilmez**. Yerine ffmpeg `blurdetect` + Laplacian varyansı |
| VMAF | github.com/Netflix/vmaf | BSD-2-Clause-Patent | 2026-10 | Referanslı kalite (sıkıştırma kaybı) | ffmpeg `libvmaf` | Yalnız dışa aktarma kalitesini ölçmek için (referans gerekir) |
| VideoScore | github.com/TIGER-AI-Lab/VideoScore | MIT (kod) | 2025-12 | Mantis-8B tabanlı, 5 boyutta (görsel kalite, zamansal tutarlılık, …) insan benzeri puan | 8B model, GPU ister | Önerilmez (CPU yok) |
| CoTracker | github.com/facebookresearch/co-tracker | **CC BY-NC 4.0** | 2026-03 | Nokta izleme | GPU tercih | Ticari değil, alınmaz |
| TAPNet / TAPIR | github.com/google-deepmind/tapnet | Apache-2.0 | 2026-09 | Nokta izleme (nesne "kayma" ölçümü) | ağır | İleride; şart değil |

**ffmpeg varsayılanları (filters.texi'den):** `freezedetect` noise −60 dB, süre 2 sn;
`blackdetect` d=2.0, pic_th=0.98; `silencedetect` −60 dB, 2 sn; `scdet` eşik 10.
8 sn'lik kliplerde bu süreler **çok uzun**. §6'daki kısaltılmış değerler önerilir.

---

## 4. Sinema süreklilik kurallarını makineyle denetlenebilir yapmak

Genel ilke: **önce kâğıt üstü (plan JSON'u) kural denetimi** yapılır, kredi yok. Sonra **görüntüden ölçülen
gerçek değerler** plandakiyle karşılaştırılır. 180 derece kuralını doğrudan görüntüden tespit eden olgun bir
açık kaynak araç **bulunamadı**. Arama yalnız blog ve eğitim yazıları ile bir 3D animasyon aracının
"iki karakter görünür olmalı" şartlı çizgi geçiş denetimini gösterdi. Bu yüzden kural, ölçülebilir
vekillere bölünür:

| Kural | Kâğıt üstü denetim (plan JSON) | Görüntüden ölçüm (araç) |
|---|---|---|
| **180° / eksen** | Sahnede bir `eksen` tanımlanır (ör. `["mara","voss"]`). Her planda `kamera_tarafi` ("A"/"B") verilir. Aynı sahnede ardışık iki plan farklı taraftaysa ve aradaki planda `eksen_gecis: true` (nötr plan, kamera hareketiyle geçiş) yoksa → HATA | İkili planda karakterlerin **soldan sağa sırası**: yüz eşleşmesi (SFace) kutularının x-sırası `kadraj_sirasi` ile aynı olmalı. Tekli planda bakış yönü işareti (aşağıda) eksene uymalı |
| **Bakış yönü / eyeline** | Plan `bakis` alanı: `"kadraj_sagi"`, `"kadraj_solu"`, `"kamera"`, `"asagi"`. Karşılıklı konuşmada A sağa bakıyorsa B sola bakmalı (ters plan) | MediaPipe Face Landmarker `facial_transformation_matrixes` → **yaw** açısı. \|yaw\| > 15° ise yön işaretten okunur. Not: işaret kuralı bir test görselinde bir kez doğrulanmalı. L2CS-Net (github.com/Ahmednull/L2CS-Net, MIT, 2024-02, CPU destekli) göz bakışı için ikinci görüş olabilir, ancak ağırlıklar Google Drive'dan iniyor |
| **Ekran yönü (hareket)** | `hareket_yonu`: "soldan_saga" / "sagdan_sola". Kovalama ya da yürüyüşte ardışık planlar aynı yönde olmalı | Klipte kişi kutusunun merkezinin x ekseninde ilk → son kare değişimi (yüz ya da poz noktaları). Optik akış gerekmez |
| **Ters el / nesne hangi elde** | `nesneler: [{ad:"eldiven", kimde:"mara", el:"sol"}]`. Nesne yolu listesi: her planda nesnenin konumu | MediaPipe Hand Landmarker handedness + açık sözcüklü nesne bulucu (OWLv2 ya da Grounding DINO, `transformers` içinde; Apache-2.0) → nesne kutusu hangi el kutusuyla çakışıyor. **Dikkat (MediaPipe belgesi):** "handedness is determined assuming the input image is mirrored". Ayna olmayan film karesinde **sol/sağ çıktısı ters çevrilmeli**. Ayrıca karakterin kameraya sırtı dönükse el ataması tersine döner. Bu durumda VLM'e bırak |
| **Kaybolup belirme** | `kadrajdakiler` listesi + `giris_cikis` (ör. `{"voss":"sagdan_girer@4s"}`). Önceki planda kadrajdaki karakter, sahnede kalıyorsa bir sonraki planda ya görünmeli ya `kadraj_disi_ama_mekanda` diye işaretlenmeli | Klipten 0.5 sn arayla kare örnekle → her karede yüz sayısı/kimliği. Sayının plan açıklamasız değişmesi ya da DINOv2 ardışık kare benzerliğinde ani düşüş → BAYRAK |
| **Işık yönü / ambiyans** | Sahne düzeyinde `isik: {ana_kaynak:"fener", yon:"kadraj_solu", renk_sicakligi:"sicak", gun_saati:"gece"}`. Planlar sahneden miras alır, değişiklik yalnız `isik_degisimi` ile | (a) Yüz noktalarıyla yanak sol/sağ yarı parlaklık oranı > 1.25 → ışık o taraftan. (b) Ardışık iki planın Lab renk ortalaması farkı (ΔE) ve ortalama parlaklık farkı. (c) Kesin karar VLM'de |
| **Mekân / nesne zıplaması** | Oda krokisi: kapı, ocak, pencere yönleri (`mekan_krokisi`). Planda kamera hangi duvara bakıyor (`kamera_bakis_duvari`) | DINOv2 ile önceki "aynı kamera konumu" planının başlangıç karesine benzerlik; düşükse VLM'e "kapı hâlâ solda mı" sor |

**Plan ölçeği / açı / ışık türü** sınıflandırması için en ciddi açık iş **ShotBench / ShotVL**
(github.com/Vchitect/ShotBench, lisans dosyası yok, 2025-09). Plan ölçeği, çerçeveleme, kamera açısı,
lens, ışık türü ve ışık koşulu dahil 8 sinematografi boyutunu ölçüyor. ShotVL-3B/7B GPU ister.
Kıyas sonuçlarına göre genel VLM'ler bu ayrıntılarda zayıf. Bu yüzden **VLM'e açık uçlu değil,
seçenekli ve tek tek sorular** sorulmalı. **CameraBench** (github.com/sy77777en/CameraBench, NOASSERTION,
2026-03): kamera hareketi (pan, tilt, dolly) sınıflandırmasında da aynı ders var: geometri için klasik
yöntem, anlam için VLM.

---

## 5. Görüntü-dil modeli (VLM) denetçisi — bugünkü elle denetimin kodlanmış hâli

B3'te 44 görselde 21 bozuk kare elle bulundu (yanlış kişi, ters el, yasak ışık). Bu iş, yukarıdaki ucuz yerel
ölçümlerle **önceden süzülür**. Yalnız şüpheli ve kural gerektiren durumlar VLM'e gider:

- **Sağlayıcı**: Claude API (görüntü girişi; CLAUDE.md'deki model `claude-opus-5-5`) ya da Gemini API.
  **Ücretli API**: maliyet plan başına 1–3 görüntülü çağrı. Anahtar yalnız `AYARLAR/` ya da ortam değişkeninde.
  Testlerde `sahte` sağlayıcı.
- **Girdi**: başlangıç karesi + en çok 2 karakter kartı + önceki planın son karesi + o planın süreklilik JSON'u.
- **Çıktı**: zorunlu JSON (ViMax `best_image_selector` yapısına benzer):
  `{"karar":"GEC|KUCUK_DUZELT|YENIDEN_URET", "hatalar":[{"tur":"ters_el|yanlis_kisi|bakis|isik|nesne|fazla_kisi|anatomi", "aciklama":"...", "duzeltme":"CORRECTION: ..."}], "puan":0-10}`.
- **Soru biçimi**: ShotBench/CameraBench dersine göre her kural için ayrı, seçenekli soru sorulur
  ("Lantern is in which hand of the woman? A) left B) right C) none D) not visible").
- **Best-of-N**: Flow'dan 2–4 görsel geldiyse VLM en tutarlıyı seçer (ViMax yöntemi). Hiçbiri geçmezse
  `YENIDEN_URET` kuyruğuna "CORRECTION:" cümlesiyle girer (mevcut 5. adım).

---

## 6. Önerilen süreklilik sistemi

### 6.1 Plan başına süreklilik alanları (SAHNELER.json uyumlu)

> **Tarihsel öneri; geçerli şema TASARIM §5.1** (`semalar/plan_v2.json`). Aşağıdaki `sureklilik` alt nesnesi, `plan_olcegi`, `kamera_konumu`
> ve plan içi `denetim` v2'de başka yerdedir; alanların v2'deki yeri TASARIM §5.1 kural 8'deki eşleme tablosundadır.

Mevcut alanlar (`no`, `parti`, `referans`, `gorsel_istem`, `hareket_istem`, `amac`, `duygu`, `replik`)
**aynen kalır**. Her sahne nesnesine isteğe bağlı bir `sureklilik` alt nesnesi eklenir. Eski dosyalar bu alan
olmadan da çalışmaya devam eder. Film düzeyinde `mekanlar` ve `sahne_gruplari` eklenir.

```json
{
  "mekanlar": {
    "magara_agzi": {
      "kart": "02_MEKANLAR/magara_agzi.jpg",
      "kroki": {"giris": "kuzey", "ates": "dogu", "ucurum": "bati"},
      "isik": {"ana_kaynak": "fener", "yon": "kadraj_solu", "renk_sicakligi": "sicak", "gun_saati": "alacakaranlik", "hava": "kar"},
      "ambiyans": "ruzgar_kar_magara_ici"
    }
  },
  "sahne_gruplari": {
    "S03": {"mekan": "magara_agzi", "eksen": ["mara", "ember"], "planlar": [3, 4, 5]}
  },
  "sahneler": [
    {
      "no": 3,
      "parti": 1,
      "referans": ["mara", "ember"],
      "gorsel_istem": "...",
      "hareket_istem": "...",
      "sureklilik": {
        "sahne_grubu": "S03",
        "gecis_turu": "kesme_ayni_mekan",
        "onceki_plan": 2,
        "kamera_konumu": "S03_K1",
        "kamera_tarafi": "A",
        "eksen_gecis": false,
        "plan_olcegi": "orta",
        "kamera_acisi": "goz_hizasi",
        "kamera_hareketi": "yavas_ileri",
        "kamera_bakis_duvari": "giris",
        "kadrajdakiler": [
          {"id": "mara", "konum": "sol_ucte_bir", "bakis": "kadraj_sagi", "poz": "diz_cokmus",
           "kostum": "kurk_yakali_deri_ceket", "durum": "eldiven_sol_elde_tek"},
          {"id": "ember", "konum": "sag_ucte_bir", "bakis": "kadraj_solu", "olcek": "kedi_boyu"}
        ],
        "kadraj_sirasi": ["mara", "ember"],
        "kadraj_disi_ama_mekanda": [],
        "giris_cikis": {},
        "hareket_yonu": null,
        "nesneler": [
          {"ad": "fener", "kimde": "mara", "el": "sag", "durum": "yanik"},
          {"ad": "eldiven", "kimde": "mara", "el": "sol"}
        ],
        "isik": "miras",
        "isik_degisimi": null,
        "yasaklar": ["ikinci_ates", "acik_kapi", "ucuncu_kisi"],
        "ilk_kare_tarifi": "Mara kneels left third facing right, lantern in right hand ...",
        "son_kare_tarifi": "Mara's gloved left hand 20 cm from Ember's snout ...",
        "son_kare_kullan": false,
        "kurulmus_bilgi": ["ember_magarada"],
        "uretim": {"saglayici": "flow", "model": "omni", "seed": null, "deneme": 1,
                   "secilen_gorsel": "03_GORSELLER/s03_b.jpg", "video": "04_VIDEOLAR/s03.mp4"},
        "denetim": {"G1": null, "V1": null, "V2": null, "K1": null}
      }
    }
  ]
}
```

Alan açıklamaları (kısa):
- `gecis_turu`: `devam` | `kesme_ayni_mekan` | `yeni_sahne` (§2.3). Zincirleme ve referans seçimini bu alan belirler.
- `kamera_konumu`: aynı konuma dönen planlar o konumun ilk onaylı görselinden türetilir (ViMax kamera ağacı).
- `kamera_tarafi` + `eksen_gecis` + sahne grubunun `eksen`'i: 180° kâğıt denetimi.
- `kadrajdakiler[].konum/bakis`: ölçülen yüz konumu ve yaw ile karşılaştırılır.
- `nesneler[].kimde/el`: nesne yolu ("kim nerede / nesnenin yolu" listesinin makine hâli).
- `kurulmus_bilgi`: hikâye denetimi. Bir bilgi ya da nesne ilk kez kullanılmadan önce bir planda kurulmuş olmalı (03_DERSLER).
- `denetim`: her kapının sonuç özeti (`GEC`/`BAYRAK`/`HATA` + rapor yolu). `film.py` kaldığı yerden devam ederken bunu okur.

### 6.2 Denetim kapıları, araçları ve eşikleri

Her kapı `RAPORLAR/<kapi>_<parti>.json` raporu ve gerekiyorsa `YENIDEN_URET.json` kuyruğu üretir.
Eşikler **başlangıç değeridir**. Kaynağı olanlar belirtildi, kalanlar §7'deki gibi ayarlanır.

**K0 — Kâğıt üstü süreklilik (kredi yok, ağ yok, saf Python)** → `sureklilik_denetim.py --kagit`
- 180°: aynı `sahne_grubu`nda ardışık planlarda `kamera_tarafi` değişti ve `eksen_gecis` false → HATA.
- Bakış: karşılıklı iki tekli planda iki karakterin `bakis` değerleri birbirine dönük değil → HATA.
- Nesne yolu: nesne bir planda `kimde: X` iken sonraki planda açıklamasız `kimde: Y` → HATA. `el` değişimi → BAYRAK.
- Kaybolma: önceki planda kadrajda olan karakter sonraki planda ne `kadrajdakiler` ne `kadraj_disi_ama_mekanda` ne `giris_cikis` içinde → HATA.
- Işık: `isik` mekândan farklı ve `isik_degisimi` boş → HATA.
- Referans sınırı: `referans` en çok 2 öğe (Flow kuralı). `devam` geçişinde zincir derinliği en çok 2.
- Kurulum: `kurulmus_bilgi` kullanımı kurulumdan önce → HATA.

**G1 — Başlangıç karesi denetimi (video kredisinden ÖNCE; en kritik kapı)** → `sureklilik_denetim.py --gorsel`
1. Kimlik (insan): OpenCV YuNet + SFace, kare yüzü ↔ karakter kartı yüzü kosinüs benzerliği:
   ≥ 0.45 GEC · 0.363–0.45 BAYRAK→VLM · < 0.363 HATA (0.363 = OpenCV resmî eşiği, 0.45 = tahmin).
   Kartta yüz bulunamazsa ya da karakter profilden görünüyorsa → doğrudan VLM.
2. Kişi sayısı: bulunan yüz sayısı > `kadrajdakiler` içindeki insan sayısı → HATA ("ucuncu_kisi").
   Eksikse BAYRAK (sırt dönük olabilir).
3. Kadraj sırası: yüz kutularının x-sırası ≠ `kadraj_sirasi` → HATA (180° / ayna).
4. Bakış: MediaPipe yaw, \|yaw\| > 15° ve işaret `bakis` ile ters → HATA. Bulunamazsa VLM.
5. Ters el: MediaPipe handedness (**ayna düzeltmesiyle**) + OWLv2 nesne kutusu çakışması (IoU > 0.1).
   Plandakiyle ters → BAYRAK→VLM. Güvenilirlik orta olduğu için tek başına HATA verilmez.
6. İnsan olmayan karakter/nesne/kostüm: DINOv2 kırpıntı ↔ kart kırpıntı kosinüsü < 0.5 → BAYRAK→VLM (tahmin).
7. Işık: yanak parlaklık oranı > 1.25 olan taraf ≠ `isik.yon` → BAYRAK→VLM.
8. VLM son söz (§5): BAYRAK'ların hepsi + her planda bir kez `yasaklar` listesi. Karar `YENIDEN_URET` ise
   "CORRECTION:" cümlesi kuyruğa girer. Küçükler (ayna, kırpma) işaret dosyasıyla **bir kez** uygulanır.
   En çok 2 tur, sonra insana.

**V1 — Teknik video denetimi (indirme sonrası)** → `kalite_denetim.py`
- Bütünlük: `ffprobe` süre ≥ 7.5 sn (8 sn klip için), video akışı var (kesik indirme dersi).
- Siyah: `blackdetect=d=0.1:pic_th=0.98:pix_th=0.10` → bulunan her aralık HATA
  (planlı `karartma` varsa hariç).
- Donma: `freezedetect=n=-60dB:d=1.0` → `kamera_hareketi` "sabit" değilse ve karakter hareketi bekleniyorsa HATA.
- Klip içi istenmeyen kesme: PySceneDetect `ContentDetector(threshold=27)` (varsayılan). 8 sn'lik klipte
  ≥ 1 kesme → HATA (gerekirse klip kesmeden önceki parçaya kırpılır). Yumuşak geçişlerde ikinci görüş TransNetV2.
- Titreme: ardışık kare MAE dizisinde (VBench yöntemi) bir değer > 3 × medyan ve > 8 (0–255 ölçeği) → BAYRAK.
- Sessizlik (replik planı): replik penceresinde `silencedetect=n=-50dB:d=1.0` → BAYRAK (dudak denetimine gider).
- Bulanıklık: `blurdetect` ortalaması klip medyanının 1.5 katından kötüyse BAYRAK (tahmin).

**V2 — Video içi süreklilik (klip başına, CPU)** → `sureklilik_denetim.py --video`
- 0.5 sn arayla 17 kare örneklenir.
- Kimlik kayması: her karede SFace benzerliği kart yüzüne göre. İlk kareye göre 0.15'ten fazla düşüş ve
  < 0.363 → HATA ("yüz değişti"). Tahmin değer, 0.363 resmî.
- Belirme/kaybolma: yüz/kişi sayısı plan `giris_cikis` dışında değişirse → HATA.
- Morf / nesne zıplaması: DINOv2 ardışık kare kosinüsü, klip medyanından 0.15'ten fazla düşük bir sıçrama → BAYRAK→VLM (tahmin).
- Ekran yönü: kişi kutusu x-merkezinin ilk → son kare değişimi işareti ≠ `hareket_yonu` → HATA.
- İlk kare sadakati: video ilk karesi ↔ onaylı başlangıç görseli DINOv2 kosinüsü < 0.85 → BAYRAK
  (model başlangıç karesinden saptı) (tahmin).

**K1 — Plan geçişi denetimi (kurgu sırasıyla, A'nın son karesi ↔ B'nin ilk karesi)** → `sureklilik_denetim.py --gecis`
- `devam` geçişi: DINOv2 kosinüsü < 0.80 → HATA (zıplama). Ortalama parlaklık farkı > 12/255 → BAYRAK.
- `kesme_ayni_mekan`: CIE Lab ortalama renk farkı ΔE > 10 ya da parlaklık farkı > 20/255 → BAYRAK
  (ışık/ambiyans zıplaması). `isik_degisimi` varsa hariç.
- Aynı `kamera_konumu`na dönüş: o konumun ilk planının başlangıç karesiyle DINOv2 < 0.70 → BAYRAK→VLM ("kapı hâlâ solda mı").
- Ses ambiyansı: ardışık planlarda aynı sahne grubunda tek sürekli zemin kullanıldığı denetlenir (`ses_katmani.py` ile).
  Ambiyans katmanının LUFS farkı > 3 LU → BAYRAK.
- Bulgular kare paketine (A son kare + B ilk kare yan yana) eklenip **kurgu izleme denetimi** (habersiz seyirci)
  ajanına "kopukluk adayları" olarak verilir.

### 6.3 Kurulum önerisi (Windows, Python 3.10, CPU)

Ana hat için yalnız **ticari kullanıma uygun lisanslı** parçalar:
- `opencv-python` (YuNet + SFace; model dosyaları opencv_zoo'dan, Apache-2.0)
- `mediapipe` (1.1.1, py3-none-win_amd64)
- `scenedetect` (0.7.2; py≥3.10)
- `torch==2.9.1` CPU (son cp310 Windows wheel'i) + `transformers` (DINOv2-small, OWLv2; Apache-2.0)
- ffmpeg (zaten var)
- `onnxruntime` gerekiyorsa `<=1.23.2` (son cp310 Windows wheel'i; yeni sürümler py≥3.11 istiyor)

Ağır ya da ticari olmayan lisanslı araçlar (VBench-2.0, InsightFace modelleri, pyiqa, DOVER, CoTracker,
ShotVL, VideoScore) **ana hatta yok**. Yalnız GPU'lu ortamda kalibrasyon ve araştırma için kullanılabilir.

## 7. Kalibrasyon (eşikleri uydurmamak için)

- B3'ün 44 görsellik setinde 21 kare elle "bozuk" işaretlendi (03_DERSLER). Bu set **etiketli doğrulama verisi**
  olarak kullanılmalı. Her ölçüm için eşik, kaçırma (false negative) oranı ≤ %10 olacak şekilde seçilir.
  Yanlış alarmların bedeli yalnız bir VLM çağrısı olduğu için bu daha kabul edilebilir.
- `ORNEK_3_SAHNE` için `sahte` sağlayıcıyla uçtan uca test: sentetik bozuk girdiler (aynalanmış kare → kadraj
  sırası HATA, 1 sn siyah ekleme → V1 HATA, kart dışı yüz → G1 HATA). Ağ ve kredi gerekmez.

## 8. Bot tespiti notu

Bu belgede önerilen hiçbir araç Flow'un kısıtlarını atlatmaya yönelik değil. Tüm denetimler indirilen
dosyalar üzerinde yerelde ya da resmî API'lerle çalışır. Flow uyarısında Memmet durur (03_DERSLER).
