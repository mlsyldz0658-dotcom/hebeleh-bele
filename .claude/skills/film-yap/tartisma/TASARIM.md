# TASARIM — YZ Film Seti: konudan yayına tek tasarım

> **Durum:** tamamlandı; uygulanacak karar belgesi; `SON_DENETIM.md` bulguları işlendi (aşağıdaki tablo). **Tarih:** 23.10.2026.
> **Hazırlayan:** sentez yazarı ve baş tasarımcı (Claude Opus 5.5).
> **Kaynaklar:** `tartisma/tur1_*.md` (7), `tur2_*.md` (7), `elestiri_seyirci_yapimci.md`, `elestiri_seytanin_avukati.md`, `SON_DENETIM.md`; eğitim belgeleri
> (`BILGI_KURALLARI.md`, `ZANAAT.md`, `ritim_esikleri.json`, `arastirma/01–03`, `FILMLE ILGILI CLAUDE/00–07`, `YZ_FILM/BILGI/*`) ve mevcut kod.
> **Bu belge tur 3'ün yerine geçer ve karardır.** Uzman belgeleriyle çeliştiği her yerde bu belge geçerlidir; uzman belgelerine yalnız ayrıntı
> (tablo, örnek) için başvurulur ve bu belgede "aynen alınır" denen yerler oradan alınır.
>
> **Kısaltmalar:** [CM2] Claude Code mimarisi · [UM2] üretim mühendisi · [SN2] senarist · [YN2] yönetmen · [GS2] görüntü-süreklilik ·
> [SM2] ses-müzik · [KU2] kurgucu (hepsi tur 2) · [ESY] seyirci-yapımcı eleştirisi (EK = KRİTİK, EO = ORTA) · [SA] şeytanın avukatı
> (K = KRİTİK, O = ORTA, S = KÜÇÜK) · [SON] son denetim (`SON_DENETIM.md`; aynı harf düzeni) · ZN `ZANAAT.md` · RE `ritim_esikleri.json` ·
> BK `BILGI_KURALLARI.md` · DR `03_DERSLER.md` · AR1–AR3 `arastirma/01–03`.
>
> **Sayı etiketleri:** kaynağı olan sayının yanında kaynağı yazar · **(tahmin)** kaynağı yok, ilk filmde ölçülüp ders defteriyle ayarlanır ·
> **(hesap)** kaynaktaki sayılardan türetildi · **(doğrulanacak)** Claude Code ya da dış servis davranışı, Ö0 ölçüm turunda bir kez sınanır.
>
> **Yer adları:** `<depo>` = depo kökü (Windows'ta `C:\Users\Soysal\Desktop\YZ_FILM_SET`), `<veri>` = veri kökü (Windows'ta
> `C:\Users\Soysal\Desktop\YZ_FILM`, yeri değişmez), `<film>` = `<veri>/FILMLER/<FILM_ADI>/`, `<evren>` = `<veri>/EVREN/<SERI>/`.
> Araçlar `<depo>/YZ_FILM/ARACLAR/` altındadır. Bütün yollar kodda yalnız `ortak.yollar()` ile `YOLLAR.json`'dan okunur; hiçbir araç AYARLAR,
> FILMLER, EVREN ya da SES_KUTUPHANESI'ni kendi dosya konumuna göre aramaz; `YOLLAR.json` yoksa açık hata verir (sessiz varsayılan yok; §5.6).

## Son denetim düzeltmeleri (`SON_DENETIM.md`, 23.10.2026)
Bağımsız son denetimin 30 bulgusu (KRİTİK 4 · ORTA 15 · KÜÇÜK 11) bu belgeye işlendi: 29'u tam, 1'i (S-4) kısmen. Hiçbir düzeltme bir güvenlik
kuralını gevşetmez. Bulgu satır numaraları denetimin okuduğu eski sürüme aittir; aşağıda yeni bölüm adresleri verilir.

| Bulgu | Sv. | Ne yaptım (nerede) | Durum |
|---|---|---|---|
| K-1 memmet3'ün `elle` kipi uyarıda durmuyor; PR-0 dar | K | PR-0'ın kapsamı D-02 a–g oldu ve depodaki Memmet ile memmet3'e aynen uygulanır: her kipte uyarıda dur (sayfada işlem yok, "GÖNDER'e basma, sayfayı yenileme"), `elle` kipindeki "sayfayı yenile, devam" yolu ve gece kipindeki 5 yenileme silinir, kodda 17.10 tempo (ayardaki hızlı değer geçmez), `FLOW_TEMPO.json` molası, `flow.py` çıkış kodu → `Kisitlandi(kod)` ve bilinmeyen kodda geçiş yok, reCAPTCHA'da dur, `_surum` reddi. T10 her kipte (elle, gece, doğrulama); Ö0-b memmet3 birleşmeden başlamaz (D-02, §1.2 Ö0-b, §4.5, §6.1, §6.10, §9 adım 0, 2, 9; SKILL kuralı 3; §4.8 #13) | uygulandı |
| K-2 Masaüstündeki eski Memmet ve `.bat`'lar canlı | K | Veri kökü emniyeti (`kurulum.py --veri-emniyet`, PR-0; ilk yerel oturumun ilk işi): `<veri>`'deki eski Memmet, `film.py`, Memmet'i çağıran `.bat/.cmd/.ps1` (B3 `gece_video.ps1` dahil), veri kökü `BASLA_BURADAN`, `KURULUM.bat`, film adı soran `YENI_FILM.bat` `_ESKI/`'ye taşınır (silinmez), yerlerine emeklilik `.bat`'ı ve depoya giden sarmalayıcı; veri kökü `CLAUDE.md`'si; OpenMontage'a dokunulmaz; `test_veri_emniyet` (D-02, §6.1, §6.9, §8.2 adım 0b, §9 adım 0, 2; R25) | uygulandı |
| K-3 Ses ve müzik yayından önce dinlenmiyor; motor doğallıksız seçiliyor | K | Ücretsiz Gemini anahtarı kurulumun fiziksel işi (§8.2 adım 3b, kart §8.1); kural: anahtar varsa ve maliyet 0 ise `izleyici`/`dinleyici` açık, `izinler.gemini_api_ucretli` yalnız ücretli kullanımı yönetir; ücretsiz katmanın veri koşulu `LISANSLAR.json` + bilgi; Ö0-c'ye doğallık ölçüsü (MOS P2'den çekildi ya da `dinleyici` kör ikili; fısıltı/bağırma zorunlu), yoksa "ölçülemedi" BAYRAK + izle-dinle örneği; müzik kapısı `dinleyici` yoksa ÖLÇÜLEMEDİ ve açık eksik (D-06, D-19, D-25, §1.2 Ö0-c/e, §2.2, §2.3, §5.6, §6.6; `test_izinler`) | uygulandı |
| K-4 Seyirci dışı kapılarda tavan sonrası yol yok; kural 8 ↔ küresel bütçe | K | §1.5'e tavan sonrası genel merdiveni (sahibin başka kipi → üst sahip → `durdu` + `kurgucu·sifir_kredi` → feragat edilemeyenler → `hedef_alti` + açık rapor) ve aşama aşama tablo; `hat/asamalar.py`'de `tavan_sonrasi` zorunlu; A05 `hata_donus_max` 3 (tahmin); kural 8 "KRİTİK = 0 ya da kurgu tavanı doldu ve KRİTİK'ler açık eksik raporunda"; 6 KAPI yalnız merdiven tükenince (§1.1, §1.3 A05/A16, §1.4, §1.5, D-07, §6.1, §8.4, §6.10 `test_gorev_defteri`; M16, R26) | uygulandı |
| O-1 Araçlar yolları kendi konumlarına göre arıyor | O | `ortak.yollar()` tek yol kaynağı ve 10 aracın yol göçü PR-1'de; `kurulum.py --yollar`; `YOLLAR.json` yoksa açık hata; `.bat`'lar Python'u ve betiği mutlak yolla çağırır; `test_yollar` (Yer adları, §5.6, §6.1, §6.9, §9 adım 1) | uygulandı |
| O-2 Ö0 ölçümleri sonraki PR'lara bağlı | O | Ö0 üçe bölündü: Ö0-a (adım 2), Ö0-1 b/c/d/e/g kendi içinde yeterli betiklerle (adım 9; bağımlılık 0–4), Ö0-2 f/h/Ö0-b·V3 (adım 12a; 6, 7, 12); §1.2 tablosuna bağımlılık sütunu; Ö0-b istemleri elle yazılmış sürümlü 45 istemlik fikstür, klipler saklanır (§1.2, D-01, §9) | uygulandı |
| O-3 Ö0-b uyarıyı yokluyor, kilit kuralıyla çelişiyor | O | Merdivenli protokol 10/15/20 (tahmin), ilk uyarıda o gün + 7 gün ölçüm yok ve Ö0-b kapanır; alt sınır "uyarıdan önceki en yüksek uyarısız gün"; politika reddi yalnız kendiliğinden gelirse; kasıtlı tetikleme yasak (§10.4); ≤ 540 kr ölçüm harcaması BUT0'da ve kartta; A/B'ler 2×2 çapraz, ön karar, kol başına 12 (tahmin) yoksa varsayılan, A14a doğrular (§1.2, D-04, D-05, D-13, §8.1, §8.2) | uygulandı |
| O-4 Kullanıcı eyleminden sonra "kendiliğinden algılama" süreci yok | O | Döngü adım 5: `film.py bekle --kullanici <id>` / `--blok` arka planda eseri yoklar, 6 saatte hatırlatır, bitişi oturumu uyandırır; Ö0-a #16; tutmazsa kartta "tamam" yazma işi ve sayısı (§4.2, D-39, §4.4, §8.1, §8.3, §8.4, §10.3 #16) | uygulandı |
| O-5 Yerel geliştirme oturumu kullanıcı adımlarında yok; `GUNCELLE.bat` çakışması | O | §8.2 adım 0b "ilk kurulum" yazma; kurulum yalnız `git clone` (özel depoda Git Credential Manager), ZIP'te `GUNCELLE.bat` kapalı; memmet3 ve `B3_44.json` yerelde depoya commit'lenmez, `<veri>/GELISTIRME/` + dar `esitle --gelistirme` (P0, PR-1) ile ayrı dala, birleştirme bulutta PR; push yoksa bilgi (denetimin a seçeneği yedek); `GUNCELLE.bat` yerel değişiklikte durur (D-12, §4.5, §6.1, §6.9, §8.2, §9 adım 1, 2, 4) | uygulandı |
| O-6 Seri evreni ve ders defterinin yedeği yok | O | A18'de `evren.py --yedekle` ve `ders_defteri --yedekle` (`robocopy /E`, `/MIR` yasak) → `D:\YZ_FILM_YEDEK\…`; D yoksa bilgi ve sonraki filmin A00'ı; A00'da sha1 doğrulaması; "git'e yalnız JSON" kaldırıldı (D-33, D-42, §1.3 A00/A18, §2.6, §5.4; R24) | uygulandı |
| O-7 Disk kapısının çözümü P2'de | O | `arsivle.py` P1 (adım 16); A16, A17 sonunda ve disk kapısında Claude kendisi başlatır; kullanıcının tek işi "D'yi tak"; bağlı yollar taşınmaz, testli (D-38, §1.3, §6.1, §6.9, §8.4, §9; R17) | uygulandı |
| O-8 SAHNELER v2 ↔ ZN §6.1, Z0 #17, AR2 §6.1 | O | §5.1 kural 8'e eşleme tablosu (hikâye alanları `HIKAYE.json` → `_derlenir.hikaye`, kamera tarafı kodda vb.); örnek plana `_derlenir.hikaye`; §2.5'e ZN başlığı, ZN §6.1, Z0 #5/#14/#17, AR2 §6.1 "tarihsel" notu, RE `eylem_adim_*` yeni adım modeli; `test_adlar` ZN ve AR2'yi de tarar (D-35) | uygulandı |
| O-9 v1↔v2 geriye uyumluluk boşlukları | O | Geriye uyum tek yönlü: v1 araçları `_surum ≥ 2`'de 4 ile çıkar (PR-0); tek ayırt edici `_surum`, v2'de `zanaat` zorunlu; v1→v2 eşleme (`bitis_karesi`, `motor`, `*_yedek` → `istem_derle --yedek`; filtre reddi → yedek bir kez → `yonetmen·onarim`); `plan_birlestir` `ref`/`ses`'i evrenden doldurur (§5.1 kural 1, 2, 7; §6.1, §6.2, §6.4) | uygulandı |
| O-10 Güvenlik sayıları iki dosyada | O | Sayısal güvenlik sınırları yalnız `hat_esikleri.json`'da (`gevsetilemez`); `FILM_AYAR` yalnız izin, tercih ve para tavanı; ayarda sınır bulunursa sıkı olan uygulanır + BAYRAK; `mod` tek alan, `onayli_kip` kalktı (D-04, D-34, §5.6, §7.1, §7.3, §6.1 `esikler.py`) | uygulandı |
| O-11 Kancalar tutmazsa habersizliğin yedeği yok | O | `kanca.py` kendi içinde kapalı başarısız (try/except, deny, ≤ 1 sn); kör roller için başsız `claude -p` yedeği (`<veri>` dışı geçici klasör, `Read,Write`, CLAUDE.md ve bellek yüklenmez; doğrulanacak), o da tutmazsa BAYRAK'lı talimat yalıtımı; Ö0-a'ya dört olay ve `onFailure`'sız hata davranışı; model sapması SubagentStop dökümünden (D-08, D-11, §1.2 Ö0-a, §6.2, §10.3 #5, #17–#19; R5) | uygulandı (yedeklerin davranışı Ö0-a'da doğrulanacak) |
| O-12 A07b paralel planlama ↔ önceki sahnenin son 2 planı | O | Paralel görevde girdi sözleşmedeki `cikis_durumu`; çözülmüş plan bitişi yalnız aynı mekân ve zamandaki ardışık çiftte, o çift sırayla; `dilim.py` ayırır; uyuşmazlık K0 `sahne_uclari.hikaye_esit`, `YENIDEN_YAZ` yalnız iki sahneye (§1.3 A07b/A07c, §3.3 yönetmen, §5.2, §6.2) | uygulandı |
| O-13 Depo bulutta açılınca ne olacağı tanımsız | O | D-45: bulutta konu sorulmaz, film başlatılmaz, tek bilgi cümlesi; `film-yap` bulutta yalnız `sahte` deneme; görev metninden sapma ve yeniden açma koşulu karar olarak yazıldı; §4.8 #12; §10.3 #20 (§1.1, §4.1, §4.7, §10.4) | uygulandı |
| O-14 Yayın müziği tek ölçülmemiş yola dayanıyor | O | Zincir boşsa ipucu müziksiz, S6 BAYRAK, açık eksik; `kutuphane` KUR1'de lisanslı çekirdek setle (kurulum indirmesi); ACE-Step 4 GB süresi Ö0-c'de, olmazsa düşer; Gemini elle müzik yalnız lisans koşuluyla son basamak, "KK1" gerekçesi kaldırıldı; `elle` sağlayıcı yalnız son basamak (D-25, D-37, D-41, §5.6, §6.6, §8.1, §10.4; R9) | uygulandı |
| O-15 Flow kilitliyken Vertex: D-03/R1 ↔ D-41 | O | Otomatik geçiş yok; `FLOW_KILIDI` varken Vertex yalnız `izinler.flow_kilitliyken_vertex` + `usd_tavan_film > 0` ile, `blok_plani` planlar, Flow gönderimi 0, her çağrı BUTK'dan; testli (D-03, D-41, §5.6, §6.1, §8.4; R1) | uygulandı |
| S-1 Kanonik örnek kendi eşiklerini çiğniyor | S | `eylem_adim_mikro_min_sn` 0,8 (tahmin; mikro ve ses vuruşu), Z0 #5'e "L/J taşması görünen süreden düşülür"; örnek artık HATA'sız (a1 1,0 ≥ 0,8; 3,95 − 1,1 ≤ 3,6); `test_plan_dili` kanonik örneği geçirir (§2.5, §6.4, §7.2, §7.3) | uygulandı |
| S-2 Tanımsız dosya ve araçlar | S | `pilot_sec` → `blok_plani --kesit`; `ses_olcum` → `olcum/ses.py --kontrol`; `MERDIVEN.md` → `kuyruk.py --merdiven-md`; `veri/tur_kanca.json`, `veri/aksan_sozlugu.json`; `PROJE_KARARLARI.md` → `KARAR_DEFTERI.md`; `FILM_SONU_RAPORU` → `ders_derle --film-sonu`; izle-dinle → `kurgu_render --bilgi-paketi`; FluidSynth + SF2 → KUR1; veri kökü `CLAUDE.md` → `--veri-emniyet`; `test_adlar` üreticisiz girdiyi HATA sayar (§1.3, §3.3, §6) | uygulandı |
| S-3 Girdiyi üreten çağrılar eksik | S | A07a'ya `kroki.py --ciz`, A07c'ye `cekim_listesi` (P0), A11/A14a/A16'ya `kor_paket --kip kapak/kesit/kurgu`; `asamalar.py`'de her girdinin üreticisi zorunlu (§1.3, §6.1, §6.4) | uygulandı |
| S-4 Ad çakışmaları, aynı işi yapan iki araç | S | Önekler: kurulum kademesi `KUR1–3`, kamera kurulumu `KAM1…`, bütçe `BUT0–2/BUTK` belge boyunca değiştirildi; `BK` yalnız BILGI_KURALLARI; `seyirci-topla` `puan_oku`'ya yönlendi; §3.1'e "yalnız yeni dosya yazar" istisnası (D-35, §3.1, §6.3). **Kısmen:** `S0–S8` ↔ `S12` çakışması yeniden adlandırılmadı, biçim kuralıyla çözüldü (sahne ≥ 2 hane, ses kapısı tek hane; `test_adlar` zorlar); gerekçe: iki ad ailesi uzman belgelerinde ve şemalarda yüzlerce yerde, biçim kuralı aynı güvenceyi daha az kırılmayla verir | kısmen |
| S-5 Zarf kuralı örneklerde uygulanmıyor | S | Tek ad `_surum`; `FILM_DURUM`, `GOREV`, kapı raporu, dünya defteri, `KURALLAR_OGRENILEN` örnekleri düzeltildi; istisnalar listelendi (ajan `CIKTI/`, `.jsonl`, `FILM_AYAR`, ders ham kaydı, `GOREV.json`); kural `plan_sema`/`kapi.py` testlerinde (§5, §5.2, §5.3, §5.5, §5.7, §5.8) | uygulandı |
| S-6 `altyazi_dili: "tr"` ve `baslik`'ın iki anlamı | S | Örnek `null`; `baslik` ekran/seri adı, YouTube başlığı yalnız `YAYIN/PAKET.json`; `capcut_film --yayin` Altyazi kanalı koymaz; CLAUDE_ICIN şema notu (§5.1, §2.5, §6.7, §1.3 A17) | uygulandı |
| S-7 `film-durum` öneri kalıbı KK1 ile gerilimli; "bak" alışkanlığı yok | S | Kalıp bilgi cümlesi oldu ("Ekip şunu yapacak: …; itiraz edersen yaz"); `film.py goster pencere capcut` (salt okunur PrintWindow) (§4.3, §4.4, §6.1) | uygulandı |
| S-8 Etiketsiz sayılar; takvim tutarsızlığı | S | D-23, D-28, §3.1, A11 sayıları etiketlendi; `film_token_tavan` tanımlandı (§1.5, §7.3); belgedeki takvim günleri silindi, takvim yalnız `olcek.py` çıktısı (§1.6, §8.3) | uygulandı |
| S-9 Lisans ayrıntıları | S | `kullanici_araci: true` (`pycapcut`, `kurgu_koprusu`, `demucs`), lisansları P0'da; `LISANSLAR.json` geçişli bağımlılıkları kaydeder; OpenVoice'ta AGPL'li yol kapatılır ya da ayrı ortamda yerel kalır (D-36, §6.6, §6.7) | uygulandı |
| S-10 `YOUTUBE_BAGLA.bat` ağır | S | Varsayılan YouTube Studio CSV dışa aktarımı (adımlar BASLA_BURADAN'da); OAuth P2 (D-24, §1.2 Ö0-g, §6.3, §6.8, §8.1, §8.2, §9) | uygulandı |
| S-11 reCAPTCHA belge ↔ kod tutarsız | S | Tek davranış: PR-0'da reCAPTCHA/doğrulama/oturum düşmesinde Memmet beklemez, bildirir, çıkış 2; kullanıcı çözer ve `VIDEO_*.bat`'ı yeniden açar (D-02 f, §6.1, §8.4) | uygulandı |

**Açık kalanlar** (karar verildi, gerçek davranış ölçülecek): `onFailure` alanı ve `onFailure`'sız kanca davranışı, arka plan işinin oturumu
uyandırması, dört kanca olayının varlığı, başsız `claude -p`'nin abonelikle ve CLAUDE.md/bellek yüklenmeden çalışması, bulutta kancalar (§10.3 #5,
#16–#20); Gemini ücretsiz katmanında video ve ses girişi, kotası ve veri kullanım koşulu (Ö0-e); YouTube OAuth'un Google Cloud projesi isteyip
istemediği (P2); OpenVoice V2'nin geçişli AGPL bağımlılığı, MOS modeli, müzik çekirdek seti ve Gemini müziğinin lisansları (P0 lisans
doğrulaması); memmet3'ün `elle` kipindeki gerçek davranışı (kod depoda yok; aktarımda okunur); ACE-Step'in 4 GB süresi (Ö0-c); bu turda
eklenen tahmin sayıları (Ö0-b 10/15/20, kol başına 12 örnek, `hata_donus_max` 3, mikro adım 0,8 sn, `film_token_tavan` × 1,5, ≈ 110 dk bekleme).

## 0. Kısa özet

Kullanıcıya, sade Türkçe:

