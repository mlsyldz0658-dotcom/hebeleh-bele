# Tur 2 — Yönetmen uzmanı: itirazlar, çakışmalar, revize nihai öneri

Hazırlayan: yönetmen uzmanı (Claude Opus 5.5). Tarih: 23.10.2026.
Bu turda okunanlar: `tartisma/` klasöründeki yedi tur 1 dosyasının **tamamı** (kendi dosyam dahil) ve onlara dayanak olan
`ZANAAT.md` §2–§3, §6, `ritim_esikleri.json` (anahtarlar betikle listelendi), `BILGI_KURALLARI.md` §8 (21 çelişki),
mevcut `.claude/agents/yonetmen.md`.

**Uzman kısaltmaları:** `[GS]` = `tur1_goruntu-sureklilik.md` · `[KU]` = `tur1_kurgucu.md` · `[SN]` = `tur1_senarist.md` ·
`[SM]` = `tur1_ses-muzik.md` · `[UM]` = `tur1_uretim-muhendisi.md` · `[CM]` = `tur1_claude-code-mimari.md` ·
`[YN1]` = benim tur 1 dosyam (`tur1_yonetmen.md`).
**Kaynak kısaltmaları** tur 1 ile aynı: `ZN` ZANAAT.md · `RE` ritim_esikleri.json · `BK` BILGI_KURALLARI.md ·
`A1/A2/A3` araştırma 01/02/03 · `DR` 03_DERSLER.md · `YR` YAPIM_REHBERI.md · `FK` FLOW_KESIF.md · `H/<ad>` hafıza notu.
**Sayı etiketleri:** kaynağı olan sayının yanında kaynak yazar · `(hesap)` = kaynaktaki sayılardan ya da formülden türetildi ·
`(tahmin)` = kaynağı yok, ilk partide ölçülüp ayarlanacak başlangıç değeri.

### Bu turun özü (5 satır)
1. **Durum yalnız olgudur; kadraj bilgisi ayrı tutulur ve kodla hesaplanır.** Bu, bütün zıplama denetiminin doğru çalışmasının şartıdır (en önemli itirazım).
2. **Kare zinciri, kullanıcının (d) kararıyla aynen uygulanır:** `devam` geçişinde varsayılan, önceki klibin kesme anındaki **gerçek karesidir** (Z1). Bitir karesi (Z2) hedefli kullanılır. Her plan için planlanmış görsel yine üretilir (animatik ve yedek için). Tur 1'deki "Mod A varsayılan" önerimi geri çekiyorum.
3. **Kroki tek dosya, tek yazar:** yönetmen yazar, seri evreninde durur. Kart tasarımcısı onu çevirmez, okur.
4. **`cekim` adını geri çekiyorum:** plan alanları ZN §6.1'deki `zanaat` alt nesnesinde kalır. `sureklilik` alt nesnesi kalkar. Kodun hesapladığı her şey `_derlenir`'e gider. Her alanın tek sahibi vardır.
5. **`plan-yazari` ayrı ajan olmaz:** `yonetmen` ajanının `plan` kipi olur ve sahne grubu başına yeni örnekle çalışır. Ajanda Bash yoktur. Denetim SubagentStop kancasıyla yapılır.

---

## 1. Diğer önerilere itirazlarım (dosya + madde + neden + önerim)

★ işaretli üç madde en önemli itirazlarımdır.

### ★ İ-1 · [GS] §5 "tek doğruluk kaynağı" ve §5.5 · [UM] §8.3-b · [SN] §5.2 — Durum nesnesinin içine kadraj bilgisi yazılması
- **Ne yazılmış:**
  - [GS] `baslangic_durumu.kadrajdakiler[]` içinde `"konum": "sol_ucte_bir"`, `"yon": "kadraj_sagi"` ve el hâli `"gorunmuyor"` var.
  - [UM]'nin `DUNYA_DEFTERI` örneğinde her satırda `"kadraj": "sol_ucte_bir"` var.
  - [SN] sahne girişinde `"sera": "mağara ağzı, sol, diz çökmüş"` yazıyor. Buradaki "sol" kadraj solu mu, mağaranın solu mu, belli değil.
- **Neden yanlış:**
  1. K0 kuralı (ZN Z0 #16, [GS] §7.1) `bitis[N] ≡ baslangic[N+1]` eşitliğini arar. Oysa açı her değiştiğinde kadraj konumu meşru olarak değişir. Örnek, tur 1 kroki hesabı: K2'de Mara sol üçte birde, K5'te kadraj dışında, ters açıda (K3) ön planda soldadır. Bu alanlar durumda dururken karşılaştırma iki şeyden birini yapar: ya her `eylem_kesme`de yanlış HATA verir ya da bu alanları atlar. Atlıyorsa bu alanlar zaten "durum" değildir.
  2. Kadraj konumunu yazar elle yazarsa ≈495 planda aynı bilgi açı başına yeniden yazılır. [GS] R10'daki "yazım yorgunluğu" riski artar. Asıl sorun da şu: elle yazılan konum geometriyle çelişebilir ve bunu yakalayacak bir kaynak kalmaz.
  3. `gorunmuyor` bir el **hâli** değildir. Elin kadrajda görünüp görünmemesi kameraya bağlıdır. Aynı el bir sonraki açıda görünür. Bunu durumda tutmak da yanlış zıplama üretir.
- **Önerim:**
  - **Olgular** (kameradan bağımsız) durumdadır: işaret, poz, dünyaya göre yüz yönü, bakış hedefi, eller (`tutar / yer / sekil`), nesneler, kostüm ve görünüm, mekân öğesi durumları.
  - **Kadraj** planın `zanaat.kadrajdakiler[]` listesindedir: kim kadrajda, ölçeği, yüz açısı, görünen parçalar.
  - Kadraj konumu, kadraj sırası, bakışın kadrajdaki yönü, ışığın kadrajdaki yönü ve ekran yönü `kroki.py` ile **hesaplanır** ve `_derlenir` alanına yazılır.
  - G1 başlangıç karesini olgulara ve `_derlenir`'e karşı ölçer. Hikâye odasının sahne uçları da aynı olgu şemasının alt kümesidir (Ç-9).

### ★ İ-2 · [UM] §2.2 V05 ve §8.3-d (ayrıca kendi [YN1] §8.2-d'm) — Kare zincirinde `bitis_karesi` varsayılanı ve `son_kare` planlarına önceden görsel üretilmemesi
- **Ne yazılmış:**
  - [UM]: "`zincir.yontem = son_kare` olan planlar burada üretilmez." `bitis_karesi` (planlanan görsel, Bitir yuvasında) `devam`da varsayılan.
  - Ben de tur 1'de aynı varsayılanı (Mod A) önermiştim.
- **Neden yanlış:**
  1. **Kesin karar 3(d) sözcüğü sözcüğüne şunu söylüyor:** "son kare → sonraki klibin başlangıcı". Planlanmış bir görseli bitiş karesi olarak dayatmak bu kararın kendisi değil, ona benzeyen başka bir yöntemdir. Kullanıcı kararı tartışılmaz; tartışılacak olan yalnız nasıl en iyi uygulanacağıdır.
  2. Gerçek son kare, Veo'nun klip içinde kendiliğinden ürettiği her şeyi (ışık kayması, arka plan ayrıntısı, tam poz) piksel düzeyinde taşır. Planlanmış görsel bunları taşımaz. Bitir yuvası ise iki görsel arasında morf riski taşır ([YN1] R3, [GS] R5).
  3. Bedel kalite değil **süredir**: zincir ≤ 3 dalga sürer ([GS] A11, [UM] §8.3-d). Kesin karar 6 ("tasarruf için kaliteden ödün yok") bu takası açıkça belirler. Flow temposu zaten darboğaz olduğu için ([UM] §1.3: ≈13 saat (hesap)) ek gecikme dalga sayısıyla sınırlı kalır.
  4. `son_kare` planına önceden görsel üretilmezse iki şey olur. (a) Animatikte bu planlar delik kalır; [KU] K3'ün "yer tutucu ≤ %10" (tahmin) sınırı, `devam` planı çok olan aksiyon sahnelerinde aşılır. (b) Zincir karesi G1'den geçemezse düşülecek bir yedek kalmaz ([GS] A15 "Z0'a düşer" ancak yedek varsa çalışır).
- **Önerim (§4.8-d'de tablo hâlinde):**
  - `devam` geçişinde **Z1 gerçek kesme karesi varsayılandır**.
  - **Z2 (Bitir)** iki durumda kullanılır: (1) önceki klipte durum değiştiren kritik bir adım varsa, (2) V3'te bitiş durumu tutmadıysa, yeniden çekimde.
  - **Her plana planlanmış görsel üretilir.** Z1 planları için bu görsel animatikte ve yedek olarak kullanılır.
  - Doğrudan bitişik zincir yalnız eylem doğal olarak duruyorsa kurulur. Diğer durumlarda zincir bir araya kesme planıyla örtülür (Y54).

### ★ İ-3 · [GS] §2.2 A2, §5.3 `mekan.json`, §9.2 — Krokinin kart tasarımcısı tarafından yönetmen haritasından "çevrilmesi" ve 4 noktalık kroki
- **Ne yazılmış:** "Kroki koordinatlarını `kart-tasarimcisi` yönetmenin parti haritasından `mekan.json`'a çevirir." Örnek krokide yalnız `noktalar: {kapi, ocak, pencere, masa}` var.
- **Neden yanlış:**
  1. Çeviri, aynı geometrinin ikinci kopyasıdır. Her kopya zamanla ayrışır ([YN1] §5.2 ilkesi, A1 B2 drama-skills "her belge yalnız kendi kararlarının sahibi").
  2. Dört noktalık krokiyle şu denetimler **hesaplanamaz**: görüş hattı (duvar arkasını görme, Y14), ışığın kadrajdaki yönü (Y23), göz yüksekliği ve bakış eğimi (Y25), oyuncu işaretlerinden kadraj sırası (Y28), kurulum çiftleri arası açı farkı (Y19). Bunun için duvarlar, açıklıklar, öğe yükseklikleri, işaretler ve ışık kaynakları gerekir.
  3. Oyuncu ve kamera yerleşimi (blocking) bir yönetmenlik kararıdır. Kapının ocağa göre nerede olduğu, karşılıklı çekimin hangi duvara bakacağını belirler.
- **Önerim:**
  - `EVREN/<SERI>/mekanlar/<id>/kroki.json` dosyasını yalnız yönetmen yazar (şema §4.5.4).
  - Görüntü tarafının `mekan.json` dosyası bu dosyayı **okur**. Kendisi tarifi (`tarif_en`), nötr durumu ve plaka görsellerini taşır.
  - Plakaların (mekân kartlarının) konumunu ve yönünü kroki belirler. Plakada görünmesi gereken öğe listesini `kroki.py` hesaplar ve kart istemine verir. Kart tasarımcısı koordinat yazmaz.

### İ-4 · [UM] §2.1 K06 — "yonetmen (parti başına 1 çağrı)"
- **Neden yanlış:** Bir parti ≈165 plandır (RE `hedef_plan_parti`). Plan başına ≈1–1,5 bin token ile bu, tek çağrıda ≈165–250 bin token çıktı eder (tahmin). Bu kadar çıktı tek çağrıda güvenilir biçimde üretilemez (tahmin; [CM] §3.3 de "495 planı tek çağrıda yazmaya kalkıyor (çıktı sınırı)" diyor).
- **Önerim:** Parti başına bir **harita** görevi (sahne sözleşmeleri, krokiler, kurulumlar), ardından **sahne grubu başına** bir plan görevi ([CM] A07a/A07b ile aynı). Sınırlar sözleşmeyle sabitlendiği için plan görevleri paralel çalışabilir.

### İ-5 · [KU] §5.2 ve [GS] §5.5 — Aynı çıkış noktasının üç yerde tutulması
- **Ne yazılmış:** `kullanim: {bas: 0.5, sure: 5.5}`, `zanaat.sure_sn: 5.5` ve `zanaat.kesme.nokta_sn: 5.6` ([KU] örneğinde 0,5 + 5,5 = 6,0 ≠ 5,6: kopyalar daha ilk örnekte ayrışmış).
- **Önerim:**
  - Planlanan kırpmanın **tek** yazılan alanı mevcut `kullanim {bas, sure}`'dir (Memmet ve capcut_film bu alanı zaten tanıyor).
  - `sure_sn` ve `kesme.nokta_sn` `_derlenir` alanına hesaplanır.
  - Ölçülen gerçek değerler yalnız `KURGU_PLANI.json`'a yazılır ([KU] §2.1'e katılıyorum).

### İ-6 · [GS] §5.5, [SM] §5.1, ZN §3.7 — Eylem adımı örneklerinin atomik zincir kuralını kendisinin çiğnemesi
- **Ne yazılmış:**
  - [GS]: `{"bas": 0.0, "fiil": "walk", "govde": "iki_adim", "yon": "kadraj_sagina"}`.
  - [SM]: `{"bas": 0.0, "fiil": "lowers", "hedef": "clay cup onto table", "govde": "both hands"}`.
  - ZN §3.7: "takes two slow steps". `take`, RE `yasak_sonuc_fiilleri` listesinde.
- **Neden yanlış:**
  - 0,0'da başlayan adım, Veo klibinin ilk 0,3–1,0 sn'lik durağan bölümüne düşer (ZN §2.2, RE `kullanim_bas_varsayilan_sn`).
  - Serbest metin fiil sözlükle denetlenemez.
  - Kadraja göre yön ("kadraj_sagina") yazarın elinde açıya bağlı bir hata kaynağıdır.
  - `etki` alanı yoksa bitiş durumu hesaplanamaz ve yazar onu elle yazmak zorunda kalır.
- **Önerim:** Adım şeması §4.5.8:
  - Sözlükteki `fiil` id'si ve fiilin zorunlu parametreleri
  - Karakterin kendi sağı/solu
  - Hedef (varlık, nesne, işaret)
  - `etki`
  - Kalıcı `id` (`a1`, `a2`…; ses ve kurgu adıma bu id ile bağlanır)
  
  ZN §3.7'deki örnek "walks two slow steps" olarak düzeltilmeli.

### İ-7 · [GS] §5.5 `sureklilik.kadraj_sirasi` ve `hareket_yonu`
- **Neden yanlış:**
  - Kadraj sırası işaretlerden ve kurulumdan hesaplanabilir. Yazarın elle yazması İ-1'deki ikinci kopya sorununu doğurur.
  - `hareket_yonu` adı benim `kamera.hareket_yonu` alanımla (kameranın kayma yönü) çakışıyor.
- **Önerim:**
  - Kadraj sırası `_derlenir.kadraj_sirasi` olur ve yazılmaz.
  - Öznenin ekrandaki hareket yönü ZN §3.3'teki adıyla `ekran_yonu` olur. Sahnenin hedef ekran yönü sahne alanında yazılır, planınki `_derlenir.ekran_yonu`'ya hesaplanır. V2 denetimi ([GS] §7.6 "kişi kutusu x merkezi") bu alanı okur.

### İ-8 · [CM] §3.1 madde 3 ("hiçbir ajanda Bash yok") ve A07a "parti haritası"
- **Bash konusu:** Katılıyorum, ama bir uyarlama gerekiyor. Tur 1'de (R4) krokide koordinat yazmanın zor olduğunu, `kroki.py --karsilikli` aracının ajana standart karşılıklı çekim kurulumları **önerdiğini** yazmıştım. Ajanda Bash yoksa bu öneriler ajan çağrılmadan önce **betikle hesaplanıp GIRDI'ye konmalıdır**. Kroki ve plan denetimi de SubagentStop kancasında çalışmalıdır: HATA varsa durma engellenir, hata listesi ve yeniden çizilmiş kroki PNG'sinin yolu ajana geri verilir, en çok 2 kez.
- **Parti haritası konusu:** Kroki parti başına değil **mekân başına** tektir; mekân partiler ve filmler boyunca aynı kalır. Bir mekânın krokisi ilk kullanıldığı partide yazılır. Sonraki partiler onu yalnız okur. Değişiklik yeni sürüm demektir ve etkilenen sahneler yeniden denetlenir.

### İ-9 · [SM] §5.1 — `ekran_disi_ses`, `dinleyen_agiz`, `agiz_gorunur`, `efektler[].adim: 0`
- **Neden yanlış:**
  - `dinleyen_agiz` ve `agiz_gorunur`, `ekran_disi_ses`, kadraj ve yüz açısından türetilebilir; ayrıca yazılırsa ikinci kopya olur.
  - `ekran_disi_ses` hem plan üst düzeyinde ([SM]) hem `zanaat` içinde ([YN1]) önerilmiş.
  - `adim: 0` dizin numarasıdır. Adım eklenince ya da silinince efekt yanlış adıma kayar.
- **Önerim:**
  - `zanaat.ekran_disi_ses = {replik, karakter, kaynak: "plan:<no>" | "tts", bas_sn, sure_sn}`.
  - `agiz_gorunur` ve `dinleyen_agiz` `_derlenir` alanına hesaplanır, ses aracı okur.
  - Efekt adıma `adim: "a1"` biçimindeki kalıcı id ile bağlanır.

### İ-10 · [KU] §5.2 `kurgu.ayna_yasak` ve §5.5 0 kredi merdiveni #6 "Ayna"
- **Neden:** Görüntü aynalanınca elde tutulan nesne öbür ele geçer (fener sağ elden sol ele). Bu, dünya defterine göre bir el zıplamasıdır (Y16 HATA). Kostüm ve yüz asimetrisi de aynı riski taşır (ZN §3.3).
- **Önerim:** `_derlenir.ayna_yasak` alanı kodla hesaplanır: görünen herhangi bir karakterde elde nesne varsa, evren kartında `asimetrik` öğe varsa ya da sahnede yazı/levha varsa `true` olur. Kurgu ve G1 bu tek alanı okur, kendi kopyalarını tutmaz.

### İ-11 · [KU] §5.5 #2 (sahne içi sıra), #10 (planı kes) ve [CM] A16 — Sıra değişince defterin hangi durumla yeniden koşacağı
- **Sorun:** `baslangic_durumu: "miras"` her çalıştırmada önceki planın bitişinden çözülür. Kurgucu 43 ile 44'ün yerini değiştirince miras yeni komşudan gelir. Oysa 44'ün görseli ve videosu eski komşunun durumuyla üretilmiştir. Bu durumda defter "temiz" der ama ekranda zıplama vardır.
- **Önerim:** **Durum dondurma.** Bir planın görseli üretildiği anda çözülmüş başlangıç ve bitiş durumu `uretim.durum_dondu`'ya yazılır (özetiyle birlikte). Kurgu sonrası sıra ve kesme denetimi bu dondurulmuş durumlarla yapılır (Y58). Planın durumu sonradan değişirse görseli `bayat` olur ([UM] §2.0'daki `bayat` mekanizmasıyla aynı).

### İ-12 · [SN] §5.2 `replikler[].ton`, [SM] `replik.ton_fiili` ve [YN1] adım `teslim`
- **Sorun:** Aynı bilgi üç adla, iki yerde öneriliyor.
- **Önerim:** Tek alan `replik.ton_fiili` olsun (değerler zaten fiil: "says coldly"). Sahibi senarist, `seviye` ise ses uzmanının. Tur 1'deki `teslim` alanımı kaldırıyorum. Konuşma adımı repliği `replik` id'siyle anar ve tonunu oradan alır.

### İ-13 · [UM] §8.2 `govde: {el, parmak: "basparmak+isaret", acik: 2}` ve [GS] §5.5 el hâli birleşik dizgeleri
- **Sorun:** Serbest `parmak` dizgesi ve `uzanmis_parmaklar_anahtarin_10cm_ustunde` gibi parametreli birleşik dizgeler sözlükle denetlenemez. G1 sorusu da bunlardan üretilemez.
- **Önerim:** El üç alana ayrılır: `tutar` (nesne id), `yer` (sözlük ya da öğe/nesne id), `sekil` (sözlük). `sekil` sözlüğünde her şeklin açık parmak sayısı tanımlıdır (`kiskac` → 2, `yumruk` → 0 …). Bu sayı `_derlenir.acik_parmak` olarak G1'in "kaç parmak açık" sorusuna gider ([CM] §5.9 soru q6).

### İ-14 · [SN] §9.2-1 — Sahne bölme kuralı ve süre payı (kabul edip sınırını belirliyorum)
- **Önerim:**
  - Hikâye sahnesi ile sahne grubu **1:1** eşleşir. Süre payı ±%20'dir ([SN] önerisi; tahmin).
  - Bölme ya da birleştirme gerekiyorsa senariste `YENIDEN_YAZ` maddesi gider, yönetmen kendisi bölmez.
  - **Tek teknik istisna:** `sahne_max_sn` 180'i aşan sahne (RE). Ekran metni değişmeden `S12a/S12b` diye bölünür, hikâye kimliği korunur ve senariste bildirilir (soru değil, bilgi).

---

## 2. Çakışmalar ve önerdiğim çözüm (alan adları, aşama sırası, sorumluluk sınırları)

### 2.1 Alan adları ve yerleri

