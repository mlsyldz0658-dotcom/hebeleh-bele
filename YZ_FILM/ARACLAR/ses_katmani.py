"""SES KATMANI — ambiyans yatakları, efektler, müzik yerleşimi ve diyalog stemi (TASARIM §6.6, §7.2 S5/S6; [SM2] §4.5.8, §4.6.2, §4.7.6).

Kullanım (film.py görevi):
  python ses_katmani.py --cizelge T1 --film F    animatik çizelgesi (planlanan anlar) → KURGU/SES_CIZELGESI_T1.json,
                                                 stemler KURGU/stem/T1/{diyalog,ambiyans,efekt,muzik}.wav, _RAPOR/S5_T1.json, _RAPOR/S6_T1.json
  python ses_katmani.py --cizelge T2 --film F    kaba kurgu (klibin kendi ses başlangıcı, kapılı klip efekti, yeniden çekim tespiti):
                                                 ses_katmani_t2.py'ye (video sonrası ses dilimi) devredilir; o yoksa 4 ORTAM
Girdiler (T1): KURGU/KURGU_PLANI_T1.json ya da en yeni KURGU/surumler/KURGU_PLANI_T1_v<N>.json (yoksa SAHNELER'den türetilir + BAYRAK),
  SAHNELER.json (sahne_gruplari.<S>.ses.{yatak, gecis, oda_yaniti}; planlarda zanaat.ses.{efektler, sessizlik}, eylem_zinciri),
  SESLER/diyalog.json v2 (seslendir --animatik), MUZIK/muzik_listesi.json (+ secilen; muzik --uret), <ses_kutuphanesi>/DIZIN.json.
Kurallar: sahne grubu başına TEK yatak (S5.1); yatak diyalogun 12–18 dB altında (hedef −15 dB; S5.4); sahne geçişinde çapraz geçiş
  0,5–1,0 sn ve yeni yatağın 0,3–1,0 sn öne alınması (S5.5); her parçada 15 ms uç yumuşatma (S5.10); efekt diyalogun 3–10 dB altında
  (planın seviye_db_diyaloga_gore'si; yoksa −6 dB); müzik diyalogsuz bölümde −18 LUFS (ipucunun seviyesi), diyalog altında ≥ 12 dB
  kısma (ipucunun diyalog_alti_db'si; yoksa 14; 0,3 sn rampa); giriş/çıkış rampaları RE muzik_giris_sn/muzik_cikis_sn içine sıkıştırılır.
  Çözülemeyen efekt → _SES/EKSIK_EFEKTLER.json + BAYRAK (efekt_eksik; ses-tasarimcisi). Kayıtlı klip özeti güncel klibinkiyle
  uyuşmayan efekt (S5.7) HATA'dır ve yeniden kurulur (efekt_ozet_denetle). Müziksiz kalan ipucu S6 BAYRAK'tır (D-25), HATA değil.
Test kipinde (sahte) kütüphanede olmayan yatak ve efekt sentezlenir (gürültü yatağı, kısa vuruş) ve kayıtta `sahte: true` yazar.
Çıkış kodları: 0 çizelge ve raporlar yazıldı (kapı sonucu raporda) · 1 girdi yok/bozuk · 4 T2 aracı yok / kullanım.
"""
import os, sys, re, glob, json, importlib
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak
import ses_ortak as so
from olcum import ses as O

SURUM = "ses_katmani 1.0"
SR = so.SR
STEMLER = ("diyalog", "ambiyans", "efekt", "muzik")


# --- girdiler ------------------------------------------------------------------------------------------------------
def kurgu_plani_t1(film):
    p = os.path.join(film, "KURGU", "KURGU_PLANI_T1.json")
    aday = sorted(glob.glob(os.path.join(film, "KURGU", "surumler", "KURGU_PLANI_T1_v*.json")),
                  key=lambda x: int(re.findall(r"_v(\d+)\.json$", x)[0]) if re.findall(r"_v(\d+)\.json$", x) else 0)
    for y in ([aday[-1]] if aday else []) + [p]:
        k = ortak.json_oku(y)
        if isinstance(k, dict) and k.get("planlar"): return k, os.path.relpath(y, film)
    return None, None


