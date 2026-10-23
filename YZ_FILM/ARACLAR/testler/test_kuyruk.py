"""kuyruk.py testleri (TASARIM §5.7, D-31, §1.5, §6.10): 0 kredi kuralı, soy sayacı ve merdiven, öncelik, tekrar ayıklama,
kirp maddesi, kapı raporlarından toplama, YENIDEN_YAZ, eski klibin _ESKI/'ye taşınması, MERDIVEN.md, CLI çıkış kodları."""
import os, sys, json, shutil, tempfile, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import kapi, kuyruk, ortak

ARAC = os.path.join(os.path.dirname(HERE), "kuyruk.py")
E = {"oncelik_konum_agirligi": 1.5, "oncelik_dogrulanmis_carpan": 1.25}
SK = {"denendi": True, "basamaklar": [1, 5, 6], "gerekce": "kusur pencerenin içinde; kırpma yetmez"}


def madde(plan=41, **ek):
    m = {"plan": plan, "tur": "video", "kaynak_kapi": "KI", "kaynak_rapor": "_RAPOR/SEYIRCI_KARAR_T2_t1.json",
         "kok_neden": "nesne_zipladi", "seviye": "KRITIK", "seyirci_sayisi": 2, "dogrulanmis": True, "konum_agirligi": 1.5,
         "cozum": "yeniden_cek", "duzeltme": "CORRECTION: the lantern stays in Mara's LEFT hand.", "sifir_kredi": dict(SK),
         "kredi_tahmini": 24}
    m.update(ek); return m


