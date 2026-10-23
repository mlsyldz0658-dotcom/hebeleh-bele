# CLAUDE.md — YZ Film Otomasyonu (hebeleh-bele)

> **İlk iş:** Repo kökündeki `PAKET.zip` dosyasını köke aç (`unzip PAKET.zip`), içeriği commit et,
> ardından `PAKET.zip`'i repodan sil. Aşağıdaki yollar zip açıldıktan sonra geçerlidir.

Bu repoyu açan Claude oturumu ÖNCE bu dosyayı, sonra şunları okur:
1. `FILMLE ILGILI CLAUDE/00_OKU_BENI.md` … `07_*.md` (11–20 Ekim 2026 deneyiminin tam devri)
2. `YZ_FILM/BILGI/CLAUDE_ICIN.md`, `KARARLAR.md`, `YAPIM_REHBERI.md`
3. `FILMLE ILGILI CLAUDE/03_DERSLER.md` — deneyerek öğrenilen kurallar, ihlal etme

Kullanıcı Türkçe konuşur, teknik bilgisi az. Belgeler Türkçe, kullanım `.bat` dosyalarıyla adım adım.

## Hedef
Senaryo yazımından bitmiş filme (kurgu + ses + müzik + altyazı + kapak + YouTube paketi) kadar
**tam otomatik** çalışabilen, sonucu "mükemmele yakın" olan bir üretim hattı. İnsan yalnızca
isterse onay noktalarında devreye girer (`--onayli` / `--tam-otomatik`).

## Mevcut durum ve eksikler (paketten çıkarıldı)
- Paketteki araçlar: `memmet.py`, `kontrol.py`, `seslendir.py`, `ai84.py`, `capcut_film.py`,
  `notlari_oku.py`, `yeni_film.py`, `paketle.py`, `kurulum.py`, `kurgu_koprusu/`.
- Belgelerde anlatılan ama pakette OLMAYAN araçlar (yeniden yazılmalı):
  `plan_kurgu.py`, `dudak_denetim.py`, `diyalog_esitle.py`, `ses_katmani.py`, `gemini_paket.py`,
  `gemini_al.py`, `gemini_muzik.py`, `renk_cila.py`, `taslak_fark.py`, `animatik.py`, `birlestir.py`,
  `jenerik.py`, `shorts_mp4.py`, `kalite_denetim.py`, `memmet_topla.py`, `izleme_paketi.py`.
- Hikâye odası, habersiz seyirci, yönetmen, süreklilik denetçisi, kurgu izleme denetçisi
  şimdiye kadar elle yürütülen Claude ajanlarıydı → kodlanmış, tekrar edilebilir aşamalar olmalı.
- Bilinen sınırlar: gerçek müzik kaynağı yok, kapak üretimi ve YouTube yükleme otomatik değil,
  Flow "olağan dışı etkinlik" kısıtları tek sağlayıcıya bağımlılık yaratıyor.

## Yapılacaklar (öncelik sırasıyla)
1. **Orkestratör** `film.py`: aşama aşama, kaldığı yerden devam eden (durum dosyası), her aşamanın
   girdisi/çıktısı tanımlı hat. Kredi harcayan aşamalar en sonda; önce kâğıt üstü kalite kapıları.
2. **Senaryo/yönetmen aşamaları** (Claude API, model `claude-opus-5-5`): brifing → A/B öneri →
   3 partilik yapı (8 başlık) → habersiz seyirci puanı → v2 → yönetmen planı + süreklilik listesi →
   `SAHNELER.json` (mevcut şemaya uyumlu). Puan eşiğine (ör. 8/10) ulaşana kadar döngü.
   İstem kuralları ve filtre yasaklı kelime listesi koda gömülü doğrulayıcı olsun.
3. **Sağlayıcı soyutlaması**: görsel/video/ses/müzik için arayüz. Flow (Memmet, yerelde),
   API sağlayıcıları (Veo/Kling/kie.ai, ElevenLabs/AI84, müzik) ve testler için `sahte` sağlayıcı.
   Bir sağlayıcı kısıtlanınca diğerine geçebilsin. Anahtarlar yalnız `AYARLAR/` veya ortam değişkeni.
4. **Eksik araçları yeniden yaz** (yukarıdaki liste), mevcut araçlarla aynı stil ve klasör yapısı.
5. **Kalite kapıları**: görsel süreklilik denetimi (görüntü modeliyle), dudak denetimi, LUFS
   eşitleme, kalite_denetim (siyah kare/donma/sessizlik), kurgu izleme denetimi (kare paketi →
   habersiz seyirci). Her kapı rapor üretir ve gerekirse yeniden üretim kuyruğu çıkarır.
6. **Yayın**: jenerik, kapak (KARARLAR.md'deki kalıp), YouTube başlık/açıklama/bölüm/etiket paketi,
   3 Short. Yükleme isteğe bağlı ve onaylı.
7. **Testler**: `sahte` sağlayıcılarla uçtan uca `ORNEK_3_SAHNE` üzerinden çalışan test; ağ/kredi yok.
8. **Kullanıcı belgeleri**: `BASLA_BURADAN.txt` güncel, yeni `.bat` dosyaları.

## Kurallar
- Bot tespitini atlatma yok; Flow uyarısında dur (`03_DERSLER.md`).
- Gizli bilgi yazma, loglama, commit etme. `AYARLAR/` içindeki anahtar dosyaları boş kalır.
- Kullanıcının mevcut dosya yollarını (Windows, `C:\Users\Soysal\Desktop\YZ_FILM`) bozma;
  yollar ayar dosyasından okunsun.
- Küçük, anlamlı commit'ler; her büyük parça ayrı PR olabilir.
