# TUR 2 — Claude Code mimarisi: itirazlar, çakışmalar, revize nihai öneri

Hazırlayan: claude-code-mimari uzmanı (Claude Opus 5.5) · 23.10.2026 · Durum: TAMAM (2. tur).

**Bu turda okunanlar**
- `tartisma/` altındaki yedi `tur1_*.md`: senarist ve üretim mühendisi dosyalarının tamamı; yönetmen, kurgucu, görüntü-süreklilik ve
  ses-müzik dosyalarının §1–§4, §6 ve §9'u (benim alanıma dokunan bütün bölümler) ile §5/§8'in alanıma dokunan kısımları; kendi tur 1'im.
- Benden önce yazılmış altı `tur2_*.md` (senarist, yönetmen, kurgucu, ses-müzik, üretim mühendisi, görüntü-süreklilik). Yalnız bana
  ([CM]/[MİM]) yöneltilen maddeler, ad kararları ve ajan kadroları okundu; amaç aynı adları kullanmak ve itirazlara cevap vermektir.
- **Claude Code belgeleri bugün yeniden okundu** (code.claude.com/docs/en/ `settings`, `sub-agents`, `hooks`, `skills`; WebFetch, 23.10.2026).
  Kısaltma: `D/settings`, `D/agents`, `D/hooks`, `D/skills`. Tur 1'den sonra öğrendiğim üç davranış (fork kipinin varsayılan açık olması,
  alt ajanın varsayılan olarak arka planda başlaması, zaman aşımına uğrayan kancanın varsayılan olarak engellememesi) bu turun en önemli
  düzeltmesidir.
- Mevcut kod yeniden bakıldı: `film.py` (`Durdur`, `input()` onayı, `_RAPOR`), `capcut_film.py` (`KURGU/son_capcut_projesi.json` yazıyor),
  `notlari_oku.py`, `.claude/agents/*.md` (klasör adları `_HIKAYE_ODASI`, `_YONETMEN`, `_RAPOR`).

**Dosya kısaltmaları:** `[CM1]` benim tur 1 dosyam · `[SN1]/[SN2]` senarist · `[YN1]/[YN2]` yönetmen · `[KU1]/[KU2]` kurgucu ·
`[GS1]/[GS2]` görüntü-süreklilik · `[SM1]/[SM2]` ses-müzik · `[UM1]/[UM2]` üretim mühendisi.
**Kaynak kısaltmaları (tur 1 ile aynı):** `BK` BILGI_KURALLARI · `ZN` ZANAAT · `RE` ritim_esikleri.json (anahtar adıyla) · `AR1/AR2/AR3`
araştırma 01/02/03 · `UH` 01_URETIM_HATTI · `DR` 03_DERSLER · `YR` YAPIM_REHBERI · `CI` CLAUDE_ICIN · `KR` KARARLAR · `H/<ad>` HAFIZA_YEDEGI notu.
**Etiketler:** **(tahmin)** = kaynağı olmayan başlangıç değeri · **(doğrulanacak)** = belgede yazıyor ya da mantıken gerekiyor ama bu kurulumda
denenmedi; uygulamadan önce §4.9.4'teki listeyle bir kez sınanır.

**Bu turun özü (6 satır)**
1. Tur 1'deki ve [UM2]'deki döngü varsayımı ("ajan döner → PostToolUse kancası sıradakini söyler") güncel Claude Code'da tutmuyor: fork kipi
   v2.1.302'den beri varsayılan açık, ana konuşmanın açtığı alt ajan **arka planda** başlıyor, fork ise **bütün sohbeti miras alıyor** (habersizliği
   bitirir). Çözüm: fork kapalı, kadro dışı ajan kancayla ret, "bitti" kararı yalnız SubagentStop kancasında, döngü iki dönüş biçiminde de doğru.
2. Herkesin habersizlik ve gizlilik güvencesi kancaya dayanıyor; ama kanca bazı ortamlarda hiç çalışmıyor, zaman aşımında da varsayılan olarak
   engellemiyor. Çözüm: `onFailure: "block"`, **kanca nabzı** (kanca devrede değilse `film.py basla` ajan görevi başlatmaz), becerinin içinde yedek kanca.
3. Aşamalı okumayı ana Claude'un `SendMessage`'ı değil **SubagentStop kancası** yürütür: bölüm raporu doğrulanınca betik sonraki bölümü GIRDI'ye
   koyar, kanca aynı seyirci örneğini "devam" talimatıyla sürdürür.
4. Kadro uzmanların tur 2 kararlarıyla **21 ajan**; hepsi `opus`·`high`, Bash'siz, Agent aracısız, `permissionMode: acceptEdits`, `memory` yok;
   6 kör ajanda `omitClaudeMd`. `memmet-bakimci` kaynak koda yazmaz, yalnız aday yama yazar; yamayı korkuluk testleri geçince betik uygular.
5. Ad kararları: `_HIKAYE_ODASI/ _YONETMEN/ _SES/ _RAPOR/ _GOREV/ KUYRUK/ kararlar/`; iki kök (depo + veri kökü) `additionalDirectories` ile;
   dış protokol [UM2]'nin 0–8 çıkış kodları; aşama kodları A00–A18. Geliştirme oturumlarını bozacak statik yasaklar kancaya (sürüşe bağlı) taşındı.
6. Kural yerleşimi: sıkıştırmadan sonra yalnız SKILL.md'nin ilk 5.000 tokeni geri gelir; referans dosyalarının "ilk 40 satırı" geri gelmez.
   Değişmez kurallar sırasıyla **kanca/betik → ajan gövdesi → SKILL.md çekirdeği**'ne yerleşir.

---

## 1. Diğer önerilere itirazlarım (dosya + madde + neden + önerim)

Biçim: **Dosya + madde** · **Ne yazılmış** · **Neden** · **Önerim**. ★ = en önemli üç itiraz. Hepsi doğrudan benim alanıma (ajan çalıştırma,
kanca, beceri, durum, bağımsızlık, kesilme) dokunur. İkisi kendi tur 1 önerimi de düzeltir; bunu açıkça yazıyorum.

### ★ İ-1 · [CM1] §2.0 adım 4–5 ve K-7 · [UM2] §4.2.0 adım 4–5 · [SN2] İ6 · [KU2] §2.6 — Alt ajanın ön planda ve taze bağlamla çalıştığı varsayımı
- **Ne yazılmış:**
  - [CM1] §2.0: "4) SubagentStop kancası çıktıyı doğrular … 5) PostToolUse(Agent) kancası 'sıradaki: …' bağlamını ekler → 1'e dön". [UM2] §4.2.0 aynı akışı aldı.
  - [SN2] İ6 ve [KU2] §2.6: "ana Claude aynı örneği SendMessage ile sürdürür".
  - Bütün uzmanlar "her çağrı yeni, birbirini görmeyen örnek" varsayıyor ([GS2] §4.3, [YN2] §4.3, [SM2] §4.3).
- **Neden yanlış (D/agents, 23.10.2026):**
  1. "With nothing configured, a subagent that Claude spawns from your main conversation starts in the background." Arka plandaki ajanın sonucu
     "a completion notification in a later turn" olarak gelir. Yani PostToolUse(Agent) kancası ajan **başlarken** çalışır. O anda görev bitmemiştir;
     "sıradaki" bağlamı yanlış olur ve ana Claude bitmemiş göreve bağlı işi başlatabilir.
  2. "Fork mode is on by default from Claude Code v2.1.302." "A fork is a subagent that inherits the entire conversation so far … This drops the
     input isolation." "Claude can start a fork on its own while fork mode is on." Ana Claude'un bağlamında konu, karar özetleri, önceki turların
     OZET satırları ve ajan dönüşleri vardır. Seyirci, jüri ya da kör gözlem işini bir fork yaparsa habersizlik tamamen biter. `erisim_kapisi`
     dosya okumayı engeller, ama forkun bağlamında zaten olanı engelleyemez.
  3. Yerleşik `general-purpose` ajanı bütün araçlarla açılır. Ana Claude "şu sahneyi düzelt" işini ona devrederse rol araç kısıtı ve tek yazar
     ilkesi atlanır (rol tablosunda olmayan `agent_type`).
  4. Agent teams açıksa `name` verilen alt ajan "launches as a teammate instead" (D/agents); ekip üyesi kendi kurallarıyla çalışır.
- **Önerim:**
  - `.claude/settings.json → env`: `CLAUDE_CODE_FORK_SUBAGENT=0` (D/agents "Let Claude wait for a subagent"). Agent teams değişkeni tanımlanmaz.
  - **`ajan_kapisi.py`** (PreToolUse `Agent`, yeni kanca): film sürüşü açıkken yalnız kadrodaki 21 ad kabul edilir; `fork`, `general-purpose`,
    `Explore`, `Plan` ve tanınmayan her ad reddedilir. Çağrının istemindeki `GOREV.json` yolu `calisiyor` durumda ve aynı ajan adına bağlı
    olmalıdır; değilse ret (ana Claude defter dışı ajan açamaz). Aynı anda çalışan film görevi 5'i geçerse ret ([UM2]/[YN2] paralel tavanı 5).
    Bu yasaklar statik `permissions.deny`'a konmaz, çünkü aynı depoda çalışan geliştirme oturumları (bu tartışmayı yürüten iş akışı dahil)
    yerleşik ajanlara ihtiyaç duyar (§2.1, karar "sürüşe bağlı yasak").
  - **"Bitti" kararının tek yeri SubagentStop kancasıdır** (`ajan_bitti.py` → `film.py bitir`). PostToolUse(Agent) kancası yalnız bilgi verir ve
    görev durumunu okur: `bitti` ise "sıradaki: …"; `calisiyor` ise "G0041 arka planda; bildirim gelince `film.py sonraki`".
  - SKILL.md döngüsü iki dönüşü de kapsar: Agent sonucu ya da tamamlanma bildirimi → her durumda `film.py sonraki`. `sonraki`, bağımlılığı
    bitmemiş görevi vermediği için ana Claude yanlış sırayla iş başlatamaz.
  - Stop kancası, Stop girdisindeki `background_tasks` doluysa ya da defterde `calisiyor` görev varsa durmaya izin verir; bildirim oturumu uyandırır (doğrulanacak).
  - Ajan çağrısında `name` parametresi kullanılmaz. Aynı yazarın sürdürülmesi ajan kimliğiyle (`agentId`) yapılır.
  - **Araç şartı:** arka plan ajanlarında araç seti küçülür, ama `Read, Write, Edit, Glob, Grep` korunur (D/agents listesi). Hiçbir ajana arka
    planda düşen bir araç verilmez; böylece ajan ön planda da arka planda da aynı çalışır.

### ★ İ-2 · [SN2] İ6 "ileriyi okumak teknik olarak imkânsızdır" · [KU2] §2.6 "İlerisi teknik olarak okunamaz" ve "dört katman" · [GS2] §4.3 · [UM2] §4.4.3 · [CM1] K-3 ve §6 son paragraf — Kancanın her ortamda çalıştığı varsayımı
- **Ne yazılmış:** Habersizlik ve gizlilik "teknik olarak imkânsız" sayılıyor. [CM1] "hata durumunda alt ajan çağrısıysa ret" dedi ama bunun nasıl
  sağlanacağını yazmadı.
- **Neden:**
  1. D/hooks: "A timed-out PreToolUse hook doesn't block the call unless `onFailure: "block"` is set." Varsayılan **açık başarısızlıktır**: kanca
     çökerse ya da süresi dolarsa (çoğu olayda varsayılan 600 sn) araç çağrısı geçer.
  2. D/settings: proje içindeki bulut iş parçacıklarında "none of a repository's `.claude/settings.json` permission rules, hooks, or `env` apply".
     Kâğıt aşaması böyle bir oturumda koşarsa erişim kancası da fork kapatma değişkeni de yoktur.
  3. D/agents: proje ajanlarının frontmatter kancaları çalışma alanı güveni ister ve "a `-p` session doesn't count as trusted". Paylaşılan ayar
     dosyasındaki izin ve `env` değerleri de güven bekler (D/settings).
  4. Sonuç: güvence sessizce kaybolur ve hiçbir rapor bunu söylemez. Kesin karar 3(a) ve 6 açısından en tehlikeli hata türü budur.
- **Önerim (kapalı başarısızlık, ölçülebilir):**
  - Bütün güvenlik kancalarında `"onFailure": "block"` ve kısa `timeout` (erişim ve komut kancası 10 sn, tahmin).
  - **Kanca nabzı:** `komut_kapisi.py` (PreToolUse `Bash|PowerShell`) `film.py basla` komutunu görünce `_GOREV/KANCA_NABZI.json` yazar
    (§4.5.8). `film.py basla` her ajan görevinde nabzı ister: ≤ 15 sn önce yazılmış (tahmin), kanca dosyalarının sha1'i depodakiyle aynı, `env`
    değerleri doğru. Şart tutmazsa görev başlamaz, çıkış `1 HATA` ve düz Türkçe "Kancalar devrede değil; bağımsızlık garanti edilemez".
    Kanca yoksa nabız da yazılmaz; yani kör görev **hiç başlamaz**.
  - **Yedek kanca:** `film-yap` SKILL.md'nin `hooks` alanında aynı `erisim_kapisi` ve `komut_kapisi` komutları. D/skills: beceri kancaları "registers
    when the skill is invoked and keeps running for the rest of the session"; D/hooks: güvenilmemiş klasördeki `-p` koşusunda bile kaydolur.
    Ayar kancası da çalışıyorsa özdeş komutun iki kez koşması zararsızdır (ikisi de aynı kararı verir); tekilleştirme doğrulanacak.
  - **Başsız yürütme** ([UM2] İ-6 `film.py yurut --basliksiz`) kanca istemez: modele yalnız GIRDI içeriği gider. Nabız şartı yalnız Claude Code yolunda aranır.
  - Belgelerde habersizlik "kanca + nabız + paket beyaz listesi" diye yazılır. "Teknik olarak imkânsız" ifadesi nabız testi (T-nabız, §4.6) geçmeden kullanılmaz.

### ★ İ-3 · [UM2] §4.3.3 `memmet-bakimci` — Krediye ve Flow hesabına dokunan kodu film sırasında bir ajanın yerinde değiştirmesi
- **Ne yazılmış:** "Edit ve Write yalnız `memmet.py`, `saglayicilar/flow.py`, `testler/fikstur_flow/*`, `BILGI/FLOW_KESIF.md` için (kanca)".
  "SubagentStop kancası `python -m unittest testler.test_memmet` koşar … Yeşilse `film.py` değişikliği … kaydeder."
- **Neden:**
  1. Film sürerken ve kullanıcının haberi olmadan, krediye ve Flow hesabına dokunan kodu bir ajan **yerinde** değiştiriyor. Bu hem "ajan yalnız
     görevin CIKTI'sine yazar" ilkesini ([CM1] §5.7, bütün uzmanlarca kabul) hem "film yaparken sistem kodu değişmez" ayrımını (`film-gelistir`) deler.
  2. Kesin karar 5'in sessiz ihlal yolu açık kalır. "Seçici bulunamadı" düzeltmesi kılığında bekleme süresini kısaltan, `OLAGANDISI_KELIMELERI`'ni
     daraltan ya da yeniden deneme ekleyen bir değişiklik birim testlerinden geçebilir. Birim testleri fikstürü sınar, **politikayı** sınamaz.
  3. Kancanın dosya düzeyindeki Edit izni, satır düzeyindeki politikayı korumaz.
- **Önerim (ajan kalır, yetkisi daralır; plan → doğrula → uygula, AR3 B4):**
  - `memmet-bakimci` yazar rolündedir ama kaynak dosyalara yazmaz. Yalnız `CIKTI/memmet_yama.diff`, `CIKTI/fikstur/*.html` ve `CIKTI/BAKIM.md` yazar.
  - Betik `memmet_yama.py` yamayı **geçici kopyada** uygular ve üç kapıdan geçirir:
    (a) birim ve fikstür testleri;
    (b) **korkuluk testi** `test_memmet_korkuluk.py` (AST ve düzenli ifade): tempo ve mola sabitleri yalnız artabilir; `OLAGANDISI_KELIMELERI` ve
    `DOGRULAMA_KELIMELERI` yalnız büyüyebilir; `pyautogui|pynput|SendKeys|mouse|keyboard` içe aktarımı yok; yeniden deneme sayısı artmaz;
    `--mod` varsayılanı `elle` kalır; `FLOW_TEMPO.json` okuması kaldırılamaz;
    (c) değişen satır ≤ 80 (tahmin). Aşarsa yama uygulanmaz; bir `film-gelistir` görevi açılır ve hat `7 KISIT` ile durur.
  - Üçü geçerse yama uygulanır, `kararlar/`'a yazılır, kullanıcıya **bilgi** verilir ("Flow ekranı değişmişti, Memmet uyarlandı; ilk blok elle").
  - Onarımdan sonraki ilk blok `elle` modda gider ([UM2] ile aynı).

### İ-4 · [SN2] İ6 · [KU2] §2.6, KR3, KR8 — Aşamalı okumanın ana Claude'un SendMessage'ıyla yürütülmesi
- **Neden:**
  1. Ana Claude her bölüm için ajan kimliğini taşımak zorunda. Sıkıştırma ya da kesinti sonrası kimlik bağlamdan düşer ([SN2] R13 bunu risk olarak yazıyor).
  2. Her bölüm geçişi ana bağlama bir tur ekler: 3 seyirci × 4 bölüm, kâğıt, plan, animatik ve kurgu turlarında.
  3. D/agents: biten bir ajanı sürdürmek "takes a fresh slot without checking the limit"; paralel tavanı sessizce aşılabilir.
- **Önerim:** Bölüm geçişini **SubagentStop kancası** yürütür. D/hooks: `decision: "block"` + `reason` "keeps the subagent running and delivers
  `reason` to the subagent as its next instruction". Akış:
  1. Seyirci P0 raporunu yazar ve durmak ister.
  2. `ajan_bitti.py` raporu doğrular; `film.py asama-ilerlet G0041` P1'i görevin `GIRDI/`'sine kopyalar.
  3. Kanca `block` döner: "Yeni bölüm GIRDI/P1.md'de. Önceki bölümlere dönme. P1'i oku, CIKTI/rapor_P1.md'yi yaz."
  4. Son bölümden sonra kanca durmaya izin verir; görev `bitti` olur. Ana Claude bu sırada hiçbir şey yapmaz.
  - `stop_hook_active` her devamda `true` gelir; bu yüzden sayaç kancada değil görevde tutulur (`GOREV.json → asamali.siradaki`). Düzeltme sayacı (≤ 2) bölüm başına ayrıdır.
  - Yedekler sırası: (1) SubagentStop devamı; (2) ana Claude'un `SendMessage`'ı; (3) [SN2] R13'teki bölüm başına ayrı görev + seyircinin kendi
    önceki raporu GIRDI'de. Hangisinin kullanılacağına kurulumdaki T-asamali testi karar verir.
  - Aynı mekanizma kâğıt, plan, ilk 2 dk, animatik ve kurgu kiplerinde ortaktır.

### İ-5 · [CM1] K-7b ve §5.6 · [GS2] §4.8.7 · [SM2] §2.5 · [UM2] §5.8 — Derslerin SubagentStart kancasıyla ajana verilmesi (kendi önerimin düzeltmesi)
- **Neden:**
  1. Kancanın eklediği metin görevin girdi imzasına girmez. Aynı görev iki kez koşarsa farklı ders setiyle koşabilir. [UM2]'nin "hangi düzeltme
     işe yaradı" ölçümü (`sonuc` alanı) bozulur.
  2. [SN2] hikâye derslerini brifinge koyuyor. İki yol aynı dersi iki kez verir.
