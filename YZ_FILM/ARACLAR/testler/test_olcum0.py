"""Ö0-1 betikleri (TASARIM §1.2, §9 adım 9): Ö0-b merdiveni (ilk uyarıda kapanır, kapasite = son uyarısız gün), fikstür denetimi, Ö0-d
CapCut denemesi, Ö0-e Gemini denemesi, ortak OLCUM0 yazıcısı ve film.py olcum0. Gerçek Flow, Gemini ya da CapCut YOK: sahte Memmet
koşucusu (gerçek Ö0-b blok yetkisi + gerçek BUTK + gerçek flow_yuk defteriyle), sahte Gemini taşıyıcısı, sahte taslak yazıcısı.
Çalıştırma: python -m unittest discover -s ARACLAR/testler     (YZ_FILM klasöründen)
"""
import os, sys, io, json, time, base64, shutil, zipfile, tempfile, unittest, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401
OLCUM0 = os.path.join(ARACLAR, "olcum0")
for _p in (OLCUM0, os.path.join(OLCUM0, "fikstur")):
    if _p not in sys.path: sys.path.insert(0, _p)
import ortak, flow_yuk, kredi, olcek
import ortak_o0 as o0, fikstur_denetim as fd, flow_deneme as fdn, gemini_deneme as gd, capcut_deneme as cd
from PIL import Image

GUN = 86400
T0 = time.mktime((2026, 11, 2, 10, 0, 0, 0, 0, -1))       # yerel 10:00 (gün sınırından uzak)


def jpg(yol, renk=(120, 80, 40), boyut=(1376, 768)):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    Image.new("RGB", boyut, renk).save(yol, "JPEG", quality=90); return yol


def fikstur_uret(b3, yol):
    """Önerilen dağılımla geçerli 45 istemlik fikstür: gün 1 10 ab · gün 2 14 ab + 1 zincir(yok) · gün 3 20 zincir (12 var, 8 yok)."""
    hucre = [("aralik", "holds still"), ("aralik", "holds the pose, breathing"), ("sira", "holds still"), ("sira", "holds the pose, breathing")]
    ist = []; n = 0

    def kare(i):
        p = jpg(os.path.join(b3, "SIRALI_GORSEL", "%03d.jpg" % i), (i * 5 % 255, 90, 160))
        return "SIRALI_GORSEL/%03d.jpg" % i, fd._sha1(p)[:12]

    def ab(gun):
        nonlocal n
        n += 1; b, w = hucre[(n - 1) % 4]; k, sh = kare(n)
        if b == "aralik":
            m = (f"Static medium shot, the camera does not move. 0.5-3s: the hunter woman lifts her right hand and rests it on table {n}. "
                 f"3-6s: she turns her head toward the window. 6-8s: she {w}. No music.")
        else:
            m = (f"Static medium shot, the camera does not move. First the hunter woman lifts her right hand and rests it on table {n}, "
                 f"then she turns her head toward the window. Then she {w}. No music.")
        ist.append({"id": "O0B-%03d" % n, "gun": gun, "deney": "ab", "kollar": {"istem_bicimi": b, "bekleme": w, "son_kare_ref": "yok",
                    "zincir_kare": None}, "b3_plan": n, "kare": k, "kare_sha1": sh, "b3_denetim": "iki_tur_gecti", "istem": m,
                    "adimlar": [{"bas": 0.5, "bit": 3.0, "metin": "lifts her right hand"}, {"bas": 3.0, "bit": 6.0, "metin": "turns her head"}],
                    "klip_sn": 8})

    def zn(gun, kaynak, ref, boy=None):
        nonlocal n
        n += 1
        m = f"Static medium shot, the camera does not move. 0.5-3s: the hunter woman stands up from table {n}. 3-6s: she walks two slow steps. 6-8s: she holds still. No music."
        it = {"id": "O0B-%03d" % n, "gun": gun, "deney": "zincir", "kollar": {"istem_bicimi": "aralik", "bekleme": "holds still",
              "son_kare_ref": ref, "zincir_kare": boy}, "b3_plan": n, "istem": m, "klip_sn": 8,
              "adimlar": [{"bas": 0.5, "bit": 3.0, "metin": "stands up"}, {"bas": 3.0, "bit": 6.0, "metin": "walks two slow steps"}],
              "zincir": {"kaynak": kaynak, "kare_sn": 6.5 if ref == "var" else None}}
        if ref == "yok":
            k, sh = kare(n); it.update(kare=k, kare_sha1=sh, b3_denetim="iki_tur_gecti")
        ist.append(it)

    for _ in range(10): ab(1)
    for _ in range(14): ab(2)
    zn(2, "O0B-001", "yok")
    for j in range(20):
        kay = "O0B-%03d" % (j + 1)
        if j < 6: zn(3, kay, "var", "dogal_1280x720")
        elif j < 12: zn(3, kay, "var", "1376x774_kirp3")
        else: zn(3, kay, "yok")
    doc = {"_sema": "O0b_istemler", "fikstur_surum": "v1", "sablon": False, "yazar": "test", "tarih": "2026-10-24", "istemler": ist}
    ortak.atomik_yaz(yol, doc); return doc


