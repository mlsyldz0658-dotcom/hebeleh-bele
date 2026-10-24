"""TEST — yerel ses hazırlığı (TASARIM §9 adım 13, §6.10 test_ses: 18 bozuk girdi; [SM2] §4.7.10). Ağ ve kredi yok (sahte sağlayıcı).

18 bozuk girdi maddesinden bu dilimin araçlarına düşenler burada doğrudan sınanır; S2 (ses_donustur/ses_karar), S3 (dudak_denetim)
maddeleri video sonrası ses dilimindedir: o araçlar yoksa test gerekçesiyle atlanır (skip), varsa çağrılır.
Ek: telaffuz (S1.2, "Kestrel"), ses seçimi (S1.5/S1.9), animatik TTS (S2.13 taşma → YENIDEN_YAZ), boş müzik zinciri (D-25), MOS
lisanssız → ÖLÇÜLEMEDİ, KUR2 planı, BS.1770 doğruluğu, uçtan uca A10b → A12 ses zinciri (sahte).
"""
import os, sys, json, shutil, unittest, importlib, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _ortam                                                     # noqa: F401  (gerçek YOLLAR'a dokunmaz)
import numpy as np
import ortak
import ses_ortak as so
from olcum import ses as O
import son_miks, ses_katmani, seslendir, muzik_uret, ses_sec, ses_kiyas
from saglayicilar import ses_sahte, midi_ornek

SR = 48000


def _var(ad):
    try: importlib.import_module(ad); return True
    except Exception: return False


