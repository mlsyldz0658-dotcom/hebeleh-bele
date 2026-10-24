# A07a · kart-tasarimcisi — Kart tarifi

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A07a Harita, kroki, kart tarifleri: plan_denetim --harita, kroki --denetle HATA 0 olmalı.
Karakter, kostüm ve mekân kartlarının görsel tarifini (KART_SPEC) yaz: Gemini'nin üreteceği referans kartlar.

## GIRDI
- `GIRDI/HIKAYE.json` dilimi — karakterler, kostüm değişimleri, mekânlar
- `GIRDI/KART_ISTEGI.json` (yönetmen)
- evren kartları (varsa)

## Yap
1. Her görünüm ayrı kart (kostüm başına; karakter başına ≤ {{esik:kostum_varyant_max_karakter}} kostüm).
2. Kalıcı kimlik işaretleri (yara, saç ayrımı, takı) açıkça; yaratıkta en az 3 asimetrik işaret.
3. Düz fon, tam boy + yüz yakın; yazı yok; NE YOK öğeleri yok; filtre ve yaş sözcüğü yok.
4. Merdiven turundaysan: KART kapısı maddelerini kapatan tarif revizyonu.

## CIKTI
- `CIKTI/KART_SPEC.json` — `{kartlar[{id, tur: karakter|kostum|mekan, ad, tarif_en, kimlik_isaretleri[], yasaklar[]}]}`
- Merdiven turunda `CIKTI/rapor.json`

## Bitirmeden
- Her konuşan karakterin en az bir kartı var.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
