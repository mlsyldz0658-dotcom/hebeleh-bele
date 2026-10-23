# Eleştiri — Seyirci ve yapımcı gözü: Bu sistem izlenen bir film çıkarır mı?

Hazırlayan: seyirci-yapımcı eleştirmeni (Claude Opus 5.5). Tarih: 23.10.2026. Durum: TAMAM.

**Okunanlar (tamamı):**
- Yedi tur 2 dosyası: `tur2_senarist.md`, `tur2_yonetmen.md`, `tur2_kurgucu.md`, `tur2_ses-muzik.md`, `tur2_goruntu-sureklilik.md`,
  `tur2_uretim-muhendisi.md`, `tur2_claude-code-mimari.md`.
- Eğitim malzemesi: `BILGI_KURALLARI.md`, `ZANAAT.md`, `ritim_esikleri.json`, `arastirma/01–03`, `FILMLE ILGILI CLAUDE/00–07` ve
  `HAFIZA_YEDEGI/` notları, `YZ_FILM/BILGI/CLAUDE_ICIN.md`, `KARARLAR.md`, `YAPIM_REHBERI.md`.
- Mevcut kod: `film.py`, `saglayicilar/`, `istem_denetim.py`, `puan_oku.py`, `izleme_paketi.py`, `memmet.py` (başlık), `seslendir.py`,
  `capcut_film.py` (başlık), `.claude/agents/*.md`.

**Kısaltmalar:** [SN2] senarist · [YN2] yönetmen · [KU2] kurgucu · [SM2] ses-müzik · [GS2] görüntü-süreklilik · [UM2] üretim mühendisi ·
[CM2] Claude Code mimarisi (hepsi tur 2) · BK BILGI_KURALLARI · ZN ZANAAT · RE ritim_esikleri.json (anahtar adıyla) · AR1–AR3 araştırma 01–03 ·
DR 03_DERSLER · OB 00_OKU_BENI + 05_PROJELER_VE_ARSIV · KR KARARLAR · H/<ad> hafıza notu.

**Sayı etiketleri:** kaynaklı sayının yanında kaynağı yazar · **(hesap)** kaynaktaki sayılardan türetildi · **(tahmin)** kaynağı yok, ilk filmde
ölçülüp ayarlanmalı · **(bellekten; doğrulanmalı)** bildiğim ama bu oturumda açıp doğrulamadığım bilgi.

**Madde kodları:** `EK` = KRİTİK, `EO` = ORTA, `EÇ` = KÜÇÜK. (Diğer belgelerin K0/K1 kapılarıyla, KR adımlarıyla ve S kapılarıyla karışmasın diye.)

**Bu rolün sınırı:** Teknik doğruluğa değil sonuca bakıyorum: YouTube'da biri bu filmi açar mı, ilk 30 sn'de kalır mı, 40 dakikayı bitirir mi,
karakterlere bağlanır mı, YZ kusurları onu rahatsız eder mi? Uzmanların araç ve şema kararlarına yalnız bu sonuca dokundukları yerde değiniyorum.

### Bu belgenin özü (6 satır)
1. Tasarım filmin **doğru** olmasını (aynı yüz, doğru el, zıplamayan nesne, dudakla giden ses) çok iyi güvenceye alıyor. Filmin **canlı ve
   dokunaklı** olmasını güvenceye alan bir katman yok.
2. Yayından önce filmi kimse gerçekten **izlemiyor ve dinlemiyor**: bütün "seyirciler" Claude; kare ve metin okuyor, ses duymuyor. Seyircinin
   en çok fark ettiği YZ kusurları (hareket, ses tınısı, müzik, donuk yüz) bu kanalda görünmüyor.
3. Sistem kendi kendine öğreniyor, ama yalnız Claude'un beğenisinden. Gerçek seyirci verisi (gösterim, tıklama oranı, tutma eğrisi) hatta yok;
   B1'in neden yalnız ≈ 671 kez izlendiği hâlâ bilinmiyor.