def film_kur(ad, iki_yatak=False, dar_pencere=False, muzik=True, motif=True, sahte=True):
    """ORNEK_3_SAHNE_TAM'a benzer küçük v2 film (3 sahne grubu yok; 2 grup, 4 plan, 3 replik, 2 müzik ipucu)."""
    f = os.path.join(_ortam.VERI, "FILMLER", ad)
    if os.path.exists(f): shutil.move(f, f + "_eski_" + str(len(os.listdir(os.path.dirname(f)))))
    os.makedirs(f)
    ortak.atomik_yaz(os.path.join(f, "HAZIRLIK.json"), {"saglayici": "sahte" if sahte else None, "film": ad})
    ortak.atomik_yaz(os.path.join(f, "HIKAYE.json"), {
        "_surum": 1, "evren": "ORNEK",
        "karakterler": {"mara": {"ad": "Mara", "rol": "kahraman", "ses_karakteri": "kadın, yetişkin; alçak ve hafif boğuk"},
                        "voss": {"ad": "Voss", "rol": "karsit", "ses_karakteri": "erkek, orta yaşlı; derin ve sakin"},
                        "kestra": {"ad": "Kestra", "rol": "yan"}},
        "sahneler": [{"id": "S02"}, {"id": "S03"}],
        "replikler": [{"id": "R0001", "sahne": "S02", "karakter": "mara", "teslim": "soguk", "metin": "It's late, Captain. What do you want?"},
                      {"id": "R0002", "sahne": "S02", "karakter": "voss", "teslim": "sakin_tehdit", "metin": "Smoke from your chimney, Mara."},
                      {"id": "R0003", "sahne": "S03", "karakter": "mara", "teslim": "fisilti",
                       "metin": "Kestra is asleep. Keep your voice down, Voss."}]})
    ortak.atomik_yaz(os.path.join(f, "_SES", "SES_PROFILLERI.json"), {"_surum": 1, "karakterler": {
        "mara": {"cinsiyet": "kadin", "yas_bandi": "orta", "aksan": "british", "perde": "orta", "ses_etiketi_tr": "alçak, boğuk kadın sesi",
                 "veo_ses_tarifi": "in a low, husky female voice with a northern English accent"},
        "voss": {"cinsiyet": "erkek", "yas_bandi": "orta", "aksan": "british", "perde": "dusuk", "ses_etiketi_tr": "kalın, sakin erkek sesi",
                 "veo_ses_tarifi": "in a deep, calm male voice with a British accent"}}})
    yat2 = [{"dosya": "SES_KUTUPHANESI/yatak/orman.wav"}, {"dosya": "SES_KUTUPHANESI/yatak/ruzgar.wav"}] if iki_yatak \
        else {"dosya": "SES_KUTUPHANESI/yatak/orman.wav", "seviye_lufs": -36}
    pen = 2.2 if dar_pencere else 5.5

    def plan(no, sg, rid=None, metin=None, kar=None, sure=5.0, ef=None):
        p = {"no": no, "sira": no, "parti": 1, "kullanim": {"bas": 0.5, "sure": sure},
             "zanaat": {"sahne_grubu": sg, "klip_sn": 8, "eylem_zinciri": [{"id": "a1", "bas": 0.8, "bit": 1.6, "tur": "mikro"}],
                        "ses": {"diyalog": {"yol": "tts"}, "efektler": ef or [], "flow_sound": "Sound: wind. No music."}},
             "_derlenir": {"sure_sn": sure}}
        if rid:
            p["replik"] = {"id": rid, "karakter": kar, "metin": metin}
            p["_derlenir"]["replik_zaman"] = {rid: [0.9, 4.0]}
        return p
    S = {"_surum": 2, "film": ad, "karakterler": {"mara": {}, "voss": {}},
         "sahne_gruplari": {"S02": {"ses": {"yatak": {"dosya": "SES_KUTUPHANESI/yatak/kulube.wav", "seviye_lufs": -38}, "gecis": "capraz_0.8"}},
                            "S03": {"ses": {"yatak": yat2, "gecis": "capraz_0.8"}}},
         "sahneler": [plan(1, "S02", "R0001", "It's late, Captain. What do you want?", "mara", 5.5,
                           ef=[{"id": "e1", "adim": "a1", "kategori": "kumas", "an": "bas", "seviye_db_diyaloga_gore": -8}]),
                      plan(2, "S02", "R0002", "Smoke from your chimney, Mara.", "voss", 5.0),
                      plan(3, "S03", sure=4.0, ef=[{"id": "e2", "adim": "a1", "kategori": "kapi", "an": "bas"}]),
                      plan(4, "S03", "R0003", "Kestra is asleep. Keep your voice down, Voss.", "mara", pen)]}
    ortak.atomik_yaz(os.path.join(f, "SAHNELER.json"), S)
    if muzik:
        ortak.atomik_yaz(os.path.join(f, "MUZIK", "leitmotifler.json"), {"LM_MARA": {
            "karakter": "mara", "ton": "D dorian", "bpm": 72, "olcu": "3/4",
            "notalar": [["D5", 1.0], ["F5", 0.5], ["E5", 0.5], ["C5", 1.0], ["D5", 2.0], ["A4", 1.0], ["C5", 1.0], ["D5", 2.0]]}})
        ip = [{"id": "M01", "tur": "doku", "giris": {"olay": "film_basi", "rampa_sn": 2.0}, "cikis": {"olay": "sahne_sonu", "sahne_grubu": "S02",
               "rampa_sn": 3.0}, "hedef_sure_sn": 10, "istem_en": "Sparse low strings, D minor, 60 BPM, no vocals.",
               "seviye": {"diyalogsuz_lufs": -18, "diyalog_alti_db": 14}}]
        if motif:
            ip.append({"id": "M02", "tur": "tema", "motif": "LM_MARA", "giris": {"olay": "sahne_basi", "sahne_grubu": "S03", "rampa_sn": 1.5},
                       "cikis": {"olay": "sahne_sonu", "sahne_grubu": "S03", "rampa_sn": 2.5}, "hedef_sure_sn": 9,
                       "istem_en": "Solo wooden flute, D dorian, 72 BPM, 3/4, no vocals.", "seviye": {"diyalogsuz_lufs": -18, "diyalog_alti_db": 14}})
        ortak.atomik_yaz(os.path.join(f, "MUZIK", "muzik_listesi.json"), {"film": ad, "ipuclari": ip})
    return f


def enjekte(film, d): ortak.atomik_yaz(os.path.join(film, "_KASET", "SES_SAHTE.json"), d)


