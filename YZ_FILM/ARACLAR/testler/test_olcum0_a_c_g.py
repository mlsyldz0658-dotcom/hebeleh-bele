"""Ö0-a (olcum0/kanca_deneme), Ö0-c (olcum0/ses_deneme.py) ve Ö0-g (kanal_teshis → O0g) testleri (TASARIM §1.2, §10.3, §2.2, D-25).

Tamamen çevrimdışı: gerçek Claude, gerçek model, ağ ve kredi yok; motorlar, claude -p, ffmpeg/ffprobe ve dinleyici sahte işlevlerle.
Kanca denemesi HER ZAMAN geçici bir .claude KOPYASINDA kurulur; gerçek .claude/settings.json ve settings.local.json'a dokunulmadığı
her testte sha ile denetlenir. Her test sınıfı kendi geçici veri kökünü (YOLLAR.json) kullanır: O0*.json başka testlere sızmaz.
"""
import os, sys, io, json, time, shutil, hashlib, tempfile, unittest, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for _p in (ARACLAR, HERE, os.path.join(ARACLAR, "olcum0"), os.path.join(ARACLAR, "olcum0", "kanca_deneme")):
    if _p not in sys.path: sys.path.insert(0, _p)
import _ortam
import ortak
import numpy as np

DEPO = os.path.dirname(os.path.dirname(ARACLAR))
GERCEK_AYAR = os.path.join(DEPO, ".claude", "settings.json")
GERCEK_YEREL = os.path.join(DEPO, ".claude", "settings.local.json")
SONDA = os.path.join(ARACLAR, "olcum0", "kanca_deneme", "o0a_sonda.py")


def metin(p):
    with open(p, encoding="utf-8") as f: return f.read()


def metin_yaz(p, m=""):
    with open(p, "w", encoding="utf-8") as f: f.write(m)


def json_(p):
    with open(p, encoding="utf-8") as f: return json.load(f)


def sha(p):
    if not os.path.isfile(p): return None
    with open(p, "rb") as f: return hashlib.sha1(f.read()).hexdigest()


class _VeriKoku(unittest.TestCase):
    """Sınıfa özel geçici veri kökü (YZ_FILM_YOLLAR); tearDown'da eski değere döner."""
    def setUp(self):
        self.gercek = (sha(GERCEK_AYAR), sha(GERCEK_YEREL), os.path.exists(os.path.join(DEPO, ".claude", "agents", "o0a-sonda.md")))
        self.kok = tempfile.mkdtemp(prefix="yz_o0_")
        self.veri = os.path.join(self.kok, "VERI"); os.makedirs(os.path.join(self.veri, "AYARLAR"))
        self.yollar = os.path.join(self.kok, "YOLLAR.json")
        y = ortak.varsayilan_yollar(self.veri); y["onbellek"] = os.path.join(self.kok, "ONBELLEK"); ortak.atomik_yaz(self.yollar, y)
        self._eski = os.environ.get("YZ_FILM_YOLLAR"); os.environ["YZ_FILM_YOLLAR"] = self.yollar

    def tearDown(self):
        os.environ["YZ_FILM_YOLLAR"] = self._eski
        self.assertEqual(self.gercek, (sha(GERCEK_AYAR), sha(GERCEK_YEREL),
                                       os.path.exists(os.path.join(DEPO, ".claude", "agents", "o0a-sonda.md"))),
                         "gerçek .claude dosyaları değişti")
        shutil.rmtree(self.kok, True)