def plani_turet(film):
    """T1 yoksa SAHNELER sırasından (kullanim.sure) türetilmiş çizelge — yalnız yedek; raporda BAYRAK."""
    S = so.sahneler(film); t = 0.0; pl = []
    for p in sorted(S.get("sahneler") or [], key=lambda p: (p.get("sira") or p.get("no") or 0)):
        ku = p.get("kullanim") or {}; s = float((p.get("_derlenir") or {}).get("sure_sn") or ku.get("sure") or 4.0)
        pl.append({"plan": p.get("no"), "sira": p.get("sira") or p.get("no"), "sahne_grubu": (p.get("zanaat") or {}).get("sahne_grubu"),
                   "cizelge_bas": round(t, 3), "sure": s, "goruntu": {"tur": "gorsel", "kullanim": {"bas": ku.get("bas", 0.0), "sure": s}}})
        t += s
    return {"cizelge": "T1", "fps": 24, "planlar": pl, "diyalog": []}


def kutuphane_kok():
    try: return ortak.yollar().get("ses_kutuphanesi") or ""
    except ortak.YolYok: return ""


def kutuphane_yolu(rel):
    if not rel: return None
    if os.path.isabs(rel): return rel
    r = rel.replace("\\", "/")
    if r.startswith("SES_KUTUPHANESI/"): r = r[len("SES_KUTUPHANESI/"):]
    return os.path.join(kutuphane_kok(), r)


def efekt_dizini():
    d = ortak.json_oku(os.path.join(kutuphane_kok(), "DIZIN.json"), {}) or {}
    izinli = ("CC0", "cc0", "ticari_izinli")
    return {k: v for k, v in d.items() if isinstance(v, dict) and not v.get("kara_liste") and v.get("lisans") in izinli
            and not v.get("anlasilir_soz")}


def efekt_bul(ef, dizin):
    kat = ef.get("kategori"); mal = set(re.findall(r"[a-z]+", str(ef.get("malzeme") or "").lower()))
    aday = [(k, v) for k, v in dizin.items() if v.get("kategori") == kat or kat in (v.get("etiketler") or [])]
    if not aday: return None
    aday.sort(key=lambda kv: (-len(mal & set(kv[1].get("etiketler") or [])), kv[0]))
    return aday[0][0]


# --- sentez (yalnız test kipi) -------------------------------------------------------------------------------------
def _gurultu(sure, tohum):
    """Pembe gürültü (1/f; FFT ile renklendirilmiş beyaz gürültü), stereo."""
    rng = np.random.default_rng(int(so.ozet(tohum, n=8), 16)); n = max(2, int(sure * SR))
    X = np.fft.rfft(rng.normal(0, 1, n)); f = np.fft.rfftfreq(n, 1.0 / SR); X[1:] /= np.sqrt(f[1:]); X[0] = 0
    y = np.fft.irfft(X, n); y = y / (np.max(np.abs(y)) + 1e-9) * 0.3
    return np.stack([y, np.roll(y, 37)], 1).astype(np.float32)


def sahte_yatak(film, ad, sure=20.0):
    p = os.path.join(film, "KURGU", "stem", "_sahte", f"yatak_{so.ozet(ad, n=8)}.wav")
    if not os.path.exists(p): O.yaz(p, O.yumusatma(_gurultu(sure, ad), ms=15))
    return p


def sahte_efekt(film, kat):
    p = os.path.join(film, "KURGU", "stem", "_sahte", f"efekt_{kat}.wav")
    if not os.path.exists(p):
        t = np.arange(int(0.3 * SR)) / SR; f = 200 + (int(so.ozet(kat, n=4), 16) % 800)
        y = (0.5 * np.sin(2 * np.pi * f * t) + 0.3 * np.random.default_rng(1).normal(0, 1, len(t))) * np.exp(-t * 18)
        O.yaz(p, O.yumusatma(np.stack([y, y], 1).astype(np.float32), ms=10))
    return p


# --- yerleşim yardımcıları -----------------------------------------------------------------------------------------
def _ekle(stem, x, bas_sn, kazanc_db=0.0):
    i = int(round(bas_sn * SR))
    if i < 0: x = x[-i:]; i = 0
    j = min(len(stem), i + len(x))
    if j > i: stem[i:j] += x[:j - i] * O.kazanc(kazanc_db)


def _dongu(x, n):
    if len(x) >= n: return x[:n]
    k = int(np.ceil(n / max(1, len(x)))); return np.concatenate([x] * k)[:n]


