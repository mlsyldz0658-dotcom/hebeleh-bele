# `olcum0/` — ölçüm turu Ö0 betikleri (TASARIM §1.2, §6.1, §9 adım 9)

Ö0, tasarımın ölçülmemiş temellerini ilk filmden önce ölçer. Ö0-1 (b, c, d, e, g) ve Ö0-2 (f, h, Ö0-b·V3), `film.py olcum0`'ın
**sistem görevleridir** ve ilk filmin kâğıt aşamalarıyla (A00–A09) **paralel** yürür: film onları beklemez (Ö0-b sonucu yoksa BUT0
1800 sn seçer, D-05). Bütün sonuçlar `<veri>/BILGI/OLCUM0/O0<harf>.json` + `OLCUM0.json` dosyalarına yazılır (`ortak_o0.py`).

| Dosya | Ölçüm | Kullanıcının işi |
|---|---|---|
| `ortak_o0.py` | ortak yazıcı/okuyucu: `O0<harf>.json` (kararlar üst düzeyde) + `OLCUM0.json` (bölümler + `denemeler`) | — |
| `flow_deneme.py` | **Ö0-b** Flow günlük uyarısız kapasite (merdiven 10/15/20) + A/B çekimleri | her istemde GÖNDER (3 gün) |
| `fikstur/` | Ö0-b istem fikstürü: şema, denetleyici, ŞABLON | — |
| `capcut_deneme.py` | **Ö0-d** pycapcut okuma, klon, segment taşıma, şifre | CapCut'ı iki kez aç-kapat |
| `gemini_deneme.py` | **Ö0-e** 1 Gemini paketi (2 ve 3 aday) + ücretsiz API katmanı (video/ses girişi, görsel kotası, katman) | 1 paket taşımak |
| `kanca_deneme/`, `ses_deneme.py` | Ö0-a, Ö0-c (ayrı iş) | |

Kısayol: `python .claude/bin/film.py olcum0` (durum ve sıradaki görevler) · `python .claude/bin/film.py olcum0 calis <b|c|d|e|g> <alt komut…>`.
Bulutta yalnız `durum` ve `denetle-fikstur` gibi salt okunur alt komutlar koşar; ölçümler kullanıcının bilgisayarındadır.

## OLCUM0 biçimi (okuyan araçlarla uyumlu)
- `olcek.py` / `kredi.py`: `OLCUM0.json` → `O0b.olculen_gunluk_kapasite`, `O0b.olculemedi`, `O0b.uretim_sn_720p`, `O0e.gemini_api_paket`.
  **Ö0-b sürerken `olculen_gunluk_kapasite` anahtarı hiç yazılmaz** (olcek anahtarın varlığını "Ö0-b yapıldı" sayar); kapanınca sayı ya da
  `null` + `olculemedi: true`. `hat_esikleri.json`'daki `olculen_gunluk_kapasite`'ye yerelde yazılmaz (depo dosyası; GUNCELLE.bat bozulur):
  olcek onu bulamazsa OLCUM0'dan okur.
