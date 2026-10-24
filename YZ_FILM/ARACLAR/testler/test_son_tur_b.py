"""test_son_tur_b — son tur temizlik maddeleri (B): tek ışık biçimi + çevirici, plan_kurgu'nun KURGU_DUZEN_T2'yi yeniden uygulaması,
video_hazir'in zincir/sha1 kabulü, aşama komutları, .bat'lar, şablon eşikleri ve küçük araç temizlikleri. Ağ ve kredi yok."""
import os, sys, json, io, glob, contextlib, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for p in (HERE, ARACLAR):
    if p not in sys.path: sys.path.insert(0, p)
import _ortam  # noqa: F401  (önce: geçici YOLLAR.json)
import ortak, kroki


def _j(*yol):
    with open(os.path.join(*yol), encoding="utf-8") as f: return json.load(f)


class IsikTekBicim(unittest.TestCase):
    """kroki _derlenir.isik_kadrajda'yı {rol: "<on|arka>_<sol|sag>"} yazar; tüketiciler kroki.isik_yonu ile çevirir."""
    def test_cevirici(self):
        self.assertEqual(kroki.isik_yonu({"ana": "on_sol", "dolgu": "arka_sag"}), "soldan")
        self.assertEqual(kroki.isik_yonu({"ana": "arka_sag"}), "sagdan")
        self.assertEqual(kroki.isik_yonu({"dolgu": "on_sol"}, "dolgu"), "soldan")
        self.assertEqual(kroki.isik_yonu("soldan"), "soldan")                  # eski düz dize aynen
        for bos in (None, {}, {"dolgu": "on_sol"}, "duz", 3): self.assertIsNone(kroki.isik_yonu(bos))

    def test_istem_derle_gorsel_zanaat(self):
        """istem_derle --gorsel ORNEK_3_SAHNE_ZANAAT'ta TypeError vermeden koşar; ana ışığın yönü istemde 'from frame left/right'."""
        import _zanaat as Z, plan_birlestir, istem_derle
        kok = Z.kopya("ZN_ISIK")
        self.assertEqual(Z.kos(plan_birlestir, "--film", kok)[0], 0)
        kod, _ = Z.kos(istem_derle, "--gorsel", "--film", kok)
        self.assertIn(kod, (0, 1))                 # 1 = evren kaydı yok (kimlik_dizesi_yok); çökme yok
        for p in _j(kok, "SAHNELER.json")["sahneler"]:
            isik = (p.get("_derlenir") or {}).get("isik_kadrajda")
            self.assertIsInstance(isik, dict)
            beklenen = {"soldan": "from frame left", "sagdan": "from frame right"}[kroki.isik_yonu(isik)]
            self.assertIn(beklenen, p.get("gorsel_istem") or "", p.get("no"))

    def test_duzeltme_ve_kare_denetim_ceviriciyi_kullanir(self):
        import duzeltme
        plan = {"no": 1, "_derlenir": {"isik_kadrajda": {"ana": "on_sag"}}, "zanaat": {"kadrajdakiler": []}}
        self.assertIn("right", duzeltme.madde_cumlesi({"alan": "isik"}, plan))
        plan["_derlenir"]["isik_kadrajda"] = {"ana": "arka_sol"}
        self.assertIn("left", duzeltme.madde_cumlesi({"alan": "isik"}, plan))
        for ad in ("duzeltme.py", "kare_denetim.py", "istem_derle_gorsel.py"):
            with open(os.path.join(ARACLAR, ad), encoding="utf-8") as f: m = f.read()
            self.assertIn("kroki.isik_yonu(der.get(\"isik_kadrajda\"))", m, ad)


