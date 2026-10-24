"""Adım 18 testleri (TASARIM §9 #18, §6.9, §8.1–8.5, §6.8 paketle, §6.10 CI): .bat takımı ADLAR ve §6.9 ile tam, kalan .bat
işlerinin güvenli davranışı, BASLA_BURADAN.txt sözleşme kartı == olcek.py çıktısı, kullanıcı rehberinin zorunlu içeriği, paketle
künyesi ve sızıntı taraması, CI iş akışı (geçerli YAML, doğru matris). Ağ ve kredi yok."""
import os, sys, io, re, json, zipfile, tempfile, unittest, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
YZ = os.path.dirname(ARACLAR); DEPO = os.path.dirname(YZ)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import ortak, esikler, olcek, bat_yenile, bat_isleri, kullanici_karti, paketle

TASARIM = os.path.join(DEPO, ".claude", "skills", "film-yap", "tartisma", "TASARIM.md")
BASLA = os.path.join(YZ, "BASLA_BURADAN.txt")
CI = os.path.join(DEPO, ".github", "workflows", "testler.yml")
try:
    import yaml
except ImportError:          # CI PyYAML kurar; yerelde yoksa yalnız YAML ayrıştırma testi atlanır
    yaml = None


def oku(p):
    with open(p, encoding="utf-8-sig") as f: return f.read()


def sessiz(fn, *a, **k):
    o = io.StringIO()
    with contextlib.redirect_stdout(o): r = fn(*a, **k)
    return r, o.getvalue()


def adlar_bat():
    return json.loads(oku(os.path.join(ARACLAR, "veri", "ADLAR.json")))["bat"]


def tasarim_69_batlari():
    """TASARIM §6.9 tablosunun depo kökü ve film klasörü satırlarındaki .bat adları."""
    m = oku(TASARIM); bol = m.split("### 6.9", 1)[1].split("### 6.10", 1)[0]
    out = {}
    for satir in bol.splitlines():
        for tur, im in (("depo", "| `.bat` (depo kökü)"), ("film", "| `.bat` (film klasörü)")):
            if satir.startswith(im): out[tur] = set(re.findall(r"`([A-Z0-9_]+\.bat)`", satir))
    return out


class BatTakimi(unittest.TestCase):
    def setUp(self):
        self.d = bat_yenile.depo_batlari(python="/usr/bin/python3", araclar="/x/ARACLAR", depo="/x")
        self.f = bat_yenile.film_batlari(python="/usr/bin/python3", araclar="/x/ARACLAR", depo="/x")

    def test_adlar_ile_tam(self):
        a = adlar_bat(); uretilen_depo = set(self.d) | set(bat_yenile.SABIT)
        self.assertEqual(set(self.d), set(bat_yenile.DEPO_KOKU)); self.assertEqual(set(self.f), set(bat_yenile.FILM_KLASORU))
        self.assertEqual(set(a["depo_koku"]) - uretilen_depo, set(), "ADLAR'daki depo kökü .bat'ı üretilmiyor")
        self.assertEqual(set(a["film_klasoru"]) - set(self.f), set(), "ADLAR'daki film klasörü .bat'ı üretilmiyor")
        self.assertEqual(set(self.d) - set(a["depo_koku"]) - set(a["film_klasoru"]), set(), "ADLAR'da olmayan depo .bat'ı")
        self.assertEqual(set(self.f) - set(a["film_klasoru"]), set(), "ADLAR'da olmayan film .bat'ı")
        self.assertEqual(set(a["emekli"]) & (set(self.d) | set(self.f)), set(), "emekli .bat üretiliyor")

    def test_tasarim_69_ile_tam(self):
        t = tasarim_69_batlari()
        self.assertTrue(t.get("depo") and t.get("film"), "§6.9 .bat satırları bulunamadı")
        self.assertEqual(t["depo"] - set(self.d) - set(bat_yenile.SABIT), set())
        self.assertEqual(t["film"] - set(self.f), set())

    def test_kurallar(self):
        for ad, m in list(self.d.items()) + list(self.f.items()):
            self.assertEqual(bat_yenile.denetle(m), [], ad); m.encode("ascii")
            self.assertTrue(m.endswith("\r\n")); self.assertNotIn("memmet", m.lower(), ad); self.assertNotIn("film.py", m, ad)
            self.assertIn(f'"{os.path.abspath("/usr/bin/python3")}" "' + os.path.join(os.path.abspath("/x/ARACLAR"), ""), m, ad)   # mutlak yol
        bek = {"TELEGRAM_TEST.bat": "bat_isleri.py\" telegram-test", "YOUTUBE_BAGLA.bat": "bat_isleri.py\" youtube-bagla"}
        for ad, b in bek.items(): self.assertIn(b, self.d[ad])
        bek = {"DURUM.bat": "bat_isleri.py\" durum", "VIDEO_GECE.bat": "bat_isleri.py\" video-gece",
               "ARSIVLE.bat": "arsivle.py\" --film", "YUKLE.bat": "bat_isleri.py\" yukle"}
        for ad, b in bek.items(): self.assertIn(b, self.f[ad]); self.assertIn('"%~dp0."', self.f[ad])

    def test_gitignore_uretilen_depo_batlari(self):
        g = oku(os.path.join(DEPO, ".gitignore")).splitlines()
        for ad in bat_yenile.DEPO_KOKU: self.assertIn("/" + ad, g, ad + " .gitignore'da yok (GUNCELLE yerel değişiklik görür)")


