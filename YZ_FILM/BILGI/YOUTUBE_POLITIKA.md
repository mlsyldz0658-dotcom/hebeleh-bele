# YouTube politika özeti (yayın paketi için)

- **Yazıldı:** 24.10.2026, bulut geliştirme oturumu (TASARIM D-40, §6.9).
- **Durum: ŞABLON — resmî sayfalardan DOĞRULANMADI.** Bu oturumda internet erişimi yoktu; aşağıdakiler bellekten yazıldı.
  Her maddenin yanındaki resmî sayfa bir sonraki geliştirme oturumunda açılıp okunur, metin ve tarih güncellenir.
- **Tazeleme:** 90 günden eskiyse `yayin_paketi.py --dogrula` BAYRAK verir (bilgi). Kopyası veri kökünde `<veri>/BILGI/YOUTUBE_POLITIKA.md`.
- Politika yorumu gerekirse karar insanındır (TASARIM R18). Yükleme otomatik değildir (P2; her film için `YUKLE.bat` onayı).

## 1. Değiştirilmiş ya da sentetik içerik beyanı (`yz_beyani`)
- Kaynak: https://support.google.com/youtube/answer/14328491 (Disclosing use of altered or synthetic content) — doğrulanacak.
- Gerçekçi görünen, yapay zekâyla üretilmiş ya da değiştirilmiş içerik yüklenirken YouTube Studio'daki "Altered or synthetic content"
  sorusu **Evet** işaretlenir. Bizim filmlerimizde görüntü, video ve ses yapay zekâyla üretildiği için cevap her zaman **Evet**tir.
- Açıkça gerçek dışı (animasyon, fantastik yaratık) içerikte zorunluluk tartışmalı olabilir; biz fotogerçekçi insan karakterler
  kullandığımız için her filmde beyan ederiz (`PAKET.json → yz_beyani.sentetik_icerik: true`, açıklamada bir satır).
- Beyan edilmeyen gerçekçi sentetik içerikte YouTube etiketi kendisi ekleyebilir; tekrarlanan ihlal yaptırım getirebilir (doğrulanacak).

## 2. Özgün olmayan / seri üretim içerik (para kazanma)
- Kaynak: https://support.google.com/youtube/answer/1311392 (YouTube channel monetization policies; "inauthentic content",
  eski adıyla "repetitious content"; "reused content") — doğrulanacak.
- Kalıpla seri üretilmiş, birbirinin aynısı, emek ve özgün katkı göstermeyen videolar para kazanmadan çıkarılabilir.
- Bizim karşılığımız: her film kendi hikâyesi, karakterleri ve kurgusuyla özgündür; seri evreni tekrar değil devamlılıktır. Kontrol
  listesi maddesi: `ozgun_olmayan_icerik` — aynı şablondan arka arkaya benzer film yayımlanmaz, açıklama film başına yazılır.

## 3. Yanıltıcı meta veri ve kapak (spam ve aldatıcı uygulamalar)
- Kaynak: https://support.google.com/youtube/answer/2801973 (Spam, deceptive practices & scams policies) — doğrulanacak.
- Başlık, kapak ve açıklama videoda olmayan bir şey vaat edemez. Bizim karşılığımız vaat sözleşmesidir: başlığın her öğesi ve kapak
  imgesi filmde vardır (`yayin_paketi --dogrula` vaat sahnesi filmde yoksa HATA). Kontrol listesi: `yaniltici_meta_veri`, `kapak_yaniltmaz`.
- Etiket doldurma (alakasız çok sayıda etiket) spam sayılabilir; etiketler kısa ve ilgili tutulur.

## 4. Alan sınırları (yayin_paketi'nin denetlediği sayılar)
- Başlık ≤ 100 karakter; açıklama ≤ 5000 karakter; etiketlerin toplamı ≤ 500 karakter; başlık ve açıklamada `<` ve `>` kullanılamaz
  (YouTube Data API alan kuralları; https://developers.google.com/youtube/v3/docs/videos — doğrulanacak).

## 5. Bölümler (chapters)
- Kaynak: https://support.google.com/youtube/answer/9884579 (Video chapters) — doğrulanacak.
- Açıklamadaki zaman damgası listesinin ilki `00:00` olmalı; en az 3 zaman damgası; her bölüm en az 10 sn; artan sırada.
  Kanal düzeyinde ek koşullar olabilir (topluluk kuralları uyarısı olmaması vb.).
- Bizim kuralımız ayrıca en çok 8 bölüm ister (RE `bolum_sayisi_max`, zanaat kuralı; YouTube sınırı değil).

## 6. Shorts
- Kaynak: https://support.google.com/youtube/answer/10059070 (YouTube Shorts) — doğrulanacak.
- Dikey ya da kare video; süre sınırı (2024'ten beri en çok 3 dk olduğu biliniyor; doğrulanacak). Bizim kuralımız 30–60 sn, 9:16,
  ilk 2 sn kanca, filme bağlantı metni (TASARIM §6.7). Short'tan uzun videoya "ilgili video" bağlantısı verilebilir (doğrulanacak).

## 7. Müzik ve telif
- Kaynak: https://support.google.com/youtube/answer/2797370 (Content ID) — doğrulanacak.
- Müziğin kaynak kaydı (`MUZIK/KAYNAK_KAYDI.json`: model, sürüm, lisans, istem, tohum, SHA-1) Content ID itirazının kanıtıdır (D-25).
  Kontrol listesi: `muzik_lisansi`.

## 8. Çocuklara yönelik içerik
- Kaynak: https://support.google.com/youtube/answer/9528076 (Made for kids) — doğrulanacak.
- Filmlerimiz çocuklara yönelik değildir (şiddet, karanlık tema); yüklemede "Hayır, çocuklara özel değil" işaretlenir. Kontrol listesi:
  `cocuk_icerigi_degil`.

## Kontrol listesi (PAKET.json → politika_kontrol; maddeler yayin_paketi.POLITIKA_MADDELERI ile aynı)
| Madde | Ne denetlenir |
|---|---|
| `sentetik_icerik_beyani` | Studio'da "Altered or synthetic content: Yes"; açıklamada YZ satırı |
| `ozgun_olmayan_icerik` | film özgün; açıklama ve kapak film başına |
| `yaniltici_meta_veri` | başlık ve açıklama filmde olanı anlatır |
| `kapak_yaniltmaz` | kapak filmde olan bir anı gösterir (D-26) |
| `muzik_lisansi` | her müzik parçasının kaynak kaydı var |
| `cocuk_icerigi_degil` | "çocuklara özel değil" işaretlenir |
