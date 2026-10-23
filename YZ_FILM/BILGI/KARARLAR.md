# KARARLAR — YZ Sinema Kanalı (13 Ekim 2026)

## Kanal
- **Dil ve süre:** İngilizce, 30-45 dk YZ sinema filmleri.
- **Karakter seslendirmesi:** Yüz yok, kendi sesin yok.
- **Format:** Anlatıcı yok, belgesel yok. Karakterler konuşuyor.

### Neden bu format (YouTube API araştırması, 11-13 Ekim)
- **Manhwa/anime şeridi:** Büyük rakamların çoğu Hintçe recap kanallarından geliyor ve düşüşte. Özgün İngilizce kanal az.
- **YZ sinema şeridi:** İzleyici YZ'yi kabul ediyor; yorumlar "best AI movie", "part 2 please" gibi.
- **Kazananlar:**

  | Kanal | Sonuç |
  |---|---|
  | Relatos de Eterya | 7/7 video 1M+ |
  | Aurelume Films | 4/7 video 1M+ |
  | Cine Drop | 14M (tek video) |
  | Epic AI Films | 12-14M, tek kişi |

- **Ne tutuyor:**
  - Az ama özenli üretim (haftada 0,3-1 film)
  - Kendi seri evreni olan filmler
- **Kancalar:**
  - İnsan + yaratık/uzaylı bağı
  - İhanet, küçümsenen kahraman, geri dönüş
- **Kapak:** Fotogerçekçi sinema karesi. İnsan ve yaratık aynı karede, film afişi gibi logo, kalabalık yazı yok.
- **Başlık:** `Kanca cümlesi | SERİ ADI | Full Movie 4K 2026`
- **Tek büyük eleştiri:** Karakter tutarsızlığı. Çözüm: referanslı üretim.
- Ayrıntılı veri: `BILGI\ARASTIRMA_NOTLARI.md` (Tur 1-16), `BILGI\NIS_VERITABANI.md`, kapak örnekleri `BILGI\kazanan_kapaklar.jpg`.

## Üretim hattı
- **Görsel:** Google Flow, Nano Banana 2.1 (0 kredi). 16:9, karakter referanslı.
- **Video:** Flow, Omni 1.1 Flash. 360p, 8 sn klip ≈ 7 kredi (10 sn = 7 kredi; 8 sn ölçülmedi).
- **Otomasyon:** ViralDNA uzantısı.
  - Yazı→Sahne: istemler arasında boş satır.
  - Foto→Video: en fazla 20'li parti, Başlangıç modu.
- **Referans kuralı:** Her sahneye yalnızca içinde görünen karakterin referansını ver. 3 referans birden verilince Flow karıştırıyor.
- **İki kişilik sahneler:** Karşılıklı çekim (her çekimde tek kişi). Aynı karede iki konuşan olmasın.
- **Diyalog:** Her klipte tek kişi konuşur.
- **Sesler:** ElevenLabs v4, AI84.pro üzerinden.
  - Anahtar: `Masaüstü\ai84_anahtar.txt` (asla paylaşma).
  - **TTS:** Karakter başına 1 kredi.
  - **Voice Changer:** 13 Ekim'de bakımdaydı. Tahmini maliyet saniyede 2.000 kredi, pahalı.
  - **Yöntem:** Flow konuşmayı üretir. Konuşmanın saniyeleri whisper ile bulunur, sabit sesle TTS üretilip oraya oturtulur. Flow'un sesi demucs ile ortam sesinden ayrılır.
- **Karakter sesleri (EMBERFALL):**
  - Mara: Meaghan (mrmaApeLxpgZi4RK7oGq)
  - Voss: Gravel Midnight (M5E055lOUxMi0kJpGyE9)
- **Kurgu:** Bitmiş mp4 yerine CapCut projesi (Kurgu Köprüsü, `ARACLAR\kurgu_koprusu`). Kullanıcı önce CapCut'ta görür, dışa aktarmayı kendisi yapar.
- **Editör:** CapCut. VS Code ve Remotion gerekmiyor.

## Ölçek
- **Film boyutu:** 35-40 dk film ≈ 250-300 klip. 20'lik partiler; mümkünse sahne sınırından bölünür.
- **Flow projesi:** Her film için ayrı.
- **Disk:**
  - Çalışma C'de (dahili SSD, 137 GB boş).
  - Arşiv D'de. D harici USB disk; çalışırken kullanma, kablo çıkarsa CapCut projesi bozulur.

## Pilot (EMBERFALL, 13 Ekim)
- 20 klip, kalite iyi, karakterler tutarlı.
- KONTROL sistemi pilot verisiyle test edildi:
  - 20/20 görsel ve 20/20 video doğru yerleşti.
  - Kullanıcının elle sıralamasındaki 6↔8 hatasını kendiliğinden buldu.
- **Dikkat:** Flow dosya adları istem metni değil, Flow'un özeti. Video adları hareket istemine göre veriliyor. Bu yüzden eşleştirme görüntü içeriğine göre yapılıyor.
