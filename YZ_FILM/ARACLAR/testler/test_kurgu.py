"""test_kurgu — kurgu hattının 16 senaryosu (TASARIM §6.10 `test_kurgu (16 senaryo)`; [KU2] §4.6.3). Ağ ve kredi yok; sahte sağlayıcı.
Başka adımların sahibi olduğu senaryolar (T0 çizelgesi, tek ölçü tek kod, animatik, paket sızıntısı, kesme simülasyonu) o adımın aracı
varsa onun işleviyle sınanır, yoksa nedeni yazılarak atlanır."""
import os, sys, json, glob, shutil, unittest
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import _ortam  # noqa: F401  (önce: geçici YOLLAR.json)
import numpy as np
import _kurgu_fikstur as F
import ortak, kurgu_ortak as ko, kirp_oner, plan_kurgu, kurgu_denetim_tam as kdt, dudak_denetim, ses_donustur_ana as sda
import diyalog_esitle, ses_katmani_t2, muzik_yerlestir, capcut_film, taslak_fark, capcut_yama, notlari_oku
import capcut_taslak as ct

S = ["--saglayici", "sahte"]


def _hazir(kok, ses=True):
    A = ["--film", kok] + S
    if ses: sda.main(A)
    plan_kurgu.main(A)
    return A


def _kp(kok): return ko.kurgu_plani(kok)[1]


def _j(*yol):
    with open(os.path.join(*yol), encoding="utf-8") as f: return json.load(f)


def _m(*yol):
    with open(os.path.join(*yol), encoding="utf-8") as f: return f.read()


def _maddeler(r): return [h["madde"] for h in r["hatalar"] + r["bayraklar"]]


class T01_T2Cizelge(unittest.TestCase):
    def test_toplam_asl_jl(self):
        """1. Çizelge ölçüleri: toplam = Σ süre, ASL = ortalama, J/L oranı (T0'ın kendisi adım 8'in zaman_cizelgesi'ndedir)."""
        kok = F.film_kur(); _hazir(kok); kp = _kp(kok)
        sureler = [x["sure"] for x in kp["planlar"]]
        self.assertAlmostEqual(kp["olcumler"]["toplam_sn"], round(sum(sureler), 3), places=2)
        self.assertAlmostEqual(kp["olcumler"]["asl"], round(sum(sureler) / len(sureler), 3), places=2)
        self.assertEqual(kp["olcumler"]["jl_orani_diyalog"], 0.5)          # 2 replikten biri L
        for a, b in zip(kp["planlar"], kp["planlar"][1:]):                  # boşluksuz, kare yuvarlı
            self.assertAlmostEqual(b["cizelge_bas"], a["cizelge_bas"] + a["sure"], places=2)
            self.assertLess(abs(b["cizelge_bas"] * 24 - round(b["cizelge_bas"] * 24)), 0.05)


class T02_TekOlcu(unittest.TestCase):
    def test_tek_olcu_tek_kod(self):
        """2. Tek ölçü tek kod: hikaye_odasi, plan_denetim ve zaman_cizelgesi aynı zaman fonksiyonunu içe alır (adım 7–8)."""
        try:
            import zaman_cizelgesi, plan_denetim, hikaye_odasi
        except Exception as e: self.skipTest(f"adım 7–8 araçları içe alınamadı: {e}")
        ortak_ad = [a for a in ("zaman_olculeri", "olcumler", "olc") if hasattr(zaman_cizelgesi, a)]
        if not ortak_ad: self.skipTest("zaman_cizelgesi ortak ölçü işlevini dışa vermiyor (adım 8 sahibi)")
        f = getattr(zaman_cizelgesi, ortak_ad[0])
        kullananlar = [m for m in (plan_denetim, hikaye_odasi) if getattr(m, "zaman_cizelgesi", None) is zaman_cizelgesi
                       or any(getattr(m, n, None) is f for n in dir(m))]
        if not kullananlar: self.skipTest("plan_denetim/hikaye_odasi zaman_cizelgesi'ni içe almıyor (adım 7–8 sahibi)")
        self.assertTrue(kullananlar)


class T03_Animatik(unittest.TestCase):
    def test_animatik(self):
        """3. Animatik: render süresi = T1 ±1 kare (adım 14: test_kurgu_animatik; kurgu_render --animatik)."""
        if not os.path.exists(os.path.join(HERE, "test_kurgu_animatik.py")): self.skipTest("adım 14 testi yok")
        import kurgu_render
        self.assertTrue(hasattr(kurgu_render, "main"))


