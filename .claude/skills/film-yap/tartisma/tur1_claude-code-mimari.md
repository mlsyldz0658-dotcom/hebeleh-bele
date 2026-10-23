# TUR 1 — Claude Code mimarisi (beceriler, ajanlar, durum, kancalar, dayanıklılık)

Hazırlayan: claude-code-mimari uzmanı · 23.10.2026 · Diğer uzmanların dosyaları okunmadı.

**Kaynak kısaltmaları:** `BK` BILGI_KURALLARI.md · `ZN` ZANAAT.md · `RE` ritim_esikleri.json ·
`AR1/AR2/AR3` arastirma/01, 02, 03 · `UH` FILMLE ILGILI CLAUDE/01_URETIM_HATTI.md · `DR` 03_DERSLER.md ·
`YR` YAPIM_REHBERI.md · `CI` CLAUDE_ICIN.md · `H/<ad>` HAFIZA_YEDEGI notu.
**Bugün belgeden doğrulananlar** (code.claude.com/docs/en/ hooks.md, sub-agents.md, skills.md, model-config.md; 23.10.2026
WebFetch ile okundu): `D/hooks`, `D/agents`, `D/skills`, `D/model`. AR3'te olmayan Claude Code bilgilerini bunlardan aldım.
Kaynağı olmayan her sayı **(tahmin)** diye işaretli.

**Tek cümlelik öneri:** Hattın beyni `film.py` içindeki **görev defteri** olsun (ne bitti, sıradaki iş ne, geçme şartı ne);
ana Claude yalnız "set amiri" olarak bu defterden sıradaki görevi alıp ajana, betiğe ya da kullanıcıya (yalnız fiziksel iş için)
dağıtsın; bağımsızlık, gizlilik ve "kullanıcıya yalnız konu sorulur" kuralları metinde değil **kancalarda (hook)** zorlansın.
Böylece oturum kesilse, bağlam sıkıştırılsa ya da kullanım sınırı dolsa da hiçbir şey hafızaya bağlı kalmaz.

---

## 1. Alanımın hedefi ve başarı ölçütü (sayılarla)

**Hedef:** Depo Claude Code'da açıldığında Claude kullanıcıya **yalnız filmin konusunu** sorar; sonra konudan yayın paketine
kadar bütün işi, dosyaya yazılmış bir görev defteri üzerinden, birbirini okumayan uzman ajanlarla ve makine kapılarıyla yürütür.
Oturum kesilmesi, sıkıştırma (compaction), kullanım sınırı ya da bilgisayarın kapanması **hiçbir işi kaybettirmez ve hiçbir
işi iki kez yaptırmaz**.

| # | Ölçüt | Hedef | Nasıl ölçülür |
|---|---|---|---|
| M1 | Kullanıcıya sorulan **karar** sorusu | Film başına **1** (konu). Konuyu ilk mesajda verdiyse **0** | `FILM_KAYIT.txt` içindeki `SORU` olayları + Stop kancası `soru_kapisi` engel sayısı (§6 K-8) |
| M2 | Kullanıcıdan istenen fiziksel iş (Gemini'ye paket verme, Flow'da GÖNDER, kredi yükleme) | Her biri ayrı `kullanici_eylemi` görevi, `.bat` adıyla; bitişi **kendiliğinden algılanır** (kullanıcının "bitti" demesi gerekmez) ≥ %90 **(tahmin)** | Görev defterinde `algilama: dosya_var` alanı dolu görev oranı |
| M3 | Kesilmeye dayanıklılık | Sahte uçtan uca testte **30 rastgele kesme noktasında** (ajan ortası, betik ortası, kapı ortası, paralel grubun yarısı) %100 tamamlanma; **biten görevin yeniden çalışması 0**; **kredili işin çift gönderimi 0** | `testler/test_gorev_defteri.py` (§6 K-18) |
| M4 | Bağımsızlık | Bağımsız ajanların başka görev çıktısını okuma denemesi → **izin verilen 0** (engellenenler günlüğe yazılır); kör pakette yasak alan sızıntısı **0** | `erisim_kapisi` günlüğü; `test_kor_paket.py` |
| M5 | Beceri boyutu | Her SKILL.md ≤ 500 satır (hedef ≤ 250); SKILL.md'nin ilk bölümü ("çekirdek") ≤ 4.500 token **(tahmin: karakter/3)**; `description` ≤ 1.024 kr; `description + when_to_use` ≤ 1.536 kr | `beceri_denetim.py` (§6 K-19) |
| M6 | Ajan tanımları | 15 ajan; açıklamaların toplamı ≤ 3.000 token (belge uyarı eşiği 15.000); iç içe ajan **0** | `beceri_denetim.py` |
| M7 | Oturum başı özeti | `additionalContext` ≤ 10.000 kr (belge sınırı), hedef ≤ 6.000 kr | `oturum_basi.py` kendi uzunluğunu ölçer |
| M8 | Ana Claude'un bağlamı | Ajan dönüşü ≤ 5 satır / ≤ 600 kr; ana Claude 200 KB'tan büyük dosyayı Read ile açmaz **(tahmin eşik)** | `ajan_bitti` kancası dönüşü kırpar ve uyarır; `erisim_kapisi` büyük dosyada `film.py goster` önerir |
| M9 | Ajan çıktı sözleşmesi | İlk denemede şemadan geçme ≥ %90 **(tahmin hedef)**; SubagentStop ile en çok 2 düzeltme, sonra görev `gecersiz` → yeniden | `DEFTER.jsonl` istatistiği |
| M10 | İzin penceresi | Kâğıt aşamalarının tamamı izin penceresi açmadan (allowlist); hedef **0** istem | Sahte kuru çalıştırma |
| M11 | Model disiplini | Bütün ajanlar `model: opus`, `effort: high`; `fallbackModel` **tanımsız**; alt ajanda otomatik model geçişi **0** (olursa kayıt + o görev yeniden) | `PostModelSwitch` kancası |

---

## 2. Aşama aşama süreç

### 2.0 Yürütme modeli (bütün aşamalar için ortak)

