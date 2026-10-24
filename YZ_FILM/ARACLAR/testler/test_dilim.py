"""dilim.py testi (TASARIM §6.2, §1.3 A07b, [SON] O-12): sahne grubu = hikâye sahnesi (1:1); paralel görevlere önceki sahnenin
sözleşmedeki cikis_durumu; yalnız aynı mekân ve zamandaki ardışık çiftte çözülmüş plan bitişi ve "bagimli" (sırayla koşar);
film.py'nin sahne_grubu adedi DILIM.json'dan; A07a parti dilimleri; HIKAYE yoksa 1."""
import os, sys, json, tempfile, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak
import film as FILM


def jo(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def hikaye():
    z = lambda gun, saat, atlama="yok": {"gun": gun, "saat": saat, "atlama": atlama}
    s = lambda sid, mekan, zaman, parti="P1": {"id": sid, "hikaye_partisi": parti, "mekan": mekan, "zaman": zaman, "hedef_sure_sn": 60,
                                              "vurus": "v", "giris_durumu": {"varliklar": {}}, "cikis_durumu": {"varliklar": {sid: 1}},
                                              "ekran": {"gorulen": ["x"], "duyulan": ["R%s" % sid[1:].zfill(4)]}}
    return {"partiler": [{"id": "P1", "sahneler": ["S01", "S03"], "tek_cumle": "t"}, {"id": "P2", "sahneler": ["S04", "S04"]}],
            "mekanlar": [{"id": "kulube"}, {"id": "orman"}],
            "sahneler": [s("S01", "kulube", z(1, "gece")), s("S02", "kulube", z(1, "gece")), s("S03", "orman", z(1, "gece")),
                         s("S04", "orman", z(1, "gece", "sonra"), "P2")],
            "replikler": [{"id": "R%04d" % i, "sahne": "S%02d" % i, "karakter": "sera", "metin": "m%d" % i, "teslim": "fisilti"}
                          for i in range(1, 5)]}


class TestDilim(unittest.TestCase):
    def setUp(self):
        self.film = tempfile.mkdtemp(prefix="dl_", dir=os.path.join(_ortam.VERI, "FILMLER"))
        ortak.atomik_yaz(os.path.join(self.film, "HIKAYE.json"), hikaye())

    def kos(self, *a):
        return subprocess.run([sys.executable, os.path.join(ARACLAR, "dilim.py")] + list(a) + ["--film", self.film],
                              capture_output=True, text=True)

    def test_a07b_gruplar_ve_sirali_cift(self):
        self.assertEqual(self.kos("--asama", "A07b").returncode, 0)
        d = jo(os.path.join(self.film, "_YONETMEN", "DILIM.json"))
        self.assertEqual([g["sahne"] for g in d["gruplar"]], ["S01", "S02", "S03", "S04"])
        self.assertEqual([g["bagimli"] for g in d["gruplar"]], [None, "G1", None, None])     # S04: zaman atlaması var
        self.assertEqual(d["sirali_ciftler"], [["G1", "G2"]])
        g2 = jo(os.path.join(self.film, "_YONETMEN", "DILIM", "G2.json"))
        self.assertEqual(g2["onceki"], {"sahne": "S01", "cikis_durumu": {"varliklar": {"S01": 1}}})
        self.assertEqual(g2["onceki_plan_bitisi"], {"durum": "bekliyor"})
        self.assertEqual(g2["replikler"][0]["metin"], "m2")
        g3 = jo(os.path.join(self.film, "_YONETMEN", "DILIM", "G3.json"))
        self.assertIsNone(g3["onceki_plan_bitisi"]); self.assertEqual(g3["onceki"]["sahne"], "S02")
        self.assertEqual(FILM.Defter(self.film)._adet_coz("sahne_grubu"), 4)          # film.py adedi buradan sayar

    def test_grup_yenile_plan_bitisi(self):
        self.assertEqual(self.kos("--asama", "A07b").returncode, 0)
        ortak.atomik_yaz(os.path.join(self.film, "_YONETMEN", "PLANLAR", "G1.json"),
                         {"planlar": [{"zanaat": {"kod": "S01-P01"}}, {"zanaat": {"kod": "S01-P02"}},
                                      {"zanaat": {"kod": "S01-P03", "bitis_durumu": "derlenir"}, "_derlenir": {"bitis_durumu": {"poz": "ayakta"}}}]})
        self.assertEqual(self.kos("--asama", "A07b", "--grup", "2").returncode, 0)
        g2 = jo(os.path.join(self.film, "_YONETMEN", "DILIM", "G2.json"))
        self.assertEqual([p["kod"] for p in g2["onceki_plan_bitisi"]["planlar"]], ["S01-P02", "S01-P03"])
        self.assertEqual(g2["onceki_plan_bitisi"]["planlar"][1]["bitis_durumu"], {"poz": "ayakta"})
        self.assertEqual(self.kos("--asama", "A07b", "--grup", "9").returncode, 1)

    def test_harita_sozlesmesi_genisletir(self):
        ortak.atomik_yaz(os.path.join(self.film, "_YONETMEN", "HARITA_P1.json"),
                         {"sahneler": {"S01": {"plan_hedef": 9, "kalip": "klasik_giris", "cikis_durumu": {"varliklar": {"tam": 1}}}}})
        self.assertEqual(self.kos("--asama", "A07b").returncode, 0)
        g1 = jo(os.path.join(self.film, "_YONETMEN", "DILIM", "G1.json")); g2 = jo(os.path.join(self.film, "_YONETMEN", "DILIM", "G2.json"))
        self.assertEqual(g1["harita"]["plan_hedef"], 9); self.assertEqual(g1["sozlesme"]["cikis_durumu"], {"varliklar": {"tam": 1}})
        self.assertEqual(g2["onceki"]["cikis_durumu"], {"varliklar": {"tam": 1}})

    def test_a07a_parti(self):
        self.assertEqual(self.kos("--asama", "A07a").returncode, 0)
        p1 = jo(os.path.join(self.film, "_YONETMEN", "DILIM", "P1.json"))
        self.assertEqual([s["id"] for s in p1["sahneler"]], ["S01", "S02", "S03"])
        self.assertEqual({m["id"] for m in p1["mekanlar"]}, {"kulube", "orman"})
        self.assertEqual([s["id"] for s in jo(os.path.join(self.film, "_YONETMEN", "DILIM", "P2.json"))["sahneler"]], ["S04"])

    def test_hatalar(self):
        os.replace(os.path.join(self.film, "HIKAYE.json"), os.path.join(self.film, "HIKAYE.yok"))
        self.assertEqual(self.kos("--asama", "A07b").returncode, 1)
        self.assertEqual(self.kos("--asama", "A99").returncode, 4)


if __name__ == "__main__":
    unittest.main()