class SahteMemmet:
    """Memmet v2 blok koşusunun sahtesi. Önce GERÇEK Ö0-b blok yetkisini (O0bMemmet.blok_dogrula) koşar; sonra her plan için gerçek BUTK +
    kredi defteri + flow_yuk gönderim kaydı; senaryo: red, uyarı (n. gönderimden sonra), doğrulama, durma."""
    def __init__(self, hesap, bakiye=2000):
        self.hesap = hesap; self.bakiye = bakiye; self.simdi = T0; self.red = set(); self.red_yakar = True
        self.uyari_sonra = None; self.dogrulama_sonra = None; self.dur_sonra = None; self.zaman_asimi = set(); self.cagri = []

    def _cikis(self, film, kod, mesaj):
        ortak.atomik_yaz(os.path.join(film, "_memmet_cikis.json"), {"kod": kod, "mesaj": mesaj, "zaman": "x"})

    def __call__(self, argv):
        self.cagri.append(list(argv))
        if "--bakiye" in argv:
            ortak.atomik_yaz(os.path.join(self.hesap, "FLOW_BAKIYE.json"), {"bakiye": self.bakiye, "zaman":
                             time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.simdi))})
            return 0
        assert argv[1] == "memmet-blok" and argv[argv.index("--mod") + 1] == "elle"
        film = argv[2]; blok = argv[argv.index("--blok") + 1]; imza = argv[argv.index("--onizleme") + 1]
        import memmet
        with mock.patch.object(memmet, "HESAP", self.hesap), mock.patch.object(fdn, "saat", lambda: self.simdi):
            m = fdn.olcum_memmet_sinifi(memmet)(film, {"blok": blok, "onizleme": imza, "mod": "elle"})
            try: b = m.blok_dogrula()
            except memmet.Durdur as e:
                m.kayit.close(); self._cikis(film, e.kod, str(e)); return memmet.CIKIS.get(e.kod, 2)
            m.kayit.close()
        dp = os.path.join(film, "MEMMET_DURUM.json"); D = ortak.json_oku(dp, {}) or {"isler": {}}
        log = open(os.path.join(film, "MEMMET_KAYIT.txt"), "a", encoding="utf-8")
        try:
            for i, no in enumerate(b["planlar"], 1):
                is_k = f"V-{no}-d1-x"
                if self.dur_sonra is not None and i > self.dur_sonra:          # gönderilmeden durdu (oturum düştü)
                    self._cikis(film, "giris", "oturum düştü"); return 2
                r, kod = kredi.butk(film, is_k, 12, birim="flow", dilim="ana", saglayici="flow", plan=no)
                if kod: self._cikis(film, "butce", "BUTK red"); return 5
                kredi.defter_ekle(film, "gonderim", 12, birim="flow", dilim="ana", madde=is_k, plan=no, saglayici="flow", is_kimligi=is_k,
                                  tur="video", blok=blok)
                flow_yuk.gonderim_kaydet("video", "elle", film=fdn.FILM_AD, plan=no, kok=self.hesap, simdi=self.simdi + i)
                D["isler"][is_k] = {"plan": no, "tur": "video", "durum": "gonderildi", "blok": blok}
                if self.uyari_sonra is not None and i >= self.uyari_sonra:
                    flow_yuk.uyari_kaydet(fdn.FILM_AD, "olağan dışı etkinlik", kok=self.hesap, simdi=self.simdi + i)
                    self._cikis(film, "olagandisi", "uyarı"); return 7
                if self.dogrulama_sonra is not None and i >= self.dogrulama_sonra:
                    self._cikis(film, "dogrulama", "reCAPTCHA"); return 2
                self.bakiye -= 12
                pid = next(k for k, v in fdn.durum_oku()["istemler"].items() if v["no"] == no)
                if pid in self.zaman_asimi:
                    D["isler"][is_k]["durum"] = "zaman_asimi"; continue
                if pid in self.red:
                    D["isler"][is_k]["durum"] = "filtre_red"
                    if not self.red_yakar: self.bakiye += 12
                    continue
                os.makedirs(os.path.join(film, "SIRALI_VIDEO"), exist_ok=True)
                with open(os.path.join(film, "SIRALI_VIDEO", "%03d.mp4" % no), "wb") as f: f.write(b"sahte mp4 %d" % no)
                D["isler"][is_k]["durum"] = "indirildi"
                log.write("02.11 10:00:00 %03d video: KAYDEDİLDİ (%d sn)\n" % (no, 90 + no))
        finally:
            ortak.atomik_yaz(dp, D); log.close()
        if any(v["durum"] == "zaman_asimi" for v in D["isler"].values()): self._cikis(film, "topla", "toplanacak"); return 8
        self._cikis(film, "tamam", "blok bitti"); return 0


