"""kapi.py testleri (TASARIM §5.7, §7.1): ortak zarf, sonuç birleştirme, ÖLÇÜLEMEDİ → BAYRAK (asla GEÇ), atomik yazım, denetim."""
import os, sys, json, shutil, tempfile, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import kapi

ARAC = os.path.join(os.path.dirname(HERE), "kapi.py")


def o(madde, seviye, plan=None, **ek):
    d = {"madde": madde, "seviye": seviye, **ek}
    if plan is not None: d["plan"] = plan
    return d


class Sonuc(unittest.TestCase):
    def test_esdeger_adlar(self):
        self.assertEqual(kapi.sonuc_normal("GEÇ"), "GEC")
        self.assertEqual(kapi.sonuc_normal("KAL"), "HATA")
        self.assertEqual(kapi.sonuc_normal("ÖLÇÜLEMEDİ"), "OLCULEMEDI")
        self.assertEqual(kapi.sonuc_normal("bayrak"), "BAYRAK")
        with self.assertRaises(ValueError): kapi.sonuc_normal("BELKI")

    def test_olculemedi_asla_gec_degil(self):
        self.assertEqual(kapi.madde_sonucu("OLCULEMEDI"), "BAYRAK")
        self.assertEqual(kapi.en_kotu(["GEC", "OLCULEMEDI"]), "BAYRAK")
        self.assertEqual(kapi.birlestir(["GEC", "ÖLÇÜLEMEDİ"]), "BAYRAK")
        self.assertFalse(kapi.gecti_mi("OLCULEMEDI"))
        self.assertTrue(kapi.engelsiz_mi("BAYRAK")); self.assertFalse(kapi.engelsiz_mi("KISMI"))

    def test_bos_gecmez(self):
        self.assertEqual(kapi.en_kotu([]), "BAYRAK")
        self.assertEqual(kapi.birlestir([]), "BAYRAK")
        self.assertEqual(kapi.rapor_kur("G1", "P1", [])["sonuc"], "BAYRAK")

    def test_birlestir(self):
        self.assertEqual(kapi.birlestir(["GEC", "GEC"]), "GEC")
        self.assertEqual(kapi.birlestir(["HATA", "HATA"]), "HATA")
        self.assertEqual(kapi.birlestir(["HATA", "GEC"]), "KISMI")
        self.assertEqual(kapi.birlestir(["KISMI", "GEC"]), "KISMI")
        self.assertEqual(kapi.birlestir(["BAYRAK", "GEC"]), "BAYRAK")
        self.assertEqual(kapi.en_kotu(["GEC", "HATA", "BAYRAK"]), "HATA")


