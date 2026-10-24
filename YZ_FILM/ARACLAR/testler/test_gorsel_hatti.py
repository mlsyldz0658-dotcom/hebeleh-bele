"""Görsel hattı yardımcı testleri (PR-8): istem_derle_gorsel (kimlik dizesi aynen, çıplak sol/sağ yok, CORRECTION tek, referans ≤ 2 kart +
ebeveyn, basamak), gemini_paket (> 10 ek → REFERANSLAR.zip, düzeltme paketi yok), gemini_al (ZIP güvenliği, 16:9 kırpma/ret, SIRALI_GORSEL'e
yazmaz, _ISLENDI), duzeltme (şablon, ayna yasağı, işaret dosyası), kapak (aday sayısı, ikili seçim, 1280×720 çıktı)."""
import os, sys, io, json, glob, zipfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401
import _gorsel_fikstur as F
import ortak, kor
import istem_derle, istem_derle_gorsel as idg, gemini_paket, gemini_al, duzeltme, kapak


def _jpg_bayt(w, h):
    from PIL import Image
    b = io.BytesIO(); Image.new("RGB", (w, h), (100, 110, 120)).save(b, "JPEG"); return b.getvalue()


class Istem(unittest.TestCase):
    def test_gorsel_istem(self):
        F.evren_kur(); kok = F.film_kur("IS")
        kod, r = idg.derle_gorsel(kok)
        self.assertEqual(kod, 0)
        P = F.planlar(kok)
        mara = ortak.json_oku(os.path.join(F.EVREN, "TEST", "karakterler", "mara", "karakter.json"))["kimlik_en"]
        for no, p in P.items():
            self.assertEqual(istem_derle.yasak_bul(p["gorsel_istem"]), [], p["gorsel_istem"])
            self.assertLessEqual(len([x for x in p["uretim"]["gorsel"]["referanslar"] if x.startswith("kart:")]), 2)
            self.assertEqual(p["uretim"]["gorsel"]["basamak"], 1)
        self.assertIn("Mara — " + mara, P[101]["gorsel_istem"])
        self.assertIn("Mara's RIGHT hand holds a lit lantern", P[101]["gorsel_istem"])
        self.assertIn("plaka:kulube/ic_genel", P[101]["uretim"]["gorsel"]["referanslar"])
        self.assertTrue(os.path.isfile(os.path.join(kok, "YAYIN", "KAPAK_SPEC.json")))
        # CORRECTION alan başına tek cümle, değiştirilir
        s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
        s["sahneler"][0]["_derlenir"]["duzeltmeler"] = {"agiz": "CORRECTION: Mara's mouth is closed, lips together."}
        ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s); idg.derle_gorsel(kok)
        s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
        s["sahneler"][0]["_derlenir"]["duzeltmeler"]["agiz"] = "CORRECTION: Mara's mouth is closed."
        ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s); idg.derle_gorsel(kok)
        g = F.planlar(kok)[101]["gorsel_istem"]
        self.assertEqual(g.count("CORRECTION:"), 1); self.assertTrue(g.endswith("CORRECTION: Mara's mouth is closed."))

    def test_basamak(self):
        self.assertEqual(idg.basamak({"zanaat": {"zincir": {"baslangic": "kart"}}}), 1)
        self.assertEqual(idg.basamak({"zanaat": {"zincir": {"baslangic": "turev"}}}), 2)
        self.assertEqual(idg.basamak({"zanaat": {"zincir": {"baslangic": "son_kare"}}}), 3)


class Paket(unittest.TestCase):
    def test_referans_zip_ve_ertelenen(self):
        F.evren_kur(); kok = F.film_kur("PK")
        refs = {}
        for i in range(11):
            p = os.path.join(_ortam.KOK, f"ref{i}.jpg"); F._jpg(p); refs[f"R{i}.jpg"] = p
        m = gemini_paket._yaz_paket(kok, "PK_GORSEL_B1_t1", "gorsel", [{"blok": "x", "dosya": "101_a.jpg", "referans": ["R0.jpg"], "istem": "p"}],
                                    refs, 1, "16:9", {"101_a.jpg": {"tur": "gorsel", "plan": 101, "aday": "a"}})
        self.assertTrue(m["referanslar_zip"])
        self.assertTrue(os.path.isfile(os.path.join(m["klasor"], "REFERANSLAR.zip")))
        self.assertFalse(os.path.isdir(os.path.join(m["klasor"], "REFERANSLAR")))
        self.assertIn(m["zip_adi"], open(os.path.join(m["klasor"], "GOREV.txt"), encoding="utf-8").read())
        self.assertTrue(os.path.isfile(os.path.join(kok, "GELENLER", "_PAKETLER", m["paket"] + ".json")))