class Taban(unittest.TestCase):
    def setUp(self):
        self.kok = tempfile.mkdtemp(prefix="o0_"); self.veri = os.path.join(self.kok, "VERI"); self.hesap = os.path.join(self.kok, "HESAP")
        for d in ("AYARLAR", "HESAP", "FILMLER"): os.makedirs(os.path.join(self.veri, d), exist_ok=True)
        os.makedirs(self.hesap)
        self.p = [mock.patch.dict(os.environ, {"YZ_FILM_VERI": self.veri, "YZ_FILM_ORTAM": "yerel"}),
                  mock.patch.object(fdn, "hesap", lambda: self.hesap)]
        for x in self.p: x.start()

    def tearDown(self):
        for x in reversed(self.p): x.stop()
        shutil.rmtree(self.kok, ignore_errors=True)

    def on_kosul_tamam(self):
        ortak.atomik_yaz(os.path.join(self.veri, "_ESKI", "EMNIYET_RAPORU.json"), {"kalan_giris_noktasi": []})
        o0.yaz("a", {"durum": "bitti"})


class TestOrtakO0(Taban):
    def test_yaz_ozet_deneme_durum(self):
        self.assertEqual(o0.durum("b"), "yok")
        o0.yaz("b", {"durum": "suruyor", "uretim_sn_720p": 100, "gunler": []})
        oz = o0.ozet_oku()
        self.assertEqual(oz["O0b"], {"durum": "suruyor", "uretim_sn_720p": 100})
        self.assertNotIn("olculen_gunluk_kapasite", oz["O0b"])                    # süren Ö0-b: anahtar yok
        _, _, o0b_var, _ = olcek.kapasite({"o0b_gun_tavanlari": [10, 15, 20]}, oz)
        self.assertFalse(o0b_var)                                                 # BUT0 "Ö0-b yok → 1800"
        o0.deneme("b", "x", 1, "k", "g")
        self.assertEqual(o0.ozet_oku()["denemeler"][-1]["olcum"], "Ö0-b")
        self.assertEqual(o0.durum("b"), "suruyor")
        ortak.atomik_yaz(o0.yol("c"), {"baska_arac": True})                       # durum alanı yoksa bitti sayılır
        self.assertEqual(o0.durum("c"), "bitti")


class TestFikstur(Taban):
    def test_sablon_gecerli_ve_reddedilir(self):
        y = os.path.join(OLCUM0, "fikstur", "O0b_istemler_SABLON.json")
        doc = fd.oku(y)
        self.assertTrue(doc["sablon"]); self.assertEqual(len(doc["istemler"]), 3)
        self.assertFalse(fd.hata_var(fd.denetle(doc)))
        with self.assertRaises(fdn.Dur) as c: fdn.fikstur_yukle(y)
        self.assertEqual(c.exception.kod, fdn.ORTAM)

    def test_gercek_fikstur_ve_hatalar(self):
        b3 = os.path.join(self.kok, "B3"); y = os.path.join(self.kok, "f.json"); doc = fikstur_uret(b3, y)
        B = fd.denetle(doc, b3_kok=b3)
        self.assertFalse(fd.hata_var(B), [b for b in B if b["seviye"] == "HATA"])
        self.assertTrue(any(b["madde"] == "kol_sayisi" and "zincir_kare" in b["neden"] for b in B))   # 6/6 < 12: bilerek
        def bozuk(f):
            d = json.loads(json.dumps(doc)); f(d); return [b["madde"] for b in fd.denetle(d) if b["seviye"] == "HATA"]
        self.assertIn("filtre", bozuk(lambda d: d["istemler"][0].update(istem=d["istemler"][0]["istem"].replace("hunter woman", "little girl"))))
        self.assertIn("bicim", bozuk(lambda d: d["istemler"][0].update(istem=fd.ARALIK.sub("then", d["istemler"][0]["istem"]))))
        self.assertIn("bekleme", bozuk(lambda d: d["istemler"][0].update(istem=d["istemler"][0]["istem"].replace("holds still", "stops"))))
        self.assertIn("sayi", bozuk(lambda d: d["istemler"].pop()))
        self.assertIn("zincir", bozuk(lambda d: d["istemler"][24].update(gun=1)))   # kaynak O0B-001 ile aynı gün
        self.assertIn("adim", bozuk(lambda d: d["istemler"][0]["adimlar"][1].update(bit=7.5)))
        d2 = json.loads(json.dumps(doc)); d2["istemler"][0]["kare_sha1"] = "deadbeefdeadbeef"
        self.assertIn("kare", [b["madde"] for b in fd.denetle(d2, b3_kok=b3) if b["seviye"] == "HATA"])