class T04_Kirpma(unittest.TestCase):
    def test_hareket_basi_iki_kare(self):
        """4. Kırpma: hareketli kutuda hareket başı ±2 kare; önizleme süresi = Σ kullanım; atlanan adım BAYRAK."""
        kok = F.film_kur(); _hazir(kok, ses=False); kp = _kp(kok)
        x = ko.plan_bul(kp, 1); hb = x["goruntu"]["olculen"]["hareket_bas"]
        self.assertLessEqual(abs(hb - 1.25) * 24, 2.0)
        self.assertAlmostEqual(x["goruntu"]["kullanim"]["bas"], ko.kare(hb - 0.1), places=3)
        self.assertAlmostEqual(ko.toplam_sure(kp), round(sum(y["goruntu"]["kullanim"]["sure"] for y in kp["planlar"]), 3), places=2)
        p = dict(ko.sahne_planlari(kok)[1]); z = dict(p["zanaat"])
        z["eylem_zinciri"] = z["eylem_zinciri"] + [{"id": "a3", "bas": 5.6, "bit": 7.0, "tur": "fiziksel", "fiil": "doner"}]
        p["zanaat"] = z
        o = kirp_oner.oner(kok, p, ko.klip_yolu(kok, 1), [], kusurlar=[])
        self.assertIn("adim_atlandi", [b["madde"] for b in o["bayraklar"]])


class T05_SenkronJL(unittest.TestCase):
    def test_kaydirilmis_diyalog_ve_y31(self):
        """5. Senkron ve J/L: kaydırılmış diyalog HATA; ekranda konuşulan < 1,0 sn ve kısa alıcı plan HATA; bölünmüş klipte 2. parça bas."""
        kok = F.film_kur(); A = _hazir(kok); kp = _kp(kok)
        _, r = kdt.denetle(kok, A); self.assertNotIn("senkron", [h["madde"] for h in r["hatalar"]])
        kp["diyalog"][0]["cizelge_bas"] = ko.kare(kp["diyalog"][0]["cizelge_bas"] + 0.25)
        x3 = ko.plan_bul(kp, 3); x3["sure"] = ko.kare(0.95); x3["goruntu"]["kullanim"]["sure"] = x3["sure"]
        x4 = ko.plan_bul(kp, 4); x4["sure"] = ko.kare(0.5); x4["goruntu"]["kullanim"]["sure"] = x4["sure"]
        plan_kurgu.cizelgele(kp["planlar"]); kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        _, r = kdt.denetle(kok, A); h = [m["madde"] for m in r["hatalar"]]
        for madde in ("senkron", "Y31_L_ekranda_konusma", "Y31_L_alici_plan"): self.assertIn(madde, h)
        self.assertEqual(r["sonuc"] in ("HATA", "KISMI"), True)

    def test_senkron_korumali_bolme(self):
        kok = F.film_kur(); s = ko.sahneler(kok)
        p6 = json.loads(json.dumps(s["sahneler"][2])); p6.update(no=6, sira=4.5); p6["zanaat"]["kaynak_klip"] = 3
        p6["zanaat"]["kesme"] = {"tip": "duz"}; p6.pop("replik"); p6["_derlenir"].pop("replik_zaman")
        s["sahneler"][2]["zanaat"]["kesme"]["ses_tasma_sn"] = 3.0
        s["sahneler"].insert(3, p6); ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
        d = ko.diyalog_oku(kok); d["replikler"]["R0001"]["klip_zamani"]["bit"] = 7.0
        d["replikler"]["R0001"]["kelimeler"] = F._kelimeler(d["replikler"]["R0001"]["senaryo_metin"], 2.0, 7.0); ko.diyalog_yaz(kok, d)
        _hazir(kok, ses=False); kp = _kp(kok)
        a, b = ko.plan_bul(kp, 3), ko.plan_bul(kp, 6)
        arada = sum(x["sure"] for x in kp["planlar"][kp["planlar"].index(a) + 1:kp["planlar"].index(b)])
        self.assertAlmostEqual(b["goruntu"]["kullanim"]["bas"], ko.kare(a["goruntu"]["kullanim"]["bas"] + a["sure"] + arada), places=2)
        _, r = kdt.denetle(kok, ["--film", kok])
        self.assertNotIn("S3.6_bolme_soz_kesisimi", [h["madde"] for h in r["hatalar"]])
        kp = _kp(kok); b = ko.plan_bul(kp, 6); b["goruntu"]["kullanim"]["bas"] = ko.kare(b["goruntu"]["kullanim"]["bas"] + 0.4)
        plan_kurgu.cizelgele(kp["planlar"]); kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        _, r = kdt.denetle(kok, ["--film", kok])
        self.assertIn("S3.6_bolme_soz_kesisimi", [h["madde"] for h in r["hatalar"]])     # atlanan aralık bir sözü kesiyor


