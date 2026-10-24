"""Görev defteri testi (TASARIM §1.1, §1.5, §5.5, §6.1 film.py v2, §6.10; [CM2] M3).

  - 30 kesme senaryosu: ajan ortası, aşamalı okumanın bölüm geçişi, betik ortası, kapı ortası, paralel grubun yarısı, kredili
    gönderimin hemen sonrası, kullanıcı eyleminin ortası, arka plan bildirimi gelmeden … Her birinde süreç "ölür" (kilit
    dosyası kalır), sonra film.py kurtar + sonraki ile sürer. Şart: %100 tamamlanma · biten görevin yeniden çalışması 0 ·
    kredili işin çift gönderimi 0 · FILM_DURUM görev dosyalarından aynen yeniden kurulur.
  - Tavan sonrası (§1.5, [SON] K-4): bir planı her turda HATA veren kaset fikstüründe hat 6'da kalmaz, plan durdu olur,
    rapor yazılır, film sonraki aşamaya geçer. Film düzeyi HATA'da 6 KAPI; yalnız KISMI'de hedef_alti.
  - Kapılar: Flow kilidi (7), disk (8), token (8), bütçe (5), bulut (4, D-45), kanca nabzı (1), kilit (8).
  - Gerçek kayıtla (hat/asamalar.py) A00–A18 sahte uçtan uca ve not turu (A16n).
Ağ yok, kredi yok, gerçek bekleme yok."""
import os, sys, json, io, glob, time, shutil, contextlib, unittest, unittest.mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak
import film
from hat import asamalar as HAT
from hat.asamalar import Asama, B, J, K, G, M, R, DURDU_SIFIR, DOKTOR, HEDEF_ALTI, BOLUMLER


class Oldu(BaseException):
    """Sürecin ölmesi (kill): Exception değildir, kilit bırakılmaz, durum yazılmaz."""


MINI = (
    HAT.asama("A00"),
    Asama("A01", "Konu kartı", "test", (G("konu", "A00", "00_KONU.md"),), ("_HIKAYE_ODASI/01_KONU_KARTI.json",),
          (R("KONU", "_RAPOR/KONU_t{tur}.json"),), None, "her_ikisi", 2,
          (M("ayni_sahip", "yeni eksen", "yapimci", "konu"), M("kapi6", "konu üretilemez")), None,
          (J("YK", "yapimci", "konu", grup=0, cikti=("CIKTI/kart.json", "CIKTI/not.md"),
             tasima=(("CIKTI/kart.json", "_HIKAYE_ODASI/01_KONU_KARTI.json"),)),
           B("KD", "hikaye_odasi.py", "konu-denetim", grup=1, cikti=("_RAPOR/KONU_t{tur}.json",), kapi="KONU"))),
    Asama("A03", "Öneriler", "test", (G("konu kartı", "A01", "_HIKAYE_ODASI/01_KONU_KARTI.json"),), ("_HIKAYE_ODASI/02_*.md",),
          (R("ONERI", "_RAPOR/ONERI_t{tur}.json"),), None, "her_ikisi", 1, (HEDEF_ALTI,), None,
          (J("HM", "hikaye-mimari", grup=0, adet=3, persona=("D", "S", "E"), cikti=("CIKTI/oneri.md",),
             tasima=(("CIKTI/oneri.md", "_HIKAYE_ODASI/02_oneri_{persona}.md"),)),
           B("OD", "hikaye_odasi.py", "oneri-denetim", grup=1, cikti=("_RAPOR/ONERI_t{tur}.json",), kapi="ONERI"))),
    Asama("A06", "Kâğıt seyirci", "test", (G("öneriler", "A03", "_HIKAYE_ODASI/02_oneri_D.md"),), ("HIKAYE.json",),
          (R("HS_KAGIT", "_RAPOR/HS_KAGIT_FILM_t{tur}.json", seyirci=True),), None, "her_ikisi", 2,
          (DOKTOR, M("kagit_urun", "kâğıt ürün")), None,
          (J("HS", "habersiz-seyirci", "kagit", grup=0, adet=3, persona=("A", "B", "C"), asamali=BOLUMLER,
             tasima=(("CIKTI/rapor.json", "_RAPOR/SEYIRCI/kagit_t{tur}/s{i}.json"),)),
           J("OE", "ozet-eslestirici", "ozet", grup=1, tasima=(("CIKTI/rapor.json", "_RAPOR/SEYIRCI/e_t{tur}.json"),)),
           B("ST", "seyirci_topla.py", grup=2, cikti=("_RAPOR/HS_KAGIT_FILM_t{tur}.json",), kapi="HS_KAGIT"),
           B("DV", "hikaye_odasi.py", "devir", grup=3, cikti=("HIKAYE.json",)))),
    Asama("A07b", "Planlar", "test", (G("HIKAYE", "A06", "HIKAYE.json"),), ("_YONETMEN/PLANLAR/*.json",),
          (R("Z0", "_RAPOR/Z0_SAHNE_t{tur}.json"),), None, "her_ikisi", 2,
          (M("ayni_sahip", "harita revizyonu", "yonetmen", "harita"), DURDU_SIFIR), None,
          (J("YP", "yonetmen", "plan", grup=0, adet=2, cikti=("CIKTI/plan.json",),
             tasima=(("CIKTI/plan.json", "_YONETMEN/PLANLAR/G{i}.json"),)),
           B("PS", "plan_denetim.py", "--sahne", grup=1, cikti=("_RAPOR/Z0_SAHNE_t{tur}.json",), kapi="Z0"))),
    Asama("A10b", "Telaffuz", "test", (G("HIKAYE", "A06", "HIKAYE.json"),), ("_RAPOR/S1a_telaffuz.json",),
          (R("S1a", "_RAPOR/S1a_telaffuz.json"),), "ai84", "her_ikisi", 1, (HEDEF_ALTI,), None,
          (B("TL", "ses_sec.py", "--telaffuz", grup=0, cikti=("_RAPOR/S1a_telaffuz.json",), kapi="S1a", kredili=True),
           B("SA", "seslendir.py", "--animatik", grup=1, kredili=True, cikti=("SESLER/animatik.json",)))),
    Asama("A10d", "Kartlar", "test", (G("HIKAYE", "A06", "HIKAYE.json"),), ("_RAPOR/KART_KAPISI.json",),
          (R("KART", "_RAPOR/KART_KAPISI.json"),), None, "her_ikisi", 1, (HEDEF_ALTI,), None,
          (K("GZ", "Paketi Gemini'ye ver, ZIP'i GELENLER'e koy.", {"tur": "dosya_var", "desen": "GELENLER/*KART*.zip"}, grup=0),
           B("KD", "kart_denetim.py", grup=1, cikti=("_RAPOR/KART_KAPISI.json",), kapi="KART"))),
    Asama("A14", "Video", "test", (G("kartlar", "A10d", "_RAPOR/KART_KAPISI.json"),), ("SIRALI_VIDEO/NNN.mp4",),
          (R("V2", "_RAPOR/V2_FILM_t{tur}.json"),), "flow", "yerel", 1, (DURDU_SIFIR,), None,
          (K("VG", "VIDEO_YARI_OTOMATIK.bat'a çift tıkla.", {"tur": "blok", "blok": "*"}, grup=0),
           B("VD", "video_denetim.py", grup=1, cikti=("_RAPOR/V2_FILM_t{tur}.json",), kapi="V2"))),
)


