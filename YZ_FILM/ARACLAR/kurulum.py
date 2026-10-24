"""YZ_FILM KURULUM v2 (KUR1) — bu bilgisayarda seti hazırlar; SORU SORMAZ (TASARIM §6.9, §8.2 adım 1, §9 adım 4, D-37).
KURULUM.bat (depo kökü) çalıştırır. Tekrar çalıştırmak güvenlidir (kurulu olanı atlar, kullanıcının izinlerine dokunmaz).

  python kurulum.py [--kuru] [--deneme] [--veri <klasör>] [--depo <klasör>]
                                                        KUR1 kurulumu. Her çalıştırmada ÖNCE --yollar, SONRA --veri-emniyet.
                                                        --kuru: ağ, pip, winget, model ve dosya indirmesi YOK (bulut/CI denemesi);
                                                        yerel işler (ayar dosyaları, .bat'lar, denetimler, kart) yapılır.
                                                        --deneme: lisansı "bilinmiyor" bileşenler de kurulur (yalnız deneme kipi).
  python kurulum.py --yollar [--veri <klasör>]          yalnız YOLLAR.json (varsayılan veri: Masaüstü\\YZ_FILM)
  python kurulum.py --veri-emniyet [--veri <klasör>]    yalnız veri kökü emniyeti (veri_emniyet.py; eski Memmet ve .bat'lar emekliye)
  python kurulum.py --ses-ortamlari | --kur3            KUR2 / KUR3 (P1; henüz yok → 4)

Adımlar: yollar + veri emniyeti → Python (ana ortam 3.10) → güvenli FILM_AYAR.json (yalnız izin/tercih/para tavanı; var olan izinler
korunur) → git ve .git (ZIP ise GUNCELLE kapalı) → claude --version (≥ 2.1.302 kaydı) → ffmpeg, Chrome, CapCut → anahtar dosyaları (depodakiler
BOŞ olmalı; veri kökündekilerin yalnız varlığı, boş olup olmadığı (boyut) ve tarihi; İÇERİK AÇILMAZ, yazdırılmaz) → disk ve önbellek →
KUR1 kütüphaneleri (CPU torch + requirements.txt) → modeller (bir kez; sonra HF_HUB_OFFLINE=1) → FluidSynth + SF2 + müzik çekirdek seti
(sabit adres + SHA-1; lisansı kayıtlı olmayan kurulmaz, D-25, D-36) → settings.local.json + .claude/bin/python_yolu.txt → .bat'lar
(bat_yenile.py) → "çalışıyor / çalışmıyor" kartı ve kullanıcı sözleşmesi kartı (sayılar olcek.py'den, §8.1).
Rapor: <veri>/AYARLAR/KURULUM_RAPORU.json. Ağ yoksa (ya da --kuru) ağ adımları açık bir mesajla ATLANIR.
Çıkış kodları: 0 her şey çalışıyor (atlananlar olabilir) · 1 en az bir madde çalışmıyor · 3 veri emniyeti kalan giriş noktası ·
4 ortam (Python yok/eski, P1 kademe).
"""
import os, sys, subprocess, shutil, glob, importlib.util, json, time, re, socket, hashlib, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
try: import olcek                       # kart sayıları (§8.1); içe aktarırken stdout'u ayarlar, bu yüzden en başta
except Exception: olcek = None

KD = os.path.join(HERE, "kurulum_dosyalari")
SURUM = "kurulum 2.0"
CLAUDE_EN_AZ = (2, 1, 302)             # TASARIM D-11 (doğrulanacak)
ANA_PYTHON = (3, 10)
# Depodaki YZ_FILM/AYARLAR'da bulunabilecek anahtar dosyaları: depoda BOŞ kalmalı (§5.6). Veri kökündekiler yalnız denetlenir.
ANAHTAR_DESENI = re.compile(r"anahtar|_bot\.txt$|token|oauth|secret|api_?key|\.key$", re.I)
VERI_ANAHTARLARI = {"ai84_anahtar.txt": "AI84.pro (ElevenLabs) anahtarı — seslendirme",
                    "gemini_anahtar.txt": "ücretsiz Gemini API anahtarı — filmi yayından önce dinleyen 'kulak' (§8.2 adım 3b)",
                    "telegram_bot.txt": "Telegram bot anahtarı — telefon bildirimi (isteğe bağlı; yalnız tarihi denetlenir)"}
