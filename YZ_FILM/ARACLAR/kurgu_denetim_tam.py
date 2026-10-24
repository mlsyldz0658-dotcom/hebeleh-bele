"""KURGU DENETİM (Z3 ana kapı) — kurgu planının makine denetimi (TASARIM §6.7, §7.2 Z3; [KU2] KR7, §4.7.1, §4.7.3).

Kullanım (kurgu_denetim.py bu modülü çağırır; tek başına da çalışır):
  python kurgu_denetim_tam.py --film <film> [--hepsi] [--kullanici] [--saglayici sahte]
      → _RAPOR/Z3_v<N>.json (görev bağlamında GOREV.json'daki rapor yolu)
  --hepsi: önce dudak_denetim (S3, ağız dizisi) koşar, sonra Z3 (A16n "kurgu_denetim --hepsi").
  --kullanici: T3 kuralı — kullanıcının kendi kırpması ya da sırası yüzünden doğan HATA, BAYRAK'a döner (karar geri alınmaz).
Kodda: kurgu_denetim_tam.denetle(kok, argv=()) → (yol, rapor)
Ölçüler (her biri tek araçta; ses ölçüleri ses raporlarından birleştirilir, burada yeniden ölçülmez — İ-9):
  çizelge     boşluk/bindirme yok (planlı karartma hariç); sure = kullanim.sure / hiz                                  H
  #41–43      kullanim.bas ≥ 0,3; bas + sure ≤ klip_sn − 0,5; ölü süre ≤ 0,6 (kirp_oner ölçüsü)                         B
  senkron     görünen konuşan: |diyalog.cizelge_bas − (plan.cizelge_bas + (klip.bas − kullanim.bas)/hiz)| ≤ 1 kare           H
  Y31 ekleri  L: görüntü + taşma ≥ formül; ekranda konuşulan ≥ 1,0 sn; replik klipte klip_sn − 0,3'ten önce biter;
              üzerine binilen plan ≥ taşma + 0,5 · J: sonraki klipte konuşma başı ≥ J öne alma                           H
  B9          L/J/ekran dışı replik sırasında kadrajdaki başka yüzün ağzı oynuyor (KURGU/AGIZ_DIZISI.json, std > 0,05)    H
  S3.6        bölünmüş klipte atlanan aralık bir sözle kesişiyor; senkron korumalı bölme formülü                          H
  cevap       karşılıklı konuşmada cevap boşluğu 0,2–0,6 sn                                                              B
  Y54 / İ-11  örtü planı ≥ max(1,0; A tutma + B durağanlık) (ortu_min_sn)                                                B
  Y55         devam geçişinde kesme bitiş tutmasının içinde (son adım + 0,2)                                             H
  Y58         sahne içi sıra değişince etkili planların göreli sırası ve dondurulmuş durum zinciri                       H
  Z0 #11/#12  aynı plan tipi art arda ≤ 4 (B); aynı kurulumda ölçek kademesi farkı ≥ 2 (H; T3'te B)
  #44–47      S3–S7 ses raporlarının sonucu (ses tarafı ölçer; yoksa ÖLÇÜLEMEDİ)
Çıkış kodları: 0 Z3 GEÇ/BAYRAK · 1 Z3 HATA ya da bozuk girdi · 2 KURGU_PLANI yok · 4 kullanım.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "kurgu_denetim_tam 1.0"
AGIZ_STD_MAX = 0.05            # S3.5 (tahmin; blendshape birimi)
SES_KAPILARI = ("S3", "S4", "S5", "S6", "S7")


def _H(kullanici): return "BAYRAK" if kullanici else "HATA"


def _cumle_sayisi(p):
    r = p.get("replik") or {}
    return max(1, len(r.get("cumleler") or []) or 1)


def cizelge(kp, olc):
    ps = kp.get("planlar") or []; kar = {k.get("sonra_plan"): float(k.get("sure") or 0) for k in kp.get("karartmalar") or []}
    for a, b in zip(ps, ps[1:]):
        bek = a["cizelge_bas"] + a["sure"] + kar.get(a["plan"], 0.0)
        if ko.kare_farki(b["cizelge_bas"], bek) > 0.5:
            olc.append(ko.m("cizelge_bosluk", "HATA", b["plan"], olcu=round(b["cizelge_bas"] - bek, 3), esik=0,
                            neden="çizelgede boşluk ya da bindirme (karartma dışı)"))
    for x in ps:
        g = x["goruntu"]; bek = g["kullanim"]["sure"] / float(g.get("hiz") or 1.0)
        if ko.kare_farki(x["sure"], bek) > 0.5:
            olc.append(ko.m("sure_kullanim", "HATA", x["plan"], olcu=x["sure"], esik=round(bek, 3)))


def pencereler(kp, E, olc):
    for x in kp.get("planlar") or []:
        g = x["goruntu"]
        if g.get("tur") not in ("video",): continue
        u = g["kullanim"]; ks = float(g.get("klip_sn") or 8)
        if u["bas"] < float(E.get("kullanim_bas_min_sn", 0.3)) - 1e-6:
            olc.append(ko.m("Z3#41_kullanim_bas", "BAYRAK", x["plan"], olcu=u["bas"], esik=E.get("kullanim_bas_min_sn", 0.3)))
        if u["bas"] + u["sure"] > ks - float(E.get("kullanim_son_pay_sn", 0.5)) + 1e-6:
            olc.append(ko.m("Z3#42_kullanim_son", "BAYRAK", x["plan"], olcu=round(u["bas"] + u["sure"], 3), esik=ks - 0.5))
        olu = (g.get("olculen") or {}).get("olu_sure_sn")
        if olu is not None and olu > float(E.get("olu_sure_max_sn", 0.6)):
            olc.append(ko.m("Z3#43_olu_sure", "BAYRAK", x["plan"], olcu=olu, esik=E.get("olu_sure_max_sn", 0.6), kok_neden="olu_sure"))
        if g.get("guven") is not None and g["guven"] < float(E.get("kirp_guven_min", 0.6)):
            olc.append(ko.m("kirp_guveni", "BAYRAK", x["plan"], olcu=g["guven"], esik=E.get("kirp_guven_min", 0.6),
                            neden="kurgucu·kirp_incele bakar"))


def _agiz(kok):
    return ortak.json_oku(os.path.join(kok, "KURGU", "AGIZ_DIZISI.json"), {}) or {}


def _agiz_oynuyor(agiz, x, bas, bit, haric=None):
    """Plan x'in kadrajındaki (haric dışındaki) bir yüzün [bas, bit] çizelge aralığında ağız std'si; ölçülemezse None."""
    a = agiz.get(str(x["plan"]))
    if not a: return None
    fps = float(a.get("fps") or ko.FPS); en = 0.0
    k0, k1 = ko.klip_zamanina(x, bas), ko.klip_zamanina(x, bit)
    for yid, dizi in (a.get("yuzler") or {}).items():
        if yid == haric: continue
        v = np.asarray(dizi[max(0, int(k0 * fps)):max(0, int(k1 * fps))], float)
        if len(v) >= 2: en = max(en, float(v.std()))
    return en


def diyalog(kok, kp, pl, E, olc, kullanici):
    dz = {x["plan"]: x for x in kp.get("planlar") or []}; agiz = _agiz(kok); tol = float(E.get("senkron_tolerans_kare", 1))
    for d in kp.get("diyalog") or []:
        x = dz.get(d.get("plan")); kz = d.get("klip_zamani") or {}
        if not x: olc.append(ko.m("diyalog_plani_yok", "HATA", None, replik=d.get("replik"))); continue
        g = x["goruntu"]; hiz = float(g.get("hiz") or 1.0); bas, bit = float(d["cizelge_bas"]), float(d["cizelge_bas"]) + float(d["sure"])
        if d.get("gorunen_konusan") and kz.get("bas") is not None:
            bek = x["cizelge_bas"] + (float(kz["bas"]) - float(g["kullanim"]["bas"])) / hiz
            fark = ko.kare_farki(bas, bek)
            olc.append(ko.m("senkron", "HATA" if fark > tol + 1e-6 else "GEC", x["plan"], replik=d["replik"], olcu=round(fark, 2),
                            esik=tol, kok_neden="senkron_kaydi" if fark > tol else None,
                            oneri={"op": "diyalog_kaydir", "replik": d["replik"], "sn": round(bek - bas, 3)} if fark > tol else None))
        jl = d.get("jl") or {}
        if jl.get("tip") == "L" and d.get("gorunen_konusan"):
            ps = ko.plan_sonu(x); tasma = bit - ps; p = pl.get(x["plan"], {})
            konusma = float(kz.get("bit", 0)) - float(kz.get("bas", 0))
            formul = float(E.get("diyalog_giris_payi_sn", 0.4)) + konusma + float(E.get("cumle_arasi_sn", 0.25)) * (_cumle_sayisi(p) - 1)
            if x["sure"] + tasma < formul - ko.KARE:
                olc.append(ko.m("Y31_L_formul", _H(kullanici), x["plan"], replik=d["replik"], olcu=round(x["sure"] + tasma, 3), esik=round(formul, 3)))
            ekranda = ps - bas
            if ekranda < float(E.get("l_kesme_gorunen_konusma_min_sn", 1.0)) - 1e-6:
                olc.append(ko.m("Y31_L_ekranda_konusma", _H(kullanici), x["plan"], replik=d["replik"], olcu=round(ekranda, 3),
                                esik=E.get("l_kesme_gorunen_konusma_min_sn", 1.0), kok_neden="konusan_belirsiz"))
            if float(kz.get("bit", 0)) > float(g.get("klip_sn") or 8) - float(E.get("l_kesme_klip_ses_son_pay_sn", 0.3)) + 1e-6:
                olc.append(ko.m("Y31_L_klip_ses_sonu", _H(kullanici), x["plan"], replik=d["replik"], olcu=kz.get("bit")))
            for un in jl.get("uzerindeki_planlar") or []:
                y = dz.get(un)
                if not y: continue
                if un == (kp["planlar"][kp["planlar"].index(x) + 1]["plan"] if kp["planlar"].index(x) + 1 < len(kp["planlar"]) else None):
                    if y["sure"] < tasma + float(E.get("l_kesme_alici_plan_ek_sn", 0.5)) - ko.KARE:
                        olc.append(ko.m("Y31_L_alici_plan", _H(kullanici), un, replik=d["replik"], olcu=y["sure"],
                                        esik=round(tasma + float(E.get("l_kesme_alici_plan_ek_sn", 0.5)), 3)))
        if jl.get("tip") == "J":
            j = float(jl.get("tasma_sn") or 0)
            if kz.get("bas") is not None and float(kz["bas"]) < j - 1e-6:
                olc.append(ko.m("J_klip_kosulu", _H(kullanici), x["plan"], replik=d["replik"], olcu=kz["bas"], esik=j))
        ust = list(jl.get("uzerindeki_planlar") or []) if jl else []
        if d.get("ekran_disi"): ust.append(x["plan"])
        for un in ust:                                       # B9: başkasının repliği ağzı oynayan yüzün üstüne konmaz
            y = dz.get(un)
            if not y: continue
            a0, a1 = max(bas, y["cizelge_bas"]), min(bit, ko.plan_sonu(y))
            if a1 - a0 < ko.KARE: continue
            std = _agiz_oynuyor(agiz, y, a0, a1)              # konuşan bu planda görünmüyor: kadrajdaki hiçbir ağız oynamamalı
            if std is None: olc.append(ko.m("B9_agiz", "OLCULEMEDI", un, replik=d["replik"], neden="ağız dizisi yok (dudak_denetim)"))
            else:
                olc.append(ko.m("B9_agiz", "HATA" if std > AGIZ_STD_MAX else "GEC", un, replik=d["replik"], olcu=round(std, 3),
                                esik=AGIZ_STD_MAX, kok_neden="dudak_ustune_replik" if std > AGIZ_STD_MAX else None))
    # cevap boşluğu (S3.8'den taşındı): aynı sahne grubunda ardışık iki farklı konuşan
    sg = {x["plan"]: x.get("sahne_grubu") for x in kp.get("planlar") or []}
    ds = sorted(kp.get("diyalog") or [], key=lambda d: d["cizelge_bas"]); lo, hi = E.get("cevap_boslugu_sn") or [0.2, 0.6]
    for a, b in zip(ds, ds[1:]):
        if sg.get(a["plan"]) != sg.get(b["plan"]) or a.get("karakter") == b.get("karakter"): continue
        bos = b["cizelge_bas"] - (a["cizelge_bas"] + a["sure"])
        if not (lo - 1e-6 <= bos <= hi + 1e-6):
            olc.append(ko.m("cevap_boslugu", "BAYRAK", b["plan"], replik=b["replik"], olcu=round(bos, 3), esik=[lo, hi],
                            kok_neden="diyalog_kopuk"))


def bolme(kp, d, E, olc, kullanici):
    ps = kp.get("planlar") or []
    for i, x in enumerate(ps):
        kk = x["goruntu"].get("kaynak_klip")
        if kk is None: continue
        j = next((k for k in range(i - 1, -1, -1) if ps[k]["plan"] == kk or ps[k]["goruntu"].get("kaynak_klip") == kk), None)
        if j is None: continue
        a = ps[j]["goruntu"]["kullanim"]; b = x["goruntu"]["kullanim"]
        arada = sum(ps[k]["sure"] for k in range(j + 1, i))
        atl0, atl1 = a["bas"] + a["sure"] + arada, b["bas"]                  # aradaki planların süresi sesle (L) duyulur; kalan atlanır
        for rid, r in (d.get("replikler") or {}).items():
            if r.get("kaynak_plan") != kk: continue
            kes = [w for w in r.get("kelimeler") or [] if w["bas"] < atl1 - 1e-6 and w["bit"] > atl0 + 1e-6]
            if kes:
                bek = a["bas"] + a["sure"] + arada
                olc.append(ko.m("S3.6_bolme_soz_kesisimi", _H(kullanici), x["plan"], replik=rid, olcu=[round(atl0, 3), round(atl1, 3)],
                                kelime=[w["w"] for w in kes][:5], oneri={"op": "kirp", "plan": x["plan"], "bas": ko.kare(bek)},
                                neden="senkron korumalı bölme: parca2.bas = parca1.bas + parca1.sure + aradaki"))
        if 1e-6 < atl1 - (a["bas"] + a["sure"]) < float(E.get("klip_bolme_atlama_min_sn", 0.4)) - 1e-6:
            olc.append(ko.m("klip_bolme_atlama", "BAYRAK", x["plan"], olcu=round(atl1 - atl0, 3), esik=E.get("klip_bolme_atlama_min_sn", 0.4)))


def ortu(kp, E, olc):
    ps = kp.get("planlar") or []; taban = float((E.get("ortu_min_sn") or {}).get("taban", 1.0)) if isinstance(E.get("ortu_min_sn"), dict) else 1.0
    for i, x in enumerate(ps):
        if not x.get("ortu"): continue
        a = ps[i - 1] if i > 0 else None; b = ps[i + 1] if i + 1 < len(ps) else None
        at = float(((a or {}).get("goruntu") or {}).get("olculen", {}).get("tutma_sn") or 0.0)
        bd = float(((b or {}).get("goruntu") or {}).get("olculen", {}).get("duraganlik_sn") or 0.0)
        alt = max(taban, at + bd)
        olc.append(ko.m("Y54_ortu_suresi", "BAYRAK" if x["sure"] < alt - 1e-6 else "GEC", x["plan"], olcu=x["sure"], esik=round(alt, 3),
                        formul="max(1.0, a_tutma_sn + b_duraganlik_sn)", kok_neden="devam_dikisi" if x["sure"] < alt else None))


def zincir_cikis(kp, pl, E, olc, kullanici):
    ps = kp.get("planlar") or []; ic = float(E.get("zincir_cikis_tutma_ic_min_sn", 0.2))
    for a, b in zip(ps, ps[1:]):
        if (ko.zanaat(pl.get(b["plan"], {})).get("zincir") or {}).get("gecis_turu") != "devam": continue
        son = next((s["bit"] for s in reversed(a["goruntu"].get("adimlar_olculen") or []) if s.get("bit") is not None), None)
        u = a["goruntu"]["kullanim"]; cikis = u["bas"] + u["sure"]
        if son is None: olc.append(ko.m("Y55_zincir_cikis", "OLCULEMEDI", a["plan"], neden="son adımın ölçülen bitişi yok")); continue
        olc.append(ko.m("Y55_zincir_cikis", "GEC" if cikis >= son + ic - 1e-6 else _H(kullanici), a["plan"], olcu=round(cikis, 3),
                        esik=round(son + ic, 3), kok_neden=None if cikis >= son + ic - 1e-6 else "zincir_dikis"))


def dondurma(kp, pl, olc, kullanici):
    """Y58: sahne içi sıra değişince etkili planların göreli sırası korunur; etkili planların dondurulmuş durum zinciri kopmaz.
    Etkisiz planlar (tepki, ekleme) serbesttir."""
    gruplar = {}
    for x in kp.get("planlar") or []:
        if x.get("ortu"): continue
        gruplar.setdefault(x.get("sahne_grubu"), []).append(x)
    for sg, xs in gruplar.items():
        etkili = [x for x in xs if x.get("etkili")]
        plan_sira = sorted(etkili, key=lambda x: (float(pl.get(x["plan"], {}).get("sira", x["plan"]) or 0), x["plan"]))
        if [x["plan"] for x in etkili] != [x["plan"] for x in plan_sira]:
            olc.append(ko.m("Y58_etkili_sira", _H(kullanici), etkili[0]["plan"], sahne_grubu=sg, olcu=[x["plan"] for x in etkili],
                            esik=[x["plan"] for x in plan_sira], kok_neden="bilgi_durumu_ihlali",
                            neden="etkisi olan planın sahne içi sırası değişti; yalnız etkisiz planlar yer değiştirir"))
        for a, b in zip(etkili, etkili[1:]):
            ab, bb = (a.get("durum_ozet") or {}).get("bit"), (b.get("durum_ozet") or {}).get("bas")
            if ab and bb and ab != bb and [x["plan"] for x in etkili] == [x["plan"] for x in plan_sira]:
                olc.append(ko.m("Y58_dondurulmus_zincir", _H(kullanici), b["plan"], onceki=a["plan"], olcu=bb, esik=ab))


def komsuluk(kp, pl, E, olc, kullanici):
    ps = [x for x in kp.get("planlar") or [] if not x.get("ortu")]; mx = int(E.get("ayni_plan_tipi_ardisik_max", 4))
    kad = E.get("olcek_kademeleri") or {}; fark_min = int(E.get("olcek_kademe_min_fark", 2)); seri = 1
    for a, b in zip(ps, ps[1:]):
        za, zb = ko.zanaat(pl.get(a["plan"], {})), ko.zanaat(pl.get(b["plan"], {}))
        seri = seri + 1 if za.get("plan_tipi") and za.get("plan_tipi") == zb.get("plan_tipi") else 1
        if seri > mx: olc.append(ko.m("Z0#11_ayni_plan_tipi", "BAYRAK", b["plan"], olcu=seri, esik=mx))
        ka, kb = za.get("kamera") or {}, zb.get("kamera") or {}
        if a.get("sahne_grubu") == b.get("sahne_grubu") and ka.get("kurulum") and ka.get("kurulum") == kb.get("kurulum"):
            fa, fb = kad.get(ka.get("kadraj")), kad.get(kb.get("kadraj"))
            if fa is not None and fb is not None and abs(fa - fb) < fark_min:
                olc.append(ko.m("Z0#12_olcek_sicramasi", _H(kullanici), b["plan"], olcu=abs(fa - fb), esik=fark_min,
                                kok_neden="olcek_sicramasi", neden="aynı kurulumdan ölçek farkı yetersiz (sıçrama kesmesi)"))


def ses_raporlari(kok, olc):
    for k in SES_KAPILARI:
        yol, r = ko.son_rapor(kok, k)
        if not r: olc.append(ko.m(f"{k}_raporu", "OLCULEMEDI", None, neden=f"{k} raporu yok (ses tarafı ölçer)")); continue
        s = {"HATA": "HATA", "KISMI": "HATA", "BAYRAK": "BAYRAK"}.get(r["sonuc"], "GEC")
        olc.append(ko.m(f"{k}_raporu", s, None, olcu=r["sonuc"], kanit=ko.goreli(kok, yol)))


def denetle(kok, argv=()):
    argv = list(argv); kullanici = ko.bayrak(argv, "--kullanici")
    kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: return None, None
    pl = ko.sahne_planlari(kok); d = ko.diyalog_oku(kok); E = ko.po.esik(); olc = []
    cizelge(kp, olc); pencereler(kp, E, olc); diyalog(kok, kp, pl, E, olc, kullanici); bolme(kp, d, E, olc, kullanici)
    ortu(kp, E, olc); zincir_cikis(kp, pl, E, olc, kullanici); dondurma(kp, pl, olc, kullanici); komsuluk(kp, pl, E, olc, kullanici)
    ses_raporlari(kok, olc)
    birim = [x["plan"] for x in kp.get("planlar") or []]
    return ko.rapor(kok, "Z3", ko.kapsam_surum(kp), olc, "A16" if not kullanici else "A16n", SURUM, birimler=birim,
                    ek={"kurgu_plani": ko.goreli(kok, kp_yol), "kurgu_plani_imza": ko.plan_imza(kp), "t3_kurali": kullanici},
                    girdi_imza=ko.plan_imza(kp))


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    if ko.bayrak(argv, "--hepsi"):
        import dudak_denetim
        dudak_denetim.denetle(kok, argv)
    yol, r = denetle(kok, argv)
    if not r: print("!! KURGU_PLANI yok; önce plan_kurgu.py", flush=True); return 2
    return ko.po.cikis(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
