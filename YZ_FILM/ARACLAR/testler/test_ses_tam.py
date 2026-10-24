"""test_ses_tam — video sonrası ses (A15–A16) bozuk girdi senaryoları (TASARIM §6.10 `test_ses` tam; [SM2] §4.7.10, §2.2 ses merdiveni).
Adım 10 test_ses.py'nin (kâğıt), adım 13 test_ses_hazirlik.py'nin (hazırlık) sahibidir; bu dosya PR-12'nin araçlarını sınar:
ses_donustur_ana, ses_karar, dudak_denetim, diyalog_esitle, ses_katmani_t2, muzik_yerlestir. Ağ ve kredi yok; sahte sağlayıcı."""
import os, sys, json, glob, shutil, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401
import numpy as np
import _kurgu_fikstur as F
import ortak, kurgu_ortak as ko, plan_kurgu, ses_donustur_ana as sda, ses_karar, dudak_denetim, diyalog_esitle, ses_katmani_t2, muzik_yerlestir

S = ["--saglayici", "sahte"]


def _j(*y):
    with open(os.path.join(*y), encoding="utf-8") as f: return json.load(f)


def _A(kok): return ["--film", kok] + S


def _hazir(kok, plan=True):
    A = _A(kok); sda.main(A)
    if plan: plan_kurgu.main(A)
    return A


def _hepsi(r): return {h["madde"]: h for h in r["hatalar"] + r["bayraklar"]}


class Dudak(unittest.TestCase):
    def test_200ms_kayma_S31(self):
        """Repliği kurguda 200 ms kaydır → S3.1 HATA → kurgu_uygula önerisi (diyalog_kaydir)."""
        kok = F.film_kur(); A = _hazir(kok)
        _, r = dudak_denetim.denetle(kok, A); self.assertEqual(r["sonuc"], "GEC")
        kp = ko.kurgu_plani(kok)[1]; kp["diyalog"][0]["cizelge_bas"] = ko.kare(kp["diyalog"][0]["cizelge_bas"] + 0.2)
        kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        _, r = dudak_denetim.denetle(kok, A)
        h = [x for x in r["hatalar"] if x["madde"] == "S3.1_ofset"]
        self.assertTrue(h); self.assertGreater(abs(h[0]["olcu"]), 125)
        on = _j(kok, "KURGU", f"S3_ONERI_v{kp['kurgu_surumu']}.json")["islemler"]
        self.assertEqual(on[0]["op"], "diyalog_kaydir"); self.assertAlmostEqual(on[0]["sn"], -0.208, places=2)

    def test_ekran_disi_agiz_oynuyor_S35(self):
        """L taşmasının üstündeki planda (dinleyen) ağız açıklığı oynuyor → S3.5 HATA; Z3'te B9 HATA."""
        kok = F.film_kur(); A = _hazir(kok)
        z = list(np.abs(np.sin(np.arange(192) / 2.0)))
        os.makedirs(os.path.join(kok, "_SAHTE", "agiz"), exist_ok=True)
        ortak.atomik_yaz(os.path.join(kok, "_SAHTE", "agiz", "4.json"), {"fps": 24, "yuzler": {"voss": z}})
        _, r = dudak_denetim.denetle(kok, A)
        self.assertIn("S3.5_ekran_disi_agiz", [x["madde"] for x in r["hatalar"]])
        import kurgu_denetim_tam as kdt
        _, r = kdt.denetle(kok, A)
        self.assertIn("B9_agiz", [x["madde"] for x in r["hatalar"]])

    def test_wav2lip_yasak(self):
        self.assertEqual(dudak_denetim.main(["--motor", "wav2lip"]), 4)
        self.assertFalse([s for s in ko.zincir("dudak", []) if "wav2lip" in s.ad.lower()])

    def test_musetalk_yeni_dosya(self):
        """tts_dudak: yeni dosya NNN_dudak_<k>.mp4 (eski klip ezilmez) + V2 yeniden denetim kaydı."""
        kok = F.film_kur(); A = _hazir(kok, plan=False)
        tts = ko.wav_yaz(os.path.join(kok, "SESLER", "tts", "R0001.wav"), 0.1 * np.ones(48000, np.float32))
        d = ko.diyalog_oku(kok); d["replikler"]["R0001"]["tts"] = {"dosya": ko.goreli(kok, tts), "sure_sn": 1.0}; ko.diyalog_yaz(kok, d)
        ortak.atomik_yaz(os.path.join(kok, "SESLER", "DUDAK_ISTEK.json"), {"replikler": [{"replik": "R0001", "plan": 3}]})
        once = ko.sha1(os.path.join(kok, "SIRALI_VIDEO", "003.mp4"))
        self.assertEqual(dudak_denetim.main(A + ["--musetalk"]), 0)
        self.assertTrue(os.path.exists(os.path.join(kok, "SIRALI_VIDEO", "003_dudak_1.mp4")))
        self.assertEqual(once, ko.sha1(os.path.join(kok, "SIRALI_VIDEO", "003.mp4")))
        self.assertEqual(_j(kok, "KUNYE", "V2_YENIDEN.json")["klipler"][0]["plan"], 3)
        self.assertEqual(ko.diyalog_oku(kok)["replikler"]["R0001"]["yol_gercek"], "tts_dudak")


