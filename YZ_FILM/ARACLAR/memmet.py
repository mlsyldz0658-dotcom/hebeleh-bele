"""MEMMET AUTO — SAHNELER.json'daki sahneleri Google Flow'da kendi kendine üretir.

Kullanım:
  python memmet.py <film_klasoru> --giris            Memmet Chrome'unu açar; Google'a bir kez sen giriş yaparsın
  python memmet.py <film_klasoru>                    bütün partiler: her partide önce görseller, sonra videolar
  python memmet.py <film_klasoru> --mod elle         (varsayılan) Memmet istemi hazırlar, GÖNDER'e (Oluşturmaya başla) SEN basarsın
  python memmet.py <film_klasoru> --mod gece         Memmet kendisi gönderir; yalnız AYARLAR/FILM_AYAR.json "izinler.gece_flow": true ise
  python memmet.py <film_klasoru> --asama gorsel     yalnız görseller   (--asama video: yalnız videolar)
  python memmet.py <film_klasoru> --parti 1,2        yalnız bu partiler  (--sahne 3,7: yalnız bu sahneler)
  python memmet.py <film_klasoru> --telegram-test    telefona deneme mesajı

Kendi Chrome profiliyle (ARACLAR/memmet_profil) gerçek Chrome'u açar ve ona bağlanır; senin diğer oturumlarına dokunmaz.
Ekran görüntüsüne bakmaz, sayfanın yapısını okur. Her sonucu Flow'daki istem metninden tanıyıp NNN.jpg / NNN.mp4 olarak kaydeder.
Yük sınırı: gönderimler arası bekleme ve molalar kodda sabittir (17.10 değerleri); MEMMET_AYAR.json yalnız YAVAŞLATABİLİR.
Son gönderim zamanı ve kalan mola HESAP/FLOW_TEMPO.json'da tutulur; Memmet'i kapatıp açmak molayı sıfırlamaz.

GÜVENLİK (bot tespiti atlatılmaz; 03_DERSLER.md):
  - Flow "olağan dışı etkinlik" derse, HER KİPTE anında durur: sayfada başka hiçbir işlem yapmaz (tıklama, yazma, yenileme yok),
    HESAP/FLOW_KILIDI.json yazar, haber verir ve 7 ile çıkar. Kilit varken Memmet açılmaz. GÖNDER'e basma, sayfayı yenileme.
  - reCAPTCHA, doğrulama ya da oturum düşmesinde beklemez, kendiliğinden sürmez: haber verir ve 2 ile çıkar.
    Sen çözersin, sonra Memmet'i yeniden başlatırsın.
  - SAHNELER.json "_surum" ≥ 2 ise (v2 dosyası) bu sürüm hiçbir şey yapmaz, 4 ile çıkar.
Çıkış kodları: 0 bitti · 1 beklenmeyen hata · 2 durdu (doğrulama/giriş/kredi/arayüz) · 4 ortam/sürüm · 7 Flow uyarısı.
Son çıkışın nedeni film klasöründe _memmet_cikis.json'a yazılır. Her şey MEMMET_KAYIT.txt'ye, durum MEMMET_DURUM.json'a yazılır.
"""
import os, sys, re, json, time, datetime, random, shutil, socket, subprocess, urllib.request, urllib.parse, traceback, ctypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import ortak
try: _Y = ortak.yollar()                     # yollar yalnız YOLLAR.json'dan (kurulum.py --yollar)
except ortak.YolYok as e:
    if __name__ == "__main__": print("!!", e); sys.exit(4)
    raise
VERI = _Y["veri_kok"]
AYARLAR = _Y["ayarlar"]
AYAR_DOSYA = os.path.join(AYARLAR, "MEMMET_AYAR.json")
FILM_AYAR = os.path.join(AYARLAR, "FILM_AYAR.json")
HESAP = _Y["hesap"]                          # hesap düzeyindeki durum: tempo ve kilit (filmden bağımsız)


