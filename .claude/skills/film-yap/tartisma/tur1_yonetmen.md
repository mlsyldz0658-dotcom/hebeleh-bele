# Tur 1 — Yönetmen uzmanı: plan dili ve çekim listesi

Hazırlayan: yönetmen uzmanı (Claude, bağımsız; diğer uzmanların dosyaları okunmadı). Tarih: 23.10.2026.
Kapsam: hikâye v2'den sonra gelen **çekim listesi** işi. Atomik eylem zinciri, başlangıç/bitiş durumu, kare zinciri,
kadraj / 180° / bakış / ışık yönünün plana yazılışı, karşılıklı çekim, tepki ve ekleme planları, mekân krokileri,
kamera konumu ağacı ve `SAHNELER.json` uzantısının tam şeması.

**Okunan kaynaklar** (kısaltmalar): `ZN` = `.claude/skills/film-yap/ZANAAT.md`, `RE` = `ritim_esikleri.json`,
`BK` = `BILGI_KURALLARI.md`, `A1/A2/A3` = `arastirma/01_film_hatlari.md`, `02_sureklilik.md`, `03_ses_ve_claude_code.md`,
`UH` = `FILMLE ILGILI CLAUDE/01_URETIM_HATTI.md`, `DR` = `03_DERSLER.md`, `CI` = `YZ_FILM/BILGI/CLAUDE_ICIN.md`,
`KR` = `KARARLAR.md`, `YR` = `YAPIM_REHBERI.md`, `FK` = `FLOW_KESIF.md`, `H/<ad>` = `HAFIZA_YEDEGI/<ad>.md`.
Mevcut kod: `film.py`, `istem_denetim.py`, `puan_oku.py`, `izleme_paketi.py`, `saglayicilar/`, `memmet.py`, `seslendir.py`, `capcut_film.py`.

**Sayı etiketleri:** kaynağı olan her sayının yanında kaynak kısaltması var. `(hesap)` = kaynaktaki sayılardan ya da
optik formülden türetildi. `(tahmin)` = kaynağı yok, ilk partide ölçülüp ayarlanacak başlangıç değeri.

---

## 1. Alanımın hedefi ve başarı ölçütü (sayılarla)

### 1.1 Hedef (tek cümle)
Onaylanmış hikâyeyi, her biri "unutkan" 8–10 sn'lik ayrı bir klipten üretilecek **≈495 planlık** (40 dk için, RE
`hedef_plan_dagilimi_40dk`) bir çekim listesine çevirmek. Her plan için şunlar kâğıtta kesinleşir ve makineyle kanıtlanır:
kamera nerede duruyor, kim nerede, kim neye bakıyor, ışık nereden geliyor, kimin hangi elinde ne var, klipte saniye
saniye ne oluyor, klip hangi durumda bitiyor ve sonraki plana nasıl bağlanıyor.

### 1.2 Temel ilke: ajan karar verir, kod derler ve denetler
Bugünkü hatta yönetmen ajanı görsel ve hareket istemini elle yazıyor (`.claude/agents/yonetmen.md`). Bu yüzden
"kim nerede / nesnenin yolu" bilgisi yalnız Markdown'da kalıyor ve istemlere eksik geçiyor (B3: 44 karede 21 bozuk, DR).
Önerim A1'deki 1 numaralı fikirle aynı yönde:
1. Yönetmen ve plan yazarı **yapılandırılmış plan alanlarını** doldurur: kurulum, işaret noktası, durum, eylem zinciri.
2. Şunları **kod hesaplar**: kadrajdaki konum (sol/orta/sağ üçte bir), eksen tarafı, bakış yönü, ışığın kadrajdaki
   yönü ve bitiş durumu. Kroki geometrisi ve eylem etkileri bunun için yeterlidir.
3. Kod `gorsel_istem` ve `hareket_istem`'i bu alanlardan **derler**. Kimlik dizeleri kelimesi kelimesine tekrarlanır (DirectorSKILL, A1 B3).
4. Ajanın yazdığıyla kodun hesapladığı birbirini tutmazsa HATA verilir.

### 1.3 Başarı ölçütleri