class Seviye(unittest.TestCase):
    def test_tepe_normal_S41(self):
        """Tepeye göre normalleştirilmiş, tepe faktörü farklı iki replik → S4.1 HATA (--denetle); diyalog_esitle düzeltir → ±1 LU."""
        kok = F.film_kur(); A = _hazir(kok)
        t = np.arange(int(2.5 * 48000)) / 48000.0
        sabit = np.sin(2 * np.pi * 220 * t).astype(np.float32); sabit *= 0.6 / np.max(np.abs(sabit))
        darbe = np.zeros_like(sabit); darbe[::4800] = 1.0; darbe = np.convolve(darbe, np.exp(-np.arange(400) / 40.0), "same").astype(np.float32)
        darbe *= 0.6 / np.max(np.abs(darbe))
        d = ko.diyalog_oku(kok)
        for rid, a in (("R0001", sabit), ("R0002", darbe)):
            d["replikler"][rid]["dosya"] = ko.goreli(kok, ko.wav_yaz(os.path.join(kok, "SESLER", "donusum", f"{rid}.wav"), a))
        ko.diyalog_yaz(kok, d)
        _, r = diyalog_esitle.esitle(kok, A + ["--denetle"])
        self.assertIn("S4.1_seviye", [x["madde"] for x in r["hatalar"]])
        _, r = diyalog_esitle.esitle(kok, A)
        self.assertNotIn("S4.1_seviye", [x["madde"] for x in r["hatalar"]])
        d = ko.diyalog_oku(kok)
        for rid in ("R0001", "R0002"): self.assertLessEqual(abs(d["replikler"][rid]["olculen_lufs"] + 19.5), 1.0)
        self.assertTrue(os.path.exists(ko.stem_yolu(kok, "diyalog")))


class Katman(unittest.TestCase):
    def test_iki_yatak_S51(self):
        kok = F.film_kur(); s = ko.sahneler(kok)
        s["sahneler"][3]["zanaat"]["ses"]["yatak_dosya"] = "_SES/baska_yatak.wav"; ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
        A = _hazir(kok); _, r = ses_katmani_t2.kur(kok, A)
        self.assertIn("S5.1_tek_yatak", [x["madde"] for x in r["hatalar"]])

    def test_eski_ozetli_efekt_S57(self):
        """Yeniden çekim taklidi: klip değişti, efekt kaydı eski özetli → S5.7 HATA (denetim); yeniden kurulunca özet güncel."""
        kok = F.film_kur(); A = _hazir(kok); _, r = ses_katmani_t2.kur(kok, A); self.assertFalse(r["hatalar"])
        eski = ko.ses_cizelgesi(kok)["efektler"][0]["klip_ozet"]
        shutil.copyfile(os.path.join(kok, "SIRALI_VIDEO", "002.mp4"), os.path.join(kok, "SIRALI_VIDEO", "001.mp4"))
        _, r = ses_katmani_t2.kur(kok, A + ["--denetle"])
        self.assertIn("S5.7_klip_ozet", [x["madde"] for x in r["hatalar"]])
        ko.sahne_planlari(kok)
        _, r = ses_katmani_t2.kur(kok, A)
        yeni = [e for e in ko.ses_cizelgesi(kok)["efektler"] if e["plan"] == 1]
        if yeni: self.assertNotEqual(yeni[0]["klip_ozet"], eski)
        _, r = ses_katmani_t2.kur(kok, A + ["--denetle"])
        self.assertNotIn("S5.7_klip_ozet", [x["madde"] for x in r["hatalar"]])

    def test_ambiyans_diyalog_alti(self):
        kok = F.film_kur(); A = _hazir(kok); diyalog_esitle.esitle(kok, A); _, r = ses_katmani_t2.kur(kok, A)
        self.assertNotIn("S5.4_diyalog_alti", [x["madde"] for x in r["hatalar"]])
        self.assertNotIn("S5.2_ambiyans_boslugu", [x["madde"] for x in r["hatalar"]])
        sc = ko.ses_cizelgesi(kok)
        self.assertEqual(set(sc["stemler"]), {"diyalog", "ambiyans", "efekt"})


