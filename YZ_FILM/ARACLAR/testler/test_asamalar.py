"""Aşama kaydı testi (TASARIM §1.3, §1.5, §6.1 hat/asamalar.py, §6.10): her kapıda tavan_sonrasi dolu, her girdinin
üreticisi var (önceki aşama ya da dış kaynak), ajan·kip ve kapı adları ad sözlüğünde, 6 KAPI yalnız merdivenin sonunda.
Ağ yok, kredi yok."""
import os, sys, json, io, contextlib, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401
from hat import asamalar as HAT
import film

ADLAR = json.load(open(os.path.join(ARACLAR, "veri", "ADLAR.json"), encoding="utf-8"))


class Asamalar(unittest.TestCase):
    def test_kayit_tutarli(self):
        self.assertEqual(HAT.denetle(ADLAR), [])

    def test_adlar_ile_ayni_asamalar(self):
        self.assertEqual([a.kod for a in HAT.ASAMALAR], list(ADLAR["asamalar"]))

    def test_her_asamada_tavan_sonrasi_ve_ureten(self):
        for a in HAT.ASAMALAR:
            self.assertTrue(a.tavan_sonrasi, a.kod)
            for g in a.girdiler: self.assertTrue(g.ureten, f"{a.kod}: {g.ad}")

    def test_bos_tavan_sonrasi_ve_ureticisiz_girdi_hata(self):
        a = HAT.ASAMALAR[1]
        bozuk = (HAT.ASAMALAR[0], a.__class__(**dict(a.__dict__, tavan_sonrasi=())),
                 a.__class__(**dict(a.__dict__, kod="A02", girdiler=(HAT.G("x", ""), HAT.G("y", "A18")))))
        eski, edizin = HAT.ASAMALAR, HAT._DIZIN
        try:
            HAT.ASAMALAR = bozuk; HAT._DIZIN = {x.kod: x for x in bozuk}
            h = HAT.denetle()
        finally: HAT.ASAMALAR, HAT._DIZIN = eski, edizin
        self.assertTrue(any("tavan_sonrasi boş" in x for x in h), h)
        self.assertTrue(any("üreteni yok" in x for x in h), h)
        self.assertTrue(any("sonraki aşama" in x or "bilinmiyor" in x for x in h), h)

    def test_alti_kapi_yalniz_merdivenin_sonunda(self):
        for a in HAT.ASAMALAR:
            for b in a.tavan_sonrasi[:-1]: self.assertNotIn(b.tur, ("kapi6", "kagit_urun"), a.kod)

    def test_kredili_asamalar_kagit_kapilarindan_sonra(self):
        sira = [a.kod for a in HAT.ASAMALAR]
        ilk_kredili = min(sira.index(a.kod) for a in HAT.ASAMALAR if a.kredi)
        self.assertGreater(ilk_kredili, sira.index("A09"))
        self.assertLess(sira.index("A12"), sira.index("A14a")); self.assertLess(sira.index("A14a"), sira.index("A14"))

    def test_imza_kendi_ve_sonraki_ciktilari_disarida(self):
        self.assertNotIn("SAHNELER.json", film.imza_dosyalari(HAT.asama("A08")))   # A09 SAHNELER'e yazar
        self.assertIn("_HIKAYE_ODASI/01_KONU_KARTI.json", film.imza_dosyalari(HAT.asama("A02")))
        self.assertNotIn("00_KONU.md", film.imza_dosyalari(HAT.asama("A00")))

    def test_markdown_ve_komut(self):
        md = HAT.markdown()
        for a in HAT.ASAMALAR: self.assertIn(f"| {a.kod}", md)
        b = io.StringIO()
        with contextlib.redirect_stdout(b): self.assertEqual(film.main(["asamalar", "--md"]), 0)
        self.assertIn("A14a", b.getvalue())
        b = io.StringIO()
        with contextlib.redirect_stdout(b): self.assertEqual(film.main(["asamalar", "--json"]), 0)
        self.assertEqual(len(json.loads(b.getvalue())), len(HAT.ASAMALAR))


