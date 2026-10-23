"""MEMMET AUTO — SAHNELER.json'daki sahneleri Google Flow'da kendi kendine üretir.

Kullanım:
  python memmet.py <film_klasoru> --giris            Memmet Chrome'unu açar; Google'a bir kez sen giriş yaparsın
  python memmet.py <film_klasoru>                    bütün partiler: her partide önce görseller, sonra videolar
  python memmet.py <film_klasoru> --asama gorsel     yalnız görseller   (--asama video: yalnız videolar)
  python memmet.py <film_klasoru> --parti 1,2        yalnız bu partiler  (--sahne 3,7: yalnız bu sahneler)
  python memmet.py <film_klasoru> --telegram-test    telefona deneme mesajı

Kendi Chrome profiliyle (ARACLAR/memmet_profil) gerçek Chrome'u açar ve ona bağlanır; senin diğer oturumlarına dokunmaz.
Ekran görüntüsüne bakmaz, sayfanın yapısını okur. Her sonucu Flow'daki istem metninden tanıyıp NNN.jpg / NNN.mp4 olarak kaydeder.
İnsan temposunda çalışır (rastgele bekleme, partiler arası mola). reCAPTCHA / olağandışı etkinlik görürse DURUR ve haber verir;
doğrulamayı sen çözersin, kaldığı yerden devam eder. Her şey MEMMET_KAYIT.txt'ye yazılır; durum MEMMET_DURUM.json'da tutulur.
"""
import os, sys, re, json, time, random, shutil, socket, subprocess, urllib.request, urllib.parse, traceback, ctypes
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

AYARLAR = os.path.join(os.path.dirname(HERE), "AYARLAR")
AYAR_DOSYA = os.path.join(AYARLAR, "MEMMET_AYAR.json")


