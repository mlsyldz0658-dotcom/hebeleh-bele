---
name: film-gelistir
description: >-
  Film setinin kendisini (ARACLAR betikleri, sağlayıcılar, kancalar, ajan ve beceri dosyaları, testler) değiştirmek, Ö0-a Claude Code
  ölçümünü yapmak ya da memmet3'ü depoya aktarmak için geliştirici kipi. Film üretimi için kullanılmaz.
when_to_use: >-
  Yalnız kullanıcı "/film-gelistir" yazdığında ya da oturum açıkça bir geliştirme oturumuysa. Film sürüşü açıksa önce sürüşü kapatır;
  anahtar dosyalarına ve kullanıcının veri klasöründeki film dosyalarına dokunmaz.
disable-model-invocation: true
argument-hint: "[değişiklik | ilk-kurulum | olcum0-a | memmet3-aktar]"
---
# FİLM GELİŞTİR — sistemi değiştirme kipi
## 0. Sürüş kapanır (sürüşe bağlı yasaklar kalkar; anahtar okuma ve robocopy /MIR yasakları KALIR)
!`python .claude/bin/film.py surus kapat --gelistirme || true`
## 1. Kurallar (geliştirmede de geçerli)
1. Önce YZ_FILM/ARACLAR/CLAUDE.md'yi oku; bağlayıcı karar belgesi .claude/skills/film-yap/tartisma/TASARIM.md (parça parça oku, §9 sırası).
2. Bot tespitini atlatma yok: fare/klavye taklidi, reCAPTCHA çözme, uyarıdan sonra yeniden başlatma ya da sayfa yenileme, tempo
   hızlandırma, başka Google/Flow hesabı yok. Flow uyarısında her kipte dur. kie.ai kullanılmaz.
3. Güvenlik korkulukları gevşetilmez: test_memmet_korkuluk (T10 her kipte) ve test_veri_emniyet her değişiklikte yeşil kalır;
   sayısal güvenlik sınırları yalnız veri/hat_esikleri.json'da (gevsetilemez).
4. Gizli bilgi okunmaz, yazdırılmaz, loglanmaz, commit edilmez. AYARLAR içindeki anahtar dosyaları depoda boş kalır; anahtar
   dosyalarının yalnız varlığı ve tarihi denetlenir.
5. Kullanıcının yolları bozulmaz (veri Desktop\YZ_FILM, depo Desktop\YZ_FILM_SET); yollar ortak.yollar() ile YOLLAR.json'dan.
6. Kalıcı silme yok (eskiler _ESKI/'ye taşınır); robocopy /MIR yok; OpenMontage klasörüne dokunulmaz.
7. Kullanıcının veri klasöründeki film dosyalarına dokunulmaz; denemeler sahte filmle ya da geçici veri kökünde (testler/_ortam.py).
8. Film sürüşü bu kipte kapalıdır; film konusu sorulmaz, film başlatılmaz, Flow'a gönderim yapılmaz.
## 2. Adımlar (değişiklik)
1. python .claude/bin/film.py surus kapat --gelistirme (yukarıda kendiliğinden koştu).
2. YZ_FILM/ARACLAR/CLAUDE.md'yi oku; TASARIM'ın ilgili bölümünü bul (grep ile).
3. Değişikliği yap: küçük, testli, Python 3.10 uyumlu, stdlib; yeni ad önce veri/ADLAR.json'a.
4. Testler: python -m unittest discover -s YZ_FILM/ARACLAR/testler (ağ ve kredi yok).
5. Beceri ve ajan denetimi: python .claude/bin/film.py beceri-denetim (gerekirse --senaryo hepsi).
6. Küçük commit (kullanıcı ya da görev istediyse). Yerelde açılan oturumda commit ana dala yapılmaz: dosyalar <veri>/GELISTIRME/'de
   hazırlanır ve python .claude/bin/film.py esitle --gelistirme ile ayrı yerel/<ad>-<tarih> dalına gider (D-12); birleştirme bulutta PR ile.
## 3. ilk-kurulum (ilk yerel oturumun sırası; §8.2 adım 0b)
Ön koşul: bu bilgisayarda O0a.json yok ve PR-0, PR-1 birleşmiş. Film başlatılmaz, konu sorulmaz, Flow'a gönderim yapılmaz;
kullanıcıdan yalnız fiziksel iş istenir. Python mutlak yolla çağrılır.
1. Yollar: python YZ_FILM/ARACLAR/kurulum.py --yollar → YOLLAR.json (veri kökü yerinde kalır).
2. Veri kökü emniyeti: python YZ_FILM/ARACLAR/kurulum.py --veri-emniyet (D-02). Taşınanların listesi kullanıcıya bilgi olarak verilir.
   Kabul: EMNIYET_RAPORU.json'da yamasız Memmet'e giden giriş noktası 0.
3. memmet3-aktar (aşağıda).
4. olcum0-a (aşağıda).
## 4. olcum0-a (Ö0-a: Claude Code davranışları)
1. YZ_FILM/ARACLAR/olcum0/kanca_deneme/ kancalarını GEÇİCİ settings.local.json ile kur (asıl settings.json'a dokunma).
2. TASARIM §10.3'teki 20 davranışı tek tek sına; her biri "çalışıyor / çalışmıyor + seçilen yedek" ile kapanır.
3. <veri>/BILGI/OLCUM0/O0a.json'u yaz; geçici ayarı geri al (eski hâli _ESKI/'ye taşı, silme).
4. Kanca nabzı çalışmıyorsa PR-3 birleştirilmez; erişim kancası güvenilmezse kör roller başsız claude -p yedeğine geçer (D-11, §10.3 #19).
olcum0/ henüz depoda yoksa bu adım atlanır, O0a.json yazılmaz ve bu tek cümleyle söylenir.
## 5. memmet3-aktar
1. Kullanıcının yerel memmet3 dosyasını (veri kökü emniyeti onu _ESKI/'ye taşıdıysa oradan) <veri>/GELISTIRME/memmet3/ altına KOPYALA.
2. PR-0'ın bütün maddelerini uygula (D-02 a–g): her kipte uyarıda dur; elle kipindeki "sayfayı yenile, devam" yolunu ve gece kipindeki
   5 yenileme denemesini kaldır; 17.10 tempo varsayılanı; FLOW_TEMPO.json molası; çıkış kodları (7, 2, 4); reCAPTCHA'da dur; _surum reddi.
3. Yollarını ortak.yollar()'a bağla (Chrome profili ve MEMMET_AYAR.json <veri>/AYARLAR/'dan; içerikleri okunmaz).
4. T10'u her kip için koş (elle, gece, dogrulama).
5. python YZ_FILM/ARACLAR/esitle_gelistirme.py --ad memmet3 (anahtar taraması + yerel/memmet3-<tarih> dalı). Ana dala commit yok.
   Push yetkisi yoksa dosyalar <veri>/GELISTIRME/'de kalır; kullanıcıya bilgi: "bu klasörü bir sonraki geliştirme oturumuna ekle".
6. Birleştirme bulutta PR ile, CI'daki T10'dan geçince olur. Birleşme olmadan Ö0-b başlamaz.
## 6. Bulutta
Bulut oturumu geliştirme içindir: testler sahte ve kaset sağlayıcılarıyla koşar; gerçek üretim, Ö0 ölçümleri ve memmet3 aktarımı
yalnız kullanıcının Windows bilgisayarında yapılır.
## 7. Referans
YZ_FILM/ARACLAR/CLAUDE.md · ../film-yap/tartisma/TASARIM.md (§4, §6, §9, §10.3) · ../film-yap/GOREV_SEMASI.md
