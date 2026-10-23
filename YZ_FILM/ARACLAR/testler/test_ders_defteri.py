"""ders_defteri.py testleri (TASARIM D-33, §5.3): ham kayıt şeması, gizli bilgi maskesi, öğrenilen kurallar yalnız sıkılaştırır,
aktif güvenlik kuralı geri alınamaz; KURALLAR_OGRENILEN.json esikler.py tarafından okunur."""
import os, sys, json, shutil, tempfile, unittest, io, contextlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import ortak, esikler, ders_defteri as dd

E = esikler.yukle()
TAVAN = {"id": "OK-0014", "tur": "flow_tavan", "deger": {"gorsel_gunluk": 15}, "durum": "aktif", "yanlis_alarm_orani": None}


class Taban(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(prefix="ders_"); self.addCleanup(shutil.rmtree, self.d, True)
        self.bilgi = os.path.join(self.d, "BILGI"); os.makedirs(self.bilgi)
        self.yol = os.path.join(self.bilgi, "KURALLAR_OGRENILEN.json")


class HamKayit(Taban):
    def test_sema_ve_dosya_adi(self):
        z = datetime.datetime(2026, 11, 3, 10, 15, 0).astimezone()
        p = dd.kaydet("kapi_hatasi", kaynak="kapi", belirti="fener istemde sol elde, iki adayda da sağ elde", film="EMBERFALL_F2",
                      seri="EMBERFALL", asama="A11", kapi="G1", madde="el_nesne", plan=214, kategori="ters_el", rol_etiketi="goruntu",
                      baglam={"plan_tipi": "eylem"}, kanit=["_RAPOR/G1_P2_B1.json#214"], eylem="CORRECTION: lantern in her LEFT hand",
                      maliyet={"flow_kredi": 0, "gorsel": 2}, zaman=z, bilgi=self.bilgi)
        self.assertEqual(os.path.dirname(p), os.path.join(self.bilgi, "DERSLER", "ham"))
        self.assertEqual(os.path.basename(p), "20261103T101500_EMBERFALL_F2_kapi_hatasi.json")
        r = ortak.json_oku(p)
        self.assertEqual((r["_surum"], r["id"], r["olay"], r["plan"], r["sonuc"]), (1, "D-20261103-0001", "kapi_hatasi", 214, None))
        self.assertIn(r["ortam"], ("yerel", "bulut")); self.assertTrue(r["zaman"].startswith("2026-11-03T10:15:00"))
        p2 = dd.kaydet("kapi_hatasi", kaynak="kapi", belirti="ikinci", film="EMBERFALL_F2", zaman=z, bilgi=self.bilgi)
        self.assertNotEqual(p, p2); self.assertEqual(ortak.json_oku(p2)["id"], "D-20261103-0002")    # üzerine yazılmaz

    def test_gecersiz_alanlar(self):
        for k in ({"olay": "uydurma"}, {"kaynak": "sezgi"}, {"belirti": " "}, {"sonuc": "belki"}):
            a = dict(olay="arac_hatasi", kaynak="ajan", belirti="x"); a.update(k)
            with self.assertRaises(ValueError): dd.kaydet(bilgi=self.bilgi, **a)

    def test_gizli_bilgi_maskelenir(self):
        p = dd.kaydet("arac_hatasi", "ajan", "hesap ali@example.com ile açıldı, anahtar sk-abcdefghijklmnopqrstuv",
                      olcum={"not": "AIzaSyA1234567890abcdefghijk"}, bilgi=self.bilgi)
        with open(p, encoding="utf-8") as f: metin = f.read()
        for x in ("ali@example.com", "sk-abcdef", "AIzaSy"): self.assertNotIn(x, metin)

    def test_sonuc_sonradan(self):
        p = dd.kaydet("yeniden_cekim", "kapi", "x", bilgi=self.bilgi)
        i = ortak.json_oku(p)["id"]
        self.assertEqual(dd.sonuc_yaz(i, "duzeldi", bilgi=self.bilgi), p)
        self.assertEqual(ortak.json_oku(p)["sonuc"], "duzeldi")
        with self.assertRaises(KeyError): dd.sonuc_yaz("D-19990101-0001", "duzeldi", bilgi=self.bilgi)


class Korkuluk(Taban):
    def h(self, **k): return dd.korkuluk(dict({"id": "OK-0001", "durum": "aktif"}, **k), E)

    def test_flow_tavan_yalniz_duser(self):
        self.assertEqual(dd.korkuluk(TAVAN, E), [])
        self.assertTrue(self.h(tur="flow_tavan", deger={"gorsel_gunluk": 25}))
        self.assertTrue(self.h(tur="flow_tavan", deger={"gorsel_gunluk": 20}))                       # aynı: sıkılaştırmıyor
        self.assertTrue(self.h(tur="flow_tavan", deger={"gorsel_sonrasi_video_saat": 6}))
        self.assertEqual(self.h(tur="flow_tavan", deger={"gorsel_sonrasi_video_saat": 18}), [])
        self.assertTrue(self.h(tur="flow_tavan", deger={"stop_ardisik_max": 4}))                     # güvenlik sınırı değil
        self.assertTrue(self.h(tur="flow_tavan", deger=15))

    def test_tempo_yalniz_yavaslar(self):
        self.assertEqual(self.h(tur="tempo", deger={"gece": {"gonderim_arasi_sn": [15, 40], "ayni_anda": 2}}), [])
        self.assertTrue(self.h(tur="tempo", deger={"gece": {"gonderim_arasi_sn": [6, 20]}}))
        self.assertTrue(self.h(tur="tempo", deger={"elle": {"ayni_anda": 3}}))
        self.assertTrue(self.h(tur="tempo", deger={"elle": {"mola_kac_gonderimde": 0}}))             # mola kapatılamaz
        self.assertTrue(self.h(tur="tempo", deger={"gece": {"mola_kac_gonderimde": 4}}))             # kapalı olan açılmaz (değişmez)

    def test_esik_sikilasir_ve_yanlis_alarm(self):
        self.assertEqual(self.h(tur="esik", deger={"stop_ardisik_max": 6}, yanlis_alarm_orani=0.2), [])
        self.assertTrue(self.h(tur="esik", deger={"stop_ardisik_max": 6}))                            # ölçülmedi
        self.assertTrue(self.h(tur="esik", deger={"stop_ardisik_max": 6}, yanlis_alarm_orani=0.4))
        self.assertEqual(dd.korkuluk({"id": "OK-0002", "durum": "deneme", "tur": "esik", "deger": {"stop_ardisik_max": 6}}, E), [])
        self.assertTrue(self.h(tur="esik", deger={"stop_ardisik_max": 12}, yanlis_alarm_orani=0.1))   # gevşetme
        self.assertTrue(self.h(tur="esik", deger={"flow_model": "baska"}, yanlis_alarm_orani=0.1))     # sabit
        self.assertTrue(self.h(tur="esik", deger={"yok_boyle_anahtar": 1}, yanlis_alarm_orani=0.1))

    def test_sface_tabani(self):
        p = os.path.join(self.d, "s.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"sface_hata": {"deger": 0.30, "aciklama": "t", "kaynak": "tahmin", "etiket": "T", "yon": "taban"}}, f)
        Es = esikler.yukle([p])
        self.assertTrue(any("0.363" in x for x in dd.korkuluk({"id": "OK-0003", "tur": "esik", "durum": "deneme",
                                                               "deger": {"sface_hata": 0.33}}, Es)))
        self.assertEqual(dd.korkuluk({"id": "OK-0003", "tur": "esik", "durum": "deneme", "deger": {"sface_hata": 0.40}}, Es), [])

    def test_guvenlik_konulari_ve_gizli_bilgi(self):
        self.assertTrue(self.h(tur="yol_kurali", deger="Flow uyarısında sayfayı yenile ve devam et"))
        self.assertTrue(self.h(tur="saglayici_notu", deger="kısıtlanınca başka hesap kullan"))
        self.assertTrue(self.h(tur="plan_kurali", deger="onaysız yükleme yapılabilir"))
        self.assertEqual(self.h(tur="istem_eki", deger="the empty hand rests at her side", kapsam={"plan_tipi": "eylem"}), [])
        self.assertEqual(self.h(tur="filtre_kelimesi", deger="cradle", seviye="HATA"), [])
        self.assertTrue(self.h(tur="istem_eki", deger="contact me at ali@example.com"))
        self.assertTrue(self.h(tur="uydurma_tur", deger="x"))
        self.assertTrue(dd.korkuluk({"id": "kotu", "tur": "istem_eki", "durum": "aktif", "deger": "x"}, E))


class Ogrenilen(Taban):
    def test_yaz_ve_esikler_okur(self):
        dd.ogrenilen_yaz({"kurallar": [dict(TAVAN), {"id": "OK-0003", "tur": "filtre_kelimesi", "deger": "cradle", "durum": "aktif"}]},
                         self.yol, E, uretim={"asama": "A18"})
        v = ortak.json_oku(self.yol)
        self.assertEqual(v["_surum"], 3); self.assertEqual(v["_uretim"]["sonuc"], "GEC"); self.assertEqual(v["_uretim"]["asama"], "A18")
        self.assertEqual(list(v)[:2], ["_surum", "_uretim"])
        self.assertTrue(all(k["korkuluk"] == "gecti" for k in v["kurallar"]))
        self.assertEqual(esikler.yukle(ogrenilen=self.yol)["flow_gorsel_gunluk_tavan"], 15)

    def test_korkuluktan_gecmeyen_yazilmaz(self):
        with self.assertRaises(dd.KorkulukHatasi): dd.ogrenilen_yaz({"kurallar": [dict(TAVAN, deger={"gorsel_gunluk": 30})]}, self.yol, E)
        self.assertFalse(os.path.exists(self.yol))
        with self.assertRaises(dd.KorkulukHatasi): dd.ogrenilen_yaz({"kurallar": [dict(TAVAN), dict(TAVAN)]}, self.yol, E)   # çift id

    def test_aktif_guvenlik_kurali_geri_alinamaz(self):
        dd.ogrenilen_yaz({"kurallar": [dict(TAVAN)]}, self.yol, E)
        once = ortak.json_oku(self.yol)
        for yeni in ([], [dict(TAVAN, durum="pasif")], [dict(TAVAN, durum="deneme")], [dict(TAVAN, deger={"gorsel_gunluk": 18})]):
            with self.assertRaises(dd.KorkulukHatasi): dd.ogrenilen_yaz({"kurallar": yeni}, self.yol, E)
            self.assertEqual(ortak.json_oku(self.yol), once)
        dd.ogrenilen_yaz({"kurallar": [dict(TAVAN, deger={"gorsel_gunluk": 12})]}, self.yol, E)          # daha sıkı: olur
        self.assertEqual(esikler.yukle(ogrenilen=self.yol)["flow_gorsel_gunluk_tavan"], 12)

    def test_esik_kurali_emekli_olabilir(self):
        k = {"id": "OK-0005", "tur": "esik", "deger": {"stop_ardisik_max": 6}, "durum": "aktif", "yanlis_alarm_orani": 0.1}
        dd.ogrenilen_yaz({"kurallar": [k]}, self.yol, E)
        dd.ogrenilen_yaz({"kurallar": [dict(k, durum="pasif")]}, self.yol, E)                         # gevsetilemez değil

    def test_kural_ekle(self):
        a = dd.kural_ekle({"tur": "flow_tavan", "deger": {"gorsel_gunluk": 15}, "durum": "aktif"}, self.yol, E)
        b = dd.kural_ekle({"tur": "istem_eki", "deger": "x", "durum": "aday"}, self.yol, E)
        self.assertEqual((a["id"], a["onceki"], a["yon"], b["id"]), ("OK-0001", 20, "sikilastir", "OK-0002"))
        with self.assertRaises(dd.KorkulukHatasi):
            dd.kural_ekle({"tur": "tempo", "deger": {"elle": {"gonderim_arasi_sn": [1, 2]}}, "durum": "aktif"}, self.yol, E)
        self.assertEqual(len(ortak.json_oku(self.yol)["kurallar"]), 2)

    def test_komut_denetle(self):
        dd.ogrenilen_yaz({"kurallar": [dict(TAVAN)]}, self.yol, E)
        out = io.StringIO()
        with contextlib.redirect_stdout(out): self.assertEqual(dd.main(["--denetle", self.yol]), 0)
        v = ortak.json_oku(self.yol); v["kurallar"].append(dict(TAVAN, id="OK-0099", deger={"gorsel_gunluk": 40}))
        ortak.atomik_yaz(self.yol, v)
        with contextlib.redirect_stdout(out): self.assertEqual(dd.main(["--denetle", self.yol]), 1)
        with contextlib.redirect_stdout(out): self.assertEqual(dd.main(["--yanlis"]), 4)


if __name__ == "__main__":
    unittest.main()
