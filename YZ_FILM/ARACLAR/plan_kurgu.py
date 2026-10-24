"""PLAN KURGU — kaba kurgu çizelgesi T2'yi kurar (TASARIM §6.7, §1.3 A16; [KU2] KR6, §4.5.1).

Kullanım:
  python plan_kurgu.py --film <film> [--saglayici sahte] [--cizelge T2]
      → KURGU/surumler/KURGU_PLANI_T2_v<N>.json + KURGU/KURGU_PLANI.json (son sürüm) + KURGU/KIRP_INCELE.md + KURGU/KIRP_ONERI.json
Girdi: SAHNELER.json v2 (sira, kullanim, zanaat), SIRALI_VIDEO/NNN.mp4, SESLER/diyalog.json v2 (kelime ve klip zamanları), önceki KURGU_PLANI
(T1 ya da T2: sıra, kartlar, karartmalar, örtü planları, kurgucu ve kullanıcı kararları).
İş:
  1. Her plan için kirp_oner (kullanim + guven + gerekce). kullanim_kaynak kurgucu/kullanici ya da kullanim_kilit zincir/kullanici olan
     değer olduğu gibi kalır (kullanıcının kararı hiçbir otomatik araçla değişmez). Videosu olmayan plan yer_tutucu (görsel + yavaş zoom) olur.
  2. Senkron korumalı bölme (aynı klipten iki plan, replik aradaki planın üstünden sürüyorsa): parca2.bas = parca1.bas + parca1.sure + aradaki.
  3. Çizelge boşluksuz: planlar[i+1].cizelge_bas = planlar[i].cizelge_bas + sure (planlı karartma tek istisna); bütün değerler 1/24 sn.
  4. Diyalog senkron kuralıyla: görünen konuşan → cizelge_bas = plan.cizelge_bas + (klip_zamani.bas − kullanim.bas) / hiz; plan sonunu
     aşan ses L taşması, plan başından önce başlayan J; ekran dışı replik (zanaat.ekran_disi_ses) üzerine konduğu planın çizelgesinde.
  5. Kalıcı işlem katmanı KURGU/KURGU_DUZEN_T2.json (kurgu_uygula yazar) yeniden uygulanır (zaman_cizelgesi_t1'in T1'de yaptığı gibi):
     diyalog_kaydir, ekran_disi, jl, kes … yeniden kuruluşta kaybolmaz. Önceki sürümden zaten taşınan hiz ve ortu ikinci kez uygulanmaz.
  6. Ölçüler: toplam süre, ASL (film, ilk 120, ilk 30), J/L oranı, tepki oranı. zaman_cizelgesi.py varsa "--asama kurgu" çağrılır (T2 ölçüleri
     ve SAPMA_T2 orada; tek ölçü tek kod).
Ses görevleri (diyalog_esitle, ses_katmani T2, muzik --yerlestir, son_miks) bu sürümün imzasıyla görev defterindeki sonraki gruplarda koşar.
Çıkış kodları: 0 tamam · 1 hata · 2 SAHNELER yok · 4 kullanım.
"""
import os, sys, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kurgu_ortak as ko, kirp_oner

SURUM = "plan_kurgu 1.0"


def _sira_anahtari(p): return (float(p.get("sira", p.get("no", 0)) or 0), p.get("no", 0))


def _kilit(onceki):
    if not onceki: return None
    g = onceki.get("goruntu") or {}
    kay, kil = g.get("kullanim_kaynak"), g.get("kullanim_kilit")
    if kil in ("kullanici", "zincir") or kay in ("kullanici", "kurgucu"):
        return {"kullanim": g["kullanim"], "kaynak": kil if kil in ("kullanici", "zincir") else kay}
    return None


def _goruntu(kok, p, klip, oneri, onceki):
    z = ko.zanaat(p); no = p["no"]; var = os.path.exists(klip)
    g = {"tur": "video" if var else "yer_tutucu", "dosya": ko.goreli(kok, klip) if var else _gorsel(kok, no),
         "dosya_ozet": ko.sha1(klip) if var else None, "klip_sn": float(oneri["olculen"].get("klip_sn") or z.get("klip_sn") or 8),
         "kaynak_klip": z.get("kaynak_klip"), "kullanim": oneri["kullanim"], "kullanim_kaynak": oneri.get("kullanim_kaynak", "otomatik"),
         "kullanim_kilit": ((onceki or {}).get("goruntu") or {}).get("kullanim_kilit"), "guven": oneri["guven"],
         "gerekce": oneri["gerekce"], "hiz": float(((onceki or {}).get("goruntu") or {}).get("hiz") or 1.0),
         "ayna": bool(((onceki or {}).get("goruntu") or {}).get("ayna")), "kadraj_kirpma": ((onceki or {}).get("goruntu") or {}).get("kadraj_kirpma"),
         "olculen": oneri.get("olculen") or {}, "adimlar_olculen": oneri.get("adimlar_olculen") or []}
    if z.get("plan_tipi") == "kart": g["tur"] = "kart"
    if oneri.get("bayraklar"): g["bayraklar"] = oneri["bayraklar"]
    return g


