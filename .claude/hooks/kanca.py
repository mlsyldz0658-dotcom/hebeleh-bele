"""KANCA — Claude Code kancalarının TEK dosyası (TASARIM §1.1, §4.2, §6.2, D-10, D-11, D-45; [CM2] §4.5.7–§4.5.10).

Kullanım (Claude Code çağırır; girdi stdin'de JSON, çıktı stdout'ta JSON):
  bash "$CLAUDE_PROJECT_DIR/.claude/bin/kanca.sh" <olay> [--kaynak ayar|beceri]
  python .claude/hooks/kanca.py <olay> < girdi.json
Olaylar (alt komutlar):
  erisim        PreToolUse Read|Glob|Grep|Write|Edit|NotebookEdit: gizli dosya (iki kök) reddi; alt ajan yalnız bağlı görev klasörü
                (rolüne göre), ileri bölüm reddi; sürüşte makine sahipli dosyaya yazma ve 200 KB üstü Read reddi.        KAPALI BAŞARISIZ
  komut         PreToolUse Bash|PowerShell: gizli dosya, robocopy /MIR, kalıcı silme (_gecici/ ve geçici klasör hariç),
                pyautogui/pynput/SendKeys/stealth/captcha/kie.ai; Flow kilidiyken Memmet; sürüşte doğrudan memmet.py, git push,
                git add -A, makine sahipli dosyaya kabuktan yazma; yerelde main/master'a push. `film.py basla` görünce
                KANCA NABZI yazar (<film>/_GOREV/KANCA_NABZI.json; film.py basla ≤ 15 sn'lik nabız ister).          KAPALI BAŞARISIZ
  ajan          PreToolUse Agent: sürüşte kadro dışı / fork / yerleşik ajan, name/isolation, `calisiyor` olmayan görev, paralel
                ≤ ajan_paralel_max reddi; görevi BAGLAR.json'a "bekleyen" yazar (ilk okumada agent_id bağlanır).          KAPALI BAŞARISIZ
  oturum_basi   SessionStart: "FİLM SETİ DURUMU" bağlamı (≤ 6.000 kr; ortam=bulut|yerel, D-45)                          açık başarısız
  istem         UserPromptSubmit: mesajı soru/not/konu/diğer sınıflar, bağlam ekler; "dur/durdur/bekle" → sürüş kapanır       açık
  ajan_basi     SubagentStart: iki sabit satır (İ-5)                                                                     açık
  ajan_bitti    SubagentStop: çıktı doğrulama, aşamalı bölüm geçişi (decision: block), kullanım kaydı → film.py bitir       açık (görev bitmez)
  ajan_sonrasi  PostToolUse Agent: görev durumu bilgisi; dönüş metni 600 kr'yi aşarsa uyarı                              açık
  stop          Stop: soru kapısı + devam kapısı (ardışık stop_ardisik_max, film_token_tavan)                            açık
  hata          StopFailure: çalışan bağları "kesildi" işaretler, kayıt                                                   açık
  ozet_sakla    PreCompact/PostCompact: özet anlık görüntüsü _GOREV/OZETLER/'e                                           açık
  model_degisti PostModelSwitch: model sapması kaydı (D-08)                                                              açık
Kapalı başarısızlık (D-11): güvenlik olaylarında beklenmeyen her hata → stderr + çıkış 2 (çağrı engellenir). Ağır içe aktarma yok
(subprocess yalnız gereken olayda, tembel). Gizli bilgi yazılmaz: kayıtta komut metni yok, yalnız kural adı ve dosya adı.
Sürüş = aktif film var ve FILM_DURUM.otomatik_surus.acik (film.py surus kapat --gelistirme ile geliştirme serbest).
"""
import os, sys, re, json, time, hashlib

GUVENLIK = ("erisim", "komut", "ajan")
BURASI = os.path.dirname(os.path.abspath(__file__))
DEPO = os.path.dirname(os.path.dirname(BURASI))
ARACLAR = os.path.join(DEPO, "YZ_FILM", "ARACLAR")
ERISIM_DOSYASI = os.path.join(DEPO, ".claude", "kurallar", "erisim.json")
AYAR_DOSYASI = os.path.join(DEPO, ".claude", "settings.json")
TEK_SORU = ("Filmin konusu ne olsun? Bir cümle yeter (ör. ejderha yavrusunu saklayan avcı kadın). "
            "İstersen 'sen seç' yaz.")
BULUT_CUMLESI = "Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz."
IKI_SATIR = "İlk işin GOREV.json'u okumak. Yalnız GIRDI/'yi oku, yalnız CIKTI/'ye yaz."
BAGLAM_MAX = 6000
ISTEM_BAGLAM_MAX = 1500
AJAN_DONUS_MAX = 600
BEKLEYEN_OMUR_SN = 2 * 3600
VARSAYILAN_ESIK = {"ajan_paralel_max": 5, "stop_ardisik_max": 8, "film_token_tavan": None}
MODEL_AILESI = "opus"


# ---- küçük yardımcılar ---------------------------------------------------------------------------------------------
def simdi(): return time.strftime("%Y-%m-%dT%H:%M:%S") + _tz()


def _tz():
    o = -time.timezone if not time.localtime().tm_isdst else -time.altzone
    return "%+03d:%02d" % (o // 3600, abs(o) % 3600 // 60)


def json_oku(yol, vars_=None):
    try:
        with open(yol, encoding="utf-8-sig") as f: return json.load(f)
    except (OSError, ValueError): return vars_


def atomik_yaz(yol, veri):
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    tmp = "%s.%d.tmp" % (yol, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f: json.dump(veri, f, ensure_ascii=False, indent=1)
    for d in range(5):
        try: os.replace(tmp, yol); return
        except PermissionError:
            if d == 4: raise
            time.sleep(0.05)


def sha1(yol):
    try:
        with open(yol, "rb") as f: return hashlib.sha1(f.read()).hexdigest()
    except OSError: return None


def cikti(veri):
    sys.stdout.write(json.dumps(veri, ensure_ascii=False)); sys.stdout.flush()


def reddet(olay, neden):
    """PreToolUse reddi (JSON). Neden düz Türkçe, kuralı söyler; sır içermez."""
    cikti({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                  "permissionDecisionReason": "[film seti kuralı] " + neden}})
    return 0


def baglam(olay_adi, metin, sinir=BAGLAM_MAX):
    if not metin: return 0
    if len(metin) > sinir: metin = metin[: sinir - 40] + "\n… (kısaltıldı; film.py ozet --uzun)"
    cikti({"hookSpecificOutput": {"hookEventName": olay_adi, "additionalContext": metin}})
    return 0


def engelle_karar(neden):
    cikti({"decision": "block", "reason": neden}); return 0


# ---- yollar ve durum ---------------------------------------------------------------------------------------------
_YOL = []


def yollar():
    """ortak.yollar() (tek yol kaynağı); YOLLAR.json yoksa {} (bulut geliştirme oturumu)."""
    if not _YOL:
        y = {}
        try:
            if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
            import ortak
            y = ortak.yollar()
        except Exception:
            y = {}
        _YOL.append(y)
    return _YOL[0]


def ortam():
    """yerel | bulut. YZ_FILM_ORTAM → FILM_AYAR.json "ortam" → CLAUDE_CODE_REMOTE → Windows ise yerel, değilse bulut (D-45)."""
    v = os.environ.get("YZ_FILM_ORTAM")
    if v in ("yerel", "bulut"): return v
    y = yollar()
    if y.get("ayarlar"):
        a = json_oku(os.path.join(y["ayarlar"], "FILM_AYAR.json"), {}) or {}
        if a.get("ortam") in ("yerel", "bulut"): return a["ortam"]
    if str(os.environ.get("CLAUDE_CODE_REMOTE", "")).lower() in ("1", "true", "yes"): return "bulut"
    return "yerel" if os.name == "nt" else "bulut"


def aktif_film():
    y = yollar()
    if not y.get("filmler"): return None
    a = json_oku(os.path.join(y["filmler"], "_AKTIF.json"), {}) or {}
    p = a.get("yol")
    return os.path.abspath(p) if p and os.path.isdir(p) else None


def film_coz(arg):
    if not arg: return aktif_film()
    if os.path.isdir(arg): return os.path.abspath(arg)
    y = yollar()
    if y.get("filmler") and os.path.isdir(os.path.join(y["filmler"], arg)): return os.path.join(y["filmler"], arg)
    return None


def film_durum(film): return json_oku(os.path.join(film, "FILM_DURUM.json"), {}) or {} if film else {}


def surus_acik(film=None):
    film = film or aktif_film()
    if not film: return False
    s = (film_durum(film).get("otomatik_surus") or {})
    return bool(s.get("acik", True))


def flow_kilitli():
    y = yollar()
    return bool(y.get("hesap")) and os.path.exists(os.path.join(y["hesap"], "FLOW_KILIDI.json"))


_ADLAR = []


def kadro():
    """ADLAR.json ajanlar → {ad: rol}."""
    if not _ADLAR:
        a = json_oku(os.path.join(ARACLAR, "veri", "ADLAR.json"), {}) or {}
        _ADLAR.append({k: (v or {}).get("rol") for k, v in (a.get("ajanlar") or {}).items() if not k.startswith("_")})
    return _ADLAR[0]


_ESIK = []


def esik(ad):
    if not _ESIK:
        e = json_oku(os.path.join(ARACLAR, "veri", "hat_esikleri.json"), {}) or {}
        d = {}
        for k, v in e.items():
            if isinstance(v, dict) and "deger" in v: d[k] = v["deger"]
        _ESIK.append(d)
    return _ESIK[0].get(ad, VARSAYILAN_ESIK.get(ad))


def kayit(film, **k):
    """Kanca kaydı (yalnız kural adı, araç, dosya adı; komut metni ve içerik YAZILMAZ)."""
    if not film: return
    try:
        p = os.path.join(film, "_GOREV", "KANCA_KAYIT.jsonl")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "a", encoding="utf-8") as f: f.write(json.dumps(dict(zaman=simdi(), **k), ensure_ascii=False) + "\n")
    except OSError:
        pass


