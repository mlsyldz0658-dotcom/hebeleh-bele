---
name: gemini-ajan-gorsel
description: Başlangıç görselleri Gemini ajanında toplu üretilir (GOREV+ISTEMLER+REFERANSLAR → ZIP); Flow yalnız videoya kalır
metadata:
  node_type: memory
  type: reference
  originSessionId: 2139e0c3-5b43-4636-b0b5-3ac5f98b918e
  modified: 2026-10-18T19:54:14.935Z
---

Kullanıcının 18.10.2026 keşfi: Gemini ajanına (Gemini uygulaması) bir klasör verince (GOREV.txt kurallar, ISTEMLER.txt blokları "=== NNN === / FILE NAME / REFERENCE IMAGES / PROMPT", REFERANSLAR\ kart görselleri) referanslı, tutarlı görselleri tek ZIP'te veriyor. Örnekler: `Masaüstü\GEMINI GORSEL ISTEM` (başka kanalın 3D/Pixar Shorts projeleri — SHORTS00x, HIKAYE0xx, TOPLU1 104 görsel; dokunma). Çıktı 768x1376 (dikey istenince).

Araçlar (ARACLAR): `gemini_paket.py <film> [--parti N] [--sahne ..] [--ad B3_P1]` → Masaüstü\GEMINI GORSEL ISTEM\<FILM>_<ad>\ (30 sahnelik paketler, 16:9 kuralı); `gemini_al.py <film> <zip|klasör>` → SIRALI_GORSEL\NNN.jpg (16:9 kırp, 1376x768). Memmet SIRALI_GORSEL'de jpg varsa Flow'da görsel üretmez → yalnız video gönderir.

Gemini ajanı en fazla 10 ek dosya alıyor; referanslar ZIP'lenince sorun yok (kullanıcı 18.10) → gemini_paket 10'dan fazla referansta otomatik REFERANSLAR.zip yapar. B3 kart paketi (29 kart) tek seferde, kaliteli geldi; ölçek isteyen nesnelerde (minik çizme) referansı ölçekli görselle ver.

KULLANICI KURALI (18.10 akşam, kızdı): düzeltme/yeniden üretim görsellerini kullanıcıya paket olarak VERME → Memmet ile Flow'da kendim yaparım (memmet.py --asama gorsel --sahne ..; kart gerekiyorsa geçici "gorsel" motorlu sahne). Kullanıcıya yalnız büyük toplu paketler ve VİDEO paketleri gider. Video paketi = GORSELLER + REFERANSLAR (kartlar) + AKIS.txt (her klibin öncesi/sonrası) + SUREKLILIK.md (yönetmenin parti haritası, _BOLUM3\AKIS_P<n>.md) — "Gemini'yi zorla" isteği.

18.10 VİDEO DENEMESİ: Gemini ajanı bu ortamda image-to-video / dudak senkronu / ses üretemiyor → videolar Flow'da (Memmet) kalır. AMA aynı paketle (GORSELLER + REFERANSLAR + AKIS + SUREKLILIK) başlangıç karelerini süreklilik listesine göre denetledi ve benim kaçırdığım 3 hatayı buldu (sopaya asılı boş eldiven, verilmiş eldivenin hâlâ elde olması, yanlış kişinin omuz üstü). → Video öncesi her partide "görsel süreklilik denetimi" adımı ekle (kendi ajanımla; gerekirse Gemini).

**Why:** Flow'daki "olağan dışı etkinlik" uyarıları görsel gönderimlerinde de geliyordu; görseli Flow'dan çıkarmak gönderimleri yarıya indirir, kredi ve risk azalır.
**How to apply:** B3'ten itibaren görsel aşaması varsayılan olarak Gemini paketiyle; kullanıcı ZIP'i verir, ben içe alırım, sonra görsel denetimi → Memmet video. Bkz. [[PROJE-b3]], [[olagandisi-dur]].