def oku(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def yaz(p, metin):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(metin)


def calistir(*a):
    b = io.StringIO()
    with contextlib.redirect_stdout(b): kod = film.main(list(a))
    try: r = json.loads(b.getvalue())
    except ValueError: r = b.getvalue()
    return kod, r


class Ortam(unittest.TestCase):
    kayit = MINI

    def setUp(self):
        self._eski = (HAT.ASAMALAR, HAT._DIZIN)
        HAT.ASAMALAR = self.kayit; HAT._DIZIN = {a.kod: a for a in self.kayit}; film._IMZA_DOSYA.clear()
        self.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "bulut"}); self.env.start()
        self.ad = "T_" + self._testMethodName[-40:]
        shutil.rmtree(os.path.join(_ortam.VERI, "FILMLER", self.ad), ignore_errors=True)
        kod, r = calistir("yeni", "--konu", "Ejderha yavrusunu saklayan avcı kadın", "--ad", self.ad, "--saglayici", "sahte")
        self.assertEqual(kod, 0, r)
        self.kok = r["yol"]; self.sayac = {}; self.kesmeler = []; self.ajan_kosu = []

    def tearDown(self):
        self.env.stop(); HAT.ASAMALAR, HAT._DIZIN = self._eski; film._IMZA_DOSYA.clear()
        hesap = os.path.join(_ortam.VERI, "HESAP", "FLOW_KILIDI.json")
        if os.path.exists(hesap): os.remove(hesap)

    # ---- kesme düzeneği
    def nokta(self, ad):
        self.sayac[ad] = self.sayac.get(ad, 0) + 1
        if (ad, self.sayac[ad]) in self.kesmeler: raise Oldu(f"{ad}#{self.sayac[ad]}")

    def nabiz(self):
        ortak.atomik_yaz(os.path.join(self.kok, "_GOREV", "KANCA_NABZI.json"), {"zaman": film.simdi(), "yazan": "test"})

    def k(self, *a): return calistir(*a, "--film", self.ad)

    def ajan(self, gid):
        """Gerçek ajan taklidi: CIKTI'yı yazar, aşamalı okumada bölüm bölüm ilerler, sonra SubagentStop'un yaptığı bitir."""
        g = oku(os.path.join(self.kok, "_GOREV", gid, "GOREV.json"))
        self.ajan_kosu.append(gid); self.nokta("ajan_basladi")
        d = os.path.join(self.kok, "_GOREV", gid)
        if g.get("asamali"):
            for i, b in enumerate(g["asamali"]["bolumler"]):
                film._metin_yaz(os.path.join(d, "CIKTI", f"rapor_{b}.md"), f"# {b}\nOZET | test\n")
                self.nokta("bolum_ortasi")
                if i + 1 < len(g["asamali"]["bolumler"]):
                    kod, r = self.k("asama-ilerlet", gid); self.assertEqual(kod, 0, r)
        zorunlu = [c for c in g["cikti"]["zorunlu"] if not c.startswith("CIKTI/rapor_")]
        for j, c in enumerate(zorunlu):
            p = os.path.join(d, c)
            if c.endswith(".json"): ortak.atomik_yaz(p, {"sonuc": "GEC", "ajan": g["ajan"]})
            else: film._metin_yaz(p, "test\n")
            if j == 0: self.nokta("ajan_yarim")
        self.nokta("ajan_bitir_once")
        kod, r = self.k("bitir", gid, "--kullanim", json.dumps({"girdi": 1000, "cikti": 100, "model": film.MODEL}))
        self.assertEqual(kod, 0, r)
        self.nokta("bildirim_yok")

    def surucu(self, maks=400):
        """Set amiri taklidi (SKILL.md §2 döngüsü). Ölünce film.py kurtar ve döngü baştan sürer."""
        for _ in range(maks):
            try:
                kod, r = self.k("sonraki")
                if r["tur"] == "bitti": return r
                if r["tur"] == "ajan":
                    self.nabiz()
                    ids = [g["id"] for g in r["gorevler"]]
                    kod2, r2 = self.k("basla", ",".join(ids)); self.assertEqual(kod2, 0, r2)
                    for n, gid in enumerate(ids):
                        self.ajan(gid)
                        if n == 0 and len(ids) > 1: self.nokta("paralel_yarim")
                elif r["tur"] == "betik":
                    for g in r["gorevler"]:
                        kod2, r2 = self.k("calis", g["id"]); self.assertIn(kod2, (0,), r2)
                elif r["tur"] == "kullanici_eylemi":
                    al = r["gorevler"][0]["algilama"]; self.nokta("kullanici_once")
                    if al["tur"] == "dosya_var":
                        p = os.path.join(self.kok, al["desen"].replace("*", "X")); yaz(p, "zip")
                    else:
                        yaz(os.path.join(self.kok, "KUNYE", "BLOK_HEPSI.bitti"), "1")
                    self.nokta("bekle_ortasi")
                    kod2, r2 = self.k("bekle", "--kullanici", r["gorevler"][0]["id"], "--kez", "1", "--aralik", "0")
                    self.assertEqual(kod2, 0, r2)
                else:
                    return r
            except Oldu:
                kod, r = self.k("kurtar"); self.assertEqual(kod, 0, r)
        self.fail("sürücü bitmedi")

    def gorevler(self):
        return [oku(p) for p in glob.glob(os.path.join(self.kok, "_GOREV", "*", "GOREV.json"))]

    def degismezler(self):
        gs = self.gorevler()
        anahtar = {}
        for g in gs: anahtar.setdefault(g["anahtar"], []).append(g)
        for an, ls in anahtar.items():
            bitti = [g for g in ls if g["durum"] == "bitti"]
            self.assertLessEqual(len(bitti), 1, f"{an}: iki kez bitti")
            if bitti:   # biten görevden sonra aynı iş için yeni görev açılmadı (yeniden çalışma 0)
                self.assertFalse([g for g in ls if g["deneme"] > bitti[0]["deneme"]], an)
        kosu = [s["gorev"] for s in film.jsonl_oku(os.path.join(self.kok, "_GOREV", "SAHTE_CALISMA.jsonl"))]
        self.assertEqual(len(kosu), len(set(kosu)), "aynı betik görevi iki kez koştu")
        self.assertEqual(len(self.ajan_kosu), len(set(self.ajan_kosu)), "aynı ajan görevi iki kez koştu")
        gonderim = {}
        for s in film.jsonl_oku(os.path.join(self.kok, "KREDI_DEFTERI.jsonl")): gonderim[s["madde"]] = gonderim.get(s["madde"], 0) + 1
        self.assertTrue(gonderim)
        for an, n in gonderim.items(): self.assertEqual(n, 1, f"{an}: kredili çift gönderim")
        self.assertFalse(os.path.exists(os.path.join(self.kok, "FILM.kilit")))
        # FILM_DURUM önbellektir: görev ve rapor dosyalarından aynen yeniden kurulur
        once = oku(os.path.join(self.kok, "FILM_DURUM.json"))
        os.remove(os.path.join(self.kok, "FILM_DURUM.json"))
        self.assertEqual(self.k("kurtar", "--yeniden-kur")[0], 0)
        sonra = oku(os.path.join(self.kok, "FILM_DURUM.json"))
        self.assertEqual({k: v["durum"] for k, v in once["asamalar"].items()}, {k: v["durum"] for k, v in sonra["asamalar"].items()})


