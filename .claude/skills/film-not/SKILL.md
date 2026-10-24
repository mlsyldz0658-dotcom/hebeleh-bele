---
name: film-not
description: >-
  Kullanıcı animatik, dikey kesit, CapCut taslağı ya da bitmiş film hakkında not, şikâyet veya kendi yaptığı düzenlemeyi
  bildirdiğinde notları salt okunur okur, karar ve ders defterine işler, düzeltme görevlerine çevirir. Use when the
  user says "notlar hazır", "CapCut'ta değiştirdim kontrol et", "şu sahne kopuk", "ses kaymış", "beğenmedim", "şunu kes",
  "bu ses olmamış", or describes a problem in a draft or in an information package.
when_to_use: >-
  Kullanıcının kurgu kararı aynen uygulanır; kullanıcının taslağına yazılmaz, klonlanıp yamanır. Kendiliğinden gelen
  itiraz kesin istektir ve ilgili aşamayı yeniden açar. Notlar işlendikten sonra film-yap döngüsüne dönülür.
allowed-tools: Bash(python .claude/bin/film.py notlar*), Bash(python .claude/bin/film.py karar ekle*), Bash(python .claude/bin/film.py ders ekle*), Bash(python .claude/bin/film.py goster pencere*), Bash(python .claude/bin/film.py bekle*)
---
# FİLM NOT — kullanıcı notu, şikâyet, CapCut düzenlemesi → görev
## 1. Kurallar
1. Kullanıcının kurgu kararı aynen ve kilitli uygulanır. Kullanıcının CapCut taslağına yazılmaz; sistem onu klonlar ve klonu yamar.
2. Not ya da şikâyet kesin istektir; ilgili aşamayı yeniden açar. Kullanıcıya soru sorulmaz ("şunu mu demek istedin" YOK):
   belirsizlikte en makul yorum karar defterine yazılır ("Kullanıcı notu N: … — yorum: … — yanlışsa maliyeti: …").
3. Notları yalnız film.py okur (salt okunur). Sen not dosyası, plan, rapor ya da kurgu dosyası yazmazsın; içerik üretmezsin.
4. AYARLAR okunmaz; kalıcı silme, robocopy /MIR, git push yok. Flow kilidi varken video işi açılmaz (film.py söyler).
## 2. Adımlar
1. python .claude/bin/film.py notlar oku → notlari_oku.py + taslak_fark.py çıktısı (salt okunur).
   Çıktı "CapCut açık" derse kullanıcıya film.py'nin cümlesini aynen ilet ("CapCut'ı kapat"); sonra
   python .claude/bin/film.py bekle --kullanici <id>'yi ARKA PLANDA başlat ve turu bitir (kapanınca oturum kendiliğinden sürer).
2. Her notu sınıfla (sınıflama senin işin değil, film.py çıktısındaki "sinif" alanı esastır; boşsa şu sırayla):
   a. Kullanıcının kendi kurgu kararı (CapCut'ta kesti, taşıdı, sildi) → aynen ve kilitli KURGU_PLANI'na (film.py notlar isle yapar).
   b. Şikâyet ("kopuk", "ses kaymış", "robot gibi") → hangi kapı yakalamalıydı:
      python .claude/bin/film.py ders ekle --kapi <KAPI> --belirti "<kullanıcının cümlesi>" --kaynak kullanici_notu [--plan <no>]
      Kapı adı tahmini: görüntü kopukluğu K1/V3, ses kayması S3, ses doğallığı S2, ritim/sıkılma HS_KURGU, hikâye anlaşılmazlığı HS_KAGIT.
   c. Yeni sahne ya da ses isteği → kesin istek: içerik hikaye-yazari, plan yonetmen, ses ses-tasarimcisi (görevleri film.py açar).
3. Her not için karar: python .claude/bin/film.py karar ekle "Kullanıcı notu N: <özet> — uygulanacak — <yanlışsa maliyeti>"
4. python .claude/bin/film.py notlar isle → kurgucu·not görevi (A16n) açılır; film.py'nin döndürdüğü görevi film-yap döngüsüyle yürüt.
5. Kullanıcıya yalnız bilgi ver (soru yok):
   "Notlarını aldım: N düzeltme. Bitince CapCut'ta listenin en üstünde yeni adla göreceksin; senin taslağına dokunmadım."
6. Kesme sonrası Z1 kurulum ve Y58 denetimleri yeniden çalışır (film.py yapar); sen ayrıca bir şey yapmazsın.
## 3. Sık notlar ve karşılıkları (bilgi)
| Kullanıcı der | Sınıf | Ne olur |
|---|---|---|
| "CapCut'ta değiştirdim, kontrol et" | a | taslak_fark → kullanıcının kararları kilitlenir, klon taslak "<adı> · v<N+1>" |
| "şu sahne kopuk", "adam birden masada" | b | ders (K1/V3) + kurgucu·not çözümü (kesme, örtü, yeniden çekim kuyruğu) |
| "ses robot gibi", "bu ses olmamış" | b+c | ders (S2) + ses aşaması yeniden açılır (kesin istek) |
| "şunu kes", "bu kısım uzun" | a | kesme kilitli uygulanır; süre ve ritim denetimi yeniden koşar |
| "buraya bir sahne ekle" | c | kesin istek: hikaye-yazari·dar_degisiklik → yonetmen → üretim kuyruğu |
## 4. Referans
../film-yap/reference/kurgu.md §Not · ../film-yap/KULLANICI_DILI.md
