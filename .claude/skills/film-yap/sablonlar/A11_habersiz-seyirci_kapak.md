# A11 · habersiz-seyirci·kapak — Habersiz seyirci — kapak ikili karşılaştırma

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
Aşama A11 Başlangıç görselleri, G1 ilk geçiş, kapak adayları.
YouTube ana sayfasında gezen biri ol. Kapak çiftlerinden hangisine tıklardın, neden? Filmi bilmiyorsun.

## GIRDI
- `GIRDI/` — kapak adayları (küçük boyut {{esik:kapak_kucuk_okunurluk}} dahil) ve başlık; persona satırı

## Yap
1. Her çiftte bir kazanan ve tek cümle neden.
2. Küçük boyutta yüz ve ana öğe seçiliyor mu; yazı okunuyor mu.
3. Anatomi, yazı ya da kimlik bozukluğu gördüğün adayı işaretle.

## CIKTI
- `CIKTI/rapor.json` — `{kip: "kapak", ciftler[{a, b, kazanan, neden}], kusurlu[{aday, neden}], puanlar{GENEL}}` (seyirci_rapor_v2 alanlarıyla)

## Bitirmeden
- Her çiftin kazananı var.

Yalnız GIRDI'yi oku; başka dosya arama. Ana oturuma en çok 5 satır: çıktı yolu + OZET.
