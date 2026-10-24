"""Animatik testi (TASARIM §9 adım 14 / PR-10: test_kurgu animatik senaryoları; §6.10; [KU2] §4.6.3 #3, #6, #9, #10, #11).

  - T1: TTS süresi plan süresine girer, kare sayıları tamsayı, sapma ve yer tutucu ölçülür, eylem şeridi adsız.
  - Render: animatik süresi = T1 toplamı ±1 kare; görseli eksik plan yer tutucuyla; plan başına önbellek (ikinci render yeniden kodlamaz).
  - Kör paket izleme kipleri: 2 × A + 1 × B persona, P0–P3 bölümleri, parça kesimi (240–300 sn, sahne sınırı), sızıntı 0 (amaç,
    ekranda_bilgi, kadraj etiketi yok), ad maskeleme, ilk 2 dk paketi, kesici paketi (KESME_GIRDI, ekranda_bilgi yok).
  - seyirci_topla izleme ekleri: G1 GEÇ olmayan kare kapıyı kapatır (D-14); izleyici/dinleyici BAYRAK (ölçülemezse ÖLÇÜLEMEDİ).
  - `animatik: ONAYLI` imzası: koşullar sağlanmadan imza yok; imzasız/bayat imzada video görevi açılmaz; T1 değişince bayat.
  - kurgu_uygula: --kuru kilitli alan, etkili planın sırası, B9, hız, 0 kredi kuralı HATA; --uygula yeni sürüm + kalıcı katman.
  - kurgu_denetim --kesme-simule: kurulum götüren kesme HATA ve paydaya girmez; uygulama oranı (≥ %50) zorlanır.
  - bildirim: sahte kanal, 30 dk tekrar bastırma, saatte ≤ 12, ACİL tavanı aşar, gizli bilgi maskelenir.
  - izleyici açılma kuralı (D-19): anahtar yok → kapalı; ücretsiz katman → açık; ücretli + izin yok → kapalı; video girişi yok → kapalı.
"""
import os, sys, re, json, glob, shutil, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak
import _animatik_fikstur as fik
import zaman_cizelgesi_t1 as t1
import kor_paket_izleme as kpi
import kurgu_uygula as ku
import kurgu_denetim as kd
import animatik_imza as ai
import seyirci_topla as st
import bildirim

FFMPEG = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))
BOYUT = (320, 180)


