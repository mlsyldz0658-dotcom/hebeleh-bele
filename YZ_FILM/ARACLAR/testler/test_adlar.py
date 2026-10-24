"""Ad sözlüğü testi (TASARIM D-35, §6.1): veri/ADLAR.json, veri/kok_neden.json, veri/LISANSLAR.json.
Önekler ve kapı/sahne/ses biçimi, tekrar yok, ajan dosyaları, yeni_film.py'nin .bat adları, ORNEK_3_SAHNE alanları,
TASARIM'daki ajan·kip yazımları ve kodda sabit dizi olarak geçen adlar (KoddaAdlar: kapı, ajan·kip, kör paket kipi, kök neden,
kaynak kapı, film klasörü, veri dosyası). Yalnız stdlib; ağ yok."""
import ast, json, os, re, sys, unittest

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


def _py_dosyalari(atla=("__pycache__", "testler", "kurgu_koprusu")):
    """ARACLAR altındaki araç dosyaları (testler ve dış kurgu köprüsü hariç): (göreli yol, ast ağacı)."""
    for kok, ds, fs in os.walk(ARACLAR):
        ds[:] = sorted(d for d in ds if d not in atla)
        for f in sorted(fs):
            if f.endswith(".py"):
                p = os.path.join(kok, f)
                with open(p, encoding="utf-8-sig") as fh:
                    try: yield os.path.relpath(p, ARACLAR).replace(os.sep, "/"), ast.parse(fh.read())
                    except SyntaxError: continue


def _sabit(n): return n.value if isinstance(n, ast.Constant) and isinstance(n.value, str) else None


def _cagri_adi(n):
    f = n.func
    if isinstance(f, ast.Attribute): return (f.value.id if isinstance(f.value, ast.Name) else None), f.attr
    return None, (f.id if isinstance(f, ast.Name) else None)


class FilmDosyalariEk(unittest.TestCase):
    def test_son_tur_adlari(self):
        """film.py ajanının istediği dosya adları ADLAR film_dosyalari'nda (birleştirme son turu)."""
        with open(os.path.join(ARACLAR, "veri", "ADLAR.json"), encoding="utf-8") as f: fd = json.load(f)["film_dosyalari"]
        for kl, ad in (("_HIKAYE_ODASI", "EVREN_OZETI.md"), ("_HIKAYE_ODASI", "06_SENARYO_v1<NN>.json"),
                       ("_YONETMEN", "KART_ISTEGI_P<n>.json"), ("_YONETMEN", "ONARIM_f<n>.json"),
                       ("_RAPOR", "G1/HAKEM_G1_t<n>.json"), ("_SES", "SES_TASARIMI_G<i>.md"), ("_SES", "SES_G<i>.json")):
            self.assertIn(ad, fd[kl], (kl, ad))


class StdoutKorumasi(unittest.TestCase):
    def test_reconfigure_korumali(self):
        """sys.stdout.reconfigure her araçta korumalı (hasattr ya da try): stdout StringIO'ya yönlendirilmişken araç içe alınabilir."""
        kotu = []
        for kok, ds, fs in os.walk(ARACLAR):
            ds[:] = [d for d in ds if d not in ("__pycache__", "testler")]
            for f in fs:
                if not f.endswith(".py"): continue
                p = os.path.join(kok, f)
                with open(p, encoding="utf-8") as h: satir = h.read().split("\n")
                for i, s in enumerate(satir):
                    onceki = satir[i - 1].strip() if i else ""
                    if s.strip().startswith("sys.stdout.reconfigure(") and not ("hasattr(sys.stdout" in onceki or onceki == "try:"):
                        kotu.append(f"{os.path.relpath(p, ARACLAR)}:{i + 1}")
        self.assertEqual(kotu, [])


