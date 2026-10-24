"""Beceri denetimi testi (TASARIM §4, §6.2 beceri_denetim, §4.8 senaryoları 1–7, §9 adım 6 kabul şartı).

- Gerçek depo: 4 SKILL.md, film-yap destek dosyaları, şablonlar ve şemalar HATA'sız; hat/asamalar.py'deki her ajan görevinin şablonu var;
  reference/hat.md güncel; istem-muhendisi.md ve muzik-supervizoru.md .claude/_ESKI/agents/'e taşınmış.
- Fikstür: denetimin yakaladıkları (konu dışı soru, araç/rol, kör ajan, model, açıklama uzunluğu, şablon yer tutucusu, OZET biçimi,
  kör şablon sızıntısı) ve yakalamadıkları (olumsuzlanan kural satırı).
- Şemalar: TASARIM §5.5/§5.7/§5.8 örnekleri şemalardan geçer, bozuk örnek geçmez.
- §4.8 senaryoları 1–7 geçici veri kökünde, sahte sağlayıcıyla (film.py + kanca.py gerçek süreç)."""
import os, sys, json, shutil, tempfile, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import beceri_denetim as bd

DEPO = os.path.dirname(os.path.dirname(ARACLAR))
FY = os.path.join(DEPO, ".claude", "skills", "film-yap")


def yaz(p, t):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write(t)


def sema(ad):
    with open(os.path.join(FY, "semalar", ad + ".json"), encoding="utf-8") as f: return json.load(f)


class GercekDepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r = bd.denetle(DEPO)

    def bizim(self, x):
        d = x["dosya"] or ""
        return d.startswith(os.path.join(".claude", "skills")) or d == "CLAUDE.md"

    def test_beceriler_sablonlar_semalar_hatasiz(self):
        h = [x for x in self.r["maddeler"] if x["seviye"] == "HATA" and self.bizim(x)]
        self.assertEqual(h, [], json.dumps(h, ensure_ascii=False, indent=1))

    def test_butun_ajan_gorevlerinin_sablonu_var(self):
        self.assertFalse([x for x in self.r["maddeler"] if x["madde"] in ("sablon_eksik", "sablon_esik", "sablon_yer_tutucu")])
        self.assertGreaterEqual(len(os.listdir(os.path.join(FY, "sablonlar"))), 60)

    def test_hata_sifir_bayrak_yalniz_henuz_olmayan_dosya(self):
        """Birleştirme turu: HATA 0; BAYRAK yalnız depoda henüz olmayan (olcum0/) ya da makineye özgü (python_yolu.txt) atıflar."""
        self.assertEqual([x for x in self.r["maddeler"] if x["seviye"] == "HATA"], [])
        b = [x for x in self.r["maddeler"] if x["seviye"] == "BAYRAK"]
        self.assertEqual({x["madde"] for x in b} - {"atif_depo"}, set(), json.dumps(b, ensure_ascii=False, indent=1))
        for x in b: self.assertRegex(x["neden"], r"olcum0/|python_yolu\.txt")

    def test_ajanlarda_sabit_sayi_yok_sablonda_esik(self):
        for ad in ("hikaye-mimari", "hikaye-yazari"):
            g = bd.oku(os.path.join(DEPO, ".claude", "agents", ad + ".md"))
            self.assertLessEqual(len(__import__("re").findall(r"(?:≥|≤|en çok|en az)\s*\d", g)), 2, ad)   # yalnız '≤ 5 satır' protokolü
        for s, anahtarlar in (("A03_hikaye-mimari.md", ("kanca_cumlesi_karakter_max", "seri_sorusu_max", "kostum_varyant_max_karakter")),
                              ("A05_hikaye-yazari_yapi.md", ("bolum_sayisi_max", "doruk_yogunluk_min")),
                              ("A05_hikaye-yazari_senaryo.md", ("ekran_disi_tasima_kelime_esigi", "gosterisiz_aralik_max_sn"))):
            m = bd.oku(os.path.join(FY, "sablonlar", s))
            for k in anahtarlar: self.assertIn("{{esik:%s}}" % k, m, s)
            self.assertNotIn("{{", bd.sablon_doldur(m))
        self.assertNotIn("_HIKAYE_ODASI", bd.oku(os.path.join(DEPO, ".claude", "agents", "oyuncu.md")))

    def test_son_tur_hikaye_esikleri_yer_tutucu(self):
        """A03/A04/A05 şablonlarındaki düz sayılar hikaye_esikleri.json anahtarlarına bağlandı (son tur B)."""
        bek = {"merak_sorusu_min": 8, "kurulum_min": 5, "kapak_imgesi_max_sn": 120, "ornek_replik_max": 5, "ayni_karakter_ardisik_max": 3}
        E = bd.esikleri_yukle(DEPO)
        for k, v in bek.items(): self.assertEqual(E.get(k), v, k)
        for s, anahtarlar in (("A03_hikaye-mimari.md", ("merak_sorusu_min", "kurulum_min", "kapak_imgesi_max_sn", "ornek_replik_max")),
                              ("A04_hikaye-mimari.md", ("merak_sorusu_min", "kurulum_min", "kapak_imgesi_max_sn", "ornek_replik_max")),
                              ("A05_hikaye-yazari_senaryo.md", ("ayni_karakter_ardisik_max",))):
            m = bd.oku(os.path.join(FY, "sablonlar", s))
            for k in anahtarlar: self.assertIn("{{esik:%s}}" % k, m, s)
            dolu = bd.sablon_doldur(m)
            self.assertNotIn("{{", dolu)
            for duz in ("en az 8,", "en az 5;", "ilk 120 sn", "en çok 5,", "en çok 3 blok"):
                if duz in m: self.fail("%s: düz sayı kaldı: %s" % (s, duz))

    def test_son_tur_gorev_dosya_adlari(self):
        """Şablonlar görev kaydının dosya adlarını kullanır: A06 RV CIKTI/senaryo.json, kart KART_ISTEGI_P*, A11 hakem HAKEM_G1."""
        import hat.asamalar as HAT
        rv = next(s for s in HAT.asama("A06").gorevler if s.kod == "RV")
        m = bd.oku(os.path.join(FY, "sablonlar", "A06_hikaye-yazari_revizyon.md"))
        for c in rv.cikti: self.assertIn("`%s`" % c, m)
        kt = next(s for s in HAT.asama("A07a").gorevler if s.kod == "KT")
        self.assertIn("_YONETMEN/KART_ISTEGI_P*.json", kt.girdi)
        for s in ("A07a_kart-tasarimcisi.md", "A10d_kart-tasarimcisi.md"):
            k = bd.oku(os.path.join(FY, "sablonlar", s)); self.assertIn("KART_ISTEGI_P<n>.json", k); self.assertNotIn("`GIRDI/KART_ISTEGI.json`", k)
        rf = next(s for s in HAT.asama("A11").gorevler if s.kod == "RF")
        self.assertEqual(rf.cikti, ("CIKTI/HAKEM_G1.json",))
        self.assertIn("`CIKTI/HAKEM_G1.json`", bd.oku(os.path.join(FY, "sablonlar", "A11_sureklilik-denetcisi_hakem.md")))

    def test_kurgu_ve_kesici_kararlari_kok_neden_ve_bulgu_ister(self):
        m = bd.oku(os.path.join(FY, "sablonlar", "A12_kurgucu_duzelt.md"))
        self.assertIn("kararlar[{madde, bulgu, kok_neden,", m)
        for s in ("A12_kesici_animatik.md", "A16_kesici_kurgu.md"):
            self.assertIn("kesmeler[{id, kok_neden,", bd.oku(os.path.join(FY, "sablonlar", s)), s)

    def test_hat_tablosu_guncel(self):
        self.assertFalse([x for x in self.r["maddeler"] if x["madde"] == "hat_tablosu"])

    def test_eski_taslaklar_tasindi(self):
        for ad in ("istem-muhendisi.md", "muzik-supervizoru.md"):
            self.assertFalse(os.path.exists(os.path.join(DEPO, ".claude", "agents", ad)))
            self.assertTrue(os.path.isfile(os.path.join(DEPO, ".claude", "_ESKI", "agents", ad)))

    def test_film_yap_govdesi_tasarim_metni(self):
        g, fm, h = bd.on_bilgi(bd.oku(os.path.join(FY, "SKILL.md")))
        self.assertIsNone(h); self.assertEqual(fm["name"], "film-yap"); self.assertEqual(fm["effort"], "high")
        self.assertIn("!`python .claude/bin/film.py ozet --kisa || true`", g)
        self.assertIn(bd.TEK_SORU, g); self.assertIn(bd.BULUT_CUMLESI, g)
        self.assertLessEqual(bd.token_tahmin(g.split(bd.CEKIRDEK_SONU)[0]), bd.CEKIRDEK_TOKEN_MAX)

    def test_film_gelistir_model_acamaz_film_durum_yazamaz(self):
        _, fm, _ = bd.on_bilgi(bd.oku(os.path.join(DEPO, ".claude", "skills", "film-gelistir", "SKILL.md")))
        self.assertIs(fm["disable-model-invocation"], True)
        _, fm, _ = bd.on_bilgi(bd.oku(os.path.join(DEPO, ".claude", "skills", "film-durum", "SKILL.md")))
        self.assertTrue({"Write", "Edit", "NotebookEdit", "Agent"} <= set(bd.arac_listesi(fm["disallowed-tools"])))

    def test_film_py_sarmalayici(self):
        r = subprocess.run([sys.executable, os.path.join(DEPO, ".claude", "bin", "film.py"), "beceri-denetim"], capture_output=True,
                           env=dict(os.environ, PYTHONIOENCODING="utf-8"), timeout=120)
        cikti = r.stdout.decode("utf-8", "replace")
        self.assertIn("BECERİ DENETİM", cikti)
        self.assertIn(r.returncode, (0, 1), cikti[-500:])     # 1 yalnız başka dilimin (ajan dosyaları) HATA'sıyla

    def test_sablon_doldur(self):
        E = bd.esikleri_yukle(DEPO)
        t = bd.sablon_doldur(bd.oku(os.path.join(FY, "sablonlar", "A07b_yonetmen_plan.md")), E)
        self.assertNotIn("{{", t); self.assertIn(bd.deger_metni(E["eylem_adim_max"]), t)
        with self.assertRaises(bd.SablonHatasi): bd.sablon_doldur("x {{esik:yok_boyle_anahtar}}", E)
        with self.assertRaises(bd.SablonHatasi): bd.sablon_doldur("x {{film}}", E)
        self.assertEqual(bd.deger_metni([1800, 2700]), "1800–2700"); self.assertEqual(bd.deger_metni(0.8), "0,8")


