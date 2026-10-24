# reference/ses.md — ses kadrosu, ses tasarımı, müzik, ses kapıları (A06s, A08, A10b–c, A15; bilgi, kural taşımaz)

İçindekiler: §1 Karar (KK4) · §2 Akış · §3 Ses profili · §4 Ses tasarımı · §5 Müzik · §6 Kapılar S0–S8 · §7 Merdiven

## §1 Karar: "Veo konuşur, sesi biz sabitleriz" (§2.2)
Diyaloğu Veo klipte söyler (dudak doğal); karakter sesi sonra yerel ses dönüşümüyle (OpenVoice / Chatterbox; RVC koşullu) kadrodaki sese
sabitlenir. Yedek yol: TTS + MuseTalk dudak eşleme. Wav2Lip kullanılmaz. Seçim Ö0-c ölçümüne bağlıdır.

## §2 Akış
| Aşama | Ne | Kim |
|---|---|---|
| A06s | `_SES/SES_PROFILLERI.json`, `SES_KADROSU.md` | `ses-tasarimcisi·kadro`; `ses_plani.py --profil-denetle` (S0) |
| A08 | `_SES/SES_<grup>.json` (sahne grubu başına), `SES_TASARIMI.md`, `MUZIK/muzik_listesi.json` | `ses_plani --taslak`; `ses-tasarimcisi·tasarim` × grup, `·muzik`; `muzik.py --kagit`; S0 |
| A10b | telaffuz testi (uydurma adlar) | `ses_sec.py --telaffuz` (S1a) |
| A10c | ses seçimi, motor kıyası | `ses_sec.py`; yakın puanda `ses-tasarimcisi·kadro` (S1) |
| A15 | diyalog dönüşümü, karar merdiveni | `seslendir`, `ses_donustur`, `ses_karar`; gri bantta `hikaye-yazari·replik_kabul` (S2) |

## §3 Ses profili
Her konuşan karakter için `ses_profil_alanlari` (cinsiyet, yaş bandı, aksan, perde, tını …) ve Veo için tek satır `veo_ses_tarifi`
(≤ `veo_ses_tarifi_kelime_max` kelime; sıra: tını + cinsiyet + aksan; yaş ve filtre sözcükleri yok). Aynı yaş bandındaki iki karakter
belirgin ayrışır (`ses_profil_ayni_bant_ayrisma`). Tarif istemde birebir kullanılır (ISTEM kapısı).

## §4 Ses tasarımı (sahne grubu)
- Yatak (ambiyans): sahne grubu başına ≤ `yatak_sahne_grubu_max`; seviye diyalogun altında (`ambiyans_diyalog_alti_db`).
- Efekt: fiil → kategori (`veri/efekt_sozlugu.json`); an (adımın başı/ortası/sonu ± `efekt_an_pay_sn`); söze uzaklık ≥ `efekt_soz_uzaklik_min_ms`.
- `flow_sound`: klip istemine giden kısa ses cümlesi ("Sound: … No music."), ≤ `flow_sound_kelime_max` kelime, müzik sözcüğü yok.
- Sessizlik: vurgu sessizliği (`vurgu_sessizlik_sn`), mutlak sessizlik sınırı (`mutlak_sessizlik_*`).

## §5 Müzik (D-25)
Kaynak merdiveni: `acestep` (yerel) → `kutuphane` → `elevenlabs_muzik` (izinle) → `gemini_muzik_paketi` → `midi_ornek`. Zincir boşsa film
müziksiz biter ve BAYRAK yazılır. Leitmotif ajanın yazdığı özgün notalardır (`leitmotif_nota_min`; MIDI). İstem `muzik_istem_zorunlu_ifade`
taşır, `muzik_istem_yasak_ifadeler` taşımaz. Kaplama oranı `muzik_kaplama_oran`; soğuk açılış ve en karanlık an müziksizdir.

## §6 Kapılar
| Kapı | Ne zaman | Ne ölçer |
|---|---|---|
| S0 | A06s, A08 | profil kuralları, ses planı şeması, efekt anları, flow_sound kalıbı, müzik planı |
| S1a / S1 / S1b | A10b–c | ad telaffuzu (ad hatası 0), aday sesler, motor kıyası |
| S2 / S2m | A14–A15 | dönüşüm benzerliği (`ses_donusum_benzerlik_min`), zarf gecikmesi, WER artışı, dudak/konuşan uyumu |
| S3–S7 | A16 | hizalama, seviye (`diyalog_lufs`), katmanlar, müzik, final ses (`final_lufs`, `true_peak_max_dbtp`) |
| S8 | A17 | yayın dosyasının sesi |

## §7 Merdiven (A15)
Veo konuşmadı ya da yanlış kişi konuştu → Flow'da yeniden çekim (CORRECTION, ≤ 2) → TTS + dudak → kurgucu repliği ekran dışına taşır
(L taşma) → yönetmen onarımı → açık rapor. Gri bantta (`replik_wer_gri_bant`) replik kabulünü `hikaye-yazari·replik_kabul` verir.
