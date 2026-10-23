"""flow_yuk.py testleri (TASARIM D-02 d, D-03, D-04, §8.4; [UM2] T21, T22, T28): mola sıfırlanmaz, günlük görsel tavanı,
görselden videoya bekleme, haftalık kilit, hesap değişimi kilidi, UYARI_GECTI şartları; PR-0 Memmet dosyalarıyla geriye uyum.
Gerçek bekleme yok: bütün zamanlar 'simdi' ile verilir."""
import os, sys, json, time, random, shutil, tempfile, unittest, io, contextlib, datetime
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import ortak, memmet, flow_yuk as fy

T0 = time.mktime((2026, 10, 21, 10, 0, 0, 0, 0, -1))      # çarşamba 10:00 (yerel)
DK, SA, GUN = 60, 3600, 86400
EPOSTA_A, EPOSTA_B = "asil.hesap@example.com", "baska.hesap@example.com"


class Taban(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="flowyuk_"); self.addCleanup(shutil.rmtree, self.d, True)
        self.kok = os.path.join(self.d, "HESAP")
        for k in ("HESAP", "AYARLAR", "BILGI"): os.makedirs(os.path.join(self.d, k))
        self.E = fy.esik_yukle(self.kok); self.rnd = random.Random(7)

    def gonder(self, tur, kip, t, **k):
        return fy.gonderim_kaydet(tur, kip, film="F_TEST", kok=self.kok, E=self.E, simdi=t, rnd=self.rnd, **k)

    def izin(self, tur, kip, t): return fy.izinli_mi(tur, kip, kok=self.kok, E=self.E, simdi=t)

    def memmet_hesap(self): return mock.patch.object(memmet, "HESAP", self.kok)


