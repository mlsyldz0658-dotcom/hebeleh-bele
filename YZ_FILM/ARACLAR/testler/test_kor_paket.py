"""Kör paket testi (TASARIM §6.2, §6.10 "test_kor_paket: sızıntı 0", D-18, [CM2] §4.5.9).

  - Kâğıt kipi: yasak alanların (amac, duygu, hedef_duygu, vurus, risk, sahne_degeri, seyirci_ogrenir, kagit bloğu, anahtar olgular,
    merak, kurulum, karakter sırrı, çeviri) değerleri seyirci klasörlerine ve ilk 2 dk dosyalarına SIZMAZ (sızıntı 0).
  - Ad maskeleme: ad ve hitaplar ilk kez sözle söylenene/yazılana kadar görünüş etiketiyle; satır sırasıyla bağımsız denetim.
  - Aşamalı bölümler P0 (0–120 sn) → P1 → P2 → P3; film.py'nin asamali kaynağı (_KOR_PAKET/<kip>_t<tur>/<persona>/<bolum>) ile uyumlu.
  - Persona satırı (kâğıt: 3 × A); eşleştirici anahtarı yalnız ESLESTIRICI/'de; plan kipi (SAHNELER v2); izleme kipleri → kor_paket_izleme, kapak → kapak.kor_paketi;
    kendi sızıntı denetimi tutarsa paket yayımlanmaz (1, _RED/); eski paket _ESKI/'ye taşınır (silinmez)."""
import os, sys, re, json, glob, shutil, tempfile, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak
import kor_paket

KAR = {"sera": {"ad": "Sera", "rol": "kahraman", "sir": "SIZINTI_SIR yavruyu saklıyor", "istek": "SIZINTI_ISTEK ağabeyin affı",
                "maske": {"etiket_anonim_en": "woman in a green cloak", "takma_adlar": ["huntress", "sister"]}},
       "brann": {"ad": "Brann", "rol": "karsit", "korku": "SIZINTI_KORKU yalnızlık",
                 "maske": {"etiket_anonim_en": "man with a scarred jaw", "takma_adlar": ["Captain"]}}}


def sahne(sid, sure, parti, gorulen, duyulan, **ek):
    s = {"id": sid, "hikaye_partisi": parti, "mekan": "kulube", "zaman": {"gun": 1, "saat": "gece", "atlama": "yok"},
         "hedef_sure_sn": sure, "vurus": "SIZINTI_VURUS_" + sid, "hedef_duygu": "SIZINTI_DUYGU_" + sid, "yogunluk": 7,
         "sahne_degeri": {"bas": "SIZINTI_DEGER_BAS_" + sid, "son": "SIZINTI_DEGER_SON_" + sid}, "risk": "SIZINTI_RISK_" + sid,
         "merak_ac": ["m01"], "seyirci_ogrenir": "SIZINTI_OGRENIR_" + sid + " seyirci bunu öğrenir",
         "kagit": {"amac": "SIZINTI_KAGIT_AMAC_" + sid, "neden_simdi": "SIZINTI_NEDEN_" + sid},
         "ekran": {"gorulen": gorulen, "duyulan": duyulan, "ekran_disi": ["distant horn"]}}
    s.update(ek); return s


