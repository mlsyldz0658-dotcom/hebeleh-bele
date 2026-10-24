"""Zincir ve blok planı (PR-11): kare_zinciri --cikar + G1Z, blok_plani uygunluk/bloklar/kesit/pilot, video_denetim V2/V3
(hareketli kutu videosu; TASARIM D-15, D-17, §7.2 G1Z/V2/V3). ffmpeg yoksa klip isteyen testler atlanır. Ağ ve kredi yok."""
import os, sys, json, shutil, tempfile, unittest, io, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401
import ortak, kapi, blok_plani, kare_zinciri, video_denetim, kredi
import _video_fikstur as VF


def kunye(kok, no, gecen=("V1", "V2", "V3")):
    ortak.atomik_yaz(os.path.join(kok, "KUNYE", f"{no:03d}.json"),
                     {"_surum": 1, "plan": no, "is": f"V-{no}-d1-aaaaaa", "kapilar": {g: {"sonuc": "GEC"} for g in gecen}})


class Zincir(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.kok = os.path.join(self.tmp, "FILM"); self.hesap = os.path.join(self.tmp, "HESAP")
        adim = [{"id": "a1", "bas": 1.0, "bit": 3.0, "ozne": "mara", "tur": "fiziksel", "fiil": "yurur"}]
        self.doc = VF.film_kur(self.kok, [VF.plan(1, adimlar=adim),
                                          VF.plan(2, zincir={"yontem": "son_kare", "kaynak": 1, "derinlik": 1}),
                                          VF.plan(3, zincir={"yontem": "son_kare", "kaynak": 2, "derinlik": 2}),
                                          VF.plan(4)])

    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def sahneler(self): return {int(p["no"]): p for p in ortak.json_oku(os.path.join(self.kok, "SAHNELER.json"))["sahneler"]}

    def plan_kur(self, **k):
        with contextlib.redirect_stdout(io.StringIO()): return blok_plani.plan_kur(self.kok, hesap_kok=self.hesap, **k)

    # ---------------------------------------------------------------- blok planı
    def test_zincir_ardili_ayni_blokta_degil_bagimli_bekler(self):
        BP, kod = self.plan_kur()
        self.assertEqual(kod, 0)
        planli = [n for b in BP["bloklar"] for n in b["planlar"]]
        self.assertEqual(sorted(planli), [1, 4]); self.assertIn("2", BP["bagimli_bekleyen"]); self.assertIn("3", BP["bagimli_bekleyen"])
        self.assertTrue(all(b["saglayici"] == "flow" for b in BP["bloklar"]))
        self.assertEqual(BP["onizleme_imza"], blok_plani.onizleme_imza(self.kok))

    def test_blok_en_cok_20_ve_sahne_siniri(self):
        pl = [VF.plan(n, sahne=("S01" if n <= 18 else "S02")) for n in range(1, 46)]
        VF.film_kur(self.kok, pl)
        BP, _ = self.plan_kur()
        boy = [len(b["planlar"]) for b in BP["bloklar"]]
        self.assertTrue(all(x <= blok_plani.BLOK_MAX for x in boy)); self.assertEqual(sum(boy), 45)
        self.assertEqual(BP["bloklar"][0]["planlar"][-1], 18, "sahne sınırına 3 plandan yakın blok sınırda kesilir")
        self.assertEqual([b["id"] for b in BP["bloklar"]], ["B01", "B02", "B03"])

    def test_kritik_yeniden_cekim_once_ve_ayrinti(self):
        VF.klip_yaz(os.path.join(self.kok, "SIRALI_VIDEO", "004.mp4"), sure=1) if VF.ffmpeg_var() else \
            (os.makedirs(os.path.join(self.kok, "SIRALI_VIDEO"), exist_ok=True), open(os.path.join(self.kok, "SIRALI_VIDEO", "004.mp4"), "wb").write(b"0"))
        with mock.patch.object(blok_plani, "_kuyruk_videolari", lambda f: [{"id": "YU-V2-1-001", "plan": 4, "tur": "video", "seviye": "KRITIK",
                                                                            "dilim": "goruntu"}]):
            BP, _ = self.plan_kur()
        b = BP["bloklar"][0]
        self.assertEqual(b["planlar"][0], 4); self.assertEqual(b["ayrinti"]["4"]["madde"], "YU-V2-1-001")

    def test_soy_tavani_ve_toplanmamis_gonderim(self):
        for i in range(3):
            kredi.defter_ekle(self.kok, "gonderim", 12, plan=4, saglayici="flow", is_kimligi=f"V-4-d{i}-x", tur="video")
        ortak.atomik_yaz(os.path.join(self.kok, "MEMMET_DURUM.json"), {"isler": {f"V-4-d{i}-x": {"durum": "hata"} for i in range(3)}})
        ok, neden = blok_plani.uygun_mu(self.kok, self.sahneler()[4], self.sahneler(), "video")
        self.assertFalse(ok); self.assertIn("soy tavanı", neden)
        kredi.defter_ekle(self.kok, "gonderim", 12, plan=1, saglayici="flow", is_kimligi="V-1-d1-y", tur="video")
        ok, neden = blok_plani.uygun_mu(self.kok, self.sahneler()[1], self.sahneler(), "video")
        self.assertFalse(ok); self.assertIn("memmet_topla", neden)

    def test_bitti_isaretleri_ve_yeni_blokta_hepsi_eskiye(self):
        BP, _ = self.plan_kur()
        for b in BP["bloklar"]: blok_plani.bitti_isaretle(self.kok, b["id"])
        self.assertTrue(blok_plani.blok_bitti_mi(self.kok, "*"))
        VF.film_kur(self.kok, [VF.plan(n) for n in (1, 4, 5)])
        BP2, _ = self.plan_kur()
        self.assertFalse(blok_plani.blok_bitti_mi(self.kok, "*"), "yeni blok yazılınca BLOK_HEPSI işareti _ESKI'ye taşınır")
        self.assertTrue(os.listdir(os.path.join(self.kok, "_ESKI")))
        self.assertIn("B02", [b["id"] for b in BP2["bloklar"]], "blok numarası sürer, eski kimlik yeniden kullanılmaz")

    def test_kesin_butce_yoksa_hata(self):
        ortak.atomik_yaz(os.path.join(self.kok, "URETIM_ONIZLEME.json"), {"taslak": True, "butce": {}})
        with self.assertRaises(blok_plani.Hata): self.plan_kur()
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(blok_plani.main(["--imza", "--film", self.kok]), 1)

    def test_kesit_ve_kapsama_ve_pilot_karari(self):
        pl = []
        for n in range(1, 61):
            p = VF.plan(n, kadraj=2 if n % 5 == 0 else 1)
            if n % 7 == 0: p["replik"] = {"id": f"R{n}", "karakter": "mara", "metin": "Go."}
            p["_derlenir"] = {"sure_sn": 4.0}
            pl.append(p)
        VF.film_kur(self.kok, pl)
        BP, kod = self.plan_kur(kesit=True)
        kes = BP["kesit"]["planlar"]
        self.assertTrue(45 <= len(kes) <= 45 + blok_plani.KESIT_EK_MAX, len(kes))
        self.assertTrue(all(b["id"].startswith("KESIT-") and len(b["planlar"]) <= 20 for b in BP["bloklar"]))
        self.assertGreaterEqual(BP["kesit"]["kapsama"]["iki_kisi"], 4); self.assertIn("son_kare", BP["kesit"]["eksik"])
        with contextlib.redirect_stdout(io.StringIO()): r = blok_plani.pilot_karar(self.kok)
        self.assertEqual(kapi.dogrula(r), []); self.assertEqual(r["kapi"], "PILOT")
        self.assertEqual(r["kararlar"]["istem_bicimi"]["deger"], "aralik")
        self.assertIn("olculemedi", r["kararlar"]["istem_bicimi"]["kaynak"])
        self.assertNotEqual(r["sonuc"], "GEC", "ölçülemeyen karar GEÇ sayılmaz")

    # ---------------------------------------------------------------- kare zinciri (klip ister)
    def kaynak_klip(self, gecen=("V1", "V2", "V3")):
        if not VF.ffmpeg_var(): self.skipTest("ffmpeg yok")
        VF.klip_yaz(os.path.join(self.kok, "SIRALI_VIDEO", "001.mp4"), kutu=[(1.0, 3.0)])
        kunye(self.kok, 1, gecen)

    def test_cikar_kaynak_hazir_degilse_beklenir(self):
        self.kaynak_klip(gecen=("V1", "V2"))
        with contextlib.redirect_stdout(io.StringIO()): r = kare_zinciri.cikar(self.kok, [2])
        self.assertEqual(r["ozet"]["plan"], 0)
        self.assertFalse(os.path.exists(os.path.join(self.kok, "SIRALI_GORSEL", "_PLANLI", "002.jpg")))
        ok, neden = blok_plani.uygun_mu(self.kok, self.sahneler()[2], self.sahneler(), "video")
        self.assertFalse(ok); self.assertIn("V3", neden)

    def test_cikar_y55_penceresi_planli_gorsel_saklanir_g1z(self):
        self.kaynak_klip()
        planli_sha = VF.sha1(os.path.join(self.kok, "SIRALI_GORSEL", "002.jpg"))
        with contextlib.redirect_stdout(io.StringIO()): r = kare_zinciri.cikar(self.kok, [2])
        self.assertEqual(kapi.dogrula(r), [])
        self.assertTrue(os.path.exists(os.path.join(self.kok, "_RAPOR", "G1Z_FILM_t1.json")))
        self.assertEqual(VF.sha1(os.path.join(self.kok, "SIRALI_GORSEL", "_PLANLI", "002.jpg")), planli_sha, "planlı görsel silinmez")
        z = self.sahneler()[2]["uretim"]["zincir"]
        self.assertGreaterEqual(z["kesim_sn"], 3.0 + 0.2 - 1e-6); self.assertLessEqual(z["kesim_sn"], 7.5)
        self.assertEqual(z["kare_sha1"], VF.sha1(os.path.join(self.kok, "SIRALI_GORSEL", "002.jpg")))
        self.assertEqual(self.sahneler()[1]["uretim"]["zincir_cikis"]["kilit"], True)
        from PIL import Image
        self.assertEqual(Image.open(os.path.join(self.kok, "SIRALI_GORSEL", "002.jpg")).size, (320, 180), "doğal en-boy korunur")
        # kimlik ölçülemiyorsa G1Z GEÇ değildir → ardıl gönderilmez
        if z["g1z"]["sonuc"] != "GEC":
            ok, neden = blok_plani.uygun_mu(self.kok, self.sahneler()[2], self.sahneler(), "video"); self.assertFalse(ok)
        z["g1z"]["sonuc"] = "GEC"; doc = ortak.json_oku(os.path.join(self.kok, "SAHNELER.json"))
        doc["sahneler"][1]["uretim"]["zincir"] = z; VF.sahneler_yaz(self.kok, doc)
        ok, neden = blok_plani.uygun_mu(self.kok, self.sahneler()[2], self.sahneler(), "video"); self.assertTrue(ok, neden)
        ok, neden = blok_plani.uygun_mu(self.kok, self.sahneler()[2], self.sahneler(), "video", blok_nolar={1, 2}); self.assertFalse(ok)

    def test_derinlik_asilirsa_hata(self):
        self.kaynak_klip()
        doc = ortak.json_oku(os.path.join(self.kok, "SAHNELER.json"))
        doc["sahneler"][0]["uretim"]["zincir"] = {"yontem": "son_kare", "kaynak": 9, "derinlik": 2}; VF.sahneler_yaz(self.kok, doc)
        with contextlib.redirect_stdout(io.StringIO()): r = kare_zinciri.cikar(self.kok, [2])
        self.assertTrue(any(h["madde"] == "derinlik" for h in r["hatalar"]))

    # ---------------------------------------------------------------- V2 / V3 (hareketli kutu videosu)
    def test_v3_adim_tepesi_ve_bitis_tutmasi(self):
        if not VF.ffmpeg_var(): self.skipTest("ffmpeg yok")
        VF.klip_yaz(os.path.join(self.kok, "SIRALI_VIDEO", "001.mp4"), kutu=[(1.0, 3.0)]); kunye(self.kok, 1, ())
        VF.klip_yaz(os.path.join(self.kok, "SIRALI_VIDEO", "004.mp4"), kutu=[(4.5, 5.0), (6.5, 7.5)]); kunye(self.kok, 4, ())
        with contextlib.redirect_stdout(io.StringIO()): r2, r3 = video_denetim.klip_denetle(self.kok, [1, 4])
        self.assertEqual(kapi.dogrula(r2), []); self.assertEqual(kapi.dogrula(r3), [])
        self.assertTrue(os.path.exists(os.path.join(self.kok, "_RAPOR", "V2_FILM_t1.json")))
        m = {(x["plan"], x["madde"]): x for x in r3["hatalar"] + r3["bayraklar"]}
        self.assertNotIn((1, "adim_tepe"), m); self.assertNotIn((1, "bitis_tutma"), m)
        self.assertEqual(m[(4, "adim_tepe")]["seviye"], "BAYRAK", "adım penceresinde hareket yok, tepe kaydı")
        self.assertEqual(m[(4, "bitis_tutma")]["seviye"], "BAYRAK", "kesmeden önce hâlâ hareket var")
        self.assertTrue(m[(1, "bitis_olgulari")].get("olculemedi"), "kör gözlem yoksa ÖLÇÜLEMEDİ")
        self.assertTrue(os.path.exists(os.path.join(self.kok, "_RAPOR", "V3", "kareler", "001_kesme.jpg")))
        k = json.load(open(os.path.join(self.kok, "KUNYE", "001.json"), encoding="utf-8"))["kapilar"]
        self.assertEqual(k["V3"]["sonuc"], "BAYRAK", "ÖLÇÜLEMEDİ asla GEÇ değil: zincir ardılı bu kaynağa bağlanamaz")
        ortak.atomik_yaz(os.path.join(self.kok, "_RAPOR", "V3", "gozlem_t1_1.json"), {"planlar": {"1": {"bitis_olgulari": "HATA"}}})
        with contextlib.redirect_stdout(io.StringIO()): r2, r3 = video_denetim.klip_denetle(self.kok, [1])
        self.assertTrue(any(h["madde"] == "bitis_olgulari" and h["plan"] == 1 for h in r3["hatalar"]))

    def test_v2_kimlik_olculemezse_bayrak(self):
        if not VF.ffmpeg_var(): self.skipTest("ffmpeg yok")
        VF.klip_yaz(os.path.join(self.kok, "SIRALI_VIDEO", "001.mp4")); kunye(self.kok, 1, ())
        with mock.patch.object(video_denetim, "_kimlik", side_effect=video_denetim.Olculemedi("kimlik: opencv yok")), \
                mock.patch.object(video_denetim, "_gorunum", side_effect=video_denetim.Olculemedi("DINOv2 yok")), \
                contextlib.redirect_stdout(io.StringIO()):
            r2, _ = video_denetim.klip_denetle(self.kok, [1], blok="KESIT")
        self.assertEqual(r2["kapsam"], "KESIT"); self.assertEqual(r2["sonuc"], "BAYRAK")
        self.assertTrue(os.path.exists(os.path.join(self.kok, "_RAPOR", "V2_KESIT_t1.json")))

    def test_v2_yuz_sayisi_ve_kimlik_dususu(self):
        if not VF.ffmpeg_var(): self.skipTest("ffmpeg yok")
        VF.klip_yaz(os.path.join(self.kok, "SIRALI_VIDEO", "001.mp4"), sure=2); kunye(self.kok, 1, ())
        import numpy as np
        v = lambda a: np.array([a, 1 - a]) / np.linalg.norm([a, 1 - a])
        sayac = {"n": 0}
        class SahteKimlik:
            @staticmethod
            def yuzler(yol):
                if "SIRALI_GORSEL" in yol: return [{"vektor": v(1.0)}]
                sayac["n"] += 1
                return [{"vektor": v(1.0 if sayac["n"] < 3 else 0.2)}] + ([{"vektor": v(0.5)}] if sayac["n"] == 4 else [])
            @staticmethod
            def benzerlik(a, b): return float(np.dot(a, b))
        with mock.patch.object(video_denetim, "_kimlik", return_value=SahteKimlik), \
                mock.patch.object(video_denetim, "_gorunum", side_effect=video_denetim.Olculemedi("DINOv2 yok")), \
                contextlib.redirect_stdout(io.StringIO()):
            r2, _ = video_denetim.klip_denetle(self.kok, [1])
        h = {x["madde"]: x for x in r2["hatalar"]}
        self.assertIn("yuz_sayisi", h); self.assertIn("kimlik", h); self.assertEqual(h["kimlik"]["kok_neden"], "yuz_degisti")
        self.assertTrue(os.path.exists(os.path.join(self.kok, "_RAPOR", "V2_FILM", "001_yuz.jsonl")))
        self.assertEqual({m["kok_neden"] for m in r2["kuyruk"]}, {"fazla_kisi", "yuz_degisti"})


if __name__ == "__main__":
    unittest.main()
