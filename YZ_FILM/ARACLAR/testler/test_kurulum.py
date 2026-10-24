"""PR-2b testleri (TASARIM §9 adım 4, §6.9, §8.2, §5.6): kurulum KUR1 kuru çalıştırması geçici klasörlerde, .bat üretimi
(ASCII + CRLF, mutlak yol, göreli ..\\..\\ARACLAR yok), GUNCELLE çakışma fikstüründe hiçbir dosyayı değiştirmeden durur, anahtar
dosyalarının içeriği hiçbir zaman yazdırılmaz/açılmaz, izin paneli, DURDUR/DEVAM, sabit adres + SHA-1 indirmesi. Ağ ve kredi yok."""
import os, sys, io, json, shutil, hashlib, tempfile, unittest, contextlib, subprocess, builtins, pathlib
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
DEPO = os.path.dirname(os.path.dirname(ARACLAR))
sys.path.insert(0, ARACLAR); sys.path.insert(0, HERE)
import _ortam  # noqa: F401  (geçici YOLLAR.json; araçlardan önce)
import ortak, kurulum, bat_yenile, bat_isleri, yeni_film, veri_emniyet

GIZLI = "GIZLI_DEGER_9f3a71"


def jl(p, **_):
    with open(p, encoding="utf-8") as f: return json.load(f)


def txt(p, kip="r", **k):
    with open(p, kip, **({} if "b" in kip else dict(dict(encoding="utf-8", newline=""), **k))) as f: return f.read()


def yaz(p, m):
    with open(p, "w", encoding="utf-8") as f: f.write(m)


def sessiz(fn, *a, **k):
    o = io.StringIO()
    with contextlib.redirect_stdout(o): r = fn(*a, **k)
    return r, o.getvalue()


class Ortam(unittest.TestCase):
    """Her test: ayrı geçici depo + veri + YOLLAR.json (gerçek depoya ve _ortam'ın dosyalarına dokunmaz)."""
    def setUp(self):
        self.kok = tempfile.mkdtemp(dir=_ortam.KOK)
        self.masa = os.path.join(self.kok, "Masaustu"); self.veri = os.path.join(self.masa, "YZ_FILM")
        self.depo = os.path.join(self.masa, "YZ_FILM_SET"); os.makedirs(os.path.join(self.depo, "YZ_FILM", "AYARLAR"))
        for ad in ("ai84_anahtar.txt", "telegram_bot.txt"): open(os.path.join(self.depo, "YZ_FILM", "AYARLAR", ad), "w").close()
        os.makedirs(self.veri)
        self.yollar = os.path.join(self.kok, "YOLLAR.json")
        p = mock.patch.dict(os.environ, {"YZ_FILM_YOLLAR": self.yollar, "YZ_FILM_ORTAM": "bulut"}); p.start(); self.addCleanup(p.stop)
        y = ortak.varsayilan_yollar(self.veri); y["depo_kok"] = self.depo; y["capcut_taslak"] = os.path.join(self.kok, "YOK")
        y["onbellek"] = os.path.join(self.kok, "onbellek"); ortak.atomik_yaz(self.yollar, y)

    def kur(self, **k):
        ag_cagrisi = []
        def ag(*a, **kw): ag_cagrisi.append(a); raise OSError("ağ yasak (test)")
        cikti = lambda cmd, timeout=30: "2.1.305 (Claude Code)" if cmd[0] == "claude" else "git version 2.40"
        with mock.patch("socket.create_connection", ag), mock.patch("urllib.request.urlopen", ag), \
             mock.patch.object(kurulum, "_cikti", cikti), mock.patch.object(kurulum, "pip", lambda *a: self.fail("pip çağrıldı")), \
             mock.patch.object(kurulum, "model_indir", lambda *a: self.fail("model indirildi")):
            kod, out = sessiz(kurulum.Kurulum(veri=self.veri, depo=self.depo, kuru=True, **k).calis)
        self.assertEqual(ag_cagrisi, [], "kuru çalıştırmada ağa çıkıldı")
        return kod, out