def hikaye():
    return {"_surum": "v2", "baslik": {"secilen": "The Hidden Hatchling"},
            "logline": "SIZINTI_LOGLINE a huntress hides a dragon",
            "vaat_sozlesmesi": [{"oge": "kapak_imgesi", "sahne": "S01", "ekranda": "Sera holds a glowing cloak"}],
            "anahtar_olgular": [{"id": "o01", "olgu": "SIZINTI_OLGU Sera yavruyu saklıyor", "kritik": True}],
            "MERAK_DEFTERI": [{"id": "m01", "soru": "SIZINTI_MERAK Brann ele verecek mi?"}],
            "KURULUMLAR": [{"id": "kur1", "ne": "SIZINTI_KURULUM kemik düdük"}],
            "karakterler": KAR,
            "partiler": [{"id": "P1", "sahneler": ["S01", "S03"]}, {"id": "P2", "sahneler": ["S04", "S04"]},
                         {"id": "P3", "sahneler": ["S05", "S05"]}],
            "sahneler": [
                sahne("S01", 60, "P1", ["Sera kneels at the cave mouth.", "The huntress brushes the snow aside."], ["R0001"]),
                sahne("S02", 70, "P1", ["Brann rides up the slope.", "Sera watches from the door."], ["R0002"]),
                sahne("S03", 100, "P1", ["Sera bars the door.", "Brann waits outside."], ["R0003"]),
                sahne("S04", 90, "P2", ["Brann draws his sword."], ["R0004"]),
                sahne("S05", 80, "P3", ["Brann falls into the snow."], []),
            ],
            "replikler": [
                {"id": "R0001", "sahne": "S01", "karakter": "sera", "metin": "Easy now.", "tr": "SIZINTI_TR Sakin ol.", "tasidigi": ["o01"]},
                {"id": "R0002", "sahne": "S02", "karakter": "brann", "metin": "Sera! Open the door.", "ad_soyler": ["sera"],
                 "tr": "SIZINTI_TR Sera! Kapıyı aç."},
                {"id": "R0003", "sahne": "S03", "karakter": "sera", "metin": "Go away, Captain."},
                {"id": "R0004", "sahne": "S04", "karakter": "sera", "metin": "Brann, please.", "ad_soyler": ["brann"]},
            ]}


