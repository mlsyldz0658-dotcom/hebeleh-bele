---
name: is-bitince-d-arsiv
description: "Biten iş klasörleri C'de kalmaz → D:\\YZ_FILM_ARSIV'e TAŞINIR (kopya değil); gerekince D'den geri çekilir"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 2139e0c3-5b43-4636-b0b5-3ac5f98b918e
  modified: 2026-10-17T21:50:27.460Z
---

Kullanıcı (18.10.2026): "C'de yer yok. Sen D'ye sadece yedek açmışsın. Mantık şu: iş bitince D'ye atacaksın, C'de yer kaplamayacak, lazım olursa D'den çekeceksin."

- Biten/eskiyen ara klasörler (eski kurgu sürümleri _v3/_v4, parti kurguları, eski taslak klasörleri) **robocopy /E /MOVE** ile `D:\YZ_FILM_ARSIV\<FİLM>\` altına taşınır. /MIR kullanma (14.10'da eski zip'i sildirdi).
- Son taslağın bağlı olduğu klasör (draft_content.json'daki "path"ler) ve dışa aktarılmamış iş taşınmaz. Kullanıcı "son video bitmedi" derse son kurgu + üretim klasörü C'de kalır.
- Çöp kutusunu boşaltmak kullanıcının işi (kalıcı silme bende yasak); geri dönüşüme atılan şey C'de yer kaplamaya devam eder, bunu söyle.

**Why:** C diski doluyor. D 840 GB boş. Önceki yedekleme mantığı (kopya) C'yi boşaltmıyordu.
**How to apply:** Her film/parti/sürüm bittiğinde, kullanıcıya sormadan eski sürümleri D'ye taşı ve taşınanların listesini ver. Bkz. [[PROJE-b2]], [[yz-film-studyo]].