# ======================================================================================================================
# Ö0-a
# ======================================================================================================================
class KancaDeneme(_VeriKoku):
    def setUp(self):
        super().setUp()
        import o0a_kos as kos, o0a_davranislar as davranislar, o0a_sonda as sonda
        self.kos, self.DV, self.sonda = kos, davranislar, sonda
        self.depo = os.path.join(self.kok, "depo"); os.makedirs(self.depo)
        shutil.copytree(os.path.join(DEPO, ".claude"), os.path.join(self.depo, ".claude"),
                        ignore=shutil.ignore_patterns("__pycache__", "settings.local.json", "python_yolu.txt"))
        self.kayit = os.path.join(self.kok, "kayit")
        self.y = kos.Yer(depo=self.depo, kayit=self.kayit, python=sys.executable)
        self.cikti = io.StringIO(); self._out = sys.stdout; sys.stdout = self.cikti

    def tearDown(self):
        sys.stdout = self._out
        super().tearDown()

    def kancala(self, olay, girdi, giris="mutlak", env=None):
        r = subprocess.run([sys.executable, SONDA, olay, "--giris", giris, "--kayit", self.kayit], input=json.dumps(girdi).encode("utf-8"),
                           capture_output=True, timeout=60, env=dict(os.environ, **(env or {})))
        return r.returncode, r.stdout.decode("utf-8")

    def olaylar(self): return self.kos.olaylar(self.y)

    # --- kurulum ve geri alma -------------------------------------------------------------------------------------
    def test_kur_ve_geri_al_onceki_yerel_ayar_aynen_doner(self):
        yerel = os.path.join(self.depo, ".claude", "settings.local.json")
        onceki = {"env": {"PATH": "C:/Python310;x"}, "permissions": {"deny": ["Read(./gizli)"], "allow": ["Bash(ls)"]}}
        ortak.atomik_yaz(yerel, onceki); s0, a0 = sha(yerel), sha(self.y.ayar)
        self.assertEqual(self.kos.kur(self.y), 0)
        b = json_(yerel)
        self.assertEqual(b["permissions"]["deny"], ["Read(./gizli)"])                      # yalnız ekler
        self.assertIn("Bash(ls)", b["permissions"]["allow"])
        self.assertEqual(b["env"]["PATH"], "C:/Python310;x"); self.assertEqual(b["env"]["O0A_SONDA_ENV"], "1")
        self.assertIn(self.y.yazma.replace("\\", "/"), b["permissions"]["additionalDirectories"])
        for olay in ("SessionStart", "PreToolUse", "SubagentStop", "Stop", "PostCompact", "PostModelSwitch", "SubagentStart", "StopFailure"):
            self.assertIn(olay, b["hooks"])
        a = [h for g in b["hooks"]["PreToolUse"] for h in g["hooks"] if "--giris A" in h["command"]][0]
        self.assertEqual((a["timeout"], a["onFailure"]), (2, "block"))
        self.assertFalse([h for g in b["hooks"]["PreToolUse"] for h in g["hooks"] if "--giris B" in h["command"] and "onFailure" in h])
        self.assertNotIn("_aciklama", b)
        self.assertTrue(os.path.isfile(self.y.ajan) and os.path.isfile(self.y.beceri))
        self.assertIn("--giris C", metin(self.y.beceri))
        self.assertEqual(sha(self.y.ayar), a0)                                             # asıl settings.json'a yazılmadı
        kod, hata = self.kos.geri_al(self.y)
        self.assertEqual((kod, hata), (0, []))
        self.assertEqual(sha(yerel), s0)
        self.assertFalse(os.path.exists(self.y.ajan) or os.path.exists(os.path.dirname(self.y.beceri)))
        eski = os.listdir(os.path.join(self.kayit, "_ESKI"))
        tasinan = [f for e in eski for f in os.listdir(os.path.join(self.kayit, "_ESKI", e))]
        self.assertIn("settings.local.json", tasinan)                                      # silinmedi, taşındı
        self.assertEqual(self.kos.durum_oku(self.y)["durum"], "geri_alindi")
        self.assertEqual(self.kos.geri_al(self.y), (0, []))                                 # idempotent

    def test_onceki_yerel_yoksa_geri_almada_dosya_kalmaz(self):
        self.assertEqual(self.kos.kur(self.y), 0)
        self.assertEqual(self.kos.kur(self.y), 2)                                           # ikinci kur reddedilir
        self.kos.geri_al(self.y)
        self.assertFalse(os.path.exists(self.y.yerel))

    def test_kur_yarida_coker_ise_geri_alinir(self):
        gercek = self.kos.metin_yaz
        def bozuk(p, m):
            if p.endswith("SKILL.md"): raise OSError("disk dolu (sahte)")
            return gercek(p, m)
        self.kos.metin_yaz = bozuk
        try:
            with self.assertRaises(OSError): self.kos.kur(self.y)
        finally:
            self.kos.metin_yaz = gercek
        self.assertFalse(os.path.exists(self.y.yerel)); self.assertFalse(os.path.exists(self.y.ajan))
        self.assertEqual(self.kos.durum_oku(self.y)["durum"], "geri_alindi")

    def test_bitir_yazici_cokse_de_geri_alir(self):
        self.kos.kur(self.y)
        def bozuk(g): raise RuntimeError("yazıcı çöktü")
        with self.assertRaises(RuntimeError): self.kos.bitir(self.y, yaz=bozuk)
        self.assertFalse(os.path.exists(self.y.yerel)); self.assertFalse(os.path.exists(self.y.ajan))

    def test_suresi_dolunca_kendiliginden_geri_alinir(self):
        self.kos.kur(self.y)
        d = self.kos.durum_oku(self.y); d["son_gecerlilik"] = time.time() - 1; self.kos.json_yaz(self.y.durum, d)
        kod, _ = self.kancala("oturum_basi", {"hook_event_name": "SessionStart", "source": "startup"})
        self.assertEqual(kod, 0)
        self.assertFalse(os.path.exists(self.y.yerel)); self.assertEqual(self.kos.durum_oku(self.y)["durum"], "geri_alindi")
        self.kos.kur(self.y)
        d = self.kos.durum_oku(self.y); d["son_gecerlilik"] = time.time() - 1; self.kos.json_yaz(self.y.durum, d)
        self.kos.main(["durum", "--depo", self.depo, "--kayit", self.kayit, "--python", sys.executable])
        self.assertFalse(os.path.exists(self.y.yerel))

    # --- sonda ------------------------------------------------------------------------------------------------------
    def test_sonda_kurulu_degilken_edilgen(self):
        kod, out = self.kancala("komut", {"tool_name": "Bash", "tool_input": {"command": "x O0A_KOD3_B"}}, giris="B")
        self.assertEqual((kod, out), (0, "")); self.assertEqual(self.olaylar(), [])

    def test_sonda_gizli_metin_yazmaz_ve_isaretli_kodlar(self):
        self.kos.kur(self.y)
        gizli = "AIzaSy-SAHTE-ANAHTAR-12345"
        kod, out = self.kancala("komut", {"hook_event_name": "PreToolUse", "tool_name": "Bash", "session_id": "s1",
                                          "tool_input": {"command": f"echo {gizli} O0A_KOD3_B"}}, giris="B", env={"O0A_SONDA_ENV": "1"})
        self.assertEqual(kod, 3)
        self.kancala("istem", {"hook_event_name": "UserPromptSubmit", "prompt": f"devam {gizli}"})
        ham = metin(self.y.olaylar)
        self.assertNotIn(gizli, ham); self.assertNotIn("echo", ham)
        o = [x for x in self.olaylar() if x["olay"] == "kod3_verdi"][0]
        self.assertEqual(o["isaretler"], ["O0A_KOD3_B"]); self.assertEqual(o["env"]["O0A_SONDA_ENV"], "1")
        kod, out = self.kancala("komut", {"tool_name": "Bash", "tool_input": {"command": "ls"}}, giris="B")
        self.assertEqual((kod, out), (0, ""))

    def test_sonda_yavas_giris_a(self):
        self.kos.kur(self.y)
        eski, stdin = self.sonda.YAVAS_SN, sys.stdin
        self.sonda.YAVAS_SN = 0
        try:
            sys.stdin = io.TextIOWrapper(io.BytesIO(json.dumps({"tool_name": "Bash", "tool_input": {"command": "a O0A_YAVAS_A"}}).encode()))
            self.assertEqual(self.sonda.main(["komut", "--giris", "A", "--kayit", self.kayit]), 0)
        finally:
            self.sonda.YAVAS_SN, sys.stdin = eski, stdin
        self.assertEqual([o["olay"] for o in self.olaylar()], ["yavas_basladi", "yavas_bitti"])

    def test_sonda_engelleme_kipleri(self):
        self.kos.kur(self.y)
        self.kos.adim(self.y, 3)
        g = {"hook_event_name": "SubagentStop", "agent_id": "a1", "agent_type": "o0a-sonda", "agent_transcript_path": ""}
        kod, out = self.kancala("ajan_bitti", g)
        self.assertEqual(json.loads(out)["decision"], "block")
        self.assertEqual(self.kancala("ajan_bitti", g)[1], "")                              # ajan başına bir kez
        self.assertEqual(self.kancala("ajan_bitti", dict(g, agent_type="baska"))[1], "")
        self.kos.adim(self.y, 14)
        st = {"hook_event_name": "Stop", "session_id": "s", "stop_hook_active": False}
        r1, r2, r3 = (self.kancala("stop", st)[1] for _ in range(3))
        self.assertIn("stop-1", json.loads(r1)["reason"]); self.assertIn("stop-2", json.loads(r2)["reason"]); self.assertEqual(r3, "")
        self.assertIn(self.kos.ileri(self.kayit), json.loads(r1)["reason"])                 # {I}/{K} biçimlendi

    def test_sonda_dokum_ozeti_icerik_yazmaz(self):
        self.kos.kur(self.y)
        dokum = os.path.join(self.kok, "dokum.jsonl")
        with open(dokum, "w", encoding="utf-8") as f:
            f.write(json.dumps({"message": {"role": "user", "content": "# YZ FİLM SETİ gizli içerik"}}, ensure_ascii=True) + "\n")
            f.write(json.dumps({"message": {"model": "claude-opus", "usage": {"input_tokens": 100, "output_tokens": 20}}}) + "\n")
        self.kancala("ajan_bitti", {"hook_event_name": "SubagentStop", "agent_id": "a2", "agent_type": "o0a-sonda", "agent_transcript_path": dokum})
        o = self.olaylar()[-1]
        self.assertEqual((o["kullanim_satiri"], o["girdi"], o["cikti"], o["claude_md_gorundu"]), (1, 100, 20, True))
        self.assertNotIn("gizli içerik", metin(self.y.olaylar))

    def test_isaret(self):
        self.kos.kur(self.y)
        r = subprocess.run([sys.executable, SONDA, "isaret", "paralel-1", "--kayit", self.kayit], capture_output=True, timeout=30)
        self.assertEqual(r.returncode, 0)
        self.assertEqual([o["asama"] for o in self.olaylar()], ["bas", "bit"])

    # --- değerlendiriciler ------------------------------------------------------------------------------------------
    def bag(self, **k): return dict({"elle": {}, "otomatik": {}, "tum": [], "sonuclar": {}}, **k)

    def test_d1_paralel(self):
        DV = self.DV
        ol = []
        for i in (1, 2, 3):
            ol += [{"olay": "isaret", "ad": f"paralel-{i}", "asama": "bas", "t": 10 + i * 0.1}, {"olay": "isaret", "ad": f"paralel-{i}", "asama": "bit", "t": 30 + i}]
            ol.append({"olay": "arac_sonrasi", "tool_name": "Agent", "t": 35 + i})
        ol.append({"olay": "komut", "env": {"CLAUDE_CODE_FORK_SUBAGENT": "0"}, "t": 9})
        self.assertEqual(DV.d1(ol, self.bag())["sonuc"], "calisiyor")
        sira = []
        for i in (1, 2, 3):
            sira += [{"olay": "isaret", "ad": f"paralel-{i}", "asama": "bas", "t": i * 100}, {"olay": "isaret", "ad": f"paralel-{i}", "asama": "bit", "t": i * 100 + 20},
                     {"olay": "arac_sonrasi", "tool_name": "Agent", "t": i * 100 + 21}]
        self.assertEqual(DV.d1(sira, self.bag())["sonuc"], "calismiyor")
        self.assertIsNone(DV.d1(sira[:3], self.bag())["sonuc"])

    def test_d2_d16_kendiliginden_uyanma(self):
        DV = self.DV; f = DV.KATALOG[1]["f"]
        temel = [{"olay": "isaret", "ad": "arka-ajan", "asama": "bas", "t": 1}, {"olay": "stop", "t": 2}, {"olay": "isaret", "ad": "arka-ajan", "asama": "bit", "t": 60}]
        self.assertEqual(f(temel + [{"olay": "stop", "t": 70}], self.bag())["sonuc"], "calisiyor")
        self.assertEqual(f(temel + [{"olay": "istem", "t": 200}, {"olay": "stop", "t": 210}], self.bag())["sonuc"], "calismiyor")
        self.assertIsNone(f([temel[0], temel[2], {"olay": "stop", "t": 61}], self.bag())["sonuc"])   # tur bitmeden beklendi
        # ilk yerel oturum bulgusu (#2/#16): bildirim oturuma istem olarak gelir; yalnız GERÇEK kullanıcı istemi "uyanmadı" saydırır
        self.assertEqual(f(temel + [{"olay": "istem", "istem_turu": "sistem", "t": 61}, {"olay": "stop", "t": 70}], self.bag())["sonuc"], "calisiyor")
        self.assertEqual(f(temel + [{"olay": "istem", "istem_turu": "kullanici", "t": 200}], self.bag())["sonuc"], "calismiyor")
        self.assertEqual(f(temel + [{"olay": "bildirim", "t": 61}, {"olay": "istem", "istem_turu": "kullanici", "t": 200}],
                           self.bag())["sonuc"], "calismiyor")                                  # masaüstü bildirimi kullanıcı değildir
        self.assertEqual(DV.KATALOG[15]["f"](
            [dict(o, ad="arka-bash") if o.get("ad") else o for o in temel] + [{"olay": "istem", "istem_turu": "sistem", "t": 90}],
            self.bag())["sonuc"], "calisiyor")

    def test_sonda_istem_turu_bildirim_kullanici_degil(self):
        self.kos.kur(self.y)
        for g, tur in (({"prompt": "<task-notification>\n<task-id>b1</task-id>\n<status>completed</status>\n</task-notification>"}, "sistem"),
                       ({"prompt": "  <system-reminder>arka plan işi bitti</system-reminder>"}, "sistem"),
                       ({"prompt": "devam", "isSynthetic": True}, "sistem"), ({"prompt": ""}, "sistem"),
                       ({"prompt": "devam"}, "kullanici"), ({"prompt": "ejderha yavrusunu saklayan <avcı> kadın"}, "kullanici")):
            self.kancala("istem", dict(g, hook_event_name="UserPromptSubmit", session_id="s"))
            self.assertEqual(self.olaylar()[-1]["istem_turu"], tur, g)
        self.assertNotIn("task-notification", metin(self.y.olaylar)); self.assertNotIn("ejderha", metin(self.y.olaylar))

    def test_sonda_stop_nedeni_utf8_kod_sayfasindan_bagimsiz(self):
        """#14: Windows'ta kanca süreci cp1254/cp1252 (burada en kötüsü: ascii) stdout'la koşsa da Stop nedeni bozulmaz."""
        self.kos.kur(self.y); self.kos.adim(self.y, 14)
        kod, _ = 0, None
        r = subprocess.run([sys.executable, SONDA, "stop", "--giris", "mutlak", "--kayit", self.kayit],
                           input=json.dumps({"hook_event_name": "Stop", "session_id": "s"}).encode("utf-8"), capture_output=True,
                           timeout=60, env=dict(os.environ, PYTHONIOENCODING="ascii", PYTHONUTF8="0"))
        self.assertEqual(r.returncode, 0)
        neden = json.loads(r.stdout.decode("utf-8"))["reason"]
        self.assertIn("kapısı", neden); self.assertIn("çalıştır", neden)
        r = subprocess.run([sys.executable, SONDA, "isaret", "utf8-deneme", "--kayit", self.kayit], capture_output=True, timeout=30,
                           env=dict(os.environ, PYTHONIOENCODING="ascii", PYTHONUTF8="0"))
        self.assertEqual(r.returncode, 0); self.assertIn("işaret", r.stdout.decode("utf-8"))
        self.assertIn("PYTHONUTF8=1", metin(os.path.join(ARACLAR, "olcum0", "kanca_deneme", "o0a_sonda.sh")))
        self.assertEqual(json_(self.kos.SABLON)["env"]["PYTHONUTF8"], "1")

    def test_d7_yazma_olcusu_yazan_ve_okuyan_ayni(self):
        """#7: değerlendirici OTOMATIK.json["7"]["dosya_var"]'ı okur; onu artık degerlendir 7 yazar (alt ajanın yazdığı {YAZMA} dosyası)."""
        self.kos.kur(self.y); self.kos.adim(self.y, 7)
        self.assertIn(self.kos.ileri(self.y.yazma) + "/ajan_yazdi.txt", self.kos.bicimle(self.DV.madde(7)["adimlar"][0], self.y))
        t = time.time() + 1
        ol = {"olay": "erisim", "tool_name": "Write", "agent_id": "a7", "dosya_adi": "ajan_yazdi.txt", "t": t}
        with open(self.y.olaylar, "a", encoding="utf-8") as f: f.write(json.dumps(ol) + "\n")
        self.assertEqual(self.kos.degerlendir(self.y, 7)[1]["sonuc"], "calismiyor")       # dosya yok
        metin_yaz(os.path.join(self.y.yazma, "ajan_yazdi.txt"), "o0a")
        kod, k = self.kos.degerlendir(self.y, 7)
        self.assertEqual((kod, k["sonuc"], k["olcu"]["dosya_var"]), (0, "calisiyor", True))
        self.assertTrue(json_(self.y.otomatik)["7"]["dosya_var"])

    def test_d4_name_isolation_tolerans_d11_ilk_mesaj_devam_gerekmez(self):
        DV = self.DV
        a = {"olay": "ajan", "tool_name": "Agent", "subagent_type": "o0a-sonda", "name_var": False, "isolation_var": False, "t": 1}
        r = DV.d4([a], self.bag()); self.assertEqual(r["sonuc"], "calisiyor"); self.assertFalse(r["olcu"]["name_gorunur"])
        self.assertEqual(DV.d4([dict(a, subagent_type=None)], self.bag())["sonuc"], "calismiyor")
        self.assertNotIn("isolation 'worktree'", " ".join(DV.madde(4)["adimlar"]))
        tum = [{"olay": "komut", "session_id": "s1", "t": 1}]
        ol = [{"olay": "oturum_basi", "kaynak": "resume", "session_id": "s1", "t": 10},
              {"olay": "istem", "prompt_devam": False, "istem_turu": "kullanici", "t": 20}]
        r = DV.d11(ol, self.bag(tum=tum + ol)); self.assertEqual(r["sonuc"], "calisiyor"); self.assertFalse(r["olcu"]["ilk_mesaj_devam"])
        yeni = [{"olay": "oturum_basi", "kaynak": "startup", "session_id": "s2", "t": 10}]
        self.assertEqual(DV.d11(yeni, self.bag(tum=tum + yeni))["sonuc"], "calismiyor")

    def test_d12_effort_degersiz_anahtar(self):
        DV = self.DV
        s = {"3": {"olcu": {"maxturns_subagentstop": True}}, "7": {"olcu": {"izin_sorusu": False}}, "9": {"olcu": {"beceri_kancasi_kostu": True}}}
        tum = [{"olay": "ajan_basi", "agent_type": "o0a-sonda", "effort_anahtari": True, "effort": None},
               {"olay": "ajan_bitti", "agent_type": "o0a-sonda", "dokum_var": True, "claude_md_gorundu": False}]
        elle = {"disable_model_invocation": "evet", "allowed_tools": "evet", "disallowed_tools": "evet", "effort": "  "}
        r = DV.d12([], self.bag(tum=tum, elle=elle, sonuclar=s))
        self.assertEqual(r["sonuc"], "calisiyor", r); self.assertEqual(r["olcu"]["effort"], "degersiz"); self.assertEqual(r["olcu"]["degersiz"], ["effort"])
        tum[0]["effort"] = "high"
        self.assertIs(DV.d12([], self.bag(tum=tum, elle=elle, sonuclar=s))["olcu"]["effort"], True)
        self.assertIsNone(DV.d12([], self.bag(tum=tum[1:], elle=elle, sonuclar=s))["sonuc"])          # hiç bilgi yok: elle sorulur
        self.kos.kur(self.y)
        for e in (None, "", {"level": ""}, {"level": "high"}):
            self.kancala("ajan_basi", {"hook_event_name": "SubagentStart", "agent_id": "a", "agent_type": "o0a-sonda", "effort": e})
            o = self.olaylar()[-1]; self.assertTrue(o["effort_anahtari"])
            self.assertEqual(o["effort"], "high" if e == {"level": "high"} else None, e)

    def test_d5_d18_zaman_asimi_ve_kod(self):
        DV = self.DV
        self.assertEqual(DV.d5([{"olay": "yavas_basladi", "giris": "A", "t": 1}], self.bag())["sonuc"], "calisiyor")
        gecti = [{"olay": "yavas_basladi", "giris": "A", "t": 1}, {"olay": "isaret", "ad": "yavas-a", "asama": "bit", "t": 3}]
        r = DV.d5(gecti, self.bag()); self.assertEqual(r["sonuc"], "calismiyor"); self.assertFalse(r["olcu"]["onfailure_engelledi"])
        b = [{"olay": "kod3_verdi", "t": 1}, {"olay": "yavas_basladi", "giris": "B", "t": 2}, {"olay": "isaret", "ad": "kod3-b", "asama": "bit", "t": 3}]
        r = DV.d18(b, self.bag()); self.assertEqual(r["sonuc"], "calismiyor")
        self.assertEqual((r["olcu"]["beklenmeyen_kod"], r["olcu"]["zaman_asimi"]), ("geciyor", "engelleniyor"))

    def test_d9_cift_kosu_ve_d14(self):
        DV = self.DV
        ol = [{"olay": "komut", "giris": "C", "isaretler": ["O0A_CIFT"], "tool_use_id": "t1"},
              {"olay": "komut", "giris": "C", "isaretler": ["O0A_CIFT"], "tool_use_id": "t1"},
              {"olay": "komut", "giris": "D", "isaretler": ["O0A_CIFT"], "tool_use_id": "t1"}]
        r = DV.d9(ol, self.bag()); self.assertEqual(r["sonuc"], "calisiyor"); self.assertTrue(r["olcu"]["cift_kosu"])
        st = [{"olay": "stop", "engelledi": True, "t": 1}, {"olay": "isaret", "ad": "stop-1", "asama": "bit", "t": 2},
              {"olay": "stop", "engelledi": True, "t": 3}, {"olay": "isaret", "ad": "stop-2", "asama": "bit", "t": 4}]
        self.assertEqual(DV.d14(st, self.bag())["sonuc"], "calisiyor")
        self.assertEqual(DV.d14(st[:1] + st[2:3], self.bag())["sonuc"], "calismiyor")

    def test_katalog_tam_ve_yedekli(self):
        self.assertEqual(self.DV.NOLAR, list(range(1, 21)))
        self.assertEqual(sorted(self.DV.ONERILEN_SIRA), list(range(1, 21)))
        self.assertEqual(self.DV.ONERILEN_SIRA[-1], 11)
        for m in self.DV.KATALOG:
            self.assertTrue(m["yedek"] and m["adimlar"] and callable(m["f"]), m["no"])
            self.assertIsNone(m["f"]([], self.bag())["sonuc"], m["no"])                    # kayıt yokken karar uydurulmaz

    # --- otomatik ve bitiş ------------------------------------------------------------------------------------------
    def test_kor_rol_sahte_claude(self):
        gorulen = {}
        def sahte(cmd, cwd=None, env=None, **k):
            if cmd[1:] == ["--help"]: return subprocess.CompletedProcess(cmd, 0, "  --restricted\n  --tools <tools>\n  --no-session-persistence\n", "")
            gorulen["cmd"], gorulen["env"] = cmd, env
            kod = metin(os.path.join(cwd, "GIRDI", "a.txt")).strip()
            os.makedirs(os.path.join(cwd, "CIKTI"), exist_ok=True)
            with open(os.path.join(cwd, "CIKTI", "b.txt"), "w", encoding="utf-8") as f: f.write(kod)
            return subprocess.CompletedProcess(cmd, 0, json.dumps({"result": '{"dis_kod": null, "claude_md_kod": null}', "is_error": False}), "")
        os.environ["ANTHROPIC_API_KEY"] = "sahte-deger"
        try: o = self.kos.kor_rol(calistir=sahte, kok=os.path.join(self.kok, "kor"))
        finally: os.environ.pop("ANTHROPIC_API_KEY", None)
        self.assertNotIn("ANTHROPIC_API_KEY", gorulen["env"])
        self.assertIn("--restricted", gorulen["cmd"]); self.assertIn("Read,Write", gorulen["cmd"])
        self.assertTrue(o["abonelik"] and o["cikti_yazildi"]); self.assertFalse(o["dis_okundu"] or o["claude_md_yuklendi"] or o["bash_calisti"])
        self.assertNotIn("sahte-deger", json.dumps(o))
        self.assertEqual(self.DV.d19([], self.bag(otomatik={"19": o}))["sonuc"], "calisiyor")
        sizdi = dict(o, claude_md_yuklendi=True)
        self.assertEqual(self.DV.d19([], self.bag(otomatik={"19": sizdi}))["sonuc"], "calismiyor")

    def test_kor_rol_windows_claude_cmd_istem_cmd_exeden_gecmez(self):
        """#19 (ilk yerel oturum): which('claude') → npm claude.CMD; istemdeki <…> cmd.exe'de yönlendirme oldu. Artık: claude.exe
        varsa o çağrılır; yalnız .CMD varsa bile istem argv'de değil stdin'de."""
        from unittest import mock
        gorulen = []
        def sahte(cmd, input=None, cwd=None, **k):
            if cmd[1:] == ["--help"]: return subprocess.CompletedProcess(cmd, 0, "  --restricted\n", "")
            gorulen.append((cmd, input))
            return subprocess.CompletedProcess(cmd, 0, json.dumps({"result": "{}", "is_error": False}), "")
        cmd_yolu = "C:\\Users\\Soysal\\AppData\\Roaming\\npm\\claude.CMD"
        exe = "C:\\Users\\Soysal\\AppData\\Roaming\\npm\\node_modules\\@anthropic-ai\\claude-code\\bin\\claude.exe"
        for var, beklenen in ((set(), cmd_yolu), ({exe}, exe)):
            gercek_isfile = os.path.isfile
            with mock.patch.object(ortak.os, "name", "nt"), \
                    mock.patch("shutil.which", lambda ad, *a, **k: cmd_yolu if ad == "claude" else None), \
                    mock.patch.object(ortak.os.path, "isfile", lambda p: p in var or (not p.startswith("C:\\") and gercek_isfile(p))):
                self.assertEqual(ortak.claude_yolu(), beklenen)
                o = self.kos.kor_rol(calistir=sahte, kok=tempfile.mkdtemp(dir=self.kok))
            cmd, girdi = gorulen[-1]
            self.assertEqual(cmd[0], beklenen); self.assertEqual(girdi, self.kos.KOR_ISTEM)
            self.assertFalse([x for x in cmd if self.kos.KOR_ISTEM in x or "<" in x or ">" in x], cmd)
            self.assertTrue(o["istem_stdin"]); self.assertEqual(o["kabuk_sarmalayici"], beklenen.endswith(".CMD"))

    def test_yeniden_duzeltilen_maddeler_acilir_O0a_degismez(self):
        """Ö0-a bulguları düzeltildi: çalışmıyor olan #2/#7/#16/#19 yeniden açılır, #4 eldeki kayıttan çalışıyor olur; öteki sonuçlar
        korunur; kullanıcının O0a.json'u değişmez (bitir yenisini yazar, eskisi _ESKI'ye kopyalanır)."""
        import ortak_o0
        davr = [{"no": n, "baslik": "x", "sonuc": "calismiyor", "yedek": "y", "kaynak": "otomatik"} for n in range(1, 21)]
        davr[0]["sonuc"] = "calisiyor"; davr[10]["sonuc"] = "calisiyor"
        ortak_o0.yaz("a", {"durum": "bitti", "davranislar": davr, "kararlar": {}}); once = sha(ortak_o0.yol("a"))
        os.makedirs(self.kayit, exist_ok=True)
        with open(self.y.olaylar, "a", encoding="utf-8") as f:
            f.write(json.dumps({"olay": "ajan", "tool_name": "Agent", "subagent_type": "o0a-sonda", "name_var": False, "isolation_var": False, "t": 5}) + "\n")
        kod, acilan, kapanan = self.kos.yeniden(self.y)
        self.assertEqual(kod, 0); self.assertEqual(kapanan, [4]); self.assertEqual(acilan, [2, 7, 12, 16, 19])
        s = self.kos.sonuclar(self.y)
        self.assertEqual(s["1"]["sonuc"], "calisiyor"); self.assertEqual(s["11"]["sonuc"], "calisiyor")      # korunur
        self.assertIsNone(s["19"]["sonuc"]); self.assertEqual(s["19"]["onceki"]["sonuc"], "calismiyor")
        self.assertEqual(sha(ortak_o0.yol("a")), once)
        self.kos.kur(self.y); self.assertEqual(self.kos.bitir(self.y), 0)
        self.assertTrue(os.listdir(os.path.join(os.path.dirname(ortak_o0.yol("a")), "_ESKI")))           # eski O0a.json kopyalandı
        self.assertEqual(ortak_o0.oku("a")["davranislar"][3]["sonuc"], "calisiyor")

    def test_kanca_suresi_sahte(self):
        o = self.kos.kanca_suresi(self.y, calistir=lambda *a, **k: subprocess.CompletedProcess(a, 0, b"", b""))
        self.assertIsNotNone(o["kanca_py_medyan_sn"])

    def test_bitir_O0a_her_madde_kapanir_ve_kararlar(self):
        import ortak_o0
        self.kos.kur(self.y)
        self.kos.adim(self.y, 6)
        self.kancala("komut", {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "ls"}}, giris="A",
                     env={"O0A_SONDA_ENV": "1", "CLAUDE_CODE_FORK_SUBAGENT": "0"})
        self.assertEqual(self.kos.degerlendir(self.y, 6)[0], 0)
        self.kos.kaydet(self.y, 20, "calismiyor", not_="bulutta kanca görülmedi")
        self.assertEqual(self.kos.bitir(self.y), 0)
        o = ortak_o0.oku("a")
        self.assertEqual(len(o["davranislar"]), 20)
        for d in o["davranislar"]:
            self.assertIn(d["sonuc"], ("calisiyor", "calismiyor"))
            if d["sonuc"] == "calismiyor": self.assertTrue(d["yedek"], d["no"])
        self.assertEqual(o["davranislar"][5]["sonuc"], "calisiyor")
        self.assertEqual(o["davranislar"][19]["kaynak"], "elle")
        self.assertTrue(o["davranislar"][0].get("olculmedi"))
        k = o["kararlar"]
        self.assertEqual(k["kanca_nabzi"], "calisiyor"); self.assertTrue(k["pr3_birlestirilebilir"])
        self.assertEqual((k["kor_rol_yolu"], k["kor_rapor_bayragi"], k["m12"]), ("talimat_yalitimi", "habersizlik: dogrulanmadi", "olculemedi"))
        self.assertEqual(ortak_o0.ozet_oku()["O0a"]["kor_rol_yolu"], "talimat_yalitimi")
        self.assertEqual(ortak_o0.durum("a"), "bitti")
        self.assertFalse(os.path.exists(self.y.yerel))
        # kanca.py oturum başı O0a.json'u BILGI/OLCUM0'da görür
        import importlib.util
        sp = importlib.util.spec_from_file_location("kanca_o0a", os.path.join(DEPO, ".claude", "hooks", "kanca.py"))
        m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        self.assertTrue(m.o0a_var())

    def test_kararlar_kor_yolu(self):
        s = {"19": {"sonuc": "calisiyor"}, "6": {"sonuc": "calisiyor"}}
        tum = [{"olay": "komut"}]
        self.assertEqual(self.kos.kararlar(s, tum)["kor_rol_yolu"], "claude_p")
        s.update({"5": {"sonuc": "calisiyor"}}); tum.append({"olay": "erisim", "agent_id": "x"})
        self.assertEqual(self.kos.kararlar(s, tum)["kor_rol_yolu"], "agent")
        self.assertEqual(self.kos.kararlar({}, [])["kanca_nabzi"], "calismiyor")

    def test_paket_015M(self):
        self.kos.kur(self.y)
        p = self.kos.paket_hazirla(self.y, tohum=1)
        self.assertEqual(len(p["kodlar"]), 24); self.assertGreater(p["token_tahmin"], 150000)
        for f in os.listdir(self.y.paket): self.assertLess(os.path.getsize(os.path.join(self.y.paket, f)), 200 * 1024)
        self.kos.kaydet(self.y, 15, alanlar={"kodlar": ",".join(p["kodlar"])})
        self.assertEqual(self.kos.sonuclar(self.y)["15"]["sonuc"], "calisiyor")

    def test_sablon_yalniz_ekler(self):
        s = json_(self.kos.SABLON)
        self.assertNotIn("deny", s["permissions"])
        for olay, gl in s["hooks"].items():
            for g in gl:
                for h in g["hooks"]: self.assertIn("sonda", h["command"].lower(), olay)
        m = metin(self.kos.AJAN_SABLON)
        for alan in ("effort:", "omitClaudeMd:", "permissionMode:", "maxTurns:", "o0a_bilinmeyen_alan:"): self.assertIn(alan, m)


