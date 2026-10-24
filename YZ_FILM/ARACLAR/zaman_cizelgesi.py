"""ZAMAN ÇİZELGESİ — filmin zaman çizelgesi, olay listesi ve zamana bağlı ölçüler; T0 (kâğıt) Z1 bilgi ve Z2 duygu kapıları
(TASARIM §6.4, §7.2 Z1/Z2, §5.1 kural 8; ZN §1.2–1.3, §2.5, §4.1–4.4, §6.2 #21–#40).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"):
  python zaman_cizelgesi.py --asama kagit --film <film>     A07c T0: SAHNELER.json (kurgu sırası, kullanim.sure) →
        KURGU/surumler/KURGU_PLANI_T0.json   planların film üstündeki yeri (bas, bit, sure, kesme, L/J taşması)
        KURGU/ZAMAN_T0.json                  olay listesi (sahne, ilk eylem, replik, ad, merak aç/kapat, kurulum/kullanım, vuruş, ironi)
                                             + ölçüler + yoğunluk eğrisi (plan başına) ve hedef eğri
        KURGU/EGRI_T0.png                    yoğunluk ve hedef eğrisi (Pillow; yoksa ÖLÇÜLEMEDİ, rapora not)
        _RAPOR/ZAMAN_T0.json                 Z1 (bilgi) kapı raporu   · _RAPOR/ZAMAN_Z2_T0.json  Z2 (duygu) kapı raporu
  python zaman_cizelgesi.py --asama animatik [--tur N] --film <film>   A12 T1 → zaman_cizelgesi_t1.py (animatik çizelgesi)
  python zaman_cizelgesi.py --asama kurgu --film <film>      A16 T2: son KURGU_PLANI_T2 (plan_kurgu çağırır) →
        KURGU/ZAMAN_T2.json (ölçüler plan_kurgu.olcumler'den, olaylar, eğri) · _RAPOR/ZAMAN_T2.json (Z1 + T0'a göre sapma BAYRAK'ları)
        · _RAPOR/ZAMAN_Z2_T2.json (Z2) · _RAPOR/SAPMA_T2.json (plan başına |T2 − T0| / T0 > sapma_plan_oran_max → BAYRAK)
  python zaman_cizelgesi.py --asama yayin --film <film>      T3: henüz yok, 4 ile çıkar.
Kodda: cizelge(sahneler) → planlar · olaylar(sahneler, hikaye, planlar) · z1(...) · z2(...) · egri_ciz(...)
Kurallar:
  - Süre yalnız kullanim.sure'den (kod alanı _derlenir.sure_sn ile aynı); L/J taşması görünen süreyi değiştirmez, olay anını kaydırmaz.
  - Hikâye alanları (vuruş, yoğunluk, merak, kurulum, ironi, risk) HIKAYE.json'dan okunur ve plana _derlenir.hikaye olarak eşlenmiştir
    (plan_birlestir); plan düzeyinde zanaat.merak_ac / kurulum verilmişse an o planın başıdır, yoksa sahnenin başı.
  - Film yapısına bağlı ölçüler (parti sonu, doruk, en karanlık an, duygu haritası, ASL, başlık kartı, kahraman adı ≤ 120 sn) film süresi
    film_sure_aralik_sn alt sınırının yarısından kısaysa (örnek ve test filmleri) uygulanmaz; rapordaki "uygulanmadi" listesine yazılır.
  - Hikâye toplam süresi: T0 süresi sahne hedeflerinin toplamından ±%15'ten fazla saparsa HATA, bant içi sapma > %5 BAYRAK (§7.2 Z1).
Çıkış kodları: 0 GEÇ/BAYRAK · 1 HATA (Z1/Z2) ya da bozuk girdi · 2 SAHNELER.json yok · 4 kullanım ya da henüz desteklenmeyen aşama.
"""
import os, sys, re, math
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "zaman_cizelgesi 1.0"
ASAMA_T = {"kagit": "T0", "animatik": "T1", "kurgu": "T2", "yayin": "T3"}
SONRAKI = {"yayin": "adım 16–17 (T3 yayın çizelgesi)"}
MANZARA = ("kurulus", "gecis")


def _r(x): return round(float(x), 2)


# --- çizelge ------------------------------------------------------------------------------------------------------
def cizelge(s):
    """Kurgu sırasıyla planlar: {no, sira, sahne, parti, bas, bit, sure, plan_tipi, kesme, ses_tasma_sn, kullanim}."""
    P = sorted(s.get("sahneler") or [], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0))
    t, out = 0.0, []
    for p in P:
        z = p.get("zanaat") or {}; k = p.get("kullanim") or {}
        sure = float(k.get("sure") or (p.get("_derlenir") or {}).get("sure_sn") or 0)
        ks = z.get("kesme") or {}
        out.append({"no": p.get("no"), "sira": p.get("sira"), "kod": z.get("kod"), "sahne": z.get("sahne_grubu"),
                    "parti": int(p.get("parti") or 1), "bas": _r(t), "bit": _r(t + sure), "sure": _r(sure), "plan_tipi": z.get("plan_tipi"),
                    "kesme": ks.get("tip"), "ses_tasma_sn": float(ks.get("ses_tasma_sn") or 0), "kullanim": {"bas": k.get("bas"), "sure": sure},
                    "yogunluk": ((p.get("_derlenir") or {}).get("hikaye") or {}).get("yogunluk") or z.get("yogunluk"),
                    "duygu": ((p.get("_derlenir") or {}).get("hikaye") or {}).get("hedef_duygu") or p.get("duygu")})
        t += sure
    return out


