"""Veri kökü emniyeti testi (PR-0, D-02): geçici bir "eski masaüstü YZ_FILM" kurar, emniyete alır;
yamasız Memmet'e giden giriş noktası 0 kalmalı, hiçbir dosya silinmemeli, OpenMontage'a dokunulmamalı."""
import os, sys, json, shutil, tempfile, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import veri_emniyet as ve

ESKI_DOSYALAR = {
    "ARACLAR/memmet.py": "print('eski memmet: uyarida 12 saat bekler')\n",
    "ARACLAR/_memmet_yedek_1710.py": "print('yedek')\n",
    "ARACLAR/memmet3.py": "print('memmet3')\n",
    "ARACLAR/film.py": "input('onay?')\n",
    "ARACLAR/kontrol.py": "print('kontrol kalir')\n",
    "FILMLER/B3/MEMMET_BASLAT.bat": '@echo off\r\npython "%~dp0..\\..\\ARACLAR\\memmet.py" "%~dp0."\r\n',
    "FILMLER/B3/FILM_HATTI.bat": '@echo off\r\npython "%~dp0..\\..\\ARACLAR\\film.py" "%~dp0."\r\n',
    "FILMLER/B3/KONTROL.bat": '@echo off\r\npython "%~dp0..\\..\\ARACLAR\\kontrol.py" "%~dp0."\r\n',
    "FILMLER/B3/_BOLUM3/_araclar/gece_video.ps1": "python ..\\ARACLAR\\MEMMET.py --mod gece\r\n",
    "FILMLER/B3/SAHNELER.json": "{}",
    "BASLA_BURADAN.txt": "eski anlatim\n", "00_BENI_OKU.txt": "eski\n", "KURULUM.bat": "@echo off\r\n", "YENI_FILM.bat": "set /p AD=\r\n",
    "OpenMontage/run.bat": "python memmet.py\r\n",
    "GELISTIRME/memmet3/memmet.py": "print('gelistirme kopyasi')\n",
}


class VeriEmniyet(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.veri = os.path.join(self.tmp, "YZ_FILM")
        for rel, icerik in ESKI_DOSYALAR.items():
            p = os.path.join(self.veri, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "w", encoding="utf-8", newline="").write(icerik)

    def tearDown(self): shutil.rmtree(self.tmp, ignore_errors=True)

    def dosyalar(self):
        out = set()
        for k, _, fs in os.walk(self.veri):
            for f in fs: out.add(os.path.relpath(os.path.join(k, f), self.veri).replace("\\", "/"))
        return out

    def test_giris_noktasi_sifir_silinen_yok(self):
        r = ve.veri_emniyet(self.veri, sessiz=True)
        self.assertEqual(r["durum"], "temiz"); self.assertEqual(r["kalan_giris_noktasi"], [])
        tasinan = {t["dosya"].replace("\\", "/") for t in r["tasinan"]}
        beklenen = {"ARACLAR/memmet.py", "ARACLAR/_memmet_yedek_1710.py", "ARACLAR/memmet3.py", "ARACLAR/film.py",
                    "FILMLER/B3/MEMMET_BASLAT.bat", "FILMLER/B3/FILM_HATTI.bat", "FILMLER/B3/_BOLUM3/_araclar/gece_video.ps1",
                    "BASLA_BURADAN.txt", "00_BENI_OKU.txt", "KURULUM.bat", "YENI_FILM.bat"}
        self.assertEqual(tasinan, beklenen)
        # hiçbir şey silinmedi: her eski dosyanın içeriği _ESKI altında aynen duruyor
        for t in r["tasinan"]:
            eski = open(os.path.join(self.veri, t["nereye"]), encoding="utf-8", newline="").read()
            self.assertEqual(eski, ESKI_DOSYALAR[t["dosya"].replace("\\", "/")])
        # dokunulmayanlar
        for rel in ("ARACLAR/kontrol.py", "FILMLER/B3/KONTROL.bat", "FILMLER/B3/SAHNELER.json", "OpenMontage/run.bat",
                    "GELISTIRME/memmet3/memmet.py"):
            self.assertEqual(open(os.path.join(self.veri, rel), encoding="utf-8", newline="").read(), ESKI_DOSYALAR[rel], rel)
        # yerine konanlar
        bat = open(os.path.join(self.veri, "FILMLER/B3/MEMMET_BASLAT.bat"), encoding="ascii").read()
        self.assertIn("emekli", bat); self.assertNotIn("memmet", bat.lower())
        self.assertIn("FILM_SETI.bat", open(os.path.join(self.veri, "CLAUDE.md"), encoding="utf-8").read())
        self.assertTrue(os.path.exists(os.path.join(self.veri, "_ESKI", "EMNIYET_RAPORU.json")))

    def test_sarmalayici_yamali_memmeti_cagirir(self):
        ve.veri_emniyet(self.veri, sessiz=True)
        s = os.path.join(self.veri, "ARACLAR", "memmet.py")
        self.assertIn(os.path.join(os.path.abspath(ARACLAR), "memmet.py"), open(s, encoding="utf-8").read())
        r = subprocess.run([sys.executable, s], capture_output=True, text=True, encoding="utf-8", timeout=60)
        self.assertEqual(r.returncode, 0); self.assertIn("MEMMET AUTO", r.stdout)   # argümansız: depo Memmet'inin kullanım metni

    def test_tekrar_calistirmak_guvenli(self):
        ve.veri_emniyet(self.veri, sessiz=True); once = self.dosyalar()
        r = ve.veri_emniyet(self.veri, sessiz=True)
        self.assertEqual((r["tasinan"], r["durum"]), ([], "temiz"))
        self.assertEqual(self.dosyalar() - {"_ESKI/EMNIYET_RAPORU.json"}, once - {"_ESKI/EMNIYET_RAPORU.json"})

    def test_veri_yoksa_bir_sey_yapmaz(self):
        self.assertEqual(ve.veri_emniyet(os.path.join(self.tmp, "YOK"), sessiz=True)["durum"], "veri_yok")

    def test_depo_klasoru_veri_sayilmaz(self):
        with self.assertRaises(SystemExit): ve.veri_emniyet(os.path.dirname(ARACLAR), sessiz=True)


if __name__ == "__main__":
    unittest.main()