class KuruKurulum(Ortam):
    def test_kuru_calistirma_yerel_dosyalar(self):
        kod, out = self.kur()
        self.assertIn(kod, (0, 1))                                  # ffmpeg/Chrome/CapCut bulutta yok → 1 olabilir
        A = os.path.join(self.veri, "AYARLAR")
        a = jl(os.path.join(A, "FILM_AYAR.json"), encoding="utf-8")
        self.assertEqual((a["_surum"], a["ortam"], a["mod"]), (3, "bulut", "tam_otomatik"))
        self.assertFalse(any(a["izinler"].values())); self.assertEqual(a["butce"]["usd_tavan_film"], 0)
        for k in ("gorsel_gunluk_tavan", "disk_bos_min_gb", "paralel_max"): self.assertNotIn(k, a)     # güvenlik sayısı yazılmaz (D-34)
        s = jl(os.path.join(self.depo, ".claude", "settings.local.json"), encoding="utf-8")
        self.assertIn(self.veri, s["permissions"]["additionalDirectories"])
        self.assertTrue(os.path.isabs(s["env"]["YZ_FILM_PYTHON"]))
        self.assertTrue(s["env"]["PATH"].startswith(os.path.dirname(s["env"]["YZ_FILM_PYTHON"])))
        self.assertNotIn("HF_HUB_OFFLINE", s["env"])                 # modeller indirilmedi
        py = txt(os.path.join(self.depo, ".claude", "bin", "python_yolu.txt"), encoding="utf-8").strip()
        self.assertTrue(os.path.isabs(py))
        r = jl(os.path.join(A, "KURULUM_RAPORU.json"), encoding="utf-8")
        self.assertTrue(r["kuru"]); self.assertEqual(r["claude"]["uygun"], True); self.assertFalse(r["git"]["depo_git"])
        self.assertIn("SENDEN İSTENEN TEK KARAR", r["sozlesme_karti"])
        durum = {m["ad"]: m["durum"] for m in r["maddeler"]}
        self.assertEqual(durum["KUR1 kütüphaneleri"], "atlandı"); self.assertEqual(durum["modeller"], "atlandı")
        self.assertIn("kuru", next(m["mesaj"] for m in r["maddeler"] if m["ad"] == "modeller"))
        self.assertEqual(durum["GUNCELLE.bat"], "bilgi")             # ZIP kurulumu: kapalı + bilgi
        for ad in bat_yenile.DEPO_KOKU: self.assertTrue(os.path.isfile(os.path.join(self.depo, ad)), ad)
        self.assertTrue(os.path.isfile(os.path.join(self.masa, "FILM_SETI.bat")))
        self.assertTrue(os.path.isfile(os.path.join(self.veri, "CLAUDE.md")))      # veri emniyeti çalıştı
        self.assertIn("Müzik çekirdek seti", out); self.assertIn("ÇALIŞIYOR / ÇALIŞMIYOR", out)
        self.assertFalse(os.path.exists(os.path.join(DEPO, "YZ_FILM", "AYARLAR", "KURULUM_RAPORU.json")))

    def test_izinler_korunur_ve_onayli_kip_gocu(self):
        self.kur()
        p = os.path.join(self.veri, "AYARLAR", "FILM_AYAR.json")
        a = jl(p, encoding="utf-8"); a["izinler"]["gece_flow"] = True; a["butce"]["usd_tavan_film"] = 5
        a["gorsel_gunluk_tavan"] = 10; ortak.atomik_yaz(p, a)
        self.kur()
        b = jl(p, encoding="utf-8")
        self.assertTrue(b["izinler"]["gece_flow"]); self.assertEqual(b["butce"]["usd_tavan_film"], 5)
        self.assertEqual(b["gorsel_gunluk_tavan"], 10)              # kullanıcının sıkı değeri korunur (esikler yalnız sıkılaştırır)
        e = kurulum.film_ayar_birlestir({"_surum": 2, "izinler": {"onayli_kip": True, "gece_flow": "evet"}})
        self.assertEqual(e["mod"], "onayli"); self.assertNotIn("onayli_kip", e["izinler"]); self.assertIs(e["izinler"]["gece_flow"], False)

    def test_anahtar_icerigi_yazdirilmaz_ve_acilmaz(self):
        dk = os.path.join(self.depo, "YZ_FILM", "AYARLAR", "ai84_anahtar.txt")
        yaz(dk, GIZLI)
        os.makedirs(os.path.join(self.veri, "AYARLAR"), exist_ok=True)
        vk = [os.path.join(self.veri, "AYARLAR", a) for a in kurulum.VERI_ANAHTARLARI]
        for p in vk: yaz(p, GIZLI)
        acilan = []; asil = builtins.open
        def izle(f, *a, **k):
            acilan.append(os.path.abspath(str(f))); return asil(f, *a, **k)
        K = kurulum.Kurulum(veri=self.veri, depo=self.depo, kuru=True)
        with mock.patch.object(builtins, "open", izle):
            dolu = kurulum.depo_anahtar_denetimi(self.depo)
            sessiz(K.yollar_ve_emniyet); acilan.clear()                # (veri_emniyet ayrı araç; paylaşılan istekte)
            _, out1 = sessiz(K.anahtarlar)
            kod, out2 = sessiz(bat_isleri.gemini_test)
        self.assertEqual(dolu, ["YZ_FILM/AYARLAR/ai84_anahtar.txt"])
        for p in [dk] + vk: self.assertNotIn(os.path.abspath(p), acilan, "anahtar dosyası açıldı: " + p)
        self.assertEqual(kod, 0)
        _, out3 = self.kur()
        rapor = txt(os.path.join(self.veri, "AYARLAR", "KURULUM_RAPORU.json"), encoding="utf-8")
        gd = txt(os.path.join(self.veri, "AYARLAR", "GEMINI_DURUMU.json"), encoding="utf-8")
        for metin in (out1, out2, out3, rapor, gd): self.assertNotIn(GIZLI, metin)
        self.assertIn("ai84_anahtar.txt", out3); self.assertIn("içerik gösterilmedi", out3)
        self.assertEqual(json.loads(gd)["olculemedi"], True)

    def test_gemini_anahtar_yoksa_kullanici_isi(self):
        kod, out = sessiz(bat_isleri.gemini_test)
        self.assertEqual(kod, 2); self.assertIn("AI Studio", out)
        self.assertTrue(os.path.isfile(os.path.join(self.veri, "AYARLAR", "gemini_anahtar.txt")))
        yaz(os.path.join(self.veri, "AYARLAR", "gemini_anahtar.txt"), GIZLI)
        kod, out = sessiz(bat_isleri.gemini_test, True)
        self.assertEqual(kod, 0); self.assertNotIn(GIZLI, out)
        self.assertEqual(jl(os.path.join(self.veri, "AYARLAR", "GEMINI_DURUMU.json"))["gemini_katman"], "ucretsiz")

    def test_kur3_izinsiz_kurmaz_onayla_yollar_yazar(self):
        import kurulum_kur3 as k3
        kurulan = []
        with mock.patch.object(k3, "kur3_kur", lambda plan, calistir=False: kurulan.append(calistir) or []):
            kod, out = sessiz(kurulum.main, ["--kur3", "--gerekenler", "musetalk"])
            self.assertEqual(kod, 0); self.assertEqual(kurulan, []); self.assertIn("izni yok", out)
            kod, out = sessiz(kurulum.main, ["--kur3", "--gerekenler", "musetalk", "--onay", "--kuru"])
            self.assertEqual(kurulan, [])                                    # kuru: izin olsa da kurulmaz
            kod, r = sessiz(kurulum.kur3, {"musetalk"}, True)[0]
        self.assertEqual((kod, kurulan, r["kuruldu"]), (0, [True], ["musetalk"]))
        self.assertIn("musetalk", jl(self.yollar)["ortamlar"])

    def test_kur2_plan_kurallari(self):
        import ses_kiyas
        kos = []
        plan = {"kur": True, "motor": "openvoice", "python_yolu": os.path.join(self.kok, "venv", "python"), "deneme_kipi": True,
                "neden": "lisans 'bilinmiyor'", "adimlar": [{"ne": "venv", "komut": ["py", "-m", "venv", "x"]}]}
        with mock.patch.object(ses_kiyas, "kur2_plani", lambda: plan):
            k, r = sessiz(kurulum.kur2, False, False, kos=lambda c: kos.append(c) or True)[0]
            self.assertEqual((r["durum"], kos), ("lisans", []))              # bilinmiyor lisans → yalnız --deneme
            k, r = sessiz(kurulum.kur2, True, True, kos=lambda c: kos.append(c) or True)[0]
            self.assertEqual((r["durum"], kos), ("plan", []))                # kuru → yalnız plan
            with mock.patch.object(kurulum.os, "name", "nt"):
                k, r = sessiz(kurulum.kur2, False, True, kos=lambda c: kos.append(c) or True)[0]
        self.assertEqual((r["durum"], len(kos)), ("kuruldu", 1))
        self.assertEqual(jl(self.yollar)["ortamlar"]["ses_donustur"], plan["python_yolu"])
        with mock.patch.object(ses_kiyas, "kur2_plani", lambda: {"kur": False, "neden": "Ö0-c ölçülmedi"}):
            self.assertEqual(sessiz(kurulum.main, ["--ses-ortamlari"])[0], 0)

    def test_kur1_model_plani_ve_politika(self):
        kod, out = self.kur()
        r = jl(os.path.join(self.veri, "AYARLAR", "KURULUM_RAPORU.json"))
        plan = {a.get("dosya") or a.get("kimlik"): a for a in r["kur1_model_plani"]}
        mk = kurulum.model_kok(ortak.yollar())
        for d in ("face_detection_yunet_2023mar.onnx", "face_recognition_sface_2021dec.onnx", "face_landmarker.task",
                  "pose_landmarker_lite.task"):
            self.assertEqual(plan[d]["hedef"], os.path.join(mk, d)); self.assertFalse(plan[d]["hazir"])
        for k in ("facebook/dinov2-small", "openai/clip-vit-base-patch32", "google/owlv2-base-patch16-ensemble"):
            self.assertEqual(plan[k]["hedef"], os.path.join(mk, "hf"))
        import olcum.gorunum as G
        for k in (G.DINO, G.CLIP, G.OWL): self.assertIn(k, plan)                  # ölçüm kodunun okuduğu kimliklerle aynı
        self.assertTrue(os.path.isfile(os.path.join(self.veri, "BILGI", "YOUTUBE_POLITIKA.md")))
        yaz(os.path.join(self.veri, "BILGI", "YOUTUBE_POLITIKA.md"), "kullanıcı sürümü"); self.kur()
        self.assertEqual(txt(os.path.join(self.veri, "BILGI", "YOUTUBE_POLITIKA.md")), "kullanıcı sürümü")   # var olana dokunulmaz

    def test_kur1_ag_varken_indirme_ve_sha1(self):
        Y = ortak.yollar(); L = {k: {"dogrulama": "bellekten"} for k in ("yunet", "sface", "mediapipe", "clip", "dinov2-small",
                                                                          "owlv2-base", "faster-whisper", "demucs")}
        plan = kurulum.kur1_model_plani(Y, L)
        a = next(x for x in plan if x["tur"] == "dosya")
        with mock.patch("urllib.request.urlopen", lambda url, timeout=0: io.BytesIO(b"onnx")):
            s = kurulum.dosya_indir(a["url"], a["hedef"])
        self.assertEqual(s, hashlib.sha1(b"onnx").hexdigest())
        self.assertTrue(next(x for x in kurulum.kur1_model_plani(Y, L, sha1ler={a["dosya"]: s}) if x.get("dosya") == a["dosya"])["hazir"])
        self.assertFalse(next(x for x in kurulum.kur1_model_plani(Y, L, sha1ler={a["dosya"]: "0" * 40}) if x.get("dosya") == a["dosya"])["hazir"])

    def test_dogrula_kur_raporu(self):
        film = os.path.join(self.veri, "FILMLER", "F"); os.makedirs(film)
        gd = os.path.join(film, "_GOREV", "A10a-KD-s1-t1"); os.makedirs(gd)
        ortak.atomik_yaz(os.path.join(gd, "GOREV.json"), {"id": "A10a-KD-s1-t1", "tur_no": 1})
        with mock.patch.dict(os.environ, {"YZ_FILM_GOREV": gd}):
            kod, out = sessiz(kurulum.main, ["--dogrula", "--film", "--film", film])      # film.py araç sözleşmesi --film'i ekler
        self.assertEqual(kod, 0)
        r = jl(os.path.join(film, "_RAPOR", "KURULUM_FILM.json"))
        self.assertEqual((r["kapi"], r["_uretim"]["gorev"], r["_uretim"]["asama"], r["tur"]), ("KUR", "A10a-KD-s1-t1", "A10a", 1))
        import kapi
        self.assertEqual(kapi.dogrula(r), [])
        self.assertIn("basamaklar", r); self.assertIn("kapali", r); self.assertIn("olcum_durumu", r)
        h = {x["birim"] for x in r["hatalar"]}; b = {x["birim"] for x in r["bayraklar"]}
        self.assertIn("kimlik", h)                                             # bulutta model yok: KUR1 eksiği HATA
        self.assertFalse(h & {"ses_donustur", "tts_dudak", "acestep"})         # KUR2/KUR3 yalnız kendi basamağını kapatır
        self.assertTrue({"ses_donustur", "tts_dudak"} <= b)

    def test_surum_karsilastirma(self):
        self.assertEqual(kurulum.surum_ayikla("2.1.302 (Claude Code)"), (2, 1, 302))
        self.assertTrue(kurulum.surum_ayikla("2.1.4") < kurulum.CLAUDE_EN_AZ); self.assertIsNone(kurulum.surum_ayikla("yok"))