class KalanBatIsleri(unittest.TestCase):
    def setUp(self):
        sessiz(bat_isleri.izin_degistir, kapat=["gece_flow"])
        self.addCleanup(lambda: sessiz(bat_isleri.izin_degistir, kapat=["gece_flow"]))

    def gonderim_yok(self):
        hata = lambda *a, **k: self.fail("süreç başlatıldı: " + repr(a)[:200])
        return mock.patch.multiple(bat_isleri.subprocess, call=hata, run=hata, Popen=hata)

    def test_video_gece_izinsiz_ve_olcumsuz_acilmaz(self):
        with self.gonderim_yok():
            kod, out = sessiz(bat_isleri.video_gece, None)
            self.assertEqual(kod, bat_isleri.KULLANICI); self.assertIn("IZINLER.bat", out)
            bat_isleri.izin_degistir(ac=["gece_flow"])
            kod, out = sessiz(bat_isleri.video_gece, None)
            self.assertEqual(kod, bat_isleri.KULLANICI); self.assertIn("ölçülene kadar", out)
            with mock.patch.object(olcek, "kapasite", lambda E, o: (20, True, True, "test")):
                kod, out = sessiz(bat_isleri.video_gece, None)
            self.assertEqual(kod, bat_isleri.ORTAM); self.assertIn("VIDEO_YARI_OTOMATIK.bat", out)

    def test_p2_batlari_yalniz_bilgi(self):
        with self.gonderim_yok():
            for k in ("youtube-bagla", "yukle"):
                kod, out = sessiz(bat_isleri.main, [k, "/yok"])
                self.assertEqual(kod, bat_isleri.ORTAM); self.assertIn("henüz yok", out)

    def test_durum_salt_okunur_ozet(self):
        film = tempfile.mkdtemp(dir=_ortam.KOK); cagri = []

        def run(k, **kw):
            cagri.append(k); return mock.Mock(returncode=0, stdout=json.dumps({"ozet": "Film: X\nAşama: A07"}), stderr="")
        with mock.patch.object(bat_isleri.subprocess, "run", run):
            kod, out = sessiz(bat_isleri.durum, film)
        self.assertEqual(kod, 0); self.assertIn("Aşama: A07", out)
        self.assertEqual(cagri[0][1:], [os.path.join(ortak.ARACLAR, "film.py"), "ozet", "--film", film, "--kullanici", "--json"])

    def test_telegram_test_bildirim_test_kipi(self):
        cagri = []
        with mock.patch.object(bat_isleri.subprocess, "call", lambda k: cagri.append(k) or 0):
            self.assertEqual(bat_isleri.main(["telegram-test"]), 0)
        self.assertEqual(cagri[0][1:], [os.path.join(ortak.ARACLAR, "bildirim.py"), "--test"])


class SozlesmeKarti(unittest.TestCase):
    def test_kart_olcek_ciktisi(self):
        o = olcek.hesapla(1800, E=esikler.yukle(), olcum={}, ayar={})
        k = kullanici_karti.kart()
        self.assertEqual(k, olcek.kart_md(o))
        self.assertEqual(kullanici_karti.dosyadaki_kart(BASLA), k, "BASLA_BURADAN.txt kartı eski: python kullanici_karti.py --yaz")
        el, t, kr = o["el_isi"], o["takvim"], o["kredi"]
        for parca in (f"≈ {el['paket']} paket", f"≈ {olcek.say(el['gonder_video'])} kez, ≈ {t['video_gun']} gün",
                      f"≤ {olcek.say(kr['olcum_kredi'])} kredi", f"≈ {olcek.ond(el['toplam_saat'], 1)} saat",
                      f"≈ {olcek.aralik(t['toplam_gun'])} gün", f"≈ {el['tamam']} kez", f"≈ {el['d_tak']} kez",
                      f"≈ {olcek.say(kr['butce_tahmini'])} kredi"):
            self.assertIn(parca, k)
        self.assertNotIn("{", k)                                   # doldurulmamış yer tutucu yok

    def test_kart_yerlestir(self):
        m = "a\n" + kullanici_karti.BAS + "\neski\n" + kullanici_karti.SON + "\nb\n"
        y = kullanici_karti.yerlestir(m, "YENI")
        self.assertEqual(y, "a\n" + kullanici_karti.BAS + "\nYENI\n" + kullanici_karti.SON + "\nb\n")
        with self.assertRaises(ValueError): kullanici_karti.yerlestir("imsiz", "x")