def _an(c, p, adim_bas):
    """Klip içi an → film anı (kullanılan pencereye kırpılır)."""
    kb = float((c["kullanim"] or {}).get("bas") or 0)
    return _r(min(c["bit"], max(c["bas"], c["bas"] + float(adim_bas or 0) - kb)))


def _ad_desen(ad): return re.compile(r"\b" + re.escape(ad) + r"\b", re.I) if ad else None


def olaylar(s, h, C):
    """Olay listesi (zamana göre sıralı)."""
    h = h or {}; P = {p.get("no"): p for p in s.get("sahneler") or []}
    hs = {x.get("id"): x for x in h.get("sahneler") or [] if isinstance(x, dict)}
    ev = []; E = ev.append
    sahne_bas, sahne_bit = {}, {}
    for c in C:
        sahne_bas.setdefault(c["sahne"], c["bas"]); sahne_bit[c["sahne"]] = c["bit"]
    for sid, t in sahne_bas.items():
        x = hs.get(sid) or {}
        E({"t": t, "tur": "sahne", "sahne": sid, "parti": (s.get("sahne_gruplari") or {}).get(sid, {}).get("hikaye", {}).get("parti")})
        if x.get("vurus"): E({"t": t, "tur": "vurus", "deger": x["vurus"], "sahne": sid})
        if x.get("ironi"): E({"t": t, "tur": "ironi", "deger": x["ironi"], "sahne": sid})
        if x.get("risk"): E({"t": t, "tur": "risk", "deger": x["risk"], "sahne": sid, "sozlu": bool(x.get("risk_sozlu"))})
    adlar = {k: (v or {}).get("ad") or k.capitalize() for k, v in (h.get("karakterler") or {}).items()}
    gorulen = set(); plan_merak = set(); plan_kur = set()
    for c in C:
        p = P.get(c["no"]) or {}; z = p.get("zanaat") or {}
        for a in sorted(z.get("eylem_zinciri") or [], key=lambda a: a.get("bas") or 0):
            if a.get("tur") == "fiziksel": E({"t": _an(c, p, a.get("bas")), "tur": "eylem", "plan": c["no"], "kim": a.get("ozne"), "fiil": a.get("fiil")})
            if a.get("tur") == "konusma":
                r = p.get("replik") or {}; metin = r.get("metin") or ""
                E({"t": _an(c, p, a.get("bas")), "tur": "replik", "plan": c["no"], "kim": a.get("ozne"), "replik": a.get("replik"),
                   "kelime": len(metin.split())})
                for kid, ad in adlar.items():
                    d = _ad_desen(ad)
                    if d and d.search(metin): E({"t": _an(c, p, a.get("bas")), "tur": "ad_soylendi", "kim": kid, "plan": c["no"], "sahne": c["sahne"]})
        for k in z.get("kadrajdakiler") or []:
            if isinstance(k, dict) and k.get("id") and k["id"] not in gorulen and k.get("yuz_acisi") not in ("gorunmez",):
                gorulen.add(k["id"]); E({"t": c["bas"], "tur": "ilk_gorunus", "kim": k["id"], "plan": c["no"], "sahne": c["sahne"]})
        for m in z.get("merak_ac") or []: plan_merak.add(m); E({"t": c["bas"], "tur": "merak_ac", "id": m, "plan": c["no"]})
        for m in z.get("merak_kapat") or []: plan_merak.add("x" + m); E({"t": c["bit"], "tur": "merak_kapat", "id": m, "plan": c["no"]})
        for m in z.get("kurulum") or []: plan_kur.add(m); E({"t": c["bas"], "tur": "kurulum", "id": m, "plan": c["no"]})
        for m in z.get("kullanim_bilgi") or []: plan_kur.add("x" + m); E({"t": c["bas"], "tur": "kullanim", "id": m, "plan": c["no"]})
    for sid, x in hs.items():
        if sid not in sahne_bas: continue
        for m in x.get("merak_ac") or []:
            if m not in plan_merak: E({"t": sahne_bas[sid], "tur": "merak_ac", "id": m, "sahne": sid})
        for m in x.get("merak_kapat") or []:
            if "x" + m not in plan_merak: E({"t": sahne_bit[sid], "tur": "merak_kapat", "id": m, "sahne": sid})
        for m in x.get("kurulum") or []:
            if m not in plan_kur: E({"t": sahne_bas[sid], "tur": "kurulum", "id": m, "sahne": sid})
        for m in x.get("kullanim_bilgi") or []:
            if "x" + m not in plan_kur: E({"t": sahne_bas[sid], "tur": "kullanim", "id": m, "sahne": sid})
    # MERAK_DEFTERI / KURULUMLAR: sahne alanında yazılmamış ama defterde olan açılış/kapanış ve kullanım
    var = {(e["tur"], e.get("id")) for e in ev}
    for m in h.get("MERAK_DEFTERI") or []:
        if m.get("ac") in sahne_bas and ("merak_ac", m.get("id")) not in var: E({"t": sahne_bas[m["ac"]], "tur": "merak_ac", "id": m.get("id"), "sahne": m["ac"]})
        if m.get("kapat") in sahne_bit and ("merak_kapat", m.get("id")) not in var:
            E({"t": sahne_bit[m["kapat"]], "tur": "merak_kapat", "id": m.get("id"), "sahne": m["kapat"]})
    for k in h.get("KURULUMLAR") or []:
        if k.get("kurulum") in sahne_bas and ("kurulum", k.get("id")) not in var: E({"t": sahne_bas[k["kurulum"]], "tur": "kurulum", "id": k.get("id"), "sahne": k["kurulum"]})
        if k.get("kullanim") in sahne_bas and ("kullanim", k.get("id")) not in var:
            E({"t": sahne_bit[k["kullanim"]], "tur": "kullanim", "id": k.get("id"), "sahne": k["kullanim"]})
    ev.sort(key=lambda e: (e["t"], e["tur"]))
    return ev


