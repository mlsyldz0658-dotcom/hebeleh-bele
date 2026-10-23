"""Ad sözlüğü testi (TASARIM D-35, §6.1): veri/ADLAR.json, veri/kok_neden.json, veri/LISANSLAR.json.
Önekler ve kapı/sahne/ses biçimi, tekrar yok, ajan dosyaları, yeni_film.py'nin .bat adları, ORNEK_3_SAHNE alanları,
TASARIM'daki ajan·kip yazımları. Yalnız stdlib; ağ yok."""
import ast, json, os, re, unittest

HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
YZ = os.path.dirname(ARACLAR); DEPO = os.path.dirname(YZ)
VERI = os.path.join(ARACLAR, "veri")
AJAN_KLASORU = os.path.join(DEPO, ".claude", "agents")
BECERI_KLASORU = os.path.join(DEPO, ".claude", "skills")
TASARIM = os.path.join(BECERI_KLASORU, "film-yap", "tartisma", "TASARIM.md")
ORNEK = os.path.join(YZ, "FILMLER", "ORNEK_3_SAHNE", "SAHNELER.json")


def _tekrarsiz(ciftler):
    d = {}
    for k, v in ciftler:
        if k in d:
            raise ValueError("tekrarlanan anahtar: %s" % k)
        d[k] = v
    return d


def yukle(ad):
    with open(os.path.join(VERI, ad), encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=_tekrarsiz)


def acik(d):
    """'_' ile başlayan açıklama anahtarlarını atar."""
    return {k: v for k, v in d.items() if not k.startswith("_")}


AJAN_AD = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*")
KIP_AD = re.compile(r"[a-z][a-z0-9_]*")
KAPI_AD = re.compile(r"[A-Z][A-Z0-9_]*[a-z]?")
BAT_AD = re.compile(r"[A-Z0-9_]+\.bat")