| # | Ölçüt | Hedef | Kim ölçer | Kaynak / etiket |
|---|---|---|---|---|
| Ö1 | Plan şeması geçerliliği (`cekim` alanları, sözlük değerleri) | Görsel aşamasından önce HATA = 0 | `plan_sema.py` | yeni |
| Ö2 | Kâğıt üstü plan dili kapısı (Z0 #4–6, #11–19 + bu belgedeki Y kuralları) | HATA = 0; BAYRAK'ların hepsi gerekçeli | `plan_denetim.py` | ZN §6.2 |
| Ö3 | Durum zinciri: `bitis_durumu[N]` ≡ `baslangic_durumu[N+1]` (olgular). Açıklaması olmayan sıçrama | 0 | `durum_defteri.py` | ZN Z0 #16, A2 K0 |
| Ö4 | Kâğıtta 180°, bakış ve kadraj sırası ihlali | 0 | `kroki.py` | ZN Z0 #17–18 |
| Ö5 | Görüntüde (G1) kadraj sırası ve bakış ihlali, ilk geçişte | ≤ %3 plan | G1 raporu | (tahmin) |
| Ö6 | Başlangıç karelerinde ilk geçiş bozuk oranı | B3'te 21/44 = **%48** idi → hedef ≤ %15. Plan diline bağlı türler (yanlış kişi, ters el, bakış, yasak ışık) ≤ %8 | G1 raporu | B3 değeri DR; hedef (tahmin) |
| Ö7 | Eylem zinciri uyumu: eylem ve aksiyon planlarında, ilk videoda planlanan bitiş durumuna ulaşma | ≥ %80; ikinci denemede ≥ %95 | `zincir_olcum.py` (VLM durum soruları + MediaPipe) | (tahmin, ilk partide ayarlanır) |
| Ö8 | `devam` geçişlerinde dikiş (A'nın son karesi ↔ B'nin ilk karesi, DINOv2) | ≥ %90 geçişte kosinüs ≥ 0,80 | K1 kapısı | eşik A2 §6.2; oran (tahmin) |
| Ö9 | Video yeniden çekim oranı (plan dili kaynaklı ret dahil) | ≤ %20 | `FILM_DURUM` sayaçları | RE `kredi_yeniden_deneme_payi` |
| Ö10 | Kurgu izleme denetiminde akıcılık medyanı; parti başına KRİTİK / ORTA kopukluk | ≥ 8; KRİTİK 0, ORTA ≤ 3 | habersiz seyirci | ZN §7.3, RE |
| Ö11 | Plan sayısı / ASL / diyalog sahnesinde tepki oranı | 495 ±%15 / 4,2–5,2 sn / ≥ %25 | `plan_denetim.py` | RE |
| Ö12 | Sahne başına plan yazarı öz-denetim turu | ≤ 2, sonra ana Claude'a | `film.py` durum | A3 B6 (OpenMontage 2 tur) |
| Ö13 | Yönetmen aşamasında kullanıcıya sorulan soru | 0 | — | kesin karar 1 |

**Ö6 ve Ö7 neden önemli?** Kullanıcının tek büyük şikâyeti "kopuk" ve "karakter değişiyor" (BK 1.4 #3, H/kurgu-izleme-denetimi).
Bu iki ölçüt, kopukluğun **plan dilinden** gelen kısmını ölçer. Geri kalanı (yüz kayması, morf) süreklilik ve
üretim uzmanlarının alanıdır.

---

## 2. Aşama aşama süreç: her adım için girdi → iş → çıktı dosyası → geçme şartı → kim yapar (ajan/betik/ana Claude)

Yönetmen aşaması, v2 sırasında (BK 7.6) "3. yönetmen" adımıdır. Hikâye v2 kâğıt üstü seyirciden geçtikten sonra başlar,
görsel üretiminden önce biter. Kredi harcamaz. Sonraki aşamalardan (görsel denetimi, video, kurgu izleme) gelen bulgular
yine bu aşamanın yazarlarına döner, çünkü revizyonu aynı yazar yapar (YR §1).

**Neden sahne sözleşmesi?** 495 planı tek ajan tek seferde yazamaz. Plan başına ≈1–1,5 bin token (tahmin) tutar,
toplam yüz binlerce token eder. Bu yüzden iş **sahne sahne** bölünür. Bölününce sahneler arası sürekliliği korumak gerekir.
Bunu Y1'deki **sahne sözleşmesi** sağlar: her sahnenin giriş ve çıkış durumu önceden yazılır. Sahne yazarları
bu sözleşmeye bağlı kaldıkları için paralel çalışabilir.

Aşağıda her adım aynı kalıpla anlatılır: **Girdi → İş → Çıktı → Geçme şartı → Kim**.

### Y0 — Yönetmen brifingi (betik)
- **Girdi:**
  - Hikâye odasının v2 çıktısı: partiler, 8 başlık, replikler, `KURULUMLAR`, `MERAK_DEFTERI`, `IRONILER`, duygu haritası. Dosya adı hikâye uzmanınca belirlenir; burada `_HIKAYE_ODASI/HIKAYE_v2.json` + `.md` varsayıldı.
  - Seri evreni kütüphanesi `EVREN/<SERI>/`: karakter, kostüm ve mekân kartları; varsa önceki filmlerin krokileri ve kurulumları.
  - Onaylı dersler `DERS_DEFTERI.json` (§8.2-e).
- **İş:** `yonetmen_paket.py --brifing` bu dosyaları tek belgede toplar. Toplanan alanlar: karakterlerin görünür kısa tarifi, kostüm durum sözlüğü, mekân listesi, filmde geçerli onaylı dersler, eşik özeti.
- **Çıktı:** `_YONETMEN/00_BRIFING.md`
- **Geçme şartı:** kâğıt seyirci geçti (`puan_oku.py` çıkış 0). Her konuşan karakterin evren kartı var, her mekânın kartı var ya da kart listesine yazıldı.
- **Kim:** betik + ana Claude.

### Y1 — Sahne dökümü ve sahne sözleşmeleri
- **Girdi:** `00_BRIFING.md`, hikâye v2, ZN §1–2 ve §4, RE.
- **İş:** hikâye ≈45–55 sahne grubuna bölünür (ZN §2.4). Her sahne için yazılanlar:
  - `mekan`, `zaman` (gün saati, hava), `sahne_tipi`, `sure_hedef_sn`, `plan_hedef`
  - `vurus`, `sahne_degeri {bas, son}`, `kalip` (klasik_giris / gec_giris / yukselen_diyalog / acilan_sonuc)
  - `konusanlar` ve `sessizler`, `eksen` (iki ve daha çok kişili sahnede)
  - `giris_durumu` ve `cikis_durumu`: kim nerede, nesne kimde, kostüm durumu, ışık kaynaklarının durumu
  - `ironi` rolü, `kurulumlar` ve `kullanimlar` (hikâye defterinden)
- **Çıktı:** `_YONETMEN/10_SAHNE_DOKUMU.json` + okunur özet `05_yonetmen.md` (§1 bölümü)
- **Geçme şartı** (`plan_denetim.py --dokum`):
  - Z0 #1–3: toplam süre 1800–2700 sn, parti oranı 0,30–0,35, vuruş ±%4
  - Z0 #8: sahne ≤ 180 sn
  - Sahne tipi süre ve plan aralıkları (RE `sahne_tipi_aralik`)
  - `sahne_degeri.bas ≠ son` (ZN §7.2 #4)
  - `cikis_durumu[S_n]` → `giris_durumu[S_n+1]` kalıcı olgularda (nesne, kostüm) tutarlı olmalı. Değişen olgu `degisim` satırıyla açıklanır.
  - Konuşan ≤ 8, sahne başına yeni ad ≤ 2 (RE)
  - Sonuç: HATA = 0.
- **Kim:** `yonetmen` ajanı (Opus, yüksek efor). Düzeltmeyi aynı ajan yapar, en çok 2 tur.

### Y2 — Mekân krokileri ve kamera kurulumları
- **Girdi:** `10_SAHNE_DOKUMU.json`, evren mekân kartları, `EVREN/<SERI>/MEKANLAR/*/kroki.json` (seride daha önce varsa).
- **İş:** her mekân için metre ölçekli bir kroki çizilir. Krokide şunlar bulunur:
  - duvarlar, kapı, pencere, ocak, masa
  - **işaret noktaları** (oyuncu işaretleri M1, M2…)
  - ışık kaynakları
  
  Her sahne için de şunlar seçilir:
  - kullanılan işaretler ve eksen
  - **kamera kurulumları** K1…Kn: konum, yön, yükseklik, lens, varsayılan kadraj
  - kamera ağacındaki ebeveyn
  
  `kroki.py --ciz` her sahne için şunları gösteren bir PNG çizer: işaretler, eksen çizgisi, kameralar ve görüş konileri.
- **Çıktı:** `_YONETMEN/20_KROKILER.json`, `_YONETMEN/KROKI/<mekan>.png`, `_YONETMEN/KROKI/<sahne>.png`. Ayrıca yeni mekân kartı açısı gerekiyorsa `_YONETMEN/KART_ISTEGI.json`.
- **Geçme şartı** (`kroki.py --denetle`):
  - Her sahnenin bütün işaretleri tanımlı.
  - İki ve daha çok kişili sahnede `eksen` var. Bütün kurulumlar eksenin aynı tarafında; tek istisna `notr` olarak işaretli eksen üstü kurulum.
  - Her kurulumun görüş konisi, sahnenin bakılan duvarındaki mekân kartı açısıyla eşleşiyor. Eşleşmiyorsa kart isteği yazılır.
  - Işık kaynakları tanımlı.
  - Aynı sahnede art arda kullanılabilecek kurulum çiftleri listelenir: aynı özneye ≥ 30° açı farkı ya da ≥ 2 ölçek kademesi (RE `aci_min_fark_derece`, `olcek_kademe_min_fark`).
  - Sonuç: HATA = 0.
- **Kim:** `yonetmen` ajanı yazar, `kroki.py` hesaplar ve çizer.

### Y3 — Sahne başına plan yazımı (paralel)
- **Girdi:** `yonetmen_paket.py --sahne S07` ile hazırlanan `_YONETMEN/PAKET/S07.md`. İçinde şunlar var:
  - sahne dökümü satırı ve sözleşme (giriş/çıkış)
  - kroki PNG'si, kurulumlar
  - bu sahnenin replikleri (hikâye v2'den)
  - önceki sahnenin son 2 planının özeti
  - ilgili onaylı dersler
  
  Ayrıca `PLAN_DILI.md` (yazım kılavuzu) ve `fiil_sozlugu.json` okunur.
- **İş:** her plan `cekim` alanlarıyla yazılır (§5). Yazılanlar:
  - kurulum, kadraj, kadrajdakiler (işaret, yüz açısı, bakış hedefi)
  - başlangıç durumu (önceki plandan **miras** alınır, yalnız fark yazılır)
  - eylem zinciri (2–3 adım, saniyeli), replik zamanı
  - zincir (geçiş türü, başlangıç ve bitiş karesi kaynağı), kesme, `ekranda_bilgi`
  
  Bitiş durumu adımların `etki` alanlarından hesaplanır. Ajan isterse kendi beklediğini de yazar, kod ikisini karşılaştırır.
- **Çıktı:** `_YONETMEN/30_PLANLAR/S07.json`
- **Geçme şartı:** `plan_denetim.py --sahne S07` HATA = 0. Kapsananlar:
  - Z0 #4–6 ve #11–19 (sahne içi)
  - §7'deki Y kuralları
  - çıkış durumu = sözleşme
  - Öz-denetim en çok 2 tur. Sonra kalan HATA'larla ana Claude'a döner.
- **Kim:** `plan-yazari` ajanı (Opus, yüksek efor), sahne başına bir örnek. Aynı anda en çok 5 örnek çalışır (tahmin; kullanım sınırına göre).

### Y4 — Birleştirme, dünya durumu defteri, film geneli denetim (betik)
- **Girdi:** `30_PLANLAR/*.json`, `20_KROKILER.json`, `10_SAHNE_DOKUMU.json`.
- **İş:**
  - `plan_birlestir.py` sahneleri sırayla birleştirip `SAHNELER.json`'u yazar: `no`, `sira`, `parti`, `kod`. Klip bölme planları `kaynak_klip` ile işaretlenir.
  - `durum_defteri.py` bütün planların durumlarını hikâye zamanı boyunca katlar (fold). Çıktı `DUNYA_DEFTERI.json`: her plan sınırında her varlığın durumu. Zıplama raporu da yazılır.
  - `plan_denetim.py --tum` film genelinde tam Z0'ı ve sahne sınırlarını denetler.
- **Çıktı:** `SAHNELER.json`, `_YONETMEN/DUNYA_DEFTERI.json`, `RAPORLAR/Z0_plan.json`. HATA varsa `YENIDEN_YAZ.json` (ZN §6.2 biçimi).
- **Geçme şartı:** HATA = 0. Her HATA, planı yazan `plan-yazari` örneğine döner (SendMessage).
- **Kim:** betik; yönlendirmeyi ana Claude yapar.

### Y5 — İstem derleme (betik)
- **Girdi:** `SAHNELER.json` (`cekim` dolu), evren kimlik ve kostüm dizeleri, film `stil_eki`, onaylı ders istem ekleri.
- **İş:** `istem_derle.py` her plan için şunları derler:
  - `gorsel_istem` (başlangıç anı; ViMax'in anlık görüntü kuralı, A2 §2.3)
  - `hareket_istem` (saniyeli adımlar + replik + Sound + `No music.`)
  - `*_yedek` (filtre riskine karşı yumuşatılmış hâl)
  - `bitis_karesi` istemi (yalnız Bitir karesi gereken planlarda)
- **Çıktı:** `SAHNELER.json` istem alanları dolu; `_RAPOR/ISTEM_DERLEME.txt` (her planın istem özeti ve kelime sayısı)
- **Geçme şartı:** mevcut `istem_denetim.py` HATA = 0. Ana istemlerde filtre kelimesi = 0 (DR). Yasak sonuç fiili = 0 (RE `yasak_sonuc_fiilleri`).
- **Kim:** betik.

### Y6 — Plan eleştirisi (parti başına)
- **Girdi:** `cekim_listesi.py --parti 1` ile çizilen `_YONETMEN/CEKIM_LISTESI_P1.md`: sahne sahne tablo + kroki PNG'leri + derlenmiş istemler. Ayrıca sahne dökümü (vuruş, sahne değeri).
- **İş:** ajan makinenin yakalayamadığına bakar:
  - Kapsama dramaya hizmet ediyor mu (tepki doğru anda mı, ekleme hangi bilgiyi taşıyor)?
  - Eylem zinciri fiziksel olarak 8 sn'de yapılabilir mi?
  - Kuleshov / göz izi
  - "Kâğıtta doğru, ekranda okunmaz" anlar
- **Çıktı:** `_YONETMEN/40_ELESTIRI_P1.md`. Maddeler `KRİTİK/ORTA/KÜÇÜK | plan | sorun | öneri` biçiminde, son satır `OZET | kapsama: 8 | fiziksel: 7 | kadraj_dili: 8 | okunurluk: 8 | KRITIK: 0`.
- **Geçme şartı:** KRİTİK = 0, ORTA ≤ 3 (ZN §7.3 eşiğiyle aynı ölçek). En çok 2 tur, düzeltmeleri plan yazarları yapar.
- **Kim:** `plan-elestirmeni` ajanı (Opus). Her turda yeni örnek açılır, önceki turu bilmez.

### Y7 — Animatik ve kâğıt seyirci dönüşü (başka uzmanın aşaması, bana dönen kısım)
- **Girdi:** animatik seyirci raporu (kopukluk listesi, sıkıldığım anlar).
- **İş:** plan kaynaklı maddeler (kopukluk, "nereden çıktı", konum anlaşılmıyor) ilgili sahnenin `plan-yazari` örneğine gider. Sahne düzeyindeki maddeler (sıra, sahne kesme) `yonetmen` ajanına gider.
- **Çıktı:** güncellenmiş `30_PLANLAR/*.json` → Y4 ve Y5 yeniden çalışır.
- **Geçme şartı:** animatik seyirci eşiği (o uzmanın kapısı).
- **Kim:** ana Claude yönlendirir.

### Y8 — Görsel denetiminden dönüş (G1)
- **Girdi:** `_RAPOR/YENIDEN_URET.json` (süreklilik uzmanının çıktısı).
- **İş:** aynı plan 2 kez G1'den kalırsa sorun zar değil plandadır. `yonetmen` şunlardan birine karar verir:
  - kadrajı ya da açıyı değiştir
  - riskli eylemi eklemeye böl
  - referans sayısını düşür (üçüncü kişi siluet olur)
  - kurulumu değiştir
  
  Karar `YENIDEN_PLAN_<tur>.json`'a yazılır. Kural: ikinci başarısızlıktan sonra aynı istemle üçüncü deneme yapılmaz (tahmin; G1'in "2 tur sonra insana" kuralına, A2 §6.2, uyumlu).
- **Kim:** `yonetmen` + plan yazarı.

### Y9 — Videodan dönüş (V2 ve zincir ölçümü)
- **Girdi:** `zincir_olcum.py` raporu. Plan bitiş durumuna ulaşmadı, adım sırası değişti ya da fazladan eylem var.
- **İş:** düzeltme sırası:
  1. Aynı istemle 1 yeniden deneme.
  2. Hâlâ olmuyorsa Bitir karesi eklenir (§8.2-d).
  3. Hâlâ olmuyorsa adım planlara bölünür ya da riskli kısım eklemeye taşınır.
  
  Her değişiklik `ders_aday` olarak kaydedilir.
- **Kim:** `yonetmen`, ölçümü betik yapar.

### Y10 — Kurgu izleme dönüşü
- **Girdi:** kurgu izleme raporu (KRİTİK/ORTA).
- **İş:** her madde için "sıra değiştir / kırp / bağlayıcı plan ekle / yeniden çek" kararı verilir.
  - Yeni plan `no = max+1` alır ve iki plan arasına `sira` ile girer (ör. 121.5). Dosya adları değişmez.
  - Yeni sahne gerekiyorsa `--onayli` modda kullanıcıya sorulur. `--tam-otomatik` modda ekip karar verir ve kayda yazar.
- **Çıktı:** `_YONETMEN/YENIDEN_CEKIM_<tur>.json`
- **Kim:** `yonetmen`.

### Y11 — Ders defterine işleme (betik + yönetmen)
- **Girdi:** G1, V2, zincir ölçümü ve kurgu raporları, `SAHNELER.json` plan özellikleri.
- **İş:** `ders_cikar.py` hata türlerini plan özellikleriyle çaprazlar (kadraj × hareket_tipi × fiil × referans sayısı × Bitir). Aynı birleşim ≥ 3 kez başarısızsa `aday` ders yazar (tahmin eşik). `yonetmen` adayı onaylar ya da reddeder. Onaylı ders **bir sonraki partide** `plan_denetim` ve `istem_derle`'ye, sonraki filmlerde Y0 brifingine girer (§8.2-e).
- **Çıktı:** `EVREN/<SERI>/DERS_DEFTERI.json`, ayrıca hat geneli için `YZ_FILM/BILGI/DERS_DEFTERI.json`.
- **Kim:** betik + `yonetmen`.

**Akış özeti:**
```
hikâye v2 ✔ → Y0 brifing → Y1 döküm+sözleşme ⟲ → Y2 kroki+kurulum ⟲ → Y3 sahne planları (paralel) ⟲
→ Y4 birleştir+defter+Z0 ⟲ → Y5 istem derle → Y6 eleştiri ⟲ → [animatik+seyirci] → [kartlar/görsel+G1] → [video+V2] → [kurgu]
                                   ↑___________ Y7 / Y8 / Y9 / Y10 dönüşleri (aynı yazar) ___________|
```

---

## 3. Gereken ajanlar (ad, model, araçlar, görev, okuyacağı dosyalar, çıktısı) — yalnız kendi alanın

Ajan ve beceri ayrımında A3 B5'e uyuldu: uzun çıktı üreten, kendi içinde kapalı ve araç kısıtı isteyen işler ajan olur.
Model seçimi kullanıcı kuralına göre: önemli işlerde Opus + yüksek efor (BK 7.2, H/ajan-opus-yuksek).
Bash izni geniş verilmez. Her ajana yalnız kendi betiği izin listesine (allow) yazılır (A3 öneri 7).

### 3.1 `yonetmen` (mevcut taslak baştan yazılır)

| Alan | Değer |
|---|---|
| model / efor | `opus` (claude-opus-5-5), effort `high` |
| araçlar | `Read, Write, Edit, Glob, Grep, Bash`. Bash yalnız `python YZ_FILM/ARACLAR/plan_denetim.py *` ve `python YZ_FILM/ARACLAR/kroki.py *` için izinli |
| görevi | Y1 sahne dökümü ve sözleşmeler; Y2 kroki ve kamera kurulumları; Y8–Y10 yeniden plan ve yeniden çekim kararları; Y11 ders onayı. Sahne sırası, sahne bölme/birleştirme ve kurulum seçimi ona aittir. Plan plan yazım onun işi değil |
| okuyacağı dosyalar | `_YONETMEN/00_BRIFING.md`, hikâye v2, `ZANAAT.md` §2–4 ve §6, `ritim_esikleri.json`, `PLAN_DILI.md` §Kroki ve §Kurulum, `EVREN/<SERI>/MEKANLAR/*`, `03_DERSLER.md`, `DERS_DEFTERI.json` (onaylı) |
| çıktısı | `10_SAHNE_DOKUMU.json`, `20_KROKILER.json`, `05_yonetmen.md` (insan okunur özet: sahne listesi, kroki bağlantıları, riskli planlar), `KART_ISTEGI.json`, `YENIDEN_PLAN_<tur>.json`, `YENIDEN_CEKIM_<tur>.json` |
| döndürdüğü | dosya yolları + sahne sayısı, plan hedefi, kurulum sayısı, kalan BAYRAK sayısı (≤ 5 satır) |

**Mevcut taslaktan farkı:** Mevcut taslak `gorsel` ve `hareket` istemini elle yazıyor. Yeni taslakta istem yazmaz;
istemleri `istem_derle.py` alanlardan üretir. Stil son eki ajana bırakılmaz, film düzeyinde tek alandır.

### 3.2 `plan-yazari` (yeni)

| Alan | Değer |
|---|---|
| model / efor | `opus`, effort `high` |
| araçlar | `Read, Write, Glob, Bash`. Bash yalnız `python YZ_FILM/ARACLAR/plan_denetim.py * --sahne *` için |
| görevi | Tek bir sahne grubunun planlarını `cekim` şemasıyla yazmak (Y3); Y4, Y6 ve Y7 düzeltmelerini **aynı örnekte** yapmak (SendMessage ile geri dönülür) |
| okuyacağı dosyalar | **Yalnız** `_YONETMEN/PAKET/<S>.md` (her şey içinde), `.claude/skills/film-yap/PLAN_DILI.md`, `YZ_FILM/ARACLAR/veri/fiil_sozlugu.json`. Hikâye belgesinin tamamı verilmez: bağlam küçük kalır, başka sahnenin kararlarını değiştiremez |
| çıktısı | `_YONETMEN/30_PLANLAR/<S>.json` |
| döndürdüğü | plan sayısı, toplam süre, tepki oranı, J/L oranı, kalan BAYRAK listesi, "replik değiştirdim" listesi (hikâye ya da oyuncu denetimi için) |

**Kural (gövdeye yazılır):**
- Replik metnini kendiliğinden değiştirmez. Satır 16 kelimeyi aşıyorsa (RE `replik_max_kelime_8sn`) bölme önerir ve `replik_degisti` listesine yazar.
- Sözleşmedeki çıkış durumuna ulaşamıyorsa sözleşmeyi kendisi değiştirmez; gerekçeyle `yonetmen`e bildirir.

### 3.3 `plan-elestirmeni` (yeni)

| Alan | Değer |
|---|---|
| model / efor | `opus`, effort `high` |
| araçlar | `Read, Write, Glob` (Bash yok) |
| görevi | Parti başına çekim listesini sinematografi gözüyle eleştirmek (Y6). Yazar değildir, düzeltme önerir |
| okuyacağı dosyalar | `_YONETMEN/CEKIM_LISTESI_P<n>.md`, `_YONETMEN/KROKI/*.png`, `10_SAHNE_DOKUMU.json` (yalnız o parti), `PLAN_DILI.md` §Kontrol listesi. Plan yazarının notlarını ve önceki eleştiri turlarını **okumaz** |
| çıktısı | `_YONETMEN/40_ELESTIRI_P<n>[_t<k>].md`. Son satır: `OZET \| kapsama: 8 \| fiziksel: 7 \| kadraj_dili: 8 \| okunurluk: 8 \| KRITIK: 0` (`puan_oku.py` okur) |
| kontrol listesi | (1) Her önemli replikten sonra tepki var mı, doğru kişide mi? (2) Ekleme planı hangi kurulumu ya da kullanımı taşıyor? (3) Eylem zinciri 8 sn'de ve tek klipte fiziksel olarak mümkün mü? (4) Aynı anda iki kişi hareket ediyor mu? (5) Konuşan yüz okunur mu (ölçek, açı)? (6) Konum planı ilk 3 planda mı? (7) Ekran yönü sürüyor mu? (8) Işık kaynağı görünür olanla tutarlı mı? (9) "Geç gir, erken çık" uygulanmış mı? (10) Seyirci bu planda yeni ne öğreniyor (`ekranda_bilgi` gerçekten ekranda mı)? |

### 3.4 Benim alanıma dokunan ama başka uzmanın sahip olduğu ajanlar
- `sureklilik-denetcisi`: G1/V2 görsel modunda **benim ürettiğim durum sorularını** (`durum_sorulari()`, §6) kullanmalı.
  Listeyi görmeden kör tarif yapması A1'deki ARIS önerisine uyar. Ajanın sahibi süreklilik uzmanı.
- `istem-muhendisi`: plan `cekim` alanlarıyla doluysa istemi elle yazmaz, `istem_derle.py`'yi çalıştırır.
  Kendisine yalnız `istem_elle: true` işaretli istisnalar kalır. Bu bir çakışma noktası (§9).
- `habersiz-seyirci`: `ekranda_bilgi` alanını **asla görmez**. Bu alan, seyircinin ne öğrendiğiyle karşılaştırmak içindir (ZN §7.3).

---

## 4. Beceri (skill) tarif adımları — kendi alanın

### 4.1 Dosya yerleşimi
Biçim A3 B4'e göre: SKILL.md < 500 satır, ayrıntılar tek seviye bağlantıyla.
- `film-yap/SKILL.md` içinde kısa bir **"Yönetmen aşaması"** bölümü (≤ 25 satır). Kontrol listesi ve aşağıdaki iki dosyaya bağlantı içerir.
- `film-yap/reference/yonetmen_asamasi.md`: ana Claude'un yürüteceği tarif (4.2). Başında içindekiler olur.
- `film-yap/PLAN_DILI.md`: plan yazarı ve eleştirmenin kılavuzu. İçeriği: sözlükler, atomik zincir yazım kuralları, 6 örnek, kroki ve kurulum kuralları, kontrol listesi. Bu belgenin §5 ve §8'i oraya taşınır.
- `YZ_FILM/ARACLAR/veri/fiil_sozlugu.json`: fiil sözlüğü (§5.4). Ajanlar okur, betikler kullanır.
- Kredi harcamayan bir aşama olduğu için `disable-model-invocation` gerekmez. Ama Y3 paralel ajan açtığı için ana Claude bu
  bölümü yalnız `FILM_DURUM.json` aşaması `yonetmen` iken uygular. Durum `` !`python YZ_FILM/ARACLAR/film.py <film> --durum` `` ile alınır (A3 B6).

### 4.2 Tarif (ana Claude'un kontrol listesi; kopyalanıp işaretlenir)
```
YÖNETMEN AŞAMASI — <FİLM>
[ ] 0. film.py <film> --durum  → "hikaye" tamam, "yonetmen" bekliyor mu? Değilse dur.
[ ] 1. python ARACLAR/yonetmen_paket.py <film> --brifing        → _YONETMEN/00_BRIFING.md
[ ] 2. Ajan yonetmen (mod: DOKUM) → 10_SAHNE_DOKUMU.json
       python ARACLAR/plan_denetim.py <film> --dokum  → HATA varsa aynı ajana SendMessage (≤2 tur)
[ ] 3. Ajan yonetmen (mod: KROKI; aynı örnek) → 20_KROKILER.json
       python ARACLAR/kroki.py <film> --ciz --denetle → HATA varsa aynı ajana (≤2 tur)
       KART_ISTEGI.json doluysa → kart/görsel aşamasına not düş (mekân kartı açısı)
[ ] 4. python ARACLAR/yonetmen_paket.py <film> --sahne all      → _YONETMEN/PAKET/S*.md
[ ] 5. Her sahne için Ajan plan-yazari (en çok 5 paralel; her biri yalnız kendi paketi)
       Her ajan kendi içinde: plan_denetim.py --sahne Sxx (≤2 tur)
       Dönüşte: kalan HATA'lı sahneleri listele
[ ] 6. python ARACLAR/plan_birlestir.py <film>  → SAHNELER.json
       python ARACLAR/durum_defteri.py <film>   → DUNYA_DEFTERI.json + zıplama raporu
       python ARACLAR/plan_denetim.py <film> --tum → RAPORLAR/Z0_plan.json
       HATA → ilgili plan-yazari örneğine SendMessage (sahne kodu → ajan adı eşlemesi 00_DURUM.md'de)
[ ] 7. python ARACLAR/istem_derle.py <film> ; python ARACLAR/istem_denetim.py <film>  → HATA 0
[ ] 8. python ARACLAR/cekim_listesi.py <film> --parti 1,2,3 → CEKIM_LISTESI_P*.md
       Her parti için YENİ Ajan plan-elestirmeni → 40_ELESTIRI_P*.md
       python ARACLAR/puan_oku.py 40_ELESTIRI_P1.md --esik 7 ; KRİTİK>0 ya da ORTA>3 → plan yazarlarına (≤2 tur)
[ ] 9. 00_DURUM.md ve FILM_DURUM.json güncelle → "yonetmen" tamam → animatik aşamasına geç
```

### 4.3 Durma ve devam kuralları
- Her adımın çıktısı dosyadadır. Sıkıştırmadan sonra hafızaya değil `00_DURUM.md`, `FILM_DURUM.json` ve `git log`'a güvenilir (A3 B6).
- 2 öz-denetim turundan sonra HATA kalırsa iki yol var:
  - `--tam-otomatik` modda `yonetmen` ajanı sahneyi yeniden böler ya da kurulumu değiştirir.
  - `--onayli` modda kullanıcıya **tek cümlelik** durum bildirimi verilir. Soru sorulmaz (kesin karar 1); kullanıcı isterse araya girer.
- Kararlar `KARAR_DEFTERI.md`'ye `karar — neden — yanlışsa maliyeti` biçiminde yazılır (A3 B6).
  Örnek: `S12'de eksen batıdan — Mara hep solda — yanlışsa S12'nin 16 görseli yeniden`.
- Paralel ajanlar birbirinin dosyasını okumaz (YR §1). Sahneler arası tutarlılığı ajanlar değil, sözleşme ve `durum_defteri.py` sağlar.

### 4.4 Değerlendirme senaryoları (beceri testi, A3 B4)
1. `ORNEK_3_SAHNE`'nin `cekim` alanlı hâli: Y4–Y5 betikleri hatasız çalışır, derlenen istemler beklenen metinle aynıdır.
2. Bozuk sahne: P2'de kamera eksenin öbür tarafında. `plan_denetim` 180° HATA'sını, `kroki.py` kadraj sırası çelişkisini bulmalı.
3. Bozuk zincir: P3'te fener sol ele geçmiş, ama etki yazılmamış. `durum_defteri` zıplama HATA'sı vermeli.
4. "Kalemi al" tek cümlesiyle gelen plan: `plan_denetim` yasak sonuç fiili HATA'sı vermeli. Plan yazarı atomik zincire çevirmeli.

---

## 5. Veri şeması / plan alanları (JSON örneğiyle)

### 5.1 Katmanlar
```
Film ─┬─ Hikâye partisi (3)               ZN §1.2 (plan düzeyindeki `parti` ise üretim partisi, §5.3)
      ├─ Mekân ── kroki (duvar, öğe, işaret M1..Mn, ışık kaynağı) ── kurulumlar K1..Kn (kamera)
      └─ Sahne grubu S01..S55 (tek mekân + kesintisiz zaman; eksen, ışık, sözleşme)
             └─ Plan (kurgu birimi; SAHNELER.json "sahneler[]" öğesi; no = dosya adı NNN)
                    └─ Klip (üretim birimi, 8/10 sn). Bir klipten 1 ya da 2 plan çıkar (kaynak_klip)
```
- **`no` kimliktir, sıra değildir.** Görsel üretimi başladıktan sonra `no` asla yeniden numaralanmaz, çünkü dosyalar
  `NNN.jpg/mp4` adını taşır. Kurgu sırası `sira` alanındadır (ondalık olabilir: 121.5).
- Bu, B2'deki "A15N, RC27 = no 189–201" karmaşasının çözümüdür (H/proje-b2).

### 5.2 Sahiplik ilkesi ve önceki önerilerle eşleme
Her alt nesnenin **tek sahibi** var: drama-skills'teki "her belge yalnız kendi kararlarının sahibi" kuralı (A1 B2).
Sahibi olmayan ajan o alt nesneye yazmaz; okur.

| Alt nesne | Sahibi | İçerik |
|---|---|---|
| üst düzey mevcut alanlar (`no, parti, referans, replik, kullanim, amac, duygu, motor`) | yönetmen / plan yazarı | şema değişmez (CI) |
| `gorsel_istem*`, `hareket_istem*`, `bitis_karesi` | **`istem_derle.py`** (kod) | `cekim` doluysa elle yazılmaz |
| `cekim` (yeni) | yönetmen / plan yazarı | kamera, kadraj, durum, eylem zinciri, zincir, kesme |
| `zanaat` | hikâye odası | `hedef_duygu, yogunluk, vurus, merak_*, kurulum, kullanim_bilgi, ironi, risk` (ZN §6.1) |
| `ses` | ses / müzik uzmanı | ZN §5 alanları |
| `uretim`, `denetim` | üretim betikleri / kapılar | A2 §6.1 |
| film düzeyi `mekanlar`, `sahne_gruplari` | yönetmen | kroki, kurulum, sözleşme |

ZN §6.1 ve A2 §6.1 aynı bilgileri farklı alt nesnelere (`zanaat` / `sureklilik`) koymayı öneriyordu.
Aynı bilgi iki yerde tutulursa iki kopya zamanla ayrışır. Önerdiğim eşleme:

| Önceki öneri (kaynak) | Yeni yer | Not |
|---|---|---|
| `sure_sn` (ZN) | `kullanim.sure` (mevcut alan) | Aynı şey iki kez tutulmaz. ZN eşikleri `kullanim.sure` üstünden çalışır |
| `sahne_grubu, plan_tipi, klip_sn, kaynak_klip, kesme, eylem_zinciri, ekran_disi_ses, ekranda_bilgi` (ZN) | `cekim.*` | aynen |
| `kadraj` (ZN), `plan_olcegi` (A2) | `cekim.kamera.kadraj` | ZN §3.1 sözlüğü |
| `kamera_konumu, kamera_acisi, kamera_hareketi` (A2), `hareket_tipi` (ZN) | `cekim.kamera.{kurulum, aci, hareket_tipi}` | |
| `kamera_tarafi` (ZN, A2) | sahne `kamera_tarafi` + kod hesaplar | Planda elle yazılmaz; yalnız `eksen_gecis` yazılır |
| `bakis` (ZN, A2) | `cekim.kadrajdakiler[].bakis.hedef` | Kadraj yönünü (`kadraj_sagi`…) kod hesaplar |
| `kadrajdakiler, kadraj_sirasi` (A2) | `cekim.kadrajdakiler` | Sıra, kod hesabıyla konumdan çıkar |
| `kadraj_disi_ama_mekanda` (A2) | dünya defterinden | Mekânda olup kadrajda görünmeyeni geometri bulur |
| `giris_cikis` (A2) | eylem adımı `kadraja_girer` / `kadrajdan_cikar` | Zamanlı olur |
| `nesneler` (A2) | `cekim.baslangic_durumu.nesneler` | Bitişte etkiyle güncellenir |
| `isik, isik_degisimi` (A2) | sahne `isik` + `cekim.isik_degisimi` | |
| `ilk_kare_tarifi, son_kare_tarifi` (A2) | derlenir → `gorsel_istem`, bitiş karesi istemi | Elle yazılmaz |
| `gecis_turu, onceki_plan, son_kare_kullan` (A2) | `cekim.zincir` | §8.2-d |
| `kurulmus_bilgi` (A2) | `zanaat.kurulum` | ZN §4.2 ile aynı |
| `replik_zaman` (ZN) | konuşma adımından derlenir | Ayrı yazılmaz |

### 5.3 Film, mekân ve sahne düzeyi alanları

| Alan | Tür | Zorunlu | Doldurur | Açıklama |
|---|---|---|---|---|
| `stil_eki` | str | evet | yönetmen (Y1) | Filmin tamamında aynı. İçinde "warm firelight" gibi ışık ifadesi **yasak** (BK 4.1 #3) |
| `mekanlar.<id>.evren` | yol | evet | yönetmen | Seri evreni kütüphanesindeki mekân klasörü (§8.2-f) |
| `mekanlar.<id>.kroki.birim / yonler / sinir` | str / str / [[x,y],[x,y]] | evet | yönetmen | metre; x = doğu, y = kuzey; yön_derece 0 = kuzey (pusula) |
| `…kroki.duvarlar[]` | `{id, a, b, aciklik[]}` | evet | yönetmen | Görüş hattı (duvar arkasını görme) hesabı için |
| `…kroki.ogeler[]` | `{id, tur, konum, …}` | evet | yönetmen | kapı (menteşe, açılış yönü), ocak, masa, kilit… |
| `…kroki.isaretler.M*` | `{konum, ad}` | evet | yönetmen | Oyuncu işaretleri; planlar konumu yalnız buradan verir |
| `…kroki.isik_kaynaklari[]` | `{id, konum, tur, renk, varsayilan}` | evet | yönetmen | Taşınan ışık (fener, meşale) kroki dışıdır, nesne olarak elde durur |
| `mekanlar.<id>.kurulumlar.K*` | `{konum, yon_derece, yukseklik, lens_mm, varsayilan_kadraj, ebeveyn, not}` | evet | yönetmen | Kamera ağacı düğümü. `ebeveyn` = `mekan_karti:<açı>` ya da başka bir K |
| `sahne_gruplari.<S>.hikaye_partisi, mekan, zaman, sahne_tipi, sure_hedef_sn, plan_hedef, kalip` | | evet | yönetmen | ZN §2.4 ve §3.2. Hikâye partisi (1–3) burada durur; plan düzeyindeki `parti` mevcut anlamıyla **üretim partisidir** (20 plan, CI) → BK çelişki #14 böyle çözülür |
| `….sahne_degeri {bas, son}` | | evet | yönetmen | ZN §7.2 #4 |
| `….eksen` / `kamera_tarafi` | [id, id] / str | ≥ 2 kişide evet | yönetmen | 180° kuralının kaynağı |
| `….kurulumlar` | [K…] | evet | yönetmen | Bu sahnede kullanılan kurulumlar |
| `….isik {ana, dolgu, arka}` | | evet | yönetmen | Kaynak kimlikleri; renk ve konum krokiden ya da nesneden gelir |
| `….yasaklar` | [str] | hayır | yönetmen | G1 VLM'e sorulur (A2 §6.2 #8) |
| `….giris_durumu / cikis_durumu` | durum nesnesi (5.4) | evet | yönetmen | **Sahne sözleşmesi** |
| `….ana_kareler` | {K: no} | derlenir | `kamera_agaci.py` | Her kurulumun ilk kullanıldığı plan |

### 5.4 Plan düzeyi `cekim` alanları

| Alan | Tür / değerler | Zorunlu | Doldurur | Denetim |
|---|---|---|---|---|
| `kod` | `"S12-P02"` | evet | birleştirici | tekil |
| `sahne_grubu` | `"S12"` | evet | yazar | dökümde var |
| `plan_tipi` | ZN §2.1 sözlüğü | evet | yazar | süre aralığı (RE `plan_sure_aralik_sn`) |
| `klip_sn` | 8 / 10 | evet | yazar | RE `klip_sn` |
| `kaynak_klip` | plan no / null | evet | yazar | Doluysa bu planın kendi görseli ve videosu yok; Memmet atlar |
| `kamera.kurulum` | `"K2"` | evet | yazar | sahnenin kurulum listesinde |
| `kamera.kadraj` | ZN §3.1 | evet | yazar | ölçek sıçraması (Z0 #12) |
| `kamera.aci` | `goz_hizasi, alcak, yuksek, kus_bakisi` | evet | yazar | |
| `kamera.lens_mm` | 24 / 28 / 35 / 50 / 85 | hayır (kurulumdan) | yazar | görüş açısı hesabı |
| `kamera.hareket_tipi`, `hareket_yonu` | ZN §3.6 + `sola/saga/yukari` | evet | yazar | tek hareket (RE `kamera_hareketi_klip_max`) |
| `kamera.odak` | varlık / nesne id | hayır | yazar | `odak_kaydirma`da `{bas, son}` |
| `eksen_gecis` | bool | evet | yazar | Z0 #17 |
| `kadrajdakiler[]` | `{id, olcek, yuz_acisi, bakis{hedef\|yon}, konusur, kimlik_demiri, gorunen[]}` | evet | yazar | Geometri ile karşılaştırılır; referans listesi bundan derlenir |
| `baslangic_durumu` | `"miras"` / `{"fark": {...}}` / tam durum | evet | yazar | `yeni_sahne` dışında `miras` ya da `fark` |
| `eylem_zinciri[]` | adım nesnesi (aşağıda) | evet (insanlı/yaratıklı planda) | yazar | §7 Y kuralları |
| `bitis_durumu` | `"derlenir"` / beklenen tam durum | evet | kod (+ yazar) | Yazar yazdıysa kodun hesabıyla eşit olmalı |
| `replik_kaynagi` | `klip` / `klip:<no>` / `tts` / null | replikte evet | yazar | §8 ses kararı |
| `ekran_disi_ses` | `{karakter, kaynak, bas_sn, sure_sn}` / null | hayır | yazar | Görünen kişi bu sırada "mouth closed" olmalı |
| `zincir` | `{gecis_turu, onceki_plan, baslangic_karesi{kaynak, ebeveyn}, bitis_karesi, derinlik}` | evet | yazar | §8.2-d tablosu |
| `kesme` | `{tip, nokta_sn, ses_tasma_sn}`. `nokta_sn` klibin saatinde. `ses_tasma_sn` > 0 ise L: bu planın sesi sonrakine taşar. < 0 ise J: sonrakinin sesi önce başlar | evet | yazar (kurgu düzeltir) | `kullanim.bas + sure = nokta_sn` (±0,05); Y33–Y36 |
| `isik_degisimi` | `{kaynak, yeni_durum, adim}` / null | hayır | yazar | A2 K0 |
| `yasaklar` | [str] | hayır | yazar | sahne yasaklarına eklenir |
| `ekranda_bilgi` | Türkçe tek cümle | evet | yazar | Habersiz seyirci özetiyle karşılaştırılır; seyirciye **verilmez** |
| `risk_uretim` | `dusuk/orta/yuksek` | evet | yazar | Yüksekse yedek istem ve Bitir kararı |
| `istem_elle` | `{neden}` / yok | hayır | yazar | Derlemeyi o plan için kapatır. Film başına ≤ %5 (tahmin) |
| `_derlenir` | nesne | — | kod | `kadraj_konumu, kamera_tarafi, bakis_kadrajda, isik_kadrajda, replik_zaman, ayna_yasak, gorunmesi_gerekenler` |

**Durum nesnesi** (`giris_durumu`, `cikis_durumu`, `baslangic_durumu`, `bitis_durumu` aynı yapıda):
```json
{
 "varliklar": {
  "<id>": {"mekan": "...", "isaret": "M1", "poz": "ayakta", "yuz_yonu": "guney | <derece> | {\"hedef\": id}",
           "bakis": {"hedef": "<id>"} , "kostum": "mara_k1", "kostum_durumu": ["kapusonu_inik"],
           "sol_el": {"tutar": null, "yer": "dogu_kasa_ic", "sekil": "tutus_tam"},
           "sag_el": {"tutar": "fener", "yer": "kalca_hizasi", "sekil": "tutus_tam"},
           "ifade": "sert (isteğe bağlı)", "gorunur": true}
 },
 "nesneler": {"<id>": {"kimde": "<varlik>", "el": "sol|sag", "durum": "yanik"}  |  {"nerede": "<oge|isaret>", "durum": "..."}}
}
```
- **Olgular** kameradan bağımsızdır: işaret, poz, yüz yönü, eller, nesneler, kostüm, ışık kaynağı durumu.
  `bitis[N] ≡ baslangic[N+1]` karşılaştırması yalnız olgularla yapılır.
- **Kadraj bilgileri** kameraya bağlıdır: konum, ölçek, yüz açısı, bakışın kadrajdaki yönü. Bunlar `kadrajdakiler`
  ve `_derlenir` alanlarında durur. Bu ayrım, "açı değişse de olgular aynı" kuralını (ZN §3.7 #4) makinece uygulanabilir yapar.

**Eylem adımı:**
```json
{"bas": 0.5, "bit": 2.5, "ozne": "mara", "tur": "fiziksel | mikro | konusma",
 "fiil": "<fiil_sozlugu id>", "govde": "sag_kol | sol_el | bas | gozler | tum_beden | kuyruk | kanat ...",
 "yon": "ileri | geri | sola | saga | yukari | asagi", "hedef": "<varlik | nesne | oge | isaret>",
 "olcu": "iki_yavas_adim | 15cm | 90_derece | hafif", "el_sekli": "kiskac | tutus_tam | ...",
 "hiz": "yavas | normal | hizli", "teslim": "fisilti | yumusak | normal | soguk | bagirma (konuşmada)",
 "etki": {"mara.sol_el.tutar": "anahtar", "anahtar.kimde": "mara", "anahtar.el": "sol"},
 "efekt": "tahta_gicirtisi (ses uzmanı doldurabilir)"}
```
- Sağ ve sol **daima karakterin kendi** sağı ve soludur.
- Kadraj yönü yalnız `kadraj_sagi` / `kadraj_solu` sözcükleriyle yazılır. İngilizce istemde de böyledir: `her left hand`, `toward frame right`.
  Çıplak "left/right" yasak (Y-kuralı, §7).

### 5.5 Sözlükler

| Sözlük | Değerler (EN karşılığı derleyicide) | Kaynak |
|---|---|---|
| `kadraj` | EG extreme wide · G wide · OG medium-wide (knees up) · O medium (waist up) · OY medium close-up · Y close-up · CY extreme close-up · D insert/macro · OU over-the-shoulder · IK two-shot | ZN §3.1 |
| kişi `olcek` | kadraj basamakları + `on_plan_omuz` (OU'da öndeki kişi) · `el` · `siluet` | yeni |
| `aci` | `goz_hizasi` eye-level · `alcak` low angle · `yuksek` high angle · `kus_bakisi` top-down | yeni |
| `lens_mm` → yatay görüş açısı | 24 → 73,7° · 28 → 65,5° · 35 → 54,4° · 50 → 39,6° · 85 → 23,9° | (hesap: 2·atan(18/f), 36 mm genişlik) |
| `hareket_tipi` | ZN §3.6 (sabit, yavas_ileri, yavas_geri, yavas_pan, tilt_acilis, takip_yan, omuz_kamera, odak_kaydirma, yörünge, hizli_hareket) | ZN §3.6 |
| `poz` | ayakta, yuruyor, kosuyor, diz_cokmus, comelmis, oturuyor, egilmis, yerde | yeni |
| `yuz_acisi` (kameraya göre yaw) | `on` 0–15° · `3/4` 15–60° · `profil` 60–100° · `sirt` > 100° · `gorunmez` | 15° sınırı A2 §4; diğerleri (tahmin) |
| `el.sekli` (açık parmak sayısıyla) | `serbest` · `acik_avuc` (5 açık) · `yumruk` (0) · `kiskac` (başparmak + işaret, 3 parmak kıvrık) · `uc_parmak` (başparmak + işaret + orta) · `tutus_tam` (4 parmak + başparmak sarılı) · `isaret` (işaret uzatılmış, 4 kıvrık) | kesin karar 2 |
| `el.yer` | yanda, kalca_hizasi, govde_onunde, omuz_hizasi, bas_ustu, cepte, arkada, `<oge/nesne id>` | yeni (EN'de "chest" yerine "in front of the torso": "chest" filtre kelimesi, DR) |
| `zincir.gecis_turu` | `yeni_sahne` · `eylem_kesme` · `devam` · `kurulum_donusu` · `araya_kesme` · `zaman_atlama` | A2 §2.3 genişletildi |
| `baslangic_karesi.kaynak` | `bagimsiz` · `ana_kare` (kurulumun ilk planı; ebeveyn kurulumun ana karesinden) · `turev` (aynı kurulumun sonraki planı) · `onceki_bitis` (Mod A) · `son_kare` (Mod B) | §8.2-d |
| `kesme.tip` | ZN §3.4 (eylem, replik_sonu, L, J, tepki, bakis, eslesme, sert) + `duz` + `devam` | ZN §3.4 |
| `teslim` → EN fiil | fisilti "whispers" · yumusak "says quietly" · normal "says" · soguk "says coldly" · bagirma "shouts" | BK 4.2 #4 |

**Fiil sözlüğü** (`ARACLAR/veri/fiil_sozlugu.json`). Örnek kayıtlar aşağıda; tam liste ≈40 fiil olur (tahmin).
Şablonlarda filtre kelimesi ve yasak sonuç fiili bulunmaz. Bunu test denetler.

| id | tür | zorunlu parametre | EN şablon (tek kişide öznesiz) | `etki` | not |
|---|---|---|---|---|---|
| `yurur` | fiziksel | hedef ya da yon, olcu | `walks {olcu} toward the {hedef}` | `ozne.isaret` | "takes N steps" yazılmaz: `take` yasak (RE). ZN §3.7 örneği bu yüzden düzeltilmeli |
| `doner` | fiziksel | govde, yon ya da hedef, olcu | `turns the {govde} {olcu} toward the {hedef}` | `ozne.yuz_yonu` | |
| `uzanir` | fiziksel | govde (sag_kol/sol_kol), hedef, olcu | `extends the {empty?} {side} arm toward the {hedef}, fingers stopping {olcu} above it` | `ozne.<el>.yer` | |
| `kavrar` | fiziksel | govde (el), el_sekli, hedef | `the thumb and index finger close around the {hedef}, the other three fingers stay curled` (kiskac) | `nesne.kimde/el`, `<el>.tutar/sekil` | OG ve daha genişse BAYRAK → ekleme planına böl (ZN §3.5) |
| `kaldirir` / `indirir` | fiziksel | govde ya da nesne, olcu, hedef | `lifts the {nesne} {olcu}` / `lowers the {nesne} onto the {hedef}` | nesne konumu | |
| `birakir` | fiziksel | govde, hedef | `opens the fingers and releases the {nesne} onto the {hedef}` | `nesne.nerede`, `<el>.tutar = null` | |
| `iter` / `ceker` | fiziksel | govde, hedef, olcu | `pushes / pulls the {hedef} {olcu} with the {side} hand` | `kapi.durum` vb. | "opens the door" yasak; açma biçimi yazılır (RE notu) |
| `el_kaydirir` | fiziksel | govde, yon, hedef, olcu | `the {side} hand slides {olcu} {yon} along the {zemin} to the {hedef}` | `<el>.yer` | |
| `diz_coker` / `ayaga_kalkar` / `oturur` | fiziksel | (hedef) | `kneels on one knee` / `rises to standing` / `sits down on the {hedef}` | `poz` | |
| `kadraja_girer` / `kadrajdan_cikar` | fiziksel | yon | `enters from frame left` / `exits frame right` | kadraj listesi | A2 `giris_cikis` |
| `bakis_kaydirir` | mikro | hedef | `eyes shift to the {hedef}` | `bakis` | ≥ 0,5 sn tutulur (RE `bakis_tutma_min_sn`) |
| `cene_kaldirir`, `cene_sikar`, `yutkunur`, `nefes_verir`, `kas_kaldirir`, `goz_kisar`, `basini_sallar` | mikro | — | `lifts the chin slightly` · `the jaw tightens, mouth closed` · `swallows once, mouth closed` … | — | Tepki planı eki her zaman: `listens silently, mouth closed` (ZN §3.5) |
| `konusur` | konusma | teslim | `{Ad} {teslim_en}: "{metin}"` | — | Konuşma ile fiziksel adım örtüşmez (ZN §2.3) |
| `boyun_uzatir`, `kanat_acar`, `kuyruk_kaydirir`, `bas_egir` | fiziksel (yaratık) | hedef/olcu | `stretches the neck toward the {hedef}, nostrils flaring` … | — | Yaratık adı + "dragon/creature"; "baby / little" yasak (DR) |

### 5.6 Tam örnek: S12 "Kapıdaki kaptan" (EMBERFALL dünyası)
Kurgu: Gece. Mara kulübenin kapısını yarı açık tutuyor. Kaptan Voss dışarıda, sol elinde meşale. Ember içeride,
odun yığınının arkasında saklı; seyirci bunu biliyor (ironi). 7 kurulum, 16 plan hedefi.
Aşağıdaki örnekte mekân, sahne ve 3 plan tam yazıldı: diyalog-OU, tepki, ekleme. Kalan planlar tabloda.

```json
{
 "film": "EMBERFALL_FILM1",
 "stil_eki": "cinematic film still, photorealistic, anamorphic lens, 4K",
 "karakterler": {
  "mara": {"ref": "01_KARAKTERLER/mara.jpg", "ses": "<voice_id>", "ses_adi": "Meaghan",
           "evren": "EVREN/EMBERFALL/KARAKTERLER/mara.json"},
  "voss": {"ref": "01_KARAKTERLER/voss.jpg", "ses": "<voice_id>", "ses_adi": "Gravel Midnight",
           "evren": "EVREN/EMBERFALL/KARAKTERLER/voss.json"}
 },
 "mekanlar": {
  "mara_kulubesi": {
   "evren": "EVREN/EMBERFALL/MEKANLAR/mara_kulubesi/",
   "kroki": {
    "birim": "metre",
    "yonler": "x = dogu, y = kuzey; yon_derece 0 = kuzey, 90 = dogu (pusula)",
    "sinir": [[0, -4], [5, 4]],
    "duvarlar": [
     {"id": "guney_duvar", "a": [0, 0], "b": [5, 0], "aciklik": [{"id": "kapi", "x": [2.0, 3.0]}]},
     {"id": "bati_duvar", "a": [0, 0], "b": [0, 4], "aciklik": [{"id": "pencere", "y": [2.0, 3.0]}]},
     {"id": "kuzey_duvar", "a": [0, 4], "b": [5, 4]},
     {"id": "dogu_duvar", "a": [5, 0], "b": [5, 4]}
    ],
    "ogeler": [
     {"id": "kapi", "tur": "kapi", "konum": [2.5, 0.0], "mentese": "bati_kasa", "acilis": "iceri", "varsayilan": "kapali"},
     {"id": "surgu", "tur": "kilit", "konum": [3.0, 0.1], "not": "dogu kasanin ic yuzunde demir surgu, yuvarlak topuzlu"},
     {"id": "ocak", "tur": "ocak", "konum": [4.0, 3.8]},
     {"id": "odun_yigini", "tur": "esya", "konum": [4.7, 1.2]},
     {"id": "basamak", "tur": "zemin", "konum": [2.5, -1.0], "not": "dis, karli tek basamak"}
    ],
    "isaretler": {
     "M1": {"konum": [2.5, 0.0], "ad": "kapi araligi (esik)"},
     "M2": {"konum": [2.5, -1.2], "ad": "basamak alti, disarida"},
     "M3": {"konum": [4.0, 3.0], "ad": "ocak onu"},
     "M4": {"konum": [4.7, 1.2], "ad": "odun yigini arkasi"}
    },
    "isik_kaynaklari": [
     {"id": "ocak_atesi", "konum": [4.0, 3.8], "tur": "ates", "renk": "sicak", "varsayilan": "yanik"},
     {"id": "ay", "konum": "gok_guneybati", "tur": "ay", "renk": "soguk", "varsayilan": "acik"}
    ]
   },
   "kurulumlar": {
    "K1": {"konum": [1.0, -0.9], "yon_derece": 75, "yukseklik": "goz", "lens_mm": 28, "varsayilan_kadraj": "OG",
           "ebeveyn": "mekan_karti:dis_guneybati", "not": "disaridan ikili konum plani"},
    "K2": {"konum": [2.0, -1.9], "yon_derece": 24, "yukseklik": "goz", "lens_mm": 50, "varsayilan_kadraj": "OU",
           "ebeveyn": "K1", "not": "Voss'un SOL omzu ustunden Mara"},
    "K3": {"konum": [2.0, 0.6], "yon_derece": 157, "yukseklik": "goz", "lens_mm": 50, "varsayilan_kadraj": "OU",
           "ebeveyn": "mekan_karti:ic_guney", "not": "Mara'nin SAG omzu ustunden Voss (ters aci)"},
    "K4": {"konum": [1.8, -1.0], "yon_derece": 43, "yukseklik": "goz", "lens_mm": 85, "varsayilan_kadraj": "Y",
           "ebeveyn": "K2", "not": "Mara tekli"},
    "K5": {"konum": [1.7, -0.2], "yon_derece": 135, "yukseklik": "goz", "lens_mm": 85, "varsayilan_kadraj": "Y",
           "ebeveyn": "K3", "not": "Voss tekli"},
    "K6": {"konum": [2.1, 0.5], "yon_derece": 114, "yukseklik": "goz", "lens_mm": 85, "varsayilan_kadraj": "D",
           "ebeveyn": "K3", "not": "dogu kasa ici, surgu (ekleme)"},
    "K7": {"konum": [3.5, 2.0], "yon_derece": 124, "yukseklik": "alcak", "lens_mm": 35, "varsayilan_kadraj": "O",
           "ebeveyn": "mekan_karti:ic_dogu", "not": "odun yigini (ironi araya kesmesi); eksen sahnesi disi"}
   }
  }
 },
 "sahne_gruplari": {
  "S12": {
   "hikaye_partisi": 1, "mekan": "mara_kulubesi",
   "zaman": {"gun_saati": "gece", "hava": "hafif_kar"},
   "sahne_tipi": "diyalog", "sure_hedef_sn": 95, "plan_hedef": 16, "kalip": "yukselen_diyalog",
   "sahne_degeri": {"bas": "Mara guvende: kapi aralik, Voss disarida", "son": "Voss supheli, iceri adim atiyor"},
   "eksen": ["mara", "voss"], "kamera_tarafi": "bati",
   "kurulumlar": ["K1", "K2", "K3", "K4", "K5", "K6", "K7"],
   "isik": {"ana": "mesale", "dolgu": "ay", "arka": "ocak_atesi"},
   "yasaklar": ["ikinci_ates_kaynagi", "ucuncu_kisi", "acik_pencere"],
   "giris_durumu": {
    "varliklar": {
     "mara": {"mekan": "mara_kulubesi", "isaret": "M1", "poz": "ayakta", "yuz_yonu": "guney",
              "bakis": {"hedef": "voss"}, "kostum": "mara_k1", "kostum_durumu": ["kapusonu_inik", "eldivensiz"],
              "sol_el": {"tutar": null, "yer": "dogu_kasa_ic", "sekil": "tutus_tam"},
              "sag_el": {"tutar": null, "yer": "kapi_kenari", "sekil": "tutus_tam"}},
     "voss": {"mekan": "mara_kulubesi", "isaret": "M2", "poz": "ayakta", "yuz_yonu": "kuzey",
              "bakis": {"hedef": "mara"}, "kostum": "voss_k1", "kostum_durumu": ["migfer_takili"],
              "sol_el": {"tutar": "mesale", "yer": "omuz_hizasi", "sekil": "tutus_tam"},
              "sag_el": {"tutar": null, "yer": "yanda", "sekil": "serbest"}},
     "ember": {"mekan": "mara_kulubesi", "isaret": "M4", "poz": "comelmis", "gorunur": false}
    },
    "nesneler": {
     "mesale": {"kimde": "voss", "el": "sol", "durum": "yanik"},
     "kapi": {"durum": "yari_acik"},
     "surgu": {"durum": "acik"},
     "ocak_atesi": {"durum": "yanik"}
    }
   },
   "cikis_durumu": {"varliklar": {"voss": {"isaret": "M1"}, "mara": {"isaret": "M1_geri"}},
                    "nesneler": {"kapi": {"durum": "tam_acik"}}},
   "ana_kareler": {"K1": 120, "K2": 121, "K5": 122, "K3": 123, "K6": 124},
   "_not": "ana_kareler kamera_agaci.py ile derlenir"
  }
 },
 "sahneler": [
  {
   "no": 121, "sira": 121, "parti": 1,
   "referans": ["mara", "voss"],
   "gorsel_istem": "(istem_derle.py doldurur)", "gorsel_istem_yedek": "(istem_derle.py doldurur)",
   "hareket_istem": "(istem_derle.py doldurur)", "hareket_istem_yedek": "(istem_derle.py doldurur)",
   "bitis_karesi": null, "motor": "flow",
   "replik": {"karakter": "mara", "metin": "It's late, Captain. What do you want?",
              "cumleler": [{"en": "It's late, Captain.", "tr": "Saat geç oldu, Kaptan."},
                           {"en": "What do you want?", "tr": "Ne istiyorsun?"}]},
   "kullanim": {"bas": 0.6, "sure": 3.6},
   "amac": "Mara soğukkanlı rol yapıyor", "duygu": "gerilim",
   "cekim": {
    "kod": "S12-P02", "sahne_grubu": "S12", "plan_tipi": "diyalog", "klip_sn": 8, "kaynak_klip": null,
    "kamera": {"kurulum": "K2", "kadraj": "OU", "aci": "goz_hizasi", "lens_mm": 50,
               "hareket_tipi": "sabit", "hareket_yonu": null, "odak": "mara"},
    "eksen_gecis": false,
    "kadrajdakiler": [
     {"id": "mara", "olcek": "OY", "yuz_acisi": "3/4", "bakis": {"hedef": "voss"}, "konusur": true, "kimlik_demiri": true},
     {"id": "voss", "olcek": "on_plan_omuz", "yuz_acisi": "sirt", "bakis": {"hedef": "mara"}, "konusur": false}
    ],
    "baslangic_durumu": "miras",
    "eylem_zinciri": [
     {"bas": 0.5, "bit": 2.0, "ozne": "mara", "tur": "mikro", "fiil": "cene_kaldirir", "govde": "bas", "olcu": "hafif"},
     {"bas": 2.0, "bit": 5.4, "ozne": "mara", "tur": "konusma", "fiil": "konusur", "teslim": "soguk"}
    ],
    "replik_kaynagi": "klip",
    "ekran_disi_ses": null,
    "bitis_durumu": "derlenir",
    "zincir": {"gecis_turu": "eylem_kesme", "onceki_plan": 120,
               "baslangic_karesi": {"kaynak": "ana_kare", "ebeveyn": "K1@120"},
               "bitis_karesi": null, "derinlik": 0},
    "kesme": {"tip": "L", "nokta_sn": 4.2, "ses_tasma_sn": 1.2},
    "isik_degisimi": null,
    "yasaklar": [],
    "ekranda_bilgi": "Mara kapıyı yarı açık tutuyor ve Kaptan'a soğuk davranıyor; onu içeri almak istemiyor.",
    "risk_uretim": "orta",
    "_derlenir": {
     "kadraj_konumu": {"mara": "sol_ucte_bir", "voss": "sag_on"},
     "kamera_tarafi": "bati",
     "bakis_kadrajda": {"mara": "kadraj_sagi"},
     "isik_kadrajda": {"ana": "on_sol (mesale)", "arka": "orta (ocak, kapi icinden)", "dolgu": "soguk ay"},
     "replik_zaman": {"bas": 2.0, "bit": 5.4},
     "diyalog_sure_formul_sn": 3.95,
     "ayna_yasak": true
    }
   },
   "zanaat": {"hedef_duygu": "gerilim", "yogunluk": 6, "ironi": {"id": "ir_ember_ic", "rol": "surdur"}},
   "ses": "(ses uzmanı doldurur)",
   "uretim": {}, "denetim": {"G1": null, "V1": null, "V2": null, "K1": null}
  },
  {
   "no": 122, "sira": 122, "parti": 1,
   "referans": ["voss"],
   "gorsel_istem": "(derlenir)", "hareket_istem": "(derlenir)",
   "bitis_karesi": null, "motor": "flow",
   "replik": null,
   "kullanim": {"bas": 0.5, "sure": 3.0},
   "amac": "Voss bir şeyden şüpheleniyor", "duygu": "gerilim",
   "cekim": {
    "kod": "S12-P03", "sahne_grubu": "S12", "plan_tipi": "tepki", "klip_sn": 8, "kaynak_klip": null,
    "kamera": {"kurulum": "K5", "kadraj": "Y", "aci": "goz_hizasi", "lens_mm": 85,
               "hareket_tipi": "yavas_ileri", "hareket_yonu": null, "odak": "voss"},
    "eksen_gecis": false,
    "kadrajdakiler": [
     {"id": "voss", "olcek": "Y", "yuz_acisi": "3/4", "bakis": {"hedef": "mara"}, "konusur": false, "kimlik_demiri": true}
    ],
    "baslangic_durumu": "miras",
    "eylem_zinciri": [
     {"bas": 0.5, "bit": 2.0, "ozne": "voss", "tur": "mikro", "fiil": "bakis_kaydirir", "govde": "gozler",
      "hedef": "ocak_atesi", "etki": {"voss.bakis": {"hedef": "ocak_atesi"}}},
     {"bas": 2.0, "bit": 3.5, "ozne": "voss", "tur": "mikro", "fiil": "cene_sikar", "govde": "bas"}
    ],
    "replik_kaynagi": null,
    "ekran_disi_ses": {"karakter": "mara", "kaynak": "klip:121", "bas_sn": 0.0, "sure_sn": 1.2, "not": "121'in L taşması"},
    "bitis_durumu": "derlenir",
    "zincir": {"gecis_turu": "eylem_kesme", "onceki_plan": 121,
               "baslangic_karesi": {"kaynak": "ana_kare", "ebeveyn": "K3@123"},
               "bitis_karesi": null, "derinlik": 0},
    "kesme": {"tip": "duz", "nokta_sn": 3.5, "ses_tasma_sn": 0.0},
    "ekranda_bilgi": "Voss, Mara'nın arkasında, kulübenin içindeki ateşe bakıyor; bir şeyden şüpheleniyor.",
    "risk_uretim": "dusuk",
    "_derlenir": {
     "kadraj_konumu": {"voss": "sag_ucte_bir"},
     "bakis_kadrajda": {"voss_bas": "kadraj_solu", "voss_bit": "kadraj_solu (daha yana, içeri)"},
     "isik_kadrajda": {"ana": "sag_alt (mesale, kadraj disi)", "dolgu": "soguk ay"},
     "ayna_yasak": true
    }
   },
   "zanaat": {"hedef_duygu": "gerilim", "yogunluk": 7, "merak_ac": ["m07"]},
   "uretim": {}, "denetim": {}
  },
  {
   "no": 124, "sira": 124, "parti": 1,
   "referans": ["mara"],
   "gorsel_istem": "(derlenir)", "hareket_istem": "(derlenir)",
   "bitis_karesi": null, "motor": "flow",
   "replik": null,
   "kullanim": {"bas": 1.0, "sure": 2.4},
   "amac": "Mara gizlice sürgüye uzanıyor (kurulum)", "duygu": "gerilim",
   "cekim": {
    "kod": "S12-P05", "sahne_grubu": "S12", "plan_tipi": "ekleme", "klip_sn": 8, "kaynak_klip": null,
    "kamera": {"kurulum": "K6", "kadraj": "D", "aci": "goz_hizasi", "lens_mm": 85,
               "hareket_tipi": "sabit", "hareket_yonu": null, "odak": "surgu"},
    "eksen_gecis": false,
    "kadrajdakiler": [
     {"id": "mara", "olcek": "el", "yuz_acisi": "gorunmez", "konusur": false, "gorunen": ["sol_el", "sol_kol_yeni"]}
    ],
    "baslangic_durumu": "miras",
    "eylem_zinciri": [
     {"bas": 0.5, "bit": 2.5, "ozne": "mara", "tur": "fiziksel", "fiil": "el_kaydirir", "govde": "sol_el",
      "yon": "asagi", "hedef": "surgu", "olcu": "15cm",
      "etki": {"mara.sol_el.yer": "surgu_topuzu", "mara.sol_el.sekil": "serbest"}},
     {"bas": 2.5, "bit": 4.0, "ozne": "mara", "tur": "fiziksel", "fiil": "kavrar", "govde": "sol_el",
      "el_sekli": "kiskac", "hedef": "surgu",
      "etki": {"mara.sol_el.sekil": "kiskac", "mara.sol_el.yer": "surgu_topuzu"}}
    ],
    "replik_kaynagi": null,
    "ekran_disi_ses": {"karakter": "voss", "kaynak": "klip:123", "bas_sn": 0.0, "sure_sn": 1.0, "not": "123'ün L taşması"},
    "bitis_durumu": "derlenir",
    "zincir": {"gecis_turu": "araya_kesme", "onceki_plan": 123,
               "baslangic_karesi": {"kaynak": "ana_kare", "ebeveyn": "K3@123"},
               "bitis_karesi": null, "derinlik": 0},
    "kesme": {"tip": "eylem", "nokta_sn": 3.4, "ses_tasma_sn": 0.0},
    "ekranda_bilgi": "Kapının iç tarafında demir bir sürgü var; Mara gizlice ona uzanıyor.",
    "risk_uretim": "orta",
    "_derlenir": {"kostum_capasi_el": "sol el: yalın el, kürk yakalı kahverengi deri ceketin kolu", "ayna_yasak": true}
   },
   "zanaat": {"kurulum": ["kur_surgu"], "ironi": {"id": "ir_ember_ic", "rol": "surdur"}, "yogunluk": 7},
   "uretim": {}, "denetim": {}
  }
 ]
}
```

**`kroki.py`'nin bu örnekte hesapladıkları** (tanjant izdüşümü: kadraj konumu = tan(açı) / tan(yarım görüş açısı);
−1/3'ten küçükse sol üçte bir, +1/3'ten büyükse sağ üçte bir. Bu hesap betiğin yapacağı işin aynısı; sayılar elle değil hesapla bulundu):

| Kurulum | Lens / görüş | Mara (M1) | Voss (M2) | Meşale | Ocak | Eksen tarafı |
|---|---|---|---|---|---|---|
| K1 | 28 mm / 65,5° | −16° → −0,44 **sol** | +26° → +0,77 **sağ** | +0,86 sağ | kadraj dışı | batı |
| K2 | 50 / 39,6° | −0,45 **sol** | +0,57 **sağ (ön plan)** | −0,39 sol (önde, ana ışık sol-önden) | −0,23 orta (kapıdan arka ışık) | batı |
| K3 | 50 / 39,6° | −0,84 **sol (ön plan omuz)** | +0,36 **sağ** | +0,83 sağ | arkada | batı |
| K4 | 85 / 23,9° | −0,66 **sol** | kadraj dışı (sağ) | dışı, sağ | dışı | batı |
| K5 | 85 / 23,9° | kadraj dışı (sol) | +0,52 **sağ** | dışı (sağ-alt) | arkada | batı |

Hesaptan çıkan dersler:
- Bütün kurulumlarda Mara solda, Voss sağda kalıyor. Kural ZN §3.3'teki "A solda sağa bakar" ile tutarlı. 180° kâğıtta kanıtlandı.
- K2'den K4'e doğrudan kesilemez. Mara'ya bakış açısı farkı yalnız 20°, ölçek farkı OY→Y 1 kademe. RE `aci_min_fark_derece` 30 ve `olcek_kademe_min_fark` 2 sınırlarının ikisi de sağlanmıyor. Araya mutlaka ters açı (K3/K5) girer. `kroki.py` bu çifti "yasak ardışık" listesine yazar.
- K2'de odun yığını (M4) görüş konisinde, ama güney duvarının arkasında kalıyor. Görüş hattı denetimi bunu "görünmez" sayar. Bu yüzden duvarlar krokiye girer.

**Kalan planlar (özet):**

| no | kod | kurulum / kadraj | tip | özet |
|---|---|---|---|---|
| 120 | S12-P01 | K1 / OG (IK, sessiz) | kurulus | Konum planı. [0,5–2,0] Voss meşaleyi omuz hizasına kaldırır; [2,0–3,5] Mara sağ eliyle kapıyı 10 cm daha kapatır. Aynı anda tek özne hareket eder |
| 123 | S12-P04 | K3 / OU (Mara'nın sağ omzu) | diyalog | Voss: "Smoke from your chimney. On a night you swore you had no wood left." 14 kelime → 0,4 + 5,6 + 0,25 + 0,5 = 6,75 sn ≤ 8 sn klip (ZN §2.3). L taşma 1,0 sn → P124 |
| 125 | S12-P06 | K4 / Y | tepki | Mara yutkunur, ağız kapalı, gözler kısa bir an sola-içeri kayar (ironi; bakış ≥ 0,5 sn) |
| 126 | S12-P07 | K7 / O (alçak) | ekleme (araya kesme) | Odun yığınının arkasından pullu bir kuyruk ucu 20 cm sağa kayıp kaybolur. Eksen sahnesi dışında, ayrı ironi zinciri |

**Derlenen istemler** (`istem_derle.py` çıktısı; kimlik dizeleri evren kütüphanesinden kelimesi kelimesine gelir,
burada `{MARA_KIMLIK}` diye kısaltıldı):

- P121 `gorsel_istem` (başlangıç anı, durağan):
  `Over-the-shoulder medium close-up, eye-level, 50mm lens, night. Foreground on frame right, softly out of focus: Voss seen from behind — {VOSS_KIMLIK} — his left shoulder and the back of his helmet, a burning torch held in his left hand at shoulder height. On the left third of frame: Mara — {MARA_KIMLIK} — standing in the half-open doorway of a log cabin, body facing the camera at three-quarter angle, looking toward frame right at Voss, her right hand gripping the edge of the wooden door, the door leaf on frame left, her left hand hidden behind the door frame. Warm torchlight on her face from the front-left; warm hearth glow behind her inside the cabin; cold moonlight on the snow. Light snow falling. {STIL_EKI}`
- P121 `hareket_istem` (iki kişi kadrajda → adlar yazılır):
  `Static over-the-shoulder shot. 0.5-2s: Mara lifts her chin slightly, eyes fixed on Voss. 2-5.4s: Mara says coldly: "It's late, Captain. What do you want?" Voss stays still, seen from behind, silent. 5.4-8s: Mara holds still, mouth closed. Sound: wind over snow, torch flame crackling. No music.`
- P122 `hareket_istem` (tek kişi → öznesiz; H/video-istem-kurali):
  `Slow push-in, close-up. 0.5-2s: listens silently, mouth closed; eyes shift toward frame left, past the doorway into the cabin. 2-3.5s: the jaw tightens, mouth still closed. 3.5-8s: holds still. Sound: wind, torch flame crackling. No music.`
- P124 `hareket_istem` (ekleme, yalnız el → "the left hand"):
  `Static macro insert. 0.5-2.5s: the left hand slides 15 cm down the inner side of the wooden door frame to the round knob of an iron bolt. 2.5-4s: the thumb and index finger close around the knob, the other three fingers stay curled. 4-8s: holds still. Sound: fabric rustle, faint creak of wood, muffled wind outside. No music.`

Sound satırı ses uzmanının `ses` alanından gelir; burada yer tutucu olarak yazıldı.

### 5.7 Miras, derleme ve geriye uyumluluk kuralları
1. **Miras:** `baslangic_durumu: "miras"` yazılırsa kod, önceki planın (`zincir.onceki_plan`) hesaplanmış bitiş durumunu alır.
   `{"fark": {...}}` yalnız açıklanan farkları uygular. Farklar yalnız şu durumlarda geçerlidir: `zaman_atlama`, `yeni_sahne` ya da kadraj dışında olduğu açıklanan bir değişiklik.
   Gerekçesiz fark HATA'dır. Bu kural, zinciri **yazım biçimiyle** zorunlu kılar.
2. **Araya kesme ve paralel kurgu:** `araya_kesme` planının `onceki_plan`'ı hikâye zamanında hemen önceki plandır.
   Dünya defteri ise tek ve hikâye zamanına göre sıralıdır. Ember'in kuyruk planı (126) Mara ile Voss'un durumunu değiştirmez, yalnız Ember'inkini değiştirir.
   Geri dönüşler (flashback) ayrı bir zaman çizgisinde tutulur: `zaman_cizgisi: "gecmis_1"`. Ana defteri etkilemez.
3. **Klip bölme:** `kaynak_klip: 121` olan plan kendi görselini ve videosunu üretmez. Başlangıç durumu, kaynak klibin zincirinde `kullanim.bas` anına kadar adımların uygulanmasıyla hesaplanır. Bölünen iki parça arasında ≥ 0,4 sn atlanır (RE `klip_bolme_atlama_min_sn`).
4. **Derleme tek yönlüdür:** `cekim` → istemler. `istem_derle.py` her derlemede istem metninin özetini (hash) `uretim.istem_ozeti`'ne yazar.
   Biri istemi elle değiştirmişse sonraki derleme bunu fark eder, uyarır ve üstüne yazmaz. Kalıcı istisna yalnız `istem_elle` alanıyla yapılır.
5. **Geriye uyumluluk:** `cekim` alanı olmayan planlar (ORNEK_3_SAHNE, eski filmler) bugünkü gibi çalışır.
   `plan_denetim.py` onlara yalnız eski kuralları uygular. `film.py` bu filmlerde `yonetmen` aşamasını "eski biçim" diye atlar.
6. **Üst düzey `bitis_karesi`** (memmet'in bugün okuduğu alan) `zincir.bitis_karesi.kaynak == "sonraki_baslangic"` ise o planın `no`'su olarak derlenir.
   `ozel` bitiş karesi için `SIRALI_GORSEL/NNN_son.jpg` kullanılır. Bunun için memmet'te küçük bir değişiklik gerekir (§6).

---

## 6. Yazılması/değişmesi gereken kod (araç adı, ne yapar, girdi/çıktı, öncelik)

Ortak kurallar:
- Hepsi `YZ_FILM/ARACLAR/` altında, mevcut stilde yazılır: Türkçe docstring + kullanım, `sys.stdout.reconfigure`, `_RAPOR`/`RAPORLAR` çıktısı, çıkış kodu 0 / 1 / 2.
- Python 3.10, Windows. Ağ yok, kredi yok. P1 araçlarının hiçbiri GPU ya da yeni ağır bağımlılık istemez; yalnız PIL ve numpy kullanır (ikisi de kurulu).
- Öncelik: **P1** = görsel aşamasından önce şart · **P2** = ilk video partisinden önce · **P3** = ilk filmden sonra.

### 6.1 Yeni araçlar

| Araç | Ne yapar | Girdi → Çıktı | Öncelik |
|---|---|---|---|
| `veri/fiil_sozlugu.json`, `veri/plan_sozlukleri.json` | Fiil, kadraj, poz, el şekli, yüz açısı, geçiş ve kesme sözlükleri + EN şablonları | — | P1 |
| `plan_sema.py` | `cekim`, sahne ve mekân alanlarının şema ve sözlük denetimi. `jsonschema` (saf Python) varsa onu kullanır, yoksa yerleşik basit doğrulayıcı | `SAHNELER.json` / `30_PLANLAR/*.json` → `RAPORLAR/sema.json` | P1 |
| `kroki.py` | Geometri motoru: tanjant izdüşümüyle kadraj konumu, eksen tarafı, duvarla görüş hattı, bakışın ve ışığın kadrajdaki yönü, göz hizası farkı (aşağı/yukarı bakış), kurulum çiftleri arası açı ve ölçek farkı ("yasak ardışık" listesi). `--karsilikli A B --taraf bati`: iki işaret ve eksen tarafından standart karşılıklı çekim kurulumlarını (ikili konum, iki OU, iki tekli) **önerir** (R4). `--ciz` (PIL): işaretler, eksen, görüş konileri; mekân ve sahne PNG'leri | `20_KROKILER.json` + planlar → `_derlenir` alanları, `KROKI/*.png`, `RAPORLAR/kroki.json` | P1 |
| `durum_defteri.py` | Miras ve fark çözümü; etkilerin katlanması (fold); bitiş durumunun hesabı; klip bölmede ara an durumu; olgu zıplaması; "görünmesi gerekip listede olmayan kişi" (geometri + defter); sahne sözleşmesi eşleşmesi. Ayrıca `durum_sorulari(plan, an)` API'si: durumdan VLM için **seçenekli sorular** üretir. Örnek: `Which hand holds the lantern? A) left B) right C) none D) not visible` (A2 §5) | planlar → `_YONETMEN/DUNYA_DEFTERI.json`, `RAPORLAR/K0_defter.json` | P1 |
| `plan_denetim.py` | ZN Z0 #4–6, #11–19 ve §7'deki Y kuralları. Modlar `--dokum`, `--sahne S07`, `--tum`. Eşikleri `ritim_esikleri.json`'dan okur | → `RAPORLAR/Z0_plan.json`, `YENIDEN_YAZ.json`; çıkış 1 = HATA | P1 |
| `istem_derle.py` | `gorsel_istem` (anlık görüntü), `hareket_istem` (saniyeli adımlar, tek kişide öznesiz, iki kişide adlı), `*_yedek`, bitiş karesi istemi. Kimlik dizeleri, ışık cümlesi, en çok 2 mekân çapası, film `stil_eki`, onaylı ders ekleri. `--zaman-bicimi aralik\|sira` (§9 açık soru 2). İstem özetini (hash) yazar ve elle yapılan değişikliği fark eder | `SAHNELER.json` → aynı dosya + `_RAPOR/ISTEM_DERLEME.txt` | P1 |
| `plan_birlestir.py` | `30_PLANLAR/S*.json` → `SAHNELER.json`. `kod → no` eşlemesini `_YONETMEN/NO_ESLEME.json`'da kalıcı tutar: eski planın no'su değişmez, yeni plan max+1 alır. `sira`, üretim partisi (20, sahne sınırından; CI kural 5), `kaynak_klip` | → `SAHNELER.json` | P1 |
| `yonetmen_paket.py` | `--brifing` ve `--sahne` paketleri: ajan bağlamını küçük ve tam tutar | → `_YONETMEN/00_BRIFING.md`, `PAKET/S*.md` | P1 |
| `cekim_listesi.py` | İnsan ve eleştirmen için okunur çekim listesi: sahne başına tablo + kroki PNG + derlenmiş istemler | → `_YONETMEN/CEKIM_LISTESI_P*.md` | P1 |
| `kamera_agaci.py` | Ana kare belirleme. Görsel üretim sırası: topolojik; önce mekân kartı → ana kareler → türevler. Ebeveyn yeniden üretilince çocukları "bayat" işaretler. Gemini paketlerini bu sıraya göre gruplar (paket içeriği görsel uzmanının) | → `_YONETMEN/KAMERA_AGACI.json`, `sahne_gruplari.*.ana_kareler` | P1 |
| `zincir_kare.py` | Mod A: Bitir eşleme listesi ve Memmet yükleme listesi. Mod B: son kare çıkarma (`ffmpeg -sseof -0.1 -frames:v 1`, A2 §2.3), zincir derinliği sayacı | → `SIRALI_GORSEL/NNN.jpg` (Mod B), `_RAPOR/ZINCIR.json` | P2 |
| `zincir_olcum.py` | Video sonrası **eylem zinciri uyumu**: (a) bitiş anı karesinde (`bit` + 0,5 sn) durum soruları, VLM, kör biçimde (A1 B4 ARIS yöntemi); (b) MediaPipe el noktaları ve el ayrımı (ayna düzeltmesiyle, A2 §4) ile elin hedef bölgeye ulaşıp ulaşmadığı; (c) her adım penceresinde kare farkı enerjisi, yani adımın kendi penceresinde mi olduğu. V2 ile aynı kare örneklerini kullanır | `SIRALI_VIDEO/NNN.mp4` + plan → `RAPORLAR/V3_zincir.json`, `YENIDEN_URET.json` | P2 |
| `ders_cikar.py` | Plan özellikleri × hata türü tablosu. Aynı birleşim ≥ 3 kez başarısızsa `aday` ders | raporlar → `DERS_DEFTERI.json` | P3 |

### 6.2 Değişecek mevcut kod

| Dosya | Değişiklik | Öncelik |
|---|---|---|
| `film.py` | `senaryo` ile `istem_denetim` arasına deterministik bir `yonetmen` aşaması: `plan_birlestir → durum_defteri → kroki --denetle → plan_denetim --tum → istem_derle`. İmza: `30_PLANLAR/`, `20_KROKILER.json`, `10_SAHNE_DOKUMU.json`. Ajan işleri beceride kalır. Aşama yalnız deftere ve kapıya bakar | P1 |
| `istem_denetim.py` | Yeni kurallar: yasak sonuç fiilleri (RE `yasak_sonuc_fiilleri`); `left/right` sözcüğü `her/his/its/the … /frame` olmadan geçiyorsa UYARI; hareket istemi kelime sınırı (§7); `cekim`'li planda istem özeti uyuşmazsa UYARI | P1 |
| `memmet.py` | (a) `cekim.kaynak_klip` dolu planları atla: bugünkü `motor != flow` atlamasının yanına bir satır. (b) `bitis_karesi` için `NNN_son.jpg` dosya adını da kabul et. (c) `baslangic_karesi.kaynak == "son_kare"` olan planı, kaynak video V1 ve V2'den geçmeden kuyruğa alma. Tempo ve uyarı davranışına **dokunulmaz** | P2 |
| `capcut_film.py` | Bugün klibi baştan sona koyuyor; `kullanim{bas,sure}` kullanılmıyor (kod okundu). Şunlar eklenmeli: `kullanim` penceresi, `sira`, `kaynak_klip` (kaynak dosya + pencere), `kesme.ses_tasma_sn` (L/J). Kurgu uzmanıyla birlikte | P2 |
| `izleme_paketi.py` | Sıralama `sira` ile. Kareler klibin tamamından değil `kullanim` penceresinden alınır. `kaynak_klip` planında kaynak video kullanılır | P2 |
| `seslendir.py` | Whisper araması planın `replik_zaman` penceresinde yapılır (DR: "aynı klip iki plana bölününce" dersi). Ses uzmanının alanı, bağımlılık olarak yazıldı | P2 |
| `saglayicilar/sahte.py` | Sahte görsel, kroki hesabındaki kadraj konumlarına etiketli kutular çizer ("MARA" solda, "VOSS" sağda). G1'in kadraj sırası mantığı ağsız test edilebilir | P2 |
| `ritim_esikleri.json` | §7'deki `plan_*` anahtarları eklenir. ZN'nin "çelişkide JSON geçerli" kuralı sürer | P1 |
| `testler/test_plan_dili.py` + `FILMLER/ORNEK_3_SAHNE_CEKIM/` | `cekim` alanlı 3 plan + kroki. Bozuk varyantlar: eksen ihlali, nesne zıplaması, yasak fiil, adım örtüşmesi, konuşma ile fiziksel adımın örtüşmesi, K2→K4 ardışığı, konuşan plana L taşması, "chest" içeren şablon. Mevcut `ORNEK_3_SAHNE` ve testi **değişmez** | P1 |

---

## 7. Makinenin denetleyeceği eşikler (kaynağıyla)

**Kodlar:** H = HATA (geçmez), B = BAYRAK (ajan bakar). ZN Z0 #1–20 maddeleri aynen geçerlidir. Aşağıdaki **Y kuralları** onları
plan diline göre ayrıntılandırır ya da yeni kural ekler. Kodlar `plan_denetim.py` raporunda kural numarasıyla görünür.
"Hesap" sütunu, eşiğin `kroki.py` ya da `durum_defteri.py` hesabına dayanıp dayanmadığını söyler.

### 7.1 Atomik eylem zinciri
| # | Ölçü | Eşik | Sonuç | Kaynak / RE anahtarı |
|---|---|---|---|---|
| Y01 | Plandaki adım sayısı (fiziksel + mikro + konuşma; bitişte durup beklemek sayılmaz). İnsansız kuruluş ve geçiş planları hariç | 2–3 | H | kesin karar 2 ("klip başına 2–3 adım"); üst sınır RE `eylem_adim_max`; yeni `plan_adim_min` = 2 |
| Y02 | Konuşmalı planda fiziksel adım; konuşma ile fiziksel adımın zaman örtüşmesi | ≤ 1; 0 | H | RE `eylem_adim_konusmali_max`, ZN §2.3 |
| Y03 | Adım süresi; adımlar arası örtüşme | ≥ 1,5 sn; yok | H | RE `eylem_adim_min_sn`, Z0 #14 |
| Y04 | İlk adımın başlangıcı | ≥ 0,5 sn | B | ZN §2.2 (klibin ilk 0,3–1,0 sn'si durağan), RE `kullanim_bas_varsayilan_sn`; yeni `plan_ilk_adim_min_sn` |
| Y05 | Son adımın bitişi | ≤ klip_sn − 1,0 (8 sn'de 7,0) | H | (hesap) RE `bitis_tutma_sn` 0,5 + `kullanim_son_pay_sn` 0,5 |
| Y06 | Aynı anda hareket eden özne sayısı | ≤ 1 | B | (tahmin; iki kişili klipte eylemler sıralanır) yeni `plan_es_zamanli_ozne_max` |
| Y07 | Fiil sözlükte değil / yasak sonuç fiili | 0 | H | ZN §3.7, RE `yasak_sonuc_fiilleri` |
| Y08 | Fiilin zorunlu parametresi eksik (el, el şekli, hedef, yön, ölçü) | 0 | H | kesin karar 2 ("hangi el, yön, kaç parmak") |
| Y09 | İnce el eylemi (`kavrar`, `birakir`, kilit, düğüm) OG ya da daha geniş kadrajda | 0 | B → eklemeye böl | ZN §3.5 |
| Y10 | Adım `etki`leri ile yazarın beklediği `bitis_durumu` uyuşmazlığı | 0 | H | ZN Z0 #16 |

### 7.2 Durum zinciri ve dünya defteri
| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y11 | `bitis[N]` ≠ `baslangic[N+1]` (olgular; `yeni_sahne` ve `zaman_atlama` hariç) | 0 | H | Z0 #16, A2 K0 |
| Y12 | Gerekçesiz `fark` | 0 | H | yeni (§5.7 #1) |
| Y13 | Sahnenin son planındaki durum ≠ sözleşmedeki `cikis_durumu` | 0 | H | yeni |
| Y14 | Görüş konisinde, görüş hattı açık ve `gorunur` olan kişi `kadrajdakiler`'de yok; ya da listede olup geometriye göre kadraj dışı | 0 | H (hesap) | A2 K0 "kaybolma" + kroki geometrisi |
| Y15 | Nesne `kimde` değişimi etki olmadan | 0 | H | A2 K0 "nesne yolu" |
| Y16 | Nesne `el` değişimi etki olmadan | 0 | H | A2 K0'da BAYRAK. Atomik zincirde her el değişimi bir adım olduğu için HATA'ya yükseltildi |

### 7.3 Kadraj, 180°, bakış, ışık
| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y17 | Kurulum sahnenin `kamera_tarafi`'nda değil ve `eksen_gecis` yok | 0 | H (hesap) | Z0 #17, ZN §3.3 |
| Y18 | Karşılıklı tekli planlarda iki kişinin kadrajdaki bakış yönü zıt değil | 0 | H (hesap) | Z0 #18 |
| Y19 | Ardışık iki planda aynı özneye açı farkı < 30° **ve** ölçek farkı < 2 kademe | 0 | H (hesap) | Z0 #12, RE `aci_min_fark_derece`, `olcek_kademe_min_fark` |
| Y20 | Aynı kurulum art arda | ≤ 2 | B | RE `ayni_kamera_konumu_ardisik_max` |
| Y21 | Konum planı (G/OG/IK) sahnenin ilk N planında | N = 3 (geç girişte 5) | B | RE `sahne_konum_plani_max_sira` |
| Y22 | 90 sn'den uzun sahnede ortada G/OG | var | B | RE `sahne_yeniden_konum_sn` |
| Y23 | Işığın kadrajdaki yönü sahnenin ana kaynağından hesaplanana uymuyor ve `isik_degisimi` yok | 0 | H (hesap) | A2 K0 ışık |
| Y24 | `ayna_yasak` plana ayna düzeltmesi önerisi (elde nesne, asimetrik kostüm) | 0 | H | ZN §3.3 |
| Y25 | Göz yüksekliği farkı > 0,3 m iken bakışta "aşağı/yukarı" eki yok | 0 | B (hesap) | ZN §3.3 bakış çizgisi. Göz yükseklikleri: ayakta 1,6 · oturan 1,2 · diz çökmüş 0,9 · yerde 0,3 m (tahmin); yaratıkta evren kartındaki `goz_yuksekligi_m` |
| Y26 | Yolculuk ve kovalamacada `hareket_yonu` sahnenin `ekran_yonu`'ne uymuyor; arada `doner` adımı yok | 0 | H | ZN §3.3 |
| Y27 | Klipte kamera hareketi; düşük güvenli hareket (yörünge, hızlı) | ≤ 1; yalnız doruk + yedek istemle | H; B | RE `kamera_hareketi_klip_max`, `dusuk_guven_hareketler` |
| Y28 | Kişinin kadrajdaki konumu (tan izdüşümü) yazılan üçte birle aynı | eşit | H (hesap) | yeni. Görüş açısı: (hesap) 2·atan(18/f) |

### 7.4 Konuşma, dudak ve ses köprüleri
| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y29 | Klipte konuşan sayısı; OU'da öndeki kişi sırtı dönük ve sessiz | ≤ 1; evet | H | RE `konusan_karede_max`, ZN K4 |
| Y30 | Replik kelime sayısı | ≤ 16 (8 sn) / ≤ 20 (10 sn) | H | RE `replik_max_kelime_8sn`, `replik_max_kelime` |
| Y31 | Diyalog formülü (ZN §2.3); L kesmede **görüntü süresi + taşma** toplamına uygulanır | ≥ formül | H | ZN §2.3 + yorumum (kurgu uzmanıyla doğrulanacak) |
| Y32 | Konuşan yüzün ölçeği ve açısı | O/OY/Y; `on` ya da `3/4` (≤ 45° yaw); konuşurken CY yok | B | (tahmin) Dudak modelleri ve ses dönüştürme yolu yan profilde zayıf (A3 A2) |
| Y33 | L taşması, konuşanın da görünüp konuştuğu bir plana gidiyor (çift ses) | 0 | H | yeni; BK 5.1 #8'in genişletilmesi |
| Y34 | J kesmesi: sonraki planın konuşanı bu planda görünüyor ve ağzı kapalı | 0 | H | yeni; aynı mantık |
| Y35 | `ekran_disi_ses` olan planda görünen herkeste `listens silently, mouth closed` eki | var | H | BK 5.1 #8, ZN §3.5 |
| Y36 | L taşma / J öne alma süresi | 0,3–2,5 / 0,3–0,8 sn | B | RE `l_kesme_aralik_sn`, `j_kesme_aralik_sn` |

### 7.5 Kurgu bağlantısı, klip bölme, kare zinciri
| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y37 | `kullanim.bas`; `bas + sure` = `kesme.nokta_sn`; `bas + sure` ≤ klip_sn − 0,5 | ≥ 0,3; ±0,05; evet | B; H; B | RE `kullanim_bas_min_sn`, yeni, RE `kullanim_son_pay_sn` |
| Y38 | `kesme.tip = eylem` iken kesme noktasının son adım içindeki yeri | %60–70 | B | ZN §3.4 |
| Y39 | Klip bölmede kaynağın kullanılabilir süresi; parçalar arası atlama | ≥ 6,0 sn; ≥ 0,4 sn | H | RE `klip_bolme_min_kullanilabilir_sn`, `klip_bolme_atlama_min_sn` |
| Y40 | `devam` zinciri derinliği (Mod B, son kareden) | ≤ 2, sonra temiz görselle yeniden demirle | H | A2 §2.3 |
| Y41 | `onceki_bitis` (Mod A) ve Bitir karesi aynı kurulumdan | evet | H | yeni (§8.2-d) |
| Y42 | Yalnız bitiş için üretilen ek görsel (`NNN_son.jpg`) oranı | ≤ %10 plan | B | (tahmin) yükleme sayısı uyarı riski (DR) |
| Y43 | Kamera ağacı derinliği (mekân kartı → plan görseli) | ≤ 3 düğüm | B | (tahmin) her türetmede kayma birikir (A2 §2.3 ile aynı mantık) |

### 7.6 Kimlik, referans, istem
| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y44 | Karakterin sahnedeki ilk görünüşü (`kimlik_demiri`) | ölçek ≥ OY, yüz `on` ya da `3/4` | B | (tahmin) SFace eşiği önden fotoğraf için verilmiş, profilde düşer (A2 §1.1) |
| Y45 | `referans`: kadrajda yüzü ya da bedeni görünen adlı karakterler; sayı | `kadrajdakiler`'den derlenir; ≤ 2 | H | RE `referans_max`, BK 4.1 #7 |
| Y46 | Derlenmiş hareket isteminin kelime sayısı | ≤ 75 | B | (tahmin) "kısa istem" kuralı (H/video-istem-kurali) ile saniyeli adım ihtiyacının dengesi; ilk partide ölçülür |
| Y47 | Çıplak `left/right` (sahiplik ya da `frame` sözcüğü olmadan) | 0 | H | yeni |
| Y48 | Derlenmiş ana istemde filtre kelimesi | 0 | H | DR. `istem_denetim`'de bugün UYARI; derlenen istemde HATA önerilir |
| Y49 | `ekranda_bilgi` boş | 0 | H | ZN §6.1 |

### 7.7 Sahne kapsaması
| # | Ölçü | Eşik | Sonuç | Kaynak |
|---|---|---|---|---|
| Y50 | Diyalog sahnesinde kurulum sayısı | ≥ 3 (ikili/konum + iki taraf) | B | (hesap) ZN §3.3 karşılıklı çekim düzeni; en az sayı (tahmin) |
| Y51 | Diyalog sahnesinde tepki planı. K konuşan plan ve O diğer plan için tepki ≥ ⌈(K + O) / 3⌉ | RE `tepki_orani_min` 0,25 | B | (hesap) 0,25·T ≤ R ve T = K + O + R'den |
| Y52 | J/L oranı (diyalog sahnesi) | ≥ %30 | B | RE `jl_kesme_orani_min` |
| Y53 | Plan sayısı (sahne ve film hedefinden) | ±%15 | B | RE `plan_sayisi_tolerans_oran` |

### 7.8 Görüntü sonrası ölçümler (G1/V2/V3; benim plan alanlarımı kullanır, kapının sahibi süreklilik uzmanı)
| Ölçü | Eşik | Kaynak |
|---|---|---|
| Kadraj sırası: yüz kutularının x-sırası = `_derlenir.kadraj_konumu` sırası | eşit, yoksa H | A2 §6.2 G1 #3 |
| Bakış: yaw > 15° ise yönün işareti = `bakis_kadrajda` | eşit, yoksa H | A2 §6.2 G1 #4 |
| Durum soruları (eller, nesneler, kişi sayısı, ışık tarafı); VLM kör yanıtı ile beklenen | Kritik olgu (el, nesne, kişi) yanlışsa YENİDEN; "görünmüyor" yanıtı B | A1 B4 (ARIS), A2 §5 |
| V3 zincir uyumu: bitiş anı karesinde durum soruları doğru | bütün kritik olgular | Ö7 hedefi (tahmin) |
| V3 adım zamanlaması: kare farkı enerjisinin tepesi adım penceresi içinde | sapma ≤ 1,0 sn | (tahmin) |
| V3 bitişte durma: son 0,5 sn'de ardışık kare MAE ortalaması | klip medyanının ≤ %50'si | yöntem A2 §1.2 (VBench titreme); eşik (tahmin) |
| `devam` dikişi DINOv2 | ≥ 0,80, yoksa H | A2 §6.2 K1 |
| `kurulum_donusu` DINOv2 (kurulumun ana karesine) | ≥ 0,70, yoksa B → VLM | A2 §6.2 K1 |

**`ritim_esikleri.json`'a eklenecek anahtarlar:** `plan_adim_min` (2), `plan_ilk_adim_min_sn` (0,5),
`plan_son_adim_pay_sn` (1,0), `plan_es_zamanli_ozne_max` (1), `plan_goz_farki_bakis_m` (0,3), `plan_goz_yukseklik_m`
({ayakta: 1,6, oturan: 1,2, diz_cokmus: 0,9, yerde: 0,3}), `plan_konusan_yaw_max` (45), `plan_bitis_ozel_oran_max` (0,10),
`plan_agac_derinlik_max` (3), `plan_zincir_derinlik_max` (2), `plan_hareket_istem_kelime_max` (75),
`plan_istem_elle_oran_max` (0,05), `plan_dialog_kurulum_min` (3), `plan_zincir_zaman_sapma_max_sn` (1,0).
Her birinin `aciklama` alanına "(tahmin)" ya da kaynağı yazılır.

---

## 8. Kesin kararların (atomik zincir + 6 özellik + gerekiyorsa ses kararı) kendi alanımda uygulanışı

### 8.1 Karar 2 — Atomik eylem zinciri

**Neden?** Video modeline sonuç söylenirse ("picks up the pen") modelin sonuca nasıl gideceği bilinmez:
hangi el, hangi yoldan, ne kadar sürede. Her klip unutkan olduğu için sonraki klip de bu sonucu bilemez.
Fiziksel adımlar ve saniyeler yazıldığında üç şey olur:
1. Modelin serbestliği daralır.
2. Planın bitişi önceden bilinir; sonraki planın başlangıç karesi o bitişten çizilir.
3. Videodan sonra "bitişe ulaştı mı" sorusu ölçülebilir hâle gelir (Ö7).

**Yazım kuralları:**
1. Plan bir **başlangıç durumuyla** açılır. Bu durum başlangıç karesinin ta kendisidir ve görsel istemi bundan derlenir.
   Durumda şunlar yazılır: kim hangi işarette, poz, yüz yönü, bakış hedefi, iki elin her biri (ne tutuyor, nerede, hangi şekilde, kaç parmak açık), nesnelerin durumu.
2. İnsanlı ya da yaratıklı planda **2–3 adım** olur (Y01).
   - Her adım: `[bas–bit sn] özne + tek fiil (sözlükten) + vücut parçası + yön/hedef + ölçü`.
   - Konuşma bir adımdır. Konuşmalı planda en çok 1 fiziksel adım olur ve konuşmayla örtüşmez.
3. Sağ ve sol **karakterin kendi** sağı ve soludur. Kadraj yönü yalnız `kadraj_sagi` / `kadraj_solu` ile yazılır.
4. Adımlar 0,5 sn'den sonra başlar, klip_sn − 1,0'dan önce biter (Y04, Y05). Kalan süre başlangıçta ve bitişte durup beklemektir: `holds still`.
5. Her adımın `etki`'si yazılır. Bitiş durumunu kod hesaplar. Bu durum sonraki planın başlangıcıdır (`miras`).
6. İnce el işi (kavrama, bırakma, kilit, düğüm) geniş kadrajda yazılmaz, **ekleme planına bölünür** (Y09).
   Bağlantı eylem üstünde kesmeyle yapılır.
7. Sürekli hâller (koşuyor, yürüyor) **poz** olarak yazılır, adım olarak yazılmaz. Böylece "koşarken başını çevirir" örtüşme yaratmaz.
8. Yasak sonuç fiilleri (take, grab, pick up, get, use, fix, prepare, fight, search; açma biçimi yazılmamış open) hiçbir alanda geçmez (Y07).
   **Düzeltme:** ZN §3.7'deki örnek "takes two slow steps" diyor. Bu ifade kendi yasak listesindeki `take`'i içeriyor. "walks two slow steps" olmalı.

**Örnek 1: "kalemi al"** (kullanıcının kendi örneği: yürü → sağ kolunu uzat → başparmak ve işaret parmağıyla kavra)

*1a: tek planlık yazım.* İzin var, ama Y09 BAYRAK verir: OG kadrajda kavrama yapılıyor.
```json
"kamera": {"kurulum": "K1", "kadraj": "OG", "hareket_tipi": "sabit"},
"baslangic_durumu": {"varliklar": {"mara": {"isaret": "M1", "poz": "ayakta", "yuz_yonu": {"hedef": "masa"}, "bakis": {"hedef": "kalem"},
   "sol_el": {"tutar": null, "yer": "yanda", "sekil": "serbest"}, "sag_el": {"tutar": null, "yer": "yanda", "sekil": "serbest"}}},
  "nesneler": {"kalem": {"nerede": "masa_ustu", "isaret": "M5", "durum": "yatay, ucu kadraj soluna"}}},
"eylem_zinciri": [
 {"bas": 0.5, "bit": 3.0, "ozne": "mara", "tur": "fiziksel", "fiil": "yurur", "hedef": "masa", "olcu": "uc_yavas_adim", "etki": {"mara.isaret": "M5_onu"}},
 {"bas": 3.0, "bit": 4.8, "ozne": "mara", "tur": "fiziksel", "fiil": "uzanir", "govde": "sag_kol", "hedef": "kalem", "olcu": "5cm", "etki": {"mara.sag_el.yer": "kalem_ustu"}},
 {"bas": 4.8, "bit": 6.5, "ozne": "mara", "tur": "fiziksel", "fiil": "kavrar", "govde": "sag_el", "el_sekli": "kiskac", "hedef": "kalem",
  "etki": {"kalem.kimde": "mara", "kalem.el": "sag", "mara.sag_el.tutar": "kalem", "mara.sag_el.sekil": "kiskac"}}
]
```
Derlenen istem (tek kişi → öznesiz):
`Static medium-wide shot. 0.5-3s: walks three slow steps toward the desk. 3-4.8s: extends the empty right arm toward the quill lying on the desk, fingers stopping just above it. 4.8-6.5s: the thumb and index finger close around the quill, the other three fingers stay curled. 6.5-8s: holds still. Sound: footsteps on wooden floor, quiet room tone. No music.`

*1b: iki planlık yazım (önerilen).* Kalem hikâyede önemliyse (kurulum ya da kullanım) bu biçim seçilir.
- **P_a** (OG, eylem, `kesme: eylem@4.2`): yalnız adım 1 ve 2. Bitiş: sağ elin parmak uçları kalemin 5 cm üstünde.
- **P_b** (D, ekleme, aynı taraf, `baslangic_durumu: miras`). Adımlar:
  - [0,5–2,0] başparmak ve işaret parmağı alçalır, kalemi kavrar (`kiskac`)
  - [2,0–3,5] kalemi 10 cm kaldırır, `etki: kalem.yukseklik = 10cm`
  
  Bitiş: kalem sağ elde kıskaçla tutuluyor, ucu kadraj soluna dönük.
- Kesme noktası P_a'nın uzanma adımının %67'sinde: 3,0 + 0,67 × 1,8 ≈ 4,2 sn (Y38).

**Örnek 2: "kapıyı açar"** (`open` yasak, açma biçimi yazılır):
`0.5-2s: the right hand rises to the iron latch, four fingers curling over it. 2-3.5s: the thumb presses the latch down. 3.5-6s: pulls the door about 40 cm inward, the body staying in the gap. 6-8s: holds still.`
Etki: `kapi.durum = "aralik_40cm"`, `mara.sag_el.yer = "kapi_kenari"`.

**Örnek 3: konuşmalı plan** (§5.6 P121): 1 mikro adım + 1 konuşma adımı = 2 adım.
- Fiziksel ya da mikro adım konuşmadan önce biter.
- Konuşma süresi ZN §2.3 formülünden gelir: 7 kelime, 2 cümle → 3,95 sn.

**Örnek 4: tepki** (§5.6 P122): `listens silently, mouth closed` + 2 mikro adım (bakış kayar, çene sıkılır).
- Ekran dışından duyulan ses `ekran_disi_ses` alanında yazar.
- Görünen ağız kapalı kalır (Y35).

**Örnek 5: yaratık** (Ember eldiveni kokluyor; kadrajda Mara'nın yalnız eli var):
`0.5-2.5s: Ember stretches the neck about 10 cm toward Mara's gloved left hand, nostrils flaring. 2.5-4.5s: Ember tilts the head slightly to its right and lifts the eyes to Mara's face. 4.5-8s: holds still; Mara's hand stays still. Sound: soft snuffling breath, wind at the cave mouth. No music.`
- Yaratıkta sağ ve sol yine yaratığın kendisine göredir ("its right").
- Bitiş: burun eldivene 10 cm, baş eğik, bakış hedefi Mara.

**Örnek 6: aksiyon ve ekran yönü** (kaçış, sahnenin `ekran_yonu` değeri `soldan_saga`):
- **P_x:** G, `takip_yan`, kamera kadraj sağına doğru ilerliyor, poz `kosuyor`. Adımlar:
  - [0,5–3,5] kadraj sağına doğru 4 adım ilerler
  - [3,5–5,5] başını sol omzunun üstünden geriye çevirir; bakış kadraj solunda (takipçi o yönde)
- **P_y:** takipçi. O da `soldan_saga` gider (Y26).
- Kaçanın yön değiştirmesi ancak ekranda bir `doner` adımıyla olur.

### 8.2 Karar 3 — Altı özellik

**(a) Videodan önce animatik ve habersiz seyirci denetimi.**
Animatiği başka bir uzman kurar. Benim alanımın ona verdikleri:
- `kullanim.sure` ve `kesme`: zaman çizelgesi; L ve J ses kaymaları dahil.
- `hareket_tipi`: hareketsiz görüntüye eklenecek yavaş zoom ve kaydırma (`yavas_ileri` → yakınlaşma, `yavas_pan` → kırparak kaydırma).
- `devam` çiftleri (Mod A): başlangıç ve Bitir görselleri arasında çapraz geçiş. Eylem animatikte de görünür.
- `ekran_disi_ses`: kimin sesinin kimin yüzü üstünde duyulduğu.

Animatiğe geçmeden önce Z0 ve Y kurallarında HATA = 0 olmalı. Seyirci bulguları planı yazan örneğe döner (Y7).
Mod A, kare zincirini animatikle **çakıştırmamak** için seçildi (§8.2-d). Bütün başlangıç ve bitiş görselleri videodan önce
var olduğu için animatik eksiksiz kurulur. Son kare zinciri (Mod B) yalnız istisnadır.

**(b) Makinenin tuttuğu dünya durumu defteri ve otomatik zıplama denetimi.**
- Plan yazarı yalnız **etki** yazar. `durum_defteri.py` bütün filmi hikâye zamanına göre katlar.
  Her plan sınırında her varlığın konumunu, pozunu, ellerini, nesnelerini ve kostüm durumunu bilir.
- Denetler: Y11–Y16 (zıplama, kaybolma, gerekçesiz fark, sözleşme).
- Geometriyle birleşince "görünmesi gerekip görünmeyen" kişiyi de bulur (Y14). B2'deki "Bram kapıda ama araya ateşi söndüren el giriyor"
  ve "Ember bacaya girdi ama sonra evde görünmüyor" türü kopukluklar böyle yakalanır (H/kurgu-izleme-denetimi).
- Defter aynı zamanda görüntü kapılarının **soru kaynağıdır**. `durum_sorulari()` her olguyu seçenekli bir soruya çevirir.
  Karakterlere adla değil görünür kısa tarifle atıf yapılır (A2 §1.4, ViMax).
  VLM kör yanıt verir, kod karşılaştırır (A1 B4, ARIS). Bu, B3'teki elle denetimin (21/44 bozuk) kodlanmış ve tekrarlanabilir hâlidir.

**(c) Referansla otomatik yüz kontrolü.**
Planın bu kapıya verdikleri:
- **Kimin görüneceği** (`kadrajdakiler`) ve buradan derlenen `referans` (≤ 2).
- **Yüz açısı ve ölçek**: `on` / `3/4` yüzler SFace'e gider. `profil`, `sirt` ve `gorunmez` yüzler DINOv2 ya da VLM'e (A2 §6.2 G1 #1).
- **Kimlik demiri** (Y44): her karakterin her sahnedeki ilk görünüşü SFace'in doğrulayabileceği bir plan olur (≥ OY, `on`/`3/4`). Sahnenin geri kalanında sırt ve profil planları serbesttir, çünkü kimlik o sahnede kanıtlanmıştır.
- **Kadraj sırası**: yüz kutularının x-sırası `_derlenir.kadraj_konumu` ile karşılaştırılır. Bu hem 180° hem ayna hatasını yakalar.

**(d) Kare zinciri (son kare → sonraki klibin başlangıcı).** Ne zaman ve nasıl:

| `gecis_turu` | Ne zaman | Başlangıç karesi | Bitir karesi | Maliyet ve risk | Denetim |
|---|---|---|---|---|---|
| `devam`, **Mod A** (varsayılan) | Aynı kurulum, zaman kesintisiz, eylem tek klibe sığmıyor: uzun yürüyüş, uzun duygu tutma, yaratığın boyunu yavaş tilt ile gösterme, doruktaki tek uzun plan | N+1'in görseli, N'nin planlanan bitişidir. N'nin görselinden **türetilir**; yalnız planlanan durum farkı uygulanır | N'de Bitir = N+1'in görseli (Memmet'in bugünkü `bitis_karesi` alanı) | Ek görsel yok; yükleme sayısı aynı. Risk: başla–bitir farkı büyükse morf | K1 dikiş DINOv2 ≥ 0,80; V2 morf; V3 uyum |
| `devam`, **Mod B** | Mod A morf verdiyse ya da sonucu önceden çizilemeyen hareketlerde: su, ateş, kalabalık, kanat açılışı | N videosunun **gerçek** son karesi (`ffmpeg -sseof -0.1`), N V1 ve V2'den geçtikten sonra | yok | Sıralı üretim: N bitmeden N+1 gönderilmez. Her nesilde kalite düşer; derinlik ≤ 2, sonra temiz görselle yeniden demirleme (A2 §2.3) | K1 |
| `eylem_kesme` | Açı ya da ölçek değişir, an aynıdır | Yeni kurulumun ana karesinden türev; olgular N'nin bitişi | Yalnız bitiş durumu kritikse (nesne el değiştirir, kadraja giriş/çıkış, poz değişimi) ve `risk_uretim = yuksek`: `NNN_son.jpg` (≤ %10, Y42) | Ek görsel ve ek yükleme | G1 durum soruları, V3 |
| `kurulum_donusu` | Sahnede daha önce kullanılan kuruluma dönüş | O kurulumun ana karesinden türev (ViMax kamera ağacı, A2 §1.4) | yok | — | K1 ≥ 0,70 |
| `araya_kesme` | Tepki, ekleme, ironi | Kurulumun ana karesinden türev | yok | — | G1 |
| `zaman_atlama` | Aynı mekân, zaman geçti | Kurulum ana karesi + gerekçeli fark | yok | — | K0 fark gerekçesi |
| `yeni_sahne` | Yeni mekân ya da zaman | Bağımsız: mekân kartı + karakter kartları | yok | — | Sözleşme |

Mod A'nın varsayılan olmasının dört nedeni var:
1. Bütün görseller videodan önce üretilir. Animatik (a) ve "bozuk görsel videoya gitmez" kuralı (BK 7.6 #6) bozulmaz.
2. Klibin iki ucu da sabitlenir, atomik zincir planlanan bitişe iner.
3. Sonraki klip, öncekinin zorla bittiği görselden başlar. Dikiş yapısı gereği tutar.
4. Flow'da Bitir'in çalıştığı görüldü: "yumuşak geçiş çalışıyor" (FK), "son kare = hedef görsel" (H/proje-b2).

Bitir varsayılan olarak **konuşmalı planda kullanılmaz**, çünkü bitiş karesinin dudak davranışına etkisi ölçülmedi (§9 açık soru 3).

**Kamera konumu ağacı** (ViMax, A2 §1.4):
- Kök: mekân kartları. Bunlar çok açılı ve kart aşamasında üretilir (BK 4.1 #11).
- Çocuklar: kurulumların ana kareleri. Torunlar: aynı kurulumun sonraki planları.
- `kamera_agaci.py` görsel üretim sırasını buna göre verir: önce ana kareler paketi, G1'den geçer, sonra türevler paketi.
- Böylece bir ana karedeki hata 10 türeve yayılmadan yakalanır. Ebeveyn yeniden üretilirse çocuklar "bayat" işaretlenir.
- Ağaç derinliği ≤ 3 (Y43).

**(e) Kendi kendine öğrenen ders defteri.**
- Her plan özellikleri `denetim` sonuçlarıyla birlikte kaydedilir: kadraj, açı, hareket tipi, fiil, el şekli, referans sayısı, Bitir, geçiş türü, ışık türü.
- `ders_cikar.py` her partiden sonra "özellik birleşimi × hata türü" tablosunu çıkarır.
- Aynı birleşim ≥ 3 kez başarısızsa (tahmin) **aday ders** yazılır. `yonetmen` onaylar.
- Onaylı ders **bir sonraki partide** uygulanır; yeni filmi beklemez.
- Ders türleri:
  - `istem_eki`: `istem_derle` ekler
  - `plan_kurali`: `plan_denetim` yeni H/B kuralı olarak uygular
  - `esik`: RE değişiklik önerisi; ana Claude onaylar
  - `yasak_kalip`
- Bir dersin uygulandığı planlarda o hata oranı düşmüyorsa (≥ 5 kullanımdan sonra, tahmin) ders `etkisiz` işaretlenir. Defter böyle şişmez.
- Biçim:
  ```json
  {"id": "D014", "durum": "onayli", "tur": "istem_eki", "kosul": {"kamera.kadraj": "OU"},
   "eylem": {"gorsel_istem_ekle": "the foreground person seen from behind keeps {SAC} and {KOSTUM} exactly as in the reference"},
   "kanit": ["G1_P1.json#121", "G1_P2.json#233", "G1_P2.json#240"], "kullanim": 0, "basari_orani": null}
  ```
- **Tohum dersler** (sistem kurulurken onaylı girer, mevcut belgelerden):
  1. OU ve arkadan planda öndeki kişinin saç ve kıyafet çapası zorunlu (YR §5 Ç032; H/gemini-ajan-gorsel "yanlış kişinin omuz üstü").
  2. Oda kartında istenmeyen nesne varsa kart referanstan çıkarılır (DR).
  3. Ölçek isteyen nesneye ölçekli referans verilir (DR).
  4. Stil ekinde ışık ifadesi yok (BK 4.1 #3).
  5. Bebek yüzü makrosu yerine görsel + yavaş zoom (DR).
  6. Karakterli planda "İçerik öğeleri" modu ve iki referans yasak, yalnız Kareler (FK).
  7. Tek modelle çalışılır (DR).

**(f) Kalıcı seri evreni kütüphanesi.** Benim alanımın kütüphaneye koydukları ve oradan aldıkları:
```
EVREN/<SERI>/
  MEKANLAR/<mekan>/kroki.json · kurulumlar.json · kart_<aci>.jpg · ana_kareler/<isik_varyanti>/<K>.jpg
  KARAKTERLER/<id>.json   → kimlik_dizesi*, gorunur_kisa_tarif (VLM soruları için), boy_m, goz_yuksekligi_m,
                            baskin_el, asimetrik_ayrintilar[] (ör. "sol kaşta yara izi" → ayna_yasak)
  KOSTUMLER/<id>.json     → dizesi*, durum_sozlugu[] (kapusonu_inik, sol_eldiven_tek…), asimetrik
  EKRAN_YONU.json         → seri boyunca coğrafya yönü (ör. "kuzey diyarına yolculuk = soldan_saga")
  DERS_DEFTERI.json
```
- `*` alanların sahibi görsel ve kart uzmanıdır. Diğer alanlar yönetmenin.
- İkinci filmde aynı kulübeye dönüldüğünde kroki, kurulumlar ve onaylı ana kareler yeniden kullanılır. Mekân sürekliliği filmler arasında da korunur.
- `baskin_el` sayesinde Mara'nın bıçağı her filmde aynı elle çekmesi denetlenir: ince el işi baskın olmayan elle yapılıyorsa ve gerekçesi yoksa BAYRAK.

### 8.3 Karar 4 — Ses ve dudak uyumu (benim alanıma düşen kısım)
- Yolu ses uzmanı seçer. Plan dili **iki yolu da** destekleyecek şekilde yazılır.
- A3'ün değerlendirmesine katılıyorum: ana yol "Veo konuşur + ses dönüştürme" olmalı, yedek yol "TTS + dudak senkronu" (MuseTalk). Gerekçe: dudak, duygu ve zamanlama klipten gelir, görüntüye ikinci model dokunmaz.

Bu yolun plan diline getirdiği şartlar:
1. **Replik isteme birebir yazılır.** `Mara says coldly: "..."` biçimi kullanılır, teslim fiili sözlükten gelir. Veo konuşmayı bu metinden üretir; whisper ya da stable-ts ile metin karşılaştırması bunun üstüne kurulur (A3).
2. **Konuşan yüz okunur olur** (Y32): O/OY/Y, `on` ya da `3/4`. Ağzın önünde el, atkı ya da kupa yok; `yasaklar`a `agiz_onu_engel` yazılır. Bu hem Veo'nun dudak üretimini hem dudak denetimini (SyncNet, A3) hem de yedek dudak senkronunu kolaylaştırır.
3. **Konuşurken fiziksel adım yok** (Y02). ZN §2.3: konuşurken nesneyle uğraşan karakterde Flow dudakları bozuyor.
4. **`replik_kaynagi`**:
   - `klip`: konuşma bu planın klibinde.
   - `klip:<no>`: L/J kesmede ses başka planın klibinden gelir.
   - `tts`: yalnız hiç görünmeyen konuşmacı, örneğin başka odadan gelen ses.
   Ekran dışı replik ilk tercih olarak konuşanın **kendi klibinden** L taşmasıyla verilir. Ses dönüştürme bu yolda da aynı ses kimliğini verir.
5. **Çift ses ve sahte dudak yasakları** (Y33–Y35): L taşması konuşanın da göründüğü plana gitmez. J sesi aynı kişinin kapalı ağzının üstüne binmez. Ekran dışı ses varken görünen herkes `mouth closed` kalır.
6. **`replik_zaman` penceresi** konuşma adımından derlenir. Whisper araması ve dudak denetimi bu pencerede yapılır (DR: "aynı klip iki plana bölününce" dersi).
7. **Ses tarifi** (cinsiyet, perde, tını) hareket istemine girerse kelime bütçesini (Y46) paylaşır. Yaş sözcükleri yasaktır: "young" filtre listesinde (`istem_denetim.py` `YAS_IFADESI`). Tarif "deep, gravelly male voice" gibi yaş içermeyen biçimde yazılır.

---

## 9. Riskler, diğer uzmanlarla çakışabilecek noktalar, açık sorular

### 9.1 Riskler ve önlemler
| # | Risk | Etki | Önlem |
|---|---|---|---|
| R1 | Flow/Omni saniyeli adımlara ("0.5-3s:") uymayabilir. Bu ölçülmedi; Seedance'ta "SHOT n — around a-b seconds" biçimi çalışıyordu (H/seedance-director-yontemi) | Ö7 düşer, yeniden çekim artar | İlk partide eylem planlarının yarısı `aralik`, yarısı `sira` ("First… then… finally…") biçimiyle derlenir. Planlar gerçek üretimden seçildiği için ek kredi yok. V3 sonucuna göre biçim sabitlenir. İkisi de kötüyse adım sayısı 2'ye iner ve Bitir oranı artırılır |
| R2 | Saniyeli zincir istemi uzatır. Bu, "kısa istem" kuralıyla (H/video-istem-kurali) çatışır | Model istemin bir kısmını görmezden gelebilir | Hareket isteminde kimlik, stil ve mekân **hiç** yok, görsel taşıyor. Y46 ≤ 75 kelime (tahmin), ilk partide ölçülür |
| R3 | Mod A'da başlangıç ile Bitir karesi çok farklıysa model ara hareketi morf ile uydurur | Doğal olmayan hareket | Bitir karesi başlangıç görselinden türetilir. Fark yalnız 2–3 adımın getirdiği değişimdir. V2 morf ölçümü (DINOv2 ani düşüş, A2). İki morftan sonra Mod B ya da plan bölme |
| R4 | Ajanların koordinat yazması zor; işaret ve kurulumlar tutarsız olabilir | Y2 tıkanır | `kroki.py --karsilikli A B --taraf bati`, iki işaret ve eksen tarafından **standart karşılıklı çekim kurulumlarını kendisi önerir**: ikili konum planı, iki OU, iki tekli; mesafe ve lens kalıpla. Ajan seçer ya da düzeltir. Kroki PNG'si her turda yeniden çizilir. Hazır mekân şablonları da var (oda + kapı + ocak; mağara ağzı; orman açıklığı) |
| R5 | Üretilen görsel krokiye uymayabilir (kapı yanlış tarafta) | Mekân zıplaması | Mekân kartı açıları krokiye göre istenir (`KART_ISTEGI.json`). Ana kareye G1'de mekân çapası soruları sorulur ("Is the door on frame left?"). Türevler ana kareden üretilir |
| R6 | Dış ve büyük mekânlarda (orman, savaş alanı) duvar yok, koordinat zayıf | 180° ve yön karışır | İşaretler ve yer işaretleri (kaya, ağaç) yeterli. Yolculukta koordinat yerine `EKRAN_YONU.json` + sahne `ekran_yonu` kullanılır |
| R7 | Ek bitiş görselleri yükleme sayısını artırır ("çok dosya aynı anda" uyarısı, DR) | Olağan dışı uyarısı | Y42 ≤ %10. Mod A ek görsel istemez. Memmet temposuna dokunulmaz; konu üretim uzmanına bildirilir |
| R8 | 3+ kişili sahne ve kalabalık (K3: ≤ 2 referans) | Yüz karışması | Defterde `figuran` varlığı tutulur, referansı yok. Planda `siluet` / `el` / `sirt` ölçeği. Y45 referansı kadrajdakilerden derler |
| R9 | Klip bölmede tek klip iki plana dağılır | Replik yanlış plana kayar (DR) | `replik_zaman` penceresi; `kaynak_klip` + `kullanim` penceresi; `capcut_film` ve `izleme_paketi` değişiklikleri (§6.2) |
| R10 | 495 plan × plan yazarı turları; kullanım sınırı ve süre | Aşama uzar | Sahne başına paket (bağlam küçük), ≤ 5 paralel, ≤ 2 öz-denetim turu. Deterministik işin hepsi betikte |
| R11 | Şema ağırlaşır, ajan alan atlar | Sessiz eksik | `plan_sema.py` zorunlu alanları HATA yapar. Miras ve `derlenir` yazımı yazarın yükünü azaltır |

### 9.2 Diğer uzmanlarla çakışabilecek noktalar
1. **Şema sahipliği** (süreklilik, hikâye, kurgu): ZN `zanaat` ve A2 `sureklilik` alt nesneleri yerine alt nesne başına tek sahip ve `cekim` öneriyorum (§5.2). Süreklilik uzmanı `sureklilik` nesnesini savunabilir. Eşleme tablosu uzlaşma için yazıldı. **Kesin olan tek şey:** aynı olgu iki yerde tutulmamalı.
2. **Dünya durumu defteri** (süreklilik): `durum_defteri.py` tek araç olmalı. Süreklilik kapıları (G1/V2) onun `durum_sorulari()` API'sini kullanmalı. Defterin sahibi kim olursa olsun, plan tarafındaki yazım biçimi (`etki`, `miras`, sözleşme) benim önerim.
3. **İstem yazımı** (istem mühendisi): `cekim` doluysa istemi `istem_derle.py` yazar. İstem mühendisinin rolü önerim şu: derleyici şablonlarının bakımı, `istem_elle` istisnaları, CORRECTION cümlelerinin `cekim` alanlarına mı (kalıcı düzeltme) yoksa `istem_eki`'ne mi gideceği. Mevcut `istem-muhendisi.md` buna göre değişir.
4. **Görsel paket sırası** (görsel / kart uzmanı): kamera ağacı ana kareleri türevlerden önce istiyor. Gemini paketleri 30'arlık; sayı aynı kalır, sıra değişir. Ana kare paketi G1'den geçmeden türev paketi verilmez. Bu bir kullanıcı bekleme noktası ekleyebilir.
5. **`parti` anlamı** (üretim): plan düzeyinde `parti` = üretim partisi (20, Memmet'in bugünkü anlamı). Hikâye partisi sahne düzeyinde `hikaye_partisi` (BK #14).
6. **Kurgu** (kurgu uzmanı): `kullanim` ve `kesme`'yi yönetmen **planlar**. Kurgu gerçek değerleri kendi `KURGU_PLANI.json`'ına yazar ve `SAHNELER.json`'a geri yazmaz; yalnız Y10 kararıyla değişir. Y31'deki "L kesmede görüntü + taşma ≥ formül" yorumu kurgu uzmanınca onaylanmalı.
7. **Ses** (ses uzmanı): `teslim` alanı, adım başına `efekt` anahtarı, `replik_kaynagi` değerleri ve hareket istemindeki ses tarifi kelime bütçesi birlikte kararlaştırılmalı.
8. **Hikâye ve oyuncu denetimi**: 16 kelimeyi aşan repliklerin bölünmesi `replik_degisti` listesiyle hikâye tarafına döner. Kim onaylar? (Hikâye uzmanının önerisine bağlı.)
9. **Animatik**: Mod A'nın Bitir görselleri animatikte çapraz geçişle kullanılmalı. Animatik uzmanı farklı bir hareket taklidi önerirse (ara kare vb.) uyum gerekir.
10. **Kesin karar 1**: önceki hatta mekân kartı onayı kullanıcıdaydı (BK 7.3). Benim alanımda kullanıcı onayı yok. Y10'daki yeni sahne onayı yalnız `--onayli` modda sorulur.

### 9.3 Açık sorular (ölçülmeden karar verilmemeli)
1. Omni 1.1 Flash saniyeli adım sırasına ve zamanlamasına ne kadar uyuyor? (R1; ilk partide V3 ile ölçülür.)
2. `aralik` ("0.5-3s:") ile `sira` ("First… then…") biçimlerinden hangisi daha iyi? (R1.)
3. Konuşmalı klipte Bitir karesi dudak hareketini bozuyor mu, kapalı ağızla bitişi zorluyor mu? Ölçülene kadar konuşmalı planda Bitir yok.
4. Gemini ajanında "2 karakter kartı + ana kare + (mekân kartı)" = 3–4 referansla kimlik tutuyor mu? Kare başına 2 karakter referansı kuralı (DR, CI) karakterler için ölçüldü; karakter dışı referansların sınırı ölçülmedi.
5. 720p **10 sn** klibin kredisi ölçülmedi. Bilinen tek sayı 360p'de 10 sn = 7 kredi (KR); 720p 8 sn = 12 (FK). 17–20 kelimelik replik 10 sn ister (ZN §2.3).
6. Veo videonun ilk karesi onaylı başlangıç görseline ne kadar sadık? A2'de DINOv2 ≥ 0,85 tahmini var; ölçülmeli.
7. Flow "Extend / Jump to" (A2 §2.2, doğrulanmadı) Mod B'nin yerine geçer mi? Model değiştirme uyarısı riski de denenmeden kullanılmaz.
8. 720p'de OY ölçekli yüzde SFace güvenilir mi? Kimlik demiri kuralı (Y44) B3'ün 44 karelik etiketli setiyle ayarlanmalı (A2 §7).
9. MediaPipe yaw işaretinin bakış yönüne çevrimi bir test görselinde bir kez doğrulanmalı (A2 §4 uyarısı).
10. Aynı anda kaç `plan-yazari` çalıştırılabilir? Kullanıcının Claude kullanım sınırına bağlı (tahmin: 5).

### 9.4 Bu turda bilerek dışarıda bıraktıklarım
- Görsel ve video denetiminin kendi eşikleri ve araçları süreklilik uzmanının; burada yalnız kullandığım alanlar yazıldı.
- Duygu haritası, merak ve kurulum defterleri hikâye uzmanının (ZN §1, §4). Burada yalnız `zanaat` alt nesnesine yer ayrıldı.
- Müzik, ambiyans ve LUFS ses uzmanının (ZN §5).
- Memmet temposu ve sağlayıcı geçişi üretim uzmanının. Plan dili tempoya dokunmaz; bot tespitini atlatma yok, uyarıda dur (DR).