# KUR1 modelleri (D-37). lisans: LISANSLAR.json anahtarı. YuNet/SFace (OpenCV zoo ONNX) sabit adres + SHA-1 seçilince INDIRMELER'e girer.
MODELLER = [("clip", "CLIP (görsel eşleştirme)", "transformers", "openai/clip-vit-base-patch16"),
            ("dinov2-small", "DINOv2-small (kimlik/benzerlik)", "transformers", "facebook/dinov2-small"),
            ("owlv2-base", "OWLv2-base (nesne bulma)", "transformers", "google/owlv2-base-patch16-ensemble"),
            ("faster-whisper", "Whisper small.en (konuşma)", "whisper", "small.en"),
            ("demucs", "Demucs htdemucs (ses ayırma)", "demucs", "htdemucs")]
# Sabit adres + SHA-1 indirmeleri (D-25, D-37). Dosya listesi geliştirme oturumunda lisansı LISANSLAR.json'a yazılarak doldurulur;
# boş liste = "henüz seçilmedi" (müzik zinciri kutuphane basamağı boş → ipucu müziksiz + BAYRAK, hat durmaz).
INDIRMELER = [
    {"ad": "fluidsynth", "baslik": "FluidSynth (midi_ornek, yalnız animatik)", "lisans": "fluidsynth", "hedef": ["onbellek", "fluidsynth"],
     "ikili": "fluidsynth", "dosyalar": []},
    {"ad": "sf2_ses_bankasi", "baslik": "SF2 ses bankası (FluidSynth)", "lisans": "sf2_ses_bankasi", "hedef": ["onbellek", "sf2"],
     "dosyalar": []},
    {"ad": "muzik_cekirdek_seti", "baslik": "Müzik çekirdek seti (≈ 10–15 CC0 parça)", "lisans": "muzik_cekirdek_seti",
     "hedef": ["ses_kutuphanesi", "MUZIK_CEKIRDEK"], "dosyalar": []},
]
VARSAYILAN_AYAR = {
    "_surum": 3, "ortam": "yerel", "mod": "tam_otomatik",
    "saglayicilar": {"gorsel": ["gemini_paket"], "gorsel_duzeltme": ["flow_gorsel"], "video": ["flow"], "tts": ["ai84"],
                     "muzik": {"yayin": ["acestep", "kutuphane"], "animatik": ["acestep", "midi_ornek"]}},
    "butce": {"flow_kredi_tavan_film": None, "ai84_kredi_tavan_film": 60000, "ai84_seri_kurulum_tavan": 40000, "ai84_vc_tavan_film": 20000,
              "usd_tavan_film": 0, "takvim_hedef_gun": 21},
    "izinler": {"gece_flow": False, "gemini_api_ucretli": False, "flow_kilitliyken_vertex": False, "cc0_efekt_indir": False,
                "youtube_baglanti": False, "yukleme": False},
    "bildirim": {"telegram": True, "masaustu": True}, "yayin_kaynagi": "capcut"}

CALISIYOR, CALISMIYOR, ATLANDI, BILGI = "çalışıyor", "çalışmıyor", "atlandı", "bilgi"