- `saglayicilar/gemini_api.py`, `izleyici`, `dinleyici`: `O0e.json` üst düzey `gemini_katman`, `video_girisi`, `ses_girisi`, `gorsel_uygun`.
- `capcut_yama.py`: `O0d.json` üst düzey `klon` (`"calisiyor"` ise yama açık).
- `plan_dili.py`: `OLCUM0.json` üst düzey `canli_bekleme` — Ö0-b bunu YAZMAZ (karar Ö0-b·V3'tedir).

## Ö0-b istem fikstürü — gerçek 45 istem nasıl yazılır (ilk yerel oturum)
Gerçek dosya **`olcum0/fikstur/O0b_istemler_v1.json`**'dur; bulutta yazılamaz çünkü B3 kareleri yalnız kullanıcının bilgisayarındadır.
`O0b_istemler_SABLON.json` yalnız biçimi gösterir (`"sablon": true`, kareler uydurma) ve `flow_deneme` onu **reddeder**.

Geliştirici Claude, ilk yerel oturumda (`ilk kurulum` / `/film-gelistir ilk-kurulum`; memmet3 aktarımı ve Ö0-a'dan sonra):
1. B3 klasöründe eski iki tur denetimden geçmiş P1 karelerini bulur (PA: 44 kare; B3'ün denetim raporları hangi karelerin geçtiğini söyler).
   Yalnız geçmiş kareler kullanılır (`b3_denetim: "iki_tur_gecti"`).
2. Her kareye `Read` ile bakar ve karede olanı bozmayan, durum değiştiren 2–3 basit fiziksel adımlı bir hareket istemi yazar (D-13):
   ilk adım ≥ 0,5 sn, son adım ≤ 7,0 sn; sağ/sol karakterin kendisine göre; fiiller `veri/fiil_sozlugu.json`'dan; sonuç fiili yok.
   **Filtre/risk/yaş kelimesi yok** (istem_denetim listeleri: child, girl, little, bed, chest, blood, kill, young …) ve politika reddini
   tetikleyebilecek hiçbir şey yok (§10.4). Yedek istem yazılmaz (ret yeniden gönderilmez).
3. Dağılım (şemadaki öneri; her A/B kolunda 12 klip için): **gün 1** 10 `ab` · **gün 2** 14 `ab` + 1 `zincir`(yok) · **gün 3** 20 `zincir`.
   `ab` = 24 istem, 2×2 çapraz (`aralik`/`sira` × `"holds still"`/`"holds the pose, breathing"`), hücre başına 6. `aralik` istemlerinde
   `"0.5-3s: …"` kalıbı, `sira` istemlerinde "First … then …"; bekleme ifadesi istemde **birebir**. `zincir` = 21: `son_kare_ref: "var"` 12
   (`dogal_1280x720` 6, `1376x774_kirp3` 6; `zincir.kaynak` daha önceki günün bir `ab` istemi, `kare_sn` son adım + 0,2 … 7,5; varsa
   `kare` = o planın B3 planlı karesi, G1Z karşılaştırması için) + `"yok"` 9 (B3 planlı karesi). 44 kare 45 istem: bir kare iki istemde
   kullanılabilir. Kol başına < 12 kalan A/B'ler "ölçülemedi → varsayılan" olur; bu bilinçli kabuldür.
4. `kare_sha1`'leri kopyalamadan önce hesaplar ve denetler:
   `python YZ_FILM/ARACLAR/olcum0/fikstur/fikstur_denetim.py <dosya> --b3-kok "<B3 klasörü>"` → **HATA 0** olmalı.
5. Dosyayı `<veri>/GELISTIRME/olcum0/fikstur/O0b_istemler_v1.json`'a koyar ve `python YZ_FILM/ARACLAR/esitle_gelistirme.py --ad o0b-fikstur`
   ile ayrı dala gönderir (birleştirme bulutta PR ile; dosya `olcum0/fikstur/`'a yerleşir). `flow_deneme` önce depo kopyasını, yoksa
   `<veri>/GELISTIRME/...` kopyasını kullanır ve hangisini kullandığını + SHA1'ini `O0b.json`'a yazar. Hazırlıktan sonra fikstür
   değişirse ölçüm durur (yeni sürüm = `v2`, yeni dosya).

## Ö0-b: kullanıcı adım adım
Ön koşul (betik denetler): veri kökü emniyeti (`EMNIYET_RAPORU.json`, yamasız giriş noktası 0) ve ilk yerel oturum bitti (`O0a.json`;
memmet3 birleşti). Son 7 günde Flow uyarısı varsa başlamaz. Tek kip `elle`; çözünürlük 720p.
1. Claude: `film.py olcum0 calis b hazirla --b3-kok "<B3 klasörü>"` (fikstür denetimi, B3 karelerinin SHA1'li kopyası,
   `<veri>/BILGI/OLCUM0/O0b_FILM/` ölçüm klasörü).
2. **Gün 1** — Claude `film.py olcum0 calis b gun`'u arka planda başlatır. Memmet Flow bakiyesini salt okur, Chrome'da 10 istemi sırayla
   hazırlar; **kullanıcı her birinde GÖNDER'e (Oluşturmaya başla) basar.** Tempo 17.10 değerleridir (gönderimler arası bekleme, 8'de bir mola).
   Gün bitince klipler `OLCUM0/O0b_klipler/`'e saklanır.
3. **Gün 2** (ertesi takvim günü; gün 1 uyarısız ve tam bittiyse) 15 istem, **gün 3** 20 istem; aynı iş.
4. Flow "olağan dışı etkinlik" ya da reCAPTCHA gösterirse: **hiçbir şeye basma, sayfayı yenileme, başka hesap deneme.** Memmet durur
   (çıkış 7), Ö0-b o anda **kapanır** ve bir daha açılmaz; o gün ve sonraki 7 gün Flow ölçümü yok. Kapasite = uyarıdan önceki en yüksek
   uyarısız günün video sayısı (gün 1'de uyarı → "ölçülemedi"). Kilidi yalnız `UYARI_GECTI.bat` kaldırır (kendi şartlarıyla).
5. Oturum düşmesi, giriş, arayüz hatası (çıkış 2): sorun giderilince aynı gün `gun` yeniden çalışır, yalnız gönderilmemiş istemler gider.
   Gün ertesi güne kalırsa "yarım gün" sayılır (uyarısız, tam değil) ve merdiven aynı basamakta kalır. Zaman aşımı (8): önce
   `memmet_topla.py --film <O0b_FILM>`; hiçbir klip yeniden gönderilmez.
6. Bitince `O0b.json` + `OLCUM0.json`: `olculen_gunluk_kapasite`, `uretim_sn_720p` (medyan), politika reddinin kredi etkisi (yalnız
   kendiliğinden gelen ret; gün başı/sonu bakiyesinden), A/B kol sayıları (değerlendirme Ö0-b·V3'te), zincir karesi keskinlik oranı.
   Ölçüm harcaması ≤ 540 kr (BUT0'da `olcum0` kalemi; her klip BUTK'dan geçer).

Ö0-b gönderimleri memmet'in kendi `Memmet` sınıfıyla yapılır (`flow_deneme.py memmet-blok`): türetilmiş sınıf **yalnız** `blok_dogrula`'yı
değiştirir — ölçüm klasöründe film animatiği olmadığı için animatik imzası yerine Ö0-b gün yetkisi (`O0B_OLCUM.json` + `O0b.json` günü,
bugünün tarihi, elle kip, 720p, bütçe imzası) aranır. Sayfaya dokunan her işlem, uyarı/doğrulama durdurmaları, tempo, BUTK ve kredi
defteri memmet'in aynı kodudur (`test_olcum0.TestOlcumMemmet`).

## Ö0-d ve Ö0-e kısaca
- Ö0-d: CapCut kapalıyken `calis d hazirla` → kullanıcı CapCut'ta `YZ_O0D_DENEME`'yi açıp kapatır → `calis d olc` (salt okuma + klon +
  1 sn kaydırma; kaynak hiç yazılmaz) → kullanıcı `YZ_O0D_DENEME · klon`'u açıp kapatır → `calis d dogrula`. Şifreliyse ya da klon
  çalışmıyorsa `yayin_kaynagi: master`, not yolu "yeni adla kur".
- Ö0-e: `calis e paket --b3 "<B3>\SAHNELER.json"` (30 plan; 15 × 2, 15 × 3 aday) → kullanıcı paketi Gemini'ye verir, ZIP'i
  `OLCUM0\O0e_PAKET\GELENLER\`'e koyar → `calis e al` → `calis e api --paket-api` (ücretsiz katmanda; ilk 429'da durur; katman bilinen
  "ücretli" ise izin + dolar tavanı yoksa hiç çağrı yapılmaz) → `calis e rapor`. Veri kullanım koşulu `lisans_istegi` olarak yazılır:
  bir geliştirme oturumu `veri/LISANSLAR.json` `gemini_api_ucretsiz` satırını kaynağından doğrular.
