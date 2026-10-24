"""V1 (kalite_denetim --klip) ve SC1 (ses_donustur --hizala) — her indirmede koşan kapılar (TASARIM §7.2 V1, [SM2] S2.1–S2.6, D-31).
Sahte klipler ffmpeg lavfi ile üretilir (ffmpeg yoksa V1 testleri atlanır); ASR kaset dosyasından. Ağ ve kredi yok."""
import os, sys, json, shutil, tempfile, unittest, io, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401
import ortak, kapi, kalite_denetim, ses_donustur
import _video_fikstur as VF


def kunye(kok, no):
    ortak.atomik_yaz(os.path.join(kok, "KUNYE", f"{no:03d}.json"), {"_surum": 1, "plan": no, "is": f"V-{no}-d1-abc123", "kapilar": {}})


class V1(unittest.TestCase):
    def setUp(self):
        if not VF.ffmpeg_var(): self.skipTest("ffmpeg yok")
        self.tmp = tempfile.mkdtemp(); self.kok = os.path.join(self.tmp, "FILM")
        VF.film_kur(self.kok, [VF.plan(n) for n in range(1, 7)])

    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def klip(self, no, **k):
        VF.klip_yaz(os.path.join(self.kok, "SIRALI_VIDEO", f"{no:03d}.mp4"), **k); kunye(self.kok, no)

    def olcumler(self, r, no):
        return {m["madde"]: m for m in r["hatalar"] + r["bayraklar"] if m.get("plan") == no}

    def test_kapi_kusurlari_pencere_ve_kirp(self):
        self.klip(1)                                   # temiz
        self.klip(2, siyah=(3.0, 3.6))                 # kullanılan pencerede (0,5–6,5) siyah → HATA
        self.klip(3, siyah=(7.0, 7.6))                 # pencere dışında → kirp, madde yok
        self.klip(4, donma=(2.0, 4.0))                 # pencerede donma → HATA
        self.klip(5, sure=4.0)                         # kesik indirme → HATA (yeniden indirme önerisi)
        with contextlib.redirect_stdout(io.StringIO()): r = kalite_denetim.klip_denetle(self.kok, [1, 2, 3, 4, 5], blok="B01")
        self.assertEqual(kapi.dogrula(r), []); self.assertEqual(r["kapi"], "V1"); self.assertEqual(r["kapsam"], "B01")
        self.assertTrue(os.path.exists(os.path.join(self.kok, "_RAPOR", "V1_B01.json")))
        self.assertEqual(self.olcumler(r, 1), {})
        self.assertIn("siyah", self.olcumler(r, 2))
        self.assertEqual({k for k, m in self.olcumler(r, 3).items() if m["seviye"] == "HATA"}, set())
        k3 = json.load(open(os.path.join(self.kok, "KUNYE", "003.json"), encoding="utf-8"))["kapilar"]["V1"]
        self.assertEqual(k3["sonuc"], "GEC"); self.assertTrue(any(x["kusur"] == "siyah" for x in k3["kirp"]))
        self.assertIn("donma", self.olcumler(r, 4))
        self.assertIn("kesik_indirme", self.olcumler(r, 5)); self.assertIn("memmet_topla", self.olcumler(r, 5)["kesik_indirme"]["oneri"])
        self.assertEqual(r["sonuc"], "KISMI")
        q = {m["plan"] for m in r["kuyruk"]}
        self.assertEqual(q, {2, 4}, "kesik indirme ve pencere dışı kusur kuyruğa yeniden çekim açmaz")
        for m in r["kuyruk"]:
            self.assertEqual((m["kaynak_kapi"] if "kaynak_kapi" in m else "V1", m["cozum"], m["tur"]), ("V1", "yeniden_cek", "video"))
            self.assertTrue(m["sifir_kredi"]["denendi"] and m["sifir_kredi"]["gerekce"])
        k2 = json.load(open(os.path.join(self.kok, "KUNYE", "002.json"), encoding="utf-8"))["kapilar"]["V1"]
        self.assertEqual(k2["sonuc"], "HATA")

    def test_kuyruk_maddeleri_kuyruk_py_kurallarindan_gecer(self):
        import kuyruk
        self.klip(2, siyah=(3.0, 3.6))
        with contextlib.redirect_stdout(io.StringIO()): kalite_denetim.klip_denetle(self.kok, [2], blok="B01")
        s = kuyruk.topla(self.kok)
        self.assertEqual(len(s["eklenen"]), 1, s); self.assertEqual(s["reddedilen"], [])

    def test_ffmpeg_yoksa_olculemedi_gec_degil(self):
        self.klip(1)
        with mock.patch.object(kalite_denetim.shutil, "which", lambda x: None), contextlib.redirect_stdout(io.StringIO()):
            r = kalite_denetim.klip_denetle(self.kok, [1], blok="B01")
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertTrue(r["bayraklar"][0].get("olculemedi"))

    def test_komut_satiri_blok(self):
        self.klip(1); self.klip(2)
        ortak.atomik_yaz(os.path.join(self.kok, "BLOK_PLANI.json"), {"bloklar": [{"id": "B01", "planlar": [1, 2]}]})
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(kalite_denetim.main(["--klip", "--blok", "B01", "--film", self.kok]), 0)
        self.assertEqual(json.load(open(os.path.join(self.kok, "_RAPOR", "V1_B01.json"), encoding="utf-8"))["ozet"]["plan"], 2)


