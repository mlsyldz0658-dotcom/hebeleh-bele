"""Uçtan uca TAM sahte deneme iskeleti (TASARIM §9 adım 17 kabul şartı "test_uctan_uca_tam A00–A18 sahte ≤ 5 dk", §6.10).

Üç katman:
  1. Hat: hat/asamalar.py'nin gerçek kaydıyla film.py v2 sahte kipte A00 → A18 (bulutta testi olmayan aşamalar atlanır);
     süre ≤ 5 dk, A00–A18'in bütün ana hat aşamaları "tamam", animatik imzası ONAYLI, A17/A18 kapı raporları yazıldı.
  2. Araç sözleşmesi: kayıttaki her betik görevinin aracı ARACLAR'da var mı? Eksikler (önceki adımların araçları) SEBEBİYLE atlanır.
  3. Bu dilimin araçları (A17, A18, A18a) gerçek olarak, film.py'nin çağırdığı biçimde ("<arac> <args> --film <film>",
     YZ_FILM_GOREV = görev klasörü) sahte hattın bıraktığı film klasöründe koşar: çıkış 0, bildirilen çıktılar ve kapı raporları
     geçerli zarfla yazılmış, rapor görevin kendisine ait. Sahte yer tutucu medyada ölçümler ÖLÇÜLEMEDİ (= BAYRAK) olmalı, asla GEÇ.
  ORNEK_3_SAHNE_TAM (adım 10) + kaset fikstürü gelince "tam" kip (bütün araçlar gerçek, sağlayıcılar kaset) bu dosyaya eklenir;
  fikstür yoksa o sınama sebebiyle atlanır.
Ağ yok, kredi yok, gerçek bekleme yok.
"""
import os, sys, json, time, glob, shutil, subprocess, unittest, unittest.mock, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak, kapi
import film
from hat import asamalar as HAT

SURE_MAX_SN = 300
BU_DILIM = ("A17", "A18", "A18a")
BU_DILIMIN_ARACLARI = ("kalite_denetim.py", "jenerik.py", "yayin_paketi.py", "shorts_mp4.py", "ders_derle.py", "evren.py", "yayin_analiz.py")
DEPO_FILMLER = os.path.join(os.path.dirname(ARACLAR), "FILMLER")


def calistir(*a):
    b = io.StringIO()
    with contextlib.redirect_stdout(b): kod = film.main(list(a))
    try: return kod, json.loads(b.getvalue())
    except ValueError: return kod, b.getvalue()