class Tempo(Taban):
    def test_tempo_memmet_ile_ayni(self):
        for kip in memmet.KIPLER:
            t = fy.tempo(kip, self.kok, self.E, T0); t.pop("carpan")
            self.assertEqual(t, memmet.TEMPO[kip])

    def test_gonderim_arasi_ve_kayit(self):
        T = self.gonder("video", "elle", T0, plan=5)
        self.assertTrue(T0 + 6 <= T["sonraki_izin"] <= T0 + 15)
        satir = fy.yuk_oku(self.kok)[0]
        self.assertEqual((satir["tur"], satir["mod"], satir["plan"], satir["film"]), ("video", "elle", 5, "F_TEST"))
        self.assertEqual(self.izin("video", "elle", T0 + 5)["kod"], fy.BEKLE)
        self.assertTrue(self.izin("video", "elle", T0 + 16)["izinli"])
        # gece kipine geçince gönderim arası gecenin alt sınırının (12 sn) altına inmez
        self.assertEqual(self.izin("video", "gece", T0 + 11)["kod"], fy.BEKLE)

    def test_mola_yeniden_acilista_sifirlanmaz(self):
        t = T0
        for i in range(8): self.gonder("video", "elle", t); t += 20
        T = fy.tempo_oku(self.kok)
        self.assertTrue(t - 20 + 3 * DK <= T["mola_bitis"] <= t - 20 + 6 * DK)
        d = fy.tempo_durumu("elle", self.kok, self.E, t)              # yeni süreç gibi: yalnız dosyadan
        self.assertTrue(d["molada"]); self.assertEqual(d["molaya_kalan_gonderim"], 8)
        self.assertEqual(self.izin("video", "elle", t)["kod"], fy.BEKLE)
        self.assertTrue(self.izin("video", "elle", T["mola_bitis"] + 1)["izinli"])

    def test_parti_molasi_gece(self):
        self.assertFalse(fy.blok_bitti("gece", self.kok, self.E, T0, self.rnd))
        self.assertTrue(fy.blok_bitti("gece", self.kok, self.E, T0, self.rnd))
        b = fy.tempo_oku(self.kok)["mola_bitis"]
        self.assertTrue(T0 + 15 * DK <= b <= T0 + 30 * DK)

    def test_memmet_v1_dosyasi_okunur_ve_ek_alanlar_korunur(self):
        ortak.atomik_yaz(fy.tempo_yolu(self.kok), {"_surum": 1, "son_gonderim": T0, "sonraki_izin": T0 + 10, "mola_bitis": T0 + 200,
                                                   "gonderim_sayaci": 8, "parti_sayaci": 0, "kip": "elle"})
        self.assertEqual(self.izin("video", "elle", T0 + 100)["kod"], fy.BEKLE)
        self.gonder("gorsel", "elle", T0 + 300)
        T = fy.tempo_oku(self.kok); self.assertEqual(T["gonderim_sayaci"], 9); self.assertIn("gunluk", T)
        # Memmet aynı dosyaya (flow_yuk üzerinden) yazınca ek alanlar kaybolmaz
        sahte = mock.Mock(A=memmet.ayar("elle"), film="F_TEST", log=lambda *a: None)
        sahte.tempo_ek = lambda: memmet.Memmet.tempo_ek(sahte)
        with self.memmet_hesap(): memmet.Memmet.gonderim_kaydet(sahte, "video")
        T2 = fy.tempo_oku(self.kok)
        self.assertEqual(T2["gonderim_sayaci"], 10); self.assertEqual(T2["gunluk"]["video"], 1)   # Memmet artık günlük sayıyı da yazar
        self.assertEqual(T2["son_gorsel_gonderimi"], T["son_gorsel_gonderimi"])

    def test_ayar_yalniz_yavaslatir(self):
        veri = self.d
        ortak.atomik_yaz(os.path.join(veri, "AYARLAR", "FILM_AYAR.json"), {"_surum": 1, "gorsel_gunluk_tavan": 50})
        ortak.atomik_yaz(os.path.join(veri, "BILGI", "KURALLAR_OGRENILEN.json"), {"_surum": 3, "kurallar": [
            {"id": "OK-0001", "tur": "tempo", "durum": "aktif", "deger": {"gece": {"gonderim_arasi_sn": [20, 40]}}},
            {"id": "OK-0002", "tur": "tempo", "durum": "aktif", "deger": {"elle": {"gonderim_arasi_sn": [1, 2]}}}]})
        E = fy.esik_yukle(self.kok)
        self.assertEqual(E["flow_gorsel_gunluk_tavan"], 20)
        self.assertEqual(fy.tempo("gece", self.kok, E, T0)["gonderim_arasi_sn"], [20, 40])
        self.assertEqual(fy.tempo("elle", self.kok, E, T0)["gonderim_arasi_sn"], [6, 15])
        # MEMMET_AYAR benzeri ek değer de yalnız yavaşlatır
        t = fy.tempo("elle", self.kok, E, T0, ek={"gonderim_arasi_sn": [3, 30], "ayni_anda": 5})
        self.assertEqual((t["gonderim_arasi_sn"], t["ayni_anda"]), ([6, 30], 2))

    def test_bozuk_son_satir_atlanir(self):
        self.gonder("video", "elle", T0)
        with open(fy.yuk_yolu(self.kok), "a", encoding="utf-8") as f: f.write('{"zaman": "yar')
        self.assertEqual(len(fy.yuk_oku(self.kok)), 1)


class Tavanlar(Taban):
    def test_gunluk_gorsel_tavani(self):
        t = T0
        for i in range(20): self.gonder("gorsel", "elle", t); t += 20
        d = self.izin("gorsel", "elle", t + 60)
        self.assertEqual(d["kod"], fy.BEKLE)
        ertesi = time.mktime((2026, 10, 22, 0, 0, 0, 0, 0, -1))
        self.assertEqual(d["bekle_bitis"], ertesi)
        self.assertTrue(self.izin("gorsel", "elle", ertesi + 1)["izinli"])
        self.assertEqual(fy.gunluk_sayim(self.kok, t)["gorsel"], 20)

    def test_gorselden_sonra_video_12_saat(self):
        self.gonder("gorsel", "elle", T0)
        d = self.izin("video", "elle", T0 + 11 * SA)
        self.assertEqual(d["kod"], fy.BEKLE); self.assertEqual(d["bekle_bitis"], T0 + 12 * SA)
        self.assertTrue(self.izin("video", "elle", T0 + 12 * SA + 1)["izinli"])

    def test_tavan_butun_filmler_icin_ortak(self):
        for i in range(10): fy.gonderim_kaydet("gorsel", "elle", film="A", kok=self.kok, E=self.E, simdi=T0 + i * 20, rnd=self.rnd)
        for i in range(10): fy.gonderim_kaydet("gorsel", "elle", film="B", kok=self.kok, E=self.E, simdi=T0 + 300 + i * 20, rnd=self.rnd)
        self.assertEqual(self.izin("gorsel", "elle", T0 + 2 * SA)["kod"], fy.BEKLE)


