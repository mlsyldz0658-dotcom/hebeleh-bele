"""İzin testleri — Gemini API kısmı (TASARIM §6.10 test_izinler, D-19, D-41, [SON] K-3, O-10): sahte Gemini: anahtar var + usd_tavan_film 0 →
dinleyici çağrılır; anahtar yok → "ölçülemedi" + bilgi paketi; ücretli katman yalnız izin + dolar tavanıyla; Ö0-e ses/video girişi yoksa kapalı;
kota → Kisitlandi(kota); ikinci göz kullanıcıya paket olarak verilmez; FILM_AYAR'daki güvenlik sınırı (SFace 0,363) sıkılaştırır, gevşetmez.
Flow kilidi + Vertex kuralı test_izinler_video.py'dedir (adım 15)."""
import os, sys, json, glob, wave, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401
import _gorsel_fikstur as F
import ortak, kapi, esikler
from saglayicilar import Kisitlandi
from saglayicilar import gemini_api as ga

AYAR = os.path.join(_ortam.VERI, "AYARLAR")
O0E = os.path.join(_ortam.VERI, "BILGI", "OLCUM0", "O0e.json")


class Tasiyici:
    def __init__(self, durum=200, govde=None):
        self.cagri = []; self.durum = durum
        self.govde = govde or {"candidates": [{"content": {"parts": [{"text": json.dumps({"cevaplar": [{"soru": "metalik", "cevap": "hayir"}]})}]}}]}

    def __call__(self, yontem, url, veri, basliklar, zaman_asimi=180):
        self.cagri.append({"url": url, "basliklar": basliklar, "bayt": len(veri or b"")})
        return self.durum, json.dumps(self.govde).encode(), {}


