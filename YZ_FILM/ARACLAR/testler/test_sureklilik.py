"""test_sureklilik — dünya defteri ve K0 (TASARIM §5.2, §7.2 K0, D-13, D-15, D-22, §6.10; [YN2] §4.5.13, Y10–Y16, Y57, Y58).

Kapsam:
  - Örnek film (ORNEK_3_SAHNE_ZANAAT) K0'dan HATA'sız geçer; defter planların bas/bit durumunu, olayları ve sahne uçlarını taşır; durum mirası
    (bir planın bitişi sonrakinin başlangıcı) ve el ↔ nesne eşitlemesi.
  - Sıçrama yakalama (bozuk varyantlar, _BOZUK/*.json "arac": "k0"): nesne ışınlanması, el değişimi, kostüm değişimi, durumun sonraki klibin
    başına taşınmaması, gerekçesiz fark, sahne ucu ↔ sözleşme uyuşmazlığı → K0 HATA + KUYRUK/YENIDEN_YAZ.json.
  - Duygu katmanı: gerekçesiz ifade sıçraması BAYRAK; gerekçeyle sessiz; zaman atlamasında şiddet bir azalır.
  - Dondurma ve komşuluk (Y58): dondurulmuş durumla yeni komşu çiftte sıçrama HATA, kullanıcı kararında BAYRAK.
  - A07a–A07c uçtan uca: film.py v2 görev zinciri `kaset` ile (ajan görevleri kasetten; kroki, plan_denetim, dilim, plan_birlestir,
    dunya_defteri, zaman_cizelgesi, kredi but1, cekim_listesi GERÇEK) → SAHNELER.json v2, DUNYA_DEFTERI.json, K0/T0, A07d'ye geçiş.
Ağ yok, kredi yok."""
import os, sys, json, io, glob, shutil, contextlib, unittest, unittest.mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import _zanaat as Z
import ortak, plan_ortak as po, plan_birlestir, dunya_defteri, plan_denetim, kroki


def hazirla(ad=None, varyant=None):
    kok = Z.kopya(ad)
    if varyant: Z.bozuk_uygula(kok, varyant)
    Z.kos(plan_birlestir, "--film", kok)
    return kok


def k0(kok):
    kod, _ = Z.kos(dunya_defteri, "--derle", "--denetle", "--film", kok)
    return kod, Z.jl(os.path.join(kok, "_RAPOR", "K0_FILM.json"))


class Defter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.kok = hazirla("ZN_DEFTER")
        cls.kod, cls.r = k0(cls.kok)
        cls.D = Z.jl(os.path.join(cls.kok, "DUNYA_DEFTERI.json"))

    def test_ornek_k0_gecer(self):
        self.assertEqual(self.kod, 0, self.r["hatalar"])
        self.assertIn(self.r["sonuc"], ("GEC", "BAYRAK"))
        self.assertEqual(self.r["hatalar"], [])

    def test_defter_semasi(self):
        D = self.D
        for k in ("_surum", "_uretim", "film", "planlar", "olaylar", "sahne_uclari", "zaman_cizgileri", "hikaye", "dondurulmus", "gozlenen"):
            self.assertIn(k, D)
        self.assertEqual(D["_uretim"]["arac_surum"], dunya_defteri.SURUM)
        self.assertEqual(set(D["sahne_uclari"]), {"S01", "S02", "S03"})
        self.assertTrue(all(v["hikaye_esit"] for v in D["sahne_uclari"].values()))
        self.assertTrue(D["hikaye"]["salt_okunur"])

    def test_durum_mirasi(self):
        P = self.D["planlar"]
        nolar = sorted(int(n) for n in P)
        for a, b in zip(nolar, nolar[1:]):
            if P[str(a)]["sahne"] == P[str(b)]["sahne"]:
                self.assertEqual(P[str(a)]["bit"], P[str(b)]["bas"], f"{a} → {b}: bitiş sonraki klibin başlangıcı olmalı")

    def test_el_nesne_esitlemesi_ve_olay(self):
        P = self.D["planlar"]
        bit2 = P["2"]["durum"]["bit"]          # S01-P02: anahtar sol elde
        self.assertEqual(bit2["nesneler"]["anahtar"].get("kimde"), "mara")
        self.assertEqual(bit2["nesneler"]["anahtar"].get("el"), "sol")
        self.assertEqual(bit2["karakterler"]["mara"]["eller"]["sol"]["tutar"], "anahtar")
        self.assertNotIn("nerede", bit2["nesneler"]["anahtar"])
        turler = {o["tur"] for o in self.D["olaylar"]}
        self.assertIn("nesne_al", turler)
        bit9 = P["9"]["durum"]["bit"]           # S03-P02: anahtar masaya bırakıldı, fener söndü
        self.assertIsNone(bit9["karakterler"]["mara"]["eller"]["sol"]["tutar"])

    def test_ses_alanlari(self):
        self.assertIn("S01", self.D["ses_alanlari"])


