"""test_son_tur_b — son tur temizlik maddeleri (B): tek ışık biçimi + çevirici, plan_kurgu'nun KURGU_DUZEN_T2'yi yeniden uygulaması,
video_hazir'in zincir/sha1 kabulü, aşama komutları, .bat'lar, şablon eşikleri ve küçük araç temizlikleri. Ağ ve kredi yok."""
import os, sys, json, io, glob, contextlib, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for p in (HERE, ARACLAR):
    if p not in sys.path: sys.path.insert(0, p)
import _ortam  # noqa: F401  (önce: geçici YOLLAR.json)
import ortak, kroki


def _j(*yol):
    with open(os.path.join(*yol), encoding="utf-8") as f: return json.load(f)


class IsikTekBicim(unittest.TestCase):
    """kroki _derlenir.isik_kadrajda'yı {rol: "<on|arka>_<sol|sag>"} yazar; tüketiciler kroki.isik_yonu ile çevirir."""
    def test_cevirici(self):
        self.assertEqual(kroki.isik_yonu({"ana": "on_sol", "dolgu": "arka_sag"}), "soldan")
        self.assertEqual(kroki.isik_yonu({"ana": "arka_sag"}), "sagdan")
        self.assertEqual(kroki.isik_yonu({"dolgu": "on_sol"}, "dolgu"), "soldan")
        self.assertEqual(kroki.isik_yonu("soldan"), "soldan")                  # eski düz dize aynen
        for bos in (None, {}, {"dolgu": "on_sol"}, "duz", 3): self.assertIsNone(kroki.isik_yonu(bos))

    def test_istem_derle_gorsel_zanaat(self):
        """istem_derle --gorsel ORNEK_3_SAHNE_ZANAAT'ta TypeError vermeden koşar; ana ışığın yönü istemde 'from frame left/right'."""
        import _zanaat as Z, plan_birlestir, istem_derle
        kok = Z.kopya("ZN_ISIK")
        self.assertEqual(Z.kos(plan_birlestir, "--film", kok)[0], 0)
        kod, _ = Z.kos(istem_derle, "--gorsel", "--film", kok)
        self.assertIn(kod, (0, 1))                 # 1 = evren kaydı yok (kimlik_dizesi_yok); çökme yok
        for p in _j(kok, "SAHNELER.json")["sahneler"]:
            isik = (p.get("_derlenir") or {}).get("isik_kadrajda")
            self.assertIsInstance(isik, dict)
            beklenen = {"soldan": "from frame left", "sagdan": "from frame right"}[kroki.isik_yonu(isik)]
            self.assertIn(beklenen, p.get("gorsel_istem") or "", p.get("no"))

    def test_duzeltme_ve_kare_denetim_ceviriciyi_kullanir(self):
        import duzeltme
        plan = {"no": 1, "_derlenir": {"isik_kadrajda": {"ana": "on_sag"}}, "zanaat": {"kadrajdakiler": []}}
        self.assertIn("right", duzeltme.madde_cumlesi({"alan": "isik"}, plan))
        plan["_derlenir"]["isik_kadrajda"] = {"ana": "arka_sol"}
        self.assertIn("left", duzeltme.madde_cumlesi({"alan": "isik"}, plan))
        for ad in ("duzeltme.py", "kare_denetim.py", "istem_derle_gorsel.py"):
            with open(os.path.join(ARACLAR, ad), encoding="utf-8") as f: m = f.read()
            self.assertIn("kroki.isik_yonu(der.get(\"isik_kadrajda\"))", m, ad)


