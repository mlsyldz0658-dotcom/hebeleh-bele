# TUR 1 — SENARİST UZMANI: Hikâye odası süreci

Hazırlayan: senarist uzmanı (Claude Opus 5.5, bağımsız; diğer uzmanların dosyaları okunmadı). Tarih: 23.10.2026.
Durum: TAMAM (1. tur). Teslim biçimi: 9 başlık, görevde istenen sırayla.

**Kısaltmalar (kaynak):** `BK` = `BILGI_KURALLARI.md`, `ZN` = `ZANAAT.md`, `RE` = `ritim_esikleri.json` (anahtar adıyla),
`AR1/AR2/AR3` = `arastirma/01_film_hatlari.md` / `02_sureklilik.md` / `03_ses_ve_claude_code.md`, `UH` = `01_URETIM_HATTI.md`,
`DR` = `03_DERSLER.md`, `YR` = `YAPIM_REHBERI.md`, `KR` = `KARARLAR.md`, `AN` = `ARASTIRMA_NOTLARI.md`,
`OB` = `FILMLE ILGILI CLAUDE/00_OKU_BENI.md` ve `05_PROJELER_VE_ARSIV.md`.
Kaynağı olmayan her sayı **(tahmin)** diye işaretlidir ve ilk iki filmin verisiyle ayarlanmalıdır.

**Bu belgenin tek cümlelik özü:** Kullanıcının tek cümlelik konusu, makinenin denetlediği bir **brifinge**, 4 bağımsız
mimarın birbirinden *zorla farklı* önerisine, 5 kişilik kör jüriye, kazanan yazarın **3 parti × 8 başlıklık** yapısına ve
sahne sahne **ekran metnine** dönüşür; bu metin yalnız ekranda görülen/duyulanı okuyabilen (araçla zorlanmış) 3 habersiz
seyirciden **medyan 8/10** alana kadar aynı yazar tarafından düzeltilir; sonunda yönetmene sözleşmeli bir `HIKAYE.json`,
seri evreni kütüphanesine de hikâye kaydı gider.

---

## 1. Alanımın hedefi ve başarı ölçütü (sayılarla)

### 1.1 Alanım (ne benim, ne değil)
- **Benim:** konu → brifing; öneri çeşitliliği (mimarlar, tonlar); jüri ve seçim kuralı; 3 parti × 8 başlık; sahne sahne
  senaryo (ekran metni + İngilizce replikler); kâğıt üstü habersiz seyirci döngüsü (hikâye düzeyi) ve v2…vN revizyonu;
  oyuncu (karakter) ve diyalog denetimi; başlık/kanca/kapak vaadinin hikâyeye gömülmesi (vaat sözleşmesi, bölüm adları,
  Short adayları, seri kancası); seri evreni kütüphanesinin **hikâye tarafı** (karakter yayları, evren kuralları, NE YOK
  listesi, kanon, bilgi durumu, ad sözlüğü).
- **Benim değil (yalnız sözleşmesini yazarım):** plan plan çekim listesi, kadraj, eylem zincirinin saniyeleri, istem
  derleme (yönetmen/istem mühendisi); görsel/yüz denetimi; ses yöntemi ve LUFS; müzik; kurgu; yayın paketinin üretimi.
  Bunlara hikâye odasından giden **girdiler** bu belgede tanımlıdır (§5.2 `HIKAYE.json`).

### 1.2 Başarı ölçütleri (kapı = geçmeden yönetmene devir yok)

| # | Ölçüt | Eşik | Kaynak |
|---|---|---|---|
| S1 | Kâğıt üstü habersiz seyirci GENEL puanı (3 bağımsız seyircinin **medyanı**) | **≥ 8** | RE `seyirci_genel_esik`, ZN §7.3, CLAUDE.md |
| S2 | Hiçbir ölçütün medyanı (anlaşılırlık, akıcılık, merak, duygu, ritim, ilk30) | ≥ 7; anlaşılırlık/akıcılık/merak/ilk30 hedef ≥ 8 | RE `seyirci_olcut_min`, `seyirci_olcut_hedef` |
| S3 | KRİTİK kopukluk / ORTA kopukluk (parti başına, 3 seyircinin birleşimi) | 0 / ≤ 3 | RE `kopukluk_kritik_max`, `kopukluk_orta_max_parti` |
| S4 | Seyircinin özeti ↔ hikâye odasının kontrol önermeleri anlamsal eşleşmesi | ≥ %80 | RE `ozet_eslesme_min` |
| S5 | İlk 2 dakika testi ("devam eder miydin?") | 3 seyircinin 3'ü "evet" | RE `ilk2dk_devam_evet_min`, ZN §7.2.2 |
| S6 | Hikâye düzeyindeki Z1 (bilgi) ve Z2 (duygu) maddelerinde HATA | 0 | ZN §6.2 Z1 #21–34, Z2 #35–39 |
| S7 | Her parti tek cümleyle savunulabiliyor; her sahnede `sahne_degeri.bas ≠ son` | %100 | ZN §7.2.3, §7.2.4 |
| S8 | Kâğıt seyirci tur sayısı | ≤ 4 (aşılırsa §2 H11 kuralı) | RE `kagit_tur_max` |
| S9 | Jüri: kazanan önerinin ölçüt ortalaması | ≥ 8,0/10 **(tahmin)**; dayanak: EMBERFALL'da iki öneri 420/500 = 8,4 aldı (YR A3) | YR A3 |
| S10 | Vaat sözleşmesi: başlıktaki her öğe ve kapak imgesi ekranda gerçekleşiyor; vaat imgesi | %100; ≤ 120 sn | RE `vaat_imgesi_max_sn`, ZN §1.4, BK 1.7.6 |
| S11 | Oyuncu denetimi: "karakter dışı" ya da "bilmediği şeyi bilen" replik | 0 KRİTİK | ZN §7.2.5, AR1 A1 |
| S12 | Toplam replik kelimesi (40 dk film için; süreyle oranla) | 2.100–2.600 kelime | ZN §2.6 |
| S13 | Sahne sayısı / sahne süresi | 45–55 sahne (40 dk) / her sahne ≤ 180 sn | ZN §2.4, RE `sahne_max_sn` |
| S14 | Replikler filtreye ve klibe uygun (yasak kelime, ≤ 16 kelime/8 sn klip) | 0 HATA | DR, RE `replik_max_kelime_8sn`, `istem_denetim.py` |

### 1.3 Alt akış (downstream) ölçütleri — hikâye odasının işi doğru yaptığının gecikmeli kanıtı
Bunlar hikâye odasının kapısı değildir; ama ders defterine (özellik e) "hikâye odasının karnesi" olarak yazılır.
- Animatik habersiz seyircisinde **hikâye kaynaklı** (`tur: hikaye` — bilgi eksik, motivasyon, kurulum) KRİTİK = 0;
  hikâyeye geri dönüş en çok 1 tur **(tahmin)**. Geçmişte bu boşluklar ancak kurguda yakalandı: B2 ilk taslak "bilmesem ne
  izledim derim" (H/kurgu-izleme-denetimi), B1'de babanın adı 84. çekimde (YR A8).
- Kurgu izleme seyircisinde aynı 6 ölçütle GENEL ≥ 8 (geçmiş seyir: B2 P1 5 → 7, B3 kâğıt 6/8/7 — BK 3.9, OB).
- Yayın sonrası (kapı değil, yalnız kayıt): izlenme, ilk 30 sn tutma, ortalama izlenme süresi. **Bugün elimizde tutma
  verisi yok** (BK 1.8.5). Kıyas tabanı: B1 ana video ≈ 671 izlenme, 6 abone (OB). Hikâye kalitesinin izlenmeyi tek
  başına getireceğini iddia etmiyorum; ders defterine kanıt olarak girer.

### 1.4 Bütçe (kredi değil, emek)
Hikâye odası **Flow/AI84 kredisi harcamaz** (ZN K8). Harcadığı, Claude kullanım hakkıdır. Tahmini ajan çağrısı:
konu 1 + mimar 4 + jüri 5 + senarist 3–6 + oyuncu/diyalog 5–6 + seyirci 3×(1–4 tur) + anlama ölçer 3×(1–4) + ilk 2 dk 6 +
doktor 0–1 + evren 1 ≈ **35–60 çağrı (tahmin)**. Kesin karar 6 gereği bu sayı kısılmaz; kullanım sınırına takılırsa iş
dosyalarda kaldığı yerden sürer (YR §1 altın kural 3, AR3 B6).

## 2. Aşama aşama süreç: her adım için girdi → iş → çıktı dosyası → geçme şartı → kim yapar (ajan/betik/ana Claude)

Çalışma klasörü: `<film>/_HIKAYE_ODASI/`. Her aşamanın çıktısı dosyadır; `film.py` her aşamayı `FILM_DURUM.json`'a
imzasıyla yazar (girdi değişirse aşama yeniden açılır — mevcut `imza()` mantığı). "Kim" sütunu: **AC** = ana Claude
(yönetmen-yapımcı; kendisi puan vermez, tarafsız kalır — YR §1), **betik** = Python (deterministik, ağsız), **ajan** = `.claude/agents/` alt ajanı.

### Genel akış (kâğıt üstü; kredi yok)
```
H0 konu_al ─► H1 konu_karti ─► H2 brifing ─► H3 oneriler(3 paralel + bonus) ─► H4 oneri_denetim
   ─► H5 juri(5 paralel) ─► H6 secim ─► H7 yapi(3 parti × 8 başlık) ─► H8 senaryo v1
   ─► H9 oyuncu + diyalog denetimi ─► H10 senaryo_denetim (Z1/Z2/filtre/kanon) ─► H11 kâğıt seyirci döngüsü (≤4 tur)
   ─► H12 ilk 2 dakika testi ─► H13 kilit ve devir (HIKAYE.json → yönetmen) ─► … (film biter) … ─► H14 evren kaydı
```

### H0 — Konu al (kullanıcıya sorulan TEK soru)
- **Girdi:** yok (ya da kullanıcının ilk mesajı zaten bir konu içeriyorsa o).
- **İş:** AC yalnız şunu sorar, başka hiçbir şey sormaz (kesin karar 1):
  > "Filmin konusu ne olsun? Bir cümle yeter (ör. *ejderha yavrusunu saklayan avcı kadın*). İstersen **sen seç** yaz."
  Kullanıcı konunun yanında bir istek söylerse ("komik olsun", "uzay geçsin") o da **kesin istek** olarak kaydedilir; ama
  ekip ona soru sormaz. Belirsizlik varsa AC sormaz, **varsayım** yapar ve deftere yazar (H1).
- **Çıktı:** `_HIKAYE_ODASI/00_KONU.txt` (kullanıcının sözü aynen, tarih).
- **Geçme şartı:** dosya boş değil. `film.py` bu dosya yoksa `Durdur("Konu bekleniyor")` verir.
- **Kim:** AC.

### H1 — Konu kartı (konudan karar vermeye)
- **Girdi:** `00_KONU.txt`; kanal kararları (`AYARLAR/KANAL_KARARLARI.json` → yoksa `BILGI/KARARLAR.md`); seri evreni
  kütüphanesi (`YZ_FILM/EVREN/*/EVREN.json`); ders defteri (`hikaye` etiketli dersler); BK §1–2 (kazanan kalıplar).