# --- Z1 (bilgi) ---------------------------------------------------------------------------------------------------
def _uzun(toplam, E): return toplam >= float((E.get("film_sure_aralik_sn") or [1800])[0]) * 0.5


def z1(s, h, C, ev, E):
    olc, uyg = [], []; O = olc.append; h = h or {}
    toplam = C[-1]["bit"] if C else 0.0; uzun = _uzun(toplam, E)
    ilk = lambda tur: next((e for e in ev if e["tur"] == tur), None)
    e = ilk("eylem")
    if e is None or e["t"] > E.get("ilk_eylem_max_sn", 5):
        O(po.m("ilk_eylem_gec", "HATA", (e or {}).get("plan"), olcu=(e or {}).get("t"), esik=E.get("ilk_eylem_max_sn", 5), kural="Z1#21",
               kok_neden="ilk_eylem", neden="ilk görünür eylem ilk 5 sn içinde"))
    m = ilk("merak_ac")
    if (m is None and toplam > E.get("ilk_merak_max_sn", 20)) or (m and m["t"] > E.get("ilk_merak_max_sn", 20)):
        O(po.m("ilk_merak_gec", "HATA", (m or {}).get("plan"), olcu=(m or {}).get("t"), esik=E.get("ilk_merak_max_sn", 20), kural="Z1#21",
               kok_neden="merak"))
    ilk30 = [c for c in C if c["bas"] < 30 and c["plan_tipi"] in MANZARA]
    if len(ilk30) > E.get("ilk30_manzara_plan_max", 1) or sum(c["sure"] for c in ilk30) > E.get("ilk30_manzara_sure_max_sn", 3.0) + 1e-9:
        O(po.m("ilk30_manzara_fazla", "BAYRAK", ilk30[-1]["no"], olcu={"plan": len(ilk30), "sure": _r(sum(c["sure"] for c in ilk30))},
               esik={"plan": E.get("ilk30_manzara_plan_max", 1), "sure": E.get("ilk30_manzara_sure_max_sn", 3.0)}, kural="ZN§1.4"))
    # kahraman adı ve ad kuralı (#23)
    kahraman = next((k for k, v in (h.get("karakterler") or {}).items() if (v or {}).get("rol") == "kahraman"), None)
    sahne_sira = [x for x in dict.fromkeys(c["sahne"] for c in C)]
    for kid in (h.get("karakterler") or {}):
        gor = next((x for x in ev if x["tur"] == "ilk_gorunus" and x["kim"] == kid), None)
        ad = next((x for x in ev if x["tur"] == "ad_soylendi" and x["kim"] == kid), None)
        if not gor: continue
        si = sahne_sira.index(gor["sahne"]) if gor["sahne"] in sahne_sira else 0
        sinir_sahne = si + E.get("ad_ilk_gorunus_max_sahne", 2)
        if ad is None:
            if len(sahne_sira) > sinir_sahne + 1:          # film o sahneyi geçmeden ölçülemez
                O(po.m("ad_soylenmedi", "HATA" if kid == kahraman else "BAYRAK", gor["plan"], kim=kid, esik=E.get("ad_ilk_gorunus_max_sahne", 2),
                       kural="Z1#23", kok_neden="ad", neden="karakterin adı ilk görünüşünden sonra en geç 2 sahnede söylenir"))
        elif ad["sahne"] in sahne_sira and sahne_sira.index(ad["sahne"]) > sinir_sahne:
            O(po.m("ad_gec_soylendi", "HATA" if kid == kahraman else "BAYRAK", ad["plan"], kim=kid, kural="Z1#23", kok_neden="ad"))
        if kid == kahraman:
            t = ad["t"] if ad else None
            if (t is None and toplam > E.get("kahraman_adi_max_sn", 120)) or (t is not None and t > E.get("kahraman_adi_max_sn", 120)):
                O(po.m("kahraman_adi_gec", "HATA", (ad or gor)["plan"], kim=kid, olcu=t, esik=E.get("kahraman_adi_max_sn", 120), kural="Z1#23", kok_neden="ad"))
    # risk sözlü (#24)
    rs = [x for x in ev if x["tur"] == "risk" and x.get("sozlu")]
    if uzun and (not rs or rs[0]["t"] > E.get("risk_sozlu_max_sn", 180)):
        O(po.m("risk_sozlu_gec", "HATA", None, olcu=rs[0]["t"] if rs else None, esik=E.get("risk_sozlu_max_sn", 180), kural="Z1#24", kok_neden="risk"))
    elif not uzun: uyg.append("risk_sozlu_max_sn")
    # merak aralığı ve açık soru sayısı (#25, #26, #27, #28)
    mt = [x["t"] for x in ev if x["tur"] in ("merak_ac", "merak_kapat")]
    if mt:
        bos = max([b - a for a, b in zip([0.0] + mt, mt + [toplam])])
        if bos > E.get("merak_olay_aralik_max_sn", 90):
            O(po.m("merak_boslugu", "BAYRAK", None, olcu=_r(bos), esik=E.get("merak_olay_aralik_max_sn", 90), kural="Z1#25"))
    acik, acilis, omur = set(), {}, E.get("soru_omru_max_sn") or {}
    tur = {m.get("id"): m.get("tur") for m in h.get("MERAK_DEFTERI") or []}
    ilk_ac = next((x["t"] for x in ev if x["tur"] == "merak_ac"), None)
    for x in ev:
        if x["tur"] == "merak_ac": acik.add(x["id"]); acilis[x["id"]] = x["t"]
        elif x["tur"] == "merak_kapat":
            acik.discard(x["id"])
            sinir = omur.get(tur.get(x["id"]))
            if isinstance(sinir, (int, float)) and x["id"] in acilis and x["t"] - acilis[x["id"]] > sinir:
                O(po.m("soru_omru_uzun", "BAYRAK", x.get("plan"), olcu=_r(x["t"] - acilis[x["id"]]), esik=sinir, id=x["id"], kural="Z1#27"))
        aa = E.get("acik_soru_aralik") or [1, 5]
        if ilk_ac is not None and x["t"] > ilk_ac and x["t"] < toplam - 1e-6 and not (aa[0] <= len(acik) <= aa[1]) and x["tur"] in ("merak_ac", "merak_kapat"):
            O(po.m("acik_soru_sayisi", "BAYRAK", x.get("plan"), olcu=len(acik), esik=aa, t=x["t"], kural="Z1#26"))
    partiler = sorted({c["parti"] for c in C})
    if uzun:
        for n in partiler:
            son = max(c["bit"] for c in C if c["parti"] == n)
            acik_n = {x["id"] for x in ev if x["tur"] == "merak_ac" and x["t"] <= son} - {x["id"] for x in ev if x["tur"] == "merak_kapat" and x["t"] <= son}
            if not acik_n: O(po.m("parti_sonu_acik_soru_yok", "HATA", None, parti=n, kural="Z1#28", kok_neden="merak"))
    else: uyg.append("parti_sonu_acik_soru")
    # kurulum → kullanım (#29, #30)
    kur = {x["id"]: x["t"] for x in ev if x["tur"] == "kurulum"}
    for x in ev:
        if x["tur"] != "kullanim": continue
        if x["id"] not in kur or kur[x["id"]] > x["t"]:
            O(po.m("kurulumsuz_kullanim", "HATA", x.get("plan"), id=x["id"], kural="Z1#29", kok_neden="kurulum", neden="kullanımdan önce kurulum yok"))
        elif x["t"] - kur[x["id"]] < E.get("kurulum_kullanim_min_sn", 20):
            O(po.m("kurulum_kullanim_yakin", "HATA", x.get("plan"), id=x["id"], olcu=_r(x["t"] - kur[x["id"]]), esik=E.get("kurulum_kullanim_min_sn", 20),
                   kural="Z1#29", kok_neden="kurulum"))
        elif x["t"] - kur[x["id"]] > E.get("hatirlatma_esigi_sn", 600):
            O(po.m("hatirlatma_gerek", "BAYRAK", x.get("plan"), id=x["id"], olcu=_r(x["t"] - kur[x["id"]]), kural="Z1#30"))
    kul = {x["id"] for x in ev if x["tur"] == "kullanim"}
    for k, t in kur.items():
        if k not in kul and uzun: O(po.m("kullanilmayan_kurulum", "BAYRAK", None, id=k, kural="Z1#32"))
    # sahne başına yeni ad, konuşan karakter (#34)
    konusan = {x["kim"] for x in ev if x["tur"] == "replik"}
    if len(konusan) > E.get("konusan_karakter_max", 8):
        O(po.m("konusan_karakter_fazla", "BAYRAK", None, olcu=len(konusan), esik=E.get("konusan_karakter_max", 8), kural="Z1#34"))
    for sid in sahne_sira:
        n = len({x["kim"] for x in ev if x["tur"] == "ad_soylendi" and x.get("sahne") == sid
                 and not any(y["tur"] == "ad_soylendi" and y["kim"] == x["kim"] and y["t"] < x["t"] for y in ev)})
        if n > E.get("sahne_yeni_ad_max", 2): O(po.m("sahne_yeni_ad_fazla", "BAYRAK", None, sahne=sid, olcu=n, esik=E.get("sahne_yeni_ad_max", 2), kural="Z1#34"))
    # ironi (#33)
    if uzun:
        for n in partiler:
            if not any(x["tur"] == "ironi" for x in ev if any(c["parti"] == n and c["sahne"] == x.get("sahne") for c in C)):
                O(po.m("ironi_yok", "BAYRAK", None, parti=n, esik=E.get("ironi_parti_min", 1), kural="Z1#33"))
    else: uyg += ["ironi_parti_min", "kahraman_adi_max_sn (film kısa)"]
    # ASL (Z0 #7)
    if uzun and C:
        asl = toplam / len(C); a = E.get("asl_film_aralik_sn") or [4.2, 5.2]
        if not a[0] <= asl <= a[1]: O(po.m("asl_film", "BAYRAK", None, olcu=_r(asl), esik=a, kural="Z0#7"))
        for sinir, ad in ((120, "ilk120_asl_max_sn"), (30, "ilk30_asl_max_sn")):
            cc = [c for c in C if c["bas"] < sinir]
            if cc and sum(c["sure"] for c in cc) / len(cc) > E.get(ad, 4.0):
                O(po.m(ad.replace("_max_sn", ""), "BAYRAK", None, olcu=_r(sum(c["sure"] for c in cc) / len(cc)), esik=E.get(ad), kural="Z0#7"))
    else: uyg.append("asl_film_aralik_sn")
    # hikâye süresi bandı
    hed = sum(float(x.get("hedef_sure_sn") or 0) for x in h.get("sahneler") or [] if x.get("id") in sahne_sira)
    if hed > 0:
        sap = abs(toplam - hed) / hed
        if sap > 0.15: O(po.m("hikaye_suresi_bant_disi", "HATA", None, olcu=_r(toplam), esik=_r(hed), oran=round(sap, 3), kural="§7.2 Z1 ±%15",
                              kok_neden="sure", neden="T0 süresi sahne hedeflerinin toplamından ±%15'ten fazla sapıyor"))
        elif sap > 0.05: O(po.m("hikaye_suresi_sapmasi", "BAYRAK", None, olcu=_r(toplam), esik=_r(hed), oran=round(sap, 3), kural="§7.2 Z1"))
    return olc, uyg


