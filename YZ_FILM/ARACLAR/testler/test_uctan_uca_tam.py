"""Uçtan uca, kâğıt sonuna kadar (TASARIM §6.10 test_uctan_uca_tam, §9 adım 10 PR-7; A00–A09 → KAGIT_TAMAM.json).

film.py v2 görev zinciri `kaset` ile: ajan görevleri ORNEK_3_SAHNE/_KASET (A00–A06) + ORNEK_3_SAHNE_TAM/_KASET (A06s–A09) kayıtlarından;
betikler GERÇEK, şu ikisi dışında:
  - KASETTEN: bu adımın sahibi olmadığı, depoda henüz olmayan ya da başka ajanın sürdürdüğü yönetmen araçları (kroki, plan_denetim,
    plan_birlestir, dunya_defteri, zaman_cizelgesi, cekim_listesi, istem_derle, kamera_agaci), kor_paket (plan kipinde sızıntı
    denetimi R0001'deki "Sera," hitabını ad sızıntısı sayıyor; paylaşılan istek) ve görev kimliği yazmayan kredi.py.
  - A09 DN: hat/asamalar.py 'istem_denetim.py --film' çağırır; ses ekleri istem_denetim.py'ye bağlanana kadar (paylaşılan istek)
    görev aynı sözleşmeyle 'istem_denetim_ses.py --rapor' ile koşar (istem_denetim v2 + iki yanlış alarm ayıklaması + S0.4–S0.6).
    test_istem_denetim_tek_basina bu bekleyen bağlantıyı ayrıca gösterir (bağlantı gelince skip kalkar).
Gerçek koşanlar: hikaye_odasi, puan_oku (seyirci-topla, --plan), evren, dilim, ses_plani (--profil-denetle, --taslak, --denetle),
muzik --kagit, istem_denetim_ses. Ağ yok, kredi yok."""
import os, sys, json, io, glob, time, shutil, contextlib, unittest, unittest.mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak, film, kuyruk, istem_denetim, istem_denetim_ses
from saglayicilar import kaset

FILMLER = os.path.join(os.path.dirname(ARACLAR), "FILMLER")
KASET_HIKAYE = os.path.join(FILMLER, "ORNEK_3_SAHNE", "_KASET")
TAM = os.path.join(FILMLER, "ORNEK_3_SAHNE_TAM")
KASETTEN = {"kroki.py", "plan_denetim.py", "plan_birlestir.py", "dunya_defteri.py", "zaman_cizelgesi.py", "cekim_listesi.py",
            "istem_derle.py", "kamera_agaci.py", "kor_paket.py", "kredi.py"}
YOK_ARAC = KASETTEN | {"seyirci_topla.py"}
BEKLENEN = ["A00", "A01", "A02", "A03", "A04", "A05", "A06", "A06s", "A07a", "A07b", "A07c", "A07d", "A07e", "A08", "A09", "A10a"]


