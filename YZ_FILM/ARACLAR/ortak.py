"""ORTAK — araçların paylaştığı küçük yardımcılar.

  yollar()             tek yol kaynağı: <depo>/YZ_FILM/AYARLAR/YOLLAR.json (kurulum.py --yollar yazar; git'e girmez).
                       Dosya yoksa açık hata (YolYok: "önce KURULUM.bat"). YZ_FILM_YOLLAR ortam değişkeni başka bir dosyayı
                       gösterebilir (testler); YZ_FILM_VERI yalnız veri kökünü değiştirir (veri kökü sarmalayıcısı).
                       Türetilmiş anahtarlar: ayarlar, filmler, hesap (hepsi veri kökü altında), araclar (depo).
                       hesap (Flow kilidi, tempo, günlük sayılar: Google hesabına bağlı) HER ZAMAN YOLLAR.json'daki veri kökünden
                       türer; YZ_FILM_VERI onu taşıyamaz (taşınsaydı aynı hesap için kilit ve molalar sıfırlanırdı).
  yollar_yaz(...)      YOLLAR.json'u soru sormadan yazar (varsayılan veri kökü: Masaüstü/YZ_FILM)
  sahneler_oku(kok)    SAHNELER.json'u okur; "_surum" ≥ 2 ise v1 araç onu işlemez, 4 ile çıkar ("Memmet v2 gerekli")
  atomik_yaz(yol, v)   JSON'u önce .tmp'ye yazıp yerine koyar (yarım dosya kalmaz; Windows'ta kilitliyse 3 kez dener)
  json_oku(yol, vars)  yoksa ya da bozuksa varsayılanı döndürür
  claude_yolu()        Claude Code'un GERÇEK çalıştırılabiliri (Windows'ta claude.exe; npm'in claude.cmd'si cmd.exe'den geçer)
  claude_komutu(argv, istem)  alt süreç için (komut listesi, stdin metni): kullanıcı/istem metni hiçbir zaman argv'de cmd.exe'ye gitmez
"""
import os, sys, json, time, re, shutil

SURUM_CIKIS = 4   # ortam/sürüm uyuşmazlığı: bu araç bu dosyayı işleyemez
ARACLAR = os.path.dirname(os.path.abspath(__file__))
DEPO_YZ = os.path.dirname(ARACLAR)                     # <depo>/YZ_FILM
DEPO_KOK = os.path.dirname(DEPO_YZ)


class YolYok(Exception):
    """YOLLAR.json yok ya da bozuk: araç hangi klasörle çalışacağını bilmiyor."""


def yollar_dosyasi(): return os.environ.get("YZ_FILM_YOLLAR") or os.path.join(DEPO_YZ, "AYARLAR", "YOLLAR.json")


def varsayilan_yollar(veri=None):
    ev = os.path.expanduser("~"); masa = os.path.join(ev, "Desktop")
    veri = os.path.abspath(veri or os.path.join(masa, "YZ_FILM"))
    win = os.name == "nt"
    return {
        "_surum": 1, "depo_kok": DEPO_KOK, "veri_kok": veri, "evren_kok": os.path.join(veri, "EVREN"),
        "arsiv": r"D:\YZ_FILM_ARSIV" if win else os.path.join(veri, "_ARSIV"),
        "yedek": r"D:\YZ_FILM_YEDEK" if win else os.path.join(veri, "_YEDEK"),
        "gelistirme": os.path.join(veri, "GELISTIRME"),
        "gemini_paket": os.path.join(masa, "GEMINI GORSEL ISTEM"),
        "capcut_taslak": os.path.join(os.environ.get("LOCALAPPDATA", os.path.join(ev, "AppData", "Local")),
                                      "CapCut", "User Data", "Projects", "com.lveditor.draft"),
        "ses_kutuphanesi": os.path.join(veri, "SES_KUTUPHANESI"),
        "onbellek": r"C:\YZ_FILM_ONBELLEK" if win else os.path.join(ev, ".cache", "yz_film"),
        "python": {"ana": sys.executable, "py312": None, "py311": None},
        "ortamlar": {"ses_donustur": None, "musetalk": None, "acestep": None, "buyutme": None},
    }


def yollar_yaz(veri=None, yol=None):
    """YOLLAR.json'u yazar. Var olan dosyadaki elle verilmiş değerler (python sürümleri, ortamlar) korunur."""
    yol = yol or yollar_dosyasi()
    y = varsayilan_yollar(veri); eski = json_oku(yol, {}) or {}
    for k in ("python", "ortamlar"):
        for a, v in (eski.get(k) or {}).items():
            if v and not y[k].get(a): y[k][a] = v
    if veri is None and eski.get("veri_kok"): y["veri_kok"] = eski["veri_kok"]
    atomik_yaz(yol, y)
    return y


def yollar():
    y = json_oku(yollar_dosyasi())
    if not isinstance(y, dict) or not y.get("veri_kok"):
        raise YolYok(f"YOLLAR.json yok ya da bozuk ({yollar_dosyasi()}). Önce KURULUM.bat'ı çalıştır "
                     "(ya da: python kurulum.py --yollar).")
    y = dict(y)
    hesap = os.path.join(y["veri_kok"], "HESAP")           # hesap düzeyi durum: ortam değişkeniyle taşınmaz
    if os.environ.get("YZ_FILM_VERI"): y["veri_kok"] = os.environ["YZ_FILM_VERI"]
    v = y["veri_kok"]
    y.update(ayarlar=os.path.join(v, "AYARLAR"), filmler=os.path.join(v, "FILMLER"), hesap=hesap, araclar=ARACLAR)
    return y


