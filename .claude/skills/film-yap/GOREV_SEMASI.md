# GÖREV ŞEMASI — `film.py sonraki` çıktısı ve `GOREV.json` v2 (bilgi; kuralları SKILL.md taşır)

İçindekiler: §sonraki · §GOREV.json · §Durumlar · §Görev türleri · §Aşamalı okuma · §Çıkış kodları · §Kimlikler · §Şemalar

## §sonraki — tek JSON (≤ 1.200 karakter)
```json
{"film": "F20261024_ejderha", "asama": "A06 Kâğıt seyirci, ilk 2 dk, kilit", "tur_no": 2, "cikis_kodu": 3, "tur": "ajan",
 "gorevler": [{"id": "A06-HS-004", "tur": "ajan", "ajan": "habersiz-seyirci", "kip": "kagit", "paralel_grup": "A06-s1-t2-g1",
               "istem": "Görevin: <film>/_GOREV/A06-HS-004/GOREV.json — önce onu oku, yalnız orada yazanı yap."}],
 "kullaniciya": null, "oku": null}
```
- `tur`: `ajan` · `betik` · `kullanici_eylemi` · `bekle` · `kisit` · `ortam` · `butce` · `kapi` · `hazirlaniyor` · `bitti`.
- `gorevler`: aynı paralel gruptaki görevler (ajanda en çok `ajan_paralel_max`). Ajan görevinde `istem` Agent'a AYNEN verilir.
- `kullaniciya`: kullanıcıya aynen söylenecek cümle (yoksa null). `oku`: takılınca okunacak dosya (rapor ya da KURTARMA bölümü).

## §GOREV.json — `<film>/_GOREV/<id>/GOREV.json` (film.py yazar; ajan okur, değiştirmez)
Klasör: `GOREV.json`, `ISTEM.md` (şablondan basılmış görev metni), `GIRDI/` (yalnız bu görev için kopyalanmış girdiler), `CIKTI/` (ajanın tek yazma yeri).
| Alan | Anlam |
|---|---|
| `id` | `A12-AS-014` biçimi: aşama · görev kodu · sıra |
| `asama`, `tur`, `ajan`, `kip`, `persona`, `rol` | ne, kim, hangi kipte; rol `yazar` / `denetci` / `kor` |
| `ornek` | `yeni` (taze ajan) ya da `ayni_yazar` (SendMessage ile aynı ajana devam) |
| `paralel_grup` | aynı gruptaki görevler TEK MESAJDA açılır |
| `durum` | §Durumlar |
| `deneme`, `deneme_max` | SubagentStop düzeltme sayacı (en çok 2 düzeltme) |
| `asamali` | `{bolumler, acik, mekanizma}`; §Aşamalı okuma |
| `girdi`, `girdi_imza` | GIRDI listesi ve imzası (değişirse görev bayat) |
| `cikti.zorunlu` | yazılması gereken `CIKTI/...` dosyaları; `cikti.sema` şema adı (`semalar/<ad>.json`) |
| `tasima` | doğrulanınca CIKTI dosyasının taşınacağı yer (betik taşır, zarf ekler) |
| `kapi`, `rapor` | betik görevinde kapı ve rapor yolu (`_RAPOR/<KAPI>_<kapsam>[_t<tur>].json`) |
| `kredili`, `gonderildi` | kredili işte gönderim kaydı önce yazılır; kesilince `--topla` |
| `mesaj`, `algilama` | kullanıcı eyleminde aynen iletilecek cümle ve eserin nasıl algılanacağı |
| `yarim_davranisi` | yazar `devam_et`, kör/denetçi `sifirdan` |
| `kullanim` | token, süre, model (SubagentStop kancası yazar) |
| `zaman` | `olusturma`, `basla`, `bitir` |

## §Durumlar
- Görev: `hazir` → `calisiyor` → `bitti`; ayrıca `gecersiz` (çıktı doğrulanamadı, düzeltme hakkı bitti), `kesildi`, `iptal`, `model_sapmasi`.
- Aşama: `bekliyor, calisiyor, ajan_bekliyor, kullanici_bekliyor, bekle, kapi_gecmedi, kismi, tamam, bayat`. `kismi` = kapı geçti, hedef değil
  (`hedef_alti`, §1.4); `bayat` = girdi imzası değişti, aşama yeniden açılır.

## §Görev türleri
| `tur` | Set amiri ne yapar |
|---|---|
| `ajan` | `film.py basla <id,…>` → aynı gruptakilere tek mesajda Agent (subagent_type=`ajan`, prompt=`istem` AYNEN) |
| `betik` | `film.py calis <id>` (aracı film.py çağırır: `python <ARACLAR>/<arac> <argümanlar> --film <film>`) |
| `kullanici` | `mesaj`'ı aynen ilet; `film.py bekle --kullanici <id>` ARKA PLANDA; turu bitir |

## §Aşamalı okuma
Seyirci görevleri bölüm bölüm okur (`P0` → `P1` → …). Ajan her bölümün `CIKTI/rapor_<bölüm>.md`'sini yazıp durur; SubagentStop kancası
(`kanca.py ajan_bitti`) sonraki bölümü `GIRDI/`'ye koyar ve ajana "devam" der. Set amiri bir şey yapmaz. İleri bölümü okumak erişim kancasınca reddedilir.

## §Çıkış kodları
`0` BİTTİ · `1` HATA · `2` KULLANICI · `3` AJAN · `4` ORTAM · `5` BÜTÇE · `6` KAPI · `7` KISIT · `8` BEKLE. Sabit cümleler: KULLANICI_DILI.md.

## §Kimlikler
Aşama `A[0-9]{2}[a-z]?` · görev `A12-AS-014` · sahne `S05` · ses kapısı `S2m` · kuyruk `YU-T2-1-007` · yazım maddesi `YY-A07c-031` ·
öğrenilen kural `OK-0003` · kurulum kademesi `KUR1` · kamera kurulumu `KAM3` · bütçe noktası `BUT0`. Kaynak: `YZ_FILM/ARACLAR/veri/ADLAR.json`.

## §Şemalar (`semalar/`)
`gorev_v2` (bu dosya) · `seyirci_rapor_v2` (§5.8) · `juri_v1` · `ozet_eslesme_v1` · `denetci_rapor_v1` · `kapi_rapor_v1` (§5.7) ·
`kuyruk_madde_v1` · `plan_v2` (§5.1; yönetmen kâğıdı). Ajanın CIKTI dosyaları zarfsızdır; betik taşırken `_surum` ve `_uretim` ekler.
