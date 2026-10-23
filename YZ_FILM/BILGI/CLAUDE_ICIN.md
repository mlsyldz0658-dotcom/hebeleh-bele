# CLAUDE İÇİN: YZ_FILM sistemine hızlı giriş

Bu klasörü açan Claude oturumu önce bu dosyayı, sonra `KARARLAR.md`'yi okumalı. `FLOW_KESIF.md`'yi Memmet bakımı gerektiğinde oku.
Kullanıcı Türkçe konuşur, samimi bir dil kullanır ("kanka"). Teknik bilgisi az: her şeyi adım adım, .bat dosyalarıyla ver.

## Sistem (ARACLAR/)
| Program | Görev | Komut |
|---|---|---|
| `memmet.py` | Google Flow'u gerçek Chrome + Playwright (CDP, port 9333, profil `AYARLAR/memmet_profil`) ile sürer. Görsel, sonra video (Kareler modu). Sonucu istem metninden tanır, `SIRALI_GORSEL/NNN.jpg` ve `SIRALI_VIDEO/NNN.mp4` olarak indirir. Sonra seslendir ve capcut_film'i zincirler | `python memmet.py <film> [--asama gorsel\|video] [--parti 1,2] [--sahne 3,7] [--kurgu-yok] [--giris]` |
| `kontrol.py` | Elle indirilen zip/dosyaları CLIP ile sahnelere eşleştirir. RAPOR.html, EKSIKLER.txt üretir; DUZELT.txt komutlarını uygular | `python kontrol.py <film>` |
| `seslendir.py` | Konuşmayı whisper ile bulur, demucs ile ortamı ayırır, AI84 (ElevenLabs v4) ile sabit sesi üretip konuşma süresine sığdırır | `python seslendir.py <film>` |
| `capcut_film.py` | pycapcut ile CapCut taslağı kurar. Kanallar: Klipler (1080p büyütülmüş), Bantlar, Baslik, Altyazi, NOTLAR, Diyalog, Ortam, Muzik | `python capcut_film.py <film>` |
| `notlari_oku.py` | Kullanıcının CapCut'ta eklediği yazıları bulur, sahne numarasına bağlar → `KURGU/NOTLARIM.txt` | `python notlari_oku.py <film>` |
| `yeni_film.py` | Boş film klasörü kurar | `python yeni_film.py AD` |
| `kurulum.py` | Yeni bilgisayar kurulumu ve kontrolü | `KURULUM.bat` |

Gizli bilgiler `AYARLAR/` klasöründe: `ai84_anahtar.txt`, `telegram_bot.txt`, `memmet_profil/`, `MEMMET_AYAR.json`. Anahtarları ASLA yazdırma; dosyayı okurken maskele.

## SAHNELER.json şeması
```json
{
 "film": "EMBERFALL",
 "baslik": "She Raised the Dragon They Ordered Her to Kill | EMBERFALL | Full Movie 4K 2026",
 "altyazi_dili": null,
 "karakterler": {
  "mara": {"ref": "01_KARAKTERLER/mara.jpg", "ses": "<elevenlabs voice_id>", "ses_adi": "Meaghan"}
 },
 "sahneler": [
  {"no": 1, "parti": 1, "referans": ["mara"],
   "amac": "Mara yavruyu ilk kez görüyor", "duygu": "korku → şefkat",
   "gorsel_istem": "...", "gorsel_istem_yedek": "...",
   "hareket_istem": "...", "hareket_istem_yedek": "...",
   "bitis_karesi": 12,
   "motor": "flow",
   "replik": {"karakter": "mara", "metin": "Easy, little one.",
              "cumleler": [{"en": "Easy, little one.", "tr": "Sakin ol, küçüğüm."}]}}
 ]
}
```
- `bitis_karesi`: isteğe bağlı. O sahnenin görseli bitiş karesi olur (yumuşak geçiş).
- `motor`: isteğe bağlı. `flow` dışındaysa (`kling`, `seedance`) Memmet o sahneyi atlar.
- `altyazi_dili`: `"tr"` ise CapCut'a Türkçe altyazı konur. Normal filmlerde `null`; İngilizce SRT her zaman KURGU'ya yazılır.

## Senaryo ve istem kuralları (deneyimle öğrenildi)
1. **Referans:** Her sahneye YALNIZCA görünen karakterlerin referansı verilir. 3 referans birden verilince Flow yüzleri karıştırır. İki konuşan karakter aynı kareye konmaz; karşılıklı çekim kullanılır.
2. **Konuşma:** Her klipte tek kişi konuşur, replik ≤ 8 saniyeye sığar. Hareket isteminde `He says: "..."` biçimi kullanılır.
3. **Sahne ayrışması:** Art arda benzeyen çekimler farklılaştırılır (geniş/yakın, önden/arkadan, ışık). Bu hem eşleştirme belirsizliğini azaltır hem filmi zenginleştirir.
4. **Riskli sahneler:** Şiddet, kan, ölü beden gibi ifadeler içeren sahnelere `*_yedek` istem yazılır (yumuşatılmış, tepki yüzü ya da dolaylı anlatım).
5. **Partiler:** 20 sahnelik partiler; mümkünse sahne sınırından bölünür.
6. **Kare-video tutarlılığı:** Video her zaman o sahnenin görselinden (Kareler modu) üretilir. İçerik öğeleri modu karakterli sahnede karakteri kaydırır.
7. **Süre:** 35-40 dk film ≈ 250-300 klip (8 sn). Geçiş ve manzara çekimleri kısa tutulur; kullanıcı pilotta "gereksiz uzun" notu verdi.
8. **Kanal formatı ve başlık/kapak kalıbı:** `KARARLAR.md`.

## Akış
`yeni_film` → senaryo (önce Türkçe özet, onay) → SAHNELER.json → karakter referansları (kullanıcı seçer) → `MEMMET_BASLAT.bat` → RAPOR → CapCut'ta izleme ve notlar → `notlari_oku` → düzeltme (istem/replik değiştir, ilgili NNN dosyalarını sil, Memmet'i yeniden çalıştır, capcut_film) → kullanıcı render alıp yükler.

## Bilinen sınırlar / yapılacaklar
- Müzik geçici (sentez akorlar); gerçek müzik kaynağı henüz yok.
- Kapak üretimi ve YouTube yükleme otomatik değil.
- AI84 Voice Changer pahalı (≈2000 kredi/sn) ve 13.10'da bakımdaydı; TTS + zamanlama yöntemi kullanılıyor.
- Flow arayüzü değişirse `memmet.py`'deki seçiciler güncellenir (`FLOW_KESIF.md`, `_MEMMET_HATALAR/` ekran görüntüleri).
