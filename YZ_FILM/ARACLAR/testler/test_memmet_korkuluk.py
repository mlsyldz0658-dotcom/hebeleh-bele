"""Memmet korkuluk testi (PR-0, D-02): Flow uyarısında HER KİPTE dur, sayfaya dokunma; doğrulamada bekleme; tempo yalnız yavaşlar.
Gerçek tarayıcı yok: sahte bir Flow sayfası, Memmet'in sayfada yaptığı her işlemi (tıklama, yazma, gezinme...) kaydeder.
Çalıştırma: python -m unittest discover -s ARACLAR/testler     (YZ_FILM klasöründen)
"""
import os, sys, json, time, shutil, tempfile, unittest, io, contextlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR)
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


if __name__ == "__main__":
    unittest.main()