# ---- yol desenleri -------------------------------------------------------------------------------------------------
def norm(p, cwd=None):
    """Karşılaştırma biçimi: mutlak, sembolik bağ çözülmüş, '/' ayraçlı, küçük harf (Windows büyük/küçük harf duyarsız)."""
    if not p: return ""
    s = str(p).replace("\\", "/")
    if not (os.path.isabs(s) or re.match(r"^[A-Za-z]:/", s)): s = os.path.join(cwd or os.getcwd(), s)
    try: s = os.path.realpath(s)
    except (OSError, ValueError): s = os.path.abspath(s)
    s = s.replace("\\", "/")
    if len(s) > 1: s = s.rstrip("/")
    return s.lower()


def ust_cikis_var(p): return bool(re.search(r"(^|[\\/])\.\.([\\/]|$)", str(p or "")))


_RE = {}


def desen_re(d):
    if d not in _RE:
        r, i = "", 0
        while i < len(d):
            if d.startswith("**/", i): r += "(?:.*/)?"; i += 3
            elif d.startswith("**", i): r += ".*"; i += 2
            elif d[i] == "*": r += "[^/]*"; i += 1
            elif d[i] == "?": r += "[^/]"; i += 1
            else: r += re.escape(d[i]); i += 1
        _RE[d] = re.compile("^" + r + "$")
    return _RE[d]


def yer_tutucu(d, gorev=None):
    """'{veri_kok}/AYARLAR/**' → normalleştirilmiş desen; değeri bilinmeyen yer tutucuda None."""
    y = yollar()
    deg = {"veri_kok": y.get("veri_kok"), "depo_kok": DEPO, "gorev": gorev}
    for k, v in deg.items():
        if "{%s}" % k in d:
            if not v: return None
            d = d.replace("{%s}" % k, norm(v))
    return d.replace("\\", "/").lower()


def eslesir(yol_n, desenler, gorev=None):
    for d in desenler or ():
        dd = yer_tutucu(d, gorev)
        if dd and desen_re(dd).match(yol_n): return d
    return None


_KURAL = []


def kurallar():
    if not _KURAL:
        k = json_oku(ERISIM_DOSYASI)
        if not isinstance(k, dict): raise RuntimeError("erisim.json okunamadı")
        _KURAL.append(k)
    return _KURAL[0]


def gizli_mi(yol_n):
    k = kurallar()
    return bool(eslesir(yol_n, k.get("gizli"))) and not eslesir(yol_n, k.get("gizli_istisna"))


def gizli_klasor_icerir(kok_n):
    """Arama kökü (Grep yolu) veri kökündeki AYARLAR'ı içeriyor ya da herhangi bir AYARLAR'ın içinde mi."""
    for d in kurallar().get("gizli_klasorler") or ():
        dd = yer_tutucu(d)
        if not dd: continue
        if kok_n == dd or kok_n.startswith(dd + "/"): return True               # AYARLAR'ın kendisi ya da içi
        if "{veri_kok}" in d and dd.startswith(kok_n.rstrip("/") + "/"): return True   # veri AYARLAR'ının üst klasörü
    return False


def makine_sahipli(yol_n): return bool(eslesir(yol_n, kurallar().get("makine_sahipli")))


def film_yolu_mu(yol_n): return bool(eslesir(yol_n, kurallar().get("film_yollari")))


# ---- görev bağları (BAGLAR.json) ---------------------------------------------------------------------------------
class BagKilidi:
    """BAGLAR.json için kısa kilit (paralel alt ajanların kancaları aynı anda yazabilir). 10 sn'den eski kilit bayattır."""
    def __init__(self, film): self.p = os.path.join(film, "_GOREV", "BAGLAR.kilit")

    def __enter__(self):
        os.makedirs(os.path.dirname(self.p), exist_ok=True)
        son = time.time() + 3
        while True:
            try:
                fd = os.open(self.p, os.O_CREAT | os.O_EXCL | os.O_WRONLY); os.write(fd, str(os.getpid()).encode()); os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - os.path.getmtime(self.p) > 10: os.replace(self.p, self.p + ".bayat"); continue
                except OSError: pass
                if time.time() > son: raise RuntimeError("BAGLAR kilidi alınamadı")
                time.sleep(0.02)

    def __exit__(self, *a):
        try: os.remove(self.p)
        except OSError: pass


def baglar_yolu(film): return os.path.join(film, "_GOREV", "BAGLAR.json")


def baglar_oku(film):
    b = json_oku(baglar_yolu(film), {}) or {}
    b.setdefault("bekleyen", []); b.setdefault("bagli", {}); b.setdefault("biten", {})
    return b


def gorev_dir(film, gid): return os.path.join(film, "_GOREV", gid)


def gorev_oku(film, gid): return json_oku(os.path.join(gorev_dir(film, gid), "GOREV.json"), {}) or {}


def bag_bul(agent_id, film=None):
    film = film or aktif_film()
    if not (film and agent_id): return film, None
    return film, baglar_oku(film)["bagli"].get(str(agent_id))


def bekleyenden_bagla(film, agent_id, agent_type, gorev_json_n=None):
    """İlk araç çağrısında agent_id'yi bekleyen göreve bağlar. gorev_json_n verilirse yalnız o görev; yoksa o türden TEK bekleyen."""
    with BagKilidi(film):
        b = baglar_oku(film); t = time.time()
        b["bekleyen"] = [x for x in b["bekleyen"] if t - x.get("t", 0) < BEKLEYEN_OMUR_SN]
        aday = [x for x in b["bekleyen"] if x.get("ajan") == agent_type]
        if gorev_json_n: aday = [x for x in aday if norm(x.get("gorev_json")) == gorev_json_n]
        elif len(aday) != 1: aday = []
        if not aday: return None
        x = aday[0]
        if any(v.get("gorev") == x["gorev"] for v in b["bagli"].values()): return None     # bağlı göreve ikinci ajan yok
        b["bekleyen"].remove(x)
        bag = {"gorev": x["gorev"], "ajan": agent_type, "rol": kadro().get(agent_type), "t": t, "zaman": simdi(), "duzeltme": {}}
        b["bagli"][str(agent_id)] = bag
        atomik_yaz(baglar_yolu(film), b)
        return bag


def bag_guncelle(film, agent_id, **alan):
    with BagKilidi(film):
        b = baglar_oku(film); bag = b["bagli"].get(str(agent_id))
        if bag is None: return None
        bag.update(alan)
        if alan.get("bitti"):
            b["biten"][str(agent_id)] = b["bagli"].pop(str(agent_id))
        atomik_yaz(baglar_yolu(film), b)
        return bag