SENARYOLAR = [
    [("gorev_kuruldu", 1)], [("gorev_kuruldu", 4)], [("gorev_kuruldu", 9)], [("tasima_sonra", 1)], [("tasima_sonra", 3)],
    [("bolum_acildi", 1)], [("bolum_acildi", 4)], [("calis_basladi", 1)], [("calis_basladi", 5)], [("calis_bitti", 2)],
    [("calis_bitti", 6)], [("cikis_kaydedildi", 1)], [("cikis_kaydedildi", 7)], [("sahte_gonderim_sonra", 1)],
    [("sahte_gonderim_sonra", 2)], [("ajan_basladi", 1)], [("ajan_basladi", 3)], [("ajan_yarim", 1)], [("ajan_yarim", 2)],
    [("ajan_bitir_once", 1)], [("paralel_yarim", 1)], [("bolum_ortasi", 2)], [("bildirim_yok", 1)], [("kullanici_once", 1)],
    [("bekle_ortasi", 2)], [("calis_basladi", 2), ("calis_basladi", 3)], [("ajan_basladi", 1), ("yenile_isaret_once", 1)],
    [("sahte_gonderim_sonra", 1), ("calis_basladi", 4)], [("gorev_kuruldu", 2), ("tasima_sonra", 2)],
    [("calis_bitti", 9), ("ajan_basladi", 6), ("bolum_acildi", 7)],
]


class KesmeSenaryolari(Ortam):
    def test_30_kesme_senaryosu(self):
        self.assertEqual(len(SENARYOLAR), 30)
        tetiklenen = 0
        for no, kesme in enumerate(SENARYOLAR, 1):
            with self.subTest(senaryo=no, kesme=kesme):
                if no > 1: self.setUp()
                self.kesmeler = kesme
                with unittest.mock.patch.object(film, "_kesme", self.nokta):
                    r = self.surucu()
                self.assertEqual(r["tur"], "bitti", r)
                tetiklenen += any(self.sayac.get(ad, 0) >= n for ad, n in kesme)
                self.degismezler()
                if no < len(SENARYOLAR): self.env.stop(); HAT.ASAMALAR, HAT._DIZIN = self._eski
        self.assertEqual(tetiklenen, 30, "her senaryoda en az bir kesme gerçekten olmalı")

    def test_kesilmeyen_film_biter_ve_durum_tutarli(self):
        with unittest.mock.patch.object(film, "_kesme", self.nokta): r = self.surucu()
        self.assertEqual(r["tur"], "bitti"); self.degismezler()
        st = oku(os.path.join(self.kok, "FILM_DURUM.json"))
        self.assertEqual(st["_surum"], 2); self.assertTrue(all(v["durum"] == "tamam" for v in st["asamalar"].values()))
        self.assertEqual(st["harcama"]["token"]["girdi"], 1000 * len(self.ajan_kosu))
        self.assertIn("A14", st["asamalar"]); self.assertIsNone(st["bekleyen_kullanici"])


class TavanSonrasi(Ortam):
    def kaset(self, kapi, icerik):
        ortak.atomik_yaz(os.path.join(self.kok, "_KASET", f"{kapi}.json"), icerik)

    def test_plan_her_turda_hata_durdu_olur_hat_surer(self):
        self.kaset("Z0", {"sonuc": "HATA", "hatalar": [{"madde": "eylem_adim", "plan": 2, "seviye": "HATA"}]})
        r = self.surucu()
        self.assertEqual(r["tur"], "bitti", r)                   # 6'da kalmadı
        tv = oku(os.path.join(self.kok, "_RAPOR", "TAVAN_A07b_s1.json"))
        self.assertEqual(tv["karar"], "durdu"); self.assertEqual(tv["durdu"], ["2"]); self.assertTrue(tv["hedef_alti"])
        gs = [g for g in self.gorevler() if g["asama"] == "A07b"]
        self.assertEqual(max(g["tur_no"] for g in gs), 4)       # 2 tur + harita revizyonu turu + sıfır kredi turu
        mb = sorted((g for g in gs if g["anahtar"].split("/")[3] == "MB"), key=lambda g: g["tur_no"])
        self.assertEqual([(g["ajan"], g["kip"]) for g in mb], [("yonetmen", "harita"), ("kurgucu", "sifir_kredi")])
        st = oku(os.path.join(self.kok, "FILM_DURUM.json"))
        self.assertEqual(st["asamalar"]["A07b"]["durum"], "kismi"); self.assertEqual(st["durdu_planlar"], ["2"])
        self.assertEqual(st["asamalar"]["A14"]["durum"], "tamam")
        self.assertIn("tur tavanı doldu", film._bayt(os.path.join(self.kok, "KARAR_DEFTERI.md")).decode("utf-8"))

    def test_film_duzeyi_hata_6_kapi(self):
        self.kaset("KONU", {"sonuc": "HATA", "hatalar": [{"madde": "cocuk_kahraman", "seviye": "HATA"}]})
        r = self.surucu()
        self.assertEqual(r["tur"], "kapi"); self.assertEqual(r["cikis_kodu"], 6)
        self.assertEqual(self.k("sonraki")[0], 6)
        self.assertEqual(oku(os.path.join(self.kok, "_RAPOR", "TAVAN_A01_s1.json"))["karar"], "kapi6")

    def test_seyirci_yalniz_kismi_hedef_alti(self):
        self.kaset("HS_KAGIT", {"sonuc": "KISMI", "hatalar": [{"madde": "genel_medyan", "olcu": 7.4, "seviye": "ORTA"}]})
        r = self.surucu()
        self.assertEqual(r["tur"], "bitti", r)
        self.assertEqual(oku(os.path.join(self.kok, "_RAPOR", "TAVAN_A06_s1.json"))["karar"],
                         "hedef_alti")
        self.assertTrue(os.path.exists(os.path.join(self.kok, "HIKAYE.json")))      # hat sürdü: devir koştu

    def test_seyirci_hata_kagit_urun(self):
        self.kaset("HS_KAGIT", {"sonuc": "HATA", "hatalar": [{"madde": "kritik", "seviye": "KRITIK"}]})
        r = self.surucu()
        self.assertEqual(r["cikis_kodu"], 6); self.assertIn("kâğıt ürün", r["kullaniciya"])

    def test_ikinci_turda_gecer(self):
        self.kaset("KONU", {"turlar": {"1": {"sonuc": "HATA", "hatalar": [{"madde": "x", "seviye": "HATA"}]}}})
        r = self.surucu()
        self.assertEqual(r["tur"], "bitti")
        self.assertFalse(os.path.exists(os.path.join(self.kok, "_RAPOR", "TAVAN_A01_s1.json")))
        a01 = [g for g in self.gorevler() if g["asama"] == "A01"]
        self.assertEqual(max(g["tur_no"] for g in a01), 2); self.assertTrue(all(g["merdiven"] is None for g in a01))


