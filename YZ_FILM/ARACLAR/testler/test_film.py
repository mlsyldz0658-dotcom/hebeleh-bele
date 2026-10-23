"""Uçtan uca test: ORNEK_3_SAHNE'yi geçici klasöre kopyalar, hattı 'sahte' sağlayıcıyla çalıştırır. Ağ ve kredi yok.
Çalıştırma: python -m unittest discover -s ARACLAR/testler     (YZ_FILM klasöründen)
"""
import os, sys, json, shutil, tempfile, unittest, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE); ROOT = os.path.dirname(ARACLAR)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import film, istem_denetim

ORNEK = os.path.join(ROOT, "FILMLER", "ORNEK_3_SAHNE")


def calistir(*a):
    with contextlib.redirect_stdout(io.StringIO()): return film.main(list(a))


class FilmHatti(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.kok = os.path.join(self.tmp, "ORNEK_3_SAHNE")
        shutil.copytree(ORNEK, self.kok)

    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def plan(self): return json.load(open(os.path.join(self.kok, "SAHNELER.json"), encoding="utf-8"))

    def test_uctan_uca_ve_devam(self):
        self.assertEqual(calistir(self.kok, "--saglayici", "sahte"), 0)
        for n in (1, 2, 3):
            self.assertTrue(os.path.exists(os.path.join(self.kok, "SIRALI_GORSEL", f"{n:03d}.jpg")))
            self.assertTrue(os.path.exists(os.path.join(self.kok, "SIRALI_VIDEO", f"{n:03d}.mp4")))
        dlg = json.load(open(os.path.join(self.kok, "SESLER", "diyalog.json"), encoding="utf-8"))
        self.assertEqual(len(dlg["3"]["cumleler"]), 2)
        self.assertTrue(os.path.getsize(os.path.join(self.kok, "KURGU", "onizleme.mp4")) > 0)
        self.assertGreater(film.dur(os.path.join(self.kok, "KURGU", "onizleme.mp4")), 20)
        self.assertIn("Easy, little one.", open(os.path.join(self.kok, "KURGU", "altyazi_en.srt"), encoding="utf-8").read())
        st = json.load(open(os.path.join(self.kok, "FILM_DURUM.json"), encoding="utf-8"))
        self.assertEqual(list(st["asamalar"]), ["senaryo", "istem_denetim", "gorsel", "video", "ses", "muzik", "kurgu"])
        # ikinci çalıştırma: her şey atlanır, dosyalar yeniden yazılmaz
        t = os.path.getmtime(os.path.join(self.kok, "SIRALI_VIDEO", "002.mp4"))
        self.assertEqual(calistir(self.kok, "--saglayici", "sahte"), 0)
        self.assertEqual(os.path.getmtime(os.path.join(self.kok, "SIRALI_VIDEO", "002.mp4")), t)
        self.assertIn("[video] tamam, atlandı", open(os.path.join(self.kok, "FILM_KAYIT.txt"), encoding="utf-8").read())
        # bir görsel silinince yalnız o yeniden üretilir; video zaten var olduğu için dokunulmaz
        os.remove(os.path.join(self.kok, "SIRALI_GORSEL", "002.jpg"))
        self.assertEqual(calistir(self.kok, "--saglayici", "sahte"), 0)
        self.assertTrue(os.path.exists(os.path.join(self.kok, "SIRALI_GORSEL", "002.jpg")))
        self.assertEqual(os.path.getmtime(os.path.join(self.kok, "SIRALI_VIDEO", "002.mp4")), t)

    def test_denetim_hatasi_hatti_durdurur_kredi_harcanmaz(self):
        p = self.plan(); p["sahneler"][2]["referans"] = ["mara", "ember", "voss"]
        json.dump(p, open(os.path.join(self.kok, "SAHNELER.json"), "w", encoding="utf-8"))
        self.assertEqual(calistir(self.kok, "--saglayici", "sahte"), 2)
        self.assertFalse(os.path.exists(os.path.join(self.kok, "SIRALI_GORSEL")))
        self.assertIn("3 referans", open(os.path.join(self.kok, "_RAPOR", "ISTEM_DENETIM.txt"), encoding="utf-8").read())

    def _kisitli(self, kod):
        import saglayicilar as sg
        from saglayicilar.sahte import Sahte

        class Kisitli(Sahte):
            ad = "kisitli"
            def gorsel(self, *a): raise sg.Kisitlandi("deneme", kod=kod)
        sg.KAYIT["kisitli"] = "testler.test_film.Kisitli"; globals()["Kisitli"] = Kisitli
        sys.modules.setdefault("testler.test_film", sys.modules[__name__])
        f = film.Film(self.kok, {"tam_otomatik": True})
        f.ayar["saglayicilar"]["gorsel"] = ["kisitli", "sahte"]
        return f

    def test_kota_kisitinda_sonrakine_gecer(self):
        f = self._kisitli("kota")
        with contextlib.redirect_stdout(io.StringIO()): f.a_gorsel()
        self.assertEqual(len(os.listdir(os.path.join(self.kok, "SIRALI_GORSEL"))), 3)
        self.assertIn("KISITLANDI (kota)", open(os.path.join(self.kok, "FILM_KAYIT.txt"), encoding="utf-8").read())

    def test_flow_uyarisinda_ve_bilinmeyende_saglayici_degismez(self):
        for kod, cikis in (("olagandisi", 7), ("dogrulama", 2), ("bilinmeyen", 2)):
            f = self._kisitli(kod)
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(film.Durdur) as c: f.a_gorsel()
            self.assertEqual(c.exception.kod, kod)
            self.assertEqual(film.CIKIS.get(kod, 2), cikis)
            self.assertFalse(os.listdir(os.path.join(self.kok, "SIRALI_GORSEL")), "sahte sağlayıcıya geçilmemeli")

    def test_v2_dosyasini_v1_araclar_islemez(self):
        p = self.plan(); p["_surum"] = 2
        json.dump(p, open(os.path.join(self.kok, "SAHNELER.json"), "w", encoding="utf-8"))
        self.assertEqual(calistir(self.kok, "--saglayici", "sahte"), 4)
        self.assertFalse(os.path.exists(os.path.join(self.kok, "SIRALI_GORSEL")))
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as c: istem_denetim.rapor(self.kok)
        self.assertEqual(c.exception.code, 4)

    def test_onay_verilmezse_durur(self):
        f = film.Film(self.kok, {})
        f.ayar["saglayicilar"]["gorsel"] = ["flow_yerine"]
        from saglayicilar.sahte import Sahte
        kredili = type("Kredili", (Sahte,), {"ad": "kredili", "kredili": True})()
        with contextlib.redirect_stdout(io.StringIO()), unittest.mock.patch("builtins.input", return_value="h"):
            with self.assertRaises(film.Durdur): f.onay("GÖRSEL", [kredili])


class IstemDenetim(unittest.TestCase):
    def test_ornek_temiz_ama_filtre_uyarisi(self):
        plan = json.load(open(os.path.join(ORNEK, "SAHNELER.json"), encoding="utf-8"))
        b = istem_denetim.denetle(plan, ORNEK)
        self.assertFalse([x for x in b if x[0] == "HATA"])
        self.assertTrue(any(x[1] == 3 and "little" in x[2] for x in b))

    def test_uzun_replik_ve_iki_konusan(self):
        plan = {"karakterler": {"a": {"ses": "x"}}, "sahneler": [{"no": 1, "parti": 1, "gorsel_istem": "g",
                "hareket_istem": 'Mara says: "Go." Voss replies: "No." No music.',
                "replik": {"karakter": "a", "metin": " ".join(["word"] * 21)}}]}
        b = istem_denetim.denetle(plan)
        self.assertTrue(any(x[0] == "HATA" and "21 kelime" in x[2] for x in b))
        self.assertTrue(any("birden çok konuşan" in x[2] for x in b))


import unittest.mock  # noqa: E402

if __name__ == "__main__":
    unittest.main()
