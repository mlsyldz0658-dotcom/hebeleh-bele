# TASARIM — YZ Film Seti: konudan yayına tek tasarım

> **Durum:** tamamlandı; uygulanacak karar belgesi. **Tarih:** 23.10.2026. **Hazırlayan:** sentez yazarı ve baş tasarımcı (Claude Opus 5.5).
> **Kaynaklar:** `tartisma/tur1_*.md` (7), `tur2_*.md` (7), `elestiri_seyirci_yapimci.md`, `elestiri_seytanin_avukati.md`; eğitim belgeleri
> (`BILGI_KURALLARI.md`, `ZANAAT.md`, `ritim_esikleri.json`, `arastirma/01–03`, `FILMLE ILGILI CLAUDE/00–07`, `YZ_FILM/BILGI/*`) ve mevcut kod.
> **Bu belge tur 3'ün yerine geçer ve karardır.** Uzman belgeleriyle çeliştiği her yerde bu belge geçerlidir; uzman belgelerine yalnız ayrıntı
> (tablo, örnek) için başvurulur ve bu belgede "aynen alınır" denen yerler oradan alınır.
>
> **Kısaltmalar:** [CM2] Claude Code mimarisi · [UM2] üretim mühendisi · [SN2] senarist · [YN2] yönetmen · [GS2] görüntü-süreklilik ·
> [SM2] ses-müzik · [KU2] kurgucu (hepsi tur 2) · [ESY] seyirci-yapımcı eleştirisi (EK = KRİTİK, EO = ORTA) · [SA] şeytanın avukatı
> (K = KRİTİK, O = ORTA, S = KÜÇÜK) · ZN `ZANAAT.md` · RE `ritim_esikleri.json` · BK `BILGI_KURALLARI.md` · DR `03_DERSLER.md`.
>
> **Sayı etiketleri:** kaynağı olan sayının yanında kaynağı yazar · **(tahmin)** kaynağı yok, ilk filmde ölçülüp ders defteriyle ayarlanır ·
> **(hesap)** kaynaktaki sayılardan türetildi · **(doğrulanacak)** Claude Code ya da dış servis davranışı, Ö0 ölçüm turunda bir kez sınanır.
>
> **Yer adları:** `<depo>` = depo kökü (Windows'ta `C:\Users\Soysal\Desktop\YZ_FILM_SET`), `<veri>` = veri kökü (Windows'ta
> `C:\Users\Soysal\Desktop\YZ_FILM`, yeri değişmez), `<film>` = `<veri>/FILMLER/<FILM_ADI>/`, `<evren>` = `<veri>/EVREN/<SERI>/`.
> Araçlar `<depo>/YZ_FILM/ARACLAR/` altındadır. Bütün yollar kodda `YOLLAR.json`'dan okunur.

## 0. Kısa özet

Kullanıcıya, sade Türkçe:

1. Sen yalnız filmin konusunu bir cümleyle söylersin. Senaryo, oyuncu sesleri, müzik ve kurgu dahil bütün kararları ekip verir; sana karar sorusu sorulmaz.
2. Önce her şey kâğıtta yapılır ve kredi harcanmaz: hikâye odası senaryoyu yazar, filmi hiç bilmeyen üç "seyirci" okur, puan 8/10'a yaklaşana kadar düzeltilir.
3. Yönetmen her planı saniye saniye, elle ve yönle yazar ("sağ elini kaleme uzatır, başparmak ve işaret parmağıyla kavrar"). Bilgisayar kimin elinde ne olduğunu bir defterde tutar ve zıplamaları yakalar.
4. Karakter kartları ve her planın başlangıç görseli üretilir. Her görsel karakterin kartıyla ölçülür ve beklentiyi bilmeyen bir gözlemciye tarif ettirilir.
5. Videoya geçmeden önce film, durağan karelerle ve gerçek seslerle bir "animatik" olarak seyircilere izletilir; kopukluklar kredisiz düzeltilir.
6. Sonra filmin ilk 3 dakikası yayın kalitesinde bitirilir ve sana bilgi olarak gönderilir. Kalan videolar bundan sonra çekilir.
7. Senin işin yalnız fiziksel işlerdir: Flow'a giriş, bazı görsel paketlerini Gemini'ye taşımak, video oturumlarında GÖNDER'e basmak, CapCut'tan dışa aktarmak. Sayıları baştan "kullanıcı sözleşmesi" kartında yazar.
8. Flow "olağan dışı etkinlik" ya da doğrulama gösterirse sistem hemen durur ve sana haber verir. Asla atlatmaz, hızlandırmaz, başka hesaba geçmez.
9. Karakterin sesi filmden filme aynı kalır: Veo konuşur, ses karakterin kalıcı sesine çevrilir, dudak bozulmaz. Ağzı görünmeyen repliklerde aynı ses doğrudan okunur.
10. Sonunda CapCut taslağı, kapak, YouTube metinleri, fragman ve 3 Short hazır olur; yükleme yalnız sen istersen yapılır. İlk kurulumda sistem birkaç gün kendi ölçümünü yapar; her filmden ders çıkarır ve bir sonrakinde aynı hatayı tekrarlamamaya çalışır.

## 1. Akış

### 1.1 Yürütme modeli (bütün aşamalar için)
- **Tek protokol: görev defteri** ([CM2]). Ana Claude yalnız "set amiri"dir: `film.py sonraki` → `film.py basla <id,…>` → görevin türüne göre
  ajanı açar (aynı paralel gruptaki en çok 5 ajan tek mesajda), betiği çalıştırır (`film.py calis <id>`) ya da kullanıcı eylemini aynen iletir → bitti
  kararını **SubagentStop kancası** (`kanca.py ajan_bitti`) verir → döngü başa döner. Ana Claude içerik üretmez, puan vermez, ajan çıktısını
  düzeltmez, plan ya da rapor dosyası yazmaz.
- **Görev klasörü:** `<film>/_GOREV/<id>/{GOREV.json, ISTEM.md, GIRDI/, CIKTI/}`. Ajan yalnız kendi görev klasörünü okur ve yalnız `CIKTI/`'ya yazar
  (`kanca.py erisim`). Betik `CIKTI/`'yı doğrular ve sahibi olduğu yere taşır.
- **Çıkış kodları** ([UM2]): `0` BİTTİ · `1` HATA · `2` KULLANICI (fiziksel iş) · `3` AJAN (ajan görevi var) · `4` ORTAM (bu ortamda yapılamaz) ·
  `5` BÜTÇE · `6` KAPI (tur tavanı doldu) · `7` KISIT (Flow uyarısı, hesap kilidi) · `8` BEKLE (mola, GPU, kullanım sınırı, bekleme süresi).
- **Nerede:** Üretim **yalnız kullanıcının Windows bilgisayarında** yürür (§2.1 D-12). Bulut oturumları yalnız geliştirme içindir; orada bütün
  aşamalar `sahte` ve `kaset` sağlayıcılarıyla, ağsız ve kredisiz test edilir. Aşağıdaki tabloda "yerel" sütunu üretim yerini, "bulutta test"
  sütunu otomatik testin bulutta koşup koşmadığını gösterir.
- **İmza:** her aşama çıktısı `_uretim {asama, gorev, girdi_imza, arac_surum, esik_surum, sonuc, zaman, ortam}` zarfını taşır. Aşama "tamam" =
  çıktı var + girdi imzası eşit + kapı GEÇ. Kredili çıktı asla silinmez; girdi değişirse `bayat` işaretlenir ve kuyruğa girer.

### 1.2 Ölçüm turu Ö0 (sistem düzeyi; bir kez, ilk filmden önce başlar)
Ö0, tasarımın ölçülmemiş temellerini ([SA] K-1, K-3, K-4) kod yığılmadan önce ölçer. Ö0-a geliştirme oturumunda yapılır; Ö0-b…h `film.py`'nin
sistem görevleridir ve ilk filmin kâğıt aşamalarıyla (A00–A09) **paralel** yürür. Sonuçlar `<veri>/BILGI/OLCUM0/O0<harf>.json` +
`OLCUM0.json` (her deneme: ölçüm, karar, gerekçe) dosyalarına yazılır; bu belgede "Ö0 ölçer" denen her karar bu dosyadan okunur.

| No | Deneme | Kim | Girdi | Çıktı | Geçme şartı (karar kuralı) | Üst sınır | Kredi | Yer |
|---|---|---|---|---|---|---|---|---|
| Ö0-a | Claude Code davranışları (§10.3'teki 15 madde) | geliştirici Claude, `olcum0/kanca_deneme/` | deneme kancaları | `O0a.json` | Her davranış "çalışıyor / çalışmıyor + seçilen yedek" ile kapanır. Kanca nabzı ve erişim kancası çalışmıyorsa PR-3 birleştirilmez | 1 tur | yok | yerel |
| Ö0-b | Flow/Omni: günlük uyarısız kapasite; `aralik` ve `sira` istem biçiminde adım tutma (V3); "holds still" ↔ "holds the pose, breathing"; 720p üretim süresi; politika reddinin kredi yakıp yakmadığı; 1280×720 son kare zinciri karesinin kalitesi; eylem kesmede önceki son karenin **görsel referansı** | `olcum0/flow_deneme.py` + Memmet (`elle`) + kullanıcı (GÖNDER) | B3'ün G1'den geçmiş P1 kareleri (PA: 44 kare, 2 tur denetim) ve bunlardan atomik istemler | `O0b.json` | 3 **ayrı** günde, günde ≤ 20 video (ölçüm tavanı, tahmin), 17.10 temposu; ilk uyarıda o günün ölçümü biter. Ölçülen değer günlük uyarısız kapasitenin **alt sınırıdır** (`olculen_gunluk_kapasite`, en çok 20); takvim bununla hesaplanır. Bir gün bile 20'ye uyarısız ulaşılamadıysa ilk film 30 dk. V3 tutma < %60 → adım sayısı 2'ye iner, `bitis_sabit` payı artar (tahmin eşiği) | 3 gün; toplam ≤ 40 klip | evet, ≤ 480 kr (tahmin tavanı; B3'ün kendi planları) | yerel |
| Ö0-c | Ses: arşiv Veo kliplerinde OpenVoice V2 ve Chatterbox dönüşümü (RVC yalnız koşullar okununca); MuseTalk 1.5 kurulumu + 1 klip; ACE-Step 1.5 ipucu süresi; büyütücü (Real-ESRGAN türü) 8 sn klip süresi | `olcum0/ses_deneme.py` | B2/B3 arşiv klipleri | `O0c.json` | S1.11 eşiklerini geçen motor varsa ana yol `veo_donustur`; yoksa §2.2 B planı. Büyütme 1 saatlik içerik için > 12 saat (tahmin) ise 1080p + gren yolu | 1 | AI84 ≈ 2–5 bin (tahmin) | yerel |
| Ö0-d | CapCut: `pycapcut` ile taslak okuma, klon, segment taşıma; taslak şifrelemesi | `olcum0/capcut_deneme.py` + kullanıcı (CapCut'ı kapatıp açar) | 1 dk'lık deneme taslağı | `O0d.json` | Şifreliyse ya da klon çalışmıyorsa `yayin_kaynagi: master` ve not yolu "yeni adla kur" | 1 | yok | yerel |
| Ö0-e | Gemini: 1 paket (30 plan, plan başına 2 ve 3 aday); Gemini API (AI Studio) görsel kotası ve fiyatı | `gemini_paket.py` + kullanıcı (1 paket) | B3 planları | `O0e.json` | API kotası yeterli ve ücret 0 ise (ya da kullanıcı dolar izni verdiyse) paketler API'ye geçer; değilse paket sayısı kesinleşir | 1 | yok / küçük $ | yerel |
| Ö0-f | Claude kullanımı: 1 kâğıt turu (3 seyirci + eşleştirici) ve 1 `kare-tarifcisi` görevinde gerçek token; seyirci gürültüsü (aynı metin 5 seyirciye 2 kez: B2 P1 v11 ve B3 kâğıdı); "karar 6 testi" (aynı etiketli sette daha ucuz model/effort ↔ Opus·high) | betik + ajanlar | B2/B3 metinleri, 44 kare | `O0f.json` | `seyirci_gurultu_std` yazılır; ucuz yapılandırma ancak fark gürültü bandının içindeyse ve karar defterine yazılarak seçilir | 1 | abonelik | yerel |
| Ö0-g | Kanal teşhisi: B1/B2 gösterim, tıklama oranı, ortalama izleme, tutma eğrisi, trafik kaynağı | `kanal_teshis.py` (YouTube OAuth varsa API, yoksa kullanıcının isteğe bağlı CSV'si) | YouTube verisi | `<veri>/BILGI/KANAL_TESHIS.md` | Veri yoksa "ölçülemedi" yazılır; film başlamasını engellemez | 1 | yok | yerel |
| Ö0-h | Kalibrasyon seti: B3'ün 44 karesinin etiket JSON'u (kayıtlı denetim raporlarından; eksikler `kare-tarifcisi` + `sureklilik-denetcisi` ile) | betik + ajanlar | B3 kareleri ve raporları | `YZ_FILM/ARACLAR/veri/kalibrasyon/B3_44.json` (yalnız etiket; görseller yerelde) | 44 kare × alan etiketleri tam | 1 | yok | yerel |

**Ö0 sırası:** PR-0 (güvenlik yaması, §9) → Ö0-a → film.py çekirdeği → Ö0-b…h ilk filmin kâğıt aşamalarıyla paralel. A01'de (B0) Ö0-b sonucu
yoksa film **1800 sn** (30 dk) hedefle yazılır; varsa süre bütçe + ölçülen kapasite + takvimle seçilir (§2.1 D-05).

### 1.3 Film akışı (A00–A18)
"Döngü üst sınırı" sütunundaki tur sayıları ayrıca §1.5'teki küresel geri dönüş bütçesine tabidir. "Kapı" ve "hedef" ayrımı §1.4'tedir.

| No | Aşama | Kim (ajan · betik · kullanıcı) | Girdi | Çıktı dosyası | Geçme şartı | Döngü üst sınırı | Kredi | Nerede (bulutta test) |
|---|---|---|---|---|---|---|---|---|
| A00 | Hazırlık ve konu | ana Claude tek soruyu sorar (aktif film yoksa; metin §4.1); betik `film.py yeni --konu "<cümle>"` | kullanıcının cümlesi | `<film>/00_KONU.md`, `HAZIRLIK.json` (sürüm, kanca nabzı, disk, kurulum kademesi) | Kanca nabzı ≤ 15 sn; K1 kurulum tamam; disk ≥ `disk_bos_min_gb` | — | yok | yerel (evet) |
| A01 | Konu kartı ve süre (B0) | `yapimci·konu`; betik `hikaye_odasi.py konu-denetim`, `kredi.py b0` | `00_KONU.md`, evren özeti, `OLCUM0.json`, bakiye | `_HIKAYE_ODASI/01_KONU_KARTI.json`, `01_VARSAYIMLAR.md`, `PROJE_KARARLARI.md`, `_RAPOR/B0_FILM.json` | konu-denetim HATA 0; süre ∈ [1800, 2700] (Ö0-b yoksa 1800); kullanıcıya 3 satır bilgi | SubagentStop düzeltme ≤ 2 | yok | yerel (evet) |
| A02 | Brifing | betik `hikaye_odasi.py brifing` | konu kartı, aktif hikâye dersleri, RE | `_HIKAYE_ODASI/00_BRIFING.md` (sha1 kaydı) | 7 bölüm, 1.500–4.000 kelime | — | yok | yerel (evet) |
| A03 | Dört öneri | `hikaye-mimari` × 3 (eksen D/S/E, paralel) + 1 (X; yalnız loglineları "kaçınılacak yol" olarak görür) | brifing | `_HIKAYE_ODASI/02_oneri_<eksen>.md` | `oneri-denetim`: 10 başlık, başlık ≤ 100 kr, konuşan ≤ 8, filtre, çeşitlilik dörtlüsü | BENZER çıkarsa yeni eksenle 1 kez | yok | yerel (evet) |
| A04 | Kör jüri ve seçim | `juri-uyesi` × 4 rol + `uretilebilirlik-denetcisi·juri`; betik `juri-topla` | anonim öneriler | `03_juri_<rol>.json`, `04_SECIM.json`, `04_KULLANICIYA_OZET.md` (bilgi) | Kazanan ≥ 8,0 (hedef); veto yok | Kazanan < 8,0 → yazar 1 kez yeniden + jüri | yok | yerel (evet) |
| A05 | Yapı ve senaryo | `hikaye-yazari·yapi`, `·senaryo`; `oyuncu` × ana karakter (≤ 8); `diyalog-editoru`; betik `yapi-denetim`, `senaryo-denetim` | `04_SECIM.json`, kazanan öneri | `05_YAPI.json`, `06_SENARYO_v<N>.json`, `_RAPOR/HIKAYE_Z_v<N>.json` | yapi-denetim ve senaryo-denetim HATA 0 (Z1/Z2 hikâye ölçüleri, filtre, NE YOK, bilgi durumu, ilk replik ekranda) | SubagentStop ≤ 2; HATA dönüşleri kâğıt turuna sayılmaz | yok | yerel (evet) |
| A06 | Kâğıt seyirci, ilk 2 dk, kilit | `habersiz-seyirci·kagit` × 3 (aşamalı P0→P3), `·ilk2dk` × 3 × 2 sürüm (A/B), `ozet-eslestirici·ozet/bulgu` × 3; betik `seyirci_topla`, `bulgu_yonlendir`; tıkanırsa `yapimci·doktor`; revizyon `hikaye-yazari·revizyon`; betik `devir` (kilit) | senaryonun EKRAN bloğu (`kor_paket --kip kagit`) | `_RAPOR/HS_KAGIT_FILM_t<n>.json`, `HS_ILK2DK_FILM.json`, `HIKAYE.json` + `HIKAYE.md` (kilit), `evren.py on-kayit` | **Kapı:** §1.4 · **Hedef:** GENEL ≥ 8, ölçüt ≥ 7, ORTA ≤ 3/parti, ilk 2 dk 3/3, bütün olgular ≥ 0,80 | 4 tur + doktor 2 yapısal tur + ikinci öneriyle 4 tur (≤ 10); plato kuralı §1.4; ilk 2 dk A/B + 1 üçüncü sürüm (≤ 2 tur) | yok | yerel (evet) |
| A06s | Ses kadrosu (kâğıt) | `ses-tasarimcisi·kadro`; betik `ses_plani.py --profil-denetle` | `HIKAYE.json` (ses_karakteri, ad_telaffuz), evren ses kayıtları | `_SES/SES_PROFILLERI.json`, `_SES/SES_KADROSU.md` | profil denetimi HATA 0 (`veo_ses_tarifi` ≤ 12 kelime, aksan, yaş/filtre sözcüğü yok) | SubagentStop ≤ 2 | yok | yerel (evet) |
| A07a | Harita, kroki, kart tarifleri | `yonetmen·harita` × 3 parti (betik `kroki.py --karsilikli` önerilerini önce GIRDI'ye koyar) ∥ `kart-tasarimcisi` | `HIKAYE.json`, evren mekânları | `_YONETMEN/HARITA_P<n>.json`, `<evren>/mekanlar/<id>/kroki.json` (yeni sürüm), `_YONETMEN/KART_ISTEGI.json`, `_KARTLAR/KART_SPEC.json` | `plan_denetim --harita`, `kroki.py --denetle`, `evren.py --spec-dogrula` HATA 0 | SubagentStop ≤ 2; kart tarifi revizyonu ≤ 2 | yok | yerel (evet) |
| A07b | Sahne grubu planları | `yonetmen·plan` × sahne grubu (≈ 45–55 görev, paralel ≤ 5) | sözleşme, kroki PNG + kurulumlar, EKRAN metni + replik kimlikleri, önceki sahnenin son 2 planının çözülmüş bitişi, `PLAN_DILI.md`, sözlükler, GIRDI/DERSLER.md | `_YONETMEN/PLANLAR/S<k>.json` | `plan_sema` + `plan_denetim --sahne` + `kroki.py --sahne` HATA 0 (kancada) | SubagentStop ≤ 2, sonra o partinin harita revizyonu 1 kez | yok | yerel (evet) |
| A07c | Birleştirme, K0, T0, B1 | betik `plan_birlestir`, `dunya_defteri --derle --denetle`, `kroki --tum`, `plan_denetim --tum`, `zaman_cizelgesi --asama kagit`, `kredi.py b1`, `olcek.py` | planlar | `SAHNELER.json`, `DUNYA_DEFTERI.json`, `_RAPOR/K0_FILM.json`, `_RAPOR/Z0_P<n>.json`, `KURGU/surumler/KURGU_PLANI_T0.json`, `URETIM_ONIZLEME.json` (taslak) | K0 ve Z0 HATA 0; B1: tahmin ≤ tavan (aşılırsa 5 BÜTÇE; yazılmış film kısaltılmaz) | HATA → `KUYRUK/YENIDEN_YAZ.json` → aynı sahnenin yönetmeni (≤ 2) | yok | yerel (evet) |
| A07d | Kâğıt plan eleştirisi | `plan-elestirmeni` × 3 ∥ `uretilebilirlik-denetcisi·plan` × 3 ∥ `sureklilik-denetcisi·kagit` × 3 (parti başına) | `CEKIM_LISTESI_P<n>.md`, K0 BAYRAK'ları | `_RAPOR/PLAN_ELESTIRI_P<n>_t<n>.json`, `URET_PLAN_P<n>`, `K0_HAKEM.md` | KRİTİK 0; ORTA ≤ 3/parti | 2 tur | yok | yerel (evet) |
| A07e | Plan seyircisi (ilk iki filmde; değeri ölçülür) | `habersiz-seyirci·plan` × 3/parti | `kor_paket --kip plan` | `_RAPOR/HS_PLAN_P<n>_t<n>.json` | §1.4 kapı politikası | 2 tur | yok | yerel (evet) |
| A08 | Ses tasarımı ve müzik planı | betik `ses_plani --taslak`; `ses-tasarimcisi·tasarim` × sahne grubu, `·muzik`; betik `muzik.py --kagit`, `ses_plani --denetle --tum` | `SAHNELER.json`, `DUNYA_DEFTERI.json`, evren | `_SES/SES_<S>.json`, `_SES/SES_TASARIMI.md`, `MUZIK/muzik_listesi.json`, `<evren>/muzik/leitmotifler.json`, `_RAPOR/S0_FILM.json` | S0 HATA 0 | SubagentStop ≤ 2 | yok | yerel (evet) |
| A09 | İstem derleme ve kâğıt sonu | betik `istem_derle --hareket`, `istem_denetim`, `kamera_agaci` | `SAHNELER.json` (zanaat + ses) | `SAHNELER.json → hareket_istem`, `KAMERA_AGACI.json`, `_RAPOR/ISTEM_FILM.json`, `KAGIT_TAMAM.json` | ISTEM HATA 0; elle istem ≤ %5 | yonetmen·onarim ≤ 2 | yok | yerel (evet) |
| A10a | Yerel kurulum ölçümü | betik `kurulum.py --dogrula`, `ses_olcum --kontrol` | — | `_RAPOR/KURULUM_FILM.json` | K1 tam; eksik K2/K3 ortamı yalnız kendi basamağını kapatır | — | yok | yerel (hayır) |
| A10b | Telaffuz testi (yerelin ilk işi) | betik `ses_sec.py --telaffuz` | uydurma adlar | `_RAPOR/S1a_telaffuz.json` | ad hatası 0; geçmeyen ad `hikaye-yazari·dar_degisiklik` (H15) | ad başına 1 değişiklik | AI84 ≈ 1,8 bin (tahmin) | yerel (sahte) |
| A10c | Ses seçimi, motor kıyası, efekt | betik `ses_sec.py --ara/--olc/--oku/--puanla/--sec`; puan farkı < 0,03 ise `ses-tasarimcisi·kadro`; seri başında `ses_kiyas.py`; `ses_kutuphanesi.py --dizinle --eksik` | profiller | `<evren>/karakterler/<id>/ses.json`, `SES_SECIM.html` (bilgi), `_RAPOR/S1*.json` | S1 HATA 0 | — | AI84 ≈ 5 bin; seri kurulumu tavanı 40 bin | yerel (sahte) |
| A10d | Kartlar | betik `istem_derle --kart` → `gemini_paket --kartlar` (kullanıcı taşır) → `gemini_al`; `kart_denetim` + `kare-tarifcisi·kart` + `kare_denetim --karar`; `yonetmen·kart_secimi`; `evren.py --kilitle` | `KART_SPEC.json` | `<evren>` kart sayfaları (kilitli), `_RAPOR/KART_KAPISI.json`, `_KARTLAR/KART_SECIM.json` | KART HATA 0 | 2 CORRECTION turu; sonra tarif revizyonu ≤ 2; sonra en iyi teknik aday + BAYRAK | yok (düzeltme görseli Flow'da 0 kr; günlük tavan) | yerel (sahte) |
| A11 | Başlangıç görselleri, G1 ilk geçiş, kapak adayları | betik `istem_derle --gorsel`, `kamera_agaci` basamakları, `gemini_paket --basamak k --aday 2` → `gemini_al`; `olcum` yerel ölçüm → `kare-tarifcisi·g1` (≤ 12 görsel/görev) → `kare_denetim --karar` → `sureklilik-denetcisi·hakem` (yalnız tek kaynaklı BAYRAK / ÖLÇÜLEMEDİ); kapak 8–12 aday + `kare-tarifcisi·kapak` + `habersiz-seyirci·kapak` (ikili) | `SAHNELER.json`, kilitli kartlar | `SIRALI_GORSEL/_ADAYLAR/`, `SIRALI_GORSEL/NNN.jpg` (yalnız G1 GEÇ), `_RAPOR/G1_P<n>_B<k>.json`, `KUYRUK/YENIDEN_URET.json` (G1 maddeleri), `YAYIN/KAPAK_SPEC.json` | İlk geçiş bütün planlarda bitti; kimlik HATA'sı yüzünden yer tutucu ≤ %15 (değilse yalnız kimlik maddeleri için 1 düzeltme turu). **Düzeltme turları A12 tur 1'den sonra** (§2.1 D-14). Sıra: önce P1'in ilk geçişi → **KR3a** P1 animatik ön turu (kapı değil; dersleri P2/P3 planlarına ve görsellerine geçer) → P2/P3 ilk geçişi | ilk geçiş 1 | yok | yerel (sahte) |
| A12 | Animatik | T1 (`zaman_cizelgesi --asama animatik`); ses `seslendir --animatik` (seçilmiş seslerle TTS), `muzik --uret`, `ses_katmani --cizelge T1`, `son_miks --animatik`; `kurgu_render --animatik`; `kor_paket --kip animatik`; `habersiz-seyirci·animatik` × 3 + `·ilk2dk` × 3 (gerçek kapakla); `ozet-eslestirici`; `seyirci_topla`; tur 1'de `kesici` + `kurgu_denetim --kesme-simule`; `kurgucu·duzelt`; `kurgu_uygula`; tur 1'den sonra G1 düzeltmeleri; varsa `izleyici` (BAYRAK) | T1, görseller, sesler, `HIKAYE.json` | `ANIMATIK/animatik_v<N>.mp4`, `ANIMATIK/ISITSEL_DOKUM.md`, `_RAPOR/HS_ANIMATIK_FILM_t<n>.json`, `KURGU/surumler/KURGU_PLANI_T1_v<N>.json`, `FILM_DURUM → animatik: ONAYLI` (imza), `BILGI_PAKETI/animatik/` (kullanıcıya bilgi) | **Kapıyı yalnız bütün kareleri G1 GEÇ olan tur açar.** Kapı §1.4; render süresi = T1 ±1 kare; yer tutucu ≤ %10 | 3 tur + 1 kurtarma (`yapimci·doktor`); sonra DUR + kâğıt ürün teslimi | AI84 ≈ 13–16 bin (tahmin) | yerel (sahte) |
| A13 | Kesin bütçe B2 | betik `kredi.py b2`, `olcek.py`; `hat-denetcisi` | `URETIM_ONIZLEME`, kuyruk, `OLCUM0` | `URETIM_ONIZLEME.json/.md` (kredi, Flow günleri, kullanıcı el işi saati, token projeksiyonu), `_RAPOR/HAT_B2.json` | tahmin ≤ bakiye × 0,9 ve ≤ tavan; HAT: GİT | — | yok | yerel (sahte) |
| A14a | Dikey kesit (ilk filmde atlanamaz) | betik `blok_plani --kesit`; Memmet `--mod elle` (kullanıcı GÖNDER'e basar); V1 + SC1 + V2 + V3 + G1Z; `seslendir --parti`; `muzik --yerlestir`; `renk_cila`; `buyut`; `son_miks`; `kurgu_render --kesit`; `habersiz-seyirci·kurgu` × 3 (yalnız kesit); varsa `izleyici`; `ders-editoru` (PILOT) | P0 + P1'in ilk dakikası (≈ 43 plan, hesap) + kapsama eksikse ≤ 10 plan | `KESIT/kesit_v<N>.mp4`, `_RAPOR/PILOT_FILM.json`, `BILGI_PAKETI/kesit/` (kullanıcıya bilgi) | teknik kapılar HATA 0; kesit seyircisinde KRİTİK 0; PILOT kararları (istem biçimi, take değeri, canlı bekleme, ses yolu) yazıldı | yeniden çekim plan başına ≤ 2 | evet (≈ 35–45 klip; filmin kendi planları, ek kredi değil) | yerel (sahte) |
| A14 | Video blokları | betik `blok_plani` (uygunluk kuyruğu, blok ≤ 20 plan) → Memmet (`elle`; gece yalnız izinle) → her indirmede V1 + SC1 → blok arasında V2, V3, `kare_zinciri --cikar` + G1Z → `kuyruk.py`; P1 videoları bitince **KR8a** P1 kurgu ön turu (kapı değil; dersleri P2/P3 bloklarına geçer); kullanıcı GÖNDER'e basar | `SIRALI_GORSEL` (G1 GEÇ + SHA1), `hareket_istem` | `SIRALI_VIDEO/NNN.mp4`, `KUNYE/NNN.json`, `KREDI_DEFTERI.jsonl`, `<veri>/HESAP/FLOW_YUK.jsonl`, `_RAPOR/V1_B*`, `V2_*`, `V3_*`, `G1Z_*`, `S2m_D*` | her klip V1 + V2 + V3 GEÇ; zincir kaynağı ayrıca G1Z GEÇ | plan soyu başına toplam deneme ≤ 3 (ilk + 2 yeniden) | evet | yerel (sahte) |
| A15 | Ses | betik `seslendir --parti`, `ses_donustur`, `ses_karar` (merdiven); gri bantta `hikaye-yazari·replik_kabul` (her seferinde yeni örnek) | klipler, evren sesleri, `SESLER/diyalog.json` | `SESLER/diyalog.json` v2, `SESLER/donusum/`, `_RAPOR/S2_*.json` | S2 HATA 0; merdiven tükenirse açık rapor | merdiven basamakları; yeniden çekim ≤ 2 | AI84 (`ai84_vc` ≤ 20 bin tavan) + Flow (ses dilimi) | yerel (sahte) |
| A16 | Kurgu | `plan_kurgu` (`kirp_oner`), ses (`diyalog_esitle`, `ses_katmani T2`, `muzik --yerlestir`, `son_miks`), `kurgu_render --onizleme`, `kurgu_denetim` (Z3), `habersiz-seyirci·kurgu` × 3 (aşamalı, tam film) + `·ilk2dk` × 3, varsa `izleyici`, `kurgucu·duzelt/·sifir_kredi/·kirp_incele`, tur 1'de `kesici`, `kuyruk.py`, `renk_cila`, `buyut`, `capcut_film` | videolar, `diyalog.json`, raporlar | `KURGU/KURGU_PLANI.json` + `surumler/`, `KURGU/onizleme_v<N>.mp4`, `_RAPOR/Z3_v<N>.json`, `HS_KURGU_FILM_t<n>.json`, `S3…S7`, CapCut taslağı "YZ <FILM> v<N>", `KURGU/son_capcut_projesi.json`, `KURGU/altyazi_en.srt`, `altyazi_tr.srt` | Z3 HATA 0; §1.4 kapı; S7 −14 ±1 LUFS, ≤ −1 dBTP; KRİTİK = 0 olmadan taslak kullanıcıya verilmez | 3 tur + 1 koşullu (son turda GENEL ≥ 0,5 arttıysa) | evet (kurgu dilimi; plan başına ≤ 2) | yerel (sahte) |
| A16n | Kullanıcı notu (isteğe bağlı döngü) | beceri `film-not` → betik `taslak_fark`, `notlari_oku`; `kurgucu·not`; `kurgu_uygula`; `kurgu_denetim --hepsi`; `capcut_yama`; kullanıcı CapCut'ı kapatır | kullanıcının notu ya da CapCut düzenlemesi | `KURGU/TASLAK_FARK.json`, `NOTLARIM.json`, `NOT_CEVAPLARI.md`, klon taslak "<adı> · v<N+1>", `_RAPOR/YAMA_v<N>.json` | notların %100'ü bir kararla kapanır; kullanıcının kaynak taslağı değişmez; klon öz denetimi 0 fark | kullanıcı istedikçe | yalnız KRİTİK için, dilimden | yerel (sahte) |
| A17 | Yayın | betik `capcut_film --yayin` (NOTLAR'sız taslak); kullanıcı CapCut'tan 4K 24 fps dışa aktarır → `YAYIN/`; betik `kalite_denetim --final` + yayın doğrulaması (+ gerekirse `son_miks --mux`); `jenerik`; `kapak`; `yayin-paketcisi·paket` + `·kapak`; `yayin_paketi --dogrula`; `shorts_mp4` (3 Short + fragman) | yayın taslağı, `KURGU_PLANI`, `HIKAYE.json`, `KANAL_TESHIS.md` | `YAYIN/<FILM>_4K.mp4` (kullanıcı), `YAYIN/YAYIN_DOGRULAMA.json`, `YAYIN/ses_master.wav`, `YAYIN/kapak_<n>.jpg`, `YAYIN/PAKET.json`, `YAYIN/SHORTS/*.mp4`, `YAYIN/FRAGMAN/*.mp4`, `KURGU/altyazi_*.srt` | final kalite HATA 0 (siyah, donma, planlanmamış sessizlik, −14 ±1 LUFS, ≤ −1 dBTP); paket doğrulama HATA 0 (başlık ≤ 100 kr, bölüm kuralları, YZ beyanı alanı, "kill" BAYRAK) | mux kanıtı yoksa A16n | yok | yerel (sahte) |
| A17y | Yükleme (isteğe bağlı; varsayılan kapalı) | betik `youtube_yukle.py` | `YAYIN/PAKET.json` | yükleme kaydı | kullanıcının o film için `YUKLE.bat` ile verdiği açık onay | — | yok | yerel (hayır) |
| A18 | Kapanış ve öğrenme | betik `ders_derle`; `ders-editoru`; `hikaye-yazari·evren`; betik `evren.py --film-sonu`; `arsivle` (bilgi + `ARSIVLE.bat`) | bütün raporlar, ders ham kayıtları | `<veri>/BILGI/DERSLER_AKTIF.md`, `KURALLAR_OGRENILEN.json` (aday/deneme), güncel evren, `FILM_SONU_RAPORU.md` | ders korkulukları HATA 0 | — | yok | yerel (evet) |
| A18a | Yayın sonrası analiz (48 sa, 7 gün, 28 gün) | betik `yayin_analiz.py`; `yayin-paketcisi·izleme` | YouTube Analytics (OAuth varsa) | `_RAPOR/YAYIN_ANALIZ_<gun>.json`, ders kayıtları (`kaynak: gercek_seyirci`) | veri yoksa "ölçülemedi" | — | yok | yerel (hayır) |

### 1.4 Seyirci kapılarında "kapı" ve "hedef" (ilk iki film)
Bütün habersiz seyirci kapıları (HS_KAGIT, HS_PLAN, HS_ANIMATIK, HS_KESIT, HS_KURGU) aynı politikayla çalışır:
- **Kapı (hattı durdurur):** KRİTİK = 0 (geçerli sayılan; §2.1 D-21) · kritik anahtar olguların özet eşleşmesi ≥ 0,80 (parti başına) ·
  GENEL medyan ≥ 7 · şema, filtre ve kimlik HATA'sı 0. HS_KESIT'te özet eşleşmesi yalnız kesitin kapsadığı olgularla hesaplanır.
- **Hedef (döngüyü sürdürür):** GENEL medyan ≥ 8 (RE `seyirci_genel_esik`) · her ölçüt medyanı ≥ 7 (RE `seyirci_olcut_min`) ve RE
  `seyirci_olcut_hedef` · ORTA ≤ 3/parti (RE `kopukluk_orta_max_parti`) · ilk 2 dk 3/3 (RE `ilk2dk_devam_evet_min`) · bütün olguların özet
  eşleşmesi ≥ 0,80 (RE `ozet_eslesme_min`).
- **Döngü:** Hedefe ulaşılmadıkça tur sürer. Durma sırası: (1) hedef sağlandı; (2) aşamanın tur tavanı doldu; (3) **plato**: iki tur üst üste
  GENEL medyan artışı < max(0,5; Ö0-f'nin ölçtüğü `seyirci_gurultu_std`) → bir kez merdiven (`yapimci·doktor`), sonra durma.
- **Durunca:** Kapı sağlanıyorsa hat sürer; `hedef_alti: true` karar defterine ve `FILM_SONU_RAPORU.md`'ye yazılır, kullanıcıya bilgi verilir.
  Kapı sağlanmıyorsa merdiven tükenmiş demektir: kâğıt aşamasında konu kartı bir kez yeniden yorumlanır (`yapimci·konu`, yeni eksen); yine
  geçmezse **kâğıt ürün** (senaryo + varsa animatik) "yüzüne vur" raporuyla teslim edilir, videoya geçilmez, kullanıcıya soru sorulmaz.
- **Üçüncü filmden itibaren:** gerçek seyirci verisi (A18a) ve panel puanları arasındaki ilişki ölçüldükçe `ders-editoru` kapı tabanını 7'den
  yukarı taşımayı önerebilir (yalnız kanıtla; §5.3 korkulukları). Gerekçe §2.1 D-20.

### 1.5 Sabit sıra kuralları ve küresel geri dönüş bütçesi
**Sıra kuralları (kodla zorlanır; `film.py` girdi imzasına bağlar):**
1. Kredili bir aşama, kendisinden önceki bütün kapılar aynı girdi imzasıyla GEÇ olmadan başlamaz ([UM2]).
2. Telaffuz testi yerelin ilk işidir (A10b); geçmeyen ad kartlardan ve istemlerden önce değişir ([SM2] İ-10).
3. Ses kadrosu (A10c) animatikten önce biter; animatik sesi son sestir ([SM2] İ-2, [KU2] İ-4).
4. `animatik: ONAYLI` imzası olmadan video görevi açılmaz ([UM2] T4, [KU2] test 9).
5. İlk filmde dikey kesit (A14a) atlanamaz; `PILOT_FILM.json` olmadan A14 başlamaz.
6. Videoya yalnız G1 (zincirde G1Z) GEÇ ve SHA1'i eşleşen kare gider ([GS2] B1).
7. Yoğun görsel düzeltme yapılan gün video gönderilmez (görsel günü ≠ video günü; [GS2], 18.10 kuralı).
8. KRİTİK = 0 olmadan CapCut taslağı kullanıcıya verilmez ([KU2]).

**Küresel geri dönüş bütçesi (film başına; dolunca "en iyi sürüm + yüzüne vur raporu"; [SA] K-5 #4):**

| Döngü | Tavan | Dolunca |
|---|---|---|
| H15 dar hikâye değişikliği (kilit sonrası) | 2 parti-turu (her turda birden çok sahne olabilir) | kalan hikâye bulguları açık raporda; 0 kredi kurgu çözümleri |
| Kart tarifi revizyonu | 2 | `yonetmen·kart_secimi` en iyi teknik adayı seçer, BAYRAK |
| Plan soyu başına üretim denemesi | 3 (ilk + 2 yeniden çekim; bölmeden doğan planlar soyun sayacını taşır) | `yonetmen·onarim` planı değiştirir; o da tutmazsa plan `durdu` → `kurgucu·sifir_kredi` zorunlu çözüm (örtü, yer tutucu, kesme) |
| G1 | 2 düzeltme turu → kaçış (`sureklilik-denetcisi·kacis` + `yonetmen·onarim`) → K0'dan 1 kez | plan `durdu` (yukarıdaki gibi) |
| Animatik + kurgu turları toplamı | 8 (animatik 3 + 1, kurgu 3 + 1) | en iyi medyanlı sürüm, açık eksik raporu |
| İlk 2 dk | A/B + 1 üçüncü sürüm | en iyi sürüm + BAYRAK |
| Flow uyarısı | aynı takvim haftasında 2. uyarı → hesap 7 gün kilitli (tahmin) | `FLOW_KILIDI.json` süreli; kullanıcıya bilgi |
| Stop kancası devamı | 8 ardışık + film token bütçesi | 8 BEKLE + projeksiyon raporu |
| Aşama başına görev sayısı | `olcek.py` tahmini × 1,5 (tahmin) | 8 BEKLE + `TOKEN_PROJEKSIYON.md` (soru değil) |

### 1.6 Ölçek ve takvim (tek kaynak `olcek.py`; belgelerdeki sayılar yerine onun çıktısı kullanılır)
| Kalem | 30 dk | 40 dk | Kaynak |
|---|---|---|---|
| Plan / klip | ≈ 370 / ≈ 305 | ≈ 495 / ≈ 405 (aralık 300–440 klip) | ZN §2.6; BK §3 #5; B2'den ölçekleme ([SA] K-1) |
| Flow video kredisi (taban × 1,30 kapı payı) | ≈ 4.750 | ≈ 6.320 | RE `kredi_klip_720p` 12; [UM2] pay 0,30 |
| Flow video gönderimi (× 1,3) | ≈ 400 | ≈ 527 | [UM2] (hesap) |
| Flow görsel düzeltme gönderimi | ≈ 90–180 | ≈ 116–240 | [UM2] / [GS2] (tahmin; kesme turundan sonra düşer) |
| AI84 kredisi (film) | ≈ 20–25 bin | ≈ 25–30 bin; tavan 60 bin | [SM2] |
| Ajan görevi | ≈ 300–450 | ≈ 350–570 (kör gözlem ≈ 145–175 dahil; §3.6) | [UM2], [GS2] (tahmin) |
| Takvim | Ö0 ölçümünden türetilir: `gun = ceil(gonderim / olculen_gunluk)` + kâğıt 1–3 gün + yerel hazırlık 1–2 + görsel 4–7 + animatik 1–2 + kurgu/ses 2–4 | | [UM2] takvimi, [SA] K-1 #2 (tahmin; `elle` modda 3–6 hafta olabilir) |
| Kullanıcının el işi saati | `olcek.py` hesaplar ve `URETIM_ONIZLEME`'de gösterir (GÖNDER sayısı × süre + paket sayısı × süre + dışa aktarım) | | [ESY] EO10, [SA] K-2 #3 |

## 2. Tartışmalı noktalarda verilen kararlar ve gerekçeleri

### 2.1 Temel kararlar (D-01 … D-44)
Her karar: **ne** → **neden** (kanıt) → **nerede uygulanır**. Kesin kararlar (KK1–KK6) kullanıcınındır ve tartışılmaz; aşağıdakiler onların
nasıl uygulanacağına dair ekip kararlarıdır.

**Hat güvenliği ve ölçüm**
- **D-01 · Önce ölç, sonra yaz: Ö0 ölçüm turu.** Kâğıt aşamalarının kodu Ö0'ı beklemez; yerel aşamaların (A10–A17) P1 sırası Ö0 sonucuna göre
  kesinleşir. Neden: tasarımın taşıyıcı varsayımları ölçülmedi: Omni'nin saniyeli adımlara uyması ([YN2] R1), 4 GB kartta ses dönüştürme
  ([SM2] §4.8.3 "kıyasla ölçülecek"), 11 Claude Code davranışı ([CM2] §4.9.4), CapCut klonu ([KU2] R8), Gemini kotası ([UM2] Q16), Flow kapasitesi
  ([SA] K-1). Pilotu ilk filmin A14a'sına bırakmak, ≈ 120 P0 satırını ölçülmemiş temelle yazmak demektir ([SA] K-4). Yer: §1.2, §9 adım 2 ve 9.
- **D-02 · Güvenlik yaması her şeyden önce (PR-0).** Depodaki `memmet.py` bugün KK5'i çiğniyor: `DOGRULAMA_KELIMELERI` (satır 58) "olağan dışı
  etkinlik"i doğrulama sayıyor ve `kontrol_noktasi()` (satır 167–176) metin kaybolunca 12 saate kadar bekleyip kendiliğinden devam ediyor;
  `HATA_KELIMELERI`'ndeki "olağan/unusual" tek bir sonuç kartında yeniden gönderime yol açıyor ([UM2] S1, S1b); `film.py` `Kisitlandi` gelince
  sıradaki sağlayıcıya geçiyor; eski `.bat`'lar kapıları atlıyor ([UM2] S2). Yama memmet3'ün depoya gelişini beklemez ([SA] K-6). memmet3'ün
  aktarımı ilk yerel geliştirme oturumunun ilk işidir (sahibi: üretim); aynı yama ve aynı fikstür testi ona da uygulanır, memmet3'ün gece modundaki
  "uyarıda 5 kez sayfa yenile" davranışı silinir ([UM2] S6). Yer: §6.1, §9 PR-0.
- **D-03 · Hesap değiştirme yasağı.** İşaretli Flow hesabının yerine başka bir Google/Flow hesabıyla (ortak, aile, ikinci hesap) devam edilmez;
  kie.ai hiç kullanılmaz (BK §6.4 "gri abonelik havuzu" şüphesi). Neden: işaretlemeden sonra hesap değiştirmek bot tespitini atlatmanın bir
  biçimidir (KK5); BK §6.2 #8'deki "ikinci hesap ya da kie.ai" seçeneği bu kararla kapanır. Uygulama: Memmet Flow'da görünen hesap e-postasının
  yalnız sha1'ini `HESAP_DURUMU.json`'a yazar (açık metin saklanmaz). Son uyarıdan sonraki 14 gün içinde (tahmin) hesap kimliği değişirse
  `FLOW_KILIDI.json` (`neden: hesap_degisti`, kod 7) yazılır; kilit yalnız **asıl hesapta** `UYARI_GECTI.bat` şartlarıyla kalkar. Uyarı kaydı yokken
  hesap değişirse yalnız kaydedilir ve bilgi verilir. Resmî Vertex Veo API'si atlatma değildir (ayrı, resmî hizmet); yalnız kullanıcının
  `IZINLER.bat` ile verdiği dolar izniyle ve Ö0'da fiyatı ölçüldükten sonra yedek olur.
- **D-04 · Flow yükü hesap düzeyinde ve yalnız sıkılaşır.** Tempo 17.10 değerleridir (gece 12–30 sn, aynı anda 2, iki partide bir 15–30 dk mola;
  gündüz 6–15 sn; 8 gönderimde 3–6 dk mola; BK §6.2). `FLOW_YUK.jsonl` her gönderimi, `FLOW_TEMPO.json` bir sonraki izinli zamanı ve mola
  sayaçlarını tutar; Memmet yeniden açılsa da kalan mola sıfırlanmaz ([UM2]). Günlük görsel tavanı 20 ve görselden videoya 12 saat Ö0-b ölçene kadar
  geçerlidir (tahmin). Aynı takvim haftasında ikinci uyarı → hesap 7 gün kilitli (tahmin; [SA] §7). Ders defteri tempoyu yalnız yavaşlatabilir,
  tavanı yalnız düşürebilir. Takvim ölçümden türetilir: `gun = ceil(gonderim / olculen_gunluk)` ([SA] K-1 #2).
- **D-05 · Süre yazımdan önce seçilir; yazılmış film kısaltılmaz.** B0 (A01) [1800, 2700] sn aralığında bütçeye ve ölçülen kapasiteye
  (`gun ≤ takvim_hedef_gun`, varsayılan 21 gün, tahmin) sığan en uzun süreyi seçer. Ö0-b sonucu yoksa, üç ölçüm gününden biri bile 20 videoya uyarısız
  ulaşamadıysa ya da 40 dk takvime sığmıyorsa ilk film 1800 sn yazılır; 1800 sn bile sığmıyorsa yine 1800 sn yazılır ve takvim olduğu gibi bilgi
  olarak verilir. Neden: bütçe ve kapasite ancak yazımdan önce süreyi belirleyebilir ([SN2] §2.5); 30 dk RE `film_sure_aralik_sn`'nin
  alt sınırı ve kullanıcının 30–45 dk aralığının içindedir; süre kalite değildir (KK6 çiğnenmez). Yer: `kredi.py b0`, `olcek.py`.
- **D-06 · KK1'in yorumu: soru yok, bekleme yok, iş baştan yazılı.** Kullanıcıya konu dışında karar sorusu sorulmaz ve hat hiçbir kullanıcı kararını
  beklemez (tek istisna: kullanıcının kendisi açtığı `--onayli` kipi, §8.5). Para, gece çalışması ya da dış hesap içeren ayarların güvenli varsayılanı vardır ve hepsi **kapalıdır**: gece Flow çalışması, dolar
  harcaması (`usd_tavan_film: 0`), CC0 efekt indirme, YouTube bağlantısı, yükleme. Kullanıcı bunları yalnız kendi isteğiyle `IZINLER.bat` ile açar;
  sistem bu dosyayı `BASLA_BURADAN.txt`'de ve kullanıcı sözleşmesi kartında bir kez anar, hiçbir zaman sormaz. Kullanıcının fiziksel işleri
  baştan sayılarıyla yazılır (**kullanıcı sözleşmesi kartı**, §8.1; sayılar `olcek.py`'den). Neden: [UM2] Q9 ("kurulumda bir kez sorulur") KK1'e
  aykırıdır; [CM2] İ-9'un ".bat bilgi" biçimi doğrudur ama [SA] K-2'nin uyardığı gizli iş yükü ancak sayıların baştan söylenmesiyle dürüst olur.
- **D-07 · DUR'dan sonra ekip varsayılanı.** Kapı merdiveni tükenirse (§1.4) kullanıcıya "ne yapayım?" diye sorulmaz: kâğıtta konu kartı bir kez
  yeni eksenle yeniden yorumlanır; yine geçmezse kâğıt ürün (senaryo + varsa animatik) "yüzüne vur" raporuyla teslim edilir ve videoya geçilmez
  ([SA] K-2 #5). Kullanıcı kendiliğinden "yeni konu" ya da "bu hâliyle devam" derse bu bir kesin istek olarak karar defterine yazılır ve ilgili aşama
  yeniden açılır ([SN2] §4.8.1).
- **D-08 · Claude kullanımı ölçülür ve sınırlanır.** Her görevin `GOREV.json → kullanim {girdi, cikti, onbellek_okuma, sure_sn, model, effort}`
  alanı SubagentStop kancasında ajanın döküm dosyasındaki kullanım satırlarından doldurulur (döküm yolunun kanca girdisinde gelmesi
  doğrulanacak; gelmezse karakter/3 tahmini, "tahmin" etiketiyle). `film.py` film ve aşama toplamlarını `FILM_DURUM → harcama.token`'da tutar.
  İlk 30–50 görevden sonra kalan aşamaların projeksiyonu `TOKEN_PROJEKSIYON.md`'ye yazılır ve kullanıcıya bilgi verilir. Aşama görev tavanı
  (`olcek.py` tahmini × 1,5) ya da kullanım sınırı dolunca hat **8 BEKLE** + projeksiyon verir; DUR değildir. Neden: EMBERFALL'da kullanım sınırı
  doldu ve ajanlar yarıda kesildi (YAPIM_REHBERI §1); film ≈ 350–570 görev ve en kötü durumda ≈ 6–7 M seyirci tokeni ister ([KU2] R3, [SA] K-3).
- **D-09 · Model: bütün ajanlar `opus` + `effort: high`; kısma yalnız "karar 6 testi"yle.** Kullanıcının kuralı önemli işlerde Opus + yüksek efordur
  (BK §7 #2; basit dönüştürmeler zaten betikte). Bir rolün daha ucuz model ya da efora geçmesi ancak etiketli bir sette kalite farkı gürültü
  bandının içinde kalırsa ve karar defterine "ölçüm — fark — karar" yazılırsa yapılır ([SA] O-14). Ö0-f bu testi en yüksek hacimli iki rolde
  (`kare-tarifcisi`, `ozet-eslestirici`) koşar. Aynı test aday sayısı, tam/kısmi izleme ve plan seyircisi kararlarında da kullanılır.

**Claude Code katmanı**
- **D-10 · Görev defteri ve set amiri** ([CM2] §2.0 bütünüyle kabul). `GOREV.json` sözleşmesi, `_GOREV/<id>/` klasörü, ajanlara görev dışı bilgi
  verilmemesi (devretme mesajı tek cümle), "bitti" kararının yalnız SubagentStop'ta verilmesi, kesilmede kurtarma (`film.py kurtar`), yarım kör
  görevin sıfırdan, yarım yazar görevinin kaldığı yerden sürmesi, paralel ≤ 5, iç içe ajan yok (`tools`'ta `Agent` yok), fork kapalı
  (`CLAUDE_CODE_FORK_SUBAGENT=0`), yerleşik ajanlar (`general-purpose`, `Explore`, `Plan`) film sürüşünde yasak.
- **D-11 · Kancalar tek dosyada, mutlak Python yoluyla, kapalı başarısız.** Bütün kanca olayları `.claude/hooks/kanca.py <olay>` alt komutlarıdır
  (soğuk başlangıç ve bakım için; [SA] S-2); içe aktarmalar tembeldir. Komut `settings.local.json`'a kurulumun yazdığı **mutlak** Python
  yoluyla girer (`YOLLAR.json → python.ana`; çıplak `python` yok; [SA] O-15). Ana döngünün `python .claude/bin/film.py …` komutu için kurulum
  `settings.local.json → env.PATH`'in başına ana Python klasörünü ekler; Ö0-a #10 bunu doğrular, tutmazsa beceri komutları ve izin listesi
  `py -3.10 .claude/bin/film.py …` biçimine çevrilir. Güvenlik kancaları `timeout: 10`, `onFailure: block`. Kanca nabzı:
  `film.py basla` son 15 sn içinde nabız görmezse ajan görevi başlamaz. Becerideki kancalar ayar kancalarının yedeğidir. En düşük Claude Code
  sürümü 2.1.302'dir (doğrulanacak; [CM2] §4.7); kurulum sürümü kaydeder, nabız sürümü taşır, sürüm değişince SessionStart `test_kancalar.py`'yi
  çalıştırır. Otomatik güncelleme kapatılmaz (güvenlik düzeltmeleri gelsin diye); değişen sürüm testten geçmeden sürüş açılmaz.
- **D-12 · Üretim yerelde, bulut geliştirmede; iki kök kalır.** Film üretimi baştan sona kullanıcının Windows bilgisayarında yürür; bulut oturumu
  yalnız geliştirme ve `sahte`/`kaset` testleri içindir. Neden: bulutta proje iş parçacığında depo kancaları uygulanmayabilir ([CM2] R-12), git
  eşitlemesi teknik bilgisi az kullanıcıya iş yükler ([UM2] R8, [SA] O-4). `film.py esitle` P2'ye alınır. **İki kök kalır:** depo
  `Desktop\YZ_FILM_SET` (Claude Code burada açılır, `FILM_SETI.bat`), veri `Desktop\YZ_FILM` yerinde (kullanıcının dosyaları ve yolları bozulmaz;
  CLAUDE.md kuralı). Tek kök önerisi reddedildi: kullanıcının veri klasörünü git deposuna çevirmek anahtar ve medya sızıntısı riskini büyütür.
  Yanlış klasörde açılma riski veri kökündeki 5 satırlık yönlendirme `CLAUDE.md`'siyle ve SessionStart denetimiyle kapatılır ([CM2] §4.4.7).
  Kullanıcının tek git işi `GUNCELLE.bat`'tır (`git pull --ff-only`).

**Film zanaatı**
- **D-13 · Atomik eylem zinciri (KK2) — [YN2] şeması aynen.** Adım `{id a1.., bas, bit, ozne, tur fiziksel|mikro|konusma|ses_vurusu, fiil,
  govde, yon, hedef, olcu, el_sekli, hiz, etki{}}`; fiil yalnız `veri/fiil_sozlugu.json`'dan; sonuç fiilleri (RE `yasak_sonuc_fiilleri`: take,
  grab, pick up, get, use, fix, prepare, fight, search; açılışı tarif edilmedikçe open) ve iç durum fiilleri (realizes, decides, remembers, knows)
  HATA; klip başına 2–3 adım (konuşmalı planda ≤ 1 fiziksel adım ve konuşmadan ≥ 0,2 sn önce biter); ilk adım ≥ 0,5 sn'de başlar, son adım
  `klip_sn − 1,0`'da biter; sağ/sol daima **karakterin kendi** sağı/solu; eller `{sag, sol: {tutar, yer, sekil}}`, açık parmak sayısı `sekil`'den
  türetilir (kıskaç = 2); başlangıç durumu = başlangıç karesi, bitiş durumu = sonraki klibin başlangıcı (dünya defteri denetler). Durum yalnız olgu
  taşır; kadraj konumu, sırası, bakışın kadraja düşüşü, ışık yönü ve ekran yönü `kroki.py` ile `_derlenir`'e hesaplanır ([YN2] öz 1). İstem biçimi
  `aralik` ("0.5-3s: …") varsayılandır; Ö0-b `sira` biçimi V3 tutmada ≥ 10 yüzde puanı üstün çıkarsa (tahmin) `sira`'ya geçilir. ZN §3.7'deki
  "takes two slow steps" → "walks two slow steps" düzeltilir. "Holds still" yerine "holds the pose, breathing" ve kadrajdaki öbür kişiler için
  durum değiştirmeyen "canlı bekleme" Ö0-b A/B'sinde zıplama ve dudak hatası artışı ≤ 2 yüzde puanıysa varsayılan olur ([ESY] EK2-5); Y06 "aynı
  anda **durum değiştiren** adım atan özne ≤ 1" diye daraltılır.
- **D-14 · Animatiğin ilk turu G1 düzeltmelerinden önce.** A11'de her planın 2 adayı G1 ilk geçişinden (yerel ölçüm + kör gözlem + kod kararı)
  geçer; düzeltme turları (CORRECTION, Flow görsel günleri) **A12 tur 1'den sonra** ve yalnız kesilmeyen planlar için yapılır. Tur 1'de her planın en
  iyi adayı gösterilir; kimlik HATA'lı plan yer tutucuyla (gri kare + eylem şeridi) gösterilir. Tur 1'in G1 kuyruğundaki planlara düşen süreklilik
  bulguları "zaten kuyrukta" işaretlenir ve kapı kararına sayılmaz; hikâye ve ritim bulguları sayılır. Animatik kapısını yalnız bütün kareleri G1
  GEÇ olan tur açar ([GS2] ilkesi korunur). Neden: hikâye ve ritim bulguları ile kesme turu, en pahalı kredisiz iş olan ≈ 116–240 düzeltme
  görselinden önce gelmeli; kesilecek plana düzeltme görseli üretilmemeli ([SA] O-9). KR3a (P1 ön turu) ilk iki filmde kalır; değer ölçülür.
- **D-15 · Kare zinciri (KK3d).** `gecis_turu: devam` → **son kare zinciri**: kurguda kullanılan kesme anındaki gerçek kare ([KU2] Y55 penceresi:
  son adımın ölçülen bitişi + ≥ 0,2 sn ile `klip_sn − 0,5` arası; en durgun ve keskin kare), doğal 1280×720 en-boyunda, üretken düzeltme olmadan
  ([GS2] İ-7). Teknik son kare (`-sseof`) hiçbir yerde kullanılmaz. **Bitiş sabitleme (Flow "Bitir")** yalnız önceki klipte durum değiştiren kritik
  adım varsa ya da V3 tutmadıysa, konuşmasız planda kullanılır ([YN2] Y56). **Her plana planlanmış görsel** üretilir (animatik ve yedek).
  Derinlik ≤ 2; sonra yeniden demirleme. Doğal durak yoksa araya örtü planı: süre ≥ max(1,0; A'nın kullanılan tutması + B'nin ölçülen durağan
  başı) ([KU2] İ-11). Zincir kaynağının çıkış noktası kurguda kilitlidir (`kullanim_kilit: zincir`). Ardıl plan aynı blokta değil, kaynağı V1 + V2 +
  V3 + G1Z'den geçtikten sonraki blokta gönderilir. Kodda değerler `bagimsiz | son_kare | bitis_sabit`'tir (ZN'nin Z0–Z3 kapı adlarıyla çakışmasın;
  [UM2] İ-4). [UM2] C5'in "Bitir varsayılan" önerisi reddedildi: Bitir karesine klibin son karesinde (8,0 sn) ulaşılır, bu an güvenli pencerenin
  dışındadır ve seyircinin gördüğü kesme karesi değildir ([KU2] §4.8.2-d). Eylem kesmesinde önceki klibin gerçek karesinin türev görsele **ek
  referans** olarak verilmesi Ö0-b'de A/B'lenir; fayda yoksa gerekçesi karar defterine yazılır ([SA] O-6c).
- **D-16 · G1: her plana 2 aday, her aday tam denetim.** Yerel ölçüm (YuNet + SFace, MediaPipe, OWLv2, DINOv2, CLIP) → `kare-tarifcisi` kör gözlemi
  (iki aşamalı form: serbest envanter p1/p2 + görüntü koordinatlı hedefli sorular; anatomik sol/sağ ve kişi eşlemesi kodda) → kod kararı (iki
  kaynağın HATA'sı HATA; tek kaynak BAYRAK; ölçülemeyen BAYRAK) → `sureklilik-denetcisi·hakem` yalnız tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ alanlarını
  karara bağlar; iki kaynağın HATA dediğini GEÇ'e çeviremez ([GS2] İ-3). **ÖLÇÜLEMEDİ asla GEÇ değildir.** SFace eşikleri 0,363 (resmî, HATA
  sınırı) / 0,45 (tahmin, GEÇ) ve 0,363'ün altına inemez. Düzeltme görselleri kullanıcıya paket olarak gitmez: `vertex_gorsel` (dolar izni varsa)
  → `flow_gorsel` (Memmet, çift çıktı, `elle`, ayrı görsel günü). Kör soru daraltma yalnız soru düzeyinde ve ≥ 30 etiketli örnekte (tahmin; [GS2]) kaçırma ≤ %10
  olduğunda yapılabilir; kimlik, el–nesne, kişi sayısı ve yasak öğe soruları asla kaldırılmaz. Plan başına 3 aday varsayılan değildir: Ö0-e
  Gemini'nin plan başına 3 aday verdiğini ve karar 6 testi düzeltme hacmini anlamlı düşürdüğünü gösterirse 3'e çıkılır.
- **D-17 · Dikey kesit = pilot dalga = ilk film kalibrasyonu.** [UM2] A14a pilot dalgası, [ESY] EK1-2 dikey kesiti ve [GS2] GS0'ın ilk film bölümü tek
  aşamadır: animatik geçtikten sonra P0 + P1'in ilk dakikası (≈ 180 sn ≈ 43 plan ≈ 35 klip, hesap: RE `ilk120_asl_max_sn`, `asl_parti_hedef_sn`,
  `klip_bolme_oran_hedef`) videodan son miks, renk ve büyütmeye kadar yayın kalitesinde bitirilir. [UM2]'nin kapsama listesi (3 son kare zinciri
  derinlik 1–2, 3 bitiş sabitleme, 4 iki kişilik, 3 el–nesne kavrama, 3 konuşmalı, 2 yaratık, 2 düşük ışık, 2 profil/sırt) eksik kalırsa P1'in
  sonraki planlarından en çok 10 plan eklenir. Ek kredi değildir: planlar filmin kendisidir. [GS2] GS0'ın karşılaştırma klipleri (≈ 120 kr) filmden
  çıkarılıp Ö0-b'ye (B3 planları) taşındı. Kesit 3 Claude seyircisinden, varsa `izleyici`'den geçer ve kullanıcıya **bilgi** olarak gönderilir;
  fragman ve Short ham maddesidir. Kesitte görülen sistematik sorun (donuk yüz, süzülen hareket, ucuz müzik, metalik ses) kalan klipler gönderilmeden
  düzeltilir.

**Seyirci ve kapılar**
- **D-18 · Tek habersiz seyirci ajanı, altı kip.** `habersiz-seyirci` kipleri: `kagit`, `plan`, `ilk2dk`, `animatik`, `kurgu` (dikey kesit de bu
  kiple, kesit paketiyle), `kapak`. Her tur 3 **yeni** örnek; birbirini okumaz; `omitClaudeMd: true`. **Aşamalı okuma** (P0 = 0–120 sn → P1 → P2 →
  P3; izleme kiplerinde 240–300 sn'lik `izleme_parcasi`): mekanizma Ö0-a'nın sonucuyla seçilir, sıra (1) SubagentStop `decision: block` ile aynı
  örneğe sonraki bölüm, (2) `SendMessage` ile aynı örneği sürdürme, (3) bölüm başına yeni görev + aynı seyircinin önceki bölüm raporları GIRDI'de
  ([SA] Ç5). Seyirciye **verilmeyenler**: `ekranda_bilgi`, `seyirci_ogrenir`, amaç, duygu, vuruş, merak/kurulum kimlikleri, kopukluk adayları
  (K1ON/K1 bulguları dahil; [KU2] İ-1), önceki tur raporları, önceki filmin özeti ([SN2] İ2), izleme kiplerinde kadraj etiketi ve plan tipi
  ([KU2] İ-7). Ad, ekranda söylenene kadar maskeli kalır. İzleme kiplerinde panel 2 × "A personası" (akşam TV'de izleyen, 25–55 yaş, fantastik ve
  savaş seven) + 1 × "B personası" (telefondan yarım dikkatle izleyen, ilk 30 sn'de karar veren) olur ([ESY] EO7); kâğıt ve plan kiplerinde 3 × A.
  Seri devamında isteğe bağlı 4. "dönen seyirci" (C personası, `IZLEYICI_OZETI.md` ile) medyana girmez. Her seyirci `kapatma_ani` ve
  `devam_olasiligi` yazar; betik bunlardan tahmini tutma eğrisi çıkarır (ölçü, kapı değil). Kurgu turunda her tur bütün film izlenir ([KU2] KR8:
  geri gidiş ancak tam izlemede görülür); kısmi izleme ikinci filmde A/B'lenir ve karar 6 testiyle karara bağlanır ([SA] K-3 #4).
- **D-19 · Çapraz göz ve kulak: `izleyici` ve `dinleyici` sağlayıcıları.** `izleyici` render edilmiş MP4'ü (görüntü + ses) izleyip aynı seyirci
  şemasında rapor yazar ve `yz_kusurlari[] {zaman, tur: yuz|hareket|ses|dudak|muzik|goruntu, siddet}` ekler; `dinleyici` ses sorularını cevaplar
  (aksan, ses–yüz uyumu, müzik ikili kalite karşılaştırması, yaratık sesi). İkisi de başka bir model ailesindendir (ilk sağlayıcı Gemini API) ve
  **bulgu kaynağıdır, onay kaynağı değildir**; ilk filmlerde BAYRAK verir, medyana girmez. Yalnız `<veri>/AYARLAR/` içinde Gemini API anahtarı varsa
  ve maliyet ücretsiz kotada ya da kullanıcının dolar izninin içindeyse çalışır; yoksa "ölçülemedi" yazılır ve aynı malzeme kullanıcıya **izle-dinle
  bilgi paketi** olarak gider (D-24). Görsel "ikinci göz" de yalnız API ile yapılır; kullanıcıya ek paket olarak verilmez ([GS2] İ-6'nın kullanıcı
  paketi yolu [SA] K-2 gereği kalktı). İlk üç filmde Claude paneli ve `izleyici` puanları gerçek tutma eğrisiyle karşılaştırılır; `izleyici` daha iyi
  öngörürse panel bileşimi `ders-editoru` önerisi ve karar defteriyle değişir ([SA] O-8).
- **D-20 · Seyirci kapıları: kapı 7 + olgular, hedef 8.** §1.4'teki politika. Neden: 8/10 geçmişte hiç tutturulmadı (B2 P1 v7 6, v8 5, v9 6,
  v10 6,5, v11 7 ve kullanıcı v11'i "süper" buldu; B3 kâğıt 6/8/7; BK §3 #9, PA); puanlar gürültülüdür (ZN §7.2 #10); her turda yeni seyirciyle
  10 tur, metin iyileşmese de şansla geçirebilir ([SA] K-5: p = 0,2 için ≈ %89). 8 hedef olarak kalır ve döngü platoya kadar sürer; bu yüzden
  KK6 çiğnenmez: döngü tasarruf için değil, ölçümün artık iyileşme gösteremediği için durur. BK §8 #20'nin çözümü ("8/10 hedef; 7 geçmişte
  kabul edilmişti") böylece aynen uygulanır. Aşama takvim kutusu: kâğıt aşamasında (A01–A06) görev sayısı `olcek.py` tahmininin 1,5 katını aşarsa
  `yapimci·doktor` teşhisi zorunludur ([ESY] EO8).
- **D-21 · KRİTİK reddinin dört şartı** ([CM2] İ-8; [SN2] H11 ve [KU2] §2.6 ile birleşik): tek seyircinin KRİTİK'i yalnız (1) yeni bir örnekte,
  (2) yazar olmayan bir rolde (hikâye ve akış: `yapimci·doktor`; görsel: `sureklilik-denetcisi·hakem`), (3) kanıtla — seyircinin kendi paketindeki,
  kopukluk anından önceki, maskesiz satır ya da kare; betik doğrular — ve (4) tur ve seyirci başına en çok 1 kez geçersiz sayılabilir. İki ya da daha
  çok seyircinin KRİTİK'i geçersiz sayılamaz. Kurgucu kendi kesimini aklayamaz. Her red `kararlar/`'a ve ders defterine (`yanlis_alarm`) yazılır.

**Oyunculuk, gösteri, diyalog**
- **D-22 · Oyunculuk tasarlanır** ([ESY] EK2). Plan düzeyinde kadrajdaki her karakter için `zanaat.oyunculuk.<karakter> {ic_durum, alt_metin, dis_ifade {bas, bit}, isaretler[], siddet 0–3}`:
  `ic_durum` ve `alt_metin` senaristin sahne notundan gelir ve seyirciye verilmez; `dis_ifade` `veri/ifade_sozlugu.json`'daki ≈ 16 değerden (tahmin) biridir ve
  her değerin filtre-güvenli İngilizce karşılığı istemlere, kör soru karşılığı forma derlenir (ör. `gizli_endise` → "a composed face, eyes darting,
  lips pressed together"; "cheek", "trembles" gibi filtre kelimeleri şablona giremez, `istem_denetim` testinden geçer). İnsanlı her planda
  kadrajdaki her karakterin `dis_ifade.bas` değeri zorunludur (durum defterine `ifade` olarak geçer); "notr" gerekçe ister. Dünya defterinde duygu sürekliliği: `karakterler.<id>.duygu {durum, siddet, izler[]}`
  (izler: `gozler_kizarik`, `nefes_nefese`, `yuz_terli`, `sac_dagilmis`), sahne içinde miras, zaman atlamasında azalma; K0'da gerekçesiz duygu
  sıçraması BAYRAK. `kare-tarifcisi` formuna beklenen değer gösterilmeden ifade sorusu eklenir (neutral, fear, anger, sadness, tenderness,
  surprise, determination, joy, contempt, unclear + şiddet 0–3); G1'de uyumsuzluk BAYRAK, iki aday da geçtiyse seçim sırası (1) BAYRAK sayısı,
  (2) ifade uyumu, (3) kimlik fark payı, (4) mekân benzerliği, (5) keskinlik; V3'te replik penceresinin ortası ve sonu için aynı soru. `teslim`
  sözlüğü 5'ten 12 değere çıkar (eklenenler: `aci`, `yalvaran`, `alayci`, `sefkatli`, `yorgun`, `aceleci`, `sakin_tehdit`; her biri 4 LUFS
  sınıfından birine eşli). Sözsüz ses vuruşları (iç çekiş, kısa gülüş, yutkunma, nefes) replik bloğunun dışında `tur: ses_vurusu` mikro adımıdır.
  `plan-elestirmeni` listesine iki madde: "Seyirci karakterin ne hissettiğini yüzünden okuyabilir mi?" ve "İç durum ile dış ifade arasında alt metin
  var mı?".
- **D-23 · Çoklu çekim (take) ölçüyle açılır.** Dikey kesitte duygu yükü yüksek ≈ 10 plan iki kez çekilir; seçim kör ifade okuması, V1/V2 ve varsa
  `izleyici`'nin ikili karşılaştırmasıyla yapılır. İkinci çekim ≥ %30 durumda açık farkla seçilirse (tahmin) take, `oyunculuk_kritik` kümesinde açılır:
  `duygu_tutma` planları (RE `duygu_tutma_film_max` 25), vuruş noktalarındaki konuşmalı yakın planlar, ilk 120 sn'nin konuşmalı yakın planları,
  doruk yakın planları ve vitrin anları; film başına en çok 60 plan (tahmin). B0/B1 bu 60 × 12 = 720 krediyi (hesap) **take payı** olarak ayırır;
  take açılmazsa pay kapı payına döner. Take gönderimleri D-04'ün tempo ve kapasite kurallarından geçer.
- **D-24 · Gerçek seyirciyle bağ** ([ESY] EK3). Ö0-g kanal teşhisi (B1/B2: gösterim, tıklama oranı, ortalama izleme, tutma eğrisi, trafik kaynağı)
  ilk filmi beklemez, ama bulguları kapak/başlık ve ritim önceliklerini belirler. YouTube salt okuma bağlantısı (`YOUTUBE_BAGLA.bat`, OAuth belirteci
  yalnız `<veri>/AYARLAR/`'da) bir kurulum işidir, soru değildir; kullanıcı bağlamazsa sonuç "ölçülemedi"dir. `yayin_analiz.py` yayından 48 saat,
  7 gün ve 28 gün sonra tutma eğrisini `KURGU_PLANI` çizelgesine eşler ve düşüş noktalarını plan kimliğiyle ders defterine `kaynak: gercek_seyirci`
  olarak yazar; bu kaynak defterdeki en yüksek kanıt ağırlığını alır. 48 saatte tıklama oranı ya da ilk 30 sn tutması kanal ortalamasının altındaysa
  kapak/başlık değişikliği önerisi bilgi olarak yazılır; değişiklik kullanıcının işidir. Animatik ve dikey kesitten sonra 3–5 dk'lık izle-dinle bilgi
  paketi (kesit, ses kadrosu örnekleri, ana tema) Telegram'a ya da masaüstüne gider; kullanıcı susarsa hat beklemez, itiraz ederse `film-not`.
- **D-25 · Müzik: kaynak merdiveni ve kalite kapısı** ([ESY] EK4, [SM2] §4.8.4). Leitmotif ajanın yazdığı özgün notalardır (MIDI; kroma şablonuyla
  ölçülür). Yayın zinciri: `acestep` (ACE-Step 1.5, yerel; "Cover/Refer audio" ile motifin çalınmış hâli girdi) → `kutuphane` (lisansı kayıtlı
  parçalar: CC0 ya da YouTube Ses Kitaplığı; kullanıcının bir kerelik isteğe bağlı indirmesi) → `elevenlabs_muzik` (yalnız koşulları okunup
  `LISANSLAR.json`'a "ticari YouTube: evet" yazılınca; P2) → `midi_ornek` **yalnız animatikte ve motif omurgası olarak**; yayında tema ipucu General
  MIDI örnekleriyle çalınmaz. Müzik kalite kapısı: her ipucunun adayları `dinleyici` ile ikili karşılaştırılır ("hangisi sinema filmi müziğine
  benziyor?") ve yerelde spektral genişlik, dinamik aralık, stereo genişlik, artefakt ölçülür; ilk filmde BAYRAK. Gemini'de elle müzik üretimi yok
  (KK1); Lyria/Gemini ambiyans için hiç kullanılmaz (BK §5.1.2). Her seçilen dosyanın kaynak kaydı tutulur (model, sürüm, lisans, istem, tohum, motif,
  SHA-1) ve Content ID itirazının kanıtıdır.
- **D-26 · Paketleme sahiplenilir** ([ESY] EK5). `yayin-paketcisi` baştan yazılır ve yayın stratejisinin sahibidir (`YAYIN/PAKET.json`,
  `YAYIN/KAPAK_SPEC.json`): kanal teşhisinin yorumu, hikâye odasının başlık adaylarından seçim (başlık yazmaz; [SN2] İ11), kapak şartnamesi, Short ve
  fragman planı, YZ beyanı, 48 saat izleme yorumu. **Kapak kuralı:** kapak filmde olan bir **anı** (aynı karakterler, aynı yer, aynı olay; vaat
  sözleşmesi) gösterir ama filmdeki karenin kendisi olmak zorunda değildir; kilitli kartlarla ayrıca kurulmuş yüksek çözünürlüklü görseldir. Neden:
  BK §1.7.6 yalnız yanıltıcı kapağı yasaklar; kapak küçük boyutta okunacak biçimde kurulmalıdır. 8–12 aday (A11'in ilk görsel paketinde) →
  `kare-tarifcisi·kapak` (anatomi, yazı, kimlik; 168×94'e indirildiğinde yüz ve yaratık seçiliyor mu) → `habersiz-seyirci·kapak` × 3 ikili
  karşılaştırma ("bu başlık ve bu kapakla tıklar mıydın?") → `yayin-paketcisi·kapak` seçer. Animatiğin ilk 2 dk testi kapak **görseliyle** yapılır.
  Fragman (30–60 sn) dikey kesitten çıkar; 3 Short dikey kadraja uygun anlardan seçilir. Yayından sonra YouTube'un kapak testi (Test & Compare)
  kullanıcıya bilgi olarak önerilir (kanalda açık olup olmadığı doğrulanacak).
- **D-27 · Gösteri, açıklama, diyalog ritmi, hareket** ([ESY] EO1–EO4). (a) `HIKAYE.json → seyirlik_anlar[]` (senarist; planı yönetmen): parti başına
  ≥ 2 vitrin anı (ölçek ifşası, uçuş/yükseklik, hava olayı, ateş ve ışık, siluet kalabalık, manzara + yaratık), her biri 3–6 plan; vitrin planına
  ≤ 7 sn süre istisnası; en uzun gösterisiz aralık ≤ 360 sn BAYRAK; doruk "iki kişi + yaratık + çevre" ölçeğinde kurulur. (b) Seyirci formuna iki soru
  ("gereksiz açıklanan ya da tekrarlanan yer", "kendini aptal yerine konmuş hissettiğin an"); `anahtar_olgular`'ın ≥ %50'si öncelikle görüntü ya da
  eylemle verilir (BAYRAK); `diyalog-editoru`'ne klişe/açıklama listesi ("As you know", "We need to talk" …) ve "bilgi taşıyan replikte çatışma"
  denetimi. (c) İş yaparken konuşma illüzyonu: diyalog sahnesi başına ≥ 1 replik L taşmasıyla ağzın görünmediği bir eylem planının üstünde sürer
  (BAYRAK; ses tanıtım kuralı korunur); söz kesme "—" ile yazılır ve metin kapısı tanır; cevap boşluğu (RE `cevap_boslugu_sn`) kurguda ölçülür.
  (d) V2'ye hareket hızı ölçüsü (özne kutusunun yer değiştirmesi + optik akış) fiil sözlüğündeki `beklenen_hiz` aralığıyla karşılaştırılır;
  diyalogsuz yavaş planda kurguda 1,05–1,15× uygulanır, değilse BAYRAK; sahne düzeyinde durum değiştirmeyen `canli_arka_plan` istemi (duman, kar,
  alev, uzak siluet).
- **D-28 · Yaratık ve parmak ölçüleri H'ye yükselebilir** ([ESY] EO5, [SA] O-6a-b). Yaratık kartı ≥ 3 sabit asimetrik işaret (ör. sol kaşta beyaz
  leke, sağ boynuzun kırık ucu) + Lab renk paleti + baş/gövde oranı taşır; kör sorular bu işaretleri görüntü koordinatında sorar; kart görünümlerinden
  DINOv2 yaratık kimlik bankası kurulur; davranış sözlüğü (merak = baş eğme + kulaklar ileri; korku = sinme + kuyruk kıvırma; sevgi = burun sürtme)
  `oyunculuk`'a girer; evre geçişi ekranda bir olaydır, boy planlar arasında kendiliğinden değişmez. Yaratık kimliği ve açık parmak sayısı bugün en
  çok BAYRAK'tır; ≥ 30 etiketli örnekte ölçülen doğruluk ≥ %90 olunca (ikisi de tahmin) tek başına HATA verebilir.
- **D-29 · 720p'den yayın görüntüsüne** ([ESY] EO6). Kurgudan sonra yalnız kullanılan pencereler (`kullanim`) 2× yapay zekâ büyütücüsünden geçer;
  büyütmeden sonra yüz bölgesinde SFace yeniden ölçülür (büyütücü yüzü değiştiremez; HATA). Ortak film görünümü `renk_cila.py` ile verilir: sabit renk
  LUT'u + ince gren + hafif halation, ayarı `<evren>/dunya.json`'da. Büyütücünün süresi Ö0-c'de ölçülür; 1 saatlik içerik için > 12 saatse (tahmin)
  1080p Lanczos + gren yoluna düşülür. Başlıkta "4K" ancak büyütme kapısı geçtiyse yazılır (`yayin-paketcisi`).

**Kurgu, bütçe, veri**
- **D-30 · Teslim CapCut taslağıdır; kullanıcı taslağı klonlanır** ([KU2] İ-2; KR satır 48, BK §8 #18). Dışa aktarmayı kullanıcı yapar; ffmpeg
  çıktısı ölçüm ve yedek içindir. Kullanıcı CapCut'ta düzenlediyse taslağı sıfırdan kurulmaz: salt okunur incelenir, kararları `KURGU_PLANI`'na
  kilitli işlenir, taslak **klonlanır**, klonda yalnız sistemin kanalları (Diyalog, Efekt, Ambiyans, Muzik, Altyazi, Kartlar, NOTLAR) yamanır, yeni
  medya yeni dosya adıyla bağlanır, kaynağa hiç yazılmaz. Yayın dosyasının sesi ancak "aynı çizelge" kanıtıyla (süre ±1 kare + 40 pencerede ses
  çapraz korelasyonu ofseti 0 ±1 kare, tepe ≥ 0,9 tahmin) değiştirilir. Ö0-d klonun ya da okumanın çalışmadığını gösterirse `yayin_kaynagi: master`
  (ffmpeg yayın dosyası) kurulum değeri olur ve not yolu "kullanıcının kararlarıyla yeni adla kur"dur.
- **D-31 · Bütçe dilimleri ve 0 kredi kuralı** ([KU2] İ-3, [UM2] C1). Kapı payı 0,30 (ilk film; RE 0,20 hedef olarak kalır, gerçekleşeni defter
  ölçer); dilimler görüntü/süreklilik/plan dili 0,15 · ses 0,07 · kurgu 0,08 (tahmin). Dilimler arası aktarım yalnız KRİTİK için ve `hat-denetcisi`
  notuyla. `cozum ∈ {yeniden_cek, bitis_sabit, yeni_plan, yeni_sahne}` olan kuyruk maddesi `sifir_kredi.denendi: true` ve gerekçe olmadan reddedilir
  (`kuyruk.py`, testli). V1/V2 kusuru kullanılan pencerenin dışındaysa betik `cozum: kirp` yazar, kuyruğa madde açmaz. Plan soyu başına toplam deneme
  ≤ 3. Bütçe biterse kalan maddeler 0 kredi çözümüne düşer; KRİTİK için o da yoksa hat 5 BÜTÇE ile durur ve "X kredi gerekiyor" bilgisi gider.
  Model, çözünürlük ya da plan sayısı düşürülmez (KK6).
- **D-32 · Tek ölçü, tek kod.** Aynı ölçü iki araçta hesaplanmaz ([KU2] İ-9): zamana bağlı her ölçü `zaman_cizelgesi.py` (hikâye TH, yönetmen T0,
  kurgu T1–T3 içe alır); fiziksel durum `dunya_defteri.py`; geometri `kroki.py`; istemler `istem_derle.py`; ses sinyali `olcum/ses.py`; tek miks
  `son_miks.py` (animatik, önizleme, final, Shorts aynı işlev; [SM2] İ-1); kör paket ve ad maskeleme `kor_paket.py`; puan birleştirme
  `seyirci_topla` (`puan_oku.py` v2); bulgu yönlendirme `bulgu_yonlendir`; kuyruk `kuyruk.py`; bütçe `kredi.py`; ölçek sayıları `olcek.py`;
  eşikler `esikler.py`. [SM2] S3.6 ve S3.8 çizelge aritmetiği olduğu için `kurgu_denetim.py`'ye taşınır; replik penceresi sessizliği yalnız S2.1'de
  ölçülür.
- **D-33 · Ders defteri: olay başına dosya, iki yönlü kalibrasyon, ilk filmde deneme.** Yer `<veri>/BILGI/DERSLER/ham/<zaman>_<film>_<olay>.json`
  ([UM2]); derleme `DERSLER_AKTIF.md` + `KURALLAR_OGRENILEN.json`; ajanlara yalnız `GIRDI/DERSLER.md` olarak (imzaya girer) verilir, kör rollere hiç
  verilmez ([CM2] İ-5). Yaşam döngüsü aday → deneme → aktif → pasif; terfi destek ≥ 3 ve ≥ 2 film (tek filmde ≥ 5), hikâye dersleri ≥ 2 film. İlk
  filmde "deneme" durumundaki **sıkılaştırıcı** dersler aynı filmin sonraki partisine uygulanabilir ([SA] O-6d). Bir eşik sıkılaştırılmadan önce aynı
  kalibrasyon setinde yanlış alarm oranı ölçülür; %30'u aşarsa sıkılaştırma reddedilir ([SA] K-5 #5). Güvenlik kuralları (Flow'da dur, tempo,
  gizli bilgi, silme yasağı, onay kuralları) öğrenmeyle gevşetilemez.
- **D-34 · Eşik dosyalarında kaynak zorunlu.** Her eşik anahtarı `{deger, aciklama, kaynak: olcum|belge|tahmin, etiket, gevsetilemez?}` taşır;
  `esikler.py` kaynaksız anahtarı "tahmin" diye raporlar; aynı anahtar iki dosyada HATA'dır. RE'nin bugünkü 148 anahtarının hiçbirinde kaynak yok
  ([SA] K-5 #3); geçiş PR-1'de yapılır. Belgelerde "[kaynak: RE]" yazımı tek başına kaynak sayılmaz.
- **D-35 · Adlar tek dosyada.** `YZ_FILM/ARACLAR/veri/ADLAR.json` klasör, ajan, kip, kapı, plan alanı, sağlayıcı türü ve `.bat` adlarının tek
  listesidir; `test_adlar.py` kodda ve becerilerde geçen her adın burada olduğunu denetler ([SA] O-1). İçeriği §2.4 ve §5'tir.
- **D-36 · Lisans defteri.** `YZ_FILM/ARACLAR/veri/LISANSLAR.json`: her bileşen için sürüm, kod lisansı, ağırlık lisansı, kaynak bağlantısı, doğrulama
  tarihi, "ticari YouTube: evet / hayır / bilinmiyor". `kurulum.py` "bilinmiyor" olan bileşeni ana hatta kurmaz, yalnız `--deneme` kipinde kurar.
  Kullanıcının hâlihazırda kullandığı hizmetler (Flow, AI84) `kullanici_hizmeti: true` ile işaretlenir; AI84'ün aracı (kriptoyla alınmış) olmasından
  doğan risk §10'da yazılıdır. Yayın paketine kaynak künyesi eklenir ([SA] O-5).
- **D-37 · Kademeli kurulum, ana ortamda CPU torch** ([SA] O-3). K1: kâğıt + Flow + G1 ölçümleri (ana Python 3.10; `torch` CPU; DINOv2-small,
  OWLv2-base, CLIP, YuNet, SFace, MediaPipe tek sürüm). K2: yalnız Ö0-c'de kazanan ses dönüştürme motoru (tek ayrı ortam). K3: MuseTalk, ACE-Step,
  büyütücü (ayrı ortamlar, CUDA), yalnız gerektiğinde. Her kademe "çalışıyor / çalışmıyor" kartı yazar; eksik kademe yalnız kendi basamağını kapatır.
  Model ve pip önbellekleri C'de tek klasörde (`YOLLAR.json`) toplanır, boyutları raporda gösterilir; D harici diski çalışırken kullanılmaz
  (BK §8 #21); önbellek temizliği kullanıcının işidir (Claude kalıcı silemez).
- **D-38 · Disk kapısı** ([SA] O-11). `film.py` her aşama başında `shutil.disk_usage` ile boş yeri ölçer; `disk_bos_min_gb` (20, tahmin) altında
  8 BEKLE + "`ARSIVLE.bat` ile bitmiş partileri D'ye taşı" bilgisi. Yeniden üretilebilir ara dosyalar (render önbelleği, eski 1080p türevleri) ve
  bitmiş partilerin eski sürümleri `robocopy /E /MOVE` ile taşınır; açık iş C'de kalır.
- **D-39 · Oturum hazırlığı ve gece** ([SA] O-12, [UM2] uygunluk kuyruğu). Bir Flow oturumuna girecek blokların bütün ön koşulları (G1 GEÇ kareler,
  derlenmiş istemler, BK onayı) oturumdan önce hazırdır; zincir ardılları sonraki bloğa planlanır ve V3 kör gözlemi bloklar arasında yapılır. Gece
  kipi Memmet'in kullanıcıya ait özelliğidir; varsayılan kapalıdır, yalnız `IZINLER.bat` ile açılır, aynı ya da daha yavaş tempoyla çalışır, gece başına
  gönderim tavanı Ö0-b'nin ölçtüğü uyarısız günlük kapasitenin %80'idir (tahmin) ve bütün durma kuralları aynen geçerlidir. Sistem gece kipini
  hızlandırma için önermez (KK5: Memmet seri üretim aracı değildir).
- **D-40 · YouTube kuralları ve yükleme** ([SA] O-13, S-6). `YAYIN/PAKET.json` bir `yz_beyani` alanı (YouTube'un gerçekçi sentetik içerik beyanı) ve
  politika kontrol listesi (özgün olmayan içerik kuralı dahil) taşır; `<veri>/BILGI/YOUTUBE_POLITIKA.md` resmî sayfalardan, kaynak ve tarihle,
  geliştirme oturumunda yazılır; 90 günden eskiyse (tahmin) `film.py` bilgi verir. Otomatik yükleme varsayılan **kapalıdır** (P2); açıksa bile her
  film için kullanıcının `YUKLE.bat` ile verdiği açık onay gerekir (CLAUDE.md, Yapılacaklar 6).
- **D-41 · Sağlayıcı türleri ve zincirleri.** `TURLER = (llm, gozlemci, izleyici, dinleyici, gorsel, gorsel_duzeltme, video, tts, ses_donustur,
  ayristirma, asr, dudak, muzik, buyutme)`; eski `ses` adı bir sürüm boyunca `tts` olarak tanınır. Gözlem türünün adı **`gozlemci`**dir ([GS2] ve
  [SM2] `vlm`, [UM2] `gozlemci` dedi; Türkçe adlandırma kuralı ve rol adı belirler). Zincirler §5.6'dadır. `Kisitlandi.kod ∈ {olagandisi, dogrulama,
  kredi_bitti, arayuz, filtre_red, anahtar_yok, ag, kota, ortam, zaman_asimi}`; zincirde sonraki sağlayıcıya geçiş yalnız `anahtar_yok`, `ortam`,
  `ag`, `kota`'da olur; `olagandisi` ve `dogrulama` **hiçbir zaman** başka sağlayıcıya geçirmez (D-02, D-03). `elle = True` sağlayıcı (kullanıcı işi
  gerektiren) müzik zincirine konamaz. `sahte`, `kaset` ve `sahte_bozuk` yalnız test kipinde (`--saglayici sahte` ya da `ORNEK_*` filmleri) çalışır;
  gerçek bir filmin zincirinde bulunurlarsa `film.py` HATA verir.
- **D-42 · Seri evreni sahip başına dosya** ([GS2] İ-11, [SN2], [SM2] İ-8). `<evren>/` yalnız `evren.py` ile yazılır; karakter, mekân, nesne, müzik
  kayıtları sahip uzmanın dosyasıdır (`karakter.json` görüntü, `hikaye.json` senarist, `ses.json` ses, `kroki.json` yönetmen). Git'e yalnız JSON girer;
  görseller, ses bankaları ve `.npz` dosyaları yerelde ve D yedeğinde durur. Kanon yalnız eklenir; sürümler silinmez.
- **D-43 · Dünya durumu defteri makinenindir** ([GS2] sahip, [YN2] §4.5.13 çözüm kuralları). `dunya_defteri.py` planların `baslangic_durumu`
  ve `eylem_zinciri.etki` alanlarından `DUNYA_DEFTERI.json`'u derler; olay çıkarır (bitiş − başlangıç → olay; her olayın etkili adımı ya da zaman
  atlaması kartı olmalı); görsel üretildiği anda planın durumunu dondurur (`uretim.durum_dondu`); kurgu sırası değişince yeni komşuları dondurulmuş
  durumla denetler (Y58). Elle düzenlenmez; makine sahipli dosyaların sha1'i saklanır, uyuşmazlık HATA'dır.
- **D-44 · Plan seyircisi ve ön turlar değeriyle kalır.** A07e (plan seyircisi), KR3a (P1 animatik ön turu) ve KR8a (P1 kurgu ön turu) ilk iki
  filmde koşar; tek başına yakaladığı ve sonraki partilerde önlenen bulgu sayısı ders defterine yazılır; iki filmde değer yoksa karar defterine
  gerekçeyle kaldırılır ([YN2] açık soru 8, [KU2] açık soru 11).

### 2.2 Ses ve dudak kararı (KK4): "Veo konuşur, sesi biz sabitleriz"

**Seçenekler** (kullanıcının donanımı RTX 3050 Ti 4 GB, Python 3.10; hesaplar Flow ve AI84; [SM2] §4.8.3):

| Yol | Dudak | Ses tutarlılığı | Metin | Oyunculuk | 4 GB kartta | Maliyet | Karar |
|---|---|---|---|---|---|---|---|
| 1. Veo'nun kendi sesi (`veo_ham`) | kusursuz | zayıf: her klipte ses yeniden icat ediliyor | bazen kelime ekleyip atlıyor | iyi | gerekmez | 0 | yalnız tek replikli figüran; ana yolun ham maddesi |
| 2. TTS + süreye sığdırma (bugünkü `seslendir.py`) | zayıf (B2: "dudakla gitmiyor") | tam | tam | TTS'nin | gerekmez | AI84 ≈ 13–16 bin | yalnız ağzı görünmeyen replikte (`tts`) |
| 3. TTS + yerel dudak senkronu (MuseTalk 1.5; `tts_dudak`) | iyi; ağız bölgesi 256 px'te yeniden üretilir | tam | tam | TTS'nin | çalışır: 8 sn klip ≈ 5 dk, fp16 (MuseTalk README: "tested on RTX 3050 Ti Laptop 4GB") | 0 $, zaman | merdivenin geç basamağı; çıktı V2'den yeniden geçer |
| 4. Veo sesi + AI84 Voice Changer (`ai84_vc`) | kusursuz | iyi | Veo'nun | korunur | gerekmez | tüm film ≈ 1,7–2,1 milyon kredi (tahmin; bakiyenin 2,6–3,2 katı) | tüm film için hayır; tek kritik replik, film tavanı 20 bin |
| **5. Veo sesi + yerel ses dönüştürme (`veo_donustur`)** | **kusursuz** (zamanlama Veo'nun) | **iyi–çok iyi** | Veo'nun → metin kapısı | **korunur** | ölçülecek (Ö0-c) | 0 $, ek kredi yok | **ANA YOL** |
| Wav2Lip, ticari olmayan modeller (MusicGen CC-BY-NC vb.), `fal_latentsync` | — | — | — | — | — | — | **asla** (kalite ve lisans) |

**Karar.**
1. **Ağzı görünen replik → `veo_donustur`.** İstem `{Ad} {ton_fiili_en}, {veo_ses_tarifi}: "{veo_metin|metin}"` biçimindedir; `veo_ses_tarifi`
   ≤ 12 kelime, sabit sıra: perde/tını + cinsiyet + **aksan** (ör. "in a low, husky female voice with a northern English accent"); aksan, seçilen
   ElevenLabs sesinin aksan etiketidir ([SM2] İ-3). Her indirmede **metin kapısı** (SC1): BS-RoFormer ile konuşma ayrılır → stable-ts ile hizalanır →
   VAD + ASR (replik penceresi ±1 sn), WER, ad doğruluğu, `tasidigi` içerik kelimeleri ve "ağzı en çok oynayan yüz = replik karakteri" denetlenir →
   kapıdan geçen söz pencereleri yerel dönüştürücüyle karakterin evren sesine çevrilir (F0 kaydırma 12·log2(f_hedef/f_kaynak), yalnız hizalanmış
   pencereler ±0,1 sn).
2. **Ağzı görünmeyen replik (ekran dışı, sırt, uzak, köprü) → `tts`** (AI84 üzerinden ElevenLabs v4; animatikteki dosya son sestir, ikinci kez
   ücretlenmez). Dönüştürücünün hedefi aynı TTS sesi olduğu için iki yol aynı tınıya oturur.
3. **Yol kodla önerilir:** `ses_plani.py --taslak` `_derlenir.agiz_gorunur ∈ {tam, kismi, yok}`'a göre yolu yazar; ajan ancak `yol_neden` yazarak
   değiştirebilir (gerekçesiz değişiklik S0.1 HATA). Gerçekleşen yol `SESLER/diyalog.json → replikler.<id>.yol_gercek`'te durur.
4. **Motor ölçüyle seçilir:** Ö0-c arşiv Veo klipleriyle (B2/B3) OpenVoice V2 ve Chatterbox'ı (RVC yalnız ElevenLabs/AI84 koşulları TTS çıktısıyla
   eğitime izin verdiği okunduktan sonra) kör ölçüyle kıyaslar: hedef benzerlik ≥ 0,70, zarf gecikmesi ≤ 20 ms, ASR WER artışı ≤ 0,05 (S1.11;
   tahmin); "TTS + süreye sığdırma" kıyasa çıta olarak girer. Seri başında `ses_kiyas.py` (SB3) aynı kıyası yapar; ilk filmin ilk 20 repliğinde yeniden
   ölçülür. Seed-VC dışarıdadır (lisans).
5. **B planı (Ö0-c hiçbir motorun eşiği geçmediğini gösterirse):** ağzı görünen replikte `tts_dudak` (MuseTalk 1.5, ayrı ortam, gece kuyruğu; 190
   diyalog planı × ≈ 5 dk ≈ 16 saat GPU, hesap) ve çıktısı V2 kimlik + S3 dudak denetiminden geçmek zorundadır; geçmeyen replik kurguda ekran
   dışına taşınır (`tts`) ya da yönetmen planı değiştirir. Bu durumda karar defterine "ana yol B" yazılır ve kullanıcıya bilgi verilir.

**Neden 5. yol:** (1) seyircinin tek büyük şikâyeti karakter görünüşünün değişmesidir (BK §1.4.3, 803 beğeni); ağız bölgesini yeniden üreten her
model yüz kapısının koruduğunu bozabilir, ana yol görüntüye dokunmaz; (2) kullanıcının iki sorunu ("ses klipten klibe değişiyor", "ses dudakla
gitmiyor") aynı anda çözülür; (3) oyunculuk yüzle uyumlu kalır (Veo bağırırken ses de bağırır); (4) dolar harcaması yoktur; (5) sağlayıcıdan
bağımsızdır: Flow yerine resmî Veo API'si kullanılsa da ses aynı evren sesine çevrilir.

**Ön koşullar (planlama kuralları):** replik bloğunda tek `teslim`; konuşurken fiziksel adım yok (konuşmadan ≥ 0,2 sn önce biter); konuşan yüz
okunur ölçekte (O/OY/Y; |yaw| ≤ 45°; yüz ≥ kare yüksekliğinin %12'si; Y32); konuşan planın başlangıç karesinde ağız kapalı (jawOpen ≤ 0,15);
dinleyenin ağzı kapalı ("listens silently, mouth closed", Y35); ekran dışı ses ancak karakter daha önce ekranda konuşurken duyulduysa
(`ses_tanitim_kurali()`; gizem sesi istisna); konuşmalı planda Bitir karesi kullanılmaz; üst üste konuşma ve replik ortasında gülme/ağlama yok
(sözsüz ses vuruşu ayrı mikro adımdır, D-22).

**Ses merdiveni** (`ses_karar.py`; hata türüne göre; her basamak ölçülür; kalite önceliği KK6 gereği yeniden çekim, kaliteyi düşürmeyen 0 kredili
basamaklardan sonra gelir). Kredili basamak da D-31'in 0 kredi kuralından geçer: `kurgucu·sifir_kredi` kaliteyi düşürmeyen bir çözüm (ör. repliği
ağzı zaten görünmeyen bir plana taşımak) bulursa o uygulanır; bulamazsa `sifir_kredi.gerekce` "kalite (KK6)" diye yazılır:

| Hata (kapı) | 1 | 2 | 3 | 4 | Son |
|---|---|---|---|---|---|
| Veo konuşmadı, yanlış kişi ya da dinleyen konuştu (S2.1, S2.5) | Flow'da yeniden çekim, CORRECTION şablonu (≤ 2) | `tts_dudak` → V2 + S3 | kurgucu: repliği ekran dışına taşı (L taşma, ses tanıtım kuralı) → `tts` | yönetmen onarımı | açık rapor |
| Metin gri bantta (WER 0,10–0,25) ya da `tasidigi` kelimesi değişti (S2.2, S2.4) | `hikaye-yazari·replik_kabul` (yeni örnek, 0 kredi): kabul → `duyulan_metin` altyazıya | ret → "word for word" CORRECTION ile yeniden çekim (≤ 2) | `tts_dudak` | yönetmen onarımı | açık rapor |
| Ad yanlış (S2.3) | yeniden çekim, ad CORRECTION + `veo_metin` okunuş yazımı (≤ 2); `istem_kalibi` ders adayı | `tts_dudak` | ekran dışına taşı → `tts` | — | açık rapor |
| Dönüşüm kalitesi (S2.8–S2.10; ör. fısıltıda metalik) | motor zincirinde sonraki motor | kurguda ağız görünmüyorsa (S3.7) `tts` | `ai84_vc` (film tavanı 20 bin; önce `estimate`) | `tts_dudak` | `teslim` değişikliği isteği (`hikaye-yazari`) + yeniden çekim |
| Aksan kayması (S2.16) | ağız görünmüyorsa `tts` | aksan CORRECTION ile yeniden çekim | `ai84_vc` | — | ders kaydı |
| Dudak ofseti (S3.1) | yerleşim hatasıysa `kurgu_uygula` düzeltmesi | `tts_dudak` çıktısıysa yeniden işleme | yeniden çekim | — | açık rapor |
| Ekran dışı replikte dinleyenin ağzı oynuyor (S3.5) | kurgucu: başka kırpma penceresi ya da aynı sahnenin başka tepki planı | "listens silently, mouth closed" CORRECTION ile yeniden çekim | — | — | açık rapor |
| Seviye, ambiyans, müzik, miks (S4–S7) | otomatik yeniden işleme | müzik kipine revizyon | — | — | açık rapor |

**Maliyet** (AI84 TTS 1 kredi/harf, BK §6.4; kelime ≈ 6 harf, tahmin): telaffuz testi ≈ 1,8 bin · ses seçimi ≈ 5 bin · animatik TTS (2.100–2.600
kelime) ≈ 12,6–15,6 bin · animatik turlarında değişen replikler ≈ 5–6 bin · son `tts` sesleri önbellekten 0 → **film başına ≈ 25–30 bin** (tavan
60 bin). Seri kurulumu (RVC seçilirse banka) 0–36 bin (tavan 40 bin). `ai84_vc` ≤ 20 bin. İlk film en kötü durumda ≈ 86 bin ≈ bakiyenin %13'ü
(≈ 649 bin, 13.10). Flow tarafında ses kaynaklı yeniden çekim ≈ 190 × %15 ≈ 29 klip ≈ 340 kredi (oran tahmin; ses dilimi 0,07 bunun içindir).

**Kalan sınırlar:** Claude sesi duyamaz; her ses yargısı ölçümle (WER, gömme benzerliği, F0, LUFS, dudak ofseti) ya da varsa `dinleyici` ile verilir
(D-19). `dinleyici` yoksa aksan tutarlılığı (S2.16) ve ses–yüz uyumu "ölçülemedi"dir ve ses kadrosu 30 sn'lik dinleme dosyasıyla kullanıcıya bilgi
olarak gider (`SES_SECIM.html` + izle-dinle paketi); kullanıcının itirazı `film-not` ile gelir.

### 2.3 Eleştirmenlerin KRİTİK ve ORTA maddeleri: karar tablosu
"Uygulandı" = önerinin özü tasarıma girdi; "kısmen" = bir parçası değiştirilerek ya da koşula bağlanarak girdi (neden yazılı); "uygulanmadı" =
neden yazılı.

**Seyirci-yapımcı eleştirisi ([ESY])**

| Madde | Karar | Nasıl / neden | Yer |
|---|---|---|---|
| EK1-1 İşitsel-görsel seyirci (`izleyici`) | kısmen | Sağlayıcı türü ve sözleşme girer, ilk filmlerde BAYRAK (öneriyle aynı). "Her zaman çalışır" değil: Gemini API anahtarı ve ücretsiz kota ya da dolar izni gerekir; KK1 yüzünden kullanıcıya sorulamaz, varsayılan dolar 0'dır. Yoksa izle-dinle bilgi paketi kullanıcıya gider | D-19, D-24 |
| EK1-2 Dikey kesit | uygulandı | Pilot dalga, dikey kesit ve GS0'ın ilk film bölümü tek aşama (A14a); ≈ 180 sn yayın kalitesinde; ek kredi yok | D-17, §1.3 |
| EK1-3 Kare paketinin göremediğini ölçen betikler | uygulandı | hareket hızı (V2), enerji eğrisi (T2), müzik tını/dinamik ölçüleri; MOS tahmincisi lisansı doğrulanınca (P2) | D-25, D-27d, §7 |
| EK1-4 İzle-dinle bilgi paketi | uygulandı | animatik ve dikey kesitten sonra; Telegram ya da masaüstü; hat beklemez | D-24, §8 |
| EK2-1 `zanaat.oyunculuk` + ifade sözlüğü + `ifade` zorunlu | uygulandı | ≈ 16 değerli filtre-güvenli sözlük | D-22, §5.1 |
| EK2-2 Duygu sürekliliği defterde | uygulandı | `duygu {durum, siddet, izler}`; K0 BAYRAK | D-22, §5.2 |
| EK2-3 Kör ifade okuması + seçim ölçütü | uygulandı | seçim sırasının 2. ölçütü | D-22 |
| EK2-4 Çoklu çekim (60–110 plan) | kısmen | Önce dikey kesitte ölçülür; değer görülürse en çok 60 plan (tahmin) ve ayrı take payıyla açılır. Neden: Flow kapasitesi ölçülmedi ([SA] K-1); 110 planlık ek yük ölçmeden alınamaz | D-23 |
| EK2-5 Canlı bekleme | uygulandı | Y06 daraltıldı; "holds the pose, breathing" Ö0-b A/B'siyle varsayılan olur | D-13 |
| EK2-6 `teslim` 12 değer | uygulandı | 4 LUFS sınıfına eşli | D-22, §5.1 |
| EK2-7 Sözsüz ses vuruşları | uygulandı | `tur: ses_vurusu` mikro adım | D-22 |
| EK2-8 Plan eleştirmenine 2 madde | uygulandı | — | D-22, §3 |
| EK3-1 Kanal teşhisi | kısmen | Ö0-g olarak yapılır ama ilk filmi bekletmez. Neden: veri OAuth ya da kullanıcının CSV'sini ister; KK1 gereği istenemez, ancak bilgi olarak önerilir. Sonuçlar kapak, başlık ve ritim önceliğini değiştirir | §1.2, D-24 |
| EK3-2 `yayin_analiz.py` | uygulandı | 48 sa / 7 gün / 28 gün; ders kaynağı `gercek_seyirci` | D-24, A18a |
| EK3-3 Kalibrasyon | uygulandı | panel ↔ gerçek tutma ilişkisi ilk üç filmde | D-19, D-24 |
| EK3-4 Erken uyarı | uygulandı | bilgi; değişiklik kullanıcının işi | D-24 |
| EK4-1 Müzik kalite kapısı | uygulandı | `dinleyici` varsa ikili karşılaştırma + yerel ölçüler; ilk filmde BAYRAK | D-25 |
| EK4-2 Kaynak merdiveni | uygulandı | `midi_ornek` yayında tema çalmaz | D-25 |
| EK4-3 Ses–yüz uyumu | uygulandı | `dinleyici` kör sorusu + 30 sn dinleme dosyası bilgi | D-19, §2.2 |
| EK4-4 Dönüşüm doğallığı (MOS) | kısmen | Lisanslı, Windows/CPU'da çalışan model doğrulanınca BAYRAK olarak (P2). Neden: lisansı ve uyumu bilinmiyor (O-5) | §6 |
| EK5-1 Yayın stratejisti ajanı | kısmen | Rol girdi ama ayrı ad açılmadı: `yayin-paketcisi` baştan yazılıp bu rolü alır. Neden: aynı dosyaların sahibi tek rol olmalı ([CM2] Ç-10); `juri-uyesi·youtube_stratejisti` ile ad karışıklığı önlenir | D-26, §3 |
| EK5-2 Kapak hattı (8–12 aday, küçük boyut, ikili seçim, gerçek kapakla ilk 2 dk) | uygulandı | "filmdeki kare" kuralı "filmdeki an" oldu | D-26 |
| EK5-3 Yayın sonrası kapak testi | uygulandı | kullanıcıya bilgi; kanalda açıklığı doğrulanacak | D-26 |
| EK5-4 Fragman ve Short | uygulandı | dikey kesitten fragman; dikey Shorts | D-26, §6 |
| EO1 Gösteri açığı | kısmen | Seyirlik anlar, süre istisnası, gösterisiz aralık BAYRAK uygulandı. Vitrin planlarında 1080p resmî API ancak kullanıcının dolar izniyle; varsayılan değil | D-27a |
| EO2 Aşırı açıklama | uygulandı | 2 soru, görsel taşıma oranı, klişe listesi; özet eşleşmesinde HATA yalnız kritik olgular | D-27b, §1.4 |
| EO3 Masa başı okuma | uygulandı | iş yaparken konuşma illüzyonu, söz kesme, cevap boşluğu ölçümü | D-27c |
| EO4 Hareket kalitesi | uygulandı | hareket hızı ölçüsü, canlı bekleme, canlı arka plan | D-27d, D-13 |
| EO5 Yaratık | uygulandı | kimlik kartı, davranış sözlüğü, evre olayı | D-28 |
| EO6 720p → 4K | uygulandı | büyütme kapısı + SFace; film görünümü; "4K" yalnız kapı geçerse | D-29 |
| EO7 Personalar + kapatma anı | uygulandı | izleme kiplerinde 2 A + 1 B; tahmini tutma eğrisi | D-18 |
| EO8 Kapı yığılması | uygulandı | kapı 7 + olgular / hedef 8; çapalama Ö0-f; aşama takvim kutusu (görev tavanı aşılırsa kâğıtta `yapimci·doktor` zorunlu) | D-20, D-08 |
| EO9 Enerji eğrisi | uygulandı | T2'de görüntü + ses + kesme yoğunluğu; T1'de yalnız ses | §7 |
| EO10 Yapımcı ekonomisi | uygulandı | aşamalı yatırım (Ö0 → kâğıt → animatik → kesit → kalan üretim); el işi saati `URETIM_ONIZLEME`'de | §1.6, D-06 |

KÜÇÜK maddeler: EÇ3 (parti başına ≥ 2 imza plan, tahmin; plan eleştirmeni listesine), EÇ4 (parti başına ≥ 1 nefes ya da mizah anı, tahmin; küçük güzel sahneyle
birleşebilir), EÇ5 (Y/CY planlarda nefes ve kumaş katmanı, diyalogdan 18–24 dB aşağı, tahmin), EÇ6 (dikey Shorts), EÇ8 (≥ 2 sahnede görünen figürana
mini kart), EÇ9 (kart adaylarında küçük boyut kör ikili karşılaştırma) uygulandı; EÇ1 (yapı varyasyonu) ve EÇ2 (ilk 30 sn'de kapak yankısı)
BAYRAK olarak uygulandı; EÇ7 (ikinci dil ses izi) ilk iki filmden sonraya bırakıldı (§10.4).

**Şeytanın avukatı ([SA])**

| Madde | Karar | Nasıl / neden | Yer |
|---|---|---|---|
| K-1 Flow kapasitesi ölçülmemiş, tek hesap | uygulandı | Ö0-b 3 gün ölçümü; takvim ölçülen kapasite alt sınırından; kapasite ya da takvim yetmezse 30 dk; Vertex fiyatı Ö0'da; hesap değiştirme yasağı ve kodu | §1.2, D-03, D-04, D-05 |
| K-2 "Yalnız konu" iş yüküyle delinmiş | uygulandı | kullanıcı sözleşmesi kartı; tek `IZINLER.bat` (soru değil); el işi saati ölçülür ve gösterilir (sabit "≤ N saat" tavanı konmadı: N'nin kaynağı yok); Gemini API Ö0-e; DUR sonrası ekip varsayılanı; "elle dinleme" tasarımdan çıktı | D-06, D-07, §8 |
| K-3 Token bütçesi yok | uygulandı | kullanım kaydı, aşama tavanı + BEKLE, karar 6 testi, kısmi izleme ikinci filmde A/B, erken projeksiyon | D-08, D-09, D-18 |
| K-4 Temeller ölçülmeden P0 | uygulandı | Ö0-a…h; P0 listesi yerel aşamalar için Ö0'dan sonra kesinleşir | D-01, §9 |
| K-5 Kalibrasyonsuz kapılar | kısmen | (1) "gölge kip" yerine kapı 7 + olgular / hedef 8: puan tamamen gölgeye alınmadı, çünkü kullanıcının "süper" dediği düzeyin (7) altındaki film video kredisine geçmemeli; (2) seyirci güvenilirliği Ö0-f; (3) zorunlu kaynak alanı; (4) küresel geri dönüş bütçesi; (5) iki yönlü kalibrasyon — uygulandı | D-20, D-33, D-34, §1.5 |
| K-6 Depodaki kod KK5'i çiğniyor | uygulandı | PR-0, memmet3'ten bağımsız; korkuluk testi CI'da zorunlu | D-02, §9 |
| O-1 Bütünleştirici yok | uygulandı | bu belge karardır; `ADLAR.json` + `test_adlar.py` | D-35 |
| O-2 Sahipsiz işler | uygulandı | `renk_cila.py`, `shorts_mp4.py`, `jenerik.py`, kapak üretimi, YZ beyanı, memmet3 aktarımı, B3 etiketleri, torch kararı, kullanıcı belgeleri, token ölçümü, kapasite ölçümü, lisans defteri, Gemini kotası, izin kartı, `durdu` planın karşılığı — hepsinin sahibi §6'da | §6 |
| O-3 Kurulum karmaşık | uygulandı | K1/K2/K3 kademeleri; CPU torch | D-37 |
| O-4 Bulut/yerel | kısmen | Üretim yerelde, `esitle` P2 — uygulandı. Tek kök reddedildi (veri klasörünü git deposu yapmak sızıntı riskini büyütür) | D-12 |
| O-5 Lisans zinciri | uygulandı | `LISANSLAR.json`; "bilinmiyor" ana hatta kurulmaz | D-36 |
| O-6 Karar 2/3 B düzeyinde | uygulandı | (a) H'ye yükselme yolu, (b) yaratık kimlik bankası, (c) son kare referansı A/B, (d) ilk filmde sıkılaştırıcı deneme dersleri | D-28, D-15, D-33 |
| O-7 Sesin kulağı yok | kısmen | `dinleyici` varsayılan açık olamaz (anahtar/dolar; KK1); yerine dinleme dosyası bilgi olarak, itiraz `film-not` ile | D-19, §2.2 |
| O-8 Aynı model yazıyor ve yargılıyor | kısmen | Farklı aileden `izleyici` (BAYRAK) + personalar; panel ilk filmlerde Claude kalır; puan kapısının kalkması ilk üç filmin tutma ölçümüne bağlandı | D-18, D-19 |
| O-9 Animatik G1'den sonra | uygulandı | tur 1 düzeltmelerden önce | D-14 |
| O-10 Sayılar tutarsız | uygulandı | `olcek.py` tek araç | §1.6 |
| O-11 Disk | uygulandı | disk kapısı + arşiv | D-38 |
| O-12 Gece üretimi Claude'a bağlı | uygulandı | oturum öncesi hazırlık; ardıllar sonraki bloğa | D-39 |
| O-13 YouTube kuralları | uygulandı | `yz_beyani` + politika listesi | D-40 |
| O-14 Karar 6 aşırı yorumu | uygulandı | karar 6 testi | D-09 |
| O-15 Çıplak `python` | uygulandı | mutlak yol `settings.local.json`'da; kurulum testi | D-11 |

KÜÇÜK maddeler: S-1 (`atomik_yaz` 3 kez yeniden dener), S-2 (tek `kanca.py`), S-4 (adlar), S-6 (yükleme varsayılan kapalı), S-7 (Telegram anahtar
dosyasının yalnız tarihi denetlenir), S-8 (git ön koşul denetimi), S-9 (`DEVAM.bat` tek tanım), S-10 (medyan + ad sızıntısı) uygulandı. S-3 kısmen:
soru kapısı ilk günden **engeller** (KK1'in uygulayıcısıdır; yanlış pozitifin bedeli Claude'un cümleyi yeniden yazması kadar küçüktür) ama kanca 50
örnek mesajlık Türkçe test seti CI'da geçmeden birleştirilmez. S-5 kısmen: tek sürüm numarası ve güncelleme sonrası test uygulandı; otomatik
güncelleme güvenlik düzeltmeleri yüzünden kapatılmadı.

### 2.4 Uzmanlar arası çelişkiler: kararlar
| # | Konu | Taraflar | Karar | Gerekçe |
|---|---|---|---|---|
| Ç1 | Klasör adları | [YN2] `30_YONETMEN/`, [SM2] `35_SES/` · [CM2] `_YONETMEN/`, `_SES/` | `_HIKAYE_ODASI/`, `_YONETMEN/`, `_SES/`, `_KARTLAR/`, `_RAPOR/`, `_GOREV/`, `KUYRUK/`, `kararlar/` | alt çizgi makine/iş klasörünü ayırır; sıra aşama kodundadır; mevcut kod `_RAPOR/` kullanıyor |
| Ç2 | `memmet-bakimci` yetkisi | [UM2] kaynağa yazar · [CM2] aday yama | aday yama + `memmet_yama.py` korkuluk testi; kaynağa yalnız testten geçen yama betikle uygulanır | KK5'e en yakın olan |
| Ç3 | Derslerin ajana verilişi | [UM2], [GS2], [SN2] kanca/brifing · [CM2] GIRDI | yalnız `GIRDI/DERSLER.md`, imzaya girer; SubagentStart yalnız 2 sabit satır ekler | girdi imzası ve tekrarlanabilirlik |
| Ç4 | Ders defterinin yeri | [UM2] `BILGI/DERSLER/ham/` · [GS2], [SN2] başka adlar | `<veri>/BILGI/DERSLER/ham/<zaman>_<film>_<olay>.json` | olay başına dosya, birleştirme çakışması yok |
| Ç5 | Aşamalı okuma | [CM2] SubagentStop · [SN2], [KU2] SendMessage | Ö0-a ölçer; sıra SubagentStop → SendMessage → bölüm başına görev | davranış doğrulanmadı |
| Ç6 | Repliğin ton alanı | [YN2] `ton_fiili` · [SN2], [SM2] `teslim` | yazılan alan `replik.teslim` (12 değer); `_derlenir.ton_fiili_en`, `seviye`, `tts_etiket` sözlükten | tek yazar, tek sözlük; 3'e 1 |
| Ç7 | Son kare zinciri karesinin boyutu | [YN2] 1376×768'e Lanczos · [GS2] doğal 1280×720 | doğal 1280×720; 1376×774 + 3 px kırpma Ö0-b'de kıyaslanır | yeniden örnekleme oranı bozar (%0,8) |
| Ç8 | Kurulumda soru | [UM2] Q9 · [CM2] İ-9 | soru yok; `IZINLER.bat` kullanıcının kendi isteğiyle | KK1 |
| Ç9 | `DEVAM.bat` | [UM2] `film.py calis` · [CM2] `claude --continue "devam"` | `claude --continue "devam"` (doğrulanacak); çalışmazsa `FILM_SETI.bat` açılır ve kullanıcı "devam" yazar | görev defteri ana Claude'dan yürür |
| Ç10 | En düşük Claude Code sürümü | 2.1.271 · 2.1.302 | 2.1.302 (doğrulanacak) | kancaların kullandığı alanlar yeni sürümde |
| Ç11 | Gözlem sağlayıcısı | `vlm` · `gozlemci` | `gozlemci` | Türkçe ad kuralı |
| Ç12 | Kör gözlemci ajanı | `kor-gozlemci` · `kare-tarifcisi` | `kare-tarifcisi` | kadro 21 ([CM2]) |
| Ç13–15, 19–20 | Düzeltme hacmi, paket sayısı, gece varsayımı, görev sayısı, klip sayısı | çeşitli | `olcek.py` hesaplar, aralık verilir; takvim `elle` moda göre hesaplanır (gece varsayılmaz) | tek kaynak |
| Ç16 | KRİTİK reddi | doktor/hakem · dört şart | dört şart | D-21 |
| Ç17 | Z0/Z1/Z2 adları | [GS2] · [UM2] | kodda `bagimsiz`, `son_kare`, `bitis_sabit`; belgede "bağımsız / son kare zinciri / bitiş sabitleme" | ZN kapı adlarıyla çakışmasın |
| Ç18 | Kadro sayısı | 15 + 1 · 21 | 21 | §3 |
| Ç21 | Kare zinciri varsayılanı | [UM2] C5 Bitir · [YN2], [GS2], [KU2] son kare | son kare zinciri (yalnız `devam`); Bitir hedefli | D-15 |
| Ç22 | Yayın kaynağı | [UM2] C9 ffmpeg master · KR satır 48 | CapCut dışa aktarımı; master yalnız Ö0-d başarısızsa | kullanıcının kayıtlı kararı |
| Ç23 | "Aynı projede" ↔ klon | [CM2] `film-not` · [KU2] | klon, yeni adla listenin en üstünde | kaynak taslağa yazmak DR'ye aykırı |
| Ç24 | S3.6 ve S3.8 | [SM2] · [KU2] | `kurgu_denetim.py` | çizelge aritmetiği |
| Ç25 | Kesme oranının paydası | RE · [KU2] İ-6 | simülasyondan HATA'sız geçen öneriler | zararlı kesme zorunlu olmasın |
| Ç26 | Bulgu ↔ olgu eşlemesi | [SN2] betik · [KU2] İ-5 | `ozet-eslestirici·bulgu` eşler, `bulgu_yonlendir` sahibi seçer | anlam işi betikte güvenilmez |
| Ç27 | Kuyruk ve rapor yeri | çeşitli | `KUYRUK/YENIDEN_URET.json`, `KUYRUK/YENIDEN_YAZ.json`; raporlar `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json` | — |
| Ç28 | Zincir karesi kapısının adı | [UM2] `ZK` · [GS2] `G1Z` | `G1Z`; "K1-ön" dosya adlarında `K1ON` | kapı ailesi G1 ile aynı ölçüler |
| Ç29 | Telaffuz ↔ kart sırası | [UM2] kartlardan önce · [GS2] kart ad içermez | telaffuz yerelin ilk işi; kart kimlik dizesi ad içermez, ad değişirse yalnız istem ve altyazı yeniden derlenir | ikisi birlikte |
| Ç30 | GS0 karşılaştırma klipleri | [GS2] ≈ 120 kr · [UM2] ek kredi yok | Ö0-b'ye (B3 planları) taşındı | D-17 |
| Ç31 | CC0 efekt indirme | [SM2] açık · [UM2] kapalı | varsayılan kapalı, `IZINLER.bat`; kapalıyken eksik efekt BAYRAK + ders + bilgi | KK1, dış indirme izni |
| Ç32 | Gemini ikinci göz | [GS2] varsayılan açık (kullanıcı paketi) | yalnız API ile; kullanıcı paketi yok | [SA] K-2 |
| Ç33 | Kart biçimi | BK §8 #19 belirsiz | açık gri düz fonda birleşik kart sayfası (tam boy ön + 3/4 + 2×2 yüz paneli + tam boy arka) | [GS2] GS3; yeşil fon kıyası yapılmadı (§10) |
| Ç34 | Ses tasarımının sırası | [YN2] Y6'dan sonra Y7'den önce | A08 istem derlemeden (A09) önce | `Sound:` cümlesi `flow_sound`'dan derlenir |
| Ç35 | İlk 2 dk testinde kapak | [SN2], [KU2] tarif · [ESY] görsel | kâğıtta tarif, animatik ve kurguda görsel | kapak görseli A11'de doğar |
| Ç36 | `ifade` alanı | [YN2] isteğe bağlı · [ESY] zorunlu | insanlı planda zorunlu ("notr" gerekçeli) | D-22 |
| Ç37 | Klip süresi | RE `klip_sn` [8, 10] · [UM2] Q3 10 sn fiyatı bilinmiyor | varsayılan 8 sn; 10 sn yalnız Ö0-b fiyatı ölçtükten sonra vitrin ve uzun duygu tutma planlarında | fiyat bilinmeden bütçe kurulamaz |
| Ç38 | Replik kelime sınırı | `istem_denetim` 20 · ZN 8 sn'de 16 | 8 sn klipte ≤ 16 (RE `replik_max_kelime_8sn`), 10 sn klipte ≤ 20 (RE `replik_max_kelime`) | ZN konuşma hızı |
| Ç39 | Konuşan karakter | `hikaye-mimari` taslağı "en çok 4" · RE 8 | ana karakter ≤ 4, konuşan ≤ 8 | RE `konusan_karakter_max` |
| Ç40 | `maxTurns` | [CM2] 100/60/60 · sahipler 80 | yazar 100 (yönetmen, hikâye yazarı, kurgucu 80), denetçi 60, kör 60, `kare-tarifcisi` 40 | sahibin değeri; hepsi tahmin |

### 2.5 Belgelerde yapılacak düzeltmeler (PR-1 içinde)
- **ZN §2.6:** "Bütçe yetmezse … film kısaltılır" → "Bütçe yetmezse süre hikâye yazılmadan önce seçilir; yazılmış film kısaltılmaz."
- **ZN §3.7:** "takes two slow steps" → "walks two slow steps" (take yasak sonuç fiilidir).
- **ZN §5.1:** ambiyans kaynağı "demucs ile ayrılmış Flow ortamı" çıkar; yatak yalnız gerçek kayıttan.
- **ZN §6.2:** `RAPORLAR/<kapi>_<parti>.json` → `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json`.
- **ZN §7.3:** seyirci girdi listesinden `ekranda_bilgi` ve "önceki filmlerin izleyici özeti" çıkar; kurgu kare paketi tarifi [KU2] §4.5.4 biçimine;
  kesme turu cümlesine "simülasyondan HATA'sız geçen önerilerin" eklenir.
- **`arastirma/02_sureklilik.md` §2.3:** `-sseof` teknik son kare komutu → "kurguda kullanılan kesme anındaki kare" (D-15).
- **RE:** her anahtara `kaynak` ve `etiket` alanı; `kesme_turu_oneri.aciklama`'ya payda tanımı; yeni anahtarlar §7.
- **BK §5.3.3'e uygulama notu** (kural kullanıcınındır, değişmez): "Taslak yeniden kurulmaz" klonla uygulanır (D-30). **BK §6.2 #8'e uygulama
  notu:** "ikinci hesap" ve kie.ai seçenekleri KK5 gereği kullanılmaz (D-03).
- **Kök `CLAUDE.md`:** "İlk iş: PAKET.zip'i aç" satırı bayattır (zip e962e6a'da açıldı); [CM2] §4.4.7'deki ≤ 45 satırlık akış metni yazılır; geliştirme
  listesi `YZ_FILM/ARACLAR/CLAUDE.md`'ye taşınır.

### 2.6 Kesin kararların uygulanışı (özet)
| Kesin karar | Uygulanışı | Kalan sınır |
|---|---|---|
| KK1 Yalnız konu sorulur | tek soru metni (§4.1); `kanca.py stop` soru kapısı; bütün kararlar `film.py karar ekle` ile deftere; izinler varsayılan kapalı ve `IZINLER.bat`; kullanıcı sözleşmesi kartı; bilgi mesajları | fiziksel işler kalır (§8); sayıları baştan yazılır |
| KK2 Atomik eylem zinciri | D-13; fiil sözlüğü, `plan_sema`, `plan_denetim` (Y01–Y60), `istem_derle --hareket`, V3 | saniyeli uyum Ö0-b ve dikey kesitte ölçülür |
| KK3a Animatik + habersiz seyirci | A12; D-14; `animatik: ONAYLI` imzası video girdisinde | kare paketi izlemek değildir; `izleyici` ve dikey kesit tamamlar |
| KK3b Dünya defteri + zıplama denetimi | D-43; K0, Y58, K1; duygu katmanı | — |
| KK3c Referansla yüz kontrolü | D-16; G1, G1Z, V2, K1; kimlik bankası; yaratık D-28 | yaratık ve parmak ilk filmlerde çoğunlukla BAYRAK |
| KK3d Kare zinciri | D-15; `kare_zinciri.py`, G1Z, KR5 kilidi | yalnız `devam` geçişinde son kare; diğerlerinde kamera ağacı türevi |
| KK3e Öğrenen ders defteri | D-33; olay kaydı her kapıda; `ders-editoru`; gerçek seyirci kaynağı (D-24) | terfi ≥ 2 film; ilk filmde yalnız sıkılaştırıcı deneme |
| KK3f Seri evreni kütüphanesi | D-42; `evren.py`; kartlar, sesler, kroki, leitmotif, kalibrasyon | görseller git'e girmez (yerel + D yedeği) |
| KK4 Ses/dudak | §2.2 | motor Ö0-c ile seçilir; B planı yazılı |
| KK5 Memmet, bot tespiti, uyarıda DUR | D-02, D-03, D-04, D-39; `elle` varsayılan; korkuluk testi; `UYARI_GECTI.bat` şartları | Flow kapasitesi takvimi belirler; atlatma yoktur |
| KK6 Üstün körü iş yok | ÖLÇÜLEMEDİ GEÇ değildir; 2 aday + tam G1; tam film izleme; ölçülmeden kısma yok (karar 6 testi); bütçe yetmezse hat bekler, kalite düşmez | — |

## 3. Ajan kadrosu

### 3.1 Kadro ilkeleri (hepsine uygulanır)
1. **21 ajan**, üç rol ([CM2] §4.3.1): **yazar** (sahip olduğu dosyayı yazar ve revize eder) `tools: Read, Write, Edit, Glob, Grep` · **denetçi**
   (içerik üretmez, kör değildir) `tools: Read, Write, Glob, Grep` · **kör** (her turda yeni örnek, yalnız GIRDI) `tools: Read, Write` +
   `omitClaudeMd: true`. Hiçbir ajanda `Bash`, `Agent`, web aracı ve `memory:` alanı yoktur.
2. Hepsi `model: opus` (claude-opus-5-5), `effort: high`, `permissionMode: acceptEdits`. `fallbackModel` yazılmaz. Daha ucuz yapılandırma yalnız
   karar 6 testiyle (D-09). `maxTurns`: yazar 100 (yönetmen, hikâye yazarı, kurgucu 80), denetçi 60, kör 60, `kare-tarifcisi` 40 (hepsi tahmin).
3. **Açıklama kalıbı:** "<Rol>. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler: …". Claude ajanı kendiliğinden
   seçmez; `kanca.py ajan` kadro dışı tipi, fork'u ve yerleşik ajanları reddeder. 21 açıklamanın toplamı ≤ 3.000 token (`beceri_denetim.py`).
4. **Gövde kalıbı:** rol cümlesi → **KESİN KURALLAR** (aşağıda her ajan için verilen ilk satırlar; davranış kuralı burada durur, `reference/`'ta
   değil) → "Çağrıldığında" adımları (önce `GOREV.json`'u oku; yalnız orada yazanı yap) → kontrol listesi (GIRDI'deki kopyadan) → çıktı sözleşmesi.
5. **Çıktı sözleşmesi:** `CIKTI/` altında önce başlıklar, sonra bölüm bölüm doldurma; şemalı `.json` (`semalar/`); `.md`'nin son satırı sabit
   `OZET | …`; ana oturuma ≤ 5 satır (çıktı yolu + OZET). Puanı mesajdan değil dosyadan betik okur. SubagentStop doğrulaması HATA verirse aynı ajana
   en çok 2 düzeltme döner.
6. **Sayılar şablondan:** ajan istemleri `sablonlar/<ASAMA>_<ajan>[_<kip>].md`'den betikle üretilir; eşikler yer tutucuyla eşik dosyalarından basılır;
   ajan gövdesine sabit sayı yazılmaz. Dersler yalnız `GIRDI/DERSLER.md`'den gelir; kör rollere ders verilmez.
7. **Yeni ajan ölçütü:** ancak ayrı bir dosyanın tek sahibi ya da ayrı kör girdili bağımsız değerlendiriciyse; değilse mevcut ajanın kipi
   ([CM2] Ç-10).

### 3.2 Mevcut 8 taslağın akıbeti
| Taslak | Karar | Neden |
|---|---|---|
| `habersiz-seyirci.md` | **kalır, güncellenir**: `Read, Write`, `omitClaudeMd`, 6 kip, 6 ölçüt + GENEL, aşamalı okuma, personalar | `Glob` var, 3 ölçüt + ortalama, CLAUDE.md okuyor |
| `hikaye-mimari.md` | **kalır, güncellenir**: 10 başlıklı öneri, sayılar şablondan, v2 yok | "≈ 80–100 klip/parti" ZN ile, "en çok 4 konuşan" RE `konusan_karakter_max` 8 ile çelişiyor |
| `istem-muhendisi.md` | **depodan kaldırılır** (git geçmişinde kalır) | istemi elle yazıyor; yerine `istem_derle.py` + `yonetmen·onarim` + `duzeltme.py` |
| `muzik-supervizoru.md` | **depodan kaldırılır** | `sonnet`; yerine `ses-tasarimcisi·muzik` |
| `sureklilik-denetcisi.md` | **baştan yazılır** | `sonnet`; beklenen listeyi görerek karar veriyor; kuyruğu kendisi yazıyor |
| `uretilebilirlik-denetcisi.md` | **güncellenir**: `juri` ve `plan` kipleri, kredi hesabı yok | LLM ile "%25 pay" kredi hesabı; atomik zincir ve el/parmak denetimi yok |
| `yayin-paketcisi.md` | **baştan yazılır**: yayın stratejisti rolü (D-26) | kapağı "kullanıcı seçer"; bölüm ve Short kuralı yok; başlık yazıyor |
| `yonetmen.md` | **baştan yazılır**: 5 kip, sahne grubu başına görev, istem kodla | atomik zincir yok; istem yazıyor; 495 planı tek çağrıda yazmaya kalkıyor |

Yeni 15 ajan: `yapimci`, `hikaye-yazari`, `kart-tasarimcisi`, `ses-tasarimcisi`, `kurgucu`, `ders-editoru`, `memmet-bakimci`, `juri-uyesi`,
`diyalog-editoru`, `hat-denetcisi`, `ozet-eslestirici`, `oyuncu`, `kare-tarifcisi`, `kesici`, `plan-elestirmeni` (kalan ve baştan yazılan 6 taslakla
birlikte toplam 21). Kalkan ya da birleşen adlar: `plan-yazari` (→ `yonetmen·plan`), `senarist` (→ `hikaye-yazari`), `konu-analisti`,
`hikaye-doktoru` (→ `yapimci`), `evren-arsivcisi` (→ `hikaye-yazari·evren`), `anlama-olcer` (→ `ozet-eslestirici`), `kor-gozlemci`, `vlm-denetci`
(→ `kare-tarifcisi`), `kurgu-seyircisi` (→ `habersiz-seyirci` izleme kipleri), `ses-kadrocusu`, `ses-denetcisi` (→ `ses-tasarimcisi·kadro` +
`ses_karar.py`), `ders-katibi` (→ `ders-editoru`), `yayin-stratejisti` (→ `yayin-paketcisi`).

### 3.3 Yazarlar (10)

**`yapimci`** · yeni
```yaml
---
name: yapimci
description: Filmin yapımcısı. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler konu (konu kartı, süre önerisi, eksenler, varsayımlar, "sen seç") ve doktor (tıkanan kapıda yapısal teşhis, tek seyircinin KRİTİK'ini kanıtla değerlendirme). Hikâye ve replik yazmaz.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Kullanıcıya soru yazmazsın; belirsizlikte varsayım yap ve `01_VARSAYIMLAR.md`'ye 'karar — neden — yanlışsa maliyeti' diye yaz. Süreyi
  GIRDI/B0.json'daki üst sınırın üstünde öneremezsin. Hikâye yazmazsın."
- **Görev sınırı:** seri tespiti (devam/yeni; eski seri ancak adıyla anılırsa), tür ve kanca ailesi, vaat imgesi taslağı, risk taraması (çocuk kahraman
  → yetişkin ya da dolaylı; şiddet; telif; Flow'da zayıf işler), süre önerisi, eksenler (yeni seri D/S/E + X; devam A/B/S + X), "sen seç" kipinde 3 konu
  adayı × 4 ölçüt. **Doktor:** tur tıkanınca yapısal teşhis ve D-21 şartlarıyla KRİTİK reddi.
- **Okur (GIRDI):** `00_KONU.md`, evren özeti, `KANAL_TESHIS.md` özeti, `B0.json`, tür–kanca tablosu, `DERSLER.md`; doktor kipinde tur raporları,
  `HIKAYE.json` dilimi, ilgili kopukluk ve seyircinin paket sayfaları.
- **Çıktı:** `01_KONU_KARTI.json`, `01_VARSAYIMLAR.md`; doktor kipinde `08_DOKTOR_<tur>.md`, `KRITIK_RED_<kip>_t<n>.json`.

**`hikaye-mimari`** · güncellenir
```yaml
---
name: hikaye-mimari
description: Hikâye mimarı. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; verilen eksende (D/S/E/X, seri devamında A/B/S/X) 10 başlıklı film önerisi yazar. Diğer önerileri okumaz, ikinci sürüm yazmaz.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Yalnız GIRDI'deki brifingi ve eksen satırını kullan. X ekseninde öbür loglinelar yalnız kaçınılacak yollardır. Filtre kelimesi ve yaş
  ifadesi yazma."
- **Görev sınırı:** 10 başlık ([SN2] H3: logline EN ≤ 35 kelime + TR; başlık × 3 + kapak imgesi; ≤ 4 ana, ≤ 8 konuşan karakter; dönem + 3–5 kural + NE
  YOK; 3 parti tek cümle + vuruşlar; soğuk açılış + ilk 2 dk; merak ≥ 8, kurulum ≥ 5, parti başına ≥ 1 ironi ve ≥ 1 küçük güzel sahne; seri kancası;
  üretilebilirlik notu; parti başına ≥ 2 seyirlik an).
- **Okur:** `00_BRIFING.md`, ISTEM.md'deki eksen satırı. **Çıktı:** `02_oneri_<eksen>.md` + `02_oneri_<eksen>.json`.

**`hikaye-yazari`** · yeni
```yaml
---
name: hikaye-yazari
description: Filmin hikâye yazarı ve replik metninin tek sahibi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler yapi, senaryo, revizyon, dar_degisiklik, evren, replik_kabul (her seferinde yeni örnek).
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 80
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Ekran metni yalnız görülen ve duyulan olaydır; iç durum fiili (realizes, decides, remembers, knows) ve sonuç fiili yazma. Replik ≤ 16 kelime
  (10 sn klipte ≤ 20), tek konuşan, filtre kelimesi yok; her replikte `tasidigi` doldur. Konuşma ile el işi aynı satırda olmaz. İlk replik ekranda,
  ağzı görünürken."
- **Görev sınırı:** 3 parti × 8 başlık yapı; senaryo (EKRAN + KÂĞIT blokları, R0001… kimlikleri, iki soğuk açılış sürümü); bütün revizyonlar; H15 dar
  değişiklik merdiveni; evren taslağı; `replik_kabul` kipinde Veo'nun söylediği metni kabul ya da ret (`{karar, gerekce}`); `seyirlik_anlar`,
  `ic_durum` ve `alt_metin` sahne notları; başlık adayları × 3, kapak imgesi, bölüm adları, Short adayları.
- **Okur:** brifing, kazanan öneri, `04_SECIM.json`, önceki sürüm + değişiklik tablosu, kendine yönlenen bulgular, oyuncu ve diyalog raporları,
  `DERSLER.md`, `yazar_defteri.md`, evren hikâye kaydı; `replik_kabul`'de yalnız replik, sahne metni, duyulan metin ve `tasidigi`.
- **Çıktı:** `05_YAPI.json`, `06_SENARYO_v<N>.json` + `.md`, `DEGISIKLIK_v<N>.md`, `EVREN_TASLAK.json`, `REPLIK_KABUL.json`, `yazar_defteri.md`.

**`yonetmen`** · baştan yazılır
```yaml
---
name: yonetmen
description: Filmin yönetmeni. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler harita (parti sözleşmeleri, kroki, kurulumlar), plan (bir sahne grubunun atomik eylem zinciri ve oyunculuğu), onarim, kart_secimi, ders. İstem yazmaz, replik metnine dokunmaz.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 80
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "YZ'ye sonuç söylenmez ('kalemi al' yok). Her planda 2–3 adım; konuşma bir adımdır. Adım = [bas–bit sn] + sözlükten tek fiil + vücut
  parçası + karakterin KENDİ sağı/solu + hedef + ölçü + el şekli; `etki` yaz. Durum yalnız olgudur; kadraj konumu, bakış yönü ve ışık yönü yazma, kod
  hesaplar. İnsanlı her planda `dis_ifade` yaz. İstem yazmazsın; replik metnine dokunmazsın (bölme ve zamanlama serbest)."
- **Görev sınırı:** harita (plan hedefi, kalıp, eksen, kamera tarafı, ekran yönü, ışık, yasaklar, kurulumlar, sahne uç durumları), kroki ve kurulumlar
  (mekân başına, ilk kullanımda; değişiklik yeni sürüm), `KART_ISTEGI.json`, sahne grubu planları (`zanaat`, `oyunculuk`, zincir niyeti), onarım
  (animatik, G1 kaçışı, V3, kurgu yeni planı, filtre reddi), kart sanat seçimi, ders önerisi. Sahne süresi ±%20; sahne sınırı, sırası ve silme
  `hikaye-yazari`'nın işidir (`sahne_degisiklik_istegi`).
- **Okur:** sözleşme, kroki PNG + kurulumlar + `yasak_ardisik`, EKRAN metni + replik kimlikleri + `teslim`, önceki sahnenin son 2 planının çözülmüş
  bitişi, `PLAN_DILI.md`, `plan_sozlukleri.json`, `fiil_sozlugu.json`, `ifade_sozlugu.json`, `DERSLER.md`; onarımda ilgili rapor ve kareler.
- **Çıktı:** `_YONETMEN/HARITA_P<n>.json` + `.md`, kroki önerisi, `KART_ISTEGI.json`, `PLANLAR/S<k>.json`, `ONARIM_<id>.json`, `KART_SECIM.json`,
  `DERS_ONERI.md`.

**`kart-tasarimcisi`** · yeni
```yaml
---
name: kart-tasarimcisi
description: Seri evreninin görsel tarifçisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; karakter, kostüm, yaratık, mekân ve nesne kartlarının tarifini (kimlik dizesi, asimetrik ayrıntılar, varyantlar, ölçek) yazar. Koordinat yazmaz, kart seçmez.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Kimlik dizesi (`kimlik_en`) ad içermez, ≤ 45 kelime (tahmin), yaş rakamı yok; asimetrik öğe BÜYÜK HARFLE LEFT/RIGHT ve karakterin kendisine göre.
  Hikâyeye bağlı öğeyi değiştiremezsin; gerekiyorsa `GORUNUS_DEGISIKLIK_ISTEGI.json` yaz. Stil ekine ışık ifadesi yazma."
- **Görev sınırı:** kadro ayrışması (siluet, saç rengi, kostüm rengi), kostüm varyantları ≤ 2, `boy_m`, `goz_yuksekligi_m`, `baskin_el`, yaratık evreleri
  boy benzetmesiyle ve ≥ 3 sabit asimetrik işaretle (D-28), mekân tarifi + nötr durum + plaka istekleri, nesne ölçek kartı, tekrar eden figüran mini
  kartı.
- **Okur:** `HIKAYE.json` karakter kartları (`gorsel_ayirt_edici`, `hikaye_baglayici`), `KART_ISTEGI.json`, evrenin kilitli kartları, `dunya.json`,
  `DERSLER.md`. **Çıktı:** `_KARTLAR/KART_SPEC.json`, `GORUNUS_DEGISIKLIK_ISTEGI.json`.

**`ses-tasarimcisi`** · yeni (`muzik-supervizoru`'nun yerine)
```yaml
---
name: ses-tasarimcisi
description: Filmin ses tasarımcısı. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler kadro (ses profilleri; puan farkı küçükse ses seçimi), tasarim (bir sahne grubunun efekt, ambiyans ve sessizlik planı), muzik (leitmotif notaları ve ipucu listesi). Sesi duyamaz; ölçüye göre karar verir.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
```
- **İlk satırlar ([SM2] 8 kural):** "Sesi duyamazsın; yalnız ölçü tablolarına ve tariflere dayan. `veo_ses_tarifi` ≤ 12 kelime: perde/tını + cinsiyet +
  aksan; yaş sözcüğü yok. `flow_sound` 'Sound: … No music.' biçiminde, arası ≤ 12 kelime. Ambiyansa müzik modeli kullanılmaz. Ses yolunu kod önerir;
  değiştirirsen `yol_neden` yaz. Müzik sözsüzdür; istemde sanatçı ve film adı yok. Replik metnine dokunmazsın. Kullanıcıya soru yazmazsın."
- **Görev sınırı:** profil (cinsiyet, arama için yaş bandı, ElevenLabs sözlüğünden aksan, perde, tını, tempo, enerji, `ses_etiketi_tr`); ses seçimi
  (yalnız puan farkı < 0,03 iken); sahne grubu tasarımı (adım kimliğine bağlı efektler, tek yatak + defterden katmanlar, oda yanıtı, sessizlikler,
  `flow_sound`); müzik (motif notaları, ton/mod, BPM, ölçü, çalgı, dönüşümler; ipucu giriş/çıkışı olaya bağlı; İngilizce istem "no vocals").
- **Okur:** kadro: karakter kartları (`ses_karakteri`, `ad_telaffuz`), aksan sözlüğü, ölçüm tablosu; tasarım: `ses_plani` taslağı, sahne grubunun
  planları, defter dilimi, `DIZIN.json` özeti; müzik: duygu haritası, vuruşlar, sahne listesi, evren leitmotifleri.
- **Çıktı:** `_SES/SES_PROFILLERI.json`, `SES_KADROSU.md`, `SES_SECIM_GEREKCE.md`; `_SES/SES_<S>.json`, `EKSIK_EFEKTLER.json`; `MUZIK/muzik_listesi.json`,
  `leitmotifler.json` taslağı.

**`kurgucu`** · yeni
```yaml
---
name: kurgucu
description: Filmin kurgucusu. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler duzelt (bulgu → kurgu işlem listesi), kirp_incele (güveni düşük kırpmalar), sifir_kredi (kredili maddeden önce 0 kredi çözümü), not (kullanıcı notu ve CapCut düzenlemesi). KURGU_PLANI'nı elle değiştirmez.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 80
permissionMode: acceptEdits
---
```
- **İlk satırlar ([KU2] §4.3):** "Kural sırası: duygu > hikâye > ritim > göz izi > 2B > 3B. Önce 0 kredi merdiveni; kredili çözüm ancak merdiven tükenince
  ve gerekçeyle. İşlem listesini `CIKTI/KURGU_KARARLARI.json`'a yaz; doğrulamayı sistem yapar. `kaynak: kullanici` olan kırpma ve sırayı asla geri alma.
  Dudağı oynayan karakterin üstüne başkasının repliğini koyma. Durumu değiştiren planın sahne içi sırasını değiştirme. Her işleme `kok_neden` ve bulgu
  kimliği yaz. Bir seyircinin KRİTİK'ini geçersiz sayamazsın."
- **Görev sınırı:** kırpma, sahne içi sıra, J/L, ekran dışına taşıma, kart, hız, ayna, yeniden kadraj, örtü, sahne içi plan kesme; yeni plan ve yeniden
  çekim için yalnız **gereksinim** yazar (istem yazmaz); `durdu` plana zorunlu 0 kredi çözümü.
- **Okur:** `KURGU_PLANI` dilimi, seyirci karar ve ilgili raporları, bulgu yönlendirmesi, `Z3`, `K1`, `K1ON`, `V2V3`, `S3` özetleri, `SAHNELER.json`
  dilimi, olay listesi, ZN §2–§5 dilimi, `URETIM_ONIZLEME` dilimleri, `MERDIVEN.md`, `DERSLER.md`; not kipinde `NOTLARIM.json`, `TASLAK_FARK.json`.
- **Çıktı:** `KURGU_KARARLARI.json`, `sifir_kredi.json`, `NOT_CEVAPLARI.md`; son satır
  `OZET | islem: _ | sifir_kredi: _ | yeniden_cek: _ | yeni_plan: _ | kredi_tahmini: _`.

**`yayin-paketcisi`** · baştan yazılır (yayın stratejisti)
```yaml
---
name: yayin-paketcisi
description: Yayın stratejisti ve paketçi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler teshis (kanal verisini yorumlar), paket (başlık seçimi, açıklama, bölümler, etiketler, YZ beyanı, Short ve fragman planı), kapak (kapak şartnamesi ve seçimi), izleme (yayın sonrası veriyi yorumlar). Başlık yazmaz, adaylardan seçer.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Başlığı `HIKAYE.json`'daki adaylardan seçersin; yeni başlık gerekiyorsa gerekçesini yazıp `hikaye-yazari`'na istek bırakırsın.
  Başlığın her öğesi ilk 120 sn'de ekranda olmalı. 'kill' sözcüğü BAYRAK'tır. Kapak filmdeki bir anı gösterir; filmde olmayan vaat yazılamaz.
  YZ beyanı alanını boş bırakamazsın."
- **Görev sınırı:** kanal teşhisinin yorumu; başlık seçimi (adaylardan); açıklama, bölümler (zamanlar `KURGU_PLANI`'ndan), etiketler, YZ beyanı; kapak şartnamesi ve seçimi; Short ve fragman pencereleri; yayın sonrası 48 sa / 7 / 28 gün yorumu. Görsel üretmez, kurguya dokunmaz, yükleme yapmaz.
- **Okur:** `KANAL_TESHIS.md`, `HIKAYE.json` (başlık adayları, vaat sözleşmesi, bölüm adları, Short adayları), `KURGU_PLANI` zamanları, kazanan kapak
  kalıbı (KARARLAR.md), `YOUTUBE_POLITIKA.md`, kapak denetimi ve ikili seçim sonuçları, `YAYIN_ANALIZ_<gun>.json`.
- **Çıktı:** `YAYIN/PAKET.json`, `YAYIN/KAPAK_SPEC.json`, `KAPAK_SECIM.json`, `TESHIS_YORUM.md`, `IZLEME_YORUM_<gun>.md`.

**`ders-editoru`** · yeni
```yaml
---
name: ders-editoru
description: Ders defteri editörü. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; birikmiş ders kümelerinden aday kural yazar (filtre kelimesi, istem kalıbı, eşik, yol kuralı, kara liste). Güvenlik kurallarını gevşetemez; kuralı betik uygular.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Tempo hızlandırma, Flow tavanı yükseltme, uyarı/doğrulama/gizli bilgi/onay/silme kurallarını gevşetme ve kanıtsız kural yazamazsın. Tek filmden
  hikâye dersi genellenmez (≥ 2 film). Sıkılaştırıcı eşik için kalibrasyon setindeki yanlış alarm oranını yaz."
- **Görev sınırı:** yalnız aday kural önerir; kuralı `ders_derle.py` korkuluk testinden geçirip uygular. Film içeriğine, eşik dosyalarına ve kodlara doğrudan yazmaz.
- **Okur:** `ders_derle` kümeleri, `KURALLAR_OGRENILEN.json`, korkuluk listesi, kalibrasyon özetleri. **Çıktı:** `aday_kurallar.json`, `DERS_RAPORU.md`.

**`memmet-bakimci`** · yeni
```yaml
---
name: memmet-bakimci
description: Flow arayüzü değiştiği için Memmet durduğunda değişen seçiciyi bulan bakımcı. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır. Yalnız aday yama yazar; kaynak dosyalara dokunmaz.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 100
permissionMode: acceptEdits
---
```
- **İlk satırlar ([CM2] §4.3.5):** "Yalnız `CIKTI/memmet_yama.diff`, `CIKTI/fikstur/*.html` ve `CIKTI/BAKIM.md` yazarsın. Bekleme ve mola süresini kısaltamazsın;
  uyarı ve doğrulama kelime listelerini daraltamazsın; yeniden deneme ekleyemezsin; fare/klavye taklidi ekleyemezsin; reCAPTCHA'ya dokunamazsın. Yamayı
  korkuluk testleri sınar; geçmeyen yama uygulanmaz."
- **Görev sınırı:** yalnız `arayuz` kısıtında çağrılır; değişen seçiciyi bulur ve aday yama + fikstür yazar. Tempo, kelime listeleri, deneme sayısı ve kip varsayılanı onun alanı değildir.
- **Okur:** GIRDI'deki `memmet.py` kopyası, hata sayfasının HTML'i ve PNG'si, `_memmet_cikis.json`. **Çıktı:** aday yama, fikstür, bakım notu.

### 3.4 Denetçiler (5)

**`juri-uyesi`** · yeni
```yaml
---
name: juri-uyesi
description: Kör jüri üyesi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler (rol) ilk_kez_izleyen, youtube_stratejisti, tur_uzmani, duygu_elestirmeni. Anonim film önerilerini 10 ölçütle puanlar ve sıralar.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Önerilerin yazarını bilmiyorsun ve tahmin etmeye çalışma. Cömert olma: 8, 'bu kanalda izlenir' demektir. Her puana bir cümle gerekçe."
- **Görev sınırı:** A04'te anonim önerileri puanlar ve sıralar; öneri yazmaz, düzeltmez, kazananı seçmez (seçim betikte, medyanla).
- **Okur:** anonim öneriler, `JURI_TABLOSU.md` (10 ölçüt: kanca, netlik, merak, duygu, karakter, özgünlük, yapı, üretilebilirlik, süreklilik yükü,
  seri; 1/5/8/10 çapaları), rol tarifi. **Çıktı:** `03_juri_<rol>.json` + `.md` (çalınmaya değer, mutlaka düzelt, veto, sıralama; OZET satırı).

**`uretilebilirlik-denetcisi`** · güncellenir
```yaml
---
name: uretilebilirlik-denetcisi
description: Üretilebilirlik denetçisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler juri (önerilerin Flow/Veo ile çekilebilirliği) ve plan (bir partinin planlarında 2–3 adımın sığması, el ve parmak, ölçek, filtre riski, zayıf işler). Kredi hesabı yapmaz.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Kredi ve süre hesaplamazsın; onu `kredi.py` yapar. Yalnız GIRDI'deki kısıt matrisine ve derslere göre çekilemeyeni, riskliyi ve sığmayanı yaz."
- **Görev sınırı:** çekilemez, riskli ve 8 sn'ye sığmayan öğeyi yazar; çözüm önerebilir ama planı değiştirmez; kredi ve süre hesabı yapmaz.
- **Okur:** juri: anonim öneriler + Veo/Flow kısıt matrisi; plan: `CEKIM_LISTESI_P<n>.md`, plan dilimi, kısıt matrisi, `DERSLER.md`.
  **Çıktı:** `URET_JURI.json` / `URET_PLAN_P<n>.json`.

**`sureklilik-denetcisi`** · baştan yazılır
```yaml
---
name: sureklilik-denetcisi
description: Süreklilik denetçisi ve hakem. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler kagit (dünya defterinin göremediği anlam hataları), hakem (yalnız tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ alanları; görsel KRİTİK reddi), kacis (iki tur düzelmeyen planın kök nedeni), ders. İlk gözlemi yapmaz, CORRECTION yazmaz.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "İki kaynağın HATA dediği alanı GEÇ'e çeviremezsin; sistem reddeder. ÖLÇÜLEMEDİ GEÇ değildir: kanıtın yoksa BAYRAK bırak. CORRECTION cümlesi
  yazmazsın (şablondan gelir). Her kararına kare ya da satır kanıtı yaz."
- **Görev sınırı:** betiğin göremediği anlam hatalarını yazar; hakem kipinde yalnız tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ alanlarına karar verir; kaçışta kök nedeni yazar (planı `yonetmen·onarim` değiştirir); görsel KRİTİK reddinde D-21 şartlarıyla hakemdir.
- **Okur:** kagit: `K0_FILM.json` BAYRAK'ları, defter ve plan dilimi; hakem: ilgili kareler, yerel ölçüm, kör cevaplar (alan bazında); kacis: plan
  geçmişi ve raporlar; ders: kategori sayımları. **Çıktı:** `K0_HAKEM.md`, `HAKEM_<kapi>.json` (`[{plan, alan, karar, gerekce, kanit}]`), `KACIS.json`,
  `KRITIK_RED_<kip>_t<n>.json`, `DERS_ONERI.md`.

**`diyalog-editoru`** · yeni
```yaml
---
name: diyalog-editoru
description: Diyalog editörü. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; bütün replikleri sırayla okur ve doğallık, dönem dili, ad tutarlılığı, telaffuz riski, filtre kelimesi, kelime sınırı, klişe, açıklama, alt metin ve yarım cümle açısından denetler; TR altyazı önerir. Repliği değiştirmez.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Replik metnini değiştirmezsin; her öneriyi replik kimliğiyle ve seviyesiyle yaz. Bilgi taşıyan replikte çatışma yoksa ORTA. Klişe listesi
  GIRDI'dedir."
- **Görev sınırı:** bütün replik listesini denetler ve öneri yazar; replik metnini değiştirme yetkisi `hikaye-yazari`'ndadır.
- **Okur:** `06_SENARYO` replikleri, evren sözlüğü (adlar, güvenli karşılıklar), filtre ve klişe listeleri, `DERSLER.md`. **Çıktı:** `DIYALOG_RAPOR.json`
  (`R0123 | KRITIK/ORTA/KUCUK | öneri | tr`).

**`hat-denetcisi`** · yeni
```yaml
---
name: hat-denetcisi
description: Hat denetçisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kesin bütçe noktasında (B2), pilottan sonra, kuyruk 30 klibi aşınca ve dilim aktarımında betik kapılarının göremediği riskleri arar ve GİT ya da GİTME der.
tools: Read, Write, Glob, Grep
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
---
```
- **İlk satırlar:** "Tempo, uyarı ve hesap kurallarını yorumlayarak gevşetemezsin. GİTME dediğinde nedenini ve kapatma koşulunu yaz."
- **Görev sınırı:** yalnız GİT/GİTME ve kapatma koşulu yazar; bütçeyi, tempoyu ve kapıları değiştirmez.
- **Okur:** `URETIM_ONIZLEME`, kuyruk özeti, kapı raporları özeti, `OLCUM0.json`, `FLOW_YUK` özeti. **Çıktı:** `HAT_<kapsam>.json` + `.md`
  (`OZET | karar: GIT/GITME | KRITIK | ORTA`).

### 3.5 Kör değerlendiriciler (6)

**`habersiz-seyirci`** · güncellenir
```yaml
---
name: habersiz-seyirci
description: Filmi hiç bilmeyen, ilk kez izleyen YouTube seyircisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler kagit, plan, ilk2dk, animatik, kurgu, kapak. Her turda yeni örnek açılır.
tools: Read, Write
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
omitClaudeMd: true
---
```
- **İlk satırlar ([CM2] §4.3.4 + [KU2] §4.3):** "Bu filmi İLK KEZ izliyorsun; planını, yazarların niyetini ve önceki turları bilmiyorsun. Yalnız GIRDI'deki bölümü sırayla
  'izle'; ileriyi tahmin etme, geri dönüp düzeltme. Adını ekranda duymadığın karakteri adıyla anma; tarif et. 'Duyulan' satırı o anda duyduğun tek şeydir;
  '(anlaşılmayan konuşma)' yazıyorsa o sözü duymadın. Cömert olma." Persona satırı GOREV.json'dan gelir.
- **Kipler:** `kagit`, `plan` (gövde: senarist, yönetmen), `ilk2dk` (başlık + kapak tarifi ya da görseli + ilk 120 sn; "30 sn'den sonra kalır mıydın, 2. dk
  sonunda devam eder miydin, vaat edileni gördün mü"), `animatik`, `kurgu` (gövde: kurgucu; dikey kesit de bu kiple), `kapak` (ikili: "bu başlık ve bu
  kapakla tıklar mıydın?").
- **Görev sınırı:** yalnız izler ve raporlar; düzeltme önermesi serbesttir ama hiçbir dosyaya dokunmaz, ilerideki bölümleri okuyamaz.
- **Okur:** yalnız o ana kadar açılmış GIRDI bölümleri. **Çıktı:** `rapor_<bolum>.md`, son bölümde `rapor.json` (şema §5.8); son satır
  `OZET | anlasilirlik | akicilik | merak | duygu | ritim | ilk30 | GENEL | KRITIK | ORTA`. Formda ayrıca: kopukluklar (plan ya da zaman koduyla),
  sıkıldığı anlar, dakika ya da sahne başına ilgi, açık sorular, 3 cümle özet, kahraman ne kaybedebilir, ekran dışı sesler kime ait, gereksiz
  açıklanan yer, aptal yerine konduğu an, `kapatma_ani`, `devam_olasiligi`.

**`ozet-eslestirici`** · yeni
```yaml
---
name: ozet-eslestirici
description: Özet eşleştirici. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler ozet (seyirci özetini anahtar olgularla karşılaştırır) ve bulgu (her kopukluğu ve açık soruyu bir olgu, merak ya da kurulum kimliğiyle eşler). Puan vermez.
tools: Read, Write
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
omitClaudeMd: true
---
```
- **İlk satırlar:** "Kendi bilginle tamamlama; seyircinin yazmadığı şeyi bulundu sayma. Her eşleşmeye seyircinin cümlesinden alıntı koy. Oran hesaplama; betik hesaplar."
- **Görev sınırı:** tek seyircinin raporunu olgu, merak ve kurulum kimlikleriyle eşler; puan, öneri ve yorum yazmaz.
- **Okur:** tek seyircinin raporu, `anahtar_olgular`, `MERAK_DEFTERI`, `KURULUMLAR` (kimlik + ad), maske listesi. **Çıktı:** `eslesme.json`
  (`bulundu | kismen | yok` + alıntı; bulgu kipinde `{eslesen: {tur, id} | null, alinti}`).

**`oyuncu`** · yeni
```yaml
---
name: oyuncu
description: Oyuncu. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; yalnız kendi karakterinin kartını ve repliklerini okur ve bu karakterin bunu böyle söyleyip söylemeyeceğini, neyi bilmesinin imkânsız olduğunu yazar.
tools: Read, Write
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
omitClaudeMd: true
---
```
- **İlk satırlar:** "Yalnız kendi karakterini oynarsın. Repliği yeniden yazma; sorunu ve nedenini yaz."
- **Görev sınırı:** yalnız kendi karakterinin repliklerini (ve her birinin hemen öncesindeki karşı repliği) okur; senaryonun geri kalanını görmez.
- **Okur:** karakter kartı (istek, korku, yara, sır, yay,
  konuşma tarzı, bildikleri), o karakterin replikleri ve hemen öncesindeki karşı replik. **Çıktı:** `OYUNCU_<karakter>.json` (`R id | seviye | not`).

**`kare-tarifcisi`** · yeni
```yaml
---
name: kare-tarifcisi
description: Kör kare tarifçisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler kart, g1, v3, kapak. Beklenen değeri görmeden görselleri iki aşamalı soru formuna göre tarif eder.
tools: Read, Write
model: opus
effort: high
maxTurns: 40
permissionMode: acceptEdits
omitClaudeMd: true
---
```
- **İlk satırlar ([GS2] 5 kural):** "Tahmin etme. Önce serbest envanter: her kişiye p1, p2 ver; yerini (üçte bir), yüz yönünü, ellerini yaz. Sol ve sağ GÖRÜNTÜNÜN sol ve
  sağıdır. Sonra hedefli soruları cevapla. Emin değilsen 'cannot tell'."
- **Görev sınırı:** yalnız görüleni tarif eder; karar, puan ve düzeltme yazmaz; beklenen değeri görmez.
- **Okur:** anonim `g01.jpg…` (≤ 12 görsel/görev, tahmin), `SORULAR.json` (ad, kostüm, rol ve beklenen konum içermez; kritik sorular karışık sırayla iki
  kez; ifade sorusu D-22). **Çıktı:** `CEVAP_gNN.json`.

**`kesici`** · yeni
```yaml
---
name: kesici
description: Kör kesme önericisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler animatik ve kurgu. Tek soruya cevap verir; hangi 10 planı ya da 2 sahneyi atarsak film daha iyi olur?
tools: Read, Write
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
omitClaudeMd: true
---
```
- **İlk satırlar:** "Her öneri için gerekçe, beklenen kazanç (sn) ve 'seyirci olarak neyi kaybedebilirim' notu yaz. Öneriyi sistem simüle eder; zararlıysa uygulanmaz."
- **Görev sınırı:** yalnız kesme önerir; öneriyi `kurgu_denetim --kesme-simule` sınar, plan kesmesini kurgucu, sahne kesmesini `hikaye-yazari` uygular.
- **Okur:** izleme sayfaları + `IZLE.md` + `KESME_GIRDI.md` (plan süreleri, ortak sıkılma anları, medyan ilgi eğrisi). `ekranda_bilgi`, amaç ve kurulum
  listesi yoktur. **Çıktı:** `KESME_ONERI.json`.

**`plan-elestirmeni`** · yeni
```yaml
---
name: plan-elestirmeni
description: Plan eleştirmeni. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; bir partinin çekim listesini görüntü dili, kapsama, okunurluk, akış ve oyunculuk açısından eleştirir.
tools: Read, Write
model: opus
effort: high
maxTurns: 60
permissionMode: acceptEdits
omitClaudeMd: true
---
```
- **İlk satırlar:** "Yalnız GIRDI'deki çekim listesine, kroki görsellerine ve kontrol listesine bak. İstem yazma; sorunu plan numarasıyla ve seviyesiyle yaz."
- **Görev sınırı:** bir partinin çekim listesini eleştirir; plan yazmaz, istem yazmaz; bulgularını yönetmenin onarım görevi kullanır.
- **Okur:** `CEKIM_LISTESI_P<n>.md`, kroki PNG'leri, sahne değerleri ve vuruşlar, `PLAN_DILI.md §Kontrol listesi` kopyası (11 + 2 oyunculuk + 1 imza plan
  maddesi). **Çıktı:** `PLAN_ELESTIRI_P<n>.json` + `.md` (`OZET | kapsama | kadraj_dili | okunurluk | akis | oyunculuk | KRITIK | ORTA`).

### 3.6 Ajan çağrısı bütçesi (40 dk; tahmin, [UM2] §4.3.6 + bu belgenin ekleri)
hikâye 40–75 · ses 15–55 · yönetmen 70–110 · kart 1–3 · kör gözlem ≈ 145–175 (kart, G1, V3, kapak) · hakem 15–40 · animatik 20–35 (+ KR3a) · dikey kesit
6–10 · hat/ders 3–6 · replik kabul 5–15 · kurgu 20–35 (+ KR8a) · yayın 5–10 → **≈ 350–570**. Gerçek sayı ve token Ö0-f ile ölçülür ve aşama görev
tavanını belirler (D-08).

## 4. Beceriler

### 4.1 Kaç beceri, neden
**Dört beceri** ([CM2] §4.4.1). Aşama başına beceri yoktur: kullanıcı yalnız konu verir, `/…` komutlarını kimse yazmaz; aşama ayrıntısı ajanın
işidir ve şablonlarda durur. `disable-model-invocation: true` taşıyan beceriyi Claude kendisi açamaz.

| Beceri | Kim açar | Rol | Neden ayrı |
|---|---|---|---|
| `film-yap` | Claude (otomatik) + `/film-yap` | set amiri döngüsü; Ö0 sistem görevleri de bu döngüden gelir | ana iş |
| `film-durum` | Claude + `/film-durum` | soru = yalnız cevap | o sırada yazma araçları ve Agent kapalı |
| `film-not` | Claude + `/film-not` | kullanıcı notu, şikâyeti, CapCut düzenlemesi → görev | kullanıcının kurgu kararı korunur |
| `film-gelistir` | yalnız `/film-gelistir` | sistemi değiştirme (araç, ajan, kanca, test); Ö0-a; memmet3 aktarımı | film sırasında kod değişmesin |

**Tek soru metni** (A00; aktif film yoksa ve kullanıcı konu vermediyse, harfiyen): "Filmin konusu ne olsun? Bir cümle yeter (ör. ejderha yavrusunu
saklayan avcı kadın). İstersen 'sen seç' yaz." Konuyla birlikte gelen istekler `kesin_istekler`'e yazılır; belirsizlikte soru değil varsayım.

### 4.2 `film-yap`
```yaml
---
name: film-yap
description: >-
  Kullanıcı bir film konusu verdiğinde ya da süren bir filme devam edilmesi gerektiğinde YZ film setini yürütür:
  görev defterindeki sıradaki işi çalıştırır, uzman ajanlara dağıtır, kapılardan geçirir. Use when the user gives a
  movie topic or story idea, asks for a film ("film yap", "yeni film", "şu konuda bir film", "make a movie about"),
  says "sen seç", "devam", "devam et", "kaldığın yerden", "continue", reports that a requested physical step is done
  ("zipi koydum", "Flow'da gönderdim", "kredi yükledim", "dışa aktardım"), or when the session context shows an active
  film or a pending system measurement task.
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
        - {type: command, command: "bash \"$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh\" erisim", timeout: 10, onFailure: block}
    - matcher: "Bash|PowerShell"
      hooks:
        - {type: command, command: "bash \"$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh\" komut", timeout: 10, onFailure: block}
    - matcher: "Agent"
      hooks:
        - {type: command, command: "bash \"$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh\" ajan", timeout: 10, onFailure: block}
---
```
(`kanca.sh` kurulumun yazdığı mutlak Python yolunu `.claude/bin/python_yolu.txt`'den okur, yoksa `py -3.10`'a düşer; becerideki kancalar
`settings.json` kancalarının yedeğidir. Becerideki ve ayardaki kancanın aynı komutla iki kez koşup koşmadığı Ö0-a'da ölçülür.)

**`SKILL.md` gövdesi** (≤ 250 satır; ilk ≈ 110 satır çekirdek ≤ 4.500 token; sıkıştırmadan sonra geri gelen kısım budur):
```markdown
# FİLM YAP — set amiri döngüsü
## 0. Şu anki durum (beceri açılırken betik yazar)
!`python .claude/bin/film.py ozet --kisa || true`
## 1. Değişmez kurallar (kancalar da zorlar)
1. Kullanıcıya YALNIZ filmin konusu sorulur, yalnız şu cümleyle: "Filmin konusu ne olsun? Bir cümle yeter (ör. ejderha yavrusunu
   saklayan avcı kadın). İstersen 'sen seç' yaz." Diğer bütün kararları ekip verir: film.py karar ekle "karar — neden — yanlışsa
   maliyeti". "Hangisini istersin / onaylıyor musun / devam edeyim mi" YOK.
2. Kullanıcıdan yalnız onun yapabileceği FİZİKSEL iş istenir. Talimat cümlesini film.py verir; aynen ilet.
3. Flow "olağan dışı etkinlik" / doğrulama → hat durur. Yeniden başlatma, atlatma, tempo hızlandırma, fare/klavye taklidi,
   BAŞKA HESAPLA DEVAM YOK. Kilidi yalnız kullanıcı kaldırır (UYARI_GECTI.bat).
4. AYARLAR hiçbir kökte okunmaz, yazdırılmaz, kopyalanmaz. Ayar gerekiyorsa: film.py goster ayar (maskeli).
5. Sen içerik üretmezsin, puan vermezsin, ajan çıktısını düzeltmezsin, plan/rapor dosyası yazmazsın.
6. Ajan çağırırken: yalnız görevdeki ajan tipi; istem AYNEN; name verme; fork başlatma; yerleşik ajan kullanma.
7. Büyük dosya açma. Bilgi gerekiyorsa: film.py goster <ne>.
8. Hafızana değil film.py'ye güven: film.py sonraki ne diyorsa o doğrudur.
9. Kullanıcı soru sorarsa film-durum; not verirse film-not. Soruya işlemle cevap verme.
10. Kredi yalnız film.py'nin bütçe noktası geçince harcanır. memmet.py'yi ya da bir sağlayıcıyı doğrudan çağırma.
11. Kalıcı silme yok; robocopy /MIR yok; git push yok.
12. Çıkış kodu 2, 4, 5, 6, 7 ya da 8 ise film.py'nin cümlesini söyle ve turu bitir. Soru ekleme.
## 2. Döngü
1. python .claude/bin/film.py sonraki → JSON.
2. python .claude/bin/film.py basla <id,id,…>. Reddederse (kanca nabzı yok): KURTARMA.md §Kanca; ajan çalıştırma.
3. tur=ajan → aynı paralel_grup'taki görevlerin HEPSİ İÇİN TEK MESAJDA Agent çağır (en çok 5): subagent_type=<ajan>,
   prompt=<istem> AYNEN. Sonucu bekle. ornek=ayni_yazar ise önce SendMessage(<ajan_id>); kimlik yoksa yeni örnek.
   Aşamalı görevlerde bölüm geçişini sistem yapar; sen bir şey yapmazsın.
4. tur=betik → python .claude/bin/film.py calis <id>. 8 BEKLE dönerse film.py bekle <iş>'i arka planda başlat ya da turu bitir.
5. tur=kullanici_eylemi → mesajı aynen ilet ve turu bitir.
6. tur=bekle/kisit/ortam/butce → nedeni film.py'nin cümlesiyle söyle, turu bitir.
7. tur=bitti → film.py ozet --kullanici çıktısını ilet.
8. Ajan sonucu ya da tamamlanma bildirimi gelince doğrulama yapma (kanca yaptı) → 1'e dön.
## 3. Kullanıcıyla konuşma
Türkçe, kısa, teknik terim yok. Her ilerlemede en çok 3 satır: ne bitti · şimdi ne oluyor · senden bir şey gerekiyor mu (yalnız fiziksel iş).
## 4. Takılırsan
- film.py "takildi" derse KURTARMA.md'yi oku ve yazanı uygula.
- Bir kanca işlemi engellediyse gerekçeyi oku, kuralı çiğneme; film.py sonraki.
- Kullanım sınırı ya da kesilme: hiçbir şey yapma; yeniden açılınca döngü kaldığı yerden sürer.
--- (çekirdek sonu) ---
## 5. Referanslar (yalnız film.py `oku` alanında gösterirse ya da takılınca)
KURTARMA.md · GOREV_SEMASI.md · KULLANICI_DILI.md · reference/hat.md
```

**Adımlar (döngünün ürettiği iş sırası; ana Claude bunları bilmek zorunda değildir, `film.py sonraki` verir):** Ö0 sistem görevleri (§1.2) → A00 …
A18a (§1.3). **Ek referans dosyaları:** `KURTARMA.md` (kanca nabzı yok, kilit bayat, DUR, kesik indirme, GPU kilidi, kullanım sınırı, Flow kilidi,
disk dolu), `GOREV_SEMASI.md`, `KULLANICI_DILI.md` (çıkış koduna göre sabit Türkçe cümleler, `.bat` adları, kavram sözlüğü), `reference/hat.md`
(`film.py asamalar --md` ile üretilen aşama listesi, kısıt ve bütçe dili). **Çağırdığı betikler:** yalnız `.claude/bin/film.py` (`sonraki`,
`basla`, `calis`, `bekle`, `ozet`, `goster`, `karar ekle`); geri kalan her araç `film.py calis` içinden çağrılır.

### 4.3 `film-durum`
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
allowed-tools: Bash(python .claude/bin/film.py ozet*), Bash(python .claude/bin/film.py goster*), Bash(python .claude/bin/film.py surus kapat --soru*)
---
```
**Adımlar** (≤ 60 satır): (1) `` !`python .claude/bin/film.py surus kapat --soru || true` `` (otomatik sürüş yalnız bu tur kapanır; Stop kancası
sürmeye zorlamaz); (2) soruya göre `film.py ozet --uzun` · `goster plan 042` · `goster maliyet` · `goster neden-durdu` · `goster token` ·
`goster ayar` (maskeli) · `goster sozlesme` (kullanıcı sözleşmesi kartı); (3) cevap düz Türkçe, ≤ 6 satır, sayı varsa kaynağıyla; son satır en çok
bir öneri; işlem yok. **Referans:** `KULLANICI_DILI.md`. **Betikler:** `film.py ozet`, `goster`, `surus kapat --soru`.

### 4.4 `film-not`
```yaml
---
name: film-not
description: >-
  Kullanıcı animatik, dikey kesit, CapCut taslağı ya da bitmiş film hakkında not, şikâyet veya kendi yaptığı düzenlemeyi
  bildirdiğinde notları salt okunur okur, karar ve ders defterine işler, düzeltme görevlerine çevirir. Use when the
  user says "notlar hazır", "CapCut'ta değiştirdim kontrol et", "şu sahne kopuk", "ses kaymış", "beğenmedim", "şunu kes",
  "bu ses olmamış", or describes a problem in a draft or in an information package.
when_to_use: >-
  Kullanıcının kurgu kararı aynen uygulanır; kullanıcının taslağına yazılmaz, klonlanıp yamanır. Kendiliğinden gelen
  itiraz kesin istektir ve ilgili aşamayı yeniden açar. Notlar işlendikten sonra film-yap döngüsüne dönülür.
allowed-tools: Bash(python .claude/bin/film.py notlar*), Bash(python .claude/bin/film.py karar ekle*), Bash(python .claude/bin/film.py ders ekle*)
---
```
**Adımlar** (≤ 120 satır): (1) `film.py notlar oku` → `notlari_oku.py` + `taslak_fark.py` salt okunur (CapCut açıksa kullanıcı eylemi "CapCut'ı
kapat"; kapanış kendiliğinden algılanır); (2) her not sınıflanır: (a) kullanıcının kendi kurgu kararı → aynen ve kilitli `KURGU_PLANI`'na;
(b) şikâyet → hangi kapı yakalamalıydı (`film.py ders ekle --kapi … --belirti "…"`, `kaynak: kullanici_notu`); (c) yeni sahne ya da ses isteği →
kesin istek, içerik `hikaye-yazari`, plan `yonetmen`, ses `ses-tasarimcisi`; (3) `film.py karar ekle "Kullanıcı notu N: … — uygulanacak"`;
`film.py notlar isle` → `kurgucu·not` görevi; (4) kullanıcıya bilgi: "Notlarını aldım: N düzeltme. Bitince CapCut'ta listenin en üstünde yeni adla
göreceksin; senin taslağına dokunmadım." (soru yok); (5) kesme sonrası Z1 kurulum ve Y58 denetimleri yeniden çalışır. **Referans:**
`reference/kurgu.md` §Not. **Betikler:** `film.py notlar oku|isle`, `karar ekle`, `ders ekle`.

### 4.5 `film-gelistir`
```yaml
---
name: film-gelistir
description: >-
  Film setinin kendisini (ARACLAR betikleri, sağlayıcılar, kancalar, ajan ve beceri dosyaları, testler) değiştirmek, Ö0-a Claude Code
  ölçümünü yapmak ya da memmet3'ü depoya aktarmak için geliştirici kipi. Film üretimi için kullanılmaz.
when_to_use: >-
  Yalnız kullanıcı "/film-gelistir" yazdığında ya da oturum açıkça bir geliştirme oturumuysa. Film sürüşü açıksa önce sürüşü kapatır;
  anahtar dosyalarına ve kullanıcının veri klasöründeki film dosyalarına dokunmaz.
disable-model-invocation: true
argument-hint: "[değişiklik | olcum0-a | memmet3-aktar]"
---
```
**Adımlar** (≤ 150 satır): (1) `film.py surus kapat --gelistirme` (sürüşe bağlı yasaklar kalkar; anahtar okuma ve `robocopy /MIR` yasakları
kalır); (2) `YZ_FILM/ARACLAR/CLAUDE.md`'yi oku; (3) değişiklik; (4) `python -m unittest discover -s YZ_FILM/ARACLAR/testler`; (5) `film.py
beceri-denetim`; (6) küçük commit (kullanıcı ya da görev istediyse). **`olcum0-a`:** `olcum0/kanca_deneme/` kancalarını geçici `settings.local.json`
ile kurar, §10.3'teki 15 davranışı tek tek sınar, `O0a.json`'u yazar, geçici ayarı geri alır. **`memmet3-aktar`:** kullanıcının yerel memmet3
dosyasını depoya kopyalar, PR-0 yamasını ve fikstür testini uygular, gece kipindeki 5 yenileme denemesini siler. **Referans:**
`YZ_FILM/ARACLAR/CLAUDE.md`. **Betikler:** `film.py surus`, `beceri-denetim`, `unittest`.

### 4.6 Beceri klasörü ve kural yerleşimi
```
.claude/skills/film-yap/
  SKILL.md                ≤ 250 satır (çekirdek ilk ≈ 110 satır)
  KURTARMA.md · GOREV_SEMASI.md · KULLANICI_DILI.md
  reference/              ≤ 300 satır her biri; 100 satırı aşanın başında içindekiler; KURAL TAŞIMAZ
    hat.md  hikaye_odasi.md  yonetmen.md  goruntu_sureklilik.md  ses.md  kurgu.md  yayin.md
  PLAN_DILI.md            sözlükler, atomik zincir yazımı, 6 örnek, kroki/kurulum, karşılıklı çekim, kontrol listesi
  sablonlar/<ASAMA>_<ajan>[_<kip>].md     ajan istem şablonları (yer tutuculu sayılar)
  semalar/*.json          çıktı şemaları (seyirci_rapor_v2, juri_v1, plan_v2, gorev_v2, kapi_rapor_v1 …)
  BILGI_KURALLARI.md · ZANAAT.md · ritim_esikleri.json   (dilimleri GIRDI'ye konur; ana Claude okumaz)
  arastirma/ · tartisma/  tasarım belgeleri; üretimde hiçbir rol okuyamaz (erisim.json)
.claude/skills/film-durum/SKILL.md · film-not/SKILL.md · film-gelistir/SKILL.md   (referansları film-yap/'tan tek seviye bağlar)
```

| Kural türü | Nerede | Örnek |
|---|---|---|
| Makinede ölçülür ya da engellenir | kanca / betik | AYARLAR okunmaz; fork yok; Flow kilidi; hesap değişimi kilidi; yasak fiil HATA; ileri bölüm okunmaz; soru kapısı |
| Ajanın davranışı | ajan gövdesinin ilk satırları (§3) | "YZ'ye sonuç söylenmez"; "Sesi duyamazsın"; "adını duymadığın karakteri adıyla anma" |
| Ana Claude'un davranışı | `SKILL.md` çekirdeği | 12 değişmez kural, döngü |
| Açıklama, gerekçe, örnek | `reference/*.md`, `PLAN_DILI.md` | sözlükler, örnek planlar, eşiklerin anlamı |
| Sayılar | eşik dosyaları (`esikler.py`) | şablonlara yer tutucuyla basılır |

### 4.7 Kök `CLAUDE.md` ve veri kökü yönlendirmesi
Kök `CLAUDE.md` [CM2] §4.4.7'deki ≤ 45 satırlık metinle değiştirilir ("YZ FİLM SETİ" · açılışta oturum bağlamı ya da `film.py ozet` · aktif film yoksa
ve konu yoksa yalnız tek soru · konu ya da aktif film varsa soru sormadan `film-yap` · her zaman: yalnız konu sorulur, soru = cevap, Flow uyarısında dur
ve başka hesaba geçme, AYARLAR gizli, kalıcı silme yok · sistemi değiştirmek yalnız `/film-gelistir` ya da geliştirme oturumunda; ayrıntı
`YZ_FILM/ARACLAR/CLAUDE.md`). Bugünkü geliştirme listesi `YZ_FILM/ARACLAR/CLAUDE.md`'ye taşınır. Veri kökündeki 5 satırlık `CLAUDE.md`: "Bu klasör film
setinin VERİ klasörüdür; set burada çalışmaz. Kullanıcıya yalnız şunu söyle: 'Masaüstündeki FILM_SETI.bat'a çift tıkla; Claude doğru klasörde
açılır.' Başka bir şey yapma."

### 4.8 Değerlendirme senaryoları (`beceri_denetim.py` + elle bir kez)
1. "film yap" (aktif film yok) → yalnız tek soru; başka cümle yok.
2. "Ejderha büyüten bir kadın hakkında film yap" → soru yok; `film.py yeni --konu …`; A01 görevi; Ö0-b yoksa B0 1800 sn seçer ve bunu bilgi olarak söyler.
3. "devam" (bağlam boş; A07b'de 3 sahne grubu bitmiş, 2 `calisiyor` kesik) → yalnız kesikler ve kalanlar; bitenler yeniden yapılmaz.
4. Kancalar kapalıyken "devam" → `basla` reddeder; ajan açılmaz; düz Türkçe yönlendirme.
5. Ana Claude bir seyirci görevini `general-purpose` ile açmaya çalışır → `kanca.py ajan` reddeder.
6. "kaç kredi lazım?" → `film-durum`; dosya değişmez, ajan açılmaz.
7. Geliştirme oturumunda (sürüş kapalı) `Explore` → engellenmez.
8. Flow uyarısı fikstürü → Memmet ≤ 10 sn içinde durur, yeni gönderim 0, `FLOW_KILIDI.json` yazılır, kod 7, kullanıcıya tek cümle; "başka hesapla dene"
   isteği kural 3 ile reddedilir.
9. Animatik `ONAYLI` değilken "videoları çek" → video görevi açılmaz; nedeni bir cümle.
10. Ana Claude "Hangisini istersin, A mı B mi?" yazmaya kalkar → Stop kancası engeller ve "kararı ver, deftere yaz" der.
11. Kullanıcı dikey kesit paketinden sonra "ses robot gibi" der → `film-not`; kesin istek; ses aşaması yeniden açılır; kullanıcıya soru sorulmaz.

## 5. Veri şemaları

Bütün makine dosyaları `_surum` ve `_uretim` zarfı taşır; şemalar `.claude/skills/film-yap/semalar/` altında JSON Schema olarak durur ve
`plan_sema.py` / `kapi.py` ile doğrulanır. Aşağıdaki örneklerin sayıları **örnektir**, ölçüm değildir. Bu bölümde verilmeyen şemalar uzman
belgesinden **aynen alınır**: `KURGU/KURGU_PLANI.json`, `KURGU_KARARLARI`, `TASLAK_FARK.json`, `son_capcut_projesi.json` v2, `YAYIN_DOGRULAMA.json`
([KU2] §4.5); `SESLER/diyalog.json` v2, `KURGU/SES_CIZELGESI.json`, `MUZIK/muzik_listesi.json`, `KAYNAK_KAYDI.json`, `SES_KUTUPHANESI/DIZIN.json`
([SM2] §4.5); `kroki.json`, sözlükler ([YN2] §4.5); `SORULAR.json`, `CEVAP_gNN.json`, `ZINCIR_PLANI.json`, `G1` raporu ([GS2] §4.5); `KUNYE/NNN.json`,
`KREDI_DEFTERI.jsonl`, `URETIM_ONIZLEME.json`, `FLOW_TEMPO.json`, `FLOW_KILIDI.json` ([UM2] §4.5); `01_KONU_KARTI.json`, `HIKAYE.json` ([SN2] §4.5) —
bu belgenin eklediği alanlarla (`seyirlik_anlar`, `oyunculuk`, `duygu`, `take`, `kullanim`, `hesap_kimligi`).

### 5.1 `SAHNELER.json` v2 (mevcut şemayla geriye uyumlu)
```json
{
 "_surum": 2, "_sema": "sahneler_v2",
 "_uretim": {"asama": "A07c", "gorev": "A07c-001", "girdi_imza": "4be1c0d2", "arac_surum": "plan_birlestir 1.0",
             "esik_surum": "ritim@1.1+ogrenilen@3", "sonuc": "GEC", "zaman": "2026-11-02T21:14:05+03:00", "ortam": "yerel"},
 "film": "EMBERFALL_F2",
 "baslik": "She Raised the Dragon They Ordered Her to Hunt",
 "altyazi_dili": "tr",
 "karakterler": {
  "mara": {"ref": "01_KARAKTERLER/mara.jpg", "ses": "<voice_id>", "ses_adi": "<paylaşılan ses adı>",
           "evren": "EVREN/EMBERFALL/karakterler/mara@4", "kostum_varsayilan": "k1"},
  "voss": {"ref": "01_KARAKTERLER/voss.jpg", "ses": "<voice_id>", "ses_adi": "<paylaşılan ses adı>",
           "evren": "EVREN/EMBERFALL/karakterler/voss@2", "kostum_varsayilan": "k1"}
 },
 "mekanlar": {"kulube": {"evren": "EVREN/EMBERFALL/mekanlar/kulube@2",
                         "kurulumlar": {"K3": {"konum": [2.1, 0.8], "yon_derece": 250, "yukseklik_m": 1.5, "lens_mm": 50, "ebeveyn": "K1"}}}},
 "sahne_gruplari": {
  "S12": {"hikaye": {"sahne": "S12", "parti": 1}, "mekan": "kulube",
          "zaman": {"gun": 3, "gun_saati": "gece", "hava": "kar", "atlama": "yok"},
          "sahne_tipi": "diyalog", "sure_hedef_sn": 46, "plan_hedef": 11, "kalip": "yukselen_diyalog",
          "eksen": ["mara", "voss"], "kamera_tarafi": "dogu", "isik": {"ana": "ocak_ates", "dolgu": "pencere_ay", "arka": null},
          "yasaklar": ["no other people", "no open flame in frame except the hearth"],
          "giris_durumu": "HIKAYE.json#S12.giris_durumu", "cikis_durumu": "HIKAYE.json#S12.cikis_durumu",
          "canli_arka_plan": "snow drifting past the window",
          "ses": {"yatak": {"dosya": "SES_KUTUPHANESI/yatak/kulube_gece_ruzgar.wav", "seviye_lufs": -38, "dongu": true,
                            "katmanlar": [{"kaynak": "defter:mekan.kulube.ocak=yanik"}]},
                  "oda_yaniti": "ahsap_kucuk", "gecis": "capraz_0.8"},
          "_derlenir": {"ana_kareler": ["K1", "K3", "K5"], "yasak_ardisik": [["K3", "K4"]]}}
 },
 "sahneler": [
  {
   "no": 121, "sira": 121, "parti": 1,
   "referans": ["mara"],
   "gorsel_istem": "<istem_derle --gorsel çıktısı>",
   "hareket_istem": "Static medium close-up. 0.6-1.6s: Mara lifts her chin slightly, jaw set. 2.0-5.3s: Mara says coldly, in a low, husky female voice with a northern English accent: \"It's late, Captain. What do you want?\" 5.3-8s: holds the pose, breathing. Sound: wind against the door, a torch crackling. No music.",
   "amac": "Mara kaptanı içeri almıyor",
   "duygu": "gerilim",
   "replik": {"id": "R0042", "karakter": "mara", "metin": "It's late, Captain. What do you want?", "teslim": "soguk",
              "cumleler": [{"en": "It's late, Captain.", "tr": "Geç oldu, Kaptan."}, {"en": "What do you want?", "tr": "Ne istiyorsun?"}]},
   "kullanim": {"bas": 0.6, "sure": 3.6},
   "zanaat": {
    "kod": "S12-P02", "sahne_grubu": "S12", "plan_tipi": "diyalog", "klip_sn": 8,
    "kamera": {"kurulum": "K3", "kadraj": "OY", "aci": "goz_hizasi", "lens_mm": 50, "hareket_tipi": "sabit", "odak": "mara"},
    "kadrajdakiler": [{"id": "mara", "olcek": "OY", "yuz_acisi": "3/4", "konusur": true, "kimlik_demiri": true}],
    "baslangic_durumu": "miras",
    "eylem_zinciri": [
     {"id": "a1", "bas": 0.6, "bit": 1.6, "ozne": "mara", "tur": "mikro", "fiil": "cene_kaldirir", "govde": "cene", "olcu": "hafif", "hiz": "yavas", "etki": {}},
     {"id": "a2", "bas": 2.0, "bit": 5.3, "ozne": "mara", "tur": "konusma", "fiil": "konusur", "replik": "R0042", "cumleler": [0, 1], "etki": {}}
    ],
    "bitis_durumu": "derlenir",
    "oyunculuk": {"mara": {"ic_durum": "korkusunu saklıyor", "alt_metin": "kaptanı içeri almamak için soğuk davranıyor",
                           "dis_ifade": {"bas": "kontrollu_sakin", "bit": "gizli_endise"}, "isaretler": ["cene_sikili", "bakis_kacirir"], "siddet": 2}},
    "zincir": {"gecis_turu": "eylem_kesme", "onceki_plan": 120, "baslangic": "ana_kare", "ebeveyn": "K3", "dogal_durak": false, "bitis_sabitle": false},
    "kesme": {"tip": "L", "ses_tasma_sn": 1.1},
    "ekran_disi_ses": null,
    "ekranda_bilgi": "Mara kaptanı kapıda soğuk karşılıyor.",
    "yasaklar": [],
    "risk_uretim": "dusuk",
    "istem_elle": null,
    "ses": {"diyalog": {"yol": "veo_donustur", "yol_neden": null, "seviye_ozel": null},
            "efektler": [{"id": "e1", "adim": "a1", "kategori": "kumas", "malzeme": "kostum:mara/k1", "an": "bas", "kaynak_tercih": "klip", "yedek": "kutuphane", "seviye_db_diyaloga_gore": -8}],
            "flow_sound": "Sound: wind against the door, a torch crackling. No music.", "sessizlik": null, "dis_katman_db": null}
   },
   "_derlenir": {"sure_sn": 3.6, "kesme_nokta_sn": 4.2, "kadraj_konumu": {"mara": "sag_ucte_bir"}, "kadraj_sirasi": ["mara"],
                 "kamera_tarafi": "dogu", "bakis_kadrajda": {"mara": "kadraj_soluna"}, "isik_kadrajda": "soldan", "ekran_yonu": null,
                 "replik_zaman": {"R0042": [2.0, 5.3]}, "agiz_gorunur": "tam", "dinleyen_agiz": null, "ayna_yasak": true,
                 "acik_parmak": {"mara": {"sag": 0, "sol": 5}}, "ton_fiili_en": "says coldly", "seviye": -19.5,
                 "gorunmesi_gerekenler": ["mara", "kapi_esigi"], "referans": ["kart:mara/k1@4"], "istem_ozeti": "9c1e44a0"},
   "uretim": {"uretim_blogu": 7, "saglayici": "flow", "model": "omni-1.1-flash", "cozunurluk": "720p", "klip_sn": 8, "istem_bicimi": "aralik",
              "zincir": {"yontem": "bagimsiz", "kaynak": null, "kesim_sn": null, "derinlik": 0, "yedege_dustu": false},
              "gorsel": {"saglayici": "gemini_paket", "basamak": 2, "aday": "b", "sha1": "e3b0c442", "referanslar": ["kart:mara/k1@4", "ana_kare:K3"], "tohum": null},
              "durum_dondu": {"bas": "d41f09", "bit": "77c0a1"}, "plan_imza": "51aa09c3", "deneme": 1, "deneme_max": 3, "soy": 121,
              "take": {"sayi": 1, "secilen": null}, "is_kimligi": "a1b2c3", "durum": "gecti"},
   "denetim": {"G1": {"sonuc": "GEC", "sha1": "e3b0c442", "rapor": "_RAPOR/G1_P1_B2.json"},
               "V1": {"sonuc": "GEC", "rapor": "_RAPOR/V1_B07.json"}, "V2": {"sonuc": "GEC"}, "V3": {"sonuc": "GEC"}, "G1Z": null, "K1": null},
   "kurgu": {"kirpma_onceligi": "replik"}
  }
 ]
}
```
**Geriye uyumluluk ve sahiplik kuralları:**
1. Eski alanlar (`film`, `baslik`, `karakterler.<id>.{ref, ses, ses_adi}`, `sahneler[].{no, parti, referans, gorsel_istem, hareket_istem, amac, duygu,
   replik{karakter, metin, cumleler[{en, tr}]}}`, `altyazi_dili`) aynı adla ve anlamla kalır; mevcut `seslendir.py`, `capcut_film.py`, `memmet.py`,
   `kontrol.py` bunları okumayı sürdürür. **`zanaat` yoksa** dosya v1 sayılır ve eski kurallar uygulanır (`istem_denetim` filtre kelimesini UYARI
   verir; `ORNEK_3_SAHNE` ve `test_film.py`'nin buna dayanan beklentileri değişmez).
2. **Anlam değişikliği:** `parti` artık hikâye partisidir (1–3). 20 planlık gönderim bloğu `uretim.uretim_blogu`'dur; Memmet `parti`'yi okumaz,
   `BLOK_PLANI.json`'u okur ([UM2] S15).
3. `gorsel_istem` ve `hareket_istem` artık **derlenmiş** alanlardır (`istem_derle.py`); elle yazım yalnız `zanaat.istem_elle` ile, plan oranı ≤ %5.
4. `no` kalıcı kimliktir; `sira` kurgu sırasıdır (araya plan girerse ondalık: 121.5). `replik.id` HIKAYE.json'daki R kimliğidir; metin kelimesi
   kelimesine aynıdır (bölme serbest, `replik_bolundu` kaydıyla).
5. Alan sahipleri: `zanaat` (kamera, eylem zinciri, oyunculuk, zincir niyeti, kesme, ekran dışı ses) yönetmen · `oyunculuk.ic_durum/alt_metin`
   ve `replik.{metin, teslim}` senarist · `zanaat.ses` ve `sahne_gruplari.<S>.ses` ses · `_derlenir` yalnız kod (ajan yazarsa HATA) · `uretim` üretim
   betikleri · `denetim` kapılar · `kurgu.kirpma_onceligi` kurgucu. Kırpmanın tek yazılan alanı `kullanim{bas, sure}`; ölçülen kırpma yalnız
   `KURGU_PLANI`'nda durur.
6. Durum nesnesi yalnız olgudur: `karakterler.<id>{mekan, isaret, poz, yuz_yonu, bakis{hedef}, kostum, kostum_durumu, gorunum{kir, islak, yaralar,
   sac}, eller{sag, sol: {tutar, yer, sekil}}, ifade, duygu{durum, siddet, izler[]}, gizli_arkasinda}`, `nesneler.<id>{kimde, el, durum} |
   {nerede, durum}`, `mekan_durumu`. Sağ/sol karakterin kendisine göredir; kadraja göre yön yalnız `kadraja_girer` / `kadrajdan_cikar` fiillerinde.

### 5.2 Dünya durumu defteri `<film>/DUNYA_DEFTERI.json` (sahibi `dunya_defteri.py`; elle düzenlenmez)
```json
{
 "_surum": 1, "film": "EMBERFALL_F2", "evren": "EVREN/EMBERFALL@7", "girdi_imza": "c19a2f07",
 "baslangic": {"kaynak": "EVREN/EMBERFALL/DURUM_SON.json@4", "zaman": {"gun": 1, "gun_saati": "safak"},
   "karakterler": {"mara": {"mekan": "orman_yolu", "kostum": "k1", "kostum_durumu": "temiz",
                            "eller": {"sag": {"tutar": null, "yer": "yanda", "sekil": "serbest"}, "sol": {"tutar": "fener", "yer": "govde_onunde", "sekil": "tutus_tam"}},
                            "ifade": "dikkatli", "duygu": {"durum": "tetikte", "siddet": 1, "izler": []}}},
   "nesneler": {"fener": {"kimde": "mara", "el": "sol", "durum": "yanik"}, "anahtar": {"nerede": "kulube.masa", "durum": "kapali"}}},
 "zaman_cizgileri": {"ana": ["S01", "S02", "S12"], "gecmis_1": ["S07"]},
 "planlar": {
  "120": {"kaynak": "PLANLAR/S12.json#120", "bas": "d41f09", "bit": "77c0a1",
          "bas_ozet": "Mara kapı eşiğinde; fener sol elde, yanık; ifade kontrollu_sakin",
          "bit_ozet": "Mara kapı eşiğinde; fener sol elde; ifade gizli_endise; duygu gerilim 2",
          "olaylar": ["O-0311"]},
  "121": {"kaynak": "PLANLAR/S12.json#121", "bas": "77c0a1", "bit": "8e21d0", "olaylar": []}
 },
 "olaylar": [{"id": "O-0311", "plan": "120", "adim": "a2", "tur": "duygu_degis", "kim": "mara", "deger": {"durum": "gerilim", "siddet": 2}}],
 "sahne_uclari": {"S12": {"giris": "d41f09", "cikis": "9a7713", "hikaye_esit": true}},
 "hikaye": {"kaynak": "HIKAYE.json#bilgi", "salt_okunur": true},
 "ses_alanlari": {"S12": {"yatak_katmanlari": ["mekan.kulube.ocak=yanik", "hava=kar"], "surekli_nesne_sesleri": ["fener:cizirti"]}},
 "gozlenen": {"121": {"G1": {"rapor": "_RAPOR/G1_P1_B2.json", "uyum": true}, "V3": {"uyum": true, "fark": []}}},
 "dondurulmus": {"121": {"bas": "77c0a1", "bit": "8e21d0", "zaman": "2026-11-03T10:02:11+03:00"}}
}
```
- **Olay türleri:** `nesne_al`, `nesne_birak`, `nesne_ver`, `nesne_el_degis`, `nesne_durum`, `kostum_degis`, `kostum_durum`, `gorunum_degis`, `giris`,
  `cikis`, `yer_degis`, `mekan_durum`, `isik_degis`, `zaman_atla`, **`duygu_degis`** (bu belgenin eki).
- **Kurallar** ([YN2] §4.5.13): durum mirası (bir planın bitişi sonrakinin başlangıcıdır); her olayın etkili bir adımı ya da zaman atlaması kartı olur
  (yoksa K0 HATA "olgu sıçraması"); sahne sınırında kalıcı özellikler taşınır; görsel üretildiği anda plan durumu dondurulur; kurgu sırası değişince
  komşuluk dondurulmuş durumla denetlenir (Y58; kullanıcı kararından doğarsa BAYRAK); duygu zaman atlamasında `siddet` bir azalır, gerekçesiz duygu
  sıçraması BAYRAK.

### 5.3 Ders defteri
**Ham kayıt** `<veri>/BILGI/DERSLER/ham/20261103T101500_EMBERFALL_F2_kapi_hatasi.json` (her olay ayrı dosya; herkes `ders_defteri.kaydet()` çağırır):
```json
{"id": "D-20261103-0042", "zaman": "2026-11-03T10:15:00+03:00", "film": "EMBERFALL_F2", "seri": "EMBERFALL", "ortam": "yerel",
 "olay": "kapi_hatasi", "asama": "A11", "kapi": "G1", "madde": "el_nesne", "plan": 214, "kategori": "ters_el", "rol_etiketi": "goruntu",
 "kaynak": "kapi",
 "belirti": "fener istemde sol elde, iki adayda da sağ elde",
 "olcum": {"yerel": "OWLv2 bilek–nesne mesafesi sağda 0,04", "kor": "image-left hand holds lantern (iki kez tutarlı)"},
 "baglam": {"plan_tipi": "eylem", "hareket_tipi": "sabit", "kadraj": "OG", "referans": 2, "isik": "dusuk", "saglayici": "gemini_paket",
            "model": "nano-banana", "istem_bicimi": "aralik", "zincir": "bagimsiz", "derinlik": 0},
 "kanit": ["_RAPOR/G1_P2_B1.json#214"], "eylem": "CORRECTION: lantern in her LEFT hand",
 "sonuc": null, "maliyet": {"flow_kredi": 0, "gorsel": 2}}
```
- `olay` ∈ `kapi_hatasi, kapi_bayragi_dogrulandi, saglayici_red, saglayici_kisit, yeniden_cekim, kullanici_notu, seyirci_bulgusu, butce_sapmasi,
  arac_hatasi, yanlis_alarm, kacirma, pilot_olcumu, gercek_seyirci`. `kaynak` ∈ `kapi, ajan, kullanici_notu, gercek_seyirci, olcum0`; kanıt ağırlığı
  `gercek_seyirci` > `kullanici_notu` > `kapi` > `ajan`. `sonuc` sonradan `duzeldi | duzelmedi | plan_degisti` olarak doldurulur.
- **Derleme** (`ders_derle.py`, A18 ve pilot sonrası): kümeler → `ders-editoru` aday kural → korkuluk testi → `KURALLAR_OGRENILEN.json`:
```json
{"_surum": 3, "kurallar": [
 {"id": "OK-0003", "tur": "filtre_kelimesi", "deger": "cradle", "seviye": "HATA", "durum": "aktif",
  "destek": 4, "karsi": 0, "filmler": ["EMBERFALL_F1", "EMBERFALL_F2"], "kanit": ["D-20261019-0007", "D-20261103-0011"], "korkuluk": "gecti"},
 {"id": "OK-0011", "tur": "istem_eki", "kapsam": {"plan_tipi": "eylem", "kadraj": "OG"}, "deger": "the empty hand rests at her side",
  "durum": "deneme", "deneme": {"yontem": "cift_plan_no", "baslangic": "A11"}, "destek": 3, "karsi": 1},
 {"id": "OK-0014", "tur": "flow_tavan", "deger": {"gorsel_gunluk": 15}, "onceki": 20, "yon": "sikilastir", "durum": "aktif",
  "yanlis_alarm_orani": null}
]}
```
- **İzinli kural türleri:** `filtre_kelimesi, yasak_fiil, risk_desen, esik, tempo` (yalnız yavaşlatır), `flow_tavan` (yalnız düşürür), `kredi_payi,
  sure_tahmini, istem_kalibi, istem_eki, plan_kurali, yasak_kalip, yol_kurali, kara_liste, saglayici_notu, sure_carpani`.
- **Yaşam döngüsü:** aday → deneme (sonraki ≈ 40 planın yarısına, tek/çift plan no) → aktif → pasif. Terfi: destek ≥ 3 ve ≥ 2 film (tek filmde ≥ 5);
  hikâye dersleri ≥ 2 film; deneme başarısı ≥ 2/3. Emeklilik: karşı ≥ destek. **İlk filmde** yalnız sıkılaştırıcı deneme dersleri aynı filmin sonraki
  partisine uygulanabilir (D-33).
- **Korkuluklar (öğrenmeyle gevşemez):** tempo hızlandırma, Flow tavanı yükseltme, bot/uyarı/hesap/gizli bilgi/onay/silme kuralları, kalibrasyonsuz eşik
  gevşetme (kaçırma ≤ %10 kanıtı olmadan), SFace HATA eşiğinin 0,363 altına inmesi. Sıkılaştırmadan önce kalibrasyon setinde yanlış alarm ≤ %30.
- **Ajanlara veriliş:** `DERSLER_AKTIF.md`'den rol etiketine göre süzülen satırlar `GIRDI/DERSLER.md` olarak (imzaya girer); kör rollere verilmez.
  Satır biçimi: `OK-0011 · eylem/OG · "the empty hand rests at her side" · deneme · kanıt 3/1`.

### 5.4 Seri evreni kütüphanesi `<evren>/` (yalnız `evren.py` yazar; git'e yalnız JSON)
```
EVREN/EMBERFALL/
  evren.json                 seri adı, sürüm, filmler, kilit durumu
  hikaye.json                dönem, kurallar, NE YOK, kanon (yalnız eklenir), seri soruları, başlık geçmişi, ad sözlüğü (telaffuz, güvenli karşılıklar)
  dunya.json                 stil eki (ışık ifadesi yok), palet, kumaş, gerçekçilik ekleri, görsel NE YOK, renk_cila ayarı (LUT, gren, halation)
  karakterler/<id>/          karakter.json · kart_k1_v4.jpg · yuz_v4.jpg · arka_k1_v4.jpg · banka_v4.npz · hikaye.json · ses.json · ses/ (referans, merkez, model)
  mekanlar/<id>/             kroki.json · kurulumlar.json · mekan.json · plaka_*.jpg · ana_kareler/<isik>/<K>.jpg · durum_*.jpg · ses.json
  nesneler/<id>/             nesne.json · kart_olcekli.jpg · ses.json
  muzik/                     leitmotifler.json · <motif>.mid · referans çalımlar · kroma şablonları · KAYNAK_KAYDI.json
  sablonlar/                 başlık, yer/zaman kartı, jenerik şablonları; CapCut kanal düzeni
  EKRAN_YONU.json · DURUM_SON.json · KALIBRASYON.json · IZLEYICI_OZETI.md
```
`karakterler/mara/karakter.json` (görüntünün dosyası):
```json
{"id": "mara", "seri": "EMBERFALL", "tur": "insan", "surum": 4, "durum": "kilitli",
 "kimlik_en": "a lean woman with a weathered face, a pale scar through her RIGHT eyebrow, dark auburn hair in a single braid over her LEFT shoulder, grey-green eyes",
 "asimetrik": ["yara:sag_kas", "orgu:sol_omuz"],
 "ayirt_edici": [{"oge": "sag kaşta yara", "tur": "yuz", "hikaye_baglayici": true}, {"oge": "kürk yakalı deri palto", "tur": "kostum", "hikaye_baglayici": false}],
 "bilincli_benzerlik": [],
 "kostumler": {"k1": {"tarif_en": "a fur-collared brown leather coat over a wool tunic, leather gloves", "kart": "kart_k1_v4.jpg", "arka": "arka_k1_v4.jpg"},
               "k1_yirtik": {"turetildigi": "k1", "fark_en": "the LEFT sleeve torn at the elbow", "kart": "kart_k1_yirtik_v1.jpg", "olay_plani": "EMBERFALL_F2#311"}},
 "varsayilan_kostum": "k1", "yasak": ["zipper", "modern jacket", "makeup", "jewelry"],
 "boy_m": 1.70, "goz_yuksekligi_m": 1.58, "baskin_el": "sag",
 "olcum": {"yontem": "sface", "banka": "banka_v4.npz", "gorunum_sayisi": 6, "esik_gec": 0.45, "esik_hata": 0.363, "fark_payi_min": 0.05,
           "kalibrasyon_ref": "KALIBRASYON.json#mara"},
 "hikaye_ref": "hikaye.json", "ses_ref": "ses.json", "hash": "sha1:…", "gecmis": ["v3 → v4: 2026-11-01, yara belirginleştirildi"]}
```
Yaratıkta `olcum.yontem: "dinov2"`, `bulucu_sorgu`, `esik_bayrak 0,5`, `evreler{<evre>: {boy_cm, benzetme: "house cat size"}}`, `kimlik_isaretleri`
(≥ 3 sabit asimetrik işaret), `palet_lab`, `bas_govde_orani`, `davranis` sözlüğü (D-28) bulunur. `ses.json` (sesin dosyası): `profil` (aksan dahil),
`veo_ses_tarifi`, `ses_etiketi_tr`, `secim {voice_id, accent_etiketi, notice_period_gun, puan, adaylar}`, `olcum {f0, merkez, benzerlik_esigi 0,70}`,
`donusum {motor, model}`, `telaffuz_testi`, `lisans_notu`. `KALIBRASYON.json`: karakter başına kimlik bantları, alan başına kaçırma/yanlış alarm,
kör görev boyu, MediaPipe yaw işareti, etiketli örnek sayısı. `DURUM_SON.json`: son filmin bitiş durumu (sonraki filmin başlangıcı).

### 5.5 `FILM_DURUM.json` v2 ve `GOREV.json` v2
`<film>/FILM_DURUM.json` (önbellektir; git'e girmez; `film.py kurtar --yeniden-kur` görev ve rapor dosyalarından yeniden kurar):
```json
{"surum": 2, "film": "EMBERFALL_F2", "seri": "EMBERFALL", "ortam_son": "yerel", "aktif_asama": "A12",
 "otomatik_surus": {"acik": true, "neden": null, "ardisik_devam": 2},
 "asamalar": {
  "A06": {"durum": "tamam", "tur": 3, "girdi_imza": "aa01c9", "rapor": "_RAPOR/HS_KAGIT_FILM_t3.json", "hedef_alti": false},
  "A11": {"durum": "kismi", "tur": 1, "girdi_imza": "c3d4e5", "rapor": "_RAPOR/G1_FILM.json", "not": "düzeltmeler A12 tur 1'den sonra"},
  "A12": {"durum": "calisiyor", "tur": 1, "girdi_imza": "f00ba7", "rapor": null}
 },
 "donguler": {"kagit": 3, "animatik": 1, "kurgu": 0, "h15": 0, "kart_tarif": 1, "ilk2dk": 1},
 "kuresel_butce": {"animatik_kurgu_tur": {"kullanilan": 1, "tavan": 8}, "h15": {"kullanilan": 0, "tavan": 2}},
 "animatik": {"durum": "bekliyor", "imza": null},
 "bekleyen_kullanici": null,
 "sayaclar": {"gorev": 187, "ajan": 141, "betik": 44, "kullanici_eylemi": 2},
 "harcama": {"flow_kredi": 0, "ai84_kredi": 7410, "usd": 0.0,
             "token": {"girdi": 21400000, "cikti": 1830000, "onbellek_okuma": 9100000, "tahmin_orani": 0.06, "projeksiyon_film": 61000000}},
 "gecmis": [{"zaman": "2026-11-02T09:00:00+03:00", "olay": "asama_bitti", "asama": "A09"}],
 "model_sapmasi": []}
```
Aşama `durum` değerleri: `bekliyor, calisiyor, ajan_bekliyor, kullanici_bekliyor, bekle, kapi_gecmedi, kismi, tamam, bayat`.

`<film>/_GOREV/A12-AS-014/GOREV.json` (görev sözleşmesi; [CM2] §4.5.2 tabanı + `kullanim` + `persona`):
```json
{"surum": 2, "id": "A12-AS-014", "film": "EMBERFALL_F2", "asama": "A12", "tur": "ajan", "ajan": "habersiz-seyirci", "kip": "animatik",
 "persona": "A", "ornek": "yeni", "paralel_grup": "A12-t1-seyirci", "durum": "calisiyor", "deneme": 1, "deneme_max": 3,
 "asamali": {"bolumler": ["P0", "P1_1", "P1_2", "P1_3"], "acik": ["P0"], "mekanizma": "subagentstop"},
 "girdi": ["GIRDI/P0/", "GIRDI/IZLE.md", "GIRDI/SORULAR.md"], "girdi_imza": "7d1e02",
 "cikti": {"zorunlu": ["CIKTI/rapor_P0.md"], "son": ["CIKTI/rapor.json"], "sema": "seyirci_rapor_v2"},
 "tasima": {"CIKTI/rapor.json": "_RAPOR/SEYIRCI/animatik_t1/s2_rapor.json"},
 "yarim_davranisi": "sifirdan", "agent_id": null,
 "kullanim": {"girdi": null, "cikti": null, "onbellek_okuma": null, "sure_sn": null, "model": "claude-opus-5-5", "effort": "high"},
 "zaman": {"olusturma": "2026-11-05T20:11:00+03:00", "basla": "2026-11-05T20:11:09+03:00", "bitir": null}}
```
Görev `durum`: `hazir, calisiyor, bitti, gecersiz, kesildi, iptal, model_sapmasi`. `film.py sonraki` çıktısı yalnız bir sonraki paralel grubu tek JSON
olarak verir (≤ 1.200 karakter).

### 5.6 Sağlayıcı zincirleri ve ayar dosyaları
| Tür | Zincir (sırayla) | Not |
|---|---|---|
| `llm` | `claude_code` · `claude_api` (P2, başsız) · `kaset` (test) | |
| `gozlemci` | `claude_code` (`kare-tarifcisi`) · `claude_api` (P2) · `gemini_api` (yalnız ikinci göz, BAYRAK) · `sahte` | |
| `izleyici` / `dinleyici` | `gemini_api` · `sahte` | yalnız anahtar + kota/dolar izni varsa (D-19) |
| `gorsel` | `gemini_paket` (kullanıcı taşır) · `gemini_api` (Ö0-e uygunsa) · `vertex_gorsel` (dolar izni) · `sahte` | |
| `gorsel_duzeltme` | `vertex_gorsel` (dolar izni) · `flow_gorsel` (Memmet, çift çıktı, `elle`) · `sahte` | kullanıcı paketi yok |
| `video` | `flow` · `veo_vertex` (dolar izni + Ö0 fiyatı; P2) · `sahte` · `sahte_bozuk` (test) | kie.ai yok |
| `tts` | `ai84` · `sahte` | eski ad `ses` |
| `ses_donustur` | Ö0-c sırası (`openvoice` · `chatterbox` · `rvc` koşullar okununca) · `ai84_vc` (tavanlı) · `sahte` | |
| `ayristirma` / `asr` / `dudak` | `roformer` · `demucs` / `faster_whisper` (+ stable-ts) / `musetalk` · hepsinde `sahte` | Wav2Lip yok |
| `muzik` | `acestep` · `kutuphane` · `elevenlabs_muzik` (P2) · `midi_ornek` (yalnız animatik) · `sahte` | `elle = True` konamaz |
| `buyutme` | Ö0-c'de kazanan yapay zekâ büyütücü · `lanczos` · `sahte` | |

Tablodaki `sahte`, `kaset` ve `sahte_bozuk` yalnız test kipindedir (D-41).

`<veri>/AYARLAR/FILM_AYAR.json` (anahtar içermez; kurulum yazar, kullanıcı yalnız `IZINLER.bat` ile değiştirir):
```json
{"_surum": 2, "ortam": "yerel", "mod": "tam_otomatik",
 "saglayicilar": {"gorsel": ["gemini_paket"], "gorsel_duzeltme": ["flow_gorsel"], "video": ["flow"], "tts": ["ai84"],
                  "muzik": {"yayin": ["acestep", "kutuphane"], "animatik": ["acestep", "midi_ornek"]}},
 "flow": {"mod": "elle", "gece_izni": false, "model": "omni-1.1-flash", "cozunurluk": "720p", "klip_sn": 8,
          "gorsel_gunluk_tavan": 20, "gorsel_sonrasi_video_saat": 12, "haftalik_uyari_kilidi_gun": 7},
 "butce": {"flow_kredi_tavan_film": null, "guvenlik_payi": 0.10, "kapi_payi": 0.30, "take_payi_kredi": 720,
           "ai84_kredi_tavan_film": 60000, "ai84_seri_kurulum_tavan": 40000, "ai84_vc_tavan_film": 20000, "usd_tavan_film": 0,
           "takvim_hedef_gun": 21},
 "izinler": {"onayli_kip": false, "cc0_efekt_indir": false, "youtube_baglanti": false, "yukleme": false, "gemini_api": false},
 "ajan": {"paralel_max": 5}, "bildirim": {"telegram": true, "masaustu": true},
 "yayin_kaynagi": "capcut", "disk_bos_min_gb": 20}
```
`<depo>/YZ_FILM/AYARLAR/YOLLAR.json` (makineye özgü; git'e girmez; kurulum yazar): `depo_kok`, `veri_kok`, `evren_kok`, `arsiv` (D:), `gemini_paket`
(`Desktop\GEMINI GORSEL ISTEM`), `capcut_taslak`, `ses_kutuphanesi`, `onbellek` (model + pip, C'de tek klasör), `python {ana, py312, py311}`,
`ortamlar {ses_donustur, musetalk, acestep, buyutme}`. Anahtar dosyaları (AI84, Telegram, Gemini, Anthropic, Freesound, YouTube OAuth) yalnız
`<veri>/AYARLAR/` içinde ya da ortam değişkenindedir; depodaki `YZ_FILM/AYARLAR/` anahtar dosyaları boş kalır ve kurulum boş olduklarını denetler.

### 5.7 Kapı raporu ve kuyruk maddesi
`_RAPOR/<KAPI>_<kapsam>[_t<tur>].json` (bütün kapılar aynı zarf; `kapi.py` yazar):
```json
{"kapi": "G1", "kapsam": "P1_B2", "tur": 1, "sonuc": "KISMI", "girdi_imza": "c3d4e5", "esik_surum": "sureklilik@1.0+ogrenilen@3",
 "arac": "kare_denetim 1.0", "ozet": {"plan": 30, "gec": 22, "bayrak": 5, "hata": 3, "olculemedi": 1},
 "hatalar": [{"madde": "el_nesne", "plan": 214, "olcu": {"yerel": 0.04, "kor": "image-left"}, "esik": "iki kaynak", "seviye": "HATA",
              "oneri": "CORRECTION:el_nesne", "kanit": ["SIRALI_GORSEL/_ADAYLAR/214_a.jpg", "CEVAP_g07.json"]}]}
```
`KUYRUK/YENIDEN_URET.json` maddesi ([UM2] §5.4 tabanı + [KU2] alanları; bütün kapılar aynı şemayla yazar):
```json
{"id": "YU-T2-1-007", "plan": 41, "tur": "video", "kaynak_kapi": "KI", "kaynak_rapor": "_RAPOR/SEYIRCI_KARAR_T2_t1.json",
 "kok_neden": "nesne_zipladi", "seviye": "KRITIK", "seyirci_sayisi": 2, "dogrulanmis": true, "konum_agirligi": 1.5, "oncelik": 6.75,
 "cozum": "yeniden_cek", "duzeltme": "CORRECTION: the lantern stays in Mara's LEFT hand for the whole shot; her RIGHT hand is empty.",
 "sifir_kredi": {"denendi": true, "basamaklar": [1, 5, 6], "gerekce": "kusur 1,1 sn'de başlıyor; kusursuz pencere 0,6 sn < eylem planı alt sınırı"},
 "plan_metni_sahibi": "yonetmen", "zincir_etkisi": [42], "dilim": "kurgu", "kredi_tahmini": 24,
 "soy": 41, "deneme": 2, "deneme_max": 3, "is_kimligi": "9f2a1c", "durum": "bekliyor", "karar_veren": null}
```
`kaynak_kapi` ∈ `G1, G1Z, V1, V2, V3, K1, S2, S2m, S3, Z3, AI` (animatik izleme), `KI` (kurgu izleme), `KESIT`, `NOT`. `KUYRUK/YENIDEN_YAZ.json`:
`{id, konum, kapi, madde, kok_neden, yazar, oneri, tur, durum}`. Kök neden sözlüğü `YZ_FILM/ARACLAR/veri/kok_neden.json` ([KU2] + [SN2] hikâye
satırları + [SM2] ses satırları + [UM2] hat satırları).

### 5.8 Seyirci raporu `rapor.json` (bütün kipler tek şema; [SN2] §4.5.6 tabanı + [KU2] §4.5.3 + bu belgenin ekleri)
```json
{"kip": "kurgu", "tur": 1, "seyirci": 2, "persona": "A", "bolum": "P1", "parca": 3, "donen_seyirci": false,
 "puanlar": {"anlasilirlik": 8, "akicilik": 7, "merak": 8, "duygu": 7, "ritim": 6, "ilk30": 9, "GENEL": 7},
 "parca_puanlari": [{"parca": 1, "GENEL": 8}, {"parca": 2, "GENEL": 7}],
 "kopukluklar": [{"konum": {"sahne": "S05", "plan": 41, "onceki_plan": 40, "zaman": "01:01"}, "tur": "KRITIK",
                  "neden": "Kadın kapıdaydı, sonraki karede masanın yanında", "oneri": "arada yürüdüğünü gösteren bir plan"}],
 "sikilma": [{"bas": "07:40", "bit": "08:30", "neden": "aynı tartışma ikinci kez"}],
 "ilgi": [{"konum": {"zaman_bas": "00:00", "zaman_bit": "01:00"}, "puan": 9}],
 "acik_sorular": ["Kardaki ışık neydi?"], "ozet_parti": "Üç cümle.",
 "karakterler": [{"ad_ya_da_tarif": "kürk yakalı kadın", "kim": "avcı", "adi_nereden": null}],
 "kahraman_ne_kaybedebilir": "yavruyu ve köydeki yerini", "ekran_disi_sesler": [{"plan": 122, "kime_ait_sandim": "kapıdaki kadın"}],
 "gereksiz_aciklama": [{"zaman": "12:10", "neden": "aynı bilgi üçüncü kez söylendi"}], "aptal_yerine_konma": [],
 "anlasilmayan_konusmalar": [], "kapatma_ani": null, "devam_olasiligi": 0.8, "devam": true,
 "yz_kusurlari": []}
```
`yz_kusurlari` yalnız `izleyici` raporunda doludur (`{zaman, tur, siddet}`). `.md`'nin son satırı:
`OZET | anlasilirlik: 8 | akicilik: 7 | merak: 8 | duygu: 7 | ritim: 6 | ilk30: 9 | GENEL: 7 | KRITIK: 1 | ORTA: 2`. `puan_oku.py` v2 önce JSON'u, yoksa
bu satırı okur; birleştirme **medyandır**.

## 6. Kod işleri

**Öncelik:** **P0** = güvenlik, çekirdek ve kâğıt aşamaları (A00–A09); ilk film başlamadan hazır · **P1** = ilk filmin yerel aşamaları (A10–A18);
sırası Ö0 sonucuyla kesinleşir · **P2** = ilk filmden sonra ya da izne bağlı. **Ortak kurallar:** bütün araçlar `<depo>/YZ_FILM/ARACLAR/` altında,
mevcut stilde (başta Türkçe kullanım metni, `sys.stdout.reconfigure(encoding="utf-8")`, `_RAPOR/` raporu, 0–8 çıkış kodları, `--saglayici sahte`
ile ağsız çalışma, `ortak.atomik_yaz`, `_uretim` zarfı); ana ortam **Python 3.10** (3.11+ özelliği yasak: `tomllib`, `ExceptionGroup`, `typing.Self`
vb.); yollar yalnız `YOLLAR.json`'dan; anahtar yalnız `<veri>/AYARLAR/` ya da ortam değişkeninden okunur, hiçbir zaman yazdırılmaz ya da
loglanmaz. "Win/3.10" sütunu: ✓ = ana ortamda Windows + Python 3.10; "ayrı" = kendi sanal ortamında (sürümü yazılı). Lisanslar `LISANSLAR.json`'a
yazılır; "(bellekten)" işaretli lisanslar kurulumda kaynağından doğrulanır, doğrulanmazsa D-36 kuralı uygulanır. Kullanıcının arşivindeki B2/B3
betikleri (`D:\YZ_FILM_ARSIV\PROJE_B2\…\_BOLUM2\`: `parti_kur`, `parti_birlestir`, `izleme_paketi`, `dudak_denetim`, `diyalog_esitle`, `jenerik`,
`shorts_render`, `yeni_sahne_ekle`) ilk yerel geliştirme oturumunda emsal olarak okunur; yol sabitleri ve bilinen ses kusurları taşınmaz.

### 6.1 Güvenlik ve çekirdek hat
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık (lisans) | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `memmet.py` (acil yama) | değişir | `OLAGANDISI_KELIMELERI` ayrı liste → anında `Durdur(kod="olagandisi")` + `FLOW_KILIDI.json`; "olağan/unusual" `HATA_KELIMELERI`'nden çıkar; `kontrol_noktasi()` olağan dışı metinde beklemez; docstring "insan temposu" → "yük sınırı"; varsayılan 720p | Flow sayfası → `_memmet_cikis.json` | playwright (Apache-2.0) | ✓ | **P0 (PR-0)** | evet: HTML fikstürü (T10) |
| `memmet.py` v2 (memmet3 tabanlı) | değişir | `--blok <BLOK_PLANI> --onizleme <imza> --mod elle\|gece --bakiye --giris`; gönderim kaydı önce (`KREDI_DEFTERI.jsonl`), `FLOW_YUK`, `FLOW_TEMPO`'yu her gönderimden önce okur, `DUR` dosyası; filtre reddinde aynı istemi yeniden göndermez (yedek istem); zaman aşımında önce toplar; hesap kimliği sha1'i; çift çıktı görselde; `kaynak_klip` atlanır; zincir kaynağı hazır değilse ardılı almaz. "gündüz otomatik" kipi kalkar (BK §6.2 #7: 15–20 dk'da bir uyarı) | `BLOK_PLANI.json` → `SIRALI_VIDEO/`, `KUNYE/`, `_memmet_cikis.json` | playwright | ✓ | P1 | evet: fikstür + `sahte` Flow sayfası |
| `memmet_topla.py` | yeni | yeni gönderim yapmadan biten sonuçları indirir, `KREDI_DEFTERI` ile eşler; bulunamayan `kayip` | Flow projesi → `SIRALI_VIDEO/` | playwright | ✓ | P1 | evet |
| `memmet_yama.py` + `testler/test_memmet_korkuluk.py` | yeni | aday yamayı geçici kopyada uygular; korkuluk: tempo yalnız artar, uyarı kelimeleri yalnız büyür, pyautogui/pynput/SendKeys yok, yeniden deneme artmaz, `--mod` varsayılanı `elle`, `FLOW_TEMPO` okuması kalır, ≤ 80 satır | diff → GEÇ/KAL | stdlib | ✓ | P1 | evet |
| `film.py` v2 + `.claude/bin/film.py` (sarmalayıcı) | değişir/yeni | görev defteri: `yeni, sonraki, basla, calis, bitir, kurtar, asama-ilerlet, bekle, karar ekle, ders ekle, goster, ozet, surus ac/kapat, notlar oku/isle, beceri-denetim, olcum0, asamalar --md, esitle (P2)`; `onay()`/`input()` kalkar; atomik yazım + `FILM.kilit`; plan düzeyi imza; `Kisitlandi(olagandisi\|dogrulama)` sonrası sağlayıcı geçişi yok; disk ve token kapıları | görev klasörleri ↔ `FILM_DURUM.json` | stdlib | ✓ | P0 (PR-0'da Kisitlandi düzeltmesi; PR-2 çekirdek) | evet: `test_gorev_defteri` (30 kesme senaryosu) |
| `hat/asamalar.py` | yeni | `Asama(kod, ad, kim, girdiler, ciktilar, kapilar, kredi, ortam, tur_max, geri_don, gorevler)` kaydı; §1.3'ün tek kaynağı | — | stdlib | ✓ | P0 | evet |
| `ortak.py` | yeni | `atomik_yaz` (Windows'ta 3 kez kısa beklemeyle yeniden dener), `jsonl_ekle` (fsync), `imza`, `kilit`, `ortam`, `yollar`, `maskele`, `ffprobe_sure`, `disk_bos_gb` | — | stdlib | ✓ | P0 | evet |
| `esikler.py` | yeni | eşik dosyalarını yükler; `kaynak` alanı zorunlu; aynı anahtar iki dosyada HATA; `KURALLAR_OGRENILEN.json` katmanı | eşik dosyaları → sözlük | stdlib | ✓ | P0 | evet |
| `kapi.py` | yeni | ortak kapı raporu zarfı ve `sonuc` birleştirme; ÖLÇÜLEMEDİ → BAYRAK | — | stdlib | ✓ | P0 | evet |
| `kuyruk.py` | yeni | bütün kapıların maddelerini birleştirir, tekrarları ayıklar, öncelik ve zincir etkisi; **0 kredi kuralı**; dilim; soy sayacı ≤ 3; eski klibi `_ESKI/`'ye taşır | kapı raporları → `KUYRUK/*.json`, `URETIM_ONIZLEME.md` | stdlib | ✓ | P0 (şema) / P1 (video) | evet |
| `kredi.py` + `olcek.py` | yeni | B0/B1/B2/BK; dilimler; take payı; ölçek, takvim, kullanıcı el işi saati, token projeksiyonu tek kaynaktan | SAHNELER, OLCUM0, bakiye → `URETIM_ONIZLEME.json`, `_RAPOR/B*` | stdlib | ✓ | P0 | evet |
| `flow_yuk.py` | yeni | `FLOW_YUK.jsonl`, `FLOW_TEMPO.json`, `FLOW_KILIDI.json`, `HESAP_DURUMU.json`; haftalık uyarı kilidi; hesap değişimi kilidi (D-03) | — | stdlib | ✓ | P0 | evet |
| `blok_plani.py` | yeni | uygunluk kuyruğu; blok ≤ 20; önce KRİTİK yeniden çekim, sonra hikâye sırası; zincir ardılı sonraki bloğa; `--kesit` | SAHNELER, denetim → `BLOK_PLANI.json` | stdlib | ✓ | P1 | evet |
| `bildirim.py` | yeni | olay tablosu (§8.3); Telegram + masaüstü; tekrar 30 dk, saatte ≤ 12; içerikte gizli bilgi yok | olay → mesaj | requests (Apache-2.0) | ✓ | P1 | evet (`sahte` kanal) |
| `ders_defteri.py` + `ders_derle.py` | yeni | `kaydet()`; kümeleme; `DERSLER_AKTIF.md`, `KURALLAR_OGRENILEN.json`; korkuluk testi; yanlış alarm ölçümü | ham kayıtlar → derleme | stdlib | ✓ | P0 (kaydet) / P1 (derle) | evet |
| `yerel_is.py` | yeni | ağır iş kuyruğu + `GPU.kilit`; tek GPU işi; ayrı ortamları `YOLLAR.json`'dan çağırır; OOM bir kez yeniden, sonra ÖLÇÜLEMEDİ + ders | iş → çıktı | stdlib | ✓ | P1 | evet |
| `olcum0/` (`flow_deneme.py`, `ses_deneme.py`, `capcut_deneme.py`, `kanca_deneme/`) | yeni | Ö0 denemeleri ve `O0<harf>.json` | §1.2 | ilgili araçlar | ✓ | **P0** | kısmen (rapor biçimi) |
| `veri/ADLAR.json` + `testler/test_adlar.py` | yeni | ad sözlüğü ve denetimi (D-35) | — | stdlib | ✓ | P0 | evet |
| `veri/LISANSLAR.json` | yeni | lisans defteri (D-36) | — | — | — | P0 | evet (şema) |
| `veri/kok_neden.json` | yeni | kök neden sözlüğü ve sahipleri | — | — | — | P0 | evet |
| `arsivle.py` | yeni | `robocopy /E /MOVE` ile D'ye taşıma; son taslağın bağlı olduğu dosyaları atlar; taşınanların listesi | — | stdlib | ✓ | P2 | evet (kuru çalıştırma) |
| `film.py esitle` | yeni | bulut ↔ yerel beyaz listeli eşitleme | — | git | ✓ | P2 | evet |

### 6.2 Claude Code katmanı
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `.claude/settings.json` + `settings.local.json` (kurulum yazar) | yeni | `env: CLAUDE_CODE_FORK_SUBAGENT=0`; izin listesi yalnız `python .claude/bin/film.py *`; statik ret: anahtar dosyası okuma, `robocopy /MIR`; kancalar (SessionStart, UserPromptSubmit, PreToolUse × 3, SubagentStart, SubagentStop timeout 120, PostToolUse Agent, Stop, StopFailure, PreCompact, PostCompact, PostModelSwitch); `settings.local.json`: mutlak Python yolu, `additionalDirectories` (veri kökü), `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` | — | — | ✓ | P0 | evet (`test_kancalar`) |
| `.claude/hooks/kanca.py` + `.claude/bin/kanca.sh` | yeni | alt komutlar: `erisim` (görev klasörü, iki kökte AYARLAR reddi, ileri bölüm reddi, 200 KB üstü Read reddi), `komut` (gizli dosya, `robocopy /MIR`, kalıcı silme, pyautogui/pynput/SendKeys; sürüşte doğrudan `memmet.py`, Flow kilidiyken gönderim, `git push`, makine sahipli dosyaya yazma), `ajan` (kadro dışı, fork, yerleşik ajan, `calisiyor` şartı, paralel ≤ 5), `oturum_basi` (≤ 6.000 kr bağlam), `ajan_basi`, `ajan_bitti` (doğrulama, aşamalı devam, kullanım kaydı), `ajan_sonrasi`, `stop` (soru kapısı + devam kapısı, ardışık 8 + token bütçesi), `istem` ("dur/durdur/bekle" → sürüş kapanır), `hata`, `ozet_sakla`, `model_degisti`; kanca nabzı | kanca girdisi → karar | stdlib | ✓ | P0 | evet (`test_kancalar`, 50 mesajlık soru seti) |
| `.claude/kurallar/erisim.json` | yeni | rol başına okuma/yazma desenleri (kör, denetçi, yazar), gizli ve makine sahipli yollar | — | — | — | P0 | evet |
| `kor_paket.py` | yeni (`izleme_paketi.py` buraya taşınır; eski dosya v1 filmler için sarmalayıcı kalır) | kipler `kagit, plan, ilk2dk, animatik, kurgu, kesit, kesici, kapak`; beyaz liste; ad maskeleme; işitsel döküm; aşamalı parça klasörleri; persona satırı | SAHNELER, HIKAYE, medya → `_GOREV/<id>/GIRDI/` | Pillow (HPND) | ✓ | P0 (kâğıt kipleri) / P1 (izleme) | evet (`test_kor_paket`: sızıntı 0) |
| `dilim.py`, `plan_birlestir.py` | yeni | ajanlara SAHNELER/HIKAYE dilimi; planlar + ses → `SAHNELER.json` (v1 alanlarıyla uyumlu), `NO_ESLEME.json` | — | stdlib | ✓ | P0 | evet |
| `beceri_denetim.py` | yeni | SKILL.md satır/çekirdek token tahmini; ad kuralı; açıklama uzunlukları; ajan frontmatter'ı (`opus`, `effort: high`, `acceptEdits`, `memory` yok, `Bash`/`Agent` yok, kör ajanda `omitClaudeMd` + `Read, Write`); açıklama toplamı ≤ 3.000 token; şablonlardaki OZET biçimi | — | stdlib | ✓ | P1 | evet |
| 21 ajan dosyası, 4 `SKILL.md`, `KURTARMA.md`, `GOREV_SEMASI.md`, `KULLANICI_DILI.md`, `reference/*.md`, `PLAN_DILI.md`, `sablonlar/*.md`, `semalar/*.json` | yeni/değişir | §3, §4 | — | — | — | P0 | evet (`beceri_denetim`) |
| Kök `CLAUDE.md`, `YZ_FILM/ARACLAR/CLAUDE.md`, veri kökü `CLAUDE.md` | değişir/yeni | §4.7 | — | — | — | P0 | — |

### 6.3 Hikâye odası
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `hikaye_odasi.py` | yeni | `konu-denetim, butce-bilgisi, brifing, logline, oneri-denetim, juri-paketi, juri-topla, yapi-denetim, oyuncu-paketi, senaryo-denetim, seyirci-topla, ilk2dk-topla, devir, sahne-sozlesme, vaat-denetim, seyirlik-denetim` | — | stdlib | ✓ | P0 | evet (`kaset`) |
| `bulgu_yonlendir.py` | yeni (tek kod; [SN2] `bulgu-sinifla` + [KU2]) | `ozet-eslestirici·bulgu` eşlemesi + sahip tablosu + K1 eşlemesi → sahip, kök neden, merdiven önerisi | → `BULGU_YONLENDIRME_<T>_t<n>.json` | stdlib | ✓ | P0 | evet |
| `puan_oku.py` v2 (`seyirci_topla`) | değişir | **medyan**, 6 ölçüt + GENEL, KRİTİK birleştirme (±1 plan), D-21 kanıt doğrulaması, plato, personalar, tahmini tutma eğrisi, parça konum yanlılığı; eski `OZET` biçimini okur | raporlar → `SEYIRCI_KARAR_*.json` | stdlib | ✓ | **P0 (PR-1'de medyan)** | evet ({6, 8, 9} → 8) |
| `istem_denetim.py` v2 | değişir | v1 davranışı korunur; v2'de replik filtre taraması HATA, 8 sn'de ≤ 16 kelime, yasak sonuç ve iç durum fiilleri, çıplak left/right, `veo_ses_tarifi` birebir ve ≤ 12 kelime, `flow_sound` kalıbı, kimlik dizesi birebir, iki el tarifli, süren eylem fiili (görselde), referans ≤ 2 karakter, ifade sözlüğü şablonları, öğrenilen kurallar | SAHNELER → `_RAPOR/ISTEM_*.json` | stdlib | ✓ | P0 | evet |
| `evren.py` | yeni | `--kur, --bagla, --on-kayit, --spec-dogrula, --kilitle, --surum-ac, --film-sonu, --disa-aktar, --ice-al, hikaye-kaydet --dogrula, ne_yok_kelimeleri, izleyici-ozeti, ozet` | — | stdlib, numpy (BSD) | ✓ | P0 | evet |
| `veri/hikaye_esikleri.json`, `semalar/` hikâye şemaları, `JURI_TABLOSU.md`, şablonlar | yeni | [SN2] §4.7 + §7 | — | — | — | P0 | evet |
| `kanal_teshis.py` | yeni | YouTube Analytics (salt okuma OAuth varsa) ya da kullanıcının CSV'si → `KANAL_TESHIS.md` | — | google-api-python-client (Apache-2.0) | ✓ | P1 (Ö0-g) | evet (CSV fikstürü) |
| `claude_api.py` | yeni | başsız mod sağlayıcısı (effort high, yapılandırılmış çıktı); yalnız `ANTHROPIC_API_KEY` ya da `AYARLAR/anthropic_anahtar.txt` | — | anthropic SDK (MIT) | ✓ | P2 | evet (`kaset`) |

### 6.4 Yönetmen ve plan dili
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `veri/plan_sozlukleri.json`, `veri/fiil_sozlugu.json` (+ `beklenen_hiz`, `sure_carpani`), `veri/ifade_sozlugu.json` (≈ 16 değer; EN istem + kör soru karşılığı), `veri/efekt_sozlugu.json` | yeni | sözlükler | — | — | — | P0 | evet |
| `plan_sema.py` | yeni | plan şeması (v1/v2), sahiplik (`_derlenir`'e yazım HATA) | — | jsonschema (MIT) | ✓ | P0 | evet |
| `kroki.py` | yeni (kütüphane + CLI) | izdüşüm, görüş hattı, bakış/ışık/ekran yönü, göz farkı, ağız görünürlüğü, ayna yasağı, görünmesi gerekenler, plaka görüneni, yasak ardışık, `--karsilikli`, `--ciz` | kroki + plan → `_derlenir`, PNG | Pillow | ✓ | P0 | evet |
| `plan_denetim.py` | yeni | `--harita`, `--sahne`, `--tum`; Y01–Y60 + oyunculuk (ifade zorunlu, duygu sıçraması) | → `_RAPOR/PLAN_*`, `Z0_*` | stdlib | ✓ | P0 | evet (`ORNEK_3_SAHNE_ZANAAT` bozuk varyantları) |
| `plan_dili.py` | yeni | `gorunur_tarif(dil)`: EN istem cümleleri, TR kör paket metni, animatik eylem şeridi, çekim listesi | — | stdlib | ✓ | P0 | evet |
| `istem_derle.py` | yeni | `--hareket` (yönetmen), `--gorsel`, `--kart`, `--bitis` (görüntü), `--kapak`; `aralik`/`sira` biçimi; istem özeti | SAHNELER, evren → istemler | stdlib | ✓ | P0 (`--hareket`) / P1 (görsel) | evet |
| `kamera_agaci.py` | yeni | plakalar → ana kareler → türevler → planlanmış görseller; ebeveyn değişince çocuklar bayat | → `KAMERA_AGACI.json` | stdlib | ✓ | P0 | evet |
| `cekim_listesi.py`, `plan_ozellik.py` | yeni | parti çekim listesi; ders bağlamı alanları | — | stdlib | ✓ | P1 | evet |
| `zaman_cizelgesi.py` | yeni (kütüphane + CLI) | TH/T0/T1/T2/T3; olay listesi; zamana bağlı bütün ölçüler; eğri grafiği; sapma; müzik ve kart olaylarının anı; **enerji eğrisi** (T2'de görüntü + ses + kesme; T1'de ses) | → `KURGU_PLANI_<T>.json`, `ZAMAN_<T>.json`, `EGRI_<T>.png` | matplotlib (PSF tabanlı) | ✓ | P0 (T0) / P1 (T1–T3) | evet |

### 6.5 Görüntü ve süreklilik
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `dunya_defteri.py` | yeni | `--derle, --denetle (K0), --dondur, --komsuluk, --gozlenen`; duygu katmanı | planlar → `DUNYA_DEFTERI.json`, `K0_*` | stdlib | ✓ | P0 | evet |
| `kor.py` | yeni | kör soru üretimi (`_derlenir.gorunmesi_gerekenler`'den), anonim görev klasörü, cevap okuma, kişi eşleme (SFace + üçte bir), görüntü sol/sağ → anatomik çeviri, ifade sorusu | → `SORULAR.json`, karşılaştırma | stdlib | ✓ | P0 | evet |
| `kare_denetim.py` | yeni | `--yerel` (ölçüm), `--kor-gorev`, `--karar` (iki kaynak/tek kaynak/ölçülemedi; seçim sırası), `--hakem` (hakem sınırını zorlar), `--serbest` (kapak) | → `_RAPOR/G1_*`, `KUYRUK` | — | ✓ | P0 (karar) / P1 (ölçüm) | evet |
| `olcum/` paketi (`kimlik.py`, `gorunum.py`, `poz.py`, `isik.py`, `teknik.py`, `hareket.py`, `ses.py`, `dudak.py`) | yeni | YuNet + SFace (Macar eşlemesi), MediaPipe (tek sürüm), OWLv2, DINOv2-small, CLIP, Lab ΔE, keskinlik; hareket hızı/optik akış (EO4); ses: LUFS, gerçek tepe, LRA, F0, gömme, WER, VAD, kroma, BPM; dudak: jawOpen ↔ zarf | görsel/klip/wav → sayılar | opencv-python (Apache-2.0), mediapipe (Apache-2.0), torch CPU (BSD-3), transformers (Apache-2.0), scipy (BSD), pyloudnorm (MIT), librosa (ISC), jiwer (Apache-2.0); YuNet/SFace ve DINOv2/OWLv2/CLIP ağırlık lisansları (bellekten) | ✓ | P0 (`sahte` arka uç) / P1 (gerçek) | evet |
| `kart_denetim.py` | yeni | kart kapısı (yüz sayısı, öz tutarlılık, kadro ayrışması < 0,363, foto/çizim, fon, plakada kişi yok, hikâyeye bağlı ayrışma kilidi) | → `KART_KAPISI.json` | olcum | ✓ | P1 | evet |
| `duzeltme.py` | yeni | şablonlu CORRECTION (fazla_kisi, yanlis_kisi, nesne_el, bakis, isik, yasak_oge, kostum, olcek, stil, mekan, agiz, ifade) + ses şablonları | madde → cümle | stdlib | ✓ | P0 | evet |
| `kare_zinciri.py` | yeni | `--plan` (`ZINCIR_PLANI.json`, derinlik), `--cikar` (Y55 penceresinden kare; en-boy korunur) | → `SIRALI_GORSEL/<B>.jpg` | opencv | ✓ | P0 (plan) / P1 (çıkarma) | evet |
| `kalite_denetim.py` | yeni (belgede var, pakette yok) | `--klip` (V1: ffprobe, blackdetect, freezedetect, blurdetect, PySceneDetect, titreme); `--final` (siyah, donma, sessizlik, −14 ±1, ≤ −1 dBTP; ses ve kurguyla ortak) | → `_RAPOR/V1_*`, `KALITE_FINAL` | ffmpeg (LGPL/GPL derleme; dış ikili), scenedetect (BSD-3) | ✓ | P1 | evet |
| `video_denetim.py` | yeni | `--onceden` (K1ON), `--klip` (V2 + yüz izi + V3), `--dudak`, `--islem`, `--gecis` (K1) | → raporlar | olcum | ✓ | P1 (karar P0) | evet (hareketli kutu videosu) |
| `gemini_paket.py`, `gemini_al.py` | yeni (belgede var, pakette yok) | `--kartlar`, `--basamak k --aday 2`, `--kapak`, `--ikinci-goz` (yalnız API kipinde); > 10 ekte `REFERANSLAR.zip`; içe alma yalnız `_ADAYLAR/`'a; 16:9 denetimi | SAHNELER → paket klasörü; ZIP → `_ADAYLAR/` | stdlib, Pillow | ✓ | P1 | evet |
| `saglayicilar/` genişletme | değişir | türler (D-41); `Kisitlandi.kod`; `hazir()`, `birim_fiyat()`, `ortam`, `kredili`, `elle`; yeni sınıflar `gozlemci_claude_code`, `gemini_api` (gözlemci/izleyici/dinleyici/görsel), `flow_gorsel`, `vertex_gorsel` (P2), `veo_vertex` (P2), `kaset`, `sahte_bozuk` | — | — | ✓ | P0 (arayüz + sahte) / P1 | evet |
| `saglayicilar/sahte.py` | değişir | 2 aday + yan dosya; `SAHTE_HATA` enjeksiyonu; adım pencerelerinde hareketli kutu videosu; yüz izi; ağız dizisi; replik penceresinde ton; sahte CapCut taslak fikstürü | — | — | ✓ | P0 | — |
| `renk_cila.py` | yeni (sahipsizdi) | sabit LUT + gren + halation (`dunya.json`); sahne içi Lab ΔE eşleme | klipler → işlenmiş klipler | ffmpeg | ✓ | P1 | evet |
| `buyut.py` | yeni | yalnız kullanılan pencereler; 2× yapay zekâ büyütme (ayrı ortam), sonra SFace denetimi; olmazsa Lanczos + gren | → `KURGU/surumler/v<N>/buyuk/` | büyütücü (Real-ESRGAN türü, BSD-3, bellekten; ağırlık lisansı doğrulanacak) | ayrı (CUDA) | P1 | evet (`sahte`: Lanczos) |
| `kontrol.py` | değişir | `_ADAYLAR/` desteği | — | — | ✓ | P1 | — |

### 6.6 Ses ve müzik ([SM2] §4.6 aynen; ekler işaretli)
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `ai84.py` | değişir | tembel anahtar okuma (import'ta `SystemExit` yok → `Kisitlandi("anahtar_yok")`); `voices()` sayfalama/süzgeç; `estimate()` | — | requests | ✓ | **P0 (PR-1)** | evet |
| `ses_plani.py` | yeni | `--profil-denetle`, `--taslak` (yol, efekt olayları, yatak + katmanlar, `flow_sound`, sessizlik), `--denetle` (S0), `ses_tanitim_kurali()` | → `_SES/SES_<S>.taslak.json`, `_RAPOR/S0_*` | stdlib | ✓ | P0 | evet |
| `muzik.py` | yeni (`gemini_muzik.py` **yazılmaz**) | `--kagit` (S0), `--midi`, `--uret` (zincir; aday ölçümü), `--yerlestir` (olay çözümü, bar kesimi, kısma ≥ 12 dB), **kalite kapısı** (D-25) | `muzik_listesi.json` → `MUZIK/secilen/`, `KAYNAK_KAYDI.json` | mido (MIT), FluidSynth (LGPL, dış ikili; bellekten) | ✓ | P0 (`--kagit`) / P1 | evet (`midi_ornek`, `sahte`) |
| `ses_sec.py` | yeni | `--telaffuz`, `--ara`, `--olc`, `--oku`, `--puanla`, `--sec`, `--banka`; `SES_SECIM.html` (bilgi) | profiller → evren `ses.json` | olcum | ✓ | P1 | evet |
| `ses_kiyas.py` | yeni | motor kıyası (Ö0-c ve SB3) | → `_RAPOR/S1b_motor_kiyas.json` | olcum | ✓ | P1 | evet |
| `ses_donustur.py` | yeni | `--ayristir`, `--hizala` (SC1 metin kapısı), `--donustur`, `--egit` (RVC; yalnız izinle) | klip → `SESLER/ayrik`, `hizalama`, `donusum` | audio-separator (MIT), stable-ts (MIT), faster-whisper (MIT); motorlar ayrı ortamda: OpenVoice V2 (MIT), Chatterbox (MIT), RVC (MIT) | ✓ / motor ayrı | P1 | evet |
| `ses_karar.py` | yeni | ses merdiveni (§2.2) | S2/S3 → kararlar, kuyruk, `replik_kabul` görevi | stdlib | ✓ | P1 | evet |
| `seslendir.py` | değişir (yönlendirici) | `--animatik`, `--parti N`; `diyalog.json` v2; [SM2] §4.6.1 kusurları kalkar (tepe normalleştirme, atempo 0,8–1,3, kelime sayısıyla cümle bölme, sessiz oransal yayma, sessizce Flow sesine düşme, 44,1 kHz → 48 kHz, `htdemucs` → RoFormer) | → `SESLER/*`, `_RAPOR/S2*` | — | ✓ | P1 | evet |
| `ses_kutuphanesi.py` | yeni | `--dizinle` (lisans, ölçüm, anlaşılır söz taraması), `--eksik --indir` (yalnız Freesound CC0; yalnız izinle), kara liste | → `DIZIN.json` | requests | ✓ | P1 | evet |
| `diyalog_esitle.py` | yeni (belgede var, pakette yok) | replik başına LUFS hedefi (`teslim` → seviye), oda yanıtı, uzaklık, iki yol arası tını eşleme | → `SESLER/esit/`, `_RAPOR/S4_*` | pyloudnorm, pyroomacoustics (MIT) | ✓ | P1 | evet |
| `ses_katmani.py` | yeni (belgede var, pakette yok) | `--cizelge T1\|T2`: tek yatak, çapraz geçiş, efekti klibin kendi ses başlangıcına oturtma, yaratık kiti, defterden nesne sesleri, Y/CY'de nefes ve kumaş katmanı (EÇ5) | → `SES_CIZELGESI.json`, stemler | — | ✓ | P1 | evet |
| `dudak_denetim.py` | yeni (belgede var, pakette yok) | S3: ofset/güven, konuşan yüz kimliği, ekran dışı replikte oynayan dudak; SyncNet isteğe bağlı | → `_RAPOR/S3_*` | olcum | ✓ | P1 | evet |
| `son_miks.py` | yeni (**tek miks kodu**) | stem toplama, kısma, tek doğrusal kazanç + 4× gerçek tepe sınırlayıcı, ölçüm; `--animatik`, `--onizleme`, `--final` (mux ya da yalnız ölçüm), `--shorts` | stemler → `YAYIN/ses_master.wav`, `_RAPOR/S7_*`, `S8_*` | ffmpeg, numpy | ✓ | P1 | evet |
| `saglayicilar/` ses sınıfları | yeni | `openvoice`, `chatterbox`, `rvc`, `roformer`, `faster_whisper`, `musetalk`, `acestep`, `midi_ornek`, `kutuphane`, `ai84_vc` (P2), `dinleyici` | — | ayrı ortamlar: MuseTalk (Py 3.10 + torch 2.0.1; kod MIT, model "any purpose"), ACE-Step 1.5 (Py 3.11–3.12; MIT, ağırlık sayfası doğrulanacak) | ayrı | P1 | evet |
| `veri/ses_esikleri.json`, `testler/test_ses.py` | yeni | [SM2] §4.7 eşikleri; 18 bozuk girdi testi | — | — | ✓ | P0 | evet |
| MOS tahmincisi (UTMOS türü) | yeni | dönüşüm doğallığı BAYRAK (EK4-4) | wav → puan | lisans doğrulanacak | ayrı | P2 | evet |

### 6.7 Kurgu ([KU2] §4.6 aynen; ekler işaretli)
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `kirp_oner.py` | yeni | `kullanim` önerisi; adım eşleme; `--zincir` (Y55 penceresi); güven | klip + plan → kırpma | opencv, numpy | ✓ | P1 | evet (hareketli kutu ±2 kare) |
| `plan_kurgu.py` | yeni (belgede var, pakette yok) | T2: kırpma, senkron kuralıyla diyalog, ekran dışı replik, J/L, kartlar, örtü planları; ses görevlerini tetikler | → `KURGU_PLANI_T2_v<N>.json` | stdlib | ✓ | P1 | evet |
| `kurgu_uygula.py` | yeni | işlem listesi `--kuru` (SubagentStop'ta) / `--uygula`; kilitli alanlar; `*_iste` ve `yeniden_cek` kuyruklara | → yeni `KURGU_PLANI` sürümü | stdlib | ✓ | P1 | evet |
| `kurgu_denetim.py` | yeni | Z3; çizelge aritmetiği (S3.6, S3.8 dahil), Y31 ekleri, Y54/Y55, B9; komşuluk (dondurulmuş durum); `--kesme-simule`, `--hepsi` | → `_RAPOR/Z3_*`, `KESME_SIMULE_*` | stdlib | ✓ | P1 | evet |
| `kurgu_render.py` (+ `animatik.py` sarmalayıcı) | yeni | `--animatik` (Ken Burns + eylem şeridi + bitiş görseline geçiş + kartlar; yer tutucu), `--onizleme`, `--kesit`, `--yayin` (`yayin_kaynagi: master`), `--otio` (P2); plan başına önbellek; stemleri `son_miks`'ten alır; `birlestir.py` **yazılmaz** (işini bu araç yapar) | → `ANIMATIK/`, `KURGU/onizleme_v<N>.mp4`, `KESIT/` | ffmpeg, Pillow | ✓ | P1 | evet (süre = çizelge ±1 kare) |
| `capcut_film.py` | değişir | `KURGU_PLANI`'ndan sürümlü taslak; `source_timerange` = `kullanim`; sürüm klasörü; Klipler sessiz; kanallar Bantlar, Kartlar, Altyazi, Diyalog, Efekt, Ambiyans, Muzik, NOTLAR; `--yayin`; 48 kHz; geçici akor yalnız müzik yoksa `GECICI` adıyla | → taslak + `son_capcut_projesi.json` v2 | pycapcut (lisans doğrulanacak) | ✓ | P1 | evet (fikstür) |
| `taslak_fark.py` | yeni (belgede var, pakette yok) | taslağı salt okunur inceler; şifreliyi tanıyıp durur; `--oz-denetim` | → `TASLAK_FARK.json` | stdlib | ✓ | P1 | evet |
| `capcut_yama.py` | yeni | kullanıcı taslağını klonlar (kaynak yazılmaz; `kurgu_koprusu` `clone_project` emsali), bizim kanalları yamar, öz denetim | → klon + `YAMA_v<N>.json` | pycapcut | ✓ | P1 (yedek yolu var) | evet |
| `notlari_oku.py` | değişir | not ↔ `segment_id` → plan eşlemesi; `NOTLARIM.json` | — | — | ✓ | P1 | evet |
| `jenerik.py` | yeni (sahipsizdi) | jenerik görüntüsü (evren şablonu; metin `yayin-paketcisi`) ≤ 60 sn | → klip + taslak parçası | Pillow, ffmpeg | ✓ | P1 | evet |
| `shorts_mp4.py` | yeni (sahipsizdi) | 3 Short (9:16, 30–60 sn, ilk 2 sn kanca, filme bağlantı metni) + fragman (30–60 sn, dikey kesitten); doğrudan MP4; ses `son_miks --shorts` | `KURGU_PLANI` pencereleri → `YAYIN/SHORTS/`, `YAYIN/FRAGMAN/` | ffmpeg | ✓ | P1 | evet |

### 6.8 Yayın ve öğrenme
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `kapak.py` | yeni (sahipsizdi) | kapak adaylarının istemi (`istem_derle --kapak`), başlık yazısı bindirme, 1280×720 ve 168×94 önizleme, kazanan kalıp denetimi | → `YAYIN/kapak_<n>.jpg` | Pillow | ✓ | P1 | evet |
| `yayin_paketi.py` | yeni | `PAKET.json` doğrulama (başlık ≤ 100 kr, açıklama, bölümler 00:00 + ≥ 3 + ≥ 10 sn, etiketler, `yz_beyani` dolu, "kill" BAYRAK, vaat sözleşmesi) | → `_RAPOR/YAYIN_PAKET.json` | stdlib | ✓ | P1 | evet |
| `yayin_analiz.py` | yeni | 48 sa / 7 gün / 28 gün; tutma eğrisi → `KURGU_PLANI`; ders kaydı `gercek_seyirci`; erken uyarı | → `_RAPOR/YAYIN_ANALIZ_*` | google-api-python-client | ✓ | P2 | evet (CSV) |
| `youtube_yukle.py` | yeni | isteğe bağlı yükleme; her film için `YUKLE.bat` onayı | `PAKET.json` → yükleme | google-api-python-client | ✓ | P2 | evet (kuru) |
| `paketle.py` | değişir | anahtar sızıntı taraması + kaynak künyesi (`LISANSLAR.json`) | — | — | ✓ | P1 | evet |

### 6.9 Kurulum, `.bat` dosyaları, belgeler
| Dosya | Yeni/değişir | Sorumluluk | Öncelik |
|---|---|---|---|
| `kurulum.py` v2 | değişir | soru sormaz; K1 (ana ortam, CPU torch, modeller bir kez indirilir sonra `HF_HUB_OFFLINE=1`), K2/K3 (`--ses-ortamlari`, `--k3`); `YOLLAR.json`, `FILM_AYAR.json` güvenli varsayılanlar; `settings.local.json` mutlak Python yolu; `.claude/bin/python_yolu.txt`; `claude --version` ≥ 2.1.302 kaydı; git ön koşulu; disk ölçümü (önbellek boyutları dahil); depodaki anahtar dosyalarının boş olduğunun denetimi; Telegram anahtar dosyasının yalnız tarihi; "çalışıyor/çalışmıyor" kartı; `LISANSLAR.json`'a göre "bilinmiyor" lisanslı bileşeni yalnız `--deneme` | P0 (K1) / P1 (K2, K3) |
| `bat_yenile.py` | yeni | `.bat`'ları üretir: ASCII + CRLF, `chcp 65001`, `cd /d "%~dp0"`, mutlak Python yolu, tek iş; Türkçe mesajı Python yazar | P1 |
| `.bat` (depo kökü) | yeni | `FILM_SETI.bat` (Claude Code'u doğru klasörde açar), `KURULUM.bat`, `GUNCELLE.bat` (`git pull --ff-only`), `FLOW_GIRIS.bat`, `IZINLER.bat` (izin paneli; kullanıcının kendi isteğiyle), `UYARI_GECTI.bat`, `TELEGRAM_TEST.bat`, `YOUTUBE_BAGLA.bat` (isteğe bağlı) | P1 |
| `.bat` (film klasörü) | yeni | `DEVAM.bat` (`claude --continue "devam"`), `DURUM.bat`, `DURDUR.bat`, `VIDEO_YARI_OTOMATIK.bat`, `VIDEO_GECE.bat` (yalnız gece izni varsa çalışır), `VIDEO_TOPLA.bat`, `NOTLARI_OKU.bat`, `ARSIVLE.bat`, `YUKLE.bat` (P2), `FILM_DENEME_SAHTE.bat`; `KONTROL.bat` kalır | P1 |
| eski `.bat`'lar | taşınır | `MEMMET_BASLAT`, `MEMMET_SADECE_GORSEL`, `MEMMET_SADECE_VIDEO`, `CAPCUT_PROJESI_OLUSTUR`, `FILM_HATTI` → `_ESKI/` (silinmez; kapıları atlıyorlardı) | **P0 (PR-0)** |
| `BASLA_BURADAN.txt` | yeniden yazılır | kullanıcı sözleşmesi kartı (§8.1), ilk kurulum adımları, `.bat` listesi, "yalnız konu sorulur" açıklaması, izinlerin varsayılanı | P1 |
| `<veri>/BILGI/YOUTUBE_POLITIKA.md` | yeni | resmî kaynaklı politika özeti ve tarih (geliştirme oturumunda) | P1 |

### 6.10 Testler (ağ ve kredi yok; `sahte` + `kaset` sağlayıcıları)
`test_film.py` (v1 davranışı korunur; yalnız şimdi yasak olan iki beklenti güncellenir: `onay()`/`input()` testi görev defteri onayına, "kısıtlanan
sağlayıcıdan sonrakine geçer" testi `kota` koduna taşınır ve `olagandisi` kodu için "geçmez, kod 7" testi eklenir; `ORNEK_3_SAHNE` verisi değişmez) ·
`test_gorev_defteri` (30 kesme senaryosu) · `test_kancalar` (+ 50 mesajlık soru seti) · `test_kor_paket` (sızıntı 0) · `test_hikaye` · `test_plan_dili`
(+ `ORNEK_3_SAHNE_ZANAAT` bozuk varyantları) · `test_sureklilik` (K0, duygu) · `test_g1_karar` · `test_v1` · `test_zincir` · `test_kart` ·
`test_evren` · `test_ses` (18 bozuk girdi) · `test_kurgu` (16 senaryo) · `test_memmet_korkuluk` (T10: olağan dışı fikstüründe yeni gönderim 0, ≤ 10 sn
durma) · `test_flow_yuk` (haftalık kilit, hesap değişimi kilidi, mola sıfırlanmaz) · `test_adlar` · `test_uctan_uca_tam` (`ORNEK_3_SAHNE_TAM` + kaset;
A00–A17 sahte) · `test_kuyruk` (0 kredi kuralı, soy sayacı) · `test_olcek`. CI: `windows-latest` + Python 3.10 + ffmpeg ve `ubuntu-latest`;
`test_uctan_uca_tam` ≤ 5 dk, bütün takım ≤ 10 dk.

## 7. Ölçülebilir kapılar ve eşikler

### 7.1 Eşik dosyaları ve kurallar
- **Dosyalar** (hepsi `esikler.py` ile yüklenir; aynı anahtar iki dosyada HATA): `ritim_esikleri.json` (RE; ZANAAT + plan dili + kurgu + seyirci),
  `veri/hikaye_esikleri.json` ([SN2] §4.7), `veri/sureklilik_esikleri.json` ([GS2] §4.7), `veri/ses_esikleri.json` ([SM2] §4.7),
  `veri/hat_esikleri.json` ([UM2] §4.7 + token + Ö0), `<veri>/BILGI/KURALLAR_OGRENILEN.json` (öğrenilen katman, yalnız korkuluk içinde).
- **Her anahtar:** `{"deger": …, "aciklama": "…", "kaynak": "olcum|belge|tahmin", "etiket": "<belge ya da ölçüm kimliği>", "gevsetilemez": true?}`.
  RE'nin bugünkü 148 anahtarı PR-1'de bu biçime geçer: ZANAAT/BK'dan türeyenler `belge` (etiketiyle), geri kalanı `tahmin`.
- **Sonuç kodları:** **H** = HATA (kapı geçmez) · **B** = BAYRAK (sahibi ya da hakem bakar) · **ÖLÇÜLEMEDİ** = B sayılır, **asla GEÇ değildir**.
- **Kalibrasyon:** `tahmin` etiketli eşikler ilk iki filmde ölçülür; değişiklik yalnız ders defteri terfisiyle (§5.3), ≥ 30 etiketli örnekte kaçırma ≤ %10
  ve sıkılaştırmada yanlış alarm ≤ %30 kanıtıyla. `gevsetilemez: true` olanlar (Flow temposu, uyarıda dur, hesap kilidi, SFace 0,363, gizli bilgi)
  öğrenmeyle değişmez.

### 7.2 Kapı tablosu
| Kapı | Ne zaman · araç | Ölçüler ve eşikler (anahtar → değer) | H/B | Rapor |
|---|---|---|---|---|
| **ISTEM / SEMA** | A05, A07, A09 · `istem_denetim`, `plan_sema` | filtre kelimesi 0, yaş ifadesi 0 (H; v1 dosyada UYARI); RE `yasak_sonuc_fiilleri` 0, iç durum fiili 0; RE `replik_max_kelime_8sn` 16 / `replik_max_kelime` 20; RE `konusan_karede_max` 1; RE `referans_max` 2; `plan_hareket_istem_kelime_max` 75; `plan_adim_cumle_kelime_max` 16; çıplak left/right 0; `veo_ses_tarifi` ≤ 12 kelime ve birebir (S0.4–S0.5); `flow_sound` kalıbı (S0.6); `plan_istem_elle_oran_max` 0,05; `_derlenir`'e ajan yazımı 0 | H | `_RAPOR/ISTEM_*` |
| **Z0** (plan dili, T0) | A07b–c · `plan_denetim`, `kroki`, `zaman_cizelgesi` | RE `eylem_adim_max` 3, `eylem_adim_konusmali_max` 1, `eylem_adim_min_sn` 1,5, `bitis_tutma_sn` 0,5, `kamera_hareketi_klip_max` 1, `plan_sure_aralik_sn`, `ayni_plan_tipi_ardisik_max` 4, `ayni_kamera_konumu_ardisik_max` 2, `olcek_kademe_min_fark` 2, `aci_min_fark_derece` 30, `sahne_konum_plani_max_sira` 3, `sahne_yeniden_konum_sn` 90, `plan_sayisi_tolerans_oran` 0,15, `sahne_max_sn` 180, `sahne_tipi_aralik`, `monolog_ardisik_plan_max` 3; [YN2] Y01–Y60 (yeni anahtarlar §7.3); `ifade_zorunlu_insanli_plan` | H/B (Y kuralının kendi kodu) | `_RAPOR/Z0_P<n>.json` |
| **Z1** (hikâye zamanları; TH, T0–T3) | A05, A07c, A12, A16 · `zaman_cizelgesi` | RE `ilk_eylem_max_sn` 5, `ilk_merak_max_sn` 20, `ilk30_manzara_plan_max` 1, `ilk30_manzara_sure_max_sn` 3,0, `baslik_karti_aralik_sn` [45, 120], `baslik_karti_sure_max_sn` 6, `vaat_imgesi_max_sn` 120, `kahraman_adi_max_sn` 120, `ad_ilk_gorunus_max_sahne` 2, `risk_sozlu_max_sn` 180, `parti_basi_risk_tazeleme_max_sn` 60, `parti_basi_kanca_donus_max_sn` 20, `seri_kancasi_max_sn` 20, `jenerik_max_sn` 60, `merak_olay_aralik_max_sn` 90, `acik_soru_aralik` [1, 5], `soru_omru_max_sn`, `seri_sorusu_max` 2, `cevap_yeni_soru_max_sn` 30, `kurulum_kullanim_min_sn` 20, `hatirlatma_esigi_sn` 600, `bilgi_tekrar_max` 2, `ironi_parti_min` 1, `ironi_sure_aralik_sn`, `sahne_yeni_ad_max` 2, `konusan_karakter_max` 8, `diyalog_yeni_bilgi_max_sn` 60, `gerilim_yeni_ayrinti_max_sn` 20, `bilgisiz_gecis_max_sn` 15, `geri_donus_max_sn` 20; hikâyede ±%15 belirsizlik bandı (bant dışı H, içi B) | H (#21, #23, #24, #28–32) / B | `_RAPOR/ZAMAN_<T>.json` |
| **Z2** (duygu ve enerji eğrisi) | A07c, A12, A16 · `zaman_cizelgesi` | RE `duygu_haritasi_40dk`, `yogunluk_sapma_max` 2 / `yogunluk_sapma_sure_max_sn` 60, `pencere_tepe_sn` 180 / `pencere_tepe_min` 6, `duz_cizgi_max_sn` 180, `ayni_duygu_ardisik_dk_max` 2, `tepe_esigi` 8, `tepe_oncesi_cukur_pencere_sn` [60, 120] / `tepe_oncesi_cukur_min_dusus` 2, `parti_sonu_yogunluk_min` 8, `doruk_yogunluk_min` 9, `en_karanlik_yogunluk_min` 6, `tepe_oncesi_asl_dusus_min` 0,25; `enerji_duz_max_sn` 180 (±%10 bant; T2 görüntü + ses + kesme, T1 yalnız ses); `seyirlik_an_parti_min` 2, `gosterisiz_aralik_max_sn` 360 | B / H (#39) | `_RAPOR/ZAMAN_<T>.json`, `EGRI_<T>.png` |
| **Z3** (kurgu) | A16 · `kurgu_denetim` | RE `film_sure_aralik_sn` [1800, 2700], `parti_sure_oran_aralik` [0,30, 0,35], `vurus_oranlari` ±`vurus_oran_tolerans` 0,04, `asl_film_aralik_sn` [4,2, 5,2], `asl_parti_hedef_sn` ±`asl_parti_tolerans_sn` 0,6, `ilk120_asl_max_sn` 4,0, `ilk30_asl_max_sn` 3,5, `tepki_orani_min` 0,25, `jl_kesme_orani_min` 0,30, `j_kesme_aralik_sn`, `l_kesme_aralik_sn`, `replik_sonu_kesme_sn`, `cevap_boslugu_sn` [0,2, 0,6], `kullanim_bas_min_sn` 0,3, `kullanim_son_pay_sn` 0,5, `olu_sure_max_sn` 0,6, `kesme_ilk_duragan_yasak_sn` 0,3, `klip_bolme_atlama_min_sn` 0,4, `klip_bolme_min_kullanilabilir_sn` 6,0, `bakis_tutma_min_sn` 0,5, `eslesme_gecis_orani_min` 0,15, `sert_kesme_parti_max` 4, `duygu_tutma_film_max` 25, `duygu_tutma_ardisik_max` 1; `senkron_tolerans_kare` 1; L/J ekleri (`l_kesme_*`, `j_kesme_klip_kosulu`); B9 (dudağı oynayan yüze başka replik) 0; Y54/Y55; geri gidiş 0; render = çizelge ±1 kare | H/B | `_RAPOR/Z3_v<N>.json` |
| **K0** (kâğıt süreklilik) | A07c · `dunya_defteri` | [GS2] K0.1–K0.19 (olgu sıçraması, el/nesne, kostüm, sahne ucu eşitliği, görüş hattı, 180°, bakış, ışık, kart kapsamı) + `duygu_sicramasi_gerekcesiz` 0 (B) | H/B | `_RAPOR/K0_FILM.json` |
| **KART** | A10d · `kart_denetim`, `kare_denetim` | [GS2] kart kapısı: yüz sayısı = görünüm sayısı; SFace öz tutarlılık ≥ 0,45; kadro ötekilerine < 0,363 (hedef < 0,25); foto/çizim (CLIP); düz fon; plakada kişi/yüz 0; NE YOK 0; hikâyeye bağlı öğe uyuşmazlığı 0; yaratıkta ≥ 3 asimetrik işaret | H/B | `_RAPOR/KART_KAPISI.json` |
| **G1** | A11 · `olcum` → `kare-tarifcisi` → `kare_denetim --karar` → hakem | [GS2] G1 tablosu: 16:9 ±%1, kısa kenar ≥ 720; YuNet ≥ 0,9 ve yüz ≥ 48 px; SFace GEÇ ≥ 0,45, HATA < 0,363 (`gevsetilemez`), fark payı ≥ 0,05; fazla yüz H, eksik yüz B; kadraj sırası H; yaw > 15° H; el–nesne iki kaynak H / tek B; ağız kapalı jawOpen ≤ 0,15 (konuşan planda) B; konuşan yüz ≥ %12 ve \|yaw\| ≤ 45° B; açık parmak B (kalibrasyon ≥ %90 → H); yaratık DINOv2 < 0,5 B (kalibrasyonla H); ölçek ±%35 B; mekân < 0,60 B; ışık B; Lab ΔE > 10 B; stil < 0,5 + kör "çizim" H; yazı/logo H; yasak öğe H; keskinlik < 0,5 B; kör iki cevap uyuşmazlığı B; **ifade uyumu** B (`ifade_uyum_min_oran` ≥ 0,85, film düzeyi); 2 aday × ≤ 2 düzeltme turu | H/B | `_RAPOR/G1_P<n>_B<k>.json` |
| **G1Z** (zincir karesi) | A14 · `kare_zinciri --cikar` | kimlik bantları (G1 ile aynı); keskinlik ≥ 0,6 × A'nın ilk karesi B; V3 gözlemi ±0,2 sn H; kişi sayısı H; B'nin planlanmış görseline DINOv2 < 0,70 B; `zincir_cikis_tutma_ic_min_sn` 0,2; `zincir_derinlik_max` 2 | H/B | `_RAPOR/G1Z_*` |
| **K1ON / K1** | A11 sonu / A16 · `video_denetim --onceden / --gecis` | `devam` DINOv2 < 0,80 H, parlaklık > 12/255 B; aynı mekân kesmesi Lab ΔE > 10 / parlaklık > 20/255 B; kurulum dönüşü ana kareye < 0,70 B; kostüm < 0,6 B; dondurulmuş olgu eşitliği H (kullanıcı kararında B). Bulgular seyirciye verilmez | H/B | `_RAPOR/K1ON_P<n>.json`, `K1_v<N>.json` |
| **V1** | her indirme · `kalite_denetim --klip` | `blackdetect d=0.1 pic_th=0.98 pix_th=0.10`, `freezedetect n=-60dB d=1.0`, `blurdetect`, PySceneDetect ContentDetector(27), titreme MAE; süre ≥ 7,5 sn (kesik indirme); kusur kullanılan pencerenin dışındaysa `cozum: kirp` (madde açılmaz) | H/B | `_RAPOR/V1_B<k>.json` |
| **V2** | blok arası · `video_denetim --klip` | 17 kare / 0,5 sn: kimlik düşüşü > 0,15 ve < 0,363 H; yüz/kişi sayısı değişimi H; DINOv2 sıçraması > 0,15 B; ekran yönü H; ilk kare sadakati < 0,85 B; **hareket hızı** `beklenen_hiz` dışında B (EO4); yüz izi `V2_P<n>/NNN_yuz.jsonl` | H/B | `_RAPOR/V2_*` |
| **V3** | blok arası · `video_denetim --klip` + `kare-tarifcisi·v3` | kesme anındaki kare kör gözlemi ↔ `bitis_durumu` kritik olguları H; adım enerji tepesi sapması ≤ 1,0 sn (`plan_zincir_zaman_sapma_max_sn`) B; dirsek > 140° B; son 0,5 sn MAE ≤ medyanın %50'si B; replik ortası ve sonunda ifade uyumu B | H/B | `_RAPOR/V3_*` |
| **S0–S8** (ses) | A06s, A08 (S0); A10 (S1); A14–A15 (S2, S2m); A16 (S3–S7); A17 (S8) · ses araçları | [SM2] §4.7.1–4.7.8 aynen (S0.1–S0.21, S1.1–S1.12, S2.1–S2.16, S3.1–S3.8, S4.1–S4.5, S5.1–S5.11, S6.1–S6.10, S7.1–S7.9, S8.1–S8.2); RE eşleri: `diyalog_lufs` {fısıltı −24, yumuşak −21,5, normal −19,5, bağırma −17} ±`diyalog_lufs_tolerans` 1, `ambiyans_diyalog_alti_db` [12, 18], `efekt_diyalog_alti_db` [3, 10], `muzik_diyalog_alti_min_db` 12, `muzik_diyalogsuz_lufs` [−20, −16], `final_lufs` −14 ±`final_lufs_tolerans` 1, `true_peak_max_dbtp` −1, `ambiyans_sahne_ici_fark_max_lu` 3, `ambiyans_capraz_gecis_sn`, `ses_koprusu_sn`, `mutlak_sessizlik_db` −50 / `_max_sn` 1,0 / `_film_max` 2, `vurgu_sessizlik_sn`, `muzik_kaplama_oran` [0,40, 0,65], `muziksiz_blok_max_sn` 240, `muzikli_blok_max_sn` 300, `muzik_giris_sn`, `muzik_cikis_sn`, `leitmotif_donus_min` 3, `konusma_hizi_kelime_sn` 2,5; S3.6 ve S3.8 ölçümü `kurgu_denetim`'de (D-32); ek: `muzik_kalite_ikili_min` ≥ 0,5 B, `ses_dogallik_mos_min` B (P2) | H/B | `_RAPOR/S<n>_*` |
| **HS_KAGIT, HS_PLAN, HS_ANIMATIK, HS_KESIT, HS_KURGU** | A06, A07e, A12, A14a, A16 · `seyirci_topla` | **Kapı:** `seyirci_kapi_genel_min` 7, RE `kopukluk_kritik_max` 0, `ozet_eslesme_kritik_min` 0,80. **Hedef:** RE `seyirci_genel_esik` 8, `seyirci_olcut_min` 7, `seyirci_olcut_hedef`, `kopukluk_orta_max_parti` 3, `ozet_eslesme_min` 0,80, `ilk2dk_devam_evet_min` 3. RE `seyirci_sayisi` 3, `seyirci_karar` medyan, `sikilma_ortak_isaret_min` 2, `kagit_tur_max` 4, `kurgu_tur_max` 3, `kesme_turu_oneri` {10 plan, 2 sahne, uygulama ≥ 0,5; payda simülasyondan HATA'sız geçenler}; `plato_genel_artis_min` max(0,5; `seyirci_gurultu_std`); `ilgi_korelasyon_min` 0,5 B; `parca_konum_egim_bayrak` −0,15 B; `gorsel_tasima_orani_min` 0,5 B | H (kapı) / hedef | `_RAPOR/HS_*`, `SEYIRCI_KARAR_*` |
| **HS_KAPAK** | A11 · `habersiz-seyirci·kapak` + `kare-tarifcisi·kapak` | `kapak_aday_min` 8; `kapak_kucuk_okunurluk` (168×94'te yüz ve yaratık seçiliyor) H; anatomi/yazı/kimlik H; ikili karşılaştırma kazananı | H/B | `_RAPOR/KAPAK_*` |
| **B0 / B1 / B2 / BK** | A01 / A07c / A13 / her kredili madde · `kredi.py` | `kapi_payi` 0,30; `kredi_yeniden_deneme_payi` (RE) 0,20 hedef; dilimler `yeniden_pay_dilim` {görüntü 0,15, ses 0,07, kurgu 0,08}; `take_payi_kredi` 720; `guvenlik_payi` 0,10 (B2: tahmin ≤ bakiye × 0,9 ve ≤ tavan); `kredi_klip_720p` (RE) 12; `plan_basi_yeniden_cekim_max` 2 (soy toplam 3); AI84 tavanları 60.000 / 40.000 / 20.000; `usd_tavan_film` 0 | H | `_RAPOR/B*_FILM.json` |
| **FLOW** (yük) | her gönderim · `flow_yuk`, Memmet | gece 12–30 sn, aynı anda 2, iki partide bir 15–30 dk mola; gündüz 6–15 sn; 8 gönderimde 3–6 dk mola (17.10; `gevsetilemez`); `gorsel_gunluk_tavan` 20 (tahmin); `gorsel_sonrasi_video_saat` 12 (tahmin); `haftalik_uyari_kilidi_gun` 7 (tahmin); `uyari_sonrasi_bekleme_dk` 30; uyarıda yeni gönderim 0 ve ≤ 10 sn'de dur; hesap değişimi kilidi 14 gün (tahmin) | H | `HESAP/FLOW_*`, `_memmet_cikis.json` |
| **PILOT / KESIT** | A14a · `pilot_sec`, kapılar | kapsama listesi (D-17); kesit seyircisinde KRİTİK 0; teknik kapılar HATA 0; take kararı `take_ikinci_secim_min_oran` 0,30 (tahmin); canlı bekleme `canli_bekleme_ab_fark_max` 0,02 | H/B | `_RAPOR/PILOT_FILM.json` |
| **YAYIN** | A17 · `kalite_denetim --final`, `yayin_paketi` | final −14 ±1 LUFS, ≤ −1 dBTP; siyah/donma/planlanmamış sessizlik 0; `mux_ofset_max_kare` 1, `mux_korelasyon_min` 0,9, `mux_pencere` 40 × 10 sn; `yayin_sure_tolerans_kare` 1; başlık ≤ 100 kr; bölüm adı kuralları (RE `bolum_sayisi_max` 8); `yz_beyani` dolu; Shorts −14 ±1 LUFS | H | `_RAPOR/YAYIN_*` |
| **HAT** | A13, pilot sonrası, kuyruk > 30 klip, dilim aktarımı · `hat-denetcisi` | `hat_denetcisi_kuyruk_esigi` 30 | GİT/GİTME | `_RAPOR/HAT_*` |
| **DISK / TOKEN** | her aşama başı · `film.py` | `disk_bos_min_gb` 20 (tahmin); `gorev_tavani_carpan` 1,5 (tahmin); `stop_ardisik_max` 8 | 8 BEKLE | `FILM_DURUM` |

### 7.3 `ritim_esikleri.json`'a eklenecek anahtarlar (bu belgenin kararı; hepsinde `kaynak` ve `etiket`)
| Anahtar | Değer | Sonuç | Kaynak |
|---|---|---|---|
| `plan_adim_min` | 2 | H | [YN2] Y01 (belge: KK2) |
| `plan_ilk_adim_min_sn` / `plan_son_adim_pay_sn` | 0,5 / 1,0 | B / H | [YN2] Y04, Y05 (tahmin) |
| `plan_es_zamanli_ozne_max` | 1 (yalnız **durum değiştiren** adım) | B | [YN2] Y06 + [ESY] EK2-5 (tahmin) |
| `plan_konusma_adim_arasi_min_sn` | 0,2 | B | [YN2] Y02b (tahmin) |
| `plan_goz_farki_bakis_m` / `plan_goz_yukseklik_m` | 0,3 / evren değeri | B | [YN2] Y25 (tahmin) |
| `plan_konusan_yaw_max` / `plan_konusan_yuz_oran_min` | 45 / 0,12 | B | [YN2] Y32 (tahmin) |
| `plan_bitis_ozel_oran_max` | 0,10 | B | [YN2] Y42 (tahmin) |
| `plan_agac_derinlik_max` / `zincir_derinlik_max` | 3 / 2 | B / H | [YN2] Y43; AR2 §2.3 |
| `devam_kesme_tutma_min_sn` / `zincir_cikis_tutma_ic_min_sn` | 0,2 | H | [YN2] Y55 (tahmin) |
| `ortulu_devam_araya_min_sn` + `ortu_min_sn` formülü | 1,0; max(1,0; A tutma + B durağanlık) | B | [YN2] Y54 + [KU2] İ-11 (tahmin) |
| `plan_hareket_istem_kelime_max` / `plan_adim_cumle_kelime_max` | 75 / 16 | B | [YN2] Y46 (tahmin) |
| `plan_istem_elle_oran_max` | 0,05 | B | [YN2] (tahmin) |
| `plan_dialog_kurulum_min` | 3 | B | [YN2] Y50 (tahmin) |
| `plan_zincir_zaman_sapma_max_sn` | 1,0 | B | [YN2] (tahmin) |
| `ifade_zorunlu_insanli_plan` | evet ("notr" gerekçeli) | H | [ESY] EK2 (belge: bu karar) |
| `ifade_uyum_min_oran` | 0,85 | B | [ESY] (tahmin) |
| `duygu_sicramasi_gerekcesiz` | 0 | B | [ESY] (tahmin) |
| `teslim_sozluk_boyutu` | 12 | — | D-22 |
| `take_kapsami_plan_max` / `take_ikinci_secim_min_oran` | 60 / 0,30 | — | D-23 (tahmin) |
| `canli_bekleme_ab_fark_max` | 0,02 | — | [ESY] (tahmin) |
| `seyirlik_an_parti_min` / `gosterisiz_aralik_max_sn` / `vitrin_plan_max_sn` | 2 / 360 / 7 | B | [ESY] EO1 (tahmin) |
| `gorsel_tasima_orani_min` | 0,5 | B | [ESY] EO2 (tahmin) |
| `enerji_duz_max_sn` | 180 (±%10) | B | [ESY] EO9; süre RE `duz_cizgi_max_sn` ile aynı |
| `seyirci_kapi_genel_min` / `ozet_eslesme_kritik_min` | 7 / 0,80 | H | D-20 (belge: BK §3 #9 "süper" = 7) |
| `plato_genel_artis_min` | 0,5 (ya da ölçülen `seyirci_gurultu_std`) | — | D-20 (tahmin) |
| `seyirci_persona_izleme` | {A: 2, B: 1} | — | D-18 |
| `izleme_parcasi_sn` / `izleme_kare_plan` / `izleme_sayfa_plan` | [240, 300] / kurgu 3, animatik 1 / 6 | — | [KU2] (BK §3.8; tahmin) |
| `animatik_tur_max` / `animatik_kurtarma_tur` / `kurgu_kurtarma_tur` | 3 / 1 / 1 | — | §1.5 (küresel toplam 8) |
| `kurgu_kurtarma_kosul_genel_artis` | 0,5 | — | [KU2] (tahmin) |
| `animatik_yer_tutucu_max_oran` / `animatik_tur1_yer_tutucu_max_oran` | 0,10 / 0,15 | H | [KU2] / D-14 (tahmin) |
| `animatik_bitis_gecis_sn`, `ken_burns_zoom`, `ken_burns_kayma` | 0,5; 0,08; 0,02 | — | [KU2]; kurgu köprüsü V5 |
| `render_sure_tolerans_kare` / `senkron_tolerans_kare` | 1 / 1 | H | [KU2] (hesap; AR3) |
| `sapma_plan_oran_max` | 0,25 | B | [KU2] (tahmin) |
| `l_kesme_gorunen_konusma_min_sn` / `l_kesme_klip_ses_son_pay_sn` / `l_kesme_alici_plan_ek_sn` | 1,0 / 0,3 / 0,5 | H | [KU2] (tahmin; RE `diyalog_cikis_payi_sn`) |
| `kirp_guven_min` / `kirp_hareket_mad_k` / `kirp_hareket_sure_sn` | 0,6 / 3 / 0,2 | B / — | [KU2] (tahmin) |
| `hiz_aralik_diyalogsuz` / `yeniden_kadraj_max` | [0,90, 1,15] / 0,10 | H | [KU2] (tahmin) |
| `tepe_sonrasi_uzun_plan_pencere_sn` | 20 | B | [KU2] (tahmin) |
| `oncelik_konum_agirligi` / `oncelik_dogrulanmis_carpan` | 1,5 / 1,25 | — | [KU2] (tahmin) |
| `ilgi_korelasyon_min` / `ilgi_dusuk_esik` / `parca_konum_egim_bayrak` | 0,5 / 4 / −0,15 | B | [KU2] (tahmin) |
| `ozet_kismen_agirlik` / `anlasilmayan_konusma_wer` | 0,5 / 0,30 | — | [KU2]; [SM2] S7.6 |
| `kopru_replik_sahne_max` / `is_yaparken_konusma_sahne_min` | 1 / 1 | B | [SN2] H15 / [ESY] EO3 (tahmin) |
| `mux_ofset_max_kare` / `mux_korelasyon_min` / `mux_pencere` / `yayin_sure_tolerans_kare` | 1 / 0,9 / 40 × 10 sn / 1 | H | [KU2] (tahmin) |
| `kapak_aday_min` / `kapak_kucuk_okunurluk` | 8 / 168×94'te seçilebilir | — / H | [ESY] EK5 (tahmin) |

`hikaye_esikleri.json` ([SN2] §4.7 listesi aynen: sahne sayısı 45–55, replik kelimesi 2.100–2.600 (40 dk), anahtar olgu 8–12/parti, ad kuralları, jüri
kazanan ≥ 8,0, doktor tetiği, kopru replik ≤ 1 vb.), `sureklilik_esikleri.json` ([GS2] §4.7 aynen), `ses_esikleri.json` ([SM2] §4.7 aynen),
`hat_esikleri.json` ([UM2] §4.7 aynen + `gorev_tavani_carpan`, `stop_ardisik_max`, `disk_bos_min_gb`, `haftalik_uyari_kilidi_gun`,
`hesap_degisim_kilidi_gun`, `seyirci_gurultu_std` (Ö0-f yazar), `olculen_gunluk_kapasite` (Ö0-b yazar)).

### 7.4 Başarı ölçütleri (film düzeyi; `FILM_SONU_RAPORU.md` yazar)
| # | Ölçüt | Hedef | Kaynak |
|---|---|---|---|
| M1 | Kullanıcıya sorulan karar sorusu | 1 (yalnız konu) | KK1 |
| M2 | Kullanıcının el işi | sayısı ve saati baştan yazıldı; gerçekleşen ölçüldü | D-06 |
| M3 | Kapısız kredi harcaması / çift harcama | 0 / 0 | [UM2] |
| M4 | Flow uyarısından sonra yeni gönderim | 0; ≤ 10 sn'de dur | KK5 |
| M5 | Videoya giden karelerde G1/G1Z GEÇ + SHA1 eşleşmesi | %100 | [GS2] B1 |
| M6 | Görsel kaynaklı KRİTİK / parti | 0 | [GS2] B2 |
| M7 | Yeniden çekim oranı | ≤ %20 hedef; kapı payı %30 | RE, [UM2] |
| M8 | Kurgu: senkron ±1 kare; dudak ofseti ≥ %95 ≤ 42 ms; dudağı oynayan yüze başka replik 0 | — | [KU2] B8–B9, [SM2] B1 |
| M9 | Ses kimliği ≥ 0,70 (tahmin) %100; aynı karakter filmden filme aynı ses ve aksan | — | [SM2] B3, B5 |
| M10 | Final −14 ±1 LUFS, ≤ −1 dBTP; Shorts aynı | — | RE |
| M11 | Seyirci kapıları | kapı her aşamada; hedef (GENEL ≥ 8) ve `hedef_alti` sayısı raporlanır | D-20 |
| M12 | Habersizlik sızıntısı | 0 | [KU2] B15 |
| M13 | Kredi tahmin isabeti | gerçek / tahmin ∈ [0,90; 1,15] | [UM2] M6 |
| M14 | Ö0 ve pilot kararlarının hepsi gerekçeyle defterde | %100 | D-01, D-17 |
| M15 | Gerçek seyirci verisi (yayın sonrası) | tutma eğrisi plan kimliğiyle defterde (bağlantı varsa) | D-24 |

## 8. Kullanıcının yapacakları

### 8.1 Kullanıcı sözleşmesi kartı (`BASLA_BURADAN.txt`'nin başı ve kurulum sonu ekranı; sayıları `olcek.py` doldurur)
```
SENDEN İSTENEN TEK KARAR: filmin konusu (bir cümle). Gerisini ekip karar verir; sana "hangisi?" diye sorulmaz.
SENDEN İSTENEN FİZİKSEL İŞLER (bu film için tahmini; film başında güncellenir):
  • Flow'a Google ile giriş ve gerekirse "ben robot değilim" doğrulaması ............ kurulumda 1 kez + istendikçe
  • Gemini paketlerini taşımak (klasörü Gemini'ye ver, gelen ZIP'i GELENLER'e at) ..... ≈ {paket} paket (Gemini API bağlıysa 0)
  • Video oturumları: VIDEO_YARI_OTOMATIK.bat'ı aç, Memmet hazırlayınca GÖNDER'e bas .. ≈ {gonder} kez, ≈ {video_gun} gün, günde ≈ {saat} saat
  • CapCut'ı kapatıp açmak (taslak güncellenince) ve sonunda 4K 24 fps dışa aktarmak .. ≈ 2–4 kez + 1 dışa aktarım
  • Flow uyarı verirse: beklemek, elle 1 video denemek, UYARI_GECTI.bat ................ yalnız uyarı olursa
  • Kredi biterse yüklemek ............................................................ yalnız gerekirse
TAHMİNİ TOPLAM EL İŞİ: ≈ {el_isi_saat} saat · TAHMİNİ TAKVİM: ≈ {takvim_gun} gün (Flow'un günlük güvenli kapasitesine bağlı)
İSTERSEN (hiçbiri zorunlu değil, sistem beklemez): film hakkında not bırakmak (CapCut NOTLAR ya da sohbet), izinleri açmak (IZINLER.bat:
gece çalışma, dolar harcama, efekt indirme, YouTube bağlantısı, yükleme), kanal verisini bağlamak (YOUTUBE_BAGLA.bat).
SİSTEM ASLA: Flow uyarısını atlatmaz, hızlandırmaz, başka hesaba geçmez; anahtarlarını okumaz ya da yazdırmaz; dosya silmez.
```
Gerçekleşen el işi `FILM_SONU_RAPORU.md`'de tahminle karşılaştırılır (D-06, [SA] K-2 #3).

### 8.2 Bir kez (kurulum)
| Adım | Kullanıcının yaptığı | Sistemin yaptığı | Ne zaman çağrılır |
|---|---|---|---|
| 0 | Depoyu indirir (GitHub'dan ZIP ya da `git clone`) ve `Desktop\YZ_FILM_SET`'e açar; veri klasörü `Desktop\YZ_FILM` olduğu gibi kalır | — | ilk kez, bir defa |
| 1 | `KURULUM.bat`'a çift tıklar | K1 kurulumu (ana Python 3.10 ortamı, CPU torch, modeller), `YOLLAR.json`, güvenli `FILM_AYAR.json`, `settings.local.json`, sürüm ve disk ölçümü, "çalışıyor/çalışmıyor" kartı; soru sormaz | ilk açılışta |
| 2 | (gerekirse) git kurar | git yoksa kurulum raporu tek cümleyle ne yapılacağını söyler | kurulum raporunda |
| 3 | `FLOW_GIRIS.bat` ile Flow'a Google'la girer | oturumu Memmet profilinde saklar; hesap kimliğinin yalnız sha1'ini kaydeder | kurulumda ve oturum düşünce |
| 4 | (isteğe bağlı) Telegram bot anahtarını `<veri>/AYARLAR/telegram_bot.txt`'ye yazar, `TELEGRAM_TEST.bat` | dosyanın yalnız varlığını ve tarihini denetler, içeriği okumaz | — |
| 5 | (isteğe bağlı) `YOUTUBE_BAGLA.bat` (salt okuma) | Ö0-g kanal teşhisi; yayından sonra analiz | — |
| 6 | Ö0 ölçüm turunda: 3 ayrı günde video oturumu (GÖNDER), 1 Gemini paketi, CapCut'ı bir kez kapatıp açmak | Ö0-a…h ölçümleri ve `OLCUM0.json` | ilk filmin kâğıt aşamalarıyla paralel; her iş Telegram'la bildirilir |
| 7 | (gerekirse) K2/K3 için ek Python kurulumuna izin veren Windows penceresini onaylar | ses dönüştürme, MuseTalk, ACE-Step, büyütücü ortamları (yalnız gerektiğinde) | A10a'da |

### 8.3 Her film
| Ne zaman | Kullanıcının yaptığı | Sistemin mesajı (bilgi; soru değil) | Kanal |
|---|---|---|---|
| A00 | konuyu bir cümleyle söyler (ya da "sen seç") | — | sohbet |
| A01 sonu | — | "Konu kartı hazır: <tür, kanca>. Süre: 30 dk (Flow kapasitesi henüz ölçülmedi). Kâğıt aşaması ≈ 1–3 gün." | sohbet + Telegram |
| A06 sonu | — | "Senaryo kilitlendi: '<başlık>'. Seyirci puanı 8/8/9. Şimdi yönetmen planları." (hedefin altındaysa açıkça yazar) | sohbet + Telegram |
| A10d, A11 (her paket) | Gemini paketini taşır | "Gemini paketi 3/12 hazır: Masaüstü\GEMINI GORSEL ISTEM\<FILM>_K2_03 klasörünü Gemini'ye ver, gelen ZIP'i GELENLER'e at." Bitiş ZIP gelince kendiliğinden algılanır; 6 saat sonra 1 hatırlatma | sohbet + Telegram |
| A12 sonu | (isteğe bağlı) animatik paketini izler | "Animatik geçti (8/7/8). İzle-dinle paketi masaüstünde: <yol>. Not bırakırsan işlerim; bırakmazsan devam ediyorum." | Telegram (dosya) + masaüstü |
| A13 | — | "Video için ≈ 4.750 kredi gerekiyor; hesapta 6.100 var. Takvim ≈ 18 video günü." | sohbet + Telegram |
| A14a, A14 (her blok) | `VIDEO_YARI_OTOMATIK.bat`'ı açar, Memmet hazırladıkça GÖNDER'e basar | "Blok 7/21 hazır (20 plan). VIDEO_YARI_OTOMATIK.bat'ı aç; Memmet her planı hazırlayınca GÖNDER'e bas." | Telegram |
| A14a sonu | (isteğe bağlı) dikey kesiti izler | "Filmin ilk 3 dakikası yayın kalitesinde hazır: <yol>. Kalan videolar bundan sonra çekilecek." | Telegram (dosya) + masaüstü |
| A16 sonu | CapCut'ı kapatıp açar; isterse izler ve not bırakır | "Taslak hazır: CapCut'ı kapatıp aç; 'YZ <FILM> v3' en üstte. İstersen izleyip not bırak, istersen doğrudan dışa aktar." | sohbet + Telegram |
| A16n | not bırakır ya da CapCut'ta düzenler (isteğe bağlı) | "Notlarını aldım: 6 not → 5 düzeltme, 1 bilgi. Düzeltilmiş taslak: '<senin taslağın> · v4'. Kendi taslağına dokunmadım." | sohbet |
| A17 | CapCut'tan 4K 24 fps dışa aktarır, dosyayı `YAYIN/`'a koyar | "Yayın taslağı hazır (NOTLAR'sız). Dışa aktarıp YAYIN klasörüne koy; gerisini ben denetlerim." Sonra: "Kapak, YouTube metinleri, fragman ve 3 Short YAYIN/'da." | sohbet + Telegram |
| A17y | (isteğe bağlı) `YUKLE.bat` | yalnız o film için onay; yükleme kaydı | — |
| A18a | — | "Yayından 48 saat sonra: tıklama oranı %X, ilk 30 sn tutma %Y. Kapak değişikliği önerisi: …" (yalnız bağlantı varsa) | Telegram |

### 8.4 Kısıt durumlarında
| Durum | Sistem | Kullanıcı | Kanal |
|---|---|---|---|
| Flow "olağan dışı etkinlik" | ≤ 10 sn'de durur; bekleyenleri gönderim yapmadan toplar; `FLOW_KILIDI.json`; kod 7; aynı hafta ikinci uyarıda 7 gün kilit | bekler; en erken 30 dk sonra Flow'da **elle** 1 video dener; başarılıysa `UYARI_GECTI.bat` (yalnız o gün geçerli; o günün kalanında tempo ×1,5 yavaş, ertesi gün ilk blok elle) | **ACİL** Telegram + sohbet |
| reCAPTCHA / doğrulama | durur; kod 2 | doğrulamayı çözer; `VIDEO_*.bat`'ı yeniden açar | ACİL |
| Kredi bitti / bütçe yetmiyor | 5 BÜTÇE; "X kredi gerekiyor"; kalite düşürülmez | isterse kredi yükler; sistem algılayınca kendisi sürer | ACİL |
| Claude kullanım sınırı / görev tavanı | 8 BEKLE + `TOKEN_PROJEKSIYON.md` | sınır açılınca `DEVAM.bat` ya da sohbette "devam" | BİLGİ |
| Disk dolu | 8 BEKLE | `ARSIVLE.bat` (bitmiş partileri D'ye taşır) | BİLGİ |
| Kapı merdiveni tükendi | kâğıt ürün + "yüzüne vur" raporu; videoya geçilmez | — (isterse yeni konu söyler; kesin istek olarak işlenir) | ACİL |
| Flow arayüzü değişti | `memmet-bakimci` aday yaması + korkuluk testi; onarımdan sonra ilk blok elle | — | BİLGİ |

**Bildirim kuralları** ([UM2] `bildirim.py`): olaylar `kisit_olagandisi` (ACİL), `dogrulama` (ACİL), `butce` (ACİL), `kapi_tukendi` (ACİL),
`kullanici_isi` (BİLGİ, 6 saat sonra 1 hatırlatma), `blok_hazir`, `bilgi_paketi`, `asama_bitti`, `oturum_ozeti`, `sinir_doldu`, `disk`, `hata`;
aynı olay 30 dk içinde tekrar edilmez, saatte ≤ 12 mesaj; mesajda gizli bilgi, anahtar, hesap e-postası yoktur; Telegram kapalıysa masaüstü bildirimi ve
`FILM_KAYIT.txt`. Telegram'dan gelen komutlar (`/durum`, `/dur`) P2'dir.

### 8.5 Kullanıcının hiç yapmadığı (ekibin kararları)
Senaryo onayı · karakter ve mekân görünüşü onayı · ses kadrosu seçimi · müzik seçimi · plan, animatik ya da kurgu onayı · kapak ve başlık seçimi ·
yeniden çekim kararı · süre kararı · sağlayıcı seçimi. Hepsi `KARAR_DEFTERI.md`'de gerekçesiyle durur; kullanıcı `film-durum` ile sorabilir, `film-not` ile
itiraz edebilir (itiraz kesin istek olur). `--onayli` kipi (CLAUDE.md "isterse onay noktaları") varsayılan kapalıdır ve yalnız kullanıcı kendisi
`IZINLER.bat` ile açarsa vardır; o kipte animatik, dikey kesit ve kurgu taslağında hat kod 2 ile durur ve kullanıcı "devam" ya da not verene kadar
bekler. Bu durumda da soru sorulmaz: dosya hazır tutulur ve "istersen izle; devam demen yeter" bilgisi verilir. Varsayılan `tam_otomatik` kipte hat
hiçbir noktada beklemez.

## 9. Uygulama sırası

Her adım küçük bir PR'dır (CLAUDE.md: küçük, anlamlı commit'ler); kabul şartı otomatik testtir; "yer" yazıldığı yerde yazılır ve sınanır. Bir adım
bitmeden ona bağlı adım birleştirilmez. Ö0 sonucu (adım 9) P1 adımlarının sırasını değiştirebilir; değişiklik karar defterine yazılır.

| # | Adım | İçerik | Kabul şartı (test) | Bağlı olduğu | Yer |
|---|---|---|---|---|---|
| 0 | **PR-0 güvenlik acil yaması** | `memmet.py`: `OLAGANDISI_KELIMELERI` → `Durdur(kod="olagandisi")` + `FLOW_KILIDI.json`; "olağan/unusual" `HATA_KELIMELERI`'nden çıkar; `kontrol_noktasi()` olağan dışı metinde beklemez; varsayılan 720p; docstring. `film.py`: `Kisitlandi(olagandisi\|dogrulama)` sonrası sağlayıcı geçişi yok. Eski `.bat`'lar (`MEMMET_BASLAT`, `MEMMET_SADECE_*`, `CAPCUT_PROJESI_OLUSTUR`, `FILM_HATTI`) `_ESKI/`'ye; `yeni_film.py` bunları üretmez | `test_memmet_korkuluk` T10: olağan dışı HTML fikstüründe yeni gönderim 0, ≤ 10 sn'de çıkış 7; `test_film.py` (iki beklenti §6.10'daki gibi güncellenir; v1 davranışı korunur) | — | bulut (yazım + test) |
| 1 | **PR-1 hızlı düzeltmeler ve temel veri** | `puan_oku.py` medyan; `izleme_paketi.py` konuşan adı yerine ekranda kurulmuş tarif; `ai84.py` tembel anahtar; `ortak.py`; `esikler.py` + RE'ye `kaynak`/`etiket` geçişi; `veri/ADLAR.json` + `test_adlar.py`; `veri/LISANSLAR.json`; `veri/kok_neden.json`; §2.5 belge düzeltmeleri; kök `CLAUDE.md` yeniden ve `YZ_FILM/ARACLAR/CLAUDE.md` | {6, 8, 9} → 8; anahtarsız `import ai84` süreci öldürmez; RE'de kaynaksız anahtar 0; `test_adlar` yeşil | 0 | bulut |
| 2 | **Ö0-a Claude Code ölçümü** | kullanıcının bilgisayarındaki geliştirme oturumunda `olcum0/kanca_deneme/` ile §10.3'teki 15 davranış (beceri adım 6'da gelir; sonraki sürümlerde aynı ölçüm `/film-gelistir olcum0-a` ile tekrarlanır); memmet3'ün depoya aktarımı ve PR-0 yamasının ona uygulanması | `O0a.json` her davranışı "çalışıyor / çalışmıyor + yedek" ile kapatır; memmet3 T10'dan geçer | 0 | **yerel** (kullanıcının bilgisayarında geliştirme oturumu) |
| 3 | **PR-2 görev defteri çekirdeği** | `film.py` v2 komutları, `GOREV.json`, `FILM_DURUM` v2, `hat/asamalar.py`, `kapi.py`, `kuyruk.py` (şema + 0 kredi kuralı + soy sayacı), `kredi.py` + `olcek.py`, `flow_yuk.py`, `ders_defteri.kaydet`, disk ve token kapıları, `.claude/bin/film.py` | `test_gorev_defteri` (30 kesme senaryosu), `test_kuyruk`, `test_olcek`, `test_flow_yuk` | 1 | bulut |
| 4 | **PR-2b kurulum K1 ve ilk .bat'lar** | `kurulum.py` K1 (soru yok; `YOLLAR.json`, güvenli `FILM_AYAR.json`, `settings.local.json`, `python_yolu.txt`, sürüm, disk, git, anahtar dosyası boşluk denetimi); `bat_yenile.py`; `FILM_SETI.bat`, `KURULUM.bat`, `GUNCELLE.bat`, `FLOW_GIRIS.bat`, `IZINLER.bat`, `UYARI_GECTI.bat`, `DURDUR.bat` | kurulum kuru çalıştırması ve Windows CI'da `.bat` üretimi (ASCII + CRLF) | 3 | bulut + yerel doğrulama |
| 5 | **PR-3 Claude Code katmanı** | `settings.json`, `kanca.py` + `kanca.sh`, `erisim.json`, `kor_paket.py` (kâğıt kipleri), `dilim.py`, aşamalı okuma mekanizması (Ö0-a'nın seçtiği) | `test_kancalar` (+ 50 mesajlık soru seti), `test_kor_paket` (sızıntı 0), nabız testi | 2, 3 | bulut + yerel doğrulama |
| 6 | **PR-4 ajanlar ve beceriler** | 21 ajan dosyası, 4 `SKILL.md`, `sablonlar/`, `semalar/`, `reference/`, `KURTARMA.md`, `GOREV_SEMASI.md`, `KULLANICI_DILI.md`, `PLAN_DILI.md`, `beceri_denetim.py`; `istem-muhendisi.md` ve `muzik-supervizoru.md` depodan kaldırılır | `beceri_denetim` yeşil; §4.8 senaryoları 1–7 sahte ortamda | 5 | bulut |
| 7 | **PR-5 hikâye odası** | `hikaye_odasi.py`, `bulgu_yonlendir.py`, `puan_oku.py` v2 tam, `istem_denetim.py` v2 (replik), `evren.py` (`--on-kayit`, `ne_yok_kelimeleri`, `ozet`), `hikaye_esikleri.json`, `kaset` sağlayıcısı | `test_hikaye`; A00–A06 `kaset` ile uçtan uca | 6 | bulut |
| 8 | **PR-6 yönetmen kâğıdı** | sözlükler (plan, fiil + `beklenen_hiz`, ifade, efekt), `plan_sema`, `kroki`, `plan_denetim`, `plan_dili`, `istem_derle --hareket`, `plan_birlestir`, `dunya_defteri` (K0 + duygu), `zaman_cizelgesi` T0 (Z1/Z2), `kamera_agaci`, `cekim_listesi`; `FILMLER/ORNEK_3_SAHNE_ZANAAT/` (+ bozuk varyantlar) | `test_plan_dili`, `test_sureklilik`; A07 `kaset` ile | 7 | bulut |
| 9 | **Ö0-b…h yerel ölçümler** | `olcum0/` betikleri + `film.py olcum0`: Flow kapasitesi (3 ayrı gün), istem biçimi ve canlı bekleme A/B, son kare referansı A/B, ses dönüştürme kıyası, MuseTalk ve ACE-Step kurulumu/süresi, büyütücü süresi, CapCut klon/şifre, Gemini paketi ve kotası, token + seyirci gürültüsü + karar 6 testi, kanal teşhisi, B3 etiketleri | `OLCUM0.json` her denemede ölçüm + karar + gerekçe; P1 sırası yeniden yazıldı | 0, 3, 4 | **yerel**; 5–8 ile paralel |
| 10 | **PR-7 ses kâğıdı ve kâğıt sonu** | `ses_plani.py`, `muzik.py --kagit/--midi`, `istem_denetim` ses ekleri, `ses_esikleri.json`, `test_ses` (kâğıt kısmı); `FILMLER/ORNEK_3_SAHNE_TAM/` + kaset | A08–A09 ve `KAGIT_TAMAM.json` `kaset` ile; `test_uctan_uca_tam` kâğıt sonuna kadar | 8 | bulut |
| 11 | **İlk filmin kâğıt aşaması** | gerçek ajanlarla A00–A09 (konu kullanıcıdan); Ö0-b yoksa 1800 sn | kâğıt kapıları; Ö0-f'nin token ölçümüyle karşılaştırma | 10 (ve 9 paralel) | yerel |
| 12 | **PR-8 görsel hattı** | `gemini_paket.py`/`gemini_al.py`, `olcum/` gerçek arka uçlar, `kor.py`, `kare_denetim`, `kart_denetim`, `duzeltme`, `evren --kilitle`, `istem_derle --gorsel/--kart/--kapak`, `kapak.py`, `gemini_api` sağlayıcısı (anahtar varsa) | `test_g1_karar`, `test_kart`, `test_evren`; B3 44 kare etiketinde kaçırma oranı raporu | 9, 11 | bulut (sahte) + yerel |
| 13 | **PR-9 yerel ses hazırlığı** | `ses_sec` (telaffuz, seçim), `ses_kiyas`, `seslendir --animatik`, `muzik --uret` (ACE-Step/kütüphane/MIDI), `ses_katmani` T1, `son_miks`, `olcum/ses` gerçek; K2 kurulumu | `test_ses` (bozuk girdi 18 madde); A10a–c gerçek ortamda | 9, 11 | bulut (sahte) + yerel |
| 14 | **PR-10 animatik** | `zaman_cizelgesi` T1, `kurgu_render --animatik`, `kor_paket` izleme kipleri, `seyirci_topla` izleme ekleri ve personalar, `kurgu_uygula`, `kurgu_denetim --kesme-simule`, kurgucu/kesici şablonları, izle-dinle paketi, `bildirim.py`, `izleyici`/`dinleyici` sağlayıcıları | `test_kurgu` (animatik senaryoları), render = T1 ±1 kare; `animatik: ONAYLI` imzası olmadan video görevi açılmaz | 12, 13 | bulut (sahte) + yerel |
| 15 | **PR-11 video hattı** | `memmet.py` v2 (memmet3 tabanlı), `blok_plani`, `memmet_topla`, `yerel_is`, `kalite_denetim --klip`, `video_denetim`, `kare_zinciri --cikar`, `ses_donustur --hizala` (SC1), `pilot_sec` (dikey kesit) | `test_v1`, `test_zincir`, `test_memmet_korkuluk` tam; sahte Flow sayfasında blok akışı | 9, 14 | bulut (sahte) + yerel |
| 16 | **PR-12 video sonrası ses ve kurgu** | `ses_donustur`, `ses_karar`, `diyalog_esitle`, `ses_katmani` T2, `dudak_denetim`, `muzik --yerlestir`, `plan_kurgu`, `kirp_oner`, `kurgu_denetim`, `capcut_film` v2, `taslak_fark`, `capcut_yama` (Ö0-d olumluysa), `notlari_oku` v2, `renk_cila`, `buyut`; K3 kurulumu | `test_kurgu` (16 senaryo), `test_ses` tam | 15 | bulut (sahte) + yerel |
| 17 | **PR-13 yayın ve öğrenme** | `jenerik.py`, `shorts_mp4.py`, `yayin_paketi.py`, `kalite_denetim --final` + yayın doğrulaması, `kanal_teshis.py`, `ders_derle.py`, `evren --film-sonu`, `<veri>/BILGI/YOUTUBE_POLITIKA.md` | `test_uctan_uca_tam` A00–A18 sahte ≤ 5 dk | 16 | bulut (sahte) + yerel |
| 18 | **PR-14 kullanıcı yüzü ve CI** | kalan `.bat`'lar, `BASLA_BURADAN.txt` (sözleşme kartı), `paketle.py` künye, CI (`windows-latest` Py 3.10 + `ubuntu-latest`), bütün takım ≤ 10 dk | CI yeşil | 17 | bulut |
| 19 | **İlk filmin yerel üretimi** | A10–A18; dikey kesit ve PILOT kararları; ilk filmin sonu raporu | §7.4 M1–M15 raporu | 11–18 | yerel |
| 20 | **P2** | `yayin_analiz.py`, `youtube_yukle.py`, `film.py esitle`, `claude_api.py`, `vertex_gorsel`, `veo_vertex`, `ai84_vc`, `elevenlabs_muzik`, MOS tahmincisi, OTIO, Telegram komutları, `arsivle.py` | her biri kendi testiyle | 19 | — |

**Ö0'dan sonra olası yeniden sıralamalar (karar kuralları önceden yazılı):** Ö0-c hiçbir dönüştürücünün eşiği geçmediğini gösterirse MuseTalk (K3)
adım 13'e çekilir ve ana ses yolu B planına geçer (§2.2); Ö0-d CapCut klonunun çalışmadığını gösterirse `capcut_yama` çıkar, `kurgu_render --yayin`
adım 16'da P1 olur ve `yayin_kaynagi: master` yazılır; Ö0-e Gemini API kotasını uygun bulursa `gemini_api` görsel sağlayıcısı adım 12'nin başına
alınır ve paket yükü kalkar; Ö0-b'de bir gün bile 20 videoya uyarısız ulaşılamazsa ilk film 30 dk kalır ve takvim §1.6 formülüyle ölçülen kapasiteden yeniden hesaplanır.

## 10. Açık riskler ve bilinçli olarak dışarıda bırakılanlar

### 10.1 Açık riskler
| # | Risk | Etki | Önlem (bu tasarımda) | Kalan |
|---|---|---|---|---|
| R1 | Flow hesabının kapasitesi düşük ya da hesap uzun süre işaretli kalır (B3'te video tarafı ilk gönderimlerde işaretlendi; ≈ 137 klip kaldı) | takvim haftalarca uzar | Ö0-b ölçümü; ölçülmüş kapasiteyle süre ve takvim; 17.10 temposu; haftalık uyarı kilidi; zincir ardılları ayrı blokta; take ölçüyle | Flow kilitliyse film videoda bekler; resmî API ancak dolar izniyle ve ölçülmüş fiyatla |
| R2 | Claude kullanım sınırı ve token tüketimi (≈ 350–570 görev; en kötü seyirci yükü ≈ 6–7 M token) | hat bekler, ajanlar yarıda kalır | kullanım kaydı, aşama görev tavanı, erken projeksiyon, 8 BEKLE, karar 6 testi, dosya tabanlı devam | abonelik penceresi takvimi belirleyebilir |
| R3 | Omni saniyeli adımlara uymaz | V3 düşer, yeniden çekim artar | Ö0-b `aralik`/`sira` A/B; adım 2'ye inme ve `bitis_sabit` payı; dikey kesitte yeniden ölçüm | ölçüm kötü çıkarsa atomik zincir korunur ama yeniden çekim payı büyür |
| R4 | 4 GB kartta ses dönüştürme metalik ya da aksanı taşır | "ses değişti", "robot ses" | Ö0-c kıyası, metin kapısı, ses merdiveni, B planı (`tts_dudak`), aksanlı `veo_ses_tarifi` | `dinleyici` yoksa aksan ve doğallık "ölçülemedi" |
| R5 | Claude Code davranışları belgede yazıldığı gibi işlemez ya da sürümle değişir | habersizlik ya da "uyarıda dur" güvencesi sessizce kalkar | Ö0-a 15 madde; nabız; kapalı başarısız kancalar; sürüm değişince test; yedek mekanizmalar | doğrulanamayan davranışın yerine betik kapısı |
| R6 | Seyirci puanları kalibre değil; Claude Claude'u puanlıyor | ya hiç geçmez ya da şişer | kapı 7 + olgular / hedef 8; plato kuralı; Ö0-f gürültü ölçümü; personalar; farklı aileden `izleyici`; gerçek tutma verisiyle kalibrasyon | gerçek veri gelene kadar puanın izlenmeyle ilişkisi bilinmiyor |
| R7 | Kare paketi izlemek değildir (hareket, ses, oyunculuk görünmez) | "doğru ama ruhsuz" film | dikey kesit; `izleyici`; hareket hızı ve enerji eğrisi; oyunculuk katmanı; kör ifade okuması | `izleyici` yoksa hareket ve ses kalitesi yalnız betik ölçüsüyle |
| R8 | MuseTalk ağız bölgesini 256 px'te üretir; yüz değişebilir | yakın planda bulanıklık | merdivenin geç basamağı; V2 ve S3 zorunlu | B planına düşülürse yük artar |
| R9 | ACE-Step orkestra kalitesi zayıf; YZ müziğine Content ID talebi | ucuz ses, yayın sorunu | kalite kapısı, kütüphane basamağı, özgün motif, kaynak kaydı | kalite kapısı `dinleyici`'ye bağlı |
| R10 | ElevenLabs/AI84 koşulları belirsiz; AI84 kriptoyla alınmış bir aracı | seri sesi hukuken kırılgan | eğitimsiz OpenVoice önce, RVC yalnız koşullar okununca, referans kayıt, `LISANSLAR.json` notu | kullanıcının mevcut hizmet kararıdır; risk raporda yazılı |
| R11 | CapCut taslakları şifreler ya da `pycapcut` klonu desteklemez | not ve yama yolu çalışmaz | Ö0-d; `yayin_kaynagi: master`; "yeni adla kur" yolu | kullanıcı CapCut'ta düzenlediyse kararları elle taşınamayabilir |
| R12 | Windows kurulumu kırılır (cp310 için son torch tekerleği 2.9.1, onnxruntime ≤ 1.23.2; mmcv; çok Python sürümü) | yerel aşamalar başlamaz | K1/K2/K3 kademeleri, ayrı ortamlar, "çalışıyor/çalışmıyor" kartı, eksik kademe yalnız kendi basamağını kapatır | ilk kurulum zaman alır |
| R13 | Kullanıcının fiziksel iş yükü (≈ 400–527 GÖNDER, ≈ 12–24 paket) | yorgunluk, güven kaybı | sözleşme kartı; Gemini API (Ö0-e); işler toplanır, bitiş kendiliğinden algılanır | `elle` modda GÖNDER sayısı yüksek kalır |
| R14 | Yaratığın deseni ve boyu oynar | kancanın kendisi zayıflar | kimlik kartı (≥ 3 işaret), DINOv2 bankası, kör sorular, davranış sözlüğü | ilk filmlerde çoğunlukla BAYRAK |
| R15 | 720p'den büyütme yavaş ya da yüzü değiştirir | yumuşak görüntü, "4K" vaadi | Ö0-c süresi; SFace denetimi; Lanczos + gren yolu; "4K" yalnız kapı geçerse | — |
| R16 | B1'in düşük izlenmesinin nedeni bilinmiyor | yatırımın yönü belirsiz | Ö0-g teşhisi; yayın sonrası analiz | kullanıcı veri bağlamazsa "ölçülemedi" |
| R17 | Disk dolar (her plana 2 aday, ≈ 1.200 görsel, önbellekler) | hat durur | disk kapısı, arşiv taşıma, önbellek boyutu raporu | temizlik kullanıcının işi (Claude silemez) |
| R18 | YouTube politikaları değişir (sentetik içerik beyanı, özgün olmayan içerik) | kanal riski | `yz_beyani`, politika kontrol listesi, 90 günlük tazeleme | politika yorumu insan kararı gerektirebilir |
| R19 | Ana Claude Bash'te Python ile kancayı atlatır | makine sahipli dosya elle değişir | izin listesi yalnız `film.py`; komut kapısı sezgisel tarama; makine sahipli dosyaların sha1'i | sezgisel tarama kaçırabilir |
| R20 | Tek seyirci örneği tam filmi (≈ 0,2 M token) okuyamaz ya da bağlamı sıkışır | izleme turu bozulur | Ö0-a #15; sıkışırsa görev geçersiz, parça sayısı ayarlanır | — |
| R21 | Ders defteri yalnız sıkılaşır (mandal) | zamanla DUR olasılığı artar | iki yönlü kalibrasyon; yanlış alarm ≤ %30 şartı | güvenlik eşikleri bilerek mandallı |
| R22 | Zincir dalgaları ve görsel/video gün ayrımı takvimi uzatır | süre | uygunluk kuyruğu; derinlik ≤ 2; örtü planları | — |
| R23 | Telif ya da tanınır eser benzerliği (müzik, görsel, hikâye) | yayın riski | özgün motif; istemde sanatçı/film adı yok; kaynak kaydı; jüri özgünlük ölçütü | Content ID yanlış talebi olabilir |

### 10.2 Açık sorular (cevabı bilinmiyor; hangi ölçüm cevaplar)
| Soru | Cevaplayan |
|---|---|
| Flow'un uyarısız günlük kapasitesi; uyarıdan sonra hesabın açılma süresi; 720p üretim süresi; 10 sn klip fiyatı; politika reddi kredi yakıyor mu | Ö0-b |
| Omni'nin `aralik`/`sira` istem biçimine ve "holds the pose, breathing"e uyumu; son kare zinciri karesinin kalite kaybı | Ö0-b, dikey kesit |
| Flow'da (Omni 1.1 Flash) ses referansı ya da sabit ses özelliği var mı | Ö0-b sırasında arayüzde bakılır |
| Veo'nun metin sapma ve konuşmama oranı | Ö0-c (arşiv), SB3, dikey kesit |
| AI84'ün ElevenLabs parametrelerini (seed, önceki/sonraki metin, telaffuz sözlüğü, Voice Design, müzik) iletip iletmediği | Ö0-c küçük denemeler |
| Gemini API görsel kotası ve fiyatı; plan başına 3 aday | Ö0-e |
| Vertex Veo fiyatı ve kotası (kullanıcının Google Cloud hesabı varsa) | Ö0-b ek denemesi |
| YouTube Analytics API'nin tutma, gösterim ve tıklama oranı verisi; kanalda kapak testi açık mı | Ö0-g |
| `pycapcut` lisansı ve yetenekleri; taslak şifrelemesi | Ö0-d |
| ACE-Step, büyütücü ve MOS modellerinin ağırlık lisansları; FluidSynth ve örnek kütüphanesi lisansları | kurulum (`LISANSLAR.json`) |
| Kör gözlem görev boyu (12 ↔ 20 görsel), MediaPipe yaw işareti | Ö0-h + GS0 kalibrasyonu |
| Plan seyircisi, ön turlar (KR3a/KR8a), take ve kısmi izlemenin değeri | ilk iki film (D-44, D-23, D-18) |
| Claude paneli ve `izleyici` puanlarının gerçek tutma eğrisiyle ilişkisi | ilk üç film (D-19, D-24) |

### 10.3 Ö0-a'da doğrulanacak Claude Code davranışları (15)
1. `CLAUDE_CODE_FORK_SUBAGENT=0` ile tek mesajdaki 3–5 Agent çağrısının paralel koşması ve ana Claude'un sonucu beklemesi.
2. Arka planda biten alt ajanın tamamlanma bildiriminin, ana tur bitmişken oturumu kendiliğinden uyandırması.
3. SubagentStop `decision: "block"` ile aşamalı devam (ön planda ve arka planda); `maxTurns`'e ulaşan ajanda SubagentStop'un tetiklenmesi ve kısmi çıktının
   `SendMessage` ile sürdürülmesi.
4. PreToolUse `Agent` girdisinde `subagent_type`'ın (fork dahil) ve `name`/`isolation` parametrelerinin görünmesi.
5. `onFailure: "block"` ve `timeout` alanlarının komut kancasında beklendiği gibi çalışması (kasıtlı yavaş kanca testi).
6. Ayar `env`'inin kanca süreçlerine geçmesi (nabız `ayar_sha` yedeği hazır).
7. `settings.local.json → additionalDirectories` ile veri köküne `acceptEdits` alt ajanın soru sormadan yazabilmesi.
8. Windows'ta Git Bash ile `bash "$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh" …` komutunun, PowerShell aracı eşleyicisinin ve mutlak Python yolunun
   çalışması; kanca süresinin ≤ 2 sn olması.
9. Becerideki `hooks` alanı ile ayar kancası aynı komutu taşıyınca iki kez koşup koşmadığı.
10. Becerideki `!` komutunun Windows'ta Python'u bulması (`|| true` yedeği; `py -3.10` sarmalayıcıda).
11. `claude --continue "devam"`'ın son oturumu sürdürüp ilk mesajı göndermesi (`DEVAM.bat`).
12. Ajan frontmatter alanlarının (`effort`, `omitClaudeMd`, `permissionMode`, `maxTurns`) ve beceri alanlarının (`disallowed-tools`, `allowed-tools`,
    `disable-model-invocation`, `hooks`) tanınması; tanınmayan alanın sessizce yok sayılıp sayılmadığı.
13. SubagentStop kanca girdisinde alt ajanın döküm dosyası yolunun gelmesi ve kullanım (token) satırlarının okunabilmesi (D-08).
14. Stop kancasının `decision: block` ile ana Claude'u sürmeye zorlaması ve ardışık sınırın araç çağrısında sıfırlanması (soru kapısı ve devam kapısı).
15. Bir alt ajanın ≈ 0,2 M tokenlik izleme paketini tek oturumda okuyabilmesi; otomatik sıkıştırmanın tetiklenip tetiklenmediği.

### 10.4 Bilinçli olarak dışarıda bırakılanlar
| Dışarıda bırakılan | Neden |
|---|---|
| Bot tespitini atlatan her şey: fare/klavye taklidi, reCAPTCHA çözümü, uyarıdan sonra otomatik yeniden başlatma ya da sayfa yenileme, tempo hızlandırma, ikinci/ortak/aile hesabı, kie.ai | KK5; D-02, D-03; BK §6.4 "gri havuz" |
| Memmet'in "gündüz otomatik" kipi | gündüz kipinde 15–20 dk'da bir uyarı geldi (BK §6.2 #7); `elle` varsayılan, gece yalnız izinle |
| "İnsan temposu" çerçevesi | tempo insan taklidi değil yük sınırıdır ([UM2] §4.8.5); metinler buna göre düzeltilir |
| Wav2Lip, `fal_latentsync`, Seed-VC, MusicGen, YuE2, Stable Audio Open | kalite ya da lisans (CC-BY-NC, InsightFace riski, belirsiz ağırlık lisansı, şirket lisansı) |
| Gemini'de elle müzik; Lyria/Gemini ile ambiyans | KK1 (elle iş) ve lisans; BK §5.1.2 (ambiyansta mırıltı dersi) |
| Bütün filmin `ai84_vc` ile dönüştürülmesi | maliyet bakiyenin 2,6–3,2 katı (tahmin); yalnız kritik replik |
| RVC eğitimi | ElevenLabs/AI84 koşulları okunana kadar |
| Bulutta film üretimi; `film.py esitle` | kancalar bulutta uygulanmayabilir; kullanıcıya git yükü (D-12); `esitle` P2 |
| Otomatik YouTube yüklemesi (varsayılan) | CLAUDE.md "isteğe bağlı ve onaylı"; varsayılan kapalı, P2 |
| Ayrı `kurgu-seyircisi` ajanı, `ONCEKI_OZET`, "previously" özeti; seyirciye kopukluk adayı, `ekranda_bilgi` ya da önceki filmin özeti verilmesi | habersizlik ([KU2] İ-1, [SN2] İ2) |
| Plan başına 3 aday (varsayılan) | kanıt yok; Ö0-e ve karar 6 testi açarsa açılır (D-16) |
| Gemini "ikinci göz"ün kullanıcı paketiyle yapılması | kullanıcı iş yükü ([SA] K-2); yalnız API ile (D-19) |
| Karakter görünüşü, ses, animatik ve kurgu için kullanıcı onay noktaları | KK1; yalnız kullanıcının kendisi açtığı `--onayli` kipinde bekleme |
| Teknik son kare (`-sseof`) ile zincir | seyircinin gördüğü kesme karesi değildir (D-15) |
| Yeşil fon kart karşılaştırması | yapılmadı; açık gri birleşik kart sayfası seçildi ([GS2] GS3); ilk filmin kart kapısı sonuçları kötüyse ders adayı olur |
| İkinci dil ses izi ([ESY] EÇ7) | ilk iki filmden sonra; YouTube çok dilli ses koşulları doğrulanınca |
| Telegram'dan komut almak (`/durum`, `/dur`) | güvenlik ve kapsam; P2 |
| Ayrı `yayin-stratejisti` ajan adı | rol `yayin-paketcisi`'nde ([CM2] Ç-10; ad karışıklığı) |
| Sabit "kullanıcı el işi ≤ N saat" tavanı | N'nin kaynağı yok; el işi ölçülür ve baştan gösterilir (D-06) |
| Otomatik güncellemenin kapatılması | güvenlik düzeltmeleri gelsin; sürüm değişince kancalar test edilir (D-11) |