class Kurulum:
    def __init__(self, veri=None, depo=None, kuru=False, deneme=False, yaz=print):
        self.veri_arg, self.depo_arg, self.kuru, self.deneme, self.yaz = veri, depo, kuru, deneme, yaz
        self.maddeler, self.rapor, self.ag = [], {}, None

    # -------------------------------------------------------------- yardımcılar
    def m(self, durum, ad, mesaj, **ek):
        self.maddeler.append(dict(durum=durum, ad=ad, mesaj=mesaj, **ek))
        self.yaz(f"  [{durum.upper()}] {ad}: {mesaj}")

    def baslik(self, t): self.yaz("\n" + "=" * 64 + f"\n {t}\n" + "=" * 64)

    def ag_var(self):
        if self.kuru: return False
        if self.ag is None:
            try: socket.create_connection(("pypi.org", 443), timeout=4).close(); self.ag = True
            except OSError: self.ag = False
        return self.ag

    def ag_yok_mesaji(self, ad):
        self.m(ATLANDI, ad, "kuru çalıştırma (--kuru): ağ adımı yapılmadı" if self.kuru else
               "internet yok: bu adım atlandı; internet gelince KURULUM.bat'ı yeniden çalıştır")

    # -------------------------------------------------------------- adımlar
    def yollar_ve_emniyet(self):
        import veri_emniyet
        self.baslik("1/9 Yollar ve veri kökü emniyeti (eski Memmet ve .bat'lar _ESKI'ye taşınır; hiçbir şey silinmez)")
        y = ortak.yollar_yaz(self.veri_arg)
        if self.depo_arg: y["depo_kok"] = os.path.abspath(self.depo_arg); ortak.atomik_yaz(ortak.yollar_dosyasi(), y)
        self.Y = ortak.yollar(); self.depo = self.Y["depo_kok"]
        self.m(CALISIYOR, "YOLLAR.json", f"veri kökü {self.Y['veri_kok']}")
        try:
            r = veri_emniyet.veri_emniyet(self.Y["veri_kok"], sessiz=True)
            iyi = r["durum"] in ("temiz", "veri_yok")
            self.emniyet = r["durum"]
            self.m(CALISIYOR if iyi else CALISMIYOR, "veri kökü emniyeti",
                   f"{r['durum']}; {len(r['tasinan'])} dosya _ESKI'ye taşındı" + (": " + ", ".join(t["dosya"] for t in r["tasinan"][:8])
                                                                               if r["tasinan"] else ""))
        except BaseException as e:
            self.emniyet = "hata"; self.m(CALISMIYOR, "veri kökü emniyeti", f"çalışmadı: {str(e)[:120]}")
        for d in ("AYARLAR", "FILMLER", "HESAP", "_ESKI"): os.makedirs(os.path.join(self.Y["veri_kok"], d), exist_ok=True)

    def python(self):
        self.baslik("2/9 Python (ana ortam)")
        v = sys.version_info
        if v < (3, 10): self.m(CALISMIYOR, "Python", f"{v.major}.{v.minor} eski; python.org'dan Python 3.10 kur ('Add to PATH')"); return False
        (self.m(CALISIYOR, "Python", f"{v.major}.{v.minor}.{v.micro} · {sys.executable}") if v[:2] == ANA_PYTHON else
         self.m(BILGI, "Python", f"{v.major}.{v.minor}.{v.micro}: ana ortam Python 3.10 olmalı (KUR1); kütüphaneler bu sürümle denendi"))
        return True

    def film_ayar(self):
        p = os.path.join(self.Y["ayarlar"], "FILM_AYAR.json"); eski = ortak.json_oku(p, None)
        yeni = film_ayar_birlestir(eski or {})
        if eski is not None and eski != yeni and int((eski or {}).get("_surum", 0) or 0) < 3:
            h = os.path.join(self.Y["ayarlar"], "_ESKI", time.strftime("FILM_AYAR_%Y%m%d_%H%M%S.json"))
            os.makedirs(os.path.dirname(h), exist_ok=True); shutil.copy2(p, h)
        if eski != yeni: ortak.atomik_yaz(p, yeni)
        acik = [k for k, v in yeni["izinler"].items() if v]
        self.m(CALISIYOR, "FILM_AYAR.json", f"v3; mod {yeni['mod']}; açık izin: {', '.join(acik) or 'yok'} (IZINLER.bat ile yalnız sen değiştirirsin)")

    def git(self):
        self.baslik("3/9 Programlar: git, Claude Code, ffmpeg, Chrome, CapCut")
        g = shutil.which("git"); dot = os.path.exists(os.path.join(self.depo, ".git"))
        self.rapor["git"] = {"var": bool(g), "depo_git": dot, "guncelle": bool(g and dot)}
        if not g: self.m(CALISMIYOR, "git", "kurulu değil: git-scm.com'dan git'i kur (GUNCELLE.bat için gerekli), sonra KURULUM.bat'ı yeniden çalıştır")
        else: self.m(CALISIYOR, "git", (_cikti(["git", "--version"]) or "var").strip())
        self.m(CALISIYOR if dot else BILGI, "GUNCELLE.bat", "açık (set git clone ile kurulmuş)" if dot else
               "kapalı: set ZIP ile kurulmuş (.git yok). Güncelleme için BASLA_BURADAN.txt'deki 'git clone' adımıyla yeniden kur")

    def claude(self):
        s = _cikti(["claude", "--version"]) if shutil.which("claude") else None
        v = surum_ayikla(s); self.rapor["claude"] = {"surum": ".".join(map(str, v)) if v else None,
                                                     "en_az": ".".join(map(str, CLAUDE_EN_AZ)), "uygun": bool(v and v >= CLAUDE_EN_AZ)}
        if not v: self.m(CALISMIYOR, "Claude Code", "bulunamadı: Claude Code'u kur (claude.ai/code); FILM_SETI.bat onu açar")
        elif v < CLAUDE_EN_AZ: self.m(CALISMIYOR, "Claude Code", f"{self.rapor['claude']['surum']} eski; en az {self.rapor['claude']['en_az']} (kendini günceller; sonra yeniden çalıştır)")
        else: self.m(CALISIYOR, "Claude Code", f"{self.rapor['claude']['surum']} (en az {self.rapor['claude']['en_az']}; kaydedildi)")

    def programlar(self):
        if shutil.which("ffmpeg") and shutil.which("ffprobe"): self.m(CALISIYOR, "ffmpeg", "bulundu")
        elif not self.ag_var() or os.name != "nt": self.m(CALISMIYOR, "ffmpeg", "yok" + ("" if os.name == "nt" else " (Windows dışı: paket yöneticisiyle kur)"))
        else:
            subprocess.run(["winget", "install", "-e", "--id", "Gyan.FFmpeg", "--accept-package-agreements", "--accept-source-agreements"])
            self.m(CALISIYOR if shutil.which("ffmpeg") else CALISMIYOR, "ffmpeg", "kuruldu" if shutil.which("ffmpeg") else
                   "kuruldu ama görünmüyor: pencereyi kapatıp KURULUM.bat'ı yeniden çalıştır")
        c = chrome_bul()
        self.m(CALISIYOR if c else CALISMIYOR, "Google Chrome", c or "bulunamadı: google.com/chrome adresinden kur")
        cc = self.Y.get("capcut_taslak") or ""
        self.m(CALISIYOR if os.path.isdir(cc) else CALISMIYOR, "CapCut masaüstü", "bulundu" if os.path.isdir(cc) else
               "proje klasörü yok: CapCut'ı kur, bir kez açıp boş proje oluştur, kapat")
        prof = os.path.join(self.Y["ayarlar"], "memmet_profil")
        self.m(CALISIYOR if os.path.isdir(prof) else BILGI, "Flow girişi", "Memmet profili var" if os.path.isdir(prof) else
               "henüz yok: FLOW_GIRIS.bat ile Flow'a kendi Google hesabınla bir kez gir")

    def anahtarlar(self):
        self.baslik("4/9 Anahtar dosyaları (içerik açılmaz, yazdırılmaz; yalnız var/boş ve tarih)")
        dolu = depo_anahtar_denetimi(self.depo)
        self.rapor["depo_anahtar_dolu"] = dolu
        self.m(CALISMIYOR if dolu else CALISIYOR, "depodaki anahtar dosyaları",
               ("DOLU (içerik gösterilmedi): " + ", ".join(dolu) + ". Anahtarı veri klasöründeki AYARLAR'a taşı; depodaki dosya boş kalmalı")
               if dolu else "hepsi boş")
        os.makedirs(self.Y["ayarlar"], exist_ok=True); durum = {}
        for ad, aciklama in VERI_ANAHTARLARI.items():
            p = os.path.join(self.Y["ayarlar"], ad)
            if not os.path.exists(p): open(p, "w", encoding="utf-8").close()
            d = dosya_durumu(p); durum[ad] = d
            if ad == "telegram_bot.txt":
                self.m(BILGI, ad, f"tarih {d['tarih']}" + ("" if d["dolu"] else " (boş; isteğe bağlı)"))
            elif ad == "gemini_anahtar.txt":
                self.m(CALISIYOR if d["dolu"] else BILGI, ad, f"var, tarih {d['tarih']}; GEMINI_TEST.bat ile sına" if d["dolu"] else
                       "boş: Google AI Studio'dan (faturalandırma açmadan) ücretsiz anahtar al, bu dosyanın ilk satırına yapıştır, GEMINI_TEST.bat")
            else:
                self.m(CALISIYOR if d["dolu"] else BILGI, ad, f"var, tarih {d['tarih']}" if d["dolu"] else f"boş — {aciklama}")
        self.rapor["anahtar_dosyalari"] = durum
        eski = ortak.json_oku(self.rapor_yolu(), {}) or {}
        if not eski.get("gemini_bilgi_verildi"):
            import bat_isleri
            self.m(BILGI, "Gemini ücretsiz katman", bat_isleri.GEMINI_BILGI)
        self.rapor["gemini_bilgi_verildi"] = True

    def disk(self):
        self.baslik("5/9 Disk ve önbellek")
        try:
            import esikler; en_az = esikler.yukle()["disk_bos_min_gb"]
        except Exception: en_az = 20
        bos = shutil.disk_usage(self.Y["veri_kok"]).free / 1e9
        onb = {}
        for ad, yol in (("onbellek", self.Y.get("onbellek")), ("huggingface", os.path.join(os.path.expanduser("~"), ".cache", "huggingface"))):
            if yol and os.path.isdir(yol): onb[ad] = round(klasor_boyutu(yol) / 1e9, 2)
        self.rapor["disk"] = {"bos_gb": round(bos, 1), "en_az_gb": en_az, "onbellek_gb": onb}
        self.m(CALISIYOR if bos >= en_az else CALISMIYOR, "disk", f"boş {bos:.1f} GB (en az {en_az} GB)" +
               (f"; önbellek: " + ", ".join(f"{k} {v} GB" for k, v in onb.items()) if onb else "") +
               ("" if bos >= en_az else ". Yer aç: önbellek temizliği senin işin (Claude silmez)"))

    def kutuphaneler(self):
        self.baslik("6/9 KUR1 kütüphaneleri (CPU torch + requirements.txt)")
        if not self.ag_var(): self.ag_yok_mesaji("KUR1 kütüphaneleri"); return
        if var("torch"): self.m(CALISIYOR, "torch", "zaten kurulu")
        else: self.m(CALISIYOR if pip("torch", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cpu") else CALISMIYOR,
                     "torch (CPU, D-37)", "kurulum")
        self.m(CALISIYOR if pip("-r", os.path.join(KD, "requirements.txt")) else CALISMIYOR, "requirements.txt", "kurulum")

    def modeller(self):
        self.baslik("7/9 Yapay zekâ modelleri (bir kez indirilir; sonra çevrimdışı)")
        self.rapor["modeller_tamam"] = (ortak.json_oku(self.rapor_yolu(), {}) or {}).get("modeller_tamam", False)
        if not self.ag_var():
            self.ag_yok_mesaji("modeller"); return
        os.environ.setdefault("HF_HOME", os.path.join(self.Y.get("onbellek") or "", "huggingface"))
        L, tamam = lisanslar(), True
        for anahtar, baslik, tur, kimlik in MODELLER:
            if not lisans_izinli(L, anahtar, self.deneme):
                self.m(ATLANDI, baslik, "lisansı doğrulanmadı ('bilinmiyor'): ana hatta kurulmaz (yalnız --deneme)"); continue
            try: model_indir(tur, kimlik); self.m(CALISIYOR, baslik, "hazır")
            except Exception as e: tamam = False; self.m(CALISMIYOR, baslik, f"indirilemedi: {str(e)[:120]}")
        self.rapor["modeller_tamam"] = tamam

    def muzik(self):
        self.baslik("8/9 Müzik: FluidSynth, SF2, çekirdek set (sabit adres + SHA-1)")
        self.rapor["indirmeler"] = {}
        for g in INDIRMELER:
            r = indirme_uygula(g, self.Y, lisanslar(), deneme=self.deneme, ag=self.ag_var())
            self.rapor["indirmeler"][g["ad"]] = r
            self.m({"hazir": CALISIYOR, "kuruldu": CALISIYOR, "hata": CALISMIYOR}.get(r["durum"], ATLANDI), g["baslik"], r["mesaj"])
            if r["durum"] in ("ag_yok",) and self.kuru: self.maddeler[-1]["mesaj"] = "kuru çalıştırma: indirilmedi"
        if self.rapor["indirmeler"]["muzik_cekirdek_seti"]["durum"] not in ("hazir", "kuruldu"):
            self.m(BILGI, "müzik zinciri", "kütüphane basamağı boş: bu durumda ipucu müziksiz kalır ve BAYRAK yazılır, hat durmaz (D-25)")

    def claude_ayarlari(self):
        self.baslik("9/9 Claude Code ayarları ve .bat dosyaları")
        py = os.path.abspath((self.Y.get("python") or {}).get("ana") or sys.executable)
        p = os.path.join(self.depo, ".claude", "settings.local.json")
        s = settings_local(ortak.json_oku(p, {}) or {}, py, self.Y, self.rapor.get("modeller_tamam"))
        ortak.atomik_yaz(p, s)
        self.m(CALISIYOR, "settings.local.json", f"mutlak Python yolu, PATH başı, veri kökü ek klasör ({p})")
        pt = os.path.join(self.depo, ".claude", "bin", "python_yolu.txt")
        os.makedirs(os.path.dirname(pt), exist_ok=True)
        with open(pt + ".tmp", "w", encoding="utf-8", newline="\n") as f: f.write(py + "\n")
        os.replace(pt + ".tmp", pt)
        self.m(CALISIYOR, "python_yolu.txt", py)

    def batlar(self):
        import bat_yenile
        try:
            r = bat_yenile.yenile(depo=self.depo, veri=self.Y["veri_kok"], yaz=lambda *a: None)
            n = len(r["yazilan"]); asc = all(x["ascii"] for x in r["yazilan"])
            self.m(CALISIYOR, ".bat dosyaları", f"{n} dosya (Python ve betik mutlak yolla" + ("" if asc else "; yolda Türkçe harf: UTF-8") + ")")
        except Exception as e: self.m(CALISMIYOR, ".bat dosyaları", f"yazılamadı: {str(e)[:120]}")

    # -------------------------------------------------------------- akış
    def rapor_yolu(self): return os.path.join(self.Y["ayarlar"], "KURULUM_RAPORU.json")

    def kart(self):
        try:
            return olcek.kart_md(olcek.hesapla(1800, ayar=os.path.join(self.Y["ayarlar"], "FILM_AYAR.json")))
        except Exception as e: return f"(sözleşme kartı hesaplanamadı: {str(e)[:100]})"

    def calis(self):
        self.yollar_ve_emniyet()
        if not self.python(): return self.bitir(4)
        self.film_ayar(); self.git(); self.claude(); self.programlar(); self.anahtarlar(); self.disk()
        self.kutuphaneler(); self.modeller(); self.muzik(); self.claude_ayarlari(); self.batlar()
        return self.bitir()

    def bitir(self, kod=None):
        cal = [x for x in self.maddeler if x["durum"] == CALISMIYOR]
        if kod is None: kod = 1 if cal else (3 if getattr(self, "emniyet", "") == "KALAN_VAR" else 0)
        self.yaz("\n" + "=" * 64 + "\n ÇALIŞIYOR / ÇALIŞMIYOR KARTI\n" + "=" * 64)
        for x in self.maddeler:
            if x["durum"] != BILGI or x["ad"] in ("GUNCELLE.bat",): self.yaz(f"  {x['durum']:<11} {x['ad']}")
        kart = self.kart()
        self.yaz("\n" + kart)
        self.yaz("\n" + ("KURULUM TAMAM. Masaüstündeki FILM_SETI.bat'a çift tıkla ve filmin konusunu yaz." if not cal else
                         f"{len(cal)} madde çalışmıyor; yukarıdaki satırları düzeltip KURULUM.bat'ı yeniden çalıştır."))
        r = dict(self.rapor, _surum=1, _uretim={"arac": SURUM, "zaman": time.strftime("%Y-%m-%d %H:%M:%S")}, kuru=self.kuru,
                 maddeler=self.maddeler, cikis_kodu=kod, sozlesme_karti=kart)
        try: ortak.atomik_yaz(self.rapor_yolu(), r)
        except Exception: pass
        return kod


# ---------------------------------------------------------------- saf yardımcılar (testlenir)
def film_ayar_birlestir(eski):
    """Güvenli v3 FILM_AYAR (§5.6): eksik alanlar varsayılanla dolar; kullanıcının izin, tercih ve para tavanları korunur;
    eski izinler.onayli_kip → mod. Bilinmeyen alanlar korunur (güvenlik sayısıysa esikler.py yalnız sıkılaştırır + BAYRAK).
    ortam makine gerçeğidir: YZ_FILM_ORTAM ya da Windows → yerel, değilse bulut."""
    import copy
    a = copy.deepcopy(VARSAYILAN_AYAR)
    for k, v in (eski or {}).items():
        if k in ("_surum", "ortam"): continue
        if isinstance(v, dict) and isinstance(a.get(k), dict) and k != "saglayicilar":
            a[k].update(v)
        elif k == "saglayicilar" and isinstance(v, dict):
            for t, z in v.items():
                if t in ("ses",) and "tts" not in v: a["saglayicilar"]["tts"] = z
                elif t == "muzik" and isinstance(z, list): continue        # eski düz liste: v3 yayin/animatik yapısı korunur
                else: a["saglayicilar"][t] = z
        else: a[k] = v
    izin = a["izinler"]
    if "onayli_kip" in izin:
        if izin.pop("onayli_kip") and "mod" not in (eski or {}): a["mod"] = "onayli"
    if a.get("mod") not in ("tam_otomatik", "onayli"): a["mod"] = "tam_otomatik"
    for k in VARSAYILAN_AYAR["izinler"]: izin[k] = izin.get(k) is True
    e = os.environ.get("YZ_FILM_ORTAM")
    a["ortam"] = e if e in ("yerel", "bulut") else ("yerel" if os.name == "nt" else "bulut")
    a["_surum"] = 3
    return a


def settings_local(eski, python, Y, modeller_tamam=False):
    """settings.local.json (D-11, §6.2): mutlak Python, PATH başına ana Python klasörü, veri kökü ek klasör, alt ajan derinliği 1,
    önbellekler; modeller indirildiyse HF_HUB_OFFLINE=1. Kullanıcının başka anahtarları korunur."""
    import copy
    s = copy.deepcopy(eski or {}); env = s.setdefault("env", {})
    pdir = os.path.dirname(os.path.abspath(python)); bas = [pdir, os.path.join(pdir, "Scripts")] if os.name == "nt" else [pdir]
    yol = [p for p in os.environ.get("PATH", "").split(os.pathsep) if p and p not in bas]
    env.update(PATH=os.pathsep.join(bas + yol), YZ_FILM_PYTHON=os.path.abspath(python), CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH="1")
    onb = Y.get("onbellek")
    if onb: env.update(HF_HOME=os.path.join(onb, "huggingface"), PIP_CACHE_DIR=os.path.join(onb, "pip"))
    if modeller_tamam: env["HF_HUB_OFFLINE"] = "1"
    izin = s.setdefault("permissions", {}); ek = izin.setdefault("additionalDirectories", [])
    if Y["veri_kok"] not in ek: ek.append(Y["veri_kok"])
    return s


def dosya_durumu(yol):
    """Anahtar dosyası için yalnız var/dolu (boyut > 0) ve tarih. İçerik AÇILMAZ."""
    if not os.path.isfile(yol): return {"var": False, "dolu": False, "tarih": None}
    st = os.stat(yol)
    return {"var": True, "dolu": st.st_size > 0, "tarih": time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))}