def _gorsel(kok, no):
    for uz in ("png", "jpg", "jpeg", "webp"):
        p = os.path.join(kok, "SIRALI_GORSEL", f"{int(no):03d}.{uz}")
        if os.path.exists(p): return ko.goreli(kok, p)
    return None


def _bolme_duzelt(planlar, pl, d):
    """Senkron korumalı klip bölme ([KU2] §4.5.1): aynı kaynak klipten gelen parçada replik aradaki planların üstünden sürüyorsa
    parca2.kullanim.bas = parca1.kullanim.bas + parca1.sure + aradaki_planlarin_suresi."""
    for i, x in enumerate(planlar):
        kk = x["goruntu"].get("kaynak_klip")
        if kk is None or x["goruntu"].get("kullanim_kaynak") == "kullanici": continue
        j = next((k for k in range(i - 1, -1, -1) if planlar[k]["plan"] == kk or planlar[k]["goruntu"].get("kaynak_klip") == kk), None)
        if j is None: continue
        a = planlar[j]["goruntu"]["kullanim"]; arada = sum(planlar[k]["sure"] for k in range(j + 1, i))
        surer = any(r.get("kaynak_plan") == kk and (r.get("klip_zamani") or {}).get("bit", 0) > a["bas"] + a["sure"]
                    for r in (d.get("replikler") or {}).values())
        if surer:
            yb = ko.kare(a["bas"] + planlar[j]["sure"] * float(planlar[j]["goruntu"]["hiz"]) + arada)
            ust = float(x["goruntu"]["klip_sn"]) - float(ko.esik("kullanim_son_pay_sn", 0.5))
            x["goruntu"]["kullanim"]["bas"] = yb
            x["goruntu"]["kullanim"]["sure"] = ko.kare(max(ko.KARE, min(x["goruntu"]["kullanim"]["sure"], ust - yb)))
            if ust - yb < 0.5: x["goruntu"].setdefault("bayraklar", []).append({"madde": "bolme_pencere_dar", "neden": "kaynak klipte süre kalmadı"})
            x["goruntu"]["gerekce"] += "; senkron korumalı bölme (replik aradaki planın üstünden sürüyor)"
            x["sure"] = ko.kare(x["goruntu"]["kullanim"]["sure"] / float(x["goruntu"]["hiz"]))


def cizelgele(planlar, karartmalar=()):
    ek = {k.get("sonra_plan"): float(k.get("sure") or 0) for k in karartmalar or []}
    t = 0.0
    for x in planlar:
        x["cizelge_bas"] = ko.kare(t); x["sure"] = ko.kare(x["goruntu"]["kullanim"]["sure"] / float(x["goruntu"].get("hiz") or 1.0))
        t = x["cizelge_bas"] + x["sure"] + ek.get(x["plan"], 0.0)
    return ko.kare(t)


