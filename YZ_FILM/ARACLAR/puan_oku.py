"""PUAN OKU — seyirci/jüri raporlarını okur ve birleştirir (v1: ÖZET satırı + medyan; v2: rapor.json + seyirci_topla).

v1 (değişmedi):
  python puan_oku.py <rapor.md|rapor.json> [<rapor2> ...] [--esik 8]
  Rapor biçimi (son satırlardan biri):  OZET | anlasilirlik: 7 | merak: 8 | duygu: 6 | ORTALAMA: 7.0 | KRITIK: 2
  Birden çok rapor verilirse ORTALAMA'ların MEDYANI alınır (seyirci puanları gürültülü; tek uç puan sonucu çekmez). ör. 6, 8, 9 → 8
  Çıkış kodu: 0 eşik geçildi ve KRITIK yok · 3 eşik altında ya da KRITIK var · 1 ÖZET satırı bulunamadı

v2 (TASARIM §1.4, §5.8, §6.3, §7.2 HS_*; film.py görevi olarak; YZ_FILM_GOREV ortam değişkeni görev klasörüdür):
  python puan_oku.py seyirci-topla --kip kagit|plan|animatik|kesit|kurgu --tur N --film <film>
      _RAPOR/SEYIRCI/<kip>_t<N>/s<i>_rapor.json (+ yoksa .md OZET satırları), e<i>_eslesme.json (ozet-eslestirici),
      <kip>_ilk2dk_t<N>/s<i>_rapor.json, KRITIK_RED.json (yapimci·doktor kanıtları) →
      _RAPOR/SEYIRCI_KARAR_<KIP>_t<N>.json (tam karar) + kapı raporu _RAPOR/HS_<KIP>_FILM_t<N>.json (kapi.py zarfı)
  python puan_oku.py ilk2dk-topla --kip kagit --tur N --film <film>      → _RAPOR/HS_ILK2DK_FILM.json
  python puan_oku.py --plan --tur N --film <film>      A07d: plan eleştirisi raporları → _RAPOR/PLAN_ELESTIRI_FILM_t<N>.json
  Kodda: seyirci_topla(film, kip, tur, gorev=None) → karar · rapor_oku(yol) → normal rapor · medyan(x)
Birleştirme (seyirci_topla):
  - **Medyan**: 6 ölçüt + GENEL, parti başına GENEL; dönen seyirci medyana girmez.
  - KRİTİK/ORTA birleştirme: aynı konum ±kritik_birlestirme_komsu plan (kâğıtta sahne sırası). 2+ seyircinin KRİTİK'i reddedilemez;
    tek seyircinin KRİTİK'i yalnız KRITIK_RED.json'daki kanıt betikle doğrulanırsa (satır o seyircinin paketinde, kopukluk anından önce,
    maskesiz) geçersiz sayılır (D-21).
  - Özet eşleşmesi: bulundu 1, kismen ozet_kismen_agirlik, yok 0; parti başına seyirci medyanı (kritik olgular ayrıca).
  - Plato: iki tur üst üste GENEL artışı < max(plato_genel_artis_min, seyirci_gurultu_std) → plato. Salınım: en iyi turdan ≥ salinim_dusus
    düşüş → en_iyi_tur. Personalar, tahmini tutma eğrisi, parça konum yanlılığı (eğim < parca_konum_egim_bayrak → BAYRAK), seyirciler
    arası ilgi korelasyonu (Spearman < ilgi_korelasyon_min → BAYRAK), ortak sıkılma → kesme adayı.
  - Kapı (§1.4): geçerli KRİTİK 0 · kritik olgu eşleşmesi ≥ ozet_eslesme_kritik_min (parti başına) · GENEL ≥ seyirci_kapi_genel_min ·
    şema HATA 0. Hedef: GENEL ≥ seyirci_genel_esik, ölçüt ≥ seyirci_olcut_min ve seyirci_olcut_hedef, ORTA ≤ kopukluk_orta_max_parti,
    ilk 2 dk ≥ ilk2dk_devam_evet_min, bütün olgular ≥ ozet_eslesme_min.
    Sonuç: kapı yok → HATA · kapı var + hedef var → GEC · kapı var + hedef yok → KISMI (hedef maddeleri "hedef": true) ·
    kapı var + plato ve merdiven turu zaten koştu → BAYRAK (hedef_alti: true; döngü durur, hat sürer).
Çıkış kodları (v2): 0 rapor yazıldı (kapı sonucu raporda) · 1 araç/kullanım hatası · 4 YOLLAR.json yok.
"""
import os, re, sys, json, glob, math
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
try: import kapi                       # v2 zarfı; v1 (OZET satırı) kapi olmadan da çalışır
except Exception: kapi = None
OZET = re.compile(r"^\s*\**\s*[OÖ]ZET\s*\|(.+)$", re.I | re.M)
OZET_TUM = re.compile(r"^\s*\**\s*[OÖ]ZET(?:_(P\d+))?\s*\|(.+)$", re.I | re.M)
OLCUTLER = ("anlasilirlik", "akicilik", "merak", "duygu", "ritim", "ilk30")
SURUM = "puan_oku 2.0"


def _alanlar(govde):
    alanlar = {}
    for parca in govde.split("|"):
        if ":" in parca:
            k, v = parca.split(":", 1)
            try: alanlar[k.strip().lower()] = float(v.strip().split()[0].replace(",", "."))
            except (ValueError, IndexError): pass
    return alanlar