def chrome_bul():
    for p in (os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if os.path.exists(p): return p
    return "chrome.exe"


def telegram_bul():
    for p in (os.path.join(AYARLAR, "telegram_bot.txt"), os.path.join(os.path.expanduser("~"), "Desktop", "telegram_bot.txt")):
        if os.path.exists(p) and open(p, encoding="utf-8-sig").read().strip(): return p
    return os.path.join(AYARLAR, "telegram_bot.txt")


# Bilgisayara özel yollar (chrome, profil, telegram) her çalıştırmada bulunur
VARSAYILAN = {
    "chrome": chrome_bul(),
    "profil": os.path.join(AYARLAR, "memmet_profil"),
    "port": 9333,
    "gorsel_zaman_asimi_sn": 180,
    "video_zaman_asimi_sn": 360,
    "video_cozunurluk": "720p",
    "video_sure": "8 sn.",
    "telegram_dosya": telegram_bul(),   # 1. satır bot anahtarı, 2. satır sohbet no
}
# Yük sınırı (17.10 değerleri). Kodda sabit; ayar dosyası bunları yalnız YAVAŞLATABİLİR (sikilastir).
#   gonderim_arasi_sn   iki gönderim arası rastgele bekleme      ayni_anda           aynı anda en fazla kaç üretim beklesin
#   mola_kac_gonderimde N gönderimde bir mola (0: yok)           mola_kac_partide    N partide bir mola (0: yok)
TEMPO = {
    "elle": {"gonderim_arasi_sn": [6, 15], "ayni_anda": 2, "mola_kac_gonderimde": 8, "gonderim_mola_dk": [3, 6],
             "mola_kac_partide": 0, "parti_mola_dk": [0, 0]},
    "gece": {"gonderim_arasi_sn": [12, 30], "ayni_anda": 2, "mola_kac_gonderimde": 0, "gonderim_mola_dk": [0, 0],
             "mola_kac_partide": 2, "parti_mola_dk": [15, 30]},
}
KIPLER = tuple(TEMPO)
FLOW = "https://flow.google.com/"
# Olağan dışı etkinlik: HER KİPTE anında dur, sayfaya dokunma (çıkış 7). Bu liste yalnız BÜYÜYEBİLİR.
OLAGANDISI_KELIMELERI = ["olağandışı etkinlik", "olağan dışı etkinlik", "olagandisi etkinlik", "olagan disi etkinlik",
                         "unusual traffic", "unusual activity", "olağandışı trafik", "olağan dışı trafik"]
# Tek sonuç kartındaki üretim hatası (yeniden denenebilir). "olağan/unusual" BURADA YOK: onlar uyarıdır, hata değil.
HATA_KELIMELERI = ["politika", "ihlal", "uygunsuz", "güvenlik", "başarısız", "oluşturulamadı",
                   "üretilemedi", "violat", "policy", "couldn't", "could not", "failed", "something went wrong",
                   "bir sorun", "bir hata"]
# Doğrulama / robot sorusu: beklemeden dur (çıkış 2). "doğrulayın" tek başına yazılmaz: Flow'un altında hep "yanıtları doğrulayın" yazıyor
DOGRULAMA_KELIMELERI = ["robot olmadığınızı", "not a robot", "kimliğinizi doğrulayın", "verify it's you"]
KREDI_KELIMELERI = ["yetersiz kredi", "kredi yetersiz", "kredin bitti", "not enough credits", "out of credits", "insufficient credits"]
CIKIS = {"tamam": 0, "beklenmeyen": 1, "dogrulama": 2, "giris": 2, "kredi": 2, "arayuz": 2, "genel": 2, "ortam": 4, "surum": 4,
         "olagandisi": 7, "kilitli": 7}


def _yavas(kod, gelen):
    """İki değerden yavaş (güvenli) olanı. Aralıklar eleman eleman büyük; ayni_anda küçük; mola sıklığı küçük (0 = yok sayılır)."""
    try:
        if isinstance(kod, list):
            g = [float(x) for x in gelen][:len(kod)]
            return [max(a, b) for a, b in zip(kod, g)] if len(g) == len(kod) else kod
        g = int(gelen)
        if kod == 0: return 0                                # kodda kapalı olan mola sıklığı ayarla açılmaz (gece/elle farkı)
        return min(kod, g) if g > 0 else kod
    except (TypeError, ValueError): return kod


def sikilastir(kip, dosya_ayar):
    """Kodda sabit tempo + ayar dosyası → yalnız yavaşlayan birleşim."""
    t = {k: (list(v) if isinstance(v, list) else v) for k, v in TEMPO[kip].items()}
    for k in t:
        if k in dosya_ayar: t[k] = _yavas(t[k], dosya_ayar[k])
    return t


def ayar(kip="elle"):
    a = dict(VARSAYILAN)
    d = {}
    if os.path.exists(AYAR_DOSYA):
        try: d = json.load(open(AYAR_DOSYA, encoding="utf-8-sig"))
        except ValueError: d = {}
    # eski (sürümsüz) dosyayı eski Memmet kendiliğinden yazmıştı (360p, hızlı tempo): ondan yalnız yavaşlatan tempo alınır
    if int(d.get("_surum", 1) or 1) >= 2:
        for k in ("port", "gorsel_zaman_asimi_sn", "video_zaman_asimi_sn", "video_cozunurluk"):
            if k in d: a[k] = d[k]
        if a["video_cozunurluk"] not in ("720p", "1080p"): a["video_cozunurluk"] = "720p"   # en az 720p
    a.update(sikilastir(kip, d)); a["kip"] = kip
    return a


def gece_izni():
    try: return bool(json.load(open(FILM_AYAR, encoding="utf-8-sig")).get("izinler", {}).get("gece_flow"))
    except (OSError, ValueError, AttributeError): return False


def kilit_yolu(): return os.path.join(HESAP, "FLOW_KILIDI.json")


def tempo_yolu(): return os.path.join(HESAP, "FLOW_TEMPO.json")


uyu = time.sleep   # testler bekleme yapmadan koşabilsin diye tek noktadan


def _atomik(yol, veri):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=1)
    os.replace(tmp, yol)


def cikis_yaz(root, kod, mesaj):
    """Son çıkışın nedeni: film.py / saglayicilar.flow kodu buradan okur."""
    try: _atomik(os.path.join(root, "_memmet_cikis.json"), {"kod": kod, "cikis": CIKIS.get(kod, 1), "mesaj": mesaj,
                                                              "zaman": time.strftime("%Y-%m-%d %H:%M:%S")})
    except OSError: pass