def wav(yol):
    with wave.open(yol, "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000); w.writeframes(b"\0\0" * 800)
    return yol


class Izinler(unittest.TestCase):
    def setUp(self):
        self.eski = os.environ.pop("GEMINI_API_KEY", None)
        for p in (os.path.join(AYAR, "FILM_AYAR.json"), O0E):
            if os.path.exists(p): os.replace(p, p + ".onceki")
        self.assertFalse(os.path.exists(os.path.join(AYAR, "gemini_anahtar.txt")))

    def tearDown(self):
        os.environ.pop("GEMINI_API_KEY", None)
        if self.eski is not None: os.environ["GEMINI_API_KEY"] = self.eski

    def ayar(self, usd=0, ucretli=False):
        ortak.atomik_yaz(os.path.join(AYAR, "FILM_AYAR.json"), {"_surum": 3, "butce": {"usd_tavan_film": usd},
                                                                 "izinler": {"gemini_api_ucretli": ucretli}})

    def test_anahtar_var_usd_sifir_dinleyici_cagrilir(self):
        os.environ["GEMINI_API_KEY"] = "test-anahtari-gizli"; self.ayar(0)
        self.assertEqual(ga.izin_karari("dinleyici"), (True, "ucretsiz"))
        t = Tasiyici(); s = ga.GeminiAPI(tasiyici=t)
        r = s.dinle(wav(os.path.join(_ortam.KOK, "d.wav")), "listen")
        self.assertEqual(len(t.cagri), 1)
        self.assertEqual(r["cevaplar"][0]["soru"], "metalik")
        self.assertNotIn("test-anahtari-gizli", t.cagri[0]["url"])            # anahtar URL'de değil, yalnız başlıkta
        self.assertEqual(t.cagri[0]["basliklar"]["x-goog-api-key"], "test-anahtari-gizli")
        kayit = open(os.path.join(_ortam.VERI, "HESAP", "GEMINI_KULLANIM.jsonl"), encoding="utf-8").read()
        self.assertNotIn("test-anahtari-gizli", kayit)

    def test_anahtar_yok_olculemedi_ve_bilgi_paketi(self):
        self.ayar(0)
        acik, neden = ga.izin_karari("dinleyici")
        self.assertFalse(acik); self.assertIn("ölçülemedi", neden)
        m = ga.olculemedi_kaydi("dinleyici", neden)
        self.assertEqual(m["seviye"], "OLCULEMEDI"); self.assertTrue(m["bilgi_paketi"])
        self.assertEqual(kapi.madde_sonucu(m["seviye"]), "BAYRAK")
        t = Tasiyici()
        with self.assertRaises(Kisitlandi) as c: ga.GeminiAPI(tasiyici=t).dinle(wav(os.path.join(_ortam.KOK, "d2.wav")), "x")
        self.assertTrue(c.exception.gecilebilir); self.assertEqual(t.cagri, [])

    def test_ucretli_katman_yalniz_izin_ve_dolar_tavaniyla(self):
        os.environ["GEMINI_API_KEY"] = "k"; ortak.atomik_yaz(O0E, {"gemini_katman": "ucretli"})
        self.ayar(0, ucretli=True); self.assertFalse(ga.izin_karari("izleyici")[0])
        self.ayar(5, ucretli=False); self.assertFalse(ga.izin_karari("izleyici")[0])
        self.ayar(5, ucretli=True); self.assertTrue(ga.izin_karari("izleyici")[0])

    def test_o0e_ses_video_girisi_yok(self):
        os.environ["GEMINI_API_KEY"] = "k"; self.ayar(0)
        ortak.atomik_yaz(O0E, {"gemini_katman": "ucretsiz", "ses_girisi": False, "video_girisi": False})
        self.assertFalse(ga.izin_karari("dinleyici")[0]); self.assertFalse(ga.izin_karari("izleyici")[0])
        self.assertTrue(ga.izin_karari("gozlemci")[0])
        self.assertFalse(ga.izin_karari("gorsel")[0])                          # görsel ayrıca Ö0-e gorsel_uygun ister

    def test_kota_ve_filtre(self):
        os.environ["GEMINI_API_KEY"] = "k"; self.ayar(0)
        g = os.path.join(_ortam.KOK, "g.jpg"); F._jpg(g)
        with self.assertRaises(Kisitlandi) as c: ga.GeminiAPI(tasiyici=Tasiyici(429)).gozlem([g], "x")
        self.assertEqual(c.exception.kod, "kota")
        with self.assertRaises(Kisitlandi) as c:
            ga.GeminiAPI(tasiyici=Tasiyici(200, {"candidates": [{"finishReason": "SAFETY"}]})).gozlem([g], "x")
        self.assertEqual(c.exception.kod, "filtre_red"); self.assertFalse(c.exception.gecilebilir)

    def test_ikinci_goz_kullaniciya_paket_degil(self):
        import gemini_paket
        self.ayar(0)
        kok = F.film_kur("IZ")
        once = set(glob.glob(os.path.join(F.y["gemini_paket"], "*")))
        kod, r = gemini_paket.ikinci_goz(kok, 1)
        self.assertEqual(kod, 0)
        self.assertEqual(set(glob.glob(os.path.join(F.y["gemini_paket"], "*"))), once)
        self.assertEqual(r["ozet"]["olculemedi"], 0 if r["sonuc"] == "GEC" else r["ozet"]["olculemedi"])
        self.assertNotEqual(r["sonuc"], "GEC")

    def test_film_ayar_guvenlik_siniri_gevsetmez(self):
        import olcum
        E = esikler.yukle(ayar={"g1_kimlik_hata": 0.2})
        self.assertEqual(E["g1_kimlik_hata"], 0.363)
        self.assertTrue(E.bayraklar)
        E = esikler.yukle(ayar={"g1_kimlik_hata": 0.5})
        self.assertEqual(E["g1_kimlik_hata"], 0.5)
        olcum._E.clear(); olcum._E["g1_kimlik_hata"] = 0.1; olcum._E["_kaynak"] = "test"
        self.assertEqual(olcum.esik("g1_kimlik_hata"), 0.363)
        olcum._E.clear()


if __name__ == "__main__":
    unittest.main()
