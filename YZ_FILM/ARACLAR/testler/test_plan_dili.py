"""test_plan_dili — yönetmen kâğıdı ve plan dili (TASARIM §5.1, §6.4, §7.2 SEMA/Z0/Z1/Z2, D-13, D-15, D-22, §6.10; [SON] S-1;
[YN2] §4.7 Y01–Y60; ZN §2.3).

Kapsam:
  - Sözlükler: fiil (beklenen_hiz, sure_carpani, şablonlarda filtre/sonuç fiili/çıplak sol-sağ yok), ifade (≈ 16, EN + kör karşılığı),
    efekt, plan (teslim 12).
  - plan_sema: §5.1'in kanonik örneği (TASARIM'dan okunur) HATA'sız; v1 dosya v1 kuralı; v2'de zanaat zorunlu; 'surum' zarfı; ajan
    dosyasında _derlenir; SAHNELER'de elle değişmiş _derlenir.
  - plan_dili: EN istem gövdesi saniyeli, iyelikli sağ/sol, tek kişide öznesiz / çok kişide adlı, replik kelimesi kelimesine; TR, şerit,
    çekim çıktıları; sira biçimi.
  - plan_denetim: örnek film --harita / --sahne --tum / --tum HATA'sız; ZANAAT bozuk varyantları ("arac": "z0") adıyla yakalanır;
    ZN §2.3 diyalog formülü tablosu; --dosya (SubagentStop) kipi.
  - istem_derle --hareket (istem özeti, elle değişmiş istem korunur), --gorsel/--kart istem_derle_gorsel'e yönlenir; kroki --ciz / --karsilikli / kroki yoksa
    HESAPLANAMADI; zaman_cizelgesi T0 (Z1/Z2, olaylar, eğri) ve bozuk zaman; kamera_agaci (ağaç, bayat yayılımı, KAGIT_TAMAM);
    cekim_listesi.
Ağ yok, kredi yok."""
import os, sys, json, re, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import _zanaat as Z
import ortak, plan_ortak as po, plan_sema, plan_dili, plan_birlestir, plan_denetim, istem_derle, kroki, dunya_defteri
import zaman_cizelgesi, kamera_agaci, cekim_listesi

try:
    import PIL  # noqa
    PILLOW = True
except ImportError:
    PILLOW = False
TASARIM = os.path.join(ortak.DEPO_KOK, ".claude", "skills", "film-yap", "tartisma", "TASARIM.md")


def kanonik():
    with open(TASARIM, encoding="utf-8") as f: t = f.read()
    i = t.index("### 5.1"); j = t.index("```json", i) + 7; k = t.index("```", j)
    return json.loads(t[j:k])


def birlesik(ad=None):
    kok = Z.kopya(ad); Z.kos(plan_birlestir, "--film", kok); return kok


def rapor(kok, ad): return Z.jl(os.path.join(kok, "_RAPOR", ad))


class Sozlukler(unittest.TestCase):
    def test_fiil_sozlugu(self):
        fl = po.fiiller(); self.assertGreaterEqual(len(fl), 40)
        turler = set(po.sozluk("plan").get("adim_tur") or ["fiziksel", "mikro", "konusma", "ses_vurusu"])
        yasak = [y.lower() for y in po.esik().get("yasak_sonuc_fiilleri")]
        for ad, f in fl.items():
            self.assertIn(f["tur"], turler, ad)
            for k in ("en", "tr", "beklenen_hiz", "sure_carpani"): self.assertIn(k, f, ad)
            for k, v in f.items():
                if not (k.startswith("en") and isinstance(v, str)): continue
                metin = re.sub(r"\{[a-z_]+\}", "x", v).lower()
                self.assertFalse(istem_derle.yasak_bul(metin), (ad, k, v))
                self.assertFalse(plan_denetim.ciplak_yon(metin), (ad, k, v))
                for y in yasak: self.assertIsNone(re.search(r"\b" + re.escape(y) + r"\b", metin), (ad, y))
            if f["tur"] == "fiziksel" and f.get("durum_degistirir"):
                self.assertTrue(f.get("etki_sablonu"), ad)

    def test_ifade_efekt_plan(self):
        i = po.sozluk("ifade")["degerler"]
        self.assertTrue(14 <= len(i) <= 20, len(i))
        for ad, v in i.items(): self.assertTrue(v.get("en") and v.get("tr") and v.get("kor"), ad)
        e = po.sozluk("efekt"); self.assertTrue(e.get("kategoriler")); self.assertTrue(e.get("fiiller"))
        for ad in e["fiiller"]: self.assertIn(ad, po.fiiller(), ad)
        p = po.sozluk("plan")
        self.assertEqual(len(p["teslim"]), 12)                         # teslim_sozluk_boyutu (D-22)
        for k in ("kadraj", "olcek", "hareket_tipi", "plan_tipi", "zincir_gecis_turu", "zincir_baslangic", "kesme_tip"): self.assertIn(k, p)


