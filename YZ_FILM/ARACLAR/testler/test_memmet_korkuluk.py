"""Memmet korkuluk testi (PR-0, D-02): Flow uyarısında HER KİPTE dur, sayfaya dokunma; doğrulamada bekleme; tempo yalnız yavaşlar.
Gerçek tarayıcı yok: sahte bir Flow sayfası, Memmet'in sayfada yaptığı her işlemi (tıklama, yazma, gezinme...) kaydeder.
Çalıştırma: python -m unittest discover -s ARACLAR/testler     (YZ_FILM klasöründen)
"""
import os, sys, json, time, shutil, tempfile, unittest, io, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import memmet

UYARI = "Olağan dışı etkinlik algıladık. Lütfen daha sonra tekrar deneyin."
PROJE = "https://labs.google/fx/tools/flow/project/deneme"


class SahteSayfa:
    """Playwright sayfasının Memmet'in kullandığı kadarı. islemler: sayfayı DEĞİŞTİREN her çağrı."""
    def __init__(self):
        self.metin = ""; self.url = PROJE; self.recaptcha = False; self.kart = {"var": False}
        self.kutu = ""; self.islemler = []; self.yazilanlar = []; self.gonder_tiklaninca = None
        self.keyboard = _Klavye(self); self.mouse = _Fare(self)

    def islem(self, ad): self.islemler.append(ad)

    def evaluate(self, js, *a):
        if "recaptcha" in js: return self.recaptcha
        if "innerText.slice" in js: return self.metin
        if "flow-expandable-prompt" in js: return self.kart
        return None

    def goto(self, url, **k): self.islem("goto"); self.url = url
    def reload(self, **k): self.islem("reload")
    def screenshot(self, **k): self.islem("screenshot")
    def content(self): return ""
    def set_default_timeout(self, t): pass
    def wait_for_selector(self, *a, **k): pass
    def wait_for_url(self, *a, **k): pass
    def locator(self, sec): return _Oge(self, sec)
    def get_by_role(self, rol, name=None, **k): return _Oge(self, f"{rol}:{name}")
    def get_by_text(self, t, **k): return _Oge(self, f"text:{t}")
    def get_by_placeholder(self, t, **k): return _Oge(self, f"ph:{t}")


class _Klavye:
    def __init__(self, s): self.s = s
    def type(self, metin, **k): self.s.islem("type"); self.s.kutu += metin; self.s.yazilanlar.append(metin)
    def press(self, tus): self.s.islem("press:" + tus)


class _Fare:
    def __init__(self, s): self.s = s
    def move(self, *a): self.s.islem("mouse")


class _Oge:
    def __init__(self, s, sec): self.s = s; self.sec = sec
    @property
    def first(self): return self
    def nth(self, i): return self
    def filter(self, **k): return self
    def count(self): return 1
    def is_visible(self): return True
    def is_enabled(self): return True
    def inner_text(self): return self.s.kutu if self.sec == ".ProseMirror" else ""
    def click(self, **k):
        self.s.islem("click:" + self.sec)
        if self.sec == "button:Oluşturmaya başla":
            self.s.kutu = ""
            if self.s.gonder_tiklaninca: self.s.gonder_tiklaninca()
    def fill(self, *a, **k): self.s.islem("fill")
    def type(self, *a, **k): self.s.islem("type")
    def hover(self, **k): self.s.islem("hover")
    def scroll_into_view_if_needed(self, **k): self.s.islem("scroll")


PLAN = {"film": "KORKULUK", "karakterler": {},
        "sahneler": [{"no": n, "parti": 1, "referans": [], "gorsel_istem": f"Scene {n} wide shot of a quiet valley at dawn.",
                      "hareket_istem": f"Scene {n} camera holds. No music."} for n in (1, 2, 3)]}


