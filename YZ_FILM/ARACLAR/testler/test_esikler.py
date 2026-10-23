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


if __name__ == "__main__":
    unittest.main()
