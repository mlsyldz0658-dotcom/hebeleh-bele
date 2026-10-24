"""yerel_is.py: ağır iş kuyruğu ve GPU kilidi (TASARIM §6.1; UM2 §4.5.15, T26). Gerçek işlem yok: sahte koşucu."""
import os, sys, json, shutil, tempfile, unittest, io, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401
import yerel_is


class Surec:
    """Popen benzeri: ilk poll'da hemen bitmez (eşzamanlılık sayılabilsin)."""
    acik = {"gpu": 0, "en_cok_gpu": 0}
    def __init__(self, cmd, rc=0, cikti=""):
        self.cmd, self.returncode_, self.cikti, self.n = cmd, rc, cikti, 0
        self.gpu = "--gpu-is" in " ".join(cmd)
        if self.gpu: Surec.acik["gpu"] += 1; Surec.acik["en_cok_gpu"] = max(Surec.acik["en_cok_gpu"], Surec.acik["gpu"])
        self.returncode = None
    def poll(self):
        self.n += 1
        if self.n < 2: return None
        if self.returncode is None:
            self.returncode = self.returncode_
            if self.gpu: Surec.acik["gpu"] -= 1
        return self.returncode
    def communicate(self): return (self.cikti, "")


class YerelIs(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.y = mock.patch.object(yerel_is, "klasor", lambda: self.tmp); self.y.start()
        Surec.acik.update(gpu=0, en_cok_gpu=0)

    def tearDown(self): self.y.stop(); shutil.rmtree(self.tmp, ignore_errors=True)

    def test_tek_gpu_isi_ve_oncelik(self):
        for i in range(3): yerel_is.ekle("F", f"video_denetim.py --klip {i} --gpu-is", gpu=True, oncelik=2, kimlik=f"G{i}")
        yerel_is.ekle("F", "kare_zinciri.py --cikar --gpu-is", gpu=True, oncelik=1, kimlik="Z")
        yerel_is.ekle("F", "ses_donustur.py --hizala", gpu=False, oncelik=3, kimlik="C")
        sira = []
        def kos(cmd): sira.append(os.path.basename(cmd[1])); return Surec(cmd)
        s = yerel_is.calis(kosucu=kos, bekle_sn=0)
        self.assertEqual(s["tamam"], 5); self.assertEqual(Surec.acik["en_cok_gpu"], 1, "aynı anda tek GPU işi")
        self.assertEqual(sira[0], "kare_zinciri.py", "blok arası zincir işi önce")
        self.assertFalse(os.path.exists(yerel_is.gpu_kilit_yolu()))

    def test_oom_bir_kez_yeniden_sonra_olculemedi_ve_ders(self):
        yerel_is.ekle("F", "video_denetim.py --klip 1 --gpu-is", gpu=True, kimlik="OOM")
        dersler = []
        with mock.patch("ders_defteri.kaydet", lambda *a, **k: dersler.append(k)):
            s = yerel_is.calis(kosucu=lambda cmd: Surec(cmd, 1, "RuntimeError: CUDA out of memory"), bekle_sn=0)
        j = yerel_is.isler()["OOM"]
        self.assertEqual((j["durum"], j["deneme"]), ("olculemedi", 2)); self.assertEqual(s["olculemedi"], 1)
        self.assertEqual(dersler[0]["kategori"], "gpu_bellek")

    def test_ortam_yoksa_olculemedi_ve_hata(self):
        yerel_is.ekle("F", "ses_donustur.py --donustur", ortam="musetalk", kimlik="M")
        yerel_is.ekle("F", "kalite_denetim.py --klip", kimlik="H")
        s = yerel_is.calis(kosucu=lambda cmd: Surec(cmd, 1, "beklenmeyen"), bekle_sn=0)
        I = yerel_is.isler()
        self.assertEqual(I["M"]["durum"], "olculemedi"); self.assertEqual(I["H"]["durum"], "hata"); self.assertEqual(s["hata"], 1)

    def test_gpu_kilidi_baska_surecteyse_bekler_ve_kesilen_is_yeniden(self):
        json.dump({"pid": os.getppid(), "is": "BASKA", "zaman": __import__("time").time()}, open(yerel_is.gpu_kilit_yolu(), "w"))
        yerel_is.ekle("F", "video_denetim.py --klip 1 --gpu-is", gpu=True, kimlik="G")
        s = yerel_is.calis(kosucu=lambda cmd: Surec(cmd), bekle_sn=0)
        self.assertTrue(s["gpu_mesgul"]); self.assertEqual(yerel_is.isler()["G"]["durum"], "bekliyor")
        os.remove(yerel_is.gpu_kilit_yolu())
        yerel_is._durum_yaz(yerel_is.isler()["G"], durum="calisiyor")          # kesilmiş
        s = yerel_is.calis(kosucu=lambda cmd: Surec(cmd), bekle_sn=0)
        self.assertEqual(yerel_is.isler()["G"]["durum"], "tamam")

    def test_ayni_is_iki_kez_eklenmez_ve_film_eklenir(self):
        a = yerel_is.ekle("/F", "video_denetim.py --klip 1"); b = yerel_is.ekle("/F", "video_denetim.py --klip 1")
        self.assertEqual(a["id"], b["id"]); self.assertEqual(len(yerel_is.isler()), 1)
        self.assertEqual(yerel_is._komut(a)[-2:], ["--film", "/F"])
        with self.assertRaises(ValueError): yerel_is.ekle("F", "rm -rf /")


if __name__ == "__main__":
    unittest.main()