| # | Çakışma | Taraflar | Önerdiğim çözüm |
|---|---|---|---|
| Ç-1 | Plan alt nesnesinin adı | [YN1] `cekim` · ZN §6.1, [GS], [KU], [SM] `zanaat` · [GS], A2 `sureklilik` | **`zanaat`** kalır (`cekim`'i geri çekiyorum). `sureklilik` alt nesnesi **kalkar**; alanlarının yeni yerleri §4.5.3 eşleme tablosunda. Kodun hesapladıkları plan üst düzeyinde **`_derlenir`**'dedir. Yürütme bilgileri `uretim`'de, kapı sonuçları `denetim`'dedir. Kurgucunun kendi küçük `kurgu` nesnesinde yalnız `kirpma_onceligi` kalır |
| Ç-2 | Sahiplik birimi | [YN1] alt nesne başına · [CM] §5.11 alan başına (`_sahip`) | **Alan başına sahip.** `zanaat` içinde hikâye alanları (`vurus`, `merak_*`, `kurulum`…) senaristindir, plan alanları yönetmenindir, `zanaat.ses` ses uzmanınındır. Tablo §4.5.2'de. [CM]'nin `plan_birlestir` aşamasındaki sahiplik denetimi bu tabloyu okur |
| Ç-3 | Durum nesnesinde karakterlerin anahtarı | [YN1] `varliklar` · [SN], [GS] `karakterler` | **`karakterler`** (yaratık ve figüran da bu anahtarın altında, evren kartındaki `tur` alanıyla ayrılır) |
| Ç-4 | Ellerin yazılışı | [YN1] `sol_el/sag_el{tutar,yer,sekil}` · [GS] `eller.sag{tutar,hal}` · [UM] `govde{el,parmak,acik}` | **`eller: {sag: {tutar, yer, sekil}, sol: {…}}`**. Açık parmak sayısı `sekil`'den türetilir (İ-13) |
| Ç-5 | Defter aracı ve dosyası | [YN1] `durum_defteri.py` · [GS] `sureklilik_defteri.py` · [UM] `dunya_defteri.py` · [CM] `dunya_durumu.py` / `DUNYA_DURUMU.json` | **Tek araç `dunya_defteri.py`**, dosyası **`DUNYA_DEFTERI.json`** (dört uzmandan üçü bu adı kullanıyor). **Sahibi süreklilik uzmanıdır.** Durum çözüm kuralları (miras, fark, etki, sözleşme, dondurma) benim şartnamemdir (§4.5.13). Geometri modülü `kroki.py` kütüphane olarak içe alınır. Z0 #16 ile K0 **aynı fonksiyonu** çağırır ([GS] §9.2 ile aynı fikir) |
| Ç-6 | Zincir bilgisinin yeri | [YN1] `cekim.zincir` · [GS] `sureklilik.zincir`, `bitis_sabitle` · [UM] `uretim.zincir.yontem` | **Niyet** `zanaat.zincir`'dedir: `gecis_turu`, `onceki_plan`, `baslangic`, `ebeveyn`, `bitis_sabitle`; yönetmen yazar. **Yürütme** `uretim.zincir`'dedir: `dalga`, gerçek `kaynak`, `kesim_sn`, `derinlik`, `yedege_dustu`; `kare_zinciri.py` ([GS]) yazar |
| Ç-7 | Geçiş türü sözlüğü | [GS] `yeni_sahne / kesme_ayni_mekan / devam` · [YN1] 6 değer | [YN1]'in 6 değeri kalır: `yeni_sahne, eylem_kesme, devam, kurulum_donusu, araya_kesme, zaman_atlama`. Kamera ağacı ve K1 eşiklerinde (`kurulum_donusu` → ana kareye DINOv2 ≥ 0,70, A2 §6.2) bu ayrım gerekiyor. [GS]'nin `kesme_ayni_mekan` sınıfı, `devam` ve `yeni_sahne` dışındaki türlerin birleşimi olarak kodla türetilir |
| Ç-8 | `parti` anlamı | [YN1] plan `parti` = 20'lik üretim bloğu · [UM] C6, [CM] Ç-6, [KU] D4 `parti` = hikâye partisi | **Çoğunluğa katılıyorum:** plan `parti` = hikâye partisi (1–3). `uretim_blogu` (20'lik blok) betikle hesaplanır, `gemini_paketi` 30'luktur, `izleme_parcasi` 240–300 sn'dir. BK §8 #14'teki çelişki böylece kapanır. Memmet'in `parti` okuması üretim uzmanının değişikliğidir |
| Ç-9 | Sahne giriş ve çıkış durumu | [SN] kaba (`yer`, `kostum`, `yara`, nesne dizgeleri) · [YN1] tam şema | Aynı durum şeması kullanılır. Hikâye uçları **alt küme** olarak yazılır: `yer` serbest ad, eller yalnız `tutar`. Yönetmen sözleşmesi bu uçları içerir ve tamamlar. Makine **olgu alt küme eşitliğini** denetler (Y57). Hikâyenin `bilgi` (kim neyi biliyor) katmanı yalnız hikâye katmanında durur, plan durumunda yoktur |
| Ç-10 | `ton` / `ton_fiili` / `teslim` | [SN], [SM], [YN1] | `replik.ton_fiili` (İ-12) |
| Ç-11 | Ekran dışı ses ve dudak alanları | [SM] üst düzey + `ses.diyalog.*` · [YN1] `cekim.ekran_disi_ses`, `replik_kaynagi` | `zanaat.ekran_disi_ses` (İ-9). Tur 1'deki `replik_kaynagi` alanımı kaldırıyorum: konuşma adımı varsa söz bu klipte demektir, `ekran_disi_ses` varsa söz başka yerden gelir. **Ses yolunu** (A / B / L_tasma / Y2) ses uzmanı `zanaat.ses.diyalog.yol`'da seçer |
| Ç-12 | Adım ↔ efekt / kesme bağı | [SM] `adim: 0` · [KU] `kesme_cikis.adim: 2` | Adımın kalıcı `id`'si: `a1…a3` |
| Ç-13 | Mekân kamera konumları ile sahne kurulumları | [GS] `mekan.json → kamera_konumlari.K1..K4` (plaka) · [YN1] `kurulumlar.K1..Kn` | İki ayrı düzey ve iki ayrı ad: **mekân düzeyi `plakalar.<id>`** (boş mekân kartı açıları; EVREN'de; id bakış yönüyle, ör. `ic_guneye`) ve **film düzeyi `kurulumlar.K<n>`** (sahne kamera konumları). Kamera ağacında kök plakadır: `ebeveyn: "plaka:ic_guneye"` |
| Ç-14 | `kroki` yeri ve sahibi | [GS] `mekan.json` (kart tasarımcısı) · [YN1] film `mekanlar.<id>.kroki` · [SN] `b6_mekan` notu | `EVREN/<SERI>/mekanlar/<id>/kroki.json` → yönetmen · `mekan.json` → görüntü ve kart · `ses.json` → ses ([SN] §9.2-4'teki "sahip başına ayrı dosya" önerisiyle aynı). [SN]'nin kroki notu bu dosyanın **girdisidir** |
| Ç-15 | Stil eki | [YN1] film düzeyi, yönetmen · [GS] `dunya.json`, [CM] "evrende olmalı" | **Seri evreninde** (`EVREN/<SERI>/dunya.json → stil_eki`, sahibi görüntü uzmanı). Seri boyunca sabit kalması süreklilik için daha iyidir. İçinde ışık ifadesi yasaktır (BK §8 #12) |

### 2.2 Araç sahipliği

| # | Çakışma | Önerdiğim çözüm |
|---|---|---|
| Ç-16 | `istem_derle.py`: [YN1] tamamı · [GS] `--gorsel` · [CM] ve [UM] `istem-muhendisi` kaldırılsın | Tek araç, iki modül. `--hareket` modülü **yönetmenin**: saniyeli adımlar, fiil sözlüğü şablonları, `veo_ses_tarifi` ile `flow_sound` eklenmesi. `--gorsel` modülü **görüntü uzmanının**: anlık görüntü, kimlik dizesi, referans seçimi. İki modül de aynı alanları ve aynı `plan_sozlukleri.json`'u okur. `istem-muhendisi` ajanı kalkar. Görsel CORRECTION cümleleri `duzeltme.py` şablonlarıyla üretilir ([GS]). Plan değişikliği gerektiren onarım `yonetmen onarim` kipine gider ([CM]) |
| Ç-17 | Durum soruları: [YN1] `durum_sorulari()` API · [GS] `kor.py` · [CM] soru formu | **Soru üretimi `kor.py`'dedir** ([GS]). Benim katkım: `_derlenir.gorunmesi_gerekenler` (kadrajda görünen kişiler, eller, nesneler) ve `kadrajdakiler[].yuz_acisi` (görüntüdeki sol/sağın kişinin kendi sol/sağına çevrilmesi için gereken bilgi) |
| Ç-18 | Video sonrası zincir ölçümü: [YN1] `zincir_olcum.py` · [GS] `video_denetim.py --klip` V3 · [KU] `kirp_oner.py` adım eşleme | `zincir_olcum.py`'yi **geri çekiyorum**. V3, [GS]'nin aracıdır. Benim katkım iki ölçü: adım penceresinde kare farkı enerjisi tepesi (Y-ölçü §4.7.8) ve bitiş anının `_derlenir.kesme_nokta_sn` olarak tanımı. Planlanan ve ölçülen adım eşlemesi [KU]'nun `kirp_oner.py`'sindedir |
| Ç-19 | Paket hazırlayıcı: [YN1] `yonetmen_paket.py` · [CM] `dilim.py` + `_GOREV/<id>/GIRDI` | **[CM]'nin `dilim.py`'si.** Yönetmen dilimlerinin **içeriği** benim tanımımdır (§4.2 Y1 ve Y3 girdileri) |
| Ç-20 | Ders defteri biçimi: [GS], [UM], [CM], [KU], [SM] beş farklı biçim | Bu benim alanım değil. [UM] ve [CM]'nin ortak biçimi (tek olay tek kayıt, terfi kuralı) kullanılmalı. Benim katkım `plan_ozellik.py`: her olaya plan özellik vektörünü ekler (kadraj, açı, hareket tipi, fiil, el şekli, referans sayısı, geçiş türü, başlangıç kaynağı, Z2, ışık türü). Ders türlerim §4.8-e'de |
| Ç-21 | Rapor klasörü (`_RAPOR/` ile `RAPORLAR/`) ve çıkış kodları (ajan işi: [GS] 2, [UM] 3, [KU] 4) | Orkestratör sahibinin ([UM] ve [CM]) tek kararı geçerlidir. Benim araçlarım ayardan okur. Öneri olarak [UM]'nin 0–7 tablosunu destekliyorum |

### 2.3 Aşama sırası (benim alanımın çevresi)
```
[SN] H13 hikâye kilidi (HIKAYE.json)
 → Y0 yönetmen brifingi (betik)
 → Y1+Y2 parti haritası: sözleşmeler + krokiler + kurulumlar (yonetmen harita kipi; 3 parti paralel olabilir)
      └→ KART_ISTEGI.json → [GS] A2 kart tarifleri (paralel başlayabilir)
 → Y3 sahne grubu planları (yonetmen plan kipi; paralel; SubagentStop denetimi)
 → Y4 birleştir + dunya_defteri (K0) + kroki + Z0 + [KU] T0 zaman çizelgesi (betik)
 → Y5 kâğıt plan denetimi: plan-elestirmeni ∥ uretilebilirlik-denetcisi ∥ sureklilik-denetcisi (kagit)
 → Y6 plan seyircisi ([UM] K11, [CM] A07d)
 → [SM] A4–A7 ses kâğıtta (efekt adım id'leriyle, flow_sound, ses yolu)
 → Y7 istem derleme (--hareket + --gorsel) + istem_denetim
 → Y8 kamera ağacı: görsel üretim sırası (plakalar → ana kareler → türevler → devam planlanmış görselleri)
 → [GS] görsel + G1 → [KU] animatik ⟲ → [UM] bütçe → video dalgaları (Z1) → V1/V2/V3 → kurgu ⟲
 ↑______ Y9 dönüşleri (yonetmen onarim kipi): animatik, G1 kaçışı, V3, kurgu yeni planı, filtre reddi ______|
```
- **Neden ses kâğıtta Y6'dan sonra, Y7'den önce:** `hareket_istem` içindeki `Sound:` cümlesi ses uzmanının `flow_sound` alanından gelir ([SM] §5.1). Ses tasarımı da bitmiş eylem zincirine (adım id'lerine) ihtiyaç duyar. Plan seyircisi sesi beklemez: duyulan replik ve ekran dışı ses plandan zaten bilinir.

---

## 3. Diğerlerinden kabul edip kendi önerime kattıklarım

**[GS] görüntü-süreklilik**
- K0'ın **kalıcı özellikleri** (yara, kir, ıslaklık, kostüm hasarı, taşınan nesne) sahne sınırında taşıma kuralı. Gün saatinin geri gitmesi HATA'sı. Durum şemasına `gorunum: {kir, islak, yaralar}` eklendi.
- **Z0 / Z1 / Z2** terimleri ve yöntemleri. `devam` planları için de planlanmış aday görsel üretilmesi (animatikte yer tutucu ve yedek olarak).
- Zincir derinliği ≤ 2; 3. halkada temiz görselle yeniden demirleme. Yeniden demirlenen kare ile zincir karesi arasında DINOv2 ≥ 0,90 (tahmin).
- Zincir karesinin kesme çevresindeki pencereden **en durgun ve en keskin** kare olarak seçilmesi.
- G1'in iki CORRECTION turundan sonra **kaçış** adımı: kök nedeni süreklilik denetçisi yazar, planı yönetmen değiştirir. Bu, benim Y9-b dönüşüm oldu.
- Kart adayları arasındaki sanatsal seçimi `yonetmen` ajanının yapması (`kart_secimi` kipi).
- Konuşan planda başlangıç karesi şartları: yüz yüksekliği karenin ≥ %12'si (tahmin), |yaw| ≤ 45° (tahmin). Y32'ye eklendi.
- "Kimliği yalnız sırttan taşıyan plan" sayısını azaltma uyarısı. Bu, Y44 "kimlik demiri" kuralımı destekliyor.
- "Ölçülemedi" sonucunun asla GEÇ sayılmaması. Benim hesaplarım için de geçerli: kroki eksikse sonuç `HESAPLANAMADI` olur ve HATA sayılır.

**[KU] kurgucu**
- **Planlanan / ölçülen ayrımı:** `SAHNELER.json` neyin üretileceğini, `KURGU_PLANI.json` neyin kullanıldığını söyler. `kullanim_kilit: "zincir"` ile Z1 kaynağı olan klibin çıkış noktası kilitlenir.
- **Animatikteki eylem şeridi = eylem zincirinin kendisi.** Şeridin Türkçe metnini benim `plan_dili.py` derleyicim üretir (§4.6). Bu metin istemle aynı kaynaktan çıkar.
- Kesme simülasyonunda dünya defterinin yeni sırayla yeniden koşması. Buna durum dondurma eklendi (İ-11, Y58).
- `yeni_plan_iste.gereksinim`: kurgucu **ne ve neden** gerektiğini söyler, yönetmen **nasıl** çekileceğini yazar.
- Senkron korumalı klip bölme formülü: `parca2.kullanim.bas = parca1.kullanim.bas + parca1.sure + aradaki_planlarin_suresi`. Bu formül Y39'a eklendi.
- Ölçülen ve planlanan adım sürelerinin ders defterine yazılması. Örnek: "Veo `yurur` adımını kaç kat uzun oynatıyor?" Bu veri `fiil_sozlugu.json → sure_carpani` alanını kalibre eder.

**[SN] senarist**
- Hikâye sahnesi = sahne grubu (1:1); süre ±%20; bölme ve birleştirme senariste döner (İ-14).
- **Replik metnine dokunulmaz.** Yönetmen yalnız böler ve zamanlar (L/J kesme, ekran dışı). Konuşma adımı `replik` id'sini ve `cumleler` aralığını anar (Y59).
- Plan düzeyindeki `ekranda_bilgi` alanlarının birleşimi, sahne düzeyindeki `seyirci_ogrenir` alanını karşılar.
- EKRAN bloğunda yalnız gözlenebilir eylem yazılır; sonuç fiilleri BAYRAK alır. Bu, yönetmenin atomik zincirinin ham maddesidir.
- `zaman.atlama: "yok"` ile işaretlenen sürekli eylem akışları ve sahne içi doğal **yeniden demirleme noktaları**. Bunlar Z1 ve örtülü devam için doğal yerlerdir (Y54).
- `b6_mekan` kroki notu, krokinin girdisidir.
- **İç durum fiilleri yasak** (realizes, decides, knows). Fiil sözlüğünde böyle bir fiil yoktur; `ekranda_bilgi`'de de BAYRAK alır.

**[SM] ses-müzik**
- `replik.ton_fiili`, `seviye`, `veo_metin` (adın okunuşa göre yazılmış hâli; istem bunu kullanır, altyazı kullanmaz).
- Konuşan klipte `veo_ses_tarifi` istemde kelimesi kelimesine yer alır. Hareket istemi kalıbı: `<Ad> says coldly, in a low, warm, slightly husky female voice: "…"`.
- Adım başına bir efekt olayı; efekt adıma `id` ile bağlanır.
- Konuşmalı planda fiziksel adımın efekti ilk sözden ≥ 150 ms önce biter ([SM] S0.9). Y02b'ye adımlar arası boşluk olarak ≥ 0,2 sn (tahmin) eklendi.
- **Ses tanıtım kuralı** ([SM] S0.3): bir karakterin ekran dışı sesi, o karakter ekranda konuşurken duyulduktan sonra kullanılır. Benim `ekran_disi_ses.kaynak: "tts"` seçeneğim bu kurala bağlandı.

**[UM] üretim mühendisi**
- Çıktı zarfı ve imza. Plan imzası değişince kredili çıktı **`bayat`** işaretlenir ve asla kendiliğinden silinmez.
- Adım cümlesi için kelime üst sınırı. [UM] 12 kelime önerdi; ben **16** öneriyorum (tahmin), çünkü kıskaç şablonu "kaç parmak" bilgisini taşımak için 15 kelime tutuyor.
- **Plan düzeyinde kâğıt seyircisi** (K11), Y6 olarak.
- `uretim_blogu` (Ç-8); `deneme_max: 2`.

**[CM] Claude Code mimarisi**
- Ajanlarda Bash yok; denetim **SubagentStop** kancasında. Görevler `_GOREV/<id>/GIRDI` dilimleriyle verilir, istemler şablondan üretilir.
- **Konuşmalı planda replik bir adım sayılır** (1 fiziksel + 1 replik = 2 adım). Bu benim Y01 yorumumla aynı.
- **`ekranda_bilgi` seyirciye verilmez**: karşılaştırma anahtarıdır. Kör pakette plan görünür sözle anlatılır.
- `30_YONETMEN/` klasör adı ve `HARITA_P<n>.json` dosya adı.
- Değerlendirici ajanların her turda yeni örnekle açılması. Yazar ajanın revizyonu aynı örnekte yapması (oturum kesildiyse yeni örnek, önceki sürüm ve raporlarla).
- `istem-muhendisi` ajanının kaldırılması; plan değişikliği gerektiren onarımın `yonetmen` kipine geçmesi.

---

## 4. REVİZE NİHAİ ÖNERİM

Bu bölüm tur 1 dosyamın yerine geçer ve kendi başına okunabilir. Tur 1'den farklı olan yerler **(değişti)** ya da **(yeni)** diye işaretlidir.

---

### 4.1 Alanımın hedefi ve başarı ölçütü (sayılarla)

**Hedef (tek cümle):** Kilitlenmiş hikâyeyi (`HIKAYE.json`), her biri "unutkan" 8–10 sn'lik ayrı bir klipten üretilecek **≈495 planlık** çekim listesine çevirmek (40 dk için, RE `hedef_plan_dagilimi_40dk`). Her plan için kâğıtta şunlar kesinleşir ve makineyle kanıtlanır:
- kamera nerede duruyor
- kim nerede duruyor ve kime bakıyor
- ışık nereden geliyor
- kimin hangi elinde ne var, kaç parmağı açık
- klipte saniye saniye ne oluyor
- klip hangi durumda bitiyor ve sonraki plana nasıl bağlanıyor (kesme türü ve başlangıç karesinin kaynağı)

**İlke: ajan karar verir, kod derler ve denetler.**
1. Yönetmen ajanı yapılandırılmış alanları doldurur: sahne sözleşmesi, kroki, kurulum, kadrajdakiler, durum farkı, eylem zinciri, zincir niyeti, kesme.
2. Kod şunları hesaplar: kadrajdaki konum, eksen tarafı, bakış ve ışığın kadrajdaki yönü, ekran yönü, bitiş durumu, ayna yasağı, ağız görünürlüğü, referans listesi.
3. Kod istemleri bu alanlardan derler. Kimlik ve ses tarifleri kelimesi kelimesine tekrarlanır (A1 B3).
4. Ajanın yazdığı ile kodun hesapladığı birbirini tutmazsa HATA verilir.
5. **(yeni)** Her alanın tek sahibi vardır (§4.5.2). Aynı olgu iki yerde tutulmaz.

**Başarı ölçütleri**

| # | Ölçüt | Hedef | Kim ölçer | Kaynak / etiket |
|---|---|---|---|---|
| Ö1 | Plan şeması (alan, sözlük değeri, sahiplik) | Görsel aşamasından önce HATA = 0 | `plan_sema.py` | yeni |
| Ö2 | Kâğıt plan dili kapısı (Z0 #4–6, #11–19 + Y kuralları) | HATA = 0; her BAYRAK gerekçeli | `plan_denetim.py` | ZN §6.2 |
| Ö3 | Durum zinciri: açıklaması olmayan olgu sıçraması | 0 | `dunya_defteri.py` (K0) | ZN Z0 #16, A2 K0 |
| Ö4 | Kâğıtta 180°, bakış, kadraj sırası ihlali | 0 | `kroki.py` | ZN Z0 #17–18 |
| Ö5 | G1'de kadraj sırası ve bakış ihlali (ilk geçiş) | ≤ %3 plan | [GS] G1 raporu | (tahmin) |
| Ö6 | Başlangıç karelerinin ilk geçişte bozuk oranı | B3'te 21/44 = **%48** idi (DR) → ≤ %15. Plan diline bağlı türler (yanlış kişi, ters el, bakış, yasak ışık) ≤ %8 | [GS] G1 | hedefler (tahmin) |
| Ö7 | V3: planlanan bitiş durumuna ulaşma (eylem ve aksiyon planları) | ilk videoda ≥ %80; ikinci denemede ≥ %95 | [GS] `video_denetim.py` V3 | (tahmin) |
| Ö8 | `devam` dikişi: Z1 kaynağının kesme karesi ↔ sonraki klibin ilk kullanılan karesi, DINOv2 | geçişlerin ≥ %90'ında ≥ 0,80 | [GS] K1 | eşik A2 §6.2; oran (tahmin) |
| Ö9 | Plan dili kök nedenli video yeniden çekimi ([KU] §5.6 "yönetmen" sınıfı) | ≤ %5 klip; toplam pay RE `kredi_yeniden_deneme_payi` (%20) içinde | `KREDI_DEFTERI` + kök neden | (tahmin) **(değişti)** |
| Ö10 | Kurgu izleme: akıcılık medyanı; yönetmen sınıfı kök nedenli KRİTİK | ≥ 8; 0 | habersiz seyirci + [KU] | ZN §7.3, RE |
| Ö11 | Plan sayısı / ASL / diyalog sahnesinde tepki oranı / J-L oranı | 495 ±%15 / 4,2–5,2 sn / ≥ %25 / ≥ %30 | `plan_denetim.py`, [KU] T0 | RE |
| Ö12 | Sahne grubu başına SubagentStop düzeltme turu | ≤ 2, sonra harita revizyonu | `film.py` | A3 B6 (OpenMontage 2 tur) **(değişti)** |
| Ö13 | Yönetmen aşamasında kullanıcıya sorulan soru | 0 | [CM] `soru_kapisi` | kesin karar 1 |
| Ö14 | **(yeni)** Plan seyircisi: GENEL medyan; KRİTİK; ORTA | ≥ 8; 0; ≤ 3/parti; ≤ 2 tur | `puan_oku.py` | RE `seyirci_*`, `kopukluk_*`; tur sayısı (tahmin) |
| Ö15 | **(yeni)** Plan eleştirisi: KRİTİK; ORTA | 0; ≤ 3/parti | `puan_oku.py` | ZN §7.3 ölçeği |

**Ö6 ve Ö7 neden önemli?** Kullanıcının iki büyük şikâyeti "kopuk" ve "karakter değişiyor" (BK 1.4 #3, H/kurgu-izleme-denetimi). Bu iki ölçüt, kopukluğun **plan dilinden** gelen kısmını ölçer.

---

### 4.2 Aşama aşama süreç: girdi → iş → çıktı → geçme şartı → kim

Klasör: `<film>/30_YONETMEN/` ([CM] kanonik düzeni). Bütün ajan görevleri [CM]'nin görev defterinden geçer: `film.py sonraki` → ana Claude ajanı başlatır → SubagentStop kancası denetler.
Aşama kodları orkestratöre aittir. Eşlemesi: Y0–Y2 ≈ [CM] A07a / [UM] K06; Y3 ≈ A07b; Y4 ≈ A07c / K07 + K10; Y5–Y6 ≈ A07d / K11; Y7 ≈ A09 / K09.

**Y0 — Yönetmen brifingi (betik)**
- **Girdi:**
  - `HIKAYE.json` (kilitli, [SN] §5.2)
  - `EVREN/<SERI>/` içinden: mekân krokileri ve kurulumlar varsa, karakter kartları, `boy_m`, `goz_yuksekligi_m`, `baskin_el`, `asimetrik`
  - `DERSLER_AKTIF.md` içinde rol etiketi `yonetmen` olan dersler
  - RE
- **İş:** `dilim.py --yonetmen-brifing` betiği şunları tek belgede toplar:
  - karakterlerin görünür kısa tarifi (`etiket_anonim`)
  - kostüm durum sözlüğü
  - mekân listesi ve her mekânın kroki durumu (var / yok / eksik)
  - filmde geçerli onaylı dersler
  - eşik özeti
- **Çıktı:** `30_YONETMEN/00_BRIFING.md`
- **Geçme şartı:**
  - [SN] H13 kilidi var
  - her hikâye sahnesinde tek mekân var
  - her konuşan karakterin evren kaydı ya da ön kaydı var
- **Kim:** betik.

**Y1 — Parti haritası: sahne sözleşmeleri** (yonetmen `harita` kipi; parti başına bir görev; parti sınır durumları hikâyede yazılı olduğu için 3 görev paralel çalışabilir) **(değişti)**
- **Girdi (GIRDI dilimi):**
  - o partinin hikâye sahneleri: EKRAN bloğu, `giris_durumu` ve `cikis_durumu`, `sahne_degeri`, `vurus`, `hedef_sure_sn`, `b3_kim_nerede`, `b4_nesne_yolu`, `b6_mekan`
  - brifing
  - mekânların krokileri, yoksa hazır mekân şablonları
  - `PLAN_DILI.md` §Harita
- **İş:** Hikâye sahneleri 1:1 sahne grubu olur. Yönetmen her sahne için şunları ekler:
  - `plan_hedef` ve `kalip` (klasik_giris / gec_giris / yukselen_diyalog / acilan_sonuc)
  - iki ve daha çok kişili sahnede `eksen` ve `kamera_tarafi`
  - yolculuk ve kovalamacada `ekran_yonu`
  - `isik {ana, dolgu, arka}`, `yasaklar`
  - kullanılacak kurulumlar (Y2)
  - **tam şemada** `giris_durumu` ve `cikis_durumu`: hikâyenin `yer` adı işarete bağlanır, yüz yönü, eller (yer ve şekil) ve mekân öğesi durumları eklenir
  
  Süre ±%20 içinde ayarlanabilir ([SN]). Sahne bölme ve birleştirme yalnız İ-14'teki istisnayla yapılır.
- **Çıktı:** `30_YONETMEN/HARITA_P<n>.json` + `HARITA_P<n>.md` (insan özeti: sahne listesi, kroki bağlantıları, riskli sahneler)
- **Geçme şartı:** `plan_denetim.py --harita` HATA = 0. Kapsananlar:
  - Z0 #1–3 ve #8
  - RE `sahne_tipi_aralik` (süre, plan sayısı, ASL)
  - Sözleşme zinciri: `cikis[S_n]` → `giris[S_n+1]` olgularda eşit; değilse `zaman.atlama` ya da ekranda bir olay
  - Hikâye uçları ⊆ sözleşme (Y57)
  - Konuşan ≤ 8; sahne başına yeni ad ≤ 2 (RE)
- **Kim:** `yonetmen` (harita kipi). SubagentStop kancası en çok 2 kez geri gönderir.

**Y2 — Krokiler, plakalar, kurulumlar** (aynı harita görevi içinde) **(değişti)**
- **Girdi:** Y1 girdisine ek olarak `kroki.py --karsilikli` ile **betiğin görevden önce hesapladığı** standart karşılıklı çekim önerileri: her eksen çifti ve taraf için ikili konum planı, iki omuz üstü, iki tekli; mesafe ve lens kalıplarıyla.
- **İş:**
  - Mekân ilk kez kullanılıyorsa `EVREN/<SERI>/mekanlar/<id>/kroki.json` taslağı yazılır: duvarlar ve açıklıklar, öğeler (yükseklik ve engel bilgisiyle), oyuncu işaretleri, ışık kaynakları, **plakalar** (mekân kartı açıları).
  - Mekân evrende varsa kroki okunur; yalnız eksik işaret ya da plaka eklenir (yeni sürüm).
  - Her sahne için kurulumlar (K1…Kn) seçilir ya da düzeltilir: konum, yön, yükseklik, lens, varsayılan kadraj, ebeveyn (plaka ya da başka kurulum).
- **Çıktı:**
  - `kroki.json` (taslak; plakalar G1'den geçince kilitlenir)
  - `HARITA_P<n>.json → mekanlar.<id>.kurulumlar`
  - `30_YONETMEN/KROKI/<mekan>.png` ve `<sahne>.png` (`kroki.py --ciz`)
  - **`KART_ISTEGI.json`**: plaka açıları ve her plakada görünmesi gereken öğeler (hesapla), kostüm durum varyantları, ölçek isteyen nesneler → [GS] A2'nin girdisi
- **Geçme şartı:** `kroki.py --denetle` HATA = 0. Kapsananlar:
  - işaretler tanımlı
  - kurulumlar eksenin aynı tarafında (eksen üstü `notr` kurulum hariç)
  - her kurulumun görüş konisindeki duvar ve öğeler bir plakada var (Y60)
  - ışık kaynakları tanımlı
  - "yasak ardışık" kurulum çiftleri listelendi (Y19)
- **Kim:** `yonetmen` yazar, `kroki.py` hesaplar ve çizer.

**Y3 — Sahne grubu planları** (yonetmen `plan` kipi; sahne grubu başına yeni örnek; paralel grup, aynı anda ≤ 5 (tahmin; kullanım sınırına bağlı)) **(değişti: ayrı `plan-yazari` ajanı yok)**
- **Girdi (GIRDI dilimi, [CM] `dilim.py`; ajan başka dosya okumaz):**
  - sahne sözleşmesi
  - kroki PNG'leri, kurulumlar ve `yasak_ardisik` listesi
  - sahnenin EKRAN metni ve replikleri (R id'leriyle, `ton_fiili` ile)
  - önceki sahnenin son 2 planının **çözülmüş** bitiş durumu
  - onaylı dersler
  - `PLAN_DILI.md`, `plan_sozlukleri.json`, `fiil_sozlugu.json`
- **İş:** Her plan için `zanaat` alanları yazılır (§4.5.6):
  - kurulum ve kadraj
  - kadrajdakiler
  - başlangıç durumu (`miras` ya da gerekçeli `fark`)
  - eylem zinciri (2–3 adım, saniyeli, `etki`li; konuşma adımı R id'siyle)
  - `ekran_disi_ses`
  - zincir niyeti
  - kesme
  - `kullanim`
  - `ekranda_bilgi`
  - `risk_uretim`
  
  Bitiş durumunu kod hesaplar.
- **Çıktı:** `30_YONETMEN/PLANLAR/Sxx.json`
- **Geçme şartı:** SubagentStop → `plan_sema.py` + `plan_denetim.py --sahne Sxx` + `kroki.py --sahne Sxx`, HATA = 0. En çok 2 düzeltme yapılır. Sonra görev `gecersiz` olur ve `film.py` bir **harita revizyonu** görevi açar (kurulum ya da sözleşme değişikliği).
- **Kim:** `yonetmen` (plan kipi).

**Y4 — Birleştirme ve kâğıt kapıları (betik)**
- **İş:**
  1. `plan_birlestir.py` → `SAHNELER.json`: `no` (kalıcı, `NO_ESLEME.json`), `sira`, `parti` (hikâye), `kaynak_klip`, sahiplik denetimi.
  2. `dunya_defteri.py` → `DUNYA_DEFTERI.json` + K0 raporu.
  3. `kroki.py --denetle --tum` → `_derlenir` alanları.
  4. `plan_denetim.py --tum` (tam Z0 + Y).
  5. [KU] `zaman_cizelgesi.py --asama kagit` (T0: Z1 ve Z2 zaman ölçüleri).
- **Çıktı:** `SAHNELER.json`, `DUNYA_DEFTERI.json`, Z0, K0 ve T0 raporları. HATA varsa `YENIDEN_YAZ.json` (`{plan, madde, yazar: "yonetmen", sahne: "Sxx"}`).
- **Geçme şartı:** HATA = 0.
- **Kim:** betik. Her HATA, sahneyi yazan yönetmen örneğine gider: oturum sürüyorsa SendMessage ile, sürmüyorsa önceki sürüm ve rapor GIRDI'de olacak şekilde yeni örnekle ([CM] §2.2-3).

**Y5 — Kâğıt plan denetimi (paralel değerlendiriciler)**
- **Girdi:** `cekim_listesi.py --parti n` çıktısı: sahne sahne tablo, kroki PNG'leri, `plan_dili` Türkçe görünür tarifleri. Ayrıca sahne değeri ve vuruş.
- **İş:**
  - **`plan-elestirmeni`** (parti başına; her turda yeni örnek): sinematografi kontrol listesi (§4.3).
  - **`uretilebilirlik-denetcisi`** (plan kipi, [CM]): fiziksel uygunluk. 2–3 adım 8 sn'ye sığıyor mu, el ve parmak ayrıntısı, ölçek, filtre riski.
  - **`sureklilik-denetcisi`** (kâğıt kipi, [GS]): K0 BAYRAK'larını kapatır, anlam hatalarını bulur.
- **Çıktı:** `30_YONETMEN/denetim/ELESTIRI_P<n>_t<k>.md` ve diğer iki denetçinin raporları.
- **Geçme şartı:** eleştirmende KRİTİK = 0 ve ORTA ≤ 3; denetçilerde KRİTİK = 0; BAYRAK'lar kapanmış. En çok 2 tur. Düzeltmeyi sahnenin yönetmen örneği yapar.
- **Kim:** ajanlar + `puan_oku.py`.

**Y6 — Plan seyircisi** ([UM] K11, [CM] A07d) **(yeni)**
- **Girdi:** `kor_paket.py --kip plan`. Paket şunlardan oluşur:
  - `plan_dili.gorunur_tarif(..., dil="tr")`: kadraj düz sözle, kadrajdaki kişiler etiketiyle ve konumuyla, görünür adımlar saniyeleriyle
  - duyulan replik (ekranda ya da ekran dışı)
  - yer ve zaman kartları
  
  Ad maskeleme [SN] `ekran_metni.py`'nin kodudur. `ekranda_bilgi`, `amac`, `vurus` ve benzeri alanlar **verilmez**.
- **İş:** Parti başına 3 habersiz seyirci (yeni örnek), ZN §7.3 ölçütleriyle.
- **Geçme şartı:** Ö14. Seyirci özeti `ekranda_bilgi` birleşimiyle eşleştirilir ([KU] `ozet-eslestirici`). Hikâye kaynaklı bulgu senariste gider ([SN] H13 dar geri dönüş), plan kaynaklı bulgu yönetmene.
- **Neden ayrı bir kapı:** Animatik görselleri bekler (Gemini paketi = kullanıcının eli + G1 turları). Plan düzeyindeki bilgi kopukluğunu görsel emeğinden **önce** yakalamak 0 kredilidir. B1'de babanın adının 84. çekimde geçmesi bu düzeyde bulunmuştu (YR A8).

**Y7 — İstem derleme (betik)** — [SM] A4–A7 ses kâğıt aşamasından sonra
- **İş:**
  - `istem_derle.py --hareket` (benim modülüm): saniyeli adımlar, tek kişide öznesiz, iki kişide adlı; konuşmada `ton_fiili` + `veo_ses_tarifi` + `veo_metin`; `Sound:` = `zanaat.ses.flow_sound`; `No music.`
  - `istem_derle.py --gorsel` ([GS] modülü): anlık görüntü.
  - Her ikisinin `*_yedek` hâlleri.
  - `bitis_karesi` (Memmet'in bugünkü alanı) derlenir.
  - Ardından `istem_denetim.py`.
- **Çıktı:** `SAHNELER.json` istem alanları; `RAPORLAR/ISTEM_DERLEME.txt`.
- **Geçme şartı:** HATA = 0. Kapsananlar:
  - filtre kelimesi 0
  - yasak sonuç fiili 0
  - çıplak left/right 0 (Y47)
  - hareket istemi ≤ 75 kelime ve adım cümlesi ≤ 16 kelime (Y46, tahmin)
- **Kim:** betik.

**Y8 — Kamera ağacı ve görsel üretim sırası (betik)**
- **İş:** `kamera_agaci.py` şu sırayı çıkarır:
  1. plakalar (kart aşaması)
  2. her kurulumun **ana karesi** (kurulumun ilk planı)
  3. türevler
  4. `devam` planlarının planlanmış görselleri
  
  Her basamak G1'den geçmeden sonraki basamağın paketi verilmez. Ebeveyni yeniden üretilen görselin çocukları `bayat` işaretlenir.
- **Çıktı:** `30_YONETMEN/KAMERA_AGACI.json`; `sahne_gruplari.*._derlenir.ana_kareler`; Gemini paket gruplaması (paket içeriği [GS]'nindir).
- **Kim:** betik.

**Y9 — Dönüşler** (yonetmen `onarim` kipi; her değişiklik Y4 → Y7'yi yalnız etkilenen sahneler için yeniden koşturur; etkilenen görseller `bayat` olur)
- **a) Animatik seyircisi** ([KU] K5): plan kaynaklı maddeler (kopukluk, "nereden çıktı", konum anlaşılmıyor) gelir.
- **b) G1 kaçışı** ([GS] A9 adım 4): 2 CORRECTION turundan sonra şu seçeneklerden biri uygulanır:
  - kadrajı ya da açıyı değiştir
  - sorunlu eli kadraj dışına al
  - riskli eylemi eklemeye böl
  - üçüncü kişiyi siluet yap
  - kurulumu değiştir
  
  Aynı istemle üçüncü deneme yapılmaz.
- **c) V3** ([GS] A14): bitiş durumuna ulaşılmadıysa sıra şöyledir:
  1. daha erken bir kare durumu karşılıyorsa `kullanim` kısaltılır ([KU])
  2. Z2 ile yeniden çekim
  3. adımı ayrı plana böl ya da eklemeye taşı
- **d) Kurgu** ([KU] K9 `yeni_plan_iste`): yeni plan `no = max+1` alır, `sira` ondalıktır (ör. 121.5), dosya adları değişmez.
- **e) Filtre reddi** ([CM] onarım): fiil ya da öğe sözlükteki güvenli karşılığıyla değiştirilir ([SN] `sozluk.guvenli_karsilik`). Değişiklik istem üzerinde değil plan alanında yapılır.
- **Çıktı:** `30_YONETMEN/ONARIM_<tur>.json` (karar — neden — yanlışsa maliyeti) + güncel `PLANLAR/Sxx.json`.

**Y10 — Ders defteri** (betik + yonetmen `ders` kipi)
- `ders_defteri.py` ([UM]/[CM]) olayları toplar. `plan_ozellik.py` her olaya plan özellik vektörünü ekler.
- Rol etiketi `yonetmen` olan aday dersleri yonetmen `ders` kipi tek cümlelik kurala çevirir. Terfi `ders-editoru` ile yapılır ([CM]).
- Onaylı ders **bir sonraki partide** `plan_denetim` ve `istem_derle`'ye girer (§4.8-e).

**Akış özeti**
```
HIKAYE ✔ → Y0 → Y1+Y2 (harita ⟲2) → Y3 (sahne planları ∥ ⟲2) → Y4 (betik kapıları ⟲)
 → Y5 (eleştiri ∥ üretilebilirlik ∥ süreklilik ⟲2) → Y6 (plan seyircisi ⟲2) → [ses kâğıtta] → Y7 → Y8
 → [görsel+G1] → [animatik ⟲] → [bütçe] → [video Z1 dalgaları + V1/V2/V3] → [kurgu ⟲]
   ↑__________________ Y9 a–e (aynı yazar rolü; Y4→Y7 yalnız etkilenenler) __________________|
```

---

### 4.3 Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı)

Ajan ve kip ayrımında [CM] Ç-10 ölçütüne uydum: yeni ajan ancak (a) ayrı bir dosyanın sahibi ya da (b) bağımsız bir değerlendirici ise açılır. Diğer işler mevcut ajanın kipi olur.
Bütün ajanlarda `model: opus` (claude-opus-5-5) ve `effort: high` (H/ajan-opus-yuksek, kesin karar 6). `fallbackModel` ve `memory:` tanımlanmaz. **Bash yoktur** ([CM]).

#### 4.3.1 `yonetmen` (mevcut taslak baştan yazılır)

| Alan | Değer |
|---|---|
| araçlar | `Read, Write, Edit, Glob, Grep`. Okuma ve yazma, [CM] erişim kancasıyla görev klasörüne bağlıdır |
| kipler | `harita` (Y1–Y2), `plan` (Y3; sahne grubu başına yeni örnek), `onarim` (Y9), `kart_secimi` ([GS] A4: kart adayları arasında sanatsal seçim), `ders` (Y10) |
| yapmaz | İstem yazmaz (kod derler). Replik metnini değiştirmez; yalnız böler ve zamanlar, değişiklik gerekiyorsa `replik_degisiklik_istegi` yazar. Sahne sınırını değiştirmez (İ-14). Kendi çıktısını puanlamaz |
| okuyacağı | Yalnız GIRDI dilimi + `.claude/skills/film-yap/PLAN_DILI.md` + `plan_sozlukleri.json` + `fiil_sozlugu.json` |
| çıktısı | harita: `HARITA_P<n>.json/.md`, `kroki.json` taslakları, `KART_ISTEGI.json` · plan: `PLANLAR/Sxx.json` · onarim: `ONARIM_<tur>.json` · kart_secimi: `KART_SECIM.json` (gerekçeli) · ders: `DERS_ONERI.json` |
| döndürdüğü | ≤ 5 satır: çıktı yolları + plan sayısı, toplam süre, tepki oranı, J/L oranı, kalan BAYRAK sayısı, `replik_degisiklik_istegi` sayısı |

Örnek başlık (gövdenin ilk satırları sıkıştırmadan sonra da bağlamda kalır):
```markdown
---
name: yonetmen
description: Filmin yönetmeni. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır. Kipler: harita (sahne sözleşmeleri, kroki, kurulum), plan (tek sahne grubunun atomik eylem zincirli plan listesi), onarim (G1/V3/kurgu/filtre dönüşü), kart_secimi, ders.
tools: Read, Write, Edit, Glob, Grep
model: opus
effort: high
maxTurns: 80
---
KESİN KURAL: YZ'ye sonuç söylenmez. Klip başına 2–3 adım (konuşma bir adımdır). Her adım: [bas–bit sn] + sözlükten tek fiil
+ vücut parçası + karakterin KENDİ sağı/solu + hedef + ölçü + (el işinde) el şekli. Her adımın `etki`si yazılır; bitiş durumunu
kod hesaplar. Durum yalnız olgudur; kadraj konumunu, bakış yönünü, ışık yönünü YAZMA — kroki.py hesaplar.
hareket_istem / gorsel_istem YAZMAZSIN. Replik metnine dokunmazsın. Yasak sonuç fiilleri GIRDI/sozluk'tedir.
```

#### 4.3.2 `plan-elestirmeni` (yeni; bağımsız değerlendirici)

| Alan | Değer |
|---|---|
| araçlar | `Read, Write`; `omitClaudeMd: true` ([CM]) |
| görevi | Parti başına çekim listesini sinematografi gözüyle eleştirir. Yazar değildir; madde başına düzeltme önerir |
| okuyacağı | Yalnız GIRDI: `CEKIM_LISTESI_P<n>.md`, kroki PNG'leri, o partinin sahne değerleri ve vuruşları, `PLAN_DILI.md` §Kontrol listesi. Yazarın notlarını ve önceki turları **görmez** |
| kontrol listesi | (1) Her önemli replikten sonra tepki var mı, doğru kişide mi? (2) Ekleme planı hangi kurulumu ya da kullanımı taşıyor? (3) Aynı anda iki kişi hareket ediyor mu? (4) Konuşan yüz okunur mu (ölçek, açı)? (5) Konum planı ilk 3 planda mı? (6) Ekran yönü sürüyor mu? (7) Görünen ışık kaynağı ile ışık yönü tutarlı mı? (8) "Geç gir, erken çık" uygulanmış mı? (9) Bu planda seyirci yeni ne öğreniyor? (10) Kuleshov ve göz izi: dikkat merkezi kesmede aynı üçte birde mi? (11) **(yeni)** Doğrudan bitişik `devam` gerçekten doğal bir durakta mı? |
| çıktısı | `ELESTIRI_P<n>_t<k>.md` + `.json`. Maddeler `KRİTİK/ORTA/KÜÇÜK \| plan \| sorun \| öneri` biçiminde. Son satır: `OZET \| kapsama: 8 \| kadraj_dili: 8 \| okunurluk: 8 \| akis: 7 \| KRITIK: 0 \| ORTA: 2` |
| sınır | Fiziksel uygunluk (8 sn'ye sığar mı) `uretilebilirlik-denetcisi`'nindir; anlam ve süreklilik `sureklilik-denetcisi`'nindir. Bu ajan yalnız görüntü dili ve kapsamaya bakar |

#### 4.3.3 Benim alanımı kullanan, sahibi başka olan ajanlar
- **`habersiz-seyirci`** ([SN] / [KU] / [CM]): Y6 `plan` kipi. `ekranda_bilgi` alanını **asla görmez**.
- **`uretilebilirlik-denetcisi`** ([CM]): Y5 plan kipi.
- **`sureklilik-denetcisi`** ([GS]): Y5 kâğıt kipi; G1, V2 ve V3'te hakem.
- **`kor-gozlemci` / `kare-tarifcisi`** ([GS] / [CM]; ad onların kararı): `_derlenir.gorunmesi_gerekenler`'den üretilen sorulara kör cevap verir.
- **`kurgucu`** ([KU]): `yeni_plan_iste` ile bana iş açar.

#### 4.3.4 Kaldırılan
- **`plan-yazari`** ([YN1]) → `yonetmen` plan kipi.
- **`istem-muhendisi`** → `istem_derle.py` + `yonetmen` onarım kipi + `duzeltme.py` ([GS]) ([CM] ile aynı karar).

---

### 4.4 Beceri (skill) tarif adımları — kendi alanım

**4.4.1 Dosyalar** (A3 B4: SKILL.md < 500 satır; ayrıntılar tek seviye bağlantıyla)
- `film-yap/SKILL.md`'de ≤ 15 satırlık "Yönetmen aşaması" maddesi: dört kural + iki bağlantı.
- `film-yap/reference/yonetmen.md` (≤ 200 satır, başında içindekiler): ana Claude'un görev sırası, durma ve devam kuralları.
- `film-yap/PLAN_DILI.md`: ajan kılavuzu. İçeriği: sözlüklerin anlamı, atomik zincir yazım kuralları, 6 örnek (§4.8.1), kroki ve kurulum kuralları, karşılıklı çekim kalıpları, kontrol listesi.
- `film-yap/sablonlar/yonetmen_harita.md`, `yonetmen_plan.md`, `yonetmen_onarim.md`, `plan_elestirmeni.md`: [CM] görev şablonları.
- `YZ_FILM/ARACLAR/veri/plan_sozlukleri.json`, `fiil_sozlugu.json`: ajan ve betikler aynı dosyayı okur.

**4.4.2 SKILL.md'deki kurallar** (sıkıştırmadan sonra da ilk bölümde kalır)
1. Yönetmen istem yazmaz; istemi kod derler. İstemde bir sorun varsa kaynağı olan plan alanı düzeltilir.
2. Durum yalnız olgudur. Kadraj konumu ve yönler `_derlenir`'dedir.
3. Replik metni senaristindir.
4. `SAHNELER.json`, `DUNYA_DEFTERI.json` ve `EVREN/` dosyaları elle değiştirilmez.

**4.4.3 Görev sırası** (`film.py sonraki` bu sırayla görev üretir; ana Claude kopyalayıp işaretler)
```
YÖNETMEN AŞAMASI — <FİLM>
[ ] 0  film.py ozet → hikâye kilitli mi, aşama Y0 mı? Değilse dur.
[ ] 1  (betik) dilim.py --yonetmen-brifing → 30_YONETMEN/00_BRIFING.md
[ ] 2  (betik) kroki.py --karsilikli --hepsi → her parti GIRDI'sine kurulum önerileri
[ ] 3  TEK mesajda 3× Agent(yonetmen, kip=harita, P1/P2/P3) → SubagentStop: plan_denetim --harita + kroki --denetle (≤2)
[ ] 4  KART_ISTEGI.json → kart aşamasına görev açıldı mı? (paralel ilerler)
[ ] 5  (betik) dilim.py --yonetmen-plan --hepsi → her sahne grubu için GIRDI
[ ] 6  Paralel grup: Agent(yonetmen, kip=plan, Sxx) ≤ 5 aynı anda → SubagentStop: plan_sema + plan_denetim --sahne + kroki --sahne (≤2)
[ ] 7  (betik) plan_birlestir → dunya_defteri → kroki --tum → plan_denetim --tum → zaman_cizelgesi --asama kagit
       HATA → YENIDEN_YAZ → ilgili Sxx yönetmen örneğine (SendMessage ya da yeni örnek + önceki sürüm)
[ ] 8  (betik) cekim_listesi --parti 1,2,3 → TEK mesajda: plan-elestirmeni×3 ∥ uretilebilirlik(plan)×3 ∥ sureklilik(kagit)
       puan_oku → KRİTİK>0 ya da ORTA>3 → ilgili sahnelere (≤2 tur)
[ ] 9  (betik) kor_paket --kip plan → habersiz-seyirci ×3/parti (yeni örnek) → puan_oku → Ö14 (≤2 tur)
[ ] 10 [ses kâğıtta: ses uzmanının görevleri]
[ ] 11 (betik) istem_derle --hareket --gorsel → istem_denetim → HATA 0
[ ] 12 (betik) kamera_agaci → görsel paket sırası → durum "yonetmen: tamam"
```

**4.4.4 Durma ve devam**
- Her adımın çıktısı dosyadadır. Sıkıştırmadan sonra hafızaya değil `film.py ozet`, `FILM_DURUM.json` ve görev defterine güvenilir (A3 B6).
- 2 SubagentStop turundan sonra HATA kalırsa harita revizyonu yapılır: kurulum değişir, sahne bölünür (yalnız İ-14 istisnasıyla) ya da sözleşme değişir. Bu da tutmazsa ([CM] S-3 kuralıyla) kullanıcıya **bilgi** verilir; soru sorulmaz.
- Kararlar `KARAR_DEFTERI.md`'ye `karar — neden — yanlışsa maliyeti` biçiminde yazılır (A3 B6). Örnek: `S12'de eksen batıdan — Mara hep solda — yanlışsa S12'nin 16 görseli yeniden`.
- Paralel yönetmen örnekleri birbirinin dosyasını okumaz. Sahneler arası tutarlılığı ajanlar değil, sözleşme ve `dunya_defteri.py` sağlar.

**4.4.5 Değerlendirme senaryoları** (beceri testi, A3 B4)
1. Zanaat alanlı `ORNEK_3_SAHNE`: Y4–Y7 betikleri hatasız çalışır; derlenen istemler beklenen metinle birebir aynıdır.
2. Kamera eksenin öbür tarafında → `plan_denetim` Y17 HATA'sı, `kroki.py` kadraj sırası çelişkisi.
3. Fener sol ele geçmiş ama etki yazılmamış → `dunya_defteri` Y16 HATA'sı.
4. "Kalemi al" tek cümlesi → Y07 HATA'sı; yönetmen atomik zincire çevirir.
5. **(yeni)** Kurgucu 43 ile 44'ün yerini değiştiriyor → dondurulmuş durumla Y58 HATA'sı.
6. **(yeni)** `devam` planında kesme noktası hareketin ortasında → Y55 HATA'sı.

---

### 4.5 Veri şeması / plan alanları (JSON örneğiyle)

#### 4.5.1 Katmanlar
```
Seri evreni (EVREN/<SERI>/) ── mekân ── kroki.json (duvar, öğe, işaret M1..Mn, ışık kaynağı, plakalar)
Film ─┬─ Hikâye partisi (1–3)                                  [SN] partiler; plan `parti` = bu
      ├─ Mekân (film) ── kurulumlar K1..Kn (kamera; ebeveyn = plaka ya da başka K)
      └─ Sahne grubu S01..S55  (= hikâye sahnesi; tek mekân + kesintisiz zaman; eksen, ışık, sözleşme)
             └─ Plan (kurgu birimi; SAHNELER.json "sahneler[]" öğesi; no = dosya adı NNN)
                    └─ Klip (üretim birimi, 8/10 sn); bir klipten 1–2 plan çıkar (kaynak_klip)
```
- **`no` kimliktir, sıra değildir.** Görsel üretimi başladıktan sonra yeniden numaralanmaz. Kurgu sırası `sira`'dadır (ondalık olabilir: 121.5). Bu, B2'deki "A15N, RC27 = no 189–201" karmaşasının çözümüdür (H/proje-b2).

#### 4.5.2 Sahiplik (alan başına) **(değişti)**

| Alan | Sahibi | Not |
|---|---|---|
| `no`, `sira`, `parti`, `kesme`'nin hesaplanan kısmı | betik (`plan_birlestir`) | `parti` = hikâye partisi |
| `replik.{id, karakter, metin, cumleler, ton_fiili}` | senarist | Yönetmen yalnız konuşma adımıyla böler ve zamanlar |
| `replik.{seviye, veo_metin}` | ses | |
| `kullanim {bas, sure}`, `amac` | yönetmen | Planlanan değer; ölçülen değer `KURGU_PLANI`'ndadır |
| `duygu` (mevcut alan) | betik | `zanaat.hedef_duygu`'nun ilk türü |
| `gorsel_istem*` | `istem_derle --gorsel` ([GS]) | elle yazılmaz |
| `hareket_istem*` | `istem_derle --hareket` (yönetmen) | elle yazılmaz |
| `bitis_karesi`, `referans`, `motor` | betik | Memmet uyumu için derlenir |
| `zanaat.{vurus, hedef_duygu, yogunluk, risk, merak_ac, merak_kapat, kurulum, kullanim_bilgi, ironi, vaat_imgesi}` | senarist tanımlar, **yönetmen plana yerleştirir** | Makine her kimliğin tam bir planda taşındığını denetler ([SN] §5.2) |
| `zanaat.{kod, sahne_grubu, plan_tipi, klip_sn, kaynak_klip, kamera, eksen_gecis, kadrajdakiler, baslangic_durumu, eylem_zinciri, bitis_durumu (beklenen), ekran_disi_ses, zincir, kesme, isik_degisimi, yasaklar, ekranda_bilgi, risk_uretim, istem_elle}` | yönetmen | |
| `zanaat.ses` | ses ([SM]) | `efektler[].adim` = adım id'si |
| `_derlenir` | kod (`kroki.py`, `dunya_defteri.py`, `plan_birlestir.py`) | Yazılırsa `plan_sema` HATA verir |
| `uretim` | üretim betikleri ([UM], [GS] `kare_zinciri`) | `durum_dondu` burada |
| `denetim` | kapılar | |
| `kurgu.kirpma_onceligi` | kurgucu | |

#### 4.5.3 Eşleme: önceki öneriler → nihai yer **(yeni)**

| Önceki | Nihai | Not |
|---|---|---|
| [YN1] `cekim.*` | `zanaat.*` | Ç-1 |
| [YN1] `varliklar`, `sol_el/sag_el` | `karakterler`, `eller.sol/sag` | Ç-3, Ç-4 |
| [YN1] adım `teslim`, `efekt` | `replik.ton_fiili`, `zanaat.ses.efektler[].adim` | İ-12, İ-9 |
| [YN1] `replik_kaynagi` | konuşma adımı / `ekran_disi_ses.kaynak` / `zanaat.ses.diyalog.yol` | Ç-11 |
| [YN1] `mekan_karti:<açı>` | `plaka:<id>` | Ç-13 |
| [YN1] `zincir.baslangic_karesi.kaynak` `onceki_bitis` / `son_kare` | `zincir.baslangic: son_kare` (Z1) + `bitis_sabitle` (Z2) | İ-2 |
| [GS] `zanaat.baslangic_durumu.kadrajdakiler[]` | `zanaat.kadrajdakiler[]` (kadraj) + durum `karakterler` (olgu) | İ-1 |
| [GS] `konum: sol_ucte_bir`, `kadraj_sirasi` | `_derlenir.kadraj_konumu`, `_derlenir.kadraj_sirasi` | İ-1, İ-7 |
| [GS] `yer` | durum `isaret` (krokideki `ad` ile) | |
| [GS] `yon: kadraj_sagi`, `bakis` | durum `yuz_yonu`, `bakis.hedef` + `_derlenir.bakis_kadrajda` | |
| [GS] `eller.*.hal` | `eller.*.{yer, sekil}` | İ-13 |
| [GS] `gorunum`, `mekan.durumlar` | durum `gorunum`, `mekan_durumu` | kabul |
| [GS] `isik{ana_kaynak, yon, gun_saati}` | sahne `isik`, sahne `zaman` + `_derlenir.isik_kadrajda` | |
| [GS] `sureklilik.{sahne_grubu, kamera_konumu, eksen_gecis, yasaklar}` | `zanaat.{sahne_grubu, kamera.kurulum, eksen_gecis, yasaklar}` | |
| [GS] `sureklilik.gecis_turu`, `zincir`, `bitis_sabitle` | `zanaat.zincir.*` (niyet) + `uretim.zincir.*` (yürütme) | Ç-6, Ç-7 |
| [GS] `hareket_yonu` (özne), `yuz_gorunur`, `giris_cikis` | `_derlenir.ekran_yonu`, `kadrajdakiler[].yuz_acisi`, `kadraja_girer` / `kadrajdan_cikar` adımları | İ-7 |
| [GS] `referans_gorseller`, `uretim`, `denetim` | `uretim.gorsel.referanslar`, üst düzey `uretim`, `denetim` | |
| [KU] `zanaat.sure_sn`, `kesme.nokta_sn` | `kullanim.sure` → `_derlenir.sure_sn`, `_derlenir.kesme_nokta_sn` | İ-5 |
| [KU] `kurgu.{ayna_yasak, vaat_imgesi, zincir_kaynagi}` | `_derlenir.ayna_yasak`, `zanaat.vaat_imgesi`, `uretim.zincir.kaynak` | İ-10 |
| [SM] `replik_zaman{bas, bit, tts_sn}` | `_derlenir.replik_zaman` + `zanaat.ses.tts_sn` | |
| [SM] `ekran_disi_ses`, `ses.diyalog.{agiz_gorunur, dinleyen_agiz}` | `zanaat.ekran_disi_ses`, `_derlenir.{agiz_gorunur, dinleyen_agiz}` | İ-9 |
| [UM] `uretim.zincir.yontem`, adım `govde.{el, parmak, acik}` | Ç-6; adım `govde` + `el_sekli` → `_derlenir.acik_parmak` | İ-13 |
| [CM] `DUNYA_DURUMU.json` | `DUNYA_DEFTERI.json` | Ç-5 |

#### 4.5.4 Seri evreni: `EVREN/<SERI>/mekanlar/<id>/kroki.json` (sahibi yönetmen) **(değişti)**

| Alan | Tür | Açıklama |
|---|---|---|
| `birim`, `yonler`, `sinir` | str, str, [[x,y],[x,y]] | metre; x = doğu, y = kuzey; `yon_derece` 0 = kuzey, 90 = doğu (pusula) |
| `duvarlar[]` | `{id, a, b, aciklik[]}` | Görüş hattı hesabı için |
| `ogeler[]` | `{id, tur, konum, yukseklik_m, engel, …}` | kapı (menteşe, açılış yönü), ocak, masa, kilit… `engel: true` olan öğenin arkası görünmez |
| `isaretler.M*` | `{konum, ad}` | Oyuncu işaretleri; durum `isaret` alanı yalnız bunları kullanır |
| `isik_kaynaklari[]` | `{id, konum, tur, renk, varsayilan}` | Taşınan ışık (fener, meşale) nesnedir, kroki dışıdır |
| `plakalar.<id>` | `{konum, yon_derece, lens_mm, yukseklik, gorunen[] (hesaplanır)}` | Boş mekân kartı açıları; kamera ağacının kökü. Görseller ve `mekan.json` [GS]'nindir |
| `surum`, `gecmis` | | Kroki değişikliği yeni sürüm açar; etkilenen sahneler yeniden denetlenir |

Film düzeyinde `SAHNELER.json → mekanlar.<id> = {evren: "<yol>@<sürüm>", kurulumlar: {K*: {konum, yon_derece, yukseklik, lens_mm, varsayilan_kadraj, ebeveyn, not}}}`.
Kurulumlar film sonunda evrene eklenir (`EVREN/<SERI>/mekanlar/<id>/kurulumlar.json`). Onaylı ana kareler de ışık varyantıyla birlikte saklanır (`ana_kareler/<isik>/<K>.jpg`, sahibi [GS]).

#### 4.5.5 Sahne grubu alanları (`HARITA_P<n>.json` → `SAHNELER.json → sahne_gruplari.<S>`)

| Alan | Zorunlu | Doldurur | Açıklama |
|---|---|---|---|
| `hikaye.{sahne, parti}` | evet | betik | `HIKAYE.json` bağı. `sahne_degeri`, `vurus`, `risk`, `seyirci_ogrenir` oradan **salt okunur** kopyalanır |
| `mekan`, `zaman{gun, gun_saati, hava, atlama}` | evet | hikâyeden | |
| `sahne_tipi`, `sure_hedef_sn` | evet | hikâyeden; süre ±%20 yönetmen | RE `sahne_tipi_aralik` |
| `plan_hedef`, `kalip` | evet | yönetmen | ZN §2.4, §3.2 |
| `eksen`, `kamera_tarafi` | ≥ 2 kişide evet | yönetmen | 180°'nin kaynağı |
| `ekran_yonu` | yolculuk ve kovalamacada | yönetmen | `soldan_saga` / `sagdan_sola`; seri boyunca `EVREN/<SERI>/EKRAN_YONU.json` ile tutarlı |
| `kurulumlar` | evet | yönetmen | Bu sahnede kullanılanlar |
| `isik{ana, dolgu, arka}` | evet | yönetmen | Kaynak id'leri |
| `yasaklar` | hayır | yönetmen | G1 sorularına gider |
| `giris_durumu`, `cikis_durumu` | evet | yönetmen (hikâye uçlarını içerir, Y57) | **Sahne sözleşmesi** |
| `_derlenir.{ana_kareler, yasak_ardisik}` | — | kod | |

#### 4.5.6 Plan düzeyi `zanaat` alanları (yönetmenin yazdıkları)

| Alan | Tür / değerler | Zorunlu | Denetim |
|---|---|---|---|
| `kod` | `"S12-P02"` | evet | tekil |
| `sahne_grubu` | `"S12"` | evet | haritada var |
| `plan_tipi` | RE `plan_sure_aralik_sn` anahtarları | evet | süre aralığı |
| `klip_sn` | 8 / 10 | evet | RE `klip_sn` |
| `kaynak_klip` | plan no / null | evet | Doluysa bu planın görseli ve videosu yoktur; Memmet atlar |
| `kamera.{kurulum, kadraj, aci, lens_mm?, hareket_tipi, hareket_yonu, odak}` | sözlükler | evet (`lens_mm` kurulumdan gelir) | Y19, Y27 |
| `eksen_gecis` | bool | evet | Y17 |
| `kadrajdakiler[]` | `{id, olcek, yuz_acisi, konusur, kimlik_demiri, gorunen[]}` | evet | Geometriyle karşılaştırılır (Y14, Y28); `referans` bundan derlenir |
| `baslangic_durumu` | `"miras"` / `{"fark": {...}, "neden": "..."}` / tam durum | evet | Tam durum yalnız `yeni_sahne`'de; `fark` yalnız `zaman_atlama`'da ya da kadraj dışı gerekçeyle |
| `eylem_zinciri[]` | adım (§4.5.8) | insanlı veya yaratıklı planda evet | Y01–Y10 |
| `bitis_durumu` | `"derlenir"` / beklenen tam durum | evet | Yazılmışsa kodun hesabına eşit olmalı (Y10) |
| `ekran_disi_ses` | `{replik, karakter, kaynak: "plan:<no>"\|"tts", bas_sn, sure_sn}` / null | hayır | Y33–Y35; `tts` yalnız ses tanıtım kuralıyla |
| `zincir` | §4.5.9 | evet | Y40–Y43, Y54–Y56 |
| `kesme` | `{tip, ses_tasma_sn}` (`ses_tasma_sn` > 0 L, < 0 J) | evet | Y36–Y38 |
| `isik_degisimi` | `{kaynak, yeni_durum, adim}` / null | hayır | Y23 |
| `yasaklar` | [str] | hayır | Sahne yasaklarına eklenir |
| `ekranda_bilgi` | Türkçe tek cümle | evet | Seyirci özetiyle karşılaştırılır; seyirciye verilmez |
| `risk_uretim` | `dusuk` / `orta` / `yuksek` | evet | Yüksekse yedek istem ve Z2 değerlendirmesi |
| `istem_elle` | `{neden}` / yok | hayır | O plan için derlemeyi kapatır; film başına ≤ %5 (tahmin) |
| hikâye alanları | §4.5.2 | — | Senaristin; yönetmen yalnız plana yerleştirir |

#### 4.5.7 Durum nesnesi (sözleşme, başlangıç, bitiş, defter: hepsi aynı yapı) **(değişti)**
```json
{
 "karakterler": {
  "<id>": {"mekan": "...", "isaret": "M1", "poz": "ayakta", "yuz_yonu": "guney | <derece> | {\"hedef\": \"<id>\"}",
           "bakis": {"hedef": "<id>"}, "kostum": "mara_k1", "kostum_durumu": ["kapusonu_inik"],
           "gorunum": {"kir": 1, "islak": false, "yaralar": []},
           "eller": {"sag": {"tutar": "fener", "yer": "kalca_hizasi", "sekil": "tutus_tam"},
                     "sol": {"tutar": null, "yer": "yanda", "sekil": "serbest"}},
           "ifade": "sert (isteğe bağlı)", "gizli_arkasinda": null}
 },
 "nesneler": {"<id>": {"kimde": "<karakter>", "el": "sol|sag", "durum": "yanik"}
              /* ya da */ , "<id2>": {"nerede": "<oge|isaret>", "durum": "..."}},
 "mekan_durumu": {"kapi": "yari_acik", "ocak_atesi": "yanik"}
}
```
- **Olgular** kameradan bağımsızdır. `bitis[N] ≡ baslangic[N+1]` karşılaştırması yalnız olgularla yapılır.
- **Kadraj bilgisi** yalnız `zanaat.kadrajdakiler` ve `_derlenir`'dedir. Elin görünüp görünmemesi bir olgu değildir: `kadrajdakiler[].gorunen` ve geometri belirler.
- `gizli_arkasinda`: karakter mekândadır ama bir engel öğesinin arkasındadır. Görüş hattı hesabı bu bilgiyi kullanır.
- Hikâye katmanı ([SN]) aynı şemanın alt kümesini yazar. `bilgi` (kim neyi biliyor) yalnız `DUNYA_DEFTERI.hikaye` katmanındadır.

#### 4.5.8 Eylem adımı **(değişti)**
```json
{"id": "a1", "bas": 0.5, "bit": 2.5, "ozne": "mara", "tur": "fiziksel | mikro | konusma",
 "fiil": "<fiil_sozlugu id>", "govde": "sag_kol | sol_el | bas | gozler | tum_beden | kuyruk | kanat ...",
 "yon": "ileri | geri | sola | saga | yukari | asagi", "hedef": "<karakter | nesne | oge | isaret>",
 "olcu": "iki_yavas_adim | 15cm | 90_derece | hafif", "el_sekli": "kiskac | tutus_tam | ...", "hiz": "yavas | normal | hizli",
 "etki": {"mara.eller.sol.tutar": "anahtar", "anahtar.kimde": "mara", "anahtar.el": "sol"}}
```
Konuşma adımı:
```json
{"id": "a2", "bas": 2.0, "bit": 5.4, "ozne": "mara", "tur": "konusma", "fiil": "konusur", "replik": "R0121", "cumleler": [0, 1]}
```
- Sağ ve sol **daima karakterin kendi** sağı ve soludur (yaratıkta da: "its right").
- Kadraja göre yön yalnız `kadraja_girer` / `kadrajdan_cikar` fiillerinde yazılır ve geometriyle karşılaştırılır.
- Sürekli hâller (koşuyor, yürüyor) **poz** olarak yazılır, adım olarak yazılmaz.

#### 4.5.9 Zincir nesnesi (niyet: `zanaat.zincir`; yürütme: `uretim.zincir`) **(değişti)**
```json
"zanaat": {"zincir": {"gecis_turu": "devam", "onceki_plan": 70, "baslangic": "son_kare",
                      "ebeveyn": "070@kesme", "dogal_durak": true, "bitis_sabitle": false}},
"uretim": {"zincir": {"dalga": 2, "kaynak": "SIRALI_VIDEO/070.mp4@6.6", "kesim_sn": 6.6, "derinlik": 1,
                      "yedek": "SIRALI_GORSEL/_ADAYLAR/071_plan.jpg", "yedege_dustu": false},
           "durum_dondu": {"bas_ozet": "c41f…", "bit_ozet": "9a07…"}}
```

| Alan | Değerler |
|---|---|
| `gecis_turu` | `yeni_sahne` · `eylem_kesme` · `devam` · `kurulum_donusu` · `araya_kesme` · `zaman_atlama` |
| `baslangic` | `kart` (yeni sahne: plaka + karakter kartları) · `ana_kare` (kurulumun ilk planı; ebeveyn plaka ya da başka kurulumun ana karesi) · `turev` (aynı kurulumun onaylı karesinden + durum farkı) · `son_kare` (Z1: önceki klibin kesme anındaki gerçek kare) |
| `ebeveyn` | `plaka:<id>` · `K3@123` (kurulum @ ana kare planı) · `<no>@kesme` (Z1) |
| `dogal_durak` | `devam`'da zorunlu. `true` ise doğrudan bitişik zincire izin verilir (Y54) |
| `bitis_sabitle` | Z2: bu klibin Bitir yuvasına görsel konur. Kaynağı: sonraki plan `devam` ise onun **planlanmış** görseli, değilse `NNN_son.jpg` (Y41) |

#### 4.5.10 `_derlenir` (yalnız kod yazar)
`baslangic_durumu` ve `bitis_durumu` (çözülmüş) · `sure_sn` · `kesme_nokta_sn` · `kadraj_konumu` · `kadraj_sirasi` · `kamera_tarafi` · `bakis_kadrajda` · `isik_kadrajda` · `ekran_yonu` · `replik_zaman` · `agiz_gorunur` · `dinleyen_agiz` · `ayna_yasak` · `acik_parmak` · `gorunmesi_gerekenler` · `goz_yukseklik_farki` · `referans`.

#### 4.5.11 Sözlükler (`veri/plan_sozlukleri.json`; EN ve TR karşılıklarıyla)

| Sözlük | Değerler | Kaynak |
|---|---|---|
| `kadraj` | EG · G · OG · O · OY · Y · CY · D (ekleme/makro) · OU (omuz üstü) · IK (ikili) | ZN §3.1; kademe RE `olcek_kademeleri` |
| kişi `olcek` | kadraj basamakları + `on_plan_omuz` · `el` · `siluet` | |
| `aci` | `goz_hizasi` · `alcak` · `yuksek` · `kus_bakisi` | |
| `lens_mm` → yatay görüş açısı | 24 → 73,7° · 28 → 65,5° · 35 → 54,4° · 50 → 39,6° · 85 → 23,9° | (hesap: 2·atan(18/f)) |
| `hareket_tipi` | ZN §3.6 | ZN |
| `poz` | ayakta, yuruyor, kosuyor, diz_cokmus, comelmis, oturuyor, egilmis, yerde | |
| `yuz_acisi` (kameraya göre yaw) | `on` 0–15° · `3/4` 15–60° · `profil` 60–100° · `sirt` > 100° · `gorunmez` | 15° A2 §4; diğerleri (tahmin) |
| `el.sekli` → açık parmak | `serbest` (—) · `acik_avuc` (5) · `yumruk` (0) · `kiskac` (başparmak + işaret, 2; diğer 3 kıvrık) · `uc_parmak` (3) · `tutus_tam` (0, sarılı) · `isaret` (1) | kesin karar 2 |
| `el.yer` | yanda, kalca_hizasi, govde_onunde, omuz_hizasi, bas_ustu, cepte, arkada, `<oge/nesne id>` | EN'de "chest" yerine "in front of the torso" ("chest" filtre kelimesi, DR) |
| `zincir.gecis_turu`, `zincir.baslangic` | §4.5.9 | |
| `kesme.tip` | ZN §3.4 + `duz` + `devam` | |

**Fiil sözlüğü** (`veri/fiil_sozlugu.json`, ≈40 fiil (tahmin)). Alanları: `tur`, `zorunlu`, `en_sablon` (tek kişi öznesiz / iki kişi adlı), **`tr_sablon`** (yeni: kör paket, animatik şeridi, çekim listesi için), `etki_sablonu`, `sure_carpani` (ders defteri kalibre eder, başlangıçta 1,0). Testler şablonlarda filtre kelimesi ve yasak sonuç fiili bulunmadığını denetler. Örnekler:

| id | zorunlu | EN şablon | TR şablon | etki |
|---|---|---|---|---|
| `yurur` | hedef ya da yon, olcu | `walks {olcu} toward the {hedef}` | `{hedef} yönüne {olcu} yürür` | `ozne.isaret` |
| `uzanir` | govde, hedef, olcu | `extends the empty {side} arm toward the {hedef}, fingers stopping {olcu} above it` | `boş {taraf} kolunu {hedef} doğru uzatır` | `<el>.yer` |
| `kavrar` | govde (el), el_sekli, hedef | `the thumb and index finger close around the {hedef}, the other three fingers stay curled` (kıskaç; 15 kelime) | `başparmak ve işaret parmağıyla {hedef} kavrar` | `nesne.kimde/el`, `<el>.tutar/sekil` |
| `iter` / `ceker` | govde, hedef, olcu | `pushes / pulls the {hedef} {olcu} with the {side} hand` | | `oge` durumu ("opens" yasak) |
| `bakis_kaydirir` | hedef | `eyes shift to the {hedef}` | `gözleri {hedef} kayar` | `bakis` |
| `konusur` | replik | `{Ad} {ton_fiili}, {veo_ses_tarifi}: "{metin}"` | `{etiket}, {ton_tr}: "{metin}"` | — |
| `kadraja_girer` | yon | `enters from frame {yon}` | `kadraja {yon}dan girer` | kadraj listesi |
| `cene_sikar` … (mikro) | — | `the jaw tightens, mouth closed` | `çenesi kasılır` | — |

#### 4.5.12 Tam örnek: S12 "Kapıdaki kaptan" (EMBERFALL dünyası, revize şema)
Gece. Mara kulübenin kapısını yarı açık tutuyor. Kaptan Voss dışarıda, sol elinde meşale. Ember içeride, odun yığınının arkasında saklı; seyirci bunu biliyor (ironi). 16 plan hedefleniyor.

**Seri evreni krokisi** (`EVREN/EMBERFALL/mekanlar/mara_kulubesi/kroki.json`, kısaltılmış):
```json
{
 "id": "mara_kulubesi", "surum": 1, "birim": "metre",
 "yonler": "x = dogu, y = kuzey; yon_derece 0 = kuzey (pusula)", "sinir": [[0, -4], [5, 4]],
 "duvarlar": [
  {"id": "guney_duvar", "a": [0, 0], "b": [5, 0], "aciklik": [{"id": "kapi", "x": [2.0, 3.0]}]},
  {"id": "bati_duvar", "a": [0, 0], "b": [0, 4], "aciklik": [{"id": "pencere", "y": [2.0, 3.0]}]},
  {"id": "kuzey_duvar", "a": [0, 4], "b": [5, 4]}, {"id": "dogu_duvar", "a": [5, 0], "b": [5, 4]}],
 "ogeler": [
  {"id": "kapi", "tur": "kapi", "konum": [2.5, 0.0], "mentese": "bati_kasa", "acilis": "iceri"},
  {"id": "surgu", "tur": "kilit", "konum": [3.0, 0.1], "not": "dogu kasa ic yuzu, demir, yuvarlak topuz"},
  {"id": "ocak", "tur": "ocak", "konum": [4.0, 3.8], "yukseklik_m": 1.2},
  {"id": "odun_yigini", "tur": "esya", "konum": [4.7, 1.2], "yukseklik_m": 1.0, "engel": true},
  {"id": "basamak", "tur": "zemin", "konum": [2.5, -1.0], "not": "dis, karli tek basamak"}],
 "isaretler": {"M1": {"konum": [2.5, 0.0], "ad": "kapi esigi"}, "M2": {"konum": [2.5, -1.2], "ad": "basamak alti"},
               "M3": {"konum": [4.0, 3.0], "ad": "ocak onu"}, "M4": {"konum": [4.7, 1.2], "ad": "odun yigini arkasi"}},
 "isik_kaynaklari": [{"id": "ocak_atesi", "konum": [4.0, 3.8], "tur": "ates", "renk": "sicak", "varsayilan": "sonuk"},
                     {"id": "ay", "konum": "gok_guneybati", "tur": "ay", "renk": "soguk"}],
 "plakalar": {
  "dis_kuzeydoguya": {"konum": [0.5, -3.0], "yon_derece": 40, "lens_mm": 28, "yukseklik": "goz"},
  "ic_guneye":       {"konum": [2.5, 3.2], "yon_derece": 180, "lens_mm": 28, "yukseklik": "goz"},
  "ic_doguya":       {"konum": [1.0, 2.0], "yon_derece": 90, "lens_mm": 28, "yukseklik": "goz"}}
}
```
Plakalar nötr durumdadır (ateş sönük, kapı kapalı; [GS] §5.3). Ateşin yanık durumu istemle verilir.

**Film mekânı ve sahne grubu** (`SAHNELER.json` içinden):
```json
"mekanlar": {"mara_kulubesi": {"evren": "EVREN/EMBERFALL/mekanlar/mara_kulubesi@1", "kurulumlar": {
  "K1": {"konum": [1.0, -0.9], "yon_derece": 75, "yukseklik": "goz", "lens_mm": 28, "varsayilan_kadraj": "OG", "ebeveyn": "plaka:dis_kuzeydoguya", "not": "disaridan ikili konum"},
  "K2": {"konum": [2.0, -1.9], "yon_derece": 24, "yukseklik": "goz", "lens_mm": 50, "varsayilan_kadraj": "OU", "ebeveyn": "K1", "not": "Voss'un SOL omzu ustunden Mara"},
  "K3": {"konum": [2.0, 0.6], "yon_derece": 157, "yukseklik": "goz", "lens_mm": 50, "varsayilan_kadraj": "OU", "ebeveyn": "plaka:ic_guneye", "not": "Mara'nin SAG omzu ustunden Voss"},
  "K4": {"konum": [1.8, -1.0], "yon_derece": 43, "yukseklik": "goz", "lens_mm": 85, "varsayilan_kadraj": "Y", "ebeveyn": "K2", "not": "Mara tekli"},
  "K5": {"konum": [1.7, -0.2], "yon_derece": 135, "yukseklik": "goz", "lens_mm": 85, "varsayilan_kadraj": "Y", "ebeveyn": "K3", "not": "Voss tekli"},
  "K6": {"konum": [2.1, 0.5], "yon_derece": 114, "yukseklik": "goz", "lens_mm": 85, "varsayilan_kadraj": "D", "ebeveyn": "K3", "not": "surgu ekleme"},
  "K7": {"konum": [3.5, 2.0], "yon_derece": 124, "yukseklik": "alcak", "lens_mm": 35, "varsayilan_kadraj": "O", "ebeveyn": "plaka:ic_doguya", "not": "odun yigini; eksen sahnesi disi"}}}},
"sahne_gruplari": {"S12": {
  "hikaye": {"sahne": "S12", "parti": 1},
  "mekan": "mara_kulubesi", "zaman": {"gun": 2, "gun_saati": "gece", "hava": "hafif_kar", "atlama": "yok"},
  "sahne_tipi": "diyalog", "sure_hedef_sn": 95, "plan_hedef": 16, "kalip": "yukselen_diyalog",
  "eksen": ["mara", "voss"], "kamera_tarafi": "bati", "ekran_yonu": null,
  "kurulumlar": ["K1", "K2", "K3", "K4", "K5", "K6", "K7"],
  "isik": {"ana": "mesale", "dolgu": "ay", "arka": "ocak_atesi"},
  "yasaklar": ["ikinci_ates_kaynagi", "ucuncu_kisi", "acik_pencere"],
  "giris_durumu": {
   "karakterler": {
    "mara": {"mekan": "mara_kulubesi", "isaret": "M1", "poz": "ayakta", "yuz_yonu": "guney", "bakis": {"hedef": "voss"},
             "kostum": "mara_k1", "kostum_durumu": ["kapusonu_inik", "eldivensiz"], "gorunum": {"kir": 1, "islak": false, "yaralar": []},
             "eller": {"sol": {"tutar": null, "yer": "dogu_kasa_ic", "sekil": "tutus_tam"},
                       "sag": {"tutar": null, "yer": "kapi_kenari", "sekil": "tutus_tam"}}},
    "voss": {"mekan": "mara_kulubesi", "isaret": "M2", "poz": "ayakta", "yuz_yonu": "kuzey", "bakis": {"hedef": "mara"},
             "kostum": "voss_k1", "kostum_durumu": ["migfer_takili"], "gorunum": {"kir": 0, "islak": true, "yaralar": []},
             "eller": {"sol": {"tutar": "mesale", "yer": "omuz_hizasi", "sekil": "tutus_tam"},
                       "sag": {"tutar": null, "yer": "yanda", "sekil": "serbest"}}},
    "ember": {"mekan": "mara_kulubesi", "isaret": "M4", "poz": "comelmis", "gizli_arkasinda": "odun_yigini"}},
   "nesneler": {"mesale": {"kimde": "voss", "el": "sol", "durum": "yanik"}},
   "mekan_durumu": {"kapi": "yari_acik", "surgu": "acik", "ocak_atesi": "yanik"}},
  "cikis_durumu": {"karakterler": {"voss": {"isaret": "M1"}, "mara": {"isaret": "M1_ici"}},
                   "mekan_durumu": {"kapi": "tam_acik"}},
  "_derlenir": {"ana_kareler": {"K1": 120, "K2": 121, "K5": 122, "K3": 123, "K6": 124},
                "yasak_ardisik": [["K2", "K4"], ["K4", "K2"]]}}}
```
`cikis_durumu` örnekte yalnız farklarla gösterildi; gerçek dosyada tam durum yazılır.

**Plan 121** (diyalog, omuz üstü):
```json
{"no": 121, "sira": 121, "parti": 1, "kullanim": {"bas": 0.6, "sure": 3.6}, "amac": "Mara soğukkanlı rol yapıyor",
 "replik": {"id": "R0121", "karakter": "mara", "metin": "It's late, Captain. What do you want?",
            "cumleler": [{"en": "It's late, Captain.", "tr": "Saat geç oldu, Kaptan."}, {"en": "What do you want?", "tr": "Ne istiyorsun?"}],
            "ton_fiili": "says coldly", "seviye": "normal", "veo_metin": null},
 "zanaat": {
  "kod": "S12-P02", "sahne_grubu": "S12", "plan_tipi": "diyalog", "klip_sn": 8, "kaynak_klip": null,
  "hedef_duygu": "gerilim", "yogunluk": 6, "ironi": {"id": "ir_ember_ic", "rol": "surdur"},
  "kamera": {"kurulum": "K2", "kadraj": "OU", "aci": "goz_hizasi", "hareket_tipi": "sabit", "hareket_yonu": null, "odak": "mara"},
  "eksen_gecis": false,
  "kadrajdakiler": [
   {"id": "mara", "olcek": "OY", "yuz_acisi": "3/4", "konusur": true, "kimlik_demiri": true, "gorunen": ["yuz", "sag_el"]},
   {"id": "voss", "olcek": "on_plan_omuz", "yuz_acisi": "sirt", "konusur": false, "gorunen": ["sol_omuz", "migfer_arkasi", "sol_el"]}],
  "baslangic_durumu": "miras",
  "eylem_zinciri": [
   {"id": "a1", "bas": 0.5, "bit": 1.8, "ozne": "mara", "tur": "mikro", "fiil": "cene_kaldirir", "govde": "bas", "olcu": "hafif"},
   {"id": "a2", "bas": 2.0, "bit": 5.4, "ozne": "mara", "tur": "konusma", "fiil": "konusur", "replik": "R0121", "cumleler": [0, 1]}],
  "bitis_durumu": "derlenir", "ekran_disi_ses": null,
  "zincir": {"gecis_turu": "eylem_kesme", "onceki_plan": 120, "baslangic": "ana_kare", "ebeveyn": "K1@120", "bitis_sabitle": false},
  "kesme": {"tip": "L", "ses_tasma_sn": 1.2},
  "isik_degisimi": null, "yasaklar": ["agiz_onu_engel"],
  "ekranda_bilgi": "Mara kapıyı yarı açık tutuyor ve Kaptan'a soğuk davranıyor; onu içeri almak istemiyor.",
  "risk_uretim": "orta",
  "ses": "(ses uzmanı: flow_sound, efektler[{adim: \"a1\"…}], diyalog.yol)"},
 "_derlenir": {"sure_sn": 3.6, "kesme_nokta_sn": 4.2, "referans": ["mara", "voss"],
  "kadraj_konumu": {"mara": "sol_ucte_bir", "voss": "sag_on"}, "kadraj_sirasi": ["mara", "voss"], "kamera_tarafi": "bati",
  "bakis_kadrajda": {"mara": "kadraj_sagi"}, "isik_kadrajda": {"ana": "on_sol (mesale)", "arka": "orta (ocak, kapi icinden)", "dolgu": "soguk ay"},
  "replik_zaman": {"bas": 2.0, "bit": 5.4}, "agiz_gorunur": {"mara": "tam"}, "dinleyen_agiz": {"voss": "gorunmez"},
  "ayna_yasak": true, "gorunmesi_gerekenler": ["mara.yuz", "mara.eller.sag", "voss.eller.sol:mesale", "mesale", "kapi"]},
 "uretim": {}, "denetim": {"G1": null, "V1": null, "V2": null, "V3": null, "K1": null}}
```
- `a1` konuşmadan 0,2 sn önce biter (Y02b).
- Kesme 4,2'dedir (= 0,6 + 3,6). Sözün kalan 1,2 sn'si (4,2–5,4) L taşmasıyla 122'nin üstünde duyulur.
- Diyalog formülü (ZN §2.3): 7 kelime, 2 cümle → 0,4 + 2,8 + 0,25 + 0,5 = **3,95 sn** (hesap). Görüntü 3,6 + taşma 1,2 = 4,8 ≥ 3,95 (Y31).

**Plan 122** (tepki, yalnız farklı alanlar):
```json
{"no": 122, "kullanim": {"bas": 0.5, "sure": 3.0}, "replik": null,
 "zanaat": {"kod": "S12-P03", "plan_tipi": "tepki", "klip_sn": 8,
  "kamera": {"kurulum": "K5", "kadraj": "Y", "aci": "goz_hizasi", "hareket_tipi": "yavas_ileri", "odak": "voss"},
  "kadrajdakiler": [{"id": "voss", "olcek": "Y", "yuz_acisi": "3/4", "konusur": false, "kimlik_demiri": true, "gorunen": ["yuz"]}],
  "baslangic_durumu": "miras",
  "eylem_zinciri": [
   {"id": "a1", "bas": 0.5, "bit": 2.0, "ozne": "voss", "tur": "mikro", "fiil": "bakis_kaydirir", "govde": "gozler",
    "hedef": "ocak_atesi", "etki": {"voss.bakis": {"hedef": "ocak_atesi"}}},
   {"id": "a2", "bas": 2.0, "bit": 3.5, "ozne": "voss", "tur": "mikro", "fiil": "cene_sikar", "govde": "bas"}],
  "ekran_disi_ses": {"replik": "R0121", "karakter": "mara", "kaynak": "plan:121", "bas_sn": 0.0, "sure_sn": 1.2},
  "zincir": {"gecis_turu": "eylem_kesme", "onceki_plan": 121, "baslangic": "ana_kare", "ebeveyn": "K3@123", "bitis_sabitle": false},
  "kesme": {"tip": "duz", "ses_tasma_sn": 0.0},
  "ekranda_bilgi": "Voss, Mara'nın arkasında, kulübenin içindeki ateşe bakıyor; bir şeyden şüpheleniyor.",
  "risk_uretim": "dusuk", "merak_ac": ["m07"]},
 "_derlenir": {"kadraj_konumu": {"voss": "sag_ucte_bir"}, "bakis_kadrajda": {"voss@bas": "kadraj_solu", "voss@bit": "kadraj_solu_ic"},
  "dinleyen_agiz": {"voss": "kapali"}, "ayna_yasak": true}}
```

**Plan 124** (ekleme; yalnız el görünüyor):
```json
{"no": 124, "kullanim": {"bas": 1.0, "sure": 2.4},
 "zanaat": {"kod": "S12-P05", "plan_tipi": "ekleme", "klip_sn": 8,
  "kamera": {"kurulum": "K6", "kadraj": "D", "aci": "goz_hizasi", "hareket_tipi": "sabit", "odak": "surgu"},
  "kadrajdakiler": [{"id": "mara", "olcek": "el", "yuz_acisi": "gorunmez", "konusur": false, "gorunen": ["eller.sol", "sol_kol_yeni"]}],
  "baslangic_durumu": "miras",
  "eylem_zinciri": [
   {"id": "a1", "bas": 0.5, "bit": 2.5, "ozne": "mara", "tur": "fiziksel", "fiil": "el_kaydirir", "govde": "sol_el",
    "yon": "asagi", "hedef": "surgu", "olcu": "15cm", "etki": {"mara.eller.sol.yer": "surgu_topuzu", "mara.eller.sol.sekil": "serbest"}},
   {"id": "a2", "bas": 2.5, "bit": 4.0, "ozne": "mara", "tur": "fiziksel", "fiil": "kavrar", "govde": "sol_el", "el_sekli": "kiskac",
    "hedef": "surgu", "etki": {"mara.eller.sol.sekil": "kiskac"}}],
  "ekran_disi_ses": {"replik": "R0123", "karakter": "voss", "kaynak": "plan:123", "bas_sn": 0.0, "sure_sn": 1.0},
  "zincir": {"gecis_turu": "araya_kesme", "onceki_plan": 123, "baslangic": "ana_kare", "ebeveyn": "K3@123", "bitis_sabitle": false},
  "kesme": {"tip": "eylem", "ses_tasma_sn": 0.0},
  "ekranda_bilgi": "Kapının iç tarafında demir bir sürgü var; Mara gizlice ona uzanıyor.",
  "risk_uretim": "orta", "kurulum": ["kur_surgu"]},
 "_derlenir": {"kesme_nokta_sn": 3.4, "acik_parmak": {"mara.sol": 2}, "ayna_yasak": true}}
```
Kesme noktası 3,4, `a2`'nin %60'ındadır: 2,5 + 0,6 × 1,5 = 3,4 (hesap; Y38).

**`kroki.py`'nin hesapladıkları** (tanjant izdüşümü: konum = tan(açı) / tan(yarım görüş açısı); −1/3'ten küçükse sol üçte bir, +1/3'ten büyükse sağ üçte bir; tur 1'deki hesap aynen geçerli):

| Kurulum | Lens / görüş | Mara (M1) | Voss (M2) | Meşale | Ocak | Taraf |
|---|---|---|---|---|---|---|
| K1 | 28 / 65,5° | −0,44 sol | +0,77 sağ | +0,86 | dışı | batı |
| K2 | 50 / 39,6° | −0,45 sol | +0,57 sağ (ön) | −0,39 (ana ışık sol-ön) | −0,23 (kapıdan arka ışık) | batı |
| K3 | 50 / 39,6° | −0,84 sol (ön omuz) | +0,36 sağ | +0,83 | arkada | batı |
| K4 | 85 / 23,9° | −0,66 sol | dışı | dışı | dışı | batı |
| K5 | 85 / 23,9° | dışı | +0,52 sağ | dışı (sağ-alt) | arkada | batı |

Bu hesaptan üç sonuç çıkıyor:
- Bütün kurulumlarda Mara solda, Voss sağdadır. 180° kuralı kâğıtta kanıtlanmıştır.
- K2'den K4'e doğrudan kesilemez: açı farkı 20°, ölçek farkı 1 kademe. Bu, RE `aci_min_fark_derece` 30 ve `olcek_kademe_min_fark` 2 sınırlarının ikisinin de altındadır, bu yüzden `yasak_ardisik` listesine girer.
- K2'nin görüş konisinde M4 (Ember) var, ama güney duvarı ve `engel` olan odun yığını arkasında kalıyor. Bu yüzden `gorunmesi_gerekenler` listesine girmez.

**Kalan planlar (özet)**

| no | kod | kurulum / kadraj | tip | özet |
|---|---|---|---|---|
| 120 | S12-P01 | K1 / OG (IK, sessiz) | kurulus | a1 [0,5–2,0] Voss meşaleyi omuz hizasına kaldırır; a2 [2,0–3,5] Mara sağ eliyle kapıyı 10 cm kapatır. Aynı anda tek özne hareket eder |
| 123 | S12-P04 | K3 / OU (Mara'nın sağ omzu) | diyalog | R0123 Voss: "Smoke from your chimney. On a night you swore you had no wood left." 14 kelime → 0,4 + 5,6 + 0,25 + 0,5 = 6,75 sn ≤ 8 sn klip (hesap, ZN §2.3); L taşma 1,0 sn → 124 |
| 125 | S12-P06 | K4 / Y | tepki | a1 yutkunur, ağız kapalı; a2 gözler 0,6 sn içeri kayar (ironi; bakış ≥ 0,5 sn); 124 → 125 açı farkı ≥ 30° |
| 126 | S12-P07 | K7 / O (alçak) | ekleme (araya kesme) | Odun yığınının arkasından pullu bir kuyruk ucu 20 cm sağa kayıp kaybolur (`kuyruk_kaydirir`); Ember'in olgularını değiştirir, Mara ve Voss'unkileri değiştirmez |

**Derlenen istemler** (`{X_KIMLIK}` = evrendeki kimlik dizesi, kelimesi kelimesine)
- **P121 `hareket_istem`** (iki kişi → adlar yazılır; 53 kelime (sayım), Y46 ≤ 75):
  `Static over-the-shoulder shot. 0.5-1.8s: Mara lifts her chin slightly, eyes on Voss. 2-5.4s: Mara says coldly, in a low, warm, slightly husky female voice: "It's late, Captain. What do you want?" Voss stays still, seen from behind, silent. 5.4-8s: Mara holds still, mouth closed. Sound: wind over snow, torch flame crackling. No music.`
- **P122** (tek kişi → öznesiz):
  `Slow push-in, close-up. 0.5-2s: listens silently, mouth closed; eyes shift toward frame left, past the doorway into the cabin. 2-3.5s: the jaw tightens, mouth still closed. 3.5-8s: holds still. Sound: wind, torch flame crackling. No music.`
- **P124** (ekleme, yalnız el):
  `Static macro insert. 0.5-2.5s: the left hand slides 15 cm down the inner side of the wooden door frame to the round knob of an iron bolt. 2.5-4s: the thumb and index finger close around the knob, the other three fingers stay curled. 4-8s: holds still. Sound: fabric rustle, faint creak of wood, muffled wind outside. No music.`
- **P121 `gorsel_istem`** ([GS] modülü; anlık görüntü):
  `Over-the-shoulder medium close-up, eye-level, 50mm lens, night. Foreground on frame right, softly out of focus: Voss seen from behind — {VOSS_KIMLIK} — his left shoulder and the back of his helmet, a burning torch held in his left hand at shoulder height. On the left third of frame: Mara — {MARA_KIMLIK} — standing in the half-open doorway of a log cabin, body at three-quarter angle, looking toward frame right at Voss, her right hand gripping the edge of the wooden door, her left hand hidden behind the door frame, mouth closed. Warm torchlight on her face from the front-left; warm hearth glow behind her inside the cabin; cold moonlight on the snow. Light snow falling. {STIL_EKI}`

#### 4.5.13 Miras, derleme, dondurma ve geriye uyumluluk kuralları (`dunya_defteri.py` şartnamesi)
1. **Miras:** `baslangic_durumu: "miras"` → önceki planın (`zincir.onceki_plan`) çözülmüş bitiş durumu alınır.
   - `{"fark": {...}, "neden": "..."}` yalnız açıklanan farkları uygular.
   - Fark yalnız şu durumlarda geçerlidir: `zaman_atlama`, `yeni_sahne` ya da kadraj dışında olduğu açıklanan bir değişiklik.
   - Gerekçesiz fark HATA'dır (Y12).
2. **Etki katlama:** Bitiş durumu = başlangıç durumu + adımların `etki` alanları (zaman sırasıyla). Yazar beklenen bitiş durumunu yazdıysa kodun hesabıyla karşılaştırılır (Y10).
3. **Araya kesme ve paralel kurgu:** Dünya defteri tektir ve hikâye zamanına göre sıralıdır. `araya_kesme` planı yalnız kendi öznelerinin olgularını değiştirir.
4. **Geri dönüş (flashback):** Ayrı zaman çizgisinde tutulur (`zaman_cizgisi: "gecmis_1"`). Ana defteri etkilemez. Süresi ≤ 20 sn (RE `geri_donus_max_sn`).
5. **Klip bölme:** `kaynak_klip` planının durumu, kaynak klibin adımlarının `kullanim.bas` anına kadar uygulanmasıyla hesaplanır. Parçalar arasında ≥ 0,4 sn atlanır (RE). Ya da [KU] senkron korumalı formülü kullanılır (Y39).
6. **Dondurma (yeni):** Görsel üretildiği anda planın çözülmüş başlangıç ve bitiş durumu `uretim.durum_dondu`'ya özetiyle yazılır.
   - Kurgu sırası ya da kesme değişikliğinden sonra komşuluk denetimi **dondurulmuş** durumlarla yapılır (Y58).
   - Planın olguları sonradan değişirse görseli `bayat` olur.
7. **Derleme tek yönlüdür:** `zanaat` → istemler. İstem özeti `uretim.istem_ozeti`'ne yazılır. Elle değiştirilmiş istem fark edilir, uyarı verilir ve üstüne yazılmaz. Kalıcı istisna yalnız `istem_elle` ile yapılır.
8. **Geriye uyumluluk:** `zanaat` alanı olmayan planlar (`ORNEK_3_SAHNE`, eski filmler) bugünkü gibi çalışır. `plan_denetim.py` bu planlara yalnız eski kuralları uygular. `film.py` yönetmen aşamasını "eski biçim" diye atlar.
9. **Üst düzey `bitis_karesi`** (Memmet'in bugünkü alanı): `zincir.bitis_sabitle` doluysa derlenir. Değeri sonraki `devam` planının no'sudur ya da `NNN_son` olur.

---

### 4.6 Yazılması / değişmesi gereken kod (araç, ne yapar, girdi/çıktı, öncelik)

Ortak kurallar:
- Araçlar `YZ_FILM/ARACLAR/` altında, mevcut stilde yazılır: Türkçe docstring ve kullanım metni, `sys.stdout.reconfigure`, rapor klasörü ayardan, çıkış kodu orkestratör tablosundan.
- Python 3.10 ve Windows. 3.11+ özellikleri yok ([UM] R8).
- P0 araçları ağsızdır ve GPU istemez. Yalnız PIL ve numpy kullanır.
- **Öncelik:** **P0** = bulutta sahte testle yazılır ve görsel aşamasından önce şarttır · **P1** = ilk video partisinden önce · **P2** = ilk filmden sonra.

**4.6.1 Sahibi olduğum yeni araçlar**

| Araç | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|
| `veri/plan_sozlukleri.json`, `veri/fiil_sozlugu.json` | §4.5.11 sözlükleri; EN ve TR şablonları; etki şablonları; `sure_carpani` | — | P0 |
| `plan_sema.py` | Plan, harita ve kroki şema denetimi; sözlük değerleri; **sahiplik** (§4.5.2; [CM] `_sahip` ile); `_derlenir`'e elle yazma = HATA. `jsonschema` varsa onu kullanır, yoksa yerleşik doğrulayıcıyı | `PLANLAR/*.json`, `HARITA_*.json`, `kroki.json` → `RAPORLAR/sema.json` | P0 |
| `kroki.py` (kütüphane + CLI) | Tanjant izdüşümüyle kadraj konumu ve sırası; eksen tarafı; duvar ve engel öğeyle görüş hattı; bakış, ışık ve ekran yönünün kadrajdaki karşılığı; göz yüksekliği farkı; ağız görünürlüğü; ayna yasağı; görünmesi gerekenler; plaka `gorunen` listesi; kurulum çiftleri arası açı ve ölçek farkı (`yasak_ardisik`); `--karsilikli` (standart kurulum önerileri; betik görevden önce çalıştırır); `--ciz` (PIL ile PNG) | kroki + harita + planlar → `_derlenir`, `KROKI/*.png`, `RAPORLAR/kroki.json` | P0 |
| `plan_denetim.py` | ZN Z0 #4–6, #11–19 + bütün Y kuralları. Modlar: `--harita`, `--sahne Sxx`, `--tum`. Eşikler `ritim_esikleri.json`'dan okunur | → `RAPORLAR/Z0_plan.json`, `YENIDEN_YAZ.json` | P0 |
| `plan_dili.py` (yeni) | `gorunur_tarif(plan, dil)`: kadraj sözü, kadrajdaki kişilerin etiketi ve konumu, görünür adımlar (fiil sözlüğü şablonlarıyla). Tek derleyici dört yerde kullanılır: `istem_derle --hareket` (EN), `kor_paket --kip plan` (TR), animatik eylem şeridi (TR, [KU]), çekim listesi (TR) | plan → metin | P0 |
| `istem_derle.py` (`--hareket` modülü; `--gorsel` modülü [GS]'nin) | Saniyeli adımlar; tek kişide öznesiz, iki kişide adlı; konuşmada `ton_fiili` + `veo_ses_tarifi` + `veo_metin`; `flow_sound` + `No music.`; `*_yedek`; `--zaman-bicimi aralik\|sira` (açık soru 1); istem özeti | `SAHNELER.json` → aynı dosya + `RAPORLAR/ISTEM_DERLEME.txt` | P0 |
| `plan_birlestir.py` | `PLANLAR/S*.json` → `SAHNELER.json`; kalıcı `kod → no` eşlemesi (`NO_ESLEME.json`); `sira`; `parti`; derlenen mevcut alanlar (`referans`, `duygu`, `bitis_karesi`, `motor`) | → `SAHNELER.json` | P0 |
| `kamera_agaci.py` | Plaka → ana kare → türev → planlanmış `devam` görseli sırası; `bayat` yayılımı; Gemini paket gruplaması; ağaç derinliği (Y43) | → `KAMERA_AGACI.json` | P0 |
| `cekim_listesi.py` | Eleştirmen ve insan için okunur çekim listesi: sahne başına tablo, kroki PNG'si, TR görünür tarif, derlenmiş istemler | → `CEKIM_LISTESI_P*.md` | P1 |
| `plan_ozellik.py` | Ders defteri olayına plan özellik vektörünü ekler (Ç-20) | olay + plan → olay | P1 |

**4.6.2 Başkasının aracı, benim şartnamemle**

| Araç (sahibi) | Benim payım | Öncelik |
|---|---|---|
| `dunya_defteri.py` ([GS]) | §4.5.13 çözüm kuralları; Y11–Y16, Y57, Y58; `kroki.py` içe alınır | P0 |
| `dilim.py` ([CM]) | Yönetmen brifing, harita ve plan dilimlerinin içeriği (§4.2) | P0 |
| `kor_paket.py --kip plan` ([CM] / [SN] `ekran_metni.py`) | `plan_dili` TR çıktısı; `ekranda_bilgi` yasak alanlar listesinde | P1 |
| `video_denetim.py --klip` V3 ([GS]) | Bitiş anı = `_derlenir.kesme_nokta_sn`; adım penceresinde kare farkı enerjisi tepesi | P1 |
| `kirp_oner.py` ([KU]) | Planlanan adım ↔ ölçülen hareket eşlemesi; ölçülen süreler → `sure_carpani` | P1 |
| `kare_zinciri.py` ([GS]) | Dalgalar `zanaat.zincir`'den; kesme penceresi Y55'e göre | P1 |
| `ses_plani.py` ([SM]) | Efektler adım id'leriyle | — |

**4.6.3 Değişecek mevcut kod**

| Dosya | Değişiklik | Öncelik |
|---|---|---|
| `film.py` | [UM] `ASAMALAR` kaydına Y0–Y8 satırları (girdi ve çıktı imzaları: `HARITA_P*.json`, `PLANLAR/`, `kroki.json` sürümleri); kredili aşamaların imzası Y4–Y7 raporlarını içerir | P0 |
| `istem_denetim.py` | Yeni kurallar: yasak sonuç fiilleri (RE); çıplak `left/right` (Y47); kelime sınırları (Y46); istem özeti uyuşmazlığı; derlenmiş istemde filtre kelimesi = HATA | P0 |
| `memmet.py` | (a) `zanaat.kaynak_klip` dolu planı atla. (b) Bitir için `NNN_son.jpg` dosya adını da kabul et. (c) `zincir.baslangic = son_kare` olan planı, kaynak klip V1/V2/V3'ten geçmeden ve zincir karesi G1'den geçmeden kuyruğa alma. **Tempo, uyarıda durma ve reCAPTCHA davranışına dokunulmaz** | P1 |
| `capcut_film.py`, `izleme_paketi.py` | [KU]'nun değişikliği; benim istediğim `kullanim`, `sira`, `kaynak_klip`, `kesme.ses_tasma_sn` alanlarının okunması | P1 |
| `seslendir.py` | Whisper araması `_derlenir.replik_zaman` penceresinde yapılır ([SM]'nin aracı) | P1 |
| `saglayicilar/sahte.py` | Sahte görsel, `_derlenir.kadraj_konumu`'na etiketli kutular çizer ("MARA" solda, "VOSS" sağda); sahte video, adım pencerelerinde hareket eden kutu üretir ([KU] ile ortak) | P0 |
| `ritim_esikleri.json` | §4.7 sonundaki anahtarlar | P0 |
| `.claude/agents/yonetmen.md` | §4.3.1 ile baştan yazılır (atomik zincir kuralı en üstte; istem yazma bölümü kalkar; kipler) | P0 |
| `.claude/agents/plan-elestirmeni.md` | Yeni | P1 |
| `testler/test_plan_dili.py` + `FILMLER/ORNEK_3_SAHNE_ZANAAT/` | Zanaat alanlı 3 plan + kroki. Bozuk varyantlar: eksen ihlali, nesne zıplaması, yasak fiil, adım örtüşmesi, konuşma ile fiziksel adım örtüşmesi, K2 → K4 ardışığı, konuşan plana L taşması, "chest" içeren şablon, **ortada kesilen `devam`, kurgu sırası değişince dondurulmuş durum zıplaması, `_derlenir`'e elle yazma**. Mevcut `ORNEK_3_SAHNE` ve testi **değişmez** | P0 |

---

### 4.7 Makinenin denetleyeceği eşikler (kaynağıyla)

**Kodlar:** H = HATA (geçmez) · B = BAYRAK (ajan bakar). ZN Z0 #1–20 maddeleri aynen geçerlidir. Y kuralları onları plan diline uyarlar ya da yeni kural ekler. "(hesap)" işaretli kuralları `kroki.py` ya da `dunya_defteri.py` hesaplar.
Kroki eksik olduğu için hesaplanamayan kural `HESAPLANAMADI` sonucunu verir ve **H** sayılır. [GS]'nin "ölçülemedi asla GEÇ değildir" ilkesinin kâğıttaki karşılığıdır.

**4.7.1 Atomik eylem zinciri**

| # | Ölçü | Eşik | Sonuç | Kaynak / RE |
|---|---|---|---|---|
| Y01 | Plandaki adım sayısı (fiziksel + mikro + konuşma; bitişte durup beklemek sayılmaz); insansız kuruluş ve geçiş planları hariç | 2–3 | H | Kesin karar 2; üst sınır RE `eylem_adim_max`; konuşma bir adımdır ([CM] Ç-1 ile aynı); yeni `plan_adim_min` = 2 |
| Y02 | Konuşmalı planda fiziksel adım; konuşma ile fiziksel adımın örtüşmesi | ≤ 1; 0 | H | RE `eylem_adim_konusmali_max`, ZN §2.3 |
| Y02b | **(yeni)** Fiziksel adım bitişi ile konuşma başı arasındaki boşluk | ≥ 0,2 sn | B | [SM] S0.9 (150 ms) → (tahmin) |
| Y03 | Adım süresi; adımlar arası örtüşme | ≥ 1,5 sn; yok | H | RE `eylem_adim_min_sn`, Z0 #14 |
| Y04 | İlk adımın başlangıcı | ≥ 0,5 sn | B | ZN §2.2, RE `kullanim_bas_varsayilan_sn` |
| Y05 | Son adımın bitişi | ≤ klip_sn − 1,0 | H | (hesap) RE `bitis_tutma_sn` + `kullanim_son_pay_sn` |
| Y06 | Aynı anda hareket eden özne sayısı | ≤ 1 | B | (tahmin) |
| Y07 | Fiil sözlükte değil / yasak sonuç fiili / iç durum fiili | 0 | H | ZN §3.7, RE `yasak_sonuc_fiilleri`, [SN] R2 |
| Y08 | Fiilin zorunlu parametresi eksik (el, el şekli, hedef, yön, ölçü) | 0 | H | Kesin karar 2 |
| Y09 | İnce el eylemi (`kavrar`, `birakir`, kilit, düğüm) OG ya da daha geniş kadrajda | 0 | B → eklemeye böl | ZN §3.5 |
| Y10 | Yazarın beklediği bitiş durumu ≠ etkilerden hesaplanan | 0 | H | ZN Z0 #16 |

**4.7.2 Durum zinciri ve dünya defteri**

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y11 | `bitis[N]` ≠ `baslangic[N+1]` (yalnız olgular; `yeni_sahne` ve `zaman_atlama` hariç) | 0 | H | Z0 #16, A2 K0 |
| Y12 | Gerekçesiz `fark` | 0 | H | §4.5.13 #1 |
| Y13 | Sahnenin son planındaki durum ≠ sözleşmedeki `cikis_durumu` | 0 | H | |
| Y14 | Görüş konisinde, görüş hattı açık ve `gizli_arkasinda` olmayan kişi `kadrajdakiler`'de yok; ya da listede olup kadraj dışında | 0 | H (hesap) | A2 K0 "kaybolma" |
| Y15 | Nesnenin `kimde` alanı etki olmadan değişiyor | 0 | H | A2 K0 |
| Y16 | Nesnenin `el` alanı etki olmadan değişiyor | 0 | H | A2'de B idi; atomik zincirde her el değişimi bir adım olduğu için H ([GS] de H) |
| Y57 | **(yeni)** Hikâye sahne uçlarının olguları ⊄ sözleşme | 0 | H | Ç-9, [SN] `sahne_siniri_durum_esitligi` |
| Y58 | **(yeni)** Kurgu sırası ya da kesme değişince yeni komşu çiftlerde **dondurulmuş** olgu eşitliği | eşit | H (kullanıcının CapCut kararında B, [KU] T3 kuralı) | İ-11 |

**4.7.3 Kadraj, 180°, bakış, ışık**

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y17 | Kurulum sahnenin `kamera_tarafi`'nda değil ve `eksen_gecis` yok | 0 | H (hesap) | Z0 #17 |
| Y18 | Karşılıklı tekli planlarda kadrajdaki bakış yönleri zıt değil | 0 | H (hesap) | Z0 #18 |
| Y19 | Ardışık iki planda aynı özneye açı farkı < 30° **ve** ölçek farkı < 2 kademe | 0 | H (hesap) | Z0 #12, RE |
| Y20 | Aynı kurulum art arda | ≤ 2 | B | RE `ayni_kamera_konumu_ardisik_max` |
| Y21 | Konum planı (G/OG/IK) sahnenin ilk N planında | N = 3 (geç girişte 5) | B | RE `sahne_konum_plani_max_sira` |
| Y22 | 90 sn'den uzun sahnede ortada G/OG planı | var | B | RE `sahne_yeniden_konum_sn` |
| Y23 | Işığın kadrajdaki yönü ana kaynaktan hesaplanana uymuyor ve `isik_degisimi` yok | 0 | H (hesap) | A2 K0 |
| Y24 | `_derlenir.ayna_yasak` olan plana ayna düzeltmesi (G1 ya da kurgu) | 0 | H | ZN §3.3, İ-10 |
| Y25 | Göz yüksekliği farkı > 0,3 m iken bakışta aşağı/yukarı eki yok | 0 | B (hesap) | ZN §3.3; yükseklikler (tahmin): ayakta 1,6 · oturan 1,2 · diz çökmüş 0,9 · yerde 0,3 m; yaratıkta evren kartındaki `goz_yuksekligi_m` |
| Y26 | Yolculukta `_derlenir.ekran_yonu` ≠ sahnenin `ekran_yonu` ve arada `doner` adımı yok | 0 | H | ZN §3.3 |
| Y27 | Klipte kamera hareketi; düşük güvenli hareket | ≤ 1; yalnız doruk + yedek istemle | H; B | RE `kamera_hareketi_klip_max`, `dusuk_guven_hareketler` |
| Y28 | `kadrajdakiler` ↔ geometri: kadrajdaki kişi seti ve ölçek tutarlı | eşit | H (hesap) | Görüş açısı (hesap) 2·atan(18/f) |
| Y60 | **(yeni)** Her kurulumun görüş konisindeki duvar ve öğeler bir plakada (ebeveyn zincirinde) var | evet | H (hesap) | Ç-13; R5 |

**4.7.4 Konuşma, dudak, ses köprüleri**

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y29 | Klipte konuşan sayısı; OU'da öndeki kişi sırtı dönük ve sessiz | ≤ 1; evet | H | RE `konusan_karede_max`, ZN K4 |
| Y30 | Replik kelime sayısı | ≤ 16 (8 sn) / ≤ 20 (10 sn) | H | RE (senaristin kapısında da var) |
| Y31 | Diyalog formülü (ZN §2.3); L kesmede **görüntü + taşma** toplamına uygulanır | ≥ formül | H | ZN §2.3; T1'de gerçek TTS süresiyle [KU] / [SM] B1 |
| Y32 | Konuşan yüz: ölçek, açı, yüz yüksekliği | O / OY / Y; `on` ya da `3/4` (\|yaw\| ≤ 45°); konuşurken CY yok; başlangıç karesinde yüz ≥ kare yüksekliğinin %12'si | B | (tahmin); %12 ve 45° [GS] §8.9 |
| Y33 | L taşması, konuşanın da görünüp konuştuğu bir plana gidiyor (çift ses) | 0 | H | BK 5.1 #8'in genişletilmesi |
| Y34 | J kesmesi: sonraki planın konuşanı bu planda görünüyor ve ağzı kapalı | 0 | H | |
| Y35 | `ekran_disi_ses` varken görünen herkeste `listens silently, mouth closed` (`_derlenir.dinleyen_agiz = kapali`) | var | H | BK 5.1 #8, ZN §3.5, [SM] S0.2 |
| Y36 | L taşma / J öne alma süresi | 0,3–2,5 / 0,3–0,8 sn | B | RE `l_kesme_aralik_sn`, `j_kesme_aralik_sn` |
| Y59 | **(yeni)** Bölünen replikte `cumleler` planlar arasında eksiksiz ve tekrarsız; `ekran_disi_ses.kaynak = tts` ise ses tanıtım kuralı sağlanmış | evet | H; B | Ç-11, [SM] S0.3 |

**4.7.5 Kurgu bağlantısı, klip bölme, kare zinciri**

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y37 | `kullanim.bas`; `bas + sure` | ≥ 0,3; ≤ klip_sn − 0,5 | B | RE `kullanim_bas_min_sn`, `kullanim_son_pay_sn` |
| Y38 | `kesme.tip = eylem` iken kesme noktasının son adım içindeki yeri | %60–70 | B | ZN §3.4 |
| Y39 | Klip bölmede kaynağın kullanılabilir süresi; parçalar arası atlama ya da senkron korumalı formül | ≥ 6,0 sn; ≥ 0,4 sn ya da formül | H | RE; [KU] §5.1 |
| Y40 | Z1 zincir derinliği | ≤ 2; 3. halkada yeniden demirleme | H | A2 §2.3; RE `zincir_derinlik_max` ([KU] adı) |
| Y41 | **(değişti)** `bitis_sabitle` görselinin kaynağı: sonraki plan `devam` ise onun planlanmış görseli, değilse `NNN_son.jpg`; Bitir görseli ile başlangıç görseli aynı kurulumdan | evet | H | İ-2 |
| Y42 | Yalnız Bitir için ayrıca üretilen görsel (`NNN_son.jpg`) oranı | ≤ %10 plan | B | (tahmin); yükleme uyarısı riski (DR) |
| Y43 | Kamera ağacı derinliği (plaka → ana kare → türev) | ≤ 3 düğüm | B | (tahmin) |
| Y54 | **(yeni)** Doğrudan bitişik `devam` (arada plan yok) yalnız `dogal_durak: true` ise; değilse araya ≥ 1,0 sn'lik bir `araya_kesme` planı girer (örtülü devam) | evet | B | Veo'nun ilk 0,3–1,0 sn'lik durağanlığı ve bitiş tutması dikişte takılma yapar (ZN §2.2, [GS] R5); süre (tahmin) |
| Y55 | **(yeni)** Z1 kaynağı olan planda kesme noktası bitiş tutmasının içinde: son adım bitişi + ≥ 0,2 sn ≤ `kesme_nokta_sn` ≤ klip_sn − 0,5 | evet | H | [GS] A15, [KU] §6.1-6; 0,2 (tahmin) |
| Y56 | **(yeni)** Z2 politikası: sonraki plan `devam` ve bu planda durum değiştiren fiziksel adım (eller, nesne, poz, kadraja giriş/çıkış) varsa `bitis_sabitle` önerilir; **konuşmalı planda `bitis_sabitle` yok** (ölçülene kadar) | öneri; 0 | B; H | İ-2; açık soru 3 |

**4.7.6 Kimlik, referans, istem**

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y44 | Karakterin sahnedeki ilk görünüşü (`kimlik_demiri`) | ölçek ≥ OY; yüz `on` ya da `3/4` | B | (tahmin); SFace eşiği önden fotoğrafa göre verilmiş (A2 §1.1) |
| Y45 | `referans` = kadrajda yüzü ya da bedeni görünen adlı karakterler | `kadrajdakiler`'den derlenir; ≤ 2 | H | RE `referans_max` |
| Y46 | Derlenmiş hareket isteminin kelime sayısı; adım cümlesinin kelime sayısı | ≤ 75; ≤ 16 | B | (tahmin); [UM] C12 12 önerdi, kıskaç şablonu 15 kelime tutuyor |
| Y47 | Çıplak `left/right` (iyelik ya da `frame` sözcüğü olmadan) | 0 | H | |
| Y48 | Derlenmiş istemde filtre kelimesi | 0 | H | DR |
| Y49 | `ekranda_bilgi` boş ya da iç durum fiili içeriyor | 0 | H / B | ZN §6.1, [SN] R2 |

**4.7.7 Sahne kapsaması**

| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y50 | Diyalog sahnesinde kurulum sayısı | ≥ 3 | B | ZN §3.3 karşılıklı çekim düzeni; en az sayı (tahmin) |
| Y51 | Diyalog sahnesinde tepki planı ≥ ⌈(K + O) / 3⌉ (K konuşan plan, O diğer plan) | RE `tepki_orani_min` 0,25 | B | (hesap: 0,25·T ≤ R ve T = K + O + R'den) |
| Y52 | J/L oranı | ≥ %30 | B | RE `jl_kesme_orani_min` |
| Y53 | Plan sayısı (sahne ve film hedefinden) | ±%15 | B | RE `plan_sayisi_tolerans_oran` |

**4.7.8 Görüntü sonrası ölçümler** (kapıların sahibi [GS]; benim alanlarımı kullanır)

| Ölçü | Eşik | Kaynak |
|---|---|---|
| Kadraj sırası: yüz ya da kişi kutularının x sırası = `_derlenir.kadraj_sirasi` | eşit, değilse H | A2 §6.2 |
| Bakış: \|yaw\| > 15° ise yönün işareti = `bakis_kadrajda` | eşit, değilse H | A2 §6.2 |
| Kör durum soruları (`gorunmesi_gerekenler`'den): el, nesne, kişi sayısı, ışık tarafı, açık parmak | kritik olgu yanlışsa YENİDEN; "görünmüyor" B | A1 B4 (ARIS), A2 §5 |
| V3: kesme anındaki kare ↔ `bitis_durumu` | kritik olgular eşit | Ö7 (tahmin) |
| V3 adım zamanlaması: kare farkı enerjisinin tepesi adım penceresi içinde | sapma ≤ 1,0 sn | (tahmin) |
| V3 bitişte durma: son 0,5 sn'de ardışık kare MAE ortalaması | klip medyanının ≤ %50'si | yöntem A2 §1.2; eşik (tahmin) |
| Z1 dikişi DINOv2 / `kurulum_donusu` DINOv2 (ana kareye) | ≥ 0,80 H / ≥ 0,70 B | A2 §6.2 |

**`ritim_esikleri.json`'a eklenecek anahtarlar** (her birinin `aciklama` alanına kaynağı ya da "(tahmin)" yazılır):

| Anahtar | Değer |
|---|---|
| `plan_adim_min` | 2 |
| `plan_ilk_adim_min_sn` | 0,5 |
| `plan_son_adim_pay_sn` | 1,0 |
| `plan_es_zamanli_ozne_max` | 1 |
| `plan_konusma_adim_arasi_min_sn` | 0,2 |
| `plan_goz_farki_bakis_m` | 0,3 |
| `plan_goz_yukseklik_m` | {ayakta: 1,6, oturan: 1,2, diz_cokmus: 0,9, yerde: 0,3} |
| `plan_konusan_yaw_max` | 45 |
| `plan_konusan_yuz_oran_min` | 0,12 |
| `plan_bitis_ozel_oran_max` | 0,10 |
| `plan_agac_derinlik_max` | 3 |
| `zincir_derinlik_max` | 2 |
| `devam_kesme_tutma_min_sn` | 0,2 |
| `ortulu_devam_araya_min_sn` | 1,0 |
| `plan_hareket_istem_kelime_max` | 75 |
| `plan_adim_cumle_kelime_max` | 16 |
| `plan_istem_elle_oran_max` | 0,05 |
| `plan_dialog_kurulum_min` | 3 |
| `plan_zincir_zaman_sapma_max_sn` | 1,0 |

---

### 4.8 Kesin kararların kendi alanımda uygulanışı

#### 4.8.1 Karar 2 — Atomik eylem zinciri

**Neden böyle yazıyoruz?** Video modeline sonuç söylenirse ("picks up the pen"), modelin oraya nasıl gideceği bilinmez: hangi elle, hangi yoldan, ne kadar sürede. Her klip unutkan olduğu için sonraki klip de bu sonucu bilemez. Fiziksel adımlar saniyeleriyle yazıldığında üç şey olur:
1. Modelin serbestliği daralır.
2. Planın bitişi önceden bilinir; sonraki planın başlangıcı o bitişten türetilir ya da (Z1'de) piksel olarak alınır.
3. "Bitişe ulaştı mı?" sorusu V3'te ölçülebilir hâle gelir.

**Yazım kuralları**
1. Plan bir **başlangıç durumuyla** açılır. Bu durum başlangıç karesinin ta kendisidir ve görsel istemi ondan derlenir. Durumda şunlar bulunur: kim hangi işarette, poz, yüz yönü, bakış hedefi, iki elin her biri (ne tutuyor, nerede, hangi şekilde → kaç parmak açık), nesnelerin durumu. Kadraj konumu yazılmaz, hesaplanır.
2. İnsanlı ya da yaratıklı planda **2–3 adım** olur. Her adım: `[bas–bit sn] özne + tek fiil (sözlükten) + vücut parçası + karakterin kendi sağı/solu + yön ya da hedef + ölçü (+ el şekli)`. Konuşma bir adımdır; konuşmalı planda en çok 1 fiziksel adım olur ve konuşmayla örtüşmez.
3. Adımlar 0,5 sn'den sonra başlar, klip_sn − 1,0'dan önce biter. Geri kalan süre başta ve sonda durup beklemektir (`holds still`).
4. Her adımın `etki`si yazılır. Bitiş durumunu kod hesaplar ve sonraki plan bunu miras alır.
5. İnce el işi geniş kadrajda yazılmaz, **ekleme planına bölünür**. Bağlantı eylem üstünde kesmeyle yapılır.
6. Sürekli hâller poz olarak yazılır. Yasak sonuç fiilleri ve iç durum fiilleri hiçbir alanda geçmez.

**Örnek 1 — "kalemi al"** (kullanıcının kendi örneği: yürü → sağ kolunu uzat → başparmak ve işaret parmağıyla kavra)

*1a: Tek planda yazım.* İzin verilir, ama OG kadrajda kavrama olduğu için Y09 BAYRAK verir.
```json
"kamera": {"kurulum": "K1", "kadraj": "OG", "hareket_tipi": "sabit"},
"baslangic_durumu": {"karakterler": {"mara": {"isaret": "M1", "poz": "ayakta", "yuz_yonu": {"hedef": "masa"}, "bakis": {"hedef": "kalem"},
   "eller": {"sol": {"tutar": null, "yer": "yanda", "sekil": "serbest"}, "sag": {"tutar": null, "yer": "yanda", "sekil": "serbest"}}}},
  "nesneler": {"kalem": {"nerede": "masa_ustu", "durum": "yatay"}}},
"eylem_zinciri": [
 {"id": "a1", "bas": 0.5, "bit": 3.0, "ozne": "mara", "tur": "fiziksel", "fiil": "yurur", "hedef": "masa", "olcu": "uc_yavas_adim", "etki": {"mara.isaret": "M5"}},
 {"id": "a2", "bas": 3.0, "bit": 4.8, "ozne": "mara", "tur": "fiziksel", "fiil": "uzanir", "govde": "sag_kol", "hedef": "kalem", "olcu": "5cm", "etki": {"mara.eller.sag.yer": "kalem_ustu"}},
 {"id": "a3", "bas": 4.8, "bit": 6.5, "ozne": "mara", "tur": "fiziksel", "fiil": "kavrar", "govde": "sag_el", "el_sekli": "kiskac", "hedef": "kalem",
  "etki": {"kalem.kimde": "mara", "kalem.el": "sag", "mara.eller.sag.tutar": "kalem", "mara.eller.sag.sekil": "kiskac"}}]
```
Derlenen istem (tek kişi, öznesiz):
`Static medium-wide shot. 0.5-3s: walks three slow steps toward the desk. 3-4.8s: extends the empty right arm toward the quill lying on the desk, fingers stopping just above it. 4.8-6.5s: the thumb and index finger close around the quill, the other three fingers stay curled. 6.5-8s: holds still. Sound: footsteps on wooden floor, quiet room tone. No music.`

*1b: İki planda yazım (önerilen; kalem hikâyede kurulumsa).*
- **P_a** (OG, eylem): yalnız a1 ve a2. Kesme `eylem`, uzanma adımının %67'sinde: 3,0 + 0,67 × 1,8 ≈ **4,2 sn** (hesap; Y38). Bitiş: sağ elin parmak uçları kalemin 5 cm üstünde.
- **P_b** (D ekleme, `eylem_kesme`, aynı taraf, `baslangic: turev`, `baslangic_durumu: "miras"`):
  - a1 [0,5–2,0] başparmak ve işaret parmağı alçalır ve kalemi kavrar (`kiskac`)
  - a2 [2,0–3,5] kalemi 10 cm kaldırır
- P_a'nın bitiş durumu kritik ama sonraki plan `devam` değil. Bu yüzden ilk çekimde Z2 yok. V3 tutmazsa yeniden çekimde `NNN_son.jpg` ile Z2 kullanılır (Y56, Y41).

**Örnek 2 — "kapıyı açar"** (`open` yasak; açma biçimi yazılır):
`0.5-2s: the right hand rises to the iron latch, four fingers curling over it. 2-3.5s: the thumb presses the latch down. 3.5-6s: pulls the door about 40 cm inward, the body staying in the gap. 6-8s: holds still.`
Etki: `mekan_durumu.kapi = "aralik_40cm"`, `mara.eller.sag.yer = "kapi_kenari"`.

**Örnek 3 — konuşmalı plan** (§4.5.12 P121): 1 mikro adım + 1 konuşma adımı = 2 adım. Mikro adım konuşmadan ≥ 0,2 sn önce biter. Konuşma süresi ZN §2.3 formülünden gelir (3,95 sn, hesap).

**Örnek 4 — tepki** (P122): `listens silently, mouth closed` + 2 mikro adım. Ekran dışı ses `ekran_disi_ses` alanındadır; görünen ağız kapalı kalır (Y35).

**Örnek 5 — yaratık:**
`0.5-2.5s: Ember stretches the neck about 10 cm toward Mara's gloved left hand, nostrils flaring. 2.5-4.5s: Ember tilts the head slightly to its right and lifts the eyes to Mara's face. 4.5-8s: holds still; Mara's hand stays still.`
Yaratıkta sağ ve sol yaratığın kendisine göredir ("its right"). "baby" ve "little" yasaktır (DR).

**Örnek 6 — aksiyon ve ekran yönü** (sahnenin `ekran_yonu` = `soldan_saga`):
- **P_x:** G, `takip_yan`, poz `kosuyor`. a1 [0,5–3,5] dört adım ilerler; a2 [3,5–5,5] başını sol omzunun üstünden geriye çevirir. `_derlenir.ekran_yonu = soldan_saga`.
- **P_y:** takipçi, o da `soldan_saga` gider (Y26). Kaçanın yön değiştirmesi ancak ekranda bir `doner` adımıyla olur.

#### 4.8.2 Karar 3 — Altı özellik

**(a) Videodan önce animatik ve habersiz seyirci denetimi.** Benim alanımın animatiğe verdikleri:
- **Her plan için planlanmış görsel**, Z1 planları dahil (İ-2). Animatikte delik kalmaz.
- `kullanim` ve `kesme`, L/J kaymalarıyla birlikte zaman çizelgesine.
- `hareket_tipi` → durağan kareye eklenecek yavaş hareket ([KU] Ken Burns oranları).
- `bitis_sabitle` olan planlarda başlangıç ve bitiş görselleri arasında çapraz geçiş. Seyirci eylemin sonucunu görür ([GS] §8.3 ile aynı).
- **Eylem şeridi:** `plan_dili.gorunur_tarif(dil="tr")`. Flow'a giden istemle aynı kaynaktan çıkar ([KU] §8.1-5).

Animatikten **önce** iki kâğıt katmanı vardır: Y5 plan eleştirisi ve Y6 plan seyircisi. İkisi de görsel emeğinden önce, 0 kredidir. Animatiğe geçmek için Z0, K0 ve Y kurallarında HATA = 0 olmalıdır.

**(b) Makinenin tuttuğu dünya durumu defteri ve otomatik zıplama denetimi.**
- **Tek araç** (`dunya_defteri.py`, sahibi [GS]) ve **tek anlam** (§4.5.13). Yönetmen yalnız sözleşme, `miras` / `fark` ve `etki` yazar; defteri kod katlar.
- **Olgu ve kadraj ayrımı** (İ-1) sayesinde açı değişimi yanlış zıplama üretmez. Geometriyle birleşince "görünmesi gerekip görünmeyen" kişi de bulunur (Y14). B2'deki "Bram kapıda ama araya ateşi söndüren el giriyor" türü kopukluk böyle yakalanır (H/kurgu-izleme-denetimi).
- **Hikâye katmanı** ([SN]: sahne uçları, `bilgi`) ile plan katmanı aynı dosyada, ayrı bölümlerdedir. Uçlar alt küme olarak eşleştirilir (Y57).
- **Dondurma** (İ-11) sayesinde kurgu sırası değişince de defter doğru kalır (Y58).
- **Gözlenen sütun** ([UM]): G1 ve V3'ün kör gözlem sonuçları plan durumunun yanına yazılır. Planlanan ile gözlenen arasındaki fark kuyruğa ve ders defterine gider.

**(c) Referansla otomatik yüz kontrolü.** Planın bu kapıya verdikleri:
- `kadrajdakiler` → `referans` (≤ 2) ve `gorunmesi_gerekenler`.
- `yuz_acisi`: `on` ve `3/4` yüzler SFace'e, `profil`, `sirt` ve `gorunmez` yüzler DINOv2 ile arka görünüm kartına ya da kör gözleme gider ([GS] §8.5). Bu alan aynı zamanda görüntüdeki sol/sağı kişinin kendi sol/sağına çevirmenin girdisidir.
- **Kimlik demiri** (Y44): her karakterin her sahnedeki ilk görünüşü SFace'in doğrulayabileceği bir plandır. Sahnenin geri kalanında sırt ve profil planları serbesttir.
- **Kadraj sırası:** yüz kutularının x sırası `_derlenir.kadraj_sirasi` ile karşılaştırılır. Bu hem 180° hatasını hem ayna hatasını yakalar.

**(d) Kare zinciri (son kare → sonraki klibin başlangıcı)** **(değişti)**

| `gecis_turu` | Ne zaman | Başlangıç karesi | Bitir karesi (Z2) | Denetim |
|---|---|---|---|---|
| **`devam`** | Aynı kurulum, kesintisiz zaman; aynı eylem ya da duygu tutma sürüyor, tek klibe sığmıyor (uzun yürüyüş, yaratığın boyunu tilt ile gösterme, doruktaki uzun plan, su, ateş, kalabalık) | **Z1: önceki klibin `kesme_nokta_sn` çevresindeki gerçek kare.** Bitiş tutmasının içinden en durgun ve keskin kare seçilir (Y55, [GS] A15); 1280×720 → 1376×768 Lanczos ile büyütülür, üretken düzeltme yapılmaz. Planlanmış görsel ayrıca üretilir (animatik ve yedek) | Önceki klipte durum değiştiren fiziksel adım varsa önerilir; görsel bu planın planlanmış görselidir (Y56, Y41). Konuşmalı planda yok | G1-zincir; Z1 dikişi DINOv2 ≥ 0,80; derinlik ≤ 2 (Y40); tutmazsa planlanmış görsele düşülür (`yedege_dustu`) |
| `eylem_kesme` | Açı ya da ölçek değişir, an aynıdır | Kurulumun ana karesinden türev; olgular önceki planın bitişi | Yalnız kritik bitiş + `risk_uretim = yuksek` ya da V3 başarısızlığında `NNN_son.jpg` (≤ %10, Y42) | G1, V3 |
| `kurulum_donusu` | Sahnede daha önce kullanılmış kuruluma dönüş | O kurulumun ana karesinden türev (ViMax kamera ağacı, A2 §1.4) | — | K1 ≥ 0,70 |
| `araya_kesme` | Tepki, ekleme, ironi; örtülü devamın örtüsü | Kurulumun ana karesinden türev | — | G1 |
| `zaman_atlama` | Aynı mekân, zaman geçti | Ana kare + gerekçeli fark | — | K0 fark gerekçesi |
| `yeni_sahne` | Yeni mekân ya da zaman | Plaka + karakter kartları (`kart`) | — | sözleşme |

**Neden Z1 varsayılan?**
1. Kullanıcının kararı bu yöntemi aynen söylüyor.
2. Piksel düzeyinde süreklilik en yüksek olan yöntem budur.
3. Bedeli kalite değil sıradır: ≤ 3 dalga gerekir ve Flow temposu zaten darboğazdır.
4. Planlanmış görselin üretilmesi animatiği ve "bozuk görsel videoya gitmez" kuralını korur (BK 7.6 #6). Zincir karesinin kendisi de G1-zincir kapısından geçer.

**Neden Z2 hedefli kullanılır?** Bitir yuvası Flow'da çalışıyor (FK; H/proje-b2 16.10). Ama başlangıç ile bitiş arasındaki fark büyükse morf riski var ([YN1] R3). Z2 bu yüzden yalnız iki yerde kullanılır: durum değiştiren adımın bitişini sabitlemek ve V3 başarısızlığını düzeltmek.

**Örtülü devam (Y54):** Veo klibinin başındaki durağanlık ile önceki klibin bitiş tutması doğrudan dikişte "takılma" hissi verir. Doğal bir durak yoksa iki klip arasına ≥ 1,0 sn'lik bir tepki ya da ekleme planı girer. [SN]'nin "doğal yeniden demirleme noktaları" bu yerlerdir.

**Örnek — S07, Mara ocak önünden kapıya yürüyor** (K3, OG, sabit)
- **070:**
  - a1 [0,5–3,5] `yurur` M3 → M3b, `uc_yavas_adim`
  - a2 [3,5–5,5] `doner` başını 60° sola, pencereye (dışarıdan bir ses gelir)
  - `kullanim {0.5, 6.1}` → kesme 6,6 (son adım 5,5 + 1,1 ≥ 0,2 ✓, Y55)
  - Kesme `devam`.
- **071:**
  - `zincir {gecis_turu: devam, baslangic: son_kare, ebeveyn: "070@kesme", dogal_durak: true}`
  - a1 [0,5–2,0] `bakis_kaydirir` kapıya
  - a2 [2,0–5,0] `yurur` M3b → M1 iki adım
- 070'in etkileri yalnız işaret ve bakış; elde, nesnede ya da pozda değişiklik yok. Bu yüzden Z2 yok (Y56).
- 071'in planlanmış görseli 070'in görselinden fark uygulanarak türetilir, animatikte ve yedek olarak kullanılır.
- `uretim.zincir = {dalga: 2, kaynak: "070.mp4@6.6", derinlik: 1}`. 072 `eylem_kesme` ile K6'ya geçer (D, el sürgüye). Zincir 1 halkada biter.

**Kamera konumu ağacı** (ViMax, A2 §1.4) **(değişti: kök plaka)**
- **Kök:** mekân plakaları (EVREN; kart aşamasında G1'den geçer).
- **Çocuk:** kurulumların ana kareleri. Ebeveyn plaka ya da karşı kurulumun ana karesidir.
- **Torun:** aynı kurulumun sonraki planları.
- **Z1 halkaları:** ağacın dışında bir zincirdir ve derinliği ≤ 2'dir.
- `kamera_agaci.py` paket sırasını verir: bir ana karedeki hata türevlere yayılmadan yakalanır. Ebeveyn yeniden üretilirse çocukları `bayat` olur. Ağaç derinliği ≤ 3 (Y43).

**(e) Kendi kendine öğrenen ders defteri.**
- **Kayıt biçimi** [UM] ve [CM]'nin ortak biçimidir (Ç-20). Benim katkım `plan_ozellik.py` ile her olaya şu özellik vektörünün eklenmesi: kadraj, açı, hareket tipi, fiil ve el şekli, referans sayısı, geçiş türü, başlangıç kaynağı (Z1 mi), Z2, ışık türü, `risk_uretim`.
- **Aday ders:** aynı birleşim ≥ 3 kez başarısız olursa (tahmin; [CM] terfi eşiğiyle aynı). Yonetmen `ders` kipi dersi tek cümleye çevirir. Onaylı ders **bir sonraki partide** uygulanır.
- **Plan dili ders türleri:**
  - `istem_eki`: `istem_derle` ekler
  - `plan_kurali`: `plan_denetim` yeni H/B kuralı olarak uygular
  - `fiil_kalibrasyonu`: `sure_carpani`; [KU]'nun ölçülen adım sürelerinden
  - `esik`: RE önerisi; güvenlik eşikleri öğrenmeyle gevşetilemez ([GS] §7.9)
  - `yasak_kalip`
- **Etkisiz ders:** bir dersin uygulandığı ≥ 5 planda hata oranı düşmüyorsa (tahmin) ders `etkisiz` işaretlenir.
- **Tohum dersler** (sistem kurulurken onaylı girer):
  1. OU ve arkadan planlarda öndeki kişinin saç ve kıyafet çapası zorunlu (YR §5 Ç032)
  2. Oda kartında istenmeyen nesne varsa kart referanstan çıkarılır (DR)
  3. Ölçek isteyen nesneye ölçekli referans verilir (DR)
  4. Stil ekinde ışık ifadesi yok (BK §8 #12)
  5. Bebek yüzü makrosu yerine görsel + yavaş zoom (DR)
  6. Karakterli planda "İçerik öğeleri" modu yok, yalnız Kareler modu (FK)
  7. Tek model Omni (BK §8 #3)

**(f) Kalıcı seri evreni kütüphanesi.** Benim alanımın kütüphaneye koydukları ve oradan aldıkları:
```
EVREN/<SERI>/
  mekanlar/<id>/kroki.json        (yönetmen)  · kurulumlar.json (yönetmen, film sonunda birikir)
                mekan.json, plakalar, ana_kareler/<isik>/<K>.jpg  ([GS])  · ses.json ([SM])
  karakterler/<id>/karakter.json  ([GS]) → yönetmen okur: boy_m, goz_yuksekligi_m, baskin_el, asimetrik[], etiket_anonim
  EKRAN_YONU.json                 (yönetmen) seri boyunca coğrafya yönü (ör. "kuzey diyarına yolculuk = soldan_saga")
  dunya.json → stil_eki           ([GS])
```
- İkinci filmde aynı kulübeye dönüldüğünde kroki, kurulumlar ve onaylı ana kareler yeniden kullanılır.
- `baskin_el` ile ince el işi baskın olmayan elle yapılıyorsa ve gerekçesi yoksa BAYRAK verilir.

#### 4.8.3 Karar 4 — Ses ve dudak uyumu (benim alanıma düşen kısım)
- Yolu ses uzmanı seçer ([SM] §1.2). Ben de aynı görüşteyim:
  - **Yol A:** Veo konuşur; ses ayrıştırılır, hizalanır ve karakterin evren sesine yerel dönüştürücüyle çevrilir.
  - **Yol B:** ağzı görünmeyen repliklerde aynı sesle TTS.
  - **Yedek:** TTS + dudak senkronu (MuseTalk).
  - Gerekçe: dudak, duygu ve zamanlama klipten gelir; görüntüye ikinci model dokunmaz. G1 ve V2'nin kimlik ölçümleri bu yüzden geçerli kalır ([GS] §8.9).
- Plan dilinin bu yol için getirdiği şartlar:
  1. **Replik isteme birebir girer:** `<Ad> {ton_fiili}, {veo_ses_tarifi}: "{veo_metin|metin}"`. Altyazı ve WER denetimi `metin` alanını kullanır ([SM] S0.4, S2.2).
  2. **Konuşan yüz okunur olur** (Y32). Ağzın önünde el, atkı ya da kupa yoktur (`yasaklar: agiz_onu_engel`).
  3. **Konuşurken fiziksel adım yoktur**, ve fiziksel adım konuşmadan ≥ 0,2 sn önce biter (Y02, Y02b; ZN §2.3: nesneyle uğraşan karakterde Flow dudakları bozuyor).
  4. **Ekran dışı replik** önce konuşanın kendi klibinden L taşmasıyla verilir (`kaynak: "plan:<no>"`). `tts` yalnız ses tanıtım kuralıyla kullanılır (Y59).
  5. **Çift ses ve sahte dudak yasakları:** Y33–Y35.
  6. `_derlenir.replik_zaman` penceresi konuşma adımından derlenir. Whisper araması ve dudak denetimi bu pencerede yapılır (DR: "aynı klip iki plana bölününce" dersi).
  7. Ses tarifi istemin kelime bütçesini paylaşır (Y46). Yaş sözcükleri yasaktır (`istem_denetim.py` `YAS_IFADESI`).

#### 4.8.4 Karar 1, 5 ve 6
- **Karar 1:** Yönetmen aşamasında kullanıcıya soru yoktur. Kurulum, kart seçimi, sahne bölme ve yeniden çekim kararları ekiptedir ve `KARAR_DEFTERI.md`'ye yazılır. Kurgu kaynaklı yeni plan da varsayılan olarak ekip kararıdır; `--onayli` modda yalnız bilgi gösterilir.
- **Karar 5:** Plan dili Flow temposuna dokunmaz.
  - Z1 dalgaları gönderimi sıraya sokar, hızlandırmaz.
  - Y42 ek görsel yüklemesini sınırlar.
  - Bot tespiti atlatılmaz; uyarıda durulur (DR).
- **Karar 6:**
  - "Hesaplanamadı" sonucu HATA sayılır.
  - Plan sayısı ve kurulum sayısı tasarruf için azaltılmaz.
  - Z1, süre bedeli olmasına rağmen kalite gerekçesiyle varsayılandır.
  - Değerlendiriciler her turda yeni örnekle açılır.

---

### 4.9 Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

**4.9.1 Riskler ve önlemler**

| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | Flow ya da Omni saniyeli adımlara ("0.5-3s:") uymayabilir; ölçülmedi. Seedance'ta "SHOT n — around a-b seconds" biçimi çalışıyordu (H/seedance-director-yontemi) | Ö7 düşer | İlk partide eylem planlarının yarısı `aralik`, yarısı `sira` ("First… then…") biçimiyle derlenir; ek kredi gerekmez. V3 sonucuna göre biçim sabitlenir. İkisi de kötüyse adım sayısı 2'ye iner ve Z2 oranı artırılır |
| R2 | Saniyeli zincir istemi uzatır ("kısa istem" kuralıyla çatışma, H/video-istem-kurali) | Model istemin bir kısmını görmezden gelebilir | Hareket isteminde kimlik, stil ve mekân yok (görsel taşıyor); Y46 |
| R3 | Z2'de başlangıç ile Bitir arasındaki fark büyükse morf | Doğal olmayan hareket | Z2 hedefli kullanılır; Bitir görseli başlangıç görselinden türetilir; V2 morf ölçümü; iki morftan sonra plan bölünür |
| R4 | Ajanın koordinat yazması zor | Y2 tıkanır | Betik görevden önce `--karsilikli` önerilerini hesaplar; hazır mekân şablonları; SubagentStop her turda kroki PNG'sini yeniden çizer |
| R5 | Üretilen görsel krokiye uymayabilir (kapı yanlış tarafta) | Mekân zıplaması | Plakalar krokiden istenir; plakada `gorunen` öğe soruları sorulur; Y60; türevler ana kareden üretilir |
| R6 | Dış ve büyük mekânlarda duvar yok, koordinat zayıf | 180° ve yön karışır | Yer işaretleri (kaya, ağaç) + `EKRAN_YONU.json` + sahne `ekran_yonu` |
| R7 | Ek bitiş görselleri yükleme sayısını artırır (DR "çok dosya" uyarısı) | Olağan dışı uyarısı | Y42 ≤ %10; Z2'de `devam` için ek görsel yok (planlanmış görsel kullanılır) |
| R8 | 3+ kişili sahne ve kalabalık (≤ 2 referans) | Yüz karışması | `siluet` / `el` / `sirt` ölçekleri; Y45 |
| R9 | Klip bölmede replik yanlış plana kayar (DR) | Ses kayması | `replik_zaman`, `kaynak_klip`, [KU] senkron korumalı formül, Y59 |
| R10 | ≈495 plan × yazım turları; kullanım sınırı | Aşama uzar | Sahne başına dilim; ≤ 5 paralel (tahmin); ≤ 2 SubagentStop turu; deterministik işin hepsi betikte |
| R11 | Şema ağırlaşır, ajan alan atlar | Sessiz eksik | `plan_sema.py` zorunlu alanları HATA yapar; `miras` ve `derlenir` yazımı yükü azaltır |
| R12 | **(yeni)** Z1 dalgaları üretim süresini uzatır ([UM] ≈13 saat tahmininin üstüne) | Takvim | ≤ 3 dalga; zincirler sahne başına 1–2 halka; örtülü devam çoğu zinciri tek halkada bitirir; DAG gönderimi hızlandırmaz, yalnız sıralar |
| R13 | **(yeni)** Z1 karesi 720p'dir, sıkıştırma ve hareket bulanıklığı taşır | Başlangıç karesi kalitesi düşer | Bitiş tutmasından kare seçilir (Y55); derinlik ≤ 2; G1-zincir; tutmazsa planlanmış görsele düşülür |
| R14 | **(yeni)** Tek `yonetmen` ajanının çok kipli olması bağlamı kirletebilir | Kip karışması | Her görev yeni örnektir; kip şablonu ayrıdır; GIRDI yalnız o kipin dilimidir |
| R15 | **(yeni)** Durum dondurma karmaşıklığı | Hatalı "bayat" yayılımı | `test_plan_dili.py` senaryo 5; özet tabanlı karşılaştırma |

**4.9.2 Diğer uzmanlarla kalan çakışma noktaları** (çözüm önerileri §2'de)
1. **[GS]** Durumun yeri ve biçimi (İ-1), kroki sahipliği (İ-3), Z1/Z2 dengesi (İ-2): [GS] Z1'i zaten istiyordu, fark yalnız Z2'nin hedefli kullanımında ve planlanmış görselin her plana üretilmesinde.
2. **[UM]** `bitis_karesi` varsayılanından Z1'e geçiş (İ-2) ve parti başına tek çağrı (İ-4).
3. **[KU]** Tek kırpma kaynağı (İ-5); ayna yasağının tek yerde hesaplanması (İ-10); dondurma (İ-11). Y31'deki "L kesmede görüntü + taşma ≥ formül" yorumunu kurgucu T1'de onaylamalı.
4. **[SN]** Sahne uçlarının şeması (Ç-9) ve tek teknik bölme istisnası (İ-14).
5. **[SM]** Türetilmiş dudak alanları ve adım id'leri (İ-9).
6. **[CM]** Bash'siz yönetmen ve önceden hesaplanmış kurulum önerileri (İ-8); kroki mekân başına.
7. **Orkestratör:** rapor klasörü ve çıkış kodları (Ç-21).

**4.9.3 Açık sorular** (ölçülmeden karar verilmemeli)
1. Omni 1.1 Flash saniyeli adım sırasına ve zamanlamasına ne kadar uyuyor? `aralik` ile `sira` biçimlerinden hangisi daha iyi? (R1; ilk parti V3.)
2. Z1 karesi (1280×720 → 1376×768) başlangıç karesi olarak kaliteyi ne kadar düşürüyor? ([GS] açık soru 3; pilotta derinlik 0/1/2 karşılaştırması.)
3. Konuşmalı klipte Bitir karesi dudak hareketini bozuyor mu, kapalı ağızla bitişe zorluyor mu? Ölçülene kadar konuşmalı planda Z2 yok (Y56).
4. **(yeni)** Aynı planda Z1 başlangıç **ve** Z2 Bitir birlikte (Flow Kareler modu: başlangıç + bitiş) morf riskini artırıyor mu?
5. Veo videonun ilk karesi başlangıç görseline ne kadar sadık? (A2'de DINOv2 ≥ 0,85 tahmini var.)
6. 720p **10 sn** klibin kredisi ölçülmedi (bilinen: 360p 10 sn = 7 (KR), 720p 8 sn = 12 (FK)). 17–20 kelimelik replik 10 sn ister.
7. **(yeni)** SubagentStop kancası durmayı engelleyip hata listesini yönetmen ajanına geri verebiliyor mu? `maxTurns`'e ulaşan ajanda tetikleniyor mu? ([CM] §9.4-3; bir kez denenmeli.)
8. **(yeni)** Plan seyircisi (Y6) gerçekten ek bir şey yakalıyor mu? İlk filmde Y6'nın KRİTİK bulgularının animatikte tekrar yakalanma oranı ve Y6'nın tek başına yakaladığı bulgular sayılır. Tek başına yakaladığı bulgu yoksa Y6 kaldırılır ve karar ders defterine yazılır.
9. 720p'de OY ölçekli yüzde SFace güvenilir mi? Y44 ve Y32 eşikleri B3'ün 44 karelik etiketli setiyle ayarlanmalı (A2 §7; [GS] açık soru 7).
10. MediaPipe yaw işaretinin bakış yönüne çevrimi bir test görselinde bir kez doğrulanmalı (A2 §4).
11. Aynı anda kaç `yonetmen` plan örneği çalıştırılabilir? Kullanıcının Claude kullanım sınırına bağlı (tahmin: 5).
12. Flow "Extend / Jump to" (A2 §2.2, doğrulanmadı) Z1'in yerine geçer mi? Model değiştirme uyarısı riski var; denenmeden kullanılmaz.

**4.9.4 Bu turda bilerek dışarıda bıraktıklarım**
- Görsel ve video kapılarının kendi eşikleri ve araçları [GS]'nindir; burada yalnız kullandığım alanlar yazıldı.
- Duygu haritası, merak ve kurulum defterleri [SN]'nindir.
- Müzik, ambiyans ve LUFS [SM]'nindir.
- Memmet temposu, sağlayıcı geçişi, bütçe ve görev defteri [UM] ve [CM]'nindir.
