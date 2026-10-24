# reference/goruntu_sureklilik.md — kartlar, görseller, video, süreklilik kapıları (A10d–A14; bilgi, kural taşımaz)

İçindekiler: §1 Akış · §2 Kart kapısı · §3 G1 · §4 Video kapıları V1–V3 · §5 Zincir karesi G1Z · §6 Kuyruk · §7 Kör gözlem nasıl kullanılır

## §1 Akış
| Aşama | Ne | Kim |
|---|---|---|
| A10d | karakter/mekân kartları: `istem_derle --kart` → Gemini paketi (kullanıcı taşır) → `gemini_al` → `kart_denetim` + `kare-tarifcisi·kart` → `yonetmen·kart_secimi` → `evren.py --kilitle` | betik + kör gözlem + yönetmen |
| A11 | başlangıç görselleri (plan başına 2 aday), G1 ilk geçiş, kapak adayları | betik + `kare-tarifcisi·g1` + `sureklilik-denetcisi·hakem` |
| A12 | animatik (resimli taslak; görsellerle) | §kurgu.md |
| A14a, A14 | video (Flow, `elle` kip; kullanıcı GÖNDER'e basar) | Memmet + V1/V2/V3 + `kare-tarifcisi·v3` |

Sıra kuralları: animatik ONAYLI olmadan video görevi açılmaz; videoya yalnız G1 (zincirde G1Z) GEÇ ve SHA1'i eşleşen kare gider;
yoğun görsel düzeltme yapılan gün video gönderilmez.

## §2 Kart kapısı (KART)
Yüz sayısı = görünüm sayısı; yüz öz tutarlılığı ve kadronun ötekilerine benzememe (kimlik bantları); foto/çizim üslubu; düz fon; plakada kişi yok;
NE YOK öğesi yok; hikâyeye bağlı öğe uyuşmazlığı yok; yaratıkta asimetrik işaretler. Kart tarifi revizyonu küresel bütçeden (2).

## §3 G1 (başlangıç karesi)
Yerel ölçüm (en-boy, çözünürlük, yüz bulma, kimlik benzerliği, ağız, parmak, keskinlik, renk) + kör gözlem (`kare-tarifcisi·g1`: soruları
GIRDI'den cevaplar, beklenen listeyi görmez) + kod kararı (`kare_denetim --karar`). İki kaynak (ölçüm + kör) uyuşursa HATA kesin; tek kaynak
BAYRAK → hakem (`sureklilik-denetcisi·hakem`). Kimlik HATA eşiği `gevsetilemez`. İfade uyumu film düzeyinde `ifade_uyum_min_oran`.

## §4 Video kapıları
- V1 (her indirme): siyah kare, donma, bulanıklık, sahne kesmesi, titreme, kısa süre (kesik indirme). Kusur kullanılan pencerenin dışındaysa `kirp`.
- V2 (blok arası): yarım saniyede bir kimlik düşüşü, yüz/kişi sayısı değişimi, sıçrama, ekran yönü, ilk kare sadakati, hareket hızı (`beklenen_hiz`).
- V3 (blok arası): kesme anındaki kare kör gözlemi ↔ `bitis_durumu` kritik olguları (HATA), adım zamanları (`plan_zincir_zaman_sapma_max_sn`),
  son 0,5 sn durgunluğu, ifade uyumu.
- SC1: ses dönüşümü için metin hizalaması (Veo konuştu mu, doğru kişi mi).

## §5 Zincir karesi (G1Z)
`son_kare` zincirinde önceki klibin son karesi sonraki klibin başlangıcı olur; kare kimlik bantlarından, keskinlikten ve kişi sayısından geçmelidir.
Derinlik ≤ `zincir_derinlik_max`; zincir karesi alınmadan önce son adımın içinde ≥ `zincir_cikis_tutma_ic_min_sn` tutma gerekir.

## §6 Kuyruk (`KUYRUK/YENIDEN_URET.json`)
Her kapı maddesi aynı şemayla yazılır (`semalar/kuyruk_madde_v1.json`): kaynak kapı, kök neden (`veri/kok_neden.json`), seviye, öncelik
(konum ağırlığı × doğrulanmış çarpanı), çözüm (`yeniden_cek`, `bitis_sabit`, `yeni_plan`, `yeni_sahne`, `kirp`), CORRECTION cümlesi,
0 kredi denemesi. Plan soyu başına toplam deneme 3; dolunca `yonetmen·onarim`, sonra `durdu` + `kurgucu·sifir_kredi`.

## §7 Kör gözlem nasıl kullanılır
Kör gözlemci yalnız kareyi ve soruları görür; plan metni, amaç, beklenen cevap gitmez. Cevabı kod karşılaştırır. Gözlemcinin "emin değilim"
cevabı ÖLÇÜLEMEDİ sayılır (HATA değil); iki kör cevap uyuşmazsa BAYRAK.