class Sema(unittest.TestCase):
    def test_kanonik_ornek_hatasiz(self):
        d = kanonik(); E = po.esik()
        self.assertEqual(plan_sema.surum(d), 2)
        o = plan_sema.denetle(d, "sahneler", None, "kanonik")
        self.assertEqual([x for x in o if x["seviye"] == "HATA"], [])
        o = plan_denetim.plan_kurallari(d["sahneler"][0], E, None, plan_denetim._filtre())
        self.assertEqual([x for x in o if x["seviye"] == "HATA"], [], o)

    def test_v1_ve_zanaatsiz_v2(self):
        self.assertEqual(plan_sema.surum({"film": "X", "sahneler": []}), 1)
        o = plan_sema.denetle({"film": "X", "sahneler": [{"no": 1}]}, "sahneler")
        self.assertEqual([x["madde"] for x in o], ["v1_dosya"])
        d = kanonik(); d["sahneler"][0].pop("zanaat")
        self.assertIn("zanaat_yok", [x["madde"] for x in plan_sema.denetle(d, "sahneler") if x["seviye"] == "HATA"])
        d = kanonik(); d["surum"] = 2
        self.assertIn("zarf_surum_alt_cizgisiz", [x["madde"] for x in plan_sema.denetle(d, "sahneler")])

    def test_ajan_derlenir_yazamaz(self):
        kok = Z.kopya("ZN_SEMA1"); Z.bozuk_uygula(kok, "derlenir_elle")
        kod, _ = Z.kos(plan_sema, "--film", kok)
        self.assertEqual(kod, 1)
        self.assertIn("derlenir_ajan_yazimi", [h["madde"] for h in rapor(kok, "SEMA_PLAN.json")["hatalar"]])

    def test_yeniden_birlestirme_ses_alanlarini_korur(self):
        """Birleştirme: A08'in yazdığı zanaat.ses, sahne_gruplari.<S>.ses ve sese bağlı _derlenir alanları A07c yeniden koşunca kaybolmaz."""
        kok = birlesik("ZN_SESK"); y = os.path.join(kok, "SAHNELER.json"); s = Z.jl(y)
        p0 = s["sahneler"][0]; sid = next(iter(s["sahne_gruplari"]))
        p0["zanaat"]["ses"] = {"flow_sound": "Sound: wind over snow. No music.", "diyalog": {"yol": "tts"}}
        p0["_derlenir"]["ton_fiili_en"] = "whispers"; p0["_derlenir"]["muzik_ipucu"] = "M01"
        s["sahne_gruplari"][sid]["ses"] = {"yatak": {"dosya": "_SES/yatak.wav", "seviye_lufs": -38}}
        ortak.atomik_yaz(y, s)
        self.assertEqual(Z.kos(plan_birlestir, "--film", kok)[0], 0)
        s2 = Z.jl(y); q0 = next(p for p in s2["sahneler"] if p["no"] == p0["no"])
        self.assertEqual(q0["zanaat"]["ses"], p0["zanaat"]["ses"])
        self.assertEqual((q0["_derlenir"]["ton_fiili_en"], q0["_derlenir"]["muzik_ipucu"]), ("whispers", "M01"))
        self.assertEqual(s2["sahne_gruplari"][sid]["ses"], s["sahne_gruplari"][sid]["ses"])
        self.assertEqual(Z.kos(plan_sema, "--film", kok)[0], 0)          # derlenir imzası korunan alanlarla tazelendi

    def test_sahnelerde_elle_derlenir(self):
        kok = birlesik("ZN_SEMA2")
        self.assertEqual(Z.kos(plan_sema, "--film", kok)[0], 0)
        p = os.path.join(kok, "SAHNELER.json"); s = Z.jl(p)
        s["sahneler"][0]["_derlenir"]["kadraj_konumu"] = {"mara": "orta"}; ortak.atomik_yaz(p, s)
        self.assertEqual(Z.kos(plan_sema, "--film", kok)[0], 1)
        self.assertIn("derlenir_elle_yazim", [h["madde"] for h in rapor(kok, "SEMA_PLAN.json")["hatalar"]])


