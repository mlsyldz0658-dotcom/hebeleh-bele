# TUR 2 — SENARİST UZMANI: Hikâye odası (itirazlar, çakışmalar, revize nihai öneri)

Hazırlayan: senarist uzmanı (Claude Opus 5.5). Tarih: 23.10.2026. Durum: TAMAM (2. tur).
Okunanlar: `tartisma/` altındaki 7 tur-1 dosyasının tamamı (kendi dosyam dahil) ve tur 1'deki kaynak belgeler.

**Dosya kısaltmaları:** [MİM] `tur1_claude-code-mimari.md` · [YÖN] `tur1_yonetmen.md` · [KUR] `tur1_kurgucu.md` ·
[GÖR] `tur1_goruntu-sureklilik.md` · [SES] `tur1_ses-muzik.md` · [ÜRE] `tur1_uretim-muhendisi.md` · [SEN1] benim tur-1 dosyam.
**Kaynak kısaltmaları (tur 1'deki anlamlarıyla):** `BK` BILGI_KURALLARI · `ZN` ZANAAT · `RE` ritim_esikleri.json (anahtar adıyla) ·
`AR1/AR2/AR3` arastirma/01–03 · `UH` 01_URETIM_HATTI · `DR` 03_DERSLER · `YR` YAPIM_REHBERI · `KR` KARARLAR · `AN` ARASTIRMA_NOTLARI ·
`OB` 00_OKU_BENI + 05_PROJELER_VE_ARSIV · `H/<ad>` HAFIZA_YEDEGI notu.
Kaynağı olmayan her sayı **(tahmin)** diye işaretlidir; ilk iki filmde §4.7'deki kalibrasyon kuralıyla ayarlanır.

**Bu turun özü (5 satır):**
1. [MİM]'in görev defteri, kör paket ve erişim kancası modelini kabul ediyorum. Tur 1'deki `metin` sağlayıcısını,
   `GOREV_<asama>.md` el sıkışmasını ve ajan dosyasına gömülü seyirci kancasını geri çekiyorum.
2. Hikâye odası ajanları 10'dan 6'ya (+ 2 ortak) indi: konu-analisti → `yapimci`, senarist → `hikaye-yazari`,
   anlama-olcer → `ozet-eslestirici`, hikaye-doktoru → `yapimci` doktor kipi, evren-arsivcisi → `hikaye-yazari` evren kipi.
3. En önemli üç itiraz: (★1) hikâye kaynaklı bulguların yönetmene gitmesi ve yeni sahnenin kullanıcıya sorulması; (★2) habersiz
   seyirciye `ekranda_bilgi` ve önceki film özeti verilmesi; (★3) yönetmenin sahne dökümünü yeniden yapıp sahne değerini ve uçlarını yazması.
4. Yeni çözümler: kök nedene göre **betiğin** verdiği bulgu yönlendirmesi; film süresinin **yazımdan önce** bütçeye göre seçilmesi
   (ZN §2.6 "kısaltılır" ile "kısaltma yok" çelişkisinin çözümü); kâğıt seyircide aşamalı GIRDI ile zorunlu sıralı okuma; replik başına
   `tasidigi` alanı; kilitten sonra 0 kredili "ekran dışı köprü replik" basamağı.
5. Revize nihai öneri §4'te, tur 1 biçimindeki 9 başlıkla ve kendi başına okunur biçimde.

---

## 1. Diğer önerilere itirazlarım

Biçim: **Dosya + madde** · **İtiraz** · **Neden** · **Önerim**. ★ = en önemli üç itiraz.

### ★İ1 — Hikâye kaynaklı bulgular yönetmene gidiyor, yeni sahne kullanıcıya soruluyor
- **Dosya + madde:**
  - [KUR] §2.2 K5: "Hikâye/plan düzeyindekiler `YENIDEN_YAZ.json`'a (kâğıt, 0 kredi) yazılır → yönetmen düzeltir". Ayrıca §4 Tarif A adım 8.
  - [YÖN] §2 Y7: plan kaynaklı maddeler `plan-yazari`na, sahne düzeyi maddeler `yonetmen`e gider; hikâye yolu yok.
  - [YÖN] Y10 ve [KUR] §5.5 K2: "Yeni sahne gerekiyorsa `--onayli` modda kullanıcıya sorulur."
- **İtiraz:** Animatik ve kurgu seyircisinin "bu kim", "bunu nereden biliyor", "neden umursayayım" türü bulguları yönetmene gidiyor.
  Yönetmen bunu plan ekleyerek kapatırsa replik, bilgi durumu, kurulum ve merak defteri hikâye belgesinden kopar.
- **Neden:**
  - Replik ve sahne içeriğinin tek sahibi hikâye yazarıdır ([MİM] §2.2 #2 "tek yazar ilkesi"; [YÖN] §3.2'nin kendi kuralı: "replik metnini kendiliğinden değiştirmez").
  - Revizyonu metni yazan yapar (YR §1.4).
  - [KUR] §5.6 kök neden sözlüğünde zaten bir "Hikâye" satırı var (`kurulum_yok`, `ad_gec`, `risk_belirsiz`, `duygu_hak_edilmedi`), ama yönlendirme bu satırı kullanmıyor.
  - Yeni sahneyi kullanıcıya sormak kesin karar 1'e aykırı. CLAUDE.md'deki `--onayli` "isterse onay" demektir, varsayılan soru değildir.
- **Önerim:** §2.4'teki makineli yönlendirme. Betik (`hikaye_odasi.py bulgu-sinifla`) bulguyu `HIKAYE.json`'a bakarak sınıflar:
  - Bilgi hikâyede EKRAN'a yazılmış ama planda yoksa → yönetmen (`hikaye_adimi_ekranda_yok`).
  - Bilgi hikâyede hiç yoksa → `hikaye-yazari` (dar kapsamlı değişiklik, §4.2 H15).
  - Yeni sahne gerekiyorsa içeriğini (EKRAN, replik, uç durumları) `hikaye-yazari` yazar, yönetmen planlar.
  - Hiçbir modda kullanıcıya soru sorulmaz. `--onayli` modda yalnız bilgi verilir.

### ★İ2 — Habersiz seyirciye cevap anahtarı ve dış özet veriliyor
- **Dosya + madde:**
  - [ÜRE] §2.1 K11: plan seyircisinin girdisinde `ekranda_bilgi` var.
  - ZN §7.3 girdi listesi: `ekranda_bilgi` ve "önceki filmlerin izleyici özeti".
  - [MİM] §5.8 kör paket "Verilir: önceki filmlerin `IZLEYICI_OZETI.md`'si" ve §3.2 habersiz-seyirci okuyacakları.
  - [KUR] §8.8: "önceki filmin seyirci özeti sonraki filmin seyircisine 'previously' olarak verilir". Yöntemin kaynağı UH §2.
- **İtiraz (iki parça):**
  - (a) `ekranda_bilgi` yazarın "seyirci burada bunu öğrenir" iddiasıdır. Seyirciye vermek cevabı söylemektir.
  - (b) Önceki filmin özeti kapı seyircisine verilirse, filmin o bilgiyi ekranda verip vermediği ölçülemez.
- **Neden:**
  - (a) [MİM] Ç-2 ve [YÖN] §3.4 zaten "verilmez" diyor; ZN §7.3 ve [ÜRE] K11 bunlardan ayrılıyor.
  - (b) UH §2'deki yöntem EMBERFALL'ın 12–15 dk'lık "Episode" biçimi içindi (OB). Yeni hedef biçim "Full Movie" (BK 1.5).
    YouTube'da serinin 2. filmine öneri akışından gelen izleyici özet okumaz.
  - B1'deki "babanın adı 84. çekimde" dersi (YR A8) seri ölçeğinde de geçerli: bilgi özette kalır, ekrana çıkmaz.
- **Önerim:**
  - (a) `ekranda_bilgi` ve `seyirci_ogrenir` hiçbir seyirci paketine girmez. Yalnız `ozet-eslestirici`nin karşılaştırma anahtarıdır.
    ZN §7.3 girdi listesi düzeltilmeli.
  - (b) Kapıyı tutan 3 seyirci **özetsiz** okur.
  - Seri devamında isteğe bağlı 4. bir "dönen seyirci" `IZLEYICI_OZETI.md` ile okur. Medyana girmez; yalnız kanon çelişkisi ve
    gereksiz tekrar bulgusu verir. Bu seyircinin değeri ilk iki filmde ölçülür (tahmin).
  - Film önceki filmden bir bilgiye dayanıyorsa o bilgi filmin içinde, ekranda verilir ve bir `anahtar_olgu` maddesi olur.

### ★İ3 — Yönetmen sahne dökümünü yeniden yapıyor, sahne değerini ve uçlarını kendisi yazıyor
- **Dosya + madde:**
  - [YÖN] §2 Y1: "hikâye ≈45–55 sahne grubuna bölünür"; `sahne_degeri`, `giris_durumu`, `cikis_durumu`, `vurus`, `kurulumlar` yazılır.
  - [YÖN] §5.3 tablosu: bu alanların "Doldurur" sütunu "yönetmen".
  - [MİM] A07a: "Parti haritası … **sahne sınır durumları**".
- **İtiraz:** Hikâye odası sahne listesini, her sahnenin değerini (`bas ≠ son`), vuruşunu ve giriş/çıkış olgularını zaten yazıyor.
  Kâğıt seyirci kapısı da bunlar üzerinden geçiyor. Yönetmen sahneleri yeniden bölerse ya da uçları yeniden yazarsa, seyircinin
  onayladığı metin ile çekilen metin ayrışır.
- **Neden:**
  - [YÖN] §9.2-1'in kendi kuralı: "aynı olgu iki yerde tutulmamalı".
  - ZN §7.4: `hedef_duygu`, `yogunluk`, `merak_*`, `kurulum`, `ironi`, `risk` hikâye odasının sorumluluğunda.
  - ZN §7.2.4: sahne değeri kuralı bir hikâye kuralıdır.
- **Önerim:** Sahne = hikâye sahnesi; kimlik 1:1 (`S07`). Yönetmen şunları yapabilir:
  - (a) Bir hikâye sahnesini yalnız mekân ya da zaman kırılımında `S07a/S07b` diye bölmek.
  - (b) Hedef süreyi ±%20 oynatmak (tahmin).
  - (c) Hikâye olgularını **inceltmek** (işaret, poz, el, ışık). Değiştiremez.
  - Birleştirme, sıra değişikliği, sahne silme, sahne değeri ya da uç olgusu değişikliği `sahne_degisiklik_istegi` ile `hikaye-yazari`na gider.
  - Betiğin `sahne-sozlesme` denetimi şunu arar: hikâyenin uç olguları ⊆ yönetmenin sahne ilk/son plan durumu (§4.5.3).

### İ4 — Hikâye odası daraltılmış, jüri kararını yazar veriyor
- **Dosya + madde:** [ÜRE] §2.1:
  - K03: "hikaye-mimari ×3, jüri ×5, hakem (senarist)".
  - K04: yapıyı "ajan: hikaye-mimari" yazar.
  - K05: "Geçmezse aynı mimar yeni sürüm yazar".
  - §3.5 bütçesi: "K03 ≈ 10 çağrı; K04–K05 ≈ 8–16".
- **İtiraz:**
  - 3 mimar (A/B + bonus) çeşitlilik için az.
  - Seçimi "hakem (senarist)" yaparsa, kazanan metni sonra kendisi yazacak rol seçmiş olur.
  - Çağrı bütçesi hikâye odasını yarıya indiriyor.
- **Neden:** YR A2 "3–4 mimar + bonus; en özgün fikir genelde bonustan çıkar"; YR §1 tarafsızlık (ana Claude ve yazar puan vermez); kesin karar 6.
- **Önerim:** 4 mimar (eksenli 3 + bonus), kör 5 jüri, karar betikte (`juri-topla`, medyan). Çağrı tahmini §4.1.4'te: 40–75 (tahmin).
  [MİM] A03–A04 bu yapıyla zaten uyumlu.

### İ5 — Özet eşleştirme jüri kipinde ya da Sonnet'te; kurgucuda proje hafızası
- **Dosya + madde:**
  - [MİM] §3.2: `juri-uyesi` "A06 `ozet_eslestirme` kipi".
  - [KUR] §3: `ozet-eslestirici` "model: sonnet".
  - [KUR] §3.1: `kurgucu` frontmatter'ında `memory: project`.
- **İtiraz:**
  - Eşleştirici bir değerlendiricidir ve kör olmalıdır; yalnız seyirci metnini ve olgu listesini görmeli.
  - Jüri tanımı önerileri, brifingi ve `.claude/skills/film-yap/*.md`'yi okuyan "denetçi" rolündedir ([MİM] §5.7). Aynı ajan iki farklı erişim rolüne düşer.
  - Sonnet ve proje hafızası kullanıcı kuralına aykırı.
- **Neden:** H/ajan-opus-yuksek (BK 7.2); [MİM] §3.1 #4–#5 (hepsi opus·high, `memory` yok); [MİM] Ç-10 (ayrı kör girdili değerlendirici ayrı ajan olur).
- **Önerim:**
  - Tek bir `ozet-eslestirici` ajanı (ad [KUR]'dan): kör rolde, `opus`/`high`, `omitClaudeMd`.
  - Kâğıt, plan, animatik ve kurgu turlarında aynı tanım kullanılır.
  - Hiçbir ajanda `memory:` alanı olmaz.

### İ6 — Kâğıt seyirci tam filmi tek pakette alıyor
- **Dosya + madde:** [MİM] §5.2 örneğindeki `GIRDI/PAKET_FILM.md`; §2.1 A06 "3 habersiz seyirci (tam film)".
- **İtiraz:** Seyirci tek pakette ileriyi okuyabilir. "Parti sonunda durabilir miydim" ve "2. dakikada devam eder miydim"
  soruları, ilerisini bilen biri tarafından cevaplanmış olur.
- **Neden:**
  - ZN §7.3'teki merak ölçütü ("parti sonunda durabilir miydim?") sıralı izlemeyi varsayar.
  - [MİM] §2.2 #4 aynı tur içinde aynı seyircinin bölüm bölüm sürdürülmesine zaten izin veriyor (izleme kipi için).
- **Önerim:** Kâğıt kipinde de aşamalı GIRDI kullanılsın: P0 (0–120 sn) → P1 kalanı → P2 → P3.
  - Seyirci bir bölümün raporunu yazınca betik sonraki bölümü GIRDI'ye kopyalar.
  - Ana Claude aynı örneği SendMessage ile sürdürür.
  - `erisim_kapisi`, henüz kopyalanmamış bölümü zaten göremez; ileriyi okumak teknik olarak imkânsızdır.

### İ7 — Önerilerde 3 parti × 8 başlık zorunluluğu
- **Dosya + madde:** [MİM] §2.1 A03 geçme şartı "3×8 başlık dolu"; mevcut `.claude/agents/hikaye-mimari.md` teslim maddesi 4.
- **İtiraz:** Dört öneride "kim nerede durur", "nesnelerin yolu" gibi üretim ayrıntılarını yazmak jüriye kadar boşa giden emek.
  Seçimden sonra kazanan yazar bu ayrıntıları zaten yeniden yazıyor.
- **Neden:** Jüri hikâyeyi seçer (YR A3). 8 başlığın 3., 4., 6. ve 8. maddeleri, seçilmiş hikâyenin plan öncesi ayrıntısıdır (UH §1: bölüm tasarımı).
- **Önerim:** Öneri 10 başlıktan oluşur (§4.2 H3). Parti tek cümlesi, vuruş listesi, riskli sahneler ve mekân/kostüm sayısı
  üretilebilirlik jürisine yeter. 3×8 yapı kazanan yazarın H7 işidir.

### İ8 — Replik kısaltma ve "anlam eşdeğer" kabulü hikâyenin dışında kalıyor
- **Dosya + madde:**
  - [SES] §2 B1: "Sığmayanlar `YENIDEN_YAZ.json` ile yönetmene döner (replik kısaltma …)".
  - [SES] §3.4: `ses-denetcisi` "anlam eşdeğerliği" kararı verir.
  - [KUR] K1: sığmayan replik yönetmene gider.
  - [YÖN] §3.2: `replik_degisti` listesi ("Kim onaylar?", [YÖN] §9.2-8).
- **İtiraz:** Kısaltma bir metin değişikliğidir. "Anlam eşdeğer" kararı repliğin hangi bilgiyi taşıdığı bilinmeden verilirse ad,
  kurulum ya da merak sorusu sessizce kaybolur.
- **Neden:** Tek yazar ilkesi ([MİM] §2.2 #2). Z1 maddeleri (ad ≤ 120 sn, kurulum → kullanım) replikteki tek bir kelimeye bağlı olabilir (ZN §4).
- **Önerim:**
  - Her replikte bir `tasidigi` alanı olur: taşıdığı `anahtar_olgu`, `merak`, `kurulum`, `ad` ve `ironi` kimlikleri.
  - Kelime değiştirmeyen bölme yönetmende ya da kurguda serbesttir; kayıt düşülür.
  - Kısaltma ve kelime değişikliği `hikaye-yazari`na gider. Diyalog editörü, gerekirse oyuncu da yeniden bakar.
  - `ses-denetcisi`, `tasidigi` öğelerinden biri duyulan metinde yoksa "kabul" veremez; repliği yeniden çekime ya da Yol B'ye yollar.

### İ9 — Kart tasarımcısı görünüşü hikâyeden habersiz değiştirebiliyor
- **Dosya + madde:** [GÖR] §2.2 A2/A4: "iki karakter çok benziyorsa saç rengi/yüz biçimi ayrıştırılır"; §3.3.
- **İtiraz:** Replikte ya da hikâyede görünüşe bağlanan bir öğe ("the red-haired one", "the scarred man") kartta değişirse hikâye bozulur.
- **Neden:** Kadro ayrışması gerekli (BK 1.4 "appearance keep changing"; [GÖR] B11), ama hikâyeyle bağ makinede tutulmuyor.
- **Önerim:**
  - Karakter kartında `gorsel_ayirt_edici[].hikaye_baglayici: true/false` alanı olur.
  - Hikâyeye bağlı öğe kilitlidir; yalnız `hikaye-yazari`nın isteğiyle değişir. Diğer öğeleri kart tasarımcısı ayrışma için serbestçe değiştirir.
  - Replikler görünüşe yalnız hikâyeye bağlı öğeyle atıf yapar (makine denetler).
  - [GÖR] §9.2'deki `bilincli_benzerlik` alanını (ikizler, kılık değiştirme) kabul ediyorum.

### İ10 — Tur tavanı dolunca "en iyi sürümle bayraklı devam"
- **Dosya + madde:** [MİM] §9.3 S-3. (Kurgu için [KUR] K9'un son maddesine itirazım yok.)
- **İtiraz:** Hikâye kapısında bayraklı devam etmek, eşiği geçmemiş bir hikâyeye yönetmen, kart ve kullanıcının Gemini paket emeğini
  (≈ 15 paket, [ÜRE] R2) harcatır.
- **Neden:**
  - Kâğıt puanı kurgu puanının genelde üstünde çıkar, altında kalmaz: B2'de "kâğıtta mantıklı, kurguda kopuk" görüldü
    (H/kurgu-izleme-denetimi); B3'te kâğıt puanları 6/8/7 idi (OB). Kâğıtta 8'e ulaşmayan hikâyenin animatikte 8 alması beklenmez.
  - ZN §7.3 de eşiğe ulaşılmazsa "raporlanır" der, "devam edilir" demez.
  - Kesin karar 6.
- **Önerim:** §4.2 H11'deki merdiven:
  1. 4 tur.
  2. KRİTİK 0 ve GENEL ≥ 7,5 ise doktor + 2 yapısal tur.
  3. Jürinin ikinci önerisi H7'den başlar (en çok 4 tur).
  4. Hâlâ geçmezse DUR ve engel bildirimi (soru değil).
  - [MİM]'in "yapısal kurtarma turu (yapımcı + yazar)" fikri bu merdivenin ikinci basamağıdır.

### İ11 — Başlık ve bölüm adları yayın aşamasında doğuyor
- **Dosya + madde:**
  - [MİM] §3.2: `yayin-paketcisi` "başlık (3 aday), … bölüm adları (merak cümlesi, ≤ 8)" yazar.
  - Mevcut `.claude/agents/yayin-paketcisi.md`: başlıkta "kill" yasağı.
- **İtiraz:**
  - Başlık ve kapak filmin ilk sözleşmesidir; hikâye ona göre kurulur (vaat imgesi ≤ 120 sn, RE `vaat_imgesi_max_sn`; risk ≤ 180 sn'de sözle).
    Yayın aşamasında yeni başlık yazılırsa vaat sözleşmesi bozulabilir.
  - "kill" yasağının kaynağı yok. Kazanan başlıklar bu kelimeyi taşıyor ("She Raised a Monster They Tried to Kill", 3,3M; BK 1.6).
- **Önerim:**
  - Başlık adayları (3), kapak imgesi, bölüm adları (≤ 8) ve Short adayları hikâye odasında yazılır (`HIKAYE.json`).
  - Yayın bunlardan **seçer**, zamanları kurgudan alır ve YouTube kurallarını doğrular. Yeni başlık yazarsa `vaat-denetim` betiğinden geçmek zorundadır.
  - "kill" yasağı BAYRAK'a iner. Reklam etkisine dair veri gelirse ders defterine girer.

### İ12 — Ana Claude brifing yazıyor (kendi tur-1 önerim dahil)
- **Dosya + madde:** [ÜRE] §2.1 K02 ("ana Claude + (senarist)"); [SEN1] H2 (bölüm 7 ve 8'i ana Claude yazar).
- **İtiraz/düzeltme:** Ana Claude içerik üretmez ([MİM] §3.1 #1). Kendi önerimi de bu yönde düzeltiyorum.
- **Önerim:** Brifing = betiğin doldurduğu kalıp bölümleri + `yapimci`nın konu yorumu. Eksen satırı her mimarın kendi `ISTEM.md`'sine girer;
  böylece brifingin sha1'i dört mimarda da aynı kalır ([MİM] A02).

### İ13 — Mekân sayısı ve krokinin hikâyede yazılması
- **Dosya + madde:** [GÖR] §1.4 "≤ 6 mekân (`hikaye-mimari.md`)"; [SEN1] `mekan_max` 10 ve 8 başlığın 6. maddesindeki kroki notu
  ("kapı batı, ocak kuzey"); [YÖN] Y2 metrik kroki.
- **İtiraz (kendime de):**
  - Hikâyenin kapı yönü yazması yönetmenin krokisiyle çelişebilir.
  - 6 mekân 40 dk ve 45–55 sahne için dar; 10 mekân kart yükü için geniş olabilir.
- **Önerim:**
  - Hikâye yalnız **hikâye olgularını** yazar: tek giriş var, pencereden yol görünür, ateş yakmak yasak. Yön ve ölçü yönetmenindir.
  - Sınır: tekrar eden (≥ 3 sahnede kullanılan) mekân ≤ 6, toplam mekân ≤ 10. Tek sahnelik mekânlar ağırlıkla dış/doğa olur.
    Bu sınır BAYRAK'tır (tahmin); üretilebilirlik jürisi bakar.

### İ14 — Ayrı `kurgu-seyircisi` ajanı
- **Dosya + madde:** [KUR] §3 `kurgu-seyircisi` (yeni) ve §9.2-1 ("ajan ikiye bölünürse").
- **Önerim:**
  - Tek `habersiz-seyirci` ajanı, kipleri `kagit | plan | ilk2dk | animatik | kurgu` ve tek rapor şemasıyla ([KUR] §5.3 temel alındı, §4.5.6).
  - Böylece kipler arası puanlar aynı cetvelle kıyaslanır; kâğıt → animatik → kurgu farkı ders defterine girer.
  - [KUR]'un izleme kipi gövde metni bu ajana girer.

---

## 2. Çakışmalar ve önerdiğim çözüm

### 2.1 Alan, ajan ve dosya adları

| Kavram | Öneriler (dosya) | Önerim | Gerekçe |
|---|---|---|---|
| Seyircinin anlaması gereken olgular | `kontrol_onermeleri` 12–20, film düzeyi [SEN1] · `ana_olgular[10]` [MİM] · `ANAHTAR_OLGULAR_P<p>` 8–12/parti [KUR] | **`anahtar_olgular[]`**, her maddede `hikaye_partisi`, `kritik`, `ekranda` (taşıyan sahne/replik); parti başına 8–12 (tahmin) | ZN §7.3 eşleşmeyi parti özetiyle yapar; `ekranda` alanı bulgu yönlendirmesini mümkün kılar |
| Özet eşleştirici | `anlama-olcer` [SEN1] · `juri-uyesi` kipi [MİM] · `ozet-eslestirici` [KUR] | **`ozet-eslestirici`** (opus, kör) | İ5 |
| Seyirci ajanı | `habersiz-seyirci` · `kurgu-seyircisi` [KUR] | **`habersiz-seyirci`** (5 kip) | İ14 |
| Hikâye yazarı | `senarist` [SEN1] · `hikaye-yazari` [MİM] · `hikaye-mimari` [ÜRE] | **`hikaye-yazari`** | [MİM]'in erişim politikasında ve kadrosunda bu ad var; mimar ile yazar ayrı roller |
| Konu ve proje kararları | `konu-analisti` [SEN1] · `yapimci` [MİM] | **`yapimci`** (kipler: `konu`, `doktor`) | Aynı iş; Ç-10 ölçütü |
| Hikâye doktoru | `hikaye-doktoru` [SEN1] · "yapısal kurtarma (yapımcı + yazar)" [MİM] S-3 | **`yapimci` doktor kipi** (yeni örnek) | Ayrı dosya sahibi değil, yazmaz; ajan sayısı azalır |
| Evren hikâye kaydı | `evren-arsivcisi` [SEN1] · "EVREN yalnız `evren.py` yazar" [MİM] | **`hikaye-yazari` evren kipi** taslak yazar → `evren.py` doğrular ve yazar | Hikâyeyi en iyi bilen yazar; makine sahipliği korunur |
| Ad maskeleme | `hitaplar[]` [SEN1] · `etiket_anonim`, `takma_adlar` [KUR] | **`maske: {etiket_anonim_en, takma_adlar[]}`** (karakter kartında) | Tek kod: `kor_paket.py` |
| Replik tonu | `ton` [SEN1] · `teslim` [YÖN] · `seviye` + `ton_fiili` [SES] | Hikâye **`teslim`** yazar ([YÖN] §5.5 sözlüğü); `ton_fiili_en` ve `seviye` betikle türetilir | Tek kaynak; [SES] B6 seviyeleri bu sözlükten çıkar |
| Ses tarifi | `ses_tarifi_en` [SEN1] · `veo_ses_tarifi` [SES] | Hikâye **`ses_karakteri`** (Türkçe, serbest) yazar; Veo dizesini `ses-kadrocusu` yazar | [YÖN] §8.3-7 ve [SES] A1: Veo dizesinde yaş sözcüğü yok; benim örneğimdeki "early 30s" hatalıydı |
| Parti | `parti` = üretim partisi, `hikaye_partisi` ayrı [YÖN] · `parti` = 1–3, `uretim_blogu` = 20 [MİM][ÜRE][KUR] | Hikâye belgesinde sahne düzeyinde **`hikaye_partisi`** (P1–P3). Plan düzeyinde çoğunluğun önerisi (`parti` 1–3 + `uretim_blogu`) | Hangi tercih seçilirse seçilsin hikâye alanı belirsiz kalmaz (BK §8 #14) |
| Kostüm varyantı kimliği | `sera_k1_pelerin` [SEN1] · `k1`, `k1_yirtik` karakter kapsamlı [GÖR] | **[GÖR] biçimi**; hikâye `kostum_degisimleri[]` olayını yazar, tarifi kart tasarımcısı aynı kimliğe yazar | Tek kimlik, iki sahip, iki ayrı alan |
| Klasörler | `_HIKAYE_ODASI/`, `_RAPOR/` [SEN1][ÜRE][SES][GÖR][KUR] ve mevcut kod/ajanlar · `20_HIKAYE/`, `10_PROJE/`, `RAPORLAR/` [MİM], ZN | **`_HIKAYE_ODASI/`** ve **`_RAPOR/`**; [MİM]'in `_GOREV/` klasörü aynen kalır, görevin `tasima` alanı hedefi `_HIKAYE_ODASI/` olur | Çoğunluk + mevcut kod (`film.py` `_RAPOR`) + mevcut ajan taslakları; ZN düzeltilir |
| Seri kütüphanesi kökü | `EVREN/<SERI>/` [MİM][YÖN][GÖR][SES][SEN1] · `KUTUPHANE/<SERI>/` [ÜRE] | **`EVREN/<SERI>/`** (yol `FILM_AYAR.json → evren_kok`) | Çoğunluk |
| Eşik dosyası | `hikaye_esikleri.json` [SEN1] · `hat_esikleri.json` [ÜRE] · `sureklilik_esikleri.json` [GÖR] · `ritim_esikleri.json`'a ekleme [YÖN][KUR] | Ayrı dosyalar kalabilir; **ortak yükleyici `esikler.py`** hepsini birleştirir, aynı anahtar iki dosyada geçerse HATA verir | Tek değer, tek yer; ZN "çelişkide JSON geçerli" kuralı sürer |
| Kopukluk konumu | `sahne` (kâğıt) · `plan` (plan, izleme) | `konum: {sahne, plan?, zaman}` | Tek seyirci şeması, her kipte |
| Bulgu kök nedeni | [KUR] §5.6 sözlüğü | Aynı sözlük + hikâye satırına `bilgi_eksik`, `motivasyon_belirsiz`, `bilgi_durumu_ihlali`, `kanon_ihlali`, `ad_karisik` eklenir | §2.4 yönlendirmesi bu sözlükle çalışır |

### 2.2 Aşama sırası ve kodlar
Dışarıya karşı aşama kodu olarak [MİM]'in A-kodlarını kullanıyorum. H-adımları hikâye odasının iç alt adımları ve şablon adları olarak kalır.

| Hikâye adımı | [MİM] kodu | [ÜRE] kodu | Görev türü | Ortam |
|---|---|---|---|---|
| H0 konu | A00 | K01 | AC + betik | bulut/yerel |
| H1 konu kartı (+ süre, eksenler) | A01 | K02 | ajan `yapimci` + betik | bulut/yerel |
| H2 brifing | A02 | K02 | betik | bulut/yerel |
| H3–H4 öneriler + denetim | A03 | K03 | ajan ×4 + betik | bulut/yerel |
| H5–H6 jüri + seçim | A04 | K03 | ajan ×5 + betik | bulut/yerel |
| H7–H10 yapı, senaryo, oyuncu/diyalog, makine denetimi | A05 | K04 | ajan + betik | bulut/yerel |
| H11–H12 kâğıt seyirci + ilk 2 dk | A06 | K05 | ajan + betik | bulut/yerel |
| H13 kilit ve devir | A06 sonu | K05 sonu | betik | bulut/yerel |
| H15 kilit sonrası dar değişiklik | A07d/A12/A16 dönüşleri | K11/V08/M04 dönüşleri | ajan + betik | bulut/yerel |
| H14 evren kaydı | A18 | S02 | ajan + betik | bulut/yerel |

**Sıra:** H13 kilidinden sonra yönetmen (A07) başlar. Plan düzeyi kâğıt seyirci ([MİM] A07d, [ÜRE] K11) aynı `anahtar_olgular`
listesiyle ve `ekranda_bilgi` verilmeden çalışır. Bu kapıdan, animatikten ve kurgudan gelen `hikaye` kök nedenli bulgular
H15 yoluyla hikâye odasına döner.

### 2.3 Sorumluluk sınırları

| Konu | Tek sahibi | Diğerleri ne yapabilir | Değişiklik yolu |
|---|---|---|---|
| Replik metni (kelimeler) | `hikaye-yazari` | Okur | Kelime değişikliği isteği → yazar → diyalog-editörü (+ gerekirse oyuncu) → H10 |
| Replik bölme (kelime değişmeden), ekran dışına taşıma, J/L | yönetmen (plan), kurgucu (kurgu) | Serbest; `replik_bolundu` kaydı | Kayıt yeterli |
| Sahne listesi, sırası, sınırı | `hikaye-yazari` | Yönetmen mekân/zaman kırılımında `S07a/b` böler | Birleştirme, silme, sıra → `sahne_degisiklik_istegi` |
| Sahne hedef süresi | `hikaye-yazari` (hedef) · yönetmen (plan toplamı) | Yönetmen ±%20 (tahmin) | Daha büyük sapma → istek |
| `sahne_degeri`, `vurus`, `hedef_duygu`, `merak_*`, `kurulum`, `ironi`, `risk` | `hikaye-yazari` | Yönetmen plan düzeyinde yoğunluğu ±2 inceltir; her kimlik tam olarak bir planda taşınır | İstek |
| Sahne uç olguları (mekân, kostüm, görünüm, nesne kimde/nerede/durum) | `hikaye-yazari` | Yönetmen inceltir (işaret, el, poz, ışık), çelişemez | İstek |
| Plan durumu, eylem zinciri, kroki | yönetmen | Hikâye okur | — |
| Dünya durumu defteri (fiziksel) | betik (süreklilik kuralları) | — | — |
| Bilgi durumu (kim neyi biliyor) | `hikaye-yazari` yazar, betik izler | Oyuncu denetler | — |
| Görünüşün hikâyeye bağlı öğesi | `hikaye-yazari` | Kart tasarımcısı kilitli kabul eder | İstek |
| Görünüşün diğer öğeleri, kimlik dizesi | kart tasarımcısı | Hikâye okur | — |
| Ad, `ad_telaffuz` önerisi | `hikaye-yazari` | `ses-kadrocusu` TTS + ASR ile doğrular; Flow istemine `veo_metin` yazar | Doğrulama geçmezse ad değişikliği isteği (kilitten önce) |
| Veo ses dizesi, ses seçimi | `ses-kadrocusu` | Hikâye `ses_karakteri` girdisini verir | — |
| Başlık adayları, kapak imgesi, vaat sözleşmesi, bölüm adları, Short adayları | `hikaye-yazari` | Yayın seçer, zamanlar, doğrular | Yeni başlık → `vaat-denetim` |
| Dönem, evren kuralları, hikâye NE YOK listesi, kanon, seri soruları | `hikaye-yazari` (taslak) → `evren.py` | Görüntü kendi görsel NE YOK listesini ekler | — |
| Stil eki, palet, kumaş, gerçekçilik ekleri | görüntü | Hikâye renk/ton duygusunu brifingde söyler | — |
| `IZLEYICI_OZETI.md` | betik (kurgu seyircisi özetlerinden) | Yalnız "dönen seyirci" okur | — |
| Hikâye etiketli dersler | betik kaydeder; terfi ders sahibinde | Hikâye odası okur (brifinge girer) | — |

### 2.4 Bulgu yönlendirmesi (kök neden → sahip)
Animatik, plan seyircisi, kurgu seyircisi ve kullanıcı notu bulguları önce `hikaye_odasi.py bulgu-sinifla` betiğinden geçer. Betiğin kuralı:
1. Bulguda kök neden yoksa betik, seyircinin cümlesinden ve konumundan ilgili `anahtar_olgu`, `kurulum`, `merak` ya da karakter kimliğini bulur.
   Bulamazsa bulgu `kurgucu`ya gider; kurgucu [KUR] §5.6 sözlüğüyle kök neden yazar.
2. **Olgu `HIKAYE.json`'da yok** (hiçbir sahnenin EKRAN bloğunda ya da replikte geçmiyor) → kök neden `bilgi_eksik` → **`hikaye-yazari`** (H15).
3. **Olgu hikâyede var, ama ilgili sahnenin planlarında `tasidigi`/`ekranda_bilgi` karşılığı yok** → `hikaye_adimi_ekranda_yok` → **yönetmen**.
4. **Olgu hem hikâyede hem planda var** → üretim ya da kurgu sorunudur: görüntü kesildi, replik duyulmadı, kare bozuk → kurgucu,
   süreklilik ya da ses (kendi kök nedenleriyle).
5. Karakter bilgisi: "bunu nereden biliyor" → `bilgi_durumu_ihlali` → yazar. "Bu kim" → betik önce ad zamanını ölçer (Z1 #23);
   ad zamanında geçiyorsa görünüş ayrışması → görüntü, değilse → yazar.

| Kök neden | Sahip | Not |
|---|---|---|
| `bilgi_eksik`, `kurulum_yok`, `ad_gec`, `risk_belirsiz`, `duygu_hak_edilmedi`, `motivasyon_belirsiz`, `bilgi_durumu_ihlali`, `kanon_ihlali`, `ad_karisik` | `hikaye-yazari` | H15 dar değişiklik; önce 0 kredili basamaklar |
| `hikaye_adimi_ekranda_yok`, `konum_plani_gec`, `mekan_belirsiz`, `olcek_sicramasi`, `eksen_180`, `bakis`, `ekran_yonu` | yönetmen | [KUR] §5.6 |
| `olu_sure`, `gec_giris`, `uzun_plan`, `bilgisiz_uzun`, `ritim_tekduze`, `diyalog_kopuk`, `konusan_belirsiz`, … | kurgucu | [KUR] §5.6 |
| `nesne_zipladi`, `karakter_kayboldu`, `yuz_degisti`, `isik_zipladi` | süreklilik | [GÖR] |
| `ambiyans_zipladi`, `seviye_zipladi`, ses/dudak | ses | [SES] |

**Yeni sahne / bağlayıcı plan isteği ([KUR] `yeni_plan_iste`):**
- Gereksinim yeni replik ya da yeni hikâye olayı içeriyorsa → yazar sahne ekini yazar, yönetmen planlar.
- Yalnız görsel köprüyse (kapıdan masaya yürür, aynı bilgi) → doğrudan yönetmene gider; hikâye değişmez.

### 2.5 Bütçe ve film süresi (ZN §2.6 ↔ [ÜRE] C2, [KUR] D1)
- **Çelişki:** ZN §2.6 "Bütçe yetmezse planlar uzatılmaz, film kısaltılır: 30 dk ≈ 370 plan ≈ 305 klip ≈ 4.400 kredi" diyor.
  [ÜRE] C2 ve [KUR] D1 "hat bekler, makine kısaltmaz" diyor.
- **Çözüm:** Süre bir yaratıcı karardır ve **yazımdan önce** H1'de verilir. Yazılmış hikâyeyi bütçe için kısaltmak hikâyeyi kesmek demektir
  (kesin karar 6); kilitten sonra makine kısaltmaz, hat bekler.
- **H1'deki hesap** (ZN §2.6 oranıyla, hesap):
  - Klip sayısı ≈ 0,169 × süre (sn). Kaynak: 40 dk'da 405 klip, 30 dk'da 305 klip.
  - Kredi ≈ klip × 12 × (1 + 0,30). Kaynaklar: RE `kredi_klip_720p`; [ÜRE] C1 kapı payı 0,30, ilk film için (tahmin).
  - Örnekler: 30 dk ≈ 4.750 kredi · 40 dk ≈ 6.320 kredi · 45 dk ≈ 7.120 kredi.
- **Karar kuralı:**
  - Bakiye ya da tavan biliniyorsa (`FILM_AYAR.json → butce`, son Memmet okuması), [1800, 2700] sn içinde bütçeye sığan en uzun süre hikâyenin
    doğal süresi için **üst sınır** olur. Hedef RE `film_sure_hedef_sn` = 2400'dür.
  - Bakiye bilinmiyorsa (bulut oturumu) hedef 2400 sn olur ve varsayım defterine yazılır.
  - 30 dk bile sığmıyorsa hikâye 30 dk yazılır, kullanıcıya H1'de **bilgi** verilir ("Bu film ≈ 4.750 kredi isteyecek; hesapta X var")
    ve hat video kapısında kredi yüklenmesini bekler.
- **Dolgu yasağı sürer** (ZN §2.5): hedef bir tavandır, doldurulacak bir süre değildir. Yazar yapı aşamasında hedefi ±5 dk içinde belirler.
- ZN §2.6'daki cümle şöyle güncellenmeli: "Bütçe yetmezse süre hikâye yazılmadan önce seçilir; yazılmış film kısaltılmaz."

### 2.6 Hikâye kapısı tükenirse
[MİM] S-3, [ÜRE] C11 ve [KUR] K5'i birleştiren öneri (ayrıntısı §4.2 H11'de):
1. Tur 1–4 normal.
2. Tur 3'te GENEL medyanın iyileşmesi 0,5'ten azsa `yapimci` doktor kipi hemen devreye girer.
3. 4. tur sonunda KRİTİK 0 ve GENEL ≥ 7,5 ise doktor + 2 yapısal tur yapılır; değilse doğrudan 4. adıma geçilir.
4. Jürinin ikinci önerisiyle H7'den yeniden başlanır (en çok 4 tur, doktor kuralı aynı).
5. Hâlâ geçmezse DUR: engel bildirimi (en iyi sürüm `EN_IYI`, en düşük 3 ölçüt, öneriler). Bu bir soru değildir; hat bekler.
   Kullanıcı kendi isteğiyle yeni bir konu yazar ya da "bu hâliyle devam" der. İkincisi KARAR_DEFTERI'ne kullanıcı kararı olarak yazılır.
- Bayraklı otomatik devam **yoktur** (İ10).

### 2.7 Evren kütüphanesi düzeni ve sahipliği
```
EVREN/<SERI>/
  evren.json                 seri adı, sürüm, bağlı filmler                      (evren.py)
  hikaye.json                dönem, kurallar, hikâye NE YOK listesi, kanon,
                             seri soruları, başlık geçmişi, ad sözlüğü           (hikâye taslağı → evren.py)
  dunya.json                 stil eki, palet, kumaş, gerçekçilik ekleri,
                             görsel NE YOK listesi; dönemi hikaye.json'dan okur  (görüntü → evren.py)
  karakterler/<id>/
     hikaye.json             rol, yay geçmişi, bildikleri, ilişkiler, konuşma tarzı,
                             maske, ses_karakteri, hikâyeye bağlı görünüş        (hikâye taslağı → evren.py)
     karakter.json + kartlar görsel kimlik ([GÖR] §5.2)
     ses.json + banka        ses kimliği ([SES] §5.2; [SES]'in EVREN/SESLER/<id>/ önerisi yerine bu klasör önerilir)
  mekanlar/<id>/             mekan.json ([GÖR]), kroki ([YÖN]), ses.json ([SES])
  DURUM_SON.json             son filmin fiziksel bitiş durumu ([GÖR]); hikâye kaydı kostüm/yara yazmaz, buraya bakar
  IZLEYICI_OZETI.md          kurgu seyircisi özetlerinden (betik)
```
- **NE YOK taraması:** `evren.py ne_yok_kelimeleri()`, `hikaye.json` ve `dunya.json` listelerinin birleşimini döndürür;
  `istem_denetim` ve `senaryo-denetim` aynı işlevi çağırır.

### 2.8 Küçük çakışmalar
- **Konu sorusu ↔ soru kancası:** [MİM] K-8 `soru_kapisi` "ister misin" kalıbını yakalıyor. Benim konu sorumdaki "İstersen 'sen seç' yaz"
  ifadesi beyaz listeye alınmalı (aktif film yokken, yalnız konu sorusu).
- **Ders ekleme yolu:** [MİM] K-7b `SubagentStart` kancası rol derslerini ajana ekliyor. Hikâye rollerinde dersler brifingin içinde,
  betikle basılmış olarak gelir (dört mimar aynı metni görsün, sha1 tutsun). Kanca hikâye rollerine **ayrıca** ders eklemez.
- **Ders terfisi:** [ÜRE] §5.8 "≥ 3 kayıt ve ≥ 2 film (ya da tek filmde ≥ 5)" diyor. Hikâye etiketli dersler için **en az 2 farklı film**
  şartını koruyorum, çünkü hikâye bulguları filme özgüdür. Bu, [ÜRE] korkuluklarının içinde kalan daha sıkı bir alt kuraldır.

---

## 3. Diğerlerinden kabul edip kendi önerime kattıklarım

| Kaynak | Kabul ettiğim | Önerimdeki yeri |
|---|---|---|
| [MİM] §2.0, §5.2–5.3 | Görev defteri (`film.py sonraki/basla/bitir`), `GOREV.json`, betiğin şablondan doldurduğu `ISTEM.md`, `GIRDI/` ve `CIKTI/`, paralel grup, `tasima` | §4.2, §4.4; tur 1'deki `metin` sağlayıcısı ve `GOREV_<asama>.md` kaldırıldı |
| [MİM] K-3, §5.7 | Ayar dosyası düzeyinde `erisim_kapisi.py` kancası, rol politikası, "ilk okumada görev bağlama" | Tur 1'deki ajan içi `seyirci_bekci.py` kancası kaldırıldı |
| [MİM] §3.1 | Ana Claude içerik üretmez ve puan vermez; düz yapı; kör ajanlarda `omitClaudeMd: true`; `memory:` alanı yok; dönüş ≤ 5 satır; önce başlıkları yaz, bölüm bölüm doldur; ajana sabit sayı yazılmaz (RE'den basılır) | §4.3 |
| [MİM] §2.3 | Değerlendiricinin yarım işi sıfırdan yapılır, yazarınki devam ettirilir; SubagentStop doğrulaması (≤ 2 düzeltme) | §4.3, §4.4 |
| [MİM] §5.8, K-13 | Kör paket beyaz listesi ve `kor_paket.py`; tur 1'deki `ekran_metni.py` buna katıldı (hikâye kipi + ad maskeleme benim tanımım) | §4.6 |
| [MİM] Ç-2, [YÖN] §3.4 | `ekranda_bilgi` seyirciye verilmez | İ2, §4.2 H11 |
| [MİM] A01 | `yapimci` ajanı; mimar tonlarını yapımcı atar; "karar — neden — yanlışsa maliyeti" defteri | §4.2 H1 |
| [MİM] §2.2 #4 | Aynı tur içinde aynı seyircinin SendMessage ile sürdürülmesi | Kâğıtta aşamalı okuma (İ6) |
| [MİM] §5.11, [ÜRE] §5.3 | Çıktıda `_sahip/_surum` üst bilgisi ve `_uretim` zarfı (girdi imzası) | §4.5.2 |
| [MİM] K-8 | `soru_kapisi` Stop kancası (karar 1'in makinedeki bekçisi) | §4.8.1 |
| [KUR] §5.2–5.4 | Parti başına 8–12 anahtar olgu; `etiket_anonim`, `takma_adlar`; ad sızdırmama kuralı | §4.5.2, §4.6 |
| [KUR] §5.3, §5.9 | Seyirci JSON şeması; `kahraman_ne_kaybedebilir`; ilgi eğrisi; "kısmen = 0,5"; KRİTİK birleştirme; tek seyircinin KRİTİK'inin kanıtla geçersiz sayılması | §4.5.6, §4.2 H11 |
| [KUR] §5.6 | Kök neden sözlüğü | §2.4 |
| [KUR] D11 | Kesme turunun animatikte de yapılması; her kesmeden sonra Z1 kurulum denetimi | §4.8.3 (a) |
| [YÖN] §5.4 | Durum nesnesi yapısı (`varliklar`, `nesneler`; sağ/sol karakterin kendisine göre) → hikâye uçları bu yapının alt kümesi | §4.5.2 |
| [YÖN] §5.5 | `teslim` sözlüğü | §4.5.2 |
| [YÖN] §8.3-7, [SES] A1 | Veo ses dizesinde yaş sözcüğü yok; dizeyi `ses-kadrocusu` yazar | §2.1 |
| [YÖN] §3.2 | `replik_degisti` mekanizması (onayı benim tanımımla) | §2.3 |
| [GÖR] §5.2, §9.2 | `ayirt_edici` (siluet/renk/saç), `bilincli_benzerlik`, karakter kapsamlı kostüm kimliği, yaratıkta "baby/little/young" yerine boy benzetmesi, `DURUM_SON.json` | §4.5, §2.7 |
| [SES] A1–A2, §8.2 (a) | Ad telaffuzunun TTS + ASR ile doğrulanması (ad WER = 0); `veo_metin`; ses tanıtım kuralı (ekran dışı ses ancak karakter önce ekranda konuştuysa); işitsel döküm ve "ekran dışı sesi kime ait sandın?" sorusu; kadroda ses ayrışması | §4.2 H8, H11; §4.7 |
| [ÜRE] §5.8, §7.4 | Ders defteri korkulukları (kanıtsız kural yok, tek filmden genelleme yok) | §4.8.3 (e) |
| [ÜRE] §6.4 | Testlerde `kaset` sağlayıcısı (kayıtlı ajan çıktıları), bulutta kâğıt aşamaları, `input()` yalnız `yeni --konu` yolunda | §4.6 |
| [ÜRE] K11, [MİM] A07d | Plan düzeyi kâğıt seyirci (aynı `anahtar_olgular`, `ekranda_bilgi`siz) | §2.2, §4.8.3 (a) |
| [ÜRE] C2, [KUR] D1 | Yazılmış film bütçe için kısaltılmaz | §2.5 |

**Geri çektiklerim:** `metin` sağlayıcısı ve `GOREV_<asama>.md` el sıkışması; ajan frontmatter'ında `hooks`; `ses_tarifi_en` alanı;
hikâyede kroki yönleri; `konu-analisti`, `senarist`, `anlama-olcer`, `hikaye-doktoru`, `evren-arsivcisi` adları; `seyirci_bekci.py` ve `ekran_metni.py`
(işlevleri [MİM]'in araçlarına taşındı); ana Claude'un brifing yazması.

---

## 4. REVİZE NİHAİ ÖNERİM

**Tek cümlelik öz:**
1. Kullanıcının tek cümlelik konusunu `yapimci` bir konu kartına çevirir; süre bütçeye göre yazımdan önce seçilir.
2. Betik brifingi kurar; 4 mimar aynı konuyu zorla farklı motorlarla önerir.
3. Kör 5 jüriden betik bir kazanan çıkarır.
4. Kazanan yazar 3 parti × 8 başlıklık yapıyı ve sahne sahne ekran metnini yazar.
5. Oyuncu, diyalog ve makine kapılarından sonra metin, adları maskeli ve sırayla okuyan 3 özetsiz habersiz seyirciden medyan 8/10 alana
   kadar aynı yazar tarafından düzeltilir.
6. İlk 2 dakika A/B testinden geçen hikâye kilitlenir ve yönetmene sahne sözleşmesi olarak devredilir. Hikâyenin kalıcı kısmı seri evrenine yazılır.

### 4.1 Alanımın hedefi ve başarı ölçütü (sayılarla)

#### 4.1.1 Alanım
- **Benim:** konudan brifinge geçiş; öneri çeşitliliği (eksenler, mimar sayısı); jüri ve seçim kuralı; 3 parti × 8 başlık; sahne sahne
  ekran metni ve İngilizce replikler (metnin tek sahibi); kâğıt seyirci döngüsü ve revizyonlar; oyuncu ve diyalog denetimi;
  başlık, kapak vaadi, bölüm adı, Short adayı ve seri kancasının hikâyeye gömülmesi; seri evreninin hikâye tarafı (karakter yayları,
  kurallar, NE YOK, kanon, bilgi durumu, ad sözlüğü); kilitten sonra hikâye kaynaklı dar değişiklikler.
- **Benim değil (yalnız sözleşmesini yazarım):** plan, eylem zinciri, kroki ve istem (yönetmen); kartlar, görünüş tarifi ve görsel
  denetim (görüntü); ses yolu, ses seçimi ve müzik (ses); kurgu ve kesme (kurgucu); görev defteri ve kancalar (mimari);
  bütçe ve sağlayıcı (üretim); yayın paketinin üretimi.

#### 4.1.2 Başarı ölçütleri (kapı: hepsi geçmeden yönetmene devir yok)

| # | Ölçüt | Eşik | Kaynak |
|---|---|---|---|
| S1 | Kâğıt seyirci GENEL puanı (3 özetsiz seyircinin medyanı; parti başına ve film) | ≥ 8 | RE `seyirci_genel_esik`, ZN §7.3 |
| S2 | Hiçbir ölçütün medyanı (anlaşılırlık, akıcılık, merak, duygu, ritim, ilk30) | ≥ 7 (anlaşılırlık, akıcılık, merak, ilk30 için hedef ≥ 8) | RE `seyirci_olcut_min`, `seyirci_olcut_hedef` |
| S3 | KRİTİK / ORTA kopukluk (parti başına, birleştirilmiş) | 0 / ≤ 3 | RE `kopukluk_kritik_max`, `kopukluk_orta_max_parti` |
| S4 | Özet eşleşmesi (`anahtar_olgular`; kısmen = 0,5), parti başına medyan | ≥ 0,80 | RE `ozet_eslesme_min`; kısmen ağırlığı [KUR] (tahmin) |
| S5 | İlk 2 dk testi (seçilen sürüm, başlık + kapakla) | 3/3 "evet" | RE `ilk2dk_devam_evet_min`, ZN §7.2.2 |
| S6 | Hikâye düzeyi Z1 (bilgi) ve Z2 (duygu) maddelerinde HATA | 0 | ZN §6.2 |
| S7 | Her parti tek cümleyle savunulur; her sahnede `sahne_degeri.bas ≠ son` | %100 | ZN §7.2.3–4 |
| S8 | Kâğıt seyirci turu | normal ≤ 4; merdivenle en çok 10 (§4.2 H11) | RE `kagit_tur_max`; merdiven (tahmin) |
| S9 | Jüride kazananın ölçüt ortalaması | ≥ 8,0 (tahmin) | EMBERFALL 420/500 = 8,4 (YR A3) |
| S10 | Vaat sözleşmesi: başlığın her öğesi ve kapak imgesi ekranda; vaat imgesi | %100; ≤ 120 sn | RE `vaat_imgesi_max_sn`, BK 1.7.6 |
| S11 | Oyuncu denetimi: karakter dışı ya da bilmediği şeyi söyleyen replik | 0 KRİTİK | ZN §7.2.5, AR1 A1 |
| S12 | Toplam replik kelimesi (40 dk için; süreyle oranlanır) | 2.100–2.600 | ZN §2.6 |
| S13 | Sahne sayısı / sahne süresi | 45–55 (40 dk) / ≤ 180 sn | ZN §2.4, RE `sahne_max_sn` |
| S14 | Replik filtre ve klip uyumu (yasak kelime, ≤ 16 kelime/8 sn) | 0 HATA | DR, RE `replik_max_kelime_8sn`, `istem_denetim.py` |
| S15 | Her replikte `tasidigi` dolu; her `anahtar_olgu`nun en az bir `ekranda` kaynağı var | %100 | bu öneri (İ8) |
| S16 | Tek seyircinin KRİTİK'inin geçersiz sayılması yalnız betikle doğrulanmış kanıtla | %100 kanıtlı | [KUR] §5.9 kuralının kâğıt uyarlaması |

#### 4.1.3 Alt akış ölçütleri (hikâye odasının gecikmeli karnesi; kapı değil, ders defterine yazılır)
- Plan seyircisinde, animatikte ve kurguda `bilgi_eksik` ve diğer hikâye kök nedenli KRİTİK sayısı 0 olmalı. Hikâyeye geri dönüş
  en çok 1 kez (tahmin). Geçmiş: B2 ilk taslakta "bilmesem ne izledim derim" (H/kurgu-izleme-denetimi); B1'de babanın adı 84. çekimde (YR A8).
- Kâğıt → animatik → kurgu GENEL farkı her filmde karneye yazılır. Kâğıt puanı kurgudan sistematik olarak 1 puandan fazla yüksekse
  kâğıt eşiği yükseltilir (R1).
- Yayın sonrası izlenme, ilk 30 sn tutma ve ortalama izlenme süresi yalnız kayıt olarak tutulur. Bugün tutma verisi yok (BK 1.8.5).
  Kıyas tabanı: B1 ≈ 671 izlenme (OB).

#### 4.1.4 Emek bütçesi (kredi değil)
Hikâye odası Flow ya da AI84 kredisi harcamaz (ZN K8). Yalnız Claude kullanımı harcar.
- Ajan örneği tahmini (ilk film, tahmin):

| Adım | Örnek sayısı |
|---|---|
| Yapımcı | 1 |
| Mimar | 4 (+ 0–2 düzeltme) |
| Jüri | 5 (+ 0–5 ek tur) |
| Yazar (yapı + 3 parti, aynı örnek sürdürülür) | 1–2 |
| Oyuncu + diyalog editörü (tur 1) | ≤ 9 |
| Kâğıt seyirci turu × 1–4 (3 seyirci + 3 eşleştirici; değişen karakter için oyuncu) | ≈ 7–10 / tur |
| İlk 2 dk testi | 6 (+ 3 yeniden) |
| Doktor | 0–2 |
| Evren | 1 |
| **Toplam** | **≈ 40–75** |

- [ÜRE] §3.5'teki ≈ 18–26 tahmini hikâye odası için düşük, [MİM]'in film toplamı (≈ 350–450) ile uyumlu.
- Kesin karar 6 gereği bu sayı kısılmaz. Kullanım sınırına takılırsa iş dosyalardan kaldığı yerden sürer ([MİM] §2.3).

### 4.2 Aşama aşama süreç
Her adım görev defterinde bir ya da daha çok görevdir ([MİM] §2.0). Çalışma klasörü `<film>/_HIKAYE_ODASI/`. Ajan çıktısı önce
`_GOREV/<id>/CIKTI/`'ya yazılır, sonra betik `tasima` alanıyla buraya kopyalar.

**Kim sütunu:** **B** = betik (`film.py` görevi; içerikte `hikaye_odasi.py`, `kor_paket.py`, `evren.py`) · **A:<ajan>** = alt ajan ·
**AC** = ana Claude (yalnız dağıtır ve `film.py`'nin metnini iletir; içerik yazmaz, puan vermez).

```
H0 konu ─► H1 konu kartı (+süre, eksenler) ─► H2 brifing ─► H3 öneriler (3 paralel + bonus) ─► H4 öneri denetimi
 ─► H5 jüri (5 paralel) ─► H6 seçim ─► H7 yapı (3 parti × 8 başlık) ─► H8 senaryo v1 (+ A/B soğuk açılış)
 ─► H9 oyuncu + diyalog ─► H10 senaryo denetimi ─► H11 kâğıt seyirci döngüsü ║ H12 ilk 2 dk A/B (tur 1 ile paralel)
 ─► H13 kilit ve devir ─► [yönetmen … kurgu] ─► H15 dar değişiklik dönüşleri ─► H14 evren kaydı
```

#### H0 — Konu al (kullanıcıya sorulan tek soru)
- **Girdi:** kullanıcının mesajı; `film.py ozet` → "aktif film yok".
- **İş:**
  - Mesajda konu varsa soru sorulmaz.
  - Yoksa AC yalnız şunu sorar:
    > "Filmin konusu ne olsun? Bir cümle yeter (ör. *ejderha yavrusunu saklayan avcı kadın*). İstersen *sen seç* yaz."
  - Cevap gelince `film.py yeni --konu "<aynen>"` çalışır.
  - Kullanıcının konuyla birlikte söylediği istekler ("komik olsun", "uzayda geçsin") aynen kaydedilir; H1'de `kesin_istekler` olur.
  - Belirsizlikte soru sorulmaz; H1'de varsayım yapılır.
- **Çıktı:** `_HIKAYE_ODASI/00_KONU.md` (kullanıcının sözü aynen + tarih), `FILM_DURUM.json`.
- **Geçme şartı:** dosya boş değil. `soru_kapisi` aynı turda başka bir karar sorusuna izin vermez ([MİM] K-8; konu sorusu beyaz listede).
- **Kim:** AC + B.

#### H1 — Konu kartı (konudan karara)
- **Girdi** (betik GIRDI'ye kopyalar):
  - `00_KONU.md`.
  - Kanal kararları (`AYARLAR/KANAL_KARARLARI.json`; yoksa `KARARLAR.md`).
  - BK §1–2 dilimi (kanallar, süre verisi, kanca aileleri).
  - Evren dizini (yalnız seri adları ve özetleri).
  - `DERSLER` (`hikaye` etiketli, `dogrulandi`).
  - `butce_bilgisi.json`: betik yazar. İçinde Flow bakiyesi ya da tavanı ve kaynağı, ya da "bilinmiyor" ve ortam bilgisi bulunur.
- **İş** (A:`yapimci`, kip `konu`):
  1. **Seri tespiti:** konu kayıtlı bir evreni ya da karakteri anıyorsa `devam`, anmıyorsa `yeni` (varsayılan). EMBERFALL kapandı ve
     izlenme almadı (OB); açıkça anılmadıkça geri çağrılmaz.
  2. **Tür ve kanca ailesi** (aşağıdaki tablo): birincil ve gerekirse ikincil.
  3. **Vaat imgesi taslağı:** kapakta görülecek tek kare (KR kalıbı: insan + yaratık aynı karede; BK 1.7).
  4. **Risk taraması ve dönüşüm:**
     - Küçükler filtresi: insan çocuk kahraman yetişkine çevrilir ya da çocuk yalnız dolaylı anlatılır; kullanıcıya bilgi notunda söylenir.
     - Şiddet ve kan.
     - Telif: "X gibi" konularda yalnız tür hissi alınır; ad, olay ve tasarım alınmaz.
     - Flow'da zayıf işler (kalabalık savaş, su altı, hızlı dövüş, ekranda okunacak yazı).
     - Anime tarzı (BK 1.9.2).
  5. **Süre kararı** (§2.5): `film_sure_hedef_sn` ve gerekçesi; bütçe biliniyorsa tahmini kredi.
  6. **Mimar eksenleri:**
     - Yeni seri: D (duygu), S (sır/ironi), E (eylem) + X (bonus).
     - Seri devamı: A (sadık), B (sürpriz), S (sır) + X (UH §1, BK 2.7).
     - Her eksen için konuya özgü bir motor cümlesi yazılır.
  7. **Varsayım defteri:** her belirsizlik için "karar — neden — yanlışsa maliyeti" (AR3 B6). Kayıtlar `film.py karar ekle` ile KARAR_DEFTERI'ne gider.
  8. **"Sen seç" modu:** kanca ailelerinden ve evrendeki boşluklardan 3 konu adayı yazılır. Her aday 4 ölçütle puanlanır (kanca gücü,
     tür talebi BK 1.2, üretilebilirlik, seri potansiyeli) ve en yükseği seçilir. Kullanıcıya sorulmaz; gerekçesiyle deftere yazılır.
- **Çıktı:** `01_KONU_KARTI.json` (§4.5.1), `01_VARSAYIMLAR.md`.
- **Geçme şartı** (B `konu-denetim`):
  - Şema geçerli; `kanca_ailesi` sözlükten.
  - Her riskin `cozum` alanı dolu; telif riski `yuksek` ise `donusum` alanı dolu.
  - Süre [1800, 2700] içinde ve gerekçeli.
  - Eksenler birbirinden farklı.
- **Kullanıcıya bilgi** (soru değil; `film.py ozet --kullanici`): konu yorumu, süre, dönüşüm varsa nedeni, bütçe biliniyorsa tahmini kredi.
- **Kim:** A:`yapimci` → B.

**Konu sinyali → kanca ailesi → mimar eksenleri** (kanca aileleri BK §2.1 ve AN T14–16'dan; eksen eşlemesi benim önerim):

| Konu sinyali | Kanca ailesi (kazanan örnek) | D (duygu) | S (sır) | E (eylem) |
|---|---|---|---|---|
| yaratık, ejderha, uzaylı, canavar | insan + yaratık bağı ("She Raised a Monster They Tried to Kill", 3,3M) | ebeveynlik | saklama, dramatik ironi | kaçış, takip |
| taht, krallık, kardeş, miras | ihanet ve taht (AGE OF KINGDOMS 12–14M) | aile yarası | komplo | kuşatma |
| asker, savaş, ordu | orduya karşı seçim ("He Chose the Alien Woman Over the Army") | sadakat ikilemi | emir ile vicdan | kurtarma |
| zayıf, alay, sürgün, köle | küçümsenen kahramanın dönüşü (manhwa mantığı [H], BK §2.2) | onur | gizli güç | sınav |
| kıyamet, dev yaratık, robot | hayatta kalma + bağ (Domain Filmes 10/18 ≥ 1M) | koruyan–korunan | felaketin sebebi | yolculuk |
| köy, aile, ahlak | ahlak draması (Dramaplace medyan 1,8M) | aile sırrı | iftira | yüzleşme |

#### H2 — Brifing
- **Girdi:** konu kartı, varsayımlar, kanal kararları, evren (devamsa), dersler, RE, `hikaye_esikleri.json`, filtre listesi (`istem_denetim`).
- **İş** (B `hikaye_odasi.py brifing`): her filmde aynı ve güncel kalıp bölümleri basılır.
  1. Kanal ve izleyici (BK §1).
  2. Kesin istekler: konu + kalıcı kanal imzaları (anlatıcı yok; İngilizce; 30–45 dk; yavru yaratık aşırı şirin, yetişkini heybetli;
     küçük güzel sahneler, BK §2.5, §2.10).
  3. Üretim sınırları (ZN K1–K9, filtre kelimeleri, NE YOK kuralı, ≤ 2 referans, tek konuşan, replik ≤ 16 kelime). Sayılar RE'den basılır.
  4. Ritim iskeleti (ZN §1.2–1.3, §4 eşikleri; "makine denetler" notu).
  5. Doğrulanmış hikâye dersleri (kanıtlarıyla).
  6. Teslim şablonu (H3'ün 10 başlığı ve dosya adları).
  7. **Konu yorumu:** yapımcının konu kartından yazdığı 1 paragraf.
  - Eksen satırı brifinge değil, her mimarın `ISTEM.md`'sine girer.
- **Çıktı:** `00_BRIFING.md` + sha1 kaydı.
- **Geçme şartı:** 7 bölüm var; filtre listesi `istem_denetim.FILTRE_KELIMELERI` ile aynı; 1.500–4.000 kelime (tahmin);
  dört mimar görevindeki brifing sha1'i aynı ([MİM] A02).
- **Kim:** B.

#### H3 — Öneriler: 4 mimar, zorla farklı motorlar
- **İş:**
  - A:`hikaye-mimari` ×3, eksen D, S ve E: aynı mesajda, paralel, birbirini okumaz (YR A2).
  - Sonra B `logline` ilk üç önerinin tek cümlelik loglinelarını çıkarır.
  - A:`hikaye-mimari` (eksen X, bonus "beni şaşırt") bu loglineları yalnız "kaçınılacak yollar" olarak alır. Bu, bağımsızlık kuralına
    bilinçli ve dar bir istisnadır: bonusun farklılığını garanti eder, metinler okunmaz.
- **10 başlık** (makinece aranır):
  1. Logline EN (≤ 35 kelime) + `logline_tr` + `ozet_tr` (3 cümle; kullanıcıya bilgi özeti için).
  2. Başlık adayları ×3 (kalıp `Kanca cümlesi | SERİ ADI | Full Movie 4K 2026`) + kapak imgesi (filmde olan tek kare).
  3. Karakterler (≤ 4 ana, ≤ 8 konuşan). Her biri için: istek, korku, yara, sır, yay (baş → son); görsel ayırt edici
     (hikâyeye bağlı öğeler işaretli); `ses_karakteri`; ad + telaffuz (§4.7 ad kuralları).
  4. Dönem, 3–5 evren kuralı, NE YOK listesi.
  5. 3 partinin tek cümlelik savunması + vuruş listesi (ZN §1.2 oranları).
  6. Soğuk açılış (ilk 30 sn, an an) ve ilk 2 dk.
  7. Merak soruları (≥ 8), kurulum → kullanım (≥ 5), parti başına ≥ 1 ironi.
  8. Parti başına ≥ 1 küçük güzel sahne.
  9. Seri kancası + sonraki filmin tek cümlelik tohumu.
  10. Üretilebilirlik: riskli sahneler ve çözümü; tekrar eden ve toplam mekân sayısı; kostüm değişimleri; konuşan sayısı.
- **Çıktı:** `02_oneri_<D|S|E|X>.md` + `.json` (makine alanları: başlıklar, karakter listesi, çeşitlilik dörtlüsü).
  Uzunluk 2.500–5.000 kelime (tahmin).
- **Kim:** A:`hikaye-mimari` ×4.

#### H4 — Öneri denetimi (mekanik)
- **İş** (B `oneri-denetim`):
  - 10 başlık var mı.
  - Başlık kalıbı ve ≤ 100 karakter.
  - Konuşan ≤ 8; ad kuralları.
  - Örnek repliklerde filtre ve NE YOK kelimesi.
  - **Çeşitlilik:** iki önerinin (kahraman tipi, çekirdek ilişki, doruk mekanizması, ana mekân) dörtlüsünden ≥ 3'ü aynıysa `BENZER` (tahmin).
- **Geçme şartı ve dönüş:**
  - HATA = 0. HATA'lı öneri aynı mimara döner (SendMessage; örnek kaybolduysa yeni örnek + önceki sürüm GIRDI'de), en çok 2 kez.
  - `BENZER` çıkarsa bonus dışındaki benzer öneri yeni bir eksenle 1 kez yeniden yazılır.
- **Çıktı:** `_RAPOR/ONERI_DENETIM.json`. **Kim:** B.

#### H5 — Jüri (kör, kullanıcı seçmez)
- **Girdi:** B `juri-paketi` önerileri anonimleştirir ("Öneri 1–4"; eksen bilgisi silinir) + brifing + `JURI_TABLOSU.md`.
- **İş:** 5 bağımsız jüri, paralel, aynı JSON şemasıyla:
  - A:`juri-uyesi` ×4: `ilk_kez_izleyen`, `youtube_stratejisti`, `tur_uzmani`, `duygu_elestirmeni`.
  - A:`uretilebilirlik-denetcisi` jüri kipinde ([MİM] A04).
  - **10 ölçüt × 1–10**, her puan gerekçeli: `kanca`, `netlik`, `merak`, `duygu`, `karakter`, `ozgunluk`, `yapi`, `uretilebilirlik`,
    `sureklilik_yuku` (az olan iyi), `seri`.
  - Her jüri ayrıca "çalınmaya değer" ve "mutlaka düzelt" listesi ve gerekirse `veto` yazar.
- **Çıktı:** `03_juri_<rol>.md` + `.json`. Son satır `OZET | 1: 7.4 | 2: 6.8 | … | SIRALAMA: 1>3>2>4`.
- **Geçme şartı:** 5 JSON şemaya uyuyor; her puanın gerekçesi var.

#### H6 — Seçim (deterministik)
- **İş** (B `juri-topla`):
  - Her öneri ve ölçüt için 5 jürinin **medyanı** alınır (puanlar gürültülü; ZN §7.2.10). Öneri puanı = medyanların ortalaması.
  - **Veto:** `uretilebilirlik` medyanı < 5 ya da çözümsüz KRİTİK → öneri elenir (tahmin).
  - **Birleştirme:** ilk iki öneri arasındaki fark ≤ 0,3 ise `BIRLESTIR` (tahmin; EMBERFALL 420/420 birleştirildi, YR A3–A4).
  - **Eşik altı:** kazanan < 8,0 ise kazanan yazar "mutlaka düzelt" maddeleriyle bir kez yeniden yazar, jüri yeniden puanlar (1 tur).
    Yine < 8,0 ise en iyisiyle devam edilir ve "eşik altı başladı" diye kaydedilir.
  - Seri adı (yeni seri) kazanan önerinin başlığından kesinleşir.
- **Çıktı:** `04_SECIM.json`; `04_KULLANICIYA_OZET.md`. Özeti betik `ozet_tr` ve `logline_tr` alanlarından kurar; AC aynen iletir (soru yok).
- **Kim:** B.

#### H7 — Yapı: 3 parti × 8 başlık
- **Girdi:** kazanan öneri (+ birleşecek öneri), `04_SECIM.json`, brifing, evren, ZN §1, §4, §2.3, RE.
- **Kim yazar:** A:`hikaye-yazari`. Mümkünse kazanan mimarın **aynı örneği** SendMessage ile sürdürülür ("revizyonu yazan yapar", YR §1.4).
  Örnek kaybolduysa yeni örnek açılır; GIRDI'de kazanan öneri ve `yazar_defteri.md` bulunur.
- **Film düzeyi alanlar:**
  - `duygu_haritasi` (ZN §1.3, süreye oranlı), `vuruslar` (ZN §1.2), `MERAK_DEFTERI`, `KURULUMLAR`, `IRONILER`.
  - `vaat_sozlesmesi`, `bolum_adlari` (≤ 8), `short_adaylari`, `seri_kancasi`.
  - `anahtar_olgular` (parti başına 8–12, tahmin), `mekanlar` (hikâye olgularıyla), `kostum_degisimleri`.
- **Her parti için 8 başlık** (UH §1; sınırları bu turda netleşti):
  1. **Amaç / duygu** + partinin tek cümlelik savunması ("P2'de [kahraman] [hedef] için [engel]le karşılaşır ve [kayıp]la biter.", ZN §7.2.3).
  2. **Vuruş vuruş olay akışı:** sahneler (S01…). Her biri için tip, hedef süre, `sahne_degeri {bas, son}`, vuruş, yoğunluk, hedef duygu.
  3. **Kim nerede durur (hikâye düzeyi):** sahne giriş ve çıkışında her adlı karakter için mekân + bölge (serbest etiket),
     hikâyeyi taşıyorsa poz, kostüm varyantı, görünüm (yara, kir). İşaret ve el ayrıntısı yönetmenindir.
  4. **Nesnelerin yolu:** her hikâye nesnesi kimde ya da nerede. Her el değiştirme ekranda bir olaydır. Sağ/sol yalnız hikâyeyi taşıyorsa yazılır.
  5. **Yalan/niyet ve bilgi durumu:** kim kime ne yalan söylüyor; seyirci bunu hangi araçla görür (ironi, tepki, ekleme, replik; ZN §4.4);
     sahne sahne kim neyi öğreniyor.
  6. **Mekânın hikâye olguları:** mekân listesi; hikâyenin gerektirdiği sabit öğeler; saat, hava; hikâye için önemli ışık kaynağı.
     Yön ve ölçü yazılmaz (kroki yönetmenindir).
  7. **Parti sonu kancası:** hangi merak sorusuyla biter (yoğunluk ≥ 8); sonraki parti ilk 20 sn'de nereden açılır.
  8. **Kaba plan tahmini** (ZN §2.6 oranı) ve riskli sahneler (çözüm önerisiyle: karşılıklı çekim, el/makro, siluet). Kesin plan sayısı yönetmenindir.
- **Çıktı:** `05_YAPI.md` + `05_YAPI.json`.
- **Geçme şartı** (B `yapi-denetim`):
  - 3 parti, her birinde 8 başlık dolu.
  - Parti oranı 0,30–0,35 ve vuruşlar ±0,04 (RE).
  - Parti sonu yoğunluğu ≥ 8, doruk ≥ 9, en karanlık an ≥ 6.
  - Her sahnede `bas ≠ son`.
  - Kurulum → kullanım sırası doğru; doruk çözümü P1 ya da P2'de kurulmuş (ZN Z1 #31).
  - Her `anahtar_olgu`nun `ekranda` kaynağı var.
- HATA çıkarsa aynı yazara döner.

#### H8 — Senaryo v1 (sahne sahne ekran metni)
- **İş:** A:`hikaye-yazari` parti parti yazar; her partiden sonra `yazar_defteri.md`'ye kararlarını ekler. Her sahne için:
  - **EKRAN bloğu** (seyircinin göreceği tek şey):
    - Yer/zaman kartı.
    - Görülen olaylar: kısa, fiziksel, gözlenebilir cümleler ("hazırlanır" değil, "çantaya ekmeği koyar, ipi omzuna atar").
    - Duyulan replikler (`R0001…`).
    - Ekran dışı ses.
  - **KÂĞIT bloğu** (seyirciye verilmez): amaç, risk, vuruş, merak aç/kapat, kurulum/kullanım, ironi, giriş/çıkış durumu,
    bilgi değişimi, `seyirci_ogrenir`, sahne değeri.
  - **İki soğuk açılış sürümü** (A/B, ilk 120 sn; ZN §7.2.2).
- **Replik kuralları** (baştan klibe uygun):
  - Tek konuşan; blok ≤ 16 kelime (10 sn klipte ≤ 20); ≥ 12 kelimelik blok "ekran dışına taşınabilir" diye işaretlenir.
  - Aynı karakter art arda ≤ 3 blok.
  - `teslim` sözlükten (`fisilti | yumusak | normal | soguk | bagirma`); bir blokta tek teslim.
  - Her replikte `tasidigi` alanı dolu.
  - **Filtre kelimesi yok**, çünkü replik Veo istemine girer (BK 4.2.4). Listede "sleep", "bed", "chest", "little", "child", "baby" var:
    "Get some sleep" → "Rest now", "Easy, little one" → "Easy now. I won't hurt you.", "treasure chest" → "the iron box" (DR, `istem_denetim.py`).
  - Yaş ifadesi yok (`YAS_IFADESI`).
  - Bilgi taşıyan replikte çatışma var; "bildiğin gibi" repliği yok (ZN §4.5).
  - **Konuşma ile el işi aynı satırda yok** (ZN §2.3); eylem ayrı satırda, replikten önce ya da sonra.
  - **Ses tanıtım kuralı:** her karakterin ilk repliği ekranda ve ağzı görünür biçimde yazılır ([SES] S0.3). İstisna:
    `gizemli_ses: true` + açık bir merak sorusu.
  - **Görünüşe atıf** yalnız hikâyeye bağlı görünüş öğesiyle yapılır (İ9).
  - EKRAN dilinde iç durum fiili yok (realizes, decides, remembers, knows): BAYRAK (R2). Sonuç fiilleri (RE `yasak_sonuc_fiilleri`): BAYRAK.
- **Çıktı:** `06_SENARYO_v1.md` + `.json` (§4.5.2 `sahneler[]`, `replikler[]`).

#### H9 — Oyuncu ve diyalog denetimi
- **Girdi:** B `oyuncu-paketi`. Her konuşan karakter için kart (bildiği, bilmediği, istediği, konuşma tarzı) + yalnız o karakterin replikleri;
  her repliğin hemen önündeki ekran olayı ve önceki replik. Diyalog editörüne bütün replikler + dönem kuralları + evren sözlüğü.
- **İş:**
  - A:`oyuncu`: ana karakter başına bir örnek; yan karakterler tek örnekte. "Bunu böyle söyler mi, nereden biliyor, neden şimdi?"
    (FilmAgent; AR1 A1; ZN §7.2.5).
  - A:`diyalog-editoru`: İngilizce doğallık; dönem dili (ortaçağda "okay", "guys" yok); ad tutarlılığı; telaffuz riski; filtre;
    kelime sınırı; TR altyazı önerisi.
  - **Tur 1'de hepsi** çalışır. Sonraki turlarda betik replik farkını çıkarır; yalnız replikleri değişen karakterlerin oyuncusu
    ve değişen repliklerle diyalog editörü çalışır.
- **Çıktı:** `07_oyuncu_<id>.md`, `07_diyalog.md`. Her madde `R0123 | KRİTİK/ORTA/KÜÇÜK | sorun | öneri` biçimindedir.
- **Geçme şartı:** yazar bütün KRİTİK ve ORTA maddeleri uygular ya da gerekçesini yazar (→ `v1b`); betik madde kapanışını denetler.

#### H10 — Senaryo denetimi (makine)
- **İş** (B `senaryo-denetim`): sahne süresi tahmini (`hedef_sure_sn` + ZN §2.3 replik formülü) ile birikimli zaman çizelgesi kurulur.
  Sonra §4.7'deki bütün hikâye düzeyi maddeler çalışır:
  - Z1/Z2 maddeleri.
  - Filtre ve NE YOK (`evren.py ne_yok_kelimeleri`).
  - **Kanon** (ölü karakter konuşuyor mu, evren kuralı çiğneniyor mu).
  - **Bilgi durumu** (karakter bilmediği kimliği kullanıyor mu).
  - **Sahne sınırı durumu** (S_n çıkışı ≠ S_n+1 girişi ve arada zaman atlaması ya da ekranda sebep yoksa HATA).
  - Vaat sözleşmesi, ilk replik ekranda, görünüş atfı, `tasidigi` ↔ `anahtar_olgular` tutarlılığı.
- **Çıktı:** `_RAPOR/HIKAYE_Z_<surum>.json` (ZN §6.2 biçimi) + `YENIDEN_YAZ.json` (yazar: `hikaye-yazari`).
- **Geçme şartı:** HATA = 0. BAYRAK'lar raporda kalır ve seyirci turuna taşınabilir.

#### H11 — Kâğıt seyirci döngüsü
- **Paket:** B `kor_paket.py --kip kagit --tur n` paketi **yalnız EKRAN bloklarından** üretir:
  - Bölümler: `P0` (0–120 sn), `P1` kalanı, `P2`, `P3`. Her bölümün başında tahmini zaman kodu.
  - **Ad maskeleme:** karakter adı ekranda sözle söylenene ya da yazıyla gösterilene kadar `maske.etiket_anonim_en` ile anılır
    ("WOMAN IN A FUR-COLLARED COAT"). `takma_adlar` (unvan, akrabalık sözcüğü) de aynı kurala uyar.
  - Ekran dışı replik [SES]'in işitsel döküm biçimiyle verilir: "ekran dışı: daha önce duyduğun boğuk erkek sesi".
  - Pakette olmayanlar: `ekranda_bilgi`, `seyirci_ogrenir`, KÂĞIT blokları, merak defteri, önceki tur raporları ve **önceki film özeti**.
  - `SORULAR.md` (açık uçlu, bilgi sızdırmaz): ana karakterler kim, ilişkileri ne; kahraman neyi kaybedebilir; bu dünyanın kuralları neler;
    ekran dışı sesler kime aitti; bir karakterin adını ilk nereden öğrendin; bir sonraki filmi izler miydin.
- **İş:**
  - 3 A:`habersiz-seyirci` (kip `kagit`): her turda **yeni** örnek, paralel, birbirini okumaz.
  - **Sıralı okuma zorunlu:** GIRDI'de önce yalnız P0 vardır. Seyirci P0'dan sonra "2. dakikanın sonunda devam eder miydin" sorusunu
    cevaplar (bu cevap bilgi amaçlıdır, kapıyı H12 tutar). Her bölümün raporunu yazınca betik sonraki bölümü GIRDI'ye kopyalar;
    AC aynı örneği SendMessage ile sürdürür (İ6).
  - Rapor: 6 ölçüt (parti başına ve film); kopukluklar; sıkıldığım sahneler; sahne başına ilgi (1–10); açık sorular; 3 cümle parti özeti;
    `SORULAR.md` cevapları; son satırlar `OZET_P1..3` ve `OZET`.
  - Seri devamında + 1 "dönen seyirci" `IZLEYICI_OZETI.md` ile okur. Medyana girmez; kanon çelişkisi ve gereksiz tekrar bulgusu verir (İ2, tahmin).
  - 3 A:`ozet-eslestirici`: her seyircinin özetini ve cevaplarını `anahtar_olgular` ile, açık sorularını `MERAK_DEFTERI` ile karşılaştırır.
    Her olgu için `bulundu / kismen / yok` kararı verir ve seyirci metninden alıntı yapar. Oranı betik hesaplar.
  - B `seyirci-topla`:
    - Medyanlar; KRİTİK birleştirme (aynı sahne ±1).
    - 2+ seyircinin işaretlediği sıkılma sahneleri → kesme adayı.
    - İlgi ↔ `duygu_haritasi` korelasyonu (Spearman ≥ 0,5; tahmin; BAYRAK).
    - "Defterde var, seyircide yok" soruları.
- **Tek seyircinin KRİTİK'i** ([KUR] §5.9 uyarlaması):
  - İki ya da daha çok seyircinin verdiği KRİTİK geçersiz sayılamaz.
  - Tek seyircinin verdiği KRİTİK'i yalnız A:`yapimci` (doktor kipi, yeni örnek, yazar değil) `kanit: {ekran_satiri, zaman}` ile geçersiz sayabilir.
  - Betik kanıtı doğrular: alıntılanan satır o seyircinin paketinde var mı, kopukluk anından önce mi, maskelenmemiş mi. Doğrulanmazsa KRİTİK kalır.
- **Çıktı:**
  - `_HIKAYE_ODASI/_SEYIRCI/<tur>/s<k>_rapor.md/.json`
  - `08_ESLESME_<tur>.json`
  - `08_SEYIRCI_TUR<n>.json` (§4.5.7)
- **Geçme şartı:** S1–S4 (parti başına ve film).
- **Döngü:**
  - Geçmezse aynı `hikaye-yazari` v(n+1) yazar. Her KRİTİK ve ORTA maddeyi uygular ya da gerekçe yazar; dosyanın başına "vN değişiklikleri"
    tablosu koyar (YR A5).
  - Kesme adaylarının en az yarısı uygulanır (RE `kesme_turu_oneri`). Her kesmeden sonra H10 yeniden koşar; kesilen sahne bir kurulumu
    götürmüş olabilir (DR "miğfer" dersi).
  - **Salınım koruması:** GENEL medyan bir önceki turdan ≥ 1 düşerse betik en iyi sürümü `EN_IYI` diye işaretler; yazar yeni tura bu sürümden başlar
    (B2 P1'de v7 6 → v8 5; H/proje-b2).
  - **Merdiven** (§2.6):
    1. Tur 1–4.
    2. Tur 3'te iyileşme < 0,5 ise `yapimci` doktor kipi yapısal teşhis yazar (sorun sahnede mi, partide mi, yayda mı; en çok 5 somut değişiklik;
       kendisi yazmaz).
    3. 4. tur sonunda KRİTİK 0 ve GENEL ≥ 7,5 ise doktor + 2 yapısal tur.
    4. Jürinin ikinci önerisiyle H7'den (≤ 4 tur).
    5. DUR + engel bildirimi. Soru sorulmaz.
- **Kim:** B + A:`habersiz-seyirci` ×3 (+1) + A:`ozet-eslestirici` ×3 + A:`hikaye-yazari` (+ A:`yapimci` doktor kipi).

#### H12 — İlk 2 dakika testi (A/B)
- **Zaman:** **tur 1 ile paralel** çalışır. Sonraki turlarda yalnız ilk 120 sn'nin EKRAN metni değişirse yeniden koşar
  (3 seyirci, seçilen sürüm). Kilitte son sürümün 3/3 almış olması şarttır.
- **Paket:** B `kor_paket.py --kip ilk2dk`: başlık + kapak imgesi tarifi + ilk 120 sn. Seyirci gerçek YouTube'daki gibi başlığı ve kapağı görerek girer.
- **İş:** her sürüme 3 yeni A:`habersiz-seyirci` (kip `ilk2dk`). Sorular: "30 sn'den sonra kalır mıydın? 2. dakikanın sonunda devam eder miydin? Neden?
  Başlıkta ve kapakta vaat edileni gördün mü?"
- **Çıktı:** `09_ILK2DK.json`; kazanan sürüm metne girer.
- **Geçme şartı:** 3/3 "evet" (S5). İki sürüm de geçemezse yazar üçüncü bir sürüm yazar (en çok 2 tur).

#### H13 — Kilit ve devir
- **İş** (B `hikaye_odasi.py devir`):
  - `HIKAYE.json` (+ `_sahip`, `_surum`, `_uretim` zarfı) ve `HIKAYE.md` üretilir.
  - `anahtar_olgular`, `MERAK_DEFTERI` ve ilk 2 dk sürümü plan, animatik ve kurgu seyircileri için **aynen** saklanır; ölçütler kıyaslanabilir kalır.
  - **Evren ön kaydı:** `evren.py on-kayit` seri adını, karakter kimliklerini, adları, kostüm kimliklerini ve mekân kimliklerini kilitler.
    Görüntü (A1/A2) ve ses (A1) aynı kimlikleri kullanır.
  - KARAR_DEFTERI güncellenir; `FILM_DURUM`'da hikâye aşaması kilitlenir.
- **Geçme şartı:** S1–S16 yeşil; `HIKAYE.json` jsonschema doğrulamasından geçti.
- **Kullanıcıya:** 5 satırlık bilgi (soru değil).

#### H15 — Kilit sonrası hikâye değişikliği (dar kapsam)
- **Tetik:** §2.4 yönlendirmesinde sahibi `hikaye-yazari` olan bulgu; ya da yönetmen veya kurgucunun `sahne_degisiklik_istegi`,
  `replik_degisiklik_istegi`, ad değişikliği isteği.
- **Hikâye merdiveni** (en ucuzdan başlanır; kurgucunun 0 kredi merdiveniyle aynı ruh, [KUR] §5.5):
  1. Mevcut repliği bölme ya da ekran dışına taşıma (kelime değişmez; yönetmen veya kurgucu).
  2. **Ekran dışı köprü replik:** yazar, bilgiyi taşıyan kısa bir ekran dışı replik yazar (Yol B TTS, Flow kredisi 0).
     Şartlar: konuşan daha önce ekranda konuşmuş olmalı; sahne başına ≤ 1 (tahmin); filtre, oyuncu ve diyalog denetimi.
  3. Yer/zaman kartı (kurgucu).
  4. Mevcut sahneye ekleme ya da tepki planı (yönetmen; görsel 0 kredi, video kredili).
  5. Yeni sahne (yazar içeriği yazar, yönetmen planlar; kredili).
- **Akış:** yazar değişikliği yalnız etkilenen sahnelerde yapar → H10 → etkilenen partide kâğıt seyirci 1 tur (3 yeni seyirci, tam metin) →
  yönetmen etkilenen sahneyi yeniden planlar → maliyet `URETIM_ONIZLEME`'ye yansır.
- **Video sonrası:** yalnız KRİTİK bulgular için ve önce 1–3. basamaklar denenir.
- **Kullanıcıya:** soru sorulmaz.

#### H14 — Evren kaydı (film yayına hazır olunca)
- **Girdi:** son `HIKAYE.json`, kurgudan sonra gerçekleşen değişiklikler (kesilen sahneler kanondan düşer), `DURUM_SON.json` (salt okunur).
- **İş:** A:`hikaye-yazari` (kip `evren`) `_HIKAYE_ODASI/EVREN_TASLAK.json`'u yazar. İçinde bu filmin kanon olayları (yalnız ekranda kalanlar),
  karakterlerin yay sonu ve bildikleri, yeni kurallar, açık seri soruları, kullanılan başlık ve kanca ailesi, sonraki tohum bulunur.
  B `evren.py hikaye-kaydet --dogrula` şemayı ve kanon çelişkisini denetleyip sürümlü olarak yazar. Silme yoktur.
- **Kim:** A + B.

#### 4.2.1 Kanca ve başlık mantığının hikâyeye gömülmesi
Başlık ve kapak filmin ilk sözleşmesidir. YouTube izleyicisi 0–2 dk arasında bu sözleşmenin tutulup tutulmadığına bakar
(ZN §1.4 "vaat görülmedi" bırakma anı). Bu yüzden başlık en son değil, **en başta** yazılır ve hikâye ona bağlanır:
1. **Önce başlık:** her mimar loglinedan hemen sonra 3 başlık yazar (BK 1.6 kalıbı). Kanca cümlesinin 4 öğesi:
   - özne (She/He/The Soldier),
   - güçlü geçmiş zaman fiili (Raised, Chose, Hid),
   - yasak ya da bedel nesnesi (the Dragon),
   - karşı güç (They Ordered Her to Kill, Over the Army).
   Bu ayrıştırma kazanan örneklerden (AN T14–16) benim çıkarımımdır [Y].
2. **Vaat sözleşmesi** (makine denetler): başlığın her öğesi ve kapak imgesi bir sahneye bağlanır.
   - Kapak imgesi ve çekirdek ilişki ≤ 120 sn'de ekranda olur (RE `vaat_imgesi_max_sn`).
   - Karşı gücün yasağı ≤ 180 sn'de sözle verilir (RE `risk_sozlu_max_sn`).
   - Başlık fiilinin süreci orta noktaya kadar ekranda gerçekleşir (tahmin).
   - Filmde olmayan kare kapak olamaz (BK 1.7.6).
3. **Bölüm adları** hikâyede yazılır, çünkü merak sorusudur: ≤ 8 bölüm, parti/vuruş sınırlarında (ZN §1.4). Zamanı kurgu verir,
   YouTube kurallarını yayın doğrular (ilk bölüm 00:00, ≥ 3 bölüm, her biri ≥ 10 sn; bu oturumda doğrulanmadı).
4. **Short adayları:** her partide ≥ 1 aday. Kendi başına anlaşılır, ilk 2 sn'de kanca verir, soruyla biter (BK 1.8.4, 3.10).
   Doruğu ve en büyük sırrı açmaz.
5. **Seri kancası:** jenerikten önce ≤ 20 sn (RE `seri_kancasi_max_sn`). `sonraki_tohum` evrene yazılır (BK 2.4: hitler seride yoğunlaşıyor).
6. **"Full Movie" bütünlüğü:** ana soru filmin içinde kapanır; açık kalan seri sorusu ≤ 2 (RE `seri_sorusu_max`). Önceki filmden gereken bilgi
   filmde ekranda verilir (İ2). Format kararının neden-sonuç kanıtı yok [H] (BK 1.5).
7. **Manhwa kancası katmanı [H]:** birincil aile insan + yaratık bağıysa ikincil ihanet ya da küçümsenen kahraman katmanı jüride `kanca`
   ölçütünde ayrıca değerlendirilir (BK 2.2); tutup tutmadığı ders defterine yazılır.
8. **Yayınla sınır:** yayın, hikâyenin adaylarından seçer. Yeni başlık `vaat-denetim`den geçer. "kill" BAYRAK'tır, yasak değildir (İ11).

### 4.3 Gereken ajanlar

**Ortak kurallar ([MİM] §3.1 ile aynı):**
- Hepsi `model: opus` (`claude-opus-5-5`) ve `effort: high`. Opus 5.5'te varsayılan efor `medium` olduğu için `high` açıkça yazılır.
- `memory:` alanı hiçbir ajanda yok; `fallbackModel` tanımlanmaz.
- Değerlendiricilerde araçlar `Read, Write`; yazarlarda `Read, Write, Edit, Glob, Grep`. Hiçbir ajanda `Bash`, `Agent`, `WebFetch` yok.
- Kör rollerde (`habersiz-seyirci`, `oyuncu`, `ozet-eslestirici`) `omitClaudeMd: true` ve `Glob/Grep` yok.
- Erişim, ayar dosyasındaki `erisim_kapisi` kancasıyla görev klasörüne bağlanır.
- Devretme mesajı yalnız şudur: `"Görevin: <yol>/GOREV.json — önce onu oku, yalnız orada yazanı yap."`
- Gövde sırası: rol → "Çağrıldığında" adımları → kontrol listesi → çıktı sözleşmesi.
- Çıktı sözleşmesi: önce başlıkları yaz, bölüm bölüm doldur; `.json` + son satır `OZET | …`; ana Claude'a ≤ 5 satır dön.
- Sayılar gövdeye yazılmaz; şablon RE'den basar.
- Değerlendirici her turda yeni örnektir. Tek istisna aynı tur içinde aşamalı okumadır.

| # | Ajan | Durum | Kipler | Görev | Okuduğu (GIRDI) | Çıktısı |
|---|---|---|---|---|---|---|
| 1 | `yapimci` | ortak ([MİM]); konu-analisti ve hikaye-doktoru buna katıldı | `konu`, `doktor` | Konu kartı, süre, eksenler, varsayımlar, "sen seç". Doktor kipinde yapısal teşhis ve tek-seyirci KRİTİK reddi (kanıtlı). **Yazmaz.** | Konu, kanal kararları, BK dilimi, evren dizini, dersler, bütçe bilgisi; doktor kipinde son senaryo, raporlar, ZN §7.1 | `01_KONU_KARTI.json`, `01_VARSAYIMLAR.md`; `08_DOKTOR_<tur>.md`, `KRITIK_RED_<tur>.json` |
| 2 | `hikaye-mimari` | güncellenir | eksen D/S/E/X (A/B/S/X) | Verilen eksende 10 başlıklı öneri. Diğer önerileri okumaz | Brifing, eksen satırı, (bonusta) kaçınılacak loglinelar, evren (devamsa) | `02_oneri_<X>.md/.json` |
| 3 | `juri-uyesi` | yeni ([MİM] ile aynı) | 4 rol | Anonim 4 öneriyi 10 ölçütle puanlar | Brifing, jüri paketi, `JURI_TABLOSU.md` | `03_juri_<rol>.md/.json` |
| 4 | `uretilebilirlik-denetcisi` | ortak (mevcut) | `juri` kipi | 5. jüri: K1–K9, süreklilik yükü, filtre; aşırı temkin uyarısı (YR A5) | + DR, kendi kontrol listesi | `03_juri_uretilebilirlik.md/.json` |
| 5 | `hikaye-yazari` | yeni ([MİM] adı) | `yapi`, `senaryo`, `revizyon`, `dar_degisiklik`, `evren` | Birleştirme, 3×8 yapı, senaryo, bütün revizyonlar, H15, evren taslağı. **Replik metninin tek sahibi.** `yazar_defteri.md`'yi tutar | Kazanan öneri, seçim, brifing, ZN §1, §2.3, §4, RE, evren, gelen raporlar | `05_YAPI`, `06_SENARYO_vN`, `vN_DEGISIKLIKLER.md`, `EVREN_TASLAK.json` |
| 6 | `oyuncu` | ortak ([MİM]); kör | karakter başına | Yalnız kendi karakterinin repliklerini kendi kartına göre okur | Betiğin oyuncu paketi | `07_oyuncu_<id>.md` |
| 7 | `diyalog-editoru` | yeni | — | Doğallık, dönem dili, ad tutarlılığı, telaffuz riski, filtre, TR altyazı önerisi. Ayrı girdisi var (bütün replikler sırayla, yapı yok): [MİM] Ç-10 (b) | Replikler, evren sözlüğü, DR filtre bölümü | `07_diyalog.md` + `tr` önerileri |
| 8 | `habersiz-seyirci` | ortak, güncellenir; kör | `kagit`, `plan`, `ilk2dk`, `animatik`, `kurgu` | Habersiz izleme; 6 ölçüt; tek şema | Yalnız GIRDI paketi | `rapor.md/.json` |
| 9 | `ozet-eslestirici` | yeni ([KUR] adı, opus); kör | — | Seyirci özeti ↔ `anahtar_olgular`; açık sorular ↔ merak defteri; puan vermez | Seyirci JSON'u, olgu listesi, merak soruları (cevapsız) | `eslesme.json` |

**`hikaye-yazari` frontmatter:**
```yaml
---
name: hikaye-yazari
description: Hikâye odasının yazarı. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır; kazanan öneriyi
  3 parti × 8 başlık yapıya ve sahne sahne ekran metnine çevirir, jüri/seyirci/oyuncu raporlarıyla revizyon yazar, kilit sonrası
  dar değişiklikleri ve evren taslağını hazırlar. Replik metninin tek sahibidir.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 80
---
```
**`habersiz-seyirci` frontmatter** ([MİM] §3.4 ile aynı; kipler eklendi):
```yaml
---
name: habersiz-seyirci
description: Filmi hiç bilmeyen, ilk kez izleyen YouTube seyircisi. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında
  kullanılır; kagit, plan, ilk2dk, animatik ya da kurgu kipinde yalnız GIRDI paketini sırayla okuyup puan ve kopukluk raporu yazar.
  Her turda yeni örnek açılır.
tools: Read, Write
model: opus
effort: high
maxTurns: 60
omitClaudeMd: true
---
```
**`ozet-eslestirici` gövdesinin çekirdeği:** "Sana bir seyircinin özeti ve bir olgu listesi verildi. Her olgu için seyircinin metninde
bu olgu **açıkça** var mı bak: `bulundu`, `kismen`, `yok`. Kararını seyirci metninden alıntıyla destekle. Olguyu kendi bilginle tamamlama;
seyirci yazmadıysa yok demektir. Oran hesaplama."

**`JURI_TABLOSU.md`** (yeni referans dosyası): 10 ölçütün tanımı; her ölçüt için 1/5/8/10 puanın neye benzediği ("8 = gerçekten iyi,
cömert olma"); rol başına bakış açısı; JSON şeması.

### 4.4 Beceri (skill) tarif adımları
- [MİM] §4 modeline uyuyorum: aşama ayrıntısı ana Claude'un SKILL.md'sinde durmaz. Ayrıntı `film.py`'nin aşama kaydında (`hat/asamalar.py`)
  ve ajan şablonlarında (`.claude/skills/film-yap/sablonlar/`) durur. Ana Claude yalnız `film.py sonraki`'nin verdiği görevi dağıtır.
- Hikâye odası kredi harcamadığı için `disable-model-invocation` gerekmez.

**SKILL.md çekirdeğine eklenecek hikâye kuralları** ([MİM] §4.3'teki 10 maddenin içine, en üstte):
1. Kullanıcıya yalnız konu sorulur. Ton, süre, ad, öneri seçimi sorulmaz.
2. Öneriyi, senaryoyu ya da raporu sen puanlamaz ve düzeltmezsin. Seçimi betik, düzeltmeyi metni yazan ajan yapar.
3. Habersiz seyirciye yalnız görev paketi verilir; ona ipucu, açıklama ya da "şuna dikkat et" yazılmaz.

**Şablonlar** (betik doldurur; ajana sabit sayı yazılmaz):

| Şablon | Ajan / kip | İçerik (kısa) |
|---|---|---|
| `A01_yapimci_konu.md` | yapimci / konu | H1 adımları 1–8, konu kartı şeması, kanca ailesi tablosu |
| `A03_mimar.md` | hikaye-mimari | 10 başlık, eksen satırı, (bonus) kaçınılacak loglinelar, "diğer önerileri okuma" |
| `A04_juri_<rol>.md` | juri-uyesi / rol; uretilebilirlik-denetcisi / juri | Rol bakışı, `JURI_TABLOSU`, JSON şeması |
| `A05_yazar_yapi.md`, `A05_yazar_senaryo.md` | hikaye-yazari | 8 başlık tanımı; EKRAN/KÂĞIT; replik kuralları; A/B açılış |
| `A05_oyuncu.md`, `A05_diyalog.md` | oyuncu, diyalog-editoru | Kontrol soruları, madde biçimi |
| `A06_seyirci_kagit.md`, `A06_seyirci_ilk2dk.md` | habersiz-seyirci | Sıralı okuma, ölçütler, `SORULAR.md`, rapor şeması |
| `A06_eslestirici.md` | ozet-eslestirici | Karar kuralı, alıntı zorunluluğu |
| `A06_yazar_revizyon.md` | hikaye-yazari / revizyon | Madde kapanış tablosu, EN_IYI kuralı, kesme adayları |
| `A06_yapimci_doktor.md` | yapimci / doktor | ZN §7.1 teşhis tablosu, ≤ 5 değişiklik, KRİTİK reddi kanıt biçimi |
| `H15_yazar_dar.md` | hikaye-yazari / dar_degisiklik | Hikâye merdiveni, etkilenen sahne sınırı |
| `A18_yazar_evren.md` | hikaye-yazari / evren | Evren taslak şeması, kanon kuralları |

**`hat/asamalar.py` girişlerinden örnek** (alan adları [MİM] ve [ÜRE] ile uzlaşılacak):
```python
("A06", "kagit_seyirci", "ajan+betik",
 girdiler=["_HIKAYE_ODASI/06_SENARYO_v*.json", "ESIKLER"],
 gorevler=[("kor_paket", "betik"), ("habersiz-seyirci", 3, "kagit", "yeni", "asamali:P0,P1,P2,P3"),
           ("ozet-eslestirici", 3), ("seyirci-topla", "betik")],
 kapi="S1-S4", tur_max=4, merdiven="hikaye_merdiveni", geri_don="A05:revizyon")
```

**Devam etme:** her adım dosya üretir. Betik çıktı dosyası varsa ve imza aynıysa "zaten var" der. Sıkıştırmadan sonra durum
`oturum_basi` kancasıyla geri gelir ([MİM] K-5).

**Değerlendirme senaryoları:**
1. "film yap" → yalnız konu sorusu gelir.
2. "ejderha yavrusu saklayan kadın" → soru yok; A01–A03 görevleri.
3. "sen seç" → 3 aday ve seçim kaydı.
4. Yarım kalmış film → kaldığı görevden devam; biten görev tekrar edilmez.
5. "EMBERFALL'ın devamı" → A/B/S/X eksenleri ve dönen seyirci.
6. Animatikten gelen "bunu nereden biliyor" bulgusu → `bulgu-sinifla` hikâyeye yönlendirir; yönetmen görevi açılmaz.
7. Seyircinin ileriyi okuma girişimi → `erisim_kapisi` reddeder.

### 4.5 Veri şeması / plan alanları (JSON örneğiyle)
Hepsi UTF-8 JSON ve `jsonschema` ile doğrulanır (`YZ_FILM/ARACLAR/semalar/*.schema.json`).
Örnek konu "ejderha yavrusunu saklayan avcı kadın" uydurmadır, gerçek proje değildir.

#### 4.5.1 `01_KONU_KARTI.json`
```json
{
 "_sahip": "yapimci", "_gorev": "G0003", "_surum": 1,
 "konu_ham": "ejderha yavrusunu saklayan avcı kadın",
 "kesin_istekler": [],
 "seri": {"durum": "yeni", "evren": null, "gerekce": "konu kayıtlı evren/karakter anmıyor"},
 "tur": "fantastik",
 "kanca_ailesi": {"birincil": "insan_yaratik_bagi", "ikincil": "ihanet"},
 "vaat_imgesi": "A huntress in a snowstorm shields a glowing dragon hatchling under her cloak while torches approach",
 "riskler": [
  {"tur": "filtre", "aciklama": "yavru için 'baby/little'", "seviye": "orta", "cozum": "sözlük: 'the hatchling'; boy benzetmeyle"},
  {"tur": "uretim", "aciklama": "kalabalık asker", "seviye": "orta", "cozum": "siluet, meşale, sırt; yüz ≤ 2 adlı karakter"}
 ],
 "sure": {"film_sure_hedef_sn": 2400, "butce_kaynagi": "bilinmiyor",
          "tahmini_kredi": 6320, "gerekce": "bulut oturumu; RE film_sure_hedef_sn"},
 "eksenler": {"D": "Sera yavruyu büyütürken anneliği öğrenir",
              "S": "Seyirci yavrunun yerini bilir, ağabeyi bilmez",
              "E": "Kral avcılarından kış boyu kaçış",
              "X": "serbest"},
 "varsayimlar": [{"karar": "süre 40 dk", "neden": "bakiye bilinmiyor", "yanlissa_maliyet": "video kapısında bekleme"}]
}
```

#### 4.5.2 `HIKAYE.json` — hikâye odasının tek çıktısı
- `06_SENARYO_vN.json` aynı şemadadır; `HIKAYE.json` kilitli sürümdür.
- Film düzeyi alanlar ZN §6.1'deki adları kullanır.
```json
{
 "_sahip": "hikaye-yazari", "_surum": "v3", "_uretim": {"asama": "A06", "girdi_imza": "…", "esik_surum": "…"},
 "kilit": true, "evren": "FROSTHOLLOW", "film_no": 1, "film_sure_hedef_sn": 2400,
 "logline": "A disgraced huntress hides the last dragon hatchling from the king's burners, while her own brother leads the hunt.",
 "baslik": {"secilen": "She Hid the Dragon the King Ordered Burned | FROSTHOLLOW | Full Movie 4K 2026", "adaylar": ["…", "…"]},
 "vaat_sozlesmesi": [
  {"oge": "Hid the Dragon", "sahne": "S03", "ekranda": "Sera wraps the hatchling in her cloak as torches approach"},
  {"oge": "the King Ordered Burned", "sahne": "S02", "replik": "R0006", "sozlu": true},
  {"oge": "kapak_imgesi", "sahne": "S03", "ekranda": "cloak + glow + torches"}
 ],
 "duygu_haritasi": {"0": {"yogunluk": 8, "tur": "gerilim"}},
 "vuruslar": {"soguk_acilis": 0.0, "ilk_kanca": 0.3, "orta_nokta": 20.0, "doruk": 36.0, "seri_kancasi": 38.6},
 "anahtar_olgular": [
  {"id": "o01", "hikaye_partisi": "P1", "olgu": "Sera ejderha yavrusunu kraldan saklıyor", "kritik": true, "ekranda": ["S03", "R0011"]},
  {"id": "o02", "hikaye_partisi": "P1", "olgu": "Ejderha saklamak ölüm cezası", "kritik": true, "ekranda": ["S02", "R0006"]},
  {"id": "o03", "hikaye_partisi": "P1", "olgu": "Avı yöneten kaptan Brann, Sera'nın ağabeyi", "kritik": true, "ekranda": ["S09", "R0042"]}
 ],
 "MERAK_DEFTERI": [{"id": "m03", "soru": "Brann kız kardeşini ele verecek mi?", "ac": "S09", "kapat": "S31", "tur": "buyuk"}],
 "KURULUMLAR": [{"id": "kur_duduk", "ne": "Kemik düdük ejderhayı sakinleştirir", "kurulum": "S05",
                 "hatirlatma": ["S22"], "kullanim": "S44"}],
 "IRONILER": [{"id": "i01", "seyirci_bilir": "S08", "karakter_ogrenir": "S11", "ne": "Brann'ın adamı kulübeyi gözlüyor"}],
 "bolum_adlari": [{"bas_sahne": "S01", "ad": "The Light Under the Snow"}],
 "short_adaylari": [{"sahneler": ["S03"], "kanca_2sn": "torches + glowing cloak", "acmadigi": ["m03", "doruk"]}],
 "seri_kancasi": {"sahne": "S49", "sure_sn": 18, "merak": "m99", "sonraki_tohum": "He Burned the Village That Hid Her"},
 "mekanlar": [
  {"id": "kulube", "tekrar": 9, "hikaye_olgulari": ["tek giriş kapısı", "pencereden vadi yolu görünür"],
   "isik_hikaye": "ateş yakmak yasak (ev01); içeride yalnız kandil"},
  {"id": "magara_agzi", "tekrar": 4, "hikaye_olgulari": ["aşağıda yol görünür"]}
 ],
 "kostum_degisimleri": [{"karakter": "sera", "varyant": "k1_yirtik", "sahne": "S24",
                         "neden": "kayalıktan düşüş", "ekranda": "S24 düşüş anı"}],
 "karakterler": {
  "sera": {"ad": "Sera", "ad_telaffuz": "SEH-rah", "rol": "kahraman", "yas_bandi": "yetiskin",
           "istek": "ağabeyinin affı", "korku": "yine terk edilmek", "yara": "sürgün edilmiş avcı", "sir": "yavruyu saklıyor",
           "yay": {"bas": "kimseye güvenmez", "son": "bağ için her şeyi göze alır"},
           "konusma_tarzi": "kısa, kuru cümleler; asla 'please' demez",
           "bildikleri_bas": ["ferman", "dağ yolları"],
           "maske": {"etiket_anonim_en": "woman in a fur-collared green cloak", "takma_adlar": ["sister", "huntress"]},
           "gorsel_ayirt_edici": [{"oge": "kızıl tek örgü", "hikaye_baglayici": true, "neden": "R0120 'the red-braided one'"},
                                  {"oge": "koyu yeşil yün pelerin", "hikaye_baglayici": false}],
           "bilincli_benzerlik": [],
           "ses_karakteri": "kadın, yetişkin; alçak ve hafif boğuk; kuzey aksanı; kesik ve ölçülü",
           "kostum": {"varsayilan": "k1", "varyantlar": ["k1", "k1_yirtik"]}},
  "kit": {"ad": "Kit", "rol": "yaratik", "konusmaz": true,
          "boy": {"S03": "kedi boyu (benzetme)", "S40": "at boyu (benzetme)"}}
 },
 "partiler": [
  {"id": "P1", "sahneler": ["S01", "S17"], "sure_hedef_sn": 780,
   "tek_cumle": "P1'de Sera ölüm fermanına rağmen yavruyu saklamaya karar verir ve ağabeyinin avı yönettiğini öğrenerek biter.",
   "b1_amac_duygu": {"amac": "…", "duygu_seyri": "gerilim>şefkat>korku"},
   "b2_vurus_akisi": ["S01 soğuk açılış", "S02 ferman", "…"],
   "b3_kim_nerede": [{"sahne": "S03", "giris": {"sera": "mağara ağzı, diz çökmüş"}, "cikis": {"sera": "patika, sırtında heybe"}}],
   "b4_nesne_yolu": [{"nesne": "kemik_duduk", "olaylar": [{"sahne": "S05", "kimden": "yasli_avci", "kime": "sera", "ekranda": "eline bırakır"}]}],
   "b5_yalan_niyet_bilgi": [{"kim": "brann", "yalan": "yardım ettiğini söyler", "seyirci_okur": {"arac": "ironi", "sahne": "S08"}}],
   "b6_mekan_olgulari": ["kulube", "magara_agzi"],
   "b7_parti_kancasi": {"sahne": "S17", "merak": "m03", "yogunluk": 9, "sonraki_acilis": "P2 ilk 20 sn'de Brann kapıda"},
   "b8_kaba_plan_ve_risk": {"plan_tahmini": 165, "riskli": [{"sahne": "S12", "neden": "elden yemek", "cozum": "ekleme + tepki"}]}}
 ],
 "sahneler": [
  {"id": "S03", "hikaye_partisi": "P1", "mekan": "magara_agzi",
   "zaman": {"gun": 1, "saat": "alacakaranlik", "hava": "kar", "atlama": "yok"},
   "sahne_tipi": "gerilim", "hedef_sure_sn": 95, "vurus": "ilk_kanca", "hedef_duygu": "korku>sefkat", "yogunluk": 7,
   "sahne_degeri": {"bas": "yalnız ve güvende", "son": "sırrı olan ve tehlikede"},
   "risk": "Sera yakalanırsa yavruyla birlikte yakılır",
   "merak_ac": ["m02"], "merak_kapat": ["m01"], "kurulum": [], "kullanim_bilgi": [], "ironi": null,
   "giris_durumu": {"varliklar": {"sera": {"mekan": "magara_agzi", "bolge": "agiz", "poz": "diz_cokmus",
                                            "kostum": "k1", "gorunum": {"kir": 1, "yaralar": []}}},
                    "nesneler": {"yay": {"kimde": "sera", "yer": "sirt"}, "fener": {"kimde": "sera", "el": "sag", "durum": "yanik"}}},
   "cikis_durumu": {"varliklar": {"sera": {"mekan": "patika", "kostum": "k1", "gorunum": {"kir": 1, "yaralar": []}},
                                  "kit": {"mekan": "patika", "yer": "sera_pelerin_ici"}},
                    "nesneler": {"yay": {"kimde": "sera", "yer": "sirt"}, "fener": {"nerede": "magara_agzi_zemin", "durum": "sonuk"}}},
   "bilgi_degisimi": [{"kim": "sera", "ogrenir": "yavru_yasiyor"}],
   "seyirci_ogrenir": "Ejderha yavrusu yaşıyor ve Sera onu saklamaya karar veriyor.",
   "ekran": {"kart": null,
             "gorulen": ["Torchlight flickers far below on the slope.",
                         "Sera kneels at the cave mouth; a faint orange glow pulses under the snow.",
                         "She brushes the snow aside with her gloved left hand; the hatchling's eyes open."],
             "duyulan": ["R0011"], "ekran_disi": ["distant horn", "wind"]},
   "kagit": {"amac": "Bağın ilk anı + saklama kararı", "neden_simdi": "askerler yaklaşırken karar zorunlu"}}
 ],
 "replikler": [
  {"id": "R0011", "sahne": "S03", "karakter": "sera", "teslim": "fisilti", "metin": "Easy now. Nobody burns you tonight.",
   "kelime": 6, "tasidigi": ["o01"], "ad_soyler": [], "ilk_replik": true, "ekran_disi_uygun": false,
   "tr": "Sakin ol. Bu gece kimse seni yakmayacak."}
 ]
}
```
**Durum nesnesi kuralı:** `giris_durumu` ve `cikis_durumu` [YÖN] §5.4 durum nesnesinin alt kümesidir:
- `varliklar.<id>.{mekan, bolge, poz, kostum, gorunum}` ve `nesneler.<id>.{kimde | nerede, el?, durum}`.
- `bolge` hikâyenin serbest etiketidir; yönetmen onu bir işarete (`M1`…) eşler.
- `el` yalnız hikâyeyi taşıyorsa yazılır. Sağ/sol daima karakterin kendisine göredir.

#### 4.5.3 `HIKAYE.json` → yönetmen: sahne sözleşmesi (makine denetler)

| HIKAYE alanı | Yönetmen tarafı | Kural |
|---|---|---|
| `sahneler[].id` | sahne grubu (`S07`, bölünürse `S07a/S07b`) | Kimlik 1:1. Bölme yalnız mekân/zaman kırılımında. Birleştirme, silme, sıra → istek |
| `hedef_sure_sn` | planların toplam süresi | ±%20 (tahmin); fazlası istek |
| `sahne_degeri`, `vurus`, `hedef_duygu`, `risk` | aynen | Değişmez. Plan yoğunluğu sahne değerinin ±2'si içinde |
| `merak_ac/kapat`, `kurulum`, `kullanim_bilgi`, `ironi` | plan `zanaat` alanları | Her kimlik tam olarak bir planda (kayıp ya da çift yok) |
| `giris_durumu` / `cikis_durumu` | sahnenin ilk planının `baslangic_durumu` / son planının `bitis_durumu` | Hikâyenin yazdığı her olgu eşittir (mekân, kostüm, görünüm, nesne kimde/nerede/durum, yazılmışsa el); yönetmen ekler, çelişemez |
| `replikler[].metin` | `replik.metin` | Kelimesi kelimesine aynı; bölme serbest (`replik_bolundu`); değişiklik → istek |
| `replikler[].tasidigi` | planın `ekranda_bilgi` alanı | Her `kritik` olgunun en az bir planda `ekranda_bilgi` karşılığı var |
| `seyirci_ogrenir` | sahnedeki planların `ekranda_bilgi` birleşimi | `ozet-eslestirici` anahtarı; seyirciye verilmez |
| `karakterler.*.maske` | `kor_paket.py` (bütün kipler) | Ad duyulana kadar etiketle anılır |
| `karakterler.*.ses_karakteri`, `ad_telaffuz` | `ses-kadrocusu` | Veo ses dizesi ve `veo_metin` buradan türetilir |
| `gorsel_ayirt_edici`, `bilincli_benzerlik`, `kostum_degisimleri` | kart tasarımcısı | Hikâyeye bağlı öğe kilitli |
| `mekanlar[].hikaye_olgulari` | kroki ve mekân kartı | Kroki bu olguları sağlamak zorunda |

#### 4.5.4 Evren: hikâye tarafı (`EVREN/<SERI>/hikaye.json` ve `karakterler/<id>/hikaye.json`)
```json
{
 "seri": "FROSTHOLLOW", "surum": 3, "son_film": 1,
 "donem": {"cag": "geç ortaçağ benzeri, barut yok", "teknoloji": "demir, yay, kızak, yağ kandili"},
 "kurallar": [{"id": "ev01", "kural": "Ateş Taç'ın malıdır; izinsiz ateş yakmak suç",
               "ekranda_kuruldu": {"film": 1, "sahne": "S02", "replik": "R0006"}}],
 "ne_yok_hikaye": [{"oge": "barut silahı", "neden": "dönem", "kelimeler_en": ["gun", "rifle", "pistol", "musket"]}],
 "kanon": [{"film": 1, "olay": "Kit yumurtadan çıktı, Sera onu sakladı", "sahne": "S03"}],
 "seri_sorulari": [{"id": "m99", "soru": "Kuzeyde başka yumurta var mı?", "acildigi_film": 1, "durum": "acik"}],
 "baslik_gecmisi": [{"film": 1, "baslik": "She Hid the Dragon the King Ordered Burned", "kanca_ailesi": "insan_yaratik_bagi"}],
 "sozluk": {"adlar": {"Sera": {"telaffuz": "SEH-rah", "hece": 2, "tts_dogrulandi": true}},
            "guvenli_karsilik": {"baby dragon": "the hatchling", "little one": "easy now", "chest (sandık)": "the iron box",
                                 "child": "(sahne yeniden tasarlanır)"}},
 "degisiklik_gunlugu": [{"surum": 3, "tarih": "2026-11-02", "film": 1, "ozet": "film 1 kanonu eklendi"}]
}
```
`karakterler/sera/hikaye.json`:
```json
{"id": "sera", "durum": "yasiyor", "yay_gecmisi": [{"film": 1, "bas": "kimseye güvenmez", "son": "bağ için her şeyi göze alır"}],
 "bildikleri": ["kit_bir_ejderha", "brann_avi_yonetiyor"], "iliskiler": {"brann": "ağabey, düşman", "kit": "bağ"},
 "konusma_tarzi": "kısa, kuru", "maske": {"etiket_anonim_en": "woman in a fur-collared green cloak", "takma_adlar": ["sister"]},
 "ses_karakteri": "kadın, yetişkin; alçak, hafif boğuk; kuzey aksanı",
 "hikaye_baglayici_gorunus": ["kızıl tek örgü"], "ilk_film": 1}
```
- Kanon yalnız **eklenir**; eski sürüm `hikaye_v{n}.json` olarak kalır.
- `bildikleri` sonraki filmin başlangıç bilgi durumudur; oyuncu denetimi buna göre yapılır.
- Fiziksel son durum (kostüm, yara) burada değil, `DURUM_SON.json`'dadır.

#### 4.5.5 Jüri çıktısı `03_juri_<rol>.json`
```json
{"rol": "youtube_stratejisti", "oneriler": {
  "1": {"puan": {"kanca": 8, "netlik": 7, "merak": 8, "duygu": 7, "karakter": 7, "ozgunluk": 6, "yapi": 7,
                 "uretilebilirlik": 8, "sureklilik_yuku": 7, "seri": 9},
        "gerekce": {"kanca": "insan+yaratık+emir başlıkta; kapak imgesi filmde S03'te var"},
        "calinmaya_deger": ["Öneri 3'ün kemik düdük kurulumu"],
        "mutlaka_duzelt": ["Ağabey ilişkisi 3. dakikadan önce sözle verilmeli"], "veto": null}},
 "siralama": ["1", "3", "2", "4"]}
```

#### 4.5.6 Seyirci raporu (bütün kiplerde tek şema; [KUR] §5.3 temel alındı)
```json
{"kip": "kagit", "tur": 2, "seyirci": 1, "bolum": "P1", "donen_seyirci": false,
 "ilk2dk_devam": true,
 "puanlar": {"anlasilirlik": 8, "akicilik": 7, "merak": 8, "duygu": 7, "ritim": 7, "ilk30": 9, "GENEL": 8},
 "kopukluklar": [{"konum": {"sahne": "S07", "plan": null, "zaman": "05:40"}, "tur": "KRITIK",
                  "neden": "Kürk yakalı kadının yavruyu nereden bildiğini anlamadım", "oneri": "…"}],
 "sikilma": [{"sahne": "S14", "bas": "09:10", "bit": "10:20", "neden": "aynı tartışma ikinci kez"}],
 "ilgi": [{"sahne": "S01", "puan": 9}, {"sahne": "S02", "puan": 7}],
 "acik_sorular": ["Kardaki ışık neydi?"],
 "ozet": "Üç cümle.",
 "karakterler": [{"ad_ya_da_tarif": "Sera", "kim": "avcı kadın", "adi_nereden": "R0004"}],
 "kahraman_ne_kaybedebilir": "Yavruyu ve kendi hayatını",
 "dunya_kurallari": ["ateş yakmak yasak"],
 "ekran_disi_sesler": [{"replik": "R0031", "kime_ait_sandim": "yaşlı avcı"}],
 "devam": true}
```
Rapor `.md`'sinin son satırları (`puan_oku.py` v2 önce JSON'u, yoksa bunları okur):
```
OZET_P1 | anlasilirlik: 8 | akicilik: 7 | merak: 8 | duygu: 7 | ritim: 7 | ilk30: 9 | GENEL: 8 | KRITIK: 0 | ORTA: 1
OZET | anlasilirlik: 8 | akicilik: 8 | merak: 8 | duygu: 7 | ritim: 7 | ilk30: 9 | GENEL: 8 | KRITIK: 0 | ORTA: 2
```

#### 4.5.7 Tur toplamı `08_SEYIRCI_TUR<n>.json` (betik üretir)
```json
{"tur": 2, "senaryo_surum": "v2", "seyirci": 3,
 "medyan": {"anlasilirlik": 8, "akicilik": 8, "merak": 8, "duygu": 7, "ritim": 7, "ilk30": 9, "GENEL": 8},
 "parti_medyan": {"P1": {"GENEL": 8}, "P2": {"GENEL": 7}, "P3": {"GENEL": 8}},
 "kopukluk": [{"sahne": "S22", "tur": "ORTA", "kac_seyirci": 2, "neden": "düdüğün nereden geldiği hatırlanmıyor"}],
 "kritik_gecersiz_sayilan": [{"sahne": "S07", "seyirci": 3, "kanit": {"ekran_satiri": "R0042", "zaman": "04:10"}, "betik_dogruladi": true}],
 "sikilma": [{"sahne": "S14", "kac_seyirci": 2, "kesme_adayi": true}],
 "eslesme": {"P1": 0.86, "P2": 0.78, "P3": 0.83, "eksik_olgular": ["o07"], "ekranda_acilmamis_sorular": ["m05"]},
 "ilgi_korelasyon": 0.61, "donen_seyirci": null,
 "gecti": false, "neden": ["P2 GENEL 7 < 8", "P2 eşleşme 0,78 < 0,80"], "en_iyi_surum": "v2", "merdiven_basamagi": 1}
```

#### 4.5.8 Bulgu yönlendirmesi `_HIKAYE_ODASI/BULGU_YONLENDIRME_<kaynak>_<tur>.json`
```json
[{"kaynak": "animatik_t1", "bulgu": "s2:k3", "konum": {"sahne": "S22", "plan": 241},
  "eslesen": {"tur": "anahtar_olgu", "id": "o07"}, "hikayede_var": false, "planda_var": false,
  "kok_neden": "bilgi_eksik", "sahip": "hikaye-yazari", "merdiven_onerisi": 2}]
```

#### 4.5.9 `_HIKAYE_ODASI/` klasör düzeni
```
00_KONU.md  00_BRIFING.md  00_DURUM.md  01_KONU_KARTI.json  01_VARSAYIMLAR.md
02_oneri_D|S|E|X.md/.json  03_juri_<rol>.md/.json  04_SECIM.json  04_KULLANICIYA_OZET.md
05_YAPI.md/.json  06_SENARYO_vN.md/.json  vN_DEGISIKLIKLER.md  07_oyuncu_<id>.md  07_diyalog.md
08_ESLESME_<tur>.json  08_SEYIRCI_TUR<n>.json  08_DOKTOR_<tur>.md  KRITIK_RED_<tur>.json  09_ILK2DK.json
BULGU_YONLENDIRME_*.json  yazar_defteri.md  EVREN_TASLAK.json  HIKAYE.json  HIKAYE.md
_SEYIRCI/<tur>/s<k>_rapor.md/.json      (paketler _GOREV/<id>/GIRDI/ içinde; kor_paket.py üretir)
```
KARAR_DEFTERI ve raporlar [MİM] düzenine göre film kökünde ve `_RAPOR/` altında durur.

### 4.6 Yazılması/değişmesi gereken kod
Stil: mevcut araçlar gibi tek dosya, Türkçe ad, `"""Kullanım: …"""`. Python 3.10; standart kütüphane + `jsonschema`.
Yollar ayardan okunur, ağ yok.
**P0** = ilk filmden önce şart · **P1** = ilk film sırasında · **P2** = ikinci filmden önce.

| Öncelik | Araç | Ne yapar | Girdi → Çıktı |
|---|---|---|---|
| **P0** | `ARACLAR/hikaye_odasi.py` (yeni, alt komutlu; `film.py` görevi olarak çağrılır) | `konu-denetim`, `butce-bilgisi`, `brifing`, `logline`, `oneri-denetim`, `juri-paketi`, `juri-topla`, `yapi-denetim`, `oyuncu-paketi` (fark kipli), `senaryo-denetim`, `seyirci-topla` (KRİTİK birleştirme, kanıt doğrulama, ilgi korelasyonu, EN_IYI, merdiven), `ilk2dk-topla`, `devir`, `bulgu-sinifla`, `sahne-sozlesme`, `vaat-denetim`. Çıkış kodları [MİM]/[ÜRE] ortak sözleşmesine uyar | `_HIKAYE_ODASI/*` → raporlar, `HIKAYE.json` |
| **P0** | `ARACLAR/kor_paket.py` ([MİM] K-13; ortak) — **hikâye kipleri benim tanımım** | `kagit` (aşamalı P0–P3), `ilk2dk`, `plan`; ad + takma ad maskeleme; işitsel döküm biçimi; beyaz liste; zaman kodu tahmini (ZN §2.3). Animatik ve kurgu kipleri aynı maskeleme kodunu kullanır (`izleme_paketi.py` bunu içe aktarır) | `HIKAYE/SENARYO.json` → `GIRDI/P*.md`, `SORULAR.md` |
| **P0** | `ARACLAR/semalar/` | `konu_karti`, `hikaye`, `juri`, `seyirci_rapor` (tek şema, bütün kipler), `seyirci_tur`, `eslesme`, `evren_hikaye` | — |
| **P0** | `ARACLAR/puan_oku.py` v2 (ortak: [MİM] K-20, [KUR]) | Önce JSON, yoksa OZET satırı; medyan; `OZET_P1..3`; KRİTİK/ORTA; eski biçim çalışmaya devam eder | raporlar → karar |
| **P0** | `ARACLAR/istem_denetim.py` (değişir) | Filtre listesini tek kaynaktan okur; **replik metnini** de tarar; `evren.py ne_yok_kelimeleri()` listesini istemlerde arar | `SAHNELER.json` + evren → rapor |
| **P0** | `.claude/skills/film-yap/hikaye_esikleri.json` + ortak `ARACLAR/esikler.py` | §4.7.2 eşikleri; yükleyici bütün eşik dosyalarını birleştirir, çift anahtarı HATA sayar | — |
| **P0** | `sablonlar/` hikâye şablonları + `JURI_TABLOSU.md` | §4.4 | — |
| **P0** | Ajan dosyaları | `hikaye-mimari` güncellenir; `hikaye-yazari`, `juri-uyesi`, `diyalog-editoru`, `ozet-eslestirici` yeni; `habersiz-seyirci` 5 kip ve 6 ölçüt; `yapimci`, `oyuncu` ([MİM] ile ortak) | — |
| **P0** | `testler/test_hikaye.py` + `testler/kaset/hikaye/` | Bkz. aşağıdaki test listesi | — |
| **P1** | `ARACLAR/evren.py` (ortak; hikâye bölümü benim) | `on-kayit`, `hikaye-kaydet --dogrula` (kanon çelişkisi), `ne_yok_kelimeleri`, `bilgi_durumu(karakter, film)`, `izleyici-ozeti` (kurgu seyircisi özetlerinden) | `EVREN/<SERI>/…` |
| **P1** | `hikaye_odasi.py karne` | Film sonunda hikâye kök nedenli bulguları, kâğıt ↔ animatik ↔ kurgu puan farkını ve BAYRAK isabetini ders adayı olarak yazar | → `DERS_DEFTERI` (`rol_etiketi: hikaye`) |
| **P1** | `saglayicilar/claude_api.py` (ortak, [ÜRE] P3) | Başsız mod: aynı şablonlar; `claude-opus-5-5`; `thinking: adaptive`; `output_config.effort: high`; uzun çıktıda akış; JSON aşamalarında yapılandırılmış çıktı + şema; `refusal` denetimi. Anahtar yalnız ortam değişkeninden ya da `AYARLAR/`'dan okunur, yazdırılmaz | görev → çıktı |
| **P2** | `hikaye_odasi.py baslik-denetim` | Kanca cümlesinin 4 öğesi, `baslik_gecmisi` tekrarı | → BAYRAK |
| **P2** | `hikaye_odasi.py cesitlilik` | Öneri dörtlüsü karşılaştırması; ileride yerel metin gömmesi | → `BENZER` |

**Test listesi** (`kaset` ile, ağsız ve kredisiz):
- (a) Ad maskeleme: "Sera" R0004'e kadar görünmez; takma ad ("sister") da maskelenir.
- (b) Aşamalı okuma: P1 kopyalanmadan seyircinin P1'i okuma denemesini `erisim_kapisi` reddeder ([MİM] test düzeneğiyle).
- (c) Medyan: (9, 6, 8) → 8.
- (d) Tek KRİTİK reddi: kanıt satırı kopukluktan sonra ya da maskeliyse betik reddi geri çevirir.
- (e) `juri-topla`: fark ≤ 0,3 → BIRLESTIR.
- (f) NE YOK: "zipper" ve replikteki "sleep" → HATA.
- (g) `bulgu-sinifla`: hikâyede olmayan olgu → `hikaye-yazari`; hikâyede olup planda olmayan → yönetmen.
- (h) `sahne-sozlesme`: yönetmen çıkış kostümünü değiştirirse HATA.
- (i) `film.py` görev zinciri A00–A06 uçtan uca `kaset` + `sahte` ile çalışır ve `HIKAYE.json` üretir (CLAUDE.md görev 7).

### 4.7 Makinenin denetleyeceği eşikler (kaynağıyla)
**Zaman belirsizliği kuralı:** hikâye aşamasında plan yoktur. Zaman kodu `hedef_sure_sn` + ZN §2.3 replik formülünden tahmin edilir.
- Zamana bağlı eşiklerde ±%15 (tahmin) bant kullanılır: bandın açıkça dışında kalan HATA, bant içindeki BAYRAK olur.
- Aynı maddeler plan, animatik ve kurguda gerçek sürelerle yeniden ölçülür ([KUR] §7.1 T0–T3).
- **H** = HATA (geçmez), **B** = BAYRAK.

#### 4.7.1 Mevcut eşiklerden hikâye düzeyinde uygulananlar (yeni sayı yok)

| Madde | Eşik | Sonuç | Kaynak |
|---|---|---|---|
| Film süresi (kart ve jenerik dahil) | 1800–2700 sn; hedef konu kartından | H | RE `film_sure_aralik_sn` |
| Parti oranı / vuruş konumu | 0,30–0,35 / ±0,04 | B | RE `parti_sure_oran_aralik`, `vurus_oran_tolerans` |
| Sahne süresi | ≤ 180 sn | H | RE `sahne_max_sn` |
| Replik bloğu | ≤ 16 kelime (8 sn), ≤ 20 (10 sn) | H | RE `replik_max_kelime_8sn`, `replik_max_kelime` |
| Aynı karakterin art arda bloğu | ≤ 3 | B | RE `monolog_ardisik_plan_max` |
| İlk merak / ilk eylem | ≤ 20 sn / S01'in ilk görülen satırı fiziksel eylem | H / B | RE `ilk_merak_max_sn`, `ilk_eylem_max_sn` |
| Vaat imgesi | ≤ 120 sn | H | RE `vaat_imgesi_max_sn` |
| Kahraman adı sözle | ≤ 120 sn ve ilk görünüşten ≤ 2 sahne | H | RE `kahraman_adi_max_sn`, `ad_ilk_gorunus_max_sahne` |
| Risk sözle / parti başında tazelenme | ≤ 180 sn / ≤ 60 sn | H | RE `risk_sozlu_max_sn`, `parti_basi_risk_tazeleme_max_sn` |
| Parti başında kancaya dönüş | ≤ 20 sn | H | RE `parti_basi_kanca_donus_max_sn` |
| Merak olayları arası boşluk / açık soru sayısı | ≤ 90 sn / 1–5 | B | RE `merak_olay_aralik_max_sn`, `acik_soru_aralik` |
| Soru ömrü / büyük soru kapanınca yeni soru | RE değerleri / ≤ 30 sn | B | RE `soru_omru_max_sn`, `cevap_yeni_soru_max_sn` |
| Parti sonunda açık soru | ≥ 1 | H | ZN Z1 #28 |
| Film sonunda açık seri sorusu | ≤ 2 | B | RE `seri_sorusu_max` |
| Kurulum → kullanım | önce ve ≥ 20 sn; > 600 sn'de hatırlatma | H / B | RE `kurulum_kullanim_min_sn`, `hatirlatma_esigi_sn` |
| Doruk çözümü P1/P2'de kurulmuş / kullanılmayan kurulum | evet / 0 | H / B | ZN Z1 #31–32 |
| Aynı bilginin tekrarı | ≤ 2 | B | RE `bilgi_tekrar_max` |
| Dramatik ironi | parti başına ≥ 1; 30–300 sn | B | RE `ironi_parti_min`, `ironi_sure_aralik_sn` |
| Sahne başına yeni ad / film başına konuşan | ≤ 2 / ≤ 8 | B | RE `sahne_yeni_ad_max`, `konusan_karakter_max` |
| Geri dönüş | ≤ 20 sn, soluk ton işaretli | B | RE `geri_donus_max_sn`, DR |
| Duygu eğrisi kuralları | ZN §1.3 | B | RE `pencere_*`, `duz_cizgi_max_sn`, `ayni_duygu_ardisik_dk_max`, `tepe_oncesi_*` |
| Parti sonu / doruk / en karanlık yoğunluğu | ≥ 8 / ≥ 9 / ≥ 6 | H | RE `*_yogunluk_min` |
| Seri kancası / bölüm sayısı | ≤ 20 sn / ≤ 8 | B | RE `seri_kancasi_max_sn`, `bolum_sayisi_max` |
| Filtre kelimeleri (replik + ekran metni) | 0 | H | DR, `istem_denetim.FILTRE_KELIMELERI`, `YAS_IFADESI` |
| Seyirci: GENEL / ölçüt / KRİTİK / ORTA / eşleşme / ilk 2 dk | ≥ 8 / ≥ 7 / 0 / ≤ 3 / ≥ 0,80 / 3 evet | H | RE `seyirci_*`, `kopukluk_*`, `ozet_eslesme_min`, `ilk2dk_devam_evet_min` |
| Kâğıt turu / sıkılma → kesme / kesme uygulama | ≤ 4 / ≥ 2 seyirci / ≥ %50 | — / B / B | RE `kagit_tur_max`, `sikilma_ortak_isaret_min`, `kesme_turu_oneri` |

#### 4.7.2 Yeni eşikler (`hikaye_esikleri.json`; her anahtarda `deger`, `aciklama`, `kaynak`, `etiket: kaynakli|tahmin`)

| Anahtar | Değer | Sonuç | Kaynak / gerekçe |
|---|---|---|---|
| `sahne_sayisi_40dk` | 45–55 (süreyle oranlanır) | B | ZN §2.4 |
| `replik_toplam_kelime_40dk` | 2.100–2.600 (oranlanır) | B | ZN §2.6 |
| `sahne_degeri_degismeli` | her sahnede `bas ≠ son` | H | ZN §7.2.4 |
| `parti_tek_cumle` | 3/3 dolu, kalıba uygun | H | ZN §7.2.3 |
| `ana_karakter_max` | 4 (yaratık hariç) | B | mevcut `hikaye-mimari` taslağı |
| `mekan_tekrar_eden_max` / `mekan_toplam_max` | 6 / 10 | B | (tahmin); [GÖR] kart yükü + 45–55 sahne (İ13) |
| `kostum_varyant_max_karakter` | 2 | B | (tahmin); her varyant yeni kart ve yüz denetimi |
| `uc_adli_karakter_sahne_parti_max` | 3 sahne/parti | B | (tahmin); ≤ 2 referans kuralı (K3) |
| `ad_hece_max_ana` / `ad_ayrisma` | 2 / ilk harf ve ilk ses farklı, düzenleme uzaklığı ≥ 3 | B | (tahmin); telaffuz ve ASR karışıklığı |
| `ad_tts_wer` | 0 (ad sözcüğünde) | H (kilitten önce, yerelde ölçülür) | [SES] A2; ölçüm `ses_sec.py`; bulutta BAYRAK kalır |
| `ses_kadro_ayrisma` | aynı cinsiyet ve yaş bandında konuşan ana karakter ≤ 2 | B | (tahmin); [SES] B4, S1.5 |
| `ilk_replik_ekranda` | her karakterin ilk repliği ekranda (istisna `gizemli_ses`) | H | [SES] S0.3 ses tanıtım kuralı |
| `gorunus_atfi_kilitli` | replikteki görünüş atfı yalnız `hikaye_baglayici` öğeyle | H | İ9 |
| `replik_tasidigi_zorunlu` | her replikte dolu; her kritik olgunun `ekranda` kaynağı var | H | İ8 |
| `anahtar_olgu_parti` | 8–12 / parti | B | [KUR] (tahmin) |
| `kucuk_guzel_sahne_parti_min` | 1 | B | kullanıcı isteği (BK 2.10); sayı (tahmin) |
| `logline_kelime_max` / `baslik_karakter_max` / `kanca_cumlesi_karakter_max` | 35 / 100 / 60 | B / H / B | (tahmin) / YouTube başlık sınırı (doğrulanmadı) / (tahmin) |
| `vaat_surec_max_oran` | başlık fiilinin süreci ≤ 0,50 | B | (tahmin); ZN §1.2 |
| `short_aday_parti_min` | 1 (30–60 sn, kanca 2 sn) | B | BK 1.8.4, 3.10; sayı (tahmin) |
| `oneri_benzerlik_esigi` | dörtlüden ≥ 3 aynı → BENZER | B | (tahmin) |
| `juri_kazanan_min` / `juri_beraberlik_fark` / `juri_veto_uretilebilirlik` | 8,0 / ≤ 0,3 / medyan < 5 | B / — / H | (tahmin); YR A3–A4 |
| `revizyon_madde_kapanis` | KRİTİK + ORTA %100 uygulandı ya da gerekçeli | H | YR A5, A8 |
| `salinim_dusus` | GENEL ≥ 1 düşerse en iyi sürümden devam | — | (tahmin); B2 P1 v7 6 → v8 5 |
| `doktor_tetik_iyilesme` / `yapisal_tur_alt_esik` | tur 3'te < 0,5 / KRİTİK 0 ve GENEL ≥ 7,5 | — | (tahmin) |
| `tek_kritik_red_kanit` | betikle doğrulanmış kanıt | H | [KUR] §5.9 uyarlaması |
| `ilgi_korelasyon_min` | Spearman ≥ 0,5 | B | [KUR] §7.3 (tahmin) |
| `donen_seyirci` | seri devamında 1, medyan dışı | — | İ2 (tahmin) |
| `zaman_belirsizlik_bandi` | ±%15 | — | (tahmin) |
| `sahne_siniri_durum_esitligi` | S_n çıkışı = S_n+1 girişi; aksi `zaman.atlama` ya da ekranda olay | H | ZN §3.7 #4'ün sahne ölçeği |
| `bilgi_durumu_ihlali` / `kanon_ihlali` | 0 | H | ZN §7.2.5; YR §5 |
| `yonetmen_sahne_sure_sapma` | ±%20 | B | (tahmin); §4.5.3 |
| `kopru_replik_sahne_max` | 1 | B | (tahmin); H15 |
| `butce_sure_kurali` | süre ≤ bütçeye sığan en uzun süre; bakiye bilinmiyorsa 2400 | — | §2.5 (hesap: ZN §2.6 oranı) |

**Kalibrasyon (uydurmamak için):**
- (tahmin) işaretli her eşik ilk iki filmde **yalnız BAYRAK** olarak çalışır; kaynaklı HATA'lar bunun dışındadır.
- Her filmden sonra `karne` hangi BAYRAK'ın plan, animatik ya da kurgu seyircisinde gerçekten sorun çıkardığını (isabet) ve hangisinin
  çıkarmadığını (yanlış alarm) yazar.
- İsabeti yüksek olan eşik HATA'ya yükselir, düşük olan gevşer. Bu değişiklik iki farklı filmde görülen kanıtla ve ders kaydıyla yapılır
  ([ÜRE] §5.8 korkulukları; AR2 §7).

### 4.8 Kesin kararların kendi alanımda uygulanışı

#### 4.8.1 Karar 1 — Kullanıcıya yalnız konu sorulur
- Tek soru H0'daki metindir. Eskiden kullanıcıda olan iki hikâye kararı ekibe geçti:
  - A/B öneri seçimi (B2 ve B3'te kullanıcı seçiyordu; UH §1) → kör jüri + `juri-topla`.
  - Proje kararları (YR A0) → `yapimci` + varsayım defteri.
- Makinede: [MİM] `soru_kapisi` karar sorusunu engeller; `sayaclar.kullaniciya_soru` sayılır.
- Kullanıcı bilgilendirilir ama onaya zorlanmaz: H1'den sonra konu yorumu ve süre, H6'dan sonra 1 sayfa özet, H13'ten sonra 5 satır.
  Kavramlar (soğuk açılış, cliffhanger) bir cümleyle açıklanır (BK 7.13).
- Kullanıcı kendiliğinden itiraz ederse bu bir kesin istek olur ve ilgili aşama yeniden açılır.
- Tükenmiş kapı bir engel bildirimidir, soru değildir (§2.6).

#### 4.8.2 Karar 2 — Atomik eylem zinciri (hikâye tarafı)
Hikâye plan yazmaz, ama zincirin **uçlarını ve ham maddesini** üretir:
1. **Gözlenebilir eylem dili:** EKRAN'da sonuç fiilleri (RE `yasak_sonuc_fiilleri`) ve iç durum fiilleri BAYRAK alır.
   "She prepares to flee" yerine "She stuffs bread into the satchel, slings the rope over her right shoulder". Bu cümleler
   yönetmenin 2–3 adımlı zincirlerine doğrudan bölünür.
2. **Sahne uçları = zincirin uçları:** `giris_durumu` ve `cikis_durumu` [YÖN] durum nesnesinin alt kümesidir. Yönetmenin ilk ve son plan
   durumu bunlarla olgu olarak eşit olmak zorundadır (`sahne-sozlesme`). Sahne arası değişim yalnız ekranda bir olayla ya da `zaman.atlama` ile olur.
3. **Nesnenin her el değiştirmesi ekranda bir olaydır** (8 başlığın 4. maddesi; DR "öteki yumurta", "kömür diski").
4. **Konuşma ile el işi ayrıdır** (ZN §2.3).
5. **İnce el işi** (düğüm, kilit, yazı) `riskli` işaretlenir ve ekleme + tepki ile anlatılabilecek biçimde kurulur (ZN §3.5).
6. **El ve yön** hikâyenin anlamını taşıyorsa (yara sol kolda, yüzük sağ elde) karakter kartına ve sahne ucuna yazılır; ayna yasağı gerektiren
   asimetri baştan bilinir.

#### 4.8.3 Karar 3 — Altı özellik
- **(a) Animatik + habersiz seyirci:**
  - Hikâye odası bütün seyirci turlarının **cetvelini** sağlar: aynı 6 ölçüt, aynı `SORULAR.md`, aynı `anahtar_olgular` ve `MERAK_DEFTERI`,
    aynı maskeleme kodu (`kor_paket.py`), aynı rapor şeması.
  - Kâğıt (8) → plan seyircisi → animatik → kurgu puanları böylece kıyaslanır; "hikâye sağlamdı, görüntü bozdu" ile "hikâye zaten eksikti"
    birbirinden ayrılır.
  - Animatik ve kurgu bulguları `bulgu-sinifla`dan geçer (§2.4).
  - Animatikte kesme turu ([KUR] D11) kurulum zincirini kırarsa, kesilen sahnenin taşıdığı olgu `anahtar_olgular` üzerinden yakalanır.
- **(b) Dünya durumu defteri + zıplama denetimi:**
  - Fiziksel defteri betik plan durumlarından kurar ([YÖN]/[GÖR]/[ÜRE]).
  - Hikâye iki katman ekler: (1) sahne sınırı koşulları (defterin sınır değerleri), (2) **bilgi durumu** (kim neyi biliyor).
    Bilgi durumu görsel değildir ama seyircinin en çok takıldığı kopukluklardan biridir ("bunu nereden biliyor?").
  - `senaryo-denetim` ikisini de denetler.
- **(c) Referansla yüz kontrolü:**
  - Hikâye, kontrolün başarabileceği bir kadro tasarlar: ana karakterler küçük karede de ayırt edilir (`gorsel_ayirt_edici` zorunlu).
  - Olay gerektirmedikçe benzer yaşta ve benzer saçlı ana karakter yoktur; gerekiyorsa `bilincli_benzerlik` yazılır.
  - Karakter başına kostüm varyantı ≤ 2; konuşan ≤ 8.
  - Hikâyeye bağlı görünüş öğesi kilitlidir (İ9).
- **(d) Kare zinciri:**
  - Sürekli eylem akışları `zaman.atlama: "yok"` ile işaretlenir.
  - Uzun kesintisiz akışın ortasına bir ekleme ya da tepki vuruşu konur. Zincir derinliği 2'yi geçince kalite düşer (AR2 §2.3); yeniden
    demirleme noktası hikâyede hazır olur.
- **(e) Kendi kendine öğrenen ders defteri:**
  - Okur: brifing `hikaye` etiketli doğrulanmış dersleri betikle içerir.
  - Yazar: `karne` hikâye kök nedenli bulguları, kâğıt ↔ kurgu puan farkını ve BAYRAK isabetini ders adayı yapar.
  - Hikâye dersi en az 2 farklı filmde görülmeden `dogrulandi` olmaz.
  - Makinece denetlenebilir dersler `hikaye_esikleri.json`'a girer.
  - Yayın verisi (izlenme, tutma) kullanıcı verirse kanıt olarak eklenir; tahminle ders yazılmaz.
- **(f) Kalıcı seri evreni:**
  - H1 okur (seri tespiti); H3 ve H7 için kanon ve NE YOK kaynağıdır; H10 için denetim kuralıdır.
  - H13'te ön kayıt yapılır (kimlik kilidi), H14'te güncellenir.
  - Düzen ve sahiplik §2.7'dedir.

#### 4.8.4 Karar 4 — Ses ve dudak (hikâye tarafındaki gereklilikler)
- Yöntemi ses uzmanı seçer. [SES], [YÖN], [KUR] ve [GÖR] ana yol olarak "Veo konuşur + yerel ses dönüştürme", yedek olarak TTS
  (ağız görünmeyen replik) ve dudak senkronunu öneriyor (AR3 A2); bu seçime katılıyorum.
- Hangi yol seçilirse seçilsin hikâye odası şunları garanti eder:
  1. **Replikler filtre-güvenlidir**, çünkü Veo istemine `X says: "…"` olarak girer.
  2. **Metin dondurulur ve kimliklidir** (`R0011`): WER metin kapısı ve altyazı hizalaması bu metne göre yapılır. `tasidigi` alanı
     "anlam eşdeğer" kabulünün sınırını çizer (İ8).
  3. **`ses_karakteri`** ses kadrocusunun girdisidir. Veo dizesini (≤ 10 kelime, yaş sözcüğü yok) o yazar.
  4. **`teslim`:** replik başına tek teslim; ses seviyesi ([SES] B6) bu sözlükten türetilir. Dönüştürücüler ton geçişinde zorlanır (AR3 A2).
  5. **Telaffuz-güvenli adlar:** 2 heceli, ayrışan adlar; `ad_telaffuz`; kilitten önce TTS + ASR doğrulaması (yerelde).
     Veo yanlış okursa `veo_metin` kullanılır.
  6. **Ses tanıtım kuralı:** ilk replik ekranda. Üst üste konuşma yok; replik ortasında gülme/ağlama yok, duygu ayrı tepki vuruşunda.
  7. **0 kredili köprü:** kilitten sonra bilgi eksikliği Yol B ile ekran dışı köprü repliğiyle kapatılabilir (H15 basamak 2).

#### 4.8.5 Karar 5 — Memmet ve Flow uyarısı
- Hikâye odası Flow'a dokunmaz.
- Dolaylı katkısı: üretilebilir hikâye daha az yeniden üretim, dolayısıyla daha az gönderim ve uyarı riski demektir (DR).
  Üretilebilirlik jürisinin vetosu ve riskli sahne çözümleri bu yüzden kâğıtta zorunludur.
- Hikâye odası hiçbir aşamada "Flow'da dene, bakalım" önermez.
- H15'te 0 kredili basamaklar kredili olanlardan önce gelir.

#### 4.8.6 Karar 6 — Üstün körü iş yok
- Seyirci 3'ün, jüri 5'in, mimar 4'ün altına inmez.
- Tur sınırına "zaman yok" diye erken çıkılmaz; bayraklı devam yoktur.
- Bütün yargı ajanları Opus/high.
- Kullanım sınırında iş durur ve dosyadan devam eder; kısaltılmaz.
- Yazılmış film bütçe için kısaltılmaz (§2.5).
- Kaynaksız sayı yazılmaz; (tahmin) işaretliler kalibrasyon listesindedir.

### 4.9 Riskler, kalan çakışmalar, açık sorular

#### 4.9.1 Riskler ve önlemler

| # | Risk | Önlem |
|---|---|---|
| R1 | **Claude'un Claude'u puanlaması:** puan şişmesi; kâğıtta 8, kurguda 6 (B2 dersi) | Medyan; her tur yeni seyirci; "cömert olma" + puan çapaları (`JURI_TABLOSU.md`); özetsiz kapı seyircisi; sıralı okuma; kâğıt ↔ kurgu farkı karnede; fark sistematik olarak > 1 ise kâğıt eşiği yükselir; çapraz model açık soru (Q2) |
| R2 | **Habersizlik sızıntısı** | Kör paket beyaz listesi; `erisim_kapisi`; aşamalı GIRDI; ad ve takma ad maskeleme; `ekranda_bilgi` ve önceki film özeti verilmez; EKRAN dilinde iç durum fiili BAYRAK |
| R3 | **Maskelemenin kısmi kalması** (lakap, unvan) | `takma_adlar`; seyircinin "adı nereden öğrendin" cevabı R-kimliğiyle karşılaştırılır; uyuşmazlık BAYRAK |
| R4 | **Ölçüt avcılığı (Goodhart):** eşiklere uyan ama ruhsuz hikâye | Yaratıcı eşiklerin çoğu BAYRAK; jüride `ozgunluk`; bonus mimar; seyirci ölçütleri his sorar ("endişelendim mi?") |
| R5 | **Uzun metinde dikkat dağılması** (≈ 50 sahne; AR1 C) | Parti parti sıralı okuma ve parti başına puan; yazar da parti parti yazar |
| R6 | **Zamanın tahmin olması** | ±%15 bant; plan ve kurgu aşamalarında gerçek süreyle yeniden ölçüm ([KUR] T0–T3) |
| R7 | **Yazar örneğinin sürdürülememesi** | `yazar_defteri.md` ("karar — neden — yanlışsa maliyeti"); yeni örnek önce onu okur ([MİM] yarım iş kuralı) |
| R8 | **Kullanım sınırı** (40–75 örnek, tahmin) | Dosya tabanlı devam; paralel çağrılar tek mesajda; kısaltma yok |
| R9 | **Hikâye kalitesi izlenmeyi garanti etmez** (B1 ≈ 671 izlenme; tutma verisi yok) | Kullanıcıya dürüstçe söylenir; format ve kanca veriye göre seçilir ama [H] diye işaretlenir; yayın verisi gelirse ders defterine |
| R10 | **Konu filtreyle çatışıyor** (insan çocuk kahraman) | Konu kartında dönüşüm + bilgi notunda açıkça söylenir (BK 7.13) |
| R11 | **Telif / kanca kopyası** | `donusum`; jüride `ozgunluk`; `baslik_gecmisi`; "hit kopyaları tutmuyor" (BK 1.3.2) |
| R12 | **Hikâye kapısı hiç geçmeyebilir** (geçmişte kâğıt medyanı 7; B3 6/8/7) | Merdiven (en çok ≈ 10 tur); doktor; ikinci öneri; yine olmazsa dürüst durma. İlk iki filmde S1 eşiğinin kurgu sonucuyla ilişkisi karneye yazılır |
| R13 | **Aşamalı okuma için SendMessage ile sürdürmenin** Claude Code'da beklenen gibi çalışmaması | [MİM] §9.4 #3 doğrulamasına eklenir. Çalışmazsa yedek: her bölüm için ayrı görev; seyirci bir önceki bölümün **kendi** raporunu GIRDI'de alır (habersizlik korunur) |
| R14 | **Yönetmen inceltmesinin hikâye ucunu gizlice değiştirmesi** | `sahne-sozlesme` betiği; `_sahip` alanı ([MİM] §5.11) |
| R15 | **Ad doğrulaması bulutta yapılamaz** (AI84 yerelde) | Bulutta BAYRAK; ad değişikliği yerelde, kart üretiminden önce tek görev olarak (ucuz) |

#### 4.9.2 Kalan çakışmalar (ekip kararı gereken)
1. **Klasör adları** (`_HIKAYE_ODASI/` + `_RAPOR/` ↔ [MİM] `20_HIKAYE/` + `RAPORLAR/`): §2.1'deki önerim çoğunluk ve mevcut koddur; son söz mimarinin.
2. **Plan düzeyinde `parti` anlamı** ([YÖN] ↔ [MİM]/[ÜRE]/[KUR]): hikâye `hikaye_partisi` kullandığı için ben etkilenmiyorum; çoğunluğu destekliyorum.
3. **Ajan iş devri çıkış kodu:** [ÜRE] 3, [KUR] 4, [GÖR] 2, [MİM] JSON görev listesi. Tek protokol olmalı; hikâye odası [MİM]'in `film.py sonraki` sözleşmesine uyar.
4. **Ders defteri yeri ve terfi kuralı** ([MİM] `BILGI/DERS_DEFTERI.jsonl`, [ÜRE] `KUTUPHANE/DERSLER/`, [GÖR] ve [SES] `EVREN/…`):
   hikâye yalnız `rol_etiketi: hikaye` ve "≥ 2 film" alt kuralını ister.
5. **`ses.json` yeri** ([SES] `EVREN/SESLER/<id>/` ↔ [GÖR] `karakterler/<id>/`): §2.7'de karakter klasörü önerildi; karar ses ve görüntü uzmanlarının.
6. **Eşik dosyası birleştirme:** `esikler.py` önerisi [ÜRE] ve [YÖN] ile uzlaşılmalı.

#### 4.9.3 Açık sorular
- **Q1 (sürüyor).** Bonus mimara ilk üç önerinin yalnız loglinelarını vermek kabul mü? Bu tur kimse itiraz etmedi; görev defteri bu bağımlılığı destekliyor.
  Önerim: kabul.
- **Q2 (sürüyor).** Jüri ya da seyircilerden birini başka bir model (Gemini) yapmalı mıyız ([MİM] S-4, AR1 B4)? Hatta Gemini metin API'si yok;
  anahtar ve maliyet kurulum kararıdır.
- **Q3 (yeni).** Seri devamında "dönen seyirci" gerçekten bilgi verecek mi, yoksa gürültü mü? İlk seri devamında ölçülür.
- **Q4 (yeni).** Tek seyircinin KRİTİK'ini geçersiz saymayı `yapimci` doktor kipine vermek yeterince tarafsız mı? Alternatif: kanıt yalnız
  betikle doğrulanır, ajan kararı hiç olmaz (kanıtı kim bulacak sorusu kalır).
- **Q5 (sürüyor).** Başlıkta "kill": yayın uzmanı yok; reklam etkisi verisi gelene kadar BAYRAK.
- **Q6 (sürüyor).** Kalibrasyon çapası: B2/B3'ün hikâye metinleri ve seyirci raporları `D:\YZ_FILM_ARSIV\`'de (OB). Depoya alınırsa yeni seyirci
  ajanının puanları eskileriyle kıyaslanabilir (puan şişmesi ölçümü). Yerel oturumda bir kez kopyalanması önerilir; o zamana kadar çapasız başlanır.
- **Q7 (yeni).** `--onayli` modda kullanıcıya hikâye özetinin gösterilmesi isteğe bağlı itiraz penceresiyle mi olsun, yalnız bilgi olarak mı?
  Önerim: yalnız bilgi; itiraz kullanıcının kendi mesajıyla gelir.
- **Kapanan sorular:**
  - Tur 1 Q3 (tavan sonrası) → §2.6.
  - Q4 (süre) → §2.5.
  - Q7 (çocuk kahraman dönüşümü) → H1.
  - Q8 → bu turdaki Q7.
  - Q9 (ajan frontmatter'ında kanca) → [MİM]'in ayar düzeyindeki kancası.

---
*Bu belge senarist uzmanının 2. tur önerisidir. Diğer altı uzmanın tur-1 belgeleri okunarak yazıldı. Sayıların kaynağı satırlarında yazılıdır;
(tahmin) işaretli olanlar §4.7'deki kalibrasyon kuralıyla ilk iki filmde ayarlanacaktır.*