class Kilit(Taban):
    def memmet_uyari(self):
        """PR-0 Memmet'in kendi kilit_yaz'ı (gerçek saatle); döndürür: yazıldığı an."""
        t = time.time()
        with self.memmet_hesap(): memmet.kilit_yaz("F_TEST", "Olağan dışı etkinlik")
        return t

    def test_memmet_kilidi_okunur(self):
        t = self.memmet_uyari()
        k = fy.kilit_durumu(self.kok, self.E, t + 10 * DK)
        self.assertTrue(k["kilitli"]); self.assertFalse(k["kalkabilir"])
        self.assertAlmostEqual(k["en_erken"], t + 30 * DK, delta=60)   # dakikaya yukarı yuvarlanır (yalnız uzar)
        self.assertGreaterEqual(k["en_erken"], t + 30 * DK - 1)
        self.assertEqual(self.izin("video", "elle", t + 10 * DK)["kod"], fy.KILITLI)
        self.assertEqual(self.izin("gorsel", "elle", t + 40 * DK)["kod"], fy.KILITLI)   # süre geçse de kilit kendiliğinden kalkmaz

    def test_haftada_ikinci_uyari_7_gun(self):
        fy.uyari_kaydet("F_TEST", "uyarı 1", kok=self.kok, E=self.E, simdi=T0 - 2 * GUN)        # pazartesi
        r = fy.uyari_gecti(True, kok=self.kok, E=self.E, simdi=T0 - 2 * GUN + 40 * DK)
        self.assertEqual(r["sonuc"], "kaldirildi")
        k = fy.uyari_kaydet("F_TEST", "uyarı 2", kok=self.kok, E=self.E, simdi=T0)              # aynı hafta çarşamba
        self.assertEqual(k["haftanin_uyarisi"], 2)
        self.assertAlmostEqual(k["en_erken"], T0 + 7 * GUN, delta=1)
        r = fy.uyari_gecti(True, kok=self.kok, E=self.E, simdi=T0 + 2 * SA)
        self.assertEqual(r["sonuc"], "red")
        self.assertTrue(fy.kilit_durumu(self.kok, self.E, T0 + 6 * GUN)["kilitli"])

    def test_farkli_haftada_uyari_30_dk(self):
        fy.uyari_kaydet("F_TEST", "uyarı 1", kok=self.kok, E=self.E, simdi=T0 - 7 * GUN)
        fy.uyari_gecti(True, kok=self.kok, E=self.E, simdi=T0 - 7 * GUN + 31 * DK)
        k = fy.uyari_kaydet("F_TEST", "uyarı 2", kok=self.kok, E=self.E, simdi=T0)
        self.assertEqual(k["haftanin_uyarisi"], 1); self.assertAlmostEqual(k["en_erken"], T0 + 30 * DK, delta=1)

    def test_memmet_ikinci_uyari_kilidi_uzar(self):
        self.memmet_uyari()
        t = self.memmet_uyari()        # kilit varken ikinci uyarı: Memmet kilidi değiştirmez, flow_yuk geçmişten 7 gün sayar
        k = fy.kilit_durumu(self.kok, self.E, t)
        self.assertEqual(k["haftanin_uyarisi"], 2); self.assertAlmostEqual(k["en_erken"], t + 7 * GUN, delta=60)
        self.assertGreaterEqual(k["en_erken"], t + 7 * GUN - 1)