# --- Z2 (duygu eğrisi) --------------------------------------------------------------------------------------------
def egri(C, E, adim=1.0):
    """Saniyelik yoğunluk dizisi [(t, y, duygu)]."""
    out = []
    for c in C:
        t = c["bas"]
        while t < c["bit"] - 1e-9:
            out.append((round(t, 2), c["yogunluk"], c["duygu"])); t += adim
    return out


def hedef_egri(toplam, E):
    """duygu_haritasi_40dk (dakika başına) film süresine ölçeklenir."""
    dh = E.get("duygu_haritasi_40dk") or []
    if not dh or toplam <= 0: return lambda t: None
    return lambda t: dh[min(len(dh) - 1, int(t / toplam * len(dh)))]


def z2(s, h, C, E):
    olc, uyg = [], []; O = olc.append
    toplam = C[-1]["bit"] if C else 0.0; uzun = _uzun(toplam, E)
    eksik = [c["no"] for c in C if not isinstance(c["yogunluk"], (int, float))]
    if eksik: O(po.m("yogunluk_yok", "BAYRAK", eksik[0], olcu=len(eksik), neden="planın yoğunluğu HIKAYE.json'da yok", planlar=eksik[:20]))
    seri = [(t, y, d) for t, y, d in egri(C, E) if isinstance(y, (int, float))]
    if not seri: return olc, uyg
    H = hedef_egri(toplam, E)
    if uzun:
        sap_bas = None
        for t, y, _ in seri:
            hy = H(t)
            if hy is not None and abs(y - hy) > E.get("yogunluk_sapma_max", 2):
                sap_bas = t if sap_bas is None else sap_bas
                if t - sap_bas > E.get("yogunluk_sapma_sure_max_sn", 60):
                    O(po.m("duygu_haritasi_sapmasi", "BAYRAK", None, t=sap_bas, olcu=y, esik=hy, kural="Z2#35")); sap_bas = -1e9
            else: sap_bas = None
        pen = E.get("pencere_tepe_sn", 180); t0 = 0.0
        while t0 < toplam:
            ys = [y for t, y, _ in seri if t0 <= t < t0 + pen]
            if ys and max(ys) < E.get("pencere_tepe_min", 6): O(po.m("pencerede_tepe_yok", "BAYRAK", None, t=_r(t0), olcu=max(ys), kural="Z2#36"))
            t0 += pen
        for n in sorted({c["parti"] for c in C}):
            cc = [c for c in C if c["parti"] == n and isinstance(c["yogunluk"], (int, float))]
            if cc and max(c["yogunluk"] for c in cc[-3:]) < E.get("parti_sonu_yogunluk_min", 8):
                O(po.m("parti_sonu_yogunluk", "HATA", cc[-1]["no"], parti=n, olcu=max(c["yogunluk"] for c in cc[-3:]),
                       esik=E.get("parti_sonu_yogunluk_min", 8), kural="Z2#39", kok_neden="yogunluk"))
        mx = max(y for _, y, _ in seri)
        if mx < E.get("doruk_yogunluk_min", 9): O(po.m("doruk_yogunluk", "HATA", None, olcu=mx, esik=E.get("doruk_yogunluk_min", 9), kural="Z2#39", kok_neden="yogunluk"))
        vur = {c["no"]: c for c in C}
        for x in s.get("sahneler") or []:
            if ((x.get("_derlenir") or {}).get("hikaye") or {}).get("vurus") == "en_karanlik_an":
                c = vur.get(x.get("no"))
                if c and isinstance(c["yogunluk"], (int, float)) and c["yogunluk"] < E.get("en_karanlik_yogunluk_min", 6):
                    O(po.m("en_karanlik_yogunluk", "HATA", c["no"], olcu=c["yogunluk"], esik=E.get("en_karanlik_yogunluk_min", 6), kural="Z2#39", kok_neden="yogunluk"))
                break
        for i, (t, y, _) in enumerate(seri):          # tepe öncesi çukur (#38)
            if y >= E.get("tepe_esigi", 8) and (i == 0 or seri[i - 1][1] < y):
                a, b = E.get("tepe_oncesi_cukur_pencere_sn") or [60, 120]
                once = [yy for tt, yy, _ in seri if t - b <= tt <= t - a]
                if once and y - min(once) < E.get("tepe_oncesi_cukur_min_dusus", 2):
                    O(po.m("tepe_oncesi_cukur_yok", "BAYRAK", None, t=t, olcu=y - min(once), esik=E.get("tepe_oncesi_cukur_min_dusus", 2), kural="Z2#38"))
    else: uyg += ["duygu_haritasi_40dk", "pencere_tepe_min", "parti_sonu_yogunluk_min", "doruk_yogunluk_min", "en_karanlik_yogunluk_min",
                  "tepe_oncesi_cukur"]
    # düz çizgi (#37) ve aynı duygu (her uzunlukta)
    bas, ref, refd = seri[0][0], seri[0][1], seri[0][2]
    for t, y, d in seri[1:] + [(toplam, None, None)]:
        if y is None or abs(y - ref) > 1 or d != refd:
            if t - bas > E.get("duz_cizgi_max_sn", 180): O(po.m("duz_cizgi", "BAYRAK", None, t=_r(bas), olcu=_r(t - bas), esik=E.get("duz_cizgi_max_sn", 180), kural="Z2#37"))
            if y is not None: bas, ref, refd = t, y, d
    dk = E.get("ayni_duygu_ardisik_dk_max", 2) * 60; bas, refd = seri[0][0], seri[0][2]
    for t, _, d in seri[1:] + [(toplam, None, None)]:
        if d != refd:
            if refd and t - bas > dk: O(po.m("ayni_duygu_uzun", "BAYRAK", None, t=_r(bas), olcu=_r(t - bas), esik=dk, duygu=refd, kural="Z2"))
            bas, refd = t, d
    return olc, uyg