class BirlestirmeKaydi(unittest.TestCase):
    """TUM_ISTEKLER hat/asamalar.py maddeleri: sıra, girdiler, çıktılar (görev kodu → grup)."""
    def gs(self, kod): return {(s.kod, s.turda): s for s in HAT.asama(kod).gorevler}

    def sira(self, kod): return [(s.kod, s.grup) for s in HAT.asama(kod).gorevler]

    def test_a01_butce_ve_evren_ozeti_yapimcidan_once(self):
        g = dict(self.sira("A01"))
        self.assertLess(max(g["B0"], g["EO"], g["BB"]), g["YK"]); self.assertLess(g["YK"], g["KD"])
        yk = next(s for s in HAT.asama("A01").gorevler if s.kod == "YK")
        for x in ("_HIKAYE_ODASI/butce_bilgisi.json", "_HIKAYE_ODASI/EVREN_OZETI.md", "_RAPOR/BUT0_FILM.json"): self.assertIn(x, yk.girdi)

    def test_a03_logline_x_mimarindan_once(self):
        g = dict(self.sira("A03")); self.assertEqual((g["HM"], g["LG"], g["HX"], g["OD"]), (0, 1, 2, 3))
        self.assertIn("_HIKAYE_ODASI/02_LOGLINELAR.md", next(s for s in HAT.asama("A03").gorevler if s.kod == "HX").girdi)

    def test_a04_juri_onerileri_gorur(self):
        for s in HAT.asama("A04").gorevler:
            if s.kod in ("JU", "UJ"): self.assertEqual(len([x for x in s.girdi if "Oneri_" in x]), 4)

    def test_a06_revizyon_senaryo_bulgu_yonlendirme(self):
        a = HAT.asama("A06"); s = {x.kod: x for x in a.gorevler}
        self.assertEqual(s["RV"].cikti, ("CIKTI/senaryo.json", "CIKTI/rapor.json"))
        self.assertIn(("CIKTI/senaryo.json", "_HIKAYE_ODASI/06_SENARYO_v{tur100}.json"), s["RV"].tasima)
        self.assertEqual((s["OB"].ajan, s["OB"].kip, s["OB"].adet), ("ozet-eslestirici", "bulgu", 3))
        self.assertLess(s["ST"].grup, s["BY"].grup); self.assertLess(s["BY"].grup, s["DV"].grup)
        # revizyon sürümü A05'in v<N>'iyle çakışmaz ve A06'nın kendi girdi imzasını (06_SENARYO_v1) dışarıda bırakmaz
        self.assertIn("_HIKAYE_ODASI/06_SENARYO_v1.json", film.imza_dosyalari(a))
        self.assertTrue(film.fnmatch.fnmatch("_HIKAYE_ODASI/06_SENARYO_v102.json", film._desen("_HIKAYE_ODASI/06_SENARYO_v{tur100}.json")))

    def test_seyirci_turu_kor_girdileri(self):
        for kod in ("A06", "A07e", "A12", "A14a", "A16"):
            s = {x.kod: x for x in HAT.asama(kod).gorevler}
            self.assertTrue(s["IK"].girdi[0].startswith("_KOR_PAKET/") and s["IK"].girdi[0].endswith("_ilk2dk_t{tur}/"), kod)
            self.assertTrue(any(x.endswith("ESLESTIRICI/ANAHTAR.json") for x in s["OE"].girdi), kod)
            self.assertIn("s{i}_rapor.json", " ".join(s["OE"].girdi))
            self.assertEqual(s["ST"].arac, "seyirci_topla.py")

    def test_a07_dilim_kart_istegi_ve_z0(self):
        g = dict(self.sira("A07a")); self.assertEqual(g["DL"], 0); self.assertLess(g["KR"], g["YH"]); self.assertLess(g["YH"], g["KT"])
        yh = next(s for s in HAT.asama("A07a").gorevler if s.kod == "YH")
        self.assertIn("_YONETMEN/DILIM/P{i}.json", yh.girdi); self.assertIn("CIKTI/KART_ISTEGI.json", dict(yh.tasima))
        self.assertIn("_YONETMEN/DILIM/G{i}.json", next(s for s in HAT.asama("A07b").gorevler if s.kod == "YP").girdi)
        c = {x.kod: x for x in HAT.asama("A07c").gorevler}
        self.assertEqual((c["KT"].argumanlar, c["PT"].argumanlar, c["PT"].kapi), (("--tum",), ("--tum",), "Z0"))
        self.assertIn("_RAPOR/ZAMAN_T0.json", c["ZC"].cikti)

    def test_a11_hakem_kapidan_once(self):
        s = {x.kod: x for x in HAT.asama("A11").gorevler}
        self.assertIsNone(s["KK"].kapi); self.assertEqual(s["KH"].kapi, "G1")
        self.assertLess(s["KK"].grup, s["RF"].grup); self.assertLess(s["RF"].grup, s["KH"].grup)
        self.assertEqual((s["RF"].ajan, s["RF"].kip), ("sureklilik-denetcisi", "hakem"))
        self.assertEqual(s["KG"].girdi, ("_KOR_PAKET/g1_t{tur}/{i}/",))

    def test_a12_sirasi(self):
        bek = [("KD", 0), ("KU", 1), ("SA", 2), ("ZT", 3), ("MU", 3), ("SK", 4), ("SM", 5), ("KR", 6), ("KK", 7), ("KS", 8), ("KM", 9),
               ("KP", 10), ("HS", 11), ("IK", 11), ("OE", 12), ("ST", 13), ("BP", 14)]
        self.assertEqual(self.sira("A12"), bek)
        s = {x.kod: x for x in HAT.asama("A12").gorevler}
        self.assertEqual([s[k].turda for k in ("KK", "KS", "KM")], ["ilk"] * 3); self.assertEqual(s["KU"].turda, "sonra")
        self.assertEqual(s["KS"].girdi, ("_KOR_PAKET/kesici_t{tur}/",))

    def test_a14_flow_reddi_onarimi_ve_video_komutu(self):
        for kod in ("A14a", "A14"):
            s = {x.kod: x for x in HAT.asama(kod).gorevler}
            self.assertEqual((s["FO"].ajan, s["FO"].kip, s["FO"].kosul), ("yonetmen", "onarim", "flow_filtre_red"))
            self.assertEqual(s["VG"].komut[:2], ("film.py", "video"))
        self.assertEqual(HAT.asama("A14a").gorevler[-1].argumanlar, ("--bilgi-paketi", "--kip", "kesit"))

    def test_a15_a16_a17(self):
        self.assertIn("--donustur", next(s for s in HAT.asama("A15").gorevler if s.kod == "SD").argumanlar)
        g = dict(self.sira("A16"))
        self.assertEqual(g["MY"], g["SK"]); self.assertLess(g["DU"], g["KZ"]); self.assertLess(g["KZ"], g["KK"])
        self.assertLess(g["KM"], g["KP"]); self.assertLess(g["ST"], g["RC"]); self.assertEqual(g["RC"], g["BY"]); self.assertLess(g["BY"], g["CC"])
        y = {x.kod: x for x in HAT.asama("A17").gorevler}
        self.assertLess(y["PT"].grup, y["YP"].grup); self.assertIn("YAYIN/PAKET_TASLAK.json", y["YP"].girdi)

    def test_kosul_denetimi(self):
        a = HAT.asama("A14"); s = a.gorevler[0]
        bozuk = a.__class__(**dict(a.__dict__, gorevler=a.gorevler + (s.__class__(**dict(s.__dict__, kod="ZZ", kosul="uydurma")),)))
        eski, edizin = HAT.ASAMALAR, HAT._DIZIN
        try:
            HAT.ASAMALAR = tuple(bozuk if x.kod == "A14" else x for x in eski); HAT._DIZIN = {x.kod: x for x in HAT.ASAMALAR}
            self.assertTrue(any("bilinmeyen koşul" in x for x in HAT.denetle()))
        finally: HAT.ASAMALAR, HAT._DIZIN = eski, edizin


if __name__ == "__main__":
    unittest.main()