class Korkuluk(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.kok = os.path.join(self.tmp, "FILM"); os.makedirs(self.kok)
        json.dump(PLAN, open(os.path.join(self.kok, "SAHNELER.json"), "w", encoding="utf-8"))
        ay = os.path.join(self.tmp, "AYARLAR"); os.makedirs(ay)
        self.yamalar = [mock.patch.object(memmet, "AYARLAR", ay), mock.patch.object(memmet, "HESAP", os.path.join(self.tmp, "HESAP")),
                        mock.patch.object(memmet, "AYAR_DOSYA", os.path.join(ay, "MEMMET_AYAR.json")),
                        mock.patch.object(memmet, "FILM_AYAR", os.path.join(ay, "FILM_AYAR.json")),
                        mock.patch.object(memmet, "uyu", self._uyu),
                        mock.patch.object(memmet.Memmet, "bildir", lambda m, msg, acil=False: self.bildirimler.append(msg))]
        for y in self.yamalar: y.start()
        self.bildirimler = []; self.uykular = []; self.uyku_tetik = None
        self.sayfa = SahteSayfa()

    def tearDown(self):
        for y in self.yamalar: y.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _uyu(self, sn):
        self.uykular.append(sn)
        if len(self.uykular) > 500: raise AssertionError("Memmet durmadı: sonsuz bekleme (uyarı fark edilmedi)")
        if self.uyku_tetik: self.uyku_tetik()

    def memmet(self, kip="elle"):
        with contextlib.redirect_stdout(io.StringIO()):
            m = memmet.Memmet(self.kok, {"mod": kip, "asama": "gorsel"})
        m.page = self.sayfa
        for ad in ("mod_ayarla", "yukle", "kutuyu_temizle"): setattr(m, ad, lambda *a, **k: None)
        return m

    def uyarida_dur(self, m):
        """asama() koşar; uyarının belirdiği andaki işlem sayısını döndürür ve Durdur'u doğrular."""
        t0 = time.time()
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c:
            m.asama("gorsel", m.sahneler())
        self.assertEqual(c.exception.kod, "olagandisi")
        self.assertLess(time.time() - t0, 10)
        return c

    def uyari_ver(self):
        self.sayfa.metin = UYARI; self.uyari_aninda = len(self.sayfa.islemler)

    # ---------------------------------------------------------------- T10: her kipte uyarıda dur
    def test_T10_elle_gonder_beklerken_uyari(self):
        m = self.memmet("elle")
        bekleme = []
        def tetik():   # istem yazıldı, Memmet GÖNDER bekliyor (2 sn'lik yoklama); kullanıcı basmadan uyarı belirdi
            if self.uykular[-1] != 2: return
            if not bekleme: bekleme.append(1)
            elif self.sayfa.metin != UYARI: self.uyari_ver()
        self.uyku_tetik = tetik
        self.uyarida_dur(m)
        self.assertEqual(len(self.sayfa.islemler), self.uyari_aninda, "uyarıdan sonra sayfada işlem yapıldı")
        self.assertEqual(len(self.sayfa.yazilanlar), 1, "sonraki plan hazırlanmamalı")
        self.assertNotIn("click:button:Oluşturmaya başla", self.sayfa.islemler, "elle kipte GÖNDER'e Memmet basmaz")

    def test_T10_elle_kullanici_gonderdikten_sonra_uyari(self):
        m = self.memmet("elle")
        def tetik():   # GÖNDER yoklaması sırasında kullanıcı bastı (kutu boşaldı) ve aynı anda uyarı geldi
            if self.uykular[-1] == 2 and self.sayfa.kutu and self.sayfa.metin != UYARI: self.sayfa.kutu = ""; self.uyari_ver()
        self.uyku_tetik = tetik
        self.uyarida_dur(m)
        self.assertEqual(len(self.sayfa.islemler), self.uyari_aninda)
        self.assertEqual(len(self.sayfa.yazilanlar), 1, "kullanıcı GÖNDER'e bassa bile sonraki plan hazırlanmaz")

    def test_T10_gece_gonderimden_sonra_uyari(self):
        json.dump({"izinler": {"gece_flow": True}}, open(memmet.FILM_AYAR, "w", encoding="utf-8"))
        m = self.memmet("gece"); m.on_kosullar()
        self.sayfa.gonder_tiklaninca = self.uyari_ver
        self.uyarida_dur(m)
        self.assertEqual(len(self.sayfa.islemler), self.uyari_aninda)
        self.assertEqual(self.sayfa.islemler.count("click:button:Oluşturmaya başla"), 1)
        self.assertNotIn("goto", self.sayfa.islemler); self.assertNotIn("reload", self.sayfa.islemler)

    def test_T10_gece_sonuc_kartinda_uyari(self):
        json.dump({"izinler": {"gece_flow": True}}, open(memmet.FILM_AYAR, "w", encoding="utf-8"))
        m = self.memmet("gece"); m.A["ayni_anda"] = 1
        def kart():   # sayfa gövdesi temiz, uyarı yalnız sonuç kartında
            self.sayfa.kart = {"var": True, "yuzde": False, "metin": "unusual activity detected"}
            self.uyari_aninda = len(self.sayfa.islemler)
        self.sayfa.gonder_tiklaninca = kart
        self.uyarida_dur(m)
        self.assertEqual(len(self.sayfa.islemler), self.uyari_aninda)
        self.assertEqual(len(self.sayfa.yazilanlar), 1, "uyarılı kart yeniden denenmez")

    def test_T10_dogrulama_beklemez(self):
        m = self.memmet("elle"); self.sayfa.recaptcha = True
        t0 = time.time()
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.asama("gorsel", m.sahneler())
        self.assertEqual(c.exception.kod, "dogrulama"); self.assertLess(time.time() - t0, 10)
        self.assertEqual(self.sayfa.islemler, []); self.assertFalse(any(u >= 10 for u in self.uykular))
        self.assertEqual(memmet.CIKIS["dogrulama"], 2)

    def test_oturum_dusunce_beklemez(self):
        m = self.memmet("elle"); self.sayfa.url = "https://accounts.google.com/signin"
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.asama("gorsel", m.sahneler())
        self.assertEqual(c.exception.kod, "dogrulama")

    # ---------------------------------------------------------------- çıkış, kilit
    def calistir(self, *ek):
        acilan = []
        def chrome_ac(m): acilan.append(1); m.page = self.sayfa
        with mock.patch.object(memmet.Memmet, "chrome_ac", chrome_ac), contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaises(SystemExit) as c:
            memmet.main([self.kok, *ek])
        return c.exception.code, acilan

    def test_uyari_kilit_yazar_cikis_7_ve_kilitliyken_acilmaz(self):
        self.sayfa.metin = UYARI
        kod, acilan = self.calistir()
        self.assertEqual(kod, 7)
        self.assertNotIn("goto", self.sayfa.islemler)
        k = json.load(open(memmet.kilit_yolu(), encoding="utf-8")); self.assertEqual(k["neden"], "olagandisi")
        c = json.load(open(os.path.join(self.kok, "_memmet_cikis.json"), encoding="utf-8"))
        self.assertEqual((c["kod"], c["cikis"]), ("olagandisi", 7))
        self.assertTrue(any("GÖNDER'e basma" in b for b in self.bildirimler))
        # sayfa temizlense bile kilit varken Memmet Chrome'u açmaz
        self.sayfa.metin = ""; self.sayfa.islemler.clear()
        kod, acilan = self.calistir()
        self.assertEqual((kod, acilan, self.sayfa.islemler), (7, [], []))
        kod, acilan = self.calistir("--giris")
        self.assertEqual((kod, acilan), (7, []))

    def test_ayni_hafta_ikinci_uyari_7_gun(self):
        memmet.kilit_yaz("A", "ilk"); os.remove(memmet.kilit_yolu()); memmet.kilit_yaz("B", "ikinci")
        k = json.load(open(memmet.kilit_yolu(), encoding="utf-8"))
        self.assertEqual(k["haftanin_uyarisi"], 2)
        self.assertGreater(time.mktime(time.strptime(k["en_erken"], "%Y-%m-%d %H:%M")), time.time() + 6.9 * 86400)

    def test_gece_izinsiz_acilmaz(self):
        kod, acilan = self.calistir("--mod", "gece")
        self.assertEqual((kod, acilan), (4, []))

    def test_v2_sahneler_4(self):
        p = dict(PLAN, _surum=2); json.dump(p, open(os.path.join(self.kok, "SAHNELER.json"), "w", encoding="utf-8"))
        kod, acilan = self.calistir()
        self.assertEqual((kod, acilan), (4, []))

    # ---------------------------------------------------------------- tempo
    def test_tempo_ayarla_hizlanamaz_yalniz_yavaslar(self):
        json.dump({"gonderim_arasi_sn": [1, 2], "ayni_anda": 6, "mola_kac_gonderimde": 50, "mola_kac_partide": 1,
                   "video_cozunurluk": "360p"}, open(memmet.AYAR_DOSYA, "w", encoding="utf-8"))
        a = memmet.ayar("elle")
        self.assertEqual((a["gonderim_arasi_sn"], a["ayni_anda"], a["mola_kac_gonderimde"]), ([6, 15], 2, 8))
        self.assertEqual(a["mola_kac_partide"], 0); self.assertEqual(a["video_cozunurluk"], "720p")
        json.dump({"_surum": 2, "gonderim_arasi_sn": [20, 40], "mola_kac_gonderimde": 4, "video_cozunurluk": "360p"},
                  open(memmet.AYAR_DOSYA, "w", encoding="utf-8"))
        a = memmet.ayar("elle")
        self.assertEqual((a["gonderim_arasi_sn"], a["mola_kac_gonderimde"], a["video_cozunurluk"]), ([20, 40], 4, "720p"))
        self.assertEqual(memmet.ayar("gece")["gonderim_arasi_sn"], [20, 40])
        self.assertEqual(memmet.ayar("gece")["parti_mola_dk"], [15, 30])

    def test_mola_yeniden_acilista_sifirlanmaz(self):
        m = self.memmet("elle")
        with contextlib.redirect_stdout(io.StringIO()):
            for _ in range(8): m.gonderim_kaydet()
        T = json.load(open(memmet.tempo_yolu(), encoding="utf-8"))
        self.assertGreaterEqual(T["mola_bitis"] - time.time(), 3 * 60 - 5)
        m2 = self.memmet("elle"); self.uykular.clear()
        with contextlib.redirect_stdout(io.StringIO()): m2.tempo_bekle()
        self.assertTrue(self.uykular and self.uykular[0] >= 3 * 60 - 5, self.uykular)

    def test_gonderimler_arasi_en_az_6_sn(self):
        m = self.memmet("elle")
        with contextlib.redirect_stdout(io.StringIO()): m.gonderim_kaydet(); self.uykular.clear(); m.tempo_bekle()
        self.assertTrue(self.uykular and self.uykular[0] >= 5.5)

    def test_gunluk_gorsel_tavani_ve_gorselden_videoya_bekleme(self):
        m = self.memmet("elle")
        with contextlib.redirect_stdout(io.StringIO()):
            for _ in range(20): memmet.flow_yuk.gonderim_kaydet("gorsel", "elle", kok=memmet.HESAP, simdi=time.time() - 30)
            with self.assertRaises(memmet.Durdur) as c: m.tempo_bekle("gorsel")
        self.assertEqual(c.exception.kod, "yuk"); self.assertIn("tavan", str(c.exception))
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.tempo_bekle("video")
        self.assertIn("saat", str(c.exception))     # son görselden 12 saat geçmeden video yok
        self.assertEqual(memmet.CIKIS["yuk"], 2)

    def test_gonderim_yuk_defterine_yazilir(self):
        m = self.memmet("elle")
        with contextlib.redirect_stdout(io.StringIO()): m.gonderim_kaydet("video", 7)
        satir = memmet.flow_yuk.yuk_oku(memmet.HESAP)[-1]
        self.assertEqual((satir["tur"], satir["plan"], satir["mod"], satir["film"]), ("video", 7, "elle", "KORKULUK"))

    def test_kaynak_kodda_atlatma_yok(self):
        kaynak = open(os.path.join(ARACLAR, "memmet.py"), encoding="utf-8").read().lower()
        for yasak in ("pyautogui", "pynput", "sendkeys", "page.reload", "stealth", "undetected"):
            self.assertNotIn(yasak, kaynak)
        for k in ("olağan", "olagan", "unusual"):
            self.assertFalse(any(k in h for h in memmet.HATA_KELIMELERI), "uyarı kelimesi hata listesinde: yeniden gönderime yol açar")


class FlowSaglayici(unittest.TestCase):
    def test_cikis_kodu_kisitlandi(self):
        from saglayicilar import flow
        self.assertEqual(flow.cikis_cevir(7).kod, "olagandisi")
        self.assertEqual(flow.cikis_cevir(2).kod, "dogrulama")
        self.assertEqual(flow.cikis_cevir(4).kod, "ortam")
        self.assertEqual(flow.cikis_cevir(9).kod, "bilinmeyen")
        for rc in (7, 2, 4, 9, 1): self.assertFalse(flow.cikis_cevir(rc).gecilebilir)
        d = tempfile.mkdtemp()
        try:
            p = os.path.join(d, "_memmet_cikis.json")
            json.dump({"kod": "kredi", "cikis": 2, "mesaj": "Flow kredisi bitti."}, open(p, "w", encoding="utf-8"))
            e = flow.cikis_cevir(2, p); self.assertEqual(e.kod, "kredi"); self.assertTrue(e.gecilebilir)
            json.dump({"kod": "kredi", "cikis": 2}, open(p, "w", encoding="utf-8"))
            self.assertEqual(flow.cikis_cevir(7, p).kod, "olagandisi")   # 7 her zaman uyarı
        finally: shutil.rmtree(d, ignore_errors=True)


# ==================================================================== PR-11: Memmet v2 (BLOK_PLANI) — sahte Flow sayfasında blok akışı
import blok_plani, kredi, memmet_topla, memmet_yama, difflib  # noqa: E402
import _video_fikstur as VF  # noqa: E402

HAZIR = {"var": True, "yuzde": False, "video_kutusu": True, "video_url": "https://flow-content.google/video/0f0e0d0c-0b0a-0908-0706-050403020100",
         "metin": "plan"}


class BlokV2(unittest.TestCase):
    """memmet.py --blok: her PR-0 korkuluğu v2'de de geçerli (her kipte uyarıda dur, sayfa işlemi 0, doğrulamada bekleme yok) +
    gönderim kaydı önce, filtre reddinde yedek bir kez, zaman aşımında yeniden gönderim yok, DUR, imza, BUTK, kilit, hesap sha1."""
    def setUp(self):
        self.tmp = tempfile.mkdtemp(); self.kok = os.path.join(self.tmp, "FILM")
        ay = os.path.join(self.tmp, "AYARLAR"); os.makedirs(ay)
        self.yamalar = [mock.patch.object(memmet, "AYARLAR", ay), mock.patch.object(memmet, "HESAP", os.path.join(self.tmp, "HESAP")),
                        mock.patch.object(memmet, "AYAR_DOSYA", os.path.join(ay, "MEMMET_AYAR.json")),
                        mock.patch.object(memmet, "FILM_AYAR", os.path.join(ay, "FILM_AYAR.json")),
                        mock.patch.object(memmet, "uyu", self._uyu),
                        mock.patch.object(memmet.Memmet, "bildir", lambda m, msg, acil=False: self.bildirimler.append(msg))]
        for y in self.yamalar: y.start()
        self.bildirimler = []; self.uykular = []; self.uyku_tetik = None; self.sayfa = SahteSayfa()
        self.doc = VF.film_kur(self.kok, [VF.plan(n) for n in (1, 2, 3)])
        self.imza = self.blok_kur()

    def tearDown(self):
        for y in self.yamalar: y.stop()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _uyu(self, sn):
        self.uykular.append(sn)
        if len(self.uykular) > 500: raise AssertionError("Memmet durmadı: sonsuz bekleme")
        if self.uyku_tetik: self.uyku_tetik()

    def blok_kur(self):
        with contextlib.redirect_stdout(io.StringIO()): BP, kod = blok_plani.plan_kur(self.kok, hesap_kok=memmet.HESAP)
        self.assertEqual(kod, 0); return BP["onizleme_imza"]

    def mm(self, kip="gece", blok="B01"):
        if kip == "gece": json.dump({"izinler": {"gece_flow": True}}, open(memmet.FILM_AYAR, "w", encoding="utf-8"))
        with contextlib.redirect_stdout(io.StringIO()):
            m = memmet.Memmet(self.kok, {"mod": kip, "blok": blok, "onizleme": self.imza}); m.on_kosullar(); m.blok_dogrula()
        m.page = self.sayfa; m.A["ayni_anda"] = 1
        for ad in ("mod_ayarla", "yukle", "kutuyu_temizle", "blok_denetimleri"): setattr(m, ad, lambda *a, **k: None)
        m.indir = lambda url, hedef: open(hedef, "wb").write(b"\0" * 20000)
        return m

    def kos(self, m):
        with contextlib.redirect_stdout(io.StringIO()): return m.blok_asama()

    def gonderimler(self): return [s for s in kredi.defter_oku(self.kok)[0] if s.get("olay") == "gonderim"]
    def tiklamalar(self): return self.sayfa.islemler.count("click:button:Oluşturmaya başla")

    def uyari_ver(self): self.sayfa.metin = UYARI; self.uyari_aninda = len(self.sayfa.islemler)

    def uyarida_dur(self, m):
        t0 = time.time()
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.blok_asama()
        self.assertEqual(c.exception.kod, "olagandisi"); self.assertLess(time.time() - t0, 10)
        self.assertEqual(len(self.sayfa.islemler), self.uyari_aninda, "uyarıdan sonra sayfada işlem yapıldı")
        self.assertNotIn("reload", self.sayfa.islemler)
        return c

    # ---------------------------------------------------------------- T10 v2: her kipte
    def test_v2_T10_elle_gonder_beklerken_uyari(self):
        m = self.mm("elle"); bekleme = []
        def tetik():
            if self.uykular[-1] != 2: return
            if not bekleme: bekleme.append(1)
            elif self.sayfa.metin != UYARI: self.uyari_ver()
        self.uyku_tetik = tetik
        self.uyarida_dur(m)
        self.assertEqual(len(self.sayfa.yazilanlar), 1); self.assertEqual(self.tiklamalar(), 0, "elle kipte GÖNDER'e Memmet basmaz")
        self.assertEqual(len(self.gonderimler()), 1, "gönderim kaydı istem hazırlanmadan önce yazılır, sonrası yok")
        self.assertFalse(blok_plani.blok_bitti_mi(self.kok, "B01"))

    def test_v2_T10_gece_gonderimden_sonra_uyari(self):
        m = self.mm("gece"); self.sayfa.gonder_tiklaninca = self.uyari_ver
        self.uyarida_dur(m)
        self.assertEqual(self.tiklamalar(), 1); self.assertNotIn("goto", self.sayfa.islemler)
        self.assertEqual(len(self.gonderimler()), 1)

    def test_v2_T10_gece_sonuc_kartinda_uyari(self):
        m = self.mm("gece")
        def kart():
            self.sayfa.kart = {"var": True, "yuzde": False, "metin": "unusual activity detected"}; self.uyari_aninda = len(self.sayfa.islemler)
        self.sayfa.gonder_tiklaninca = kart
        self.uyarida_dur(m)
        self.assertEqual(len(self.sayfa.yazilanlar), 1, "uyarılı kart yeniden denenmez, sonraki plan hazırlanmaz")

    def test_v2_uyari_cikis_7_kilit_ve_bekleyen_kayitli(self):
        self.sayfa.gonder_tiklaninca = self.uyari_ver
        json.dump({"izinler": {"gece_flow": True}}, open(memmet.FILM_AYAR, "w", encoding="utf-8"))
        def hazirla(m):
            m.page = self.sayfa; m.A["ayni_anda"] = 1
            for ad in ("mod_ayarla", "yukle", "kutuyu_temizle", "blok_denetimleri"): setattr(m, ad, lambda *a, **k: None)
        with mock.patch.object(memmet.Memmet, "chrome_ac", hazirla), mock.patch.object(memmet.Memmet, "giris_kontrol", lambda m, **k: True), \
                mock.patch.object(memmet.Memmet, "projeye_git", lambda m: None), contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaises(SystemExit) as c:
            memmet.main([self.kok, "--blok", "B01", "--onizleme", self.imza, "--mod", "gece"])
        self.assertEqual(c.exception.code, 7)
        self.assertEqual(json.load(open(memmet.kilit_yolu(), encoding="utf-8"))["neden"], "olagandisi")
        self.assertEqual(len(blok_plani.acik_gonderimler(self.kok)), 1, "gönderilmiş iş memmet_topla için açık kalır")
        self.assertFalse(os.path.exists(memmet.flow_kilit_yolu()), "FLOW.kilit bırakılır")

    def test_v2_dogrulama_beklemez(self):
        m = self.mm("elle"); self.sayfa.recaptcha = True
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.blok_asama()
        self.assertEqual(c.exception.kod, "dogrulama"); self.assertEqual(self.sayfa.islemler, [])
        self.assertEqual(self.gonderimler(), [])

    # ---------------------------------------------------------------- blok akışı
    def test_v2_mutlu_yol_gece_kayit_once(self):
        m = self.mm("gece"); sira = []
        def tik():
            sira.append(len(self.gonderimler())); self.sayfa.kart = dict(HAZIR)
        self.sayfa.gonder_tiklaninca = tik
        o = self.kos(m)
        self.assertEqual(sorted(o["indirilen"]), [1, 2, 3]); self.assertEqual(sira, [1, 2, 3], "kredi satırı her GÖNDER'den ÖNCE")
        for n in (1, 2, 3):
            k = json.load(open(os.path.join(self.kok, "KUNYE", f"{n:03d}.json"), encoding="utf-8"))
            self.assertEqual(k["plan"], n); self.assertTrue(k["is"].startswith(f"V-{n}-d1-"))
            self.assertEqual(k["plan_imza"], blok_plani.plan_imza(self.doc["sahneler"][n - 1]))
            self.assertTrue(os.path.exists(os.path.join(self.kok, "SIRALI_VIDEO", f"{n:03d}.mp4")))
        with contextlib.redirect_stdout(io.StringIO()): m.blok_bitir()
        self.assertTrue(blok_plani.blok_bitti_mi(self.kok, "B01")); self.assertTrue(blok_plani.blok_bitti_mi(self.kok, "*"))
        r = json.load(open(os.path.join(self.kok, "_RAPOR", "FLOW_B01.json"), encoding="utf-8")); self.assertEqual(r["sonuc"], "GEC")
        self.assertEqual(blok_plani.acik_gonderimler(self.kok), {})
        self.assertEqual(len([u for u in memmet.flow_yuk.yuk_oku(memmet.HESAP) if u.get("tur") == "video"]), 3)

    def test_v2_elle_kullanici_basar(self):
        m = self.mm("elle")
        def tetik():
            if self.uykular[-1] == 2 and self.sayfa.kutu: self.sayfa.kutu = ""; self.sayfa.kart = dict(HAZIR)
        self.uyku_tetik = tetik
        o = self.kos(m)
        self.assertEqual(sorted(o["indirilen"]), [1, 2, 3]); self.assertEqual(self.tiklamalar(), 0)

    def test_v2_filtre_reddi_yedek_bir_kez(self):
        m = self.mm("gece")
        self.sayfa.gonder_tiklaninca = lambda: self.sayfa.kart.update(var=True, yuzde=False, metin="this prompt violates our policy")
        o = self.kos(m)
        self.assertEqual(len(self.sayfa.yazilanlar), 6, "plan başına ana + yedek: 2 gönderim, üçüncüsü yok")
        for n in (1, 2, 3):
            yaz = [y for y in self.sayfa.yazilanlar if f"plan {n} " in y.lower() or f"of plan {n}." in y]
            self.assertEqual(len(yaz), 2); self.assertIn("waits calmly", yaz[1], "ikinci gönderim derlenmiş yedek istemdir")
        self.assertEqual(sorted(r["plan"] for r in o["reddedilen"]), [1, 2, 3])
        with contextlib.redirect_stdout(io.StringIO()): m.blok_bitir()
        r = json.load(open(os.path.join(self.kok, "_RAPOR", "FLOW_B01.json"), encoding="utf-8"))
        self.assertEqual(r["sonuc"], "HATA"); self.assertTrue(all("yonetmen·onarim" in h["oneri"] for h in r["hatalar"]))

    def test_v2_filtre_reddi_yedek_yoksa_tek_gonderim(self):
        for p in self.doc["sahneler"]: p.pop("hareket_istem_yedek")
        VF.sahneler_yaz(self.kok, self.doc); self.imza = self.blok_kur()
        m = self.mm("gece")
        self.sayfa.gonder_tiklaninca = lambda: self.sayfa.kart.update(var=True, yuzde=False, metin="policy violation")
        self.kos(m)
        self.assertEqual(len(self.sayfa.yazilanlar), 3)

    def test_v2_zaman_asimi_yeniden_gondermez_once_topla(self):
        m = self.mm("gece"); m.A["video_zaman_asimi_sn"] = -1
        self.sayfa.gonder_tiklaninca = lambda: self.sayfa.kart.update(var=True, yuzde=True, metin="%40")
        o = self.kos(m)
        self.assertEqual(self.tiklamalar(), 3); self.assertEqual(sorted(o["zaman_asimi"]), [1, 2, 3])
        self.assertNotIn("goto", self.sayfa.islemler, "zaman aşımında sayfa yenilenmez/gezilmez")
        self.assertEqual(len(blok_plani.acik_gonderimler(self.kok)), 3)
        ok, neden = blok_plani.uygun_mu(self.kok, self.doc["sahneler"][0], {}, "video")
        self.assertFalse(ok); self.assertIn("memmet_topla", neden)

    def test_v2_dur_dosyasi_yeni_gonderim_yok(self):
        m = self.mm("gece")
        def tik():
            self.sayfa.kart = dict(HAZIR); open(os.path.join(self.kok, "DUR"), "w").write("{}")
        self.sayfa.gonder_tiklaninca = tik
        o = self.kos(m)
        self.assertEqual(self.tiklamalar(), 1); self.assertTrue(o["dur"]); self.assertEqual(o["indirilen"], [1], "elindeki iş bitirilir")
        with contextlib.redirect_stdout(io.StringIO()): m.blok_bitir()
        self.assertFalse(blok_plani.blok_bitti_mi(self.kok, "B01"))
        self.assertEqual(memmet.CIKIS["dur"], 2)

    def test_v2_bloksuz_imzasiz_animatiksiz_4_chrome_acilmaz(self):
        acilan = []
        def calistir(*ek):
            with mock.patch.object(memmet.Memmet, "chrome_ac", lambda m: acilan.append(1)), contextlib.redirect_stdout(io.StringIO()), \
                    self.assertRaises(SystemExit) as c:
                memmet.main([self.kok, *ek])
            return c.exception.code
        self.assertEqual(calistir(), 4)                                              # v2 + --blok yok
        self.assertEqual(calistir("--blok", "B01"), 4)                               # imza yok
        self.assertEqual(calistir("--blok", "B01", "--onizleme", "deadbeef0000"), 4)  # imza tutmuyor
        on = json.load(open(os.path.join(self.kok, "URETIM_ONIZLEME.json"), encoding="utf-8")); on["taslak"] = True
        ortak_yaz = memmet._atomik; ortak_yaz(os.path.join(self.kok, "URETIM_ONIZLEME.json"), on)
        self.assertEqual(calistir("--blok", "B01", "--onizleme", self.imza), 4)      # kesin bütçe yok
        on["taslak"] = False; ortak_yaz(os.path.join(self.kok, "URETIM_ONIZLEME.json"), on)
        ortak_yaz(os.path.join(self.kok, "FILM_DURUM.json"), {"animatik": {"durum": "bekliyor"}})
        self.assertEqual(calistir("--blok", "B01", "--onizleme", self.imza), 4)      # animatik imzası yok
        self.assertEqual(acilan, []); self.assertEqual(self.gonderimler(), [])

    def test_v2_uygunluk_kaynak_klip_bayat_gorsel_zincir_ayni_blok(self):
        p = self.doc["sahneler"]
        p[0]["uretim"]["kaynak_klip"] = {"plan": 9, "bas": 0.0}
        VF.gorsel_yaz(os.path.join(self.kok, "SIRALI_GORSEL", "002.jpg"), 55)          # G1 kaydından sonra değişti
        p[2]["uretim"]["zincir"] = {"yontem": "son_kare", "kaynak": 2, "derinlik": 1, "g1z": {"sonuc": "GEC", "sha1": "0" * 12}}
        VF.sahneler_yaz(self.kok, self.doc)
        m = self.mm("gece"); m.blok_nolar = {1, 2, 3}; m.planlar = {int(x["no"]): x for x in p}
        self.sayfa.gonder_tiklaninca = lambda: self.sayfa.kart.update(HAZIR)
        o = self.kos(m)
        self.assertEqual(self.tiklamalar(), 0)
        neden = {a["plan"]: a["neden"] for a in o["atlanan"]}
        self.assertIn("kaynak_klip", neden[1]); self.assertIn("bayat", neden[2]); self.assertIn("aynı blokta", neden[3])

    def test_v2_butk_red_5_gonderim_yok(self):
        VF.film_kur(self.kok, [VF.plan(n) for n in (1, 2, 3)], butce_ana=5); self.imza = self.blok_kur()
        m = self.mm("gece")
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.blok_asama()
        self.assertEqual(c.exception.kod, "butce"); self.assertEqual(memmet.CIKIS["butce"], 5)
        self.assertEqual(self.tiklamalar(), 0); self.assertEqual(self.gonderimler(), [])
        self.assertEqual(self.sayfa.yazilanlar, [])

    def test_ayni_hesapta_ikinci_memmet_8(self):
        os.makedirs(memmet.HESAP, exist_ok=True)
        json.dump({"pid": os.getppid(), "zaman": time.time(), "film": "BASKA"}, open(memmet.flow_kilit_yolu(), "w", encoding="utf-8"))
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: memmet.flow_kilidi_al("FILM")
        self.assertEqual((c.exception.kod, memmet.CIKIS["mesgul"]), ("mesgul", 8))
        json.dump({"pid": os.getppid(), "zaman": time.time() - 2 * 3600, "film": "BASKA"}, open(memmet.flow_kilit_yolu(), "w", encoding="utf-8"))
        self.assertTrue(memmet.flow_kilidi_al("FILM")); memmet.flow_kilidi_birak()       # bayat kilit kalkar

    def test_hesap_yalniz_sha1_ve_uyaridan_sonra_degisim_kilit(self):
        m = self.mm("elle"); eposta = ["Google Hesabı: Mara (mara.deneme@example.com)"]
        self.sayfa.evaluate = lambda js, *a: eposta[0] if "aria-label" in js and "getAttribute" in js else None
        with contextlib.redirect_stdout(io.StringIO()): k = m.hesap_denetle()
        self.assertEqual(len(k), 8)
        for ad in os.listdir(memmet.HESAP):
            self.assertNotIn("example.com", open(os.path.join(memmet.HESAP, ad), encoding="utf-8", errors="replace").read())
        memmet.kilit_yaz("FILM", "uyarı"); shutil.move(memmet.kilit_yolu(), memmet.kilit_yolu() + ".eski")
        eposta[0] = "Google Account: Baska (ikinci.hesap@example.com)"
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.hesap_denetle()
        self.assertEqual(c.exception.kod, "kilitli")
        self.assertEqual(json.load(open(memmet.kilit_yolu(), encoding="utf-8"))["neden"], "hesap_degisti")

    def test_bakiye_salt_okunur(self):
        m = self.mm("elle"); self.sayfa.metin = "Flow · Kalan 1.250 AI kredi"
        with contextlib.redirect_stdout(io.StringIO()): b = m.bakiye_oku()
        self.assertEqual(b, 1250); self.assertEqual(self.sayfa.islemler, [], "bakiye okuma sayfada işlem yapmaz")
        self.assertEqual(json.load(open(os.path.join(memmet.HESAP, "FLOW_BAKIYE.json"), encoding="utf-8"))["bakiye"], 1250)
        self.sayfa.metin = "Flow"
        with contextlib.redirect_stdout(io.StringIO()): self.assertIsNone(m.bakiye_oku())
        self.sayfa.metin = UYARI
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: m.bakiye_oku()
        self.assertEqual(c.exception.kod, "olagandisi")

    def test_gunduz_otomatik_kip_yok_varsayilan_elle(self):
        self.assertEqual(memmet.KIPLER, ("elle", "gece"))
        for k in ("gunduz", "otomatik"):
            with self.assertRaises(memmet.Durdur) as c: memmet.Memmet(self.kok, {"mod": k, "blok": "B01", "onizleme": self.imza})
            self.assertEqual(c.exception.kod, "ortam")
        self.assertEqual(memmet.argumanlar([self.kok, "--blok", "B01"])[1]["mod"], "elle")
        self.assertEqual(memmet.argumanlar(["--film", self.kok, "--bakiye"])[0], self.kok)

    def test_tempo_her_gonderimden_once(self):
        m = self.mm("gece"); cagri = []
        asil = m.tempo_bekle
        m.tempo_bekle = lambda tur=None: (cagri.append(tur), asil(tur))[1]
        self.sayfa.gonder_tiklaninca = lambda: self.sayfa.kart.update(HAZIR)
        self.kos(m)
        self.assertEqual(cagri, ["video", "video", "video"])

    # ---------------------------------------------------------------- memmet_topla: yeni gönderim YOK
    def _acik_is(self):
        m = self.mm("gece"); self.sayfa.gonder_tiklaninca = lambda: self.sayfa.kart.update(var=True, yuzde=True, metin="%10")
        m.A["video_zaman_asimi_sn"] = -1; self.kos(m)
        self.sayfa.islemler.clear(); self.sayfa.yazilanlar.clear(); self.sayfa.kart = {"var": False}
        m.D["proje_url"] = PROJE; m.save()

    def test_topla_indirir_gondermez(self):
        self._acik_is(); self.sayfa.kart = dict(HAZIR)
        with mock.patch.object(memmet.Memmet, "indir", lambda m, u, h: open(h, "wb").write(b"\0" * 20000)), \
                mock.patch.object(memmet.Memmet, "girisli", lambda m: True), contextlib.redirect_stdout(io.StringIO()):
            kod, oz = memmet_topla.topla(self.kok, sayfa=self.sayfa)
        self.assertEqual((kod, sorted(oz["indirilen"])), (0, [1, 2, 3]))
        self.assertEqual(self.sayfa.yazilanlar, []); self.assertNotIn("click:button:Oluşturmaya başla", self.sayfa.islemler)
        self.assertNotIn("type", self.sayfa.islemler); self.assertNotIn("reload", self.sayfa.islemler)
        self.assertTrue(blok_plani.blok_bitti_mi(self.kok, "B01"))

    def test_topla_bulamazsa_kayip_kilitliyken_acilmaz_uyarida_durur(self):
        self._acik_is()
        with mock.patch.object(memmet.Memmet, "girisli", lambda m: True), contextlib.redirect_stdout(io.StringIO()):
            kod, oz = memmet_topla.topla(self.kok, sayfa=self.sayfa)
        self.assertEqual((kod, sorted(oz["kayip"])), (0, [1, 2, 3]))
        self._acik_is(); memmet.kilit_yaz("FILM", "uyarı")
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(memmet.Durdur) as c: memmet_topla.topla(self.kok, sayfa=self.sayfa)
        self.assertEqual(c.exception.kod, "kilitli"); self.assertEqual(self.sayfa.islemler, [])
        shutil.move(memmet.kilit_yolu(), memmet.kilit_yolu() + ".eski"); self.uyari_ver()
        with mock.patch.object(memmet.Memmet, "girisli", lambda m: True), contextlib.redirect_stdout(io.StringIO()), \
                self.assertRaises(memmet.Durdur) as c:
            memmet_topla.topla(self.kok, sayfa=self.sayfa)
        self.assertEqual(c.exception.kod, "olagandisi"); self.assertEqual(len(self.sayfa.islemler), self.uyari_aninda)


class Yama(unittest.TestCase):
    """memmet_yama.py: memmet-bakımcı onarımının korkulukları."""
    def setUp(self): self.kaynak = open(os.path.join(ARACLAR, "memmet.py"), encoding="utf-8").read()

    def diff(self, eski, yeni):
        return "".join(difflib.unified_diff(self.kaynak.splitlines(True), self.kaynak.replace(eski, yeni, 1).splitlines(True),
                                            "a/memmet.py", "b/memmet.py"))

    def sonuc(self, eski, yeni, test=False):
        self.assertIn(eski, self.kaynak)
        r = memmet_yama.denetle(self.diff(eski, yeni), test=test)
        return r["sonuc"], {x["madde"]: x["sonuc"] for x in r["maddeler"]}

    def test_yavaslatan_yama_gecer_ve_T10_yamali_kopyada_kosar(self):
        if os.environ.get("MEMMET_YAMA_IC"): self.skipTest("iç koşu (özyineleme yok)")
        s, m = self.sonuc('"elle": {"gonderim_arasi_sn": [6, 15]', '"elle": {"gonderim_arasi_sn": [8, 15]', test=True)
        self.assertEqual(s, "GEC", m); self.assertEqual(m["T10_her_kipte"], "GEC")

    def test_korkuluk_ihlalleri_kalir(self):
        durum = [
            ('"elle": {"gonderim_arasi_sn": [6, 15]', '"elle": {"gonderim_arasi_sn": [3, 15]', "tempo_yalniz_yavaslar"),
            ('"ayni_anda": 2, "mola_kac_gonderimde": 8', '"ayni_anda": 3, "mola_kac_gonderimde": 8', "tempo_yalniz_yavaslar"),
            ('"mola_kac_gonderimde": 8', '"mola_kac_gonderimde": 12', "tempo_yalniz_yavaslar"),
            ('"unusual traffic", ', '', "uyari_kelimeleri_buyur"),
            ('HATA_KELIMELERI = ["politika", ', 'HATA_KELIMELERI = ["unusual", "politika", ', "uyari_kelimeleri_buyur"),
            ("import os, sys, re, json", "import pyautogui\nimport os, sys, re, json", "yasak_cagri"),
            ("            raise Durdur(\"Flow uyarı verdi", "            self.page.goto(FLOW)\n            raise Durdur(\"Flow uyarı verdi", "yeniden_deneme_artmaz"),
            ('args = {"asama": "hepsi", "mod": "elle"}', 'args = {"asama": "hepsi", "mod": "gece"}', "mod_varsayilan_elle"),
            ('"olagandisi": 7, "kilitli": 7', '"olagandisi": 2, "kilitli": 7', "mod_varsayilan_elle"),
            ("        d = flow_yuk.tempo_durumu(self.A[\"kip\"], kok=HESAP)", "        d = {\"sonraki_izin\": 0}", "flow_tempo_okunur"),
            ('TEMPO = {\n', 'TEMPO = {\n    "gunduz": {"gonderim_arasi_sn": [6, 15], "ayni_anda": 2, "mola_kac_gonderimde": 8, "gonderim_mola_dk": [3, 6], '
                         '"mola_kac_partide": 0, "parti_mola_dk": [0, 0]},\n', "tempo_yalniz_yavaslar"),
        ]
        for eski, yeni, madde in durum:
            s, m = self.sonuc(eski, yeni)
            self.assertEqual((s, m[madde]), ("KAL", "KAL"), f"{madde}: {yeni[:50]}")

    def test_buyuk_yama_ve_baska_dosya_kalir(self):
        kirk = "\n".join(f"# satır {i}" for i in range(90))
        s, m = self.sonuc("uyu = time.sleep", "uyu = time.sleep\n" + kirk); self.assertEqual(m["boyut"], "KAL")
        d = self.diff("uyu = time.sleep", "uyu = time.sleep  # x").replace("a/memmet.py", "a/film.py").replace("b/memmet.py", "b/film.py")
        self.assertEqual({x["madde"]: x["sonuc"] for x in memmet_yama.denetle(d, test=False)["maddeler"]}["boyut"], "KAL")


if __name__ == "__main__":
    unittest.main()