# ======================================================================================================================
# Ö0-c
# ======================================================================================================================
SR = 48000


def ton(hz, sn=1.5, gurultu=0.0, tohum=0):
    t = np.arange(int(SR * sn)) / SR; r = np.random.RandomState(tohum)
    x = 0.3 * np.sin(2 * np.pi * hz * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * t)) + 0.15 * np.sin(2 * np.pi * 2 * hz * t)
    return (x + gurultu * r.randn(len(t))).astype(np.float32)


class SesDeneme(_VeriKoku):
    def setUp(self):
        super().setUp()
        import ses_deneme, ortak_o0
        from olcum import ses as O
        self.S, self.o0, self.O = ses_deneme, ortak_o0, O
        self.cikti = io.StringIO(); self._out = sys.stdout; sys.stdout = self.cikti

    def tearDown(self):
        sys.stdout = self._out
        super().tearDown()

    def klipler(self, fisilti=4, bagirma=4, normal=2):
        d = os.path.join(self.kok, "klipler"); os.makedirs(d, exist_ok=True)
        n = 0
        for teslim, say in (("whisper", fisilti), ("shouting", bagirma), ("normal", normal)):
            for i in range(say):
                n += 1; p = os.path.join(d, f"k{n:02d}.wav"); self.O.yaz(p, ton(180 + 5 * i, tohum=n))
                ortak.atomik_yaz(os.path.splitext(p)[0] + ".json", {"metin": "we leave at dawn", "teslim": teslim})
        ref = os.path.join(self.kok, "hedef.wav"); self.O.yaz(ref, ton(210, sn=3))
        return d, ref

    def sahte_kos(self, iyi=("openvoice",)):
        O = self.O
        def kos(py, motor, istek, env=None, **k):
            x, _ = O.oku(istek["giris"])
            if motor in iyi: y = ton(210, sn=len(x) / SR)
            else: y = (0.3 * np.random.RandomState(3).randn(len(x))).astype(np.float32)
            O.yaz(istek["cikti"], y); return {}, 0.5, 0
        return kos

    def test_plan_gecici_ortamlar_yollara_yazmaz(self):
        y0 = sha(self.yollar)
        p = self.S.plan()
        adlar = [b["ad"] for b in p["bilesenler"]]
        for a in ("openvoice", "chatterbox", "mos", "musetalk", "acestep", "buyutme"): self.assertIn(a, adlar)
        kok = self.S.ortam_kok()
        for b in p["bilesenler"]:
            if b.get("kur"):
                self.assertTrue(b["venv"].startswith(kok), b["ad"])
                for a in b.get("adimlar") or []: self.assertNotIn("yollar", a)
        self.assertFalse([b for b in p["bilesenler"] if b["ad"] == "mos"][0]["kur"])        # lisans doğrulanmadı
        self.assertEqual(sha(self.yollar), y0)
        self.assertTrue(os.path.isfile(os.path.join(self.o0.kok(), "O0c_plan.json")))

    def test_kur_sahte_calistir(self):
        gorulen = []
        kod, s = self.S.kur("openvoice", calistir=lambda c, **k: (gorulen.append(c), subprocess.CompletedProcess(c, 0, "", ""))[1], zorla=True)
        self.assertEqual(kod, 0); self.assertTrue(s["openvoice"]["kuruldu"]); self.assertTrue(gorulen)
        self.assertIn("openvoice", self.S.ortamlar())
        kod, s = self.S.kur("chatterbox", calistir=lambda c, **k: subprocess.CompletedProcess(c, 1, "", "pip hata"), zorla=True)
        self.assertFalse(s["chatterbox"]["kuruldu"]); self.assertNotIn("chatterbox", self.S.ortamlar())

    def test_donustur_dogallik_olculemedi_bayrakla_secer(self):
        d, ref = self.klipler()
        self.S.ortam_kaydet(openvoice=sys.executable, chatterbox=sys.executable)
        kod, v = self.S.donustur(d, ref, kos=self.sahte_kos(), asr=None, ikili=None)
        self.assertEqual(kod, 0)
        t = v["tablo"]
        self.assertTrue(t["openvoice"]["s1_11"]); self.assertFalse(t["chatterbox"]["s1_11"])
        self.assertTrue(t["openvoice"]["dogallik"]["olculemedi"])
        self.assertTrue(v["kiyas_seti"]["yeterli"])
        k = self.S.donustur_karari(v)
        self.assertEqual((k["ses_donustur_sira"], k["ana_yol"]), (["openvoice"], "veo_donustur"))
        self.assertIn("dogallik_olculemedi", k["bayraklar"]); self.assertTrue(k["dogallik"]["olculemedi"])
        orn = os.listdir(self.S.ornek_klasoru())
        self.assertEqual(len([f for f in orn if f.startswith("openvoice_")]), 8)            # fısıltı + bağırma örnekleri

    def test_donustur_dinleyici_metalik_bulursa_B_plani(self):
        d, ref = self.klipler()
        self.S.ortam_kaydet(openvoice=sys.executable)
        sorulan = []
        def ikili(a, b):
            sorulan.append((a, b))
            don = "A" if "cikti" in a.replace("\\", "/") else "B"
            return {"metalik": don, "dogal": "B" if don == "A" else "A"}
        kod, v = self.S.donustur(d, ref, motorlar=["openvoice"], kos=self.sahte_kos(), asr=None, ikili=ikili)
        dg = v["tablo"]["openvoice"]["dogallik"]
        self.assertEqual((dg["yontem"], dg["n"], dg["metalik_oran"], dg["gecer"]), ("dinleyici_kor_ikili", 8, 1.0, False))
        self.assertEqual(len({a.endswith(".wav") and "cikti" in a for a, b in sorulan}), 2)  # sıra gizli: iki yönde de
        k = self.S.donustur_karari(v)
        self.assertEqual((k["ses_donustur_sira"], k["ana_yol"]), ([], "B"))
        self.assertNotIn("dogallik_olculemedi", k["bayraklar"])

    def test_donustur_set_eksik_bayrak(self):
        d, ref = self.klipler(fisilti=2, bagirma=4)
        self.S.ortam_kaydet(openvoice=sys.executable)
        _, v = self.S.donustur(d, ref, motorlar=["openvoice"], kos=self.sahte_kos(), asr=None, ikili=None)
        self.assertFalse(v["kiyas_seti"]["yeterli"])
        self.assertIn("kiyas_seti_eksik", self.S.donustur_karari(v)["bayraklar"])

    def test_ikili_kor_sira_geri_cevrilir(self):
        def ikili(a, b): return {"metalik": "hicbiri", "dogal": "A" if "don" in a else "B"}
        r = self.S.ikili_degerlendir(ikili, [("org%d" % i, "don%d" % i, "m:%d" % i) for i in range(6)])
        self.assertEqual((r["n"], r["metalik_oran"], r["dogal_kazanma"]), (6, 0.0, 1.0))

    def test_acestep_buyutme_musetalk_ve_karar(self):
        import ses_kiyas, buyut
        from saglayicilar.acestep import AceStep
        self.S.ortam_kaydet(acestep=sys.executable, musetalk=sys.executable, musetalk_kok=self.kok)
        yavas = lambda py, motor, istek, env=None, **k: ({"sure_sn": 900.0}, 900.0, 0)
        def nvidia(c, **k): return subprocess.CompletedProcess(c, 0, "NVIDIA GeForce RTX 3050 Ti Laptop GPU, 4096\n" if c[0] == "nvidia-smi" else "8.0\n", "")
        def yaz_ve_don(py, motor, istek, env=None, **k):
            metin_yaz(istek["cikti"]); return {"sure_sn": 900.0}, 900.0, 0
        _, a = self.S.acestep(30, kos=yaz_ve_don, calistir=nvidia)
        self.assertEqual((a["calisti"], a["kabul"], a["zincirden_dus"], a["gpu"]["bellek_gb"]), (True, False, True, 4.0))
        _, m = self.S.musetalk("plan.mp4", "replik.wav", kos=lambda py, motor, istek, env=None, **k: ({"sure_sn": 300.0}, 300.0, 0), calistir=nvidia)
        self.assertTrue(m["calisti"]); self.assertEqual(m["oran"], 37.5)
        exe = os.path.join(self.kok, "realesrgan.exe"); metin_yaz(exe)
        _, b = self.S.buyutme("klip.mp4", exe=exe, calistir=nvidia)
        self.assertEqual(b["yol"], "yz_buyutucu"); self.assertIn("sn_basina_sn", b)
        d, ref = self.klipler(); self.S.ortam_kaydet(openvoice=sys.executable)
        self.S.donustur(d, ref, motorlar=["openvoice"], kos=self.sahte_kos(), asr=None, ikili=None)
        v = self.S.karar()
        self.assertEqual(v["durum"], "bitti"); self.assertEqual(v["ses_donustur_sira"], ["openvoice"])
        self.assertIs(v["acestep_zincirde"], False); self.assertEqual(v["tts_dudak"], "acik")
        self.assertTrue(v["dogallik"]["olculemedi"])
        oz = self.o0.ozet_oku()["O0c"]
        self.assertEqual((oz["ana_yol"], oz["dogallik_olculemedi"], oz["buyutme_yolu"]), ("veo_donustur", True, "yz_buyutucu"))
        self.assertTrue([x for x in self.o0.ozet_oku()["denemeler"] if x["olcum"] == "Ö0-c" and x["deneme"] == "dogallik"])
        self.assertEqual(ses_kiyas.kur2_plani()["motor"], "openvoice")                     # KUR2 = Ö0-c kazananı
        self.assertEqual(buyut.hiz_orani(), b["sn_basina_sn"])
        ok, neden = AceStep().hazir(); self.assertFalse(ok); self.assertIn("Ö0-c", neden)   # D-25: zincirden düştü

    def test_buyutme_yavassa_1080p_gren_ve_olculmeyen_parca(self):
        exe = os.path.join(self.kok, "realesrgan.exe"); metin_yaz(exe)
        def kisa(c, **k):
            time.sleep(0.1); return subprocess.CompletedProcess(c, 0, "0.01\n", "")
        _, b = self.S.buyutme("klip.mp4", exe=exe, calistir=kisa)
        self.assertEqual(b["yol"], "1080p_gren")
        v = self.S.karar()
        self.assertEqual(v["durum"], "suruyor"); self.assertEqual(v["ana_yol"], "B")
        self.assertEqual(sorted(v["olculmeyen"]), ["acestep", "donustur", "musetalk"])
        self.assertIsNone(v["acestep_zincirde"]); self.assertEqual(v["tts_dudak"], "kapali")
        self.assertIn("b_plani_musetalk_calismiyor", v["bayraklar"])

    def test_ana_komut_satiri(self):
        self.assertEqual(self.S.main(["--plan"]), 0)
        self.assertEqual(self.S.main(["--donustur"]), 4)
        self.assertEqual(self.S.main(["durum"]), 0)
        self.assertEqual(self.S.durum_metni()["sonraki"], "--donustur")
        self.assertEqual(self.S.main(["--kur", "openvoice"]), 0 if os.name == "nt" else 4)