# ---- erisim ------------------------------------------------------------------------------------------------------
def arac_yollari(arac, ti):
    """(okuma|yazma|arama, ham yol) listesi."""
    ti = ti or {}
    if arac in ("Read", "NotebookRead"): return [("okuma", ti.get("file_path") or ti.get("notebook_path"))]
    if arac in ("Write", "Edit", "MultiEdit"): return [("yazma", ti.get("file_path"))]
    if arac == "NotebookEdit": return [("yazma", ti.get("notebook_path") or ti.get("file_path"))]
    if arac == "Grep": return [("arama", ti.get("path") or "")]
    if arac == "Glob": return [("liste", ti.get("path") or "")]
    return []


def k_erisim(g):
    arac = g.get("tool_name") or ""; ti = g.get("tool_input") or {}; cwd = g.get("cwd") or os.getcwd()
    agent_id, agent_type = g.get("agent_id"), g.get("agent_type")
    yollar_ = arac_yollari(arac, ti)
    film = aktif_film()
    for tur, ham in yollar_:
        p = norm(ham or cwd, cwd)
        if tur in ("okuma", "yazma") and gizli_mi(p):
            kayit(film, olay="ret", kural="gizli", arac=arac, dosya=os.path.basename(p))
            return reddet("erisim", "AYARLAR ve anahtar dosyaları hiçbir kökte okunmaz/yazılmaz. Ayar gerekiyorsa: "
                                    "python .claude/bin/film.py goster ayar (maskeli).")
        if tur == "arama" and gizli_klasor_icerir(p):
            kayit(film, olay="ret", kural="gizli_arama", arac=arac)
            return reddet("erisim", "Bu arama AYARLAR klasörünü kapsıyor; anahtar dosyalarında arama yapılmaz. Daha dar bir klasör ver.")
    if agent_id:
        return erisim_alt_ajan(g, film, arac, yollar_, cwd, str(agent_id), agent_type)
    if surus_acik(film):
        for tur, ham in yollar_:
            p = norm(ham or cwd, cwd)
            if tur == "yazma" and makine_sahipli(p):
                kayit(film, olay="ret", kural="makine_sahipli", arac=arac, dosya=os.path.basename(p))
                return reddet("erisim", "Bu dosyayı yalnız film.py ve betikler yazar (makine sahipli). Sen içerik/rapor yazmazsın; "
                                        "python .claude/bin/film.py sonraki.")
            if tur == "okuma" and arac == "Read":
                sinir = (kurallar().get("ana_claude") or {}).get("okuma_buyuk_dosya_kb", 200) * 1024
                try: boy = os.path.getsize(ham if os.path.isabs(str(ham)) else os.path.join(cwd, str(ham)))
                except OSError: boy = 0
                if boy > sinir and not ti.get("limit"):
                    kayit(film, olay="ret", kural="buyuk_dosya", arac=arac, dosya=os.path.basename(p))
                    return reddet("erisim", "Büyük dosya açılmaz (%d KB üstü). Bilgi gerekiyorsa: python .claude/bin/film.py goster <ne>."
                                  % (sinir // 1024))
    return 0


def erisim_alt_ajan(g, film, arac, yollar_, cwd, agent_id, agent_type):
    rol_kadro = kadro().get(agent_type)
    bag = None
    if film: film, bag = bag_bul(agent_id, film)
    if bag is None and film and rol_kadro:
        hedef = None
        for tur, ham in yollar_:
            if tur == "okuma" and str(ham or "").replace("\\", "/").endswith("GOREV.json"): hedef = norm(ham, cwd)
        bag = bekleyenden_bagla(film, agent_id, agent_type, hedef) if hedef else None
        if bag is None:
            kayit(film, olay="ret", kural="bagsiz_ajan", arac=arac, ajan=agent_type)
            return reddet("erisim", "Önce görev dosyanı oku: istemindeki GOREV.json yolu. Başka dosya okunmaz.")
        kayit(film, olay="bag", ajan=agent_type, gorev=bag["gorev"])
    if bag is None:
        # Kadro dışı (yerleşik/iç) ajan: film dosyalarına erişemez (tanimsiz_agent_type: ret); geliştirme dosyaları serbest.
        for tur, ham in yollar_:
            p = norm(ham or cwd, cwd)
            if film_yolu_mu(p) or (tur in ("arama", "liste") and film and (p == norm(film) or norm(film).startswith(p + "/"))):
                kayit(film, olay="ret", kural="kadro_disi_ajan", arac=arac, ajan=agent_type)
                return reddet("erisim", "Kadro dışı ajan film dosyalarına erişemez.")
        return 0
    gdir = gorev_dir(film, bag["gorev"]); gd_n = norm(gdir)
    rol = (kurallar().get("roller") or {}).get(bag.get("rol") or "kor") or (kurallar()["roller"]["kor"])
    gv = gorev_oku(film, bag["gorev"]); asamali = gv.get("asamali") or {}
    for tur, ham in yollar_:
        if ust_cikis_var(ham):
            return reddet("erisim", "Yolda '..' kullanılmaz; yalnız görev klasörün.")
        p = norm(ham or cwd, cwd)
        if eslesir(p, kurallar().get("yasak_okuma_film_rolleri")):
            return reddet("erisim", "Tasarım ve araştırma belgeleri film rollerine kapalıdır.")
        if tur == "yazma":
            if not eslesir(p, rol.get("yazma"), gdir):
                kayit(film, olay="ret", kural="yazma_disari", ajan=agent_type, gorev=bag["gorev"], dosya=os.path.basename(p))
                return reddet("erisim", "Yalnız görev klasörünün CIKTI/ klasörüne yazarsın.")
            continue
        if tur in ("arama", "liste") and not (p == gd_n or p.startswith(gd_n + "/")):
            return reddet("erisim", "Arama yalnız görev klasöründe yapılır.")
        if tur == "okuma" and not eslesir(p, rol.get("okuma"), gdir):
            kayit(film, olay="ret", kural="okuma_disari", ajan=agent_type, gorev=bag["gorev"], dosya=os.path.basename(p))
            return reddet("erisim", "Yalnız kendi görev klasörünü okursun (GOREV.json, ISTEM.md, GIRDI/).")
        m = re.match(re.escape(gd_n) + r"/girdi/([^/]+)", p)
        if asamali and m:
            acik = [x.lower() for x in asamali.get("acik") or []]; tum = [x.lower() for x in asamali.get("bolumler") or []]
            if m.group(1) in tum and m.group(1) not in acik:
                kayit(film, olay="ret", kural="ileri_bolum", ajan=agent_type, gorev=bag["gorev"])
                return reddet("erisim", "Bu bölüm henüz açılmadı; ileriyi okuma. Sonraki bölümü sistem verir.")
    return 0


# ---- komut -------------------------------------------------------------------------------------------------------
AYIRAC = re.compile(r"\s*(?:&&|\|\||;|\||\n|\r)\s*")
SILME = {"rm", "rmdir", "del", "erase", "rd", "unlink", "shred", "remove-item", "ri", "srm", "wipe"}
OKUMA = {"cat", "head", "tail", "less", "more", "type", "get-content", "gc", "bat", "sed", "awk", "nl"}
LISTE = {"ls", "dir", "stat", "test", "[", "get-item", "get-childitem", "gci", "test-path", "find", "tree", "du", "wc"}
ARAMA = {"grep", "rg", "egrep", "fgrep", "findstr", "select-string", "sls", "ag", "ack"}
BOT = re.compile(r"pyautogui|pynput|send-?keys|sendinput|keybd_event|mouse_event|xdotool|autohotkey|\.ahk\b|wscript\.shell|"
                 r"undetected[_-]chromedriver|selenium[_-]stealth|puppeteer-extra-plugin-stealth|playwright[_-]stealth|"
                 r"2captcha|anti-?captcha|capsolver|captcha[_-]?solver|kie\.ai", re.I)
GIZLI_AD = re.compile(r"[\w.\-]*_anahtar\.txt|telegram_bot\.txt|(?<![\w.])\.env\b|memmet_profil|MEMMET_AYAR\.json", re.I)
AYARLAR_YOL = re.compile(r"[^\s\"'`|;&<>]*AYARLAR(?:[\\/][^\s\"'`|;&<>]*)?", re.I)
ISTISNA_AD = re.compile(r"(\.ornek\.json|OKU_BENI\.txt)$", re.I)
MAKINE_AD = re.compile(r"FILM_DURUM\.json|GOREV\.json|DEFTER\.jsonl|BAGLAR\.json|KANCA_NABZI\.json|SAHNELER\.json|"
                       r"DUNYA_DEFTERI\.json|KARAR_DEFTERI\.md|KURGU_PLANI[\w.]*\.json|[\\/]_RAPOR[\\/]|[\\/]KUYRUK[\\/]|[\\/]kararlar[\\/]", re.I)
YAZMA_KABUK = re.compile(r">>?|\btee\b|out-file|set-content|add-content|\bcp\b|\bmv\b|\bcopy\b|copy-item|move-item|"
                         r"open\([^)]*['\"][wa]", re.I)
MEMMET_KOS = re.compile(r"(?:^|[\s\"'(&;|])(?:[\w:\\/.\-]*[\\/])?(?:python[\d.]*|py|python[\d.]*\.exe|py\.exe)(?:\s+-[\w.]+)*\s+"
                        r"[\"']?(?:[^\s\"']*[\\/])?memmet\.py\b", re.I)


def kelimeler(seg):
    import shlex
    try:
        if "\\" in seg: t = [x.strip("\"'") for x in shlex.split(seg, posix=False)]   # Windows yolu: ters bölü kaçış değildir
        else: t = shlex.split(seg, posix=True)
    except ValueError: t = seg.split()
    while t and (re.match(r"^\w+=", t[0]) or t[0] in ("sudo", "(", "{", "then", "do", "!", "exec", "time", "nohup", "&")):
        t = t[1:]
    return t


def program(t):
    if not t: return ""
    p = t[0].replace("\\", "/").rsplit("/", 1)[-1].lower()
    return p[:-4] if p.endswith(".exe") else p


def silme_serbest(arg):
    a = arg.replace("\\", "/").lower()
    if "/_gecici/" in a or a.startswith("_gecici/") or a.rstrip("/").endswith("/_gecici") or a == "_gecici": return True
    if "__pycache__" in a or a.endswith((".pyc", ".tmp")): return True
    import tempfile
    for d in {tempfile.gettempdir(), "/tmp", os.environ.get("TMPDIR") or "", os.environ.get("TEMP") or ""}:
        dn = d.replace("\\", "/").lower().rstrip("/")
        if dn and (a == dn or a.startswith(dn + "/")) and ".." not in a: return True
    return False


def silme_kontrol(seg, t):
    p = program(t)
    if p in SILME:
        hedef = [x for x in t[1:] if not x.startswith("-") and not re.match(r"^/[a-z]$", x, re.I)]
        if not hedef or not all(silme_serbest(x) for x in hedef): return "kalıcı silme"
    if p == "find" and ("-delete" in t or ("-exec" in t and any(program([x]) in SILME for x in t))):
        kok = [x for x in t[1:] if not x.startswith("-")][:1]
        if not (kok and silme_serbest(kok[0])): return "kalıcı silme (find -delete)"
    if p == "git" and len(t) > 1:
        if t[1] == "clean" and any(x.startswith("-") and "f" in x for x in t[2:]): return "kalıcı silme (git clean -f)"
        if t[1] == "rm" and "--cached" not in t: return "kalıcı silme (git rm)"
    if p == "rsync" and any(x.startswith("--delete") for x in t): return "kalıcı silme (rsync --delete)"
    return None


def _gizli_ref(s):
    refs = [m.group(0) for m in AYARLAR_YOL.finditer(s)] + [m.group(0) for m in GIZLI_AD.finditer(s)]
    return [r for r in refs if not ISTISNA_AD.search(r)]


def gizli_komut(segler, cwd):
    """Gizli dosyaya dokunan segment var mı. Listeleme (ls/dir/Test-Path) serbest; grep'te ilk argüman desendir, yol sayılmaz;
    yolsuz özyinelemeli arama veri kökündeki AYARLAR'ı kapsıyorsa ret."""
    for seg in segler:
        t = kelimeler(seg); p = program(t)
        if p in ARAMA or (p == "git" and len(t) > 1 and t[1] == "grep"):
            arg = [x for x in t[1:] if not x.startswith("-")]
            if p == "git": arg = arg[1:]
            arg = arg[1:]                                                  # ilk argüman desendir (-e ile de)
            if any(_gizli_ref(x) for x in arg): return True
            if not arg and gizli_klasor_icerir(norm(cwd)): return True
            if any(gizli_klasor_icerir(norm(x, cwd)) for x in arg): return True
            continue
        if not _gizli_ref(seg): continue
        if p in LISTE and not re.search(r"-exec|-delete", seg): continue
        if p == "git" and re.match(r"\s*git\s+(status|check-ignore|ls-files|log|diff --stat)\b", seg): continue
        return True
    return False


def git_push(t):
    """git push segmenti → (push_mu, hedef_ana_dal_mi, zorla_mi)."""
    if program(t) != "git": return False, False, False
    i = 1
    while i < len(t) and t[i].startswith("-"):
        i += 2 if t[i] in ("-C", "-c") else 1
    if i >= len(t) or t[i] != "push": return False, False, False
    arg = t[i + 1:]
    ana = any(re.fullmatch(r"(\+?(?:[\w./-]*:)?(?:refs/heads/)?(main|master))", x) for x in arg if not x.startswith("-"))
    return True, ana, any(x in ("-f", "--force", "--force-with-lease") or x.startswith("+") for x in arg)


def k_komut(g, kaynak="ayar"):
    cmd = str((g.get("tool_input") or {}).get("command") or "")
    arac = g.get("tool_name") or "Bash"
    film = aktif_film()
    segler = [s for s in AYIRAC.split(cmd) if s.strip()]
    def ret(kural, neden):
        kayit(film, olay="ret", kural=kural, arac=arac)
        return reddet("komut", neden)
    if gizli_komut(segler, g.get("cwd") or os.getcwd()):
        return ret("gizli", "AYARLAR ve anahtar dosyaları okunmaz, kopyalanmaz, yazdırılmaz (yalnız varlığı denetlenir: ls/dir).")
    if re.search(r"\brobocopy\b[^\n|;&]*\s/(mir|purge)\b", cmd, re.I):
        return ret("robocopy_mir", "robocopy /MIR ve /PURGE yasak (kalıcı silme). Eskiler _ESKI/'ye taşınır.")
    if re.search(r"\bpy(?:thon[\d.]*)?(?:\.exe)?\b[^|&]*\s-c\b", cmd, re.I) and \
            re.search(r"shutil\.rmtree|os\.remove|os\.unlink|\.unlink\(|os\.rmdir|rmtree\(", cmd):
        return ret("silme", "Kalıcı silme yok (python -c ile silme). Eskiler _ESKI/'ye taşınır.")
    for seg in segler:
        t = kelimeler(seg)
        s = silme_kontrol(seg, t)
        if s: return ret("silme", "Kalıcı silme yok (%s). Eskiler _ESKI/'ye taşınır (mv/move); yalnız _gecici/ ve geçici klasör serbest." % s)
    bot = [s for s in segler if BOT.search(s) and not (program(kelimeler(s)) in ARAMA | OKUMA
                                                       or re.match(r"\s*git\s+(grep|log|diff|show)\b", s))]
    if bot:
        return ret("bot_taklidi", "Fare/klavye taklidi, gizlilik (stealth) eklentisi, captcha çözücü ve kie.ai kullanılmaz (Flow kuralı).")
    memmet = bool(MEMMET_KOS.search(cmd)) and not re.search(r"py_compile|-m\s+unittest", cmd)
    memmet_serbest = bool(re.search(r"--(giris|bakiye)\b", cmd))
    if memmet and flow_kilitli() and not memmet_serbest:
        return ret("flow_kilidi", "Flow kilidi var: gönderim yapılmaz (her kipte). Kilidi yalnız kullanıcı UYARI_GECTI.bat ile kaldırır.")
    surus = surus_acik(film)
    for seg in segler:
        t = kelimeler(seg)
        push, ana, zorla = git_push(t)
        if push and surus:
            return ret("git_push", "Film sürüşünde git push yok; eşitleme yalnız film.py esitle ile.")
        if push and ana and ortam() == "yerel":
            return ret("git_push_ana", "Yerelde ana dala push yok (D-12): film.py esitle --gelistirme ayrı dala gönderir.")
        if surus and program(t) == "git" and len(t) > 2 and t[1] == "add" and any(x in ("-A", "--all", ".") for x in t[2:]):
            return ret("git_add_hepsi", "Film sürüşünde git add -A yok.")
    if surus:
        if memmet and not memmet_serbest:
            return ret("memmet_dogrudan", "memmet.py doğrudan çalıştırılmaz; Flow işi yalnız film.py calis içinden yürür.")
        if MAKINE_AD.search(cmd) and YAZMA_KABUK.search(cmd) and not re.search(r"(^|[\s\"'])[\w:\\/.\-]*film\.py\b", cmd):
            return ret("makine_sahipli_kabuk", "Makine sahipli dosyaya kabuktan yazılmaz; yalnız film.py ve betikler yazar.")
    if re.search(r"film\.py\b", cmd):
        stop_sayac_sifirla(film)
        m = re.search(r"film\.py\s+basla\b", cmd)
        if m:
            fm = re.search(r"--film[ =][\"']?([^\"'\s]+)", cmd)
            nabiz_yaz(film_coz(fm.group(1)) if fm else film, g, kaynak)
    return 0


def fork_kapali():
    """CLAUDE_CODE_FORK_SUBAGENT=0: kanca sürecine geçtiyse ondan, geçmediyse settings.json'dan (§10.3 #6 yedeği)."""
    v = os.environ.get("CLAUDE_CODE_FORK_SUBAGENT")
    if v is not None: return str(v).strip() in ("0", "false", "False")
    for p in (AYAR_DOSYASI, os.path.join(DEPO, ".claude", "settings.local.json")):
        e = (json_oku(p, {}) or {}).get("env") or {}
        if "CLAUDE_CODE_FORK_SUBAGENT" in e: return str(e["CLAUDE_CODE_FORK_SUBAGENT"]).strip() in ("0", "false")
    return False


def nabiz_icerik(g, kaynak):
    return {"zaman": simdi(), "session_id": g.get("session_id"), "yazan": "kanca.komut", "kaynak": kaynak,
            "kanca_sha": {"kanca.py": sha1(os.path.abspath(__file__)), "erisim.json": sha1(ERISIM_DOSYASI)},
            "ayar_sha": {"settings.json": sha1(AYAR_DOSYASI)}, "fork_kapali": fork_kapali(),
            "env_kancada": os.environ.get("CLAUDE_CODE_FORK_SUBAGENT") is not None,
            "claude_surum": os.environ.get("CLAUDE_CODE_VERSION"), "ortam": ortam()}


def nabiz_yaz(film, g, kaynak):
    """KANCA_NABZI.json (§4.5.8). Fork kapalı değilse nabız YAZILMAZ: ajan görevi başlamaz (D-10)."""
    if not film: return
    n = nabiz_icerik(g, kaynak)
    if not n["fork_kapali"]:
        kayit(film, olay="nabiz_yok", neden="CLAUDE_CODE_FORK_SUBAGENT=0 değil"); return
    atomik_yaz(os.path.join(film, "_GOREV", "KANCA_NABZI.json"), n)


# ---- ajan --------------------------------------------------------------------------------------------------------
GOREV_YOLU = re.compile(r"((?:[A-Za-z]:)?[^\s\"'`<>|]*_GOREV[\\/]([A-Za-z0-9][\w.\-]*)[\\/]GOREV\.json)")


def k_ajan(g):
    ti = g.get("tool_input") or {}
    tip = ti.get("subagent_type") or ""
    istem = str(ti.get("prompt") or "")
    film = aktif_film()
    m = GOREV_YOLU.search(istem)
    surus = surus_acik(film)
    if not (surus or m): return 0                                        # sürüş kapalı ve film görevi değil: geliştirme serbest
    def ret(kural, neden):
        kayit(film, olay="ret", kural=kural, ajan=tip)
        return reddet("ajan", neden)
    yasak = set(kurallar().get("yerlesik_ajanlar_yasak") or ())
    if not tip or tip in yasak or tip.lower() == "fork":
        return ret("yerlesik_ajan", "Film sürüşünde fork ve yerleşik ajan yok; yalnız görevdeki ajan tipi (subagent_type=<ajan>).")
    if tip not in kadro():
        return ret("kadro_disi", "Kadro dışı ajan: %s. Yalnız film.py sonraki'nin verdiği ajan tipi." % tip)
    if ti.get("name") or ti.get("isolation") or ti.get("team_name"):
        return ret("parametre", "Agent çağrısında name/isolation verilmez; yalnız subagent_type ve istem AYNEN.")
    if not m:
        return ret("gorevsiz", "İstemde görev yolu yok. film.py sonraki'nin istemini AYNEN ver.")
    gid = m.group(2); gfilm = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(m.group(1)))))
    if not os.path.isfile(os.path.join(gfilm, "_GOREV", gid, "GOREV.json")): gfilm = film
    gv = gorev_oku(gfilm, gid) if gfilm else {}
    if not gv: return ret("gorev_yok", "Görev bulunamadı: %s." % gid)
    if gv.get("durum") != "calisiyor":
        return ret("calismiyor", "Görev %s 'calisiyor' değil (%s). Önce: python .claude/bin/film.py basla %s." % (gid, gv.get("durum"), gid))
    if gv.get("ajan") != tip:
        return ret("tip_uyusmaz", "Bu görevin ajanı %s; %s değil." % (gv.get("ajan"), tip))
    with BagKilidi(gfilm):
        b = baglar_oku(gfilm); t = time.time()
        b["bekleyen"] = [x for x in b["bekleyen"] if t - x.get("t", 0) < BEKLEYEN_OMUR_SN and x.get("gorev") != gid]
        if any(v.get("gorev") == gid for v in b["bagli"].values()):
            return ret("bagli", "Bu görev zaten bir ajana bağlı; ikinci ajan açılmaz.")
        calisan = len(b["bagli"]) + len(b["bekleyen"])
        if calisan >= int(esik("ajan_paralel_max") or 5):
            return ret("paralel", "Aynı anda en çok %s ajan; önce çalışanların bitmesini bekle." % esik("ajan_paralel_max"))
        b["bekleyen"].append({"gorev": gid, "ajan": tip, "gorev_json": os.path.join(gfilm, "_GOREV", gid, "GOREV.json"),
                              "t": t, "zaman": simdi(), "arka_plan": bool(ti.get("run_in_background"))})
        atomik_yaz(baglar_yolu(gfilm), b)
    return 0


