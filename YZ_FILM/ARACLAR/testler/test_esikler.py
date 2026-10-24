"""esikler.py testleri (TASARIM D-34, §7.1): kaynak zorunlu, çift anahtar HATA, FILM_AYAR ve öğrenilen katman yalnız sıkılaştırır."""
import os, sys, json, shutil, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import esikler, memmet


def k(deger, kaynak="tahmin", **ek):
    r = {"deger": deger, "aciklama": "deneme", "etiket": "TEST", **ek}
    if kaynak: r["kaynak"] = kaynak
    return r


class Esikler(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="esik_"); self.addCleanup(shutil.rmtree, self.d, True)

    def yaz(self, ad, veri):
        p = os.path.join(self.d, ad)
        with open(p, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False)
        return p

    def hat(self):
        return self.yaz("hat.json", {"_surum": 1,
            "tavan_x": k(20, gevsetilemez=True, yon="tavan"), "taban_y": k(0.30, gevsetilemez=True, yon="taban"),
            "model": k("omni-1.1-flash", "belge", gevsetilemez=True, yon="sabit"),
            "coz": k("720p", "belge", gevsetilemez=True, yon="cozunurluk"),
            "flow_tempo_1710": k(memmet.TEMPO, "belge", gevsetilemez=True, yon={
                "gonderim_arasi_sn": "taban", "ayni_anda": "tavan", "mola_kac_gonderimde": "siklik", "gonderim_mola_dk": "taban",
                "mola_kac_partide": "siklik", "parti_mola_dk": "taban"}),
            "serbest": k(5)})

    def test_kaynaksiz_anahtar_hata(self):
        p = self.yaz("a.json", {"iyi": k(1), "kotu": k(2, kaynak=None)})
        with self.assertRaises(esikler.EsikHatasi) as c: esikler.yukle([p])
        self.assertTrue(any("kotu" in h and "kaynak" in h for h in c.exception.hatalar))

    def test_gecersiz_kaynak_ve_etiketsiz_hata(self):
        r = k(1); del r["etiket"]
        p = self.yaz("a.json", {"x": k(1, kaynak="sezgi"), "y": r})
        with self.assertRaises(esikler.EsikHatasi) as c: esikler.yukle([p])
        self.assertEqual(len(c.exception.hatalar), 2)

    def test_iki_dosyada_ayni_anahtar_hata(self):
        a = self.yaz("a.json", {"ortak": k(1)}); b = self.yaz("b.json", {"ortak": k(1), "_surum": 1})
        with self.assertRaises(esikler.EsikHatasi) as c: esikler.yukle([a, b])
        self.assertTrue(any("ortak" in h and "iki eşik dosyasında" in h for h in c.exception.hatalar))

    def test_film_ayar_gevsetemez(self):
        rap = os.path.join(self.d, "_RAPOR")
        E = esikler.yukle([self.hat()], ayar={"mod": "tam_otomatik", "butce": {"tavan_x": 40, "taban_y": 0.1},
                                             "flow": {"model": "veo-lite", "coz": "360p",
                                                      "tempo": {"gece": {"gonderim_arasi_sn": [5, 10], "ayni_anda": 4,
                                                                         "mola_kac_partide": 0}}}}, rapor=rap)
        self.assertEqual((E["tavan_x"], E["taban_y"], E["model"], E["coz"]), (20, 0.30, "omni-1.1-flash", "720p"))
        self.assertEqual(E["flow_tempo_1710"], memmet.TEMPO)
        self.assertTrue(E.bayraklar and all(b["durum"] in ("gevsek", "degismez") for b in E.bayraklar))
        r = esikler._oku(os.path.join(rap, "ESIK_AYAR.json"))
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertEqual(len(r["bayraklar"]), len(E.bayraklar))

    def test_film_ayar_sikilastirabilir(self):
        E = esikler.yukle([self.hat()], ayar={"tavan_x": 10, "taban_y": 0.5, "coz": "1080p", "serbest": 1,
                                              "tempo": {"elle": {"gonderim_arasi_sn": [10, 20], "ayni_anda": 1, "mola_kac_gonderimde": 4}}})
        self.assertEqual((E["tavan_x"], E["taban_y"], E["coz"]), (10, 0.5, "1080p"))
        self.assertEqual(E["serbest"], 5)                     # gevsetilemez olmayan anahtar FILM_AYAR'dan okunmaz
        t = E["flow_tempo_1710"]["elle"]
        self.assertEqual((t["gonderim_arasi_sn"], t["ayni_anda"], t["mola_kac_gonderimde"]), ([10, 20], 1, 4))
        self.assertEqual(E["flow_tempo_1710"]["gece"], memmet.TEMPO["gece"])
        self.assertTrue(all(b["durum"] == "sikilasti" for b in E.bayraklar))
        self.assertEqual(memmet.TEMPO["elle"]["ayni_anda"], 2)   # kaynak sözlük bozulmadı

    def test_ogrenilen_yalniz_sikilastirir(self):
        ogr = {"_surum": 3, "kurallar": [
            {"id": "OK-1", "tur": "flow_tavan", "deger": {"tavan_x": 15}, "durum": "aktif"},
            {"id": "OK-2", "tur": "esik", "deger": {"taban_y": 0.1}, "durum": "aktif"},
            {"id": "OK-3", "tur": "esik", "deger": {"tavan_x": 1}, "durum": "deneme"},
            {"id": "OK-4", "tur": "tempo", "deger": {"gece": {"ayni_anda": 1}}, "durum": "aktif"}]}
        E = esikler.yukle([self.hat()], ogrenilen=ogr)
        self.assertEqual((E["tavan_x"], E["taban_y"]), (15, 0.30))
        self.assertEqual(E["flow_tempo_1710"]["gece"]["ayni_anda"], 1)
        self.assertNotIn("OK-3", {b.get("kural") for b in E.bayraklar})

    def test_gercek_dosyalar(self):
        E = esikler.yukle()
        self.assertEqual(sum(1 for r in E.kayit.values() if r.get("kaynak") not in esikler.KAYNAKLAR), 0)
        re = esikler._oku(esikler.RE)
        eksik = [a for a, r in re.items() if not a.startswith("_") and not (r.get("kaynak") in esikler.KAYNAKLAR and r.get("etiket"))]
        self.assertEqual(eksik, [])
        self.assertEqual(E["eylem_adim_mikro_min_sn"], 0.8)
        self.assertTrue(all(r.get("gevsetilemez") for a, r in E.kayit.items() if a in (
            "flow_tempo_1710", "flow_gorsel_gunluk_tavan", "flow_gorsel_sonrasi_video_saat", "haftalik_uyari_kilidi_gun",
            "kapi_payi", "take_payi_kredi", "guvenlik_payi", "flow_model", "flow_cozunurluk_min", "klip_sn_varsayilan",
            "ajan_paralel_max", "disk_bos_min_gb")))

    def test_hat_tempo_memmet_ile_ayni(self):
        hat = esikler._oku(os.path.join(esikler.VERI_DIR, "hat_esikleri.json"))
        self.assertEqual(hat["flow_tempo_1710"]["deger"], memmet.TEMPO)
        self.assertEqual(hat["flow_cozunurluk_min"]["deger"], memmet.VARSAYILAN["video_cozunurluk"])


