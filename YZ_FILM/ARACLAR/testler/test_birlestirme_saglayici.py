"""Birleştirme turu (sağlayıcı/kuyruk/kurulum dilimi): saglayicilar KAYIT ve TURLER, ai84.tts tohum ve komşu metin alanları.
Ağ ve kredi yok: ai84 isteği yamalanır, sağlayıcılar yalnız yüklenir (hazir() çağrılmaz)."""
import os, sys, json, unittest
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import saglayicilar as sg
import kapi


class Kayit(unittest.TestCase):
    def test_her_kayit_yuklenir_ve_turu_tanimli(self):
        for ad in sg.KAYIT:
            s = sg.yukle(ad)
            self.assertTrue(s.turler, ad)
        for ad in ("izleyici", "dinleyici", "sahte_izleyici", "sahte_dinleyici", "gemini_api", "ses_sahte", "faster_whisper",
                   "midi_ornek", "acestep", "kutuphane", "gemini_muzik_paketi", "openvoice", "chatterbox", "rvc", "roformer", "demucs",
                   "musetalk", "yz_buyutucu", "lanczos", "sahte_kurgu"):
            self.assertIn(ad, sg.KAYIT)
        for t in ("izleyici", "dinleyici", "tts", "asr", "ses_donustur"): self.assertIn(t, sg.TURLER)
        for t in ("gorsel", "video", "ses", "muzik"): self.assertIn(t, sg.TURLER)        # v1 hattı

    def test_faster_whisper_tek_sinif_ve_ai84_tts(self):
        self.assertEqual(sg.KAYIT["faster_whisper"], "saglayicilar.asr_whisper.FasterWhisper")
        a = sg.yukle("ai84")
        self.assertEqual(type(a).__name__, "AI84Tts"); self.assertIn("ses", a.turler); self.assertTrue(callable(a.ses))   # v1 ses()

    def test_dislanan_kayitta_yok(self):
        dis = set(kapi.adlar().get("saglayici_dislanan") or [])
        self.assertFalse(dis & set(sg.KAYIT), dis & set(sg.KAYIT))
        for yol in sg.KAYIT.values(): self.assertFalse(any(d.replace(".", "") in yol.lower() for d in dis), yol)

    def test_zincir_adlari_kayitta(self):
        """ADLAR saglayici_turleri'ndeki ve depoda sınıfı olan adlar KAYIT'ta (gelecek servisler hariç)."""
        gelecek = {"claude_code", "claude_api", "gemini_paket", "vertex_gorsel", "flow_gorsel", "veo_vertex", "sahte_bozuk", "ai84_vc",
                   "elevenlabs_muzik"}
        for tur, adlar in (kapi.adlar().get("saglayici_turleri") or {}).items():
            if tur.startswith("_"): continue
            for ad in adlar:
                if ad not in gelecek: self.assertIn(ad, sg.KAYIT, (tur, ad))


class AI84Tts(unittest.TestCase):
    def test_tohum_ve_komsu_metin_govdeye_girer(self):
        import ai84
        istekler = []
        def req(yontem, yol, govde=None, **k):
            istekler.append((yontem, yol, govde)); return {"job_id": "j1"}
        with mock.patch.object(ai84, "_req", req), mock.patch.object(ai84, "_poll", lambda *a, **k: {"audioUrl": "u", "credit_cost": 5}), \
                mock.patch.object(ai84, "_download", lambda *a: None):
            self.assertEqual(ai84.tts("Hello.", "v", "o.mp3", seed=42, previous_text="Before.", next_text="After."), 5)
            ai84.tts("Hello.", "v", "o.mp3")
        g1, g2 = istekler[0][2], istekler[1][2]
        self.assertEqual((g1["seed"], g1["previous_text"], g1["next_text"]), (42, "Before.", "After."))
        for k in ("seed", "previous_text", "next_text"): self.assertNotIn(k, g2)


if __name__ == "__main__":
    unittest.main()
