# A14a · kurgucu·sifir_kredi — Sıfır kredi çözüm

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A14a Dikey kesit: teknik kapılar HATA 0, kesit seyircisinde KRİTİK 0; PILOT kararları yazılır.
Bir plan ya da sahne merdivenin sonunda `durdu`. Kredi harcamadan zorunlu çözümü yaz; hat o plansız sürecek.

Bu görev bir **merdiven basamağıdır** (§1.5): önceki turların kapı raporu ve maddeleri GIRDI'dedir; çıktın `CIKTI/rapor.json`.

## GIRDI
- `GIRDI/` — durdurulan plan(lar), neden (kapı maddesi), komşu planlar, varsa kusursuz pencere ölçümleri

## Yap
1. Kâğıtta (A07–A09): planı çıkar, köprü kartı koy ya da repliği ekran dışı sese taşı.
2. Videoda (A14–A16): kırp (kusursuz pencere ≥ eylem alt sınırı) → örtü (tepki/ekleme) → yer tutucu → L/J taşıma → ekran dışı ses → köprü kartı → çıkar.
3. Feragat edilemeyen HATA'lı öğe (güvenlik, filtre/yaş, yasak öğe, kimlik, şema) MUTLAKA çıkarılır.
4. Çözümün anlattığı bilgi kaybını ve hangi sahneye taşındığını yaz; BAYRAK.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `cozumler[{plan, cozum, basamak, bilgi_kaybi, bayrak: true}]`

## Bitirmeden
- Her durdurulan plan için tek çözüm.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