class Adlar(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.a = yukle("ADLAR.json")
        cls.ajanlar = acik(cls.a["ajanlar"])
        cls.kapilar = acik(cls.a["kapilar"])
        cls.onek = {k: re.compile(v["desen"]) for k, v in acik(cls.a["onekler"]).items()}

    # --- biçim ve önekler -------------------------------------------------
    def test_zorunlu_bolumler(self):
        for k in ("_surum", "_aciklama", "onekler", "klasorler", "ajanlar", "beceriler", "kipler", "asamalar", "kapilar",
                  "plan_alanlari", "saglayici_turleri", "bat", "film_dosyalari"):
            self.assertIn(k, self.a)

    def test_onek_ornekleri_desene_uyar(self):
        for ad, v in acik(self.a["onekler"]).items():
            for o in v.get("ornek", []):
                self.assertTrue(self.onek[ad].fullmatch(o), "%s örneği desene uymuyor: %s" % (ad, o))

    def test_kapi_kodu_bicimi_ve_onekler(self):
        for kod, v in self.kapilar.items():
            self.assertTrue(KAPI_AD.fullmatch(kod), kod)
            self.assertFalse(self.onek["sahne_kimligi"].fullmatch(kod), "kapı kodu sahne kimliğine benziyor: " + kod)
            self.assertFalse(self.onek["kamera_kurulumu"].fullmatch(kod), kod)
            self.assertFalse(self.onek["kurulum_kademesi"].fullmatch(kod), kod)
            self.assertFalse(self.onek["kesin_karar"].fullmatch(kod), kod)
            self.assertFalse(self.onek["proje_bolumu"].fullmatch(kod), kod)
            self.assertNotEqual(kod, "BK")
            if re.fullmatch(r"K[0-9].*", kod):
                self.assertTrue(self.onek["sureklilik_kapisi"].fullmatch(kod), "K ile başlayan kapı yalnız K0/K1/K1ON: " + kod)
            if kod.startswith("BUT"):
                self.assertTrue(self.onek["butce_noktasi"].fullmatch(kod), kod)
                self.assertEqual(v["aile"], "butce", kod)
            if re.fullmatch(r"S[0-9].*", kod):
                self.assertTrue(self.onek["ses_kapisi"].fullmatch(kod), "ses kapısı tek hane: " + kod)
                self.assertEqual(v["aile"], "ses", kod)
            for asama in v["asama"]:
                self.assertIn(asama, self.a["asamalar"], "%s: bilinmeyen aşama %s" % (kod, asama))

    def test_ses_kapilari_tam(self):
        for n in range(9):
            self.assertIn("S%d" % n, self.kapilar)

    def test_kuyruk_kaynak_kapilari_kapi(self):
        for k in self.a["kuyruk_kaynak_kapilari"]:
            self.assertIn(k, self.kapilar)

    def test_ad_aileleri_kendi_desenine_uyar(self):
        for k in self.a["kurulum_kademeleri"]:
            self.assertTrue(self.onek["kurulum_kademesi"].fullmatch(k), k)
        for k in self.a["kesin_kararlar"]:
            self.assertTrue(self.onek["kesin_karar"].fullmatch(k), k)
        for k in self.a["proje_bolumleri"]:
            self.assertTrue(self.onek["proje_bolumu"].fullmatch(k), k)
        for k in self.a["asamalar"]:
            self.assertTrue(self.onek["asama"].fullmatch(k), k)
        for k in self.a["olcum0"]:
            self.assertTrue(self.onek["olcum0"].fullmatch(k), k)

    def test_kodlar_aileler_arasinda_tekrarsiz(self):
        hepsi = (list(self.kapilar) + list(self.a["asamalar"]) + self.a["kurulum_kademeleri"] + self.a["kesin_kararlar"]
                 + self.a["proje_bolumleri"] + list(acik(self.a["on_turlar"])) + self.a["olcum0"])
        tekrar = sorted({k for k in hepsi if hepsi.count(k) > 1})
        self.assertEqual(tekrar, [], "aynı kod iki ailede")

    # --- ajanlar, beceriler -----------------------------------------------
    def test_ajan_kadrosu(self):
        self.assertEqual(len(self.ajanlar), 21)
        sayi = {}
        for ad, v in self.ajanlar.items():
            self.assertTrue(AJAN_AD.fullmatch(ad), ad)
            sayi[v["rol"]] = sayi.get(v["rol"], 0) + 1
            for kip in v["kipler"]:
                self.assertTrue(KIP_AD.fullmatch(kip), "%s·%s" % (ad, kip))
            self.assertEqual(len(v["kipler"]), len(set(v["kipler"])), ad)
        self.assertEqual(sayi, self.a["ajan_rol_sayilari"])

    def test_eski_ve_kalkan_adlar_kadroda_yok(self):
        for ad in list(acik(self.a["ajanlar_eski"])) + list(acik(self.a["ajan_adlari_kalkan"])):
            self.assertNotIn(ad, self.ajanlar, ad)
        for ad, yerine in acik(self.a["ajan_adlari_kalkan"]).items():
            self.assertIn(yerine.split("·")[0], self.ajanlar, ad)

    def test_ajan_dosyalari(self):
        """Var olan her .claude/agents/<ad>.md ya kadroda ya da §3.2'nin kaldırılacak eski taslağıdır; dosyası
        henüz olmayan kadro ajanı atlanır (PR-4'te gelir). Dosyadaki name: alanı dosya adıyla aynıdır."""
        if not os.path.isdir(AJAN_KLASORU):
            self.skipTest(".claude/agents yok")
        izinli = set(self.ajanlar) | set(acik(self.a["ajanlar_eski"]))
        for f in sorted(os.listdir(AJAN_KLASORU)):
            if not f.endswith(".md"):
                continue
            ad = f[:-3]
            self.assertIn(ad, izinli, "ADLAR.json'da olmayan ajan dosyası: " + f)
            with open(os.path.join(AJAN_KLASORU, f), encoding="utf-8") as fh:
                m = re.search(r"^name:\s*(\S+)\s*$", fh.read(), re.M)
            if m:
                self.assertEqual(m.group(1), ad, f)

    def test_beceriler(self):
        self.assertEqual(sorted(self.a["beceriler"]), ["film-durum", "film-gelistir", "film-not", "film-yap"])
        if os.path.isdir(BECERI_KLASORU):
            for d in os.listdir(BECERI_KLASORU):
                if os.path.isfile(os.path.join(BECERI_KLASORU, d, "SKILL.md")):
                    self.assertIn(d, self.a["beceriler"], "ADLAR.json'da olmayan beceri: " + d)

    def test_tasarimdaki_ajan_kip_yazimlari(self):
        """TASARIM'da `ajan·kip` diye geçen her çiftin kipi ADLAR'da o ajanın kipidir."""
        if not os.path.isfile(TASARIM):
            self.skipTest("TASARIM.md yok")
        with open(TASARIM, encoding="utf-8") as f:
            metin = f.read()
        eksik = set()
        for ajan, kip in re.findall(r"([a-z][a-z-]+)·([a-z0-9_]+)", metin):
            if ajan in self.ajanlar and kip not in self.ajanlar[ajan]["kipler"]:
                eksik.add("%s·%s" % (ajan, kip))
        self.assertEqual(sorted(eksik), [])

    # --- .bat, plan alanları, sağlayıcılar --------------------------------
    def tum_batlar(self):
        b = self.a["bat"]
        return b["depo_koku"] + b["film_klasoru"] + list(b["gecis"]) + b["emekli"]

    def test_bat_adlari(self):
        hepsi = self.tum_batlar()
        self.assertEqual(len(hepsi), len(set(hepsi)), "tekrarlanan .bat adı")
        for ad in hepsi:
            self.assertTrue(BAT_AD.fullmatch(ad), ad)

    def test_yeni_film_bat_adlari_adlarda(self):
        yol = os.path.join(ARACLAR, "yeni_film.py")
        with open(yol, encoding="utf-8") as f:
            agac = ast.parse(f.read())
        # BATS bir sabit sözlük ya da sözlük döndüren işlev olabilir: anahtarı ".bat" ile biten her sözlük kalıbı sayılır.
        adlar = [k.value for d in ast.walk(agac) if isinstance(d, ast.Dict) for k in d.keys
                 if isinstance(k, ast.Constant) and isinstance(k.value, str) and k.value.lower().endswith(".bat")]
        self.assertTrue(adlar, "yeni_film.py'de .bat sözlüğü (BATS) bulunamadı")
        izinli = set(self.tum_batlar()) - set(self.a["bat"]["emekli"])
        for ad in adlar:
            self.assertIn(ad, izinli, "yeni_film.py ADLAR'da olmayan ya da emekli .bat üretiyor: " + ad)

    def test_ornek_film_alanlari_adlarda(self):
        if not os.path.isfile(ORNEK):
            self.skipTest("ORNEK_3_SAHNE yok")
        with open(ORNEK, encoding="utf-8") as f:
            d = json.load(f)
        p = self.a["plan_alanlari"]
        self.assertLessEqual(set(d), set(p["v1_kok"]) | set(p["kok"]))
        for k in d.get("karakterler", {}).values():
            self.assertLessEqual(set(k), set(p["v1_karakter"]) | set(p["karakter"]))
        for s in d.get("sahneler", []):
            self.assertLessEqual(set(s), set(p["v1_plan"]) | set(p["plan"]), s.get("no"))
            r = s.get("replik")
            if isinstance(r, dict):
                self.assertLessEqual(set(r), set(p["v1_replik"]) | set(p["replik"]))
                for c in r.get("cumleler", []):
                    self.assertLessEqual(set(c), set(p["v1_cumle"]))

    def test_plan_alanlari_tekrarsiz(self):
        for ad, liste in acik(self.a["plan_alanlari"]).items():
            self.assertEqual(len(liste), len(set(liste)), ad)

    def test_saglayici_turleri(self):
        turler = acik(self.a["saglayici_turleri"])
        hepsi = set()
        for tur, zincir in turler.items():
            self.assertTrue(KIP_AD.fullmatch(tur), tur)
            self.assertEqual(len(zincir), len(set(zincir)), tur)
            for s in zincir:
                self.assertTrue(KIP_AD.fullmatch(s), s)
            hepsi |= set(zincir)
        self.assertLessEqual(set(self.a["saglayici_yalniz_test"]), hepsi)
        for eski, yeni in self.a["saglayici_eski_adlar"].items():
            self.assertNotIn(eski, turler, "eski tür adı kullanılıyor: " + eski)
            self.assertTrue(yeni in turler or yeni in hepsi, yeni)

    def test_klasor_listeleri_tekrarsiz(self):
        for ad, liste in acik(self.a["klasorler"]).items():
            if isinstance(liste, list):
                self.assertEqual(len(liste), len(set(liste)), ad)


class KokNeden(unittest.TestCase):
    def test_sozluk(self):
        k = yukle("kok_neden.json")
        adlar = acik(yukle("ADLAR.json")["ajanlar"])
        alanlar = acik(k["alanlar"])
        kodlar = acik(k["kok_nedenler"])
        self.assertIn("nesne_zipladi", kodlar)  # §5.7 örneği
        for alan, v in alanlar.items():
            self.assertIn(v["varsayilan_sahip"], adlar, alan)
        for kod, v in kodlar.items():
            self.assertTrue(KIP_AD.fullmatch(kod), kod)
            self.assertIn(v["alan"], alanlar, kod)
            s = v["sahip"]
            self.assertTrue(s in adlar or s == "kullanici" or re.fullmatch(r"betik:[a-z0-9_]+\.py", s), "%s: sahip %s" % (kod, s))
            self.assertTrue(v.get("aciklama"), kod)
        for eski, yeni in acik(k["es_anlamlar"]).items():
            self.assertNotIn(eski, kodlar, eski)
            self.assertIn(yeni, kodlar, eski)


class Lisanslar(unittest.TestCase):
    def test_defter(self):
        d = yukle("LISANSLAR.json")
        alanlar = set(d["alanlar"])
        for ad, v in d["bilesenler"].items():
            self.assertEqual(set(v), alanlar, ad)
            self.assertIn(v["dogrulama"], ("bellekten", "dogrulandi", "bilinmiyor"), ad)
            self.assertIn(v["ticari_youtube"], ("evet", "hayir", "bilinmiyor"), ad)
            self.assertIn(v["kurulum"], ("KUR1", "KUR2", "KUR3", "P2", "hizmet", "dis_ikili", "dislandi"), ad)
            self.assertIsInstance(v["kullanici_araci"], bool, ad)
            self.assertIsInstance(v["kullanici_hizmeti"], bool, ad)
            self.assertIsInstance(v["gecisli"], list, ad)
            if v["dogrulama"] == "dogrulandi":  # kesinlik ancak kaynak ve tarihle
                self.assertTrue(v["kaynak"] and v["dogrulama_tarihi"], ad)
            else:
                self.assertIsNone(v["dogrulama_tarihi"], ad)
            if v["dogrulama"] == "bilinmiyor":
                self.assertNotEqual(v["ticari_youtube"], "evet", ad)
        for zorunlu in ("playwright", "pycapcut", "kurgu_koprusu", "demucs", "faster-whisper", "yunet", "sface", "dinov2-small",
                        "openvoice_v2", "rvc", "chatterbox", "musetalk", "ace-step", "pyloudnorm", "pyscenedetect", "fluidsynth",
                        "sf2_ses_bankasi", "gemini_api_ucretsiz", "muzik_cekirdek_seti", "gemini_muzik"):
            self.assertIn(zorunlu, d["bilesenler"])
        for ad in ("pycapcut", "kurgu_koprusu", "demucs"):  # D-36
            self.assertTrue(d["bilesenler"][ad]["kullanici_araci"], ad)
        for ad in ("flow", "ai84"):
            self.assertTrue(d["bilesenler"][ad]["kullanici_hizmeti"], ad)

    def test_dislananlar_kurulmaz(self):
        d = yukle("LISANSLAR.json")
        for ad in acik(d["dislananlar"]):
            self.assertNotIn(ad, d["bilesenler"], ad)


if __name__ == "__main__":
    unittest.main()