def jo(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def jy(p, v):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: json.dump(v, f, ensure_ascii=False)


def oku(p):
    with open(p, encoding="utf-8") as f: return f.read()


def metinler(kok):
    out = {}
    for dp, _, fs in os.walk(kok):
        for f in fs:
            if f.endswith(".md"):
                with open(os.path.join(dp, f), encoding="utf-8") as h: out[os.path.relpath(os.path.join(dp, f), kok)] = h.read()
    return out


def seyirci_raporlari(film, kip="animatik", tur=1, genel=8, personalar=("A", "A", "B")):
    d = os.path.join(film, "_RAPOR", "SEYIRCI", "%s_t%d" % (kip, tur))
    for i, per in enumerate(personalar, 1):
        jy(os.path.join(d, "s%d_rapor.json" % i), {"kip": kip, "tur": tur, "seyirci": i, "persona": per,
           "puanlar": {"anlasilirlik": 8, "akicilik": 8, "merak": 8, "duygu": 8, "ritim": 8, "ilk30": 8, "GENEL": genel},
           "kopukluklar": [], "acik_sorular": [], "ozet_parti": "x", "devam": True})
        jy(os.path.join(d, "e%d_eslesme.json" % i), {"olgular": [{"id": "o01", "karar": "bulundu"}]})
        jy(os.path.join(film, "_RAPOR", "SEYIRCI", "%s_ilk2dk_t%d" % (kip, tur), "s%d_rapor.json" % i),
           {"kip": "ilk2dk", "tur": tur, "persona": per, "puanlar": {"GENEL": 8}, "kopukluklar": [], "acik_sorular": [],
            "ozet_parti": "x", "devam": True, "ilk2dk_devam": True})


class Temel(unittest.TestCase):
    def setUp(self):
        self.kok = tempfile.mkdtemp(prefix="anim_", dir=_ortam.KOK)
        self.film = os.path.join(self.kok, "FILM")
        os.environ["YZ_FILM_IZLEYICI"] = "sahte"; os.environ["YZ_FILM_BILDIRIM"] = "sahte"
        os.environ.pop("YZ_FILM_GOREV", None); os.environ.pop("GEMINI_API_KEY", None)

    def kur(self, **k): return fik.kur(self.film, **k)

    def render(self, tur=1):
        import kurgu_render as kr
        return kr.animatik(self.film, tur, BOYUT)


class T1Testi(Temel):
    def test_tts_sure_kare_ve_yer_tutucu(self):
        self.kur(gorsel=(1, 2, 3, 4, 6))
        p = t1.t1_kur(self.film, 1)
        pl = {x["plan"]: x for x in p["planlar"]}
        # plan 2: konuşma başı 0,5 + TTS 3,1 + pay 0,2 = 3,8 → 91 kare (T0 3,0'dan uzar)
        self.assertEqual(pl[2]["kare"], 91); self.assertGreater(pl[2]["sapma_oran"], 0.25)
        self.assertEqual(pl[4]["sure"], 2.5)                         # TTS kısa: diyalog plan tipinin alt sınırı korunur
        for x in p["planlar"]: self.assertEqual(x["kare"], round(x["sure"] * 24))
        self.assertEqual(p["toplam_kare"], sum(x["kare"] for x in p["planlar"]))
        self.assertEqual(pl[5]["goruntu"]["tur"], "yer_tutucu"); self.assertEqual(p["olcumler"]["yer_tutucu_planlar"], [5])
        self.assertEqual(pl[2]["goruntu"]["bitis_dosya"], "SIRALI_GORSEL/002_bitis.jpg")
        d = {x["replik"]: x for x in p["diyalog"]}
        self.assertAlmostEqual(d["R0001"]["cizelge_bas"], pl[2]["cizelge_bas"] + 0.5, places=3)
        for x in p["planlar"]:
            for s in x["serit"]: self.assertNotRegex(s["metin"], r"(?i)\b(mara|voss|captain|huntress)\b")
        sap = jo(os.path.join(self.film, "_RAPOR", "SAPMA_T1.json"))
        self.assertIn(2, [x["plan"] for x in sap["planlar"] if x["seviye"] == "BAYRAK"])
        self.assertTrue(os.path.isfile(os.path.join(self.film, "KURGU", "surumler", "KURGU_PLANI_T1_v1.json")))

    def test_tts_yoksa_olculemedi(self):
        self.kur(tts=False)
        p = t1.t1_kur(self.film, 1)
        z = jo(os.path.join(self.film, "_RAPOR", "ZAMAN_T1.json"))
        self.assertTrue(any(o["madde"] == "tts_yok" and o["seviye"] == "OLCULEMEDI" for o in z["olcumler_liste"]))
        self.assertEqual({x["plan"]: x["sure"] for x in p["planlar"]}[2], 3.0)

    def test_v1_sahneler_ortam(self):
        os.makedirs(self.film); jy(os.path.join(self.film, "SAHNELER.json"), {"sahneler": [{"no": 1}]})
        self.assertEqual(t1.main(["--asama", "animatik", "--film", self.film]), 4)


@unittest.skipUnless(FFMPEG, "ffmpeg yok")
class RenderTesti(Temel):
    def test_sure_t1_artieksi_bir_kare_ve_onbellek(self):
        self.kur(gorsel=(1, 2, 3, 4, 6))
        p = t1.t1_kur(self.film, 1)
        r = self.render()
        self.assertLessEqual(abs(r["kare_olculen"] - p["toplam_kare"]), 1)
        self.assertNotEqual(r["sonuc"], "HATA")
        self.assertEqual(r["onbellek"], {"isabet": 0, "yeni": 6})
        self.assertIn("ses_yok", [b["madde"] for b in r["bayraklar"]])
        self.assertIn(5, r["yer_tutucu_planlar"])
        self.assertTrue(os.path.isfile(os.path.join(self.film, "ANIMATIK", "ISITSEL_DOKUM.md")))
        r2 = self.render()
        self.assertEqual(r2["onbellek"], {"isabet": 6, "yeni": 0})
        self.assertLessEqual(abs(r2["kare_olculen"] - p["toplam_kare"]), 1)

    def test_bilgi_paketi(self):
        self.kur(); t1.t1_kur(self.film, 1); self.render()
        import kurgu_render as kr
        b = kr.bilgi_paketi(self.film, "animatik")
        k = os.path.join(self.film, b["klasor"])
        for f in ("animatik_v1.mp4", "OKU_BENI.txt", "PAKET.json", "ISITSEL_DOKUM.md"): self.assertTrue(os.path.isfile(os.path.join(k, f)), f)
        self.assertEqual(sorted(b["icerik"]["ses_kadrosu"]), ["mara.wav", "voss.wav"])
        sahte = os.path.join(_ortam.VERI, "HESAP", "BILDIRIM_SAHTE.jsonl")
        self.assertTrue(os.path.isfile(sahte))


class KorPaketTesti(Temel):
    def paket(self, kip="animatik"):
        os.environ["YZ_FILM_FILM"] = self.film
        try: return kpi.main(["--kip", kip, "--tur", "1", "--film", self.film])
        finally: os.environ.pop("YZ_FILM_FILM", None)

    def test_persona_bolum_sizinti_maske(self):
        self.kur(gorsel=(1, 2, 3, 4, 6)); t1.t1_kur(self.film, 1)
        self.assertEqual(self.paket(), 0)
        kok = os.path.join(self.film, "_KOR_PAKET", "animatik_t1")
        m = jo(os.path.join(kok, "PAKET.json"))
        self.assertEqual(m["klasorler"], {"A": "A", "B": "A", "C": "B"})
        self.assertEqual(m["sizinti"], {"yasak_alan": 0, "ad": 0, "izleme_yasak": 0})
        for b in ("P0", "P1", "P2", "P3"): self.assertTrue(os.path.isfile(os.path.join(kok, "A", b, "IZLE.md")))
        self.assertTrue(glob.glob(os.path.join(kok, "A", "P0", "sayfa_*.jpg")))
        self.assertIn("Persona B", oku(os.path.join(kok, "C", "P0", "IZLE.md")))
        hepsi = metinler(kok); hepsi.update(metinler(os.path.join(self.film, "_KOR_PAKET", "animatik_ilk2dk_t1")))
        for ad, t in hepsi.items():
            self.assertNotIn("SIZINTI", t, ad)
            self.assertNotRegex(t.lower(), r"orta yakın plan|plan tipi|kesme tipi", ad)
        # ad: R0002'de duyulana kadar tırnak dışında "Mara" yok
        izle = oku(os.path.join(kok, "A", "P0", "IZLE.md"))
        once = izle.split("Mara! Open the door.")[0]
        self.assertNotRegex(re.sub(r"\"[^\"]*\"", "", once), r"\bMara\b")
        self.assertIn("[ekranda, woman in a green cloak]", izle)
        ik = oku(os.path.join(self.film, "_KOR_PAKET", "animatik_ilk2dk_t1", "ILK2DK_A.md"))
        self.assertIn("BAŞLIK: The Hidden Hatchling", ik); self.assertNotIn("Mara holds", ik)
        self.assertTrue(os.path.isfile(os.path.join(kok, "ESLESTIRICI", "ANAHTAR.json")))

    def test_bolumleme_parca(self):
        ps, t = [], 0.0
        sahneler = [("S01", 1, 4, 30.0), ("S02", 1, 5, 30.0), ("S03", 1, 4, 30.0), ("S04", 1, 4, 30.0), ("S05", 2, 2, 40.0), ("S06", 2, 12, 30.0)]
        no = 1
        for sg, parti, n, s in sahneler:
            for _ in range(n):
                ps.append({"plan": no, "parti": parti, "sahne_grubu": sg, "sure": s, "cizelge_bas": t}); t += s; no += 1
        b = kpi.bolumle({"planlar": ps})
        self.assertEqual(b[0][0], "P0"); self.assertTrue(all(p["cizelge_bas"] < 120 for p in b[0][2]))
        for bol, parca, pl in b[1:]:
            top = sum(p["sure"] for p in pl)
            if len({p["sahne_grubu"] for p in pl}) > 1: self.assertLessEqual(top, 300 + 1e-6)
            self.assertNotEqual(bol, "P0")
        tum = [p["plan"] for _, _, pl in b for p in pl]
        self.assertEqual(tum, [p["plan"] for p in ps])
        s06 = [x for x in b if any(p["sahne_grubu"] == "S06" for p in x[2])]
        self.assertGreaterEqual(len(s06), 2)                 # 360 sn'lik tek sahne plan sınırından bölündü
        self.assertTrue(all(sum(p["sure"] for p in x[2]) <= 300 for x in s06))

    def test_kesici_paketi(self):
        self.kur(); t1.t1_kur(self.film, 1)
        self.assertEqual(self.paket("kesici"), 0)
        kok = os.path.join(self.film, "_KOR_PAKET", "kesici_t1")
        g = oku(os.path.join(kok, "KESME_GIRDI.md"))
        self.assertIn("| 1 | #1 | S01 |", g); self.assertIn("en çok 10 planı", g)
        for ad, t in metinler(kok).items(): self.assertNotIn("SIZINTI", t, ad)
        self.assertTrue(glob.glob(os.path.join(kok, "SAYFALAR", "sayfa_*.jpg")))

    def test_t1_yoksa_ortam(self):
        self.kur()
        self.assertEqual(self.paket(), 4)


@unittest.skipUnless(FFMPEG, "ffmpeg yok")
class KapiVeImzaTesti(Temel):
    def hazirla(self, gorsel):
        self.kur(gorsel=gorsel); t1.t1_kur(self.film, 1); self.render(); seyirci_raporlari(self.film)

    def test_g1_eksik_kapi_kapanir_imza_yok(self):
        self.hazirla((1, 2, 3, 4, 6))
        k = st.topla(self.film, "animatik", 1)
        r = jo(os.path.join(self.film, "_RAPOR", "HS_ANIMATIK_FILM_t1.json"))
        self.assertEqual(r["sonuc"], "HATA"); self.assertFalse(r["kapi_saglandi"])
        self.assertIn("g1_tamam_degil", [h["madde"] for h in r["hatalar"]])
        self.assertFalse(os.path.exists(ai.onay_yolu(self.film)))
        ok, neden, _ = ai.dogrula(self.film); self.assertFalse(ok)
        self.assertFalse(ai.video_acilabilir(self.film)[0])
        self.assertIn("yz_kusuru", [b["madde"] for b in r["bayraklar"]])       # sahte izleyici bulgusu BAYRAK
        self.assertIn("ses_bulgusu", [b["madde"] for b in r["bayraklar"]])

    def test_kapi_saglaninca_imza_ve_bayatlama(self):
        self.hazirla((1, 2, 3, 4, 5, 6))
        k = st.topla(self.film, "animatik", 1)
        r = jo(os.path.join(self.film, "_RAPOR", "HS_ANIMATIK_FILM_t1.json"))
        self.assertTrue(r["kapi_saglandi"]); self.assertIn(r["sonuc"], ("GEC", "BAYRAK"))
        ok, neden, imza = ai.dogrula(self.film); self.assertTrue(ok, neden)
        self.assertEqual(ai.durum(self.film)["durum"], "ONAYLI")
        self.assertTrue(ai.video_acilabilir(self.film)[0])
        # yeni T1 sürümü → imza bayat, video görevi açılmaz
        t1.t1_kur(self.film, 2)
        ok, neden, _ = ai.dogrula(self.film); self.assertFalse(ok); self.assertIn("yeni T1", neden)
        self.assertEqual(ai.main(["--dogrula", "--film", self.film]), 1)

    def test_imza_kosullari_bagimsiz(self):
        self.hazirla((1, 2, 3, 4, 5, 6))
        ok, s = ai.imzala(self.film, 1)                      # seyirci raporu yok → imza yok
        self.assertFalse(ok); self.assertTrue(any("HS_ANIMATIK" in n for n in s["nedenler"]))
        st.topla(self.film, "animatik", 1)
        self.assertTrue(ai.dogrula(self.film)[0])
        with open(os.path.join(self.film, "ANIMATIK", "animatik_v1.mp4"), "ab") as f: f.write(b"0")
        ok, neden, _ = ai.dogrula(self.film); self.assertFalse(ok); self.assertIn("video", neden)

    def test_sahte_film_a12_durumu(self):
        self.assertTrue(ai.video_acilabilir(self.kok, sahte=True, a12_durum="kismi")[0])
        self.assertFalse(ai.video_acilabilir(self.kok, sahte=True, a12_durum="calisiyor")[0])

    def test_izleyici_anahtarsiz_olculemedi(self):
        os.environ.pop("YZ_FILM_IZLEYICI", None)
        self.hazirla((1, 2, 3, 4, 5, 6))
        st.topla(self.film, "animatik", 1)
        r = jo(os.path.join(self.film, "_RAPOR", "HS_ANIMATIK_FILM_t1.json"))
        iz = [b for b in r["bayraklar"] if b["madde"] in ("izleyici", "dinleyici")]
        self.assertEqual(len(iz), 2); self.assertTrue(all(b.get("olculemedi") for b in iz))
        self.assertNotEqual(r["sonuc"], "GEC")                # ÖLÇÜLEMEDİ asla GEÇ değildir


class KurguUygulaTesti(Temel):
    def setUp(self):
        super().setUp(); self.kur(); t1.t1_kur(self.film, 1)

    def kararlar(self, islemler, tur=1):
        p = os.path.join(self.film, "KURGU", "KURGU_KARARLARI_T1_t%d.json" % tur); jy(p, {"asama": "T1", "tur": tur, "islemler": islemler}); return p

    def hatalar(self, islemler):
        kod, s = ku.calistir(self.film, "T1", 1, self.kararlar(islemler), kuru=True)
        return kod, [h["neden"] for h in s["hatalar"]]

    def test_kuru_hatalar(self):
        k, h = self.hatalar([{"op": "uc", "bulgu": "s1:k1", "kok_neden": "olu_sure"}]); self.assertEqual(k, 1); self.assertTrue(h)
        k, h = self.hatalar([{"op": "kirp", "plan": 1, "sure": 2.5, "bulgu": "s1:k1"}]); self.assertTrue(any("kok_neden" in x for x in h))
        k, h = self.hatalar([{"op": "sira", "sahne_grubu": "S01", "yeni_sira": [2, 1, 3], "kok_neden": "konum_plani_gec", "bulgu": "s1"}])
        self.assertTrue(any("durumu değiştiriyor" in x for x in h))
        k, h = self.hatalar([{"op": "sira", "sahne_grubu": "S02", "yeni_sira": [4, 6, 5], "kok_neden": "konum_plani_gec", "bulgu": "s1"}])
        self.assertEqual((k, h), (0, []))
        k, h = self.hatalar([{"op": "ekran_disi", "replik": "R0001", "uzerine_plan": 4, "kok_neden": "konusan_belirsiz", "bulgu": "s2"}])
        self.assertTrue(any("B9" in x for x in h))
        k, h = self.hatalar([{"op": "hiz", "plan": 2, "hiz": 1.1, "kok_neden": "uzun_plan", "bulgu": "s2"}])
        self.assertTrue(any("diyaloglu" in x for x in h))
        k, h = self.hatalar([{"op": "yeniden_cek", "plan": 3, "kok_neden": "nesne_zipladi", "bulgu": "s3", "sifir_kredi": {"basamaklar": [1]}}])
        self.assertTrue(any("0 kredi" in x for x in h))
        k, h = self.hatalar([{"op": "ayna", "plan": 1, "kok_neden": "eksen_180", "bulgu": "s1"}]); self.assertTrue(any("ayna yasak" in x for x in h))
        plan, yol, _ = t1.plan_oku(self.film, "T1")
        plan["planlar"][0]["goruntu"]["kullanim_kaynak"] = "kullanici"; jy(yol, plan)
        k, h = self.hatalar([{"op": "kirp", "plan": 1, "sure": 2.5, "kok_neden": "olu_sure", "bulgu": "s1"}])
        self.assertTrue(any("kilitli" in x for x in h))

    def test_uygula_surum_ve_kalici_katman(self):
        kod, s = ku.calistir(self.film, "T1", 1, self.kararlar([
            {"op": "kirp", "plan": 6, "sure": 2.0, "kok_neden": "olu_sure", "bulgu": "s1:k2"},
            {"op": "kart", "kart_tur": "yer_zaman", "metin": "The Cabin — Night", "plan": 1, "kok_neden": "mekan_belirsiz", "bulgu": "s1:k1"},
            {"op": "yeni_plan_iste", "araya": [3, 4], "gereksinim": "kadın kapıya yürür", "kok_neden": "hikaye_adimi_ekranda_yok", "bulgu": "s1:k3"}]))
        self.assertEqual(kod, 0, s["hatalar"])
        v2 = jo(os.path.join(self.film, "KURGU", "surumler", "KURGU_PLANI_T1_v2.json"))
        self.assertEqual({p["plan"]: p["sure"] for p in v2["planlar"]}[6], 2.0)
        self.assertEqual(v2["toplam_kare"], sum(p["kare"] for p in v2["planlar"]))
        self.assertTrue(os.path.isfile(os.path.join(self.film, "KURGU", "ISTEKLER_T1_t1.json")))
        yy = jo(os.path.join(self.film, "KUYRUK", "YENIDEN_YAZ.json")); self.assertTrue(yy["maddeler"])
        p3 = t1.t1_kur(self.film, 3)                          # yeniden kurulumda kalıcı işlemler yeniden uygulanır
        self.assertEqual({p["plan"]: p["sure"] for p in p3["planlar"]}[6], 2.0)
        self.assertTrue(any(k.get("metin") == "The Cabin — Night" for k in p3["kartlar"]))

    def test_kisa_karar_bicimi(self):
        p = os.path.join(self.film, "KURGU", "KURGU_KARARLARI_T1_t1.json")
        jy(p, {"gorev": "x", "kip": "duzelt", "kararlar": [{"madde": "s1:k1", "tur": "kirp", "plan": 6, "deger": 2.5, "kok_neden": "olu_sure"}]})
        kod, s = ku.calistir(self.film, "T1", 1, p)
        self.assertEqual(kod, 0, s["hatalar"])


class KesmeSimuleTesti(Temel):
    def setUp(self):
        super().setUp(); self.kur(); t1.t1_kur(self.film, 1)

    def test_kurulum_goturen_kesme_hata_oran_zorlanir(self):
        jy(os.path.join(self.film, "KURGU", "KESME_T1.json"), {"kesmeler": [
            {"konum": {"plan": 3}, "tur": "plan", "neden": "tepki uzun", "kayip": "yok"},
            {"konum": {"plan": 5}, "tur": "plan", "neden": "boş bakış", "kayip": "yok"}]})
        r = kd.kesme_simule(self.film, "T1", 1)
        o = {x["hedef"][0]: x for x in r["oneriler"]}
        self.assertFalse(o[3]["gecti"]); self.assertTrue(any("kurulum" in h for h in o[3]["hatalar"]))
        self.assertTrue(o[5]["gecti"]); self.assertEqual(r["temiz"], 1); self.assertEqual(r["uygulanmasi_gereken"], 1)
        kar = os.path.join(self.film, "KURGU", "KURGU_KARARLARI_T1_t2.json")
        jy(kar, {"islemler": [{"op": "kirp", "plan": 6, "sure": 2.5, "kok_neden": "olu_sure", "bulgu": "s1"}]})
        kod, s = ku.calistir(self.film, "T1", 2, kar, kuru=True)
        self.assertEqual(kod, 1); self.assertTrue(any("kesme turu" in h["neden"] for h in s["hatalar"]))
        jy(kar, {"islemler": [{"op": "kes", "plan": 3, "kok_neden": "bilgisiz_uzun", "bulgu": "kesici:1", "simule": "_RAPOR/KESME_SIMULE_T1.json#1"}]})
        kod, s = ku.calistir(self.film, "T1", 2, kar, kuru=True)
        self.assertTrue(any("simülasyonda HATA" in h["neden"] for h in s["hatalar"]))
        jy(kar, {"islemler": [{"op": "kes", "plan": 5, "kok_neden": "bilgisiz_uzun", "bulgu": "kesici:2", "simule": "_RAPOR/KESME_SIMULE_T1.json#2"}]})
        kod, s = ku.calistir(self.film, "T1", 2, kar)
        self.assertEqual(kod, 0, s["hatalar"])
        v2 = jo(os.path.join(self.film, "KURGU", "surumler", "KURGU_PLANI_T1_v2.json"))
        self.assertNotIn(5, [p["plan"] for p in v2["planlar"]])

    def test_durum_degistiren_plan(self):
        jy(os.path.join(self.film, "KURGU", "KESME_T1.json"), {"oneriler": [{"tur": "plan", "plan": 2}]})
        r = kd.kesme_simule(self.film, "T1", 1)
        self.assertFalse(r["oneriler"][0]["gecti"]); self.assertTrue(any("Y58" in h for h in r["oneriler"][0]["hatalar"]))


class BildirimTesti(unittest.TestCase):
    def setUp(self): os.environ["YZ_FILM_BILDIRIM"] = "sahte"

    def test_bastirma_ve_gizli(self):
        a = "t-%s" % os.getpid()
        r = bildirim.gonder("asama_bitti", "A12 bitti 123456789:" + "A" * 35 + " mls@example.com", anahtar=a + "x")
        self.assertTrue(r["gonderildi"]); self.assertNotIn("A" * 35, r["metin"]); self.assertNotIn("@example.com", r["metin"])
        self.assertFalse(bildirim.gonder("asama_bitti", "tekrar", anahtar=a + "x")["gonderildi"])
        simdi = __import__("time").time()
        gec = [{"olay": "disk", "anahtar": str(i), "t": simdi - 10, "gonderildi": True} for i in range(12)]
        self.assertTrue(bildirim.bastir_mi(gec, "blok_hazir", "yeni")[0])
        self.assertFalse(bildirim.bastir_mi(gec, "kisit_olagandisi", "yeni")[0])      # ACİL saat tavanına takılmaz
        self.assertTrue(bildirim.bastir_mi([{"olay": "kisit_olagandisi", "anahtar": "k", "t": simdi - 60, "gonderildi": True}],
                                           "kisit_olagandisi", "k")[0])
        with self.assertRaises(ValueError): bildirim.gonder("uydurma", "x")

    def test_hatirlatma(self):
        import datetime
        eski = (datetime.datetime.now().astimezone() - datetime.timedelta(hours=7)).isoformat()
        yeni = datetime.datetime.now().astimezone().isoformat()
        self.assertTrue(bildirim.hatirlat(None, {"id": "A11-GZ-%d" % os.getpid(), "mesaj": "ZIP'i koy", "zaman": {"basla": eski}}))
        self.assertFalse(bildirim.hatirlat(None, {"id": "A11-GZ-y%d" % os.getpid(), "mesaj": "ZIP", "zaman": {"basla": yeni}}))


class IzleyiciKuraliTesti(unittest.TestCase):
    def setUp(self):
        from saglayicilar import izleyici as iz
        self.iz = iz; self.o0 = os.path.join(_ortam.VERI, "BILGI", "OLCUM0", "O0e.json")
        self.ayar = os.path.join(_ortam.VERI, "AYARLAR", "FILM_AYAR.json")
        os.environ.pop("GEMINI_API_KEY", None)

    def tearDown(self):
        os.environ.pop("GEMINI_API_KEY", None)
        for p in (self.o0, self.ayar):
            if os.path.exists(p): os.replace(p, p + ".test_eski")

    def test_acilma_kurali(self):
        s = self.iz.Izleyici()
        self.assertFalse(s.hazir()[0])
        os.environ["GEMINI_API_KEY"] = "test-degeri"
        jy(self.o0, {"gemini_katman": "ucretsiz", "video_girisi": True}); self.assertTrue(s.hazir()[0])
        jy(self.o0, {"gemini_katman": "ucretli"}); jy(self.ayar, {"izinler": {"gemini_api_ucretli": False}, "butce": {"usd_tavan_film": 0}})
        self.assertFalse(s.hazir()[0])
        jy(self.ayar, {"izinler": {"gemini_api_ucretli": True}, "butce": {"usd_tavan_film": 5}}); self.assertTrue(s.hazir()[0])
        jy(self.o0, {"gemini_katman": "ucretsiz", "video_girisi": False}); self.assertFalse(s.hazir()[0])
        jy(self.o0, {}); ok, _, bay = self.iz.acik_mi(s); self.assertTrue(ok); self.assertIn("katman_dogrulanmadi", bay)

    def test_rapor_semasi(self):
        r = self.iz.rapor_normal({"puanlar": {"GENEL": 7, "uydurma": 3}, "yz_kusurlari": [{"zaman": "00:01", "tur": "yuz", "siddet": 2},
                                                                                          {"tur": "bilinmeyen"}]}, "animatik", 1)
        self.assertEqual(r["puanlar"], {"GENEL": 7}); self.assertEqual(len(r["yz_kusurlari"]), 1)


if __name__ == "__main__":
    unittest.main()