class TestFlowDeneme(Taban):
    def setUp(self):
        super().setUp()
        self.b3 = os.path.join(self.kok, "B3"); self.fy = os.path.join(self.kok, "O0b_istemler_v1.json")
        self.doc = fikstur_uret(self.b3, self.fy)
        self.k = SahteMemmet(self.hesap)
        self.ornek = jpg(os.path.join(self.kok, "kare.jpg"), (10, 200, 10), (1280, 720))

    def kare_al(self, klip, t, hedef):
        os.makedirs(os.path.dirname(hedef), exist_ok=True); shutil.copyfile(self.ornek, hedef); return hedef

    def gun(self, t, **k):
        self.k.simdi = t
        with mock.patch.object(fdn, "saat", lambda: t), contextlib.redirect_stdout(io.StringIO()):
            try:
                return fdn.gun(kosucu=self.k, simdi=t, kare_al=self.kare_al, g1z_fn=lambda *a: [{"madde": "keskinlik", "seviye": "GEC"}],
                               keskinlik=lambda y: 80.0 if ("zincir" in y or "kirp" in y) else 100.0, **k)
            except fdn.Dur as e: return e.kod, {"dur": str(e)}

    def hazirla(self):
        self.on_kosul_tamam()
        with mock.patch.object(fdn, "saat", lambda: T0): return fdn.hazirla(self.b3, self.fy, simdi=T0)

    def test_on_kosul_yoksa_baslamaz(self):
        with self.assertRaises(fdn.Dur) as c: fdn.hazirla(self.b3, self.fy)
        self.assertEqual(c.exception.kod, fdn.KULLANICI)
        self.assertIn("memmet3", str(c.exception))

    def test_uyarisiz_merdiven_kapasite_20(self):
        self.hazirla()
        self.assertEqual(o0.durum("b"), "hazir")
        kod, r = self.gun(T0)
        self.assertEqual(kod, 0, r)
        d = fdn.durum_oku(); g = d["gunler"][0]
        self.assertEqual((g["basamak"], g["gonderilen"], g["uyarisiz"], g["tam"]), (1, 10, True, True))
        self.assertNotIn("olculen_gunluk_kapasite", o0.ozet_oku()["O0b"])                 # sürerken anahtar yok
        kod, r = self.gun(T0 + 3600)                                                       # aynı gün: yarın
        self.assertEqual(kod, fdn.BEKLE)
        n = len(self.k.cagri)
        kod, r = self.gun(T0 + GUN); self.assertEqual(kod, 0, r)
        self.assertEqual(fdn.durum_oku()["gunler"][1]["gonderilen"], 15)
        kod, r = self.gun(T0 + 2 * GUN); self.assertEqual(kod, 0, r)
        d = fdn.durum_oku()
        self.assertEqual(d["durum"], "kapandi"); self.assertEqual(d["gunler"][2]["gonderilen"], 20)
        self.assertEqual(d["olculen_gunluk_kapasite"], 20); self.assertFalse(d["olculemedi"])
        self.assertEqual(d["klip_sayisi"], 45); self.assertEqual(kredi.defter_ozet(fdn.film_yolu())["birim"]["flow"]["harcanan"], 540)
        self.assertEqual(len(os.listdir(fdn.klip_kok())), 90)                              # 45 mp4 + 45 yan dosya (V3 için saklanır)
        self.assertEqual(d["uretim_sn_720p"], 113)
        ok = d["on_kararlar"]
        self.assertEqual(ok["istem_bicimi"]["karar"], "kayitli_v3_bekliyor"); self.assertEqual(ok["bekleme"]["kollar"]["holds still"], 12)
        self.assertEqual(ok["zincir_kare"]["karar"], "olculemedi_varsayilan"); self.assertEqual(ok["zincir_kare"]["varsayilan"], "dogal_1280x720")
        self.assertEqual(d["zincir_karesi"]["dogal_1280x720"], 0.8)
        oz = o0.ozet_oku()
        kap, olculdu, var, _ = olcek.kapasite({"o0b_gun_tavanlari": [10, 15, 20]}, oz)
        self.assertEqual((kap, olculdu, var), (20, True, True))
        r, _ = kredi.but0(olcum=oz, ayar={})
        self.assertTrue(r["kapasite"]["olculdu"])
        self.assertEqual(r["olcum_kredi"], 0)
        # memmet-blok komutu: yalnız elle, kendi sarmalayıcısı
        bloklar = [c for c in self.k.cagri if "memmet-blok" in c]
        self.assertTrue(all(c[0].endswith("flow_deneme.py") and c[c.index("--mod") + 1] == "elle" for c in bloklar))
        n = len(self.k.cagri); kod, r = self.gun(T0 + 3 * GUN)
        self.assertEqual(len(self.k.cagri), n); self.assertIn("kapandı", r["kullaniciya"])

    def test_kullanici_beyani_merdiveni_kapatir(self):
        self.hazirla()
        kod, r = self.gun(T0); self.assertEqual(kod, 0, r)                                # gün 1: 10 video, uyarısız
        with contextlib.redirect_stdout(io.StringIO()): kod, r = fdn.kapat(fdn.durum_oku(), "kullanıcı kararı", beyan=100, simdi=T0 + 3600)
        self.assertEqual(kod, 0)
        d = fdn.durum_oku()
        self.assertEqual((d["durum"], d["olculen_gunluk_kapasite"], d["olculemedi"]), ("kapandi", 100, False))
        self.assertEqual((d["kapasite_kaynagi"], d["olculen_alt_sinir"]), ("kullanici_beyani", 10))
        oz = o0.ozet_oku(); self.assertEqual(oz["O0b"]["kapasite_kaynagi"], "kullanici_beyani")
        kap, olculdu, var, _ = olcek.kapasite({"o0b_gun_tavanlari": [10, 15, 20]}, oz)
        self.assertEqual((kap, olculdu, var), (100, True, True))
        kod, r = self.gun(T0 + GUN); self.assertEqual(kod, fdn.BITTI)                     # kapandı: merdiven yeniden açılmaz

    def test_uyari_kayitliyken_beyan_alinmaz(self):
        self.hazirla()
        d = fdn.durum_oku(); d["gunler"] = [{"basamak": 1, "durum": "bitti", "uyarisiz": False, "gonderilen": 4}]
        with self.assertRaises(fdn.Dur) as c: fdn.kapat(d, "kullanıcı kararı", beyan=100, simdi=T0)
        self.assertEqual(c.exception.kod, fdn.KISIT)

    def test_ikinci_gunde_uyari_kapanir_kapasite_10(self):
        self.hazirla()
        self.assertEqual(self.gun(T0)[0], 0)
        self.k.uyari_sonra = 5
        kod, r = self.gun(T0 + GUN)
        self.assertEqual(kod, fdn.KISIT, r)
        d = fdn.durum_oku()
        self.assertEqual(d["durum"], "kapandi"); self.assertEqual(d["olculen_gunluk_kapasite"], 10)
        self.assertFalse(d["gunler"][1]["uyarisiz"])
        self.assertEqual(d["olcum_yasak_bitis"], fdn._tarih(T0 + GUN + 5 + 7 * GUN))
        self.assertIn("GÖNDER'e basma", r["kullaniciya"])
        n = len(self.k.cagri)
        for t in (T0 + 2 * GUN, T0 + 9 * GUN): self.gun(t)                                 # hiçbir zaman yeniden denenmez
        self.assertEqual(len(self.k.cagri), n)
        r, _ = kredi.but0(olcum=o0.ozet_oku(), ayar={})
        self.assertEqual(r["sure_sn"], 1800); self.assertIn("10 < 20", r["neden"])

    def test_ilk_gunde_uyari_olculemedi(self):
        self.hazirla(); self.k.uyari_sonra = 1
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.KISIT)
        d = fdn.durum_oku(); self.assertIsNone(d["olculen_gunluk_kapasite"]); self.assertTrue(d["olculemedi"])
        kap, olculdu, var, _ = olcek.kapasite({"o0b_gun_tavanlari": [10, 15, 20]}, o0.ozet_oku())
        self.assertEqual((olculdu, var), (False, True))

    def test_dogrulama_da_kapatir(self):
        self.hazirla(); self.k.dogrulama_sonra = 3
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.KISIT); self.assertEqual(fdn.durum_oku()["durum"], "kapandi")

    def test_uyari_olcum_disinda_gelse_de_kapanir(self):
        self.hazirla(); self.assertEqual(self.gun(T0)[0], 0)
        flow_yuk.uyari_kaydet("BASKA_FILM", "olağan dışı", kok=self.hesap, simdi=T0 + 7200)
        n = len(self.k.cagri)
        kod, r = self.gun(T0 + GUN)
        self.assertEqual(kod, fdn.KISIT); self.assertEqual(len(self.k.cagri), n)
        self.assertEqual(fdn.durum_oku()["olculen_gunluk_kapasite"], 10)

    def test_yakin_uyari_baslatmaz_ve_yabanci_video_bekletir(self):
        self.hazirla()
        flow_yuk.uyari_kaydet("ESKI", "uyarı", kok=self.hesap, simdi=T0 - 2 * GUN)
        os.replace(os.path.join(self.hesap, "FLOW_KILIDI.json"), os.path.join(self.kok, "kilit_tasindi.json"))   # kilit kalktı, uyarı geçmişi durur
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.BEKLE); self.assertEqual(self.k.cagri, [])
        kod, r = self.gun(T0 + 6 * GUN)                                                    # 8. gün: başlar; ama bugün başka video gitmiş
        self.assertEqual(kod, 0, r)
        flow_yuk.gonderim_kaydet("video", "elle", film="F2026_x", plan=1, kok=self.hesap, simdi=T0 + 7 * GUN - 100)
        kod, r = self.gun(T0 + 7 * GUN)
        self.assertEqual(kod, fdn.BEKLE); self.assertIn("başka video", r["dur"])

    def test_red_yeniden_gonderilmez_kredi_etkisi(self):
        self.hazirla(); self.k.red = {"O0B-003"}
        kod, r = self.gun(T0)
        self.assertEqual(kod, 0, r)
        d = fdn.durum_oku(); g = d["gunler"][0]
        self.assertEqual(g["red"], ["O0B-003"]); self.assertEqual(d["istemler"]["O0B-003"]["durum"], "filtre_red")
        self.assertEqual((g["bakiye_once"], g["bakiye_sonra"]), (2000, 1880))
        self.assertEqual(fdn.politika_reddi(d)["kredi_etkisi"], "yakti")
        bloklar = [c for c in self.k.cagri if "memmet-blok" in c]; self.assertEqual(len(bloklar), 1)
        d["gunler"][0]["bakiye_sonra"] = 1892
        self.assertEqual(fdn.politika_reddi(d)["kredi_etkisi"], "yakmadi")

    def test_yarim_gun_ayni_gun_surer_sonra_basamak_tekrar(self):
        self.hazirla(); self.k.dur_sonra = 4
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.KULLANICI, r)
        d = fdn.durum_oku(); self.assertEqual(d["gunler"][0]["gonderilen"], 4); self.assertEqual(d["durum"], "suruyor")
        self.k.dur_sonra = None
        kod, r = self.gun(T0 + 1800)                                                       # aynı gün: kalan 6 istem
        self.assertEqual(kod, 0, r)
        d = fdn.durum_oku(); self.assertEqual(len(d["gunler"]), 1); self.assertEqual(d["gunler"][0]["gonderilen"], 10)
        self.assertEqual(fdn.basamak(d), 2)

    def test_yarim_gun_ertesi_gun_ayni_basamak(self):
        self.hazirla(); self.k.dur_sonra = 4
        self.gun(T0); self.k.dur_sonra = None
        kod, r = self.gun(T0 + GUN)
        self.assertEqual(kod, 0, r)
        d = fdn.durum_oku()
        self.assertEqual([(g["basamak"], g["gonderilen"], g["tam"]) for g in d["gunler"]], [(1, 4, False), (1, 6, True)])
        self.assertEqual(fdn.kapasite(d), (6, False))

    def test_kilit_varken_baslamaz(self):
        self.hazirla()
        flow_yuk.uyari_kaydet("ESKI", "uyarı", kok=self.hesap, simdi=T0 - 30 * GUN)
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.BEKLE); self.assertEqual(fdn.durum_oku()["durum"], "hazir"); self.assertEqual(self.k.cagri, [])

    def test_zaman_asimi_toplanir_yeniden_gonderilmez(self):
        self.hazirla(); self.k.zaman_asimi = {"O0B-004"}
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.BEKLE); self.assertIn("memmet_topla", r["dur"])
        film = fdn.film_yolu(); dp = os.path.join(film, "MEMMET_DURUM.json"); D = ortak.json_oku(dp)
        for v in D["isler"].values():                                                       # memmet_topla'nın yaptığı
            if v["durum"] == "zaman_asimi":
                v["durum"] = "indirildi"
                with open(os.path.join(film, "SIRALI_VIDEO", "%03d.mp4" % v["plan"]), "wb") as f: f.write(b"toplandi")
        ortak.atomik_yaz(dp, D)
        n = len(self.k.cagri)
        kod, r = self.gun(T0 + 3600)
        self.assertEqual(kod, 0, r); self.assertEqual(len(self.k.cagri), n)                # yeni gönderim yok
        d = fdn.durum_oku(); g = d["gunler"][0]
        self.assertEqual((g["durum"], g["tam"], g["uyarisiz"], g["gonderilen"]), ("bitti", True, True, 10))
        self.assertEqual(d["istemler"]["O0B-004"]["durum"], "indirildi")

    def test_kuru_ve_butce(self):
        self.hazirla()
        kod, r = self.gun(T0, kuru=True)
        self.assertEqual((kod, len(r["planlar"]), r["kredi"]), (0, 10, 120)); self.assertEqual(self.k.cagri, [])
        self.k.bakiye = 100
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.BUTCE)
        self.assertEqual(len([c for c in self.k.cagri if "memmet-blok" in c]), 0)

    def test_fikstur_degisirse_durur(self):
        self.hazirla()
        d = json.load(open(self.fy, encoding="utf-8")); d["yazar"] = "değişti"; ortak.atomik_yaz(self.fy, d)
        kod, r = self.gun(T0)
        self.assertEqual(kod, fdn.HATA); self.assertIn("değişti", r["dur"])