def diyalog_yerlestir(kok, kp, pl, d):
    """Diyalog yerleşimi (senkron kuralı, J/L, ekran dışı). kp['diyalog'] listesini baştan kurar."""
    planlar = kp["planlar"]; dizin = {x["plan"]: x for x in planlar}; out = []
    ekran_disi = {}
    for no, p in pl.items():
        e = ko.zanaat(p).get("ekran_disi_ses")
        if isinstance(e, dict) and e.get("replik"): ekran_disi[e["replik"]] = (no, e)
    replikler = dict(d.get("replikler") or {})
    for no, p in pl.items():                          # diyalog.json yoksa plan düzeyinden (animatik/T1 verisi)
        r = p.get("replik") or {}
        if r.get("id") and r["id"] not in replikler:
            rz = ((p.get("_derlenir") or {}).get("replik_zaman") or {}).get(r["id"])
            if rz: replikler[r["id"]] = {"karakter": r.get("karakter"), "kaynak_plan": no, "klip_zamani": {"bas": rz[0], "bit": rz[1]},
                                         "yol_plan": (ko.zanaat(p).get("ses") or {}).get("diyalog", {}).get("yol")}
    for rid, r in sorted(replikler.items()):
        kz = r.get("klip_zamani") or {}
        if rid in ekran_disi:
            hedef, e = ekran_disi[rid]; x = dizin.get(hedef)
            if not x: continue
            sure = float(((r.get("tts") or {}).get("sure_sn")) or (kz.get("bit", 0) - kz.get("bas", 0)) or 2.0)
            bas = ko.kare(x["cizelge_bas"] + float(e.get("bas", ko.esik("diyalog_giris_payi_sn", 0.4))))
            out.append({"replik": rid, "parca": 0, "plan": hedef, "kaynak": f"SESLER/diyalog.json#{rid}", "klip_zamani": None,
                        "cizelge_bas": bas, "sure": ko.kare(sure), "gorunen_konusan": False, "ekran_disi": True,
                        "karakter": r.get("karakter"), "jl": None})
            continue
        x = dizin.get(r.get("kaynak_plan"))
        if not x or kz.get("bas") is None: continue
        g = x["goruntu"]; hiz = float(g.get("hiz") or 1.0)
        tts = r.get("yol_gercek", r.get("yol_plan")) == "tts"
        sure = float(((r.get("tts") or {}).get("sure_sn")) if tts and (r.get("tts") or {}).get("sure_sn") else kz["bit"] - kz["bas"]) / hiz
        bas = ko.kare(x["cizelge_bas"] + (float(kz["bas"]) - float(g["kullanim"]["bas"])) / hiz)
        bit = bas + sure; ps, pb = ko.plan_sonu(x), x["cizelge_bas"]; jl = None
        if bit > ps + ko.KARE:
            ust = [y["plan"] for y in planlar if y["cizelge_bas"] < bit - 1e-6 and ko.plan_sonu(y) > ps + 1e-6 and y is not x]
            jl = {"tip": "L", "tasma_sn": round(bit - ps, 3), "uzerindeki_planlar": ust}
        elif bas < pb - ko.KARE:
            ust = [y["plan"] for y in planlar if ko.plan_sonu(y) > bas + 1e-6 and y["cizelge_bas"] < pb - 1e-6 and y is not x]
            jl = {"tip": "J", "tasma_sn": round(pb - bas, 3), "uzerindeki_planlar": ust}
        out.append({"replik": rid, "parca": 0, "plan": x["plan"], "kaynak": f"SESLER/diyalog.json#{rid}",
                    "klip_zamani": {"bas": kz["bas"], "bit": kz["bit"]}, "cizelge_bas": bas, "sure": ko.kare(sure),
                    "gorunen_konusan": not tts, "ekran_disi": tts, "karakter": r.get("karakter"), "jl": jl})
    kp["diyalog"] = sorted(out, key=lambda y: y["cizelge_bas"])
    return kp["diyalog"]


def olcumler(kp, pl):
    ps = [x for x in kp["planlar"] if x["goruntu"]["tur"] != "kart"]; top = ko.toplam_sure(kp)
    asl = lambda xs: round(sum(x["sure"] for x in xs) / len(xs), 3) if xs else None
    dg = kp.get("diyalog") or []
    diyalog_gruplari = {ko.zanaat(p).get("sahne_grubu") for p in pl.values() if ko.zanaat(p).get("plan_tipi") == "diyalog"}
    dp = [x for x in ps if x.get("sahne_grubu") in diyalog_gruplari]
    return {"toplam_sn": top, "asl": asl(ps), "asl_ilk120": asl([x for x in ps if x["cizelge_bas"] < 120]),
            "asl_ilk30": asl([x for x in ps if x["cizelge_bas"] < 30]),
            "jl_orani_diyalog": round(sum(1 for y in dg if y.get("jl")) / len(dg), 3) if dg else None,
            "tepki_orani_diyalog": round(sum(1 for x in dp if ko.zanaat(pl.get(x["plan"], {})).get("plan_tipi") == "tepki") / len(dp), 3)
            if dp else None}


