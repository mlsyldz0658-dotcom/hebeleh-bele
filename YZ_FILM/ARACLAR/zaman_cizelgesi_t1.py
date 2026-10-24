"""ZAMAN ÇİZELGESİ T1 — animatik çizelgesi (TASARIM §1.3 A12, §6.4 `zaman_cizelgesi` T1; [KU2] KR1, §4.5.1).

Kullanım (film.py calis çağırır; zaman_cizelgesi.py --asama animatik bu modüle devreder):
  python zaman_cizelgesi_t1.py --asama animatik [--tur N] --film <film>
Kodda:
  import zaman_cizelgesi_t1 as t1
  plan = t1.t1_kur(film, tur)            → KURGU/surumler/KURGU_PLANI_T1_v<tur>.json (+ _RAPOR/ZAMAN_T1.json, _RAPOR/SAPMA_T1.json)
  t1.yeniden_zamanla(plan)               çizelge_bas, kare, diyalog ve kart anlarını plan sırasından yeniden hesaplar (kurgu_uygula da kullanır)
  t1.son_surum(film, "T1") → (N, yol) · t1.plan_oku(film, "T1", N=None) · t1.kare(sn) (1/24 sn'ye yuvarlar)
Girdi: SAHNELER.json v2 (planlar, `kullanim`, `_derlenir.replik_zaman`, `zanaat.kesme`, eylem zinciri), varsa
  KURGU/surumler/KURGU_PLANI_T0.json (T0 süreleri ve kartları), SESLER/diyalog.json v2 (`replikler.<id>.tts {dosya, sure_sn}`,
  seslendir --animatik yazar), SIRALI_GORSEL/NNN.jpg (yalnız G1 GEÇ kareler; A11 yazar), KURGU/KURGU_DUZEN_T1.json (kurgu_uygula'nın
  önceki turlarda uyguladığı kurgucu işlemleri; her T1 kurulumunda yeniden uygulanır).
Kurallar:
  - Plan süresi: konuşmalı planda formül yerine gerçek TTS süresi: konuşma başı (replik_zaman − kullanim.bas) + TTS + replik sonu payı
    (RE replik_sonu_kesme_sn alt ucu); L kesmede planlanan taşma çıkar; görünür adımların bitişi ve plan tipinin alt sınırı (RE
    plan_sure_aralik_sn) korunur. TTS yoksa T0 süresi kalır, ölçüm ÖLÇÜLEMEDİ. Süreler 1/24 sn'ye yuvarlanır; çizelgede boşluk yoktur.
  - Görüntü: SIRALI_GORSEL/NNN.jpg varsa (ve denetim.G1.sha1 eşleşiyorsa) `gorsel` + g1 GEC; yoksa `yer_tutucu` (D-14: tur 1 yer
    tutucularla koşar). Bitiş görseli: SIRALI_GORSEL/NNN_bitis.jpg ya da uretim.zincir.bitis_gorsel "plan:<no>".
  - Eylem şeridi yalnız görünür adımlardan (konuşma adımı hariç) ve **adsız** kurulur: karakterler her zaman görünüş etiketiyle
    (kör paket aynı videoyu kullanır; ad sızmaz). Amaç, risk, vuruş yazılmaz.
  - Sapma: plan başına |T1 − T0| / T0 > RE sapma_plan_oran_max → BAYRAK (SAPMA_T1.json). Komşu repliklerde cevap boşluğu RE
    cevap_boslugu_sn alt ucundan kısa → BAYRAK.
Çıkış kodları: 0 BİTTİ · 1 HATA (SAHNELER yok/bozuk) · 4 ORTAM (SAHNELER v1).
"""
import os, sys, re, json, glob, hashlib, argparse, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "zaman_cizelgesi_t1 1.0"
FPS = 24
KONUSMA = ("konusma",)
HAREKET = {"yavas_ileri": "ileri", "ileri": "ileri", "dolly_ileri": "ileri", "yavas_geri": "geri", "geri": "geri", "dolly_geri": "geri",
           "yavas_pan": "pan", "pan": "pan", "pan_sol": "pan", "pan_sag": "pan", "kayma": "pan"}