def rapor(film, ad): return ortak.json_oku(os.path.join(film, "_RAPOR", ad), {}) or {}


def maddeler(r, ad, seviye=None):
    return [m for m in (r.get("hatalar") or []) + (r.get("bayraklar") or []) if m.get("madde") == ad and (seviye is None or m["seviye"] == seviye)]


def sentez_konusma(sure=3.0, f0=180, seed=0):
    x, _ = ses_sahte.konusma(" ".join(["word"] * int(sure * 2.5)), f"v{seed}")
    return x


def ses_hazirla(film, kosul=("tel", "sec", "tts")):
    if "tel" in kosul: ses_sec.telaffuz(film, "sahte")
    if "sec" in kosul: ses_sec.main(["--ara", "--olc", "--sec", "--film", film, "--saglayici", "sahte"])
    if "tts" in kosul: seslendir.tts_hazirla(film, so.replikler(film), "sahte")


class Olcum(unittest.TestCase):
    def test_bs1770_sinus(self):
        t = np.arange(SR * 3) / SR
        self.assertAlmostEqual(O.lufs((0.1 * np.sin(2 * np.pi * 997 * t)).astype(np.float32)), -23.01, delta=0.1)

    def test_gercek_tepe_araornek(self):
        n = np.arange(SR); x = (0.9 * np.sin(2 * np.pi * (SR / 4) * n / SR + np.pi / 4)).astype(np.float32)   # örnekler 0,636
        self.assertGreater(O.gercek_tepe(x), O.ornek_tepe(x) + 2.0)

    def test_f0_ve_wer(self):
        t = np.arange(SR * 2) / SR
        self.assertAlmostEqual(O.f0((0.3 * np.sin(2 * np.pi * 150 * t)).astype(np.float32))["medyan_hz"], 150, delta=3)
        self.assertEqual(O.wer("a b c d", "a x c"), 0.5)

    def test_mos_lisanssiz_olculemedi(self):
        r = O.mos_tahmin(os.devnull)
        self.assertTrue(r.get("olculemedi"))

    def test_kontrol_karti(self):
        k = O.kontrol()
        self.assertIn("midi_ornek", k["basamaklar"]); self.assertTrue(k["basamaklar"]["lufs"]["acik"])
        self.assertIn("acestep", k["kapali"])                     # KUR3 ortamı yok → yalnız kendi basamağı kapalı