class Sicrama(unittest.TestCase):
    """Bozuk varyantlar: her biri tek bir sıçramayı içerir ve K0 onu adıyla yakalar."""
    def _dene(self, ad):
        v = Z.varyant(ad)
        kok = hazirla(f"ZN_K0_{ad}", ad)
        kod, r = k0(kok)
        b = v["beklenen"]
        bulunan = [h for h in r["hatalar"] if h["madde"] == b["madde"] and (not b.get("tur") or h.get("tur") == b["tur"])]
        self.assertTrue(bulunan, f"{ad}: {b} beklenirken {Z.maddeler(r)}")
        self.assertEqual(kod, 1, ad)
        self.assertIn(r["sonuc"], ("HATA", "KISMI"))
        return kok, r, bulunan

    def test_nesne_isinlanmasi(self): self._dene("nesne_isinlanmasi")
    def test_el_degisimi(self): self._dene("el_degisimi")
    def test_kostum_degisimi(self): self._dene("kostum_degisimi")
    def test_gerekcesiz_fark(self): self._dene("gerekcesiz_fark")
    def test_sahne_cikisi_sozlesmeye_uymuyor(self): self._dene("sahne_cikisi")

    def test_durum_sonraki_klibin_basina_tasinmadi(self):
        kok, r, b = self._dene("durum_tasinmadi")
        self.assertEqual(b[0]["plan"], 3)
        self.assertTrue(any("anahtar" in str(h.get("yol")) or "eller" in str(h.get("yol")) for h in b))

    def test_hatalar_yeniden_yaz_kuyruguna(self):
        kok, r, b = self._dene("nesne_isinlanmasi")
        q = Z.jl(os.path.join(kok, "KUYRUK", "YENIDEN_YAZ.json"))
        md = q.get("maddeler") if isinstance(q, dict) else q
        self.assertTrue(any(m.get("kapi") == "K0" and (m.get("konum") or {}).get("sahne") == "S01" for m in md), md)

    def test_bozuk_varyantlar_kaset_planlarina_dokunmaz(self):
        for ad in Z.varyantlar():
            for x in Z.varyant(ad)["degisiklikler"]:
                self.assertFalse(x["dosya"].startswith("_KASET"), ad)


class Duygu(unittest.TestCase):
    def _planlar(self, kok, sid):
        p = os.path.join(kok, "_YONETMEN", "PLANLAR", f"{sid}.json"); return p, Z.jl(p)

    def test_gerekcesiz_ifade_sicramasi_bayrak(self):
        kok = Z.kopya("ZN_DUYGU1")
        p, d = self._planlar(kok, "S01")
        d["planlar"][2]["zanaat"]["oyunculuk"]["mara"]["dis_ifade"]["bas"] = "ofkeli"     # önceki plan "dikkatli" bitti
        ortak.atomik_yaz(p, d); Z.kos(plan_birlestir, "--film", kok)
        kod, r = k0(kok)
        self.assertEqual(kod, 0, r["hatalar"])
        self.assertIn("duygu_sicramasi_gerekcesiz", [b["madde"] for b in r["bayraklar"]])

    def test_gerekceli_ifade_gecisi_sessiz(self):
        kok = Z.kopya("ZN_DUYGU2")
        p, d = self._planlar(kok, "S01")
        o = d["planlar"][2]["zanaat"]["oyunculuk"]["mara"]
        o["dis_ifade"]["bas"] = "ofkeli"; o["ifade_gecis_neden"] = "kapıdaki sesi duyunca yüzü sertleşir (kesmede)"
        ortak.atomik_yaz(p, d); Z.kos(plan_birlestir, "--film", kok)
        kod, r = k0(kok)
        self.assertNotIn("duygu_sicramasi_gerekcesiz", [b["madde"] for b in r["bayraklar"]])

    def test_zaman_atlamasinda_siddet_azalir(self):
        d = dunya_defteri.bos_durum()
        d["karakterler"]["mara"] = {"duygu": {"durum": "korku", "siddet": 3, "izler": []}}
        dunya_defteri._duygu_azalt(d)
        self.assertEqual(d["karakterler"]["mara"]["duygu"]["siddet"], 2)