def _metin(yol):
    with open(yol, encoding="utf-8-sig") as f: return f.read()


def oku(yol):
    m = OZET.findall(_metin(yol))
    if not m: return None
    alanlar = _alanlar(m[-1])
    if "ortalama" not in alanlar:
        puanlar = [v for k, v in alanlar.items() if k not in ("kritik", "orta")]
        if puanlar: alanlar["ortalama"] = alanlar.get("genel", sum(puanlar) / len(puanlar))
    return alanlar


def oku_tum(yol):
    """{"OZET": {...}, "P1": {...}, …} — bütün OZET ve OZET_P<n> satırları (son geçerli olan)."""
    out = {}
    for parti, govde in OZET_TUM.findall(_metin(yol)):
        out[(parti or "OZET").upper()] = _alanlar(govde)
    return out


def medyan(x):
    x = sorted(x); n = len(x)
    if not n: return None
    return x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2


def main(a):
    esik = float(a[a.index("--esik") + 1]) if "--esik" in a else 8.0
    yollar = [x for i, x in enumerate(a) if not x.startswith("--") and (i == 0 or a[i - 1] != "--esik")]
    if not yollar: print(__doc__); return 0
    sonuc = []
    for y in yollar:
        r = oku(y) if not y.endswith(".json") else _json_ozet(y)
        if r is None or "ortalama" not in r: print(f"ÖZET satırı yok: {y}"); return 1
        sonuc.append(r); print(f"{y}: ORTALAMA {r['ortalama']:.2f} · KRITIK {int(r.get('kritik', 0))}")
    ort = medyan([r["ortalama"] for r in sonuc]); kritik = sum(int(r.get("kritik", 0)) for r in sonuc)
    gecti = ort >= esik and kritik == 0
    print(f"GENEL (medyan): {ort:.2f} / eşik {esik} · KRITIK {kritik} → {'GEÇTİ' if gecti else 'GEÇMEDİ'}")
    return 0 if gecti else 3


def _json_ozet(y):
    r = rapor_oku(y)
    if not r or r["puanlar"].get("GENEL") is None: return None
    return {"ortalama": r["puanlar"]["GENEL"], "kritik": r["kritik"]}


# ======================================================================================================== v2 ===
_E = None


def esikler_():
    global _E
    if _E is None:
        try:
            import esikler
            _E = esikler.yukle()
        except Exception: _E = {}
    return _E


VARSAYILAN = {"seyirci_kapi_genel_min": 7, "seyirci_genel_esik": 8, "seyirci_olcut_min": 7, "seyirci_olcut_hedef": {},
              "kopukluk_kritik_max": 0, "kopukluk_orta_max_parti": 3, "ozet_eslesme_min": 0.8, "ozet_eslesme_kritik_min": 0.8,
              "ilk2dk_devam_evet_min": 3, "plato_genel_artis_min": 0.5, "seyirci_gurultu_std": None, "ozet_kismen_agirlik": 0.5,
              "sikilma_ortak_isaret_min": 2, "ilgi_korelasyon_min": 0.5, "parca_konum_egim_bayrak": -0.15, "salinim_dusus": 1,
              "kritik_birlestirme_komsu": 1, "seyirci_gecerli_rapor_min": 2, "tutma_egrisi_dilim_sn": 60, "doktor_tetik_iyilesme": 0.5}


def E(ad):
    v = esikler_().get(ad) if hasattr(esikler_(), "get") else None
    return VARSAYILAN.get(ad) if v is None else v


def json_oku(p, v=None):
    try:
        with open(p, encoding="utf-8-sig") as f: return json.load(f)
    except (OSError, ValueError): return v


def atomik_yaz(p, v):
    import ortak
    ortak.atomik_yaz(p, v)


# --- görev bağlamı ve kapı raporu (hikaye_odasi.py ve bulgu_yonlendir.py de kullanır) ---------------------------
def gorev_baglami(tur=None, asama=None):
    """YZ_FILM_GOREV/GOREV.json'dan {id, tur_no, asama, rapor, merdiven}; yoksa verilenlerle."""
    g = json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV") or "", "GOREV.json"), {}) or {}
    return {"id": g.get("id"), "tur_no": int(tur or g.get("tur_no") or 1), "asama": g.get("asama") or asama,
            "rapor": g.get("rapor"), "merdiven": g.get("merdiven"), "surum": g.get("surum")}


def dosya_imza(film, rels):
    import hashlib
    h = hashlib.sha1()
    for r in rels:
        p = os.path.join(film, r)
        if os.path.isfile(p):
            h.update(r.encode())
            with open(p, "rb") as f: h.update(f.read())
        else: h.update((r + ":yok").encode())
    return h.hexdigest()[:16]


def yerel_kapilar():
    try:
        from hat import asamalar
        return set(asamalar.YEREL_KAPILAR) | {"SEMA"}
    except Exception: return set()


def kapi_yaz(film, kapi_kod, kapsam, olcumler, tur, asama, gorev=None, girdi=(), arac=SURUM, ek=None, yol=None, sonuc=None,
             birimler=None):
    """kapi.rapor_kur ile zarflı rapor kurar, (gerekirse) sonucu üstüne yazar, denetler ve atomik yazar. (yol, rapor).
    ADLAR.json'da henüz olmayan yerel kâğıt kapıları (hat.asamalar.YEREL_KAPILAR) için yalnız 'kapi bilinmiyor' denetimi atlanır."""
    r = kapi.rapor_kur(kapi_kod, kapsam, olcumler, tur=tur, asama=asama, gorev=gorev, girdi_imza=dosya_imza(film, girdi),
                       arac_surum=arac, ek=ek, birimler=birimler)
    if sonuc:
        r["sonuc"] = sonuc; r["_uretim"]["sonuc"] = sonuc
    h = [x for x in kapi.dogrula(r) if not (x.startswith("kapi bilinmiyor") and kapi_kod in yerel_kapilar())]
    if h: raise kapi.RaporHatasi(h)
    yol = yol or os.path.join(film, "_RAPOR", f"{kapi_kod}_{kapsam}_t{tur}.json")
    atomik_yaz(yol, r)
    return yol, r