def sahneler_oku(kok, arac="bu araç"):
    p = os.path.join(kok, "SAHNELER.json")
    with open(p, encoding="utf-8-sig") as f: plan = json.load(f)
    if isinstance(plan, dict) and int(plan.get("_surum", 1) or 1) >= 2:
        print(f"!! SAHNELER.json sürüm {plan['_surum']} (v2). {arac} v1 dosyası bekliyor; işlem yapılmadı. "
              "Memmet v2 / film.py v2 gerekli.", flush=True)
        sys.exit(SURUM_CIKIS)
    return plan


def atomik_yaz(yol, veri):
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1); f.flush(); os.fsync(f.fileno())
    for deneme in range(3):
        try: os.replace(tmp, yol); return
        except PermissionError:
            if deneme == 2: raise
            time.sleep(0.2)


def pid_yasiyor(pid):
    """Süreç yaşıyor mu (bayat kilit kararı). Windows'ta os.kill süreci öldürür: OpenProcess + GetExitCodeProcess kullanılır.
    Ölçülemezse yaşıyor sayılır (kilit yalnız yaşla kalkar)."""
    if os.name != "nt":
        try: os.kill(pid, 0); return True
        except ProcessLookupError: return False
        except OSError: return True
    try:
        import ctypes
        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        h = k32.OpenProcess(0x1000, False, int(pid))                 # PROCESS_QUERY_LIMITED_INFORMATION
        if not h: return ctypes.get_last_error() == 5                  # ERROR_ACCESS_DENIED: süreç var; 87: süreç yok
        try:
            kod = ctypes.c_ulong(0)
            if not k32.GetExitCodeProcess(h, ctypes.byref(kod)): return True
            return kod.value == 259                                    # STILL_ACTIVE
        finally: k32.CloseHandle(h)
    except Exception: return True


def json_oku(yol, varsayilan=None):
    try:
        with open(yol, encoding="utf-8-sig") as f: return json.load(f)
    except (OSError, ValueError): return varsayilan


# ---- Claude Code alt süreci (Ö0-a #19: Windows'ta claude.CMD + istemdeki <…> = cmd.exe yönlendirmesi) -------------------------------
CLAUDE_NPM_EXE = os.path.join("node_modules", "@anthropic-ai", "claude-code", "bin", "claude.exe")
_KABUK_UZANTI = (".cmd", ".bat")
_CMD_HEDEF = re.compile(r'%~?dp0%?[\\/]*([^"%\r\n*]+?\.exe)\b', re.I)


def claude_kabuktan_mi(yol):
    """Bu yol cmd.exe'den geçen bir sarmalayıcı mı (.cmd/.bat)? Öyleyse argv'deki metin cmd.exe'de yorumlanır."""
    return bool(yol) and str(yol).lower().endswith(_KABUK_UZANTI)


def claude_yolu(which=None, nt=None, dosya_var=None, oku=None):
    """Claude Code'un GERÇEK çalıştırılabiliri; bulunamazsa None. Windows sırası: PATH'te .exe → npm sarmalayıcısının (claude.cmd)
    yanındaki node_modules\\@anthropic-ai\\claude-code\\bin\\claude.exe → sarmalayıcının içinde adı geçen .exe (node.exe değil) →
    PATH'te claude.exe, %USERPROFILE%\\.local\\bin\\claude.exe (yerel kurucu) → son çare sarmalayıcının kendisi (claude_kabuktan_mi True:
    çağıran istem metnini argv'de VERMEZ, claude_komutu stdin'den verir). which/nt/dosya_var/oku testler içindir."""
    which = which or shutil.which; nt = (os.name == "nt") if nt is None else nt
    dosya_var = dosya_var or os.path.isfile
    def oku_(p):
        try:
            with open(p, encoding="utf-8", errors="replace") as f: return f.read(20000)
        except OSError: return ""
    oku = oku or oku_
    w = which("claude")
    if not nt: return w
    import ntpath as P                                   # Windows yolu (testler Linux'ta da Windows biçimiyle sınar)
    if w and str(w).lower().endswith(".exe"): return w
    adaylar = []
    if w:
        d = P.dirname(w)
        adaylar.append(P.join(d, CLAUDE_NPM_EXE.replace("/", "\\")))
        if claude_kabuktan_mi(w):
            for m in _CMD_HEDEF.finditer(oku(w)):
                g = m.group(1).replace("/", "\\")
                if P.basename(g).lower() != "node.exe": adaylar.append(P.join(d, g))
    e = which("claude.exe")
    if e: adaylar.append(e)
    ev = os.environ.get("USERPROFILE") or os.path.expanduser("~")
    adaylar.append(P.join(ev, ".local", "bin", "claude.exe"))
    for a in adaylar:
        if a and dosya_var(a): return a
    return w


def claude_komutu(argv, istem=None, yol=None):
    """(komut listesi, stdin metni) ya da yol yoksa (None, None). İstem/kullanıcı metni HER ZAMAN stdin'den gider (claude -p istemi
    stdin'den okur): .exe'de de .cmd'de de argv'de yalnız sabit bayraklar kalır; cmd.exe hiçbir kullanıcı metnini yorumlayamaz.
    Liste biçimi (shell=False) zorunlu; kabuk dizesi kurulmaz."""
    yol = yol or claude_yolu()
    if not yol: return None, None
    return [yol] + [str(x) for x in argv], istem