class TestOlcumMemmet(Taban):
    """Ö0-b sarmalayıcısı memmet'ten YALNIZ blok_dogrula'yı değiştirir (sayfaya dokunan hiçbir yöntem yok) ve yetkisiz/yanlış kipte durur."""
    def test_yalniz_blok_dogrula(self):
        import memmet
        S = fdn.olcum_memmet_sinifi(memmet)
        self.assertEqual({k for k in S.__dict__ if not k.startswith("__")}, {"blok_dogrula"})
        self.assertTrue(issubclass(S, memmet.Memmet))

    def test_yetkisiz_ve_gece_kipi_reddedilir(self):
        import memmet
        self.on_kosul_tamam()
        b3 = os.path.join(self.kok, "B3"); fy = os.path.join(self.kok, "f.json"); fikstur_uret(b3, fy)
        fdn.hazirla(b3, fy)
        film = fdn.film_yolu(); S = fdn.olcum_memmet_sinifi(memmet)
        with mock.patch.object(memmet, "HESAP", self.hesap):
            m = S(film, {"blok": "O0B-G1-1", "onizleme": "x", "mod": "elle"})
            with self.assertRaises(memmet.Durdur) as c: m.blok_dogrula()
            self.assertIn(c.exception.kod, ("kilitli", "imza"))
            m.kayit.close()
            m = S(film, {"blok": "O0B-G1-1", "onizleme": "x", "mod": "gece"})
            with self.assertRaises(memmet.Durdur) as c: m.blok_dogrula()
            self.assertEqual(c.exception.kod, "ortam"); m.kayit.close()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(fdn.memmet_blok([film, "--blok", "B", "--onizleme", "x", "--mod", "gece"]), fdn.ORTAM)