class PlanKurguDuzenT2(unittest.TestCase):
    def test_diyalog_kaydir_ekran_disi_yeniden_kurulusta_kalir(self):
        import _kurgu_fikstur as F, kurgu_ortak as ko, plan_kurgu, ses_donustur_ana as sda, kurgu_uygula as ku
        kok = F.film_kur("SON_TUR_DUZEN"); A = ["--film", kok, "--saglayici", "sahte"]
        with contextlib.redirect_stdout(io.StringIO()): sda.main(A); plan_kurgu.main(A)
        d0 = {d["replik"]: d for d in ko.kurgu_plani(kok)[1]["diyalog"]}
        on = os.path.join(kok, "KURGU", "S3_ONERI_v1.json")
        ortak.atomik_yaz(on, {"asama": "T2", "islemler": [
            {"op": "diyalog_kaydir", "replik": "R0001", "sn": -0.208, "plan": 3, "kok_neden": "dudak_kayma", "bulgu": "S3.1"}]})
        self.assertEqual(ku.calistir(kok, "T2", 1, kararlar=on)[0], 0)
        ortak.atomik_yaz(os.path.join(kok, "KURGU", "SES_ISTEKLERI.json"),
                         {"islemler": [{"replik": "R0002", "op": "ekran_disi", "plan": 5, "kok_neden": "dudak_kayma"}]})
        self.assertEqual(ku.calistir(kok, "T2", 2)[0], 0)
        once = {d["replik"]: d for d in ko.kurgu_plani(kok)[1]["diyalog"]}
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(plan_kurgu.main(A), 0)       # T2 yeniden kurulur
        kp = ko.kurgu_plani(kok)[1]; d = {x["replik"]: x for x in kp["diyalog"]}
        self.assertAlmostEqual(d["R0001"]["cizelge_bas"], d0["R0001"]["cizelge_bas"] - 0.208, places=2)
        self.assertAlmostEqual(d["R0001"]["cizelge_bas"], once["R0001"]["cizelge_bas"], places=2)
        self.assertEqual((d["R0002"]["plan"], d["R0002"]["ekran_disi"]), (once["R0002"]["plan"], True))
        self.assertGreaterEqual(kp.get("duzen_uygulanan", 0), 1)
        self.assertFalse(kp.get("duzen_atlanan"), kp.get("duzen_atlanan"))
        with contextlib.redirect_stdout(io.StringIO()): plan_kurgu.main(A)                           # ikinci kez: katlanmaz
        d2 = {x["replik"]: x for x in ko.kurgu_plani(kok)[1]["diyalog"]}
        self.assertAlmostEqual(d2["R0001"]["cizelge_bas"], d["R0001"]["cizelge_bas"], places=3)


class VideoHazir(unittest.TestCase):
    def _film(self, plan):
        import tempfile, hashlib
        kok = tempfile.mkdtemp(dir=_ortam.VERI); os.makedirs(os.path.join(kok, "SIRALI_GORSEL"))
        y = os.path.join(kok, "SIRALI_GORSEL", "002.jpg")
        with open(y, "wb") as f: f.write(b"kare-002")
        with open(y, "rb") as f: sha = hashlib.sha1(f.read()).hexdigest()
        ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), {"sahneler": [dict(plan(sha), no=2)]})
        return kok, sha

    def test_g1_kisa_sha_onek(self):
        import kare_denetim as kd
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "GEC", "sha1": sha[:12]}}})
        self.assertEqual(kd.video_hazir(kok, 2), (True, ""))
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "GEC", "sha1": sha[:7]}}})      # < 8 hane: kabul yok
        self.assertFalse(kd.video_hazir(kok, 2)[0])
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "GEC", "sha1": "f" * 12}}})
        self.assertIn("SHA1", kd.video_hazir(kok, 2)[1])
        kok, _ = self._film(lambda sha: {"denetim": {"G1": {"sonuc": "BAYRAK", "sha1": sha}}})
        self.assertFalse(kd.video_hazir(kok, 2)[0])

    def test_zincir_g1z(self):
        import kare_denetim as kd
        zin = lambda sonuc, sha: {"uretim": {"zincir": {"yontem": "son_kare", "kaynak": 1, "kare_sha1": sha, "g1z": {"sonuc": sonuc, "sha1": sha}}}}
        kok, _ = self._film(lambda sha: zin("GEC", sha[:10]))                      # G1 kaydı yok; zincir G1Z GEÇ yeter
        self.assertEqual(kd.video_hazir(kok, 2), (True, ""))
        kok, _ = self._film(lambda sha: zin("BAYRAK", sha))
        self.assertFalse(kd.video_hazir(kok, 2)[0])
        kok, _ = self._film(lambda sha: zin("GEC", "0" * 12))                      # bayat zincir karesi
        self.assertFalse(kd.video_hazir(kok, 2)[0])

    def test_memmet_yedek_yolu_kalkti(self):
        with open(os.path.join(ARACLAR, "memmet.py"), encoding="utf-8") as f: m = f.read()
        govde = m[m.index("    def video_hazir(self"):m.index("    def kredi_once(")]
        self.assertNotIn("_sha_tutar", govde); self.assertNotIn("get(\"g1z\")", govde)


