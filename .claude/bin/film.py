"""film.py sarmalayıcısı (TASARIM §4.2, §4.5.1): ana Claude'un çağırdığı TEK betik.

  python .claude/bin/film.py <komut> [...]      → <depo>/YZ_FILM/ARACLAR/film.py <komut> [...]

Depo kökünü kendi konumundan bulur, aracı MUTLAK yolla ve aynı Python ile çalıştırır, çıkış kodunu aynen döndürür.
Veri kökünü araç YOLLAR.json'dan okur (ortak.yollar()); bu dosya hiçbir yol ya da ayar tutmaz.
"""
import os, subprocess, sys

DEPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ARAC = os.path.join(DEPO, "YZ_FILM", "ARACLAR", "film.py")

if __name__ == "__main__":
    if not os.path.isfile(ARAC):
        sys.stdout.write("!! film.py bulunamadı: " + ARAC + "\n")
        sys.exit(4)
    sys.exit(subprocess.call([sys.executable, ARAC] + sys.argv[1:]))