class Batlar(Ortam):
    def denetle(self, yol, python):
        ham = txt(yol, "rb"); metin = ham.decode("ascii")         # ASCII değilse burada patlar
        self.assertNotIn(b"\n", ham.replace(b"\r\n", b""), "CRLF olmalı: " + yol)
        self.assertNotIn("..\\..\\ARACLAR", metin); self.assertNotIn("../../ARACLAR", metin)
        self.assertIn("chcp 65001", metin); self.assertIn(bat_yenile.IM, metin)
        self.assertIn(f'"{os.path.abspath(python)}"', metin)
        self.assertIn(os.path.join(ARACLAR, ""), metin)
        return metin

    def test_uretim_ascii_crlf_mutlak(self):
        film = os.path.join(self.veri, "FILMLER", "F1"); os.makedirs(film)
        yaz(os.path.join(film, "SAHNELER.json"), "{}")
        r, _ = sessiz(bat_yenile.yenile)
        py = jl(self.yollar)["python"]["ana"]
        yazilan = {x["yol"] for x in r["yazilan"]}
        for ad in bat_yenile.DEPO_KOKU: self.assertIn(os.path.join(self.depo, ad), yazilan)
        for ad in bat_yenile.FILM_KLASORU: self.assertIn(os.path.join(film, ad), yazilan)
        for y in yazilan:
            m = self.denetle(y, py)
            if y.endswith("UYARI_GECTI.bat"): self.assertIn("flow_yuk.py\" --uyari-gecti", m)
        fs = txt(os.path.join(self.masa, "FILM_SETI.bat"), encoding="ascii")
        self.assertIn(f'cd /d "{self.depo}"', fs); self.assertIn("\r\nclaude\r\n", fs)
        self.assertIn('claude --continue "devam"', txt(os.path.join(film, "DEVAM.bat")))
        self.assertFalse(os.path.exists(os.path.join(self.depo, "KURULUM.bat")))        # sabit önyükleyiciye dokunulmaz
        # veri emniyeti üretilen film .bat'larını eski giriş noktası saymaz (her kurulumda taşınıp durmaz)
        self.assertEqual(veri_emniyet.tara(self.veri), [])
        r2, _ = sessiz(bat_yenile.yenile); self.assertTrue(all(x["durum"] == "ayni" for x in r2["yazilan"]))

    def test_imsiz_eski_bat_tasinir_silinmez(self):
        y = os.path.join(self.depo, "IZINLER.bat"); yaz(y, "@echo off\r\necho benim\r\n")
        r, _ = sessiz(bat_yenile.yenile, filmler=False)
        self.assertIn("tasindi_yazildi", {x["durum"] for x in r["yazilan"] if x["yol"] == y})
        eski = [str(p) for p in pathlib.Path(self.veri, "_ESKI").rglob("IZINLER.bat")]
        self.assertEqual(len(eski), 1); self.assertIn("benim", txt(eski[0]))

    def test_kural_ihlali_yazilmaz(self):
        with self.assertRaises(ValueError): bat_yenile.bat_yaz(os.path.join(self.kok, "X.bat"), "@echo off\r\n..\\..\\ARACLAR\\a.py\r\n")
        with self.assertRaises(ValueError): bat_yenile.bat_yaz(os.path.join(self.kok, "X.bat"), bat_yenile.IM + "\na\n")
        self.assertFalse(os.path.exists(os.path.join(self.kok, "X.bat")))

    def test_turkce_yol_utf8_isaretlenir(self):
        r, _ = sessiz(bat_yenile.yenile, filmler=False, python=os.path.join(self.kok, "Kullanıcı", "python.exe"))
        self.assertTrue(any(not x["ascii"] for x in r["yazilan"]))

    def test_yeni_film_memmet_giris_uretmez(self):
        b = yeni_film.batlar()
        self.assertNotIn("MEMMET_GIRIS.bat", b); self.assertEqual(set(b), set(yeni_film.BATS))
        self.assertTrue(set(b) <= set(jl(os.path.join(ARACLAR, "veri", "ADLAR.json"), encoding="utf-8")["bat"]["film_klasoru"]))
        for ic in b.values(): self.assertNotRegex(ic, r"memmet|film\.py")

    def test_depo_koku_kurulum_bat(self):
        p = os.path.join(DEPO, "KURULUM.bat")
        ham = txt(p, "rb"); m = ham.decode("ascii")
        self.assertNotIn(b"\n", ham.replace(b"\r\n", b"")); self.assertNotIn("..\\..\\ARACLAR", m)
        self.assertIn("python_yolu.txt", m); self.assertIn("YZ_FILM\\ARACLAR\\kurulum.py", m)