class EvrenLeitmotif(unittest.TestCase):
    def test_film_sonu_leitmotif_adaylari_evrene(self):
        import shutil, evren, evren_film_sonu as efs
        from test_yayin import HIKAYE
        seri = "SONTURB"; shutil.rmtree(evren.seri_yolu(seri), ignore_errors=True)
        film = os.path.join(_ortam.VERI, "FILMLER", "T_SON_TUR_LM")
        ortak.atomik_yaz(os.path.join(film, "HAZIRLIK.json"), {"film": "T_SON_TUR_LM", "seri": seri})
        ortak.atomik_yaz(os.path.join(film, "HIKAYE.json"), dict(HIKAYE, evren=seri, seri=seri))
        self.assertEqual(evren.on_kayit(film, seri)[1], 0)
        ortak.atomik_yaz(evren.seri_yolu(seri, "muzik", "leitmotifler.json"), {"LM_ESKI": {"notalar": [60, 62], "ilk_film": "F0"}})
        ortak.atomik_yaz(os.path.join(film, "MUZIK", "leitmotif_adaylari.json"), {"durum": "aday", "leitmotifler": {
            "LM_SERA": {"notalar": [64, 67, 69], "bpm": 72}, "LM_ESKI": {"notalar": [1, 2, 3]}}})
        r, kod = efs.film_sonu(film); self.assertEqual(kod, 0, r)
        self.assertIn("muzik/leitmotifler.json", r["degisen"]); self.assertEqual(r["leitmotifler"], ["LM_SERA"])
        lm = _j(evren.seri_yolu(seri, "muzik", "leitmotifler.json"))
        self.assertEqual(lm["LM_SERA"], {"notalar": [64, 67, 69], "bpm": 72, "ilk_film": "T_SON_TUR_LM"})
        self.assertEqual(lm["LM_ESKI"]["notalar"], [60, 62])                       # evrenin kaydı kalır (yalnız eklenir)
        self.assertTrue(glob.glob(evren.seri_yolu(seri, "muzik", "leitmotifler_v*.json")))   # eski hâl silinmedi
        self.assertTrue(os.path.isfile(os.path.join(film, "MUZIK", "leitmotif_adaylari.json")))
        self.assertNotIn("muzik/leitmotifler.json", efs.film_sonu(film)[0]["degisen"])   # tekrar: değişiklik yok
        import muzik
        self.assertIn("LM_SERA", muzik.evren_motifleri({"evren": seri}))            # muzik.py düz biçimi okur