class PlanDili(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kok = birlesik("ZN_DIL")
        cls.s = Z.jl(os.path.join(cls.kok, "SAHNELER.json"))
        cls.B = plan_dili.baglam(cls.kok, cls.s)
        cls.P = {p["no"]: p for p in cls.s["sahneler"]}

    def test_en_saniyeli_ve_iyelikli(self):
        for no, p in self.P.items():
            t = plan_dili.gorunur_tarif(p, "en", self.B)
            self.assertRegex(t, r"\d(\.\d)?-\d+(\.\d)?s: ", no)
            self.assertEqual(plan_denetim.ciplak_yon(t), [], (no, t))
            self.assertFalse(istem_derle.yasak_bul(t.replace((p.get("replik") or {}).get("metin") or "@@", " ")), (no, t))
        t1 = plan_dili.gorunur_tarif(self.P[1], "en", self.B)
        self.assertIn("her empty left arm", t1)                      # karakterin KENDİ sağı/solu
        self.assertNotIn("Mara walks", t1)                           # tek kişi: öznesiz

    def test_cok_kisi_adli_ve_replik_aynen(self):
        t = plan_dili.gorunur_tarif(self.P[5], "en", self.B)
        self.assertIn("Mara", t); self.assertIn("\"It's late, Captain. What do you want?\"", t)
        self.assertIn("a low, husky female voice", t)                # _SES/SES_PROFILLERI.json veo_ses_tarifi
        self.assertIn("seen from behind, silent", t)                  # OU: öndeki kişi sırtı dönük ve sessiz

    def test_tr_serit_cekim_ve_sira(self):
        p = self.P[2]
        tr = plan_dili.gorunur_tarif(p, "tr", self.B); self.assertIn("sn:", tr); self.assertIn("sol", tr)
        self.assertIn("|", plan_dili.gorunur_tarif(self.P[1], "serit", self.B))
        c = plan_dili.gorunur_tarif(p, "cekim", self.B); self.assertIsInstance(c, list); self.assertGreaterEqual(len(c), 3)
        sira = plan_dili.gorunur_tarif(p, "en", self.B, "sira")
        self.assertNotRegex(sira, r"\d-\d+(\.\d)?s: ")


class PlanDenetim(unittest.TestCase):
    def test_ornek_hatasiz(self):
        kok = Z.kopya("ZN_PD")
        self.assertEqual(Z.kos(plan_denetim, "--harita", "--film", kok)[0], 0)
        self.assertIn(rapor(kok, "HARITA_t1.json")["sonuc"], ("GEC", "BAYRAK"))
        self.assertEqual(Z.kos(plan_denetim, "--sahne", "--tum", "--film", kok)[0], 0)
        r = rapor(kok, "Z0_SAHNE_t1.json"); self.assertEqual(r["hatalar"], []); self.assertEqual(r["kapi"], "Z0")
        self.assertEqual(Z.kos(plan_denetim, "--sahne", "S02", "--film", kok)[0], 0)
        Z.kos(plan_birlestir, "--film", kok)
        self.assertEqual(Z.kos(plan_denetim, "--tum", "--film", kok)[0], 0)
        self.assertEqual(rapor(kok, "Z0_P1.json")["hatalar"], [])
        self.assertTrue(os.path.isfile(os.path.join(kok, "_RAPOR", "Z0_FILM.json")))

    def test_bozuk_varyantlar(self):
        z0 = [ad for ad in Z.varyantlar() if Z.varyant(ad)["arac"] == "z0"]
        self.assertGreaterEqual(len(z0), 12)
        for ad in z0:
            with self.subTest(varyant=ad):
                kok = Z.kopya(f"ZN_Z0_{ad}"); v = Z.bozuk_uygula(kok, ad)
                kod, _ = Z.kos(plan_denetim, "--sahne", "--tum", "--film", kok)
                r = rapor(kok, "Z0_SAHNE_t1.json")
                self.assertIn(v["beklenen"]["madde"], [h["madde"] for h in r["hatalar"]], (ad, Z.maddeler(r)))
                self.assertEqual(kod, 1, ad)

    def test_tum_hatasi_yeniden_yaz_kuyruguna(self):
        kok = Z.kopya("ZN_PDQ"); Z.bozuk_uygula(kok, "adim_kisa"); Z.kos(plan_birlestir, "--film", kok)
        self.assertEqual(Z.kos(plan_denetim, "--tum", "--film", kok)[0], 1)
        q = Z.jl(os.path.join(kok, "KUYRUK", "YENIDEN_YAZ.json"))
        self.assertTrue(any(m["kapi"] == "Z0" and m["madde"] == "adim_kisa" for m in q["maddeler"]), q)

    def test_diyalog_formulu(self):
        E = po.esik()
        for kel, cum, sn in ((5, 1, 2.9), (10, 2, 5.2), (16, 2, 7.6), (20, 3, 9.4)):
            self.assertAlmostEqual(plan_denetim.diyalog_formulu(kel, cum, E), sn, places=1)

    def test_dosya_kipi(self):
        kok = Z.kopya("ZN_PDD")
        y = os.path.join(kok, "_YONETMEN", "PLANLAR", "S01.json")
        self.assertEqual(Z.kos(plan_denetim, "--dosya", y, "--film", kok)[0], 0)
        Z.bozuk_uygula(kok, "adim_ortusmesi")
        kod, cikti = Z.kos(plan_denetim, "--dosya", y, "--film", kok)
        self.assertEqual(kod, 1); self.assertIn("adim_ortusmesi", cikti)


class IstemKroki(unittest.TestCase):
    def test_hareket_istemi(self):
        kok = birlesik("ZN_IST")
        self.assertEqual(Z.kos(istem_derle, "--hareket", "--film", kok)[0], 0)
        s = Z.jl(os.path.join(kok, "SAHNELER.json"))
        for p in s["sahneler"]:
            self.assertTrue(p["hareket_istem"].endswith("No music."), p["no"])
            self.assertEqual(p["_derlenir"]["istem_ozeti"], po.imza(p["hareket_istem"]))
        self.assertEqual(Z.kos(plan_sema, "--film", kok)[0], 0)          # derlenir imzası istem_derle'den sonra da geçerli
        p0 = s["sahneler"][0]; p0["hareket_istem"] = "Static shot. She walks."; ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
        kod, cikti = Z.kos(istem_derle, "--hareket", "--film", kok)
        self.assertIn("istem_elle_degismis", cikti)
        self.assertEqual(Z.jl(os.path.join(kok, "SAHNELER.json"))["sahneler"][0]["hareket_istem"], "Static shot. She walks.")
        # adım 12 kipleri istem_derle_gorsel'e yönlenir (birleştirme: artık "henüz yok → 4" değil)
        from unittest import mock
        import istem_derle_gorsel
        with mock.patch.object(istem_derle_gorsel, "main", return_value=0) as m:
            self.assertEqual(Z.kos(istem_derle, "--gorsel", "--film", kok)[0], 0)
            self.assertEqual(Z.kos(istem_derle, "--kart", "--film", kok)[0], 0)
        self.assertEqual([c.args[0] for c in m.call_args_list], [["--gorsel", "--film", kok], ["--kart", "--film", kok]])
        kod, cikti = Z.kos(istem_derle, "--bitis", "--film", kok)          # gerçek alt araç: bitiş görseli adım 15'te
        self.assertEqual(kod, 4); self.assertIn("kare_zinciri", cikti)

    def test_kroki_ciz_karsilikli_ve_hesaplanamadi(self):
        kok = Z.kopya("ZN_KR")
        self.assertEqual(Z.kos(kroki, "--karsilikli", "--film", kok)[0], 0)
        o = Z.jl(os.path.join(kok, "_YONETMEN", "KROKI_ONERI.json"))["oneriler"]
        self.assertIn("kulube", o)
        self.assertEqual(Z.kos(kroki, "--ciz", "--film", kok)[0], 0)
        self.assertEqual(os.path.isfile(os.path.join(kok, "_YONETMEN", "KROKI", "kulube.png")), PILLOW)   # Pillow yoksa ÖLÇÜLEMEDİ
        os.rename(os.path.join(kok, "EVREN"), os.path.join(kok, "_EVREN_YOK"))
        kod, _ = Z.kos(plan_denetim, "--sahne", "--tum", "--film", kok)
        self.assertEqual(kod, 1)                                          # kroki yoksa geometri HESAPLANAMADI = HATA


class ZamanAgacListe(unittest.TestCase):
    def zinc(self, ad, varyant=None):
        kok = Z.kopya(ad)
        if varyant: varyant(kok)
        Z.kos(plan_birlestir, "--film", kok); Z.kos(dunya_defteri, "--derle", "--denetle", "--film", kok)
        return kok

    def test_t0(self):
        kok = self.zinc("ZN_T0")
        self.assertEqual(Z.kos(zaman_cizelgesi, "--asama", "kagit", "--film", kok)[0], 0)
        kp = Z.jl(os.path.join(kok, "KURGU", "surumler", "KURGU_PLANI_T0.json"))
        self.assertEqual(kp["plan_sayisi"], 9)
        self.assertAlmostEqual(kp["toplam_sn"], sum(p["sure"] for p in kp["planlar"]), places=1)
        self.assertEqual(kp["planlar"][1]["bas"], kp["planlar"][0]["bit"])
        z = Z.jl(os.path.join(kok, "KURGU", "ZAMAN_T0.json"))
        turler = {e["tur"] for e in z["olaylar"]}
        for t in ("sahne", "eylem", "replik", "merak_ac", "merak_kapat", "kurulum", "kullanim", "ilk_gorunus"): self.assertIn(t, turler)
        r1, r2 = rapor(kok, "ZAMAN_T0.json"), rapor(kok, "ZAMAN_Z2_T0.json")
        self.assertEqual((r1["kapi"], r2["kapi"]), ("Z1", "Z2"))
        self.assertEqual(r1["hatalar"] + r2["hatalar"], [])
        self.assertIn("doruk_yogunluk_min", r2["uygulanmadi"])          # kısa örnek filmde film yapısı ölçüleri uygulanmaz
        self.assertEqual(os.path.isfile(os.path.join(kok, "KURGU", "EGRI_T0.png")), PILLOW)
        # birleştirme: --asama animatik → zaman_cizelgesi_t1 (T1 çizelgesi T0'dan kurulur); --asama kurgu T2 planı ister; yayin henüz yok
        self.assertEqual(Z.kos(zaman_cizelgesi, "--asama", "animatik", "--film", kok)[0], 0)
        self.assertTrue(os.path.isfile(os.path.join(kok, "KURGU", "surumler", "KURGU_PLANI_T1_v1.json")))
        self.assertEqual(Z.kos(zaman_cizelgesi, "--asama", "kurgu", "--film", kok)[0], 2)
        self.assertEqual(Z.kos(zaman_cizelgesi, "--asama", "yayin", "--film", kok)[0], 4)

    def test_t0_bozuk(self):
        def gec_eylem(kok):                                  # ilk plan 7 sn statik tutuluyor: ilk eylem > 5 sn
            p = os.path.join(kok, "_YONETMEN", "PLANLAR", "S01.json"); d = Z.jl(p)
            d["planlar"].insert(0, json.loads(json.dumps(d["planlar"][0])))
            z = d["planlar"][0]["zanaat"]; z["kod"] = "S01-P00"; z["plan_tipi"] = "kurulus"; z["kadrajdakiler"] = []
            z["eylem_zinciri"] = []; z["oyunculuk"] = {}; d["planlar"][0]["kullanim"] = {"bas": 0.5, "sure": 6.5}
            ortak.atomik_yaz(p, d)
        kok = self.zinc("ZN_T0B", gec_eylem)
        self.assertEqual(Z.kos(zaman_cizelgesi, "--asama", "kagit", "--film", kok)[0], 1)
        self.assertIn("ilk_eylem_gec", [h["madde"] for h in rapor(kok, "ZAMAN_T0.json")["hatalar"]])

    def test_kurulumsuz_kullanim(self):
        def bozuk(kok):
            p = os.path.join(kok, "HIKAYE.json"); h = Z.jl(p)
            h["KURULUMLAR"][0]["kurulum"] = "S03"; h["sahneler"][0]["kurulum"] = []; h["sahneler"][2]["kurulum"] = ["kur_anahtar"]
            ortak.atomik_yaz(p, h)
            y = os.path.join(kok, "_YONETMEN", "PLANLAR", "S01.json"); d = Z.jl(y)
            d["planlar"][1]["zanaat"].pop("kurulum", None); ortak.atomik_yaz(y, d)
            y = os.path.join(kok, "_YONETMEN", "PLANLAR", "S03.json"); d = Z.jl(y)
            d["planlar"][-1]["zanaat"]["kurulum"] = ["kur_anahtar"]; ortak.atomik_yaz(y, d)
        kok = self.zinc("ZN_T0K", bozuk)
        Z.kos(zaman_cizelgesi, "--asama", "kagit", "--film", kok)
        self.assertTrue({"kurulumsuz_kullanim", "kurulum_kullanim_yakin"} & {h["madde"] for h in rapor(kok, "ZAMAN_T0.json")["hatalar"]})

    def test_kamera_agaci_ve_bayat(self):
        kok = self.zinc("ZN_KA")
        self.assertEqual(Z.kos(kamera_agaci, "--yalniz-agac", "--film", kok)[0], 0)
        a = Z.jl(os.path.join(kok, "KAMERA_AGACI.json")); D = a["dugumler"]
        self.assertEqual(D["plan:2"]["ebeveyn"], "ana_kare:S01/KAM1")
        self.assertEqual(D["ana_kare:S01/KAM1"]["ebeveyn"], "plaka:kulube/ic_genel")
        self.assertEqual(a["paketler"][0]["basamak"], 1)
        self.assertEqual(a["bayat"], [])
        h = os.path.join(kok, "_YONETMEN", "HARITA_P1.json"); d = Z.jl(h)
        d["mekanlar"]["kulube"]["kurulumlar"]["KAM1"]["yon_derece"] = 300; ortak.atomik_yaz(h, d)
        Z.kos(plan_birlestir, "--film", kok); Z.kos(kamera_agaci, "--yalniz-agac", "--film", kok)
        b = set(Z.jl(os.path.join(kok, "KAMERA_AGACI.json"))["bayat"])
        self.assertTrue({"ana_kare:S01/KAM1", "plan:1", "plan:2", "ana_kare:S01/KAM3", "plan:3"} <= b, b)
        self.assertNotIn("plan:5", b)

    def test_kagit_tamam(self):
        kok = self.zinc("ZN_KT")
        Z.kos(istem_derle, "--hareket", "--film", kok); Z.kos(plan_denetim, "--tum", "--film", kok)
        Z.kos(zaman_cizelgesi, "--asama", "kagit", "--film", kok)
        kod, _ = Z.kos(kamera_agaci, "--film", kok)
        t = Z.jl(os.path.join(kok, "KAGIT_TAMAM.json"))
        self.assertEqual(kod, 1); self.assertFalse(t["tamam"])
        self.assertTrue(any("S0" in e for e in t["eksikler"]) and any("ISTEM" in e for e in t["eksikler"]), t["eksikler"])
        import kapi
        for kp, ad in (("S0", "S0_FILM.json"), ("ISTEM", "ISTEM_FILM.json")):
            ortak.atomik_yaz(os.path.join(kok, "_RAPOR", ad), kapi.rapor_kur(kp, "FILM", [], birimler=[1]))
        kod, _ = Z.kos(kamera_agaci, "--film", kok)
        t = Z.jl(os.path.join(kok, "KAGIT_TAMAM.json"))
        self.assertEqual(kod, 0, t["eksikler"]); self.assertTrue(t["tamam"])

    def test_cekim_listesi(self):
        kok = self.zinc("ZN_CL")
        self.assertEqual(Z.kos(cekim_listesi, "--film", kok)[0], 0)
        with open(os.path.join(kok, "_YONETMEN", "CEKIM_LISTESI_P1.md"), encoding="utf-8") as f: md = f.read()
        for k in ("S01-P01", "S02-P03", "S03-P02", "Başlangıç karesi", "Bitiş (sonraki klibin başı)", "It's late, Captain."): self.assertIn(k, md)
        self.assertNotIn("_derlenir", md)


if __name__ == "__main__":
    unittest.main()
