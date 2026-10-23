# TUR 1 — KURGUCU UZMANI

Rol: kurgucu. Odak: duygu eğrisinin ve plan sürelerinin uygulanması, animatik film, kırpma, J/L kesme,
kurgu izleme denetimi, yeniden çekim kuyruğu ve bütçe, CapCut taslağı ve kullanıcı notları.
Tarih: 23.10.2026. Diğer uzmanların dosyaları okunmadı.

Kaynak kısaltmaları: `ZN` = `ZANAAT.md`, `RE` = `ritim_esikleri.json` (anahtar adıyla), `BK` = `BILGI_KURALLARI.md`,
`AR1/AR2/AR3` = `arastirma/01_film_hatlari.md`, `02_sureklilik.md`, `03_ses_ve_claude_code.md`,
`DR` = `03_DERSLER.md`, `UH` = `01_URETIM_HATTI.md`, `YR` = `YAPIM_REHBERI.md`, `H/<ad>` = `HAFIZA_YEDEGI/<ad>.md`.
Kaynağı olmayan her sayı **(tahmin)** diye işaretlidir.

---

## 1. Alanımın hedefi ve başarı ölçütü (sayılarla)

### 1.1 Hedef (tek cümle)
Kâğıttaki plan listesini, **video kredisi harcanmadan önce** izlenebilir bir animatik filmle ve **kullanıcıya
gösterilmeden önce** kurgulanmış filmle iki kez habersiz seyirciye "izletip" geçirmek; ZANAAT'taki süre, ritim
ve duygu eğrisi eşiklerini dört ayrı zaman çizelgesinde (kâğıt → animatik → kaba kurgu → CapCut) aynı kodla ölçmek;
kopuklukları önce **0 kredili** kurgu çözümleriyle, gerekmezse bütçe sınırlı yeniden çekimle kapatmak; sonunda
kullanıcıya boşluksuz, katmanlı, sürümlü bir CapCut taslağı vermek.

### 1.2 Bugünkü kodda alanımın durumu (neden bu hedef)
Kodu okuyunca gördüğüm, "gereksiz uzun" ve "kopuk" notlarının (ZN §7.1) doğrudan teknik nedenleri:
1. **`kullanim{bas,sure}` hiçbir yerde uygulanmıyor.** `capcut_film.py` her klibi `source_timerange=(0, L)` ile tam
   boy koyuyor; `film.py`'nin ffmpeg önizlemesi tam klipleri art arda ekliyor; `izleme_paketi.py` kareleri tam
   klip süresinden alıyor. Yani 8 sn'lik klip olduğu gibi kullanılıyor. ZN §7.1'de "gereksiz uzun" notunun ilk kök nedeni olarak yazılan durum budur.
2. **Ambiyans plan başına.** `capcut_film.py` her replikli klibin kendi demucs zeminini "Ortam" kanalına koyuyor.
   Klip geçişinde zemin değişiyor (DR: kapı sahnesi dersi). Sahne başına tek zemin yok.
3. **J/L kesme yok.** Diyalog ses dosyaları klibin kendi aralığına kırpılıyor (`ln = min(..., us(t0)+L-st)`); bir
   repliğin sonraki plana taşması mümkün değil.
4. **Animatik, kurgu izleme kapısı, yeniden çekim kuyruğu, taslak farkı kodda yok** (`plan_kurgu.py`,
   `animatik.py`, `taslak_fark.py`, `dudak_denetim.py` belgede var, pakette yok: CLAUDE.md).
5. **Seyirci paketi ad sızdırıyor.** `izleme_paketi.py` duyulan repliği `MARA: "..."` diye konuşanın adıyla yazıyor.
   Seyirci adı ekranda duymadan öğreniyor; Z1 #23 ("ad ≤ 120 sn'de sözle") bu paketle ölçülemez.
6. **Puan ortalamayla birleşiyor.** `puan_oku.py` ortalama alıyor, 3 ölçüt okuyor. ZN §7.2.10 ve §7.3 **medyan** ve
   **6 ölçüt** istiyor.

### 1.3 Başarı ölçütleri

| # | Ölçüt | Hedef | Kaynak |
|---|---|---|---|
| B1 | Animatik habersiz seyirci (3 seyirci, parti başına) | GENEL medyan ≥ 8, hiçbir ölçüt medyanı < 7, KRİTİK = 0, ORTA ≤ 3/parti, özet eşleşmesi ≥ %80 | ZN §7.3, RE `seyirci_*`, `kopukluk_*`, `ozet_eslesme_min` |
| B2 | İlk 2 dk testi (animatik ve kurgu) | 3 seyircinin 3'ü "devam ederdim" | ZN §7.2.2, RE `ilk2dk_devam_evet_min` |
| B3 | Kurgu izleme (kare paketi) | B1 ile aynı eşikler; en çok 3 tur | ZN §7.3, RE `kurgu_tur_max` |
| B4 | Zaman çizelgesi kapıları (her aşamada) | Z0 zaman ölçüleri + Z2 + Z3'te HATA = 0 | ZN §6.2 |
| B5 | Film süresi | 1800–2700 sn (kart + jenerik dahil); dolgu yok | RE `film_sure_aralik_sn`, ZN §2.5.5 |
| B6 | ASL | film 4,2–5,2 sn; ilk 120 sn ≤ 4,0; ilk 30 sn ≤ 3,5; parti hedefi ±0,6 | RE `asl_*`, `ilk120_asl_max_sn`, `ilk30_asl_max_sn` |
| B7 | Diyalog sahnelerinde tepki planı / J-L kesme oranı | ≥ %25 / ≥ %30 | RE `tepki_orani_min`, `jl_kesme_orani_min` |
| B8 | Görünen konuşanın sesi ile dudağı arasındaki yerleşim kayması | ≤ 1 kare (24 fps'te ≤ 42 ms) | AR3 öneri 4 (offset 0 ±1 kare; mühendislik tercihi) |
| B9 | Dudakları oynayan karakterin üstüne başkasının repliği | 0 | H/video-istem-kurali |
| B10 | CapCut taslağı | boşluk 0, eksik medya 0, taslak ↔ KURGU_PLANI farkı 0 | H/capcut-elle-duzenleme |
| B11 | Video öncesi kesilen plan | Animatik kesme turunda ≥ 1 kesme önerisi uygulanır (kesilen plana video kredisi harcanmaz) | ZN §7.2.9 (kesme turunu animatiğe de uyguluyorum) |
| B12 | Kurgu aşamasında yeniden çekim | ≤ temel video kredisinin %8'i **(tahmin)**; toplam yeniden deneme payı %20'yi aşmaz | RE `kredi_yeniden_deneme_payi` (0,2); %8 bölüşümü tahmin |
| B13 | Kullanıcı notu | notların %100'ü `NOT_CEVAPLARI.md`'de bir kararla kapanır; kullanıcı kurgu kararı aynen uygulanır | BK §5.3.3 |

**Ölçeği göstermek için karşılaştırma:** B2'de animatik atlanmış (ortak hesap, H/proje-b2) ve **50+ yeniden çekim**
olmuştu (`04_KIM_NE_YAPTI.md`). İlk taslaktaki 134 video klibine oranla bu ≈ %37'dir (oran hesabı bana ait).
B12'nin %8 hedefi, kopuklukların çoğunun animatikte, yani kredisiz yakalanacağı varsayımına dayanıyor (tahmin).
İlk filmde gerçek oran ölçülüp ders defterine yazılır (§8.5).

## 2. Aşama aşama süreç

### 2.1 Temel ilke: tek veri yapısı, dört zaman çizelgesi
Kurgunun tek kaynağı `KURGU/KURGU_PLANI.json` olur (şema §5.1). `SAHNELER.json` **neyin üretileceğini**,
`KURGU_PLANI.json` **nasıl birleştirileceğini** söyler. Ölçülen her şey (gerçek süre, kırpma, J/L, kullanıcının
CapCut kararı) KURGU_PLANI'na yazılır; SAHNELER.json'a yalnız yönetmenin planı kalır.

Aynı çizelge dört kez, her seferinde daha gerçek verilerle kurulur ve **aynı kodla** ölçülür:

| Çizelge | Ne zaman | Plan süresi nereden gelir | Ses nereden gelir |
|---|---|---|---|
| **T0 kâğıt** | SAHNELER.json + istem denetimi geçince | `zanaat.sure_sn` (yönetmen), diyalogda ZN §2.3 formülü | yok (formül) |
| **T1 animatik** | görseller G1'den geçince | T0 + TTS ile ölçülen gerçek replik süreleri | TTS (seçilen karakter sesi) |
| **T2 kaba kurgu** | videolar V1/V2'den geçince | gerçek klipten ölçülen kırpma (`kirp_oner.py`) | dönüştürülmüş Veo sesi ya da TTS (ses kararına göre) |
| **T3 CapCut** | kullanıcı taslakta değişiklik yaparsa | kullanıcının kırpması (`taslak_fark.py`), kilitli | aynı |

**Geri gidiş yasağı:** Bir ölçü Tk'de geçtiyse ve Tk+1'de HATA veriyorsa, düzeltilmeden taslak kullanıcıya verilmez.
T0→T1→T2 arasındaki plan süresi farkları `_RAPOR/SAPMA_T<k>.json`'a yazılır ve ders defterini besler (§8.5).

### 2.2 Adımlar
Her adım şu düzende yazıldı: **Girdi → İş → Çıktı → Geçme şartı → Kim.**
Kısaltmalar: ana Claude = beceriyi yürüten oturum; betik = `YZ_FILM/ARACLAR/` aracı (`film.py` aşaması olarak).

**K0. Kâğıt zaman çizelgesi (T0)**
- Girdi: `SAHNELER.json` (zanaat + süreklilik alanlarıyla), `ritim_esikleri.json`.
- İş: `zaman_cizelgesi.py --asama kagit` planları sıraya dizer. Kartları, seri kancasını ve jeneriği çizelgeye ekler,
  J/L ofsetlerini uygular, olay listesini (her ad, risk, merak, kurulum olayının saniyesi) çıkarır.
  Aynı araç zamana bağlı ölçüleri hesaplar (§7.1'deki "T0" sütunu).
- Çıktı: `KURGU/surumler/KURGU_PLANI_T0.json`, `_RAPOR/ZAMAN_T0.json`, `_RAPOR/EGRI_T0.png` (hedef eğri ile plan eğrisi aynı grafikte).
- Geçme: zamana bağlı HATA = 0. BAYRAK'lar yönetmene ya da hikâye odasına gider (revizyonu metni yazan yapar, YR §1).
- Kim: betik. Yönlendirmeyi ana Claude yapar.

**K1. Animatik sesi (TTS)**
- Girdi: `SAHNELER.json` replikleri ve `ekran_disi_ses` satırları, karakterlerin seçilmiş sesleri (seri kütüphanesi).
- İş: Her replik TTS ile üretilir (AI84, önbellekli, aynı cümle iki kez ücretlenmez). Kelime zamanları bilinen metne
  hizalanır (stable-ts `align`, AR3 A4). Karakter başına gerçek konuşma hızı ölçülür (kelime/sn).
- Çıktı: `SESLER/TTS/R<plan>_<j>.wav`, `SESLER/replik_olcum.json`.
- Geçme: Her replik planına sığar: `giriş 0,4 + replik + çıkış 0,5 ≤ sure_sn + izinli L taşması`. Sığmayan replik
  BAYRAK olur ve yönetmene gider (repliği böl ya da ekran dışına taşı, ZN §2.3).
- Kim: betik (`--saglayici sahte` ile bulutta bip). Maliyet: ≈ 2.100–2.600 kelime (ZN §2.6) ≈ 14 bin harf ≈ 14 bin AI84
  kredisi (harf sayısı tahmin; 1 kredi/harf, BK §6.4). Bakiyenin (≈ 649 bin) ≈ %2'si. Onay, `film.py`'nin kredili aşama sorusuyla alınır.

**K2. Animatik kurgu planı (T1)**
- Girdi: T0 + `replik_olcum.json`.
- İş: `zaman_cizelgesi.py --asama animatik` formül süresini ölçülen süreyle değiştirir. Cevap boşluğunu (0,2–0,6 sn)
  ve J/L ofsetlerini gerçek sesle yerleştirir, ölçüleri yeniden hesaplar.
- Çıktı: `KURGU_PLANI_T1.json`, `_RAPOR/ZAMAN_T1.json`, `_RAPOR/SAPMA_T1.json`.
- Geçme: T0 ile aynı.
- Kim: betik.

**K3. Animatik film (video kredisi yok)**
- Girdi: T1, G1'den geçmiş başlangıç kareleri (`SIRALI_GORSEL/`), TTS, sahne ambiyans zeminleri, müzik listesi.
- İş: `kurgu_render.py --animatik` (ayrıntı §6.1). İçerik:
  - Her plan kendi `sure_sn`'i kadar ekranda kalır.
  - Durağan kareye `hareket_tipi`'nden türetilen yavaş hareket uygulanır (Ken Burns).
  - Eylem şeridi: `eylem_zinciri` adımları kadrajın altında, plan içindeki saniyelerinde, ayırt edici italik yazıyla gösterilir.
    Yalnız görünür eylem yazılır; `amac`, `risk`, `vurus` asla yazılmaz.
  - Kartlar, Diyalog (TTS, J/L dahil), sahne başına tek ambiyans zemini, efektler (ses planında varsa) ve müzik eklenir.
    Gerçek müzik yoksa leitmotif listesinden geçici müzik çalar ve `GECICI` diye işaretlenir.
  - Karışım −14 LUFS'a çekilir.
- Çıktı: `ANIMATIK/animatik_v<N>.mp4`, parti başına `animatik_v<N>_P<p>.mp4`. İsteğe bağlı aynı içerikte CapCut taslağı ("YZ <FILM> ANIMATIK v<N>").
- Geçme: süre = T1 toplamı ±0,1 sn. `kalite_denetim.py`: planlanmamış siyah ya da sessizlik yok.
  Görseli eksik (yer tutucu) plan oranı ≤ %10 (tahmin). Üstündeyse animatik izletilmez, görsel aşamasına dönülür.
- Kim: betik.

**K4. Animatik izleme turu (tur n)**
- Girdi: K3 çıktısı.
- İş: `izleme_paketi.py --asama animatik --tur n` paketi kurar (§5.4). Paketle iki iş yapılır:
  - Parti başına **3 yeni** `kurgu-seyircisi` ajanı paketi izler.
  - Ayrıca ilk 120 sn için 3 seyirci "devam eder miydin" testi yapar.
  - `puan_oku.py` medyanı alır, `ozet-eslestirici` özet eşleşmesini ölçer.
- Çıktı: `_RAPOR/SEYIRCI/T1_tur<n>_P<p>_s<k>.{md,json}`, `_RAPOR/SEYIRCI_KARAR_T1_tur<n>.json`.
- Geçme: B1 + B2 (§1.3).
- Kim: ana Claude ajanları başlatır. Puanları betik birleştirir.

**K5. Animatik düzeltmesi ve kesme turu**
- Girdi: `SEYIRCI_KARAR_T1_tur<n>.json`, T1.
- İş: `kurgucu` ajanı her kopukluğu sınıflar (§5.6 kök neden sözlüğü):
  - Kurgu düzeyindekiler (süre, sahne içi sıra, J/L, kart zamanı, ekran dışı replik) KURGU_PLANI'nda hemen düzeltilir.
  - Hikâye/plan düzeyindekiler `YENIDEN_YAZ.json`'a (kâğıt, 0 kredi) yazılır → yönetmen düzeltir → değişen görseller
    yeniden üretilir (0 kredi) → G1 → K1–K3 yalnız değişen planlar için tekrarlanır.
  - **Kesme turu yalnız 1. turda yapılır:** `kesici` ajanı en çok 10 plan + 2 sahne önerir. İki seyircinin ortak
    işaretlediği sıkılma anları (RE `sikilma_ortak_isaret_min`) bu öneriye eklenir. `kurgu_denetim.py --kesme-simule`
    her öneriyi çizelgeden çıkarıp Z0/Z1/Z2'yi yeniden çalıştırır. Yeni HATA getirmeyenlerden en az %50'si uygulanır
    (RE `kesme_turu_oneri`). Kesilen plana video kredisi harcanmaz.
  - Yeni seyirciyle K4'e dönülür.
- Çıktı: `KURGU/KURGU_KARARLARI_T1_tur<n>.json`, `YENIDEN_YAZ.json`, `KESME_ONERI_T1.json`, yeni `KURGU_PLANI_T1`.
- Geçme: B1 + B2 sağlanınca `FILM_DURUM.json`'da `animatik: ONAYLI` yazılır. En çok 3 tur (tahmin; RE'de kâğıt için 4, kurgu için 3 var).
  3 turda geçmezse hat DURUR: en düşük 3 ölçüt ve öneriler raporlanır, hikâye odasına yapısal revizyon gider.
  **Video aşamasına geçilmez** (kesin karar 6). `--onayli` modda animatik kullanıcıya gösterilir. Tam otomatikte
  dosya hazır tutulur, kullanıcı beklenmez (kesin karar 1).
- Kim: `kurgucu` + `kesici` ajanları, betikler. Plan metnini yönetmen ajanı düzeltir.

**K6. Kare zinciri çıkış noktası (video aşamasının içinde)**
- Girdi: `gecis_turu: devam` olan A→B çifti, A'nın videosu (V1/V2'den geçmiş).
- İş: B üretilmeden önce `kirp_oner.py --zincir A` A'nın çıkış noktasını (`bas+sure`) kesinleştirir. **O andaki** kare
  çıkarılır ve B'nin başlangıç karesi olur. Klibin en son karesi alınmaz. G1 bu kareyi denetler, sonra B üretilir.
