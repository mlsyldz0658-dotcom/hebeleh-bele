# Araçlar (C:\Users\Soysal\Desktop\YZ_FILM\ARACLAR)

Hepsi Python 3.10 ile çalışır: `C:\Users\Soysal\AppData\Local\Programs\Python\Python310\python.exe`. Her dosyanın başında kullanım açıklaması var (`python <dosya>.py` tek başına çalıştırılınca yardımı basar).

## Üretim (Google Flow)
| Araç | Ne yapar |
|---|---|
| `memmet.py` | **Memmet Auto.** SAHNELER.json'daki sahneleri Google Flow'da üretir (görsel → video). Chrome'u kendi profiliyle (port 9333) açar. Seçenekler: `--asama gorsel/video`, `--parti`, `--sahne`, `--mod gece/gunduz/elle`, `--tek-tek` (kare/referansları tek tek yükle), `--yeni-proje`. Olağan dışı uyarısında durur. Yarı otomatik (`--mod elle`): hazırlar, gönder'e kullanıcı basar. |
| `memmet_topla.py` | Yeni bir şey göndermeden Flow projesinde bitmiş sonuçları bulup indirir (kredi korur). |
| `kontrol.py`, `kontak.py`, `gorsel_kontak.py` | Durum raporu, kare kontrol sayfaları. |
| `yeni_film.py` | Yeni film klasörü (.bat dosyalarıyla) kurar. |

## Gemini ajanı
| Araç | Ne yapar |
|---|---|
| `gemini_paket.py` | Görsel paketleri (`--parti`, `--sahne`), kart paketi (`--kartlar PLANLAR.json`), video paketi (`--video`: GORSELLER.zip + REFERANSLAR.zip + AKIS.txt + SUREKLILIK.md). >10 referansta otomatik ZIP. Hedef: `Masaüstü\GEMINI GORSEL ISTEM\`. |
| `gemini_al.py` | Gelen ZIP'i SIRALI_GORSEL/SIRALI_VIDEO'ya ya da kart yollarına koyar, 16:9 kırpar; işi biten paketi geri dönüşüme atar. |

## Kurgu ve ses
| Araç | Ne yapar |
|---|---|
| `plan_kurgu.py` | Yönetmen plan listesinden kurgu klasörü; TTS replikleri "kaynak/ofset/whisper" ile yerleştirir (whisper planın kendi penceresinde arar). |
| `seslendir.py`, `ai84.py` | ElevenLabs (AI84 aracısı) ile sabit karakter sesleri, önbellekli (aynı cümle iki kez ücretlenmez). |
| `ses_katmani.py` | Efekt + mekân zemini tek WAV (CC0 SES_KUTUPHANESI). |
| `gemini_muzik.py` | Kullanıcının Gemini'de ürettiği müzikleri plan adına bağlı yerleştirir. |
| `capcut_film.py` | Katmanlı CapCut taslağı (Klipler, Diyalog, Efekt_Ambiyans, Muzik_Gemini, altyazı). |
| `renk_cila.py` | Taslaktaki kliplere ortak sinematik renk, saç rengi düzeltmesi. |
| `taslak_fark.py`, `notlari_oku.py` | Kullanıcının CapCut'ta sildiği/değiştirdiği planları ve yazdığı notları okur (salt okunur). |
| `animatik.py` | Video kredisi harcamadan görsel+ses taslak film. |
| `birlestir.py`, `paketle.py` | Kurgu birleştirme, paketleme. |

## Yayın ve kalite
| Araç | Ne yapar |
|---|---|
| `shorts_mp4.py` | Dikey Short MP4: kanca yazısı, kelime kelime altyazı (OpenMontage Remotion), yüz + Ember ışığına göre kadraj, -14 LUFS, son kart. |
| `shorts.py` | Eski yöntem: Shorts'u CapCut taslağı olarak kurar. |
| `kalite_denetim.py` | Siyah kare, donma, sessizlik, LUFS, tepe kontrolü. |
| `om_kopru.py` | OpenMontage araçlarını kendi venv'inde çağırır (`Masaüstü\YZ_FILM\OpenMontage`). |

## Bölüme özel betikler
- B2: `D:\YZ_FILM_ARSIV\PROJE_B2\PROJE_B2\_BOLUM2\` → `parti_kur.py`, `parti_birlestir.py`, `parti_taslak.ps1`, `izleme_paketi.py`, `dudak_denetim.py`, `diyalog_esitle.py`, `yeni_sahne_ekle.py`, `jenerik.py`, `shorts_render.py`.
- B3: `C:\...\FILMLER\PROJE_B3\_BOLUM3\_araclar\` → `sahne_aktar.py`, `kucuk_duzelt_P1.py`, `tur2_duzelt_P1.py`, `gece_video.ps1` ve B2 betiklerinin kopyaları.

## Diğer
- `SES_KUTUPHANESI\`: 62 CC0 efekt (BigSoundBank vb.) + gerçek rüzgâr/oda zeminleri; lisanslar LISANS.txt'te.
- `AYARLAR\`: Memmet ayarları, Chrome profili, anahtar dosyaları — **paylaşma/paketleme, gizli bilgi içerir.**
- `ai_uretim\`: Google Cloud Gemini 3 Pro Image ile ücretli görsel üretimi (her seferinde onay ister).
- `kurgu_koprusu\`: CapCut taslak kütüphanesi (pycapcut) köprüsü.