class AsamaKomutlari(unittest.TestCase):
    def test_a15_istek_a16_s3_onerisi(self):
        import hat.asamalar as HAT
        a15 = {x.kod: x for x in HAT.asama("A15").gorevler}
        self.assertEqual((a15["TI"].arac, a15["TI"].argumanlar), ("seslendir.py", ("--istek",)))
        self.assertGreater(a15["TI"].grup, a15["SK"].grup); self.assertTrue(a15["TI"].kredili)
        a16 = {x.kod: x for x in HAT.asama("A16").gorevler}
        self.assertEqual((a16["KU"].arac, a16["KU"].argumanlar), ("kurgu_uygula.py", ("--kararlar", "S3_ONERI", "--cizelge", "T2")))
        self.assertLess(a16["DU"].grup, a16["KU"].grup); self.assertLess(a16["KU"].grup, a16["KZ"].grup)
        self.assertEqual(HAT.YEREL_KAPILAR, ()); self.assertEqual(HAT.denetle(), [])

    def test_kurgu_uygula_s3_onerisi_bir_kez(self):
        import _kurgu_fikstur as F, kurgu_ortak as ko, plan_kurgu, ses_donustur_ana as sda, kurgu_uygula as ku
        kok = F.film_kur("SON_TUR_S3"); A = ["--film", kok, "--saglayici", "sahte"]
        with contextlib.redirect_stdout(io.StringIO()): sda.main(A); plan_kurgu.main(A)
        S3 = ["--kararlar", "S3_ONERI", "--cizelge", "T2", "--film", kok]
        with contextlib.redirect_stdout(io.StringIO()) as o: self.assertEqual(ku.main(S3), 0)        # öneri yok: iş yok, 0
        self.assertIn("S3 önerisi yok", o.getvalue())
        kp = ko.kurgu_plani(kok)[1]; n = kp["kurgu_surumu"]; d0 = {d["replik"]: d["cizelge_bas"] for d in kp["diyalog"]}
        on = os.path.join(kok, "KURGU", "S3_ONERI_v%d.json" % n)
        ortak.atomik_yaz(on, {"asama": "T2", "kip": "s3_yerlesim", "kaynak": "dudak_denetim", "islemler": [
            {"op": "diyalog_kaydir", "replik": "R0001", "sn": -0.208, "plan": 3, "kok_neden": "dudak_kayma", "bulgu": "S3.1"}]})
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(ku.main(S3), 0)
        d1 = {d["replik"]: d["cizelge_bas"] for d in ko.kurgu_plani(kok)[1]["diyalog"]}
        self.assertAlmostEqual(d1["R0001"], d0["R0001"] - 0.208, places=2)
        self.assertTrue(_j(on).get("uygulandi"))
        with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(ku.main(S3), 0)               # ikinci kez: katlanmaz
        d2 = {d["replik"]: d["cizelge_bas"] for d in ko.kurgu_plani(kok)[1]["diyalog"]}
        self.assertAlmostEqual(d2["R0001"], d1["R0001"], places=3)