class KoddaAdlar(unittest.TestCase):
    """D-35: kodda sabit dizi olarak geçen adlar ADLAR.json'dadır. Yalnız kesin okunan kalıplar taranır (değişkenle kurulan ad atlanır),
    böylece yanlış alarm olmaz: hat/asamalar.py R()/J()/B(kor_paket --kip), kapi.kaydet/rapor_kur ve ses_ortak.rapor kapı kodları,
    kok_neden= ve kaynak_kapi= değerleri, os.path.join(film, "<AD>") film klasörü adları, veri/*.json dosyaları."""
    @classmethod
    def setUpClass(cls):
        cls.a = yukle("ADLAR.json"); cls.kapilar = set(acik(cls.a["kapilar"]))
        cls.ajanlar = acik(cls.a["ajanlar"]); cls.agaclar = list(_py_dosyalari())
        cls.asamalar = next(t for r, t in cls.agaclar if r == "hat/asamalar.py")

    def cagrilar(self, agac=None):
        for n in ast.walk(agac or self.asamalar):
            if isinstance(n, ast.Call): yield n

    def test_asama_kapilari_adlarda(self):
        """hat/asamalar.py'deki her R("<KAPI>") ADLAR kapilar'dadır (YEREL_KAPILAR da dahil; yerel liste artık yedek değildir)."""
        say, eksik = 0, set()
        for n in self.cagrilar():
            if _cagri_adi(n)[1] == "R" and n.args and _sabit(n.args[0]):
                say += 1
                if _sabit(n.args[0]) not in self.kapilar: eksik.add(_sabit(n.args[0]))
        self.assertGreater(say, 20, "R() çağrıları bulunamadı (tarama bozuk)")
        self.assertEqual(sorted(eksik), [])
        for n in ast.walk(self.asamalar):
            if isinstance(n, ast.Assign) and any(isinstance(h, ast.Name) and h.id == "YEREL_KAPILAR" for h in n.targets):
                self.assertLessEqual({_sabit(e) for e in n.value.elts}, self.kapilar)

    def test_asama_ajan_kipleri_adlarda(self):
        say, hata = 0, []
        for n in self.cagrilar():
            if _cagri_adi(n)[1] == "J" and len(n.args) >= 2:
                say += 1
                ajan, kip = _sabit(n.args[1]), (_sabit(n.args[2]) if len(n.args) > 2 else None)
                if ajan not in self.ajanlar: hata.append(ajan); continue
                if kip and kip not in self.ajanlar[ajan]["kipler"]: hata.append("%s·%s" % (ajan, kip))
        self.assertGreater(say, 20)
        self.assertEqual(hata, [])

    def test_kor_paket_kipleri_adlarda(self):
        kipler = set(self.a["kipler"]["kor_paket"])
        for n in self.cagrilar():
            a = [_sabit(x) for x in n.args]
            if _cagri_adi(n)[1] == "B" and "kor_paket.py" in a and "--kip" in a and a.index("--kip") + 1 < len(a):
                k = a[a.index("--kip") + 1]
                if k: self.assertIn(k, kipler, "asamalar.py kor_paket --kip " + k)
        kp = next(t for r, t in self.agaclar if r == "kor_paket.py")
        for n in ast.walk(kp):
            if isinstance(n, ast.Assign) and any(isinstance(h, ast.Name) and h.id in ("KAGIT_KIPLERI", "IZLEME_KIPLERI") for h in n.targets):
                self.assertLessEqual({_sabit(e) for e in n.value.elts}, kipler)

    def test_rapor_kapi_kodlari_adlarda(self):
        """kapi.kaydet(klasor, "<KAPI>", …), kapi.rapor_kur("<KAPI>", …), so.rapor(film, "<KAPI>", …)."""
        say, eksik = 0, set()
        for r, t in self.agaclar:
            for n in self.cagrilar(t):
                on, ad = _cagri_adi(n); i = None
                if on == "kapi" and ad == "kaydet": i = 1
                elif on == "kapi" and ad == "rapor_kur": i = 0
                elif on in ("so", "ses_ortak") and ad == "rapor": i = 1
                if i is not None and len(n.args) > i and _sabit(n.args[i]):
                    say += 1
                    if _sabit(n.args[i]) not in self.kapilar: eksik.add("%s: %s" % (r, _sabit(n.args[i])))
        self.assertGreater(say, 5)
        self.assertEqual(sorted(eksik), [])

    def test_kok_neden_ve_kaynak_kapi_degerleri(self):
        if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
        import plan_ortak
        k = yukle("kok_neden.json"); kodlar = set(acik(k["kok_nedenler"]))
        self.assertLessEqual(set(plan_ortak.KOK_ESLEME.values()), kodlar, "KOK_ESLEME sözlükte olmayan koda eşliyor")
        gecerli = kodlar | set(acik(k["es_anlamlar"])) | set(plan_ortak.KOK_ESLEME)
        kaynak = set(self.a["kuyruk_kaynak_kapilari"]); say, hata = 0, set()
        for r, t in self.agaclar:
            for n in ast.walk(t):
                ciftler = []
                if isinstance(n, ast.keyword) and n.arg in ("kok_neden", "kaynak_kapi"): ciftler = [(n.arg, n.value)]
                elif isinstance(n, ast.Dict): ciftler = [(_sabit(a), v) for a, v in zip(n.keys, n.values) if a is not None]
                for ad, v in ciftler:
                    deger = _sabit(v)
                    if ad == "kok_neden" and deger:
                        say += 1
                        if deger not in gecerli: hata.add("%s: kok_neden %s" % (r, deger))
                    if ad == "kaynak_kapi" and deger and deger not in kaynak: hata.add("%s: kaynak_kapi %s" % (r, deger))
        self.assertGreater(say, 30)
        self.assertEqual(sorted(hata), [])

    def test_film_klasoru_adlari(self):
        """os.path.join(film, "<AD>…") ile açılan büyük harfli ya da '_' önekli üst ad ADLAR klasorler.film / film_dosyalari'ndadır."""
        izin = set(self.a["klasorler"]["film"]) | set(self.a["film_dosyalari"]["kok"]) | set(self.a["film_dosyalari"])
        say, eksik = 0, set()
        for r, t in self.agaclar:
            for n in self.cagrilar(t):
                if _cagri_adi(n)[1] != "join" or len(n.args) < 2: continue
                if not (isinstance(n.args[0], ast.Name) and n.args[0].id in ("film", "film_kok")): continue
                s = _sabit(n.args[1])
                if not s: continue
                ust = s.replace("\\", "/").split("/")[0]
                if re.fullmatch(r"[A-Z0-9_]+(\.[A-Za-z0-9]+)?", ust) or ust.startswith("_"):
                    say += 1
                    if ust not in izin: eksik.add("%s: %s" % (r, ust))
        self.assertGreater(say, 50)
        self.assertEqual(sorted(eksik), [])

    def test_veri_dosyalari_adlarda(self):
        v = self.a["veri_dosyalari"]; liste = set(v["veri_sozlukleri"]) | set(v["esik_dosyalari"])
        for f in os.listdir(VERI):
            if f.endswith(".json"): self.assertIn("veri/" + f, liste, "ADLAR veri_dosyalari'nda olmayan veri dosyası: " + f)
        for kapi_kodu in ("KONU", "BRIFING", "ONERI", "JURI", "YAPI", "PLAN_ELESTIRI", "HAZIRLIK", "HARITA", "KUR", "DERS", "S2a"):
            self.assertIn(kapi_kodu, self.kapilar)
        for kip in ("ilk2dk", "kesici"):
            self.assertIn(kip, self.a["kipler"]["kor_paket"])
        self.assertIn(".claude/_ESKI/agents", self.a["klasorler"]["depo"])
        self.assertIn("yeni_film.py artık üretmiyor", self.a["bat"]["gecis"]["MEMMET_GIRIS.bat"])