# --- çizim --------------------------------------------------------------------------------------------------------
def egri_ciz(yol, C, E):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        return "OLCULEMEDI"
    W, Hh, m = 1200, 360, 40; toplam = (C[-1]["bit"] if C else 1.0) or 1.0
    im = Image.new("RGB", (W, Hh), (252, 252, 248)); dr = ImageDraw.Draw(im)
    X = lambda t: m + (W - 2 * m) * t / toplam; Y = lambda y: Hh - m - (Hh - 2 * m) * y / 10.0
    for y in range(0, 11, 2):
        dr.line([(m, Y(y)), (W - m, Y(y))], fill=(225, 225, 225)); dr.text((8, Y(y) - 6), str(y), fill=(120, 120, 120))
    H = hedef_egri(toplam, E); onceki = None
    for i in range(0, 201):
        t = toplam * i / 200.0; hy = H(t)
        if hy is None: break
        p = (X(t), Y(hy))
        if onceki: dr.line([onceki, p], fill=(160, 160, 200), width=1)
        onceki = p
    for c in C:
        if isinstance(c["yogunluk"], (int, float)):
            dr.line([(X(c["bas"]), Y(c["yogunluk"])), (X(c["bit"]), Y(c["yogunluk"]))], fill=(200, 60, 40), width=3)
    sahne = None
    for c in C:
        if c["sahne"] != sahne:
            sahne = c["sahne"]; dr.line([(X(c["bas"]), m), (X(c["bas"]), Hh - m)], fill=(200, 200, 200)); dr.text((X(c["bas"]) + 2, m - 14), str(sahne), fill=(80, 80, 80))
    dr.text((m, Hh - m + 10), f"T0 yoğunluk (kırmızı) · hedef (mavi) · {toplam:.0f} sn", fill=(60, 60, 60))
    os.makedirs(os.path.dirname(yol), exist_ok=True); tmp = yol + ".tmp.png"; im.save(tmp); os.replace(tmp, yol)
    return "GEC"


