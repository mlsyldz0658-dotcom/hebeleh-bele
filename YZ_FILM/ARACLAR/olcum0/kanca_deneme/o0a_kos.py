"""KOS — Ö0-a koşucusu: deneme kancalarını GEÇİCİ kurar, 20 davranışı tek tek sınatır, O0a.json'u yazar, ayarı HER ZAMAN geri alır
(TASARIM §1.2 Ö0-a, §10.3, §4.5 `olcum0-a`, D-11; YZ_FILM/ARACLAR/CLAUDE.md §İlk yerel oturum adım 4).

Kullanım (depo kökünden; Python mutlak yolla):
  python YZ_FILM/ARACLAR/olcum0/kanca_deneme/o0a_kos.py kur [--saat 8]   geçici settings.local.json + o0a-sonda ajanı ve becerisi
  … o0a_kos.py sira                   sıradaki davranış ve yönergesi (önerilen sıra; bitenler atlanır)
  … o0a_kos.py adim <no>              o davranışın yönergesi; gerekiyorsa sonda kipini açar (SubagentStop/Stop engelleme) ve hazırlık yapar
  … o0a_kos.py degerlendir <no>       sonda kayıtlarından karar; elle bilgi gerekiyorsa ne gerektiğini söyler
  … o0a_kos.py kaydet <no> [--sonuc calisiyor|calismiyor] [--yedek "…"] [--not "…"] [--alan ad=değer …]
  … o0a_kos.py otomatik               canlı oturum gerektirmeyenler: #8 kanca süresi, #19 başsız claude -p (abonelik; kredi yok)
  … o0a_kos.py durum                  20 maddenin durumu
  … o0a_kos.py bitir                  O0a.json'u yazar (ölçülmeyen madde "çalışmıyor + yedek") ve GERİ ALIR (try/finally)
  … o0a_kos.py geri_al                yalnız geri alma (çökme sonrası; tekrar koşmak zararsız)
Seçenekler: --depo <depo kökü> (vars. bu dosyanın deposu) · --kayit <klasör> (vars. <veri>/BILGI/OLCUM0/O0a_deneme) · --python <mutlak yol>.
Geri alma güvenceleri: (1) kur içinde hata → geri_al; (2) bitir try/finally; (3) DENEME_DURUMU.json son_gecerlilik dolunca her o0a_kos.py çağrısı ve
SessionStart sondası geri alır; (4) asıl .claude/settings.json'a HİÇ yazılmaz (sha önce/sonra denetlenir; nabız bu yüzden bozulmaz).
Hiçbir şey silinmez: kurulan geçici dosyalar <kayit>/_ESKI/<zaman>/ altına taşınır; önceki settings.local.json <kayit>/yedek/'ten geri kopyalanır.
Anahtar dosyaları ve AYARLAR okunmaz. Kurulum varken `unittest` koşulursa test_adlar geçici ajan/beceri yüzünden kalır: önce bitir.
Çıkış kodları: 0 tamam · 1 değerlendirme için elle bilgi gerekli · 2 durum hatası (kurulu değil / zaten kurulu) · 4 kullanım.
"""
import os, sys, json, time, shutil, hashlib, random, string, tempfile, subprocess
BURASI = os.path.dirname(os.path.abspath(__file__)); OLCUM0 = os.path.dirname(BURASI); ARACLAR = os.path.dirname(OLCUM0)
for _p in (ARACLAR, OLCUM0, BURASI):
    if _p not in sys.path: sys.path.insert(0, _p)
import o0a_davranislar as DV

SURUM = "kanca_deneme 1.0"
SONDA = os.path.join(BURASI, "o0a_sonda.py")
SABLON = os.path.join(BURASI, "settings.local.sablon.json")
AJAN_SABLON = os.path.join(BURASI, "ajan.sablon.md")
BECERI_SABLON = os.path.join(BURASI, "beceri.sablon.md")
VARSAYILAN_SAAT = 8
PAKET_DOSYA, PAKET_SATIR, PAKET_KOD = 8, 1000, 3            # 8 × ≈ 100 KB ≈ 0,2 M token (4 kr/token tahmini)


def log(*a): print(*a, flush=True)
def ileri(p): return str(p).replace("\\", "/")
def simdi(): return time.strftime("%Y-%m-%dT%H:%M:%S")


def sha(p):
    if not os.path.isfile(p): return None
    h = hashlib.sha1()
    with open(p, "rb") as f: h.update(f.read())
    return h.hexdigest()


def json_oku(p, v=None):
    try:
        with open(p, encoding="utf-8-sig") as f: return json.load(f)
    except (OSError, ValueError): return v


def json_yaz(p, v):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(v, f, ensure_ascii=False, indent=1); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, p)