def depo_anahtar_denetimi(depo):
    """Depodaki YZ_FILM/AYARLAR altında boyutu > 0 olan anahtar dosyalarının adları (içerik açılmaz)."""
    k = os.path.join(depo, "YZ_FILM", "AYARLAR"); out = []
    if not os.path.isdir(k): return out
    for kok, ds, fs in os.walk(k):
        ds[:] = [d for d in ds if d not in ("memmet_profil", "_ESKI")]
        for f in fs:
            if ANAHTAR_DESENI.search(f) and os.path.getsize(os.path.join(kok, f)) > 0:
                out.append(os.path.relpath(os.path.join(kok, f), depo).replace("\\", "/"))
    return sorted(out)


def surum_ayikla(s):
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", s or "")
    return tuple(int(x) for x in m.groups()) if m else None


def _cikti(cmd, timeout=30):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return (r.stdout or r.stderr) if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError): return None


def klasor_boyutu(yol, sinir=200000):
    t = n = 0
    for kok, _, fs in os.walk(yol):
        for f in fs:
            n += 1
            if n > sinir: return t
            try: t += os.path.getsize(os.path.join(kok, f))
            except OSError: pass
    return t


def var(m): return importlib.util.find_spec(m) is not None


def chrome_bul():
    try:
        import memmet
        c = memmet.chrome_bul()
        return c if c and os.path.exists(c) else None
    except BaseException:
        for ad in ("google-chrome", "chrome", "chromium"):
            if shutil.which(ad): return shutil.which(ad)
        return None


