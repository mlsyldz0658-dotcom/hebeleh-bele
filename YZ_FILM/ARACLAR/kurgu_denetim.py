"""KURGU DENETİM — kesme simülasyonu (TASARIM §6.7, A12 tur 1, A16; [KU2] KR4 madde 2, §4.6.2, İ-6).

Kullanım:
  python kurgu_denetim.py --kesme-simule [--oneri KURGU/KESME_T1.json] [--cizelge T1|T2] [--tur N] --film <film>
      kesicinin önerilerini (en çok RE kesme_turu_oneri {plan 10, sahne 2}) tek tek çizelgeden çıkarır ve yeniden denetler →
      _RAPOR/KESME_SIMULE_<T>.json {oneriler[{no, tur, hedef, gecti, hatalar, bayraklar, kazanc_sn}], temiz, uygulanmasi_gereken}
  python kurgu_denetim.py [--hepsi] --film <film>    Z3 kurgu kapısı: kurgu_denetim_tam.py'dedir (adım 16, PR-12); yoksa 4 ORTAM.
Simülasyonun denetimleri (öneri başına, kalan çizelgede):
  - kurulum → kullanım (Z1 #29–32): HIKAYE.KURULUMLAR'ın kurulum ya da kullanım planı kesilirse, ya da aradaki süre RE
    kurulum_kullanim_min_sn'nin altına düşerse HATA (kurulum götüren kesme paydaya girmez).
  - anahtar olgu: olgunun tek taşıyıcısı (replik `tasidigi`, HIKAYE olgu `plan`/`replik`) kesilirse HATA; merak sorusu açan tek plan da.
  - dondurulmuş durum (Y58): kesilen plan(lar) dünya durumunu değiştiriyorsa (durum_ozet bas ≠ bit) ve kesme yeni komşulara zıplama
    getiriyorsa HATA.
  - vaat imgesi (zanaat.vaat_imgesi) taşıyan plan kesilemez (HATA); ana karakterin adı ilk 120 sn'de duyulmaz olursa HATA
    (RE kahraman_adi_max_sn); 180°: aynı sahne grubunda yeni komşuların kamera tarafı farklıysa HATA.
  - film toplam süresi RE film_sure_aralik_sn alt ucunun altına inerse BAYRAK (kâğıtta onaylı süre; kısaltma kurgucunun kararıdır).
Kesici önerisi biçimi (CIKTI/KESME_ONERI.json): {"oneriler": [{"tur": "plan", "plan": 63 | "planlar": [63, 64]} |
  {"tur": "sahne", "sahne": "S05"}, "gerekce", "kazanc_sn", "kayip"]}. Uygulama oranı kurgu_uygula --kuru'da zorlanır (≥ %50).
Çıkış kodları: 0 rapor yazıldı · 1 girdi yok/bozuk · 4 ORTAM (Z3 bu sürümde yok).
"""
import os, sys, re, json, math, copy, argparse
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import zaman_cizelgesi_t1 as t1

SURUM = "kurgu_denetim 1.0 (kesme-simule)"


def oneri_oku(film, cizelge, yol=None):
    yol = yol or os.path.join(film, "KURGU", "KESME_%s.json" % cizelge)
    j = ortak.json_oku(yol if os.path.isabs(yol) else os.path.join(film, yol))
    if j is None: return None, yol
    if isinstance(j, dict) and j.get("oneriler") is None and isinstance(j.get("kesmeler"), list):   # şablondaki kısa biçim
        out = []
        for x in j["kesmeler"]:
            if not isinstance(x, dict): continue
            ko = x.get("konum") if isinstance(x.get("konum"), dict) else {"plan": x.get("konum")}
            o = {"tur": x.get("tur") or ("sahne" if ko.get("sahne") else "plan"), "gerekce": x.get("neden"), "kayip": x.get("kayip"),
                 "kazanc_sn": x.get("kazanc_sn")}
            if o["tur"] == "sahne": o["sahne"] = ko.get("sahne")
            elif ko.get("planlar"): o["planlar"] = ko["planlar"]
            else: o["plan"] = ko.get("plan")
            out.append(o)
        return out, yol
    return (j.get("oneriler") if isinstance(j, dict) else j) or [], yol