class SC1(unittest.TestCase):
    """Metin kapısı: kaset ASR ile (gerçek motor yoksa ÖLÇÜLEMEDİ)."""
    REPLIK = {"id": "R0042", "karakter": "mara", "metin": "It's late, Captain Voss. What do you want?", "tasidigi": ["late"]}

    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.kok = os.path.join(self.tmp, "FILM")
        p = VF.plan(1, replik=dict(self.REPLIK)); p["_derlenir"] = {"replik_zaman": {"R0042": [2.0, 5.3]}}
        doc = VF.film_kur(self.kok, [p]); doc["karakterler"]["voss"] = {"ad": "Captain Voss"}; VF.sahneler_yaz(self.kok, doc)
        os.makedirs(os.path.join(self.kok, "SIRALI_VIDEO")); open(os.path.join(self.kok, "SIRALI_VIDEO", "001.mp4"), "wb").write(b"\0" * 100)
        kunye(self.kok, 1)

    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def kaset(self, metin, bas=2.1, hiz=2.5, konusan="mara"):
        kel = [{"w": w, "bas": round(bas + i / hiz, 2), "bit": round(bas + (i + 0.8) / hiz, 2)} for i, w in enumerate(metin.split())]
        ortak.atomik_yaz(os.path.join(self.kok, "_KASET", "SC1", "001.json"), {"kelimeler": kel, "konusan_yuz": konusan})

    def kos(self):
        with contextlib.redirect_stdout(io.StringIO()): r = ses_donustur.hizala(self.kok, [1], blok="B01")
        self.assertEqual(kapi.dogrula(r), [])
        return r, {m["madde"]: m for m in r["hatalar"] + r["bayraklar"]}

    def test_dogru_soz_gecer_ve_hizalama_yazilir(self):
        self.kaset("It's late Captain Voss what do you want")
        r, m = self.kos()
        self.assertEqual(r["sonuc"], "GEC", m)
        h = json.load(open(os.path.join(self.kok, "SESLER", "hizalama", "001.json"), encoding="utf-8"))
        self.assertEqual(h["wer"], 0.0); self.assertEqual(h["replik"], "R0042")
        self.assertEqual(json.load(open(os.path.join(self.kok, "KUNYE", "001.json"), encoding="utf-8"))["kapilar"]["SC1"]["sonuc"], "GEC")
        self.assertTrue(os.path.exists(os.path.join(self.kok, "_RAPOR", "S2m_B01.json")))

    def test_konusma_yok_S2_1_hata_ve_kuyruk(self):
        self.kaset("It's late Captain Voss", bas=7.5)              # pencere (1,0–6,3) dışında
        r, m = self.kos()
        self.assertEqual(m["S2.1"]["seviye"], "HATA"); self.assertEqual(r["kuyruk"][0]["kok_neden"], "veo_konusmadi")

    def test_gri_bant_replik_kabul_ust_bant_hata(self):
        self.kaset("It's late Captain Voss what do want")            # 1/8 = 0,125 → gri
        r, m = self.kos(); self.assertEqual(m["S2.2"]["seviye"], "BAYRAK"); self.assertIn("replik_kabul", m["S2.2"]["oneri"])
        self.kaset("Go away now please")                             # çok saptı + ad ve tasidigi yok
        r, m = self.kos()
        self.assertEqual(m["S2.2"]["seviye"], "HATA"); self.assertEqual(m["S2.3"]["seviye"], "HATA"); self.assertEqual(m["S2.4"]["seviye"], "BAYRAK")

    def test_dinleyen_konustu_S2_5(self):
        self.kaset("It's late Captain Voss what do you want", konusan="voss")
        r, m = self.kos(); self.assertEqual(m["S2.5"]["seviye"], "HATA")

    def test_motor_yoksa_olculemedi(self):
        with mock.patch.object(ses_donustur, "_asr_gercek", side_effect=ses_donustur.Olculemedi("ASR yok")), \
                mock.patch.object(ses_donustur, "ayristir", return_value=("x.wav", False)):
            r, m = self.kos()
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertTrue(m["SC1"].get("olculemedi"))

    def test_wer_normallestirme(self):
        self.assertEqual(ses_donustur.wer("It's 2 o'clock!", "its two oclock"), 0.0)
        self.assertEqual(ses_donustur.wer("a b c d", "a x c"), 0.5)


if __name__ == "__main__":
    unittest.main()