class Kapilar(Ortam):
    def ilerlet_kadar(self, kod):
        for _ in range(200):
            k, r = self.k("sonraki")
            if r.get("asama", "") and r["asama"].startswith(kod) or r["tur"] == "bitti": return k, r
            if r["tur"] == "ajan":
                self.nabiz(); self.k("basla", ",".join(g["id"] for g in r["gorevler"]))
                for g in r["gorevler"]: self.ajan(g["id"])
            elif r["tur"] in ("betik", "kullanici_eylemi"):
                for g in r["gorevler"]: self.assertEqual(self.k("calis", g["id"])[0], 0)
            else: return k, r
        self.fail("ulaşılamadı")

    def test_flow_kilidinde_7_ve_gorev_acilmaz(self):
        ortak.atomik_yaz(os.path.join(_ortam.VERI, "HESAP", "FLOW_KILIDI.json"), {"neden": "olagandisi"})
        k, r = self.ilerlet_kadar("A14")
        self.assertEqual((k, r["tur"]), (7, "kisit"))
        self.assertFalse([g for g in self.gorevler() if g["asama"] == "A14"])
        self.assertIn("Başka servise geçilmedi", r["kullaniciya"])

    def test_disk_kapisi_8(self):
        with unittest.mock.patch.object(film, "disk_bos_gb", lambda y: 1.0):
            k, r = self.k("sonraki")
        self.assertEqual(k, 8); self.assertIn("D'yi tak", r["kullaniciya"]); self.assertFalse(self.gorevler())

    def test_token_kapisi_8(self):
        self.ilerlet_kadar("A03")
        with unittest.mock.patch.object(film, "esik", lambda ad: 500 if ad == "film_token_tavan" else film.ESIK_VARSAYILAN.get(ad)):
            k, r = self.k("sonraki")
        self.assertEqual(k, 8); self.assertTrue(os.path.exists(os.path.join(self.kok, "TOKEN_PROJEKSIYON.md")))

    def test_butce_kapisi_5(self):
        kayit = (MINI[0], Asama("A01", "Bütçe", "test", (G("konu", "A00", "00_KONU.md"),), ("x",),
                                (R("BUT0", "_RAPOR/BUT0_FILM.json", butce=True),), None, "her_ikisi", 3, (HEDEF_ALTI,), None,
                                (B("B0", "kredi.py", "but0", cikti=("_RAPOR/BUT0_FILM.json",), kapi="BUT0"),)))
        HAT.ASAMALAR = kayit; HAT._DIZIN = {a.kod: a for a in kayit}
        ortak.atomik_yaz(os.path.join(self.kok, "_KASET", "BUT0.json"), {"sonuc": "HATA", "hatalar": [{"madde": "tavan"}]})
        k, r = self.ilerlet_kadar("A01")
        while r["tur"] == "betik":
            for g in r["gorevler"]: self.k("calis", g["id"])
            k, r = self.k("sonraki")
        self.assertEqual((k, r["tur"]), (5, "butce"))
        self.assertEqual(len([g for g in self.gorevler() if g["asama"] == "A01"]), 1)   # tur açılmadı, kısaltma yok

    def test_nabizsiz_ajan_baslamaz(self):
        k, r = self.ilerlet_kadar("A01")
        while r["tur"] != "ajan":
            for g in r["gorevler"]: self.k("calis", g["id"])
            k, r = self.k("sonraki")
        k2, r2 = self.k("basla", r["gorevler"][0]["id"])
        self.assertEqual(k2, 1); self.assertIn("nabz", r2["hata"])
        self.assertEqual(self.gorevler_id(r["gorevler"][0]["id"])["durum"], "hazir")

    def gorevler_id(self, gid): return oku(os.path.join(self.kok, "_GOREV", gid, "GOREV.json"))

    def test_bitir_eksik_cikti_1_model_sapmasi_yeniden(self):
        k, r = self.ilerlet_kadar("A01")
        while r["tur"] != "ajan":
            for g in r["gorevler"]: self.k("calis", g["id"])
            k, r = self.k("sonraki")
        gid = r["gorevler"][0]["id"]; self.nabiz(); self.k("basla", gid)
        k2, r2 = self.k("bitir", gid); self.assertEqual(k2, 1); self.assertIn("CIKTI/kart.json", r2["eksik"])
        d = os.path.join(self.kok, "_GOREV", gid, "CIKTI")
        ortak.atomik_yaz(os.path.join(d, "kart.json"), {}); film._metin_yaz(os.path.join(d, "not.md"), "x")
        k3, r3 = self.k("bitir", gid, "--kullanim", json.dumps({"model": "claude-baska"}))
        self.assertEqual(r3["durum"], "model_sapmasi")
        k4, r4 = self.k("sonraki")
        self.assertEqual(r4["tur"], "ajan"); self.assertNotEqual(r4["gorevler"][0]["id"], gid)
        self.assertEqual(self.gorevler_id(r4["gorevler"][0]["id"])["onceki"], gid)

    def test_sonraki_kisa_ve_kullanici_eylemi(self):
        k, r = self.ilerlet_kadar("A10d")
        while r["tur"] != "kullanici_eylemi":
            if r["tur"] == "ajan":
                self.nabiz(); self.k("basla", ",".join(g["id"] for g in r["gorevler"]))
                for g in r["gorevler"]: self.ajan(g["id"])
            else:
                for g in r["gorevler"]: self.k("calis", g["id"])
            k, r = self.k("sonraki")
        b = io.StringIO()
        with contextlib.redirect_stdout(b): film.main(["sonraki", "--film", self.ad])
        self.assertLessEqual(len(b.getvalue().strip()), film.SONRAKI_MAX_KR)
        self.assertEqual(k, 2); self.assertIn("GELENLER", r["kullaniciya"])
        gid = r["gorevler"][0]["id"]
        self.assertEqual(self.k("bekle", "--kullanici", gid, "--kez", "1", "--aralik", "0")[0], 8)
        yaz(os.path.join(self.kok, "GELENLER", "P_KART_1.zip"), "z")
        with unittest.mock.patch.object(film, "uyu", lambda s: None):
            self.assertEqual(self.k("bekle", "--kullanici", gid, "--kez", "3", "--aralik", "5")[0], 0)
        self.assertEqual(self.gorevler_id(gid)["durum"], "bitti")

    def test_bayat_girdi_asamayi_yeniden_acar(self):
        r = self.surucu(); self.assertEqual(r["tur"], "bitti")
        p = os.path.join(self.kok, "_HIKAYE_ODASI", "01_KONU_KARTI.json")
        ortak.atomik_yaz(p, {"degisti": True})
        k, r = self.k("sonraki")
        self.assertTrue(r["asama"].startswith("A03"), r)
        self.assertEqual(max(g["surum"] for g in self.gorevler() if g["asama"] == "A03"), 2)
        st = oku(os.path.join(self.kok, "FILM_DURUM.json"))
        self.assertEqual(st["aktif_asama"], "A03")

    def test_kilit(self):
        kilit = os.path.join(self.kok, "FILM.kilit")
        yaz(kilit, json.dumps({"pid": os.getppid(), "zaman": time.time(), "jeton": "x"}))
        self.assertEqual(self.k("sonraki")[0], 8)
        yaz(kilit, json.dumps({"pid": 2 ** 22 + 12345, "zaman": time.time(), "jeton": "x"}))   # ölü süreç
        self.assertNotEqual(self.k("sonraki")[0], 8)
        self.assertFalse(os.path.exists(kilit))

    def test_karar_ders_ozet_surus_goster(self):
        k, r = self.k("karar", "ekle", "Öneri B kazandı — jüri 4/5 B — A06'da 1 ek tur", "--asama", "A04", "--kaynak", "betik:puan_oku")
        self.assertEqual(k, 0)
        x = oku(os.path.join(self.kok, r["kayit"]))
        self.assertEqual((x["karar"], x["neden"], x["yanlissa_maliyeti"]), ("Öneri B kazandı", "jüri 4/5 B", "A06'da 1 ek tur"))
        self.assertIn("Öneri B", film._bayt(os.path.join(self.kok, "KARAR_DEFTERI.md")).decode("utf-8"))
        k, r = self.k("ders", "ekle", "--kapi", "G1", "--belirti", "fener sağ elde")
        self.assertEqual(k, 0)
        self.assertTrue(os.path.isfile(r["kayit"]))
        self.assertEqual(oku(r["kayit"])["belirti"], "fener sağ elde")
        self.assertEqual(self.k("ders", "ekle", "--belirti", "x", "--olay", "uydurma")[0], 1)
        self.assertEqual(self.k("ozet", "--kisa")[0], 0)
        self.assertEqual(calistir("ozet", "--film", "YOK_BOYLE_FILM")[0], 0)
        self.assertEqual(self.k("surus", "kapat", "--soru")[1]["otomatik_surus"]["neden"], "soru")
        self.assertFalse(oku(os.path.join(self.kok, "FILM_DURUM.json"))["otomatik_surus"]["acik"])
        self.assertTrue(self.k("surus", "ac")[1]["otomatik_surus"]["acik"])
        for ne in ("durum", "maliyet", "token", "neden-durdu", "ayar", "sozlesme", "karar", "plan-imza"):
            self.assertEqual(self.k("goster", ne)[0], 0, ne)
        self.assertEqual(self.k("goster", "pencere", "capcut")[0], 4)
        self.assertEqual(calistir("esitle")[0], 4)

    def test_ayar_maskeli(self):
        self.assertEqual(film.maskele({"telegram_token": "123:abc", "izinler": {"api_key": "x", "gece_flow": False}}),
                         {"telegram_token": "***", "izinler": {"api_key": "***", "gece_flow": False}})