```
kullanıcı ──(yalnız konu)──► ana Claude (set amiri, film-yap becerisi)
                                 │  1) python .claude/bin/film.py sonraki      → sıradaki görev(ler) JSON
                                 │  2) python .claude/bin/film.py basla G…      → görev "calisiyor"
                                 │  3a) tur=ajan   → Agent(<ajan>, "Görevin: …/GOREV.json; önce onu oku")
                                 │  3b) tur=betik  → Bash(python .claude/bin/film.py kapi …)
                                 │  3c) tur=kullanici_eylemi → kullanıcıya düz Türkçe talimat (.bat adıyla), tur biter
                                 │  3d) tur=bekle  → nedeni söyle (Flow dinlenmesi, kredi), tur biter
                                 │  4) SubagentStop kancası çıktıyı doğrular → film.py bitir G… (kendiliğinden)
                                 └─ 5) PostToolUse(Agent) kancası "sıradaki: …" bağlamını ekler → 1'e dön
```
- **Görev** = `_GOREV/<id>/` klasörü: `GOREV.json` (sözleşme), `ISTEM.md` (film.py'nin şablondan doldurduğu talimat),
  `GIRDI/` (ajanın okuyabileceği HER şeyin kopyası), `CIKTI/` (ajanın yazabileceği tek yer). Ana Claude istem yazmaz;
  istemler `.claude/skills/film-yap/sablonlar/` içindeki şablonlardan **betikle** üretilir → aynı görev her seferinde aynı talimatla çalışır.
- **Paralel grup:** aynı `paralel_grup` değerli görevler ana Claude'un tek mesajında birlikte başlatılır (3 seyirci, 4 mimar…).
- **Kim yapar** sütunundaki kısaltmalar: **AC** ana Claude · **B** betik (`film.py` alt komutu) · **A:<ad>** ajan · **K** kullanıcı (yalnız fiziksel iş).
- **Ortam:** `bulut` = Claude Code web oturumu da yapabilir (kâğıt + sahte); `yerel` = yalnız kullanıcının Windows'u (Flow, Gemini uygulaması, CapCut, GPU).

### 2.1 Aşama tablosu

| Aşama | Girdi | İş | Çıktı dosyası | Geçme şartı | Kim | Ortam |
|---|---|---|---|---|---|---|
| **A00 Konu** | Kullanıcı mesajı; `film.py ozet` → "aktif film yok" | Konu yoksa TEK soru: *"Filmin konusu ne olsun? Bir cümle yeter."* Konu gelince `film.py yeni --konu "<aynen>"` | `FILMLER/<id>/00_KONU.md`, `FILM_DURUM.json`, `FILMLER/_AKTIF.json` | Konu boş değil; aynı turda başka soru yok | AC + B | bulut/yerel |
| **A01 Proje kararları** | GIRDI: 00_KONU, KARARLAR.md, BK §1–2 ve §7, ZN §0, RE özeti, `EVREN/` dizini, `DERSLER_AKTIF.md` | Format, hedef süre, tür/ton, seri adı (yeni ya da mevcut evren), kanca, NE YOK listesi taslağı, mimar tonları; her karar gerekçeli | `10_PROJE/PROJE_KARARLARI.md`, `proje.json`; KARAR_DEFTERI'ne kayıtlar | Şema; süre 1800–2700 sn (RE `film_sure_aralik_sn`); her kararda `neden` + `kaynak` | A:yapimci → B doğrular | bulut |
| **A02 Brifing** | proje.json, ZN §0 K1–K9, YR §5, evren özeti, DERSLER_AKTIF | Bütün mimarlara aynı brifing (deterministik birleştirme) | `10_PROJE/00_BRIFING.md` (+ sha1) | Bütün A03 görevlerinin GIRDI'sinde aynı sha1 | B | bulut |
| **A03 Hikâye odası** | Brifing + ton (A01'den; 4. mimar tonsuz "beni şaşırt", YR A2) | 4 paralel öneri; 3 parti × 8 başlık (UH §1) | `20_HIKAYE/oneriler/oneri_A..D.md` + `.json` | Şema; 3×8 başlık dolu; son satır `OZET`; okuma günlüğü temiz | A:hikaye-mimari ×4 | bulut |
| **A04 Jüri** | 4 öneri + jüri tablosu (YR A3, 10 ölçüt × 1–10) | 4 rol (ilk kez izleyen, YouTube stratejisti, tür uzmanı, duygu eleştirmeni) + üretilebilirlik; birbirini okumaz | `20_HIKAYE/juri/juri_1..5.md` | 5 geçerli rapor; `puan_oku` medyan sıralaması; karar KARAR_DEFTERI'ne (kullanıcıya **sorulmaz**) | A:juri-uyesi ×4 + A:uretilebilirlik-denetcisi | bulut |
| **A05 Birleştirme + senaryo** | Öneriler, jüri raporları | Kazanan(lar)ı organik birleştir; sahne sahne senaryo (diyalog EN); makine alanları | `20_HIKAYE/HIKAYE_v1.md`, `HIKAYE.json` (duygu_haritasi, vuruslar, MERAK_DEFTERI, KURULUMLAR, IRONILER, karakter kartları, mekânlar, NE YOK, `ana_olgular[10]`) | Şema; Z1/Z2 kâğıt kapıları HATA 0 (ZN §6.2) | A:hikaye-yazari → B | bulut |
| **A06 Kâğıt döngüsü** (≤4 tur, RE `kagit_tur_max`) | HIKAYE_vN; kör paket (adlar söylenene kadar maskeli) | 3 habersiz seyirci (tam film) + 3 ayrı "ilk 2 dk" seyircisi + konuşan karakter başına oyuncu denetimi + özet eşleştirme; aynı yazar v(N+1) yazar | `20_HIKAYE/seyirci/tN_s1..3.md/.json`, `ilk2dk_tN_*.json`, `oyuncu_<ad>_tN.md`, `HIKAYE_v(N+1).md` | GENEL medyan ≥ 8; ölçüt medyanı ≥ 7; KRİTİK 0; ORTA ≤ 3/parti; özet eşleşme ≥ 0,80; ilk 2 dk 3/3 "evet" (RE `seyirci_*`, `ilk2dk_devam_evet_min`) | A:habersiz-seyirci ×6, A:oyuncu ×≤8, A:juri-uyesi (eşleştirme kipi), A:hikaye-yazari; B puan_oku | bulut |
| **A07a Parti haritası** | HIKAYE (son), evren mekân kartları | Parti başına sahne grupları, mekân krokisi, eksenler, kamera konumları, ışık, **sahne sınır durumları** (giriş/çıkış dünya durumu) | `30_YONETMEN/HARITA_P1..3.json` | Şema; sahne ≤ 180 sn (RE `sahne_max_sn`); sınır durumları tam | A:yonetmen | bulut |
| **A07b Plan yazımı** | Harita + ilgili sahne senaryosu dilimi | Sahne grubu başına plan listesi; atomik eylem zinciri; replik yalnız bölünür/zamanlanır (metnin sahibi hikâye yazarı) | `30_YONETMEN/PLANLAR/Sxx.json` | Şema + Z0/K0 (dilim) HATA 0 | A:yonetmen (sahne grubu başına; sınırlar sabit olduğu için paralel) | bulut |
| **A07c Plan kapıları** | Bütün PLANLAR | Birleştir → SAHNELER.json; dünya durumu defteri; Z0, K0, Z1, Z2 (ZN §6.2, AR2 §6.2) | `SAHNELER.json`, `DUNYA_DURUMU.json`, `RAPORLAR/Z0_P*.json` …, `YENIDEN_YAZ.json` | HATA 0; varsa yalnız ilgili sahne grubu için yönetmen revizyon görevi | B (+ A:yonetmen revizyon) | bulut |
| **A07d Plan denetimi** (≤4 tur) | Plan kör paketi; PLANLAR | Kâğıt süreklilik (anlam), üretilebilirlik, 3 habersiz seyirci (plan düzeyi) | `30_YONETMEN/denetim/…` | Denetçi KRİTİK 0; seyirci eşikleri (A06 ile aynı) | A:sureklilik-denetcisi, A:uretilebilirlik-denetcisi, A:habersiz-seyirci ×3, A:yonetmen | bulut |
| **A08 Ses kâğıtta** | SAHNELER (dilim), HIKAYE | Plan başına `ses` alanı, ambiyans, efekt, müzik ipucu, leitmotif, ses yöntemi (karar 4) | `35_SES/SES_Sxx.json`, `leitmotifler.json`, `muzik_listesi.json`, `EKSIK_EFEKT.json` | Z2 #40 (müzik kaplama %40–65) ve ZN §5 kuralları | A:ses-tasarimcisi → B | bulut |
| **A09 İstem derleme** | SAHNELER + evren kimlik dizeleri | `gorsel_istem` / `hareket_istem` **kodla** derlenir (ZN §6.1); filtre ve yasak fiil taraması | SAHNELER.json (istem alanları), `RAPORLAR/ISTEM_DENETIM.json` | HATA 0 (istem_denetim genişletilmiş) | B (+ A:yonetmen onarım kipi) | bulut |
| **A10 Kartlar / evren** | Eksik kart listesi, evren | Kart paketi → Gemini (K) ya da API; 3 aday → kör tarif + yüz gömme → seçim; ses adayı seçimi ölçülerle | `EVREN/<SERI>/karakterler/<id>/…`, `01_KARAKTERLER/` | Her kart: kör tarif ↔ kart metni eşleşmesi; farklı karakterler arası SFace kosinüs < 0,363 (AR2 §1.1 eşiği, ters yönde kullanım benim önerim) | B, K, A:kare-tarifcisi, A:sureklilik-denetcisi (hakem) | yerel (Gemini) |
| **A11 Başlangıç kareleri + G1** | SAHNELER, kartlar | 30'luk Gemini paketleri (K) → içe al → G1: SFace + kör tarif + deterministik karşılaştırma + hakem | `SIRALI_GORSEL/NNN.jpg`, `RAPORLAR/G1_P*.json`, `YENIDEN_URET.json` | G1 HATA 0; en çok 2 tur (UH §5), sonra hakem kararı | B, K, A:kare-tarifcisi (parti başına ~12 karelik görevler, tahmin), A:sureklilik-denetcisi | yerel |
| **A12 Animatik** (≤3 tur) | Görseller + geçici ses + zamanlama | Animatik → kör kare paketi (4–5 dk'lık bölüm, BK §3.8) → 3 seyirci/parti → düzeltme | `KURGU/ANIMATIK_vN/`, `RAPORLAR/ANIMATIK_P*_tN.json` | Seyirci eşikleri; KRİTİK 0 | B, A:habersiz-seyirci ×3/parti (SendMessage ile bölüm bölüm), A:yonetmen / A:kurgucu | yerel (bulutta sahte) |
| **A13 Maliyet + bütçe kapısı** | SAHNELER, `AYARLAR/butce.json` | Klip × 12 × 1,2 (RE `kredi_klip_720p`, `kredi_yeniden_deneme_payi`) | `URETIM_ONIZLEME.json/.md` | Bütçe yeterli → devam; değilse **DUR ve bilgi ver** (soru değil; kalite kısılmaz, BK §3.7) | B | herhangi |
| **A14 Video** | Onaylı başlangıç kareleri, hareket istemleri | Memmet `--mod elle` (K GÖNDER'e basar); zincirli planlar sırayla; her indirmede V1, V2, metin kapısı, son kare çıkarma | `SIRALI_VIDEO/NNN.mp4`, `RAPORLAR/V1_*`, `V2_*`, `YENIDEN_URET.json` | V1/V2 HATA 0; Flow uyarısında **kilit** | B, K | yerel |
| **A15 Ses üretimi** | Videolar, ses kararları | Dönüştürme / TTS, dudak denetimi, LUFS eşitleme, ambiyans katmanı | `SESLER/…`, `RAPORLAR/SES_*.json` | Z3 #44–47; SyncNet eşikleri (AR3 A1) | B | yerel |
| **A16 Kurgu** (≤3 tur, RE `kurgu_tur_max`) | Videolar + sesler + müzik | Kurgu taslağı, K1 geçiş denetimi, Z3; kurgu izleme (üçlü pencere, AR1 §5); kesme turu (RE `kesme_turu_oneri`) | CapCut taslağı, `KURGU/KURGU_PLANI_vN.json`, `RAPORLAR/KURGU_P*_tN.json` | Seyirci eşikleri; KRİTİK 0; kesici önerilerinin ≥ %50'si uygulandı; kesmeden sonra Z1 yeniden temiz | B, A:habersiz-seyirci, A:kurgucu, A:kesici | yerel |
| **A17 Yayın** | Son kurgu, HIKAYE, KARARLAR.md | Jenerik, YouTube paketi, bölüm adları, kapak adayları → kör denetim, 3 Short, son kalite | `YAYIN/YOUTUBE_PAKETI.md`, `paket.json`, `KAPAK_*.jpg`, `SHORTS/*.mp4` | Başlık kalıbı (BK §1.6), ≤ 8 bölüm (RE `bolum_sayisi_max`), kapakta el/yazı/anatomi HATA 0; −14 LUFS | A:yayin-paketcisi, A:kare-tarifcisi, A:juri-uyesi (YouTube rolü seçer), B, K (yükleme) | yerel |
| **A18 Kapanış** | DEFTER, RAPORLAR, kullanıcı notları | Ders adaylarını kümele → terfi önerileri; evreni güncelle (izleyici özeti, kart, ses); arşiv talimatı | `BILGI/DERS_DEFTERI.jsonl`, `DERSLER_AKTIF.md`, `EVREN/<SERI>/IZLEYICI_OZETI.md` | Her terfide kanıt sayısı ve kaynak görev; kural dosyası değişikliği KARAR_DEFTERI'nde | A:ders-editoru → B; K (ARSIVLE.bat) | herhangi |

### 2.2 Aşamalar arası kurallar
1. **Kredi en sonda:** A00–A13 kredisizdir (görseller Gemini'de 0 kredi, BK §6.3.8). A14'ten önce A06, A07d, A11 ve A12 eşiklerinin
   hepsi geçmiş olmalı; `film.py` bunu `giris_sarti` alanıyla zorlar (BK §5.3.7: B1'de animatik onayı olmadan kredi yakıldı).
2. **Tek yazar ilkesi** (drama-skills "her belge yalnız kendi kararlarının sahibi", AR1 B2): `replik.metin` → hikâye yazarı;
   plan alanları → yönetmen; `ses` alanları → ses tasarımcısı (ayrı dosya, betik birleştirir); `SAHNELER.json`, `DUNYA_DURUMU.json`,
   `RAPORLAR/`, kuyruklar, `FILM_DURUM.json`, `EVREN/` → yalnız betik. Kanca bu kuralı zorlar (§6 K-3).
3. **Revizyonu aynı yazar yapar** (YR §1.4): aynı oturumda `SendMessage` ile aynı ajan örneği sürdürülür (D/agents: "Resumed
   subagents keep their full history"). Oturum kesildiyse yeni örnek açılır ve GIRDI'ye önceki sürüm + bütün raporlar + kendi
   "vN değişiklikleri" tabloları konur (rol sürekliliği hafızayla değil dosyayla).
4. **Değerlendirici her turda yenidir** (ZN §7.3): seyirci, jüri, oyuncu, kesici, kare tarifçisi asla `SendMessage` ile bir sonraki
   tura taşınmaz. Tek istisna: aynı turdaki animatik/kurgu izlemesinde **aynı seyirci** filmi bölüm bölüm izlemeye devam eder
   (bir seyircinin filmi baştan sona izlemesi doğaldır; bağlam sınırı yüzünden bölünür).
5. **Kapı döngüsü tavanı:** kâğıt 4, kurgu 3, görsel 2 tur (RE, UH §5). Tavan aşılırsa bkz. §9 açık soru S-3.
6. **Fiziksel iş ≠ soru:** Kullanıcı yalnız yapabileceği işler için (Gemini uygulamasına paket verme, Flow'da GÖNDER, CapCut'ta
   dışa aktarma, kredi yükleme, Flow uyarısını kendi gözüyle kontrol) talimat alır; ona karar sorulmaz. Talimat `.bat` adıyla verilir
   ve bitişi dosyadan algılanır (ZIP GELENLER'e düştü, NNN.mp4 indi).
7. **Bulut/yerel ayrımı:** Bulut oturumu yerel görevde durur: "Bu adım senin bilgisayarında; Claude'u orada açıp 'devam' de."
   Önerim: üretimin tamamı kullanıcının Windows'unda yürüsün, bulut yalnız geliştirme ve sahte test için kullanılsın (§9 S-1).

### 2.3 Kesilme ve kurtarma akışı
| Olay | Kanca / araç | Ne olur |
|---|---|---|
| Kullanım sınırı, API hatası | `StopFailure` (D/hooks: `error` = `rate_limit`, `overloaded`…; çıktısı yok sayılır ama yan etki yapılabilir) | `hata_kaydi.py`: koşan görevleri `kesildi` işaretler, FILM_KAYIT'a yazar, Telegram'a "sınır doldu; açılınca DEVAM.bat" gönderir |
| Sıkıştırma | `PreCompact` (günlük), `PostCompact` (`compact_summary` → `_GOREV/OTURUM_OZETLERI/`), `SessionStart` matcher `compact` | Durum özeti + değişmez kurallar `additionalContext` olarak geri gelir; beceri metninin ilk 5.000 tokenı zaten geri eklenir (D/skills) |
| Yeni oturum / devam | `SessionStart` `startup|resume|clear` | Aynı özet; aktif film varsa soru sorulmadan devam edilir |
| Ajan yarıda kaldı (maxTurns, sınır) | `film.py kurtar` | **Yazar** görevi: yarım CIKTI yeni görevin `GIRDI/YARIM/` klasörüne kopyalanır, aynı rol devam eder. **Değerlendirici** görevi: yarım çıktı arşive, görev sıfırdan, **yeni** örnekle (başka seyircinin yarım fikri okunmaz) |
| Paralel grubun bir kısmı bitti | Defter | Yalnız bitmeyenler yeniden çalışır; bitenler bağımsız olduğu için geçerli kalır |
| Kredili iş | Görev `istek_kimligi` = plan no + deneme no; "gönderildi" kaydı gönderimden **önce** yazılır | Kesilmeden sonra önce `memmet_topla` (yeni gönderim yok, BK §6.2.4), dosya yoksa ve gönderim kaydı varsa **kör yeniden gönderim yasak** → kullanıcı eylemi "Flow projesinde NNN var mı bak" |
| Biten görev | Defter `bitti` + çıktı imzası | Asla yeniden gönderilmez (superpowers: en pahalı hata "biten işi yeniden dağıtmak", AR3 B6) |
| Otomatik model geçişi | `PostModelSwitch` `source: auto` (D/hooks; kullanım sınırı model değiştirmez, D/model) | Kayıt. Alt ajanlar kendi `model: opus` alanıyla çalışır; geçiş bir alt ajanda görülürse o aralıkta biten görevi `model_sapmasi` işaretler ve yeniden kuyruğa koyar. Yalnız ana oturum değiştiyse görev yeniden çalışmaz (ana Claude içerik üretmez) |

---

## 3. Gereken ajanlar

### 3.1 Kadro ilkeleri (Claude Code düzeyinde)
1. **Ana Claude ajan değildir, set amiridir:** içerik üretmez, puan vermez, ajan çıktısını düzeltmez, plan dosyası yazmaz
   (YR §1: "Kendisi puan vermez; tarafsız kalır"). Bağlamını küçük tutar: büyük dosya yerine `film.py ozet/goster`.
2. **Düz yapı:** ajan ajan açmaz. `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` (D/agents: "Setting it to `1` turns nesting off").
   Her görev defterden geçsin diye bütün dağıtım ana Claude'dadır.
3. **En az araç:** değerlendiricilerde `Read, Write`; yazarlarda `Read, Write, Edit, Glob, Grep`. Hiçbir ajanda `Bash`, `Agent`,
   `WebFetch` yok (betik işleri betikte, AR3 B4 "deterministik işler betiğe"). Okuma/yazma yolu kancayla görev klasörüne bağlanır.
4. **Model:** hepsi `model: opus` + `effort: high` (H/ajan-opus-yuksek: kullanıcı açıkça istedi; karar 6). YR §1'deki "Sonnet: süreklilik,
   istem, müzik, YouTube" tablosu bu karar nedeniyle geçersiz. `fallbackModel` ayarlanmaz: D/model'e göre yedek zinciri yalnız bir
   tur sürer ve `PostModelSwitch` tetiklemez, yani sessizce başka modelle iş yapılmış olur. Kullanım sınırı model değiştirmez (D/model).
5. **`memory:` alanı hiçbir ajanda yok.** Habersiz seyirci hafıza tutarsa habersiz olmaz; dersler dosyayla ve `SubagentStart`
   kancasıyla (yalnız yazar ve denetçilere) verilir (§8 özellik e).
6. **Kör ajanlarda `omitClaudeMd: true`** (D/agents; v2.1.271+): seyirci depo kurallarını da, filmin yapım planını da bilmez.
7. **Çıktı sözleşmesi:** her ajan (a) `CIKTI/` altına önce başlıkları yazar, sonra bölüm bölüm doldurur (kesilirse yarım iş kalır),
   (b) makinece okunur bir `.json` yazar, (c) son satıra sabit `OZET | …` koyar, (d) ana Claude'a ≤ 5 satır döner: çıktı yolu + OZET
   (YR §4 "5 satırlık özet dön"). Puanı mesajdan değil dosyadan betik okur.
8. **Görev dışı bilgi yok:** alt ajan sohbeti görmez (D/agents). Bu bir avantaj: devretme mesajı yalnız
   `"Görevin: <yol>/GOREV.json — önce onu oku, yalnız orada yazanı yap."` olur. Her şey GOREV.json + ISTEM.md + GIRDI'dedir.

### 3.2 Tam kadro (15 ajan)

**Yazarlar** (sahip oldukları dosyayı yazarlar; revizyonu da onlar yapar)

| Ajan | Model / araçlar | Görev (sınırı) | Okuyacakları (GIRDI kopyası) | Çıktısı |
|---|---|---|---|---|
| `yapimci` | opus·high · Read, Write | A01: format, süre, ton, seri/evren, kanca, NE YOK taslağı, mimar tonları. **Yapmaz:** hikâye yazmaz | 00_KONU, KARARLAR.md, BK §1–2 §7, ZN §0, RE özeti, EVREN dizini, DERSLER_AKTIF | `PROJE_KARARLARI.md`, `proje.json`, `kararlar.jsonl` (her biri: karar—neden—yanlışsa maliyeti) |
| `hikaye-mimari` | opus·high · Read, Write | A03: tek tonda tam öneri. **Yapmaz:** başka öneri okumaz, birleştirmez | Brifing, ton, ZN §0–1 §4, BK §2 | `oneri_X.md` + `oneri_X.json` |
| `hikaye-yazari` | opus·high · Read, Write, Edit, Glob, Grep | A05–A06: birleştirme, sahne sahne senaryo, bütün revizyonlar, `HIKAYE.json`. **Replik metninin tek sahibi** | Öneriler, jüri, seyirci/oyuncu raporları, ZN §1 §4 §7, BK §2 | `HIKAYE_vN.md`, `HIKAYE.json`, `vN_DEGISIKLIKLER.md` |
| `yonetmen` | opus·high · Read, Write, Edit, Glob, Grep | A07: parti haritası, sahne grubu planları, revizyon, **onarım** (filtre reddi, CORRECTION), yeniden çekim. Eski `istem-muhendisi` işinin yargı kısmı buraya taşındı. **Yapmaz:** replik metnini değiştirmez (yalnız böler/zamanlar; değişiklik gerekiyorsa `replik_degisiklik_istegi` yazar) | HIKAYE dilimi, harita, evren kimlik dizeleri, ZN §2–3, AR2 §2.3 §6.1, RE | `HARITA_Pn.json`, `PLANLAR/Sxx.json`, `ONARIM_*.json` |
| `ses-tasarimcisi` | opus·high · Read, Write | A08: plan `ses` alanları, ambiyans zemini, efekt listesi, müzik ipuçları, leitmotif, plan başına ses yöntemi. Eski `muzik-supervizoru`nun yerine | SAHNELER dilimi, HIKAYE özeti, ZN §5, BK §5, ses uzmanının kural dosyası | `SES_Sxx.json`, `leitmotifler.json`, `muzik_listesi.json`, `EKSIK_EFEKT.json` |
| `kurgucu` | opus·high · Read, Write, Edit | A12/A16: seyirci ve kesici raporlarını kurgu değişikliğine çevirir (sıra, kırpma, J/L, bağlayıcı plan isteği). **Yapmaz:** CapCut dosyasına dokunmaz; öneri dosyası yazar, betik uygular | KURGU_PLANI, raporlar, ZN §2.2 §3.4 §5 | `KURGU_DEGISIKLIK_tN.json` |
| `yayin-paketcisi` | opus·high · Read, Write | A17: başlık (3 aday), açıklama, bölüm adları (merak cümlesi, ≤ 8), etiketler, kapak istemleri, 3 Short aralığı, jenerik metni | HIKAYE özeti, KURGU zaman çizelgesi, KARARLAR.md, BK §1.6–1.8, ZN §1.4 | `YOUTUBE_PAKETI.md`, `paket.json` |
| `ders-editoru` | opus·high · Read, Write | A18: ders adaylarını kanıtla terfi ettirir ya da reddeder. **Yapmaz:** kural dosyası yazmaz; yama önerir, betik uygular | `DERS_ADAYLARI.json` (betik kümeler), kapı istatistikleri, kullanıcı notları | `TERFI_ONERILERI.json` |

**Değerlendiriciler** (her turda yeni örnek; birbirini okumaz)

| Ajan | Model / araçlar | Görev (sınırı) | Okuyacakları | Çıktısı |
|---|---|---|---|---|
| `habersiz-seyirci` | opus·high · Read, Write · `omitClaudeMd` | Kipler: `kagit` (senaryo/plan kör paketi), `ilk2dk`, `izleme` (kare paketi). 6 ölçüt + kopukluk + sıkıldığım anlar + açık sorular + 3 cümle özet (ZN §7.3). **Bilmez:** amaç, risk, vuruş, merak defteri, `ekranda_bilgi`, zanaat kuralları, önceki turlar | Yalnız GIRDI/PAKET (betik üretir) + `IZLEYICI_OZETI.md` (önceki filmler) | `rapor.md`, `rapor.json`, OZET satırı |
| `juri-uyesi` | opus·high · Read, Write | A04 rolleri (`ilk_kez_izleyen`, `youtube_stratejisti`, `tur_uzmani`, `duygu_elestirmeni`), A06 `ozet_eslestirme` kipi (seyirci özeti ↔ `ana_olgular`), A17 kapak/başlık seçimi | Öneriler + jüri tablosu / eşleştirme listesi / aday listesi | `juri_N.md` + OZET; `eslesme.json` |
| `oyuncu` | opus·high · Read, Write · `omitClaudeMd` | Tek karakterin repliklerini kendi kartına göre okur: "bunu böyle söylemez", "bunu bilemez", "bildiğin gibi" hatası (ZN §7.2.5, AR1 A1) | Karakter kartı + yalnız o karakterin replikleri ve bir önceki replik | `oyuncu_<ad>.json` |
| `uretilebilirlik-denetcisi` | opus·high · Read, Write | A04 ve A07d: çekilemez fikir, filtre riski, ≤ 2 referans, 2–3 adım sığar mı, ölçek, el/parmak ayrıntısı; kanıtla bilinen çalışan şeyi yasaklamaz (YR A5). **Kredi hesabı yapmaz** (betik yapar) | Öneriler ya da plan dilimi, DR, BK §6 | `uretilebilirlik.json` + OZET |
| `sureklilik-denetcisi` | opus·high · Read, Write | (1) Kâğıt: betiğin yakalayamadığı anlam hataları (dönem/NE YOK, olanaksız yer değiştirme, mantık). (2) **Hakem:** G1/V2'de kör tarif ile beklenen arasında BAYRAK kalan kareler için karar + CORRECTION cümlesi | Plan dilimi + DUNYA_DURUMU dilimi; hakemde kare + beklenen + kör tarif | `sureklilik.json` (KRİTİK/ORTA/KÜÇÜK) |
| `kare-tarifcisi` | opus·high · Read, Write · `omitClaudeMd` | **Kör** görüntü dökümü (ARIS `panel_gate`, AR1 B4): beklenen değeri görmeden seçenekli sorulara cevap ("Fener kadının hangi elinde? A) sol B) sağ C) yok D) görünmüyor"). Kartlarda, başlangıç karelerinde, kapakta | Yalnız görseller + `SORU_FORMU.json` (betik üretir, cevapsız) | `tarif.json` |
| `kesici` | opus·high · Read, Write · `omitClaudeMd` | A16 sonu: "Hangi 10 planı ya da 2 sahneyi atarsak film daha iyi olur?" (ZN §7.2.9, RE `kesme_turu_oneri`) | Kurgu kör kare paketi + süreler | `kesme_onerileri.json` |

**Kaldırılan / birleştirilen:** `istem-muhendisi` → istemler kodla derlenir (`istem_derle.py`, ZN §6.1 "kodla derlenir", AR1 B3
"bir kez yaz, kelimesi kelimesine tekrarla"); yargı gerektiren onarım `yonetmen` onarım kipine. `muzik-supervizoru` → `ses-tasarimcisi`.

### 3.3 Mevcut 8 taslağın eksik ve yanlışları

| Taslak | Sorun | Düzeltme |
|---|---|---|
| **Hepsi** | `effort` alanı yok (kullanıcı "opus yüksek efor" istedi); `maxTurns` yok; çıktı yolları dağınık (`_HIKAYE_ODASI`, `_YONETMEN/05_PLANLAR.json`, `_RAPOR`, `KURGU/`) ve ZN'deki `RAPORLAR/` ile çelişiyor; yalnız OZET satırı var, JSON çıktı sözleşmesi yok; "dosyayı erken oluştur, bölüm bölüm doldur" kuralı yok; açıklamalar eski YR aşama kodlarına (A2, A5, A8) bağlı; `FILMLE ILGILI CLAUDE/…` yolları Windows kurulumunda bulunmayabilir | Ortak gövde kalıbı: rol → "Çağrıldığında" adımları → kontrol listesi → çıktı sözleşmesi (AR3 B5, öneri 10); bütün yollar görev klasörüne göreli; kurallar yalnız `.claude/skills/film-yap/` altından |
| `habersiz-seyirci` | `Glob` var → başka dosyaları keşfedebilir (bağımsızlık ve habersizlik bozulur). 3 ölçüt + ORTALAMA; ZN §7.3 6 ölçüt + GENEL + medyan istiyor. `ilk2dk` kipi, açık sorular, sıkıldığım anların zaman kodu, 3 cümle özet yok. "Önceki turları bilmiyorsun" yazmıyor. CLAUDE.md'yi okuyor | `tools: Read, Write`; `omitClaudeMd: true`; ZN §7.3 biçimi; kanca yalnız GIRDI'ye izin verir |
| `hikaye-mimari` | "Parti ≈ 80–100 klip" ZN §2.6 (P1 165 plan, ≈ 135 klip/parti) ile çelişiyor; "en çok 4 konuşan" RE `konusan_karakter_max: 8` ile çelişiyor; duygu haritası, vuruş oranı, merak defteri, kurulumlar, ironi, sahne değeri yok (ZN §7.4 hikâye odasının sorumluluğu); `Glob/Grep/Edit` ile diğer önerileri okuyabilir; v2'yi mimarın yazması birleştirme rolüyle karışıyor | Sayılar şablona RE'den betikle basılır (ajana sabit sayı yazılmaz); v2 ve sonrası `hikaye-yazari`'na |
| `istem-muhendisi` | İstemleri elle yazıyor (sapma kaynağı); `parti`yi 20'lik üretim bloğu sayıyor (BK §8 #14 çelişkisi: hikâye partisi ≠ üretim partisi); dosya taşıma işini ajan yapıyor (`ESKI_GORSEL`'e taşı) | Kaldır → `istem_derle.py` + `yonetmen` onarım kipi; dosya işleri `yeniden_uret` betiğinde |
| `muzik-supervizoru` | `sonnet` (ses tasarımı kullanıcının "opus" listesinde); `bas_sahne/bitis_sahne` plan numarası, sahne grubu yok; ambiyans/efekt tasarımı, sessizlik süreleri, müzik kaplama oranı, giriş/çıkış kuralları (ZN §5) yok | `ses-tasarimcisi` |
| `sureklilik-denetcisi` | `sonnet` (denetim kullanıcının "opus" listesinde); görsel kipte beklenen listeyi görerek karar veriyor (ARIS dersi: önce kör döküm, sonra deterministik karşılaştırma, AR1 B4); 405 kareyi tek ajana veriyor (bağlam sınırı); `YENIDEN_URET.json`'u kendisi yazıyor (makine kuyruğu) | Kör döküm `kare-tarifcisi`'ne, karşılaştırma betiğe; bu ajan yalnız anlam denetimi + BAYRAK hakemi; kuyruğu betik yazar |
| `uretilebilirlik-denetcisi` | Kredi tahmini "%25 pay" (RE: %20) ve LLM'e hesaplatılıyor; atomik zincir/el-parmak sığma denetimi yok; `sonnet` | Kredi `maliyet.py`'de; opus |
| `yayin-paketcisi` | `KURGU/son_capcut_projesi.json` diye bir dosya yok; bölüm adı kuralı (merak cümlesi, ≤ 8, parti/vuruş sınırı, ZN §1.4) yok; Shorts ölçüleri (30–60 sn, ilk 2 sn kanca, BK §1.8/§3.10) yok; kapağı "kullanıcı seçer" varsayımı karar 1 ile çelişiyor | Zaman çizelgesi `film.py goster zaman`dan; kapak seçimi kör tarif + jüri |
| `yonetmen` | **Atomik eylem zinciri yok**, "tek hareket" diyor (karar 2 ile çelişki); ZN §6.1 alanları (plan_tipi, sure_sn, kadraj sözlüğü, kamera_tarafi, kesme, baslangic/bitis_durumu, eylem_zinciri, replik_zaman, ekran_disi_ses) ve AR2 §6.1 `sureklilik` alanları yok; istemleri elle yazıyor; 495 planı tek çağrıda yazmaya kalkıyor (çıktı sınırı); stil son eki gövdeye gömülü (evrende olmalı) | Sahne grubu başına görev; yapılandırılmış alan; istem kodla |

### 3.4 Örnek tanım: `habersiz-seyirci.md` (önerilen tam metin, kısaltılmış gövde)
```markdown
---
name: habersiz-seyirci
description: Filmi hiç bilmeyen, ilk kez izleyen YouTube seyircisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kâğıt, ilk-2-dakika ya da kare paketi izleme kipinde puan ve kopukluk raporu yazar. Her turda yeni örnek açılır; önceki tur seyircisi sürdürülmez.
tools: Read, Write
model: opus
effort: high
maxTurns: 60
omitClaudeMd: true
color: cyan
---
Sen bu filmi İLK KEZ izleyen sıradan bir izleyicisin. Filmin planını, yazarların niyetini ve yapım kurallarını bilmiyorsun.
Yalnız GOREV.json'da adı geçen GIRDI dosyalarını okursun. Başka bir dosyayı açmaya çalışma; sistem engeller.

Çağrıldığında:
1. GOREV.json'u oku (kip: kagit | ilk2dk | izleme; çıktı yolları; tur).
2. CIKTI/rapor.md dosyasını hemen başlıklarıyla oluştur; her bölümü bitirdikçe doldur.
3. Paketi baştan sona sırayla "izle"; ilerideki kısımlara atlama. ...
4. ... (ZN §7.3 ölçütleri, kopukluk tablosu, sıkıldığım anlar, açık sorular, 3 cümle özet)
5. CIKTI/rapor.json'u şemaya göre yaz; rapor.md'nin son satırı:
   OZET | anlasilirlik: _ | akicilik: _ | merak: _ | duygu: _ | ritim: _ | ilk30: _ | GENEL: _ | KRITIK: _ | ORTA: _
6. Ana oturuma yalnız iki satır dön: CIKTI yolu ve OZET satırı.
```

### 3.5 Örnek tanım: `yonetmen.md` başlığı
```markdown
---
name: yonetmen
description: Filmin yönetmeni. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; parti haritası, sahne grubu plan listesi (atomik eylem zinciri, başlangıç/bitiş durumu), plan revizyonu, filtre/CORRECTION onarımı ve yeniden çekim planı yazar.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 80
color: purple
---
KESİN KURAL (her planda): YZ'ye sonuç söylenmez. eylem_zinciri 2–3 saniyeli adım; her adım tek fiil + yön/hedef + vücut
parçası + taraf (sol/sağ) + parmak; baslangic_durumu = başlangıç karesi; bitis_durumu = sonraki planın baslangic_durumu.
Yasak sonuç fiilleri listesi GOREV.json'dadır (RE'den betikle basılır). hareket_istem ve gorsel_istem YAZMAZSIN: kod derler.
...
```

---

## 4. Beceri (skill) tarif adımları

### 4.1 Kaç beceri, neden
**4 beceri.** Aşama başına ayrı beceri yazmıyorum: kullanıcı yalnız konu verdiği için `/…uret` gibi komutları kimse yazmayacak;
`disable-model-invocation: true` taşıyan bir beceriyi Claude kendisi açamaz (D/skills). Aşama ayrıntısı ise ana Claude'un değil
ajanın işidir ve betiğin doldurduğu şablonlarda durur. Ana Claude'un bağlamına giren beceri metni küçük kalır.

| Beceri | Kim açar | Rol | Neden ayrı |
|---|---|---|---|
| `film-yap` | Claude (otomatik) + `/film-yap` | Set amiri döngüsü | Ana iş |
| `film-durum` | Claude + `/film-durum` | Soru = sadece cevap (H/soru-sadece-cevap) | Salt okunur kalmalı: `disallowed-tools` ile yazma araçları o tur kapalı |
| `film-not` | Claude + `/film-not` | Kullanıcı notu / CapCut düzenlemesi → görev | Kullanıcının kurgu kararı korunur (BK §5.3.3); ayrı akış |
| `film-gelistir` | yalnız `/film-gelistir` (`disable-model-invocation: true`) | Sistemi değiştirme (araç, ajan, test) | Film yaparken kod değişmesin |

Sıkıştırmada her becerinin ilk 5.000 tokenı geri eklenir, toplam bütçe 25.000 token (D/skills) → 4 beceri sığar.

### 4.2 Frontmatter metinleri (karakter sayıları ölçüldü)

**`film-yap`** (description 574 kr; + when_to_use = 910 kr ≤ 1.536)
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
  Örnekler: "Ejderha büyüten bir kadın hakkında film yap" · "konu: uzaylı çocuğa babalık eden asker" · "devam" ·
  "sınır açıldı, devam et" · "Gemini zipini GELENLER'e koydum". Kullanıcı SORU soruyorsa (ne durumda, neden durdu,
  kaç kredi, istemde ne yazıyor) film-durum; not, şikâyet ya da kendi CapCut düzenlemesi için film-not kullanılır.
argument-hint: "[film konusu | devam]"
effort: high
allowed-tools: Bash(python .claude/bin/film.py *)
---
```
**`film-durum`** (406 / 587 kr)
```yaml
---
name: film-durum
description: >-
  Film hakkında soru soran kullanıcıya yalnız cevap verir; dosya değiştirmez, ajan çalıştırmaz, üretim başlatmaz.
  Use when the user asks a question about the film or the system: "ne durumda", "hangi aşamadayız", "neden durdu",
  "kaç kredi lazım", "promptta ne yazıyor", "şu sahnede ne oluyor", "ne zaman biter", "what's the status", or any
  message that ends with a question mark and does not ask for a change.
when_to_use: >-
  Soru = sadece cevap kuralı (kullanıcı kesin istedi). Cevaptan sonra en çok bir cümle öneri: "İstersen şunu yaparım".
  Kullanıcı bir değişiklik ya da devam isterse film-yap'a dönülür.
disallowed-tools: Write, Edit, NotebookEdit, Agent
allowed-tools: Bash(python .claude/bin/film.py * ozet*), Bash(python .claude/bin/film.py * goster*)
---
```
**`film-not`** (374 / 521 kr)
```yaml
---
name: film-not
description: >-
  Kullanıcı animatik, CapCut taslağı ya da bitmiş film hakkında not, şikâyet veya kendi yaptığı düzenlemeyi
  bildirdiğinde notları salt okunur okur, karar ve ders defterine işler, düzeltme görevlerine çevirir. Use when the
  user says "notlar hazır", "CapCut'ta değiştirdim kontrol et", "şu sahne kopuk", "ses kaymış", "beğenmedim",
  "şunu kes", or describes a problem in a draft.
when_to_use: >-
  Kullanıcının kurgu kararı aynen uygulanır, taslak yeniden kurulmaz (dosyalar yerinde değişir). Notlar işlendikten
  sonra film-yap döngüsüne dönülür.
---
```
**`film-gelistir`** (244 kr): `disable-model-invocation: true`; "Film setinin kendisini (ARACLAR betikleri, sağlayıcılar, kancalar,
ajan ve beceri dosyaları, testler) değiştirmek için geliştirici kipi…"

### 4.3 `film-yap/SKILL.md` gövdesi (satır bütçesi ve sıra)
**Bütçe:** toplam ≤ 250 satır (sınır 500, D/skills). **İlk 110 satır = çekirdek** (≤ 4.500 token, tahmin): sıkıştırmadan sonra
geri gelen kısım budur, kurallar ve döngü burada olmalı (AR3 B4). Ayrıntı tek seviye referans dosyalarına (AR3 B4).

```markdown
# FİLM YAP — set amiri döngüsü

## 0. Şu anki durum (beceri açılırken betik yazar)
!`python .claude/bin/film.py ozet --kisa`

## 1. Değişmez kurallar (her turda geçerli; kancalar da zorlar)
1. Kullanıcıya YALNIZ filmin konusu sorulur. Diğer bütün kararları ekip verir ve KARAR_DEFTERI'ne yazılır
   (`film.py karar ekle "karar — neden — yanlışsa maliyeti"`). "Hangisini istersin / onaylıyor musun" YOK.
2. Kullanıcıdan yalnız onun yapabileceği FİZİKSEL iş istenir (Gemini'ye paket, Flow'da GÖNDER, kredi yükleme).
   Talimatı film.py verir; aynen, adım adım, .bat adıyla ilet.
3. Flow "olağan dışı etkinlik" / doğrulama → hat durur. Yeniden başlatma, atlatma, fare/klavye taklidi YOK.
4. Gizli bilgi (AYARLAR) okunmaz, yazdırılmaz, kopyalanmaz.
5. Sen içerik üretmezsin, puan vermezsin, ajan çıktısını düzeltmezsin, plan/rapor dosyası yazmazsın. Yalnız dağıtırsın.
6. Büyük dosya açma (SAHNELER.json vb.). Bilgi gerekiyorsa: `film.py goster <ne>`.
7. Hafızana değil film.py'ye güven. Bir işi bitti sanıyorsan `film.py sonraki` ne diyorsa o doğrudur.
8. Kullanıcı soru sorarsa film-durum; not verirse film-not. Soruya işlemle cevap verme.
9. Kredi harcayan iş yalnız bütçe kapısı geçtiyse (film.py karar verir). Kalite kısılmaz; bütçe yoksa dur ve söyle.
10. Kalıcı silme yok (geri dönüşüm kutusu); robocopy /MIR yok.

## 2. Döngü
1. `python .claude/bin/film.py sonraki` → JSON görev listesi.
2. `python .claude/bin/film.py basla <id,id,…>`
3. tur=ajan → aynı paralel_grup'taki bütün görevler İÇİN TEK MESAJDA Agent çağır:
   subagent_type=<ajan>, prompt = görevdeki `istem` alanı AYNEN (yalnız GOREV.json yolu).
   Değerlendirici görevler daima yeni örnek; `ornek: ayni_yazar` ise önce SendMessage ile o ajanı sürdür,
   ajan kimliği yoksa yeni örnek aç (GIRDI'de geçmiş vardır).
4. tur=betik → yalnız görevdeki `komut`u çalıştır.
5. tur=kullanici_eylemi → `mesaj`ı aynen kullanıcıya ilet ve turu bitir. Soru ekleme.
6. tur=bekle → nedeni bir cümleyle söyle, turu bitir.
7. tur=bitti → `film.py ozet --kullanici` çıktısını ilet.
8. Ajan döndü → kanca doğrular; dönen "sıradaki" bağlamına göre 1'e dön. Doğrulama "gecersiz" derse
   film.py yeni deneme görevini verir; sen düzeltme yazma.

## 3. Kullanıcıyla konuşma
Türkçe, kısa, teknik terim yok (gerekirse bir cümleyle açıkla: cold open, cliffhanger). Her ilerlemede en çok 3 satır:
ne bitti · şimdi ne oluyor · senden bir şey gerekiyor mu (yalnız fiziksel iş).

## 4. Takılırsan
- film.py `takildi` derse: KURTARMA.md'yi oku, yazanı uygula.
- Kanca bir işlemi engellediyse: engel gerekçesini oku, kuralı çiğneme; gerekirse `film.py sonraki`.
- Kullanım sınırı / kesilme: hiçbir şey yapma; yeniden açılınca döngü kaldığı yerden sürer.
--- (çekirdek sonu) ---
## 5. Referanslar (yalnız film.py `oku` alanında gösterirse ya da takılınca)
- KURTARMA.md · GOREV_SEMASI.md · KULLANICI_DILI.md (talimat kalıpları, kavram sözlüğü)
- BILGI_KURALLARI.md · ZANAAT.md · ritim_esikleri.json (ajan şablonları bunları GIRDI'ye koyar; ana Claude okumaz)
```
**Referans dosyaları** (hepsi `film-yap/` altında, SKILL.md'den tek seviye, 100 satırı aşanın başında içindekiler, AR3 B4):
`KURTARMA.md`, `GOREV_SEMASI.md`, `KULLANICI_DILI.md`, `sablonlar/<asama>_<ajan>.md` (ajan istem şablonları; betik doldurur),
`semalar/*.json` (çıktı şemaları), mevcut `BILGI_KURALLARI.md`, `ZANAAT.md`, `ritim_esikleri.json`, `arastirma/`.
`tartisma/` klasörü üretimde kullanılmaz (tasarım tartışması).

### 4.4 Diğer becerilerin adımları
**film-durum** (≤ 60 satır)
1. `!`python .claude/bin/film.py surus kapat`` — otomatik sürüşü bu tur kapatır (§6 K-9). Komut hata vermez (D/skills: başarısız
   `!` komutu beceriyi iptal eder → sarmalayıcı daima 0 ile çıkar).
2. Soruya göre: `film.py ozet --uzun` · `film.py goster plan 042` · `film.py goster maliyet` · `film.py goster neden-durdu`.
3. Cevap: düz Türkçe, ≤ 6 satır, sayı varsa kaynağıyla. Son satır en çok bir öneri ("İstersen … yaparım"). İşlem yok.

**film-not** (≤ 120 satır)
1. `film.py notlar oku` → `notlari_oku.py` + `taslak_fark.py` salt okunur (BK §5.3.3); kullanıcı CapCut'ta düzenlediyse fark listesi.
2. Her notu sınıfla: (a) kullanıcının kendi kurgu kararı → **aynen** `KURGU_DEGISIKLIK` (taslak yeniden kurulmaz);
   (b) şikâyet → hangi kapı bunu yakalamalıydı (`film.py ders ekle --kapi K1 --belirti "…"`); (c) yeni sahne isteği → yönetmen görevi.
3. `film.py karar ekle "Kullanıcı notu N: … — uygulanacak"`; `film.py notlar isle` → yeniden iş görevleri.
4. Kullanıcıya: "Notlarını aldım: N düzeltme. Bitince yine CapCut'ta aynı projede göreceksin." (soru yok) → film-yap döngüsü.
5. Kesmeden sonra Z1 kurulum denetimi yeniden çalışır (DR: "kullanıcının kestiği plan bir bilgiyi de götürebilir").

**film-gelistir** (≤ 150 satır): `YZ_FILM/ARACLAR/CLAUDE.md`'yi oku → değişiklik → `python -m unittest discover -s YZ_FILM/ARACLAR/testler`
→ `film.py beceri-denetim` → küçük commit. Anahtar dosyalarına dokunma.

### 4.5 Kök `CLAUDE.md` akışı (önerilen tam metin, ≤ 45 satır)
Mevcut kök CLAUDE.md'nin "İlk iş: PAKET.zip'i aç" satırı **bayat** (zip e962e6a'da açılıp silindi); yeni bir oturum olmayan dosyayı
açmaya çalışır. Geliştirme listesi `YZ_FILM/ARACLAR/CLAUDE.md`'ye taşınmalı (alt klasör CLAUDE.md'si yalnız o klasörde çalışırken
yüklenir; film setini açan Claude'un bağlamını doldurmaz).
```markdown
# YZ FİLM SETİ
Bu klasör bir YZ film setidir. Kullanıcı Türkçe konuşur, teknik bilgisi azdır.

## Açılışta
Oturum başında "FİLM SETİ DURUMU" bağlamı gelir (kanca). Gelmediyse: `python .claude/bin/film.py ozet`.
- Aktif film YOK ve kullanıcı konu vermediyse YALNIZ şunu sor: "Filmin konusu ne olsun? Bir cümle yeter."
- Kullanıcı konu verdiyse ya da aktif film VARSA: soru sormadan film-yap becerisiyle devam et.

## Her zaman
- Kullanıcıya yalnız konu sorulur; diğer kararları ekip verir (KARAR_DEFTERI).
- Kullanıcı soru sorarsa yalnız cevap ver (film-durum). Not verirse film-not.
- Flow "olağan dışı etkinlik" ya da doğrulama → dur, haber ver. Atlatma, fare/klavye taklidi yok.
- AYARLAR/ gizli: okuma, yazdırma, kopyalama yok. Kalıcı silme yok. robocopy /MIR yok.
- Durum hafızada değil: `film.py` ve dosyalar doğrudur.

## Sistemi değiştirmek
Yalnız kullanıcı /film-gelistir derse. Ayrıntı: YZ_FILM/ARACLAR/CLAUDE.md
```

---

## 5. Veri şeması / plan alanları

### 5.1 Film klasörü (kanonik düzen; mevcut araçların klasör adları korunur)
```
FILMLER/_AKTIF.json                     {"film": "F20261023_ejderha", "degisti": "..."}   (betik)
FILMLER/<id>/
  00_KONU.md                            kullanıcının cümlesi, aynen (AC → betik yazar)
  FILM_DURUM.json · 00_DURUM.md         makine durumu · insan özeti (betik)
  KARAR_DEFTERI.md · FILM_KAYIT.txt     yalnız `film.py karar ekle` / betik
  _GOREV/DEFTER.jsonl · BAGLAR.json     görev defteri (append-only) · ajan_id ↔ görev bağı (kanca)
  _GOREV/G0041/ {GOREV.json, ISTEM.md, GIRDI/, CIKTI/}
  10_PROJE/ 20_HIKAYE/ 30_YONETMEN/ 35_SES/            yazar ajanların kopyalanmış çıktıları (betik taşır)
  SAHNELER.json · DUNYA_DURUMU.json                     betik (Memmet/capcut_film uyumu için SAHNELER korunur)
  RAPORLAR/<kapi>_<parti>[_tN].json · YENIDEN_YAZ.json · YENIDEN_URET.json   betik (ZN §6.2; `_RAPOR` → `RAPORLAR`)
  01_KARAKTERLER/ SIRALI_GORSEL/ SIRALI_VIDEO/ SESLER/ KURGU/ YAYIN/ GELENLER/   mevcut adlar
YZ_FILM/EVREN/<SERI>/ ...               seri evreni kütüphanesi (yalnız evren.py yazar)
YZ_FILM/BILGI/DERS_DEFTERI.jsonl · DERSLER_AKTIF.md   ders defteri (yalnız ders_defteri.py yazar)
```
SAHNELER.json büyür (≈ 495 plan × 3–5 KB ≈ 1,5–2,5 MB, tahmin); ne ana Claude ne ajan bütününü okur. Ajanlar `dilim.py`'nin
çıkardığı parçayı GIRDI'de alır.

### 5.2 `GOREV.json` (görev sözleşmesi)
```json
{
  "id": "G0041", "film": "F20261023_ejderha", "asama": "A06", "tur_no": 2, "parti": null,
  "tur": "ajan", "ajan": "habersiz-seyirci", "kip": "kagit",
  "ornek": "yeni",                         "paralel_grup": "A06_t2_seyirci",
  "ortam": "herhangi",                      "kredili": false,
  "istem": "Görevin: FILMLER/F20261023_ejderha/_GOREV/G0041/GOREV.json — önce onu oku, yalnız orada yazanı yap.",
  "talimat": "ISTEM.md",
  "girdi": ["GIRDI/PAKET_FILM.md", "GIRDI/IZLEYICI_OZETI.md"],
  "cikti": {"rapor": "CIKTI/rapor.md", "veri": "CIKTI/rapor.json"},
  "gecme_sarti": {"dosyalar_var": true, "sema": "seyirci_rapor_v1", "son_satir": "^OZET \\|"},
  "tasima": [{"kaynak": "CIKTI/rapor.json", "hedef": "20_HIKAYE/seyirci/t2_s1.json"}],
  "bagimlilik": ["G0038"], "deneme": 1, "en_cok_deneme": 3,
  "durum": "hazir", "ajan_id": null, "basladi": null, "bitti": null,
  "yarim_davranisi": "sifirdan"             
}
```
`yarim_davranisi`: değerlendiricide `sifirdan`, yazarda `devam_et` (§2.3). `durum`: `hazir | calisiyor | bitti | gecersiz | kesildi | iptal | model_sapmasi`.

### 5.3 `film.py sonraki` çıktısı (ana Claude'un tek okuduğu şey)
```json
{"film": "F20261023_ejderha", "asama": "A06 Kâğıt döngüsü", "tur_no": 2,
 "gorevler": [
   {"id": "G0041", "tur": "ajan", "ajan": "habersiz-seyirci", "paralel_grup": "A06_t2_seyirci", "istem": "Görevin: …/G0041/GOREV.json — önce onu oku…"},
   {"id": "G0042", "tur": "ajan", "ajan": "habersiz-seyirci", "paralel_grup": "A06_t2_seyirci", "istem": "…"},
   {"id": "G0043", "tur": "ajan", "ajan": "habersiz-seyirci", "paralel_grup": "A06_t2_seyirci", "istem": "…"}],
 "kullaniciya": null, "oku": null}
```
Kullanıcı eylemi örneği:
```json
{"id": "G0310", "tur": "kullanici_eylemi", "ortam": "yerel",
 "mesaj": "1) Masaüstü\\GEMINI GORSEL ISTEM\\F20261023_P1_1 klasörünü Gemini'ye ver.\n2) Gelen ZIP'i FILMLER\\F20261023_ejderha\\GELENLER içine koy.\nBen ZIP'i görünce kendim devam ederim.",
 "algilama": {"tur": "dosya_var", "desen": "GELENLER/*P1_1*.zip"}, "bat": null}
```

### 5.4 `FILM_DURUM.json` v2 (mevcut `asamalar` yapısı korunur, yeni alanlar eklenir)
```json
{
  "surum": 2, "film": "F20261023_ejderha", "seri": "EMBERFALL",
  "aktif_asama": "A06", "otomatik_surus": true,
  "asamalar": {"A05": {"zaman": "2026-10-23 14:02:11", "imza": "9f2c…", "sonuc": "GEC"}},
  "donguler": {"A06": {"tur": 2, "tavan": 4, "medyanlar": [{"tur": 1, "GENEL": 6.5, "KRITIK": 2}], "yazar_ajan_id": "a1b2…"}},
  "kilitler": {"flow_uyari": null, "butce": {"gerekli": 5800, "mevcut": null}},
  "bekleyen_kullanici": ["G0310"],
  "sayaclar": {"kullaniciya_soru": 1, "kanca_engeli": 0, "ajan_cagrisi": 57},
  "model_sapmasi": []
}
```

### 5.5 `KARAR_DEFTERI.md` satırı (superpowers "Ruling", AR3 B6)
```
- 2026-10-23 14:05 · A04 · Öneri B kazandı (medyan 8,1 > A 7,4) — jüri 4/5 B'yi ilk sıraya koydu — yanlışsa maliyeti: A06'da 1–2 ek tur · kaynak: G0019–G0023 · karar veren: betik (puan_oku)
```

### 5.6 `DERS_DEFTERI.jsonl` satırı ve terfi
```json
{"id": "D0137", "zaman": "2026-10-23T15:10", "film": "F20261023_ejderha", "kaynak": "kapi:K1|kullanici_notu|yeniden_uretim",
 "belirti": "Kapı sahnesinde ambiyans zıpladı", "kok_neden": "sahne grubunda iki ayrı ambiyans dosyası",
 "kural_onerisi": {"tur": "makine", "hedef": "ritim_esikleri.ambiyans_sahne_ici_fark_max_lu", "yama": null},
 "rol_etiketi": ["ses-tasarimcisi"], "kanit": ["G0412", "RAPORLAR/K1_P2.json"], "sayac": 3, "durum": "aday"}
```
Terfi kuralı (öneri): aynı `belirti` anahtarı ≥ 3 kez ya da ≥ 2 filmde → `ders-editoru`'ya gider **(tahmin eşik)**. Terfi iki
türlüdür: (1) **makine kuralı** (yasak kelime listesi, eşik) → betik yamayı uygular, test çalışır, KARAR_DEFTERI'ne yazar;
(2) **talimat dersi** → `DERSLER_AKTIF.md`'ye rol etiketiyle girer; `SubagentStart` kancası o role ait dersleri ajanın bağlamına
ekler (D/hooks: SubagentStart `additionalContext`). Kör ajanlara ders eklenmez.

### 5.7 Erişim politikası `.claude/kurallar/erisim.json`
```json
{
  "gizli": ["**/AYARLAR/*anahtar*", "**/AYARLAR/telegram_bot.txt", "**/AYARLAR/memmet_profil/**", "**/.env"],
  "makine_sahipli": ["**/FILM_DURUM.json", "**/_GOREV/DEFTER.jsonl", "**/_GOREV/BAGLAR.json", "**/_GOREV/*/GOREV.json",
                     "**/_GOREV/*/GIRDI/**", "**/SAHNELER.json", "**/DUNYA_DURUMU.json", "**/RAPORLAR/**",
                     "**/YENIDEN_YAZ.json", "**/YENIDEN_URET.json", "**/KARAR_DEFTERI.md", "**/EVREN/**",
                     "**/BILGI/DERS_DEFTERI.jsonl", "**/BILGI/DERSLER_AKTIF.md"],
  "roller": {
    "kor":    {"ajanlar": ["habersiz-seyirci", "oyuncu", "kare-tarifcisi", "kesici"],
               "okuma": ["{gorev}/GOREV.json", "{gorev}/ISTEM.md", "{gorev}/GIRDI/**", "{gorev}/CIKTI/**"],
               "yazma": ["{gorev}/CIKTI/**"]},
    "yazar":  {"ajanlar": ["yapimci", "hikaye-mimari", "hikaye-yazari", "yonetmen", "ses-tasarimcisi", "kurgucu", "yayin-paketcisi", "ders-editoru"],
               "okuma": ["{gorev}/**", ".claude/skills/film-yap/*.md", ".claude/skills/film-yap/*.json", ".claude/skills/film-yap/sablonlar/**"],
               "yazma": ["{gorev}/CIKTI/**"]},
    "denetci":{"ajanlar": ["juri-uyesi", "uretilebilirlik-denetcisi", "sureklilik-denetcisi"],
               "okuma": ["{gorev}/**", ".claude/skills/film-yap/*.md", ".claude/skills/film-yap/*.json"],
               "yazma": ["{gorev}/CIKTI/**"]}
  },
  "ana_claude": {"okuma_buyuk_dosya_kb": 200, "yazma_yasak": "makine_sahipli"}
}
```
`{gorev}` = kancanın `agent_id` ile bağladığı görev klasörü. **Bağlama:** ana Claude `film.py basla` ile görevi `calisiyor`
yapar; ajanın ilk araç çağrısı (GOREV.json'u okuma) `agent_id`'yi o göreve bağlar ("ilk okumada sahiplen"); aynı türden paralel
ajanlar ayrı görevlere bağlanır; bağlanmış göreve ikinci bir `agent_id` erişemez. `agent_id` / `agent_type` alanları PreToolUse
girdisinde vardır (D/hooks: "the input carries the `agent_id` and `agent_type` common input fields").
`tartisma/` ve `arastirma/` yazar rolüne açık değildir (tasarım belgeleri, üretim kuralı değil).

### 5.8 Kör paket alanları (`kor_paket.py`, beyaz liste)
| Verilir | Verilmez (sızıntı) |
|---|---|
| Zaman kodu, sahne/plan sırası; kadraj (düz sözle); atomik eylem zincirinin **görünür** adımları; replik metni ve kimin söylediği (ses yönü); ekran yazısı, yer/zaman kartı; ses ipucu (duyulan); önceki filmlerin `IZLEYICI_OZETI.md`'si; izleme kipinde kareler | `amac`, `duygu`, `hedef_duygu`, `yogunluk`, `vurus`, `risk`, `merak_ac/kapat`, `kurulum`, `kullanim_bilgi`, `ironi`, `ekranda_bilgi`, `sahne_degeri`, yönetmen notları, `gorsel_istem` ham metni, önceki tur raporları, puan geçmişi |

**Ad maskeleme:** karakter adı, ekranda ilk kez **sözle söylenene ya da yazıyla gösterilene kadar** görsel tariflerde görünür
özellikle değiştirilir ("yara izli, kürk yakalı kadın"). Aksi hâlde seyirci adı istemden öğrenir ve ZN §4.1 "ad ≤ 120 sn" ölçümü
anlamsızlaşır. **`ekranda_bilgi` verilmez:** yazarın "seyirci bunu öğrenir" iddiasıdır; seyirciye vermek cevabı söylemektir.
Betik seyirci özetini bu alanla karşılaştırır (ZN §7.3 girdi listesinde bu alan var; bkz. §9 Ç-2).

### 5.9 `kare-tarifcisi` soru formu (beklenen değer yok)
```json
{"kare": "GIRDI/042.jpg", "sorular": [
  {"id": "q1", "soru": "How many people are visible (faces or bodies)?", "secenek": ["0","1","2","3+"]},
  {"id": "q2", "soru": "Which hand of the woman on the left holds the lantern?", "secenek": ["left","right","none","not visible"]},
  {"id": "q3", "soru": "Where is the woman in frame?", "secenek": ["left third","center","right third"]},
  {"id": "q4", "soru": "Which way does she look?", "secenek": ["frame left","frame right","camera","down","not visible"]},
  {"id": "q5", "soru": "Is there an open flame other than the lantern?", "secenek": ["yes","no"]},
  {"id": "q6", "soru": "How many fingers of her left hand are extended?", "secenek": ["0","1","2","3","4","5","not visible"]}]}
```
Sorular `baslangic_durumu`/`bitis_durumu`/`yasaklar` alanlarından betikle üretilir; cevaplar betikle beklenenle karşılaştırılır
(ARIS kör döküm + deterministik fark, AR1 B4; seçenekli soru, AR2 §5). "not visible" → BAYRAK → hakem.

### 5.10 Oturum başı bağlamı (`oturum_basi.py` çıktısı; hedef ≤ 6.000 kr)
```json
{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext":
"[FİLM SETİ DURUMU · 23.10.2026 14:05 · otomatik]\nAktif film: F20261023_ejderha (seri EMBERFALL)\nAşama: A07b Plan yazımı · P2 sahne grupları 6/17 · kâğıt döngüsü tur 1/4\nSıradaki: G0213 ajan yonetmen (S23) → `python .claude/bin/film.py sonraki`\nBekleyen kullanıcı işi: yok · Flow kilidi: yok · Bütçe: A13'te hesaplanacak\nSon 3 karar: …\nKURALLAR: 1) Kullanıcıya yalnız konu sorulur… (10 madde, SKILL.md §1 ile aynı)\nDöngü: film-yap becerisi. Hafızana değil film.py'ye güven."}}
```
Aktif film yoksa tek cümle: *"Aktif film yok. Konu verildiyse film-yap ile başla; verilmediyse YALNIZ şunu sor: 'Filmin konusu ne olsun? Bir cümle yeter.'"*

### 5.11 Plan dosyasında sahiplik üst bilgisi (yalnız mimariye ait alanlar)
Her yazar çıktısının başında: `"_sahip": "yonetmen", "_gorev": "G0213", "_surum": 3, "_onceki": "G0188"`. Betik, sahibi
olmayan bir rolün yazdığı alanı (ör. yönetmenin `replik.metin` değiştirmesi) `HATA: sahiplik` diye reddeder. Plan içeriği
alanlarının (atomik zincir, süreklilik) şeması yönetmen/süreklilik uzmanlarınındır; ben yalnız sahiplik ve sürüm alanlarını öneriyorum.

---

## 6. Yazılması / değişmesi gereken kod

Öncelik: **P0** = tasarımın çalışması için şart, bulutta sahte testle yazılabilir · **P1** = ilk gerçek filmden önce · **P2** = iyileştirme.

| # | Araç | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|---|
| K-1 | `.claude/bin/film.py` (sarmalayıcı) | YZ_FILM kökünü bulur (`YZ_FILM_KOK` ortam değişkeni → `./ARACLAR` → `./YZ_FILM/ARACLAR`) ve `ARACLAR/film.py`'yi çalıştırır. Böylece beceri, ajan, kanca ve izin kuralları her iki düzende (depo kökü / Windows'ta `Desktop\YZ_FILM`) **aynı komut metnini** kullanır. `ozet` alt komutu hiçbir durumda sıfır dışı kodla çıkmaz (`!` komutu başarısız olursa beceri iptal olur, D/skills) | argümanlar → aynı | P0 |
| K-2 | `ARACLAR/film.py` v2 | Görev defteri. Alt komutlar: `yeni`, `ozet [--kisa/--uzun/--kullanici]`, `sonraki`, `basla`, `bitir`, `kurtar`, `karar ekle`, `ders ekle`, `goster <plan/maliyet/zaman/neden-durdu>`, `surus ac/kapat`, `kapi <Z0…K1>`, `notlar oku/isle`, `beceri-denetim`. Aşama tablosu veri olarak `ARACLAR/hat/asamalar.py`; görev üretici `hat/gorev.py`; doğrulayıcı `hat/dogrula.py` + `ARACLAR/semalar/*.json`. Mevcut 7 üretim aşaması (`senaryo…kurgu`) korunur, `test_film.py` bozulmaz. `onay()` içindeki `input()` görev kipinde kaldırılır (ana Claude Bash'ten çalıştırınca EOF → "onay verilmedi" durması olur); yerine bütçe kapısı | FILM_DURUM + DEFTER → JSON görevler | P0 |
| K-3 | `.claude/hooks/erisim_kapisi.py` | PreToolUse `Read|Glob|Grep|Write|Edit|NotebookEdit`. Gizli dosya: herkes için ret. Makine sahipli: yazma reddi. Alt ajan (`agent_id` var): erisim.json rolüne göre yalnız bağlı görev klasörü; ilk okumada görev bağlama. Ana Claude: 200 KB üstü Read → ret + "`film.py goster` kullan". Her ret `FILM_KAYIT`'a | stdin JSON → `permissionDecision: deny` + gerekçe | P0 |
| K-4 | `.claude/hooks/komut_kapisi.py` | PreToolUse `Bash`. Ret: AYARLAR gizli dosyalarını okuyan/kopyalayan komutlar; `robocopy … /MIR`; kalıcı silme (`rm -r`, `del /s`, `rmdir /s`, `Remove-Item -Recurse`; `_gecici/` hariç, BK §6.5.4); fare/klavye kütüphaneleri (`pyautogui`, `pynput`, `SendKeys`; BK §6.2.10); **Flow kilidi açıkken `memmet.py`** (kilit yalnız kullanıcının çalıştırdığı `UYARI_GECTI.bat` ile kalkar; gün değişince yeniden sorulur, BK §6.2.9); `memmet.py` `--mod elle` dışı kip, `FILM_AYAR.json` izin vermiyorsa (karar 5) | stdin → deny | P0 |
| K-5 | `.claude/hooks/oturum_basi.py` | SessionStart `startup|resume|clear|compact` → §5.10 bağlamı (≤ 6.000 kr; 10.000 sınırını aşarsa kendisi kısaltır) | FILM_DURUM → additionalContext | P0 |
| K-6 | `.claude/hooks/ajan_bitti.py` | SubagentStop: bağlı görevin CIKTI'sini `gecme_sarti`na göre doğrular; eksikse ve `stop_hook_active` false ise `decision: block` + eksik listesi (D/hooks: "keeps the subagent running and delivers `reason` … as its next instruction"); geçerse `film.py bitir` | stdin → block / bitir | P0 |
| K-7 | `.claude/hooks/ajan_sonrasi.py` | PostToolUse `Agent`: ana Claude'a "G0041 GEÇTİ · sıradaki: G0044 (yonetmen)" bağlamı (D/hooks: üst oturuma bağlam eklemek için PostToolUse önerilir); ajan dönüş metni 600 kr'yi aşarsa uyarı | → additionalContext | P0 |
| K-7b | `.claude/hooks/ajan_basi.py` | SubagentStart (D/hooks: oluşturmayı engelleyemez, ajanın bağlamına `additionalContext` ekler): yazar/denetçi rolüne `DERSLER_AKTIF.md`'den o rolün dersleri (≤ 8.000 kr) + "ilk işin GOREV.json'u okumak" hatırlatması; kör rollere hiçbir şey | `agent_type` → additionalContext | P1 |
| K-8 | `.claude/hooks/soru_kapisi.py` | Stop: `otomatik_surus` açıkken `last_assistant_message` kullanıcıya **karar sorusu** içeriyorsa ("hangisini", "onaylıyor musun", "ister misin", "A mı B mi", "devam edeyim mi") → `decision: block`, gerekçe: "Ekip karar verir; KARAR_DEFTERI'ne yaz ve devam et". A00'da aktif film yokken konu sorusu serbest; film-durum turunda (`surus kapali`) serbest | → block | P1 |
| K-9 | `.claude/hooks/devam_kapisi.py` | Stop: `otomatik_surus` açık + `film.py sonraki` çalıştırılabilir görev (ajan/betik) veriyorsa durmayı engeller ("Sıradaki görev hazır: …"). `stop_hook_active` ve 8 ardışık devam tavanı (D/hooks; her araç çağrısında sıfırlanır) döngüyü sınırlar. Kullanıcı eylemi / bekle / bitti durumunda serbest | → block | P2 |
| K-10 | `.claude/hooks/hata_kaydi.py`, `model_degisti.py`, `ozet_sakla.py` | StopFailure (koşanları `kesildi`, Telegram) · PostModelSwitch `source:auto` (sapma kaydı) · PostCompact (`compact_summary` arşivi) | yan etki | P1 |
| K-10b | `.claude/hooks/istem_baglami.py` | UserPromptSubmit: her kullanıcı mesajına ≤ 1.500 kr bağlam (aktif film, bekleyen kullanıcı işi; "bu mesaj soruysa yalnız cevap ver"); mesajda "dur/durdur/bekle" varsa `surus kapat` | → additionalContext | P1 |
| K-11 | `.claude/settings.json` | Kancalar, izinler, `env` (aşağıda) | — | P0 |
| K-12 | `.claude/kurallar/erisim.json` | §5.7 | — | P0 |
| K-13 | `ARACLAR/kor_paket.py` | Kipler `hikaye`, `plan`, `ilk2dk`, `animatik`, `kurgu`; beyaz liste + ad maskeleme; izleme kipinde plan başına kare şeridi (3 kare tek görselde; görsel sayısını üçe böler) | HIKAYE/SAHNELER/kareler → `_GOREV/<id>/GIRDI/PAKET*.md` | P0 |
| K-14 | `ARACLAR/dilim.py`, `plan_birlestir.py` | Ajanlara SAHNELER/HIKAYE dilimi; PLANLAR + SES → SAHNELER.json (eski şemayla uyumlu) | — | P0 |
| K-15 | Şablonlar `.claude/skills/film-yap/sablonlar/*.md` | Her (aşama, ajan, kip) için ISTEM.md şablonu; sayılar RE'den yer tutucuyla basılır (ajana sabit sayı yazılmaz → eşik değişince tek yer) | — | P0 |
| K-16 | 15 ajan dosyası | §3 | — | P0 |
| K-17 | 4 SKILL.md + referanslar; kök `CLAUDE.md`; `YZ_FILM/ARACLAR/CLAUDE.md` (geliştirici) | §4 | — | P0 |
| K-18 | Testler: `test_gorev_defteri.py` (30 kesme noktası; ajan çıktıları kayıtlı **sahte ajan** dosyalarından gelir, LLM yok), `test_kancalar.py` (stdin örnekleri: başka görevin CIKTI'sini okuyan seyirci → deny; gizli dosya → deny; makine sahipli yazma → deny; kilitliyken memmet → deny), `test_kor_paket.py` (yasak alan/ad sızıntısı 0) | ağsız, kredisiz | P0 |
| K-19 | `ARACLAR/beceri_denetim.py` | SKILL.md satır ve çekirdek token tahmini; `name` kuralı (≤ 64, küçük harf-rakam-tire, "claude/anthropic" yok, AR3 B2); `description` ≤ 1.024, + `when_to_use` ≤ 1.536; ajanlarda `model: opus`, `effort: high`, `memory` yok; kör ajanlarda `Glob/Grep/Bash` yok ve `omitClaudeMd: true`; şablonlardaki OZET biçimi `puan_oku` deseniyle aynı; referans dosyaları var | → RAPORLAR/BECERI_DENETIM.json | P1 |
| K-20 | `puan_oku.py` v2 | 6 ölçüt + GENEL, **medyan** (RE `seyirci_karar`; şimdiki kod ortalama alıyor), KRİTİK/ORTA sayısı, `rapor.json` önce, OZET yedek; eski biçimi de okur | raporlar → karar JSON | P1 |
| K-21 | `ders_defteri.py`, `evren.py`, `maliyet.py` | §5.6 terfi; evren yazımı (kart, kostüm, mekân, ses, yüz gömmesi, izleyici özeti); A13 önizleme | — | P1 |
| K-22 | `.bat`: `DEVAM.bat`, `DURUM.bat`, `UYARI_GECTI.bat`, `GUNCELLE.bat`, `ARSIVLE.bat` | Kullanıcının tek tık işleri; `GUNCELLE.bat` depo → `Desktop\YZ_FILM` eşitlemesi (AYARLAR, FILMLER, SES_KUTUPHANESI'ne dokunmaz) | — | P1 |
| K-23 | Başsız yürütücü (araştırma) | `film.py`'nin ajan görevlerini `claude -p` ile kendisinin çalıştırması (ana oturum olmadan gece sürüşü). Belgeden doğrulanmadı | — | P2 |

**`.claude/settings.json` (öneri)**
```json
{
  "env": {"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1"},
  "permissions": {
    "allow": ["Bash(python .claude/bin/film.py *)", "Read(./YZ_FILM/**)", "Read(./.claude/skills/film-yap/**)"],
    "deny":  ["Read(./YZ_FILM/AYARLAR/ai84_anahtar.txt)", "Read(./YZ_FILM/AYARLAR/telegram_bot.txt)",
              "Read(./YZ_FILM/AYARLAR/kie_anahtar.txt)", "Read(./YZ_FILM/AYARLAR/memmet_profil/**)",
              "Bash(robocopy * /MIR*)", "Bash(git push *)"]
  },
  "hooks": {
    "SessionStart": [{"matcher": "startup|resume|clear|compact",
                      "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/oturum_basi.py\""}]}],
    "PreToolUse":  [{"matcher": "Read|Glob|Grep|Write|Edit|NotebookEdit",
                      "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/erisim_kapisi.py\""}]},
                    {"matcher": "Bash",
                      "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/komut_kapisi.py\""}]}],
    "SubagentStart": [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_basi.py\""}]}],
    "SubagentStop":  [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_bitti.py\""}]}],
    "PostToolUse":   [{"matcher": "Agent", "hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ajan_sonrasi.py\""}]}],
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/istem_baglami.py\""}]}],
    "Stop":          [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/soru_kapisi.py\""}]}],
    "StopFailure":   [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/hata_kaydi.py\""}]}],
    "PostCompact":   [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/ozet_sakla.py\""}]}],
    "PostModelSwitch": [{"hooks": [{"type": "command", "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/model_degisti.py\""}]}]
  }
}
```
`ajan_basi.py` (SubagentStart): yazar/denetçi rolüne `DERSLER_AKTIF.md`'den o role ait dersleri ve görev bağlama hatırlatmasını
ekler; kör rollere hiçbir şey eklemez. Kancalar ayarlar dosyasında olduğu için alt ajan araç çağrılarında da çalışır ve rol ayrımını
`agent_type` ile yapar; ajan dosyasına kanca gömmeye gerek kalmaz (proje ajan kancaları ayrıca çalışma alanı güven onayı ister, D/hooks).
`fallbackModel` **yazılmaz** (§3.1 madde 4). Bütün kanca betikleri yalnız standart kütüphane kullanır (kullanıcı PC'sinde ek kurulum yok)
ve 2 sn içinde biter **(tahmin hedef)**. Hata durumunda: alt ajan çağrısıysa **ret** (bağımsızlık kapalı başarısızlıkla korunur),
ana Claude çağrısıysa "karar yok" (hat kilitlenmez); gizli dosya kuralı her durumda reddeder.

---

## 7. Makinenin denetleyeceği eşikler (kaynağıyla)

**Claude Code yapısı** (denetleyen: `beceri_denetim.py`, kancalar)

| Eşik | Değer | Kaynak | Denetleyen |
|---|---|---|---|
| SKILL.md satır | < 500 (hedef ≤ 250) | D/skills "keeping SKILL.md under 500 lines"; AR3 B4 | beceri_denetim |
| Sıkıştırma sonrası geri gelen beceri metni | ilk 5.000 token/beceri; toplam 25.000 | D/skills | beceri_denetim: çekirdek ≤ 4.500 token (tahmin: kr/3) |
| `description + when_to_use` | 1.536 kr'de kesilir | D/skills; AR3 B2 | beceri_denetim |
| `description` | ≤ 1.024 kr | AR3 B2 (Agent Skills spesifikasyonu) | beceri_denetim |
| `name` (beceri) | ≤ 64 kr; küçük harf/rakam/tire; "claude", "anthropic" yok | AR3 B2 | beceri_denetim |
| Ajan açıklamaları toplamı | uyarı > 15.000 token; hedef ≤ 3.000 | D/agents | beceri_denetim |
| İç içe ajan derinliği | varsayılan 3; bizde 1 (kapalı) | D/agents (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`) | settings.json |
| Kanca bağlamı (`additionalContext`) | ≤ 10.000 kr (aşarsa dosyaya yazılır, 2.000 kr önizleme) | D/hooks | oturum_basi kendini kısaltır |
| Stop kancası ardışık devam | 8 (araç çağrısında sıfırlanır) | D/hooks | devam_kapisi bu tavana güvenir |
| SubagentStop düzeltme | en çok 2 blok, sonra `gecersiz` | AR3 B6 OpenMontage "en fazla 2 öz-denetim turu" | ajan_bitti |
| Görev deneme tavanı | 3 (ilk + 2) | tahmin (yukarıdaki 2 turla uyumlu) | film.py |
| Referans dosyası > 100 satır | başında içindekiler | AR3 B4 | beceri_denetim |
| Referans derinliği | 1 seviye | AR3 B4 | beceri_denetim |
| Ajan dönüş mesajı | ≤ 5 satır | YR §4 şablonları | ajan_sonrasi uyarır |
| Ana Claude Read sınırı | 200 KB | tahmin | erisim_kapisi |
| Kanca süresi | ≤ 2 sn | tahmin | test_kancalar ölçer |
| SessionEnd kancası | 1,5 sn varsayılan süre | D/hooks | (kullanılmıyor; ağır iş koymayın) |

**Döngü ve değerlendirme** (denetleyen: `film.py`, `puan_oku.py` v2)

| Eşik | Değer | Kaynak |
|---|---|---|
| Seyirci sayısı / birleştirme | 3 / medyan | RE `seyirci_sayisi`, `seyirci_karar`; ZN §7.3 |
| GENEL medyan; ölçüt medyanı alt sınırı | ≥ 8; ≥ 7 | RE `seyirci_genel_esik`, `seyirci_olcut_min` (BK §8 #20: 8 hedef) |
| KRİTİK / ORTA kopukluk | 0 / ≤ 3 parti başına | RE `kopukluk_kritik_max`, `kopukluk_orta_max_parti` |
| Özet eşleşmesi | ≥ 0,80 | RE `ozet_eslesme_min` |
| İlk 2 dk "devam ederdim" | 3/3 | RE `ilk2dk_devam_evet_min`; ZN §7.2.2 |
| Sıkılma ortak işareti | ≥ 2 seyirci → kesme turuna | RE `sikilma_ortak_isaret_min` |
| Tur tavanı kâğıt / kurgu / görsel | 4 / 3 / 2 | RE `kagit_tur_max`, `kurgu_tur_max`; UH §5 |
| Kesme turu | 10 plan ya da 2 sahne öneri, ≥ %50 uygulama | RE `kesme_turu_oneri` |
| Jüri | 5 rol, 10 ölçüt × 1–10, gerekçe şart, OZET satırı | YR A3; BK §2.12 |
| Oyuncu denetimi | konuşan karakter başına 1 (≤ 8) | ZN §7.2.5; RE `konusan_karakter_max` |
| Kurgu izleme bölümü | 4–5 dk, plan başına 3 kare + duyulan replik | BK §3.8; H/kurgu-izleme-denetimi |
| Gemini paketi | 30 sahne; > 10 ek dosya → ZIP | BK §3.12, §4.1.12 |
| Kare tarifçisi görev boyu | ≈ 12 kare/görev | tahmin (bağlam ve dikkat için) |
| Yönetmen görev boyu | 1 sahne grubu (7–45 plan, ZN §2.4); > 30 plan ise ikiye bölünür | 30: tahmin |
| Toplam ajan çağrısı / film | ≈ 350–450 | tahmin (A03 4 + A04 5 + A06 ≤ 4×≈13 + A07 ≈ 55 yazım + ≈ 40 denetim + A11 ≈ 2×34 tarif + A12/A16 ≈ 2×27 seyirci + düzeltmeler) |

**Kredi ve gizlilik** (denetleyen: `maliyet.py`, `komut_kapisi`)

| Eşik | Değer | Kaynak |
|---|---|---|
| Klip kredisi; yeniden deneme payı | 12 (720p Omni); %20 | RE `kredi_klip_720p`, `kredi_yeniden_deneme_payi`; BK §8 #1–3 |
| Bütçe yetmezse | dur; kalite kısma yok | BK §3.7, §8 #16 |
| Flow uyarısı | ilk uyarıda dur; yeniden başlatma yalnız kullanıcı beyanıyla, gün başına | BK §6.2, §8 #5; H/olagandisi-dur |
| Gizli dosya erişimi | 0 | BK §6.5; CLAUDE.md kuralları |

---

## 8. Kesin kararların benim alanımda uygulanışı

### Karar 1 — Kullanıcıya yalnız konu sorulur
- **Metinde:** kök CLAUDE.md ve SKILL.md çekirdeğinin 1. maddesi; oturum başı bağlamında her seferinde tekrar.
- **Makinede:** `soru_kapisi` (Stop kancası) ana Claude'un son mesajında karar sorusu yakalarsa durmayı engeller ve "ekip karar
  verir" diye geri gönderir; `sayaclar.kullaniciya_soru` sayılır (M1). Seçimler (A/B önerisi, kapak, karakter kartı, ses) ekip
  kararıdır: jüri medyanı, kör tarif + yüz ölçümü, ölçülü ses testi; hepsi KARAR_DEFTERI'ne "karar — neden — yanlışsa maliyeti" biçiminde.
- **Eski onay noktaları** (karakter görünüşü, ses, kurgu, animatik; BK §7.3, §8 #17) bu kararla **kalkar**. Kullanıcı yine de CapCut'ta
  izleyip not bırakabilir; bu bir soru değil, `film-not` girdisidir.
- **Soru ile fiziksel iş ayrı:** kredi yüklemek, Gemini'ye paket vermek, Flow'da GÖNDER'e basmak kullanıcının elindedir (Flow'da
  gönderimi kullanıcı yapar, karar 5). Bunlar talimat olarak verilir, bitişleri dosyadan algılanır.

### Karar 2 — Atomik eylem zinciri
- **Tek sahip:** `eylem_zinciri`, `baslangic_durumu`, `bitis_durumu` alanlarını yalnız `yonetmen` yazar; `hareket_istem` **kodla
  derlenir** (ajan istem yazamaz → "kalemi al" gibi sonuç cümlesi istemlere sızamaz).
- **Kural en üstte:** yonetmen.md gövdesinin ilk satırları bu kuraldır (sıkıştırma sonrası da ajan bağlamında kalır); yasak sonuç
  fiilleri şablona RE `yasak_sonuc_fiilleri` listesinden basılır (tek kaynak).
- **Denetim:** Z0 #13–16 (ZN §6.2) betikte. Kullanıcının "klip başına 2–3 adım" kuralı ile ZN'nin "konuşmalı planda en çok 1 adım"
  kuralı şöyle birleşir: konuşmalı planda **replik bir adım sayılır** (`fiil: "says"`), yani 1 fiziksel adım + 1 replik = 2 adım;
  sessiz planda 2–3 fiziksel adım (bkz. §9 Ç-1). Her adımda `taraf` (sol/sağ), `govde` (el/kol/baş), `parmak` (ör. "başparmak+işaret"),
  `yon` zorunlu.
- **Görüntüde:** `kare-tarifcisi` soru formu bu alanlardan üretilir ("kaç parmak açık", "hangi el") → başlangıç karesi
  `baslangic_durumu` ile makinece karşılaştırılır.
- **Habersiz seyirci de kullanır:** kâğıt kör paketinde planlar atomik adımlarla anlatılır; seyirci yalnız görünür fiziksel
  adımlardan bir şey anlayabiliyorsa hikâye ekrana çıkmış demektir (anlatıcısız filmin testi).

### Karar 3 — Altı özellik
| Özellik | Aşama | Ajan | Betik | Kanca / durum |
|---|---|---|---|---|
| **(a) Animatik + habersiz seyirci** | A12 (video kredisinden önce; `giris_sarti` ile zorunlu) | habersiz-seyirci ×3/parti, yonetmen/kurgucu | animatik.py, izleme_paketi.py, kor_paket.py, puan_oku v2 | erisim_kapisi (kör rol); `donguler.A12` |
| **(b) Dünya durumu defteri + zıplama denetimi** | A07c'de üretilir; A11, A14, A16'da görüntüyle karşılaştırılır | yonetmen (durumları yazar), sureklilik-denetcisi (anlam/hakem) | dunya_durumu.py (planlardan türetir), sureklilik_denetim --kagit/--gecis | `DUNYA_DURUMU.json` makine sahipli: hiçbir ajan elle düzeltemez (erisim_kapisi) |
| **(c) Referansla otomatik yüz kontrolü** | A10 (kartlar), A11 (G1), A14 (V2) | kare-tarifcisi yalnız BAYRAK'ta | yuz_denetim.py (SFace, AR2 §1.1 eşikleri) | yüz gömmeleri `EVREN/…/yuz_gomme.npy` (evren.py) |
| **(d) Kare zinciri** | A11 → A14 | — | son_kare.py (`ffmpeg -sseof`, AR2 §2.3), görev üretici | `gecis_turu: devam` planları görev defterinde **sıralı bağımlılık**; en çok 2 zincir, sonra temiz görselle yeniden demirleme (AR2 §2.3); paralel gönderim yok (Flow uyarısı, AR1 B6) |
| **(e) Kendi kendine öğrenen ders defteri** | Her kapıda kendiliğinden kayıt; film-not'ta kullanıcı şikâyeti; A18'de terfi | ders-editoru | ders_defteri.py | `SubagentStart` kancası rol dersini yazar ve denetçi ajanlara ekler; kör ajanlara eklemez; `memory:` alanı kullanılmaz (habersizliği bozar, denetlenemez) |
| **(f) Kalıcı seri evreni kütüphanesi** | A01 (seri seçimi), A10 (kart/ses), A18 (güncelleme) | yapimci, ses-tasarimcisi, kare-tarifcisi | evren.py (tek yazar) | `EVREN/` makine sahipli; ajanlar yalnız GIRDI kopyasını görür; seyirci yalnız `IZLEYICI_OZETI.md`'yi (önceki filmler, ZN §7.3) |

### Karar 4 — Ses / dudak uyumu
Ses yöntemini ses uzmanı seçer; mimarinin buna koyduğu üç şart:
1. **Claude ajanları ses duyamaz.** Ses kalitesi, dudak ve tını kararları ajana bırakılamaz; hepsi betikle ölçülür: metin kapısı
   (whisper/stable-ts ile WER), SyncNet offset/confidence, LUFS, perde istatistiği (AR3 A1–A4). Ses seçimi (karar 1 gereği ekip
   seçer) de ölçülerle yapılır; ajan yalnız tarif metadatasına bakar.
2. Plan başına `ses.yontem` alanı (`veo_donustur | tts_dudak | veo_ham`) A08'de `ses-tasarimcisi` tarafından yazılır; A15'te betik
   bu alana göre sağlayıcı zincirini seçer; metin kapısı geçmezse görev defteri yeniden çekim ya da yedek yöntem görevi açar.
3. AR3'ün değerlendirmesi (ana yol: Veo sesini sabit karakter sesine dönüştürme; yedek: TTS + dudak senkronu) bu yapıya uyar;
   hangi araçla yapılacağı ses uzmanının kararıdır.

### Karar 5 — Memmet bir yerleştirme yardımcısıdır
- `komut_kapisi`: Flow kilidi varken `memmet.py` çalıştırılamaz; kilidi yalnız kullanıcının `UYARI_GECTI.bat`'ı kaldırır (o gün için).
  Varsayılan kip `--mod elle` (BK §6.1); başka kip `FILM_AYAR.json`'da izinli değilse ret. Fare/klavye kütüphanesi çağrısı ret.
- A14 görevleri `kullanici_eylemi` olarak gelir ("Memmet hazırladı; Flow penceresinde GÖNDER'e bas"); bitiş indirilen dosyadan algılanır.
- Kredi idempotency: gönderim kaydı gönderimden önce; kesilmeden sonra önce `memmet_topla`.

### Karar 6 — Üstün körü iş yok
- Bütün ajanlar opus + high; yedek model zinciri tanımsız; otomatik geçiş kaydı (M11).
- Hiçbir kapı "zaman/kredi az" diye atlanmaz: `giris_sarti` alanları kredili aşamayı kâğıt kapıları geçmeden açmaz.
- Değerlendiricinin yarım işi tamamlanmaz, sıfırdan yapılır; yazarın yarım işi devam ettirilir (§2.3).
- Kesilme dayanıklılığı, bağımsızlık ve sızıntı testleri P0 (M3, M4).

---

## 9. Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

### 9.1 Riskler
| # | Risk | Etki | Önlem |
|---|---|---|---|
| R-1 | **Claude Code'un açıldığı klasör.** Beceriler açılış klasöründen ve depo köküne kadar üst klasörlerden yüklenir; alttaki `.claude/skills` ancak o klasörde dosya okununca yüklenir (D/skills). Kullanıcının gerçek klasörü `C:\Users\Soysal\Desktop\YZ_FILM` = depodaki `YZ_FILM/`, `.claude/` ise depo kökünde | Windows'ta `Desktop\YZ_FILM`'de açılırsa ajanlar/beceriler yüklenmez; depo kökünde açılırsa kullanıcının yolları değişir | Öneri: Windows'ta açılış klasörü `Desktop\YZ_FILM`; `GUNCELLE.bat` depodaki `.claude/` ve film seti `CLAUDE.md`'sini oraya kopyalar (AYARLAR/FILMLER/SES_KUTUPHANESI'ne dokunmaz). Bütün komutlar `.claude/bin/film.py` sarmalayıcısıyla iki düzende aynı (K-1). Ajanlar `FILMLE ILGILI CLAUDE/` gibi depo-özel yolları okumaz |
| R-2 | **Kullanım sınırı.** Film başına ≈ 350–450 opus ajan çağrısı (tahmin) → üretim birkaç güne yayılır; Claude kendi kendine uyanamaz | Kullanıcı "devam" demeden hat bekler | Her şey dosyada (M3); StopFailure Telegram bildirimi; `DEVAM.bat`; otomatik devam (zamanlanmış görev) açık soru S-2 |
| R-3 | **Kanca hatası her şeyi kilitler** (alt ajanda kapalı başarısızlık) | Hat durur | `test_kancalar.py` P0; kanca günlüğü `FILM_KAYIT`'ta; `DURUM.bat` son engelleri gösterir |
| R-4 | **Kanca atlatma:** kancalar yalnız araç çağrılarını görür; ana Claude Bash'te Python ile dosya yazabilir | Makine sahipli dosyalar elle değişir | İzin listesi yalnız `film.py`; `komut_kapisi` sezgisel tarama; `film.py` makine sahipli dosyaların sha1'ini saklar, uyuşmazsa "elle değiştirilmiş" HATA |
| R-5 | **Sürüm:** `omitClaudeMd` v2.1.271+, `PostModelSwitch` v2.1.251+ (D/agents, D/hooks) | Eski sürümde alan sessizce yok sayılır (D/agents "Unrecognized fields are ignored silently") | `kurulum.py` `claude --version` ≥ 2.1.271 denetler |
| R-6 | **Alt ajana git durumu gider** (D/agents: "a git status snapshot") → depo içinde çalışırken dosya adları görünür | Küçük sızıntı (ör. `oneri_B.md` adı) | Görev klasörleri kimlik adlı (`G0041`); Windows'taki `YZ_FILM` git deposu değil |
| R-7 | **Aynı model ailesi kendi yazısını yargılar** (ARIS "hiçbir model kendi çıktısını onaylamaz", AR1 B4) | Kör nokta | Kör paket + yeni örnek + betik karşılaştırması; ikinci model (Gemini) seyirci açık soru S-4 |
| R-8 | **Ajanlar ses duyamaz, hareketi göremez** (yalnız kare) | Ses ve hareket hataları ajan denetiminden kaçar | Ses ve hareket kapıları betikte (V1/V2, SyncNet, LUFS, WER) |
| R-9 | **Durdurulamayan sürüş** (K-9) kullanıcının "dur"unu ezebilir | Kullanıcı kızar | UserPromptSubmit kancası "dur/durdur/bekle" görünce `surus kapat` (P1); `film-durum` da kapatır |
| R-10 | **Eski şemaya bağlı araçlar** (memmet, capcut_film, seslendir SAHNELER.json okur) | Yeni alanlarla bozulma | `plan_birlestir` eski alanları aynen doldurur; yeni alanlar alt nesnelerde (ZN §6.1, AR2 §6.1 ilkesi) |
| R-11 | **Fiziksel iş yükü:** ≈ 14 Gemini paketi (405 klip / 30, tahmin) + kart paketleri + Flow oturumları | Kullanıcı yorulur, karar 1'in ruhu zayıflar | İşler partilere toplanır; her biri tek `.bat`/tek talimat; bitiş otomatik algılanır (M2) |

### 9.2 Diğer uzmanlarla çakışabilecek noktalar (önerilen çözümle)
- **Ç-1 Adım sayısı:** Kullanıcı "klip başına 2–3 adım"; ZN §3.7 ve RE `eylem_adim_konusmali_max: 1` konuşmalı planda 1 adım diyor. Önerim: replik bir adım sayılır (§8 Karar 2). Yönetmen/görüntü uzmanı farklı önerebilir; doğrulayıcı tek kaynaktan (RE) okuyacağı için hangisi seçilirse tek yerde değişir.
- **Ç-2 `ekranda_bilgi` seyirciye verilmesin:** ZN §7.3 girdi listesinde var; yazarın niyetini seyirciye söylemek olur. Karşılaştırma anahtarı olarak kalsın.
- **Ç-3 Model tablosu:** YR §1 bazı rollere Sonnet diyor; kullanıcı kuralı (H/ajan-opus-yuksek) ve karar 6 nedeniyle hepsi opus·high.
- **Ç-4 CLAUDE.md "senaryo aşamaları Claude API ile film.py'de":** Bu tasarımda yaratıcı aşamalar Claude Code alt ajanlarıyla (kullanıcının aboneliği) yürür; `film.py` API çağırmaz, görev üretir. API sağlayıcısı yalnız ileride başsız yürütücü (K-23) ya da ikinci model için.
- **Ç-5 `--onayli` varsayılanı:** CLAUDE.md ve `film.py onay()` kredi aşamasında soru soruyor. Karar 1 gereği varsayılan: bütçe kapısı (sorusuz); `--onayli` yalnız geliştirme.
- **Ç-6 "Parti" sözcüğü** (BK §8 #14): `parti` (hikâye üçte biri), `uretim_blogu` (20 plan), `gemini_paketi` (30), `izleme_bolumu` (4–5 dk) ayrı alan adları.
- **Ç-7 Rapor klasörü:** mevcut kod `_RAPOR/`, ZN ve AR2 `RAPORLAR/`. Öneri `RAPORLAR/`.
- **Ç-8 Puan birleştirme:** `puan_oku.py` ortalama alıyor; RE medyan diyor. OZET biçimi de taslak ajandakiyle (3 ölçüt) ZN (6 ölçüt) arasında farklı. Tek biçim: ZN §7.3 + `KRITIK`/`ORTA`.
- **Ç-9 Replik metninin sahibi:** hikâye yazarı (senaryo) mı, yönetmen mi? Önerim: metin hikâye yazarının; yönetmen yalnız böler, zamanlar, ekran dışına taşır; değişiklik isteğini dosyayla bildirir. Senarist ve yönetmen uzmanları farklı bölüşüm önerebilir; mimari "her alanın tek sahibi" şartını korur.
- **Ç-10 Yeni ajan önerileri:** Diğer uzmanlar ek ajan (ritim editörü, görüntü yönetmeni, renk) önerebilir. Mimari ölçüt: yeni ajan ancak (a) ayrı bir dosyanın sahibi ya da (b) ayrı kör girdili bağımsız değerlendirici ise açılır; değilse mevcut ajanın kipi olur. Açıklama bütçesi (15.000 token uyarısı) bunu sınırlamaz, karmaşıklık sınırlar.
- **Ç-11 Görsel denetçi:** Gemini ajanı B3'te süreklilik hatası yakaladı (H/gemini-ajan-gorsel). Claude `kare-tarifcisi` mi, Gemini mi, ikisi birden mi? İkisi birden = çapraz model (R-7) ama kullanıcıya fiziksel iş ekler.
- **Ç-12 Kurgu izleme paketi:** mevcut `izleme_paketi.py` plan başına 3 kare; AR1 §5 üçlü pencere (önceki son kare + 3 kare + sonraki ilk kare). `kor_paket` izleme kipinde ikisini birleştirir.

### 9.3 Açık sorular
- **S-1** Üretimin tamamı kullanıcının Windows'unda mı yürüsün (önerim), yoksa kâğıt aşamaları bulutta yapılıp depoya itilsin, Windows çeksin mi? İkincisi kullanıcıya `git` işi çıkarır.
- **S-2** Kullanım sınırından sonra kendiliğinden devam: Claude masaüstü uygulamasının zamanlanmış görevleri ya da `claude --continue` ile başlayan bir `.bat` güvenle kullanılabilir mi? Belgeden doğrulanmadı.
- **S-3** Tur tavanı dolup eşik tutmazsa ne olacak? Karar 6 "üstün körü yok" der, sonsuz döngü de olmaz. Önerim: bir "yapısal kurtarma turu" (yapımcı + yazar, yapıyı değiştirme yetkisiyle), sonra en yüksek medyanlı sürümle BAYRAKLI devam ve kullanıcıya **bilgi** (soru değil). Ekip onayı gerek.
- **S-4** İkinci model (Gemini) seyirci/denetçi olarak eklensin mi? Elle (kullanıcı işi) mi, API anahtarıyla (AYARLAR) mı?
- **S-5** Karakter kartlarında kullanıcı onayı tamamen kalkınca (karar 1) seçilen kartlar kullanıcıya en azından son özette gösterilsin mi? Önerim: evet, bilgi olarak; itirazı `film-not` ile.
- **S-6** `effort: high` mı, `xhigh` mı? Kullanıcı "yüksek" dedi; xhigh kullanım süresini uzatır. Kanıt olmadan high.
- **S-7** Başsız yürütücü (K-23, `claude -p`) gece sürüşü için istenir mi?
- **S-8** Görev boyu sayıları (12 kare, 30 plan, 4–5 dk izleme bölümü) ilk filmde ölçülerek ayarlanmalı.

### 9.4 Uygulamadan önce bir kez doğrulanacak Claude Code davranışları
1. `settings.json` `env` alanındaki `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` değişkeninin alt ajan açmayı gerçekten kapatması.
2. Windows'ta (Git Bash) `python "$CLAUDE_PROJECT_DIR/.claude/hooks/…"` komutunun çalışması ve Python 3.10 ile kancaların 2 sn altında bitmesi.
3. `maxTurns`'e ulaşan alt ajanda SubagentStop'un tetiklenmesi ve `SendMessage` ile sürdürme (D/agents "marked as partial … resume").
4. İzin kuralı sözdizimi `Bash(python .claude/bin/film.py *)` (D/skills örneği ve AR3 aynı biçimi kullanıyor).
5. İlk okumada görev bağlama: paralel 3 seyircinin her birinin ayrı görev klasörüne bağlanması (`test_kancalar.py` + gerçek bir deneme).
6. `!` komutunun Windows'ta `python` bulması (bulamazsa beceri iptal olur → sarmalayıcı `py -3.10` yedeği).
