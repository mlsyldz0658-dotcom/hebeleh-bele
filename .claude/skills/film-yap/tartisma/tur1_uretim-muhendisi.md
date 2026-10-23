# Tur 1 — Üretim Mühendisi (hattın mühendisliği)

Hazırlayan: üretim-mühendisi uzmanı (Claude). Tarih: 23.10.2026.
Okunanlar: `BILGI_KURALLARI.md`, `ZANAAT.md`, `ritim_esikleri.json`, `arastirma/01–03`, `FILMLE ILGILI CLAUDE/00–07` ve
`HAFIZA_YEDEGI` içindeki ilgili notlar, `YZ_FILM/BILGI/CLAUDE_ICIN.md`, `KARARLAR.md`, `YAPIM_REHBERI.md`, `FLOW_KESIF.md`,
`YZ_FILM/ARACLAR/` altındaki bütün mevcut kod ve `.claude/agents/*.md`. Diğer uzmanların tur-1 dosyaları okunmadı.

Etiketler: **[kaynak: X]** belgeden alınan bilgi · **[hesap]** benim yaptığım aritmetik (girdileri yazılı) ·
**[tahmin]** kaynağı olmayan başlangıç değeri, kalibre edilecek · **[doğrulanmadı]** denenmeden yazılan bilgi.

Mevcut durumun ölçümü (23.10, bu oturum): `python -m unittest discover -s ARACLAR/testler` → **6 test, hepsi geçti, 14 sn**
(Python 3.13, Linux). Bulut ortamında Python 3.10 yok. Kullanıcının bilgisayarında Python 3.10 var.

---

## 1. Alanımın hedefi ve başarı ölçütü (sayılarla)

### 1.1 Hedef
Konu cümlesinden YouTube paketine kadar giden hattı **tek bir durum makinesi** olarak kurmak. Bu makinenin özellikleri:
1. Her aşamanın girdisi, çıktısı ve geçme şartı kodda tanımlı. Belgeler bu tanımdan üretilir, elle yazılmaz.
2. Kâğıt kapıları önce çalışır. Kredi harcayan iş, kapıların **aynı girdi imzasıyla** geçtiği kanıtlanmadan başlayamaz.
3. Kesilen iş (elektrik, Ctrl+C, bağlam sıkıştırması, Flow uyarısı) kaldığı yerden sürer. Yapılan iş tekrarlanmaz, kredi iki kez harcanmaz.
4. Sağlayıcı kısıtlanınca hat **durur**. Hiçbir zaman kısıtı atlatmaya çalışmaz. Yedek sağlayıcıya geçiş yalnız izinliyse, eşit ya da daha iyi kaliteyle ve sahne grubu sınırında olur.
5. Ana Claude ile betikler arasında net bir iş bölümü vardır. Yargı gerektiren işi ajan yapar. Ölçülebilen her işi betik yapar. Sırayı `film.py` söyler.
6. Her hata, red, yeniden çekim ve kullanıcı notu otomatik olarak ders defterine yazılır. Defter bir sonraki çalıştırmada doğrulayıcıları sıkılaştırır.

### 1.2 Başarı ölçütleri
| # | Ölçüt | Hedef | Nasıl ölçülür |
|---|---|---|---|
| M1 | Kullanıcıya sorulan karar sorusu | **1** (konu) | Kod içinde `input()` yalnız `yeni --konu` yolunda olur. Diğer aşamalarda input() çağrısı testle yasaklanır |
| M2 | Kullanıcının zorunlu el işi | Yalnız kaçınılmaz 4 tür: Flow girişi ya da reCAPTCHA, (seçilirse) Gemini paket taşıma, video `.bat`'ını başlatma, YouTube yükleme onayı | `kim: kullanici` olan aşama listesi kodda sabittir. Test bu listenin dışına çıkılmadığını denetler |
| M3 | Kapısız kredi harcaması | **0** | Kredili aşamanın girdi imzası kapı raporlarının imzalarını içerir. Uyuşmazsa sağlayıcı çağrılmaz (test) |
| M4 | Çift harcama (aynı işin iki kez gönderilmesi) | **0** (planlı yeniden çekimler hariç) | `KREDI_DEFTERI.jsonl` içinde aynı `is_kimligi` için ikinci `gonderildi` kaydı olmaz |
| M5 | Kesintiden sonra devam | Her aşamanın ortasında kesilen sahte çalışmada **%100** doğru devam | Kesme testleri (§6.4) |
| M6 | Kredi tahmini doğruluğu | İlk filmde gerçek/tahmin ∈ **[0,90; 1,15]**, sonra ders defteriyle **[0,95; 1,10]** [tahmin] | `S03` film sonu raporu |
| M7 | Yeniden çekim oranı | B2'de ≈ **%37** idi [hesap: "50+ yeniden çekim" ÷ 134 planlı video, kaynak: 04_KIM_NE_YAPTI, H/proje-b2]. Hedef ≤ **%20** [kaynak: ritim_esikleri `kredi_yeniden_deneme_payi`] | `KREDI_DEFTERI` |
| M8 | Flow uyarısından sonra yeni gönderim | **0**. Uyarı göründükten sonra en geç bir kontrol döngüsünde (≤ 10 sn) durulur | HTML fikstürüyle Memmet testi (§6.4) |
| M9 | Uçtan uca sahte test | `ORNEK_3_SAHNE` için ≤ 5 dk, tüm takım ≤ 10 dk, **Python 3.10 Windows'ta yeşil** | CI (§6.4) |
| M10 | Ders defterine otomatik kayıt | Kapı HATA'sı, sağlayıcı reddi ya da kısıtı, yeniden çekim, kullanıcı notu ve seyirci KRİTİK bulgusu için **%100** | Test: her olay türü bir kayıt üretir |
| M11 | Bulutta kredili sağlayıcı çağrısı | **0** | Ortam algılama + test |
| M12 | Her klibin künyesi | **%100** (istem özeti, sağlayıcı, model, deneme, kapı sonuçları) | `KUNYE/NNN.json` sayısı = video sayısı |
| M13 | Gizli bilgi sızıntısı (log, Telegram, commit) | **0** | Anahtar deseni taraması testte ve `paketle.py`'de |

### 1.3 Ölçek ve süre beklentisi (40 dk film)
- ≈ 495 plan, ≈ 405 klip [kaynak: ZANAAT §2.6].
- Flow kredisi: 405 × 12 = 4.860 taban. %20 payla 5.832, %30 payla **6.318** [hesap]. Ultra hesap 10.000 kredi + günde 50 bedava kredi verir [kaynak: H/ucuz-erisim].
- Flow gece temposunda video süresi ≈ **13 saat**, yani 2 gece [hesap, tahmin]. Hesabın girdileri:
  - 527 gönderim (405 × 1,3).
  - Gönderim arası ortalama 21 sn; 8 gönderimde bir ortalama 4,5 dk ara mola. Gönderim başına ≈ 55 sn düşer → ≈ 8,0 saat.
  - 20'lik bloklarda 2 blokta bir ortalama 22,5 dk mola → 13 mola ≈ 4,9 saat.
  - Tempo değerleri: H/olagandisi-dur 17.10. Video üretim süresi ~40 sn: FLOW_KESIF, 360p deneme hesabı. 720p'de daha uzun olabilir [doğrulanmadı].
- Bu süre yarı otomatik modda kullanıcının ≈ 8+ saat başında oturması demektir. Bu, "yalnız konu sorulur" kararıyla gerilim yaratıyor (§9 R2, Q9).

---

## 2. Aşama aşama süreç: her adım için girdi → iş → çıktı dosyası → geçme şartı → kim yapar (ajan/betik/ana Claude)

### 2.0 Mimari: kim neyi yürütür

```
Kullanıcı ──(konu)──► ana Claude (film-yap becerisi) ──► film.py <film> --sonraki --json
                          ▲                                   │
                          │      ┌────────────────────────────┴───────────────────────┐
                          │      │ kim: betik     → film.py --calis (bir sonraki ajan/insan işine kadar) │
                          │      │ kim: ajan      → Agent(ad, girdiler, çıktı) → film.py --dogrula <aşama> │
                          │      │ kim: kullanici → tek cümlelik Türkçe iş + Telegram; tur biter          │
                          │      │ kim: ortam     → bulutta: kâğıdı commit et, "bilgisayarında DEVAM.bat" │
                          │      │ kim: butce     → sayıları raporla; dur                                 │
                          └──────┴──────────────────────────────────────────────────────────┘
```
- **`film.py` = durum makinesi + deterministik kapılar.** Claude API'yi varsayılan olarak çağırmaz. Ajan gereken aşamada bir **iş tanımı** yazar ve çıkış kodu **3** ile çıkar.
- **Ana Claude = yapım yöneticisi.** İş tanımını okur, ajanı başlatır, çıktıyı `--dogrula` ile kapıya sokar. Kendisi puan vermez. Bu, YAPIM_REHBERİ §1'deki "tarafsız yönetmen" kuralıdır.
- **Başsız mod** (`--llm claude_api`, isteğe bağlı): aynı iş tanımlarını Claude API ile (`claude-opus-5-5`) `film.py` kendisi yürütür. Bu mod Claude Code açık olmadan gece çalışmak için var. Ajan istemleri iki yolda da **aynı şablon dosyasından** gelir.

**Çıkış kodları** (`.bat` ve beceri bunlara göre konuşur):