# --- ana iş -------------------------------------------------------------------------------------------------------
def kagit(kok, tur):
    E = po.esik()
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(s, dict) or int(s.get("_surum", 1) or 1) < 2:
        print("!! v2 SAHNELER.json yok (önce plan_birlestir)", flush=True); return 2
    h = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    C = cizelge(s); ev = olaylar(s, h, C); imza = po.imza([C, h.get("sahneler")])
    toplam = C[-1]["bit"] if C else 0.0
    o1, u1 = z1(s, h, C, ev, E); o2, u2 = z2(s, h, C, E)
    egri_yol = os.path.join(kok, "KURGU", "EGRI_T0.png"); es = egri_ciz(egri_yol, C, E)
    zarf = po.zarf("A07c", SURUM, "GEC", imza)
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "surumler", "KURGU_PLANI_T0.json"),
                     {"_surum": 1, "_uretim": zarf, "surum": "T0", "toplam_sn": _r(toplam), "plan_sayisi": len(C),
                      "asl_sn": _r(toplam / len(C)) if C else None, "planlar": C})
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "ZAMAN_T0.json"),
                     {"_surum": 1, "_uretim": zarf, "surum": "T0", "toplam_sn": _r(toplam), "olaylar": ev,
                      "egri": [{"t": t, "yogunluk": y, "duygu": d} for t, y, d in egri(C, E, 5.0)],
                      "enerji": None, "enerji_not": "enerji eğrisi T1 (ses) ve T2'de (görüntü + ses + kesme) ölçülür",
                      "egri_png": "KURGU/EGRI_T0.png" if es == "GEC" else None})
    birim = [c["no"] for c in C]
    not_ = [] if es == "GEC" else ["EGRI_T0.png çizilemedi (Pillow yok): ÖLÇÜLEMEDİ"]
    _, r1 = po.rapor_yaz(kok, "Z1", "T0", o1, asama="A07c", arac=SURUM, birimler=birim, tur=tur, girdi_imza=imza,
                         varsayilan=os.path.join("_RAPOR", "ZAMAN_T0.json"), ek={"uygulanmadi": u1, "toplam_sn": _r(toplam), "notlar": not_})
    _, r2 = po.rapor_yaz(kok, "Z2", "T0", o2, asama="A07c", arac=SURUM, birimler=birim, tur=tur, girdi_imza=imza,
                         varsayilan=os.path.join("_RAPOR", "ZAMAN_Z2_T0.json"), ek={"uygulanmadi": u2, "egri": es})
    po.yaz_ozet(r1, "Z1 T0"); po.yaz_ozet(r2, "Z2 T0")
    print(f"T0: {len(C)} plan, {toplam:.1f} sn, {len(ev)} olay", flush=True)
    return max(po.cikis(r1), po.cikis(r2))