- Çıktı: `SIRALI_GORSEL/<B>.jpg` (zincir karesi), KURGU_PLANI'nda A için `goruntu.kullanim_kilit: "zincir"`.
- Geçme: Çıkış noktası klibin son 0,5 sn'sine düşüyorsa yalnız bitiş tutması (hold) varsa kabul edilir (RE `kullanim_son_pay_sn`).
  Zincir derinliği ≤ 2 (AR2 §2.3).
- Kim: `film.py` video aşaması betiği çağırır.
- Not: A yeniden çekilirse B de yeniden çekilmek zorunda kalır (zincir). Kuyruk bunu maliyete katar (§5.5).

**K7. Kaba kurgu (T2)**
- Girdi: bütün videolar (V1/V2 raporlarıyla), son diyalog sesi (ses uzmanının yolu), ambiyans ve efekt planı, müzik listesi, T1.
- İş: `plan_kurgu.py` her planın kırpmasını `kirp_oner.py`'den alır. Kaynaklar: hareket başlangıcı, whisper kelime
  zamanları, V1/V2 kusur anları, klip içi kesme. Sonra:
  - Diyalog **klip zamanıyla tutarlı** yerleşir (§8.1 senkron kuralı).
  - Ekran dışı replikler, J/L, sahne ambiyansı, efektler (ölçülen eylem anlarına) ve müzik (olay anlarına) yerleşir.
  - `kurgu_render.py` önizlemeyi üretir.
  - `kurgu_denetim.py` Z3'ü, senkronu ve ses ölçülerini çalıştırır, `dudak_denetim.py`'yi çağırır.
  - `zaman_cizelgesi.py` T2 ölçülerini ve T1↔T2 sapmasını hesaplar.
- Çıktı: `KURGU_PLANI_T2_v1.json`, `KURGU/onizleme_v1.mp4` (720p + karışım), `_RAPOR/Z3_v1.json`, `ZAMAN_T2_v1.json`, `SAPMA_T2.json`.
- Geçme: Z3 HATA = 0, geri gidiş yok. `kirp_oner` güveni < 0,6 olan kırpmalara (tahmin) `kurgucu` ajanı kareleriyle bakar.
- Kim: betikler, gerekirse `kurgucu`.

**K8. Kurgu izleme turu (tur n ≤ 3)**
- Girdi: önizleme ve KURGU_PLANI.
- İş: `izleme_paketi.py --asama kurgu`. Gerçek kareler kırpılmış pencereden alınır. Akış K4 ile aynıdır.
  2. ve 3. turda yalnız geçemeyen ya da değişen partiler yeni seyirciye izletilir. Seyirciye önceki partiler için
  bir önceki turun **seyirci özetleri** verilir. Bu özet ekrandan çıkarılmıştır, hikâye belgesi değildir.
- Çıktı: `_RAPOR/SEYIRCI/T2_tur<n>_*`, `SEYIRCI_KARAR_T2_tur<n>.json`.
- Geçme: B3.
- Kim: ana Claude + `kurgu-seyircisi`, betikler.

**K9. Kurgu düzeltmesi ve yeniden çekim kuyruğu**
- Girdi: `SEYIRCI_KARAR_T2_tur<n>.json`, `Z3`/`K1` (süreklilik) raporları, `BUTCE.json`.
- İş: `kurgucu` her kopukluğu **0 kredi merdiveninden** geçirir (§5.5):
  - Önce: kırp/uzat → sahne içi sıra → J/L ya da ekran dışı replik → alternatif çekim → mevcut klipten bölme →
    ayna ya da yeniden kadraj (koşullu) → kart/efekt ipucu → planı kesmek.
  - Bunlar yetmezse kredili adımlar: aynı planın yeniden çekimi (CORRECTION cümlesiyle) → bağlayıcı yeni plan.
    Yeni planın metnini yönetmen yazar; kurgucu yalnız gereksinimi tarif eder.
  - Kredili işler `kuyruk.py` ile `YENIDEN_URET.json`'a girer (öncelik + maliyet + zincir etkisi).
  - `URETIM_ONIZLEME.md` yazılır, bütçe denetlenir. `film.py --asama video --sahne <liste>` yalnız listedekileri üretir
    (Memmet, Flow kuralları, uyarıda DUR) → V1/V2 → değişen planlar için K7 (efekt yerleşimi dahil, DR) → yeni turla K8.
  - Tur 1'in sonunda kesme turu yapılır (K5'teki gibi).
- Çıktı: `KURGU_KARARLARI_T2_tur<n>.json`, `YENIDEN_URET.json`, `URETIM_ONIZLEME.md`, yeni KURGU_PLANI sürümü.
- Geçme:
  - KRİTİK madde kuyrukta kalmaz.
  - Bütçe biterse kalan maddeler 0 kredi çözümüne düşer. KRİTİK için o da yoksa hat DURUR ve "kredi gerekiyor"
    bildirimi gider. Bu bir soru değil, bildirimdir. KRİTİK'li taslak kullanıcıya verilmez.
  - 3 turda B3 sağlanmazsa en iyi medyanlı sürüm taslak yapılır. Eksikler raporda açıkça yazılır (BK §7.13 "yüzüne vur").
- Kim: `kurgucu`, `yonetmen` (yeni plan metni), `istem-muhendisi` (derleme), betikler.

**K10. CapCut taslağı**
- Girdi: son KURGU_PLANI.
- İş: `capcut_film.py` KURGU_PLANI'ndan sürümlü bir taslak kurar: "YZ <FILM> v<N>". Kanallar: Klipler (kırpılmış),
  Bantlar, Kartlar, Altyazi, Diyalog, Efekt, Ambiyans, Muzik, NOTLAR.
  Segment ↔ plan eşlemesi `son_capcut_projesi.json`'a yazılır. Altyazı gerçekte söylenen metinden üretilir (§8.6).
- Çıktı: CapCut taslağı, `KURGU/son_capcut_projesi.json`, `KURGU/altyazi_en.srt`.
- Geçme: yeni kurulan taslakta `taslak_fark.py` farkı 0. Boşluk 0, eksik medya 0, süre = KURGU_PLANI ±1 kare.
- Kim: betik. Ana Claude kullanıcıya tek mesajla "taslak hazır" der; soru sormaz.

**K11. Kullanıcı notu ya da düzenlemesi (isteğe bağlı döngü)**
- Girdi: kullanıcının "değiştirdim / not bıraktım" demesi.
- İş:
  - `taslak_fark.py` (salt okunur; `Timelines/` kopyası ve birleşik klip içi dahil) ve `notlari_oku.py` çalışır.
  - Kullanıcının değişiklikleri KURGU_PLANI'na `kaynak: kullanici` ve kilitli olarak işlenir. Kullanıcı kararı aynen uygulanır (BK §5.3.3).
  - Ardından yeniden denetlenir: kurulum (Z1), dünya durumu zıplaması yeni sırayla, senkron/dudak, ambiyans ve efekt hizası.
  - Silinen planın götürdüğü bilgi için kurgucu bağlayıcı çözüm önerir (DR: "miğferin inişi").
  - Taslak karar ağacı §8.7'dedir.
- Çıktı: `KURGU/TASLAK_FARK.json`, `NOTLARIM.json`, `NOT_CEVAPLARI.md`, yeni sürüm taslak ya da yerinde değişen dosyalar.
- Geçme: B10 + B13. Kullanıcı kesmesinden doğan yeni KRİTİK varsa kullanıcıya bir cümleyle söylenir (soru değil, bilgi), önerilen çözüm uygulanır.
- Kim: betikler + `kurgucu`.

**K12. Teslim (kurgu payı)**
- İş:
  - NOTLAR kanalı olmayan "yayın" taslağı kurulur (kullanıcı silmeyi unutmasın; BK §5.3.10).
  - Kullanıcı dışa aktardığı mp4'ü `YAYIN/`'a koyarsa `kalite_denetim.py` −14 LUFS / ≤ −1 dBTP'yi ve siyah/donma/sessizliği denetler.
  - Bölüm (chapter) zamanları KURGU_PLANI'ndaki parti ve vuruş sınırlarından yayın paketçisine verilir.
  - Kurgu dersleri deftere işlenir.
- Kim: betik + ana Claude.

### 2.3 `film.py` aşama sırası (kurgu payı eklenmiş hâli)
`senaryo → istem_denetim → zaman_T0 → [kartlar, gorsel → G1] → tts → animatik(T1) → animatik_izleme ⟲ →
video(+K6 zincir) → V1/V2 → ses → kaba_kurgu(T2) → kurgu_izleme ⟲ yeniden_cekim → capcut → (notlar ⟲) → yayin`.
`⟲` = döngü kapısı. Durum `FILM_DURUM.json`'da tur numarası, parti sonuçları ve harcanan krediyle tutulur.
Kesintiden sonra kaldığı turdan devam edilir (AR3 B6: "hafızaya değil deftere güven").

## 3. Gereken ajanlar

Genel kural (AR3 B5, YR §1):
- Her ajanın tek bir işi ve en az aracı olur.
- Yargı işleri Opus + yüksek effort ile yapılır (H/ajan-opus-yuksek). Mekanik karşılaştırma Sonnet ile yapılır.
- Deterministik her şey betikte kalır.
- Ajan KURGU_PLANI'nı **elle düzenlemez**. Bir işlem listesi yazar, `kurgu_uygula.py` bu listeyi uygular ve denetler
  (AR3 B4: plan → doğrula → uygula).