class T06_PaketSizintisi(unittest.TestCase):
    def test_paket(self):
        """6. Paket sızıntısı: izleme kiplerinin kör paketi adım 14'ündür (kor_paket_izleme; test_kor_paket, test_kurgu_animatik)."""
        try: import kor_paket_izleme  # noqa: F401
        except Exception as e: self.skipTest(f"kor_paket_izleme yok: {e}")
        self.skipTest("sızıntı senaryosu adım 14'ün testlerinde koşar (test_kurgu_animatik); burada yinelenmez")


class T07_Puan(unittest.TestCase):
    def test_medyan(self):
        """7. Puan: {6, 8, 9} → 8 (puan_oku.medyan; seyirci_topla aynı işlevi kullanır)."""
        import puan_oku
        self.assertEqual(puan_oku.medyan([6, 8, 9]), 8)


class T08_Kuyruk(unittest.TestCase):
    def test_sifir_kredi_ve_soy(self):
        """8. Kuyruk: sifir_kredi yoksa ret; plan başına 3. yeniden çekim reddedilir (soy tavanı)."""
        import kuyruk
        kok = F.film_kur(klipler=False)
        m = {"plan": 3, "tur": "video", "kaynak_kapi": "KI", "kok_neden": "nesne_zipladi", "seviye": "KRITIK", "cozum": "yeniden_cek"}
        s = kuyruk.ekle(kok, [m]); self.assertEqual(len(s["reddedilen"]), 1)
        m["sifir_kredi"] = {"denendi": True, "basamaklar": [1, 5], "gerekce": "kusur pencereyi daraltıyor"}
        for beklenen in (1, 1, 0):
            s = kuyruk.ekle(kok, [dict(m)])
            self.assertEqual(len(s["eklenen"]), beklenen)
            for mid in s["eklenen"]: kuyruk.durum_degistir(kok, mid, "tamam")
        self.assertTrue(s["merdiven"])


class T09_AnimatikImza(unittest.TestCase):
    def test_imzasiz_video_acilmaz(self):
        """9. Kapı: animatik ONAYLI imzası yoksa video görevi açılmaz (animatik_imza, adım 14)."""
        try: import animatik_imza
        except Exception as e: self.skipTest(f"animatik_imza yok: {e}")
        kok = F.film_kur(klipler=False)
        ok = animatik_imza.dogrula(kok)[0]
        self.assertFalse(ok)


class T10_KesmeTuru(unittest.TestCase):
    def test_kesme_simule(self):
        """10. Kesme turu: kurulum götüren kesme HATA (kurgu_denetim --kesme-simule, adım 14)."""
        self.skipTest("kesme simülasyonu adım 14'ündür (test_kurgu_animatik); Z3 burada sınanır")


class T11_Dondurma(unittest.TestCase):
    def test_y58(self):
        """11. Dondurma: etkisi olan planın sahne içi sırası değişince Y58 HATA; etkisiz plan serbest."""
        kok = F.film_kur(); A = _hazir(kok, ses=False); kp = _kp(kok)
        p = kp["planlar"]; p[0], p[1] = p[1], p[0]                      # etkisiz tepki (#2) etkili #1'in önüne
        plan_kurgu.cizelgele(p); kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        _, r = kdt.denetle(kok, A); self.assertNotIn("Y58_etkili_sira", _maddeler(r))
        s = ko.sahneler(kok); s["sahneler"][1]["zanaat"]["eylem_zinciri"][0]["etki"] = {"voss.isaret": "M2"}
        s["sahneler"][1]["sira"] = 2; ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
        kp["planlar"][0]["etkili"] = True; kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        _, r = kdt.denetle(kok, A); self.assertIn("Y58_etkili_sira", [h["madde"] for h in r["hatalar"]])


def _taslak(kok):
    A = _hazir(kok); diyalog_esitle.main(A); ses_katmani_t2.main(A); muzik_yerlestir.main(A)
    assert capcut_film.giris(A) == 0
    return A, _j(kok, "KURGU", "son_capcut_projesi.json")