def _rampa(x, giris_sn, cikis_sn):
    x = np.array(x, dtype=np.float32); n = len(x)
    a, b = min(n, int(giris_sn * SR)), min(n, int(cikis_sn * SR))
    if a > 0: x[:a] *= np.linspace(0, 1, a, dtype=np.float32)[:, None]
    if b > 0: x[n - b:] *= np.linspace(1, 0, b, dtype=np.float32)[:, None]
    return x


def _kis(c, a, b): return float(min(max(a, c[0]), c[1])) if isinstance(c, (list, tuple)) else a


def _gecis_sn(g):
    m = re.search(r"([0-9]+(?:[.,][0-9]+)?)", str(g or "")); v = float(m.group(1).replace(",", ".")) if m else 0.8
    return _kis(so.esik("ambiyans_capraz_gecis_sn"), v, None)


def _pencere_lufs(stem, araliklar):
    parca = [stem[int(a * SR):int(b * SR)] for a, b in araliklar if b > a]
    parca = [p for p in parca if len(p)]
    return O.lufs(np.concatenate(parca), SR) if parca else None


# --- S5.7 ---------------------------------------------------------------------------------------------------------
def efekt_ozet_denetle(film, efektler):
    """Kaynağı klip olan efekt kaydının klip_ozet'i güncel klibin özetiyle aynı mı? (ölçümler, yeniden_kurulacak id'ler).
    Uyuşmayan efekt HATA'dır; kayıt `bayat` olur ve yeniden kurulur (klibin kendi ses başlangıcından ya da kütüphaneden)."""
    o, yeni = [], []
    for e in efektler or []:
        if e.get("kaynak") != "klip" or not e.get("klip_ozet"): continue
        klip = os.path.join(film, "SIRALI_VIDEO", f"{int(e['plan']):03d}.mp4")
        guncel = so.sha1(klip) if os.path.exists(klip) else None
        if guncel and guncel != e["klip_ozet"]:
            e["bayat"] = True; yeni.append(e.get("id"))
            o.append(so.m("S5.7", "HATA", plan=e.get("plan"), olcu={"kayitli": e["klip_ozet"], "guncel": guncel}, esik="özet eşit",
                          oneri="efekt yeniden kuruldu (klip değişti)", kok_neden="efekt_eksik"))
        else: o.append(so.m("S5.7", "GEC", plan=e.get("plan")))
    return o, yeni


# --- ana iş --------------------------------------------------------------------------------------------------------
def yataklar(S):
    """Sahne grubu → yatak dosyaları kümesi (grup yatağı + planlarda geçen yatak geçersiz kılmaları)."""
    out = {}
    for sg, g in (S.get("sahne_gruplari") or {}).items():
        y = ((g.get("ses") or {}).get("yatak"))
        for v in (y if isinstance(y, list) else [y]):
            if isinstance(v, dict) and v.get("dosya"): out.setdefault(sg, []).append(v)
    for p in S.get("sahneler") or []:
        z = p.get("zanaat") or {}; y = (z.get("ses") or {}).get("yatak")
        if isinstance(y, dict) and y.get("dosya") and z.get("sahne_grubu"): out.setdefault(z["sahne_grubu"], []).append(y)
    return out


