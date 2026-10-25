# YZ FİLM SETİ — geliştirme rehberi (`YZ_FILM/ARACLAR/`)

Bu dosya **sistemi değiştiren** oturumlar içindir: kullanıcı `/film-gelistir` dediğinde ya da oturum açıkça bir geliştirme
oturumuysa (bulut geliştirme oturumu, ilk yerel oturum). Film üretimi bu dosyadan yürümez; kök `CLAUDE.md` geçerlidir.
Bu klasörde çalışırken Claude Code bu dosyayı kendisi yükler; kök `CLAUDE.md` buraya yönlendirir.

## Önce oku
1. **`.claude/skills/film-yap/tartisma/TASARIM.md`** — bağlayıcı karar belgesi. Uzman belgeleriyle ya da aşağıdaki eski listeyle
   çeliştiği her yerde TASARIM geçerlidir. Uzun belge: parça parça oku, `grep` ile bölüm bul (§9 uygulama sırası, §6 kod işleri).
2. `FILMLE ILGILI CLAUDE/00_OKU_BENI.md` … `07_*.md` (11–20 Ekim 2026 deneyiminin tam devri).
3. `YZ_FILM/BILGI/CLAUDE_ICIN.md`, `KARARLAR.md`, `YAPIM_REHBERI.md`.
4. `FILMLE ILGILI CLAUDE/03_DERSLER.md` — deneyerek öğrenilen kurallar, ihlal etme.

Kullanıcı Türkçe konuşur, teknik bilgisi az. Belgeler Türkçe, kullanım `.bat` dosyalarıyla adım adım.

## Hedef
Konudan bitmiş filme (kurgu + ses + müzik + altyazı + kapak + YouTube paketi) kadar kendi kendine yürüyen, sonucu "mükemmele yakın"
bir üretim hattı. Kullanıcıya yalnız konu sorulur; diğer kararları ekip verir (KK1). Üretim yalnız kullanıcının Windows bilgisayarında
yürür; bulut oturumları geliştirme ve `sahte`/`kaset` testleri içindir (TASARIM D-12, D-45).

