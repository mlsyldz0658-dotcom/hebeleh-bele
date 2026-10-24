"""Kart kapısı testleri (TASARIM §6.10 test_kart, §7.2 KART, [GS2] §4.6.3, İ-12): kadro çifti ≥ 0,363 → HATA; yalnız hikâyeye bağlı öğe
farkı → ayrisma_kilitli; plaka görünen öğe eksik → HATA; plakada kişi → HATA; NE YOK öğesi → HATA; kart istemleri (3 aday, ad yok, çıplak
sol/sağ yok); [UM] T18 gerçek SFace (model ve fikstür yoksa atlanır)."""
import os, sys, json, glob, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401
import _gorsel_fikstur as F
import ortak, kor, kapi
import istem_derle_gorsel as idg, gemini_paket, gemini_al, kart_denetim as kd, istem_derle


def spec(bagli_yalniz=False):
    m = [{"oge": "dark-auburn braid", "tur": "sac", "hikaye_baglayici": True}]
    v = [{"oge": "close-cropped grey beard", "tur": "sac", "hikaye_baglayici": True}]
    if not bagli_yalniz:
        m.append({"oge": "cream fleece collar", "tur": "kostum", "hikaye_baglayici": False})
        v.append({"oge": "black wool cloak", "tur": "kostum", "hikaye_baglayici": False})
    return {"karakterler": [
        {"id": "mara", "tur": "insan", "kimlik_en": "an adult woman with one long dark-auburn braid over her LEFT shoulder",
         "asimetrik": ["braid over LEFT shoulder"], "ayirt_edici": m, "kostumler": {"k1": {"tarif_en": "a dark-brown shearling coat"}}},
        {"id": "voss", "tur": "insan", "kimlik_en": "a broad-shouldered man with a close-cropped grey beard",
         "ayirt_edici": v, "kostumler": {"k1": {"tarif_en": "a black wool cloak"}}}],
        "mekanlar": [{"id": "kulube", "tarif_en": "a cramped log cabin interior", "notr_durum": {"kapi": "kapali", "ocak_atesi": "sonuk"},
                      "plakalar": [{"id": "ic_genel", "gorunen": [{"id": "kapi", "ad": "a closed wooden door", "ucte_bir": "orta"}]}]}],
        "nesneler": [{"id": "fener", "tarif_en": "a hand-forged iron lantern"}]}


def hazirla(hata=None, bagli_yalniz=False, evren_bos=True):
    ev = F.evren_kur()
    if evren_bos:                                  # kart testinde karakterler henüz kilitli değil (ön kayıt)
        for kid in ("mara", "voss"):
            p = os.path.join(ev, "karakterler", kid, "karakter.json"); j = ortak.json_oku(p)
            ortak.atomik_yaz(p, {"id": kid, "ad": j["ad"], "seri": "TEST", "tur": "insan", "surum": 0, "durum": "on_kayit"})
    kok = F.film_kur("KF")
    ortak.atomik_yaz(os.path.join(kok, "_KARTLAR", "KART_SPEC.json"), spec(bagli_yalniz))
    self_kod, r = idg.derle_kart(kok)
    gemini_paket.paket_kart(kok, 1)
    gemini_al.sahte_uret(kok, "kart", hata or {})
    kor.sahte_cevaplar(kok, "kart", 1)
    kod, rap = kd.denetle(kok, 1)
    return kok, r, rap


def kart(rap, kid): return rap["kartlar"][kid]


def alanlar(rap, kid, aday="a"): return {a["alan"]: a for a in next(x for x in kart(rap, kid)["adaylar"] if x["aday"] == aday)["alanlar"]}


