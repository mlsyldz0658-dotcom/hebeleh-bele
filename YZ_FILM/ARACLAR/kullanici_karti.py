"""KULLANICI KARTI — BASLA_BURADAN.txt'nin başındaki kullanıcı sözleşmesi kartını olcek.py'den üretir (TASARIM §8.1, §6.9, §9 adım 18).

Kartın sayıları elle yazılmaz: olcek.kart_md() hesaplar. Depodaki kart yeniden üretilebilir olsun diye girdiler sabittir:
ilk film süresi 1800 sn (Ö0-b ölçülmeden BUT0 her zaman 1800 sn seçer, D-05), ölçüm yok (OLCUM0 = {}), FILM_AYAR yok ({}),
eşikler yalnız depodaki veri/*_esikleri.json. Ölçüm gelince kart film başında kurulum/BUT0 tarafından güncellenir (kurulum.py kart()).

Kullanım:
  python kullanici_karti.py              kartı yazdırır
  python kullanici_karti.py --yaz        BASLA_BURADAN.txt'deki iki im arasını yeniden yazar
  python kullanici_karti.py --denetle    dosyadaki kart üretilenle aynı mı (0 aynı · 1 farklı/im yok)
  Kodda: kullanici_karti.kart() · kullanici_karti.dosyadaki_kart(yol) · kullanici_karti.yerlestir(metin, kart)
"""
import os, sys
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import olcek, esikler

SURE_SN = 1800
BAS = "----- SÖZLEŞME KARTI BAŞI (kullanici_karti.py yazar; elle değiştirme) -----"
SON = "----- SÖZLEŞME KARTI SONU -----"
DOSYA = os.path.join(os.path.dirname(HERE), "BASLA_BURADAN.txt")


def hesap():
    return olcek.hesapla(SURE_SN, E=esikler.yukle(), olcum={}, ayar={})


def kart(o=None):
    return olcek.kart_md(o or hesap())


def yerlestir(metin, k):
    if BAS not in metin or SON not in metin: raise ValueError("BASLA_BURADAN.txt'de kart imleri yok")
    on, kalan = metin.split(BAS, 1); _, arka = kalan.split(SON, 1)
    return on + BAS + "\n" + k + "\n" + SON + arka


def dosyadaki_kart(yol=DOSYA):
    with open(yol, encoding="utf-8-sig") as f: m = f.read().replace("\r\n", "\n")
    if BAS not in m or SON not in m: return None
    return m.split(BAS, 1)[1].split(SON, 1)[0].strip("\n")


def main(a=None):
    a = sys.argv[1:] if a is None else list(a)
    k = kart()
    if "--denetle" in a:
        ayni = dosyadaki_kart() == k
        print("kart güncel" if ayni else "kart GÜNCEL DEĞİL: python kullanici_karti.py --yaz"); return 0 if ayni else 1
    if "--yaz" in a:
        with open(DOSYA, encoding="utf-8-sig") as f: m = f.read().replace("\r\n", "\n")
        y = yerlestir(m, k)
        with open(DOSYA + ".tmp", "w", encoding="utf-8", newline="\r\n") as f: f.write(y)
        os.replace(DOSYA + ".tmp", DOSYA); print("BASLA_BURADAN.txt kartı yazıldı."); return 0
    print(k); return 0


if __name__ == "__main__":
    sys.exit(main())
