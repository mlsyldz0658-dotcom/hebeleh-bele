"""Yayın ve öğrenme testi (TASARIM §9 adım 17 / PR-13, §1.3 A17–A18a, §7.2 S8 + YAYIN, §5.3, §5.4, D-24, D-26, D-33, D-40, D-42).

Ağ yok, kredi yok. Medya fikstürleri ffmpeg ile üretilir (ffmpeg yoksa medya testleri atlanır, sebebi yazılır).
  - kalite_denetim --final: −14 LUFS/−1 dBTP, süre ±1 kare, planlı/plansız siyah ve sessizlik, 40 pencere mux korelasyonu, mux kanıtı,
    medya olmayan dosyada ÖLÇÜLEMEDİ (= BAYRAK, asla GEÇ), görev bağlamı (rapor yolu ve _uretim.gorev GOREV.json'dan).
  - yayin_paketi: taslak → doğrulama HATA 0; bozuk paketin her kuralı; "yayına hazır değil" + nedeni; YOUTUBE_METIN.txt.
  - jenerik ≤ jenerik_max_sn; shorts 3 × 9:16 + fragman, S7.9 −14 ±1 LUFS.
  - yayin_analiz CSV: düşüş → plan kimliği → ders kaydı (gercek_seyirci, bir kez); veri yoksa ölçülemedi. kanal_teshis CSV (EN/TR).
  - ders_derle: kümeler, korkuluktan geçmeyen aday reddi (BAYRAK), yaşam döngüsü, FILM_SONU_RAPORU, DERS kapısı.
  - evren --film-sonu (yalnız ekleme, kanon ihlali HATA, tekrar çalıştırma değişiklik yok), --yedekle (kopya; silme yok; AYARLAR
    yedeğe girmez; sha1), --yedek-dogrula, D takılı değil → ertelendi; robocopy komutunda /MIR yok.
"""
import os, sys, json, glob, shutil, unittest, unittest.mock, subprocess, datetime, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak, kapi
import kalite_denetim_final as kdf
import yayin_paketi as yp
import jenerik, shorts_mp4, yayin_analiz, kanal_teshis, ders_derle, evren, evren_film_sonu as efs, ders_yedekle as dy
import ders_defteri as dd

FFMPEG = kdf.ffmpeg_var()
MEDYA = tempfile.mkdtemp(prefix="yz_yayin_medya_")
SURE = 100.0
SERI = "FROSTTEST"


def ff(*a):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-v", "error", "-y", *a], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr


def medya_kur():
    if not FFMPEG or os.path.isfile(os.path.join(MEDYA, "iyi.mp4")): return
    v = ["-f", "lavfi", "-i", f"testsrc2=s=320x180:r=24:d={SURE}", "-f", "lavfi", "-i", f"anoisesrc=d={SURE}:c=pink:r=48000:a=0.3"]
    enc = ["-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000"]
    ff(*v, "-filter_complex", "[1:a]loudnorm=I=-13.2:TP=-2.5:LRA=7,alimiter=limit=0.65:level=disabled[a]", "-map", "0:v", "-map", "[a]", *enc, os.path.join(MEDYA, "iyi.mp4"))
    ff("-i", os.path.join(MEDYA, "iyi.mp4"), "-vn", "-ar", "48000", os.path.join(MEDYA, "master.wav"))
    ff(*v, "-filter_complex", "[1:a]loudnorm=I=-13.2:TP=-2.5:LRA=7,volume=6dB[a]", "-map", "0:v", "-map", "[a]", *enc, os.path.join(MEDYA, "yuksek.mp4"))
    ff(*v, "-filter_complex", "[0:v]drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='between(t,40,43)'[v];"
           "[1:a]loudnorm=I=-13.2:TP=-2.5:LRA=7,alimiter=limit=0.65:level=disabled,volume=enable='between(t,40,43)':volume=0[a]", "-map", "[v]", "-map", "[a]", *enc,
       os.path.join(MEDYA, "siyah.mp4"))
    ff("-i", os.path.join(MEDYA, "siyah.mp4"), "-vn", "-ar", "48000", os.path.join(MEDYA, "siyah_master.wav"))


def yaz(p, v):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if isinstance(v, (dict, list)): ortak.atomik_yaz(p, v)
    else:
        with open(p, "w", encoding="utf-8") as f: f.write(v)