class Rehber(unittest.TestCase):
    def setUp(self): self.m = oku(BASLA)

    def test_bolumler_ve_zorunlu_icerik(self):
        m = self.m
        self.assertIn("EMEKLİ", m.splitlines()[3])                             # §6.9: başta emeklilik satırları
        self.assertLess(m.index("EMEKLİ"), m.index(kullanici_karti.BAS))
        for b in ("1) SÖZLEŞME KARTI", "2) BİR KEZ", "3) HER FİLM", "4) BİR ŞEY TERS GİDERSE", "5) SENİN HİÇ YAPMADIKLARIN"):
            self.assertIn(b, m)
        for s in ("git clone", "ilk kurulum", "GitHub", "gemini_anahtar.txt", "faturalandırma", ".csv", "GELENLER\\KANAL",
                  "GÖNDER'e BASMA", "YENİLEME", "30 dakika", "UYARI_GECTI.bat", "VARSAYILAN KAPALI", "sen seç",
                  "KARAR_DEFTERI.md", "ZIP"):
            self.assertIn(s, m, s)
        for ad in set(adlar_bat()["depo_koku"]) | set(adlar_bat()["film_klasoru"]): self.assertIn(ad, m, ad)
        self.assertNotIn("Soysal", m)                                          # gerçek yol kodda/rehberde sabit yazılmaz
        with open(BASLA, "rb") as f: self.assertIn(b"\r\n", f.read())

    def test_beni_oku(self):
        m = oku(os.path.join(YZ, "00_BENI_OKU.txt"))
        self.assertIn("BASLA_BURADAN.txt", m); self.assertIn("FILM_SETI.bat", m)


