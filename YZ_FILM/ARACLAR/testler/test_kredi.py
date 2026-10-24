"""kredi.py testleri (TASARIM D-05, D-23, D-31, §7.2 BUT0/BUT1/BUT2/BUTK): süre seçimi, bütçe kapıları, dilimler, tavanlar,
kredi defteri. Geçici klasörlerde; ağ ve kredi yok."""
import os, sys, io, json, shutil, tempfile, unittest, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import esikler, olcek, kredi

ORNEK = os.path.join(os.path.dirname(os.path.dirname(HERE)), "FILMLER", "ORNEK_3_SAHNE", "SAHNELER.json")


def oku(p, metin=False):
    with open(p, encoding="utf-8") as f: return f.read() if metin else json.load(f)


def sessiz(fn, *a):
    with contextlib.redirect_stdout(io.StringIO()): return fn(*a)


class Temel(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.E = esikler.yukle()

    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="kredi_"); self.addCleanup(shutil.rmtree, self.d, True)
        self.film = os.path.join(self.d, "FILM"); os.makedirs(self.film)
        shutil.copy(ORNEK, os.path.join(self.film, "SAHNELER.json"))


class But0(Temel):
    def test_o0b_yoksa_1800_ve_rapor(self):
        r, kod = kredi.but0(olcum={}, ayar={}, film=self.film)
        self.assertEqual((kod, r["sure_sn"], r["ust_sinir_sn"]), (0, 1800, 1800))
        self.assertIn("Ö0-b", r["neden"]); self.assertFalse(r["kapasite"]["olculdu"])
        self.assertEqual(r["olcum_kredi"], sum(self.E["o0b_gun_tavanlari"]) * self.E["kredi_klip_720p"])     # ≤ 540 ölçüm harcaması
        self.assertEqual(len(r["bilgi"]), 3); self.assertIn("ölçülmedi", r["bilgi"][0])
        dosya = oku(os.path.join(self.film, "_RAPOR", "BUT0_FILM.json"))
        self.assertEqual(dosya["kapi"], "BUT0"); self.assertEqual(dosya["_uretim"]["asama"], "A01")

    def test_gorev_ve_tur_goreV_json_dan(self):
        """film.py görevi altında _uretim.gorev = GOREV.json id, tur = tur_no (kapi_oku 'rapor_bu_goreve_ait_degil' demesin)."""
        r, _ = kredi.but0(olcum={}, ayar={}, film=self.film)
        self.assertIsNone(r["_uretim"]["gorev"]); self.assertIsNone(r["tur"])
        gd = os.path.join(self.film, "_GOREV", "A01-B0-s1-t2")
        os.makedirs(gd); json.dump({"id": "A01-B0-s1-t2", "tur_no": 2, "asama": "A01"}, open(os.path.join(gd, "GOREV.json"), "w"))
        from unittest import mock
        with mock.patch.dict(os.environ, {"YZ_FILM_GOREV": gd}):
            r, _ = kredi.but0(olcum={}, ayar={}, film=self.film)
        d = oku(os.path.join(self.film, "_RAPOR", "BUT0_FILM.json"))
        self.assertEqual((d["_uretim"]["gorev"], d["tur"], d["_uretim"]["asama"]), ("A01-B0-s1-t2", 2, "A01"))

    def test_olculemedi_ve_dusuk_kapasite_1800(self):
        for o in ({"O0b": {"olculen_gunluk_kapasite": None, "olculemedi": True}}, {"O0b": {"olculen_gunluk_kapasite": 15}}):
            r, _ = kredi.but0(olcum=o, ayar={"butce": {"takvim_hedef_gun": 365}})
            self.assertEqual(r["sure_sn"], 1800, o)

    def test_varsayilan_takvimde_40dk_sigmaz(self):
        # 20/gün ölçülse bile 21 günlük hedefe 40 dk sığmaz (video gönderimi / 20 > 21) → 1800 (D-05)
        r, _ = kredi.but0(olcum={"O0b": {"olculen_gunluk_kapasite": 20}}, ayar={})
        o40 = olcek.hesapla(2400, E=self.E, olcum={"O0b": {"olculen_gunluk_kapasite": 20}}, ayar={})
        self.assertGreater(o40["takvim"]["video_gun"], 21)
        self.assertEqual(r["sure_sn"], 1800); self.assertIn("sığmıyor", r["neden"])

    def test_en_uzun_sigan_sure(self):
        o = {"O0b": {"olculen_gunluk_kapasite": 20}}
        r, _ = kredi.but0(olcum=o, ayar={"butce": {"takvim_hedef_gun": 365}})
        self.assertEqual(r["sure_sn"], 2700); self.assertEqual(r["sonuc"], "GEC")
        g40 = olcek.hesapla(2400, E=self.E, olcum=o, ayar={})["takvim"]["video_gun"]
        g45 = olcek.hesapla(2700, E=self.E, olcum=o, ayar={})["takvim"]["video_gun"]
        r, _ = kredi.but0(olcum=o, ayar={"butce": {"takvim_hedef_gun": g40}})
        self.assertTrue(2400 <= r["sure_sn"] < 2700 or g40 == g45, r["sure_sn"])
        # bakiye 40 dk'ya yetmiyorsa 1800
        b40 = olcek.hesapla(2400, E=self.E, olcum=o, ayar={})["kredi"]["butce_tahmini"]
        r, _ = kredi.but0(olcum=o, ayar={"butce": {"takvim_hedef_gun": 365}}, bakiye=b40)
        self.assertEqual(r["sure_sn"], 1800)