- **Önerim:** Dersler yalnız **GIRDI**'de verilir. `film.py` görevi kurarken `DERSLER_AKTIF.md`'den rol etiketli satırları `GIRDI/DERSLER.md`'ye
  kopyalar; dosya `girdi_imza`'ya girer. Kör rollere hiç verilmez. SubagentStart kancası yalnız değişmez iki satırı ekler: "İlk işin GOREV.json'u
  okumak. Yalnız GIRDI/'yi oku, yalnız CIKTI/'ye yaz." D/hooks'a göre alt ajan kendi bağlamını sıkıştırınca bu satırlar yeniden eklenir.

### İ-6 · [GS1] §4.1 · [SM1] §4.1 ve [SM2] §4.4.1 · [KU1] §4 son blok · [SN1] §4 — Referans dosyasının "ilk 40 satırı / ilk 5.000 tokeni sıkıştırmadan sonra görünür" varsayımı
- **Neden:** D/skills: sıkıştırmada Claude Code "re-attaches the most recent invocation of each skill … keeping the first 5,000 tokens of each".
  Geri gelen, çağrılmış **SKILL.md** içeriğidir. Sonradan okunmuş `reference/*.md` dosyaları geri gelmez. Ayrıca ana Claude bu dosyaları zaten
  okumaz ([CM1] §4.3; [KU2], [SM2], [YN2] kabul etti). Ajanlar SKILL.md'yi değil kendi gövdelerini görür.
- **Önerim:** Kural yerleşim sırası (§4.4.6 tablosu):
  1. Makinede zorlanabiliyorsa kanca ya da betik.
  2. Ajanı bağlıyorsa ajan gövdesinin ilk satırları (alt ajanın sistem istemi her zaman bağlamdadır).
  3. Ana Claude'u bağlıyorsa SKILL.md çekirdeği (ilk ≈ 110 satır, ≤ 4.500 token, tahmin).
  - Referans dosyaları yalnız açıklamadır. "Sıkıştırmadan sonra görünsün" diye kural taşımaz. Örnek: [SM2] §4.4.1'in 10 kuralı `ses-tasarimcisi`
    gövdesine, `ses_plani.py` denetimine ve `komut_kapisi`'na dağılır.

### İ-7 · [SN2] §2.2 `_HIKAYE_ODASI/` · [YN2] §4.2 `30_YONETMEN/` · [SM2] Ç-2 `35_SES/` · [CM1] §5.1 `10_PROJE/ 20_HIKAYE/ RAPORLAR/` · [UM2] `_RAPOR/`, `KUYRUK/` — Aynı filmde iki ad kuralı
- **Neden:** [SN2] son sözü mimariye bıraktı. [YN2] ve [SM2] benim tur 1 numaralarımı aldı. [UM2] mevcut kodu (`_RAPOR`) seçti. Karışık ad kuralı
  erişim politikasını (`erisim.json` desenleri) ve `.gitignore`'u da karışık yapar.
- **Önerim (karar):** Tek kural: `_` ile başlayan klasör = hattın çalışma klasörü, kullanıcı açmaz; ön eksiz büyük harfli klasör = kullanıcının da
  baktığı medya ve teslim klasörü (mevcutlar: `SIRALI_GORSEL`, `SIRALI_VIDEO`, `SESLER`, `KURGU`, `YAYIN`, `GELENLER`). Buna göre:
  `_HIKAYE_ODASI/`, `_YONETMEN/` ([YN2]'nin `30_YONETMEN` adı buna döner), `_SES/` ([SM2]'nin `35_SES` adı buna döner), `_RAPOR/`, `_GOREV/`;
  istisna olarak iş kuyruğu `KUYRUK/` ([UM2]) ve kayıt klasörü `kararlar/` ([UM2]). `10_PROJE/` kalkar; proje kararları `_HIKAYE_ODASI/01_KONU_KARTI.json`'dadır ([SN2]).
  Gerekçe: mevcut kod ve sekiz ajan taslağı bu kuralla yazılmış; CLAUDE.md "mevcut araçlarla aynı stil ve klasör yapısı" diyor.

### İ-8 · [SN2] §4.3 `yapimci` doktor kipi "tek-seyirci KRİTİK reddi" · [KU2] §4.3 "Hakem … `KRITIK_RED`" — Kapı eşiğinin bir ajan kararıyla aşılması
- **Neden:** KRİTİK = 0 eşiği hattın en güçlü kalite kapısıdır. Bir ajanın "bu KRİTİK geçersiz" demesi ölçüt avcılığının (Goodhart) en kısa yoludur.
  Yapımcı konu kartını ve eksenleri yazdığı için içeriğe taraftır.
- **Önerim (kabul, dört şartla):**
  1. Red kararını **yeni örnek** ve o içeriğin yazarı olmayan bir rol verir. Yazar ajan red isteyemez.
  2. Kanıt, seyircinin **kendi paketinden** satır alıntısıdır. Betik alıntının o seyircinin GIRDI'sinde ve sorunlu bölümden **önce** geçtiğini doğrular.
  3. Tur başına, seyirci başına en çok 1 red (tahmin).
  4. Her red `kararlar/`'a ve ders defterine (`yanlis_alarm`) yazılır; red oranı film sonu raporunda görünür.

### İ-9 · [UM2] §4.1.2 "Kurulumda bir kez: … kurulum ayarları" ve Q9 "Kullanıcıya kurulumda bir kez dürüstçe sorulur" — Kurulumda karar sorusu
- **Neden:** Kesin karar 1 kurulumu da kapsar ("kullanıcıya yalnız konu sorulur"). `soru_kapisi` kurulum sorusu ile film sorusunu ayıramaz.
- **Önerim:** Kurulum soru sormaz; güvenli varsayılanları yazar (dolar tavanı 0, gece kapalı, `elle` mod). A13'te kullanıcıya **bilgi** verilir:
  süre, kredi ve "gece modu için `GECE_IZNI.bat`". Bu bir seçenek bilgisidir, karar sorusu değildir; kullanıcı .bat'a basmazsa hat varsayılanla
  sürer. `soru_kapisi` bu mesaj kalıbını beyaz listeye alır (§4.5.10).

### İ-10 · [UM2] §4.2.0 adım 3 "tür = betik → `film.py calis <id>`" — Uzun yerel işin Bash aracında koşması
- **Neden:** Claude Code'un Bash aracında ön plan komutunun üst sınırı 10 dk'dır (Bash aracı tanımı, 600.000 ms). Uzun yerel işler (40 dk'lık önizleme
  render'ı 15–40 dk [KU1 R11, tahmin], RVC eğitimi, toplu ASR) ön planda koşarsa zaman aşımıyla yarıda kalır ve kesilme kurtarmasına düşer.
- **Önerim:** `film.py calis` 60 sn'yi aşacak işi kendisi `yerel_is.py` kuyruğuna **ayrık süreç** olarak koyar ve `8 BEKLE` döner ([UM2]'nin yeni
  kodu). Ana Claude iki yoldan birini seçer: `film.py bekle <is>`'i arka plan Bash komutu olarak başlatır (bitince oturum uyanır; doğrulanacak)
  ya da turu bitirir. Her iki durumda `DEVAM.bat` doğru yerden sürer, çünkü durum dosyadadır.

### İ-11 · [UM2] İ-3 "Çıplak `git push` yasağı kalır" · [CM1] §6 `permissions.deny` — Geliştirme oturumlarını bozan statik yasaklar
- **Neden:** `.claude/settings.json` bu depoda açılan **her** oturumda geçerlidir: kullanıcının film oturumu da, sistemi geliştiren bulut oturumları da
  (bu tartışmayı yürüten iş akışı dahil). Statik `deny` hiçbir düzeyde ezilemez (D/settings: kurallar birleşir, `deny` önce gelir). `Bash(git push *)`
  ya da `Agent(general-purpose)` yasağı geliştirme oturumunun commit gönderimini ve yerleşik ajanlarını kapatır.
- **Önerim:** Statik `deny`'da yalnız her bağlamda yanlış olanlar kalır: anahtar dosyaları okumak, `robocopy … /MIR`. Bağlama bağlı yasaklar
  (çıplak `git push`, kadro dışı ajan, `memmet.py`'yi doğrudan çalıştırmak) kancalardadır ve yalnız **film sürüşü açıkken** (`FILM_DURUM.otomatik_surus`
  ve `film-yap` becerisi bu oturumda çağrılmış) uygulanır. `film-gelistir` kipinde serbesttir. Push, sürüşte yalnız `film.py esitle --gonder` ile olur
  ([UM2] ile aynı; Python alt süreci Bash aracı değildir, kancaya takılmaz).

### İ-12 · [GS2] §4.3.1 ve [UM2] §4.3.6 ≈ 145–175 `kare-tarifcisi` görevi · [CM1] §7 "≈ 350–450" — Ana Claude'un bağlam bütçesi
- **Neden:** Ajan dönüşü ≤ 5 satır olsa da her görev ana bağlama ≈ 4 araç çağrısı ekler (`sonraki`, `basla`, Agent, bildirim). 350–550 görevde bu
  ≈ 1.400–2.200 çağrı demektir (tahmin); bağlam film boyunca birkaç kez sıkıştırılır (tahmin).
- **Önerim (itiraz değil, sayı ve önlem):** (1) `film.py sonraki` bir paralel grubun bütün görevlerini tek JSON'da verir, `basla` virgüllü kimlik
  alır (çağrı sayısı yarıya iner); (2) `sonraki` çıktısı ≤ 1.200 kr (tahmin); (3) sıkıştırma beklenen bir olaydır: SessionStart `compact` özeti ve
  SKILL.md'nin geri gelen çekirdeği döngüyü taşır; (4) toplam ajan çağrısı [UM2] §4.3.6'daki ≈ 350–550 kabul edilir (tahmin).

---

## 2. Çakışmalar ve önerdiğim çözüm (alan adları, aşama sırası, sorumluluk sınırları)

### 2.1 Ad ve dosya kararları (Claude Code tarafının nihai önerisi)

| Konu | Öneriler | Karar | Gerekçe |
|---|---|---|---|
| İş birimi | [GS1] `_AJAN_ISLERI/` · [KU1] `AJAN_ISLERI.json` · [SN1] `GOREV_<asama>.md` · [CM1] görev defteri | **`_GOREV/<id>/{GOREV.json, ISTEM.md, GIRDI/, CIKTI/}`** + `film.py sonraki/basla/bitir/kurtar/asama-ilerlet` | Altı uzman tur 2'de kabul etti |
| Dış protokol | 2/3/4 karışık | **[UM2] 0–8 tablosu**; `sonraki` JSON'unda `cikis_kodu` alanı; `film.py ozet` her durumda 0 | `!` komutu sıfır dışı kodda becerinin tamamını iptal eder (D/skills) |
| Çalışma klasörleri | numaralı / alt çizgili | `_HIKAYE_ODASI/ _YONETMEN/ _SES/ _RAPOR/ _GOREV/` + `KUYRUK/`, `kararlar/` | İ-7 |
| Rapor adı | — | `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json` ([UM2] §2.3 kapı ad alanı) | Kapı adları çakışmasın |
| Karar defteri | [CM1] tek `KARAR_DEFTERI.md` | **Olay başına dosya** `kararlar/<zaman>_<kaynak>.json`; `KARAR_DEFTERI.md` betikle türetilir ([UM2]) | İki makine aynı dosyaya eklemesin |
| Ders defteri | beş biçim | **`<veri_kok>/BILGI/DERSLER/ham/<zaman>_<film>_<olay>.json`**; `DERSLER_AKTIF.md` türetilir ([UM2], [GS2]) | Bozuk son satır ve git çakışması olmaz |
| Görev defteri | [CM1] `DEFTER.jsonl` | Durumun kaynağı her görevin `GOREV.json`'u (atomik yazım). `DEFTER.jsonl` yalnız olay günlüğüdür; okuyucu bozuk son satırı atlar. Git'e girmez; karşı ortam `kurtar --yeniden-kur` ile zarflardan kurar ([UM2]) | Tek dosya bozulsa durum kaybolmaz |
| Seri evreni | `KUTUPHANE/` · `EVREN/` | **`<veri_kok>/EVREN/<SERI>/`**, sahip başına ayrı dosya, yalnız `evren.py` yazar | Çoğunluk |
| Dünya defteri | `DUNYA_DURUMU.json` ([CM1]) · `durum_defteri` · `sureklilik_defteri` | **`dunya_defteri.py` → `DUNYA_DEFTERI.json`**; sahibi süreklilik ([YN2] Ç-5). Benim adımı geri çekiyorum | Çoğunluk |
| Kör paket | `ekran_metni.py` · `izleme_paketi.py` · `seyirci_hazirla.py` · `kor_paket.py` | **`kor_paket.py`** çatı (beyaz liste, ad maskeleme, aşamalı klasör) benim; kipler: `kagit/ilk2dk` [SN2], `plan` [YN2], `animatik/kurgu/kesici` [KU2]; `izleme_paketi.py` modül olur | Tek maskeleme kodu |
| GIRDI dilimi | `yonetmen_paket.py` · `dilim.py` | **`dilim.py`** çatı benim; dilim içerikleri alan sahiplerinin ([YN2] Ç-19) | — |
| Şablon | `hat/sablonlar/` ([UM1]) · `sablonlar/` ([CM1]) | **`.claude/skills/film-yap/sablonlar/<ASAMA>_<ajan>[_<kip>].md`**; içeriği alan sahibi yazar; yer tutucu ve OZET biçimi `beceri_denetim.py` ile sınanır | Sayılar eşik dosyasından basılır |
| Referans dosyaları | dağınık | `.claude/skills/film-yap/reference/{hikaye_odasi, yonetmen, goruntu_sureklilik, ses, kurgu, hat}.md` (+ `PLAN_DILI.md` yönetmende) | §4.4.5 |
| Plan `parti` | 20'lik blok ([YN1]) · hikâye partisi | [UM2] kararı: `parti` = hikâye partisi (1–3); `uretim_blogu`, `gemini_paketi`, `izleme_parcasi` ayrı | BK §8 #14 |
| Aşama kodları | A-kodları + iç kodlar | **A00–A18** dış kod; H/Y/GS/KR/S iç kodları şablon adında kalır | [UM2] §2.1 |
| Bağlama bağlı yasaklar | statik `deny` | **Kanca, sürüşe bağlı** (İ-11) | Geliştirme oturumları bozulmasın |
| Ders verme yolu | SubagentStart ([CM1]) | **GIRDI/DERSLER.md** (imzalı) | İ-5 |

### 2.2 Aşama sırası
- Dış sıra [UM2] §2.1 tablosudur (A00–A18; A06s, A07e, A10a–d, A14a, A16n dahil). Benim katkım her aşamanın **görev türleri, ajan·kip adetleri,
  paralel grupları ve ortamı**dır (§4.2.2).
- **Tek düzeltme ([GS2] İ-5):** [UM2] A09 "istem derleme" kart kilidinden (A10d) önce. `gorsel_istem` kimlik dizesini kilitli karttan aldığı için
  A09 ikiye ayrılır: A09 = `istem_derle --hareket` (kimlik, stil, mekân içermez; [YN1] R2) + kart tarifleri (`kart-tasarimcisi`, bulut);
  `istem_derle --gorsel` A11'in ilk betik görevidir ve girdi imzası kilitli kart sürümlerini içerir.
- **Aşamalı okuma** her seyirci aşamasında aynı görev biçimiyle çalışır (İ-4); aşama sırası değişmez.

### 2.3 Sorumluluk sınırları (benim alanım ve komşuları)

| Konu | Tek sahibi | Benim yaptığım | Ötekinin yaptığı |
|---|---|---|---|
| `GOREV.json` biçimi, görev durumları, paralel grup, aşamalı görev, yarım iş davranışı | Claude Code mimarisi | biçim, durum geçişleri, doğrulama sözleşmesi | [UM2] aşama kaydından görevleri üretir |
| `film.py` görev komutları (`sonraki/basla/bitir/kurtar/asama-ilerlet/bekle`) | ortak | sözleşme ve testler (T-defter, T-nabız) | [UM2] kodlar ve aşama kaydına bağlar |
| Aşama sırası, imza, kilit, DUR, ortam, çıkış kodu, `esitle` | üretim | — | hepsi |
| Kancalar (11 betik) | Claude Code mimarisi | hepsi | [UM2] kancaya alan kuralı ekler (Flow kilidi, tempo, `esitle`) |
| `erisim.json` rolleri | Claude Code mimarisi | rol tanımları ve ajan → rol eşlemesi | uzmanlar ajanlarının ne okuyacağını önerir |
| Ajan dosyaları | ortak | frontmatter (model, araç, rol, kip listesi, `maxTurns`) ve ortak gövde kalıbı | gövde içeriği alan sahibinin |
| SKILL.md'ler ve kök CLAUDE.md | Claude Code mimarisi | hepsi | uzmanlar çekirdeğe en çok 2'şer satır önerir |
| `reference/*.md`, `PLAN_DILI.md` | alan sahibi | biçim kuralı (içindekiler, ≤ 300 satır, kural taşımaz) | içerik |
| Şablonlar | alan sahibi | yer tutucu sözdizimi, OZET biçimi, şema bağı | içerik |
| `kor_paket.py`, `dilim.py` | çatı mimaride | beyaz liste, maskeleme, aşamalı klasör, dilim çatısı | kip ve dilim içerikleri |
| `puan_oku.py` v2 | ortak ([KU2], [SN2]) | OZET satırı sözleşmesi | medyan, eşik, birleştirme |
| `memmet.py` ve yaması | üretim | `memmet_yama.py` akışı ve korkuluk testinin yeri | korkuluk kurallarının içeriği |

---

## 3. Diğerlerinden kabul edip kendi önerime kattıklarım