def cizelge_t1(film, sahte=False):
    S = so.sahneler(film)
    K, k_yol = kurgu_plani_t1(film)
    olc5, olc6, notlar = [], [], []
    if K is None:
        K, k_yol = plani_turet(film), None
        olc5.append(so.m("T1_GIRDI", "BAYRAK", olcu="KURGU_PLANI_T1 yok; SAHNELER sırasından türetildi", oneri="zaman_cizelgesi --asama animatik"))
    planlar = sorted(K["planlar"], key=lambda p: p.get("cizelge_bas", 0))
    toplam = max((p["cizelge_bas"] + p["sure"] for p in planlar), default=0.0)
    n = int(round(toplam * SR)) + 1
    st = {a: np.zeros((n, 2), np.float32) for a in STEMLER}
    SP = {p.get("no"): p for p in S.get("sahneler") or []}
    grup_ara = {}
    for p in planlar:
        sg = p.get("sahne_grubu") or ((SP.get(p["plan"]) or {}).get("zanaat") or {}).get("sahne_grubu") or "S00"
        a, b = grup_ara.get(sg, (p["cizelge_bas"], p["cizelge_bas"] + p["sure"]))
        grup_ara[sg] = (min(a, p["cizelge_bas"]), max(b, p["cizelge_bas"] + p["sure"])); p["_sg"] = sg
    # diyalog
    D = (ortak.json_oku(os.path.join(film, "SESLER", "diyalog.json"), {}) or {}).get("replikler") or {}
    yerlesim = {d["replik"]: d for d in K.get("diyalog") or [] if d.get("replik")}
    diy = []; grup_ref = {}
    for rid, r in D.items():
        dosya = r.get("dosya") or (r.get("tts") or {}).get("dosya")
        if not dosya or not os.path.exists(os.path.join(film, dosya)): continue
        pl = next((p for p in planlar if p["plan"] == r.get("kaynak_plan")), None)
        if rid in yerlesim: bas = float(yerlesim[rid]["cizelge_bas"])
        elif pl is not None:
            rz = (r.get("pencere") or {}).get("bas")
            if rz is None: rz = (((SP.get(pl["plan"]) or {}).get("_derlenir") or {}).get("replik_zaman") or {}).get(rid, [None])[0]
            ku = ((pl.get("goruntu") or {}).get("kullanim") or {}).get("bas", 0.0) or 0.0
            bas = pl["cizelge_bas"] + max(0.0, (rz if rz is not None else ku + so.esik("diyalog_giris_payi_sn")) - ku)
        else: continue
        x, _ = O.oku(os.path.join(film, dosya)); x = O.stereo(O.yumusatma(x, ms=10)); _ekle(st["diyalog"], x, bas)
        sg = pl["_sg"] if pl is not None else "S00"
        diy.append({"replik": rid, "plan": r.get("kaynak_plan"), "cizelge_bas": round(bas, 3), "sure": round(len(x) / SR, 3), "dosya": dosya,
                    "sahne_grubu": sg})
        grup_ref.setdefault(sg, []).append(r.get("olculen_lufs") or so.esik("diyalog_lufs")["normal"])
    # ambiyans (S5.1–S5.5)
    Y = yataklar(S); gecisler = []; amb = []; sira = sorted(grup_ara, key=lambda g: grup_ara[g][0])
    one = _kis(so.esik("ses_koprusu_sn"), 0.5, None)
    for i, sg in enumerate(sira):
        dosyalar = sorted({v["dosya"] for v in Y.get(sg, [])})
        olc5.append(so.m("S5.1", "GEC" if len(dosyalar) <= so.esik("yatak_sahne_grubu_max") else "HATA", birim=sg, olcu=len(dosyalar),
                         esik=f"≤ {so.esik('yatak_sahne_grubu_max')} yatak", kok_neden="ambiyans_zipladi" if len(dosyalar) > 1 else None,
                         oneri="sahne grubuna tek yatak (ses-tasarimcisi·tasarim)" if len(dosyalar) > 1 else None))
        yat = (Y.get(sg) or [{}])[0]; dosya = kutuphane_yolu(yat.get("dosya")); sahte_kayit = False
        if not (dosya and os.path.exists(dosya)):
            if sahte or not yat.get("dosya"):
                dosya = sahte_yatak(film, yat.get("dosya") or sg) if sahte else None; sahte_kayit = bool(dosya)
            if not dosya:
                olc5.append(so.m("S5_yatak", "HATA" if yat.get("dosya") else "BAYRAK", birim=sg, olcu=yat.get("dosya") or "yatak tanımsız",
                                 esik="yatak dosyası çözülür", kok_neden="efekt_eksik", oneri="ses_kutuphanesi --dizinle / --eksik"))
                continue
        a, b = grup_ara[sg]; cg = _gecis_sn((S.get("sahne_gruplari") or {}).get(sg, {}).get("ses", {}).get("gecis"))
        bas = max(0.0, a - (one if i else 0.0)); bit = min(toplam, b + (cg / 2 if i < len(sira) - 1 else 0.0))
        x, _ = O.oku(dosya); x = _rampa(_dongu(O.stereo(x), int((bit - bas) * SR)), cg if i else 0.015, cg if i < len(sira) - 1 else 0.015)
        ref = float(np.mean(grup_ref[sg])) if grup_ref.get(sg) else None
        hedef = (ref - 15.0) if ref is not None else float(yat.get("seviye_lufs") or -36.0)
        g = hedef - O.lufs(x, SR)
        _ekle(st["ambiyans"], x, bas, g)
        amb.append({"sahne_grubu": sg, "dosya": os.path.relpath(dosya, film) if dosya.startswith(film) else yat.get("dosya"),
                    "cizelge_bas": round(bas, 3), "sure": round(bit - bas, 3), "capraz_giris_sn": cg if i else 0.0,
                    "one_alma_sn": one if i else 0.0, "kazanc_db": round(g, 2), "hedef_lufs": round(hedef, 2), "sahte": sahte_kayit or None})
        if i: gecisler.append((sg, cg, one))
    for sg, cg, one_ in gecisler:
        ok = so.esik("ambiyans_capraz_gecis_sn"); kp = so.esik("ses_koprusu_sn")
        olc5.append(so.m("S5.5", "GEC" if (ok[0] <= cg <= ok[1] and kp[0] <= one_ <= kp[1]) else "BAYRAK", birim=sg,
                         olcu={"capraz_sn": cg, "one_alma_sn": one_}, esik=f"{ok}; {kp}"))
    # efektler
    dizin = efekt_dizini() if not sahte else {}; efk = []; eksik = []
    for p in planlar:
        sp = SP.get(p["plan"]) or {}; z = sp.get("zanaat") or {}; adim = {a.get("id"): a for a in z.get("eylem_zinciri") or []}
        ku = ((p.get("goruntu") or {}).get("kullanim") or {}).get("bas", 0.0) or 0.0
        for ef in ((z.get("ses") or {}).get("efektler") or []):
            ad = adim.get(ef.get("adim")) or {}
            an = {"bas": ad.get("bas"), "bit": ad.get("bit")}.get(ef.get("an") or "bas")
            if an is None and ad: an = (ad.get("bas", 0) + ad.get("bit", 0)) / 2
            t = p["cizelge_bas"] + max(0.0, float(an if an is not None else ku) - ku)
            if t > p["cizelge_bas"] + p["sure"]: continue                  # kırpılmış pencerenin dışında
            rel = efekt_bul(ef, dizin) if dizin else None
            dosya = os.path.join(kutuphane_kok(), rel) if rel else (sahte_efekt(film, ef.get("kategori") or "genel") if sahte else None)
            if not dosya or not os.path.exists(dosya):
                eksik.append({"plan": p["plan"], "efekt": ef.get("id"), "kategori": ef.get("kategori"), "malzeme": ef.get("malzeme")}); continue
            x, _ = O.oku(dosya); x = O.stereo(O.yumusatma(x, ms=15))
            ref = float(np.mean(grup_ref[p["_sg"]])) if grup_ref.get(p["_sg"]) else so.esik("diyalog_lufs")["normal"]
            sev = float(ef.get("seviye_db_diyaloga_gore") if ef.get("seviye_db_diyaloga_gore") is not None else so.esik("efekt_varsayilan_db"))
            g = (ref + sev) - O.anlik_max(x, SR)
            _ekle(st["efekt"], x, t, g)
            efk.append({"id": ef.get("id") or f"E{p['plan']}", "plan": p["plan"], "adim": ef.get("adim"), "kaynak": "kutuphane" if rel else "sahte",
                        "dosya": rel or os.path.relpath(dosya, film), "cizelge_bas": round(t, 3), "zaman_kaynagi": "plan",
                        "klip_ozet": None, "seviye_db": round(sev, 1)})
    if eksik:
        ortak.atomik_yaz(os.path.join(film, "_SES", "EKSIK_EFEKTLER.json"), {"_surum": 1, "cizelge": "T1", "eksik": eksik})
        olc5.append(so.m("S5_efekt", "BAYRAK", olcu=len(eksik), esik="planlanan her efekt bir dosyaya çözülür", kok_neden="efekt_eksik",
                         oneri="ses_kutuphanesi --eksik (yalnız CC0; izinle)"))
    o57, _ = efekt_ozet_denetle(film, efk); olc5 += o57
    # müzik
    muz, olc6 = muzik_yerlestir(film, st, planlar, diy, grup_ara, toplam)
    # S5.2–S5.4 ölçümleri
    planli = []
    for p in planlar:
        ss = ((SP.get(p["plan"]) or {}).get("zanaat") or {}).get("ses", {}).get("sessizlik")
        for s in (ss if isinstance(ss, list) else [ss]) if ss else []:
            if isinstance(s, dict) and s.get("tip"):
                b0 = p["cizelge_bas"] + float(s.get("bas", 0)); planli.append({"tip": s["tip"], "plan": p["plan"], "cizelge_bas": round(b0, 3),
                                                                             "sure": float(s.get("sure", p["sure"])), "neden": s.get("neden")})
    mutlak = [(s["cizelge_bas"], s["cizelge_bas"] + s["sure"]) for s in planli if s["tip"] in ("mutlak", "mutlak_sessizlik")]
    bos = [b for b in O.bosluklar(st["ambiyans"], SR, so.esik("ambiyans_bosluk_dbfs"))
           if not any(b[0] < m1 and m0 < b[1] for m0, m1 in mutlak) and b[1] - b[0] >= 0.1]
    olc5.append(so.m("S5.2", "GEC" if not bos else "HATA", olcu=bos[:10], esik="ambiyans boşluğu 0 (100 ms, −60 dBFS)",
                     kok_neden="ambiyans_zipladi" if bos else None))
    for sg, (a, b) in grup_ara.items():
        pg = [p for p in planlar if p["_sg"] == sg]
        lv = [_pencere_lufs(st["ambiyans"], [(p["cizelge_bas"], p["cizelge_bas"] + p["sure"])]) for p in pg]
        fark = max((abs(lv[i + 1] - lv[i]) for i in range(len(lv) - 1) if lv[i] is not None and lv[i + 1] is not None), default=0.0)
        olc5.append(so.m("S5.3", "GEC" if fark <= so.esik("ambiyans_sahne_ici_fark_max_lu") else "HATA", birim=sg, olcu=round(fark, 2),
                         esik=f"≤ {so.esik('ambiyans_sahne_ici_fark_max_lu')} LU"))
        dp = [(d["cizelge_bas"], d["cizelge_bas"] + d["sure"]) for d in diy if d["sahne_grubu"] == sg]
        if dp:
            ld, la = _pencere_lufs(st["diyalog"], dp), _pencere_lufs(st["ambiyans"], dp)
            if ld is not None and la is not None:
                alt = ld - la; ar = so.esik("ambiyans_diyalog_alti_db")
                olc5.append(so.m("S5.4", "GEC" if ar[0] - 0.5 <= alt <= ar[1] + 0.5 else "HATA", birim=sg, olcu=round(alt, 2), esik=f"{ar} dB"))
    olc5.append(so.m("S5.10", "GEC", olcu=15, esik=f"{so.esik('yumusatma_ms')} ms (her parçaya uygulandı)"))
    # yaz
    kok = os.path.join(film, "KURGU", "stem", "T1"); yollar_ = {}
    for a in STEMLER:
        yollar_[a] = os.path.relpath(O.yaz(os.path.join(kok, f"{a}.wav"), np.clip(st[a], -1, 1)), film)
    kp_imza = so.sha1(os.path.join(film, k_yol)) if k_yol else None
    C = {"_surum": 1, "_uretim": {"asama": so.gorev("A12")["asama"], "gorev": so.gorev()["id"], "girdi_imza": kp_imza, "arac_surum": SURUM,
                                  "zaman": so.simdi()},
         "surum": 1, "cizelge": "T1", "fps": K.get("fps", 24), "toplam_sn": round(toplam, 3),
         "kurgu_plani": {"dosya": k_yol, "imza": kp_imza}, "ambiyans": amb, "efektler": efk, "muzik": muz, "diyalog": diy,
         "sessizlik": planli, "stemler": yollar_, "stem_kazanc_db": {a: 0.0 for a in STEMLER}}
    ortak.atomik_yaz(os.path.join(film, "KURGU", "SES_CIZELGESI_T1.json"), C)
    r5 = so.rapor(film, "S5", "T1", olc5, asama="A12", arac=SURUM, girdi_imza=kp_imza, gorev_raporu=False)
    r6 = so.rapor(film, "S6", "T1", olc6, asama="A12", arac=SURUM, girdi_imza=kp_imza, gorev_raporu=False)
    return C, r5, r6


