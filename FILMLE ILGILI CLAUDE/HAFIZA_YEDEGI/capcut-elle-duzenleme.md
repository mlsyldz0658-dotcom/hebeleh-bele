---
name: capcut-elle-duzenleme
description: "Kullanıcı CapCut'ta klipleri elle siler/kırpar/taşır; bu değişiklikler kurgu betiğine işlenip proje yeniden kurulmalı (ses kanalları kaymasın)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c02834a3-78d7-42ef-8b9f-3353299f1117
  modified: 2026-10-15T15:27:54.667Z
---

Kullanıcı bazen not yazmak yerine CapCut'ta doğrudan düzenliyor (15.10.2026: saklama sahnesini prolog önüne taşıdı, H2'yi sildi, H4'ü kırptı). CapCut'ta yalnız Klipler kanalı kayınca Diyalog/Anlatıcı/Müzik/Ortam/Altyazı eski yerinde kalır ve boşluklar oluşur.

**Why:** Kullanıcı "bi sahne sildim, kırptım, arada boşluk var, kontrol et" dedi; anlatıcı yanlış görüntülerin üstüne kaymıştı.
**How to apply:** "Değiştirdim/kontrol et" denince taslağı salt okunur incele (draft_content.json, Klipler kanalı: sıra, source_timerange, boşluklar; "Birleşik klip" = birleşik/compound), farkları kurgu betiğinin plan listesine işle, projeyi yeniden kur, boşluk kontrolünü tekrarla. Kullanıcının kurgu kararlarına saygı: aynen uygula. Bkz. [[PROJE-yapimi]].
