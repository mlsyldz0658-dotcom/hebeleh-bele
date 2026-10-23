---
name: video-istem-kurali
description: "Flow video (hareket) istemi kalıbı — kullanıcı kararı 15.10.2026; tek kişide özne yok, iki kişide ad; yaş/girl yazılmaz"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c02834a3-78d7-42ef-8b9f-3353299f1117
  modified: 2026-10-17T19:17:56.810Z
---

Video istemi kısa olur: hareket + kamera + replik + kısa Sound. Görsel zaten karakteri/mekânı/stili gösterir, sahne türü/stil tekrarı gereksiz.
- Kadrajda tek kişi: özne yazılmaz, doğrudan eylem ("Looks up, laughing; static shot. Wren says quietly: ...").
- İki kişi: karakter adlarıyla.
- Yaş, girl, little, frail, bed, sleep, cheek, chest, trembles gibi kelimeler yazılmaz. B2 (17.10): "baby", "siblings" da tetikledi; "blanket-wrapped figures" geçti. Bebek yüzü makrosu 3 denemede de reddedildi → başlangıç görseli + yavaş zoom + zamanla ısınan renk (ffmpeg blend) ile çözüldü; yönetmen istemlerine bu kelimeleri hiç koydurma.
- Sound satırı yalnız efekt/ortam ister ve "No music." ile biter (kullanıcı 15.10: "flow'da sadece ses efektleri kalsın, müzikleri komple sen üret"). Kurguda sahne boyunca kesintisiz ambiyans zemini olur; klip geçişinde ses "tak" diye değişmemeli.

- AMBİYANS İÇİN LYRIA KULLANMA: Lyria müzik modeli, "rüzgâr" istesen bile müzikal ton/drone koyuyor; kullanıcı bunu "Flow müziği hâlâ çalıyor" diye fark etti (15.10). Zeminler gerçek CC0 kayıttan (SES_KUTUPHANESI/yatak: DIS/IC/GECE/ZINDAN/SALON). Kullanıcı kararı: filmde müzik yok ya da yalnız ayrı katmanda, kendisi açıp kapatabilsin; efekt+ambiyans en alt ayrı katmanda.
- (eski not) Lyria ambiyans: canlı/kalabalık tarifi (kennel, puppies, blacksmith...) insan sesine benzer mırıltı üretiyor → kullanıcı "konuşmalar yankı yapıyor" dedi. Ambiyansı yalnız rüzgâr/oda tonu gibi cansız seslerle iste ve whisper ile konuşma taraması yap; şüpheliyse temiz bir yatağı (AMB_ODA) kullan.
- Dudakları oynayan bir karakterin üstüne başkasının (ekran dışı) repliğini koyma; konuşulan şeyi ya da dinleyenin kıpırdamayan anını göster.

**Why:** PROJE B1'de genç Wren'li 12 sahne Flow'un küçükler politikasına takıldı; tetikleyici kelimeler çıkınca geçti. Kullanıcı "sahne türü gereksiz, flow fotoğraftan görüyor; karakter adı olsun ya da tek kişiyse direkt yapacağı şeyi söylesin" dedi. Flow'da inatla geçmeyen sahne Google Cloud Veo'da geçti (070, 099 orijinal istemle).

**How to apply:** Değerlendirmede YAPIM_REHBERI ve istem mühendisi şablonuna işlenecek; mekanik kontrole riskli kelime taraması önerildi. Bkz. [[PROJE-yapimi]], [[soru-sadece-cevap]].
