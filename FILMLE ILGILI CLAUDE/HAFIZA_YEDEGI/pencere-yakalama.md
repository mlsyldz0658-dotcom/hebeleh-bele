---
name: pencere-yakalama
description: Kullanıcının masaüstü uygulamalarını (CapCut vb.) arkadayken PowerShell PrintWindow ile görme yöntemi; kullanıcı ekran görüntüsü atmak istemiyor
metadata:
  node_type: memory
  type: feedback
  originSessionId: c02834a3-78d7-42ef-8b9f-3353299f1117
  modified: 2026-10-15T01:12:50.964Z
---

Kullanıcı ekran görüntüsü atmaktan yoruldu: "ekran görüntüsü al, önemli yerlerde hafızana at" (15.10.2026). Masaüstü uygulamasının penceresi PowerShell + user32 PrintWindow(flag 2) ile arkadayken de yakalanabiliyor (simge durumunda değilse). Betik örneği: Get-Process CapCut → MainWindowHandle → GetWindowRect → PrintWindow → PNG, sonra Read ile bak.

**Why:** CapCut Director/Seedance incelemesi sırasında kullanıcı sürekli ekran atıyordu.
**How to apply:** "bak" denince pencereyi kendin yakala. Fare/klavye kontrolü yapma; kredi/para harcatan onaylara (Approve, Generate) kullanıcı basar — Claude söyler. Bkz. [[seedance-director-yontemi]].
