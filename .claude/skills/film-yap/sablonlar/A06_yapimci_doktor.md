# A06 · yapimci·doktor — Hikâye doktoru (yapısal tur)

<!-- Görev şablonu (TASARIM §3.1 kural 6). film.py ISTEM.md'nin sonuna ekler; esik yer tutucuları eşik dosyalarından basılır. -->

## Bu görev
A06 Kâğıt seyirci: kapı GENEL medyan ≥ {{esik:seyirci_kapi_genel_min}}, KRİTİK {{esik:kopukluk_kritik_max}}; hedef GENEL ≥ {{esik:seyirci_genel_esik}}.
Döngü tıkandı (plato ya da tur tavanı). Raporları oku, kök nedeni bul ve yazara uygulanabilir YAPISAL bir düzeltme reçetesi ver. Metni kendin yeniden yazmazsın.

Bu görev bir **merdiven basamağıdır** (§1.5): önceki turların kapı raporu ve maddeleri GIRDI'dedir; çıktın `CIKTI/rapor.json`.

## GIRDI
- `GIRDI/` — son turların kapı raporları ve seyirci kararları, güncel senaryo/hikâye özeti, önceki doktor notları (varsa)

## Yap
1. Son iki turun GENEL medyanını ve kalan KRİTİK/ORTA maddelerini çıkar; tekrar eden şikâyetleri birleştir.
2. Kök nedeni sınıfla: kanca zayıf · risk sözlü değil · kahraman pasif · bilgi sırası yanlış · parti sonu kancası yok · ton karışık.
3. En çok 3 yapısal değişiklik öner; her biri: ne değişir, hangi sahneler etkilenir, hangi bulguyu kapatır, maliyeti.
4. Plato kuralı: iki tur üst üste artış {{esik:plato_genel_artis_min}} altındaysa küçük düzeltme önerme; yapı değiştir.

## CIKTI
- `CIKTI/rapor.json` — şema `denetci_rapor_v1` (`gorev`, `kip`, `sonuc`, `maddeler[{madde, seviye, konum, kanit, oneri, sahip}]`, `ozet`); ek alan `recete[{degisiklik, sahneler, kapattigi, maliyet}]`, `kok_neden`
- `CIKTI/08_DOKTOR.md` (isteğe bağlı açıklama) — son satır `OZET | recete: <n> | kok_neden: <ad>`

## Bitirmeden
- Her reçete maddesi bir bulguya bağlı.
- Reçete en çok 3 madde.
- Metin yazmadın; reçete verdin.

Ana oturuma en çok 5 satır: çıktı yolu + OZET. Puanı ve kararı dosyadan betik okur.