def git(d, *a):
    r = subprocess.run(["git", "-C", d, "-c", "user.email=t@t", "-c", "user.name=t", "-c", "init.defaultBranch=main"] + list(a),
                       capture_output=True, text=True)
    if r.returncode: raise AssertionError(r.stderr)
    return r.stdout


def anlik(d):
    """Çalışma ağacının (.git hariç) bayt düzeyinde görüntüsü + HEAD."""
    out = {}
    for k, ds, fs in os.walk(d):
        ds[:] = [x for x in ds if x != ".git"]
        for f in fs: out[os.path.relpath(os.path.join(k, f), d)] = txt(os.path.join(k, f), "rb")
    return out, git(d, "rev-parse", "HEAD")


@unittest.skipUnless(shutil.which("git"), "git yok")
class Guncelle(unittest.TestCase):
    def setUp(self):
        self.k = tempfile.mkdtemp(dir=_ortam.KOK); self.uzak = os.path.join(self.k, "uzak.git")
        git(self.k, "init", "--bare", "-q", self.uzak)
        self.gel = os.path.join(self.k, "gelistirici"); git(self.k, "clone", "-q", self.uzak, self.gel)
        yaz(os.path.join(self.gel, "A.txt"), "a1\n"); yaz(os.path.join(self.gel, ".gitignore"), "YOLLAR.json\n")
        git(self.gel, "add", "."); git(self.gel, "commit", "-qm", "ilk"); git(self.gel, "push", "-q", "origin", "HEAD")
        self.kul = os.path.join(self.k, "kullanici"); git(self.k, "clone", "-q", self.uzak, self.kul)
        yaz(os.path.join(self.gel, "A.txt"), "a2\n"); yaz(os.path.join(self.gel, "YENI.txt"), "yeni\n")
        os.makedirs(os.path.join(self.gel, "D")); yaz(os.path.join(self.gel, "D", "x.txt"), "x\n")
        git(self.gel, "add", "-f", "."); git(self.gel, "commit", "-qm", "iki"); git(self.gel, "push", "-q", "origin", "HEAD")

    def dene(self):
        once = anlik(self.kul)
        kod, out = sessiz(bat_isleri.guncelle, self.kul, bat_yenile=False)
        self.assertEqual(kod, 2, out); self.assertEqual(anlik(self.kul), once, "dosya değişti"); return out

    def test_yerel_degisiklikte_durur(self):
        yaz(os.path.join(self.kul, "A.txt"), "benim\n")
        self.assertIn("yerel değişiklik", self.dene())

    def test_izlenmeyen_cakismada_durur(self):
        yaz(os.path.join(self.kul, "YENI.txt"), "benim\n")
        self.assertIn("üzerine yazacaktı", self.dene())

    def test_yok_sayilan_cakismada_ve_klasor_cakismasinda_durur(self):
        yaz(os.path.join(self.kul, "D"), "dosya\n")              # gelen klasörle aynı adda dosya
        self.dene()

    def test_yerel_commitde_durur(self):
        yaz(os.path.join(self.kul, "B.txt"), "b\n"); git(self.kul, "add", "."); git(self.kul, "commit", "-qm", "yerel")
        self.assertIn("yerel kayıt", self.dene())

    def test_temizse_ileri_sarar(self):
        yaz(os.path.join(self.kul, "BAT_URETILDI.bat"), "x")       # ilgisiz izlenmeyen dosya engellemez
        kod, out = sessiz(bat_isleri.guncelle, self.kul, bat_yenile=False)
        self.assertEqual(kod, 0, out)
        self.assertEqual(txt(os.path.join(self.kul, "A.txt")), "a2\n")
        self.assertEqual(sessiz(bat_isleri.guncelle, self.kul, bat_yenile=False)[1].strip(), "Set zaten güncel.")

    def test_zip_kurulumunda_kapali(self):
        z = os.path.join(self.k, "zip"); os.makedirs(z)
        kod, out = sessiz(bat_isleri.guncelle, z, bat_yenile=False)
        self.assertEqual(kod, 4); self.assertIn("ZIP", out)


