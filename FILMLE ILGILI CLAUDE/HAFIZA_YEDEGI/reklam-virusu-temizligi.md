---
name: reklam-virusu-temizligi
description: Kullanıcının bilgisayarındaki reklam yazılımı — PROJE B1 bitince temizlik hatırlatılacak
metadata:
  node_type: memory
  type: project
  originSessionId: c02834a3-78d7-42ef-8b9f-3353299f1117
  modified: 2026-10-14T09:14:54.150Z
---

14 Ekim 2026'da kullanıcının bilgisayarında reklam yazılımı bulundu (salt okunur taramayla).

**Bulgular:**
- Zararlı zamanlanmış görev `\GoogleUpdateDaily`: Google güncellemesi kılığında, 27 Ağustos 2026 01:41'de oluşturulmuş. 6 saatte bir `cmd /c start https://www.pop-broker.com/...` çalıştırıyor.
- Muhtemel kaynak: HKCU Run'daki "IDM trial reset" (Temp\Rar$... klasöründen çalışan crack aracı).
- AVG ve Malwarebytes yakalayamadı.
- Chrome uzantıları temiz görünüyor (Profile 12'deki Amharca adlı uzantı bir YouTube yorum toplayıcı).

**Why:** Kullanıcı "bu proje bitsin en son hallederim" dedi.

**How to apply:** PROJE Bölüm 1 bitince kullanıcıya hatırlat:
- Görev Zamanlayıcı'dan GoogleUpdateDaily'i silmesi (GoogleUserPEH görevleri gerçek, onlara dokunulmayacak)
- Görev Yöneticisi > Başlangıç'ta IDM Trial Reset'i devre dışı bırakması
- AdwCleaner taraması
- Temiz bir cihazdan Google şifresini değiştirmesi; istenirse AI84 ve Telegram anahtarlarını yenilemesi

Sistem ayarlarını Claude değiştirmez, kullanıcı yapar; Claude sonradan kontrol eder. İlgili: [[PROJE-yapimi]].