- **İş (ajan `konu-analisti`):**
  1. **Seri tespiti:** konu bir evren adını ya da kayıtlı karakteri anıyorsa `seri: devam`; yoksa `seri: yeni`.
     Varsayılan **yeni evren** (EMBERFALL kapatıldı ve izlenme almadı — OB; kullanıcı açıkça anmadıkça geri çağrılmaz).
  2. **Tür ve kanca ailesi eşlemesi** (aşağıdaki tablo). Konu birden çok aileye düşüyorsa birincil + ikincil seçilir.
  3. **Vaat imgesi taslağı:** kapakta görülecek tek kare (BK 1.7: insan + yaratık/uzaylı aynı karede, soğuk/doğa tonu).
  4. **Risk taraması:** küçükler filtresi (insan çocuk ana karakter mi?), şiddet/kan, telif (var olan eser/gerçek kişi —
     konu "Harry Potter gibi" ise yalnız *tür hissi* alınır, ad/olay/tasarım alınmaz), Flow'da zayıf işler (kalabalık
     savaş, su altı, hızlı dövüş koreografisi, ekranda okunacak yazı — `uretilebilirlik-denetcisi` listesi), anime tarzı
     (Flow'da tutarlılık zor — BK 1.9.2).
  5. **Varsayım defteri:** her belirsizlik için `karar — neden — yanlışsa maliyeti` (AR3 B6 biçimi).
  6. **"Sen seç" modu:** konu yoksa ajan, kazanan kanca ailelerinden ve evren kütüphanesindeki boşluklardan 3 konu adayı
     yazar; her adayı 4 ölçütle (kanca gücü, tür talebi BK 1.2, üretilebilirlik, seri potansiyeli) puanlar ve en yükseğini
     seçer. Kullanıcıya sorulmaz; seçim gerekçesiyle deftere yazılır.
- **Çıktı:** `01_KONU_KARTI.json` (şema §5.1) + `01_VARSAYIMLAR.md`.
- **Geçme şartı (betik `hikaye_odasi.py konu-denetim`):** zorunlu alanlar dolu; `kanca_ailesi` sözlükten; `riskler[]`
  her biri `cozum` alanlı; telif riski `yuksek` ise `donusum` alanı dolu.
- **Kim:** ajan `konu-analisti` → betik.

**Konu sinyali → kanca ailesi → mimar eksenleri** (kaynak: kanca aileleri BK §2.1 ve AN T14–16; eksen fikri benim):

| Konu sinyali | Kanca ailesi (kazanan örnek) | Eksen D (duygu motoru) | Eksen S (sır motoru) | Eksen E (eylem motoru) |
|---|---|---|---|---|
| yaratık, ejderha, uzaylı, canavar | **insan + yaratık bağı** ("She Raised a Monster They Tried to Kill", 3,3M) | ebeveynlik / sahiplenme | saklama, dramatik ironi | kaçış, takip |
| taht, krallık, kardeş, miras | **ihanet ve taht** ("His Brother Stole The Crown", AGE OF KINGDOMS 12–14M) | aile yarası | komplo, çifte ajan | taht savaşı, kuşatma |
| asker, savaş, ordu | **orduya/topluma karşı seçim** ("He Chose the Alien Woman Over the Army") | sadakat ikilemi | emir ile vicdan | görev, kurtarma |
| zayıf, alay, sürgün, köle | **küçümsenen kahramanın geri dönüşü** (manhwa mantığı [H], BK §2.2) | onur, kabul | gizli güç/kimlik | sınav, turnuva |
| kıyamet, dev yaratık, robot | **hayatta kalma + bağ** (Domain Filmes 10/18 ≥1M) | koruyucu ile korunan | felaketin sebebi | yolculuk, sığınak |
| köy, aile, ahlak | **ahlak draması** (Dramaplace medyan 1,8M) | aile sırrı | yalan, iftira | yüzleşme |

Her filmde mimarlara **farklı eksen zorunlu verilir** (H3). Birincil kanca ailesi ortak kalır: dört öneri aynı konuyu
dört farklı *motorla* çalıştırır. Bu, "bağımsız ama birbirine benzeyen öneriler" riskini baştan azaltır.

### H2 — Brifing
- **Girdi:** `01_KONU_KARTI.json`, `01_VARSAYIMLAR.md`, kanal kararları, evren (devam ise), ders defteri, `RE`, DR filtre listesi.
- **İş:** Betik `hikaye_odasi.py brifing` **kalıp bölümleri** doldurur (elle yazılmaz, her filmde aynı ve güncel):
  1. Kanal ve izleyici (BK §1: profil, kazanan kanallar tablosu, süre verisi, YZ'ye tavır, "tek büyük eleştiri karakter tutarsızlığı").
  2. Kullanıcının kesin istekleri: `00_KONU.txt` + kalıcı kanal imzaları (anlatıcı yok; İngilizce; 30–45 dk, hedef 40;
     yavru yaratık aşırı şirin, yetişkini heybetli; küçük güzel sahneler — BK §2.5, §2.10).
  3. **Üretim sınırları** ZN K1–K9 + filtre kelimeleri + NE YOK kuralı + ≤ 2 referans + tek konuşan + replik ≤ 16 kelime.
  4. Ritim ve yapı iskeleti: ZN §1.2 üç parti × vuruş tablosu, §1.3 eğri, §4 bilgi yönetimi eşikleri (kısa özet + "makine denetler" notu).
  5. Ders defterinden `hikaye` etiketli **doğrulanmış** dersler (özellik e) — her biri kanıtıyla.
  6. Teslim başlıkları (H3'teki şablon) ve dosya adı.
  AC yalnız iki bölümü kendisi yazar: **(7) bu filmin konu yorumu** (konu kartından 1 paragraf) ve **(8) mimar eksen ataması**.
- **Çıktı:** `00_BRIFING.md` (Türkçe; görsel tarif ve replik örnekleri İngilizce).
- **Geçme şartı:** betik 8 bölümün varlığını, filtre listesinin güncel `istem_denetim.FILTRE_KELIMELERI` ile aynı olduğunu
  ve dosyanın 1.500–4.000 kelime arasında olduğunu **(tahmin)** denetler.
- **Kim:** betik + AC.

### H3 — Öneriler: kaç mimar, hangi tonlar
- **Girdi:** `00_BRIFING.md` (hepsine aynı), mimar başına eksen satırı.
- **İş:** **4 mimar** (YR A2: "3–4 mimar + bonus; en özgün fikir genelde bonustan çıkar"):
  - **M-D** (duygu motoru), **M-S** (sır/ironi motoru), **M-E** (eylem/macera motoru): aynı anda, paralel, birbirini okumaz.
  - **M-X bonus "beni şaşırt":** ilk üçü bitince başlar. Ona ton verilmez; yalnız ilk üç önerinin **tek cümlelik logline'ları**
    "kaçınılacak yollar" olarak verilir. Bu, YR'nin bağımsızlık kuralına bilinçli ve dar bir istisnadır: amaç bonusun
    farklılığını garantilemektir; mimarlar yine birbirinin metnini okumaz (§9 açık soru 1).
  - **Seri devamı ise** tonlar: A *sadık* (evrene ve açık seri sorularına sadık), B *sürpriz*, S *sır*, X bonus (UH §1, BK 2.7).
- **Her önerinin teslim başlıkları** (şablon brifingde; makinece aranır):
  1. Logline (tek cümle, ≤ 35 kelime) · 2. **Başlık adayları ×3** (kalıp `Kanca cümlesi | SERİ ADI | Full Movie 4K 2026`)
  + **kapak imgesi** (filmde gerçekten olan tek kare) · 3. Karakterler: ≤ 4 ana konuşan, toplam konuşan ≤ 8; her biri için
  istek/korku/yara/sır, **yay** (başta → sonda), görsel ayırt edici (siluet, renk), ses tarifi (yaş, tını, aksan), ad
  (§7.4 ad kuralları) · 4. Evren kuralları (3–5) + dönem + renk paleti + **NE YOK listesi** · 5. 3 partinin tek cümlelik
  savunması + vuruş listesi (ZN §1.2 dakikalarıyla) · 6. Soğuk açılış (ilk 30 sn, plan plan değil ama an an) ve ilk 2 dk ·
  7. Merak soruları taslağı (≥ 8), kurulum → kullanım taslağı (≥ 5), ironi zinciri (her partide ≥ 1) · 8. "Küçük güzel
  sahneler" (≥ 1/parti) · 9. Seri kancası + sonraki filmin tek cümlelik tohumu · 10. Üretilebilirlik notu (riskli sahneler
  ve çözümü, mekân sayısı, kostüm varyantı sayısı).
- **Çıktı:** `02_oneri_D.md`, `02_oneri_S.md`, `02_oneri_E.md`, `02_oneri_X.md` (her biri 2.500–5.000 kelime **(tahmin)**).
- **Geçme şartı:** H4.
- **Kim:** 4 × ajan `hikaye-mimari` (Opus, effort high).

### H4 — Öneri denetimi (mekanik, jüriden önce)
- **Girdi:** 4 öneri, brifing.
- **İş (betik `hikaye_odasi.py oneri-denetim`):** 10 başlık var mı; başlık adayı kalıba uyuyor mu (regex, ≤ 100 karakter —
  YouTube başlık sınırı); konuşan karakter ≤ 8; ad kuralları (§7.4); filtre ve NE YOK kelimeleri öneri içindeki İngilizce
  örnek repliklerde var mı; **çeşitlilik ölçüsü:** iki önerinin (kahraman tipi, çekirdek ilişki, doruk mekanizması,
  ana mekân) dörtlüsünden ≥ 3'ü aynıysa `BENZER` bayrağı **(tahmin eşiği)**.
- **Çıktı:** `_RAPOR/ONERI_DENETIM.json`.
- **Geçme şartı:** her öneride HATA = 0. HATA varsa öneri **aynı mimara** döner (en çok 2 kez). `BENZER` varsa
  puanı düşük olan değil, **bonus dışındaki** benzer öneri yeni bir eksenle yeniden yazdırılır (1 kez).
- **Kim:** betik; düzeltme aynı ajan.

### H5 — Jüri (kullanıcı seçmez; kör jüri + kodla karar)
- **Girdi:** brifing, 4 öneri (adları **anonimleştirilir**: "Öneri 1–4", eksen bilgisi silinir — betik yapar), jüri tablosu.
- **İş:** 5 bağımsız jüri (YR A3 rolleri; hepsi Opus — §3'te gerekçe), birbirini okumaz:
  1. **İlk kez izleyen seyirci** (merak, anlaşılırlık, "bir film daha" isteği)
  2. **YouTube stratejisti** (BK §1 verisine dayanarak tıklanma, başlık/kapak vaadi, seri potansiyeli)
  3. **Tür uzmanı** (konuya göre persona: fantastik/bilimkurgu/tarihî…; özgünlük, klişe, "hit kopyaları tutmuyor" BK 1.3.2)
  4. **Duygu ve karakter eleştirmeni** (bağ, yay, duygunun hak edilmesi)
  5. **Üretilebilirlik denetçisi** (K1–K9, süreklilik yükü, filtre; aşırı temkin uyarısı YR A5)
  **10 ölçüt × 1–10** (her puan gerekçeli; tablo benim önerim, YR'deki tablo depoda yok):
  `kanca` (başlık+kapak+ilk 30 sn vaadi) · `netlik` (kim/nerede/risk) · `merak` (soru motoru, parti sonları) ·
  `duygu` (bağ ve hak edilmişlik) · `karakter` (yay, motivasyon, oyunculuk) · `ozgunluk` (tür vaadi + taze açı) ·
  `yapi` (3 parti, vuruş oranları, orta bölüm sarkması) · `uretilebilirlik` (Flow kısıtlarına uyum) ·
  `sureklilik_yuku` (mekân, kostüm varyantı, kalabalık; az = iyi) · `seri` (evren, seri kancası, tekrar kullanılabilir karakter).
  Her jüri ayrıca **çalınmaya değer** (diğer önerilerden alınacak parça) ve **mutlaka düzelt** listesi yazar.
- **Çıktı:** `03_juri_<rol>.md` + makinece okunur `03_juri_<rol>.json` (§5.4).
- **Geçme şartı:** 5 JSON'un hepsi şemaya uyuyor; her puanın gerekçesi ≥ 1 cümle.
- **Kim:** 5 × ajan `juri-uyesi` (aynı tanım, `rol` parametresiyle).

### H6 — Seçim (deterministik)
- **Girdi:** 5 jüri JSON'u.
- **İş (betik `hikaye_odasi.py juri-topla`):** her öneri ve her ölçüt için 5 jürinin **medyanı** (puanlar gürültülü — DR,
  ZN §7.2.10); öneri puanı = medyanların ortalaması.
  - **Veto:** `uretilebilirlik` medyanı < 5 ya da üretilebilirlik jürisinin KRİTİK maddesi çözümsüzse öneri elenir **(tahmin eşiği)**.
  - **Kazanan:** en yüksek puan. İlk iki öneri arasındaki fark ≤ 0,3 puansa **(tahmin)** → `BIRLESTIR` (EMBERFALL'da
    420/420 beraberlik birleştirildi — YR A3, A4).
  - Kazananın puanı < 8,0 ise **(S9, tahmin)**: jürinin "mutlaka düzelt" maddeleriyle kazanan yazar bir kez daha yazar,
    jüri yeniden puanlar (en çok 1 tur). Yine < 8,0 ise en iyi öneriyle devam edilir ve karar deftere "eşik altı başladı" diye yazılır.
- **Çıktı:** `04_SECIM.json` (`kazanan`, `birlestir_ile`, `calinacaklar[]`, `mutlaka_duzelt[]`, puan tablosu) +
  kullanıcıya **bilgi** amaçlı 1 sayfalık sade özet `04_KULLANICIYA_OZET.md` (onay istenmez; kesin karar 1).
- **Geçme şartı:** karar alanı dolu.
- **Kim:** betik; AC yalnız özeti kullanıcıya iletir.

### H7 — Yapı: 3 parti × 8 başlık
- **Girdi:** kazanan öneri (+ birleşecek öneri), `04_SECIM.json`, brifing, evren.
- **İş (ajan `senarist`; mümkünse kazanan mimarın **aynı örneği** devam ettirilir — "revizyonu metni yazan yapar", YR §1.4;
  oturum kaybolursa yeni örnek `yazar_defteri.md`'den devam eder):**
  - Film düzeyi: `duygu_haritasi` (ZN §1.3 eğrisi, süreye oranla), `vuruslar` (ZN §1.2 oranları), `MERAK_DEFTERI`,
    `KURULUMLAR`, `IRONILER`, `vaat_sozlesmesi` (§2.1 aşağıda), `bolum_adlari` (YouTube chapter, ≤ 8), `kontrol_onermeleri` (12–20 olgu).
  - **Her parti için 8 başlık** (UH §1, H/proje-b3; makine alanları §5.2):
    1. **Amaç / duygu** + partinin tek cümlelik savunması ("P2'de [kahraman] [hedef] için [engel]le karşılaşır ve [kayıp]la biter." — ZN §7.2.3)
    2. **Vuruş vuruş olay akışı** (sahne grupları S01…: sahne tipi, hedef süre, `sahne_degeri {bas, son}`, vuruş, yoğunluk, hedef duygu)
    3. **Kim nerede durur** (sahne giriş ve çıkışında her adlı karakterin yeri, pozu, kostüm varyantı, yarası/kiri)
    4. **Nesnelerin yolu** (her hikâye nesnesi: kimde, nerede; el değiştirdiği her an **ekranda bir olay** olarak)
    5. **Yalan/niyet seyirciye nasıl okunur** (kim kime ne yalan söylüyor; seyirci bunu hangi araçla görür: ironi planı,
       tepki planı, ekleme planı, replik — ZN §4.4)
    6. **Mekân tutarlılığı** (mekân listesi; kroki notu: kapı/ocak/pencere yönü, ışık kaynağı, saat, hava; mekân ≤ 10)
    7. **Parti sonu kancası** (hangi merak sorusuyla biter, yoğunluk ≥ 8; sonraki parti ilk 20 sn'de nereden açılır)
    8. **Plan sayısı tahmini ve riskli sahneler** (ZN §2.6 dağılımı; her riskli sahne için çözüm: karşılıklı çekim, el/makro, siluet)
- **Çıktı:** `05_YAPI.md` + `05_YAPI.json` (aynı içerik, makine alanları).
- **Geçme şartı (betik `hikaye_odasi.py yapi-denetim`):** 3 parti var; her partide 8 başlık dolu; parti oranları 0,30–0,35
  (RE `parti_sure_oran_aralik`); vuruş oranları ±0,04 (RE); parti sonu yoğunluk ≥ 8, doruk ≥ 9, en karanlık ≥ 6 (RE);
  her sahnede `sahne_degeri.bas ≠ son`; kurulum → kullanım sırası doğru; doruk çözümü P1/P2'de kurulmuş (ZN Z1 #31).
- **Kim:** ajan `senarist` → betik.

### H8 — Senaryo v1 (sahne sahne ekran metni)
- **Girdi:** `05_YAPI.json`, brifing, evren.
- **İş (ajan `senarist`, **parti parti** yazar; her partiden sonra `yazar_defteri.md`'ye kararlarını ekler):** her sahne için:
  - **EKRAN bloğu** (seyircinin göreceği tek şey): yer/zaman kartı (varsa), görülen olaylar (kısa, fiziksel, gözlenebilir
    cümleler — "hazırlanır" değil, "çantaya ekmeği koyar, ipi omzuna atar"), duyulan replikler (`R0001…` kimlikli; konuşan
    karakter, ton fiili, metin), ekran dışı ses.
  - **KÂĞIT bloğu** (seyirciye verilmez): amaç, risk, vuruş, merak aç/kapat, kurulum/kullanım, ironi rolü, giriş/çıkış
    durumu, bilgi durumu değişimi, sahne değeri.
  - **Replik kuralları** baştan klibe uygun yazılır: tek konuşan; replik bloğu ≤ 16 kelime (10 sn klip istenirse ≤ 20 —
    RE); ≥ 12 kelimeyse "ekran dışına taşınabilir" işaretlenir; aynı karakter art arda ≤ 3 blok; filtre kelimesi yok
    (ör. "Easy, little one" → "Easy now. I won't hurt you."; DR, BK §8 #11); "bildiğin gibi" repliği yok; bilgi taşıyan
    replikte çatışma var (ZN §4.5); konuşma sırasında nesneyle uğraşma yok, eylem ayrı satırda (ZN §2.3).
- **Çıktı:** `06_SENARYO_v1.md` + `06_SENARYO_v1.json` (§5.2 `sahneler[]`, `replikler[]`).
- **Geçme şartı:** H10.
- **Kim:** ajan `senarist`.

### H9 — Oyuncu ve diyalog denetimi (paralel)
- **Girdi:** her konuşan karakter için **yalnız o karakterin replikleri** + karakter kartı (bildiği, bilmediği, istediği,
  konuşma tarzı) — betik `hikaye_odasi.py oyuncu-paketi` hazırlar. Diyalog editörüne tüm replikler + dönem kuralları.
- **İş:**
  - **Oyuncu ajanları** (ana karakter başına 1; yan karakterler tek ajanda): "Bu karakter bunu böyle söyler mi? Bunu nereden
    biliyor? Neden şimdi söylüyor?" (FilmAgent Critique-Correct-Verify — AR1 A1; ZN §7.2.5).
  - **Diyalog editörü:** İngilizce doğallık, dönem uygunluğu (ortaçağ dünyasında "okay", "guys" yok), ad tutarlılığı,
    TTS/Veo telaffuz riski, filtre kelimeleri, kelime sınırı, TR altyazı karşılığı (`tr`).
- **Çıktı:** `07_oyuncu_<karakter>.md`, `07_diyalog.md` (her madde `R0123 | KRİTİK/ORTA/KÜÇÜK | sorun | öneri`).
- **Geçme şartı:** senarist bütün KRİTİK ve ORTA maddeleri uygular ya da gerekçesini yazar → `06_SENARYO_v1b`.
  Betik madde kimliklerinin hepsinin değişiklik tablosunda olduğunu denetler.
- **Kim:** ajanlar `oyuncu` (×N), `diyalog-editoru`; uygulayan `senarist`.

### H10 — Senaryo denetimi (makine; ajan değil)
- **Girdi:** son senaryo JSON'u, `RE`, `hikaye_esikleri.json` (§7), evren.
- **İş (betik `hikaye_odasi.py senaryo-denetim`):** sahne süresi tahmini (`hedef_sure_sn` + replik formülü ZN §2.3) ile
  birikimli zaman çizelgesi kurar ve hikâye düzeyinde ölçülebilen bütün Z1/Z2 maddelerini çalıştırır (§7): ad ≤ 120 sn,
  risk ≤ 180 sn, ilk merak ≤ 20 sn, merak boşluğu ≤ 90 sn, açık soru 1–5, kurulum → kullanım ≥ 20 sn, doruk çözümü kurulmuş,
  ironi/parti ≥ 1, sahne başına yeni ad ≤ 2, konuşan ≤ 8, eğri kuralları, vaat sözleşmesi, filtre ve NE YOK kelimeleri,
  **kanon denetimi** (ölü karakter konuşuyor mu, evren kuralı çiğneniyor mu, karakter bilmediği şeyi söylüyor mu),
  **sahne sınırı durum denetimi** (S_n çıkış ≠ S_n+1 giriş ve arada zaman atlaması/ekranda sebep yok → HATA).
- **Çıktı:** `_RAPOR/HIKAYE_Z_<surum>.json` (`{kapi, sonuc, hatalar:[{madde, sahne, olcu, esik, oneri}]}` — ZN §6.2 biçimi) + `YENIDEN_YAZ.json`.
- **Geçme şartı:** HATA = 0 (BAYRAK'lar seyirci turuna taşınabilir, raporda kalır).
- **Kim:** betik; düzeltme `senarist`.

### H11 — Kâğıt üstü habersiz seyirci döngüsü
- **Girdi:** betik `hikaye_odasi.py seyirci-paketi` çıktısı `_SEYIRCI_PAKETI/<tur>/P1.md, P2.md, P3.md, SORULAR.md`.
  Paket **yalnız EKRAN bloklarından** üretilir; amaç/risk/vuruş/merak defteri yoktur. **Ad maskeleme:** karakterin adı
  ekranda sözle söylenene kadar paket onu görünüşüyle anar ("KÜRK YAKALI KADIN"); ad ilk kez bir replikte geçtiği andan
  sonra adıyla anar. Böylece "bu kim?" sorunu metinde de gerçek seyircideki gibi yaşanır (B1 "84. çekim" dersi). İlişki
  sözcükleri ("brother", "captain") için de aynı kural uygulanır **(kapsamı kısmi; §9 risk)**.
- **İş:** 3 **yeni** seyirci örneği (her turda yeni; önceki metni bilen seyirci habersiz değildir — ZN §7.3), paralel,
  birbirini okumaz. Her biri partileri **sırayla** okur ve her partiden sonra o partinin raporunu yazar, sonra sonrakini
  açar (geriye dönüp düzeltmez — gerçek izleme taklidi). Rapor: 6 ölçüt (anlaşılırlık, akıcılık, merak, duygu, ritim,
  ilk30) parti başına ve genel; kopukluk listesi `{sahne, tur: KRITIK/ORTA/KUCUK, neden, oneri}`; sıkıldığım sahneler;
  aklımdaki açık sorular (her parti sonunda); `SORULAR.md`'deki açık uçlu sorulara cevap ("Ana karakterler kim, ilişkileri
  ne?", "Kahraman neyi kaybedebilir?", "Bu dünyanın kuralları neler?" — sorular bilgi sızdırmaz).
  Ardından ajan `anlama-olcer` seyirci cevaplarını `kontrol_onermeleri` ve `MERAK_DEFTERI` ile karşılaştırır (oran + eksik
  önermeler + "defterde var, seyircide yok" sorular).
- **Çıktı:** `_SEYIRCI_PAKETI/<tur>/rapor_1..3.md` (son satır OZET), `08_ANLAMA_<tur>.json`, betik `seyirci-topla` →
  `08_SEYIRCI_TUR<n>.json` (medyanlar, birleşik kopukluk listesi, 2+ seyircinin işaretlediği sıkılma sahneleri → kesme adayı).
- **Geçme şartı:** S1–S4 (GENEL medyan ≥ 8, ölçüt medyanı ≥ 7, KRİTİK 0 / ORTA ≤ 3 parti başına, eşleşme ≥ %80).
- **Döngü:** geçmezse aynı `senarist` v(n+1) yazar: her KRİTİK/ORTA madde → uygula ya da gerekçe; başa "vN değişiklikleri"
  tablosu (YR A5). Kesme adaylarından en az yarısı uygulanır (ZN §7.2.9 kesme turu mantığı); her kesmeden sonra H10 yeniden
  koşar (kesilen sahne bir kurulumu götürmüş olabilir — DR "miğfer" dersi).
  - **Salınım koruması:** GENEL medyan bir önceki turdan ≥ 1 puan düşerse betik en iyi sürümü `EN_IYI` olarak işaretler;
    yazar yeni tura *en iyi sürümden* başlar (B2 P1'de v7 6 → v8 5 düşüşü yaşandı — H/proje-b2).
  - **Tur 3'te iyileşme < 0,5 puansa** ajan `hikaye-doktoru` yapısal teşhis yazar (sorun sahne düzeyinde mi, yapıda mı?);
    yazar teşhisi uygular.
  - **4 tur sonunda eşik yoksa:** (a) KRİTİK = 0 ve GENEL ≥ 7,5 ise bir **yapısal tur** daha (doktor + yazar, toplam en çok 6);
    (b) hâlâ yoksa hikâye odası jürinin **ikinci önerisiyle** H7'den yeniden açılır (bir kez). (c) O da geçmezse hat DURUR
    ve kullanıcıya en düşük 3 ölçüt + öneriler raporlanır (ZN §7.3). Kullanıcıdan karar istenmez; durma bir engel bildirimidir.
- **Kim:** betik + 3 × ajan `habersiz-seyirci` + ajan `anlama-olcer` + `senarist` (+ `hikaye-doktoru`).

### H12 — İlk 2 dakika testi (soğuk açılış A/B)
- **Girdi:** senarist her filmde **iki soğuk açılış** (ilk 120 sn) yazar (ZN §7.2.2). Paket yalnız o 2 dakikayı içerir + kapak
  imgesi tarifi + başlık (gerçek YouTube'daki gibi seyirci başlığı ve kapağı görerek girer).
- **İş:** her versiyon için 3 yeni seyirci: "İlk 30 sn'den sonra kalır mıydın? 2. dakikanın sonunda devam eder miydin? Neden?"
  + "Başlıkta ve kapakta vaat edileni gördün mü?".
- **Çıktı:** `09_ILK2DK.json`.
- **Geçme şartı:** seçilen versiyonda 3/3 "evet" (S5). İkisi de geçmezse senarist üçüncü versiyonu yazar (en çok 2 tur).
- **Kim:** betik + 6 × `habersiz-seyirci` (mod `ilk2dk`) + `senarist`.

### H13 — Kilit ve devir
- **Girdi:** geçen senaryo sürümü, bütün raporlar.
- **İş (betik `hikaye_odasi.py devir`):** `HIKAYE.json` (yönetmene sözleşme, §5.2) ve `HIKAYE.md` üretir; kontrol önermeleri,
  merak defteri ve ilk 2 dk sürümü **animatik ve kurgu seyircileri için aynen saklanır** (ölçütler kıyaslanabilir kalsın);
  adlar ve kostüm varyantları evrene **ön kayıt** yapılır (görsel ekip kart üretirken aynı adları kullansın);
  `KARAR_DEFTERI.md`'ye seçim ve varsayımlar yazılır; `FILM_DURUM.json`'da `hikaye` aşaması kilitlenir.
- **Geçme şartı:** S1–S14 hepsi yeşil; `HIKAYE.json` şema doğrulamasından (jsonschema) geçti.
- **Kim:** betik; AC kullanıcıya 5 satırlık bilgi notu verir (onay değil).
- **Kilitten sonra hikâye değişikliği:** yalnız animatik/kurgu seyircisinin `tur: hikaye` bulgusuyla, etkilenen sahnelerle
  sınırlı, aynı senarist tarafından; ardından H10 ve etkilenen partide H11 (1 tur) yeniden koşar.

### H14 — Evren kaydı (film yayına hazır olunca)
- **Girdi:** son `HIKAYE.json`, kurgudan sonra gerçekleşen değişiklikler, kart/ses kararları (diğer ekiplerin dosyaları — yalnız okunur).
- **İş (ajan `evren-arsivcisi` + betik `evren.py kaydet`):** kanona bu filmin olaylarını, karakterlerin yay sonundaki
  durumunu (yaşıyor/yaralı/sürgün, kostüm varyantı, bildikleri), yeni evren kurallarını, açık seri sorularını, kullanılan
  başlık kancasını ve seri kancasını ekler. **Silme yok, sürümlü ekleme** (`EVREN_v{n}.json`, değişiklik günlüğü).
- **Geçme şartı:** `evren.py dogrula` (şema + kanon çelişkisi yok).
- **Kim:** ajan + betik.

### 2.1 Kanca ve başlık mantığının hikâyeye gömülmesi (H3, H7, H10, H12'ye dağılmış kurallar)
Başlık ve kapak, filmin **ilk sözleşmesidir**; YouTube seyircisi 0–2 dk arasında bu sözleşmenin tutulup tutulmadığına bakar
(ZN §1.4 "vaat görülmedi" bırakma anı). Bu yüzden başlık en son değil, **en başta** yazılır ve hikâye ona bağlanır:
1. **Başlık önce:** her mimar logline'dan hemen sonra 3 başlık yazar. Kalıp `[kanca cümlesi] | SERİ ADI | Full Movie 4K 2026`
   (BK 1.6). Kanca cümlesi şu dört öğeyi taşır: **özne** (She/He/The Soldier) + **güçlü geçmiş zaman fiili** (Raised, Chose,
   Stole, Hid) + **yasak/bedel nesnesi** (the Dragon, the Alien Child, the Crown) + **karşı güç** (They Ordered Her to Kill,
   Over the Army). Kaynak: kazanan örneklerin ortak yapısı (AN T14–16) — bu ayrıştırma benim çıkarımım **[Y]**.
2. **Vaat sözleşmesi (makine denetler):** başlığın her öğesi ve kapak imgesi bir sahneye bağlanır:
   `{oge: "Raised", sahne: "S12", ekranda: "Mara feeds the hatchling by hand"}`. Kurallar: kapak imgesi ve başlığın
   çekirdek ilişkisi ≤ 120 sn'de ekranda (RE `vaat_imgesi_max_sn`); "karşı güç"ün yasağı/emri ≤ 180 sn'de **sözle**
   (RE `risk_sozlu_max_sn`); başlık fiilinin anlattığı süreç (büyütmek, seçmek) en geç orta noktaya (%50) kadar ekranda
   gerçekleşir. Kapak, filmde olmayan bir kare olamaz (yanıltıcı kapak yasağı — BK 1.7.6).
3. **Bölüm (chapter) adları** hikâye odasında yazılır, çünkü onlar merak sorularıdır: ≤ 8 bölüm, parti/vuruş sınırlarına
   denk, "The Egg That Should Not Exist" gibi soru taşıyan ad (ZN §1.4). YouTube'un bölüm kuralları (ilk 00:00, ≥ 3 bölüm,
   her biri ≥ 10 sn) yayın aşamasında doğrulanır **(bu oturumda doğrulanmadı)**.
4. **Short adayları:** senarist her partide en az 1 "kendi başına anlaşılan, ilk 2 sn'de kanca, soruyla biten" 30–60 sn'lik
   anı işaretler (BK 1.8.4, 3.10). Doruğu ve en büyük sırrı **açmayan** anlar seçilir (Short filmi yakmamalı).
5. **Seri kancası** jenerikten önce ≤ 20 sn (RE `seri_kancasi_max_sn`); sonraki filmin başlığı için tohum (`sonraki_kanca`)
   evrene yazılır. Kazanan kanallarda hitler seride yoğunlaşıyor (BK 2.4).
6. **"Full Movie" bütünlüğü:** film kendi içinde kapanan bir ana soruyla biter; yalnız ≤ 2 seri sorusu açık kalır
   (RE `seri_sorusu_max`). EMBERFALL 12–15 dk'lık "Episode" olarak yayınlandı ve ≈ 671 izlenmede kaldı (OB); kazananların
   süresi 21–70 dk ve "Full Movie" (BK 1.5). Neden-sonuç kanıtı yok **[H]**, ama hedef format buna göre seçilir.
7. **Manhwa kancası katmanı [H]:** birincil kanca ailesi insan+yaratık bağı ise ikincil olarak ihanet / küçümsenen kahraman
   eklenmesi jüride `kanca` ölçütünde ayrıca değerlendirilir (BK 2.2 hipotezi); tutup tutmadığı ders defterine yazılır.

## 3. Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) — yalnız kendi alanım

**Ortak kurallar (hepsi):**
- Model: `opus` (= `claude-opus-5-5`), `effort: high`. Gerekçe: kullanıcı talimatı "önemli işlerde ajanlar Opus + yüksek
  efor" (H/ajan-opus-yuksek, BK 7.2) ve kesin karar 6 (tasarruf için kaliteden ödün yok). YR'de YouTube stratejisti ve
  üretilebilirlik jürisi Sonnet'ti; jüri bir **yargı** işi olduğu için Opus'a çıkarıyorum. Opus 5.5'te effort varsayılanı
  `medium` olduğundan **açıkça `high` yazılmalı** (claude-api belgesi).
- Araçlar en az yetkiyle; yaratıcı ajanlarda `Bash` yok (betikleri AC çalıştırır). Hiçbirinde `WebFetch/WebSearch` yok
  (kaynak veri depoda; habersizliği ve tekrarlanabilirliği bozmasın).
- `memory: project` **kullanılmaz**: öğrenme kontrollü biçimde DERS_DEFTERI'nden gelir (özellik e); ajanın kendi gizli
  hafızası seyircinin habersizliğini ve tekrarlanabilirliği bozar.
- Gövde sırası (AR3 B5, öneri 10): rol → "Çağrıldığında" adımları → kontrol listesi → makinece okunur çıktı (JSON ya da
  sabit başlıklı rapor + son satır `OZET | …`). Dönüş mesajı: yalnız dosya yolu + 3–5 satır özet.
- Her ajan dosya yolunu **devretme mesajında** alır; alt ajan sohbet geçmişini görmez (AR3 B5).

| # | Ad (dosya) | Durum | Araçlar | Görev | Okuyacağı dosyalar | Çıktısı |
|---|---|---|---|---|---|---|
| 1 | `konu-analisti` | **yeni** | Read, Write, Glob, Grep | Konuyu konu kartına çevirir; seri tespiti, kanca ailesi, vaat imgesi, risk taraması, varsayım defteri; "sen seç" modunda 3 aday + seçim | `00_KONU.txt`, `KANAL_KARARLARI.json`/`KARARLAR.md`, `BILGI_KURALLARI.md` §1–2, `EVREN/*/EVREN.json` (yalnız adlar ve özetler), `DERS_DEFTERI.json` (`hikaye`) | `01_KONU_KARTI.json`, `01_VARSAYIMLAR.md` |
| 2 | `hikaye-mimari` | **güncellenir** (mevcut taslak 3 parti × 8 başlığı zaten istiyor; öneri kapsamına daraltılır) | Read, Write, Edit, Glob | Verilen **eksende** tam öneri (H3'teki 10 başlık); bonus modunda "kaçınılacak logline'lar" alır | `00_BRIFING.md`, `DERS_DEFTERI.json` (`hikaye`), evren (devam ise). Diğer önerileri **okumaz** | `02_oneri_<eksen>.md` |
| 3 | `juri-uyesi` | **yeni** (tek tanım, `rol` parametresi: seyirci / strateji / tur_uzmani / duygu / uretilebilirlik) | Read, Write | Anonim 4 öneriyi 10 ölçütle puanlar, gerekçe, çalınmaya değer, mutlaka düzelt | `00_BRIFING.md`, `_JURI_PAKETI/oneri_1..4.md`, `JURI_TABLOSU.md`; `uretilebilirlik` rolü ayrıca `03_DERSLER.md` ve `uretilebilirlik-denetcisi.md` kontrol listesini okur | `03_juri_<rol>.md` + `.json` |
| 4 | `senarist` | **yeni** (kazanan mimarın devamı) | Read, Write, Edit, Glob, Grep | Birleştirme, `05_YAPI`, `06_SENARYO` (parti parti), bütün revizyonlar; `yazar_defteri.md`'yi tutar | kazanan öneri (+ birleşecek), `04_SECIM.json`, brifing, `ZANAAT.md` §1, §4, §2.3, `ritim_esikleri.json`, evren, gelen raporlar | `05_YAPI.md/.json`, `06_SENARYO_vN.md/.json`, `vN_DEGISIKLIKLER.md`, `yazar_defteri.md` |
| 5 | `oyuncu` | **yeni** (karakter başına bir örnek) | Read, Write | Yalnız kendi karakterinin repliklerini, kendi kartına göre okur: ses, motivasyon, bildiği/bilmediği, "bildiğin gibi" hatası | `_OYUNCU_PAKETI/<karakter>.md` (betik üretir: kart + o karakterin replikleri + replikten hemen önceki ekran olayı) | `07_oyuncu_<karakter>.md` |
| 6 | `diyalog-editoru` | **yeni** | Read, Write | İngilizce doğallık, dönem dili, ad tutarlılığı, telaffuz riski (TTS/Veo), filtre ve kelime sınırı, TR altyazı karşılığı | senaryo JSON'unun `replikler[]` kısmı, evren `sozluk`, `03_DERSLER.md` filtre bölümü | `07_diyalog.md` (+ `tr` önerileri JSON) |
| 7 | `habersiz-seyirci` | **güncellenir** (3 ölçüt → 6 ölçüt, parti sıralı okuma, açık sorular, ad maskeli paket; `Glob` kaldırılır) | Read, Write (+ **PreToolUse kancası**, aşağıda) | Kâğıt / ilk 2 dk / animatik / kurgu modlarında aynı ölçütlerle habersiz izleme | yalnız `_SEYIRCI_PAKETI/<tur>/` altındaki dosyalar | `rapor_<n>.md` (son satır OZET) |
| 8 | `anlama-olcer` | **yeni** | Read, Write | Seyirci cevaplarını kontrol önermeleri ve merak defteriyle karşılaştırır; puan vermez, yalnız eşleştirir | `08_KONTROL.json` (önermeler + merak defteri), seyirci raporları | `08_ANLAMA_<tur>.json` |
| 9 | `hikaye-doktoru` | **yeni** (yalnız tur 3'te iyileşme < 0,5 ise) | Read, Write | Yapısal teşhis: sorun sahnede mi, partide mi, karakter yayında mı; en çok 5 somut yapı değişikliği önerir; **kendisi yazmaz** | son senaryo, bütün seyirci ve anlama raporları, `ZANAAT.md` §7.1 teşhis tablosu | `08_DOKTOR.md` |
| 10 | `evren-arsivcisi` | **yeni** | Read, Write, Edit | Film bitince kanon, karakter durumu, kurallar, NE YOK, seri soruları, başlık geçmişi güncellemesi | `HIKAYE.json`, son kurgu planı (salt okunur), `EVREN.json` | `EVREN_v{n+1}.json` taslağı + `EVREN_DEGISIKLIK.md` |

**Habersiz seyircinin habersizliğini araçla zorlamak (yeni ve önemli):** bugünkü taslakta seyirci `Read` ve `Glob` ile
film klasöründeki her dosyayı (amaç alanlı SENARYO, merak defteri) açabilir; habersizlik yalnız talimata güveniyor.
Öneri: ajan frontmatter'ına `hooks` ile **PreToolUse** kancası (`YZ_FILM/ARACLAR/seyirci_bekci.py`): `Read`/`Write` hedef
yolu `_SEYIRCI_PAKETI/<aktif tur>/` dışındaysa çağrıyı reddeder. Aktif tur yolu ortam değişkeni ya da paket klasöründeki
`AKTIF` işaret dosyasından okunur. (Ajan frontmatter'ında `hooks` alanı AR3 B5'te listeleniyor; Windows'ta kancanın
`python` yolu `.bat` kurulumundaki tam yol olmalı — kurulumda bir kez sınanmalı.)

**Örnek frontmatter (senarist):**
```yaml
---
name: senarist
description: Use when the story room has a winning proposal and needs the 3-part structure, the scene-by-scene screenplay
  (screen text + English lines), or a revision after audience/jury/actor reports. Hikâye odası kazanan öneriyi yapıya ve
  senaryoya çevirir, bütün revizyonları yazar. Use proactively after juri-topla selects a winner.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
---
```
**Örnek frontmatter (habersiz-seyirci):**
```yaml
---
name: habersiz-seyirci
description: Use when a story, animatic or cut needs a first-time viewer's blind judgement. Reads ONLY the audience packet
  path given in the task. Each call must be a fresh instance.
tools: Read, Write
model: opus
effort: high
hooks:
  PreToolUse:
    - matcher: "Read|Write"
      hooks:
        - type: command
          command: "python YZ_FILM/ARACLAR/seyirci_bekci.py"
---
```

**Seyirci raporunun son satırları (puan_oku ile uyumlu; ZN §7.3 biçimi + kopukluk sayıları):**
```
OZET_P1 | anlasilirlik: 8 | akicilik: 7 | merak: 8 | duygu: 7 | ritim: 7 | ilk30: 9 | GENEL: 8 | KRITIK: 0 | ORTA: 1
OZET_P2 | ...
OZET_P3 | ...
OZET | anlasilirlik: 8 | akicilik: 8 | merak: 8 | duygu: 7 | ritim: 7 | ilk30: 9 | GENEL: 8 | KRITIK: 0 | ORTA: 2
```

**Jüri tablosu dosyası:** `.claude/skills/film-yap/reference/JURI_TABLOSU.md` (yeni): 10 ölçütün tanımı, her ölçüt için
1/5/8/10 puanın neye benzediği (çapa örnekleri; "8 = gerçekten iyi, cömert olma"), rol başına bakış açısı, JSON çıktı şeması.

## 4. Beceri (skill) tarif adımları — kendi alanım

Yer: `.claude/skills/film-yap/SKILL.md` içinde kısa bir "Hikâye odası" maddesi + ayrıntı tek seviye bağlantıyla
`.claude/skills/film-yap/reference/hikaye_odasi.md` (AR3 B4: SKILL.md < 500 satır, ayrıntı referansta). Hikâye odası
**kredi harcamadığı** için `disable-model-invocation` gerekmez; kullanıcı "film yap / yeni film / start a film" dediğinde
tetiklenir. SKILL.md'nin en üstünde şu üç satır durur (sıkıştırmadan sonra ilk 5.000 token yeniden eklenir — AR3 B4):
1. Kullanıcıya **yalnız konu** sorulur. 2. Hiçbir ajan çıktısını AC puanlamaz; kararları betikler verir. 3. Habersiz
seyirciye yalnız `_SEYIRCI_PAKETI` verilir.

**Tarif (AC'nin kopyalayıp işaretleyeceği kontrol listesi):**
```
HİKÂYE ODASI — <film>
- [ ] 0. Durumu oku: !`python YZ_FILM/ARACLAR/film.py <film> --durum`  (hafızaya değil dosyaya güven)
- [ ] 1. Konu yoksa TEK soruyu sor (H0 metni aynen). Cevabı _HIKAYE_ODASI/00_KONU.txt'ye yaz. Başka soru YOK.
- [ ] 2. Agent(konu-analisti) → 01_KONU_KARTI.json · sonra: python hikaye_odasi.py <film> konu-denetim
- [ ] 3. python hikaye_odasi.py <film> brifing  → 00_BRIFING.md iskeleti; bölüm 7 (konu yorumu) ve 8 (eksenler) AC yazar
- [ ] 4. TEK mesajda 3 paralel Agent(hikaye-mimari): eksen D, S, E (her birine brifing yolu + çıktı yolu + "diğerlerini okuma")
- [ ] 5. python hikaye_odasi.py <film> logline  → bonus için 3 logline; Agent(hikaye-mimari, eksen X, kaçınılacak logline'lar)
- [ ] 6. python hikaye_odasi.py <film> oneri-denetim  → HATA'lı öneri aynı mimara (≤2), BENZER → yeniden eksen (≤1)
- [ ] 7. python hikaye_odasi.py <film> juri-paketi (anonimleştirme) → TEK mesajda 5 paralel Agent(juri-uyesi, rol=…)
- [ ] 8. python hikaye_odasi.py <film> juri-topla  → 04_SECIM.json; 04_KULLANICIYA_OZET.md'yi kullanıcıya İLET (soru sorma)
- [ ] 9. Agent(senarist) [kazanan mimar örneğine SendMessage; yoksa yeni örnek + yazar_defteri] → 05_YAPI
        python hikaye_odasi.py <film> yapi-denetim  → HATA varsa aynı senariste geri
- [ ] 10. Agent(senarist) → 06_SENARYO_v1 (parti parti; her partiden sonra yazar_defteri)
- [ ] 11. python hikaye_odasi.py <film> oyuncu-paketi → TEK mesajda Agent(oyuncu)×N + Agent(diyalog-editoru)
         → senarist uygular (v1b) → betik madde kapanışını denetler
- [ ] 12. python hikaye_odasi.py <film> senaryo-denetim  → HATA=0 olana dek senarist
- [ ] 13. TUR n: python hikaye_odasi.py <film> seyirci-paketi --tur n
         → TEK mesajda 3 paralel Agent(habersiz-seyirci, YENİ örnek, paket yolu)
         → Agent(anlama-olcer) → python hikaye_odasi.py <film> seyirci-topla --tur n
         → GEÇTİ ise 14'e; değilse senarist v(n+1) (EN_IYI sürümden) → 12'ye dön
         → tur 3'te iyileşme <0,5: Agent(hikaye-doktoru) → senarist ; tur 4 sonu: H11 durma kuralı
- [ ] 14. python hikaye_odasi.py <film> ilk2dk-paketi → 2 sürüm × 3 Agent(habersiz-seyirci, mod=ilk2dk) → ilk2dk-topla
- [ ] 15. python hikaye_odasi.py <film> devir  → HIKAYE.json + evrene ön kayıt + KARAR_DEFTERI; kullanıcıya 5 satır bilgi
- [ ] 16. (film bitince) Agent(evren-arsivcisi) → python evren.py <seri> dogrula → kaydet
```

**Yapılmayacaklar (referans dosyasında "yasaklar" başlığıyla):**
- Kullanıcıya ton, süre, karakter adı, öneri seçimi sorulmaz (kesin karar 1). Kullanıcı kendiliğinden bir şey söylerse
  kesin istek olarak `00_KONU.txt`'ye eklenir ve ilgili aşama yeniden açılır (`film.py --sifirla brifing`).
- AC hiçbir öneriyi/senaryoyu kendisi puanlamaz, "bence bu daha iyi" diye jüri kararını değiştirmez (YR §1 tarafsızlık).
- Aynı seyirci örneği ikinci tura sokulmaz; seyirciye paket dışı dosya yolu verilmez; seyirciye "şuna dikkat et" ipucu
  verilmez (yönlendirme habersizliği bozar).
- Senaryo metnini AC düzeltmez; düzeltmeyi metni yazan `senarist` yapar (YR §1.4).
- Raporlar okunurken ham puan değil medyan ve eğilim konuşulur (DR "puanlar gürültülü").

**Devam etme (kullanım sınırı / sıkıştırma sonrası):** `SessionStart` (`compact|resume`) kancası `film.py --durum`
özetini ve `_HIKAYE_ODASI/00_DURUM.md`'yi `additionalContext` olarak geri getirir (AR3 B6). Her adım dosya ürettiği için
adım atlanmaz, tekrar edilmez: betikler çıktı dosyası varsa "zaten var" der.

**Beceri değerlendirme senaryoları (AR3 B4, öneri 12):** (1) "film yap" → yalnız konu sorusu gelmeli; (2) "ejderha
yavrusu saklayan kadın" → H1–H3 dosyaları; (3) "sen seç" → 3 konu adayı ve seçim; (4) ortada kalmış film klasörü →
`--durum`'dan devam, tamamlanan aşamayı tekrarlamama; (5) "EMBERFALL'ın devamı" → seri devamı tonları (A/B/S/X).

## 5. Veri şeması / plan alanları (JSON örneğiyle)

Hepsi JSON (UTF-8), hepsi `jsonschema` ile doğrulanır (şemalar `YZ_FILM/ARACLAR/semalar/*.schema.json`). Örnek film:
konu "ejderha yavrusunu saklayan avcı kadın" (uydurma örnek; gerçek proje değil).

### 5.1 `01_KONU_KARTI.json`
```json
{
 "konu_ham": "ejderha yavrusunu saklayan avcı kadın",
 "kesin_istekler": [],
 "seri": {"durum": "yeni", "evren": null, "gerekce": "konu kayıtlı evren/karakter anmıyor"},
 "tur": "fantastik", "alt_tur": "insan+yaratik_bagi",
 "kanca_ailesi": {"birincil": "insan_yaratik_bagi", "ikincil": "ihanet"},
 "vaat_imgesi": "A huntress in a snowstorm shields a glowing dragon hatchling under her cloak while soldiers' torches approach",
 "seyirci_vaadi": ["bağ ve büyütme", "saklama gerilimi", "yetişkin ejderhanın heybetli dönüşü"],
 "riskler": [
  {"tur": "filtre", "aciklama": "yavru için 'baby/little' sözcükleri", "seviye": "orta",
   "cozum": "sözlük: 'the hatchling', ad verildikten sonra adıyla"},
  {"tur": "uretim", "aciklama": "kalabalık asker sahneleri", "seviye": "orta",
   "cozum": "siluet, meşale ışığı, sırt; yüz yalnız ≤2 adlı karakter"}
 ],
 "varsayimlar": [
  {"karar": "süre 40 dk", "neden": "RE film_sure_hedef_sn, BK 1.5 tatlı nokta 30–45", "yanlissa_maliyet": "yapı oranla gerilir, düşük"}
 ],
 "film_sure_hedef_sn": 2400
}
```

### 5.2 `HIKAYE.json` — hikâye odasının tek çıktısı ve yönetmenle sözleşme
`06_SENARYO_vN.json` aynı şemadadır; `HIKAYE.json` kilitlenmiş sürümdür. Film düzeyi alanlar ZN §6.1 "film düzeyi"
listesiyle **aynı adları** kullanır (`duygu_haritasi`, `vuruslar`, `MERAK_DEFTERI`, `KURULUMLAR`, `IRONILER`); böylece
yönetmen ve makine aynı alanları plan düzeyinde doldurup denetler.
```json
{
 "surum": "v3", "kilit": true, "evren": "FROSTHOLLOW", "film_no": 1,
 "logline": "A disgraced huntress hides the last dragon hatchling from the king's burners, while her own brother leads the hunt.",
 "baslik": {"secilen": "She Hid the Dragon the King Ordered Burned | FROSTHOLLOW | Full Movie 4K 2026",
            "adaylar": ["...", "..."]},
 "vaat_sozlesmesi": [
  {"oge": "She", "sahne": "S01", "ekranda": "Sera is seen in the first 5 s, named by line R0004"},
  {"oge": "Hid the Dragon", "sahne": "S03", "ekranda": "Sera wraps the hatchling in her cloak as torches approach"},
  {"oge": "the King Ordered Burned", "sahne": "S02", "ekranda": "Herald reads the decree aloud (R0006)", "sozlu": true},
  {"oge": "kapak_imgesi", "sahne": "S03", "ekranda": "cloak + glow + torches"}
 ],
 "film_sure_hedef_sn": 2400,
 "duygu_haritasi": {"0": {"yogunluk": 8, "tur": "gerilim"}, "1": {"yogunluk": 6, "tur": "merak"}},
 "vuruslar": {"soguk_acilis": 0.0, "ilk_kanca": 0.3, "baslik_karti": 1.3, "tetikleyici": 5.0, "perde1_donus": 10.0,
              "parti1_kanca": 12.8, "orta_nokta": 20.0, "parti2_kanca": 26.2, "en_karanlik": 29.5, "doruk": 36.0, "seri_kancasi": 38.6},
 "kontrol_onermeleri": [
  {"id": "k01", "onerme": "Sera ejderha yavrusunu kraldan saklıyor", "kritik": true},
  {"id": "k02", "onerme": "Ejderha beslemek ya da saklamak ölüm cezası", "kritik": true},
  {"id": "k03", "onerme": "Avı yöneten kaptan Brann, Sera'nın ağabeyi", "kritik": true}
 ],
 "MERAK_DEFTERI": [
  {"id": "m01", "soru": "Karın altındaki ışık ne?", "ac": "S01", "kapat": "S02", "tur": "kisa"},
  {"id": "m03", "soru": "Brann kız kardeşini ele verecek mi?", "ac": "S09", "kapat": "S31", "tur": "buyuk"},
  {"id": "m99", "soru": "Kuzeyde başka yumurta var mı?", "ac": "S49", "kapat": null, "tur": "seri"}
 ],
 "KURULUMLAR": [
  {"id": "kur_duduk", "ne": "Kemik düdük ejderhayı sakinleştirir", "kurulum": "S05", "nasil": "ekleme + R0031",
   "hatirlatma": ["S22"], "kullanim": "S44", "odeme": "Doruğu çözen hamle"}
 ],
 "IRONILER": [
  {"id": "i01", "seyirci_bilir": "S08", "karakter_ogrenir": "S11", "ne": "Brann'ın adamı kulübeyi gözlüyor"}
 ],
 "bolum_adlari": [{"bas_sahne": "S01", "ad": "The Light Under the Snow"}, {"bas_sahne": "S06", "ad": "A Fire That Must Not Burn"}],
 "short_adaylari": [{"sahneler": ["S03"], "kanca_2sn": "torches + glowing cloak", "biter": "m02 açık"}],
 "karakterler": {
  "sera": {"ad": "Sera", "rol": "kahraman", "yas_bandi": "yetiskin", "istek": "kardeşinin affı", "korku": "yine terk edilmek",
           "yara": "sürgün edilen avcı", "sir": "yavruyu saklıyor",
           "yay": {"bas": "kimseye güvenmez", "son": "bağ için her şeyi göze alır"},
           "konusma_tarzi": "kısa, kuru cümleler; asla 'please' demez", "bildikleri_bas": ["ferman", "dağ yolları"],
           "gorsel_ayirt_edici": "kızıl örgü, koyu yeşil yünlü pelerin, sol elde deri bilek bandı",
           "ses_tarifi_en": "woman, early 30s, low husky voice, northern English accent, clipped",
           "kostum_varyantlari": ["sera_k1_pelerin", "sera_k2_yarali_kol"]},
  "hatchling": {"ad": "Kit", "rol": "yaratik", "konusmaz": true, "olcek": {"S03": "kedi boyu", "S40": "at boyu"}}
 },
 "partiler": [
  {"id": "P1", "sahneler": ["S01", "S17"], "sure_hedef_sn": 780,
   "tek_cumle": "P1'de Sera ölüm fermanına rağmen yavruyu saklamaya karar verir ve ağabeyinin avı yönettiğini öğrenerek biter.",
   "b1_amac_duygu": {"amac": "...", "duygu_seyri": "gerilim>sefkat>korku"},
   "b2_vurus_akisi": ["S01 soğuk açılış", "S02 ferman", "..."],
   "b3_kim_nerede": [{"sahne": "S03", "giris": {"sera": "mağara ağzı, sol, diz çökmüş"}, "cikis": {"sera": "patika, sırtında heybe"}}],
   "b4_nesne_yolu": [{"nesne": "kemik_duduk", "olaylar": [{"sahne": "S05", "kimden": "yasli_avci", "kime": "sera", "ekranda": "eline bırakır, ekleme planı"}]}],
   "b5_yalan_niyet": [{"kim": "brann", "yalan": "kardeşine yardım ettiğini söyler", "seyirci_okur": {"arac": "ironi", "sahne": "S08"}}],
   "b6_mekan": [{"mekan": "kulube", "kroki": "kapı batı, ocak kuzey, pencere doğu", "isik": "ocak (sıcak, kadraj solu)", "saat": "gece"}],
   "b7_parti_kancasi": {"sahne": "S17", "merak": "m03", "yogunluk": 9, "sonraki_acilis": "P2 ilk 20 sn'de Brann kapıda"},
   "b8_plan_tahmini": {"plan": 165, "riskli": [{"sahne": "S12", "neden": "yavru elden yemek alıyor (makro)", "cozum": "D ekleme + tepki"}]}}
 ],
 "sahneler": [
  {"id": "S03", "parti": "P1", "mekan": "magara_agzi", "zaman": {"gun": 1, "saat": "alacakaranlik", "atlama": "yok"},
   "sahne_tipi": "gerilim", "hedef_sure_sn": 95, "vurus": "ilk_kanca", "hedef_duygu": "korku>sefkat", "yogunluk": 7,
   "sahne_degeri": {"bas": "yalnız ve güvende", "son": "sırrı olan ve tehlikede"},
   "risk": "Sera yakalanırsa yavruyla birlikte yakılır",
   "merak_ac": ["m02"], "merak_kapat": ["m01"], "kurulum": [], "kullanim_bilgi": [], "ironi": null,
   "giris_durumu": {"karakterler": {"sera": {"yer": "mağara ağzı", "kostum": "sera_k1_pelerin", "yara": null}},
                    "nesneler": {"yay": "sera_sirt", "fener": "sera_sag_el_yanik"}},
   "cikis_durumu": {"karakterler": {"sera": {"yer": "patika", "kostum": "sera_k1_pelerin", "yara": null},
                                    "hatchling": {"yer": "sera_pelerin_ici"}},
                    "nesneler": {"yay": "sera_sirt", "fener": "sondu_yerde"}},
   "bilgi_degisimi": [{"kim": "sera", "ogrenir": "yavru_yasiyor"}],
   "seyirci_ogrenir": "Ejderha yavrusu yaşıyor ve Sera onu saklamaya karar veriyor.",
   "ekran": {
    "kart": null,
    "gorulen": ["Torchlight flickers far below on the slope.", "Sera kneels at the cave mouth; a faint orange glow pulses under the snow.",
                "She brushes the snow aside with her gloved left hand; the hatchling's eyes open."],
    "duyulan": ["R0011", "R0012"], "ekran_disi": ["distant horn", "wind"]},
   "kagit": {"amac": "Bağın ilk anı + saklama kararı", "neden_simdi": "askerler yaklaşırken karar zorunlu"}}
 ],
 "replikler": [
  {"id": "R0011", "sahne": "S03", "karakter": "sera", "ton": "whispers", "metin": "Easy now. Nobody burns you tonight.",
   "kelime": 6, "ekran_disi_uygun": false, "ad_soyler": [], "tr": "Sakin ol. Bu gece kimse seni yakmayacak."}
 ],
 "seri_kancasi": {"sahne": "S49", "sure_sn": 18, "merak": "m99", "sonraki_tohum": "He Burned the Village That Hid Her"}
}
```

**`HIKAYE.json` → `SAHNELER.json` aktarımı (yönetmenin sözleşmesi; makine denetler):**

| HIKAYE alanı | SAHNELER plan alanı (ZN §6.1) | Kural |
|---|---|---|
| `sahneler[].id` | `zanaat.sahne_grubu` | Her plan bir sahne grubuna bağlı; her sahne grubunun ≥ 1 planı var |
| `sahneler[].vurus`, `hedef_duygu`, `yogunluk`, `risk` | aynı adlar | Sahneden planlara miras; yönetmen plan bazında ±2 yoğunlukla ince ayar yapabilir |
| `merak_ac/kapat`, `kurulum`, `kullanim_bilgi`, `ironi` | aynı adlar | Sahnedeki her kimlik **tam olarak bir** planda taşınır (makine: kayıp ya da çift yok) |
| `replikler[].id` | `replik.id` (+ `karakter`, `metin`, `cumleler[].en/tr`) | Yönetmen repliği **bölebilir** (ekran dışı L kesme) ama metni değiştiremez; değişiklik isteği senariste gider |
| `giris_durumu` / `cikis_durumu` | sahnenin ilk planının `baslangic_durumu`, son planının `bitis_durumu` | Olgular eşit (yer, kostüm, yara, nesne kimde) — özellik (b) zincirinin hikâye uçları |
| `seyirci_ogrenir` | sahnedeki planların `ekranda_bilgi` birleşimi | Plan düzeyi kâğıt seyircisinin karşılaştırma kaynağı |
| `karakterler.*.ses_tarifi_en`, `konusma_tarzi`, `replikler[].ton` | ses/istem ekiplerine | Veo istemi ya da TTS etiketi bu sabit metinden türetilir (§8.3) |

### 5.3 `YZ_FILM/EVREN/<SERI>/EVREN.json` — seri evreni kütüphanesinin hikâye tarafı
Görsel kartlar (`kartlar`), ses kimlikleri (`sesler`) ve mekân görselleri diğer ekiplerin alanıdır; aynı dosyada ayrı
anahtarlar altında durur. Hikâye tarafı:
```json
{
 "seri": "FROSTHOLLOW", "surum": 3, "son_film": 1,
 "donem": {"cag": "geç ortaçağ benzeri, barut yok", "teknoloji": "demir, yay, kızak, yağ kandili",
           "kumas": ["yün", "deri", "kürk", "keten"], "renk_paleti": ["buz mavisi", "kömür", "ateş turuncusu"]},
 "kurallar": [
  {"id": "ev01", "kural": "Ateş Taç'ın malıdır; izinsiz ateş yakmak suç", "ekranda_kuruldu": {"film": 1, "sahne": "S02"},
   "kanit_replik": "R0006"}
 ],
 "ne_yok": [
  {"oge": "fermuar", "neden": "dönem", "kelimeler_en": ["zipper", "zip"]},
  {"oge": "modern mont", "neden": "pilot uyumsuzluğu (YR §5)", "kelimeler_en": ["jacket", "parka", "hoodie", "puffer"]},
  {"oge": "barut silahı", "neden": "dönem", "kelimeler_en": ["gun", "rifle", "pistol", "musket"]}
 ],
 "karakterler": {
  "sera": {"durum": "yaşıyor", "son_kostum": "sera_k2_yarali_kol", "yay_gecmisi": [{"film": 1, "bas": "...", "son": "..."}],
           "bildikleri": ["kit_bir_ejderha", "brann_avi_yonetiyor"], "iliskiler": {"brann": "ağabey, düşman", "kit": "bağ"},
           "konusma_tarzi": "kısa, kuru", "ses_tarifi_en": "woman, early 30s, low husky voice, northern English accent, clipped",
           "ilk_film": 1}
 },
 "kanon": [{"film": 1, "olay": "Kit yumurtadan çıktı, Sera onu sakladı", "sahne": "S03"}],
 "seri_sorulari": [{"id": "m99", "soru": "Kuzeyde başka yumurta var mı?", "acildigi_film": 1, "durum": "acik"}],
 "baslik_gecmisi": [{"film": 1, "baslik": "She Hid the Dragon the King Ordered Burned", "kanca_ailesi": "insan_yaratik_bagi"}],
 "sozluk": {
  "adlar": {"Sera": {"telaffuz": "SEH-rah", "hece": 2}, "Brann": {"telaffuz": "BRAN", "hece": 1}},
  "guvenli_karsilik": {"baby dragon": "the hatchling", "little one": "easy now", "child": "(sahne yeniden tasarlanır)"}
 },
 "degisiklik_gunlugu": [{"surum": 3, "tarih": "2026-11-02", "film": 1, "ozet": "film 1 kanonu eklendi"}]
}
```
Kurallar: (1) kanon yalnız **eklenir**; eski sürüm `EVREN_v{n}.json` olarak kalır. (2) `ne_yok[].kelimeler_en` her filmde
`senaryo-denetim` ve `istem_denetim` tarafından taranır. (3) `karakterler.*.bildikleri` bir sonraki filmin başlangıç
bilgi durumudur (oyuncu denetimi buna göre yapılır). (4) `sozluk.guvenli_karsilik` filtre kelimelerinin evren içi
karşılığıdır; diyalog editörü buradan seçer.

### 5.4 Jüri çıktısı `03_juri_<rol>.json`
```json
{"rol": "strateji", "oneriler": {
  "1": {"puan": {"kanca": 8, "netlik": 7, "merak": 8, "duygu": 7, "karakter": 7, "ozgunluk": 6, "yapi": 7,
                 "uretilebilirlik": 8, "sureklilik_yuku": 7, "seri": 9},
        "gerekce": {"kanca": "insan+yaratık+emir üçlüsü başlıkta; kapak imgesi filmde S03'te var", "...": "..."},
        "calinmaya_deger": ["Öneri 3'ün kemik düdük kurulumu"], "mutlaka_duzelt": ["Ağabey ilişkisi 3. dakikadan önce sözle verilmeli"],
        "veto": null}},
 "siralama": ["1", "3", "2", "4"]}
```
Son satır (md dosyasında, YR A3 biçimiyle uyumlu): `OZET | 1: 7.4 | 2: 6.8 | 3: 7.1 | 4: 6.5 | SIRALAMA: 1>3>2>4`.

### 5.5 Seyirci turu toplamı `08_SEYIRCI_TUR<n>.json` (betik üretir)
```json
{"tur": 2, "senaryo_surum": "v2", "seyirci": 3,
 "medyan": {"anlasilirlik": 8, "akicilik": 8, "merak": 8, "duygu": 7, "ritim": 7, "ilk30": 9, "GENEL": 8},
 "parti_medyan": {"P1": {"GENEL": 8}, "P2": {"GENEL": 7}, "P3": {"GENEL": 8}},
 "kopukluk": [{"sahne": "S22", "tur": "ORTA", "kac_seyirci": 2, "neden": "düdüğün nereden geldiği hatırlanmıyor", "oneri": "S22'ye hatırlatma eklemesi"}],
 "sikilma": [{"sahne": "S14", "kac_seyirci": 2, "kesme_adayi": true}],
 "anlama": {"eslesme": 0.85, "eksik_onermeler": ["k07"], "ekranda_acilmamis_sorular": ["m05"]},
 "gecti": false, "neden": ["P2 GENEL 7 < 8"], "en_iyi_surum": "v2"}
```

### 5.6 `_HIKAYE_ODASI/` klasör düzeni
```
00_KONU.txt  00_BRIFING.md  00_DURUM.md  01_KONU_KARTI.json  01_VARSAYIMLAR.md
02_oneri_D|S|E|X.md  03_juri_<rol>.md/.json  04_SECIM.json  04_KULLANICIYA_OZET.md
05_YAPI.md/.json  06_SENARYO_vN.md/.json  vN_DEGISIKLIKLER.md  07_oyuncu_<k>.md  07_diyalog.md
08_KONTROL.json  08_SEYIRCI_TUR<n>.json  08_ANLAMA_<n>.json  08_DOKTOR.md  09_ILK2DK.json
yazar_defteri.md  KARAR_DEFTERI.md  HIKAYE.json  HIKAYE.md
_SEYIRCI_PAKETI/<tur>/{P1.md,P2.md,P3.md,SORULAR.md,AKTIF,rapor_1..3.md}   _JURI_PAKETI/  _OYUNCU_PAKETI/
```

## 6. Yazılması/değişmesi gereken kod (araç adı, ne yapar, girdi/çıktı, öncelik)

Stil: mevcut araçlar gibi tek dosyalı, Türkçe adlı, `"""Kullanım: …"""` belgeli, Python 3.10, yalnız standart kütüphane +
`jsonschema` (saf Python; `kurulum.py` listesine eklenir). Yollar `/` ile ve ayar dosyasından (CLAUDE.md kuralı). Ağ yok
(API modu hariç). **P0** = ilk filmden önce şart · **P1** = ilk film sırasında · **P2** = ikinci filmden önce.

| Öncelik | Araç | Ne yapar | Girdi → Çıktı |
|---|---|---|---|
| **P0** | `ARACLAR/hikaye_odasi.py` (yeni, alt komutlu) | Hikâye odasının bütün deterministik adımları: `konu-denetim`, `brifing`, `logline`, `oneri-denetim`, `juri-paketi` (anonimleştirme), `juri-topla`, `yapi-denetim`, `oyuncu-paketi`, `senaryo-denetim`, `seyirci-paketi`, `seyirci-topla`, `ilk2dk-paketi`, `ilk2dk-topla`, `devir`, `durum` | `_HIKAYE_ODASI/*` → raporlar, paketler, `HIKAYE.json`. Çıkış kodu: 0 geçti · 3 eşik altı · 2 girdi eksik · 1 hata (`puan_oku` ile aynı anlam) |
| **P0** | `ARACLAR/ekran_metni.py` (yeni, kütüphane) | Senaryodan **yalnız EKRAN bloklarını** çıkarır; **ad ve ilişki maskeleme** (ad ilk kez bir replikte geçene kadar görünüş tarifi); süre tahmini ve birikimli zaman kodu (ZN §2.3 formülü). Kâğıt, animatik ve kurgu paketleri **aynı** maskeleme kodunu kullanır | `HIKAYE/SENARYO.json` → `P1.md…P3.md` |
| **P0** | `ARACLAR/seyirci_bekci.py` (yeni, kanca) | PreToolUse kancası: habersiz seyircinin `Read/Write` hedefi aktif paket klasörü dışındaysa reddeder (stdin JSON → çıkış kodu 2 + açıklama) | araç çağrısı → izin/ret |
| **P0** | `ARACLAR/semalar/konu_karti.schema.json`, `hikaye.schema.json`, `juri.schema.json`, `seyirci_tur.schema.json`, `evren.schema.json` | §5 şemaları | — |
| **P0** | `ARACLAR/puan_oku.py` (değişir) | `GENEL` alanını tanır; birden çok raporda **medyan** (varsayılan) ya da ortalama (`--ortalama`, eski davranış); ölçüt başına en düşük medyan eşiği (`--olcut-min 7`); `KRITIK`/`ORTA` toplamı; `OZET_P1..3` satırlarını parti bazında okur. Eski `ORTALAMA` biçimli raporlar çalışmaya devam eder | raporlar → konsol + çıkış kodu |
| **P0** | `ARACLAR/film.py` (değişir) | `senaryo` aşamasından önce kâğıt aşamaları: `konu → konu_karti → brifing → oneriler → juri → yapi → senaryo_yaz → senaryo_denetim → seyirci → ilk2dk → hikaye_kilit`. Ajan gerektiren aşamada **`metin` sağlayıcısı** çağrılır (aşağıda). Mevcut `a_senaryo` artık `HIKAYE.json` kilidini de arar; `SAHNELER.json`'u yönetmen aşaması üretir. `--durum` hikâye aşamalarını da gösterir | `FILM_DURUM.json` |
| **P0** | `ARACLAR/saglayicilar/` (değişir): `TURLER`'e `"metin"`; `claude_code.py`, `claude_api.py`, `sahte.py`'ye `metin()` | `claude_code`: aşama için `_HIKAYE_ODASI/GOREV_<asama>.md` yazar ve `Durdur` (çıkış 2) ile ana oturuma bırakır — beceri görevi okuyup ajanları çalıştırır, `film.py`'yi yeniden çağırır. `claude_api` (P1): aynı görevi başsız çalıştırır. `sahte`: `testler/ornekler/hikaye/` sabit dosyalarını kopyalar (ağ yok, kredi yok) | görev → çıktı dosyası |
| **P0** | `ARACLAR/istem_denetim.py` (değişir) | (1) Filtre listesini tek kaynaktan (`hikaye_esikleri.json` ya da ortak modül) okur; (2) **replik metnini** de tarar (bugün yalnız `hareket_istem` taranıyor; replik Veo'ya istemle gidiyorsa aynı filtreye takılır); (3) evrenin `ne_yok[].kelimeler_en` listesini `gorsel_istem`/`hareket_istem`'de arar | `SAHNELER.json` + `EVREN.json` → rapor |
| **P0** | `.claude/skills/film-yap/hikaye_esikleri.json` (yeni) | §7'deki hikâyeye özgü eşikler (her anahtar `deger` + `aciklama` + `kaynak`); ritimle ortak olanlar `ritim_esikleri.json`'dan okunur, kopyalanmaz | — |
| **P0** | `testler/test_hikaye.py` + `testler/ornekler/hikaye/` (yeni) | `ORNEK_3_SAHNE` için küçük sahte `HIKAYE.json` (3 sahne, 3 replik) ve sahte seyirci/jüri raporları. Testler: (a) ad maskeleme — "Mara" adı R0003'e kadar "HUNTRESS IN FUR-LINED COAT" görünür; (b) Z1: ad > 120 sn → HATA; (c) `seyirci-topla` medyan: (9, 6, 8) → 8, tek seyircinin 9'u başarı sayılmaz; (d) `juri-topla` fark ≤ 0,3 → `BIRLESTIR`; (e) NE YOK: "zipper" → HATA; (f) bekçi kancası paket dışı `Read`'i reddeder; (g) `film.py --saglayici sahte` hikâye aşamalarından `SAHNELER.json`'a kadar uçtan uca (ağ/kredi yok — CLAUDE.md görev 7) | — |
| **P1** | `ARACLAR/evren.py` (yeni, kütüphane + CLI) | `yukle`, `dogrula` (şema + kanon çelişkisi), `kaydet` (sürümlü, silmesiz), `on_kayit` (adları ve kostüm varyantlarını kilitler), `ne_yok_kelimeleri`, `bilgi_durumu(karakter, film)`; kök yol `AYARLAR/FILM_AYAR.json → evren_kok` (yoksa `YZ_FILM/EVREN`) | `EVREN.json` ↔ `HIKAYE.json` |
| **P1** | `hikaye_odasi.py senaryo-denetim` içine **kanon ve durum denetimi** | ölü karakter replik veriyor; karakter `bildikleri` dışındaki bir şeyi söylüyor (replikte geçen anahtar kimlikler `bilgi_degisimi` ile izlenir); sahne sınırında durum zıplaması; kostüm varyantı ekranda sebepsiz değişiyor | → `HIKAYE_Z_*.json` |
| **P1** | `saglayicilar/claude_api.py` | Başsız mod (`--tam-otomatik` ve Claude Code yokken): Anthropic Python SDK, model `claude-opus-5-5`, `thinking: {type: "adaptive"}`, `output_config.effort: "high"`, uzun çıktıda **akış** (`messages.stream(...).get_final_message()`), JSON üreten aşamalarda `output_config.format` (yapılandırılmış çıktı) + şema doğrulaması, `stop_reason == "refusal"` denetimi ve sunucu tarafı yedek (`fallbacks`) — claude-api belgesi. Anahtar yalnız `ANTHROPIC_API_KEY` ya da `AYARLAR/anthropic_anahtar.txt` (asla yazdırılmaz). Her ajan tanımının gövdesi sistem istemi olarak kullanılır; paralel ajanlar ayrı isteklerdir (birbirinin çıktısını görmez) | görev → çıktı |
| **P1** | `DERS_DEFTERI` bağlantısı (`hikaye_odasi.py brifing` içinde) | `hikaye` etiketli, `durum: dogrulandi` dersleri brifinge; `durum: aday` dersleri yalnız "izlenecek" listesine koyar. Film sonunda `hikaye_odasi.py karne` hikâye kaynaklı bulguları (animatik/kurgu seyircisinin `tur: hikaye` maddeleri, kullanıcı notları) **ders adayı** olarak yazar | → `DERS_DEFTERI.json` (sahibi ders defteri ekibi; ben yalnız `hikaye` etiketli girdiyi üretirim) |
| **P1** | `ARACLAR/izleme_paketi.py` (değişir) | Ad maskelemesini `ekran_metni.py`'den alır; paket sonuna aynı `SORULAR.md`'yi ekler; ölçütler kâğıtla aynı 6 ölçüt olur (kıyaslanabilirlik) | — |
| **P2** | `hikaye_odasi.py baslik-denetim` | Başlık kalıbı, ≤ 100 karakter, kanca cümlesinin 4 öğesi (özne/fiil/nesne/karşı güç) için basit sözdizimsel kontrol, `baslik_gecmisi` ile tekrar kontrolü (aynı kanca ikinci kez kullanılmaz) | → BAYRAK |
| **P2** | `hikaye_odasi.py cesitlilik` | Öneriler arası dörtlü (kahraman tipi, çekirdek ilişki, doruk mekanizması, ana mekân) karşılaştırması; ileride yerel metin gömmesiyle | → `BENZER` bayrağı |

**`film.py` ile beceri arasındaki el sıkışma (önemli tasarım kararı):** `film.py` Claude Code alt ajanlarını kendisi
çağıramaz. Bu yüzden ajan gerektiren her aşamada `metin` sağlayıcı zinciri çalışır: ayarda `["claude_code"]` (varsayılan)
ise `film.py` görevi dosyaya yazıp **çıkış kodu 2** ile durur; beceri bu görev dosyasını okur, ajanları çalıştırır,
çıktı dosyaları oluşunca `film.py`'yi yeniden çağırır (imza değiştiği için aşama "tamam" olur). `["claude_api"]` ise
`film.py` aynı görevi başsız yürütür. Testte `["sahte"]`. Böylece tek orkestratör (`film.py`), tek durum dosyası
(`FILM_DURUM.json`) ve üç çalışma biçimi olur; CLAUDE.md görev 2 ("Claude API, model `claude-opus-5-5`") ile görev
hedefi ("Claude Code'da ajanlar") çelişmez.

**Kurulum notu:** `jsonschema` eklenir; `anthropic` paketi yalnız API modu seçilirse kurulur (`kurulum.py` sorar değil,
`FILM_AYAR.json`'a bakar).

## 7. Makinenin denetleyeceği eşikler (kaynağıyla)

**Zaman belirsizliği kuralı:** hikâye aşamasında plan yoktur; zaman kodu `hedef_sure_sn` + replik formülünden (ZN §2.3)
**tahmin** edilir. Bu yüzden zamana bağlı eşiklerde ±%15 **(tahmin)** belirsizlik bandı kullanılır: eşik bandın açıkça
dışındaysa HATA, bant içindeyse BAYRAK. Aynı maddeler yönetmen planından sonra plan süreleriyle kesin olarak yeniden
ölçülür (ZN Z1/Z2, makine). **H** = HATA (geçmez), **B** = BAYRAK.

### 7.1 Mevcut eşiklerden hikâye düzeyinde uygulananlar (yeni sayı yok; kaynak anahtar adı)

| Madde | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Film süresi (tahmini, kart+jenerik dahil) | 1800–2700 sn | H | RE `film_sure_aralik_sn`, ZN Z0 #1 |
| Parti oranı | 0,30–0,35 | B | RE `parti_sure_oran_aralik` |
| Vuruş konumu | ZN §1.2 oranı ±0,04 | B | RE `vurus_oranlari`, `vurus_oran_tolerans` |
| Sahne süresi | ≤ 180 sn | H | RE `sahne_max_sn` |
| Replik bloğu | ≤ 16 kelime (8 sn klip), ≤ 20 (10 sn) | H | RE `replik_max_kelime_8sn`, `replik_max_kelime` |
| Aynı karakter art arda replik bloğu | ≤ 3 | B | RE `monolog_ardisik_plan_max` |
| İlk merak sorusu / ilk eylem | ≤ 20 sn / S01'in ilk görülen satırı fiziksel eylem | H / B | RE `ilk_merak_max_sn`, `ilk_eylem_max_sn` |
| Başlık kartı | 45–120 sn, ≤ 6 sn | B | RE `baslik_karti_aralik_sn`, `baslik_karti_sure_max_sn` |
| Vaat imgesi (kapak + çekirdek ilişki) | ≤ 120 sn | H | RE `vaat_imgesi_max_sn` |
| Kahraman adı sözle | ≤ 120 sn ve ilk görünüşten ≤ 2 sahne | H | RE `kahraman_adi_max_sn`, `ad_ilk_gorunus_max_sahne` |
| Risk sözle / parti başında tazelenme | ≤ 180 sn / parti başından ≤ 60 sn | H | RE `risk_sozlu_max_sn`, `parti_basi_risk_tazeleme_max_sn` |
| Parti başında önceki kancaya dönüş | ≤ 20 sn | H | RE `parti_basi_kanca_donus_max_sn` |
| Merak olayları arası boşluk | ≤ 90 sn | B | RE `merak_olay_aralik_max_sn` |
| Açık soru sayısı | 1–5 | B | RE `acik_soru_aralik` |
| Soru ömrü | kısa ≤ 120 sn, orta ≤ 900 sn, büyük ≤ 1 parti | B | RE `soru_omru_max_sn` |
| Büyük soru kapanınca yeni soru | ≤ 30 sn | B | RE `cevap_yeni_soru_max_sn` |
| Parti sonu açık soru | ≥ 1 | H | ZN Z1 #28 |
| Film sonunda açık seri sorusu | ≤ 2 | B | RE `seri_sorusu_max` |
| Kurulum → kullanım | kurulum önce ve ≥ 20 sn; > 600 sn ise hatırlatma | H / B | RE `kurulum_kullanim_min_sn`, `hatirlatma_esigi_sn` |
| Doruk çözümü P1/P2'de kurulmuş | evet | H | ZN Z1 #31 |
| Kullanılmayan kurulum (seri hariç) | 0 | B | ZN Z1 #32 |
| Aynı bilginin verilmesi | ≤ 2 kez | B | RE `bilgi_tekrar_max` |
| Dramatik ironi | parti başına ≥ 1; süre 30–300 sn | B | RE `ironi_parti_min`, `ironi_sure_aralik_sn` |
| Sahne başına yeni ad / film başına konuşan | ≤ 2 / ≤ 8 | B | RE `sahne_yeni_ad_max`, `konusan_karakter_max` |
| Geri dönüş (flashback) | ≤ 20 sn, soluk ton işaretli | B | RE `geri_donus_max_sn`, DR |
| Duygu eğrisi: 3 dk pencerede tepe ≥ 6; düz çizgi ≤ 180 sn; aynı tür ≤ 2 dk art arda; tepe öncesi çukur | ZN §1.3 kuralları | B | RE `pencere_*`, `duz_cizgi_max_sn`, `ayni_duygu_ardisik_dk_max`, `tepe_oncesi_*` |
| Parti sonu / doruk / en karanlık yoğunluk | ≥ 8 / ≥ 9 / ≥ 6 | H | RE `parti_sonu_yogunluk_min`, `doruk_yogunluk_min`, `en_karanlik_yogunluk_min` |
| Seri kancası | jenerikten önce, ≤ 20 sn | B | RE `seri_kancasi_max_sn` |
| YouTube bölüm adı sayısı | ≤ 8 | B | RE `bolum_sayisi_max` |
| Filtre kelimeleri (replik + ekran metni) | 0 | H | DR, `istem_denetim.FILTRE_KELIMELERI`, `YAS_IFADESI` |
| Seyirci: GENEL medyan / ölçüt medyanı / KRİTİK / ORTA / eşleşme / ilk 2 dk | ≥ 8 / ≥ 7 / 0 / ≤ 3 parti / ≥ 0,80 / 3 evet | H | RE `seyirci_*`, `kopukluk_*`, `ozet_eslesme_min`, `ilk2dk_devam_evet_min` |
| Kâğıt seyirci turu | ≤ 4 | — (H11 kuralı) | RE `kagit_tur_max` |
| Sıkılma işareti → kesme adayı | ≥ 2 seyirci | B | RE `sikilma_ortak_isaret_min` |
| Kesme önerilerinden uygulanan | ≥ %50 | B | RE `kesme_turu_oneri` |

### 7.2 Yeni eşikler (`hikaye_esikleri.json`)

| Anahtar | Değer | Sonuç | Kaynak / gerekçe |
|---|---|---|---|
| `sahne_sayisi_40dk` | 45–55 (süreyle oranla) | B | ZN §2.4 "Film ≈ 45–55 sahne" |
| `replik_toplam_kelime_40dk` | 2.100–2.600 (oranla) | B | ZN §2.6 |
| `sahne_degeri_degismeli` | `bas ≠ son` her sahnede | H | ZN §7.2.4 |
| `parti_tek_cumle` | 3 partinin üçünde de dolu, kalıba uygun | H | ZN §7.2.3 |
| `ana_karakter_max` | 4 (yaratıklar hariç) | B | mevcut `hikaye-mimari` taslağı |
| `mekan_max` | 10 | B | **(tahmin)**; taslakta 6 vardı ama 40 dk / 45–55 sahne için dar; her mekân bir kart ve süreklilik yükü |
| `kostum_varyant_max_karakter` | 2 | B | **(tahmin)**; her varyant yeni referans kartı ve yüz/kıyafet denetimi demek (özellik c) |
| `uc_adli_karakter_sahne_parti_max` | 3 sahne/parti | B | **(tahmin)**; ≤ 2 referans kuralı (K3) yüzünden ≥ 3 adlı karakterli sahne pahalı |
| `ad_hece_max_ana` | 2 | B | **(tahmin)**; TTS/Veo telaffuz tutarlılığı (§8.3) |
| `ad_ayrisma` | ilk harf ve ilk ses farklı; iki ad arası düzenleme uzaklığı ≥ 3 | B | **(tahmin)**; seyircinin ve whisper'ın adları karıştırmaması |
| `kucuk_guzel_sahne_parti_min` | 1 | B | kullanıcı isteği (BK 2.10, H/kurgu-izleme); sayı **(tahmin)** |
| `logline_kelime_max` | 35 | B | **(tahmin)** |
| `baslik_karakter_max` | 100 | H | YouTube başlık sınırı (genel bilgi; bu oturumda doğrulanmadı) |
| `kanca_cumlesi_karakter_max` | 60 | B | **(tahmin)**; mobilde kesilme payı, seri adı ve "Full Movie" ekinin sığması |
| `vaat_surec_max_oran` | başlık fiilinin süreci ≤ 0,50 (orta nokta) | B | **(tahmin)**; ZN §1.2 "vaadin eğlencesi" 14–19. dk |
| `short_aday_parti_min` | 1 (30–60 sn, kanca 2 sn) | B | BK 1.8.4, 3.10; sayı **(tahmin)** |
| `oneri_benzerlik_esigi` | dörtlüden ≥ 3 aynı → BENZER | B | **(tahmin)** |
| `juri_kazanan_min` | 8,0 | B (1 ek tur) | **(tahmin)**; EMBERFALL 420/500 = 8,4 (YR A3) |
| `juri_beraberlik_fark` | ≤ 0,3 → birleştir | — | **(tahmin)**; YR A3/A4 birleştirme deneyimi |
| `juri_veto_uretilebilirlik` | medyan < 5 → elenir | H | **(tahmin)** |
| `revizyon_madde_kapanis` | KRİTİK ve ORTA maddelerin %100'ü "uygulandı" ya da gerekçeli | H | YR A5, A8 ("gerekçesiz madde bırakmaz") |
| `salinim_dusus` | GENEL medyan önceki turdan ≥ 1 düşerse en iyi sürümden devam | — | **(tahmin)**; B2 P1 v7 6 → v8 5 (H/proje-b2) |
| `doktor_tetik_iyilesme` | tur 3'te iyileşme < 0,5 | — | **(tahmin)** |
| `yapisal_tur_alt_esik` | KRİTİK 0 ve GENEL ≥ 7,5 ise 5–6. tura izin | — | **(tahmin)** |
| `zaman_belirsizlik_bandi` | ±%15 | — | **(tahmin)**; plan süreleri bilinmeden yapılan ölçüm |
| `sahne_siniri_durum_esitligi` | S_n çıkış = S_n+1 giriş (aynı karakter/nesne), aksi `zaman.atlama` ya da ekranda olay | H | ZN §3.7 kural 4'ün sahne ölçeği; özellik (b) |
| `bilgi_durumu_ihlali` | karakter bilmediği kimliği replikte kullanıyor | H | ZN §7.2.5 oyuncu denetimi, BK 2.8 |
| `kanon_ihlali` | ölü/ayrılmış karakter konuşuyor; evren kuralı çiğneniyor; NE YOK kelimesi | H | YR §5, özellik (f) |

**Eşiklerin ayarlanması (uydurmamak için):** **(tahmin)** işaretli her eşik ilk iki filmde **yalnız BAYRAK** olarak çalışır
(HATA olanlar hariç, onlar kaynaklı). Her filmden sonra `hikaye_odasi.py karne` şunu yazar: hangi BAYRAK'lı sahne animatik
ya da kurgu seyircisinde gerçekten sorun çıkardı (isabet) ve hangisi çıkarmadı (yanlış alarm). İsabet oranı yüksek olan
eşik HATA'ya yükseltilir, düşük olan gevşetilir — ders defteri kaydıyla (AR2 §7 kalibrasyon ilkesinin hikâyeye uyarlaması).

## 8. Kesin kararların (atomik zincir + 6 özellik + gerekiyorsa ses kararı) kendi alanımda uygulanışı

### 8.1 Karar 1 — Kullanıcıya yalnız konu sorulur
- Tek soru H0'daki metindir. Eskiden kullanıcıya bırakılan iki hikâye kararı artık ekipte: **A/B öneri seçimi** (B2 ve B3'te
  kullanıcı seçiyordu — UH §1) → kör jüri + `juri-topla` betiği; **proje kararları (YR A0)** → kanal kararları dosyasındaki
  kalıcı varsayılanlar + konu kartındaki varsayım defteri.
- Kullanıcı **bilgilendirilir ama onaya zorlanmaz**: seçimden sonra 1 sayfa sade özet, kilitten sonra 5 satır. CLAUDE.md
  "İnsan yalnızca isterse onay noktalarında devreye girer" diyor; kullanıcı kendiliğinden itiraz ederse itiraz kesin
  istek olur ve ilgili aşama yeniden açılır.
- Kullanıcının bilmediği kavramlar (soğuk açılış, cliffhanger, leitmotif) özette kibarca açıklanır (BK 7.13).

### 8.2 Karar 2 — Atomik eylem zinciri (hikâye tarafı)
Hikâye odası plan yazmaz; ama zincirin **uçlarını ve hammaddesini** o üretir. Yönetmenin işini mümkün kılan kurallar:
1. **Gözlenebilir eylem dili:** EKRAN bloğunda sonuç fiilleri (take, grab, prepare, search, fight, use…; RE
   `yasak_sonuc_fiilleri`) **BAYRAK** alır. "She prepares to flee" yerine "She stuffs bread into the satchel, slings the
   rope over her right shoulder". Bu cümleler yönetmenin 2–3 adımlı zincirlerine doğrudan bölünür.
2. **Sahne uçları = zincirin uçları:** her sahnenin `giris_durumu`/`cikis_durumu` (konum, poz, kostüm varyantı, yara,
   nesne kimde/hangi elde/durumu) yazılır. Yönetmenin ilk planının `baslangic_durumu` ve son planının `bitis_durumu` bunlarla
   **olgu olarak** eşit olmak zorundadır (§5.2 aktarım tablosu). Sahne arası değişim yalnız iki yolla olur: ekranda bir olay
   ya da `zaman.atlama` (kartla veya replikle verilir).
3. **Nesnenin her el değiştirmesi bir olaydır** (8 başlığın 4. başlığı): "düdük Sera'ya geçti" ekranda gösterilmeden sonraki
   sahnede Sera'nın elinde olamaz ("öteki yumurta", "kömür diski" dersleri — DR).
4. **Konuşma ile el işi ayrılır:** aynı EKRAN satırında hem replik hem nesne manipülasyonu yazılmaz (ZN §2.3: Flow dudakları
   bozar). Senarist eylemi repliğin öncesine ya da sonrasına koyar.
5. **El işi yoğun vuruşlar** (düğüm atmak, kilit açmak, yazı yazmak, iğne-iplik) `riskli` işaretlenir ve hikâye bunları
   **ekleme + tepki** ile anlatılabilecek biçimde kurar (ZN §3.5) ya da başka bir eylemle değiştirir.
6. **Hangi el / yön:** el ve yön bilgisi hikâyenin anlamını taşıyorsa (yara sol kolda, yüzük sağ elde) karakter kartına ve
   `giris_durumu`'na yazılır; ayna yasağı gerektiren asimetrik ayrıntılar (ZN §3.3) baştan bilinir.

### 8.3 Karar 3 — Altı özellik
**(a) Animatik + habersiz seyirci:** Hikâye odası animatik seyircisinin **ölçüm altyapısını** hazırlar: aynı 6 ölçüt, aynı
`SORULAR.md`, aynı `kontrol_onermeleri` ve `MERAK_DEFTERI`, aynı ad maskeleme kodu (`ekran_metni.py`). Böylece kâğıt (8) →
animatik (?) → kurgu (?) puanları aynı cetvelle kıyaslanır ve "hikâye sağlamdı ama görüntü bozdu" ile "hikâye zaten
eksikti" ayrılabilir. Animatik bulgusu `tur: hikaye` ise H13'teki dar kapsamlı geri dönüş yolu işler. İlk 2 dk'nın
seçilen sürümü animatikte ilk sınanan parçadır.

**(b) Dünya durumu defteri + zıplama denetimi:** Defterin hikâye katmanı benim: sahne sınırlarında karakter yeri, kostüm
varyantı, yara/kir, nesne sahipliği ve **bilgi durumu** (kim neyi biliyor). Bilgi durumu yeni bir eksendir: görsel değil
ama seyircinin en çok takıldığı kopukluklardan biri ("Bunu nereden biliyor?"). Makine: `senaryo-denetim` sahne sınırında
olgu eşitliğini (`sahne_siniri_durum_esitligi`) ve replikteki bilgi kullanımını (`bilgi_durumu_ihlali`) denetler. Plan
düzeyindeki defteri süreklilik ekibi tutar; benim sahne uçlarım onun **başlangıç ve bitiş sınır koşuludur**.

**(c) Referansla otomatik yüz kontrolü:** Hikâye tarafındaki katkı, kontrolün **başarabileceği** bir kadro tasarlamaktır:
ana karakterler kırpılmış küçük karede bile ayırt edilir (saç rengi + kostüm rengi + bir ayırt edici; `gorsel_ayirt_edici`
alanı zorunlu); ikiz/benzer yaşta-benzer saçlı ana karakter yok (olay gerektirmedikçe); kostüm varyantı karakter başına ≤ 2;
konuşan ≤ 8. AN T15'teki tek büyük eleştiri ("appearance of the characters keep changing", 803 beğeni) hikâye aşamasında
**yüz sayısını ve varyantı azaltarak** da küçültülür.

**(d) Kare zinciri (son kare → sonraki başlangıç):** Senarist sürekli eylem akışlarını (aynı mekân, zaman atlaması yok)
`zaman.atlama: "yok"` ile işaretler; sahne başına doğal **yeniden demirleme noktaları** (bir ekleme, bir tepki, bir yer
değişimi) koyar, çünkü zincir derinliği 2'yi geçince kalite düşer (AR2 §2.3). Bir sahnede 90 sn'den uzun kesintisiz tek
akış yazmaktan kaçınır ya da ortasına bir ekleme/tepki vuruşu koyar (ZN §3.2 "yeniden konumlandırma" kuralıyla uyumlu).

**(e) Kendi kendine öğrenen ders defteri:** Hikâye odası defterin hem okuru hem yazarıdır. Okur: brifing `hikaye`
etiketli doğrulanmış dersleri otomatik içerir (H2). Yazar: film sonunda `karne` hikâye kaynaklı bulguları ders adayı
yapar (ör. "ilişki sözcüğü 3. dakikadan önce verilmezse 3 seyircinin 2'si kopuyor"). Bir ders **iki filmde** tekrar
görülmeden `dogrulandi` olmaz (aşırı uydurmaya karşı). Makinece denetlenebilir dersler `hikaye_esikleri.json`'a eşik olarak
girer (§7.2 kalibrasyon kuralı). Yayın verisi (izlenme, tutma) kullanıcı YouTube Studio'dan verirse **kanıt** olarak
eklenir; tahminle ders yazılmaz.

**(f) Kalıcı seri evreni kütüphanesi:** §5.3 `EVREN.json` hikâye tarafı; H1'de okunur (seri tespiti), H3/H7'de kanon ve
NE YOK kaynağıdır, H10'da denetim kuralıdır, H13'te ön kayıt (ad ve kostüm varyantı kilidi), H14'te güncellenir.
Kütüphane film klasörünün **dışında** (`YZ_FILM/EVREN/<SERI>/`) durur ve arşivlemede D'ye taşınmaz (sonraki filmin girdisi).

### 8.4 Karar 4 — Ses/dudak (hikâye tarafındaki gereklilikler)
Yöntem seçimi ses uzmanınındır; araştırmanın önerisi Veo'nun kendi konuşması + ses dönüştürme, yedek TTS + dudak senkronu
(AR3 A2). **Hangi yol seçilirse seçilsin** hikâye odası şunları garanti eder:
1. **Replikler filtre-güvenli:** replik metni Veo istemine `X says: "…"` olarak girer (BK 4.2.4); bu yüzden replikte de
   "little, baby, child…" ve yaş ifadeleri yoktur (bugünkü `istem_denetim` repliği taramıyor — §6'da düzeltiliyor).
2. **Replik metni dondurulur ve kimliklidir** (`R0011`): Veo kelime atlarsa/eklerse whisper karşılaştırması (WER) bu
   metne göre yapılır (AR3 A2 metin kapısı); altyazı hizalaması (stable-ts `align`) aynı metni kullanır.
3. **Her karakterin sabit `ses_tarifi_en` dizesi** (cinsiyet, yaş bandı, tını, aksan, tempo; ≤ 15 kelime **(tahmin)**):
   Veo yolunda her klipte kelimesi kelimesine tekrarlanır (AR1 B3 "bir kez yaz, aynen tekrarla"), dönüştürme yolunda
   dönüştürücünün daha az zorlanması için, TTS yolunda ses seçiminin tarifi olarak kullanılır.
4. **Replik başına `ton` fiili** (whispers / says quietly / says coldly / raises his voice / shouts) ve bundan türeyen
   seviye sınıfı (fısıltı/yumuşak/normal/bağırma → RE `diyalog_lufs`). Bir replik bloğunda tek ton (dönüştürücüler ton
   geçişinde zorlanır — AR3 A2 "fısıltı ve bağırmada zorlanır").
5. **Telaffuz güvenli adlar** (§7.2 ad kuralları) ve `sozluk.adlar.telaffuz`: Veo her klipte adı yeniden okur; zor uydurma
   adlar klipten klibe farklı söylenir.
6. **Üst üste konuşma, replik ortasında gülme/ağlama yok;** duygu replikten önceki ya da sonraki ayrı vuruşta (tepki planı).

### 8.5 Karar 5 — Memmet ve Flow uyarısı
Hikâye odası Flow'a dokunmaz. Dolaylı katkısı: üretilebilir hikâye = daha az yeniden üretim = daha az gönderim. Her
yeniden deneme hem kredi hem "olağan dışı etkinlik" riskidir (DR); bu yüzden üretilebilirlik jürisinin vetosu ve riskli
sahne çözümleri kâğıtta zorunludur. Hikâye odası hiçbir aşamada "Flow'da dene, bakalım" önermez.

### 8.6 Karar 6 — Üstün körü iş yok
Seyirci sayısı 3'ün, jüri 5'in, mimar 4'ün altına inmez; tur sınırına "zaman yok" diye erken çıkılmaz; bütün yargı ajanları
Opus/high. Kullanım sınırına takılırsa iş durur ve dosyadan devam eder, kısaltılmaz. Kaynaksız sayı yazılmaz (bu belgede
**(tahmin)** işaretli olanlar kalibrasyon listesindedir).

## 9. Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

### 9.1 Riskler ve önlemler

| # | Risk | Neden önemli | Önlem |
|---|---|---|---|
| R1 | **Claude'un Claude'u puanlaması** (yazar, jüri ve seyirci aynı model ailesi) — puan şişmesi | Kâğıtta 8 alıp kurguda 6 almak, B2'deki "kâğıtta mantıklı, kurguda kopuk" dersinin tekrarıdır (H/kurgu-izleme-denetimi) | Medyan; her turda yeni seyirci; "cömert olma" + puan çapaları (`JURI_TABLOSU.md`); **kâğıt ↔ animatik ↔ kurgu puan farkı** her filmde karneye yazılır; kâğıt puanı kurgudan sistematik olarak > 1 yüksekse kâğıt eşiği yükseltilir. Çapraz model seyirci açık soru (Q2) |
| R2 | **Habersizlik sızıntısı** | Seyirci amaç alanını görürse "bilgi kâğıtta kaldı" hatası yakalanmaz (B1 "84. çekim") | Paket yalnız EKRAN; bekçi kancası; ad maskeleme; **EKRAN dilinde iç durum fiilleri BAYRAK** (realizes, decides, remembers, knows — görülen satırı yalnız gözlenebilir şeyi yazar; aksi hâlde yazar bilgiyi "görüntü"ye gizlice koyar) |
| R3 | Ad maskelemenin kısmi kalması (lakap, unvan, "Captain") | Seyirci adı paketten öğrenir, ekrandan değil | Karakter kartında `hitaplar[]` (Captain, brother, Mother…) da maskelenir; maskeleme testleri (§6 test a); kalan durumlar seyirci raporunda "isim nereden çıktı" sorusuyla yakalanır |
| R4 | Ölçüt avcılığı (Goodhart) — formül hikâye | Eşiklere uyup ruhsuz kalan film izlenmez | Yaratıcı eşiklerin çoğu BAYRAK; jüride `ozgunluk`; bonus mimar; seyirci ölçütleri eşik değil his sorar ("endişelendim mi?") |
| R5 | Uzun metinde dikkat dağılması (40 dk ≈ 50 sahne) | Seyirci P3'te yüzeyselleşir (AR1 C, LongStoryEval) | Parti parti sıralı okuma ve parti başına OZET; senarist de parti parti yazar |
| R6 | Hikâye zamanının tahmin olması | Z1 zaman eşikleri yanlış alarm verebilir | ±%15 bant (§7); plan sonrası kesin ölçüm yönetmen/makine kapısında tekrar |
| R7 | Aynı yazar örneğinin sürdürülememesi (oturum, sıkıştırma) | "Revizyonu yazan yapar" ilkesi bozulur | `yazar_defteri.md` (karar — neden — yanlışsa maliyeti); yeni örnek önce onu okur |
| R8 | Kullanım sınırı / süre (35–60 Opus çağrısı **(tahmin)**) | Hikâye odası saatler sürebilir | Dosya tabanlı devam; paralel çağrılar tek mesajda; kısaltma yok (karar 6) |
| R9 | **Hikâye kalitesinin izlenmeyi garanti etmemesi** | B1 ≈ 671 izlenme (OB); tutma/CTR verisi yok (BK 1.8.5) | Kullanıcıya dürüstçe söylenir; başlık/kapak vaadi ve "Full Movie" formatı veriye göre seçilir ama **[H]** olarak işaretlenir; yayın verisi gelirse ders defterine kanıt |
| R10 | Konu filtreyle çatışıyor (insan çocuk kahraman: "a girl and her dragon") | `girl/child/young` ve yaş ifadeleri filtreye takılır (DR) | Konu kartında dönüşüm (yetişkin kahraman ya da çocuk yalnız dolaylı anlatım: eller, siluet, "blanket-wrapped figure") + varsayım defteri. Kullanıcının konusunu değiştirmek riskli → Q7 |
| R11 | Telif / var olan eser konusu | Kanal riski | Konu kartında `donusum`; jüride özgünlük; ad/olay/tasarım kopyası HATA |
| R12 | Kanca kopyası (hit başlığın aynısı) | "Hit kopyaları tutmuyor" (BK 1.3.2) | `baslik_gecmisi` + kalıp ama yeni içerik; jüri `ozgunluk` |

### 9.2 Diğer uzmanlarla çakışabilecek noktalar (her biri için önerdiğim sınır)
1. **Yönetmen:** sahne grubu sınırlarını ve hedef süreleri kim belirler? — Öneri: hikâye odası `sahneler[]` sınırını ve
   hedef süreyi yazar, yönetmen ±%20 **(tahmin)** oynayabilir; daha büyük değişiklik ya da sahne bölme/birleştirme senariste
   döner. **Replik metni** yalnız senaristte; yönetmen bölebilir (ekran dışı L kesme), değiştiremez. `ekranda_bilgi`
   (plan) ↔ `seyirci_ogrenir` (sahne) birleşimi makinece eşleştirilir.
2. **Süreklilik / dünya durumu defteri:** benim `giris_durumu/cikis_durumu` biçimimle yönetmenin `baslangic_durumu`
   biçimi (`{tarif_en, konumlar, bakislar, nesneler[{ad,kimde,el,durum}]}` — ZN §6.1) **aynı alt şemayı** kullanmalı;
   önerim: ZN'deki plan şemasını temel alıp `karakterler.{yer, kostum, yara}` ve `bilgi` eklemek. Defter tek dosya mı
   (`DUNYA_DURUMU.json`), katmanlı mı (hikâye/plan) — süreklilik uzmanıyla ortak karar.
3. **Ses:** `ses_tarifi_en` ve `ton` sözlüğü ortak olmalı; replik Veo istemine girecek mi (ses yöntemine bağlı) — girse
   de girmese de filtre-güvenli yazıyorum (§8.4).
4. **Görsel/kart:** `gorsel_ayirt_edici` ve kostüm varyant kimlikleri (`sera_k1_pelerin`) kart dosya adlarıyla aynı olmalı;
   `EVREN.json`'da hikâye, kart ve ses anahtarlarının **ayrı sahipleri** var → aynı dosyaya eşzamanlı yazma çakışması.
   Önerim: `EVREN/<SERI>/hikaye.json`, `kartlar.json`, `sesler.json` ayrı dosyalar + birleştiren salt okunur `EVREN.json`.
5. **Yayın:** mevcut `yayin-paketcisi` taslağı başlıkta "kill" kelimesini yasaklıyor; oysa kazanan örnekler ve pilot başlık
   bu kelimeyi taşıyor ("She Raised a Monster They Tried to **Kill**" 3,3M; "…They Ordered Her to **Kill**" — BK 1.6, PJ).
   Reklam ("sarı dolar") etkisine dair veri yok. Bölüm adları ve Short adayları benden, son seçim yayından.
6. **Orkestratör (`film.py`):** `metin` sağlayıcısı ve `GOREV_<asama>.md` el sıkışması; aşama adları; `FILM_DURUM.json`'a
   hikâye aşamalarının eklenmesi orkestratör sahibiyle uzlaşılmalı.
7. **Animatik / kurgu denetimi:** aynı 6 ölçüt, aynı `SORULAR.md`, aynı ad maskeleme — `izleme_paketi.py` sahibiyle ortak.
8. **Eşik dosyası:** `hikaye_esikleri.json` ayrı mı, `ritim_esikleri.json`'a mı eklenir? ZN "her sayı orada" diyor; çakışmayı
   önlemek için ayrı dosya önerdim, ileride birleştirilebilir.
9. **Ders defteri:** `hikaye` etiketli girdinin şeması ve `aday → dogrulandi` kuralı defter sahibiyle ortak olmalı.

### 9.3 Açık sorular
- **Q1.** Bonus mimara ilk üç önerinin yalnız logline'larını vermek (bağımsızlık kuralına dar istisna) kabul mü? Alternatif:
  bonus da kör çalışır, çeşitliliği yalnız eksen ataması ve `BENZER` denetimi sağlar.
- **Q2.** Jüri ya da seyircilerden birini **başka bir model** (ör. Gemini) yapmalı mıyız? ARIS "hiçbir model kendi çıktısını
  onaylamaz" diyor (AR1 B4). Kullanıcının Gemini erişimi var ama hatta Gemini **metin API'si** tanımlı değil.
- **Q3.** 6 kâğıt tur + ikinci öneriyle yeniden açılış da 8'e ulaşmazsa hat durur. Kesin karar 1 ile bu "engel bildirimi"
  uyumlu mu, yoksa ekip en iyi sürümle **uyarı notuyla** devam mı etmeli? (Ben durmayı öneriyorum: karar 6.)
- **Q4.** Film süresi: 40 dk sabit hedef mi, yoksa 30–45 arasında hikâyeye göre serbest mi? Dolgu yasağı (ZN §2.5) ikinciyi
  gerektiriyor; ben `film_sure_hedef_sn`'i senaristin yapı aşamasında ±5 dk belirlemesini öneriyorum.
- **Q5.** Her film yeni bir **seri başlangıcı** mı olmalı (seri kancası zorunlu), yoksa tek film de kabul mü? Veri seriden
  yana (BK 2.4); varsayılanım: her film kendi içinde kapanır + ≤ 2 seri sorusu açık bırakır.
- **Q6.** Başlıkta "Kill" — yayın uzmanıyla ortak karar (§9.2-5).
- **Q7.** Konu insan çocuk kahraman gerektiriyorsa ekip konuyu dönüştürebilir mi (kullanıcıya sormadan)? Önerim: dönüştür,
  varsayım defterine yaz, özette açıkça söyle ("yüzüne vur" — BK 7.13).
- **Q8.** Kullanıcı isterse kilitlenmeden önce hikâyeyi okuyabilsin mi (isteğe bağlı, varsayılan kapalı)? CLAUDE.md
  `--onayli` modu bunu ima ediyor; kesin karar 1 ise sorulmamasını istiyor. Önerim: sorulmaz, ama `--onayli` modda 1 sayfalık
  özet gösterilip 1 dakika itiraz penceresi verilir **(tahmin)**.
- **Q9.** Ajan frontmatter'ında `hooks` + `PreToolUse` sözdizimi ve Windows'ta kancanın Python yolu kurulumda sınanmalı
  (AR3 B5 alanın varlığını söylüyor; tam sözdizimi bu oturumda denenmedi).
- **Q10.** Kalibrasyon çapası: B2/B3'ün hikâye v2'leri ve seyirci raporları `D:\YZ_FILM_ARSIV\`'de (OB). Depoya alınırsa yeni
  seyirci ajanı eski metinleri okuyup eski puanlarla kıyaslanabilir (puan şişmesi ölçümü). Kullanıcıya sormadan bu yapılamaz;
  ilk filmde çapasız başlanır.

---
*Bu belge senarist uzmanının 1. tur önerisidir; diğer uzmanların belgeleri okunmadan yazıldı. Sayıların kaynağı her
satırda yazılıdır; **(tahmin)** işaretli olanlar §7.2'deki kalibrasyon kuralıyla ilk iki filmde ayarlanacaktır.*