class Kart(unittest.TestCase):
    def test_kart_istemleri(self):
        kok, r, rap = hazirla()
        ks = {k["kart_id"]: k for k in r["kartlar"]}
        self.assertEqual(sorted(ks), ["karakter_mara_k1", "karakter_voss_k1", "mekan_kulube_ic_genel", "nesne_fener_olcek"])
        for k in ks.values():
            self.assertEqual(len(k["dosyalar"]), 3)
            self.assertEqual(istem_derle.yasak_bul(k["istem"]), [], k["istem"])
            self.assertNotIn("Mara", k["istem"])
        self.assertIn("plain light-grey studio backdrop", ks["karakter_mara_k1"]["istem"])
        self.assertIn("no people", ks["mekan_kulube_ic_genel"]["istem"])
        self.assertIn("the kapi is closed", ks["mekan_kulube_ic_genel"]["istem"])

    def test_temiz_kartlar_gecer(self):
        kok, r, rap = hazirla()
        self.assertEqual(rap["sonuc"], "GEC", json.dumps(rap["bayraklar"], ensure_ascii=False)[:500])
        self.assertEqual(kapi.dogrula(rap), [])
        self.assertEqual(kart(rap, "karakter_mara_k1")["secilebilir"], ["a", "b", "c"])

    def test_kadro_cifti_benzer_hata(self):
        kok, r, rap = hazirla({"karakter_mara_k1": ["benzer=voss@0.41"]})
        a = alanlar(rap, "karakter_mara_k1")
        self.assertEqual(a["kadro_benzer"]["seviye"], "HATA")
        self.assertEqual(kart(rap, "karakter_mara_k1")["karar"], "HATA")
        d = ortak.json_oku(os.path.join(kok, "_KARTLAR", "KART_DUZELTME.json"))
        self.assertTrue(any(m["alan"] == "kadro_benzer" and m["cozum"] == "tarif_revizyonu" for m in d["maddeler"]))
        kok, r, rap = hazirla({"karakter_mara_k1": ["benzer=voss@0.30"]})
        self.assertEqual(alanlar(rap, "karakter_mara_k1")["kadro_benzer"]["seviye"], "BAYRAK")

    def test_yalniz_hikaye_bagli_fark_ayrisma_kilitli(self):
        kok, r, rap = hazirla({"karakter_mara_k1": ["benzer=voss@0.5"]}, bagli_yalniz=True)
        a = alanlar(rap, "karakter_mara_k1")
        self.assertEqual(a["ayrisma_kilitli"]["seviye"], "HATA")
        self.assertEqual(a["ayrisma_kilitli"]["sahip"], "hikaye-yazari")
        g = ortak.json_oku(os.path.join(kok, "_KARTLAR", "GORUNUS_DEGISIKLIK_ISTEGI.json"))
        self.assertEqual(g["istekler"][0]["karakter"], "mara")

    def test_plaka_gorunen_eksik_ve_kisi_hata(self):
        kok, r, rap = hazirla({"mekan_kulube_ic_genel": ["gorunen_yok"]})
        self.assertEqual(alanlar(rap, "mekan_kulube_ic_genel")["plaka_gorunen"]["seviye"], "HATA")
        kok, r, rap = hazirla({"mekan_kulube_ic_genel": ["kisi"]})
        self.assertEqual(alanlar(rap, "mekan_kulube_ic_genel")["plaka_kisi"]["seviye"], "HATA")
        self.assertEqual(kart(rap, "mekan_kulube_ic_genel")["karar"], "HATA")

    def test_cizim_ve_yazi(self):
        kok, r, rap = hazirla({"nesne_fener_olcek": ["yazi", "cizim"]})
        a = alanlar(rap, "nesne_fener_olcek")
        self.assertEqual(a["yazi_logo"]["seviye"], "HATA")
        self.assertEqual(a["stil"]["seviye"], "BAYRAK")             # yerel CLIP fotoğraf dedi, kör çizim: tek kaynak

    def test_kor_gozlem_yoksa_gecmez(self):
        kok = F.film_kur("KF2"); F.evren_kur()
        ortak.atomik_yaz(os.path.join(kok, "_KARTLAR", "KART_SPEC.json"), spec())
        idg.derle_kart(kok); gemini_paket.paket_kart(kok, 1); gemini_al.sahte_uret(kok, "kart")
        kod, rap = kd.denetle(kok, 1)
        self.assertNotEqual(rap["sonuc"], "GEC")

    def test_t18_gercek_sface(self):
        """[UM] T18: mara.jpg ↔ mara ≥ 0,45; voss.jpg ↔ mara < 0,363 (YZ_FILM_T18 klasöründe mara.jpg, mara2.jpg, voss.jpg + modeller)."""
        from olcum import kimlik
        d = os.environ.get("YZ_FILM_T18")
        ok, neden = kimlik.hazir()
        if not ok or not d or not all(os.path.isfile(os.path.join(d, f)) for f in ("mara.jpg", "mara2.jpg", "voss.jpg")):
            self.skipTest(f"T18 fikstürü ya da model yok ({neden or 'YZ_FILM_T18'})")
        m = kimlik.yuzler(os.path.join(d, "mara.jpg"))[0]["vektor"]
        m2 = kimlik.yuzler(os.path.join(d, "mara2.jpg"))[0]["vektor"]
        v = kimlik.yuzler(os.path.join(d, "voss.jpg"))[0]["vektor"]
        self.assertGreaterEqual(kimlik.benzerlik(m, m2), 0.45)
        self.assertLess(kimlik.benzerlik(m, v), 0.363)

    def test_macar_esleme(self):
        from olcum import kimlik
        self.assertEqual(sorted(kimlik.macar([[0.1, 0.9], [0.8, 0.2]])), [(0, 0), (1, 1)])
        self.assertEqual(sorted(kimlik.macar([[0.9, 0.1, 0.5]])), [(0, 1)])


if __name__ == "__main__":
    unittest.main()