## Şu anki durum (24.10.2026)
TASARIM §9'un bulutta yapılabilen adımları **0, 1, 3, 4, 5, 6, 7, 8, 10, 12–18** uygulandı (her biri `sahte`/`kaset` testleriyle; gerçek
model ve servis çağrısı yok). Adım başına ana araçlar:
- **0 PR-0 güvenlik:** `memmet.py` Flow uyarısında **her kipte** durur (`FLOW_KILIDI.json`, çıkış 7; doğrulamada 2; `_surum ≥ 2` → 4; varsayılan
  `elle`; 17.10 temposu kodda), `saglayicilar/flow.py` `Kisitlandi(kod)`, `veri_emniyet.py` + `kurulum.py --veri-emniyet` (eskiler `_ESKI/`'ye).
  Testler `test_memmet_korkuluk` (T10), `test_veri_emniyet`.
- **1 PR-1:** `ortak.yollar()` + `YOLLAR.json`, `esikler.py` + `veri/hat_esikleri.json`, `veri/ADLAR.json`, `veri/LISANSLAR.json`,
  `veri/kok_neden.json`, `puan_oku.py` medyan, `esitle_gelistirme.py`.
- **3 PR-2 görev defteri:** `film.py` v2 (`yeni, sonraki, basla, calis, bitir, kurtar, asama-ilerlet, bekle, karar/ders ekle, goster, ozet, surus …`),
  `hat/asamalar.py` (A00–A18a), `.claude/bin/film.py`, `kapi.py`, `kuyruk.py`, `kredi.py`, `olcek.py`, `flow_yuk.py`, `ders_defteri.py`.
- **4 PR-2b:** `kurulum.py` v2 KUR1 (`--kuru`, `--deneme`), `bat_yenile.py`, `bat_isleri.py`, depo kökü `KURULUM.bat`; `test_kurulum`.
- **5 PR-3 Claude Code katmanı:** `.claude/settings.json`, `.claude/hooks/kanca.py` + `.claude/bin/kanca.sh`, `.claude/kurallar/erisim.json`,
  `kor_paket.py` (kâğıt kipleri), `dilim.py`; `test_kancalar` (50 mesajlık set, nabız). Gizli kural yalnız gerçek erişimi engeller (okuma,
  kopyalama, yazdırma, arşivleme, taşıma, kodda `open(...)`); adın komut metninde geçmesi serbest. SubagentStop `yonetmen·plan`'da
  `plan_sema.py --dosya` + `plan_denetim.py --dosya` koşar.
- **6 PR-4 ajanlar ve beceriler:** 21 ajan dosyası (`.claude/agents/`), 4 `SKILL.md` (`film-yap`, `film-durum`, `film-not`, `film-gelistir`),
  `sablonlar/` (`{{esik:…}}` yer tutucuları), `semalar/`, `reference/`, `KURTARMA.md`, `beceri_denetim.py` (HATA 0; §4.8 senaryoları 1–7 GEÇ).
- **7 PR-5 hikâye odası:** `hikaye_odasi.py`, `bulgu_yonlendir.py`, `puan_oku.py` v2, `istem_denetim.py` v2, `evren.py` (`--on-kayit`, `ozet`),
  `kaset` sağlayıcısı; `test_hikaye` (A00–A06 kasetle).
- **8 PR-6 yönetmen kâğıdı:** `plan_sema`, `kroki`, `plan_dili`, `plan_denetim`, `plan_birlestir`, `dunya_defteri`, `zaman_cizelgesi` T0,
  `kamera_agaci`, `cekim_listesi`, `istem_derle --hareket`, `FILMLER/ORNEK_3_SAHNE_ZANAAT/`; `test_plan_dili`, `test_sureklilik`.
- **10 PR-7 ses kâğıdı:** `ses_plani.py`, `muzik.py --kagit/--midi`, `istem_denetim_ses`, `veri/ses_esikleri.json`, `FILMLER/ORNEK_3_SAHNE_TAM/`;
  `test_ses` (kâğıt), `test_uctan_uca_tam`.
- **12 PR-8 görsel hattı:** `olcum/` (kimlik, görünüm, ışık, poz, teknik), `kor.py`, `kare_denetim` G1, `kart_denetim`, `duzeltme`,
  `istem_derle_gorsel`, `gemini_paket`/`gemini_al`, `kapak`, `evren --kilitle`, `gemini_api` sağlayıcısı.
- **13 PR-9 yerel ses hazırlığı:** `olcum/ses`, `ses_sec`, `ses_kiyas`, `seslendir --animatik`, `muzik_uret`, `ses_katmani` T1, `son_miks`,
  ses sağlayıcıları.
- **14 PR-10 animatik:** `zaman_cizelgesi_t1`, `kurgu_render --animatik/--bilgi-paketi`, `kor_paket_izleme`, `seyirci_topla`, `animatik_imza`
  (onaysız animatikte video kredisi yok), `kurgu_uygula`, `kurgu_denetim --kesme-simule`, `bildirim`, `izleyici`/`dinleyici` sağlayıcıları.
- **2 (kısmen) memmet3 aktarımı birleşti (24.10):** yerel dal `yerel/memmet3-20261024-1346` birleştirildi; dosya yalnız başvuru olarak
  `YZ_FILM/_ESKI/memmet3/` (BENIOKU.md; ilk satırı `raise SystemExit`; kanca `memmet_arsiv` `_ESKI/`/`GELISTIRME/` altındaki Memmet'i
  her bağlamda reddeder). Koşan tek Memmet `ARACLAR/memmet.py`. memmet3, 34a9097'deki `memmet.py` + küçük arayüz ekleridir; ondan
  `dokun`/`oku` üzerinden alınanlar: video modeli seçici (ayar menüsünde `button "Model"`, yoksa tek `arrow_drop_down` düğmesi →
  `get_by_text(<model>, exact)`; model ayar yazısında görünmez, gezinmede sıfırlanır; bulunamazsa gönderim yok, 2), SAHNELER `en_boy`
  16:9 | 9:16, MEMMET_AYAR (_surum ≥ 2) `video_model` / `gorsel_adet` (v1 x2 → `_ADAYLAR/NNN_b.jpg`), elle kipte referans sahnesinde
  yüklenir, `MEMMET_OLCEK` (0.5–3). **Alınmayanlar:** Chrome arka plan yavaşlatma bayrakları (örtülü sekme insan sekmesinden farklı
  koşar), modeli bulamayınca "seçili modelle devam" (bütçe/kalite tutmaz), sürümsüz ayar dosyasından model/adet; memmet3'ün kendi
  notundaki `--hesap`, `--telefon`, beklemeyi kısaltma, uyarıda yenileme / F5, MEMMET_KONUM çoklu pencere (zaten alınmamıştı).
  Testler `test_memmet_korkuluk` `Memmet3Aktarim` + `HerAn` model seçicili tarama. Kalan: Ö0-a (`O0a.json` yerelde).
- **15 PR-11 video hattı:** `memmet.py` v2 (`--blok`, `--onizleme`; animatik ONAYLI değilse göndermez), `blok_plani`, `memmet_topla`, `yerel_is`,
  `kalite_denetim --klip`, `video_denetim`, `kare_zinciri`, `ses_donustur --hizala`, `memmet_yama`.
- **16 PR-12 video sonrası ses ve kurgu:** `ses_karar`, `diyalog_esitle`, `dudak_denetim`, `muzik_yerlestir`, `plan_kurgu`, `kirp_oner`,
  `capcut_film` v2, `taslak_fark`, `capcut_yama`, `notlari_oku`, `renk_cila`, `buyut`, `arsivle.py`, `kurulum_kur3`.
- **17 PR-13 yayın ve öğrenme:** `jenerik`, `shorts_mp4`, `yayin_paketi`, `yayin_analiz` (CSV), `kanal_teshis` (CSV), `ders_derle`,
  `ders_yedekle`, `evren_film_sonu` (`--film-sonu`, `--yedekle`, `--yedek-dogrula`).
- **18 PR-14 kullanıcı yüzü ve CI:** §6.9'un bütün `.bat`'ları (`bat_yenile.py`: depo kökünde + `TELEGRAM_TEST`, `YOUTUBE_BAGLA`;
  film klasöründe + `DURUM`, `VIDEO_GECE`, `ARSIVLE`, `YUKLE`; işleri `bat_isleri.py`'de. `VIDEO_GECE` yalnız gece izni + ölçülmüş Flow
  kapasitesiyle düşünülür ve gece döngüsü `film.py video`'ya bağlanana kadar yalnız bilgi verir; `YOUTUBE_BAGLA`/`YUKLE` P2 bilgisi).
  `BASLA_BURADAN.txt` son kullanıcı rehberi (§8.1 kartı + §8.2–8.5); kartı `kullanici_karti.py` `olcek.kart_md()`'den yazar
  (`--yaz`, `--denetle`; girdiler sabit: 1800 sn, ölçüm yok). `00_BENI_OKU.txt`. `paketle.py` künye (`KUNYE.txt`, `LISANSLAR.json`'dan)
  + sızıntı taraması (anahtar dosyaları okunmaz; zip içinde gizli adlı dolu girdi, profil, anahtar biçimli dizi → paket reddedilir,
  silinmez, gizli `AYARLAR/_REDDEDILEN_PAKET/`'e taşınır). CI `.github/workflows/testler.yml`: `windows-latest` Py 3.10, `ubuntu-latest`
  Py 3.10 ve 3.13; numpy, Pillow, PyYAML + ffmpeg; takım `testler/kos.py` ile modül/sınıf başına paralel süreçte (tek süreçte de
  `python -m unittest discover -s ARACLAR/testler` aynı testleri koşar). `test_kullanici_yuzu`.
  Bat ya da kart değişince: `python YZ_FILM/ARACLAR/kullanici_karti.py --yaz` (eşik dosyası değişirse kart testi bunu ister).

**Bekleyen adımlar:**
- **2 İlk yerel oturum** (aşağıda §İlk yerel oturum; kullanıcı `ilk kurulum` yazınca): veri kökü emniyeti ve memmet3 aktarımı yapıldı
  (24.10); Ö0-a'nın bulguları (Windows `claude.CMD`, bildirim/uyanma, #7 yazma ölçüsü, UTF-8, `effort`, `name`/`isolation`,
  masaüstünde sürdürme) düzeltildi (§Ö0-a bulguları); Ö0-a yeniden koşulup `O0a.json` yerelde yazılır.
- **9 Ö0-1 yerel ölçümler** (b, c, d, e, g): `olcum0/` betikleri ve `film.py olcum0` **henüz depoda yok** (Ö0-a'nın `olcum0/kanca_deneme/`'si dahil).
- **11 İlk filmin kâğıt aşaması** (gerçek ajanlarla A00–A09, yerel).
- **12a Ö0-2 ölçümleri** (f, h, Ö0-b·V3).
- **19 İlk filmin yerel üretimi** (A10–A18); burada gece kipi (`VIDEO_GECE.bat` → `film.py video --mod gece`, ölçülen kapasitenin
  %80'i tavanıyla) bağlanır. CI'nın ilk gerçek Windows koşusu da henüz görülmedi (iş akışı bulutta yazıldı, yerelde 3.10 + 3.13 yeşil).

**Bilinen açık riskler:**
- Flow kapasitesi: **kullanıcı kararı (25.10)** — Ö0-b merdiveni gün 1'den (10 video, uyarısız) sonra bırakılır; kapasite kullanıcının
  beyanından: `python olcum0/flow_deneme.py kapat --beyan 100` (yerelde, bir kez; `kapasite_kaynagi: kullanici_beyani`, ölçüm değil).
  Asıl sınır kredi. Flow uyarısında her kipte durma, 17.10 temposu ve kilit kuralları değişmez; uyarı kayıtlıysa beyan reddedilir.
  Beyan yokken `olcek.py`/BUT0 ölçüm olmadan **1800 sn** seçer.
- Gerçek model ve servis çağrıları (Claude ajanları, Flow/Veo, Gemini, ai84, yerel ses/müzik modelleri) doğrulanmadı; bütün testler `sahte`/`kaset`.
- `veri/LISANSLAR.json` girdileri bellekten yazıldı (`bellekten`); doğrulanmadı (ACE-Step ağırlıkları, MuseTalk modeli, Real-ESRGAN ağırlıkları,
  OpenVoice'un dolaylı bağımlılıkları dahil).
- Bilinen sınırlar: gerçek müzik kaynağı yoksa müziksiz + BAYRAK (D-25); kapak ve YouTube yükleme otomatik değil (P2); Flow kısıtı takvimi
  belirler (atlatma yok, D-02–D-04).

## Uygulama sırası
**TASARIM §9'daki tablo geçerlidir** (her adım küçük bir PR; kabul şartı otomatik test; bir adım bitmeden ona bağlı adım birleşmez).
Kısaca: 0 PR-0 güvenlik → 1 PR-1 hızlı düzeltmeler ve temel veri → 2 ilk yerel oturum (aşağıda) → 3 PR-2 görev defteri çekirdeği →
4 PR-2b KUR1 ve ilk `.bat`'lar → 5 PR-3 Claude Code katmanı → 6 PR-4 ajanlar ve beceriler → 7–8 hikâye odası, yönetmen kâğıdı → 9 Ö0-1 yerel
ölçümler → 10 ses kâğıdı → … → 18 kullanıcı yüzü ve CI → 19 ilk filmin yerel üretimi → 20 P2.

Eski "Yapılacaklar" listesindeki şu maddeler TASARIM ile değişti: senaryo ve yönetmen aşamaları Claude API değil Claude Code ajanlarıyla
yürür (`claude_api.py` P2); sağlayıcı soyutlaması kalır ama **`olagandisi`, `dogrulama` ve kodu bilinmeyen `Kisitlandi` hiçbir zaman başka
sağlayıcıya geçirmez**, Flow kilitliyken Vertex yalnız izinle (D-03, D-41); kie.ai ve ikinci hesap hiç kullanılmaz; `--onayli`/`--tam-otomatik`
yerine `FILM_AYAR.json`'da tek `mod` alanı (D-34); testler `sahte` + `kaset` ile `ORNEK_3_SAHNE*` üzerinden (§6.10).

## Kurallar (geliştirmede de geçerli)
- Bot tespitini atlatma yok: fare/klavye taklidi, reCAPTCHA çözme, uyarıdan sonra hangi kipte olursa olsun yeniden başlatma ya da sayfa
  yenileme, tempo hızlandırma, başka hesap yok. Flow uyarısında **her kipte dur** (`03_DERSLER.md`, TASARIM D-02, §10.4).
- Güvenlik korkuluklarını gevşetme: `test_memmet_korkuluk` (T10 her kipte) ve `test_veri_emniyet` her değişiklikte yeşil kalır;
  sayısal güvenlik sınırları yalnız `hat_esikleri.json`'da (`gevsetilemez`).
- Gizli bilgi yazma, loglama, commit etme. `AYARLAR/` içindeki anahtar dosyaları depoda boş kalır; anahtar dosyaları okunmaz, yalnız
  varlığı ve tarihi denetlenir.
- Kullanıcının dosya yollarını bozma (veri `C:\Users\Soysal\Desktop\YZ_FILM`, depo `C:\Users\Soysal\Desktop\YZ_FILM_SET`); yollar
  `ortak.yollar()` ile `YOLLAR.json`'dan okunur, araç kendi konumuna göre aramaz.
- Kalıcı silme yok (eskiler `_ESKI/`'ye taşınır); `robocopy /MIR` yok; `OpenMontage` klasörüne dokunulmaz.
- Testler: `python -m unittest discover -s YZ_FILM/ARACLAR/testler` (ağ ve kredi yok; tek süreç) ya da aynı testleri paralel koşan
  `python YZ_FILM/ARACLAR/testler/kos.py` (CI bunu koşar; yeni test modülü kendiliğinden girer, uzun modül `kos.BOL`'a eklenebilir).
- Küçük, anlamlı commit'ler; yalnız görevde belirtilen dala. PR yalnız istenirse. **Yerelde açılan oturumda** commit ana dala yapılmaz:
  dosyalar `<veri>/GELISTIRME/`'de hazırlanır ve `esitle_gelistirme.py` ile ayrı `yerel/<ad>-<tarih>` dalına gider; birleştirme bulutta PR ile.

## İlk yerel oturum
**Ne zaman:** Kullanıcı Claude masaüstü uygulamasında Code sekmesini `Desktop\YZ_FILM_SET` (depo) klasöründe açıp yalnız `ilk kurulum`
yazdığında ve bu bilgisayarda `O0a.json` yokken (TASARIM §8.2 adım 0b, §9 adım 2). Beceriler geldikten sonra aynı iş `/film-gelistir
ilk-kurulum`'dur (§4.5). Ön koşul: PR-0 ve PR-1 birleşmiş olmalı; değilse hiçbir şeyi değiştirmeden tek cümleyle söyle.
Bu oturumda film başlatılmaz, konu sorulmaz, Flow'a gönderim yapılmaz; kullanıcıdan yalnız fiziksel işler istenir. Python mutlak yolla çağrılır.

1. **Yollar:** `python YZ_FILM/ARACLAR/kurulum.py --yollar` → `YOLLAR.json` (veri kökü yerinde kalır).
2. **Veri kökü emniyeti:** `python YZ_FILM/ARACLAR/kurulum.py --veri-emniyet` (D-02). `<veri>/ARACLAR/memmet.py`, `film.py`,
   `_memmet_yedek_*.py`, `<veri>` altında `memmet.py`'yi çağıran bütün `.bat/.cmd/.ps1` (`MEMMET_*`, `FILM_HATTI`, `CAPCUT_PROJESI_OLUSTUR`,
   B3 `gece_video.ps1`, bulunursa `memmet_dongu.ps1`) ve veri kökündeki `BASLA_BURADAN.txt`, `00_BENI_OKU.txt`, `KURULUM.bat`, `YENI_FILM.bat`
   `_ESKI/`'ye **taşınır** (silinmez); yerlerine emeklilik `.bat`'ı, depo sürümüne giden `memmet.py` sarmalayıcısı ve veri kökü `CLAUDE.md`'si.
   Kabul: `EMNIYET_RAPORU.json`'da yamasız Memmet'e giden giriş noktası 0. Taşınanların listesini kullanıcıya bilgi olarak ver.
3. **memmet3 aktarımı** (sahibi: üretim): kullanıcının yerel memmet3 dosyasını (emniyet onu `_ESKI/`'ye taşıdıysa oradan)
   `<veri>/GELISTIRME/memmet3/` altına kopyala. PR-0'ın bütün maddelerini uygula (D-02 a–g): her kipte uyarıda dur, `elle` kipindeki
   "sayfayı yenile, devam" yolunu ve gece kipindeki 5 yenileme denemesini sil, 17.10 tempo varsayılanı, `FLOW_TEMPO.json` molası,
   çıkış kodları (7, 2, 4), reCAPTCHA'da dur, `_surum` reddi. Yollarını `ortak.yollar()`'a bağla (Chrome profili ve `MEMMET_AYAR.json`
   `<veri>/AYARLAR/`'dan). T10'u her kip için koş (`elle`, `gece`, `dogrulama`). Sonra `python YZ_FILM/ARACLAR/esitle_gelistirme.py --ad memmet3`
   (anahtar taraması + `yerel/memmet3-<tarih>` dalı). memmet3 yerelde ana dala commit'lenmez. Push yetkisi yoksa dosyalar
   `<veri>/GELISTIRME/`'de kalır; kullanıcıya "bu klasörü bir sonraki geliştirme oturumuna ekle" bilgisini ver. Birleştirme bulutta PR ile,
   CI'daki T10'dan geçince olur. **Birleşme olmadan Ö0-b başlamaz.**
4. **Ö0-a:** `olcum0/kanca_deneme/` kancalarını geçici `settings.local.json` ile kur, TASARIM §10.3'teki 20 davranışı tek tek sına,
   `O0a.json`'u yaz (her davranış "çalışıyor / çalışmıyor + yedek"), geçici ayarı geri al. `olcum0/` henüz depoda yoksa bu adımı atla,
   `O0a.json` yazma ve bunu tek cümleyle söyle.

Her adımda: anahtar dosyaları okunmaz; kalıcı silme ve `robocopy /MIR` yok; Flow uyarısı görülürse dur ve haber ver.

### Ö0-a bulguları (ilk yerel oturum, 24.10.2026) ve düzeltmeler
- **#19 Windows `claude.CMD`:** `shutil.which("claude")` npm sarmalayıcısını verir; istemdeki `<…>` cmd.exe'de yönlendirme oldu.
  `ortak.claude_yolu()` gerçek `claude.exe`'yi bulur (PATH'te .exe → `.cmd` yanında `node_modules\@anthropic-ai\claude-code\bin\claude.exe`
  → `.cmd`'nin içinde adı geçen .exe → `%USERPROFILE%\.local\bin\claude.exe` → son çare `.cmd`); `ortak.claude_komutu()` istemi HER ZAMAN
  stdin'den verir (argv'de yalnız sabit bayraklar). `o0a_kos.kor_rol`, `kurulum.py`, `bat_isleri.py` bunu kullanır; yeni kod yalın
  `["claude", …]` ya da `which("claude")` yazmaz (test `ClaudeYolu`).
- **#2/#16 uyanma:** arka plan işinin bildirimi oturuma istem olarak gelir (`<task-notification>` …); sonda `istem_turu`
  (`kullanici` | `sistem`, metin yazılmaz) yazar, `uyandi_mi` yalnız gerçek kullanıcı istemini "uyanmadı" sayar.
- **#7:** `degerlendir 7` alt ajanın yazdığı `{YAZMA}/ajan_yazdi.txt`'yi ölçüp `OTOMATIK.json["7"]`'ye yazar (önce kimse yazmıyordu).
- **#14 UTF-8:** kanca ve sonda çıktısı UTF-8 bayt (JSON yalnız ASCII); `kanca.sh`/`o0a_sonda.sh` `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`;
  geçici `settings.local.json` env'i de.
- **#12 `effort`:** kanca girdisinde anahtar var, değeri yok → `degersiz` (ölçülemedi; madde onunla çalışmıyor sayılmaz); boş elle değer
  yok sayılır.
- **#4:** Agent aracında `name` alanı yok; `isolation: worktree` `origin/main` olmadan başarısız. Sistem ikisini de kullanmaz (kanca
  name/isolation verilen çağrıyı reddeder; görev bağlama istemdeki GOREV.json yolundan); karar yalnız `subagent_type`'a bakar,
  yönerge isolation istemez.
- **#11:** masaüstünde sürdürme aynı konuşmayı açar ama ilk mesaj "devam" olmaz. `kanca.py` resume'da `_GOREV/OTURUM_SURDURULDU.json`
  işareti koyar; sonraki ilk mesaj soru/dur değilse devam sayılır (soru yüzünden kapanmış sürüş açılır; kullanıcının "dur"u açılmaz).
  DEVAM.bat (`claude --continue`) yedek yol olarak kalır; d11 kararı yalnız aynı oturumun sürmesine bakar.
- **Yeniden ölçüm (yerelde):** `o0a_kos.py yeniden` → `kur` → `sira` → `otomatik` → `bitir`. Kullanıcının `O0a.json`'u elle düzenlenmez;
  `bitir` yenisini yazar, eskisini `_ESKI/`'ye kopyalar. Kararlar (`kor_rol_yolu`, `kart_tamam_satiri` …) yeni sonuçlardan yeniden hesaplanır.