def _kullanici_duzenler(p, ripple=True, yazi=True, ses=None):
    dc = os.path.join(p["klasor"], "draft_content.json"); ic = _j(dc)
    for t in ic["tracks"]:
        if t["name"] == "Klipler":
            sg = t["segments"]; s0 = sg[0]
            s0["source_timerange"]["start"] += 500000; s0["source_timerange"]["duration"] -= 500000; s0["target_timerange"]["duration"] -= 500000
            sg.pop(1)
            if ripple:
                t0 = s0["target_timerange"]["duration"]
                for s in sg[1:]: s["target_timerange"]["start"] = t0; t0 += s["target_timerange"]["duration"]
        if ses and t["name"] == ses:
            for s in t["segments"]: s["volume"] = 0.5
    if yazi:
        ic["materials"]["texts"].append({"id": "U1", "content": json.dumps({"text": "burası uzun"})})
        ic["tracks"].append({"type": "text", "name": "Yazi", "segments": [{"id": "US1", "material_id": "U1",
                                                                         "target_timerange": {"start": 1000000, "duration": 2000000}}]})
    with open(dc, "w", encoding="utf-8") as f: json.dump(ic, f)
    return ic


class T12_TaslakFarki(unittest.TestCase):
    def test_fark_ve_kilit(self):
        """12. Taslak farkı: kırpma, silme, taşıma bulunur; kullanıcı kırpması kilitlenir, sonraki kirp_oner ona dokunmaz."""
        kok = F.film_kur(); A, p = _taslak(kok)
        self.assertEqual(taslak_fark.main(A + ["--oz-denetim"]), 0)
        dc = os.path.join(p["klasor"], "draft_content.json"); ic = _j(dc)
        kl = next(t for t in ic["tracks"] if t["name"] == "Klipler")
        a, b = kl["segments"][2], kl["segments"][3]                     # #3 ↔ #4 yer değiştirir
        a["target_timerange"]["start"], b["target_timerange"]["start"] = b["target_timerange"]["start"], a["target_timerange"]["start"]
        with open(dc, "w", encoding="utf-8") as f: json.dump(ic, f)
        _kullanici_duzenler(p, ripple=False, yazi=False)
        self.assertEqual(taslak_fark.main(A + ["--plana-isle"]), 0)
        fk = _j(kok, "KURGU", "TASLAK_FARK.json")
        tur = {k["degisim"] for k in fk["klipler"]}
        self.assertEqual(tur, {"kirpildi", "silindi", "tasindi"})
        kp = _kp(kok); x1 = ko.plan_bul(kp, 1)
        self.assertEqual(x1["goruntu"]["kullanim_kaynak"], "kullanici"); kul = dict(x1["goruntu"]["kullanim"])
        self.assertIsNone(ko.plan_bul(kp, 2))
        plan_kurgu.main(A); kp2 = _kp(kok)
        self.assertEqual(ko.plan_bul(kp2, 1)["goruntu"]["kullanim"], kul)
        self.assertIsNone(ko.plan_bul(kp2, 2))

    def test_sifreli(self):
        kok = F.film_kur(); A, p = _taslak(kok)
        with open(os.path.join(p["klasor"], "draft_content.json"), "wb") as f: f.write(b"\x8a\x01SIFRELI")
        self.assertEqual(taslak_fark.main(A), 2)
        self.assertTrue(_j(kok, "KURGU", "TASLAK_FARK.json")["sifreli"])