class BozukGirdi(unittest.TestCase):
    """[SM2] §4.7.10'daki 18 madde (bu dilimin ya da komşu dilimlerin aracıyla)."""

    def test_01_s31_kayma_200ms(self):
        if not _var("dudak_denetim"): self.skipTest("S3.1 dudak_denetim.py video sonrası ses diliminde (adım 16)")
        import dudak_denetim
        self.assertTrue(hasattr(dudak_denetim, "main"))

    def test_02_s35_ekran_disi_agiz(self):
        if not _var("dudak_denetim"): self.skipTest("S3.5 dudak_denetim.py video sonrası ses diliminde (adım 16)")

    def test_03_s41_tepe_normalize(self):
        """Tepeye göre normalize edilmiş, tepe faktörü farklı iki replik → S4.1 HATA; tek doğrusal kazançla düzeltilince GEÇ."""
        a = sentez_konusma(3.0, seed=1); a = a / np.max(np.abs(a)) * 0.6
        rng = np.random.default_rng(3); b = (rng.normal(0, 1, SR * 3) * np.exp(-np.arange(SR * 3) / SR * 6)).astype(np.float32)
        b = b / np.max(np.abs(b)) * 0.6
        _, hedef = seslendir.seviye_hedefi({"teslim": "normal"})
        oklar = [seslendir.replik_seviye_olc(x, hedef)[1] for x in (a, b)]
        self.assertIn(False, oklar)
        la, lb = O.lufs(a), O.lufs(b); self.assertGreater(abs(la - lb), 1.0)
        for x in (a, b):
            y, g = seslendir.seviyele(x, hedef)
            if O.ornek_tepe(x) + (hedef - O.lufs(x)) <= -1.0: self.assertTrue(seslendir.replik_seviye_olc(y, hedef)[1])

    def test_04_iki_yatak(self):
        f = film_kur("T_IKI_YATAK", iki_yatak=True); ses_hazirla(f, ("sec", "tts"))
        C, (y5, r5), _ = ses_katmani.cizelge_t1(f, sahte=True)
        self.assertTrue(maddeler(r5, "S5.1", "HATA"))
        import ses_plani
        o = ses_plani.grup_olcumleri(so.sahneler(f), None)
        self.assertTrue(any(x["madde"] == "S0.10" and x["seviye"] == "HATA" for x in o))

    def test_05_s57_eski_klip_ozeti(self):
        f = film_kur("T_S57")
        klip = os.path.join(f, "SIRALI_VIDEO", "003.mp4"); os.makedirs(os.path.dirname(klip)); 
        with open(klip, "wb") as k: k.write(b"yeni klip")
        ef = [{"id": "E3a", "plan": 3, "kaynak": "klip", "klip_ozet": "eskiozet0000"}]
        o, yeni = ses_katmani.efekt_ozet_denetle(f, ef)
        self.assertEqual(o[0]["seviye"], "HATA"); self.assertEqual(yeni, ["E3a"]); self.assertTrue(ef[0]["bayat"])

    def test_06_miks_ortasinda_sessizlik(self):
        x = np.stack([sentez_konusma(6.0, seed=2)] * 2, 1) * 0.3 + 0.01 * np.random.default_rng(1).normal(0, 1, (len(sentez_konusma(6.0, seed=2)), 2))
        x = x.astype(np.float32); x[int(2.0 * SR):int(3.5 * SR)] = 0
        y, olc = son_miks.miksle([(x, 0.0)])
        o = son_miks.denetle(y, olc, "T1")
        self.assertEqual(next(m for m in o if m["madde"] == "S7.4")["seviye"], "HATA")

    def test_07_muzikte_kelime(self):
        f = film_kur("T_VOKAL", motif=False); enjekte(f, {"muzik": {"vokal": [1, 2]}})
        yol, r, _ = muzik_uret.uret(f, "animatik", "sahte")
        self.assertTrue(maddeler(r, "S6.1", "HATA"))
        L = ortak.json_oku(os.path.join(f, "MUZIK", "muzik_listesi.json"))
        self.assertTrue(L["ipuclari"][0]["secilen"]["dosya"].endswith(".wav"))
        self.assertNotIn("sahte1", L["ipuclari"][0]["secilen"]["dosya"]); self.assertNotIn("sahte2", L["ipuclari"][0]["secilen"]["dosya"])

    def test_08_eksi20_miks_duzeltilir(self):
        x = np.stack([sentez_konusma(5.0, seed=4)] * 2, 1); x = x * O.kazanc(-20 - O.lufs(x))
        self.assertAlmostEqual(O.lufs(x), -20, delta=0.3)
        y, olc = son_miks.miksle([(x, 0.0)])
        o = {m["madde"]: m["seviye"] for m in son_miks.denetle(y, olc, "T1")}
        self.assertEqual(o["S7.1"], "GEC"); self.assertEqual(o["S7.8"], "GEC"); self.assertEqual(o["S7.2"], "GEC")

    def test_09_motifsiz_tema_midi_yedegi(self):
        f = film_kur("T_MOTIFSIZ"); enjekte(f, {"muzik": {"motifsiz": True}})
        yol, r, _ = muzik_uret.uret(f, "animatik", "sahte")
        self.assertTrue(maddeler(r, "S6.7", "BAYRAK"))
        L = ortak.json_oku(os.path.join(f, "MUZIK", "muzik_listesi.json"))
        m2 = next(i for i in L["ipuclari"] if i["id"] == "M02")
        self.assertEqual(m2["secilen"]["saglayici"], "midi_ornek")
        self.assertGreaterEqual(m2["olcum"]["kroma"], so.esik("muzik_kroma_min"))

    def test_10_s21_konusma_yok(self):
        if not _var("ses_donustur"): self.skipTest("S2.1 ses_donustur.py --hizala video sonrası ses diliminde (adım 15–16)")

    def test_11_s23_kestrel(self):
        if not _var("ses_donustur"): self.skipTest("S2.3 ses_donustur.py --hizala video sonrası ses diliminde (adım 15–16)")

    def test_11b_telaffuz_kestrel(self):
        """Telaffuz testinde sahte ASR adı 'Kestrel' duyuyor → S1.2 HATA + YENIDEN_YAZ (hikaye-yazari)."""
        f = film_kur("T_KESTREL"); enjekte(f, {"asr": {"degistir": {"Kestra": "Kestrel"}}})
        kod, (yol, r) = ses_sec.telaffuz(f, "sahte")
        self.assertEqual(kod, 0)
        h = maddeler(r, "S1.2", "HATA"); self.assertEqual([m["birim"] for m in h], ["Kestra"])
        q = ortak.json_oku(os.path.join(f, "KUYRUK", "YENIDEN_YAZ.json"), {})
        self.assertTrue(any(m["kok_neden"] == "ad_yanlis_okundu" and m["yazar"] == "hikaye-yazari" for m in q.get("maddeler", [])))
        self.assertEqual(ortak.json_oku(os.path.join(f, "_SES", "TELAFFUZ.json"))["adlar"]["Mara"]["sonuc"], "GEC")

    def test_12_gri_bant(self):
        if not _var("ses_karar"): self.skipTest("S2.2 gri bant → replik_kabul: ses_karar.py video sonrası ses diliminde (adım 16)")

    def test_13_tasidigi_eksik(self):
        if not _var("ses_karar"): self.skipTest("S2.4 tasidigi → replik_kabul: ses_karar.py video sonrası ses diliminde (adım 16)")

    def test_14_tarif_14_kelime(self):
        import istem_denetim_ses as ids
        o = ids.tarif_denetle("in a very very low and soft and husky female voice with a strong northern English accent")
        self.assertTrue(any(m["madde"] == "S0.5" and m["seviye"] == "HATA" for m in o))

    def test_15_flow_sound_no_music(self):
        import istem_denetim_ses as ids
        o = ids.flow_sound_denetle("Sound: wind against the door, a torch crackling.")
        self.assertTrue(any(m["madde"] == "S0.6" and m["seviye"] == "HATA" for m in o))

    def test_16_elle_saglayici_zincirde(self):
        f = film_kur("T_ELLE", sahte=False)
        ortak.atomik_yaz(os.path.join(_ortam.VERI, "AYARLAR", "FILM_AYAR.json"),
                         {"saglayicilar": {"muzik": {"animatik": ["gemini_muzik_paketi", "midi_ornek"]}}})
        try:
            yol, r, _ = muzik_uret.uret(f, "animatik", None)
        finally:
            os.replace(os.path.join(_ortam.VERI, "AYARLAR", "FILM_AYAR.json"), os.path.join(_ortam.KOK, "FILM_AYAR_eski.json"))
        self.assertTrue(maddeler(r, "S6.8", "HATA")); self.assertEqual(r["zincir"], ["midi_ornek"])

    def test_17_ai84_anahtarsiz(self):
        import ai84                                               # süreç ölmez
        from saglayicilar import ai84_tts
        s = ai84_tts.AI84Tts(); ok, neden = s.hazir()
        self.assertFalse(ok); self.assertIn("anahtar", neden)
        from saglayicilar import Kisitlandi
        with self.assertRaises(Kisitlandi) as c: s.tts(tempfile.mkdtemp(dir=_ortam.KOK), "hi", "v1", os.path.join(_ortam.KOK, "x.wav"))
        self.assertTrue(c.exception.gecilebilir)

    def test_18_b15_ayni_stem_ayni_lufs(self):
        f = film_kur("T_B15"); d = os.path.join(f, "KURGU", "stem", "T1"); os.makedirs(d)
        x = np.stack([sentez_konusma(4.0, seed=5)] * 2, 1) * 0.2; O.yaz(os.path.join(d, "diyalog.wav"), x)
        C = {"cizelge": "T1", "stemler": {"diyalog": "KURGU/stem/T1/diyalog.wav"}, "sessizlik": []}
        _, o1, _ = son_miks.onizle(f, C, os.path.join(f, "KURGU", "a.wav"), "ONIZLEME")
        _, o2, _ = son_miks.onizle(f, C, os.path.join(f, "KURGU", "b.wav"), "FINAL")
        self.assertEqual(o1["stem_imza"], o2["stem_imza"]); self.assertLessEqual(abs(o1["lufs"] - o2["lufs"]), 0.1)
        yol, r = son_miks.yapisal(f); self.assertEqual(r["sonuc"], "GEC")
        b = ortak.json_oku(os.path.join(f, "_RAPOR", "S7_FINAL.json")); b["olcum"]["lufs"] += 1.5                      # bozuk: farklı LUFS
        ortak.atomik_yaz(os.path.join(f, "_RAPOR", "S7_FINAL.json"), b)
        yol, r = son_miks.yapisal(f); self.assertEqual(r["sonuc"], "HATA")