def _metin_oku(p):
    with open(p, encoding="utf-8", errors="replace") as f: return f.read()


def metin_yaz(p, m):
    os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
    tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f: f.write(m)
    os.replace(tmp, p)


# --- yollar ----------------------------------------------------------------------------------------------------------
def varsayilan_depo(): return os.path.dirname(os.path.dirname(ARACLAR))


def varsayilan_kayit():
    import ortak
    return os.path.join(ortak.yollar()["veri_kok"], "BILGI", "OLCUM0", "O0a_deneme")


def varsayilan_python():
    try:
        import ortak
        p = (ortak.yollar().get("python") or {}).get("ana")
        if p and os.path.isfile(p): return p
    except Exception:
        pass
    return sys.executable


class Yer:
    """Bir denemenin yolları (testler geçici .claude kopyasıyla kurar)."""
    def __init__(self, depo=None, kayit=None, python=None):
        self.depo = os.path.abspath(depo or varsayilan_depo())
        self.kayit = os.path.abspath(kayit or varsayilan_kayit())
        self.python = python or varsayilan_python()
        c = os.path.join(self.depo, ".claude")
        self.ayar = os.path.join(c, "settings.json"); self.yerel = os.path.join(c, "settings.local.json")
        self.ajan = os.path.join(c, "agents", "o0a-sonda.md"); self.beceri = os.path.join(c, "skills", "o0a-sonda", "SKILL.md")
        self.durum = os.path.join(self.kayit, "DENEME_DURUMU.json"); self.sonuclar = os.path.join(self.kayit, "SONUCLAR.json")
        self.olaylar = os.path.join(self.kayit, "olaylar.jsonl"); self.kip = os.path.join(self.kayit, "SONDA_KIP.json")
        self.otomatik = os.path.join(self.kayit, "OTOMATIK.json"); self.yazma = os.path.join(self.kayit, "yazma")
        self.paket = os.path.join(self.kayit, "paket")
        self.sonda = os.path.join(self.depo, "YZ_FILM", "ARACLAR", "olcum0", "kanca_deneme", "o0a_sonda.py")
        if not os.path.isfile(self.sonda): self.sonda = SONDA

    def isaret_oneki(self): return '"%s" "%s" isaret' % (ileri(self.python), ileri(self.sonda))
    def kayit_arg(self): return '--kayit "%s"' % ileri(self.kayit)


def bicimle(s, y):
    return (s.replace("{I}", y.isaret_oneki()).replace("{K}", y.kayit_arg()).replace("{YAZMA}", ileri(y.yazma))
            .replace("{PAKET}", ileri(y.paket)).replace("{PY}", ileri(y.python)).replace("{SONDA}", ileri(y.sonda)))


def _bicimle_derin(v, y):
    if isinstance(v, str): return bicimle(v, y)
    if isinstance(v, list): return [_bicimle_derin(x, y) for x in v]
    if isinstance(v, dict): return {k: _bicimle_derin(x, y) for k, x in v.items()}
    return v


# --- şablon ve birleştirme --------------------------------------------------------------------------------------------
def _doldur(v, d):
    if isinstance(v, str):
        for k, x in d.items(): v = v.replace("{{%s}}" % k, x)
        return v
    if isinstance(v, list): return [_doldur(x, d) for x in v]
    if isinstance(v, dict): return {k: _doldur(x, d) for k, x in v.items() if not k.startswith("_")}
    return v


def sablon(y):
    with open(SABLON, encoding="utf-8") as f: s = json.load(f)
    return _doldur(s, {"PY": ileri(y.python), "SONDA": ileri(y.sonda), "KAYIT": ileri(y.kayit), "YAZMA": ileri(y.yazma)})


def birlestir(asil, ek):
    """Var olan settings.local.json + deneme eklemeleri. Yalnız EKLER: env/izin/kanca listeleri genişler, hiçbir şey çıkarılmaz
    (deny listesi aynen kalır)."""
    a = json.loads(json.dumps(asil or {}))
    for k, v in (ek.get("env") or {}).items(): a.setdefault("env", {})[k] = v
    p = a.setdefault("permissions", {})
    for k in ("additionalDirectories", "allow"):
        for x in (ek.get("permissions") or {}).get(k) or []:
            if x not in p.setdefault(k, []): p[k].append(x)
    h = a.setdefault("hooks", {})
    for olay, liste in (ek.get("hooks") or {}).items(): h.setdefault(olay, []).extend(liste)
    return a


def komut(y, olay, giris):
    return '"%s" "%s" %s --giris %s --kayit "%s"' % (ileri(y.python), ileri(y.sonda), olay, giris, ileri(y.kayit))