def kilit_yaz(film, mesaj):
    """Flow uyarısı → hesap düzeyinde kilit. Aynı takvim haftasında ikinci uyarı → en erken 7 gün sonra (tahmin)."""
    os.makedirs(HESAP, exist_ok=True)
    simdi = time.time(); y, h, _ = datetime.date.today().isocalendar(); hafta = f"{y}-{h:02d}"   # %G/%V Windows'ta yok
    gecmis = os.path.join(HESAP, "FLOW_UYARILARI.jsonl")
    onceki = 0
    if os.path.exists(gecmis):
        for l in open(gecmis, encoding="utf-8"):
            try: onceki += json.loads(l).get("hafta") == hafta
            except ValueError: pass
    with open(gecmis, "a", encoding="utf-8") as f:
        f.write(json.dumps({"zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "hafta": hafta, "film": film}, ensure_ascii=False) + "\n")
    if os.path.exists(kilit_yolu()): return            # var olan kilidin tarihi korunur
    _atomik(kilit_yolu(), {
        "_surum": 1, "neden": "olagandisi", "film": film, "mesaj": mesaj, "zaman": time.strftime("%Y-%m-%d %H:%M:%S"),
        "zaman_epoch": int(simdi), "haftanin_uyarisi": onceki + 1,
        "en_erken": time.strftime("%Y-%m-%d %H:%M", time.localtime(simdi + (7 * 86400 if onceki else 1800))),
        "nasil_kalkar": "GÖNDER'e basma, sayfayı yenileme. Bekle; en erken 'en_erken' zamanında Flow'da ELLE tek bir video dene. "
                        "Sorunsuzsa Claude'a 'Flow uyarısı geçti' de; kilidi o kaldırır. Başka Google/Flow hesabıyla devam edilmez."})


def norm(s): return re.sub(r"\s+", " ", (s or "")).strip().lower()


class Durdur(Exception):
    """Kullanıcının müdahalesi gereken durum. kod: olagandisi | kilitli | dogrulama | giris | kredi | arayuz | ortam | surum | genel."""
    def __init__(self, msg, kod="genel"):
        super().__init__(msg); self.kod = kod


class Memmet:
    def __init__(self, root, args):
        self.root = os.path.abspath(root); self.args = args
        kip = args.get("mod", "elle")
        if kip not in KIPLER: raise Durdur(f"Bilinmeyen kip: {kip} (elle | gece)", kod="ortam")
        self.A = ayar(kip)
        self.plan = json.load(open(os.path.join(self.root, "SAHNELER.json"), encoding="utf-8-sig"))
        if int(self.plan.get("_surum", 1) or 1) >= 2:
            raise Durdur("SAHNELER.json v2 (_surum ≥ 2): bu Memmet v1, hiçbir şey yapmadı. Memmet v2 gerekli.", kod="surum")
        self.film = self.plan["film"]
        self.sg = os.path.join(self.root, "SIRALI_GORSEL"); self.sv = os.path.join(self.root, "SIRALI_VIDEO")
        self.hata_dir = os.path.join(self.root, "_MEMMET_HATALAR"); self.gecici = os.path.join(self.root, "_memmet_gecici")
        for d in (self.sg, self.sv, self.hata_dir, self.gecici): os.makedirs(d, exist_ok=True)
        self.kayit = open(os.path.join(self.root, "MEMMET_KAYIT.txt"), "a", encoding="utf-8")
        self.dp = os.path.join(self.root, "MEMMET_DURUM.json")
        self.D = json.load(open(self.dp, encoding="utf-8")) if os.path.exists(self.dp) else {"proje_url": None, "yuklenen": [], "sahne": {}}
        self.page = None; self._tg = None; self.uyari_goruldu = False

    # ------------------------------------------------------------------ kayıt ve bildirim
    def log(self, *a):
        line = time.strftime("%d.%m %H:%M:%S ") + " ".join(str(x) for x in a)
        print(line, flush=True); self.kayit.write(line + "\n"); self.kayit.flush()

    def save(self): json.dump(self.D, open(self.dp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def sc(self, n): return self.D["sahne"].setdefault(str(n), {})

    def telegram(self):
        if self._tg is None:
            p = self.A.get("telegram_dosya")
            self._tg = [l.strip() for l in open(p, encoding="utf-8-sig") if l.strip()][:2] if p and os.path.exists(p) else []
        return self._tg if len(self._tg) == 2 else None

    def bildir(self, msg, acil=False):
        self.log("BİLDİRİM:", msg)
        try:
            import winsound
            for _ in range(3 if acil else 1): winsound.MessageBeep(winsound.MB_ICONEXCLAMATION); time.sleep(0.4)
        except Exception: pass
        try:   # Windows balon bildirimi
            ps = ("Add-Type -AssemblyName System.Windows.Forms; $n=New-Object System.Windows.Forms.NotifyIcon; "
                  "$n.Icon=[System.Drawing.SystemIcons]::Information; $n.Visible=$true; "
                  f"$n.ShowBalloonTip(15000,'Memmet Auto','{msg.replace(chr(39), '')[:200]}','Info'); Start-Sleep 16; $n.Dispose()")
            subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps],
                             creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        except Exception: pass
        tg = self.telegram()
        if tg:
            try:
                data = urllib.parse.urlencode({"chat_id": tg[1], "text": ("🚨 " if acil else "🎬 ") + f"[{self.film}] {msg}"}).encode()
                urllib.request.urlopen(f"https://api.telegram.org/bot{tg[0]}/sendMessage", data, timeout=8)
            except Exception as e: self.log("telegram gönderilemedi:", str(e)[:80])

    # ------------------------------------------------------------------ Chrome
    def chrome_ac(self):
        port = self.A["port"]
        def acik():
            with socket.socket() as s:
                s.settimeout(1); return s.connect_ex(("127.0.0.1", port)) == 0
        if not acik():
            os.makedirs(self.A["profil"], exist_ok=True)
            subprocess.Popen([self.A["chrome"], f"--remote-debugging-port={port}", f"--user-data-dir={self.A['profil']}",
                              "--no-first-run", "--no-default-browser-check", "--start-maximized", FLOW])
            for _ in range(60):
                if acik(): break
                time.sleep(1)
            else: raise Durdur("Memmet Chrome'u açılamadı.")
        from playwright.sync_api import sync_playwright
        self.pw = sync_playwright().start()
        self.browser = self.pw.chromium.connect_over_cdp(f"http://127.0.0.1:{port}")
        ctx = self.browser.contexts[0]
        self.page = next((p for p in ctx.pages if "flow.google.com" in p.url), None) or (ctx.pages[0] if ctx.pages else ctx.new_page())
        self.page.set_default_timeout(20000)
        self.log("Chrome bağlandı.")

    def kapat(self):
        try: self.pw.stop()
        except Exception: pass

    # ------------------------------------------------------------------ güvenlik kontrolleri
    def sayfa_metni(self):
        try: return norm(self.page.evaluate("document.body ? document.body.innerText.slice(0, 20000) : ''"))
        except Exception: return ""

    def olagandisi_denetle(self, t=None):
        """Olağan dışı etkinlik → HER KİPTE anında Durdur(olagandisi). Bundan sonra sayfaya hiçbir işlem yapılmaz."""
        t = self.sayfa_metni() if t is None else norm(t)
        if any(k in t for k in OLAGANDISI_KELIMELERI):
            self.uyari_goruldu = True
            raise Durdur("Flow uyarı verdi (olağan dışı etkinlik): GÖNDER'e basma, sayfayı yenileme. Memmet durdu; Claude'a haber ver.",
                         kod="olagandisi")

    def dogrulama_var_mi(self, t=None):
        try:
            if self.page.evaluate("""[...document.querySelectorAll('iframe[src*="recaptcha"]')].some(f => {
                const r = f.getBoundingClientRect(); return r.width > 100 && r.height > 100 && getComputedStyle(f).visibility !== 'hidden'; })"""):
                return True
        except Exception: pass
        t = self.sayfa_metni() if t is None else t; u = self.page.url or ""
        return any(k in t for k in DOGRULAMA_KELIMELERI) or "accounts.google.com" in u or "/about" in u

    def kontrol_noktasi(self):
        """Sayfada her işlemden önce çağrılır. Beklemez, kendiliğinden sürmez: uyarıda 7, doğrulama/oturumda 2 ile durdurur."""
        t = self.sayfa_metni()
        self.olagandisi_denetle(t)
        if self.dogrulama_var_mi(t):
            raise Durdur("Doğrulama (reCAPTCHA) ya da Google girişi istendi. Memmet beklemeden durdu: Memmet Chrome penceresinde "
                         "kendin çöz, sonra Memmet'i yeniden başlat.", kod="dogrulama")
        if any(k in t for k in KREDI_KELIMELERI): raise Durdur("Flow kredisi bitti.", kod="kredi")

    # ------------------------------------------------------------------ yük sınırı (tempo)
    def tempo_oku(self):
        try: return json.load(open(tempo_yolu(), encoding="utf-8"))
        except (OSError, ValueError): return {"_surum": 1, "son_gonderim": 0, "sonraki_izin": 0, "mola_bitis": 0,
                                              "gonderim_sayaci": 0, "parti_sayaci": 0}

    def tempo_bekle(self):
        """Bir sonraki izinli zamana kadar bekler. Zaman dosyada; Memmet'i yeniden açmak molayı sıfırlamaz."""
        T = self.tempo_oku(); hedef = max(T.get("sonraki_izin", 0), T.get("mola_bitis", 0)); kalan = hedef - time.time()
        if kalan > 0:
            if kalan > 60: self.log(f"MOLA / yük sınırı: {int(kalan // 60)} dk {int(kalan % 60)} sn bekleniyor (sayfaya dokunulmuyor)")
            uyu(kalan)

    def gonderim_kaydet(self):
        T = self.tempo_oku(); simdi = time.time(); A = self.A
        T["son_gonderim"] = simdi; T["gonderim_sayaci"] = T.get("gonderim_sayaci", 0) + 1; T["kip"] = A["kip"]
        T["sonraki_izin"] = simdi + random.uniform(*A["gonderim_arasi_sn"])
        n = A.get("mola_kac_gonderimde", 0)
        if n and T["gonderim_sayaci"] % n == 0:
            T["mola_bitis"] = max(T.get("mola_bitis", 0), simdi + random.uniform(*A["gonderim_mola_dk"]) * 60)
            self.log(f"{n} gönderim oldu → mola (bitiş {time.strftime('%H:%M', time.localtime(T['mola_bitis']))})")
        _atomik(tempo_yolu(), T)

    def parti_bitti(self):
        """Parti sonu. Mola düştüyse True (mola sonrası proje sayfası yeniden açılır)."""
        T = self.tempo_oku(); n = self.A.get("mola_kac_partide", 0); T["parti_sayaci"] = T.get("parti_sayaci", 0) + 1
        mola = bool(n and T["parti_sayaci"] % n == 0)
        if mola:
            T["mola_bitis"] = max(T.get("mola_bitis", 0), time.time() + random.uniform(*self.A["parti_mola_dk"]) * 60)
            self.log(f"{n} parti oldu → mola (bitiş {time.strftime('%H:%M', time.localtime(T['mola_bitis']))})")
        _atomik(tempo_yolu(), T)
        return mola

    def hata_kaydi(self, ad):
        base = os.path.join(self.hata_dir, time.strftime("%m%d_%H%M%S_") + ad)
        try: self.page.screenshot(path=base + ".png", timeout=15000)
        except Exception: pass
        try: open(base + ".html", "w", encoding="utf-8").write(self.page.content())
        except Exception: pass
        self.log("hata kaydı:", base)

    def bekle(self, a, b=None):
        uyu(random.uniform(a, b if b is not None else a))

    # ------------------------------------------------------------------ giriş ve proje
    def giris_kontrol(self, bekle_giris=False):
        """bekle_giris=True yalnız --giris içindir (sen giriş yaparsın). Üretimde girişsizse beklemez, 2 ile durur."""
        self.olagandisi_denetle()
        self.page.goto(FLOW, wait_until="domcontentloaded"); self.bekle(4)
        self.olagandisi_denetle()
        if self.girisli(): return True
        if not bekle_giris:
            raise Durdur("Memmet Chrome'unda Flow girişi yok (oturum düşmüş). MEMMET_GIRIS.bat ile giriş yap, sonra yeniden başlat.", kod="giris")
        self.bildir("Memmet Chrome'unda Google'a giriş yapılmamış. Açılan pencerede Flow'a giriş yap.", acil=True)
        t0 = time.time()
        while not self.girisli():
            uyu(10); self.olagandisi_denetle()
            if time.time() - t0 > 3600: raise Durdur("Bir saat içinde giriş yapılmadı.", kod="giris")
        return True

    def girisli(self):
        """Girişsiz kullanıcıyı Flow /about tanıtım sayfasına atar; girişliyken hesap düğmesi vardır."""
        u = self.page.url or ""
        if "accounts.google.com" in u or "/about" in u: return False
        try:
            return self.page.evaluate("""!!document.querySelector('[aria-label^="Google Hesabı"], [aria-label^="Google Account"]')
                || [...document.querySelectorAll('a[href*="/project/"]')].length > 0 || !!document.querySelector('.ProseMirror')""")
        except Exception: return False

    def projeye_git(self):
        self.kontrol_noktasi()
        if self.D.get("proje_url"):
            self.page.goto(self.D["proje_url"], wait_until="domcontentloaded")
        else:
            self.page.goto(FLOW, wait_until="domcontentloaded"); self.bekle(3)
            self.kontrol_noktasi()
            self.page.get_by_text("Yeni proje", exact=False).first.click()
            self.page.wait_for_url(re.compile(r"/project/"), timeout=30000); self.bekle(3)
            title = self.page.get_by_role("textbox", name="Düzenlenebilir metin").first
            title.click(click_count=3); self.bekle(0.5)
            self.page.keyboard.type(self.film[:60], delay=60); self.page.keyboard.press("Enter")
            self.D["proje_url"] = self.page.url.split("?")[0]; self.save()
            self.log("Yeni Flow projesi:", self.film, self.D["proje_url"])
        self.page.wait_for_selector(".ProseMirror", timeout=45000); self.bekle(2, 4)
        self.kontrol_noktasi()
        self.yukari()

    def yukari(self):
        try: self.page.evaluate("(document.getElementById('main-content') || document.scrollingElement).scrollTo(0, 0)")
        except Exception: pass

    # ------------------------------------------------------------------ ayarlar
    def ayar_dugmesi(self): return self.page.get_by_role("button", name="Ayarlar tetikleyicisi").first

    def ayar_yazisi(self): return norm(self.ayar_dugmesi().inner_text())

    def radyo(self, metin):
        """Seçenek yazısı 'simge|Yazı' biçiminde (ör. 'image|Resim'); son parçası eşleşeni tıkla."""
        i = self.page.evaluate("""(m) => [...document.querySelectorAll('[role=radio]')]
            .findIndex(r => r.innerText.split('\\n').map(s => s.trim()).includes(m))""", metin)
        if i < 0: raise Durdur(f"Ayar seçeneği bulunamadı: {metin} (Flow arayüzü değişmiş olabilir)")
        r = self.page.locator("[role=radio]").nth(i)
        if r.get_attribute("aria-checked") != "true": r.click(); self.bekle(0.3, 0.7)

    def ayar_menusu_ac(self):
        for _ in range(3):
            self.ayar_dugmesi().click(); self.bekle(0.8, 1.2)
            try: self.page.wait_for_selector("[role=radio]", timeout=4000); return
            except Exception: self.page.keyboard.press("Escape"); self.bekle(1)
        self.hata_kaydi("ayar_menusu"); raise Durdur("Ayar menüsü açılmadı.")

    def mod_ayarla(self, tur):
        """tur: 'gorsel' ya da 'video'. Yanlışsa düzeltir, sonra yazıdan doğrular."""
        def dogru():
            y = self.ayar_yazisi()
            if tur == "gorsel": return "nano banana" in y and "x1" in y and "video" not in y
            return "video" in y and norm(self.A["video_cozunurluk"]) in y and norm(self.A["video_sure"]).replace(".", "") in y.replace(".", "") and "x1" in y
        if dogru(): return
        for deneme in range(2):
            self.ayar_menusu_ac()
            if tur == "gorsel":
                self.radyo("Resim"); self.radyo("16:9"); self.radyo("x1")
            else:
                self.radyo("Video"); self.radyo("Kareler"); self.radyo("16:9")
                self.radyo(self.A["video_cozunurluk"]); self.radyo(self.A["video_sure"]); self.radyo("x1")
            self.page.keyboard.press("Escape"); self.bekle(0.6, 1.2)
            if dogru(): self.log("Ayar:", self.ayar_yazisi()); return
        self.hata_kaydi("ayar"); raise Durdur(f"Ayar doğrulanamadı ({tur}): {self.ayar_yazisi()}")

    # ------------------------------------------------------------------ yükleme
    def yukle(self, yollar):
        """Dosyaları Flow projesine yükler (adı korunur: mara.jpg, 007.jpg). Daha önce yüklenenleri atlar."""
        yollar = [p for p in yollar if os.path.basename(p) not in self.D["yuklenen"]]
        for i in range(0, len(yollar), 10):
            grup = yollar[i:i + 10]
            self.kontrol_noktasi()
            self.yukari()
            self.page.evaluate("""() => { let i = document.getElementById('memmet_yukle'); if (!i) { i = document.createElement('input');
                i.type = 'file'; i.multiple = true; i.id = 'memmet_yukle'; i.style.cssText = 'position:fixed;left:-9999px;top:0';
                document.body.appendChild(i); } }""")
            self.page.set_input_files("#memmet_yukle", grup)
            self.page.evaluate("""() => { const i = document.getElementById('memmet_yukle'); const dt = new DataTransfer();
                for (const f of i.files) dt.items.add(f); const x = innerWidth / 2, y = innerHeight / 2; const el = document.elementFromPoint(x, y);
                for (const t of ['dragenter', 'dragover', 'drop']) el.dispatchEvent(new DragEvent(t, {bubbles: true, cancelable: true, composed: true, dataTransfer: dt, clientX: x, clientY: y})); }""")
            # liste sanal (görünmeyen karolar sayfada yok), o yüzden karo saymak yerine yükleme yüzdelerinin bitmesini bekle
            t0, sakin = time.time(), 0
            self.bekle(4)
            while time.time() - t0 < 180:
                self.bekle(2)
                sakin = sakin + 1 if not self.ilerleme_var() else 0
                if sakin >= 2: break
            else: self.log("UYARI: yükleme beklenenden uzun sürdü", [os.path.basename(p) for p in grup])
            self.D["yuklenen"] += [os.path.basename(p) for p in grup]; self.save()
            self.log("yüklendi:", ", ".join(os.path.basename(p) for p in grup))
            self.bekle(*self.A["gonderim_arasi_sn"])

    def ilerleme_var(self):
        return self.page.evaluate(r"""[...document.querySelectorAll('div.batch-container *')].some(e => e.childElementCount === 0 && /^%\d+$/.test(e.textContent.trim()))""")

    # ------------------------------------------------------------------ istem kutusu
    def kutudaki_icerik(self):
        return self.page.evaluate("""() => { const b = document.querySelector('flow-base-prompt-box'); if (!b) return 0;
            let w = b; for (let k = 0; k < 3 && w.parentElement; k++) w = w.parentElement;
            return w.querySelectorAll('img[alt="İçerik öğesi resmi"]').length; }""")

    def secicide_sec(self, dosya):
        """Açık medya seçicisinde dosyayı adıyla bulup isteme ekler."""
        ara = self.page.get_by_placeholder(re.compile("Öğe ara", re.I)).first
        ara.fill(""); ara.type(dosya, delay=40); self.bekle(1.2, 2)
        opt = self.page.locator("[role=option]").filter(has_text=dosya)
        if opt.count() == 0: raise Durdur(f"Seçicide bulunamadı: {dosya}")
        opt.first.click(); self.bekle(0.8, 1.3)
        ekle = self.page.get_by_role("button", name="İsteme ekle")
        if ekle.count() and ekle.first.is_visible() and ekle.first.is_enabled():
            ekle.first.click(); self.bekle(0.8, 1.3)
        if self.page.locator("[role=listbox]").count() and self.page.locator("[role=listbox]").first.is_visible():
            self.page.keyboard.press("Escape"); self.bekle(0.5)

    def referans_ekle(self, dosya):
        once = self.kutudaki_icerik()
        self.page.get_by_role("button", name="İçerik öğelerini istem kutusuna ekle").first.click(); self.bekle(1, 1.6)
        self.secicide_sec(dosya)
        if self.kutudaki_icerik() <= once:
            self.hata_kaydi("referans"); raise Durdur(f"Referans istem kutusuna eklenemedi: {dosya}")

    def kare_ekle(self, yuva, dosya):
        self.page.get_by_role("button", name=yuva, exact=True).first.click(); self.bekle(1, 1.6)
        self.secicide_sec(dosya)

    def kutuyu_temizle(self):
        """Önceki denemeden kalan referans/kareleri ve yazıyı siler."""
        try:
            x = self.page.locator("flow-base-prompt-box").locator("xpath=../../..").get_by_role("button", name=re.compile("Temizle|Kaldır|close", re.I))
            for _ in range(5):
                if self.kutudaki_icerik() == 0: break
                if x.count(): x.first.click(); self.bekle(0.4)
                else: break
        except Exception: pass
        pm = self.page.locator(".ProseMirror").first
        pm.click(); self.page.keyboard.press("Control+A"); self.page.keyboard.press("Delete")

    def istem_yaz_gonder(self, metin, etiket=""):
        """İstemi yazar. gece: kendisi gönderir. elle: GÖNDER'e (Oluşturmaya başla) kullanıcının basmasını bekler."""
        self.kontrol_noktasi()
        pm = self.page.locator(".ProseMirror").first
        pm.click(); self.bekle(0.3, 0.6)
        self.page.keyboard.type(metin, delay=random.randint(8, 18))
        self.bekle(0.6, 1.5)
        self.kontrol_noktasi()
        if norm(pm.inner_text())[:40] != norm(metin)[:40]: raise Durdur("İstem kutusuna yazılamadı.", kod="arayuz")
        if self.A["kip"] == "elle":
            self.log(f">> {etiket} HAZIR. Memmet Chrome'unda istemi kontrol et, doğruysa 'Oluşturmaya başla'ya SEN bas.")
            t0 = time.time(); hatirlat = t0 + 600
            while norm(pm.inner_text()):
                uyu(2); self.kontrol_noktasi()
                if time.time() > hatirlat: self.log(f">> {etiket} hâlâ GÖNDER bekliyor."); hatirlat = time.time() + 600
            return True
        self.page.get_by_role("button", name="Oluşturmaya başla").first.click()
        t0 = time.time()
        while time.time() - t0 < 20:
            self.bekle(1)
            self.olagandisi_denetle()
            if not norm(pm.inner_text()): return True
        self.hata_kaydi("gonderim"); self.log("UYARI: istem gönderilmedi gibi görünüyor (kutu temizlenmedi)")
        return False

    # ------------------------------------------------------------------ sonuç takibi
    def kutu_bul(self, metin):
        """İstem metniyle eşleşen üretim kutusunun durumunu döndürür."""
        return self.page.evaluate("""(hedef) => {
            const n = s => (s || '').replace(/\\s+/g, ' ').trim().toLowerCase();
            const kutular = [...document.querySelectorAll('div.batch-container')];
            for (const b of kutular) {
                const p = b.querySelector('flow-expandable-prompt'); if (!p) continue;
                const t = n(p.innerText || p.textContent);
                if (!t || !(hedef.startsWith(t.slice(0, 60)) || t.startsWith(hedef.slice(0, 60)))) continue;
                const img = b.querySelector('img[data-media-id]');
                const vid = [...b.querySelectorAll('video')].map(v => v.currentSrc || v.src).find(s => /flow-content\\.google\\/video\\//.test(s));
                const yuzde = [...b.querySelectorAll('*')].some(e => e.childElementCount === 0 && /^%\\d+$/.test(e.textContent.trim()));
                return {var: true, gorsel_id: img ? img.getAttribute('data-media-id') : null, gorsel_url: img ? (img.currentSrc || img.src) : null,
                        video_url: vid || null, video_kutusu: !!b.querySelector('flow-video-tile'), yuzde,
                        metin: n(b.innerText).slice(0, 400), sira: kutular.indexOf(b)};
            }
            return {var: false};
        }""", norm(metin))

    def video_adresi(self, metin):
        """Video kutusunun üstüne gelip <video> adresini yükletir."""
        idx = self.kutu_bul(metin).get("sira")
        if idx is None: return None
        tile = self.page.locator("div.batch-container").nth(idx).locator("flow-video-tile").first
        try: tile.scroll_into_view_if_needed(timeout=5000); tile.hover(timeout=5000)
        except Exception: return None
        for _ in range(10):
            self.bekle(0.6)
            r = self.kutu_bul(metin)
            if r.get("video_url"): self.page.mouse.move(5, 5); return r["video_url"]
        return None

    def indir(self, url, hedef):
        tmp = hedef + ".part"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": FLOW})
            with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as f: shutil.copyfileobj(r, f)
        except Exception as e:   # yedek yol: dosyayı sayfanın içinden al
            self.log("doğrudan indirme olmadı, sayfa içinden alınıyor:", str(e)[:60])
            import base64
            b64 = self.page.evaluate("""async (u) => { const r = await fetch(u); const b = await r.blob();
                return await new Promise(res => { const fr = new FileReader(); fr.onload = () => res(fr.result.split(',')[1]); fr.readAsDataURL(b); }); }""", url)
            open(tmp, "wb").write(base64.b64decode(b64))
        if os.path.getsize(tmp) < 10_000: os.remove(tmp); raise RuntimeError("indirilen dosya çok küçük")
        os.replace(tmp, hedef)

    # ------------------------------------------------------------------ KONTROL ile köprü
    def kontrol_isle(self, n, tur, kaynak):
        try:
            import kontrol
            f = kontrol.Film(self.root); s = f.sc(n)
            if tur == "gorsel": s.update(gorsel=kaynak, gorsel_emin=True, gorsel_skor=None, gorsel_kaynak="memmet")
            else: s.update(video=kaynak, video_emin=True, video_skor=None, video_kaynak="memmet")
            f.save()
        except Exception as e: self.log("KONTROL güncellenemedi:", str(e)[:100])

    # ------------------------------------------------------------------ üretim döngüsü
    def sahneler(self, parti=None):
        out = []
        for s in self.plan["sahneler"]:
            if s.get("motor", "flow") != "flow": continue
            if parti is not None and s.get("parti") != parti: continue
            if self.args.get("sahne") and s["no"] not in self.args["sahne"]: continue
            out.append(s)
        return out

    def istemler(self, s, tur):
        ana = s["gorsel_istem"] if tur == "gorsel" else s["hareket_istem"]
        yedek = s.get("gorsel_istem_yedek" if tur == "gorsel" else "hareket_istem_yedek")
        return [ana, ana] + ([yedek] if yedek else [])          # aynı istemle 2 deneme, sonra yedek

    def asama(self, tur, sahneler):
        hedef_dir = self.sg if tur == "gorsel" else self.sv; ext = "jpg" if tur == "gorsel" else "mp4"
        isler = [s for s in sahneler if not os.path.exists(os.path.join(hedef_dir, f"{s['no']:03d}.{ext}"))
                 and self.sc(s["no"]).get(tur + "_durum") != "reddedildi"]
        if tur == "video":
            isler = [s for s in isler if os.path.exists(os.path.join(self.sg, f"{s['no']:03d}.jpg"))]
        if not isler: self.log(f"{tur}: yapılacak sahne yok"); return
        self.log(f"=== {tur.upper()} aşaması: {len(isler)} sahne ({', '.join(str(s['no']) for s in isler)})")
        self.mod_ayarla(tur)
        if tur == "gorsel":
            refs = {r for s in isler for r in s.get("referans", [])}
            self.yukle([os.path.join(self.root, self.plan["karakterler"][r]["ref"]) for r in sorted(refs)])
        else:   # kare olarak kullanılacak sahne görsellerini (ve bitiş karelerini) NNN.jpg adıyla yükle
            lazim = {s["no"] for s in isler} | {int(s["bitis_karesi"]) for s in isler if s.get("bitis_karesi")}
            self.yukle([os.path.join(self.sg, f"{n:03d}.jpg") for n in sorted(lazim) if os.path.exists(os.path.join(self.sg, f"{n:03d}.jpg"))])
        kuyruk = list(isler); bekleyen = {}       # sahne no -> {istem, gonderim, deneme}
        zaman_asimi = self.A["gorsel_zaman_asimi_sn" if tur == "gorsel" else "video_zaman_asimi_sn"]
        while kuyruk or bekleyen:
            self.kontrol_noktasi()
            # yeni gönderim
            if kuyruk and len(bekleyen) < self.A["ayni_anda"]:
                s = kuyruk.pop(0); st = self.sc(s["no"]); deneme = st.get(tur + "_deneme", 0)
                ist = self.istemler(s, tur)
                if deneme >= len(ist):
                    st[tur + "_durum"] = "reddedildi"; self.save(); self.log(f"{s['no']:03d} {tur}: bütün denemeler bitti → reddedildi")
                    continue
                metin = ist[deneme]
                self.tempo_bekle(); self.kontrol_noktasi()
                try:
                    self.mod_ayarla(tur); self.kutuyu_temizle()
                    if tur == "gorsel":
                        for r in s.get("referans", []): self.referans_ekle(os.path.basename(self.plan["karakterler"][r]["ref"]))
                    else:
                        self.kare_ekle("Başlat", f"{s['no']:03d}.jpg")
                        if s.get("bitis_karesi"): self.kare_ekle("Bitir", f"{int(s['bitis_karesi']):03d}.jpg")
                    ok = self.istem_yaz_gonder(metin, f"{s['no']:03d} {tur}")
                except Durdur: raise
                except Exception as e:
                    self.hata_kaydi(f"{s['no']:03d}_{tur}"); self.log(f"{s['no']:03d} {tur}: gönderim hatası: {str(e)[:150]}")
                    ok = False
                st[tur + "_deneme"] = deneme + 1; self.save()
                if ok: self.gonderim_kaydet()
                if ok:
                    bekleyen[s["no"]] = {"istem": metin, "t": time.time(), "s": s}
                    self.log(f"{s['no']:03d} {tur}: gönderildi (deneme {deneme + 1}{', yedek istem' if deneme >= 2 else ''})")
                else:
                    kuyruk.insert(0, s); self.projeye_git()
                continue
            # sonuçları kontrol et
            self.bekle(4, 7)
            for n in list(bekleyen):
                b = bekleyen[n]; s = b["s"]; r = self.kutu_bul(b["istem"]); gecen = time.time() - b["t"]
                if r.get("var"): self.olagandisi_denetle(r.get("metin", ""))
                hedef = os.path.join(hedef_dir, f"{n:03d}.{ext}")
                if r.get("var") and tur == "gorsel" and r.get("gorsel_url") and not r.get("yuzde"):
                    try:
                        self.indir(r["gorsel_url"], hedef); self.kontrol_isle(n, tur, f"memmet:{r['gorsel_id']}")
                        self.sc(n)[tur + "_durum"] = "tamam"; self.save(); self.log(f"{n:03d} görsel: KAYDEDİLDİ ({int(gecen)} sn)")
                        del bekleyen[n]
                    except Exception as e: self.log(f"{n:03d} görsel indirilemedi, tekrar denenecek: {str(e)[:80]}")
                    continue
                if r.get("var") and tur == "video" and r.get("video_kutusu") and not r.get("yuzde"):
                    url = r.get("video_url") or self.video_adresi(b["istem"])
                    if url:
                        try:
                            self.indir(url, hedef)
                            vid = (re.search(r"video/([0-9a-f-]{36})", url) or [None, "?"])[1]
                            self.kontrol_isle(n, tur, f"memmet:{vid}")
                            self.sc(n)[tur + "_durum"] = "tamam"; self.save(); self.log(f"{n:03d} video: KAYDEDİLDİ ({int(gecen)} sn)")
                            del bekleyen[n]
                        except Exception as e: self.log(f"{n:03d} video indirilemedi, tekrar denenecek: {str(e)[:80]}")
                        continue
                hata = r.get("var") and not r.get("yuzde") and not r.get("gorsel_url") and not r.get("video_kutusu") \
                    and any(k in r.get("metin", "") for k in HATA_KELIMELERI)
                if hata or gecen > zaman_asimi:
                    neden = "Flow reddetti/hata" if hata else "zaman aşımı"
                    self.log(f"{n:03d} {tur}: {neden} → yeniden denenecek. Flow'un yazısı: {r.get('metin', '')[:160]}")
                    if not hata: self.hata_kaydi(f"{n:03d}_{tur}_zamanasimi")
                    del bekleyen[n]; kuyruk.append(s)
                    if gecen > zaman_asimi: self.projeye_git()

    def on_kosullar(self):
        """Chrome açılmadan önce: kilit ve izin. Sayfaya dokunmaz."""
        if os.path.exists(kilit_yolu()):
            k = {}
            try: k = json.load(open(kilit_yolu(), encoding="utf-8"))
            except (OSError, ValueError): pass
            raise Durdur(f"Flow kilidi var ({k.get('zaman', '?')} uyarısı; en erken {k.get('en_erken', '?')}). Memmet açılmadı. "
                         "GÖNDER'e basma; Claude'a haber ver.", kod="kilitli")
        if self.A["kip"] == "gece" and not gece_izni():
            raise Durdur("Gece kipi kapalı: AYARLAR/FILM_AYAR.json içinde izinler.gece_flow açık değil. Varsayılan kip: elle.", kod="ortam")

    def calis(self):
        self.on_kosullar()
        ES = 0x80000000 | 0x00000001
        try: ctypes.windll.kernel32.SetThreadExecutionState(ES)   # çalışırken uyku yok
        except Exception: pass
        self.chrome_ac(); self.giris_kontrol(); self.projeye_git()
        partiler = sorted({s.get("parti", 1) for s in self.sahneler()})
        if self.args.get("parti"): partiler = [p for p in partiler if p in self.args["parti"]]
        asamalar = ["gorsel", "video"] if self.args.get("asama", "hepsi") == "hepsi" else [self.args["asama"]]
        self.log(f"BAŞLADI · film {self.film} · kip {self.A['kip']} · partiler {partiler} · aşama {asamalar}")
        self.bildir(f"Başladı ({self.A['kip']}): partiler {partiler}, aşama {'+'.join(asamalar)}")
        for i, p in enumerate(partiler, 1):
            for tur in asamalar: self.asama(tur, self.sahneler(p))
            self.bildir(f"Parti {p} bitti.")
            if self.parti_bitti() and i < len(partiler):
                self.tempo_bekle(); self.projeye_git()
        try:
            import kontrol
            f = kontrol.Film(self.root); f.reports(); f.save()
        except Exception as e: self.log("rapor hatası:", str(e)[:100])
        red = [n for n, v in self.D["sahne"].items() if "reddedildi" in (v.get("gorsel_durum"), v.get("video_durum"))]
        self.bildir("Üretim BİTTİ." + (f" Reddedilen sahneler: {', '.join(red)}" if red else " Reddedilen sahne yok."))
        if not self.args.get("kurgu_yok") and "video" in asamalar: self.kurgu()

    def kurgu(self):
        """Zincirin sonu: seslendirme + CapCut projesi (render yok)."""
        videolu = [s for s in self.plan["sahneler"] if os.path.exists(os.path.join(self.sv, f"{s['no']:03d}.mp4"))]
        if not videolu: return
        for ad, betik in (("Seslendirme", "seslendir.py"), ("CapCut projesi", "capcut_film.py")):
            self.log(f"{ad} başlıyor...")
            r = subprocess.run([sys.executable, os.path.join(HERE, betik), self.root], capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            self.kayit.write(r.stdout[-4000:] + "\n" + r.stderr[-2000:] + "\n"); self.kayit.flush()
            if r.returncode != 0:
                self.bildir(f"{ad} hata verdi; MEMMET_KAYIT.txt'ye bak.", acil=True); return
        try:
            info = json.load(open(os.path.join(self.root, "KURGU", "son_capcut_projesi.json"), encoding="utf-8"))
            self.bildir(f"CapCut projesi hazır: {info['proje']} ({info['klip']} klip, {round(info['sure_sn'] / 60, 1)} dk). CapCut'ı aç, en üstte.")
        except Exception: self.bildir("CapCut projesi hazır.")


def bitir(m, root, kod, mesaj):
    """Durdur sonrası: önce kilit ve çıkış dosyası (sayfaya dokunmadan), sonra bildirim. Çıkış kodunu döndürür."""
    if kod == "olagandisi":
        kilit_yaz(getattr(m, "film", os.path.basename(root)), mesaj)
    cikis_yaz(root, kod, mesaj)
    if m is not None:
        try: m.bildir(f"DURDU: {mesaj}", acil=True)
        except Exception: pass
    else: print("DURDU:", mesaj, flush=True)
    return CIKIS.get(kod, 2)


def telegram_test():
    A = ayar(); p = A.get("telegram_dosya")
    lines = [l.strip() for l in open(p, encoding="utf-8-sig") if l.strip()] if p and os.path.exists(p) else []
    if not lines: print("Telegram bot anahtarı yok. @BotFather'dan aldığın anahtarı şu dosyanın İLK SATIRINA yapıştır:", p); return
    tok = lines[0]
    if len(lines) < 2:   # sohbet numarasını bota yazılan son mesajdan bul
        r = json.load(urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/getUpdates", timeout=20))
        ids = [u["message"]["chat"]["id"] for u in r.get("result", []) if "message" in u]
        if not ids: print("Önce telefondan bota bir mesaj yaz (örn. 'merhaba'), sonra tekrar çalıştır."); return
        open(p, "a", encoding="utf-8").write(f"\n{ids[-1]}\n"); lines.append(str(ids[-1])); print("Sohbet numarası kaydedildi.")
    data = urllib.parse.urlencode({"chat_id": lines[1], "text": "🎬 Memmet Auto bağlandı. Bildirimler buraya gelecek."}).encode()
    urllib.request.urlopen(f"https://api.telegram.org/bot{tok}/sendMessage", data, timeout=20); print("Deneme mesajı gönderildi.")


def main(a=None):
    a = sys.argv[1:] if a is None else a
    if not a: print(__doc__); return
    if "--telegram-test" in a: telegram_test(); return
    root = a[0]; args = {"asama": "hepsi", "kurgu_yok": "--kurgu-yok" in a, "mod": "elle"}
    for k in ("--asama", "--parti", "--sahne", "--mod"):
        if k in a:
            v = a[a.index(k) + 1]
            args[k[2:]] = v if k in ("--asama", "--mod") else [int(x) for x in v.split(",")]
    m = None
    try:
        m = Memmet(root, args)
        if "--giris" in a:
            m.on_kosullar(); m.chrome_ac(); m.giris_kontrol(bekle_giris=True)
            m.log("Giriş tamam. Bu pencereyi açık bırakabilir ya da kapatabilirsin."); cikis_yaz(root, "tamam", "giriş"); return
        m.calis(); cikis_yaz(root, "tamam", "bitti")
    except Durdur as e:
        if e.kod != "olagandisi" and m is not None and m.page is not None:
            try: m.olagandisi_denetle()      # başka bir nedenle duruyorsak bile uyarı varsa uyarı olarak kaydedilir
            except Durdur as e2: e = e2
        sys.exit(bitir(m, root, e.kod, str(e)))
    except KeyboardInterrupt:
        if m: m.log("Kullanıcı durdurdu.")
        cikis_yaz(root, "genel", "kullanıcı durdurdu"); sys.exit(2)
    except Exception:
        if m is None: raise
        m.log("BEKLENMEYEN HATA:\n" + traceback.format_exc())
        if not getattr(m, "uyari_goruldu", False): m.hata_kaydi("beklenmeyen")
        cikis_yaz(root, "beklenmeyen", "beklenmeyen hata")
        m.bildir("Beklenmeyen hata ile durdu. MEMMET_KAYIT.txt'ye bak.", acil=True); sys.exit(1)
    finally:
        if m: m.kapat()


if __name__ == "__main__":
    main()