class Rapor(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="kapi_"); self.addCleanup(shutil.rmtree, self.d, True)

    def test_ornek_kismi_ozet(self):
        olc = [o("el_nesne", "HATA", 214, olcu={"yerel": 0.04}, esik="iki kaynak", oneri="CORRECTION:el_nesne", kanit=["a.jpg"]),
               o("kimlik", "GEC", 214), o("isik", "BAYRAK", 215), o("yuz", "ÖLÇÜLEMEDİ", 216, neden="yüz bulunamadı")]
        r = kapi.rapor_kur("G1", "P1_B2", olc, asama="A11", gorev="A11-G1-007", girdi_imza="c3d4e5", arac_surum="kare_denetim 1.0",
                           birimler=[214, 215, 216, 217])
        self.assertEqual(r["sonuc"], "KISMI"); self.assertEqual(r["_uretim"]["sonuc"], "KISMI")
        self.assertEqual(r["ozet"], {"plan": 4, "gec": 1, "bayrak": 2, "hata": 1, "olculemedi": 1})
        self.assertEqual([m["madde"] for m in r["hatalar"]], ["el_nesne"])
        self.assertEqual(r["hatalar"][0]["seviye"], "HATA")
        olcm = [m for m in r["bayraklar"] if m["madde"] == "yuz"][0]
        self.assertEqual(olcm["seviye"], "BAYRAK"); self.assertTrue(olcm["olculemedi"])
        for a in kapi.ZARF_ALANLARI: self.assertIn(a, r["_uretim"])
        self.assertEqual(kapi.dogrula(r), [])

    def test_sonuc_kurallari(self):
        self.assertEqual(kapi.rapor_kur("G1", "P1", [o("a", "HATA", 1), o("a", "HATA", 2)])["sonuc"], "HATA")
        self.assertEqual(kapi.rapor_kur("G1", "P1", [o("a", "GEC", 1), o("a", "GEC", 2)])["sonuc"], "GEC")
        self.assertEqual(kapi.rapor_kur("G1", "P1", [o("a", "OLCULEMEDI", 1)])["sonuc"], "BAYRAK")
        # film düzeyinde HATA (plan yok) → HATA, geçen planlar olsa da
        self.assertEqual(kapi.rapor_kur("Z3", "v1", [o("film_sure", "HATA"), o("x", "GEC", 1)])["sonuc"], "HATA")
        self.assertEqual(kapi.rapor_kur("Z3", "v1", [o("film_sure", "GEC")])["sonuc"], "GEC")
        with self.assertRaises(kapi.RaporHatasi): kapi.rapor_kur("G1", "P1", [o("a", "KISMI", 1)])
        with self.assertRaises(kapi.RaporHatasi): kapi.rapor_kur("G1", "P1", [{"seviye": "GEC"}])

    def test_yaz_oku_yol(self):
        yol, r = kapi.kaydet(self.d, "HS_KURGU", "FILM", [o("genel", "GEC")], tur=2, tur_dosyada=True, asama="A16")
        self.assertEqual(os.path.basename(yol), "HS_KURGU_FILM_t2.json")
        self.assertFalse(os.path.exists(yol + ".tmp"))
        self.assertEqual(kapi.oku(yol)["sonuc"], "GEC")
        yol2, _ = kapi.kaydet(self.d, "G1", "P1_B2", [o("a", "HATA", 3)], tur=1)
        self.assertEqual(os.path.basename(yol2), "G1_P1_B2.json")
        self.assertEqual(kapi.son_sonuc(self.d, "G1", "P1_B2"), "HATA")
        self.assertIsNone(kapi.son_sonuc(self.d, "V1"))
        self.assertEqual(len(kapi.raporlar(self.d)), 2)

    def test_son_sonuc_imza_ve_tur(self):
        kapi.kaydet(self.d, "HS_KURGU", "FILM", [o("g", "HATA")], tur=1, tur_dosyada=True, girdi_imza="aa")
        kapi.kaydet(self.d, "HS_KURGU", "FILM", [o("g", "GEC")], tur=2, tur_dosyada=True, girdi_imza="aa")
        self.assertEqual(kapi.son_sonuc(self.d, "HS_KURGU", "FILM"), "GEC")
        self.assertIsNone(kapi.son_sonuc(self.d, "HS_KURGU", "FILM", girdi_imza="bb"))

    def test_gecersiz_rapor_yazilmaz(self):
        r = kapi.rapor_kur("G1", "P1", [o("a", "GEC", 1)])
        for boz in (lambda x: x.update(kapi="YOK"), lambda x: x.update(sonuc="OLCULEMEDI"), lambda x: x.update(kapsam="../x"),
                    lambda x: x["_uretim"].pop("girdi_imza"), lambda x: x.update(tur=0), lambda x: x.update(sonuc="HATA"),
                    lambda x: x.update(surum=1)):
            b = json.loads(json.dumps(r)); boz(b)
            self.assertTrue(kapi.dogrula(b), b)
            with self.assertRaises(kapi.RaporHatasi): kapi.yaz(self.d, b)
        self.assertEqual(os.listdir(self.d), [])
        b = json.loads(json.dumps(r)); b["bayraklar"] = [{"madde": "x", "seviye": "BAYRAK"}]
        self.assertTrue(any("GEC olamaz" in x for x in kapi.dogrula(b)))

    def test_bozuk_dosya(self):
        p = os.path.join(self.d, "G1_P1.json")
        with open(p, "w") as f: f.write("{yarim")
        with self.assertRaises(kapi.RaporHatasi): kapi.oku(p)
        self.assertEqual(kapi.raporlar(self.d), [])

    def test_kuyruk_ve_ek(self):
        r = kapi.rapor_kur("V2", "B07", [o("kimlik", "HATA", 142)], kuyruk=[{"plan": 142}], ek={"izler": ["V2_P1/142_yuz.jsonl"]})
        self.assertEqual(r["kuyruk"], [{"plan": 142}]); self.assertIn("izler", r)
        with self.assertRaises(kapi.RaporHatasi): kapi.rapor_kur("V2", "B07", [], ek={"sonuc": "GEC"})

    def test_cli(self):
        yol, _ = kapi.kaydet(self.d, "G1", "P1", [o("a", "GEC", 1)])
        bozuk = os.path.join(self.d, "Z0_P1.json")
        with open(bozuk, "w", encoding="utf-8") as f: json.dump({"kapi": "Z0"}, f)
        cal = lambda *a: subprocess.run([sys.executable, ARAC, *a], capture_output=True, text=True, encoding="utf-8").returncode
        self.assertEqual(cal("--denetle", yol), 0)
        self.assertEqual(cal("--denetle", bozuk), 1)
        self.assertEqual(cal("--denetle", os.path.join(self.d, "yok.json")), 2)
        self.assertEqual(cal("--ozet", self.d), 0)
        self.assertEqual(cal("--bilinmeyen"), 4)


if __name__ == "__main__":
    unittest.main()
