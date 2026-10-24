# reference/hat.md — aşama listesi, kısıt ve bütçe dili (bilgi; kural taşımaz)

İçindekiler: §1 Aşamalar (üretilmiş tablo) · §2 Görev akışı · §3 Kısıt dili · §4 Bütçe dili · §5 Merdiven dili · §6 Yeniden üretmek

## §1 Aşamalar
Tablo `python .claude/bin/film.py asamalar --md` çıktısıdır (kaynak `YZ_FILM/ARACLAR/hat/asamalar.py`); elle düzenlenmez.
`beceri_denetim.py` tablonun güncel olup olmadığını denetler (eskiyse BAYRAK).
<!-- hat.asamalar:bas -->

| No | Aşama | Kim | Girdi (üreten) | Çıktı | Kapı | Tur | Tavan sonrası | Kredi | Ortam |
|---|---|---|---|---|---|---|---|---|---|
| A00 | Hazırlık ve konu | betik film.py yeni + hazirlik; ana Claude yalnız tek soruyu sorar (bulutta sormaz, D-45) | kullanıcının cümlesi (kullanici) | 00_KONU.md; HAZIRLIK.json | HAZIRLIK | 1 | kapi6 | yok | her_ikisi |
| A01 | Konu kartı ve süre (BUT0) | betik kredi.py but0, hikaye_odasi.py butce-bilgisi, evren özeti; yapimci·konu; konu-denetim | 00_KONU.md (A00); evren özeti (evren); OLCUM0.json (olcum0); bakiye (bakiye) | _HIKAYE_ODASI/01_KONU_KARTI.json; _HIKAYE_ODASI/01_VARSAYIMLAR.md; KARAR_DEFTERI.md; _RAPOR/BUT0_FILM.json | KONU, BUT0 | 1 | ayni_sahip yapimci·konu → kapi6 | yok | her_ikisi |
| A02 | Brifing | betik hikaye_odasi.py brifing | konu kartı (A01); aktif hikâye dersleri (ders_defteri); ritim eşikleri (ayar) | _HIKAYE_ODASI/00_BRIFING.md | BRIFING | 1 | kapi6 | yok | her_ikisi |
| A03 | Dört öneri | hikaye-mimari ×3 (D/S/E, paralel); betik logline; + 1 (X); betik oneri-denetim | brifing (A02) | _HIKAYE_ODASI/02_oneri_<eksen>.md | ONERI | 1 | ayni_sahip hikaye-mimari → hedef_alti | yok | her_ikisi |
| A04 | Kör jüri ve seçim | juri-uyesi × 4 rol + uretilebilirlik-denetcisi·juri; betik juri-topla | anonim öneriler (A03) | _HIKAYE_ODASI/04_SECIM.json; _HIKAYE_ODASI/04_KULLANICIYA_OZET.md | JURI | 1 | ayni_sahip hikaye-mimari → hedef_alti | yok | her_ikisi |
| A05 | Yapı ve senaryo | hikaye-yazari·yapi, ·senaryo; oyuncu × ana karakter; diyalog-editoru; yapi-denetim, senaryo-denetim | 04_SECIM.json (A04); kazanan öneri (A03) | _HIKAYE_ODASI/05_YAPI.json; _HIKAYE_ODASI/06_SENARYO_v<N>.json; _RAPOR/HIKAYE_Z_v<N>.json | YAPI, SEMA | 3 | ust_sahip yapimci·doktor → ust_sahip hikaye-yazari·dar_degisiklik → hedef_alti | yok | her_ikisi |
| A06 | Kâğıt seyirci, ilk 2 dk, kilit | habersiz-seyirci·kagit ×3 (aşamalı), ·ilk2dk ×3, ozet-eslestirici ×3; seyirci_topla; devir | senaryo EKRAN bloğu (A05) | _RAPOR/HS_KAGIT_FILM_t<n>.json; HIKAYE.json; HIKAYE.md | HS_KAGIT | 4 | ust_sahip yapimci·doktor → ust_sahip yapimci·doktor → ayni_sahip yapimci·konu → kagit_urun | yok | her_ikisi |
| A06s | Ses kadrosu (kâğıt) | ses-tasarimcisi·kadro; betik ses_plani.py --profil-denetle | HIKAYE.json (A06); evren ses kayıtları (evren) | _SES/SES_PROFILLERI.json; _SES/SES_KADROSU.md | S0 | 1 | hedef_alti | yok | her_ikisi |
| A07a | Harita, kroki, kart tarifleri | dilim.py (parti dilimleri); yonetmen·harita × parti → kart-tasarimcisi; kroki.py --karsilikli/--ciz | HIKAYE.json (A06); evren mekânları (evren) | _YONETMEN/HARITA_P<n>.json; _YONETMEN/KART_ISTEGI.json; _KARTLAR/KART_SPEC.json | HARITA | 1 | ayni_sahip yonetmen·harita → ust_sahip hikaye-yazari·dar_degisiklik → durdu kurgucu·sifir_kredi | yok | her_ikisi |
| A07b | Sahne grubu planları | yonetmen·plan × sahne grubu (paralel ≤ 5); betik dilim.py, plan_denetim --sahne | haritalar (A07a); HIKAYE.json (A06); kroki PNG (A07a); dersler (ders_defteri) | _YONETMEN/PLANLAR/S<k>.json | Z0 | 1 | ayni_sahip yonetmen·harita → durdu kurgucu·sifir_kredi | yok | her_ikisi |
| A07c | Birleştirme, K0, Z0, T0, BUT1 | betik plan_birlestir, dunya_defteri, kroki --tum, plan_denetim --tum, zaman_cizelgesi, kredi.py but1, olcek.py, cekim_listesi | planlar (A07b); evren karakter kayıtları (evren) | SAHNELER.json; DUNYA_DEFTERI.json; _RAPOR/K0_FILM.json; KURGU/surumler/KURGU_PLANI_T0.json; URETIM_ONIZLEME.json | K0, Z0, BUT1 | 3 | durdu kurgucu·sifir_kredi | yok | her_ikisi |
| A07d | Kâğıt plan eleştirisi | plan-elestirmeni ×3 ∥ uretilebilirlik-denetcisi·plan ×3 ∥ sureklilik-denetcisi·kagit ×3 | çekim listeleri (A07c); K0 BAYRAK'ları (A07c) | _RAPOR/PLAN_ELESTIRI_P<n>_t<n>.json | PLAN_ELESTIRI | 2 | ayni_sahip yonetmen·onarim → ust_sahip hikaye-yazari·dar_degisiklik → durdu kurgucu·sifir_kredi | yok | her_ikisi |
| A07e | Plan seyircisi | habersiz-seyirci·plan ×3/parti; ozet-eslestirici; seyirci_topla | SAHNELER.json (A07c) | _RAPOR/HS_PLAN_P<n>_t<n>.json | HS_PLAN | 2 | ust_sahip yapimci·doktor → kagit_urun | yok | her_ikisi |
| A08 | Ses tasarımı ve müzik planı | ses_plani --taslak; ses-tasarimcisi·tasarim × sahne grubu, ·muzik; muzik.py --kagit; S0 | SAHNELER.json (A07c); DUNYA_DEFTERI.json (A07c); evren müzik (evren) | _SES/SES_<S>.json; _SES/SES_TASARIMI.md; MUZIK/muzik_listesi.json; _RAPOR/S0_FILM.json | S0 | 1 | ayni_sahip ses-tasarimcisi·tasarim → hedef_alti | yok | her_ikisi |
| A09 | İstem derleme ve kâğıt sonu | betik istem_derle --hareket, istem_denetim, kamera_agaci | SAHNELER.json (zanaat + ses) (A07c); ses tasarımı (A08) | SAHNELER.json; KAMERA_AGACI.json; _RAPOR/ISTEM_FILM.json; KAGIT_TAMAM.json | ISTEM | 3 | durdu kurgucu·sifir_kredi | yok | her_ikisi |
| A10a | Yerel kurulum ölçümü | betik kurulum.py --dogrula, olcum/ses.py --kontrol | kurulum (kurulum) | _RAPOR/KURULUM_FILM.json | KUR | 1 | hedef_alti | yok | yerel (bulutta test yok) |
| A10b | Telaffuz testi | betik ses_sec.py --telaffuz (yerelin ilk işi) | uydurma adlar (A06) | _RAPOR/S1a_telaffuz.json | S1a | 1 | ust_sahip hikaye-yazari·dar_degisiklik → hedef_alti | ai84 | yerel |
| A10c | Ses seçimi, motor kıyası, efekt | betik ses_sec.py --ara/--olc/--sec; yakın puanda ses-tasarimcisi·kadro | ses profilleri (A06s) | _RAPOR/S1_FILM.json | S1 | 1 | ayni_sahip ses-tasarimcisi·kadro → hedef_alti | ai84 | yerel |
| A10d | Kartlar | istem_derle --kart → gemini_paket (kullanıcı taşır) → gemini_al; kart_denetim + kare-tarifcisi·kart; yonetmen·kart_secimi | KART_SPEC.json (A07a) | _RAPOR/KART_KAPISI.json; _KARTLAR/KART_SECIM.json | KART | 2 | ayni_sahip kart-tasarimcisi → hedef_alti yonetmen·kart_secimi | yok | yerel |
| A11 | Başlangıç görselleri, G1 ilk geçiş, kapak adayları | istem_derle --gorsel, gemini_paket → gemini_al; kare-tarifcisi·g1; kare_denetim --karar; sureklilik-denetcisi·hakem → kare_denetim --hakem; kapak | SAHNELER.json (A09); kilitli kartlar (A10d) | SIRALI_GORSEL/NNN.jpg; _RAPOR/G1_P<n>_B<k>.json; KUYRUK/YENIDEN_URET.json; YAYIN/KAPAK_SPEC.json | G1, HS_KAPAK | 2 | hedef_alti | yok | yerel |
| A12 | Animatik | kurgu_uygula, seslendir --animatik, zaman_cizelgesi T1, muzik, ses_katmani, son_miks, kurgu_render; kesici + kesme simülasyonu; habersiz-seyirci·animatik ×3; bilgi paketi | görseller (A11); sesler (A10c); HIKAYE.json (A06) | ANIMATIK/animatik_v<N>.mp4; _RAPOR/HS_ANIMATIK_FILM_t<n>.json; KURGU/surumler/KURGU_PLANI_T1_v<N>.json | HS_ANIMATIK | 3 | ust_sahip yapimci·doktor → kagit_urun | ai84 | yerel |
| A13 | Kesin bütçe BUT2 | betik kredi.py but2, olcek.py; hat-denetcisi | URETIM_ONIZLEME (A07c); kuyruk (A11); OLCUM0 (olcum0); animatik imzası (A12) | URETIM_ONIZLEME.json; URETIM_ONIZLEME.md; _RAPOR/HAT_BUT2.json | BUT2, HAT | 1 | ayni_sahip hat-denetcisi → hedef_alti | yok | yerel |
| A14a | Dikey kesit | blok_plani --kesit; Memmet elle (kullanıcı GÖNDER'e basar); V1–V3; kesit seyircisi; ders-editoru (PILOT) | SAHNELER.json + hareket istemi (A09); G1 GEÇ görseller (A11); BUT2 (A13) | KESIT/kesit_v<N>.mp4; _RAPOR/PILOT_FILM.json | V2, HS_KESIT, PILOT | 2 | durdu kurgucu·sifir_kredi → hedef_alti | flow+ai84 | yerel |
| A14 | Video blokları | blok_plani → Memmet (elle) → V1/SC1 → film.py bekle --blok → V2, V3, kare_zinciri + G1Z → kuyruk.py | SIRALI_GORSEL (G1 GEÇ + SHA1) (A11); hareket_istem (A09); PILOT_FILM.json (A14a) | SIRALI_VIDEO/NNN.mp4; KUNYE/NNN.json; KREDI_DEFTERI.jsonl | V2, G1Z | 3 | ayni_sahip yonetmen·onarim → durdu kurgucu·sifir_kredi | flow | yerel |
| A15 | Ses | betik seslendir --parti, ses_donustur, ses_karar; gri bantta hikaye-yazari·replik_kabul | klipler (A14); evren sesleri (evren); diyalog.json (A12) | SESLER/diyalog.json; _RAPOR/S2_FILM.json | S2 | 2 | durdu kurgucu·sifir_kredi | flow+ai84 | yerel |
| A16 | Kurgu | plan_kurgu, diyalog_esitle, ses_katmani T2 + muzik --yerlestir, son_miks, kurgu_render, dudak_denetim, kurgu_denetim (Z3); kesici + kesme simülasyonu; habersiz-seyirci·kurgu ×3; renk_cila, buyut; capcut_film; arsivle | videolar (A14); diyalog.json (A15); raporlar (A14) | KURGU/KURGU_PLANI.json; KURGU/onizleme_v<N>.mp4; _RAPOR/Z3_v<N>.json; _RAPOR/HS_KURGU_FILM_t<n>.json; KURGU/son_capcut_projesi.json; KURGU/altyazi_en.srt | Z3, HS_KURGU | 3 | ayni_sahip kurgucu·duzelt → hedef_alti | flow | yerel |
| A16n (isteğe bağlı) | Kullanıcı notu | beceri film-not → taslak_fark, notlari_oku; kurgucu·not; kurgu_uygula; kurgu_denetim --hepsi; capcut_yama | kullanıcının notu ya da CapCut düzenlemesi (kullanici); kurgu (A16) | KURGU/TASLAK_FARK.json; NOTLARIM.json; NOT_CEVAPLARI.md; _RAPOR/YAMA_v<N>.json | NOT | 1 | hedef_alti | flow | yerel |
| A17 | Yayın | capcut_film --yayin; kullanıcı 4K dışa aktarır; kalite_denetim --final; jenerik; kapak; yayin-paketcisi; shorts_mp4; arsivle | yayın taslağı (A16); HIKAYE.json (A06); KANAL_TESHIS.md (olcum0) | YAYIN/<FILM>_4K.mp4; YAYIN/YAYIN_DOGRULAMA.json; YAYIN/PAKET.json; YAYIN/SHORTS/*.mp4 | S8, YAYIN | 1 | hedef_alti | yok | yerel |
| A17y (isteğe bağlı) | Yükleme (isteğe bağlı) | betik youtube_yukle.py (kullanıcının YUKLE.bat onayıyla) | YAYIN/PAKET.json (A17); YUKLE.bat onayı (kullanici) | YAYIN/YUKLEME.json | — | 1 | hedef_alti | yok | yerel (bulutta test yok) |
| A18 | Kapanış ve öğrenme | ders_derle; ders-editoru; hikaye-yazari·evren; evren.py --film-sonu; FILM_SONU_RAPORU; yedek; arsivle | bütün raporlar (A17); ders ham kayıtları (ders_defteri) | FILM_SONU_RAPORU.md | DERS | 1 | hedef_alti | yok | her_ikisi |
| A18a (isteğe bağlı) | Yayın sonrası analiz | betik yayin_analiz.py; yayin-paketcisi·izleme (48 sa, 7 gün, 28 gün) | YouTube Studio CSV'si (youtube); yayın paketi (A17) | _RAPOR/YAYIN_ANALIZ_<gun>.json | — | 1 | hedef_alti | yok | yerel (bulutta test yok) |

Basamaklar (§1.5): ayni_sahip → ust_sahip → durdu (kurgucu·sifir_kredi) → hedef_alti; feragat edilemeyen HATA (güvenlik, filtre, kimlik, şema) hiçbir zaman üretime gitmez. Seyirci kapılarında KISMI = kapı sağlandı, hedef değil (§1.4).
<!-- hat.asamalar:son -->

## §2 Görev akışı (bir aşamanın içi)
1. Aşama açılır → `film.py` ilk grubun görevlerini kurar (GOREV.json + ISTEM.md + GIRDI/).
2. Grup sırası iş sırasıdır: betik grubu (paket, dilim, kör paket) → ajan grubu (paralel) → betik grubu (topla, denetle, kapı raporu).
3. Kapı raporu `_RAPOR/<KAPI>_<kapsam>[_t<tur>].json` GEÇ ise aşama `tamam`; KISMI ise (seyirci kapısı) hedef altı, tur sürer ya da `kismi`.
4. HATA ise tur sayacı artar; tur tavanı dolunca `tavan_sonrasi` merdiveninin sonraki basamağı görev olarak açılır (§5).
5. Girdi imzası değişirse aşama `bayat` olur ve yeniden açılır; kredili çıktı silinmez, kuyruğa girer.

## §3 Kısıt dili (kullanıcıya söylenen; ayrıntı KULLANICI_DILI.md)
| Durum | Kod | Anlamı | Kim çözer |
|---|---|---|---|
| Flow uyarısı / hesap kilidi | 7 KISIT | yeni gönderim yok, sayfa işlemi yok; başka hesap ve başka servis yok | kullanıcı (UYARI_GECTI.bat; koşulları flow_yuk denetler) |
| Doğrulama, reCAPTCHA, oturum düştü | 2 KULLANICI | Memmet bekler ve çıkar; kullanıcı tarayıcıda kendisi giriş yapar | kullanıcı |
| Bulut oturumu | 4 ORTAM | üretim yalnız kullanıcının Windows bilgisayarında | FILM_SETI.bat |
| Mola, GPU, kullanım sınırı, disk, token | 8 BEKLE | süreli bekleme; `film.py bekle` ya da yeniden açılış | sistem |
| Görsel günü | (sıra kuralı 7) | yoğun görsel düzeltme yapılan gün video gönderilmez | sistem |

## §4 Bütçe dili
- BUT0 (A01): süre seçimi. Ö0-b ölçümü yoksa ya da ölçülemediyse süre 1800 sn'dir (D-05); kullanıcıya bilgi olarak söylenir.
- BUT1 (A07c): planlardan kredi tahmini; tavan aşılırsa 5 BÜTÇE (yazılmış film kısaltılmaz).
- BUT2 (A13): kesin bütçe; tahmin ≤ bakiye × (1 − `guvenlik_payi`) ve ≤ tavan; `hat-denetcisi` GİT/GİTME.
- BUTK: her kredili madde (yeniden çekim, ses dönüşümü) kendi dilim payından düşer; dilim dolunca 0 kredi çözüm (`kurgucu·sifir_kredi`).
- Sayıların tek kaynağı `olcek.py` ve `kredi.py`dir; belgede sabit kredi ya da gün sayısı yazılmaz.

## §5 Merdiven dili (§1.5 tavan sonrası)
| Basamak (`tur`) | Ne olur |
|---|---|
| `ayni_sahip` | aynı sahibin başka kipi 1 tur (ör. `yonetmen·onarim`, `hikaye-yazari·revizyon`) |
| `ust_sahip` | plan/sahne maddesi `hikaye-yazari·dar_degisiklik`, film maddesi `yapimci·doktor` |
| `durdu` | plan ya da sahne durdurulur, `kurgucu·sifir_kredi` zorunlu çözümü yazar, BAYRAK, hat sürer |
| `hedef_alti` | kapı sağlandı ama hedef değil; `FILM_SONU_RAPORU.md`'ye yazılır, hat sürer |
| `kagit_urun` | seyirci kapısı sağlanmadı: senaryo (ve varsa animatik) yüzüne vur raporuyla teslim, videoya geçilmez |
| `kapi6` | film düzeyi feragat edilemez HATA ya da kod hatası: 6 KAPI, `film-gelistir` işi |
Feragat edilemeyenler (güvenlik, filtre ve yaş sözcüğü, yasak öğe, kimlik, şema HATA'sı) üretime ya da yayına hiç gitmez.

## §6 Yeniden üretmek
`python YZ_FILM/ARACLAR/beceri_denetim.py --hat-yenile` bu dosyanın §1 tablosunu `hat/asamalar.py`'den yeniden yazar (geri kalanı korunur).
