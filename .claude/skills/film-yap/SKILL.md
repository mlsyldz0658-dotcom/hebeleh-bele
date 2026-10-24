---
name: film-yap
description: >-
  Kullanıcı bir film konusu verdiğinde ya da süren bir filme devam edilmesi gerektiğinde YZ film setini yürütür:
  görev defterindeki sıradaki işi çalıştırır, uzman ajanlara dağıtır, kapılardan geçirir. Use when the user gives a
  movie topic or story idea, asks for a film ("film yap", "yeni film", "şu konuda bir film", "make a movie about"),
  says "sen seç", "devam", "devam et", "kaldığın yerden", "continue", reports that a requested physical step is done
  ("zipi koydum", "Flow'da gönderdim", "kredi yükledim", "dışa aktardım"), or when the session context shows an active
  film or a pending system measurement task.
when_to_use: >-
  Örnekler: "Ejderha büyüten bir kadın hakkında film yap" · "konu: uzaylı çocuğa babalık eden asker" · "sen seç" ·
  "devam" · "sınır açıldı, devam et" · "Gemini zipini GELENLER'e koydum". Kullanıcı SORU soruyorsa (ne durumda, neden
  durdu, kaç kredi) film-durum; not, şikâyet ya da kendi CapCut düzenlemesi için film-not kullanılır.
argument-hint: "[film konusu | sen seç | devam]"
effort: high
allowed-tools: Bash(python .claude/bin/film.py *)
hooks:
  PreToolUse:
    - matcher: "Read|Glob|Grep|Write|Edit|NotebookEdit"
      hooks:
        - {type: command, command: "bash \"$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh\" erisim --kaynak beceri", timeout: 10, onFailure: block}
    - matcher: "Bash|PowerShell"
      hooks:
        - {type: command, command: "bash \"$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh\" komut --kaynak beceri", timeout: 10, onFailure: block}
    - matcher: "Agent"
      hooks:
        - {type: command, command: "bash \"$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh\" ajan --kaynak beceri", timeout: 10, onFailure: block}
---
# FİLM YAP — set amiri döngüsü
## 0. Şu anki durum (beceri açılırken betik yazar)
!`python .claude/bin/film.py ozet --kisa || true`
## 1. Değişmez kurallar (kancalar da zorlar)
1. Kullanıcıya YALNIZ filmin konusu sorulur, yalnız şu cümleyle: "Filmin konusu ne olsun? Bir cümle yeter (ör. ejderha yavrusunu saklayan avcı kadın). İstersen 'sen seç' yaz."
   Diğer bütün kararları ekip verir: film.py karar ekle "karar — neden — yanlışsa
   maliyeti". "Hangisini istersin / onaylıyor musun / devam edeyim mi" YOK.
2. Kullanıcıdan yalnız onun yapabileceği FİZİKSEL iş istenir. Talimat cümlesini film.py verir; aynen ilet.
3. Flow "olağan dışı etkinlik" / doğrulama → hat her kipte durur. Yeniden başlatma, sayfa yenileme, atlatma, tempo hızlandırma,
   fare/klavye taklidi, BAŞKA HESAPLA DEVAM YOK. Kilidi yalnız kullanıcı kaldırır (UYARI_GECTI.bat).