| Kod | Ad | Anlamı |
|---|---|---|
| 0 | BİTTİ | İstenen aşamalar tamam |
| 1 | HATA | Program hatası (iz `FILM_KAYIT.txt`'de) |
| 2 | KULLANICI | İnsanın yapması gereken bir iş var (giriş, paket taşıma, `.bat`) |
| 3 | AJAN | Claude'un yapacağı bir ajan işi var |
| 4 | ORTAM | Bu iş bu ortamda yapılamaz (bulutta Flow gibi) |
| 5 | BÜTÇE | Bütçe kapısı geçmedi |
| 6 | KAPI | Kapı geçmedi ve tur sınırı doldu |
| 7 | KISIT | Sağlayıcı kısıtlandı ve izinli yedek yok. **ACİL** |

**Kaldığı yerden devam: durum dosyadan türetilir.** Bunun için `FILM_DURUM.json` yalnız önbellektir. Asıl kanıt çıktıların kendisidir:
- Her aşama çıktısını bir **zarf** ile yazar: JSON'da `_uretim` alanı, Markdown'da yanında `<dosya>.imza.json`. Zarfın içinde `{asama, girdi_imza, arac_surum, esik_surum, sonuc, zaman}` bulunur.
- Bir aşama "tamam" sayılırsa üç koşul birden sağlanır: çıktı var, zarftaki `girdi_imza` şimdiki girdilerin imzasına eşit, kapı `GEC`.
- Bu sayede bulutta ve yerelde aynı klasörde `--durum` aynı sonucu verir. `FILM_DURUM.json` çakışma kaynağı olmaz (git'e girmez).
- Kredili çıktılar (video, ücretli ses) girdi değişince **asla kendiliğinden geçersiz sayılmaz** ve asla silinmez. Plan bazında `bayat` diye işaretlenir ve `KUYRUK/YENIDEN_URET.json`'a girer. Yeniden üretim de bütçe kapısından geçer. Eski dosya `_ESKI/` altına taşınır, kalıcı silme yoktur [kaynak: H/is-bitince-d-arsiv].
- Kredili aşama yeniden başlarken önce `KREDI_DEFTERI.jsonl` okunur. `gonderildi` olup `indirildi` olmayan işler **yeni gönderim yapmadan** toplanır (`memmet_topla.py`). Yeni gönderim ancak bundan sonra yapılır [kaynak: H/olagandisi-dur].
- **Kilit:** `FILM.kilit` dosyası `{pid, makine, ortam, zaman}` tutar. İkinci bir `film.py` ya da Memmet aynı filmde çalışamaz (çift tıklama çift harcama yapar). Kilidin bayat sayılması için iki koşuldan biri yeter: süreç yok ya da kilit 30 dk güncellenmemiş [tahmin].
- **DUR dosyası:** `DURDUR.bat` film klasörüne `DUR` adlı bir dosya yazar. `film.py` ve Memmet her döngüde buna bakar. Elindeki indirmeyi bitirir, yeni gönderim yapmaz, çıkış kodu 2 ile durur.
- **Atomik yazım:** Her JSON önce `x.tmp`'ye yazılır, sonra `os.replace` ile yerine konur. Şimdiki `film.py` dosyayı doğrudan `open(..., "w")` ile yazıyor; elektrik giderse durum dosyası bozulur.

**Ortam algılama:** Windows ise `yerel`. Diğer her durumda `bulut`, meğer ki `AYARLAR/FILM_AYAR.json` içinde `"ortam": "yerel"` yazsın. Bulutta yalnız `sahte`, `kaset` (testler) ve `claude_code` sağlayıcıları açıktır. Kredili sağlayıcıyı çağıran kod yolu `ORTAM` (4) ile çıkar.

### 2.1 Kâğıt evresi (kredi yok; bulutta da çalışır)

Kısaltmalar: **B** = bulutta olur, **Y** = yalnız yerelde. Uzman alanı parantez içinde.

| Kod | Girdi → İş | Çıktı | Geçme şartı | Kim | Ortam |
|---|---|---|---|---|---|
| H0 hazırlık | Makine durumu → Python sürümü, ffmpeg, disk (C'de ≥ 20 GB [tahmin; film başına 5–8 GB, kaynak: BASLA_BURADAN]), sağlayıcıların `hazir()` sonucu, model dosyaları, kilit, ortam | `_RAPOR/H0.json` | Eksikler yalnız kendi aşamasını engeller. Yalnız disk ve kilit genel engeldir | betik `film.py --hazirlik` | B/Y |
| K01 konu | Kullanıcının tek cümlesi | `00_KONU.md` | Boş değil | ana Claude (tek soru) | B/Y |
| K02 kararlar + brifing | Konu + seri evreni kütüphanesi + `KARARLAR.md` + araştırma | `PROJE_KARARLARI.md`, `_HIKAYE_ODASI/00_BRIFING.md` | Şema: zorunlu başlıklar, süre hedefi, NE YOK listesi, seri kararı (yeni ya da devam) | ana Claude + (senarist) | B/Y |
| K03 hikâye odası | Brifing → A/B + bonus öneri → 5 jüri → hakem | `oneri_*.md`, `juri_*.md`, `oneri_SECIM.md` | Bütün raporlarda ÖZET satırı okunur (`puan_oku.py`). Seçim gerekçesi var | ajan: hikaye-mimari ×3, jüri ×5, hakem (senarist) | B/Y |
| K04 3 partilik yapı | Seçilen öneri → 8 başlıklı 3 parti + makine alanları | `hikaye_vN.md` + `HIKAYE.json` (vuruşlar, duygu haritası, MERAK_DEFTERI, KURULUMLAR, IRONILER, karakter ve mekân listesi) | `HIKAYE.json` şeması. Vuruş oranı ±%4, parti sonu ≥ 8 [kaynak: ritim_esikleri] | ajan: hikaye-mimari | B/Y |
| K05 kâğıt seyirci (S1a) | Betiğin hazırladığı `OKUNACAK.md`: yalnız ekranda olan, amaç yok → 3 bağımsız seyirci + ilk 2 dk testi | `_SEYIRCI/kagit_tN/seyirci_{1..3}.md` → `_RAPOR/S1a_tN.json` | GENEL medyanı ≥ 8, ölçüt medyanı ≥ 7, KRİTİK 0, özet eşleşmesi ≥ 0,8, ilk 2 dk sorusuna 3/3 "evet" [kaynak: ZANAAT §7.2–7.3]. Geçmezse aynı mimar yeni sürüm yazar, en çok 4 tur | betik `seyirci_hazirla.py` + ajan ×3 (yeni örnek) + betik `seyirci_karar.py` | B/Y |
| K06 yönetmen planı | `hikaye_vN` + `HIKAYE.json` → parti parti plan listesi (eylem zinciri, durumlar, kadraj, kesme, kamera konumu, eksen) | `_YONETMEN/05_PLANLAR.json`, `05_yonetmen.md` (kroki) | Şema geçerli. Her planda `baslangic_durumu`, `bitis_durumu`, `eylem_zinciri` dolu | ajan: yonetmen (parti başına 1 çağrı) | B/Y |
| K07 dünya defteri + K0 | `05_PLANLAR.json` → makine varlık zaman çizelgesini kurar, zıplamaları arar | `DUNYA_DEFTERI.json`, `_RAPOR/K0_Pn.json` | K0'da HATA 0 [kaynak: 02_sureklilik §6.2] | betik `dunya_defteri.py` + (yorum gerekenlerde) ajan: sureklilik-denetcisi | B/Y |
| K08 ses kâğıtta | Planlar → plan başına ses yolu, ambiyans, efekt, müzik ipucu, leitmotif | `_SES/ses_plani.json`, `KURGU/muzik_listesi.json` | Şema + Z2 #40 [kaynak: ZANAAT] | ajan: muzik-supervizoru, ses tasarımcısı (ses uzmanı) | B/Y |
| K09 istem derleme | Plan alanları → `gorsel_istem` ve `hareket_istem` kodla derlenir (saniyeli adımlar, `No music.`), yedekler yazılır | `SAHNELER.json` (mevcut şemayla uyumlu) | `istem_denetim.py` HATA 0 | betik `istem_derle.py` + (yalnız istisnalarda) ajan: istem-muhendisi | B/Y |
| K10 kâğıt kapıları | `SAHNELER.json` + `DUNYA_DEFTERI` + `HIKAYE.json` → Z0, Z1, Z2, K0, istem denetimi, şema, üretilebilirlik | `_RAPOR/Z0..Z2_Pn.json`, `KUYRUK/YENIDEN_YAZ.json` | HATA 0. BAYRAK'lar bir kez ilgili ajana gösterilir. HATA'lı plan yazan ajana döner (K06 ya da K04), en çok 3 tur [tahmin] | betik `kagit_kapilari.py` + ajan: uretilebilirlik-denetcisi | B/Y |
| K11 plan seyircisi (S1b) | Plan düzeyinde ekranda olan alanlar (`ekranda_bilgi`, replik, görsel tarifi, kartlar) → 3 seyirci, parti parti | `_SEYIRCI/plan_Pn_tN/` → `_RAPOR/S1b_Pn_tN.json` | S1a ile aynı eşikler, en çok 3 tur [tahmin]. Gerekçe: babanın adının 84. çekimde geçtiği bu düzeyde bulunmuştu [kaynak: YR A8] | betik + ajan ×3 | B/Y |
| K12 ön bütçe (B1) | Plan ve klip sayısı, model, birim fiyat, yeniden çekim payı, bakiye (biliniyorsa) | `URETIM_ONIZLEME.json` (taslak) | Tahmin ≤ film bütçe tavanı. Geçmezse **5 BÜTÇE** ile durur. Hat **kendiliğinden film kısaltmaz** (§9 C2) | betik `kredi.py` | B/Y |

### 2.2 Varlık evresi (Flow video kredisi yok; görsel 0 kredi ya da elle)

| Kod | Girdi → İş | Çıktı | Geçme şartı | Kim | Ortam |
|---|---|---|---|---|---|
| V01 kart eşleme | `HIKAYE.json` karakter, mekân ve nesne listesi + `KUTUPHANE/<SERI>` → yeniden kullanılacaklar (`id@sürüm`) ve üretilecek yeniler | `KART_LISTESI.json` | Her `referans` ya kütüphaneden çözülmüş ya da üretim listesinde | betik `kutuphane.py esle` + ana Claude | B/Y |
| V02 kart üretimi | Yeni kartlar → Gemini paketi (karakter başına 3 aday [kaynak: YR A6]) ya da `vertex_gorsel` | `GELENLER/*.zip` → `01_KARAKTERLER/`, `02_MEKANLAR/`, `03_NESNELER/` adayları | Beklenen dosyalar geldi | betik `gemini_paket.py --kartlar` / `gemini_al.py` + **kullanıcı (paketi Gemini'ye taşır)** | Y (paket B'de hazırlanabilir) |
| V03 kart seçimi + denetim | Adaylar → yüz bulunur mu (SFace), tam boy mu, fon, NE YOK listesi, anatomi (VLM) → seçim | Kütüphaneye kayıt: `kimlik.json`, `yuz_sface.npy`, kartlar | Her insan kartında yüz bulunur, VLM `GEC`. `--onayli` modda kullanıcı onaylar | betik `kutuphane.py kaydet` + ajan (görüntü uzmanı) | Y |
| V04 ses kartları | Karakter ses tarifi → AI84 paylaşılan seslerinden 2 aday, karakterin kendi repliğiyle okunur → seçim. Dönüştürücü seçildiyse referans ses ya da RVC eğitim verisi | Kütüphane `sesler.json`, `ses/ornek.wav` | Konuşan her karakterin `voice_id`'si var. AI84 bütçesi geçer (küçük tutar) | ajan (ses uzmanı) + betik `seslendir.py --aday` | Y |
| V05 başlangıç görselleri | `SAHNELER.json` → 30 sahnelik Gemini paketleri [kaynak: H/gemini-ajan-gorsel]. `risk` işaretli planlara 2 aday [kaynak: 01_film_hatlari fikir 2]. `zincir.yontem = son_kare` olan planlar burada üretilmez (§8.3-d) | `SIRALI_GORSEL/NNN.jpg` (+ `NNN_b.jpg`) | Bütün planlarda görsel var (son_kare planları hariç) | betik + **kullanıcı (paket taşıma)**; az sayıdaki düzeltmeyi Memmet Flow'da yapar (0 kredi) | Y |
| V06 G1 görsel kapısı | Görseller + kütüphane yüz gömmeleri + plan `baslangic_durumu` → yerel ölçümler + kör VLM tarifi + deterministik karşılaştırma | `_RAPOR/G1_Pn.json`, `KUYRUK/YENIDEN_URET.json` (görsel) | HATA 0. En çok 2 düzeltme turu [kaynak: 01_URETIM_HATTI §5], sonra plan değişikliği için yönetmene döner | betik `gorsel_denetim.py` + ajan: vlm-denetci (görüntü uzmanı) + betik `karsilastir.py` | Y (ölçüm B'de olur, görseller yerelde) |
| V07 animatik | Görseller + `sure_sn` + taslak TTS (AI84, ucuz) + ambiyans + geçici müzik → parti başına mp4 + izleme paketi | `ANIMATIK/P{n}.mp4`, `_RAPOR/IZLEME_ANIMATIK_Pn/` | Dosyalar var. Süre ≈ planlanan ±%5 [tahmin] | betik `animatik.py`, `izleme_paketi.py --animatik` | Y |
| V08 animatik seyircisi (S2) | Kare paketi + duyulan replik → 3 bağımsız seyirci, parti parti | `_SEYIRCI/animatik_Pn_tN/` → `_RAPOR/S2_Pn_tN.json` | S1 eşikleri. Geçmezse yönetmen düzeltir ve yalnız etkilenen planlar K09 → V05 → V06 → V07 yoluna döner. En çok 3 tur [tahmin] | ajan ×3 + betik `seyirci_karar.py` | Y |
| V09 kesin bütçe (B2) + üretim önizlemesi + git/gitme | Bütün kapı raporları + plan sayıları + bakiyeler (Flow menüsü, `ai84.credits()`) | `URETIM_ONIZLEME.md/.json` | (1) Z0–Z2, K0, S1a, S1b, G1 ve S2 bu girdi imzasıyla `GEC`. (2) Tahmin ≤ bakiye × 0,9 [tahmin] ve ≤ tavan. (3) hat-denetcisi `GIT` dedi. Hepsi sağlanmazsa 5 ya da 6 ile durur | betik `kredi.py --kesin` + ajan: hat-denetcisi | Y |

### 2.3 Üretim evresi (kredi)

| Kod | Girdi → İş | Çıktı | Geçme şartı | Kim | Ortam |
|---|---|---|---|---|---|
| U01 video (dalgalar) | Onaylı önizleme → sağlayıcı zinciri. Dalga 1: bağımsız ve `bitis_karesi` zincirli planlar. Dalga 2+: `son_kare` planları (§8.3-d) | `SIRALI_VIDEO/NNN.mp4`, `KUNYE/NNN.json`, `KREDI_DEFTERI.jsonl` | Her plan için dosya var ve V1 geçti. Kısıt gelirse hemen durur | betik `film.py` → sağlayıcı (`flow`/Memmet, `veo_vertex`, `sahte`) + **kullanıcı: `VIDEO_*.bat`'ı başlatır** | Y |
| U02 V1 teknik | Her indirmeden hemen sonra: ffprobe süresi, siyah kare, donma, klip içi kesme | `_RAPOR/V1.json` | [kaynak: 02_sureklilik §6.2 V1] | betik `kalite_denetim.py --klip` | Y |
| U03 V2 + K1 + bitiş durumu | Klip kareleri + kütüphane + plan durumları → yüz kayması, belirme, morf, ekran yönü, ilk kare sadakati, son kare ↔ sonraki ilk kare. Kör VLM son kareyi tarif eder, betik `bitis_durumu` ile karşılaştırır | `_RAPOR/V2_Pn.json`, `_RAPOR/K1_Pn.json`, `KUYRUK/YENIDEN_URET.json` (video) | HATA 0. Plan başına en çok 2 yeniden çekim [tahmin], sonra yönetmen karar verir: plan değiştir, bağlayıcı plan ekle ya da kırp | betik `video_denetim.py` + ajan: vlm-denetci | Y |
| U04 zincir dalgası | `son_kare` planları: önceki klibin son karesi çıkarılır → hızlı G1 → başlangıç görseli olur | `SIRALI_GORSEL/NNN.jpg` (`kaynak: son_kare`) | G1 (kimlik + bitiş durumu) geçer. Zincir derinliği ≤ 2 [kaynak: 02_sureklilik §2.3, ölçülmemiş öneri] | betik `zincir.py` | Y |
| U05 yeniden çekim kuyruğu | `YENIDEN_URET.json` (video) → mini bütçe kapısı → U01 | aynı | Kuyruktaki her madde ya üretildi ya da yönetmen kararıyla kapandı | betik + (karar için) ajan: yonetmen | Y |

### 2.4 Kurgu evresi (kredi yok, yerel CPU)
Bu aşamaların içeriği kurgu ve ses uzmanlarının alanında. Hat yalnız sırayı, çıktıyı ve kapıyı tanımlar.

| Kod | İş | Çıktı | Geçme şartı | Kim |
|---|---|---|---|---|
| M01 | `plan_kurgu`: kırpma, kesme, J/L | `KURGU/KURGU_PLANI.json` (+ `.otio` yedek) | Şema | betik |
| M02 | Ses: ayrıştırma → dönüştürme ya da TTS + dudak → `dudak_denetim` → `diyalog_esitle` → `ses_katmani` → müzik yerleşimi | `SESLER/`, `KURGU/` | Ses uzmanının eşikleri (WER, SyncNet, LUFS) | betikler (+ ses uzmanı ajanları) |
| M03 | Z3 kurgu kapısı | `_RAPOR/Z3_Pn.json` | HATA 0 [kaynak: ZANAAT §6.2 Z3] | betik |
| M04 | Kurgu izleme denetimi (S3): üçlü pencereli kare paketi, 3 seyirci, parti parti | `_RAPOR/S3_Pn_tN.json` | S1 eşikleri. Parti başına KRİTİK 0, ORTA ≤ 3. En çok 3 tur. Yeni çekim gerekirse U05'e döner (bütçe kapısı) | ajan ×3 + betik |
| M05 | Kesme turu: kesici ajan → Z1 kurulum denetimi yeniden | `_RAPOR/KESME.json` | Önerilerin ≥ %50'si uygulanır. Z1 HATA 0 | ajan (kurgu) + betik |
| M06 | CapCut katmanlı taslak + renk cilası + ffmpeg master render | `KURGU/son_capcut_projesi.json`, `FINAL/film.mp4` | Dosyalar var | betik |
| M07 | Son kalite: siyah kare, donma, sessizlik, −14 LUFS ±1, ≤ −1 dBTP | `_RAPOR/KALITE_FINAL.json` | HATA 0 [kaynak: ZANAAT §5.1] | betik `kalite_denetim.py --final` |

### 2.5 Yayın ve kapanış
| Kod | İş | Çıktı | Kim |
|---|---|---|---|
| Y01–Y05 | Jenerik, kapak adayları ve kapak denetimi, YouTube paketi, 3 Short, altyazı (EN, istenirse TR) | `YAYIN/` | ajan: yayin-paketcisi + betikler (yayın uzmanı) |
| Y06 | Yükleme: **isteğe bağlı ve onaylı** [kaynak: CLAUDE.md §Yapılacaklar 6] | — | kullanıcı onayı |
| S01 | Ders defteri derlemesi | `KUTUPHANE/DERSLER/derleme_<film>.md`, aday kurallar | ajan: ders-katibi + betik `ders_defteri.py` |
| S02 | Kütüphane güncellemesi (yeni varyant, ses, mekân) | `KUTUPHANE/<SERI>/` | betik + ana Claude |
| S03 | Film sonu raporu: tahmin ve gerçek kredi, yeniden çekim oranı, kapı istatistikleri, süreler | `FILM_SONU_RAPORU.md` | betik |
| S04 | Arşiv: ara klasörler `D:\YZ_FILM_ARSIV\<FİLM>\` altına **taşınır** (`robocopy /E /MOVE`, `/MIR` yasak). Son taslağın bağlı olduğu dosyalara dokunulmaz [kaynak: H/is-bitince-d-arsiv] | taşıma listesi | betik `arsivle.py` |

### 2.6 Sıranın gerekçesi (kısa)
- v2 sırası korunuyor [kaynak: H/uretim-hatti-v2]: hikâye → seyirci → yönetmen → ses → kartlar → görsel + denetim → animatik → video → kurgu → yayın.
- Eklediğim üç şey var:
  - **K11 plan seyircisi.** Bilgi kopukluklarının çoğu plan düzeyinde kâğıtta görünür [kaynak: YR A8].
  - **İki bütçe kapısı.** K12 erken uyarır; tasarım bütçeyi aşıyorsa görsel emeği boşa gitmez. V09 kesin kapıdır.
  - **U04 zincir dalgası.** Kare zinciri video üretimini sıralı bir bağımlılığa çevirir (§8.3-d).
- B1'deki hata, video kredisinin animatik onayı olmadan harcanmasıydı [kaynak: H/proje-b2]. Bunu kod engeller: U01'in girdi imzası S2 raporlarının imzasını içerir.

---

## 3. Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) — yalnız kendi alanım

Hattın ana yürütücüsü bir ajan değildir. **Ana Claude** (film-yap becerisi) yürütür, `film.py` sırayı söyler (§2.0). Alanımda ölçülemeyen ve
yargı isteyen yalnız üç iş var. Bunlar için üç ajan öneriyorum. Kredi tahmini, dalga planı, kilit ve bildirim gibi ölçülebilen işler
**betiktir, ajan değildir** [kaynak: 03_ses_ve_claude_code B4 "Prefer scripts for deterministic operations"].

### 3.1 `ders-katibi`
| Alan | Değer |
|---|---|
| model / effort | `opus` / `high`. Gerekçe: defterdeki her kural bütün gelecek filmleri etkiler [kaynak: H/ajan-opus-yuksek] |
| tools | `Read, Glob, Grep, Write, Bash(python YZ_FILM/ARACLAR/ders_defteri.py *)`. Edit yok. Write yalnız `KUTUPHANE/DERSLER/` altına (hook ile zorlanır, §4.3) |
| Görev | Ham kayıtları kümelemek ve aday kural çıkarmak. Kanıt eşiği aşılan adayları `KURALLAR_OGRENILEN.json` önerisine yazmak. Çelişen ya da işe yaramayan kuralları emekliye ayırmak. Film sonunda 1 sayfalık "bu filmde ne öğrendik" yazmak |
| Okuyacakları | `ders_defteri.py --derle` çıktısı (kümeler ve sayılar), `KURALLAR_OGRENILEN.json`, `03_DERSLER.md`, `BILGI_KURALLARI.md` §8 çelişkiler, `ritim_esikleri.json`, `FILM_SONU_RAPORU.md` |
| Çıktı | `KUTUPHANE/DERSLER/derleme_<film>_<tarih>.md` ve `aday_kurallar.json`. Aday kurallar `ders_defteri.py --uygula` ile şemadan ve korkuluklardan geçirilerek birleştirilir (§5.8) |
| Kesin yasaklar | Güvenlik kurallarını gevşetmek: bot tespiti, Flow uyarısında durma, gizli bilgi, kalıcı silme, onay atlama. Tempoyu hızlandırmak. Kanıtsız kural. Tek filmden genelleme (§7) |

### 3.2 `memmet-bakimci`
| Alan | Değer |
|---|---|
| model / effort | `opus` / `high`. Değişmiş bir DOM'u çözmek yargı ister; yanlış seçici kredi yakar |
| tools | `Read, Glob, Grep, Edit, Bash(python -m unittest *), Bash(python YZ_FILM/ARACLAR/memmet.py * --kuru)`. Edit yalnız `memmet.py`, `saglayicilar/flow.py`, `testler/fikstur_flow/*` ve `BILGI/FLOW_KESIF.md` için (hook) |
| Ne zaman | Memmet `arayuz` kısıt koduyla durunca (seçici bulunamadı, beklenmeyen sayfa). Yalnız yerel ortamda |
| Görev | `_MEMMET_HATALAR/*.html` ve `.png` dosyalarını okumak. Değişen seçiciyi bulmak. Yeni sayfayı HTML fikstürü olarak `testler/fikstur_flow/`'a eklemek. `memmet.py`'yi düzeltmek. Testleri çalıştırmak. `FLOW_KESIF.md`'yi güncellemek. Düzeltme sonrası ilk gerçek gönderim **yarı otomatik modda** (insan basar) yapılır |
| Çıktı | Kod değişikliği + `_MEMMET_HATALAR/BAKIM_<tarih>.md` (ne değişti, hangi fikstürle doğrulandı) |
| Kesin yasaklar | reCAPTCHA çözme, insan taklidi fare ya da klavye, tempo hızlandırma, uyarı metnini görmezden gelme, uyarıdan sonra kendiliğinden yeniden başlatma [kaynak: H/olagandisi-dur, 03_DERSLER] |

### 3.3 `hat-denetcisi`
"Hiçbir model kendi çıktısını onaylamaz" ilkesinin kredi kapısındaki karşılığı [kaynak: 01_film_hatlari B4 ARIS].
| Alan | Değer |
|---|---|
| model / effort | `opus` / `high` |
| tools | `Read, Glob, Grep, Write` (yalnız `_RAPOR/HAT_DENETIM_*.md`) |
| Ne zaman | V09'da her kesin bütçe kapısından önce. U05'te yeniden çekim kuyruğu 30 klibi aşarsa [tahmin] |
| Görev | Betik kapılarının göremediği şeyleri aramak. Sağlayıcı ya da model karışımı sahne grubu ortasına düşüyor mu? Ders defterinde 3/3 başarısız olmuş bir desen (ör. diyalogda yörünge kamera) planda 12 kez var mı? Tempo planı son uyarı geçmişiyle çelişiyor mu? Aynı gün yoğun görsel gönderimi oldu mu (ders: o akşam ~40 görsel sonrası hesap işaretlendi [kaynak: 03_DERSLER])? Bütçe tavanı tek bir sahneyi yarıda bırakacak mı? |
| Okuyacakları | `URETIM_ONIZLEME.json`, `_RAPOR/*.json` özetleri, `KURALLAR_OGRENILEN.json`, son 30 günün kısıt kayıtları, `FILM_AYAR.json` (anahtar dosyaları değil) |
| Çıktı | `_RAPOR/HAT_DENETIM_<n>.md`. Son satır: `OZET | karar: GIT/GITME | KRITIK: 0 | ORTA: 2`. `film.py` bunu `puan_oku` mantığıyla okur. `GITME` → çıkış kodu 6 ve gerekçe |

### 3.4 Başka alanlardan kullandığım ajanlar (tanım onlarda)
`habersiz-seyirci` (S1a, S1b, S2, S3), `vlm-denetci` (G1, V2 kör tarifi), `yonetmen`, `hikaye-mimari`, `istem-muhendisi`, `sureklilik-denetcisi`,
`uretilebilirlik-denetcisi`, `muzik-supervizoru`, `yayin-paketcisi`. Benim bunlardan iki isteğim var:
1. Çıktıları **makinece okunur** olsun: sabit JSON ya da son satırda `OZET |`.
2. Her ajanın girdi ve çıktı yolları `film.py` iş tanımından gelsin. Ajan kendi başına dosya aramasın. Habersizlik ancak böyle korunur: seyircinin okuyacağı tek dosyayı betik hazırlar.

### 3.5 Ajan çağrısı bütçesi (40 dk film) [tahmin]
| Aşama | Çağrı |
|---|---|
| K03 hikâye odası | ≈ 10 |
| K04–K05 (2–4 tur × 3 seyirci + yazar) | ≈ 8–16 |
| K06 yönetmen (3 parti × 1–3 tur) | ≈ 3–9 |
| K10–K11 (3 parti × 3 seyirci × 1–3 tur) | ≈ 9–27 |
| V06 G1 (≈ 440 görsel ÷ 20'lik parti × 1–2 tur) | ≈ 22–44 |
| V08 S2 | ≈ 9–27 |
| U03 V2 kör tarif (şüpheliler) | ≈ 10–20 |
| M04 S3 | ≈ 9–27 |
| Diğer | ≈ 10 |
| **Toplam** | **≈ 90–190** |

Bu sayı abonelik kullanım sınırına takılabilir ("EMBERFALL'da sınır doldu, ajanlar yarıda kesildi" [kaynak: YR §1]). Bu yüzden iki kural var:
- Her ajan önce dosyasını yazar.
- `film.py` yarım çıktıyı `--dogrula` ile yakalar ve aynı işi yeniden kuyruğa koyar.

---

## 4. Beceri (skill) tarif adımları — kendi alanım (hat yürütme)

### 4.1 Dosya düzeni
```
.claude/skills/film-yap/
  SKILL.md                 ≤ 500 satır. En üstte kesin kurallar, sonra yürütme döngüsü [kaynak: 03 B4]
  hat/ASAMALAR.md          film.py --asamalar --md ile ÜRETİLİR (elle yazılmaz; drift olmasın)
  hat/KISITLAR.md          sağlayıcı kısıtında ne yapılır (§5.6 tablosu)
  hat/sablonlar/<KOD>.md   her ajan aşamasının talimat şablonu (Claude Code ve claude_api yolu aynı dosyayı kullanır)
  hat/KULLANICI_MESAJLARI.md  kullanıcıya giden sabit Türkçe cümleler (tek cümle + hangi .bat)
```

### 4.2 SKILL.md'nin hat bölümü (tarif)
**Frontmatter**
- `name: film-yap`
- `description`: Türkçe ve İngilizce tetikleyiciler ilk cümlede ("film yap, yeni film, devam et, nerede kaldık, film, movie, continue the film"). description + when_to_use ≤ 1.536 karakter [kaynak: 03 B2–B3].
- `allowed-tools`: yalnız dar komutlar: `Bash(python YZ_FILM/ARACLAR/film.py *)`, `Bash(py -3.10 YZ_FILM/ARACLAR/film.py *)`. Geniş `Bash` yok.
- Dinamik bağlam: `` !`python YZ_FILM/ARACLAR/film.py --aktif --durum --kisa` ``. Beceri her açıldığında hat durumu metne gömülür [kaynak: 03 B2, B6].

**En üst kurallar** (sıkıştırmadan sonra yalnız ilk 5.000 token geri gelir [kaynak: 03 B4]):
1. Kullanıcıya yalnız konu sorulur. Diğer kararları ekip verir ve `KARAR_DEFTERI.md`'ye "karar — neden — yanlışsa maliyeti" biçiminde yazar [kaynak: 03 B6].
2. Kredi yalnız `film.py` bütçe kapısı geçince harcanır. Claude sağlayıcıyı doğrudan çağırmaz.
3. Flow "olağan dışı etkinlik" uyarısında hat durur. Yeniden başlatma, atlatma ve tempo hızlandırma yoktur.
4. `AYARLAR/` okunmaz ve yazılmaz. Anahtarları yalnız betikler okur.
5. Kalıcı silme yok; eski dosyalar `_ESKI/`'ye taşınır.
6. Hafızaya değil `film.py --durum` çıktısına ve dosyalara güvenilir.

**Yürütme döngüsü**
```
0. Aktif film yoksa: kullanıcıya TEK soru ("Filmin konusu ne?") →
   film.py yeni --konu "<cevap>"   (film adını ekip verir, klasör ve .bat'lar kurulur)
1. film.py <film> --sonraki --json  →  iş tanımı (§5.1)
2. kim'e göre:
   betik     → film.py <film> --calis   (bir sonraki ajan ya da insan işine kadar yürür)
   ajan      → tanımdaki her ajanı başlat (paralel=true ise aynı mesajda, her biri YENİ örnek);
               istemi hat/sablonlar/<KOD>.md + iş tanımının girdi ve çıktı yollarıyla kur;
               bitince film.py <film> --dogrula <KOD>
               (şema hatasında aynı ajana SendMessage ile en çok 2 düzeltme; habersiz seyirciye ASLA)
   kullanici → iş tanımındaki tek cümleyi kullanıcıya yaz (Telegram'ı film.py zaten gönderdi); turu bitir
   ortam     → (bulut) kâğıt çıktıları commit et; "bilgisayarında GUNCELLE.bat, sonra DEVAM.bat" de; turu bitir
   butce     → URETIM_ONIZLEME.md özetini (3 satır) yaz; turu bitir
   kisit     → kısıtın Türkçe açıklamasını ve elde kalan yolları (hat/KISITLAR.md) yaz; turu bitir
   bitti     → film sonu raporunun özetini yaz
3. 1'e dön. Bir turda en çok N aşama yürütülür (bağlamı korumak için, N=6 [tahmin]); sonra kısa durum satırı.
```

**Kullanıcıya konuşma biçimi.** Soru sorulmaz, durum söylenir. Örnek: "Hikâye 3. turda 8/8/9 aldı, yönetmen planı yazılıyor."
Kullanıcının bilmediği kavramlar bir kez açıklanır [kaynak: YR A0].

### 4.3 Hook'lar (her zaman uyulması gereken kurallar becerinin değil hook'un işi [kaynak: 03 B4, öneri 11])
| Olay | Eşleyici | Ne yapar |
|---|---|---|
| `SessionStart` | `startup\|resume\|compact` | `film.py --aktif --durum --kisa` çıktısını `additionalContext` olarak ekler (≤ 10.000 karakter) |
| `PreToolUse` | `Read\|Edit\|Write` yolu `YZ_FILM/AYARLAR/` | Reddeder. `OKU_BENI.txt` ve `*.ornek.json` hariç |
| `PreToolUse` | `Bash` içinde `AYARLAR`, `rm -rf`, `del /s`, `rmdir /s`, `git add -A` + `AYARLAR`, `robocopy … /MIR` | Reddeder |
| `PreToolUse` | `Bash` içinde `memmet.py` + (bulut ortamı) | Reddeder ("bulutta Flow yok") |
| `PreToolUse` | `ders-katibi` / `memmet-bakimci` ajanlarının Write ve Edit yolu | Kendi izinli klasörleri dışında reddeder |

### 4.4 Değerlendirme senaryoları (beceri tetiklenme ve davranış testi, en az 3 [kaynak: 03 B4, öneri 12])
1. "Ejderha büyüten bir kadın hakkında film yap" → tek soru sorulmaz (konu zaten verildi), `yeni --konu` çalışır, K02'den başlar.
2. "Devam et" (bağlam boş, K10 yarımken) → `--sonraki` K10'u verir, yeniden yazım kuyruğu işlenir, K01–K09 yeniden yapılmaz.
3. Bulutta "videoları üret" → `ORTAM` (4), commit ve yerel yönlendirmesi; Memmet çağrılmaz.
4. Flow kısıtı kaydı varken "devam et" → `KISIT` (7), yeniden deneme önerilmez; elle 1 deneme ya da izinli yedek seçenekleri söylenir.

---

## 5. Veri şeması / plan alanları (JSON örneğiyle)

### 5.1 İş tanımı (`film.py <film> --sonraki --json`)
```json
{
 "film": "DEMIR_KANAT",
 "asama": "K05",
 "ad": "kagit_seyirci_hikaye",
 "durum": "ajan_bekliyor",
 "tur": 2, "tur_max": 4,
 "kim": "ajan",
 "ajanlar": [
  {"ad": "habersiz-seyirci", "adet": 3, "paralel": true, "yeni_ornek": true,
   "girdiler": ["_SEYIRCI/kagit_t2/OKUNACAK.md"],
   "cikti_kalibi": "_SEYIRCI/kagit_t2/seyirci_{i}.md",
   "sablon": ".claude/skills/film-yap/hat/sablonlar/K05.md"}
 ],
 "sonra": ["python YZ_FILM/ARACLAR/film.py DEMIR_KANAT --dogrula K05"],
 "ortam_gerek": "her_ikisi",
 "kullaniciya": null,
 "cikis_kodu": 3
}
```
`kim: kullanici` olduğunda `kullaniciya` tek cümledir:
`{"metin": "Gemini paketi 3/15 hazır: Masaüstü\\GEMINI GORSEL ISTEM\\DEMIR_KANAT_P1_03 klasörünü Gemini'ye ver, gelen ZIP'i GELENLER'e at.", "bat": "GEMINI_AL.bat"}`.

### 5.2 Aşama kaydı (kodda tek doğruluk kaynağı; belge bundan üretilir)
```python
ASAMALAR = [
 # kod,   ad,                      kim,       girdiler,                                    ciktilar,                           kapi,   kredili, ortam,   tur_max, geri_don
 ("K09", "istem_derle",           "betik",   ["_YONETMEN/05_PLANLAR.json","_SES/ses_plani.json","KUTUPHANE:evren"], ["SAHNELER.json"], "ISTEM", False, "her_ikisi", 1, None),
 ("K10", "kagit_kapilari",        "betik",   ["SAHNELER.json","DUNYA_DEFTERI.json","HIKAYE.json","ESIKLER"], ["_RAPOR/Z0_P*.json", "..."], "Z0+Z1+Z2+K0", False, "her_ikisi", 3, "K06"),
 ("V09", "butce_kesin",           "betik+ajan", ["_RAPOR/*", "SAHNELER.json", "BAKIYE"], ["URETIM_ONIZLEME.json"], "B2", False, "yerel", 1, None),
 ("U01", "video",                 "betik",   ["URETIM_ONIZLEME.json@GEC", "SIRALI_GORSEL/"], ["SIRALI_VIDEO/","KUNYE/"], "V1", True,  "yerel",  None, "U05"),
]
```
`ESIKLER` = `ritim_esikleri.json` + `KURALLAR_OGRENILEN.json`. Bunların sürümü imzaya girer. Eşik değişince kâğıt kapıları yeniden çalışır, kredili çıktılar yalnız `bayat` diye işaretlenir.

### 5.3 Çıktı zarfı ve `FILM_DURUM.json` (önbellek)
```json
"_uretim": {"asama": "K09", "girdi_imza": "9f1c0a2b7e44d310", "arac": "istem_derle.py 1.0",
            "esik_surum": "ritim@1.0+ogrenilen@7", "sonuc": "GEC", "zaman": "2026-10-23T15:02:11+03:00", "ortam": "bulut"}
```
```json
{
 "surum": 2, "film": "DEMIR_KANAT", "ortam_son": "yerel",
 "asamalar": {
  "K05": {"durum": "tamam", "tur": 3, "girdi_imza": "…", "rapor": "_RAPOR/S1a_t3.json", "son": "…"},
  "V06": {"durum": "kapi_gecmedi", "tur": 1, "kuyruk": "KUYRUK/YENIDEN_URET.json", "son": "…"},
  "U01": {"durum": "kismi", "dalga": 1, "biten": 212, "toplam": 405}
 },
 "harcama": {"flow_kredi": 2544, "ai84_kredi": 15840, "usd": 0.0},
 "gecmis": [{"zaman": "…", "olay": "kisit", "asama": "U01", "kod": "olagandisi", "plan": 213}]
}
```
`durum` değerleri: `bekliyor`, `calisiyor`, `ajan_bekliyor`, `kullanici_bekliyor`, `kapi_gecmedi`, `kismi`, `tamam`, `bayat`.

### 5.4 Kapı raporu ve kuyruklar (ZANAAT §6.2 biçimine imza ve tur eklendi)
```json
{"kapi": "G1", "parti": 2, "tur": 1, "sonuc": "HATA",
 "girdi_imza": "…", "esik_surum": "ritim@1.0+ogrenilen@7", "arac": "gorsel_denetim.py 0.3",
 "ozet": {"plan": 168, "gec": 151, "bayrak": 12, "hata": 5},
 "hatalar": [{"madde": "G1.1_kimlik", "plan": 212, "olcu": 0.31, "esik": 0.363, "seviye": "H",
              "oneri": "CORRECTION: Mara's scar is above her LEFT eyebrow.", "kanit": "SIRALI_GORSEL/212.jpg"}]}
```
`KUYRUK/YENIDEN_URET.json` (görsel ve video tek dosya, `tur` alanıyla ayrılır):
```json
[{"plan": 212, "tur": "gorsel", "neden": "G1.1_kimlik", "duzeltme": "CORRECTION: …", "kaynak_rapor": "_RAPOR/G1_P2.json",
  "deneme": 2, "deneme_max": 2, "durum": "bekliyor", "karar_veren": null}]
```
`KUYRUK/YENIDEN_YAZ.json` kâğıt hataları içindir. Her maddede `{"plan", "madde", "yazar": "yonetmen|hikaye-mimari", "oneri"}` bulunur. Kuyruk yazan ajana geri gider (revizyonu aynı yazar yapar [kaynak: YR §1]).

### 5.5 Plan düzeyi: `uretim` alt nesnesi (yalnız benim alanım; diğer alt nesneler `zanaat`, `sureklilik`, `ses` diğer uzmanlarda)
```json
"uretim": {
  "uretim_blogu": 7,
  "saglayici": "flow", "model": "omni-1.1-flash", "cozunurluk": "720p", "klip_sn": 8,
  "zincir": {"yontem": "bitis_karesi", "bitis_plan": 143, "kaynak_plan": null, "derinlik": 0, "dalga": 1},
  "deneme": 1, "deneme_max": 2, "seed": null,
  "is_kimligi": "V-142-d1-7f3a9c",
  "plan_imza": "c0ffee12",
  "durum": "bekliyor"
}
```
- `zincir.yontem`: `yok` | `bitis_karesi` | `son_kare` (§8.3-d).
  - `bitis_karesi`: sonraki planın başlangıç görseli bu klibin bitiş karesi olarak verilir. Derleme sırasında mevcut alan `bitis_karesi: 143` olarak SAHNELER'e yazılır; Memmet bunu zaten destekliyor ("Bitir" yuvası [kaynak: memmet.py, H/proje-b2]).
  - `son_kare`: bu planın başlangıç görseli `kaynak_plan`'ın son karesidir ve video dalgası sonrası üretilir.
- `uretim_blogu`: 20'lik gönderim bloğu. **Betik hesaplar**, kimse yazmaz. `parti` alanı hikâye/kurgu partisi (1–3) olarak kalır (§9 C12).
- `plan_imza`: istem, görsel, model ve süre alanlarının özeti. Değişirse video `bayat` olur.
- `is_kimligi` = sha1(plan, tür, istem metni, başlangıç görselinin sha'sı, bitiş görselinin sha'sı, model, çözünürlük, deneme)[:6].

### 5.6 Sağlayıcı arayüzü ve kısıt davranışı
Mevcut `saglayicilar/__init__.py` korunur. Eklenecekler:
```python
TURLER = ("llm", "vlm", "gorsel", "video", "tts", "ses_donustur", "dudak", "muzik")
class Saglayici:
    ad, turler, toplu_mu, kredili
    para_birimi = "flow_kredi" | "ai84_kredi" | "usd" | None
    ortam = "yerel" | "her_ikisi"
    elle = False                   # True: kullanıcı işi gerektirir (gemini_paket, gemini_elle müzik)
    def hazir(self) -> (bool, str)
    def birim_fiyat(self, is_) -> float | None    # None = bilinmiyor → bütçe kapısı BAYRAK
    def bakiye(self) -> float | None               # Flow menüsünden, ai84.credits(); okunamazsa None
class Kisitlandi(Exception):
    kod: "olagandisi"|"dogrulama"|"kredi_bitti"|"arayuz"|"filtre_red"|"anahtar_yok"|"ag"|"kota"|"ortam"
    yeniden_dene: bool     # yalnız ag/kota için True
    plan: int | None
```
Önerilen kayıt (`KAYIT`):

| Tür | Sağlayıcılar (öncelik sırası) | Not |
|---|---|---|
| llm | `claude_code` (varsayılan; iş tanımı yazar, çıkış 3) · `claude_api` (başsız, `claude-opus-5-5`, anahtar `ANTHROPIC_API_KEY` ya da `AYARLAR/anthropic_anahtar.txt`) · `kaset` (testler: kayıtlı yanıtlar) | |
| vlm | `claude_code` · `claude_api` · `gemini_api` · `sahte` | Çapraz model: Gemini üretti → Claude denetler [kaynak: 01 B4] |
| gorsel | `gemini_paket` (elle-toplu) · `flow_gorsel` (Memmet, yalnız düzeltmeler) · `vertex_gorsel` (≈ 0,134 $/görsel [kaynak: 06_SERVISLER]) · `sahte` | |
| video | `flow` (Memmet; `mod: elle\|gece`) · `veo_vertex` (resmî API, $) · `kie` (varsayılan kapalı, §9 Q5) · `sahte`, `sahte_bozuk` (testte hata enjekte eder) | |
| tts | `ai84` · `sahte` | |
| ses_donustur | `openvoice` (yerel) · `rvc` (yerel) · `ai84_vc` (pahalı, yalnız kritik replik) · `sahte` | Karar ses uzmanında |
| dudak | `musetalk` (bulut ya da Colab) · `fal_latentsync` ($) · `sahte` | Wav2Lip yasak (ticari değil [kaynak: 03 A1]) |
| muzik | `acestep` · `gemini_elle` · `sahte` | |

**Kısıt davranış tablosu** (`hat/KISITLAR.md`'ye girer):

| Kod | Örnek | Hattın davranışı | Ders kaydı | Telegram |
|---|---|---|---|---|
| `olagandisi` | Flow "Olağan dışı etkinlikler tespit ettik" | Memmet **o anda** durur. Bekleyen indirmeler yeni gönderimsiz toplanır. O gün Flow'a yeniden başlatma yok [kaynak: H/olagandisi-dur]. İzinli yedek varsa yalnız **sonraki sahne grubundan** itibaren geçilir; yoksa çıkış 7. Ertesi gün öneri: kullanıcı Flow'da **elle 1 video** dener | evet | ACİL |
| `dogrulama` | reCAPTCHA, giriş istendi | Dur (çıkış 2). Çözen kullanıcıdır, devamı kullanıcı `.bat` ile başlatır [kaynak: BILGI_KURALLARI §8 #7] | evet | ACİL |
| `kredi_bitti` | Gönder düğmesi pasif, "yetersiz kredi" | Dur (çıkış 5). Bütçe kapısı yeniden hesaplanır [kaynak: 03_DERSLER] | evet | ACİL |
| `arayuz` | Seçici yok, beklenmeyen sayfa | Dur (çıkış 2). HTML ve PNG kaydı, memmet-bakimci devreye girer. Kör yeniden deneme yok | evet | ACİL |
| `filtre_red` | Politika reddi | **Aynı istem yeniden gönderilmez**; doğrudan yedek istem. Yedek de reddedilirse plan `reddedildi` olur, istem-muhendisi yeniden yazar | evet (kelime adayları) | toplu özet |
| `anahtar_yok` | Boş anahtar dosyası | Sağlayıcı zincirde atlanır (mevcut davranış) | hayır | yalnız gerekiyorsa |
| `ag` / `kota` | Bağlantı koptu, 429 | Üstel bekleme, en çok 3 deneme. Dosya ffprobe ile doğrulanmadan iş "tamam" sayılmaz | evet (3. denemede) | 3. denemede |
| zaman aşımı | Sonuç 360 sn'de gelmedi | Önce **topla** (aynı iş geç bitmiş olabilir). Bulunamazsa 1 yeniden gönderim | evet | hayır |

Yedeğe geçişin şartları (hepsi birden):
1. `FILM_AYAR.json` içinde `video_yedek_izinli` listesinde olmak.
2. `usd` bütçesinin yetmesi.
3. Aynı ya da daha iyi çözünürlük.
4. Sahne grubu sınırında başlamak; bir sahne içinde iki sağlayıcının görünümü karışmaz [tahmin: görünüm farkı ölçülmedi].
5. hat-denetcisi notu.

### 5.7 Kredi defteri, künye, üretim önizlemesi
`KREDI_DEFTERI.jsonl` (yalnız eklenir):
```json
{"zaman":"2026-10-24T01:12:40+03:00","is":"V-142-d1-7f3a9c","plan":142,"tur":"video","saglayici":"flow","model":"omni-1.1-flash","cozunurluk":"720p","klip_sn":8,"deneme":1,"olay":"gonderildi","tahmini":12}
{"zaman":"2026-10-24T01:13:31+03:00","is":"V-142-d1-7f3a9c","olay":"indirildi","dosya":"SIRALI_VIDEO/142.mp4","sure_sn":8.0,"sha":"…","gercek":null}
```
`gercek`: sağlayıcı söylerse doldurulur (Flow menüsündeki kredi farkı, `ai84.tts()` dönüşündeki `credit_cost`).

`KUNYE/142.json`:
```json
{"plan":142,"video":"SIRALI_VIDEO/142.mp4","baslangic":"SIRALI_GORSEL/142.jpg","bitis":"SIRALI_GORSEL/143.jpg",
 "istem_sha":"…","saglayici":"flow","model":"omni-1.1-flash","deneme":1,"is":"V-142-d1-7f3a9c","flow_medya_id":"…",
 "kapilar":{"V1":"GEC","V2":"BAYRAK","K1":"GEC"},"plan_imza":"c0ffee12","bayat":false}
```
`URETIM_ONIZLEME.json`:
```json
{"girdi_imza":"…","kapilar":{"Z0":"GEC","Z1":"GEC","Z2":"GEC","K0":"GEC","S1a":"GEC(8,8,9)","S1b":"GEC","G1":"GEC","S2":"GEC(8,8,8)"},
 "plan":495,"klip":405,"zincir":{"bitis_karesi":88,"son_kare":21,"dalga":2},
 "saglayici_plani":[{"sahne_grubu":"S01-S48","saglayici":"flow","model":"omni-1.1-flash","cozunurluk":"720p"}],
 "kredi":{"flow":{"birim":12,"taban":4860,"pay":0.30,"toplam":6318,"bakiye":9420,"bakiye_kaynagi":"flow_menu","sinir":8478,"sonuc":"GEC"},
          "ai84":{"harf":15600,"bakiye":610000,"sonuc":"GEC"},
          "usd":{"toplam":0.0,"tavan":0.0,"sonuc":"GEC"}},
 "sure_saat":{"flow_gece":12.9,"gece":2},
 "uyarilar":["Bugün Flow'da 0 görsel gönderildi","Son Flow uyarısı 2026-10-19 00:57"],
 "hat_denetcisi":"_RAPOR/HAT_DENETIM_1.md","karar":"GEC"}
```
`sinir` = bakiye × (1 − güvenlik payı 0,10) [tahmin].

### 5.8 Ders defteri (kendi kendine öğrenen; otomatik kayıt biçimi)
**Ham kayıt.** Makine yazar; bir olay bir dosyadır. Bulut ile yerelde git çakışması olmaz.
`KUTUPHANE/DERSLER/ham/20261024-011540_DEMIR_KANAT_V2-142.json`:
```json
{
 "id": "D-20261024-011540-a1b2",
 "zaman": "2026-10-24T01:15:40+03:00", "film": "DEMIR_KANAT", "seri": "DEMIR_KANAT", "ortam": "yerel",
 "olay": "kapi_hatasi",
 "asama": "U03", "kapi": "V2", "madde": "V2.kimlik_kaymasi", "plan": 142,
 "kategori": "yuz_kaymasi",
 "belirti": "SFace 0.29 (kart mara@v2), ilk kareye göre -0.21",
 "olcum": {"sface": 0.29, "esik": 0.363},
 "baglam": {"plan_tipi": "aksiyon", "hareket_tipi": "yörünge", "kadraj": "OY", "referans": ["mara"],
            "isik": "gece", "saglayici": "flow", "model": "omni-1.1-flash", "istem_sha": "…", "zincir": "bitis_karesi"},
 "kanit": ["_RAPOR/V2_P2.json#142", "SIRALI_VIDEO/142.mp4"],
 "eylem": "yeniden_cekim:yedek_istem",
 "sonuc": null,
 "maliyet": {"flow_kredi": 12}
}
```
- `olay` sözlüğü: `kapi_hatasi`, `kapi_bayragi_dogrulandi`, `saglayici_red`, `saglayici_kisit`, `yeniden_cekim`, `kullanici_notu` (notlari_oku'dan), `seyirci_bulgusu` (KRİTİK ve ORTA), `butce_sapmasi`, `arac_hatasi`, `yanlis_alarm`.
- `kategori` sabit sözlüktür (ör. `yuz_kaymasi`, `ters_el`, `nesne_ziplama`, `kaybolma`, `filtre_kelimesi`, `isik_ziplama`, `dudak_kayma`, `bilgi_eksik`, `kurulumsuz_kullanim`, `tempo_uyari`, `arayuz_degisti`). Yeni kategoriyi yalnız ders-katibi ekler.
- **`sonuc` sonradan otomatik dolar.** Aynı planın sonraki denemesi kapıdan geçerse `duzeldi`, geçmezse `duzelmedi`, yönetmen değiştirdiyse `plan_degisti`. Hangi düzeltmenin işe yaradığı böyle ölçülür.
- **Kim yazar:** Her kapı betiği, Memmet, sağlayıcılar, `notlari_oku.py` ve `seyirci_karar.py` ortak `ders_defteri.kaydet(...)` işlevini çağırır. Kayıt yazılamazsa iş durmaz; uyarı loglanır.

**Derleme:** `ders_defteri.py --derle`. `(kategori, baglam anahtarları)` kümeleri çıkarılır: sayı, film sayısı, eylem başarı oranı, maliyet.

**Öğrenilmiş kurallar.** Doğrulayıcılar başlarken `KUTUPHANE/DERSLER/KURALLAR_OGRENILEN.json` dosyasını okur:
```json
{"surum": 7, "kurallar": [
 {"id": "OK-0003", "tur": "filtre_kelimesi", "kapsam": "hareket_istem", "deger": "cradle", "etki": "UYARI→HATA",
  "destek": 4, "karsi": 0, "film_sayisi": 2, "kanit": ["D-…", "D-…"], "durum": "aktif", "tarih": "2026-11-03",
  "gerekce": "4 Flow reddinin 4'ünde istemde 'cradle' vardı; yedek istemle 4/4 geçti", "geri_al": "kelimeyi listeden çıkar"},
 {"id": "OK-0006", "tur": "risk_desen", "kosul": {"hareket_tipi": "yörünge", "plan_tipi": "diyalog"}, "etki": "BAYRAK→HATA"},
 {"id": "OK-0007", "tur": "kredi_payi", "anahtar": "yeniden_pay_oran", "deger": 0.24, "olcum": {"film": 2, "gonderim": 1003, "plan": 809}},
 {"id": "OK-0008", "tur": "tempo", "anahtar": "gece.gonderim_arasi_sn", "deger": [15, 30], "yon": "yavaslat"},
 {"id": "OK-0009", "tur": "esik", "anahtar": "g1.sface_gec", "deger": 0.42, "eski": 0.45,
  "kalibrasyon": {"etiketli_kare": 44, "kacirma": 0.09, "yanlis_alarm": 0.21}}
]}
```
- İzinli `tur` değerleri: `filtre_kelimesi`, `yasak_fiil`, `risk_desen`, `esik`, `tempo` (**yalnız `yavaslat`**), `kredi_payi`, `sure_tahmini`, `istem_kalibi`, `saglayici_notu`.
- **Korkuluklar** (`--uygula` reddeder):
  - `tempo` hızlandırma.
  - Bot, Flow uyarısı, gizli bilgi, onay ya da silme ile ilgili herhangi bir kural.
  - Bir eşiği **gevşeten** değişiklik, etiketli kalibrasyon kanıtı (`kacirma ≤ %10` [kaynak: 02_sureklilik §7]) olmadan.
- **Terfi eşiği** [tahmin]: destek ≥ 3 ve ≥ 2 filmde (ya da tek filmde ≥ 5). Önerilen eylemin başarısı ≥ 2/3.
- **Emeklilik:** karşı kanıt ≥ destek olunca kural `pasif` olur.
- Her kural `kanit` ile ham kayıtlara bağlıdır; izlenebilirlik budur. Kural değişince `surum` artar, doğrulayıcı imzaları değişir, kâğıt kapıları yeniden çalışır.
- İnsan okuması için `KUTUPHANE/DERSLER/DERSLER.md`'ye bir satır eklenir: "Karar — neden — yanlışsa maliyeti" [kaynak: 03 B6].

### 5.9 Kalıcı seri evreni kütüphanesi (yapı; içeriği diğer uzmanlar tanımlar)
```
YZ_FILM/KUTUPHANE/<SERI>/
  evren.json                 dünya kuralları, NE YOK listesi, palet, sabit stil eki, çağ, film listesi
  karakterler/<id>/kimlik.json  + kart_on.jpg, kart_34.jpg, yuz_sface.npy, ses/ornek.wav
  mekanlar/<id>/mekan.json      + kart_*.jpg, kroki, ışık, ambiyans.wav
  nesneler/<id>/nesne.json      + ölçekli referans görsel
  sesler.json                karakter → voice_id, ayarlar, dönüştürücü modeli
  leitmotif.json
  SURUMLER.jsonl             kim, ne zaman, hangi sürüm (yalnız eklenir)
YZ_FILM/KUTUPHANE/DERSLER/   (seriden bağımsız; §5.8)
```
`karakterler/mara/kimlik.json`:
```json
{"id": "mara", "surum": 2, "durum": "onayli",
 "kimlik_dizesi_en": "Mara, an adult huntress with braided auburn hair, a thin scar above her left eyebrow, fur-lined dark leather coat",
 "degismez_capalar": ["braided auburn hair", "scar above left eyebrow"],
 "kostumler": {"k1": {"tarif_en": "fur-lined dark leather coat", "kart": "kart_k1_on.jpg"}},
 "varyantlar": [{"id": "mara@v2+sargili_sag_el", "fark": "bandaged right hand", "ilk_film": "DEMIR_KANAT"}],
 "yuz": {"dosya": "yuz_sface.npy", "model": "face_recognition_sface_2021dec", "kaynak_kart": "kart_on.jpg"},
 "ses": {"saglayici": "ai84", "voice_id": "mrmaApeLxpgZi4RK7oGq", "ses_adi": "Meaghan",
         "tarif_en": "warm, low, calm female voice", "donusturucu": {"tur": "openvoice", "referans": "ses/ornek.wav"}},
 "filmler": ["EMBERFALL_PILOT"]}
```
- Onaylı sürümün üzerine **yazılmaz**. Değişiklik yeni sürüm demektir.
- Film `SAHNELER.json` içinde `karakterler.mara.kutuphane: "EMBERFALL/mara@2"` diye başvurur. `film.py` dosyaları `01_KARAKTERLER/` altına **kopyalar** (Windows'ta sembolik bağ yönetici yetkisi ister).
- Git'e yalnız JSON'lar girer. Görseller, `.npy` ve sesler yerelde kalır ve D'ye yedeklenir. Bulut kimlik dizesiyle çalışır; görsel kapıları yerelde çalışır.

### 5.10 Ayar dosyaları
`AYARLAR/FILM_AYAR.json` gizli değildir ama makineye özeldir. Git'e `FILM_AYAR.ornek.json` girer.
```json
{
 "ortam": "otomatik",
 "mod": "tam_otomatik",
 "saglayicilar": {"llm": ["claude_code"], "vlm": ["claude_code"], "gorsel": ["gemini_paket", "flow_gorsel"],
                  "video": ["flow"], "video_yedek_izinli": [], "tts": ["ai84"],
                  "ses_donustur": ["openvoice"], "dudak": ["musetalk"], "muzik": ["acestep", "gemini_elle"]},
 "flow": {"mod": "elle", "gece_izni": false, "model": "omni-1.1-flash", "cozunurluk": "720p"},
 "butce": {"flow_kredi_tavan_film": null, "ai84_kredi_tavan_film": 60000, "usd_tavan_film": 0, "guvenlik_payi": 0.10},
 "bildirim": {"telegram": true}
}
```
- Varsayılanlar kullanıcıya soru sormadan dürüst çalışır:
  - Flow tavanı `null` = okunan bakiye.
  - Dolar tavanı 0 = ücretli API yedeği kapalı.
  - Gece modu kapalı.
- Bunları açmak bir **kurulum ayarıdır**, film başına soru değildir (§9 Q4, Q9).

`AYARLAR/YOLLAR.json` (kullanıcının mevcut Windows yolları bozulmaz; yollar buradan okunur):
```json
{"yz_film_kok": "C:\\Users\\Soysal\\Desktop\\YZ_FILM", "arsiv": "D:\\YZ_FILM_ARSIV",
 "gemini_paket": "C:\\Users\\Soysal\\Desktop\\GEMINI GORSEL ISTEM", "capcut_taslak": "%LOCALAPPDATA%\\CapCut\\User Data\\Projects\\com.lveditor.draft",
 "openmontage": "C:\\Users\\Soysal\\Desktop\\YZ_FILM\\OpenMontage", "python": "py -3.10"}
```

### 5.11 Bildirim olayları (Telegram)
Ortak `bildirim.py` tek yerdir; Memmet ve `film.py` aynı işlevi çağırır.
- Anahtar `AYARLAR/telegram_bot.txt` dosyasında: 1. satır bot, 2. satır sohbet numarası. Ya da `TELEGRAM_BOT_TOKEN` / `TELEGRAM_CHAT_ID` ortam değişkenleri.
- Mesaja anahtar, yol içindeki kullanıcı adı ya da URL imzası yazılmaz. Gönderilmeden önce maskeleme süzgecinden geçer (test).

| Olay | Seviye | Örnek metin | Tekrar kuralı |
|---|---|---|---|
| `kisit_olagandisi` | ACİL 🚨 | "[DEMIR_KANAT] Flow 'olağan dışı etkinlik' dedi. Memmet durdu, 212/405 video hazır. Bugün yeniden başlatma yok." | Olay başına 1 |
| `dogrulama` | ACİL | "Flow doğrulama istiyor. Memmet penceresinde sen çöz, sonra VIDEO_DEVAM.bat." | 30 dk'da 1 [tahmin] |
| `kullanici_isi` | BİLGİ 🎬 | "Gemini paketi 3/15 hazır: … (GEMINI_AL.bat)" | İş başına 1, 6 saat sonra 1 hatırlatma |
| `butce` | ACİL | "Video için 6.318 kredi gerekiyor, hesapta 4.900 var. Film kısaltılmadı, hat bekliyor." | Olay başına 1 |
| `asama_bitti` | BİLGİ | "Animatik P2 seyirci: 8/8/9 — geçti." | Yalnız önemli aşamalar (K05, V08, U01 dalgası, M04, M06) |
| `gece_ozeti` | BİLGİ | "Gece özeti: 186 klip, 2.232 kredi, 21 yeniden çekim, sıradaki: U03 denetim." | Çalışma başına 1 |
| `hata` | ACİL | "film.py hata verdi (U03). Kayıt: FILM_KAYIT.txt." | 30 dk'da 1 |

- Aynı `(olay, film, asama)` 30 dk içinde ikinci kez gönderilmez. Saatte en çok 12 mesaj gider [tahmin]. Gerekçe: daha önce "Telegram tekrar mesajları" sorun olmuştu [kaynak: H/uretim-hatti-v2].
- Bulutta Telegram varsayılan olarak kapalıdır. Anahtar bulutta yoktur; mesaj yalnız loga yazılır.
- İsteğe bağlı (P3): kayıtlı sohbet numarasından gelen `/durum` ve `/dur` komutları. `/dur` yalnız `DUR` dosyası yazar.

### 5.12 Bulut ↔ yerel iş bölümü ve dosya trafiği
| İş | Bulut (Claude Code web, Linux) | Yerel (Windows, Claude Code masaüstü + Python 3.10) |
|---|---|---|
| K01–K12 kâğıt aşamaları, ajanlar, deterministik kapılar, kredi tahmini | **Evet** | Evet |
| Kod geliştirme, testler (`sahte`, `kaset`) | **Evet** (CI'da Windows/3.10) | Evet |
| Gemini paketlerini hazırlama | Evet (paket klasörü commit edilmez, yerelde yeniden üretilir) | Evet |
| Kart ve görsel alma, G1 ölçümleri, animatik, S2 | Hayır (medya yerelde) | **Evet** |
| Flow ve Memmet, AI84, Vertex, CapCut, Telegram | **Hayır** (çıkış 4) | **Evet** |
| Kurgu, ses, final, yayın, arşiv | Hayır | **Evet** |

- **Taşıma yolu: git.** Kâğıt çıktıları (`00_KONU.md` … `SAHNELER.json`, `DUNYA_DEFTERI.json`, `_RAPOR/*.json`, `_SEYIRCI/`), kütüphane JSON'ları ve ders kayıtları commit edilir.
- **Git'e girmeyenler** (`.gitignore`): `SIRALI_*`, `ANIMATIK/`, `SESLER/`, `KURGU/`, `FINAL/`, `YAYIN/*.mp4`, `GELENLER/`, `_ESKI/`, `FILM_DURUM.json`, `FILM.kilit`, `DUR`, `KREDI_DEFTERI.jsonl` (yerel; D'ye yedeklenir), `AYARLAR/*` (`*.ornek.json` ve `OKU_BENI.txt` hariç).
- Yerelde `GUNCELLE.bat` = `git pull --ff-only`. Yereldeki Claude Code bitirdiği aşamaları commit edip gönderebilir; ancak commit ve push yalnız kullanıcının ayarladığı dalda yapılır.
- Durum dosyalardan türetildiği için (§2.0) iki ortamın `--durum` çıktısı aynıdır.

---

## 6. Yazılması/değişmesi gereken kod (araç adı, ne yapar, girdi/çıktı, öncelik)

### 6.1 Mevcut kodda bulduğum somut sorunlar (önce bunlar)
| # | Yer | Sorun | Neden önemli | Düzeltme |
|---|---|---|---|---|
| S1 | `memmet.py` `DOGRULAMA_KELIMELERI` ve `kontrol_noktasi()` | "olağan dışı etkinlik" ve "unusual activity" **doğrulama** sayılıyor. Memmet 12 saate kadar bekliyor, metin kaybolunca **kendiliğinden devam ediyor** | Kesin kural ihlali: "uyarıda kesin dur, kendiliğinden yeniden başlatma yok" [kaynak: H/olagandisi-dur, 03_DERSLER] | Ayrı `OLAGANDISI_KELIMELERI`. Bulunduğu anda `Durdur(kod="olagandisi")`. reCAPTCHA da durur (§5.6). Çıkış sebebi `_memmet_cikis.json` dosyasına yazılır, böylece `flow.py` kodu okur |
| S2 | `yeni_film.py` → `MEMMET_BASLAT.bat`, `MEMMET_SADECE_VIDEO.bat`; `memmet.py calis()` → `kurgu()` | Memmet doğrudan çalıştırılınca **bütün kapıları atlıyor**. Video kredisi harcıyor, sonra seslendirme ve CapCut zincirini kendisi kuruyor | M3 "kapısız kredi = 0" kodla sağlanmalı | Memmet video aşaması yalnız `--onizleme <imza>` ile çalışır. İmza `URETIM_ONIZLEME.json` ile uyuşmazsa reddeder. Eski `.bat`'lar kaldırılır ya da `film.py`'ye yönlendirilir. `kurgu()` zinciri kaldırılır |
| S3 | `memmet.py` `VARSAYILAN` | `video_cozunurluk: "360p"`. Tempo 4–12 sn, 2–3 partide 5–15 dk | 720p kesin karar [kaynak: BILGI_KURALLARI §8 #1]. 17.10 tempo değerleri [kaynak: §8 #6] | Varsayılan 720p, gece 12–30 sn, aynı anda 2, 8 gönderimde 3–6 dk, 2 blokta 15–30 dk |
| S4 | `memmet.py istemler()` | `[ana, ana, yedek]`: politika reddinden sonra **aynı istem bir kez daha** gönderiliyor | Kredi harcanıp harcanmadığı bilinmiyor (Q2). Gönderim sayısını boşuna artırıyor | `filtre_red` → doğrudan yedek. Aynı istemle ikinci deneme yalnız teknik hatada |
| S5 | `memmet.py asama()` zaman aşımı dalı | Zaman aşımında `kuyruk.append(s)`: sonuç kontrol edilmeden yeniden gönderiliyor | İlk iş geç bitebilir → **çift harcama** | Önce sayfada `kutu_bul` ve `memmet_topla` ile ara; yalnız bulunamazsa 1 yeniden gönderim. `KREDI_DEFTERI`'ne yaz |
| S6 | Depodaki `memmet.py` | Bu sürüm **eski**. Belgelere göre kullanıcının bilgisayarındaki sürüm memmet3: `--mod elle\|gece\|gunduz`, `--tek-tek`, `--yeni-proje`, `flow-prompt-box`, `/asb/` video adresi, "Bitir" yuvası doğrulaması, 720p [kaynak: H/olagandisi-dur, H/proje-b2, 07_OPENMONTAGE]. memmet3 ayrıca gece modunda uyarıda 5 kez sayfa yenileyip **deniyor** | Depodaki sürüme yapılan düzeltme Windows'taki çalışan sürümü ezer. Ya da tam tersi: memmet3 gelirse 5 deneme kuralı geri gelir | **P0, ilk iş:** memmet3 (ve D arşivindeki B2/B3 betikleri) depoya alınır. 5 deneme davranışı silinir. Sonra S1–S5 uygulanır (§9 Q6) |
| S7 | `film.py onay()` | `input()` kullanıyor. Claude Code'un Bash aracında stdin yok → EOF → hep `Durdur` | Ajanla yürütülen hatta kredili aşama hiç geçemez. Ya da `--tam-otomatik` bütün güvenceyi kaldırır | `onay()` kaldırılır. Yerine bütçe kapısı (V09) ve kullanıcının çift tıkladığı `VIDEO_*.bat` gelir |
| S8 | `film.py kaydet()`, `json.dump(open(...,"w"))` her yerde | Atomik değil, kilit yok | Elektrik kesilince durum bozulur; iki süreç aynı anda çalışırsa çift harcama | `atomik_yaz()`, `FILM.kilit`, `DUR` |
| S9 | `film.py imza()` | Aşama düzeyinde imza. Bir planın istemi değişince video yeniden üretilmiyor, yalnız eksik dosyalar üretiliyor | Düzeltilen plan eski videoyla kalır ve sessizce yanlış kurgulanır | Plan bazında `plan_imza` + `bayat` işareti + kuyruk (§5.5) |
| S10 | `ai84.py` başlangıcı | Anahtar yoksa **içe aktarırken `SystemExit`** | Bulutta ya da testte biri `import ai84` derse süreç ölür | Anahtar ilk çağrıda okunur; yoksa `AI84Error("anahtar_yok")` |
| S11 | `istem_denetim.py` | Sabit listeler. 8 sn klipte replik sınırı 20 kelime | ZANAAT: 8 sn'de ≤ 16, 10 sn'de ≤ 20 [kaynak: ritim_esikleri]. Öğrenilen kurallar okunmuyor | Eşikleri `ritim_esikleri.json` ve `KURALLAR_OGRENILEN.json`'dan okur. Raporu §5.4 biçiminde yazar |
| S12 | `yeni_film.py` `.bat`'ları | `python` çağırıyor | Ders: ".bat'lar tam Python310 yolu kullansın" [kaynak: H/uretim-hatti-v2] | `py -3.10`, yoksa `python`. Yol `YOLLAR.json`'dan gelir |
| S13 | `flow.py` | Memmet çıkış kodu 2 → tek tür `Kisitlandi` | Hat olağan dışı uyarıyla "giriş yapılmamış" durumunu ayırt edemiyor | `_memmet_cikis.json` okunur → `Kisitlandi(kod=…)` |

### 6.2 Yeni ya da yeniden yazılacak araçlar (benim alanım; öncelik sırasıyla)
| Öncelik | Araç | Ne yapar | Girdi → Çıktı |
|---|---|---|---|
| P0 | `film.py` v2 | Aşama kaydı (§5.2), `--sonraki --json`, `--calis`, `--dogrula KOD`, `--durum [--kisa] [--json]`, `--asamalar --md`, `--aktif`, `yeni --konu`. Çıkış kodları, zarf ve imza, kilit, DUR, ortam algılama, tur sayaçları, kapı bağlama | film klasörü → `FILM_DURUM.json`, `FILM_KAYIT.txt`, iş tanımı |
| P0 | `ortak.py` | `atomik_yaz`, `imza`, `kilit`, `ortam`, `yollar` (YOLLAR.json), `maskele`, `ffprobe_sure` | — |
| P0 | `saglayicilar/` genişletme | `Kisitlandi.kod`, `birim_fiyat`, `bakiye`, `elle`, `ortam`; yeni türler; `claude_code`, `kaset`, `sahte_bozuk` | — |
| P0 | `kredi.py` | Tahmin (§7), bütçe kapısı B1 ve B2, `URETIM_ONIZLEME.json/.md`, Flow süre tahmini, `KREDI_DEFTERI` yardımcıları | SAHNELER + bakiyeler → önizleme |
| P0 | `bildirim.py` | Telegram + Windows balonu + ses; tekrar engeli, maskeleme, sessiz bulut | olay → mesaj |
| P0 | `ders_defteri.py` | `kaydet()` (her yerden çağrılır), `--derle`, `--uygula` (korkuluklar), `kurallar()` (doğrulayıcılar için) | olaylar → `KUTUPHANE/DERSLER/` |
| P0 | `memmet.py` (memmet3 tabanlı) | S1–S6 düzeltmeleri; `--onizleme`; `KREDI_DEFTERI` yazımı; `_memmet_cikis.json`; Flow kredi bakiyesini ayar menüsünden **salt okuma** [doğrulanmadı: FLOW_KESIF "Kredi bilgisi menünün altında yazar"]; mod `elle` (insan gönderir) ve `gece` (yalnız `gece_izni` varsa) | SAHNELER + görseller → videolar |
| P0 | `memmet_topla.py` | Yeni gönderim yapmadan biten sonuçları indirir; `KREDI_DEFTERI` ile eşleştirir | Flow projesi → SIRALI_VIDEO |
| P1 | `kagit_kapilari.py` | Z0, Z1, Z2 çalıştırıcısı. Kural içeriği zanaat uzmanında; ben çatıyı, rapor biçimini, kuyruk üretimini ve imzayı yazarım | SAHNELER + HIKAYE → `_RAPOR/Z*` |
| P1 | `istem_derle.py` | `eylem_zinciri` → saniyeli `hareket_istem` (ZANAAT §3.7 örneği), kimlik dizesi + stil eki → `gorsel_istem`, `zincir` → `bitis_karesi` | 05_PLANLAR → SAHNELER |
| P1 | `dunya_defteri.py` | Varlık zaman çizelgesi (planlanan / gözlenen), K0 zıplama denetimi | planlar (+ VLM tarifleri) → `DUNYA_DEFTERI.json`, `_RAPOR/K0` |
| P1 | `seyirci_hazirla.py`, `seyirci_karar.py` | Habersiz girdiyi üretir (amaç, risk ve vuruş çıkarılır). 3 raporun medyanı, özet eşleşmesi, ortak sıkılma anları | → `OKUNACAK.md`; raporlar → `_RAPOR/S*` (`puan_oku.py` bunun içine alınır) |
| P1 | `kutuphane.py` | `esle`, `kaydet`, `kopyala`, sürümleme | KART_LISTESI ↔ KUTUPHANE |
| P1 | `gemini_paket.py`, `gemini_al.py` | Paketler (30 sahne, > 10 referansta ZIP), içe alma, 16:9 kırpma (1376×768) [kaynak: H/gemini-ajan-gorsel] | SAHNELER → paket; ZIP → SIRALI_GORSEL |
| P1 | `zincir.py` | Dalga planı (DAG yalnız sıra için, hız için değil [kaynak: 01 B6]), son kare çıkarma (`ffmpeg -sseof -0.1 … -frames:v 1` [kaynak: 02 §2.3]), derinlik denetimi | SAHNELER + videolar → dalgalar, başlangıç kareleri |
| P1 | `animatik.py`, `izleme_paketi.py` v2 | Animatik mp4; üçlü pencereli kare paketi (önceki son kare, 3 kare, sonraki ilk kare) [kaynak: 01 fikir 5] | → `ANIMATIK/`, `_RAPOR/IZLEME_*` |
| P1 | `gorsel_denetim.py`, `video_denetim.py`, `kalite_denetim.py`, `karsilastir.py` | G1, V2, K1, V1 ve final. Ölçüm kuralları görüntü uzmanında; ben çağrı yerini, rapor biçimini ve kuyruğu yazarım | → `_RAPOR/G1,V1,V2,K1` |
| P1 | `saglayicilar/veo_vertex.py` | Resmî Veo API: başlangıç karesi, `last_frame`, `seed`, `duration_seconds`, `resolution` [kaynak: 02 §2.1, google-genai types.py]. Fiyat bilinmiyor → `birim_fiyat` ayardan | — |
| P2 | Kurgu ve ses araçları (`plan_kurgu`, `dudak_denetim`, `diyalog_esitle`, `ses_katmani`, `renk_cila`, `taslak_fark`, `birlestir`, `gemini_muzik`) | İçerik kurgu ve ses uzmanlarında. Hat onlardan zarf, imza ve `ders_defteri.kaydet()` ister | — |
| P2 | Yayın araçları (`jenerik`, `shorts_mp4`, kapak) + `arsivle.py` | Arşiv: `robocopy /E /MOVE`, taşınanların listesi, son taslağın bağlı olduğu dosyaları atla | — |
| P3 | `saglayicilar/claude_api.py` | Başsız mod. `claude-opus-5-5`, yapılandırılmış JSON çıktı (`output_config.format`), sabit şablonlarda istem önbelleği. Üç seyirci için toplu istek (Batches, %50 maliyet) | iş tanımı → aynı çıktı dosyaları |
| P3 | Telegram gelen komutlar, OTIO dışa aktarma, `kie` sağlayıcısı (izin gelirse) | — | — |

### 6.3 Windows ve `.bat` kullanımı
**İlkeler**
- Her `.bat` ASCII ve CRLF kullanır, ilk satırları `chcp 65001` ve `cd /d "%~dp0"` olur. Python çağrısı `py -3.10`, launcher yoksa `python`.
- Türkçe mesajı `.bat` yazmaz, **Python yazar**. `.bat` yalnız çalıştırır ve `pause` ile bekler. Mevcut uygulamada da `.bat` metinleri Türkçe karaktersizdi; böylece kod sayfası sorunu çıkmaz.
- Her `.bat` tek iş yapar. Çift tıklamak güvenlidir: kilit vardır, kaldığı yerden sürer.

**Film klasörü `.bat`'ları** (`yeni_film.py` kurar):
| Dosya | Ne yapar | Kim basar |
|---|---|---|
| `DEVAM.bat` | `film.py <film> --calis`. İnsan ya da ajan işine kadar yürür; Claude yoksa ne yapılacağını yazar | Kullanıcı (isteğe bağlı; Claude da çağırır) |
| `DURUM.bat` | `--durum`: Türkçe tablo ve sıradaki iş | Kullanıcı |
| `DURDUR.bat` | `DUR` dosyasını yazar. Hat ve Memmet elindeki işi bitirip durur | Kullanıcı |
| `GEMINI_AL.bat` | `GELENLER/`'deki ZIP'leri içe alır, sonra `--calis` | Kullanıcı (paketi getirdiğinde) |
| `FLOW_GIRIS.bat` | Memmet Chrome'unda Google girişi (eski `MEMMET_GIRIS.bat`) | Kullanıcı (bir kez) |
| `VIDEO_YARI_OTOMATIK.bat` | U01'i Memmet `--mod elle` ile çalıştırır: Memmet hazırlar, GÖNDER'e kullanıcı basar | Kullanıcı |
| `VIDEO_GECE.bat` | U01'i `--mod gece` ile çalıştırır. Yalnız `gece_izni: true` ise kurulur | Kullanıcı |
| `VIDEO_TOPLA.bat` | `memmet_topla.py`: gönderimsiz toplar | Kullanıcı |
| `NOTLARI_OKU.bat` | CapCut notları → `NOTLARIM` + ders kaydı | Kullanıcı |
| `FILM_DENEME_SAHTE.bat` | Bütün hat sahte sağlayıcılarla (kredisiz) | Kullanıcı |
- Kaldırılanlar: `MEMMET_BASLAT.bat`, `MEMMET_SADECE_GORSEL.bat`, `MEMMET_SADECE_VIDEO.bat`, `CAPCUT_PROJESI_OLUSTUR.bat` (kapı deliği, S2). `KONTROL.bat` elle indirme yolu için kalır.
- Kök klasöre eklenir: `GUNCELLE.bat` (`git pull --ff-only`; git yoksa nasıl kurulacağını yazar) ve `TELEGRAM_TEST.bat`.
- Kullanıcı belgesi: `BASLA_BURADAN.txt` yeniden yazılır. Ana mesajı: "Claude'a konuyu söyle; senden istenen her iş Telegram'a ve ekrana tek cümle olarak gelir; ne zaman hangi `.bat`'a basacağın orada yazar."

**Kurulum** (`kurulum.py` ekleri)
- Paketler: `scenedetect==0.7.2`, `mediapipe` (ana ortamda sürüm görüntü uzmanıyla belirlenir; OpenMontage venv'indeki `0.10.14` sabitine dokunulmaz [kaynak: H/openmontage]), `pyloudnorm`.
- Model dosyaları: opencv_zoo YuNet ve SFace (Apache-2.0 [kaynak: 02 §1.1]).
- İsteğe bağlı paket grupları (`requirements-api.txt`): `anthropic`, `google-genai`.
- Kurulum ayrıca şunları denetler: `git` var mı, `py -3.10` var mı, C'de 20 GB boş yer var mı.

### 6.4 Testler (sahte sağlayıcıyla, ağsız ve kredisiz)
İki örnek film olur. Mevcut `ORNEK_3_SAHNE` geriye uyumluluk için olduğu gibi kalır (eski şema çalışmaya devam etmeli). Yeni `ORNEK_3_SAHNE_TAM` kâğıt çıktılarıyla birlikte gelir; ajan aşamaları `kaset` sağlayıcısının kayıtlı yanıtlarıyla geçer.

| # | Test | Neyi kanıtlar |
|---|---|---|
| T1 | Uçtan uca (`kaset` + `sahte`): K01 → S03 | Bütün aşamalar sırayla, çıkış 0, her çıktıda zarf var |
| T2 | Her aşamanın ortasında kesme (sahte `kes_sonra=N`) | Yeniden çalıştırmada yalnız eksikler yapılır (M5) |
| T3 | `gonderildi` sonrası kesme | Yeniden başlatmada önce toplama yapılır, yeni gönderim 0 (M4) |
| T4 | S2 geçtikten sonra SAHNELER değişir | U01 reddeder (imza uyuşmaz), sağlayıcı çağrısı 0 (M3) |
| T5 | Bakiye < tahmin | Çıkış 5, sağlayıcı çağrısı 0 |
| T6 | `sahte_bozuk` 2. planda `olagandisi` atar | Çıkış 7. İzin yoksa yedek yok; izinli yedek yalnız sonraki sahne grubundan. Telegram taklidine ACİL gider. Ders kaydı yazılır |
| T7 | Aynı anda iki süreç | İkincisi kilitle reddedilir |
| T8 | `DUR` dosyası | Elindeki iş biter, yeni gönderim 0, çıkış 2 |
| T9 | Bulut ortamında kredili sağlayıcı | Çıkış 4 (M11) |
| T10 | Memmet sayfa durumu (HTML fikstürleri: olağan dışı, reCAPTCHA, kredi bitti, değişmiş arayüz) | `sayfa_durumu()` doğru kodu döner; "olağan dışı" görüldükten sonra gönder işlevi çağrılmaz (M8) |
| T11 | Gizli bilgi | Telegram ve log maskelenir. Depoda `AYARLAR/` anahtar dosyaları boş. Anahtar deseni taraması (M13) |
| T12 | Ders defteri | Her olay türü kayıt üretir. `--uygula` tempo hızlandırmayı ve kanıtsız eşik gevşetmeyi reddeder |
| T13 | Kredi hesabı | 405 klip × 12 × 1,3 = 6.318. Süre tahmini formülü |
| T14 | Zincir | Dalgalar doğru. Derinlik > 2 → K0 HATA. Son kare çıkarılıp başlangıç olur |
| T15 | `.bat` biçimi | ASCII, CRLF, `cd /d`. Kodda "Soysal" yolu yok (yalnız `YOLLAR.ornek.json`'da) |
| T16 | `--sonraki --json` sözleşmesi | Her aşama geçerli iş tanımı döner; `kim: kullanici` yalnız izinli listede (M2) |
| T17 | `input()` taraması (AST) | Yalnız `yeni --konu` yolunda (M1) |
| T18 | Yüz kontrolü (model dosyası yoksa atlanır) | `mara.jpg` ↔ `mara` kartı ≥ eşik; `voss.jpg` ↔ `mara` kartı < 0,363 |
- **CI:** GitHub Actions `windows-latest` + Python **3.10** + ffmpeg. Aynı takım `ubuntu` + 3.13'te de koşar. Bulutta 3.10 olmadığı için Windows uyumu ancak böyle kanıtlanır.
- Süre hedefi: T1 ≤ 5 dk, takım ≤ 10 dk.

### 6.5 PR sırası (CLAUDE.md "küçük, anlamlı commit'ler; her büyük parça ayrı PR")
| PR | İçerik |
|---|---|
| 1 | **Güvenlik:** memmet3'ü depoya al; S1–S6, S10, S12, S13; eski `.bat`'ları kaldır |
| 2 | `film.py` v2 çekirdeği + `ortak.py` + sağlayıcı arayüzü + T1–T9, T16, T17 |
| 3 | `kredi.py`, `bildirim.py`, `ders_defteri.py` + T5, T11–T13 |
| 4 | Kâğıt kapıları çatısı, `istem_derle`, `dunya_defteri` (zanaat ve süreklilik uzmanlarıyla) |
| 5 | Kütüphane, Gemini paketleri, G1, seyirci hazırla ve karar |
| 6 | Animatik, izleme paketi v2, zincir, V1/V2/K1, `memmet_topla` |
| 7 | Kurgu ve ses araçları, `veo_vertex` |
| 8 | Yayın, arşiv, `BASLA_BURADAN.txt`, `.bat`'lar |
| 9 | CI, başsız mod, Telegram komutları |

---

## 7. Makinenin denetleyeceği eşikler (kaynağıyla)

Zanaat, süreklilik ve ses eşikleri o uzmanların dosyalarındadır (`ritim_esikleri.json`, `02_sureklilik §6.2`). Aşağıdakiler hattın kendi eşikleridir.
Önerim: hepsi `ritim_esikleri.json` yanında **`hat_esikleri.json`** dosyasında, aynı `{deger, aciklama}` biçiminde durur. Öğrenilen kurallar
(`KURALLAR_OGRENILEN.json`) bu dosyanın değerlerini yalnız korkuluklar içinde ezebilir.

### 7.1 Kredi ve bütçe
| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `fiyat.flow.omni_720p_8sn` | 12 kredi | — | FLOW_KESIF, H/ucuz-erisim (gerçek test) |
| `fiyat.flow.omni_360p_8sn` | 6 | — | aynı |
| `fiyat.flow.lite_720p_8sn` | 5 (kullanılmaz: tek model kuralı) | — | H/ucuz-erisim; tek model: H/olagandisi-dur, 03_DERSLER |
| `fiyat.flow.omni_720p_10sn` | **bilinmiyor** → bütçe kapısı BAYRAK; ilk kullanımda Memmet menüden okur | B | [doğrulanmadı] |
| `fiyat.ai84.tts` | 1 kredi/harf | — | H/ai84-ses-servisi |
| `fiyat.ai84.vc` | ≈ 2.000 kredi/sn | — | H/ai84 (tahmin aracı; servis bakımdaydı) |
| `fiyat.vertex.gorsel` | ≈ 0,134 $/görsel | — | 06_SERVISLER |
| `fiyat.vertex.veo` | **bilinmiyor** | B | — |
| `yeniden_pay_butce` | 0,30 (ilk film); sonra öğrenilen değer | — | [tahmin]: B2 gözlemi ≈ 0,37 [hesap] ile hedef 0,20 [ritim_esikleri] arası |
| `butce.guvenlik_payi` | Bakiyenin %10'u harcanmaz | DUR (5) | [tahmin] |
| `butce.sahne_grubu_butunlugu` | Kalan bakiye bir sahne grubunu bitirmeye yetmiyorsa o grup başlatılmaz | DUR (5) | [tahmin]: yarım sahne, sağlayıcı karışımı riskini doğurur |
| `kredi_tahmin_sapma` | gerçek/tahmin ∉ [0,90; 1,15] → ders kaydı `butce_sapmasi` | B | [tahmin] |
| `ai84_animatik_harf` | ≈ 15.600 harf/geçiş (2.600 kelime × 6) | — | [hesap]; kelime: ZANAAT §2.6 |
| `ai84_vc_tum_film` | ≈ 1.040 sn × 2.000 ≈ 2,1 M kredi > ≈ 649 bin bakiye → **tüm film için kullanılamaz** | — | [hesap]; bakiye: H/ai84 (13.10) |

### 7.2 Flow ve Memmet
| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `flow.olagandisi_tolerans` | 0: ilk uyarıda dur | DUR (7) | H/olagandisi-dur, 03_DERSLER, CLAUDE.md |
| `flow.uyari_sonrasi_ayni_gun` | Yeniden başlatma yok. Ertesi gün önce kullanıcı elle 1 video dener | — | H/olagandisi-dur (17.10 "zorla bugün" kalıcı değildir) |
| `flow.dogrulama` | Dur; devamı kullanıcı başlatır | DUR (2) | BILGI_KURALLARI §8 #7 |
| `flow.model_tek` | Bir filmde tek model (Omni 1.1 Flash) | H (K10) | 03_DERSLER, BILGI_KURALLARI §8 #3 |
| `flow.gece.gonderim_arasi_sn` | 12–30 | — | H/olagandisi-dur 17.10 |
| `flow.gunduz.gonderim_arasi_sn` | 6–15 (yalnız `elle` modda anlamlı) | — | aynı |
| `flow.ayni_anda` | 2 | — | aynı |
| `flow.ara_mola` | Her 8 gönderimde 3–6 dk | — | aynı |
| `flow.blok_mola` | 2 blokta bir 15–30 dk | — | aynı |
| `flow.tempo_yon` | Yalnız yavaşlatılabilir; makine hızlandıramaz | korkuluk | Bot tespitini atlatma yasağı (kesin karar 5) |
| `flow.gorsel_sonrasi_video` | Aynı gün Flow'a > 20 görsel gönderildiyse video o gün başlamaz | DUR (2) | [tahmin]; ders: ~40 görselden sonra hesap işaretlendi [03_DERSLER] |
| `flow.zaman_asimi_sn` | Görsel 180, video 360. Aşılırsa önce topla | — | memmet.py VARSAYILAN |
| `flow.deneme_max` | Plan başına 1 ana + 1 yedek; teknik hatada +1 | — | [tahmin]; S4 |
| `flow.indirme_butunluk` | İndirilen dosya ffprobe süresi ≥ 7,5 sn (8 sn klip) | H → yeniden indir | 02 §6.2 V1; ders: Flow'un kesik indirmeleri [03_DERSLER] |
| `flow.blok_boyu` | 20 plan, mümkünse sahne sınırında | — | CLAUDE_ICIN, YR A9 |

### 7.3 Hat, devam, kapılar
| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `tur_max.kagit_seyirci` | 4 | Çıkış 6 | ritim_esikleri `kagit_tur_max` |
| `tur_max.plan_seyirci`, `tur_max.animatik` | 3, 3 | Çıkış 6 | [tahmin] |
| `tur_max.kurgu_seyirci` | 3 | Çıkış 6 | ritim_esikleri |
| `tur_max.kagit_kapilari` | 3 | Çıkış 6 | [tahmin] |
| `tur_max.g1_duzeltme` | 2 | Yönetmene döner | 01_URETIM_HATTI §5 |
| `tur_max.video_yeniden` | Plan başına 2 | Yönetmene döner | [tahmin] |
| `tur_max.ajan_sema_duzeltme` | 2 (seyircide 0: yeni örnek açılır) | — | [tahmin]; habersizlik ilkesi: ZANAAT §7.3 |
| `seyirci.genel_medyan`, `seyirci.olcut_min`, `KRITIK`, `ozet_eslesme` | 8, 7, 0, 0,8 | Kapı | ritim_esikleri |
| `zincir.derinlik_max` | 2, sonra temiz görselle yeniden demirle | H (K0) | 02 §2.3 (öneri, ölçülmedi) |
| `kilit.bayat_dk` | 30 | — | [tahmin] |
| `disk.c_bos_min_gb` | 20 | DUR (2) | [tahmin]; film başına 5–8 GB [BASLA_BURADAN] |
| `bildirim.tekrar_dk`, `bildirim.saat_max` | 30, 12 | — | [tahmin] |
| `ajan_tur_basina_asama` | 6 | — | [tahmin]; bağlam koruma |
| `animatik.sure_sapma` | ±%5 | B | [tahmin] |
| `hat_denetcisi.yeniden_kuyruk_esigi` | > 30 klip | Ajan çağrılır | [tahmin] |

### 7.4 Ders defteri
| Anahtar | Değer | Kaynak |
|---|---|---|
| `ders.terfi_destek_min` | 3 kayıt ve ≥ 2 film (ya da tek filmde ≥ 5) | [tahmin] |
| `ders.terfi_basari_min` | Önerilen eylemin başarısı ≥ 2/3 | [tahmin] |
| `ders.emeklilik` | Karşı kanıt ≥ destek → `pasif` | [tahmin] |
| `ders.esik_gevsetme` | Yalnız etiketli kalibrasyonla, kaçırma ≤ %10 | 02 §7 |
| `ders.yasak_turler` | Bot, uyarı, gizli bilgi, onay, silme, tempo hızlandırma | Kesin karar 5; CLAUDE.md §Kurallar |

**Kalibrasyon notu.** Yukarıdaki [tahmin] değerleri ilk iki filmde ders defteriyle ayarlanır. Görsel kapı eşikleri için etiketli veri hazır: B3'ün 44 görseli
(21 bozuk) kullanıcının diskinde [kaynak: 02 §7, 05_PROJELER]. Bu set depoya alınmalı; yalnız etiket JSON'u git'e girer.

---

## 8. Kesin kararların (atomik zincir + 6 özellik + ses kararı) kendi alanımda uygulanışı

### 8.1 Karar 1: Kullanıcıya yalnız konu sorulur
- `film.py yeni --konu "…"` tek girişti. Film adını, süreyi, seri kararını ve onay noktalarını ekip verir. Kararlar `KARAR_DEFTERI.md`'ye yazılır.
- Eski onay noktaları (karakter görünüşü, ses, mekân kartı, animatik, yeni sahne [kaynak: BILGI_KURALLARI §8 #17]) `--onayli` modda isteğe bağlı kalır. **Varsayılan `tam_otomatik`'tir.**
- `input()` yalnız `yeni --konu` yolunda bulunur (T17). `onay()` kaldırılır (S7).
- **Karar değil ama kaçınılmaz** el işleri kodda sabit bir listedir (M2):
  1. Google girişi ve reCAPTCHA (yasal zorunluluk; Claude çözmez).
  2. Gemini paket taşıma (yalnız `gemini_paket` seçiliyse).
  3. Video `.bat`'ını başlatma; `elle` modda GÖNDER'e basma.
  4. YouTube yükleme onayı.

  Her biri Telegram'a ve ekrana tek cümle olarak gelir (§5.11).
- Bütçe tavanı, gece izni ve ücretli API izni **kurulum ayarıdır**. Varsayılanlar soru sormadan güvenli çalışır: bakiye kadar Flow, 0 $, gece kapalı (§5.10).

### 8.2 Karar 2: Atomik eylem zinciri
- **Veri:** `eylem_zinciri: [{bas, bit, ozne, fiil, hedef, yon, govde: {el: "sag|sol|iki", parmak: "basparmak+isaret", acik: 2}}]`, `baslangic_durumu` ve `bitis_durumu`. Alanların anlamı ZANAAT §3.7'de; şema yönetmen ve zanaat uzmanlarında.
- **Derleme kodla yapılır.** `hareket_istem` elle yazılmaz. `istem_derle.py` adımları "0-3s: … 3-5.5s: …" biçiminde dizer ve sona tutma cümlesi, `Sound: …` ve `No music.` ekler.
  - Elle yazılmış istem `elle_yazildi: true` ve gerekçeyle işaretlenir. Bu işaret BAYRAK üretir.
  - Böylece "kalemi al" türü bir sonuç fiili istemde görünemez. Z0 #15'teki yasak fiil sayısı 0'dır [kaynak: ritim_esikleri].
- **Kâğıt kapıları (K10):** Z0 #13–16 [kaynak: ZANAAT §6.2]. Benim eklediğim kural: kavrama, bırakma ve verme fiillerinde `govde.el` ve `govde.parmak` zorunludur, eksikse HATA. Karar 2 "hangi el, kaç parmak" diyor.
- **Görüntüde doğrulama:**
  - G1: kör VLM başlangıç karesini tarif eder (kim, hangi üçte birde, hangi elde ne var, bakış). Betik bunu `baslangic_durumu` ile karşılaştırır. Sonuç: **başlangıç durumu = başlangıç karesi**.
  - U03: aynı karşılaştırma klibin son karesiyle `bitis_durumu` arasında yapılır.
  - Sonuç dünya defterinin "gözlenen" sütununa yazılır. Gözlenen bitiş sonraki planın başlangıcıyla çelişirse K1 HATA verir ve kuyruğa üç seçenek girer:
    - (a) Bitiş durumuna klibin ortasında ulaşıldıysa oradan kırp.
    - (b) Yeniden çek.
    - (c) Yönetmen bir bağlayıcı plan ekler.
- **Çelişki:** Karar "klip başına 2–3 adım" diyor. ZANAAT "en çok 3; konuşmalı planda en çok 1; tepki planı tek mikro hareket" diyor. Doğrulayıcı üst sınırı uygular; alt sınır ekip kararına kalır (§9 C4).
- Ders defteri hangi fiil, adım ve kamera birleşimlerinin bozulduğunu sayar. Örnek: "kavrama + konuşma" dudakları bozar [kaynak: ZANAAT §2.3]. Bu bilgi `risk_desen` kuralına dönüşür.

### 8.3 Karar 3: Altı özellik
**(a) Videodan önce animatik + habersiz seyirci.**
- V07–V08. U01'in girdi imzası S2 raporlarının imzasını içerir. Animatik geçmeden video **kodla** başlayamaz (T4).
- Animatikte taslak TTS kullanılır (AI84, ≈ 15.600 harf [hesap]). Bu, gerçek replik sürelerini verir; Z0'daki diyalog süresi formülü gerçek sesle bir kez daha sınanır.
- Seyirci kareleri ve duyulan repliği okur. Ses zevki insan içindir; insan bu hatta sorulmuyor.

**(b) Makinenin tuttuğu dünya durumu defteri + otomatik zıplama denetimi.**
- `DUNYA_DEFTERI.json`'ı **ajan değil betik** kurar (`dunya_defteri.py`), plan alanlarından her çalıştırmada yeniden:
```json
{"surum": 3, "girdi_imza": "…",
 "varliklar": {
  "mara":  {"tur": "karakter", "cizelge": [
     {"plan": 41, "an": "bas", "kaynak": "plan", "sahne_grubu": "S03", "kadraj": "sol_ucte_bir", "poz": "ayakta", "kostum": "k1", "durum": ["yorgun"]},
     {"plan": 41, "an": "bit", "kaynak": "plan", "kadraj": "sol_ucte_bir", "poz": "masa_kenari"},
     {"plan": 41, "an": "bit", "kaynak": "gozlenen", "vlm_tarif": "_RAPOR/V2_P1.json#41", "uyum": true}]},
  "fener": {"tur": "nesne", "cizelge": [
     {"plan": 41, "an": "bas", "kaynak": "plan", "kimde": "mara", "el": "sag", "durum": "yanik"}]}},
 "isik": {"S03": {"ana_kaynak": "fener", "yon": "kadraj_solu", "gun_saati": "gece"}}}
```
- Zıplama kuralları (K0, K1) süreklilik uzmanınındır [kaynak: 02 §6.2]. Benim katkım şunlar: defterin makinede kurulması, "planlanan ve gözlenen" iki sütun, zarf ve imza, HATA'ların kuyruğa ve ders defterine akması.

**(c) Referansla otomatik yüz kontrolü.**
- V03'te kütüphaneye kart yüz gömmesi (`yuz_sface.npy`) bir kez yazılır.
- G1 (görsel) ve V2 (video karelerinde) OpenCV YuNet + SFace ile çalışır: Windows, CPU, Apache-2.0 [kaynak: 02 §1.1].
- Üç bantlı karar: ≥ 0,45 GEÇ · 0,363–0,45 VLM'e · < 0,363 HATA. 0,363 resmî eşik, 0,45 tahmin [kaynak: 02 §6.2].
- İnsan olmayan karakterde DINOv2 + VLM kullanılır.
- Test T18 depodaki `mara.jpg` ve `voss.jpg` ile çalışır. Kalibrasyon B3'ün etiketli 44 görseliyle yapılır.

**(d) Kare zinciri (son kare → sonraki klibin başlangıcı).** Bu özellik video üretimine sıra bağımlılığı getirir. İki yöntem öneriyorum:

| Yöntem | Nasıl | Artı | Eksi | Ne zaman |
|---|---|---|---|---|
| `bitis_karesi` (varsayılan, `devam` geçişlerinde) | N+1'in başlangıç görseli (V05'te `bitis_durumu[N]`'den üretilmiş, G1'den geçmiş) N'nin **bitiş karesi** olarak verilir. Flow "Bitir" yuvası [kaynak: FLOW_KESIF, doğrulandı H/proje-b2]; Veo API `last_frame` (yalnız görselden videoya; `reference_images` ile birlikte kullanılamaz [kaynak: 02 §2.1]) | Paralel: dalga gerekmez. Her iki uç da krediden önce G1'den geçer. Mevcut `bitis_karesi` alanı ve Memmet desteği var | Zorlanan bitiş morf ya da doğal olmayan hareket getirebilir → V2 morf denetimi | Aynı eylem süren, açı aynı ya da yakın |
| `son_kare` (yedek ya da yönetmen seçimi) | N'nin gerçek son karesi (`ffmpeg -sseof -0.1`) N+1'in başlangıç görseli olur. Dalga 2'de üretilir | Fiziksel süreklilik en yüksek | Sıralı (≤ 3 dalga). Her nesilde 720p sıkıştırması birikir → derinlik ≤ 2, sonra temiz görselle yeniden demirleme [kaynak: 02 §2.3] | Karmaşık süren hareket; `bitis_karesi` K1'den geçemezse (DINOv2 < 0,80 [kaynak: 02 §6.2 K1]) |

- `kesme_ayni_mekan` geçişinde fiziksel zincir yoktur. Son kare yalnız K1 ışık ve renk denetiminde ve düzeltme turunda referans olarak kullanılır.
- `yeni_sahne` geçişinde zincir yoktur.
- Dalga planlayıcı (`zincir.py`):
  - Dalga 1 = `son_kare` dışındaki her şey.
  - Dalga k+1 = kaynağı dalga k'de olan `son_kare` planları.
  - DAG yalnız sırayı belirler, gönderim hızını değil [kaynak: 01 B6].
  - Her dalga normal Memmet blokları gibi gider.

**(e) Kendi kendine öğrenen ders defteri.** §5.8: kayıt biçimi, derleme, terfi, emeklilik, korkuluklar. §3.1: `ders-katibi`.
- Döngünün kapanması: doğrulayıcı → kayıt → derleme → kural → doğrulayıcı. Öğrenilen kural bir sonraki çalıştırmada etkili olur; çünkü `KURALLAR_OGRENILEN.json`'un sürümü kapı imzasına girer.
- Kredi payı, süre tahmini ve Flow tempo verisi de buradan öğrenilir. Tempo yalnız yavaşlatma yönünde değişebilir.

**(f) Kalıcı seri evreni kütüphanesi.** §5.9.
- Yeni film aynı seriden başlarsa K02 `evren.json`'u okur; V01 kartları `id@sürüm` ile yeniden kullanır. Aynı kimlik dizesi, aynı yüz gömmesi ve aynı `voice_id` kullanıldığı için filmler arası karakter tutarlılığı makinece korunur.
- Bu, izleyicinin tek büyük eleştirisine ("appearance of the characters keep changing", 803 beğeni) doğrudan cevaptır [kaynak: BILGI_KURALLARI §1.4].

### 8.4 Karar 4: Ses ve dudak uyumu (hattın tarafı; seçim ses uzmanında)
- Hat plan başına `ses.yol` alanını destekler:
  - `veo_donustur`: Veo konuşur → ayrıştırma → sabit karakter sesine dönüştürme.
  - `tts_dudak`: TTS + dudak senkronu.
  - `veo_dogal`: yaratık, kalabalık, ses tarifi yeterli.
  - `ai84_vc`: kritik replik.

  Seçimi ses uzmanı yapar. Hat her yolu sağlayıcı zinciri ve kapılarla yürütür.
- **Otomatik karar ağacı** (M02): klip gelince whisper metni senaryoyla karşılaştırılır.
  - WER eşiğin altındaysa `veo_donustur` yoluna gider.
  - Üstündeyse bir yeniden çekim yapılır (kredi, mini bütçe kapısı).
  - Yine üstündeyse `tts_dudak` yoluna düşer.

  WER eşiği ses uzmanındadır; araştırmada örnek olarak %15 geçiyor [kaynak: 03 öneri 2].
- **Mühendislik verisi** (seçimi etkiler):
  - AI84 Voice Changer tüm film için bütçeye sığmaz (≈ 2,1 M kredi > ≈ 649 bin [hesap]).
  - Kullanıcının kartı 4 GB'tır; LatentSync 1.5 en az 8 GB istiyor, yani yerelde çalışmaz [kaynak: 03 A1]. Dudak senkronu bulut ya da Colab işidir.
  - OpenVoice V2 MIT lisanslı ve hafif, yerelde çalışabilir [kaynak: 03 A2].
  - Mevcut `seslendir.py`'nin yöntemi (TTS'i whisper aralığına `atempo` ile sığdırmak) B2'de "seslerde kayma, dudakla gitmiyor" şikâyetini getirmişti [kaynak: H/proje-b2].
- **Öneri:** Karar fikirle değil **ölçüyle** verilsin. İlk filmin P1'inde 20 replik iki yolla da işlenir: `veo_donustur` ve `tts_dudak`. `dudak_denetim` (SyncNet offset ve güven), WER, LUFS ve S3 seyirci bulguları karşılaştırılır. Sonuç ders defterine `saglayici_notu` olarak girer. Kredi maliyeti yoktur, çünkü aynı klipler kullanılır.

### 8.5 Karar 5: Memmet seri üretim aracı değildir; bot tespiti atlatılmaz
- Memmet'in görevi **doğruluktur**: doğru referans, doğru istem, doğru sahne, sonucun kimlikten tanınması, NNN künyesi, çift harcamanın önlenmesi. Hız onun işi değildir.
- `elle` modu (insan gönderir) kullanıcı başındayken varsayılandır [kaynak: H/olagandisi-dur]. `gece` modu yalnız kurulumda verilmiş `gece_izni` ile açılır, kullanıcının 17.10'da onayladığı yavaş tempoyla çalışır ve makine o tempoyu yalnız yavaşlatabilir.
- Uyarıda durulur (S1), aynı gün yeniden başlatılmaz, rastgele hareketle "insan gibi görünme" eklenmez.
  - Mevcut rastgele bekleme insan taklidi için değil, yük sınırlamak içindir.
  - Bekleme süresi tam rastgele olmak yerine sabit bir aralıkta tutulabilir. Amaç kimliği gizlemek değil, hesabı az kullanmak.
- **Dürüst sonuç:** İnsansız tam otomatik video üretimi için doğru yol **resmî API**'dir (Vertex Veo). Flow aboneliği bir insan arayüzüdür. 40 dk'lık bir filmin ≈ 13 saatlik Flow süresi [hesap], ya `elle` modda kullanıcının başında olmasını ya da açık `gece_izni`ni gerektirir. Bu, kullanıcıya bir kez, kurulumda söylenmelidir (§9 Q9).

### 8.6 Karar 6: Hiçbir iş üstün körü yapılmaz; tasarruf için kaliteden ödün verilmez
- Çözünürlük, model ve plan sayısı **kendiliğinden düşürülmez**. Bütçe yetmezse hat durur (çıkış 5) ve sayıları söyler [kaynak: H/proje-b2 "kalite düşürme yok"].
- Sağlayıcı geçişi yalnız eşit ya da daha iyi çözünürlükle ve sahne grubu sınırında yapılır (§5.6).
- Kapı atlatılamaz:
  - Sağlayıcı çağrısının imzası kapı raporlarını içerir.
  - `--zorla` bayrağı yoktur.
  - Bir kapı tur sınırını aşarsa hat durur. Hiçbir kapı kendiliğinden "geçti" sayılmaz.
- Dolgu yasağı [kaynak: ZANAAT §2.5]: kredi tahmini planlanan klip sayısıyla yapılır, süreyi doldurmak için klip eklenmez.

---

## 9. Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

### 9.1 Riskler
| # | Risk | Olasılık / etki | Önlem |
|---|---|---|---|
| R1 | Depodaki `memmet.py` eski. Kullanıcının bilgisayarındaki memmet3 ile ayrışma var (S6) | Yüksek / yüksek | İlk PR'de memmet3 depoya alınır, fark okunur, güvenlik düzeltmeleri onun üstüne yapılır |
| R2 | "Yalnız konu" kararına rağmen kullanıcıya düşen iş: ≈ 15–17 Gemini paketi taşıma [tahmin: ≈ 440 görsel ÷ 30 + kart paketleri] ve `elle` modda ≈ 8+ saat başında oturma [hesap] | Yüksek / orta | Ücretli seçenekler kurulumda açılabilir: `vertex_gorsel` (≈ 440 × 0,134 ≈ 59 $ [hesap]) ve `veo_vertex` (fiyat bilinmiyor). Varsayılan ücretsiz yol dürüstçe "elle iş var" der |
| R3 | Flow hesabı işaretlenince üretim günlerce durur; tek sağlayıcıya bağımlılık [kaynak: 05_PROJELER: B3 video aşamasında kaldı] | Orta-yüksek / yüksek | Uyarıda dur; ertesi gün elle 1 deneme; izinli yedek sahne grubu sınırında. Yoğun görsel turundan sonra video yok (§7.2) |
| R4 | Sağlayıcılar arası görünüm farkı (Omni ↔ Veo API) | Orta / orta | Geçiş yalnız sahne grubu sınırında; `renk_cila`; ölçüm ilk geçişte [doğrulanmadı] |
| R5 | Claude Code bağlam ve kullanım sınırı: ≈ 90–190 ajan çağrısı [tahmin] | Orta / orta | Durum dosyalarda; SessionStart hook; tur başına ≤ 6 aşama; başsız mod (`claude_api`, Batches %50) |
| R6 | VLM denetiminin maliyeti ve bağlamı (≈ 440 görsel + şüpheli kareler) | Orta / orta | Önce yerel ölçümlerle süz, yalnız BAYRAK'lar VLM'e [kaynak: 02 §5]; 20'lik partiler [tahmin] |
| R7 | Bulut ↔ yerel çakışması (iki ortam aynı dosyayı yazar) | Orta / düşük | Durum dosyalardan türetilir; ders kayıtları tek dosya tek olay; medya ve `FILM_DURUM` git'e girmez; kilit makine adını tutar |
| R8 | Python 3.10 uyumu bulutta sınanamıyor (bulut 3.13) | Yüksek / orta | Windows + 3.10 CI; 3.11+ özellikleri (`tomllib`, `ExceptionGroup`, `datetime.UTC`) yasak |
| R9 | 4 GB GPU: DINOv2 ve torch CPU (~2–3 GB indirme), RVC eğitimi 4 GB'ta belirsiz | Orta / düşük | CPU yolu; RVC isteğe bağlı; ağır işler bulut ya da Colab'a [kaynak: 03 A1, A5] |
| R10 | Kurgu turunda yeni çekimler kredi bütçesini aşar | Orta / orta | U05 mini bütçe kapısı; kâğıt + G1 + S2 kapılarının amacı yeniden çekimi %37'den ≤ %20'ye indirmek |
| R11 | Habersizlik sızıntısı: seyirci ajanının `amac` alanı olan dosyayı okuması | Düşük / yüksek | Seyirci girdisini betik hazırlar (tek dosya); şablonda yasak yollar; her tur yeni örnek |
| R12 | Öğrenilen kuralın yanlış olması ve hattı gereksiz sıkılaştırması | Orta / orta | Terfi eşiği, `geri_al` alanı, emeklilik, sürüm imzası; gevşetme yalnız kalibrasyonla |

### 9.2 Diğer uzmanlarla çakışabilecek noktalar
| # | Konu | Benim önerim | Karşı görüş ya da kaynak |
|---|---|---|---|
| C1 | Yeniden çekim payı | Bütçe kapısında 0,30 (ilk film), sonra öğrenilen değer | `ritim_esikleri.kredi_yeniden_deneme_payi = 0,20`. Önerim: 0,20 **hedef** olarak kalsın, kapıda 0,30 kullanılsın |
| C2 | Bütçe yetmezse | Hat durur; film kendiliğinden kısaltılmaz | ZANAAT §2.6 "film kısaltılır: 30 dk". Kısaltma yaratıcı bir karardır, ekip verir; makine vermez |
| C3 | Rapor klasörünün adı | Mevcut `_RAPOR/` korunur (kod uyumu) | ZANAAT ve 02 `RAPORLAR/` yazıyor. Tek ad seçilmeli |
| C4 | Adım sayısı | Doğrulayıcı en çok 3, konuşmalı planda en çok 1 | Karar metni "klip başına 2–3 adım" diyor. Alt sınır ve tepki planı istisnası ekipçe netleşmeli |
| C5 | Kare zinciri yöntemi | `devam` geçişinde `bitis_karesi` varsayılan, `son_kare` yedek | Görüntü-süreklilik uzmanı her yerde `son_kare` isteyebilir; bu, dalgaları ve süreyi artırır |
| C6 | `parti` alanının anlamı | `parti` = 1–3 hikâye/kurgu partisi; `uretim_blogu` = 20'lik gönderim bloğu, betik hesaplar | Mevcut `istem-muhendisi.md` ve Memmet `parti`'yi 20'lik blok olarak kullanıyor [kaynak: BILGI_KURALLARI §8 #14] |
| C7 | Animatik sesi | Taslak TTS (gerçek süre ölçümü için) | Sessiz animatik de savunulabilir; seyirci zaten metni okuyor |
| C8 | Onay noktaları | Varsayılan ekip kararı; `--onayli` isteğe bağlı | v2 listesi (karakter, ses, mekân, animatik) kullanıcı onaylıydı |
| C9 | Son dışa aktarma | ffmpeg ana kayıt (`FINAL/film.mp4`) + CapCut taslağı (isteğe bağlı düzenleme) | KARARLAR: "kullanıcı CapCut'ta görür, dışa aktarmayı kendisi yapar". 4K 24 fps kararı [kaynak: §8 #8] |
| C10 | Görsel sağlayıcısı varsayılanı | `gemini_paket` (ücretsiz, elle) | Tam otomasyon isteyen `vertex_gorsel` (ücretli) ya da Flow görsel (uyarı riski) önerebilir |
| C11 | Kapı tur sınırı aşılınca | Hat durur, ana Claude durumu raporlar. Ekip bir kez yeni yaklaşım dener (ör. yeni A/B); o da geçmezse insan kararı gerekir | "Yalnız konu sorulur" ile gerilim: tükenmiş kapıda insan kararı kaçınılmaz |
| C12 | Video istem uzunluğu | Saniyeli adım derlemesi istemi uzatır | Ders: "video istemi kısa" [kaynak: 03_DERSLER, H/video-istem-kurali]. Derleme kısa kalmalı: adım cümleleri ≤ 12 kelime [tahmin] |

### 9.3 Açık sorular
| # | Soru | Neden önemli | Nasıl kapanır |
|---|---|---|---|
| Q1 | Flow kredi bakiyesi ayar menüsünden güvenilir okunabiliyor mu? | Bütçe kapısının bakiyesi | Memmet `--kuru` ile tek okuma (gönderim yok) |
| Q2 | Flow politika reddi kredi harcıyor mu? | Yeniden deneme politikası ve tahmin | `KREDI_DEFTERI` + menü bakiyesi farkı |
| Q3 | Omni 720p 10 sn klibin fiyatı? | 20 kelimelik repliklerin maliyeti | İlk kullanımda menüden okunur |
| Q4 | Vertex Veo fiyatı, kullanıcının Google Cloud hesabı ve dolar tavanı | Yedek sağlayıcının açılması | Kurulumda bir kez; yayın ve maliyet uzmanıyla |
| Q5 | kie.ai kullanılabilir mi? | Aracıların ucuzluğunun "gri abonelik havuzundan" geldiği şüphesi var [kaynak: H/ucuz-erisim] | Varsayılan kapalı; kullanıcı kararı gerekir |
| Q6 | memmet3 ve B2/B3 betikleri (`dudak_denetim`, `plan_kurgu`, `izleme_paketi` vb.) depoya nasıl gelecek? | Yeniden yazmak yerine en son çalışan sürümden başlamak | Yereldeki Claude Code oturumu `C:\…\YZ_FILM\ARACLAR` ve `D:\YZ_FILM_ARSIV\PROJE_B2\…\_BOLUM2`'den kopyalar (AYARLAR hariç) |
| Q7 | Windows'ta git kurulu mu? | `GUNCELLE.bat` ve bulut ↔ yerel taşıma | `kurulum.py` denetler; yoksa GitHub Desktop ya da Git for Windows |
| Q8 | YouTube yükleme yapılacak mı (OAuth kurulumu)? | Y06 | Yayın uzmanı; isteğe bağlı ve onaylı |
| Q9 | Gece modu için kalıcı izin verilecek mi, yoksa resmî API mi? | İnsansız üretim; ≈ 13 saat Flow süresi | Kullanıcıya **kurulumda bir kez** dürüstçe sorulur: film başına soru değil, hesap ve maliyet tercihi |
| Q10 | Bulut oturumunda Telegram istenir mi? | Bulut bildirimleri | Ortam sırrı (`TELEGRAM_*`); varsayılan kapalı |
| Q11 | B3'ün 44 etiketli görseli depoya alınabilir mi (yalnız etiket JSON'u + yerel görsel yolu)? | Eşik kalibrasyonu | Yerel oturum |
| Q12 | Claude Code aboneliğinin ajan kullanım sınırı 40 dk'lık filme yetiyor mu? | R5 | İlk filmde ölçülür; başsız mod yedek |

---

### Kısa özet (5 satır)
1. Hat tek bir durum makinesidir: `film.py --sonraki --json` iş tanımı verir, ana Claude ajanları yürütür. Durum çıktı zarflarındaki imzadan türetilir; kilit, DUR dosyası ve atomik yazım var.
2. Sıra şöyledir: kâğıt (K01–K12: hikâye, iki seyirci kapısı, yönetmen, dünya defteri, Z0–Z2) → varlık (kütüphane, kartlar, görsel, G1, animatik + S2) → kesin bütçe kapısı → kredi (dalgalı video, V1/V2/K1) → kurgu → yayın → ders. Kredili işin imzası bütün kapı raporlarını içerir.
3. Sağlayıcı soyutlamasında kısıt kodları vardır. "Olağan dışı" uyarısında hemen durulur, aynı gün yeniden başlatılmaz, yedeğe yalnız izinle ve sahne grubu sınırında geçilir. Mevcut Memmet'te bu kuralı çiğneyen bekle-devam et davranışı ve kapı deliği (`MEMMET_BASLAT.bat`) bulundu.
4. Kare zinciri iki yöntemle kurulur: `bitis_karesi` paraleldir ve varsayılandır; `son_kare` en çok 3 dalgadır ve yedektir. Ders defterinde her olay tek bir JSON dosyasıdır; kurallar kanıt eşiğiyle terfi eder ve güvenliği asla gevşetmez.
5. 40 dk film ≈ 6.318 kredi (%30 payla) ve ≈ 13 saat Flow süresi gerektirir [hesap]. Testler sahte ve kaset sağlayıcılarla 18 senaryodur; Windows + Python 3.10 CI şarttır.
