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

## Şu anki durum (23.10.2026)
- **PR-0 tamam** (commit `5878540`, TASARIM §9 adım 0, D-02 a–g): `memmet.py` Flow "olağan dışı etkinlik" uyarısında **her kipte**
  (`elle`, `gece`) anında durur, sayfada başka işlem yapmaz, `HESAP/FLOW_KILIDI.json` yazar ve **7** ile çıkar (kilit varken Memmet
  açılmaz); reCAPTCHA/doğrulama/oturum düşmesinde beklemez, **2** ile çıkar; varsayılan kip `elle` (GÖNDER'e kullanıcı basar; gece
  yalnız `izinler.gece_flow` ile); 17.10 temposu kodda (ayar dosyası yalnız yavaşlatır), `FLOW_TEMPO.json` molayı kalıcı tutar;
  `_surum ≥ 2` → 4; varsayılan 720p. `saglayicilar/flow.py` çıkış kodunu `Kisitlandi(kod)`'a eşler; `film.py` uyarı, doğrulama ve
  bilinmeyen kodda başka sağlayıcıya geçmez. `veri_emniyet.py` + `kurulum.py --veri-emniyet` veri kökündeki eski Memmet ve `.bat`'ları
  `_ESKI/`'ye taşır (silmez). Eski `.bat`'lar depoda `_ESKI/`'de. Testler: `test_memmet_korkuluk` (T10 elle/gece/doğrulama), `test_veri_emniyet`.
- **PR-1 sürüyor** (§9 adım 1): `puan_oku.py` medyan, `izleme_paketi.py`, `ai84.py` tembel anahtar, `ortak.yollar()` + yol göçü +
  `kurulum.py --yollar`, `esitle_gelistirme.py` (dar `esitle --gelistirme`), `esikler.py` ve RE `kaynak`/`etiket`, `veri/ADLAR.json` +
  `test_adlar`, `veri/LISANSLAR.json`, `veri/kok_neden.json`, §2.5 belge düzeltmeleri, bu dosya ve kök `CLAUDE.md`.
- Henüz yok (TASARIM'da tanımlı): `.claude/bin/film.py` (v2 görev defteri), kancalar (`kanca.py`, `settings.json`), `film-yap`/`film-durum`/
  `film-not`/`film-gelistir` becerilerinin `SKILL.md`'leri, 21 ajan dosyası, `olcum0/`. Var olmadıkça geliştirme oturumu bu dosyayı izler.
- Belgelerde anlatılan ama depoda olmayan eski araçlar (`plan_kurgu`, `dudak_denetim`, `diyalog_esitle`, `ses_katmani`, `gemini_paket`,
  `gemini_al`, `gemini_muzik`, `renk_cila`, `taslak_fark`, `animatik`, `birlestir`, `jenerik`, `shorts_mp4`, `kalite_denetim`, `memmet_topla`)
  TASARIM §6'daki adları ve PR adımlarıyla yeniden yazılır.
- Bilinen sınırlar: gerçek müzik kaynağı yok (TASARIM D-25: zincir boşsa müziksiz + BAYRAK); kapak ve YouTube yükleme otomatik değil
  (yükleme P2, onaylı); Flow kısıtı takvimi belirler (atlatma yok, D-02–D-04).

## Uygulama sırası
**TASARIM §9'daki tablo geçerlidir** (her adım küçük bir PR; kabul şartı otomatik test; bir adım bitmeden ona bağlı adım birleşmez).
Kısaca: 0 PR-0 güvenlik (tamam) → 1 PR-1 hızlı düzeltmeler ve temel veri → 2 ilk yerel oturum (aşağıda) → 3 PR-2 görev defteri çekirdeği →
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
- Testler: `python -m unittest discover -s YZ_FILM/ARACLAR/testler` (ağ ve kredi yok).
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