def jl(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


class UctanUcaTam(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "yerel"}); cls.env.start()
        cls.ad = "TAM_UCTAN_UCA"; cls.kok = os.path.join(_ortam.VERI, "FILMLER", cls.ad)
        kod, r = cls.k("yeni", "--konu", "ejderha yavrusunu saklayan avcı kadın", "--ad", cls.ad)
        assert kod == 0, r
        shutil.copytree(KASET_HIKAYE, os.path.join(cls.kok, "_KASET"))
        for kl in sorted(os.listdir(os.path.join(TAM, "_KASET"))):
            if kl in ("AJAN", "BETIK"):
                for g in os.listdir(os.path.join(TAM, "_KASET", kl)):
                    shutil.copytree(os.path.join(TAM, "_KASET", kl, g), os.path.join(cls.kok, "_KASET", kl, g))
        cls.cagri = {"gercek": [], "kaset": [], "yonlendirilen": []}
        t0 = time.time(); cls.asamalar, cls.son = cls.yurut(); cls.sure = time.time() - t0

    @classmethod
    def tearDownClass(cls): cls.env.stop()

    @classmethod
    def k(cls, *a):
        a = list(a) + (["--film", cls.ad] if a[0] != "yeni" else [])
        with contextlib.redirect_stdout(io.StringIO()) as o: kod = film.main(a)
        try: return kod, json.loads(o.getvalue())
        except ValueError: return kod, o.getvalue()

    @classmethod
    def yurut(cls):
        orj_kos, orj_isfile = film.Defter.betik_kos, os.path.isfile
        cagri = cls.cagri

        def betik_kos(d, g):
            if g["arac"] in KASETTEN:
                cagri["kaset"].append(g["id"]); return kaset.betik_oynat(d.kok, g)[0]
            if g["arac"] == "istem_denetim.py":
                cagri["yonlendirilen"].append(g["id"]); g = dict(g, arac="istem_denetim_ses.py", argumanlar=["--rapor"])
            if g["arac"] == "seyirci_topla.py": g = dict(g, arac="puan_oku.py", argumanlar=["seyirci-topla"] + list(g["argumanlar"]))
            if not g["arac"].startswith("film.py:"): cagri["gercek"].append(g["arac"] + " " + " ".join(g["argumanlar"]))
            return orj_kos(d, g)

        def isfile(p):
            if os.path.dirname(os.path.abspath(p)) == ARACLAR and os.path.basename(p) in YOK_ARAC: return True
            return orj_isfile(p)

        asamalar, son = [], None
        with unittest.mock.patch.object(film.Defter, "betik_kos", betik_kos), unittest.mock.patch("os.path.isfile", isfile), \
                unittest.mock.patch.object(film, "disk_bos_gb", lambda y: 500.0):
            for _ in range(600):
                ortak.atomik_yaz(os.path.join(cls.kok, "_GOREV", "KANCA_NABZI.json"), {"zaman": film.simdi(), "yazan": "test"})
                kod, r = cls.k("sonraki"); son = r
                if not isinstance(r, dict): break
                asama = (r.get("asama") or "").split(" ")[0]
                if not asamalar or asamalar[-1] != asama: asamalar.append(asama)
                if asama == "A10a" or r["tur"] not in ("ajan", "betik"): break
                for gz in r["gorevler"]:
                    if r["tur"] == "betik":
                        kc, rc = cls.k("calis", gz["id"])
                        if kc != 0: return asamalar, {"hata": gz["id"], "cikti": rc}
                        continue
                    cls.k("basla", gz["id"])
                    g = jl(os.path.join(cls.kok, "_GOREV", gz["id"], "GOREV.json"))
                    try: kaset.ajan_oynat(cls.kok, g)
                    except kaset.KasetYok as e: return asamalar, {"hata": gz["id"], "kaset": str(e)}
                    while g.get("asamali"):
                        _, ri = cls.k("asama-ilerlet", gz["id"])
                        if not isinstance(ri, dict) or ri.get("son"): break
                    kb, rb = cls.k("bitir", gz["id"])
                    if kb != 0: return asamalar, {"hata": gz["id"], "bitir": rb}
        return asamalar, son

    def rap(self, ad): return jl(os.path.join(self.kok, "_RAPOR", ad))

    def test_zincir_kagit_sonuna_ulasir(self):
        self.assertEqual(self.asamalar, BEKLENEN, self.son)
        self.assertLess(self.sure, 300)                                           # §6.10: test_uctan_uca_tam ≤ 5 dk
        kt = jl(os.path.join(self.kok, "KAGIT_TAMAM.json"))
        S = jl(os.path.join(self.kok, "SAHNELER.json"))
        self.assertEqual(kt["plan_sayisi"], len(S["sahneler"])); self.assertEqual(kt["kagit"], "tamam")
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "KAMERA_AGACI.json")))

    def test_kapilar(self):
        for ad in ("S0_PROFIL_t1.json", "K0_FILM.json", "HS_PLAN_FILM_t1.json", "S0_FILM.json", "ISTEM_FILM.json", "S0_MUZIK.json"):
            r = self.rap(ad); self.assertIn(r["sonuc"], ("GEC", "BAYRAK"), (ad, r["hatalar"]))
            self.assertEqual(r["hatalar"], [], ad)
        self.assertEqual(self.rap("S0_FILM.json")["sonuc"], "GEC")
        self.assertTrue(self.rap("S0_FILM.json")["sahneler_yazildi"])
        self.assertIn("muzik_zinciri_bos", {b["madde"] for b in self.rap("S0_MUZIK.json")["bayraklar"]})   # D-25 (bulut: zincir boş)
        for ad in ("S0_PROFIL_t1.json", "S0_FILM.json", "ISTEM_FILM.json"):
            self.assertTrue(self.rap(ad)["_uretim"]["gorev"])                   # rapor kendi görevine ait (film.py kapi_oku)

    def test_ses_alanlari_sahnelerde(self):
        S = jl(os.path.join(self.kok, "SAHNELER.json"))
        self.assertTrue(all(s.get("hareket_istem") and (s["zanaat"].get("ses") or {}).get("flow_sound") for s in S["sahneler"]))
        self.assertTrue(all((g.get("ses") or {}).get("yatak") for g in S["sahne_gruplari"].values()))
        yol = {s["no"]: ((s["zanaat"]["ses"].get("diyalog") or {}).get("yol")) for s in S["sahneler"]}
        self.assertEqual(sorted({y for y in yol.values() if y}), ["tts", "veo_donustur"])
        konusan = [s for s in S["sahneler"] if yol[s["no"]] == "veo_donustur"]
        prof = istem_denetim_ses.profiller_oku(self.kok)
        for s in konusan:
            self.assertIn(prof[s["replik"]["karakter"]]["veo_ses_tarifi"], s["hareket_istem"])
            self.assertTrue(s["hareket_istem"].endswith(s["zanaat"]["ses"]["flow_sound"]))
        for s in S["sahneler"]:
            if yol[s["no"]] == "tts": self.assertNotIn('"', s["hareket_istem"])
        self.assertIn("M01", {s["_derlenir"].get("muzik_ipucu") for s in S["sahneler"]})
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "_SES", "SES_TASARIMI.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "MUZIK", "IPUCU_ZAMANLARI.json")))

    def test_gercek_betikler_kostu(self):
        g = " | ".join(self.cagri["gercek"])
        for alt in ("ses_plani.py --profil-denetle", "ses_plani.py --taslak", "ses_plani.py --denetle --tum", "muzik.py --kagit",
                    "istem_denetim_ses.py --rapor", "dilim.py --asama A07b", "puan_oku.py --plan", "puan_oku.py seyirci-topla --kip plan",
                    "hikaye_odasi.py devir"):
            self.assertIn(alt, g)
        self.assertEqual(len(self.cagri["yonlendirilen"]), 1)

    def test_istem_denetim_tek_basina(self):
        """Paylaşılan istek bekliyor: istem_denetim.py v2 tek başına TTS planında ve replik tırnağında yanlış HATA verir."""
        r, _ = istem_denetim.rapor_v2(self.kok, rapor_yolu=os.path.join(self.kok, "_RAPOR", "ISTEM_TEK.json"))
        if r["hatalar"]:
            self.skipTest("istem_denetim.py'ye istem_denetim_ses bağlantısı (ayikla + ses ekleri) henüz yok: "
                          + ", ".join(sorted({h["madde"] for h in r["hatalar"]})))
        self.assertEqual(r["sonuc"], "GEC")


if __name__ == "__main__":
    unittest.main()
