# memmet3 — yalnız başvuru malzemesi (ÇALIŞTIRILMAZ)

Bu klasördeki `memmet.py`, ilk yerel oturumun (24.10.2026) hazırladığı memmet3 aktarımıdır (`yerel/memmet3-20261024-1346`, ef2b74c).
Depodaki PR-0 yamalı `memmet.py`'nin (34a9097) üstüne kullanıcının 19.10 memmet3'ünden birkaç arayüz eki taşınmıştı.

- **Koşan tek Memmet `YZ_FILM/ARACLAR/memmet.py`'dir** (v2, tek korumalı kapı `dokun`). Bu dosya hiçbir `.bat`, `film.py`,
  sağlayıcı ya da sarmalayıcı tarafından çağrılmaz; çağrılmamalıdır.
- Dosyanın ilk satırı `raise SystemExit(...)`: çalıştırılırsa ya da içe aktarılırsa hemen çıkar. Kanca (`.claude/hooks/kanca.py`
  `arsiv_memmet`) `_ESKI/` ya da `GELISTIRME/` altındaki bir Memmet'i çalıştıran her komutu (`--giris`/`--bakiye` dahil) reddeder;
  `veri_emniyet.py` `_ESKI/`'yi giriş noktası saymaz ama onu çağıran `.bat/.ps1`'leri emekliye ayırır.
- Gerçek arayüz bilgisinden işe yarayanlar (video modeli seçicisi, 9:16 oranı, x2 görsel adayları, elle kipte referansın sahnesi
  gelince yüklenmesi, `MEMMET_OLCEK`) `ARACLAR/memmet.py`'ye yalnız `dokun`/`oku` üzerinden, testleriyle aktarıldı
  (`testler/test_memmet_korkuluk.py` `Memmet3Aktarim`). Alınmayanlar ve nedenleri `ARACLAR/CLAUDE.md` §Şu anki durum'da.
- Silinmez (kalıcı silme yok); yalnız okunur.
