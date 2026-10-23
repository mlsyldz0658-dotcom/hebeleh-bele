---
name: soru-sadece-cevap
description: "Kullanıcı bir şey sorduğunda (ör. \"promtta ne yazıyo\") sadece cevap ver; düzeltme/başlatma yapma"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c02834a3-78d7-42ef-8b9f-3353299f1117
  modified: 2026-10-14T22:05:16.543Z
---

Kullanıcı soru sorduğunda yalnızca cevap verilir; dosya değiştirme, Memmet başlatma gibi işlemler ayrıca istenmeden yapılmaz.

**Why:** 15 Ekim 2026'da kullanıcı "bu promptta ne yazıyor" diye sordu; Claude sormadan istemi değiştirip Memmet'i yeniden başlattı, kullanıcı sinirlendi ("yarram ben sana promtta ne yazıyo dedim"). Daha önce de "şuan yapma bişey sordum sadece" demişti.

**How to apply:** Soru → cevap + gerekirse öneri ("istersen şunu yaparım"), onay gelince işlem. Bkz. [[PROJE-yapimi]].