class But12(Temel):
    def test_but1_tavan(self):
        r, kod = kredi.but1(self.film, ayar={}, olcum={})
        self.assertEqual(kod, 0); self.assertEqual(r["sahneler"]["klip"], 3)
        on = oku(os.path.join(self.film, "URETIM_ONIZLEME.json"))
        self.assertTrue(on["taslak"])
        r, kod = kredi.but1(self.film, ayar={"butce": {"flow_kredi_tavan_film": 100}}, olcum={})
        self.assertEqual(kod, kredi.BUTCE); self.assertEqual(r["sonuc"], "HATA")
        self.assertTrue(os.path.exists(os.path.join(self.film, "_RAPOR", "BUT1_FILM.json")))

    def test_but1_sahneler_yok(self):
        os.remove(os.path.join(self.film, "SAHNELER.json"))
        with self.assertRaises(kredi.Girdi): kredi.but1(self.film, ayar={}, olcum={})
        self.assertEqual(sessiz(kredi.main, ["but1", "--film", self.film]), 1)

    def test_but2_bakiye(self):
        with self.assertRaises(kredi.Girdi): kredi.but2(self.film, None, ayar={}, olcum={})
        r, kod = kredi.but2(self.film, 100000, ayar={}, olcum={})
        self.assertEqual((kod, r["sonuc"]), (0, "GEC"))
        on = oku(os.path.join(self.film, "URETIM_ONIZLEME.json"))
        self.assertIs(on["taslak"], False); self.assertEqual(on["butce"]["toplam"], r["butce"]["toplam"])
        self.assertIn("kredi gerekiyor", oku(os.path.join(self.film, "URETIM_ONIZLEME.md"), metin=True))
        toplam = r["butce"]["toplam"]
        r, kod = kredi.but2(self.film, toplam, ayar={}, olcum={})                 # güvenlik payı yüzünden yetmez
        self.assertEqual(kod, kredi.BUTCE)
        self.assertIn("kredi gerekiyor", r["hatalar"][0]["oneri"])
        r, kod = kredi.but2(self.film, -(-toplam * 10 // 9) + 1, ayar={}, olcum={})
        self.assertEqual(kod, 0)

    def test_but2_kuyruk_kapi_payini_buyutur(self):
        r0, _ = kredi.but2(self.film, 100000, ayar={}, olcum={})
        os.makedirs(os.path.join(self.film, "KUYRUK"))
        with open(os.path.join(self.film, "KUYRUK", "YENIDEN_URET.json"), "w", encoding="utf-8") as f:
            json.dump([{"id": "YU-1", "tur": "video", "durum": "bekliyor", "kredi_tahmini": 240},
                       {"id": "YU-2", "tur": "gorsel", "durum": "bekliyor", "kredi_tahmini": 0}], f)
        r1, _ = kredi.but2(self.film, 100000, ayar={}, olcum={})
        self.assertEqual(r1["butce"]["kapi_payi"], max(240, r0["butce"]["kapi_payi"]))


class Butk(Temel):
    def hazirla(self, ayar=None):
        kredi.but2(self.film, 100000, ayar=ayar or {}, olcum={})
        return oku(os.path.join(self.film, "URETIM_ONIZLEME.json"))["butce"]

    def test_but2siz_flow_reddedilir(self):
        with self.assertRaises(kredi.Girdi): kredi.butk(self.film, "P1", 12, ayar={})

    def test_dilim_ve_aktarim(self):
        b = self.hazirla()
        r, kod = kredi.butk(self.film, "P1", b["ana"], ayar={})
        self.assertEqual(kod, 0)
        r, kod = kredi.butk(self.film, "P2", 12, ayar={})                          # ana dilimi bekleyen onayla doldu
        self.assertEqual(kod, kredi.BUTCE)
        fazla = b["dilimler"]["goruntu"] + 12
        r, kod = kredi.butk(self.film, "YU-7", fazla, dilim="goruntu", ayar={})
        self.assertEqual(kod, kredi.BUTCE); self.assertIn("KRİTİK", r["neden"])
        r, kod = kredi.butk(self.film, "YU-7", fazla, dilim="goruntu", kritik=True, aktar_not="hat-denetcisi: KRİTİK kimlik", ayar={})
        self.assertEqual(kod, 0); self.assertIsNotNone(r["aktarim"])
        oz = kredi.defter_ozet(self.film)["birim"]["flow"]
        self.assertEqual(oz["onay"], 2); self.assertEqual(oz["red"], 2)
        self.assertEqual(oz["harcanan"], 0); self.assertEqual(oz["bekleyen"], b["ana"] + fazla)
        kredi.defter_ekle(self.film, "gonderim", b["ana"], madde="P1", plan=1)    # gönderim gelince bekleyen düşer
        oz = kredi.defter_ozet(self.film)["birim"]["flow"]
        self.assertEqual((oz["harcanan"], oz["bekleyen"]), (b["ana"], fazla))

    def test_flow_film_tavani(self):
        self.hazirla()
        r, kod = kredi.butk(self.film, "P1", 24, ayar={"butce": {"flow_kredi_tavan_film": 20}})
        self.assertEqual(kod, kredi.BUTCE); self.assertIn("film tavanı", r["neden"])

    def test_usd_kapali_ve_acik(self):
        self.assertEqual(kredi.butk(self.film, "V1", 1, birim="usd", ayar={})[1], kredi.BUTCE)
        a = {"butce": {"usd_tavan_film": 5}}
        self.assertEqual(kredi.butk(self.film, "V1", 3, birim="usd", ayar=a)[1], 0)
        kredi.defter_ekle(self.film, "gonderim", 3, birim="usd", madde="V1")
        self.assertEqual(kredi.butk(self.film, "V2", 3, birim="usd", ayar=a)[1], kredi.BUTCE)

    def test_ai84_tavanlari_yalniz_duser(self):
        a = {"butce": {"ai84_kredi_tavan_film": 100000, "ai84_vc_tavan_film": 1000}}
        T, b = kredi.tavanlar(a)
        self.assertEqual((T["ai84_kredi_tavan_film"], T["ai84_vc_tavan_film"]), (60000, 1000))
        self.assertEqual([x["durum"] for x in b], ["gevsek"])
        self.assertEqual(kredi.butk(self.film, "S1", 60001, birim="ai84", ayar=a)[1], kredi.BUTCE)
        self.assertEqual(kredi.butk(self.film, "VC1", 1001, birim="ai84", dilim="vc", ayar=a)[1], kredi.BUTCE)
        self.assertEqual(kredi.butk(self.film, "VC2", 900, birim="ai84", dilim="vc", ayar=a)[1], 0)
        T, b = kredi.tavanlar({"butce": {"usd_tavan_film": -3, "takvim_hedef_gun": 0}})
        self.assertEqual((T["usd_tavan_film"], T["takvim_hedef_gun"]), (0, 21)); self.assertEqual(len(b), 2)


class Defter(Temel):
    def test_ekle_oku_ozet_ve_yarim_satir(self):
        kredi.defter_ekle(self.film, "gonderim", 12, plan=1, is_kimligi="a1")
        kredi.defter_ekle(self.film, "gonderim", 12, dilim="goruntu", plan=1)
        kredi.defter_ekle(self.film, "iade", 12, dilim="goruntu", plan=1, **{"not": "politika reddi kredi yakmadı"})
        with open(kredi.defter_yolu(self.film), "a", encoding="utf-8") as f: f.write('{"olay": "gonderim", "kre')   # çökme
        satir, bozuk = kredi.defter_oku(self.film)
        self.assertEqual((len(satir), bozuk), (3, 1))
        oz = kredi.defter_ozet(self.film)
        self.assertEqual(oz["birim"]["flow"]["harcanan"], 12); self.assertEqual(oz["birim"]["flow"]["dilim"]["goruntu"], 0)
        for k in satir: self.assertIn("zaman", k)

    def test_gecersiz_kayit(self):
        for a in (("harca", 1), ("gonderim", -1), ("gonderim", "on")):
            with self.assertRaises(ValueError): kredi.defter_ekle(self.film, *a)
        with self.assertRaises(ValueError): kredi.defter_ekle(self.film, "gonderim", 1, birim="tl")

    def test_komut_satiri(self):
        self.assertEqual(sessiz(kredi.main, []), 1)
        self.assertEqual(sessiz(kredi.main, ["but0", "--film", self.film]), 0)
        self.assertEqual(sessiz(kredi.main, ["but2", "--film", self.film]), 1)                # bakiye yok
        self.assertEqual(sessiz(kredi.main, ["but2", "--film", self.film, "--bakiye", "100000"]), 0)
        self.assertEqual(sessiz(kredi.main, ["kaydet", "--film", self.film, "--olay", "gonderim", "--kredi", "12", "--plan", "1"]), 0)
        self.assertEqual(sessiz(kredi.main, ["butk", "--film", self.film, "--madde", "U", "--kredi", "1", "--birim", "usd"]), 5)
        self.assertEqual(sessiz(kredi.main, ["ozet", "--film", self.film, "--json"]), 0)
        self.assertEqual(sessiz(kredi.main, ["kaydet", "--film", self.film, "--olay", "yok", "--kredi", "1"]), 1)


if __name__ == "__main__":
    unittest.main()
