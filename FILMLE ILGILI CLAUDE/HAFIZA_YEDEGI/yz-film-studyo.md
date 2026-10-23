---
name: yz-film-studyo
description: "Ana çalışma klasörü Masaüstü\\YZ_FILM (YZ sinema kanalı); KONTROL sistemi, film yapısı, kararlar"
metadata:
  node_type: memory
  type: project
  originSessionId: c02834a3-78d7-42ef-8b9f-3353299f1117
  modified: 2026-10-13T22:53:52.646Z
---

13 Ekim 2026'da kullanıcı temiz bir çalışma klasörü istedi: `C:\Users\Soysal\Desktop\YZ_FILM`.

**İçerik:**
- `00_BENI_OKU.txt`: kullanım kılavuzu.
- `BILGI\KARARLAR.md`: kanal ve üretim kararlarının tek kaynağı; araştırma notları da `BILGI\` altına kopyalandı.
- `ARACLAR\kontrol.py`: KONTROL.bat'ın çalıştırdığı program.
  - Flow zip'lerini açar ve siler; referansları ayıklar.
  - Görselleri CLIP + Flow başlığı + Macar ataması ile sahnelere eşleştirir. Güveni yer değiştirme farkıyla ölçer.
  - Videoları ilk kareden eşleştirir.
  - Çıktılar: `SIRALI_GORSEL`, `SIRALI_VIDEO`, `ALTERNATIFLER`, `RAPOR.html`, `EKSIKLER.txt`.
- `ARACLAR\ai84.py`.
- `ARACLAR\kurgu_koprusu`: kullanıcının CapCut proje üreticisi V5 (pycapcut 0.0.3).

**Hat tamam (13 Ekim, kullanıcı onayladı):** KONTROL.bat → CAPCUT_PROJESI_OLUSTUR.bat. Bu ikincisi seslendir.py'yi çalıştırır (whisper + demucs + AI84 v4 sabit sesler) ve ardından capcut_film.py'yi. capcut_film.py pycapcut ile yedi kanallı bir CapCut projesi kurar: Klipler, Bantlar, Baslik, Altyazi, Diyalog, Ortam, Muzik. Kullanıcı CapCut'ta açıp beğendi.

**Memmet Auto (14 Ekim, çalışıyor):** `ARACLAR\memmet.py`, Python + Playwright. Gerçek Chrome'u kendi profiliyle açıyor (`ARACLAR\memmet_profil`, port 9333) ve CDP ile bağlanıyor. Kullanıcı Flow deneme hesabıyla bir kez giriş yaptı.
- Flow'da her film için proje açıp adını veriyor.
- Referansları yüklüyor; görsel ve videoyu (Kareler modu) istem metninden tanıyıp NNN.jpg / NNN.mp4 olarak indiriyor.
- MEMMET_TEST (3 sahne) uçtan uca başarılı oldu: 3/3 görsel, 3/3 video, eşleşme doğrulandı.
- Flow ayrıntıları `BILGI\FLOW_KESIF.md`'de.
- Kullanıcı kararları: gece iki aşama da çalışacak; 2-3 partide bir 5/10/15 dk rastgele mola; reCAPTCHA çıkarsa çözen kullanıcı (otomatik çözme reddedildi); Telegram bildirimi istendi, bot henüz kurulmadı.

**Taşınabilir paket (14 Ekim):**
- Gizli dosyalar `YZ_FILM\AYARLAR`'da: ai84/telegram anahtarları, memmet_profil, MEMMET_AYAR.json.
- Kurulum ve başlangıç dosyaları: `KURULUM.bat` (ARACLAR\kurulum.py), `YENI_FILM.bat`, `BASLA_BURADAN.txt`, `BILGI\CLAUDE_ICIN.md`.
- `ARACLAR\paketle.py` ile zip oluşturuluyor: AYARLAR içeriği ve çıktılar girmiyor, anahtar sızıntısı taranıyor. Masaüstü + `D:\YZ_FILM_YEDEK`, 8.9 MB. Sıfır kurulum testi geçti.
- 20 sahnelik büyük test (FILMLER\MEMMET_PILOT20) kullanıcı isteğiyle durduruldu; henüz yapılmadı.

**Film yapısı:** Her film `FILMLER\<AD>\` altında; içinde `SAHNELER.json` ve `KONTROL.bat` var. Pilot `FILMLER\PROJE_PILOT` ile test edildi: 20/20 görsel, 20/20 video doğru.

Eski klasörler (`Masaüstü\demo deneme`, `Masaüstü\PILOT PAKET`) silinmedi. Kullanıcı onaylarsa temizlenecek.

**Why:** Kullanıcı konuşma çok uzadığı için yalnızca gerekli bilgilerin kaldığı temiz bir yapı istedi. Adım adım ilerlemek istiyor; sıradaki iş Kurgu Köprüsü ile pilotun CapCut projesi, sonra 30-40 dk filmler.

**How to apply:** Yeni işleri YZ_FILM içinde yap. Kararlar değişince KARARLAR.md'yi güncelle. Kullanıcı bitmiş mp4 değil, önce CapCut'ta görmek istiyor. İlgili: [[youtube-nis-arastirmasi]], [[ai84-ses-servisi]], [[yz-dizi-demolari]].