class Batlar(unittest.TestCase):
    def test_yeni_batlar_tek_is_ve_yasak_ad_yok(self):
        import bat_yenile as by
        d = by.depo_batlari(python="/usr/bin/python3", araclar="/x/ARACLAR", depo="/x")
        f = by.film_batlari(python="/usr/bin/python3", araclar="/x/ARACLAR", depo="/x")
        for ad, bek in (("KUR3.bat", "bat_isleri.py\" kur3"), ("VIDEO_YARI_OTOMATIK.bat", "bat_isleri.py\" video-yari"),
                        ("VIDEO_TOPLA.bat", "bat_isleri.py\" video-topla")):
            self.assertIn(ad, by.DEPO_KOKU); self.assertIn(bek, d[ad]); self.assertEqual(by.denetle(d[ad]), [])
        for ad in ("VIDEO_YARI_OTOMATIK.bat", "VIDEO_TOPLA.bat"):
            self.assertIn(ad, by.FILM_KLASORU); self.assertIn(ad, by.MASAUSTU); self.assertIn('"%~dp0."', f[ad])
        for m in list(d.values()) + list(f.values()):
            self.assertNotIn("memmet", m.lower()); self.assertNotIn("film.py", m)       # veri_emniyet: eski giriş noktası sayılmaz

    def _film(self, komut=None, durum="hazir"):
        import tempfile
        film = tempfile.mkdtemp(dir=_ortam.VERI)
        if komut: ortak.atomik_yaz(os.path.join(film, "_GOREV", "A14-VG-001", "GOREV.json"),
                                   {"id": "A14-VG-001", "tur": "kullanici", "durum": durum, "komut": komut})
        return film

    def test_video_yari_vg_gorevinin_blogu(self):
        import bat_isleri as bi
        from unittest import mock
        bin_film = os.path.join(ortak.DEPO_KOK, ".claude", "bin", "film.py")
        film = self._film()
        self.assertEqual(bi.video_yari(film, yaz=lambda *_: None), bi.KULLANICI)            # açık VG yok: hiçbir şey açılmaz
        film = self._film([bin_film, "video", "--blok", "KESIT", "--film", "/eski"], durum="bitti")
        self.assertEqual(bi.video_yari(film, yaz=lambda *_: None), bi.KULLANICI)
        film = self._film([bin_film, "video", "--blok", "KESIT", "--film", "/x"])
        with mock.patch("subprocess.call", return_value=0) as c: self.assertEqual(bi.video_yari(film, yaz=lambda *_: None), 0)
        k = c.call_args[0][0]
        self.assertEqual(k[1:], [bin_film, "video", "--film", film, "--blok", "KESIT"])
        film = self._film([bin_film, "video", "--blok", "*", "--film", "/x"])
        with mock.patch("subprocess.call", return_value=7) as c: self.assertEqual(bi.video_yari(film, yaz=lambda *_: None), 7)
        self.assertEqual(c.call_args[0][0][-2:], ["--blok", "*"])                            # Flow kilidi (7) olduğu gibi döner
        with mock.patch("subprocess.call", return_value=0) as c: self.assertEqual(bi.video_topla(film, yaz=lambda *_: None), 0)
        self.assertTrue(c.call_args[0][0][1].endswith("memmet_topla.py")); self.assertEqual(c.call_args[0][0][2], film)

    def test_kur3_soru_sorar_onaysiz_kurmaz(self):
        import bat_isleri as bi, kurulum_kur3 as k3
        from unittest import mock
        plan = {"ortamlar": [{"ad": "musetalk", "hazir": False}], "kart": ["musetalk: çalışmıyor"]}
        with mock.patch.object(k3, "kur3_plani", return_value=plan), mock.patch("subprocess.call", return_value=0) as c:
            self.assertEqual(bi.kur3(sor=lambda _: "", yaz=lambda *_: None), bi.KULLANICI); c.assert_not_called()
            self.assertEqual(bi.kur3(sor=lambda _: "hayır", yaz=lambda *_: None), bi.KULLANICI); c.assert_not_called()
            self.assertEqual(bi.kur3(kuru=True, sor=lambda _: "e", yaz=lambda *_: None), 0); c.assert_not_called()
            self.assertEqual(bi.kur3(sor=lambda _: "E", yaz=lambda *_: None), 0)
            self.assertEqual(c.call_args[0][0][1:], [os.path.join(ortak.ARACLAR, "kurulum.py"), "--kur3", "--onay"])
        with mock.patch.object(k3, "kur3_plani", return_value={"ortamlar": [{"hazir": True}], "kart": []}), \
                mock.patch("subprocess.call") as c:
            self.assertEqual(bi.kur3(sor=lambda _: "e", yaz=lambda *_: None), 0); c.assert_not_called()


