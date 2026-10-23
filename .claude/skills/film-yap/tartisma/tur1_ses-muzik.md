# Tur 1 — Ses ve Müzik Uzmanı Önerisi

Hazırlayan: ses-muzik uzmanı (Claude, bağımsız tur; diğer uzmanların dosyaları okunmadı). Tarih: 23 Ekim 2026.

**Kaynak kısaltmaları:** `Z` = `ZANAAT.md` · `RE:<anahtar>` = `ritim_esikleri.json` · `BK` = `BILGI_KURALLARI.md` ·
`A1/A2/A3` = `arastirma/01_film_hatlari.md`, `02_sureklilik.md`, `03_ses_ve_claude_code.md` · `D` = `03_DERSLER.md` ·
`UH` = `01_URETIM_HATTI.md` · `CI` = `CLAUDE_ICIN.md` · `KR` = `KARARLAR.md` · `YR` = `YAPIM_REHBERI.md` ·
`H/<ad>` = `HAFIZA_YEDEGI/<ad>.md` · kod dosyaları adıyla (`seslendir.py` …).

**Sayı etiketleri:** kaynağı olan sayının yanında kaynak yazar. **(tahmin)** = kaynağı yok, mühendislik başlangıç değeri, kendi verimizle
ayarlanacak. **(bellekten)** = bildiğim bir standart ama bu oturumda açılıp doğrulanmadı. **[arama]** = A3'teki doğrulanmamış arama bilgisi.

**Önemli kısıt:** Claude ses DUYAMAZ. Bu alandaki her yargı ya ölçümle (LUFS, benzerlik, korelasyon, ASR) ya da ölçümün yazıya
dökülmüş hâliyle verilir. "Kulakla bakılır" diye bir adım bu belgede yoktur.

---

## 1. Alanımın hedefi ve başarı ölçütü (sayılarla)

### 1.1 Hedef
Seyirci 30–45 dakika boyunca bir kez bile şunları dememeli: "dudak tutmuyor", "bu ses kimin?", "sesi değişti", "ses kesildi ya da zıpladı",
"müzik konuşmayı bastırıyor". Her karakter **filmden filme aynı sesle** konuşmalı (seri evreni). Müzik **yasal olarak kullanabileceğimiz**,
karaktere bağlı (leitmotif) ve sözsüz olmalı. Film YouTube'da **−14 LUFS**'ta temiz çalmalı. Bunların hepsi kullanıcıya soru sormadan,
ölçülerek ve kayıt altında yapılmalı (kesin karar 1 ve 6).

### 1.2 Ses/dudak kararı (kesin karar 4, kısa hâli; gerekçe ve hesap §8.3'te)
**"Veo konuşur, sesi biz sabitleriz."**
1. **Yol A — ağzı görünen replik:** Flow/Veo klibi repliği kendisi söyler (istemde replik + karakterin sabit "Veo ses tarifi").
   Konuşma ayrıştırılır → senaryoya hizalanır (metin kapısı) → karakterin evren sesine **yerel ses dönüştürücüyle** (RVC; motor ölçümle seçilir)
   çevrilir. Zamanlama, vurgu ve dudak Veo'dan geldiği için senkron bozulmaz. Görüntüye dokunulmaz.
2. **Yol B — ağzı görünmeyen replik** (ekran dışı, sırt dönük, uzak plan, L kesme taşması): doğrudan ElevenLabs v4 TTS (AI84), aynı ses.
   RVC modeli bu TTS sesinden eğitildiği için A ve B aynı tınıya oturur.
3. **Yedekler:** (Y1) metin ya da ses kapısında kalan klip → Flow'da yeniden çekim, en çok 2 kez, normal kuyruk ve tempo kurallarıyla;
   (Y2) yine olmazsa TTS + dudak senkronu (MuseTalk 1.5 yerel ya da bulut; dolar → bütçe onayı); (Y3) tek kritik replikte AI84 Voice Changer
   (bütçe onayı). **Wav2Lip asla** (ticari kullanım yasak, A3 A1).
4. Ana yolun motoru varsayımla değil, **B2 arşivindeki gerçek Veo konuşma klipleriyle kredisiz kıyas** (§2 A3) ile seçilir.
5. **Müzik:** leitmotif kimliği MIDI olarak evrende saklanır; ipuçları yerelde **ACE-Step 1.5 (MIT)** ile üretilir; motif testini geçemeyen tema ipucu
   **MIDI + CC0 orkestra örnekleri**yle çalınır. Lisansı belgelenmemiş hiçbir parça kullanılmaz (§8.4).

### 1.3 Başarı ölçütleri

| # | Ölçüt | Hedef | Ölçen | Kaynak |
|---|---|---|---|---|
| B1 | Dudak ofseti (ağzı görünen replik, kurgu sonrası) | Repliklerin ≥ %95'i \|ofset\| ≤ 42 ms (24 fps'te 1 kare); hiçbiri > 125 ms (3 kare) | `dudak_denetim.py` | 1 kare = 1/24 sn (hesap); %95 ve 3 kare (tahmin); algı eşiği için ITU-R BT.1359: ses önde +45 ms / geride −125 ms fark edilir (bellekten) |
| B2 | Başkasının repliği altında oynayan dudak | 0 | `dudak_denetim.py` | Z §5 / H/video-istem-kurali ("dudakları oynayan karakterin üstüne başkasının repliği konmaz") |
| B3 | Ses kimliği: her son replik ↔ karakterin evren ses merkezi | %100 replik benzerlik ≥ eşik (başlangıç 0,70) | `ses_olcum.py` (konuşmacı gömmesi) | eşik (tahmin), kalibrasyon §7.9 |
| B4 | Kadro ayırt ediciliği | Karakterler arası benzerlik ≤ 0,60; aynı cinsiyette F0 medyan farkı ≥ 2 yarım ton | `ses_sec.py` | (tahmin) |
| B5 | Altyazı = duyulan söz | Altyazı metni duyulan sözle aynı; karakter adları %100 doğru; son miks üzerinde ASR ↔ altyazı kelime hata oranı (WER) ≤ 0,15 / replik | `son_miks.py` + ASR | WER eşiği (tahmin); "müzik konuşmayı bastırıyor mu" ölçüsü olarak kullanılır |
| B6 | Diyalog seviyesi | Fısıltı −24 · yumuşak −21,5 · normal −19,5 · bağırma −17 LUFS, replik başına ±1 LU, %100 | `diyalog_esitle.py` | RE:diyalog_lufs, RE:diyalog_lufs_tolerans; H/proje-b2 |
| B7 | Ambiyans | Sahne içinde tek yatak dosyası; boşluk 0; ardışık planlar arası fark ≤ 3 LU; diyalogdan 12–18 dB aşağı | `ses_katmani.py` | RE:ambiyans_sahne_ici_fark_max_lu, RE:ambiyans_diyalog_alti_db; D (kapı sahnesi) |
| B8 | Efekt | Eylem zincirinin her adımına ≥ 1 efekt (sessiz işaretliler hariç); yeniden çekilen planlarda efekt güncelliği %100 | `ses_plani.py`, `ses_katmani.py` | Z §5.1; D ("yeni çekilen planlar efektsiz kalıyordu") |
| B9 | Müzik yerleşimi | Kaplama %40–65; müziksiz blok ≤ 240 sn; müzikli blok ≤ 300 sn; diyalog altında ≥ 12 dB aşağı | `muzik.py` | RE:muzik_kaplama_oran, RE:muziksiz_blok_max_sn, RE:muzikli_blok_max_sn, RE:muzik_diyalog_alti_min_db |
| B10 | Leitmotif | Doruğa kadar ≥ 3 dönüş, **ses analiziyle doğrulanmış** (kâğıtta yazılı olması yetmez) | `muzik.py` (kroma benzerliği) | RE:leitmotif_donus_min; doğrulama yöntemi (tahmin) |
| B11 | Müzik lisansı | Her parçanın kaynak kaydı (model, sürüm, lisans, istem, tohum, tarih) %100; söz/vokal 0; yayın öncesi Content ID ön kontrolünde talep 0 | `muzik.py`, yayın | BK 4.5, H/uretim-hatti-v2 ("sözsüz") |
| B12 | Sessizlik | Mutlak sessizlik (< −50 dB) ≤ 2/film, her biri ≤ 1 sn, yalnız planlı yerde; planlı müziksiz anlar yerinde | `kalite_denetim.py` | RE:mutlak_sessizlik_* |
| B13 | Final karışım | −14 ±1 LUFS; gerçek tepe ≤ −1 dBTP; LRA ≤ 14 LU; mono toplamda yükseklik farkı ≤ 3 LU | `son_miks.py` | RE:final_lufs, RE:true_peak_max_dbtp; LRA ve mono (tahmin) |
| B14 | Seyirci | Kurgu izleme raporunda ses kaynaklı KRİTİK = 0 ("kim konuştu belli değil", "ses kesildi") | habersiz seyirci + `ses-denetcisi` | RE:kopukluk_kritik_max |
| B15 | Maliyet | Ana yolda dolar harcaması 0. AI84: ilk film ≈ 85 bin kredi (bir kerelik ses bankası dahil), sonraki filmler ≈ 25–30 bin kredi. Ses kaynaklı Flow yeniden çekimi, filmin %20'lik yeniden deneme payının içinde kalır | `film.py` önizleme | hesap §8.3; RE:kredi_yeniden_deneme_payi |

## 2. Aşama aşama süreç: her adım için girdi → iş → çıktı dosyası → geçme şartı → kim yapar (ajan/betik/ana Claude)

**v2 sırasına yerleşim** (BK §7.6): hikâye → seyirci → yönetmen → **ses (kâğıtta)** → kartlar → görseller → **animatik** → video → **katmanlı kurgu** → yayın.
Ses işleri beş bloğa ayrılır. A ve B blokları Flow kredisi harcamaz ve video aşamasından ÖNCE biter (Z K8). C ve D blokları parti parti çalışır; E yayında ve sonda.

```
A KÂĞIT   : A1 ses profilleri → A2 ses seçimi → A3 ses bankası + dönüşüm modeli (seride bir kez)
            A4 ses tasarımı → A5 eksik efekt temini → A6 müzik planı → A7 kâğıt ses kapısı (S0)
B ANİMATİK: B1 replik süre kapısı (gerçek TTS süresi) → B2 animatik sesi + müzik üretimi + işitsel döküm
C VİDEO   : C1 ayrıştırma + hizalama + metin kapısı → C2 dönüşüm/TTS + S2 kapısı → C3 ses kararları (yeniden çekim kuyruğu)
D KURGU   : D1 dudak (S3) → D2 diyalog eşitleme (S4) → D3 ambiyans + efekt (S5) → D4 müzik yerleşimi (S6) → D5 son miks (S7)
            D6 kurgu değişince yeniden ölçüm → E1 yayın sesi → E2 ders defteri + evren güncellemesi
```
Klasörler: kâğıt belgeleri `_SES/`, ses dosyaları `SESLER/`, müzik `MUZIK/`, raporlar `_RAPOR/` (mevcut kodla aynı), kalıcı kütüphane
`EVREN/` (yolu `AYARLAR/FILM_AYAR.json → yollar.evren`), efekt kütüphanesi `SES_KUTUPHANESI/` (`DIZIN.json` ile).
Her kapı `_RAPOR/<kapi>_<parti>.json` yazar, biçim Z §6.2 ile aynı: `{kapi, sonuc, hatalar:[{madde, plan, olcu, esik, oneri}]}`.

### A — Kâğıt bloğu (Flow kredisi yok)