class DondurKomsuluk(unittest.TestCase):
    def test_kurgu_sirasi_degisince_dondurulmus_sicrama(self):
        kok = hazirla("ZN_KOMSU")
        k0(kok)
        kod, _ = Z.kos(dunya_defteri, "--dondur", "1,2,3", "--film", kok)
        self.assertEqual(kod, 0)
        D = Z.jl(os.path.join(kok, "DUNYA_DEFTERI.json"))
        self.assertEqual(set(D["dondurulmus"]), {"1", "2", "3"})
        s = Z.jl(os.path.join(kok, "SAHNELER.json"))
        self.assertTrue(all(p["uretim"]["durum_dondu"]["bas"] for p in s["sahneler"] if p["no"] in (1, 2, 3)))
        kod, _ = Z.kos(dunya_defteri, "--komsuluk", "--sira", "1,2,3", "--film", kok)
        self.assertEqual(kod, 0)
        kod, _ = Z.kos(dunya_defteri, "--komsuluk", "--sira", "2,1,3", "--film", kok)      # 1 ile 2 yer değişti: anahtar zıplar
        r = Z.jl(os.path.join(kok, "_RAPOR", "K0_KOMSULUK.json"))
        self.assertEqual(kod, 1)
        self.assertIn("dondurulmus_komsu_sicramasi", [h["madde"] for h in r["hatalar"]])
        kod, _ = Z.kos(dunya_defteri, "--komsuluk", "--sira", "2,1,3", "--kullanici", "--film", kok)   # kullanıcının CapCut kararı
        r = Z.jl(os.path.join(kok, "_RAPOR", "K0_KOMSULUK.json"))
        self.assertEqual(kod, 0); self.assertEqual(r["hatalar"], [])
        self.assertIn("dondurulmus_komsu_sicramasi", [b["madde"] for b in r["bayraklar"]])