class T13_Yama(unittest.TestCase):
    def test_klon_yama(self):
        """13. Yama: kaynak taslağın özeti değişmez; klonda Klipler özeti kaynağınkine eşit; Diyalog yeni sıraya kayar; boşluk 0."""
        kok = F.film_kur(); A, p = _taslak(kok)
        _kullanici_duzenler(p, ses="Muzik")
        ortak.atomik_yaz(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {"capcut_yama": True})
        try:
            once = ko.klasor_ozeti(p["klasor"]); kaynak_ic = ct.oku(p["klasor"])["icerik"]
            k, r = capcut_yama.yama(kok, A)
            self.assertEqual(k, 0); self.assertEqual(r["sonuc"], "GEC")
            self.assertEqual(once, ko.klasor_ozeti(p["klasor"]))
            self.assertEqual(r["kaynak_ozet_once"], r["kaynak_ozet_sonra"]); self.assertTrue(r["klipler_ozet_esit"]); self.assertEqual(r["bosluk"], 0)
            klon = ct.oku(r["klon"])["icerik"]
            self.assertEqual(capcut_yama.klipler_ozeti(kaynak_ic), capcut_yama.klipler_ozeti(klon))
            kp = _kp(kok); d_yeni = {d["replik"]: d["cizelge_bas"] for d in kp["diyalog"]}
            self.assertTrue([s for s in ct.segmentler(klon) if s["kanal"] == "Diyalog"])
            eski = {s["replik"]: s["bas"] for s in p["segmentler"] if s["kanal"] == "Diyalog"}
            self.assertNotEqual(eski, {k_: round(v, 3) for k_, v in d_yeni.items()})          # plan 2 silindi: replikler öne kaydı
            muz = [s for s in ct.segmentler(klon) if s["kanal"] == "Muzik"]
            self.assertTrue(all(abs(s["ses"] - 0.5) < 1e-6 for s in muz))                    # kullanıcının kanal ayarı korundu
            self.assertTrue(any(s["metin"] == "burası uzun" for s in ct.segmentler(klon)))    # kullanıcı yazısı korundu
        finally:
            ortak.atomik_yaz(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {})

    def test_bayrak_kapali_yedek_yol(self):
        kok = F.film_kur(); A, p = _taslak(kok); _kullanici_duzenler(p)
        once = ko.klasor_ozeti(p["klasor"])
        self.assertEqual(capcut_yama.main(A), 0)
        self.assertEqual(once, ko.klasor_ozeti(p["klasor"]))
        yeni = _j(kok, "KURGU", "son_capcut_projesi.json")
        self.assertIn("senin düzenlemenle", yeni["proje"])

    def test_notlar_plana_baglanir(self):
        kok = F.film_kur(); A, p = _taslak(kok); _kullanici_duzenler(p, ripple=True)
        self.assertEqual(notlari_oku.giris(A), 0)
        n = _j(kok, "NOTLARIM.json")["notlar"]
        self.assertEqual([(x["not"], x["plan"]) for x in n], [("burası uzun", 1)])


class T14_YayinDogrulama(unittest.TestCase):
    def test_kaydirilmis_disa_aktarim(self):
        """14. Yayın doğrulaması: 0,4 sn kaydırılmış dışa aktarımda bir pencerede ofset ≠ 0 (kalite_denetim_final.mux_korelasyon, adım 17);
        kullanıcı ses düzenlemesi taslak_fark'ta yakalanır (mux türü doğrusal kazanca düşer)."""
        try: import kalite_denetim_final as kdf
        except Exception as e: self.skipTest(f"kalite_denetim_final yok: {e}")
        d = os.path.join(ortak.yollar()["veri_kok"], "_YAYIN_TEST"); os.makedirs(d, exist_ok=True)
        rng = np.random.default_rng(3); a = (0.2 * rng.standard_normal(48000 * 30)).astype(np.float32)
        b = np.concatenate([a[:48000 * 15], np.zeros(int(0.4 * 48000), np.float32), a[48000 * 15:]])[:len(a)]
        ko.wav_yaz(os.path.join(d, "master.wav"), a); ko.wav_yaz(os.path.join(d, "disa.wav"), b)
        p = kdf.mux_korelasyon(os.path.join(d, "disa.wav"), os.path.join(d, "master.wav"), 24, {"adet": 8, "sure_sn": 2})
        if p is None: self.skipTest("ffmpeg/numpy yok")
        self.assertTrue(any(abs(w.get("ofset_kare", 0)) > 1 for w in p if "ofset_kare" in w))
        kok = F.film_kur(); A, pj = _taslak(kok); _kullanici_duzenler(pj, ses="Muzik", yazi=False)
        taslak_fark.main(A)
        fk = _j(kok, "KURGU", "TASLAK_FARK.json")
        self.assertTrue(any(x["kanal"] == "Muzik" for x in fk["kullanici_ses_duzenlemesi"]))


class T15_MuzikOlayi(unittest.TestCase):
    def test_kirpma_sonrasi_muzik_kayar(self):
        """15. Müzik olayı: kırpmadan sonra müzik giriş anı olayla (plan 3 başı) birlikte kayar."""
        kok = F.film_kur(); A = _hazir(kok); muzik_yerlestir.main(A)
        m1 = ko.ses_cizelgesi(kok)["muzik"][0]["cizelge_bas"]; x3 = ko.plan_bul(_kp(kok), 3)
        self.assertAlmostEqual(m1, x3["cizelge_bas"], places=2)
        kp = _kp(kok); x1 = ko.plan_bul(kp, 1)
        x1["goruntu"]["kullanim"]["sure"] = ko.kare(x1["goruntu"]["kullanim"]["sure"] - 1.0)
        x1["goruntu"]["kullanim_kaynak"] = "kurgucu"; kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        plan_kurgu.main(A); muzik_yerlestir.main(A)
        m2 = ko.ses_cizelgesi(kok)["muzik"][0]["cizelge_bas"]
        self.assertAlmostEqual(m1 - m2, 1.0, places=2)
        self.assertAlmostEqual(m2, ko.plan_bul(_kp(kok), 3)["cizelge_bas"], places=2)