def t2_cizelge(kp, pl):
    """KURGU_PLANI_T2 planları → cizelge() biçimi (bas/bit/sure T2 çizelgesinden, kullanim kırpma penceresinden)."""
    out = []
    for x in kp.get("planlar") or []:
        p = pl.get(x.get("plan"))
        if not isinstance(p, dict): continue                # örtü/kart girdisi: SAHNELER'de planı yok
        z = p.get("zanaat") or {}; g = x.get("goruntu") or {}; ku = g.get("kullanim") or {}
        bas, sure = float(x.get("cizelge_bas") or 0), float(x.get("sure") or 0)
        ks = z.get("kesme") or {}
        out.append({"no": p.get("no"), "sira": x.get("sira", p.get("sira")), "kod": z.get("kod"), "sahne": z.get("sahne_grubu"),
                    "parti": int(p.get("parti") or 1), "bas": _r(bas), "bit": _r(bas + sure), "sure": _r(sure), "plan_tipi": z.get("plan_tipi"),
                    "kesme": (x.get("kesme_cikis") or {}).get("tip") or ks.get("tip"), "ses_tasma_sn": float(ks.get("ses_tasma_sn") or 0),
                    "kullanim": {"bas": ku.get("bas"), "sure": ku.get("sure")},
                    "yogunluk": ((p.get("_derlenir") or {}).get("hikaye") or {}).get("yogunluk") or z.get("yogunluk"),
                    "duygu": ((p.get("_derlenir") or {}).get("hikaye") or {}).get("hedef_duygu") or p.get("duygu")})
    return out


