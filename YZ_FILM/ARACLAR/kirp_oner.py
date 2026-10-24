"""KIRP ÖNER — klipten kullanılacak pencereyi (kullanim) ölçerek önerir (TASARIM §6.7; [KU2] §4.6.2 kirp_oner, KR5, KR6).

Kullanım:
  python kirp_oner.py --film <film> [--plan 121,122] [--zincir] [--saglayici sahte]
      → KURGU/KIRP_ONERI.json {plan: {kullanim, guven, gerekce, adimlar_olculen, olculen, bayraklar}} + KURGU/KIRP_INCELE.md (güven < 0,6)
Kodda: kirp_oner.oner(kok, plan, klip, kelimeler=None, kusurlar=None, zincir=False, kilit=None) → sözlük
Algoritma (eşikler RE'den: kirp_hareket_mad_k, kirp_hareket_sure_sn, kullanim_*, olu_sure_max_sn, diyalog_giris_payi_sn, kirp_guven_min):
  1. Hareket enerjisi: 24 fps, 160×90 gri; E(t) = ort|f(t) − f(t−1)|, 5 karelik medyanla düzleştirilir; taban ilk 0,5 sn'nin medyanı;
     hareket = E > taban + k·MAD (MAD tabanı 0,1 gri düzey) en az 0,2 sn. Kamera hareketliyse özne kutusu gerekir (yoksa güven düşer, BAYRAK).
  2. Güvenli pencere [0,5 ; klip_sn − 0,5] ∩ ilk V1/V2/V3 kusurundan 0,1 sn öncesi.
  3. Adım eşleme: planlanan fiziksel/mikro adımlar ölçülen hareket bölütlerine sırayı koruyarak eşlenir; bölüt adımdan azsa BAYRAK (Veo adım atladı).
  4. Kırpma önceliği (kurgu.kirpma_onceligi ya da plan_tipi'nden): replik · eylem · tepki_tepesi · durgun (kurallar [KU2] §4.6.2).
  5. --zincir: çıkış [son adım bitişi + 0,2 ; klip_sn − 0,5] aralığında enerjinin en düşük olduğu an (Y55).
  6. Güven 1'den düşer: hareket başı yok −0,3 · duyulan kelime < %70 −0,3 · kusur pencereyi daralttı −0,2 · kamera hareketli −0,2;
     klip okunamazsa 0 (kurgucuya gider; sessiz geçiş yok).
  Kullanıcının kararı (kullanim_kaynak/kilit "kullanici") hiçbir zaman değişmez; zincir kilidi de korunur.
Çıkış kodları: 0 tamam · 1 hata · 2 film/klip yok · 4 kullanım.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "kirp_oner 1.0"
MAD_TABAN = 0.1


def enerji(kareler):
    if kareler is None or len(kareler) < 2: return None
    f = kareler.astype(np.float32)
    e = np.concatenate([[0.0], np.mean(np.abs(f[1:] - f[:-1]), axis=(1, 2))])
    p = np.pad(e, 2, mode="edge")
    return np.array([np.median(p[i:i + 5]) for i in range(len(e))])


def bolutler(e, fps=ko.FPS, k=3.0, min_sn=0.2):
    """Hareket bölütleri [(bas_sn, bit_sn)]; taban ilk 0,5 sn'nin medyanı."""
    n0 = max(2, int(0.5 * fps)); taban = float(np.median(e[1:n0 + 1])) if len(e) > n0 else float(np.median(e))
    mad = max(float(np.median(np.abs(e[1:n0 + 1] - taban))) if len(e) > n0 else 0.0, MAD_TABAN)
    aktif = e > taban + k * mad; out, i, n = [], 0, len(e)
    while i < n:
        if aktif[i]:
            j = i
            while j < n and aktif[j]: j += 1
            out.append([i, j]); i = j
        else: i += 1
    birles = []
    for a, b in out:
        if birles and a - birles[-1][1] < int(min_sn * fps): birles[-1][1] = b
        else: birles.append([a, b])
    return [((a - 1) / fps if a > 0 else 0.0, b / fps) for a, b in birles if b - a >= int(round(min_sn * fps))], taban, mad