class Bulut(unittest.TestCase):
    def test_d45_bulutta_film_acilmaz_konu_sorulmaz(self):
        with unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "bulut"}):
            os.makedirs(os.path.join(_ortam.VERI, "FILMLER"), exist_ok=True)
            aktif = os.path.join(_ortam.VERI, "FILMLER", "_AKTIF.json")
            yedek = film._bayt(aktif).decode("utf-8") if os.path.exists(aktif) else None
            try:
                if os.path.exists(aktif): os.remove(aktif)
                k, r = calistir("yeni", "--konu", "uzaylı çocuk")
                self.assertEqual(k, 4); self.assertIn("FILM_SETI.bat", r["kullaniciya"])
                k, r = calistir("sonraki"); self.assertEqual(k, 4); self.assertNotIn("konusu ne olsun", json.dumps(r))
                with unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "yerel"}):
                    k, r = calistir("sonraki"); self.assertEqual(k, 2); self.assertEqual(r["kullaniciya"], film.TEK_SORU)
            finally:
                if yedek is not None: yaz(aktif, yedek)

    def test_sarmalayici_mutlak_yolla_cagirir(self):
        import subprocess
        depo = os.path.dirname(os.path.dirname(ARACLAR))
        r = subprocess.run([sys.executable, os.path.join(depo, ".claude", "bin", "film.py"), "asamalar", "--json"],
                           capture_output=True, text=True, encoding="utf-8", cwd=_ortam.KOK)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(len(json.loads(r.stdout)), len(HAT.ASAMALAR))


class GercekKayit(Ortam):
    """hat/asamalar.py'nin gerçek kaydıyla A00–A18 sahte uçtan uca (bulutta testi olmayan aşamalar atlanır), sonra not turu."""
    kayit = HAT.ASAMALAR

    def test_uctan_uca_sahte_ve_not_turu(self):
        def tur():
            for _ in range(600):
                k, r = self.k("sonraki")
                if r["tur"] == "bitti": return r
                self.assertIn(r["tur"], ("ajan", "betik", "kullanici_eylemi"), r)
                for g in r["gorevler"]: self.assertEqual(self.k("calis", g["id"])[0], 0)
            self.fail("bitmedi")
        tur()
        st = oku(os.path.join(self.kok, "FILM_DURUM.json"))
        self.assertEqual(st["animatik"]["durum"], "ONAYLI")
        self.assertEqual(st["asamalar"]["A10a"]["not"], "sahte denemede atlandı")
        self.assertNotIn("A16n", st["asamalar"])
        k, r = self.k("notlar", "isle")
        self.assertIn(r["tur"], ("kullanici_eylemi", "betik")); self.assertTrue(r["asama"].startswith("A16n"))
        tur()
        self.assertEqual(oku(os.path.join(self.kok, "FILM_DURUM.json"))["asamalar"]["A16n"]["durum"],
                         "tamam")


# ---- birleştirme turu (TUM_ISTEKLER: film.py / hat/asamalar.py maddeleri) ------------------------------------------------
class YerelFilm(unittest.TestCase):
    """Sahte OLMAYAN film (sağlayıcı yok, ortam yerel): animatik kapısı gerçek imzayla sorulur."""
    def setUp(self):
        film._IMZA_DOSYA.clear()
        self.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "yerel"}); self.env.start()
        self.ad = "Y_" + self._testMethodName[-40:]
        shutil.rmtree(os.path.join(_ortam.VERI, "FILMLER", self.ad), ignore_errors=True)
        kod, r = calistir("yeni", "--konu", "Ejderha yavrusunu saklayan avcı kadın", "--ad", self.ad)
        self.assertEqual(kod, 0, r); self.kok = r["yol"]; self.d = film.Defter(self.kok)

    def tearDown(self): self.env.stop(); film._IMZA_DOSYA.clear()

    def k(self, *a): return calistir(*a, "--film", self.ad)

    def gorevler(self, asama=None):
        gs = [oku(p) for p in glob.glob(os.path.join(self.kok, "_GOREV", "*", "GOREV.json"))]
        return [g for g in gs if asama is None or g["asama"] == asama]

    def aktif_yap(self, kod):
        a = HAT.asama(kod)
        return unittest.mock.patch.object(film.Defter, "aktif", lambda d: (a, d.coz(a)))


class AnimatikKapisi(YerelFilm):
    """Kullanıcının kesin şartı: onaylı animatik (ANIMATIK/ONAY.json ONAYLI, imza güncel) yoksa video kredisi harcayan aşama
    (A13 BUT2, A14a, A14) görev AÇMAZ — sahte kipte değil, gerçek filmde."""
    def test_imzasiz_video_gorevi_acilmaz(self):
        self.assertFalse(self.d.sahte)
        for kod in ("A13", "A14a", "A14"):
            with self.aktif_yap(kod), unittest.mock.patch.object(film, "disk_bos_gb", lambda y: 500.0), \
                    unittest.mock.patch.object(film, "flow_kilitli", lambda: False):
                k, r = self.k("sonraki")
            self.assertEqual((k, r["tur"]), (6, "kapi"), (kod, r))
            self.assertIn("Animatik onaylı değil", r["kullaniciya"])
            self.assertEqual(self.gorevler(kod), [], kod)                      # hiçbir video görevi kurulmadı
        self.assertEqual(oku(os.path.join(self.kok, "FILM_DURUM.json"))["animatik"]["durum"], "bekliyor")

    def test_a12_bitti_demek_yetmez_imza_sart(self):
        # A12'nin defterde "tamam" görünmesi gerçek filmde yetmez (sahte kural yalnız sahte kipte)
        with unittest.mock.patch.object(film.Defter, "coz", lambda d, a: {"durum": "tamam"}):
            ok, neden = self.d.video_acilabilir()
        self.assertFalse(ok); self.assertIn("ONAYLI", neden)

    def test_bayat_ya_da_bozuk_imza_kapali(self):
        ortak.atomik_yaz(os.path.join(self.kok, "ANIMATIK", "ONAY.json"), {"durum": "ONAYLI", "imza": "uydurma", "tur": 1,
                                                                          "dosyalar": {}, "ozetler": {}})
        ok, neden = self.d.video_acilabilir()
        self.assertFalse(ok, neden)
        with unittest.mock.patch.dict(sys.modules, {"animatik_imza": None}):   # araç açılmazsa kapalı başarısız
            self.assertFalse(self.d.video_acilabilir()[0])

    def test_onayli_imzayla_acilir(self):
        import animatik_imza
        with self.aktif_yap("A13"), unittest.mock.patch.object(film, "disk_bos_gb", lambda y: 500.0), \
                unittest.mock.patch.object(animatik_imza, "dogrula", lambda f: (True, None, "abc")):
            k, r = self.k("sonraki")
            self.assertEqual(r["tur"], "betik", r)
            self.assertTrue(self.gorevler("A13"))
            st = film.durum_hesapla(self.d)
        self.assertEqual(st["animatik"]["durum"], "ONAYLI"); self.assertEqual(st["animatik"]["imza"], "abc")

    def test_sahte_kipte_a12_durumu(self):
        with unittest.mock.patch.object(film.Defter, "sahte", True), \
                unittest.mock.patch.object(film.Defter, "coz", lambda d, a: {"durum": "calisiyor"}):
            self.assertEqual(self.d.video_acilabilir(), (False, "A12 bitmedi"))


