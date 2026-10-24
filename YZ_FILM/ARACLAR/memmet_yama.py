"""MEMMET YAMA — memmet.py'ye önerilen yamanın korkuluk denetimi (TASARIM §6.1; memmet-bakimci onarımı, UM2 §4.3.3).

Kullanım:
  python memmet_yama.py <yama.diff> [--hedef <memmet.py>] [--test-yok] [--json]
        yamayı (birleşik diff, yalnız memmet.py) GEÇİCİ bir kopyada uygular; depodaki dosyaya dokunmaz. GEÇ ise 0, KAL ise 1.
Korkuluklar (hepsi birden; biri tutmazsa KAL):
  1. yama ≤ 80 satır (eklenen + silinen) ve yalnız memmet.py'ye dokunur
  2. eklenen satırlarda pyautogui / pynput / SendKeys / page.reload / stealth / undetected / captcha çözücü yok
  3. tempo yalnız yavaşlar: TEMPO aralıkları eleman eleman küçülmez, ayni_anda büyümez, mola sıklığı seyrekleşmez (0 = kapalı kalır),
     yeni kip eklenmez ("gündüz otomatik" yok); MEMMET_AYAR yalnız yavaşlatır (sikilastir/_yavas çağrısı kalır)
  4. uyarı kelimeleri yalnız büyür (OLAGANDISI_KELIMELERI, DOGRULAMA_KELIMELERI ⊇ eski); HATA_KELIMELERI'nde "olağan/unusual" yok
  5. yeniden deneme ve sayfa yenileme artmaz: goto / reload çağrıları, kuyruk.append/insert ve range(N) deneme sayıları büyümez
  6. uyarıdan sonra HER KİPTE sayfa işlemi 0: test_memmet_korkuluk (T10 elle, gece, doğrulama, v2 blok) yamalı kopyada yeniden koşar
  7. --mod varsayılanı elle; CIKIS olagandisi = 7, dogrulama = 2
  8. FLOW_TEMPO okuması kalır (flow_yuk.tempo_durumu, tempo_bekle(tur) çağrıları azalmaz)
Kodda: import memmet_yama; memmet_yama.denetle(diff_metni) → {"sonuc": "GEC"|"KAL", "maddeler": [...]}
Çıkış kodları: 0 GEÇ · 1 KAL · 4 kullanım ya da yama uygulanamadı.
"""
import os, sys, re, ast, json, shutil, subprocess, tempfile
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
SURUM = "memmet_yama 1.0"
SATIR_MAX = 80
YASAK = [r"pyautogui", r"pynput", r"sendkeys", r"\.reload\s*\(", r"stealth", r"undetected", r"2captcha", r"anticaptcha", r"capsolver",
         r"captcha.*(coz|çöz|solve)", r"solve.*captcha"]
UYARI_KOK = ("olağan", "olagan", "unusual")
T10_SECIM = ("T10", "dogrulama", "oturum", "uyari", "atlatma", "gece_izinsiz", "v2_sahneler", "kilitliyken", "zaman_asimi", "filtre",
             "dur_dosyasi", "bloksuz", "topla", "gunduz", "ikinci_memmet")


class YamaHatasi(Exception): pass


# ---------------------------------------------------------------- birleşik diff uygulayıcı
def parcala(diff):
    """[(eski_dosya, yeni_dosya, [(eski_bas, satirlar)])]."""
    dosyalar, cur, hunk = [], None, None
    for s in diff.splitlines():
        if s.startswith("--- "): cur = [s[4:].split("\t")[0].strip(), None, []]; dosyalar.append(cur); continue
        if s.startswith("+++ ") and cur is not None: cur[1] = s[4:].split("\t")[0].strip(); continue
        m = re.match(r"@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@", s)
        if m:
            if cur is None: cur = ["memmet.py", "memmet.py", []]; dosyalar.append(cur)
            hunk = (int(m.group(1)), []); cur[2].append(hunk); continue
        if hunk is not None and s[:1] in (" ", "+", "-"): hunk[1].append(s)
        elif hunk is not None and s.startswith("\\"): continue
    return dosyalar


def uygula(metin, hunklar):
    L = metin.split("\n"); out, i = [], 0
    for bas, satirlar in hunklar:
        bas = max(bas - 1, 0)
        if bas < i: raise YamaHatasi("parçalar sırasız")
        out += L[i:bas]; i = bas
        for s in satirlar:
            k, v = s[:1], s[1:]
            if k in (" ", "-"):
                if i >= len(L) or L[i] != v: raise YamaHatasi(f"bağlam tutmuyor (satır {i + 1}): {v[:60]!r}")
                if k == " ": out.append(v)
                i += 1
            else: out.append(v)
    return "\n".join(out + L[i:])