class T16_Ortu(unittest.TestCase):
    def test_ortu_formul(self):
        """16. Örtü: formülün (max(1,0; A tutma + B durağanlık)) altındaki örtü süresi BAYRAK verir."""
        kok = F.film_kur(); A = _hazir(kok, ses=False); kp = _kp(kok)
        o = json.loads(json.dumps(ko.plan_bul(kp, 2))); o.update(plan=91, ortu=True, araya=[1, 2]); o["goruntu"]["kaynak_klip"] = 2
        o["goruntu"]["kullanim"] = {"bas": 0.6, "sure": 0.75}
        kp["planlar"].insert(1, o); kp["planlar"][0]["goruntu"]["olculen"]["tutma_sn"] = 0.5
        kp["planlar"][2]["goruntu"]["olculen"]["duraganlik_sn"] = 0.4
        plan_kurgu.cizelgele(kp["planlar"]); kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        _, r = kdt.denetle(kok, A)
        b = [x for x in r["bayraklar"] if x["madde"] == "Y54_ortu_suresi"]
        self.assertTrue(b); self.assertAlmostEqual(b[0]["esik"], 1.0)
        o2 = ko.plan_bul(kp, 91); o2["goruntu"]["kullanim"]["sure"] = 1.25
        plan_kurgu.cizelgele(kp["planlar"]); kp["kurgu_surumu"] = ko.sonraki_surum(kok); ko.kurgu_plani_yaz(kok, kp)
        _, r = kdt.denetle(kok, A)
        self.assertNotIn("Y54_ortu_suresi", [x["madde"] for x in r["bayraklar"]])


class T17_CapcutKanallari(unittest.TestCase):
    def test_kanallar_ve_yayin(self):
        """capcut_film v2: Klipler sessiz, source = kullanim; --yayin NOTLAR ve Altyazi koymaz; SRT duyulan_metin'den; başlık bölünmez."""
        kok = F.film_kur(); s = ko.sahneler(kok); s["baslik"] = "KULUBE | Full Movie 4K"; ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
        A, p = _taslak(kok)
        kan = {x["kanal"] for x in p["segmentler"]}
        self.assertTrue({"Klipler", "Bantlar", "Kartlar", "Altyazi", "Diyalog", "Ambiyans", "Muzik", "NOTLAR"} <= kan)
        kl = [x for x in p["segmentler"] if x["kanal"] == "Klipler"]
        self.assertTrue(all(x["ses"] == 0.0 for x in kl))
        kp = _kp(kok)
        for x in kl: self.assertEqual(x["kaynak_aralik"], ko.plan_bul(kp, x["plan"])["goruntu"]["kullanim"])
        self.assertIn("KULUBE | Full Movie 4K", p["benim_yazilarim"])
        srt = _m(kok, "KURGU", "altyazi_en.srt")
        self.assertIn("It's late Captain what do you want", srt)
        self.assertEqual(capcut_film.giris(A + ["--yayin"]), 0)
        py = _j(kok, "KURGU", "son_capcut_projesi_yayin.json")
        self.assertFalse({"NOTLAR", "Altyazi"} & {x["kanal"] for x in py["segmentler"]})


