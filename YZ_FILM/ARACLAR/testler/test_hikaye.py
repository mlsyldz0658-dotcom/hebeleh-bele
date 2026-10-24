"""Hikâye odası testi (TASARIM §6.3, §6.10 test_hikaye, §9 adım 7 PR-5; [SN2] §4.6 test listesi a–i).

  - puan_oku v2: medyan (9, 6, 8) → 8; rapor.json + OZET satırı; v1 komut satırı; tek KRİTİK reddi kanıtla (D-21), kanıt kopukluktan
    sonra ya da maskeliyse red geri çevrilir; 2 seyircinin KRİTİK'i reddedilemez; KISMI (kapı var, hedef yok); plato + merdiven → BAYRAK.
  - juri-topla: fark ≤ 0,3 → BIRLESTIR; kazanan < 8 tur 1'de HATA.
  - NE YOK: karakter yasağı "zipper" ekran metninde ve replikteki "sleep" → HATA (senaryo-denetim).
  - bulgu_yonlendir: hikâyede olmayan olgu → hikaye-yazari; hikâyede olup planda olmayan → yonetmen.
  - sahne-sozlesme: yönetmen çıkış kostümünü değiştirirse HATA.
  - istem_denetim v2 replik ve istem kuralları; v1 davranışı test_film'de.
  - evren.py: ön kayıt, tekrar çalıştırma değişiklik yapmaz, kimlik çakışması HATA, ne_yok_kelimeleri, ozet.
  - Uçtan uca: film.py v2 görev zinciri A00–A06 `kaset` ile (ajan görevleri kasetten; hikâye odası betikleri GERÇEK; henüz depoda
    olmayan kor_paket.py ve görev kimliği yazmayan kredi.py but0 kasetten) → HIKAYE.json kilitli, evren ön kaydı, A06s'ye geçiş.
Ağ yok, kredi yok."""
import os, sys, json, io, glob, shutil, tempfile, contextlib, subprocess, unittest, unittest.mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak, puan_oku, hikaye_odasi, bulgu_yonlendir, istem_denetim, evren, esikler, film
from saglayicilar import kaset
import saglayicilar

DEPO_YZ = os.path.dirname(ARACLAR)
KASET = os.path.join(DEPO_YZ, "FILMLER", "ORNEK_3_SAHNE", "_KASET")
SAYAC = [0]


def yeni_film(ad=None):
    SAYAC[0] += 1
    kok = os.path.join(_ortam.VERI, "FILMLER", ad or f"HK_{SAYAC[0]:03d}")
    os.makedirs(os.path.join(kok, "_HIKAYE_ODASI"), exist_ok=True)
    return kok


