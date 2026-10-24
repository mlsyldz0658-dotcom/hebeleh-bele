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


_KANCA = []


def kanca_nabzi(film_kok, kaynak="test"):
    """Uçtan uca testler için TAM kanca nabzı (§4.5.8): içerik gerçek kancanın nabiz_icerik'inden gelir (fork_kapali, settings.json ve
    kanca dosyalarının sha'sı), böylece film.py nabiz_tamam'ın fork/sha denetimi koşulsuz çalışır. fork kapalı değilse test durur."""
    if not _KANCA:
        import importlib.util
        yol = os.path.join(ortak.DEPO_KOK, ".claude", "hooks", "kanca.py")
        spec = importlib.util.spec_from_file_location("kanca_nabiz_mod", yol); m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m); _KANCA.append(m)
    n = _KANCA[0].nabiz_icerik({"session_id": "test"}, kaynak)
    if n.get("fork_kapali") is not True: raise AssertionError("CLAUDE_CODE_FORK_SUBAGENT=0 değil: kanca nabız yazmaz")
    ortak.atomik_yaz(os.path.join(film_kok, "_GOREV", "KANCA_NABZI.json"), n)
    return n