class Kuyruk(unittest.TestCase):
    def setUp(self):
        self.film = tempfile.mkdtemp(prefix="kuyruk_"); self.addCleanup(shutil.rmtree, self.film, True)

    def ekle(self, *ms, **kw): return kuyruk.ekle(self.film, list(ms), E=E, **kw)

    # --- 0 kredi kuralı ---------------------------------------------------------------------------------------
    def test_sifir_kredi_kurali(self):
        for cz in ("yeniden_cek", "bitis_sabit", "yeni_plan", "yeni_sahne", "z2_bitis"):
            for sk in (None, {"denendi": False, "gerekce": "x"}, {"denendi": True}, {"denendi": True, "gerekce": "  "}, {"denendi": "evet", "gerekce": "x"}):
                m = madde(cozum=cz); m.pop("sifir_kredi")
                if sk is not None: m["sifir_kredi"] = sk
                s = self.ekle(m)
                self.assertEqual(s["eklenen"], [], (cz, sk))
                self.assertEqual(len(s["reddedilen"]), 1)
                self.assertTrue(any("0 kredi" in n for n in s["reddedilen"][0]["neden"]))
        self.assertEqual(kuyruk.acik_maddeler(self.film), [])
        self.assertTrue(kuyruk.oku(self.film)["reddedilenler"])          # red kaydı dosyada kalır
        self.assertEqual(len(self.ekle(madde())["eklenen"]), 1)

    def test_kirp_kuyruga_girmez(self):
        s = self.ekle(madde(cozum="kirp", kaynak_kapi="V1", sifir_kredi=None))
        self.assertEqual(s["eklenen"], []); self.assertEqual(len(s["kirp"]), 1)
        self.assertEqual(kuyruk.acik_maddeler(self.film), [])

    # --- soy sayacı -------------------------------------------------------------------------------------------
    def test_soy_sayaci_ve_merdiven(self):
        s1 = self.ekle(madde()); m1 = kuyruk.acik_maddeler(self.film)[0]
        self.assertEqual((m1["deneme"], m1["deneme_max"], m1["soy"]), (2, 3, 41))
        kuyruk.durum_degistir(self.film, m1["id"], "gonderildi"); kuyruk.durum_degistir(self.film, m1["id"], "tamam")
        self.ekle(madde(kok_neden="yuz_degisti")); m2 = kuyruk.acik_maddeler(self.film)[0]
        self.assertEqual(m2["deneme"], 3)
        kuyruk.durum_degistir(self.film, m2["id"], "tamam")
        s3 = self.ekle(madde(kok_neden="morf"))                          # 4. deneme olurdu → red + onarım
        self.assertEqual(s3["eklenen"], [])
        self.assertEqual(s3["merdiven"][0]["basamak"], "yonetmen·onarim")
        # bölmeden doğan plan soyun sayacını taşır
        s4 = self.ekle(madde(plan=412, soy=41, kok_neden="morf"))
        self.assertEqual(s4["eklenen"], [])
        self.assertEqual(s4["merdiven"][0]["basamak"], "durdu"); self.assertEqual(s4["merdiven"][0]["gorev"], "kurgucu·sifir_kredi")
        self.assertEqual(kuyruk.oku(self.film)["soylar"]["video:41"]["deneme"], 3)
        # görsel sayacı ayrı; ses yeniden çekimi video sayacına yazılır
        self.assertEqual(len(self.ekle(madde(tur="gorsel", kaynak_kapi="G1"))["eklenen"]), 1)
        self.assertEqual(self.ekle(madde(tur="ses", kaynak_kapi="S2", kok_neden="veo_konusmadi"))["merdiven"][0]["basamak"], "durdu")
        self.assertIsNotNone(s1)

    def test_ayni_cekim_deneme_harcamaz(self):
        self.ekle(madde(), madde(kok_neden="yuz_degisti"))
        acik = kuyruk.acik_maddeler(self.film)
        self.assertEqual(len(acik), 2); self.assertEqual({m["deneme"] for m in acik}, {2})
        self.assertEqual(kuyruk.oku(self.film)["soylar"]["video:41"]["deneme"], 2)

    def test_verilen_deneme_ve_tavan_yukseltilemez(self):
        s = self.ekle(madde(deneme=4, deneme_max=9))
        self.assertEqual(s["eklenen"], []); self.assertEqual(s["merdiven"][0]["basamak"], "yonetmen·onarim")
        self.ekle(madde(plan=50, deneme_max=9))
        self.assertEqual(kuyruk.acik_maddeler(self.film)[0]["deneme_max"], 3)
        self.assertEqual(kuyruk.esik({"plan_soyu_deneme_max": 9})["soy_max"], 3)
        self.assertEqual(kuyruk.esik({"plan_soyu_deneme_max": 2})["soy_max"], 2)

    def test_iptal_denemeyi_geri_verir(self):
        self.ekle(madde()); m = kuyruk.acik_maddeler(self.film)[0]
        kuyruk.durum_degistir(self.film, m["id"], "iptal")
        self.assertEqual(kuyruk.oku(self.film)["soylar"]["video:41"]["deneme"], 1)
        with self.assertRaises(kuyruk.KuyrukHatasi): kuyruk.durum_degistir(self.film, m["id"], "uydurma")
        with self.assertRaises(kuyruk.KuyrukHatasi): kuyruk.durum_degistir(self.film, "YU-X-1-999", "tamam")

    # --- öncelik, sıra, tekrar ----------------------------------------------------------------------------------
    def test_oncelik_formulu(self):
        self.assertEqual(kuyruk.oncelik_hesapla(madde(), E), 8.4375)                     # 3 × 1,5 × 1,5 × 1,25
        self.assertEqual(kuyruk.oncelik_hesapla(madde(dogrulanmis=False), E), 6.75)
        self.assertEqual(kuyruk.oncelik_hesapla(madde(seviye="ORTA", seyirci_sayisi=1, dogrulanmis=False, konum_agirligi=None), E), 2.0)
        self.assertEqual(kuyruk.oncelik_hesapla(madde(seviye="ORTA", seyirci_sayisi=1, dogrulanmis=False, konum_agirligi=None, zaman_sn=30), E), 3.0)
        self.assertEqual(kuyruk.oncelik_hesapla(madde(seviye="HATA", seyirci_sayisi=3, dogrulanmis=False, konum_agirligi=1.0), E), 6.0)
        self.assertTrue(self.ekle(madde(seviye="KÜÇÜK"))["reddedilen"])

    def test_esikler_dosyasindan_katsayi(self):
        k = kuyruk.esik()
        self.assertEqual((k["konum"], k["dogrulanmis"], k["soy_max"]), (1.5, 1.25, 3))

    def test_siralama(self):
        self.ekle(madde(plan=10, seviye="ORTA", kredi_tahmini=12, kok_neden="olcek"),
                  madde(plan=11, seviye="KRITIK", kredi_tahmini=48, dogrulanmis=False, seyirci_sayisi=1, konum_agirligi=1.0),
                  madde(plan=12, seviye="ORTA", kredi_tahmini=48, kok_neden="olcek"),
                  madde(plan=13, seviye="KRITIK", kredi_tahmini=12))
        self.assertEqual([m["plan"] for m in kuyruk.acik_maddeler(self.film)], [13, 11, 10, 12])

    def test_tekrar_birlesir(self):
        self.ekle(madde(seviye="ORTA", seyirci_sayisi=1, dogrulanmis=False, kaynak_kapi="V2", kaynak_rapor="_RAPOR/V2_B07.json"))
        s = self.ekle(madde(seviye="KRITIK", seyirci_sayisi=3))
        self.assertEqual(len(s["birlesen"]), 1); self.assertEqual(s["eklenen"], [])
        m = kuyruk.acik_maddeler(self.film)
        self.assertEqual(len(m), 1); m = m[0]
        self.assertEqual((m["seviye"], m["seyirci_sayisi"], m["dogrulanmis"]), ("KRITIK", 3, True))
        self.assertEqual(len(m["kaynaklar"]), 2)
        self.assertEqual(m["oncelik"], kuyruk.oncelik_hesapla(m, E))

    def test_alanlar_ve_dilim(self):
        self.ekle(madde(kok_neden="nesne_ziplama"), madde(plan=60, tur="ses", kaynak_kapi="S2", kok_neden="veo_konusmadi"))
        q = kuyruk.oku(self.film)
        self.assertEqual(q["_surum"], 1)
        for a in kapi.ZARF_ALANLARI: self.assertIn(a, q["_uretim"])
        a, b = sorted(q["maddeler"], key=lambda m: m["plan"])
        self.assertEqual(a["kok_neden"], "nesne_zipladi")                                 # eş anlam çevrildi
        self.assertEqual((a["dilim"], b["dilim"]), ("kurgu", "ses"))
        self.assertRegex(a["id"], r"^YU-KI-1-[0-9]{3}$"); self.assertRegex(b["id"], r"^YU-S2-1-[0-9]{3}$")
        for alan in ("id", "plan", "tur", "kaynak_kapi", "kaynak_rapor", "kok_neden", "seviye", "seyirci_sayisi", "dogrulanmis",
                     "konum_agirligi", "oncelik", "cozum", "duzeltme", "sifir_kredi", "plan_metni_sahibi", "zincir_etkisi", "dilim",
                     "kredi_tahmini", "soy", "deneme", "deneme_max", "is_kimligi", "durum", "karar_veren"):
            self.assertIn(alan, a)
        self.assertEqual(a["durum"], "bekliyor")

    def test_gecersiz_alanlar(self):
        for boz in ({"kok_neden": "uydurma"}, {"kaynak_kapi": "HS_KURGU"}, {"tur": "muzik"}, {"plan": "41"}, {"cozum": "dua_et"},
                    {"seviye": "COK"}, {"zincir_etkisi": ["42"]}, {"dogrulanmis": "evet"}):
            self.assertTrue(self.ekle(madde(**boz))["reddedilen"], boz)
        self.assertEqual(kuyruk.acik_maddeler(self.film), [])

    def test_zincir_etkisi_sahnelerden(self):
        sah = {"_surum": 2, "sahneler": [
            {"no": 41, "uretim": {"zincir": {"yontem": "bagimsiz", "kaynak": None}}},
            {"no": 42, "uretim": {"zincir": {"yontem": "son_kare", "kaynak": 41}}},
            {"no": 43, "uretim": {"zincir": {"yontem": "son_kare", "kaynak": 42}}},
            {"no": 44, "uretim": {"zincir": {"yontem": "bagimsiz", "kaynak": 43}}}]}
        self.assertEqual(kuyruk.zincir_etkisi(41, sah), [42, 43])
        ortak.atomik_yaz(os.path.join(self.film, "SAHNELER.json"), sah)
        self.ekle(madde(zincir_etkisi=[50]))
        self.assertEqual(kuyruk.acik_maddeler(self.film)[0]["zincir_etkisi"], [42, 43, 50])

    # --- kapı raporlarından toplama ---------------------------------------------------------------------------------
    def test_topla(self):
        rk = os.path.join(self.film, "_RAPOR")
        oner = madde(); [oner.pop(k) for k in ("kaynak_kapi", "kaynak_rapor")]
        kapi.kaydet(rk, "V2", "B07", [{"madde": "kimlik", "plan": 41, "seviye": "HATA"}], kuyruk=[oner])
        kapi.kaydet(rk, "Z0", "P1", [{"madde": "Y16", "plan": 41, "seviye": "HATA"}], kuyruk=[dict(oner, plan=77)])  # kuyruk kapısı değil
        s = kuyruk.topla(self.film, E=E)
        self.assertEqual(len(s["eklenen"]), 1)
        m = kuyruk.acik_maddeler(self.film)[0]
        self.assertEqual((m["kaynak_kapi"], m["kaynak_rapor"], m["dilim"]), ("V2", "_RAPOR/V2_B07.json", "goruntu"))
        kuyruk.durum_degistir(self.film, m["id"], "tamam")
        s2 = kuyruk.topla(self.film, E=E)                                  # aynı rapor ikinci kez toplanmaz
        self.assertEqual((s2["eklenen"], s2["birlesen"]), ([], []))

    # --- eski klip ---------------------------------------------------------------------------------------------------
    def test_eski_klip_esiye_tasinir(self):
        sv = os.path.join(self.film, "SIRALI_VIDEO"); os.makedirs(sv)
        with open(os.path.join(sv, "041.mp4"), "wb") as f: f.write(b"eski")
        self.ekle(madde()); m = kuyruk.acik_maddeler(self.film)[0]
        m2 = kuyruk.durum_degistir(self.film, m["id"], "gonderildi", is_kimligi="9f2a1c")
        self.assertFalse(os.path.exists(os.path.join(sv, "041.mp4")))
        hedef = os.path.join(self.film, "_ESKI", "SIRALI_VIDEO", "041_d1.mp4")
        self.assertTrue(os.path.exists(hedef)); self.assertEqual(m2["eski_cikti"], "_ESKI/SIRALI_VIDEO/041_d1.mp4")
        self.assertEqual(m2["is_kimligi"], "9f2a1c")

    # --- YENIDEN_YAZ -------------------------------------------------------------------------------------------------
    def test_yeniden_yaz(self):
        m = {"konum": {"sahne": "S12", "plan": 121}, "kapi": "K0", "madde": "Y16", "kok_neden": "nesne_zipladi", "oneri": "fener sol elde kalsın"}
        s = kuyruk.yaz_ekle(self.film, [m, dict(m), dict(m, yazar="yonetmen", madde="Y17")], "A07c")
        self.assertEqual(s["eklenen"], ["YY-A07c-001", "YY-A07c-002"]); self.assertEqual(s["birlesen"], ["YY-A07c-001"])
        q = kuyruk.oku(self.film, kuyruk.YAZ)
        self.assertEqual(set(q["maddeler"][0]), {"id", "konum", "kapi", "madde", "kok_neden", "yazar", "oneri", "tur", "durum"})
        self.assertEqual(q["maddeler"][0]["yazar"], "sureklilik-denetcisi")       # kök nedenin sahibi
        for boz in ({"kok_neden": "yok"}, {"kapi": "XX"}, {"yazar": "betik:x.py"}, {"konum": {}}, {"konum": {"sahne": "S1"}}, {"oneri": ""}):
            self.assertTrue(kuyruk.yaz_ekle(self.film, [dict(m, **boz)], "A07c")["reddedilen"], boz)
        with self.assertRaises(kuyruk.KuyrukHatasi): kuyruk.yaz_ekle(self.film, [m], "P1")
        self.assertEqual(kuyruk.durum_degistir(self.film, "YY-A07c-001", "tamam", ad=kuyruk.YAZ)["durum"], "tamam")

    # --- MERDIVEN.md ---------------------------------------------------------------------------------------------------
    def test_merdiven_md(self):
        self.ekle(madde(), madde(plan=80, kok_neden="olcek_sicramasi", seviye="ORTA"))
        self.ekle(madde(plan=90, deneme=4))
        yol = kuyruk.merdiven_md(self.film)
        self.assertEqual(yol, os.path.join(self.film, "KURGU", "MERDIVEN.md"))
        with open(yol, encoding="utf-8") as f: t = f.read()
        self.assertIn("| 12 | Yer tutucu", t); self.assertIn("KK1", t)
        self.assertIn("plan 80", t); self.assertIn("önerilen basamaklar: 8, 2", t)
        self.assertIn("denenmemiş", t); self.assertIn("video:90", t)

    def test_ozet_md(self):
        self.ekle(madde(), madde(plan=60, tur="ses", kaynak_kapi="S2", kok_neden="veo_konusmadi", kredi_tahmini=12))
        self.assertIn("2 açık madde", kuyruk.ozet_md(self.film)); self.assertIn("kredi tahmini 36", kuyruk.ozet_md(self.film))

    def test_eski_liste_bicimi_okunur_bozuk_hata(self):
        os.makedirs(os.path.join(self.film, "KUYRUK"))
        with open(kuyruk.kuyruk_yolu(self.film), "w", encoding="utf-8") as f: json.dump([dict(madde(), id="YU-V2-1-001", durum="bekliyor")], f)
        self.assertEqual(len(kuyruk.acik_maddeler(self.film)), 1)
        with open(kuyruk.kuyruk_yolu(self.film), "w", encoding="utf-8") as f: f.write("{bozuk")
        with self.assertRaises(kuyruk.KuyrukHatasi): kuyruk.oku(self.film)

    # --- CLI ---------------------------------------------------------------------------------------------------------
    def test_cli(self):
        def cal(*a): return subprocess.run([sys.executable, ARAC, *a], capture_output=True, text=True, encoding="utf-8")
        p = os.path.join(self.film, "m.json")
        with open(p, "w", encoding="utf-8") as f: json.dump([madde()], f)
        r = cal("--film", self.film, "--ekle", p); self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        with open(p, "w", encoding="utf-8") as f: json.dump([madde(plan=7, sifir_kredi=None)], f)
        self.assertEqual(cal("--film", self.film, "--ekle", p).returncode, 3)
        self.assertEqual(cal("--film", self.film, "--listele").returncode, 0)
        self.assertEqual(cal("--film", self.film, "--merdiven-md").returncode, 0)
        mid = kuyruk.acik_maddeler(self.film)[0]["id"]
        self.assertEqual(cal("--film", self.film, "--durum", mid, "tamam").returncode, 0)
        self.assertEqual(cal("--film", self.film, "--durum", "YU-X-1-001", "tamam").returncode, 1)
        self.assertEqual(cal("--film", os.path.join(self.film, "yok"), "--listele").returncode, 2)
        self.assertEqual(cal("--film", "YOK_FILM", "--listele").returncode, 2)      # ad → ortak.yollar()["filmler"]
        self.assertEqual(cal("--film", self.film).returncode, 4)
        self.assertEqual(cal("--film", self.film, "--topla").returncode, 0)


if __name__ == "__main__":
    unittest.main()