class VideoDongusu(YerelFilm):
    """film.py video (VIDEO_YARI_OTOMATIK.bat): blok_plani --imza → memmet --blok sonraki --onizleme <imza> --mod elle; 0 dışı
    kodda HEMEN durur (Flow uyarısında Memmet yeniden açılmaz)."""
    def kos(self, memmet_kodlari, bitir_sonra=None):
        cagri = []
        def arac(arac, args, yakala=False):
            cagri.append((arac, list(args)))
            if arac == "blok_plani.py": return unittest.mock.Mock(returncode=0, stdout="0123456789ab\n")
            n = sum(1 for a, _ in cagri if a == "memmet.py")
            if bitir_sonra and n >= bitir_sonra: yaz(os.path.join(self.kok, "KUNYE", "BLOK_HEPSI.bitti"), "1")
            return unittest.mock.Mock(returncode=memmet_kodlari[min(n, len(memmet_kodlari)) - 1])
        with unittest.mock.patch.object(film, "_arac_kos", arac), unittest.mock.patch.object(film, "flow_kilitli", lambda: False), \
                unittest.mock.patch.object(film.Defter, "video_acilabilir", lambda d: (True, None)):
            k, r = self.k("video", "--blok", "*")
        return k, r, cagri

    def test_flow_uyarisinda_bir_kez_ve_dur(self):
        k, r, cagri = self.kos([7])
        self.assertEqual(k, 7); self.assertIn("UYARI_GECTI", r["kullaniciya"])
        self.assertEqual([a for a, _ in cagri].count("memmet.py"), 1)            # yeniden açılmadı
        m = next(x for a, x in cagri if a == "memmet.py")
        self.assertEqual(m[1:], ["--blok", "sonraki", "--onizleme", "0123456789ab", "--mod", "elle"])

    def test_dogrulamada_dur(self):
        k, r, cagri = self.kos([0, 2])
        self.assertEqual(k, 2); self.assertEqual([a for a, _ in cagri].count("memmet.py"), 2)

    def test_bloklar_bitince_biter(self):
        k, r, cagri = self.kos([0, 0, 0], bitir_sonra=2)
        self.assertEqual(k, 0, r); self.assertEqual([a for a, _ in cagri].count("memmet.py"), 2)

    def test_imzasiz_animatik_ve_kilit(self):
        with unittest.mock.patch.object(film, "_arac_kos", lambda *a, **k: self.fail("araç çağrılmamalı")), \
                unittest.mock.patch.object(film, "flow_kilitli", lambda: False):
            k, r = self.k("video")
        self.assertEqual(k, 6); self.assertIn("Animatik", r["kullaniciya"])
        with unittest.mock.patch.object(film, "_arac_kos", lambda *a, **k: self.fail("araç çağrılmamalı")), \
                unittest.mock.patch.object(film, "flow_kilitli", lambda: True):
            self.assertEqual(self.k("video")[0], 7)

    def test_vg_gorevi_komutu_tasir(self):
        a = HAT.asama("A14"); s = next(x for x in a.gorevler if x.kod == "VG")
        g = self.d.gorev_kur(a, s, "A14@s1/t1/g1/VG/1", 1, 1, None, 1, None, None, "x")
        self.assertEqual(g["komut"][1:], ["video", "--blok", "*", "--film", self.kok])
        self.assertTrue(g["komut"][0].endswith(os.path.join(".claude", "bin", "film.py")))


class GirdiKopyasi(YerelFilm):
    def kur(self, kod, s, persona=None, kip=None, i=1, tur=1):
        a = HAT.asama(kod)
        return self.d.gorev_kur(a, s, f"{kod}@s1/t{tur}/g0/{s.kod}/{i}", 1, tur, None, i, kip, persona, "x")

    def test_kor_paket_klasoru_persona_ve_eslestirici(self):
        p = os.path.join(self.kok, "_KOR_PAKET", "kagit_ilk2dk_t1")
        gizli = "ANAH" + "TAR.json"
        for ad in ("ILK2DK_A.md", "ILK2DK_B.md", "P0/kare.jpg", "ESLESTIRICI/" + gizli, gizli): yaz(os.path.join(p, ad), "x")
        s = next(x for x in HAT.asama("A06").gorevler if x.kod == "IK")
        g = self.kur("A06", s, persona="A", kip="ilk2dk")
        gd = os.path.join(self.kok, "_GOREV", g["id"], "GIRDI")
        self.assertTrue(os.path.isfile(os.path.join(gd, "ILK2DK_A.md"))); self.assertTrue(os.path.isfile(os.path.join(gd, "P0", "kare.jpg")))
        self.assertFalse(os.path.exists(os.path.join(gd, "ILK2DK_B.md")))
        self.assertFalse(os.path.exists(os.path.join(gd, "ESLESTIRICI"))); self.assertFalse(os.path.exists(os.path.join(gd, gizli)))
        self.assertNotIn("DERSLER.md", " ".join(g["girdi"]))

    def test_eslestirici_kendi_paketini_ve_seyirci_raporunu_alir(self):
        gizli = "ANAH" + "TAR.json"
        yaz(os.path.join(self.kok, "_KOR_PAKET", "kagit_t1", "ESLESTIRICI", gizli), "{}")
        yaz(os.path.join(self.kok, "_RAPOR", "SEYIRCI", "kagit_t1", "s2_rapor.json"), "{}")
        s = next(x for x in HAT.asama("A06").gorevler if x.kod == "OE")
        g = self.kur("A06", s, i=2, kip="ozet")
        self.assertEqual(sorted(g["girdi"]), sorted(["GIRDI/" + gizli, "GIRDI/s2_rapor.json"]))

    def test_g1_kor_paketi_ornek_numarasiyla(self):
        yaz(os.path.join(self.kok, "_KOR_PAKET", "g1_t1", "2", "g01.jpg"), "x")
        yaz(os.path.join(self.kok, "_KOR_PAKET", "g1_t1", "2", "SORULAR.json"), "{}")
        yaz(os.path.join(self.kok, "_KOR_PAKET", "g1_t1", "1", "g09.jpg"), "x")
        s = next(x for x in HAT.asama("A11").gorevler if x.kod == "KG")
        g = self.kur("A11", s, i=2, kip="g1")
        self.assertEqual(sorted(g["girdi"]), ["GIRDI/SORULAR.json", "GIRDI/g01.jpg"])

    def test_son_surum_ve_glob(self):
        for n in (1, 3, 10, 102): yaz(os.path.join(self.kok, "_HIKAYE_ODASI", f"06_SENARYO_v{n}.json"), json.dumps({"n": n}))
        self.assertEqual(film.girdi_cozumle(self.kok, "son:_HIKAYE_ODASI/06_SENARYO_v*.json")[0][1], "06_SENARYO_v102.json")
        self.assertEqual(len(film.girdi_cozumle(self.kok, "_HIKAYE_ODASI/06_SENARYO_v*.json")), 4)
        self.assertNotEqual(self.d.dosya_imza(["_HIKAYE_ODASI/06_SENARYO_v*.json"]), self.d.dosya_imza(["_YOK/*.json"]))

    def test_yazar_sozlukleri_girdide(self):
        s = next(x for x in HAT.asama("A07b").gorevler if x.kod == "YP")
        yaz(os.path.join(self.kok, "_YONETMEN", "DILIM", "G1.json"), "{}")
        g = self.kur("A07b", s, kip="plan")
        for ad in ("GIRDI/G1.json", "GIRDI/fiil_sozlugu.json", "GIRDI/plan_sozlukleri.json", "GIRDI/ifade_sozlugu.json"):
            self.assertIn(ad, g["girdi"])

    def test_istem_md_esikleri_doldurur(self):
        s = next(x for x in HAT.asama("A03").gorevler if x.kod == "HM")
        g = self.kur("A03", s, persona="D")
        m = film._bayt(os.path.join(self.kok, "_GOREV", g["id"], "ISTEM.md")).decode("utf-8")
        self.assertIn("A03", m); self.assertNotIn("{{", m)
        import beceri_denetim
        def boz(*a, **k): raise beceri_denetim.SablonHatasi("bilinmeyen yer tutucu")
        with unittest.mock.patch.object(beceri_denetim, "sablon_doldur", boz):
            with self.assertRaises(film.Hata) as c: self.kur("A03", s, persona="S", i=2)
        self.assertEqual(c.exception.kod, film.HATA); self.assertIn("şablonu", str(c.exception))

    def test_karakter_adedi_son_senaryodan(self):
        yaz(os.path.join(self.kok, "_HIKAYE_ODASI", "06_SENARYO_v1.json"), json.dumps({"karakterler": {"a": {}, "b": {}}}))
        yaz(os.path.join(self.kok, "_HIKAYE_ODASI", "06_SENARYO_v2.json"), json.dumps({"karakterler": {"a": {}, "b": {}, "c": {}}}))
        self.assertEqual(self.d.adet("karakter"), 3)

    def test_degersiz_film_secenegine_film_yolu(self):
        gd = os.path.join(self.kok, "_GOREV", "A09-DN-001"); os.makedirs(gd, exist_ok=True)
        cagri = []
        with unittest.mock.patch.object(film.subprocess, "run", lambda a, **k: cagri.append(a) or unittest.mock.Mock(returncode=0)):
            self.d.betik_kos({"id": "A09-DN-001", "arac": "istem_denetim.py", "argumanlar": ["--film"]})
            self.d.betik_kos({"id": "A09-DN-001", "arac": "dilim.py", "argumanlar": ["--asama", "A07b"]})
        self.assertEqual(cagri[0][2:], ["--film", self.kok]); self.assertEqual(cagri[1][-2:], ["--film", self.kok])

    def test_evren_ozeti_ic_betik(self):
        self.assertEqual(self.d.ic_evren_ozeti({"id": "A01-EO-001"}), 0)
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "_HIKAYE_ODASI", "EVREN_OZETI.md")))