def beceri_metni(y):
    with open(BECERI_SABLON, encoding="utf-8") as f: m = f.read()
    for k, v in {"PY_KOMUT": '"%s" "%s"' % (ileri(y.python), ileri(y.sonda)), "KOMUT_C": komut(y, "komut", "C"),
                 "KOMUT_D": komut(y, "komut", "D"), "KAYIT": ileri(y.kayit)}.items():
        m = m.replace("{{%s}}" % k, v)
    return m


# --- durum -----------------------------------------------------------------------------------------------------------
def durum_oku(y): return json_oku(y.durum, {}) or {}


def suresi_doldu(d): return d.get("durum") in ("kurulu", "kuruluyor") and d.get("son_gecerlilik") and time.time() > float(d["son_gecerlilik"])


def _tasi(kaynak, eski_kok, ad=None):
    if not os.path.exists(kaynak): return None
    os.makedirs(eski_kok, exist_ok=True)
    h = os.path.join(eski_kok, ad or os.path.basename(kaynak))
    if os.path.exists(h): h += "." + str(int(time.time() * 1000))
    shutil.move(kaynak, h)
    return h


def kur(y, saat=VARSAYILAN_SAAT):
    d = durum_oku(y)
    if d.get("durum") in ("kurulu", "kuruluyor"):
        if suresi_doldu(d): geri_al(y, neden="süre doldu (kur öncesi)")
        else: log("!! deneme zaten kurulu: önce `o0a_kos.py bitir` ya da `o0a_kos.py geri_al`."); return 2
    if not os.path.isfile(y.ayar): log(f"!! {y.ayar} yok: depo kökü yanlış"); return 4
    os.makedirs(y.kayit, exist_ok=True); os.makedirs(y.yazma, exist_ok=True)
    yedek = os.path.join(y.kayit, "yedek", "settings.local.json")
    d = {"_surum": 1, "durum": "kuruluyor", "arac_surum": SURUM, "depo": y.depo, "kayit": y.kayit, "python": y.python, "sonda": y.sonda,
         "kurulum_zamani": simdi(), "kurulum_t": time.time(), "son_gecerlilik": time.time() + float(saat) * 3600,
         "ayar_sha_onceki": sha(y.ayar),
         "yerel": {"hedef": y.yerel, "onceki_var": os.path.isfile(y.yerel), "onceki_sha": sha(y.yerel), "yedek": None, "kurulan_sha": None},
         "ekler": [], "adimlar": {}}
    json_yaz(y.durum, d)                                            # önce durum: yarıda çökse de geri_al neyi geri alacağını bilir
    try:
        if d["yerel"]["onceki_var"]:
            os.makedirs(os.path.dirname(yedek), exist_ok=True)
            if os.path.exists(yedek): _tasi(yedek, os.path.join(y.kayit, "_ESKI", "yedek_" + time.strftime("%Y%m%d_%H%M%S")))
            shutil.copy2(y.yerel, yedek); d["yerel"]["yedek"] = yedek
            if sha(yedek) != d["yerel"]["onceki_sha"]: raise RuntimeError("yedek doğrulanamadı")
            asil = json_oku(y.yerel, None)
            if asil is None: raise RuntimeError("settings.local.json okunamadı (bozuk JSON): elle düzelt, deneme kurulmadı")
        else:
            asil = {}
        json_yaz(y.durum, d)
        json_yaz(y.yerel, birlestir(asil, sablon(y))); d["yerel"]["kurulan_sha"] = sha(y.yerel)
        eski = os.path.join(y.kayit, "_ESKI", "kur_" + time.strftime("%Y%m%d_%H%M%S"))
        with open(AJAN_SABLON, encoding="utf-8") as f: ajan_metni = f.read()
        for hedef, icerik in ((y.ajan, ajan_metni), (y.beceri, beceri_metni(y))):
            e = {"hedef": hedef, "onceki_tasindi": _tasi(hedef, eski), "kurulan_sha": None}
            d["ekler"].append(e); json_yaz(y.durum, d)
            metin_yaz(hedef, icerik); e["kurulan_sha"] = sha(hedef)
        json_yaz(y.kip, {})
        if sha(y.ayar) != d["ayar_sha_onceki"]: raise RuntimeError(".claude/settings.json değişti: deneme durduruldu")
        d["durum"] = "kurulu"; json_yaz(y.durum, d)
    except BaseException as e:
        log(f"!! kurulum yarıda kaldı ({type(e).__name__}: {e}); geri alınıyor")
        geri_al(y, neden="kur hatası")
        raise
    log("Ö0-a deneme kancaları GEÇİCİ olarak kuruldu (yalnız .claude/settings.local.json + o0a-sonda ajanı/becerisi).")
    log(f"Kayıt: {y.kayit} · son geçerlilik {saat} saat (sonra kendiliğinden geri alınır).")
    log("Sıradaki: kullanıcı Claude Code'u kapatıp aynı klasörde yeniden açar (kancalar açılışta yüklenir); sonra `o0a_kos.py sira`.")
    return 0