def oku(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


class UctanUcaTamSahte(unittest.TestCase):
    kok = None; sure = None

    @classmethod
    def setUpClass(cls):
        cls.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "bulut"}); cls.env.start()
        film._IMZA_DOSYA.clear()
        cls.ad = "T_UCTAN_UCA_TAM"
        shutil.rmtree(os.path.join(_ortam.VERI, "FILMLER", cls.ad), ignore_errors=True)
        kod, r = calistir("yeni", "--konu", "Ejderha yavrusunu saklayan avcı kadın", "--ad", cls.ad, "--saglayici", "sahte")
        assert kod == 0, r
        cls.kok = r["yol"]; t0 = time.time(); cls.son = None
        for _ in range(800):
            k, r = calistir("sonraki", "--film", cls.ad)
            if not isinstance(r, dict) or r.get("tur") == "bitti": cls.son = r; break
            if r.get("tur") not in ("ajan", "betik", "kullanici_eylemi"): cls.son = r; break
            for g in r["gorevler"]: calistir("calis", g["id"], "--film", cls.ad)
        cls.sure = time.time() - t0

    @classmethod
    def tearDownClass(cls):
        cls.env.stop(); film._IMZA_DOSYA.clear()

    # 1 ---------------------------------------------------------------------------------------------------------------
    def test_1_hat_a00_a18_sahte_bes_dakika(self):
        self.assertIsInstance(self.son, dict); self.assertEqual(self.son.get("tur"), "bitti", self.son)
        self.assertLessEqual(self.sure, SURE_MAX_SN, f"A00–A18 sahte {self.sure:.0f} sn > {SURE_MAX_SN} sn")
        st = oku(os.path.join(self.kok, "FILM_DURUM.json"))
        self.assertEqual(st["animatik"]["durum"], "ONAYLI")
        for a in HAT.ana_hat():
            self.assertIn(a.kod, st["asamalar"], a.kod)
            self.assertIn(st["asamalar"][a.kod]["durum"], ("tamam", "atlandi"), (a.kod, st["asamalar"][a.kod]))
        for a in ("A17", "A18"):
            for k in HAT.asama(a).kapilar:
                self.assertTrue(glob.glob(os.path.join(self.kok, film._desen(k.rapor).replace("*", "*"))), (a, k.rapor))

    # 2 ---------------------------------------------------------------------------------------------------------------
    def test_2_kayittaki_araclar(self):
        eksik = {}
        for a in HAT.ASAMALAR:
            for s in a.gorevler:
                if s.tur == "betik" and not s.arac.startswith("film.py:") and not os.path.isfile(os.path.join(ARACLAR, s.arac)):
                    eksik.setdefault(s.arac, []).append(a.kod)
        for s in (x for k in BU_DILIM for x in HAT.asama(k).gorevler if x.tur == "betik"):
            if s.arac in ("jenerik.py", "shorts_mp4.py", "yayin_paketi.py", "ders_derle.py", "yayin_analiz.py"):
                self.assertNotIn(s.arac, eksik, "bu dilimin aracı eksik")
        if eksik:
            self.skipTest("önceki adımların araçları henüz yok (tam kip bekler): "
                          + ", ".join(f"{k} ({'/'.join(sorted(set(v)))})" for k, v in sorted(eksik.items())))

    def test_2b_tam_kip_fikstur(self):
        p = os.path.join(DEPO_FILMLER, "ORNEK_3_SAHNE_TAM")
        if not os.path.isdir(p): self.skipTest("FILMLER/ORNEK_3_SAHNE_TAM (adım 10) + kaset fikstürü yok: tam kip sınanamaz")
        self.assertTrue(os.path.isfile(os.path.join(p, "HIKAYE.json")) or os.path.isfile(os.path.join(p, "SAHNELER.json")))

    # 3 ---------------------------------------------------------------------------------------------------------------
    def gorev_klasoru(self, a, s, tur_no=1):
        gd = os.path.join(self.kok, "_GOREV", f"TEST-{a.kod}-{s.kod}")
        kp = next((k for k in a.kapilar if k.kod == s.kapi), None)
        ortak.atomik_yaz(os.path.join(gd, "GOREV.json"), {"_surum": 2, "id": os.path.basename(gd), "asama": a.kod, "tur": "betik",
                                                          "tur_no": tur_no, "rapor": kp.rapor.replace("{tur}", str(tur_no)) if kp else None})
        return gd

    def test_3_bu_dilimin_araclari_film_py_bicimiyle(self):
        if "kalite_denetim.py" not in os.listdir(ARACLAR):
            yonlendir = {"kalite_denetim.py": "kalite_denetim_final.py"}       # bağlantı satırı gelene kadar
        else: yonlendir = {}
        yonlendir.update({"evren.py": "evren_film_sonu.py"} if not self._evren_bagli() else {})
        kosulan = []
        for kod in BU_DILIM:
            a = HAT.asama(kod)
            for s in a.gorevler:
                if s.tur != "betik" or s.arac not in BU_DILIMIN_ARACLARI: continue
                arac = yonlendir.get(s.arac, s.arac)
                if s.arac == "evren.py" and s.argumanlar[:1] not in (("--film-sonu",), ("--yedekle",)): continue
                p = os.path.join(ARACLAR, arac)
                if not os.path.isfile(p): continue
                gd = self.gorev_klasoru(a, s)
                env = dict(os.environ, YZ_FILM_GOREV=gd, YZ_FILM_FILM=self.kok)
                arg = [x.replace("{tur}", "1") for x in s.argumanlar] + ["--film", self.kok]
                if arac == "jenerik.py": arg += ["--boyut", "160x90", "--sure", "5"]
                r = subprocess.run([sys.executable, p] + arg, env=env, capture_output=True, text=True, timeout=120)
                if s.arac == "evren.py" and not glob.glob(os.path.join(ortak.yollar()["evren_kok"], "*", "evren.json")):
                    self.assertEqual(r.returncode, 1, r.stdout)          # sahte HIKAYE'de ön kayıt yok: açık HATA, sessiz geçiş yok
                    kosulan.append(f"{kod}/{s.kod} (evren yok → 1)"); continue
                self.assertEqual(r.returncode, 0, f"{kod}/{s.kod} {arac} {arg}: {r.stdout[-500:]} {r.stderr[-500:]}")
                for c in s.cikti:
                    c = c.replace("{tur}", "1")
                    self.assertTrue(os.path.exists(os.path.join(self.kok, c)), f"{kod}/{s.kod}: {c} yok")
                if s.kapi:
                    rp = oku(os.path.join(self.kok, next(k for k in a.kapilar if k.kod == s.kapi).rapor.replace("{tur}", "1")))
                    hatalar = [h for h in kapi.dogrula(rp) if not h.startswith("kapi bilinmiyor")]
                    self.assertEqual(hatalar, [], (kod, s.kod)); self.assertEqual(rp["_uretim"]["gorev"], os.path.basename(gd))
                    if s.kapi == "S8":                     # sahte yer tutucu medya: ölçülemedi = BAYRAK, asla GEÇ
                        self.assertNotEqual(rp["sonuc"], "GEC")
                kosulan.append(f"{kod}/{s.kod}")
        self.assertGreaterEqual(len(kosulan), 5, kosulan)

    def _evren_bagli(self):
        try:
            with open(os.path.join(ARACLAR, "evren.py"), encoding="utf-8") as f: return "evren_film_sonu" in f.read()
        except OSError: return False


if __name__ == "__main__":
    unittest.main()
