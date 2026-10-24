"""Ses testi — kâğıt kısmı (TASARIM §6.6, §6.10 test_ses, §7.2 S0, §9 adım 10 PR-7, D-25; [SM2] §4.7.1, §4.7.10).

Temiz fikstür: FILMLER/ORNEK_3_SAHNE_TAM (kâğıt sonundaki SAHNELER v2 + ses tasarımı + müzik listesi). Her test bir kopya üzerinde
tek bozukluk enjekte eder ve beklenen maddeyi arar:
  - S0 profil (A06s): veo_ses_tarifi 14 kelime / aksansız / yaş sözcüğü → S0.5 HATA; figüran kuralı; yaratığa Veo tarifi HATA;
    aynı bant ayrışmıyor BAYRAK.
  - S0 film (A08): yol ↔ ağız çelişkisi (S0.1), ekran dışı seste dinleyen ağzı (S0.2), ses tanıtım kuralı (S0.3), flow_sound kalıbı
    (S0.6), efektsiz fiziksel adım (S0.7), iki yatak / kesintisiz zamanda yatak değişimi (S0.10), defterde olmayan katman (S0.11),
    mutlak sessizlik sayısı (S0.12), _derlenir'e ajan yazımı, HATA'da SAHNELER değişmez + YENIDEN_YAZ.
  - Müzik (S0.14–S0.18 ve zincir): replik ortasında giriş, bilinmeyen olay, 'no vocals' yok, sanatçı adı, temada motif yok,
    leitmotif dönüş sayısı, ardışık aynı duygu, kaplama, 'elle' sağlayıcı son basamak değil, midi_ornek yayında; zincir boş → BAYRAK
    (D-25); --midi geçerli SMF; --uret/--yerlestir → 4.
  - İstem (A09, istem_denetim_ses): konuşan planda tarif birebir değil (S0.4), TTS planında Veo'ya söz (S0.4), flow_sound istem
    sonunda değil (S0.6); istem_denetim v2'nin iki yanlış alarmı ayıklanır; birleşik ISTEM kapısı temiz fikstürde GEÇ.
Ağ yok, kredi yok."""
import os, sys, json, io, copy, shutil, hashlib, contextlib, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam
import ortak, esikler, kuyruk, ses_plani, muzik, istem_denetim_ses as ids   # kuyruk önceden: import'ta stdout.reconfigure

TAM = os.path.join(os.path.dirname(ARACLAR), "FILMLER", "ORNEK_3_SAHNE_TAM")
SAYAC = [0]