class KasetA07(unittest.TestCase):
    """A07a → A07c film.py v2 görev zinciri; A00–A06 tamam sayılır (HIKAYE.json kilitli örnekten gelir)."""
    def setUp(self):
        import film
        self.film = film
        self.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "yerel"}); self.env.start()
        KasetA07.n = getattr(KasetA07, "n", 0) + 1
        self.ad = f"ZN_KASET_A07_{KasetA07.n}"
        self.kok = os.path.join(_ortam.VERI, "FILMLER", self.ad)
        kod, r = self.k("yeni", "--konu", "kapıdaki kaptan", "--ad", self.ad)
        self.assertEqual(kod, 0, r)
        for d in ("EVREN", "_SES", "_KASET"):
            shutil.copytree(os.path.join(Z.ORNEK, d), os.path.join(self.kok, d))
        shutil.copyfile(os.path.join(Z.ORNEK, "HIKAYE.json"), os.path.join(self.kok, "HIKAYE.json"))

    def tearDown(self): self.env.stop()

    def k(self, *a):
        a = list(a) + (["--film", self.ad] if a[0] != "yeni" else [])
        with contextlib.redirect_stdout(io.StringIO()) as o: kod = self.film.main(a)
        try: return kod, json.loads(o.getvalue())
        except ValueError: return kod, o.getvalue()

    def nabiz(self):
        _ortam.kanca_nabzi(self.kok)

    def test_kaset_planlarla_ayni(self):
        for i, s in ((1, "S01"), (2, "S02"), (3, "S03")):
            self.assertEqual(Z.jl(os.path.join(Z.ORNEK, "_KASET", "AJAN", "A07b_YP", str(i), "plan.json")),
                             Z.jl(os.path.join(Z.ORNEK, "_YONETMEN", "PLANLAR", f"{s}.json")), s)
        self.assertEqual(Z.jl(os.path.join(Z.ORNEK, "_KASET", "AJAN", "A07a_YH", "hepsi", "HARITA.json")),
                         Z.jl(os.path.join(Z.ORNEK, "_YONETMEN", "HARITA_P1.json")))

    def test_A07_kaset(self):
        from saglayicilar import kaset
        film = self.film; HAT = film.HAT
        bas = [a.kod for a in HAT.ASAMALAR].index("A07a")
        orj_aktif = film.Defter.aktif
        def aktif(d):                                         # A00–A06 tamam sayılır; A07d'de durulur
            for a in HAT.ASAMALAR[bas:]:
                if a.kod == "A07d": return a, d.coz(a)
                if a.istege_bagli and not d.asama_gorevleri(a.kod): continue
                c = d.coz(a)
                if c["durum"] in ("tamam", "kismi"): continue
                return a, c
            return None, None
        gercek, kasetten = [], []
        orj_kos = film.Defter.betik_kos
        def betik_kos(d, g):
            gercek.append(g["arac"] + " " + " ".join(g["argumanlar"])); return orj_kos(d, g)
        asamalar = []
        with unittest.mock.patch.object(film.Defter, "aktif", aktif), unittest.mock.patch.object(film.Defter, "betik_kos", betik_kos), \
                unittest.mock.patch.object(film, "disk_bos_gb", lambda y: 500.0):
            for _ in range(80):
                self.nabiz()
                kod, r = self.k("sonraki")
                self.assertIsInstance(r, dict, r)
                asama = (r.get("asama") or "").split(" ")[0]
                if not asamalar or asamalar[-1] != asama: asamalar.append(asama)
                if asama == "A07d": break
                self.assertIn(r["tur"], ("ajan", "betik"), r)
                for gz in r["gorevler"]:
                    if r["tur"] == "betik":
                        kc, rc = self.k("calis", gz["id"])
                        log = ""
                        lp = os.path.join(self.kok, "_GOREV", gz["id"], "CALISMA.log")
                        if os.path.isfile(lp):
                            with open(lp, encoding="utf-8") as f: log = f.read()[-1500:]
                        self.assertEqual(kc, 0, (gz["id"], rc, log)); continue
                    self.k("basla", gz["id"])
                    g = Z.jl(os.path.join(self.kok, "_GOREV", gz["id"], "GOREV.json"))
                    kaset.ajan_oynat(self.kok, g)
                    kb, rb = self.k("bitir", gz["id"]); self.assertEqual(kb, 0, rb)
            else:
                self.fail(f"A07d'ye ulaşılamadı: {asamalar}")
        self.assertEqual(asamalar, ["A07a", "A07b", "A07c", "A07d"])
        kok = self.kok; rap = lambda ad: Z.jl(os.path.join(kok, "_RAPOR", ad))
        self.assertIn(rap("HARITA_t1.json")["sonuc"], ("GEC", "BAYRAK"), rap("HARITA_t1.json")["hatalar"])
        self.assertIn(rap("Z0_SAHNE_t1.json")["sonuc"], ("GEC", "BAYRAK"), rap("Z0_SAHNE_t1.json")["hatalar"])
        self.assertIn(rap("K0_FILM.json")["sonuc"], ("GEC", "BAYRAK"), rap("K0_FILM.json")["hatalar"])
        self.assertIn(rap("ZAMAN_T0.json")["sonuc"], ("GEC", "BAYRAK"), rap("ZAMAN_T0.json")["hatalar"])
        s = Z.jl(os.path.join(kok, "SAHNELER.json"))
        self.assertEqual(s["_surum"], 2); self.assertEqual(len(s["sahneler"]), 9)
        self.assertTrue(all(p.get("zanaat") and p.get("_derlenir") for p in s["sahneler"]))
        self.assertTrue(os.path.isfile(os.path.join(kok, "DUNYA_DEFTERI.json")))
        self.assertTrue(os.path.isfile(os.path.join(kok, "KURGU", "surumler", "KURGU_PLANI_T0.json")))
        self.assertTrue(os.path.isfile(os.path.join(kok, "_YONETMEN", "CEKIM_LISTESI_P1.md")))
        self.assertTrue(os.path.isfile(os.path.join(kok, "_YONETMEN", "KROKI_ONERI.json")))
        self.assertEqual(sorted(os.path.basename(p) for p in glob.glob(os.path.join(kok, "_YONETMEN", "PLANLAR", "*.json"))),
                         ["G1.json", "G2.json", "G3.json"])
        self.assertEqual(kasetten, [])                                          # betik kaseti yok (kredi.py but1 gerçek)
        self.assertTrue(rap("BUT1_FILM.json")["_uretim"]["gorev"].startswith("A07c-B1-"))
        g = " | ".join(gercek)
        for alt in ("kroki.py --karsilikli", "plan_denetim.py --harita", "kroki.py --ciz", "dilim.py --asama A07b",
                    "plan_denetim.py --sahne --tum", "plan_birlestir.py", "dunya_defteri.py --derle --denetle",
                    "zaman_cizelgesi.py --asama kagit", "cekim_listesi.py", "kredi.py but1"):
            self.assertIn(alt, g)


if __name__ == "__main__":
    unittest.main()
