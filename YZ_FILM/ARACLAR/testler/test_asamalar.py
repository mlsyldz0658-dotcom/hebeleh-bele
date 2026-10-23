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


if __name__ == "__main__":
    unittest.main()