class UyariGecti(Taban):
    def setUp(self):
        super().setUp()
        fy.hesap_gozlem(eposta=EPOSTA_A, kok=self.kok, E=self.E, simdi=T0 - SA)
        fy.uyari_kaydet("F_TEST", "Olağan dışı etkinlik", plan=12, kok=self.kok, E=self.E, simdi=T0)

    def gecti(self, t, **k): return fy.uyari_gecti(k.pop("elle", True), kok=self.kok, E=self.E, simdi=t, **k)

    def test_30_dk_dolmadan_ret(self):
        r = self.gecti(T0 + 29 * DK)
        self.assertEqual(r["sonuc"], "red"); self.assertTrue(os.path.exists(fy.kilit_yolu(self.kok)))

    def test_elle_video_yoksa_ret(self):
        self.assertEqual(self.gecti(T0 + 40 * DK, elle=False)["sonuc"], "red")
        self.assertEqual(self.gecti(T0 + 40 * DK, elle="evet")["sonuc"], "red")      # yalnız True kabul

    def test_deneme_erken_ya_da_baska_gun_ret(self):
        self.assertEqual(self.gecti(T0 + 40 * DK, deneme_zamani=T0 + 10 * DK)["sonuc"], "red")
        self.assertEqual(self.gecti(T0 + GUN, deneme_zamani=T0 + 40 * DK)["sonuc"], "red")
        self.assertEqual(self.gecti(T0 + 40 * DK, deneme_zamani=T0 + 35 * DK)["sonuc"], "kaldirildi")

    def test_baska_hesapta_kalkmaz(self):
        self.assertEqual(self.gecti(T0 + 40 * DK, eposta=EPOSTA_B)["sonuc"], "red")
        fy.hesap_gozlem(eposta=EPOSTA_B, kok=self.kok, E=self.E, simdi=T0 + 35 * DK)
        r = self.gecti(T0 + 40 * DK)
        self.assertEqual(r["sonuc"], "red"); self.assertTrue(any("asıl" in n for n in r["nedenler"]))
        fy.hesap_gozlem(eposta=EPOSTA_A, kok=self.kok, E=self.E, simdi=T0 + 45 * DK)
        self.assertEqual(self.gecti(T0 + 50 * DK)["sonuc"], "kaldirildi")

    def test_basari_kurallari(self):
        r = self.gecti(T0 + 40 * DK)
        self.assertEqual(r["sonuc"], "kaldirildi")
        self.assertFalse(os.path.exists(fy.kilit_yolu(self.kok)))
        arsiv = os.listdir(os.path.join(self.kok, "_ESKI")); self.assertEqual(len(arsiv), 1)      # silinmedi, taşındı
        K = ortak.json_oku(os.path.join(self.kok, "_ESKI", arsiv[0]))
        self.assertTrue(K["kaldirma"]["elle_1_video_basarili"]); self.assertEqual(K["kaldirma"]["gecerli_gun"], "2026-10-21")
        # o günün kalanında tempo ×1,5
        self.assertEqual(fy.tempo("elle", self.kok, self.E, T0 + 2 * SA)["gonderim_arasi_sn"], [9, 22.5])
        self.assertTrue(self.izin("video", "elle", T0 + 2 * SA)["izinli"])
        # o gün ve ertesi gün ilk blok elle bitene kadar gece kapalı
        self.assertEqual(self.izin("video", "gece", T0 + 2 * SA)["kod"], fy.KIP_ELLE)
        yarin = T0 + GUN
        self.assertEqual(fy.tempo("elle", self.kok, self.E, yarin)["carpan"], 1.0)
        fy.blok_bitti("elle", self.kok, self.E, T0 + 3 * SA, self.rnd)                    # aynı gün biten elle blok sayılmaz
        self.assertEqual(self.izin("video", "gece", yarin)["kod"], fy.KIP_ELLE)
        self.assertTrue(self.izin("video", "elle", yarin)["izinli"])
        fy.blok_bitti("elle", self.kok, self.E, yarin + SA, self.rnd)
        self.assertTrue(self.izin("video", "gece", yarin + 2 * SA)["izinli"])

    def test_kilit_yoksa(self):
        self.gecti(T0 + 40 * DK)
        self.assertEqual(self.gecti(T0 + 50 * DK)["sonuc"], "kilit_yok")


