"""G1 karar testleri (TASARIM §6.10 test_g1_karar, D-16, [GS2] §4.6.3): aynalanmış kare → kadraj sırası HATA; fazla yüz → HATA; tek kaynaklı
ters el → BAYRAK → hakem; iki aday da HATA → CORRECTION kuyruğu; ölçüm modeli yok → ÖLÇÜLEMEDİ (asla GEÇ); hakem iki kaynaklı HATA'ya GEÇ
yazdı → reddedilir; G1'siz kare videoya gitmez; SHA1 uyuşmazlığı → gitmez. Ayrıca: seçim sırası, kör sol/sağ çevirisi, sızıntı, ÖLÇÜLEMEDİ
alanının GEÇ sayılmaması, kör pakette yalnız anonim adlar, _ADAYLAR'dan SIRALI_GORSEL'e yalnız GEÇ kare."""
import os, sys, json, glob, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401
import _gorsel_fikstur as F
import ortak, kor, kuyruk, kapi
import kare_denetim as kd


def g1(kok, tur=1): return ortak.json_oku(os.path.join(kok, "_RAPOR", f"G1_FILM_t{tur}.json"))


def alanlar(kok, no, tur=1):
    k = ortak.json_oku(os.path.join(kok, "_RAPOR", "G1", f"KARAR_t{tur}.json"))
    return {a["aday"]: a for a in k["planlar"][str(no)]}