class KucukTemizlikler(unittest.TestCase):
    def test_ai84_tts_tohum_ve_komsu_replik_gecer(self):
        import tempfile, ai84, wave
        from unittest import mock
        from saglayicilar import ai84_tts
        s = ai84_tts.AI84Tts(); film = tempfile.mkdtemp(dir=_ortam.VERI); cikti = os.path.join(film, "r.wav")
        def sahte_tts(metin, ses, out, **k):
            with open(out, "wb") as f: f.write(b"mp3")
            return 12
        def sahte_ffmpeg(k, check=True):
            with wave.open(k[-1], "wb") as w: w.setnchannels(1); w.setsampwidth(2); w.setframerate(48000); w.writeframes(b"\0\0" * 4800)
        with mock.patch.object(s, "hazir", return_value=(True, "")), mock.patch.object(ai84, "tts", side_effect=sahte_tts) as t, \
                mock.patch("subprocess.run", side_effect=sahte_ffmpeg):
            r = s.tts(film, "Hold the door.", "v1", cikti, seed=7, onceki="Run!", sonraki="Now.")
        self.assertEqual(t.call_args.kwargs, {"model_id": s.model, "seed": 7, "previous_text": "Run!", "next_text": "Now."})
        self.assertNotIn("gecirilmedi", r); self.assertEqual(r["kredi"], 12)

    def test_izleyici_izin_karari_paylasir(self):
        from unittest import mock
        from saglayicilar import izleyici, gemini_api
        with mock.patch.object(gemini_api, "izin_karari", return_value=(False, "neden-x")) as k:
            self.assertEqual(izleyici.acik_mi(None, "ses"), (False, "neden-x", [])); k.assert_called_with("dinleyici")
        with mock.patch.object(gemini_api, "izin_karari", return_value=(True, "ucretsiz")), \
                mock.patch.object(gemini_api, "o0e", return_value={"gemini_katman": "ucretsiz"}):
            self.assertEqual(izleyici.acik_mi(None), (True, None, []))
        with mock.patch.object(gemini_api, "o0e", return_value={"gemini_katman": "q"}): self.assertEqual(izleyici.o0e(), {"gemini_katman": "q"})

    def test_kaldirilan_yedekler(self):
        import kor_paket_izleme, puan_oku, kalite_denetim, duzeltme, kurgu_ortak, kuyruk, yayin_paketi
        from saglayicilar import yerel_ses
        self.assertFalse(hasattr(kor_paket_izleme, "kapak_kur"))
        self.assertFalse(hasattr(puan_oku, "yerel_kapilar"))
        self.assertEqual(kalite_denetim._kok(), "teknik_kusur"); self.assertTrue(kuyruk.kok_neden_normal("teknik_kusur"))
        self.assertEqual(duzeltme.KOK_NEDEN["teknik"], "gorsel_teknik"); self.assertTrue(kuyruk.kok_neden_normal("gorsel_teknik"))
        self.assertNotIn("faster_whisper", kurgu_ortak.YEREL_KAYIT); self.assertFalse(hasattr(yerel_ses, "FasterWhisper"))
        self.assertEqual(type(kurgu_ortak._yukle("faster_whisper")).__module__, "saglayicilar.asr_whisper")
        self.assertFalse(hasattr(yayin_paketi, "POLITIKA_GUN_MAX"))
        with open(os.path.join(ARACLAR, "kor_paket_izleme.py"), encoding="utf-8") as f: self.assertNotIn("or 0.30", f.read())

    def test_puan_oku_yerel_kapi_raporu_tam_denetim(self):
        import puan_oku, tempfile
        film = tempfile.mkdtemp(dir=_ortam.VERI)
        yol, r = puan_oku.kapi_yaz(film, "KONU", "FILM", [], 1, "A01")            # kâğıt kapısı artık ADLAR'da: denetim atlanmaz
        self.assertTrue(os.path.isfile(yol)); self.assertEqual(r["kapi"], "KONU")

    def test_ritim_esikleri_okunur(self):
        from unittest import mock
        import kanal_teshis as kt, yayin_analiz as ya
        sahte = {"kanal_gosterim_min": 50, "kanal_to_min": 1.0, "kanal_izlenme_min": 10.0, "tutma_dusus_min_puan": 20}
        with mock.patch.dict(kt._RE, {"E": sahte}):
            self.assertEqual(kt.video_teshisi({"gosterim": 60, "to": 2.0, "ort_oran": 12.0}), "sorun görünmüyor")
            self.assertIn("keşif", kt.video_teshisi({"gosterim": 40, "to": 2.0, "ort_oran": 12.0}))
            self.assertEqual(kt.teshis([])["sinirlar"]["gosterim_min"], 50)
            egri = [(0, 100), (20, 95), (30, 80), (60, 78)]
            self.assertEqual(ya.dususler(egri), [])                                   # 15 puanlık düşüş < 20
        with mock.patch.dict(kt._RE, {"E": dict(sahte, tutma_dusus_min_puan=3)}):
            self.assertTrue(ya.dususler([(0, 100), (20, 95), (30, 80), (60, 78)]))
        self.assertEqual(kt.re_esik("kanal_gosterim_min"), 1000)


if __name__ == "__main__":
    unittest.main()
