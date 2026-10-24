"""Evren kart kilidi testleri (TASARIM §6.10 test_evren, D-42, [GS2] §4.6.3): kilitle (sürümlü kopya, SHA1, 01_KARAKTERLER); kilitli dosyanın
SHA1'i değişti → durdu; sürüm açma; kimlik_en'de ad → HATA; KART HATA'lı aday kilitlenmez; sahip dışı alana yazma reddi; evren.py CLI."""
import os, sys, json, glob, subprocess, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401
import _gorsel_fikstur as F
import ortak, evren, evren_kilit as ek
import test_kart as TK

ARAC = os.path.join(os.path.dirname(HERE), "evren.py")


def secim_yaz(kok, secim):
    ortak.atomik_yaz(os.path.join(kok, "_KARTLAR", "KART_SECIM.json"),
                     {"secim": [{"kart_id": k, "aday": a, "gerekce": "ton uyumu"} for k, a in secim.items()]})


class Evren(unittest.TestCase):
    def kilitli(self, hata=None):
        kok, r, rap = TK.hazirla(hata)
        secim_yaz(kok, {"karakter_mara_k1": "b", "karakter_voss_k1": "a", "mekan_kulube_ic_genel": "a", "nesne_fener_olcek": "c"})
        return kok

    def test_kilitle_surumlu_kopya_ve_hash(self):
        kok = self.kilitli()
        r, kod = ek.kilitle(kok)
        self.assertEqual(kod, 0, r)
        d = evren.seri_yolu("TEST", "karakterler", "mara")
        k = ortak.json_oku(os.path.join(d, "karakter.json"))
        self.assertEqual((k["durum"], k["surum"], k["kostumler"]["k1"]["kart"]), ("kilitli", 1, "kart_k1_v1.jpg"))
        self.assertEqual(k["hash"]["kart_k1_v1.jpg"], ek.sha1(os.path.join(d, "kart_k1_v1.jpg")))
        self.assertEqual(k["ad"], "Mara")                                       # hikâye alanı korunur
        self.assertTrue(os.path.isfile(os.path.join(kok, "01_KARAKTERLER", "mara.jpg")))
        m = ortak.json_oku(evren.seri_yolu("TEST", "mekanlar", "kulube", "mekan.json"))
        self.assertEqual(m["plakalar"]["ic_genel"]["durum"], "kilitli")
        self.assertEqual(ek.kilit_dogrula("TEST"), [])
        r2, kod2 = ek.kilitle(kok)                                              # ikinci kilit yeni sürüm açar, eskisi kalır
        self.assertEqual(kod2, 0)
        self.assertTrue(os.path.isfile(os.path.join(d, "kart_k1_v1.jpg")) and os.path.isfile(os.path.join(d, "kart_k1_v2.jpg")))

    def test_kilitli_dosya_degisti_durdu(self):
        kok = self.kilitli(); ek.kilitle(kok)
        p = evren.seri_yolu("TEST", "karakterler", "mara", "kart_k1_v1.jpg")
        with open(p, "ab") as f: f.write(b"elle")
        b = ek.kilit_dogrula("TEST")
        self.assertEqual(len(b), 1); self.assertIn("--surum-ac", b[0]["neden"])
        r, kod = ek.kilitle(kok)
        self.assertEqual(kod, 1); self.assertTrue(r.get("durdu"))
        self.assertEqual(subprocess.run([sys.executable, ARAC, "--kilit-dogrula", "--seri", "TEST"], capture_output=True).returncode, 1)
        r, kod = ek.surum_ac("TEST", "mara")
        self.assertEqual(kod, 0)
        self.assertEqual(ortak.json_oku(evren.seri_yolu("TEST", "karakterler", "mara", "karakter.json"))["durum"], "surum_acik")
        self.assertEqual(ek.kilit_dogrula("TEST"), [])                         # sürüm açılınca kilit denetimi o karakteri bırakır
        self.assertTrue(os.path.isfile(p), "eski dosya silinmez")

    def test_kimlik_en_ad_icermez(self):
        kok = self.kilitli()
        s = ortak.json_oku(os.path.join(kok, "_KARTLAR", "KART_SPEC.json"))
        s["karakterler"][0]["kimlik_en"] = "Mara, an adult woman with a braid"
        ortak.atomik_yaz(os.path.join(kok, "_KARTLAR", "KART_SPEC.json"), s)
        r, kod = ek.kilitle(kok)
        self.assertEqual(kod, 1); self.assertTrue(any("adını" in h for h in r["hatalar"]))
        self.assertNotEqual(ortak.json_oku(evren.seri_yolu("TEST", "karakterler", "mara", "karakter.json")).get("durum"), "kilitli")

    def test_hatali_aday_kilitlenmez(self):
        kok = self.kilitli({"karakter_mara_k1": ["benzer=voss@0.5"]})
        r, kod = ek.kilitle(kok)
        self.assertEqual(kod, 1); self.assertTrue(any("HATA" in h for h in r["hatalar"]))
        self.assertEqual(subprocess.run([sys.executable, ARAC, "--kilitle", "--film", kok], capture_output=True).returncode, 1)

    def test_sahip_disi_alana_yazma_reddi(self):
        F.evren_kur()
        with self.assertRaises(ek.SahipHatasi): ek.alan_yaz("TEST", "karakterler/mara/karakter.json", {"ad": "Başka"}, "goruntu")
        with self.assertRaises(ek.SahipHatasi): ek.alan_yaz("TEST", "karakterler/mara/ses.json", {"profil": "x"}, "goruntu")
        with self.assertRaises(ek.SahipHatasi): ek.alan_yaz("TEST", "mekanlar/kulube/kroki.json", {"x": 1}, "goruntu")
        y = ek.alan_yaz("TEST", "karakterler/mara/karakter.json", {"boy_m": 1.7}, "goruntu")
        self.assertEqual(y["boy_m"], 1.7)
        self.assertTrue(glob.glob(evren.seri_yolu("TEST", "karakterler", "mara", "karakter_v*.json")), "eski sürüm dosyası kalır")

    def test_cli_yardim_ve_eksik_girdi(self):
        r = subprocess.run([sys.executable, ARAC, "--kilitle"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 1)
        r = subprocess.run([sys.executable, ARAC, "--film-sonu"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 4)                                     # başka adımın komutu hâlâ "henüz yok"


if __name__ == "__main__":
    unittest.main()