class G1Karar(unittest.TestCase):
    def test_temiz_hepsi_gecer_ve_yalniz_gec_kare_yerlesir(self):
        kok = F.g1_hazirla()
        self.assertFalse(glob.glob(os.path.join(kok, "SIRALI_GORSEL", "*.jpg")), "içe alma SIRALI_GORSEL/NNN.jpg'e yazmamalı")
        kod, r = kd.karar(kok, 1)
        self.assertEqual(kod, 0); self.assertEqual(r["sonuc"], "GEC"); self.assertEqual(kapi.dogrula(r), [])
        P = F.planlar(kok)
        for no in (101, 102, 103):
            self.assertEqual(P[no]["denetim"]["G1"]["sonuc"], "GEC")
            self.assertTrue(kd.video_hazir(kok, no)[0])
            self.assertEqual(P[no]["uretim"]["gorsel"]["sha1"], kd.sha1(os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % no)))
        self.assertTrue(os.path.isfile(os.path.join(kok, "_RAPOR", "G1_P1_B1.json")))
        self.assertIn("101", ortak.json_oku(os.path.join(kok, "DUNYA_DEFTERI.json"))["dondurulmus"])

    def test_aynalanmis_kare_kadraj_sirasi_hata(self):
        kok = F.g1_hazirla({102: ["ayna"]})
        kod, r = kd.karar(kok, 1)
        a = alanlar(kok, 102)["a"]
        self.assertEqual(a["karar"], "HATA")
        self.assertTrue(any(x["alan"] == "kadraj_sirasi" and x["seviye"] == "HATA" for x in a["alanlar"]))
        self.assertEqual(F.planlar(kok)[102]["denetim"]["G1"]["sonuc"], "HATA")
        self.assertFalse(os.path.isfile(os.path.join(kok, "SIRALI_GORSEL", "102.jpg")))
        self.assertIn(r["sonuc"], ("KISMI", "HATA"))
        # ayna_yasak = false: 0 kredi küçük düzeltme (ayna) bir kez uygulanır → yeni aday, işaret dosyası
        self.assertTrue(glob.glob(os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "102_*1.jpg")))
        self.assertEqual(ortak.json_oku(os.path.join(kok, "_RAPOR", "ISARET", "102.json"))["uygulanan"][0]["islem"], "ayna")

    def test_fazla_yuz_hata_ve_correction_kuyrugu(self):
        kok = F.g1_hazirla({101: ["fazla_kisi"]})
        kd.karar(kok, 1)
        a = alanlar(kok, 101)["a"]
        f = [x for x in a["alanlar"] if x["alan"] == "fazla_kisi"]
        self.assertEqual(f[0]["seviye"], "HATA"); self.assertEqual(f[0]["kaynak"], "iki")
        m = [x for x in kuyruk.acik_maddeler(kok) if x["plan"] == 101]
        self.assertEqual(len(m), 1)
        self.assertEqual((m[0]["tur"], m[0]["kaynak_kapi"], m[0]["kok_neden"]), ("gorsel", "G1", "fazla_kisi"))
        self.assertTrue(m[0]["duzeltme"].startswith("CORRECTION: exactly 1 person in frame: Mara."))
        self.assertTrue(m[0]["sifir_kredi"]["denendi"])

    def test_tek_kaynakli_ters_el_bayrak_ve_hakem(self):
        kok = F.g1_hazirla({101: ["ters_el"]})
        kd.karar(kok, 1)
        a = alanlar(kok, 101)["a"]
        ne = [x for x in a["alanlar"] if x["alan"] == "nesne_el"]
        self.assertEqual((ne[0]["seviye"], ne[0]["kaynak"]), ("BAYRAK", "tek"))
        self.assertIn(101, g1(kok)["hakem_bekleyen"])
        self.assertFalse(kd.video_hazir(kok, 101)[0])
        hp = os.path.join(kok, "HAKEM.json")
        ortak.atomik_yaz(hp, [{"plan": 101, "alan": "nesne_el", "kisi": "mara", "karar": "GEC", "gerekce": "fener sağ elde; kör yanıldı"}])
        kod, r = kd.hakem(kok, 1, hp)
        self.assertEqual(F.planlar(kok)[101]["denetim"]["G1"]["sonuc"], "GEC")
        self.assertTrue(kd.video_hazir(kok, 101)[0])

    def test_hakem_iki_kaynakli_hatayi_gece_cevirmez(self):
        kok = F.g1_hazirla({101: ["ters_el_iki"]})
        kd.karar(kok, 1)
        self.assertEqual([x for x in alanlar(kok, 101)["a"]["alanlar"] if x["alan"] == "nesne_el"][0]["kaynak"], "iki")
        hp = os.path.join(kok, "HAKEM.json")
        ortak.atomik_yaz(hp, [{"plan": 101, "aday": "a", "alan": "nesne_el", "kisi": "mara", "karar": "GEC", "gerekce": "bence doğru"},
                              {"plan": 101, "aday": "b", "alan": "nesne_el", "kisi": "mara", "karar": "GEC", "gerekce": "bence doğru"}])
        kd.hakem(kok, 1, hp)
        h = ortak.json_oku(os.path.join(kok, "_RAPOR", "G1", "HAKEM_t1.json"))
        self.assertEqual(len(h["reddedilen"]), 2)
        self.assertEqual(F.planlar(kok)[101]["denetim"]["G1"]["sonuc"], "HATA")
        self.assertFalse(kd.video_hazir(kok, 101)[0])

    def test_gerekcesiz_hakem_karari_reddedilir(self):
        kok = F.g1_hazirla({101: ["ters_el"]})
        kd.karar(kok, 1)
        hp = os.path.join(kok, "HAKEM.json")
        ortak.atomik_yaz(hp, [{"plan": 101, "alan": "nesne_el", "kisi": "mara", "karar": "GEC", "gerekce": " "}])
        kd.hakem(kok, 1, hp)
        self.assertNotEqual(F.planlar(kok)[101]["denetim"]["G1"]["sonuc"], "GEC")

    def test_olcum_modeli_yok_olculemedi_asla_gec(self):
        kok = F.g1_hazirla({103: ["olculemedi"]})
        kod, r = kd.karar(kok, 1)
        a = alanlar(kok, 103)["a"]
        self.assertEqual(a["karar"], "BAYRAK")
        self.assertTrue(any(x["seviye"] == "OLCULEMEDI" for x in a["alanlar"]))
        self.assertNotEqual(F.planlar(kok)[103]["denetim"]["G1"]["sonuc"], "GEC")
        self.assertFalse(os.path.isfile(os.path.join(kok, "SIRALI_GORSEL", "103.jpg")))
        self.assertGreater(r["ozet"]["olculemedi"], 0)
        self.assertNotEqual(r["sonuc"], "GEC")

    def test_kor_gozlem_yoksa_olculemedi(self):
        kok = F.g1_hazirla()
        for p in glob.glob(os.path.join(kok, "_RAPOR", "G1", "gozlem_t1_*.json")): os.replace(p, p + ".yok")
        kod, r = kd.karar(kok, 1)
        self.assertEqual(r["sonuc"], "BAYRAK")
        self.assertFalse(glob.glob(os.path.join(kok, "SIRALI_GORSEL", "*.jpg")))

    def test_iki_aday_secim_sirasi(self):
        kok = F.g1_hazirla({101: {"a": ["fazla_kisi"], "b": []}, 103: {"a": ["kimlik_bayrak"], "b": []}})
        kd.karar(kok, 1)
        P = F.planlar(kok)
        self.assertEqual((P[101]["denetim"]["G1"]["sonuc"], P[101]["denetim"]["G1"]["aday"]), ("GEC", "b"))
        self.assertEqual(P[103]["denetim"]["G1"]["aday"], "b")
        self.assertTrue(os.path.isfile(os.path.join(kok, "SIRALI_GORSEL", "ALTERNATIFLER", "101_a.jpg")))
        self.assertTrue(os.path.isfile(os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "101_a.jpg")), "aday silinmez")

    def test_kimlik_hatasi_yer_tutucu_ve_onizleme(self):
        kok = F.g1_hazirla({101: ["kimlik"], 102: ["kimlik"], 103: ["yazi"]})
        kod, r = kd.karar(kok, 1)
        self.assertEqual(sorted(r["yer_tutucu"]), [101, 102])
        self.assertTrue(any(h["madde"] == "yer_tutucu_orani" for h in r["hatalar"]))
        self.assertTrue(os.path.isfile(os.path.join(kok, "SIRALI_GORSEL", "_ONIZLEME", "103.jpg")))
        self.assertEqual(r["sonuc"], "HATA")

    def test_video_kapisi_g1siz_ve_sha1(self):
        kok = F.g1_hazirla()
        self.assertFalse(kd.video_hazir(kok, 101)[0])
        kd.karar(kok, 1)
        self.assertTrue(kd.video_hazir(kok, 101)[0])
        with open(os.path.join(kok, "SIRALI_GORSEL", "101.jpg"), "ab") as f: f.write(b"\0")
        ok, neden = kd.video_hazir(kok, 101)
        self.assertFalse(ok); self.assertIn("SHA1", neden)

    def test_kor_paket_anonim_ve_sizintisiz(self):
        kok = F.g1_hazirla()
        kl = os.path.join(kok, "_KOR_PAKET", "g1_t1")
        self.assertEqual(kor.sizinti(kl, ["Mara", "Voss", "mara", "voss", "lantern in her"]), [])
        for d in glob.glob(os.path.join(kl, "*", "*.jpg")): self.assertRegex(os.path.basename(d), r"^g\d{2}\.jpg$")
        s = ortak.json_oku(glob.glob(os.path.join(kl, "1", "SORULAR.json"))[0])
        q = {x["k"]: x for x in s["hedefli"][s["gorseller"][0]]}
        self.assertIn("q_kisib", q); self.assertEqual(q["q_kisib"]["tekrar_of"], "q_kisi")
        self.assertEqual(sorted(q["q_kisi"]["secenek"]), sorted(q["q_kisib"]["secenek"]))
        self.assertFalse(any(k.startswith("_") for x in q.values() for k in x), "beklenen değer pakete sızmamalı")

    def test_sol_sag_cevirisi(self):
        self.assertEqual(kor.anatomik_el("sol", "on"), "sag")
        self.assertEqual(kor.anatomik_el("sol", "3/4"), "sag")
        self.assertEqual(kor.anatomik_el("sag", "3/4"), "sol")
        self.assertEqual(kor.anatomik_el("sol", "sirt"), "sol")
        self.assertIsNone(kor.anatomik_el("sol", "profil"))
        self.assertEqual(kor.goruntu_tarafi("sag", "on"), "sol")

    def test_karar_kurali_iki_kaynak_tek_kaynak(self):
        b = {"gorunur_yuz": [], "insan": ["m"], "kadrajdakiler": ["m"], "kadraj_sirasi": [], "kadraj_konumu": {}, "bakis": {},
             "yaw_isareti": 1, "agiz_kapali": [], "konusan": [], "yaratik_ids": [], "kalibrasyon": {}, "plan_tipi": "eylem"}
        y = {"teknik": {"en_boy_16_9_sapma": 0, "kisa_kenar": 768, "keskinlik": 100}, "olculemedi": {}, "yuz_sayisi": 0,
             "el_nesne": {"fener": {"el": "sol"}}, "stil_clip_foto": 0.9}
        ks = [{"alan": "nesne_el", "kisi": "m", "nesne": "fener", "beklenen": "sag", "kor": "sol", "sonuc": "uyumsuz", "tutarli": True}]
        self.assertEqual([x["seviye"] for x in kd.degerlendir(y, ks, b, {"stil": "photograph"}) if x["alan"] == "nesne_el"], ["HATA"])
        y["el_nesne"] = {}
        self.assertEqual([x["seviye"] for x in kd.degerlendir(y, ks, b, {"stil": "photograph"}) if x["alan"] == "nesne_el"], ["BAYRAK"])
        self.assertEqual(kd.aday_karari([{"seviye": "OLCULEMEDI"}]), "BAYRAK")


if __name__ == "__main__":
    unittest.main()