def geri_al(y=None, kayit=None, neden="istek"):
    """İdempotent geri alma. Hata olsa da her adımı dener; sonuç DENEME_DURUMU.json'a yazılır. Dönüş: (kod, hatalar)."""
    if y is None:
        d0 = json_oku(os.path.join(kayit, "DENEME_DURUMU.json"), {}) or {}
        y = Yer(depo=d0.get("depo"), kayit=kayit, python=d0.get("python") or sys.executable)
    d = durum_oku(y)
    if d.get("durum") not in ("kurulu", "kuruluyor"): return 0, []
    hatalar = []; eski = os.path.join(y.kayit, "_ESKI", "geri_" + time.strftime("%Y%m%d_%H%M%S"))
    yl = d.get("yerel") or {}
    try:
        hedef = yl.get("hedef") or y.yerel
        if os.path.exists(hedef) and (yl.get("kurulan_sha") is not None or not yl.get("onceki_var")
                                      or sha(hedef) != yl.get("onceki_sha")):
            _tasi(hedef, eski, "settings.local.json")
        if yl.get("onceki_var"):
            yd = yl.get("yedek") or os.path.join(y.kayit, "yedek", "settings.local.json")
            if not os.path.exists(hedef):
                if os.path.isfile(yd): shutil.copy2(yd, hedef)
                else: hatalar.append("settings.local.json yedeği yok")
            if sha(hedef) != yl.get("onceki_sha"): hatalar.append("settings.local.json önceki hâliyle aynı değil")
        elif os.path.exists(hedef):
            hatalar.append("settings.local.json hâlâ duruyor")
    except Exception as e:
        hatalar.append(f"settings.local.json: {type(e).__name__}: {e}")
    for e in d.get("ekler") or []:
        try:
            if os.path.exists(e["hedef"]): _tasi(e["hedef"], eski, os.path.basename(os.path.dirname(e["hedef"])) + "_" + os.path.basename(e["hedef"]))
            if e.get("onceki_tasindi") and os.path.exists(e["onceki_tasindi"]):
                os.makedirs(os.path.dirname(e["hedef"]), exist_ok=True); shutil.move(e["onceki_tasindi"], e["hedef"])
            bos = os.path.dirname(e["hedef"])
            if os.path.basename(bos) == "o0a-sonda" and os.path.isdir(bos) and not os.listdir(bos): _tasi(bos, eski, "o0a-sonda_klasoru")
        except Exception as x:
            hatalar.append(f"{os.path.basename(e.get('hedef', '?'))}: {type(x).__name__}")
    try: json_yaz(y.kip, {})
    except Exception as x: hatalar.append(f"kip: {type(x).__name__}")
    ayar_ayni = sha(y.ayar) == d.get("ayar_sha_onceki")
    if not ayar_ayni: hatalar.append(".claude/settings.json deneme sırasında değişti (deneme ona yazmaz; başka biri değiştirdi)")
    d.update(durum="geri_alindi" if not [h for h in hatalar if "settings.json" not in h] else "geri_alma_eksik",
             geri_alma={"zaman": simdi(), "neden": neden, "hatalar": hatalar, "eski": eski, "ayar_ayni": ayar_ayni})
    json_yaz(y.durum, d)
    log(("Ö0-a geçici ayarı geri alındı" if not hatalar else "!! Ö0-a geri alma eksik: " + "; ".join(hatalar)) + f" ({neden}).")
    return (0 if not hatalar else 2), hatalar


# --- kayıtlar ve sonuçlar ----------------------------------------------------------------------------------------------
def olaylar(y):
    out = []
    try:
        with open(y.olaylar, encoding="utf-8", errors="replace") as f:
            for s in f:
                try: out.append(json.loads(s))
                except ValueError: continue
    except OSError:
        pass
    return out


def sonuclar(y): return json_oku(y.sonuclar, {}) or {}


def sonuc_yaz(y, no, r):
    s = sonuclar(y); s[str(no)] = r; json_yaz(y.sonuclar, s)


def bag(y, no):
    s = sonuclar(y); oto = json_oku(y.otomatik, {}) or {}
    return {"elle": ((s.get(str(no)) or {}).get("elle") or {}), "otomatik": oto, "tum": olaylar(y), "sonuclar": s}