def chrome_bul():
    for p in (os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
              r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        if os.path.exists(p): return p
    return "chrome.exe"


def telegram_bul():
    for p in (os.path.join(AYARLAR, "telegram_bot.txt"), os.path.join(os.path.expanduser("~"), "Desktop", "telegram_bot.txt")):
        if os.path.exists(p) and open(p, encoding="utf-8-sig").read().strip(): return p
    return os.path.join(AYARLAR, "telegram_bot.txt")


# Bilgisayara özel yollar (chrome, profil, telegram) her çalıştırmada bulunur; MEMMET_AYAR.json'a yalnız tempo ayarları yazılır
VARSAYILAN = {
    "chrome": chrome_bul(),
    "profil": os.path.join(AYARLAR, "memmet_profil"),
    "port": 9333,
    "gonderim_arasi_sn": [4, 12],          # iki gönderim arası rastgele bekleme
    "ayni_anda": 2,                        # aynı anda en fazla kaç üretim beklesin
    "mola_kac_partide": [2, 3],            # 2-3 partide bir mola
    "mola_dk": [5, 10, 15],                # mola süresi (rastgele biri)
    "gorsel_zaman_asimi_sn": 180,
    "video_zaman_asimi_sn": 360,
    "video_cozunurluk": "360p",
    "video_sure": "8 sn.",
    "telegram_dosya": telegram_bul(),   # 1. satır bot anahtarı, 2. satır sohbet no
}
YOL_ANAHTARLARI = ("chrome", "profil", "telegram_dosya")
FLOW = "https://flow.google.com/"
HATA_KELIMELERI = ["politika", "ihlal", "olağan", "olagan", "uygunsuz", "güvenlik", "başarısız", "oluşturulamadı",
                   "üretilemedi", "violat", "policy", "unusual", "couldn't", "could not", "failed", "something went wrong",
                   "bir sorun", "bir hata"]
# "doğrulayın" tek başına yazılmaz: Flow'un altında hep "yanıtları doğrulayın" yazıyor
DOGRULAMA_KELIMELERI = ["olağandışı etkinlik", "olağan dışı etkinlik", "unusual traffic", "unusual activity", "robot olmadığınızı",
                        "not a robot", "kimliğinizi doğrulayın", "verify it's you"]
KREDI_KELIMELERI = ["yetersiz kredi", "kredi yetersiz", "kredin bitti", "not enough credits", "out of credits", "insufficient credits"]


def ayar():
    a = dict(VARSAYILAN)
    os.makedirs(AYARLAR, exist_ok=True)
    if os.path.exists(AYAR_DOSYA): a.update(json.load(open(AYAR_DOSYA, encoding="utf-8-sig")))
    else: json.dump({k: v for k, v in VARSAYILAN.items() if k not in YOL_ANAHTARLARI},
                    open(AYAR_DOSYA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return a


def norm(s): return re.sub(r"\s+", " ", (s or "")).strip().lower()


class Durdur(Exception):
    """Kullanıcının müdahalesi gereken durum (kredi bitti, arayüz değişti...)."""


class Memmet:
    def __init__(self, root, args):
        self.root = os.path.abspath(root); self.args = args; self.A = ayar()
        self.plan = json.load(open(os.path.join(self.root, "SAHNELER.json"), encoding="utf-8-sig"))
        self.film = self.plan["film"]
        self.sg = os.path.join(self.root, "SIRALI_GORSEL"); self.sv = os.path.join(self.root, "SIRALI_VIDEO")
        self.hata_dir = os.path.join(self.root, "_MEMMET_HATALAR"); self.gecici = os.path.join(self.root, "_memmet_gecici")
        for d in (self.sg, self.sv, self.hata_dir, self.gecici): os.makedirs(d, exist_ok=True)
        self.kayit = open(os.path.join(self.root, "MEMMET_KAYIT.txt"), "a", encoding="utf-8")
        self.dp = os.path.join(self.root, "MEMMET_DURUM.json")
        self.D = json.load(open(self.dp, encoding="utf-8")) if os.path.exists(self.dp) else {"proje_url": None, "yuklenen": [], "sahne": {}}
        self.page = None; self._tg = None

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
                urllib.request.urlopen(f"https://api.telegram.org/bot{tg[0]}/sendMessage", data, timeout=15)
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

    def dogrulama_var_mi(self):
        try:
            if self.page.evaluate("""[...document.querySelectorAll('iframe[src*="recaptcha"]')].some(f => {
                const r = f.getBoundingClientRect(); return r.width > 100 && r.height > 100 && getComputedStyle(f).visibility !== 'hidden'; })"""):
                return True
        except Exception: pass
        t = self.sayfa_metni(); u = self.page.url or ""
        return any(k in t for k in DOGRULAMA_KELIMELERI) or "accounts.google.com" in u or "/about" in u

    def kontrol_noktasi(self):
        """Her adımda çağrılır: doğrulama/oturum/kredi durumunu yakalar."""
        if self.dogrulama_var_mi():
            self.bildir("Doğrulama (reCAPTCHA) ya da giriş istendi. Memmet bekliyor; Memmet Chrome penceresinde çöz, kendisi devam eder.", acil=True)
            t0 = time.time()
            while self.dogrulama_var_mi():
                time.sleep(15)
                if time.time() - t0 > 3600 * 12: raise Durdur("12 saat boyunca doğrulama çözülmedi.")
            self.log("Doğrulama çözüldü, devam."); time.sleep(5)
            self.projeye_git()
        t = self.sayfa_metni()
        if any(k in t for k in KREDI_KELIMELERI): raise Durdur("Flow kredisi bitti.")

    def hata_kaydi(self, ad):
        base = os.path.join(self.hata_dir, time.strftime("%m%d_%H%M%S_") + ad)
        try: self.page.screenshot(path=base + ".png", timeout=15000)
        except Exception: pass
        try: open(base + ".html", "w", encoding="utf-8").write(self.page.content())
        except Exception: pass
        self.log("hata kaydı:", base)

    def bekle(self, a, b=None):
        time.sleep(random.uniform(a, b if b is not None else a))

    # ------------------------------------------------------------------ giriş ve proje
    def giris_kontrol(self):
        self.page.goto(FLOW, wait_until="domcontentloaded"); self.bekle(4)
        t0 = time.time()
        while True:
            if self.girisli(): return True
            if time.time() - t0 < 5:
                self.bildir("Memmet Chrome'unda Google'a giriş yapılmamış. Açılan pencerede Flow'a giriş yap.", acil=True)
            time.sleep(10)
            if time.time() - t0 > 3600: raise Durdur("Bir saat içinde giriş yapılmadı.")

    def girisli(self):
        """Girişsiz kullanıcıyı Flow /about tanıtım sayfasına atar; girişliyken hesap düğmesi vardır."""
        u = self.page.url or ""
        if "accounts.google.com" in u or "/about" in u: return False
        try:
            return self.page.evaluate("""!!document.querySelector('[aria-label^="Google Hesabı"], [aria-label^="Google Account"]')
                || [...document.querySelectorAll('a[href*="/project/"]')].length > 0 || !!document.querySelector('.ProseMirror')""")
        except Exception: return False

    def projeye_git(self):
        if self.D.get("proje_url"):
            self.page.goto(self.D["proje_url"], wait_until="domcontentloaded")
        else:
            self.page.goto(FLOW, wait_until="domcontentloaded"); self.bekle(3)
            self.page.get_by_text("Yeni proje", exact=False).first.click()
            self.page.wait_for_url(re.compile(r"/project/"), timeout=30000); self.bekle(3)
            title = self.page.get_by_role("textbox", name="Düzenlenebilir metin").first
            title.click(click_count=3); self.bekle(0.5)
            self.page.keyboard.type(self.film[:60], delay=60); self.page.keyboard.press("Enter")
            self.D["proje_url"] = self.page.url.split("?")[0]; self.save()
            self.log("Yeni Flow projesi:", self.film, self.D["proje_url"])
        self.page.wait_for_selector(".ProseMirror", timeout=45000); self.bekle(2, 4)
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

    def istem_yaz_gonder(self, metin):
        pm = self.page.locator(".ProseMirror").first
        pm.click(); self.bekle(0.3, 0.6)
        self.page.keyboard.type(metin, delay=random.randint(8, 18))
        self.bekle(0.6, 1.5)
        if norm(pm.inner_text())[:40] != norm(metin)[:40]: raise Durdur("İstem kutusuna yazılamadı.")
        self.page.get_by_role("button", name="Oluşturmaya başla").first.click()
        t0 = time.time()
        while time.time() - t0 < 20:
            self.bekle(1)
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
                try:
                    self.mod_ayarla(tur); self.kutuyu_temizle()
                    if tur == "gorsel":
                        for r in s.get("referans", []): self.referans_ekle(os.path.basename(self.plan["karakterler"][r]["ref"]))
                    else:
                        self.kare_ekle("Başlat", f"{s['no']:03d}.jpg")
                        if s.get("bitis_karesi"): self.kare_ekle("Bitir", f"{int(s['bitis_karesi']):03d}.jpg")
                    ok = self.istem_yaz_gonder(metin)
                except Durdur: raise
                except Exception as e:
                    self.hata_kaydi(f"{s['no']:03d}_{tur}"); self.log(f"{s['no']:03d} {tur}: gönderim hatası: {str(e)[:150]}")
                    ok = False
                st[tur + "_deneme"] = deneme + 1; self.save()
                if ok:
                    bekleyen[s["no"]] = {"istem": metin, "t": time.time(), "s": s}
                    self.log(f"{s['no']:03d} {tur}: gönderildi (deneme {deneme + 1}{', yedek istem' if deneme >= 2 else ''})")
                else:
                    kuyruk.insert(0, s); self.projeye_git()
                self.bekle(*self.A["gonderim_arasi_sn"])
                continue
            # sonuçları kontrol et
            self.bekle(4, 7)
            for n in list(bekleyen):
                b = bekleyen[n]; s = b["s"]; r = self.kutu_bul(b["istem"]); gecen = time.time() - b["t"]
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

    def calis(self):
        ES = 0x80000000 | 0x00000001
        try: ctypes.windll.kernel32.SetThreadExecutionState(ES)   # çalışırken uyku yok
        except Exception: pass
        self.chrome_ac(); self.giris_kontrol(); self.projeye_git()
        partiler = sorted({s.get("parti", 1) for s in self.sahneler()})
        if self.args.get("parti"): partiler = [p for p in partiler if p in self.args["parti"]]
        asamalar = ["gorsel", "video"] if self.args.get("asama", "hepsi") == "hepsi" else [self.args["asama"]]
        self.log(f"BAŞLADI · film {self.film} · partiler {partiler} · aşama {asamalar}")
        self.bildir(f"Başladı: partiler {partiler}, aşama {'+'.join(asamalar)}")
        sonraki_mola = random.randint(*self.A["mola_kac_partide"])
        for i, p in enumerate(partiler, 1):
            for tur in asamalar: self.asama(tur, self.sahneler(p))
            self.bildir(f"Parti {p} bitti.")
            if i < len(partiler) and i % sonraki_mola == 0:
                dk = random.choice(self.A["mola_dk"]); self.log(f"MOLA: {dk} dakika")
                time.sleep(dk * 60); sonraki_mola = i + random.randint(*self.A["mola_kac_partide"])
                self.projeye_git()
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


def main():
    a = sys.argv[1:]
    if not a: print(__doc__); return
    if "--telegram-test" in a: telegram_test(); return
    root = a[0]; args = {"asama": "hepsi", "kurgu_yok": "--kurgu-yok" in a}
    for k in ("--asama", "--parti", "--sahne"):
        if k in a:
            v = a[a.index(k) + 1]
            args[k[2:]] = v if k == "--asama" else [int(x) for x in v.split(",")]
    m = Memmet(root, args)
    try:
        if "--giris" in a:
            m.chrome_ac(); m.giris_kontrol(); m.log("Giriş tamam. Bu pencereyi açık bırakabilir ya da kapatabilirsin."); return
        m.calis()
    except Durdur as e:
        m.bildir(f"DURDU: {e}", acil=True); sys.exit(2)
    except KeyboardInterrupt:
        m.log("Kullanıcı durdurdu.")
    except Exception:
        m.log("BEKLENMEYEN HATA:\n" + traceback.format_exc()); m.hata_kaydi("beklenmeyen")
        m.bildir("Beklenmeyen hata ile durdu. MEMMET_KAYIT.txt'ye bak.", acil=True); sys.exit(1)
    finally:
        m.kapat()


if __name__ == "__main__":
    main()