def jl(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def rd(p):
    with open(p, encoding="utf-8") as f: return f.read()


def wr(p, metin):
    with open(p, "w", encoding="utf-8") as f: f.write(metin)


def kaset_json(*p):
    return jl(os.path.join(KASET, *p))


def sessiz(f, *a, **k):
    with contextlib.redirect_stdout(io.StringIO()): return f(*a, **k)


def ho(*a): return sessiz(hikaye_odasi.main, list(a))


def seyirci_rapor(n, genel, kop=(), persona=None, ilk=True):
    return {"kip": "kagit", "tur": 1, "seyirci": n, "persona": persona or "ABC"[n - 1], "donen_seyirci": False,
            "puanlar": {"anlasilirlik": 8, "akicilik": 8, "merak": 8, "duygu": 8, "ritim": 8, "ilk30": 8, "GENEL": genel},
            "parti_puanlari": {"P1": {"GENEL": genel}}, "kopukluklar": list(kop), "ilk2dk_devam": ilk, "devam": True}


class PuanOku(unittest.TestCase):
    def setUp(self):
        self.kok = yeni_film()
        shutil.copyfile(os.path.join(KASET, "AJAN", "A05_SN", "hepsi", "senaryo.json"),
                        os.path.join(self.kok, "_HIKAYE_ODASI", "06_SENARYO_v1.json"))
        self.sk = os.path.join(self.kok, "_RAPOR", "SEYIRCI", "kagit_t1")

    def yaz(self, rel, v): ortak.atomik_yaz(os.path.join(self.sk, rel), v)

    def eslesme(self):
        h = kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json")
        for n in (1, 2, 3):
            self.yaz(f"e{n}_eslesme.json", {"olgular": [{"id": o["id"], "karar": "bulundu"} for o in h["anahtar_olgular"]]})

    def paket(self, persona, metin):
        p = os.path.join(self.kok, "_KOR_PAKET", "kagit_t1", persona, "P1", "PAKET.md")
        os.makedirs(os.path.dirname(p), exist_ok=True); wr(p, metin)

    def test_medyan_ve_v1(self):
        self.assertEqual(puan_oku.medyan([9, 6, 8]), 8)
        d = tempfile.mkdtemp(dir=_ortam.KOK); yollar = []
        for i, p in enumerate((9, 6, 8)):
            y = os.path.join(d, f"s{i}_rapor.md"); wr(y, f"x\nOZET_P1 | GENEL: 5\nOZET | GENEL: {p} | KRITIK: 0 | ORTA: 1\n")
            yollar.append(y)
        r = puan_oku.rapor_oku(yollar[0])
        self.assertEqual((r["puanlar"]["GENEL"], r["parti"]["P1"], r["orta"]), (9, 5, 1))
        self.assertEqual(sessiz(puan_oku.main, yollar + ["--esik", "8"]), 0)
        j = os.path.join(d, "s9_rapor.json"); wr(j, json.dumps(seyirci_rapor(1, 6)))
        self.assertEqual(sessiz(puan_oku.main, [j, "--esik", "8"]), 3)

    def test_kismi_gec_ve_kritik(self):
        self.eslesme()
        for n, g in ((1, 7), (2, 7), (3, 8)): self.yaz(f"s{n}_rapor.json", seyirci_rapor(n, g))
        r = puan_oku.seyirci_topla(self.kok, "kagit", 1)
        self.assertEqual(r["medyan"]["GENEL"], 7); self.assertEqual(r["sonuc"], "KISMI"); self.assertTrue(r["kapi"])
        rap = jl(os.path.join(self.kok, "_RAPOR", "HS_KAGIT_FILM_t1.json"))
        self.assertEqual(rap["sonuc"], "KISMI"); self.assertTrue(all(h.get("hedef") for h in rap["hatalar"]))
        # iki seyircinin KRİTİK'i (±1 sahne) birleşir ve kapı HATA
        k = {"konum": {"sahne": "S05", "zaman": "10:10"}, "tur": "KRITIK", "neden": "kadın birden dağda"}
        k2 = dict(k, konum={"sahne": "S06", "zaman": "12:40"})
        self.yaz("s1_rapor.json", seyirci_rapor(1, 8, [k])); self.yaz("s2_rapor.json", seyirci_rapor(2, 8, [k2]))
        self.yaz("s3_rapor.json", seyirci_rapor(3, 9))
        self.yaz("KRITIK_RED.json", [{"konum": {"sahne": "S05"}, "kanit": {"ekran_satiri": "Sera walks the ridge path", "zaman": "10:00"}}])
        r = puan_oku.seyirci_topla(self.kok, "kagit", 1)
        self.assertEqual(r["sonuc"], "HATA"); self.assertEqual(r["kritik_gecerli"], 1)
        self.assertEqual([c["kac_seyirci"] for c in r["kopukluk"]], [2])

    def test_tek_kritik_reddi_kanitla(self):
        self.eslesme()
        k = {"konum": {"sahne": "S05", "zaman": "10:10"}, "tur": "KRITIK", "neden": "kadının nereye gittiğini anlamadım"}
        self.yaz("s1_rapor.json", seyirci_rapor(1, 8, [k])); self.yaz("s2_rapor.json", seyirci_rapor(2, 8)); self.yaz("s3_rapor.json", seyirci_rapor(3, 9))
        self.paket("A", "[09:50]\nThe woman walks the ridge path toward the high cave.\n[11:00]\nA rider waits below.\n")
        red = lambda satir: self.yaz("KRITIK_RED.json", [{"konum": {"sahne": "S05"}, "kanit": {"ekran_satiri": satir, "zaman": "09:50"}}])
        red("The woman walks the ridge path toward the high cave.")
        r = puan_oku.seyirci_topla(self.kok, "kagit", 1)
        self.assertEqual(r["kritik_gecersiz_sayilan"], 1); self.assertNotEqual(r["sonuc"], "HATA")
        red("A rider waits below.")                                     # kopukluktan (10:10) sonra
        self.assertEqual(puan_oku.seyirci_topla(self.kok, "kagit", 1)["sonuc"], "HATA")
        red("Sera walks the ridge path toward the high cave.")         # pakette yok (maskeli ad)
        r = puan_oku.seyirci_topla(self.kok, "kagit", 1)
        self.assertEqual(r["sonuc"], "HATA"); self.assertFalse(r["kopukluk"][0]["red"][0]["betik_dogruladi"])

    def test_plato_merdivenden_sonra_bayrak(self):
        self.eslesme()
        for t, g in ((1, 7), (2, 7)):
            ortak.atomik_yaz(os.path.join(self.kok, "_RAPOR", f"SEYIRCI_KARAR_KAGIT_t{t}.json"), {"medyan": {"GENEL": g}})
        sk = os.path.join(self.kok, "_RAPOR", "SEYIRCI", "kagit_t3")
        for n in (1, 2, 3):
            ortak.atomik_yaz(os.path.join(sk, f"s{n}_rapor.json"), seyirci_rapor(n, 7))
            ortak.atomik_yaz(os.path.join(sk, f"e{n}_eslesme.json"), jl(os.path.join(self.sk, f"e{n}_eslesme.json")))
        r = puan_oku.seyirci_topla(self.kok, "kagit", 3)
        self.assertTrue(r["plato"]); self.assertEqual(r["sonuc"], "KISMI"); self.assertEqual(r["merdiven_onerisi"], "yapimci·doktor")
        r = puan_oku.seyirci_topla(self.kok, "kagit", 3, merdiven=0)
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertTrue(r["hedef_alti"])

    def test_bozuk_rapor_sema_hatasi(self):
        self.eslesme(); self.yaz("s1_rapor.json", {"puanlar": {}}); self.yaz("s2_rapor.json", seyirci_rapor(2, 9))
        self.assertEqual(puan_oku.seyirci_topla(self.kok, "kagit", 1)["sonuc"], "HATA")


class HikayeOdasi(unittest.TestCase):
    def setUp(self):
        self.kok = yeni_film(); self.ho = os.path.join(self.kok, "_HIKAYE_ODASI")

    def rapor(self, ad): return jl(os.path.join(self.kok, "_RAPOR", ad))

    def test_konu_denetim(self):
        k = kaset_json("AJAN", "A01_YK", "hepsi", "01_KONU_KARTI.json"); k.pop("varsayimlar")
        ortak.atomik_yaz(os.path.join(self.ho, "01_KONU_KARTI.json"), k)
        ho("konu-denetim", "--film", self.kok); self.assertEqual(self.rapor("KONU_t1.json")["sonuc"], "GEC")
        k["sure"]["film_sure_hedef_sn"] = 3600; k["riskler"] = [r for r in k["riskler"] if r["tur"] != "filtre"]
        k["eksenler"]["S"] = k["eksenler"]["D"]; k["konu_ham"] = "küçük kız ve ejderha"
        ortak.atomik_yaz(os.path.join(self.ho, "01_KONU_KARTI.json"), k)
        ho("konu-denetim", "--film", self.kok); r = self.rapor("KONU_t1.json")
        self.assertEqual(r["sonuc"], "HATA")
        self.assertTrue({"sure_aralik", "eksen_ayni", "filtre_riski_tanimsiz"} <= {h["madde"] for h in r["hatalar"]})

    def test_brifing_yedi_bolum(self):
        shutil.copyfile(os.path.join(KASET, "AJAN", "A01_YK", "hepsi", "01_KONU_KARTI.json"), os.path.join(self.ho, "01_KONU_KARTI.json"))
        ho("brifing", "--film", self.kok); r = self.rapor("BRIFING_t1.json")
        self.assertNotEqual(r["sonuc"], "HATA")
        md = rd(os.path.join(self.ho, "00_BRIFING.md"))
        self.assertTrue(all("## " + b in md for b in hikaye_odasi.BRIFING_BOLUMLERI)); self.assertIn("chest", md)
        self.assertTrue(os.path.isfile(os.path.join(self.ho, "00_BRIFING.md.sha1")))

    def oneriler(self):
        for e, k in (("D", "A03_HM"), ("S", "A03_HM"), ("E", "A03_HM"), ("X", "A03_HX")):
            shutil.copyfile(os.path.join(KASET, "AJAN", k, e, "oneri.md"), os.path.join(self.ho, f"02_oneri_{e}.md"))

    def test_oneri_denetim_ve_benzer(self):
        self.oneriler(); ho("oneri-denetim", "--film", self.kok)
        self.assertNotEqual(self.rapor("ONERI_t1.json")["sonuc"], "HATA")
        md = rd(os.path.join(self.ho, "02_oneri_D.md"))
        wr(os.path.join(self.ho, "02_oneri_S.md"), md.replace('"eksen": "D"', '"eksen": "S"'))
        ho("oneri-denetim", "--film", self.kok); r = self.rapor("ONERI_t1.json")
        self.assertIn(r["sonuc"], ("HATA", "KISMI")); self.assertTrue(any(h["madde"] == "BENZER" for h in r["hatalar"]))

    def test_juri_birlestir(self):
        self.oneriler(); ho("juri-paketi", "--film", self.kok)
        self.assertEqual(len(glob.glob(os.path.join(self.ho, "JURI_PAKETI", "Oneri_*.md"))), 4)
        self.assertNotIn('"eksen"', rd(os.path.join(self.ho, "JURI_PAKETI", "Oneri_1.md")))
        for rol in hikaye_odasi.JURI_ROLLERI:
            j = kaset_json("AJAN", "A04_UJ" if rol == "uretilebilirlik" else "A04_JU", "hepsi" if rol == "uretilebilirlik" else rol, "rapor.json")
            for k in j["oneriler"]["2"]["puan"]: j["oneriler"]["2"]["puan"][k] = j["oneriler"]["1"]["puan"][k]
            ortak.atomik_yaz(os.path.join(self.ho, f"03_juri_{rol}.json"), j)
        ho("juri-topla", "--film", self.kok)
        s = jl(os.path.join(self.ho, "04_SECIM.json"))
        self.assertTrue(s["birlestir"]); self.assertEqual(s["seri_adi"], "FROSTHOLLOW")
        self.assertEqual(self.rapor("JURI_t1.json")["sonuc"], "GEC")
        for rol in hikaye_odasi.JURI_ROLLERI:
            p = os.path.join(self.ho, f"03_juri_{rol}.json"); j = jl(p)
            for n in j["oneriler"]: j["oneriler"][n]["puan"] = {k: 6 for k in j["oneriler"][n]["puan"]}
            ortak.atomik_yaz(p, j)
        ho("juri-topla", "--film", self.kok); self.assertEqual(self.rapor("JURI_t1.json")["sonuc"], "HATA")

    def senaryo(self, h):
        ortak.atomik_yaz(os.path.join(self.ho, "06_SENARYO_v1.json"), h)
        ho("senaryo-denetim", "--film", self.kok); return self.rapor("HIKAYE_Z_v1.json")

    def test_yapi_ve_senaryo_temiz(self):
        shutil.copyfile(os.path.join(KASET, "AJAN", "A05_HY", "hepsi", "05_YAPI.json"), os.path.join(self.ho, "05_YAPI.json"))
        ho("yapi-denetim", "--film", self.kok); self.assertNotIn(self.rapor("YAPI_t1.json")["sonuc"], ("HATA", "KISMI"))
        r = self.senaryo(kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json"))
        self.assertNotIn(r["sonuc"], ("HATA", "KISMI"), r["hatalar"])

    def test_ne_yok_ve_filtre_hata(self):
        h = kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json")
        h["karakterler"]["sera"]["yasak"] = ["zipper"]
        h["sahneler"][2]["ekran"]["gorulen"].append("Sera pulls the zipper of her coat.")
        h["replikler"][5]["metin"] = "Get some sleep now."
        r = self.senaryo(h); m = {x["madde"] for x in r["hatalar"]}
        self.assertIn("ekran_ne_yok", m); self.assertIn("replik_filtre", m)
        q = jl(os.path.join(self.kok, "KUYRUK", "YENIDEN_YAZ.json"))
        self.assertTrue(any(x["yazar"] == "hikaye-yazari" for x in q["maddeler"]))

    def test_bilgi_durumu_ve_sahne_siniri(self):
        h = kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json")
        h["karakterler"]["oda"]["bildikleri_bas"] = []                       # Oda, Sera'nın adını bilmiyor
        h["sahneler"][1]["giris_durumu"]["varliklar"]["sera"]["kostum"] = "k2"  # S01 → S02 kostüm sıçraması
        m = {x["madde"] for x in self.senaryo(h)["hatalar"]}
        self.assertIn("bilgi_durumu", m); self.assertIn("sahne_siniri", m)

    def test_sahne_sozlesme_kostum(self):
        h = kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json"); ortak.atomik_yaz(os.path.join(self.kok, "HIKAYE.json"), h)
        planlar = []
        for i, s in enumerate(h["sahneler"]):
            rs = [r for r in h["replikler"] if r["sahne"] == s["id"]]
            for j in range(max(1, len(rs))):
                z = {"sahne_grubu": s["id"], "klip_sn": 150 / max(1, len(rs)),
                     "ekranda_bilgi": [{"olgu": o["id"]} for o in h["anahtar_olgular"] if s["id"] in o["ekranda"]],
                     "baslangic_durumu": s["giris_durumu"] if j == 0 else "miras", "bitis_durumu": s["cikis_durumu"]}
                pl = {"no": len(planlar) + 1, "zanaat": z}
                if rs: pl["replik"] = {"id": rs[j]["id"], "metin": rs[j]["metin"]}
                planlar.append(pl)
        ortak.atomik_yaz(os.path.join(self.kok, "_YONETMEN", "PLANLAR", "G1.json"), {"planlar": planlar})
        ho("sahne-sozlesme", "--film", self.kok); self.assertEqual(self.rapor("SEMA_SOZLESME.json")["sonuc"], "GEC")
        son = [p for p in planlar if p["zanaat"]["sahne_grubu"] == "S03"][-1]
        son["zanaat"]["bitis_durumu"] = json.loads(json.dumps(son["zanaat"]["bitis_durumu"]))
        son["zanaat"]["bitis_durumu"]["varliklar"]["sera"]["kostum"] = "k1_yirtik"
        ortak.atomik_yaz(os.path.join(self.kok, "_YONETMEN", "PLANLAR", "G1.json"), {"planlar": planlar})
        ho("sahne-sozlesme", "--film", self.kok); r = self.rapor("SEMA_SOZLESME.json")
        self.assertIn(r["sonuc"], ("HATA", "KISMI")); self.assertTrue(any(x["madde"] == "sahne_cikis_durumu" for x in r["hatalar"]))

    def test_vaat_ve_seyirlik(self):
        ortak.atomik_yaz(os.path.join(self.kok, "HIKAYE.json"), kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json"))
        ho("vaat-denetim", "--film", self.kok); self.assertEqual(self.rapor("SEMA_VAAT_t1.json")["sonuc"], "GEC")
        ho("vaat-denetim", "--film", self.kok, "--baslik", "She Had to Kill the Dragon | FROSTHOLLOW | Full Movie 4K 2026")
        self.assertEqual(self.rapor("SEMA_VAAT_t1.json")["sonuc"], "BAYRAK")
        ho("seyirlik-denetim", "--film", self.kok); self.assertNotEqual(self.rapor("Z2_HIKAYE.json")["sonuc"], "HATA")


class BulguYonlendir(unittest.TestCase):
    def test_sahip(self):
        kok = yeni_film(); h = kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json")
        ortak.atomik_yaz(os.path.join(kok, "HIKAYE.json"), h)
        ortak.atomik_yaz(os.path.join(kok, "_YONETMEN", "PLANLAR", "G1.json"),
                         {"planlar": [{"no": 1, "zanaat": {"sahne_grubu": "S01", "ekranda_bilgi": [{"olgu": "o01"}]}}]})
        ortak.atomik_yaz(os.path.join(kok, "_RAPOR", "SEYIRCI", "kagit_t1", "b1_bulgu.json"), [
            {"bulgu": "s1:k1", "konum": {"sahne": "S05"}, "eslesen": {"tur": "anahtar_olgu", "id": "o99"}},
            {"bulgu": "s1:k2", "konum": {"sahne": "S04"}, "eslesen": {"tur": "anahtar_olgu", "id": "o04"}},
            {"bulgu": "s1:k3", "konum": {"sahne": "S01"}, "eslesen": {"tur": "anahtar_olgu", "id": "o01"}}])
        r = bulgu_yonlendir.yonlendir(kok, "kagit", 1)
        b = {x["bulgu"]: x for x in r["bulgular"]}
        self.assertEqual((b["s1:k1"]["sahip"], b["s1:k1"]["kok_neden"], b["s1:k1"]["hikayede_var"]), ("hikaye-yazari", "bilgi_eksik", False))
        self.assertEqual((b["s1:k2"]["sahip"], b["s1:k2"]["kok_neden"]), ("yonetmen", "hikaye_adimi_ekranda_yok"))
        self.assertEqual(b["s1:k3"]["sahip"], "hikaye-yazari"); self.assertTrue(b["s1:k3"]["planda_var"])
        self.assertTrue(os.path.isfile(os.path.join(kok, "_RAPOR", "BULGU_YONLENDIRME_KAGIT_t1.json")))


class IstemV2(unittest.TestCase):
    def plan(self, **k):
        hi = 'Static medium shot. 2.0-5.0s: Sera says quietly, in a low female voice: "Rest now." Sound: wind. No music.'
        s = {"no": 1, "parti": 1, "referans": ["sera"], "gorsel_istem": "Sera kneeling at the cave mouth, turning toward the light",
             "hareket_istem": hi, "replik": {"id": "R0001", "karakter": "sera", "metin": "Rest now."},
             "zanaat": {"plan_tipi": "diyalog", "kadrajdakiler": [{"id": "sera", "konusur": True}],
                        "ses": {"flow_sound": "Sound: wind. No music."}}}
        s.update(k); return {"_surum": 2, "sahneler": [s]}

    def test_temiz_ve_hatalar(self):
        self.assertFalse([x for x in istem_denetim.denetle_v2(self.plan()) if x["seviye"] == "HATA"])
        p = self.plan(); s = p["sahneler"][0]
        s["replik"]["metin"] = "Get some sleep, little one."; s["hareket_istem"] = "She grabs the rope on the left. Sound: wind. No music."
        s["zanaat"]["ses"]["flow_sound"] = "wind"
        m = {x["madde"] for x in istem_denetim.denetle_v2(p, ne_yok=["rope"])}
        self.assertTrue({"replik_filtre", "yasak_sonuc_fiili", "ciplak_yon", "flow_sound_kalibi", "istem_ne_yok"} <= m, m)
        self.assertFalse([x for x in istem_denetim.denetle_v2(self.plan(hareket_istem=self.plan()["sahneler"][0]["hareket_istem"]
                                                                        .replace("Static", "Her LEFT hand rests. Static")))
                          if x["madde"] == "ciplak_yon"])
        self.assertTrue(istem_denetim.replik_denetle(" ".join(["word"] * 17)))

    def test_v2_rapor(self):
        kok = yeni_film(); ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), self.plan())
        r, yol = istem_denetim.rapor_v2(kok)
        self.assertEqual(r["kapi"], "ISTEM"); self.assertTrue(os.path.isfile(yol))


class Evren(unittest.TestCase):
    def test_on_kayit(self):
        kok = yeni_film(); h = kaset_json("AJAN", "A05_SN", "hepsi", "senaryo.json"); h["evren"] = "TESTSERI"
        ortak.atomik_yaz(os.path.join(kok, "HIKAYE.json"), h)
        r, kod = evren.on_kayit(kok)
        self.assertEqual(kod, 0); self.assertIn("sera", r["karakterler"])
        self.assertTrue(os.path.isfile(evren.seri_yolu("TESTSERI", "karakterler", "sera", "karakter.json")))
        r2, _ = evren.on_kayit(kok); self.assertEqual(r2["degisen"], [])
        self.assertIn("musket", evren.ne_yok_kelimeleri(seri="TESTSERI"))
        self.assertIn("TESTSERI", [s["seri"] for s in evren.ozet()["seriler"]])
        h["karakterler"]["sera"]["ad"] = "Mara"; ortak.atomik_yaz(os.path.join(kok, "HIKAYE.json"), h)
        r3, kod = evren.on_kayit(kok); self.assertEqual(kod, 1); self.assertIn("çakışma", r3["hatalar"][0])
        self.assertEqual(sessiz(evren.main, ["--yedekle"]), 4)


class EsikVeKaset(unittest.TestCase):
    def test_hikaye_esikleri_cift_anahtarsiz(self):
        E = esikler.yukle(); self.assertEqual(E["juri_kazanan_min"], 8.0)
        self.assertEqual(E.kayit["juri_kazanan_min"]["_dosya"], "hikaye_esikleri.json")

    def test_kaset_uydurmaz(self):
        g = {"id": "A09-ZZ-001", "asama": "A09", "anahtar": "A09@s1/t1/g0/ZZ/1", "tur_no": 1}
        with self.assertRaises(kaset.KasetYok): kaset.ajan_oynat(yeni_film(), g)
        self.assertIn("kaset", saglayicilar.KAYIT); self.assertEqual(saglayicilar.yukle("kaset").ad, "kaset")


# --- uçtan uca --------------------------------------------------------------------------------------------------
YOK_ARAC = {"kor_paket.py", "seyirci_topla.py"}       # henüz depoda yok (PR-3) / A06 ST → puan_oku.py seyirci-topla
KASETTEN = {"kor_paket.py", "kredi.py"}              # kredi.py but0 raporu _uretim.gorev yazmıyor (paylaşılan istek)


class UctanUca(unittest.TestCase):
    def setUp(self):
        self.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "yerel"}); self.env.start()
        self.ad = "HK_UCTAN_UCA"
        self.kok = os.path.join(_ortam.VERI, "FILMLER", self.ad)
        kod, r = self.k("yeni", "--konu", "ejderha yavrusunu saklayan avcı kadın", "--ad", self.ad)
        self.assertEqual(kod, 0, r)
        shutil.copytree(KASET, os.path.join(self.kok, "_KASET"))

    def tearDown(self): self.env.stop()

    def k(self, *a):
        a = list(a) + (["--film", self.ad] if a[0] != "yeni" else [])
        with contextlib.redirect_stdout(io.StringIO()) as o: kod = film.main(a)
        try: return kod, json.loads(o.getvalue())
        except ValueError: return kod, o.getvalue()

    def nabiz(self):
        ortak.atomik_yaz(os.path.join(self.kok, "_GOREV", "KANCA_NABZI.json"), {"zaman": film.simdi(), "yazan": "test"})

    def test_A00_A06_kaset(self):
        orj_kos, orj_isfile = film.Defter.betik_kos, os.path.isfile
        cagri = {"gercek": [], "kaset": []}

        def betik_kos(d, g):
            if g["arac"] in KASETTEN:
                cagri["kaset"].append(g["id"]); return kaset.betik_oynat(d.kok, g)[0]
            if g["arac"] == "seyirci_topla.py": g = dict(g, arac="puan_oku.py", argumanlar=["seyirci-topla"] + list(g["argumanlar"]))
            if not g["arac"].startswith("film.py:"): cagri["gercek"].append(g["arac"] + " " + " ".join(g["argumanlar"]))
            return orj_kos(d, g)

        def isfile(p):
            if os.path.dirname(os.path.abspath(p)) == ARACLAR and os.path.basename(p) in YOK_ARAC: return True
            return orj_isfile(p)

        asamalar = []
        with unittest.mock.patch.object(film.Defter, "betik_kos", betik_kos), unittest.mock.patch("os.path.isfile", isfile), \
                unittest.mock.patch.object(film, "disk_bos_gb", lambda y: 500.0):
            for _ in range(300):
                self.nabiz()
                kod, r = self.k("sonraki")
                self.assertIsInstance(r, dict, r)
                asama = (r.get("asama") or "").split(" ")[0]
                if not asamalar or asamalar[-1] != asama: asamalar.append(asama)
                if asama == "A06s": break
                self.assertIn(r["tur"], ("ajan", "betik"), r)
                for gz in r["gorevler"]:
                    if r["tur"] == "betik":
                        kc, rc = self.k("calis", gz["id"]); self.assertEqual(kc, 0, (gz, rc)); continue
                    self.k("basla", gz["id"])
                    g = jl(os.path.join(self.kok, "_GOREV", gz["id"], "GOREV.json"))
                    kaset.ajan_oynat(self.kok, g)
                    while g.get("asamali"):
                        _, ri = self.k("asama-ilerlet", gz["id"])
                        if ri.get("son"): break
                    kb, rb = self.k("bitir", gz["id"]); self.assertEqual(kb, 0, rb); self.assertEqual(rb["durum"], "bitti", rb)
            else:
                self.fail(f"A06s'ye ulaşılamadı: {asamalar}")
        self.assertEqual(asamalar, ["A00", "A01", "A02", "A03", "A04", "A05", "A06", "A06s"])
        rap = lambda ad: jl(os.path.join(self.kok, "_RAPOR", ad))
        for ad in ("KONU_t1.json", "BRIFING_t1.json", "ONERI_t1.json", "JURI_t1.json", "YAPI_t1.json", "HIKAYE_Z_v1.json"):
            self.assertIn(rap(ad)["sonuc"], ("GEC", "BAYRAK"), (ad, rap(ad)["hatalar"]))
        self.assertEqual(rap("HS_KAGIT_FILM_t1.json")["sonuc"], "KISMI")       # kapı var, hedef yok → tur 2 (revizyon)
        self.assertEqual(rap("HS_KAGIT_FILM_t2.json")["sonuc"], "GEC")
        h = jl(os.path.join(self.kok, "HIKAYE.json"))
        self.assertTrue(h["kilit"]); self.assertEqual(h["evren"], "FROSTHOLLOW"); self.assertEqual(h["seyirci_kagit"]["tur"], 2)
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "HIKAYE.md")))
        self.assertTrue(os.path.isfile(evren.seri_yolu("FROSTHOLLOW", "karakterler", "sera", "karakter.json")))
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "_HIKAYE_ODASI", "DEGISIKLIK_v2.json")))
        self.assertIn("süre 30 dk", rd(os.path.join(self.kok, "KARAR_DEFTERI.md")))
        gercek = " | ".join(cagri["gercek"])
        for alt in ("konu-denetim", "brifing", "oneri-denetim", "juri-paketi", "juri-topla", "yapi-denetim", "senaryo-denetim",
                    "seyirci-topla", "devir"):
            self.assertIn(alt, gercek)
        self.assertEqual(len(cagri["kaset"]), 3)                               # B0 + KP (tur 1, tur 2)


if __name__ == "__main__":
    unittest.main()