class Nabiz(YerelFilm):
    def nabiz(self, **k):
        ayar = os.path.join(ortak.DEPO_KOK, ".claude", "settings.json")
        sha = __import__("hashlib").sha1(film._bayt(ayar)).hexdigest() if os.path.isfile(ayar) else None
        n = {"zaman": film.simdi(), "yazan": "kanca.komut", "kanca_sha": {}, "ayar_sha": {"settings.json": sha}, "fork_kapali": True}
        n.update(k); ortak.atomik_yaz(os.path.join(self.kok, "_GOREV", "KANCA_NABZI.json"), n)

    def test_fork_kapali_ve_ayar_ozeti(self):
        self.nabiz(); self.assertTrue(self.d.nabiz_tamam())
        self.nabiz(fork_kapali=False); self.assertFalse(self.d.nabiz_tamam())
        self.nabiz(ayar_sha={"settings.json": "0" * 40}); self.assertFalse(self.d.nabiz_tamam())
        n = {"zaman": film.simdi(), "yazan": "kanca.komut"}                       # kancanın nabzında fork alanı yoksa geçersiz
        ortak.atomik_yaz(os.path.join(self.kok, "_GOREV", "KANCA_NABZI.json"), n); self.assertFalse(self.d.nabiz_tamam())


class Kaset(unittest.TestCase):
    """--saglayici kaset: ajan ve betik görevleri yalnız film.py ile (test yaması olmadan) kasetten yürür (§6.10, D-41)."""
    def setUp(self):
        film._IMZA_DOSYA.clear()
        self.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "bulut"}); self.env.start()
        self.ad = "KASET_" + self._testMethodName[-30:]
        shutil.rmtree(os.path.join(_ortam.VERI, "FILMLER", self.ad), ignore_errors=True)
        kod, r = calistir("yeni", "--konu", "ejderha yavrusunu saklayan avcı kadın", "--ad", self.ad, "--saglayici", "kaset")
        self.assertEqual(kod, 0, r)                                              # bulutta kaset de açılır (D-45)
        self.kok = r["yol"]
        shutil.copytree(os.path.join(os.path.dirname(ARACLAR), "FILMLER", "ORNEK_3_SAHNE", "_KASET"), os.path.join(self.kok, "_KASET"))

    def tearDown(self): self.env.stop()

    def k(self, *a): return calistir(*a, "--film", self.ad)

    def test_a00_a03_yalniz_film_py(self):
        asamalar = []
        with unittest.mock.patch.object(film, "disk_bos_gb", lambda y: 500.0):
            for _ in range(80):
                kod, r = self.k("sonraki")
                a = (r.get("asama") or "").split(" ")[0]
                if not asamalar or asamalar[-1] != a: asamalar.append(a)
                if a == "A04": break
                self.assertIn(r["tur"], ("ajan", "betik"), r)
                for g in r["gorevler"]:
                    kc, rc = self.k("calis", g["id"]); self.assertEqual(kc, 0, (g, rc))
        self.assertEqual(asamalar, ["A00", "A01", "A02", "A03", "A04"])
        gs = [oku(p) for p in glob.glob(os.path.join(self.kok, "_GOREV", "*", "GOREV.json"))]
        self.assertTrue(all(g["durum"] == "bitti" for g in gs if g["asama"] != "A04"))
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "_HIKAYE_ODASI", "02_oneri_X.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "_HIKAYE_ODASI", "02_LOGLINELAR.md")))
        b0 = next(g for g in gs if g["asama"] == "A01" and "-B0-" in g["id"])
        self.assertEqual(oku(os.path.join(self.kok, "_RAPOR", "BUT0_FILM.json"))["_uretim"]["gorev"], b0["id"])

    def test_kasetsiz_kredili_gercek_arac_kosmaz(self):
        d = film.Defter(self.kok)
        g = {"id": "A10b-TL-001", "asama": "A10b", "tur_no": 1, "anahtar": "A10b@s1/t1/g0/TL/1", "arac": "ses_sec.py",
             "argumanlar": ["--telaffuz"], "kredili": True, "persona": None, "kip": None}
        with self.assertRaises(film.Hata) as c: d.betik_kos(g)
        self.assertEqual(c.exception.kod, film.ORTAM)