class Al(unittest.TestCase):
    def test_zip_guvenligi_ve_169(self):
        F.evren_kur(); kok = F.film_kur("AL")
        idg.derle_gorsel(kok); kod, ms = gemini_paket.paket_gorsel(kok, 1, 2, 1, kapak=False)
        z = os.path.join(kok, "GELENLER", ms[0]["zip_adi"])
        with zipfile.ZipFile(z, "w") as zz:
            zz.writestr("out/101_a.png", _jpg_bayt(1400, 768))          # %2,3 sapma → kırpılır
            zz.writestr("101_b.jpg", _jpg_bayt(768, 1376))              # dikey → ret
            zz.writestr("../../kotu.jpg", _jpg_bayt(1376, 768))         # zip-slip denemesi → yalnız ad, eşleşmeyen
            zz.writestr("102_a.jpg", _jpg_bayt(1280, 720))
            zz.writestr("oku.txt", b"merhaba")
        kod, rap = gemini_al.al(kok, "gorsel")
        self.assertEqual(kod, 0)
        al = {os.path.basename(a["hedef"]): a for a in rap["alinan"]}
        self.assertTrue(al["101_a.jpg"]["kirpildi"])
        from PIL import Image
        w, h = Image.open(os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "101_a.jpg")).size
        self.assertLess(abs(w / h - 16 / 9) / (16 / 9), 0.01)
        self.assertTrue(any(r["dosya"] == "101_b.jpg" for r in rap["reddedilen"]))
        self.assertIn("kotu.jpg", rap["eslesmeyen"])
        self.assertFalse(os.path.exists(os.path.join(kok, "..", "kotu.jpg")))
        self.assertFalse(glob.glob(os.path.join(kok, "SIRALI_GORSEL", "*.jpg")))
        self.assertIn("103_a.jpg", rap["eksik"])
        self.assertFalse(os.path.exists(z)); self.assertTrue(glob.glob(os.path.join(kok, "GELENLER", "_ISLENDI", "*.zip")))
        self.assertEqual(gemini_al.al(kok, "gorsel")[0], 2)            # ZIP yok → kullanıcı işi


class Duzeltme(unittest.TestCase):
    def test_sablon_ve_kucuk_duzeltme(self):
        c = duzeltme.cumle("nesne_el", nesne="lit lantern", ad="Mara", EL="RIGHT", iyelik="her", OBUR_EL="LEFT", el_sekli_en="empty, fingers relaxed")
        self.assertEqual(c, "CORRECTION: the lit lantern is in Mara's RIGHT hand; her LEFT hand is empty, fingers relaxed.")
        with self.assertRaises(duzeltme.DuzeltmeHatasi): duzeltme.cumle("bakis", ad="Mara", yon="left x right", hedef="door")
        with self.assertRaises(duzeltme.DuzeltmeHatasi): duzeltme.cumle("nesne_el", nesne="x")
        self.assertEqual(duzeltme.istem_kur("Base. CORRECTION: old one.", {"agiz": "CORRECTION: new."}), "Base. CORRECTION: new.")
        kok = F.film_kur("DZ")
        p = os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "101_a.jpg"); F._jpg(p)
        plan = {"no": 101, "_derlenir": {"ayna_yasak": True}}
        sk = duzeltme.sifir_kredi(kok, plan, "a", "kadraj_sirasi")
        self.assertTrue(sk["denendi"]); self.assertIn("ayna_yasak", sk["gerekce"]); self.assertNotIn("yeni_aday", sk)
        plan["_derlenir"]["ayna_yasak"] = False
        sk = duzeltme.sifir_kredi(kok, plan, "a", "kadraj_sirasi"); self.assertEqual(sk["yeni_aday"], "101_a1.jpg")
        sk = duzeltme.sifir_kredi(kok, plan, "a", "kadraj_sirasi"); self.assertNotIn("yeni_aday", sk)   # ikinci kez uygulanmaz
        sk = duzeltme.sifir_kredi(kok, plan, "a", "kimlik"); self.assertTrue(sk["denendi"]); self.assertTrue(sk["gerekce"])


class Kapak(unittest.TestCase):
    def _aday(self, kok, n):
        for i in range(1, n + 1): F._jpg(os.path.join(kok, "YAYIN", "_KAPAK_ADAYLAR", "kapak_%02d.jpg" % i), (i * 20, 90, 120))

    def test_secim_ve_final(self):
        F.evren_kur(); kok = F.film_kur("KP")
        kod, spec = idg.derle_kapak(kok)
        self.assertEqual(len(spec), 10); self.assertTrue(all(not k["yasak"] for k in spec))
        self._aday(kok, 8); kapak.kor_paketi(kok, 1); kor.sahte_cevaplar(kok, "kapak", 1)
        an = kor.anahtar_oku(kok, "kapak", 1)["gruplar"]["1"]
        g = {v["anahtar"]: k[:-4] for k, v in an.items()}
        ciftler = ortak.json_oku(os.path.join(kok, "_KOR_PAKET", "kapak_t1", "SEYIRCI", "CIFTLER.json"))["ciftler"]
        self.assertEqual(len(ciftler), 28)
        hedef = g["kapak_03"]
        ortak.atomik_yaz(os.path.join(kok, "_RAPOR", "KAPAK", "seyirci_t1.json"),
                         {"ciftler": [dict(c, secim="a" if c["a"] == hedef else "b" if c["b"] == hedef else "a") for c in ciftler]})
        kod, r = kapak.sec(kok, 1)
        self.assertEqual(r["kazanan"], "kapak_03")
        self.assertTrue(os.path.isfile(os.path.join(kok, "_RAPOR", "KAPAK_t1.json")))
        kod, out = kapak.final(kok)
        from PIL import Image
        self.assertEqual(Image.open(os.path.join(kok, out[0])).size, (1280, 720))

    def test_az_aday_hata(self):
        kok = F.film_kur("KP2"); self._aday(kok, 5); kapak.kor_paketi(kok, 1)
        kod, r = kapak.sec(kok, 1)
        self.assertEqual(r["sonuc"], "HATA")
        self.assertTrue(any(h["madde"] == "kapak_aday_sayisi" for h in r["hatalar"]))


if __name__ == "__main__":
    unittest.main()