def _hedef_planlar(o, plan):
    if o.get("tur") == "sahne" or (o.get("sahne") and not o.get("plan") and not o.get("planlar")):
        return [p["plan"] for p in plan["planlar"] if p.get("sahne_grubu") == o.get("sahne")], "sahne"
    ps = o.get("planlar") or ([o["plan"]] if o.get("plan") is not None else [])
    return [x for x in ps], "plan"


def tasiyicilar(hikaye, sahneler):
    """olgu/merak kimliği → onu taşıyan plan numaraları (replik tasidigi, olgu plan/replik alanları, _derlenir.hikaye.merak_ac)."""
    rep_plan = {}
    for p in (sahneler.get("sahneler") or []):
        rid = (p.get("replik") or {}).get("id")
        if rid: rep_plan.setdefault(rid, set()).add(p.get("no"))
    out = {}
    for r in hikaye.get("replikler") or []:
        for o in r.get("tasidigi") or []: out.setdefault(o, set()).update(rep_plan.get(r.get("id"), set()))
    for o in hikaye.get("anahtar_olgular") or []:
        if o.get("plan") is not None: out.setdefault(o.get("id"), set()).add(o["plan"])
        if o.get("replik"): out.setdefault(o.get("id"), set()).update(rep_plan.get(o["replik"], set()))
    for p in sahneler.get("sahneler") or []:
        for m in (((p.get("_derlenir") or {}).get("hikaye") or {}).get("merak_ac") or []): out.setdefault("merak:" + str(m), set()).add(p.get("no"))
    return out


