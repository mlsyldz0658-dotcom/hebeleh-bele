# SON DENETİM — TASARIM.md'nin bağımsız son denetimi

> **Rol:** bağımsız son denetçi (Claude Opus 5.5). **Tarih:** 23.10.2026. **Denetlenen:** `tartisma/TASARIM.md` (2.119 satır).
> **Bu belge karar değildir.** TASARIM'a işlenecek düzeltmelerin listesidir. Hiçbir öneri bir güvenlik kuralını gevşetmez: "uyarıda dur",
> "bot tespiti atlatılmaz", "başka hesaba geçilmez", "anahtar okunmaz ya da yazdırılmaz", "kalıcı silme yok" aynen geçerlidir.

## Okunanlar ve yöntem

| Kapsam | Dosyalar |
|---|---|
| Baştan sona okundu | `TASARIM.md`; `elestiri_seytanin_avukati.md`; `elestiri_seyirci_yapimci.md` §0–§3 (EK1–EK5) ve bütün başlıklar; `BILGI_KURALLARI.md`; `ZANAAT.md`; `ritim_esikleri.json` (148 anahtar sayıldı, `kaynak` alanı taşıyan anahtar 0); `arastirma/01–03`; `FILMLE ILGILI CLAUDE/00–07` ve `HAFIZA_YEDEGI/`; `YZ_FILM/BILGI/CLAUDE_ICIN.md`, `KARARLAR.md`, `YAPIM_REHBERI.md`, `ORNEK_SAHNELER_EMBERFALL_PILOT_20sahne.json` |
| Okunan kod | `film.py`, `saglayicilar/*`, `istem_denetim.py`, `puan_oku.py`, `izleme_paketi.py`, `seslendir.py`, `capcut_film.py`, `ai84.py` (baş), `yeni_film.py`, `testler/test_film.py`, `memmet.py` (baş, `kontrol_noktasi`, üretim döngüsü), `.claude/agents/*.md`, `YZ_FILM/BASLA_BURADAN.txt`, `KURULUM.bat`, `YENI_FILM.bat` |
| Başlık ve hedefli arama | `tur2_*.md` (7 dosya): ★ itirazlar, `gecis_turu` sözlüğü, [UM2] §4.6.1 S1–S15, [CM2] §4.5.1, [YN2] Y3, [SM2] D-MT |

**Etiketler:** **(tahmin)** bu belgede önerdiğim, kaynağı olmayan sayı · **(bellekten, doğrulanmalı)** bu oturumda kaynağını açmadığım bilgi.
**Seviyeler:** **KRİTİK** = bir kesin karar çiğnenir ya da ilk film büyük olasılıkla bitmez · **ORTA** = kaliteyi, takvimi, güvenliği ya da
kullanıcının güvenini ciddi bozar · **KÜÇÜK** = yerel kusur, düzeltmesi ucuz. **Yer:** TASARIM bölümü ve satırı (`TASARIM:N`).
Kısaltmalar TASARIM'daki gibidir (KK1–KK6, [UM2], [CM2], [SA], [ESY], ZN, RE, BK, DR).

---

## 0. Hüküm

TASARIM, eleştirmenlerin on bir KRİTİK maddesinin (ESY EK1–EK5, SA K-1…K-6) çoğunu gerçekten bağlamış: Ö0 ölçüm turu, PR-0 güvenlik
yaması, hesap değiştirme yasağı, token kaydı, kapı/hedef ayrımı, küresel geri dönüş bütçesi, dikey kesit, oyunculuk katmanı ve yayın sahibi
belgede var. Atomik eylem zinciri (KK2), altı özellik (KK3) ve ses kararı (KK4) tam karşılık buluyor; kullanıcıya konu dışında soru sorulmuyor (KK1).

Denetimde dört KRİTİK açık çıktı:
1. **Yarı otomatik (`elle`) Memmet uyarıda durmuyor** ve bu davranış hiçbir yamada yok. Ö0-b tam bu kipte, gerçek hesapta, üç gün koşacak (KK5).
2. **Yama yalnız depoya uygulanıyor.** Kullanıcının masaüstündeki eski Memmet ve eski `.bat`'lar canlı kalıyor (KK5).
3. **Hat kilitlenebilir.** Seyirci kapıları dışındaki kapılarda tur tavanından sonra yol yok; KK1 yüzünden kullanıcıya da sorulamıyor.
4. **Varsayılan ayarda film yayından önce hiç dinlenmiyor.** KK4'ün ana ses yolu doğallık ölçülmeden seçiliyor; ESY EK1 ve EK4 fiilen açık kalıyor (KK6).

**Sayılar: KRİTİK 4 · ORTA 15 · KÜÇÜK 11.**

---

## 1. Bulgu özeti

| ID | Seviye | Bulgu | TASARIM yeri |
|---|---|---|---|
| K-1 | KRİTİK | memmet3'ün `elle` kipi uyarıda durmuyor; PR-0 kapsamı [UM2]'nin P0 güvenlik listesinden dar; Ö0-b bu eksiklerle gerçek hesapta koşuyor | D-02 (171–176), §4.5 (1282), §1.2 Ö0-b (60), §9 adım 0, 2, 9 (2004–2013) |
| K-2 | KRİTİK | Kullanıcının bilgisayarındaki eski Memmet ve `.bat` giriş noktaları yamasız ve canlı kalıyor | D-02, §6.9 (1801), §9 adım 0 (2004), §4.5 (1282) |
| K-3 | KRİTİK | `izleyici`/`dinleyici` varsayılan kapalı; ses ve müzik yayından önce hiç dinlenmiyor; ses motoru doğallık ölçülmeden seçiliyor | D-19 (293–300), §5.6 (1606), §2.2 (468–471, 507–509), §2.3 (519, 535–538, 575) |
| K-4 | KRİTİK | Seyirci dışı kapılarda tur tavanından sonra çıkış yok (kod 6 kilitlenmesi); A16'da kural 8 ile küresel bütçe çelişiyor | §1.1 (44–45), §1.3 (80–101), §1.5 (125–146), §4.2 kural 12 (1191) |
| O-1 | ORTA | İki kök kararına rağmen mevcut araçlar AYARLAR/FILMLER yolunu kendi konumlarına göre arıyor; Memmet profili ve tempo ayarı kaybolur, `.bat`'lar eski araçlara gider | Yer adları (16–18), §5.6 (1610–1613), §6.9 (1798) |
| O-2 | ORTA | Ö0-b…h (adım 9) ölçüm araçları sonraki PR'lara bağlı; §9'daki bağımlılık sütunu yanlış | §1.2 (57–69), §9 adım 9 (2013) |
| O-3 | ORTA | Ö0-b protokolü uyarıyı yokluyor, kendi haftalık kilit kuralıyla çelişiyor; kredi muhasebesi ve örneklem zayıf | §1.2 Ö0-b (60), D-04 (184–188), D-05 (189–193) |
| O-4 | ORTA | Kullanıcı eyleminden sonra "kendiliğinden algılama", hatırlatma ve bloklar arası devam için çalışan süreç yok | §4.2 adım 5 (1199), §8.3 (1962), §8.4 (1978), D-39 (417–421) |
| O-5 | ORTA | Yerel geliştirme oturumu (Ö0-a, memmet3 aktarımı) kullanıcı adımlarında yok; yerelde depoya yazılan dosyalar `GUNCELLE.bat` ile çakışır | §9 adım 2 (2006), §4.5 (1264–1283), D-12 (234), §8.2 (1944–1954) |
| O-6 | ORTA | Seri evreni ve ders defterinin yedeği tanımsız; "git'e yalnız JSON" Windows'ta geçersiz | D-42 (433–435), §5.4 (1508), §2.6 (655), D-33 (394) |
| O-7 | ORTA | Disk kapısının çözümü (`arsivle.py`) P2'de; ilk filmde çıkışsız 8 BEKLE; kullanıcının "sormadan D'ye taşı" kuralı kullanıcı işine dönmüş | D-38 (414–416), §6.1 (1691), §6.9 (1800), §9 adım 20 (2024) |
| O-8 | ORTA | SAHNELER v2 şeması ZN §6.1/Z0 #17 ve AR2 §6.1 ile çelişiyor; ajanlara bu belgelerin dilimleri veriliyor | §5.1 (1340–1437), §2.5 (631–643), §4.6 (1295) |
| O-9 | ORTA | v1↔v2 geriye uyumluluk boşlukları: `parti` anlam değişikliği eski Memmet'in molasını kaldırır; `bitis_karesi`, `motor`, `*_yedek` eşlenmemiş | §5.1 kural 1–2 (1422–1427), §6.1 (1672), §6.4 (1726) |
| O-10 | ORTA | Aynı güvenlik sayıları hem `FILM_AYAR.json`'da hem eşik dosyalarında; "yalnız sıkılaşır" korkuluğu delinebilir | §5.6 (1596–1609), §7.2 (1847–1852), §7.3 (1903–1904), D-34 (400–402) |
| O-11 | ORTA | Kancalar tutmazsa habersizliğin yedeği yok; kapalı başarısızlık doğrulanmamış bir alana bağlı; Ö0-a listesi kullanılan olayları sınamıyor | D-11 (220–227), §1.2 Ö0-a (59), §6.2 (1697), §10.3 (2077–2095) |
| O-12 | ORTA | A07b'de paralel sahne planlaması ile "önceki sahnenin son 2 planı" girdisi birbirini dışlıyor | §1.3 A07b (85), §5.1 (1363), §5.2 (1457) |
| O-13 | ORTA | Depo bulutta açılınca ne olacağı tanımsız; görev gerçekliğinden sapma karar defterinde yok | D-12 (228–234), §1.3 A00 (76), §4.8 (1316–1328) |
| O-14 | ORTA | Yayın müziği zinciri ölçülmemiş tek yola dayanıyor; zincir boşsa davranış yok; kanıtlı Gemini yolu yanlış gerekçeyle kapatılmış | D-25 (338–345), §5.6 (1600), D-41 (430–431), §10.4 (2104) |
| O-15 | ORTA | Flow kilitliyken resmî API yedeği konusunda D-03/R1 ile D-41 çelişiyor | D-03 (177–183), D-41 (426–432), §10.1 R1 (2036) |
| S-1 | KÜÇÜK | Kanonik plan örneği kendi eşiklerini çiğniyor | §5.1 (1387–1404) |
| S-2 | KÜÇÜK | Tanımsız dosya ve araçlar (`pilot_sec`, `ses_olcum`, `MERDIVEN.md` …) | §1.3, §3.3, §7.2, §9 |
| S-3 | KÜÇÜK | Aşama tablosunda girdiyi üreten çağrılar eksik | §1.3 A07a–A07d, A11, A14a, A16 |
| S-4 | KÜÇÜK | Ad çakışmaları ve aynı işi yapan iki araç | §1.3, §5.1, §6.3 (1709–1711), §3.1 |
| S-5 | KÜÇÜK | `_surum`/`_uretim` zarf kuralı kendi örneklerinde uygulanmıyor | §5 (1332), §5.5 (1545, 1566), §5.7–5.8 |
| S-6 | KÜÇÜK | `altyazi_dili: "tr"` örneği ve `baslik` alanının iki anlamı | §5.1 (1347–1348) |
| S-7 | KÜÇÜK | `film-durum`'daki öneri kalıbı KK1 ile gerilimli; "bak" alışkanlığı taşınmamış | §4.3 (1230) |
| S-8 | KÜÇÜK | Etiketsiz ya da tanımsız sayılar; takvim tutarsızlığı | D-23, D-28, §3.1, §1.5 (145), §1.6 (157) |
| S-9 | KÜÇÜK | Lisans ayrıntıları: `pycapcut` ve D-36; OpenVoice'un geçişli bağımlılığı | D-36 (405–408), §6.7 (1778), §6.6 (1758) |
| S-10 | KÜÇÜK | `YOUTUBE_BAGLA.bat` teknik bilgisi az kullanıcı için ağır | D-24 (331–337), §8.2 adım 5 |
| S-11 | KÜÇÜK | reCAPTCHA davranışı belge ile kod arasında tutarsız | §8.4 (1977), §9 adım 0 (2004) |