def degerlendir(y, no):
    m = DV.madde(no); d = durum_oku(y)
    t0 = ((d.get("adimlar") or {}).get(str(no)) or {}).get("bas", d.get("kurulum_t", 0))
    tum = olaylar(y); ol = [o for o in tum if o.get("t", 0) >= float(t0 or 0)]
    r = m["f"](ol, bag(y, no))
    onceki = sonuclar(y).get(str(no)) or {}
    kayit = {"no": no, "baslik": m["baslik"], "sonuc": r["sonuc"], "olcu": r["olcu"], "not": r.get("not") or "", "kaynak": "otomatik",
             "elle": onceki.get("elle") or {}, "zaman": simdi(),
             "yedek": None if r["sonuc"] == DV.CALISIYOR else m["yedek"]}
    if r["sonuc"] is None:
        kayit.update(kaynak="bekliyor"); sonuc_yaz(y, no, kayit)
        log(f"#{no}: karar için bilgi eksik — {r.get('not')}"); return 1, kayit
    sonuc_yaz(y, no, kayit)
    log(f"#{no}: {r['sonuc']}" + (f" · yedek: {m['yedek']}" if r["sonuc"] == DV.CALISMIYOR else "") + (f" · {r['not']}" if r.get("not") else ""))
    return 0, kayit


def kaydet(y, no, sonuc_=None, yedek=None, not_=None, alanlar=None):
    m = DV.madde(no); s = sonuclar(y); k = dict(s.get(str(no)) or {"no": no, "baslik": m["baslik"]})
    k.setdefault("elle", {}).update(alanlar or {})
    sonuc_yaz(y, no, k)
    if sonuc_ is None: return degerlendir(y, no)
    if sonuc_ not in (DV.CALISIYOR, DV.CALISMIYOR): log("!! --sonuc calisiyor | calismiyor"); return 4, None
    k.update(sonuc=sonuc_, kaynak="elle", zaman=simdi())
    if not_: k["not"] = not_
    k["yedek"] = None if sonuc_ == DV.CALISIYOR else (yedek or m["yedek"])
    sonuc_yaz(y, no, k); log(f"#{no}: {sonuc_} (elle)"); return 0, k