class IzinVeFilm(Ortam):
    def test_izin_paneli(self):
        kod, out = sessiz(bat_isleri.main, ["izinler", "--ac", "gece_flow", "--usd", "3"])
        self.assertEqual(kod, 0); self.assertIn("AÇIK", out)
        a = jl(os.path.join(self.veri, "AYARLAR", "FILM_AYAR.json"), encoding="utf-8")
        self.assertTrue(a["izinler"]["gece_flow"]); self.assertEqual(a["butce"]["usd_tavan_film"], 3)
        self.assertEqual(sessiz(bat_isleri.main, ["izinler", "--ac", "kie_ai"])[0], 1)
        self.assertEqual(sessiz(bat_isleri.main, ["izinler", "--usd", "-1"])[0], 1)
        sessiz(bat_isleri.main, ["izinler", "--kapat", "gece_flow", "--mod", "onayli"])
        a = jl(os.path.join(self.veri, "AYARLAR", "FILM_AYAR.json"), encoding="utf-8")
        self.assertFalse(a["izinler"]["gece_flow"]); self.assertEqual(a["mod"], "onayli")

    def test_durdur_devam(self):
        f = os.path.join(self.veri, "FILMLER", "F"); os.makedirs(f)
        self.assertEqual(sessiz(bat_isleri.durdur, f)[0], 0); self.assertTrue(os.path.isfile(os.path.join(f, "DUR")))
        with mock.patch("shutil.which", lambda x: "/bin/claude"): kod, _ = sessiz(bat_isleri.devam, f)
        self.assertEqual(kod, 0); self.assertFalse(os.path.exists(os.path.join(f, "DUR")))
        self.assertEqual(len(os.listdir(os.path.join(f, "_ESKI"))), 1)        # taşındı, silinmedi

    def test_flow_giris_kuru(self):
        k = bat_isleri.flow_giris_komutu()
        self.assertEqual(k[-1], "--giris"); self.assertTrue(k[1].endswith("memmet.py"))
        self.assertTrue(os.path.isfile(os.path.join(self.veri, "HESAP", "FLOW_GIRIS", "SAHNELER.json")))
        self.assertEqual(sessiz(bat_isleri.flow_giris, True)[0], 0)