def simule_et(plan, sahneler, hikaye, kesilen, tur):
    """(hatalar, bayraklar, kazanc_sn) — kesilen plan numaraları çizelgeden çıkarılınca."""
    H, B = [], []
    sp = {p.get("no"): p for p in sahneler.get("sahneler") or [] if isinstance(p, dict)}
    once = {p["plan"]: p for p in plan["planlar"]}
    k = copy.deepcopy(plan)
    k["planlar"] = [p for p in k["planlar"] if p["plan"] not in kesilen]
    k["diyalog"] = [d for d in k.get("diyalog") or [] if d.get("plan") not in kesilen]
    if not k["planlar"]: return ["bütün planlar kesiliyor"], [], 0.0
    t1.yeniden_zamanla(k)
    yeni = {p["plan"]: p for p in k["planlar"]}
    kazanc = round(sum(once[n]["sure"] for n in kesilen if n in once), 3)
    for kr in hikaye.get("KURULUMLAR") or []:
        a, b = kr.get("plan"), kr.get("kullanim_plan")
        if a in kesilen or b in kesilen:
            H.append("kurulum %s götürülüyor (plan %s)" % (kr.get("id"), a if a in kesilen else b)); continue
        if a in yeni and b in yeni:
            ara = yeni[b]["cizelge_bas"] - (yeni[a]["cizelge_bas"] + yeni[a]["sure"])
            if ara < float(t1.E("kurulum_kullanim_min_sn") or 20) and once[b]["cizelge_bas"] - (once[a]["cizelge_bas"] + once[a]["sure"]) >= float(t1.E("kurulum_kullanim_min_sn") or 20):
                H.append("kurulum %s → kullanım aralığı %.1f sn'ye iniyor (< %s)" % (kr.get("id"), ara, t1.E("kurulum_kullanim_min_sn")))
    for olgu, ps in tasiyicilar(hikaye, sahneler).items():
        if ps and ps <= set(kesilen):
            H.append(("merak sorusu %s'yi açan tek plan kesiliyor" % olgu[6:]) if olgu.startswith("merak:") else "olgu %s'nin tek taşıyıcısı kesiliyor" % olgu)
    for n in kesilen:
        s = sp.get(n) or {}
        if (s.get("zanaat") or {}).get("vaat_imgesi"): H.append("plan %s vaat imgesini taşıyor" % n)
    # dondurulmuş durum ve 180°: yeni komşular
    sira = [p["plan"] for p in plan["planlar"]]
    for n in kesilen:
        if n not in once: continue
        i = sira.index(n)
        onc = next((sira[j] for j in range(i - 1, -1, -1) if sira[j] not in kesilen), None)
        son = next((sira[j] for j in range(i + 1, len(sira)) if sira[j] not in kesilen), None)
        if onc is None or son is None: continue
        if any(once[x].get("etki_var") or _degisir(once[x]) for x in sira[sira.index(onc) + 1: sira.index(son)]):
            do, ds = once[onc].get("durum_ozet") or {}, once[son].get("durum_ozet") or {}
            if do.get("bit") and ds.get("bas") and do["bit"] != ds["bas"]:
                H.append("plan %s→%s: kesilen plan dünya durumunu değiştiriyordu; yeni komşular zıplıyor (Y58)" % (onc, son))
        if once[onc].get("sahne_grubu") == once[son].get("sahne_grubu"):
            ta = ((sp.get(onc) or {}).get("_derlenir") or {}).get("kamera_tarafi"); tb = ((sp.get(son) or {}).get("_derlenir") or {}).get("kamera_tarafi")
            if ta and tb and ta != tb: H.append("plan %s→%s: kamera tarafı değişiyor (180°)" % (onc, son))
    ana = [kid for kid, v in (hikaye.get("karakterler") or {}).items() if (v or {}).get("rol") == "kahraman"]
    if ana:
        rep = {r.get("id"): r for r in hikaye.get("replikler") or []}
        def ilk_ad(pl):
            for d in sorted(pl.get("diyalog") or [], key=lambda d: d.get("cizelge_bas") or 0):
                if set((rep.get(d.get("replik")) or {}).get("ad_soyler") or []) & set(ana): return d.get("cizelge_bas")
            return None
        once_t, sonra_t = ilk_ad(plan), ilk_ad(k); mx = float(t1.E("kahraman_adi_max_sn") or 120)
        if once_t is not None and once_t <= mx and (sonra_t is None or sonra_t > mx): H.append("kahramanın adı ilk %d sn'de duyulmuyor" % mx)
    alt = (t1.E("film_sure_aralik_sn") or [1800, 2700])[0]
    if plan.get("toplam_kare", 0) / t1.FPS >= alt > k["toplam_kare"] / t1.FPS:
        B.append("film süresi %.0f sn'ye iniyor (< %s)" % (k["toplam_kare"] / t1.FPS, alt))
    return H, B, kazanc


def _degisir(p):
    d = p.get("durum_ozet") or {}
    return bool(d) and d.get("bas") != d.get("bit")