# ======================================================================================================================
# Ö0-g
# ======================================================================================================================
class KanalO0g(_VeriKoku):
    def setUp(self):
        super().setUp()
        import kanal_teshis, ortak_o0
        self.K, self.o0 = kanal_teshis, ortak_o0
        self.cikti = io.StringIO(); self._out = sys.stdout; sys.stdout = self.cikti

    def tearDown(self):
        sys.stdout = self._out
        super().tearDown()

    def test_veri_yoksa_olculemedi_engellemez(self):
        self.assertEqual(self.K.main([]), 0)
        g = self.o0.oku("g")
        self.assertEqual((g["olculemedi"], g["engeller"], g["genel_teshis"], g["durum"]), (True, False, "ölçülemedi", "bitti"))
        self.assertTrue(os.path.isfile(os.path.join(self.veri, "BILGI", "KANAL_TESHIS.md")))
        self.assertEqual(self.o0.ozet_oku()["O0g"]["olculemedi"], True)
        self.assertEqual(self.K.main(["durum"]), 0)

    def test_csv_varsa_teshis(self):
        d = os.path.join(self.veri, "GELENLER", "KANAL"); os.makedirs(d)
        with open(os.path.join(d, "studio.csv"), "w", encoding="utf-8") as f:
            f.write("Video title,Impressions,Impressions click-through rate (%),Views,Average percentage viewed (%)\n"
                    "B1,500,2.1,40,22\nB2,3000,5.5,300,41\n")
        self.assertEqual(self.K.main([]), 0)
        g = self.o0.oku("g")
        self.assertFalse(g["olculemedi"]); self.assertEqual(g["video_sayisi"], 2); self.assertNotEqual(g["genel_teshis"], "ölçülemedi")
        self.assertTrue([x for x in self.o0.ozet_oku()["denemeler"] if x["olcum"] == "Ö0-g"])


