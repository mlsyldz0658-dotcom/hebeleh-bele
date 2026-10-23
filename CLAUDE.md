# YZ FİLM SETİ
Bu klasör bir YZ film setidir. Kullanıcı Türkçe konuşur, teknik bilgisi azdır. Tasarım: `.claude/skills/film-yap/tartisma/TASARIM.md`.

## Açılışta
Oturum başında "FİLM SETİ DURUMU" bağlamı gelir (kanca). Gelmediyse: `python .claude/bin/film.py ozet`.
- **Bulutta** (`ortam=bulut`; kanca yoksa: oturum Windows dışında açıldıysa) ve aktif film yoksa konu SORULMAZ, film başlatılmaz.
  Kullanıcı konu verse de yalnız şunu söyle: "Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla
  ve konuyu orada yaz." Bulutta `film-yap` yalnız `--saglayici sahte` ile `ORNEK_*` denemesi koşar; geliştirme `/film-gelistir` ile sürer.
- Bu bilgisayarda `O0a.json` yoksa ve kullanıcı "ilk kurulum" yazarsa: `YZ_FILM/ARACLAR/CLAUDE.md` §İlk yerel oturum uygulanır.
- Aktif film YOK ve kullanıcı konu vermediyse YALNIZ şunu sor: "Filmin konusu ne olsun? Bir cümle yeter
  (ör. ejderha yavrusunu saklayan avcı kadın). İstersen 'sen seç' yaz."
- Kullanıcı konu verdiyse ya da aktif film VARSA: soru sormadan film-yap becerisiyle devam et.

## Her zaman
- Kullanıcıya yalnız konu sorulur; diğer kararları ekip verir.
- Kullanıcı soru sorarsa yalnız cevap ver (film-durum). Not verirse film-not.
- Flow "olağan dışı etkinlik", reCAPTCHA ya da doğrulama → **her kipte dur**, haber ver. Atlatma, fare/klavye taklidi,
  sayfa yenileme, otomatik yeniden başlatma yok. Başka Google/Flow hesabına geçilmez; kie.ai kullanılmaz.
- AYARLAR gizli: okuma, yazdırma, kopyalama, loglama, commit yok; anahtar dosyaları depoda boş kalır.
- Kalıcı silme yok (eskiler `_ESKI/`'ye taşınır). robocopy /MIR yok.
- Kullanıcının yolları bozulmaz (veri `C:\Users\Soysal\Desktop\YZ_FILM`); yollar `YOLLAR.json`'dan okunur.
- Durum hafızada değil: `film.py` ve dosyalar doğrudur.

## Sistemi değiştirmek
Yalnız kullanıcı /film-gelistir derse ya da bu bir geliştirme oturumuysa. Ayrıntı: `YZ_FILM/ARACLAR/CLAUDE.md`.
Uygulama sürüyor (TASARIM §9): `film-yap`, `film-gelistir`, `.claude/bin/film.py ozet` ve kancalar henüz yoksa geliştirme oturumu
yalnız `YZ_FILM/ARACLAR/CLAUDE.md`'yi izler.