class SahteGemini:
    def __init__(self, video=200, ses=400, gorsel=200, gorsel_429_sonra=None):
        self.video, self.ses, self.gorsel, self.g429 = video, ses, gorsel, gorsel_429_sonra; self.istekler = []; self.gorsel_n = 0

    def __call__(self, yontem, url, govde, basliklar):
        assert "key=" not in url and basliklar.get("x-goog-api-key")
        j = json.loads(govde.decode()); parts = j["contents"][0]["parts"]; self.istekler.append(url)
        mime = [p["inline_data"]["mime_type"] for p in parts if "inline_data" in p]
        if "image" in url:
            self.gorsel_n += 1
            if self.g429 is not None and self.gorsel_n > self.g429:
                return 429, b'{"error": {"status": "RESOURCE_EXHAUSTED", "message": "generate_content_free_tier_requests limit"}}', {}
            veri = base64.b64encode(b"\xff\xd8sahte").decode()
            return self.gorsel, json.dumps({"candidates": [{"content": {"parts": [{"inline_data": {"mime_type": "image/jpeg", "data": veri}}]}}]}).encode(), {}
        if any(m.startswith("video") for m in mime): return self.video, b'{"candidates": [{"content": {"parts": [{"text": "{}"}]}}]}', {}
        if any(m.startswith("audio") for m in mime): return self.ses, b'{"error": {"message": "unsupported"}}', {}
        return 200, b'{"candidates": [{"content": {"parts": [{"text": "{\\"ok\\": true}"}]}}]}', {}


