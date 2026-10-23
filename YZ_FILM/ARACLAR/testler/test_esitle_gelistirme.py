"""esitle_gelistirme testi (PR-1, D-12): geçici bir git deposu ve geçici <veri>/GELISTIRME kurar.
Beyaz liste, anahtar taraması (çıkış 3, commit yok), kirli depo (4), yeni dal / açık dala dokunulmaması,
--push-yok, --kuru. Gerçek deponun git durumuna dokunmaz; ağ yok."""
import os, sys, shutil, tempfile, unittest, subprocess, io, contextlib
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR)
import esitle_gelistirme as eg

SAHTE_ANAHTAR = "f3a9c1d27b8e4f60a5d3c2b1e0f9a8b7c6d5e4f3"   # AYARLAR'daki "anahtar"
TELEGRAM = "1234567890:" + "A" * 20 + "b" * 15


def g(depo, *a):
    return subprocess.run(["git", "-C", depo, *a], capture_output=True, text=True, check=True).stdout.strip()


def yaz(kok, rel, icerik, kip="w"):
    p = os.path.join(kok, *rel.split("/")); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, kip, **({} if "b" in kip else {"encoding": "utf-8"})) as f: f.write(icerik)


class EsitleGelistirme(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.depo = os.path.join(self.tmp, "depo"); self.veri = os.path.join(self.tmp, "YZ_FILM")
        os.makedirs(self.depo)
        g(self.depo, "init", "-q", "-b", "ana")
        g(self.depo, "config", "user.name", "Test"); g(self.depo, "config", "user.email", "test@example.invalid")
        g(self.depo, "config", "commit.gpgsign", "false")
        yaz(self.depo, "README.md", "depo\n"); g(self.depo, "add", "."); g(self.depo, "commit", "-q", "-m", "ilk")
        self.ilk = g(self.depo, "rev-parse", "HEAD")
        yaz(self.veri, "AYARLAR/ai84_anahtar.txt", SAHTE_ANAHTAR + "\n")
        yaz(self.veri, "AYARLAR/OKU_BENI.txt", "Anahtarlar buraya yazilir ve asla paylasilmaz\n")
        G = "GELISTIRME/"
        yaz(self.veri, G + "memmet3/memmet.py", "import os\nKEY = os.environ.get('AI84_API_KEY')\napi_key = anahtar_oku()\nprint('memmet3')\n")
        yaz(self.veri, G + "memmet3/NOTLAR.md", "# notlar\nAnahtarlar buraya yazilir ve asla paylasilmaz\n")
        yaz(self.veri, G + "memmet3/CALISTIR.bat", "@echo off\r\npython memmet.py\r\n")
        yaz(self.veri, G + "kalibrasyon/B3_44.json", '{"kareler": []}\n')
        yaz(self.veri, G + "liste.txt", "bir\n")
        yaz(self.veri, G + "klip.mp4", b"\x00" * 10, "wb")
        yaz(self.veri, G + "kare.jpg", b"\xff\xd8", "wb")
        yaz(self.veri, G + "ses.wav", b"RIFF", "wb")
        yaz(self.veri, G + "buyuk.json", "x" * (eg.AZAMI_BOYUT + 1))
        yaz(self.veri, G + "AYARLAR/MEMMET_AYAR.json", "{}")
        yaz(self.veri, G + "memmet_profil/Default/Prefs.json", "{}")
        yaz(self.veri, G + "memmet3/__pycache__/memmet.cpython-310.pyc", b"\x00", "wb")
        yaz(self.veri, G + "telegram_token.txt", "bos\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def kos(self, *ek):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            kod = eg.main(["--veri", self.veri, "--depo", self.depo, *ek])
        return kod, out.getvalue()

    def dallar(self):
        return set(g(self.depo, "branch", "--format=%(refname:short)").split())

    def test_beyaz_liste_ve_yeni_dal(self):
        kod, out = self.kos("--push-yok", "--ad", "memmet3")
        self.assertEqual(kod, 0, out)
        # açık dal ve çalışma kopyası değişmedi
        self.assertEqual(g(self.depo, "symbolic-ref", "--short", "HEAD"), "ana")
        self.assertEqual(g(self.depo, "rev-parse", "HEAD"), self.ilk)
        self.assertEqual(g(self.depo, "status", "--porcelain"), "")
        yeni = [d for d in self.dallar() if d.startswith("yerel/memmet3-")]
        self.assertEqual(len(yeni), 1, self.dallar())
        dosyalar = set(g(self.depo, "ls-tree", "-r", "--name-only", yeni[0]).splitlines())
        self.assertEqual(dosyalar, {
            "README.md", "YZ_FILM/GELISTIRME/memmet3/memmet.py", "YZ_FILM/GELISTIRME/memmet3/NOTLAR.md",
            "YZ_FILM/GELISTIRME/memmet3/CALISTIR.bat", "YZ_FILM/GELISTIRME/liste.txt",
            "YZ_FILM/ARACLAR/veri/kalibrasyon/B3_44.json"})
        self.assertEqual(g(self.depo, "rev-parse", yeni[0] + "~1"), self.ilk)
        # push yok: uzak yok, iz bilgisi yok
        self.assertEqual(g(self.depo, "remote"), "")
        self.assertIn("push-yok", out)

    def test_anahtar_bulunursa_3_ve_commit_yok(self):
        yaz(self.veri, "GELISTIRME/memmet3/ayar.py", f"X = 1\nANAHTAR = '{SAHTE_ANAHTAR}'\n")
        yaz(self.veri, "GELISTIRME/not.md", f"bot: {TELEGRAM}\n")
        once = self.dallar()
        kod, out = self.kos("--push-yok")
        self.assertEqual(kod, 3, out)
        self.assertNotIn(SAHTE_ANAHTAR, out); self.assertNotIn(TELEGRAM, out)
        self.assertIn("memmet3/ayar.py, satır 2", out); self.assertIn("not.md, satır 1", out)
        self.assertEqual(self.dallar(), once)
        self.assertEqual(g(self.depo, "rev-parse", "HEAD"), self.ilk)
        self.assertEqual(g(self.depo, "status", "--porcelain"), "")

    def test_kaliplar(self):
        ornekler = ["k = 'AIza" + "B" * 35 + "'", "x = 'sk-ant-api03-abcdefghijk'", "-----BEGIN RSA PRIVATE KEY-----",
                    'set AI84_API_KEY=a1b2c3d4e5f6g7h8i9j0', '"xi-api-key": "0123456789abcdef0123456789abcdef"', TELEGRAM]
        for i, s in enumerate(ornekler):
            yaz(self.veri, f"GELISTIRME/k{i}.txt", s + "\n")
        bulgu = eg.tara(os.path.join(self.veri, "GELISTIRME"), [f"k{i}.txt" for i in range(len(ornekler))], set())
        self.assertEqual(sorted(r for r, _, _ in bulgu), sorted(f"k{i}.txt" for i in range(len(ornekler))))
        # kod satırları yanlış alarm vermez
        temiz = eg.tara(os.path.join(self.veri, "GELISTIRME"), ["memmet3/memmet.py", "memmet3/NOTLAR.md"],
                        eg.bilinen_anahtarlar([os.path.join(self.veri, "AYARLAR")]))
        self.assertEqual(temiz, [])

    def test_kirli_depo_4(self):
        yaz(self.depo, "README.md", "degisti\n")
        kod, out = self.kos("--push-yok")
        self.assertEqual(kod, 4, out)
        self.assertEqual(self.dallar(), {"ana"})

    def test_izlenmeyen_dosya_4(self):
        yaz(self.depo, "yeni.txt", "x\n")
        self.assertEqual(self.kos("--push-yok")[0], 4)

    def test_gelistirme_yok_ve_git_degil_4(self):
        shutil.rmtree(os.path.join(self.veri, "GELISTIRME"))
        self.assertEqual(self.kos()[0], 4)
        bos = os.path.join(self.tmp, "bos"); os.makedirs(bos)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(eg.main(["--veri", self.tmp, "--depo", bos]), 4)

    def test_kuru_hicbir_sey_degistirmez(self):
        kod, out = self.kos("--kuru")
        self.assertEqual(kod, 0, out)
        self.assertEqual(self.dallar(), {"ana"})
        self.assertEqual(g(self.depo, "status", "--porcelain"), "")
        self.assertIn("[kuru]", out)

    def test_push_yerel_uzaga(self):
        uzak = os.path.join(self.tmp, "uzak.git")
        subprocess.run(["git", "init", "-q", "--bare", uzak], check=True)
        g(self.depo, "remote", "add", "origin", uzak)
        kod, out = self.kos("--ad", "deneme")
        self.assertEqual(kod, 0, out)
        uzak_dallar = g(uzak, "branch", "--format=%(refname:short)").split()
        self.assertEqual(len(uzak_dallar), 1); self.assertTrue(uzak_dallar[0].startswith("yerel/deneme-"))
        self.assertNotIn("ana", uzak_dallar)

    def test_ikinci_calisma_yeni_dal_adi(self):
        self.assertEqual(self.kos("--push-yok")[0], 0)
        yaz(self.veri, "GELISTIRME/liste.txt", "iki\n")
        self.assertEqual(self.kos("--push-yok")[0], 0)
        self.assertEqual(len([d for d in self.dallar() if d.startswith("yerel/")]), 2)


if __name__ == "__main__":
    unittest.main()