class KokNeden(unittest.TestCase):
    def test_birlestirme_kodlari(self):
        kodlar = acik(yukle("kok_neden.json")["kok_nedenler"])
        for kod, alan, sahip in (("eylem_zinciri", "yonetmen", "yonetmen"), ("diyalog_suresi", "yonetmen", "yonetmen"),
                                 ("replik_sigmiyor", "ses", "yonetmen"), ("teknik_kusur", "sureklilik", "sureklilik-denetcisi"),
                                 ("gorsel_teknik", "sureklilik", "sureklilik-denetcisi")):
            self.assertEqual((kodlar[kod]["alan"], kodlar[kod]["sahip"]), (alan, sahip), kod)

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
                        "sf2_ses_bankasi", "gemini_api_ucretsiz", "muzik_cekirdek_seti", "gemini_muzik",
                        "stable-ts", "audio-separator", "ffmpeg", "real-esrgan", "scipy", "torchaudio", "mediapipe_modelleri"):
            self.assertIn(zorunlu, d["bilesenler"])
        # Bu sürümde hiçbir satır kaynağından doğrulanmadı: 'dogrulandi' yazılmaz (doğrulama uydurulmaz).
        self.assertEqual([a for a, v in d["bilesenler"].items() if v["dogrulama"] == "dogrulandi"], [])
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