4. AYARLAR hiçbir kökte okunmaz, yazdırılmaz, kopyalanmaz. Ayar gerekiyorsa: film.py goster ayar (maskeli).
5. Sen içerik üretmezsin, puan vermezsin, ajan çıktısını düzeltmezsin, plan/rapor dosyası yazmazsın.
6. Ajan çağırırken: yalnız görevdeki ajan tipi; istem AYNEN; name verme; fork başlatma; yerleşik ajan kullanma.
7. Büyük dosya açma. Bilgi gerekiyorsa: film.py goster <ne>.
8. Hafızana değil film.py'ye güven: film.py sonraki ne diyorsa o doğrudur.
9. Kullanıcı soru sorarsa film-durum; not verirse film-not. Soruya işlemle cevap verme.
10. Kredi yalnız film.py'nin bütçe noktası geçince harcanır. memmet.py'yi ya da bir sağlayıcıyı doğrudan çağırma.
11. Kalıcı silme yok; robocopy /MIR yok; git push yok.
12. Çıkış kodu 2, 4, 5, 6, 7 ya da 8 ise film.py'nin cümlesini söyle ve turu bitir. Soru ekleme.
## 2. Döngü
1. python .claude/bin/film.py sonraki → JSON.
2. python .claude/bin/film.py basla <id,id,…>. Reddederse (kanca nabzı yok): KURTARMA.md §Kanca; ajan çalıştırma.
3. tur=ajan → aynı paralel_grup'taki görevlerin HEPSİ İÇİN TEK MESAJDA Agent çağır (en çok 5): subagent_type=<ajan>,
   prompt=<istem> AYNEN. Sonucu bekle. ornek=ayni_yazar ise önce SendMessage(<ajan_id>); kimlik yoksa yeni örnek.
   Aşamalı görevlerde bölüm geçişini sistem yapar; sen bir şey yapmazsın.
4. tur=betik → python .claude/bin/film.py calis <id>. 8 BEKLE dönerse film.py bekle <iş>'i arka planda başlat ya da turu bitir.
5. tur=kullanici_eylemi → mesajı aynen ilet; python .claude/bin/film.py bekle --kullanici <id>'yi ARKA PLANDA başlat; turu bitir.
   (bekle beklenen eseri yoklar: GELENLER'de ZIP, KUNYE'de blok sonu, CapCut kapandı, Flow bakiyesi, D takıldı; 6 saatte bir hatırlatır;
   eser gelince çıkar ve bitişi oturumu uyandırır. "Hâlâ bekleniyor" diye çıkarsa yeniden başlat.)
6. tur=bekle/kisit/ortam/butce → nedeni film.py'nin cümlesiyle söyle, turu bitir.
7. tur=bitti → film.py ozet --kullanici çıktısını ilet.
8. Ajan sonucu ya da tamamlanma bildirimi gelince doğrulama yapma (kanca yaptı) → 1'e dön.
## 3. Kullanıcıyla konuşma
Türkçe, kısa, teknik terim yok. Her ilerlemede en çok 3 satır: ne bitti · şimdi ne oluyor · senden bir şey gerekiyor mu (yalnız fiziksel iş).
Aktif film yoksa ve kullanıcı konu vermediyse (yalnız "film yap" ya da benzeri) yalnız 1. kuraldaki tek soru sorulur, başka cümle eklenmez.
Konu verdiyse soru sorulmaz: python .claude/bin/film.py yeni --konu "<kullanıcının cümlesi>"; konuyla gelen istekler kesin istektir,
belirsizlikte soru değil varsayım (karar defterine). "sen seç" → konuyu ekip seçer: python .claude/bin/film.py yeni --konu "sen seç".
Bulutta (oturum bağlamında ortam=bulut) aktif film yoksa konu sorulmaz, film başlatılmaz; kullanıcı konu verse de yalnız şu cümle söylenir:
"Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz."
Bulutta yalnız deneme istenirse: python .claude/bin/film.py yeni --konu "<cümle>" --saglayici sahte (ORNEK_* denemesi).
## 4. Takılırsan
- film.py "takildi" derse KURTARMA.md'yi oku ve yazanı uygula.
- Bir kanca işlemi engellediyse gerekçeyi oku, kuralı çiğneme; film.py sonraki.
- Kullanım sınırı ya da kesilme: hiçbir şey yapma; yeniden açılınca döngü kaldığı yerden sürer.
--- (çekirdek sonu) ---
## 5. Referanslar (yalnız film.py `oku` alanında gösterirse ya da takılınca)
KURTARMA.md · GOREV_SEMASI.md · KULLANICI_DILI.md · reference/hat.md
