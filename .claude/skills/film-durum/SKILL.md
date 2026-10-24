---
name: film-durum
description: >-
  Film hakkında soru soran kullanıcıya yalnız cevap verir; dosya değiştirmez, ajan çalıştırmaz, üretim başlatmaz.
  Use when the user asks a question about the film or the system: "ne durumda", "hangi aşamadayız", "neden durdu",
  "kaç kredi lazım", "promptta ne yazıyor", "şu sahnede ne oluyor", "ne zaman biter", "what's the status", or any
  message that ends with a question mark and does not ask for a change.
when_to_use: >-
  Soru = yalnız cevap kuralı (kullanıcı kesin istedi). Cevaptan sonra en çok bir bilgi cümlesi: "Ekip sıradaki adımda şunu
  yapacak: …; itiraz edersen yaz." (öneri ya da onay sorusu değil; KK1). Kullanıcı "bak" derse (ör. "CapCut'a bak") pencere
  görüntüsü film.py goster pencere ile alınır. Kullanıcı bir değişiklik ya da devam isterse film-yap'a dönülür.
disallowed-tools: Write, Edit, NotebookEdit, Agent
allowed-tools: Bash(python .claude/bin/film.py ozet*), Bash(python .claude/bin/film.py goster*), Bash(python .claude/bin/film.py surus kapat --soru*)
---
# FİLM DURUM — soru = yalnız cevap
## 0. Bu tur otomatik sürüş kapalı (Stop kancası sürmeye zorlamaz)
!`python .claude/bin/film.py surus kapat --soru || true`
## 1. Kurallar
1. Yalnız cevap ver. Dosya yazma, ajan açma, betik çalıştırma (aşağıdaki salt okunur komutlar dışında), üretim başlatma.
2. Cevabı film.py'den al; hafızandan sayı söyleme. Sayı varsa kaynağını yaz ("film.py goster maliyet'e göre").
3. Anahtar dosyaları ve AYARLAR okunmaz; ayar sorusu: film.py goster ayar (maskeli).
4. Kullanıcıya soru sorma, öneri ya da onay isteme. Son satır en çok bir BİLGİ cümlesidir:
   "Ekip sıradaki adımda şunu yapacak: …; itiraz edersen yaz."
5. Kullanıcı değişiklik ya da devam isterse bu beceri biter; film-yap döngüsü (ya da not için film-not) sürer.
## 2. Soruya göre komut (yalnız bunlar)
| Soru | Komut |
|---|---|
| ne durumda, hangi aşama, ne zaman biter | python .claude/bin/film.py ozet --uzun |
| neden durdu, neden bekliyor | python .claude/bin/film.py goster neden-durdu |
| kaç kredi, ne harcandı | python .claude/bin/film.py goster maliyet |
| kaç token, kullanım | python .claude/bin/film.py goster token |
| şu planda / promptta ne yazıyor | python .claude/bin/film.py goster plan <no> |
| bir aşamanın ayrıntısı | python .claude/bin/film.py goster asama <kod> |
| hangi kararlar verildi, neden | python .claude/bin/film.py goster karar |
| ayarlar, izinler | python .claude/bin/film.py goster ayar (maskeli) |
| benden ne bekleniyor, sözleşme | python .claude/bin/film.py goster sozlesme |
| "CapCut'a bak", "ekrana bak" | python .claude/bin/film.py goster pencere capcut (salt okunur görüntü; fare ve klavye yok) |
## 3. Cevap biçimi
- Düz Türkçe, en çok 6 satır, teknik terim yok (aşama kodu yerine adı: "animatik", "video çekimi").
- Kavramlar ve çıkış kodlarının sabit cümleleri: ../film-yap/KULLANICI_DILI.md.
- Aktif film yoksa: yerelde tek soru kuralı geçerlidir (film-yap §1 kural 1); bulutta yalnız bulut bilgi cümlesi (film-yap §3).
- Son satır: en çok bir bilgi cümlesi, soru işareti yok.