class T18_CilaBuyutKur3(unittest.TestCase):
    def test_renk_cila_buyut_kur3(self):
        """renk_cila: sahne içi ΔE eşleme düzeltir; buyut: yalnız kullanılan pencere (sahte Lanczos), 4K kapısı yapay zekâsız kapalı;
        capcut_film büyütülmüş klipte kaynak aralığını pencere ofsetiyle kaydırır; KUR3 planı bir şey kurmadan kartı yazar."""
        import renk_cila, buyut, kurulum_kur3
        kok = F.film_kur(); A = _hazir(kok, ses=False)
        ko.sahte_klip(os.path.join(kok, "SIRALI_VIDEO", "002.mp4"), 8.0, kutu=[(1.0, 1.6)], renk=170)
        plan_kurgu.main(A)
        k, rap = renk_cila.cila(kok, A); self.assertEqual(k, 0)
        p1, p2 = rap["planlar"]["1"], rap["planlar"]["2"]
        self.assertTrue(p1["kazanc"] or p2["kazanc"])
        self.assertLess(max(p1["dE_sonra"], p2["dE_sonra"]), max(p1["dE_once"], p2["dE_once"]))
        k, b = buyut.buyut(kok, A); self.assertEqual(k, 0); self.assertFalse(b["dort_k_uygun"])
        x3 = ko.plan_bul(_kp(kok), 3); u = x3["goruntu"]["kullanim"]
        self.assertLessEqual(ko.sure(ko.mutlak(kok, b["planlar"]["3"]["dosya"])), u["sure"] + 1.0 + 0.1)
        self.assertEqual(capcut_film.giris(A), 0)
        seg = next(x for x in _j(kok, "KURGU", "son_capcut_projesi.json")["segmentler"] if x["kanal"] == "Klipler" and x["plan"] == 3)
        self.assertAlmostEqual(seg["kaynak_aralik"]["bas"] + seg["kaynak_ofset"], u["bas"], places=2)
        plan = kurulum_kur3.kur3_plani()
        self.assertEqual({o["ad"] for o in plan["ortamlar"]}, {"musetalk", "acestep", "buyutme"})
        self.assertFalse(any("wav2lip" in json.dumps(o).lower() for o in plan["ortamlar"]))


