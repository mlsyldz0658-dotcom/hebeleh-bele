"""test_arsivle — kendiliğinden arşiv (TASARIM D-38, §6.10 `test_arsivle`): bağlı yol ve açık kuyruk girdisi taşınmaz; ayna bayrağı yok;
kalıcı silme yok (taşınan her dosya hedefte durur); D takılı değilse 8 BEKLE. Ağ ve kredi yok."""
import os, sys, json, glob, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401
import _kurgu_fikstur as F
import ortak, kurgu_ortak as ko, arsivle, capcut_taslak as ct


def _yaz(p, icerik=b"x" * 1000):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f: f.write(icerik)
    return p


class Arsivle(unittest.TestCase):
    def kur(self):
        kok = F.film_kur(klipler=False)
        j = lambda *a: os.path.join(kok, *a)
        self.bagli = _yaz(j("KURGU", "_onbellek", "seg_bagli.mp4"))
        self.serbest = _yaz(j("KURGU", "_onbellek", "seg_serbest.mp4"))
        for v in (1, 2, 3, 4): _yaz(j("KURGU", "surumler", f"v{v}", "klipler", "001.mp4"))
        self.kuyruk_klip = _yaz(j("SIRALI_VIDEO", "_ESKI", "003_t1.mp4")); self.eski_klip = _yaz(j("SIRALI_VIDEO", "_ESKI", "005_t1.mp4"))
        for i, ad in enumerate(("animatik_v1.mp4", "animatik_v2.mp4")):
            p = _yaz(j("ANIMATIK", ad)); os.utime(p, (1000 + i, 1000 + i))
        # son taslak bağlı yolu gösterir
        taslak = j("KURGU", "CAPCUT_SAHTE", "YZ T v4"); os.makedirs(taslak)
        m = {"ad": "YZ T v4", "fps": 24, "sure_us": 1000000, "sure": 1.0,
             "kanallar": {"Klipler": [ct._seg("YZ T v4", "Klipler", 1, self.bagli, 0.0, 1.0, 0.0, 1.0, ses=0.0, plan=1)]}}
        ortak.atomik_yaz(os.path.join(taslak, "draft_content.json"), ct.icerik_kur(m))
        ortak.atomik_yaz(j("KURGU", "son_capcut_projesi.json"), {"_surum": 2, "klasor": taslak, "segmentler": []})
        ortak.atomik_yaz(j("KUYRUK", "YENIDEN_URET.json"), {"_surum": 1, "maddeler": [
            {"id": "YU-KI-1-001", "plan": 3, "tur": "video", "durum": "bekliyor"}, {"id": "YU-KI-1-002", "plan": 5, "tur": "video", "durum": "tamam"}]})
        return kok

    def test_kuru_hicbir_sey_tasimaz(self):
        kok = self.kur(); k, r = arsivle.arsivle(kok, ["--kuru"])
        self.assertEqual(k, 0); self.assertTrue(os.path.exists(self.serbest)); self.assertIn("KURGU/_onbellek/seg_serbest.mp4", r["tasinan"])

    def test_bagli_ve_kuyruk_tasinmaz(self):
        kok = self.kur(); k, r = arsivle.arsivle(kok, [])
        self.assertEqual(k, 0)
        self.assertTrue(os.path.exists(self.bagli)); self.assertIn("KURGU/_onbellek/seg_bagli.mp4", r["atlanan_bagli"])
        self.assertTrue(os.path.exists(self.kuyruk_klip)); self.assertIn("SIRALI_VIDEO/_ESKI/003_t1.mp4", r["atlanan_kuyruk"])
        hedef = r["hedef"]
        for rel in ("KURGU/_onbellek/seg_serbest.mp4", "SIRALI_VIDEO/_ESKI/005_t1.mp4", "KURGU/surumler/v1/klipler/001.mp4",
                    "ANIMATIK/animatik_v1.mp4"):
            self.assertFalse(os.path.exists(os.path.join(kok, rel)), rel)
            self.assertTrue(os.path.exists(os.path.join(hedef, rel)), rel)            # taşındı, silinmedi
        for rel in ("KURGU/surumler/v3/klipler/001.mp4", "KURGU/surumler/v4/klipler/001.mp4", "ANIMATIK/animatik_v2.mp4"):
            self.assertTrue(os.path.exists(os.path.join(kok, rel)), rel)             # son iki sürüm ve en yeni animatik kalır
        self.assertTrue(glob.glob(os.path.join(kok, "_RAPOR", "ARSIV_*.json")))

    def test_ayna_bayragi_yok(self):
        with open(arsivle.__file__, encoding="utf-8") as f: kaynak = f.read()
        self.assertNotIn("/" + "MIR", kaynak)
        for k in (arsivle.robocopy_komutu("a", "b"), arsivle.robocopy_komutu("a", "b", ["x.mp4"])):
            self.assertNotIn("/" + "MIR", [x.upper() for x in k]); self.assertTrue({"/MOV", "/MOVE"} & set(k))

    def test_P9_arsivdeki_ayni_adli_dosyanin_ustune_yazilmaz(self):
        """Taşıma kalıcı silme değildir ama arşivde aynı adlı dosya varsa üzerine YAZILMAZ: kaynak yerinde kalır, rapor bilgi verir."""
        kok = self.kur(); eski = arsivle.arsiv_koku
        import tempfile
        ayri = tempfile.mkdtemp(dir=ortak.yollar()["veri_kok"])                     # öteki testlerin arşivine karışmaz
        arsivle.arsiv_koku = lambda: os.path.join(ayri, "ARSIV")
        self.addCleanup(setattr, arsivle, "arsiv_koku", eski)
        _, r0 = arsivle.arsivle(kok, ["--kuru"])
        hedef = os.path.join(r0["hedef"], "KURGU", "_onbellek", "seg_serbest.mp4")
        _yaz(hedef, b"ARSIVDEKI_ESKI" * 10)
        k, r = arsivle.arsivle(kok, [])
        self.assertEqual(k, 0)
        with open(hedef, "rb") as f: self.assertEqual(f.read(), b"ARSIVDEKI_ESKI" * 10, "arşivdeki dosyanın üzerine yazıldı")
        self.assertTrue(os.path.exists(self.serbest), "üzerine yazılamayan kaynak silinmiş/taşınmış")
        self.assertIn("KURGU/_onbellek/seg_serbest.mp4", r["atlanan_arsivde_var"]); self.assertNotIn("KURGU/_onbellek/seg_serbest.mp4", r["tasinan"])
        for kmt in (arsivle.robocopy_komutu("a", "b"), arsivle.robocopy_komutu("a", "b", ["x.mp4"])):
            self.assertTrue({"/XC", "/XN", "/XO"} <= set(kmt), kmt)                          # robocopy de üzerine yazmaz

    def test_d_takili_degil_bekle(self):
        kok = self.kur(); eski = arsivle.arsiv_koku
        arsivle.arsiv_koku = lambda: os.path.join(ortak.yollar()["veri_kok"], "YOK_DISK", "ARSIV")
        gercek = arsivle.disk_takili              # Windows'ta geçici klasörün sürücüsü hep takılı: takılı olmayan disk benzetilir
        arsivle.disk_takili = lambda k: False if "YOK_DISK" in os.path.abspath(k) else gercek(k)
        self.addCleanup(setattr, arsivle, "disk_takili", gercek)
        try:
            k, r = arsivle.arsivle(kok, [])
            self.assertEqual(k, 8); self.assertIn("D'yi tak", r["kullaniciya"]); self.assertTrue(os.path.exists(self.serbest))
        finally: arsivle.arsiv_koku = eski


if __name__ == "__main__":
    unittest.main()