class TestGeminiDeneme(Taban):
    def setUp(self):
        super().setUp()
        self.pk = os.path.join(self.kok, "GEMINI_PAKET"); os.makedirs(self.pk)
        import gemini_paket
        self.p += [mock.patch.object(gemini_paket, "paket_kok", lambda: self.pk), mock.patch.dict(os.environ, {"GEMINI_API_KEY": "test-yok"})]
        for x in self.p[-2:]: x.start()
        b3 = os.path.join(self.kok, "B3"); ref = jpg(os.path.join(b3, "ref", "mara.jpg"))
        S = {"film": "B3", "karakterler": {"mara": {"ref": "ref/mara.jpg"}},
             "sahneler": [{"no": i, "gorsel_istem": f"Photorealistic still {i}", "referans": ["mara"]} for i in range(1, 36)]}
        self.sy = os.path.join(b3, "SAHNELER.json"); ortak.atomik_yaz(self.sy, S)
        self.video = os.path.join(self.kok, "k.mp4")
        with open(self.video, "wb") as f: f.write(b"mp4")
        self.ses = os.path.join(self.kok, "k.wav")
        with open(self.ses, "wb") as f: f.write(b"RIFF")

    def test_paket_al_api_rapor(self):
        p = gd.paket(gd.b3_planlari(self.sy, n=30))
        self.assertEqual((p["plan"], p["beklenen"], len(p["kol"]["2"]), len(p["kol"]["3"])), (30, 75, 15, 15))
        self.assertTrue(os.path.isfile(os.path.join(p["klasor"], "GOREV.txt")))
        z = os.path.join(gd.paket_kok(), "GELENLER", p["ad"] + ".zip")
        with zipfile.ZipFile(z, "w") as zf:
            for no in p["kol"]["2"]:
                for h in "ab": b = io.BytesIO(); Image.new("RGB", (1376, 768)).save(b, "JPEG"); zf.writestr("%03d_%s.jpg" % (no, h), b.getvalue())
            for no in p["kol"]["3"][:10]:
                for h in "abc": b = io.BytesIO(); Image.new("RGB", (1376, 768)).save(b, "JPEG"); zf.writestr("%03d_%s.jpg" % (no, h), b.getvalue())
        with contextlib.redirect_stdout(io.StringIO()): s = gd.al()
        self.assertEqual(s["kol"]["2"]["oran"], 1.0); self.assertAlmostEqual(s["kol"]["3"]["oran"], 30 / 45, places=3)
        self.assertFalse(gd.durum_oku()["uc_aday_teslim"])
        t = SahteGemini()
        r = gd.api(tasiyici=t, video=self.video, ses=self.ses, paket_api=True, ara_sn=0)
        d = gd.durum_oku()
        self.assertTrue(d["video_girisi"]); self.assertFalse(d["ses_girisi"])
        self.assertTrue(d["gorsel_uygun"]); self.assertTrue(d["gemini_api_paket"]); self.assertEqual(r["gorsel"]["basarili"], 75)
        from saglayicilar import gemini_api as ga
        self.assertFalse(ga.izin_karari("dinleyici")[0]); self.assertTrue(ga.izin_karari("izleyici")[0])
        self.assertTrue(ga.izin_karari("gorsel")[0])
        out = gd.rapor()
        self.assertEqual(o0.durum("e"), "bitti"); self.assertEqual(out["lisans_istegi"]["anahtar"], "gemini_api_ucretsiz")
        self.assertTrue(o0.ozet_oku()["O0e"]["gemini_api_paket"])
        self.assertTrue(olcek.hesapla(1800, olcum=o0.ozet_oku(), ayar={})["el_isi"]["paket"] <= 3)

    def test_kota_ucretsiz_katman_gorsel_uygun_degil(self):
        gd.paket(gd.b3_planlari(self.sy, n=30))
        t = SahteGemini(gorsel_429_sonra=4)
        r = gd.api(tasiyici=t, video=self.video, ses=self.ses, paket_api=True, ara_sn=0)
        d = gd.durum_oku()
        self.assertEqual(d["gemini_katman"], "ucretsiz"); self.assertFalse(d["gorsel_uygun"]); self.assertEqual(r["gorsel"]["ilk_429"], 4)
        self.assertEqual(t.gorsel_n, 5)                                                     # ilk 429'da durdu (yeniden deneme yok)
        gd.rapor(kapat=True)
        self.assertEqual(o0.durum("e"), "bitti"); self.assertTrue(gd.durum_oku()["paket_olculemedi"])

    def test_ucretli_katman_izinsiz_api_yok(self):
        ortak.atomik_yaz(os.path.join(self.veri, "AYARLAR", "GEMINI_DURUMU.json"), {"gemini_katman": "ucretli"})
        t = SahteGemini(); r = gd.api(tasiyici=t, ara_sn=0)
        self.assertEqual(t.istekler, []); self.assertIn("ücretli", r["atlandi"]); self.assertFalse(gd.durum_oku()["gorsel_uygun"])