---

## 2. KRİTİK maddeler

### K-1 · memmet3'ün `elle` kipi uyarıda durmuyor; PR-0 kapsamı dar; Ö0-b bu eksiklerle gerçek hesapta koşuyor
- **Yer:** D-02 (`TASARIM:171–176`), §4.5 `memmet3-aktar` (1282), §1.2 Ö0-b (60), §6.1 `memmet.py` satırları (1671–1672), §9 adım 0, 2, 9 (2004, 2006, 2013).
- **Bulgu:** Kullanıcının bilgisayarındaki Memmet (memmet3) yarı otomatik kipte uyarı görünce durmuyor, kullanıcı sayfayı yenileyip devam
  ediyor. TASARIM memmet3 için yalnız "gece kipindeki 5 yenileme denemesini" siliyor. Varsayılan kip `elle`, Ö0-b de `elle` kipte koşuyor.
- **Kanıt:**
  - `HAFIZA_YEDEGI/olagandisi-dur.md` 18.10 gece notu: "`memmet.py <film> --mod elle`: Memmet referans + istemi hazırlar, GÖNDER'e kullanıcı
    basar; **olağan dışıda durmaz, kullanıcı sayfayı yeniler.** Kullanıcı başındayken varsayılan bu."
  - TASARIM yalnız gece kipindeki otomatik 5 yenilemeyi siliyor (176, 1282). §10.4 (2100) otomatik yeniden başlatmayı ve otomatik sayfa
    yenilemeyi dışarıda bırakıyor. `elle` kipinde Memmet'in durmaması ve kullanıcının sayfayı yenileyip sürmesi hiçbir yerde ele alınmıyor.
    [UM2] S6 ve [SA] K-6 da yalnız gece kipini anıyor.
  - [UM2] §4.6.1 şunları **P0** saydı: S3 (varsayılan tempo 4–12 sn, ara mola yok), S13 (`flow.py` tek tür `Kisitlandi`), S14 (Memmet yeniden
    açılınca mola sıfırlanır). TASARIM'ın PR-0'ı (2004) bunları almıyor, memmet v2'ye (P1, adım 15) bırakıyor. Ö0-b ise adım 9'da, adım 15'ten önce.
  - Bugünkü kodda da aynı boşluk var: `memmet.py:41–49` varsayılanları eski tempodur; `saglayicilar/flow.py:24–25` çıkış 2 → kodsuz `Kisitlandi`,
    yeni çıkış 7 → `RuntimeError`.
  - T10 (1671, 2004) hangi kipte koşacağını söylemiyor.
- **Etki:** KK5'in kendisi. Ö0-b'nin amacı günlük uyarısız kapasiteyi ölçmek; uyarı tam bu ölçümde gelecek. O anda Memmet durmazsa kullanıcı
  alışkanlıkla sayfayı yenileyip GÖNDER'e basar. Hesap B3'teki gibi günlerce işaretli kalabilir (PA "Flow hesabının video tarafı 19.10 gecesi
  işaretli kaldı").
- **Düzeltme:**
  1. PR-0'ın memmet3'e uygulanan sürümü (Ö0-a içinde, Ö0-b'nin ön koşulu) şunları **hepsini birden** içersin:
     a) Her kipte (`elle`, `gece`) olağan dışı metni görülünce Memmet hazırlamayı keser, `FLOW_KILIDI.json` yazar, çıkış kodu 7 verir.
        `elle` kipindeki "kullanıcı sayfayı yeniler, devam" yolu silinir. Kullanıcı GÖNDER'e bassa bile sonraki plan hazırlanmaz.
     b) Gece kipindeki 5 yenileme denemesi silinir (TASARIM'da var).
     c) S3: kodda varsayılan tempo 17.10 değerleridir (`gevsetilemez`). `MEMMET_AYAR.json` daha hızlı bir değer taşıyorsa yavaş olan geçerli olur.
     d) S14: kalan mola `FLOW_TEMPO.json`'dan okunur. Yeniden açılış molayı sıfırlamaz.
     e) S13: `flow.py` çıkış kodunu `Kisitlandi(kod=…)`'a eşler. Kodu bilinmeyen `Kisitlandi` sağlayıcı değiştirmez (kapalı başarısız).
  2. T10 her kip için ayrı koşar. §9 adım 9'un bağımlılığına adım 2 ("memmet3 T10'dan geçti") eklenir.
- **Kabul testi:** `test_memmet_korkuluk` T10-elle ve T10-gece: fikstürde uyarı göründükten sonra hazırlanan istem 0, ≤ 10 sn'de çıkış 7,
  `FLOW_KILIDI.json` var. Boş `AYARLAR` ile açılışta tempo ≥ 17.10 değerleri. `flow.py` çıkış 7 → `Kisitlandi(kod="olagandisi")`, sağlayıcı geçişi 0.

### K-2 · Kullanıcının bilgisayarındaki eski Memmet ve `.bat` giriş noktaları yamasız ve canlı kalıyor
- **Yer:** D-02 (171–176), §9 adım 0 "bulut (yazım + test)" (2004), §4.5 `memmet3-aktar` "depoya kopyalar" (1282), §6.9 eski `.bat`'lar (1801).
- **Bulgu:** PR-0 bulutta, depodaki kopyaya uygulanıyor. memmet3 depoya **kopyalanıyor**; kaynağı (`Desktop\YZ_FILM\ARACLAR\memmet.py`) yerinde kalıyor.
  §6.9 yalnız depodaki `ORNEK_3_SAHNE` `.bat`'larını `_ESKI/`'ye taşıyor. Veri kökündeki eski film klasörlerinin `.bat`'larına dokunan bir adım yok.
- **Kanıt:**
  - `olagandisi-dur.md`: "ARACLAR\memmet.py = memmet3 sürümü". Yani kullanıcının masaüstündeki Memmet bugün hem `elle` kipte durmuyor hem
    gece kipinde 5 kez yeniliyor.
  - Eski film klasörlerinin `.bat`'ları `yeni_film.py:10`'daki göreli yolla (`%~dp0..\..\ARACLAR\memmet.py`) bu kopyayı çağırıyor:
    `MEMMET_BASLAT`, `MEMMET_SADECE_*`, `FILM_HATTI`, `CAPCUT_PROJESI_OLUSTUR` (kapıları atlıyorlar; [UM2] S2).
  - Paketten gelen `YZ_FILM/BASLA_BURADAN.txt` hâlâ bu yolu tarif ediyor (satır 76, 94: "MEMMET_BASLAT.bat → bütün partiler …"). Veri kökündeki
    kopyanın da aynı olduğu varsayılıyor; yerelde bakılmalı.
  - `YENI_FILM.bat` film adını soruyor (`set /p AD=`). KK1'e aykırı bir giriş noktası.
  - Ö0-b B3'ün klasörüyle çalışıyor (60). Kullanıcının alışık olduğu B3 `.bat`'ları tam o sırada elinin altında.
