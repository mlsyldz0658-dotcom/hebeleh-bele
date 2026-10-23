# Üretim Hattı (v2 — B1 derslerinden sonra kuruldu, B2'de olgunlaştı, B3'te parti tasarımıyla genişledi)

Her adımın çıktısı bir sonrakinin girdisi. Para/kredi harcayan adımlar en sona bırakılır; önce kâğıt üstünde düzeltilir.

## 1. Hikâye odası (kredi yok)
- **Brifing:** önceki bölümün bıraktığı yer, sezon planındaki görev, açık sorular, kostüm/kart ihtiyaçları.
- **İki öneri:** A (sezona sadık) ve B (sürprizli). Kullanıcı seçer (B2'de B, B3'te B seçildi).
- **B3'ten itibaren bölüm BAŞTAN 3 PARTİ** (her biri ~4 dk) tasarlanır. Her parti için 8 başlık: amaç/duygu, vuruş vuruş olay akışı, **kim nerede durur**, **nesnelerin yolu** (kimde, nerede), yalan/niyet nasıl okunur, mekân tutarlılığı, parti sonu kancası, plan sayısı ve riskli planlar.

## 2. Kâğıt üstü habersiz seyirci denetimi (kredi yok)
- Hikâyeyi bilmeyen bir Claude ajanı, sadece önceki bölümlerin izleyici özetiyle senaryoyu "film gibi" okur.
- Puan verir (anlaşılırlık / merak / duygu), kopuklukları KRİTİK/ORTA/KÜÇÜK diye listeler, kesilecekleri söyler, ilk 30 saniyeyi değerlendirir.
- Hikâye odası v2'yi bu rapora göre yazar.

## 3. Yönetmen (kredi yok)
- Parti haritası (oda krokisi: kapı, ocak, perde, pencere yönleri), plan plan çekim listesi, kadraj, replik, duygu.
- **Süreklilik kontrol listesi** (her planda karakter ve nesne konumu).
- Her plana **görsel istemi** (tek kare, İngilizce, sabit stil son eki) ve **hareket istemi** (kısa, "No music.", yasak kelimesiz).
- Yeni kart listesi (karakter/mekân/nesne). Çıktı: `05_yonetmen_*.md` + `05_PLANLAR_*.json`.

## 4. Kartlar ve görseller (Flow kredisi yok)
- Yeni kartlar ve sahne başlangıç görselleri **Gemini ajanına toplu paket** olarak verilir (GOREV.txt + ISTEMLER.txt + REFERANSLAR.zip). ZIP gelince içe alınır.
- Düzeltme/yeniden üretim görselleri **Memmet** ile Flow'da yapılır (kullanıcıya iş çıkarılmaz).

## 5. Görsel süreklilik denetimi (B3'te eklendi)
- Bir denetçi ajan her başlangıç görselini süreklilik listesine karşı tarar: kim kadrajda, eldiven hangi elde, bakış yönü, fazladan ateş, Ember'in boyu…
- YENİDEN ÜRET denenler "CORRECTION:" cümlesiyle Memmet'te yeniden üretilir; küçükler kırpma/ayna ile düzeltilir. 2 tur.

## 6. Video (Flow kredisi)
- Memmet her sahne için başlangıç karesi + hareket istemi gönderir. 720p, 8 sn, Omni 1.1 Flash (12 kredi). Model değiştirmek uyarı getirdiği için tek model.
- Modlar: gece (yavaş, kendi gönderir), gündüz, **yarı otomatik (elle)**: Memmet hazırlar, gönder'e kullanıcı basar.

## 7. Kurgu (parti parti)
- `plan_kurgu.py` → kurgu klasörü + TTS replikleri yerleştirme (whisper ile dudak anı).
- **Dudak denetimi** (`dudak_denetim.py`): her repliği klipteki konuşmayla karşılaştırır.
- Diyalog seviyesi eşitleme (fısıltı -24 / yumuşak -21.5 / normal -19.5 LUFS).
- Efekt + ambiyans katmanı (CC0 banka), Gemini müzik katmanı, CapCut taslağı, renk cilası.
- **Kurgu izleme denetimi:** her parti kare paketiyle habersiz seyirciye izletilir; 8/10'a yaklaşana kadar yönetmen düzeltir, gerekirse yeniden çekim.
- Kullanıcı CapCut'ta izler, not bırakır; notlar okunup düzeltilir. Kullanıcı düzenlediyse taslak yeniden kurulmaz, dosyalar yerinde değişir.

## 8. Yayın
- 4K 24fps dışa aktarma (kullanıcı, CapCut).
- Sonda kayan jenerik (`jenerik.py`), kanal adı KANAL.
- YouTube paketi (başlık, açıklama, bölüm zamanları, etiketler, sarı dolar riski kelimesi yok) ve 3 Short (`shorts_mp4.py`: kelime kelime altyazı, akıllı dikey kadraj, -14 LUFS).
- `kalite_denetim.py` ile siyah kare/donma/ses seviyesi kontrolü.

## 9. Arşiv
- İş bitince ara klasörler C'den `D:\YZ_FILM_ARSIV\<FİLM>\` altına TAŞINIR (kopya değil).
