"""KAMERA AĞACI — plaka → ana kare → türev → planlanmış görsel ağacı, bayat yayılımı ve kâğıt sonu (TASARIM §6.4, D-15, A09, A11;
[YN2] §4.6.1, Y41–Y43).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"):
  python kamera_agaci.py --film <film>              A09: KAMERA_AGACI.json + KAGIT_TAMAM.json (kâğıt sonu özeti)
  python kamera_agaci.py --yalniz-agac --film <film>   yalnız ağaç (KAGIT_TAMAM yazılmaz)
  python kamera_agaci.py --bayat <düğüm> --film <film> düğümü ve bütün çocuklarını elle bayat işaretler (ör. ana_kare:S02/KAM5)
Kodda: kur(sahneler, K) → düğümler · bayat_yay(yeni, eski) · kagit_tamam(kok)
Düğümler (id → {tur, ebeveyn, basamak, mekan, sahne, plan, kurulum, imza, bayat, gorsel}):
  kart:<karakter>              evren kartı (kök; A10d'de kilitlenir)
  plaka:<mekan>/<plaka>        boş mekân plakası (kök; basamak 1)
  ana_kare:<sahne>/<kurulum>   kurulumun ana karesi; ebeveyni kurulumun ebeveyni (plaka ya da aynı sahnede başka kurulumun ana karesi)
  plan:<no>                    planın planlanmış görseli (D-15: her plana; animatik ve yedek). Ebeveyn: zincir.baslangic'a göre
                               ana_kare (aynı kurulum) · turev (zincir.ebeveyn "KAM1@1") · kart (kimlik kartı) · son_kare (önceki plan)
  basamak = kökten uzaklık; Gemini paketleri basamak sırasıyla gider (önce plakalar, sonra ana kareler, sonra türevler).
Bayat: düğümün imzası (kendi tanımı + ebeveyn imzası) önceki ağaçtakinden farklıysa düğüm ve bütün çocukları bayat: true olur; önceki
  görsel kaydı (gorsel) korunur ama yeniden üretilecekler listesine girer. Y43: plaka → plan derinliği > plan_agac_derinlik_max BAYRAK.
KAGIT_TAMAM.json: SAHNELER v2 + DUNYA_DEFTERI + K0 / Z0 / ISTEM / S0 raporları engelsiz (GEÇ, BAYRAK, KISMI değil) ve ağaç kuruldu →
  tamam: true. Eksik ya da HATA'lı her kalem "eksikler"de.
Çıkış kodları: 0 tamam · 1 HATA (ağaç kurulamadı ya da kâğıt tamam değil) · 2 SAHNELER.json yok · 4 kullanım.
"""
import os, sys, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "kamera_agaci 1.0"
AGAC = "KAMERA_AGACI.json"
KAGIT_RAPORLARI = (("K0", "_RAPOR/K0_FILM.json"), ("Z0", "_RAPOR/Z0_FILM.json"), ("ISTEM", "_RAPOR/ISTEM_FILM.json"),
                   ("S0", "_RAPOR/S0_FILM.json"), ("Z1", "_RAPOR/ZAMAN_T0.json"))


def _plaka_id(mid, e):
    e = str(e or "")
    if e.startswith("plaka:"): e = e.split(":", 1)[1]
    return f"plaka:{mid}/{e.split('@')[0]}"