- **Etki:** KK5 ihlalinin yolu üretim makinesinde açık kalıyor. Belgedeki "PR-0 K-6'yı kapattı" iddiası yalnız depo için doğru.
- **Düzeltme:** Ö0-a'nın **ilk** adımı "veri kökü emniyeti" olsun (`kurulum.py --veri-emniyet`, PR-2b):
  1. `<veri>/ARACLAR/memmet.py` ve `film.py` ile bütün `<veri>/FILMLER/*/` içindeki `MEMMET_*`, `FILM_HATTI`, `CAPCUT_PROJESI_OLUSTUR` `.bat`'ları
     `_ESKI/` altına **taşınır** (silinmez). Taşınanların listesi kullanıcıya bilgi olarak verilir.
  2. Taşınan `.bat`'ların yerine tek satırlık bir `.bat` konur: "Bu dosya emekli. Masaüstündeki FILM_SETI.bat'ı kullan." `memmet.py`'nin yerine
     depo sürümünü mutlak yolla çağıran bir sarmalayıcı konur.
  3. Veri kökündeki `BASLA_BURADAN.txt`, `00_BENI_OKU.txt`, `KURULUM.bat`, `YENI_FILM.bat` aynı biçimde emekliye ayrılır. Veri kökü `CLAUDE.md`'sini
     (§4.7) kurulum yazar.
  4. `OpenMontage` klasörüne dokunulmaz (BK §7 #11).
- **Kabul testi:** Kurulum testinde veri kökünde `memmet.py` doğrudan çağrılınca ya depo sürümü (T10'dan geçmiş) çalışır ya da emeklilik mesajı
  basılır. `<veri>/FILMLER` altında yamasız Memmet'e giden `.bat` kalmaz.

### K-3 · Ses ve müzik yayından önce hiç dinlenmiyor; ses motoru doğallık ölçülmeden seçiliyor
- **Yer:** D-19 (293–300), §5.6 `FILM_AYAR.json` (1606), §2.2 Karar 4 (468–471) ve "Kalan sınırlar" (507–509), §2.3 EK1-1 (519), EK4-1 ve EK4-3 (535, 537),
  EK4-4 (538), O-7 (575).
- **Bulgu:** `izleyici` ve `dinleyici` yalnız Gemini API anahtarı ve izinle çalışıyor. Varsayılan `izinler.gemini_api: false`, `usd_tavan_film: 0`.
  Bu varsayılanla:
  - müzik kalite kapısı (D-25) yalnız spektral ölçüyle kalıyor;
  - ses–yüz uyumu ve aksan tutarlılığı "ölçülemedi" oluyor;
  - MOS tahmincisi P2'de;
  - Ö0-c'de ses dönüştürme motoru benzerlik, zarf gecikmesi ve WER ile seçiliyor. Bu ölçülerin hiçbiri fısıltı ve bağırmadaki metalik sesi
    görmez ([SM2] R3, AR3 A2).
- **Kanıt:**
  - D-19 "anahtar varsa **ve** ücretsiz kotadaysa çalışır" diyor. `FILM_AYAR.izinler.gemini_api: false` ücretsiz kotayı da kapatıyor. İki kural çelişiyor.
  - D-24'te YouTube bağlantısı "bir kurulum işidir, soru değildir" sayılıyor. Aynı mantık Gemini anahtarına uygulanmamış.
  - ESY EK1 ("film yayından önce hiç izlenmiyor ve dinlenmiyor") ve EK4 ("müzik ve sesler kulaksız") KRİTİK; SA O-7 ORTA. TASARIM ikisini de "kısmen" sayıyor.
- **Etki:** KK4'ün "en iyi yolu bulun" isteği kulaksız bir ölçüyle karara bağlanıyor. KK6: kalite ölçümü bir varsayılan ayar yüzünden kapalı
  kalıyor, ama ücretsiz yolda ne para ne soru var. Kullanıcı izle-dinle paketini açmazsa ilk dinleyen gerçek seyirci oluyor.
- **Düzeltme:**
  1. §8.2'ye "Gemini API anahtarı (ücretsiz katman)" kurulum adımı eklensin. Bu bir fiziksel iştir (Telegram anahtarı gibi), soru değildir;
     sözleşme kartında yazar.
  2. Kural şu olsun: anahtar varsa ve maliyet 0 ise (ücretsiz kota) `izleyici` ve `dinleyici` açıktır. `izinler.gemini_api` yalnız ücretli kullanımı yönetir.
  3. Ücretsiz katmanın veri kullanım koşulu (Google'ın içerikleri ürün geliştirmede kullanabilmesi; bellekten, doğrulanmalı) `LISANSLAR.json`'a
     ve gizlilik notuna yazılsın, kullanıcıya bir kez bilgi olarak verilsin.
  4. Ö0-c motor kıyasına en az bir doğallık ölçüsü girsin: lisansı doğrulanmış bir MOS tahmincisi (P2'den Ö0'a çekilir) ya da `dinleyici`'nin
     kör ikili karşılaştırması. İkisi de yoksa seçim "ölçülemedi" BAYRAK'ıyla karar defterine yazılsın ve motor örnekleri izle-dinle paketine konsun.
  5. Müzik kalite kapısı `dinleyici` yoksa ÖLÇÜLEMEDİ (= BAYRAK) yazsın; bu, `FILM_SONU_RAPORU`'nda ve yayın paketinde açık eksik olarak görünsün.
- **Kabul testi:** `sahte` Gemini sağlayıcısıyla: anahtar dosyası var ve `usd_tavan_film: 0` iken `dinleyici` çağrılır. Anahtar yokken rapor
  "ölçülemedi" yazar ve bilgi paketi üretilir. Ö0-c raporunda doğallık alanı ya ölçülmüş ya da `olculemedi: true`.

### K-4 · Seyirci dışı kapılarda tur tavanından sonra çıkış yok; hat kod 6'da kilitlenir
- **Yer:** §1.1 çıkış kodları (44–45), §4.2 kural 12 (1191), §1.4 (115–119), §1.3 A01, A04, A05, A07a–d, A08, A09, A10b, A11, A13, A14a, A16
  (77–101), §1.5 sıra kuralı 1 ve 8 (125, 132), küresel bütçe başlığı (134).
- **Bulgu:** Tavan sonrası yol yalnız habersiz seyirci kapıları (§1.4) ve G1, kart, video soyu, ses merdiveni için tanımlı. Öbür kapılarda tavan dolunca
  `film.py` 6 KAPI döner. Ana Claude "film.py'nin cümlesini söyler ve turu bitirir" (kural 12). KK1 yüzünden kullanıcıya "ne yapayım?" diye de sorulamıyor.
- **Kanıt (tavan sonrası tanımsız yerler):**
  - A05: "HATA dönüşleri kâğıt turuna sayılmaz" (81). Yazar ile denetim arasında sayaç yok.
  - A07b: "≤ 2, sonra harita revizyonu 1 kez" (85). A07c: "≤ 2" (86). A07d: "2 tur", KRİTİK kalırsa? (87). A08, A09: "≤ 2" (89–90).
  - A04: bir kez yeniden yazımdan sonra veto sürerse? (80). A10b: ikinci ad da geçmezse? (92). A11: yer tutucu hâlâ > %15 ise? (95).
    A13: `hat-denetcisi` GİTME derse? (97).
  - Sıra kuralı 1 (125): önceki kapılar GEÇ olmadan kredili aşama başlamaz. Yani tek bir planın kalıcı K0/Z0 HATA'sı bütün filmi durdurur.
  - A16 (101) ve kural 8 (132) "KRİTİK = 0 olmadan taslak verilmez" diyor; küresel bütçe (134) ise "dolunca en iyi sürüm + yüzüne vur raporu"
    diyor. Kurgu tavanında KRİTİK > 0 ise iki kural birbirini dışlıyor.
- **Etki:** ≈ 495 plan ve onlarca H kuralı (Y01–Y60'ın H olanları, Z0, Z1, K0) varken en az bir planın bütün turlardan sonra HATA'lı kalması
  olası (tahmin). Hat kalıcı olarak durur; kullanıcı ne yapacağını bilmez. İlk film bitmez.
- **Düzeltme:**
  1. §1.5'e **tavan sonrası genel merdiven** eklensin; `hat/asamalar.py`'de her kapının `tavan_sonrasi` alanı zorunlu olsun:
     (1) aynı sahibin başka kipi (`yonetmen·onarim`, harita revizyonu) →
     (2) üst sahip (`hikaye-yazari·dar_degisiklik`: sahneyi sadeleştir, böl ya da kes; H15 bütçesinden düşer) →
     (3) plan `durdu` + `kurgucu·sifir_kredi` (kâğıtta: planı çıkar ya da köprü kartı koy) + BAYRAK →
     (4) yalnız güvenlik, şema, filtre ve kimlik HATA'ları hattı kesin durdurur; geri kalanı `hedef_alti` ve açık eksik raporuyla sürer.
  2. A05'e `hata_donus_max` (3, tahmin) eklensin; aşılınca `yapimci·doktor`.
  3. Kural 8 şöyle yazılsın: "KRİTİK = 0, **ya da** kurgu tavanı doldu ve KRİTİK'ler açık eksik raporunda listelendi."
- **Kabul testi:** `test_gorev_defteri`'ne yeni senaryo: `kaset` ile bir planı her turda HATA veren fikstür. Hat 6'da kalmaz; plan `durdu` olur,
  rapor yazılır, film sonraki aşamaya geçer.

---

## 3. ORTA maddeler

### O-1 · İki kök kararına rağmen mevcut araçlar yolları kendi konumlarına göre arıyor
- **Yer:** Yer adları (16–18), §5.6 `YOLLAR.json` (1610–1613), §6.9 `bat_yenile.py` (1798), §9 adım 1 ve 2.
- **Bulgu:** TASARIM "bütün yollar YOLLAR.json'dan" diyor, ama hiçbir PR mevcut araçların yol göçünü listelemiyor.
  - `memmet.py:20–21, 40`, `ai84.py:5`, `saglayicilar/__init__.py:14`: AYARLAR'ı kendi dosyalarına göre arıyorlar.
  - `yeni_film.py:7, 35`: FILMLER'i kendi dosyasına göre kuruyor. `yeni_film.py:10`: film `.bat`'ları `%~dp0..\..\ARACLAR\` göreli yolunu kullanıyor.
  - Ö0-a'da depoya kopyalanan memmet3 `<depo>/YZ_FILM/AYARLAR/`'ı arar. Orada ne Flow oturumu açık Chrome profili ne de 17.10 temposunu taşıyan
    `MEMMET_AYAR.json` vardır.
  - `<veri>/FILMLER/<FILM>/` altına kurulan yeni bir `.bat` göreli yolla `<veri>/ARACLAR/`'a, yani yamasız eski araçlara gider (K-2).
  - `bat_yenile.py` yalnız "mutlak Python yolu" diyor, betiğin yolunu söylemiyor.
- **Etki:** İlk yerel çalışmada Flow girişi kaybolur. Tempo varsayılana düşer (KK5, K-1 c). Anahtar "yok" sanılır. Film klasörü yanlış köke kurulur.
- **Düzeltme:** PR-1'e `ortak.yollar()` eklensin. Bu araçların hepsi AYARLAR, FILMLER, EVREN ve SES_KUTUPHANESI yollarını yalnız buradan alsın:
  `memmet`, `ai84`, `saglayicilar`, `kontrol`, `seslendir`, `capcut_film`, `notlari_oku`, `kurulum`, `yeni_film`, `paketle`. `YOLLAR.json` yoksa
  sessiz varsayılan yerine açık hata verilsin. `.bat`'lar hem Python'u hem betiği mutlak yolla çağırsın.
- **Kabul testi:** `test_yollar`: depo ve veri iki ayrı geçici klasördeyken hiçbir araç depo içinde AYARLAR ya da FILMLER oluşturmaz.
  Üretilen `.bat` içinde `..\..\ARACLAR` geçmez.

### O-2 · Ö0-b…h ölçüm araçları sonraki PR'lara bağlı; §9 bağımlılık sütunu yanlış
- **Yer:** §1.2 (57–69), §9 adım 9 "Bağlı olduğu: 0, 3, 4" (2013).
- **Bulgu:** Adım 9, beş ile sekizinci adımlara paralel koşacak diye yazılmış. Oysa ölçümlerin kendisi sonraki adımların ürününe muhtaç:
  - Ö0-b: `elle` kipli Memmet adım 2'de geliyor. "B3 planlarından atomik istemler"in üreticisi yönetmen kâğıdı (adım 8). "V3 tutma" ölçümü
    `kare-tarifcisi` (adım 6) ve `video_denetim` (adım 15) istiyor.
  - Ö0-c: ses kıyası `ses_kiyas` ve K2 ortamı istiyor (adım 13).
  - Ö0-f: "1 kâğıt turu (3 seyirci + eşleştirici)" ajanları (adım 6), `kor_paket` (adım 5) ve hikâye odasını (adım 7) istiyor.
  - Ö0-h: `kare-tarifcisi` ve `sureklilik-denetcisi` (adım 6) ile `kor.py` (adım 12) istiyor.
- **Etki:** Ö0, yazıldığı sırayla uygulanamaz. P1'in sırası Ö0 sonucuna bağlı olduğu için yerel aşamaların planı da kayar.
- **Düzeltme:** Ö0 ikiye bölünsün.
  - **Ö0-1** (adım 9; bağımlılık 0, 2, 3, 4): kendi içinde yeterli betiklerle b-kapasite, c-ses (`olcum0/ses_deneme.py` kendi ortamıyla), d, e, g.
    Ö0-b'nin istemleri geliştirici Claude'un elle yazdığı, sürümlü bir 40 istemlik fikstürdür. Klipler saklanır.
  - **Ö0-2** (adım 12'den sonra): f, h ve Ö0-b kliplerinin V3 değerlendirmesi. Kayıtlı klipler kullanılır, yeniden çekim yapılmaz.
  - §1.2 tablosuna her denemenin bağımlılık sütunu eklensin.

### O-3 · Ö0-b protokolü uyarıyı yokluyor ve kendi haftalık kilit kuralıyla çelişiyor
- **Yer:** §1.2 Ö0-b (60), D-04 (184–188), D-05 (189–193).
- **Bulgu ve kanıt:**
  - Protokol üç ayrı günde günde 20 videoya kadar gidiyor; "ilk uyarıda o günün ölçümü biter". D-04'e göre aynı takvim haftasında ikinci uyarı
    hesabı 7 gün kilitler. Üç ölçüm günü aynı haftaya düşerse protokol kendi kilidini tetikleyebilir. Uyarıyı yoklamak, B3'te günlerce süren
    işaretlenmeyi yeniden üretebilir (H/olagandisi-dur 19.10).
  - "Politika reddinin kredi yakıp yakmadığı" ölçülecek (60), ama yöntemi yazılmamış. Kasıtlı ret tetiklemek hesap riskini artırır.
  - "B3'ün kendi planları, ek kredi değil" deniyor. Oysa B3 kapalı bir proje ("Film işi kapatıldı", `00_OKU_BENI.md`). Bu ≤ 480 kredi ölçüm
    harcamasıdır, B0'da ve sözleşme kartında görünmüyor.
  - ≤ 40 klip birden çok A/B'ye bölünüyor (istem biçimi, canlı bekleme, son kare referansı, zincir karesi). Kol başına ≈ 10 klipte
    "≥ 10 yüzde puanı üstünlük" kararı gürültü içinde kalır (hesap).
- **Düzeltme:**
  1. Merdivenli protokol (tahmin): gün 1 tavanı 10; uyarısız biterse gün 2'de 15, gün 3'te 20. Uyarı gelirse o gün ve sonraki 7 gün ölçüm yapılmaz.
     Ö0-b "uyarıdan önceki en yüksek uyarısız gün" alt sınırıyla kapanır; ikinci uyarı riskine girilmez.
  2. Politika reddi yalnız kendiliğinden gelirse kaydedilir. Kasıtlı tetikleme korkuluk listesine yasak olarak yazılır.
  3. Ö0-b harcaması B0'da "ölçüm" kalemi ve sözleşme kartında satır olsun.
  4. A/B sonuçları "ön karar" sayılsın ve dikey kesitte (A14a) yeniden doğrulansın. Kol başına en az örnek (12, tahmin) tutmazsa karar
     "ölçülemedi → varsayılan" olsun.

### O-4 · Kullanıcı eyleminden sonra "kendiliğinden algılama" için çalışan süreç yok
- **Yer:** §4.2 döngü adım 5 (1199), §8.3 A10d/A11 (1962), §8.4 kredi satırı (1978), §4.4 (1257), A14 ve D-39 (99, 417–421), §8.1 kartı (1927–1941), §10.3 #2 (2079).
- **Bulgu:** Döngü kullanıcı eyleminde "mesajı ilet ve turu bitir" diyor. Belgenin başka yerleri ise şunları vaat ediyor: "ZIP gelince kendiliğinden
  algılanır, 6 saat sonra 1 hatırlatma", "kredi yüklenince sistem kendisi sürer", "CapCut kapanışı kendiliğinden algılanır". Tur bittikten sonra
  bunları yapacak bir süreç tanımlı değil.
  - Bloklar arasında V3 ve G1Z için Claude'un uyanması gerekiyor. Ö0-a #2 yalnız alt ajan bildirimini ölçüyor, arka plan betiğinin oturumu
    uyandırmasını değil.
  - Sözleşme kartında "her işten sonra sohbete devam yaz" işi yok.
- **Etki:** Kullanıcı ≈ 12–24 paket, ≈ 21 blok ve CapCut işlerinin her birinden sonra hattı elle uyandırmak zorunda kalır, ama bunu bilmez. Hat sessizce bekler.
- **Düzeltme:**
  1. Adım 5'e ekle: `film.py bekle --kullanici <id>` arka planda başlatılır. Beklenen eseri yoklar (GELENLER'de ZIP, `KUNYE`'de blok sonu,
     CapCut süreci kapandı, Flow bakiyesi). 6 saatte `bildirim.py` ile hatırlatır. Eser gelince çıkar ve bitişi oturumu uyandırır.
  2. Ö0-a'ya madde ekle: "arka planda biten Bash işi ana tur bitmişken oturumu uyandırıyor mu?".
  3. Tutmazsa sözleşme kartına "her işten sonra sohbete 'tamam' yaz" satırı ve sayısı eklensin (≈ paket + blok + CapCut).

### O-5 · Yerel geliştirme oturumu kullanıcı adımlarında yok; yerelde depoya yazılan dosyalar `GUNCELLE.bat` ile çakışır
- **Yer:** §9 adım 2 (2006), §4.5 `film-gelistir` (1264–1283; `disable-model-invocation: true`, 1274), D-12 (234), §1.2 Ö0-h (66), §8.2 (1944–1954; adım 0, 1947).
- **Bulgu ve kanıt:**
  - Ö0-a ve memmet3 aktarımı kullanıcının bilgisayarında bir geliştirme oturumu istiyor. `film-gelistir` ancak kullanıcı `/film-gelistir` yazarsa
    açılıyor. §8.2'de bu adım ve metni yok.
  - Yerelde depoya yazılan dosyalar var: memmet3 (1282), `veri/kalibrasyon/B3_44.json` (66). `GUNCELLE.bat` = `git pull --ff-only`. İzlenmeyen ya
    da yerelde commit'lenmiş bu dosyalar sonraki çekişte "üzerine yazılır" ya da "ileri sarılamaz" hatası verir ([UM2] R13). Push yasağı (1190)
    bu dosyaların uzak depoya ulaşmasını da kapatıyor.
  - §8.2 adım 0 "GitHub'dan ZIP ya da git clone" diyor. ZIP'te `.git` yoktur; `GUNCELLE.bat` çalışmaz. Depo özelse GitHub girişi adımı da yok.
- **Düzeltme:**
  1. §8.2'ye "tek seferlik geliştirici adımı" eklensin: kurulum sonu ekranı "FILM_SETI.bat'ı aç, şunu yaz: `/film-gelistir olcum0-a`" der. Ya da
     `kurulum.py` Ö0-a'yı kendi başlatır.
  2. memmet3 ve B3 etiketleri yerelde depoya commit'lenmesin. `<veri>/GELISTIRME/` altında hazırlansın. Kullanıcı bu dosyaları bir kez bulut
     geliştirme oturumuna eklesin, yama orada PR olarak birleşsin. Ya da `esitle`'nin yalnız bu iki dosyayı taşıyan dar hâli P0 olsun.
  3. `GUNCELLE.bat` yerel değişiklik ya da izlenmeyen çakışma görürse hiçbir şeyi taşımadan durup tek cümle bilgi versin.
  4. Kurulum yalnız `git clone` ile yapılsın. ZIP'te `GUNCELLE.bat` kapalı kalsın ve bilgi versin. Özel depo için Git Credential Manager girişi §8.2'ye yazılsın.

### O-6 · Seri evreni ve ders defterinin yedeği tanımsız; "git'e yalnız JSON" Windows'ta geçersiz
- **Yer:** D-42 (433–435), §5.4 başlığı (1508), §2.6 KK3f (655), D-33 (394), D-12 (228–233), §4.2 kural 11 (1190).
- **Bulgu:** KK3f "kalıcı" kütüphane istiyor. Windows'ta `<evren>` ve `<veri>/BILGI/DERSLER/` veri kökünde duruyor ve veri kökü git deposu değil
  (D-12 bunu bilerek reddetti). Push da yasak. "Git'e yalnız JSON girer" ifadesi yalnız bulut test kurulumunda doğru.
  "D yedeği"nin sahibi ve zamanı yok. `arsivle.py` P2 ve `/MOVE` ile taşır, yedeklemez.
- **Etki:** Serinin kartları, sesleri, krokileri, leitmotifleri ve öğrenilmiş dersleri tek bir C diskine bağlı (KK3e, KK3f).
- **Düzeltme:**
  1. A18'e `evren.py --yedekle` ve `ders_defteri --yedekle` eklensin: `robocopy /E` (kopya; `/MIR` yasak) ile
     `D:\YZ_FILM_YEDEK\EVREN\<SERI>\` ve `…\DERSLER\` altına.
  2. D takılı değilse BEKLE yerine bilgi verilsin ve yedek sonraki filmin A00'ında yeniden denensin.
  3. A00'da yedeğin sha1 listesi doğrulansın.
  4. "Git'e" ifadeleri ya kaldırılsın ya da `<depo>/YZ_FILM/EVREN_YEDEK/` dışa aktarımı olarak yazılsın; o da yalnız yerel kopyadır.

### O-7 · Disk kapısının çözümü ilk filmde yok
- **Yer:** D-38 (414–416), §6.1 `arsivle.py` P2 (1691), §6.9 `ARSIVLE.bat` P1 (1800), §8.4 (1980), §9 adım 20 (2024), R17 (2052).
- **Bulgu:** Disk kapısı 8 BEKLE verip kullanıcıya "ARSIVLE.bat ile taşı" diyor. `ARSIVLE.bat` P1, çağırdığı `arsivle.py` P2 (ilk filmden sonra).
  BK §7 #10'a göre iş bitince ara klasörler **kullanıcıya sormadan** D'ye taşınır; TASARIM bunu kullanıcı işine çevirmiş.
  Hacim büyük: her plana 2 aday (≈ 1.200 görsel), 405 klip ve yeniden çekimler, 2× büyütme, 4K dışa aktarım (R17).
- **Düzeltme:** `arsivle.py` P1'e (adım 16) alınsın. A16 ve A17 sonunda ve disk kapısında Claude kendisi başlatsın; kullanıcıya düşen tek iş
  "D'yi tak"tır. Taşınanların listesi bilgi olarak verilsin. Son taslağın bağlı olduğu yollar ve dışa aktarılmamış iş taşınmasın (testli).

### O-8 · SAHNELER v2 şeması eğitim belgeleriyle çelişiyor; çelişen dilimler ajanlara veriliyor
- **Yer:** §5.1 (1340–1437), §2.5 (631–643), §4.6 (1295), kurgucu girdisi "ZN §2–§5 dilimi" (849).
- **Bulgu ve kanıt:**
  - ZN §6.1 ve TASARIM §5.1 birçok alanda ayrışıyor:

    | Alan | ZN §6.1 | TASARIM §5.1 |
    |---|---|---|
    | kadraj | `zanaat.kadraj` | `zanaat.kamera.kadraj` |
    | `sure_sn` | yönetmen yazar | `_derlenir.sure_sn`, kod yazar |
    | `kamera_tarafi` | `A/B`, yönetmen yazar (Z0 #17 buna göre) | `"dogu"`, kod hesaplar (1361, 1405) |
    | bakış | `bakis`, yönetmen | `_derlenir.bakis_kadrajda` |
    | dramatik `risk` | plan alanı | planda yok |
    | `yogunluk`, `hedef_duygu`, `merak_*`, `kurulum`, `kullanim_bilgi`, `ironi` | plan alanı, hikâye odası doldurur | planda yok (HIKAYE.json'da) |

  - AR2 §6.1'de `sureklilik` alt nesnesi, `plan_olcegi: "orta"`, `kamera_konumu` ve plan içinde `denetim` var; TASARIM'da bunlar başka yerde.
  - §2.5 yalnız ZN §2.6, §3.7, §5.1, §6.2 (dosya adı), §7.3 ve AR2 §2.3'ü düzeltiyor. ZN dilimleri ise ajanlara GIRDI olarak veriliyor.
  - ZN'nin kendisi "çelişki olursa JSON (RE) geçerlidir" diyor, ama RE'de şema yok.
- **Etki:** Hikâye odası ya da yönetmen, eline geçen ZN dilimine uyup alanı yanlış yere ya da yanlış biçimde yazar. `plan_sema` reddeder ve gereksiz tur döner.
- **Düzeltme:** PR-1 belge düzeltmelerine eklensin:
  1. ZN §6.1 tablosu TASARIM §5.1'in alan ve sahip tablosuyla değiştirilsin, ya da "geçersiz; bkz. `semalar/plan_v2.json`" notu konsun.
  2. ZN Z0 #17 "kamera tarafı `kroki.py` ile `_derlenir`'den" diye düzeltilsin.
  3. AR2 §6.1'in başına "tarihsel öneri; geçerli şema TASARIM §5.1" notu konsun.
  4. RE `eylem_adim_*` açıklamaları yeni adım modeline (konuşma bir adımdır) göre yazılsın.
  5. `test_adlar` ZN ve AR2'deki alan adlarını da tarasın.

### O-9 · v1↔v2 geriye uyumluluk boşlukları
- **Yer:** §5.1 kural 1–2 (1422–1427), `_surum` (1343) ile "zanaat yoksa v1" (1424), §6.1 memmet v2 "yedek istem" (1672), §6.4 `istem_derle` (1726).
- **Bulgu ve kanıt:**
  1. `parti` artık hikâye partisi (1–3). `memmet.py:509–520` molayı parti sayısına göre veriyor. Eski Memmet v2 dosyası görürse ≈ 165 planlık
     partilerde neredeyse hiç mola vermez ([UM2] S15). Eski araçlar v2 dosyasını reddetmiyor. Kural 1'in "eski araçlar okumayı sürdürür" sözü
     tempo açısından tehlikeli.
  2. `bitis_karesi`, `motor` ve `gorsel_istem_yedek`/`hareket_istem_yedek` (CLAUDE_ICIN şeması; `memmet.py:414, 422, 438, 458`) TASARIM'da hiç anılmıyor.
     Memmet v2 "filtre reddinde yedek istem" diyor, ama `istem_derle` yedek istem üretmiyor. Girdisi üretilmeyen bir adım.
  3. v1/v2 ayrımı için iki ayrı kural var (`_surum` ve "zanaat yoksa v1"). Planların bir kısmında `zanaat` yoksa sonuç belirsiz.
  4. `karakterler.<id>.{ref, ses}`'i evrenden kimin dolduracağı yazılı değil. v1 `istem_denetim` ref dosyası yoksa HATA veriyor.
- **Düzeltme:**
  1. PR-0'a ekle: eski Memmet ve eski araçlar `_surum ≥ 2` görürse çıkış 4 ve "Memmet v2 gerekli" mesajı.
  2. Tek ayırt edici `_surum` olsun.
  3. v1→v2 eşleme tablosu yazılsın: `bitis_karesi` → `zanaat.zincir.bitis_sabitle` + `uretim.zincir.yontem: bitis_sabit`; `motor` → `uretim.saglayici`;
     `*_yedek` → `istem_derle --yedek` (filtre-güvenli şablon). Ya da kararla kaldırılsın; o zaman memmet v2 tanımından "yedek istem" çıkar ve
     filtre reddi doğrudan `yonetmen·onarim`'a gider.
  4. `plan_birlestir` `karakterler.<id>.{ref, ses}` alanlarını evrenden doldursun ve kartı `01_KARAKTERLER/`'e kopyalasın.

### O-10 · Aynı güvenlik sayıları iki dosyada; "yalnız sıkılaşır" korkuluğu delinebilir
- **Yer:** §5.6 `FILM_AYAR.json` (1596–1609), §7.2 FLOW, B0/B1, DISK satırları (1847–1852), §7.3 `hat_esikleri.json` (1903–1904), D-32, D-34 (400–402), §5.3 korkuluklar (1503).
- **Bulgu:** `FILM_AYAR.json` şunları taşıyor: `gorsel_gunluk_tavan`, `gorsel_sonrasi_video_saat`, `haftalik_uyari_kilidi_gun`, `kapi_payi`,
  `take_payi_kredi`, `disk_bos_min_gb`. Aynı anahtarlar eşik tablosunda da var.
  - D-34 "aynı anahtar iki dosyada HATA" diyor, ama `FILM_AYAR` eşik dosyası sayılmadığı için bu denetimden kaçıyor.
  - `FILM_AYAR` düz bir JSON ve kullanıcı ayar dosyası. Flow tavanı oradan yükseltilebilir; korkuluk "flow_tavan yalnız düşürür" diyor.
  - `mod: tam_otomatik` ile `izinler.onayli_kip` aynı şeyi iki alanda tutuyor.
- **Düzeltme:** Sayısal güvenlik sınırları yalnız `hat_esikleri.json`'da dursun (`gevsetilemez: true`). `FILM_AYAR` yalnız izin ve tercih tutsun.
  `FILM_AYAR`'da bir sınır yazılmışsa `esikler.py` `min(eşik, ayar)` uygulasın (yalnız sıkılaştırır) ve bunu raporlasın. `mod` tek alan olsun.

### O-11 · Kancalar tutmazsa habersizliğin yedeği yok; kapalı başarısızlık doğrulanmamış bir alana bağlı
- **Yer:** D-11 (220–227; `onFailure: block`, 224), §1.2 Ö0-a "çalışmıyorsa PR-3 birleştirilmez" (59), §6.2 kanca olayları (1697), §10.3 #5 (2083), D-08 (204–209), R5 (2040).
- **Bulgu:**
  - Güvenlik kancalarının kapalı başarısız olması `onFailure: block` alanına dayanıyor; bu alan TASARIM'ın kendisine göre doğrulanmamış.
  - Habersizliğin tek mekanizması `erisim` kancası. Ö0-a kötü çıkarsa ne yapılacağı yazılı değil; R5'te yalnız "betik kapısı" deniyor.
  - Kullanılan dört olay Ö0-a listesinde sınanmıyor: `SubagentStart` (ders satırı), `StopFailure`, `PostCompact` (bağlam geri getirme) ve
    `PostModelSwitch` (D-08 `model_sapmasi`).
- **Düzeltme:**
  1. `kanca.py` kendi içinde kapalı başarısız yazılsın: en üstte try/except, her hatada engelleyen çıkış ya da JSON "deny". Ağır içe aktarma
     olmasın, hedef ≤ 1 sn. Bu, `onFailure` alanından bağımsız çalışır.
  2. Ö0-a'ya eklensin: bu dört olayın varlığı ve `onFailure` olmadan hata veren bir kancanın davranışı.
  3. Habersizlik için yedek mekanizma yazılsın: kör roller ana oturumdaki Agent yerine başsız `claude -p` ile çalıştırılır. Çalışma klasörü
     yalnız `_GOREV/<id>/GIRDI` olur, araçlar yalnız `Read,Write`, ek klasör yok (süreç düzeyinde yalıtım; abonelikle çalışması doğrulanacak).
  4. Model sapması için yedek: model adı SubagentStop dökümünden okunur (Ö0-a #13).

### O-12 · A07b'de paralel sahne planlaması ile "önceki sahnenin son 2 planı" girdisi birbirini dışlıyor
- **Yer:** §1.3 A07b (85), §5.1 `sahne_gruplari.<S>.giris_durumu/cikis_durumu` (1363), §5.2 `sahne_uclari` (1457); [YN2] Y3 aynı.
- **Bulgu:** A07b ≈ 45–55 sahne grubunu "paralel ≤ 5" planlıyor ve girdi olarak "önceki sahnenin son 2 planının çözülmüş bitişi"ni istiyor.
  Paralel koşan bir görev için önceki sahnenin planları henüz yoktur.
- **Düzeltme:** Paralel çalışmada girdi "önceki sahnenin sözleşmedeki `cikis_durumu`" olsun. Çözülmüş plan bitişi yalnız sırayla koşan, aynı mekân
  ve zamanda süren sahne çiftlerinde verilsin. `dilim.py` bu ayrımı yapsın. Uyuşmazlığı A07c K0 (`sahne_uclari.hikaye_esit`) yakalasın;
  `YENIDEN_YAZ` yalnız ilgili iki sahneye gitsin.

### O-13 · Depo bulutta açılınca ne olacağı tanımsız
- **Yer:** D-12 (228–234), §1.3 A00 geçme şartı "K1 kurulum tamam; kanca nabzı" (76), §4.8 (1316–1328).
- **Bulgu:** Görev metninin gerçekliği: "bulut oturumunda yalnız kâğıt aşamaları ve sahte sağlayıcı çalışır". [UM2] §2.7 de kâğıdı bulutta önerdi.
  TASARIM bulutta yalnız testi bırakıyor. Bu bir karar olabilir, ama kullanıcı depoyu bulutta açıp konu verirse ne olacağı yazılı değil.
  Muhtemel sonuç kötü: kullanıcıya konu sorulur, sonra A00 kurulum şartında durur ve 4 ORTAM döner.
- **Düzeltme:**
  1. SessionStart `ortam=bulut` görürse ve aktif film yoksa konu sorulmasın. Tek bilgi cümlesi verilsin: "Film seti bilgisayarındaki FILM_SETI.bat
     ile çalışır; konuyu orada söyle."
  2. Bulutta `film-yap` yalnız `--saglayici sahte` denemesi yapsın.
  3. §4.8'e 12. senaryo eklensin.
  4. Görev gerçekliğinden bilerek sapıldığı, gerekçesiyle karar defterine yazılsın.

### O-14 · Yayın müziği zinciri ölçülmemiş tek yola dayanıyor; zincir boşsa davranış yok
- **Yer:** D-25 (338–345), §5.6 `muzik.yayin` (1600), D-41 "`elle = True` müzik zincirine konamaz" (430–431), §10.4 (2104).
- **Bulgu ve kanıt:**
  - Yayın zinciri `acestep` → `kutuphane`. ACE-Step 1.5'in 4 GB kartta çalışması ölçülmedi (AR3 A5: "≤ 6 GB" katmanı).
  - `kutuphane` basamağı "kullanıcının isteğe bağlı indirmesi"ne bağlı. `elevenlabs_muzik` P2. `midi_ornek` yalnız animatikte.
  - İkisi de yoksa A16'da müziğe ne olacağı yazılı değil.
  - Gemini'de elle müzik yolu "KK1 (elle iş) ve lisans" diye kapatılmış. Ama KK1 fiziksel işi yasaklamıyor; tasarımın kendisi kart ve video
    paketlerini kullanıcıya taşıtıyor. B2'de çalışan tek gerçek müzik kaynağı da buydu (H/uretim-hatti-v2, `04_KIM_NE_YAPTI.md`).
- **Düzeltme:**
  1. Zincir boşsa davranış yazılsın. Önerim: S6 HATA değil BAYRAK; müziksiz kurgu ve izle-dinle bilgisi; açık eksik raporu.
  2. `kutuphane` basamağı K1 kurulumunda lisansı kayıtlı küçük bir çekirdek setle gelsin (CC0 ya da YouTube Ses Kitaplığı; dış indirme izinliyse).
  3. Gemini müzik yolu yalnız lisans gerekçesiyle dışarıda kalsın. `LISANSLAR.json`'da lisans doğrulanırsa `gemini_muzik_paketi` (elle; fiziksel iş;
     sözleşme kartında sayısıyla) zincirin son basamağı olabilsin. "KK1" gerekçesi kaldırılsın.

### O-15 · Flow kilitliyken resmî API yedeği: D-03 ve R1 ile D-41 çelişiyor
- **Yer:** D-03 (182–183), D-41 (429–431), §10.1 R1 "Kalan" (2036).
- **Bulgu:** D-03 resmî Vertex Veo API'sini dolar izniyle "yedek" sayıyor; R1 "Flow kilitliyse resmî API ancak dolar izniyle" diyor. D-41 ise
  `olagandisi`'nin hiçbir zaman başka sağlayıcıya geçirmeyeceğini ve geçişin yalnız `anahtar_yok`, `ortam`, `ag`, `kota` kodlarında olacağını söylüyor.
  Hesap haftalarca işaretli kalırsa (R1) filmin bitip bitmeyeceği bu çelişkiye bağlı. Kullanıcı geçmişte uyarıdan sonra API yolunu kabul etmişti
  (H/olagandisi-dur "ya da API yolu").
- **Düzeltme:** Açık kural yazılsın: otomatik geçiş yoktur (D-41 kalır). `FLOW_KILIDI` varken `veo_vertex` yalnız iki şartla kullanılır: kullanıcı
  ayrıca `izinler.flow_kilitliyken_vertex`'i açmıştır ve `usd_tavan_film > 0`'dır. O zaman `blok_plani` kalan planlara Vertex'i planlı sağlayıcı
  olarak yazar; Flow'a gönderim 0 kalır. Gerekçe D-03'tekidir: ayrı ve resmî bir hizmet atlatma sayılmaz, başka Flow hesabı kullanılmaz.
- **Kabul testi:** Kilit var ve izin yok → Vertex çağrısı 0. Kilit var ve izin var → Flow gönderimi 0, Vertex yalnız bütçe noktasından (BK) geçer.

---

## 4. KÜÇÜK maddeler

**S-1 · Kanonik plan örneği kendi eşiklerini çiğniyor** (§5.1, 1387–1404)
- **Bulgu:**
  - Adım a1 `0.6–1.6` = 1,0 sn; RE `eylem_adim_min_sn` 1,5 sn (Y03 ve Z0 #14 bunu H sayar). [YN2] P121'de de 1,3 sn.
  - Planın `sure_sn` değeri 3,6 sn; ZN §2.3 formülü 7 kelime ve 2 cümle için 3,95 sn veriyor (Z0 #5, H). Formül 1,1 sn'lik L taşmasını hesaba katmıyor.
  - Bu örnek PLAN_DILI.md'ye ve `ORNEK_3_SAHNE_ZANAAT` fikstürüne kopyalanacak.
- **Düzeltme:** `tur: mikro` için ayrı bir alt sınır eklensin (`eylem_adim_mikro_min_sn`, örn. 0,8; tahmin) ya da örnek düzeltilsin.
  Z0 #5'e "L/J taşması görünen süreden düşülür" yazılsın. `test_plan_dili` kanonik örneği HATA'sız geçirmeli.

**S-2 · Tanımsız dosya ve araçlar**
- **Bulgu:** Şunların üreticisi ya da sahibi yok:
  - `pilot_sec` (§7.2, 1849; §9 adım 15): §6 tablolarında yok.
  - `ses_olcum --kontrol` (A10a, 91): `olcum/ses.py` mı, belirsiz.
  - `MERDIVEN.md` (kurgucu girdisi, 849).
  - "tür–kanca tablosu" (yapımcı girdisi, 718).
  - "aksan sözlüğü" (ses tasarımcısı girdisi, 825).
  - `PROJE_KARARLARI.md` (A01 çıktısı, 77): yapımcının çıktı listesinde yok.
  - `FILM_SONU_RAPORU.md`'yi yazan araç.
  - İzle-dinle paketini kuran araç (D-24).
  - FluidSynth ve SF2 dosyalarının kurulum kademesi (`midi_ornek` için; D-37'de yok).
  - Veri kökü `CLAUDE.md`'sini yazan araç (§4.7).
- **Düzeltme:** Her biri sahip araçla §6'ya eklensin. Örnekler: `pilot_sec` → `blok_plani --kesit`; `MERDIVEN.md` → `kuyruk.py --merdiven-md`;
  tür–kanca → `veri/tur_kanca.json` (BK §2'den); aksan → `veri/aksan_sozlugu.json` (`ses_sec --ara` üretir); film sonu raporu → `ders_derle --film-sonu`;
  izle-dinle → `kurgu_render --bilgi-paketi`; FluidSynth → K1. `test_adlar` "üreticisi olmayan girdi = HATA" kuralını denetlesin.

**S-3 · Aşama tablosunda girdiyi üreten çağrılar eksik**
- **Bulgu:**
  - `cekim_listesi.py` (A07d'nin girdisi `CEKIM_LISTESI_P<n>.md`) A07c'de çağrılmıyor. §6.4'te P1 yazıyor, oysa kâğıt aşamasında gerekli (§9 adım 8'de var).
  - `kor_paket --kip kurgu/kesit/kapak` A16, A14a ve A11 satırlarında yok.
  - `kroki.py --ciz` (A07b'nin girdisi olan kroki PNG'si) A07a'da yok.
- **Düzeltme:** §1.3 satırlarına eklensin; `cekim_listesi.py` P0 yapılsın. `asamalar.py`'de her girdinin üreten aşaması zorunlu alan olsun.

**S-4 · Ad çakışmaları ve aynı işi yapan iki araç**
- **Bulgu:**
  - `K1` üç anlamda: kapı (K1 geçiş denetimi), kurulum kademesi (D-37) ve kamera kurulumu (`"kurulum": "K3"`, 1356, 1383). `KK1` de kesin karar.
  - `B0–B2` bütçe noktası, `B1–B3` bölüm. `S0–S8` ses kapısı, `S12` sahne grubu.
  - `hikaye_odasi.py seyirci-topla` (1709) ile `puan_oku.py` v2 `seyirci_topla` (1711) aynı işi yapıyor (D-32'ye aykırı).
  - `ders-editoru` ve `memmet-bakimci` yazar rolünde ama `Edit` aracı yok (§3.1 ilkesiyle tutarsız; en az yetki açısından doğru).
- **Düzeltme:** `ADLAR.json`'da ön ekler: kurulum kademesi `KUR1–3`, kamera kurulumu `KAM1…`, bütçe `BUT0–2`. `seyirci-topla` alt komutu
  `puan_oku.py`'ye yönlensin. §3.1'e "bu iki ajan yalnız yeni dosya yazar" istisnası eklensin.

**S-5 · Zarf kuralı kendi örneklerinde uygulanmıyor** (§5 girişi 1332; §5.5 1545, 1566; §5.7 1618; §5.8 1637)
- **Bulgu:** `FILM_DURUM` ve `GOREV` örneklerinde alan `surum` (alt çizgisiz). Seyirci `rapor.json` ve kapı raporunda zarf yok.
- **Düzeltme:** Tek ad `_surum` olsun. Zarf istisnaları listelensin. Kural `plan_sema` ve `kapi.py` testlerine girsin.

**S-6 · `altyazi_dili: "tr"` örneği ve `baslik` alanının iki anlamı** (§5.1, 1347–1348)
- **Bulgu:**
  - CLAUDE_ICIN'e göre normal filmde `altyazi_dili` `null` olur. `capcut_film.py` bu alan doluysa TR altyazıyı taslağa metin kanalı olarak koyar;
    dışa aktarımda altyazı görüntüye gömülür.
  - `baslik` hem YouTube başlığı (KARARLAR kalıbı) hem CapCut'taki ekran başlığı. `capcut_film.py` kalıplı başlıkta `split("|")[-1]` ile
    "Full Movie 4K 2026"yı ekrana yazar.
- **Düzeltme:** Örnek `null` olsun. `capcut_film --yayin` Altyazi kanalını koymasın (SRT YouTube'a ayrı gider). `SAHNELER.baslik` ekran ya da seri
  adı olsun; YouTube başlığı yalnız `YAYIN/PAKET.json`'da dursun.

**S-7 · `film-durum`'daki öneri kalıbı KK1 ile gerilimli; "bak" alışkanlığı taşınmamış** (§4.3, 1230)
- **Bulgu:** "İstersen şunu yaparım" KK1'den sonra bir karar teklifidir. BK §7 #9'daki "bak denince Claude pencereyi kendisi yakalar"
  (PrintWindow) alışkanlığı tasarıma girmemiş.
- **Düzeltme:** Kalıp bilgi cümlesine çevrilsin: "Ekip şunu yapacak: …; itiraz edersen yaz." `film.py goster pencere capcut` eklensin
  (salt okunur PrintWindow; fare ya da klavye yok).

**S-8 · Etiketsiz ya da tanımsız sayılar; takvim tutarsızlığı**
- **Etiketsiz:** D-23 "≈ 10 plan" (326); D-28 ve §7.2 KART "≥ 3 sabit asimetrik işaret" (365); §3.1 "açıklama toplamı ≤ 3.000 token" (669); A11 "≤ %15" (95).
- **Tanımsız:** §1.5 "film token bütçesi" (145) için anahtar da değer de yok.
- **Takvim:** §1.6 "görsel 4–7 gün" (157) diyor. D-04'ün günlük 20 görsel tavanıyla (tahmin) 116–240 düzeltme gönderimi 6–12 Flow görsel günü eder
  (hesap); üstelik görsel günü video günü olamıyor.
- **Düzeltme:** Etiketler eklensin. `film_token_tavan` `hat_esikleri.json`'a yazılsın (Ö0-f'den; tahmin) ya da ifade kaldırılsın. Belgedeki takvim
  sayıları silinsin; takvim yalnız `olcek.py` çıktısı olsun.

**S-9 · Lisans ayrıntıları** (D-36, 405–408; §6.7, 1778; §6.6, 1758)
- **Bulgu:**
  - D-36 "lisansı bilinmeyen bileşen ana hatta kurulmaz" diyor. `pycapcut` "lisans doğrulanacak" durumda; kural harfiyen uygulanırsa ana teslim
    olan CapCut taslağı kurulamaz.
  - OpenVoice V2'nin (MIT) bağımlılık listesinde AGPL'li `whisper-timestamped` bulunabilir (bellekten, doğrulanmalı). AR3 A4 bu paket için "kullanılmasın" diyor.
- **Düzeltme:** Kullanıcının hâlihazırda kullandığı yerel araçlar (`pycapcut`, `kurgu_koprusu`, `demucs`) için `kullanici_araci: true` istisnası
  konsun; lisansları P0'da doğrulansın. `LISANSLAR.json` geçişli bağımlılıkları da kaydetsin. AGPL'li bir paket çıkarsa ayrı ortamda, yalnız yerel
  çalıştırma olarak not edilsin ya da OpenVoice'ta o kod yolu kapatılsın.

**S-10 · `YOUTUBE_BAGLA.bat` teknik bilgisi az kullanıcı için ağır** (D-24, 331–337; §8.2 adım 5)
- **Bulgu:** YouTube Analytics'e salt okuma bağlantısı, kullanıcının kendi Google Cloud projesini ve OAuth istemcisini gerektirebilir (bellekten, doğrulanmalı).
- **Düzeltme:** Varsayılan yol YouTube Studio'dan tek seferlik CSV dışa aktarımı olsun; adımları BASLA_BURADAN'da yazsın. OAuth P2'ye alınsın.

**S-11 · reCAPTCHA davranışı belge ile kod arasında tutarsız** (§8.4, 1977; §9 adım 0, 2004)
- **Bulgu:** §8.4 "durur; kod 2; kullanıcı `VIDEO_*.bat`'ı yeniden açar" diyor. PR-0 yalnız olağan dışı uyarıyı ayırıyor. `kontrol_noktasi()` reCAPTCHA'da
  12 saat bekleyip kendiliğinden sürüyor (`memmet.py:167–176`).
- **Düzeltme:** Tek davranış seçilsin. Ya PR-0'a reCAPTCHA için de "bildir ve çıkış 2" eklensin ya da §8.4 bugünkü davranışa göre yazılsın.

---

## 5. Kesin kararların uygulanış denetimi

| Kesin karar | Durum | Açık kalan | Bulgu |
|---|---|---|---|
| KK1 Yalnız konu sorulur | Büyük ölçüde | `film-durum` öneri kalıbı; bulutta açılışta konu sorulup sonra durulması; kullanıcı eyleminden sonra "devam" yazma işi kartta yok | S-7, O-13, O-4 |
| KK2 Atomik eylem zinciri | Tam (şema, sözlük, Y01–Y60, V3) | Kanonik örnek kendi eşiğini çiğniyor; RE açıklamaları eski adım modelinde | S-1, O-8 |
| KK3a Animatik ve habersiz seyirci | Tam | Kulak yok | K-3 |
| KK3b Dünya defteri ve zıplama denetimi | Tam | ZN ve AR2 şemalarıyla çelişki; A07b sahne sınırı girdisi | O-8, O-12 |
| KK3c Referansla yüz kontrolü | İnsan için tam; yaratık ve parmak ilk filmlerde BAYRAK (gerekçeli) | — | — |
| KK3d Kare zinciri | Yalnız `devam` geçişinde son kare (gerekçeli) | — | — |
| KK3e Öğrenen ders defteri | Var | Yedek yok | O-6 |
| KK3f Kalıcı seri evreni | Var | Kalıcılık ve yedek tanımsız; "git'e" ifadesi geçersiz | O-6 |
| KK4 Ses ve dudak | Karar yerinde (`veo_donustur` + B planı) | Motor doğallık ölçülmeden seçiliyor; `dinleyici` varsayılan kapalı | K-3 |
| KK5 Memmet ve uyarıda DUR | Belgede tam, uygulamada delikli | `elle` kipi; masaüstündeki canlı eski kopyalar; tempo varsayılanları; Ö0-b protokolü; Vertex çelişkisi | K-1, K-2, O-1, O-3, O-15 |
| KK6 Üstün körü iş yok | Büyük ölçüde | Kulak kapalı; müzik zinciri boş kalabiliyor | K-3, O-14 |

## 6. Eleştirmenlerin KRİTİK maddeleri: son durum

| Madde | TASARIM kararı | Denetim sonucu | İlgili bulgu |
|---|---|---|---|
| ESY EK1 İzlenmiyor ve dinlenmiyor | Kısmen | Varsayılan ayarda karşılanmıyor (dikey kesit ve betik ölçüleri var; kulak yok) | K-3 |
| ESY EK2 Oyunculuk | Uygulandı | Karşılandı | S-1 (örnek) |
| ESY EK3 Gerçek seyirci bağı | Kısmen | Büyük ölçüde karşılandı; OAuth yolu ağır | S-10 |
| ESY EK4 Müzik ve ses kulaksız | Uygulandı ya da kısmen | Varsayılan ayarda karşılanmıyor; müzik zinciri boş kalabiliyor | K-3, O-14 |
| ESY EK5 Paketleme sahipsiz | Uygulandı | Karşılandı | — |
| SA K-1 Flow kapasitesi ve tek hesap | Uygulandı | Kısmen: ölçüm protokolü riskli; resmî API yedeği çelişkili | O-3, O-15 |
| SA K-2 "Yalnız konu" iş yüküyle delinmiş | Uygulandı | Büyük ölçüde; uyandırma işi kartta yok | O-4 |
| SA K-3 Token bütçesi | Uygulandı | Büyük ölçüde; film token tavanının değeri yok | S-8 |
| SA K-4 Ölçmeden P0 | Uygulandı | Kısmen: Ö0 bağımlılıkları yanlış | O-2 |
| SA K-5 Kalibrasyonsuz kapılar, tavansız döngüler | Kısmen | Büyük ölçüde; tavan sonrası yol çoğu kapıda yok | K-4 |
| SA K-6 Kod KK5'i çiğniyor | Uygulandı | Kısmen: `elle` kipi ve masaüstündeki kopyalar açık | K-1, K-2 |

## 7. Döngü tavanı denetimi

| Döngü | Tavan (TASARIM) | Tavan sonrası | Durum |
|---|---|---|---|
| A01 konu denetimi | SubagentStop ≤ 2 | yok | K-4 |
| A03 benzer öneri | 1 yeni eksen | belirsiz | K-4 |
| A04 jüri < 8 ya da veto | 1 yeniden yazım | veto sürerse yok | K-4 |
| A05 yapı ve senaryo HATA | SubagentStop ≤ 2; "HATA dönüşleri sayılmaz" | sayaç yok | K-4 |
| A06 kâğıt seyirci | ≤ 10 tur + plato | kâğıt ürün | tamam |
| A07a–c plan HATA | ≤ 2 + 1 harita revizyonu; ≤ 2 | yok | K-4 |
| A07d plan eleştirisi | 2 tur | KRİTİK kalırsa yok | K-4 |
| A08, A09 | ≤ 2 | yok | K-4 |
| A10b telaffuz | ad başına 1 | ikinci ad da geçmezse yok | K-4 |
| A10d kart | 2 + 2 + en iyi aday | var | tamam |
| A11 ilk geçiş | 1 (+1, yer tutucu > %15 ise) | hâlâ > %15 ise yok | K-4 |
| G1 düzeltme | 2 → kaçış → K0'dan 1 → durdu | var | tamam |
| A12 animatik | 3 + 1 → DUR + kâğıt ürün | var | tamam |
| A13 hat denetçisi GİTME | — | yok | K-4 |
| A14a dikey kesit | plan başına ≤ 2 | kesitte KRİTİK kalırsa yok | K-4 |
| A14 video soyu | 3 → onarım → durdu | var | tamam |
| A15 ses merdiveni | basamaklar | açık rapor | tamam |
| A16 kurgu | 3 + 1 | kural 8 ile çelişiyor | K-4 |
| H15 dar hikâye değişikliği | 2 parti-turu | açık rapor | tamam |
| Stop devamı | 8 ardışık + "film token bütçesi" | bütçenin değeri yok | S-8 |
| Aşama görev sayısı | `olcek.py` × 1,5 | 8 BEKLE | tamam |
| Flow uyarısı | haftada 2. uyarı → 7 gün kilit | var | O-3 (Ö0-b ile çelişki) |
| Ö0-b | 3 gün, ≤ 40 klip | var | O-3 |
| Kullanıcı eylemini bekleme | — | uyanma yok | O-4 |

## 8. Bu denetimin doğrulanmamış dayanakları

| Dayanak | Etiket | Hangi bulgu |
|---|---|---|
| memmet3 `elle` kipinin uyarıda durmaması | Kaynak: `HAFIZA_YEDEGI/olagandisi-dur.md` 18.10 notu; memmet3'ün kodu depoda yok, okunamadı | K-1 |
| `onFailure` hook alanının Claude Code'da bulunması | TASARIM'ın kendisi de "doğrulanacak" diyor (§10.3 #5) | O-11 |
| Gemini API ücretsiz katmanında video ve ses girişi; veri kullanım koşulu | bellekten, doğrulanmalı | K-3 |
| OpenVoice V2 bağımlılıklarında `whisper-timestamped` | bellekten, doğrulanmalı | S-9 |
| YouTube Analytics OAuth'unun Google Cloud projesi gerektirmesi | bellekten, doğrulanmalı | S-10 |
| Arka planda biten Bash işinin oturumu uyandırması; `claude -p` ile kör rol | doğrulanacak (Ö0-a'ya önerildi) | O-4, O-11 |
| Önerilen sayılar (Ö0-b merdiveni 10/15/20, kol başına 12 örnek, `hata_donus_max` 3, mikro adım 0,8 sn) | tahmin | O-3, K-4, S-1 |

## 9. Düzeltmelerin uygulama sırasına yerleşimi

| Bulgu | Yer | Ne zaman |
|---|---|---|
| K-1 | PR-0 genişler; aynı yama Ö0-a'da memmet3'e uygulanır; T10 her kip | Ö0-b'den önce, zorunlu |
| K-2 | `kurulum.py --veri-emniyet` (PR-2b); Ö0-a'nın ilk adımı | ilk yerel oturum |
| K-4 | `hat/asamalar.py` `tavan_sonrasi` + `test_gorev_defteri` (PR-2); §1.5 metni (PR-1 belge) | PR-2 |
| K-3 | §8.2 adımı ve izin kuralı (PR-2b); Ö0-c doğallık ölçüsü (Ö0-1); `dinleyici` (PR-10) | Ö0-c'den önce |
| O-1, O-9 (1–2), O-10 | PR-1 (`ortak.yollar`, `_surum` reddi, eşik tek kaynak) | PR-1 |
| O-2, O-3 | §1.2 ve §9 tabloları (belge); `olcum0/` betikleri | adım 9'dan önce |
| O-4, O-11, O-13 | PR-3 (kanca ve döngü), Ö0-a listesi | PR-3 |
| O-5 | §8.2 ve `GUNCELLE.bat` (PR-2b) | PR-2b |
| O-6, O-7 | `evren.py --yedekle`, `arsivle.py` P1 (PR-12) | ilk filmin A16'sından önce |
| O-8 | §2.5 listesine ZN §6.1, Z0 #17, AR2 §6.1 (PR-1) | PR-1 |
| O-12 | `dilim.py` (PR-6) | PR-6 |
| O-14 | `muzik.py` zincir kuralı, `kutuphane` çekirdek seti (PR-9) | PR-9 |
| O-15 | D-41 metni ve `blok_plani` (PR-11) | PR-11 |
| S-1 … S-11 | ilgili PR'lar; çoğu PR-1 belge düzeltmesi | — |

## 10. En önemli 5 madde

1. **K-1:** memmet3'ün varsayılan `elle` kipi "olağan dışı" uyarısında durmuyor; hiçbir yama bunu ele almıyor. Ö0-b tam bu kipte gerçek hesapta
   koşacak. PR-0 her kipi kapsamalı; T10 her kipte koşmalı; [UM2]'nin S3, S13 ve S14 maddeleri Ö0-b'den önce uygulanmalı.
2. **K-2:** PR-0 yalnız depoyu yamıyor. Kullanıcının masaüstündeki memmet3 ve eski `MEMMET_*`, `FILM_HATTI` `.bat`'ları (B3 dahil) KK5'i çiğner
   hâlde çalışmaya hazır. İlk yerel adım bunları silmeden emekliye ayırmalı.
3. **K-4:** Seyirci dışı kapılarda tur tavanından sonra yol yok. Kod 6'da hat kalıcı olarak durur ve KK1 yüzünden kimseye sorulamaz. Ayrıca A16'nın
   "KRİTİK = 0" kuralı küresel bütçeyle çelişiyor. Genel tavan sonrası merdiveni yazılmalı.
4. **K-3:** `izinler.gemini_api: false` varsayılanı ücretsiz kulağı da kapatıyor. Film yayından önce hiç dinlenmiyor; ses motoru doğallık
   ölçülmeden seçiliyor (ESY EK1/EK4, SA O-7, KK4/KK6). Ücretsiz anahtar bir kurulum işi olmalı; Ö0-c'ye doğallık ölçüsü girmeli.
5. **O-1:** İki kök kararına rağmen mevcut araçlar AYARLAR ve FILMLER yolunu kendi konumlarına göre arıyor. Depoya taşınan Memmet Flow oturumunu
   ve 17.10 tempo ayarını bulamaz; yeni film `.bat`'ları eski araçlara gider. Yol göçü PR-1'e girmeli.
