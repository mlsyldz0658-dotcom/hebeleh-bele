"""olcek.py testleri (TASARIM §1.6, D-04, D-05, §8.1): sayılar eşik dosyalarından türer, ölçülmeyen kapasite açıkça yazılır,
FILM_AYAR yalnız sıkılaştırır, kart ve JSON çıktıları. Ağ ve kredi yok."""
import os, sys, io, json, math, shutil, tempfile, unittest, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import esikler, olcek

ORNEK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "FILMLER", "ORNEK_3_SAHNE", "SAHNELER.json")


def sessiz(fn, *a):
    out = io.StringIO()
    with contextlib.redirect_stdout(out): kod = fn(*a)
    return kod, out.getvalue()


class Olcek(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.E = esikler.yukle()

    def test_40dk_formulden(self):
        E = self.E; o = olcek.hesapla(2400, E=E, olcum={}, ayar={})
        plan = sum(E["hedef_plan_dagilimi_40dk"].values())
        self.assertEqual(o["plan"]["kullanilan"], plan)                    # 495
        klip = math.ceil(plan * (1 - E["klip_bolme_oran_hedef"]) - 1e-9)
        self.assertEqual(o["plan"]["klip"], klip)
        taban = klip * E["kredi_klip_720p"]
        self.assertEqual(o["kredi"]["taban"], taban)
        kapi = math.ceil(taban * E["kapi_payi"] - 1e-9)
        self.assertEqual(o["kredi"]["butce_tahmini"], taban + kapi + E["take_payi_kredi"])
        self.assertEqual(o["kredi"]["gereken_bakiye"], math.ceil(o["kredi"]["butce_tahmini"] / (1 - E["guvenlik_payi"]) - 1e-9))
        # Analizdeki "40 dk ≈ 495 plan / ≈ 5.800 kredi" bulgusu: RE yeniden deneme hedefiyle (× 1,2) toplam
        self.assertEqual(plan, 495)
        self.assertTrue(5700 <= o["kredi"]["hedef_toplam"] <= 6000, o["kredi"]["hedef_toplam"])
        self.assertEqual(o["gonderim"]["video_toplam"], klip + math.ceil(kapi / E["kredi_klip_720p"]) + E["take_payi_kredi"] // E["kredi_klip_720p"])
        self.assertAlmostEqual(sum(o["kredi"]["dilimler"].values()), kapi, delta=len(o["kredi"]["dilimler"]))

    def test_sure_arttikca_buyur(self):
        a, b, c = (olcek.hesapla(s, E=self.E, olcum={}, ayar={}) for s in (1800, 2400, 2700))
        for yol in (("plan", "kullanilan"), ("kredi", "butce_tahmini"), ("gonderim", "video_toplam"), ("takvim", "video_gun")):
            x, y, z = (o[yol[0]][yol[1]] for o in (a, b, c))
            self.assertLess(x, y); self.assertLessEqual(y, z)
        self.assertLess(a["ajan"]["toplam"][1], b["ajan"]["toplam"][1])

    def test_kapasite_olculmedi_acikca_yazilir(self):
        o = olcek.hesapla(2400, E=self.E, olcum={}, ayar={})
        t = o["takvim"]
        self.assertFalse(t["kapasite_olculdu"]); self.assertFalse(t["o0b_yapildi"])
        self.assertEqual(t["kapasite_gunluk"], self.E["o0b_gun_tavanlari"][0])
        self.assertIn("ölçülmedi", t["kapasite_not"])
        self.assertTrue(any("kapasite" in m for m in o["olculmedi"]))
        self.assertEqual(t["video_gun"], math.ceil(o["gonderim"]["video_toplam"] / t["kapasite_gunluk"]))
        self.assertIn("ÖLÇÜLMEDİ", olcek.metin(o))
        o2 = olcek.hesapla(2400, E=self.E, olcum={"O0b": {"olculen_gunluk_kapasite": None, "olculemedi": True}}, ayar={})
        self.assertFalse(o2["takvim"]["kapasite_olculdu"]); self.assertTrue(o2["takvim"]["o0b_yapildi"])

    def test_olculen_kapasite_takvimi_belirler(self):
        o = olcek.hesapla(2400, E=self.E, olcum={"O0b": {"olculen_gunluk_kapasite": 20}}, ayar={})
        self.assertTrue(o["takvim"]["kapasite_olculdu"])
        self.assertEqual(o["takvim"]["video_gun"], math.ceil(o["gonderim"]["video_toplam"] / 20))
        duz = olcek.hesapla(2400, E=self.E, olcum={"olculen_gunluk_kapasite": 15}, ayar={})       # O0b.json düz biçim
        self.assertEqual(duz["takvim"]["kapasite_gunluk"], 15)
        g = o["gonderim"]["gorsel_duzeltme"]; tavan = self.E["flow_gorsel_gunluk_tavan"]
        self.assertEqual(o["takvim"]["gorsel_gun"], [math.ceil(g[0] / tavan), math.ceil(g[1] / tavan)])
        self.assertEqual(o["takvim"]["flow_gun"][0], o["takvim"]["video_gun"] + o["takvim"]["gorsel_gun"][0])   # görsel günü ≠ video günü

    def test_ayar_yalniz_sikilastirir(self):
        temel = olcek.hesapla(2400, E=self.E, olcum={}, ayar={})
        siki = olcek.hesapla(2400, olcum={}, ayar={"kapi_payi": 0.4, "gorsel_gunluk_tavan": 10})
        gevsek = olcek.hesapla(2400, olcum={}, ayar={"kapi_payi": 0.1, "gorsel_gunluk_tavan": 50})
        self.assertGreater(siki["kredi"]["kapi_payi"], temel["kredi"]["kapi_payi"])
        self.assertGreater(siki["takvim"]["gorsel_gun"][1], temel["takvim"]["gorsel_gun"][1])
        self.assertEqual(gevsek["kredi"]["kapi_payi"], temel["kredi"]["kapi_payi"])
        self.assertEqual(gevsek["takvim"]["gorsel_gun"], temel["takvim"]["gorsel_gun"])

    def test_sahne_say(self):
        with open(ORNEK, encoding="utf-8-sig") as f: v1 = json.load(f)
        n = olcek.sahne_say(v1)
        self.assertEqual((n["plan"], n["klip"], n["flow_klip"]), (len(v1["sahneler"]),) * 3)
        v2 = {"_surum": 2, "sahneler": [{"no": 1, "uretim": {"saglayici": "flow", "klip_sn": 8, "durum": "gecti"}},
                                        {"no": 2, "uretim": {"saglayici": "flow", "kaynak_klip": 1}},
                                        {"no": 3, "uretim": {"saglayici": "veo_vertex", "klip_sn": 10}}]}
        n = olcek.sahne_say(v2)
        self.assertEqual(n, {"plan": 3, "klip": 2, "flow_klip": 1, "diger_klip": 1, "uretilmis_klip": 1, "klip_sn_farkli": 1})
        o = olcek.hesapla(2400, E=self.E, olcum={}, ayar={}, plan=400, klip=330)
        self.assertEqual((o["plan"]["kullanilan"], o["plan"]["klip"]), (400, 330))
        self.assertEqual(o["kredi"]["taban"], 330 * self.E["kredi_klip_720p"])

    def test_token_ve_paket(self):
        o = olcek.hesapla(2400, E=self.E, olcum={}, ayar={})
        self.assertIsNone(o["token"]["projeksiyon"])
        o = olcek.hesapla(2400, E=self.E, olcum={"O0f": {"gorev_basi_token": 100000}, "O0e": {"gemini_api_paket": True}}, ayar={})
        self.assertEqual(o["token"]["projeksiyon"][1], o["ajan"]["toplam"][1] * 100000)
        self.assertEqual(o["el_isi"]["paket"], 0)

    def test_komut_satiri(self):
        kod, out = sessiz(olcek.main, ["--dk", "40", "--json"])
        self.assertEqual(kod, 0); j = json.loads(out)
        self.assertEqual(j["sure_sn"], 2400); self.assertEqual(j["plan"]["kullanilan"], 495)
        kod, out = sessiz(olcek.main, ["--dk", "30", "--md"])
        self.assertEqual(kod, 0); self.assertIn("SENDEN İSTENEN TEK KARAR", out)
        o30 = olcek.hesapla(1800, E=self.E, olcum={}, ayar={})
        self.assertIn(olcek.say(o30["el_isi"]["gonder_video"]) + " kez", out)
        self.assertNotIn("{", out)
        kod, out = sessiz(olcek.main, [])
        self.assertEqual(kod, 0)
        for s in ("30 dk", "40 dk", "45 dk", "ÖLÇÜLMEDİ", "BUT tahmini"): self.assertIn(s, out)
        self.assertEqual(sessiz(olcek.main, ["--bilinmeyen"])[0], 1)

    def test_film_klasorunden(self):
        d = tempfile.mkdtemp(prefix="olcek_"); self.addCleanup(shutil.rmtree, d, True)
        shutil.copy(ORNEK, os.path.join(d, "SAHNELER.json"))
        kod, out = sessiz(olcek.main, ["--film", d, "--dk", "30", "--json"])
        self.assertEqual(kod, 0)
        j = json.loads(out); self.assertEqual(j["plan"]["kaynak"], "SAHNELER.json"); self.assertEqual(j["plan"]["klip"], 3)


if __name__ == "__main__":
    unittest.main()
