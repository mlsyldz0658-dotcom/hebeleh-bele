# KURTARMA — film.py "takildi" dediğinde ya da bir şey ters gittiğinde

İçindekiler: §Kanca · §Kilit · §DUR · §Kesik görev · §Kesik indirme · §GPU · §Kullanım sınırı · §Flow kilidi · §Disk · §Bütçe ·
§Token · §Kapı · §Araç yok · §Ortam · §Veri klasörü

Her durumda: kullanıcıya soru sorulmaz; söylenecek cümle film.py'nin `kullaniciya` alanıdır (yoksa KULLANICI_DILI.md'deki sabit cümle).
Kalıcı silme yok, AYARLAR okunmaz, memmet.py ya da sağlayıcı doğrudan çağrılmaz. Bu dosyadaki bütün komutlar `python .claude/bin/film.py …`dir.

## §Kanca — `basla` "kanca nabzı yok ya da eski" dedi
Belirti: `film.py basla` 1 ile döner, ajan görevi `hazir` kalır. Neden: komut kancası `_GOREV/KANCA_NABZI.json`'u yazmadı (kancalar yüklenmedi,
Python bulunamadı, `CLAUDE_CODE_FORK_SUBAGENT=0` değil ya da Claude depo klasörü dışında açıldı).
1. Ajan ÇALIŞTIRMA (kancasız ajan habersizliği ve erişim kurallarını bozar). Agent aracını görevsiz açma.
2. Kullanıcıya: "Film seti kancaları bu oturumda çalışmıyor. Claude'u kapatıp Masaüstündeki FILM_SETI.bat ile yeniden aç; kaldığı yerden sürer."
3. Turu bitir. Yeniden açılınca döngü `film.py sonraki` ile sürer; kurulum eksikse kullanıcı KURULUM.bat'a bir kez çift tıklar.
4. Geliştirme oturumundaysan (film-gelistir): `bash .claude/bin/kanca.sh komut < girdi.json` ile kancayı elle sına; `.claude/bin/python_yolu.txt`
   ve `.claude/settings.json` env satırına bak. Nabız sahte yazılmaz.

## §Kilit — "FILM.kilit bayat" ya da "başka bir film.py çalışıyor"
1. `film.py kurtar` (bayat kilidi kendisi tanır: sahibi süreç yoksa ya da süre aşıldıysa kaldırır, kaydını tutar).
2. Hâlâ kilitliyse başka bir `film.py` gerçekten çalışıyordur (arka plan `bekle` dahil): turu bitir; bitince kendiliğinden sürer.
3. Kilit dosyasını elle silme, taşıma.

## §DUR — film durduruldu (DURDUR.bat)
Kullanıcı `DURDUR.bat`'a bastı ya da "dur" yazdı: yeni iş başlatma. Kullanıcıya: "Film durduruldu. Devam için DEVAM.bat ya da sohbete 'devam' yaz."
Kullanıcı "devam" yazınca `film.py sonraki` (sürüşü film.py açar). `DUR` dosyasını sen kaldırma.

## §Kesik görev — oturum kesildi, görev `calisiyor` kaldı
1. `film.py kurtar` → yarım görevleri sınıflar: yazar görevinde `devam_et` (aynı CIKTI'dan sürer), kör ve denetçi görevinde `sifirdan`
   (yeni örnek, CIKTI temizlenmiş kopyayla). Biten görevler YENİDEN YAPILMAZ.
2. `film.py sonraki` → yalnız kesikler ve kalanlar gelir. Ajanı film.py'nin verdiği istemle AYNEN aç.
3. Kredili betik görevi kesildiyse kör yeniden gönderim yoktur: film.py `topla: true` verir → `film.py calis <id> --topla`.

## §Kesik indirme — Flow/Gemini indirmesi yarım
`film.py calis <id> --topla` (gönderim kaydı önce yazıldığı için ikinci gönderim olmaz). Toplama da başarısızsa film.py kullanıcı eylemi
verir ("Flow'da şu kliplerin indir düğmesine bas"); aynen ilet, `film.py bekle --kullanici <id>` arka planda.

## §GPU — "GPU meşgul" / yerel model kilidi
Kod 8 BEKLE. Kullanıcıdan iş isteme (oyun ya da başka bir program açıksa film.py söyler). `film.py bekle` arka planda ya da turu bitir.

## §Kullanım sınırı — Claude kullanım sınırı, kesilme, bağlam sıkıştırma
Hiçbir şey yapma; yeni ajan açma. Yeniden açılınca ya da sınır kalkınca döngü kaldığı yerden sürer (durum dosyalardadır, hafızada değil).
Sıkıştırmadan sonra yalnız SKILL.md çekirdeğine ve `film.py sonraki`'ye güven.

## §Flow kilidi — Flow "olağan dışı etkinlik" ya da doğrulama (kod 7 KISIT)
1. Hat HER KİPTE durur. Yeniden başlatma, sayfa yenileme, bekleyip tekrar deneme, tempo hızlandırma, fare/klavye taklidi YOK.
2. BAŞKA HESAPLA DEVAM YOK; başka servise (Vertex dahil) izin olmadan geçilmez; kie.ai hiç kullanılmaz.
3. Kullanıcıya film.py'nin cümlesi: "Flow uyarı verdi; hesap kilitli. GÖNDER'e basma, sayfayı yenileme. Kilidi yalnız sen kaldırırsın (UYARI_GECTI.bat)."
4. Kâğıt ve görsel olmayan işler sürebilir; film.py ne verirse o. `HESAP/FLOW_KILIDI.json`'a dokunma.
5. Kullanıcı "başka hesapla dene" derse: "Başka hesapla devam edilmez; kilit kalkınca aynı hesapla sürer." (kural 3).

## §Disk — "Diskte yer az" (kod 8)
film.py'nin cümlesini ilet (D diskini tak; eski filmler arşivlenir). Dosya silme, taşıma önerme; arşivi `arsivle` betiği yapar.

## §Bütçe — kod 5 BÜTÇE
"Tahmini kredi bütçeyi aşıyor; yazılmış film kısaltılmaz. Kredi yükleyince kendim devam ederim." Kullanıcıya seçenek sunma.

## §Token — "Bu film için ayrılan Claude kullanımı doldu" (kod 8)
`TOKEN_PROJEKSIYON.md` yazıldı; hat-denetcisi döngü taraması görev olarak gelir. film.py ne verirse o; soru yok.

## §Kapı — kod 6 KAPI
Merdiven tükendi (kâğıt ürün ya da film düzeyi HATA). film.py'nin cümlesini ilet ve turu bitir. Kod/şema HATA'sıysa iş `film-gelistir`'e kalır;
kullanıcıya bilgi: "Sistemde bir hata bulundu; geliştirme oturumunda düzeltilecek. Senin yapacağın bir şey yok."

## §Araç yok — `calis` 4 ORTAM ("araç henüz yok")
TASARIM §9'daki sonraki adımın aracı depoda yok demektir. Kullanıcıya bilgi: "Bu aşamanın aracı henüz hazır değil; geliştirme sürüyor."
Aracı sen yazma (film sürüşünde kod değişmez).

## §Ortam — "yalnız kullanıcının bilgisayarında yürür" (kod 4)
Bulut oturumundasın (D-45). Yalnız şu cümle: "Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz."
Deneme istenirse yalnız `--saglayici sahte` ile ORNEK_* filmi.

## §Veri klasörü — Claude veri klasöründe açıldı
Kullanıcıya yalnız: "Masaüstündeki FILM_SETI.bat'a çift tıkla; Claude doğru klasörde açılır." Başka bir şey yapma.