class Fikstur(unittest.TestCase):
    def setUp(self):
        self.k = tempfile.mkdtemp(prefix="beceri_fx_")
        os.makedirs(os.path.join(self.k, ".claude", "agents"))
        os.makedirs(os.path.join(self.k, "YZ_FILM", "ARACLAR", "veri"))
        shutil.copy(os.path.join(ARACLAR, "veri", "ADLAR.json"), os.path.join(self.k, "YZ_FILM", "ARACLAR", "veri", "ADLAR.json"))
        self.d = bd.Denetim(self.k); self.d._E = bd.esikleri_yukle(DEPO); self.d._H = False

    def tearDown(self): shutil.rmtree(self.k, ignore_errors=True)

    def maddeler(self, seviye="HATA"): return {x["madde"] for x in self.d.maddeler if x["seviye"] == seviye}

    def ajan(self, ad, fm, govde="KESİN KURALLAR\nÖnce GOREV.json'u oku; yalnız CIKTI/'ye yaz.\n"):
        p = os.path.join(self.k, ".claude", "agents", ad + ".md"); yaz(p, "---\n" + fm + "\n---\n" + govde)
        self.d.ajan_dosyasi(ad, p, self.d.kadro()[ad]); return p

    def test_iyi_kor_ajan_hatasiz(self):
        self.ajan("kesici", "name: kesici\ndescription: Kesici. Yalnız film.py görev defteri bir GOREV.json yoluyla çağırdığında kullanılır.\n"
                  "tools: Read, Write\nmodel: opus\neffort: high\npermissionMode: acceptEdits\nomitClaudeMd: true\nmaxTurns: 60")
        self.assertEqual(self.maddeler(), set()); self.assertEqual(self.maddeler("BAYRAK"), set())

    def test_kor_ajan_hatalari(self):
        self.ajan("kesici", "name: kesici\ndescription: x\ntools: Read, Write, Glob, Bash\nmodel: sonnet\neffort: medium\nmemory: user",
                  "SAHNELER.json'u oku.\n")
        h = self.maddeler()
        for m in ("yasak_arac", "rol_araci", "model", "effort", "izin_kipi", "yasak_alan", "kor_claude_md", "gorev_protokolu"):
            self.assertIn(m, h)
        self.assertIn("kor_sizinti", self.maddeler("BAYRAK"))

    def test_yazar_ders_editoru_edit_alamaz(self):
        self.ajan("ders-editoru", "name: ders-editoru\ndescription: Ders. Yalnız film.py görev defteri çağırır.\n"
                  "tools:\n  - Read\n  - Write\n  - Edit\nmodel: opus\neffort: high\npermissionMode: acceptEdits\nmaxTurns: 100")
        self.assertIn("rol_araci", self.maddeler())

    def test_konu_disi_soru_ve_olumsuz_satir(self):
        self.d.soru_tarama("x.md", "Kullanıcıya hangisini istersin diye sor.\n", "test")
        self.assertIn("konu_disi_soru", self.maddeler())
        self.d.maddeler = []
        self.d.soru_tarama("x.md", '"Hangisini istersin / onaylıyor musun" YOK.\n' + bd.TEK_SORU + "\n", "test")
        self.assertEqual(self.maddeler(), set())
        self.d.soru_tarama("x.md", "Sonra robocopy a b /MIR çalıştır.\nrobocopy /MIR yok.\n", "test")
        self.assertEqual([x["madde"] for x in self.d.maddeler], ["tehlikeli_komut"])

    def test_beceri_frontmatter_hatalari(self):
        p = os.path.join(self.k, ".claude", "skills", "film-durum", "SKILL.md")
        yaz(p, "---\nname: film-durum\ndescription: >-\n  " + "uzun " * 400 + "\nallowed-tools: Bash(rm *)\n---\n# x\nOnaylıyor musun?\n")
        self.d.beceri_dosyasi("film-durum", p)
        self.assertTrue({"aciklama_uzun", "izinli_arac", "film_durum_yazmaz", "konu_disi_soru"} <= self.maddeler(), self.maddeler())
        p = os.path.join(self.k, ".claude", "skills", "film-gelistir", "SKILL.md")
        yaz(p, "---\nname: film-gelistir\ndescription: Geliştirici kipi; film üretimi için kullanılmaz, yalnız kullanıcı isterse.\n---\n# x\n")
        self.d.beceri_dosyasi("film-gelistir", p)
        self.assertIn("model_acamaz", self.maddeler())

    def test_sablon_hatalari(self):
        d = os.path.join(self.k, "sb"); os.makedirs(d)
        p = os.path.join(d, "A06_habersiz-seyirci_kagit.md")
        yaz(p, "# A06\n## Bu görev\nKapı {{esik:seyirci_kapi_genel_min}} {{esik:boyle_yok}} {{film_adi}}\nSAHNELER.json'a bak.\n"
               "## CIKTI\n- `CIKTI/rapor_P0.md` son satır `OZET | GENEL: <n> | KRITIK: <n>`\n## Bitirmeden\n")
        self.d.sablon_dosyasi(p, "habersiz-seyirci", "kor")
        self.assertTrue({"sablon_esik", "sablon_yer_tutucu", "ozet_seyirci", "kor_sizinti"} <= self.maddeler(), self.maddeler())
        self.d.maddeler = []
        p2 = os.path.join(d, "A05_diyalog-editoru.md")
        yaz(p2, "# A05\n## CIKTI\n- `CIKTI/not.md`\n## Bitirmeden\n- `OZET | a: <b|c>`\n")
        self.d.sablon_dosyasi(p2, "diyalog-editoru", "denetci")
        self.assertIn("ozet_bicimi", self.maddeler())

    def test_on_bilgi(self):
        g, fm, h = bd.on_bilgi("---\nname: a\nx: >-\n  bir\n  iki\nl:\n  - Read\n  - Write\nb: true\nn: 40\nhooks:\n  Pre:\n    - m\n---\ngövde\n")
        self.assertIsNone(h); self.assertEqual(fm["x"], "bir iki"); self.assertEqual(fm["l"], ["Read", "Write"])
        self.assertIs(fm["b"], True); self.assertEqual(fm["n"], 40); self.assertIn("Pre:", fm["hooks"]["_ham"]); self.assertEqual(g, "gövde\n")
        self.assertIsNone(bd.on_bilgi("gövde")[1])