**A1. Ses profilleri** (hikâye v2'den hemen sonra; yönetmenle paralel)
- Girdi: hikâye v2'deki karakter kartları (ses tarifi: yaş, tını, aksan, istek/korku), dünya kuralları (aksan haritası), `EVREN/SESLER/*/ses.json` (seride önceden seçilmiş sesler).
- İş: Konuşan her karakter için yapılandırılmış ses profili yazılır: cinsiyet, yaş bandı, aksan, perde (düşük/orta/yüksek), tını etiketleri, tempo, enerji;
  **Veo ses tarifi** (her konuşan klipte kelimesi kelimesine tekrarlanacak en çok 10 kelimelik İngilizce dize, filtre kelimesi ve yaş sözcüğü yok);
  **etiket ailesi** (o karakterin kullanabileceği TTS ton etiketleri); **telaffuz sözlüğü** (uydurma adların okunuşu). Evrende kayıtlı karakter yeniden seçilmez.
- Çıktı: `_SES/ses_profilleri.json`.
- Geçme şartı: konuşan her karakterin profili tam; Veo ses tarifleri `istem_denetim.py` filtre listesinden geçer; aynı cinsiyetteki karakterlerin perde/tını etiketleri ayrışır.
- Kim: `ses-kadrocusu` ajanı (Opus). Ana Claude kararı `KARAR_DEFTERI.md`'ye "karar — neden — yanlışsa maliyeti" biçiminde yazar (A3 B6).

**A2. Otomatik ses seçimi** (AI84 kredisi: karakter başına ≈ 1,5 bin)
- Girdi: `_SES/ses_profilleri.json`, karakterin hikâyedeki en karakteristik 3 repliği (normal, duygusal, fısıltı/bağırma).
- İş: `ses_sec.py` (1) AI84 paylaşılan ses kütüphanesinde profile göre arar (`ai84.voices(**filtre)`), (2) kısıtlı (`voice_restricted`) ve İngilizce olmayanları atar,
  (3) ücretsiz önizleme seslerini ölçer (F0 medyanı, konuşma hızı, konuşmacı gömmesi), (4) en iyi 6 adaya 3 repliği okutur (önbellekli TTS),
  (5) puanlar: profil uyumu, kadro ayırt ediciliği, ASR ile anlaşılırlık ve **ad telaffuzu**, 3 replik arası kararlılık; (6) seçer ve evrene yazar.
- Çıktı: `EVREN/SESLER/<karakter>/ses.json`, `_RAPOR/S1_ses_secim.json`, dinlemek isteyen için `_SES/SES_SECIM.html` (onay kapısı DEĞİL; kesin karar 1).
- Geçme şartı: S1 eşikleri (§7.2): benzerlik/ayırt edicilik, telaffuz WER = 0 (adlarda), kararlılık.
- Kim: betik ölçer; `ses-kadrocusu` adayların ölçüm ve meta verisine bakıp gerekçeli seçer (Claude duyamaz; yalnız sayılar ve açıklamalar).

**A3. Ses bankası, dönüşüm modeli ve motor kıyası** (yalnız seride YENİ karakter için; karakter başına ≈ 8,5 bin AI84 kredisi bir kez)
- Girdi: seçilen ses, etiket ailesi; kıyas için **B2/B3 arşivindeki gerçek Flow konuşma klipleri** (`D:\YZ_FILM_ARSIV\PROJE_B2\…\SIRALI_VIDEO`, yol ayardan).
- İş: (1) karakterin sesiyle ≈ 10 dk'lık **ses bankası** üretilir (farklı duygular ve etiket ailesi; metinler hikâyeden bağımsız, fonetik olarak zengin);
  (2) RVC karakter modeli yerelde eğitilir (RTX 3050 Ti, arka planda; süresi ölçülecek); (3) **ses_kiyas.py**: aynı 20 arşiv klibi OpenVoice V2, RVC ve
  (lisansı netleşirse) Seed-VC ile dönüştürülür; mevcut "TTS süreye sığdırma" yöntemi de kıyasa girer. Ölçütler: hedef sese benzerlik, zarf gecikmesi,
  dönüşmüş sesin ASR anlaşılırlığı, fısıltı/bağırma başarısı.
- Çıktı: `EVREN/SESLER/<karakter>/banka/`, `…/rvc/<karakter>_v1.pth`, `…/merkez.npy` (gömme merkezi), `_RAPOR/S1b_donusum_kiyas.json`.
- Geçme şartı: kazanan motor, tutulmuş (eğitime girmemiş) cümlelerde benzerlik ≥ eşik ve gecikme ≤ 20 ms; kazanan `AYARLAR/FILM_AYAR.json → saglayicilar.ses_donusum` sırasının başına yazılır.
- Kim: betik (eğitim ve ölçüm); ana Claude rapora göre motor sırasını yazar.

**A4. Ses tasarımı kâğıtta** (yönetmen planı ve dünya durumu defteri bittikten sonra)
- Girdi: `SAHNELER.json` (`zanaat.eylem_zinciri`, `kadraj`, `plan_tipi`, `replik`, `ekran_disi_ses`, `kesme`, `sahne_grubu`), sahne grupları (`mekan`, `eksen`),
  dünya durumu defteri (hava, gün saati, ateş/fener durumu, nesne durumları), `EVREN/MEKANLAR/*/ses.json`, `SES_KUTUPHANESI/DIZIN.json`, ders defteri (ses).
- İş: `ses_plani.py --taslak` otomatik doldurur: (1) her replik için **yol** (A/B) ve `agiz_gorunur` (kadraj + ekran dışı + sırt); (2) eylem zincirinin her adımından
  **efekt olayları** (fiil → efekt sözlüğü; zemin malzemesi mekândan, kumaş kostümden, nesne malzemesi nesne kartından); (3) sahne grubu başına **tek ambiyans yatağı**
  (mekân türü + hava + gün saati katmanları; dünya durumu defterinden); (4) Flow istemine girecek kısa `Sound:` cümlesi; (5) replik seviyesi (fiilden: whispers → fısıltı …).
  `ses-tasarimcisi` taslağı inceler ve ekler: sessizlikler (Z §5.3), yaratık sesleri, J/L ses köprüsü önerileri, iç mekândan dışarı bakan planlarda dış katman kazancı.
- Çıktı: `SAHNELER.json → zanaat.ses` ve `sahne_gruplari.<id>.ses`; `_SES/SES_TASARIMI.md`; `_SES/EKSIK_EFEKTLER.json`.
- Geçme şartı: S0 kâğıt kapısı (A7) HATA'sız.
- Kim: betik + `ses-tasarimcisi` (Opus, yüksek efor; H/ajan-opus-yuksek).

**A5. Eksik efekt temini**
- Girdi: `_SES/EKSIK_EFEKTLER.json`.
- İş: `ses_kutuphanesi.py --ara` CC0 kaynaklarda arar (Freesound API, yalnız CC0 filtresi; anahtar `AYARLAR/`), lisansı ve kaynak adresini kaydeder, indirir,
  ölçer (LUFS, süre, tepe, döngüye uygunluk, içinde anlaşılır söz var mı). İndirme izni kullanıcıdan **bir kez, kurulumda** alınır (`AYARLAR/FILM_AYAR.json → indirme_izni.cc0_efekt`), bkz. §9 açık soru.
- Çıktı: `SES_KUTUPHANESI/<kategori>/…wav`, güncel `DIZIN.json` (her dosyada `lisans`, `kaynak_url`, `indirme_tarihi`).
- Geçme şartı: planlanan her efekt bir dosyaya çözülür; lisansı CC0 (ya da açıkça ticari izinli) olmayan dosya kullanılmaz.
- Kim: betik.

**A6. Müzik planı (spotting) ve leitmotif**
- Girdi: `duygu_haritasi`, `vuruslar`, planların `hedef_duygu`, `yogunluk`, `vurus`, `zanaat.ses.sessizlik`; `EVREN/MUZIK/leitmotifler.json`; Z §5.3–5.4.
- İş: `muzik-supervizoru` ipucu (cue) listesini yazar: her ipucunun giriş olayı ve çıkış olayı (plan + ofset), türü (`tema` / `doku` / `aksiyon`), motifi ve dönüşümü,
  vuruş noktaları (hit), seviye, sağlayıcı, İngilizce istem (sanatçı/film adı yok, sözsüz). Yeni karakterin motifi evrene aday olarak yazılır.
- Çıktı: `MUZIK/muzik_listesi.json`, `MUZIK/MUZIK_PLANI.md`.
- Geçme şartı: `muzik.py --kagit` (Z2 #40 ve §7 S6 kâğıt maddeleri) HATA'sız.
- Kim: `muzik-supervizoru` (Opus, yüksek efor) + betik.

**A7. Kâğıt ses kapısı S0**
- Girdi: A4–A6 çıktıları.
- İş: `ses_plani.py --denetle`: yol/görünürlük tutarlılığı, efekt kapsamı, ekran dışı repliğin altında konuşmayan bir dudak olması, ses tanıtım kuralı (ekran dışı ses yalnız
  karakter daha önce ekranda konuşurken duyulduysa), sessizlik kotası, müzik blokları, leitmotif dönüş sayısı, yatak ↔ dünya durumu uyumu.
- Çıktı: `_RAPOR/S0_ses_kagit.json`; HATA varsa `YENIDEN_YAZ.json` (yönetmen/hikâye odasına geri).
- Geçme şartı: HATA = 0.
- Kim: betik; HATA'ları metni yazan ajan düzeltir (YR "revizyonu aynı yazar yapar").

### B — Animatik bloğu (Flow kredisi yok; AI84 ≈ 15 bin kredi, sonra önbellekten)

**B1. Replik süre kapısı**
- Girdi: bütün replikler, seçilmiş sesler, planların `klip_sn`, `kullanim`, `replik_zaman`.
- İş: Her replik Yol B ile (TTS) seslendirilir. Gerçek süre plan penceresiyle karşılaştırılır: `TTS süresi + 0,4 + 0,5 ≤ kullanılabilir pencere` (Z §2.3).
  Gerçek süreler plana `replik_zaman.tts_sn` olarak geri yazılır. Bu TTS dosyaları önbellekte kalır ve Yol B repliklerinde son ses olarak yeniden kullanılır (ikinci kez ücretlenmez).
- Çıktı: `SESLER/animatik/`, `_RAPOR/S2a_replik_sure.json`.
- Geçme şartı: sığmayan replik 0. Sığmayanlar `YENIDEN_YAZ.json` ile yönetmene döner (replik kısaltma, ekran dışına taşıma, 10 sn klip).
- Kim: betik.

**B2. Animatik sesi, müzik üretimi, işitsel döküm**
- Girdi: animatik zaman çizelgesi (`animatik.py`), B1 sesleri, kâğıt ses planı, müzik listesi.
- İş: `ses_katmani.py --animatik` yatakları ve efektleri **plandaki** saniyelere koyar; `muzik.py --uret` ipuçlarını yerelde üretir (aday başına 3), ölçer, seçer, sahneye uydurur;
  `son_miks.py --animatik` −14 LUFS önizleme yapar. Seyirci ajanı duyamadığı için **işitsel döküm** üretilir: her plan için "duyulan" satırı (konuşanın adı DEĞİL,
  "kadrajdaki kadın konuşuyor" ya da "ekran dışı: daha önce duyduğun boğuk erkek sesi"), efektler, müzik türü, sessizlikler.
- Çıktı: `ANIMATIK/ses_*.wav`, `MUZIK/secilen/*.wav`, `MUZIK/KAYNAK_KAYDI.json`, `ANIMATIK/ISITSEL_DOKUM.md`.
- Geçme şartı: S5/S6/S7 maddelerinin animatikte ölçülebilenleri; müzikte vokal 0 ve lisans kaydı tam.
- Kim: betik; işitsel döküm habersiz seyirciye gider (seyirci uzmanının alanı).

### C — Video sonrası blok (parti parti)

**C1. Ayrıştırma, hizalama, metin kapısı**
- Girdi: `SIRALI_VIDEO/NNN.mp4` (Yol A replikli planların klipleri), replik metinleri.
- İş: `ses_donustur.py --ayristir`: klip sesi 48 kHz'e alınır, konuşma ve konuşma dışı olarak ayrılır (BS-RoFormer; yedek demucs). Konuşma kanalı stable-ts ile senaryo metnine
  **hizalanır** ve ayrıca serbest ASR ile **Veo'nun gerçekte ne söylediği** çıkarılır. WER ve ad doğruluğu hesaplanır. Konuşma kanalı yalnız hizalanmış söz pencerelerinde (±0,1 sn)
  tutulur; dışı susturulur (yaratık sesi ya da gürültü dönüştürücüye girmesin).
- Çıktı: `SESLER/ayrik/NNN_konusma.wav`, `NNN_diger.wav`, `SESLER/hizalama/NNN.json` (kelime zamanları, Veo metni, WER).
- Geçme şartı: konuşma bulundu; WER ≤ 0,10 → GEÇ; 0,10–0,25 → `ses-denetcisi` anlam eşdeğerliğine bakar; > 0,25 ya da ad yanlış ya da konuşma yok → yeniden çekim kuyruğu (§7 S2).
- Kim: betik + `ses-denetcisi` (anlam kararı).

**C2. Dönüşüm (Yol A) ve TTS (Yol B), S2 kapısı**
- Girdi: C1 çıktıları, `EVREN/SESLER/<karakter>/` (model, merkez, F0 istatistiği), önbellekteki TTS.
- İş: Yol A: F0 kaydırması otomatik hesaplanır (`12·log2(F0_hedef / F0_kaynak)` yarım ton, yuvarlanır), konuşma kanalı RVC ile dönüştürülür; dönüşmüş sesin enerji zarfı
  Veo konuşmasının zarfıyla çapraz korelasyonla karşılaştırılır (gecikme), benzerlik ve ASR anlaşılırlığı ölçülür. Yol B: önbellekteki TTS alınır; gerekirse ±%8'e kadar zaman
  esnetme (fazlası için yeniden TTS). Altyazı metni = **duyulan metin** (Yol A'da Veo'nun kabul edilmiş metni, Yol B'de senaryo).
- Çıktı: `SESLER/donusum/NNN_<karakter>.wav`, `SESLER/tts/…`, `SESLER/diyalog.json` (sürüm 2, §5.4).
- Geçme şartı: S2 eşikleri (benzerlik, gecikme, anlaşılırlık).
- Kim: betik.

**C3. Ses kararları**
- Girdi: `_RAPOR/S2_*.json`, `diyalog.json`, ilgili planların kadraj ve replik alanları.
- İş: `ses-denetcisi` her başarısız replik için karar yazar: kabul (anlam eşdeğer, altyazı güncellenir) · yol değiştir (A→B: kurguda ağız görünmüyorsa) · yeniden çek
  (Flow için `CORRECTION:` cümlesi, ör. ad yanlışsa istemde adın okunuşu) · Y2 dudak senkronu (bütçe varsa). Yeniden çekimler normal `YENIDEN_URET.json` kuyruğuna gider;
  Memmet'in tempo ve "uyarıda dur" kuralları aynen geçerlidir.
- Çıktı: `_RAPOR/SES_KARARLARI_P<n>.json`, `YENIDEN_URET.json` ekleri (`sebep: "ses"`), ders adayları.
- Geçme şartı: her başarısız replik için tek bir karar var; aynı replik 2 yeniden çekimden sonra hâlâ kalıyorsa Y2'ye ya da kullanıcı raporuna düşer.
- Kim: `ses-denetcisi` (Opus; içeriği o üretmediği için denetler: "model kendi işini onaylamaz", A1 B4).

### D — Kurgu bloğu (kesim belli olduktan sonra, parti parti)

**D1. Dudak denetimi (S3)** — kesim ya da sıra her değiştiğinde taslak verilmeden önce (BK 5.1.9)
- Girdi: kurgu planı (`kullanim {bas, sure}`, `kaynak_klip`), `diyalog.json`, klipler, yüz kapısının kare başı kimlik çıktısı (V2).
- İş: `dudak_denetim.py` plan penceresinde MediaPipe yüz noktalarından **ağız açıklığı** (jawOpen) dizisini çıkarır, son diyalog sesinin zarfıyla korelasyonla ofset ve güven
  hesaplar; konuşan yüzün kimliği = replik karakteri mi; ekran dışı replik sırasında kadrajdaki yüzün ağzı oynuyor mu; bölünmüş klipte atlanan aralık bir sözün ortasına
  denk geliyor mu. İsteğe bağlı ikinci görüş: SyncNet (yalnız ölçüm).
- Çıktı: `_RAPOR/S3_dudak_P<n>.json`.
- Geçme şartı: §7 S3.
- Kim: betik; düzeltme kararı `ses-denetcisi` + kurgu.

**D2. Diyalog eşitleme ve mekân akustiği (S4)**
- Girdi: `diyalog.json`, replik seviyeleri, sahne grubu mekânı.
- İş: `diyalog_esitle.py` her repliği K-ağırlıklı ölçer (kısa repliklerde kısa süreli ölçüm), hedef LUFS'a kazanç verir (tepe normalleştirme YOK), mekâna göre oda yankısı
  (sentetik oda yanıtı) ve plan ölçeğine göre uzaklık (geniş planda daha ıslak, yakın planda kuru) ekler; aynı karakterin Yol A ve Yol B replikleri arasında tını eşleme EQ'su uygular.
- Çıktı: `SESLER/esit/…wav`, `_RAPOR/S4_diyalog_P<n>.json`.
- Geçme şartı: §7 S4.
- Kim: betik.

**D3. Ambiyans ve efekt oturtma (S5)**
- Girdi: kurgu zaman çizelgesi, `zanaat.ses`, sahne yatakları, `SESLER/ayrik/*_diger.wav` (klibin kendi efekt sesi).
- İş: `ses_katmani.py`: sahne başına tek yatak, sahne geçişinde 0,5–1,0 sn çapraz geçiş ve 0,3–1,0 sn öne alma; efekt olayları önce **klibin kendi efekt sesindeki** başlangıç
  anına oturtulur (Veo adım ve kapı seslerini görüntüyle senkron üretir), temizse klibin kendi sesi kapılı olarak kullanılır, değilse kütüphane efekti o ana yerleştirilir;
  yaratık sesleri evren kitinden. Yeniden çekilen ya da yeniden adlandırılan planlar video özetinden tanınır ve efektleri yeniden yapılır.
- Çıktı: `KURGU/STEMS/ambiyans.wav`, `efekt.wav` + CapCut için parça listesi `KURGU/ses_parcalari.json`, `_RAPOR/S5_ambiyans_efekt_P<n>.json`.
- Geçme şartı: §7 S5.
- Kim: betik.

**D4. Müzik yerleştirme (S6)**
- Girdi: kesinleşen kurgu, `MUZIK/muzik_listesi.json`, seçilmiş parçalar, diyalog zaman çizelgesi.
- İş: `muzik.py --yerlestir`: parçayı ölçü (bar) sınırından keser, vuruş noktasını ilgili planın başına ±1 kare oturtur (en çok ±%3 zaman esnetme), giriş 1–3 sn / çıkış 2–4 sn,
  diyalog pencerelerinde otomatik kısma (diyalogdan ≥ 12 dB aşağı), müziksiz yerleri boşaltır; leitmotif varlığını ses analiziyle doğrular.
- Çıktı: `KURGU/STEMS/muzik.wav` + ipucu dosyaları, `_RAPOR/S6_muzik_P<n>.json`.
- Geçme şartı: §7 S6. Başarısız ipucu `muzik-supervizoru`'na döner (revizyon aynı yazar).
- Kim: betik + `muzik-supervizoru`.

**D5. Son miks ve master (S7)**
- Girdi: dört stem (diyalog, efekt, ambiyans, müzik), planlı sessizlik listesi.
- İş: `son_miks.py`: stemler toplanır, bütünleşik ses ölçülür, **tek doğrusal kazanç** + 4× aşırı örneklemeli sınırlayıcı (gerçek tepe), yeniden ölçüm; LRA, mono uyumluluk,
  planlanmamış sessizlik, kırpılma; ASR ile anlaşılırlık (B5). CapCut kanalları: Klipler (sesi kapalı), Diyalog, Efekt, Ambiyans, Muzik (müzik açılıp kapanabilir, BK 5.2.1).
- Çıktı: `KURGU/STEMS/*.wav`, `YAYIN/ses_master.wav`, `_RAPOR/S7_miks_P<n>.json`.
- Geçme şartı: §7 S7.
- Kim: betik.

**D6. Kurgu değişince**
- Girdi: `taslak_fark.py` çıktısı (kullanıcının CapCut düzenlemesi ya da yeniden çekim).
- İş: yalnız etkilenen planlarda D1–D5 yeniden çalışır; dosyalar **yerinde** güncellenir, taslak yeniden kurulmaz (BK 5.3.3).
- Çıktı/geçme: D1–D5 ile aynı. Kim: betik.

### E — Yayın ve öğrenme

**E1. Yayın sesi**
- Girdi: dışa aktarılmış video, `YAYIN/ses_master.wav`, Shorts aralıkları, jenerik.
- İş: `son_miks.py --mux`: dışa aktarılan videonun sesi **video yeniden kodlanmadan** master ile değiştirilir (CapCut'ın kodlaması ve kanal ayarları sesi değiştirse bile son ses
  ölçülmüş olur); son dosya yeniden ölçülür. Shorts için ayrı miks (diyalog öne, müzik geri, −14 LUFS, mono kontrol). Jenerik ve seri kancasının müziği ana tema.
  Content ID ön kontrolü yayın uzmanıyla birlikte (bkz. §9).
- Çıktı: `YAYIN/<film>_final.mp4`, `YAYIN/shorts_*.mp4` sesleri, `_RAPOR/S8_yayin_ses.json`.
- Geçme şartı: son dosyada −14 ±1 LUFS, ≤ −1 dBTP.
- Kim: betik.

**E2. Ders defteri ve evren güncellemesi**
- Girdi: bütün S-kapı raporları, `ses-denetcisi` ders adayları.
- İş: tekrar eden kalıplar kurala dönüşür (§8.2 e); yeni sesler, motifler, mekân yatakları, yaratık kitleri evrene yazılır; eşik kalibrasyonu için ölçüm dağılımları saklanır.
- Çıktı: `EVREN/DERSLER/ders_defteri.jsonl`, `EVREN/…` güncellemeleri.
- Kim: betik + ana Claude (kural terfisini onaylar).

## 3. Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) — yalnız kendi alanın

Genel ilkeler (A3 B5, YR §1): tek iş, en az araç, makinece okunabilir çıktı, her çağrı yeni örnek. Ölçüm ve ses işleme **betikte**; ajan yalnız yargı ve yazı işini yapar.
Claude duyamadığı için hiçbir ajandan "dinle ve karar ver" istenmez; ajanlar ölçüm JSON'larını ve meta verileri okur.
Bash izni olan ajanlarda izin, `settings.json` izin kuralı ya da PreToolUse hook'uyla yalnız adı geçen komutlara daraltılır.

### 3.1 `ses-kadrocusu` (yeni)
- **Model:** Opus, efor yüksek (seçim, yargı işi; H/ajan-opus-yuksek).
- **Araçlar:** Read, Write, Glob, Grep, Bash (yalnız `python YZ_FILM/ARACLAR/ses_sec.py …`).
- **Görev:** (1) Karakter kartlarından ses profillerini yazar (cinsiyet, yaş bandı, aksan, perde, tını etiketleri, tempo); (2) her karakter için **Veo ses tarifi** (≤ 10 kelime,
  yaş sözcüğü ve filtre kelimesi yok, ör. `in a low, gravelly male voice`), **etiket ailesi** ve **telaffuz sözlüğü**; (3) dünya kurallarından aksan haritası (aynı halk aynı
  aksan ailesi); (4) `ses_sec.py` sonuçlarını okuyup gerekçeli seçim yapar; ayırt edicilik zayıfsa yeniden arama ister; (5) evrende kayıtlı karakteri yeniden seçmez.
- **Okur:** hikâye v2 karakter bölümü ve dünya kuralları, `EVREN/SESLER/*/ses.json`, `_RAPOR/S1_ses_secim.json`, bu belgenin §5.2 şeması, ders defterinin `alan: ses` kayıtları.
- **Çıktı:** `_SES/ses_profilleri.json`, `_SES/SES_KADROSU.md` (karakter başına seçim gerekçesi, `Ruling: karar — neden — yanlışsa maliyeti` satırları).
  Dönüş: karakter sayısı, seçilen ses adları, en zayıf ayırt edicilik çifti.

### 3.2 `ses-tasarimcisi` (yeni)
- **Model:** Opus, efor yüksek (H/uretim-hatti-v2 adım 3 "ses tasarımcısı (kâğıtta)"; H/ajan-opus-yuksek).
- **Araçlar:** Read, Write, Edit, Glob, Grep, Bash (yalnız `python YZ_FILM/ARACLAR/ses_plani.py …` ve `ses_kutuphanesi.py --ara …`).
- **Görev:** `ses_plani.py --taslak` çıktısını plan plan inceler: otomatik çıkan efekt olaylarını düzeltir (yanlış fiil eşleşmesi, eksik temas sesi), sessizlikleri yerleştirir
  (ifşa öncesi 0,8–2 sn, şok sonrası 1–3 sn, en karanlık anda 10–40 sn müziksiz, doruk öncesi 1–2 sn, soğuk açılışın ilk 3–5 sn'si; Z §5.3), yaratık seslerini tasarlar
  (evren kiti), iç mekândan dışarı bakan planlarda dış katmanı yükseltir, kurgu için J/L ses köprüsü önerir, eksik efekt listesini yazar. `S0` HATA'larını kendisi düzeltir.
- **Okur:** `SAHNELER.json` (`zanaat`, `sureklilik`, `replik`), dünya durumu defteri, `EVREN/MEKANLAR/*/ses.json`, `EVREN/YARATIK_SES/*`, `SES_KUTUPHANESI/DIZIN.json`,
  `Z` §5, `ritim_esikleri.json` (ses anahtarları), ders defteri (`alan: ses`), `_RAPOR/S0_ses_kagit.json`.
- **Çıktı:** `SAHNELER.json → zanaat.ses` ve `sahne_gruplari.<id>.ses` alanları, `_SES/SES_TASARIMI.md` (sahne sahne ses anlatısı), `_SES/EKSIK_EFEKTLER.json`.
  Dönüş: sahne sayısı, efekt olayı sayısı, eksik efekt sayısı, S0 ÖZET satırı.

### 3.3 `muzik-supervizoru` (mevcut taslak yeniden yazılır)
- **Model:** Opus, efor yüksek. Mevcut taslak Sonnet; müzik yerleşimi duygu yargısıdır (Z §1 duygu eğrisi, Z §5.4) ve H/ajan-opus-yuksek önemli işlerde Opus istiyor.
  İstem kalıbı mekanik olduğundan `muzik.py` doldurur; ajan yalnız seçim ve gerekçe yazar.
- **Araçlar:** Read, Write, Glob, Bash (yalnız `python YZ_FILM/ARACLAR/muzik.py --kagit …`).
- **Görev:** (1) Leitmotifler: evrendekini kullanır, yenisini tanımlar (enstrüman, ton/mod, BPM, ölçü, duygu, dönüşümler: sade / tehdit / zafer); (2) ipucu listesi: giriş ve çıkış
  **olayı** (kesme, eylem başı, bakış, karar repliğinin sonu; cümle ortasında asla), tür, motif, vuruş noktaları, seviye, sağlayıcı; (3) leitmotif P1'de sade, doruğa kadar ≥ 3 dönüş,
  doruğunda tam orkestra (Z §5.4); (4) ardışık iki ipucu aynı duygu türünde olmaz; (5) istemlerde sanatçı ve film adı yok, "no vocals"; (6) S6 HATA'larında revizyonu kendisi yapar.
- **Okur:** `SAHNELER.json` (`vurus`, `hedef_duygu`, `yogunluk`, `zanaat.ses.sessizlik`), film düzeyi `duygu_haritasi` ve `vuruslar`, `EVREN/MUZIK/leitmotifler.json`,
  `Z` §1.3 ve §5.3–5.4, `ritim_esikleri.json` (müzik anahtarları), `_RAPOR/S6_*.json` (revizyonda).
- **Çıktı:** `MUZIK/muzik_listesi.json` (§5.5), `MUZIK/MUZIK_PLANI.md`, yeni motifler için `EVREN/MUZIK/leitmotifler.json` aday kaydı. Dönüş: ipucu sayısı, kaplama oranı, motif dönüş sayıları.

### 3.4 `ses-denetcisi` (yeni)
- **Model:** Opus (denetim ve anlam yargısı; H/ajan-opus-yuksek). İçeriği üreten ajanlardan ayrı bir örnek; hiçbir ses dosyasını kendisi üretmez.
- **Araçlar:** Read, Write, Glob, Grep (Bash yok; ölçümler betikten gelir).
- **Görev:** S2–S7 raporlarındaki her HATA/BAYRAK için tek karar: kabul / yol değiştir / yeniden çek / Y2 dudak senkronu / yeniden miksle. Veo'nun metni senaryodan saptığında
  **anlam eşdeğerliğine** bakar (bilgi, ad, ton, merak sorusu değişti mi; değiştiyse yeniden çek). Yeniden çekim için Flow'a gidecek `CORRECTION:` cümlesini yazar
  (ör. `Say the line exactly: "…"; the name is pronounced KESS-truh`). Ders adayı yazar (aynı kök neden ikinci kez görülünce).
- **Okur:** `_RAPOR/S2_*` … `S7_*`, `SESLER/diyalog.json`, `SESLER/hizalama/*.json`, ilgili planların `replik`, `kadraj`, `ekran_disi_ses`, `merak_ac` alanları, ders defteri (`alan: ses`).
- **Çıktı:** `_RAPOR/SES_KARARLARI_P<n>.json` (§5.7), `YENIDEN_URET.json` ekleri (`sebep: "ses"`), `EVREN/DERSLER/adaylar.jsonl`. Dönüş: karar sayıları (kabul/yol/yeniden çek/Y2) ve ÖZET satırı:
  `OZET | ses_hata: 4 | kabul: 2 | yeniden_cek: 1 | yol_degistir: 1 | KRITIK: 0`.

### 3.5 Ajan OLMAYAN işler (bilinçli olarak betikte)
Ses seçimi ölçümü, ayrıştırma, hizalama, dönüştürme, LUFS, dudak ölçümü, ambiyans/efekt yerleşimi, müzik üretimi ve uydurma, son miks: hepsi deterministik ya da model
çalıştıran betik (A3 B4 "deterministik işler betiğe yazılır"). İsteğe bağlı **kör dinleyici sağlayıcısı** (ses girdisi kabul eden bir model API'si, ör. Gemini) yalnız BAYRAK
durumlarında seçenekli sorulara cevap verir ("Bu ses A) doğal B) metalik C) boğuk"; ARIS kör transkripsiyon fikri, A1 B4). Anahtar yoksa atlanır; ana hat ona bağlı değildir.

## 4. Beceri (skill) tarif adımları — kendi alanın

**Yer:** `film-yap` becerisinin altında tek seviye bağlantılı başvuru dosyası `reference/ses.md` (SKILL.md 500 satırın altında kalsın; A3 B4). Ses aşamaları ana becerinin
adımlarıdır, ayrı beceri değildir; ancak dolar harcatan yedekler (Y2 bulut dudak senkronu, Y3 Voice Changer, bulut müzik) `AYARLAR/FILM_AYAR.json → ses_butce` sınırı aşılınca durur.
Ana Claude her adımda önce `python YZ_FILM/ARACLAR/film.py <film> --durum` çıktısına bakar, hafızasına değil (A3 B6).

### 4.1 `reference/ses.md` en üstte duracak kurallar (sıkıştırmadan sonra da görünsün diye ilk 40 satır)
1. Ambiyans için müzik modeli (Lyria vb.) KULLANILMAZ; yataklar gerçek kayıttan (D, H/video-istem-kurali).
2. Klibin kendi ortam sesi yatak olarak kullanılmaz; yalnız kapılı efekt olarak (Z §5.2).
3. Replikler tepe değerine göre DEĞİL, LUFS'a göre eşitlenir.
4. Wav2Lip ve ticari olmayan lisanslı model (MusicGen ağırlıkları, InsightFace modelleri, F5-TTS hazır modelleri) ana hatta kullanılmaz (A3).
5. Müzik sözsüzdür; istemde sanatçı ve film adı yazılmaz; her parçanın kaynak kaydı tutulur (BK 4.5).
6. Dudakları oynayan karakterin üstüne başkasının repliği konmaz (H/video-istem-kurali).
7. Ses kaynaklı yeniden çekim normal kuyruktan gider; Flow uyarısında DUR kuralı aynen geçerli (kesin karar 5).
8. Anahtarlar `AYARLAR/`'dan okunur, yazdırılmaz; Freesound/Gemini anahtarı da öyle.
9. Kullanıcıya soru sorulmaz; ses seçimi ve müzik kararları ekipte (kesin karar 1). Dinleme sayfaları bilgi içindir, kapı değildir.

### 4.2 Adımlar (kopyalanıp işaretlenecek kontrol listesi)
```
SES KONTROL LİSTESİ — <film>
[ ] K0 Kurulum: python YZ_FILM/ARACLAR/ses_olcum.py --kontrol
       (ffmpeg, pyloudnorm, stable-ts, audio-separator, mediapipe, RVC ortamı, ACE-Step ortamı, FluidSynth; eksik → KURULUM.bat ile kur, kurulu varsayma)
[ ] A1 ses-kadrocusu ajanı → _SES/ses_profilleri.json
[ ] A2 python ses_sec.py <film> --ara --olc --dinlet --puanla   → _RAPOR/S1_ses_secim.json
       ses-kadrocusu seçer → python ses_sec.py <film> --sec <karakter>=<voice_id> …   (EVREN'e yazar)
[ ] A3 (yeni karakter varsa) python ses_sec.py <film> --banka <karakter>
       python ses_donustur.py --egit <karakter>            (arka planda; bitince merkez ve F0 istatistiği yazılır)
       (serinin ilk filmi) python ses_kiyas.py --arsiv <B2_klip_klasoru> --karakter <k>  → motor sırası FILM_AYAR.json'a
[ ] A4 python ses_plani.py <film> --taslak → ses-tasarimcisi ajanı inceler/düzeltir
[ ] A5 python ses_kutuphanesi.py --eksik <film> --indir    (yalnız CC0; izin FILM_AYAR.json'da)
[ ] A6 muzik-supervizoru ajanı → MUZIK/muzik_listesi.json → python muzik.py <film> --kagit
[ ] A7 python ses_plani.py <film> --denetle   → HATA varsa yazan ajana geri, en çok 2 tur, sonra ana Claude raporlar
[ ] B1 python seslendir.py <film> --animatik   → _RAPOR/S2a_replik_sure.json (sığmayan replik → yönetmene YENIDEN_YAZ)
[ ] B2 python ses_katmani.py <film> --animatik ; python muzik.py <film> --uret ; python son_miks.py <film> --animatik
       → ANIMATIK/ISITSEL_DOKUM.md habersiz seyirciye
--- video partisi indikçe ---
[ ] C1-C2 python seslendir.py <film> --parti N     (yönlendirici: Yol A ayrıştır→hizala→dönüştür, Yol B TTS)
[ ] C3 ses-denetcisi ajanı → SES_KARARLARI_PN.json ; yeniden çekimler YENIDEN_URET.json'a
--- kurgu partisi hazır olunca ---
[ ] D1 python dudak_denetim.py <film> --parti N
[ ] D2 python diyalog_esitle.py <film> --parti N
[ ] D3 python ses_katmani.py <film> --parti N
[ ] D4 python muzik.py <film> --yerlestir --parti N
[ ] D5 python son_miks.py <film> --parti N        → S3–S7 raporları; HATA → ses-denetcisi → düzelt → yeniden ölç (en çok 3 tur; RE:kurgu_tur_max)
[ ] D6 kurgu değiştiyse: python taslak_fark.py <film> → etkilenen planlarda D1–D5
--- yayın ---
[ ] E1 python son_miks.py <film> --mux <disa_aktarilan.mp4> ; python son_miks.py <film> --shorts
[ ] E2 python ders_defteri.py --topla <film> --alan ses ; python evren.py --guncelle <film> --alan ses
```

### 4.3 Geri besleme döngüsü ve durma koşulları
- Her kapı: **ölç → rapor → karar (ajan) → düzelt → yeniden ölç**. Kâğıtta en çok 2 öz-denetim turu (A3 B4, OpenMontage), kurguda en çok 3 tur (RE:kurgu_tur_max).
- Eşiğe ulaşılamazsa durulmaz, **eksik açıkça raporlanır** (BK §7.13 "yüzüne vur"): hangi replik, hangi ölçü, neden, önerilen yedek ve maliyeti.
- Durma yalnız şu durumlarda: bütçe sınırı (dolar ya da AI84 kredisi), Flow uyarısı (yeniden çekim kuyruğu durur), lisansı belirsiz bir kaynağın kullanılması gerekiyorsa.
- Değerlendirme senaryoları (A3 B4: en az 3): "yeni seride ilk film sesi", "evrendeki karakterlerle ikinci film", "yalnız müziği yeniden yap", "kullanıcı CapCut'ta 5 plan sildi".

## 5. Veri şeması / plan alanları (JSON örneğiyle)

Uyumluluk: mevcut alanlar (`karakterler.<ad>.ses`, `ses_adi`, `replik {karakter, metin, cumleler}`) değişmez. Yeni alanlar Z §6.1'deki `zanaat.ses` alt nesnesine
(`ambiyans, efektler[], muzik_ipucu, sessizlik_sn, diyalog_seviye` adları korunarak) ve `replik` içine isteğe bağlı olarak eklenir. Eski dosyalar çalışmaya devam eder.
Ses örnekleme hızı bütün hatta **48 kHz** (bugünkü kod 44,1 kHz kullanıyor; video sesi standardı 48 kHz, YouTube önerisi 48/96 kHz (bellekten)).

### 5.1 Plan düzeyi: `SAHNELER.json → sahneler[i]` (konuşmalı plan ve onun tepki planı)
```json
{
 "no": 87, "parti": 1, "referans": ["bram"],
 "replik": {
  "karakter": "bram",
  "metin": "They will burn the whole street. And they will start with us.",
  "cumleler": [{"en": "They will burn the whole street.", "tr": "Bütün sokağı yakacaklar."},
               {"en": "And they will start with us.", "tr": "Ve bizden başlayacaklar."}],
  "seviye": "normal",
  "ton_fiili": "says coldly",
  "etiketler": ["firmly"],
  "veo_metin": null
 },
 "zanaat": {
  "plan_tipi": "diyalog", "kadraj": "OY", "klip_sn": 8, "sure_sn": 7.0,
  "eylem_zinciri": [{"bas": 0.0, "bit": 1.5, "ozne": "bram", "fiil": "lowers", "hedef": "clay cup onto table", "govde": "both hands"}],
  "replik_zaman": {"bas": 1.5, "bit": 6.5, "tts_sn": 4.6},
  "kesme": {"tip": "L", "nokta_sn": 6.6, "ses_tasma_sn": 0.0},
  "ses": {
   "diyalog_seviye": "normal",
   "diyalog": {"yol": "A", "agiz_gorunur": "tam", "neden": "OY, konuşan yüz kadrajda"},
   "ambiyans": "S07",
   "efektler": [
    {"id": "E087a", "adim": 0, "kategori": "nesne_birakma", "malzeme": "kil_ahsap", "t_sn": 1.4,
     "kaynak_tercih": "klip", "yedek": "SES_KUTUPHANESI/nesne/kil_bardak_masa_02.wav", "seviye_db_diyaloga_gore": -8},
    {"id": "E087b", "adim": 0, "kategori": "kumas", "malzeme": "yun_pelerin", "t_sn": 0.2,
     "kaynak_tercih": "kutuphane", "seviye_db_diyaloga_gore": -14}
   ],
   "flow_sound": "Sound: a clay cup set down on wood, fire crackling low.",
   "muzik_ipucu": "M06",
   "sessizlik_sn": 0,
   "sessizlik": null,
   "nesne_sesleri": [],
   "video_ozet": null
  }
 }
},
{
 "no": 88, "parti": 1, "referans": ["voss"],
 "ekran_disi_ses": {"karakter": "bram", "metin": "And they will start with us.", "kaynak_plan": 87},
 "zanaat": {
  "plan_tipi": "tepki", "kadraj": "Y", "sure_sn": 2.8,
  "ses": {
   "diyalog_seviye": "normal",
   "diyalog": {"yol": "L_tasma", "agiz_gorunur": "yok", "dinleyen_agiz": "kapali",
               "neden": "Bram'ın 87'deki dönüşmüş sesi taşar; Voss'un ağzı kapalı olmalı"},
   "ambiyans": "S07", "efektler": [], "muzik_ipucu": "M06",
   "sessizlik_sn": 1.6,
   "sessizlik": {"tip": "muziksiz", "bas_sn": 1.2, "sure_sn": 1.6, "neden": "sok_sonrasi"}
  }
 }
}
```

| Alan | Değerler | Doldurur | Ne için |
|---|---|---|---|
| `replik.seviye` | `fisilti` · `yumusak` · `normal` · `bagirma` | `ses_plani.py` (fiilden), tasarımcı düzeltir | RE:diyalog_lufs hedefi |
| `replik.ton_fiili`, `etiketler` | Flow fiili; karakterin etiket ailesinden TTS etiketleri | yönetmen / kadrocu | Yol B ve ses bankası tutarlılığı |
| `replik.veo_metin` | null ya da adların okunuşa göre yazıldığı metin (yalnız Flow istemine gider; altyazı `metin`'den ya da duyulandan) | `ses-denetcisi` (ad yanlış okunduysa) | Telaffuz düzeltmesi, altyazı bozulmaz |
| `ses.diyalog.yol` | `A` (Veo + dönüştürme) · `B` (TTS) · `L_tasma` (önceki planın sesi sürer) · `Y2` (TTS + dudak senkronu) | `ses_plani.py`, kurgu sonrası `ses-denetcisi` | Kesin karar 4 yönlendirmesi |
| `ses.diyalog.agiz_gorunur` | `tam` (Y, CY, OY) · `kismi` (O, OG) · `yok` (G, EG, sırt, ekran dışı) | `ses_plani.py`; kurgu sonrası `dudak_denetim.py` gerçek görüntüden doğrular | Yol seçimi, dudak kapısı |
| `ses.diyalog.dinleyen_agiz` | `kapali` · `serbest` | yönetmen istemi ("listens silently, mouth closed", Z §3.5) | B2 ölçütü (başkasının repliği altında dudak) |
| `ses.efektler[]` | `{id, adim, kategori, malzeme, t_sn, kaynak_tercih: klip/kutuphane/kit, yedek, seviye_db_diyaloga_gore}` | `ses_plani.py` (eylem zincirinden), tasarımcı | Adım başına efekt (kesin karar 2) |
| `ses.flow_sound` | Flow istemine girecek kısa `Sound:` cümlesi (efekt listesinden derlenir; müzik yok) | `ses_plani.py` → istem derleyici | Veo'nun senkron efekt üretmesi |
| `ses.sessizlik` | `{tip: muziksiz/mutlak, bas_sn, sure_sn, neden}`; `sessizlik_sn` eski ad, aynı süre | tasarımcı | Z §5.3, S0 ve S7 |
| `ses.nesne_sesleri[]` | sürekli nesne sesi: `{nesne, durum, ses}` (ör. yanan fener cızırtısı) | dünya durumu defterinden | Ses sürekliliği (§8.2 b) |
| `ses.video_ozet` | indirilen klibin SHA-1 özeti (ilk 12 karakter) | `ses_katmani.py` | Yeniden çekilen planın efektini yenileme (D) |

### 5.2 Karakter sesi: `_SES/ses_profilleri.json` ve kalıcı `EVREN/SESLER/<karakter>/ses.json`
```json
{
 "karakter": "mara",
 "profil": {"cinsiyet": "kadin", "yas_bandi": "orta", "aksan": "british_northern", "perde": "orta_dusuk",
            "tini": ["warm", "slightly husky"], "tempo": "olculu", "enerji": "sakin_kararli"},
 "veo_ses_tarifi": "in a low, warm, slightly husky female voice",
 "etiket_ailesi": ["softly", "whispers", "firmly", "breathless"],
 "telaffuz": {"Kestra": "KESS-truh"},
 "secim": {
  "voice_id": "mrmaApeLxpgZi4RK7oGq", "ses_adi": "Meaghan", "kaynak": "ai84_paylasilan",
  "model": "eleven_v4", "ayarlar": {"stability": null, "similarity_boost": null, "style": null}, "tohum": null,
  "tarih": "2026-10-23", "puan": 0.82,
  "adaylar": [{"voice_id": "…", "puan": 0.77, "elenme": "kadro ayırt ediciliği: voss_2 ile 0,68"}],
  "lisans_notu": "paylaşılan ses; sahibinin kaldırma riski var → banka + RVC modeli sigorta"
 },
 "olcum": {"f0_medyan_hz": 182.0, "f0_p10_p90_hz": [150.0, 241.0], "hiz_kelime_sn": 2.4,
           "merkez": "merkez.npy", "benzerlik_esigi": 0.70},
 "banka": {"klasor": "banka/", "sure_sn": 612, "cumle": 140, "ai84_kredi": 8600},
 "donusum": {"motor": "rvc", "model": "rvc/mara_v1.pth", "egitim_sn": 540, "dogrulama_benzerlik": 0.79},
 "filmler": ["EMBERFALL_1"]
}
```
`ayarlar` ve `tohum` AI84'ün bunları iletip iletmediği ilk çalıştırmada denenince doldurulur (§9). `null` = bilinmiyor, uydurulmaz.

### 5.3 Sahne grubu ve mekân sesi
```json
"sahne_gruplari": {
 "S07": {
  "mekan": "bram_evi_ic", "eksen": ["bram", "voss"], "planlar": [80, 81, 82, 87, 88],
  "ses": {
   "ambiyans": {"yatak": "SES_KUTUPHANESI/yatak/IC_ODA_ahsap_01.wav",
                "katmanlar": [{"ad": "dis_ruzgar_kar", "dosya": "SES_KUTUPHANESI/yatak/DIS_ruzgar_kar_03.wav", "kazanc_db": -9}],
                "seviye_lufs": -34.0, "dongu": true},
   "oda_yaniti": "EVREN/MEKANLAR/bram_evi_ic/oda_ir.wav",
   "gecis": {"capraz_sn": 0.8, "one_alma_sn": 0.5, "zaman_surekli_onceki": false},
   "dis_bakan_planlar": {"82": {"dis_ruzgar_kar": 5}}
  }
 }
}
```
`EVREN/MEKANLAR/<mekan>/ses.json`: `{zemin_malzemesi: "ahsap", oda: {boyut_m: [5,4,2.6], emilim: 0.35}, oda_ir, varsayilan_yatak, katmanlar}` — mekân bir sonraki filmde
aynı sesle döner (kesin karar 3f).

### 5.4 `SESLER/diyalog.json` sürüm 2 (bugünkü dosyanın yerini alır; `capcut_film.py` ve `izleme_paketi.py` okur)
```json
{
 "surum": 2, "ornekleme_hz": 48000,
 "replikler": {
  "87": {
   "karakter": "bram", "yol": "A", "kaynak_klip": "SIRALI_VIDEO/087.mp4",
   "senaryo_metin": "They will burn the whole street. And they will start with us.",
   "veo_metin": "They will burn the whole street, and they'll start with us.",
   "wer": 0.08, "ad_dogru": true, "anlam_esdeger": true, "karar": "kabul",
   "altyazi_metin": "They will burn the whole street, and they'll start with us.",
   "kelimeler": [{"w": "They", "bas": 1.52, "bit": 1.68}, {"w": "will", "bas": 1.68, "bit": 1.84}],
   "bas_sn": 1.52, "bit_sn": 6.31,
   "dosya": "SESLER/donusum/087_bram.wav",
   "donusum": {"motor": "rvc", "model": "bram_v1", "f0_kaydirma_yt": -2, "zarf_gecikme_ms": 6, "benzerlik": 0.81, "asr_wer_sonra": 0.06},
   "seviye": "normal", "olculen_lufs": -19.7, "kazanc_db": 0.2, "oda": "bram_evi_ic", "uzaklik": "yakin",
   "denetim": {"S2": "GEC", "S3": "GEC", "S4": "GEC"}
  },
  "88": {"karakter": "bram", "yol": "L_tasma", "kaynak_plan": 87, "denetim": {"S3": "GEC"}}
 }
}
```
Kural: `altyazi_metin` her zaman **duyulan** sözdür (Yol A'da kabul edilmiş Veo metni, Yol B'de senaryo metni). Eski `cumleler[{dosya, bas, sure, en, tr, kaynak}]` biçimi
`izleme_paketi.py` uyumu için bir sürüm boyunca yanında yazılır.

### 5.5 Müzik: `MUZIK/muzik_listesi.json` ve `EVREN/MUZIK/leitmotifler.json`
```json
{
 "film": "EMBERFALL_1", "kaplama_hedef": [0.40, 0.65],
 "ipuclari": [
  {"id": "M06", "tur": "tema", "motif": "LM_MARA", "donusum": "sade",
   "giris": {"plan": 85, "ofset_sn": 2.0, "olay": "karar_replik_sonu", "rampa_sn": 2.0},
   "cikis": {"plan": 96, "olay": "sahne_sonu", "rampa_sn": 3.0, "tasma_sn": 1.5},
   "hit": [{"plan": 92, "ofset_sn": 0.0, "tur": "guclu_vurus"}],
   "hedef_sure_sn": 74, "duygu": "sefkat>umut", "yogunluk": [4, 6],
   "seviye": {"diyalogsuz_lufs": -18.0, "diyalog_alti_db": 14},
   "saglayici": "acestep", "aday": 3,
   "istem_en": "Intimate orchestral underscore, solo wooden flute melody over soft strings, D dorian, 72 BPM, 3/4, tender and hopeful, no vocals, no choir, cinematic.",
   "secilen": "MUZIK/secilen/M06_b.wav",
   "olcum": {"bpm": 72.1, "ton": "D dorian", "motif_benzerlik": 0.71, "vokal": false}}
 ]
}
```
```json
{
 "LM_MARA": {"karakter": "mara", "enstruman": "solo wooden flute", "ton": "D dorian", "bpm": 72, "olcu": "3/4",
             "motif_midi": "EVREN/MUZIK/LM_MARA.mid", "referans_wav": "EVREN/MUZIK/LM_MARA_ref.wav",
             "kroma_sablon": "EVREN/MUZIK/LM_MARA_kroma.npy",
             "donusumler": {"sade": "solo flute", "tehdit": "low strings, D minor, 60 BPM", "zafer": "full orchestra, 84 BPM"},
             "ilk_film": "EMBERFALL_1", "kullanim": [{"film": "EMBERFALL_1", "ipucu": ["M02", "M06", "M19", "M31"]}]}
}
```
`MUZIK/KAYNAK_KAYDI.json` (lisans kanıtı, Content ID itirazı için): her seçilen dosya için `{dosya, saglayici, model, surum, lisans, istem, tohum, tarih, sha1}`.

### 5.6 Efekt kütüphanesi dizini: `SES_KUTUPHANESI/DIZIN.json`
```json
{"yatak/DIS_ruzgar_kar_03.wav": {"kategori": "yatak", "etiketler": ["dis", "ruzgar", "kar", "gece"], "sure_sn": 184.0,
  "lufs": -31.2, "tepe_dbfs": -9.8, "dongu_uygun": true, "olay_icerir": false, "anlasilir_soz": false,
  "lisans": "CC0", "kaynak_url": "https://freesound.org/…", "indirme_tarihi": "2026-10-23"}}
```

### 5.7 Rapor ve karar biçimi
```json
{"kapi": "S3_dudak", "parti": "P2", "sonuc": "HATA",
 "hatalar": [{"madde": "S3.1", "plan": 212, "olcu": {"ofset_ms": -167, "guven": 0.41}, "esik": "|ofset| ≤ 42 ms",
              "oneri": "replik 0,17 sn erken; plan_kurgu kaynak ofsetini düzelt, yeniden ölç"}],
 "ozet": "OZET | replik: 38 | gec: 35 | bayrak: 2 | HATA: 1"}
```
`_RAPOR/SES_KARARLARI_P<n>.json`: `[{"plan": 212, "kapi": "S3", "karar": "yeniden_olc|kabul|yol_degistir|yeniden_cek|Y2", "gerekce": "…", "correction": null}]`.

### 5.8 Dünya durumu defterinden ses için gereken alanlar (defter süreklilik uzmanının; burada yalnız ihtiyaç)
`{zaman_araligi: [plan_bas, plan_bit], hava: "kar|yagmur|acik", ruzgar: 0-3, gun_saati, ates: {yer, durum}, nesneler: [{ad, durum: "yanik|kapali|zincirli"}],
karakter_durum: [{karakter, durum: "yarali|islak|nefes_nefese"}], kalabalik: "yok|uzak|yakin"}`. Ses aracı bu alanlardan yatak katmanlarını ve sürekli nesne seslerini türetir.

### 5.9 Ders defteri kaydı: `EVREN/DERSLER/ders_defteri.jsonl` (ortak defter; ses kayıtları `alan: "ses"`)
```json
{"id": "SES-007", "alan": "ses", "durum": "kural", "ilk_film": "EMBERFALL_1", "olay_sayisi": 3,
 "belirti": "RVC fısıltı repliklerinde metalik ses; S2 benzerlik 0,55-0,62",
 "kok_neden": "dönüştürücü nefesli sesi taşıyamıyor",
 "kural": "seviye=fisilti ve agiz_gorunur!=tam ise yol B",
 "uygulama": {"dosya": "EVREN/DERSLER/ses_kurallari.json", "anahtar": "yol_kurali.fisilti"},
 "kanit": ["_RAPOR/S2_P1.json#p044", "_RAPOR/S2_P2.json#p131"]}
```

### 5.10 `AYARLAR/FILM_AYAR.json` ses ekleri (anahtar içermez)
```json
{"saglayicilar": {"ses": ["ai84", "sahte"], "ses_donusum": ["rvc", "openvoice", "sahte"], "ayristirma": ["roformer", "demucs"],
                  "muzik": ["acestep", "midi_cc0", "gemini_elle", "sahte"], "dudak_yedek": [], "dinleyici": []},
 "ses_butce": {"ai84_kredi_film_max": 150000, "dolar_film_max": 0},
 "indirme_izni": {"cc0_efekt": true},
 "yollar": {"evren": "C:/Users/Soysal/Desktop/YZ_FILM/EVREN", "ses_kutuphanesi": "C:/Users/Soysal/Desktop/YZ_FILM/SES_KUTUPHANESI",
            "arsiv_klipler": "D:/YZ_FILM_ARSIV/PROJE_B2/PROJE_B2/SIRALI_VIDEO"},
 "ortamlar": {"rvc": "C:/…/venv_rvc/Scripts/python.exe", "acestep": "C:/…/ACE-Step/python.exe"}}
```
Ağır modeller (RVC, ACE-Step) `om_kopru.py` kalıbıyla **ayrı sanal ortamda** çalışır; ana Python 3.10 ortamı bozulmaz.

## 6. Yazılması/değişmesi gereken kod (araç adı, ne yapar, girdi/çıktı, öncelik)

### 6.1 Mevcut koddaki somut ses kusurları (okundu; düzeltilmeden yeni film yapılmamalı)

| Dosya:satır | Kusur | Sonucu | Düzeltme |
|---|---|---|---|
| `seslendir.py:104` | Her cümle **tepe** değerine göre ölçekleniyor (`a / max * 0.6`) | Tepe aynı, yükseklik farklı → D'deki "replikler 9 dB oynuyordu" dersinin muhtemel kaynağı | LUFS eşitleme (`diyalog_esitle.py`) |
| `seslendir.py:67-71` | TTS, Veo'nun konuşma süresine `atempo` 0,8–1,3 ile esnetiliyor | Toplam süre tutar ama heceler dudağa oturmaz (H/proje-b2: "seslerde kayma, dudakla gitmiyor") | Ağzı görünen replikte Yol A; Yol B'de en çok ±%8 (tahmin) |
| `seslendir.py:89` | Cümleler whisper kelimelerine **kelime sayısıyla** bölünüyor | Veo bir kelime ekler ya da atlarsa bütün sonraki cümleler kayar | stable-ts ile bilinen metne hizalama + WER kapısı |
| `seslendir.py:93` | Whisper konuşma duymazsa cümleler klibe "orantılı yayılıyor" | Sessiz hata: ses rastgele saniyeye konur | Konuşma yoksa HATA → yeniden çekim kuyruğu |
| `seslendir.py:102` | TTS başarısızsa sessizce Flow'un sesi kullanılıyor | Aynı karakter iki farklı sesle konuşur, raporda yalnız bir satır | Kapı hatası; `ses-denetcisi` karar verir |
| `seslendir.py:17`, `capcut_film.py:25` | 44,1 kHz | Video sesi standardı 48 kHz; her geçişte yeniden örnekleme | 48 kHz |
| `seslendir.py:54` | demucs `htdemucs` | Depo bakımsız (A3 A3); ayrıştırma zayıfsa dönüştürücü artefakt üretir | BS-RoFormer (python-audio-separator, MIT), yedek demucs |
| `capcut_film.py:116` | Ortam kanalı her replikli klibin **kendi** ayrıştırılmış ortamı (0,8) | Planlar arası ambiyans zıplaması (D: kapı sahnesi dersi) | Sahne başına tek yatak |
| `capcut_film.py:113` | Repliksiz kliplerin kendi sesi tam seviyede (1,0) kalıyor | Veo'nun kendi müziği/ortamı sızar; "No music" katman ayrımı bozulur | Klipler kanalı her zaman sessiz; efekt kapılı olarak ayrı kanalda |
| `capcut_film.py:45,97,126` | Bütün filme tek "geçici akor" (0,45), kısma yok | Müzik diyaloğun altına inmiyor; leitmotif yok | `muzik.py` ipucu yerleşimi + otomatik kısma |
| `film.py:156,163` | Gerçek ses yolu yalnız ilk sağlayıcı `ai84` ise; diğer yolda cümleler 0,8 sn'den başlayıp art arda diziliyor | `sahte` testi gerçek yolun mantığını hiç denemiyor | Yönlendirici her sağlayıcıda aynı mantıkla çalışır; sahte yalnız sesi üretir |
| `film.py:179-181` | Müzik = toplam süre kadar tek dosya | İpucu, motif, sessizlik kavramı yok | `muzik` aşaması ipucu listesiyle |
| `izleme_paketi.py:40` | "duyulan: KİM: …" konuşanın adını yazıyor | Ekran dışı replikte gerçek seyirci adı bilmez; "kim konuştu" kopukluğu yakalanamaz | §8.2 a: işitsel döküm |

### 6.2 Araçlar
Öncelik: **P0** = serinin ilk filminin ses aşamasından önce şart · **P1** = ilk film sırasında · **P2** = sonra.

| Araç | Yeni/değişir | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|---|
| `ses_olcum.py` | yeni (ortak kitaplık) | LUFS (pyloudnorm, MIT; kısa replikte kısa süreli ölçüm), gerçek tepe (ffmpeg `ebur128=peak=true`), F0 (librosa pyin, ISC), konuşmacı gömmesi (SpeechBrain ECAPA, yalnız ölçüm), WER (jiwer), zarf çapraz korelasyonu, ağız açıklığı (MediaPipe Face Landmarker `jawOpen`), kroma benzerliği; `--kontrol` kurulum denetimi | wav/mp4 → sayı/JSON | P0 |
| `seslendir.py` | değişir (yönlendirici) | Replik başına yol seçer (A/B/L_tasma/Y2); `--animatik` bütün replikleri TTS yapar ve süre kapısını çalıştırır; `diyalog.json` v2 yazar; §6.1 kusurlarını kaldırır | `SAHNELER.json`, klipler → `SESLER/*`, `diyalog.json`, `_RAPOR/S2*` | P0 |
| `ses_donustur.py` | yeni | `--ayristir` (BS-RoFormer/demucs), `--hizala` (stable-ts `align` + serbest ASR, WER, ad doğruluğu), `--donustur` (motor sağlayıcısı, F0 kaydırma, söz penceresi kapısı, gecikme/benzerlik ölçümü), `--egit <karakter>` (RVC eğitimi ayrı ortamda) | klip + metin + evren sesi → `SESLER/ayrik`, `hizalama`, `donusum` | P0 |
| `ses_kiyas.py` | yeni | Dönüşüm motorlarını arşivdeki gerçek Veo klipleriyle kör kıyaslar (benzerlik, gecikme, anlaşılırlık, fısıltı/bağırma) ve motor sırasını önerir | arşiv klipleri + karakter → `_RAPOR/S1b_donusum_kiyas.json` | P0 (serinin başında bir kez) |
| `ses_sec.py` | yeni | `--ara` (AI84 paylaşılan ses araması), `--olc` (önizleme sesleri), `--dinlet` (3 replik TTS, önbellekli), `--puanla`, `--sec`, `--banka` (≈10 dk ses bankası); `SES_SECIM.html` | profiller → `EVREN/SESLER/<k>/ses.json`, `_RAPOR/S1_ses_secim.json` | P0 |
| `ses_plani.py` | yeni | `--taslak`: yol/görünürlük, eylem zincirinden efekt olayları (fiil→efekt sözlüğü `efekt_sozlugu.json`), sahne yatakları (dünya durumu defterinden), `flow_sound`, replik seviyesi; `--denetle`: S0 kapısı | `SAHNELER.json`, defter, DIZIN → `zanaat.ses`, `_RAPOR/S0_ses_kagit.json`, `EKSIK_EFEKTLER.json` | P0 |
| `ses_kutuphanesi.py` | yeni | Mevcut 62 efekt + yatakları dizinler (`DIZIN.json`: LUFS, döngü, olay içeriyor mu, anlaşılır söz var mı (ASR), lisans); `--eksik --indir` Freesound CC0 araması ve lisans kaydı | `SES_KUTUPHANESI/` → `DIZIN.json` | Dizinleme P0, arama/indirme P1 |
| `diyalog_esitle.py` | yeniden yazılır | Replik başına LUFS hedefi, oda yanıtı (pyroomacoustics ile mekân boyutundan sentetik; MIT), uzaklık (plan ölçeği), Yol A↔B tını eşleme EQ'su | `diyalog.json` → `SESLER/esit/*`, `_RAPOR/S4_*` | P0 |
| `ses_katmani.py` | yeniden yazılır | Sahne başına tek yatak (döngü, çapraz geçiş, öne alma, dış katman kazancı), efektleri klibin kendi efekt sesindeki başlangıç anına oturtma (yoksa kütüphane), kapılı klip efekti, yaratık kiti, nesne sesleri; video özetiyle yeniden çekim tespiti | kurgu zaman çizelgesi → `KURGU/STEMS/ambiyans.wav`, `efekt.wav`, `ses_parcalari.json`, `_RAPOR/S5_*` | P0 |
| `muzik.py` | yeni (`gemini_muzik.py` bir sağlayıcısına dönüşür) | `--kagit` (S6 kâğıt maddeleri), `--uret` (sağlayıcı zinciri, aday başına ölçüm: BPM, ton, vokal yok, motif kroma benzerliği, kırpılma), `--yerlestir` (bar sınırından kesme, vuruş hizalama ±1 kare, rampalar, diyalog altında kısma), leitmotif MIDI → referans render (FluidSynth, LGPL; CC0 orkestra örnekleri) | `muzik_listesi.json` → `MUZIK/secilen/*`, `KAYNAK_KAYDI.json`, `STEMS/muzik.wav`, `_RAPOR/S6_*` | P0 (sağlayıcılar: `midi_cc0`, `gemini_elle`, `sahte`); `acestep` P1 |
| `dudak_denetim.py` | yeniden yazılır | Plan penceresinde ağız açıklığı ↔ ses zarfı korelasyonu (ofset, güven), konuşan yüz kimliği = replik karakteri, ekran dışı replikte oynayan dudak, bölünmüş klipte söz ortasından atlama; SyncNet isteğe bağlı | kurgu planı, `diyalog.json`, klipler, yüz kimliği çıktısı → `_RAPOR/S3_*` | P0 |
| `son_miks.py` | yeni | Stem toplama, −14 LUFS (doğrusal kazanç + 4× aşırı örneklemeli sınırlayıcı), LRA, mono uyumluluk, planlanmamış sessizlik, ASR anlaşılırlığı; `--mux` (videoyu yeniden kodlamadan ses değiştirme), `--shorts`, `--animatik` | stemler → `YAYIN/ses_master.wav`, `_RAPOR/S7_*`, `S8_*` | P0 |
| `capcut_film.py` | değişir | Kanallar: Klipler (sessiz), Diyalog (replik replik parça; kullanıcı taşıyabilir), Efekt, Ambiyans (sahne parçaları), Muzik (ipucu parçaları); geçici akor yalnız müzik yoksa ve adı "GECICI" ile | `diyalog.json` v2, `ses_parcalari.json`, müzik → CapCut taslağı | P0 |
| `film.py` | değişir | Yeni aşamalar: `ses_kadro` (A1–A3), `ses_kagit` (A4–A7), `animatik_ses` (B), `ses` (C), `ses_kurgu` (D1–D5), `yayin_ses` (E1); AI84 kredi önizlemesi ve `ses_butce` sınırı; imzalara `zanaat.ses` ve evren dosyaları | — | P0 |
| `saglayicilar/` | değişir | Yeni türler: `ses_donusum` (`donustur(film, giris, karakter, cikti, f0_yt)`), `ayristirma` (`ayristir(film, klip, cikti_dir)`), `muzik` imzası `muzik(film, ipucu, cikti, aday)` olur, `dinleyici` (isteğe bağlı); yeni sınıflar `rvc.py`, `openvoice.py`, `roformer.py`, `acestep.py`, `midi_cc0.py`, `gemini_elle.py`; `sahte` hepsini taklit eder | — | P0 (rvc, openvoice, roformer, midi_cc0, sahte); P1 (acestep); P2 (musetalk, sync_so, ai84_vc, lyria) |
| `istem_denetim.py` | değişir | `veo_ses_tarifi` ve `flow_sound` filtre kelimesi taraması; konuşan planda istemde ses tarifi var mı; `flow_sound` "No music." ile bitiyor mu | `SAHNELER.json` → rapor | P0 |
| `izleme_paketi.py` | değişir | "duyulan" satırında ad yerine işitsel tarif; efekt/müzik/sessizlik olayları | `diyalog.json` v2, `zanaat.ses` → `IZLE.md` | P1 (seyirci uzmanıyla ortak) |
| `testler/test_ses.py` | yeni | `ORNEK_3_SAHNE` üzerinde `sahte` sağlayıcılarla uçtan uca ses testi + bozulmuş girdi testleri (§7.10) | ağ ve kredi yok | P0 |

## 7. Makinenin denetleyeceği eşikler (kaynağıyla)

Kodlar Z §6.2 ile aynı: **H** = HATA (geçmez), **B** = BAYRAK (`ses-denetcisi` bakar). Eşiklerin hepsi `ritim_esikleri.json`'a yeni anahtarlarla eklenmeli
(çelişkide JSON geçerli; Z başı). Kaynak sütununda `RE:` olanlar zaten JSON'da var; **(tahmin)** olanlar §7.8'deki kalibrasyonla ayarlanır.

### 7.1 S0 — Kâğıt ses kapısı (`ses_plani.py --denetle`; kredi yok)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S0.1 | Konuşan her planda `yol` ve `agiz_gorunur` dolu; `kadraj` Y/CY/OY olan konuşan planda yol = A | eksik/çelişki 0 | H | §1.2 karar; Z §3.1 ölçekleri |
| S0.2 | Ekran dışı replik planında kadrajdaki karakter `dinleyen_agiz: kapali` ve hareket isteminde "listens silently, mouth closed" | var | H | Z §3.5; H/video-istem-kurali |
| S0.3 | Ses tanıtım kuralı: bir karakterin ekran dışı sesi, o karakter daha önce ekranda konuşurken duyulduktan sonra kullanılır (`gizem_sesi: true` hariç) | ihlal 0 | B | Z §4.1 "Kim?" sorusundan türetildi (tahmin) |
| S0.4 | Konuşan planda hareket isteminde karakterin `veo_ses_tarifi` kelimesi kelimesine var | %100 | H | A1 B3 (DirectorSKILL "bir kez yaz, kelimesi kelimesine tekrarla") |
| S0.5 | `veo_ses_tarifi` ve `flow_sound` içinde filtre kelimesi / yaş sözcüğü | 0 | H | D; `istem_denetim.py` listesi |
| S0.6 | `flow_sound` "No music." ile biter, müzik sözcüğü içermez | evet | H | BK 4.2.1; H/video-istem-kurali |
| S0.7 | Eylem zinciri adımı başına efekt olayı (ya da `sessiz_adim: true`) | ≥ 1 | H | Z §5.1 |
| S0.8 | Efekt zamanı kendi adım aralığında `[bas, bit + 0,3]` | evet | B | (tahmin) |
| S0.9 | Ani (transient) efekt, söz başlangıçlarına ±150 ms'den yakın değil (bilinçli şok hariç) | evet | B | (tahmin) |
| S0.10 | Sahne grubu başına yatak dosyası; aynı mekân + kesintisiz zaman ardışık sahnelerde aynı yatak | 1; aynı | H | Z §5.2 |
| S0.11 | Yatak katmanları ↔ dünya durumu defteri (hava, gün saati, ateş) | çelişki 0 | H | kesin karar 3b |
| S0.12 | Mutlak sessizlik sayısı / süresi | ≤ 2 / ≤ 1 sn | H | RE:mutlak_sessizlik_film_max, RE:mutlak_sessizlik_max_sn |
| S0.13 | En karanlık anda müziksiz süre; soğuk açılışın ilk 3–5 sn'si müziksiz | 10–40 sn; evet | B | Z §5.3 |
| S0.14 | Müzik kaplama; en uzun müziksiz / müzikli blok | %40–65; ≤ 240 / ≤ 300 sn | B | RE:muzik_kaplama_oran, RE:muziksiz_blok_max_sn, RE:muzikli_blok_max_sn |
| S0.15 | Müzik girişi bir olaya bağlı (kesme, eylem başı, bakış, karar repliği sonu); replik penceresinin ortasında giriş | olay var; 0 | H | Z §5.4 |
| S0.16 | Ardışık iki ipucunda aynı duygu türü | 0 | B | Z §5.4 |
| S0.17 | Leitmotif: P1'de sade ilk sunum, doruğa kadar dönüş, doruğunda tam orkestra | var; ≥ 3; var | B | RE:leitmotif_donus_min; Z §5.4 |
| S0.18 | Müzik isteminde sanatçı/film adı; "no vocals" ifadesi | 0; var | H | BK 4.5 |
| S0.19 | Replik `seviye` dolu ya da fiilden çıkarılabilir | %100 | H | RE:diyalog_lufs |
| S0.20 | Uydurma ad geçen replikte konuşan karakterin `telaffuz` kaydı | var | B | (tahmin) |

### 7.2 S1 — Ses seçimi ve dönüşüm motoru (`ses_sec.py`, `ses_kiyas.py`)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S1.1 | Aday: İngilizce, `voice_restricted` değil, önizleme var | evet | H | BK 6.4 (Charmion örneği) |
| S1.2 | Ad telaffuzu: 3 deneme repliğinde adlar ASR'de doğru (gerekirse telaffuz takma adıyla) | hata 0 | H | (tahmin) |
| S1.3 | TTS anlaşılırlığı (ASR WER) | ≤ 0,05 | H | (tahmin) |
| S1.4 | Kararlılık: aynı sesin 3 repliği arası gömme benzerliği | ≥ 0,80 | B | (tahmin) |
| S1.5 | Kadro ayırt ediciliği: iki karakter merkezi arası benzerlik; aynı cinsiyette F0 medyan farkı | ≤ 0,60; ≥ 2 yarım ton | H | (tahmin) |
| S1.6 | Perde bandı uyumu (F0 medyanı). Erkek: düşük < 100, orta 100–140, yüksek > 140 Hz. Kadın: düşük < 165, orta 165–225, yüksek > 225 Hz | profil bandında | B | bant sınırları (tahmin; genel fonetik bilgisi, kaynak açılmadı) |
| S1.7 | Seçim puanı = 0,30 profil uyumu + 0,20 ayırt edicilik + 0,20 kalite (S1.2–S1.3) + 0,15 kararlılık + 0,15 duygu aralığı (3 replik arası LUFS ve F0 yayılımı) | en yüksek | — | ağırlıklar (tahmin) |
| S1.8 | Dönüşüm motoru kıyası (tutulmuş cümleler): benzerlik; zarf gecikmesi; ASR WER artışı | ≥ 0,70; ≤ 20 ms; ≤ 0,05 | H | (tahmin) |

### 7.3 S2 — Replik kapısı (`seslendir.py`, video sonrası)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S2.1 | Yol A planında Veo konuşması bulundu (hizalanmış söz) | var | H | §6.1 (`seslendir.py:93` sessiz hatası) |
| S2.2 | Veo metni ↔ senaryo WER | ≤ 0,10 GEÇ · 0,10–0,25 B (anlam kararı) · > 0,25 H | H/B | A3 "WER eşiği aşılırsa (ör. > %15)" önerisinden; bantlar (tahmin) |
| S2.3 | Karakter adları doğru söylendi | evet | H | B5; Z §4.1 (ad sözle verilir) |
| S2.4 | Veo konuşma hızı | 1,8–3,2 kelime/sn | B | RE:konusma_hizi_kelime_sn (2,5) ve RE:konusma_hizi_agir_kelime_sn (2,0) çevresi; bant (tahmin) |
| S2.5 | Dönüşmüş ses ↔ Veo konuşması zarf gecikmesi | \|gecikme\| ≤ 20 ms | H | (tahmin; 1 karenin yarısından az) |
| S2.6 | Dönüşmüş ses ↔ karakter merkezi benzerliği | ≥ 0,70 | H | (tahmin) |
| S2.7 | Dönüşüm sonrası ASR WER artışı | ≤ 0,05 | B | (tahmin) |
| S2.8 | Aynı karakterin Yol A ↔ Yol B replikleri arası benzerlik | ≥ 0,75 | B | (tahmin) |
| S2.9 | Yol B zaman esnetmesi | ≤ ±%8 | H | (tahmin) |
| S2.10 | Gerçek replik süresi + 0,4 + 0,5 ≤ kullanılabilir pencere | evet | H | Z §2.3; RE:diyalog_giris_payi_sn, RE:diyalog_cikis_payi_sn |
| S2.11 | Örnek tepe | < −0,1 dBFS | H | (tahmin) |

### 7.4 S3 — Dudak denetimi (`dudak_denetim.py`, kurgu sonrası)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S3.1 | Ağız açıklığı ↔ ses zarfı ofseti | \|ofset\| ≤ 42 ms GEÇ · 42–125 ms B · > 125 ms H | H/B | 42 ms = 1 kare @24 fps (hesap); 125 ms ITU-R BT.1359 "ses geride" fark edilme eşiği (bellekten, doğrulanmalı) |
| S3.2 | Korelasyon güveni (tepe değeri) | ≥ 0,3 | B | (tahmin) |
| S3.3 | İsteğe bağlı SyncNet: ofset; güven | 0 ±1 kare; ≥ 3 | B | A3 A1 (LatentSync "sync confidence < 3" filtresi) |
| S3.4 | Ağzı oynayan yüzün kimliği = replik karakteri | evet | H | kesin karar 3c; A2 V2 kimlik çıktısı |
| S3.5 | Ekran dışı replik sırasında kadrajdaki yüzün ağız açıklığı standart sapması | ≤ 0,05 (jawOpen birimi) | H | kural: Z §5 / H/video-istem-kurali; sayı (tahmin) |
| S3.6 | Bölünmüş klipte atlanan aralık bir sözle kesişiyor | 0 | H | D ("aynı klip iki plana bölününce replik yanlış plana") ; RE:klip_bolme_atlama_min_sn |
| S3.7 | Kurguda ağız gerçekten görünüyor mu (yüz yüksekliği ≥ kare yüksekliğinin %8'i ve ağız noktaları bulundu) ↔ planlanan `agiz_gorunur` | uyumlu | B | (tahmin) |
| S3.8 | Karşılıklı konuşmada cevap boşluğu | 0,2–0,6 sn | B | RE:cevap_boslugu_sn |

### 7.5 S4 — Diyalog seviyesi (`diyalog_esitle.py`)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S4.1 | Replik yüksekliği | fısıltı −24 · yumuşak −21,5 · normal −19,5 · bağırma −17 LUFS, ±1 LU | H | RE:diyalog_lufs, RE:diyalog_lufs_tolerans |
| S4.2 | Aynı sahne + aynı karakter + aynı seviye replikler arası fark | ≤ 1 LU | H | RE toleransından türetildi |
| S4.3 | Ölçüm yöntemi: 0,4 sn'den kısa replikte bütünleşik ölçüm yapılmaz, en yüksek anlık (400 ms) değer kullanılır | — | — | A3 A3 (pyloudnorm sınırı) |
| S4.4 | Yol A ↔ Yol B uzun dönem ortalama spektrum farkı (1/3 oktav bantları, 100 Hz–8 kHz) | ≤ 3 dB | B | (tahmin) |
| S4.5 | Aynı mekândaki replikler aynı oda yanıtıyla | evet | H | Z §5.2'nin diyaloğa uygulanması |

### 7.6 S5 — Ambiyans ve efekt (`ses_katmani.py`)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S5.1 | Sahne içinde yatak dosyası sayısı | 1 | H | Z §5.2; D |
| S5.2 | Ambiyans boşluğu (100 ms pencerede < −60 dBFS; planlı mutlak sessizlik hariç) | 0 | H | Z §6.2 #45 "boşluk 0"; −60 (tahmin) |
| S5.3 | Ardışık planların ambiyans kısa süreli yükseklik farkı | ≤ 3 LU | H | RE:ambiyans_sahne_ici_fark_max_lu |
| S5.4 | Ambiyans diyalogun altında | 12–18 dB | H | RE:ambiyans_diyalog_alti_db |
| S5.5 | Sahne geçişinde çapraz geçiş; yeni yatağın öne alınması | 0,5–1,0 sn; 0,3–1,0 sn | B | RE:ambiyans_capraz_gecis_sn, RE:ses_koprusu_sn |
| S5.6 | Efekt diyalogun altında (şok planı hariç) | 3–10 dB | B | RE:efekt_diyalog_alti_db |
| S5.7 | Efekt kaydının `video_ozet`'i = güncel klibin özeti | %100 | H | D ("yeni çekilen planlar efektsiz kalıyordu") |
| S5.8 | Kapılı klip efekti kullanılan pencerede anlaşılır söz ve müzik sızıntısı | 0 | H | Z §5.2; yöntem (tahmin) |
| S5.9 | Yatakta anlaşılır söz (ASR kelime güveni ≥ 0,5) | 0 | H | H/video-istem-kurali (Lyria'nın "yankılanan konuşma" mırıltısı dersi); güven sınırı (tahmin) |
| S5.10 | Her ses parçasının başı ve sonunda yumuşatma (tık önleme) | 10–20 ms | B | (tahmin) |

### 7.7 S6 — Müzik (`muzik.py`)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S6.1 | Parçada söz/vokal (ASR anlaşılır kelime; vokal ayrıştırma enerjisi) | 0 | H | H/uretim-hatti-v2 ("sözsüz") |
| S6.2 | Diyalog sırasında müzik diyalogun altında | ≥ 12 dB | H | RE:muzik_diyalog_alti_min_db |
| S6.3 | Diyalogsuz bölümde müzik yüksekliği | −20…−16 LUFS | B | RE:muzik_diyalogsuz_lufs |
| S6.4 | Kaplama ve blok süreleri (ölçülen müzik stem'inden) | S0.14 ile aynı | B | RE |
| S6.5 | Giriş / çıkış rampası (şok hariç) | 1–3 sn / 2–4 sn | B | RE:muzik_giris_sn, RE:muzik_cikis_sn |
| S6.6 | Vuruş noktası hizası; zaman esnetme; kesim bar sınırında | ±42 ms; ≤ ±%3; ±50 ms | B | (tahmin) |
| S6.7 | Tema ipucunda motif kroma benzerliği; ölçülen leitmotif dönüş sayısı (doruğa kadar) | ≥ 0,6; ≥ 3 | B | RE:leitmotif_donus_min; benzerlik (tahmin) |
| S6.8 | Kaynak kaydı tam ve sağlayıcı lisansı izinli listede | evet | H | B11 |
| S6.9 | Parçada kırpılma; parça içinde ani kesik | 0 | H | (tahmin) |

### 7.8 S7/S8 — Son miks ve yayın (`son_miks.py`)

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| S7.1 | Bütünleşik yükseklik | −14 ±1 LUFS | H | RE:final_lufs, RE:final_lufs_tolerans; H/openmontage |
| S7.2 | Gerçek tepe | ≤ −1 dBTP (kodlama öncesi hedef −1,5) | H | RE:true_peak_max_dbtp; −1,5 payı (tahmin: AAC kodlaması tepeyi artırabilir) |
| S7.3 | Yükseklik aralığı (LRA) | ≤ 14 LU | B | (tahmin) |
| S7.4 | Planlanmamış mutlak sessizlik (`silencedetect n=-50dB d=0.3`) | 0 | H | RE:mutlak_sessizlik_db; d=0,3 (tahmin; A2 V1'deki 1,0 sn yerine kısa) |
| S7.5 | Mono toplamda yükseklik farkı; ortalama faz korelasyonu | ≤ 3 LU; ≥ 0 | B | (tahmin) |
| S7.6 | Son miksteki her replik için ASR ↔ altyazı WER | ≤ 0,15 GEÇ · 0,15–0,30 B · > 0,30 H | H/B | (tahmin) — müziğin/ambiyansın konuşmayı maskelemesinin ölçüsü |
| S7.7 | Kırpılma | 0 | H | — |
| S7.8 | Shorts: yükseklik; gerçek tepe | −14 ±1 LUFS; ≤ −1 dBTP | H | D ("Shorts −21 LUFS çıkmıştı"); H/openmontage |
| S8.1 | Dışa aktarılmış son dosyada S7.1–S7.2 yeniden | geçer | H | — |

### 7.9 Kalibrasyon (eşik uydurmamak için)
- **Dudak (S3.1–S3.2):** B2 arşivinde kullanıcının "seslerde kayma, dudakla gitmiyor" dediği taslak (H/proje-b2) olumlu örnek; kabul edilip yayınlanan son kurgu (v5) olumsuz örnek. Eşik, kaçırma ≤ %10 olacak biçimde seçilir (A2 §7 kuralı).
- **Benzerlik (S1.5, S2.6, S2.8):** ses bankasında eğitime girmeyen cümlelerin karakter merkezine benzerlik dağılımı → 5. yüzdelik "aynı kişi" alt sınırı; kadrodaki diğer seslerin dağılımı → üst sınır.
- **WER (S2.2):** B2/B3 arşivindeki Veo klipleri senaryo metniyle hizalanır; Veo'nun tipik sapma dağılımı çıkarılır. Bu oran bugün bilinmiyor.
- Kalibre edilen değerler `ritim_esikleri.json`'a, kanıt dosyasıyla birlikte ders defterine yazılır (§8.2 e).

### 7.10 Bozuk girdi testleri (`testler/test_ses.py`, `sahte` sağlayıcı, ağ/kredi yok)

| Enjekte edilen bozukluk | Beklenen |
|---|---|
| Bir repliği 200 ms kaydır | S3.1 HATA |
| Ekran dışı replik sırasında ağız açıklığı dizisi oynuyor (ölçüm fonksiyonuna sahte dizi) | S3.5 HATA |
| Tepe faktörü farklı, tepeye göre normalize edilmiş iki replik | S4.1 HATA |
| Bir sahnede iki ayrı yatak | S5.1 HATA |
| Yeniden çekim taklidi: video değişti, efekt kaydı eski | S5.7 HATA |
| Miksin ortasına 1,5 sn dijital sessizlik | S7.4 HATA |
| Sahte ASR sağlayıcısı müzik parçasında kelime bildiriyor | S6.1 HATA |
| −20 LUFS miks | `son_miks.py` düzeltir → S7.1 GEÇ |
| Tema ipucunda motif notaları yok (sahte müzik sağlayıcısı motifsiz üretir) | S6.7 BAYRAK; motifli üretimde GEÇ |

## 8. Kesin kararların (atomik zincir + 6 özellik + gerekiyorsa ses kararı) kendi alanımda uygulanışı

### 8.1 Atomik eylem zinciri (kesin karar 2) → ses
1. **Her adım bir efekt olayıdır.** `eylem_zinciri[k] = {bas, bit, ozne, fiil, hedef, govde}` → `efektler[]`. Fiil sözlüğü (`efekt_sozlugu.json`) kategoriyi verir; malzeme dünyadan gelir:
   zemin (mekân kartı), kumaş (kostüm kartı), nesne malzemesi (nesne kartı). Z §3.7 örneği:
   - P041 `[0.0–3.0] takes two slow steps` → 2 adım sesi (ahşap zemin), adım aralığına eşit yayılmış; `[3.0–5.5] extends her empty left arm` → deri ceket hışırtısı.
   - P042 `[0.0–1.5] thumb and index finger close around the key` → demir anahtarın tahtaya sürtünmesi, adımın SONUNDA (temas anı); `[1.5–2.5] lifts the key` → küçük metal tıkırtı.
   - Bitiş durumunun 0,5 sn tutulduğu an ("holds still") yeni efekt almaz; yalnız yatak duyulur. Hareketsizlik böyle okunur.
2. **Flow'un `Sound:` cümlesi aynı listeden derlenir.** Z'deki derlenmiş örnek ("Sound: creaking floorboards, wind outside. No music.") tam bu yapıdır. Böylece Veo görüntüyle
   senkron efekt üretir; biz o efekti kapılayarak kullanırız ya da kütüphane efektini onun başlangıç anına oturturuz (D3).
3. **Konuşmalı planda en çok 1 adım ve adım replikten önce** (Z §2.3, P087). Adımın efekti ilk sözden en az 150 ms önce biter (S0.9, tahmin); konuşmayı örtmez.
4. **Bitiş durumu = sonraki başlangıç durumu → ses durumu da taşınır.** Bitiş durumunda "yanık fener sağ elde" varsa sonraki planın `nesne_sesleri`'nde fener cızırtısı vardır;
   "zincirli" bir karakterin her adımına zincir şıngırtısı eklenir. Bu, nesne zıplamasının ses karşılığını önler.
5. **Eylem üstünde kesme** (`kesme.tip: eylem`): iki plana yayılan ses olayı (kapının açılışı P041'de başlar, P042'de biter) klibe değil **zaman çizelgesine** yerleştirilir;
   ses kesmenin üstünden akar ve kesmeyi örter.

### 8.2 Altı özellik
**(a) Videodan önce animatik + habersiz seyirci.**
- Animatik, gerçek seçilmiş seslerle (Yol B TTS) kurulur. **Gerçek replik süreleri** plana geri yazılır ve video kredisinden önce süre kapısı çalışır (B1). Kâğıttaki
  `kelime / 2,5` tahmini yerine o sesin gerçek hızı kullanılır (yavaş ve boğuk bir ses aynı repliği daha uzun söyler).
- Seyirci ajanı duyamaz. Bu yüzden ona **işitsel döküm** verilir: konuşanın adı yazılmaz. "Kadrajdaki kadın konuşuyor: …" ya da "ekran dışı: 2. sahnede duyduğun boğuk erkek sesi: …"
  ya da "ekran dışı: daha önce duymadığın bir erkek sesi: …" yazılır; efektler, müzik türü ve sessizlikler de eklenir. Seyirciye "ekran dışı sesi kime ait sandın?" sorulur;
  yanlışsa KRİTİK "kim konuştu belli değil". Kâğıttaki karşılığı S0.3 ses tanıtım kuralıdır.
- Kurgu izleme turunda döküm **plandan değil son miksten** çıkarılır (ASR + ölçülen olaylar). Böylece müzik bir repliği bastırdıysa seyirci o repliği "duymaz" (S7.6); kâğıtta var
  diye seyirciye ulaştı sayılmaz (ARIS kör transkripsiyon ilkesi, A1 B4).

**(b) Dünya durumu defteri + otomatik zıplama denetimi.**
- Defterin ses için gereken alanları §5.8'de. `ses_plani.py` yatak katmanlarını (hava, rüzgâr şiddeti, gün saati, uzak kalabalık), sürekli nesne seslerini (ateş, fener) ve karakter
  durum seslerini (yaralı → ağır nefes, ıslak → ıslak adım) **defterden türetir**; ajan elle seçmez.
- Zıplama denetimi iki katlı: kâğıtta S0.10–S0.11 (yatak defterle çelişiyor mu, aynı mekân ve kesintisiz zamanda yatak değişti mi), seste S5.1–S5.3 (ölçülen seviye
  zıplaması, boşluk). Defterde "zaman_surekli" olan iki sahne arasında yatak çapraz geçiş yapmaz, **kesintisiz devam eder**.

**(c) Referansla otomatik yüz kontrolü → sesin karşılığı: referansla otomatik SES kontrolü.**
- Her son replik, karakterin evren ses merkeziyle karşılaştırılır (S2.6). Bu, yüzdeki SFace karşılaştırmasının ses tarafıdır.
- **Yüz–ses bağı:** ağzı oynayan yüzün kimliği (yüz kapısının çıktısı) = replik karakteri olmalı (S3.4). "Doğru ses, yanlış ağız" ve "doğru ağız, yanlış ses" ikisi de yakalanır.
- Yaratık sesleri evren kitinden gelir; Veo'nun her klipte yeniden icat ettiği yaratık sesi kullanılmaz (kapılı efektte "yaratık sesi" kategorisi dışarıda bırakılır).

**(d) Kare zinciri (son kare → sonraki başlangıç) → ses zinciri.**
- `gecis_turu: devam` olan planlarda ambiyans aynı yatakla kesintisiz sürer; çapraz geçiş yapılmaz.
- Zincirlenmiş iki klibin sınırında aynı olayın iki kez duyulması önlenir: sınırın iki yanındaki kapılı efektlerde ±100 ms (tahmin) içinde aynı kategoriden iki olay varsa biri atılır.
- Klibin ilk 0,3–1,0 sn'si durağandır (Z §2.2); Veo'nun bu kısımdaki ses başlangıcı hiçbir zaman ham kullanılmaz. Her parça 10–20 ms yumuşatılır (S5.10).

**(e) Kendi kendine öğrenen ders defteri.**
- Kaynaklar: S0–S8 raporları ve `ses-denetcisi`'nin kararları. Aynı kök neden **ikinci kez** görülünce (ya da bir kez KRİTİK olunca) aday ders yazılır (§5.9 biçimi).
- Ders türleri ve uygulandığı yer:
  - **Yönlendirme kuralı** (ör. "fısıltı + ağız tam görünmüyor → Yol B") → `EVREN/DERSLER/ses_kurallari.json`; `seslendir.py` açılışta okur.
  - **İstem kuralı** (ör. "Veo 'Kestra'yı yanlış okuyor → `veo_metin` = KESS-truh") → karakterin evren kaydındaki `telaffuz`'a ve istem derleyicisine.
  - **Kütüphane kuralı** (ör. "IC_ODA_02 yatağında uzak mırıltı var") → `DIZIN.json` kara listesi.
  - **Eşik kalibrasyonu** → ölçüm dağılımları `EVREN/DERSLER/olcumler/ses_<film>.json`; yeni eşik `ritim_esikleri.json`'a kanıt bağlantısıyla.
- Yaşam döngüsü: `aday` → `dogrulandi` (≥ 2 olay ya da 1 KRİTİK) → `kural` (ana Claude terfi ettirir, `KARAR_DEFTERI.md`'ye yazar). Bir kural yeni hatalara yol açarsa `geri_alindi`.
- Ses ajanları her çağrıda defterin `alan: ses` ve `durum: kural` kayıtlarını okur. Dersler üretimin sonunda değil, kâğıt aşamasında uygulanır (BK §7.5).

**(f) Kalıcı seri evreni kütüphanesi.**

| Evren klasörü | İçerik | Neden |
|---|---|---|
| `EVREN/SESLER/<karakter>/` | `ses.json` (voice_id, ayarlar, etiket ailesi, Veo ses tarifi, telaffuz), ≈ 10 dk ses bankası, RVC modeli, gömme merkezi, F0 istatistikleri | Karakter filmden filme aynı sesle konuşur. **Ses sigortası:** paylaşılan ses kütüphaneden kaldırılsa bile banka + RVC modeli kimliği korur (herhangi bir TTS sesi RVC ile karaktere çevrilebilir) |
| `EVREN/MUZIK/` | `leitmotifler.json`, motif MIDI'leri, referans render, kroma şablonları, enstrüman paleti, ana tema ve jenerik müziği | Seri boyunca aynı tema döner; motif varlığı ölçülebilir |
| `EVREN/MEKANLAR/<mekan>/ses.json` | zemin malzemesi, oda boyutu ve oda yanıtı, varsayılan yatak ve katmanlar | Aynı ev ikinci filmde aynı akustikle duyulur |
| `EVREN/YARATIK_SES/<yaratik>/` | büyüme evresine göre ses kiti (CC0 hayvan kayıtlarından katmanlı, perde/formant kaydırmalı), kategori listesi | Yaratık her filmde aynı "sesle" ötüşür |
| `EVREN/NESNELER/<nesne>/ses.json` | imza sesi (anahtar, kılıç, kapı) | Kurulum → kullanım zincirinde nesne sesle de tanınır |

### 8.3 Ses/dudak kararı (kesin karar 4) — gerekçe ve hesap
**Seçenekler karşılaştırması**

| Yol | Dudak | Ses tutarlılığı | Metin | Oyunculuk/duygu | 4 GB kartta | Maliyet (film) | Lisans | Karar |
|---|---|---|---|---|---|---|---|---|
| 1. Veo sesi olduğu gibi | kusursuz | zayıf: her klipte ses yeniden icat ediliyor (kullanıcının yaşadığı sorun; A3 A2) | bazen kelime ekleyip atlıyor | iyi | gerekmez | 0 | Flow | Tek başına HAYIR; Yol A'nın ham maddesi |
| 2. TTS + süreye sığdırma (bugünkü `seslendir.py`) | zayıf (H/proje-b2 "dudakla gitmiyor") | tam | tam | TTS'nin; yüz ifadesiyle uyuşmayabilir | gerekmez | ≈ 15 bin AI84 kredisi | AI84 koşulları | Yalnız ağzı görünmeyen replikte (Yol B) |
| 3. TTS + dudak senkronu modeli | iyi, ama ağız bölgesi yeniden üretilir (bulanıklık, diş, yüz kayması riski) | tam | tam | uyumsuzluk riski | LatentSync en az 8 GB (A3); MuseTalk VRAM yazmıyor | bulut: 190 plan × 0,20 $ ≈ 38 $ (fal [arama]) ya da × 0,55–0,67 $ ≈ 105–127 $ (sync.so [arama]) | Wav2Lip ❌; LatentSync'in InsightFace dedektörü ticari değil; MuseTalk MIT ✓ | Yedek Y2 |
| 4. Veo sesi + AI84 Voice Changer | kusursuz | iyi | Veo'nun | korunur | gerekmez | 840–1.040 sn diyalog × ≈ 2.000 kredi/sn (tahmin, BK 6.4) ≈ 1,7–2,1 milyon kredi = bakiyenin (≈ 649 bin, 13.10) 2,6–3,2 katı | AI84 koşulları | HAYIR; tek kritik replikte Y3 |
| **5. Veo sesi + yerel ses dönüştürme (RVC / OpenVoice V2)** | **kusursuz** (zamanlama Veo'nun) | **iyi–çok iyi** (RVC karakter modeli) | Veo'nun → metin kapısı (S2.2) | **korunur** (fısıltı/bağırmada zayıflayabilir) | çalışabilir, ölçülecek (A3: "yerelde CPU veya 4 GB") | dolar 0; ses bankası karakter başına ≈ 8,5 bin AI84 kredisi bir kez | OpenVoice MIT, RVC MIT (A3); ElevenLabs çıktısıyla eğitim koşulu açık soru (§9) | **ANA YOL (Yol A)** |

Diyalog süresi hesabı: Z §2.6 toplam replik 2.100–2.600 kelime ÷ 2,5 kelime/sn (RE:konusma_hizi_kelime_sn) = 840–1.040 sn (14–17 dk). 190 = Z §2.6'daki 40 dk filmin `diyalog` planı sayısı.

**Neden 5. yol:**
1. Seyircinin tek büyük şikâyeti karakter görünüşünün değişmesi (BK 1.4.3, 803 beğeni). Ağız bölgesini yeniden üreten her model, yüz kapısının koruduğu şeyi bozma riski taşır.
   Yol A görüntüye dokunmaz.
2. Kullanıcının yaşadığı iki sorun ("ses klipten klibe değişiyor", "ses dudakla gitmiyor") aynı anda çözülür: dudak Veo'nun, ses evrenin.
3. Oyunculuk yüzle uyumlu kalır: Veo bağırırken ses de bağırır (A3 A2'deki TTS uyumsuzluğu yaşanmaz).
4. Dolar harcaması yok; AI84 kredisi küçük ve bir kerelik (aşağıda).
5. Yol B (TTS) ile aynı tınıya oturur, çünkü RVC modeli o TTS sesiyle eğitilir. Bir sahnede aynı karakterin ekranda ve ekran dışında konuşması aynı kişi gibi duyulur (S2.8).

**Ön koşullar (Yol A'yı güçlendiren üretim kuralları):**
- Konuşan her klipte karakterin `veo_ses_tarifi` istemde kelimesi kelimesine yer alır (S0.4). Veo'nun ürettiği ses hedefe ne kadar yakınsa dönüştürücü o kadar az zorlanır (A3 A2).
- Uydurma adlar Flow'a okunuşlarıyla gider (`veo_metin`); altyazı doğru yazımla kalır.
- Yol A'da konuşma kanalı yalnız hizalanmış söz pencerelerinde dönüştürücüye girer: aynı klipteki yaratık sesi ya da gürültü "insan sesine" çevrilmez.

**Yönlendirme tablosu (`seslendir.py`)**

| Durum | Yol |
|---|---|
| Konuşan yüz kadrajda (Y, CY, OY) | A |
| O / OG (ağız kısmen görünür) | A; kurguda S3.7 ağzın görünmediğini ölçerse B'ye düşebilir |
| G / EG, sırt dönük, omuz üstünde öndeki kişi | B |
| Tepki planı üstünde süren replik | `L_tasma` (önceki A ya da B dosyası sürer) |
| Konuşan görünmüyor ve sahnede hiç ekranda konuşmamış | B + S0.3 BAYRAK |
| Yaratık sesi | evren kiti; dönüştürücüye asla girmez |
| A başarısız: konuşma yok / yanlış kişi konuştu / WER > 0,25 / ad yanlış | Y1 Flow'da yeniden çekim (`CORRECTION:`), en çok 2 → Y2 |
| A başarısız: yalnız benzerlik düşük (S2.6), özellikle fısıltıda | B denenir, S3 ölçülür; geçerse kabul; tekrar ederse ders defterine kural adayı |

**Maliyet hesabı (AI84, 1 kredi/karakter, BK 6.4; kelime başına ≈ 5,7 karakter (tahmin))**

| Kalem | Hesap | Kredi |
|---|---|---|
| Animatik TTS (bütün replikler) | 2.100–2.600 kelime × 5,7 | ≈ 12–15 bin |
| Yol B son sesleri | animatikle aynı metin → önbellek | 0 |
| Değişen replikleri yeniden okutma | (tahmin) | ≈ 10 bin |
| Ses seçimi dinletmesi | 6 karakter × 6 aday × 3 replik × ≈ 70 karakter | ≈ 8 bin |
| Ses bankası (yalnız seride yeni karakter) | 6 karakter × 10 dk × ≈ 150 kelime/dk × 5,7 | ≈ 51 bin (bir kez) |
| **İlk film** | | **≈ 85 bin** (bakiyenin ≈ %13'ü) |
| **Sonraki film** (kadro evrende) | animatik + değişiklik + yeni karakter varsa 8,5 bin | **≈ 25–30 bin** |

Flow tarafı: ses kaynaklı yeniden çekim = 190 × Veo sapma oranı. Oran bilinmiyor (§7.9 ile ölçülecek); %15 varsayılırsa (tahmin) ≈ 29 klip × 12 kredi ≈ 340 kredi, yani
RE:kredi_yeniden_deneme_payi'nın (%20 ≈ 970 kredi, Z §2.6 hesabında) içinde kalır.

**Motor seçimi varsayımla değil ölçümle:** `ses_kiyas.py` (A3 adımı) arşivdeki gerçek Veo klipleriyle OpenVoice V2, RVC ve (lisansı netleşirse) Seed-VC'yi aynı ölçütlerle karşılaştırır;
"TTS süreye sığdırma" da kıyasa girer ki Yol A'nın gerçekten daha iyi olduğu sayıyla görülsün. RVC 4 GB kartta eğitilemezse (tahmin edilemiyor) eğitim bir kez bulutta yapılır,
çıkarım yerelde sürer; bu dolar harcaması bütçe onayına bağlıdır.

### 8.4 Müzik kaynağı kararı (lisans ve leitmotif)

| Kaynak | Ticari YouTube lisansı | Leitmotif denetimi | Otomasyon | Donanım | Karar |
|---|---|---|---|---|---|
| Gemini uygulamasında elle (B2'de FM01–FM34) | Google koşulları; repoda kaynak yok, okunmalı | zayıf (yalnız istem) | YOK: kullanıcı elle üretiyor → kesin karar 1 ve "kullanıcıya elle iş çıkarılmaz" (BK §7.8) ile çelişir | — | Yalnız içe alma sağlayıcısı `gemini_elle` (yedek) |
| **ACE-Step 1.5** | **MIT** (A3 A5) | BPM ve ton kontrolü var; melodi/ses referansıyla koşullama doğrulanmadı | tam; Windows paketi ve `.bat` var (A3) | 2B turbo ≤ 6 GB (INT8 + CPU offload); 4 GB'ta çalışıp çalışmadığı ölçülecek | **ANA üretici** (doku, aksiyon, tema denemesi) |
| **MIDI + CC0 orkestra örnekleri** (FluidSynth ile render) | FluidSynth LGPL (yalnız çalıştırılır); örnek kütüphanesi CC0 olmalı (ör. VSCO 2 Community Edition; lisansı doğrulanmalı) | **tam**: motif notası notasına aynı döner | tam | CPU | **Motif omurgası** + her zaman çalışan yedek |
| YuE2 | bireysel üretici para kazanabilir, şirket lisansı ayrı (A3) | — | — | ağır | HAYIR: sözlü şarkı üretimine odaklı (bellekten); ihtiyacımız sözsüz alt müzik |
| MusicGen | ağırlıklar CC-BY-NC ❌ (A3) | — | — | — | HAYIR |
| Stable Audio Open | ağırlık lisansı belirsiz (A3) | — | — | — | HAYIR (netleşene kadar) |
| ElevenLabs Music | plana bağlı; AI84'te sunulup sunulmadığı bilinmiyor (A3) | — | API | bulut | açık soru |
| Lyria (Vertex API) | Google Cloud koşulları okunmadı | istemle | API | bulut, dolar | P2: lisans ve bütçe netleşince |
| YouTube Ses Kitaplığı | YouTube videolarında kullanım için (bellekten; bazı parçalarda atıf şartı) | yok | elle indirme | — | Acil yedek |

**Karar:**
1. Leitmotifin **kimliği sembolik** tutulur: her motif bir MIDI dosyası + enstrüman + ton/mod + BPM + ölçü olarak evrende saklanır ve CC0 örneklerle referans olarak çalınır.
   Bu, "aynı tema döndü mü?" sorusunu ölçülebilir yapar (kroma şablonu, S6.7).
2. İpuçları **ACE-Step 1.5** ile yerelde üretilir (aday başına 3), istemde motifin enstrümanı, tonu ve temposu yazar; ACE-Step ses referansı kabul ediyorsa motif referansı da
   verilir (doğrulanmalı).
3. `tema` türündeki ipucu 3 adayda da motif testini geçemezse o ipucu **MIDI + CC0 render**'ıyla yapılır (her zaman yasal, her zaman motifli). `doku` ve `aksiyon` ipuçlarında motif şartı yok.
4. Her seçilen dosyanın kaynak kaydı (`KAYNAK_KAYDI.json`: model, sürüm, lisans, istem, tohum, tarih, SHA-1) tutulur. Yayından önce Content ID ön kontrolü yayın uzmanıyla birlikte yapılır
   (video önce özel yüklenir, YouTube'un telif kontrolü sonucu beklenir (bellekten)); talep gelirse kayıt itiraz kanıtıdır.
5. Lyria/Gemini **ambiyans için hiçbir zaman** kullanılmaz (D, H/video-istem-kurali); müzik için de kullanım koşulları okunmadan ana yol olmaz.

### 8.5 Diğer kesin kararlar
- **Karar 1 (yalnız konu sorulur):** ses seçimi, müzik, efekt indirme kararları ekipte. `SES_SECIM.html` ve animatik yalnız bilgi içindir; onay kapısı değildir. CC0 indirme izni
  kurulumda bir kez alınır (BK 5.1.4'teki "indirme kullanıcı onayıyla" kuralı bu biçime çevrilir; §9).
- **Karar 5 (Memmet, bot tespiti):** ses hattı Flow'a hiçbir ek gönderim yapmaz. Ses kaynaklı yeniden çekimler `YENIDEN_URET.json` kuyruğuna girer; Memmet'in tempo ayarları ve
  "olağan dışı uyarısında DUR" kuralı aynen geçerlidir. Yönlendirme, yeniden çekim sayısını azaltacak biçimde kuruludur (sesi bozuk ama dudağı doğru klip yeniden çekilmez, dönüştürülür).
- **Karar 6 (üstün körü iş yok):** sessiz geri dönüşler kaldırıldı (§6.1); her replik ölçülür; motor kıyası yapılmadan motor seçilmez; lisansı belgelenmemiş müzik ya da efekt
  kullanılmaz; ucuz diye Wav2Lip ya da ticari olmayan model kullanılmaz.

## 9. Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

### 9.1 Riskler ve önlemler

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | ElevenLabs/AI84 koşulları: TTS çıktısıyla RVC modeli eğitmek ve paylaşılan sesi bir aracı üzerinden ticari kullanmak izinli mi bilinmiyor. AI84 kriptoyla alınmış bir aracı (06_SERVISLER) | Seri sesi hukuken kırılgan olabilir | Koşullar okunmadan banka/eğitim başlamaz (açık soru S3). Yedekler: kendi tasarladığımız ses (ElevenLabs Voice Design, AI84'te varsa), ticari lisanslı açık TTS ile banka, ya da eğitimsiz OpenVoice V2 (yalnız referans klip) |
| R2 | RVC, Veo'nun gürültülü konuşma kanalında, fısıltıda ve bağırmada metalik ses üretebilir | S2.6'da çok replik kalır | Motor kıyası (A3), söz penceresi kapısı, BS-RoFormer ayrıştırma, fısıltıda Yol B denemesi, ders defteri |
| R3 | RTX 3050 Ti 4 GB: RVC eğitimi, ACE-Step, ayrıştırma yavaş ya da hiç çalışmayabilir | Süre ya da yol değişikliği | K0 kurulum ölçümü; ağır modeller ayrı sanal ortamda; partiler gece; eğitim gerekirse bir kez bulutta (bütçe onayı) |
| R4 | Yeni kitaplıkların Python 3.10 uyumu (audio-separator, stable-ts, ACE-Step 1.5) doğrulanmadı | Kurulum kırılır | `om_kopru.py` kalıbıyla ayrı ortam; ana ortama yalnız hafif ölçüm kitaplıkları |
| R5 | Veo'nun metin sapma ve hiç konuşmama oranı bilinmiyor | Yeniden çekim kredisi | Arşiv kliplerinde ölçülür (§7.9) ve bütçe önizlemesine yazılır |
| R6 | Omuz üstü ya da iki kişilik karede Veo dinleyeni konuşturabilir | Yanlış ağız | S3.4–S3.5 HATA → yeniden çekim; istemde "listens silently, mouth closed" (S0.2) |
| R7 | ACE-Step'in orkestra gerçekçiliği belirsiz; MIDI + CC0 render "maket" gibi duyulabilir; YZ müziğine yanlış Content ID talebi gelebilir | Müzik kalitesi / yayın | Aday başına 3 üretim + ölçüm; ilk filmde kalite kıyası; kaynak kaydı ve yayın öncesi telif kontrolü |
| R8 | CC0 kütüphanesi ince (62 efekt + 6 yatak, 02_ARACLAR); 45–55 sahnelik filme yetmeyebilir | Tekrar eden yataklar | A5 eksik efekt temini; Freesound anahtarı; döngü noktası yumuşatma; aynı yatağın aynı filmde farklı mekânda kullanılmaması (B) |
| R9 | Kullanıcı CapCut'ta sesle oynarsa (seviye, kesim), master'ı muxlamak bu değişikliği ezer | Kullanıcının kararı kaybolur | `son_miks.py` taslağı `taslak_fark.py` ile okur, parça seviyelerini ve kesimleri master'a uygular (BK 5.3.3 "kullanıcının kurgu kararı aynen uygulanır") |
| R10 | MediaPipe sürüm çakışması: OpenMontage için 0.10.14 sabit (BK §7.11), A2 1.1.1 öneriyor | Ağız ölçümü kırılır | Face Landmarker Tasks API'sinin `jawOpen` çıktısı 0.10.14'te denenmeli; çalışıyorsa tek sürüm. OpenMontage zaten kendi ortamında |
| R11 | 44,1 → 48 kHz geçişi mevcut araçlara dokunur | Gerileme | `test_ses.py` + mevcut `test_film.py` |
| R12 | Kısa replikte (< 1,5 sn, tahmin) konuşmacı gömmesi güvenilmez | Yanlış HATA | Kısa replikler aynı sahnedeki komşularıyla birleştirilip ölçülür |
| R13 | Ölçüm modellerinin lisansı (SpeechBrain ECAPA'nın eğitim verisi, SyncNet'in lisans dosyası yok, A3) | Hukukî belirsizlik | Yalnız ölçüm; çıktıya girmez; yine de lisans notu `DIZIN`/kurulum raporuna yazılır |

### 9.2 Diğer uzmanlarla çakışabilecek noktalar

| Uzman | Konu | Benim önerim / ihtiyacım |
|---|---|---|
| İstem mühendisi, yönetmen | Hareket istemine `veo_ses_tarifi` ve `flow_sound` eklenmesi, "video istemi kısa" kuralı (BK 4.2.1) | Kalıp önerisi: `Bram says coldly, in a low gravelly male voice: "…" Sound: … No music.` Ek uzunluk ≤ 10 kelime. Adlar `veo_metin` ile okunuşuna göre |
| Yönetmen | Konuşmalı planda adım replikten önce; tepki planında "mouth closed"; `agiz_gorunur` kadrajdan türer | Z §2.3 ve §3.5 ile uyumlu; yönetmen alanlarını ses aracı okur, değiştirmez |
| Kurgu | J/L kesme ve `kesme.ses_tasma_sn` kimin; klip bölmede atlanan aralığın söz ortasına denk gelmesi | Kurgu karar verir, ses aracı uygular ve S3.6 ile denetler. Bölme noktası hizalama dosyasındaki söz aralarından seçilmeli |
| Süreklilik (dünya durumu defteri) | Defterin ses alanları (§5.8), `zaman_surekli`, nesne durumları | Defter dosya adı ve şeması o uzmandan gelir; ses aracı salt okur |
| Yüz kontrolü | Kare başı yüz kimliği çıktısı (S3.4 için), MediaPipe sürümü | Tek geçişte hem yüz hem ağız açıklığı çıkarılırsa işlem süresi yarıya iner |
| Animatik ve habersiz seyirci | İşitsel döküm; `izleme_paketi.py`'de konuşanın adının yazılmaması; "ekran dışı sesi kime ait sandın?" sorusu; kurgu turunda dökümün son miksten çıkarılması | `IZLE.md` "duyulan" satırının biçimi ortak kararlaştırılmalı |
| Orkestratör (`film.py`) | Aşama adları ve sırası; rapor klasörü: Z §6.2 `RAPORLAR/` diyor, kod `_RAPOR/` kullanıyor | Ben `_RAPOR/` yazdım (koda uygun); tek ad seçilmeli |
| Yayın | Master muxlama, Shorts miksi, jenerik ve seri kancası müziği, Content ID ön kontrolü, YouTube ses ayarları (AAC-LC, 48 kHz, stereo 384 kbps (bellekten)) | Ses tarafı `YAYIN/ses_master.wav` ve ölçüm raporu verir |
| Ders defteri ve evren sahibi | Ortak şema (`alan`), klasör düzeni, kuralı kim terfi ettirir | Ses kayıtları §5.9 biçiminde; kural terfisi ana Claude'da |
| Kalite denetimi | A2 V1'deki "replik penceresinde sessizlik" maddesi ile S2.1 aynı işi yapıyor | Tek yerde (S2.1) tutulsun |
| Hikâye odası | Karakter kartında ses tarifi; konuşan karakter ≤ 8 (RE:konusan_karakter_max) | Aynı cinsiyet ve yaş bandında çok sayıda konuşan karakter ses ayırt ediciliğini zorlaştırır (S1.5); kartta ses tarifi şart |
| Belge içi çelişki (Z) | Z §5.1 ambiyans kaynağı "CC0 banka **ya da demucs ile ayrılmış Flow ortamı**" diyor; Z §5.2 ve D (kapı sahnesi) tek sürekli yatak istiyor | Flow ortamı yatak olarak kullanılmaz, yalnız kapılı efekt olarak (D dersi geçerli) |
| Belge içi çelişki (Z) | Z §6.1 `ses` alanını "müzik süpervizörü" doldurur diyor | `ses` alanını `ses-tasarimcisi` doldurur; `muzik_ipucu`'yu `muzik-supervizoru` |
| Kayıtlı karar (BK §8 #10) | "Gemini müzik + CC0 ambiyans" | Önerim: ACE-Step + MIDI/CC0 (§8.4); gerekçe kesin karar 1 ve BK §7.8. Ana Claude karar defterine yazmalı |
| Kayıtlı karar (BK 5.1.7, §8 #17) | Ses seçimi: 2 aday, kullanıcı seçer; sesler onay noktası | Kesin karar 1 bunu kaldırıyor: seçim otomatik, sayfa yalnız bilgi |

### 9.3 Açık sorular (cevabı bilinmiyor; uydurulmadı)
1. **S1** Flow'da (Omni 1.1 Flash) ses referansı ya da sabit ses özelliği var mı? Repoda bilgi yok. Varsa Yol A'nın ham maddesi çok iyileşir.
2. **S2** AI84: paylaşılan ses aramasında hangi filtreler iletiliyor (cinsiyet, yaş, aksan, kullanım alanı); `eleven_v4` için `voice_settings` ve `seed` iletiliyor mu; Voice Design,
   telaffuz sözlüğü, müzik servisi var mı? (MEMORY.md'ye göre ses efekti servisi yok.) İlk kurulumda küçük denemelerle ölçülecek.
3. **S3** ElevenLabs/AI84 koşulları: TTS çıktısının ses dönüştürme modeli eğitmekte kullanılması ve paylaşılan seslerin aracı üzerinden ticari kullanımı. Paylaşılan ses sahibince
   kaldırılırsa ne olur?
4. **S4** Gemini/Lyria müziğinin para kazanılan YouTube videosunda kullanım koşulları.
5. **S5** ACE-Step 1.5'in 4 GB kartta çalışıp çalışmadığı, istediği Python sürümü, ses referansıyla melodi koşullama yapıp yapamadığı.
6. **S6** RVC eğitiminin 4 GB kartta süresi.
7. **S7** Veo'nun ses biçimi (örnekleme hızı, kanal sayısı): arşivdeki bir klipte `ffprobe` ile bakılacak.
8. **S8** Veo'nun metin sapma ve konuşmama oranı (arşiv kliplerinde ölçülecek; §7.9).
9. **S9** CC0 indirme iznini kurulumda bir kez almak kullanıcıya uygun mu? (Kesin karar 1 ile BK 5.1.4 "indirme kullanıcı onayıyla" arasında.)
10. **S10** `pycapcut` ses parçalarında seviye anahtar karesi (keyframe) destekliyor mu? Destekliyorsa müzik kısması CapCut'ta canlı kalır; yoksa kısma dosyaya işlenir.
11. **S11** Kullanıcının bilgisayarındaki `SES_KUTUPHANESI`'nin gerçek içeriği ve lisans dosyası (repoda yok); ilk çalıştırmada `DIZIN.json` çıkarılınca belli olur.
12. **S12** CC0 orkestra örnek kütüphanesinin seçimi ve lisansının belgeyle doğrulanması.