class Indirme(Ortam):
    def plan(self, icerik, sha=None, lisans="x"):
        kaynak = os.path.join(self.kok, "kaynak.mid"); pathlib.Path(kaynak).write_bytes(icerik)
        return {"ad": "t", "baslik": "t", "lisans": lisans, "hedef": ["onbellek", "t"],
                "dosyalar": [{"ad": "a.mid", "url": pathlib.Path(kaynak).as_uri(), "sha1": sha or hashlib.sha1(icerik).hexdigest()}]}

    def test_sha1_tutar_kurulur_tekrar_hazir(self):
        L = {"x": {"dogrulama": "bellekten"}}; Y = ortak.yollar(); g = self.plan(b"muzik")
        self.assertEqual(kurulum.indirme_uygula(g, Y, L)["durum"], "kuruldu")
        self.assertEqual(kurulum.indirme_uygula(g, Y, L)["durum"], "hazir")

    def test_sha1_tutmazsa_esk_ye_tasinir(self):
        L = {"x": {"dogrulama": "bellekten"}}; Y = ortak.yollar(); g = self.plan(b"bozuk", sha="0" * 40)
        r = kurulum.indirme_uygula(g, Y, L)
        self.assertEqual(r["durum"], "hata"); self.assertFalse(os.path.exists(os.path.join(r["hedef"], "a.mid")))
        self.assertEqual(len(list(pathlib.Path(r["hedef"], "_ESKI").rglob("*.sha1_tutmadi"))), 1)

    def test_lisans_ag_ve_secilmedi(self):
        Y = ortak.yollar(); g = self.plan(b"m")
        self.assertEqual(kurulum.indirme_uygula(g, Y, {"x": {"dogrulama": "bilinmiyor"}})["durum"], "lisans")
        self.assertEqual(kurulum.indirme_uygula(g, Y, {"x": {"dogrulama": "bilinmiyor"}}, deneme=True, ag=False)["durum"], "ag_yok")
        self.assertEqual(kurulum.indirme_uygula(dict(g, dosyalar=[]), Y, {})["durum"], "secilmedi")
        L = kurulum.lisanslar()
        self.assertFalse(kurulum.lisans_izinli(L, "muzik_cekirdek_seti")); self.assertTrue(kurulum.lisans_izinli(L, "demucs"))


if __name__ == "__main__":
    unittest.main()
