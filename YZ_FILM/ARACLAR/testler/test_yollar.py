"""PR-1 testleri: tek yol kaynağı (YOLLAR.json), depo içine veri yazılmaması, mutlak yollu .bat, tembel AI84 anahtarı,
puan medyanı ve izleme paketinde ekranda kurulmamış adın saklanması."""
import os, sys, json, shutil, tempfile, unittest, subprocess, io, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE); DEPO_YZ = os.path.dirname(ARACLAR)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import ortak, film, yeni_film, puan_oku, izleme_paketi

ORNEK = os.path.join(DEPO_YZ, "FILMLER", "ORNEK_3_SAHNE")


def depo_dosyalari():
    out = set()
    for k, ds, fs in os.walk(DEPO_YZ):
        ds[:] = [d for d in ds if d != "__pycache__"]
        out |= {os.path.relpath(os.path.join(k, f), DEPO_YZ) for f in fs if not f.endswith(".pyc")}
    return out


class Yollar(unittest.TestCase):
    def test_yollar_yoksa_acik_hata(self):
        with mock.patch.dict(os.environ, {"YZ_FILM_YOLLAR": os.path.join(_ortam.KOK, "YOK.json")}):
            with self.assertRaises(ortak.YolYok) as c: ortak.yollar()
            self.assertIn("KURULUM", str(c.exception))
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(film.main([ORNEK, "--durum"]), 4)
            r = subprocess.run([sys.executable, os.path.join(ARACLAR, "memmet.py"), ORNEK], capture_output=True, text=True,
                               encoding="utf-8", timeout=60)
            self.assertEqual(r.returncode, 4); self.assertIn("YOLLAR.json", r.stdout)

    def test_yollar_yaz_korur_ve_veri_turetir(self):
        p = os.path.join(_ortam.KOK, "Y2.json"); v = os.path.join(_ortam.KOK, "V2")
        ortak.yollar_yaz(v, p)
        d = json.load(open(p, encoding="utf-8")); d["python"]["py312"] = "C:/py312/python.exe"; ortak.atomik_yaz(p, d)
        ortak.yollar_yaz(None, p)                                # ikinci yazım: elle verilen korunur, veri kökü değişmez
        d = json.load(open(p, encoding="utf-8"))
        self.assertEqual((d["python"]["py312"], d["veri_kok"]), ("C:/py312/python.exe", os.path.abspath(v)))
        with mock.patch.dict(os.environ, {"YZ_FILM_YOLLAR": p}):
            y = ortak.yollar()
            self.assertEqual(y["ayarlar"], os.path.join(os.path.abspath(v), "AYARLAR"))
            self.assertEqual(y["filmler"], os.path.join(os.path.abspath(v), "FILMLER"))

    def test_depo_icine_veri_yazilmaz_ve_bat_mutlak(self):
        once = depo_dosyalari()
        with contextlib.redirect_stdout(io.StringIO()): d = yeni_film.kur("YOL_DENEME")
        self.assertTrue(d.startswith(_ortam.VERI))
        for b in yeni_film.batlar():
            ham = open(os.path.join(d, b), "rb").read(); metin = ham.decode("utf-8")
            self.assertNotIn("..\\..\\ARACLAR", metin); self.assertIn(os.path.join(ARACLAR, ""), metin)
            self.assertNotIn(b"\n", ham.replace(b"\r\n", b""), "CRLF olmalı")
        # örnek filmi veri kökünde sahte sağlayıcıyla baştan sona çalıştır: depoya tek dosya eklenmemeli
        k = os.path.join(_ortam.VERI, "FILMLER", "ORNEK_KOPYA"); shutil.copytree(ORNEK, k)
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(film.main([k, "--saglayici", "sahte"]), 0)
        self.assertEqual(depo_dosyalari() - once, set())

    def test_ai84_anahtarsiz_import_olmez(self):
        with mock.patch.dict(os.environ, {"AI84_KEY_FILE": os.path.join(_ortam.KOK, "bos.txt")}):
            open(os.environ["AI84_KEY_FILE"], "w").close()
            r = subprocess.run([sys.executable, "-c", "import ai84; print('IMPORT_OK')\n"
                                "try: ai84.credits()\nexcept ai84.AI84Error as e: print('HATA', 'anahtarı yok' in str(e))"],
                               cwd=ARACLAR, capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(r.returncode, 0, r.stderr); self.assertIn("IMPORT_OK", r.stdout); self.assertIn("HATA True", r.stdout)


class Duzeltmeler(unittest.TestCase):
    def test_puan_medyan(self):
        d = tempfile.mkdtemp(dir=_ortam.KOK); yollar = []
        for i, p in enumerate((6, 8, 9)):
            y = os.path.join(d, f"r{i}.md"); open(y, "w", encoding="utf-8").write(f"x\nOZET | ORTALAMA: {p} | KRITIK: 0\n"); yollar.append(y)
        self.assertEqual(puan_oku.medyan([6, 8, 9]), 8); self.assertEqual(puan_oku.medyan([6, 8]), 7)
        with contextlib.redirect_stdout(io.StringIO()) as o: self.assertEqual(puan_oku.main(yollar + ["--esik", "8"]), 0)
        self.assertIn("8.00", o.getvalue())

    def test_izleme_paketi_ad_ekranda_kurulmadan_yazilmaz(self):
        k = os.path.join(_ortam.VERI, "FILMLER", "IZLEME_DENEME"); shutil.copytree(ORNEK, k)
        p = json.load(open(os.path.join(k, "SAHNELER.json"), encoding="utf-8"))
        kar = next(iter(p["karakterler"])); p["karakterler"][kar]["tarif"] = "kızıl saçlı genç kadın"
        for s in p["sahneler"]: s.pop("replik", None)
        p["sahneler"][0]["replik"] = {"karakter": kar, "metin": "Hello there.", "cumleler": [{"en": "Hello there.", "tr": ""}]}
        ad = kar.replace("_", " ").title()
        p["sahneler"][1]["replik"] = {"karakter": "x", "metin": f"{ad}, wait!", "cumleler": [{"en": f"{ad}, wait!", "tr": ""}]}
        p["sahneler"][2]["replik"] = {"karakter": kar, "metin": "I'm here.", "cumleler": [{"en": "I'm here.", "tr": ""}]}
        json.dump(p, open(os.path.join(k, "SAHNELER.json"), "w", encoding="utf-8"))
        with contextlib.redirect_stdout(io.StringIO()): film.main([k, "--saglayici", "sahte", "--asama", "gorsel,video"])
        with contextlib.redirect_stdout(io.StringIO()): h = izleme_paketi.main(k, kare=1)
        md = open(os.path.join(h, "IZLE.md"), encoding="utf-8").read()
        satirlar = [l for l in md.splitlines() if l.startswith("- duyulan:")]
        self.assertIn("[kızıl saçlı genç kadın]", satirlar[0]); self.assertNotIn(ad.upper(), satirlar[0])
        self.assertIn(ad.upper() + ":", satirlar[2])      # adı 2. sahnede duyuldu → artık adıyla


if __name__ == "__main__":
    unittest.main()
