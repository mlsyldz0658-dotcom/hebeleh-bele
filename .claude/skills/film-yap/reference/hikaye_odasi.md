# reference/hikaye_odasi.md — konudan kilitli hikâyeye (A00–A06; bilgi, kural taşımaz)

İçindekiler: §1 Akış · §2 Dosyalar · §3 Kapılar ve anlamları · §4 Seyirci kapısı: kapı ve hedef · §5 Evren · §6 Sık bulgular

## §1 Akış
| Aşama | Ne üretilir | Kim | Denetim |
|---|---|---|---|
| A00 | `00_KONU.md`, `HAZIRLIK.json` | `film.py yeni`, `hazirlik` | kanca nabzı, KUR1, disk |
| A01 | `01_KONU_KARTI.json`, `01_VARSAYIMLAR.md`, BUT0 | `yapimci·konu` | `hikaye_odasi.py konu-denetim`, `kredi.py but0` |
| A02 | `00_BRIFING.md` (7 bölüm) | betik | `brifing_bolum_sayisi`, `brifing_kelime_aralik` |
| A03 | `02_oneri_<eksen>.md` × 4 (D, S, E paralel; X "kaçınılacak yol") | `hikaye-mimari` | `oneri-denetim` (10 başlık, çeşitlilik) |
| A04 | `03_juri_<rol>.json`, `04_SECIM.json`, `04_KULLANICIYA_OZET.md` | `juri-uyesi` × 4 + `uretilebilirlik-denetcisi·juri` | `juri-topla` (medyan, veto) |
| A05 | `05_YAPI.json`, `06_SENARYO_v<N>.json` | `hikaye-yazari·yapi/·senaryo`, `oyuncu`, `diyalog-editoru` | `yapi-denetim`, `senaryo-denetim` |
| A06 | kâğıt seyirci raporları, `HIKAYE.json` + `HIKAYE.md` (kilit) | `habersiz-seyirci` × 3, `ozet-eslestirici` | `seyirci_topla`, `bulgu_yonlendir`, `devir` |

## §2 Dosyalar (hepsi `<film>/_HIKAYE_ODASI/` altında; sahibi betik, ajan CIKTI'ya yazar)
- Konu kartı: konu cümlesi, kanca ailesi (`konu_kanca_aileleri`), kahraman, risk, seri bağı, `kesin_istekler`, varsayımlar.
- Öneri (10 başlık; `oneri_baslik_sayisi`): logline (≤ `logline_kelime_max` kelime), başlık (≤ `baslik_karakter_max` kr), kanca, üç parti,
  ana karakterler (konuşan ≤ `oneri_konusan_max`), mekânlar, seyirlik anlar, üretilebilirlik notu, seri kancası, NE YOK.
- Jüri paketi anonimdir: eksen adı silinir (`JURI_ANAHTAR.json` jüriye verilmez). Ölçütler `juri_olcutleri`.
- Senaryo: sahneler, replikler (R kimliği), EKRAN bloğu (seyircinin göreceği tarif), bilgi durumu, anahtar olgular (`anahtar_olgu_parti`).
- `HIKAYE.json` kilitlidir: kilitten sonra değişiklik yalnız `hikaye-yazari·dar_degisiklik` ile ve H15 bütçesinden.

## §3 Kapılar ve anlamları
| Kapı | Ne ölçer |
|---|---|
| KONU | konu üretilebilir mi (yaş/filtre, çocuk kahraman riski, yasak öğe), kanca ailesi, süre aralığı |
| BRIFING | bölüm sayısı ve uzunluk |
| ONERI | başlık sayısı, başlık uzunluğu, konuşan sayısı, filtre, dört önerinin birbirine benzerliği (`oneri_benzerlik_esigi`) |
| JURI | kazanan medyanı ≥ `juri_kazanan_min`; veto yok; beraberlikte birleştirme (`juri_beraberlik_fark`) |
| YAPI / SEMA | Z1/Z2 hikâye ölçüleri, filtre, NE YOK, bilgi durumu, ilk replik ekranda (`ilk_replik_ekranda`) |
| HS_KAGIT | §4 |

## §4 Seyirci kapısı: kapı ve hedef (§1.4)
- Kapı (hattı durdurur): KRİTİK 0 (geçerli sayılan), kritik olguların özet eşleşmesi ≥ `ozet_eslesme_kritik_min`, GENEL medyan ≥ `seyirci_kapi_genel_min`.
- Hedef (döngüyü sürdürür): GENEL medyan ≥ `seyirci_genel_esik`, her ölçüt ≥ `seyirci_olcut_min`, ORTA ≤ `kopukluk_orta_max_parti`/parti,
  ilk 2 dk `ilk2dk_devam_evet_min`/3, bütün olgular ≥ `ozet_eslesme_min`.
- Plato: iki tur üst üste GENEL artışı < max(`plato_genel_artis_min`, `seyirci_gurultu_std`) → bir kez `yapimci·doktor`, sonra durma.
- Birleştirme medyandır; tek seyircinin KRİTİK'i kanıtla doğrulanır (`tek_kritik_red_kanit`), komşu konumlar birleşir (`kritik_birlestirme_komsu`).
- Seyirci habersizdir: yalnız EKRAN metnini (aşamalı P0 → P3) görür; adlar duyulmadıkça maskelenir; amaç ve duygu alanı hiç gitmez.

## §5 Evren (seri kütüphanesi `<evren>/`; yalnız `evren.py` yazar)
`evren.py --on-kayit` A06 kilidinde yeni karakter/mekân/nesne taslağını açar; `ne_yok_kelimeleri` evrende olmayan öğeleri listeler;
`ozet` sonraki filmin brifingine girer. Kanon ihlali (`kanon_ihlali_max`) senaryo denetiminde HATA'dır.

## §6 Sık bulgular ve çözüm sahibi
| Bulgu | Sahibi |
|---|---|
| "Kim kimdir anlaşılmadı" (ad ekranda yok) | hikaye-yazari·revizyon (ad ilk görünüşü `ad_ilk_gorunus_max_sahne`) |
| "Neden umursamalıyım" (risk sözlü değil) | hikaye-yazari (risk `risk_sozlu_max_sn` içinde) |
| İlk 2 dakikada kapatma | ilk 2 dk A/B sürümü, sonra üçüncü sürüm |
| Aynı bilgi tekrarı | `bilgi_tekrar_max`; gereksiz açıklama satırı silinir |
| Yapısal tıkanma (plato) | yapimci·doktor |
