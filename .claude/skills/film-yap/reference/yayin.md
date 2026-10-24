# reference/yayin.md — yayın paketi, kapak, yükleme, film sonu öğrenme (A17–A18a; bilgi, kural taşımaz)

İçindekiler: §1 Akış · §2 Yayın paketi · §3 Kapak · §4 Yükleme · §5 Kapanış ve dersler · §6 Yayın sonrası analiz

## §1 Akış
| Aşama | Ne | Kim |
|---|---|---|
| A17 | yayın taslağı → kullanıcı CapCut'tan 4K 24 fps dışa aktarır → `YAYIN/` → final kalite + mux kanıtı → jenerik, kapak, paket, Shorts | betikler + `yayin-paketcisi·paket/·kapak` |
| A17y | yükleme (varsayılan kapalı) | `youtube_yukle.py`, yalnız `YUKLE.bat` onayıyla |
| A18 | dersler, evren güncellemesi, film sonu raporu, yedek | `ders_derle`, `ders-editoru`, `hikaye-yazari·evren`, `evren.py` |
| A18a | 48 sa / 7 gün / 28 gün analiz | `yayin_analiz.py`, `yayin-paketcisi·izleme` |

## §2 Yayın paketi (`YAYIN/PAKET.json`)
Başlık (≤ `baslik_karakter_max` kr), açıklama, bölüm adları (≤ `bolum_sayisi_max`), etiketler, YZ beyanı alanı (dolu), Shorts ve fragman
listesi, kanal teşhisine (`KANAL_TESHIS.md`) dayalı strateji notu. `yayin_paketi --dogrula` başlık, bölüm kuralları, beyan ve "kill" sözcüğü
(BAYRAK) denetler. Yayın stratejisti başlığı kanıtla seçer; kapak ve başlık birlikte düşünülür.

## §3 Kapak
A11'de 8–12 aday (`kapak_aday_min`); küçük boyutta (`kapak_kucuk_okunurluk`) yüz ve yaratık seçilir olmalı; `kare-tarifcisi·kapak` (kör) +
`habersiz-seyirci·kapak` ikili karşılaştırma. A17'de `yayin-paketcisi·kapak` son seçimi gerekçeleriyle yazar (kullanıcıya bilgi).

## §4 Yükleme
Varsayılan kapalıdır. Kullanıcı o film için `YUKLE.bat` ile açık onay verirse `youtube_yukle.py` yükler (OAuth P2). Onay yoksa paket
`YAYIN/`'da hazır bekler; yükleme kullanıcının işidir.

## §5 Kapanış ve dersler (A18)
`ders_derle` film boyunca toplanan ham ders kayıtlarını (`BILGI/DERSLER/ham/`) birleştirir; `ders-editoru` aday kural yazar (yalnız yeni dosya;
korkuluklar: kanıt sayısı, kaynak, gevşetmeme). `hikaye-yazari·evren` evren taslağını, `evren.py --film-sonu` kanonu günceller.
`FILM_SONU_RAPORU.md`: açık eksikler, `hedef_alti` maddeleri, ölçülemeyenler, harcama. Evren ve ders yedeği D diskine (sha1 listesi).

## §6 Yayın sonrası analiz (A18a)
Kullanıcı YouTube Studio'dan isteğe bağlı CSV verirse gösterim, tıklama oranı, ortalama izleme ve tutma eğrisi okunur; ders kayıtları
`kaynak: gercek_seyirci` ile yazılır. Veri yoksa "ölçülemedi"; film akışını engellemez.
