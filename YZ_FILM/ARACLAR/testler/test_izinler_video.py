"""Flow kilitliyken Vertex kuralı (TASARIM D-03, D-41, [SON] O-15; §6.10 test_izinler'in video bölümü).
Otomatik geçiş yok: kilit + izin yok → Vertex çağrısı 0 ve blok 0 (7); kilit + izin + usd_tavan_film > 0 → Flow gönderimi 0, bloklar
veo_vertex ve her çağrı BUTK'dan; Memmet Vertex bloğunu göndermez; FILM_AYAR güvenlik sınırını gevşetemez. Ağ ve kredi yok."""
import os, sys, json, shutil, tempfile, unittest, io, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401
import ortak, blok_plani, flow_yuk, memmet, kredi
import _video_fikstur as VF
from saglayicilar import flow as flow_sg


class VertexKurali(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.kok = os.path.join(self.tmp, "FILM"); self.hesap = os.path.join(self.tmp, "HESAP")
        VF.film_kur(self.kok, [VF.plan(n) for n in (1, 2, 3)])

    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def kilit(self): flow_yuk.uyari_kaydet("FILM", "olağan dışı etkinlik", kok=self.hesap)

    def kur(self, ayar):
        with contextlib.redirect_stdout(io.StringIO()): return blok_plani.plan_kur(self.kok, ayar=ayar, hesap_kok=self.hesap)

    def test_kilitsiz_flow(self):
        BP, kod = self.kur({})
        self.assertEqual(kod, 0); self.assertTrue(BP["bloklar"]); self.assertTrue(all(b["saglayici"] == "flow" for b in BP["bloklar"]))

    def test_kilit_izin_yok_vertex_0_blok_0(self):
        self.kilit()
        for ayar in ({}, {"izinler": {"flow_kilitliyken_vertex": False}, "butce": {"usd_tavan_film": 50}},
                     {"izinler": {"flow_kilitliyken_vertex": True}}, {"izinler": {"flow_kilitliyken_vertex": True}, "butce": {"usd_tavan_film": 0}}):
            BP, kod = self.kur(ayar)
            self.assertEqual(kod, 7, ayar); self.assertEqual(BP["bloklar"], [], ayar)
            self.assertFalse(BP["flow_kilidi"]["vertex"])
            self.assertFalse(any(b.get("saglayici") == "veo_vertex" for b in BP["bloklar"]))

    def test_kilit_izin_ve_usd_vertex_planli_flow_0(self):
        self.kilit()
        BP, kod = self.kur({"izinler": {"flow_kilitliyken_vertex": True}, "butce": {"usd_tavan_film": 25}})
        self.assertEqual(kod, 0); self.assertTrue(BP["bloklar"])
        self.assertTrue(all(b["saglayici"] == "veo_vertex" and b["butk"] == "her_cagri" for b in BP["bloklar"]))
        with self.assertRaises(ValueError): blok_plani.blok_bul(self.kok, "sonraki")       # gönderilecek Flow bloğu yok
        # Memmet Vertex bloğunu Flow'a göndermez (kilit olmasa bile)
        os.rename(flow_yuk.kilit_yolu(self.hesap), flow_yuk.kilit_yolu(self.hesap) + ".eski")
        with mock.patch.object(memmet, "HESAP", self.hesap), contextlib.redirect_stdout(io.StringIO()):
            m = memmet.Memmet(self.kok, {"mod": "elle", "blok": BP["bloklar"][0]["id"], "onizleme": BP["onizleme_imza"]})
            with self.assertRaises(memmet.Durdur) as c: m.blok_dogrula()
        self.assertEqual(c.exception.kod, "ortam")
        self.assertFalse(any(s.get("olay") == "gonderim" for s in kredi.defter_oku(self.kok)[0]))

    def test_usd_harcamasi_yalniz_butk_ile(self):
        r, kod = kredi.butk(self.kok, "VX-1", 1.2, birim="usd", ayar={"butce": {"usd_tavan_film": 0}})
        self.assertEqual(kod, 5, "usd_tavan_film 0 → Vertex çağrısı bütçe noktasından geçemez")
        r, kod = kredi.butk(self.kok, "VX-2", 1.2, birim="usd", ayar={"butce": {"usd_tavan_film": 5}})
        self.assertEqual(kod, 0)

    def test_kisit_kodlari_saglayici_degistirmez(self):
        for rc in (7, 2, 4, 8, 9):
            self.assertFalse(flow_sg.cikis_cevir(rc).gecilebilir, rc)
        self.assertEqual(memmet.CIKIS["olagandisi"], 7); self.assertEqual(memmet.CIKIS["kilitli"], 7)

    def test_film_ayar_guvenlik_sinirini_gevsetemez(self):
        import esikler
        E = esikler.yukle(ayar={"flow_tempo_1710": {"elle": {"gonderim_arasi_sn": [1, 2]}}})
        self.assertGreaterEqual(E["flow_tempo_1710"]["elle"]["gonderim_arasi_sn"][0], 6)
        a = memmet.sikilastir("elle", {"gonderim_arasi_sn": [1, 2], "ayni_anda": 9})
        self.assertEqual((a["gonderim_arasi_sn"], a["ayni_anda"]), ([6, 15], 2))


if __name__ == "__main__":
    unittest.main()
