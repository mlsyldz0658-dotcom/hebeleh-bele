"""ORNEK_3_SAHNE_ZANAAT test yardımcıları (test_plan_dili, test_sureklilik): geçici film kopyası, bozuk varyant uygulama, araçları
sessiz çalıştırma. _ortam test modülünde bundan ÖNCE import edilmiş olmalı (geçici YOLLAR.json)."""
import os, sys, json, io, glob, shutil, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import _ortam, ortak
# stdout yönlendirmesinden önce yüklensin (modül yüklenirken sys.stdout.reconfigure çağırır)
import kapi, kuyruk, esikler, plan_ortak, plan_sema, plan_dili, plan_birlestir, dunya_defteri, kroki, plan_denetim, istem_derle  # noqa
import zaman_cizelgesi, kamera_agaci, cekim_listesi  # noqa

DEPO_YZ = os.path.dirname(ARACLAR)
ORNEK = os.path.join(DEPO_YZ, "FILMLER", "ORNEK_3_SAHNE_ZANAAT")
BOZUK = os.path.join(ORNEK, "_BOZUK")
_SAYAC = [0]


def kopya(ad=None):
    """Örnek filmi geçici veri köküne kopyalar (_BOZUK, _KASET ve _TEST hariç)."""
    _SAYAC[0] += 1
    kok = os.path.join(_ortam.VERI, "FILMLER", f"{ad or 'ZN'}_{_SAYAC[0]:03d}")
    shutil.copytree(ORNEK, kok, ignore=shutil.ignore_patterns("_BOZUK", "_KASET", "_TEST", "_RAPOR", "SAHNELER.json", "DUNYA_DEFTERI.json"))
    return kok


def jl(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def koy(veri, yol, deger, sil=False):
    ps = yol.split("."); d = veri
    for p in ps[:-1]: d = d[int(p)] if isinstance(d, list) else d.setdefault(p, {})
    son = ps[-1]
    if isinstance(d, list):
        if sil: d.pop(int(son))
        else: d[int(son)] = deger
    elif sil: d.pop(son, None)
    else: d[son] = deger


def varyantlar(): return sorted(os.path.splitext(os.path.basename(y))[0] for y in glob.glob(os.path.join(BOZUK, "*.json")))


def varyant(ad): return jl(os.path.join(BOZUK, ad + ".json"))


def bozuk_uygula(kok, ad):
    v = varyant(ad)
    for x in v["degisiklikler"]:
        p = os.path.join(kok, x["dosya"]); d = jl(p)
        koy(d, x["yol"], x.get("deger"), x.get("sil", False))
        ortak.atomik_yaz(p, d)
    return v


def kos(modul, *argv):
    with contextlib.redirect_stdout(io.StringIO()) as o: kod = modul.main(list(argv))
    return kod, o.getvalue()


def maddeler(r, seviye=None):
    return [(b.get("madde"), b.get("tur"), b.get("plan")) for b in (r.get("hatalar") or []) + (r.get("bayraklar") or [])
            if seviye is None or b.get("seviye") == seviye]