class Birlestirme(Ortam):
    """MINI kayıt (sahte): bitir --gecersiz, bekle hatırlatma bildirimi, sıralı çift, koşullu görev, plato, hedef maddeleri."""
    def ilk(self, kod):
        for _ in range(200):
            k, r = self.k("sonraki")
            if (r.get("asama") or "").startswith(kod) or r["tur"] not in ("ajan", "betik", "kullanici_eylemi"): return k, r
            if r["tur"] == "ajan":
                self.nabiz(); self.k("basla", ",".join(g["id"] for g in r["gorevler"]))
                for g in r["gorevler"]: self.ajan(g["id"])
            else:
                for g in r["gorevler"]: self.assertEqual(self.k("calis", g["id"])[0], 0)
        self.fail("ulaşılamadı")

    def test_bitir_gecersiz_yeni_deneme(self):
        k, r = self.ilk("A01")
        while r["tur"] != "ajan":
            for g in r["gorevler"]: self.k("calis", g["id"])
            k, r = self.k("sonraki")
        gid = r["gorevler"][0]["id"]; self.nabiz(); self.k("basla", gid)
        k2, r2 = self.k("bitir", gid, "--gecersiz", "2 düzeltme sonrası şema HATA'sı")
        self.assertEqual((k2, r2["durum"]), (0, "gecersiz"))
        g = oku(os.path.join(self.kok, "_GOREV", gid, "GOREV.json"))
        self.assertEqual(g["durum"], "gecersiz"); self.assertIn("şema", g["gecersiz_neden"])
        k3, r3 = self.k("sonraki")
        yeni = r3["gorevler"][0]["id"]; self.assertNotEqual(yeni, gid)
        self.assertEqual(oku(os.path.join(self.kok, "_GOREV", yeni, "GOREV.json"))["onceki"], gid)

    def test_bekle_hatirlatmasi_bildirim(self):
        k, r = self.ilk("A10d")
        while r["tur"] != "kullanici_eylemi":
            for g in r["gorevler"]: self.k("calis", g["id"])
            k, r = self.k("sonraki")
        gid = r["gorevler"][0]["id"]; p = os.path.join(self.kok, "_GOREV", gid, "GOREV.json")
        g = oku(p); g["zaman"]["basla"] = "2020-01-01T00:00:00+00:00"; ortak.atomik_yaz(p, g)
        import bildirim
        with unittest.mock.patch.object(bildirim, "gonder") as gon:
            self.assertEqual(self.k("bekle", "--kullanici", gid, "--kez", "1", "--aralik", "0")[0], 8)
        gon.assert_called_once()
        self.assertEqual(gon.call_args[0][0], "kullanici_isi"); self.assertTrue(gon.call_args[0][1].startswith("Hatırlatma: "))
        self.assertEqual(gon.call_args[1]["anahtar"], gid)
        with unittest.mock.patch.object(bildirim, "gonder", side_effect=RuntimeError("ağ yok")):   # bildirim hatası beklemeyi bozmaz
            g = oku(p); g["hatirlatma"] = "2020-01-01T00:00:00+00:00"; ortak.atomik_yaz(p, g)
            self.assertEqual(self.k("bekle", "--kullanici", gid, "--kez", "1", "--aralik", "0")[0], 8)

    def test_sirali_cift_dilim_yenilenir(self):
        ortak.atomik_yaz(os.path.join(self.kok, "_YONETMEN", "DILIM.json"),
                         {"gruplar": [{"i": 1, "grup": "G1", "bagimli": None}, {"i": 2, "grup": "G2", "bagimli": "G1"}]})
        k, r = self.ilk("A07b")
        self.assertEqual(r["tur"], "ajan")
        self.assertEqual([g["id"].split("-")[1] for g in r["gorevler"]], ["YP"])   # G2, G1 bitmeden verilmez
        cagri = []
        orj = film.subprocess.run
        def run(a, **kw):
            if os.path.basename(a[1]) != "dilim.py": return orj(a, **kw)
            cagri.append(a); yaz(os.path.join(self.kok, "_YONETMEN", "DILIM", "G2.json"), '{"yenilendi": true}')
            return unittest.mock.Mock(returncode=0, stdout="")
        self.nabiz(); self.k("basla", r["gorevler"][0]["id"]); self.ajan(r["gorevler"][0]["id"])
        with unittest.mock.patch.object(film.subprocess, "run", run):
            k, r2 = self.k("sonraki")
        self.assertEqual(r2["tur"], "ajan"); gid = r2["gorevler"][0]["id"]
        self.assertEqual(len(cagri), 1); self.assertEqual(cagri[0][2:6], ["--asama", "A07b", "--grup", "2"])
        self.assertEqual(oku(os.path.join(self.kok, "_GOREV", gid, "GIRDI", "G2.json")), {"yenilendi": True})
        with unittest.mock.patch.object(film.subprocess, "run", run):
            self.k("sonraki")
        self.assertEqual(len(cagri), 1)                                          # bir kez

    def test_terminal_hedef_maddeleri_film_hatasi_degil(self):
        d = film.Defter(self.kok); a = HAT.asama("A06")
        son = {"sonuclar": ["HATA"], "hatalar": [{"madde": "genel_hedef", "hedef": True, "sahne": "P1", "seviye": "HATA"},
                                                 {"madde": "genel_hedef", "hedef": True, "sahne": "FILM", "seviye": "HATA"}]}
        t = d.terminal(a, "durdu", son, 0, 1, 2)
        self.assertEqual((t["karar"], t["durdu"]), ("durdu", []))
        son["hatalar"].append({"madde": "kritik", "seviye": "HATA"})
        self.assertEqual(d.terminal(a, "durdu", son, 0, 1, 2)["karar"], "kapi6")

    def test_plato_dogrudan_doktor(self):
        ortak.atomik_yaz(os.path.join(self.kok, "_KASET", "HS_KAGIT.json"),
                         {"sonuc": "KISMI", "plato": True, "hatalar": [{"madde": "genel_medyan", "seviye": "ORTA"}]})
        r = self.surucu(); self.assertEqual(r["tur"], "bitti", r)
        gs = [g for g in self.gorevler() if g["asama"] == "A06"]
        t2 = [g for g in gs if g["tur_no"] == 2]
        self.assertTrue(t2 and all(g["merdiven"] == 0 for g in t2))                # tur 2 olağan değil: doktor basamağı
        mb = [g for g in t2 if g["anahtar"].split("/")[3] == "MB"]
        self.assertEqual([(g["ajan"], g["kip"]) for g in mb], [("yapimci", "doktor")])
        self.assertTrue(mb[0].get("plato_basamagi"))

    def test_kosullu_grup_atlanir_ve_flow_reddi_onarim_acar(self):
        kayit = (MINI[0], Asama("A14", "Video", "test", (G("konu", "A00", "00_KONU.md"),), ("x",), (R("V2", "_RAPOR/V2_FILM_t{tur}.json"),),
                                None, "her_ikisi", 1, (HEDEF_ALTI,), None,
                                (HAT._flow_onarim(0),
                                 B("VD", "video_denetim.py", grup=1, cikti=("_RAPOR/V2_FILM_t{tur}.json",), kapi="V2"))))
        HAT.ASAMALAR = kayit; HAT._DIZIN = {a.kod: a for a in kayit}; film._IMZA_DOSYA.clear()
        r = self.surucu(); self.assertEqual(r["tur"], "bitti", r)
        gs = [g for g in self.gorevler() if g["asama"] == "A14"]
        atla = [g for g in gs if "-ATLA-" in g["id"]]
        self.assertEqual(len(atla), 1); self.assertEqual(atla[0]["durum"], "bitti")
        self.assertFalse([g for g in gs if "-FO-" in g["id"]])
        d = film.Defter(self.kok); a = HAT.asama("A14"); s = a.gorevler[0]
        self.assertFalse(d.kosul_tamam(a, s))
        ortak.atomik_yaz(os.path.join(self.kok, "_RAPOR", "FLOW_B01.json"),
                         {"kapi": "FLOW", "hatalar": [{"madde": "filtre_red", "plan": 4, "seviye": "HATA"}]})
        self.assertTrue(d.kosul_tamam(a, s))


if __name__ == "__main__":
    unittest.main()