class ClaudeYolu(unittest.TestCase):
    """ortak.claude_yolu / claude_komutu: Windows'ta gerçek claude.exe; kullanıcı metni hiçbir zaman cmd.exe argv'sine girmez."""
    NPM = "C:\\Users\\Soysal\\AppData\\Roaming\\npm"

    def yol(self, which, var=(), icerik=""):
        return ortak.claude_yolu(which=lambda ad: which.get(ad), nt=True, dosya_var=lambda p: p in set(var), oku=lambda p: icerik)

    def test_cmd_yanindaki_npm_exe(self):
        exe = self.NPM + "\\node_modules\\@anthropic-ai\\claude-code\\bin\\claude.exe"
        self.assertEqual(self.yol({"claude": self.NPM + "\\claude.CMD"}, [exe]), exe)

    def test_cmd_icindeki_hedef_node_exe_degil(self):
        cmd = self.NPM + "\\claude.cmd"
        icerik = '@IF EXIST "%~dp0\\node.exe" (\r\n  "%~dp0\\node.exe" %*\r\n)\r\n"%dp0%\\..\\claude-yerel\\claude.exe"   %*\r\n'
        hedef = self.NPM + "\\..\\claude-yerel\\claude.exe"
        self.assertEqual(self.yol({"claude": cmd}, [hedef, self.NPM + "\\node.exe"], icerik), hedef)

    def test_path_exe_ve_yerel_kurucu(self):
        self.assertEqual(self.yol({"claude": "C:\\x\\claude.EXE"}), "C:\\x\\claude.EXE")
        self.assertEqual(self.yol({"claude": self.NPM + "\\claude.cmd", "claude.exe": "C:\\y\\claude.exe"}, ["C:\\y\\claude.exe"]), "C:\\y\\claude.exe")
        self.assertIsNone(self.yol({}))

    def test_yalniz_cmd_varsa_istem_stdinden(self):
        cmd = self.NPM + "\\claude.cmd"
        y = self.yol({"claude": cmd})
        self.assertEqual(y, cmd); self.assertTrue(ortak.claude_kabuktan_mi(y))
        istem = "konu: <avcı> & ejderha | ^%PATH%"
        argv, girdi = ortak.claude_komutu(["-p", "--output-format", "json"], istem, yol=y)
        self.assertEqual(argv, [cmd, "-p", "--output-format", "json"]); self.assertEqual(girdi, istem)
        from unittest import mock
        with mock.patch("shutil.which", lambda *a, **k: None), mock.patch.object(ortak.os.path, "isfile", lambda p: False):
            self.assertEqual(ortak.claude_komutu(["-p"], "x"), (None, None))

    def test_windows_disi_which(self):
        self.assertEqual(ortak.claude_yolu(which=lambda ad: "/usr/bin/claude" if ad == "claude" else None, nt=False), "/usr/bin/claude")
        self.assertFalse(ortak.claude_kabuktan_mi("/usr/bin/claude"))

    def test_claude_cagiran_kod_ortak_cozucuyu_kullanir(self):
        """Depoda claude'u alt süreçle çağıran ya da arayan her araç ortak.claude_yolu'ndan geçer (yalın "claude" argv'si yok)."""
        import re
        kotu = []
        for kok, ds, fs in os.walk(ARACLAR):
            ds[:] = [d for d in ds if d not in ("testler", "__pycache__")]
            for f in fs:
                if not f.endswith(".py"): continue
                m = metin(os.path.join(kok, f))
                for i, sat in enumerate(m.splitlines(), 1):
                    if re.search(r"""\[\s*["']claude["']\s*,|which\(\s*["']claude["']\s*\)""", sat) and "ortak.py" not in f:
                        kotu.append(f"{f}:{i}")
        self.assertEqual(kotu, [])


if __name__ == "__main__":
    unittest.main()