4. Müzik ve sesler "kulaksız" seçiliyor. Müzik kaynağı (4 GB'ta 2B model + MIDI yedeği) "maket" tını riski taşıyor ve bunu ölçen bir kapı yok.
5. Paketleme (kapak, başlık, test) sahibi olan uzmanın bulunmadığı tek alan; oysa izlenmenin kapısı orası.
6. Öneriler kesin kararlara uyuyor: kullanıcıya soru yok (yalnız bilgi), atomik zincir korunuyor, Flow temposu değişmiyor, kalite için ek maliyet
   açıkça yazılıyor.

---

## 1. Dört soruya seyirci olarak kısa cevap

| Soru | Cevabım | Neden |
|---|---|---|
| İlk 30 sn'de kalır mıydım? | **Büyük ihtimalle evet** | Kurallar güçlü: ilk 5 sn'de eylem, 20 sn'de soru, ilk 30 sn'de ASL ≤ 3,5, manzara ≤ 1 plan ve ≤ 3 sn, başlık kartı geç (RE `ilk_eylem_max_sn`, `ilk_merak_max_sn`, `ilk30_*`). Risk: açılıştaki ilk yakın planlarda donuk yüz ya da "plastik" görüntü (EK2, EO6) ve kapaktaki vaadin 2. dakikaya kadar bekleyebilmesi (EÇ2) |
| 40 dk sonuna kadar izler miydim? | **Belki** | Hikâye motoru iyi kurulmuş: merak defteri (≤ 90 sn'de yeni soru), parti kancaları, orta nokta, kurulum → kullanım, dramatik ironi (ZN §1, §4). Ama ritim ve duygu yalnız kâğıtta ve durağan karelerde ölçülüyor (EK1, EO9); planlanan film süresinin %63'ü konuşma ve dinleme (EO1); müziğin kalitesi bilinmiyor (EK4). 20–30. dakikalardaki sarkmayı kâğıt göremez |
| Karakterlere bağlanır mıydım? | **En zayıf halka** | Sistem yüzün **aynı** kalmasını garanti ediyor, **canlı** olmasını değil. İfade alanı isteğe bağlı, teslim sözlüğü 5 değer, aday seçimi ifadeye bakmıyor, duygu durumu bir plandan ötekine taşınmıyor (EK2) |
| YZ kusurları beni rahatsız eder mi? | **Yüz, nesne, dudak ve ses zıplamaları büyük ölçüde hayır; hareket, ses tınısı ve müzik evet olabilir** | §7'deki tablo: zıplama türleri çok iyi kapılanmış. Kapısız kalanlar: süzülen ya da donup kalan hareket, ifadesiz yüz, fısıltı ve bağırmada metalik dönüştürülmüş ses, "maket" müzik, 720p'den büyütülmüş yumuşak görüntü |

---

## 2. Korunması gereken güçlü yanlar (eleştiri bunlara dokunmamalı)
- **Kâğıt önce, kredi en son** (ZN K8; [UM2] §4.2.3). Kopuklukların çoğu kredisiz yakalanır. B2'deki ≈ %37 yeniden çekimin (hesap; [GS2] §4.1.2)
  ana çaresi budur.
- **Süreklilik omurgası:** atomik eylem zinciri, dünya durumu defteri, 2 aday + kör gözlem + kod kararı, kimlik demiri, Z1 kare zinciri, durum
  dondurma ([YN2], [GS2]). YZ sinema izleyicisinin tek büyük şikâyeti olan "appearance of the characters keep changing" (803 beğeni; BK §1.4.3)
  doğrudan hedefleniyor.
- **Seyirci tutma kuralları:** soğuk açılış, ilk 2 dk A/B testi, vaat sözleşmesi (başlığın her öğesi ekranda), parti sonu kancası, jenerikten önce
  seri kancası ([SN2] §4.2.1; ZN §1.4).
- **Sesin "amatör" izlerinin silinmesi:** sahne başına tek ambiyans yatağı, replik başına LUFS, J/L kesme, dudağı oynayan karakterin üstüne başka
  replik konmaması ([SM2]; [KU2]).
- **Dürüst bütçe ve takvim:** ≈ 6.318 kredi, ≈ 13 saat Flow, ≈ 2–3 hafta açıkça yazılmış ([UM2] §4.1.3).

---

## 3. KRİTİK maddeler

### EK1 — Film yayından önce hiç "izlenmiyor ve dinlenmiyor" **[KRİTİK]**
**Ne tasarlanmış (kaynaklı):**
- Bütün seyirci kipleri Claude'dur. Animatikte sayfa başına "6 plan × 1 kare + eylem şeridi", kurguda "6 plan × 3 kare" ve son miksin ASR
  metninden çıkan "duyulan" satırı okunur ([KU2] §4.5.4).
- Kurgucu bunu kendisi yazıyor: "Kare paketi izlemek değildir. Seyirci hareketi görmez, sesi duymaz; ritim ve duygu puanı gerçek izleyiciden
  sapabilir" ([KU2] R1). Mimari de aynısını söylüyor: "Ajanlar ses duyamaz, hareketi göremez" ([CM2] R-8). Önlem olarak teknik kapılar
  (V1/V2/V3, SyncNet, LUFS, WER) gösteriliyor.
- "Claude ses DUYAMAZ" ([SM2] giriş). Ses seçimi "yalnız sayıya ve tarife dayanır" ([SM2] SB2-5). Müzik adayı BPM, ton, vokal, motif kroması ve
  kırpılmayla seçilir ([SM2] SB5-2).
- İnsan gözü ve kulağı ancak en sonda, CapCut taslağında devreye girer. Animatik yalnız `--onayli` modda kullanıcıya gösterilir ([KU2] KR4, KR10).

**Seyirci olarak etkisi:** YZ filminde seyircinin ilk fark ettiği şeyler hareket ve ses kusurlarıdır: süzülen yürüyüş, kareler arasında eriyen yüz,
hiç kırpılmayan gözler, fısıltıda metalik ses, sinema değil oyun müziği gibi duyulan doruk, yüze uymayan ses. Bunların hiçbiri metinde ya da plan
başına 3 karede görünmez. Teknik kapılar "hata var mı"yı ölçer; "doğal mı, güzel mi, etkiliyor mu"yu ölçmez. B2'de kâğıt sağlamdı, kurgulanmış
film kopuktu (H/kurgu-izleme-denetimi). Aynı fark bu kez hareket ve ses düzeyinde tekrarlanır: sistem 8/10'u **okuyarak** verir, seyirci
**izleyerek** karar verir.

**Yetmeyen karar:** "Habersiz seyirci = Claude + kare paketi + işitsel döküm" tek kanal; teknik kapılar ise kaliteyi değil hatayı ölçüyor.

**Öneri:**
1. **İşitsel-görsel seyirci** (yeni sağlayıcı türü `izleyici`): video ve ses girdisi kabul eden ayrı bir model (ör. Gemini; video + ses anlama
   yeteneği bellekten, kurulumda doğrulanmalı) render edilmiş MP4'ü izler.
   - Habersizlik aynıdır: modele yalnız MP4 (ilk 2 dk kipinde ayrıca başlık ve kapak) verilir. NOTLAR kanalı yoktur.
   - Çıktı [SN2] §4.5.6 seyirci şemasıdır; iki alan eklenir: `yz_kusurlari[] {zaman, tur: yuz|hareket|ses|dudak|muzik|goruntu, siddet}` ve
     `kapatma_ani {zaman, neden}` (EO7).
   - Kipler: animatik (ses gerçek, görüntü durağan), dikey kesit (madde 2), kurgu turları.
   - İlk filmde **kapı değil BAYRAK**tır. Claude seyircileriyle ve gerçek veriyle (EK3) karşılaştırılır; isabetliyse ders defteri korkuluklarıyla
     kapıya terfi eder.
   - "Hiçbir model kendi çıktısını onaylamaz" (AR1 B4): görseller ve video Google ailesinden geliyor (Nano Banana, Veo). Aynı aileden bir izleyici
     bu ailenin kusurlarına kör olabilir (tahmin). Bu yüzden izleyici **onay** değil **bulgu** kaynağıdır ([GS2] İ-6'daki "ikinci göz" ilkesi).
     Mümkünse ikinci bir model ailesi eklenir.
   - Sınır: bu tür modeller videoyu saniyede ≈ 1 kare örnekler (bellekten; doğrulanmalı). Akıcılık ve kısa erimeler için madde 3'teki betik
     ölçüleri ayrıca şarttır.
2. **Dikey kesit** ([UM2] A14a pilot dalgasının genişletilmiş hâli): animatik geçtikten sonra filmin ilk ≈ 180 saniyesi (P0 + P1'in ilk dakikası)
   videodan son miksine, renk ve büyütmeye kadar **yayın kalitesinde** bitirilir.
   - Ölçek: ilk 120 sn'de ASL ≤ 4,0 → ≈ 30 plan; sonraki 60 sn'de P1 ASL'si 4,7 → ≈ 13 plan; toplam ≈ 43 plan ≈ 35 klip ≈ 420–430 kredi
     (hesap: RE `ilk120_asl_max_sn`, `asl_parti_hedef_sn`, `klip_bolme_oran_hedef`, `kredi_klip_720p`). **Ek kredi değildir**; planlar filmin
     kendisidir ([UM2] pilot ilkesi). Pilotun kapsama şartı ([UM2] A14a: zincir, iki kişi, el–nesne, konuşma, yaratık, düşük ışık) eksik kalırsa
     5–10 kapsama planı eklenir (tahmin).
   - Kesit: (a) işitsel-görsel izleyiciden ve 3 Claude seyircisinden geçer; (b) kullanıcıya **bilgi** olarak gider (madde 4); (c) fragman ve Short
     ham maddesidir (EK5).
   - Kalan ≈ 370 klip ancak kesitten sonra gönderilir. Kesitte görülen sistematik bir sorun (bütün yüzler donuk, müzik ucuz, hareket süzülüyor)
     370 klibe yayılmadan düzeltilir.
3. **Kare paketinin göremediğini ölçen betikler** (ilk filmde BAYRAK): klip başına hareket hızı ve enerjisi (EO4), film boyu enerji eğrisi (EO9),
   konuşma doğallığı tahmincisi (MOS tahmincisi; model ve lisansı doğrulanmalı; EK4), müziğin tını ve dinamik ölçüleri (EK4).
4. **İnsan gözü ve kulağı — soru olarak değil, bilgi olarak:** animatikten ve dikey kesitten sonra 3–5 dakikalık bir "izle-dinle" paketi
   (kesit, ses kadrosu örnekleri, ana tema) kullanıcıya gider: Telegram'a (dosya boyutu sınırı doğrulanmalı) ya da masaüstüne. Kullanıcı
   kendiliğinden itiraz ederse bu bir kesin istek olur ve ilgili aşama yeniden açılır ([SN2] §4.8.1). Kullanıcı susarsa hat beklemez.

**Maliyet:** `izleyici` API ücreti (fiyat doğrulanmadı). 40 dk'lık bir tam izleme ≈ 0,7 M girdi tokeni tutar (hesap: 2.400 sn × saniyede ≈ 290 token;
oran bellekten, doğrulanmalı). Film başına ≈ 4 izleme (animatik, kesit, 2 kurgu turu; tahmin). `usd_tavan_film > 0` gerekir ([UM2] İ-6).
**Sahip:** kurgucu (izleme kipleri ve paket), üretim (sağlayıcı, bütçe, pilot tanımı), mimari (görev defteri), ses ve görüntü (madde 3'ün ölçüleri).
**Kesin kararlar:** 1 (soru yok; paket bilgidir) · 3a (kesit animatikten sonra gelir) · 6 (bu harcama "tasarruf için kaliteden ödün yok"
ilkesinin doğrudan gereğidir).

### EK2 — Oyunculuk tasarlanmıyor: film "doğru ama ruhsuz" çıkabilir **[KRİTİK]**
**Ne tasarlanmış (kaynaklı):**
- Durum nesnesinde yüz ifadesi tek bir isteğe bağlı alandır: `"ifade": "sert (isteğe bağlı)"` ([YN2] §4.5.7).
- Konuşma tonu `teslim` sözlüğü 5 değerle başlıyor: fısıltı, yumuşak, normal, soğuk, bağırma ([SM2] §4.5.2; [SN2] H8). Mikro fiiller birkaç
  tane: `cene_sikar`, `bakis_kaydirir`, `cene_kaldirir` ([YN2] §4.5.11).
- İki aday G1'den geçerse seçim sırası şudur: "(1) BAYRAK sayısı az, (2) kimlik fark payı yüksek, (3) mekân benzerliği yüksek, (4) keskinlik
  yüksek" ([GS2] GS8-3). İfade ve kompozisyon ölçüt değildir.
- Her plan tek video çekimidir; yeniden çekim yalnız hata içindir ([KU2] §4.5.5; [UM2] A14).
- Adımlar 0,5 sn'den sonra başlar, son 1 sn'de karakter "holds still" der gibi durur ([YN2] §4.8.1 kural 3). "Aynı anda hareket eden özne ≤ 1"
  (Y06; BAYRAK, tahmin).
- Konuşan planın başlangıç karesinde ağız kapalı ve görünür olmalıdır ([GS2], [SM2] §3). İfade yazılmazsa kare nötr yüzle açılır.
- Dünya defteri kostümü, yarayı, kiri ve ıslaklığı taşır; gözyaşı, kızarık göz, nefes nefese kalma gibi **duygu izlerini** taşımaz
  ([YN2] §4.5.7; [GS2] §2.1).
- EKRAN dilinde iç durum fiilleri (realizes, knows) yasaktır ([SN2] H8). Doğru bir kural; ama yerine bir "görünür duygu dili" tanımlanmamış.

**Seyirci olarak etkisi:** Anlatıcısız filmde karakterin iç dünyası yalnız yüzden ve sesten okunur (ZN §3.5, Kuleshov). İfadesiz ama tutarlı yüzler,
sahne boyunca değişmeyen duygu, bir önceki planda gözleri dolan kadının bir sonraki planda pürüzsüz nötr yüzle konuşması seyircide "YZ filmi"
hissini en çok uyandıran şeylerdir. Bu bir **duygu zıplamasıdır** ve hiçbir kapı onu aramıyor. Sonuç kopuk değil ama soğuk bir filmdir. Bağ
kurulmazsa merak motoru 40 dakikayı tek başına taşımaz.

**Yetmeyen kararlar:** isteğe bağlı `ifade`; 5 değerli `teslim`; teknik ölçütlü aday seçimi; "bir plan = bir çekim"; Y06 ve uzun "holds still".

**Öneri:**
1. **`zanaat.oyunculuk` alanları** (plan düzeyi; sahibi yönetmen, iç durum ve alt metin senaristten):
   ```json
   "oyunculuk": {
     "ic_durum": "korkusunu saklıyor (kâğıt; seyirciye verilmez)",
     "dis_ifade": {"bas": "kontrollu_sakin", "bit": "gizli_endise"},
     "isaretler": ["cene_sikili", "bakis_kacirir"],
     "siddet": 2,
     "alt_metin": "Kaptan'ı içeri almamak için soğuk davranıyor"
   }
   ```
   - `dis_ifade` sabit sözlüktendir (≈ 12–20 değer; tahmin). Her değerin filtre-güvenli İngilizce karşılığı görsel ve hareket istemine derlenir;
     kör sorudaki karşılığı da tanımlıdır. Örnekler: `gizli_endise` → "a composed face, eyes darting, lips pressed together"; `huzun` → "eyes
     glistening, gaze lowered"; `ofke` → "brow lowered, nostrils flaring, jaw clenched"; `sefkat` → "a soft, warm smile, gentle eyes".
   - Filtre listesinde "cheek" ve "trembles" var (DR). "Tears on her cheek" gibi kalıplar yazılmaz; şablonlar `istem_denetim` testinden geçer.
     Veo'nun bu ifadelere uyumu ölçülmedi; pilotta ölçülür.
   - İnsanlı her planda `baslangic_durumu.ifade` zorunlu olur; "nötr" yazılırsa gerekçe istenir. İfade görsel istemine girer: kimlik nasıl
     başlangıç karesine "pişiyorsa" (AR2 §2.1) duygu da öyle pişer.
2. **Duygu sürekliliği** dünya defterine eklenir: `karakterler.<id>.duygu {durum, siddet, izler: [gozler_kizarik, nefes_nefese, yuz_terli,
   sac_dagilmis]}`. Sahne içinde miras alınır; zaman atlamasında azalma kuralıyla değişir. K0'da "gerekçesiz duygu sıçraması" BAYRAK'tır (tahmin).
   İzler görsel isteme `gorunum` gibi girer. Hikâyenin sahne uçları ([SN2] `giris_durumu` / `cikis_durumu`) duygu durumunu da taşır.
3. **Kör ifade okuması:** `kare-tarifcisi` formuna, beklenen değer gösterilmeden bir soru eklenir: "p1'in yüz ifadesi: neutral / fear / anger /
   sadness / tenderness / surprise / determination / joy / contempt / unclear; şiddet 0–3" ([GS2] İ-4'teki görüntü koordinatlı form).
   Kod cevabı `dis_ifade` ile karşılaştırır.
   - G1'de uyumsuzluk BAYRAK'tır. İki aday da G1'i geçtiyse ve ikisinin kimlik payı da güvenli bandın içindeyse "ifade uyumu" seçim sırasının
     2. ölçütü olur (BAYRAK sayısından hemen sonra).
   - V3'te replik penceresinin ortası ve sonu için aynı soru sorulur.
   - Yeni ajan gerekmez; mevcut kör gözlemcinin formu genişler.
4. **Çoklu çekim (take):** duygu yükü yüksek planlarda 2 video çekimi yapılır. Seçimi kör ifade okuması, V1/V2 ve işitsel-görsel izleyicinin ikili
   karşılaştırması ("hangi çekim daha doğal, hangisinde yapaylık daha az?") yapar.
   - Kaynak: kullanıcının incelediği profesyonel Seedance projesinde "planların 2 varyasyonu üretilip seçiliyor" (BK §4.3 #8;
     H/seedance-director-yontemi).
   - Kapsam: `duygu_tutma` planları (25; ZN §2.6) + vuruş noktalarındaki konuşmalı planlar + ilk 120 sn + doruğun yakın planları ≈ 60–110 plan
     (tahmin).
   - Maliyet: ≈ 720–1.320 kredi, yani tabanın %15–27'si (hesap: plan × 12 kredi, taban 4.860; RE `kredi_klip_720p`, ZN §2.6). Ek Flow süresi
     ≈ 1,5–2,7 saat (hesap: [UM2]'nin "527 gönderim ≈ 12,9 saat" oranıyla). Gönderimler `FLOW_YUK` ve `FLOW_TEMPO` kurallarından geçer.
5. **Canlı bekleme:** Y06 şöyle daraltılır: "durumu değiştiren adım atan özne ≤ 1". Kadrajdaki öbür kişiler için durumu değiştirmeyen bir "canlı
   bekleme" şablonu kullanılır: nefes, göz kırpma, hafif ağırlık aktarma. Son tutmada "holds still" yerine "holds the pose, breathing" denenir.
   Bu bir hipotezdir; pilotta A/B ile "zıplama ve dudak hatası artıyor mu?" ölçülür (tahmin).
6. **`teslim` sözlüğü 5'ten ≈ 12 değere** çıkar (ör. `aci`, `yalvaran`, `alayci`, `sefkatli`, `yorgun`, `aceleci`, `sakin_tehdit`,
   `bogazi_dugumlenen`). Her değer 4 LUFS sınıfından birine eşlenir; [SM2] §4.5.2 bu genişletmeye zaten izin veriyor. Veo'nun hangi fiile tepki
   verdiği pilotta ölçülür.
7. **Sözsüz ses vuruşları:** iç çekiş, kısa gülüş, yutkunma, nefes. Replik bloğunun dışında ayrı bir mikro adım olarak yazılır; böylece "replik
   ortasında gülme/ağlama yok" kuralı ([SN2] §4.8.4-6) bozulmaz. Ses Veo klibinden ya da karakterin evren ses bankasından gelir (TTS ton
   etiketlerinin bunu üretip üretmediği doğrulanmalı).
8. **Kâğıtta oyunculuk eleştirisi:** `plan-elestirmeni` kontrol listesine ([YN2] §4.3.2) iki madde eklenir: "Seyirci bu planda karakterin ne
   hissettiğini yüzünden okuyabilir mi?" ve "İç durum ile dış ifade arasında bir alt metin var mı?" Yeni ajan değil, yeni madde.

**Sahip:** yönetmen (oyunculuk alanları, canlı bekleme), senarist (iç durum, alt metin, sahne uçlarında duygu), görüntü (kör ifade sorusu, seçim
sırası, defterde duygu izleri), ses (teslim sözlüğü, sözsüz sesler), üretim (çekim bütçesi).
**Kesin kararlar:** 2 (ifade bir durum alanıdır ve kareye aittir; değişimi bir mikro adımdır ve 2–3 adım sınırının içinde kalır; canlı bekleme adım
sayılmaz, çünkü durum değiştirmez) · 5 (ek gönderimler aynı tempoyla gider) · 6.

### EK3 — Gerçek seyirciyle bağ yok; B1'in neden tutmadığı hâlâ bilinmiyor **[KRİTİK]**
**Ne tasarlanmış (kaynaklı):**
- Önceki iş "emeğe göre izlenme çok düşük" diye kapandı: B1 ≈ 671 izlenme, 6 abone, Short'lar ≈ 0 (OB).
- Tutma verisi hiç görülmedi; araştırma Data API ile yapıldı (BK §1.8.5).
- Tur 2'de yayın verisi "yalnız kayıt olarak tutulur" ([SN2] §4.1.3) ve "kullanıcı verirse kanıt olarak eklenir" ([SN2] §4.8.3-e). Ders defterinin
  bütün kaynakları iç kaynaklıdır: kapılar, ajanlar, kullanıcı notu ([UM2] §4.5.11).
- 8/10 eşiği Claude'un Claude'u puanlamasıdır. Senarist bunu risk olarak yazıyor ("kâğıtta 8, kurguda 6"; [SN2] R1); kalibrasyon çapası yok
  ([SN2] Q6).

**Yapımcı olarak etkisi:** Sistem "kendi kendine öğreniyor", ama öğrendiği şey Claude'un beğenisi. B1'in sorunu neydi: gösterim mi (YouTube filmi
kimseye önermedi), tıklama mı (kapak ve başlık), tutma mı (film)? Bilinmiyor. Sorun gösterim ya da tıklamaysa, 2–3 haftalık süreklilik mühendisliği
izlenmeyi tek başına artırmaz. Bu teşhis yapılmadan bütün yatırım yönsüzdür.

**Yetmeyen karar:** "Yayın verisi yalnız kayıt"; ders defterine gerçek seyirci kanıtı girmiyor; eşikler gerçek tutmaya karşı hiç ayarlanmıyor.

**Öneri:**
1. **Önce teşhis (P0; yeni film başlamadan):** B1 ve B2 için gösterim sayısı, gösterim tıklama oranı (TO), ortalama izleme süresi ve oranı, tutma
   eğrisi ve trafik kaynakları okunur. Çıktı: `BILGI/KANAL_TESHIS.md` ("B1 neden düşük kaldı: keşif mi, paketleme mi, film mi?"). Bu teşhis EK1–EK5'in
   öncelik sırasını değiştirebilir.
   - Tutma eğrisi YouTube Analytics API ile alınabilir (`elapsedVideoTimeRatio` boyutu, `audienceWatchRatio` ölçüsü; bellekten, doğrulanmalı).
     Gösterim ve TO API'de olmayabilir (bellekten; doğrulanmalı); o durumda YouTube Studio'dan tek seferlik CSV dışa aktarımı yapılır. Bu,
     kullanıcının isteğe bağlı fiziksel işidir.
   - Arşivdeki B2/B3 seyirci raporları ve B1 değerlendirme notları (MEMORY: `FILMLER\PROJE\_DEGERLENDIRME_NOTLARI.md`) yerel oturumda bu
     teşhise eklenir.
2. **`yayin_analiz.py`** (yeni, yerel): salt okuma OAuth izni kurulumda bir kez verilir (Google girişi gibi bir kurulum işi). Belirteç `AYARLAR/`'da
   durur ve yazdırılmaz (BK §6.5). Yayından 48 saat, 7 gün ve 28 gün sonra veri çeker. Tutma eğrisi `KURGU_PLANI` çizelgesine eşlenir; düşüş
   noktaları plan kimliğiyle ders defterine `kaynak: gercek_seyirci` kaydı olarak yazılır. Bu kaynak defterde en yüksek kanıt ağırlığını alır.
3. **Kalibrasyon:** Claude seyircilerinin dakika başına `ilgi` eğrisi, `sikilma` anları ve `kapatma_ani` (EO7) gerçek tutma eğrisiyle karşılaştırılır
   (sıra korelasyonu, isabet). Böylece "kâğıtta 8 = yayında şu tutma" eşlemesi kurulur. Eşikler [SN2] §4.7'deki kalibrasyon kuralıyla, bu kez
   gerçek veriyle ayarlanır.
4. **Erken uyarı:** 48 saatte TO ya da ilk 30 sn tutması kanal ortalamasının altındaysa kapak ve başlık değişikliği önerisi yazılır (EK5). Bu bir
   bilgidir; yükleme ve değişiklik onaylıdır (CLAUDE.md, Yapılacaklar 6).

**Maliyet:** 0 kredi. **Sahip:** üretim (araç), yayın stratejisti (yorum; EK5), kurgucu (çizelge eşlemesi), senarist (hikâye dersleri).
**Kesin kararlar:** 1 (OAuth bir kurulum işidir, yaratıcı karar sorusu değildir; kullanıcı istemezse madde "ölçülemedi" olur) · 3e (öğrenen defter
gerçek veriyle beslenir).

### EK4 — Müzik ve sesler "kulaksız" seçiliyor; müzik "maket" riski taşıyor **[KRİTİK]**
**Ne tasarlanmış (kaynaklı):**
- Ana üretici ACE-Step 1.5, 2B turbo, INT8 + tam CPU offload, 4 GB'ta ([SM2] D-AS, §4.8.4). Yedek `midi_ornek`: MIDI + FluidR3_GM ya da VSCO 2 CE
  örnekleri (bellekten) ([SM2] §4.8.4). Gemini'de elle müzik üretme yolu kapatıldı ([SM2] İ-6).
- Aday seçimi BPM, ton, vokal, motif kroması ve kırpılmayla yapılır ([SM2] SB5-2). Ses uzmanının kendi riski: "ACE-Step orkestra gerçekçiliği ve
  motif sadakati belirsiz; MIDI çalımı 'maket' gibi duyulabilir" ([SM2] R8). Önlemi "aday başına 3 üretim + ölçüm"; ölçüm kaliteyi ölçmüyor.
- Ses kadrosu AI84 paylaşılan seslerinden bir puan formülüyle seçilir: profil uyumu, ayırt edicilik, ASR, kararlılık, duygu aralığı
  ([SM2] S1.8). `SES_SECIM.html` yalnız bilgidir.
- Dönüştürücü fısıltıda ve bağırmada metalik ses üretebilir ([SM2] R3; AR3 A2).
- Yaratık sesi CC0 hayvan kayıtlarından katmanlanır, perde ve formant kaydırılır ([SM2] §4.5.5). Bunu da kimse dinlemez.

**Seyirci olarak etkisi:** Müzik filmin %40–65'ini kaplar (RE `muzik_kaplama_oran`) ve duygunun yarısını taşır. "Oyun müziği" ya da General MIDI
tınısında bir doruk en iyi görüntüyü bile ucuzlatır (tahmin). Yüze uymayan bir ses (genç yüze yaşlı ses, sert karaktere yumuşak ses) karakterin
inandırıcılığını bitirir; F0 ve gömme ölçüsü bunu görmez. "Yavru yaratık aşırı şirin" kullanıcının imzasıdır (BK §2.5); yavrunun sesi şirin değilse
imza kaybolur.

**Yetmeyen kararlar:** yalnız ölçüyle seçim; GM örnekleriyle çalınan yedeğin yayına girebilmesi; müzik kalitesini ölçen bir kapının olmaması.

**Öneri:**
1. **Müzik kalite kapısı** (S6'ya ek): her ipucunun adayları işitsel modelle ikili karşılaştırılır ("hangisi sinema filmi müziğine benziyor, hangisi
   yapay ya da ucuz?"). Yanında ölçüler: spektral genişlik, dinamik aralık, stereo genişlik, artefakt. Çapa olarak lisanslı birkaç referans parça
   kullanılır; bunlar yalnız karşılaştırmaya girer, yayına girmez (tahmin). İlk filmde BAYRAK'tır; EK3 verisiyle kalibre edilir.
2. **Kaynak merdiveni:** `acestep` → **lisanslı kütüphane** (ör. YouTube Ses Kitaplığı; YouTube videolarında kullanım izni var, bellekten; koşullar
   doğrulanmalı) → ticari koşulları okunmuş bir üretici (ör. ElevenLabs Music `music.compose`; [SM2] D-EL; koşullar henüz okunmadı) → `midi_ornek`
   **yalnız animatik taslağı ve motif omurgası** için. Yayında tema ipucu GM örnekleriyle çalınmaz (tahmin: bu tını "ucuz" duyulur). Kaynak kaydı
   (`KAYNAK_KAYDI.json`) aynen kalır.
3. **Ses–yüz uyumu:** son 3 ses adayı için işitsel modele kör soru sorulur: "Bu ses bu yüze (kart görseli) uyuyor mu; yaş, enerji, karizma?"
   30 sn'lik örnek ayrıca kullanıcıya **bilgi** olarak gider. Aynı yöntem yaratık ses kitine de uygulanır ("bu ses sevimli bir yavru mu, korkunç bir
   canavar mı?").
4. **Dönüşüm doğallığı:** S2'ye konuşma doğallığı tahmincisi eklenir (ör. UTMOS türü bir MOS tahmincisi; lisans ve Windows/CPU uyumu doğrulanmalı),
   BAYRAK olarak. Fısıltı ve bağırma için `yol_kurali` dersleri ([SM2] §4.8.2-e) birikmesi beklenmeden pilotta ölçülür.

**Maliyet:** lisans ya da abonelik ücreti (doğrulanmadı) ve `izleyici` çağrıları (EK1). **Sahip:** ses-müzik; üretim (bütçe, sağlayıcı); kurgucu (paket).
**Kesin kararlar:** 1 (dinleme paketi bilgidir) · 6 (lisans parası "kaliteden ödün yok" gereğidir).

### EK5 — Paketleme (kapak, başlık, test) sahipsiz **[KRİTİK]**
**Ne tasarlanmış (kaynaklı):**
- Yedi uzmanın hiçbiri yayın ve kanal stratejisi uzmanı değil; senarist bunu açıkça yazıyor: "yayın uzmanı yok" ([SN2] Q5).
- Başlık hikâye odasında yazılıyor (iyi; [SN2] §4.2.1). Kapak: `kare-tarifcisi` kapak kipi (anatomi, yazı, kimlik) + `juri-uyesi·youtube_stratejisti`
  seçimi ([CM2] A17). Kural: "Filmde olmayan kare kapak olamaz" ([SN2] §4.2.1-2).
- İlk 2 dk testinde seyirci kapağın kendisini değil **tarifini** görür ([SN2] H12; [KU2] §4.5.4).
- Kapak adayı sayısı, küçük boyutta okunurluk, tıklama testi ve yayından sonra değiştirme yok.
- B1'in Short'ları ≈ 0 izlendi (OB).

**Yapımcı olarak etkisi:** Film ne kadar iyi olursa olsun, kapak ve başlık tıklatmazsa izlenmez. Sistem 2–3 haftayı ve ≈ 350–550 ajan çağrısını filme
([UM2] §4.1.3), birkaç çağrıyı pakete ayırıyor. "Filmdeki kare" kuralı kapağı 720p video karesine ya da başlangıç görseline bağlar; oysa kapak, küçük
boyutta okunacak biçimde ayrıca kurulmuş bir görseldir. Kuralın dayandığı madde (BK §1.7.6) yalnız yanıltıcı kapağı ("son fotoğraf" gibi sahte
vaatleri) yasaklıyor.

**Öneri:**
1. **`yayin-stratejisti`** (yeni ajan, opus/high; mevcut `yayin-paketcisi` taslağı bu role dönüşür). Açılma gerekçesi [CM] Ç-10 ölçütüdür
   ([YN2] §4.3): ayrı dosyaların sahibidir (`YAYIN/PAKET.json`, `KAPAK_SPEC.json`) ve kanal verisini yorumlayan tek roldür. Görevi: kanal teşhisi
   (EK3), başlık seçimi (hikâyenin adaylarından; [SN2] §4.2.1), kapak şartnamesi, Short ve fragman planı, yayın zamanı, 48 saat izleme.
2. **Kapak hattı:** kapak filmde olan bir **anı** gösterir ama filmdeki karenin kendisi olmak zorunda değildir. Aynı kartlarla, kapak için ayrıca
   kurulmuş, yüksek çözünürlüklü 8–12 aday üretilir (0 kredi, Gemini paketi; tahmin).
   - Denetim: anatomi, yazı ve kimlik (mevcut `kare_denetim --serbest`); küçük boyutta okunurluk ("168×94 piksele indirildiğinde yüz ve yaratık
     seçiliyor mu?" kör sorusu; ölçü tahmin); kazanan kapak kalıbı (BK §1.7).
   - Seçim: 3 kör seyircinin "bu başlık ve bu kapakla tıklar mıydın?" ikili karşılaştırması (tahmin; EK3 verisiyle kalibre edilir).
   - Kapak görseli üretildikten sonra ilk 2 dk testi kapak **tarifiyle** değil **görselin kendisiyle** yapılır (Claude görsel okuyabilir).
3. **Yayın sonrası test:** YouTube Studio'nun kapak test özelliğiyle ("Test & Compare"; bellekten, kanalda açık olup olmadığı doğrulanmalı)
   3 kapak denenir. Başlık testi varsa o da kullanılır.
4. **Fragman ve Short:** dikey kesitten (EK1) 30–60 sn'lik bir fragman çıkar; filmle aynı gün ya da önce yayınlanır. Short adayları zaten hikâyede
   yazılıyor ([SN2] §4.2.1-4); dikey kadraja uygun anlardan seçilir (EÇ6).

**Sahip:** yeni yayın stratejisti; görüntü (kapak üretimi ve denetimi); senarist (başlık ve vaat sözleşmesi).
**Kesin kararlar:** 1 (kapak seçimi ekiptedir; yükleme isteğe bağlı ve onaylıdır, CLAUDE.md).

---

## 4. ORTA maddeler

### EO1 — Tür vaadi ve gösteri açığı **[ORTA]**
- **Gözlem:** ZN §2.6 hedef dağılımında diyalog (190) + tepki (90) = 280/495 plan (%57); bu planlar plan süresinin 1.448/2.313 sn'sini (%63)
  kaplar. Kuruluş + geçiş 105 sn ile %4,5'tir (hesap). Geçiş tavanı 3 sn'dir ("gereksiz uzun" notu; ZN §2.1). Üretilebilirlik taraması "kalabalık
  savaş, hızlı dövüş"ü Flow'da zayıf sayar ([SN2] H1-4). Kanca aileleri ise gösteri vaat eder: ejderha, taht, ordu (BK §2.1); kazanan kapaklarda
  "heybetli yaratık" var (BK §1.7.3). ZN §1.2'deki "vaadin eğlencesi" vuruşunun (14–19. dk) ölçüsü yok.
- **Etki:** Kapakta heybetli bir yaratık, filmde kulübede karşılıklı konuşmalar. Seyirci "söz verilen film bu değil" der. Kazanan filmlerin diyalog
  ile gösteri oranı bilinmiyor; bu yüzden bu madde bir hipotezdir (tahmin).
- **Öneri:** `seyirlik_anlar` (vitrin anları) defteri (sahibi senarist; planı yönetmen):
  - Parti başına ≥ 2 vitrin anı (tahmin). Veo'nun güçlü olduğu türlerden seçilir: tilt ya da pan ile ölçek ifşası, uçuş ve yükseklik, hava olayı,
    ateş ve ışık, siluet kalabalık, manzara + yaratık.
  - Her vitrin anı 3–6 plandır; 10 sn klip ve 2 çekim izni (EK2-4) ve gerekirse 1080p (EO6) alır.
  - Zaman çizelgesinde "en uzun gösterisiz aralık ≤ 6 dk" BAYRAK'tır (tahmin).
  - Vitrin planlarına süre istisnası: ≤ 6–7 sn (tahmin). "Gereksiz uzun" notu bilgi taşımayan manzara için verilmişti (BK §3.1); bilgi ve duygu
    taşıyan ölçek planı için değil. ZN §2.1'de "ilk kez görülen mekân ≤ 5 sn" istisnası zaten var.
  - Doruk, kalabalık yüzlerine değil "iki kişi + yaratık + çevre" ölçeğine kurulur ve ses tasarımıyla büyütülür.
  - Kapak ve Short adayları bu anlardan çıkar (EK5).

### EO2 — Metrikler aşırı açıklamaya itiyor **[ORTA]**
- **Gözlem:** Anlaşılırlık ≥ 8 ve özet eşleşmesi ≥ 0,80 (RE `seyirci_olcut_hedef`, `ozet_eslesme_min`); risk ≤ 180 sn'de sözle söylenir ve her
  parti başında tazelenir; büyük sır hem görüntüyle hem replikle verilir; ad ≤ 120 sn (ZN §4.1). Bunları ölçen seyirci dikkatle okuyan bir
  Claude'dur ve netliği ödüllendirir.
- **Etki:** Bilgi repliğe yığıldıkça diyalog "her şeyi söyleyen" bir hâl alır. Seyirci "bana film değil açıklama anlatılıyor" der. B2 dersi netliğin
  şart olduğunu gösterdi ("bilmesem ne izledim"; H/kurgu-izleme-denetimi); ama aşırısı da izleyiciyi kaybettirir.
- **Öneri:**
  - Seyirci formuna iki soru: "Gereksiz yere açıklanan ya da tekrarlanan yer neresiydi?" ve "Kendini aptal yerine konmuş hissettiğin an oldu mu?"
    (tahmin).
  - `anahtar_olgular` için **görsel taşıma oranı:** olguların ≥ %50'si öncelikle görüntü ya da eylemle verilir (tahmin; BAYRAK).
  - Diyalog editörüne klişe ve açıklama listesi ("As you know", "We need to talk", "I won't let you down" gibi) ve ZN §4.5'teki "bilgi taşıyan
    replikte çatışma olur" kuralının denetimi.
  - Özet eşleşmesi ≥ 0,80 yalnız `kritik` olgularda HATA olur; diğerlerinde BAYRAK (tahmin).

### EO3 — Diyalog ritmi: masa başı okuma hissi **[ORTA]**
- **Gözlem:** Klipte tek konuşan, ≤ 16 kelime; üst üste konuşma yok; replik ortasında gülme ya da ağlama yok; konuşma ile el işi aynı planda yok
  ([SN2] H8, §4.8.4-6; ZN §2.3). Bu kuralların teknik gerekçesi doğru (dudak bozulması).
- **Etki:** Her replik ayrı bir yakın planda ve karakterler konuşurken hiçbir şey yapmıyor. Seyirci bunu "sırayla okunan replikler" diye duyar.
  Ekipte İngilizce diyaloğu ana dil kulağıyla dinleyen bir rol tanımlı değil.
- **Öneri** (kurallar bozulmadan):
  - **İş yaparken konuşma illüzyonu:** replik L taşmasıyla ağzın görünmediği bir eylem planının (el, sırt, geniş plan) üstünde sürer ([KU2] 0 kredi
    merdiveni #3; ses tanıtım kuralı korunur). Sahne başına ≥ 1 (tahmin).
  - **Söz kesme:** A'nın repliği "—" ile yazılır ("I never—"); Veo yarım söyler, kesme hemen ardından gelir. B'nin repliği sert kesmeyle kendi
    planında başlar. Dudak kuralı bozulmaz; metin kapısı "—" işaretini tanır (tahmin).
  - Cevap boşluğu kuralının (çatışmada 0,2 sn, şaşkınlıkta 1–2 sn; ZN §5.5) kurguda gerçekten uygulandığı ölçülür.
  - Diyalog editörüne alt metin, yarım cümle ve kısaltma doğallığı maddeleri. Sahne TTS ile okutulup işitsel modele "doğal bir konuşma mı?" diye
    sorulur (EK1; tahmin).

### EO4 — Hareket kalitesi: süzülme, donup kalma, kıpırtısız figüranlar **[ORTA]**
- **Gözlem:** Y06 "tek özne hareket eder" (BAYRAK, tahmin), adımların başında ve sonunda "holds still" ([YN2]). Kurguda hız ayarı 0,90–1,15× yalnız
  0 kredi merdiveninin 9. basamağıdır ([KU2] §4.5.5). V1 donmayı ve titremeyi ölçer ([GS2]); "doğal hız" ölçüsü yok.
- **Etki:** YZ videolarında sık görülen yavaş, süzülen hareket ve kıpırtısız arka plan figürleri seyircide YZ hissini en hızlı uyandıran şeylerdendir
  (tahmin; genel gözlem).
- **Öneri:**
  - V2'ye **hareket hızı ölçüsü:** özne kutusunun saniyedeki yer değiştirmesi ve optik akış büyüklüğü, fiil sözlüğüne eklenecek `beklenen_hiz`
    aralığıyla karşılaştırılır (`sure_carpani` gibi ders defteriyle kalibre edilir). Yavaşsa diyalogsuz planda kurguda 1,05–1,15× uygulanır;
    değilse BAYRAK (tahmin).
  - EK2-5'teki canlı bekleme.
  - Sahne düzeyinde `canli_arka_plan` istemi (duman, kar, alev, uzak siluet): durum değiştirmez, defteri etkilemez.

### EO5 — Ana kanca olan yaratık en zayıf denetimde **[ORTA]**
- **Gözlem:** İnsan olmayan karakterde yüz modeli çalışmaz; kimlik DINOv2 + görüntü-dil modeliyle denetlenir ve sonuç çoğunlukla BAYRAK'tır
  (AR2 §1.1; [GS2] §4.8.5). Büyüme evreleri "boy benzetmesi"yle yazılır ([SN2] §4.5.2).
- **Etki:** İnsan + yaratık bağı kancanın kendisidir (BK §2.1). Yaratığın renk deseni, boynuzu ya da göz rengi plan plan oynarsa seyirci bunu insan
  yüzündeki değişimden daha kolay fark edebilir (tahmin). Bağın duygusu da yaratığın "oyunculuğu"ndadır.
- **Öneri:**
  - **Yaratık kimlik kartı:** ≥ 3 sabit asimetrik işaret (ör. sol kaşta beyaz leke, sağ boynuzun kırık ucu) + Lab renk paleti + baş/gövde oranı.
    Kör sorular bu işaretleri görüntü koordinatında sorar; DINOv2 eşiği yaratık başına kalibre edilir.
  - **Yaratık davranış sözlüğü** `oyunculuk` alanına (EK2): merak = baş eğme + kulaklar ileri; korku = sinme + kuyruk kıvırma; sevgi = burun
    sürtme. Filtre kelimeleri ("baby", "little") yine yasaktır (DR).
  - Evre geçişi ekranda bir olaydır (zaman atlaması kartı); planlar arasında boy kendiliğinden değişmez.

### EO6 — 720p kaynak, "4K" vaadi ve plastik görünüm **[ORTA]**
- **Gözlem:** Video 720p Omni (BK §8 #1), dışa aktarma 4K 24 fps (BK §8 #8); büyütme yöntemi tanımlı değil ([KU2] açık soru 10). Başlık kalıbı
  "Full Movie 4K 2026" (BK §1.6).
- **Etki:** Uzun filmler TV ekranında da izlenir (genel bilgi; oranı kaynakta yok). 720p'den basit büyütme yumuşak ve sıkıştırma izli görünür;
  başlıktaki "4K" vaadini görüntü karşılamaz. YZ'nin pürüzsüz "plastik" teni, ortak bir film görünümü yoksa planlar arasında da fark eder.
- **Öneri:**
  - **Büyütme kalite kapısı:** yapay zekâ tabanlı bir büyütücü (ör. Real-ESRGAN türü; lisansı ve 4 GB'taki süresi doğrulanmalı). Büyütmeden sonra
    yüz bölgesinde SFace kimlik ölçüsü yeniden koşar: büyütücü yüzü değiştirmemelidir.
  - **Ortak film görünümü:** sabit renk LUT'u + ince gren + hafif halation (`renk_cila.py`; evrende `dunya.json`). Grenin planlar arasındaki ufak
    farkları örtmesi beklenir (tahmin).
  - Vitrin planları (EO1) resmî API'de 1080p üretilir (fiyat doğrulanmadı; [UM2] `veo_vertex`).
  - Görüntü 4K hissi vermiyorsa başlıkta "4K" yazılmaz (seyirci güveni). Karar yayın stratejistinindir.

### EO7 — Seyirci ajanı tek tip; kapatma anı simüle edilmiyor **[ORTA]**
- **Gözlem:** Tek bir "sıradan YouTube seyircisi" profili; 1–10 puan; ilk 2 dk testi 3 seyircinin "evet/hayır"ı (RE `ilk2dk_devam_evet_min` = 3;
  [SN2] H12).
- **Etki:** Claude sabırlı ve dikkatli okur; gerçek izleyici telefonda ya da TV'de, yarı dikkatle izler. 3/3 "evet" kolay çıkar ve bir olasılık değildir.
- **Öneri:**
  - 3 persona: (1) fantastik ve savaş filmi seven, akşam TV'de izleyen 25–55 yaş izleyici (BK §1.1 hedef kitlesi); (2) telefondan yarım dikkatle
    izleyen ve ilk 30 sn'de karar veren izleyici; (3) seri meraklısı (yalnız seri devamında; [SN2] İ2'deki "dönen seyirci").
  - Her seyirci `kapatma_ani` ve "devam olasılığı %" verir. Betik bunlardan **tahmini bir tutma eğrisi** çıkarır ve EK3'teki gerçek eğriyle kalibre
    eder. Bu bir ölçüdür, kapı değildir.

### EO8 — Kapı yığılması: hiç bitmeme ya da şişkin puanla geçme riski **[ORTA]**
- **Gözlem:** Dört ardışık 8/10 kapısı (kâğıt, plan, animatik, kurgu; [SN2] S1, [YN2] Ö14, [KU2] B1/B3) ve ilk 2 dk'da 3/3. Geçmişte kâğıt puanları
  6/8/7, kurgu puanı 5 → 7 oldu (OB; BK §3.9). Kullanıcı 7'yi "süper" buldu (BK §3.9).
- **Etki:** Ya film kapılarda takılır ve merdiven DUR'a varır ([SN2] §2.6), ya da yazarlar seyircinin hoşuna gideni "öğrenir" ve puan şişer
  ([SN2] R1).
- **Öneri:**
  - İlk filmde 8, kâğıt ve plan kapılarında **hedef**tir. HATA yalnız KRİTİK > 0 ya da medyan < 7 olduğunda verilir (tahmin; 7, kullanıcının
    "süper" dediği düzeydir, BK §3.9).
  - B2/B3 metinleri ve raporlarıyla çapalama yapılır ([SN2] Q6): yeni seyirci aynı metne kaç puan veriyor?
  - Aşama başına takvim kutusu konur ([UM2] takvimi; ör. kâğıt ≤ 3 gün). Aşılırsa yapımcının doktor teşhisi zorunlu olur.
  - Eşikler EK3 verisiyle güncellenir.

### EO9 — Ritim, hareket ve ses enerjisiyle ölçülmüyor **[ORTA]**
- **Gözlem:** Ritim ölçüleri plan süresi, ASL, plan tipi tekrarı ve duygu eğrisidir (ZN §2.5, §1.3). Seyirci ritim puanını okuyarak verir. Animatik
  durağan karelerden oluşur; kurgucu bunun ritmi yavaş hissettireceğini kendisi yazıyor ([KU2] R13).
- **Etki:** ASL kuralları tutarken film yine tekdüze hissettirebilir: her plan "dur → 2–3 küçük hareket → dur" kalıbında, aynı enerji düzeyinde
  akar (tahmin).
- **Öneri:** Kurgu çizelgesinde (T2) bir **enerji eğrisi** çıkarılır: saniye başına görüntü hareket enerjisi (kare farkı ya da optik akış) + kısa
  süreli ses yüksekliği + kesme yoğunluğu, dakika başına toplanır ve duygu haritasıyla aynı grafikte çizilir ([KU2] `EGRI_T2.png` genişletmesi).
  - Kural: ±%10 bandında düz kalan enerji 180 sn'yi aşarsa BAYRAK (180 sn: RE `duz_cizgi_max_sn` ile aynı süre; bant tahmin). Tepeden önce enerji
    çukuru aranır (ZN §1.3 kural 3'ün enerji karşılığı).
  - Animatikte (T1) hareket olmadığı için orada yalnız ses enerjisi ölçülür.

### EO10 — Yapımcı ekonomisi ve kullanıcı yükü **[ORTA]**
- **Gözlem:** 40 dk'lık film ≈ 6.318 kredi, ≈ 12,9 saat Flow, ≈ 6 görsel düzeltme günü, ≈ 350–550 Opus çağrısı ve ≈ 2–3 hafta ister
  ([UM2] §4.1.3). Kullanıcının fiziksel işi ≈ 18–24 Gemini paketi ve `elle` modda ≈ 527 kez GÖNDER'dir ([UM2] M2). Önceki iş "emeğe göre izlenme
  düşük" diye kapandı (OB). YPP eşiği 01.02.2027'de 8.000 saate çıkıyor (BK §1.1.4).
- **Etki:** İlk film ≈ 3 haftalık bir yatırımdır ve geri bildirim ancak sonunda gelir. Yorulan kullanıcı "zorla bugün bitirek" gibi günlük kararlar
  verebilir (BK §6.2 #9); bu kararlar kaliteyi deler.
- **Öneri:**
  - **Aşamalı yatırım:** EK3 teşhisi → kâğıt → animatik → **dikey kesit** (EK1) → bilgi paketi + işitsel-görsel izleyici → kalan üretim.
  - `URETIM_ONIZLEME`'ye kullanıcının saat bütçesi eklenir (paket sayısı, GÖNDER sayısı, tahmini saat). Ücretli hızlandırıcıların (ör. `vertex_gorsel`
    ≈ 31 $; [UM2] İ-2) kaliteye değil yalnız süreye etkisi olduğu dürüstçe yazılır.
  - Gerçekçi yayın temposu "2–3 haftada 1 film" + aradaki fragman ve Short'lardır. Bu, kazananların "haftada 0,3–1 film" temposunun içindedir (KR);
    daha hızlısı zaten önerilmiyor (BK §1.3).
  - İzlenme hedefi kanal düzeyinde konuşulur. Örnek hesap: ortalama izleme oranı %25 olursa (tahmin) 40 dk'lık filmde izleme başına 10 dk eder;
    4.000 saat ≈ 24.000 izlenme ister (hesap). Bu sayı ilk film için gerçekçi hedefin ne olduğunu gösterir.

---

## 5. KÜÇÜK maddeler

| # | Madde | Öneri |
|---|---|---|
| EÇ1 | **Seri boyunca formül yorgunluğu:** her film aynı vuruş dakikalarıyla (ZN §1.2) ve aynı kapsama kalıplarıyla kurulursa dönen seyirci kalıbı sezer | ±%4'lük oran toleransını bilinçli kullanan yapı varyasyonu (sondan başlayan soğuk açılış, paralel kurgu) bonus mimar ekseninde; dönen seyirciye "tahmin edilebilirlik" sorusu |
| EÇ2 | **İlk 30 sn'de kapak yankısı yok:** vaat imgesinin sınırı 120 sn (RE `vaat_imgesi_max_sn`) | Kapaktaki yaratık ya da ilişkinin bir kesiti ilk 30 sn içinde (tahmin; ölçülmüş tutma verisi yok, BK §1.8.5); EK3 verisiyle doğrulanır |
| EÇ3 | **Görsel dil tekdüzeliği:** kalıplar (klasik giriş, yükselen diyalog; ZN §3.2) doğru ama her sahnede aynı | Parti başına ≥ 2 "imza plan" (bakış açısı planı, kuş bakışı, siluet, yansıma, dorukta uzun tutma; düşük güvenli kamera hareketleri hariç) (tahmin); plan eleştirmeninin listesine |
| EÇ4 | **Mizahın aracı yok:** duygu sözlüğünde `mizah` var (ZN §1.1; eğride 11. ve 15. dk) ama zamanlama, tepki ve yaratık şirinliği araçları tanımlı değil (kullanıcının imzası BK §2.5) | Her partide ≥ 1 nefes ya da mizah anı; küçük güzel sahneyle (BK §2.10) birleşebilir; diyalog editörüne espri zamanlaması |
| EÇ5 | **Yakın planda nefes ve kumaş sesi yok:** mikro adımlar efekt zorunluluğu taşımıyor ([SM2] §4.8.1-1) | Y/CY planlarda nefes, yutkunma ve kumaş katmanı; seviye diyalogdan 18–24 dB aşağı (tahmin) |
| EÇ6 | **Short'lar ≈ 0 izlendi** (OB) | Short'lar dikey kadraja uygun anlardan (yüz ya da yaratık merkezli) seçilir; fragman dikey kesitten çıkar; Short'tan filme bağlantı verilir (YouTube'un "ilgili video" bağlantısı; bellekten, doğrulanmalı) |
| EÇ7 | **İkinci dil ses izi [H]:** tablodaki en güçlü kanal (Relatos de Eterya, 7/7 ≥ 1M; BK §1.2) adından İspanyolca görünüyor (doğrulanmadı) ve "aynı format İspanyolcada talepli olabilir" notu var (BK §1.9.5) | Sesler evrende sabit olduğu için ilk iki filmden sonra ikinci dilde ses izi denenebilir (YouTube'un çok dilli ses özelliği; koşulları doğrulanmalı) |
| EÇ8 | **Tekrar eden figüranların kartı yok** (nöbetçi, köylü) | ≥ 2 sahnede görünen figüran için mini kart ve evren kaydı (tahmin) |
| EÇ9 | **Karakter tasarımının çekiciliği ölçülmüyor:** kart kapısı tutarlılığı ve ayrışmayı ölçüyor ([GS2] B10–B11); "akılda kalıcı mı, kapakta çeker mi?" sorusu yok | Kart adaylarına kapak boyutunda kör seyirci ikili karşılaştırması; seçilen kartlar kullanıcıya bilgi olarak gider ([CM2] S-5 ile aynı yönde) |

---

## 6. Beş alanda eksikler (görev tanımının istediği özet)

| Alan | Eksik | Madde |
|---|---|---|
| **Duygu** | Duygu durumu plandan plana taşınmıyor (gözyaşı izi, nefes nefese); duygu yalnız kâğıtta ve durağan karede puanlanıyor; duygunun yarısını taşıyan müziğin kalitesi duyulmuyor | EK2-2, EK1, EK4 |
| **Oyunculuk (yüz ifadesi, mikro mimik istemleri)** | `ifade` isteğe bağlı; görünür duygu sözlüğü yok; mikro fiil sözlüğü dar; aday ve çekim seçimi ifadeye bakmıyor; tek çekim; canlı bekleme yok; yaratık davranış sözlüğü yok | EK2, EO4, EO5 |
| **Diyalog doğallığı** | Sırayla okunan replik hissi; konuşurken eylem yok; söz kesme ve yarım cümle yok; metrikler açıklamaya itiyor; `teslim` dar; sözsüz ses vuruşu yok; ana dil kulağı tanımlı değil | EO3, EO2, EK2-6, EK2-7, EK1 |
| **Müzik** | Kaynak kalitesi (2B INT8 + GM örnekli yedek); kalite kapısı yok; yaratık ses kiti duyulmadan seçiliyor; ses–yüz uyumu ölçülmüyor | EK4 |
| **Ritim** | Ritim süreyle ölçülüyor, hareket ve ses enerjisiyle değil; animatik durağan; "dur–hareket–dur" mikro ritmi; seri boyunca formül | EO9, EO4, EK1, EÇ1 |

---

## 7. YZ kusurları: seyircinin gözüyle önlem tablosu

| Seyircinin fark ettiği kusur | Tasarımdaki önlem (kaynak) | Yeterli mi? | Ek öneri |
|---|---|---|---|
| Yüz değişmesi | 2 aday + G1 (SFace, kör gözlem), V2, kimlik demiri, kartlar, evren ([GS2]; [YN2] Y44) | **Büyük ölçüde evet** (sistemin en güçlü yanı). Kalan: profil ve karanlıkta eşik kalibrasyonu ([GS2] R1), tekrar eden figüranlar, yaratık | EO5, EÇ8 |
| Nesne zıplaması | atomik zincir, dünya defteri, V3, durum dondurma ([YN2], [GS2]) | **Evet** (hikâye nesneleri için). Kalan: defterde olmayan dekor nesneleri; bunları plaka ve ana kare ağacı kısmen korur ([YN2] Y8) | — |
| Dudak kayması | `veo_donustur`, senkron kuralı, S3 ([SM2], [KU2]) | **Evet** | — |
| Ölü sessizlik, ses zıplaması | sahne başına tek yatak, mutlak sessizlik ≤ 2, LUFS ([SM2]) | **Evet.** Kalan: ince efekt kütüphanesi → tekrar eden yataklar ([SM2] R9); yakın planda nefes yok | EÇ5 |
| Tekdüze ritim | ASL, plan tipi tekrarı, duygu eğrisi (ZN §2.5) | **Kısmen:** süre ölçülüyor, enerji ölçülmüyor | EO9 |
| Robotik replik | Veo performansı + dönüşüm, diyalog editörü ([SM2], [SN2]) | **Kısmen:** dar teslim, fısıltı ve bağırmada metalik dönüşüm riski, dinleyen yok | EK2, EK4, EO3 |
| (ek) Donuk yüz, duygu zıplaması | yok | **Hayır** | EK2 |
| (ek) Süzülen ya da donup kalan hareket, kıpırtısız figüran | Y06 ve "holds still" (tersine işliyor), V1 donma | **Hayır** | EO4 |
| (ek) "Maket" müzik | aday başına 3 üretim + teknik ölçü ([SM2] SB5) | **Hayır** | EK4 |
| (ek) Yüze uymayan ses | profil süzgeci ([SM2] SA1) | **Kısmen** | EK4-3 |
| (ek) Plastik ten, 720p yumuşaklığı | `renk_cila.py` | **Kısmen** | EO6 |
| (ek) Yaratığın deseni ve boyu oynuyor | DINOv2 + görüntü-dil modeli ([GS2]) | **Kısmen** | EO5 |

---

## 8. Yetmeyen tasarım kararları (karar → neden yetmiyor → madde)

| Karar (kaynak) | Ne için konmuş | Neden yetmiyor | Madde |
|---|---|---|---|
| Habersiz seyirci = Claude, kare + metin ([KU2] §4.5.4) | kopukluk, anlaşılırlık | hareket, ses, oyunculuk ve müzik görünmüyor | EK1, EO7 |
| G1 seçim sırası teknik ([GS2] GS8) | kimlik, süreklilik | ifade ve kompozisyon seçilmiyor | EK2-3 |
| `ifade` isteğe bağlı; `teslim` 5 değer ([YN2] §4.5.7; [SM2] §4.5.2) | — | duygu tasarlanmıyor | EK2 |
| Bir plan = bir çekim ([UM2] A14) | kredi | performans seçimi yok | EK2-4 |
| Y06 tek özne + uzun "holds still" ([YN2]) | zıplama, dudak | kıpırtısız figüran, dur–kalk ritmi | EK2-5, EO4 |
| Konuşurken el işi yok, üst üste konuşma yok, replik ortasında duygu yok ([SN2] H8, §4.8.4) | dudak bozulması | masa başı okuma hissi | EO3 |
| Ses ve müzik seçimi yalnız ölçüyle ([SM2] SB2, SB5) | otomasyon, ölçülebilirlik | kalite ve uyum duyulmuyor | EK4 |
| `midi_ornek` yedeği ([SM2] §4.8.4) | lisans güvenliği | "maket" tını yayına girebilir | EK4-2 |
| Ders defteri yalnız iç kaynaklı ([UM2] §4.5.11) | tekrar eden hatayı önlemek | gerçek seyirciden öğrenmiyor | EK3 |
| Kapak = filmdeki kare; seçim jüri kipinde ([SN2] §4.2.1; [CM2] A17) | yanıltıcı kapağı önlemek | tıklama için tasarım ve test yok | EK5 |
| 720p → 4K, yöntem tanımsız (BK §8; [KU2] açık soru 10) | kalite kararı | yumuşak görüntü, "4K" vaadi | EO6 |
| Kalabalık ve hızlı aksiyon zayıf → elenir ([SN2] H1-4) | üretilebilirlik | gösteri açığı | EO1 |
| Dört ardışık 8/10 kapısı, kalibrasyonsuz ([SN2] S1; [KU2] B1, B3) | kalite | takılma ya da şişme | EO8 |

---

## 9. Önerilen alanlar ve eşikler (tümü başlangıç değeridir)

- **Plan düzeyi `zanaat.oyunculuk`** (EK2-1): yukarıdaki JSON.
- **Durum nesnesine** (EK2-2): `karakterler.<id>.duygu {durum, siddet, izler[]}`.
- **Seyirci raporuna** (EK1, EO7): `yz_kusurlari[]`, `kapatma_ani`, `devam_olasiligi`.
- **Film düzeyine** (EO1): `seyirlik_anlar[] {id, sahne, tur, sure_hedef_sn, kapak_adayi}`.

| Önerilen anahtar | Değer | Sonuç | Etiket |
|---|---|---|---|
| `ifade_zorunlu_insanli_plan` | evet ("nötr" gerekçeli) | H | bu belge |
| `ifade_uyum_min_oran` (G1'de seçilen karelerde kör ifade okuması = hedef ifade) | ≥ %85 | B | tahmin |
| `duygu_sicramasi_gerekcesiz` | 0 | B | tahmin |
| `take_kapsami_plan` | 60–110 | — | tahmin |
| `canli_bekleme_pilot_ab` | zıplama oranı farkı ≤ 2 yüzde puanı ise varsayılan olur | — | tahmin |
| `teslim_sozluk_boyutu` | ≈ 12 | — | tahmin |
| `seyirlik_an_parti_min` | 2 | B | tahmin |
| `gosterisiz_aralik_max_sn` | 360 | B | tahmin |
| `vitrin_plan_max_sn` | 7 | — | tahmin |
| `gorsel_tasima_orani_min` | 0,5 | B | tahmin |
| `enerji_duz_max_sn` | 180 (±%10 bant) | B | süre RE `duz_cizgi_max_sn` ile aynı; bant tahmin |
| `izleyici_ilk_film` | BAYRAK (kapı değil) | — | bu belge |
| `muzik_kalite_ikili_min` (çapaya karşı kazanma oranı) | ≥ 0,5 | B | tahmin |
| `ses_dogallik_mos_min` | model seçilince | B | doğrulanmalı |
| `kapak_aday_min` | 8 | — | tahmin |
| `kapak_kucuk_okunurluk` | 168×94'te yüz ve yaratık seçilebiliyor | H | tahmin |
| `ilk_film_seyirci_hata_esigi` | KRİTİK > 0 ya da medyan < 7 | H | tahmin; BK §3.9 |

---

## 10. Sahip ve öncelik

**P0** = ilk filmden önce · **P1** = ilk film sırasında · **P2** = ilk yayından sonra.

| Öneri | Sahip | Öncelik | Kesin karar notu |
|---|---|---|---|
| EK3-1 B1/B2 kanal teşhisi | yayın stratejisti + üretim | **P0** | 1: kurulum işi, soru değil |
| EK5-1 `yayin-stratejisti` ajanı | mimari + yayın | P0 | 1 |
| EK2-1/2/3 oyunculuk alanları, duygu defteri, kör ifade sorusu | yönetmen, senarist, görüntü | P0 | 2 |
| EK1-2 dikey kesit (pilot tanımına) | üretim + kurgucu | P0 tasarım, P1 uygulama | 3a: animatikten sonra |
| EK4-2 müzik kaynak merdiveni (lisanslı yedek) | ses | P0 | 6 |
| EO1 seyirlik an defteri | senarist + yönetmen | P0 (kâğıt) | — |
| EO3 diyalog araçları | senarist + kurgucu | P0 (kâğıt) | — |
| EO5 yaratık kartı ve davranış sözlüğü | görüntü + yönetmen | P0 | 3c |
| EO8 ilk film eşik politikası | senarist + kurgucu | P0 | 6 |
| EK1-1 `izleyici` sağlayıcısı | üretim + kurgucu + mimari | P1 | 6 ($) |
| EK1-4 izle-dinle bilgi paketi | kurgucu + ses | P1 | 1: bilgi |
| EK2-4 çoklu çekim politikası | üretim + yönetmen | P1 | 5: aynı tempo |
| EK2-5/6/7 canlı bekleme, teslim sözlüğü, sözsüz ses | yönetmen + ses + senarist | P1 (pilotta A/B) | 2 |
| EK4-1/3/4 müzik kalite kapısı, ses–yüz uyumu, doğallık ölçüsü | ses | P1 | 1, 6 |
| EO2 aşırı açıklama ölçüleri | senarist | P1 | — |
| EO4 hareket hızı ölçüsü | görüntü + kurgucu | P1 | — |
| EO6 büyütme + film görünümü | kurgucu + görüntü | P1 | 6 |
| EO7 personalar + kapatma anı | senarist + kurgucu | P1 | — |
| EO9 enerji eğrisi | kurgucu | P1 | — |
| EO10 kullanıcı saat bütçesi | üretim | P1 | 1 |
| EK3-2/3/4 `yayin_analiz.py`, kalibrasyon, erken uyarı | üretim + yayın | P1 (ilk yayın) / P2 | 3e |
| EK5-2/3/4 kapak hattı, yayın sonrası test, fragman | yayın + görüntü | P1 / P2 | — |
| EÇ1–EÇ9 | ilgili uzmanlar | P2 (EÇ9: P1) | — |

---

## 11. Açık sorular (cevabı bilinmiyor; uydurulmadı)
1. B1 ve B2'nin gösterim sayısı, TO'su, ortalama izleme süresi ve tutma eğrisi neydi? (EK3; kararların sırasını belirler.)
2. İşitsel-görsel izleyici için hangi model? Video + ses girdisi, saniye başına kare örneklemesi, fiyat ve anahtar kurulumu nasıl? (EK1)
3. Veo/Omni, `dis_ifade` sözlüğündeki ifadelere ve `teslim` fiillerine ne kadar uyuyor? Hangi ifade kelimeleri filtreye takılıyor? (EK2; pilot)
4. "Canlı bekleme" zıplama ve dudak hatasını artırıyor mu? (EK2-5; pilotta A/B)
5. Lisanslı müzik kaynaklarının (YouTube Ses Kitaplığı, ElevenLabs Music vb.) para kazanan bir kanaldaki koşulları neler? (EK4)
6. Konuşma doğallığı tahmincisi (MOS) ve yapay zekâ büyütücüsü için ticari kullanıma uygun lisanslı ve 4 GB'ta çalışan seçenek hangisi? (EK4, EO6)
7. YouTube kapak testi kanalda açık mı, başlık testi var mı? Analytics API tutma eğrisini, gösterimi ve TO'yu veriyor mu? (EK5, EK3)
8. Kazanan YZ sinema filmlerinde diyalog planlarıyla gösteri planlarının oranı nedir? (EO1; bugün veri yok)

---

## 12. En kritik 5 madde (özet)
1. **EK1 — Film yayından önce hiç izlenmiyor ve dinlenmiyor.** Bütün seyirciler Claude; kare ve metin okuyor, ses duymuyor. Öneri: video + ses
   izleyen çapraz model seyirci (ilk filmde BAYRAK), filmin ilk ≈ 3 dakikasının yayın kalitesinde "dikey kesit" olarak bitirilmesi (ek kredi yok),
   kare paketinin göremediğini ölçen betikler, kullanıcıya soru değil bilgi olarak izle-dinle paketi.
2. **EK2 — Oyunculuk tasarlanmıyor.** İfade isteğe bağlı, teslim 5 değer, aday seçimi ifadeye bakmıyor, duygu planlar arasında taşınmıyor, her plan
   tek çekim. Öneri: `oyunculuk` alanları ve filtre-güvenli ifade sözlüğü, defterde duygu sürekliliği, kör ifade okuması ve seçim ölçütü, duygu yüklü
   60–110 planda 2 çekim (≈ 720–1.320 kredi, hesap), canlı bekleme, genişletilmiş teslim sözlüğü ve sözsüz ses vuruşları.
3. **EK3 — Gerçek seyirciyle bağ yok.** Ders defteri yalnız Claude'un beğenisinden öğreniyor; B1'in ≈ 671 izlenmesinin nedeni bilinmiyor. Öneri:
   önce B1/B2 kanal teşhisi, `yayin_analiz.py` ile tutma eğrisinin plan kimliklerine eşlenmesi, seyirci puanlarının gerçek veriyle kalibrasyonu.
4. **EK4 — Müzik ve sesler kulaksız seçiliyor; müzik "maket" riski taşıyor.** Öneri: işitsel modelle müzik kalite kapısı, lisanslı kütüphane ya da
   ticari koşulları okunmuş üretici yedeği (GM örnekleriyle çalınan tema yayına girmez), ses–yüz ve yaratık sesi için kör uyum sorusu, konuşma
   doğallığı ölçüsü.
5. **EK5 — Paketleme sahipsiz.** Kapak ve başlık için uzman, aday bolluğu ve test yok. Öneri: `yayin-stratejisti` ajanı, kapak için ayrıca kurulmuş
   8–12 aday ve küçük boyutta okunurluk denetimi, ilk 2 dk testinde gerçek kapak görseli, yayın sonrası kapak testi, dikey kesitten fragman.

---
*Bu belge seyirci-yapımcı eleştirisidir. Sayıların kaynağı yanında yazılıdır; (tahmin) ve (bellekten; doğrulanmalı) işaretli olanlar ilk filmde
ölçülerek ya da kurulumda doğrulanarak ayarlanmalıdır.*