def pip(*args):
    """pip; sertifika sorunu olan bilgisayarlarda (antivirüs vb.) Windows sertifika deposuyla tekrar dener."""
    base = [sys.executable, "-m", "pip", "install", "--disable-pip-version-check"]
    if subprocess.run(base + list(args)).returncode == 0: return True
    print("  (pip başarısız; Windows sertifika deposuyla tekrar deneniyor)")
    whl = glob.glob(os.path.join(KD, "truststore-*.whl"))
    if whl and not var("truststore"): subprocess.run(base + ["--no-index", whl[0]])
    return subprocess.run(base + ["--use-feature=truststore"] + list(args)).returncode == 0


def model_indir(tur, kimlik):
    if tur == "transformers":
        from transformers import AutoModel, AutoProcessor
        AutoModel.from_pretrained(kimlik); AutoProcessor.from_pretrained(kimlik)
    elif tur == "whisper":
        from faster_whisper import WhisperModel
        WhisperModel(kimlik, device="cpu", compute_type="int8")
    elif tur == "demucs":
        from demucs.pretrained import get_model
        get_model(kimlik)


def lisanslar():
    return (ortak.json_oku(os.path.join(HERE, "veri", "LISANSLAR.json"), {}) or {}).get("bilesenler", {})


def lisans_izinli(L, anahtar, deneme=False):
    """D-36: LISANSLAR.json'da 'bilinmiyor' ya da kaydı olmayan bileşen ana hatta kurulmaz (yalnız --deneme)."""
    r = L.get(anahtar)
    return bool(deneme or (r and r.get("dogrulama") in ("bellekten", "dogrulandi")))


