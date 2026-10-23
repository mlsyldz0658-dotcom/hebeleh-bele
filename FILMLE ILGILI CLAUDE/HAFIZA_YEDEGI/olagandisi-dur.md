---
name: olagandisi-dur
description: "Kullanıcı kuralı — Flow \"olağan dışı etkinlik\" uyarısı verirse Memmet KESİN durur (mola/devam yok); bot tespitini atlatma yok"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2139e0c3-5b43-4636-b0b5-3ac5f98b918e
  modified: 2026-10-18T21:58:16.638Z
---

Flow bir üretimde "Olağan dışı etkinlikler tespit ettik" derse Memmet hemen durur (memmet.py'de Durdur). Otomatik yeniden başlatma yok; kullanıcıya haber verilir. Hazır videolar `memmet_topla.py` ile (yeni gönderim olmadan) toplanabilir.

**Why:** 16.10.2026'da kullanıcının yeni Ultra hesabında (ysfootball75) gündüz modunda bu uyarı 15-20 dk'da bir geldi; kullanıcı 10.000 kredili hesabı riske atmak istemiyor ("olağan dışı rapor verirse kesin durdur"). Ayrıca "insan gibi fare/klavye ile devam" isteği reddedildi: bot tespitini atlatmak yapılmaz.
17.10 karşılaştırma: aynı kodlu avatar kanalı Memmet'i (başka hesap) uyarısız basıyor; fark TEMPO. Kalıcı ayar (MEMMET_AYAR.json): gece 12-30 sn / aynı anda 2 / 2 partide bir 15-30 dk mola; gündüz 6-15 sn / aynı anda 2; parti içinde her 8 gönderimde 3-6 dk ara mola (ara_mola_her, ara_mola_dk). Yeni Ultra hesabı (ysfootball75) düşük güvenli — hızlı tempo uyarı getiriyor.
17.10 akşam: kullanıcı "olağandışı geçti devam" / "bırak molayı" / "zorla bugün bitirek" dedi → Memmet uyarıda yine durur ama döngü 5 dk sonra yeniden başlatır (o gün için kullanıcı kararı; kalıcı değil, yeni günde tekrar sor/varsayılan 30 dk). Döngü yalnız gerçek uyarıda bekler, başka durmada 20 sn sonra devam (scratchpad memmet_dongu.ps1).
18.10 gece: YARI OTOMATİK MOD (kullanıcı fikri, "max" sekmesinde CLAUDE KANALI\memmet3'te yapıldı) YZ_FILM'e alındı: ARACLAR\memmet.py = memmet3 sürümü (eski: _memmet_yedek_1810_eski.py), MEMMET_AYAR modlar.elle. `memmet.py <film> --mod elle`: Memmet referans + istemi hazırlar, GÖNDER'e kullanıcı basar; olağan dışıda durmaz, kullanıcı sayfayı yeniler. Kullanıcı başındayken varsayılan bu.
19.10 00:05: aynı akşam ~40 görsel gönderiminden sonra B3 P1 videoları yarı otomatikte bile 3 gönderimde olağan dışı verdi (önce Lite↔Omni geçişiyle, sonra yalnız Omni ile de) → kullanıcı "durdur" dedi. Ders: yoğun görsel turundan hemen sonra video başlatma; hesabı dinlendir (gece/ertesi gün). B3 videoları tümü Omni (model değişimi yok).
19.10 00:50–00:57: yeni projede, gece temposu + tek tek yüklemeyle bile HER video gönderimi ~30 sn içinde "olağan dışı" aldı (görseller aynı akşam geçiyordu) → hesapta video tarafı geçici işaretli. Kullanıcı "durdur, yarın bakarız" dedi. Not: memmet3 sürümü gece modunda olağan dışında 5 kez sayfa yenileyip deniyor (eski kural "ilk uyarıda kesin dur"du) — sabah kullanıcıya sor/geri al. Yarın önce kullanıcı Flow'da ELLE 1 video denesin: o da işaretliyse sorun hesap düzeyinde (bekle / ikinci hesap / kie.ai API).
**How to apply:** Uyarıdan sonra kalan az sahneyi kullanıcı elle çeker (`ELLE_CEK` listesi) ya da API yolu (kie.ai) önerilir. Bkz. [[PROJE-b2]], [[ucuz-erisim-arastirmasi]].