class BirlestirmeAnahtarlari(unittest.TestCase):
    """Birleştirme turu: koddaki sabitler eşik dosyalarına taşındı; araçlar dosyadan okur."""
    @classmethod
    def setUpClass(cls):
        cls.E = esikler.yukle()

    def test_anahtarlar_dogru_dosyada(self):
        beklenen = {
            "hat_esikleri.json": ["bildirim_tekrar_dk", "bildirim_saat_max", "uyari_gecti_tempo_carpan"],
            "sureklilik_esikleri.json": ["v1_sure_min_sn", "v1_bulaniklik_max", "v1_titreme_mae_max", "v1_scdet_esik", "v1_kesme_kenar_sn",
                                         "v2_kare_aralik_sn", "v2_kimlik_dusus_max", "v2_kimlik_hata", "v2_dino_sicrama_max",
                                         "v2_ilk_kare_sadakat_min", "v3_son_tutma_sn", "v3_son_tutma_oran_max", "k1_parlaklik_max",
                                         "k1_lab_de_max", "k1_dino_min", "enerji_fps", "g1z_keskinlik_oran_min", "g1z_dino_min", "zincir_son_pay_sn"],
            "ritim_esikleri.json": ["anlasilmayan_konusma_wer", "kanal_gosterim_min", "kanal_to_min", "kanal_izlenme_min", "tutma_dusus_min_puan",
                                    "politika_belgesi_gun_max", "plan_zincir_zaman_sapma_max_sn", "zincir_derinlik_max"],
        }
        for dosya, adlar in beklenen.items():
            for a in adlar:
                self.assertIn(a, self.E.kayit, a)
                self.assertEqual(self.E.kayit[a]["_dosya"], dosya, a)
        self.assertEqual((self.E["bildirim_tekrar_dk"], self.E["bildirim_saat_max"], self.E["anlasilmayan_konusma_wer"]), (30, 12, 0.30))
        self.assertTrue(self.E.kayit["v2_kimlik_hata"].get("gevsetilemez"))
        self.assertEqual(self.E["v2_kimlik_hata"], self.E["g1_kimlik_hata"])

    def test_arac_varsayilanlari_dosyayla_ayni(self):
        """kalite_denetim / video_denetim / kare_zinciri VARSAYILAN'ı (yalnız eşik dosyası okunamazsa) dosyadaki değerle aynıdır."""
        import ast
        for arac in ("kalite_denetim.py", "video_denetim.py", "kare_zinciri.py"):
            with open(os.path.join(os.path.dirname(HERE), arac), encoding="utf-8") as f: agac = ast.parse(f.read())
            d = next(ast.literal_eval(n.value) for n in agac.body if isinstance(n, ast.Assign)
                     and any(isinstance(h, ast.Name) and h.id == "VARSAYILAN" for h in n.targets))
            for a, v in d.items():
                self.assertIn(a, self.E, "%s: %s eşik dosyasında yok" % (arac, a))
                self.assertEqual(self.E[a], v, "%s: %s" % (arac, a))

    def test_ses_ortak_dosyadan_okur(self):
        import ast, ses_ortak as so
        self.assertFalse(hasattr(so, "ESIK"), "koddaki ESIK sözlüğü kalktı; değerler ses_esikleri.json'da")
        self.assertEqual(self.E.kayit["s1_wer_max"]["_dosya"], "ses_esikleri.json")
        self.assertEqual(so.esik("s1_agirliklar"), self.E["s1_agirliklar"])
        self.assertAlmostEqual(sum(so.esik("s1_agirliklar").values()), 1.0)
        with self.assertRaises(KeyError): so.esik("boyle_bir_esik_yok")
        aracl = os.path.dirname(HERE); adlar = set()
        for f in os.listdir(aracl):
            if not f.endswith(".py"): continue
            with open(os.path.join(aracl, f), encoding="utf-8-sig") as fh: agac = ast.parse(fh.read())
            for n in ast.walk(agac):
                if (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "esik"
                        and isinstance(n.func.value, ast.Name) and n.func.value.id in ("so", "ses_ortak")
                        and n.args and isinstance(n.args[0], ast.Constant)):
                    adlar.add(n.args[0].value)
        self.assertGreater(len(adlar), 30)
        self.assertEqual(sorted(a for a in adlar if a not in self.E), [])

    def test_bildirim_esikten(self):
        import bildirim, time
        self.assertEqual(bildirim.sinirlar(), (30 * 60, 12))
        t = time.time()
        gecmis = [{"olay": "hata", "anahtar": "x", "t": t - 20 * 60, "gonderildi": True}]
        self.assertTrue(bildirim.bastir_mi(gecmis, "hata", "x", simdi=t)[0])
        eski = esikler.yukle
        def sahte(*a, **k):
            E = eski(*a, **k); E["bildirim_tekrar_dk"] = 10; E["bildirim_saat_max"] = 1; return E
        esikler.yukle = sahte
        try:
            self.assertEqual(bildirim.sinirlar(), (600, 1))
            acil = [{"olay": "kisit_olagandisi", "anahtar": "x", "t": t - 20 * 60, "gonderildi": True}]
            self.assertFalse(bildirim.bastir_mi(acil, "kisit_olagandisi", "x", simdi=t)[0])   # 20 dk > 10 dk tekrar süresi
            self.assertTrue(bildirim.bastir_mi(acil, "kisit_olagandisi", "x", simdi=t - 15 * 60)[0])
            b, neden = bildirim.bastir_mi(gecmis, "hata", "y", simdi=t)
            self.assertTrue(b); self.assertIn("saatlik tavan (1)", neden)
            self.assertFalse(bildirim.bastir_mi(gecmis, "kisit_olagandisi", "y", simdi=t)[0])   # ACİL tavana takılmaz
            def bozuk(*a, **k): raise esikler.EsikHatasi(["bozuk"])
            esikler.yukle = bozuk
            self.assertEqual(bildirim.sinirlar(), (bildirim.TEKRAR_SN, bildirim.SAAT_MAX))   # eşik hatası bildirimi susturmaz
        finally:
            esikler.yukle = eski


if __name__ == "__main__":
    unittest.main()