def kur(s, K, E=None):
    """(düğümler, bayraklar)."""
    E = E or po.esik(); D, bay = {}, []
    def ekle(i, **v):
        if i not in D: D[i] = dict(v, id=i)
        return D[i]
    for kid in (s.get("karakterler") or {}):
        ekle(f"kart:{kid}", tur="kart", ebeveyn=None, tanim={"evren": (s["karakterler"][kid] or {}).get("evren")})
    for mid, mv in K.mekanlar.items():
        for pid, pv in ((mv.get("kroki") or {}).get("plakalar") or {}).items():
            ekle(f"plaka:{mid}/{pid}", tur="plaka", ebeveyn=None, mekan=mid, tanim=pv)
    P = sorted(s.get("sahneler") or [], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0))
    gruplar = s.get("sahne_gruplari") or {}
    def ana_kare(sid, mid, kurulum, derin=0):
        i = f"ana_kare:{sid}/{kurulum}"
        if i in D or derin > 6: return i
        kv = K.kurulum(mid, kurulum) or {}
        e = kv.get("ebeveyn")
        if not e: par = None; bay.append(po.m("kurulum_ebeveynsiz", "BAYRAK", None, sahne=sid, olcu=kurulum, kural="Y60"))
        elif str(e).startswith("plaka:"): par = _plaka_id(mid, e)
        else: par = ana_kare(sid, mid, str(e).split("@")[0], derin + 1)
        if par and par.startswith("plaka:") and par not in D:
            ekle(par, tur="plaka", ebeveyn=None, mekan=mid, tanim=None, eksik=True)
            bay.append(po.m("plaka_tanimsiz", "BAYRAK", None, sahne=sid, olcu=par, kural="Y60"))
        ak = ((gruplar.get(sid) or {}).get("_derlenir") or {}).get("ana_kareler")
        ekle(i, tur="ana_kare", ebeveyn=par, mekan=mid, sahne=sid, kurulum=kurulum, plan=ak.get(kurulum) if isinstance(ak, dict) else None,
             tanim=kv)
        return i
    onceki = None
    for p in P:
        z = p.get("zanaat") or {}; sid = z.get("sahne_grubu"); mid = (gruplar.get(sid) or {}).get("mekan")
        kam = (z.get("kamera") or {}).get("kurulum"); zn = z.get("zincir") or {}; bas = zn.get("baslangic"); ref = None
        if bas == "kart":
            kim = [k.get("id") for k in z.get("kadrajdakiler") or [] if isinstance(k, dict) and k.get("id")]
            ref = [f"kart:{k}" for k in kim]                   # kart başlangıcı: kurulumun ana karesi kart + plakadan üretilir
            par = ana_kare(sid, mid, kam) if kam else (_plaka_id(mid, zn["ebeveyn"]) if str(zn.get("ebeveyn") or "").startswith("plaka:")
                                                         else (ref[0] if ref else None))
        elif bas == "son_kare":
            par = f"plan:{onceki.get('no')}" if onceki else None
        elif bas == "turev":
            e = str(zn.get("ebeveyn") or kam or "").split("@")[0]
            par = ana_kare(sid, mid, e) if e and not e.startswith("plaka:") else _plaka_id(mid, e)
        else:                                                   # ana_kare (varsayılan)
            par = ana_kare(sid, mid, kam) if kam else None
        tanim = {"kamera": z.get("kamera"), "kadrajdakiler": z.get("kadrajdakiler"), "baslangic": bas,
                 "durum": (p.get("uretim") or {}).get("durum_dondu") or (p.get("_derlenir") or {}).get("referans")}
        ekle(f"plan:{p.get('no')}", tur="plan", ebeveyn=par, referanslar=ref if bas == "kart" else None, mekan=mid, sahne=sid, plan=p.get("no"), kurulum=kam, tanim=tanim,
             zincir=zn.get("gecis_turu"), bitis_sabitle=bool(zn.get("bitis_sabitle")))
        onceki = p
    # basamak ve imza
    def basamak(i, yol=()):
        d = D[i]
        if "basamak" in d: return d["basamak"]
        if i in yol: d["basamak"] = 99; bay.append(po.m("agac_dongusu", "HATA", d.get("plan"), olcu=i)); return 99
        d["basamak"] = 1 if not d.get("ebeveyn") or d["ebeveyn"] not in D else basamak(d["ebeveyn"], yol + (i,)) + 1
        return d["basamak"]
    def imza(i):
        d = D[i]
        if "imza" not in d: d["imza"] = po.imza([d.get("tanim"), imza(d["ebeveyn"]) if d.get("ebeveyn") in D else None])
        return d["imza"]
    for i in list(D): basamak(i); imza(i)
    mx = E.get("plan_agac_derinlik_max", 3)
    for i, d in D.items():
        if d["tur"] == "plan" and d.get("zincir") != "devam":
            derin = d["basamak"]                                   # plaka = 1 … plan
            if _kok(D, i) == "plaka" and derin > mx:
                bay.append(po.m("agac_derin", "BAYRAK", d.get("plan"), olcu=derin, esik=mx, kural="Y43",
                                neden="plaka → plan zinciri 3 düğümden derin: yeniden demirle (ana kareyi plakadan türet)"))
    return D, bay


def _kok(D, i):
    seen = 0
    while D[i].get("ebeveyn") in D and seen < 50: i = D[i]["ebeveyn"]; seen += 1
    return D[i]["tur"]


def bayat_yay(D, eski):
    """Önceki ağaçla karşılaştır: imzası değişen ya da ebeveyni bayat olan düğüm bayattır; önceki görsel kaydı korunur."""
    ed = (eski or {}).get("dugumler") or {}
    sira = sorted(D, key=lambda i: D[i].get("basamak", 0))
    for i in sira:
        d = D[i]; e = ed.get(i)
        if e and e.get("gorsel"): d["gorsel"] = e["gorsel"]
        par_bayat = bool(d.get("ebeveyn") in D and D[d["ebeveyn"]].get("bayat"))
        d["bayat"] = bool(e) and (e.get("imza") != d["imza"] or par_bayat or bool(e.get("bayat") and not e.get("gorsel_yeni")))
        if not e: d["yeni"] = True
    return [i for i in sira if D[i].get("bayat")]


def _elle_bayat(D, kok_id):
    out = []
    def git(i):
        D[i]["bayat"] = True; out.append(i)
        for j, d in D.items():
            if d.get("ebeveyn") == i: git(j)
    if kok_id in D: git(kok_id)
    return out