class Muzik(unittest.TestCase):
    def test_kisma_S62(self):
        kok = F.film_kur(); A = _hazir(kok); diyalog_esitle.esitle(kok, A); _, r = muzik_yerlestir.yerlestir(kok, A)
        self.assertNotIn("S6.2_diyalog_alti", [x["madde"] for x in r["hatalar"]])
        m = ko.ses_cizelgesi(kok)["muzik"][0]; self.assertTrue(m["kisma"]); self.assertLessEqual(m["kisma"][0]["db"], -12)

    def test_zincir_bos_muziksiz(self):
        """Seçilmiş müzik yok (D-25) → müziksiz sürer + S6 BAYRAK, HATA değil."""
        kok = F.film_kur(); A = _hazir(kok)
        ml = _j(kok, "MUZIK", "muzik_listesi.json"); ml["ipuclari"][0]["secilen"] = None
        ortak.atomik_yaz(os.path.join(kok, "MUZIK", "muzik_listesi.json"), ml)
        _, r = muzik_yerlestir.yerlestir(kok, A)
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertIn("S6_muzik_yok", [x["madde"] for x in r["bayraklar"]])
        self.assertEqual(ko.ses_cizelgesi(kok)["muzik"], [])

    def test_elle_saglayici_S68(self):
        kok = F.film_kur(); A = _hazir(kok)
        ml = _j(kok, "MUZIK", "muzik_listesi.json"); ml["ipuclari"][0]["saglayici"] = "gemini_muzik_paketi"
        ortak.atomik_yaz(os.path.join(kok, "MUZIK", "muzik_listesi.json"), ml)
        _, r = muzik_yerlestir.yerlestir(kok, A)
        self.assertIn("S6.8_elle_saglayici", [x["madde"] for x in r["hatalar"]])


class Donusum(unittest.TestCase):
    def test_kapili_pencere_ve_f0(self):
        """Dönüşüm yalnız hizalanmış söz pencerelerinde; F0 kaydırma = round(12·log2(hedef/kaynak))."""
        kok = F.film_kur()
        os.makedirs(os.path.join(kok, "_SES"), exist_ok=True)
        ortak.atomik_yaz(os.path.join(kok, "_SES", "SES_PROFILLERI.json"), {"profiller": {"mara": {"f0_medyan_hz": 196.0}}})
        d = ko.diyalog_oku(kok); r = d["replikler"]["R0001"]; r["kelimeler"] = [{"w": "It's", "bas": 2.0, "bit": 2.4}, {"w": "late", "bas": 3.6, "bit": 4.5}]
        ko.diyalog_yaz(kok, d); _hazir(kok, plan=False)
        r = ko.diyalog_oku(kok)["replikler"]["R0001"]
        self.assertEqual(r["donusum"]["f0_kaydirma_yt"], round(12 * np.log2(196.0 / r["donusum"]["f0_kaynak_hz"])))
        g, sr = ko.wav_oku(ko.mutlak(kok, r["donusum"]["giris"]))
        bosluk = g[int((2.6 - 1.9) * sr):int((3.4 - 1.9) * sr)]                 # 2,5–3,5 arası söz yok → susturulmuş
        self.assertLess(float(np.max(np.abs(bosluk))), 1e-4)
        self.assertLessEqual(abs(r["donusum"]["zarf_gecikme_ms"] - 4.0), 2.0)

    def test_benzerlik_dusuk_merdiven(self):
        """Dönüşüm benzerliği 0,58 → S2.9: önce sonraki motor (0 kredi) denenir, sonra ağız görünür olduğu için ai84_vc isteği."""
        kok = F.film_kur(); ortak.atomik_yaz(os.path.join(kok, "_SAHTE", "donusum.json"), {"R0001": {"benzerlik": 0.58}})
        A = _hazir(kok); _, r = ses_karar.karar(kok, A)
        m = ko.diyalog_oku(kok)["replikler"]["R0001"]["merdiven"]
        self.assertEqual([x["basamak"] for x in m][:1], ["sonraki_motor"])
        self.assertIn("ai84_vc", [x["basamak"] for x in m])
        self.assertTrue(os.path.exists(os.path.join(kok, "SESLER", "AI84_VC_ISTEK.json")))
        self.assertIn("S2.9", [x["madde"] for x in r["hatalar"]])