class PlanKurguDuzenT2(unittest.TestCase):
    def test_diyalog_kaydir_ekran_disi_yeniden_kurulusta_kalir(self):
        import _kurgu_fikstur as F, kurgu_ortak as ko, plan_kurgu, ses_donustur_ana as sda, kurgu_uygula as ku
        kok = F.film_kur("SON_TUR_DUZEN"); A = ["--film", kok, "--saglayici", "sahte"]
        with contextlib.redirect_stdout(io.StringIO()): sda.main(A); plan_kurgu.main(A)
        d0 = {d["replik"]: d for d in ko.kurgu_plani(kok)[1]["diyalog"]}
        on = os.path.join(kok, "KURGU", "S3_ONERI_v1.json")
        ortak.atomik_yaz(on, {"asama": "T2", "islemler": [
            {"op": "diyalog_kaydir", "replik": "R0001", "sn": -0.208, "plan": 3, "kok_neden": "dudak_kayma", "bulgu": "S3.1"}]})
        self.assertEqual(ku.calistir(kok, "T2", 1, kararlar=on)[0], 0)
        ortak.atomik_yaz(os.path.join(kok, "KURGU", "SES_ISTEKLERI.json"),
                         {"islemler": [{"replik": "R0002", "op": "ekran_disi", "plan": 5, "kok_neden": "dudak_kayma"}]})
        self.assertEqual(ku.calistir(kok, "T2", 2)[0], 0)
        once = {d["replik"]: d for d in ko.kurgu_plani(kok)[1]["diyalog"]}
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(plan_kurgu.main(A), 0)       # T2 yeniden kurulur
        kp = ko.kurgu_plani(kok)[1]; d = {x["replik"]: x for x in kp["diyalog"]}
        self.assertAlmostEqual(d["R0001"]["cizelge_bas"], d0["R0001"]["cizelge_bas"] - 0.208, places=2)
        self.assertAlmostEqual(d["R0001"]["cizelge_bas"], once["R0001"]["cizelge_bas"], places=2)
        self.assertEqual((d["R0002"]["plan"], d["R0002"]["ekran_disi"]), (once["R0002"]["plan"], True))
        self.assertGreaterEqual(kp.get("duzen_uygulanan", 0), 1)
        self.assertFalse(kp.get("duzen_atlanan"), kp.get("duzen_atlanan"))
        with contextlib.redirect_stdout(io.StringIO()): plan_kurgu.main(A)                           # ikinci kez: katlanmaz
        d2 = {x["replik"]: x for x in ko.kurgu_plani(kok)[1]["diyalog"]}
        self.assertAlmostEqual(d2["R0001"]["cizelge_bas"], d["R0001"]["cizelge_bas"], places=3)


class VideoHazir(unittest.TestCase):
    def _film(self, plan):
        import tempfile, hashlib
        kok = tempfile.mkdtemp(dir=_ortam.VERI); os.makedirs(os.path.join(kok, "SIRALI_GORSEL"))
        y = os.path.join(kok, "SIRALI_GORSEL", "002.jpg")
        with open(y, "wb") as f: f.write(b"kare-002")
        with open(y, "rb") as f: sha = hashlib.sha1(f.read()).hexdigest()
        ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), {"sahneler": [dict(plan(sha), no=2)]})
        return kok, sha

    def test_g1_kisa_sha_onek(self):
        import kare_denetim as kd
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "GEC", "sha1": sha[:12]}}})
        self.assertEqual(kd.video_hazir(kok, 2), (True, ""))
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "GEC", "sha1": sha[:7]}}})      # < 8 hane: kabul yok
        self.assertFalse(kd.video_hazir(kok, 2)[0])
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "GEC", "sha1": "f" * 12}}})
        self.assertIn("SHA1", kd.video_hazir(kok, 2)[1])
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "BAYRAK", "sha1": sha}}})
        self.assertFalse(kd.video_hazir(kok, 2)[0])

    def test_zincir_g1z(self):
        import kare_denetim as kd
        zin = lambda sonuc, sha: {"uretim": {"zincir": {"yontem": "son_kare", "kaynak": 1, "kare_sha1": sha, "g1z": {"sonuc": sonuc, "sha1": sha}}}}
        kok, _ = self._film(lambda sha: zin("GEC", sha[:10]))                      # G1 kaydı yok; zincir G1Z GEÇ yeter
        self.assertEqual(kd.video_hazir(kok, 2), (True, ""))
        kok, _ = self._film(lambda sha: zin("BAYRAK", sha))
        self.assertFalse(kd.video_hazir(kok, 2)[0])
        kok, _ = self._film(lambda sha: zin("GEC", "0" * 12))                      # bayat zincir karesi
        self.assertFalse(kd.video_hazir(kok, 2)[0])

    def test_memmet_yedek_yolu_kalkti(self):
        with open(os.path.join(ARACLAR, "memmet.py"), encoding="utf-8") as f: m = f.read()
        govde = m[m.index("    def video_hazir(self"):m.index("    def kredi_once(")]
        self.assertNotIn("_sha_tutar", govde); self.assertNotIn("get(\"g1z\")", govde)


if __name__ == "__main__":
    unittest.main()