def kur(kok, argv=(), cizelge="T2"):
    s = ko.sahneler(kok); pl = ko.sahne_planlari(kok, s)
    if not pl: return None, None
    _, onceki = ko.kurgu_plani(kok)
    onceki = onceki or {}
    o_dizin = {x.get("plan"): x for x in onceki.get("planlar") or []}
    kesilen = set(onceki.get("kesilen") or []) | set(onceki.get("kesilenler") or [])
    d = ko.diyalog_oku(kok); E = ko.po.esik()
    sira = sorted((p for p in pl.values() if p["no"] not in kesilen), key=_sira_anahtari)
    if o_dizin:                                            # kurgucu/kullanıcı sırası korunur; yeni planlar kendi sırasıyla araya
        eski_sira = [x["plan"] for x in onceki["planlar"] if x.get("plan") in pl and x["plan"] not in kesilen]
        yeni = [p["no"] for p in sira if p["no"] not in eski_sira]
        sira_no = list(eski_sira)
        for n in yeni:
            k = next((i for i, m in enumerate(sira_no) if _sira_anahtari(pl[m]) > _sira_anahtari(pl[n])), len(sira_no))
            sira_no.insert(k, n)
        sira = [pl[n] for n in sira_no]
    planlar, oneriler = [], {}
    ortuler = [x for x in onceki.get("planlar") or [] if x.get("ortu")]
    for p in sira:
        no = p["no"]; z = ko.zanaat(p); onc = o_dizin.get(no)
        kaynak = z.get("kaynak_klip") or no
        klip = ko.klip_yolu(kok, kaynak)
        ks = kirp_oner.kelimeler_klipte(d, kaynak)
        rz = ((p.get("_derlenir") or {}).get("replik_zaman") or {})
        if not ks and rz: ks = [{"w": "…", "bas": float(v[0]), "bit": float(v[1])} for v in rz.values()]
        oneri = kirp_oner.oner(kok, p, klip, ks, zincir=bool((z.get("zincir") or {}).get("bitis_sabitle")), kilit=_kilit(onc), E=E)
        oneriler[str(no)] = oneri
        g = _goruntu(kok, p, klip, oneri, onc)
        if onc and onc.get("goruntu", {}).get("dosya_ozet") and g.get("dosya_ozet") and onc["goruntu"]["dosya_ozet"] != g["dosya_ozet"]:
            g["yeniden_cekildi"] = True                     # S5.7: efekt ve müzik yeniden kurulur
        dd = (p.get("uretim") or {}).get("durum_dondu") or {}
        planlar.append({"sira": p.get("sira", no), "plan": no, "parti": p.get("parti"), "sahne_grubu": z.get("sahne_grubu"),
                        "izleme_parcasi": (onc or {}).get("izleme_parcasi"), "goruntu": g, "cizelge_bas": 0.0, "sure": 0.0,
                        "kesme_giris": {"tip": planlar[-1]["kesme_cikis"]["tip"]} if planlar else {"tip": "giris"},
                        "kesme_cikis": {"tip": (z.get("kesme") or {}).get("tip", "duz"), "adim": (z.get("kesme") or {}).get("adim")},
                        "durum_ozet": {"bas": dd.get("bas"), "bit": dd.get("bit")},
                        "etkili": any(bool(a.get("etki")) for a in z.get("eylem_zinciri") or [])})
    for o in ortuler:                                       # örtü planları (kurgucu ortu işlemi) önceki yerlerinde kalır
        araya = o.get("araya") or []
        k = next((i + 1 for i, x in enumerate(planlar) if araya and x["plan"] == araya[0]), None)
        if k is not None: planlar.insert(k, o)
    for x in planlar: x["sure"] = ko.kare(x["goruntu"]["kullanim"]["sure"] / float(x["goruntu"].get("hiz") or 1.0))
    cizelgele(planlar, onceki.get("karartmalar"))
    _bolme_duzelt(planlar, pl, d)
    cizelgele(planlar, onceki.get("karartmalar"))
    kartlar = []
    dizin = {x["plan"]: x for x in planlar}
    for k in onceki.get("kartlar") or []:
        k = dict(k)
        if k.get("plan") in dizin: k["cizelge_bas"] = ko.kare(dizin[k["plan"]]["cizelge_bas"] + float(k.get("ofset", 0.0)))
        kartlar.append(k)
    kp = {"_sahip": "kurgu", "film": s.get("film") or os.path.basename(kok), "cizelge": cizelge, "fps": ko.FPS,
          "kurgu_surumu": ko.sonraki_surum(kok), "girdi_imzalari": {
              "SAHNELER.json": ko.sha1(os.path.join(kok, "SAHNELER.json"), 8),
              "SESLER/diyalog.json": ko.sha1(os.path.join(kok, "SESLER", "diyalog.json"), 8)},
          "planlar": planlar, "diyalog": [], "kartlar": kartlar, "karartmalar": list(onceki.get("karartmalar") or []),
          "kullanici_kilitleri": list(onceki.get("kullanici_kilitleri") or []), "kesilen": sorted(kesilen),
          "onceki_surum": onceki.get("kurgu_surumu")}
    diyalog_yerlestir(kok, kp, pl, d)
    duzen_uygula(kok, kp, s, cizelge)
    kp["olcumler"] = olcumler(kp, pl)
    kp["_uretim"] = ko.po.zarf("A16", SURUM, "GEC", girdi_imza=ko.po.imza(kp["girdi_imzalari"]))
    yol = ko.kurgu_plani_yaz(kok, kp, cizelge)
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "KIRP_ONERI.json"), {"_uretim": kp["_uretim"], "planlar": oneriler})
    kirp_oner.incele_md(kok, oneriler, float(E.get("kirp_guven_min", 0.6)))
    return yol, kp


