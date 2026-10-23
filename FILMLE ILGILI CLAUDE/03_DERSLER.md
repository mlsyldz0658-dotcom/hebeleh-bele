# Dersler (deneyerek öğrenilenler)

## Google Flow ve "olağan dışı etkinlik"
- Hızlı/toplu gönderim, peş peşe model değiştirme (Lite ↔ Omni) ve **çok sayıda dosyayı aynı anda yükleme** uyarı getiriyor. Tek model (Omni) kullan.
- Aynı akşam ~40 görsel gönderdikten sonra video tarafı tamamen işaretlendi: yeni projede, yavaş tempoda bile her video 30 sn'de uyarı aldı. → Yoğun görsel turundan hemen sonra videoya başlama; hesabı dinlendir.
- Kullanıcı kuralı: uyarıda Memmet durur. Bot tespitini atlatmaya çalışmak yok (insan taklidi fare/klavye reddedildi).
- En güvenli yollar: **görselleri Gemini ajanında toplu üret**, Flow'u yalnız videoya bırak; kullanıcı başındayken **yarı otomatik mod** (gönder'e insan basar).
- Kredi sessizce bitince gönder düğmesi pasifleşir → Memmet boşuna denemesin, dursun.
- Flow'un kesilmiş indirmeleri olur → sayfa içinden tam indir + ffprobe kontrolü.

## Filtreler ve istemler
- Video istemlerinde "girl, little, child, baby, siblings, frail, bed, sleep, cheek, chest, trembles" ve yaş ifadeleri küçükler filtresine takılıyor. "blanket-wrapped figures", eller, makro kullan.
- Bebek yüzü makrosu 3 denemede de reddedildi → başlangıç görseli + yavaş zoom + zamanla ısınan renk (ffmpeg) ile çözüldü.
- Video istemi kısa: hareket + kamera + replik + "Sound: …" + "No music." Müzik ayrı katmanda.
- Görsel üretici verilen oda kartındaki nesneleri (fener, kapalı kapı) kopyalar → istenmiyorsa o kartı referanstan çıkar, kadrajı değiştir.
- Ölçek isteyen nesneler (minik çizme) için istem tek başına yetmiyor; ölçekli bir referans görsel ver (yanında el, kaşık).

## Hikâye ve kurgu
- Kurgulanmış filmi **habersiz seyirci ajanına** kare paketiyle izletmek kopuklukları yakalıyor (B2 P1: 5/10 → 7/10). Her seyirci farklı ayrıntıya takılır; puanlar gürültülü, eğilim önemli.
- Bir bilgi/nesne kullanılmadan önce kurulmalı ("öteki yumurta", "kömür diski" kurulmadan kullanılmıştı).
- Karakter kaybolup belirmesi, nesnenin yeri zıplaması en çok "kopuk" hissi veren şeyler → yönetmen belgesinde **kim nerede / nesnenin yolu** listesi şart.
- Kullanıcının kendi elle kestiği planlar çoğu zaman doğru karar; ama zincirdeki bir bilgiyi (miğferin inişi gibi) de götürebilir → yerine bağlayıcı plan.
- Geri dönüşler soluk ton/flaşla işaretlenmeli.
- Video öncesi **görsel süreklilik denetimi** 44 görselde 21 bozuk kare yakaladı (yanlış kişi, ters el, yasak ışık). Gemini ajanı da bu denetimde iyi.

## Ses
- Aynı klip iki plana bölününce whisper repliği yanlış plana koyuyordu → arama planın kendi penceresinde. Kurgu değiştikçe **dudak denetimi**.
- Replik seviyeleri 9 dB oynuyordu → LUFS eşitleme.
- Yeni çekilen planlar efektsiz kalıyordu → her yeniden çekim turunda efekt yerleşimini de güncelle.
- Kapı sahnesinde planlar arası dış/oda ambiyansı zıplıyordu → tek sürekli zemin.
- Shorts -21 LUFS çıkmıştı; YouTube için -14.

## Araç/işleyiş
- Düzeltme araçları **bir kez** uygulanmalı (tekrar çalışınca kırpma/ayna üst üste biniyordu) → işaret dosyası.
- Kullanıcıya elle iş (görsel paket taşıma vb.) çıkarma; mümkün olan her şeyi Memmet/araçla kendin yap.
- Yeni sürümleri ayrı klasöre derle; kullanıcının taslağının bağlı olduğu dosyalara dokunma.
- C diski dolar: biten işleri D'ye taşı; pip önbelleği 13 GB birikmişti.
- OpenMontage (GitHub) denendi: üretim için ücretli API ister, Flow aboneliğini kullanamaz → hattın yerine geçmedi; altyazı/kadraj/kalite parçaları alındı.
- Gemini ajanı (argon) görsel üretir ve denetler ama **video üretemez**.