def kurgu(kok, tur):
    """A16 T2: KURGU_PLANI_T2'nin ölçüleri (plan_kurgu.olcumler; tek ölçü tek kod), olay listesi, Z1/Z2 ve T0'a göre sapma.
    → KURGU/ZAMAN_T2.json · _RAPOR/ZAMAN_T2.json (Z1) · _RAPOR/ZAMAN_Z2_T2.json (Z2) · _RAPOR/SAPMA_T2.json."""
    ko = _alt_modul("kurgu_ortak"); plan_kurgu = _alt_modul("plan_kurgu")
    E = po.esik()
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(s, dict) or int(s.get("_surum", 1) or 1) < 2:
        print("!! v2 SAHNELER.json yok", flush=True); return 2
    yol, kp = ko.kurgu_plani(kok, "T2")
    if not kp:
        print("!! KURGU_PLANI_T2 yok (önce plan_kurgu.py)", flush=True); return 2
    h = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    pl = ko.sahne_planlari(kok, s)
    C = t2_cizelge(kp, pl); ev = olaylar(s, h, C)
    olc = plan_kurgu.olcumler(kp, pl)
    imza = po.imza([kp.get("planlar"), kp.get("diyalog"), h.get("sahneler")])
    toplam = C[-1]["bit"] if C else 0.0
    o1, u1 = z1(s, h, C, ev, E); o2, u2 = z2(s, h, C, E)
    t0 = ortak.json_oku(os.path.join(kok, "KURGU", "surumler", "KURGU_PLANI_T0.json"), {}) or {}
    t0_sure = {x.get("no"): float(x.get("sure") or 0) for x in t0.get("planlar") or [] if isinstance(x, dict)}
    esik = float(E.get("sapma_plan_oran_max", 0.25) or 0.25)
    sapma = []
    for c in C:
        a = t0_sure.get(c["no"])
        oran = round(abs(c["sure"] - a) / a, 3) if a else None
        sapma.append({"plan": c["no"], "t0": a, "t2": c["sure"], "oran": oran,
                      "seviye": "OLCULEMEDI" if oran is None else ("BAYRAK" if oran > esik else "GEC")})
    zarf = po.zarf("A16", SURUM, "GEC", imza)
    kp_rel = os.path.relpath(yol, kok).replace("\\", "/")
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "ZAMAN_T2.json"),
                     {"_surum": 1, "_uretim": zarf, "surum": "T2", "kurgu_plani": kp_rel, "kurgu_surumu": kp.get("kurgu_surumu"),
                      "toplam_sn": _r(toplam), "olcumler": olc, "olaylar": ev,
                      "egri": [{"t": t, "yogunluk": y, "duygu": d} for t, y, d in egri(C, E, 5.0)]})
    ortak.atomik_yaz(os.path.join(kok, "_RAPOR", "SAPMA_T2.json"),
                     {"_surum": 1, "_uretim": dict(zarf, sonuc="BAYRAK" if any(x["seviye"] == "BAYRAK" for x in sapma) else "GEC"),
                      "cizelge": "T2", "kurgu_plani": kp_rel, "esik": esik, "planlar": sapma})
    birim = [c["no"] for c in C]
    o1 += [po.m("sapma", "BAYRAK", x["plan"], olcu=x["oran"], esik=esik, kural="T2−T0") for x in sapma if x["seviye"] == "BAYRAK"]
    _, r1 = po.rapor_yaz(kok, "Z1", "T2", o1, asama="A16", arac=SURUM, birimler=birim, tur=tur, girdi_imza=imza,
                         varsayilan=os.path.join("_RAPOR", "ZAMAN_T2.json"),
                         ek={"uygulanmadi": u1, "toplam_sn": _r(toplam), "olcumler": olc, "kurgu_plani": kp_rel})
    _, r2 = po.rapor_yaz(kok, "Z2", "T2", o2, asama="A16", arac=SURUM, birimler=birim, tur=tur, girdi_imza=imza,
                         varsayilan=os.path.join("_RAPOR", "ZAMAN_Z2_T2.json"), ek={"uygulanmadi": u2})
    po.yaz_ozet(r1, "Z1 T2"); po.yaz_ozet(r2, "Z2 T2")
    print(f"T2: {len(C)} plan, {toplam:.1f} sn, ASL {olc.get('asl')}, {len(ev)} olay", flush=True)
    return max(po.cikis(r1), po.cikis(r2))


def _alt_modul(ad):
    """Alt aracı yükler; alt araç içe aktarılırken stdout'u yeniden yapılandırıyorsa (StringIO altında) gerçek stdout'la yükler."""
    import importlib
    if ad in sys.modules: return sys.modules[ad]
    o = sys.stdout
    try:
        if not hasattr(o, "reconfigure"): sys.stdout = sys.__stdout__
        return importlib.import_module(ad)
    finally: sys.stdout = o


def main(argv):
    if not argv or "-h" in argv or "--help" in argv: print(__doc__); return 4
    asama = po.arg_al(argv, "--asama")
    if asama not in ASAMA_T: print(__doc__); return 4
    if asama == "animatik": return _alt_modul("zaman_cizelgesi_t1").main(list(argv))     # T1 (adım 14)
    kok = po.film_kok(po.arg_al(argv, "--film"))
    if asama == "kurgu": return kurgu(kok, po.tur_no(argv))
    if asama != "kagit":
        print(f"!! zaman_cizelgesi {ASAMA_T[asama]} ({asama}) henüz yok: TASARIM §9 {SONRAKI[asama]} ile gelir.", flush=True)
        return 4
    return kagit(kok, po.tur_no(argv))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