def kesme_simule(film, cizelge="T1", tur=1, oneri_yolu=None, gorev=None):
    film = os.path.abspath(film)
    plan, pyol, n = t1.plan_oku(film, cizelge)
    if plan is None: raise FileNotFoundError("KURGU_PLANI_%s yok" % cizelge)
    t1.yeniden_zamanla(plan)
    oneriler, oyol = oneri_oku(film, cizelge, oneri_yolu)
    if oneriler is None: raise FileNotFoundError("kesme önerisi yok (%s)" % oyol)
    sahneler = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    hikaye = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    lim = t1.E("kesme_turu_oneri") or {"plan": 10, "sahne": 2, "uygulama_orani_min": 0.5}
    sayac = {"plan": 0, "sahne": 0}; out = []
    for i, o in enumerate(oneriler, 1):
        if not isinstance(o, dict): continue
        ps, tur_ = _hedef_planlar(o, plan)
        kayit = {"no": i, "tur": tur_, "hedef": o.get("sahne") if tur_ == "sahne" else ps, "gerekce": o.get("gerekce"),
                 "beklenen_kazanc_sn": o.get("kazanc_sn"), "kayip": o.get("kayip")}
        sayac[tur_] += len(ps) if tur_ == "plan" else 1
        if sayac[tur_] > lim.get(tur_, 10):
            kayit.update(gecti=False, hatalar=["öneri tavanı aşıldı (%s ≤ %s)" % (tur_, lim.get(tur_))], bayraklar=[], kazanc_sn=0, sayilmaz=True)
            out.append(kayit); continue
        bilinmeyen = [x for x in ps if x not in {p["plan"] for p in plan["planlar"]}]
        if not ps or bilinmeyen:
            kayit.update(gecti=False, hatalar=["plan bulunamadı: %s" % (bilinmeyen or o)], bayraklar=[], kazanc_sn=0); out.append(kayit); continue
        H, B, kaz = simule_et(plan, sahneler, hikaye, ps, tur_)
        kayit.update(gecti=not H, hatalar=H, bayraklar=B, kazanc_sn=kaz,
                     uygulayan="hikaye-yazari" if tur_ == "sahne" else "kurgucu")
        out.append(kayit)
    temiz = [o for o in out if o.get("gecti")]
    r = {"_surum": 1, "_uretim": {"asama": "A12" if cizelge == "T1" else "A16", "gorev": gorev, "girdi_imza": t1.sha(pyol),
                                  "arac_surum": SURUM, "esik_surum": t1._esik_surum(), "sonuc": "GEC", "zaman": t1.simdi(), "ortam": t1.ortam()},
         "cizelge": cizelge, "tur": tur, "kurgu_plani": os.path.relpath(pyol, film).replace("\\", "/"),
         "oneri_dosyasi": os.path.relpath(oyol, film).replace("\\", "/") if os.path.isabs(oyol) else oyol,
         "oneriler": out, "temiz": len(temiz), "reddedilen": len(out) - len(temiz),
         "uygulama_orani_min": lim.get("uygulama_orani_min", 0.5),
         "uygulanmasi_gereken": math.ceil(lim.get("uygulama_orani_min", 0.5) * len(temiz) - 1e-9),
         "kesme_uygulama_payda": "simulasyon_temiz", "uygulandi": None}
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", "KESME_SIMULE_%s.json" % cizelge), r)
    return r


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kurgu denetimi (kesme simülasyonu).")
    ap.add_argument("--kesme-simule", action="store_true"); ap.add_argument("--hepsi", action="store_true"); ap.add_argument("--oneri")
    ap.add_argument("--cizelge"); ap.add_argument("--tur", type=int); ap.add_argument("--film"); ap.add_argument("--saglayici")
    o, kalan = ap.parse_known_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film): print("!! --film <film klasörü> gerekli."); return 1
    g = t1.gorev_baglami(o.tur)
    if o.kesme_simule:
        cz = o.cizelge or ("T1" if (g.get("asama") or "A12") == "A12" else "T2")
        try: r = kesme_simule(film, cz, g["tur"], o.oneri, g["id"])
        except FileNotFoundError as e: print("!! " + str(e)); return 1
        print(json.dumps({"temiz": r["temiz"], "reddedilen": r["reddedilen"], "uygulanmasi_gereken": r["uygulanmasi_gereken"]}, ensure_ascii=False))
        return 0
    try:
        import kurgu_denetim_tam
    except ImportError:
        print("Z3 kurgu kapısı (kurgu_denetim --hepsi / varsayılan) bu sürümde yok (TASARIM §9 adım 16, PR-12). Bu aşama bu kurulumda yürüyemez.")
        return 4
    return kurgu_denetim_tam.main(argv)


if __name__ == "__main__":
    sys.exit(main())
