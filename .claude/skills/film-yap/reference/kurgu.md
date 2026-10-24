# reference/kurgu.md — animatik, kurgu, kullanıcı notu (A12, A16, A16n; bilgi, kural taşımaz)

İçindekiler: §1 Zaman çizelgeleri · §2 Animatik · §3 Kurgu turu · §4 Kesici ve kesme simülasyonu · §5 Sıfır kredi çözümleri · §Not · §6 CapCut

## §1 Zaman çizelgeleri
`zaman_cizelgesi.py`: TH (hikâye, A05) → T0 (kâğıt planlar, A07c) → T1 (animatik, seçilmiş seslerle) → T2 (kurgu, gerçek kliplerle) → T3 (yayın).
Z1 hikâye zamanlarını (ilk eylem, ilk merak, başlık kartı, kahraman adı, risk …), Z2 duygu ve enerji eğrisini, Z3 kurgu ritmini ölçer.

## §2 Animatik (A12)
Görseller + son sesler (TTS ile seçilmiş sesler) + müzik taslağı + ses katmanı → `ANIMATIK/animatik_v<N>.mp4` ve işitsel döküm.
Habersiz seyirci × 3 (aşamalı) + ilk 2 dk × 3 (gerçek kapakla) + özet eşleştirici; tur 1'de kesici. Kapıyı yalnız bütün kareleri G1 GEÇ olan
tur açar; render süresi = T1 ± `render_sure_tolerans_kare`; yer tutucu ≤ `animatik_yer_tutucu_max_oran`. Onay imzası (`animatik: ONAYLI`)
olmadan video görevi açılmaz. Kullanıcıya `BILGI_PAKETI/animatik/` bilgi olarak verilir (onay istenmez).

## §3 Kurgu turu (A16)
`plan_kurgu` (kırpma önerisi) → ses (`diyalog_esitle`, `ses_katmani T2`, `muzik --yerlestir`, `son_miks`) → `kurgu_render --onizleme` →
`kurgu_denetim` (Z3) → kör paket → habersiz seyirci (tam film, aşamalı) + ilk 2 dk → `kurgucu·duzelt` → kuyruk. 3 tur + 1 koşullu tur
(son turda GENEL ≥ `kurgu_kurtarma_kosul_genel_artis` arttıysa). KRİTİK 0 olmadan CapCut taslağı verilmez, ya da tavan dolduysa açık eksik
raporuyla verilir (sıra kuralı 8).

## §4 Kesici ve kesme simülasyonu
`kesici` (kör) animatiği/kurguyu "nereden kesilir" gözüyle izler; `kurgu_denetim --kesme-simule` önerileri HATA'sız uygulanabilirlik için
sınar. Tur başına öneri tavanı `kesme_turu_oneri` (plan, sahne, uygulama oranı).

## §5 Sıfır kredi çözümleri (`kurgucu·sifir_kredi`)
Sırayla: kırp (kusursuz pencere ≥ eylem alt sınırı) → örtü (tepki/ekleme planı araya) → yer tutucu (animatikte) → L/J kesmeyle sesi taşı →
ekran dışı ses → köprü kartı → planı çıkar. Her çözümde `dunya_defteri` ve Z1 kurulum denetimi yeniden koşar.

## §Not — kullanıcı notu döngüsü (A16n; `film-not` becerisi)
1. `film.py notlar oku`: `notlari_oku.py` (NOTLARIM, sohbet notları) + `taslak_fark.py` (kullanıcının CapCut taslağı ↔ son sistem taslağı) salt okunur.
2. Sınıflar: (a) kullanıcının kurgu kararı → aynen ve kilitli `KURGU_PLANI`'na; (b) şikâyet → ders kaydı (`kaynak: kullanici_notu`) + kurgucu
   çözümü; (c) yeni sahne/ses isteği → kesin istek, sahibine görev.
3. `film.py notlar isle` → `kurgucu·not` görevi; `kurgu_uygula` → `kurgu_denetim --hepsi` → `capcut_yama` (klon taslak "<adı> · v<N+1>").
4. Kullanıcının kaynak taslağı değişmez; klonun öz denetimi 0 fark; notların %100'ü bir kararla kapanır (`NOT_CEVAPLARI.md`).

## §6 CapCut
`capcut_film` taslağı "YZ <FILM> v<N>" adıyla kurar; yayın taslağı (`--yayin`) NOTLAR ve Altyazı kanalı içermez (SRT YouTube'a ayrı gider).
CapCut açıkken taslağa yazılmaz; kullanıcıdan "CapCut'ı kapat" istenir ve kapanış arka planda beklenir.