1. Sen yalnız filmin konusunu bir cümleyle söylersin. Senaryo, oyuncu sesleri, müzik ve kurgu dahil bütün kararları ekip verir; sana karar sorusu sorulmaz.
2. Önce her şey kâğıtta yapılır ve kredi harcanmaz: hikâye odası senaryoyu yazar, filmi hiç bilmeyen üç "seyirci" okur, puan 8/10'a yaklaşana kadar düzeltilir.
3. Yönetmen her planı saniye saniye, elle ve yönle yazar ("sağ elini kaleme uzatır, başparmak ve işaret parmağıyla kavrar"). Bilgisayar kimin elinde ne olduğunu bir defterde tutar ve zıplamaları yakalar.
4. Karakter kartları ve her planın başlangıç görseli üretilir. Her görsel karakterin kartıyla ölçülür ve beklentiyi bilmeyen bir gözlemciye tarif ettirilir.
5. Videoya geçmeden önce film, durağan karelerle ve gerçek seslerle bir "animatik" olarak seyircilere izletilir; kopukluklar kredisiz düzeltilir.
6. Sonra filmin ilk 3 dakikası yayın kalitesinde bitirilir ve sana bilgi olarak gönderilir. Kalan videolar bundan sonra çekilir.
7. Senin işin yalnız fiziksel işlerdir: Flow'a giriş, kurulumda bir kez ücretsiz Gemini anahtarı almak (filmi yayından önce bir "kulağın" dinlemesi için), bazı görsel paketlerini Gemini'ye taşımak, video oturumlarında GÖNDER'e basmak, CapCut'tan dışa aktarmak. Sayıları baştan "kullanıcı sözleşmesi" kartında yazar.
8. Flow "olağan dışı etkinlik" ya da doğrulama gösterirse sistem hangi kipte olursa olsun hemen durur ve sana haber verir. Asla atlatmaz, hızlandırmaz, sayfayı yenilemez, başka hesaba geçmez. Masaüstündeki eski Memmet ve eski `.bat`'lar ilk gün emekliye ayrılır (silinmez).
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
  `5` BÜTÇE · `6` KAPI (tur tavanı **ve** §1.5'teki tavan sonrası merdiven tükendi; kâğıt ürün ya da feragat edilemez film düzeyi HATA) ·
  `7` KISIT (Flow uyarısı, hesap kilidi) · `8` BEKLE (mola, GPU, kullanım sınırı, bekleme süresi). Tur tavanının dolması tek başına 6 vermez:
  `film.py` merdivenin sonraki basamağını görev olarak açar (§1.5).
- **Nerede:** Üretim **yalnız kullanıcının Windows bilgisayarında** yürür (§2.1 D-12). Bulut oturumları yalnız geliştirme içindir; orada bütün
  aşamalar `sahte` ve `kaset` sağlayıcılarıyla, ağsız ve kredisiz test edilir. Depo bulutta açılır ve kullanıcı konu verirse konu sorulmaz, film
  başlatılmaz; tek bilgi cümlesi verilir (§4.1, D-45). Aşağıdaki tabloda "yerel" sütunu üretim yerini, "bulutta test" sütunu otomatik testin
  bulutta koşup koşmadığını gösterir.
- **İmza:** her aşama çıktısı `_uretim {asama, gorev, girdi_imza, arac_surum, esik_surum, sonuc, zaman, ortam}` zarfını taşır. Aşama "tamam" =
  çıktı var + girdi imzası eşit + kapı GEÇ. Kredili çıktı asla silinmez; girdi değişirse `bayat` işaretlenir ve kuyruğa girer.

### 1.2 Ölçüm turu Ö0 (sistem düzeyi; bir kez, ilk filmden önce başlar)
Ö0, tasarımın ölçülmemiş temellerini ([SA] K-1, K-3, K-4) kod yığılmadan önce ölçer. Üç parçadır ([SON] O-2): **Ö0-a** ilk yerel geliştirme
oturumunda (§9 adım 2); **Ö0-1** (b, c, d, e, g) kendi içinde yeterli `olcum0/` betikleriyle (§9 adım 9); **Ö0-2** (f, h ve Ö0-b kliplerinin V3
değerlendirmesi) ölçtüğü araçlar geldikten sonra (§9 adım 12a). Ö0-1 ve Ö0-2 `film.py olcum0`'ın sistem görevleridir ve ilk filmin kâğıt
aşamalarıyla (A00–A09) **paralel** yürür. Ö0-2 kayıtlı kliplerle çalışır, yeniden çekim istemez. Sonuçlar `<veri>/BILGI/OLCUM0/O0<harf>.json` +
`OLCUM0.json` (her deneme: ölçüm, karar, gerekçe) dosyalarına yazılır; bu belgede "Ö0 ölçer" denen her karar bu dosyadan okunur. Bir Ö0 sonucu
henüz yokken onu kullanan karar varsayılanla verilir ve karar defterine "Ö0 yok → varsayılan" diye yazılır.

| No | Deneme | Kim | Girdi | Çıktı | Geçme şartı (karar kuralı) | Üst sınır | Kredi | Bağlı (§9 adımı) | Yer |
|---|---|---|---|---|---|---|---|---|---|
| Ö0-a | Claude Code davranışları (§10.3'teki 20 madde) | geliştirici Claude, `olcum0/kanca_deneme/` | deneme kancaları | `O0a.json` | Her davranış "çalışıyor / çalışmıyor + seçilen yedek" ile kapanır. Kanca nabzı çalışmıyorsa PR-3 birleştirilmez. Erişim kancası güvenilmezse kör roller başsız `claude -p` yedeğine geçer (D-11, §10.3 #19); o da tutmazsa kör görevler yalnız GIRDI kopyasıyla, talimat düzeyinde yalıtımla koşar, her rapor `habersizlik: dogrulanmadi` BAYRAK'ı taşır ve M12 "ölçülemedi" yazılır | 1 tur | yok | 0, 1 | yerel |
| Ö0-b | Flow/Omni: günlük uyarısız kapasite; `aralik` ve `sira` istem biçimleri; "holds still" ↔ "holds the pose, breathing"; 720p üretim süresi; politika reddi **yalnız kendiliğinden gelirse** kredi yakıp yakmadığı; 1280×720 son kare zinciri karesinin kalitesi; eylem kesmede önceki son karenin **görsel referansı**. **Ön koşul:** memmet3'ün PR-0 sürümü T10-elle, T10-gece ve T10-dogrulama'dan geçmiş ve `FLOW_TEMPO.json` okuyor (adım 2) | `olcum0/flow_deneme.py` + Memmet (`elle`) + kullanıcı (GÖNDER) | B3'ün eski iki tur denetimden geçmiş P1 kareleri (PA: 44 kare) ve geliştirici Claude'un bunlardan elle yazdığı, sürümlü **45 istemlik fikstür** (`olcum0/fikstur/O0b_istemler_v1.json`; filtre taramasından HATA'sız; politika reddini kasıtlı tetikleyen istem yasak, §10.4) | `O0b.json` + kayıtlı klipler (`OLCUM0/O0b_klipler/`) | **Merdivenli protokol** (sayılar tahmin): gün 1 tavanı 10 video; uyarısız biterse gün 2'de 15, gün 3'te 20; 17.10 temposu. Uyarı gelirse o gün ve sonraki 7 gün ölçüm yapılmaz ve Ö0-b kapanır; ikinci uyarı riskine hiç girilmez (D-04 haftalık kilidi tetiklenmez). Sonuç: uyarıdan önceki en yüksek uyarısız günün video sayısı = günlük uyarısız kapasitenin **alt sınırı** (`olculen_gunluk_kapasite`, en çok 20); uyarısız gün yoksa "ölçülemedi"; takvim bununla hesaplanır. Alt sınır < 20 ya da ölçülemedi → ilk film 1800 sn (D-05). A/B'ler (istem biçimi × bekleme biçimi 2×2 çapraz, aynı kliplerde; kalan kliplerle son kare referansı ve zincir karesi boyutu) yalnız **ön karardır**: kol başına en az 12 klip (tahmin) yoksa "ölçülemedi → varsayılan" (istem biçimi `aralik`, bitişte "holds still", son kare referansı yok, zincir karesi doğal 1280×720); bütün kararlar A14a'da yeniden doğrulanır. Adım tutma değerlendirmesi Ö0-b·V3'tedir | 3 ölçüm günü; toplam ≤ 45 klip | evet, ≤ 540 kr (hesap: 45 × 12). **Ölçüm harcamasıdır** (B3 kapalı bir projedir, `00_OKU_BENI.md`): BUT0'da `olcum0` kalemi ve sözleşme kartında satır | 0, 1, 2, 3, 4 | yerel |
| Ö0-c | Ses: arşiv Veo kliplerinde OpenVoice V2 ve Chatterbox dönüşümü (RVC yalnız koşullar okununca); kıyas setinde fısıltı ve bağırma replikleri zorunlu (motor başına her birinden ≥ 4, tahmin); **doğallık ölçüsü**: lisansı doğrulanmış MOS tahmincisi (UTMOS türü; P2'den buraya çekildi) ve/veya `dinleyici`'nin kör ikili karşılaştırması (anahtar varsa; `olcum0/` içindeki küçük Gemini çağrısı); MuseTalk 1.5 kurulumu + 1 klip; ACE-Step 1.5'in 4 GB kartta ipucu süresi (AR3 A5: "≤ 6 GB" katmanı ölçülmedi); büyütücü (Real-ESRGAN türü) 8 sn klip süresi | `olcum0/ses_deneme.py` (geçici ayrı ortamlarıyla) | B2/B3 arşiv klipleri | `O0c.json` (doğallık alanı ölçülmüş ya da `olculemedi: true`) | S1.11 eşiklerini **ve** doğallık ölçüsünü geçen motor varsa ana yol `veo_donustur`; yoksa §2.2 B planı. Doğallık ölçülemediyse seçim `olculemedi` BAYRAK'ıyla karar defterine yazılır ve motor örnekleri (fısıltı ve bağırma dahil) izle-dinle paketine konur. ACE-Step 4 GB'ta ipucu başına süre kabul edilemezse (tahmin: > 10 dk) `acestep` zincirden düşer, `kutuphane` ana basamak olur (D-25). Büyütme 1 saatlik içerik için > 12 saat (tahmin) ise 1080p + gren yolu | 1 | AI84 ≈ 2–5 bin (tahmin) | 0, 1, 4 | yerel |
| Ö0-d | CapCut: `pycapcut` ile taslak okuma, klon, segment taşıma; taslak şifrelemesi | `olcum0/capcut_deneme.py` + kullanıcı (CapCut'ı kapatıp açar) | 1 dk'lık deneme taslağı | `O0d.json` | Şifreliyse ya da klon çalışmıyorsa `yayin_kaynagi: master` ve not yolu "yeni adla kur" | 1 | yok | 0, 1, 4 | yerel |
| Ö0-e | Gemini: 1 paket (30 plan, plan başına 2 ve 3 aday); Gemini API (AI Studio) ücretsiz katmanı: görsel kotası ve fiyatı, **video ve ses girişi** (`izleyici`/`dinleyici` için; bellekten, doğrulanacak), katman (`gemini_katman: ucretsiz \| ucretli \| bilinmiyor`) ve veri kullanım koşulu (`LISANSLAR.json`'a) | `olcum0/gemini_deneme.py` (kullanıcının `gemini_paket.py`'si emsal) + kullanıcı (1 paket) | B3 planları; kurulumdaki ücretsiz Gemini anahtarı (§8.2) | `O0e.json` | Görsel kotası yeterli ve ücret 0 ise (ya da kullanıcı dolar izni verdiyse) paketler API'ye geçer; değilse paket sayısı kesinleşir. Ücretsiz katman video ve ses girişini kabul ediyorsa `izleyici`/`dinleyici` açılır (D-19); etmiyorsa "ölçülemedi" ve izle-dinle bilgi paketi | 1 | yok / küçük $ (yalnız izinle) | 0, 1, 4 | yerel |
| Ö0-f | Claude kullanımı: 1 kâğıt turu (3 seyirci + eşleştirici) ve 1 `kare-tarifcisi` görevinde gerçek token; seyirci gürültüsü (aynı metin 5 seyirciye 2 kez: B2 P1 v11 ve B3 kâğıdı); "karar 6 testi" (aynı etiketli sette daha ucuz model/effort ↔ Opus·high) | betik + ajanlar | B2/B3 metinleri, 44 kare | `O0f.json` | `seyirci_gurultu_std` yazılır; ucuz yapılandırma ancak fark gürültü bandının içindeyse ve karar defterine yazılarak seçilir. Ö0-f yoksa plato eşiği 0,5'tir ve hiçbir rol kısılmaz | 1 | abonelik | 5, 6, 7 (ilk filmin A06'sından önce koşması hedeflenir) | yerel |
| Ö0-g | Kanal teşhisi: B1/B2 gösterim, tıklama oranı, ortalama izleme, tutma eğrisi, trafik kaynağı | `kanal_teshis.py` CSV kipi (kullanıcının YouTube Studio'dan isteğe bağlı tek seferlik CSV dışa aktarımı; adımları `BASLA_BURADAN.txt`'de; OAuth P2, [SON] S-10) | YouTube verisi | `<veri>/BILGI/KANAL_TESHIS.md` | Veri yoksa "ölçülemedi" yazılır; film başlamasını engellemez | 1 | yok | 0, 1 | yerel |
| Ö0-h | Kalibrasyon seti: B3'ün 44 karesinin etiket JSON'u (kayıtlı denetim raporlarından; eksikler `kare-tarifcisi` + `sureklilik-denetcisi` ile) | betik + ajanlar | B3 kareleri ve raporları | `<veri>/GELISTIRME/kalibrasyon/B3_44.json` (yalnız etiket; görseller yerelde); depoya `film.py esitle --gelistirme` ve PR ile girer (§4.5) → `YZ_FILM/ARACLAR/veri/kalibrasyon/B3_44.json` | 44 kare × alan etiketleri tam | 1 | yok | 6, 12 | yerel |
| Ö0-b·V3 | Ö0-b kliplerinin adım tutma ve canlı bekleme değerlendirmesi: adım bitişleri ve kesme anındaki karelerin çıkarılması + `kare-tarifcisi·v3` kör gözlemi + kod karşılaştırması (hareket enerjisi ölçüsü PR-11'le gelir ve dikey kesitte ölçülür) | betik + `kare-tarifcisi` | kayıtlı Ö0-b klipleri (yeniden çekim yok) | `O0b_v3.json` | V3 tutma < %60 → adım sayısı 2'ye iner, `bitis_sabit` payı artar (tahmin eşiği); `sira` ≥ 10 yüzde puanı üstünse `sira`; canlı bekleme zıplama ve dudak hatasını ≤ 2 yüzde puanı artırıyorsa varsayılan olur (D-13). Hepsi ön karardır, A14a doğrular | 1 | yok | 6, 12 | yerel |

**Ö0 sırası:** PR-0 (güvenlik yaması + veri kökü emniyeti, §9) → PR-1 → Ö0-a (adım 2; memmet3 aktarımı ve T10 dahil) → çekirdek ve kurulum
(adım 3–4) → Ö0-1 (adım 9: b, c, d, e, g) → Ö0-2 (f adım 7'den sonra; h ve Ö0-b·V3 adım 12'den sonra); Ö0-1 ve Ö0-2 ilk filmin kâğıt
aşamalarıyla paralel. A01'de (BUT0) Ö0-b sonucu yoksa film **1800 sn** (30 dk) hedefle yazılır; varsa süre bütçe + ölçülen kapasite +
takvimle seçilir (§2.1 D-05).

### 1.3 Film akışı (A00–A18)
"Döngü üst sınırı" sütunundaki tur sayıları ayrıca §1.5'teki küresel geri dönüş bütçesine tabidir. "Kapı" ve "hedef" ayrımı §1.4'tedir.
Bir döngünün tavanı dolunca ne olacağı her aşama için §1.5'teki **tavan sonrası tablosunda** yazılıdır; tavan dolması hattı durdurmaz ([SON] K-4).
"Kim" sütunu her girdiyi üreten çağrıyı da gösterir; `hat/asamalar.py` her girdinin üreten aşamasını zorunlu alan olarak taşır ([SON] S-3).

| No | Aşama | Kim (ajan · betik · kullanıcı) | Girdi | Çıktı dosyası | Geçme şartı | Döngü üst sınırı | Kredi | Nerede (bulutta test) |
|---|---|---|---|---|---|---|---|---|
| A00 | Hazırlık ve konu | ana Claude tek soruyu sorar (aktif film yoksa ve ortam yerelse; bulutta yalnız bilgi cümlesi, §4.1); betik `film.py yeni --konu "<cümle>"`, `evren.py --yedek-dogrula` | kullanıcının cümlesi | `<film>/00_KONU.md`, `HAZIRLIK.json` (sürüm, kanca nabzı, disk, kurulum kademesi, yedek durumu) | Kanca nabzı ≤ 15 sn; KUR1 kurulum tamam; disk ≥ `disk_bos_min_gb`; evren ve ders yedeğinin sha1 listesi doğrulandı (D takılı değilse bilgi; D-42) | — | yok | yerel (evet) |
| A01 | Konu kartı ve süre (BUT0) | `yapimci·konu`; betik `hikaye_odasi.py konu-denetim`, `kredi.py but0` | `00_KONU.md`, evren özeti, `OLCUM0.json`, bakiye | `_HIKAYE_ODASI/01_KONU_KARTI.json`, `01_VARSAYIMLAR.md`, `KARAR_DEFTERI.md` (ilk kayıtlar; `film.py karar ekle` yazar), `_RAPOR/BUT0_FILM.json` | konu-denetim HATA 0; süre ∈ [1800, 2700] (Ö0-b yoksa 1800); kullanıcıya 3 satır bilgi | SubagentStop düzeltme ≤ 2 | yok | yerel (evet) |
| A02 | Brifing | betik `hikaye_odasi.py brifing` | konu kartı, aktif hikâye dersleri, RE | `_HIKAYE_ODASI/00_BRIFING.md` (sha1 kaydı) | 7 bölüm, 1.500–4.000 kelime | — | yok | yerel (evet) |
| A03 | Dört öneri | `hikaye-mimari` × 3 (eksen D/S/E, paralel) + 1 (X; yalnız loglineları "kaçınılacak yol" olarak görür) | brifing | `_HIKAYE_ODASI/02_oneri_<eksen>.md` | `oneri-denetim`: 10 başlık, başlık ≤ 100 kr, konuşan ≤ 8, filtre, çeşitlilik dörtlüsü | BENZER çıkarsa yeni eksenle 1 kez | yok | yerel (evet) |
| A04 | Kör jüri ve seçim | `juri-uyesi` × 4 rol + `uretilebilirlik-denetcisi·juri`; betik `juri-topla` | anonim öneriler | `03_juri_<rol>.json`, `04_SECIM.json`, `04_KULLANICIYA_OZET.md` (bilgi) | Kazanan ≥ 8,0 (hedef); veto yok | Kazanan < 8,0 → yazar 1 kez yeniden + jüri | yok | yerel (evet) |
| A05 | Yapı ve senaryo | `hikaye-yazari·yapi`, `·senaryo`; `oyuncu` × ana karakter (≤ 8); `diyalog-editoru`; betik `yapi-denetim`, `senaryo-denetim` | `04_SECIM.json`, kazanan öneri | `05_YAPI.json`, `06_SENARYO_v<N>.json`, `_RAPOR/HIKAYE_Z_v<N>.json` | yapi-denetim ve senaryo-denetim HATA 0 (Z1/Z2 hikâye ölçüleri, filtre, NE YOK, bilgi durumu, ilk replik ekranda) | SubagentStop ≤ 2; HATA dönüşleri kâğıt turuna sayılmaz ama kendi sayacı vardır: denetim başına `hata_donus_max` 3 (tahmin), aşılınca `yapimci·doktor` (§1.5) | yok | yerel (evet) |
| A06 | Kâğıt seyirci, ilk 2 dk, kilit | `habersiz-seyirci·kagit` × 3 (aşamalı P0→P3), `·ilk2dk` × 3 × 2 sürüm (A/B), `ozet-eslestirici·ozet/bulgu` × 3; betik `seyirci_topla`, `bulgu_yonlendir`; tıkanırsa `yapimci·doktor`; revizyon `hikaye-yazari·revizyon`; betik `devir` (kilit) | senaryonun EKRAN bloğu (`kor_paket --kip kagit`) | `_RAPOR/HS_KAGIT_FILM_t<n>.json`, `HS_ILK2DK_FILM.json`, `HIKAYE.json` + `HIKAYE.md` (kilit), `evren.py on-kayit` | **Kapı:** §1.4 · **Hedef:** GENEL ≥ 8, ölçüt ≥ 7, ORTA ≤ 3/parti, ilk 2 dk 3/3, bütün olgular ≥ 0,80 | 4 tur + doktor 2 yapısal tur + ikinci öneriyle 4 tur (≤ 10); plato kuralı §1.4; ilk 2 dk A/B + 1 üçüncü sürüm (≤ 2 tur) | yok | yerel (evet) |
| A06s | Ses kadrosu (kâğıt) | `ses-tasarimcisi·kadro`; betik `ses_plani.py --profil-denetle` | `HIKAYE.json` (ses_karakteri, ad_telaffuz), evren ses kayıtları | `_SES/SES_PROFILLERI.json`, `_SES/SES_KADROSU.md` | profil denetimi HATA 0 (`veo_ses_tarifi` ≤ 12 kelime, aksan, yaş/filtre sözcüğü yok) | SubagentStop ≤ 2 | yok | yerel (evet) |
| A07a | Harita, kroki, kart tarifleri | `yonetmen·harita` × 3 parti (betik `kroki.py --karsilikli` önerilerini önce GIRDI'ye koyar) ∥ `kart-tasarimcisi`; harita geçince betik `kroki.py --ciz` (A07b'nin kroki PNG'leri) | `HIKAYE.json`, evren mekânları | `_YONETMEN/HARITA_P<n>.json`, `<evren>/mekanlar/<id>/kroki.json` (yeni sürüm), `_YONETMEN/KART_ISTEGI.json`, `_KARTLAR/KART_SPEC.json` | `plan_denetim --harita`, `kroki.py --denetle`, `evren.py --spec-dogrula` HATA 0 | SubagentStop ≤ 2; kart tarifi revizyonu ≤ 2 | yok | yerel (evet) |
| A07b | Sahne grubu planları | `yonetmen·plan` × sahne grubu (≈ 45–55 görev, paralel ≤ 5); betik `dilim.py` | sözleşme, kroki PNG + kurulumlar, EKRAN metni + replik kimlikleri, önceki sahnenin sözleşmedeki `cikis_durumu` (paralel görevlerde); yalnız aynı mekânda ve zamanda süren ardışık sahne çiftinde önceki sahnenin son 2 planının çözülmüş bitişi (bu çift sırayla koşar; [SON] O-12), `PLAN_DILI.md`, sözlükler, GIRDI/DERSLER.md | `_YONETMEN/PLANLAR/S<k>.json` | `plan_sema` + `plan_denetim --sahne` + `kroki.py --sahne` HATA 0 (kancada) | SubagentStop ≤ 2, sonra o partinin harita revizyonu 1 kez | yok | yerel (evet) |
| A07c | Birleştirme, K0, T0, BUT1 | betik `plan_birlestir` (evrenden `karakterler.<id>.{ref, ses}` + kart kopyası), `dunya_defteri --derle --denetle`, `kroki --tum`, `plan_denetim --tum`, `zaman_cizelgesi --asama kagit`, `kredi.py but1`, `olcek.py`, `cekim_listesi` (A07d'nin `CEKIM_LISTESI_P<n>.md`'si) | planlar | `SAHNELER.json`, `DUNYA_DEFTERI.json`, `_RAPOR/K0_FILM.json`, `_RAPOR/Z0_P<n>.json`, `KURGU/surumler/KURGU_PLANI_T0.json`, `URETIM_ONIZLEME.json` (taslak) | K0 ve Z0 HATA 0; BUT1: tahmin ≤ tavan (aşılırsa 5 BÜTÇE; yazılmış film kısaltılmaz) | HATA → `KUYRUK/YENIDEN_YAZ.json` → aynı sahnenin yönetmeni (≤ 2); `sahne_uclari.hikaye_esit` uyuşmazlığında `YENIDEN_YAZ` yalnız ilgili iki sahneye gider | yok | yerel (evet) |
| A07d | Kâğıt plan eleştirisi | `plan-elestirmeni` × 3 ∥ `uretilebilirlik-denetcisi·plan` × 3 ∥ `sureklilik-denetcisi·kagit` × 3 (parti başına) | `CEKIM_LISTESI_P<n>.md`, K0 BAYRAK'ları | `_RAPOR/PLAN_ELESTIRI_P<n>_t<n>.json`, `URET_PLAN_P<n>`, `K0_HAKEM.md` | KRİTİK 0; ORTA ≤ 3/parti | 2 tur | yok | yerel (evet) |
| A07e | Plan seyircisi (ilk iki filmde; değeri ölçülür) | `habersiz-seyirci·plan` × 3/parti | `kor_paket --kip plan` | `_RAPOR/HS_PLAN_P<n>_t<n>.json` | §1.4 kapı politikası | 2 tur | yok | yerel (evet) |
| A08 | Ses tasarımı ve müzik planı | betik `ses_plani --taslak`; `ses-tasarimcisi·tasarim` × sahne grubu, `·muzik`; betik `muzik.py --kagit`, `ses_plani --denetle --tum` | `SAHNELER.json`, `DUNYA_DEFTERI.json`, evren | `_SES/SES_<S>.json`, `_SES/SES_TASARIMI.md`, `MUZIK/muzik_listesi.json`, `<evren>/muzik/leitmotifler.json`, `_RAPOR/S0_FILM.json` | S0 HATA 0 | SubagentStop ≤ 2 | yok | yerel (evet) |
| A09 | İstem derleme ve kâğıt sonu | betik `istem_derle --hareket`, `istem_denetim`, `kamera_agaci` | `SAHNELER.json` (zanaat + ses) | `SAHNELER.json → hareket_istem`, `KAMERA_AGACI.json`, `_RAPOR/ISTEM_FILM.json`, `KAGIT_TAMAM.json` | ISTEM HATA 0; elle istem ≤ %5 | yonetmen·onarim ≤ 2 | yok | yerel (evet) |
| A10a | Yerel kurulum ölçümü | betik `kurulum.py --dogrula`, `olcum/ses.py --kontrol` (ses ortamları ve modeller hazır mı) | — | `_RAPOR/KURULUM_FILM.json` | KUR1 tam; eksik KUR2/KUR3 ortamı yalnız kendi basamağını kapatır | — | yok | yerel (hayır) |
| A10b | Telaffuz testi (yerelin ilk işi) | betik `ses_sec.py --telaffuz` | uydurma adlar | `_RAPOR/S1a_telaffuz.json` | ad hatası 0; geçmeyen ad `hikaye-yazari·dar_degisiklik` (H15) | ad başına 1 değişiklik | AI84 ≈ 1,8 bin (tahmin) | yerel (sahte) |
| A10c | Ses seçimi, motor kıyası, efekt | betik `ses_sec.py --ara/--olc/--oku/--puanla/--sec`; puan farkı < 0,03 ise `ses-tasarimcisi·kadro`; seri başında `ses_kiyas.py`; `ses_kutuphanesi.py --dizinle --eksik` | profiller | `<evren>/karakterler/<id>/ses.json`, `SES_SECIM.html` (bilgi), `_RAPOR/S1*.json` | S1 HATA 0 | — | AI84 ≈ 5 bin; seri kurulumu tavanı 40 bin | yerel (sahte) |
| A10d | Kartlar | betik `istem_derle --kart` → `gemini_paket --kartlar` (kullanıcı taşır) → `gemini_al`; `kart_denetim` + `kare-tarifcisi·kart` + `kare_denetim --karar`; `yonetmen·kart_secimi`; `evren.py --kilitle` | `KART_SPEC.json` | `<evren>` kart sayfaları (kilitli), `_RAPOR/KART_KAPISI.json`, `_KARTLAR/KART_SECIM.json` | KART HATA 0 | 2 CORRECTION turu; sonra tarif revizyonu ≤ 2; sonra en iyi teknik aday + BAYRAK | yok (düzeltme görseli Flow'da 0 kr; günlük tavan) | yerel (sahte) |
| A11 | Başlangıç görselleri, G1 ilk geçiş, kapak adayları | betik `istem_derle --gorsel`, `kamera_agaci` basamakları, `gemini_paket --basamak k --aday 2` → `gemini_al`; `olcum` yerel ölçüm → `kare-tarifcisi·g1` (≤ 12 görsel/görev) → `kare_denetim --karar` → `sureklilik-denetcisi·hakem` (yalnız tek kaynaklı BAYRAK / ÖLÇÜLEMEDİ); kapak 8–12 aday + `kor_paket --kip kapak` + `kare-tarifcisi·kapak` + `habersiz-seyirci·kapak` (ikili) | `SAHNELER.json`, kilitli kartlar | `SIRALI_GORSEL/_ADAYLAR/`, `SIRALI_GORSEL/NNN.jpg` (yalnız G1 GEÇ), `_RAPOR/G1_P<n>_B<k>.json`, `KUYRUK/YENIDEN_URET.json` (G1 maddeleri), `YAYIN/KAPAK_SPEC.json` | İlk geçiş bütün planlarda bitti; kimlik HATA'sı yüzünden yer tutucu ≤ %15 (tahmin; RE `animatik_tur1_yer_tutucu_max_oran`; değilse yalnız kimlik maddeleri için 1 düzeltme turu, sonra §1.5). **Düzeltme turları A12 tur 1'den sonra** (§2.1 D-14). Sıra: önce P1'in ilk geçişi → **KR3a** P1 animatik ön turu (kapı değil; dersleri P2/P3 planlarına ve görsellerine geçer) → P2/P3 ilk geçişi | ilk geçiş 1 | yok | yerel (sahte) |
| A12 | Animatik | T1 (`zaman_cizelgesi --asama animatik`); ses `seslendir --animatik` (seçilmiş seslerle TTS), `muzik --uret`, `ses_katmani --cizelge T1`, `son_miks --animatik`; `kurgu_render --animatik`; `kor_paket --kip animatik`; `habersiz-seyirci·animatik` × 3 + `·ilk2dk` × 3 (gerçek kapakla); `ozet-eslestirici`; `seyirci_topla`; tur 1'de `kesici` + `kurgu_denetim --kesme-simule`; `kurgucu·duzelt`; `kurgu_uygula`; tur 1'den sonra G1 düzeltmeleri; `izleyici` ve `dinleyici` (ücretsiz anahtar varsa; BAYRAK; D-19); `kurgu_render --bilgi-paketi` | T1, görseller, sesler, `HIKAYE.json` | `ANIMATIK/animatik_v<N>.mp4`, `ANIMATIK/ISITSEL_DOKUM.md`, `_RAPOR/HS_ANIMATIK_FILM_t<n>.json`, `KURGU/surumler/KURGU_PLANI_T1_v<N>.json`, `FILM_DURUM → animatik: ONAYLI` (imza), `BILGI_PAKETI/animatik/` (kullanıcıya bilgi) | **Kapıyı yalnız bütün kareleri G1 GEÇ olan tur açar.** Kapı §1.4; render süresi = T1 ±1 kare; yer tutucu ≤ %10 | 3 tur + 1 kurtarma (`yapimci·doktor`); sonra DUR + kâğıt ürün teslimi | AI84 ≈ 13–16 bin (tahmin) | yerel (sahte) |
| A13 | Kesin bütçe BUT2 | betik `kredi.py but2`, `olcek.py`; `hat-denetcisi` | `URETIM_ONIZLEME`, kuyruk, `OLCUM0` | `URETIM_ONIZLEME.json/.md` (kredi, Flow günleri, kullanıcı el işi saati, token projeksiyonu), `_RAPOR/HAT_BUT2.json` | tahmin ≤ bakiye × 0,9 ve ≤ tavan; HAT: GİT | — | yok | yerel (sahte) |
| A14a | Dikey kesit (ilk filmde atlanamaz) | betik `blok_plani --kesit`; Memmet `--mod elle` (kullanıcı GÖNDER'e basar); V1 + SC1 + V2 + V3 + G1Z; `seslendir --parti`; `muzik --yerlestir`; `renk_cila`; `buyut`; `son_miks`; `kurgu_render --kesit`; `kor_paket --kip kesit`; `habersiz-seyirci·kurgu` × 3 (yalnız kesit); `izleyici` ve `dinleyici` (anahtar varsa); `kurgu_render --bilgi-paketi`; `ders-editoru` (PILOT) | P0 + P1'in ilk dakikası (≈ 43 plan, hesap) + kapsama eksikse ≤ 10 plan | `KESIT/kesit_v<N>.mp4`, `_RAPOR/PILOT_FILM.json`, `BILGI_PAKETI/kesit/` (kullanıcıya bilgi) | teknik kapılar HATA 0; kesit seyircisinde KRİTİK 0; PILOT kararları (istem biçimi, take değeri, canlı bekleme, ses yolu) yazıldı | yeniden çekim plan başına ≤ 2 | evet (≈ 35–45 klip; filmin kendi planları, ek kredi değil) | yerel (sahte) |
| A14 | Video blokları | betik `blok_plani` (uygunluk kuyruğu, blok ≤ 20 plan) → Memmet (`elle`; gece yalnız izinle) → her indirmede V1 + SC1 → `film.py bekle --blok` blok sonunu arka planda yoklar (§4.2) → blok arasında V2, V3, `kare_zinciri --cikar` + G1Z → `kuyruk.py`; P1 videoları bitince **KR8a** P1 kurgu ön turu (kapı değil; dersleri P2/P3 bloklarına geçer); kullanıcı GÖNDER'e basar | `SIRALI_GORSEL` (G1 GEÇ + SHA1), `hareket_istem` | `SIRALI_VIDEO/NNN.mp4`, `KUNYE/NNN.json`, `KREDI_DEFTERI.jsonl`, `<veri>/HESAP/FLOW_YUK.jsonl`, `_RAPOR/V1_B*`, `V2_*`, `V3_*`, `G1Z_*`, `S2m_D*` | her klip V1 + V2 + V3 GEÇ; zincir kaynağı ayrıca G1Z GEÇ | plan soyu başına toplam deneme ≤ 3 (ilk + 2 yeniden) | evet | yerel (sahte) |
| A15 | Ses | betik `seslendir --parti`, `ses_donustur`, `ses_karar` (merdiven); gri bantta `hikaye-yazari·replik_kabul` (her seferinde yeni örnek) | klipler, evren sesleri, `SESLER/diyalog.json` | `SESLER/diyalog.json` v2, `SESLER/donusum/`, `_RAPOR/S2_*.json` | S2 HATA 0; merdiven tükenirse açık rapor | merdiven basamakları; yeniden çekim ≤ 2 | AI84 (`ai84_vc` ≤ 20 bin tavan) + Flow (ses dilimi) | yerel (sahte) |
| A16 | Kurgu | `plan_kurgu` (`kirp_oner`), ses (`diyalog_esitle`, `ses_katmani T2`, `muzik --yerlestir`, `son_miks`), `kurgu_render --onizleme`, `kurgu_denetim` (Z3), `kor_paket --kip kurgu`, `habersiz-seyirci·kurgu` × 3 (aşamalı, tam film) + `·ilk2dk` × 3, `izleyici` ve `dinleyici` (anahtar varsa), `kurgucu·duzelt/·sifir_kredi/·kirp_incele`, tur 1'de `kesici`, `kuyruk.py`, `renk_cila`, `buyut`, `capcut_film`; sonunda `arsivle` (D-38) | videolar, `diyalog.json`, raporlar | `KURGU/KURGU_PLANI.json` + `surumler/`, `KURGU/onizleme_v<N>.mp4`, `_RAPOR/Z3_v<N>.json`, `HS_KURGU_FILM_t<n>.json`, `S3…S7`, CapCut taslağı "YZ <FILM> v<N>", `KURGU/son_capcut_projesi.json`, `KURGU/altyazi_en.srt`, `altyazi_tr.srt` | Z3 HATA 0; §1.4 kapı; S7 −14 ±1 LUFS, ≤ −1 dBTP; KRİTİK = 0, **ya da** kurgu tavanı doldu ve kalan KRİTİK'ler açık eksik raporunda listelendi (§1.5 kural 8) | 3 tur + 1 koşullu (son turda GENEL ≥ 0,5 arttıysa) | evet (kurgu dilimi; plan başına ≤ 2) | yerel (sahte) |
| A16n | Kullanıcı notu (isteğe bağlı döngü) | beceri `film-not` → betik `taslak_fark`, `notlari_oku`; `kurgucu·not`; `kurgu_uygula`; `kurgu_denetim --hepsi`; `capcut_yama`; kullanıcı CapCut'ı kapatır | kullanıcının notu ya da CapCut düzenlemesi | `KURGU/TASLAK_FARK.json`, `NOTLARIM.json`, `NOT_CEVAPLARI.md`, klon taslak "<adı> · v<N+1>", `_RAPOR/YAMA_v<N>.json` | notların %100'ü bir kararla kapanır; kullanıcının kaynak taslağı değişmez; klon öz denetimi 0 fark | kullanıcı istedikçe | yalnız KRİTİK için, dilimden | yerel (sahte) |
| A17 | Yayın | betik `capcut_film --yayin` (NOTLAR'sız ve Altyazi kanalsız taslak; SRT YouTube'a ayrı gider); kullanıcı CapCut'tan 4K 24 fps dışa aktarır → `YAYIN/`; `film.py bekle --kullanici` dosyayı yoklar; betik `kalite_denetim --final` + yayın doğrulaması (+ gerekirse `son_miks --mux`); `jenerik`; `kapak`; `yayin-paketcisi·paket` + `·kapak`; `yayin_paketi --dogrula`; `shorts_mp4` (3 Short + fragman); sonunda `arsivle` | yayın taslağı, `KURGU_PLANI`, `HIKAYE.json`, `KANAL_TESHIS.md` | `YAYIN/<FILM>_4K.mp4` (kullanıcı), `YAYIN/YAYIN_DOGRULAMA.json`, `YAYIN/ses_master.wav`, `YAYIN/kapak_<n>.jpg`, `YAYIN/PAKET.json`, `YAYIN/SHORTS/*.mp4`, `YAYIN/FRAGMAN/*.mp4`, `KURGU/altyazi_*.srt` | final kalite HATA 0 (siyah, donma, planlanmamış sessizlik, −14 ±1 LUFS, ≤ −1 dBTP); paket doğrulama HATA 0 (başlık ≤ 100 kr, bölüm kuralları, YZ beyanı alanı, "kill" BAYRAK) | mux kanıtı yoksa A16n | yok | yerel (sahte) |
| A17y | Yükleme (isteğe bağlı; varsayılan kapalı) | betik `youtube_yukle.py` | `YAYIN/PAKET.json` | yükleme kaydı | kullanıcının o film için `YUKLE.bat` ile verdiği açık onay | — | yok | yerel (hayır) |
| A18 | Kapanış ve öğrenme | betik `ders_derle`; `ders-editoru`; `hikaye-yazari·evren`; betik `evren.py --film-sonu`, `ders_derle --film-sonu` (`FILM_SONU_RAPORU.md`), `evren.py --yedekle` + `ders_defteri --yedekle` (D'ye kopya; D-42), `arsivle` (kendiliğinden; D-38) | bütün raporlar, ders ham kayıtları | `<veri>/BILGI/DERSLER_AKTIF.md`, `KURALLAR_OGRENILEN.json` (aday/deneme), güncel evren, `FILM_SONU_RAPORU.md` (açık eksikler, `hedef_alti` maddeleri, ölçülemeyenler), yedek sha1 listesi | ders korkulukları HATA 0; D takılı değilse yedek bilgiyle sonraki filmin A00'ına kalır | — | yok | yerel (evet) |
| A18a | Yayın sonrası analiz (48 sa, 7 gün, 28 gün) | betik `yayin_analiz.py`; `yayin-paketcisi·izleme` | kullanıcının isteğe bağlı YouTube Studio CSV'si (OAuth P2) | `_RAPOR/YAYIN_ANALIZ_<gun>.json`, ders kayıtları (`kaynak: gercek_seyirci`) | veri yoksa "ölçülemedi" | — | yok | yerel (hayır) |

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
  Video kredisi harcandıktan sonraki kapılarda (HS_KESIT, HS_KURGU) kâğıt ürüne dönülmez; §1.5'teki tavan sonrası tablosu uygulanır.
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
8. KRİTİK = 0 olmadan CapCut taslağı kullanıcıya verilmez ([KU2]), **ya da** kurgu tavanı (küresel bütçe) doldu ve kalan KRİTİK'ler açık eksik
   raporunda plan ve zaman koduyla listelendi; taslak bu raporla birlikte verilir ([SON] K-4; küresel bütçeyle çelişki böyle kalktı).

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
| Stop kancası devamı | 8 ardışık (`stop_ardisik_max`) + `film_token_tavan` (`hat_esikleri.json`; değer = Ö0-f projeksiyonu × 1,5, Ö0-f yoksa ilk 30–50 görevden sonraki D-08 projeksiyonu × 1,5; tahmin) | 8 BEKLE + `TOKEN_PROJEKSIYON.md`; `hat-denetcisi` döngü taraması yapar: aynı görev ≥ 3 kez yinelenmişse o madde `durdu` olur ve hat sürer; döngü yoksa tavan bir kez × 1,25 genişler ve karar defterine yazılır (tahmin) |
| Aşama başına görev sayısı | `olcek.py` tahmini × 1,5 (tahmin) | 8 BEKLE + `TOKEN_PROJEKSIYON.md` (soru değil) |

**Tavan sonrası genel merdiven** ([SON] K-4; seyirci kapıları §1.4'te, aşağıdakiler geri kalan bütün kapılar için). Bir döngünün tavanı dolunca
`film.py` 6 KAPI vermez; merdivenin sonraki basamağını görev olarak açar. `hat/asamalar.py`'de her kapının `tavan_sonrasi` alanı zorunludur
(boşsa `test_asamalar` HATA). Basamaklar sırayla:
1. **Aynı sahibin başka kipi** (ör. `yonetmen·onarim`, partinin harita revizyonu, `hikaye-yazari·revizyon`, `ses-tasarimcisi·kadro`): 1 tur.
2. **Üst sahip:** plan ve sahne düzeyindeki madde `hikaye-yazari·dar_degisiklik`'e gider (sahneyi sadeleştir, böl ya da kes; H15 bütçesinden düşer;
   bütçe dolmuşsa doğrudan 3. basamak); film düzeyindeki madde `yapimci·doktor`'a gider.
3. **Plan ya da sahne `durdu`:** `kurgucu·sifir_kredi` zorunlu çözümü yazar (kâğıtta: planı çıkar, köprü kartı ya da ekran dışı ses koy; videoda:
   örtü, yer tutucu, kesme); BAYRAK; hat o plansız sürer. `dunya_defteri` ve Z1 kurulum denetimi çıkarılan plandan sonra yeniden koşar.
4. **Feragat edilemeyenler:** güvenlik (Flow kilidi, hesap, gizli bilgi), filtre ve yaş sözcüğü, yasak öğe, kimlik (G1, G1Z, V2) ve şema HATA'sı taşıyan
   öğe hiçbir zaman üretime ya da yayına gitmez; 3. basamakta mutlaka çıkarılır. Film düzeyindeki şema ya da araç HATA'sı (kod hatası) hattı tek
   başına durdurur ve `film-gelistir` işi olur (kullanıcıya bilgi; soru yok).
5. **Geri kalan bütün maddeler** `hedef_alti: true` ve açık eksik raporuyla (`FILM_SONU_RAPORU.md`) sürer. Gerekçe D-20'ninkiyle aynıdır: döngü
   tasarruf için değil, sahibin ve üst sahibin elindeki bütün kalite yolları denendikten sonra durur (KK6); hat da kimseye soru sormadan sürer (KK1).

| Aşama · döngü | Tavan | Tavan sonrası (yukarıdaki basamaklarla) |
|---|---|---|
| A01 konu denetimi | SubagentStop ≤ 2 | `yapimci·konu` yeni eksenle 1 kez (ör. çocuk kahraman → yetişkin ya da dolaylı); yine HATA → konu bu sistemle üretilemez: "yüzüne vur" raporu, kâğıt ürün yok, 6 KAPI (kullanıcı kendiliğinden yeni konu verebilir; §8.4) |
| A03 benzer öneri | 1 yeni eksen | yine BENZER → en ayrışan dört öneriyle jüriye gidilir, çeşitlilik BAYRAK'ı jüri paketine yazılır |
| A04 jüri < 8 ya da veto | 1 yeniden yazım | veto almamış en yüksek medyanlı öneri kazanır (`hedef_alti`); hepsi vetoluysa `yapimci·konu` yeni eksenle A03'ü 1 kez yeniden açar; yine hepsi vetoluysa kâğıt ürün (brifing + öneriler + jüri) ve 6 KAPI |
| A05 yapı ve senaryo HATA | SubagentStop ≤ 2; `hata_donus_max` 3 (tahmin) | `yapimci·doktor` → `hikaye-yazari·dar_degisiklik` → filtre, NE YOK ve şema maddeleri silinerek kapanır (4. basamak); Z1/Z2 hikâye ölçüleri `hedef_alti` ile sürer |
| A06s ses profili | SubagentStop ≤ 2 | kural ihlali (yaş/filtre sözcüğü, > 12 kelime) kodla kırpılır ve BAYRAK; aksan bilinmiyorsa "neutral" + BAYRAK |
| A07a harita ve kart tarifi | SubagentStop ≤ 2; kart tarifi ≤ 2 | harita: `yonetmen·harita` yeni örnek 1 kez → sahne düzeyi maddeler `dar_degisiklik`; kart: §1.5 küresel satırı (`kart_secimi` + BAYRAK) |
| A07b–c plan HATA | ≤ 2 + partinin harita revizyonu 1 kez; `YENIDEN_YAZ` ≤ 2 | 2 → 3 basamağı: plan `durdu` + `kurgucu·sifir_kredi` (kâğıtta); feragat edilemeyen HATA'lı plan çıkarılır |
| A07d plan eleştirisi | 2 tur | kalan KRİTİK → `yonetmen·onarim` 1 kez → `dar_degisiklik` → plan `durdu`; ORTA'lar `hedef_alti` |
| A07e plan seyircisi | 2 tur | §1.4 (seyirci kapısı) |
| A08, A09 ses ve istem | ≤ 2 | A08: S0 maddesi `ses-tasarimcisi·tasarim` yeni örnek 1 kez → kod varsayılanı (tek yatak, efektsiz) + BAYRAK; A09: `yonetmen·onarim` → `istem_elle` (oran ≤ %5 içinde) → plan `durdu` |
| A10b telaffuz | ad başına 1 değişiklik | ikinci ad da geçmezse `veo_metin` okunuş yazımı + `tts` sözlüğü denenir; yine geçmezse ad yalnız yazıyla (altyazı ve kart) verilir, replikte hitap kullanılmaz (`hikaye-yazari·dar_degisiklik`) + BAYRAK |
| A10c ses seçimi | — | puan farkı < 0,03'te `ses-tasarimcisi·kadro`; aday yoksa ölçü sırasıyla en iyi aday + BAYRAK + izle-dinle örneği |
| A11 ilk geçiş | 1 (+1, yer tutucu > %15 ise) | hâlâ > %15 → animatik tur 1 yer tutucularla koşar (D-14); kimlik maddeleri G1 merdivenine (küresel satır) devredilir |
| A12 animatik | 3 + 1 (küresel) | §1.4 (kâğıt ürün) |
| A13 hat denetçisi GİTME | — | GİTME'nin kapatma koşulu sahibine kuyruk maddesi olur; sahip düzeltince `hat-denetcisi` yeni örnekle 1 kez; ikinci GİTME güvenlik ya da bütçe nedenliyse 7/5 kalır (fiziksel iş bekler), değilse `hedef_alti` ile A14a'ya geçilir (kesit gerçek ölçümdür) |
| A14a dikey kesit | yeniden çekim plan başına ≤ 2 | kalan KRİTİK önce `kurgucu·sifir_kredi`; ≥ 3 planda aynı kök neden (sistematik) varsa sahibi kök nedeni düzeltir (ses yolu, istem biçimi, adım sayısı) ve ≤ 5 planda (tahmin) 1 kez yeniden ölçülür; sonra PILOT kararı yazılır, A14 `hedef_alti` ile başlar |
| A14 video soyu, A15 ses merdiveni | §1.5 küresel satırları, §2.2 | var |
| A16 kurgu | 3 + 1 (küresel) | kural 8: taslak açık eksik raporuyla verilir |
| A17 yayın denetimi | mux kanıtı yoksa A16n | teknik HATA (siyah kare, donma, LUFS) `son_miks --mux` ve `kurgu_uygula` ile 1 kez; kalırsa yayın paketi "yayına hazır değil" + nedeni yazar (yükleme zaten kullanıcının işidir) |

### 1.6 Ölçek ve takvim (tek kaynak `olcek.py`; belgelerdeki sayılar yerine onun çıktısı kullanılır)
| Kalem | 30 dk | 40 dk | Kaynak |
|---|---|---|---|
| Plan / klip | ≈ 370 / ≈ 305 | ≈ 495 / ≈ 405 (aralık 300–440 klip) | ZN §2.6; BK §3 #5; B2'den ölçekleme ([SA] K-1) |
| Flow video kredisi (taban × 1,30 kapı payı) | ≈ 4.750 | ≈ 6.320 | RE `kredi_klip_720p` 12; [UM2] pay 0,30 |
| Flow video gönderimi (× 1,3) | ≈ 400 | ≈ 527 | [UM2] (hesap) |
| Flow görsel düzeltme gönderimi | ≈ 90–180 | ≈ 116–240 | [UM2] / [GS2] (tahmin; kesme turundan sonra düşer) |
| AI84 kredisi (film) | ≈ 20–25 bin | ≈ 25–30 bin; tavan 60 bin | [SM2] |
| Ajan görevi | ≈ 300–450 | ≈ 350–570 (kör gözlem ≈ 145–175 dahil; §3.6) | [UM2], [GS2] (tahmin) |
| Takvim | Yalnız `olcek.py` çıktısıdır; belgede sabit gün sayısı yazılmaz ([SON] S-8). Formül: `video_gun = ceil(video_gonderim / olculen_gunluk_kapasite)`, `gorsel_gun = ceil(gorsel_duzeltme / gorsel_gunluk_tavan)`; görsel günü video günü olamaz (sıra kuralı 7); kâğıt, yerel hazırlık, animatik ve kurgu/ses süreleri `olcek.py`'nin ölçümle güncellenen tahminleridir | | [UM2] takvimi, [SA] K-1 #2; D-04'ün günlük 20 görsel tavanıyla (tahmin) 116–240 düzeltme yalnız görselde 6–12 Flow günü eder (hesap) |
| Kullanıcının el işi saati | `olcek.py` hesaplar ve `URETIM_ONIZLEME`'de gösterir (GÖNDER sayısı × süre + paket sayısı × süre + dışa aktarım) | | [ESY] EO10, [SA] K-2 #3 |

## 2. Tartışmalı noktalarda verilen kararlar ve gerekçeleri

### 2.1 Temel kararlar (D-01 … D-45)
Her karar: **ne** → **neden** (kanıt) → **nerede uygulanır**. Kesin kararlar (KK1–KK6) kullanıcınındır ve tartışılmaz; aşağıdakiler onların
nasıl uygulanacağına dair ekip kararlarıdır.

**Hat güvenliği ve ölçüm**
- **D-01 · Önce ölç, sonra yaz: Ö0 ölçüm turu.** Kâğıt aşamalarının kodu Ö0'ı beklemez; yerel aşamaların (A10–A17) P1 sırası Ö0 sonucuna göre
  kesinleşir. Neden: tasarımın taşıyıcı varsayımları ölçülmedi: Omni'nin saniyeli adımlara uyması ([YN2] R1), 4 GB kartta ses dönüştürme
  ([SM2] §4.8.3 "kıyasla ölçülecek"), 11 Claude Code davranışı ([CM2] §4.9.4), CapCut klonu ([KU2] R8), Gemini kotası ([UM2] Q16), Flow kapasitesi
  ([SA] K-1). Pilotu ilk filmin A14a'sına bırakmak, ≈ 120 P0 satırını ölçülmemiş temelle yazmak demektir ([SA] K-4). Ö0'ın her denemesi yalnız gerçekten var olan araçlarla koşar; bu yüzden Ö0-1 ve Ö0-2'ye
  bölündü ([SON] O-2). Yer: §1.2, §9 adım 2, 9 ve 12a.
- **D-02 · Güvenlik yaması her şeyden önce (PR-0).** Depodaki `memmet.py` bugün KK5'i çiğniyor: `DOGRULAMA_KELIMELERI` (satır 58) "olağan dışı
  etkinlik"i doğrulama sayıyor ve `kontrol_noktasi()` (satır 167–176) metin kaybolunca 12 saate kadar bekleyip kendiliğinden devam ediyor;
  `HATA_KELIMELERI`'ndeki "olağan/unusual" tek bir sonuç kartında yeniden gönderime yol açıyor ([UM2] S1, S1b); `film.py` `Kisitlandi` gelince
  sıradaki sağlayıcıya geçiyor; eski `.bat`'lar kapıları atlıyor ([UM2] S2). Yama memmet3'ün depoya gelişini beklemez ([SA] K-6).
  **PR-0'ın kapsamı** (depodaki `memmet.py`'ye ve memmet3'e aynen; Ö0-b'nin ön koşulu): (a) **her kipte** (`elle`, `gece`) olağan dışı metni
  görülünce Memmet hazırlamayı keser, sayfada başka hiçbir işlem yapmaz (tıklama, yazma, yenileme yok), `FLOW_KILIDI.json` yazar, ekrana ve Telegram'a
  "Flow uyarı verdi: GÖNDER'e basma, sayfayı yenileme" yazar ve **7** ile çıkar; memmet3'ün `elle` kipindeki "olağan dışıda durmaz, kullanıcı sayfayı
  yeniler" yolu (H/olagandisi-dur 18.10) silinir, kullanıcı GÖNDER'e bassa bile sonraki plan hazırlanmaz; (b) gece kipindeki "uyarıda 5 kez sayfa
  yenile" davranışı silinir ([UM2] S6); (c) kodda varsayılan tempo 17.10 değerleridir ([UM2] S3; `gevsetilemez`); `MEMMET_AYAR.json` daha hızlı bir
  değer taşıyorsa yavaş olan uygulanır; (d) son gönderim zamanı ve kalan mola `<veri>/HESAP/FLOW_TEMPO.json`'a yazılır ve açılışta okunur; yeniden
  açılış molayı sıfırlamaz ([UM2] S14; şemayı PR-2'de `flow_yuk.py` devralır); (e) `saglayicilar/flow.py` Memmet'in çıkış kodunu `Kisitlandi(kod=…)`'a
  eşler (7 → `olagandisi`, 2 → `dogrulama`), kodu bilinmeyen `Kisitlandi` sağlayıcı değiştirmez (kapalı başarısız; [UM2] S13); (f) reCAPTCHA, doğrulama
  ya da oturum düşmesinde Memmet beklemez, kendiliğinden sürmez: bildirir ve **2** ile çıkar (kullanıcı çözer, `VIDEO_*.bat`'ı yeniden açar; §8.4);
  (g) `SAHNELER.json`'u okuyan bütün v1 araçları `_surum ≥ 2` görünce 4 ile çıkar ("Memmet v2 gerekli"; §5.1 kural 1). T10 her kip için ayrı koşar.
  **Veri kökü emniyeti** (PR-0, `kurulum.py --veri-emniyet`; ilk yerel oturumun ilk işi; [SON] K-2): yama yalnız depoyu düzeltir, kullanıcının
  masaüstündeki eski giriş noktaları canlı kalır. Bu yüzden `<veri>/ARACLAR/memmet.py`, `film.py`, `_memmet_yedek_*.py` ile `<veri>` altında `memmet.py`'yi
  çağıran bütün `.bat`/`.cmd`/`.ps1` dosyaları (`<veri>/FILMLER/*/` içindeki `MEMMET_*`, `FILM_HATTI`, `CAPCUT_PROJESI_OLUSTUR`; B3 `_BOLUM3\_araclar\gece_video.ps1`;
  17.10'daki `memmet_dongu.ps1` döngüsü bulunursa) ve veri kökündeki `BASLA_BURADAN.txt`, `00_BENI_OKU.txt`, `KURULUM.bat`, `YENI_FILM.bat` (film adını
  soruyor; KK1) `_ESKI/` altına **taşınır** (silinmez). Yerlerine tek satırlık emeklilik `.bat`'ı ("Bu dosya emekli. Masaüstündeki FILM_SETI.bat'ı kullan.")
  ve `memmet.py` için depo sürümünü mutlak yolla çağıran sarmalayıcı konur (depo sürümü `--blok`/`--onizleme` olmadan gönderim yapmaz, [UM2] S2).
  Veri kökü `CLAUDE.md`'sini (§4.7) bu adım yazar; `OpenMontage` klasörüne dokunulmaz (BK §7 #11). Taşınanların listesi kullanıcıya bilgi olarak
  verilir. memmet3'ün aktarımı da ilk yerel geliştirme oturumunun işidir (sahibi: üretim; §4.5). Yer: §6.1, §6.9, §9 PR-0 ve adım 2.
- **D-03 · Hesap değiştirme yasağı.** İşaretli Flow hesabının yerine başka bir Google/Flow hesabıyla (ortak, aile, ikinci hesap) devam edilmez;
  kie.ai hiç kullanılmaz (BK §6.4 "gri abonelik havuzu" şüphesi). Neden: işaretlemeden sonra hesap değiştirmek bot tespitini atlatmanın bir
  biçimidir (KK5); BK §6.2 #8'deki "ikinci hesap ya da kie.ai" seçeneği bu kararla kapanır. Uygulama: Memmet Flow'da görünen hesap e-postasının
  yalnız sha1'ini `HESAP_DURUMU.json`'a yazar (açık metin saklanmaz). Son uyarıdan sonraki 14 gün içinde (tahmin) hesap kimliği değişirse
  `FLOW_KILIDI.json` (`neden: hesap_degisti`, kod 7) yazılır; kilit yalnız **asıl hesapta** `UYARI_GECTI.bat` şartlarıyla kalkar. Uyarı kaydı yokken
  hesap değişirse yalnız kaydedilir ve bilgi verilir. Resmî Vertex Veo API'si atlatma değildir (ayrı, resmî hizmet; başka Flow hesabı kullanılmaz).
  Ama **otomatik geçiş yoktur** (D-41): `FLOW_KILIDI` varken `veo_vertex` yalnız iki şartla kullanılır: kullanıcı `IZINLER.bat` ile ayrıca
  `izinler.flow_kilitliyken_vertex`'i açmıştır **ve** `usd_tavan_film > 0`'dır (fiyat Ö0'da ölçülmüş olmalı). O zaman `blok_plani` kalan planlara
  Vertex'i planlı sağlayıcı olarak yazar, Flow'a gönderim 0 kalır ve her Vertex çağrısı bütçe noktasından (BUTK) geçer ([SON] O-15).
- **D-04 · Flow yükü hesap düzeyinde ve yalnız sıkılaşır.** Tempo 17.10 değerleridir (gece 12–30 sn, aynı anda 2, iki partide bir 15–30 dk mola;
  gündüz 6–15 sn; 8 gönderimde 3–6 dk mola; BK §6.2). `FLOW_YUK.jsonl` her gönderimi, `FLOW_TEMPO.json` bir sonraki izinli zamanı ve mola
  sayaçlarını tutar; Memmet yeniden açılsa da kalan mola sıfırlanmaz ([UM2]; asgari hâli PR-0'da, D-02 d). Günlük görsel tavanı 20 ve görselden
  videoya 12 saat Ö0-b ölçene kadar geçerlidir (tahmin). Aynı takvim haftasında ikinci uyarı → hesap 7 gün kilitli (tahmin; [SA] §7). Bu sayıların
  hepsi yalnız `hat_esikleri.json`'da `gevsetilemez: true` ile durur; `FILM_AYAR.json`'da yazılırsa `esikler.py` yalnız sıkılaştırır (D-34).
  Ders defteri tempoyu yalnız yavaşlatabilir, tavanı yalnız düşürebilir. Uyarıyı ya da politika reddini **kasıtlı tetikleyen** hiçbir ölçüm ve
  deneme yapılmaz; Ö0-b ilk uyarıda kapanır (§1.2, §10.4). Takvim ölçümden türetilir: `gun = ceil(gonderim / olculen_gunluk)` ([SA] K-1 #2).
- **D-05 · Süre yazımdan önce seçilir; yazılmış film kısaltılmaz.** BUT0 (A01) [1800, 2700] sn aralığında bütçeye ve ölçülen kapasiteye
  (`gun ≤ takvim_hedef_gun`, varsayılan 21 gün, tahmin) sığan en uzun süreyi seçer. Ö0-b sonucu yoksa, Ö0-b'nin ölçtüğü uyarısız gün alt sınırı 20'nin
  altındaysa ya da ölçülemediyse (merdivenli protokol, §1.2) ya da 40 dk takvime sığmıyorsa ilk film 1800 sn yazılır; 1800 sn bile sığmıyorsa yine 1800 sn yazılır ve takvim olduğu gibi bilgi
  olarak verilir. Neden: bütçe ve kapasite ancak yazımdan önce süreyi belirleyebilir ([SN2] §2.5); 30 dk RE `film_sure_aralik_sn`'nin
  alt sınırı ve kullanıcının 30–45 dk aralığının içindedir; süre kalite değildir (KK6 çiğnenmez). Yer: `kredi.py but0`, `olcek.py`.
- **D-06 · KK1'in yorumu: soru yok, bekleme yok, iş baştan yazılı.** Kullanıcıya konu dışında karar sorusu sorulmaz ve hat hiçbir kullanıcı kararını
  beklemez (tek istisna: kullanıcının kendisi açtığı `--onayli` kipi, §8.5). Para, gece çalışması ya da dış hesap içeren ayarların güvenli varsayılanı vardır ve hepsi **kapalıdır**: gece Flow çalışması, dolar
  harcaması (`usd_tavan_film: 0`), Gemini'nin ücretli kullanımı, Flow kilitliyken Vertex, CC0 efekt indirme, YouTube bağlantısı, yükleme. Ücretsiz
  Gemini anahtarı ise bir **kurulum işidir**, soru değildir (§8.2; Telegram anahtarı ve Flow girişi gibi): anahtar varsa ve maliyet 0 ise `izleyici`
  ve `dinleyici` açıktır (D-19). Kullanıcı kapalı ayarları yalnız kendi isteğiyle `IZINLER.bat` ile açar;
  sistem bu dosyayı `BASLA_BURADAN.txt`'de ve kullanıcı sözleşmesi kartında bir kez anar, hiçbir zaman sormaz. Kullanıcının fiziksel işleri
  baştan sayılarıyla yazılır (**kullanıcı sözleşmesi kartı**, §8.1; sayılar `olcek.py`'den). Neden: [UM2] Q9 ("kurulumda bir kez sorulur") KK1'e
  aykırıdır; [CM2] İ-9'un ".bat bilgi" biçimi doğrudur ama [SA] K-2'nin uyardığı gizli iş yükü ancak sayıların baştan söylenmesiyle dürüst olur.
- **D-07 · DUR'dan sonra ekip varsayılanı.** Kapı merdiveni tükenirse (§1.4) kullanıcıya "ne yapayım?" diye sorulmaz: kâğıtta konu kartı bir kez
  yeni eksenle yeniden yorumlanır; yine geçmezse kâğıt ürün (senaryo + varsa animatik) "yüzüne vur" raporuyla teslim edilir ve videoya geçilmez
  ([SA] K-2 #5). Kâğıt seyirci kapıları dışındaki kapılarda tur tavanından sonraki yol §1.5'teki tavan sonrası merdivenidir; hat orada da
  kimseye soru sormadan sürer. Kullanıcı kendiliğinden "yeni konu" ya da "bu hâliyle devam" derse bu bir kesin istek olarak karar defterine yazılır ve ilgili aşama
  yeniden açılır ([SN2] §4.8.1).
- **D-08 · Claude kullanımı ölçülür ve sınırlanır.** Her görevin `GOREV.json → kullanim {girdi, cikti, onbellek_okuma, sure_sn, model, effort}`
  alanı SubagentStop kancasında ajanın döküm dosyasındaki kullanım satırlarından doldurulur (döküm yolunun kanca girdisinde gelmesi
  doğrulanacak; gelmezse karakter/3 tahmini, "tahmin" etiketiyle). `film.py` film ve aşama toplamlarını `FILM_DURUM → harcama.token`'da tutar.
  İlk 30–50 görevden sonra kalan aşamaların projeksiyonu `TOKEN_PROJEKSIYON.md`'ye yazılır ve kullanıcıya bilgi verilir. Aşama görev tavanı
  (`olcek.py` tahmini × 1,5) ya da kullanım sınırı dolunca hat **8 BEKLE** + projeksiyon verir; DUR değildir. Neden: EMBERFALL'da kullanım sınırı
  doldu ve ajanlar yarıda kesildi (YAPIM_REHBERI §1); film ≈ 350–570 görev ve en kötü durumda ≈ 6–7 M seyirci tokeni ister ([KU2] R3, [SA] K-3).
  Film düzeyindeki tavan `film_token_tavan`'dır (§1.5). `PostModelSwitch` olayı yoksa ya da çalışmıyorsa `model_sapmasi` SubagentStop dökümündeki
  model adından okunur (§10.3 #13, #17).
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
  `py -3.10 .claude/bin/film.py …` biçimine çevrilir. Güvenlik kancaları `timeout: 10`, `onFailure: block` (alan doğrulanacak, §10.3 #5).
  **Kapalı başarısızlık bu alana bağlı değildir** ([SON] O-11): `kanca.py`'nin en üstünde try/except vardır; her beklenmeyen hatada engelleyen
  çıkış (2) ya da JSON `deny` verir; ağır içe aktarma yapmaz, hedef süre ≤ 1 sn (zaman aşımı yalnız `onFailure` ile kapanır; bu yüzden kısa
  tutulur). **Habersizliğin yedeği:** erişim kancası güvenilmezse (Ö0-a) kör roller ana oturumdaki Agent yerine `film.py calis` içinden başsız
  `claude -p` ile koşar: çalışma klasörü `<veri>` dışında geçici bir kopyadır (yalnız `GIRDI/`), araçlar yalnız `Read,Write`, ek klasör yok, proje ve
  kullanıcı `CLAUDE.md`'si ile bellek yüklenmez (süreç düzeyinde yalıtım; abonelikle çalışması ve yüklenmeme ayarı §10.3 #19'da doğrulanır). Kanca nabzı:
  `film.py basla` son 15 sn içinde nabız görmezse ajan görevi başlamaz. Becerideki kancalar ayar kancalarının yedeğidir. En düşük Claude Code
  sürümü 2.1.302'dir (doğrulanacak; [CM2] §4.7); kurulum sürümü kaydeder, nabız sürümü taşır, sürüm değişince SessionStart `test_kancalar.py`'yi
  çalıştırır. Otomatik güncelleme kapatılmaz (güvenlik düzeltmeleri gelsin diye); değişen sürüm testten geçmeden sürüş açılmaz.
- **D-12 · Üretim yerelde, bulut geliştirmede; iki kök kalır.** Film üretimi baştan sona kullanıcının Windows bilgisayarında yürür; bulut oturumu
  yalnız geliştirme ve `sahte`/`kaset` testleri içindir. Neden: bulutta proje iş parçacığında depo kancaları uygulanmayabilir ([CM2] R-12), git
  eşitlemesi teknik bilgisi az kullanıcıya iş yükler ([UM2] R8, [SA] O-4). `film.py esitle` P2'ye alınır. **İki kök kalır:** depo
  `Desktop\YZ_FILM_SET` (Claude Code burada açılır, `FILM_SETI.bat`), veri `Desktop\YZ_FILM` yerinde (kullanıcının dosyaları ve yolları bozulmaz;
  CLAUDE.md kuralı). Tek kök önerisi reddedildi: kullanıcının veri klasörünü git deposuna çevirmek anahtar ve medya sızıntısı riskini büyütür.
  Yanlış klasörde açılma riski veri kökündeki 5 satırlık yönlendirme `CLAUDE.md`'siyle ve SessionStart denetimiyle kapatılır ([CM2] §4.4.7).
  Kurulum yalnız `git clone` iledir (ZIP'te `.git` yoktur; §8.2). Kullanıcının tek git işi `GUNCELLE.bat`'tır (`git pull --ff-only`); yerel değişiklik
  ya da izlenmeyen bir çakışma görürse hiçbir şeyi taşımadan durur ve tek cümle bilgi verir. Yerel geliştirme oturumunun ürettiği dosyalar
  (memmet3 aktarımı, `B3_44.json`) depoya yerelde commit'lenmez: `<veri>/GELISTIRME/`'de hazırlanır ve `film.py esitle --gelistirme` (dar hâl, P0)
  ile ayrı bir dala gider, birleştirme bulutta PR ile olur ([SON] O-5). Bulut davranışı D-45'tedir.

**Film zanaatı**
- **D-13 · Atomik eylem zinciri (KK2) — [YN2] şeması aynen.** Adım `{id a1.., bas, bit, ozne, tur fiziksel|mikro|konusma|ses_vurusu, fiil,
  govde, yon, hedef, olcu, el_sekli, hiz, etki{}}`; fiil yalnız `veri/fiil_sozlugu.json`'dan; sonuç fiilleri (RE `yasak_sonuc_fiilleri`: take,
  grab, pick up, get, use, fix, prepare, fight, search; açılışı tarif edilmedikçe open) ve iç durum fiilleri (realizes, decides, remembers, knows)
  HATA; klip başına 2–3 adım (konuşmalı planda ≤ 1 fiziksel adım ve konuşmadan ≥ 0,2 sn önce biter); ilk adım ≥ 0,5 sn'de başlar, son adım
  `klip_sn − 1,0`'da biter; sağ/sol daima **karakterin kendi** sağı/solu; eller `{sag, sol: {tutar, yer, sekil}}`, açık parmak sayısı `sekil`'den
  türetilir (kıskaç = 2); başlangıç durumu = başlangıç karesi, bitiş durumu = sonraki klibin başlangıcı (dünya defteri denetler). Durum yalnız olgu
  taşır; kadraj konumu, sırası, bakışın kadraja düşüşü, ışık yönü ve ekran yönü `kroki.py` ile `_derlenir`'e hesaplanır ([YN2] öz 1). İstem biçimi
  `aralik` ("0.5-3s: …") varsayılandır; Ö0-b `sira` biçimi V3 tutmada ≥ 10 yüzde puanı üstün çıkarsa (tahmin) `sira`'ya geçilir. Ö0-b'nin bütün
  A/B'leri ön karardır: kol başına 12 klip (tahmin) tutmazsa "ölçülemedi → varsayılan" olur ve A14a hepsini yeniden doğrular ([SON] O-3). ZN §3.7'deki
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
  çıkarılıp Ö0-b'ye (B3 planları) taşındı. Kesit 3 Claude seyircisinden ve (ücretsiz anahtar varsa) `izleyici` ile `dinleyici`'den geçer ve kullanıcıya **bilgi** olarak gönderilir;
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
  **bulgu kaynağıdır, onay kaynağı değildir**; ilk filmlerde BAYRAK verir, medyana girmez. **Açılma kuralı** ([SON] K-3): ücretsiz Gemini API
  anahtarı kurulumda alınır (§8.2; fiziksel iş, soru değil); anahtar `<veri>/AYARLAR/` içinde varsa ve çağrının maliyeti 0 ise (`gemini_katman:
  ucretsiz`, Ö0-e doğrular) `izleyici` ve `dinleyici` **açıktır**; `izinler.gemini_api_ucretli` yalnız ücretli kullanımı yönetir (`usd_tavan_film > 0`
  ile birlikte). Ücretsiz katmanın veri kullanım koşulu (Google'ın girdileri ürün geliştirmede kullanabilmesi; bellekten, doğrulanacak)
  `LISANSLAR.json`'a ve gizlilik notuna yazılır ve kullanıcıya kurulumda bir kez bilgi olarak verilir. Kota dolarsa dikey kesit ve son kurgu turu
  için bir kez kotanın yenilenmesi beklenir (8 BEKLE, ≤ 24 sa; tahmin); öbür çağrılar "ölçülemedi" olur. Anahtar yoksa ya da ücretsiz katman video
  ve ses girişini kabul etmiyorsa "ölçülemedi" (= BAYRAK) yazılır; bu, `FILM_SONU_RAPORU.md`'de ve yayın paketinde açık eksik olarak görünür ve
  aynı malzeme kullanıcıya **izle-dinle bilgi paketi** olarak gider (D-24). Görsel "ikinci göz" de yalnız API ile yapılır; kullanıcıya ek paket olarak verilmez ([GS2] İ-6'nın kullanıcı
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
- **D-23 · Çoklu çekim (take) ölçüyle açılır.** Dikey kesitte duygu yükü yüksek ≈ 10 plan (tahmin) iki kez çekilir; seçim kör ifade okuması, V1/V2 ve varsa
  `izleyici`'nin ikili karşılaştırmasıyla yapılır. İkinci çekim ≥ %30 durumda açık farkla seçilirse (tahmin) take, `oyunculuk_kritik` kümesinde açılır:
  `duygu_tutma` planları (RE `duygu_tutma_film_max` 25), vuruş noktalarındaki konuşmalı yakın planlar, ilk 120 sn'nin konuşmalı yakın planları,
  doruk yakın planları ve vitrin anları; film başına en çok 60 plan (tahmin). BUT0/BUT1 bu 60 × 12 = 720 krediyi (hesap) **take payı** olarak ayırır;
  take açılmazsa pay kapı payına döner. Take gönderimleri D-04'ün tempo ve kapasite kurallarından geçer.
- **D-24 · Gerçek seyirciyle bağ** ([ESY] EK3). Ö0-g kanal teşhisi (B1/B2: gösterim, tıklama oranı, ortalama izleme, tutma eğrisi, trafik kaynağı)
  ilk filmi beklemez, ama bulguları kapak/başlık ve ritim önceliklerini belirler. Varsayılan veri yolu YouTube Studio'dan **tek seferlik CSV dışa
  aktarımıdır** (adımları `BASLA_BURADAN.txt`'de; dosya `<veri>/GELENLER/KANAL/`'a; isteğe bağlı fiziksel iş, soru değil). Salt okuma OAuth bağlantısı
  (`YOUTUBE_BAGLA.bat`; kullanıcının kendi Google Cloud projesini ve OAuth istemcisini gerektirebilir, bellekten, doğrulanacak) teknik bilgisi az
  kullanıcı için ağır olduğundan P2'dir ([SON] S-10). Veri gelmezse sonuç "ölçülemedi"dir. `yayin_analiz.py` yayından 48 saat,
  7 gün ve 28 gün sonra tutma eğrisini `KURGU_PLANI` çizelgesine eşler ve düşüş noktalarını plan kimliğiyle ders defterine `kaynak: gercek_seyirci`
  olarak yazar; bu kaynak defterdeki en yüksek kanıt ağırlığını alır. 48 saatte tıklama oranı ya da ilk 30 sn tutması kanal ortalamasının altındaysa
  kapak/başlık değişikliği önerisi bilgi olarak yazılır; değişiklik kullanıcının işidir. Animatik ve dikey kesitten sonra 3–5 dk'lık izle-dinle bilgi
  paketi (kesit, ses kadrosu örnekleri, ana tema; `dinleyici` yoksa Ö0-c motor örnekleri ve ölçülemeyen müzik ipuçları da) `kurgu_render
  --bilgi-paketi` ile kurulur ve Telegram'a ya da masaüstüne gider; kullanıcı susarsa hat beklemez, itiraz ederse `film-not`.
- **D-25 · Müzik: kaynak merdiveni ve kalite kapısı** ([ESY] EK4, [SM2] §4.8.4). Leitmotif ajanın yazdığı özgün notalardır (MIDI; kroma şablonuyla
  ölçülür). Yayın zinciri ([SON] O-14): `acestep` (ACE-Step 1.5, yerel; "Cover/Refer audio" ile motifin çalınmış hâli girdi; 4 GB kartta süresi
  Ö0-c'de ölçülür, kabul edilemezse zincirden düşer) → `kutuphane` (lisansı kayıtlı parçalar: KUR1 kurulumunda gelen **çekirdek set**: geliştirme
  oturumunda seçilmiş, lisansı `LISANSLAR.json`'a yazılmış ≈ 10–15 CC0 parça (tahmin); sabit adres ve SHA-1 ile model ağırlıkları gibi bir kurulum
  indirmesidir, film başına indirme değildir; ayrıca kullanıcının isteğe bağlı YouTube Ses Kitaplığı indirmesi) → `elevenlabs_muzik` (yalnız
  koşulları okunup `LISANSLAR.json`'a "ticari YouTube: evet" yazılınca; P2) → `gemini_muzik_paketi` (zincirin **son** basamağı; elle, fiziksel iş:
  kullanıcı istem listesini Gemini'ye verir, gelen dosyaları GELENLER'e koyar; B2'de çalışan tek gerçek müzik kaynağıydı, H/uretim-hatti-v2; yalnız
  Gemini müzik koşulları `LISANSLAR.json`'da "ticari YouTube: evet" olunca açılır; sayısı sözleşme kartında yazılır) → `midi_ornek` **yalnız
  animatikte ve motif omurgası olarak**; yayında tema ipucu General MIDI örnekleriyle çalınmaz. **Zincir boşsa** ya da bir ipucunun bütün adayları
  kalite kapısından kalırsa o ipucu müziksiz kalır: S6 HATA değil BAYRAK'tır, açık eksik raporuna ve izle-dinle bilgisine girer; hat durmaz. Müzik
  kalite kapısı: her ipucunun adayları `dinleyici` ile ikili karşılaştırılır ("hangisi sinema filmi müziğine benziyor?") ve yerelde spektral genişlik,
  dinamik aralık, stereo genişlik, artefakt ölçülür; ilk filmde BAYRAK. `dinleyici` yoksa kapı **ÖLÇÜLEMEDİ** (= BAYRAK) yazar; bu,
  `FILM_SONU_RAPORU.md`'de ve yayın paketinde açık eksik olarak görünür ([SON] K-3). Gemini'deki elle müzik yolu yalnız lisans gerekçesiyle koşula
  bağlıdır; KK1 fiziksel işi yasaklamaz. Lyria/Gemini ambiyans için hiç kullanılmaz (BK §5.1.2). Her seçilen dosyanın kaynak kaydı tutulur (model,
  sürüm, lisans, istem, tohum, motif, SHA-1) ve Content ID itirazının kanıtıdır.
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
- **D-28 · Yaratık ve parmak ölçüleri H'ye yükselebilir** ([ESY] EO5, [SA] O-6a-b). Yaratık kartı ≥ 3 sabit asimetrik işaret (tahmin; [ESY] EO5
  önerisi; ör. sol kaşta beyaz leke, sağ boynuzun kırık ucu) + Lab renk paleti + baş/gövde oranı taşır; kör sorular bu işaretleri görüntü koordinatında sorar; kart görünümlerinden
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
  gizli bilgi, silme yasağı, onay kuralları) öğrenmeyle gevşetilemez. Defter veri kökündedir ve git deposu değildir; kalıcılığı A18'deki
  `ders_defteri --yedekle` (D'ye kopya) ve A00'daki sha1 doğrulamasıyla sağlanır (D-42).
- **D-34 · Eşik dosyalarında kaynak zorunlu; güvenlik sayıları tek yerde.** Her eşik anahtarı `{deger, aciklama, kaynak: olcum|belge|tahmin, etiket,
  gevsetilemez?}` taşır; `esikler.py` kaynaksız anahtarı "tahmin" diye raporlar; aynı anahtar iki eşik dosyasında HATA'dır. RE'nin bugünkü 148
  anahtarının hiçbirinde kaynak yok ([SA] K-5 #3); geçiş PR-1'de yapılır. Belgelerde "[kaynak: RE]" yazımı tek başına kaynak sayılmaz.
  **Sayısal güvenlik sınırları** (Flow temposu ve tavanları, uyarı ve hesap kilidi günleri, disk tabanı, kapı ve take payı, güvenlik payı, model,
  en düşük çözünürlük, paralel ajan tavanı) yalnız `hat_esikleri.json`'da `gevsetilemez: true` ile durur. `FILM_AYAR.json` eşik dosyası değildir;
  yalnız izin, tercih ve para tavanı taşır. Kullanıcı ya da bir araç `FILM_AYAR`'a bir güvenlik sınırı yazarsa `esikler.py` `min(eşik, ayar)`
  uygular (yalnız sıkılaştırır) ve farkı `_RAPOR/ESIK_AYAR.json`'a BAYRAK olarak yazar ([SON] O-10).
- **D-35 · Adlar tek dosyada.** `YZ_FILM/ARACLAR/veri/ADLAR.json` klasör, ajan, kip, kapı, plan alanı, sağlayıcı türü ve `.bat` adlarının tek
  listesidir; `test_adlar.py` kodda, becerilerde ve ajanlara dilimi verilen belgelerde (ZN, AR2; "tarihsel" notlu bölümler hariç) geçen her adın
  burada olduğunu denetler ([SA] O-1, [SON] O-8). İçeriği §2.4 ve §5'tir. **Ad çakışmalarını önleyen önekler** ([SON] S-4): kurulum kademesi
  `KUR1–KUR3`, kamera kurulumu `KAM1…`, bütçe noktası `BUT0–BUT2` ve `BUTK` (her kredili madde); `K0`, `K1`, `K1ON` yalnız süreklilik kapısıdır;
  `KK1–KK6` kesin kararlardır; `BK` yalnız `BILGI_KURALLARI.md`'dir; B1–B3 bölüm (PROJE) adıdır. Sahne kimlikleri en az iki hanelidir (`S01`…),
  ses kapıları tek hanelidir (`S0`…`S8`, alt madde `S2.16`); `test_adlar` bu biçimi zorlar. Uzman belgelerindeki eski adlar (`K1–K3` kademe,
  `B0–B2/BK` bütçe, kurulum `K<n>`) bu adlara eşlenir.
- **D-36 · Lisans defteri.** `YZ_FILM/ARACLAR/veri/LISANSLAR.json`: her bileşen için sürüm, kod lisansı, ağırlık lisansı, kaynak bağlantısı, doğrulama
  tarihi, "ticari YouTube: evet / hayır / bilinmiyor" ve **geçişli bağımlılıklar** (ör. OpenVoice V2'nin bağımlılık listesinde AGPL'li
  `whisper-timestamped` bulunabilir; bellekten, doğrulanacak; AR3 A4 "kullanılmasın"). `kurulum.py` "bilinmiyor" olan bileşeni ana hatta kurmaz,
  yalnız `--deneme` kipinde kurar. Kullanıcının hâlihazırda kullandığı hizmetler (Flow, AI84) `kullanici_hizmeti: true`, yerel araçları
  (`pycapcut`, `kurgu_koprusu`, `demucs`) `kullanici_araci: true` ile işaretlenir; bunlar doğrulama sürerken kullanılmaya devam eder ve lisansları
  P0'da doğrulanır ([SON] S-9; yoksa ana teslim olan CapCut taslağı kurulamazdı). AGPL'li bir geçişli paket çıkarsa o kod yolu kapatılır ya da
  ayrı ortamda yalnız yerel çalıştırma olarak not edilir (dağıtılmaz). AI84'ün aracı (kriptoyla alınmış) olmasından doğan risk §10'da yazılıdır.
  Yayın paketine kaynak künyesi eklenir ([SA] O-5).
- **D-37 · Kademeli kurulum, ana ortamda CPU torch** ([SA] O-3). KUR1: kâğıt + Flow + G1 ölçümleri (ana Python 3.10; `torch` CPU; DINOv2-small,
  OWLv2-base, CLIP, YuNet, SFace, MediaPipe tek sürüm; `midi_ornek` için FluidSynth ikilisi + lisansı kayıtlı SF2 dosyası; müzik çekirdek seti,
  D-25). KUR2: yalnız Ö0-c'de kazanan ses dönüştürme motoru (tek ayrı ortam). KUR3: MuseTalk, ACE-Step,
  büyütücü (ayrı ortamlar, CUDA), yalnız gerektiğinde. Her kademe "çalışıyor / çalışmıyor" kartı yazar; eksik kademe yalnız kendi basamağını kapatır.
  Model ve pip önbellekleri C'de tek klasörde (`YOLLAR.json`) toplanır, boyutları raporda gösterilir; D harici diski çalışırken kullanılmaz
  (BK §8 #21); önbellek temizliği kullanıcının işidir (Claude kalıcı silemez).
- **D-38 · Disk kapısı ve kendiliğinden arşiv** ([SA] O-11, [SON] O-7). `film.py` her aşama başında `shutil.disk_usage` ile boş yeri ölçer.
  `arsivle.py` **P1**'dir (ilk filmde var): A16 ve A17 sonunda ve `disk_bos_min_gb` (20, tahmin) altına düşülünce Claude onu kendisi başlatır
  (BK §7 #10: iş bitince ara klasörler kullanıcıya sormadan D'ye taşınır). Taşınanlar: yeniden üretilebilir ara dosyalar (render önbelleği, eski
  1080p türevleri), `surumler/`'in son iki sürümü dışındakiler, eski animatik render'ları, videosu GEÇ olan planların seçilmeyen adayları; yöntem
  `robocopy /E /MOVE` (`/MIR` yasak). Son taslağın bağlı olduğu yollar (`draft_content.json` path'leri), açık kuyruk maddelerinin girdileri ve
  dışa aktarılmamış iş taşınmaz (testli). Taşınanların listesi kullanıcıya bilgi olarak verilir. D takılı değilse 8 BEKLE + tek fiziksel iş
  "D'yi tak"; `film.py bekle --kullanici` diski yoklar ve takılınca sürer. Hacim büyüktür (her plana 2 aday ≈ 1.200 görsel, ≈ 405 klip ve yeniden
  çekimler, 2× büyütme, 4K dışa aktarım; R17). `ARSIVLE.bat` yalnız kullanıcı isterse elle çalıştırma içindir.
- **D-39 · Oturum hazırlığı ve gece** ([SA] O-12, [UM2] uygunluk kuyruğu). Bir Flow oturumuna girecek blokların bütün ön koşulları (G1 GEÇ kareler,
  derlenmiş istemler, BUTK onayı) oturumdan önce hazırdır; zincir ardılları sonraki bloğa planlanır ve V3 kör gözlemi bloklar arasında yapılır. Blok
  sonunu arka planda koşan `film.py bekle --blok` algılar ve bitince oturumu uyandırır (§4.2 adım 5; Ö0-a #16 tutmazsa kullanıcı "tamam" yazar,
  §8.1). Gece kipi Memmet'in kullanıcıya ait özelliğidir; varsayılan kapalıdır, yalnız `IZINLER.bat` ile açılır (`izinler.gece_flow`), aynı ya da daha yavaş tempoyla çalışır, gece başına
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
  `ag`, `kota`'da olur; `olagandisi`, `dogrulama` ve kodu bilinmeyen `Kisitlandi` **hiçbir zaman** başka sağlayıcıya geçirmez (D-02, D-03; kapalı
  başarısız). Flow kilitliyken Vertex'e geçiş de otomatik değildir: yalnız `izinler.flow_kilitliyken_vertex` + `usd_tavan_film > 0` ile ve
  `blok_plani`'nın kalan planlara planlı sağlayıcı yazmasıyla olur (D-03, [SON] O-15). `elle = True` sağlayıcı (kullanıcı işi gerektiren) yalnız
  zincirin **son** basamağı olabilir ve sayısı sözleşme kartında yazılır (ör. `gemini_muzik_paketi`, D-25). `sahte`, `kaset` ve `sahte_bozuk` yalnız
  test kipinde (`--saglayici sahte` ya da `ORNEK_*` filmleri) çalışır; gerçek bir filmin zincirinde bulunurlarsa `film.py` HATA verir.
- **D-42 · Seri evreni sahip başına dosya** ([GS2] İ-11, [SN2], [SM2] İ-8). `<evren>/` yalnız `evren.py` ile yazılır; karakter, mekân, nesne, müzik
  kayıtları sahip uzmanın dosyasıdır (`karakter.json` görüntü, `hikaye.json` senarist, `ses.json` ses, `kroki.json` yönetmen). Kanon yalnız eklenir;
  sürümler silinmez. **Kalıcılık ve yedek** ([SON] O-6): `<evren>` veri kökündedir ve git deposu değildir (D-12); depoda yalnız test fikstürü
  evrenleri durur. A18'de `evren.py --yedekle` ve `ders_defteri --yedekle` evreni (kartlar, sesler, `.npz` bankaları, krokiler, leitmotifler) ve
  `<veri>/BILGI/DERSLER/`'i `robocopy /E` ile (kopya; `/MIR` yasak) `D:\YZ_FILM_YEDEK\EVREN\<SERI>\` ve `D:\YZ_FILM_YEDEK\DERSLER\` altına kopyalar
  ve sha1 listesini yazar; AYARLAR yedeğe girmez. D takılı değilse BEKLE yerine bilgi verilir ve yedek sonraki filmin A00'ında yeniden denenir.
  A00'da yedeğin sha1 listesi `evren.py --yedek-dogrula` ile karşılaştırılır; fark bilgi olarak yazılır ve yedek yenilenir.
- **D-43 · Dünya durumu defteri makinenindir** ([GS2] sahip, [YN2] §4.5.13 çözüm kuralları). `dunya_defteri.py` planların `baslangic_durumu`
  ve `eylem_zinciri.etki` alanlarından `DUNYA_DEFTERI.json`'u derler; olay çıkarır (bitiş − başlangıç → olay; her olayın etkili adımı ya da zaman
  atlaması kartı olmalı); görsel üretildiği anda planın durumunu dondurur (`uretim.durum_dondu`); kurgu sırası değişince yeni komşuları dondurulmuş
  durumla denetler (Y58). Elle düzenlenmez; makine sahipli dosyaların sha1'i saklanır, uyuşmazlık HATA'dır.
- **D-44 · Plan seyircisi ve ön turlar değeriyle kalır.** A07e (plan seyircisi), KR3a (P1 animatik ön turu) ve KR8a (P1 kurgu ön turu) ilk iki
  filmde koşar; tek başına yakaladığı ve sonraki partilerde önlenen bulgu sayısı ders defterine yazılır; iki filmde değer yoksa karar defterine
  gerekçeyle kaldırılır ([YN2] açık soru 8, [KU2] açık soru 11).
- **D-45 · Bulutta açılış: konu sorulmaz, film başlatılmaz (görev gerçekliğinden bilinçli sapma)** ([SON] O-13). Görev metni "bulut oturumunda yalnız
  kâğıt aşamaları ve `sahte` sağlayıcı çalışır" diyor; [UM2] §2.7 de kâğıdı bulutta önermişti. Bu tasarım bulutta kâğıt aşamalarını da
  çalıştırmaz. Neden: (1) bulut proje iş parçacığında depo kancaları uygulanmayabilir ([CM2] R-12; §10.3 #20'de ölçülür) ve habersizlik, soru
  kapısı, AYARLAR yasağı kancaya bağlıdır; (2) kâğıt çıktıları kullanıcının bilgisayarına git eşitlemesiyle taşınmalıdır ve bu teknik bilgisi az
  kullanıcıya iş yükler ([UM2] R8, [SA] O-4; `esitle` P2); (3) bulutta konu sorulup A00'da 4 ORTAM'la durmak kullanıcıya boş bir soru sormak
  olur (KK1). Davranış: SessionStart `ortam=bulut` görürse ve aktif film yoksa konu sorulmaz; kullanıcı konu verse de tek bilgi cümlesi söylenir:
  "Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz." Bulutta `film-yap` yalnız
  `--saglayici sahte` ile `ORNEK_*` denemesini koşturur (geliştirme ve gösterim içindir); geliştirme `/film-gelistir` ile sürer. Yeniden açma
  koşulu: `esitle` yazılır ve §10.3 #20 bulutta kancaların uygulandığını gösterirse kâğıt aşamaları bulutta da koşabilir (karar defterine yazılarak).

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
   tahmin); "TTS + süreye sığdırma" kıyasa çıta olarak girer. Bu ölçülerin hiçbiri fısıltı ve bağırmadaki metalik sesi görmez ([SM2] R3, AR3 A2);
   bu yüzden kıyasa **doğallık ölçüsü** girer ([SON] K-3): lisansı doğrulanmış bir MOS tahmincisi ve/veya `dinleyici`'nin kör ikili
   karşılaştırması; kıyas setinde fısıltı ve bağırma replikleri zorunludur. İkisi de yoksa seçim "ölçülemedi" BAYRAK'ıyla karar defterine yazılır
   ve motor örnekleri izle-dinle paketine konur. Seri başında `ses_kiyas.py` (SB3) aynı kıyası yapar; ilk filmin ilk 20 repliğinde yeniden
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

**Kalan sınırlar:** Claude sesi duyamaz; her ses yargısı ölçümle (WER, gömme benzerliği, F0, LUFS, dudak ofseti, doğallık) ya da `dinleyici` ile
verilir (D-19). Ücretsiz Gemini anahtarı kurulumun olağan işi olduğu için `dinleyici` varsayılan yolda **açıktır**; anahtar yoksa ya da ücretsiz
katman ses girişini kabul etmiyorsa aksan tutarlılığı (S2.16), ses–yüz uyumu ve müzik kalite kapısı "ölçülemedi"dir (= BAYRAK; `FILM_SONU_RAPORU.md`
ve yayın paketinde açık eksik), ses kadrosu 30 sn'lik dinleme dosyasıyla kullanıcıya bilgi olarak gider (`SES_SECIM.html` + izle-dinle paketi);
kullanıcının itirazı `film-not` ile gelir.

### 2.3 Eleştirmenlerin KRİTİK ve ORTA maddeleri: karar tablosu
"Uygulandı" = önerinin özü tasarıma girdi; "kısmen" = bir parçası değiştirilerek ya da koşula bağlanarak girdi (neden yazılı); "uygulanmadı" =
neden yazılı.

**Seyirci-yapımcı eleştirisi ([ESY])**

| Madde | Karar | Nasıl / neden | Yer |
|---|---|---|---|
| EK1-1 İşitsel-görsel seyirci (`izleyici`) | uygulandı (son denetimle) | Sağlayıcı türü ve sözleşme girer, ilk filmlerde BAYRAK (öneriyle aynı). Ücretsiz Gemini anahtarı kurulumun fiziksel işidir (soru değil); anahtar varsa ve maliyet 0 ise varsayılan açıktır. Ücretli kullanım ve dolar izni yine kapalıdır. Anahtar yoksa ya da katman video girişini kabul etmiyorsa "ölçülemedi" açık eksik olarak raporlanır ve izle-dinle bilgi paketi gider ([SON] K-3) | D-19, D-24, §8.2 |
| EK1-2 Dikey kesit | uygulandı | Pilot dalga, dikey kesit ve GS0'ın ilk film bölümü tek aşama (A14a); ≈ 180 sn yayın kalitesinde; ek kredi yok | D-17, §1.3 |
| EK1-3 Kare paketinin göremediğini ölçen betikler | uygulandı | hareket hızı (V2), enerji eğrisi (T2), müzik tını/dinamik ölçüleri; MOS tahmincisi lisansı doğrulanınca Ö0-c'de ve sonra S2'de (P1) | D-25, D-27d, §7 |
| EK1-4 İzle-dinle bilgi paketi | uygulandı | animatik ve dikey kesitten sonra; Telegram ya da masaüstü; hat beklemez | D-24, §8 |
| EK2-1 `zanaat.oyunculuk` + ifade sözlüğü + `ifade` zorunlu | uygulandı | ≈ 16 değerli filtre-güvenli sözlük | D-22, §5.1 |
| EK2-2 Duygu sürekliliği defterde | uygulandı | `duygu {durum, siddet, izler}`; K0 BAYRAK | D-22, §5.2 |
| EK2-3 Kör ifade okuması + seçim ölçütü | uygulandı | seçim sırasının 2. ölçütü | D-22 |
| EK2-4 Çoklu çekim (60–110 plan) | kısmen | Önce dikey kesitte ölçülür; değer görülürse en çok 60 plan (tahmin) ve ayrı take payıyla açılır. Neden: Flow kapasitesi ölçülmedi ([SA] K-1); 110 planlık ek yük ölçmeden alınamaz | D-23 |
| EK2-5 Canlı bekleme | uygulandı | Y06 daraltıldı; "holds the pose, breathing" Ö0-b A/B'siyle varsayılan olur | D-13 |
| EK2-6 `teslim` 12 değer | uygulandı | 4 LUFS sınıfına eşli | D-22, §5.1 |
| EK2-7 Sözsüz ses vuruşları | uygulandı | `tur: ses_vurusu` mikro adım | D-22 |
| EK2-8 Plan eleştirmenine 2 madde | uygulandı | — | D-22, §3 |
| EK3-1 Kanal teşhisi | kısmen | Ö0-g olarak yapılır ama ilk filmi bekletmez. Neden: veri kullanıcının YouTube Studio CSV'sini ister (OAuth P2; [SON] S-10); KK1 gereği istenemez, ancak bilgi olarak önerilir. Sonuçlar kapak, başlık ve ritim önceliğini değiştirir | §1.2, D-24 |
| EK3-2 `yayin_analiz.py` | uygulandı | 48 sa / 7 gün / 28 gün; ders kaynağı `gercek_seyirci` | D-24, A18a |
| EK3-3 Kalibrasyon | uygulandı | panel ↔ gerçek tutma ilişkisi ilk üç filmde | D-19, D-24 |
| EK3-4 Erken uyarı | uygulandı | bilgi; değişiklik kullanıcının işi | D-24 |
| EK4-1 Müzik kalite kapısı | uygulandı | `dinleyici` ile ikili karşılaştırma + yerel ölçüler; ilk filmde BAYRAK; `dinleyici` yoksa ÖLÇÜLEMEDİ açık eksik olarak raporlanır | D-25 |
| EK4-2 Kaynak merdiveni | uygulandı | `midi_ornek` yayında tema çalmaz; kütüphane çekirdek seti KUR1'de; Gemini elle yolu lisansla son basamak; zincir boşsa müziksiz ipucu + BAYRAK ([SON] O-14) | D-25 |
| EK4-3 Ses–yüz uyumu | uygulandı | `dinleyici` kör sorusu + 30 sn dinleme dosyası bilgi | D-19, §2.2 |
| EK4-4 Dönüşüm doğallığı (MOS) | uygulandı (son denetimle) | Ö0-c motor kıyasına doğallık ölçüsü girer (lisansı doğrulanmış MOS tahmincisi ya da `dinleyici` kör ikili); ikisi de yoksa seçim "ölçülemedi" BAYRAK'ıyla yazılır, örnekler izle-dinle paketine konur. S2'de MOS BAYRAK'ı P1 ([SON] K-3) | §1.2, §2.2, §6.6 |
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
| K-1 Flow kapasitesi ölçülmemiş, tek hesap | uygulandı | Ö0-b merdivenli 3 gün ölçümü (ilk uyarıda kapanır, ikinci uyarıya girilmez); takvim ölçülen kapasite alt sınırından; kapasite ya da takvim yetmezse 30 dk; Vertex fiyatı Ö0'da, Flow kilitliyken Vertex yalnız ayrı izin + dolar tavanıyla; hesap değiştirme yasağı ve kodu | §1.2, D-03, D-04, D-05 |
| K-2 "Yalnız konu" iş yüküyle delinmiş | uygulandı | kullanıcı sözleşmesi kartı; tek `IZINLER.bat` (soru değil); el işi saati ölçülür ve gösterilir (sabit "≤ N saat" tavanı konmadı: N'nin kaynağı yok); Gemini API Ö0-e; DUR sonrası ekip varsayılanı; "elle dinleme" tasarımdan çıktı; kullanıcı eyleminden sonra arka plan `bekle` süreci oturumu uyandırır, tutmazsa "tamam" yazma işi sayısıyla kartta ([SON] O-4) | D-06, D-07, §4.2, §8 |
| K-3 Token bütçesi yok | uygulandı | kullanım kaydı, aşama tavanı + BEKLE, karar 6 testi, kısmi izleme ikinci filmde A/B, erken projeksiyon | D-08, D-09, D-18 |
| K-4 Temeller ölçülmeden P0 | uygulandı | Ö0-a, Ö0-1, Ö0-2 (bağımlılıkları §1.2'de); P0 listesi yerel aşamalar için Ö0'dan sonra kesinleşir | D-01, §9 |
| K-5 Kalibrasyonsuz kapılar | kısmen | (1) "gölge kip" yerine kapı 7 + olgular / hedef 8: puan tamamen gölgeye alınmadı, çünkü kullanıcının "süper" dediği düzeyin (7) altındaki film video kredisine geçmemeli; (2) seyirci güvenilirliği Ö0-f; (3) zorunlu kaynak alanı; (4) küresel geri dönüş bütçesi ve her kapıda tavan sonrası merdiveni ([SON] K-4); (5) iki yönlü kalibrasyon — uygulandı | D-20, D-33, D-34, §1.5 |
| K-6 Depodaki kod KK5'i çiğniyor | uygulandı | PR-0, memmet3'ten bağımsız; her kipte (`elle` dahil) uyarıda dur, tempo varsayılanı, kalıcı mola, kapalı başarısız `Kisitlandi`; veri kökündeki eski Memmet ve `.bat`'lar emekliye ayrılır; korkuluk testi her kipte ve CI'da zorunlu ([SON] K-1, K-2) | D-02, §9 |
| O-1 Bütünleştirici yok | uygulandı | bu belge karardır; `ADLAR.json` + `test_adlar.py` | D-35 |
| O-2 Sahipsiz işler | uygulandı | `renk_cila.py`, `shorts_mp4.py`, `jenerik.py`, kapak üretimi, YZ beyanı, memmet3 aktarımı, B3 etiketleri, torch kararı, kullanıcı belgeleri, token ölçümü, kapasite ölçümü, lisans defteri, Gemini kotası, izin kartı, `durdu` planın karşılığı — hepsinin sahibi §6'da | §6 |
| O-3 Kurulum karmaşık | uygulandı | KUR1/KUR2/KUR3 kademeleri; CPU torch | D-37 |
| O-4 Bulut/yerel | kısmen | Üretim yerelde, `esitle` P2 (yalnız geliştirme dosyaları için dar `--gelistirme` hâli P0) — uygulandı; bulutta açılış davranışı D-45. Tek kök reddedildi (veri klasörünü git deposu yapmak sızıntı riskini büyütür) | D-12, D-45 |
| O-5 Lisans zinciri | uygulandı | `LISANSLAR.json`; "bilinmiyor" ana hatta kurulmaz | D-36 |
| O-6 Karar 2/3 B düzeyinde | uygulandı | (a) H'ye yükselme yolu, (b) yaratık kimlik bankası, (c) son kare referansı A/B, (d) ilk filmde sıkılaştırıcı deneme dersleri | D-28, D-15, D-33 |
| O-7 Sesin kulağı yok | uygulandı (son denetimle) | Ücretsiz Gemini anahtarı kurulum işidir; anahtar varsa ve maliyet 0 ise `dinleyici` varsayılan açıktır (dolar izni gerekmez; KK1 çiğnenmez, soru yok). Anahtar yoksa dinleme dosyası bilgi olarak gider, itiraz `film-not` ile, ölçülemeyen her ses yargısı açık eksik raporunda | D-19, §2.2, §8.2 |
| O-8 Aynı model yazıyor ve yargılıyor | kısmen | Farklı aileden `izleyici` (BAYRAK) + personalar; panel ilk filmlerde Claude kalır; puan kapısının kalkması ilk üç filmin tutma ölçümüne bağlandı | D-18, D-19 |
| O-9 Animatik G1'den sonra | uygulandı | tur 1 düzeltmelerden önce | D-14 |
| O-10 Sayılar tutarsız | uygulandı | `olcek.py` tek araç | §1.6 |
| O-11 Disk | uygulandı | disk kapısı + kendiliğinden arşiv (`arsivle.py` P1; kullanıcının tek işi "D'yi tak") | D-38 |
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
- **ZN başlığı:** "çelişki olursa JSON geçerlidir" cümlesine eklenir: "sayıda RE, **şemada `semalar/plan_v2.json` (TASARIM §5.1)** geçerlidir"
  ([SON] O-8; RE şema taşımaz).
- **ZN §6.1:** alan tablosu TASARIM §5.1'deki alan, yer ve sahip tablosuyla (§5.1 "v1/ZN/AR2 → v2 eşleme") değiştirilir; tablonun üstüne "eski öneri;
  geçerli şema `semalar/plan_v2.json`" notu konur ([SON] O-8).
- **ZN §6.2 Z0:** #5'e "L/J taşması görünen süreden düşülür: `sure_sn ≥ formül − ses_tasma_sn`" eklenir; #14 "fiziksel adım ≥ 1,5 sn; `mikro` ve
  `ses_vurusu` adımı ≥ `eylem_adim_mikro_min_sn`" olur ([SON] S-1); #17 "kamera tarafı yönetmen yazmaz; `kroki.py` kurulum konumundan
  `_derlenir.kamera_tarafi`'na hesaplar, denetim bu değerle yapılır" olur ([SON] O-8).
- **ZN §6.2:** `RAPORLAR/<kapi>_<parti>.json` → `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json`.
- **`arastirma/02_sureklilik.md` §6.1:** başına "tarihsel öneri; geçerli şema TASARIM §5.1 (`sureklilik` alt nesnesi, `plan_olcegi`, `kamera_konumu`,
  plan içi `denetim` v2'de başka yerdedir; eşleme §5.1)" notu konur ([SON] O-8).
- **RE `eylem_adim_*` açıklamaları** yeni adım modeline göre yazılır: `eylem_adim_max` 3 = plandaki bütün adımlar (fiziksel, mikro, konuşma, ses
  vuruşu; **konuşma bir adımdır**); `eylem_adim_konusmali_max` 1 = konuşmalı plandaki fiziksel adım; `eylem_adim_min_sn` 1,5 = fiziksel adım;
  konuşma adımının süresi replik süresidir (ZN §2.3); yeni `eylem_adim_mikro_min_sn` 0,8 (tahmin) ([SON] O-8, S-1).
- **`YZ_FILM/BILGI/CLAUDE_ICIN.md` şeması:** `baslik` v2'de ekran ya da seri adıdır (YouTube başlığı yalnız `YAYIN/PAKET.json`'da); normal filmde
  `altyazi_dili: null`; `bitis_karesi`, `motor`, `*_yedek` alanlarının v2 karşılığı §5.1 eşleme tablosundadır ([SON] S-6, O-9).
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
| KK1 Yalnız konu sorulur | tek soru metni (§4.1; bulutta soru yok, bilgi cümlesi, D-45); `kanca.py stop` soru kapısı; bütün kararlar `film.py karar ekle` ile deftere; izinler varsayılan kapalı ve `IZINLER.bat`; kullanıcı sözleşmesi kartı; bilgi mesajları; `film-durum` öneri değil bilgi cümlesiyle biter; tavan sonrası merdiveni hattı soru sormadan sürdürür (§1.5); veri kökündeki film adı soran `YENI_FILM.bat` emekli | fiziksel işler kalır (§8); sayıları baştan yazılır |
| KK2 Atomik eylem zinciri | D-13; fiil sözlüğü, `plan_sema`, `plan_denetim` (Y01–Y60), `istem_derle --hareket`, V3 | saniyeli uyum Ö0-b ve dikey kesitte ölçülür |
| KK3a Animatik + habersiz seyirci | A12; D-14; `animatik: ONAYLI` imzası video girdisinde | kare paketi izlemek değildir; `izleyici` ve dikey kesit tamamlar |
| KK3b Dünya defteri + zıplama denetimi | D-43; K0, Y58, K1; duygu katmanı | — |
| KK3c Referansla yüz kontrolü | D-16; G1, G1Z, V2, K1; kimlik bankası; yaratık D-28 | yaratık ve parmak ilk filmlerde çoğunlukla BAYRAK |
| KK3d Kare zinciri | D-15; `kare_zinciri.py`, G1Z, KR5 kilidi | yalnız `devam` geçişinde son kare; diğerlerinde kamera ağacı türevi |
| KK3e Öğrenen ders defteri | D-33; olay kaydı her kapıda; `ders-editoru`; gerçek seyirci kaynağı (D-24); A18'de D'ye yedek, A00'da sha1 doğrulaması | terfi ≥ 2 film; ilk filmde yalnız sıkılaştırıcı deneme |
| KK3f Seri evreni kütüphanesi | D-42; `evren.py`; kartlar, sesler, kroki, leitmotif, kalibrasyon; A18'de `evren.py --yedekle` (D'ye kopya), A00'da sha1 doğrulaması | evren veri kökündedir, git deposu değildir; kalıcılık yalnız ekleme + D yedeğiyle (D takılı değilse sonraki filmde) |
| KK4 Ses/dudak | §2.2; `dinleyici` ücretsiz anahtarla varsayılan açık | motor Ö0-c ile, doğallık ölçüsüyle seçilir; ölçülemezse BAYRAK ve izle-dinle örneği; B planı yazılı |
| KK5 Memmet, bot tespiti, uyarıda DUR | D-02 (her kipte dur; 17.10 tempo kodda; kalıcı mola; kapalı başarısız `Kisitlandi`; veri kökü emniyeti), D-03, D-04, D-39; `elle` varsayılan; T10 her kipte; `UYARI_GECTI.bat` şartları; Ö0-b ilk uyarıda kapanır | Flow kapasitesi takvimi belirler; atlatma yoktur |
| KK6 Üstün körü iş yok | ÖLÇÜLEMEDİ GEÇ değildir; 2 aday + tam G1; tam film izleme ve dinleme (`izleyici`, `dinleyici`); ölçülmeden kısma yok (karar 6 testi); bütçe yetmezse hat bekler, kalite düşmez; tavan sonrası her kalite yolu denenir, kalan eksik açıkça raporlanır | kulak anahtar ve ücretsiz katmana bağlı (yoksa açık eksik); müzik zinciri boşsa müziksiz ipucu + BAYRAK |

## 3. Ajan kadrosu

### 3.1 Kadro ilkeleri (hepsine uygulanır)
1. **21 ajan**, üç rol ([CM2] §4.3.1): **yazar** (sahip olduğu dosyayı yazar ve revize eder) `tools: Read, Write, Edit, Glob, Grep` · **denetçi**
   (içerik üretmez, kör değildir) `tools: Read, Write, Glob, Grep` · **kör** (her turda yeni örnek, yalnız GIRDI) `tools: Read, Write` +
   `omitClaudeMd: true`. Hiçbir ajanda `Bash`, `Agent`, web aracı ve `memory:` alanı yoktur. **İstisna:** `ders-editoru` ve `memmet-bakimci`
   yazar rolündedir ama yalnız **yeni dosya** yazar (aday kural, aday yama); bu yüzden `Edit` araçları yoktur (en az yetki; [SON] S-4).
2. Hepsi `model: opus` (claude-opus-5-5), `effort: high`, `permissionMode: acceptEdits`. `fallbackModel` yazılmaz. Daha ucuz yapılandırma yalnız
   karar 6 testiyle (D-09). `maxTurns`: yazar 100 (yönetmen, hikâye yazarı, kurgucu 80), denetçi 60, kör 60, `kare-tarifcisi` 40 (hepsi tahmin).
3. **Açıklama kalıbı:** "<Rol>. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kipler: …". Claude ajanı kendiliğinden
   seçmez; `kanca.py ajan` kadro dışı tipi, fork'u ve yerleşik ajanları reddeder. 21 açıklamanın toplamı ≤ 3.000 token (hedef, tahmin; [CM2] M9;
   belgenin uyarı eşiği 15.000) (`beceri_denetim.py`).
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
  GIRDI/BUT0.json'daki üst sınırın üstünde öneremezsin. Hikâye yazmazsın."
- **Görev sınırı:** seri tespiti (devam/yeni; eski seri ancak adıyla anılırsa), tür ve kanca ailesi, vaat imgesi taslağı, risk taraması (çocuk kahraman
  → yetişkin ya da dolaylı; şiddet; telif; Flow'da zayıf işler), süre önerisi, eksenler (yeni seri D/S/E + X; devam A/B/S + X), "sen seç" kipinde 3 konu
  adayı × 4 ölçüt. **Doktor:** tur tıkanınca yapısal teşhis ve D-21 şartlarıyla KRİTİK reddi.
- **Okur (GIRDI):** `00_KONU.md`, evren özeti, `KANAL_TESHIS.md` özeti, `BUT0.json`, tür–kanca tablosu (`veri/tur_kanca.json`; BK §2'den), `DERSLER.md`; doktor kipinde tur raporları,
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
- **Okur:** sözleşme, kroki PNG + kurulumlar + `yasak_ardisik`, EKRAN metni + replik kimlikleri + `teslim`, önceki sahnenin sözleşmedeki
  `cikis_durumu` (yalnız aynı mekân ve zamandaki ardışık sahnede önceki sahnenin son 2 planının çözülmüş bitişi; `dilim.py` seçer), `PLAN_DILI.md`, `plan_sozlukleri.json`, `fiil_sozlugu.json`, `ifade_sozlugu.json`, `DERSLER.md`; onarımda ilgili rapor ve kareler.
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
- **Okur:** kadro: karakter kartları (`ses_karakteri`, `ad_telaffuz`), aksan sözlüğü (`veri/aksan_sozlugu.json`; `ses_sec --ara` üretir), ölçüm tablosu; tasarım: `ses_plani` taslağı, sahne grubunun
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
  dilimi, olay listesi, ZN §2–§5 dilimi, `URETIM_ONIZLEME` dilimleri, `MERDIVEN.md` (`kuyruk.py --merdiven-md`: 0 kredi merdiveni + maddeye özel
  basamaklar), `DERSLER.md`; not kipinde `NOTLARIM.json`, `TASLAK_FARK.json`.
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
  uyarı ve doğrulama kelime listelerini daraltamazsın; yeniden deneme ya da sayfa yenileme ekleyemezsin; hiçbir kipte uyarıdan sonra işlem
  ekleyemezsin; fare/klavye taklidi ekleyemezsin; reCAPTCHA'ya dokunamazsın. Yamayı
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
description: Hat denetçisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kesin bütçe noktasında (BUT2), pilottan sonra, kuyruk 30 klibi aşınca ve dilim aktarımında betik kapılarının göremediği riskleri arar ve GİT ya da GİTME der.
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
**Bulutta** (SessionStart `ortam=bulut`, aktif film yok; D-45) soru sorulmaz; kullanıcı konu verse de yalnız şu bilgi cümlesi söylenir: "Film seti
senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz."

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
3. Flow "olağan dışı etkinlik" / doğrulama → hat her kipte durur. Yeniden başlatma, sayfa yenileme, atlatma, tempo hızlandırma,
   fare/klavye taklidi, BAŞKA HESAPLA DEVAM YOK. Kilidi yalnız kullanıcı kaldırır (UYARI_GECTI.bat).
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
5. tur=kullanici_eylemi → mesajı aynen ilet; python .claude/bin/film.py bekle --kullanici <id>'yi ARKA PLANDA başlat; turu bitir.
   (bekle beklenen eseri yoklar: GELENLER'de ZIP, KUNYE'de blok sonu, CapCut kapandı, Flow bakiyesi, D takıldı; 6 saatte bir hatırlatır;
   eser gelince çıkar ve bitişi oturumu uyandırır. "Hâlâ bekleniyor" diye çıkarsa yeniden başlat.)
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

**Kullanıcı eyleminden sonra devam** ([SON] O-4): "kendiliğinden algılanır" denen her yer (Gemini ZIP'i, video bloğunun sonu, CapCut'ın
kapanması, kredi yüklenmesi, D diskinin takılması, dışa aktarılan yayın dosyası) arka planda koşan `film.py bekle --kullanici <id>` ya da
`--blok <B>` sürecidir; bitişi oturumu uyandırır ve döngü 1. adımdan sürer. Arka plan işinin en uzun süresi ve bitişinin ana tur bitmişken oturumu
uyandırıp uyandırmadığı Ö0-a'da ölçülür (§10.3 #16); süre sınırı varsa `bekle` sınırdan önce (≈ 110 dk, tahmin) "hâlâ bekleniyor" koduyla çıkar ve
yeniden başlatılır (küçük token maliyeti projeksiyona girer). Uyandırma tutmazsa sözleşme kartına "her işten sonra sohbete 'tamam' yaz" satırı ve
sayısı (≈ paket + blok + CapCut işi) eklenir (§8.1).

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
  Soru = yalnız cevap kuralı (kullanıcı kesin istedi). Cevaptan sonra en çok bir bilgi cümlesi: "Ekip sıradaki adımda şunu
  yapacak: …; itiraz edersen yaz." (öneri ya da onay sorusu değil; KK1). Kullanıcı "bak" derse (ör. "CapCut'a bak") pencere
  görüntüsü film.py goster pencere ile alınır. Kullanıcı bir değişiklik ya da devam isterse film-yap'a dönülür.
disallowed-tools: Write, Edit, NotebookEdit, Agent
allowed-tools: Bash(python .claude/bin/film.py ozet*), Bash(python .claude/bin/film.py goster*), Bash(python .claude/bin/film.py surus kapat --soru*)
---
```
**Adımlar** (≤ 60 satır): (1) `` !`python .claude/bin/film.py surus kapat --soru || true` `` (otomatik sürüş yalnız bu tur kapanır; Stop kancası
sürmeye zorlamaz); (2) soruya göre `film.py ozet --uzun` · `goster plan 042` · `goster maliyet` · `goster neden-durdu` · `goster token` ·
`goster ayar` (maskeli) · `goster sozlesme` (kullanıcı sözleşmesi kartı) · `goster pencere capcut` (BK §7 #9 "bak" alışkanlığı: salt okunur
PrintWindow görüntüsü, fare ya da klavye yok; [SON] S-7); (3) cevap düz Türkçe, ≤ 6 satır, sayı varsa kaynağıyla; son satır en çok bir **bilgi**
cümlesi ("Ekip şunu yapacak: …; itiraz edersen yaz"); işlem yok. **Referans:** `KULLANICI_DILI.md`. **Betikler:** `film.py ozet`, `goster`,
`surus kapat --soru`.

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
allowed-tools: Bash(python .claude/bin/film.py notlar*), Bash(python .claude/bin/film.py karar ekle*), Bash(python .claude/bin/film.py ders ekle*), Bash(python .claude/bin/film.py goster pencere*), Bash(python .claude/bin/film.py bekle*)
---
```
**Adımlar** (≤ 120 satır): (1) `film.py notlar oku` → `notlari_oku.py` + `taslak_fark.py` salt okunur (CapCut açıksa kullanıcı eylemi "CapCut'ı
kapat"; kapanışı arka planda `film.py bekle --kullanici` yoklar, §4.2); (2) her not sınıflanır: (a) kullanıcının kendi kurgu kararı → aynen ve kilitli `KURGU_PLANI`'na;
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
argument-hint: "[değişiklik | ilk-kurulum | olcum0-a | memmet3-aktar]"
---
```
**Adımlar** (≤ 150 satır): (1) `film.py surus kapat --gelistirme` (sürüşe bağlı yasaklar kalkar; anahtar okuma ve `robocopy /MIR` yasakları
kalır); (2) `YZ_FILM/ARACLAR/CLAUDE.md`'yi oku; (3) değişiklik; (4) `python -m unittest discover -s YZ_FILM/ARACLAR/testler`; (5) `film.py
beceri-denetim`; (6) küçük commit (kullanıcı ya da görev istediyse); yerelde açılan oturumda commit ana dala değil, yalnız `esitle --gelistirme`
dalına gider (D-12). **`ilk-kurulum`** (ilk yerel oturumun sırası; beceri gelmeden önceki ilk oturumda aynı sıra `YZ_FILM/ARACLAR/CLAUDE.md`
§İlk yerel oturum'dan uygulanır, §8.2 adım 0b): `kurulum.py --yollar` (`YOLLAR.json`) → `kurulum.py --veri-emniyet` (D-02; taşınanların listesi
bilgi) → `memmet3-aktar` → `olcum0-a`. **`olcum0-a`:** `olcum0/kanca_deneme/` kancalarını geçici `settings.local.json` ile kurar, §10.3'teki 20
davranışı tek tek sınar, `O0a.json`'u yazar, geçici ayarı geri alır. **`memmet3-aktar`:** kullanıcının yerel memmet3 dosyasını (veri kökü emniyeti
onu `_ESKI/`'ye taşıdıysa oradan) `<veri>/GELISTIRME/memmet3/` altına kopyalar; PR-0'ın bütün maddelerini (D-02 a–g: her kipte uyarıda dur, `elle`
kipindeki "sayfayı yenile, devam" yolunun ve gece kipindeki 5 yenileme denemesinin silinmesi, 17.10 tempo varsayılanı, `FLOW_TEMPO.json` molası,
çıkış kodları, reCAPTCHA'da dur, `_surum` reddi) uygular, yollarını `ortak.yollar()`'a bağlar (Chrome profili ve `MEMMET_AYAR.json`
`<veri>/AYARLAR/`'dan), T10'u her kip için (`elle`, `gece`, `dogrulama`) koşar, anahtar taraması yapar ve `film.py esitle --gelistirme` ile
`yerel/memmet3-<tarih>` dalına iter; birleştirme bulut geliştirme oturumunda PR ile, CI'daki T10'dan geçince olur. Push yetkisi yoksa dosyalar
`<veri>/GELISTIRME/`'de kalır ve kullanıcıya "bu klasörü bir sonraki geliştirme oturumuna ekle" bilgisi verilir. Birleşme olmadan Ö0-b başlamaz.
**Referans:** `YZ_FILM/ARACLAR/CLAUDE.md`. **Betikler:** `film.py surus`, `esitle --gelistirme`, `beceri-denetim`, `kurulum.py`, `unittest`.

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
ve konu yoksa yalnız tek soru · konu ya da aktif film varsa soru sormadan `film-yap` · bulutta (`ortam=bulut`) konu sorulmaz, yalnız bilgi cümlesi
(D-45) · bu bilgisayarda `O0a.json` yoksa ve kullanıcı "ilk kurulum" yazarsa `YZ_FILM/ARACLAR/CLAUDE.md` §İlk yerel oturum uygulanır (§4.5) ·
her zaman: yalnız konu sorulur, soru = cevap, Flow uyarısında her kipte dur ve başka hesaba geçme, AYARLAR gizli, kalıcı silme yok · sistemi
değiştirmek yalnız `/film-gelistir` ya da geliştirme oturumunda; ayrıntı `YZ_FILM/ARACLAR/CLAUDE.md`). Bugünkü geliştirme listesi
`YZ_FILM/ARACLAR/CLAUDE.md`'ye taşınır. Veri kökündeki 5 satırlık `CLAUDE.md`'yi `kurulum.py --veri-emniyet` yazar (D-02): "Bu klasör film
setinin VERİ klasörüdür; set burada çalışmaz. Kullanıcıya yalnız şunu söyle: 'Masaüstündeki FILM_SETI.bat'a çift tıkla; Claude doğru klasörde
açılır.' Başka bir şey yapma."

### 4.8 Değerlendirme senaryoları (`beceri_denetim.py` + elle bir kez)
1. "film yap" (aktif film yok) → yalnız tek soru; başka cümle yok.
2. "Ejderha büyüten bir kadın hakkında film yap" → soru yok; `film.py yeni --konu …`; A01 görevi; Ö0-b yoksa BUT0 1800 sn seçer ve bunu bilgi olarak söyler.
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
12. Depo bulut oturumunda açılır, aktif film yok, kullanıcı "Ejderha büyüten bir kadın hakkında film yap" der → konu sorulmaz, `film.py yeni`
    çağrılmaz, yalnız D-45'teki bilgi cümlesi söylenir; "deneme" isterse yalnız `--saglayici sahte` ile `ORNEK_3_SAHNE_TAM` koşar.
13. `elle` kipte Memmet hazırlarken olağan dışı fikstürü belirir → sonraki plan hazırlanmaz, sayfada işlem 0, ≤ 10 sn'de çıkış 7, ekranda
    "GÖNDER'e basma, sayfayı yenileme"; `VIDEO_YARI_OTOMATIK.bat` `UYARI_GECTI.bat`'a kadar açılmaz.
14. Bir planın her turda HATA verdiği `kaset` fikstürü → hat 6'da kalmaz; plan §1.5 merdiveniyle `durdu` olur, rapor yazılır, film sonraki aşamaya geçer.
15. Gemini ZIP'i beklenirken ana tur biter → arka plandaki `film.py bekle --kullanici` ZIP gelince çıkar ve oturum kendiliğinden sürer (Ö0-a #16).

## 5. Veri şemaları

Bütün makine dosyaları `_surum` ve `_uretim` zarfı taşır (tek ad `_surum`; alt çizgisiz `surum` geçersizdir); şemalar
`.claude/skills/film-yap/semalar/` altında JSON Schema olarak durur ve `plan_sema.py` / `kapi.py` ile doğrulanır; zarf kuralı bu iki aracın
testlerindedir ([SON] S-5). **İstisnalar:** ajanın `CIKTI/`'ya yazdığı dosyalar zarfsızdır, betik taşırken (`tasima`) zarfı ekler;
`.jsonl` defterlerinde dosya zarfı yoktur, satır şeması `semalar/`'da sürümlüdür; kullanıcı ayar dosyaları (`FILM_AYAR.json`) yalnız `_surum`
taşır; ders ham kayıtları (`DERSLER/ham/*.json`) `_surum` + kendi `zaman`/`ortam` alanlarını, `GOREV.json` `_surum` + kendi `zaman`/`girdi_imza`
alanlarını taşır. Aşağıdaki örneklerin sayıları **örnektir**, ölçüm değildir. Bu bölümde verilmeyen şemalar uzman
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
 "baslik": "EMBERFALL",
 "altyazi_dili": null,
 "karakterler": {
  "mara": {"ref": "01_KARAKTERLER/mara.jpg", "ses": "<voice_id>", "ses_adi": "<paylaşılan ses adı>",
           "evren": "EVREN/EMBERFALL/karakterler/mara@4", "kostum_varsayilan": "k1"},
  "voss": {"ref": "01_KARAKTERLER/voss.jpg", "ses": "<voice_id>", "ses_adi": "<paylaşılan ses adı>",
           "evren": "EVREN/EMBERFALL/karakterler/voss@2", "kostum_varsayilan": "k1"}
 },
 "mekanlar": {"kulube": {"evren": "EVREN/EMBERFALL/mekanlar/kulube@2",
                         "kurulumlar": {"KAM3": {"konum": [2.1, 0.8], "yon_derece": 250, "yukseklik_m": 1.5, "lens_mm": 50, "ebeveyn": "KAM1"}}}},
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
          "_derlenir": {"ana_kareler": ["KAM1", "KAM3", "KAM5"], "yasak_ardisik": [["KAM3", "KAM4"]]}}
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
    "kamera": {"kurulum": "KAM3", "kadraj": "OY", "aci": "goz_hizasi", "lens_mm": 50, "hareket_tipi": "sabit", "odak": "mara"},
    "kadrajdakiler": [{"id": "mara", "olcek": "OY", "yuz_acisi": "3/4", "konusur": true, "kimlik_demiri": true}],
    "baslangic_durumu": "miras",
    "eylem_zinciri": [
     {"id": "a1", "bas": 0.6, "bit": 1.6, "ozne": "mara", "tur": "mikro", "fiil": "cene_kaldirir", "govde": "cene", "olcu": "hafif", "hiz": "yavas", "etki": {}},
     {"id": "a2", "bas": 2.0, "bit": 5.3, "ozne": "mara", "tur": "konusma", "fiil": "konusur", "replik": "R0042", "cumleler": [0, 1], "etki": {}}
    ],
    "bitis_durumu": "derlenir",
    "oyunculuk": {"mara": {"ic_durum": "korkusunu saklıyor", "alt_metin": "kaptanı içeri almamak için soğuk davranıyor",
                           "dis_ifade": {"bas": "kontrollu_sakin", "bit": "gizli_endise"}, "isaretler": ["cene_sikili", "bakis_kacirir"], "siddet": 2}},
    "zincir": {"gecis_turu": "eylem_kesme", "onceki_plan": 120, "baslangic": "ana_kare", "ebeveyn": "KAM3", "dogal_durak": false, "bitis_sabitle": false},
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
                 "gorunmesi_gerekenler": ["mara", "kapi_esigi"], "referans": ["kart:mara/k1@4"], "istem_ozeti": "9c1e44a0",
                 "hikaye": {"vurus": null, "hedef_duygu": "gerilim", "yogunluk": 6, "merak_ac": [], "merak_kapat": [], "kurulum": [],
                            "kullanim_bilgi": [], "ironi": null, "risk": "Mara yavruyu ve saklandığı yeri kaybedebilir"}},
   "uretim": {"uretim_blogu": 7, "saglayici": "flow", "model": "omni-1.1-flash", "cozunurluk": "720p", "klip_sn": 8, "istem_bicimi": "aralik",
              "zincir": {"yontem": "bagimsiz", "kaynak": null, "kesim_sn": null, "derinlik": 0, "yedege_dustu": false},
              "gorsel": {"saglayici": "gemini_paket", "basamak": 2, "aday": "b", "sha1": "e3b0c442", "referanslar": ["kart:mara/k1@4", "ana_kare:KAM3"], "tohum": null},
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
1. Eski alanlar (`film`, `karakterler.<id>.{ref, ses, ses_adi}`, `sahneler[].{no, parti, referans, gorsel_istem, hareket_istem, amac, duygu,
   replik{karakter, metin, cumleler[{en, tr}]}}`, `altyazi_dili`) aynı adla kalır. **Geriye uyum tek yönlüdür** ([SON] O-9): v2 araçları v1
   dosyalarını okur; v1 araçları (`memmet.py` v1, `film.py` v1, `seslendir.py`, `capcut_film.py`, `kontrol.py`, `notlari_oku.py`, `izleme_paketi.py`,
   `istem_denetim.py` v1) v2 dosyasını **okumaz**: `_surum ≥ 2` görünce 4 ile çıkar ve "Memmet v2 gerekli" ya da "<araç> v2 gerekli" yazar (PR-0);
   her araç kendi PR'ında v2 desteğiyle bu korumanın yerine geçer. **Tek ayırt edici `_surum`'dur:** alan yoksa ya da 1 ise dosya v1'dir ve eski
   kurallar uygulanır (`istem_denetim` filtre kelimesini UYARI verir; `ORNEK_3_SAHNE` ve `test_film.py`'nin beklentileri değişmez); ≥ 2 ise v2'dir
   ve her planda `zanaat` zorunludur (`plan_tipi`'ne göre koşullu alanlar); eksikse `plan_sema` HATA verir ("zanaat yoksa v1" kuralı kalktı).
2. **Anlam değişikliği:** `parti` artık hikâye partisidir (1–3). 20 planlık gönderim bloğu `uretim.uretim_blogu`'dur; Memmet `parti`'yi okumaz,
   `BLOK_PLANI.json`'u okur ([UM2] S15). v1 Memmet'in molası `parti` sayısına bağlı olduğu için ≈ 165 planlık hikâye partilerinde neredeyse hiç
   mola vermezdi; kural 1'deki `_surum` reddi bunu kapatır. `baslik` artık **ekran ya da seri adıdır** (`capcut_film` kalıplı başlığı `split("|")`
   ile bölüp ekrana "Full Movie 4K 2026" yazıyordu); YouTube başlığı yalnız `YAYIN/PAKET.json`'dadır ([SON] S-6). Normal filmde `altyazi_dili: null`;
   SRT'ler YouTube'a ayrı gider, `capcut_film --yayin` Altyazi kanalı koymaz (dışa aktarımda altyazı görüntüye gömülmesin).
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
7. **v1 → v2 eşleme** (CLAUDE_ICIN şemasının ve `memmet.py`'nin kullandığı alanlar; [SON] O-9): `bitis_karesi: <no>` → `zanaat.zincir.bitis_sabitle:
   true` + `uretim.zincir {yontem: "bitis_sabit", bitis_gorsel: "plan:<no>"}`; `motor` → `uretim.saglayici` (`flow` dışı değer Memmet'te atlanır);
   `gorsel_istem_yedek` / `hareket_istem_yedek` → **derlenmiş** yedek istemler (`istem_derle --yedek`: filtre-güvenli şablon, dolaylı anlatım);
   memmet v2 filtre reddinde aynı istemi yeniden göndermez, yedeği bir kez gönderir, o da reddedilirse madde `yonetmen·onarim`'a (filtre reddi
   kipi) gider ([UM2] S4). `karakterler.<id>.{ref, ses, ses_adi}` alanlarını `plan_birlestir` evrenden doldurur ve kartı `01_KARAKTERLER/`'e kopyalar
   (v1 `istem_denetim` ref dosyası yoksa HATA veriyordu).
8. **Eğitim belgelerindeki alanların v2'deki yeri** ([SON] O-8; ZN §6.1 ve AR2 §6.1 bu tabloya göre düzeltilir, §2.5):

   | ZN §6.1 / AR2 §6.1 alanı | v2'deki yeri | Yazan |
   |---|---|---|
   | `kadraj` | `zanaat.kamera.kadraj` | yönetmen |
   | `sure_sn` | `_derlenir.sure_sn` (`kullanim.sure`'den) | kod |
   | `kamera_tarafi` (`A`/`B`), `eksen_gecis` | sahne düzeyinde `sahne_gruplari.<S>.{eksen, kamera_tarafi}` (pusula yönü, harita); plan düzeyinde `_derlenir.kamera_tarafi` (`kroki.py`, kurulum konumundan); eksen geçişi kurulumun eksene göre yerinden | yönetmen (harita) / kod |
   | `bakis` | durum nesnesinde `bakis.hedef` (olgu); kadraja düşüşü `_derlenir.bakis_kadrajda` | yönetmen / kod |
   | `vurus`, `hedef_duygu`, `yogunluk`, `merak_ac/kapat`, `kurulum`, `kullanim_bilgi`, `ironi`, dramatik `risk` | `HIKAYE.json` (sahne ve olay düzeyi, R/olay kimliğiyle); `zaman_cizelgesi` T0'da plana `_derlenir.hikaye` olarak eşlenir | hikâye odası / kod |
   | `ekranda_bilgi` | `zanaat.ekranda_bilgi` | yönetmen |
   | `baslangic_durumu`, `bitis_durumu` | `zanaat.baslangic_durumu` (`miras` ya da olgu); `bitis_durumu` `derlenir` (dünya defteri) | yönetmen / kod |
   | `eylem_zinciri` | `zanaat.eylem_zinciri` (D-13 adım şeması; konuşma bir adımdır) | yönetmen |
   | `kesme`, `ekran_disi_ses` | `zanaat.kesme`, `zanaat.ekran_disi_ses` | yönetmen → kurgu |
   | `replik_zaman` | `_derlenir.replik_zaman` | kod |
   | `ses` | `zanaat.ses`, `sahne_gruplari.<S>.ses` | ses tasarımcısı |
   | AR2 `sureklilik.{gecis_turu, onceki_plan}` | `zanaat.zincir` | yönetmen |
   | AR2 `sureklilik.{kamera_konumu, plan_olcegi, kamera_acisi, kamera_hareketi}` | `zanaat.kamera.{kurulum, kadraj, aci, hareket_tipi}` | yönetmen |
   | AR2 `sureklilik.{kadrajdakiler, nesneler, kadraj_sirasi}` | `zanaat.kadrajdakiler`, durum nesnesi (kural 6), `_derlenir.kadraj_sirasi` | yönetmen / kod |
   | AR2 `sureklilik.{isik, isik_degisimi, yasaklar}` | `sahne_gruplari.<S>.isik`, `zanaat.yasaklar` | yönetmen |
   | AR2 `sureklilik.{uretim, denetim}` | plan kökünde `uretim`, `denetim` | betikler, kapılar |

### 5.2 Dünya durumu defteri `<film>/DUNYA_DEFTERI.json` (sahibi `dunya_defteri.py`; elle düzenlenmez)
```json
{
 "_surum": 1, "_uretim": {"asama": "A07c", "girdi_imza": "c19a2f07", "arac_surum": "dunya_defteri 1.0", "sonuc": "GEC", "zaman": "…", "ortam": "yerel"},
 "film": "EMBERFALL_F2", "evren": "EVREN/EMBERFALL@7",
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
  sıçraması BAYRAK. Paralel planlanan sahnelerin ucu sözleşmedeki `giris_durumu`/`cikis_durumu` ile karşılaştırılır (`sahne_uclari.hikaye_esit`);
  uyuşmazlık K0 HATA'sıdır ve `YENIDEN_YAZ` yalnız ilgili iki sahneye gider ([SON] O-12).

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
{"_surum": 3, "_uretim": {"asama": "A18", "gorev": "A18-DD-001", "arac_surum": "ders_derle 1.0", "sonuc": "GEC", "zaman": "…", "ortam": "yerel"}, "kurallar": [
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

### 5.4 Seri evreni kütüphanesi `<evren>/` (yalnız `evren.py` yazar; veri kökünde durur, git deposu değildir; A18'de D'ye yedeklenir, D-42)
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
{"_surum": 2, "_uretim": {"asama": "film.py", "arac_surum": "film 2.0", "zaman": "…", "ortam": "yerel"}, "film": "EMBERFALL_F2", "seri": "EMBERFALL", "ortam_son": "yerel", "aktif_asama": "A12",
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
{"_surum": 2, "id": "A12-AS-014", "film": "EMBERFALL_F2", "asama": "A12", "tur": "ajan", "ajan": "habersiz-seyirci", "kip": "animatik",
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
| `izleyici` / `dinleyici` | `gemini_api` · `sahte` | ücretsiz anahtar varsa ve maliyet 0 ise **açık**; ücretli kullanım yalnız `izinler.gemini_api_ucretli` + dolar tavanıyla; yoksa ÖLÇÜLEMEDİ + izle-dinle paketi (D-19) |
| `gorsel` | `gemini_paket` (kullanıcı taşır) · `gemini_api` (Ö0-e uygunsa) · `vertex_gorsel` (dolar izni) · `sahte` | |
| `gorsel_duzeltme` | `vertex_gorsel` (dolar izni) · `flow_gorsel` (Memmet, çift çıktı, `elle`) · `sahte` | kullanıcı paketi yok |
| `video` | `flow` · `veo_vertex` (dolar izni + Ö0 fiyatı; P2) · `sahte` · `sahte_bozuk` (test) | kie.ai yok; `FLOW_KILIDI` varken Vertex'e otomatik geçiş yok, yalnız `izinler.flow_kilitliyken_vertex` + `usd_tavan_film > 0` ile `blok_plani` planlar (D-03) |
| `tts` | `ai84` · `sahte` | eski ad `ses` |
| `ses_donustur` | Ö0-c sırası (`openvoice` · `chatterbox` · `rvc` koşullar okununca) · `ai84_vc` (tavanlı) · `sahte` | |
| `ayristirma` / `asr` / `dudak` | `roformer` · `demucs` / `faster_whisper` (+ stable-ts) / `musetalk` · hepsinde `sahte` | Wav2Lip yok |
| `muzik` | `acestep` · `kutuphane` (KUR1 çekirdek seti + isteğe bağlı YouTube Ses Kitaplığı) · `elevenlabs_muzik` (P2) · `gemini_muzik_paketi` (elle; lisans doğrulanınca; son basamak) · `midi_ornek` (yalnız animatik) · `sahte` | `elle = True` yalnız son basamak; zincir boşsa müziksiz ipucu + S6 BAYRAK (D-25) |
| `buyutme` | Ö0-c'de kazanan yapay zekâ büyütücü · `lanczos` · `sahte` | |

Tablodaki `sahte`, `kaset` ve `sahte_bozuk` yalnız test kipindedir (D-41).

`<veri>/AYARLAR/FILM_AYAR.json` (anahtar içermez; kurulum yazar, kullanıcı yalnız `IZINLER.bat` ile değiştirir; **yalnız izin, tercih ve para
tavanı** taşır, sayısal güvenlik sınırı taşımaz; D-34, [SON] O-10):
```json
{"_surum": 3, "ortam": "yerel", "mod": "tam_otomatik",
 "saglayicilar": {"gorsel": ["gemini_paket"], "gorsel_duzeltme": ["flow_gorsel"], "video": ["flow"], "tts": ["ai84"],
                  "muzik": {"yayin": ["acestep", "kutuphane"], "animatik": ["acestep", "midi_ornek"]}},
 "butce": {"flow_kredi_tavan_film": null, "ai84_kredi_tavan_film": 60000, "ai84_seri_kurulum_tavan": 40000, "ai84_vc_tavan_film": 20000,
           "usd_tavan_film": 0, "takvim_hedef_gun": 21},
 "izinler": {"gece_flow": false, "gemini_api_ucretli": false, "flow_kilitliyken_vertex": false, "cc0_efekt_indir": false,
             "youtube_baglanti": false, "yukleme": false},
 "bildirim": {"telegram": true, "masaustu": true}, "yayin_kaynagi": "capcut"}
```
`mod` tek alandır (`tam_otomatik` | `onayli`; eski `izinler.onayli_kip` kalktı). Video oturumunun kipi açılan `.bat`'la seçilir
(`VIDEO_YARI_OTOMATIK.bat` = `elle`; `VIDEO_GECE.bat` yalnız `izinler.gece_flow` ile). Eski sürümdeki güvenlik sayıları (`gorsel_gunluk_tavan`,
`gorsel_sonrasi_video_saat`, `haftalik_uyari_kilidi_gun`, `kapi_payi`, `take_payi_kredi`, `guvenlik_payi`, `disk_bos_min_gb`, `paralel_max`, Flow
modeli, çözünürlük, klip süresi) `hat_esikleri.json`'a taşındı (§7.3); `FILM_AYAR`'da bulunurlarsa `esikler.py` sıkı olanı uygular (tavanlarda
`min(eşik, ayar)`, tabanlarda `max`; çözünürlük en az 720p, model değişmez) ve BAYRAK yazar.
`<depo>/YZ_FILM/AYARLAR/YOLLAR.json` (makineye özgü; git'e girmez; `kurulum.py --yollar` yazar, PR-1): `depo_kok`, `veri_kok`, `evren_kok`, `arsiv` (D:), `yedek` (`D:\YZ_FILM_YEDEK`), `gelistirme` (`<veri>/GELISTIRME`), `gemini_paket`
(`Desktop\GEMINI GORSEL ISTEM`), `capcut_taslak`, `ses_kutuphanesi`, `onbellek` (model + pip, C'de tek klasör), `python {ana, py312, py311}`,
`ortamlar {ses_donustur, musetalk, acestep, buyutme}`. Anahtar dosyaları (AI84, Telegram, Gemini, Anthropic, Freesound, YouTube OAuth) yalnız
`<veri>/AYARLAR/` içinde ya da ortam değişkenindedir; depodaki `YZ_FILM/AYARLAR/` anahtar dosyaları boş kalır ve kurulum boş olduklarını denetler.
**Yol göçü** ([SON] O-1): bugün `memmet.py` (AYARLAR, satır 20–21, 40), `ai84.py` (satır 5), `saglayicilar/__init__.py` (satır 14) ve
`yeni_film.py` (FILMLER; `.bat`'larda `%~dp0..\..\ARACLAR\` göreli yolu) yollarını kendi konumlarına göre kuruyor. PR-1'de `memmet`, `ai84`,
`saglayicilar`, `kontrol`, `seslendir`, `capcut_film`, `notlari_oku`, `kurulum`, `yeni_film`, `paketle` AYARLAR, FILMLER, EVREN ve
SES_KUTUPHANESI yollarını yalnız `ortak.yollar()`'dan alır; `YOLLAR.json` yoksa açık hata verilir ("önce KURULUM.bat"). Üretilen bütün `.bat`'lar
hem Python'u hem betiği **mutlak yolla** çağırır (`bat_yenile.py`). Kabul: `test_yollar` (depo ve veri iki ayrı geçici klasördeyken hiçbir araç
depo içinde AYARLAR ya da FILMLER oluşturmaz; üretilen `.bat` içinde `..\..\ARACLAR` geçmez).

### 5.7 Kapı raporu ve kuyruk maddesi
`_RAPOR/<KAPI>_<kapsam>[_t<tur>].json` (bütün kapılar aynı zarf; `kapi.py` yazar):
```json
{"_surum": 1, "_uretim": {"asama": "A11", "gorev": "A11-G1-007", "girdi_imza": "c3d4e5", "arac_surum": "kare_denetim 1.0",
             "esik_surum": "sureklilik@1.0+ogrenilen@3", "sonuc": "KISMI", "zaman": "…", "ortam": "yerel"},
 "kapi": "G1", "kapsam": "P1_B2", "tur": 1, "sonuc": "KISMI", "ozet": {"plan": 30, "gec": 22, "bayrak": 5, "hata": 3, "olculemedi": 1},
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
Aşağıdaki örnek ajanın `CIKTI/` biçimidir (zarfsız); `film.py` `_RAPOR/SEYIRCI/…`'ya taşırken `_surum` ve `_uretim` ekler (§5 istisnaları).
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
| `memmet.py` (acil yama; aynı yama memmet3'e, §4.5) | değişir | D-02 a–g: `OLAGANDISI_KELIMELERI` ayrı liste → **her kipte** anında `Durdur(kod="olagandisi")`, sayfada işlem 0, `FLOW_KILIDI.json`, ekrana/Telegram'a "GÖNDER'e basma, sayfayı yenileme", çıkış 7; memmet3'ün `elle` kipindeki "sayfayı yenile, devam" yolu ve gece kipindeki 5 yenileme silinir; "olağan/unusual" `HATA_KELIMELERI`'nden çıkar; `kontrol_noktasi()` reCAPTCHA/doğrulama/oturum düşmesinde beklemez, bildirir, çıkış 2; varsayılan tempo 17.10 değerleri (`MEMMET_AYAR.json` daha hızlıysa yavaş olan); son gönderim ve kalan mola `<veri>/HESAP/FLOW_TEMPO.json`'da (açılışta okunur); `_surum ≥ 2` → çıkış 4; `_memmet_cikis.json` kodu yazar; docstring "insan temposu" → "yük sınırı"; varsayılan 720p | Flow sayfası → `_memmet_cikis.json` | playwright (Apache-2.0) | ✓ | **P0 (PR-0)** | evet: HTML fikstürü (T10-elle, T10-gece, T10-dogrulama; tempo; mola) |
| `saglayicilar/flow.py` (acil yama) | değişir | Memmet çıkış kodu → `Kisitlandi(kod=…)` (7 → `olagandisi`, 2 → `dogrulama`/`giris`, 4 → `ortam`); bilinmeyen kod sağlayıcı değiştirmez (kapalı başarısız; [UM2] S13) | çıkış kodu → `Kisitlandi` | stdlib | ✓ | **P0 (PR-0)** | evet: çıkış 7 → sağlayıcı geçişi 0 |
| `kurulum.py --veri-emniyet` | yeni alt komut | D-02 veri kökü emniyeti: `<veri>` altındaki eski Memmet, `film.py` ve `memmet.py`'yi çağıran `.bat/.cmd/.ps1`'ler ile veri kökünün `BASLA_BURADAN.txt`, `00_BENI_OKU.txt`, `KURULUM.bat`, `YENI_FILM.bat` dosyaları `_ESKI/`'ye taşınır (silinmez); yerlerine emeklilik `.bat`'ı ve depo sürümüne giden `memmet.py` sarmalayıcısı; veri kökü `CLAUDE.md`'si; `OpenMontage`'a dokunulmaz; taşınanların listesi | `<veri>` → `_ESKI/`, `EMNIYET_RAPORU.json` | stdlib | ✓ | **P0 (PR-0)** | evet: geçici veri kökü fikstürü (yamasız Memmet'e giden `.bat` 0) |
| `memmet.py` v2 (memmet3 tabanlı) | değişir | `--blok <BLOK_PLANI> --onizleme <imza> --mod elle\|gece --bakiye --giris`; gönderim kaydı önce (`KREDI_DEFTERI.jsonl`), `FLOW_YUK`, `FLOW_TEMPO`'yu her gönderimden önce okur, `DUR` dosyası; filtre reddinde aynı istemi yeniden göndermez (derlenmiş yedek istemi bir kez gönderir, sonra `yonetmen·onarim`; §5.1 kural 7); zaman aşımında önce toplar; hesap kimliği sha1'i; çift çıktı görselde; `kaynak_klip` atlanır; zincir kaynağı hazır değilse ardılı almaz. "gündüz otomatik" kipi kalkar (BK §6.2 #7: 15–20 dk'da bir uyarı) | `BLOK_PLANI.json` → `SIRALI_VIDEO/`, `KUNYE/`, `_memmet_cikis.json` | playwright | ✓ | P1 | evet: fikstür + `sahte` Flow sayfası |
| `memmet_topla.py` | yeni | yeni gönderim yapmadan biten sonuçları indirir, `KREDI_DEFTERI` ile eşler; bulunamayan `kayip` | Flow projesi → `SIRALI_VIDEO/` | playwright | ✓ | P1 | evet |
| `memmet_yama.py` + `testler/test_memmet_korkuluk.py` | yeni | aday yamayı geçici kopyada uygular; korkuluk: tempo yalnız artar, uyarı kelimeleri yalnız büyür, pyautogui/pynput/SendKeys yok, yeniden deneme ve sayfa yenileme artmaz, uyarıdan sonra her kipte sayfa işlemi 0 kalır (T10 her kipte yeniden koşar), `--mod` varsayılanı `elle`, `FLOW_TEMPO` okuması kalır, ≤ 80 satır | diff → GEÇ/KAL | stdlib | ✓ | P1 | evet |
| `film.py` v2 + `.claude/bin/film.py` (sarmalayıcı) | değişir/yeni | görev defteri: `yeni, sonraki, basla, calis, bitir, kurtar, asama-ilerlet, bekle (--kullanici <id> \| --blok <B>: eser yoklama, 6 saatte hatırlatma, bitince oturumu uyandırma), karar ekle, ders ekle, goster (… \| pencere <uygulama>: salt okunur PrintWindow), ozet, surus ac/kapat, notlar oku/isle, beceri-denetim, olcum0, asamalar --md, esitle --gelistirme (P0; yalnız `<veri>/GELISTIRME/` beyaz listesi, anahtar taraması, ayrı dala), esitle (tam; P2)`; tavan sonrası merdivenini (§1.5) görev olarak açar; `onay()`/`input()` kalkar; atomik yazım + `FILM.kilit`; plan düzeyi imza; `Kisitlandi(olagandisi\|dogrulama)` sonrası sağlayıcı geçişi yok; disk ve token kapıları | görev klasörleri ↔ `FILM_DURUM.json` | stdlib | ✓ | P0 (PR-0'da Kisitlandi düzeltmesi; PR-2 çekirdek) | evet: `test_gorev_defteri` (30 kesme senaryosu) |
| `hat/asamalar.py` | yeni | `Asama(kod, ad, kim, girdiler[{ad, ureten}], ciktilar, kapilar, kredi, ortam, tur_max, tavan_sonrasi, geri_don, gorevler)` kaydı; §1.3'ün tek kaynağı; `tavan_sonrasi` ve her girdinin `ureten` aşaması zorunlu ([SON] K-4, S-3) | — | stdlib | ✓ | P0 | evet (`test_asamalar`: boş `tavan_sonrasi` ya da üreticisiz girdi HATA) |
| `ortak.py` | yeni | `atomik_yaz` (Windows'ta 3 kez kısa beklemeyle yeniden dener), `jsonl_ekle` (fsync), `imza`, `kilit`, `ortam`, `yollar` (tek yol kaynağı; `YOLLAR.json` yoksa açık hata; [SON] O-1), `maskele`, `ffprobe_sure`, `disk_bos_gb` | — | stdlib | ✓ | P0 (PR-1) | evet (`test_yollar`) |
| `kurulum.py --yollar` | yeni alt komut | `YOLLAR.json`'u soru sormadan yazar (`<depo>`, `<veri>` = `Desktop\YZ_FILM`, D yolları) | — | stdlib | ✓ | P0 (PR-1) | evet |
| `esikler.py` | yeni | eşik dosyalarını yükler; `kaynak` alanı zorunlu; aynı anahtar iki eşik dosyasında HATA; `FILM_AYAR.json`'daki güvenlik sınırına sıkı olanı uygular ve BAYRAK yazar (D-34); `KURALLAR_OGRENILEN.json` katmanı | eşik dosyaları → sözlük | stdlib | ✓ | P0 | evet |
| `kapi.py` | yeni | ortak kapı raporu zarfı ve `sonuc` birleştirme; ÖLÇÜLEMEDİ → BAYRAK | — | stdlib | ✓ | P0 | evet |
| `kuyruk.py` | yeni | bütün kapıların maddelerini birleştirir, tekrarları ayıklar, öncelik ve zincir etkisi; **0 kredi kuralı**; dilim; soy sayacı ≤ 3; eski klibi `_ESKI/`'ye taşır; `--merdiven-md` (kurgucunun `MERDIVEN.md`'si: 0 kredi merdiveni + maddeye özel basamaklar) | kapı raporları → `KUYRUK/*.json`, `URETIM_ONIZLEME.md` | stdlib | ✓ | P0 (şema) / P1 (video) | evet |
| `kredi.py` + `olcek.py` | yeni | BUT0/BUT1/BUT2/BUTK; dilimler; take payı; ölçek, takvim, kullanıcı el işi saati, token projeksiyonu tek kaynaktan | SAHNELER, OLCUM0, bakiye → `URETIM_ONIZLEME.json`, `_RAPOR/BUT*` | stdlib | ✓ | P0 | evet |
| `flow_yuk.py` | yeni | `FLOW_YUK.jsonl`, `FLOW_TEMPO.json`, `FLOW_KILIDI.json`, `HESAP_DURUMU.json`; haftalık uyarı kilidi; hesap değişimi kilidi (D-03); PR-0'da Memmet'in yazdığı `FLOW_TEMPO.json` şemasını devralır; sayılar yalnız `hat_esikleri.json`'dan | — | stdlib | ✓ | P0 | evet |
| `blok_plani.py` | yeni | uygunluk kuyruğu; blok ≤ 20; önce KRİTİK yeniden çekim, sonra hikâye sırası; zincir ardılı sonraki bloğa; `--kesit` (dikey kesit planlarını ve kapsama eksiğini seçer; eski adı `pilot_sec`); `FLOW_KILIDI` varken yalnız `izinler.flow_kilitliyken_vertex` + `usd_tavan_film > 0` ise kalan planlara `veo_vertex` yazar (D-03) | SAHNELER, denetim → `BLOK_PLANI.json` | stdlib | ✓ | P1 | evet (kilit + izin yok → Vertex 0; kilit + izin → Flow gönderimi 0) |
| `bildirim.py` | yeni | olay tablosu (§8.3); Telegram + masaüstü; `film.py bekle`'nin 6 saatlik hatırlatması; tekrar 30 dk, saatte ≤ 12; içerikte gizli bilgi yok | olay → mesaj | requests (Apache-2.0) | ✓ | P1 | evet (`sahte` kanal) |
| `ders_defteri.py` + `ders_derle.py` | yeni | `kaydet()`; kümeleme; `DERSLER_AKTIF.md`, `KURALLAR_OGRENILEN.json`; korkuluk testi; yanlış alarm ölçümü; `--film-sonu` (`FILM_SONU_RAPORU.md`: açık eksikler, `hedef_alti`, ölçülemeyenler, el işi gerçekleşeni); `--yedekle` (D'ye `robocopy /E` kopya + sha1 listesi; D-42) | ham kayıtlar → derleme | stdlib | ✓ | P0 (kaydet) / P1 (derle, film sonu, yedek) | evet |
| `yerel_is.py` | yeni | ağır iş kuyruğu + `GPU.kilit`; tek GPU işi; ayrı ortamları `YOLLAR.json`'dan çağırır; OOM bir kez yeniden, sonra ÖLÇÜLEMEDİ + ders | iş → çıktı | stdlib | ✓ | P1 | evet |
| `olcum0/` (`flow_deneme.py` + `fikstur/O0b_istemler_v1.json`, `ses_deneme.py`, `capcut_deneme.py`, `gemini_deneme.py`, `kanca_deneme/`) | yeni | Ö0-1 denemeleri kendi içinde yeterlidir (sonraki PR'ların aracına muhtaç değil); Ö0-2 betikleri ilgili araçlar gelince; `O0<harf>.json` | §1.2 | ilgili araçlar | ✓ | **P0** | kısmen (rapor biçimi; Ö0-b merdiveni ilk uyarıda kapanır) |
| `veri/ADLAR.json` + `testler/test_adlar.py` | yeni | ad sözlüğü ve denetimi (D-35): önekler (`KUR`, `KAM`, `BUT`), sahne/ses kapısı biçimi, ZN ve AR2'deki alan adları, "üreticisi olmayan girdi = HATA" | — | stdlib | ✓ | P0 | evet |
| `veri/LISANSLAR.json` | yeni | lisans defteri (D-36): geçişli bağımlılıklar, `kullanici_araci`, Gemini ücretsiz katman veri koşulu, müzik çekirdek seti, Gemini müzik koşulları | — | — | — | P0 | evet (şema) |
| `veri/tur_kanca.json`, `veri/aksan_sozlugu.json` | yeni | tür–kanca tablosu (BK §2'den; yapımcı girdisi); aksan sözlüğü (`ses_sec --ara` üretir; ses tasarımcısı girdisi) ([SON] S-2) | — | — | — | P0 / P1 | evet (şema) |
| `veri/kok_neden.json` | yeni | kök neden sözlüğü ve sahipleri | — | — | — | P0 | evet |
| `arsivle.py` | yeni | D-38: `robocopy /E /MOVE` ile D'ye taşıma (`/MIR` yok); A16, A17 sonunda ve disk kapısında Claude kendisi başlatır; son taslağın bağlı olduğu dosyaları, açık kuyruk girdilerini ve dışa aktarılmamış işi atlar; taşınanların listesi bilgi | — | stdlib | ✓ | **P1** ([SON] O-7) | evet (kuru çalıştırma; bağlı yol taşınmaz) |
| `film.py esitle` | yeni | `--gelistirme` (P0; PR-1'de bağımsız `esitle_gelistirme.py`, PR-2'de alt komut): `<veri>/GELISTIRME/` beyaz listesi → anahtar taraması → `yerel/<ad>-<tarih>` dalına commit + push (ana dala yazmaz); tam bulut ↔ yerel eşitleme (P2) | — | git | ✓ | P0 (`--gelistirme`) / P2 | evet |

### 6.2 Claude Code katmanı
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `.claude/settings.json` + `settings.local.json` (kurulum yazar) | yeni | `env: CLAUDE_CODE_FORK_SUBAGENT=0`; izin listesi yalnız `python .claude/bin/film.py *`; statik ret: anahtar dosyası okuma, `robocopy /MIR`; kancalar (SessionStart, UserPromptSubmit, PreToolUse × 3, SubagentStart, SubagentStop timeout 120, PostToolUse Agent, Stop, StopFailure, PreCompact, PostCompact, PostModelSwitch) (SubagentStart, StopFailure, PostCompact ve PostModelSwitch'in varlığı Ö0-a #17'de sınanır; olmayanın yedeği §10.3'te); `settings.local.json`: mutlak Python yolu, `additionalDirectories` (veri kökü), `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH=1` | — | — | ✓ | P0 | evet (`test_kancalar`) |
| `.claude/hooks/kanca.py` + `.claude/bin/kanca.sh` | yeni | alt komutlar: `erisim` (görev klasörü, iki kökte AYARLAR reddi, ileri bölüm reddi, 200 KB üstü Read reddi), `komut` (gizli dosya, `robocopy /MIR`, kalıcı silme, pyautogui/pynput/SendKeys; sürüşte doğrudan `memmet.py`, Flow kilidiyken gönderim, `git push`, makine sahipli dosyaya yazma), `ajan` (kadro dışı, fork, yerleşik ajan, `calisiyor` şartı, paralel ≤ 5), `oturum_basi` (≤ 6.000 kr bağlam), `ajan_basi`, `ajan_bitti` (doğrulama, aşamalı devam, kullanım kaydı), `ajan_sonrasi`, `stop` (soru kapısı + devam kapısı, ardışık 8 + token bütçesi), `istem` ("dur/durdur/bekle" → sürüş kapanır), `hata`, `ozet_sakla`, `model_degisti`; kanca nabzı; **kendi içinde kapalı başarısız**: en üstte try/except, her beklenmeyen hatada engelleyen çıkış ya da JSON `deny`, ağır içe aktarma yok, hedef ≤ 1 sn (D-11) | kanca girdisi → karar | stdlib | ✓ | P0 | evet (`test_kancalar`, 50 mesajlık soru seti) |
| `.claude/kurallar/erisim.json` | yeni | rol başına okuma/yazma desenleri (kör, denetçi, yazar), gizli ve makine sahipli yollar | — | — | — | P0 | evet |
| `kor_paket.py` | yeni (`izleme_paketi.py` buraya taşınır; eski dosya v1 filmler için sarmalayıcı kalır) | kipler `kagit, plan, ilk2dk, animatik, kurgu, kesit, kesici, kapak`; beyaz liste; ad maskeleme; işitsel döküm; aşamalı parça klasörleri; persona satırı | SAHNELER, HIKAYE, medya → `_GOREV/<id>/GIRDI/` | Pillow (HPND) | ✓ | P0 (kâğıt kipleri) / P1 (izleme) | evet (`test_kor_paket`: sızıntı 0) |
| `dilim.py`, `plan_birlestir.py` | yeni | ajanlara SAHNELER/HIKAYE dilimi (A07b'de paralel görevlere önceki sahnenin sözleşmedeki `cikis_durumu`, yalnız aynı mekân ve zamandaki ardışık sahne çiftine çözülmüş plan bitişi; o çift sırayla koşar); planlar + ses → `SAHNELER.json` (`_surum: 2`; `karakterler.<id>.{ref, ses, ses_adi}` evrenden doldurulur, kart `01_KARAKTERLER/`'e kopyalanır), `NO_ESLEME.json` | — | stdlib | ✓ | P0 | evet |
| `beceri_denetim.py` | yeni | SKILL.md satır/çekirdek token tahmini; ad kuralı; açıklama uzunlukları; ajan frontmatter'ı (`opus`, `effort: high`, `acceptEdits`, `memory` yok, `Bash`/`Agent` yok, kör ajanda `omitClaudeMd` + `Read, Write`); açıklama toplamı ≤ 3.000 token; şablonlardaki OZET biçimi | — | stdlib | ✓ | P1 | evet |
| 21 ajan dosyası, 4 `SKILL.md`, `KURTARMA.md`, `GOREV_SEMASI.md`, `KULLANICI_DILI.md`, `reference/*.md`, `PLAN_DILI.md`, `sablonlar/*.md`, `semalar/*.json` | yeni/değişir | §3, §4 | — | — | — | P0 | evet (`beceri_denetim`) |
| Kök `CLAUDE.md`, `YZ_FILM/ARACLAR/CLAUDE.md`, veri kökü `CLAUDE.md` | değişir/yeni | §4.7 | — | — | — | P0 | — |

### 6.3 Hikâye odası
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `hikaye_odasi.py` | yeni | `konu-denetim, butce-bilgisi, brifing, logline, oneri-denetim, juri-paketi, juri-topla, yapi-denetim, oyuncu-paketi, senaryo-denetim, seyirci-topla, ilk2dk-topla, devir, sahne-sozlesme, vaat-denetim, seyirlik-denetim`; `seyirci-topla` ve `ilk2dk-topla` kendi hesap yapmaz, `puan_oku.seyirci_topla`'yı çağıran ince kısayoldur (D-32, [SON] S-4) | — | stdlib | ✓ | P0 | evet (`kaset`) |
| `bulgu_yonlendir.py` | yeni (tek kod; [SN2] `bulgu-sinifla` + [KU2]) | `ozet-eslestirici·bulgu` eşlemesi + sahip tablosu + K1 eşlemesi → sahip, kök neden, merdiven önerisi | → `BULGU_YONLENDIRME_<T>_t<n>.json` | stdlib | ✓ | P0 | evet |
| `puan_oku.py` v2 (`seyirci_topla`) | değişir | **medyan**, 6 ölçüt + GENEL, KRİTİK birleştirme (±1 plan), D-21 kanıt doğrulaması, plato, personalar, tahmini tutma eğrisi, parça konum yanlılığı; eski `OZET` biçimini okur | raporlar → `SEYIRCI_KARAR_*.json` | stdlib | ✓ | **P0 (PR-1'de medyan)** | evet ({6, 8, 9} → 8) |
| `istem_denetim.py` v2 | değişir | v1 davranışı korunur; v2'de replik filtre taraması HATA, 8 sn'de ≤ 16 kelime, yasak sonuç ve iç durum fiilleri, çıplak left/right, `veo_ses_tarifi` birebir ve ≤ 12 kelime, `flow_sound` kalıbı, kimlik dizesi birebir, iki el tarifli, süren eylem fiili (görselde), referans ≤ 2 karakter, ifade sözlüğü şablonları, öğrenilen kurallar | SAHNELER → `_RAPOR/ISTEM_*.json` | stdlib | ✓ | P0 | evet |
| `evren.py` | yeni | `--kur, --bagla, --on-kayit, --spec-dogrula, --kilitle, --surum-ac, --film-sonu, --disa-aktar, --ice-al, hikaye-kaydet --dogrula, ne_yok_kelimeleri, izleyici-ozeti, ozet, --yedekle, --yedek-dogrula` (D-42: D'ye `robocopy /E` kopya, sha1 listesi, A00 doğrulaması) | — | stdlib, numpy (BSD) | ✓ | P0 | evet |
| `veri/hikaye_esikleri.json`, `semalar/` hikâye şemaları, `JURI_TABLOSU.md`, şablonlar | yeni | [SN2] §4.7 + §7 | — | — | — | P0 | evet |
| `kanal_teshis.py` | yeni | kullanıcının YouTube Studio CSV'si (varsayılan; adımlar `BASLA_BURADAN.txt`'de) → `KANAL_TESHIS.md`; salt okuma OAuth kipi P2 ([SON] S-10) | — | stdlib (CSV); google-api-python-client (Apache-2.0; yalnız P2 OAuth) | ✓ | P0 (CSV kipi, Ö0-g; adım 9) / P2 (OAuth) | evet (CSV fikstürü) |
| `claude_api.py` | yeni | başsız mod sağlayıcısı (effort high, yapılandırılmış çıktı); yalnız `ANTHROPIC_API_KEY` ya da `AYARLAR/anthropic_anahtar.txt` | — | anthropic SDK (MIT) | ✓ | P2 | evet (`kaset`) |

### 6.4 Yönetmen ve plan dili
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `veri/plan_sozlukleri.json`, `veri/fiil_sozlugu.json` (+ `beklenen_hiz`, `sure_carpani`), `veri/ifade_sozlugu.json` (≈ 16 değer; EN istem + kör soru karşılığı), `veri/efekt_sozlugu.json` | yeni | sözlükler | — | — | — | P0 | evet |
| `plan_sema.py` | yeni | plan şeması (v1/v2; tek ayırt edici `_surum`; v2'de `zanaat` zorunlu), sahiplik (`_derlenir`'e yazım HATA), `_surum`/`_uretim` zarf kuralı | — | jsonschema (MIT) | ✓ | P0 | evet |
| `kroki.py` | yeni (kütüphane + CLI) | izdüşüm, görüş hattı, bakış/ışık/ekran yönü, göz farkı, ağız görünürlüğü, ayna yasağı, görünmesi gerekenler, plaka görüneni, yasak ardışık, `--karsilikli`, `--ciz` | kroki + plan → `_derlenir`, PNG | Pillow | ✓ | P0 | evet |
| `plan_denetim.py` | yeni | `--harita`, `--sahne`, `--tum`; Y01–Y60 + oyunculuk (ifade zorunlu, duygu sıçraması); fiziksel adım ≥ 1,5 sn, `mikro`/`ses_vurusu` adımı ≥ `eylem_adim_mikro_min_sn`; diyalog süresinde L/J taşması görünen süreden düşülür (Z0 #5) | → `_RAPOR/PLAN_*`, `Z0_*` | stdlib | ✓ | P0 | evet (`ORNEK_3_SAHNE_ZANAAT` bozuk varyantları) |
| `plan_dili.py` | yeni | `gorunur_tarif(dil)`: EN istem cümleleri, TR kör paket metni, animatik eylem şeridi, çekim listesi | — | stdlib | ✓ | P0 | evet |
| `istem_derle.py` | yeni | `--hareket` (yönetmen), `--gorsel`, `--kart`, `--bitis` (görüntü), `--kapak`, `--yedek` (filtre-güvenli derlenmiş yedek istem; §5.1 kural 7); `aralik`/`sira` biçimi; istem özeti | SAHNELER, evren → istemler | stdlib | ✓ | P0 (`--hareket`) / P1 (görsel) | evet |
| `kamera_agaci.py` | yeni | plakalar → ana kareler → türevler → planlanmış görseller; ebeveyn değişince çocuklar bayat | → `KAMERA_AGACI.json` | stdlib | ✓ | P0 | evet |
| `cekim_listesi.py`, `plan_ozellik.py` | yeni | parti çekim listesi (A07c'de; A07d'nin girdisi); ders bağlamı alanları | — | stdlib | ✓ | P0 (`cekim_listesi`, [SON] S-3) / P1 (`plan_ozellik`) | evet |
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
| `saglayicilar/` genişletme | değişir | türler (D-41); `Kisitlandi.kod` (bilinmeyen kod geçiş yapmaz); `hazir()`, `birim_fiyat()`, `ortam`, `kredili`, `elle`; yeni sınıflar `gozlemci_claude_code`, `gemini_api` (gözlemci/izleyici/dinleyici/görsel; ücretsiz katmanda maliyet 0 → açık, ücretli yalnız izinle; kota dolunca `Kisitlandi(kota)`; D-19), `flow_gorsel`, `vertex_gorsel` (P2), `veo_vertex` (P2), `kaset`, `sahte_bozuk` | — | — | ✓ | P0 (arayüz + sahte) / P1 | evet |
| `saglayicilar/sahte.py` | değişir | 2 aday + yan dosya; `SAHTE_HATA` enjeksiyonu; adım pencerelerinde hareketli kutu videosu; yüz izi; ağız dizisi; replik penceresinde ton; sahte CapCut taslak fikstürü | — | — | ✓ | P0 | — |
| `renk_cila.py` | yeni (sahipsizdi) | sabit LUT + gren + halation (`dunya.json`); sahne içi Lab ΔE eşleme | klipler → işlenmiş klipler | ffmpeg | ✓ | P1 | evet |
| `buyut.py` | yeni | yalnız kullanılan pencereler; 2× yapay zekâ büyütme (ayrı ortam), sonra SFace denetimi; olmazsa Lanczos + gren | → `KURGU/surumler/v<N>/buyuk/` | büyütücü (Real-ESRGAN türü, BSD-3, bellekten; ağırlık lisansı doğrulanacak) | ayrı (CUDA) | P1 | evet (`sahte`: Lanczos) |
| `kontrol.py` | değişir | `_ADAYLAR/` desteği | — | — | ✓ | P1 | — |

### 6.6 Ses ve müzik ([SM2] §4.6 aynen; ekler işaretli)
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `ai84.py` | değişir | tembel anahtar okuma (import'ta `SystemExit` yok → `Kisitlandi("anahtar_yok")`); `voices()` sayfalama/süzgeç; `estimate()` | — | requests | ✓ | **P0 (PR-1)** | evet |
| `ses_plani.py` | yeni | `--profil-denetle`, `--taslak` (yol, efekt olayları, yatak + katmanlar, `flow_sound`, sessizlik), `--denetle` (S0), `ses_tanitim_kurali()` | → `_SES/SES_<S>.taslak.json`, `_RAPOR/S0_*` | stdlib | ✓ | P0 | evet |
| `muzik.py` | yeni (`gemini_muzik.py` ayrı araç olarak yazılmaz; işi `--gemini-paket`/`--gemini-al` alt komutlarıdır) | `--kagit` (S0), `--midi`, `--uret` (zincir; aday ölçümü), `--yerlestir` (olay çözümü, bar kesimi, kısma ≥ 12 dB), **kalite kapısı** (D-25; `dinleyici` yoksa ÖLÇÜLEMEDİ), zincir boşsa ipucu müziksiz + S6 BAYRAK; `--gemini-paket`/`--gemini-al` (zincirin elle son basamağı; yalnız lisans doğrulanınca) | `muzik_listesi.json` → `MUZIK/secilen/`, `KAYNAK_KAYDI.json` | mido (MIT), FluidSynth (LGPL, dış ikili; bellekten; KUR1'de kurulur, SF2 lisansı `LISANSLAR.json`'da) | ✓ | P0 (`--kagit`) / P1 | evet (`midi_ornek`, `sahte`) |
| `ses_sec.py` | yeni | `--telaffuz`, `--ara`, `--olc`, `--oku`, `--puanla`, `--sec`, `--banka`; `SES_SECIM.html` (bilgi) | profiller → evren `ses.json` | olcum | ✓ | P1 | evet |
| `ses_kiyas.py` | yeni | motor kıyası (Ö0-c ve SB3) | → `_RAPOR/S1b_motor_kiyas.json` | olcum | ✓ | P1 | evet |
| `ses_donustur.py` | yeni | `--ayristir`, `--hizala` (SC1 metin kapısı), `--donustur`, `--egit` (RVC; yalnız izinle) | klip → `SESLER/ayrik`, `hizalama`, `donusum` | audio-separator (MIT), stable-ts (MIT), faster-whisper (MIT); motorlar ayrı ortamda: OpenVoice V2 (MIT; geçişli bağımlılıklarında AGPL'li `whisper-timestamped` bulunabilir, bellekten, doğrulanacak: bulunursa o kod yolu kapatılır; D-36), Chatterbox (MIT), RVC (MIT) | ✓ / motor ayrı | P1 | evet |
| `ses_karar.py` | yeni | ses merdiveni (§2.2) | S2/S3 → kararlar, kuyruk, `replik_kabul` görevi | stdlib | ✓ | P1 | evet |
| `seslendir.py` | değişir (yönlendirici) | `--animatik`, `--parti N`; `diyalog.json` v2; [SM2] §4.6.1 kusurları kalkar (tepe normalleştirme, atempo 0,8–1,3, kelime sayısıyla cümle bölme, sessiz oransal yayma, sessizce Flow sesine düşme, 44,1 kHz → 48 kHz, `htdemucs` → RoFormer) | → `SESLER/*`, `_RAPOR/S2*` | — | ✓ | P1 | evet |
| `ses_kutuphanesi.py` | yeni | `--dizinle` (lisans, ölçüm, anlaşılır söz taraması), `--eksik --indir` (yalnız Freesound CC0; yalnız izinle), kara liste | → `DIZIN.json` | requests | ✓ | P1 | evet |
| `diyalog_esitle.py` | yeni (belgede var, pakette yok) | replik başına LUFS hedefi (`teslim` → seviye), oda yanıtı, uzaklık, iki yol arası tını eşleme | → `SESLER/esit/`, `_RAPOR/S4_*` | pyloudnorm, pyroomacoustics (MIT) | ✓ | P1 | evet |
| `ses_katmani.py` | yeni (belgede var, pakette yok) | `--cizelge T1\|T2`: tek yatak, çapraz geçiş, efekti klibin kendi ses başlangıcına oturtma, yaratık kiti, defterden nesne sesleri, Y/CY'de nefes ve kumaş katmanı (EÇ5) | → `SES_CIZELGESI.json`, stemler | — | ✓ | P1 | evet |
| `dudak_denetim.py` | yeni (belgede var, pakette yok) | S3: ofset/güven, konuşan yüz kimliği, ekran dışı replikte oynayan dudak; SyncNet isteğe bağlı | → `_RAPOR/S3_*` | olcum | ✓ | P1 | evet |
| `son_miks.py` | yeni (**tek miks kodu**) | stem toplama, kısma, tek doğrusal kazanç + 4× gerçek tepe sınırlayıcı, ölçüm; `--animatik`, `--onizleme`, `--final` (mux ya da yalnız ölçüm), `--shorts` | stemler → `YAYIN/ses_master.wav`, `_RAPOR/S7_*`, `S8_*` | ffmpeg, numpy | ✓ | P1 | evet |
| `saglayicilar/` ses sınıfları | yeni | `openvoice`, `chatterbox`, `rvc`, `roformer`, `faster_whisper`, `musetalk`, `acestep`, `midi_ornek`, `kutuphane` (çekirdek set KUR1), `gemini_muzik_paketi` (elle, son basamak), `ai84_vc` (P2), `dinleyici` | — | ayrı ortamlar: MuseTalk (Py 3.10 + torch 2.0.1; kod MIT, model "any purpose"), ACE-Step 1.5 (Py 3.11–3.12; MIT, ağırlık sayfası doğrulanacak) | ayrı | P1 | evet |
| `veri/ses_esikleri.json`, `testler/test_ses.py` | yeni | [SM2] §4.7 eşikleri; 18 bozuk girdi testi | — | — | ✓ | P0 | evet |
| MOS tahmincisi (UTMOS türü) | yeni | dönüşüm doğallığı: Ö0-c motor kıyasında doğallık ölçüsü, sonra S2'de BAYRAK (EK4-4; [SON] K-3) | wav → puan | kod ve ağırlık lisansı Ö0-c'den önce doğrulanır; doğrulanamazsa kullanılmaz, yerine `dinleyici` kör ikili | ayrı | **Ö0-c / P1** (P2'den çekildi) | evet |

### 6.7 Kurgu ([KU2] §4.6 aynen; ekler işaretli)
| Dosya | Yeni/değişir | Sorumluluk | Girdi → çıktı | Bağımlılık | Win/3.10 | Öncelik | Sahte test |
|---|---|---|---|---|---|---|---|
| `kirp_oner.py` | yeni | `kullanim` önerisi; adım eşleme; `--zincir` (Y55 penceresi); güven | klip + plan → kırpma | opencv, numpy | ✓ | P1 | evet (hareketli kutu ±2 kare) |
| `plan_kurgu.py` | yeni (belgede var, pakette yok) | T2: kırpma, senkron kuralıyla diyalog, ekran dışı replik, J/L, kartlar, örtü planları; ses görevlerini tetikler | → `KURGU_PLANI_T2_v<N>.json` | stdlib | ✓ | P1 | evet |
| `kurgu_uygula.py` | yeni | işlem listesi `--kuru` (SubagentStop'ta) / `--uygula`; kilitli alanlar; `*_iste` ve `yeniden_cek` kuyruklara | → yeni `KURGU_PLANI` sürümü | stdlib | ✓ | P1 | evet |
| `kurgu_denetim.py` | yeni | Z3; çizelge aritmetiği (S3.6, S3.8 dahil), Y31 ekleri, Y54/Y55, B9; komşuluk (dondurulmuş durum); `--kesme-simule`, `--hepsi` | → `_RAPOR/Z3_*`, `KESME_SIMULE_*` | stdlib | ✓ | P1 | evet |
| `kurgu_render.py` (+ `animatik.py` sarmalayıcı) | yeni | `--animatik` (Ken Burns + eylem şeridi + bitiş görseline geçiş + kartlar; yer tutucu), `--onizleme`, `--kesit`, `--yayin` (`yayin_kaynagi: master`), `--bilgi-paketi` (izle-dinle bilgi paketi: kesit, ses kadrosu örnekleri, ana tema, `dinleyici` yoksa motor örnekleri; D-24), `--otio` (P2); plan başına önbellek; stemleri `son_miks`'ten alır; `birlestir.py` **yazılmaz** (işini bu araç yapar) | → `ANIMATIK/`, `KURGU/onizleme_v<N>.mp4`, `KESIT/` | ffmpeg, Pillow | ✓ | P1 | evet (süre = çizelge ±1 kare) |
| `capcut_film.py` | değişir | `KURGU_PLANI`'ndan sürümlü taslak; `source_timerange` = `kullanim`; sürüm klasörü; Klipler sessiz; kanallar Bantlar, Kartlar, Altyazi, Diyalog, Efekt, Ambiyans, Muzik, NOTLAR; ekran başlığı `baslik`'tan bölünmeden (kalıplı YouTube başlığı okunmaz); `--yayin` NOTLAR ve Altyazi kanalı koymaz (SRT YouTube'a ayrı gider; [SON] S-6); 48 kHz; geçici akor yalnız müzik yoksa `GECICI` adıyla | → taslak + `son_capcut_projesi.json` v2 | pycapcut (`kullanici_araci`; lisansı P0'da doğrulanır, D-36) | ✓ | P1 | evet (fikstür) |
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
| `yayin_analiz.py` | yeni | 48 sa / 7 gün / 28 gün; tutma eğrisi → `KURGU_PLANI`; ders kaydı `gercek_seyirci`; erken uyarı; varsayılan girdi kullanıcının isteğe bağlı YouTube Studio CSV'si (OAuth kipi P2) | → `_RAPOR/YAYIN_ANALIZ_*` | stdlib (CSV); google-api-python-client (OAuth) | ✓ | P1 (CSV) / P2 (OAuth) | evet (CSV) |
| `youtube_yukle.py` | yeni | isteğe bağlı yükleme; her film için `YUKLE.bat` onayı | `PAKET.json` → yükleme | google-api-python-client | ✓ | P2 | evet (kuru) |
| `paketle.py` | değişir | anahtar sızıntı taraması + kaynak künyesi (`LISANSLAR.json`) | — | — | ✓ | P1 | evet |

### 6.9 Kurulum, `.bat` dosyaları, belgeler
| Dosya | Yeni/değişir | Sorumluluk | Öncelik |
|---|---|---|---|
| `kurulum.py` v2 | değişir | soru sormaz; her çalıştırmada önce `--veri-emniyet` ve `--yollar` (PR-0, PR-1); KUR1 (ana ortam, CPU torch, modeller bir kez indirilir sonra `HF_HUB_OFFLINE=1`; FluidSynth + SF2; müzik çekirdek seti sabit adres ve SHA-1 ile; D-25, D-37), KUR2/KUR3 (`--ses-ortamlari`, `--kur3`); Gemini ücretsiz anahtar dosyasının yalnız varlığı ve tarihi (içerik okunmaz) + veri kullanım koşulu bilgi notu (D-19); depo `.git` ile mi kurulmuş (ZIP'se `GUNCELLE.bat` kapalı, bilgi); `YOLLAR.json`, `FILM_AYAR.json` güvenli varsayılanlar; `settings.local.json` mutlak Python yolu; `.claude/bin/python_yolu.txt`; `claude --version` ≥ 2.1.302 kaydı; git ön koşulu; disk ölçümü (önbellek boyutları dahil); depodaki anahtar dosyalarının boş olduğunun denetimi; Telegram anahtar dosyasının yalnız tarihi; "çalışıyor/çalışmıyor" kartı; `LISANSLAR.json`'a göre "bilinmiyor" lisanslı bileşeni yalnız `--deneme` | P0 (KUR1) / P1 (KUR2, KUR3) |
| `bat_yenile.py` | yeni | `.bat`'ları üretir: ASCII + CRLF, `chcp 65001`, `cd /d "%~dp0"`, Python'u **ve betiği** mutlak yolla çağırır (`YOLLAR.json`; göreli `..\..\ARACLAR` yok, [SON] O-1), tek iş; Türkçe mesajı Python yazar | P0 (PR-2b) |
| `.bat` (depo kökü) | yeni | `FILM_SETI.bat` (Claude Code'u doğru klasörde açar), `KURULUM.bat`, `GUNCELLE.bat` (`git pull --ff-only`; yerel değişiklik ya da izlenmeyen çakışma görürse hiçbir şeyi taşımadan durur ve tek cümle bilgi verir; depo ZIP'ten kurulduysa kapalıdır ve bilgi verir; [SON] O-5), `FLOW_GIRIS.bat`, `IZINLER.bat` (izin paneli: gece Flow, dolar tavanı, Gemini ücretli, Flow kilitliyken Vertex, CC0 indirme, YouTube bağlantısı, yükleme, `onayli` kip; kullanıcının kendi isteğiyle), `UYARI_GECTI.bat`, `TELEGRAM_TEST.bat`, `GEMINI_TEST.bat` (anahtar dosyasını ve ücretsiz katmanı sınar; içerik yazdırılmaz), `YOUTUBE_BAGLA.bat` (P2) | P1 (`GUNCELLE.bat` P0, PR-2b) |
| `.bat` (film klasörü) | yeni | `DEVAM.bat` (`claude --continue "devam"`), `DURUM.bat`, `DURDUR.bat`, `VIDEO_YARI_OTOMATIK.bat`, `VIDEO_GECE.bat` (yalnız gece izni varsa çalışır), `VIDEO_TOPLA.bat`, `NOTLARI_OKU.bat`, `ARSIVLE.bat` (yalnız isteğe bağlı elle arşiv; arşivi sistem kendisi yapar, D-38), `YUKLE.bat` (P2), `FILM_DENEME_SAHTE.bat`; `KONTROL.bat` kalır | P1 |
| eski `.bat`'lar | taşınır | depoda: `MEMMET_BASLAT`, `MEMMET_SADECE_GORSEL`, `MEMMET_SADECE_VIDEO`, `CAPCUT_PROJESI_OLUSTUR`, `FILM_HATTI` ve film adı soran `YENI_FILM.bat` → `_ESKI/` (silinmez; kapıları atlıyorlardı); depodaki `BASLA_BURADAN.txt`'nin başına eski yolların emekli olduğunu söyleyen 3 satır; **veri kökünde** aynı iş `kurulum.py --veri-emniyet` ile (D-02, [SON] K-2) | **P0 (PR-0)** |
| `BASLA_BURADAN.txt` | yeniden yazılır | kullanıcı sözleşmesi kartı (§8.1), ilk kurulum adımları (`git clone`, özel depoda Git Credential Manager girişi, "ilk kurulum" yazma adımı, ücretsiz Gemini anahtarı, YouTube Studio CSV dışa aktarımı), `.bat` listesi, "yalnız konu sorulur" açıklaması, izinlerin varsayılanı, Flow uyarısında "sayfayı yenileme, GÖNDER'e basma" | P1 |
| `<veri>/BILGI/YOUTUBE_POLITIKA.md` | yeni | resmî kaynaklı politika özeti ve tarih (geliştirme oturumunda) | P1 |

### 6.10 Testler (ağ ve kredi yok; `sahte` + `kaset` sağlayıcıları)
`test_film.py` (v1 davranışı korunur; yalnız şimdi yasak olan iki beklenti güncellenir: `onay()`/`input()` testi görev defteri onayına, "kısıtlanan
sağlayıcıdan sonrakine geçer" testi `kota` koduna taşınır ve `olagandisi` kodu için "geçmez, kod 7" testi eklenir; `ORNEK_3_SAHNE` verisi değişmez) ·
`test_gorev_defteri` (30 kesme senaryosu + **tavan sonrası**: `kaset` ile bir planı her turda HATA veren fikstürde hat 6'da kalmaz, plan `durdu`
olur, rapor yazılır, film sonraki aşamaya geçer; [SON] K-4) · `test_asamalar` (her kapıda `tavan_sonrasi` ve her girdinin üreticisi dolu) ·
`test_kancalar` (+ 50 mesajlık soru seti; kanca içi hata → engelleyen çıkış) · `test_kor_paket` (sızıntı 0) · `test_hikaye` · `test_plan_dili`
(+ `ORNEK_3_SAHNE_ZANAAT` bozuk varyantları; §5.1'in kanonik örneği HATA'sız geçer, [SON] S-1) · `test_sureklilik` (K0, duygu, sahne ucu
uyuşmazlığı) · `test_g1_karar` · `test_v1` · `test_zincir` · `test_kart` · `test_evren` (yedek kuru çalıştırma, sha1 doğrulaması) · `test_ses`
(18 bozuk girdi) · `test_kurgu` (16 senaryo) · `test_memmet_korkuluk` (T10-elle, T10-gece, T10-dogrulama: uyarı ya da doğrulama fikstüründe
hazırlanan istem 0, sayfada işlem 0, ≤ 10 sn'de çıkış 7 ya da 2, `FLOW_KILIDI.json` var; boş `AYARLAR` ile açılışta tempo ≥ 17.10 değerleri;
`MEMMET_AYAR.json` daha hızlıysa yavaş olan; yeniden açılışta kalan mola `FLOW_TEMPO.json`'dan; `_surum: 2` → çıkış 4; [SON] K-1) ·
`test_flow_saglayici` (çıkış 7 → `Kisitlandi(kod="olagandisi")`, sağlayıcı geçişi 0; bilinmeyen kod → geçiş 0) · `test_veri_emniyet` (geçici veri
kökünde `memmet.py` doğrudan çağrılınca depo sürümü ya da emeklilik mesajı; yamasız Memmet'e giden `.bat`/`.ps1` 0; [SON] K-2) · `test_yollar`
([SON] O-1) · `test_izinler` (`sahte` Gemini: anahtar var + `usd_tavan_film: 0` → `dinleyici` çağrılır; anahtar yok → "ölçülemedi" + bilgi
paketi; Flow kilidi + izin yok → Vertex çağrısı 0; kilit + izin → Flow gönderimi 0, Vertex yalnız BUTK'dan; `FILM_AYAR`'daki güvenlik sınırı
sıkılaştırır, gevşetmez; [SON] K-3, O-10, O-15) · `test_arsivle` (bağlı yol ve açık kuyruk girdisi taşınmaz; `/MIR` yok) · `test_flow_yuk`
(haftalık kilit, hesap değişimi kilidi, mola sıfırlanmaz) · `test_adlar` · `test_uctan_uca_tam` (`ORNEK_3_SAHNE_TAM` + kaset; A00–A17 sahte) ·
`test_kuyruk` (0 kredi kuralı, soy sayacı) · `test_olcek`. CI: `windows-latest` + Python 3.10 + ffmpeg ve `ubuntu-latest`;
`test_uctan_uca_tam` ≤ 5 dk, bütün takım ≤ 10 dk.

## 7. Ölçülebilir kapılar ve eşikler

### 7.1 Eşik dosyaları ve kurallar
- **Dosyalar** (hepsi `esikler.py` ile yüklenir; aynı anahtar iki dosyada HATA): `ritim_esikleri.json` (RE; ZANAAT + plan dili + kurgu + seyirci),
  `veri/hikaye_esikleri.json` ([SN2] §4.7), `veri/sureklilik_esikleri.json` ([GS2] §4.7), `veri/ses_esikleri.json` ([SM2] §4.7),
  `veri/hat_esikleri.json` ([UM2] §4.7 + token + Ö0 + bütün sayısal güvenlik sınırları), `<veri>/BILGI/KURALLAR_OGRENILEN.json` (öğrenilen
  katman, yalnız korkuluk içinde). `FILM_AYAR.json` eşik dosyası değildir; içinde bir güvenlik sınırı bulunursa yalnız sıkılaştırır (D-34).
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
| **Z0** (plan dili, T0) | A07b–c · `plan_denetim`, `kroki`, `zaman_cizelgesi` | RE `eylem_adim_max` 3 (konuşma dahil bütün adımlar), `eylem_adim_konusmali_max` 1, `eylem_adim_min_sn` 1,5 (fiziksel adım), `eylem_adim_mikro_min_sn` 0,8 (mikro ve ses vuruşu; tahmin), diyalog süresi ≥ ZN §2.3 formülü − L/J taşması, `bitis_tutma_sn` 0,5, `kamera_hareketi_klip_max` 1, `plan_sure_aralik_sn`, `ayni_plan_tipi_ardisik_max` 4, `ayni_kamera_konumu_ardisik_max` 2, `olcek_kademe_min_fark` 2, `aci_min_fark_derece` 30, `sahne_konum_plani_max_sira` 3, `sahne_yeniden_konum_sn` 90, `plan_sayisi_tolerans_oran` 0,15, `sahne_max_sn` 180, `sahne_tipi_aralik`, `monolog_ardisik_plan_max` 3; [YN2] Y01–Y60 (yeni anahtarlar §7.3); `ifade_zorunlu_insanli_plan` | H/B (Y kuralının kendi kodu) | `_RAPOR/Z0_P<n>.json` |
| **Z1** (hikâye zamanları; TH, T0–T3) | A05, A07c, A12, A16 · `zaman_cizelgesi` | RE `ilk_eylem_max_sn` 5, `ilk_merak_max_sn` 20, `ilk30_manzara_plan_max` 1, `ilk30_manzara_sure_max_sn` 3,0, `baslik_karti_aralik_sn` [45, 120], `baslik_karti_sure_max_sn` 6, `vaat_imgesi_max_sn` 120, `kahraman_adi_max_sn` 120, `ad_ilk_gorunus_max_sahne` 2, `risk_sozlu_max_sn` 180, `parti_basi_risk_tazeleme_max_sn` 60, `parti_basi_kanca_donus_max_sn` 20, `seri_kancasi_max_sn` 20, `jenerik_max_sn` 60, `merak_olay_aralik_max_sn` 90, `acik_soru_aralik` [1, 5], `soru_omru_max_sn`, `seri_sorusu_max` 2, `cevap_yeni_soru_max_sn` 30, `kurulum_kullanim_min_sn` 20, `hatirlatma_esigi_sn` 600, `bilgi_tekrar_max` 2, `ironi_parti_min` 1, `ironi_sure_aralik_sn`, `sahne_yeni_ad_max` 2, `konusan_karakter_max` 8, `diyalog_yeni_bilgi_max_sn` 60, `gerilim_yeni_ayrinti_max_sn` 20, `bilgisiz_gecis_max_sn` 15, `geri_donus_max_sn` 20; hikâyede ±%15 belirsizlik bandı (bant dışı H, içi B) | H (#21, #23, #24, #28–32) / B | `_RAPOR/ZAMAN_<T>.json` |
| **Z2** (duygu ve enerji eğrisi) | A07c, A12, A16 · `zaman_cizelgesi` | RE `duygu_haritasi_40dk`, `yogunluk_sapma_max` 2 / `yogunluk_sapma_sure_max_sn` 60, `pencere_tepe_sn` 180 / `pencere_tepe_min` 6, `duz_cizgi_max_sn` 180, `ayni_duygu_ardisik_dk_max` 2, `tepe_esigi` 8, `tepe_oncesi_cukur_pencere_sn` [60, 120] / `tepe_oncesi_cukur_min_dusus` 2, `parti_sonu_yogunluk_min` 8, `doruk_yogunluk_min` 9, `en_karanlik_yogunluk_min` 6, `tepe_oncesi_asl_dusus_min` 0,25; `enerji_duz_max_sn` 180 (±%10 bant; T2 görüntü + ses + kesme, T1 yalnız ses); `seyirlik_an_parti_min` 2, `gosterisiz_aralik_max_sn` 360 | B / H (#39) | `_RAPOR/ZAMAN_<T>.json`, `EGRI_<T>.png` |
| **Z3** (kurgu) | A16 · `kurgu_denetim` | RE `film_sure_aralik_sn` [1800, 2700], `parti_sure_oran_aralik` [0,30, 0,35], `vurus_oranlari` ±`vurus_oran_tolerans` 0,04, `asl_film_aralik_sn` [4,2, 5,2], `asl_parti_hedef_sn` ±`asl_parti_tolerans_sn` 0,6, `ilk120_asl_max_sn` 4,0, `ilk30_asl_max_sn` 3,5, `tepki_orani_min` 0,25, `jl_kesme_orani_min` 0,30, `j_kesme_aralik_sn`, `l_kesme_aralik_sn`, `replik_sonu_kesme_sn`, `cevap_boslugu_sn` [0,2, 0,6], `kullanim_bas_min_sn` 0,3, `kullanim_son_pay_sn` 0,5, `olu_sure_max_sn` 0,6, `kesme_ilk_duragan_yasak_sn` 0,3, `klip_bolme_atlama_min_sn` 0,4, `klip_bolme_min_kullanilabilir_sn` 6,0, `bakis_tutma_min_sn` 0,5, `eslesme_gecis_orani_min` 0,15, `sert_kesme_parti_max` 4, `duygu_tutma_film_max` 25, `duygu_tutma_ardisik_max` 1; `senkron_tolerans_kare` 1; L/J ekleri (`l_kesme_*`, `j_kesme_klip_kosulu`); B9 (dudağı oynayan yüze başka replik) 0; Y54/Y55; geri gidiş 0; render = çizelge ±1 kare | H/B | `_RAPOR/Z3_v<N>.json` |
| **K0** (kâğıt süreklilik) | A07c · `dunya_defteri` | [GS2] K0.1–K0.19 (olgu sıçraması, el/nesne, kostüm, sahne ucu eşitliği, görüş hattı, 180°, bakış, ışık, kart kapsamı) + `duygu_sicramasi_gerekcesiz` 0 (B) | H/B | `_RAPOR/K0_FILM.json` |
| **KART** | A10d · `kart_denetim`, `kare_denetim` | [GS2] kart kapısı: yüz sayısı = görünüm sayısı; SFace öz tutarlılık ≥ 0,45; kadro ötekilerine < 0,363 (hedef < 0,25); foto/çizim (CLIP); düz fon; plakada kişi/yüz 0; NE YOK 0; hikâyeye bağlı öğe uyuşmazlığı 0; yaratıkta ≥ 3 asimetrik işaret (tahmin; [ESY] EO5) | H/B | `_RAPOR/KART_KAPISI.json` |
| **G1** | A11 · `olcum` → `kare-tarifcisi` → `kare_denetim --karar` → hakem | [GS2] G1 tablosu: 16:9 ±%1, kısa kenar ≥ 720; YuNet ≥ 0,9 ve yüz ≥ 48 px; SFace GEÇ ≥ 0,45, HATA < 0,363 (`gevsetilemez`), fark payı ≥ 0,05; fazla yüz H, eksik yüz B; kadraj sırası H; yaw > 15° H; el–nesne iki kaynak H / tek B; ağız kapalı jawOpen ≤ 0,15 (konuşan planda) B; konuşan yüz ≥ %12 ve \|yaw\| ≤ 45° B; açık parmak B (kalibrasyon ≥ %90 → H); yaratık DINOv2 < 0,5 B (kalibrasyonla H); ölçek ±%35 B; mekân < 0,60 B; ışık B; Lab ΔE > 10 B; stil < 0,5 + kör "çizim" H; yazı/logo H; yasak öğe H; keskinlik < 0,5 B; kör iki cevap uyuşmazlığı B; **ifade uyumu** B (`ifade_uyum_min_oran` ≥ 0,85, film düzeyi); 2 aday × ≤ 2 düzeltme turu | H/B | `_RAPOR/G1_P<n>_B<k>.json` |
| **G1Z** (zincir karesi) | A14 · `kare_zinciri --cikar` | kimlik bantları (G1 ile aynı); keskinlik ≥ 0,6 × A'nın ilk karesi B; V3 gözlemi ±0,2 sn H; kişi sayısı H; B'nin planlanmış görseline DINOv2 < 0,70 B; `zincir_cikis_tutma_ic_min_sn` 0,2; `zincir_derinlik_max` 2 | H/B | `_RAPOR/G1Z_*` |
| **K1ON / K1** | A11 sonu / A16 · `video_denetim --onceden / --gecis` | `devam` DINOv2 < 0,80 H, parlaklık > 12/255 B; aynı mekân kesmesi Lab ΔE > 10 / parlaklık > 20/255 B; kurulum dönüşü ana kareye < 0,70 B; kostüm < 0,6 B; dondurulmuş olgu eşitliği H (kullanıcı kararında B). Bulgular seyirciye verilmez | H/B | `_RAPOR/K1ON_P<n>.json`, `K1_v<N>.json` |
| **V1** | her indirme · `kalite_denetim --klip` | `blackdetect d=0.1 pic_th=0.98 pix_th=0.10`, `freezedetect n=-60dB d=1.0`, `blurdetect`, PySceneDetect ContentDetector(27), titreme MAE; süre ≥ 7,5 sn (kesik indirme); kusur kullanılan pencerenin dışındaysa `cozum: kirp` (madde açılmaz) | H/B | `_RAPOR/V1_B<k>.json` |
| **V2** | blok arası · `video_denetim --klip` | 17 kare / 0,5 sn: kimlik düşüşü > 0,15 ve < 0,363 H; yüz/kişi sayısı değişimi H; DINOv2 sıçraması > 0,15 B; ekran yönü H; ilk kare sadakati < 0,85 B; **hareket hızı** `beklenen_hiz` dışında B (EO4); yüz izi `V2_P<n>/NNN_yuz.jsonl` | H/B | `_RAPOR/V2_*` |
| **V3** | blok arası · `video_denetim --klip` + `kare-tarifcisi·v3` | kesme anındaki kare kör gözlemi ↔ `bitis_durumu` kritik olguları H; adım enerji tepesi sapması ≤ 1,0 sn (`plan_zincir_zaman_sapma_max_sn`) B; dirsek > 140° B; son 0,5 sn MAE ≤ medyanın %50'si B; replik ortası ve sonunda ifade uyumu B | H/B | `_RAPOR/V3_*` |
| **S0–S8** (ses) | A06s, A08 (S0); A10 (S1); A14–A15 (S2, S2m); A16 (S3–S7); A17 (S8) · ses araçları | [SM2] §4.7.1–4.7.8 aynen (S0.1–S0.21, S1.1–S1.12, S2.1–S2.16, S3.1–S3.8, S4.1–S4.5, S5.1–S5.11, S6.1–S6.10, S7.1–S7.9, S8.1–S8.2); RE eşleri: `diyalog_lufs` {fısıltı −24, yumuşak −21,5, normal −19,5, bağırma −17} ±`diyalog_lufs_tolerans` 1, `ambiyans_diyalog_alti_db` [12, 18], `efekt_diyalog_alti_db` [3, 10], `muzik_diyalog_alti_min_db` 12, `muzik_diyalogsuz_lufs` [−20, −16], `final_lufs` −14 ±`final_lufs_tolerans` 1, `true_peak_max_dbtp` −1, `ambiyans_sahne_ici_fark_max_lu` 3, `ambiyans_capraz_gecis_sn`, `ses_koprusu_sn`, `mutlak_sessizlik_db` −50 / `_max_sn` 1,0 / `_film_max` 2, `vurgu_sessizlik_sn`, `muzik_kaplama_oran` [0,40, 0,65], `muziksiz_blok_max_sn` 240, `muzikli_blok_max_sn` 300, `muzik_giris_sn`, `muzik_cikis_sn`, `leitmotif_donus_min` 3, `konusma_hizi_kelime_sn` 2,5; S3.6 ve S3.8 ölçümü `kurgu_denetim`'de (D-32); ek: `muzik_kalite_ikili_min` ≥ 0,5 B (`dinleyici` yoksa ÖLÇÜLEMEDİ = B, açık eksik), `ses_dogallik_mos_min` B (Ö0-c'de motor seçimi, sonra S2; tahmin) | H/B | `_RAPOR/S<n>_*` |
| **HS_KAGIT, HS_PLAN, HS_ANIMATIK, HS_KESIT, HS_KURGU** | A06, A07e, A12, A14a, A16 · `seyirci_topla` | **Kapı:** `seyirci_kapi_genel_min` 7, RE `kopukluk_kritik_max` 0, `ozet_eslesme_kritik_min` 0,80. **Hedef:** RE `seyirci_genel_esik` 8, `seyirci_olcut_min` 7, `seyirci_olcut_hedef`, `kopukluk_orta_max_parti` 3, `ozet_eslesme_min` 0,80, `ilk2dk_devam_evet_min` 3. RE `seyirci_sayisi` 3, `seyirci_karar` medyan, `sikilma_ortak_isaret_min` 2, `kagit_tur_max` 4, `kurgu_tur_max` 3, `kesme_turu_oneri` {10 plan, 2 sahne, uygulama ≥ 0,5; payda simülasyondan HATA'sız geçenler}; `plato_genel_artis_min` max(0,5; `seyirci_gurultu_std`); `ilgi_korelasyon_min` 0,5 B; `parca_konum_egim_bayrak` −0,15 B; `gorsel_tasima_orani_min` 0,5 B | H (kapı) / hedef | `_RAPOR/HS_*`, `SEYIRCI_KARAR_*` |
| **HS_KAPAK** | A11 · `habersiz-seyirci·kapak` + `kare-tarifcisi·kapak` | `kapak_aday_min` 8; `kapak_kucuk_okunurluk` (168×94'te yüz ve yaratık seçiliyor) H; anatomi/yazı/kimlik H; ikili karşılaştırma kazananı | H/B | `_RAPOR/KAPAK_*` |
| **BUT0 / BUT1 / BUT2 / BUTK** | A01 / A07c / A13 / her kredili madde · `kredi.py` | `kapi_payi` 0,30; `kredi_yeniden_deneme_payi` (RE) 0,20 hedef; dilimler `yeniden_pay_dilim` {görüntü 0,15, ses 0,07, kurgu 0,08}; `take_payi_kredi` 720; `guvenlik_payi` 0,10 (BUT2: tahmin ≤ bakiye × 0,9 ve ≤ tavan); `kredi_klip_720p` (RE) 12; `plan_basi_yeniden_cekim_max` 2 (soy toplam 3); AI84 tavanları 60.000 / 40.000 / 20.000; `usd_tavan_film` 0 | H | `_RAPOR/BUT*_FILM.json` |
| **FLOW** (yük) | her gönderim · `flow_yuk`, Memmet (hepsi `hat_esikleri.json`'da, `gevsetilemez`) | gece 12–30 sn, aynı anda 2, iki partide bir 15–30 dk mola; gündüz 6–15 sn; 8 gönderimde 3–6 dk mola (17.10; `gevsetilemez`); `gorsel_gunluk_tavan` 20 (tahmin); `gorsel_sonrasi_video_saat` 12 (tahmin); `haftalik_uyari_kilidi_gun` 7 (tahmin); `uyari_sonrasi_bekleme_dk` 30; uyarıda **her kipte** yeni gönderim ve sayfa işlemi 0, ≤ 10 sn'de dur; doğrulama ve reCAPTCHA'da dur (çıkış 2); hesap değişimi kilidi 14 gün (tahmin); Ö0-b merdiveni 10/15/20 (tahmin) | H | `HESAP/FLOW_*`, `_memmet_cikis.json` |
| **PILOT / KESIT** | A14a · `blok_plani --kesit`, kapılar | kapsama listesi (D-17); kesit seyircisinde KRİTİK 0; teknik kapılar HATA 0; take kararı `take_ikinci_secim_min_oran` 0,30 (tahmin); canlı bekleme `canli_bekleme_ab_fark_max` 0,02 | H/B | `_RAPOR/PILOT_FILM.json` |
| **YAYIN** | A17 · `kalite_denetim --final`, `yayin_paketi` | final −14 ±1 LUFS, ≤ −1 dBTP; siyah/donma/planlanmamış sessizlik 0; `mux_ofset_max_kare` 1, `mux_korelasyon_min` 0,9, `mux_pencere` 40 × 10 sn; `yayin_sure_tolerans_kare` 1; başlık ≤ 100 kr; bölüm adı kuralları (RE `bolum_sayisi_max` 8); `yz_beyani` dolu; Shorts −14 ±1 LUFS | H | `_RAPOR/YAYIN_*` |
| **HAT** | A13, pilot sonrası, kuyruk > 30 klip, dilim aktarımı · `hat-denetcisi` | `hat_denetcisi_kuyruk_esigi` 30 | GİT/GİTME | `_RAPOR/HAT_*` |
| **DISK / TOKEN** | her aşama başı · `film.py` | `disk_bos_min_gb` 20 (tahmin; altında `arsivle` kendiliğinden); `gorev_tavani_carpan` 1,5 (tahmin); `stop_ardisik_max` 8; `film_token_tavan` (Ö0-f projeksiyonu × 1,5; tahmin; §1.5) | 8 BEKLE | `FILM_DURUM` |

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
| `eylem_adim_mikro_min_sn` | 0,8 (`mikro` ve `ses_vurusu` adımı) | H | [SON] S-1 (tahmin); `eylem_adim_min_sn` 1,5 yalnız fiziksel adım |
| `diyalog_sure_tasma_dus` | evet (`sure_sn ≥ ZN §2.3 formülü − ses_tasma_sn`) | H | [SON] S-1 (belge: ZN §2.3 + §3.4 L kesme) |

`hikaye_esikleri.json` ([SN2] §4.7 listesi aynen: sahne sayısı 45–55, replik kelimesi 2.100–2.600 (40 dk), anahtar olgu 8–12/parti, ad kuralları, jüri
kazanan ≥ 8,0, doktor tetiği, kopru replik ≤ 1 vb.), `sureklilik_esikleri.json` ([GS2] §4.7 aynen), `ses_esikleri.json` ([SM2] §4.7 aynen),
`hat_esikleri.json` ([UM2] §4.7 aynen + `gorev_tavani_carpan`, `stop_ardisik_max`, `film_token_tavan` (tahmin; §1.5), `disk_bos_min_gb`,
`haftalik_uyari_kilidi_gun`, `hesap_degisim_kilidi_gun`, `seyirci_gurultu_std` (Ö0-f yazar), `olculen_gunluk_kapasite` (Ö0-b yazar); FILM_AYAR'dan
taşınan güvenlik sınırları, hepsi `gevsetilemez: true`: `flow_tempo_1710` {gece, gündüz, ara mola, blok molası}, `flow_gorsel_gunluk_tavan` 20,
`flow_gorsel_sonrasi_video_saat` 12, `kapi_payi` 0,30, `take_payi_kredi` 720, `guvenlik_payi` 0,10, `flow_model` "omni-1.1-flash" (model değişimi
uyarı getirir, BK §8 #3), `flow_cozunurluk_min` 720p (BK §8 #1), `klip_sn_varsayilan` 8, `ajan_paralel_max` 5; tavan sonrası ve Ö0 sayıları:
`hata_donus_max` 3, `o0b_gun_tavanlari` [10, 15, 20], `o0b_uyari_sonrasi_ara_gun` 7, `ab_kol_min_ornek` 12, `kesit_sistematik_plan_min` 3,
`kota_bekle_max_sa` 24, `bekle_azami_dk` 110 (hepsi tahmin; [SON] K-4, O-3, O-4)).

### 7.4 Başarı ölçütleri (film düzeyi; `FILM_SONU_RAPORU.md` yazar)
| # | Ölçüt | Hedef | Kaynak |
|---|---|---|---|
| M1 | Kullanıcıya sorulan karar sorusu | 1 (yalnız konu) | KK1 |
| M2 | Kullanıcının el işi | sayısı ve saati baştan yazıldı; gerçekleşen ölçüldü | D-06 |
| M3 | Kapısız kredi harcaması / çift harcama | 0 / 0 | [UM2] |
| M4 | Flow uyarısından sonra yeni gönderim ve sayfa işlemi (her kipte) | 0; ≤ 10 sn'de dur; Ö0-b'de ikinci uyarı 0 | KK5 |
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
| M15 | Gerçek seyirci verisi (yayın sonrası) | tutma eğrisi plan kimliğiyle defterde (CSV verildiyse ya da bağlantı varsa) | D-24 |
| M16 | Tavan sonrası merdiveni | `durdu` plan sayısı, `hedef_alti` maddeleri ve kalan KRİTİK'ler açık eksik raporunda %100; 6 KAPI yalnız kâğıt ürün ya da feragat edilemez HATA'da | §1.5 |
| M17 | Ölçülemeyen kalite kapıları (kulak, göz, doğallık) | her biri açık eksik olarak raporda ve izle-dinle paketinde; sessizce GEÇ sayılan 0 | D-19, D-25 |

## 8. Kullanıcının yapacakları

### 8.1 Kullanıcı sözleşmesi kartı (`BASLA_BURADAN.txt`'nin başı ve kurulum sonu ekranı; sayıları `olcek.py` doldurur)
```
SENDEN İSTENEN TEK KARAR: filmin konusu (bir cümle). Gerisini ekip karar verir; sana "hangisi?" diye sorulmaz.
SENDEN İSTENEN FİZİKSEL İŞLER (bu film için tahmini; film başında güncellenir):
  • Flow'a Google ile giriş ve gerekirse "ben robot değilim" doğrulaması ............ kurulumda 1 kez + istendikçe
  • Ücretsiz Gemini anahtarı almak ve AYARLAR'a koymak (filmi yayından önce bir "kulak"
    dinlesin diye; para yok, soru değil) ................................................ kurulumda 1 kez (≈ 5–10 dk, tahmin)
  • İlk kurulum ölçümü: 3 günde ≈ 10 / 15 / 20 video için GÖNDER (eski B3 planlarıyla
    ölçüm; ≤ {olcum_kredi} kredi) ......................................................... yalnız ilk filmden önce
  • Gemini paketlerini taşımak (klasörü Gemini'ye ver, gelen ZIP'i GELENLER'e at) ..... ≈ {paket} paket (Gemini API bağlıysa 0)
  • Video oturumları: VIDEO_YARI_OTOMATIK.bat'ı aç, Memmet hazırlayınca GÖNDER'e bas .. ≈ {gonder} kez, ≈ {video_gun} gün, günde ≈ {saat} saat
  • CapCut'ı kapatıp açmak (taslak güncellenince) ve sonunda 4K 24 fps dışa aktarmak .. ≈ 2–4 kez + 1 dışa aktarım
  • Gemini müzik paketi (yalnız kütüphane yetmezse ve Gemini koşulları uygunsa) ....... ≈ {muzik_paket} paket (çoğu filmde 0)
  • D diskini takmak (arşiv ve yedek için, sistem isterse) ............................ ≈ {d_tak} kez
  • [{uyandirma_yok} ise] her işten sonra sohbete "tamam" yazmak ....................... ≈ {tamam} kez
  • Flow uyarı verirse: GÖNDER'e BASMA, sayfayı YENİLEME; beklemek, en erken 30 dk
    sonra elle 1 video denemek, UYARI_GECTI.bat ......................................... yalnız uyarı olursa
  • Kredi biterse yüklemek ............................................................ yalnız gerekirse
TAHMİNİ TOPLAM EL İŞİ: ≈ {el_isi_saat} saat · TAHMİNİ TAKVİM: ≈ {takvim_gun} gün (Flow'un günlük güvenli kapasitesine bağlı)
İSTERSEN (hiçbiri zorunlu değil, sistem beklemez): film hakkında not bırakmak (CapCut NOTLAR ya da sohbet), izinleri açmak (IZINLER.bat:
gece çalışma, dolar harcama, Gemini'nin ücretli kullanımı, Flow kilitliyken Vertex, efekt indirme, YouTube bağlantısı, yükleme), kanal verisini
YouTube Studio'dan CSV olarak vermek (adımlar bu dosyada).
SİSTEM ASLA: Flow uyarısını atlatmaz, hızlandırmaz, sayfayı yenilemez, başka hesaba geçmez; anahtarlarını okumaz ya da yazdırmaz; dosya silmez
(eski dosyaları _ESKI'ye taşır).
```
Gerçekleşen el işi `FILM_SONU_RAPORU.md`'de tahminle karşılaştırılır (D-06, [SA] K-2 #3).

### 8.2 Bir kez (kurulum)
| Adım | Kullanıcının yaptığı | Sistemin yaptığı | Ne zaman çağrılır |
|---|---|---|---|
| 0 | Depoyu **`git clone`** ile `Desktop\YZ_FILM_SET`'e indirir (tek komut `BASLA_BURADAN.txt`'de yazılı; git yoksa önce git'i kurar; depo özelse açılan Git Credential Manager penceresinde GitHub'a girer); veri klasörü `Desktop\YZ_FILM` olduğu gibi kalır. ZIP ile kurulumda `.git` olmadığından `GUNCELLE.bat` çalışmaz ve bunu söyler ([SON] O-5) | — | ilk kez, bir defa |
| 0b | **Tek seferlik geliştirici adımı:** Claude masaüstü uygulamasında Code sekmesini `Desktop\YZ_FILM_SET` klasöründe açar ve yalnız `ilk kurulum` yazar (beceriler geldikten sonra aynı iş `/film-gelistir ilk-kurulum`); oturum açık kalır, istenen fiziksel işleri yapar | `kurulum.py --yollar` (`YOLLAR.json`) → `kurulum.py --veri-emniyet` (eski Memmet ve `.bat`'lar `_ESKI/`'ye; taşınanların listesi bilgi; D-02) → memmet3 aktarımı (PR-0 yaması, T10, `esitle --gelistirme`; §4.5) → Ö0-a ölçümü | §9 adım 2; PR-0 ve PR-1 birleşince |
| 1 | `KURULUM.bat`'a çift tıklar | KUR1 kurulumu (ana Python 3.10 ortamı, CPU torch, modeller, FluidSynth + SF2, müzik çekirdek seti), her seferinde veri kökü emniyeti, `YOLLAR.json`, güvenli `FILM_AYAR.json`, `settings.local.json`, sürüm ve disk ölçümü, "çalışıyor/çalışmıyor" kartı; soru sormaz | adım 4 (PR-2b) birleşince |
| 2 | (gerekirse) git kurar | git yoksa kurulum raporu tek cümleyle ne yapılacağını söyler | kurulum raporunda |
| 3 | `FLOW_GIRIS.bat` ile Flow'a Google'la girer | oturumu Memmet profilinde (`<veri>/AYARLAR/memmet_profil`) saklar; hesap kimliğinin yalnız sha1'ini kaydeder | kurulumda ve oturum düşünce |
| 3b | **Ücretsiz Gemini anahtarı:** Google AI Studio'da (faturalandırma açmadan) bir API anahtarı alır ve `<veri>/AYARLAR/gemini_anahtar.txt`'nin ilk satırına yapıştırır, `GEMINI_TEST.bat`'a çift tıklar (fiziksel iş; soru değil; [SON] K-3) | dosyanın yalnız varlığını ve tarihini denetler, içeriği yazdırmaz; ücretsiz katmanı ve video/ses girişini Ö0-e'de sınar; ücretsiz katmanın veri kullanım koşulunu (bellekten, doğrulanacak) bir kez bilgi olarak söyler; anahtar varsa `izleyici` ve `dinleyici` açılır (D-19) | kurulumda, bir kez |
| 4 | (isteğe bağlı) Telegram bot anahtarını `<veri>/AYARLAR/telegram_bot.txt`'ye yazar, `TELEGRAM_TEST.bat` | dosyanın yalnız varlığını ve tarihini denetler, içeriği okumaz | — |
| 5 | (isteğe bağlı) YouTube Studio'dan kanal verisini CSV olarak dışa aktarır ve `<veri>/GELENLER/KANAL/`'a koyar (adımlar `BASLA_BURADAN.txt`'de; OAuth bağlantısı P2) | Ö0-g kanal teşhisi; yayından sonra (yine isteğe bağlı CSV ile) analiz | — |
| 6 | Ö0 ölçüm turunda: 3 günde ≈ 10 / 15 / 20 videoluk oturum (GÖNDER; ilk uyarıda biter), 1 Gemini paketi, CapCut'ı bir kez kapatıp açmak | Ö0-1 ve Ö0-2 ölçümleri ve `OLCUM0.json` (§1.2) | ilk filmin kâğıt aşamalarıyla paralel; her iş Telegram'la bildirilir |
| 7 | (gerekirse) KUR2/KUR3 için ek Python kurulumuna izin veren Windows penceresini onaylar | ses dönüştürme, MuseTalk, ACE-Step, büyütücü ortamları (yalnız gerektiğinde) | A10a'da |

### 8.3 Her film
| Ne zaman | Kullanıcının yaptığı | Sistemin mesajı (bilgi; soru değil) | Kanal |
|---|---|---|---|
| A00 | konuyu bir cümleyle söyler (ya da "sen seç") | — | sohbet |
| A01 sonu | — | "Konu kartı hazır: <tür, kanca>. Süre: 30 dk (Flow kapasitesi henüz ölçülmedi). Kâğıt aşaması ≈ {kagit_gun} gün." (sayılar `olcek.py`'den) | sohbet + Telegram |
| A06 sonu | — | "Senaryo kilitlendi: '<başlık>'. Seyirci puanı 8/8/9. Şimdi yönetmen planları." (hedefin altındaysa açıkça yazar) | sohbet + Telegram |
| A10d, A11 (her paket) | Gemini paketini taşır | "Gemini paketi 3/12 hazır: Masaüstü\GEMINI GORSEL ISTEM\<FILM>_K2_03 klasörünü Gemini'ye ver, gelen ZIP'i GELENLER'e at." Arka plandaki `film.py bekle --kullanici` ZIP'i yoklar; ZIP gelince oturum kendiliğinden sürer, 6 saat sonra 1 hatırlatma (uyandırma tutmazsa mesajın sonu "Bitince sohbete 'tamam' yaz" olur; §4.2) | sohbet + Telegram |
| A12 sonu | (isteğe bağlı) animatik paketini izler | "Animatik geçti (8/7/8). İzle-dinle paketi masaüstünde: <yol>. Not bırakırsan işlerim; bırakmazsan devam ediyorum." | Telegram (dosya) + masaüstü |
| A13 | — | "Video için ≈ {kredi} kredi gerekiyor; hesapta {bakiye} var. Takvim ≈ {video_gun} video günü." (örnek değerler `olcek.py`'den) | sohbet + Telegram |
| A14a, A14 (her blok) | `VIDEO_YARI_OTOMATIK.bat`'ı açar, Memmet hazırladıkça GÖNDER'e basar | "Blok 7/21 hazır (20 plan). VIDEO_YARI_OTOMATIK.bat'ı aç; Memmet her planı hazırlayınca GÖNDER'e bas." | Telegram |
| A14a sonu | (isteğe bağlı) dikey kesiti izler | "Filmin ilk 3 dakikası yayın kalitesinde hazır: <yol>. Kalan videolar bundan sonra çekilecek." | Telegram (dosya) + masaüstü |
| A16 sonu | CapCut'ı kapatıp açar; isterse izler ve not bırakır | "Taslak hazır: CapCut'ı kapatıp aç; 'YZ <FILM> v3' en üstte. İstersen izleyip not bırak, istersen doğrudan dışa aktar." Kurgu tavanı dolup KRİTİK kaldıysa aynı mesajda açık eksik listesi: "Şu 2 yer hâlâ kopuk: 14:20, 31:05 (FILM_SONU_RAPORU)" (§1.5 kural 8) | sohbet + Telegram |
| A16n | not bırakır ya da CapCut'ta düzenler (isteğe bağlı) | "Notlarını aldım: 6 not → 5 düzeltme, 1 bilgi. Düzeltilmiş taslak: '<senin taslağın> · v4'. Kendi taslağına dokunmadım." | sohbet |
| A17 | CapCut'tan 4K 24 fps dışa aktarır, dosyayı `YAYIN/`'a koyar | "Yayın taslağı hazır (NOTLAR'sız). Dışa aktarıp YAYIN klasörüne koy; gerisini ben denetlerim." Sonra: "Kapak, YouTube metinleri, fragman ve 3 Short YAYIN/'da." | sohbet + Telegram |
| A17y | (isteğe bağlı) `YUKLE.bat` | yalnız o film için onay; yükleme kaydı | — |
| A18a | — | "Yayından 48 saat sonra: tıklama oranı %X, ilk 30 sn tutma %Y. Kapak değişikliği önerisi: …" (yalnız bağlantı varsa) | Telegram |

### 8.4 Kısıt durumlarında
| Durum | Sistem | Kullanıcı | Kanal |
|---|---|---|---|
| Flow "olağan dışı etkinlik" | **her kipte** (`elle` dahil) ≤ 10 sn'de durur; sayfada başka işlem yapmaz (yenileme, tıklama, yazma yok); bekleyenleri sonradan `memmet_topla` gönderim yapmadan toplar; `FLOW_KILIDI.json`; kod 7; aynı hafta ikinci uyarıda 7 gün kilit; Vertex'e kendiliğinden geçmez (D-03) | GÖNDER'e basmaz, sayfayı yenilemez; bekler; en erken 30 dk sonra Flow'da **elle** 1 video dener; başarılıysa `UYARI_GECTI.bat` (yalnız o gün geçerli; o günün kalanında tempo ×1,5 yavaş, ertesi gün ilk blok elle) | **ACİL** Telegram + sohbet |
| reCAPTCHA / doğrulama / oturum düştü | Memmet beklemez ve kendiliğinden sürmez: bildirir, kod 2 (PR-0; bugünkü kodun 12 saat bekleyip sürmesi kalktı, [SON] S-11) | doğrulamayı Memmet'in açık Chrome penceresinde çözer (ya da `FLOW_GIRIS.bat`); `VIDEO_*.bat`'ı yeniden açar; tempo ve mola `FLOW_TEMPO.json`'dan sürer | ACİL |
| Kredi bitti / bütçe yetmiyor | 5 BÜTÇE; "X kredi gerekiyor"; kalite düşürülmez | isterse kredi yükler; arka plandaki `film.py bekle --kullanici` bakiyeyi yoklar ve sistem kendisi sürer (uyandırma tutmazsa "tamam" yazar) | ACİL |
| Claude kullanım sınırı / görev tavanı | 8 BEKLE + `TOKEN_PROJEKSIYON.md` | sınır açılınca `DEVAM.bat` ya da sohbette "devam" | BİLGİ |
| Disk dolu | `arsivle` kendiliğinden (D-38); D takılı değilse 8 BEKLE + "D'yi tak"; `bekle` diski yoklar, takılınca sürer | yalnız D'yi takar | BİLGİ |
| Flow kilidi uzun sürer (R1) | video bekler; kâğıt ve yerel işler sürer; Vertex yalnız `izinler.flow_kilitliyken_vertex` + `usd_tavan_film > 0` ile ve bütçe noktasından | isterse `IZINLER.bat` ile izin ve dolar tavanı verir | BİLGİ |
| Kapı merdiveni tükendi | kâğıt aşamasında kâğıt ürün + "yüzüne vur" raporu, videoya geçilmez (6 KAPI); öbür kapılarda §1.5 tavan sonrası merdiveni hattı sürdürür, kalan eksikler açık raporda | — (isterse yeni konu söyler; kesin istek olarak işlenir) | ACİL |
| Flow arayüzü değişti | `memmet-bakimci` aday yaması + korkuluk testi; onarımdan sonra ilk blok elle | — | BİLGİ |

**Bildirim kuralları** ([UM2] `bildirim.py`): olaylar `kisit_olagandisi` (ACİL), `dogrulama` (ACİL), `butce` (ACİL), `kapi_tukendi` (ACİL),
`kullanici_isi` (BİLGİ, 6 saat sonra 1 hatırlatma), `blok_hazir`, `bilgi_paketi`, `asama_bitti`, `oturum_ozeti`, `sinir_doldu`, `disk`, `hata`;
aynı olay 30 dk içinde tekrar edilmez, saatte ≤ 12 mesaj; mesajda gizli bilgi, anahtar, hesap e-postası yoktur; Telegram kapalıysa masaüstü bildirimi ve
`FILM_KAYIT.txt`. Telegram'dan gelen komutlar (`/durum`, `/dur`) P2'dir.

### 8.5 Kullanıcının hiç yapmadığı (ekibin kararları)
Senaryo onayı · karakter ve mekân görünüşü onayı · ses kadrosu seçimi · müzik seçimi · plan, animatik ya da kurgu onayı · kapak ve başlık seçimi ·
yeniden çekim kararı · süre kararı · sağlayıcı seçimi. Hepsi `KARAR_DEFTERI.md`'de gerekçesiyle durur; kullanıcı `film-durum` ile sorabilir, `film-not` ile
itiraz edebilir (itiraz kesin istek olur). `--onayli` kipi (CLAUDE.md "isterse onay noktaları") varsayılan kapalıdır ve yalnız kullanıcı kendisi
`IZINLER.bat` ile açarsa vardır (`FILM_AYAR.mod: onayli`); o kipte animatik, dikey kesit ve kurgu taslağında hat kod 2 ile durur ve kullanıcı "devam" ya da not verene kadar
bekler. Bu durumda da soru sorulmaz: dosya hazır tutulur ve "istersen izle; devam demen yeter" bilgisi verilir. Varsayılan `tam_otomatik` kipte hat
hiçbir noktada beklemez.

## 9. Uygulama sırası

Her adım küçük bir PR'dır (CLAUDE.md: küçük, anlamlı commit'ler); kabul şartı otomatik testtir; "yer" yazıldığı yerde yazılır ve sınanır. Bir adım
bitmeden ona bağlı adım birleştirilmez. Ö0 sonucu (adım 9 ve 12a) P1 adımlarının sırasını değiştirebilir; değişiklik karar defterine yazılır.

| # | Adım | İçerik | Kabul şartı (test) | Bağlı olduğu | Yer |
|---|---|---|---|---|---|
| 0 | **PR-0 güvenlik acil yaması** | D-02 a–g, depodaki `memmet.py`'ye: `OLAGANDISI_KELIMELERI` → **her kipte** `Durdur(kod="olagandisi")`, sayfada işlem 0, `FLOW_KILIDI.json`, çıkış 7; "olağan/unusual" `HATA_KELIMELERI`'nden çıkar; `kontrol_noktasi()` olağan dışı metinde ve reCAPTCHA/doğrulamada beklemez (bildirir, çıkış 2); kodda 17.10 tempo varsayılanı (ayardaki daha hızlı değer yok sayılır); asgari `FLOW_TEMPO.json` (son gönderim, kalan mola); `_surum ≥ 2` → 4; varsayılan 720p; docstring. `saglayicilar/flow.py`: çıkış kodu → `Kisitlandi(kod=…)`, bilinmeyen kod geçiş yapmaz. `film.py`: `Kisitlandi(olagandisi\|dogrulama\|bilinmeyen)` sonrası sağlayıcı geçişi yok. SAHNELER okuyan v1 araçlarına `_surum ≥ 2` → 4 koruması. Depodaki eski `.bat`'lar (`MEMMET_BASLAT`, `MEMMET_SADECE_*`, `CAPCUT_PROJESI_OLUSTUR`, `FILM_HATTI`, `YENI_FILM.bat`) `_ESKI/`'ye; `yeni_film.py` bunları üretmez; `BASLA_BURADAN.txt` başına emeklilik notu. `kurulum.py --veri-emniyet` (veri kökü emniyeti; D-02) | `test_memmet_korkuluk` T10-elle, T10-gece, T10-dogrulama (uyarı fikstüründe hazırlanan istem 0, sayfada işlem 0, ≤ 10 sn'de çıkış 7; doğrulamada çıkış 2), tempo ve mola testleri; `test_flow_saglayici`; `test_veri_emniyet`; `test_film.py` (iki beklenti §6.10'daki gibi güncellenir; v1 davranışı korunur) | — | bulut (yazım + test) |
| 1 | **PR-1 hızlı düzeltmeler ve temel veri** | `puan_oku.py` medyan; `izleme_paketi.py` konuşan adı yerine ekranda kurulmuş tarif; `ai84.py` tembel anahtar; `ortak.py` (`yollar()` tek yol kaynağı) + yol göçü (§5.6: `memmet`, `ai84`, `saglayicilar`, `kontrol`, `seslendir`, `capcut_film`, `notlari_oku`, `kurulum`, `yeni_film`, `paketle`) + `kurulum.py --yollar`; `esitle_gelistirme.py` (dar `esitle --gelistirme`: beyaz liste + anahtar taraması + ayrı dal; PR-2'de `film.py esitle --gelistirme` olarak sarılır; D-12); `esikler.py` + RE'ye `kaynak`/`etiket` geçişi + FILM_AYAR'daki güvenlik sayılarının `hat_esikleri.json`'a taşınması (D-34); `veri/ADLAR.json` + `test_adlar.py`; `veri/LISANSLAR.json`; `veri/kok_neden.json`; §2.5 belge düzeltmeleri (ZN §6.1, Z0 #5/#14/#17, AR2 §6.1, RE `eylem_adim_*`, CLAUDE_ICIN dahil); kök `CLAUDE.md` yeniden ve `YZ_FILM/ARACLAR/CLAUDE.md` (§İlk yerel oturum dahil) | {6, 8, 9} → 8; anahtarsız `import ai84` süreci öldürmez; `test_yollar` yeşil; RE'de kaynaksız anahtar 0; `FILM_AYAR`'daki sınır gevşetemez; `test_adlar` yeşil | 0 | bulut |
| 2 | **İlk yerel oturum: veri kökü emniyeti, memmet3 aktarımı, Ö0-a** | kullanıcının bilgisayarındaki geliştirme oturumu (§8.2 adım 0b; kullanıcı yalnız `ilk kurulum` yazar): `kurulum.py --yollar` → `kurulum.py --veri-emniyet` → memmet3'ün `<veri>/GELISTIRME/`'ye alınması, PR-0'ın bütün maddelerinin ona uygulanması, yolların `ortak.yollar()`'a bağlanması, T10 her kipte, `esitle --gelistirme` ile ayrı dala; birleştirme bulutta PR ile → `olcum0/kanca_deneme/` ile §10.3'teki 20 davranış (beceri adım 6'da gelir; sonraki sürümlerde aynı iş `/film-gelistir ilk-kurulum` ve `olcum0-a` ile) | `EMNIYET_RAPORU.json` (yamasız Memmet'e giden giriş noktası 0); memmet3 CI'da T10-elle, T10-gece, T10-dogrulama'dan geçti ve birleşti; `O0a.json` her davranışı "çalışıyor / çalışmıyor + yedek" ile kapatır | 0, 1 | **yerel** (kullanıcının bilgisayarında geliştirme oturumu) + bulut (birleştirme) |
| 3 | **PR-2 görev defteri çekirdeği** | `film.py` v2 komutları, `GOREV.json`, `FILM_DURUM` v2, `hat/asamalar.py`, `kapi.py`, `kuyruk.py` (şema + 0 kredi kuralı + soy sayacı), `kredi.py` + `olcek.py`, `flow_yuk.py`, `ders_defteri.kaydet`, disk ve token kapıları, `.claude/bin/film.py` | `test_gorev_defteri` (30 kesme senaryosu), `test_kuyruk`, `test_olcek`, `test_flow_yuk` | 1 | bulut |
| 4 | **PR-2b kurulum KUR1 ve ilk .bat'lar** | `kurulum.py` KUR1 (soru yok; her çalıştırmada `--veri-emniyet` ve `--yollar`; güvenli `FILM_AYAR.json`, `settings.local.json`, `python_yolu.txt`, sürüm, disk, git ve `.git` denetimi, anahtar dosyası boşluk denetimi, Gemini anahtar dosyasının varlığı, FluidSynth + SF2, müzik çekirdek seti); `bat_yenile.py` (Python ve betik mutlak yolla); `FILM_SETI.bat`, `KURULUM.bat`, `GUNCELLE.bat` (yerel değişiklikte durur; ZIP'te kapalı), `FLOW_GIRIS.bat`, `IZINLER.bat`, `UYARI_GECTI.bat`, `GEMINI_TEST.bat`, `DURDUR.bat` | kurulum kuru çalıştırması ve Windows CI'da `.bat` üretimi (ASCII + CRLF; `..\..\ARACLAR` yok); `GUNCELLE.bat` çakışma fikstüründe hiçbir dosyayı değiştirmeden durur | 3 | bulut + yerel doğrulama |
| 5 | **PR-3 Claude Code katmanı** | `settings.json`, `kanca.py` + `kanca.sh`, `erisim.json`, `kor_paket.py` (kâğıt kipleri), `dilim.py`, aşamalı okuma mekanizması (Ö0-a'nın seçtiği) | `test_kancalar` (+ 50 mesajlık soru seti), `test_kor_paket` (sızıntı 0), nabız testi | 2, 3 | bulut + yerel doğrulama |
| 6 | **PR-4 ajanlar ve beceriler** | 21 ajan dosyası, 4 `SKILL.md`, `sablonlar/`, `semalar/`, `reference/`, `KURTARMA.md`, `GOREV_SEMASI.md`, `KULLANICI_DILI.md`, `PLAN_DILI.md`, `beceri_denetim.py`; `istem-muhendisi.md` ve `muzik-supervizoru.md` depodan kaldırılır | `beceri_denetim` yeşil; §4.8 senaryoları 1–7 sahte ortamda | 5 | bulut |
| 7 | **PR-5 hikâye odası** | `hikaye_odasi.py`, `bulgu_yonlendir.py`, `puan_oku.py` v2 tam, `istem_denetim.py` v2 (replik), `evren.py` (`--on-kayit`, `ne_yok_kelimeleri`, `ozet`), `hikaye_esikleri.json`, `kaset` sağlayıcısı | `test_hikaye`; A00–A06 `kaset` ile uçtan uca | 6 | bulut |
| 8 | **PR-6 yönetmen kâğıdı** | sözlükler (plan, fiil + `beklenen_hiz`, ifade, efekt), `plan_sema`, `kroki`, `plan_denetim`, `plan_dili`, `istem_derle --hareket`, `plan_birlestir`, `dunya_defteri` (K0 + duygu), `zaman_cizelgesi` T0 (Z1/Z2), `kamera_agaci`, `cekim_listesi`; `FILMLER/ORNEK_3_SAHNE_ZANAAT/` (+ bozuk varyantlar) | `test_plan_dili`, `test_sureklilik`; A07 `kaset` ile | 7 | bulut |
| 9 | **Ö0-1 yerel ölçümler (b, c, d, e, g)** | kendi içinde yeterli `olcum0/` betikleri + `film.py olcum0`: Flow kapasitesi (merdivenli protokol, ilk uyarıda kapanır; geliştirici Claude'un elle yazdığı sürümlü 45 istemlik fikstürle; klipler saklanır), istem biçimi ve canlı bekleme 2×2 A/B'si ile son kare referansı ve zincir karesi A/B'si için çekim (değerlendirme Ö0-2'de), ses dönüştürme kıyası + doğallık ölçüsü, MuseTalk ve ACE-Step kurulumu/süresi, büyütücü süresi, CapCut klon/şifre, Gemini paketi, kotası, ücretsiz katmanı ve video/ses girişi, kanal teşhisi (CSV) | `OLCUM0.json` her denemede ölçüm + karar + gerekçe; Ö0-b'de ikinci uyarı 0; P1 sırası yeniden yazıldı | 0, 1, 2, 3, 4 | **yerel**; 5–8 ile paralel |
| 10 | **PR-7 ses kâğıdı ve kâğıt sonu** | `ses_plani.py`, `muzik.py --kagit/--midi`, `istem_denetim` ses ekleri, `ses_esikleri.json`, `test_ses` (kâğıt kısmı); `FILMLER/ORNEK_3_SAHNE_TAM/` + kaset | A08–A09 ve `KAGIT_TAMAM.json` `kaset` ile; `test_uctan_uca_tam` kâğıt sonuna kadar | 8 | bulut |
| 11 | **İlk filmin kâğıt aşaması** | gerçek ajanlarla A00–A09 (konu kullanıcıdan); Ö0-b yoksa 1800 sn | kâğıt kapıları; Ö0-f'nin token ölçümüyle karşılaştırma | 10 (ve 9 paralel) | yerel |
| 12 | **PR-8 görsel hattı** | `gemini_paket.py`/`gemini_al.py`, `olcum/` gerçek arka uçlar, `kor.py`, `kare_denetim`, `kart_denetim`, `duzeltme`, `evren --kilitle`, `istem_derle --gorsel/--kart/--kapak`, `kapak.py`, `gemini_api` sağlayıcısı (ücretsiz anahtar varsa açık; D-19) | `test_g1_karar`, `test_kart`, `test_evren`, `test_izinler`; B3 44 kare etiketinde kaçırma oranı raporu (Ö0-h, adım 12a) | 9, 11 | bulut (sahte) + yerel |
| 12a | **Ö0-2 ölçümleri (f, h, Ö0-b·V3)** | Ö0-f (adım 7'den sonra, ilk filmin A06'sından önce mümkünse): token, seyirci gürültüsü, karar 6 testi; Ö0-h (B3 44 kare etiketleri, `<veri>/GELISTIRME/` → `esitle --gelistirme` → PR) ve Ö0-b kliplerinin V3 ve canlı bekleme değerlendirmesi (adım 12'den sonra; kayıtlı kliplerle, yeniden çekim yok) | `O0f.json`, `B3_44.json` birleşti, `O0b_v3.json`; ön kararlar karar defterinde | 6, 7, 12 | **yerel** |
| 13 | **PR-9 yerel ses hazırlığı** | `ses_sec` (telaffuz, seçim), `ses_kiyas`, `seslendir --animatik`, `muzik --uret` (ACE-Step/kütüphane çekirdek seti/Gemini müzik paketi (lisans doğrulanınca)/MIDI; zincir boşsa müziksiz + BAYRAK), `ses_katmani` T1, `son_miks`, `olcum/ses` gerçek, MOS tahmincisi (lisanslıysa); KUR2 kurulumu | `test_ses` (bozuk girdi 18 madde); A10a–c gerçek ortamda | 9, 11 | bulut (sahte) + yerel |
| 14 | **PR-10 animatik** | `zaman_cizelgesi` T1, `kurgu_render --animatik`, `kor_paket` izleme kipleri, `seyirci_topla` izleme ekleri ve personalar, `kurgu_uygula`, `kurgu_denetim --kesme-simule`, kurgucu/kesici şablonları, izle-dinle paketi (`kurgu_render --bilgi-paketi`), `bildirim.py`, `film.py bekle`, `izleyici`/`dinleyici` sağlayıcıları (ücretsiz anahtarla varsayılan açık) | `test_kurgu` (animatik senaryoları), render = T1 ±1 kare; `animatik: ONAYLI` imzası olmadan video görevi açılmaz | 12, 13 | bulut (sahte) + yerel |
| 15 | **PR-11 video hattı** | `memmet.py` v2 (memmet3 tabanlı), `blok_plani`, `memmet_topla`, `yerel_is`, `kalite_denetim --klip`, `video_denetim`, `kare_zinciri --cikar`, `ses_donustur --hizala` (SC1), `blok_plani --kesit` (dikey kesit; Flow kilitliyken Vertex kuralı) | `test_v1`, `test_zincir`, `test_memmet_korkuluk` tam (her kip), `test_izinler` (Vertex); sahte Flow sayfasında blok akışı | 9, 12a, 14 | bulut (sahte) + yerel |
| 16 | **PR-12 video sonrası ses ve kurgu** | `ses_donustur`, `ses_karar`, `diyalog_esitle`, `ses_katmani` T2, `dudak_denetim`, `muzik --yerlestir`, `plan_kurgu`, `kirp_oner`, `kurgu_denetim`, `capcut_film` v2, `taslak_fark`, `capcut_yama` (Ö0-d olumluysa), `notlari_oku` v2, `renk_cila`, `buyut`, `arsivle.py` (P1; [SON] O-7); KUR3 kurulumu | `test_kurgu` (16 senaryo), `test_ses` tam, `test_arsivle` | 15 | bulut (sahte) + yerel |
| 17 | **PR-13 yayın ve öğrenme** | `jenerik.py`, `shorts_mp4.py`, `yayin_paketi.py`, `kalite_denetim --final` + yayın doğrulaması, `yayin_analiz.py` (CSV kipi), `ders_derle.py` (+ `--film-sonu`), `evren --film-sonu`, `evren --yedekle` + `ders_defteri --yedekle`, `<veri>/BILGI/YOUTUBE_POLITIKA.md` (`kanal_teshis.py` CSV kipi adım 9'da) | `test_uctan_uca_tam` A00–A18 sahte ≤ 5 dk | 16 | bulut (sahte) + yerel |
| 18 | **PR-14 kullanıcı yüzü ve CI** | kalan `.bat`'lar, `BASLA_BURADAN.txt` (sözleşme kartı), `paketle.py` künye, CI (`windows-latest` Py 3.10 + `ubuntu-latest`), bütün takım ≤ 10 dk | CI yeşil | 17 | bulut |
| 19 | **İlk filmin yerel üretimi** | A10–A18; dikey kesit ve PILOT kararları; ilk filmin sonu raporu | §7.4 M1–M17 raporu | 11–18 | yerel |
| 20 | **P2** | `yayin_analiz.py` ve `kanal_teshis.py` OAuth kipi (`YOUTUBE_BAGLA.bat`), `youtube_yukle.py`, `film.py esitle` (tam), `claude_api.py`, `vertex_gorsel`, `veo_vertex`, `ai84_vc`, `elevenlabs_muzik`, OTIO, Telegram komutları | her biri kendi testiyle | 19 | — |

**Ö0'dan sonra olası yeniden sıralamalar (karar kuralları önceden yazılı):** Ö0-c hiçbir dönüştürücünün eşiği geçmediğini gösterirse MuseTalk (KUR3)
adım 13'e çekilir ve ana ses yolu B planına geçer (§2.2); Ö0-d CapCut klonunun çalışmadığını gösterirse `capcut_yama` çıkar, `kurgu_render --yayin`
adım 16'da P1 olur ve `yayin_kaynagi: master` yazılır; Ö0-e Gemini API kotasını uygun bulursa `gemini_api` görsel sağlayıcısı adım 12'nin başına
alınır ve paket yükü kalkar; Ö0-b'nin uyarısız gün alt sınırı 20'nin altında kalır ya da ölçülemezse ilk film 30 dk kalır ve takvim §1.6 formülüyle ölçülen kapasiteden yeniden hesaplanır; Ö0-c ACE-Step'i 4 GB kartta kabul edilemez bulursa `kutuphane` ana müzik basamağı olur (D-25).

## 10. Açık riskler ve bilinçli olarak dışarıda bırakılanlar

### 10.1 Açık riskler
| # | Risk | Etki | Önlem (bu tasarımda) | Kalan |
|---|---|---|---|---|
| R1 | Flow hesabının kapasitesi düşük ya da hesap uzun süre işaretli kalır (B3'te video tarafı ilk gönderimlerde işaretlendi; ≈ 137 klip kaldı) | takvim haftalarca uzar | Ö0-b ölçümü; ölçülmüş kapasiteyle süre ve takvim; 17.10 temposu; haftalık uyarı kilidi; zincir ardılları ayrı blokta; take ölçüyle | Flow kilitliyse film videoda bekler; Vertex'e otomatik geçiş yoktur, yalnız ayrı izin (`izinler.flow_kilitliyken_vertex`) + `usd_tavan_film > 0` + ölçülmüş fiyatla `blok_plani` kalan planları Vertex'e yazar (D-03, D-41) |
| R2 | Claude kullanım sınırı ve token tüketimi (≈ 350–570 görev; en kötü seyirci yükü ≈ 6–7 M token) | hat bekler, ajanlar yarıda kalır | kullanım kaydı, aşama görev tavanı, erken projeksiyon, 8 BEKLE, karar 6 testi, dosya tabanlı devam | abonelik penceresi takvimi belirleyebilir |
| R3 | Omni saniyeli adımlara uymaz | V3 düşer, yeniden çekim artar | Ö0-b `aralik`/`sira` A/B; adım 2'ye inme ve `bitis_sabit` payı; dikey kesitte yeniden ölçüm | ölçüm kötü çıkarsa atomik zincir korunur ama yeniden çekim payı büyür |
| R4 | 4 GB kartta ses dönüştürme metalik ya da aksanı taşır | "ses değişti", "robot ses" | Ö0-c kıyası (fısıltı ve bağırma dahil, doğallık ölçüsüyle), metin kapısı, ses merdiveni, B planı (`tts_dudak`), aksanlı `veo_ses_tarifi`, ücretsiz anahtarla `dinleyici` | anahtar yoksa aksan ve doğallık "ölçülemedi" (açık eksik + izle-dinle örneği) |
| R5 | Claude Code davranışları belgede yazıldığı gibi işlemez ya da sürümle değişir | habersizlik ya da "uyarıda dur" güvencesi sessizce kalkar | Ö0-a 20 madde; nabız; `kanca.py`'nin kendi içinde kapalı başarısızlığı (`onFailure`'dan bağımsız); sürüm değişince test; yedekler: kör roller için başsız `claude -p`, model sapması için SubagentStop dökümü, uyandırma için "tamam" yazma | doğrulanamayan davranışın yerine betik kapısı; `claude -p` de tutmazsa habersizlik talimat düzeyinde kalır ve BAYRAK'la raporlanır |
| R6 | Seyirci puanları kalibre değil; Claude Claude'u puanlıyor | ya hiç geçmez ya da şişer | kapı 7 + olgular / hedef 8; plato kuralı; Ö0-f gürültü ölçümü; personalar; farklı aileden `izleyici`; gerçek tutma verisiyle kalibrasyon | gerçek veri gelene kadar puanın izlenmeyle ilişkisi bilinmiyor |
| R7 | Kare paketi izlemek değildir (hareket, ses, oyunculuk görünmez) | "doğru ama ruhsuz" film | dikey kesit; `izleyici`; hareket hızı ve enerji eğrisi; oyunculuk katmanı; kör ifade okuması | `izleyici` yoksa hareket ve ses kalitesi yalnız betik ölçüsüyle |
| R8 | MuseTalk ağız bölgesini 256 px'te üretir; yüz değişebilir | yakın planda bulanıklık | merdivenin geç basamağı; V2 ve S3 zorunlu | B planına düşülürse yük artar |
| R9 | ACE-Step orkestra kalitesi zayıf; YZ müziğine Content ID talebi | ucuz ses, yayın sorunu | kalite kapısı, kütüphane çekirdek seti, lisansla Gemini elle basamağı, özgün motif, kaynak kaydı; zincir boşsa müziksiz ipucu + BAYRAK | kalite kapısı `dinleyici`'ye bağlı (yoksa ÖLÇÜLEMEDİ, açık eksik) |
| R10 | ElevenLabs/AI84 koşulları belirsiz; AI84 kriptoyla alınmış bir aracı | seri sesi hukuken kırılgan | eğitimsiz OpenVoice önce, RVC yalnız koşullar okununca, referans kayıt, `LISANSLAR.json` notu | kullanıcının mevcut hizmet kararıdır; risk raporda yazılı |
| R11 | CapCut taslakları şifreler ya da `pycapcut` klonu desteklemez | not ve yama yolu çalışmaz | Ö0-d; `yayin_kaynagi: master`; "yeni adla kur" yolu | kullanıcı CapCut'ta düzenlediyse kararları elle taşınamayabilir |
| R12 | Windows kurulumu kırılır (cp310 için son torch tekerleği 2.9.1, onnxruntime ≤ 1.23.2; mmcv; çok Python sürümü) | yerel aşamalar başlamaz | KUR1/KUR2/KUR3 kademeleri, ayrı ortamlar, "çalışıyor/çalışmıyor" kartı, eksik kademe yalnız kendi basamağını kapatır | ilk kurulum zaman alır |
| R13 | Kullanıcının fiziksel iş yükü (≈ 400–527 GÖNDER, ≈ 12–24 paket) | yorgunluk, güven kaybı | sözleşme kartı; Gemini API (Ö0-e); işler toplanır; bitişi arka plandaki `film.py bekle` algılar ve oturumu uyandırır (Ö0-a #16; tutmazsa "tamam" yazma işi sayısıyla kartta) | `elle` modda GÖNDER sayısı yüksek kalır |
| R14 | Yaratığın deseni ve boyu oynar | kancanın kendisi zayıflar | kimlik kartı (≥ 3 işaret), DINOv2 bankası, kör sorular, davranış sözlüğü | ilk filmlerde çoğunlukla BAYRAK |
| R15 | 720p'den büyütme yavaş ya da yüzü değiştirir | yumuşak görüntü, "4K" vaadi | Ö0-c süresi; SFace denetimi; Lanczos + gren yolu; "4K" yalnız kapı geçerse | — |
| R16 | B1'in düşük izlenmesinin nedeni bilinmiyor | yatırımın yönü belirsiz | Ö0-g teşhisi; yayın sonrası analiz | kullanıcı veri bağlamazsa "ölçülemedi" |
| R17 | Disk dolar (her plana 2 aday, ≈ 1.200 görsel, önbellekler) | hat durur | disk kapısı, kendiliğinden arşiv (`arsivle.py` P1; A16, A17 sonu ve disk kapısı), önbellek boyutu raporu | temizlik kullanıcının işi (Claude silemez); D takılı değilse "D'yi tak" |
| R18 | YouTube politikaları değişir (sentetik içerik beyanı, özgün olmayan içerik) | kanal riski | `yz_beyani`, politika kontrol listesi, 90 günlük tazeleme | politika yorumu insan kararı gerektirebilir |
| R19 | Ana Claude Bash'te Python ile kancayı atlatır | makine sahipli dosya elle değişir | izin listesi yalnız `film.py`; komut kapısı sezgisel tarama; makine sahipli dosyaların sha1'i | sezgisel tarama kaçırabilir |
| R20 | Tek seyirci örneği tam filmi (≈ 0,2 M token) okuyamaz ya da bağlamı sıkışır | izleme turu bozulur | Ö0-a #15; sıkışırsa görev geçersiz, parça sayısı ayarlanır | — |
| R21 | Ders defteri yalnız sıkılaşır (mandal) | zamanla DUR olasılığı artar | iki yönlü kalibrasyon; yanlış alarm ≤ %30 şartı | güvenlik eşikleri bilerek mandallı |
| R22 | Zincir dalgaları ve görsel/video gün ayrımı takvimi uzatır | süre | uygunluk kuyruğu; derinlik ≤ 2; örtü planları | — |
| R23 | Telif ya da tanınır eser benzerliği (müzik, görsel, hikâye) | yayın riski | özgün motif; istemde sanatçı/film adı yok; kaynak kaydı; jüri özgünlük ölçütü | Content ID yanlış talebi olabilir |
| R24 | C diski arızalanır ya da veri kökü kaybolur | seri evreni, sesler, krokiler, leitmotifler ve dersler gider (KK3e, KK3f) | A18'de D'ye yedek (`robocopy /E`), A00'da sha1 doğrulaması, evren yalnız ekleme (D-42) | D takılmazsa yedek bir film gecikir |
| R25 | Kullanıcının bilgisayarında bilinmeyen başka bir eski Memmet kopyası ya da döngü betiği kalır (ör. 17.10'daki `memmet_dongu.ps1`) | KK5 ihlali yolu açık kalır | veri kökü emniyeti `<veri>` altında `memmet.py`'yi çağıran her betiği tarar ve emekliye ayırır; kod veri kökündeki sarmalayıcıyla depoya yönlenir (D-02) | veri kökü dışındaki kopyalar taranmaz; `kanca.py komut` sürüşte doğrudan `memmet.py` çağrısını yine reddeder |
| R26 | Tavan sonrası merdiveni çok sayıda planı `durdu`'ya düşürür | film delikli ya da kısa çıkar | merdiven önce sahibin ve üst sahibin kalite yollarını dener; `durdu` sayısı `FILM_SONU_RAPORU`'nda ve ders defterinde; ≥ %5 plan (tahmin) `durdu` olursa `yapimci·doktor` film düzeyinde teşhis yazar | ilk filmlerde oran bilinmiyor |

### 10.2 Açık sorular (cevabı bilinmiyor; hangi ölçüm cevaplar)
| Soru | Cevaplayan |
|---|---|
| Flow'un uyarısız günlük kapasitesi (alt sınır); uyarıdan sonra hesabın açılma süresi; 720p üretim süresi; 10 sn klip fiyatı; politika reddi kredi yakıyor mu (yalnız kendiliğinden gelen retten; kasıtlı tetikleme yasak) | Ö0-b |
| Omni'nin `aralik`/`sira` istem biçimine ve "holds the pose, breathing"e uyumu; son kare zinciri karesinin kalite kaybı | Ö0-b, dikey kesit |
| Flow'da (Omni 1.1 Flash) ses referansı ya da sabit ses özelliği var mı | Ö0-b sırasında arayüzde bakılır |
| Veo'nun metin sapma ve konuşmama oranı | Ö0-c (arşiv), SB3, dikey kesit |
| AI84'ün ElevenLabs parametrelerini (seed, önceki/sonraki metin, telaffuz sözlüğü, Voice Design, müzik) iletip iletmediği | Ö0-c küçük denemeler |
| Gemini API görsel kotası ve fiyatı; plan başına 3 aday; ücretsiz katmanın video ve ses girişi, kotası ve veri kullanım koşulu (bellekten, doğrulanacak) | Ö0-e |
| Vertex Veo fiyatı ve kotası (kullanıcının Google Cloud hesabı varsa) | Ö0-b ek denemesi |
| YouTube Studio CSV dışa aktarımının tutma, gösterim ve tıklama oranı verisi; kanalda kapak testi açık mı; OAuth bağlantısının kullanıcının kendi Google Cloud projesini isteyip istemediği (bellekten, doğrulanacak; P2) | Ö0-g / P2 |
| `pycapcut` lisansı ve yetenekleri; taslak şifrelemesi | Ö0-d |
| ACE-Step, büyütücü ve MOS modellerinin ağırlık lisansları; FluidSynth ve örnek kütüphanesi lisansları; OpenVoice V2'nin geçişli bağımlılıkları (AGPL'li `whisper-timestamped`?); müzik çekirdek setinin ve Gemini müziğinin "ticari YouTube" koşulları; `pycapcut` | kurulum ve P0 lisans doğrulaması (`LISANSLAR.json`) |
| Kör gözlem görev boyu (12 ↔ 20 görsel), MediaPipe yaw işareti | Ö0-h + GS0 kalibrasyonu |
| Plan seyircisi, ön turlar (KR3a/KR8a), take ve kısmi izlemenin değeri | ilk iki film (D-44, D-23, D-18) |
| Claude paneli ve `izleyici` puanlarının gerçek tutma eğrisiyle ilişkisi | ilk üç film (D-19, D-24) |
| ACE-Step 1.5'in 4 GB kartta ipucu başına süresi | Ö0-c |
| Tavan sonrası merdiveninde `durdu` olan plan oranı; `hata_donus_max`, Ö0-b merdiveni, kol başına 12 örnek gibi tahmin sayılarının doğruluğu | ilk iki film (ders defteri) |
| memmet3'ün `elle` kipindeki gerçek davranışı (kaynak yalnız H/olagandisi-dur notu; kod depoda yok) | memmet3 aktarımında kod okunarak ve T10 ile (adım 2) |

### 10.3 Ö0-a'da doğrulanacak Claude Code davranışları (20)
1. `CLAUDE_CODE_FORK_SUBAGENT=0` ile tek mesajdaki 3–5 Agent çağrısının paralel koşması ve ana Claude'un sonucu beklemesi.
2. Arka planda biten alt ajanın tamamlanma bildiriminin, ana tur bitmişken oturumu kendiliğinden uyandırması.
3. SubagentStop `decision: "block"` ile aşamalı devam (ön planda ve arka planda); `maxTurns`'e ulaşan ajanda SubagentStop'un tetiklenmesi ve kısmi çıktının
   `SendMessage` ile sürdürülmesi.
4. PreToolUse `Agent` girdisinde `subagent_type`'ın (fork dahil) ve `name`/`isolation` parametrelerinin görünmesi.
5. `onFailure: "block"` ve `timeout` alanlarının komut kancasında beklendiği gibi çalışması (kasıtlı yavaş kanca testi); alan yoksa `kanca.py`'nin
   iç kapalı başarısızlığı (D-11) tek güvencedir ve zaman aşımı riski kanca süresiyle (≤ 1 sn hedef) küçültülür.
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
16. Arka planda başlatılan bir Bash işinin (`film.py bekle`) ana tur bitmişken bitmesinin oturumu kendiliğinden uyandırması; arka plan işinin en
    uzun süresi. Tutmazsa sözleşme kartına "her işten sonra 'tamam' yaz" satırı girer (§4.2, §8.1; [SON] O-4).
17. Kullanılan dört olayın varlığı ve tetiklenmesi: `SubagentStart` (ders satırı), `StopFailure`, `PostCompact` (bağlamın geri getirilmesi),
    `PostModelSwitch` (D-08 `model_sapmasi`); olmayanın yedeği: `SubagentStart` yerine görev başında `film.py basla`'nın yazdığı satır, `PostCompact`
    yerine SessionStart `compact` eşleyicisi, `PostModelSwitch` yerine SubagentStop dökümündeki model adı ([SON] O-11).
18. `onFailure` alanı olmadan beklenmeyen kodla çıkan ve zaman aşımına uğrayan kancanın davranışı (çağrı engelleniyor mu, geçiyor mu).
19. Başsız `claude -p` ile kör rol: abonelikle çalışması; proje ve kullanıcı `CLAUDE.md`'si ile bellek yüklenmeden çalıştırılabilmesi (bayrak ya da
    ayar); `<veri>` dışındaki geçici çalışma klasörünün dışını okuyamaması; `Read,Write` dışında araç kullanamaması (D-11).
20. Bulut oturumunda depo kancalarının (`.claude/settings.json`) uygulanıp uygulanmadığı ve SessionStart'ın `ortam=bulut`'u ayırt edebilmesi (D-45).

### 10.4 Bilinçli olarak dışarıda bırakılanlar
| Dışarıda bırakılan | Neden |
|---|---|
| Bot tespitini atlatan her şey: fare/klavye taklidi, reCAPTCHA çözümü, uyarıdan sonra **hangi kipte olursa olsun** otomatik yeniden başlatma ya da sayfa yenileme (memmet3 `elle` kipindeki "kullanıcı sayfayı yeniler, devam" akışı dahil), tempo hızlandırma, ikinci/ortak/aile hesabı, kie.ai | KK5; D-02, D-03; BK §6.4 "gri havuz" |
| Flow uyarısını ya da politika reddini **kasıtlı tetikleyen** ölçüm ve deneme (Ö0-b dahil) | KK5; hesabı günlerce işaretli bırakma riski (H/olagandisi-dur 19.10); Ö0-b ilk uyarıda kapanır, ret yalnız kendiliğinden gelirse kaydedilir (D-04) |
| Memmet'in "gündüz otomatik" kipi | gündüz kipinde 15–20 dk'da bir uyarı geldi (BK §6.2 #7); `elle` varsayılan, gece yalnız izinle |
| "İnsan temposu" çerçevesi | tempo insan taklidi değil yük sınırıdır ([UM2] §4.8.5); metinler buna göre düzeltilir |
| Wav2Lip, `fal_latentsync`, Seed-VC, MusicGen, YuE2, Stable Audio Open | kalite ya da lisans (CC-BY-NC, InsightFace riski, belirsiz ağırlık lisansı, şirket lisansı) |
| Lyria/Gemini ile ambiyans; lisansı doğrulanmadan Gemini'de elle müzik | BK §5.1.2 (ambiyansta mırıltı dersi); Gemini müziği lisans doğrulanınca zincirin elle son basamağıdır (D-25; KK1 fiziksel işi yasaklamaz) |
| Bütün filmin `ai84_vc` ile dönüştürülmesi | maliyet bakiyenin 2,6–3,2 katı (tahmin); yalnız kritik replik |
| RVC eğitimi | ElevenLabs/AI84 koşulları okunana kadar |
| Bulutta film üretimi (kâğıt aşamaları dahil); `film.py esitle` (tam) | kancalar bulutta uygulanmayabilir; kullanıcıya git yükü (D-12); bulutta konu sorulmaz (D-45, görev metninden bilinçli sapma; yeniden açma koşulu D-45'te); tam `esitle` P2 |
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