class TestCapcutDeneme(Taban):
    def setUp(self):
        super().setUp()
        self.tk = os.path.join(self.kok, "CAPCUT"); os.makedirs(self.tk)
        self.p.append(mock.patch.object(cd, "taslak_kok", lambda: self.tk)); self.p[-1].start()
        self.p.append(mock.patch.object(cd, "capcut_acik", lambda: False)); self.p[-1].start()
        import capcut_taslak as ct
        self.yazici = lambda m, k: ct.yaz(m, k, sahte=True)
        self.medya = lambda h: (os.makedirs(os.path.dirname(h), exist_ok=True), open(h, "wb").write(b"mp4"), h)[2]

    def test_klon_calisiyor(self):
        cd.hazirla(yazici=self.yazici, medya_fn=self.medya)
        self.assertEqual(cd.durum_metni()["sonraki"], "olc")
        d = cd.olc(); self.assertEqual((d["okuma"], d["segment_tasima"], d["adim"]), ("calisiyor", "calisiyor", "kullanici_2"))
        self.assertTrue(d["kaynak_degismedi"]); self.assertTrue(os.path.isdir(d["klon_taslak"]))
        d = cd.dogrula()
        self.assertEqual((d["klon"], d["yayin_kaynagi"], d["not_yolu"]), ("calisiyor", "capcut", "yama"))
        import capcut_yama
        self.assertTrue(capcut_yama.bayrak_acik()[0])
        self.assertTrue(os.path.isdir(os.path.join(self.tk, cd.AD)))                       # deneme taslağı silinmez

    def test_sifreli_master(self):
        cd.hazirla(yazici=self.yazici, medya_fn=self.medya)
        with open(os.path.join(self.tk, cd.AD, "draft_content.json"), "wb") as f: f.write(b"\x00\x13sifreli")
        d = cd.olc()
        self.assertEqual((d["sifreli"], d["klon"], d["yayin_kaynagi"], d["not_yolu"]), (True, "calismiyor", "master", "yeni_adla_kur"))
        import capcut_yama
        self.assertFalse(capcut_yama.bayrak_acik()[0])

    def test_capcut_acikken_yazmaz(self):
        with self.assertRaises(cd.Dur) as c: cd.hazirla(yazici=self.yazici, medya_fn=self.medya, acik_fn=lambda: True)
        self.assertEqual(c.exception.kod, cd.KULLANICI); self.assertEqual(os.listdir(self.tk), [])


class TestFilmOlcum0(Taban):
    def test_gorevler_ve_calis(self):
        import film
        with contextlib.redirect_stdout(io.StringIO()) as out: kod = film.main(["olcum0", "--json"])
        self.assertEqual(kod, 0)
        r = json.loads(out.getvalue())
        g = {x["olcum"]: x for x in r["gorevler"]}
        self.assertIn("Ö0-b", g); self.assertTrue(g["Ö0-b"]["paralel"])
        self.assertIn("on_kosul_eksik", g["Ö0-b"]["ayrinti"])
        self.assertEqual(g["Ö0-d"]["sonraki"], "hazirla")
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(film.main(["olcum0", "calis", "z"]), 1)
        with mock.patch.dict(os.environ, {"YZ_FILM_ORTAM": "bulut"}), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(film.main(["olcum0", "calis", "b", "gun"]), 4)


if __name__ == "__main__":
    unittest.main()
