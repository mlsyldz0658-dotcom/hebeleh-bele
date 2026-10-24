# KULLANICI DİLİ — kullanıcıya söylenen sabit cümleler, .bat adları, kavramlar

İçindekiler: §Tek soru · §Bulut · §Çıkış kodları · §İlerleme · §Fiziksel işler · §.bat dosyaları · §Kavramlar · §Söylenmeyenler

Kullanıcı Türkçe konuşur, teknik bilgisi azdır. Kısa, düz, teknik terimsiz. film.py `kullaniciya` alanı doluysa ONU aynen söyle;
bu dosyadaki cümleler alan boşsa kullanılır.

## §Tek soru (aktif film yok, yerel, konu verilmedi; harfiyen)
"Filmin konusu ne olsun? Bir cümle yeter (ör. ejderha yavrusunu saklayan avcı kadın). İstersen 'sen seç' yaz."

## §Bulut (D-45; aktif film yok; kullanıcı konu verse de)
"Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz."

## §Çıkış kodları
| Kod | Ad | Cümle (film.py `kullaniciya` boşsa) |
|---|---|---|
| 0 | BİTTİ | (iş sürer; en çok 3 satır ilerleme bilgisi) |
| 1 | HATA | "Bir adımda hata oldu; ekip yeniden deniyor. Senin yapacağın bir şey yok." |
| 2 | KULLANICI | film.py'nin talimat cümlesi aynen (fiziksel iş), sonra: "Bitince kendim fark edip devam ederim." |
| 3 | AJAN | (söylenmez; ekip çalışıyor) |
| 4 | ORTAM | "Bu adım burada yapılamıyor; senin bilgisayarında sürecek." (bulutta §Bulut cümlesi) |
| 5 | BÜTÇE | "Tahmini kredi bütçeyi aşıyor; yazılmış film kısaltılmaz. Kredi yükleyince kendim devam ederim." |
| 6 | KAPI | "Ekip bütün yolları denedi; bu aşama geçmedi. Raporu hazırladım; senin yapacağın bir şey yok." |
| 7 | KISIT | "Flow uyarı verdi; hesap kilitli. GÖNDER'e basma, sayfayı yenileme. Kilidi yalnız sen kaldırırsın (UYARI_GECTI.bat)." |
| 8 | BEKLE | "Bekleme var (mola, sıra ya da çalışan iş); bitince kendim devam ederim." |

## §İlerleme (her ilerlemede en çok 3 satır)
1. Ne bitti: "Hikâye seçildi: <başlık>." · "Senaryo kilitlendi." · "Animatik hazır."
2. Şimdi ne oluyor: "Şimdi sahne planları yazılıyor."
3. Senden bir şey gerekiyor mu: yalnız fiziksel iş; yoksa bu satır yazılmaz.
Kararlar soru değil bilgi olarak söylenir: "Film 30 dakika olacak (ölçüm olmadığı için güvenli süre seçildi)."

## §Fiziksel işler (talimatı film.py verir; aynen ilet)
Gemini paketini yükleyip ZIP'i GELENLER'e koymak · Flow'da GÖNDER'e basmak (elle kip) · kredi yüklemek · CapCut'ı kapatmak ya da dışa
aktarmak · D diskini takmak · bir .bat dosyasına çift tıklamak.

## §.bat dosyaları
| Dosya | Ne işe yarar |
|---|---|
| FILM_SETI.bat | Claude'u doğru klasörde açar (her gün buradan başlanır) |
| KURULUM.bat | bir kez: kurulum ve denetim |
| GUNCELLE.bat | depoyu günceller (yerel değişiklik varsa durur) |
| FLOW_GIRIS.bat | Flow'a bir kez elle giriş (Memmet profili) |
| IZINLER.bat | gece çalışması gibi izinleri açar/kapatır |
| UYARI_GECTI.bat | Flow uyarısından sonra kilidi kullanıcı kaldırır (koşulları değiştirmez) |
| GEMINI_TEST.bat · TELEGRAM_TEST.bat · YOUTUBE_BAGLA.bat | bağlantı denemeleri |
| DEVAM.bat · DURUM.bat · DURDUR.bat | filmi sürdür / durumu gör / durdur |
| VIDEO_YARI_OTOMATIK.bat · VIDEO_GECE.bat · VIDEO_TOPLA.bat | video gönderimi (elle kip, izinle gece) ve indirme toplama |
| NOTLARI_OKU.bat · ARSIVLE.bat · YUKLE.bat · KONTROL.bat · FILM_DENEME_SAHTE.bat | notlar, arşiv, onaylı yükleme, denetim, sahte deneme |

## §Kavramlar (kullanıcıya söylerken)
| Teknik | Kullanıcıya |
|---|---|
| aşama A07b | "sahne planları" |
| animatik | "resimli taslak film (sesli)" |
| dikey kesit | "ilk dakikaların deneme çekimi" |
| kapı / GEÇ / HATA | "kontrol" / "geçti" / "düzeltiliyor" |
| habersiz seyirci | "filmi hiç bilmeyen deneme izleyicileri" |
| kredi | "Flow kredisi" ya da "ses kredisi" |
| BUT0/BUT1/BUT2 | "bütçe hesabı" |
| kanca | (söylenmez; sorun varsa KURTARMA cümlesi) |

## §Söylenmeyenler
Karar soruları YASAK ("hangisini istersin", "onaylıyor musun", "devam edeyim mi", "A mı B mi") · teknik iç ayrıntı (görev kimliği, JSON) ·
anahtar ya da ayar içeriği · "başka hesapla deneyelim" · tahminî süre ya da kredi sayısını film.py'siz söylemek.
