# A04 · juri-uyesi·ilk_kez_izleyen — Kör jüri — ilk kez izleyen

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A04 Kör jüri: kazanan medyanı hedefi {{esik:juri_kazanan_min}}.
Anonim önerileri (`Oneri_<k>.md`) kendi rolünün gözüyle puanla. Hangi önerinin hangi eksenden geldiğini bilmezsin; tahmin etme.

## GIRDI
- `GIRDI/JURI_PAKETI/Oneri_<k>.md` — anonim öneriler
- `GIRDI/OLCUTLER.md` — ölçütlerin tanımı

## Yap
1. Her öneriyi her ölçütte 1–10 puanla; ölçütler: {{esik:juri_olcutleri}}.
2. Her puana bir cümlelik gerekçe yaz (önerinin metninden somut dayanakla).
3. Veto yalnız feragat edilemeyen nedenle (üretilemez, filtre/yaş riski, yasak öğe); gerekçesiz veto geçersizdir.
4. `mutlaka_duzelt` (kazanırsa düzeltilecek) ve `calinmaya_deger` (başka öneriye taşınabilecek fikir) listelerini doldur.
5. Rolüne sadık kal: ilk 30 saniyede kalır mıyım, anlıyor muyum.

## CIKTI
- `CIKTI/rapor.json` — şema `juri_v1`: `{rol, oneriler: {"<k>": {puan{}, gerekce{}, veto, mutlaka_duzelt[], calinmaya_deger[], siralama}}}`

## Bitirmeden
- Her önerinin her ölçütü puanlı (1–10).
- Her puanın gerekçesi var.
- Eksen tahmini yazmadın.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