def oku(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


HIKAYE = {
    "_surum": "v3", "kilit": True, "evren": SERI, "film_no": 1, "logline": "A huntress hides a dragon hatchling from the king.",
    "baslik": {"secilen": f"She Hid the Dragon the King Ordered Burned | {SERI} | Full Movie 4K 2026",
               "adaylar": [f"The Last Hatchling | {SERI} | Full Movie 4K 2026"]},
    "vaat_sozlesmesi": [{"oge": "Hid the Dragon", "sahne": "S01", "ekranda": "cloak"}, {"oge": "kapak_imgesi", "sahne": "S02"}],
    "bolum_adlari": [{"bas_sahne": "S01", "ad": "The Light Under the Snow"}, {"bas_sahne": "S02", "ad": "Torches"},
                     {"bas_sahne": "S03", "ad": "The Brother"}],
    "short_adaylari": [{"sahneler": ["S01"], "kanca_2sn": "torches + glowing cloak"}, {"sahneler": ["S02"], "kanca_2sn": "the hunt"},
                       {"sahneler": ["S03"], "kanca_2sn": "a brother's choice"}],
    "seri_kancasi": {"sahne": "S03", "sure_sn": 10, "sonraki_tohum": "He Burned the Village That Hid Her"},
    "karakterler": {"sera": {"ad": "Sera", "rol": "ana", "kostum": {"varsayilan": "k1"}},
                    "brann": {"ad": "Brann", "rol": "karsit", "kostum": {"varsayilan": "k1"}}},
    "mekanlar": [{"id": "kulube", "hikaye_olgulari": ["tek kapı"]}],
}


def kurgu_plani(karartma=False):
    planlar, t = [], 0.0
    for i, (s, d) in enumerate([("S01", 30.0), ("S02", 30.0), ("S03", 40.0)], 1):
        for j in range(2):
            planlar.append({"sira": i * 10 + j, "plan": i * 10 + j, "sahne_grubu": s, "goruntu": {"tur": "video"},
                            "cizelge_bas": t, "sure": d / 2}); t += d / 2
    kp = {"_surum": 7, "kurgu_surumu": 7, "fps": 24, "cizelge": "T2", "planlar": planlar, "kartlar": [],
          "karartmalar": [{"cizelge_bas": 40.0, "sure": 3.0}] if karartma else [], "olcumler": {"toplam_sn": SURE}}
    return kp


class Temel(unittest.TestCase):
    def setUp(self):
        medya_kur()
        self.ad = "T_YAYIN_" + self._testMethodName[-30:]
        self.film = os.path.join(_ortam.VERI, "FILMLER", self.ad)
        shutil.rmtree(self.film, ignore_errors=True)
        yaz(os.path.join(self.film, "HAZIRLIK.json"), {"film": self.ad, "seri": SERI})
        yaz(os.path.join(self.film, "HIKAYE.json"), HIKAYE)
        yaz(os.path.join(self.film, "KURGU", "KURGU_PLANI.json"), kurgu_plani())
        self.env = unittest.mock.patch.dict(os.environ, {"YZ_FILM_GOREV": ""}); self.env.start()

    def tearDown(self): self.env.stop()

    def medya(self, ad, hedef=None):
        if not FFMPEG: self.skipTest("ffmpeg yok (KUR1): medya ölçümü sınanamaz")
        h = os.path.join(self.film, hedef or f"YAYIN/{self.ad}_4K.mp4"); os.makedirs(os.path.dirname(h), exist_ok=True)
        shutil.copy(os.path.join(MEDYA, ad), h); return h

    def maddeler(self, r): return {m["madde"]: m for m in r["hatalar"] + r["bayraklar"]}


class KaliteFinal(Temel):
    def test_iyi_dosya_hata_yok_korelasyon_sifir_ofset(self):
        self.medya("iyi.mp4"); shutil.copy(os.path.join(MEDYA, "master.wav"), os.path.join(self.film, "YAYIN", "ses_master.wav"))
        yol, r = kdf.final(self.film)
        self.assertEqual(r["hatalar"], [], r["hatalar"])
        self.assertEqual(r["sonuc"], "BAYRAK")                     # 320x180 → çözünürlük BAYRAK
        self.assertIn("cozunurluk", self.maddeler(r))
        self.assertTrue(yol.endswith("S8_FINAL_t1.json")); self.assertEqual(kapi.dogrula(oku(yol)), [])
        dv = oku(os.path.join(self.film, "YAYIN", "YAYIN_DOGRULAMA.json"))
        self.assertEqual(dv["sure"]["fark_kare"], 0); self.assertEqual(dv["ses_korelasyon"]["ofset_kare"], {"min": 0, "max": 0})
        self.assertGreaterEqual(dv["ses_korelasyon"]["tepe_min"], 0.9); self.assertNotEqual(dv["sonuc"], "HATA")
        self.assertLessEqual(abs(dv["ses"]["lufs"] + 14), 1.0); self.assertFalse(dv["mux"]["gerekli"])

    def test_yuksek_ses_hata_mux_son_miks_yok(self):
        self.medya("yuksek.mp4"); shutil.copy(os.path.join(MEDYA, "master.wav"), os.path.join(self.film, "YAYIN", "ses_master.wav"))
        _, r = kdf.final(self.film)
        mm = self.maddeler(r)
        self.assertEqual(mm["S8.1_lufs"]["seviye"], "HATA"); self.assertIn(r["sonuc"], ("HATA", "KISMI"))
        dv = oku(os.path.join(self.film, "YAYIN", "YAYIN_DOGRULAMA.json"))
        self.assertTrue(dv["mux"]["gerekli"]); self.assertEqual(dv["sonuc"], "HATA"); self.assertIn("S8.1_lufs", dv["hazir_degil_nedeni"])
        self.assertFalse(dv["mux"]["yapildi"])                    # son_miks.py (PR-9) yoksa mux yapılmaz, kör karıştırma yok
        self.assertTrue(any(k in mm for k in ("mux", "mux_kaniti")))

    def test_kullanici_ses_duzenlemesi_mux_dogrusal_kazanc_yapilir(self):
        if kdf.son_miks_modulu() is None: self.skipTest("son_miks.py (PR-9) yok ya da açılamıyor")
        self.medya("yuksek.mp4")
        yaz(os.path.join(self.film, "KURGU", "TASLAK_FARK.json"), {"geri_uretilemeyen": [{"kanal": "Muzik", "tur": "ses_ayari"}]})
        _, r = kdf.final(self.film); mm = self.maddeler(r)
        dv = oku(os.path.join(self.film, "YAYIN", "YAYIN_DOGRULAMA.json"))
        self.assertTrue(dv["mux"]["yapildi"]); self.assertEqual(dv["mux"]["tur"], "dogrusal_kazanc")
        self.assertTrue(dv["dosya"].endswith("_4K_MUX.mp4")); self.assertTrue(os.path.isfile(os.path.join(self.film, "YAYIN", f"{self.ad}_4K.mp4")))
        self.assertNotIn("S8.1_lufs", mm); self.assertNotIn("S8.2_kullanici_sesi", {m["madde"] for m in r["hatalar"]})
        self.assertLessEqual(abs(dv["mux"]["sonra_lufs"] + 14), 1.0)

    def test_kullanici_ses_duzenlemesi_dogrusal_kazanc(self):
        yaz(os.path.join(self.film, "KURGU", "TASLAK_FARK.json"), {"geri_uretilemeyen": [{"kanal": "Muzik", "tur": "ses_ayari"}]})
        self.assertTrue(kdf.kullanici_ses_duzenlemesi(self.film))
        self.assertEqual(kdf.mux_karari({"kullanici_ses_duzenlemesi": True})[0], "dogrusal_kazanc")
        self.assertEqual(kdf.mux_karari({"_korelasyon_gec": True})[0], "master_stem")
        self.assertIsNone(kdf.mux_karari({})[0])

    def test_plansiz_siyah_ve_sessizlik_hata_planli_gecer(self):
        self.medya("siyah.mp4"); shutil.copy(os.path.join(MEDYA, "siyah_master.wav"), os.path.join(self.film, "YAYIN", "ses_master.wav"))
        _, r = kdf.final(self.film); mm = self.maddeler(r)
        self.assertEqual(mm["siyah"]["seviye"], "HATA"); self.assertEqual(mm["sessizlik_uzun"]["seviye"], "HATA")
        yaz(os.path.join(self.film, "KURGU", "KURGU_PLANI.json"), kurgu_plani(karartma=True))
        _, r = kdf.final(self.film); mm = self.maddeler(r)
        self.assertNotIn("siyah", mm); self.assertNotIn("sessizlik_uzun", mm); self.assertNotIn("sessizlik_sayisi", mm)

    def test_sure_farki_hata(self):
        self.medya("iyi.mp4"); kp = kurgu_plani(); kp["olcumler"]["toplam_sn"] = SURE + 1.0
        yaz(os.path.join(self.film, "KURGU", "KURGU_PLANI.json"), kp)
        _, r = kdf.final(self.film)
        self.assertEqual(self.maddeler(r)["sure"]["seviye"], "HATA"); self.assertEqual(self.maddeler(r)["sure"]["olcu"], 24)

    def test_medya_olmayan_dosya_olculemedi_gec_degil(self):
        yaz(os.path.join(self.film, "YAYIN", f"{self.ad}_4K.mp4"), "SAHTE\n")
        _, r = kdf.final(self.film)
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertTrue(all(b.get("olculemedi") for b in r["bayraklar"]))

    def test_dosya_yok_hata_ve_gorev_baglami(self):
        gd = os.path.join(self.film, "_GOREV", "A17-KF-001"); yaz(os.path.join(gd, "GOREV.json"),
                                                                    {"id": "A17-KF-001", "tur_no": 2, "asama": "A17", "rapor": "_RAPOR/S8_FINAL_t2.json"})
        with unittest.mock.patch.dict(os.environ, {"YZ_FILM_GOREV": gd}):
            self.assertEqual(kdf.main(["--final", "--film", self.film]), 0)
        r = oku(os.path.join(self.film, "_RAPOR", "S8_FINAL_t2.json"))
        self.assertEqual(r["_uretim"]["gorev"], "A17-KF-001"); self.assertEqual(r["tur"], 2); self.assertEqual(r["sonuc"], "HATA")
        self.assertEqual(kdf.main(["--film", self.film]), 4)


class YayinPaketi(Temel):
    def hazirla(self):
        yaz(os.path.join(self.film, "YAYIN", "YAYIN_DOGRULAMA.json"), {"_surum": 1, "sonuc": "BAYRAK"})
        yaz(os.path.join(self.film, "YAYIN", "kapak_1.jpg"), "jpg")
        yaz(os.path.join(_ortam.VERI, "BILGI", "YOUTUBE_POLITIKA.md"), "# politika\n")
        self.assertEqual(yp.main(["--taslak", "--film", self.film]), 0)
        return oku(os.path.join(self.film, "YAYIN", "PAKET_TASLAK.json"))

    def test_taslak_dogrulamadan_hatasiz_gecer(self):
        p = self.hazirla()
        self.assertEqual([b["zaman"] for b in p["bolumler"]], ["00:00", "00:30", "01:00"])
        self.assertTrue(yp.BASLIK_KALIBI.match(p["baslik"])); self.assertTrue(p["yz_beyani"]["sentetik_icerik"])
        self.assertEqual(len(p["shorts"]), 3); self.assertTrue(all(30 <= s["bit"] - s["bas"] <= 60 for s in p["shorts"]))
        self.assertIn("00:30 Torches", p["aciklama"]); self.assertIn(p["yz_beyani"]["metin"], p["aciklama"])
        yaz(os.path.join(self.film, "YAYIN", "PAKET.json"), p)
        yol, r = yp.paket_dogrula(self.film)
        self.assertEqual(r["hatalar"], [], r["hatalar"]); self.assertTrue(r["yayina_hazir"])
        self.assertTrue(yol.endswith("YAYIN_PAKET_t1.json")); self.assertEqual(kapi.dogrula(oku(yol)), [])
        with open(os.path.join(self.film, "YAYIN", "YOUTUBE_METIN.txt"), encoding="utf-8") as f: t = f.read()
        self.assertIn("Altered or synthetic content", t); self.assertNotIn("HAZIR DEĞİL", t)

    def test_bozuk_paket_kurallari(self):
        p = self.hazirla()
        p.update(baslik="Kill " + "x" * 110, bolumler=[{"zaman": "00:05", "ad": "A"}, {"zaman": "00:10", "ad": ""}], yz_beyani=None,
                 etiketler=[], politika_kontrol=[{"madde": "yaniltici_meta_veri", "durum": "ihlal"}],
                 shorts=[{"bas": 0, "bit": 20}], vaat_sozlesmesi=[{"oge": "Dragon", "sahne": "S99"}])
        p["aciklama"] = "kısa <script>"
        yaz(os.path.join(self.film, "YAYIN", "PAKET.json"), p)
        _, r = yp.paket_dogrula(self.film); h = {m["madde"] for m in r["hatalar"]}; b = {m["madde"] for m in r["bayraklar"]}
        for x in ("baslik_uzunluk", "bolum_ilk", "bolum_sayisi_min", "bolum_bicim", "yz_beyani", "etiketler", "aciklama_karakter",
                  "short_sure", "vaat_sahnesi", "politika_ihlal", "bolum_aciklamada"):
            self.assertIn(x, h)
        for x in ("kill", "baslik_kalibi", "baslik_aday", "short_sayisi", "short_kanca", "politika_eksik"): self.assertIn(x, b)
        self.assertFalse(r["yayina_hazir"]); self.assertIn("yz_beyani", r["hazir_degil_nedeni"])
        with open(os.path.join(self.film, "YAYIN", "YOUTUBE_METIN.txt"), encoding="utf-8") as f: self.assertIn("HAZIR DEĞİL", f.read())

    def test_final_kalite_hatasi_paketi_hazir_degil_yapar(self):
        p = self.hazirla(); yaz(os.path.join(self.film, "YAYIN", "PAKET.json"), p)
        yaz(os.path.join(self.film, "YAYIN", "YAYIN_DOGRULAMA.json"), {"sonuc": "HATA", "hazir_degil_nedeni": "S8.1_lufs"})
        _, r = yp.paket_dogrula(self.film)
        self.assertFalse(r["yayina_hazir"]); self.assertIn("final_kalite", r["hazir_degil_nedeni"])

    def test_paket_yok_hata(self):
        _, r = yp.paket_dogrula(self.film); self.assertEqual(r["sonuc"], "HATA")

    def test_zaman_cevirileri(self):
        self.assertEqual(yp.zaman_metni(3725), "1:02:05"); self.assertEqual(yp.zaman_sn("1:02:05"), 3725)
        self.assertEqual(yp.zaman_sn("00:30"), 30); self.assertIsNone(yp.zaman_sn("a:b"))


class JenerikShorts(Temel):
    def test_jenerik_sure_tavani(self):
        if not FFMPEG: self.skipTest("ffmpeg yok")
        try: import PIL  # noqa
        except ImportError: self.skipTest("Pillow yok")
        j = jenerik.uret(self.film, "320x180", 75)
        mx = jenerik.esik("jenerik_max_sn", 60)
        self.assertEqual(j["sure_sn"], mx); self.assertTrue(j["notlar"])
        mp4 = os.path.join(self.film, j["dosyalar"]["mp4"]); self.assertAlmostEqual(kdf.sure_fps(mp4)["sure"], mx, delta=0.2)
        self.assertIn("Sera", [s["metin"] for s in j["satirlar"]])
        self.assertTrue(any("synthetic" in s["metin"] for s in j["satirlar"]))

    def test_shorts_dikey_ve_ses(self):
        self.medya("iyi.mp4")
        yaz(os.path.join(self.film, "YAYIN", "PAKET.json"), yp.taslak(self.film))
        k, r = shorts_mp4.uret(self.film, "180x320")
        self.assertEqual(r["hatalar"], [], r["hatalar"])
        self.assertEqual(len([s for s in k["shorts"] if s.get("dosya")]), 3)
        for s in k["shorts"]:
            b = kdf.sure_fps(os.path.join(self.film, s["dosya"]))
            self.assertEqual((b["genislik"], b["yukseklik"]), (180, 320)); self.assertGreaterEqual(b["sure"], 29.9)
            self.assertLessEqual(abs(s["ses"]["lufs"] + 14), 1.0); self.assertLessEqual(s["ses"]["tepe_dbtp"], -1.0)
        f = kdf.sure_fps(os.path.join(self.film, k["fragman"]["dosya"])); self.assertEqual((f["genislik"], f["yukseklik"]), (320, 180))

    def test_shorts_sahte_olculemedi(self):
        yaz(os.path.join(self.film, "YAYIN", f"{self.ad}_4K.mp4"), "SAHTE\n")
        k, r = shorts_mp4.uret(self.film)
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertFalse(any(s.get("dosya") for s in k["shorts"]))


class AnalizTeshis(Temel):
    def test_yayin_analiz_dusus_plana_ve_derse(self):
        rows = ["Video position (%),Absolute audience retention (%)"]
        for i in range(0, 101):
            y = 100 - i * 0.2 - (15 if i >= 52 else 0)          # 50–52. yüzde (≈ 51 sn) 15 puan düşüş
            rows.append(f"{i},{y:.1f}")
        yaz(os.path.join(self.film, "GELENLER", "YOUTUBE", "tutma.csv"), "\n".join(rows) + "\n")
        yaz(os.path.join(self.film, "GELENLER", "YOUTUBE", "ozet.csv"),
            "Content,Video title,Impressions,Impressions click-through rate (%),Views\nTotal,,5000,2.1,105\n")
        yaz(os.path.join(_ortam.VERI, "BILGI", "KANAL_TESHIS.json"), {"kanal_ortalama": {"to": 4.5, "ilk30_tutma": 99.0}})
        uc_gun = (datetime.datetime.now().astimezone() - datetime.timedelta(days=3)).isoformat()
        r = yayin_analiz.analiz(self.film, tarih=uc_gun)
        self.assertEqual(r["gun"], 2); self.assertEqual(r["sonuc"], "tamam")
        self.assertTrue(any(40 <= d["sn"] <= 52 and d["plan"] == 21 for d in r["dususler"]), r["dususler"])
        self.assertEqual(len(r["erken_uyari"]), 2); self.assertTrue(r["ders_kayitlari"])
        ham = [d for d in dd.ham_oku() if d.get("film") == self.ad and d["olay"] == "gercek_seyirci"]
        self.assertEqual(ham[0]["kaynak"], "gercek_seyirci")
        r2 = yayin_analiz.analiz(self.film, tarih=uc_gun); self.assertEqual(r2["ders_kayitlari"], [])   # aynı gün için bir kez

    def test_yayin_analiz_veri_yok_olculemedi(self):
        self.assertEqual(yayin_analiz.main(["--gun", "7", "--film", self.film]), 0)
        r = oku(os.path.join(self.film, "_RAPOR", "YAYIN_ANALIZ_7.json")); self.assertEqual(r["sonuc"], "olculemedi")
        self.assertIsNone(yayin_analiz.gun_sec(self.film)); self.assertEqual(yayin_analiz.main(["--gun", "5", "--film", self.film]), 4)

    def test_kanal_teshis_csv(self):
        k = os.path.join(_ortam.VERI, "GELENLER", "KANAL_T"); shutil.rmtree(k, ignore_errors=True)
        yaz(os.path.join(k, "en.csv"), "Content,Video title,Impressions,Impressions click-through rate (%),Views,Average percentage viewed (%)\n"
                                        "Total,,9000,3.0,500,25\nabc,B1 film,8000,2.5,400,22\nxyz,B2 film,1000,6.0,100,45\n")
        yaz(os.path.join(k, "tr.csv"), "Video başlığı;Gösterimler;Gösterim tıklama oranı (%);Görüntüleme;Ortalama izlenme yüzdesi (%)\n"
                                        "B3 film;1.200;3,5;80;28,5\n")
        self.assertEqual(kanal_teshis.main(["--klasor", k]), 0)
        t = oku(os.path.join(_ortam.VERI, "BILGI", "KANAL_TESHIS.json"))
        self.assertEqual(t["video_sayisi"], 3); self.assertEqual(t["genel_teshis"], "paketleme")
        b3 = next(v for v in t["videolar"] if v["baslik"] == "B3 film"); self.assertEqual((b3["gosterim"], b3["to"], b3["ort_oran"]), (1200, 3.5, 28.5))
        self.assertEqual(kanal_teshis.sayi("1.234,5"), 1234.5); self.assertEqual(kanal_teshis.sure_sn("1:02:03"), 3723)
        self.assertEqual(kanal_teshis.teshis([])["genel_teshis"], "ölçülemedi")


class Dersler(Temel):
    def setUp(self):
        super().setUp()
        self.bilgi = os.path.join(_ortam.KOK, "BILGI_" + self._testMethodName[-20:]); shutil.rmtree(self.bilgi, ignore_errors=True)

    def test_derle_film_sonu_kapisi(self):
        ids = [os.path.basename(dd.kaydet("kapi_hatasi", "kapi", "cradle filtreye takıldı", film=f, asama="A14", kapi="V1",
                                          madde="filtre", kategori="filtre_red", rol_etiketi="goruntu", bilgi=self.bilgi))
               for f in (self.ad, self.ad, "ESKI_F1")]
        hamlar = dd.ham_oku(self.bilgi); kimlik = [d["id"] for d in hamlar]
        ders_derle.derle(self.film, self.bilgi, {"id": "A18-DD-001", "tur_no": 1, "asama": "A18", "rapor": None})
        k = oku(os.path.join(self.film, "_RAPOR", "DERS_KUMELERI.json"))
        self.assertEqual(k["kume_sayisi"], 1); self.assertEqual(k["kumeler"][0]["sayi"], 3)
        self.assertEqual(sorted(k["kumeler"][0]["filmler"]), sorted([self.ad, "ESKI_F1"]))
        dd.ogrenilen_yaz({"kurallar": [{"id": "OK-0001", "tur": "istem_eki", "deger": "the empty hand rests at her side", "durum": "deneme",
                                       "destek": 3, "karsi": 0, "filmler": ["ESKI_F1", "ESKI_F2"], "rol_etiketi": "goruntu",
                                       "deneme": {"basari": 3, "toplam": 4, "baslangic_film": "ESKI_F1"}}]},
                         dd.ogrenilen_yolu(self.bilgi))
        yaz(os.path.join(self.film, "_RAPOR", "DERS_ADAY.json"), {"kurallar": [
            {"tur": "filtre_kelimesi", "deger": "cradle", "seviye": "HATA", "kanit": kimlik, "rol_etiketi": "goruntu"},
            {"tur": "plan_kurali", "deger": "uyarıda sayfayı yenile ve devam et", "kanit": kimlik[:1]},
            {"tur": "tempo", "deger": {"bekleme_sn": 1}, "kanit": kimlik[:1]}]})
        kapi.kaydet(os.path.join(self.film, "_RAPOR"), "G1", "P1_B1", [{"madde": "el_nesne", "plan": 214, "seviye": "HATA"},
                                                                       {"madde": "kimlik", "plan": 215, "seviye": "OLCULEMEDI"}],
                    tur=1, asama="A11", gorev="A11-G1-001")
        yol, r = ders_derle.film_sonu(self.film, self.bilgi, {"id": "A18-DF-001", "tur_no": 1, "asama": "A18", "rapor": "_RAPOR/DERS_t1.json"})
        self.assertTrue(yol.endswith("DERS_t1.json")); self.assertEqual(r["sonuc"], "BAYRAK"); self.assertEqual(r["reddedilen"], 2)
        self.assertEqual(r["_uretim"]["gorev"], "A18-DF-001")
        ogr = dd.ogrenilen_oku(dd.ogrenilen_yolu(self.bilgi)); kur = {x["id"]: x for x in ogr["kurallar"]}
        self.assertEqual(kur["OK-0001"]["durum"], "aktif")
        yeni = next(x for x in ogr["kurallar"] if x["deger"] == "cradle")
        self.assertEqual((yeni["durum"], yeni["destek"], len(yeni["filmler"])), ("deneme", 3, 2))
        self.assertFalse(any("yenile" in json.dumps(x, ensure_ascii=False) for x in ogr["kurallar"]))
        self.assertEqual(dd.ogrenilen_denetle(ogr), [])
        with open(os.path.join(self.bilgi, "DERSLER_AKTIF.md"), encoding="utf-8") as f: md = f.read()
        self.assertIn("OK-0001 · istem_eki", md); self.assertIn('"cradle" · deneme · kanıt 3/0', md)
        with open(os.path.join(self.film, "FILM_SONU_RAPORU.md"), encoding="utf-8") as f: fs = f.read()
        self.assertIn("el_nesne · plan 214", fs); self.assertIn("G1 P1_B1: kimlik", fs); self.assertIn("M17", fs)

    def test_yasam_dongusu_pasif_ve_hikaye_iki_film(self):
        o = {"kurallar": [{"id": "OK-0002", "tur": "istem_kalibi", "deger": "x", "durum": "deneme", "destek": 1, "karsi": 2},
                          {"id": "OK-0003", "tur": "plan_kurali", "deger": "y", "durum": "deneme", "destek": 6, "karsi": 0,
                           "filmler": ["F1"], "rol_etiketi": "hikaye"}]}
        v, red, deg = ders_derle.yasam_dongusu(o, [], [], "F9")
        k = {x["id"]: x["durum"] for x in v["kurallar"]}
        self.assertEqual(k, {"OK-0002": "pasif", "OK-0003": "deneme"})


class Evren(Temel):
    def setUp(self):
        super().setUp()
        shutil.rmtree(evren.seri_yolu(SERI), ignore_errors=True)
        r, kod = evren.on_kayit(self.film, SERI); self.assertEqual(kod, 0, r)
        self.hedef = os.path.join(_ortam.KOK, "YEDEK_" + self._testMethodName[-20:]); shutil.rmtree(self.hedef, ignore_errors=True)

    def test_film_sonu_yalniz_ekler_ve_tekrar_degismez(self):
        yaz(os.path.join(self.film, "YAYIN", "PAKET.json"), {"baslik": HIKAYE["baslik"]["secilen"]})
        yaz(os.path.join(self.film, "_HIKAYE_ODASI", "EVREN_TASLAK.json"),
            {"kanon_ekle": [{"olgu": "Sera yavruyu kurtardı", "sahne": "S03"}], "karakterler": {"brann": {"durum": "olu", "yay": "ihanet"}}})
        yaz(os.path.join(self.film, "DUNYA_DEFTERI.json"), {"son_durum": {"sera": {"kostum": "k1_yirtik"}}})
        r, kod = efs.film_sonu(self.film); self.assertEqual(kod, 0, r)
        self.assertIn("hikaye.json", r["degisen"]); self.assertIn("DURUM_SON.json", r["degisen"])
        hs = oku(evren.seri_yolu(SERI, "hikaye.json"))
        self.assertEqual(hs["kanon"][0]["olgu"], "Sera yavruyu kurtardı")
        self.assertEqual(hs["seri_sorulari"][0]["soru"], "He Burned the Village That Hid Her")
        self.assertEqual(hs["baslik_gecmisi"][0]["film"], self.ad)
        self.assertEqual(oku(evren.seri_yolu(SERI, "karakterler", "brann", "hikaye.json"))["durum"], "olu")
        self.assertIn(self.ad, oku(evren.seri_yolu(SERI, "evren.json"))["film_sonu"])
        self.assertEqual(efs.film_sonu(self.film)[0]["degisen"], [])
        self.assertTrue(glob.glob(evren.seri_yolu(SERI, "hikaye_v*.json")))      # eski hâl silinmedi
        yaz(os.path.join(self.film, "_HIKAYE_ODASI", "EVREN_TASLAK.json"), {"kanon": [], "karakterler": {"brann": {"durum": "yasiyor"}}})
        once = oku(evren.seri_yolu(SERI, "hikaye.json"))
        r, kod = efs.film_sonu(self.film); self.assertEqual(kod, 1)
        self.assertEqual(len(r["hatalar"]), 2); self.assertEqual(oku(evren.seri_yolu(SERI, "hikaye.json")), once)

    def test_yedek_kopya_silmez_ayarlar_girmez_sha1(self):
        yaz(evren.seri_yolu(SERI, "AYARLAR", "anahtar.txt"), "x")
        yaz(os.path.join(self.hedef, "EVREN", SERI, "eski_fazla.txt"), "kalmalı")
        dd.kaydet("arac_hatasi", "ajan", "deneme kaydı", film=self.ad)
        self.assertEqual(efs.main(["--yedekle", "--film", self.film, "--hedef", self.hedef]), 0)
        y = os.path.join(self.hedef, "EVREN", SERI)
        self.assertTrue(os.path.isfile(os.path.join(y, "evren.json"))); self.assertFalse(os.path.exists(os.path.join(y, "AYARLAR")))
        self.assertTrue(os.path.isfile(os.path.join(y, "eski_fazla.txt")))
        lst = oku(os.path.join(y, dy.LISTE_ADI))["dosyalar"]; self.assertEqual(lst, dy.sha1_listesi(evren.seri_yolu(SERI)))
        self.assertTrue(glob.glob(os.path.join(self.hedef, "DERSLER", "ham", "*.json")))
        self.assertEqual(efs.yedek_dogrula(SERI, self.hedef)["durum"], "ayni")
        yaz(evren.seri_yolu(SERI, "yeni.json"), {"a": 1})
        r = efs.yedek_dogrula(SERI, self.hedef, yenile=True); self.assertEqual(r["durum"], "fark")
        self.assertEqual(efs.yedek_dogrula(SERI, self.hedef)["durum"], "ayni")
        durum = oku(os.path.join(_ortam.VERI, "HESAP", "YEDEK_DURUMU.json")); self.assertEqual(durum[f"evren/{SERI}"]["durum"], "tamam")

    def test_d_takili_degil_ertelenir(self):
        yok = os.path.join(_ortam.KOK, "TAKILI_DEGIL", "YEDEK")
        self.assertEqual(efs.main(["--yedekle", "--seri", SERI, "--hedef", yok]), 0)
        self.assertFalse(os.path.exists(yok))
        self.assertEqual(oku(os.path.join(_ortam.VERI, "HESAP", "YEDEK_DURUMU.json"))[f"evren/{SERI}"]["durum"], "ertelendi")

    def test_robocopy_mir_yok(self):
        gorulen = []; os.makedirs(self.hedef, exist_ok=True)
        with unittest.mock.patch.object(dy.subprocess, "run", lambda k, **_: gorulen.append(k) or subprocess.CompletedProcess(k, 1)):
            r = dy.kopya_yedek(evren.seri_yolu(SERI), os.path.join(self.hedef, "R"), robocopy=True)
        self.assertTrue(gorulen and gorulen[0][0] == "robocopy" and "/E" in gorulen[0])
        self.assertFalse({"/MIR", "/MOVE", "/PURGE", "/MOV"} & {x.upper() for x in gorulen[0]})
        self.assertEqual(r["durum"], "hata")                       # sahte robocopy dosya kopyalamadı → sha1 farkı HATA

    def test_ders_yedekle_cli(self):
        dd.kaydet("arac_hatasi", "ajan", "cli kaydı", film=self.ad)
        self.assertEqual(dy.main(["--hedef", self.hedef]), 0)
        self.assertEqual(dy.ders_dogrula(self.hedef)["durum"], "ayni")
        self.assertEqual(dy.main(["--bilinmeyen"]), 4)


if __name__ == "__main__":
    unittest.main()