def adim_esle(adimlar, bolut):
    """Planlanan adımlar → ölçülen bölütler (sıra korunur). (eşleme listesi, atlanan adım sayısı)."""
    fiz = [a for a in adimlar if a.get("tur") in ("fiziksel", "mikro")]
    if not fiz: return [], 0
    if not bolut: return [{"id": a["id"], "bas": None, "bit": None} for a in fiz], len(fiz)
    if len(bolut) == len(fiz): return [{"id": a["id"], "bas": round(b[0], 3), "bit": round(b[1], 3)} for a, b in zip(fiz, bolut)], 0
    out, j = [], 0
    for a in fiz:
        en, en_k = None, -1e9
        for k in range(j, len(bolut)):
            b = bolut[k]; ort = min(b[1], float(a.get("bit", 0))) - max(b[0], float(a.get("bas", 0)))
            if ort > en_k: en, en_k = k, ort
        if en is None or (len(bolut) < len(fiz) and en_k <= 0 and out and out[-1].get("_k") == en):
            out.append({"id": a["id"], "bas": None, "bit": None}); continue
        b = bolut[en]; out.append({"id": a["id"], "bas": round(b[0], 3), "bit": round(b[1], 3), "_k": en}); j = en + 1
    for o in out: o.pop("_k", None)
    return out, max(0, len(fiz) - len(bolut))


def _hedef_sure(plan, tip, E):
    araliklar = E.get("plan_sure_aralik_sn") or {}
    a = araliklar.get(tip) or [1.5, 6.0]
    s = float((plan.get("kullanim") or {}).get("sure") or (a[0] + a[1]) / 2)
    return min(max(s, a[0]), a[1])


def kusur_anlari(kok, plan):
    out = []
    for k, v in (plan.get("denetim") or {}).items():
        for x in ((v or {}).get("kusurlar") or []) if isinstance(v, dict) else []:
            if isinstance(x, dict) and x.get("an") is not None: out.append(float(x["an"]))
    for kd in ("V1", "V2", "V3"):
        _, r = ko.son_rapor(kok, kd)
        for h in ((r or {}).get("hatalar") or []) + ((r or {}).get("bayraklar") or []):
            if h.get("plan") == plan.get("no"):
                an = h.get("an_sn", h.get("an"))
                if isinstance(an, (int, float)): out.append(float(an))
    return sorted(out)