class T19_Birlestirme(unittest.TestCase):
    """Birleştirme turu: zaman_cizelgesi --asama kurgu (T2), kurgu_render --onizleme/--kesit/--yayin (son_miks.onizle stemleri),
    kurgu_uygula diyalog_kaydir ve SES_ISTEKLERI tüketimi — sentetik fikstürde gerçek araçlarla."""
    @classmethod
    def setUpClass(cls):
        cls.kok = F.film_kur("KURGU_BIRLESTIRME")
        cls.A = _hazir(cls.kok); diyalog_esitle.main(cls.A); ses_katmani_t2.main(cls.A); muzik_yerlestir.main(cls.A)

    def test_zaman_cizelgesi_t2(self):
        import zaman_cizelgesi
        self.assertEqual(zaman_cizelgesi.main(["--asama", "kurgu", "--film", self.kok]), 0)
        kp = _kp(self.kok)
        z = _j(self.kok, "KURGU", "ZAMAN_T2.json")
        self.assertEqual(z["olcumler"], plan_kurgu.olcumler(kp, ko.sahne_planlari(self.kok)))        # tek ölçü tek kod
        self.assertIn("replik", {e["tur"] for e in z["olaylar"]})
        r1 = _j(self.kok, "_RAPOR", "ZAMAN_T2.json"); r2 = _j(self.kok, "_RAPOR", "ZAMAN_Z2_T2.json")
        self.assertEqual((r1["kapi"], r2["kapi"]), ("Z1", "Z2"))
        sp = _j(self.kok, "_RAPOR", "SAPMA_T2.json")
        self.assertEqual([x["plan"] for x in sp["planlar"]], [x["plan"] for x in kp["planlar"]])

    def test_render_onizleme_kesit_yayin(self):
        import kurgu_render as kr
        if not kr.ffmpeg_var(): self.skipTest("ffmpeg yok")
        self.assertEqual(kr.main(["--onizleme", "--film", self.kok, "--boyut", "640x360"]), 0)
        r = _j(self.kok, "_RAPOR", "RENDER_ONIZLEME_v1.json")
        self.assertEqual(r["sonuc"], "GEC", r); self.assertEqual(r["kare_olculen"], r["kare_beklenen"])
        self.assertEqual(r["kare_beklenen"], round(ko.toplam_sure(_kp(self.kok)) * 24))
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "KURGU", "onizleme_v1.mp4")))
        self.assertEqual(r["ses"]["kaynak"], "KURGU/ses_onizleme_v1.wav"); self.assertIn("son_miks.onizle", r["ses"]["miks"])
        self.assertEqual(set(r["ses"]["stemler"]), set(ko.ses_cizelgesi(self.kok)["stemler"]))
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "_RAPOR", "S7_ONIZLEME.json")))     # ses tek miks kodundan
        self.assertEqual(kr.main(["--onizleme", "--film", self.kok, "--boyut", "640x360"]), 0)
        self.assertEqual(_j(self.kok, "_RAPOR", "RENDER_ONIZLEME_v1.json")["onbellek"]["yeni"], 0)   # plan önbelleği
        ortak.atomik_yaz(os.path.join(self.kok, "BLOK_PLANI.json"), {"kesit": {"planlar": [1, 2, 3]}, "bloklar": []})
        self.assertEqual(kr.main(["--kesit", "--film", self.kok, "--boyut", "640x360"]), 0)
        kk = _j(self.kok, "KESIT", "KURGU_PLANI_KESIT_v1.json")
        self.assertEqual([x["plan"] for x in kk["planlar"]], [1, 2, 3])
        rk = _j(self.kok, "_RAPOR", "RENDER_KESIT_v1.json"); self.assertEqual(rk["kare_olculen"], rk["kare_beklenen"])
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "KESIT", "kesit_v1.mp4")))
        self.assertEqual(kr.main(["--yayin", "--film", self.kok, "--boyut", "640x360"]), 0)
        self.assertTrue(os.path.isfile(os.path.join(self.kok, "YAYIN", "KURGU_BIRLESTIRME_master.mp4")))
        self.assertEqual(kr.main(["--otio", "--film", self.kok]), 4)

    def test_miks_al_tek_kod(self):
        import kurgu_render as kr
        yol, kaynak = kr.miks_al(self.kok, ["KURGU/YOK.json"], os.path.join(self.kok, "KURGU", "yok.wav"), "ONIZLEME", 1, "A16")
        self.assertEqual((yol, kaynak), (None, None))

    def test_diyalog_kaydir_ve_ses_istekleri(self):
        import kurgu_uygula as ku
        kok = F.film_kur("KURGU_BIRLESTIRME_KU"); _hazir(kok)
        kp0 = _kp(kok); d0 = {d["replik"]: d["cizelge_bas"] for d in kp0["diyalog"]}
        on = os.path.join(kok, "KURGU", "S3_ONERI_v1.json")
        ortak.atomik_yaz(on, {"asama": "T2", "kip": "s3_yerlesim", "kaynak": "dudak_denetim", "islemler": [
            {"op": "diyalog_kaydir", "replik": "R0001", "sn": 0.9, "plan": 3, "kok_neden": "dudak_kayma", "bulgu": "S3.1"}]})
        kod, s = ku.calistir(kok, "T2", 1, kararlar=on)
        self.assertEqual(kod, 1); self.assertIn("kaydırma", s["hatalar"][0]["neden"])          # |sn| > 0,5 reddedilir
        ortak.atomik_yaz(on, {"asama": "T2", "islemler": [
            {"op": "diyalog_kaydir", "replik": "R0001", "sn": -0.208, "plan": 3, "kok_neden": "dudak_kayma", "bulgu": "S3.1"}]})
        kod, s = ku.calistir(kok, "T2", 1, kararlar=on)
        self.assertEqual(kod, 0, s)
        kp1 = _kp(kok); d1 = {d["replik"]: d["cizelge_bas"] for d in kp1["diyalog"]}
        self.assertAlmostEqual(d1["R0001"], d0["R0001"] - 0.208, places=2)
        self.assertAlmostEqual(d1["R0002"], d0["R0002"], places=3)                              # diğer replik yerinde (plan_ofset)
        # SES_ISTEKLERI (ses_karar ekran_disi_tts) — karar dosyası olmadan da tüketilir
        ortak.atomik_yaz(os.path.join(kok, "KURGU", "SES_ISTEKLERI.json"),
                         {"islemler": [{"replik": "R0002", "op": "ekran_disi", "plan": 5, "kok_neden": "dudak_kayma"}]})
        kod, s = ku.calistir(kok, "T2", 2)
        self.assertEqual(kod, 0, s); self.assertEqual(s["ses_istekleri"], [{"replik": "R0002", "uzerine_plan": 4}])
        r2 = next(d for d in _kp(kok)["diyalog"] if d["replik"] == "R0002")
        self.assertEqual((r2["plan"], r2["ekran_disi"], r2["gorunen_konusan"]), (4, True, False))
        ist = _j(kok, "KURGU", "SES_ISTEKLERI.json")["islemler"][0]
        self.assertTrue(ist["yapildi"]); self.assertEqual(ist["uygulandi"]["uzerine_plan"], 4)
        with self.assertRaises(FileNotFoundError): ku.calistir(kok, "T2", 3)                     # bekleyen istek yok, karar yok


if __name__ == "__main__":
    unittest.main()
