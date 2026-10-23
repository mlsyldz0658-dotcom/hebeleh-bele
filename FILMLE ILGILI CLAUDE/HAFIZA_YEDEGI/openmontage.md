---
name: openmontage
description: "OpenMontage kuruldu (Masaüstü\\YZ_FILM\\OpenMontage, SİLME); bizim hattın yerine geçmez, parçaları ARACLAR'a köprülendi"
metadata:
  node_type: memory
  type: project
  originSessionId: 2139e0c3-5b43-4636-b0b5-3ac5f98b918e
  modified: 2026-10-18T10:57:22.152Z
---

18.10.2026: kullanıcı github.com/calesthio/OpenMontage'ı kurdurdu (C'de istedi, D değil): `C:\Users\Soysal\Desktop\YZ_FILM\OpenMontage`, kendi .venv'i, ~1,2 GB. Kullanıcı: "silme, diğer sekmelerde soracağım".

- Değerlendirme: video/görsel/ses üretimi hep ücretli API anahtarı ister (0/31 video, 0/23 görsel); Flow aboneliğimizi kullanamaz, CapCut taslağı vermez → PROJE hattı bizimkiyle kalır.
- Alınanlar (ARACLAR): `om_kopru.py` (OpenMontage araçlarını kendi venv'inde çağırır: kelime kelime Remotion altyazı + yüz izleme), `shorts_mp4.py` (dikey Short: akıllı kadraj yüz+turuncu Ember ışığı, kelime altyazı, -14 LUFS, son kart), `kalite_denetim.py` (siyah kare/donma/sessizlik/LUFS).
- mediapipe==0.10.14'e sabitlendi (yeni sürümde mp.solutions yok → yüz takibi sessizce ortadan kırpmaya düşüyordu).
- Kalite denetimi B2 Shorts'ta -21 LUFS buldu (YouTube -14 ister) → yeni hatta loudnorm var.

Bkz. [[yz-film-studyo]], [[PROJE-b2]].