def oner(kok, plan, klip, kelimeler=None, kusurlar=None, zincir=False, kilit=None, E=None):
    E = E or ko.po.esik(); z = ko.zanaat(plan); no = plan.get("no")
    klip_sn = ko.sure(klip) if klip and os.path.exists(klip) else None
    klip_sn = klip_sn or float(z.get("klip_sn") or 8)
    if kilit:                                                   # kullanıcı ya da zincir kararı dokunulmaz
        return {"kullanim": dict(kilit["kullanim"]), "guven": 1.0, "gerekce": f"{kilit['kaynak']} kararı (kilitli)",
                "kullanim_kaynak": kilit["kaynak"], "adimlar_olculen": [], "olculen": {}, "bayraklar": []}
    oncelik = ko.kirpma_onceligi(plan); tip = z.get("plan_tipi") or "eylem"
    guven, ger, bay = 1.0, [], []
    bas_min = float(E.get("kullanim_bas_min_sn", 0.3)); son_pay = float(E.get("kullanim_son_pay_sn", 0.5))
    pen_bas, pen_bit = max(0.5, bas_min), klip_sn - son_pay
    kus = [k for k in (kusurlar if kusurlar is not None else kusur_anlari(kok, plan)) if k >= pen_bas]
    if kus:
        pen_bit = min(pen_bit, kus[0] - 0.1); guven -= 0.2; ger.append(f"kusur {kus[0]:.2f} sn'de: pencere {pen_bit:.2f}'de biter")
    kareler = ko.kareler_gri(klip) if klip and os.path.exists(klip) else None
    e = enerji(kareler)
    if e is None:
        p = plan.get("kullanim") or {"bas": 0.5, "sure": 3.0}
        return {"kullanim": {"bas": ko.kare(p["bas"]), "sure": ko.kare(p["sure"])}, "guven": 0.0, "kullanim_kaynak": "otomatik",
                "gerekce": "klip okunamadı (ölçülemedi); plan değeri kurgucuya", "adimlar_olculen": [], "olculen": {},
                "bayraklar": [{"madde": "kirp_olculemedi", "neden": "klip okunamadı"}]}
    bol, taban, mad = bolutler(e, k=float(E.get("kirp_hareket_mad_k", 3)), min_sn=float(E.get("kirp_hareket_sure_sn", 0.2)))
    if ((z.get("kamera") or {}).get("hareket_tipi") or "sabit") != "sabit":
        guven -= 0.2; bay.append({"madde": "kamera_hareketli", "neden": "özne kutusu yok; enerji bütün karede ölçüldü"})
    adimlar = z.get("eylem_zinciri") or []
    esl, atlanan = adim_esle(adimlar, bol)
    if atlanan:
        bay.append({"madde": "adim_atlandi", "neden": f"{atlanan} planlı adımın hareketi ölçülmedi (Veo adımı atlamış olabilir)"})
    hb = bol[0][0] if bol else None; hs = bol[-1][1] if bol else None
    if hb is None and any(a.get("tur") in ("fiziksel", "mikro") for a in adimlar):
        guven -= 0.3; ger.append("hareket başlangıcı bulunamadı")
    giris_payi = float(E.get("diyalog_giris_payi_sn", 0.4))
    kesme = z.get("kesme") or {}; kt = kesme.get("tip") or "duz"; tasma = float(kesme.get("ses_tasma_sn") or 0.0)
    ks = sorted(kelimeler or [], key=lambda k: k["bas"])
    if oncelik == "replik" and ks:
        ilk, son = float(ks[0]["bas"]), float(ks[-1]["bit"])
        once = [m for m in esl if m["bas"] is not None and m["bas"] < ilk]
        bas = (once[0]["bas"] - 0.1) if once else ilk - giris_payi
        bit = son + 0.3
        if kt == "L" and tasma > 0:
            bit = max(son + 0.3 - tasma, ilk + float(E.get("l_kesme_gorunen_konusma_min_sn", 1.0)))
            ger.append(f"L kesme: görüntü {bit:.2f}'de biter, ses {tasma:.2f} sn taşar")
        plan_kelime = len(((plan.get("replik") or {}).get("metin") or "").split())
        if plan_kelime and len(ks) < 0.7 * plan_kelime: guven -= 0.3; ger.append(f"duyulan kelime {len(ks)}/{plan_kelime}")
        ger.insert(0, f"ilk kelime {ilk:.2f}, son kelime {son:.2f}")
    elif oncelik == "replik":
        guven -= 0.3; ger.append("replik planı ama kelime zamanı yok"); oncelik = "eylem"
        bas = (hb - 0.1) if hb is not None else float((plan.get("kullanim") or {}).get("bas", 0.5)); bit = None
    if oncelik == "eylem":
        bas = (hb - 0.1) if hb is not None else float((plan.get("kullanim") or {}).get("bas", 0.5))
        sonadim = next((m for m in reversed(esl) if m["bas"] is not None), None)
        if sonadim and kt == "eylem":
            bit = sonadim["bas"] + 0.65 * (sonadim["bit"] - sonadim["bas"]); ger.append("eylem kesmesi son adımın %65'inde")
        elif sonadim: bit = sonadim["bit"] + float(E.get("bitis_tutma_sn", 0.5))
        elif hs is not None: bit = hs + float(E.get("bitis_tutma_sn", 0.5))
        else: bit = bas + _hedef_sure(plan, tip, E)
        if hb is not None: ger.insert(0, f"hareket {hb:.2f}–{hs:.2f} sn")
    elif oncelik == "tepki_tepesi":
        d = _hedef_sure(plan, "tepki", E); tepe = float(np.argmax(e[1:]) + 1) / ko.FPS
        bas = tepe - d / 2; bit = bas + d; ger.append(f"tepki tepesi {tepe:.2f} sn ortalandı")
        if bas < pen_bas: bas, bit = pen_bas, bit + (pen_bas - bas)
        if bit > pen_bit: bas, bit = max(pen_bas, bas - (bit - pen_bit)), pen_bit
    elif oncelik == "durgun":
        d = _hedef_sure(plan, tip, E); n = max(1, int(d * ko.FPS)); i0, i1 = int(pen_bas * ko.FPS), int(pen_bit * ko.FPS) - n
        c = np.concatenate([[0.0], np.cumsum(e)]); en = min(range(i0, max(i0, i1) + 1), key=lambda i: c[min(i + n, len(e))] - c[min(i, len(e))])
        bas = en / ko.FPS; bit = bas + d; ger.append("sarsıntısı en az pencere")
    if zincir:
        sonadim = next((m for m in reversed(esl) if m["bit"] is not None), None)
        a = (sonadim["bit"] if sonadim else (hs or bas)) + float(E.get("zincir_cikis_tutma_ic_min_sn", 0.2))
        i0, i1 = int(a * ko.FPS), int(pen_bit * ko.FPS)
        if i1 > i0: bit = (i0 + int(np.argmin(e[i0:i1 + 1]))) / ko.FPS; ger.append(f"zincir çıkışı {bit:.2f} (Y55)")
        else: bay.append({"madde": "zincir_penceresi_yok", "neden": "son adımdan sonra tutma payı yok"})
    bas = max(pen_bas, bas); bit = min(pen_bit, bit if bit is not None else pen_bit)
    if bit - bas < 0.5:
        bay.append({"madde": "pencere_dar", "neden": f"kullanılabilir pencere {max(0.0, bit - bas):.2f} sn"}); guven -= 0.2
        bit = min(pen_bit, bas + 0.5)
    bas, sure = ko.kare(bas), ko.kare(max(ko.KARE, bit - bas))
    olu = round(max(0.0, (hb - bas) if hb is not None else 0.0), 3)
    if olu > float(E.get("olu_sure_max_sn", 0.6)) and oncelik == "eylem":
        bay.append({"madde": "olu_sure", "neden": f"hareketten önce {olu:.2f} sn"})
    son_h = next((m["bit"] for m in reversed(esl) if m["bit"] is not None), hs)
    olc = {"hareket_bas": None if hb is None else round(hb, 3), "hareket_bit": None if hs is None else round(hs, 3),
           "olu_sure_sn": olu, "duraganlik_sn": olu, "tutma_sn": None if son_h is None else round(max(0.0, bas + sure - son_h), 3),
           "taban": round(taban, 3), "mad": round(mad, 3), "klip_sn": round(klip_sn, 3)}
    guven = round(max(0.0, min(1.0, guven)), 2)
    return {"kullanim": {"bas": bas, "sure": sure}, "guven": guven, "gerekce": "; ".join(ger) or oncelik,
            "kullanim_kaynak": "otomatik", "adimlar_olculen": esl, "olculen": olc, "bayraklar": bay, "oncelik": oncelik}