def jl(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def sessiz(f, *a):
    with contextlib.redirect_stdout(io.StringIO()): return f(*a)


def maddeler(r, seviye=None):
    xs = (r["hatalar"] if seviye in (None, "HATA") else []) + (r["bayraklar"] if seviye in (None, "BAYRAK") else [])
    return {(x["madde"], x.get("alt")) for x in xs}


class Taban(unittest.TestCase):
    def setUp(self):
        SAYAC[0] += 1
        self.kok = os.path.join(_ortam.VERI, "FILMLER", f"SES_{SAYAC[0]:03d}")
        shutil.copytree(TAM, self.kok, ignore=shutil.ignore_patterns("_KASET"))
        ortak.atomik_yaz(os.path.join(self.kok, "HAZIRLIK.json"), {"film": os.path.basename(self.kok)})
        self.S = jl(os.path.join(self.kok, "SAHNELER.json"))

    def yol(self, *p): return os.path.join(self.kok, *p)
    def sahneler_yaz(self, S=None): ortak.atomik_yaz(self.yol("SAHNELER.json"), S or self.S)
    def plan(self, no): return next(s for s in self.S["sahneler"] if s["no"] == no)
    def ses_dosyasi(self, S):
        for ad in os.listdir(self.yol("_SES")):
            if ad.startswith("SES_G") and jl(self.yol("_SES", ad)).get("sahne_grubu") == S: return self.yol("_SES", ad)
        raise AssertionError(S)

    def ses_degistir(self, S, f):
        p = self.ses_dosyasi(S); j = jl(p); f(j); ortak.atomik_yaz(p, j)

    def denetle(self, *ek):
        self.assertEqual(sessiz(ses_plani.main, ["--denetle", "--tum", "--film", self.kok] + list(ek)), 0)
        return jl(self.yol("_RAPOR", "S0_FILM.json"))

    def muzik_degistir(self, f):
        p = self.yol("MUZIK", "muzik_listesi.json"); j = jl(p); f(j); ortak.atomik_yaz(p, j)

    def muzik_olc(self):
        h = jl(self.yol("HIKAYE.json")); liste = muzik.liste_oku(self.kok)
        olc, _ = muzik.kagit_olcumleri(self.S, liste, h, None, muzik.motifler(self.kok, h, liste))
        return {(x["madde"], x.get("alt")): x["seviye"] for x in olc}


class TemizFikstur(Taban):
    def test_profil_film_istem_temiz(self):
        self.assertEqual(sessiz(ses_plani.main, ["--profil-denetle", "--film", self.kok]), 0)
        self.assertEqual(jl(self.yol("_RAPOR", "S0_PROFIL_t1.json"))["sonuc"], "GEC")
        r = self.denetle()
        self.assertEqual(r["sonuc"], "GEC", r["hatalar"] + r["bayraklar"]); self.assertTrue(r["sahneler_yazildi"])
        self.assertTrue(any("S0.19" in x for x in r["ertelenen"]) and any("S0.20" in x for x in r["ertelenen"]))
        S = jl(self.yol("SAHNELER.json")); p3 = next(s for s in S["sahneler"] if s["no"] == 3)
        self.assertEqual(p3["_derlenir"]["ton_fiili_en"], "whispers"); self.assertEqual(p3["_derlenir"]["muzik_ipucu"], None)
        self.assertEqual(next(s for s in S["sahneler"] if s["no"] == 4)["_derlenir"]["muzik_ipucu"], "M01")
        imz = jl(self.yol("_YONETMEN", "DERLENIR_IMZA.json"))["imzalar"] if os.path.isfile(self.yol("_YONETMEN", "DERLENIR_IMZA.json")) else None
        if imz is not None:
            import plan_ortak as po
            self.assertEqual(imz["3"], po.imza(p3["_derlenir"]))            # kod yazdı → imza tazelendi (plan_sema elle yazım sanmaz)
        self.assertTrue(os.path.isfile(self.yol("_SES", "SES_TASARIMI.md")))
        r, _ = ids.istem_raporu(self.kok)
        self.assertEqual(r["sonuc"], "GEC", r["hatalar"] + r["bayraklar"])

    def test_tek_sahne_ve_v1(self):
        ortak.atomik_yaz(self.yol("SAHNELER.json"), dict(self.S, _surum=1))
        self.assertEqual(sessiz(ses_plani.main, ["--denetle", "--tum", "--film", self.kok]), 4)
        self.sahneler_yaz()
        self.assertEqual(sessiz(ses_plani.main, ["--denetle", "--sahne", "S11", "--film", self.kok]), 0)
        r = jl(self.yol("_RAPOR", "S0_S11.json")); self.assertEqual(r["sonuc"], "GEC", r["hatalar"]); self.assertFalse(r["sahneler_yazildi"])

    def test_esikler_cift_anahtarsiz(self):
        E = esikler.yukle()
        self.assertEqual(E["veo_ses_tarifi_kelime_max"], 12); self.assertEqual(E.kayit["flow_sound_kelime_max"]["_dosya"], "ses_esikleri.json")
        self.assertEqual(E.kayit["muzik_kaplama_oran"]["_dosya"], "ritim_esikleri.json")     # RE'de olan burada tekrarlanmaz


class Profil(Taban):
    def profil(self, f):
        p = self.yol("_SES", "SES_PROFILLERI.json"); j = jl(p); f(j["karakterler"]); ortak.atomik_yaz(p, j)
        self.assertEqual(sessiz(ses_plani.main, ["--profil-denetle", "--film", self.kok]), 0)
        return jl(self.yol("_RAPOR", "S0_PROFIL_t1.json"))

    def test_tarif_kurallari(self):
        r = self.profil(lambda k: k["sera"].update(veo_ses_tarifi="in a very low, soft, husky and slightly breathy female voice with a northern English accent"))
        self.assertIn(("S0.5", "kelime"), maddeler(r, "HATA"))
        r = self.profil(lambda k: k["sera"].update(veo_ses_tarifi="in a low, husky female voice"))
        self.assertIn(("S0.5", "aksan_yok"), maddeler(r, "HATA"))
        r = self.profil(lambda k: k["brann"].update(veo_ses_tarifi="in a deep, old male voice with a Scottish accent"))
        self.assertIn(("S0.5", "yas_sozcugu"), maddeler(r, "HATA"))
        r = self.profil(lambda k: k["brann"].update(veo_ses_tarifi="with a Scottish accent, a deep male voice"))
        self.assertIn(("S0.5", "sira"), maddeler(r, "BAYRAK")); self.assertNotIn(("S0.5", "sira"), maddeler(r, "HATA"))

    def test_yaratik_ve_ayrisma(self):
        r = self.profil(lambda k: k["kit"].update(veo_ses_tarifi="in a low, rough male voice with a Scottish accent"))
        self.assertIn(("yaratik_sesi", None), maddeler(r, "HATA"))
        def ayni(k):
            k["oda"].update(yas_bandi="yetiskin", perde=k["brann"]["perde"], tini=list(k["brann"]["tini"]))
        r = self.profil(ayni); self.assertIn(("kadro_ayrismiyor", None), maddeler(r, "BAYRAK"))
        r = self.profil(lambda k: k.pop("oda")); self.assertIn(("profil_eksik", None), maddeler(r, "HATA"))


class SesKagidi(Taban):
    def test_yol_ve_agiz(self):                                                  # S0.1
        self.ses_degistir("S01", lambda j: j["planlar"]["3"]["diyalog"].update(yol="tts"))
        r = self.denetle(); self.assertIn(("S0.1", "yol_cekisiyor"), maddeler(r, "HATA"))
        self.ses_degistir("S01", lambda j: j["planlar"]["3"]["diyalog"].update(yol_neden="fısıltı; dönüştürücü fısıltıda zorlanır (ders)"))
        self.assertNotIn(("S0.1", "yol_cekisiyor"), maddeler(self.denetle()))

    def test_dinleyen_agiz_ve_tanitim(self):                                     # S0.2, S0.3
        self.plan(28)["_derlenir"]["dinleyen_agiz"] = "acik"; self.sahneler_yaz()
        self.assertIn(("S0.2", None), maddeler(self.denetle(), "HATA"))
        self.assertFalse(ses_plani.dinleyen_agiz_kurali(self.plan(28)))
        ps = copy.deepcopy(self.S["sahneler"])
        self.assertEqual(ses_plani.ses_tanitim_kurali(ps), [])                   # R0012/R0020: konuşan önce ekranda duyuldu
        brann_ilk = [s for s in ps if (s.get("replik") or {}).get("karakter") == "brann"]
        for s in brann_ilk[:2]: s["_derlenir"]["agiz_gorunur"] = "yok"; s["zanaat"]["kadrajdakiler"] = []
        self.assertIn({"plan": 11, "karakter": "brann"}, ses_plani.ses_tanitim_kurali(ps))
        self.assertEqual(ses_plani.ses_tanitim_kurali(ps, gizem=("brann",)), [])

    def test_flow_sound_ve_efekt(self):                                          # S0.6, S0.7
        self.ses_degistir("S03", lambda j: j["planlar"]["8"].update(flow_sound="Sound: a door creaking, wind."))
        self.assertIn(("S0.6", "kalip"), maddeler(self.denetle(), "HATA"))
        self.ses_degistir("S03", lambda j: j["planlar"]["8"].update(flow_sound="Sound: a door creaking, soft music. No music.", efektler=[]))
        r = self.denetle(); m = maddeler(r, "HATA")
        self.assertIn(("S0.6", "muzik_sozcugu"), m); self.assertIn(("S0.7", "efektsiz_fiziksel_adim"), m)
        self.ses_degistir("S03", lambda j: j["planlar"]["8"].update(flow_sound="Sound: a door creaking. No music.",
                                                                    efektler=[{"adim": "a1", "sessiz_adim": True, "neden": "kapı keçeli"}]))
        self.assertNotIn(("S0.7", "efektsiz_fiziksel_adim"), maddeler(self.denetle()))

    def test_yatak(self):                                                        # S0.10, S0.11
        self.ses_degistir("S02", lambda j: j["ses"]["yatak"].update(etiket="DIS_baska_yatak"))
        self.assertIn(("S0.10", "kesintisiz_zamanda_yatak_degisti"), maddeler(self.denetle(), "HATA"))
        self.ses_degistir("S02", lambda j: j["ses"].update(yatak=[{"etiket": "a"}, {"etiket": "b"}]))
        self.assertIn(("S0.10", "birden_cok_yatak"), maddeler(self.denetle(), "HATA"))

    def test_katman_defterde_yok(self):
        def f(j):
            j["ses"]["yatak"]["katmanlar"].append({"ad": "ocak", "dosya": None, "kazanc_db": -12, "kaynak": "defter:mekan.kulube.ocak=yanik"})
        self.ses_degistir("S03", f)
        r = self.denetle(); self.assertIn(("S0.11", "katman_defterde_yok"), maddeler(r, "HATA"))
        self.ses_degistir("S03", lambda j: j["ses"]["yatak"]["katmanlar"].__setitem__(-1, {"ad": "x", "kaynak": "zaman:hava=yagmur"}))
        self.assertIn(("S0.11", "katman_zamanla_celisiyor"), maddeler(self.denetle(), "HATA"))

    def test_mutlak_sessizlik_ve_hata_davranisi(self):                            # S0.12; HATA'da SAHNELER değişmez
        once = jl(self.yol("SAHNELER.json"))
        for S, no in (("S04", "11"), ("S05", "13"), ("S06", "15")):
            self.ses_degistir(S, lambda j, no=no: j["planlar"][no].update(sessizlik={"tip": "mutlak", "bas_sn": 1.0, "sure_sn": 0.8, "neden": "sok"}))
        r = self.denetle(); self.assertIn(("S0.12", None), maddeler(r, "HATA")); self.assertFalse(r["sahneler_yazildi"])
        self.assertEqual(jl(self.yol("SAHNELER.json")), once)

    def test_ajan_alan_disi_yazim(self):
        self.ses_degistir("S05", lambda j: j["planlar"]["13"].update(_derlenir={"agiz_gorunur": "tam"}))
        r = self.denetle(); m = maddeler(r, "HATA")
        self.assertIn(("derlenir_ajan_yazimi", None), m)
        self.ses_degistir("S05", lambda j: (j["planlar"]["13"].pop("_derlenir"), j.update(sahne_grubu="S99")))
        self.assertIn(("ses_dosyasi_grup", None), maddeler(self.denetle(), "HATA"))

    def test_yeniden_yaz_kuyrugu(self):
        self.ses_degistir("S03", lambda j: j["planlar"]["8"].update(efektler=[]))
        self.denetle()
        q = jl(self.yol("KUYRUK", "YENIDEN_YAZ.json"))
        self.assertTrue(any(x.get("yazar") == "ses-tasarimcisi" and x.get("madde") == "S0.7" for x in q["maddeler"]))

    def test_taslak(self):
        self.assertEqual(sessiz(ses_plani.main, ["--taslak", "--film", self.kok]), 0)
        t = jl(self.yol("_SES", "SES_S11.taslak.json"))
        self.assertTrue(t["ses"]["gecis"]["zaman_surekli_onceki"])                 # S10 → S11 aynı mekân, kesintisiz: yatak sürer
        self.assertEqual(t["planlar"]["27"]["diyalog"]["yol"], "veo_donustur")
        tts = jl(self.yol("_SES", "SES_S07.taslak.json"))["planlar"]["19"]["diyalog"]["yol"]
        self.assertEqual(tts, "tts")                                               # ağız görünmüyor → TTS (§2.2 karar 2)
        self.assertTrue(all(len(ids.kelimeler(v["flow_sound"][7:-11])) <= 12 for v in t["planlar"].values()))


class MuzikKagidi(Taban):
    def test_temiz_ve_rapor(self):
        self.assertEqual(sessiz(muzik.main, ["--kagit", "--film", self.kok]), 0)
        r = jl(self.yol("_RAPOR", "S0_MUZIK.json")); self.assertEqual(r["hatalar"], [])
        self.assertIn(("muzik_zinciri_bos", None), maddeler(r, "BAYRAK"))          # D-25: bulutta zincir boş → müziksiz + BAYRAK
        self.assertEqual(jl(self.yol("MUZIK", "ZINCIR.json"))["ozet"], "bos")
        z = jl(self.yol("MUZIK", "IPUCU_ZAMANLARI.json")); self.assertTrue(z["muziksiz"])
        self.assertIn("LM_SERA", jl(self.yol("MUZIK", "leitmotif_adaylari.json"))["leitmotifler"])
        self.assertEqual(sessiz(muzik.main, ["--uret", "--film", self.kok]), 4)
        self.assertEqual(sessiz(muzik.main, ["--yerlestir", "--film", self.kok]), 4)

    def test_olay_ve_istem(self):
        self.muzik_degistir(lambda j: j["ipuclari"][1].update(giris={"olay": "adim_basi", "plan": 11, "adim": "a2", "ofset_sn": 1.0}))
        self.assertEqual(self.muzik_olc().get(("S0.15", "replik_ortasinda_giris")), "HATA")
        self.muzik_degistir(lambda j: j["ipuclari"][1].update(giris={"olay": "sihir", "plan": 11}))
        self.assertEqual(self.muzik_olc().get(("S0.15", "giris_olayi")), "HATA")
        def istem(j):
            j["ipuclari"][0]["istem_en"] = "Epic flute theme in the style of Hans Zimmer, D dorian."
            j["ipuclari"][2].pop("motif")
        self.muzik_degistir(istem); o = self.muzik_olc()
        for alt in ("sanatci_film_adi", "no_vocals_yok", "temada_motif_yok"): self.assertEqual(o.get(("S0.18", alt)), "HATA", alt)
        self.muzik_degistir(lambda j: j["leitmotifler"]["LM_SERA"].update(notalar=[["D5", 1.0], ["H9", 1]]))
        self.assertEqual(self.muzik_olc().get(("S0.18", "motif_notasiz")), "HATA")

    def test_leitmotif_duygu_kaplama(self):
        self.muzik_degistir(lambda j: j.update(ipuclari=[x for x in j["ipuclari"] if x["id"] not in ("M03", "M04")]))
        o = self.muzik_olc(); self.assertEqual(o.get(("S0.17", "donus_sayisi")), "BAYRAK")
        self.assertNotIn(("S0.14", "kaplama"), o)
        self.muzik_degistir(lambda j: j.update(ipuclari=[x for x in j["ipuclari"] if x["id"] in ("M01", "M06")]))
        self.assertEqual(self.muzik_olc().get(("S0.14", "kaplama")), "BAYRAK")
        self.muzik_degistir(lambda j: j["ipuclari"][1].update(duygu=j["ipuclari"][0]["duygu"]))
        self.assertEqual(self.muzik_olc().get(("S0.16", None)), "BAYRAK")
        self.muzik_degistir(lambda j: [x.update(donusum="sade") for x in j["ipuclari"] if x.get("motif")])
        self.assertEqual(self.muzik_olc().get(("S0.17", "doruk_tam_sunum")), "BAYRAK")

    def test_zincir(self):
        self.muzik_degistir(lambda j: j["ipuclari"][0].update(saglayici=["gemini_muzik_paketi", "acestep"]))
        self.assertEqual(self.muzik_olc().get(("muzik_zinciri", "elle_son_basamak_degil")), "HATA")
        self.muzik_degistir(lambda j: j["ipuclari"][0].update(saglayici=["midi_ornek"]))
        self.assertEqual(self.muzik_olc().get(("muzik_zinciri", "midi_ornek_yayinda")), "HATA")
        self.muzik_degistir(lambda j: j["ipuclari"][0].update(saglayici=["acestep", "kutuphane", "gemini_muzik_paketi"]))
        self.assertNotIn(("muzik_zinciri", "elle_son_basamak_degil"), self.muzik_olc())

    def test_midi(self):
        self.assertEqual(sessiz(muzik.main, ["--midi", "--film", self.kok]), 0)
        d = jl(self.yol("MUZIK", "motif", "DIZIN.json"))
        self.assertEqual(set(d), {"LM_SERA_sade.mid", "LM_SERA_tehdit.mid", "LM_SERA_zafer.mid"})
        with open(self.yol("MUZIK", "motif", "LM_SERA_sade.mid"), "rb") as f: b = f.read()
        self.assertEqual(b[:4], b"MThd"); self.assertEqual(b[14:18], b"MTrk"); self.assertEqual(hashlib.sha1(b).hexdigest(), d["LM_SERA_sade.mid"]["sha1"])
        self.assertIn(bytes([0x90, muzik.nota_no("D5"), 80]), b)
        with open(self.yol("MUZIK", "motif", "LM_SERA_zafer.mid"), "rb") as f: z = f.read()
        self.assertIn(bytes([0x90, muzik.nota_no("D5") + 3, 80]), z)              # D dorian → F major: +3 yarım ses
        self.assertEqual(muzik.nota_no("C4"), 60); self.assertEqual(muzik.nota_no("Bb3"), 58)
        self.assertEqual(sessiz(muzik.main, ["--midi", "--motif", "YOK", "--film", self.kok]), 1)


class IstemSes(Taban):
    def test_konusan_ve_tts(self):
        p3 = self.plan(3); p3["hareket_istem"] = p3["hareket_istem"].replace("northern English", "Irish")
        p19 = self.plan(19); p19["hareket_istem"] = p19["hareket_istem"].replace("Sound:", 'Brann says: "Search every cabin on the ridge." Sound:')
        p5 = self.plan(5); fs = p5["zanaat"]["ses"]["flow_sound"]; p5["hareket_istem"] = fs + " " + p5["hareket_istem"].replace(fs, "").strip()
        o = {(x["madde"], x.get("alt"), x.get("plan")) for x in ids.denetle(self.S, profiller=ids.profiller_oku(self.kok))}
        self.assertIn(("S0.4", "tarif_birebir_degil", 3), o)
        self.assertIn(("S0.4", "tts_planinda_veo_konusuyor", 19), o)
        self.assertIn(("S0.6", "istem_sonunda_degil", 5), o)
        p28 = self.plan(28); p28["hareket_istem"] = p28["hareket_istem"].replace("listens silently, mouth closed; ", "")
        o = {(x["madde"], x.get("alt"), x.get("plan")) for x in ids.denetle(self.S, profiller=ids.profiller_oku(self.kok))}
        self.assertIn(("S0.2", "dinleme_kalibi", 28), o)

    def test_yanlis_alarm_ayiklama(self):
        import istem_denetim as idn
        ham = idn.denetle_v2(self.S, (), None, ses_tarifleri={k: p["veo_ses_tarifi"] for k, p in ids.profiller_oku(self.kok).items()
                                                                  if p.get("veo_ses_tarifi")})
        temiz = ids.ayikla(ham, self.S)
        self.assertFalse([x for x in temiz if x["seviye"] == "HATA"], temiz)
        p21 = self.plan(21); p21["hareket_istem"] = p21["hareket_istem"].replace("Static", "Sera realizes the truth. Static")
        k = [x for x in ids.ayikla(idn.denetle_v2(self.S, ()), self.S) if x["madde"] == "ic_durum_fiili"]
        self.assertEqual([x["olcu"] for x in k if x.get("plan") == 21], [["realizes"]])  # tırnak dışı iç durum fiili kalır


if __name__ == "__main__":
    unittest.main()