# --- rapor okuma ------------------------------------------------------------------------------------------------
def _sayi(v):
    if isinstance(v, bool): return None
    if isinstance(v, (int, float)): return float(v)
    try: return float(str(v).replace(",", "."))
    except (TypeError, ValueError): return None


def zaman_sn(z):
    if isinstance(z, (int, float)) and not isinstance(z, bool): return float(z)
    if not isinstance(z, str): return None
    p = z.strip().split(":")
    try:
        if len(p) == 3: return int(p[0]) * 3600 + int(p[1]) * 60 + float(p[2])
        if len(p) == 2: return int(p[0]) * 60 + float(p[1])
        return float(p[0])
    except ValueError: return None


def rapor_oku(yol):
    """rapor.json (§5.8) ya da .md OZET satırları → normal sözlük; okunamazsa None. 'sema_hatalari' doluysa rapor geçersizdir."""
    j = json_oku(yol) if yol.endswith(".json") else None
    if j is None and yol.endswith(".json"):
        md = yol[:-5] + ".md"
        if os.path.isfile(md): yol = md
        else: return None
    if isinstance(j, dict):
        hata = []
        p = j.get("puanlar") or {}
        puan = {k: _sayi(p.get(k)) for k in OLCUTLER + ("GENEL",)}
        if puan["GENEL"] is None: hata.append("puanlar.GENEL yok")
        for k, v in puan.items():
            if v is not None and not (1 <= v <= 10): hata.append(f"puanlar.{k} 1–10 dışında"); puan[k] = None
        kop = [k for k in j.get("kopukluklar") or [] if isinstance(k, dict)]
        for k in kop: k["tur"] = str(k.get("tur") or "ORTA").upper().replace("İ", "I")
        parti = {}
        for x in j.get("parca_puanlari") or []:
            if isinstance(x, dict) and _sayi(x.get("GENEL")) is not None: parti[str(x.get("parca"))] = _sayi(x.get("GENEL"))
        for k, v in (j.get("parti_puanlari") or {}).items():
            g = _sayi((v or {}).get("GENEL") if isinstance(v, dict) else v)
            if g is not None: parti[str(k)] = g
        return {"yol": yol, "kaynak": "json", "kip": j.get("kip"), "seyirci": j.get("seyirci"), "persona": j.get("persona"),
                "donen": bool(j.get("donen_seyirci")), "puanlar": puan, "parti": parti, "kopukluklar": kop,
                "kritik": sum(1 for k in kop if k["tur"] == "KRITIK"), "orta": sum(1 for k in kop if k["tur"] == "ORTA"),
                "sikilma": [s for s in j.get("sikilma") or [] if isinstance(s, dict)],
                "ilgi": [i for i in j.get("ilgi") or [] if isinstance(i, dict)],
                "devam": j.get("devam"), "ilk2dk_devam": j.get("ilk2dk_devam", j.get("devam")), "surum": j.get("surum"),
                "devam_olasiligi": _sayi(j.get("devam_olasiligi")), "kapatma_ani": j.get("kapatma_ani"),
                "acik_sorular": j.get("acik_sorular") or [], "sema_hatalari": hata}
    try: t = oku_tum(yol)
    except OSError: return None
    if "OZET" not in t: return None
    o = t["OZET"]
    puan = {k: o.get(k) for k in OLCUTLER}; puan["GENEL"] = o.get("genel", o.get("ortalama"))
    return {"yol": yol, "kaynak": "ozet", "kip": None, "seyirci": None, "persona": None, "donen": False, "puanlar": puan,
            "parti": {k: v.get("genel") for k, v in t.items() if k != "OZET" and v.get("genel") is not None},
            "kopukluklar": [], "kritik": int(o.get("kritik", 0)), "orta": int(o.get("orta", 0)), "sikilma": [], "ilgi": [],
            "devam": None, "ilk2dk_devam": None, "surum": None, "devam_olasiligi": None, "kapatma_ani": None, "acik_sorular": [],
            "sema_hatalari": [] if puan["GENEL"] is not None else ["GENEL yok"]}


def _seyirci_no(yol):
    m = re.search(r"s(\d+)_rapor", os.path.basename(yol))
    return int(m.group(1)) if m else None


def raporlari_topla(klasor):
    out = {}
    for p in sorted(glob.glob(os.path.join(klasor, "s*_rapor.json")) + glob.glob(os.path.join(klasor, "s*_rapor.md"))):
        n = _seyirci_no(p)
        if n is None or n in out: continue
        r = rapor_oku(p)
        if r: r["no"] = n; out[n] = r
    return [out[k] for k in sorted(out)]