def kelimeler_klipte(d, no):
    ks = []
    for rid, r in sorted((d.get("replikler") or {}).items()):
        if r.get("kaynak_plan") == no and r.get("yol_gercek", r.get("yol_plan")) != "tts":
            kz = r.get("klip_zamani") or {}
            ks += r.get("kelimeler") or ([{"w": "…", "bas": kz["bas"], "bit": kz["bit"]}] if kz.get("bas") is not None else [])
    return ks


def incele_md(kok, sonuc, esik_):
    satir = ["# KIRP_INCELE — kurgucu (kirp_incele kipi) bakar", "", f"Güven < {esik_} olan kırpmalar; karelerle doğrulanır.", ""]
    for no, s in sorted(sonuc.items(), key=lambda x: str(x[0])):
        if s["guven"] < esik_:
            satir.append(f"- #{no} · kullanım {s['kullanim']['bas']:.3f} + {s['kullanim']['sure']:.3f} sn · güven {s['guven']} · {s['gerekce']}")
    if len(satir) == 4: satir.append("(yok)")
    p = os.path.join(kok, "KURGU", "KIRP_INCELE.md"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f: f.write("\n".join(satir) + "\n")
    return p


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    pl = ko.sahne_planlari(kok)
    if not pl: print("!! SAHNELER.json yok ya da plansız", flush=True); return 2
    sec = ko.secenek(argv, "--plan"); nolar = [int(x) for x in sec.split(",")] if sec else sorted(pl)
    d = ko.diyalog_oku(kok); E = ko.po.esik(); out = {}
    for no in nolar:
        p = pl.get(no)
        if not p: print(f"!! plan {no} yok", flush=True); return 2
        out[str(no)] = oner(kok, p, ko.klip_yolu(kok, no), kelimeler_klipte(d, no), zincir=ko.bayrak(argv, "--zincir"), E=E)
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "KIRP_ONERI.json"), {"_uretim": ko.po.zarf("A16", SURUM), "planlar": out})
    incele_md(kok, out, float(E.get("kirp_guven_min", 0.6)))
    for no, s in out.items(): print(f"#{no}: {s['kullanim']['bas']:.3f} + {s['kullanim']['sure']:.3f} sn · güven {s['guven']} · {s['gerekce']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
