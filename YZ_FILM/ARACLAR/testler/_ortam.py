"""Testlerin ortak ortamı: gerçek YOLLAR.json'a ve gerçek veri köküne DOKUNMADAN geçici bir veri kökü ve YOLLAR.json kurar.
Her test modülü araçları import etmeden ÖNCE `import _ortam` yapar (YZ_FILM_YOLLAR ortam değişkeni alt süreçlere de geçer)."""
import os, sys, json, atexit, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import ortak

KOK = tempfile.mkdtemp(prefix="yz_test_")
VERI = os.path.join(KOK, "VERI")
YOLLAR = os.path.join(KOK, "YOLLAR.json")
os.environ["YZ_FILM_YOLLAR"] = YOLLAR
os.environ.pop("YZ_FILM_VERI", None)
for d in ("AYARLAR", "FILMLER", "HESAP"): os.makedirs(os.path.join(VERI, d), exist_ok=True)
y = ortak.varsayilan_yollar(VERI); y["capcut_taslak"] = os.path.join(KOK, "CAPCUT_YOK")
ortak.atomik_yaz(YOLLAR, y)
atexit.register(shutil.rmtree, KOK, True)