# ---- oturum başı ---------------------------------------------------------------------------------------------------
KURAL_OZETI = ("KURALLAR: yalnız konu sorulur (tek cümle) · fiziksel iş dışında soru yok, kararı ekip verir (film.py karar ekle) · "
               "Flow uyarısı/doğrulama → her kipte dur, başka hesap yok · AYARLAR okunmaz · içerik/puan/rapor yazmazsın · "
               "ajan: görevdeki tip, istem AYNEN, name/fork yok · büyük dosya yok (film.py goster) · film.py'ye güven · "
               "soru → film-durum, not → film-not · memmet.py/sağlayıcı doğrudan yok · kalıcı silme, robocopy /MIR, git push yok · "
               "çıkış 2/4/5/6/7/8 → film.py'nin cümlesi, tur biter.")


def film_py(*arg, zaman_asimi=20):
    """film.py alt süreci (tembel subprocess). (kod, json|None)."""
    import subprocess
    try:
        r = subprocess.run([sys.executable, os.path.join(ARACLAR, "film.py")] + list(arg), capture_output=True,
                           timeout=zaman_asimi, env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    except Exception:
        return None, None
    try: return r.returncode, json.loads(r.stdout.decode("utf-8", "replace") or "null")
    except ValueError: return r.returncode, None


def o0a_var():
    y = yollar(); v = y.get("veri_kok")
    return any(os.path.isfile(p) for p in ([os.path.join(v, "O0a.json"), os.path.join(v, "OLCUM0", "O0a.json")] if v else []))


def k_oturum_basi(g):
    orm = ortam(); kaynak = g.get("source") or "startup"
    bas = "[FİLM SETİ DURUMU · %s] ortam=%s · olay=%s" % (time.strftime("%d.%m.%Y %H:%M"), orm, kaynak)
    s = [bas]
    y = yollar()
    if not y:
        s.append("YOLLAR.json yok (kurulum yapılmamış ya da bulut geliştirme oturumu).")
    cwd = norm(g.get("cwd") or os.getcwd())
    if y.get("veri_kok") and cwd == norm(y["veri_kok"]):
        s.append("UYARI: Claude veri klasöründe açıldı. Kullanıcıya yalnız şunu söyle: 'Masaüstündeki FILM_SETI.bat'a çift tıkla; "
                 "Claude doğru klasörde açılır.' Başka bir şey yapma.")
        return baglam("SessionStart", "\n".join(s))
    film = aktif_film()
    if film is None:
        if orm == "bulut":
            s.append("Aktif film yok. BULUT (D-45): konu SORMA, film başlatma. Kullanıcı konu verse de yalnız şunu söyle: \"%s\" "
                     "Bulutta film-yap yalnız --saglayici sahte ile ORNEK_* denemesi koşar; geliştirme /film-gelistir ile." % BULUT_CUMLESI)
        else:
            s.append("Aktif film yok. Konu verildiyse film-yap ile başla; verilmediyse YALNIZ şunu sor: '%s'" % TEK_SORU)
            if y and not o0a_var():
                s.append("Bu bilgisayarda O0a.json yok: kullanıcı 'ilk kurulum' yazarsa YZ_FILM/ARACLAR/CLAUDE.md §İlk yerel oturum.")
        return baglam("SessionStart", "\n".join(s))
    kod, oz = film_py("ozet", "--json", "--film", film)
    oz = oz or {}
    s.append("Aktif film: %s" % (oz.get("film") or os.path.basename(film)))
    if oz.get("ozet"): s.append(str(oz["ozet"]))
    st = film_durum(film)
    sur = st.get("otomatik_surus") or {}
    s.append("Sürüş: %s%s" % ("açık" if sur.get("acik", True) else "kapalı", (" (%s)" % sur["neden"]) if sur.get("neden") else ""))
    if st.get("bekleyen_kullanici"): s.append("Bekleyen kullanıcı işi: " + ", ".join(st["bekleyen_kullanici"][:5]))
    s.append("Flow kilidi: " + ("VAR — gönderim yok, kullanıcı UYARI_GECTI.bat" if flow_kilitli() else "yok"))
    n = json_oku(os.path.join(film, "_GOREV", "KANCA_NABZI.json"), {}) or {}
    s.append("Kanca nabzı: " + (("son %s" % n["zaman"]) if n.get("zaman") else "yok (ilk film.py basla'da yazılır)"))
    if orm == "bulut": s.append("BULUT (D-45): yalnız --saglayici sahte denemesi; gerçek üretim kullanıcının bilgisayarında.")
    s.append("Sıradaki: python .claude/bin/film.py sonraki")
    s.append(KURAL_OZETI)
    s.append("Döngü: film-yap becerisi. Hafızana değil film.py'ye güven.")
    return baglam("SessionStart", "\n".join(s))


# ---- istem (kullanıcı mesajı sınıflaması) ----------------------------------------------------------------------------
def _kucuk(s):
    return (s or "").replace("I", "ı").replace("İ", "i").lower().strip()


DUR = re.compile(r"(?:^|[\s,.!])(dur|durdur|dursun|bekle|beklet|stop|pause|durdurun)(?=$|[\s,.!])")
RICA = re.compile(r"\w+(?:[ıiuü]r|[ae]r|[ae]bil[ıi]r)\s+m[ıiuü]s[ıiuü]n(?:[ıiuü]z)?(?=$|[\s?.,!])|(?:^|\s)(?:can|could|would) you\b")
SORU_EKI = re.compile(r"(?:^|\s)m[ıiuü](?:s[ıiuü]n(?:[ıiuü]z)?|y[ıiuü]m|y[ıiuü]z|d[ıiuü]r|yd[ıiuü])?(?=$|[\s?.,!])")
SORU_SOZ = re.compile(r"(?:^|\s)(neden|niye|niçin|nasıl|nasil|kaç|kac|kaçta|hangi|hangisi|nerede|nereye|nereden|kim|kimin|"
                      r"ne zaman|ne kadar|ne durumda|ne oldu|ne yapıyor|ne yapıyorsun|nedir|ne\b(?=.*\?)|"
                      r"what|why|how|when|where|which|who|status)(?=$|[\s?.,!'’])")
NOT_SOZ = re.compile(r"(?:^|\s)(beğenme\w*|begenme\w*|olmamış|olmamis|olmadı|kopuk\w*|kaym\w*|kaydı|bozu\w*|yanlış\w*|hatal\w*|"
                     r"sıkıc\w*|sıkıl\w*|kısalt\w*|uzat\w*|değiştir\w*|degistir\w*|düzelt\w*|duzelt\w*|notlar\w*|notum\w*|"
                     r"şikay\w*|şikây\w*|berbat|kötü\w*|garip|tuhaf|çıkar\w*|cikar\w*|ekle\w*|kes|kesil\w*|sil|"
                     r"capcut'?\w*|kontrol et|ses\w* (?:\w+ )?(?:kaym|bozuk|kötü|yüksek|alçak|kısık)\w*|çok (?:uzun|kısa|hızlı|yavaş)|"
                     r"hoşuma gitme\w*|istemiyorum|didn'?t like|too long|too short|out of sync)(?=$|[\s?.,!'’])")
KONU_SOZ = re.compile(r"(film yap|film çek|bir film|filmi yap|yeni film|konu:|konusu:|hakkında (?:bir )?film|üzerine (?:bir )?film|"
                      r"şu konuda|sen seç|sen sec|make a movie|make a film|film about|movie about|story about|hikayesi)")
DEVAM_SOZ = re.compile(r"(?:^|\s)(devam\w*|kaldığın yerden|continue|go on|tamam|tamamdır|oldu|bitti|hallettim|yaptım|"
                       r"koydum|gönderdim|yükledim|aktardım|dışa aktardım|kapattım|açıldı|takıldı|taktım)(?=$|[\s?.,!])")


def sinifla(mesaj, onceki_konu_sorusu=False):
    """Kullanıcı mesajı → {sinif: soru|not|konu|diger, alt: dur|devam|ilk_kurulum|rica|None}. 50 mesajlık sette sınanır."""
    m = _kucuk(mesaj)
    if not m: return {"sinif": "diger", "alt": None}
    kelime = m.split()
    if DUR.search(m) and (len(kelime) <= 4 or re.match(r"^(dur|durdur|bekle|stop)\b", m)):
        return {"sinif": "diger", "alt": "dur"}
    if re.search(r"\bilk kurulum\b", m): return {"sinif": "diger", "alt": "ilk_kurulum"}
    rica = bool(RICA.search(m))
    soru = (m.rstrip().endswith("?") or bool(SORU_EKI.search(m)) or bool(SORU_SOZ.search(m))) and not rica
    if soru:
        if KONU_SOZ.search(m) and not SORU_SOZ.search(m): return {"sinif": "konu", "alt": None}   # "… film yapalım mı?"
        return {"sinif": "soru", "alt": None}
    if NOT_SOZ.search(m) or rica:
        if KONU_SOZ.search(m) and not re.search(r"capcut|sahne|ses|kurgu|taslak|animatik", m):
            return {"sinif": "konu", "alt": None}
        return {"sinif": "not", "alt": "rica" if rica else None}
    if KONU_SOZ.search(m): return {"sinif": "konu", "alt": None}
    if DEVAM_SOZ.search(m) and len(kelime) <= 8: return {"sinif": "diger", "alt": "devam"}
    if onceki_konu_sorusu and len(kelime) >= 2: return {"sinif": "konu", "alt": None}
    return {"sinif": "diger", "alt": None}


def son_asistan_metni(g, sinir_bayt=262144):
    """Son asistan mesajının metni: girdi alanı (last_assistant_message) ya da döküm dosyasının sonu."""
    for k in ("last_assistant_message", "last_message"):
        if isinstance(g.get(k), str): return g[k]
    p = g.get("transcript_path")
    if not p or not os.path.isfile(p): return ""
    try:
        with open(p, "rb") as f:
            f.seek(0, 2); n = f.tell(); f.seek(max(0, n - sinir_bayt)); satirlar = f.read().decode("utf-8", "replace").splitlines()
    except OSError:
        return ""
    for sat in reversed(satirlar):
        try: o = json.loads(sat)
        except ValueError: continue
        msg = o.get("message") or {}
        if (o.get("type") or msg.get("role")) != "assistant": continue
        c = msg.get("content")
        if isinstance(c, str): return c
        metin = [x.get("text", "") for x in c or [] if isinstance(x, dict) and x.get("type") == "text"]
        if metin: return "\n".join(metin)
    return ""


def k_istem(g):
    mesaj = str(g.get("prompt") or "")
    film = aktif_film(); orm = ortam()
    onceki = TEK_SORU[:30] in son_asistan_metni(g)
    s = sinifla(mesaj, onceki)
    sat = []
    if s["alt"] == "dur":
        if film:
            film_py("surus", "kapat", "--film", film, "--json")
            kayit(film, olay="surus_kapat", neden="kullanici_dur")
            sat.append("Kullanıcı DURDUR dedi: otomatik sürüş kapandı. Yeni iş başlatma; kısa bilgi ver (ne durdu, devam için 'devam' yazması yeter).")
        return baglam("UserPromptSubmit", "\n".join(sat), ISTEM_BAGLAM_MAX)
    if film is None:
        if s["sinif"] == "konu":
            if orm == "bulut":
                sat.append("BULUT (D-45): konu sorulmaz, film başlatılmaz. Yalnız şunu söyle: \"%s\"" % BULUT_CUMLESI)
            else:
                sat.append("Konu verildi: soru sormadan film-yap ile başla (konu kullanıcının cümlesi; belirsizlikte varsayım).")
        return baglam("UserPromptSubmit", "\n".join(sat), ISTEM_BAGLAM_MAX)
    st = film_durum(film); sur = st.get("otomatik_surus") or {}
    if not sur.get("acik", True) and sur.get("neden") in ("soru", "kullanici") and s["sinif"] != "soru" and \
            (s["alt"] == "devam" or s["sinif"] in ("konu", "not")):
        film_py("surus", "ac", "--film", film, "--json")
    sat.append("[film: %s · aşama %s%s]" % (st.get("film") or os.path.basename(film), st.get("aktif_asama") or "?",
                                           " · bekleyen kullanıcı işi: " + ", ".join(st["bekleyen_kullanici"][:3])
                                           if st.get("bekleyen_kullanici") else ""))
    if s["sinif"] == "soru":
        sat.append("Bu mesaj SORU: yalnız cevap ver (film-durum). İşlem yapma, dosya değiştirme, ajan açma.")
    elif s["sinif"] == "not":
        sat.append("Bu mesaj NOT/şikâyet ya da düzenleme: film-not (notu salt okunur işle, görevlere çevir; soru sorma).")
    elif s["sinif"] == "konu":
        sat.append("Aktif film var; yeni konu notu olarak işlenir (film-not) ya da kullanıcı yeni film istiyorsa film-yap kararı ekip verir.")
    else:
        sat.append("Döngü: python .claude/bin/film.py sonraki (film-yap). Soru sorma.")
    return baglam("UserPromptSubmit", "\n".join(sat), ISTEM_BAGLAM_MAX)


# ---- alt ajan başı / bitişi / sonrası ----------------------------------------------------------------------------------
def k_ajan_basi(g):
    tip = g.get("agent_type") or ""
    if tip not in kadro(): return 0
    film = aktif_film()
    if film and g.get("agent_id"):
        try: bekleyenden_bagla(film, str(g["agent_id"]), tip)
        except Exception: pass
    return baglam("SubagentStart", IKI_SATIR)


def kullanim_oku(p):
    """Alt ajan dökümünden kullanım (D-08). Yoksa karakter/3 tahmini."""
    k = {"girdi": 0, "cikti": 0, "onbellek_okuma": 0, "model": None}
    if not p or not os.path.isfile(p): return None
    ilk = son = None; n = 0
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            for sat in f:
                n += len(sat)
                try: o = json.loads(sat)
                except ValueError: continue
                z = o.get("timestamp")
                if z: ilk = ilk or z; son = z
                msg = o.get("message") or {}
                u = msg.get("usage") or {}
                if u:
                    k["girdi"] += int(u.get("input_tokens") or 0); k["cikti"] += int(u.get("output_tokens") or 0)
                    k["onbellek_okuma"] += int(u.get("cache_read_input_tokens") or 0)
                if msg.get("model"): k["model"] = msg["model"]
    except OSError:
        return None
    if not (k["girdi"] or k["cikti"]): k.update(girdi=n // 3, tahmin=True)
    try:
        import datetime
        f = lambda s: datetime.datetime.fromisoformat(str(s).replace("Z", "+00:00")).timestamp()
        if ilk and son: k["sure_sn"] = round(f(son) - f(ilk), 1)
    except (ValueError, TypeError):
        pass
    if not k["model"]: k.pop("model")
    return k


def cikti_eksik(gdir, gv):
    eksik = []
    for c in (gv.get("cikti") or {}).get("zorunlu", []) + (gv.get("cikti") or {}).get("son", []):
        p = os.path.join(gdir, c)
        if not os.path.exists(p): eksik.append(c)
        elif p.endswith(".json") and json_oku(p) is None: eksik.append(c + " (bozuk JSON)")
    return eksik


def k_ajan_bitti(g):
    agent_id = g.get("agent_id"); tip = g.get("agent_type") or ""
    film = aktif_film()
    if not (film and agent_id): return 0
    film, bag = bag_bul(str(agent_id), film)
    if bag is None and tip in kadro():
        bag = bekleyenden_bagla(film, str(agent_id), tip)
    if bag is None: return 0                                              # bağsız (iç/kadro dışı) ajan: yok sayılır
    gid = bag["gorev"]; gdir = gorev_dir(film, gid); gv = gorev_oku(film, gid)
    if gv.get("durum") != "calisiyor":
        bag_guncelle(film, agent_id, bitti=True, sonuc=gv.get("durum")); return 0
    tavan = 2
    asamali = gv.get("asamali") or {}
    if asamali.get("bolumler"):
        son = asamali["acik"][-1] if asamali.get("acik") else asamali["bolumler"][0]
        rap = "CIKTI/rapor_%s.md" % son
        if not os.path.isfile(os.path.join(gdir, rap)):
            return duzeltme(film, agent_id, bag, son, tavan, "%s bölümünün raporunu yaz: %s. Sonraki bölümü sistem verir." % (son, rap))
        if len(asamali.get("acik") or []) < len(asamali["bolumler"]):
            kod, r = film_py("asama-ilerlet", gid, "--film", film, "--json", zaman_asimi=60)
            if kod == 0 and r and r.get("bolum"):
                kayit(film, olay="bolum_acildi", gorev=gid, bolum=r["bolum"])
                return engelle_karar("Yeni bölüm GIRDI/%s/'de. Önceki bölümlere dönme, ileriyi tahmin etme. %s'i oku ve "
                                     "CIKTI/rapor_%s.md'yi yaz; bitince dur." % (r["bolum"], r["bolum"], r["bolum"]))
    eksik = cikti_eksik(gdir, gv)
    if eksik:
        return duzeltme(film, agent_id, bag, "son", tavan, "Çıktı eksik: %s. Yalnız CIKTI/'ye yaz, sonra dur." % ", ".join(eksik))
    kul = kullanim_oku(g.get("agent_transcript_path"))
    arg = ["bitir", gid, "--film", film, "--json"] + (["--kullanim", json.dumps(kul)] if kul else [])
    kod, r = film_py(*arg, zaman_asimi=90)
    if kod != 0:
        ek = ", ".join((r or {}).get("eksik") or []) if isinstance(r, dict) else ""
        return duzeltme(film, agent_id, bag, "bitir", tavan, "Doğrulama geçmedi%s. CIKTI/'yi düzelt, sonra dur." % (": " + ek if ek else ""))
    bag_guncelle(film, agent_id, bitti=True, sonuc=(r or {}).get("durum", "bitti"))
    kayit(film, olay="ajan_bitti", gorev=gid, durum=(r or {}).get("durum"))
    return 0


def duzeltme(film, agent_id, bag, anahtar, tavan, neden):
    """SubagentStop düzeltmesi (bölüm başına ≤ 2); sonra durmaya izin verilir, görev doğrulamasız BİTMEZ (gecersiz adayı)."""
    d = dict(bag.get("duzeltme") or {}); n = d.get(anahtar, 0)
    if n >= tavan:
        bag_guncelle(film, agent_id, bitti=True, sonuc="gecersiz_aday")
        kayit(film, olay="dogrulama_tukendi", gorev=bag["gorev"], bolum=anahtar)
        return 0
    d[anahtar] = n + 1; bag_guncelle(film, agent_id, duzeltme=d)
    kayit(film, olay="duzeltme", gorev=bag["gorev"], bolum=anahtar, kez=n + 1)
    return engelle_karar(neden)


def k_ajan_sonrasi(g):
    film = aktif_film()
    if not film: return 0
    yanit = g.get("tool_response")
    metin = yanit if isinstance(yanit, str) else json.dumps(yanit, ensure_ascii=False) if yanit is not None else ""
    ti = g.get("tool_input") or {}
    m = GOREV_YOLU.search(str(ti.get("prompt") or ""))
    if not m: return 0
    gv = gorev_oku(film, m.group(2)); sat = []
    if gv.get("durum") == "bitti": sat.append("Görev %s bitti. Sıradaki: python .claude/bin/film.py sonraki" % m.group(2))
    elif gv.get("durum") == "calisiyor": sat.append("Görev %s çalışıyor (arka planda olabilir); bildirim gelince film.py sonraki." % m.group(2))
    else: sat.append("Görev %s durumu: %s. python .claude/bin/film.py sonraki" % (m.group(2), gv.get("durum")))
    if len(metin) > AJAN_DONUS_MAX:
        sat.append("Not: ajan dönüş metni %d kr (sınır %d); içerik ana bağlama alınmaz, dosyalar doğrudur." % (len(metin), AJAN_DONUS_MAX))
    return baglam("PostToolUse", "\n".join(sat))


# ---- stop -----------------------------------------------------------------------------------------------------------
KARAR_SORUSU = re.compile(r"hangisini|hangisi(?:ni)? (?:istersin|tercih)|onaylıyor musun|onaylar mısın|ister misin|istiyor musun|"
                          r"devam edeyim mi|devam edelim mi|başlayayım mı|yapayım mı|uygun mu|olur mu\?|tercih(?:in)?(?: eder)? misin|"
                          r"\b\w+ mı(?:yı)? \w+ mı(?:yı)?\b.*\?|which one|should i\b|do you want|would you like|shall i\b|"
                          r"\bmi yoksa\b|\bmı yoksa\b", re.I)
SORU_BEYAZ = re.compile(r"istersen (?:'sen seç'|itiraz)|itiraz edersen yaz|GECE_IZNI\.bat|IZINLER\.bat|UYARI_GECTI\.bat", re.I)


def soru_kapisi_ihlali(metin):
    if not metin: return False
    t = metin.replace(TEK_SORU, " ").replace(BULUT_CUMLESI, " ")
    t = SORU_BEYAZ.sub(" ", t)
    return bool(KARAR_SORUSU.search(t))


def stop_yolu(film): return os.path.join(film, "_GOREV", "KANCA_STOP.json")


def stop_sayac_sifirla(film):
    if not film: return
    p = stop_yolu(film)
    if (json_oku(p, {}) or {}).get("ardisik"): atomik_yaz(p, {"ardisik": 0, "zaman": simdi()})


def k_stop(g):
    film = aktif_film(); metin = son_asistan_metni(g)
    if film is None:
        if ortam() == "bulut" and TEK_SORU[:30] in metin and len(metin) < 400:
            return engelle_karar("Bulutta (D-45) konu sorulmaz. Yalnız şu bilgi cümlesini söyle: \"%s\"" % BULUT_CUMLESI)
        return 0
    if not surus_acik(film): return 0
    st = film_durum(film)
    p = stop_yolu(film); s = json_oku(p, {}) or {}; n = int(s.get("ardisik") or 0)
    if n >= int(esik("stop_ardisik_max") or 8):
        kayit(film, olay="stop_tavan", ardisik=n); atomik_yaz(p, {"ardisik": 0, "zaman": simdi()}); return 0
    tavan = esik("film_token_tavan")
    tok = ((st.get("harcama") or {}).get("token") or {})
    if tavan and (int(tok.get("girdi") or 0) + int(tok.get("cikti") or 0)) >= tavan:
        kayit(film, olay="token_tavani"); return 0
    neden = None
    if soru_kapisi_ihlali(metin):
        neden = "Ekip karar verir; kullanıcıya karar sorusu sorma. Kararı yaz: python .claude/bin/film.py karar ekle \"karar — neden — " \
                "yanlışsa maliyeti\" ve döngüye devam et (film.py sonraki)."
    elif not g.get("background_tasks") and not calisan_ajan_var(film):
        kod, oz = film_py("ozet", "--json", "--film", film)
        if (oz or {}).get("tur") in ("ajan", "betik", "hazirlaniyor"):
            neden = "Sıradaki görev hazır: python .claude/bin/film.py sonraki (kullanıcıya soru sorma)."
    if not neden: return 0
    atomik_yaz(p, {"ardisik": n + 1, "zaman": simdi()})
    kayit(film, olay="stop_devam", ardisik=n + 1)
    return engelle_karar(neden)


def calisan_ajan_var(film):
    b = baglar_oku(film)
    return bool(b["bagli"] or b["bekleyen"])


# ---- hata, özet, model -------------------------------------------------------------------------------------------------
def k_hata(g):
    film = aktif_film()
    if not film: return 0
    with BagKilidi(film):
        b = baglar_oku(film)
        for k, v in list(b["bagli"].items()): v["sonuc"] = "kesildi"; b["biten"][k] = b["bagli"].pop(k)
        b["bekleyen"] = []
        atomik_yaz(baglar_yolu(film), b)
    kayit(film, olay="durma_hatasi", hata=str(g.get("error") or g.get("error_type") or "")[:120])
    return 0


def k_ozet_sakla(g):
    film = aktif_film()
    if not film: return 0
    olay = g.get("hook_event_name") or "Compact"
    d = os.path.join(film, "_GOREV", "OZETLER"); os.makedirs(d, exist_ok=True)
    kod, oz = film_py("ozet", "--json", "--film", film)
    kayit_ = {"zaman": simdi(), "olay": olay, "tetik": g.get("trigger"), "ozet": (oz or {}).get("ozet")}
    for k in ("summary", "compact_summary"):
        if isinstance(g.get(k), str): kayit_["sikistirma_ozeti"] = g[k][:20000]
    atomik_yaz(os.path.join(d, time.strftime("%Y%m%d_%H%M%S") + "_" + olay + ".json"), kayit_)
    return 0


def k_model_degisti(g):
    film = aktif_film()
    eski, yeni = g.get("from_model") or g.get("previous_model"), g.get("to_model") or g.get("model")
    kayit(film, olay="model_degisti", eski=eski, yeni=yeni)
    if yeni and MODEL_AILESI not in str(yeni).lower():
        kayit(film, olay="model_sapmasi", model=yeni)
        return baglam("PostModelSwitch", "Model %s: ajan görevleri opus bekler (D-09); sapmalı görevler yeniden kuyruğa girer." % yeni)
    return 0


OLAYLAR = {"erisim": k_erisim, "komut": k_komut, "ajan": k_ajan, "oturum_basi": k_oturum_basi, "istem": k_istem,
           "ajan_basi": k_ajan_basi, "ajan_bitti": k_ajan_bitti, "ajan_sonrasi": k_ajan_sonrasi, "stop": k_stop, "hata": k_hata,
           "ozet_sakla": k_ozet_sakla, "model_degisti": k_model_degisti}


def girdi_oku():
    ham = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode("utf-8")
    if not ham.strip(): return {}
    g = json.loads(ham.decode("utf-8-sig", "replace"))
    if not isinstance(g, dict): raise ValueError("kanca girdisi nesne değil")
    return g


def main(argv):
    olay = argv[0] if argv else ""
    kaynak = argv[argv.index("--kaynak") + 1] if "--kaynak" in argv and argv.index("--kaynak") + 1 < len(argv) else "ayar"
    try:
        if olay not in OLAYLAR: raise ValueError("bilinmeyen kanca olayı: %r" % olay)
        g = girdi_oku()
        f = OLAYLAR[olay]
        return f(g, kaynak) if olay == "komut" else f(g)
    except BaseException as e:                                          # D-11: kendi içinde kapalı başarısız
        if isinstance(e, SystemExit) and e.code in (0, None): return 0
        if olay in GUVENLIK or olay not in OLAYLAR:
            sys.stderr.write("[film seti kancası] %s doğrulanamadı (%s); işlem güvenlik için engellendi. "
                             "KURTARMA.md §Kanca.\n" % (olay or "?", type(e).__name__))
            return 2
        return 0                                                         # bilgi kancaları açık başarısız


if __name__ == "__main__":
    try: sys.stdout.reconfigure(encoding="utf-8", errors="replace"); sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception: pass
    sys.exit(main(sys.argv[1:]))
