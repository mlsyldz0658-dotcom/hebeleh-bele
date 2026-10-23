# OpenMontage ve Sonradan Eklenen Araçlar

## OpenMontage (github.com/calesthio/OpenMontage)
- **Ne:** Ajan tabanlı açık kaynak video üretim sistemi (AGPL-3.0). 13 hazır hat (cinematic, animated-explainer, clip-factory…), 100+ araç, Remotion/HyperFrames ile render.
- **Kurulum yeri:** `C:\Users\Soysal\Desktop\YZ_FILM\OpenMontage` (kendi `.venv`'i, ≈1,2 GB). Kullanıcı isteği: **silinmeyecek.** Claude Code o klasörde açılınca kendi `CLAUDE.md` / `AGENT_GUIDE.md` kurallarıyla çalışır.
- **Değerlendirme (18.10):**
  - Anahtarsız çalışanlar: Remotion render (demo), analiz (sahne bulma, kare örnekleme, ses enerjisi), altyazı üretme ve kelime kelime yanan altyazı, dikey kadraj (auto_reframe).
  - Çalışmayanlar: video 0/31, görsel 0/23, ses 0/13, müzik 0/5 — hepsi ücretli API anahtarı ister (FAL, Veo API, Kling, ElevenLabs, Suno…). Flow aboneliğini kullanamaz, CapCut taslağı vermez.
  - Sonuç: kendi hattımızın yerine geçmez; işe yarayan parçaları alındı.
- **Düzeltme:** yüz takibi yeni mediapipe sürümüyle bozuk → `mediapipe==0.10.14` sabitlendi.

## OpenMontage'dan alınanlar (ARACLAR'da)
| Araç | Ne yapar |
|---|---|
| `om_kopru.py` | OpenMontage araçlarını kendi venv'inde çalıştırır: `altyazi_yak()` (Remotion kelime altyazı, ad düzeltme listesi), `yuz_izle()` |
| `shorts_mp4.py` | Dikey Short: kanca yazısı, kelime kelime altyazı, yüz + sıcak ışığa göre akıllı kadraj, -14 LUFS, son kart, otomatik kalite denetimi |
| `kalite_denetim.py` | Siyah kare / donma / sessizlik / LUFS / tepe taraması (OpenMontage visual_qa fikri, ffmpeg ile) |

## Gemini ajanı (argon) entegrasyonu
- `gemini_paket.py`: görsel, kart ve video paketleri (GOREV.txt + ISTEMLER.txt + REFERANSLAR.zip; video paketinde GORSELLER.zip + AKIS.txt + SUREKLILIK.md).
- `gemini_al.py`: ZIP'i içeri alır, 16:9 kırpar, kartları kaydeder, işi biten paketi geri dönüşüme atar.
- Ajan görsel üretir ve süreklilik denetler; **video üretemez.**

## Memmet'e son eklenenler
- Yarı otomatik mod (`--mod elle`, başka sekmede geliştirildi, buraya alındı): Memmet hazırlar, gönder'e insan basar.
- `--tek-tek`: kare ve referansları sahnesi gelince tek tek yükler (toplu yükleme uyarı getiriyordu).
- `--yeni-proje`: ısınmış Flow projesini bırakıp yenisinde başlar.
- Önceki sürümün yedekleri: `ARACLAR\_memmet_yedek_*.py`.