class Semalar(unittest.TestCase):
    def test_seyirci_ornegi(self):
        o = {"kip": "kurgu", "tur": 1, "seyirci": 2, "persona": "A", "bolum": "P1", "parca": 3, "donen_seyirci": False,
             "puanlar": {"anlasilirlik": 8, "akicilik": 7, "merak": 8, "duygu": 7, "ritim": 6, "ilk30": 9, "GENEL": 7},
             "parca_puanlari": [{"parca": 1, "GENEL": 8}],
             "kopukluklar": [{"konum": {"sahne": "S05", "plan": 41, "onceki_plan": 40, "zaman": "01:01"}, "tur": "KRITIK",
                              "neden": "Kadın kapıdaydı, sonraki karede masanın yanında", "oneri": "arada yürüdüğünü gösteren bir plan"}],
             "sikilma": [{"bas": "07:40", "bit": "08:30", "neden": "aynı tartışma"}], "ilgi": [{"konum": {"zaman_bas": "00:00"}, "puan": 9}],
             "acik_sorular": ["Kardaki ışık neydi?"], "ozet_parti": "Üç cümle.", "karakterler": [{"ad_ya_da_tarif": "kürk yakalı kadın"}],
             "devam_olasiligi": 0.8, "devam": True, "yz_kusurlari": []}
        s = sema("seyirci_rapor_v2")
        self.assertEqual(bd.sema_dogrula(o, s), [])
        bozuk = dict(o, puanlar={"GENEL": 11, "uydurma": 3}); bozuk.pop("devam")
        self.assertGreaterEqual(len(bd.sema_dogrula(bozuk, s)), 3)

    def test_kapi_gorev_kuyruk_juri_eslesme(self):
        kapi = {"_surum": 1, "_uretim": {"asama": "A11", "gorev": "A11-G1-007", "girdi_imza": "c3d4e5", "arac_surum": "kare_denetim 1.0",
                "esik_surum": "x", "sonuc": "KISMI", "zaman": "t", "ortam": "yerel"}, "kapi": "G1", "kapsam": "P1_B2", "tur": 1, "sonuc": "KISMI",
                "ozet": {"plan": 30}, "hatalar": [{"madde": "el_nesne", "plan": 214, "olcu": {}, "esik": "iki kaynak", "seviye": "HATA",
                                                    "oneri": "CORRECTION:el_nesne", "kanit": ["a.jpg"]}]}
        self.assertEqual(bd.sema_dogrula(kapi, sema("kapi_rapor_v1")), [])
        gorev = {"_surum": 2, "id": "A12-AS-014", "film": "F", "asama": "A12", "tur": "ajan", "ajan": "habersiz-seyirci", "kip": "animatik",
                 "persona": "A", "ornek": "yeni", "paralel_grup": "g", "durum": "calisiyor", "deneme": 1, "deneme_max": 3,
                 "asamali": {"bolumler": ["P0"], "acik": ["P0"], "mekanizma": "subagentstop"}, "girdi": ["GIRDI/P0/"], "girdi_imza": "7d",
                 "cikti": {"zorunlu": ["CIKTI/rapor_P0.md"], "son": ["CIKTI/rapor.json"], "sema": "seyirci_rapor_v2"},
                 "tasima": {"CIKTI/rapor.json": "_RAPOR/x.json"}, "yarim_davranisi": "sifirdan", "agent_id": None, "istem": "Görevin: …",
                 "kullanim": {}, "zaman": {"olusturma": "t", "basla": "t", "bitir": None}}
        self.assertEqual(bd.sema_dogrula(gorev, sema("gorev_v2")), [])
        self.assertTrue(bd.sema_dogrula(dict(gorev, id="yanlis", durum="uyuyor"), sema("gorev_v2")))
        ku = {"id": "YU-T2-1-007", "plan": 41, "tur": "video", "kaynak_kapi": "KI", "kok_neden": "nesne_zipladi", "seviye": "KRITIK",
              "cozum": "yeniden_cek", "durum": "bekliyor", "deneme": 2, "deneme_max": 3}
        self.assertEqual(bd.sema_dogrula(ku, sema("kuyruk_madde_v1")), [])
        juri = {"rol": "tur_uzmani", "oneriler": {"1": {"puan": {"kanca": 8}, "gerekce": {"kanca": "ilk sahne güçlü"}, "veto": None}}}
        self.assertEqual(bd.sema_dogrula(juri, sema("juri_v1")), [])
        self.assertTrue(bd.sema_dogrula({"rol": "x", "oneriler": {"1": {"puan": {"kanca": 12}, "gerekce": {}}}}, sema("juri_v1")))
        es = {"olgular": [{"id": "O1", "karar": "kismen", "kanit": "kadın yavruyu saklıyor"}], "sorular": []}
        self.assertEqual(bd.sema_dogrula(es, sema("ozet_eslesme_v1")), [])
        self.assertTrue(bd.sema_dogrula({"olgular": [{"id": "O1", "karar": "belki"}]}, sema("ozet_eslesme_v1")))


class Senaryolar(unittest.TestCase):
    """§4.8 senaryoları 1–7 (sahte; ağsız, kredisiz). Kabul: HATA yok. BAYRAK başka dilimin bilinen açığını gösterir."""
    @classmethod
    def setUpClass(cls): cls.r = {x["no"]: x for x in bd.senaryolar(None, DEPO)}

    def kontrol(self, no):
        x = self.r[no]
        self.assertNotEqual(x["sonuc"], "HATA", json.dumps(x, ensure_ascii=False, indent=1))
        self.assertTrue(x["adimlar"])

    def test_1_film_yap_tek_soru(self): self.kontrol(1)
    def test_2_konu_soru_yok_a01_but0(self): self.kontrol(2)
    def test_3_devam_yalniz_kesikler(self): self.kontrol(3)
    def test_4_kancasiz_basla_reddeder(self): self.kontrol(4)
    def test_5_yerlesik_ajan_reddedilir(self): self.kontrol(5)
    def test_6_soru_dosya_degismez(self): self.kontrol(6)
    def test_7_gelistirmede_explore_serbest(self): self.kontrol(7)


if __name__ == "__main__":
    unittest.main()
