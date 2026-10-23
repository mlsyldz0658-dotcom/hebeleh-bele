---
name: yz-dizi-demolari
description: 13 Ekim 2026 gecesi ücretsiz araçlarla yapılan YZ dizi demoları (The Second Ring); üretim hattı Masaüstü\demo deneme klasöründe
metadata:
  node_type: memory
  type: project
  originSessionId: c02834a3-78d7-42ef-8b9f-3353299f1117
  modified: 2026-10-13T00:49:46.426Z
---

Kullanıcı 13 Ekim 2026 gecesi "aşk-ihanet temalı, ücretsiz araçlarla dizi demosu yap, her demonun notunu al" dedi ve çalışmayı `C:\Users\Soysal\Desktop\demo deneme` klasörüne taşıttı. Notlar `DEMO_NOTLARI.md`'de (başta sabah özeti var). Dizi: *The Second Ring* (Boğaz'da yalı, Leyla/Emir/Selin, İngilizce, Türk dizisi havası).

Kurulan ücretsiz hat (`araclar/`): `uretim.py` (görsel→ses→müzik/sfx→altyazı→kurgu→kapak), `yerel_gorsel.py` (Realistic Vision SD1.5, RTX 3050 Ti 4GB, ~1:45/görsel), `referans_tutarlilik.py` + `bolum_referansli.py` (IP-Adapter Plus Face, kimlik portreleriyle tutarlılık, ~20 sn/görsel), `derinlik.py` (Depth Anything V2 ile 2.5B paralaks), `guvenlik_kontrol.py` (Falconsai NSFW tarayıcı, karantina), `fragman.py`, `dikey_shorts.py`. Sesler: Piper ve Kokoro (yerel, ücretsiz). HF FLUX ücretsiz alanı hesapsız kullanımda 2-3 görselde kota doldurdu.

**Why:** Kullanıcı YZ film/dizi kanalı kurmaya karar verdi; önce maliyetsiz pilotla tutup tutmadığını görmek istiyor.

**How to apply:** Kullanıcının demo geri bildirimini (özellikle Piper vs Kokoro, tarz, tempo) sor. Açık kaynak model istenmeden çıplaklık üretti; her üretimde NSFW negatifleri + kapalı kıyafetli referans portre + otomatik tarama zorunlu. Gerçek hareket için ücretli görselden-videoya (fal.ai) gerekecek. İlgili: [[youtube-nis-arastirmasi]].