TASINAN_ISLEMLER = ("hiz", "ortu")    # önceki KURGU_PLANI'ndan zaten taşınır; ikinci uygulama hızı/örtüyü katlar


def duzen_uygula(kok, kp, sahneler, cizelge="T2"):
    """KURGU/KURGU_DUZEN_<cizelge>.json işlemlerini yeni kurulan plana yeniden uygular (kurgu_uygula.duzen_uygula; geçersiz olan
    işlem kp['duzen_atlanan']'a yazılır). Sonra çizelge, diyalog (plan_ofset) ve kart zamanları yeniden kurulur."""
    duzen = ortak.json_oku(os.path.join(kok, "KURGU", f"KURGU_DUZEN_{cizelge}.json"), {}) or {}
    kesilen = set(kp.get("kesilen") or [])
    islemler = [x for x in duzen.get("islemler") or [] if isinstance(x, dict) and x.get("op") not in TASINAN_ISLEMLER
                and not (x.get("op") == "kes" and x.get("plan") in kesilen)]
    if not islemler: return []
    import kurgu_uygula
    kurgu_uygula._ofset_sabitle(kp)
    gecerli = kurgu_uygula.duzen_uygula(kp, islemler, sahneler)
    if kp.get("kesilenler"): kp["kesilen"] = sorted(set(kp.get("kesilen") or []) | set(kp.pop("kesilenler")))
    cizelgele(kp["planlar"], kp.get("karartmalar"))
    bas = {x["plan"]: x["cizelge_bas"] for x in kp["planlar"]}
    for y in kp.get("diyalog") or []:
        if y.get("plan") in bas and y.get("plan_ofset") is not None: y["cizelge_bas"] = ko.kare(bas[y["plan"]] + float(y["plan_ofset"]))
    kp["diyalog"] = sorted(kp.get("diyalog") or [], key=lambda y: (y.get("cizelge_bas") is None, y.get("cizelge_bas") or 0))
    for k in kp.get("kartlar") or []:
        if k.get("plan") in bas: k["cizelge_bas"] = ko.kare(bas[k["plan"]] + float(k.get("ofset", 0.0)))
    kp["duzen_uygulanan"] = len(gecerli)
    return gecerli


def zaman_olculeri(kok):
    p = os.path.join(HERE, "zaman_cizelgesi.py")
    if not os.path.isfile(p): return None
    r = subprocess.run([sys.executable, p, "--asama", "kurgu", "--film", kok], capture_output=True, text=True)
    return r.returncode


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    yol, kp = kur(kok, argv, ko.secenek(argv, "--cizelge", "T2"))
    if not yol: print("!! SAHNELER.json yok ya da plansız", flush=True); return 2
    z = zaman_olculeri(kok)
    o = kp["olcumler"]
    print(f"KURGU_PLANI {kp['cizelge']} v{kp['kurgu_surumu']}: {len(kp['planlar'])} plan · {o['toplam_sn']:.3f} sn · ASL {o['asl']} · "
          f"diyalog {len(kp['diyalog'])}" + ("" if z is None else f" · zaman_cizelgesi çıkış {z}"), flush=True)
    dusuk = [x["plan"] for x in kp["planlar"] if x["goruntu"]["guven"] < float(ko.esik("kirp_guven_min", 0.6))]
    if dusuk: print(f"   güveni düşük kırpma (kurgucu·kirp_incele): {', '.join(map(str, dusuk))}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