| Kaynak | Kabul ettiğim | Nereye girdi |
|---|---|---|
| [UM2] §4.2.0, §2.6 | 0–8 dış çıkış kodları (8 BEKLE yeni); alt araç kodlarının içeride kalıp `film.py`'de eşlenmesi | §4.2.0, §4.5.3 |
| [UM2] İ-3, §4.5.12 | **İki kök**: Windows'ta depo `Desktop\YZ_FILM_SET` (öneri), Claude Code orada açılır; veri kökü `Desktop\YZ_FILM` yerinde kalır; bağ `AYARLAR/YOLLAR.json`. Benim tur 1'deki "`.claude/`'u veri klasörüne kopyala" önerimi geri çekiyorum | §4.5.1; Claude Code tarafı: `additionalDirectories`, `acceptEdits`, veri kökü `CLAUDE.md` yönlendirmesi |
| [UM2] İ-7, §2.2 | Ders ve karar defterinin olay başına dosya olması | §2.1, §4.5.6 |
| [UM2] İ-8 | `UYARI_GECTI.bat` şartları: elle 1 video başarılı + ≥ 30 dk; yalnız o gün | §4.6 K-4 |
| [UM2] §4.4.3 | Kancalara eklenen alan kuralları (iki kök, Flow kilidi, `memmet.py` doğrudan çalışmaz, `esitle`) | §4.6 K-3, K-4 |
| [UM2] İ-6 | Tek başsız yürütücü `film.py yurut --basliksiz` + tek `saglayicilar/claude_api.py`; tur 1'deki `claude -p` önerimi (K-23) ana yol olmaktan çıkardım | §4.6 K-24 |
| [UM2] §4.3 | `hat-denetcisi`, `ders-editoru` (benim adım), `memmet-bakimci` (İ-3 şartlarıyla) | §4.3.2 |
| [UM2] §4.3.1 | "Tur başına en çok 6 aşama" kuralının kalkması; sürüşü Stop kancası yönetir | §4.2.0 |
| [SN2] İ2 | `IZLEYICI_OZETI.md` kapı seyircisine verilmez; isteğe bağlı 4. "dönen seyirci" medyana girmez. Tur 1'deki "verilir" satırımı geri çekiyorum | §4.5.9 |
| [SN2] İ5, [KU2] | Ayrı, kör `ozet-eslestirici`; tur 1'deki `juri-uyesi` eşleştirme kipimi geri çekiyorum | §4.3.2 |
| [SN2] İ6, [KU2] §2.6 | Aşamalı okuma (mekanizması İ-4'teki gibi) | §4.2.4, §4.5.2 |
| [SN2] İ7 | Mimar önerisinde 3 × 8 başlık değil 10 başlık; 3 × 8 yapı kazanan yazarın işi. Tur 1'deki A03 geçme şartımı düzelttim | §4.2.2 |
| [SN2] İ11 | Başlık adayları, kapak imgesi, bölüm adları hikâye odasında yazılır; `yayin-paketcisi` seçer ve doğrular | §4.3.2 |
| [SN2] §4.3 | `yapimci` (konu, doktor), `hikaye-yazari` (yapi, senaryo, revizyon, dar_degisiklik, evren), `diyalog-editoru`; `konu-analisti`, `hikaye-doktoru`, `evren-arsivcisi`, `anlama-olcer` kalkar | §4.3.2 |
| [SN2] H0 | Konu sorusu metni ("İstersen 'sen seç' yaz" dahil); `soru_kapisi` beyaz listesinde | §4.4.3, §4.5.10 |
| [YN2] §4.3 | `yonetmen` 5 kip (harita, plan, onarim, kart_secimi, ders); `plan-yazari` kalkar; yeni `plan-elestirmeni` (kör) | §4.3.2 |
| [YN2] İ-8 | Bash'siz yönetmen için kroki önerileri ajan çağrılmadan önce betikle hesaplanıp GIRDI'ye konur; kroki ve plan denetimi SubagentStop'ta | §4.2.2, §4.6 K-7 |
| [YN2] Ç-2 | Sahiplik birimi alandır (`_sahip` alan başına); `plan_birlestir` sahiplik tablosunu okur | §4.5.2 |
| [GS2] İ-1 | Kare zinciri = kurguda kullanılan kesme anındaki gerçek kare (Z1); tur 1'deki `son_kare.py` (`ffmpeg -sseof`) önerimi geri çekiyorum | §4.8 |
| [GS2] İ-3 | G1 iki turdan sonra hakemle kapanmaz; kaçış merdiveni (kök neden → yönetmen onarımı → K0 → `durdu` + bilgi). Hakem yalnız tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ alanını karara bağlar | §4.3.2 |
| [GS2] İ-4 | Kör soru formu iki aşamalı, görüntü koordinatında; soruda ad, kostüm, beklenen konum yok; anatomik çeviriyi kod yapar. Tur 1 §5.9 örneğimi geri çekiyorum | §4.5.9 |
| [GS2] §4.3 | `kare-tarifcisi` (benim adım), `kart-tasarimcisi` (yazar), `sureklilik-denetcisi` 4 kip | §4.3.2 |
| [GS2] İ-6 | Gemini bulgu kaynağıdır, onay kaynağı değildir | §4.9.3 |
| [SM2] İ-5 | Tek ses ajanı `ses-tasarimcisi` (kadro, tasarim, muzik); `muzik-supervizoru` ve `ses-denetcisi` kalkar; diyalog yolu kodla önerilir | §4.3.2 |
| [SM2] §4.3.2 | `hikaye-yazari` `replik_kabul` kipi (metne dokunan tek gri karar metnin sahibine gider) | §4.3.2 |
| [SM2] İ-9 | Kör pakette ekran dışı konuşan adla değil ölçüme bağlı `ses_etiketi_tr` ile verilir; kurgu kipinde "duyulan" satırı son miksten çıkar | §4.5.9 |
| [KU2] İ-2 | Kullanıcının CapCut taslağına yazılmaz; klon + yama. `film-not`'taki "aynı projede göreceksin" cümlemi "listenin en üstünde yeni adla" diye düzelttim | §4.4.4 |
| [KU2] İ-6 | Kesme turu oranının paydası "simülasyondan HATA'sız geçen öneriler" | §4.7 |
| [KU2] İ-7 | İzleme kiplerinde kadraj etiketi verilmez; plan numarası kalır | §4.5.9 |
| [KU2] İ-10 | **Düzeltme:** `KURGU/son_capcut_projesi.json` vardır (`capcut_film.py` satır 159 yazıyor; `notlari_oku.py` ve `memmet.py` okuyor). Tur 1 §3.3'teki "böyle bir dosya yok" cümlem yanlıştı | §4.3.3 |
| [KU2] §4.3 | `kurgucu` 4 kip (duzelt, kirp_incele, sifir_kredi, not); `kesici` kör; `kurgu-seyircisi` ayrı ajan değil, `habersiz-seyirci`'nin kipi | §4.3.2 |
| [SN2], [YN2], [KU2], [GS2], [SM2], [UM2] | Ajanlarda Bash yok, `memory` yok, hepsi `opus`·`high`, dönüş ≤ 5 satır, önce başlıkları yaz; denetim SubagentStop'ta (≤ 2 düzeltme) | §4.3.1 |

---

## 4. REVİZE NİHAİ ÖNERİM

**Tek cümlelik öneri:** Hattın beyni `film.py`'nin aşama kaydı ve **görev defteridir**. Ana Claude yalnız "set amiri" olarak defterden sıradaki
görevi alıp ajana, betiğe ya da kullanıcıya (yalnız fiziksel iş için) dağıtır. Bağımsızlık, gizlilik ve "kullanıcıya yalnız konu sorulur" kuralları
metinde değil **kapalı başarısızlıkla çalışan kancalarda** zorlanır, kancaların devrede olduğu da **kanca nabzıyla** kanıtlanır. Böylece oturum
kesilse, bağlam sıkıştırılsa, ajan arka planda bitse ya da kullanım sınırı dolsa da hiçbir iş hafızaya bağlı kalmaz.

### 4.1 Alanımın hedefi ve başarı ölçütü (sayılarla)

**Hedef:** Depo Claude Code'da açıldığında Claude kullanıcıya **yalnız filmin konusunu** sorar. Konudan yayın paketine kadar bütün iş, dosyaya
yazılmış bir görev defteri üzerinden, birbirini okumayan uzman ajanlar ve makine kapılarıyla yürür. Oturum kesilmesi, sıkıştırma, arka planda biten
ajan, kullanım sınırı ya da bilgisayarın kapanması **hiçbir işi kaybettirmez ve hiçbir işi iki kez yaptırmaz**.

| # | Ölçüt | Hedef | Nasıl ölçülür |
|---|---|---|---|
| M1 | Kullanıcıya sorulan **karar** sorusu | Film başına **1** (konu); konu ilk mesajdaysa **0**; kurulumda **0** | `kararlar/` içindeki `SORU` olayları + Stop kancası `soru_kapisi` engel sayısı |
| M2 | Kullanıcıdan istenen fiziksel iş | Yalnız [UM2] M2 listesi; her biri ayrı `kullanici_eylemi` görevi, `.bat` adıyla; bitişi **kendiliğinden algılanan** görev oranı ≥ %90 (tahmin) | `GOREV.json → algilama` dolu oranı |
| M3 | Kesilmeye dayanıklılık | Sahte uçtan uca testte **30 rastgele kesme noktasında** (ajan ortası, aşamalı okumanın bölüm geçişi, betik ortası, kapı ortası, paralel grubun yarısı, arka plan bildirimi gelmeden) %100 tamamlanma; **biten görevin yeniden çalışması 0**; **kredili işin çift gönderimi 0** | `testler/test_gorev_defteri.py` |
| M4 | Bağımsızlık | Bağımsız ajanın başka görev çıktısını okuma denemesine **izin 0**; kör pakette yasak alan ya da ad sızıntısı **0**; aşamalı okumada ileri bölüme erişim **0** | `erisim_kapisi` günlüğü; `test_kor_paket.py`; T-asamali |
| M5 | Fork, yerleşik ya da kadro dışı ajanla yapılan film görevi | **0** (sürüş açıkken) | `ajan_kapisi` günlüğü; `test_kancalar.py` |
| M6 | Kanca nabzı olmadan başlayan ajan görevi; zaman aşımında geçen güvenlik kancası | **0**; **0** | `film.py basla` reddi; `onFailure: "block"` testi |
| M7 | Arka plan dönüşünde yanlış "bitti" | **0** (bitti yalnız SubagentStop doğrulamasıyla) | T-arkaplan |
| M8 | Beceri boyutu | Her SKILL.md < 500 satır (hedef ≤ 250); çekirdek ≤ 4.500 token (tahmin: karakter/3); `description` ≤ 1.024 kr; `description + when_to_use` ≤ 1.536 kr | `beceri_denetim.py` |
| M9 | Ajan tanımları | 21 ajan; açıklamaların toplamı ≤ 3.000 token (belge uyarı eşiği 15.000); hiçbir ajanda `Agent` ve `Bash` aracı yok | `beceri_denetim.py` |
| M10 | Oturum başı özeti | `additionalContext` ≤ 10.000 kr (belge sınırı), hedef ≤ 6.000 kr | `oturum_basi.py` kendi uzunluğunu ölçer |
| M11 | Ana Claude'un bağlamı | Ajan dönüşü ≤ 5 satır / ≤ 600 kr; `sonraki` çıktısı ≤ 1.200 kr (tahmin); ana Claude 200 KB'tan büyük dosyayı Read ile açmaz (tahmin eşik) | `ajan_sonrasi` uyarır; `erisim_kapisi` reddeder |
| M12 | Ajan çıktı sözleşmesi | İlk denemede şemadan geçme ≥ %90 (tahmin); en çok 2 SubagentStop düzeltmesi, sonra görev `gecersiz` → yeni deneme | `DEFTER.jsonl` istatistiği |
| M13 | İzin penceresi | Kâğıt ve ajan aşamalarında **0** izin istemi (izin listesi + ajanlarda `acceptEdits`) | Sahte kuru çalıştırma |
| M14 | Model disiplini | Bütün ajanlar `model: opus`, `effort: high`; `fallbackModel` tanımsız; alt ajanda model sapması olursa o görev yeniden | `PostModelSwitch` kancası, görev kaydı |
| M15 | Geliştirme oturumlarına zarar | Film sürüşü kapalıyken kancaların reddettiği geliştirme işlemi (`git push`, yerleşik ajan, betik düzenleme) **0** | `test_kancalar.py` (sürüş kapalı senaryosu) |

### 4.2 Aşama aşama süreç

#### 4.2.0 Yürütme modeli (bütün aşamalar için ortak)
```
kullanıcı ──(yalnız konu)──► ana Claude (set amiri; film-yap becerisi)
   │ 1) python .claude/bin/film.py sonraki            → görevler[] + cikis_kodu + kullaniciya + oku   (JSON)
   │ 2) python .claude/bin/film.py basla G…,G…        → kanca nabzını denetler; görevler "calisiyor"
   │ 3a) tur=ajan    → aynı paralel_grup (≤ 5) TEK mesajda Agent(subagent_type=<ajan>, prompt=<istem aynen>)
   │                   ajan_kapisi (PreToolUse Agent): kadro/fork/defter/paralel denetimi
   │                   ajan_basi (SubagentStart): 2 sabit satır
   │                   ajan çalışır; erisim_kapisi okumayı görev klasörüne bağlar
   │                   ajan_bitti (SubagentStop): doğrula → (aşamalıysa sonraki bölümü ver, sürdür) → film.py bitir
   │ 3b) tur=betik   → python .claude/bin/film.py calis G…   (uzun iş: ayrık süreç + 8 BEKLE)
   │ 3c) tur=kullanici_eylemi → film.py'nin mesajı aynen; tur biter (bitiş dosyadan algılanır)
   │ 3d) bekle / kisit / ortam / butce → tek cümle; tur biter
   └ 4) Agent sonucu YA DA arka plan tamamlanma bildirimi YA DA kullanıcı "devam" → 1'e dön
        (ajan_sonrasi kancası yalnız bilgi verir; "bitti" kararı 3a'daki SubagentStop'tadır)
```
- **Görev** = `_GOREV/<id>/` klasörü: `GOREV.json` (sözleşme), `ISTEM.md` (`film.py`'nin şablondan doldurduğu talimat), `GIRDI/` (ajanın okuyabileceği
  her şeyin kopyası, dersler dahil), `CIKTI/` (ajanın yazabileceği tek yer). Ana Claude istem yazmaz; aynı görev her seferinde aynı talimatla koşar.
- **Ön plan / arka plan:** `CLAUDE_CODE_FORK_SUBAGENT=0` ile Claude alt ajanı bekleyebilir (D/agents). SKILL.md "sonucu bekle" der. Ajan yine de
  arka planda başlarsa döngü bozulmaz: bitti kararı kancadadır, ana Claude bildirim gelince `sonraki`'ye döner.
- **Kim yapar** kısaltmaları: **AC** ana Claude · **B** betik (`film.py` alt komutu) · **A:<ad>·<kip>** ajan · **K** kullanıcı (yalnız fiziksel iş).
- **Ortam:** **B** bulutta da çalışır (kâğıt + sahte) · **Y** yalnız kullanıcının Windows'u. Bulutta kâğıt sonu `film.py esitle --gonder` + `4 ORTAM`.

#### 4.2.1 Görev türleri

| Tür | Kim yürütür | Bitiş nasıl anlaşılır | Kesilirse |
|---|---|---|---|
| `ajan` | AC Agent aracıyla | SubagentStop kancasının doğrulaması → `bitir` | Yazar: yarım CIKTI yeni görevin `GIRDI/YARIM/`'ına, aynı rol devam eder · Değerlendirici: yarım çıktı arşive, **yeni örnekle sıfırdan** |
| `ajan` + `asamali` | AC başlatır; bölüm geçişlerini SubagentStop kancası yapar | Son bölüm raporu doğrulanınca | Değerlendirici olduğu için sıfırdan; bitmiş bölüm raporları **kullanılmaz** (seyirci ilk okumasını yeniden yaşamalı) |
| `betik` | AC `film.py calis` ile | Çıkış kodu + zarf (`_uretim.girdi_imza`) | Zarf yoksa yeniden; kredili işte önce `memmet_topla` ([UM2]) |
| `uzun_betik` | `film.py` ayrık süreç (`yerel_is.py`) | İş kaydı `bitti` | Kuyruk kaldığı yerden; `8 BEKLE` |
| `kullanici_eylemi` | Kullanıcı | `algilama` (dosya var, ZIP geldi, indirme bitti) | Mesaj yeniden gösterilir, Telegram hatırlatır |
| `bekle` / `kisit` / `ortam` / `butce` | — | Saat, kilit kalkışı, ortam değişimi, bakiye | Durum dosyada; `DEVAM.bat` |

#### 4.2.2 Aşama tablosu (dış sıra [UM2] §2.1; görev türleri, adetler ve paralel gruplar benim)

| Kod | Aşama | Ajan görevleri (ajan·kip × adet; paralel grup) | Betik görevleri | K | Ortam |
|---|---|---|---|---|---|
| A00 | Hazırlık + konu | — | `film.py hazirlik`, `yeni --konu "<aynen>"` | konu yoksa **tek soru** (AC) | B/Y |
| A01 | Konu kartı, proje kararları, B0 | `yapimci·konu` ×1 | `hikaye_odasi konu-denetim`, `kredi B0` | — | B/Y |
| A02 | Brifing | — | `hikaye_odasi brifing` (sha1 sabit; eksen satırı mimarın kendi `ISTEM.md`'sinde) | — | B/Y |
| A03 | 4 mimar önerisi | `hikaye-mimari` ×3 (grup 1) → `hikaye-mimari` bonus ×1 | `oneri-denetim` (10 başlık, çeşitlilik) | — | B/Y |
| A04 | Kör jüri + seçim | `juri-uyesi` ×4 rol + `uretilebilirlik-denetcisi·juri` ×1 (tek grup, 5) | `juri-paketi` (anonimleştirme), `juri-topla` (medyan) | — | B/Y |
| A05 | Yapı, senaryo, oyuncu/diyalog, hikâye makine denetimi | `hikaye-yazari·yapi`, `·senaryo` (parti parti, aynı örnek); `oyuncu` ×≤8 + `diyalog-editoru` ×1 (≤ 5'lik gruplar); `hikaye-yazari·revizyon` | `yapi-denetim`, `oyuncu-paketi`, `senaryo-denetim` | — | B/Y |
| A06 | Kâğıt seyirci (aşamalı), ilk 2 dk, hikâye kilidi | `habersiz-seyirci·kagit` ×3 **aşamalı**; `·ilk2dk` ×3 × 2 sürüm; `ozet-eslestirici` ×3; `yapimci·doktor` (koşullu); `hikaye-yazari·revizyon` | `kor_paket kagit/ilk2dk`, `seyirci-topla`, `devir` (kilit) | — | B/Y |
| A06s | Ses profilleri (A07 ile paralel) | `ses-tasarimcisi·kadro` ×1 | — | — | B/Y |
| A07a | Yönetmen haritaları | `yonetmen·harita` ×3 (parti başına; mekân krokisi ilk kullanımda yazılır) | `kroki --karsilikli` önerileri **ajandan önce** GIRDI'ye; kroki denetimi SubagentStop'ta | — | B/Y |
| A07b | Sahne grubu planları | `yonetmen·plan` × sahne grubu (≈ 45–55; ≤ 5'lik gruplar) | `plan_denetim --sahne` SubagentStop'ta (≤ 2 düzeltme) | — | B/Y |
| A07c | Birleştirme, dünya defteri (K0), Z0, T0, B1 | `yonetmen·onarim` (yalnız HATA'lı sahne) | `plan_birlestir` (sahiplik), `dunya_defteri`, `Z0`, `zaman_cizelgesi`, `kredi B1` | — | B/Y |
| A07d | Kâğıt plan denetimi | `plan-elestirmeni` ×3, `uretilebilirlik-denetcisi·plan` ×3, `sureklilik-denetcisi·kagit` ×3 (parti başına 3'lü gruplar) | `puan_oku` | — | B/Y |
| A07e | Plan seyircisi | `habersiz-seyirci·plan` ×3 aşamalı + `ozet-eslestirici` ×3 | `kor_paket plan` | — | B/Y |
| A08 | Ses kâğıtta | `ses-tasarimcisi·tasarim` × sahne grubu (≤ 5'lik gruplar), `·muzik` ×1 | `ses_plani --taslak/--denetle` (S0) | — | B/Y |
| A09 | Hareket istemi + kart tarifleri | `kart-tasarimcisi` ×1 | `istem_derle --hareket`, `istem_denetim`, `kamera_agaci` | — | B/Y |
| — | **KÂĞIT SONU** | — | bulutta `esitle --gonder` → `4 ORTAM` | yerelde `GUNCELLE.bat` | — |
| A10a–c | Yerel kurulum ölçümü, telaffuz, ses seçimi | `ses-tasarimcisi·kadro` (seçim, yakın puanda) | kurulum ölçümü, telaffuz testi, `ses_sec` | — | Y |
| A10d | Kartlar | `kare-tarifcisi` × aday grubu (≤ 12 görsel/görev); `sureklilik-denetcisi·hakem`; `yonetmen·kart_secimi` | `gemini_paket --kartlar`, `kart_denetim`, `evren.py --kilitle` | Gemini paketi | Y |
| A11 | Başlangıç görselleri + G1 | `kare-tarifcisi` ×≈ 90 (≤ 5'lik gruplar); `sureklilik-denetcisi·hakem/kacis`; `yonetmen·onarim` | **`istem_derle --gorsel`** (kart kilidinden sonra), `gemini_paket`, `kare_denetim`, `duzeltme` | Gemini paketi | Y |
| A12 | Animatik | `habersiz-seyirci·animatik` ×3 aşamalı/parti; `ozet-eslestirici`; `kesici` ×1 (tur 1); `kurgucu·duzelt` | `animatik`, `kor_paket animatik`, `puan_oku` | — | Y |
| A13 | B2 kesin bütçe, önizleme | `hat-denetcisi` ×1 | `kredi B2`, `URETIM_ONIZLEME` | (bilgi) | Y |
| A14a | Pilot dalga (ilk film) | `kare-tarifcisi` (V3), `ders-editoru` (pilot sonrası) | `blok_plani`, `memmet` (`elle`), V1/V2 | `VIDEO_*.bat`, GÖNDER | Y |
| A14 | Video blokları | `kare-tarifcisi` (V3), `sureklilik-denetcisi·hakem`, `yonetmen·onarim`; `memmet-bakimci` (yalnız `arayuz` kısıtında) | `blok_plani`, V1/V2, `kare_zinciri`, `memmet_yama` | aynı | Y |
| A15 | Ses | `hikaye-yazari·replik_kabul` (gri bant) | ses merdiveni (`ses_karar.py`) | — | Y |
| A16 | Kurgu | `habersiz-seyirci·kurgu` ×3 aşamalı/parti; `ozet-eslestirici`; `kesici`; `kurgucu·duzelt/kirp_incele/sifir_kredi` | `plan_kurgu`, S3–S7, Z3, `capcut` (klon + yama) | — | Y |
| A16n | Kullanıcı notu / CapCut düzenlemesi | `kurgucu·not` | `taslak_fark`, `notlari_oku` (salt okunur) | — | Y |
| A17 | Yayın | `yayin-paketcisi` ×1; `kare-tarifcisi` (kapak adayları); `juri-uyesi·youtube_stratejisti` (kapak seçimi) | jenerik, Shorts, final kalite | dışa aktarma; yükleme onayı (isteğe bağlı) | Y |
| A18 | Kapanış | `ders-editoru` ×1; `hikaye-yazari·evren` | `ders_defteri --derle/--uygula`, `evren.py`, arşiv | `ARSIVLE.bat` | B/Y |

#### 4.2.3 Aşamalar arası kurallar
1. **Kredi en sonda:** A00–A13 kredisizdir (görseller Gemini'de 0 kredi). A14'ün girdi imzası A06, A07c–e, A08, A09, A11, A12 raporlarının imzalarını
   içerir ([UM2] sıra kuralı 1); `film.py` bunu `giris_sarti` ile zorlar.
2. **Tek yazar ilkesi:** her alanın tek sahibi var (alan başına `_sahip`, [YN2] Ç-2). `replik.metin` → `hikaye-yazari`; plan alanları → `yonetmen`;
   `zanaat.ses` → `ses-tasarimcisi` (`_SES/SES_<S>.json`, betik taşır); `SAHNELER.json`, `DUNYA_DEFTERI.json`, `_RAPOR/`, `KUYRUK/`, `FILM_DURUM.json`,
   `EVREN/`, `BILGI/DERSLER/` → yalnız betik. `erisim_kapisi` bu dosyalara ajanın ve ana Claude'un yazmasını reddeder.
3. **Revizyonu aynı yazar yapar:** aynı oturumda `SendMessage(<agentId>)` ile aynı örnek sürdürülür (D/agents: "Resumed subagents retain their full
   conversation history"). Oturum kesildiyse yeni örnek açılır; GIRDI'ye önceki sürüm, bütün raporlar ve yazarın `vN_DEGISIKLIKLER.md` tabloları konur.
4. **Değerlendirici her turda yenidir.** Tek istisna aynı tur içindeki aşamalı okumadır (aynı seyirci filmi bölüm bölüm okur; geçişi kanca yapar).
5. **Kapı döngüsü tavanı:** kâğıt 4, kurgu 3, görsel 2 tur (RE, UH §5). Tavan dolarsa [SN2] H11 merdiveni (doktor + 2 yapısal tur → ikinci öneri →
   DUR + bilgi); görselde [GS2] kaçış merdiveni. Hiçbir kapı kendiliğinden "geçti" sayılmaz.
6. **Fiziksel iş ≠ soru:** kullanıcıya yalnız [UM2] M2 listesindeki işler, `.bat` adıyla verilir; bitiş dosyadan algılanır.
7. **Bulut ↔ yerel:** bulut yalnız A00–A09 ve geliştirme. Yerel kâğıt işini tekrarlamaz (imzalar aynı). Taşıma yalnız `film.py esitle`.
8. **Ajandan önce betik:** ajanın Bash'le yapacağı her hesap (kroki önerisi, dilim, soru formu, kesme simülasyonu) görev kurulurken yapılır ve GIRDI'ye
   konur; ajanın sonradan yaptırmak istediği denetim SubagentStop kancasında koşar ([YN2] İ-8).

#### 4.2.4 Kesilme ve kurtarma akışı

| Olay | Kanca / araç | Ne olur |
|---|---|---|
| Kullanım sınırı, API hatası | `StopFailure` (D/hooks matcher: `rate_limit`, `overloaded`, `server_error` …; çıktısı yok sayılır, yan etki yapılabilir) | `hata_kaydi.py`: `calisiyor` görevleri `kesildi` işaretler, `FILM_KAYIT.txt`'ye yazar, Telegram "sınır doldu; açılınca DEVAM.bat" |
| Sıkıştırma (ana oturum) | `PreCompact` (günlük), `PostCompact` (özet arşivi), `SessionStart` matcher `compact` | Durum özeti + değişmez kurallar `additionalContext` ile geri gelir; SKILL.md'nin ilk 5.000 tokeni zaten geri eklenir (D/skills) |
| Sıkıştırma (alt ajan) | `SubagentStart` (D/hooks: alt ajan bağlamı sıkışınca kanca metni yeniden eklenir) | 2 sabit satır geri gelir; ajanın asıl girdisi dosyada olduğu için kayıp yok |
| Yeni oturum / devam | `SessionStart` `startup\|resume\|clear` | Aynı özet; aktif film varsa soru sorulmadan devam |
| Ajan arka planda bitti | Tamamlanma bildirimi + `SubagentStop` | Bitti kararı kancada verilmiştir; AC bildirimle `sonraki`'ye döner |
| Ajan `maxTurns`'e ulaştı | D/agents: çıktı "marked as partial", sürdürülebilir | Yazar: aynı örnek `SendMessage` ile sürer (en çok 1 kez), sonra yeni görev + `GIRDI/YARIM/` · Değerlendirici: sıfırdan, yeni örnek |
| Aşamalı okumanın ortasında kesilme | `GOREV.json → asamali.siradaki` | Değerlendirici olduğu için görev sıfırdan, yeni örnekle; eski bölüm raporları arşive |
| Paralel grubun bir kısmı bitti | Görev durumları | Yalnız bitmeyenler yeniden; bitenler bağımsız olduğu için geçerli |
| Kredili iş | `istek_kimligi` = plan + deneme; "gönderildi" kaydı gönderimden **önce** ([UM2] `KREDI_DEFTERI`) | Kesilmeden sonra önce `memmet_topla`; dosya yoksa ve gönderim kaydı varsa kör yeniden gönderim yasak |
| Kancalar devre dışı | `film.py basla` nabız denetimi | Ajan görevi başlamaz; `1 HATA` + düz Türkçe yönlendirme (KURTARMA.md §Kanca) |
| Otomatik model geçişi | `PostModelSwitch` (`from_model`, `to_model`) | Kayıt. Geçiş bir alt ajan görevinin süresine denk geldiyse o görev `model_sapmasi` → yeniden kuyruğa |
| Uzun betik | `yerel_is.py` | Ayrık süreç sürer; AC `8 BEKLE` ile turu bitirir ya da `film.py bekle`'yi arka planda bekler |

### 4.3 Gereken ajanlar

#### 4.3.1 Kadro ilkeleri (Claude Code düzeyinde)
1. **Ana Claude ajan değildir, set amiridir:** içerik üretmez, puan vermez, ajan çıktısını düzeltmez, plan ya da rapor dosyası yazmaz (YR §1).
   Bağlamını küçük tutar: büyük dosya yerine `film.py ozet/goster`.
2. **Düz yapı:** ajanların `tools` listesinde `Agent` yoktur; iç içe ajan imkânsızdır. Yerelde ayrıca `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1`
   (D/agents "Set `1` to turn nesting off"; `settings.local.json`, §4.6).
3. **Rol başına sabit araç seti** (arka planda da korunan araçlar, İ-1):

   | Rol | Araçlar | Okuma | Yazma | Ek |
   |---|---|---|---|---|
   | `kor` | `Read, Write` | yalnız `{gorev}/GOREV.json, ISTEM.md, GIRDI/**` | `{gorev}/CIKTI/**` | `omitClaudeMd: true` |
   | `denetci` | `Read, Write, Glob, Grep` | `{gorev}/**` + `.claude/skills/film-yap/{reference,semalar}/**` | `{gorev}/CIKTI/**` | — |
   | `yazar` | `Read, Write, Edit, Glob, Grep` | `{gorev}/**` + `.claude/skills/film-yap/{reference,semalar}/**` + `PLAN_DILI.md` | `{gorev}/CIKTI/**` | — |
4. **Model:** hepsi `model: opus` + `effort: high` (H/ajan-opus-yuksek, kesin karar 6; Opus 5.5'te varsayılan efor `medium`, açıkça yazılır).
   `fallbackModel` ayarlanmaz.
5. **`memory:` alanı hiçbir ajanda yok.** Dersler yalnız GIRDI'de (İ-5).
6. **`permissionMode: acceptEdits`** bütün ajanlarda: yazma izni istemi çıkmaz (M13); nereye yazılabileceğini `erisim_kapisi` belirler.
7. **Çıktı sözleşmesi:** (a) `CIKTI/` altına önce başlıklar, sonra bölüm bölüm doldurma; (b) şemalı `.json`; (c) `.md`'nin son satırı sabit `OZET | …`;
   (d) ana Claude'a ≤ 5 satır: çıktı yolu + OZET. Puanı mesajdan değil dosyadan betik okur.
8. **Görev dışı bilgi yok:** devretme mesajı yalnız `"Görevin: <yol>/GOREV.json — önce onu oku, yalnız orada yazanı yap."`.
9. **Açıklama kalıbı:** "<Rol>. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler: …". Böylece Claude ajanı kendiliğinden seçmez.
10. **Yeni ajan ölçütü (Ç-10):** ancak (a) ayrı bir dosyanın tek sahibi ya da (b) ayrı kör girdili bağımsız değerlendirici ise. Değilse mevcut ajanın kipi.

#### 4.3.2 Tam kadro (21 ajan; içerik sahibi uzmanların tur 2 kararlarıyla)

**Yazarlar (10)** — sahip oldukları dosyayı yazar, revizyonu da onlar yapar. `maxTurns: 100` (tahmin).

| Ajan | Kipler | Görev sınırı | İçerik sahibi |
|---|---|---|---|
| `yapimci` | `konu`, `doktor` | Konu kartı, süre, eksenler, varsayımlar, "sen seç". Doktor kipinde yapısal teşhis ve şartlı KRİTİK reddi (İ-8). **Hikâye yazmaz** | senarist |
| `hikaye-mimari` | eksen D/S/E/X (seri devamında A/B/S/X) | Verilen eksende 10 başlıklı öneri. Diğer önerileri okumaz | senarist |
| `hikaye-yazari` | `yapi`, `senaryo`, `revizyon`, `dar_degisiklik`, `evren`, `replik_kabul` | Birleştirme, 3 × 8 yapı, senaryo, bütün revizyonlar, evren taslağı. **Replik metninin tek sahibi.** `replik_kabul` her seferinde yeni örnek ([SM2]) | senarist |
| `yonetmen` | `harita`, `plan`, `onarim`, `kart_secimi`, `ders` | Harita, sahne grubu planı (atomik eylem zinciri), onarım, kart seçimi. **İstem yazmaz, repliği değiştirmez** | yönetmen |
| `kart-tasarimcisi` | — | `KART_SPEC.json` ve evrendeki görsel tarif alanları; kimlik dizesi, varyantlar, asimetrik ayrıntılar | görüntü-süreklilik |
| `ses-tasarimcisi` | `kadro`, `tasarim`, `muzik` | Ses profilleri ve seçim gerekçesi; sahne grubu ses tasarımı; leitmotif ve ipucu listesi. **Sesi duyamaz; yolu kod önerir** | ses-müzik |
| `kurgucu` | `duzelt`, `kirp_incele`, `sifir_kredi`, `not` | Bulgu → kurgu işlem listesi; `KURGU_PLANI`'na dokunmaz, betik uygular; kullanıcı kararını geri almaz | kurgucu |
| `yayin-paketcisi` | — | Hikâye odasının başlık adaylarından seçim + YouTube paketi, bölümler (zamanlar `KURGU_PLANI`'ndan), etiketler, Shorts aralıkları, jenerik metni | yayın (senarist + kurgucu sözleşmesi) |
| `ders-editoru` | — | Ders kümelerinden aday kural; güvenlik kurallarını gevşetemez; kuralı betik uygular | üretim |
| `memmet-bakimci` | — | Yalnız `arayuz` kısıtında; **aday yama** yazar (İ-3) | üretim |

**Denetçiler (5)** — kör değil ama içerik üretmez; `maxTurns: 60` (tahmin).

| Ajan | Kipler | Görev sınırı | İçerik sahibi |
|---|---|---|---|
| `juri-uyesi` | `ilk_kez_izleyen`, `youtube_stratejisti`, `tur_uzmani`, `duygu_elestirmeni` | Anonim önerileri 10 ölçütle puanlar; A17'de kapak/başlık seçimi (strateji rolü) | senarist |
| `uretilebilirlik-denetcisi` | `juri`, `plan` | Çekilemez fikir, filtre riski, 2–3 adım 8 sn'ye sığar mı, el/parmak, ölçek. **Kredi hesabı yapmaz** | yönetmen + üretim |
| `sureklilik-denetcisi` | `kagit`, `hakem`, `kacis`, `ders` | Betiğin göremediği anlam hataları; hakem yalnız tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ alanını karara bağlar ([GS2] İ-3) | görüntü-süreklilik |
| `diyalog-editoru` | — | Bütün replikler sırayla: doğallık, dönem dili, ad tutarlılığı, telaffuz riski, filtre, TR altyazı önerisi | senarist |
| `hat-denetcisi` | — | Kredi kapısından önce betik kapılarının göremediğini arar; `GIT/GITME` | üretim |

**Kör değerlendiriciler (6)** — her turda yeni örnek; yalnız GIRDI; `omitClaudeMd: true`; `maxTurns: 60` (tahmin).

| Ajan | Kipler | Görev sınırı | İçerik sahibi |
|---|---|---|---|
| `habersiz-seyirci` | `kagit`, `plan`, `ilk2dk`, `animatik`, `kurgu` | İlk kez izleyen seyirci; 6 ölçüt + GENEL; kopukluk, sıkıldığım anlar, açık sorular, 3 cümle özet; aşamalı okuma | senarist (kâğıt/plan/ilk 2 dk) + kurgucu (izleme kipleri) |
| `ozet-eslestirici` | `ozet`, `bulgu` | Seyirci özeti ↔ `anahtar_olgular`; kopukluk ↔ kimlik eşleme. Puan vermez | senarist + kurgucu |
| `oyuncu` | karakter başına | Yalnız kendi karakterinin repliklerini kendi kartına göre okur | senarist |
| `kare-tarifcisi` | `kart`, `g1`, `v3`, `kapak` | Beklenen değeri görmeden iki aşamalı soru formuna cevap (≤ 12 görsel/görev, tahmin) | görüntü-süreklilik |
| `kesici` | `animatik`, `kurgu` | "Hangi 10 planı ya da 2 sahneyi atarsak film daha iyi olur?" | kurgucu |
| `plan-elestirmeni` | — | Parti başına çekim listesini görüntü dili ve kapsama açısından eleştirir; kurallar GIRDI'ye kopyalanır | yönetmen |

**Kalkan ya da birleşen adlar:** `istem-muhendisi` (→ `istem_derle.py` + `yonetmen·onarim` + `duzeltme.py`), `muzik-supervizoru` (→ `ses-tasarimcisi·muzik`),
`plan-yazari` (→ `yonetmen·plan`), `senarist` (→ `hikaye-yazari`), `konu-analisti` ve `hikaye-doktoru` (→ `yapimci`), `evren-arsivcisi` (→ `hikaye-yazari·evren`),
`anlama-olcer` (→ `ozet-eslestirici`), `kor-gozlemci` ve `vlm-denetci` (→ `kare-tarifcisi`), `kurgu-seyircisi` (→ `habersiz-seyirci` izleme kipleri),
`ses-kadrocusu` ve `ses-denetcisi` (→ `ses-tasarimcisi·kadro` + `ses_karar.py`), `ders-katibi` (→ `ders-editoru`).

**Ajan çağrısı bütçesi:** ≈ 350–550 görev/film (tahmin, [UM2] §4.3.6; en büyük kalem `kare-tarifcisi` ≈ 145–175). Kesin karar 6 gereği kısılmaz;
paralel tavan 5 ve kesilme dayanıklılığı bunun içindir.

#### 4.3.3 Mevcut 8 taslağın eksik ve yanlışları (son karar)

| Taslak | Sorun | Karar |
|---|---|---|
| **Hepsi** | `effort`, `maxTurns`, `permissionMode` yok; çıktı yolları sabit (görev klasörü yerine `_HIKAYE_ODASI/…`); JSON çıktı sözleşmesi yok; "önce başlıkları yaz" kuralı yok; eski YR aşama kodları; `FILMLE ILGILI CLAUDE/…` yolları Windows kurulumunda yok | Ortak gövde kalıbı (rol → kesin kurallar → "Çağrıldığında" adımları → kontrol listesi → çıktı sözleşmesi); bütün yollar `GOREV.json`'dan; kurallar GIRDI'ye kopyalanır |
| `habersiz-seyirci` | `Glob` var; 3 ölçüt + ORTALAMA; ilk 2 dk, açık sorular, zaman kodlu sıkılma, 3 cümle özet yok; CLAUDE.md okuyor | **Güncellenir:** `Read, Write`, `omitClaudeMd`, 5 kip, 6 ölçüt + GENEL, aşamalı okuma (§4.3.4) |
| `hikaye-mimari` | "Parti ≈ 80–100 klip" ZN §2.6 ile, "en çok 4 konuşan" RE `konusan_karakter_max: 8` ile çelişiyor; diğer önerileri okuyabilir; v2'yi mimar yazıyor | **Güncellenir:** 10 başlıklı öneri ([SN2] İ7); sayılar şablondan; v2 ve sonrası `hikaye-yazari` |
| `istem-muhendisi` | İstemleri elle yazıyor; `parti`'yi 20'lik blok sayıyor; dosya taşıyor | **Kaldırılır** |
| `muzik-supervizoru` | `sonnet`; sahne grubu yok; ambiyans/efekt/sessizlik/kaplama kuralları yok | **Kaldırılır** (→ `ses-tasarimcisi·muzik`) |
| `sureklilik-denetcisi` | `sonnet`; görsel kipte beklenen listeyi görerek karar veriyor; 405 kareyi tek ajana veriyor; `YENIDEN_URET.json`'u kendisi yazıyor | **Baştan yazılır:** 4 kip; kör döküm `kare-tarifcisi`'nde, karşılaştırma ve kuyruk betikte; hakem yetkisi kodla sınırlı |
| `uretilebilirlik-denetcisi` | Kredi tahmini "%25 pay" ve LLM hesabı; atomik zincir ve el/parmak sığma denetimi yok; `sonnet` | **Güncellenir:** `juri` ve `plan` kipleri; kredi `kredi.py`'de |
| `yayin-paketcisi` | Bölüm adı kuralı, Shorts ölçüleri yok; kapağı "kullanıcı seçer"; başlıkta "kill" yasağının kaynağı yok. (Tur 1'deki "`son_capcut_projesi.json` yok" itirazım **yanlıştı**: dosyayı `capcut_film.py` yazıyor.) | **Güncellenir:** seçer ve doğrular, başlık yazmaz ([SN2] İ11); zamanlar `KURGU_PLANI`'ndan; "kill" BAYRAK |
| `yonetmen` | Atomik eylem zinciri yok ("tek hareket"); yapılandırılmış alanlar yok; istem yazıyor; 495 planı tek çağrıda yazmaya kalkıyor | **Baştan yazılır:** 5 kip; sahne grubu başına görev; istem kodla |

#### 4.3.4 Örnek tanım: `habersiz-seyirci.md`
```markdown
---
name: habersiz-seyirci
description: Filmi hiç bilmeyen, ilk kez izleyen YouTube seyircisi. Yalnız film.py görev defteri bir GOREV.json yoluyla
  çağırdığında kullanılır; kipler kagit, plan, ilk2dk, animatik, kurgu. Her turda yeni örnek açılır.
tools: Read, Write
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
omitClaudeMd: true
color: cyan
---
Sen bu filmi İLK KEZ izleyen sıradan bir izleyicisin. Filmin planını, yazarların niyetini, yapım kurallarını ve önceki
turları bilmiyorsun. Yalnız GOREV.json'da adı geçen GIRDI dosyalarını okursun; başka bir dosyayı açmaya çalışma, sistem engeller.

Çağrıldığında:
1. GOREV.json'u oku (kip, bölüm listesi, çıktı yolları).
2. CIKTI/rapor_<bolum>.md dosyasını hemen başlıklarıyla oluştur; her bölümü bitirdikçe doldur.
3. GIRDI'deki bölümü baştan sona sırayla "izle". İleride ne olacağını tahmin etmeye çalışma; geriye dönüp düzeltme yapma.
4. Adını ekranda duymadığın karakteri adıyla anma; gördüğün gibi tarif et ("kürk yakalı kadın").
5. Puanla (1–10, cömert olma): anlasilirlik, akicilik, merak, duygu, ritim, ilk30, GENEL.
   Kopukluklar KRITIK/ORTA/KUCUK (plan numarası ya da zaman koduyla), sıkıldığın anlar, aklındaki açık sorular, 3 cümle özet.
6. Bölüm bitince durmak iste. Yeni bölüm varsa sistem sana yolunu söyler; söylerse onu oku ve aynı biçimde raporla.
7. Son bölümde CIKTI/rapor.json'u şemaya göre yaz. Her .md'nin son satırı:
   OZET | anlasilirlik: _ | akicilik: _ | merak: _ | duygu: _ | ritim: _ | ilk30: _ | GENEL: _ | KRITIK: _ | ORTA: _
8. Ana oturuma yalnız iki satır dön: CIKTI yolu ve OZET satırı.

## Kip: kagit · plan · ilk2dk   (gövde metni: senarist)
## Kip: animatik · kurgu        (gövde metni: kurgucu)
```

#### 4.3.5 Örnek tanım: `memmet-bakimci.md` (başlık ve kesin kurallar)
```markdown
---
name: memmet-bakimci
description: Flow arayüzü değiştiği için Memmet durduğunda değişen seçiciyi bulan bakımcı. Yalnız film.py görev defteri
  bir GOREV.json yoluyla çağırdığında kullanılır. Yalnız aday yama yazar; kaynak dosyalara dokunmaz.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
KESİN KURALLAR: Yalnız CIKTI/memmet_yama.diff, CIKTI/fikstur/*.html ve CIKTI/BAKIM.md yazarsın. Bekleme ve mola süresini
kısaltamazsın, uyarı ve doğrulama kelime listelerini daraltamazsın, yeniden deneme ekleyemezsin, fare/klavye taklidi ekleyemezsin,
reCAPTCHA'ya dokunamazsın. Yamayı korkuluk testleri sınar; geçmeyen yama uygulanmaz.
```

### 4.4 Beceri (skill) tarif adımları

#### 4.4.1 Kaç beceri, neden
**4 beceri.** Aşama başına beceri yok: kullanıcı yalnız konu verdiği için `/…` komutlarını kimse yazmaz; `disable-model-invocation: true` taşıyan beceriyi
Claude kendisi açamaz (D/skills); aşama ayrıntısı ana Claude'un değil ajanın işidir ve şablonlarda durur.

| Beceri | Kim açar | Rol | Neden ayrı |
|---|---|---|---|
| `film-yap` | Claude (otomatik) + `/film-yap` | Set amiri döngüsü | Ana iş |
| `film-durum` | Claude + `/film-durum` | Soru = yalnız cevap (H/soru-sadece-cevap) | `disallowed-tools` ile o sırada yazma araçları ve Agent kapalı (D/skills alanı var) |
| `film-not` | Claude + `/film-not` | Kullanıcı notu / CapCut düzenlemesi → görev | Kullanıcının kurgu kararı korunur (BK §5.3.3) |
| `film-gelistir` | yalnız `/film-gelistir` (`disable-model-invocation: true`) | Sistemi değiştirme (araç, ajan, kanca, test) | Film sırasında kod değişmesin; sürüşü kapatır, sürüşe bağlı yasakları kaldırır |

Sıkıştırmada her becerinin en son çağrısının ilk 5.000 tokeni geri eklenir, toplam bütçe 25.000 (D/skills) → 4 beceri sığar.

#### 4.4.2 Frontmatter metinleri

**`film-yap`** (description 574 kr; + `when_to_use` ≈ 910 kr ≤ 1.536)
```yaml
---
name: film-yap
description: >-
  Kullanıcı bir film konusu verdiğinde ya da süren bir filme devam edilmesi gerektiğinde YZ film setini yürütür:
  görev defterindeki sıradaki işi çalıştırır, uzman ajanlara dağıtır, kapılardan geçirir. Use when the user gives a
  movie topic or story idea, asks for a film ("film yap", "yeni film", "şu konuda bir film", "make a movie about"),
  says "devam", "devam et", "kaldığın yerden", "continue", reports that a requested physical step is done
  ("zipi koydum", "Flow'da gönderdim", "kredi yükledim"), or when the session context shows an active film with a
  runnable next task.
when_to_use: >-
  Örnekler: "Ejderha büyüten bir kadın hakkında film yap" · "konu: uzaylı çocuğa babalık eden asker" · "sen seç" ·
  "devam" · "sınır açıldı, devam et" · "Gemini zipini GELENLER'e koydum". Kullanıcı SORU soruyorsa (ne durumda, neden
  durdu, kaç kredi) film-durum; not, şikâyet ya da kendi CapCut düzenlemesi için film-not kullanılır.
argument-hint: "[film konusu | sen seç | devam]"
effort: high
allowed-tools: Bash(python .claude/bin/film.py *)
hooks:
  PreToolUse:
    - matcher: "Read|Glob|Grep|Write|Edit|NotebookEdit"
      hooks:
        - {type: command, command: "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/erisim_kapisi.py\"", timeout: 10, onFailure: block}
    - matcher: "Bash|PowerShell"
      hooks:
        - {type: command, command: "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/komut_kapisi.py\"", timeout: 10, onFailure: block}
    - matcher: "Agent"
      hooks:
        - {type: command, command: "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_kapisi.py\"", timeout: 10, onFailure: block}
---
```
(Becerideki kancalar ayar dosyasındaki kancaların **yedeğidir**, İ-2.)

**`film-durum`**
```yaml
---
name: film-durum
description: >-
  Film hakkında soru soran kullanıcıya yalnız cevap verir; dosya değiştirmez, ajan çalıştırmaz, üretim başlatmaz.
  Use when the user asks a question about the film or the system: "ne durumda", "hangi aşamadayız", "neden durdu",
  "kaç kredi lazım", "promptta ne yazıyor", "şu sahnede ne oluyor", "ne zaman biter", "what's the status", or any
  message that ends with a question mark and does not ask for a change.
when_to_use: >-
  Soru = yalnız cevap kuralı (kullanıcı kesin istedi). Cevaptan sonra en çok bir cümle öneri: "İstersen şunu yaparım".
  Kullanıcı bir değişiklik ya da devam isterse film-yap'a dönülür.
disallowed-tools: Write, Edit, NotebookEdit, Agent
allowed-tools: Bash(python .claude/bin/film.py ozet*), Bash(python .claude/bin/film.py goster*)
---
```
**`film-not`** (description tur 1 ile aynı; `when_to_use` düzeltildi)
```yaml
when_to_use: >-
  Kullanıcının kurgu kararı aynen uygulanır; kullanıcının taslağına yazılmaz, klonlanıp yamanır. Notlar işlendikten sonra
  film-yap döngüsüne dönülür.
```
**`film-gelistir`**: `disable-model-invocation: true`; "Film setinin kendisini (ARACLAR betikleri, sağlayıcılar, kancalar, ajan ve beceri dosyaları,
testler) değiştirmek için geliştirici kipi. Önce `film.py surus kapat --gelistirme`."

#### 4.4.3 `film-yap/SKILL.md` gövdesi
**Bütçe:** toplam ≤ 250 satır. **İlk ≈ 110 satır = çekirdek** (≤ 4.500 token, tahmin): sıkıştırmadan sonra geri gelen kısım.
```markdown
# FİLM YAP — set amiri döngüsü

## 0. Şu anki durum (beceri açılırken betik yazar)
!`python .claude/bin/film.py ozet --kisa || true`

## 1. Değişmez kurallar (kancalar da zorlar)
1. Kullanıcıya YALNIZ filmin konusu sorulur, yalnız şu cümleyle: "Filmin konusu ne olsun? Bir cümle yeter
   (ör. ejderha yavrusunu saklayan avcı kadın). İstersen 'sen seç' yaz." Diğer bütün kararları ekip verir:
   `film.py karar ekle "karar — neden — yanlışsa maliyeti"`. "Hangisini istersin / onaylıyor musun" YOK.
2. Kullanıcıdan yalnız onun yapabileceği FİZİKSEL iş istenir. Talimatı film.py verir; aynen ilet.
3. Flow "olağan dışı etkinlik" / doğrulama → hat durur. Yeniden başlatma, atlatma, tempo hızlandırma,
   fare/klavye taklidi YOK. Kilidi yalnız kullanıcı kaldırır.
4. AYARLAR hiçbir kökte okunmaz, yazdırılmaz. Ayar gerekiyorsa: `film.py goster ayar` (maskeli).
5. Sen içerik üretmezsin, puan vermezsin, ajan çıktısını düzeltmezsin, plan/rapor dosyası yazmazsın.
6. Ajan çağırırken: yalnız görevdeki `ajan` tipi; istem AYNEN; `name` verme; fork başlatma; yerleşik ajan kullanma.
7. Büyük dosya açma. Bilgi gerekiyorsa: `film.py goster <ne>`.
8. Hafızana değil film.py'ye güven: `film.py sonraki` ne diyorsa o doğrudur.
9. Kullanıcı soru sorarsa film-durum; not verirse film-not. Soruya işlemle cevap verme.
10. Kredi yalnız film.py'nin bütçe noktası geçince harcanır. memmet.py'yi ya da bir sağlayıcıyı doğrudan çağırma.
11. Kalıcı silme yok; robocopy /MIR yok; çıplak git push yok (`film.py esitle --gonder`).
12. Çıkış kodu 2, 4, 5, 6, 7 ya da 8 ise film.py'nin cümlesini söyle ve turu bitir. Soru ekleme.

## 2. Döngü
1. `python .claude/bin/film.py sonraki` → JSON.
2. `python .claude/bin/film.py basla <id,id,…>`. Reddederse (kanca nabzı yok): KURTARMA.md §Kanca; ajan çalıştırma.
3. tur=ajan → aynı paralel_grup'taki görevlerin HEPSİ İÇİN TEK MESAJDA Agent çağır (en çok 5):
   subagent_type=<ajan>, prompt=<istem> AYNEN. Sonucu bekle.
   `ornek: ayni_yazar` ise önce SendMessage(<ajan_id>); ajan kimliği yoksa yeni örnek (GIRDI'de geçmiş vardır).
   Aşamalı görevlerde bölüm geçişini sistem yapar; sen bir şey yapmazsın.
4. tur=betik → `python .claude/bin/film.py calis <id>`. 8 BEKLE dönerse: `film.py bekle <iş>`'i arka planda başlat ya da turu bitir.
5. tur=kullanici_eylemi → `mesaj`ı aynen ilet ve turu bitir.
6. tur=bekle/kisit/ortam/butce → nedeni bir cümleyle söyle, turu bitir.
7. tur=bitti → `film.py ozet --kullanici` çıktısını ilet.
8. Ajan sonucu ya da tamamlanma bildirimi geldiğinde doğrulama yapma (kanca yaptı) → 1'e dön.
   Doğrulama "gecersiz" dediyse film.py yeni deneme görevini verir; sen düzeltme yazma.

## 3. Kullanıcıyla konuşma
Türkçe, kısa, teknik terim yok (gerekirse bir cümleyle açıkla). Her ilerlemede en çok 3 satır:
ne bitti · şimdi ne oluyor · senden bir şey gerekiyor mu (yalnız fiziksel iş).

## 4. Takılırsan
- film.py `takildi` derse KURTARMA.md'yi oku ve yazanı uygula.
- Bir kanca işlemi engellediyse: gerekçeyi oku, kuralı çiğneme; `film.py sonraki`.
- Kullanım sınırı / kesilme: hiçbir şey yapma; yeniden açılınca döngü kaldığı yerden sürer.
--- (çekirdek sonu) ---

## 5. Referanslar (yalnız film.py `oku` alanında gösterirse ya da takılınca)
KURTARMA.md · GOREV_SEMASI.md · KULLANICI_DILI.md · reference/hat.md (aşama listesi, kısıt ve bütçe dili)
```

#### 4.4.4 Diğer becerilerin adımları
**`film-durum`** (≤ 60 satır)
1. `` !`python .claude/bin/film.py surus kapat --soru || true` `` — otomatik sürüşü yalnız bu tur kapatır (Stop kancası sürmeye zorlamaz).
2. Soruya göre: `film.py ozet --uzun` · `goster plan 042` · `goster maliyet` · `goster neden-durdu` · `goster ayar` (maskeli).
3. Cevap: düz Türkçe, ≤ 6 satır, sayı varsa kaynağıyla. Son satır en çok bir öneri. İşlem yok.

**`film-not`** (≤ 120 satır)
1. `film.py notlar oku` → `notlari_oku.py` + `taslak_fark.py` salt okunur.
2. Her not sınıflanır: (a) kullanıcının kendi kurgu kararı → **aynen** ve kilitli `KURGU_PLANI`'na; (b) şikâyet → hangi kapı yakalamalıydı
   (`film.py ders ekle --kapi … --belirti "…"`); (c) yeni sahne isteği → içerik `hikaye-yazari`, plan `yonetmen` ([SN2] İ1).
3. `film.py karar ekle "Kullanıcı notu N: … — uygulanacak"`; `film.py notlar isle` → `kurgucu·not` görevi.
4. Kullanıcıya: "Notlarını aldım: N düzeltme. Bitince CapCut'ta listenin en üstünde yeni adla göreceksin; senin taslağına dokunmadım." (soru yok)
5. Kesme sonrası Z1 kurulum denetimi yeniden çalışır.

**`film-gelistir`** (≤ 150 satır): `film.py surus kapat --gelistirme` → `YZ_FILM/ARACLAR/CLAUDE.md`'yi oku → değişiklik →
`python -m unittest discover -s YZ_FILM/ARACLAR/testler` → `film.py beceri-denetim` → küçük commit. Anahtar dosyalarına dokunma.

#### 4.4.5 Beceri klasörü düzeni
```
.claude/skills/film-yap/
  SKILL.md                  ≤ 250 satır (çekirdek ilk ≈ 110 satır)
  KURTARMA.md               kanca nabzı yok, kilit bayat, DUR, kesik indirme, esitle çakışması, GPU kilidi ([UM2] ekleriyle)
  GOREV_SEMASI.md           GOREV.json alanları ve durumlar (§4.5.2)
  KULLANICI_DILI.md         çıkış koduna göre sabit Türkçe cümleler, .bat adları, kavram sözlüğü
  reference/                alan sahiplerinin açıklama dosyaları (≤ 300 satır, 100 satırı aşanın başında içindekiler; KURAL TAŞIMAZ)
    hat.md (ASAMALAR film.py ile üretilir, KISITLAR, BUTCE)  hikaye_odasi.md  yonetmen.md  goruntu_sureklilik.md  ses.md  kurgu.md
  PLAN_DILI.md              yönetmen ve plan eleştirmeni kılavuzu (plan eleştirmenine GIRDI kopyası olarak verilir)
  sablonlar/<ASAMA>_<ajan>[_<kip>].md   ajan istem şablonları; sayılar eşik dosyalarından yer tutucuyla basılır
  semalar/*.json            çıktı şemaları (seyirci_rapor_v2, juri_v1, plan_v2 …)
  BILGI_KURALLARI.md · ZANAAT.md · ritim_esikleri.json   (ajan şablonları gereken dilimi GIRDI'ye koyar; ana Claude okumaz)
  arastirma/ · tartisma/    tasarım belgeleri; üretimde hiçbir rol okuyamaz
```
`film-durum/`, `film-not/`, `film-gelistir/` yalnız kendi `SKILL.md`'lerini taşır; referansları `film-yap/`'tan tek seviye bağlar.

#### 4.4.6 Kural yerleşim tablosu (İ-6)

| Kural türü | Nerede | Örnek |
|---|---|---|
| Makinede ölçülür ya da engellenir | kanca / betik | AYARLAR okunmaz; fork yok; Flow kilidi; yasak sonuç fiili HATA; ileri bölüm okunmaz |
| Ajanın davranışı | ajan gövdesinin ilk satırları | "YZ'ye sonuç söylenmez" (yönetmen); "Sesi duyamazsın" (ses-tasarımcısı); "adını duymadığın karakteri adıyla anma" (seyirci) |
| Ana Claude'un davranışı | SKILL.md çekirdeği | 12 değişmez kural, döngü |
| Açıklama, gerekçe, örnek | `reference/*.md`, `PLAN_DILI.md` | sözlükler, örnek planlar, eşiklerin anlamı |
| Sayılar | eşik dosyaları (`esikler.py` yükler) | şablonlara yer tutucuyla basılır; ajana sabit sayı yazılmaz |

#### 4.4.7 Kök `CLAUDE.md` akışı (depo kökü; ≤ 45 satır)
Mevcut kök CLAUDE.md'nin "İlk iş: PAKET.zip'i aç" satırı **bayattır** (zip e962e6a'da açılıp silindi). Geliştirme listesi `YZ_FILM/ARACLAR/CLAUDE.md`'ye taşınır
(alt klasör CLAUDE.md'si yalnız o klasörde çalışırken yüklenir).
```markdown
# YZ FİLM SETİ
Bu klasör bir YZ film setidir. Kullanıcı Türkçe konuşur, teknik bilgisi azdır.

## Açılışta
Oturum başında "FİLM SETİ DURUMU" bağlamı gelir (kanca). Gelmediyse: `python .claude/bin/film.py ozet`.
- Aktif film YOK ve kullanıcı konu vermediyse YALNIZ şunu sor: "Filmin konusu ne olsun? Bir cümle yeter
  (ör. ejderha yavrusunu saklayan avcı kadın). İstersen 'sen seç' yaz."
- Kullanıcı konu verdiyse ya da aktif film VARSA: soru sormadan film-yap becerisiyle devam et.

## Her zaman
- Kullanıcıya yalnız konu sorulur; diğer kararları ekip verir.
- Kullanıcı soru sorarsa yalnız cevap ver (film-durum). Not verirse film-not.
- Flow "olağan dışı etkinlik" ya da doğrulama → dur, haber ver. Atlatma, fare/klavye taklidi yok.
- AYARLAR gizli: okuma, yazdırma, kopyalama yok. Kalıcı silme yok. robocopy /MIR yok.
- Durum hafızada değil: `film.py` ve dosyalar doğrudur.

## Sistemi değiştirmek
Yalnız kullanıcı /film-gelistir derse ya da bu bir geliştirme oturumuysa. Ayrıntı: YZ_FILM/ARACLAR/CLAUDE.md
```
**Veri kökü yönlendirmesi** (`C:\Users\Soysal\Desktop\YZ_FILM\CLAUDE.md`, 5 satır; kullanıcı alışkanlıkla Claude'u burada açarsa):
"Bu klasör film setinin VERİ klasörüdür; set burada çalışmaz. Kullanıcıya yalnız şunu söyle: 'Masaüstündeki FILM_SETI.bat'a çift tıkla; Claude doğru
klasörde açılır.' Başka bir şey yapma." (`.claude/` burada olmadığı için ne beceri ne kanca yüklenir; bu dosya yanlış klasörde iş yapılmasını önler.)

#### 4.4.8 Değerlendirme senaryoları (AR3 B4)
1. "film yap" (aktif film yok) → yalnız konu sorusu; başka cümle yok.
2. "Ejderha büyüten bir kadın hakkında film yap" → soru yok; `yeni --konu`; A01 görevi.
3. "devam" (bağlam boş, A07b'de 3 sahne grubu bitmiş, 2 `calisiyor` kesik) → yalnız kesikler ve kalanlar; bitenler yeniden yapılmaz.
4. Kancalar kapalıyken "devam" → `basla` reddeder; ajan açılmaz; düz Türkçe yönlendirme.
5. Ana Claude bir seyirci görevini `general-purpose` ile açmaya çalışır → `ajan_kapisi` reddeder.
6. "kaç kredi lazım?" → film-durum; dosya değişmez, ajan açılmaz.
7. Geliştirme oturumunda (sürüş kapalı) `git push` ve `Explore` → engellenmez (M15).

### 4.5 Veri şeması (Claude Code tarafı; JSON örnekleriyle)
Plan içeriği alanlarının (`zanaat`, `_derlenir`, `zanaat.ses`, `uretim`) sahibi yönetmen, senarist, ses ve üretim uzmanlarıdır. Aşağıdakiler görev
defterinin, kancaların ve beceri katmanının dosyalarıdır. Örneklerdeki sayılar **örnektir**, ölçüm değildir.

#### 4.5.1 İki kök ve klasör düzeni
```
<depo_kok>   Windows önerisi C:\Users\Soysal\Desktop\YZ_FILM_SET  ·  bulutta depo kökü     ← Claude Code BURADA açılır
  CLAUDE.md                               §4.4.7
  .claude/settings.json                   paylaşılan: kancalar, env, statik deny (§4.6)
  .claude/settings.local.json             makineye özel; kurulum.py yazar; git dışı (additionalDirectories, derinlik, paralel tavan)
  .claude/bin/film.py                     sarmalayıcı: veri kökünü YOLLAR.json'dan bulur, ARACLAR/film.py'yi çalıştırır
  .claude/hooks/*.py                      11 kanca betiği (yalnız standart kütüphane)
  .claude/kurallar/erisim.json            rol politikası (§4.5.7)
  .claude/agents/*.md                     21 ajan
  .claude/skills/{film-yap,film-durum,film-not,film-gelistir}/
  YZ_FILM/ARACLAR/                        kod (+ CLAUDE.md: geliştirici notları)
<veri_kok>   Windows C:\Users\Soysal\Desktop\YZ_FILM (yerinde kalır)  ·  bulutta <depo_kok>/YZ_FILM
  CLAUDE.md                               yalnız Windows: "set burada değil, FILM_SETI.bat" yönlendirmesi
  AYARLAR/                                gizli (FILM_AYAR.json, YOLLAR.json, anahtarlar; *.ornek.json ve OKU_BENI.txt açık)
  EVREN/<SERI>/                           seri kütüphanesi (yalnız evren.py yazar)
  BILGI/DERSLER/ham/*.json · DERSLER_AKTIF.md (türetilir)
  FLOW_YUK.jsonl · FLOW_TEMPO.json · HESAP_DURUMU.json      ([UM2], hesap düzeyi)
  FILMLER/_AKTIF.json
  FILMLER/<id>/
    00_KONU.md · FILM_DURUM.json (önbellek) · 00_DURUM.md · FILM_KAYIT.txt · FILM.kilit · DUR
    kararlar/<zaman>_<kaynak>.json · KARAR_DEFTERI.md (türetilir)
    _GOREV/DEFTER.jsonl (olay günlüğü) · _GOREV/KANCA_NABZI.json · _GOREV/BAGLAR.json (agent_id ↔ görev)
    _GOREV/G0041/{GOREV.json, ISTEM.md, GIRDI/, CIKTI/}
    _HIKAYE_ODASI/ · _YONETMEN/ · _SES/ · _RAPOR/ · KUYRUK/          (yazar çıktıları betikle taşınır; raporlar ve kuyruklar betiğin)
    SAHNELER.json · DUNYA_DEFTERI.json                                (yalnız betik)
    01_KARAKTERLER/ SIRALI_GORSEL/ SIRALI_VIDEO/ SESLER/ KURGU/ YAYIN/ GELENLER/ KUNYE/ _ESKI/   (mevcut adlar)
```
- `settings.local.json` örneği (kurulum yazar; D/settings: izlenmeyen yerel dosyanın `allow` kuralları güven adımı beklemez; Windows'ta dosya
  `.claude/settings.json`'un yanında kalır):
  `{"permissions": {"additionalDirectories": ["C:\\Users\\Soysal\\Desktop\\YZ_FILM"]}, "env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1",
  "CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS": "5"}}`. Bulutta yerel dosya okunmaz (D/settings); orada iki kök aynı klasördür, sınırları `ajan_kapisi` zorlar.
- `.gitignore`: `YZ_FILM/FILMLER/*/_GOREV/`, `FILM_DURUM.json`, `FILM.kilit`, `DUR`, medya klasörleri, `AYARLAR/*` (örnekler hariç). Böylece alt ajana
  giden git durumu özetinde (D/agents "Git status: a snapshot") görev ve öneri dosya adları görünmez.

#### 4.5.2 `GOREV.json` v2 (görev sözleşmesi)
```json
{
  "id": "G0041", "film": "F20261023_ejderha", "asama": "A06", "tur_no": 2, "parti": null,
  "tur": "ajan", "ajan": "habersiz-seyirci", "kip": "kagit", "rol": "kor",
  "ornek": "yeni", "paralel_grup": "A06_t2_seyirci", "ortam": "her_ikisi", "kredili": false,
  "istem": "Görevin: FILMLER/F20261023_ejderha/_GOREV/G0041/GOREV.json — önce onu oku, yalnız orada yazanı yap.",
  "talimat": "ISTEM.md", "sablon": "sablonlar/A06_habersiz-seyirci_kagit.md", "sablon_sha": "3be1…",
  "girdi": ["GIRDI/P0.md", "GIRDI/SORULAR.md"],
  "asamali": {"bolumler": ["P0", "P1", "P2", "P3"], "siradaki": 1,
              "kaynak": "_HIKAYE_ODASI/_SEYIRCI_PAKETI/t2/", "duzeltme": {"P0": 0}},
  "cikti": {"rapor": "CIKTI/rapor_{bolum}.md", "veri": "CIKTI/rapor.json"},
  "gecme_sarti": {"dosyalar_var": true, "sema": "seyirci_rapor_v2", "son_satir": "^OZET \\|", "duzeltme_max": 2},
  "tasima": [{"kaynak": "CIKTI/rapor.json", "hedef": "_HIKAYE_ODASI/seyirci/t2_s1.json"}],
  "bagimlilik": ["G0038"], "deneme": 1, "en_cok_deneme": 3,
  "girdi_imza": "9f1c0a2b7e44d310", "kanca_gerek": true,
  "durum": "hazir", "ajan_id": null, "basladi": null, "bitti": null,
  "yarim_davranisi": "sifirdan", "cikis_kodu": 3
}
```
- `durum`: `hazir | calisiyor | bitti | gecersiz | kesildi | iptal | model_sapmasi`. Durumun kaynağı bu dosyadır (atomik yazım: `x.tmp` → `os.replace`).
- `asamali` yalnız seyirci kiplerinde; bekleyen bölümler görev klasörünün **dışında** durur, kör rol göremez.
- `yarim_davranisi`: değerlendiricide `sifirdan`, yazarda `devam_et`.
- `kanca_gerek: false` yalnız başsız yürütmede (`yurut --basliksiz`).
- `ornek: ayni_yazar` + `onceki_ajan_id`: revizyonda aynı örneği sürdürmek için.

#### 4.5.3 `film.py sonraki` çıktısı (ana Claude'un tek okuduğu şey; ≤ 1.200 kr hedef, tahmin)
```json
{"film": "F20261023_ejderha", "asama": "A06 Kâğıt seyirci", "tur_no": 2, "cikis_kodu": 3,
 "gorevler": [
   {"id": "G0041", "tur": "ajan", "ajan": "habersiz-seyirci", "paralel_grup": "A06_t2_seyirci", "istem": "Görevin: …/G0041/GOREV.json — …"},
   {"id": "G0042", "tur": "ajan", "ajan": "habersiz-seyirci", "paralel_grup": "A06_t2_seyirci", "istem": "…"},
   {"id": "G0043", "tur": "ajan", "ajan": "habersiz-seyirci", "paralel_grup": "A06_t2_seyirci", "istem": "…"}],
 "kullaniciya": null, "oku": null}
```
Kullanıcı eylemi örneği: `{"id": "G0310", "tur": "kullanici_eylemi", "cikis_kodu": 2, "mesaj": "1) Masaüstü\\GEMINI GORSEL ISTEM\\F20261023_P1_1
klasörünü Gemini'ye ver.\n2) Gelen ZIP'i FILMLER\\F20261023_ejderha\\GELENLER içine koy.\nBen ZIP'i görünce kendim devam ederim.",
"algilama": {"tur": "dosya_var", "desen": "GELENLER/*P1_1*.zip"}}`.
Çıkış kodları [UM2] tablosudur: `0 BİTTİ · 1 HATA · 2 KULLANICI · 3 AJAN · 4 ORTAM · 5 BÜTÇE · 6 KAPI · 7 KISIT · 8 BEKLE`. `film.py ozet` her
durumda 0 döner; beceri içindeki `!` komutu ayrıca `|| true` taşır (D/skills: başarısız `!` komutu bütün beceri çağrısını iptal eder).

#### 4.5.4 `FILM_DURUM.json`'a eklediğim alanlar ([UM2] çekirdeği önbellektir; asıl kanıt zarflardır)
```json
{"otomatik_surus": true, "surus_kaynagi": "film-yap", "surus_kapali_neden": null,
 "donguler": {"A06": {"tur": 2, "tavan": 4, "medyanlar": [{"tur": 1, "GENEL": 6.5, "KRITIK": 2}], "yazar_ajan_id": "a1b2…"}},
 "bekleyen_kullanici": ["G0310"],
 "sayaclar": {"kullaniciya_soru": 1, "kanca_engeli": 0, "nabiz_reddi": 0, "ajan_kapisi_reddi": 0, "ajan_cagrisi": 57, "sema_duzeltme": 4},
 "model_sapmasi": []}
```

#### 4.5.5 Karar kaydı (olay başına dosya; `KARAR_DEFTERI.md` türetilir)
`kararlar/20261023-140511_A04_juri-topla.json`:
`{"zaman": "2026-10-23T14:05:11+03:00", "asama": "A04", "karar": "Öneri B kazandı (medyan 8,1 > A 7,4)", "neden": "jüri 4/5 B'yi ilk sıraya koydu",
"yanlissa_maliyeti": "A06'da 1–2 ek tur", "kaynak": ["G0019", "G0023"], "karar_veren": "betik:puan_oku", "tur": "karar"}`.
`tur` değerleri: `karar`, `soru` (kullanıcıya sorulan; M1), `bilgi` (kullanıcıya verilen), `kullanici_notu`, `red` (KRİTİK reddi, İ-8), `yama` (memmet).

#### 4.5.6 Ders kaydı (biçim [UM2] §4.5.11; benim eklediğim iki alan)
- `rol_etiketi: ["yonetmen"]`: `DERSLER_AKTIF.md` türetilirken satır bu rolün görevlerinin `GIRDI/DERSLER.md`'sine girer; kör rollere hiç girmez.
- `kaynak_gorev: "G0412"`: dersin hangi görevden doğduğu; terfi kararında kanıt zinciri buradan izlenir.

#### 4.5.7 Erişim politikası `.claude/kurallar/erisim.json` v2
```json
{
  "gizli": ["{veri_kok}/AYARLAR/**", "{depo_kok}/YZ_FILM/AYARLAR/**", "**/.env", "**/memmet_profil/**"],
  "gizli_istisna": ["**/AYARLAR/*.ornek.json", "**/AYARLAR/OKU_BENI.txt"],
  "makine_sahipli": ["**/FILM_DURUM.json", "**/_GOREV/DEFTER.jsonl", "**/_GOREV/BAGLAR.json", "**/_GOREV/KANCA_NABZI.json",
                     "**/_GOREV/*/GOREV.json", "**/_GOREV/*/GIRDI/**", "**/SAHNELER.json", "**/DUNYA_DEFTERI.json", "**/_RAPOR/**",
                     "**/KUYRUK/**", "**/kararlar/**", "**/KARAR_DEFTERI.md", "**/EVREN/**", "**/BILGI/DERSLER/**",
                     "**/KURGU/KURGU_PLANI*.json", "**/.claude/**", "**/YZ_FILM/ARACLAR/**"],
  "yasak_okuma_film_rolleri": ["**/.claude/skills/film-yap/tartisma/**", "**/.claude/skills/film-yap/arastirma/**"],
  "roller": {
    "kor":     {"ajanlar": ["habersiz-seyirci", "ozet-eslestirici", "oyuncu", "kare-tarifcisi", "kesici", "plan-elestirmeni"],
                "okuma": ["{gorev}/GOREV.json", "{gorev}/ISTEM.md", "{gorev}/GIRDI/**", "{gorev}/CIKTI/**"], "yazma": ["{gorev}/CIKTI/**"]},
    "denetci": {"ajanlar": ["juri-uyesi", "uretilebilirlik-denetcisi", "sureklilik-denetcisi", "diyalog-editoru", "hat-denetcisi"],
                "okuma": ["{gorev}/**", "{depo_kok}/.claude/skills/film-yap/reference/**", "{depo_kok}/.claude/skills/film-yap/semalar/**"],
                "yazma": ["{gorev}/CIKTI/**"]},
    "yazar":   {"ajanlar": ["yapimci", "hikaye-mimari", "hikaye-yazari", "yonetmen", "kart-tasarimcisi", "ses-tasarimcisi",
                            "kurgucu", "yayin-paketcisi", "ders-editoru", "memmet-bakimci"],
                "okuma": ["{gorev}/**", "{depo_kok}/.claude/skills/film-yap/reference/**", "{depo_kok}/.claude/skills/film-yap/semalar/**",
                          "{depo_kok}/.claude/skills/film-yap/PLAN_DILI.md"],
                "yazma": ["{gorev}/CIKTI/**"]}
  },
  "ana_claude": {"okuma_buyuk_dosya_kb": 200, "yazma_yasak": "makine_sahipli", "surus_disinda": "gelistirme_serbest"},
  "tanimsiz_agent_type": "ret"
}
```
- `{gorev}` = kancanın `agent_id` ile bağladığı görev klasörü. **Bağlama:** `film.py basla` görevi `calisiyor` yapar; `ajan_kapisi` Agent çağrısının
  istemindeki görev yolunu ve `subagent_type`'ı `BAGLAR.json`'a "bekleyen" olarak yazar; ajanın ilk araç çağrısı (GOREV.json'u okuma) `agent_id`'yi
  o göreve bağlar; bağlanmış göreve ikinci bir `agent_id` erişemez. `agent_id` ve `agent_type` alanları alt ajan içindeki araç olaylarında gelir (D/hooks).
- Yollar karşılaştırılmadan önce normalleştirilir: büyük/küçük harf duyarsız (Windows), `\` → `/`, sembolik bağ çözümü, `..` reddi.
- `tanimsiz_agent_type: ret`: SubagentStop ve araç olaylarında kadro dışı ajan (Claude Code'un iç ajanları dahil, D/hooks "internal agents")
  film dosyalarına erişemez; `ajan_bitti` bağsız `agent_id`'yi yok sayar.
- `yasak_okuma_film_rolleri` yalnız film görevlerindeki ajanlara uygulanır; geliştirme oturumu bu klasörleri okuyabilir.
- `surus_disinda: gelistirme_serbest`: film sürüşü kapalıyken ana Claude'un `.claude/` ve `ARACLAR/` yazması serbesttir (geliştirme oturumu, M15).
  Gizli dosya kuralı her durumda geçerlidir.

#### 4.5.8 `KANCA_NABZI.json` (İ-2)
```json
{"zaman": "2026-10-23T14:06:02+03:00", "session_id": "…", "yazan": "komut_kapisi",
 "kanca_sha": {"erisim_kapisi.py": "a1…", "komut_kapisi.py": "b2…", "ajan_kapisi.py": "c3…", "ajan_bitti.py": "d4…", "erisim.json": "e5…"},
 "ayar_sha": {"settings.json": "f6…"}, "kaynak": "ayar|beceri"}
```
`film.py basla` şartları: `zaman` ≤ 15 sn önce (tahmin); sha'lar depodaki dosyalarla aynı; `settings.json` sha'sı beklenen (fork kapatma değişkeni
içinde). Şart tutmazsa görev başlamaz; `sayaclar.nabiz_reddi` artar.

#### 4.5.9 Kör paket alanları (`kor_paket.py`, beyaz liste; kipler alan sahiplerinin)

| Verilir | Verilmez (sızıntı) |
|---|---|
| Zaman kodu, sahne/plan sırası; plan numarası (izleme kipleri, [KU2]) | `amac`, `duygu`, `hedef_duygu`, `yogunluk`, `vurus`, `risk`, `merak_ac/kapat`, `kurulum`, `kullanim_bilgi`, `ironi`, `sahne_degeri` |
| Kâğıt ve plan kiplerinde kadraj düz sözle; atomik eylem zincirinin **görünür** adımları | İzleme kiplerinde kadraj etiketi, plan tipi, kurulum, kesme tipi ([KU2] İ-7) |
| Replik metni; ekranda konuşan görünüyorsa görünüş tarifiyle, ekran dışıysa ölçüme bağlı `ses_etiketi_tr` ([SM2] İ-9) | Konuşanın adı (ad ekranda söylenene kadar); `ekranda_bilgi`, `seyirci_ogrenir` (yalnız eşleştiricinin anahtarı) |
| Ekran yazısı, yer/zaman kartı; duyulan ses ipucu; kurgu kipinde "duyulan" satırı son miksten (ASR anlamadıysa "(anlaşılmayan konuşma)") | `gorsel_istem`/`hareket_istem` ham metni, yönetmen notları, önceki tur raporları, puan geçmişi, K1 kopukluk adayları ([KU2] D7) |
| İzleme kiplerinde kareler; ilk 2 dk kipinde başlık + kapak imgesi tarifi | `IZLEYICI_OZETI.md` (kapı seyircisine; yalnız isteğe bağlı 4. "dönen seyirci" alır, medyana girmez — [SN2] İ2) |

- **Ad maskeleme:** karakter adı ve hitapları (`takma_adlar`, "Captain", "brother") ekranda ilk kez sözle söylenene ya da yazıyla gösterilene kadar
  görünüş tarifiyle değiştirilir; tek maskeleme kodu bütün kiplerde ortaktır ([SN2], [KU2]).
- **Kör soru formu** (`kare-tarifcisi`): [GS2] İ-4 biçimi: önce serbest envanter (`p1`, `p2` kimlikleri, görüntü koordinatında eller), sonra bu kimliklerle
  hedefli sorular; soruda ad, kostüm, rol, beklenen konum yok; kritik sorular karışık sırayla iki kez; anatomik sol/sağ çevirisini kod yapar.

#### 4.5.10 Oturum başı bağlamı ve soru kapısı beyaz listesi
`oturum_basi.py` çıktısı (hedef ≤ 6.000 kr, sınır 10.000 kr; aşarsa kendisi kısaltır):
```json
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
"[FİLM SETİ DURUMU · 23.10.2026 14:05]\nAktif film: F20261023_ejderha (seri EMBERFALL)\nAşama: A07b Plan yazımı · 6/17 sahne grubu · çalışan görev 2 (arka planda olabilir)\nSıradaki: `python .claude/bin/film.py sonraki`\nBekleyen kullanıcı işi: yok · Flow kilidi: yok · BEKLE bitişi: — · Bugün Flow görsel: 0/20 · Bütçe: B1 GEÇ\nKanca nabzı: son 14:04 (geçerli)\nSon 3 karar: …\nKURALLAR: (SKILL.md §1'in 12 maddesi, kısaltılmış)\nDöngü: film-yap becerisi. Hafızana değil film.py'ye güven."}}
```
Aktif film yoksa tek cümle: *"Aktif film yok. Konu verildiyse film-yap ile başla; verilmediyse YALNIZ şunu sor: 'Filmin konusu ne olsun? Bir cümle yeter
(ör. ejderha yavrusunu saklayan avcı kadın). İstersen 'sen seç' yaz.'"*

**`soru_kapisi` beyaz listesi** (bunların dışındaki karar sorusu sürüş açıkken engellenir): (1) A00 konu sorusu, aynen; (2) film-durum turundaki
"İstersen …" öneri cümlesi (sürüş o tur kapalı); (3) `KULLANICI_DILI.md`'deki bilgi kalıpları ("gece modu için GECE_IZNI.bat" gibi seçenek bilgisi, İ-9).
Yakalanan kalıplar (TR/EN): "hangisini", "onaylıyor musun", "ister misin", "… mı … mı?", "devam edeyim mi", "which one", "should I", "do you want".

### 4.6 Yazılması / değişmesi gereken kod
Öncelik: **P0** = tasarımın çalışması için şart, bulutta sahte testle yazılabilir · **P1** = ilk gerçek filmden önce · **P2** = iyileştirme.
Bütün kanca betikleri yalnız standart kütüphane kullanır, Python 3.10 uyumludur ve ≤ 2 sn'de biter (tahmin hedef).

| # | Araç | Ne yapar | Öncelik |
|---|---|---|---|
| K-1 | `.claude/bin/film.py` | Sarmalayıcı: `YOLLAR.json`'dan veri kökünü, `YZ_FILM_KOK` ortam değişkeninden ya da `./YZ_FILM/ARACLAR`'dan kodu bulur; iki düzende aynı komut metni. `ozet` hiçbir durumda sıfır dışı kodla çıkmaz | P0 |
| K-2 | `film.py` görev komutları (ortak, [UM2] kodlar) | `sonraki`, `basla` (nabız denetimi), `bitir`, `kurtar [--yeniden-kur]`, `asama-ilerlet`, `bekle`, `karar ekle`, `ders ekle`, `goster <plan/maliyet/zaman/neden-durdu/ayar>`, `surus ac/kapat [--soru/--gelistirme]`, `notlar oku/isle`, `beceri-denetim`. `onay()`'daki `input()` kalkar (Bash aracında stdin yok → EOF) | P0 |
| K-3 | `.claude/hooks/erisim_kapisi.py` | PreToolUse `Read\|Glob\|Grep\|Write\|Edit\|NotebookEdit`; `onFailure: block`. Gizli dosya: herkese ret (iki kök). Makine sahipli: yazma reddi. Alt ajan: rolüne göre yalnız bağlı görev klasörü; ilk okumada bağlama. Ana Claude: 200 KB üstü Read ret + "`film.py goster`". Her ret `FILM_KAYIT`'a | P0 |
| K-4 | `.claude/hooks/komut_kapisi.py` | PreToolUse `Bash\|PowerShell` (Windows'ta PowerShell aracı da var, D/agents); `onFailure: block`. Her zaman ret: gizli dosyayı okuyan/kopyalayan komut, `robocopy … /MIR`, kalıcı silme (`_gecici/` hariç), `pyautogui\|pynput\|SendKeys`. **Sürüş açıkken** ret: `memmet.py`'nin `--giris`/`--bakiye` dışı doğrudan çağrısı, Flow kilidi varken video/görsel gönderimi ([UM2] İ-8 şartları), çıplak `git push` ve `git add -A`, makine sahipli dosyaya `python -c`/yönlendirmeyle yazma (sezgisel). `film.py basla` görünce **kanca nabzı** yazar | P0 |
| K-5 | `.claude/hooks/ajan_kapisi.py` (yeni) | PreToolUse `Agent`; `onFailure: block`. Sürüş açıkken: yalnız kadrodaki 21 ad; `fork`, `general-purpose`, `Explore`, `Plan` ve tanınmayan ad ret; istemdeki görev `calisiyor` değilse ya da ajan adı uyuşmazsa ret; `name`/`isolation` parametresi ret; çalışan film görevi ≥ 5 ise ret. Sürüş kapalıyken serbest | P0 |
| K-6 | `.claude/hooks/oturum_basi.py` | SessionStart `startup\|resume\|clear\|compact` → §4.5.10 | P0 |
| K-7 | `.claude/hooks/ajan_bitti.py` | SubagentStop: bağlı görevin CIKTI'sini `gecme_sarti`na göre doğrular; eksikse `decision: block` + eksik listesi (≤ 2/bölüm); aşamalı görevde sonraki bölümü verir ve `block` + "devam" talimatı (İ-4); yazar görevinde alan denetimini koşar (kroki, `plan_denetim --sahne`, `kurgu_uygula --kuru`); geçerse `film.py bitir`. Bağsız `agent_id`'yi (iç ajanlar) yok sayar | P0 |
| K-8 | `.claude/hooks/ajan_sonrasi.py` | PostToolUse `Agent`: görev durumunu okur; `bitti` → "sıradaki: …"; `calisiyor` → "arka planda; bildirim gelince `sonraki`". Dönüş metni 600 kr'yi aşarsa uyarı | P1 |
| K-9 | `.claude/hooks/ajan_basi.py` | SubagentStart: yalnız 2 sabit satır (İ-5); kör ve yazar ayrımı yok | P1 |
| K-10 | `.claude/hooks/stop_kapisi.py` | Stop: (a) **soru kapısı**: sürüş açıkken son mesajda beyaz liste dışı karar sorusu → `block` "Ekip karar verir; `film.py karar ekle` ve devam et"; (b) **devam kapısı**: çalıştırılabilir görev varsa ve `background_tasks` boş, `calisiyor` görev yoksa → `block` "Sıradaki görev hazır". 8 ardışık devam tavanı (D/hooks; araç çağrısında sıfırlanır) döngüyü sınırlar | P1 |
| K-11 | `.claude/hooks/istem_baglami.py` | UserPromptSubmit (varsayılan süre 30 sn, D/hooks): her kullanıcı mesajına ≤ 1.500 kr bağlam (aktif film, bekleyen kullanıcı işi, "bu mesaj soruysa yalnız cevap ver"); "dur/durdur/bekle" görürse `surus kapat` | P1 |
| K-12 | `hata_kaydi.py`, `model_degisti.py`, `ozet_sakla.py` | StopFailure (koşanları `kesildi`, Telegram) · PostModelSwitch (`from_model/to_model`, sapma) · PreCompact/PostCompact (özet arşivi) | P1 |
| K-13 | `.claude/settings.json` + `kurulum.py` eki (`settings.local.json` üretimi) | Aşağıda. Kurulum ayrıca `claude --version` ≥ 2.1.302 (fork varsayılanının belgelendiği sürüm; `omitClaudeMd` 2.1.271+) denetler ve masaüstüne `FILM_SETI.bat` koyar | P0 |
| K-14 | `.claude/kurallar/erisim.json` | §4.5.7 | P0 |
| K-15 | `ARACLAR/kor_paket.py` | Çatı: beyaz liste, ad + hitap maskeleme, aşamalı bölüm klasörü (`_SEYIRCI_PAKETI/<tur>/P0..P3`), işitsel döküm satırı biçimi; kipler alan sahiplerinin; `izleme_paketi.py` modülü olur | P0 |
| K-16 | `ARACLAR/dilim.py`, `plan_birlestir.py` (sahiplik denetimi alan başına) | Ajanlara SAHNELER/HIKAYE dilimi; PLANLAR + SES → SAHNELER.json (eski şemayla uyumlu) | P0 |
| K-17 | Şablonlar + şemalar | `sablonlar/<ASAMA>_<ajan>[_<kip>].md` (sayılar yer tutucuyla basılır); `semalar/*.json` | P0 |
| K-18 | 21 ajan dosyası | §4.3; frontmatter benim, gövde alan sahibinin | P0 |
| K-19 | 4 SKILL.md + `KURTARMA.md`, `GOREV_SEMASI.md`, `KULLANICI_DILI.md` + kök `CLAUDE.md` + veri kökü `CLAUDE.md` + `ARACLAR/CLAUDE.md` | §4.4 | P0 |
| K-20 | Testler (ağsız, kredisiz, LLM'siz; ajan çıktıları kayıtlı "sahte ajan" dosyalarından) | `test_gorev_defteri.py` (30 kesme noktası, arka plan dönüşü, maxTurns kısmi çıktısı), `test_kancalar.py` (stdin örnekleri: başka görevin CIKTI'sini okuyan seyirci, ileri bölüm okuma, gizli dosya iki kökte, makine sahipli yazma, fork/general-purpose/kadro dışı ajan, `name` parametresi, nabızsız `basla`, PowerShell ile gizli dosya, iç ajan SubagentStop'u, Windows yolu `C:\…` büyük/küçük harf, sürüş kapalıyken geliştirme işlemleri serbest), `test_kor_paket.py` (yasak alan ve ad sızıntısı 0), T-nabız, T-asamali, T-arkaplan | P0 |
| K-21 | `ARACLAR/beceri_denetim.py` | SKILL.md satır ve çekirdek token tahmini; `name` kuralı (≤ 64, küçük harf-rakam-tire, "claude/anthropic" yok); `description` ≤ 1.024, + `when_to_use` ≤ 1.536; ajanlarda `model: opus`, `effort: high`, `permissionMode: acceptEdits`, `memory` yok, `Agent`/`Bash` yok; kör ajanlarda `omitClaudeMd: true` ve yalnız `Read, Write`; ajan açıklamaları toplamı; şablonlardaki OZET biçimi `puan_oku` deseniyle aynı; referans dosyasında içindekiler | P1 |
| K-22 | `ARACLAR/memmet_yama.py` + `testler/test_memmet_korkuluk.py` | İ-3 akışı (geçici kopya, üç kapı, uygula, karar kaydı) | P1 |
| K-23 | `.bat`: `FILM_SETI.bat` (depo kökünde `claude`'u açar), `DEVAM.bat` (`claude --continue "devam"`, doğrulanacak), `DURUM.bat`, `UYARI_GECTI.bat`, `GECE_IZNI.bat`, `GUNCELLE.bat` ([UM2]), `ARSIVLE.bat` | Kullanıcının tek tık işleri | P1 |
| K-24 | `ARACLAR/ajan_tanimi.py` | Ajan `.md` dosyasının frontmatter + gövdesini okuyan tek kütüphane; [UM2]'nin başsız yürütücüsü (`yurut --basliksiz`) sistem istemini buradan alır, böylece iki yol aynı tanımı ve aynı `ISTEM.md`'yi kullanır | P2 |
| K-25 | `set-amiri` ajanıyla oturum açma deneyi (`claude --agent set-amiri`, D/agents) | Ana oturumun kendisi yalnız `Read, Bash, Agent, SendMessage, Skill` araçlarıyla açılır; "ana Claude yazmaz" kuralı araçla zorlanır. Varsayılan Claude Code sistem istemi yerine ajan gövdesi geçtiği için önce sahte filmde denenir | P2 |

**`.claude/settings.json` (paylaşılan; öneri)**
```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"},
  "permissions": {
    "allow": ["Bash(python .claude/bin/film.py *)"],
    "deny":  ["Read(./YZ_FILM/AYARLAR/*_anahtar.txt)", "Read(./YZ_FILM/AYARLAR/telegram_bot.txt)",
              "Read(./YZ_FILM/AYARLAR/memmet_profil/**)", "Bash(robocopy * /MIR*)"]
  },
  "hooks": {
    "SessionStart":   [{"matcher": "startup|resume|clear|compact", "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/oturum_basi.py\""}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/istem_baglami.py\""}]}],
    "PreToolUse": [
      {"matcher": "Read|Glob|Grep|Write|Edit|NotebookEdit", "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/erisim_kapisi.py\"", "timeout": 10, "onFailure": "block"}]},
      {"matcher": "Bash|PowerShell", "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/komut_kapisi.py\"", "timeout": 10, "onFailure": "block"}]},
      {"matcher": "Agent", "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_kapisi.py\"", "timeout": 10, "onFailure": "block"}]}],
    "SubagentStart":  [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_basi.py\""}]}],
    "SubagentStop":   [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_bitti.py\"", "timeout": 120}]}],
    "PostToolUse":    [{"matcher": "Agent", "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_sonrasi.py\""}]}],
    "Stop":           [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/stop_kapisi.py\""}]}],
    "StopFailure":    [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/hata_kaydi.py\""}]}],
    "PreCompact":     [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ozet_sakla.py\""}]}],
    "PostCompact":    [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ozet_sakla.py\""}]}],
    "PostModelSwitch":[{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/model_degisti.py\""}]}]
  }
}
```
- Statik `deny`'da yalnız her bağlamda yanlış olan kalır (İ-11). Kadro dışı ajan, çıplak `git push`, `memmet.py` doğrudan çağrısı sürüşe bağlıdır ve kancadadır.
- `fallbackModel` **yazılmaz**: D/model'e göre yedek zinciri sessizce başka modelle iş yaptırır ([CM1] §3.1).
- Kanca hata davranışı: güvenlik kancaları (`erisim`, `komut`, `ajan`) kapalı başarısızdır; bilgi kancaları (`ajan_sonrasi`, `oturum_basi`) açık başarısızdır
  (hat kilitlenmez). `ajan_bitti` 120 sn'yi (tahmin) aşarsa görev `gecersiz` sayılır ve yeni deneme açılır; kör görev hiçbir zaman doğrulamasız `bitti` olmaz.

### 4.7 Makinenin denetleyeceği eşikler (kaynağıyla)

**Claude Code yapısı** (denetleyen: `beceri_denetim.py`, kancalar, `film.py`)

| Eşik | Değer | Kaynak | Denetleyen |
|---|---|---|---|
| SKILL.md satır | < 500 (hedef ≤ 250) | D/skills "Keep SKILL.md under 500 lines" | beceri_denetim |
| Sıkıştırma sonrası geri gelen beceri metni | en son çağrının ilk 5.000 tokeni; toplam 25.000 | D/skills | beceri_denetim: çekirdek ≤ 4.500 token (tahmin: kr/3) |
| `description + when_to_use` | 1.536 kr'de kesilir | D/skills | beceri_denetim |
| `description` | ≤ 1.024 kr | AR3 B2 (Agent Skills spesifikasyonu) | beceri_denetim |
| Başarısız `!` komutu | bütün beceri çağrısı iptal | D/skills | `ozet` daima 0 + `\|\| true` |
| Ajan açıklamaları toplamı | uyarı > 15.000 token; hedef ≤ 3.000 | D/agents | beceri_denetim |
| Ajan adı | ≤ 256 kr, `:` yok | D/agents | beceri_denetim |
| Eşzamanlı alt ajan | varsayılan 20; bizde 5 (yerel `CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS` + `ajan_kapisi`) | D/agents; 5: [YN2]/[UM2] tahmin | ajan_kapisi, film.py |
| İç içe ajan | varsayılan 3 katman; bizde imkânsız (araç listesinde `Agent` yok) + yerelde 1 | D/agents | beceri_denetim, settings.local |
| Fork kipi | kapalı (`CLAUDE_CODE_FORK_SUBAGENT=0`) + `fork` adı ret | D/agents (v2.1.302'den beri varsayılan açık) | ajan_kapisi, nabız `ayar_sha` |
| Kanca bağlamı (`additionalContext`) | ≤ 10.000 kr (aşarsa dosyaya yazılır, 2.000 kr önizleme) | D/hooks | oturum_basi kendini kısaltır |
| Güvenlik kancası zaman aşımı | 10 sn + `onFailure: "block"` | D/hooks (varsayılan açık başarısızlık); 10 sn tahmin | test_kancalar |
| Stop kancası ardışık devam | 8 (araç çağrısında sıfırlanır; `CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`) | D/hooks | stop_kapisi bu tavana güvenir |
| SubagentStop düzeltme | en çok 2 blok (bölüm başına), sonra `gecersiz` | AR3 B6 OpenMontage "en fazla 2 öz-denetim turu" | ajan_bitti |
| Görev deneme tavanı | 3 (ilk + 2) | tahmin | film.py |
| Kanca nabzı tazeliği | ≤ 15 sn | tahmin | film.py basla |
| Referans dosyası | > 100 satırsa başında içindekiler; derinlik 1; ≤ 300 satır | AR3 B4; 300 tahmin | beceri_denetim |
| Ajan dönüş mesajı | ≤ 5 satır / ≤ 600 kr | YR §4 şablonları; 600 tahmin | ajan_sonrasi uyarır |
| Ana Claude Read sınırı | 200 KB | tahmin | erisim_kapisi |
| Ön plan Bash komutu | ≤ 10 dk; uzun iş ayrık süreç | Bash aracı tanımı (600.000 ms) | film.py calis (60 sn üstü → `yerel_is`) |
| Claude Code sürümü | ≥ 2.1.302 | D/agents (fork varsayılanı), `omitClaudeMd` 2.1.271+ | kurulum.py |

**Döngü ve değerlendirme** (denetleyen: `film.py`, `puan_oku.py` v2; değerler alan sahiplerinin, yalnız yer)

| Eşik | Değer | Kaynak |
|---|---|---|
| Seyirci sayısı / birleştirme | 3 / medyan | RE `seyirci_sayisi`, `seyirci_karar` |
| GENEL medyan; ölçüt medyanı alt sınırı | ≥ 8; ≥ 7 | RE `seyirci_genel_esik`, `seyirci_olcut_min` |
| KRİTİK / ORTA kopukluk | 0 / ≤ 3 parti başına | RE `kopukluk_kritik_max`, `kopukluk_orta_max_parti` |
| Özet eşleşmesi | ≥ 0,80 | RE `ozet_eslesme_min` |
| İlk 2 dk "devam ederdim" | 3/3 | RE `ilk2dk_devam_evet_min` |
| KRİTİK reddi | tur başına seyirci başına ≤ 1, kanıt alıntısı betikle doğrulanır | İ-8; 1 tahmin |
| Tur tavanı kâğıt / kurgu / görsel | 4 / 3 / 2 | RE `kagit_tur_max`, `kurgu_tur_max`; UH §5 |
| Kesme turu | 10 plan ya da 2 sahne öneri; uygulanan / simülasyondan HATA'sız geçen ≥ %50 | RE `kesme_turu_oneri`; payda [KU2] İ-6 |
| Kâğıt seyirci bölümü | P0 = 0–120 sn, sonra P1 kalanı, P2, P3 | [SN2] İ6 |
| İzleme bölümü | 240–300 sn (`izleme_parcasi`) | BK §3.8; [UM2] |
| Kör gözlem görev boyu | ≤ 12 görsel/görev | [GS2] tahmin |
| Yönetmen görev boyu | 1 sahne grubu | [YN2] |
| Toplam ajan görevi / film | ≈ 350–550 | [UM2] §4.3.6 tahmin |

**Gizlilik ve kredi** (denetleyen: kancalar, `kredi.py`)

| Eşik | Değer | Kaynak |
|---|---|---|
| Gizli dosya erişimi (iki kök, Bash ve PowerShell dahil) | 0 | BK §6.5; CLAUDE.md kuralları |
| Flow uyarısı | ilk uyarıda dur; kilit yalnız `UYARI_GECTI.bat` (elle 1 video başarılı + ≥ 30 dk, yalnız o gün) | BK §6.2 #8–#9; [UM2] İ-8 |
| Bütçe yetmezse | dur; kalite kısma yok | BK §3.7, §8 #16 |
| `memmet.py` yaması | korkuluk testi HATA 0; değişen satır ≤ 80 | İ-3; 80 tahmin |

### 4.8 Kesin kararların benim alanımda uygulanışı

**Karar 1 — Kullanıcıya yalnız konu sorulur**
- Metinde: kök CLAUDE.md, SKILL.md çekirdeğinin 1. maddesi, oturum başı bağlamı (tek cümle, "sen seç" seçeneğiyle).
- Makinede: `stop_kapisi` beyaz liste dışı karar sorusunu engeller (§4.5.10); `kararlar/` içindeki `soru` kayıtları sayılır (M1). Kurulum da soru sormaz (İ-9).
- Eski onay noktaları (karakter görünüşü, ses, kurgu, animatik; BK §7.3, §8 #17) kalkar; yerine jüri medyanı, kör tarif + ölçüm, ölçülü ses seçimi gelir.
  Kullanıcı yine de CapCut'ta izleyip not bırakabilir; bu bir soru değil, `film-not` girdisidir.
- Soru ile fiziksel iş ayrıdır: kredi yüklemek, Gemini'ye paket vermek, Flow'da GÖNDER'e basmak kullanıcının elindedir; talimat olarak verilir, bitişi dosyadan algılanır.

**Karar 2 — Atomik eylem zinciri**
- Tek sahip: `eylem_zinciri`, `baslangic_durumu`, `bitis_durumu` alanlarını yalnız `yonetmen·plan` yazar; `hareket_istem` kodla derlenir (ajan istem yazamaz).
- Kural en üstte: `yonetmen.md` gövdesinin ilk satırı bu kuraldır ([YN2] §4.3.1: "Klip başına 2–3 adım (konuşma bir adımdır) … karakterin KENDİ
  sağı/solu … el şekli"); alt ajanın sistem istemi her zaman bağlamdadır (İ-6).
- Denetim: `plan_denetim --sahne` SubagentStop kancasında koşar; HATA'da durma engellenir ve hata listesi aynı yönetmen örneğine döner (≤ 2).
  Yasak sonuç fiilleri GIRDI'ye RE `yasak_sonuc_fiilleri`'nden basılır (tek kaynak).
- Görüntüde: `kare-tarifcisi`'nin soru formu bu alanlardan `kor.py` ile üretilir (görüntü koordinatında); kod beklenenle karşılaştırır.
- Habersiz seyirci de kullanır: kâğıt ve plan kör paketinde planlar görünür atomik adımlarla anlatılır; seyirci yalnız görünür adımlardan anlıyorsa
  hikâye ekrana çıkmış demektir (anlatıcısız filmin testi).

**Karar 3 — Altı özellik**

| Özellik | Aşama | Ajan | Betik | Kanca / Claude Code tarafı |
|---|---|---|---|---|
| (a) Animatik + habersiz seyirci | A12 (video kredisinden önce; `giris_sarti`) | `habersiz-seyirci·animatik` ×3 aşamalı, `ozet-eslestirici`, `kesici`, `kurgucu` | `animatik.py`, `kor_paket.py --kip animatik`, `puan_oku` v2 | Kör rol + aşamalı okuma SubagentStop'ta; nabız şartı; fork yok |
| (b) Dünya durumu defteri + zıplama denetimi | A07c'de kurulur; A11, A14, A16'da gözlemle karşılaştırılır | `yonetmen` (etkileri yazar), `sureklilik-denetcisi·kagit/hakem` | `dunya_defteri.py` → `DUNYA_DEFTERI.json` | Makine sahipli: hiçbir ajan ve ana Claude elle düzeltemez (`erisim_kapisi`) |
| (c) Referansla otomatik yüz kontrolü | A10d, A11, A14 | `kare-tarifcisi` (yalnız kör envanter), `sureklilik-denetcisi·hakem` (tek kaynaklı BAYRAK) | `yuz_denetim` (SFace), `kare_denetim` | Yüz gömmeleri `EVREN/` altında, makine sahipli |
| (d) Kare zinciri | A14 (uygunluk kuyruğu) | — | `kare_zinciri.py` (kesme anındaki gerçek kare, [GS2] İ-1), `blok_plani.py` | `zincir` planları görev defterinde sıralı bağımlılıktır; `sonraki` kaynağı geçmeyen planı vermez |
| (e) Kendi kendine öğrenen ders defteri | her kapıda kendiliğinden kayıt; `film-not`'ta şikâyet; A18'de terfi | `ders-editoru` | `ders_defteri.py` | Dersler rol etiketiyle **GIRDI/DERSLER.md**'ye girer (imzalı); kör rollere girmez; `memory:` kullanılmaz |
| (f) Kalıcı seri evreni kütüphanesi | A01 (seri seçimi), A09–A10d (kart/ses), A18 (güncelleme) | `yapimci`, `kart-tasarimcisi`, `ses-tasarimcisi·kadro`, `hikaye-yazari·evren` | `evren.py` (tek yazar) | `EVREN/` makine sahipli; ajanlar yalnız GIRDI kopyasını görür; kapı seyircisi `IZLEYICI_OZETI`'ni görmez |

**Karar 4 — Ses / dudak uyumu**
- Yöntemi ses uzmanı seçti ([SM2]: Veo konuşur, ses dönüştürülür; ağzı görünmeyende TTS; yedek TTS + dudak senkronu). Mimarinin şartları:
  1. **Claude ajanları ses duyamaz.** Ses kararı ajana bırakılmaz; ölçülür (WER, SyncNet, LUFS, konuşmacı gömmesi). Ajan yalnız ölçüm JSON'unu ve meta veriyi okur.
  2. Yol kodla önerilir (`_derlenir.agiz_gorunur`); ajan yalnız gerekçeyle değiştirir; gerçekleşen yol `SESLER/diyalog.json`'a yazılır ([SM2] İ-5).
  3. Metne dokunan tek gri karar (Veo'nun söylediği kabul mü) metnin sahibine, `hikaye-yazari·replik_kabul` kipine gider; her seferinde yeni örnek.

**Karar 5 — Memmet bir yerleştirme yardımcısıdır; bot tespiti atlatılmaz**
- `komut_kapisi`: sürüşte `memmet.py` doğrudan çalıştırılamaz (yalnız `film.py` üzerinden); Flow kilidi varken video ve görsel gönderimi yoktur; fare/klavye
  kütüphanesi her bağlamda ret.
- A14 görevleri `kullanici_eylemi` olarak gelir ("Memmet hazırladı; Flow penceresinde GÖNDER'e bas"); bitiş indirilen dosyadan algılanır.
- `memmet-bakimci` kaynak koda yazamaz; yamasını korkuluk testi sınar (İ-3).

**Karar 6 — Üstün körü iş yok**
- Bütün ajanlar opus + high; yedek model zinciri yok; sapma kaydı (M14).
- Hiçbir kapı "zaman/kredi az" diye atlanmaz: `giris_sarti` kredili aşamayı kâğıt kapıları geçmeden açmaz.
- Değerlendiricinin yarım işi tamamlanmaz, sıfırdan yapılır; yazarın yarım işi sürdürülür.
- Kanca güvenceleri kapalı başarısızdır ve nabızla kanıtlanır (M6); kesilme, bağımsızlık ve sızıntı testleri P0'dır.

### 4.9 Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

#### 4.9.1 Riskler

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R-1 | **Yanlış klasörde açılış:** kullanıcı alışkanlıkla Claude'u `Desktop\YZ_FILM`'de açar; `.claude/` orada olmadığı için beceri ve kanca yüklenmez | Set çalışmaz ya da kancasız çalışır | Veri kökü `CLAUDE.md` yönlendirmesi; `FILM_SETI.bat`; kancasız ortamda nabız olmadığı için ajan görevi zaten başlamaz |
| R-2 | **Kullanım sınırı:** ≈ 350–550 Opus görevi (tahmin); Claude kendi kendine uyanamaz | Hat günlerce bekler | Her şey dosyada (M3); StopFailure → Telegram; `DEVAM.bat`; otomatik devam açık soru S-2 |
| R-3 | **Kapalı başarısız kanca bütün hattı durdurur** (kanca hatası ya da yavaş Python) | Hat durur | `test_kancalar.py` P0; kanca ≤ 2 sn hedefi; hata `FILM_KAYIT`'a; `DURUM.bat` son engelleri gösterir; bilgi kancaları açık başarısız |
| R-4 | **Kanca atlatma:** kanca araç çağrılarını görür; ana Claude Bash'te Python ile dosya yazabilir | Makine sahipli dosya elle değişir | İzin listesi yalnız `film.py`; `komut_kapisi` sezgisel tarama; `film.py` makine sahipli dosyaların sha1'ini saklar, uyuşmazsa HATA |
| R-5 | **Arka plan bildirimi oturumu uyandırmazsa** | Ajan bitti ama döngü durdu | Bitti kararı kancada olduğu için iş kaybolmaz; `DEVAM.bat` ya da kullanıcının "devam"ı sürdürür; T-arkaplan ile ölçülür |
| R-6 | **Sürüm farkı:** fork varsayılanı, `omitClaudeMd`, `onFailure`, `PostModelSwitch` sürüme bağlı; tanınmayan frontmatter alanı sessizce yok sayılır (D/agents) | Güvence sessizce kalkar | `kurulum.py` sürüm denetimi (≥ 2.1.302); nabız `ayar_sha`'sı; `beceri_denetim` |
| R-7 | **Aynı model ailesi kendi yazısını yargılar** (ARIS "hiçbir model kendi çıktısını onaylamaz", AR1 B4) | Kör nokta, puan şişmesi | Kör paket + yeni örnek + betik karşılaştırması; kâğıt ↔ animatik ↔ kurgu puan farkı ders defterinde; Gemini yalnız bulgu kaynağı ([GS2] İ-6) |
| R-8 | **Ajanlar ses duyamaz, hareketi göremez** (yalnız kare) | Ses ve hareket hataları ajan denetiminden kaçar | Ses ve hareket kapıları betikte (V1/V2/V3, SyncNet, LUFS, WER) |
| R-9 | **Durdurulamayan sürüş** | Kullanıcının "dur"u ezilir | `istem_baglami` "dur/durdur/bekle" → `surus kapat`; `film-durum` o tur kapatır; Stop tavanı 8 |
| R-10 | **Windows'ta kanca komutu:** Git Bash ile `python "$CLAUDE_PROJECT_DIR/…"`; PowerShell aracı; yolların `C:\` biçimi | Kanca çalışmaz ya da yol eşleşmez | Kurulumda bir kez sınama (§4.9.4); yol normalleştirme; nabız |
| R-11 | **Fiziksel iş yükü:** ≈ 18–24 Gemini paketi + `elle` modda ≈ 527 GÖNDER ([UM2] hesap) | Kullanıcı yorulur | İşler toplanır; her biri tek `.bat`/tek talimat; bitiş otomatik algılanır (M2); hızlandırma yolları kurulum ayarıdır, soru değildir |
| R-12 | **Bulutta proje iş parçacığı** ayar kancalarını uygulamaz (D/settings) | Kör görev kancasız koşabilir | Nabız şartı; beceri içi yedek kanca; KURTARMA.md "tek depolu oturum aç" |
| R-13 | **SubagentStop ile aşamalı devam** beklendiği gibi çalışmazsa | Aşamalı okuma yürümez | Yedek sıra (İ-4): SendMessage → bölüm başına ayrı görev |

#### 4.9.2 Diğer uzmanlarla kalan çakışmalar (önerdiğim çözümle)
- **Ç-1 Klasör adları** (İ-7): [YN2] `30_YONETMEN` → `_YONETMEN`, [SM2] `35_SES` → `_SES`. Tur 3 yoksa bu belge karardır.
- **Ç-2 `memmet-bakimci` yetkisi** (İ-3): [UM2]'nin kabulü gerekir; korkuluk kuralının içeriği üretim uzmanınındır.
- **Ç-3 Aşamalı okumanın mekanizması** (İ-4): [SN2] ve [KU2] SendMessage'ı yedek olarak tutar; birincil yol SubagentStop.
- **Ç-4 KRİTİK reddi** (İ-8): [SN2] ve [KU2] dört şartı kabul ederse kapı korunur.
- **Ç-5 Kurulumda soru** (İ-9): [UM2] Q9'un bilgi + `.bat` biçimine dönmesi.
- **Ç-6 Plan eleştirmeninin rolü:** [YN2] kör (`omitClaudeMd`) diyor ama `PLAN_DILI.md` §Kontrol listesini okutuyor. Çözüm: o bölüm GIRDI'ye kopyalanır, rol `kor` kalır.
- **Ç-7 `diyalog-editoru` rolü:** [SN2] ayrı ajan diyor; Ç-10 ölçütü (b) ile kabul. Kör değildir (bütün replikleri ve evren sözlüğünü görür); rol `denetci`.

#### 4.9.3 Açık sorular
- **S-1** (kapandı) Bulut/yerel: [UM2] iki kök + `esitle` kabul edildi.
- **S-2** Kullanım sınırından sonra kendiliğinden devam: `DEVAM.bat` = `claude --continue "devam"` güvenle çalışır mı; masaüstü uygulamasının zamanlanmış
  görevleri kullanılabilir mi? Belgeden doğrulanmadı.
- **S-3** (kapandı) Tur tavanı dolunca: [SN2] H11 merdiveni + [GS2] kaçış merdiveni; sonunda DUR + bilgi, soru yok.
- **S-4** (kısmen kapandı) İkinci model: Gemini yalnız bulgu kaynağı, onay kaynağı değil ([GS2] İ-6). API ile mi elle mi: bütçe ayarına bağlı, varsayılan yok.
- **S-5** Seçilen kartlar ve sesler kullanıcıya son özette gösterilsin mi? Önerim: evet, bilgi olarak; itirazı `film-not` ile.
- **S-6** `effort: high` mı `xhigh` mı? Kullanıcı "yüksek" dedi; kanıt olmadan `high`.
- **S-7** `--agent set-amiri` (K-25) varsayılan olsun mu? Önce sahte filmde ölçülür; Claude Code'un varsayılan sistem istemini kaybetmenin etkisi bilinmiyor.
- **S-8** Görev boyları (12 görsel, 1 sahne grubu, 240–300 sn bölüm) ilk filmde ölçülerek ayarlanır.

#### 4.9.4 Uygulamadan önce bir kez doğrulanacak Claude Code davranışları
1. `CLAUDE_CODE_FORK_SUBAGENT=0` ile tek mesajdaki 3–5 Agent çağrısının paralel koşması ve ana Claude'un sonucu beklemesi.
2. Arka planda biten alt ajanın tamamlanma bildiriminin, ana tur bitmişken oturumu kendiliğinden uyandırması.
3. SubagentStop `decision: "block"` ile aşamalı devam: ön planda ve arka planda; `maxTurns`'e ulaşan ajanda SubagentStop'un tetiklenmesi ve kısmi çıktının `SendMessage` ile sürdürülmesi.
4. PreToolUse `Agent` girdisinde `subagent_type`'ın (fork dahil) ve `name`/`isolation` parametrelerinin görünmesi.
5. `onFailure: "block"` ve `timeout` alanlarının komut kancasında beklendiği gibi çalışması (kasıtlı yavaş kanca testi).
6. Ayar `env`'inin kanca süreçlerine geçip geçmediği (nabız `ayar_sha` yedeği hazır).
7. `settings.local.json → additionalDirectories` ile Windows veri köküne `acceptEdits` alt ajanın soru sormadan yazabilmesi.
8. Windows'ta Git Bash ile `python "$CLAUDE_PROJECT_DIR/.claude/hooks/…"` komutu, PowerShell aracı eşleyicisi ve Python 3.10 ile kancaların ≤ 2 sn'de bitmesi.
9. Becerideki `hooks` alanı ile ayar kancası aynı komutu taşıyınca iki kez koşup koşmadığı.
10. `!` komutunun Windows'ta `python` bulması (bulamazsa `|| true` beceriyi kurtarır ama özet boş gelir → `py -3.10` yedeği sarmalayıcıda).
11. `claude --continue "devam"`'ın son oturumu sürdürüp ilk mesajı göndermesi.

---
*Bu belge Claude Code mimarisi uzmanının 2. tur önerisidir. Kaynağı olan her sayının yanında kaynağı yazar; **(tahmin)** işaretli sayılar ilk filmde
ölçülerek ayarlanır; **(doğrulanacak)** davranışlar §4.9.4 listesiyle uygulamadan önce bir kez sınanır.*
