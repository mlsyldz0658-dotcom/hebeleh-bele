# Flow keşif notları (14 Ekim 2026, deneme hesabı) — Memmet Auto için

## Sayfa yapısı
- **Proje adresi:** `flow.google.com/project/<uuid>`, sabit. Memmet her filmin proje adresini dosyada tutar ve doğrudan gider.
- **Ana sayfa:** proje kartları `a[href*="/project/"]`; kartın metninde proje adı var.
- **Proje adı:** sol üstte, "Düzenlenebilir metin" textbox. Üç tıkla, yaz, Enter. Çalışıyor.
- **İstem kutusu:** `.ProseMirror` (contenteditable). `focus()` ile odaklanıp yazılır.
  - DİKKAT: "Düzenlenebilir metin" adlı başka bir textbox (proje adı) daha var; karıştırma.
- **Gönder:** aria-label "Oluşturmaya başla".
  - DİKKAT: sayfada başka `button[type=submit]` var; türüne göre seçme, adına göre seç.
- **Ayarlar:** aria-label "Ayarlar tetikleyicisi". Düğme yazısı mevcut ayarı söyler, örn. "🍌 Nano Banana 2.1 crop_16_9 x1".
  - Menüde radyolar: Resim / Video; Kareler / İçerik öğeleri; 16:9 / 9:16; model; 360p / 720p; 4 / 6 / 8 / 10 sn; x1-x4.
  - Kredi bilgisi menünün altında yazar.
- **Referans ve içerik ekleme:** aria-label "İçerik öğelerini istem kutusuna ekle".
  - Açılan seçicide `[role=option]` listesi; yanında "İsteme ekle" düğmesi.
  - Bazen öğeye tıklamak doğrudan ekliyor, bazen "İsteme ekle" de gerekiyor. Her iki durumu da ele al, sonra istem kutusundaki "İçerik öğesi resmi" sayısıyla doğrula.
- **Kareler modu:** istem kutusunda "Başlat" ve "Bitir" kare yuvaları ile "İlk ve son kareyi değiştir" düğmesi.
- **Dosya yükleme:** sayfada hazır `input[type=file]` yok.
  - Çalışan yöntem: kendi input'umuzu ekle, dosyayı ona ver, sonra ekranın ortasındaki öğeye `dragenter`/`dragover`/`drop` DragEvent gönder (DataTransfer ile).
  - Playwright'ta alternatif: `expect_file_chooser` + "Medya yükle".
  - Yüklenen dosya kendi adıyla listelenir, örn. "mara.jpg", "007.jpg".

## Medya ve takip
- **Görsel karoları:** `img[data-media-id=<uuid>]`, adres `flow-content.google/image/<uuid>` (imzalı).
- **Video karoları:** `<video>` ancak fareyle üzerine gelince oluşur; adres `flow-content.google/video/<uuid>`. 360p = 640x360, 8 sn.
- **Yeni üretimi tanıma:** göndermeden önce `data-media-id` listesini al; sonra yeni kimlik çıkınca o sahneye ait.
- **İlerleme:** karo üzerinde "%NN" yazısı.
- **Flow'un verdiği başlıklar:** karo ve seçicide istemin özeti görünür (örn. "Huntress filling water flask"). Sahne eşleştirmesinde kullanma, kimlik kullan.
- **İndirme:** imzalı adres sayfa içinde `fetch` ile alınabiliyor (200, image/jpeg, 1376x768, ~800 KB). Chrome'un indirme düğmesi kullanıcının indirme klasörüne kaydediyor; Memmet bunu kullanmaz.
- **Süreler:** görsel ~20-25 sn, video ~40 sn.
- **Gönderdikten sonra:** istem kutusu ve kare yuvaları temizlenir.

## Krediler
- Görsel (Nano Banana 2.1): 0 kredi
- Video Omni 1.1 Flash, 8 sn: 360p = 6 kredi, 720p = 12 kredi. Kareler ve İçerik öğeleri aynı fiyat.

## Kalite sonuçları
- **Kareler (görsel → video):** en tutarlısı. Karakter birebir korunuyor, diyalog söyleniyor.
- **İçerik öğeleri, tek referans:** iyi ama kadrajı ve ayrıntıları Flow seçiyor.
- **İçerik öğeleri, iki referans (Mara + Ember):** ejderha doğru, Mara kaydı (saç rengi, yaş, yara izi yok). Karakterli sahnede kullanma.
- **Başlangıç + bitiş karesi:** yumuşak geçiş çalışıyor (diz çökmüş → yürüyüp orman kenarında duruyor). Sahne bağlantılarında kullanılabilir.

## Sorunlar
- Sayfada çok video olunca Chrome ekran görüntüsü zaman aşımına uğrayabiliyor. Memmet ekran görüntüsü kullanmaz.
- `Runtime.evaluate` 45 sn sınırı: uzun bekleme döngülerini sayfa içinde değil, dışarıda (Python) yap.
- Sekme arka plandayken Chrome çizimi durdurabilir.
- Sayfada görünmez reCAPTCHA var (`g-recaptcha-response`). Doğrulama çıkarsa dur, kullanıcıya bildir.