| Ajan | Model | Araçlar | Görev | Okur | Çıktı |
|---|---|---|---|---|---|
| **kurgucu** (yeni) | opus, effort high | Read, Write, Glob, Grep, Bash (yalnız `python YZ_FILM/ARACLAR/{kurgu_uygula,kurgu_denetim,kirp_oner,izleme_paketi,zaman_cizelgesi}.py`; hook ile sınırlanır) | Seyirci, Z3, K1 ve dudak raporlarındaki her bulguyu sınıflar ve 0 kredi merdivenini uygular. Kırpması düşük güvenli planlara karelerle bakar. Kullanıcı notlarını ve taslak farkını işler. Yeniden çekim gereksinimini tarif eder ama istem yazmaz. | `KURGU_PLANI.json`, `SEYIRCI_KARAR_*.json`, seyirci JSON'ları, `_RAPOR/Z3_*`, `K1_*`, `V2_*`, `DUDAK_*`; `SAHNELER.json` (tamamı; kurgucu habersiz değildir); `MERAK_DEFTERI`, `KURULUMLAR`; ZN §2–§5; RE; `BUTCE.json`; `DERS_DEFTERI.json` (kurgu dersleri); `NOTLARIM.json`, `TASLAK_FARK.json` | `KURGU/KURGU_KARARLARI_<T>_tur<n>.json` (işlem listesi, §5.6); `YENIDEN_YAZ.json` maddeleri (yönetmene); `NOT_CEVAPLARI.md` |
| **kurgu-seyircisi** (yeni; mevcut `habersiz-seyirci`'nin izleme modu buraya taşınır) | opus, effort high | **Read, Write** (Glob/Grep/Bash yok) | Animatik ya da kurgu paketini film gibi "izler". 6 ölçütü puanlar, kopuklukları plan numarasıyla listeler. Sıkıldığı anları, ilgi eğrisini (dakika başına 1–10), açık sorularını, 3 cümle özetini ve "kahraman neyi kaybedebilir" cevabını yazar. İlk 120 sn modunda yalnız devam kararını verir. | Yalnız istemde verilen yollar: `IZLE.md`, `sayfa_*.jpg`, P2/P3 için `ONCEKI_OZET.md` | `_RAPOR/SEYIRCI/<T>_tur<n>_P<p>_s<k>.md` + `.json` (§5.3), son satır OZET |
| **kesici** (yeni) | opus | Read, Write | Tek soruya cevap verir: "Hangi 10 planı ya da 2 sahneyi atarsak film daha iyi olur?" (ZN §7.2.9). Her öneri için gerekçe ve beklenen kazancı (sn) yazar. | `KESME_DOKUMU.md` (plan başına zaman kodu, süre, `ekranda_bilgi`, duyulan metin, eylem; `amac` yok), 1 kare/plan kontak sayfaları, iki seyircinin ortak işaretlediği sıkılma anları | `KURGU/KESME_ONERI_<T>.json` |
| **ozet-eslestirici** (yeni) | sonnet | Read, Write | Seyirci özetini hikâye odasının `ANAHTAR_OLGULAR_P<p>.json` listesiyle karşılaştırır. Her olgu için `bulundu / kismen / yok` kararı ve seyirci metninden alıntı verir. Oranı kendisi hesaplamaz; `puan_oku.py` hesaplar. | seyirci `.json` özeti, `ANAHTAR_OLGULAR_P<p>.json` | `_RAPOR/SEYIRCI/<T>_tur<n>_P<p>_s<k>_eslesme.json` |

### 3.1 Ajan gövdelerinin taslağı (frontmatter + kritik kurallar)

```markdown
---
name: kurgu-seyircisi
description: Use when an animatic or edited cut must be watched by a first-time viewer — kurgu izleme, animatik izleme,
  habersiz seyirci kare paketi, ilk 2 dakika testi. Reads ONLY the package paths given in the prompt; every call must be
  a fresh instance.
tools: Read, Write
model: opus
effort: high
---
Sen bu filmi ilk kez izleyen bir YouTube seyircisisin. Sana verilen IZLE.md'yi baştan sona sırayla oku. Her `sayfa_NN.jpg`
dosyasını sırası gelince Read ile aç. Bu yolların dışında hiçbir dosya açma, klasör listeleme.
- Animatik modunda: kareler planın durağan başlangıç kareleridir, alttaki italik yazı o planda görünen hareketi anlatır.
  Hareketin kareden okunamaması kusur değildir. Kim, nerede, ne oldu, neden: bunlar anlaşılmıyorsa kusurdur.
- Kurgu modunda: her satır bir plandır (baş/orta/son karesi). Önceki satırın son karesi ile bu satırın ilk karesi
  arasındaki geçişe özellikle bak.
- Adını ekranda duymadığın karakteri adıyla anma; "sol taraftaki kadın" gibi tarif et.
Puanla (1–10, cömert olma): anlasilirlik, akicilik, merak, duygu, ritim, ilk30. Kopukluklar KRITIK/ORTA/KUCUK,
plan numarasıyla. Sıkıldığın anlar zaman koduyla. Dakika başına ilgi (1–10). Aklındaki açık sorular. 3 cümle özet,
karakterler, "kahraman neyi kaybedebilir?". JSON'u verilen yola yaz (şema IZLE.md'nin sonunda). Son satır:
OZET | anlasilirlik: 8 | akicilik: 7 | merak: 8 | duygu: 7 | ritim: 7 | ilk30: 9 | GENEL: 8 | KRITIK: 0 | ORTA: 2
Yalnız dosya yolunu ve OZET satırını döndür.
```

```markdown
---
name: kurgucu
description: Use when edit findings must be turned into concrete cut decisions — kurgu düzeltme, kırpma, J/L kesme,
  sıra değişikliği, yeniden çekim kuyruğu, CapCut notları, taslak farkı. Use proactively after every animatik/kurgu
  seyirci round and after the user edits the CapCut draft.
tools: Read, Write, Glob, Grep, Bash
model: opus
effort: high
memory: project
---
Sen filmin kurgucususun. Kural sırası: Murch (duygu > hikâye > ritim > göz izi > 2B > 3B, ZN §3.4).
1. Önce 0 kredi merdiveni (ZN §2.2, bu belgenin §5.5'i); kredili çözümü ancak merdiven tükenince öner.
2. KURGU_PLANI'nı elle düzenleme. İşlem listesini KURGU_KARARLARI JSON'una yaz, `kurgu_uygula.py --kuru` ile dene,
   HATA yoksa `--uygula`.
3. Kullanıcının (`kaynak: kullanici`) kırpma/sıra kararını asla geri alma; yarattığı açığı bağlayıcı çözümle kapat.
4. Dudağı oynayan karakterin üstüne başkasının repliğini koyma. Görünen konuşanın sesini klip zamanından kaydırma.
5. Her işlemin yanına `kok_neden` (§5.6 sözlüğü) yaz: ders defteri bundan beslenir.
Son satır: OZET | islem: 14 | sifir_kredi: 11 | yeniden_cekim: 2 | yeni_plan: 1 | kredi_tahmini: 36
```

`kesici` ve `ozet-eslestirici` gövdeleri aynı kalıpla yazılır: rol → "Çağrıldığında" adımları → çıktı şeması → OZET satırı.

**Habersizliği korumak için üç önlem:**
1. Seyirciye Glob/Grep/Bash verilmez; dosya yolları istemde açıkça yazılır.
2. Paket ayrı bir klasöre (`_RAPOR/IZLEME/...`) kopyalanır ve içinde ad sızdıran bir şey bulunmaz (§5.4).
3. İsteğe bağlı **API modu:** `ANTHROPIC_API_KEY` tanımlıysa `seyirci_api.py`, aynı ajan gövdesini sistem istemi olarak
   kullanıp sayfaları doğrudan Claude API'ye (`claude-opus-5-5`) yollar. Model yalnız gönderileni görür; habersizliğin en
   sağlam garantisi budur. API çağrısı ücretlidir (çağrı başına maliyet `URETIM_ONIZLEME`'de gösterilir).
   Anahtar yoksa ajan modu kullanılır; o mod Claude Code aboneliği içinde kalır.

## 4. Beceri (skill) tarif adımları

Yer: `.claude/skills/film-yap/reference/KURGU.md`. Ana `SKILL.md`'den tek seviye bağlantıyla verilir ve "animatik, kurgu,
CapCut ya da not aşamasına gelince oku" diye yazılır (AR3 B4). Kredili yeniden çekim ayrı bir alt komutla çalışır
(`/film-yap uret`, `disable-model-invocation: true`, AR3 "Skill / ajan yazım kuralları" madde 3). Becerinin ilk satırı durumu gömer:
`` !`python YZ_FILM/ARACLAR/film.py <film> --durum --kurgu` `` (aşama, tur, parti sonuçları, kalan bütçe).

### Tarif A — Animatik turu (K1–K5)
```
[ ] 1. python film.py <film> --asama tts,animatik          (onaylı modda TTS kredisini sorar)
[ ] 2. Çıkış 0 değilse DUR, FILM_KAYIT.txt'deki nedeni kullanıcıya sade Türkçe söyle.
[ ] 3. python izleme_paketi.py <film> --asama animatik --tur <n>   → paket yolları + ilk120 paketi
[ ] 4. Her parti için 3 AYRI kurgu-seyircisi başlat (paralel; birbirinin çıktısını okumaz). Ayrıca ilk120 için 3 seyirci.
       İstem: "Paket: <IZLE.md yolu>. Sayfalar aynı klasörde. Önceki özet: <yol|yok>. Raporu <md yolu>, JSON'u <json yolu>
       dosyasına yaz. Bu yolların dışında dosya açma."
[ ] 5. Her seyirci için ozet-eslestirici başlat (ANAHTAR_OLGULAR_P<p>.json ile).
[ ] 6. python puan_oku.py <film> --asama T1 --tur <n>      → SEYIRCI_KARAR_T1_tur<n>.json (çıkış 0 = geçti)
[ ] 7. Geçmediyse kurgucu ajanını başlat: "SEYIRCI_KARAR_T1_tur<n>.json'u işle." Tur 1'de ana Claude ayrıca kesici
       ajanını başlatır (KESME_DOKUMU.md + sıkılma anları), sonra kurgu_denetim.py --kesme-simule; sonuç kurgucuya verilir.
[ ] 8. Kurgucu'nun YENIDEN_YAZ maddelerini yönetmene SendMessage ile ver (metni yazan düzeltir) → istem_denetim →
       değişen görseller (0 kredi) → G1.
[ ] 9. python kurgu_uygula.py <film> KURGU_KARARLARI_T1_tur<n>.json --uygula → adım 1'e dön (yalnız değişenler yeniden üretilir).
[ ] 10. 3 turda geçmezse DUR: en düşük 3 ölçüt + öneriler → hikâye odasına; kullanıcıya dürüstçe bildir. Videoya GEÇME.
```

### Tarif B — Kaba kurgu (K7)
```
[ ] 1. python film.py <film> --asama kaba_kurgu   (plan_kurgu → kurgu_render → kurgu_denetim → dudak_denetim)
[ ] 2. _RAPOR/Z3_v<N>.json'da HATA varsa: kirp_oner güveni düşük planlar için kurgucuyu çağır
       ("KIRP_INCELE.md'deki planların karelerine bak, kullanim öner").
[ ] 3. SAPMA_T2.json'da T1'den ±%25'ten fazla değişen planlar (tahmin eşiği) kurgucunun ilk işidir: ritim bozulmuş olabilir.
```

### Tarif C — Kurgu izleme turu (K8–K9)
```
[ ] 1. python izleme_paketi.py <film> --asama kurgu --tur <n> [--parti <geçemeyenler>]
[ ] 2. Tarif A adım 4–6 (her turda YENİ seyirci; P2/P3'e önceki partinin seyirci özeti verilir).
[ ] 3. kurgucu: 0 kredi merdiveni → KURGU_KARARLARI_T2_tur<n>.json; tur 1'de kesme turu.
[ ] 4. python kuyruk.py <film> --topla --onizleme   → YENIDEN_URET.json + URETIM_ONIZLEME.md (kredi, zincir etkisi)
[ ] 5. Kredili madde varsa /film-yap uret (Memmet; uyarıda DUR, bot atlatma YOK) → V1/V2 → Tarif B → adım 1.
[ ] 6. KRİTİK=0 ve medyan eşikleri sağlandıysa Tarif E. 3 turda sağlanmadıysa en iyi sürümle Tarif E + açık eksik raporu.
```

### Tarif D — Bütçe kapısı (her kredili istekten önce)
```
[ ] kuyruk.py BUTCE.json'u okur: kalan_pay ≥ istek → devam (teknik tekrarlar kurgu_ayrilan payına yalnız KRİTİK için girer).
[ ] Değilse: öncelik sırasına göre sığanlar üretilir; kalanlar 0 kredi çözümüne düşer.
[ ] KRİTİK sığmıyorsa: hat DURUR, kullanıcıya "X kredi gerekiyor, yükleyince devam ederim" bildirimi. Kalite kısılmaz,
    plan çözünürlüğü/modeli değiştirilmez (kesin karar 6; DR: tek model Omni).
```

### Tarif E — CapCut taslağı (K10)
```
[ ] 1. python film.py <film> --asama capcut     → "YZ <FILM> v<N>" + son_capcut_projesi.json
[ ] 2. python taslak_fark.py <film> --oz-denetim  → fark 0, boşluk 0, eksik medya 0 olmalı
[ ] 3. Kullanıcıya tek mesaj: taslak adı, süre, seyirci medyanı, bilinen eksikler. Soru sorma.
       ("CapCut'ı kapatıp aç; 'YZ <FILM> v<N>' en üstte. İstersen izleyip not bırak, ya da direkt dışa aktar.")
```

### Tarif F — Kullanıcı "değiştirdim / notlarıma bak" dediğinde (K11)
```
[ ] 1. Soru = sadece cevap kuralı (BK §7.1): kullanıcı yalnız soru sorduysa dosyaya dokunma.
[ ] 2. python taslak_fark.py <film>   (salt okunur; şifreliyse kullanıcıya yedek yolu söyle, §9.4 soru 2)
[ ] 3. python notlari_oku.py <film>
[ ] 4. kurgucu: TASLAK_FARK + NOTLARIM → işlem listesi + NOT_CEVAPLARI.md; kullanıcı kararları kilitli.
[ ] 5. python kurgu_uygula.py ... --uygula  → kurgu_denetim --hepsi (Z1 kurulum, zıplama, senkron, dudak, ambiyans)
[ ] 6. §8.7 karar ağacı: yeni sürüm taslak mı, yerinde dosya değişimi mi. Kullanıcının taslağına asla yazma.
[ ] 7. Kullanıcıya: her not için bir satır "ne yaptım" (NOT_CEVAPLARI.md özeti).
```

### Tarif G — Teslim (K12)
```
[ ] yayın taslağı (NOTLAR'sız) → kullanıcı dışa aktarır (4K 24 fps) → YAYIN/<ad>.mp4 gelirse kalite_denetim.py
[ ] bölüm zamanlarını yayin-paketcisi'ne ver → ders_defteri.py --kurgu <film> (§8.5)
```

**Beceride en üste yazılacak kurgu kuralları** (sıkıştırmadan sonra ilk 5.000 token korunur, AR3 B4):
1. Animatik geçmeden video kredisi harcanmaz.
2. Kopuk taslak kullanıcıya gösterilmez: KRİTİK = 0 olmadan Tarif E çalışmaz.
3. Kullanıcının CapCut kararı aynen uygulanır, taslağına yazılmaz.
4. Her kurgu değişikliğinden sonra dudak/senkron denetimi çalışır.
5. Flow uyarısında DUR.

## 5. Veri şeması / plan alanları

### 5.1 `KURGU/KURGU_PLANI.json` (kurgunun tek kaynağı)
Her sürüm ayrıca `KURGU/surumler/KURGU_PLANI_<T>_v<N>.json` olarak saklanır ("her sürüm yeni klasöre", BK §5.3.8).
Zaman birimi saniyedir. Bütün `cizelge_bas` ve `sure` değerleri 1/24 sn'ye yuvarlanır (24 fps, UH §8).

```json
{
 "surum": 1,
 "film": "ORNEK_3_SAHNE",
 "cizelge": "T2",
 "kurgu_surumu": 4,
 "fps": 24,
 "girdi_imzasi": {"SAHNELER.json": "a1b2c3d4", "SIRALI_VIDEO": "9f8e7d6c", "SESLER/DIYALOG": "77aa01ce"},
 "planlar": [
  {
   "sira": 17, "plan": 41, "parti": 1, "sahne_grubu": "S05", "izleme_parcasi": 2,
   "plan_tipi": "eylem", "kadraj": "OG", "yogunluk": 6, "hedef_duygu": "gerilim",
   "goruntu": {
    "tur": "video",
    "dosya": "SIRALI_VIDEO/041.mp4",
    "klip_sn": 8.0,
    "kaynak_klip": null,
    "kullanim": {"bas": 0.625, "sure": 5.583},
    "kullanim_kaynak": "otomatik",
    "kullanim_kilit": null,
    "guven": 0.82,
    "gerekce": "hareket başlangıcı 0.71 sn; 2. adım 5.9 sn'de bitti; 0.3 sn tutma",
    "hiz": 1.0, "ayna": false, "kadraj_kirpma": null
   },
   "cizelge_bas": 61.375, "sure": 5.583,
   "kesme_giris": {"tip": "eylem"},
   "kesme_cikis": {"tip": "eylem", "adim": 2, "adim_orani": 0.65}
  }
 ],
 "diyalog": [
  {
   "id": "R087_0", "plan": 87, "karakter": "bram",
   "metin_plan": "They will burn the whole street.",
   "metin_duyulan": "They will burn the whole street.",
   "dosya": "SESLER/DIYALOG/R087_0.wav", "kaynak": "donusum",
   "klip_zamani": {"bas": 1.62, "bit": 3.95},
   "cizelge_bas": 412.333, "sure": 2.33,
   "gorunen_konusan": true, "ekran_disi": false,
   "jl": {"tip": "L", "tasma_sn": 1.1, "uzerindeki_plan": 88},
   "seviye": "normal", "lufs_hedef": -19.5, "lufs_olculen": -19.8
  },
  {
   "id": "R088_X", "plan": 88, "karakter": "voss",
   "metin_plan": "Then we leave tonight.", "metin_duyulan": "Then we leave tonight.",
   "dosya": "SESLER/TTS/R088_X.wav", "kaynak": "tts",
   "klip_zamani": null, "cizelge_bas": 418.0, "sure": 1.9,
   "gorunen_konusan": false, "ekran_disi": true, "jl": null,
   "seviye": "yumusak", "lufs_hedef": -21.5, "lufs_olculen": null
  }
 ],
 "ambiyans": [
  {"sahne_grubu": "S05", "dosya": "SES_KUTUPHANESI/yatak/IC_ODA_02.wav", "cizelge_bas": 60.9, "sure": 118.4,
   "capraz_gecis_sn": 0.8, "goruntuden_once_sn": 0.5, "diyalog_alti_db": 15}
 ],
 "efektler": [
  {"plan": 41, "ad": "adim_tahta", "dosya": "SES_KUTUPHANESI/efekt/adim_tahta_2.wav",
   "cizelge_bas": 62.125, "kaynak_olay": "eylem_adim_1", "zaman_kaynagi": "olculen"}
 ],
 "muzik": [
  {"ipucu": "FM04", "dosya": "MUZIK/FM04.wav", "cizelge_bas": 55.0, "sure": 92.0,
   "giris_sn": 2.0, "cikis_sn": 3.0, "tetik": "kesme@sira16", "gecici": false}
 ],
 "kartlar": [
  {"tur": "yer_zaman", "metin": "Northern Pass — Winter", "cizelge_bas": 0.8, "sure": 3.0, "ust_uste": true},
  {"tur": "baslik", "metin": "EMBERFALL", "cizelge_bas": 64.0, "sure": 4.5, "ust_uste": false}
 ],
 "olcumler": {"toplam_sn": 2412.6, "asl": 4.71, "asl_ilk120": 3.82, "asl_ilk30": 3.3,
              "jl_orani_diyalog": 0.34, "tepki_orani_diyalog": 0.27, "muzik_kaplama": 0.52}
}
```

Kurallar:
- `sure = kullanim.sure / hiz`. Çizelgede boşluk yoktur: `planlar[i+1].cizelge_bas = planlar[i].cizelge_bas + planlar[i].sure`.
  Tek istisna planlı `karartma` planıdır (`goruntu.tur: "siyah"`).
- `goruntu.tur`: `video` (T2/T3), `gorsel` (T1: durağan kare + `hareket`), `kart`, `siyah`, `yer_tutucu`
  (görsel + yavaş zoom; DR'deki filtre çözümü).
- `kullanim_kaynak`: `plan` (yönetmen, T0/T1) · `otomatik` (`kirp_oner`) · `kurgucu` · `kullanici`.
  `kullanici` olan değer hiçbir otomatik araçla değişmez.
- `kullanim_kilit`: `zincir` (K6: çıkış karesi sonraki planın başlangıcı oldu, kırpma değişirse zincir bozulur) ya da
  `kullanici`.
- **Senkron kuralı** (görünen konuşan için): `diyalog.cizelge_bas = plan.cizelge_bas + (klip_zamani.bas − kullanim.bas) / hiz`.
  Fark > 1 kare ise HATA (§8.1).
- **Senkron korumalı bölme:** Aynı klipten iki plan çıkıyorsa (`kaynak_klip`) ve replik aradaki tepki planının üstünden
  sürüyorsa: `parca2.kullanim.bas = parca1.kullanim.bas + parca1.sure + aradaki_planlarin_suresi`. Böylece konuşana
  dönüldüğünde dudak ile ses aynı anda olur. Replik sürmüyorsa ZN §2.2'deki ≥ 0,4 sn atlama kuralı geçerlidir.

### 5.2 `SAHNELER.json`'da kurgunun okuduğu alanlar
Var olan alanlar değişmez. Kurgu ZN §6.1'deki `zanaat` ve AR2 §6.1'deki `sureklilik` alanlarını okur. Plan başına
isteğe bağlı küçük bir `kurgu` nesnesi eklenir:

```json
{"no": 41, "kullanim": {"bas": 0.5, "sure": 5.5},
 "zanaat": {"plan_tipi": "eylem", "sure_sn": 5.5, "kesme": {"tip": "eylem", "nokta_sn": 5.6, "ses_tasma_sn": null}},
 "kurgu": {"vaat_imgesi": false, "ayna_yasak": true, "kirpma_onceligi": "eylem", "zincir_kaynagi": null}}
```
- `kullanim`: yönetmenin **planladığı** kırpma (CLAUDE_ICIN şemasındaki alan). Ölçülen kırpma KURGU_PLANI'na yazılır.
- `kurgu.vaat_imgesi`: kapak/başlıktaki ana imge bu planda mı (ZN §1.4: ≤ 120 sn).
- `kurgu.ayna_yasak`: süreklilik denetçisinin asimetri bilgisi (yara, tek eldiven, yazı; ZN §3.3).
- Film düzeyinde hikâye odasından iki alan gerekir:
  - `ANAHTAR_OLGULAR`: parti başına 8–12 olgu, özet eşleşmesi için. Sayı tahmin.
  - Karakter başına `etiket_anonim` (ör. `"woman in fur-lined coat"`). Ad ekranda söylenene kadar seyirci paketinde bu etiket kullanılır.

### 5.3 Seyirci çıktısı (`_RAPOR/SEYIRCI/<T>_tur<n>_P<p>_s<k>.json`)
```json
{
 "asama": "T2", "tur": 1, "parti": 1, "seyirci": 2,
 "puanlar": {"anlasilirlik": 8, "akicilik": 7, "merak": 8, "duygu": 7, "ritim": 6, "ilk30": 9, "GENEL": 7},
 "parca_puanlari": [{"parca": 1, "GENEL": 8}, {"parca": 2, "GENEL": 7}, {"parca": 3, "GENEL": 6}],
 "kopukluklar": [
  {"plan": 41, "onceki_plan": 40, "zaman": "01:01", "tur": "KRITIK",
   "neden": "Kadın kapıdaydı, sonraki karede masanın yanında; nasıl geldiğini görmedim",
   "oneri": "arada yürüdüğünü gösteren bir plan"}
 ],
 "sikilma": [{"bas": "07:40", "bit": "08:30", "neden": "aynı tartışma ikinci kez"}],
 "ilgi_egrisi": [9, 7, 7, 6, 8, 6, 5, 7, 6, 6, 7, 6, 8],
 "acik_sorular": ["Kardaki ışık neydi?", "Asker neden yalnız geldi?"],
 "ozet": "Üç cümle.",
 "karakterler": [{"ad_ya_da_tarif": "Mara", "kim": "avcı kadın"}, {"ad_ya_da_tarif": "uzun boylu asker", "kim": "bilinmiyor"}],
 "kahraman_ne_kaybedebilir": "Ejderhayı ve köydeki yerini",
 "devam": true
}
```
`ilgi_egrisi` dakika başına bir değerdir. Makine bunu duygu haritasıyla karşılaştırır (§7.2).

### 5.4 İzleme paketi (`_RAPOR/IZLEME/<T>_tur<n>_P<p>/`)
- `sayfa_NN.jpg`: Her sayfada **6 plan × 3 kare** (baş +0,15 sn / orta / son −0,15 sn; kırpılmış pencereden) bulunur.
  Kareler 400×225 boyutundadır, sol üstte zaman kodu ve plan numarası yazar. Sayfanın en üstünde önceki sayfanın son
  karesi küçük olarak durur. Ardışık planlar alt alta dizildiği için ZN §7.3'teki üçlü pencere (önceki son kare / bu
  plan / sonraki ilk kare) korunur. Satır başına 5 kare yerine 3 kare kullanılır. Sayfa boyutu ≈ 1200×1600 px.
  Claude'un w·h/750 kuralıyla ve yeniden boyutlandırma sınırıyla sayfa başına ≈ 1.600 token tutar. 165 planlık bir
  parti ≈ 28 sayfa ≈ 45 bin token eder (tahmin, ilk çalıştırmada ölçülmeli).
- Animatik modunda satır başına 1 kare (durağan görsel) ve altında **eylem şeridi** metni olur.
- `IZLE.md` satır örneği:
  ```
  ## Sayfa 03 (sayfa_03.jpg)
  - [04:12.4] #041 · 5,6 sn
    duyulan: (konuşma yok) · efekt: tahta gıcırtısı · müzik: alçak, gerilimli (sürüyor)
  - [04:18.0] #042 · 2,5 sn
    duyulan [ekranda]: KÜRK YAKALI KADIN: "Only the warden has one."
  - [04:20.5] #043 · 3,0 sn
    duyulan [ekran dışı]: KALIN SESLİ ERKEK: "Then take it from him."
  ```
- **Ad sızdırmama kuralı:** Bir karakterin adı repliklerde ya da kartta ilk kez geçtiği andan önce, seyirci paketinde
  o karakter `etiket_anonim` ile anılır. O andan sonra adıyla anılır. Paketlerde `amac`, `duygu`, `risk`, `vurus`,
  `merak_*`, `plan_tipi`, `kadraj` **bulunmaz**.
- Paket parçalara bölünür: `izleme_parcasi` ≈ 240–300 sn, sahne sınırından (BK §3.8, H/kurgu-izleme-denetimi).
  Seyirci partiyi tek oturumda izler, puanı **parça başına** ve parti için verir. Bu, B2'de kanıtlanan 4–5 dk birimini
  korur, parti içinde de akışı bozmaz.
- `ONCEKI_OZET.md` (P2/P3): önceki partinin geçen turundaki 3 seyirci özetinden, özet eşleşmesi medyana en yakın olanı.
  Bu özet seyirciden gelir, hikâye belgesi değildir.
- İlk 120 paketi: yalnız 0–120 sn. Soru: "Devam eder miydin? evet/hayır + neden".

### 5.5 Yeniden çekim kuyruğu ve bütçe

**0 kredi merdiveni** (kurgucu her kopuklukta yukarıdan aşağı dener):

| # | Çözüm | Ne zaman | Koşul |
|---|---|---|---|
| 1 | Kırp / uzat | ölü süre, geç giriş, uzun plan, eylem görünmedi | klibin güvenli penceresi 0,5–(klip_sn−0,5) içinde (ZN §2.2) |
| 2 | Sahne içi sıra | konum planı geç, bakış → ekleme sırası | 180° ve kurulum yeniden denetlenir |
| 3 | J/L, ekran dışı replik | "kim konuşuyor", konuşma kopuk | üstüne binilen planda ağız kapalı (B9) |
| 4 | Alternatif çekim | çekimde kusur var | `ALTERNATIFLER/` içinde V1/V2'den geçen başka sonuç varsa |
| 5 | Mevcut klipten bölme | tepki ya da ekleme eksik | aynı sahnenin kullanılmayan klip penceresi |
| 6 | Ayna | 180° ya da bakış ters | `kurgu.ayna_yasak = false` |
| 7 | Yeniden kadraj | ölçek sıçraması | dijital yakınlaştırma ≤ %10 (tahmin; 720p kaynakta kalite kaybı, kesin karar 6) |
| 8 | Hız | eylem uzun | 0,90–1,15× (tahmin), yalnız diyalogsuz plan |
| 9 | Kart / efekt ipucu | "nerede", "nereden geldi" | yer kartı ya da önceden duyulan efekt (kapı gıcırtısı) |
| 10 | Planı kes | bilgi taşımayan plan | `--kesme-simule` yeni HATA göstermiyorsa |
| 11 | Yer tutucu (görsel + yavaş zoom) | filtre reddi (DR: bebek yüzü) | ilk 120 sn, parti sonu ve dorukta kullanılmaz (tahmin) |
| K1 | **Yeniden çekim** (aynı plan, CORRECTION) | kusur görüntünün içinde | bütçe kapısı |
| K2 | **Bağlayıcı yeni plan** | hikâye adımı ekranda yok | yönetmen yazar, G1'den geçer; `--onayli` modda kullanıcıya sorulur |

**`<FILM>/BUTCE.json`** (plan sayısından otomatik hesaplanır, kullanıcıya sorulmaz):
```json
{
 "kredi_klip": 12,
 "temel_klip": 405,
 "temel_kredi": 4860,
 "yeniden_deneme_payi_oran": 0.20,
 "yeniden_deneme_payi": 972,
 "kurgu_ayrilan_oran": 0.40,
 "kurgu_ayrilan": 389,
 "harcanan": {"video_ilk": 4704, "teknik_tekrar": 312, "kurgu_tekrar": 96},
 "kalan_pay": 564,
 "plan_basi_kurgu_tekrar_max": 2
}
```
- `kredi_klip` ve %20 pay RE `kredi_klip_720p`, `kredi_yeniden_deneme_payi` değerleridir. 405 klip ZN §2.6'dan alındı.
- `kurgu_ayrilan_oran` 0,40 (= temel kredinin %8'i) tahmindir. Teknik tekrarlar (G1/V1/V2) bu ayrılmış payın altına
  ancak KRİTİK için inebilir.
- `plan_basi_kurgu_tekrar_max` 2 tahmindir. Aşılırsa çözüm plan değişikliğine (K2) ya da kurguya döner.

**`YENIDEN_URET.json` maddesi** (bütün kapılar aynı kuyruğa yazar; `kaynak_kapi` ayırır):
```json
{
 "id": "YU-T2-1-007", "plan": 41, "kaynak_kapi": "KI", "tur": "video",
 "seviye": "KRITIK", "seyirci_sayisi": 2, "konum_agirligi": 1.5, "oncelik": 6.75,
 "cozum": "yeniden_cek",
 "duzeltme": "CORRECTION: she walks from the doorway to the table in this shot; lantern stays in her RIGHT hand",
 "plan_metni_sahibi": "yonetmen", "zincir_etkisi": [42],
 "kredi_tahmini": 24, "deneme": 1, "deneme_max": 2,
 "durum": "bekliyor", "tur_no": 1
}
```
- `kaynak_kapi`: `G1`, `V1`, `V2`, `K1`, `Z3`, `KI` (kurgu izleme), `NOT` (kullanıcı).
- `oncelik = seviye_puanı × konum_agirligi × (1 + 0,5 × (seyirci_sayisi − 1))`.
  - Seviye puanı: KRİTİK 3, ORTA 2. KÜÇÜK kuyruğa girmez.
  - `konum_agirligi`: ilk 120 sn, parti sonunun son 30 sn'si, doruk sahnesi ya da vaat imgesi için 1,5; diğerleri 1,0.
  - Formül ve katsayılar tahmindir.
- Sıra: önce bütün KRİTİK'ler, sonra ORTA'lar `oncelik / kredi_tahmini` büyükten küçüğe.
- `zincir_etkisi`: K6 zinciri yüzünden yeniden çekilmesi gereken sonraki planlar. Maliyete eklenir.

### 5.6 `KURGU_KARARLARI_<T>_tur<n>.json` (kurgucunun işlem listesi)
```json
{
 "asama": "T2", "tur": 1,
 "islemler": [
  {"op": "kirp", "plan": 41, "bas": 0.9, "sure": 5.1, "kok_neden": "olu_sure", "bulgu": "s2:k3"},
  {"op": "jl", "diyalog": "R087_0", "tip": "L", "tasma_sn": 1.2, "kok_neden": "diyalog_kopuk", "bulgu": "s1:k5"},
  {"op": "sira", "sahne_grubu": "S05", "yeni_sira": [44, 43, 45], "kok_neden": "konum_plani_gec", "bulgu": "Z0#konum"},
  {"op": "ekran_disi", "diyalog": "R090_1", "uzerine_plan": 91, "kok_neden": "konusan_belirsiz", "bulgu": "s3:k2"},
  {"op": "kes", "plan": 63, "kok_neden": "bilgisiz_uzun", "bulgu": "kesici:4"},
  {"op": "kart", "kart_tur": "yer_zaman", "metin": "The Warden's House", "plan": 40, "kok_neden": "mekan_belirsiz", "bulgu": "s1:k1"},
  {"op": "yeniden_cek", "plan": 52, "istek": "nesne sağ elde kalmalı", "kok_neden": "nesne_zipladi", "bulgu": "s1:k4,s2:k1"},
  {"op": "yeni_plan_iste", "araya": [40, 41], "gereksinim": "Mara kapıdan masaya yürür; OG; soldan sağa; 3 sn; sessiz",
   "kok_neden": "hikaye_adimi_ekranda_yok", "bulgu": "s1:k1,s2:k1,s3:k2"}
 ]
}
```
**Kök neden sözlüğü ve sahibi.** Ders defteri bu sözlükle sayım yapar.
- Kurgu: `olu_sure`, `gec_giris`, `uzun_plan`, `bilgisiz_uzun`, `ritim_tekduze`, `diyalog_kopuk`, `konusan_belirsiz`,
  `senkron_kaydi`, `dudak_ustune_replik`, `muzik_yanlis_yer`
- Yönetmen: `konum_plani_gec`, `mekan_belirsiz`, `olcek_sicramasi`, `eksen_180`, `bakis`, `ekran_yonu`, `hikaye_adimi_ekranda_yok`
- Süreklilik: `nesne_zipladi`, `karakter_kayboldu`, `yuz_degisti`, `isik_zipladi`
- Ses: `ambiyans_zipladi`, `seviye_zipladi`
- Hikâye: `kurulum_yok`, `ad_gec`, `risk_belirsiz`, `duygu_hak_edilmedi`

### 5.7 `TASLAK_FARK.json` ve not cevapları
```json
{
 "taslak": "YZ ORNEK_3_SAHNE v3", "okuma": "salt_okunur", "sifreli": false,
 "klipler": [
  {"plan": 41, "degisim": "kirpildi", "eski": {"bas": 0.625, "sure": 5.583}, "yeni": {"bas": 1.1, "sure": 4.2}},
  {"plan": 63, "degisim": "silindi"},
  {"plan": 70, "degisim": "tasindi", "eski_sira": 52, "yeni_sira": 47}
 ],
 "bosluklar": [{"bas": 241.2, "sure": 0.8}],
 "kayan_kanallar": ["Diyalog", "Ambiyans"],
 "kullanici_yazilari": 3,
 "geri_uretilemeyen": ["renk ayarı: segment 20-31", "Muzik kanalı -3 dB"]
}
```
`geri_uretilemeyen`, kullanıcının taslakta yaptığı ve bizim kurulumumuzun yeniden üretemeyeceği işlerdir. Bu liste §8.7
karar ağacını belirler. `NOT_CEVAPLARI.md` her not için bir satır tutar: `[zaman] #plan · NOT: … → YAPILAN: … (işlem id)`.

### 5.8 Kapı raporu biçimi (ZN §6.2 ile aynı)
`_RAPOR/ZAMAN_<T>.json`, `_RAPOR/Z3_v<N>.json`:
`{"kapi": "Z0Z2", "cizelge": "T1", "sonuc": "BAYRAK", "hatalar": [{"madde": 7, "sira": null, "zaman": "0:00-0:30", "olcu": 3.9, "esik": 3.5, "sonuc": "B", "oneri": "ilk 30 sn'de ASL yüksek; #003'ü 1,2 sn kısalt"}]}`.
Klasör olarak mevcut kodun kullandığı `_RAPOR/` önerilir (ZN `RAPORLAR/` diyor; bkz. §9.3 D6).

### 5.9 `SEYIRCI_KARAR_<T>_tur<n>.json` (`puan_oku.py` çıktısı)
```json
{
 "asama": "T1", "tur": 2,
 "partiler": {
  "P1": {"medyan": {"anlasilirlik": 8, "akicilik": 8, "merak": 8, "duygu": 7, "ritim": 7, "ilk30": 9, "GENEL": 8},
         "kritik": 0, "kritik_gecersiz_sayilan": [], "orta": 2,
         "ozet_eslesme": [0.83, 0.91, 0.75], "ozet_eslesme_medyan": 0.83,
         "ilgi_korelasyon": 0.58, "ortak_sikilma": [["07:40", "08:30"]], "gecti": true}
 },
 "ilk120": {"evet": 3, "gecti": true},
 "karar": "GECTI"
}
```
**KRİTİK sayımı:** Aynı plan (±1) için verilen KRİTİK'ler birleştirilir.
- İki ya da daha çok seyircinin verdiği KRİTİK geçersiz sayılamaz.
- Tek seyircinin KRİTİK'ini kurgucu yalnız kare kanıtıyla, yazılı gerekçeyle geçersiz sayabilir. Bu geçersiz saymalar
  kullanıcıya giden raporda listelenir.
- Bu kuralın amacı "tek seyircinin KRİTİK'i boşa yorulmasın" ile "hiçbir KRİTİK halı altına süpürülmesin" arasında denge kurmaktır.

## 6. Yazılması/değişmesi gereken kod

Öncelik: **P0** = ilk film kurgu kapılarından geçemez · **P1** = kaliteyi artırır, geçici yolu var · **P2** = sonra.
Bütün araçlar mevcut stilde yazılır: başta Türkçe kullanım metni, `sys.stdout.reconfigure`, `_RAPOR/` raporu,
çıkış kodu 0 / 1 / 2, `--saglayici sahte` ile ağsız çalışma.

| Araç | Durum | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|---|
| `zaman_cizelgesi.py` | yeni | T0/T1/T2/T3 çizelgesini kurar. Olay listesini (ad, risk, merak, kurulum saniyeleri) çıkarır, zamana bağlı ölçüleri hesaplar, eğri grafiği çizer. Diğer kapıların ortak kütüphanesidir. | SAHNELER.json, replik_olcum, KURGU_PLANI → `KURGU_PLANI_<T>.json`, `_RAPOR/ZAMAN_<T>.json`, `OLAYLAR_<T>.json`, `EGRI_<T>.png`, `SAPMA_<T>.json` | P0 |
| `kurgu_render.py` (`animatik.py` bunu `--animatik` ile çağırır) | yeni | Herhangi bir KURGU_PLANI'ndan izlenebilir mp4 üretir: durağan kare + Ken Burns + eylem şeridi (animatik) ya da kırpılmış klip (önizleme). Ses katmanları, J/L, ambiyans çapraz geçişi, müzik girişi/çıkışı ve kısma (ducking), −14 LUFS. Plan başına önbellek tutar, yalnız değişen plan yeniden işlenir. | KURGU_PLANI + medya → `ANIMATIK/animatik_v<N>[_P<p>].mp4`, `KURGU/onizleme_v<N>[_P<p>].mp4`, katman WAV'ları | P0 |
| `izleme_paketi.py` | değişir | Tam klip yerine kırpılmış pencereden kare alır. 6 plan × 3 kare sayfa kurar, ad sızdırmaz, duyulanları yazar (ekranda/ekran dışı, efekt, müzik), parça/parti/ilk120 paketleri üretir. `ONCEKI_OZET`'i seçer, kesici için `KESME_DOKUMU.md` yazar. Animatik modunu destekler. | KURGU_PLANI, medya, seyirci özetleri → `_RAPOR/IZLEME/<T>_tur<n>_P<p>/` | P0 |
| `puan_oku.py` | değişir | 3 seyircinin **medyanını** alır, 6 ölçüt okur. KRİTİK'leri birleştirir, ORTA'ları sayar, özet eşleşmesini, ilgi korelasyonunu, ortak sıkılmayı ve ilk 120 sn kararını hesaplar. Eski OZET biçimini de okur (kâğıt modu bozulmaz). | seyirci JSON + eşleştirici JSON → `SEYIRCI_KARAR_<T>_tur<n>.json`; çıkış 0 geçti · 3 geçmedi · 1 eksik | P0 |
| `kirp_oner.py` | yeni | Klipten `kullanim` önerir (algoritma aşağıda). `--zincir` modunda K6 çıkış karesini çıkarır. | klip, plan, whisper kelimeleri, V1/V2 kusur anları → KURGU_PLANI `goruntu.kullanim` + `guven` + `gerekce`; `KIRP_INCELE.md` (güveni düşükler) | P0 |
| `plan_kurgu.py` | yeni (belgede var, pakette yok) | T2 kaba kurguyu kurar: kırpma, senkron kuralıyla diyalog, ekran dışı replikler, J/L, sahne ambiyansı, efektlerin ölçülen eylem anına yerleşmesi, müziğin olay anına bağlanması, kartlar. | SAHNELER, videolar, SESLER, ses planı, müzik listesi → `KURGU_PLANI_T2_v<N>.json` | P0 |
| `kurgu_uygula.py` | yeni | Kurgucunun işlem listesini (§5.6) doğrulayıp uygular. `--kuru` önce denetimi koşar, kilitli alanlara dokunmaz. `yeniden_cek` işlemlerini kuyruğa, `yeni_plan_iste` işlemlerini `YENIDEN_YAZ.json`'a aktarır. | KURGU_KARARLARI + KURGU_PLANI → yeni KURGU_PLANI sürümü + fark raporu | P0 |
| `kurgu_denetim.py` | yeni | Z3 #41–47'yi, senkron kuralını, B9'u (ağız oynarken başkasının repliği), boşluğu ve geri gidişi denetler. Komşuluğa bağlı Z0 maddelerini (#11, 12, 16, 17, 18) KURGU_PLANI sırasıyla yeniden koşar. `--kesme-simule` ve `--hepsi` modları vardır. `dudak_denetim.py` ve süreklilik K1 sonuçlarını okur. | KURGU_PLANI + render + katmanlar → `_RAPOR/Z3_v<N>.json` | P0 |
| `kuyruk.py` | yeni | Bütün kapıların yeniden üretim maddelerini birleştirir, tekrarları ayıklar. Önceliği, zincir etkisini ve maliyeti hesaplar, bütçeyi denetler. `URETIM_ONIZLEME.md` yazar. Eski klibi `SIRALI_VIDEO/_ESKI/NNN_t<k>.mp4`'e **taşır** (silmez, BK §6.5.4). | kapı raporları, KURGU_KARARLARI, BUTCE → `YENIDEN_URET.json`, `URETIM_ONIZLEME.md`, güncel BUTCE | P0 |
| `capcut_film.py` | değişir | KURGU_PLANI'ndan taslak kurar. `source_timerange` = `kullanim` olur. Diyalog J/L ile, ambiyans sahne başına, efekt, müzik ayrı ve kapatılabilir; kartlar, altyazı ve NOTLAR (sıra, plan, amaç, duygu, hedef yoğunluk) eklenir. Taslaklar sürümlüdür, `--yayin` modunda NOTLAR yoktur. Segment ↔ plan eşlemesi `son_capcut_projesi.json`'a yazılır. | KURGU_PLANI → CapCut taslağı + eşleme | P0 |
| `film.py` | değişir | Yeni aşamalar ve döngü kapıları (§2.3), zincir dalgalarıyla video üretimi (§8.4), çıkış kodu **4 = ajan işi bekleniyor** (`_RAPOR/AJAN_ISLERI.json`). Durumda tur, parti sonucu ve harcanan kredi tutulur, `--durum --kurgu` özeti verilir. | — | P0 |
| `saglayicilar/sahte.py` | değişir | Sahte videoda `eylem_zinciri` zamanlarında hareket eden bir kutu, `replik_zaman` penceresinde ton üretir. Böylece kirp_oner, senkron ve render ağsız test edilebilir. Sahte seyirci (sabit tohumlu JSON) ve sahte CapCut taslağı fikstürü eklenir. | — | P0 |
| `testler/test_kurgu.py` | yeni | Aşağıdaki test listesi. | ORNEK_3_SAHNE (+ zanaat alanlı 12 planlık `ORNEK_12_PLAN` önerisi) | P0 |
| `taslak_fark.py` | yeni (belgede var, pakette yok) | CapCut taslağını salt okunur inceler: `draft_content.json` + `Timelines/` kopyası, birleşik klip içi. Kırpılan, silinen, taşınan, eklenen klipleri, boşlukları, kayan kanalları ve geri üretilemeyen değişiklikleri bulur. Şifreli taslağı tanıyıp durur. `--uygula` kullanıcı işlemlerini kilitli olarak kurgu_uygula'ya verir, `--oz-denetim` yeni taslak ↔ plan farkının 0 olduğunu denetler. | taslak + son_capcut_projesi + KURGU_PLANI → `TASLAK_FARK.json` | P1 (ilk taslaktan önce hazır olmalı) |
| `notlari_oku.py` | değişir | Notu sahneye `NNN.mp4` adıyla değil `son_capcut_projesi.json` segment eşlemesiyle bağlar. Aynı klipten iki plan çıktığında da doğru planı bulur. Çıktıya sıra ve plan no eklenir. | — | P1 |
| `seyirci_api.py` | yeni | API modu: aynı ajan gövdesi + sayfalar doğrudan Claude API'ye gider (`claude-opus-5-5`). 3 bağımsız çağrı yapar, JSON'u doğrular, maliyeti raporlar. | paket → seyirci JSON | P1 |
| `ders_defteri.py --kurgu` | yeni (ders defteri sahibiyle ortak) | Kök neden sayımlarını, işe yarayan/yaramayan düzeltmeleri, ölçü ↔ puan ilişkisini ve karakter başına konuşma hızını deftere yazar (§8.5). | KURGU_KARARLARI, SEYIRCI_KARAR, SAPMA → `DERS_DEFTERI.json` | P1 |
| OTIO dışa aktarma (`kurgu_render.py --otio`) | yeni | CapCut'a yedek: DaVinci/Premiere için `.otio` (AR1 D, Apache-2.0). | KURGU_PLANI → `.otio` | P2 |

### 6.1 Ana algoritmalar

**`kirp_oner.py`**. Eşikler kalibre edilene kadar tahmindir.
1. **Hareket enerjisi:** klip 24 fps, 160×90 gri. `E(t) = ort|f(t) − f(t−1)|`, 0,25 sn medyanla düzleştirilir.
   - Taban, ilk 0,5 sn'nin medyanıdır (Flow klibi durağan başlar, ZN §2.2).
   - Başlangıç: `E > taban + 3·MAD` koşulunun ≥ 0,2 sn sürdüğü ilk an. Bitiş: koşulun son sağlandığı an.
2. **Güvenli pencere:** `[0,5 ; klip_sn − 0,5]` aralığı şunlarla kesiştirilir:
   - ilk V1/V2 kusurundan 0,1 sn öncesi,
   - klip içi kesmeden (PySceneDetect) önceki bölüm (ZN §2.2 d).
3. **Plan tipine göre kırpma:**
   - `diyalog`: kelimeler whisper ile **planın kendi replik penceresinde ±1 sn** aranır (DR, H/proje-b2).
     `bas = ilk_kelime − 0,4`. Çıkış L değilse `son = son_kelime + 0,3`; L ise kesme L taşması kadar öne alınır.
   - `eylem`/`aksiyon`: `bas = hareket_başı − 0,1` (geç gir). Plan adımları ölçülen `[baş, bitiş]` aralığına doğrusal
     eşlenir. Çıkış `eylem` kesmesiyse son adımın %60–70'inde, değilse son adım + 0,5 sn tutma noktasındadır (ZN §3.4, §3.7).
   - `tepki`: 1,5–4 sn'lik pencere mikro hareketin tepesini ortalar. Ağız hareketi varsa BAYRAK (ekran dışı replik konamaz).
   - `kurulus`/`gecis`: hareketi en düzgün (sarsıntısı en az) pencere seçilir; süre tipin hedefidir.
4. Ölü süre (hareket ya da replik bittikten sonra ≤ 0,6 sn) ve plan tipi aralığı denetlenir.
5. `guven`: bütün işaretler tutarlıysa 1. Hareket başlangıcı bulunamazsa, duyulan kelime planlananın %70'inin altındaysa
   ya da kusur pencereyi daraltıyorsa düşer. < 0,6 ise kurgucu bakar (tahmin).
6. `--zincir`: çıkış noktası, son adımdan sonraki tutma aralığında E'nin en düşük olduğu karedir. Bu kare sonraki planın
   başlangıç karesi olur.

**`zaman_cizelgesi.py` eğri ölçüleri**
- Plan yoğunluğu saniye dizisine açılır: `y(t)`, `tür(t)`.
- Hedef eğri film süresine oranla gerilir: `hedef(t) = harita[⌊t · 2400 / L / 60⌋]` (RE `duygu_haritasi_40dk`, "oranla gerilir").
- Ölçüler:
  - Sapma: `|y − hedef| > 2` olan kesintisiz bölüm > 60 sn ise B.
  - 3 dk pencerede tepe: 10 sn adımla kayan 180 sn pencerede `max y ≥ 6`.
  - Düz çizgi: tür aynı ve `max − min ≤ 2` olan bölüm > 180 sn ise B.
  - Tepe öncesi çukur: tepe ≥ 8 ise (ilk 30 sn hariç) `[t−120, t−60]` aralığında `min ≤ tepe − 2`.
  - Kademe: `ASL[t−30, t] ≤ 0,75 · ASL[t−90, t−30]`. Tepeden sonraki 20 sn içinde ≥ 5 sn'lik bir plan olmalı
    (20 sn tahmin; ZN "tepeden sonra" pencere vermiyor).
  - Dakika başına baskın tür üç dakika üst üste aynıysa B.
- Komşuluğa bağlı ölçüler (aynı tip art arda ≤ 4, ölçek sıçraması, durum zinciri, 180°, bakış) KURGU_PLANI **sırasıyla**
  yeniden hesaplanır. Kesme ve sıra değişikliği yeni komşular yaratır.

**`kurgu_render.py`**
- Görüntü: her plan ayrı parça olarak işlenir ve önbelleğe girer (`KURGU/_onbellek/seg_<özet>.mp4`, girdisi değişmeyen
  parça yeniden kodlanmaz). Sonra concat ile birleştirilir.
  - Durağan karede `zoompan` kullanılır: `yavas_ileri` %8 yakınlaşma, `yavas_geri` %8 uzaklaşma, `yavas_pan` %2–4 yatay,
    `sabit` %2 "nefes". Oranlar kurgu köprüsü V5 varsayılanlarından alındı (KULLANIM.txt: %8 zoom, %2 kayma).
  - Yazılar (eylem şeridi, kartlar) PIL ile şeffaf PNG olarak çizilip bindirilir. Windows'ta `drawtext` font yolu sorunu
    yaşanmaz.
- Ses: dört katman numpy'da 48 kHz'te kurulur.
  - Diyalog: replik başına seviye eşitleme.
  - Ambiyans: sahne başına tek dosya, döngü + 0,5–1,0 sn çapraz geçiş, görüntüden 0,3–1,0 sn önce girer.
  - Efekt.
  - Müzik: giriş 1–3 sn, çıkış 2–4 sn. Diyalog varken zarf ile en az 12 dB kısılır.
  - Son karışım ffmpeg `loudnorm` çift geçişle −14 LUFS / −1 dBTP'ye çekilir (AR3 A3, ZN §5).

**`film.py` ↔ ajan köprüsü**
`film.py` ajan başlatamaz. Ajan gerektiren aşamada paketi hazırlar, `_RAPOR/AJAN_ISLERI.json` dosyasına
`[{"ajan": "kurgu-seyircisi", "paket": "...", "cikti": "..."}]` yazar ve **4** koduyla çıkar. Beceri bu listeyi
yürütür ve `film.py`'yi yeniden çağırır. `film.py` çıktıları bulunca (puan_oku) devam eder. API modunda `film.py`,
`seyirci_api.py` ile bu işi kendisi yapar.

### 6.2 Testler (`test_kurgu.py`, ağ ve kredi yok)
1. T0 çizelgesi: toplam süre, ASL, J/L oranı, eğri sapması sentetik plana göre beklenen değeri verir.
2. Animatik render süresi = T1 toplamı ±0,1 sn. Eylem şeridi yalnız `eylem_zinciri`'nden gelir: pakette `amac` metni geçmez.
3. Sahte videoda (hareketli kutu) `kirp_oner` hareket başlangıcını ±2 kare bulur. Kırpılmış önizleme süresi = Σ kullanim.
4. Senkron kuralı: bölünmüş klipte replik tepki planının üstünden sürerken 2. parçanın `bas` değeri doğru hesaplanır. Kaydırılmış diyalog HATA verir.
5. Ad sızdırmama: ad ilk replikten önce IZLE.md'de geçmez.
6. `puan_oku`: {6, 8, 9} → medyan 8. İki seyircinin KRİTİK'i geçersiz sayılamaz. Eski OZET satırı da okunur.
7. `kuyruk`: bütçe yetmeyince ORTA maddeler `sifir_krediye_dustu` olur. KRİTİK sığmayınca çıkış 2 (durdu). Zincir etkisi maliyete eklenir.
8. `taslak_fark`: fikstür taslakta kırpma, silme ve taşıma bulunur. Kullanıcı kırpması kilitlenir, sonraki `kirp_oner` ona dokunmaz.
9. `film.py`: animatik geçmeden `video` aşaması başlamaz (kesin karar 6'nın testi).

**Kurulum eklentileri (KURULUM.bat):** `pyloudnorm` (MIT), `stable-ts` (MIT), `scenedetect` (BSD-3), `opencv-python`
(Apache-2.0). MediaPipe sürümü için §9.3 D12'ye bakın.

## 7. Makinenin denetleyeceği eşikler

### 7.1 ZANAAT eşikleri hangi aşamada, nasıl ölçülür
İşaretler: **●** bu çizelgede ölçülür · **↻** yalnız kesme/sıra değişikliğinden sonra yeniden ölçülür · **—** yok.
T0 = kâğıt, T1 = animatik, T2 = kaba kurgu, T3 = kullanıcının CapCut düzenlemesi (§2.1).
**T3 kuralı:** Kullanıcı kararı aynen uygulanır. Kullanıcının kendi kırpması ya da sırası yüzünden doğan HATA,
BAYRAK'a döner ve öneriyle bildirilir. Kullanıcının kararı geri alınmaz.

| ZN # | Ölçü | Eşik (RE anahtarı) | T0 | T1 | T2 | T3 | Nasıl ölçülür | Sonuç |
|---|---|---|---|---|---|---|---|---|
| 1 | Toplam süre (kart + jenerik dahil) | 1800–2700 sn (`film_sure_aralik_sn`) | ● | ● | ● | ● | T0 Σ`sure_sn`; T1 TTS ile; T2 Σ`kullanim.sure/hiz`; T3 taslaktan | H |
| 2 | Parti süresi / film | 0,30–0,35 (`parti_sure_oran_aralik`) | ● | ● | ● | ● | parti sınırı çizelge zamanı | B |
| 3 | Vuruş zamanı | oran ±0,04 (`vurus_oranlari`, `vurus_oran_tolerans`) | ● | ● | ● | ● | `vurus` alanlı planın `cizelge_bas / toplam` değeri | B |
| 4 | Plan süresi / tip | `plan_sure_aralik_sn` | ● | ● (diyalog) | ● | ● | T2'de ölçülen kırpma | H (T3'te B) |
| 5 | Diyalog süresi ≥ formül | ZN §2.3 | ● formül | ● TTS | ● whisper | ↻ | `0,4 + replik + 0,25·(cümle−1) + 0,5` | H |
| 7 | ASL film / parti / ilk 120 / ilk 30 | 4,2–5,2 / ±0,6 / ≤ 4,0 / ≤ 3,5 (`asl_*`) | ● | ● | ● | ● | yalnız plan süreleri (kartlar hariç) | B |
| 8 | Sahne süresi | ≤ 180 sn (`sahne_max_sn`) | ● | ● | ● | ● | `sahne_grubu` toplamı | H |
| 9 | Diyalog sahnesinde tepki oranı | ≥ 0,25 (`tepki_orani_min`) | ● | ↻ | ↻ | ↻ | `sahne_tipi: diyalog` içindeki `tepki` planlarının oranı | B |
| 10 | Diyalog sahnesinde J/L oranı | ≥ 0,30 (`jl_kesme_orani_min`) | ● plan | ● gerçek | ● gerçek | ● | J ya da L ile geçilen plan sınırı sayısı / diyalog sahnesindeki plan sınırı sayısı | B |
| 11 | Aynı plan tipi art arda | ≤ 4 (`ayni_plan_tipi_ardisik_max`) | ● | ↻ | ↻ | ↻ | KURGU_PLANI sırasıyla (diyalog↔tepki dönüşümü hariç) | B |
| 12 | Ölçek sıçraması | ≥ 2 kademe ya da ≥ 30° (`olcek_kademe_min_fark`, `aci_min_fark_derece`) | ● | ↻ | ↻ | ↻ | yeni komşu çiftler | H (T3'te B) |
| 16–18 | Durum zinciri, 180°, bakış | ZN §6.2 | ● | ↻ | ↻ | ↻ | kesme/sıra sonrası süreklilik denetçisinin kâğıt kuralları KURGU_PLANI sırasıyla yeniden koşar | H (T3'te B) |
| 21 | İlk eylem / ilk merak sorusu | ≤ 5 sn / ≤ 20 sn (`ilk_eylem_max_sn`, `ilk_merak_max_sn`) | ● | ● | ● ölçülen hareket başlangıcı | ● | T2'de `kirp_oner` hareket başlangıcı + çizelge zamanı | H |
| 22 | Başlık kartı | 45–120 sn, ≤ 6 sn (`baslik_karti_*`) | ● | ● | ● | ● | `kartlar` | B |
| 23 | Ana karakter adı | ≤ 120 sn (`kahraman_adi_max_sn`) | ● | ● | ● `metin_duyulan` | ↻ | olay listesi: adın geçtiği replik zamanı | H |
| 24 | Riskin sözle söylenmesi; parti başında tazelenmesi | ≤ 180 sn; ≤ 60 sn (`risk_sozlu_max_sn`, `parti_basi_risk_tazeleme_max_sn`) | ● | ● | ● | ↻ | `vurus: risk_sozlu` ya da risk işaretli replik zamanı | H |
| 25–28 | Merak olay aralığı, açık soru sayısı, soru ömrü, parti sonu sorusu | ZN §4.3 (`merak_*`, `acik_soru_aralik`, `soru_omru_max_sn`) | ● | ● | ● | ↻ | `merak_ac/kapat` olaylarının saniyeleri | B / H(#28) |
| 29–32 | Kurulum → kullanım | ≥ 20 sn; > 600 sn'de hatırlatma (`kurulum_kullanim_min_sn`, `hatirlatma_esigi_sn`) | ● | ↻ | ↻ | ↻ | her kesmeden sonra yeniden (DR: "kullanıcının kestiği plan bilgiyi götürür") | H |
| §1.4 | İlk 30 sn manzara; vaat imgesi; parti başı kanca dönüşü; seri kancası; jenerik | ≤ 1 plan ve ≤ 3 sn; ≤ 120 sn; ≤ 20 sn; ≤ 20 sn; ≤ 60 sn | ● | ● | ● | ● | `plan_tipi`, `kurgu.vaat_imgesi`, `kartlar` | B |
| 35–39 | Duygu eğrisi: sapma, 3 dk tepe, düz çizgi, çukur, parti sonu / doruk / en karanlık | ±2 ve 60 sn; ≥ 6; ≤ 180 sn; ≥ 2 puan; ≥ 8 / ≥ 9 / ≥ 6 (`yogunluk_*`, `pencere_*`, `duz_cizgi_max_sn`, `tepe_oncesi_*`, `*_yogunluk_min`) | ● | ● | ● | ● | §6.1 eğri ölçüleri; süreler değiştikçe eğri kayar | B / H(#39) |
| 2.5.2 | Kademe | tepeye giden 30 sn'de ASL ≥ %25 düşüş (`tepe_oncesi_asl_dusus_min`) | ● | ● | ● | ● | §6.1 | B |
| 40 | Müzik kaplama; müziksiz / müzikli en uzun blok | %40–65; ≤ 240 / ≤ 300 sn (`muzik_*`) | — | ● | ● | ● | `muzik` girdileri | B |
| 41–42 | `kullanim.bas`; `bas+sure` | ≥ 0,3; ≤ klip_sn − 0,5 (`kullanim_*`) | ● plan | — | ● | ● | | B |
| 43 | Ölü süre | ≤ 0,6 sn (`olu_sure_max_sn`) | — | — | ● | ● | son kelime / hareket bitişi → kesme | B |
| 44 | Replik seviyesi | hedef ±1 LU (`diyalog_lufs`, `diyalog_lufs_tolerans`) | — | ● TTS | ● | — | pyloudnorm, 0,4 sn'den kısa replikte komşu kazancı (AR3 A3) | H |
| 45 | Sahne içi ambiyans farkı; ambiyans boşluğu | ≤ 3 LU; 0 (`ambiyans_sahne_ici_fark_max_lu`) | — | ● | ● | ● | ambiyans katmanı | H |
| 46 | Diyalog altında müzik | ≥ 12 dB aşağı (`muzik_diyalog_alti_min_db`) | — | ● | ● | ● | diyalog pencerelerinde kısa dönem ses yüksekliği farkı | H |
| 47 | Son karışım; gerçek tepe | −14 ±1 LUFS; ≤ −1 dBTP (`final_lufs*`, `true_peak_max_dbtp`) | — | ● render | ● render | ● dışa aktarılan mp4 | ffmpeg `ebur128` | H |
| 49 | Kurgu izleme (habersiz seyirci) | ZN §7.3 | — | ● animatik | ● kurgu | ↻ büyük değişiklikte | §7.2 | H |
| — | Senkron (görünen konuşan) | ≤ 1 kare | — | — | ● | ● | §5.1 formülü | H |
| — | Ağız oynarken başkasının repliği | 0 | — | — | ● | ● | `dudak_denetim` ağız hareketi dizisi × J/L/ekran dışı aralıkları | H |
| — | CapCut boşluğu, eksik medya | 0 | — | — | — | ● | `taslak_fark` | H |
| — | Geri gidiş | Tk'de geçen ölçü Tk+1'de HATA olamaz | — | ● | ● | ● | ZAMAN raporları karşılaştırılır | H |

### 7.2 Seyirciden gelen ölçüler (T1 ve T2)

| Ölçü | Eşik | Kaynak |
|---|---|---|
| Seyirci sayısı, birleştirme | 3, medyan | RE `seyirci_sayisi`, `seyirci_karar` |
| GENEL medyan; hiçbir ölçüt medyanı | ≥ 8; ≥ 7 | RE `seyirci_genel_esik`, `seyirci_olcut_min` |
| Ölçüt hedefleri | anlaşılırlık 8, akıcılık 8, merak 8, duygu 7, ritim 7, ilk30 8 | RE `seyirci_olcut_hedef` |
| KRİTİK / ORTA (parti başına) | 0 / ≤ 3 | RE `kopukluk_kritik_max`, `kopukluk_orta_max_parti` |
| Özet eşleşmesi | ≥ %80 (kısmen = 0,5 sayılır, tahmin) | RE `ozet_eslesme_min` |
| Ortak sıkılma → kesme turu | ≥ 2 seyirci | RE `sikilma_ortak_isaret_min` |
| İlk 2 dk devam | 3/3 | RE `ilk2dk_devam_evet_min` |
| Tur sayısı | kâğıt 4, kurgu 3, animatik 3 (tahmin) | RE `kagit_tur_max`, `kurgu_tur_max` |
| Kesme turu | 10 plan + 2 sahne, ≥ %50 uygulanır | RE `kesme_turu_oneri` |
| İlgi eğrisi ↔ hedef eğri | Spearman ≥ 0,5; medyan ilgisi ≤ 4 olan dakika kesme turuna girer | tahmin, kalibre edilecek |
| Defterde açık olup seyircide olmayan soru | 0 hedef, BAYRAK → hikâye odası | ZN §7.3 ek çıktı 4 |

### 7.3 Bu belgenin önerdiği yeni eşikler (`ritim_esikleri.json`'a eklenecek)

| Anahtar | Değer | Kaynak |
|---|---|---|
| `izleme_parcasi_sn` | [240, 300] | BK §3.8, H/kurgu-izleme-denetimi ("~4–5 dk") |
| `izleme_kare_plan` | 3 | ZN §7.3, BK §3.8 |
| `izleme_sayfa_plan` | 6 | tahmin |
| `animatik_tur_max` | 3 | tahmin |
| `animatik_yer_tutucu_max_oran` | 0,10 | tahmin |
| `ken_burns_zoom`, `ken_burns_kayma` | 0,08, 0,02 | kurgu köprüsü V5 varsayılanı (`KULLANIM.txt`) |
| `senkron_tolerans_kare` | 1 (24 fps) | AR3 öneri 4 (mühendislik tercihi) |
| `syncnet_guven_min` | 3 | AR3 A1 (LatentSync filtre eşiği) |
| `whisper_pencere_pay_sn` | 1,0 | kural DR/H/proje-b2, sayı tahmin |
| `dudak_ustune_replik_max` | 0 | H/video-istem-kurali |
| `capcut_bosluk_max` | 0 | H/capcut-elle-duzenleme |
| `zincir_derinlik_max` | 2 | AR2 §2.3 |
| `kirp_guven_min` | 0,6 | tahmin |
| `kirp_hareket_mad_k`, `kirp_hareket_sure_sn` | 3, 0,2 | tahmin |
| `hiz_aralik_diyalogsuz` | [0,90, 1,15] | tahmin |
| `yeniden_kadraj_max` | 0,10 | tahmin |
| `tepe_sonrasi_uzun_plan_pencere_sn` | 20 | tahmin |
| `sapma_plan_oran_max` | 0,25 (T1↔T2 plan süresi farkı; BAYRAK) | tahmin |
| `kurgu_ayrilan_oran` | 0,40 (yeniden deneme payının; = temelin %8'i) | tahmin |
| `plan_basi_kurgu_tekrar_max` | 2 | tahmin |
| `oncelik_konum_agirligi` | 1,5 | tahmin |
| `ilgi_korelasyon_min`, `ilgi_dusuk_esik` | 0,5, 4 | tahmin |
| `ozet_kismen_agirlik` | 0,5 | tahmin |

**Kalibrasyon kuralı:** "tahmin" işaretli her eşik ilk filmde ölçülür. Ders defteri, eşik ↔ seyirci puanı ↔ kullanıcı notu
ilişkisini kaydeder. Değer ancak iki filmlik kanıtla değiştirilir (§8.5). ZN'deki sayıların çoğu da test edilmemiş
türetmelerdir (ZN §2.6 kendi hesabı). Kurgu turları bu sayıları doğrulayacak ilk veri kaynağıdır.

## 8. Kesin kararların kendi alanımda uygulanışı

### 8.1 Klip içi zaman: atomik eylem zinciri (kesin karar 2) ve senkron kuralı
Kurgu açısından atomik zincirin en büyük kazancı şudur: kesme noktası artık tahmin edilmez, plandan **hesaplanır**.
1. **Kesme eylemin üstünde:** `kesme.tip: eylem` ise A planı son adımın %60–70'inde biter. B planı aynı adımın devamıyla
   başlar (ZN §3.4). B'nin `baslangic_durumu` A'nın `bitis_durumu`'na eşittir (ZN §3.7). `kirp_oner`, planlanan adım
   saniyelerini klipte ölçülen hareket aralığına eşler ve kesmeyi oraya koyar.
2. **Ölçülen adım ≠ planlanan adım:** Ölçülen hareket bölütleri adım sayısından azsa (Flow bir adımı atladıysa) BAYRAK
   verilir. Kurgucu önce eksik adımın başka bir planda görünüp görünmediğine bakar (ekleme planı köprüsü, ZN §3.5).
   Görünmüyorsa yeniden çekim kuyruğuna yazar. Planlanan ve ölçülen adım süreleri ders defterine gider: Veo'nun "yürür"
   adımını kaç kat uzun oynattığı gibi bilgiler yönetmenin sonraki planlarını kalibre eder.
3. **Efekt yerleşimi ölçülen adım anına yapılır:** ayak sesi ilk adımın ölçülen başına, kapı sesi kavrama adımına konur.
   Yeniden çekilen planda efektler otomatik yeniden yerleşir (DR: "yeni çekilen planlar efektsiz kalıyordu").
4. **Konuşmalı planda tek adım:** adım replikten önce gelir (ZN §3.7, P087 örneği). `kirp_oner` replik penceresiyle adım
   çakışırsa BAYRAK verir (konuşurken nesneyle uğraşmak dudağı bozar, ZN §2.3).
5. **Animatikte eylem şeridi = zincirin kendisi.** Seyirci durağan karede neyin olacağını adım adım okur. Böylece zincir
   hem Flow'a hem seyirciye aynı metinle gider. Zincirde mantık boşluğu varsa (kapı açılmadan içeri girmek gibi) animatikte görünür.
6. **Senkron kuralı (§5.1):** Görünen konuşanın sesi her zaman klip zamanına bağlı yerleşir. Bu yüzden J/L kesme, klip
   bölme ve kırpma dudak kaymasına yol açamaz. B2'deki "seslerde kayma" sorunu tam olarak bunun bozulmasından çıkmıştı
   (H/proje-b2: aynı klip iki plana bölününce replikler kaydı).

### 8.2 (a) Videodan önce animatik film + habersiz seyirci
- Animatik, T1 çizelgesiyle **gerçek sürelerde** kurulur (TTS ölçülmüş). Seyirci ritmi tahminle değil, filmin gerçek
  süresiyle yargılar. "Gereksiz uzun" notu kredi harcanmadan yakalanır.
- Diyalog, J/L, ambiyans, müzik ve kartlar son kurguyla aynı kodla (`kurgu_render.py`) yerleşir. Animatikte geçen ses ve
  ritim kuralları T2'de geri gidemez (§2.1).
- Kesme turu animatikte yapılır, kesilen plana video kredisi harcanmaz (B11). B2'de animatik atlanmıştı: 50+ yeniden
  çekim olmuştu ve "B1'de video kredisini animatik onayı olmadan yakmak sonradan yamaya yol açtı" (H/proje-b2).
- Animatik geçmeden video aşaması başlamaz. Bu `film.py`'de koddur, beceride yazılı bir kural olarak kalmaz
  (test 9, §6.2). Yalnız `--onayli` modda kullanıcıya izletilir.
- Habersizlik: seyirciye yalnız paket verilir, aracı yoktur (Read/Write). İsteğe bağlı API modu vardır. Ad sızdırılmaz.
  Her tur yeni seyirciyle yapılır (ZN §7.3).

### 8.3 (b) Dünya durumu defteri + zıplama denetimi · (c) referansla yüz kontrolü
- Defterin sahibi süreklilik uzmanıdır. Kurgu defteri **tüketir**: kurgucu, kesici ya da kullanıcı çizelgede bir planı
  kesip yer değiştirdiğinde zıplama denetimi **yeni sırayla** yeniden koşar. Örnek: "anahtar A'dan B'ye geçti" bilgisini
  taşıyan plan kesilirse, sonraki planda anahtar açıklamasız B'nin elinde kalır ve kesme simülasyonu bunu HATA olarak
  yakalar. Kesici "bu plan gereksiz" dese bile bu kesme uygulanmaz.
- Yüz kontrolü (V2 kare kare benzerlik dizisi) kırpma penceresini daraltır. Yüz kaymasının başladığı andan önceki bölüm
  kullanılır (ZN §2.2 d). Kalan pencere plan tipinin alt sınırından kısaysa madde yeniden çekim kuyruğuna gider.
  Seyirci "bu aynı kişi mi?" derse kurgucu önce V2 sayılarına bakar. Sayılar yüz kaymasını doğrulamıyorsa sorun kostüm ya da
  ışık olabilir; madde süreklilik uzmanına gider.

### 8.4 (d) Kare zinciri
- K6: A'nın çıkış noktası, B'nin başlangıç karesi çıkarılmadan **önce** kesinleşir. Kare klibin en son karesinden değil,
  kurguda kullanılacak çıkış anından alınır. Böylece son 0,5–1,0 sn'deki morf riski de dışarıda kalır (ZN §2.2).
- **Zincir dalgaları:** `devam` ile bağlı planlar aynı Memmet partisinde gönderilemez. B, A'nın kırpılmış karesini bekler.
  `film.py` videoyu dalgalarla üretir: 1. dalga zincir başları ve bağımsız planlar, 2. dalga bunların ardılları, 3. dalga
  (derinlik ≤ 2). Kredi değişmez, süre biraz uzar. Tempo kuralları her dalgada aynıdır (DR).
- **Kilit:** Zincir karesi verilmiş A'nın çıkış noktası kurguda değiştirilemez (`kullanim_kilit: zincir`).
  Kurgucu yalnız B'nin başını kırpabilir (≥ 0,3 sn). A yeniden çekilirse B de çekilir. Kuyruk bu maliyeti `zincir_etkisi`
  ile önceden gösterir.

### 8.5 (e) Kendi kendine öğrenen ders defteri (kurgu payı)
Her kurgu turunun sonunda `ders_defteri.py --kurgu` şunları yazar:
1. **Kök neden sayımı:** hangi kopukluk türü, kaç kez, hangi aşamada (T1 mi T2 mi) yakalandı (§5.6 sözlüğü).
2. **Düzeltmenin işe yarayıp yaramadığı:** Düzeltilen madde sonraki turda yeniden işaretlendiyse çözüm "işe yaramadı"
   diye kaydedilir. Merdivenin hangi basamağının hangi soruna yettiği böylece öğrenilir.
3. **Ölçü ↔ puan ilişkisi:** ASL, J/L oranı, ölü süre ve eğri sapması ile seyirci ritim/akıcılık medyanı. Tahmin eşikler
   (§7.3) bu kayıtla kalibre edilir.
4. **Karakter başına gerçek konuşma hızı** (TTS ve Veo ayrı). Kâğıt formülündeki 2,5 kelime/sn yerine o karakterin
   ölçülen hızı kullanılır ve seri kütüphanesine yazılır.
5. **Veo zaman sapması:** plan tipine göre planlanan ve ölçülen adım süresi.
6. **Gerçek yeniden çekim oranı** (B12'nin %8 tahmini burada sınanır) ve harcanan kredi.

Terfi kuralı: bir aday ancak **iki filmde** ya da bir filmde **≥ 3 kez** aynı kök nedenle doğrulanırsa
`ritim_esikleri.json` ya da ajan kuralı olur. Sayılar tahmindir. Amaç tek bir gürültülü puanla kural değiştirmemektir (DR: "puanlar gürültülü").

### 8.6 Ses kararı: kurgunun ihtiyacı ve önerim
Ses yolunun seçimi ses uzmanınındır. Kurgunun koşulları şunlardır:
1. Her replik **ayrı bir dosya** olmalı ve kelime zamanları bulunmalı. Bu, hangi yol seçilirse seçilsin şarttır:
   J/L, ekran dışı replik ve altyazı bunsuz yapılamaz.
2. Görünen konuşanın sesi klip zamanına bağlı olmalı (senkron kuralı).
3. Klipte kaynağı olmayan ekran dışı replikler için **aynı hedef sesle TTS** gerekir.

Bu koşullara göre kurgu açısından en uygun yol **AR3'ün önerdiği (3)**: Veo konuşur, demucs/RoFormer ile ses ayrılır,
karakterin sabit sesine dönüştürülür. Nedenleri:
- Zamanlama Veo'dan gelir, dudak bozulmaz.
- L kesme, ayrılmış ses kanalıyla serbestçe yapılır.
- Dönüşümün hedef sesi TTS sesiyle aynı olduğu için ekran dışı TTS satırları ve **animatikteki TTS** son filmle aynı
  tınıda çıkar. Animatik seyircisinin duyduğu sesin rengi son filmde değişmez.

(2) TTS + dudak senkronu ancak Veo repliği bozduğunda yedek olarak kullanılır. Kurgu tarafında farkı yoktur, aynı senkron
kuralı uygulanır.

**Altyazı:** Altyazı **duyulan** metinden yapılır (`metin_duyulan`). Veo kelime atladıysa altyazı senaryodaki metni değil
duyulanı gösterir. Kelime hata oranı düşükse senaryo metni sese hizalanır (stable-ts `align`, AR3 A4); adların yazımı böylece doğru kalır.

### 8.7 Kullanıcı CapCut'ta düzenleme yaptığında taslak karar ağacı
Belgeler çelişiyor: H/capcut-elle-duzenleme "farkları plana işle, projeyi yeniden kur" diyor, UH ve H/uretim-hatti-v2
"düzenleme varsa taslak yeniden kurulmaz, dosyalar yerinde değişir" diyor. İkisini şöyle birleştiriyorum:
1. `TASLAK_FARK` boşsa yeni sürüm KURGU_PLANI'ndan kurulur. Eski taslak silinmez.
2. Değişiklikler yalnız Klipler'de kırpma/silme/taşıma ise ve `geri_uretilemeyen` boşsa: kullanıcı kararları KURGU_PLANI'na
   kilitli olarak işlenir. **Yeni sürüm** `v<N+1>` kurulur ve bütün kanallar kullanıcının kararını izler. Kayan
   Diyalog/Ambiyans kanalı ve boşluk sorunu böylece çözülür. Kullanıcının taslağı olduğu gibi kalır.
3. `geri_uretilemeyen` doluysa (renk, elle ses ayarı, kendi yazısı, efekti) yeniden kurulmaz. Kullanıcının taslağı
   **klonlanır** (yeni kimlik; kurgu köprüsü `hareket.py` → `clone_project` emsali: "Asıl proje değiştirilmez"). Klonda
   yalnız değişen segmentler yamanır ve sonraki segmentler bütün kanallarda aynı miktar kaydırılır.
4. Planlı yer tutucunun yerine gerçek klip gelmesi tek istisnadır. Aynı süreyle ve aynı dosya adıyla yerinde değişir
   (H/proje-b2 uygulaması).
5. Taslak şifreliyse okunamaz. Kullanıcıya yedek yol bir cümleyle söylenir (§9.4 açık soru 2).

Hiçbir durumda kullanıcının taslak klasörüne yazılmaz.

### 8.8 (f) Kalıcı seri evreni kütüphanesi (kurgu varlıkları)
Kütüphanenin sahibi ortaktır. Kurgunun koyduğu ve sonraki filmde yeniden kullandığı varlıklar:
- **Karakter ses profili:** voice_id, LUFS ofseti, ölçülen konuşma hızı, `etiket_anonim`.
- **Mekân ambiyans zemini:** dosya + seviye. Aynı mekân sonraki filmde aynı sesle duyulur.
- **Leitmotif kayıtları:** onaylı müzik parçaları, giriş/çıkış alışkanlıkları.
- **Şablonlar:** başlık/yer kartı/jenerik (font, renk, konum, süre), renk cilası ayarı, CapCut kanal düzeni.
- **Önceki filmin seyirci özeti:** sonraki filmin seyircisine "previously" olarak verilir (UH §2'deki "önceki bölümlerin
  izleyici özeti" yöntemi). Hikâye belgesi verilmez.
- **Kurgu dersleri** (§8.5) seri boyunca birikir.

### 8.9 Kesin karar 1, 5 ve 6'nın kurgu karşılığı
- **Karar 1 (yalnız konu sorulur):** Kurguda yaratıcı soru sorulmaz. Kullanıcıya giden her mesaj bilgidir: "taslak
  hazır", "X kredi gerekiyor", "Flow uyarı verdi, durdum". Kullanıcının elinin değmesi gereken üç yer kalır: kredi yüklemek,
  Flow girişi/doğrulaması, CapCut'tan dışa aktarmak. Onay noktaları yalnız `--onayli` modda devreye girer.
- **Karar 5 (Memmet seri üretim aracı değil):** Yeniden çekim kuyruğu küçük listelerle Memmet'e gider. Tempo kuralları
  aynıdır (BK §6.2.6), kullanıcı başındaysa `--mod elle` kullanılır. Uyarıda kuyruk `flow_durdu` olur, yeniden deneme
  yapılmaz, atlatma hiç yapılmaz. Kurgu, Flow'u hızlandıran hiçbir şey önermez. Zincir dalgaları gönderimi seyrekleştirir.
- **Karar 6 (kaliteden ödün yok):**
  - Bütçe yetmediğinde model, çözünürlük ya da plan sayısı düşürülmez. Hat bekler (H/proje-b2: "kredi yüklenene kadar bekler").
  - Yer tutucu ve dijital yakınlaştırma sınırlıdır (§5.5).
  - 3 turda geçemeyen film "geçti" diye sunulmaz. Eksikleri yazılı olarak verilir.

## 9. Riskler, çakışmalar, açık sorular

### 9.1 Riskler ve önlemler

| # | Risk | Önlem |
|---|---|---|
| R1 | **Kare paketi izlemek değildir.** Seyirci hareketi görmez, sesi duymaz. Ritim ve duygu puanı gerçek izleyiciden sapabilir. Tutma verisi de yok (BK §1.8.5). | Ses ve hareket kuralları makinede (Z3, senkron, B9). Duyulanlar pakete metin olarak girer. Kullanıcı notları ve yayın sonrası veriler ders defterinde puanlarla karşılaştırılır. |
| R2 | **Animatik ≠ son film.** Veo zamanlaması plandan sapar; animatikten geçen sahne kurguda düşebilir. | T1↔T2 sapma raporu, geri gidiş yasağı, kurgu izleme turu. |
| R3 | **Seyirci maliyeti ve kullanım sınırı.** En kötü durumda (3 parti × 3 seyirci × (3 animatik + 3 kurgu turu) + ilk 120 testleri) ≈ 60 Opus çalışması × ≈ 45 bin görüntü token'ı ≈ 2,7 M token (tahmin). EMBERFALL'da kullanım sınırı dolmuştu (YR §1). | 2.–3. turda yalnız geçemeyen ya da değişen partiler izletilir. Her şey dosyaya yazılır, `film.py` kaldığı turdan devam eder. |
| R4 | **Uzun oturumda dikkat dağılması.** 165 planlık parti tek oturumda izlenir (AR1 C: LongStoryEval'de uzun metinde yargıcın dikkati dağılıyor). | Puan parça başına alınır. Sonraki parçalar sistematik olarak düşük puan alıyorsa (konum yanlılığı) oturum parçaya bölünür. Karar veriyle verilir. |
| R5 | **Kamera hareketli klipte hareket başlangıcı yanlış bulunur.** Push-in, ilk kareden itibaren enerji üretir. | `hareket_tipi ≠ sabit` ise enerji yalnız özne bölgesinde ölçülür (YuNet/MediaPipe kutusu) ya da kamera hareketi telafi edilir. Olmazsa planlanan zaman kullanılır ve güven düşük işaretlenip kurgucuya gider. |
| R6 | **Senkron kuralının kalitesi ses ayrıştırmaya bağlı** (demucs artığı, AR3 A3). | Ses uzmanının alanı. Kurgu yalnız yerleşimi garanti eder. |
| R7 | **Zincir dalgaları süreyi uzatır.** Yeniden çekimde zincir zinciri tetikler. | Derinlik ≤ 2. Kuyruk zincir maliyetini önceden gösterir. |
| R8 | **CapCut uyumluluğu.** pycapcut 0.0.3'te hız, ayna, ses sönümü ve ses seviyesi anahtar karesi desteği doğrulanmadı. Yeni CapCut taslağı şifreleyebilir (`notlari_oku.py` bu durumu zaten bildiriyor). | Desteklenmeyen özellik önizlemede ffmpeg ile yapılır. Taslakta yaklaşık hâli kurulur ve NOTLAR'a yazılır. İlk kullanımda gerçek CapCut'ta 1 dakikalık deneme taslağı açılır (kurgu köprüsü KULLANIM.txt da "Windows CapCut arayüzü bu ortamda çalıştırılmadı" diyor). |
| R9 | **Otomatik araç kullanıcı kararını ezebilir.** | `kullanim_kaynak: kullanici` kilidi. Kullanıcının taslağına yazılmaz, her sürüm yeni taslak olur (test 8). |
| R10 | **Bütçe tahmini zayıf.** ZN'deki 405 klip / ≈ 5.800 kredi türetilmiş bir değerdir. B2'de yeniden çekim ≈ %37 olmuştu. | Animatik ve kâğıt kapıları sayesinde oranın düşmesi beklenir (tahmin). Her kredili adımdan önce `URETIM_ONIZLEME` yazılır. Kredi yetmezse hat bekler, kalite düşürülmez. |
| R11 | **İşlemci render süresi.** Kullanıcının bilgisayarında (x264 işlemcide) 40 dk'lık önizleme her turda yeniden render edilir. | Plan başına önbellek. Yalnız değişen parçalar yeniden kodlanır, parti başına render alınır. Tam render süresi bilinmiyor (tahmin 15–40 dk), ilk filmde ölçülmeli. |
| R12 | **Ad sızdırmama sezgisi kaçırabilir.** "Father", unvan ya da takma ad adın yerine geçebilir. | Karakter kartına `takma_adlar` listesi eklenir. Herhangi birinin ilk geçişi "ad söylendi" sayılır. |
| R13 | **Durağan kare animatiği yavaş hissettirir.** Ritim puanı aşağı yanlı çıkabilir. | Seyirci istemine not düşülür. T1 ve T2 ritim puanları karşılaştırılıp ders defterine yazılır. Gerekirse T1 ritim eşiği kalibre edilir. |
| R14 | **Kesme mekanik olarak temiz ama duygusal olarak zararlı olabilir** (bir `duygu_tutma` planını kesmek gibi). | Z2 (#35–39) kesme simülasyonuna dahildir. Son kararı kurgucu verir. Kesme sonrası turda seyirci duyguyu yeniden puanlar. |
| R15 | **API modunda anahtar güvenliği.** | Anahtar yalnız ortam değişkeninde ya da `AYARLAR/`'da tutulur, loglanmaz, `paketle.py` sızıntı taraması yapar (BK §6.5). |

### 9.2 Diğer uzmanlarla çakışabilecek noktalar (dosyaları okunmadı, olası sınırlar)
1. **Habersiz seyirci (hikâye/seyirci uzmanı):** Mevcut ajan 3 ölçüt ve ORTALAMA kullanıyor. Ben 6 ölçüt, medyan, JSON
   ve ad sızdırmama istiyorum. Kâğıt, animatik ve kurgu modları için **tek şema** önerilir. Ajan ikiye bölünürse kâğıt
   modu onlarda, izleme modu bende kalır.
2. **Z0/Z1/Z2 (yönetmen, hikâye odası):** Kurallar onlarındır. Zamana bağlı hesap ve komşuluk yeniden denetimi
   `zaman_cizelgesi.py` ortak kütüphanesinde durur. Aynı ölçünün iki ayrı kodla hesaplanması sonuçları ayrıştırır, buna izin verilmemeli.
3. **Süreklilik:**
   - `YENIDEN_URET.json` şeması ortak olmalı (`kaynak_kapi` alanı).
   - V1/V2 raporları kusurların **zaman damgasını** vermeli (`kirp_oner` buna muhtaç).
   - Dünya durumu defteri yeni sırayla yeniden koşturulabilmeli.
   - `ayna_yasak` bilgisi onlardan gelir.
   - AR2 K1 kopukluk adaylarını seyirciye değil kurgucuya vermeyi öneriyorum (habersizlik, aşağıda D7).
4. **Ses:**
   - Replik başına dosya + kelime zamanı gerekir.
   - `dudak_denetim.py`'nin ağız hareketi dizisini dışarı vermesi gerekir (B9 için).
   - Z3 #44–47 ölçümünü kimin yapacağına karar verilmeli. Önerim: ölçüm bende (`kurgu_denetim.py`), düzeltme ve eşitleme sesçide.
   - Ambiyans ve efekt planının biçimi ortak olmalı.
5. **Müzik:** Müzik listesi plan aralıklarına bağlı. Kırpmadan sonra zamana çeviren kurgudur. Animatikte geçici müzik kullanılacaksa #40 ölçüsü T1'de sınırlı kalır.
6. **Yönetmen:** `yonetmen.md`'deki "Yeniden çekim modu" kurgucunun sınıflamasıyla örtüşüyor. Sınır şöyle: kurgucu
   **ne ve neden** gerektiğini söyler (`yeni_plan_iste.gereksinim`), yönetmen **nasıl** çekileceğini yazar.
7. **Orkestratör:** `film.py` aşama sırası, 4 çıkış kodu, zincir dalgaları.
8. **Yayın:** Bölüm (chapter) zamanları ve Shorts pencereleri KURGU_PLANI'ndan alınır. Jenerik çizelgede ≤ 60 sn yer tutar.
9. **İstem mühendisi:** `kullanim` SAHNELER.json'da planlanan değer olarak kalır. Ölçülen değer KURGU_PLANI'na yazılır. İkisi karıştırılmamalı.
10. **Seri kütüphanesi:** `etiket_anonim`, `takma_adlar`, karakter ses profili, mekân zemini alanları.

### 9.3 Belgelerdeki çelişkiler (alanımla ilgili) ve önerim

| # | Çelişki | Önerim |
|---|---|---|
| D1 | Bütçe yetmezse: ZN §2.6 "film kısaltılır" ↔ H/proje-b2 ve kesin karar 6 "bekler, kalite kısılmaz" | **Bekler.** Film süresi hikâyeden gelir (ZN §2.5.5 dolgu yasağıyla tutarlı). ZN §2.6'daki cümle güncellenmeli. |
| D2 | Kullanıcı düzenlemesinden sonra taslak yeniden kurulsun mu (H/capcut-elle-duzenleme ↔ UH, H/uretim-hatti-v2) | §8.7 karar ağacı. |
| D3 | Dosyaların yerinde değişmesi (H/proje-b2) ↔ "kullanıcının taslağının bağlı olduğu dosyalara dokunma" (DR) | Yerinde değişim yalnız planlı yer tutucu için. Gerisi yeni sürüm ya da klon. |
| D4 | "Parti" anlamı (BK §8 #14) | Alanlar ayrı: `parti` (≈ 13 dk) ve `izleme_parcasi` (240–300 sn). |
| D5 | Seyirci eşiği 7 ↔ 8 (BK §8 #20) | 8 (RE). |
| D6 | Rapor klasörü `RAPORLAR/` (ZN §6.2) ↔ `_RAPOR/` (kod) | `_RAPOR/`. ZN düzeltilmeli. |
| D7 | K1 kopukluk adayları kurgu izleme ajanına verilsin (AR2 §6.2) ↔ seyirci habersiz kalmalı (ZN §7.3) | Kurgucuya verilir. Seyirci bulgusuyla sonradan eşlenir: ikisi aynı geçişi gösteriyorsa bulgu doğrulanmış sayılır. |
| D8 | `memmet.py` varsayılanı `video_cozunurluk: "360p"` ↔ karar 720p (BK §8 #1) | 720p olmalı. 360p'den 1080p'ye büyütme kurgu kalitesini düşürür. Memmet sahibine bildirilmeli. |
| D9 | Kurgu köprüsü şema örneği `fps: 30` ↔ `capcut_film.py` 24 ↔ dışa aktarma 24 fps (UH §8) | 24. |
| D10 | Animatiği kullanıcı onaylar (UH, H/uretim-hatti-v2, BK §7.3) ↔ kesin karar 1 | Onay yalnız `--onayli` modda. Varsayılanda kapıyı seyirci + kurgucu tutar. |
| D11 | Kesme turu "kurgu bitince" (ZN §7.2.9) | Animatikte de yapılsın (kredi tasarrufu, kaliteden ödün değil). Kurguda tur 1 sonunda yapılsın ki sonraki turlar kesmeyi doğrulasın. |
| D12 | MediaPipe 0.10.14 sabit (H/openmontage, OpenMontage venv'i) ↔ 1.1.1 (AR2 §6.3 ana hat) | Ana hat ve OpenMontage ayrı venv'de kalmalı. Ana hattaki sürüm ağız hareketi ölçümü için ses/süreklilik uzmanıyla birlikte sabitlenmeli. |

### 9.4 Açık sorular
1. **Kurgu turu sınırı:** RE `kurgu_tur_max = 3` sonrasında "eğilim kuralı" eklensin mi? Önerim: son tur GENEL medyanını
   ≥ 0,5 artırdıysa ve bütçe varsa en çok 5 tura kadar devam edilsin (tahmin). Ekip kararı gerekir.
2. **CapCut şifrelemesi:** Kullanıcının CapCut sürümü taslakları şifreliyor mu? Şifreliyorsa `taslak_fark` ve
   `notlari_oku` çalışmaz. Yedek yollar: notları SRT olarak dışa aktarmak (`notlari_oku.py` önerisi) ya da sürüm sabitlemek.
   Kullanıcının bilgisayarında bir kez denenmeli.
3. **pycapcut 0.0.3 yetenekleri:** hız, ayna, ses sönümü, ses seviyesi anahtar karesi. Gerçek taslakta doğrulanmalı.
4. **Flow klibinin durağan başlangıcı** gerçekte kaç saniye (ZN §2.2: 0,3–1,0)? İlk 20 klipte ölçülüp `kullanim_bas_varsayilan_sn` kalibre edilmeli.
5. **Seyirci oturumu:** parti mi, parça mı? (R4) İlk filmde konum yanlılığına bakılarak karar verilmeli.
6. **API modu:** Kullanıcının Anthropic API anahtarı var mı? Yoksa yalnız ajan modu kullanılır.
7. **Animatikte müzik:** Gerçek müzik animatikten önce hazır olacak mı (müzik/ses uzmanı)? Olmayacaksa geçici müzikle #40 ve müzik giriş/çıkış kuralları T2'ye kalır.
8. **Kesici ne kadar bilmeli?** Önerim: `ekranda_bilgi` + duyulan metin + sıkılma anları. `amac` verilmez. Bağımlılıkları zaten kesme simülasyonu yakalar.
9. **Plan numaraları seyirciye görünsün mü?** Kopukluğu plana bağlamak için gerekli. Yanlılık riskini düşük görüyorum.
   Alternatif: yalnız zaman kodu verilir, plan numarasına makine çevirir.
10. **Kullanıcının ses/müzik notları** kime gider? Önerim: kurgucu sınıflar, ses notları ses uzmanının kuyruğuna gider.