def paketler(D):
    """Gemini paket sırası: basamak → üretilecek düğümler (kart ve plaka kökleri dahil; görseli olan ve bayat olmayan atlanır)."""
    out = {}
    for i, d in D.items():
        if d.get("gorsel") and not d.get("bayat"): continue
        out.setdefault(d["basamak"], []).append(i)
    return [{"basamak": b, "dugumler": sorted(v)} for b, v in sorted(out.items())]


def agac_yaz(kok, elle=None):
    import kroki
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(s, dict) or int(s.get("_surum", 1) or 1) < 2: return None, [po.m("sahneler_yok", "HATA")]
    K = kroki.Kroki(kok, s); D, bay = kur(s, K)
    eski = ortak.json_oku(os.path.join(kok, AGAC), {}) or {}
    bayat = bayat_yay(D, eski)
    if elle: bayat = sorted(set(bayat) | set(_elle_bayat(D, elle)))
    for d in D.values(): d.pop("tanim", None)
    v = {"_surum": 1, "_uretim": po.zarf("A09", SURUM, "HATA" if any(b["seviye"] == "HATA" for b in bay) else "GEC", po.imza(sorted(d["imza"] for d in D.values()))),
         "dugumler": D, "bayat": bayat, "paketler": paketler(D), "bayraklar": bay,
         "ozet": {"plaka": sum(d["tur"] == "plaka" for d in D.values()), "ana_kare": sum(d["tur"] == "ana_kare" for d in D.values()),
                  "plan": sum(d["tur"] == "plan" for d in D.values()), "kart": sum(d["tur"] == "kart" for d in D.values()),
                  "derinlik_max": max([d["basamak"] for d in D.values()] or [0])}}
    ortak.atomik_yaz(os.path.join(kok, AGAC), v)
    return v, bay


def kagit_tamam(kok, agac):
    import kapi
    eksik, raporlar = [], {}
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(s, dict) or int(s.get("_surum", 1) or 1) < 2: eksik.append("SAHNELER.json v2")
    else:
        bos = [p.get("no") for p in s.get("sahneler") or [] if not p.get("hareket_istem")]
        if bos: eksik.append(f"hareket_istem derlenmemiş: {bos[:10]}")
    if not os.path.isfile(os.path.join(kok, "DUNYA_DEFTERI.json")): eksik.append("DUNYA_DEFTERI.json")
    for k, rel in KAGIT_RAPORLARI:
        r = ortak.json_oku(os.path.join(kok, rel))
        if not isinstance(r, dict): eksik.append(rel); raporlar[k] = None; continue
        raporlar[k] = {"rapor": rel, "sonuc": r.get("sonuc")}
        if not kapi.engelsiz_mi(r.get("sonuc")) or r.get("sonuc") == "KISMI": eksik.append(f"{k} {r.get('sonuc')}")
    if agac is None or any(b["seviye"] == "HATA" for b in (agac or {}).get("bayraklar") or []): eksik.append(AGAC)
    v = {"_surum": 1, "_uretim": po.zarf("A09", SURUM, "GEC" if not eksik else "HATA"), "tamam": not eksik, "eksikler": eksik,
         "raporlar": raporlar, "plan_sayisi": len((s or {}).get("sahneler") or []) if isinstance(s, dict) else 0,
         "kamera_agaci": AGAC if agac else None,
         "not": "Kâğıt bitti: görsel ve ses hazırlığı (A10–A11) bu dosyayla açılır." if not eksik else "Kâğıt tamam değil; eksikler kapanmadan A10'a geçilmez."}
    ortak.atomik_yaz(os.path.join(kok, "KAGIT_TAMAM.json"), v)
    return v


def main(argv):
    if not argv or "-h" in argv or "--help" in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film"))
    if not os.path.isfile(os.path.join(kok, "SAHNELER.json")): print("!! SAHNELER.json yok", flush=True); return 2
    v, bay = agac_yaz(kok, po.arg_al(argv, "--bayat"))
    if v is None: print("!! v2 SAHNELER.json değil", flush=True); return 1
    o = v["ozet"]
    print(f"kamera ağacı: {o['plaka']} plaka, {o['ana_kare']} ana kare, {o['plan']} plan, derinlik {o['derinlik_max']}, bayat {len(v['bayat'])},"
          f" BAYRAK {sum(b['seviye'] == 'BAYRAK' for b in bay)}", flush=True)
    if "--yalniz-agac" in argv or po.arg_al(argv, "--bayat"): return 1 if any(b["seviye"] == "HATA" for b in bay) else 0
    t = kagit_tamam(kok, v)
    print("KAGIT_TAMAM: " + ("tamam" if t["tamam"] else "eksik → " + "; ".join(t["eksikler"])), flush=True)
    return 0 if t["tamam"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