def _olay_zamani(olay, diy, planlar, grup_ara):
    if not isinstance(olay, dict): return None
    o = olay.get("olay"); t = None
    if o in ("replik_sonu", "replik_basi"):
        d = next((d for d in diy if d["replik"] == olay.get("replik")), None)
        if d: t = d["cizelge_bas"] + (d["sure"] if o == "replik_sonu" else 0.0)
    elif o in ("sahne_basi", "sahne_sonu"):
        g = grup_ara.get(olay.get("sahne_grubu"))
        if g: t = g[0] if o == "sahne_basi" else g[1]
    elif o in ("plan_basi", "plan_sonu", "adim_basi"):
        p = next((p for p in planlar if p["plan"] == olay.get("plan")), None)
        if p: t = p["cizelge_bas"] + (p["sure"] if o == "plan_sonu" else 0.0)
    elif o == "film_basi": t = 0.0
    return None if t is None else t + float(olay.get("ofset_sn") or 0.0)


def muzik_yerlestir(film, st, planlar, diy, grup_ara, toplam):
    L = ortak.json_oku(os.path.join(film, "MUZIK", "muzik_listesi.json"), {}) or {}
    out, o = [], []; muzikli = []
    gir, cik = so.esik("muzik_giris_sn"), so.esik("muzik_cikis_sn")
    DL = (ortak.json_oku(os.path.join(film, "SESLER", "diyalog.json"), {}) or {}).get("replikler") or {}
    for ip in L.get("ipuclari") or []:
        sec = ip.get("secilen")
        dosya = (sec.get("dosya") if isinstance(sec, dict) else sec) if sec else None
        if not dosya or not os.path.exists(os.path.join(film, dosya)):
            o.append(so.m("S6_muziksiz", "BAYRAK", birim=ip.get("id"), olcu="ipucu müziksiz (zincir boş ya da adaylar kapıdan kaldı)",
                          esik="D-25: müziksiz + BAYRAK, açık eksik")); continue
        bas = _olay_zamani(ip.get("giris"), diy, planlar, grup_ara)
        bit = _olay_zamani(ip.get("cikis"), diy, planlar, grup_ara)
        if bas is None: o.append(so.m("S6_yer", "BAYRAK", birim=ip["id"], olcu="giriş olayı çözülemedi", esik="olay çözümü")); continue
        if bit is None or bit <= bas: bit = bas + float(ip.get("hedef_sure_sn") or 30)
        bit = min(bit + float((ip.get("cikis") or {}).get("tasma_sn") or 0), toplam)
        rg = _kis(gir, float((ip.get("giris") or {}).get("rampa_sn") or 2.0), None)
        rc = _kis(cik, float((ip.get("cikis") or {}).get("rampa_sn") or 3.0), None)
        x, _ = O.oku(os.path.join(film, dosya)); x = O.stereo(x)
        x = _rampa(_dongu(x, int((bit - bas) * SR)), rg, rc)
        sev = ip.get("seviye") or {}; dsz = float(sev.get("diyalogsuz_lufs") or -18.0); alt = float(sev.get("diyalog_alti_db") or 14.0)
        alt = max(alt, so.esik("muzik_diyalog_alti_min_db"))
        g = dsz - O.lufs(x, SR)
        kisma, zarf = [], np.ones(len(x), np.float32)
        for d in diy:
            a, b = max(bas, d["cizelge_bas"] - 0.3), min(bit, d["cizelge_bas"] + d["sure"] + 0.3)
            if b <= a: continue
            ref = (DL.get(d["replik"]) or {}).get("olculen_lufs") or so.esik("diyalog_lufs")["normal"]
            db_ = min(0.0, (ref - alt) - dsz - 1.0)                       # 1 dB pay: kısa süreli ölçüm farkı
            if db_ >= 0: continue
            i0, i1 = int((a - bas) * SR), int((b - bas) * SR); r = int(0.3 * SR)
            k = O.kazanc(db_); z = np.full(i1 - i0, k, np.float32)
            z[:min(r, len(z))] = np.linspace(1, k, min(r, len(z))); z[-min(r, len(z)):] = np.linspace(k, 1, min(r, len(z)))
            zarf[i0:i1] = np.minimum(zarf[i0:i1], z); kisma.append({"bas": round(a, 3), "bit": round(b, 3), "db": round(db_, 1)})
        _ekle(st["muzik"], x * zarf[:, None], bas, g)
        out.append({"ipucu": ip["id"], "dosya": dosya, "cizelge_bas": round(bas, 3), "sure": round(bit - bas, 3), "giris_sn": rg, "cikis_sn": rc,
                    "kazanc_db": round(g, 2), "kisma": kisma, "gecici": False, "tur": ip.get("tur"), "motif": ip.get("motif")})
        muzikli.append((bas, bit))
        o.append(so.m("S6.5", "GEC" if (gir[0] <= rg <= gir[1] and cik[0] <= rc <= cik[1]) else "BAYRAK", birim=ip["id"],
                      olcu={"giris": rg, "cikis": rc}, esik=f"{gir}; {cik}"))
    # ölçüm: diyalog altında müzik (S6.2), diyalogsuz seviye (S6.3), kaplama (S6.4), leitmotif dönüşü (S6.7)
    for m_ in out:
        dp = [(max(m_["cizelge_bas"], d["cizelge_bas"]), min(m_["cizelge_bas"] + m_["sure"], d["cizelge_bas"] + d["sure"])) for d in diy]
        dp = [(a, b) for a, b in dp if b - a > 0.4]
        if dp:
            ld, lm = _pencere_lufs(st["diyalog"], dp), _pencere_lufs(st["muzik"], dp)
            if ld is not None and lm is not None:
                o.append(so.m("S6.2", "GEC" if ld - lm >= so.esik("muzik_diyalog_alti_min_db") else "HATA", birim=m_["ipucu"],
                              olcu=round(ld - lm, 2), esik=f"≥ {so.esik('muzik_diyalog_alti_min_db')} dB", kok_neden="muzik_maskeledi"
                              if ld - lm < so.esik("muzik_diyalog_alti_min_db") else None))
        bos = []; t0 = m_["cizelge_bas"] + m_["giris_sn"]; t1 = m_["cizelge_bas"] + m_["sure"] - m_["cikis_sn"]
        for a, b in sorted(dp) + [(t1, t1)]:
            if a - t0 > 1.0: bos.append((t0, a))
            t0 = max(t0, b)
        if bos:
            lm = _pencere_lufs(st["muzik"], bos); ar = so.esik("muzik_diyalogsuz_lufs")
            if lm is not None:
                o.append(so.m("S6.3", "GEC" if ar[0] - 0.5 <= lm <= ar[1] + 0.5 else "BAYRAK", birim=m_["ipucu"], olcu=round(lm, 2), esik=f"{ar} LUFS"))
    kap = sum(b - a for a, b in muzikli) / toplam if toplam else 0.0; ko = so.esik("muzik_kaplama_oran")
    o.append(so.m("S6.4", "GEC" if ko[0] <= kap <= ko[1] else "BAYRAK", olcu=round(kap, 3), esik=f"{ko} (ölçülen stemden)"))
    donus = len({m_["ipucu"] for m_ in out if m_.get("tur") == "tema" and m_.get("motif")})
    tema_var = any(ip.get("tur") == "tema" for ip in L.get("ipuclari") or [])
    if tema_var:
        o.append(so.m("S6.7_donus", "GEC" if donus >= so.esik("leitmotif_donus_min") else "BAYRAK", olcu=donus,
                      esik=f"≥ {so.esik('leitmotif_donus_min')} leitmotif dönüşü", kok_neden=None if donus >= so.esik("leitmotif_donus_min") else "muzik_motifsiz"))
    return out, o


def main(argv):
    try: film = so.film_coz(so.arg(argv, "--film"))
    except (ValueError, ortak.YolYok) as e: print(f"!! {e}"); return 4
    c = so.arg(argv, "--cizelge", "T1")
    if c == "T2":
        try: t2 = importlib.import_module("ses_katmani_t2")
        except ImportError:
            print("!! ses_katmani --cizelge T2 video sonrası ses diliminde gelir (ses_katmani_t2.py); bu kurulumda yok."); return 4
        return t2.main(argv)
    if c != "T1": print(__doc__); return 4
    if not os.path.exists(os.path.join(film, "SAHNELER.json")): print("!! SAHNELER.json yok"); return 1
    C, (y5, r5), (y6, r6) = cizelge_t1(film, sahte=so.sahte_mi(film, so.arg(argv, "--saglayici")))
    print(f"SES_CIZELGESI_T1: {len(C['ambiyans'])} yatak · {len(C['efektler'])} efekt · {len(C['muzik'])} müzik · {len(C['diyalog'])} replik · "
          f"{C['toplam_sn']} sn · S5 {r5['sonuc']} · S6 {r6['sonuc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