VARSAYILAN_E = {"replik_sonu_kesme_sn": [0.2, 0.5], "plan_sure_aralik_sn": {}, "sapma_plan_oran_max": 0.25, "cevap_boslugu_sn": [0.2, 0.6],
                "l_kesme_alici_plan_ek_sn": 0.5, "animatik_yer_tutucu_max_oran": 0.10}


class GirdiHatasi(Exception):
    pass


_E = None
def E(ad):
    global _E
    if _E is None:
        try:
            import esikler; _E = esikler.yukle()
        except Exception: _E = {}
    v = _E.get(ad) if hasattr(_E, "get") else None
    return VARSAYILAN_E.get(ad) if v is None else v


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")
def ortam(): return os.environ.get("YZ_FILM_ORTAM") or ("yerel" if os.name == "nt" else "bulut")
def kare_sayisi(sn): return max(1, int(round(float(sn) * FPS)))
def kare(sn): return round(round(float(sn) * FPS) / FPS, 4)


def sha(yol, n=12):
    h = hashlib.sha1()
    try:
        with open(yol, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    except OSError: return None
    return h.hexdigest()[:n]


def gorev_baglami(tur=None):
    gd = os.environ.get("YZ_FILM_GOREV")
    g = ortak.json_oku(os.path.join(gd, "GOREV.json"), {}) if gd else {}
    g = g or {}
    return {"id": g.get("id"), "tur": int(tur or g.get("tur_no") or 1), "asama": g.get("asama")}


# --- sürümler -------------------------------------------------------------------------------------------------
def surum_klasoru(film): return os.path.join(film, "KURGU", "surumler")


def surumler(film, cizelge="T1"):
    out = []
    for p in glob.glob(os.path.join(surum_klasoru(film), f"KURGU_PLANI_{cizelge}_v*.json")):
        m = re.search(r"_v(\d+)\.json$", p)
        if m: out.append((int(m.group(1)), p))
    return sorted(out)


def son_surum(film, cizelge="T1"):
    s = surumler(film, cizelge)
    return s[-1] if s else (0, None)


def plan_yolu(film, cizelge, n): return os.path.join(surum_klasoru(film), f"KURGU_PLANI_{cizelge}_v{int(n)}.json")


def plan_oku(film, cizelge="T1", n=None):
    """İstenen (yoksa en son) sürüm: (plan, yol, N). Yoksa (None, None, 0)."""
    if n is None: n, yol = son_surum(film, cizelge)
    else: yol = plan_yolu(film, cizelge, n)
    if not yol or not os.path.isfile(yol): return None, None, 0
    return ortak.json_oku(yol), yol, n


# --- girdiler --------------------------------------------------------------------------------------------------
def sahneler_v2(film):
    p = os.path.join(film, "SAHNELER.json")
    s = ortak.json_oku(p)
    if not isinstance(s, dict): raise GirdiHatasi("SAHNELER.json yok ya da bozuk.")
    if int(s.get("_surum", 1) or 1) < 2: raise OrtamHatasi("SAHNELER.json v1: animatik çizelgesi v2 plan ister (_surum: 2).")
    return s


class OrtamHatasi(Exception):
    pass


def tts_sureleri(film):
    """replik kimliği → {sure_sn, dosya}. SESLER/diyalog.json v2 (replikler.<id>.tts) ve eski biçim (liste) okunur."""
    d = ortak.json_oku(os.path.join(film, "SESLER", "diyalog.json"), {}) or {}
    out = {}
    rep = d.get("replikler")
    if isinstance(rep, dict):
        for rid, v in rep.items():
            t = (v or {}).get("tts") or {}
            if isinstance(t, dict) and isinstance(t.get("sure_sn"), (int, float)) and t["sure_sn"] > 0:
                out[rid] = {"sure_sn": float(t["sure_sn"]), "dosya": t.get("dosya"), "metin": (v or {}).get("duyulan_metin") or v.get("senaryo_metin")}
    elif isinstance(rep, list):
        for v in rep:
            if isinstance(v, dict) and v.get("id") and isinstance((v.get("tts") or {}).get("sure_sn"), (int, float)):
                out[v["id"]] = {"sure_sn": float(v["tts"]["sure_sn"]), "dosya": v["tts"].get("dosya"), "metin": v.get("duyulan_metin")}
    return out


def t0_oku(film):
    p = os.path.join(surum_klasoru(film), "KURGU_PLANI_T0.json")
    t0 = ortak.json_oku(p)
    if not isinstance(t0, dict):
        n, p = son_surum(film, "T0")
        t0 = ortak.json_oku(p) if p else None
    return t0 if isinstance(t0, dict) else None, (p if t0 else None)


def maske_etiketleri(film, sahneler):
    """karakter → görünüş etiketi (şerit her zaman adsız)."""
    h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    out = {}
    for kid, v in (h.get("karakterler") or {}).items():
        m = (v or {}).get("maske") or {}
        out[kid] = m.get("etiket_anonim_tr") or m.get("etiket_anonim_en") or (v or {}).get("tarif") or "ekrandaki kişi"
    for kid, v in (sahneler.get("karakterler") or {}).items():
        out.setdefault(kid, (v or {}).get("tarif") or "ekrandaki kişi")
    return out


def _sozel(x): return str(x or "").replace("_", " ").strip()


def serit_kur(plan, kb, sure, B, etiket):
    """[(bas, bit, metin)] plan içi saniyeyle; görünür adımlar, adsız."""
    z = plan.get("zanaat") or {}; out = []
    for a in sorted([a for a in z.get("eylem_zinciri") or [] if isinstance(a, dict)], key=lambda a: float(a.get("bas") or 0)):
        if a.get("tur") in KONUSMA: continue
        bas = max(0.0, float(a.get("bas") or 0) - kb); bit = min(sure, float(a.get("bit") or a.get("bas") or 0) - kb)
        if bit <= bas or bas >= sure: continue
        metin = None
        if B is not None:
            try:
                import plan_dili
                metin = plan_dili.adim_cumlesi(a, plan, B, "tr")[0]
            except Exception: metin = None
        if not metin:
            oz = etiket.get(a.get("ozne")) or _sozel(a.get("ozne"))
            hedef = a.get("hedef"); hedef = etiket.get(hedef) or _sozel(hedef) if hedef else ""
            metin = " ".join(x for x in (oz, _sozel(a.get("fiil")), ("→ " + hedef) if hedef else "") if x)
        for kid, et in etiket.items():                       # güvenlik: ad kalmışsa etiketle değiştir
            for ad in _adlar(plan, kid):
                metin = re.sub(r"(?<![\w])" + re.escape(ad) + r"(?![\w])", et, metin, flags=re.I)
        out.append({"bas": kare(bas), "bit": kare(bit), "metin": metin})
    return out


_ADLAR = {}
def _adlar(plan, kid): return _ADLAR.get(kid, [])


def _plan_dili_baglami(film, etiket):
    try:
        import plan_dili
        B = plan_dili.baglam(film)
        B["etiket"] = dict(etiket)
        return B
    except Exception: return None


def ad_tablosu(film):
    h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    _ADLAR.clear()
    for kid, v in (h.get("karakterler") or {}).items():
        v = v or {}; m = v.get("maske") or {}
        _ADLAR[kid] = [x for x in [v.get("ad") or kid.capitalize()] + list(m.get("takma_adlar") or []) if x]


def goruntu_coz(film, p):
    no = int(p.get("no"))
    g = "SIRALI_GORSEL/%03d.jpg" % no                      # planda hep / (Windows'ta da aynı JSON)
    gp = os.path.join(film, g)
    den = ((p.get("denetim") or {}).get("G1") or {})
    ok = os.path.isfile(gp)
    if ok and den.get("sha1"):
        s = sha(gp, 40) or ""
        ok = s.startswith(str(den["sha1"])[:8]) or str(den["sha1"]).startswith(s[:8])
    bitis = None
    for aday in ("SIRALI_GORSEL/%03d_bitis.jpg" % no,):
        if os.path.isfile(os.path.join(film, aday)): bitis = aday
    bg = (((p.get("uretim") or {}).get("zincir") or {}).get("bitis_gorsel"))
    if not bitis and isinstance(bg, str) and bg.startswith("plan:"):
        try:
            a = "SIRALI_GORSEL/%03d.jpg" % int(bg.split(":", 1)[1])
            if os.path.isfile(os.path.join(film, a)): bitis = a
        except ValueError: pass
    hk = HAREKET.get(str(((p.get("zanaat") or {}).get("kamera") or {}).get("hareket_tipi") or ""), "nefes")
    return {"tur": "gorsel" if ok else "yer_tutucu", "dosya": g if ok else None, "dosya_ozet": sha(gp) if ok else None,
            "bitis_dosya": bitis, "g1": "GEC" if ok else (den.get("sonuc") or "YOK"), "hareket": hk}


def plan_suresi(p, t0_sure, tts):
    """(sure, diyalog_kaydi|None, olcum notu)."""
    z = p.get("zanaat") or {}; d = p.get("_derlenir") or {}
    kb = float((p.get("kullanim") or {}).get("bas") or 0.0)
    taban = float(t0_sure or (p.get("kullanim") or {}).get("sure") or d.get("sure_sn") or z.get("klip_sn") or 8)
    tip_min = ((E("plan_sure_aralik_sn") or {}).get(z.get("plan_tipi")) or [0, 0])[0]
    adim_sonu = max([float(a.get("bit") or 0) - kb for a in z.get("eylem_zinciri") or []
                     if isinstance(a, dict) and a.get("tur") not in KONUSMA] + [0.0])
    rep = p.get("replik") or {}
    rid = rep.get("id")
    if not rid: return taban, None, None
    t = tts.get(rid)
    rz = (d.get("replik_zaman") or {}).get(rid)
    if rz is None:
        adim = next((a for a in z.get("eylem_zinciri") or [] if isinstance(a, dict) and a.get("tur") in KONUSMA), None)
        rz = [adim.get("bas"), adim.get("bit")] if adim else [kb, kb + taban]
    ofset = max(0.0, float(rz[0] or kb) - kb)
    kes = z.get("kesme") or {}
    tasma = float(kes.get("ses_tasma_sn") or 0) if str(kes.get("tip") or "").upper() == "L" else 0.0
    kayit = {"replik": rid, "plan": int(p["no"]), "karakter": rep.get("karakter"), "metin": rep.get("metin"),
             "plan_ofset": kare(ofset), "ekran_disi": bool(z.get("ekran_disi_ses")) or bool(rep.get("ekran_disi")),
             "jl": {"tip": "L", "tasma_sn": kare(tasma)} if tasma else None}
    gorunen = {x.get("id") for x in z.get("kadrajdakiler") or [] if isinstance(x, dict)}
    kayit["gorunen_konusan"] = (rep.get("karakter") in gorunen) and not kayit["ekran_disi"]
    if not t:
        kayit.update(sure=kare(max(0.1, float(rz[1] or 0) - float(rz[0] or 0))), tts=None, olcum="tts_yok")
        return taban, kayit, "tts_yok"
    pay = (E("replik_sonu_kesme_sn") or [0.2])[0]
    gerek = ofset + t["sure_sn"] + (0.0 if tasma else pay) - tasma
    kayit.update(sure=kare(t["sure_sn"]), tts=t.get("dosya"))
    return max(gerek, adim_sonu, tip_min, 0.5), kayit, None


# --- çizelge ---------------------------------------------------------------------------------------------------
def yeniden_zamanla(plan):
    """Plan sırasından çizelgeyi kurar (boşluk yok; planlı karartma hariç). Kare sayıları tamsayıdır."""
    kare_t = 0; bas = {}
    for p in plan.get("planlar") or []:
        p["kare"] = kare_sayisi(p.get("sure") or 0)
        p["sure"] = round(p["kare"] / FPS, 4)
        for k in plan.get("karartmalar") or []:
            if k.get("once_plan") == p.get("plan"): kare_t += kare_sayisi(k.get("sure") or 0)
        p["cizelge_bas"] = round(kare_t / FPS, 4); p["cizelge_kare"] = kare_t
        bas[p.get("plan")] = p; kare_t += p["kare"]
    for dk in plan.get("diyalog") or []:
        p = bas.get(dk.get("plan"))
        if p is None: dk["cizelge_bas"] = None; continue
        dk["cizelge_bas"] = round(p["cizelge_bas"] + float(dk.get("plan_ofset") or 0), 4)
    for k in plan.get("kartlar") or []:
        p = bas.get(k.get("plan"))
        if p is not None: k["cizelge_bas"] = round(p["cizelge_bas"] + float(k.get("ofset") or 0), 4)
    plan["toplam_kare"] = kare_t
    plan.setdefault("olcumler", {})["toplam_sn"] = round(kare_t / FPS, 4)
    return plan


def olcumler(plan):
    ps = plan.get("planlar") or []
    goruntulu = [p for p in ps if (p.get("goruntu") or {}).get("tur") in ("gorsel", "yer_tutucu")]
    yt = [p["plan"] for p in goruntulu if p["goruntu"]["tur"] == "yer_tutucu"]
    sure = [p["sure"] for p in ps]
    ilk120 = [p["sure"] for p in ps if p["cizelge_bas"] < 120]
    o = plan.setdefault("olcumler", {})
    o.update(plan_sayisi=len(ps), asl=round(sum(sure) / len(sure), 3) if sure else None,
             asl_ilk120=round(sum(ilk120) / len(ilk120), 3) if ilk120 else None,
             yer_tutucu_planlar=yt, yer_tutucu_orani=round(len(yt) / len(goruntulu), 4) if goruntulu else 0.0,
             g1_tamam=not yt, toplam_sn=round(plan.get("toplam_kare", 0) / FPS, 4))
    return o


def kartlar_t0(t0, t0_plan_bas):
    out = []
    for k in (t0 or {}).get("kartlar") or []:
        if not isinstance(k, dict): continue
        k = dict(k)
        if k.get("plan") is None and k.get("cizelge_bas") is not None:
            t = float(k["cizelge_bas"]); bul = None
            for no, (b, s) in sorted(t0_plan_bas.items(), key=lambda x: x[1][0]):
                if b <= t < b + s: bul = (no, t - b)
            if bul: k["plan"], k["ofset"] = bul[0], round(bul[1], 4)
        k.setdefault("ofset", 0.0)
        out.append(k)
    return out


def t1_kur(film, tur=1, gorev=None, yaz=True):
    film = os.path.abspath(film)
    s = sahneler_v2(film)
    planlar = sorted([p for p in s.get("sahneler") or [] if isinstance(p, dict) and isinstance(p.get("no"), int)],
                     key=lambda p: float(p.get("sira", p["no"]) or 0))
    if not planlar: raise GirdiHatasi("SAHNELER.json'da plan yok.")
    t0, t0_yol = t0_oku(film)
    t0_sure, t0_bas = {}, {}
    for x in (t0 or {}).get("planlar") or []:
        if isinstance(x, dict) and x.get("plan") is not None:
            t0_sure[x["plan"]] = float(x.get("sure") or 0); t0_bas[x["plan"]] = (float(x.get("cizelge_bas") or 0), float(x.get("sure") or 0))
    tts = tts_sureleri(film)
    etiket = maske_etiketleri(film, s); ad_tablosu(film)
    B = _plan_dili_baglami(film, etiket)
    cikti, diyalog, notlar = [], [], []
    for p in planlar:
        no = p["no"]
        z = p.get("zanaat") or {}
        sure, dk, nt = plan_suresi(p, t0_sure.get(no), tts)
        if nt: notlar.append({"plan": no, "madde": nt})
        g = goruntu_coz(film, p)
        kb = float((p.get("kullanim") or {}).get("bas") or 0)
        t0s = t0_sure.get(no) or float((p.get("kullanim") or {}).get("sure") or (p.get("_derlenir") or {}).get("sure_sn") or sure)
        kes = z.get("kesme") or {}
        cikti.append({"sira": p.get("sira", no), "plan": no, "parti": p.get("parti"), "sahne_grubu": z.get("sahne_grubu") or p.get("sahne_grubu"),
                      "plan_tipi_kod": z.get("plan_tipi"), "goruntu": dict(g, kullanim={"bas": kb, "sure": None}, kullanim_kaynak="plan",
                                                                          kullanim_kilit=None, hiz=1.0, ayna=False, kadraj_kirpma=None),
                      "sure": kare(sure), "t0_sure": round(t0s, 4),
                      "kesme_giris": {"tip": "duz"}, "kesme_cikis": {"tip": (str(kes.get("tip") or "duz")).lower()},
                      "durum_ozet": ((p.get("uretim") or {}).get("durum_dondu") or None),
                      "etki_var": any(bool((a or {}).get("etki")) for a in z.get("eylem_zinciri") or [] if isinstance(a, dict)),
                      "replik": (p.get("replik") or {}).get("id"),
                      "serit": serit_kur(p, kb, sure, B, etiket)})
        if dk: diyalog.append(dk)
    plan = {"_sahip": "kurgu", "_surum": 1, "film": s.get("film") or os.path.basename(film), "cizelge": "T1", "kurgu_surumu": int(tur),
            "fps": FPS, "tur": int(tur), "planlar": cikti, "diyalog": diyalog,
            "kartlar": kartlar_t0(t0, t0_bas), "karartmalar": [k for k in (t0 or {}).get("karartmalar") or [] if isinstance(k, dict)],
            "kullanici_kilitleri": [], "notlar": notlar}
    duzen = ortak.json_oku(os.path.join(film, "KURGU", "KURGU_DUZEN_T1.json"), {}) or {}
    if duzen.get("islemler"):
        import kurgu_uygula
        kurgu_uygula.duzen_uygula(plan, duzen["islemler"], s)
    yeniden_zamanla(plan)
    for p in plan["planlar"]:
        p["goruntu"]["kullanim"]["sure"] = p["sure"]
        p["sapma_oran"] = round(abs(p["sure"] - p["t0_sure"]) / p["t0_sure"], 3) if p.get("t0_sure") else None
    o = olcumler(plan)
    imzalar = {"SAHNELER.json": sha(os.path.join(film, "SAHNELER.json")), "SESLER/diyalog.json": sha(os.path.join(film, "SESLER", "diyalog.json")),
               "KURGU_PLANI_T0": sha(t0_yol) if t0_yol else None,
               "SIRALI_GORSEL": hashlib.sha1("".join(sorted(str(p["goruntu"].get("dosya_ozet")) for p in plan["planlar"])).encode()).hexdigest()[:12]}
    plan["girdi_imzalari"] = imzalar
    gimza = hashlib.sha1(json.dumps(imzalar, sort_keys=True).encode()).hexdigest()[:12]
    plan["_uretim"] = {"asama": "A12", "gorev": gorev, "girdi_imza": gimza, "arac_surum": SURUM, "esik_surum": _esik_surum(),
                       "sonuc": "GEC", "zaman": simdi(), "ortam": ortam()}
    if yaz:
        ortak.atomik_yaz(plan_yolu(film, "T1", tur), plan)
        _raporlar(film, plan, tur, gorev, gimza)
    return plan


def _esik_surum():
    try:
        import esikler; return esikler.SURUM
    except Exception: return None


def cevap_bosluklari(plan):
    """Aynı sahne grubunda ardışık iki farklı konuşanın replikleri arasındaki boşluk."""
    sg = {p["plan"]: p.get("sahne_grubu") for p in plan.get("planlar") or []}
    ds = sorted([d for d in plan.get("diyalog") or [] if d.get("cizelge_bas") is not None], key=lambda d: d["cizelge_bas"])
    out = []
    for a, b in zip(ds, ds[1:]):
        if sg.get(a["plan"]) != sg.get(b["plan"]) or a.get("karakter") == b.get("karakter"): continue
        out.append({"onceki": a["replik"], "sonraki": b["replik"], "bosluk_sn": round(b["cizelge_bas"] - (a["cizelge_bas"] + a["sure"]), 3)})
    return out


def _raporlar(film, plan, tur, gorev, gimza):
    o = plan["olcumler"]; esik = E("sapma_plan_oran_max"); cb = E("cevap_boslugu_sn") or [0.2, 0.6]
    sapma = [{"plan": p["plan"], "t0": p["t0_sure"], "t1": p["sure"], "oran": p["sapma_oran"],
              "seviye": "BAYRAK" if (p["sapma_oran"] or 0) > esik else "GEC"} for p in plan["planlar"]]
    bos = cevap_bosluklari(plan)
    olc = [{"madde": "sapma", "plan": x["plan"], "seviye": "BAYRAK", "olcu": x["oran"], "esik": esik} for x in sapma if x["seviye"] != "GEC"]
    olc += [{"madde": "cevap_boslugu", "seviye": "BAYRAK", "olcu": b["bosluk_sn"], "esik": cb[0], "replik": b["sonraki"]}
            for b in bos if b["bosluk_sn"] < cb[0]]
    olc += [{"madde": n["madde"], "plan": n["plan"], "seviye": "OLCULEMEDI", "neden": "TTS süresi yok (seslendir --animatik)"}
            for n in plan.get("notlar") or []]
    if o["yer_tutucu_planlar"]:
        olc.append({"madde": "yer_tutucu", "seviye": "BAYRAK", "olcu": o["yer_tutucu_orani"], "planlar": o["yer_tutucu_planlar"][:50]})
    u = lambda s: {"asama": "A12", "gorev": gorev, "girdi_imza": gimza, "arac_surum": SURUM, "esik_surum": _esik_surum(), "sonuc": s,
                   "zaman": simdi(), "ortam": ortam()}
    sonuc = "BAYRAK" if olc else "GEC"
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", "ZAMAN_T1.json"),
                     {"_surum": 1, "_uretim": u(sonuc), "cizelge": "T1", "kurgu_surumu": tur, "sonuc": sonuc,
                      "kurgu_plani": os.path.relpath(plan_yolu(film, "T1", tur), film).replace("\\", "/"),
                      "olcumler": o, "cevap_bosluklari": bos, "olcumler_liste": olc})
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", "SAPMA_T1.json"),
                     {"_surum": 1, "_uretim": u("BAYRAK" if any(x["seviye"] != "GEC" for x in sapma) else "GEC"),
                      "esik": esik, "planlar": sapma})


def main(argv=None):
    ap = argparse.ArgumentParser(description="Animatik zaman çizelgesi (T1).")
    ap.add_argument("--asama", default="animatik"); ap.add_argument("--tur", type=int); ap.add_argument("--film")
    ap.add_argument("--saglayici"); ap.add_argument("--json", action="store_true")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film): print("!! --film <film klasörü> gerekli."); return 1
    if o.asama not in ("animatik", "T1"):
        print("!! Bu modül yalnız T1'i (--asama animatik) kurar; diğer çizelgeler zaman_cizelgesi.py'dedir."); return 4
    g = gorev_baglami(o.tur)
    try: plan = t1_kur(film, g["tur"], g["id"])
    except OrtamHatasi as e: print("!! " + str(e)); return 4
    except GirdiHatasi as e: print("!! " + str(e)); return 1
    oz = plan["olcumler"]
    print(json.dumps({"cizelge": "KURGU/surumler/KURGU_PLANI_T1_v%d.json" % g["tur"], "toplam_sn": oz["toplam_sn"],
                      "plan": oz["plan_sayisi"], "yer_tutucu_orani": oz["yer_tutucu_orani"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