class Hesap(Taban):
    def test_uyaridan_sonra_hesap_degisimi_kilitler(self):
        fy.hesap_gozlem(eposta=EPOSTA_A, kok=self.kok, E=self.E, simdi=T0 - GUN)
        fy.uyari_kaydet("F", "uyarı", kok=self.kok, E=self.E, simdi=T0)
        fy.uyari_gecti(True, kok=self.kok, E=self.E, simdi=T0 + 40 * DK)
        s = fy.hesap_gozlem(eposta=EPOSTA_B, kok=self.kok, E=self.E, simdi=T0 + 5 * GUN)
        self.assertTrue(s["degisti"]); self.assertTrue(s["kilit"])
        k = fy.kilit_durumu(self.kok, self.E, T0 + 5 * GUN)
        self.assertEqual(k["neden"], "hesap_degisti"); self.assertEqual(k["hesap"], fy.hesap_kimligi(EPOSTA_A))
        self.assertEqual(self.izin("video", "elle", T0 + 5 * GUN + SA)["kod"], fy.KILITLI)
        self.assertEqual(fy.uyari_gecti(True, kok=self.kok, E=self.E, simdi=T0 + 5 * GUN + SA)["sonuc"], "red")
        fy.hesap_gozlem(eposta=EPOSTA_A, kok=self.kok, E=self.E, simdi=T0 + 5 * GUN + 2 * SA)
        self.assertEqual(fy.uyari_gecti(True, kok=self.kok, E=self.E, simdi=T0 + 5 * GUN + 3 * SA)["sonuc"], "kaldirildi")

    def test_uyari_yokken_yalniz_kayit(self):
        fy.hesap_gozlem(eposta=EPOSTA_A, kok=self.kok, E=self.E, simdi=T0)
        s = fy.hesap_gozlem(eposta=EPOSTA_B, kok=self.kok, E=self.E, simdi=T0 + SA)
        self.assertTrue(s["degisti"]); self.assertFalse(s["kilit"]); self.assertIsNone(fy.kilit_oku(self.kok))

    def test_14_gunden_sonra_kilit_yok(self):
        fy.hesap_gozlem(eposta=EPOSTA_A, kok=self.kok, E=self.E, simdi=T0 - 30 * GUN)
        fy.uyari_kaydet("F", "uyarı", kok=self.kok, E=self.E, simdi=T0 - 20 * GUN)
        fy.uyari_gecti(True, kok=self.kok, E=self.E, simdi=T0 - 20 * GUN + SA)
        self.assertFalse(fy.hesap_gozlem(eposta=EPOSTA_B, kok=self.kok, E=self.E, simdi=T0)["kilit"])

    def test_eposta_dosyalara_yazilmaz(self):
        fy.hesap_gozlem(eposta=EPOSTA_A, kok=self.kok, E=self.E, simdi=T0)
        fy.gonderim_kaydet("video", "elle", kok=self.kok, E=self.E, simdi=T0, rnd=self.rnd)
        fy.uyari_kaydet("F", "uyarı", kok=self.kok, E=self.E, simdi=T0 + 60)
        fy.hesap_gozlem(eposta=EPOSTA_B, kok=self.kok, E=self.E, simdi=T0 + 120)
        for kok, _, adlar in os.walk(self.kok):
            for a in adlar:
                with open(os.path.join(kok, a), encoding="utf-8") as f: metin = f.read()
                self.assertNotIn("example.com", metin, a)
        with self.assertRaises(fy.YukHatasi): fy.hesap_gozlem(kimlik="acik@metin.com", kok=self.kok, E=self.E, simdi=T0)


class Komut(Taban):
    def calistir(self, *a):
        y = dict(ortak.yollar(), hesap=self.kok)
        out = io.StringIO()
        with mock.patch.object(ortak, "yollar", return_value=y), contextlib.redirect_stdout(out):
            kod = fy.main(list(a))
        return kod, out.getvalue()

    def test_izin_ve_uyari_gecti_cikis_kodlari(self):
        self.assertEqual(self.calistir("--izin", "video")[0], 0)
        fy.uyari_kaydet("F", "uyarı", kok=self.kok, E=self.E)
        kod, metin = self.calistir("--izin", "video"); self.assertEqual(kod, 7); self.assertIn("UYARI_GECTI", metin)
        with mock.patch("sys.stdin", io.StringIO("")):
            self.assertEqual(self.calistir("--uyari-gecti")[0], 7)                      # soru cevapsız → ret
            self.assertEqual(self.calistir("--uyari-gecti", "--elle-video-basarili")[0], 7)   # 30 dk dolmadı
        self.assertEqual(self.calistir("--bilinmeyen")[0], 4)
        kod, metin = self.calistir(); self.assertEqual(kod, 0); self.assertIn("KİLİTLİ", metin)
        kod, metin = self.calistir("--json"); self.assertTrue(json.loads(metin)["kilit"]["kilitli"])


if __name__ == "__main__":
    unittest.main()