# ---------------------------------------------------------------- kaynak ölçüleri
def _sabit(agac, ad):
    for n in agac.body:
        if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == ad for t in n.targets):
            try: return ast.literal_eval(n.value)
            except ValueError: return None
    return None


def _cagri_say(agac, ad):
    return sum(1 for n in ast.walk(agac) if isinstance(n, ast.Call) and
               ((isinstance(n.func, ast.Attribute) and n.func.attr == ad) or (isinstance(n.func, ast.Name) and n.func.id == ad)))


def _kuyruk_say(agac):
    return sum(1 for n in ast.walk(agac) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("append", "insert")
               and isinstance(n.func.value, ast.Name) and n.func.value.id == "kuyruk")


def _range_toplam(agac):
    t = 0
    for n in ast.walk(agac):
        if isinstance(n, ast.For) and isinstance(n.iter, ast.Call) and isinstance(n.iter.func, ast.Name) and n.iter.func.id == "range":
            a = n.iter.args
            if len(a) == 1 and isinstance(a[0], ast.Constant) and isinstance(a[0].value, int): t += a[0].value
    return t


def olcu(kaynak):
    agac = ast.parse(kaynak)
    return {"TEMPO": _sabit(agac, "TEMPO") or {}, "OLAGANDISI": _sabit(agac, "OLAGANDISI_KELIMELERI") or [],
            "DOGRULAMA": _sabit(agac, "DOGRULAMA_KELIMELERI") or [], "HATA": _sabit(agac, "HATA_KELIMELERI") or [],
            "CIKIS": _sabit(agac, "CIKIS") or {}, "goto": _cagri_say(agac, "goto"), "reload": _cagri_say(agac, "reload"),
            "kuyruk": _kuyruk_say(agac), "range": _range_toplam(agac), "tempo_durumu": kaynak.count("flow_yuk.tempo_durumu("),
            "tempo_bekle_tur": kaynak.count("self.tempo_bekle(tur)"), "sikilastir": _cagri_say(agac, "sikilastir"),
            "mod_varsayilan": len(re.findall(r'["\']mod["\']\s*:\s*["\']elle["\']', kaynak)) + len(re.findall(r'get\(\s*["\']mod["\']\s*,\s*["\']elle["\']\s*\)', kaynak))}


def tempo_denetle(eski, yeni):
    h = []
    if set(yeni) - set(eski): h.append(f"yeni kip eklendi: {sorted(set(yeni) - set(eski))}")
    for kip, e in eski.items():
        y = yeni.get(kip)
        if y is None: h.append(f"kip silindi: {kip}"); continue
        for k, v in e.items():
            if k not in y: h.append(f"{kip}.{k} silindi"); continue
            n = y[k]
            if isinstance(v, list):
                if not (isinstance(n, list) and len(n) == len(v) and all(a >= b for a, b in zip(n, v))): h.append(f"{kip}.{k} hızlandı: {v} → {n}")
            elif k == "ayni_anda":
                if not (isinstance(n, int) and n <= v): h.append(f"{kip}.ayni_anda arttı: {v} → {n}")
            elif k.startswith("mola_kac"):
                if v == 0 and n != 0: h.append(f"{kip}.{k}: kapalı mola sayacı değişti ({n})")
                elif v > 0 and not (isinstance(n, int) and 0 < n <= v): h.append(f"{kip}.{k} seyrekleşti: {v} → {n}")
    return h