class Merdiven(unittest.TestCase):
    def _mk(self, kok, rid, **k):
        d = ko.diyalog_oku(kok); d["replikler"][rid]["metin_kapisi"].update(k); ko.diyalog_yaz(kok, d)

    def test_konusma_yok_S21(self):
        """Sahte Veo klibinde konuşma yok → S2.1 HATA → YENIDEN_URET'te kaynak_kapi S2, CORRECTION şablonu, 0 kredi gerekçesi."""
        kok = F.film_kur(); _hazir(kok, plan=False); self._mk(kok, "R0002", konusma_bulundu=False)
        _, r = ses_karar.karar(kok, _A(kok))
        self.assertIn("S2.1_konusma", [x["madde"] for x in r["hatalar"]])
        q = _j(kok, "KUYRUK", "YENIDEN_URET.json")["maddeler"]
        self.assertEqual((q[0]["plan"], q[0]["kaynak_kapi"]), (5, "S2"))
        self.assertTrue(q[0]["duzeltme"].startswith("CORRECTION: Voss speaks the line aloud"))
        self.assertTrue(q[0]["sifir_kredi"]["denendi"])

    def test_ad_yanlis_ikinci_kez_ders(self):
        """Sahte ASR adı yanlış duyuyor → S2.3 yeniden çekim; ikinci kez → istem_kalibi ders adayı."""
        kok = F.film_kur(); _hazir(kok, plan=False)
        self._mk(kok, "R0002", ad_dogru=False, ad_yazilan="Mara", ad_duyulan="Myra", okunus_yazimi="MAH-rah")
        _, r = ses_karar.karar(kok, _A(kok)); self.assertIn("S2.3_ad", [x["madde"] for x in r["hatalar"]])
        q = _j(kok, "KUYRUK", "YENIDEN_URET.json")["maddeler"]; self.assertIn('"MAH-rah"', q[0]["duzeltme"])
        import kuyruk; kuyruk.durum_degistir(kok, q[0]["id"], "tamam")
        shutil.copyfile(os.path.join(kok, "SIRALI_VIDEO", "004.mp4"), os.path.join(kok, "SIRALI_VIDEO", "005.mp4"))   # yeniden çekildi
        _, r = ses_karar.karar(kok, _A(kok))
        m = ko.diyalog_oku(kok)["replikler"]["R0002"]["merdiven"]
        self.assertEqual(sum(1 for x in m if x["basamak"] == "yeniden_cek"), 2)
        self.assertEqual(m[-1].get("ders_adayi"), "istem_kalibi")
        ham = glob.glob(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "DERSLER", "ham", "*kapi_hatasi*.json"))
        self.assertTrue(any(_j(p).get("kategori") == "istem_kalibi" for p in ham))

    def test_gri_bant_replik_kabul(self):
        """WER 0,18, tasidigi boş → gri bant → replik_kabul görevi (BAYRAK); kabul → GEÇ ve altyazı duyulan_metin'den."""
        kok = F.film_kur(); self._mk(kok, "R0001", wer=0.18, duyulan="It's late Captain what you want")
        _hazir(kok, plan=False)
        istek = _j(kok, "SESLER", "REPLIK_KABUL_ISTEK.json")
        self.assertEqual([x["replik"] for x in istek["replikler"]], ["R0001"])
        _, r = ses_karar.karar(kok, _A(kok))
        self.assertIn("S2.2_S2.4_gri_bant", [x["madde"] for x in r["bayraklar"]])
        ortak.atomik_yaz(os.path.join(kok, "_HIKAYE_ODASI", "REPLIK_KABUL.json"), {"kararlar": {"R0001": {"karar": "kabul"}}})
        sda.main(_A(kok) + ["--donustur"]); _, r = ses_karar.karar(kok, _A(kok))
        self.assertNotIn("S2.2_S2.4_gri_bant", [x["madde"] for x in r["bayraklar"] + r["hatalar"]])
        self.assertEqual(ko.diyalog_oku(kok)["replikler"]["R0001"]["duyulan_metin"], "It's late Captain what you want")

    def test_tasidigi_eksik(self):
        """WER 0,05 ama tasidigi kelimesi eksik → replik_kabul (otomatik kabul yok)."""
        kok = F.film_kur(); self._mk(kok, "R0001", wer=0.05, tasidigi_degisen_kelime=["late"])
        _hazir(kok, plan=False); _, r = ses_karar.karar(kok, _A(kok))
        self.assertIn("S2.2_S2.4_gri_bant", [x["madde"] for x in r["bayraklar"]])
        self.assertNotIn("dosya", ko.diyalog_oku(kok)["replikler"]["R0001"])            # kabul olmadan dönüştürülmedi

    def test_tts_esnetme_S212(self):
        kok = F.film_kur(); _hazir(kok, plan=False)
        d = ko.diyalog_oku(kok); r = d["replikler"]["R0002"]; r["yol_plan"] = r["yol_gercek"] = "tts"; r["tts"] = {"esnetme_oran": 0.12}
        ko.diyalog_yaz(kok, d); _, rp = ses_karar.karar(kok, _A(kok))
        self.assertIn("S2.12_tts_esnetme", [x["madde"] for x in rp["hatalar"]])


if __name__ == "__main__":
    unittest.main()