def sha1(yol):
    h = hashlib.sha1()
    with open(yol, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def indirme_uygula(g, Y, L, deneme=False, ag=True):
    """Sabit adres + SHA-1 indirmesi. durum: hazir | kuruldu | lisans | secilmedi | ag_yok | hata.
    Dosya önce .indiriliyor'a iner, SHA-1 tutarsa yerine konur; tutmazsa _ESKI/'ye taşınır (silinmez) ve hata."""
    hedef = os.path.join(Y.get(g["hedef"][0]) or "", *g["hedef"][1:])
    if g.get("ikili") and shutil.which(g["ikili"]): return {"durum": "hazir", "mesaj": f"{g['ikili']} PATH'te bulundu", "hedef": hedef}
    if not g["dosyalar"]:
        return {"durum": "secilmedi", "hedef": hedef, "mesaj": "sabit adres ve SHA-1 henüz seçilmedi (geliştirme oturumu); kurulmadı"}
    if not lisans_izinli(L, g["lisans"], deneme):
        return {"durum": "lisans", "hedef": hedef, "mesaj": "lisansı LISANSLAR.json'da doğrulanmadı ('bilinmiyor'); kurulmadı (yalnız --deneme)"}
    eksik = [d for d in g["dosyalar"] if not (os.path.isfile(os.path.join(hedef, d["ad"])) and sha1(os.path.join(hedef, d["ad"])) == d["sha1"])]
    if not eksik: return {"durum": "hazir", "hedef": hedef, "mesaj": f"{len(g['dosyalar'])} dosya hazır (SHA-1 tuttu)"}
    if not ag: return {"durum": "ag_yok", "hedef": hedef, "mesaj": f"{len(eksik)} dosya eksik; internet yok, indirilmedi"}
    os.makedirs(hedef, exist_ok=True); hatalar = []
    for d in eksik:
        son = os.path.join(hedef, d["ad"]); tmp = son + ".indiriliyor"
        try:
            with urllib.request.urlopen(d["url"], timeout=120) as r, open(tmp, "wb") as f: shutil.copyfileobj(r, f)
        except Exception as e: hatalar.append(f"{d['ad']}: indirilemedi ({str(e)[:60]})"); continue
        if sha1(tmp) != d["sha1"]:
            k = os.path.join(hedef, "_ESKI", time.strftime("%Y%m%d_%H%M%S")); os.makedirs(k, exist_ok=True)
            shutil.move(tmp, os.path.join(k, d["ad"] + ".sha1_tutmadi")); hatalar.append(f"{d['ad']}: SHA-1 tutmadı"); continue
        if os.path.exists(son):
            k = os.path.join(hedef, "_ESKI", time.strftime("%Y%m%d_%H%M%S")); os.makedirs(k, exist_ok=True); shutil.move(son, os.path.join(k, d["ad"]))
        os.replace(tmp, son)
    if hatalar: return {"durum": "hata", "hedef": hedef, "mesaj": "; ".join(hatalar)}
    return {"durum": "kuruldu", "hedef": hedef, "mesaj": f"{len(eksik)} dosya indirildi (SHA-1 tuttu)"}


def main(a=None):
    a = sys.argv[1:] if a is None else list(a)
    al = lambda k: a[a.index(k) + 1] if k in a and a.index(k) + 1 < len(a) else None
    veri = al("--veri")
    if "--yollar" in a:
        y = ortak.yollar_yaz(veri); print("YOLLAR.json yazıldı:", ortak.yollar_dosyasi(), "· veri kökü:", y["veri_kok"]); return 0
    if "--veri-emniyet" in a:
        import veri_emniyet
        print("Veri kökü emniyeti"); r = veri_emniyet.veri_emniyet(veri)
        return 0 if r["durum"] in ("temiz", "veri_yok") else 3
    if "--ses-ortamlari" in a or "--kur3" in a:
        print("KUR2/KUR3 kurulumu henüz yok (TASARIM P1); gerekince ekip ekler. Ana kurulum için: python kurulum.py"); return 4
    return Kurulum(veri=veri, depo=al("--depo"), kuru="--kuru" in a, deneme="--deneme" in a).calis()


if __name__ == "__main__":
    sys.exit(main())