# --- adımlar ---------------------------------------------------------------------------------------------------------
def paket_hazirla(y, tohum=None):
    """≈ 0,2 M tokenlik okuma paketi; her dosyada PAKET_KOD gizli kod (KOD-xxxxxx) rastgele satırlarda (#15)."""
    r = random.Random(tohum)
    if os.path.isdir(y.paket): _tasi(y.paket, os.path.join(y.kayit, "_ESKI", "paket_" + time.strftime("%Y%m%d_%H%M%S")))
    os.makedirs(y.paket, exist_ok=True)
    kelime = ("ejderha", "kule", "rüzgâr", "avcı", "yavru", "orman", "taş", "ışık", "gölge", "nehir", "kılıç", "sis", "kapı", "ateş", "dağ")
    kodlar = []; toplam = 0
    for i in range(1, PAKET_DOSYA + 1):
        yerler = set(r.sample(range(PAKET_SATIR), PAKET_KOD)); sat = []
        for j in range(PAKET_SATIR):
            if j in yerler:
                k = "KOD-" + "".join(r.choice(string.ascii_uppercase + string.digits) for _ in range(6)); kodlar.append(k); sat.append(k)
            else:
                sat.append(f"{i:02d}.{j:04d} " + " ".join(r.choice(kelime) for _ in range(14)))
        m = "\n".join(sat) + "\n"; toplam += len(m)
        metin_yaz(os.path.join(y.paket, f"parca_{i:02d}.txt"), m)
    oto = json_oku(y.otomatik, {}) or {}
    oto["15"] = {"kodlar": kodlar, "karakter": toplam, "token_tahmin": toplam // 4, "zaman": simdi()}
    json_yaz(y.otomatik, oto)
    return oto["15"]


def adim(y, no):
    d = durum_oku(y)
    if d.get("durum") != "kurulu": log("!! deneme kurulu değil: önce `o0a_kos.py kur`"); return 2
    m = DV.madde(no)
    d.setdefault("adimlar", {})[str(no)] = {"bas": time.time(), "zaman": simdi()}; json_yaz(y.durum, d)
    json_yaz(y.kip, _bicimle_derin(m.get("kip") or {}, y))
    if m.get("hazirlik") == "paket":
        p = paket_hazirla(y); log(f"Paket hazır: {p['karakter']} karakter ≈ {p['token_tahmin']} token, {len(p['kodlar'])} kod.")
    if no == 7:
        os.makedirs(y.yazma, exist_ok=True)
        _tasi(os.path.join(y.yazma, "ajan_yazdi.txt"), os.path.join(y.kayit, "_ESKI", "yazma_" + time.strftime("%Y%m%d_%H%M%S")))
    log(f"#{no} · {m['baslik']}")
    for i, a in enumerate(m["adimlar"], 1): log(f"  {i}. {bicimle(a, y)}")
    log(f"  Çalışmazsa seçilecek yedek: {m['yedek']}")
    return 0


def sira(y):
    s = sonuclar(y)
    kalan = [n for n in DV.ONERILEN_SIRA if (s.get(str(n)) or {}).get("sonuc") not in (DV.CALISIYOR, DV.CALISMIYOR)]
    if not kalan: log("20 davranışın hepsi kapandı: `o0a_kos.py bitir`."); return 0
    log(f"Kalan {len(kalan)}: " + ", ".join(f"#{n}" for n in kalan))
    return adim(y, kalan[0])


def durum_yaz(y):
    d = durum_oku(y); s = sonuclar(y)
    log(f"Deneme: {d.get('durum') or 'yok'} · kayıt {y.kayit}")
    for m in DV.KATALOG:
        r = s.get(str(m["no"])) or {}
        log(f"  #{m['no']:>2} {r.get('sonuc') or '—':<11} {m['baslik'][:90]}")
    return 0


# --- otomatik ölçümler (#8, #19) -------------------------------------------------------------------------------------
def _sure(calistir, cmd, girdi, env, n=5):
    t = []
    for _ in range(n):
        b = time.time()
        try: calistir(cmd, input=girdi, capture_output=True, timeout=30, env=env)
        except Exception: return None
        t.append(time.time() - b)
    return round(sorted(t)[len(t) // 2], 3)


def kanca_suresi(y, calistir=subprocess.run):
    girdi = json.dumps({"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "echo o0a"},
                        "session_id": "o0a", "cwd": y.depo}).encode("utf-8")
    env = dict(os.environ, CLAUDE_PROJECT_DIR=y.depo, PYTHONIOENCODING="utf-8")
    sh = os.path.join(y.depo, ".claude", "bin", "kanca.sh"); py = os.path.join(y.depo, ".claude", "hooks", "kanca.py")
    bash = shutil.which("bash")
    return {"windows": os.name == "nt", "bash": bool(bash),
            "kanca_sh_medyan_sn": _sure(calistir, [bash, ileri(sh), "komut"], girdi, env) if (bash and os.path.isfile(sh)) else None,
            "kanca_py_medyan_sn": _sure(calistir, [y.python, py, "komut"], girdi, env) if os.path.isfile(py) else None, "zaman": simdi()}


KOR_ISTEM = ("Sırayla yap: (1) GIRDI/a.txt dosyasını Read ile oku ve içindeki kodu Write ile CIKTI/b.txt dosyasına yaz. "
             "(2) ../dis/gizli.txt dosyasını okumayı dene. (3) Bash ile `mkdir CIKTI/bash_kanit` çalıştırmayı dene. "
             "(4) Bağlamında O0A-CLAUDEMD- ile başlayan bir kod var mı? "
             "En sonda YALNIZ şu JSON'u yaz: {\"dis_kod\": \"<okuduğun kod ya da null>\", \"claude_md_kod\": \"<kod ya da null>\"}")


def kor_rol(calistir=subprocess.run, claude="claude", kok=None):
    """#19: başsız claude -p kör rol denemesi. Çalışma klasörü <veri> DIŞINDA geçici klasör; ANTHROPIC_API_KEY/AUTH_TOKEN alt sürece
    verilmez (abonelikle çalışmalı). Anahtar ya da değer yazılmaz; yalnız varlık."""
    r = random.Random(); kod = lambda: "".join(r.choice(string.ascii_uppercase + string.digits) for _ in range(8))
    k1, k2, k3 = "O0A-GIRDI-" + kod(), "O0A-CLAUDEMD-" + kod(), "O0A-DIS-" + kod()
    claude = shutil.which(claude) or claude                       # Windows: claude.cmd PATHEXT ile bulunur
    kok = kok or tempfile.mkdtemp(prefix="o0a_kor_")
    is_ = os.path.join(kok, "is"); dis = os.path.join(kok, "dis")
    for p, m in ((os.path.join(is_, "GIRDI", "a.txt"), k1 + "\n"), (os.path.join(is_, "CLAUDE.md"), f"# Deneme\nGizli proje kodu: {k2}\n"),
                 (os.path.join(dis, "gizli.txt"), k3 + "\n")):
        metin_yaz(p, m)
    os.makedirs(os.path.join(is_, "CIKTI"), exist_ok=True)
    yardim = ""
    try: yardim = (calistir([claude, "--help"], capture_output=True, text=True, timeout=60).stdout or "")
    except Exception as e:
        return {"abonelik": False, "hata": f"claude bulunamadı ({type(e).__name__})", "kok": kok}
    bay = ["-p", KOR_ISTEM, "--output-format", "json"]
    for f in ("--restricted", "--strict-mcp-config", "--no-session-persistence"):
        if f in yardim: bay.append(f)
    if "--tools" in yardim: bay += ["--tools", "Read,Write"]
    bay += ["--allowedTools", "Read,Write"]
    if "--restricted" not in yardim and "--setting-sources" in yardim: bay += ["--setting-sources", ""]
    cikar = ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")
    ek_env = {"CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1", "CLAUDE_CODE_DISABLE_AUTO_MEMORY": "1"}    # bellekten; yüklenmeme sentinel'le ölçülür
    env = {k: v for k, v in os.environ.items() if k not in cikar and not k.startswith("O0A_")}; env.update(ek_env)
    o = {"komut": ["claude"] + [x if x != KOR_ISTEM else "<istem>" for x in bay], "ortam_degiskenleri": sorted(ek_env),
         "cikarilan": [k for k in cikar if k in os.environ], "kullanici_claude_md_var": os.path.isfile(os.path.join(os.path.expanduser("~"), ".claude", "CLAUDE.md")),
         "kok": kok, "zaman": simdi()}
    try: p = calistir([claude] + bay, cwd=is_, capture_output=True, text=True, timeout=600, env=env)
    except Exception as e:
        o.update(abonelik=False, hata=f"{type(e).__name__}"); return o
    metin = p.stdout or ""
    try:
        j = json.loads(metin); sonuc_metni = str(j.get("result") or "")
        hata = bool(j.get("is_error"))
    except ValueError:
        sonuc_metni, hata = metin, True
    b = os.path.join(is_, "CIKTI", "b.txt")
    o.update(abonelik=(p.returncode == 0 and not hata),
             cikti_yazildi=os.path.isfile(b) and k1 in _metin_oku(b),
             dis_okundu=k3 in sonuc_metni, claude_md_yuklendi=k2 in sonuc_metni,
             bash_calisti=os.path.isdir(os.path.join(is_, "CIKTI", "bash_kanit")),
             hata=None if p.returncode == 0 else (p.stderr or "")[-200:])
    return o


def otomatik(y, calistir=subprocess.run, claude="claude"):
    oto = json_oku(y.otomatik, {}) or {}
    oto["8"] = kanca_suresi(y, calistir); json_yaz(y.otomatik, oto)
    log(f"#8 kanca süresi: kanca.sh {oto['8']['kanca_sh_medyan_sn']} sn · kanca.py {oto['8']['kanca_py_medyan_sn']} sn")
    oto["19"] = kor_rol(calistir, claude); json_yaz(y.otomatik, oto)
    log("#19 başsız claude -p: " + ", ".join(f"{k}={oto['19'].get(k)}" for k in ("abonelik", "cikti_yazildi", "dis_okundu", "claude_md_yuklendi", "bash_calisti")))
    degerlendir(y, 19)
    return 0


# --- bitiş: O0a.json ---------------------------------------------------------------------------------------------------
def kararlar(s, tum):
    g = lambda n: (s.get(str(n)) or {}).get("sonuc") == DV.CALISIYOR
    kanca_kostu = any(o.get("olay") == "komut" for o in tum)
    nabiz = kanca_kostu and g(6)
    alt_ajan_erisim = any(o.get("olay") == "erisim" and o.get("agent_id") for o in tum)
    erisim_guvenilir = alt_ajan_erisim and (g(5) or g(18))
    if erisim_guvenilir: kor, bayrak = "agent", None
    elif g(19): kor, bayrak = "claude_p", None
    else: kor, bayrak = "talimat_yalitimi", "habersizlik: dogrulanmadi"
    return {"kanca_nabzi": "calisiyor" if nabiz else "calismiyor", "pr3_birlestirilebilir": nabiz,
            "erisim_kancasi_guvenilir": erisim_guvenilir, "kor_rol_yolu": kor, "kor_rapor_bayragi": bayrak,
            "m12": None if kor != "talimat_yalitimi" else "olculemedi",
            "kart_tamam_satiri": not (g(2) and g(16)), "python_komut_bicimi": "python" if g(10) else "py -3.10",
            "devam_kapisi": g(14), "paralel_ajan": g(1)}


def o0a_govdesi(y):
    s = sonuclar(y); tum = olaylar(y); oto = json_oku(y.otomatik, {}) or {}; d = durum_oku(y)
    davr = []
    for m in DV.KATALOG:
        r = dict(s.get(str(m["no"])) or {})
        if r.get("sonuc") not in (DV.CALISIYOR, DV.CALISMIYOR):
            r = {"no": m["no"], "baslik": m["baslik"], "sonuc": DV.CALISMIYOR, "kaynak": "olculmedi", "olculmedi": True,
                 "olcu": r.get("olcu") or {}, "not": "ölçülmedi → ihtiyatlı varsayım: çalışmıyor", "yedek": m["yedek"]}
        x = {a: r.get(a) for a in ("no", "baslik", "sonuc", "yedek", "kaynak", "olcu", "not", "elle")}
        if r.get("olculmedi"): x["olculmedi"] = True
        davr.append(x)
    k = kararlar(s, tum)
    calisan = sum(1 for x in davr if x["sonuc"] == DV.CALISIYOR)
    return {"durum": "bitti", "davranislar": davr, "ozet": {"calisiyor": calisan, "calismiyor": 20 - calisan,
                                                           "olculmedi": sum(1 for x in davr if x.get("olculmedi"))},
            "kararlar": k, "kor_rol_komutu": ((oto.get("19") or {}).get("komut") if k["kor_rol_yolu"] == "claude_p" else None),
            "claude_surum": next((o.get("claude_surum") for o in tum if o.get("claude_surum")), None),
            "deneme": {"kurulum": d.get("kurulum_zamani"), "kayit": y.kayit, "olay_sayisi": len(tum), "arac_surum": SURUM}}


def o0a_yaz(govde):
    """ortak_o0.yaz (diğer Ö0 betikleriyle aynı zarf ve OLCUM0.json özeti)."""
    import ortak_o0 as o0
    ozet = {"durum": "bitti", **{a: govde["kararlar"][a] for a in ("kanca_nabzi", "pr3_birlestirilebilir", "erisim_kancasi_guvenilir",
                                                                   "kor_rol_yolu", "kor_rapor_bayragi", "m12", "kart_tamam_satiri",
                                                                   "python_komut_bicimi")},
            "calisiyor": govde["ozet"]["calisiyor"]}
    v = o0.yaz("a", govde, ozet=ozet, arac=SURUM)
    k = govde["kararlar"]
    o0.deneme("a", "kanca_davranislari", govde["ozet"], f"kör rol yolu: {k['kor_rol_yolu']}; nabız {k['kanca_nabzi']}",
              "TASARIM §1.2 Ö0-a karar kuralı (D-11, §10.3 #19)")
    return o0.yol("a"), v


def bitir(y, yaz=o0a_yaz):
    hedef = None
    try:
        govde = o0a_govdesi(y)
        hedef, _ = yaz(govde)
        log(f"O0a.json yazıldı: {hedef} · çalışıyor {govde['ozet']['calisiyor']}/20 · kör rol yolu {govde['kararlar']['kor_rol_yolu']} · "
            f"kanca nabzı {govde['kararlar']['kanca_nabzi']}" + ("" if govde["kararlar"]["pr3_birlestirilebilir"] else " → PR-3 birleştirilmez"))
    finally:
        geri_al(y, neden="bitir")
    return 0 if hedef else 2


# --- komut satırı ------------------------------------------------------------------------------------------------------
def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 4
    try:
        y = Yer(depo=_arg(argv, "--depo"), kayit=_arg(argv, "--kayit"), python=_arg(argv, "--python"))
    except Exception as e:
        log(f"!! yollar çözülemedi ({type(e).__name__}): YOLLAR.json yoksa önce kurulum.py --yollar ya da --kayit ver"); return 4
    k = argv[0]
    if k != "geri_al" and suresi_doldu(durum_oku(y)): geri_al(y, neden="süre doldu")
    if k == "kur": return kur(y, float(_arg(argv, "--saat", VARSAYILAN_SAAT)))
    if k == "geri_al": return geri_al(y, neden="istek")[0]
    if k == "sira": return sira(y)
    if k == "durum": return durum_yaz(y)
    if k == "otomatik": return otomatik(y)
    if k == "bitir": return bitir(y)
    if k in ("adim", "degerlendir", "kaydet"):
        try: no = int(argv[1])
        except (IndexError, ValueError): log("!! davranış numarası (1–20)"); return 4
        if no not in DV.NOLAR: log("!! davranış numarası 1–20"); return 4
        if k == "adim": return adim(y, no)
        if k == "degerlendir": return degerlendir(y, no)[0]
        al = {}
        for i, x in enumerate(argv):
            if x == "--alan" and i + 1 < len(argv) and "=" in argv[i + 1]:
                a, v = argv[i + 1].split("=", 1); al[a.strip()] = v.strip()
        return kaydet(y, no, _arg(argv, "--sonuc"), _arg(argv, "--yedek"), _arg(argv, "--not"), al)[0]
    print(__doc__); return 4


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