def jo(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def oku(p):
    with open(p, encoding="utf-8") as f: return f.read()


def satir_sirasi_denetimi(metinler, karakterler):
    """Bağımsız denetim: metinler sırayla okunur; tırnak dışı metinde kurulmamış ad/hitap ([etiket] dışında) olmamalı.
    Tırnak içi (duyulan) ad geçince karakter kurulur. → hata listesi."""
    kurulan, hatalar = set(), []
    for metin in metinler:
        for sat in metin.splitlines():
            tirnak = " ".join(re.findall(r"\"([^\"]*)\"", sat))
            acik = re.sub(r"\[[^\]]*\]", "", re.sub(r"\"[^\"]*\"", "", sat))
            for kid, v in karakterler.items():
                if kid in kurulan: continue
                for a in [v["ad"]] + v["maske"]["takma_adlar"]:
                    if re.search(r"(?<![\w])" + re.escape(a) + r"(?![\w])", acik, re.I): hatalar.append((kid, a, sat))
            for kid, v in karakterler.items():
                if re.search(r"(?<![\w])" + re.escape(v["ad"]) + r"(?![\w])", tirnak, re.I): kurulan.add(kid)
    return hatalar


class TestKorPaket(unittest.TestCase):
    def setUp(self):
        self.film = tempfile.mkdtemp(prefix="kp_", dir=os.path.join(_ortam.VERI, "FILMLER"))
        ortak.atomik_yaz(os.path.join(self.film, "_HIKAYE_ODASI", "06_SENARYO_v1.json"), hikaye())
        self.kok = os.path.join(self.film, "_KOR_PAKET", "kagit_t1")

    def kos(self, *a, env=None):
        e = dict(os.environ); e.update(env or {})
        return subprocess.run([sys.executable, os.path.join(ARACLAR, "kor_paket.py")] + list(a) + ["--film", self.film],
                              capture_output=True, text=True, env=e)

    def seyirci_dosyalari(self):
        return [p for p in glob.glob(os.path.join(self.film, "_KOR_PAKET", "**", "*.md"), recursive=True)]

    def test_sizinti_sifir(self):
        r = self.kos("--kip", "kagit", "--tur", "1")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        dosyalar = self.seyirci_dosyalari()
        self.assertGreaterEqual(len(dosyalar), 15)                  # 3 persona × 4 bölüm + 3 ilk 2 dk
        for p in dosyalar:
            self.assertNotIn("SIZINTI", oku(p), p)
            for yasak in ("amac", "hedef_duygu", "seyirci_ogrenir", "sahne_degeri", "m01", "o01", "kur1"):
                self.assertNotIn(yasak, oku(p), (p, yasak))
        m = jo(os.path.join(self.kok, "PAKET.json"))
        self.assertEqual(m["sizinti"], {"yasak_alan": 0, "ad": 0})
        self.assertEqual(m["_uretim"]["sonuc"], "GEC")
        for k in ("asama", "gorev", "girdi_imza", "arac_surum", "esik_surum", "sonuc", "zaman", "ortam"):
            self.assertIn(k, m["_uretim"])

    def test_bolumler_ve_persona(self):
        self.assertEqual(self.kos("--kip", "kagit", "--tur", "1").returncode, 0)
        for k in ("A", "B", "C"):
            for b in ("P0", "P1", "P2", "P3"):
                p = os.path.join(self.kok, k, b, "EKRAN.md")
                self.assertTrue(os.path.isfile(p), p)
                self.assertIn(kor_paket.PERSONA["A"], oku(p))          # kâğıt kipinde 3 × A (D-18)
        p0 = oku(os.path.join(self.kok, "A", "P0", "EKRAN.md")); p1 = oku(os.path.join(self.kok, "A", "P1", "EKRAN.md"))
        self.assertIn("(S01)", p0); self.assertIn("(S02)", p0); self.assertNotIn("(S03)", p0)      # P0 = 0–120 sn
        self.assertIn("(S03)", p1); self.assertNotIn("(S04)", p1)
        self.assertIn("(S04)", oku(os.path.join(self.kok, "A", "P2", "EKRAN.md")))
        self.assertIn("(S05)", oku(os.path.join(self.kok, "A", "P3", "EKRAN.md")))
        self.assertIn("[02:10] Sahne 3", p1)
        self.assertIn("EKRAN DIŞI SES: distant horn", p0)
        m = jo(os.path.join(self.kok, "PAKET.json"))
        self.assertEqual(m["bolumler"]["P0"], ["S01", "S02"])

    def test_ad_maskeleme_satir_sirasi(self):
        self.assertEqual(self.kos("--kip", "kagit", "--tur", "1").returncode, 0)
        metinler = [oku(os.path.join(self.kok, "B", b, "EKRAN.md")) for b in ("P0", "P1", "P2", "P3")]
        self.assertEqual(satir_sirasi_denetimi(metinler, KAR), [])
        p0, p1, p2, p3 = metinler
        self.assertIn("[woman in a green cloak] kneels", p0)
        self.assertIn("The [woman in a green cloak] brushes", p0)      # hitap ("huntress") da maskeli
        self.assertIn("[man with a scarred jaw]: \"Sera! Open the door.\"", p0)
        self.assertIn("Sera bars the door.", p1)                        # ad söylendi: artık adıyla
        self.assertIn("[man with a scarred jaw] waits", p1)
        self.assertIn("SERA: \"Go away, Captain.\"", p1)               # duyulan hitap serbest; Brann'ı kurmaz
        self.assertIn("[man with a scarred jaw] draws", p2)             # adı bu sahnede söylenir; görülen satır sahne başı durumuyla
        self.assertIn("Brann falls", p3)

    def test_ilk2dk_ve_eslestirici_anahtari(self):
        self.assertEqual(self.kos("--kip", "kagit", "--tur", "2").returncode, 0)
        ik = os.path.join(self.film, "_KOR_PAKET", "kagit_ilk2dk_t2")
        for k in ("A", "B", "C"):
            t = oku(os.path.join(ik, "ILK2DK_%s.md" % k))
            self.assertIn("BAŞLIK: The Hidden Hatchling", t)
            self.assertIn("KAPAK: [woman in a green cloak] holds a glowing cloak", t)
            self.assertIn("(S02)", t); self.assertNotIn("(S03)", t)
            self.assertNotIn("SIZINTI", t)
        a = jo(os.path.join(self.film, "_KOR_PAKET", "kagit_t2", "ESLESTIRICI", "ANAHTAR.json"))
        self.assertEqual(a["anahtar_olgular"][0]["id"], "o01")
        self.assertTrue(any(x["id"] == "brann" for x in a["maske"]))
        for k in ("A", "B", "C"):                                       # anahtar seyirci klasörüne girmez
            self.assertFalse(glob.glob(os.path.join(self.film, "_KOR_PAKET", "kagit_t2", k, "**", "ANAHTAR*"), recursive=True))

    def test_tur_gorevden_ve_film_py_bolum_kaynagi(self):
        gd = os.path.join(self.film, "_GOREV", "A06-KP-001"); os.makedirs(gd)
        ortak.atomik_yaz(os.path.join(gd, "GOREV.json"), {"id": "A06-KP-001", "tur_no": 3})
        self.assertEqual(self.kos("--kip", "kagit", env={"YZ_FILM_GOREV": gd}).returncode, 0)
        # film.py gorev_kur: kaynak = _KOR_PAKET/{kip}_t{tur}/{persona}; _bolum_ac kaynak/<bolum>'u GIRDI'ye kopyalar
        for persona in ("A", "B", "C"):
            self.assertTrue(os.path.isdir(os.path.join(self.film, "_KOR_PAKET", "kagit_t3", persona, "P1")))
        m = jo(os.path.join(self.film, "_KOR_PAKET", "kagit_t3", "PAKET.json"))
        self.assertEqual(m["_uretim"]["gorev"], "A06-KP-001")

    def test_kendi_denetimi_sizintiyi_yakalar(self):
        h = hikaye(); h["sahneler"][0]["kagit"]["amac"] = "distant horn"     # yasak alan değeri pakete giren bir metinle aynı
        ortak.atomik_yaz(os.path.join(self.film, "_HIKAYE_ODASI", "06_SENARYO_v2.json"), h)
        r = self.kos("--kip", "kagit", "--tur", "1")
        self.assertEqual(r.returncode, 1, r.stdout)
        self.assertFalse(os.path.exists(self.kok))                      # yayımlanmadı
        self.assertTrue(glob.glob(os.path.join(self.film, "_KOR_PAKET", "_RED", "kagit_t1_SIZINTI.json")))

    def test_eski_paket_tasinir(self):
        self.assertEqual(self.kos("--kip", "kagit", "--tur", "1").returncode, 0)
        self.assertEqual(self.kos("--kip", "kagit", "--tur", "1").returncode, 0)
        self.assertTrue(glob.glob(os.path.join(self.film, "_KOR_PAKET", "_ESKI", "kagit_t1_*")))
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "PAKET.json")))

    def test_izleme_kipleri_yonlenir(self):
        """Birleştirme: izleme kipleri kor_paket_izleme'ye, kapak kapak.kor_paketi'ne yönlenir ("henüz yok → 4" kalktı).
        Bu filmde T1/T2/kesit planı yok → izleme kipi 4 (girdisi yok); kapak adayı yok → 1."""
        for kip in ("animatik", "kurgu", "kesit", "kesici"):
            r = self.kos("--kip", kip, "--tur", "1")
            self.assertEqual(r.returncode, 4, (kip, r.stdout, r.stderr)); self.assertNotIn("henüz yok", r.stdout)
        r = self.kos("--kip", "kapak", "--tur", "1")
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr); self.assertIn("kapak adayı yok", r.stdout)

    def test_kapak_kipi_kapak_kor_paketi(self):
        try:
            from PIL import Image
        except ImportError: self.skipTest("Pillow yok")
        for i in range(1, 4):
            p = os.path.join(self.film, "YAYIN", "_KAPAK_ADAYLAR", "kapak_%02d.jpg" % i); os.makedirs(os.path.dirname(p), exist_ok=True)
            Image.new("RGB", (1280, 720), (i * 40, 90, 120)).save(p)
        r = self.kos("--kip", "kapak", "--tur", "2")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        kok = os.path.join(self.film, "_KOR_PAKET", "kapak_t2")
        self.assertTrue(os.path.isfile(os.path.join(kok, "SEYIRCI", "CIFTLER.json")))       # habersiz-seyirci·kapak klasörü
        self.assertTrue(os.path.isdir(os.path.join(kok, "1")))                              # kare-tarifcisi·kapak klasörü

    def test_izleme_kipi_animatik_t1_ile(self):
        """T1 çizelgesi varsa animatik kipi gerçek paket kurar (0)."""
        import zaman_cizelgesi_t1  # noqa: F401
        film = os.path.join(_ortam.VERI, "FILMLER", "kp_izleme_%d" % os.getpid())
        if os.path.exists(film): shutil.move(film, film + "_eski_%d" % len(os.listdir(os.path.dirname(film))))
        tam = os.path.join(os.path.dirname(ARACLAR), "FILMLER", "ORNEK_3_SAHNE_TAM")
        os.makedirs(film)
        for ad in ("HIKAYE.json", "SAHNELER.json"): shutil.copy2(os.path.join(tam, ad), os.path.join(film, ad))
        shutil.copytree(os.path.join(tam, "_SES"), os.path.join(film, "_SES"))
        z = subprocess.run([sys.executable, os.path.join(ARACLAR, "zaman_cizelgesi.py"), "--asama", "animatik", "--tur", "1", "--film", film],
                           capture_output=True, text=True)
        self.assertEqual(z.returncode, 0, z.stdout + z.stderr)
        r = subprocess.run([sys.executable, os.path.join(ARACLAR, "kor_paket.py"), "--kip", "animatik", "--tur", "1", "--film", film],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertTrue(os.path.isdir(os.path.join(film, "_KOR_PAKET", "animatik_t1")))

    def test_plan_kipi_ilk2dk_hitap_sizinti_degil(self):
        """Birleştirme: ilk 2 dk dosyasında repliğin içindeki hitap ("Sera,") adı kurar; sonraki 'SERA:' etiketi sızıntı sayılmaz."""
        tam = os.path.join(os.path.dirname(ARACLAR), "FILMLER", "ORNEK_3_SAHNE_TAM")
        for ad in ("HIKAYE.json", "SAHNELER.json"): shutil.copy2(os.path.join(tam, ad), os.path.join(self.film, ad))
        shutil.copytree(os.path.join(tam, "_SES"), os.path.join(self.film, "_SES"))
        r = self.kos("--kip", "plan", "--tur", "1")
        self.assertEqual(r.returncode, 0, r.stdout)
        m = jo(os.path.join(self.film, "_KOR_PAKET", "plan_t1", "PAKET.json"))
        self.assertEqual(m["sizinti"], {"yasak_alan": 0, "ad": 0})
        ik = oku(os.path.join(self.film, "_KOR_PAKET", "plan_ilk2dk_t1", "ILK2DK_A.md"))
        self.assertIn('"Sera, they ride with torches tonight."', ik); self.assertIn("SERA der:", ik)
        kar = {k: {"ad": (v or {}).get("ad") or k.title(), "maske": {"takma_adlar": ((v or {}).get("maske") or {}).get("takma_adlar") or []}}
               for k, v in (jo(os.path.join(self.film, "HIKAYE.json")).get("karakterler") or {}).items()}
        self.assertEqual(satir_sirasi_denetimi([ik], kar), [])          # bağımsız satır sırası denetimi de temiz

    def test_girdi_yoksa_hata(self):
        shutil.move(os.path.join(self.film, "_HIKAYE_ODASI"), os.path.join(self.film, "_yok"))
        self.assertEqual(self.kos("--kip", "kagit").returncode, 1)

    def test_plan_kipi(self):
        sv = {"_surum": 2, "karakterler": {"sera": {"ref": "01_KARAKTERLER/sera.jpg"}, "brann": {}},
              "sahneler": [
                  {"no": 1, "sira": 1, "parti": 1, "amac": "SIZINTI_PLAN_AMAC", "duygu": "SIZINTI_PLAN_DUYGU",
                   "gorsel_istem": "SIZINTI_ISTEM gorsel", "hareket_istem": "SIZINTI_ISTEM hareket",
                   "replik": {"id": "R0003", "karakter": "sera", "metin": "Go away, Captain."}, "kullanim": {"bas": 0, "sure": 5},
                   "zanaat": {"kod": "S03-P01", "kamera": {"kadraj": "OY", "aci": "goz_hizasi", "hareket_tipi": "sabit"},
                              "kadrajdakiler": [{"id": "sera", "konusur": True}],
                              "eylem_zinciri": [{"bas": 0.5, "bit": 1.5, "ozne": "sera", "fiil": "cene_kaldirir", "govde": "cene",
                                                 "olcu": "hafif"},
                                                {"bas": 2.0, "bit": 4.0, "ozne": "sera", "tur": "konusma", "fiil": "konusur", "replik": "R0003"}],
                              "oyunculuk": {"sera": {"ic_durum": "SIZINTI_IC korkuyor", "alt_metin": "SIZINTI_ALT metin"}},
                              "ekranda_bilgi": "SIZINTI_EKRANDA_BILGI Sera kapıyı kapatıyor",
                              "ses": {"flow_sound": "Sound: wind against the door. No music."}},
                   "_derlenir": {"hikaye": {"hedef_duygu": "SIZINTI_DERLENIR_DUYGU"}}},
                  {"no": 2, "sira": 2, "parti": 2, "kullanim": {"sure": 200},
                   "zanaat": {"kamera": {"kadraj": "GEN"}, "kadrajdakiler": [{"id": "brann"}],
                              "eylem_zinciri": [{"bas": 0, "bit": 2, "ozne": "brann", "fiil": "kiliç_ceker", "hedef": "sera"}]}},
                  {"no": 3, "sira": 3, "parti": 3, "kullanim": {"sure": 6},
                   "zanaat": {"kamera": {"kadraj": "Y"}, "eylem_zinciri": [{"bas": 0, "bit": 2, "ozne": "brann", "fiil": "duser"}]}}]}
        ortak.atomik_yaz(os.path.join(self.film, "SAHNELER.json"), sv)
        ortak.atomik_yaz(os.path.join(self.film, "HIKAYE.json"), hikaye())
        r = self.kos("--kip", "plan", "--tur", "1")
        self.assertEqual(r.returncode, 0, r.stdout)
        kok = os.path.join(self.film, "_KOR_PAKET", "plan_t1")
        p0 = oku(os.path.join(kok, "A", "P0", "EKRAN.md"))
        self.assertIn("KADRAJ: orta yakın plan, goz hizasi, sabit kamera", p0)
        self.assertIn("[woman in a green cloak] cene kaldirir", p0)
        self.assertIn("der: \"Go away, Captain.\"", p0)
        self.assertIn("SES: wind against the door. No music.", p0)
        self.assertIn("[man with a scarred jaw] kiliç ceker → [woman in a green cloak]", p0)    # plan 2 de 5. sn'de başlar
        self.assertIn("[man with a scarred jaw] duser", oku(os.path.join(kok, "A", "P3", "EKRAN.md")))
        for p in glob.glob(os.path.join(kok, "**", "*.md"), recursive=True):
            self.assertNotIn("SIZINTI", oku(p), p)

    def test_plan_kipi_v1_dosyasinda_ortam(self):
        ortak.atomik_yaz(os.path.join(self.film, "SAHNELER.json"), {"sahneler": [{"no": 1}]})
        self.assertEqual(self.kos("--kip", "plan").returncode, 4)

    def test_maske_birimi(self):
        mk = kor_paket.Maske(KAR)
        self.assertEqual(mk.maskele("Sera meets the Captain."), "[woman in a green cloak] meets the [man with a scarred jaw].")
        mk.duyuldu("Hello Sera")
        self.assertEqual(mk.maskele("Sera meets Brann."), "Sera meets [man with a scarred jaw].")
        self.assertEqual(mk.anan("brann", gorunur=False), "[ekran dışından bir ses]")
        self.assertEqual(mk.anan("sera"), "SERA")


if __name__ == "__main__":
    unittest.main()