class Paketle(unittest.TestCase):
    def test_kunye_lisanslardan(self):
        L = json.loads(oku(paketle.LISANSLAR)); k = paketle.kunye_metni(L)
        for ad, x in L["bilesenler"].items():
            self.assertIn(f"- {ad}", k)
            if x.get("kaynak"): self.assertIn(x["kaynak"], k)
        self.assertIn(f"Toplam {len(L['bilesenler'])} bileşen", k); self.assertIn("kie.ai", k)

    def test_paket_kunye_sablon_ve_tarama(self):
        hedef = tempfile.mkdtemp(dir=_ortam.KOK)
        (kod, zp), out = sessiz(paketle.paketle, hedef)
        self.assertEqual(kod, 0, out)
        with zipfile.ZipFile(zp) as z:
            adlar = z.namelist(); self.assertIn("YZ_FILM/KUNYE.txt", adlar)
            for s in paketle.SABLONLAR: self.assertEqual(z.getinfo("YZ_FILM/AYARLAR/" + s).file_size, 0)
            self.assertFalse([a for a in adlar if "/testler/" in a or a.lower().endswith(".pyc") or "memmet_profil" in a])
            self.assertFalse([a for a in adlar if a.startswith("YZ_FILM/FILMLER/") and a.lower().endswith(".bat")])
            self.assertIn("YZ_FILM/BASLA_BURADAN.txt", adlar)
        self.assertEqual(paketle.sizinti_tara(zp), [])

    def test_sizinti_reddedilir_silinmez(self):
        sahte = "12345678" + "9:" + "A" * 35                                   # Telegram biçimli sahte dizi
        hedef = tempfile.mkdtemp(dir=_ortam.KOK)
        with mock.patch.object(paketle, "kunye_metni", lambda: "künye " + sahte):
            (kod, zp), out = sessiz(paketle.paketle, hedef)
        self.assertEqual(kod, 1); self.assertIsNone(zp); self.assertIn("REDDEDİLDİ", out); self.assertNotIn(sahte, out)
        self.assertEqual(os.listdir(hedef), [])
        red = os.path.join(ortak.yollar()["ayarlar"], "_REDDEDILEN_PAKET")
        self.assertTrue(os.listdir(red))                                       # silinmedi, gizli klasöre taşındı

    def test_sizinti_tara_kurallari(self):
        d = tempfile.mkdtemp(dir=_ortam.KOK); zp = os.path.join(d, "x.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr("YZ_FILM/AYARLAR/OKU_BENI.txt", "açıklama")
            z.writestr("YZ_FILM/AYARLAR/ai84_anahtar.txt", "")
            z.writestr("YZ_FILM/AYARLAR/x_anahtar.txt", "dolu")
            z.writestr("YZ_FILM/AYARLAR/MEMMET_AYAR.json", "{}")
            z.writestr("YZ_FILM/a.txt", "k=AIza" + "B" * 35)
            z.writestr("YZ_FILM/memmet_profil/Cookies", "")
            z.writestr("YZ_FILM/b.json", '{"sha1": "' + "a" * 40 + '"}')
        bulunan = {a for a, _ in paketle.sizinti_tara(zp)}
        self.assertEqual(bulunan, {"YZ_FILM/AYARLAR/x_anahtar.txt", "YZ_FILM/AYARLAR/MEMMET_AYAR.json", "YZ_FILM/a.txt",
                                   "YZ_FILM/memmet_profil/Cookies"})


class CIIsAkisi(unittest.TestCase):
    def setUp(self): self.m = oku(CI)

    @unittest.skipIf(yaml is None, "PyYAML yok (CI kurar)")
    def test_gecerli_yaml_ve_matris(self):
        d = yaml.safe_load(self.m)
        on = d.get("on", d.get(True))                      # YAML 1.1: 'on' anahtarı True okunur
        self.assertIn("push", on); self.assertIn("pull_request", on)
        is_ = d["jobs"]["testler"]; mat = is_["strategy"]["matrix"]
        kombin = {(o, str(p)) for o in mat["os"] for p in mat["python"]} - {(x["os"], str(x["python"])) for x in mat.get("exclude", [])}
        kombin |= {(x["os"], str(x["python"])) for x in mat.get("include", [])}
        self.assertEqual(kombin, {("windows-latest", "3.10"), ("ubuntu-latest", "3.10"), ("ubuntu-latest", "3.13")})
        self.assertFalse(is_["strategy"].get("fail-fast", True))
        self.assertLessEqual(int(is_["timeout-minutes"]), 20)
        adimlar = is_["steps"]; metin = json.dumps(adimlar)
        self.assertTrue(any(str(s.get("uses", "")).startswith("actions/setup-python@") for s in adimlar))
        self.assertTrue(any("setup-ffmpeg" in str(s.get("uses", "")) for s in adimlar))
        kur = next(s["run"] for s in adimlar if "pip install" in str(s.get("run", "")))
        self.assertEqual(set(kur.split("pip install", 1)[1].split()), {"numpy", "Pillow", "PyYAML"})
        kos = [s for s in adimlar if "ARACLAR/testler" in str(s.get("run", ""))]
        self.assertTrue(kos); self.assertEqual(kos[-1].get("working-directory"), "YZ_FILM")
        self.assertEqual(str(is_["env"]["CLAUDE_CODE_FORK_SUBAGENT"]), "0")

    def test_metin_kurallari(self):
        self.assertNotIn("\t", self.m)
        for s in ("windows-latest", "ubuntu-latest", "'3.10'", "'3.13'", "ARACLAR/testler"): self.assertIn(s, self.m)


class Kosucu(unittest.TestCase):
    def test_bolunen_modulde_her_test_bir_kez(self):
        import kos
        L = unittest.TestLoader(); isler = kos.isler()
        hedefler = [h for _, hs in isler for h in hs]
        self.assertEqual(len(hedefler), len(set(hedefler)))
        def adlar(s):
            for x in s:
                if isinstance(x, unittest.TestSuite): yield from adlar(x)
                else: yield x.id()
        for m in kos.BOL:
            tam = sorted(adlar(L.loadTestsFromName(m)))
            parca = sorted(t for h in hedefler if h.split(".")[0] == m for t in adlar(L.loadTestsFromName(h)))
            self.assertTrue(tam); self.assertEqual(parca, tam, m)
        tum = {f[:-3] for f in os.listdir(HERE) if f.startswith("test_") and f.endswith(".py")}
        self.assertEqual({h.split(".")[0] for h in hedefler}, tum)


class GelistiriciBelgesi(unittest.TestCase):
    def test_durum_adim_18_bitti(self):
        m = oku(os.path.join(ARACLAR, "CLAUDE.md")); durum = m.split("## Şu anki durum", 1)[1].split("## Uygulama sırası", 1)[0]
        self.assertIn("**18 PR-14", durum)
        bek = durum.split("**Bekleyen adımlar:**", 1)[1]
        for s in ("**2 ", "**9 ", "**11 ", "**12a ", "**19 ", "memmet3"): self.assertIn(s, bek)
        self.assertNotIn("**18 ", bek)


if __name__ == "__main__":
    unittest.main()