def denetle(diff, hedef=None, test=True):
    hedef = hedef or os.path.join(HERE, "memmet.py")
    md = []
    def m(ad, ok, ayrinti=None): md.append({"madde": ad, "sonuc": "GEC" if ok else "KAL", "ayrinti": ayrinti})
    dosyalar = parcala(diff)
    if not dosyalar: raise YamaHatasi("yamada parça yok")
    adlar = {os.path.basename(re.sub(r"^[ab]/", "", d[1] or d[0] or "")) for d in dosyalar}
    eklenen = [s[1:] for d in dosyalar for _, h in d[2] for s in h if s.startswith("+")]
    silinen = [s[1:] for d in dosyalar for _, h in d[2] for s in h if s.startswith("-")]
    m("boyut", len(eklenen) + len(silinen) <= SATIR_MAX and adlar == {"memmet.py"},
      {"satir": len(eklenen) + len(silinen), "dosyalar": sorted(adlar)})
    yasak = [s for s in eklenen if any(re.search(p, s, re.I) for p in YASAK)]
    m("yasak_cagri", not yasak, yasak[:5] or None)
    eski_k = open(hedef, encoding="utf-8").read()
    yeni_k = eski_k
    for d in dosyalar: yeni_k = uygula(yeni_k, d[2])
    try: E, Y = olcu(eski_k), olcu(yeni_k)
    except SyntaxError as e: m("sozdizimi", False, str(e)); return {"sonuc": "KAL", "maddeler": md}
    th = tempo_denetle(E["TEMPO"], Y["TEMPO"]); m("tempo_yalniz_yavaslar", not th and Y["sikilastir"] >= E["sikilastir"], th or None)
    eks = sorted(set(E["OLAGANDISI"]) - set(Y["OLAGANDISI"])) + sorted(set(E["DOGRULAMA"]) - set(Y["DOGRULAMA"]))
    hk = [k for k in Y["HATA"] if any(u in str(k).lower() for u in UYARI_KOK)]
    m("uyari_kelimeleri_buyur", not eks and not hk, {"silinen": eks, "hata_listesinde_uyari": hk} if eks or hk else None)
    art = {k: (E[k], Y[k]) for k in ("goto", "reload", "kuyruk", "range") if Y[k] > E[k]}
    m("yeniden_deneme_artmaz", not art, art or None)
    m("mod_varsayilan_elle", Y["mod_varsayilan"] >= max(1, E["mod_varsayilan"]) and Y["CIKIS"].get("olagandisi") == 7
      and Y["CIKIS"].get("dogrulama") == 2, {"cikis": {k: Y["CIKIS"].get(k) for k in ("olagandisi", "dogrulama")}})
    m("flow_tempo_okunur", Y["tempo_durumu"] >= max(1, E["tempo_durumu"]) and Y["tempo_bekle_tur"] >= E["tempo_bekle_tur"],
      {"tempo_durumu": Y["tempo_durumu"], "tempo_bekle_tur": Y["tempo_bekle_tur"]})
    if test: m("T10_her_kipte", *t10_kos(yeni_k))
    return {"sonuc": "GEC" if all(x["sonuc"] == "GEC" for x in md) else "KAL", "maddeler": md, "arac": SURUM}


def t10_kos(yeni_kaynak):
    """Yamalı memmet.py'yi geçici depo kopyasında test_memmet_korkuluk ile koşar. (geçti, özet)."""
    depo = os.path.dirname(os.path.dirname(HERE))
    d = tempfile.mkdtemp(prefix="memmet_yama_")
    try:
        hedef = os.path.join(d, "YZ_FILM", "ARACLAR")
        shutil.copytree(HERE, hedef, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "memmet_profil"))
        re_kaynak = os.path.join(depo, ".claude", "skills", "film-yap", "ritim_esikleri.json")
        if os.path.exists(re_kaynak):
            os.makedirs(os.path.join(d, ".claude", "skills", "film-yap"), exist_ok=True)
            shutil.copyfile(re_kaynak, os.path.join(d, ".claude", "skills", "film-yap", "ritim_esikleri.json"))
        with open(os.path.join(hedef, "memmet.py"), "w", encoding="utf-8") as f: f.write(yeni_kaynak)
        env = {k: v for k, v in os.environ.items() if k not in ("YZ_FILM_YOLLAR", "YZ_FILM_VERI")}
        env["MEMMET_YAMA_IC"] = "1"                 # iç koşuda yama testinin kendisi yeniden koşmaz (özyineleme yok)
        sec = [x for k in T10_SECIM for x in ("-k", k)]           # davranış korkulukları (sabit değer testleri değil: yama tempoyu yavaşlatabilir)
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", os.path.join(hedef, "testler"), "-p", "test_memmet_korkuluk.py"] + sec,
                           capture_output=True, text=True, cwd=os.path.join(d, "YZ_FILM"), env=env, timeout=600)
        son = (r.stderr or "").strip().splitlines()[-3:]
        return r.returncode == 0, " | ".join(son)
    finally: shutil.rmtree(d, ignore_errors=True)


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    yol = argv[0]
    if not os.path.isfile(yol): print("yama dosyası yok"); return 4
    hedef = argv[argv.index("--hedef") + 1] if "--hedef" in argv else None
    try: r = denetle(open(yol, encoding="utf-8").read(), hedef, test="--test-yok" not in argv)
    except YamaHatasi as e: print("Yama uygulanamadı:", e); return 4
    if "--json" in argv: print(json.dumps(r, ensure_ascii=False, indent=1))
    else:
        for x in r["maddeler"]: print(f"{x['sonuc']:4} {x['madde']}" + (f"  {x['ayrinti']}" if x["sonuc"] != "GEC" and x["ayrinti"] else ""))
        print("SONUÇ:", r["sonuc"])
    return 0 if r["sonuc"] == "GEC" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