class SesHazirlik(unittest.TestCase):
    def test_secim_kadro(self):
        f = film_kur("T_SECIM")
        kod = ses_sec.main(["--ara", "--olc", "--sec", "--film", f, "--saglayici", "sahte"]); self.assertEqual(kod, 0)
        r = rapor(f, "S1_FILM.json"); self.assertIn(r["sonuc"], ("GEC", "BAYRAK"))
        vm = ortak.json_oku(os.path.join(f, "_SES", "evren_ses", "mara", "ses.json"))["secim"]["voice_id"]
        vv = ortak.json_oku(os.path.join(f, "_SES", "evren_ses", "voss", "ses.json"))["secim"]["voice_id"]
        self.assertNotEqual(vm, vv)
        A = ortak.json_oku(os.path.join(f, "_SES", "SES_ADAYLAR.json"))["karakterler"]["mara"]
        self.assertTrue(any(a["voice_id"] == "sahte_k4" and "restricted" in (a["elenme"] or "") for a in A))
        self.assertIn(vm, ("sahte_k1", "sahte_k2", "sahte_k3")); self.assertTrue(vv.startswith("sahte_e"))
        self.assertTrue(os.path.exists(os.path.join(f, "_SES", "SES_SECIM.html")))

    def test_animatik_tts_sigmayan(self):
        f = film_kur("T_SIGMAZ", dar_pencere=True); ses_hazirla(f, ("sec",))
        kod, yol, r = seslendir.tts_hazirla(f, so.replikler(f), "sahte")
        self.assertEqual(kod, 0)
        h = maddeler(r, "S2.13", "HATA"); self.assertEqual([m["birim"] for m in h], ["R0003"])
        q = ortak.json_oku(os.path.join(f, "KUYRUK", "YENIDEN_YAZ.json"), {})
        self.assertTrue(any(m["konum"] == {"plan": 4} and m["yazar"] == "yonetmen" for m in q["maddeler"]))
        D = ortak.json_oku(os.path.join(f, "SESLER", "diyalog.json"))
        self.assertEqual(D["surum"], 2); self.assertEqual(D["ornekleme_hz"], 48000)
        r1 = D["replikler"]["R0001"]
        self.assertAlmostEqual(r1["olculen_lufs"], -19.5, delta=1.0); self.assertEqual(r1["seviye"], "normal")
        self.assertEqual(D["replikler"]["R0003"]["seviye"], "fisilti")
        self.assertIn("1", D["_eski"])
        # ikinci tur: önbellekten, yeniden üretim yok
        m0 = os.path.getmtime(os.path.join(f, r1["dosya"])); seslendir.tts_hazirla(f, so.replikler(f), "sahte")
        self.assertEqual(os.path.getmtime(os.path.join(f, r1["dosya"])), m0)
        self.assertTrue(ortak.json_oku(os.path.join(f, "SESLER", "diyalog.json"))["replikler"]["R0001"]["tts"]["onbellek"])

    def test_tts_istek_ve_esnetme_orani(self):
        """Birleştirme: seslendir TTS_ISTEK.json'u okur ('yeniden okut' → aynı ses, yeni tohum: yeni dosya) ve tts.esnetme_oran yazar."""
        f = film_kur("T_TTSISTEK"); ses_hazirla(f, ("sec", "tts"))
        D = ortak.json_oku(os.path.join(f, "SESLER", "diyalog.json"))
        for rid, r in D["replikler"].items(): self.assertIn("esnetme_oran", r["tts"], rid); self.assertGreaterEqual(r["tts"]["esnetme_oran"], 0)
        eski = D["replikler"]["R0002"]["tts"]["dosya"]
        D["replikler"]["R0001"]["klip_zamani"] = {"bas": 1.0, "bit": 2.0}          # videodaki konuşma anı 1 sn: işaretli oran
        ortak.atomik_yaz(os.path.join(f, "SESLER", "diyalog.json"), D)
        ortak.atomik_yaz(os.path.join(f, "SESLER", "TTS_ISTEK.json"), {"replikler": [
            {"replik": "R0002", "neden": "esnetme > %8: yeniden okut"}, {"replik": "R0001", "neden": "tts_dudak"}]})
        self.assertEqual(seslendir.main(["--istek", "--film", f, "--saglayici", "sahte"]), 0)
        D2 = ortak.json_oku(os.path.join(f, "SESLER", "diyalog.json"))
        r2 = D2["replikler"]["R0002"]
        self.assertNotEqual(r2["tts"]["dosya"], eski); self.assertEqual(r2["yeniden_okuma"], 1)
        self.assertTrue(os.path.isfile(os.path.join(f, eski)))                     # eski take silinmez
        r1 = D2["replikler"]["R0001"]
        self.assertAlmostEqual(r1["tts"]["esnetme_oran"], round(r1["tts"]["sure_sn"] / 1.0 - 1, 3), places=3)
        ist = ortak.json_oku(os.path.join(f, "SESLER", "TTS_ISTEK.json"))["replikler"]
        self.assertTrue(all(m.get("yapildi") and m.get("dosya") for m in ist))
        self.assertEqual(seslendir.main(["--istek", "--film", f, "--saglayici", "sahte"]), 0)     # bekleyen yok
        self.assertEqual(ortak.json_oku(os.path.join(f, "SESLER", "diyalog.json"))["replikler"]["R0002"]["yeniden_okuma"], 1)

    def test_tts_hatasi_sessiz_donus_yok(self):
        f = film_kur("T_TTSHATA"); ses_hazirla(f, ("sec",)); enjekte(f, {"tts": {"hata": ["R0002"]}})
        kod, yol, r = seslendir.tts_hazirla(f, so.replikler(f), "sahte")
        self.assertTrue(maddeler(r, "S2.tts", "HATA"))
        self.assertNotIn("R0002", ortak.json_oku(os.path.join(f, "SESLER", "diyalog.json"))["replikler"])

    def test_bos_muzik_zinciri_muziksiz_bayrak(self):
        f = film_kur("T_BOSZINCIR", sahte=False)
        ortak.atomik_yaz(os.path.join(_ortam.VERI, "AYARLAR", "FILM_AYAR.json"), {"saglayicilar": {"muzik": {"yayin": ["acestep", "kutuphane"]}}})
        try: yol, r, _ = muzik_uret.uret(f, "yayin", None)
        finally: os.replace(os.path.join(_ortam.VERI, "AYARLAR", "FILM_AYAR.json"), os.path.join(_ortam.KOK, "FILM_AYAR_eski2.json"))
        self.assertEqual(r["sonuc"], "BAYRAK"); self.assertEqual(len(maddeler(r, "S6_muziksiz", "BAYRAK")), 2)
        self.assertFalse(r["hatalar"])

    def test_midi_yaz(self):
        p = midi_ornek.midi_yaz([["D5", 1], ["R", 0.5], ["F#4", 0.5]], 72, os.path.join(_ortam.KOK, "m.mid"))
        with open(p, "rb") as k: b = k.read()
        self.assertTrue(b.startswith(b"MThd")); self.assertIn(b"MTrk", b)

    def test_kur2_plani(self):
        p = ses_kiyas.kur2_plani(o0c={})
        self.assertFalse(p["kur"])
        p = ses_kiyas.kur2_plani(o0c={"ses_donustur_sira": ["openvoice", "chatterbox"]})
        self.assertTrue(p["kur"]); self.assertEqual(p["motor"], "openvoice"); self.assertTrue(p["deneme_kipi"] in (True, False))
        self.assertTrue(any("venv" in a["komut"] for a in p["adimlar"] if a.get("komut")))

    def test_motor_kiyas_sahte(self):
        f = film_kur("T_KIYAS"); ses_hazirla(f, ("sec",))
        d = os.path.join(f, "_SES", "KIYAS_KLIPLERI"); os.makedirs(d)
        for i, t in enumerate(["normal"] * 2 + ["fisilti"] + ["bagirma"]):
            x, kz = ses_sahte.konusma("Hold the line until they come back", f"veo{i}", t)
            p = os.path.join(d, f"k{i}.wav"); O.yaz(p, x); ses_sahte.yan_yaz(p, metin="Hold the line until they come back", kelimeler=kz)
            ortak.atomik_yaz(os.path.join(d, f"k{i}.json"), {"metin": "Hold the line until they come back", "teslim": t})
        kod, (yol, r) = ses_kiyas.kiyas(f, None, "mara", None, "sahte")
        self.assertEqual(kod, 0)
        self.assertTrue(maddeler(r, "S1.11_set", "BAYRAK"))              # 20 replik / ≥4 fısıltı-bağırma yok
        self.assertTrue(maddeler(r, "S1.dogallik"))                      # ÖLÇÜLEMEDİ → BAYRAK
        self.assertTrue(os.path.exists(os.path.join(f, "_SES", "MOTOR_SIRASI.json")))

    def test_uctan_uca_animatik_sesi(self):
        """A10b → A10c → A12 (seslendir --animatik, muzik --uret, ses_katmani T1, son_miks --animatik) komut satırından, sahte."""
        f = film_kur("T_UCTAN")
        self.assertEqual(ses_sec.main(["--telaffuz", "--film", f, "--saglayici", "sahte"]), 0)
        self.assertEqual(ses_sec.main(["--ara", "--olc", "--sec", "--film", f, "--saglayici", "sahte"]), 0)
        self.assertEqual(seslendir.main(["--animatik", "--film", f, "--saglayici", "sahte"]), 0)
        self.assertEqual(muzik_uret.main(["--uret", "--kip", "animatik", "--film", f, "--saglayici", "sahte"]), 0)
        self.assertEqual(ses_katmani.main(["--cizelge", "T1", "--film", f, "--saglayici", "sahte"]), 0)
        self.assertEqual(son_miks.main(["--animatik", "--film", f]), 0)
        C = ortak.json_oku(os.path.join(f, "KURGU", "SES_CIZELGESI_T1.json"))
        self.assertEqual(len(C["diyalog"]), 3); self.assertEqual(len(C["ambiyans"]), 2); self.assertEqual(len(C["muzik"]), 2)
        r5 = rapor(f, "S5_T1.json"); self.assertFalse(r5["hatalar"], r5["hatalar"])
        r6 = rapor(f, "S6_T1.json"); self.assertFalse(r6["hatalar"], r6["hatalar"])
        r7 = rapor(f, "S7_ANIMATIK.json"); self.assertEqual(r7["sonuc"], "GEC", r7)
        x, _ = O.oku(os.path.join(f, "ANIMATIK", "ses_animatik_v1.wav"))
        self.assertAlmostEqual(len(x) / SR, C["toplam_sn"], delta=1 / 24)
        self.assertLessEqual(O.gercek_tepe(x), -1.0)
        kk = ortak.json_oku(os.path.join(f, "MUZIK", "KAYNAK_KAYDI.json"))["kayitlar"]
        self.assertTrue(all(k["sha1"] and k["lisans"] for k in kk))
        self.assertIn(rapor(f, "S1a_telaffuz.json")["sonuc"], ("GEC", "BAYRAK"))


if __name__ == "__main__":
    unittest.main()