# --- yardımcı istatistik ----------------------------------------------------------------------------------------
def _sira(v):
    s = sorted(range(len(v)), key=lambda i: v[i]); r = [0.0] * len(v); i = 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and v[s[j + 1]] == v[s[i]]: j += 1
        for k in range(i, j + 1): r[s[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(a, b):
    if len(a) < 3 or len(a) != len(b): return None
    ra, rb = _sira(a), _sira(b); ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    pay = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    payda = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return None if payda == 0 else pay / payda


def egim(ys):
    n = len(ys)
    if n < 2: return None
    xs = list(range(n)); mx, my = sum(xs) / n, sum(ys) / n
    d = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / d if d else None


# --- KRİTİK birleştirme ve kanıt -------------------------------------------------------------------------------
def _konum_anahtar(k, sahne_sira):
    ko = k.get("konum") or {}
    if isinstance(ko.get("plan"), int) and not isinstance(ko.get("plan"), bool): return ("plan", ko["plan"])
    s = ko.get("sahne")
    if s in sahne_sira: return ("sahne", sahne_sira[s])
    m = re.match(r"S(\d+)", str(s or ""))
    if m: return ("sahne", int(m.group(1)))
    z = zaman_sn(ko.get("zaman"))
    return ("zaman", int(z // 30)) if z is not None else ("yok", 0)


def kopukluk_birlestir(raporlar, sahne_sira=None, komsu=None):
    """[{tur, konum, anahtar, seyirciler, nedenler, kayitlar}] — aynı tür ve ±komsu konumdakiler tek küme."""
    komsu = E("kritik_birlestirme_komsu") if komsu is None else komsu
    kumeler = []
    for r in raporlar:
        for k in r["kopukluklar"]:
            a = _konum_anahtar(k, sahne_sira or {})
            hedef = next((c for c in kumeler if c["tur"] == k["tur"] and c["anahtar"][0] == a[0]
                          and (abs(c["anahtar"][1] - a[1]) <= (komsu if a[0] != "yok" else 0))), None)
            if hedef is None:
                hedef = {"tur": k["tur"], "anahtar": a, "konum": k.get("konum"), "seyirciler": [], "nedenler": [], "kayitlar": []}
                kumeler.append(hedef)
            if r["no"] not in hedef["seyirciler"]: hedef["seyirciler"].append(r["no"])
            hedef["nedenler"].append(k.get("neden")); hedef["kayitlar"].append({"seyirci": r["no"], "konum": k.get("konum")})
    for c in kumeler: c["kac_seyirci"] = len(c["seyirciler"])
    return kumeler


def _paket_metni(film, kip, tur, persona):
    s = []
    for p in sorted(glob.glob(os.path.join(film, "_KOR_PAKET", f"{kip}_t{tur}", str(persona), "**", "*.md"), recursive=True)):
        try: s.append(_metin(p))
        except OSError: pass
    return "\n".join(s)


def _satir_zamani(metin, satir):
    """Satırdan önceki son [mm:ss] zaman kodu."""
    i = metin.find(satir)
    if i < 0: return None
    kodlar = re.findall(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]", metin[:i + len(satir)])
    return zaman_sn(kodlar[-1]) if kodlar else None


def kritik_red_dogrula(film, kip, tur, kume, red, raporlar, maskeler=()):
    """D-21: (gecerli_mi, neden)."""
    if kume["kac_seyirci"] >= 2: return False, "iki ya da daha çok seyircinin KRİTİK'i reddedilemez"
    kan = red.get("kanit") or {}; satir = (kan.get("ekran_satiri") or "").strip()
    if not satir: return False, "kanıt satırı yok"
    sno = kume["seyirciler"][0]
    r = next((x for x in raporlar if x["no"] == sno), {})
    persona = r.get("persona") or "ABC"[sno - 1] if 1 <= sno <= 3 else r.get("persona")
    metin = _paket_metni(film, kip, tur, persona)
    if satir not in metin: return False, "kanıt satırı seyircinin paketinde yok"
    for m in maskeler:
        if m and m in satir: return False, f"kanıt satırı maskeli adı içeriyor ({m})"
    zk = zaman_sn((kume.get("konum") or {}).get("zaman")); zs = _satir_zamani(metin, satir)
    if zk is not None and zs is not None and zs > zk: return False, "kanıt satırı kopukluk anından sonra"
    return True, "betik doğruladı"


# --- özet eşleşmesi ---------------------------------------------------------------------------------------------
def _olgular(film):
    h = json_oku(os.path.join(film, "HIKAYE.json"))
    if not isinstance(h, dict):
        try:
            import evren
            h = evren.film_hikaye(film) or {}
        except Exception: h = {}
    return h


def eslesme_hesapla(film, eslesmeler, hikaye):
    """{parti: {"tum": oran, "kritik": oran}} + eksik olgular + ekranda açılmamış sorular (seyirci medyanı)."""
    agir = {"bulundu": 1.0, "kismen": E("ozet_kismen_agirlik"), "yok": 0.0}
    olg = {o.get("id"): o for o in hikaye.get("anahtar_olgular") or [] if isinstance(o, dict) and o.get("id")}
    partiler = sorted({o.get("hikaye_partisi") or "P?" for o in olg.values()})
    oran = {p: {"tum": [], "kritik": []} for p in partiler}; eksik = {}; acilmamis = set()
    for e in eslesmeler:
        kar = {}
        for x in e.get("olgular") or []:
            if isinstance(x, dict) and x.get("id") in olg: kar[x["id"]] = agir.get(str(x.get("karar")).lower(), 0.0)
        for p in partiler:
            ids = [i for i, o in olg.items() if (o.get("hikaye_partisi") or "P?") == p]
            kids = [i for i in ids if olg[i].get("kritik")]
            if ids: oran[p]["tum"].append(sum(kar.get(i, 0.0) for i in ids) / len(ids))
            if kids: oran[p]["kritik"].append(sum(kar.get(i, 0.0) for i in kids) / len(kids))
        for i in olg:
            if kar.get(i, 0.0) == 0.0: eksik[i] = eksik.get(i, 0) + 1
        for q in e.get("sorular") or []:
            if isinstance(q, dict) and str(q.get("karar")).lower() == "yok": acilmamis.add(q.get("id"))
    sonuc = {p: {"tum": medyan(v["tum"]), "kritik": medyan(v["kritik"])} for p, v in oran.items()}
    n = len(eslesmeler) or 1
    return sonuc, sorted(i for i, c in eksik.items() if c * 2 > n), sorted(x for x in acilmamis if x)


# --- karar ------------------------------------------------------------------------------------------------------
def _onceki_kararlar(film, kip, tur):
    out = {}
    for t in range(1, tur):
        k = json_oku(os.path.join(film, "_RAPOR", f"SEYIRCI_KARAR_{kip.upper()}_t{t}.json"))
        if isinstance(k, dict) and (k.get("medyan") or {}).get("GENEL") is not None: out[t] = k["medyan"]["GENEL"]
    return out


def plato_mu(gecmis, simdi_genel):
    """İki tur üst üste GENEL artışı < max(0,5; seyirci_gurultu_std)."""
    esik = max(float(E("plato_genel_artis_min") or 0.5), float(E("seyirci_gurultu_std") or 0))
    seri = [gecmis[t] for t in sorted(gecmis)] + [simdi_genel]
    if len(seri) < 3 or None in seri[-3:]: return False, esik
    return (seri[-1] - seri[-2] < esik and seri[-2] - seri[-3] < esik), esik


def ilk2dk_ozet(film, kip, tur):
    k = os.path.join(film, "_RAPOR", "SEYIRCI", f"{kip}_ilk2dk_t{tur}")
    rs = raporlari_topla(k)
    surumler = {}
    for r in rs:
        s = str(r.get("surum") or "A"); surumler.setdefault(s, []).append(bool(r.get("ilk2dk_devam")))
    ozet = {s: {"evet": sum(v), "seyirci": len(v)} for s, v in surumler.items()}
    en_iyi = max(ozet, key=lambda s: (ozet[s]["evet"], -ord(s[0]))) if ozet else None
    return {"surumler": ozet, "secilen": en_iyi, "evet": ozet[en_iyi]["evet"] if en_iyi else 0,
            "seyirci": ozet[en_iyi]["seyirci"] if en_iyi else 0, "rapor_sayisi": len(rs)}


def tutma_egrisi(raporlar, sure_sn=None):
    dilim = float(E("tutma_egrisi_dilim_sn") or 60)
    kapanis = [zaman_sn(r.get("kapatma_ani")) for r in raporlar]
    son = sure_sn or max([z for z in kapanis if z] + [dilim * 4])
    n = len(raporlar) or 1; egri = []; t = 0.0
    while t <= son:
        kalan = sum(1 for z in kapanis if z is None or z > t)
        egri.append({"zaman_sn": int(t), "kalan_oran": round(kalan / n, 3)}); t += dilim
    olas = [r["devam_olasiligi"] for r in raporlar if r.get("devam_olasiligi") is not None]
    return {"egri": egri, "devam_olasiligi_medyan": medyan(olas)}


def seyirci_topla(film, kip="kagit", tur=1, gorev=None, merdiven=None, yol=None, asama=None):
    """Bir seyirci turunu birleştirir; SEYIRCI_KARAR + HS_<KIP> kapı raporu yazar. Karar sözlüğü döner."""
    film = os.path.abspath(film); K = kip.upper()
    sk = os.path.join(film, "_RAPOR", "SEYIRCI", f"{kip}_t{tur}")
    hepsi = raporlari_topla(sk)
    sema = [f"s{r['no']}: {h}" for r in hepsi for h in r["sema_hatalari"]]
    gecerli = [r for r in hepsi if not r["sema_hatalari"]]
    medyana = [r for r in gecerli if not r["donen"]]
    hikaye = _olgular(film)
    sahne_sira = {s.get("id"): i for i, s in enumerate(hikaye.get("sahneler") or []) if isinstance(s, dict)}
    olc, hedef, bayrak = [], [], []
    if len(medyana) < int(E("seyirci_gecerli_rapor_min") or 2):
        olc.append({"madde": "seyirci_rapor_sayisi", "seviye": "HATA", "olcu": len(medyana), "esik": E("seyirci_gecerli_rapor_min"),
                    "neden": "şema HATA'sı ya da eksik rapor"})
    for h in sema: olc.append({"madde": "seyirci_sema", "seviye": "HATA", "neden": h})
    med = {k: medyan([r["puanlar"][k] for r in medyana if r["puanlar"].get(k) is not None]) for k in OLCUTLER + ("GENEL",)}
    partiler = sorted({p for r in medyana for p in r["parti"]})
    parti_med = {p: medyan([r["parti"][p] for r in medyana if p in r["parti"]]) for p in partiler}
    kumeler = kopukluk_birlestir(medyana, sahne_sira)
    red = json_oku(os.path.join(sk, "KRITIK_RED.json"), []) or []
    maskeler = [k.get("ad") for k in (hikaye.get("karakterler") or {}).values() if isinstance(k, dict) and k.get("ad")]
    gecersiz = []
    for c in kumeler:
        if c["tur"] != "KRITIK": continue
        for x in red if isinstance(red, list) else []:
            ko = (x.get("konum") or {})
            if not (ko.get("sahne") == (c["konum"] or {}).get("sahne") or ko.get("plan") == (c["konum"] or {}).get("plan")): continue
            ok, neden = kritik_red_dogrula(film, kip, tur, c, x, medyana, maskeler)
            c.setdefault("red", []).append({"kanit": x.get("kanit"), "betik_dogruladi": ok, "neden": neden})
            if ok: c["gecersiz"] = True; gecersiz.append(c)
    kritik = [c for c in kumeler if c["tur"] == "KRITIK" and not c.get("gecersiz")]
    orta = [c for c in kumeler if c["tur"] == "ORTA"]
    es_rap = [json_oku(p, {}) or {} for p in sorted(glob.glob(os.path.join(sk, "e*_eslesme.json")))]
    eslesme, eksik_olgu, acilmamis = eslesme_hesapla(film, es_rap, hikaye)
    ilk2 = ilk2dk_ozet(film, kip, tur)
    gecmis = _onceki_kararlar(film, kip, tur)
    plato, plato_esik = plato_mu(gecmis, med["GENEL"]) if med["GENEL"] is not None else (False, None)
    tum_genel = dict(gecmis); tum_genel[tur] = med["GENEL"]
    en_iyi = max((t for t in tum_genel if tum_genel[t] is not None), key=lambda t: (tum_genel[t], t), default=tur)
    salinim = med["GENEL"] is not None and tum_genel.get(en_iyi) is not None and \
        tum_genel[en_iyi] - med["GENEL"] >= float(E("salinim_dusus") or 1)
    # --- kapı
    for c in kritik:
        olc.append({"madde": "kritik_kopukluk", "seviye": "HATA", "sahne": (c["konum"] or {}).get("sahne"),
                    "olcu": c["kac_seyirci"], "neden": "; ".join(n for n in c["nedenler"] if n)[:300]})
    if med["GENEL"] is not None and med["GENEL"] < E("seyirci_kapi_genel_min"):
        olc.append({"madde": "genel_kapi", "seviye": "HATA", "olcu": med["GENEL"], "esik": E("seyirci_kapi_genel_min")})
    for p, v in eslesme.items():
        if v["kritik"] is not None and v["kritik"] < E("ozet_eslesme_kritik_min"):
            olc.append({"madde": "kritik_olgu_eslesme", "seviye": "HATA", "parti": p, "olcu": round(v["kritik"], 3),
                        "esik": E("ozet_eslesme_kritik_min")})
    if not es_rap:
        olc.append({"madde": "ozet_eslesme", "seviye": "OLCULEMEDI", "neden": "eşleştirici raporu yok"})
    kapi_ok = not any(o["seviye"] == "HATA" for o in olc)
    # --- hedef
    def H(madde, olcu, esik, kapsam="FILM", **k):
        hedef.append(dict({"madde": madde, "seviye": "HATA", "hedef": True, "sahne": kapsam, "olcu": olcu, "esik": esik}, **k))
    if med["GENEL"] is not None and med["GENEL"] < E("seyirci_genel_esik"): H("genel_hedef", med["GENEL"], E("seyirci_genel_esik"))
    oh = E("seyirci_olcut_hedef") or {}
    for k in OLCUTLER:
        if med[k] is None: continue
        if med[k] < E("seyirci_olcut_min") or med[k] < (oh.get(k) or 0):
            H("olcut_hedef", med[k], max(E("seyirci_olcut_min"), oh.get(k) or 0), olcut=k)
    for p, g in parti_med.items():
        if g is not None and g < E("seyirci_genel_esik"): H("parti_genel_hedef", g, E("seyirci_genel_esik"), kapsam=p)
    orta_parti = {}
    for c in orta:
        s = (c["konum"] or {}).get("sahne"); p = next((x.get("hikaye_partisi") for x in hikaye.get("sahneler") or []
                                                     if isinstance(x, dict) and x.get("id") == s), None) or "FILM"
        orta_parti[p] = orta_parti.get(p, 0) + 1
    for p, n in orta_parti.items():
        if n > E("kopukluk_orta_max_parti"): H("orta_kopukluk", n, E("kopukluk_orta_max_parti"), kapsam=p)
    if ilk2["rapor_sayisi"] and ilk2["evet"] < E("ilk2dk_devam_evet_min"): H("ilk2dk", ilk2["evet"], E("ilk2dk_devam_evet_min"))
    elif not ilk2["rapor_sayisi"]: bayrak.append({"madde": "ilk2dk", "seviye": "OLCULEMEDI", "neden": "ilk 2 dk raporu yok"})
    for p, v in eslesme.items():
        if v["tum"] is not None and v["tum"] < E("ozet_eslesme_min"): H("olgu_eslesme", round(v["tum"], 3), E("ozet_eslesme_min"), kapsam=p)
    # --- bayraklar (bilgi; hat sürer)
    ilgi_vek = {}
    for r in medyana:
        for i in r["ilgi"]:
            ko = i.get("konum") or {}; anah = i.get("sahne") or ko.get("sahne") or ko.get("zaman_bas")
            if anah is not None and _sayi(i.get("puan")) is not None: ilgi_vek.setdefault(r["no"], {})[str(anah)] = _sayi(i["puan"])
    kor = []
    ks = sorted(ilgi_vek)
    for a in range(len(ks)):
        for b in range(a + 1, len(ks)):
            ortak_ = sorted(set(ilgi_vek[ks[a]]) & set(ilgi_vek[ks[b]]))
            rho = spearman([ilgi_vek[ks[a]][x] for x in ortak_], [ilgi_vek[ks[b]][x] for x in ortak_])
            if rho is not None: kor.append(rho)
    ilgi_kor = round(sum(kor) / len(kor), 3) if kor else None
    if ilgi_kor is not None and ilgi_kor < E("ilgi_korelasyon_min"):
        bayrak.append({"madde": "ilgi_korelasyon", "seviye": "BAYRAK", "olcu": ilgi_kor, "esik": E("ilgi_korelasyon_min")})
    egimler = [egim([r["parti"][p] for p in sorted(r["parti"])]) for r in medyana if len(r["parti"]) >= 2]
    egimler = [e for e in egimler if e is not None]
    konum_egim = round(medyan(egimler), 3) if egimler else None
    if konum_egim is not None and konum_egim < E("parca_konum_egim_bayrak"):
        bayrak.append({"madde": "parca_konum_yanliligi", "seviye": "BAYRAK", "olcu": konum_egim, "esik": E("parca_konum_egim_bayrak")})
    sik = {}
    for r in medyana:
        for s in r["sikilma"]:
            a = s.get("sahne") or (f"{int(zaman_sn(s.get('bas')) // 60)}. dk" if zaman_sn(s.get("bas")) is not None else None)
            if a: sik.setdefault(a, set()).add(r["no"])
    kesme = sorted(a for a, v in sik.items() if len(v) >= E("sikilma_ortak_isaret_min"))
    for a in kesme: bayrak.append({"madde": "kesme_adayi", "seviye": "BAYRAK", "sahne": a, "olcu": len(sik[a])})
    if plato: bayrak.append({"madde": "plato", "seviye": "BAYRAK", "olcu": med["GENEL"], "esik": plato_esik})
    if salinim: bayrak.append({"madde": "salinim", "seviye": "BAYRAK", "olcu": med["GENEL"], "en_iyi_tur": en_iyi})
    hedef_ok = not hedef
    merdiven_kostu = merdiven is not None
    if not kapi_ok: sonuc = "HATA"
    elif hedef_ok: sonuc = "GEC" if not bayrak else "BAYRAK"
    elif plato and merdiven_kostu: sonuc = "BAYRAK"
    else: sonuc = "KISMI"
    hedef_alti = kapi_ok and not hedef_ok
    personalar = {}
    for r in medyana:
        personalar.setdefault(r.get("persona") or "?", []).append(r["puanlar"]["GENEL"])
    karar = {"_surum": 1, "kip": kip, "tur": tur, "seyirci": len(medyana), "donen_seyirci": [r["no"] for r in gecerli if r["donen"]],
             "medyan": med, "parti_medyan": parti_med,
             "kopukluk": [{"tur": c["tur"], "konum": c["konum"], "kac_seyirci": c["kac_seyirci"], "seyirciler": c["seyirciler"],
                           "gecersiz": bool(c.get("gecersiz")), "red": c.get("red"), "nedenler": c["nedenler"]} for c in kumeler],
             "kritik_gecerli": len(kritik), "kritik_gecersiz_sayilan": len(gecersiz), "orta": len(orta), "orta_parti": orta_parti,
             "sikilma": {a: sorted(v) for a, v in sik.items()}, "kesme_adaylari": kesme,
             "eslesme": eslesme, "eksik_olgular": eksik_olgu, "ekranda_acilmamis_sorular": acilmamis,
             "ilk2dk": ilk2, "ilgi_korelasyon": ilgi_kor, "parca_konum_egim": konum_egim,
             "personalar": {p: medyan([g for g in v if g is not None]) for p, v in personalar.items()},
             "tutma": tutma_egrisi(medyana, None), "plato": plato, "plato_esik": plato_esik, "gecmis_genel": tum_genel,
             "en_iyi_tur": en_iyi, "salinim": salinim, "kapi": kapi_ok, "hedef": hedef_ok, "hedef_alti": hedef_alti,
             "sonuc": sonuc, "gecti": sonuc in ("GEC", "BAYRAK"),
             "neden": [f"{o['madde']} {o.get('olcu')} (eşik {o.get('esik')})" for o in olc + hedef if o["seviye"] == "HATA"],
             "merdiven_onerisi": ("yapimci·doktor" if (plato or (tur >= 3 and len(tum_genel) >= 2 and med["GENEL"] is not None and
                                  med["GENEL"] - tum_genel.get(tur - 1, med["GENEL"]) < float(E("doktor_tetik_iyilesme") or 0.5)))
                                  and not hedef_ok else None),
             "_uretim": {"arac_surum": SURUM, "gorev": gorev, "zaman": None}}
    karar["_uretim"]["zaman"] = kapi.simdi()
    atomik_yaz(os.path.join(film, "_RAPOR", f"SEYIRCI_KARAR_{K}_t{tur}.json"), karar)
    girdi = [os.path.relpath(r["yol"], film) for r in hepsi]
    ek = {"karar": f"_RAPOR/SEYIRCI_KARAR_{K}_t{tur}.json", "medyan": med, "plato": plato, "en_iyi_tur": en_iyi,
          "hedef_alti": hedef_alti and sonuc != "KISMI", "kapi_saglandi": kapi_ok}
    if sonuc == "BAYRAK" and hedef:                  # plato + merdiven koştu: hedef maddeleri BAYRAK olarak kalır (hedef_alti)
        hedef = [dict(h, seviye="BAYRAK") for h in hedef]
    ol = olc + (hedef if kapi_ok else []) + bayrak
    kapi_kod = f"HS_{K}" if K != "ILK2DK" else "HS_ILK2DK"
    yol = yol or os.path.join(film, "_RAPOR", f"{kapi_kod}_FILM_t{tur}.json")
    kapi_yaz(film, kapi_kod, "FILM", ol, tur, asama or {"kagit": "A06", "plan": "A07e", "animatik": "A12", "kesit": "A14a",
                                                    "kurgu": "A16"}.get(kip), gorev, girdi, ek=ek, yol=yol, sonuc=sonuc)
    karar["rapor"] = os.path.relpath(yol, film)
    return karar


def ilk2dk_topla(film, kip="kagit", tur=1, gorev=None, yol=None):
    film = os.path.abspath(film)
    o = ilk2dk_ozet(film, kip, tur); olc = []
    if not o["rapor_sayisi"]: olc.append({"madde": "ilk2dk", "seviye": "OLCULEMEDI", "neden": "rapor yok"})
    elif o["evet"] < E("ilk2dk_devam_evet_min"):
        olc.append({"madde": "ilk2dk", "seviye": "HATA", "olcu": o["evet"], "esik": E("ilk2dk_devam_evet_min"), "surum": o["secilen"]})
    else: olc.append({"madde": "ilk2dk", "seviye": "GEC", "olcu": o["evet"]})
    yol = yol or os.path.join(film, "_RAPOR", "HS_ILK2DK_FILM.json")
    return kapi_yaz(film, "HS_ILK2DK", "FILM", olc, tur, "A06", gorev, ek={"ilk2dk": o}, yol=yol)[1]


def plan_elestiri_topla(film, tur=1, gorev=None, yol=None):
    """A07d: _RAPOR/PLAN_ELESTIRI/{pe,up,su}_t<tur>_<i>.json → KRİTİK 0 (HATA), ORTA ≤ kopukluk_orta_max_parti / parti (HATA)."""
    film = os.path.abspath(film); olc, girdi, kum = [], [], []
    komsu = E("kritik_birlestirme_komsu")
    for p in sorted(glob.glob(os.path.join(film, "_RAPOR", "PLAN_ELESTIRI", f"*_t{tur}_*.json"))):
        j = json_oku(p); girdi.append(os.path.relpath(p, film))
        if not isinstance(j, dict): olc.append({"madde": "rapor_bozuk", "seviye": "HATA", "neden": os.path.basename(p)}); continue
        for b in j.get("bulgular") or j.get("kopukluklar") or []:
            if not isinstance(b, dict): continue
            t = str(b.get("tur") or b.get("seviye") or "ORTA").upper().replace("İ", "I")
            pl = b.get("plan") if isinstance(b.get("plan"), int) else (b.get("konum") or {}).get("plan")
            c = next((c for c in kum if c["tur"] == t and pl is not None and c["plan"] is not None and abs(c["plan"] - pl) <= komsu), None)
            if c is None: c = {"tur": t, "plan": pl, "parti": b.get("parti"), "kaynak": [], "neden": b.get("neden")}; kum.append(c)
            c["kaynak"].append(os.path.basename(p))
    if not girdi: olc.append({"madde": "plan_elestiri", "seviye": "OLCULEMEDI", "neden": "rapor yok"})
    orta = {}
    for c in kum:
        if c["tur"] == "KRITIK": olc.append({"madde": "kritik", "seviye": "HATA", "plan": c["plan"], "neden": c["neden"]})
        elif c["tur"] == "ORTA": orta[c["parti"] or "FILM"] = orta.get(c["parti"] or "FILM", 0) + 1
    for p, n in orta.items():
        if n > E("kopukluk_orta_max_parti"): olc.append({"madde": "orta", "seviye": "HATA", "sahne": str(p), "olcu": n,
                                                         "esik": E("kopukluk_orta_max_parti")})
    yol = yol or os.path.join(film, "_RAPOR", f"PLAN_ELESTIRI_FILM_t{tur}.json")
    return kapi_yaz(film, "PLAN_ELESTIRI", "FILM", olc, tur, "A07d", gorev, girdi, ek={"kumeler": kum}, yol=yol)[1]


def _v2_main(a):
    def arg(ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v
    import ortak
    film = arg("--film")
    if not film: print("!! --film gerekli"); return 1
    if not os.path.isdir(film):
        try: film = os.path.join(ortak.yollar()["filmler"], film)
        except ortak.YolYok as e: print("!!", e); return 4
    g = gorev_baglami(arg("--tur"))
    yol = os.path.join(film, g["rapor"]) if g.get("rapor") else None
    kip = arg("--kip", "kagit")
    if "--plan" in a: r = plan_elestiri_topla(film, g["tur_no"], g["id"], yol)
    elif a[0] == "ilk2dk-topla": r = ilk2dk_topla(film, kip, g["tur_no"], g["id"], yol)
    else: r = seyirci_topla(film, kip, g["tur_no"], g["id"], g.get("merdiven"), yol, g.get("asama"))
    print(json.dumps({k: r.get(k) for k in ("sonuc", "medyan", "kapi", "hedef", "plato", "neden", "rapor") if k in r},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and (a[0] in ("seyirci-topla", "ilk2dk-topla") or "--plan" in a): sys.exit(_v2_main(a))
    sys.exit(main(a))
