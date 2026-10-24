"""PLAN DİLİ — planın görünür tarifi: tek derleyici, dört kullanım (TASARIM §6.4; [YN2] §4.6.1; D-13).

Kullanım:
  python plan_dili.py --film <film> --plan <no> [--dil en|tr|serit|cekim] [--zaman-bicimi aralik|sira]
Kodda:
  import plan_dili as pd
  B = pd.baglam(kok)                                 adlar, zamirler, nesne adları (EN/TR), ses tarifleri, dünya defteri durumları
  pd.gorunur_tarif(plan, "en", B)  → hareket istemi gövdesi (istem_derle --hareket; EN, saniyeli adımlar)
  pd.gorunur_tarif(plan, "tr", B)  → kör paket metni (kor_paket --kip plan; adlar B["etiket"] ile maskelenebilir)
  pd.gorunur_tarif(plan, "serit", B) → animatik eylem şeridi (tek satır) · pd.gorunur_tarif(plan, "cekim", B) → çekim listesi satırları
  pd.adim_cumlesi(adim, plan, B, "en") → (cümle, kelime sayısı)
Kurallar (D-13): YZ'ye sonuç söylenmez; her adım [bas–bit] + sözlükten tek fiil + karakterin KENDİ sağı/solu ("her left hand") + hedef +
ölçü + el şekli. Tek kişilik planda adımlar öznesiz, çok kişide adlıdır. Konuşma adımı: ad + ton fiili (teslim sözlüğü) + Veo ses tarifi
(_SES/SES_PROFILLERI.json) + replik metni (kelimesi kelimesine). Son adımdan klip sonuna bekleme ("holds still"; Ö0-b canlı bekleme
kararı OLCUM0.json "canli_bekleme" true ise "holds the pose, breathing"). Ekran dışı ses varken görünen herkes "listens silently, mouth
closed" (Y35). EN çıktıda çıplak left/right yoktur: yön daima iyelikli ("her own left") ya da "frame left"tir.
"""
import os, sys, re, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "plan_dili 1.0"


# --- bağlam -------------------------------------------------------------------------------------------------------
def _zamir(kv):
    z = (kv or {}).get("zamir") or (kv or {}).get("cinsiyet")
    if z in ("kadin", "erkek", "yaratik"): return z
    if (kv or {}).get("rol") == "yaratik" or (kv or {}).get("konusmaz"): return "yaratik"
    sk = ((kv or {}).get("ses_karakteri") or "").lower()
    if sk.startswith("kadın") or sk.startswith("kadin") or "female" in sk: return "kadin"
    if sk.startswith("erkek") or "male" in sk: return "erkek"
    return "bilinmiyor"


def baglam(kok, sahneler=None, durumlar=None):
    hikaye = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    zs = po.sozluk("plan").get("zamir") or {}
    B = {"ad": {}, "pos": {}, "ozne": {}, "nesne_en": {}, "nesne_tr": {}, "ses": {}, "durum": durumlar or {}, "etiket": {}, "bekleme": "sabit"}
    for kid, kv in (hikaye.get("karakterler") or {}).items():
        B["ad"][kid] = (kv or {}).get("ad") or kid.capitalize()
        z = zs.get(_zamir(kv)) or zs.get("bilinmiyor") or {"pos": "their", "ozne": "they"}
        B["pos"][kid], B["ozne"][kid] = z["pos"], z["ozne"]
    for y in sorted(glob.glob(os.path.join(kok, "_YONETMEN", "HARITA_P*.json"))):
        for nid, nv in ((ortak.json_oku(y, {}) or {}).get("nesneler") or {}).items():
            B["nesne_en"][nid] = (nv or {}).get("ad_en") or nid.replace("_", " ")
            B["nesne_tr"][nid] = (nv or {}).get("ad_tr") or nid.replace("_", " ")
    s = sahneler or ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
    try:
        import kroki
        K = kroki.Kroki(kok, s)
        for mv in K.mekanlar.values():
            kr = mv.get("kroki") or {}
            for o in (kr.get("ogeler") or []) + (kr.get("isik_kaynaklari") or []):
                if o.get("id"):
                    B["nesne_en"].setdefault(o["id"], o.get("ad_en") or o["id"].replace("_", " "))
                    B["nesne_tr"].setdefault(o["id"], o.get("ad_tr") or o.get("ad") or o["id"].replace("_", " "))
            for a, v in (kr.get("isaretler") or {}).items():
                B["nesne_en"].setdefault(a, (v or {}).get("ad_en") or (v or {}).get("ad") or a)
                B["nesne_tr"].setdefault(a, (v or {}).get("ad") or a)
    except Exception: pass
    prof = ortak.json_oku(os.path.join(kok, "_SES", "SES_PROFILLERI.json"), {}) or {}
    for kid, p in (prof.get("karakterler") or prof).items():
        if isinstance(p, dict) and p.get("veo_ses_tarifi"): B["ses"][kid] = p["veo_ses_tarifi"]
    if not B["durum"]:
        D = ortak.json_oku(os.path.join(kok, "DUNYA_DEFTERI.json"), {}) or {}
        B["durum"] = {k: v.get("durum") for k, v in (D.get("planlar") or {}).items() if isinstance(v.get("durum"), dict)}
    if not B["durum"] and isinstance(s, dict) and s.get("sahneler"):
        try:
            import dunya_defteri
            C = dunya_defteri.coz(s, hikaye)
            B["durum"] = {k: {"bas": v["bas"], "bit": v["bit"]} for k, v in C.planlar.items()}
        except Exception: pass
    try:
        o0 = ortak.json_oku(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "OLCUM0", "OLCUM0.json"), {}) or {}
        if o0.get("canli_bekleme") is True: B["bekleme"] = "canli"
    except ortak.YolYok: pass
    return B


# --- sözcük yardımcıları ------------------------------------------------------------------------------------------
def sn(x):
    x = round(float(x or 0), 2)
    return str(int(x)) if x == int(x) else ("%g" % x)


def sn_tr(x): return sn(x).replace(".", ",")


def kelime(s): return len(re.findall(r"[A-Za-z0-9']+", s or ""))


def _ad(B, kid, dil="en"):
    if dil != "en" and B.get("etiket", {}).get(kid): return B["etiket"][kid]
    return B["ad"].get(kid) or (kid or "").capitalize()


def _nesne(B, x, dil="en"):
    if x is None: return ""
    if x in B["ad"]: return _ad(B, x, dil)
    return (B["nesne_en"] if dil == "en" else B["nesne_tr"]).get(x) or str(x).replace("_", " ")


def _olcu(o, dil="en"):
    if o in (None, ""): return ""
    fs = po.sozluk("fiil").get("_olcu") or {}
    if o in fs: return fs[o]["en" if dil == "en" else "tr"]
    ey = po.sozluk("plan").get("el_yer") or {}
    if o in ey:
        en = ey[o]["en"]
        return ("to " + (en[3:] if en.startswith("at ") else en)) if dil == "en" else (ey[o]["tr"] + "na")
    m = re.fullmatch(r"([0-9.]+)cm", str(o))
    if m: return f"{m.group(1)} cm"
    m = re.fullmatch(r"([0-9]+)_derece", str(o))
    if m: return f"{m.group(1)} degrees" if dil == "en" else f"{m.group(1)} derece"
    return str(o).replace("_", " ")


def _el_adi(adim):
    g = adim.get("govde") or ""
    el = ((po.sozluk("plan").get("govde") or {}).get(g) or {}).get("el")
    return el if el in ("sag", "sol") else None


def _tut(B, plan, kid, el, adim=None):
    """Adımın başında o elde tutulan nesne: planın başlangıç durumu + adımdan önceki adımların etki'leri."""
    if not el: return None
    d = (B.get("durum") or {}).get(str(plan.get("no"))) or {}
    t = ((((d.get("bas") or {}).get("karakterler") or {}).get(kid) or {}).get("eller") or {}).get(el, {}).get("tutar")
    for a in sorted((plan.get("zanaat") or {}).get("eylem_zinciri") or [], key=lambda x: x.get("bas") or 0):
        if adim is not None and a is adim: break
        k = f"{kid}.eller.{el}.tutar"
        if k in (a.get("etki") or {}): t = a["etki"][k]
    return t


SESLI = "aeıioöuü"
def iyelik(ad):
    """Türkçe tamlayan eki: Mara → Mara'nın, Voss → Voss'un."""
    son = next((c for c in reversed(ad.lower()) if c in SESLI), "a")
    ek = {"a": "ın", "ı": "ın", "e": "in", "i": "in", "o": "un", "u": "un", "ö": "ün", "ü": "ün"}[son]
    return f"{ad}'{'n' if ad[-1].lower() in SESLI else ''}{ek}"


TR_IYELIKLI = ("gözleri", "çenesi", "omuzları", "kuyruğunun", "ağzı", "kaşları")


def _cok_kisi(plan):
    z = plan.get("zanaat") or {}
    gor = [k for k in z.get("kadrajdakiler") or [] if k.get("olcek") != "el"]
    oz = {a.get("ozne") for a in z.get("eylem_zinciri") or []}
    return len({k.get("id") for k in gor} | oz) > 1


# --- adım cümlesi -------------------------------------------------------------------------------------------------
def adim_cumlesi(a, plan, B, dil="en"):
    """(cümle, kelime). EN öznesiz şablon; çok kişide adlı. TR daima adlı."""
    fil = po.fiiller().get(a.get("fiil")) or {}
    ps = po.sozluk("plan"); kid = a.get("ozne"); cok = _cok_kisi(plan)
    pos = B["pos"].get(kid, "its" if kid not in B["ad"] else "their")
    if a.get("tur") == "konusma" or a.get("fiil") == "konusur":
        rep = plan.get("replik") or {}
        tes = (ps.get("teslim") or {}).get(rep.get("teslim") or "normal") or {"en": "says", "tr": "der"}
        cs = rep.get("cumleler") or []; secim = a.get("cumleler")
        metin = rep.get("veo_metin") or rep.get("metin") or ""
        if secim and cs and len(secim) < len(cs): metin = " ".join(cs[i]["en" if dil == "en" else "tr"] for i in secim if i < len(cs))
        elif dil != "en" and cs: metin = " ".join(c.get("tr") or c.get("en") for c in cs)
        if dil == "en":
            ses = B["ses"].get(kid)
            ses_k = (", " + (ses if ses.startswith("in ") else "in " + ses)) if ses else ""
            c = f"{_ad(B, kid)} {tes['en']}{ses_k}: \"{metin}\""
        else:
            c = f"{_ad(B, kid, dil)} {tes['tr']}: \"{metin}\""
        return c, kelime(c)
    el = _el_adi(a); tutulan = _tut(B, plan, kid, el, a)
    govde = ((ps.get("govde") or {}).get(a.get("govde")) or {})
    hedef = a.get("hedef")
    if dil == "en":
        if el == "sol" and a.get("el_sekli") == "kiskac" and fil.get("en_kiskac"): s = fil["en_kiskac"]
        elif el == "sag" and a.get("el_sekli") == "kiskac" and fil.get("en_kiskac"): s = fil["en_kiskac"]
        elif tutulan and fil.get("en_nesne"): s = fil["en_nesne"]
        elif not hedef and a.get("yon") and fil.get("en_yon"): s = fil["en_yon"]
        else: s = fil.get("en") or (a.get("fiil") or "").replace("_", " ")
        if hedef in B["ad"]: s = s.replace("the {hedef}", "{hedef}")
        yon = ((ps.get("yon") or {}).get(a.get("yon")) or {}).get("en") or ""
        el_en = (govde.get("en") or "{pos} hand") if el else "{pos} hand"
        kol = el_en.replace("hand", "arm") if "arm" not in el_en else el_en
        if a.get("fiil") == "uzanir" and not tutulan: kol = kol.replace("{pos} ", "{pos} empty ")
        es = ((ps.get("el_sekli") or {}).get(a.get("el_sekli")) or {}).get("en") or ""
        rep = {"{elsiz}": el_en.replace(" hand", "").replace(" arm", ""), "{el}": el_en, "{kol}": kol, "{hedef}": _nesne(B, hedef), "{nesne}": _nesne(B, tutulan) or "object",
               "{olcu}": _olcu(a.get("olcu")), "{yon}": yon, "{el_sekli}": es}
        for k, v in rep.items(): s = s.replace(k, v)
        bas_pos = s.startswith("{pos} ")
        s = s.replace("{pos}", pos)
        if cok:
            if bas_pos: s = f"{_ad(B, kid)}'s " + s[len(pos) + 1:]
            elif s.startswith("the "): s = f"{_ad(B, kid)}'s " + s[4:]
            elif s.startswith("a "): s = f"{_ad(B, kid)}'s face: " + s
            else: s = f"{_ad(B, kid)} " + s
        hz = ((ps.get("hiz") or {}).get(a.get("hiz")) or {}).get("en")
        if hz and hz[:4] not in s: s += f", {hz}"
        dl = plan.get("_derlenir") or {}
        if a.get("fiil") in ("bakis_kaydirir", "basini_cevirir"):
            yk = (dl.get("bakis_kadrajda") or {}).get(f"{kid}@bit")
            gor = {k.get("id") for k in (plan.get("zanaat") or {}).get("kadrajdakiler") or []}
            if yk and hedef not in gor: s += ", toward " + yk.replace("kadraj_", "frame ").replace("solu", "left").replace("sagi", "right")
            gz = (dl.get("goz_yukseklik_farki") or {}).get(kid)
            if gz: s += ", looking " + ("down" if gz == "asagi" else "up")
        s = re.sub(r"\s+", " ", s).strip().rstrip(",")
        return s, kelime(s)
    s = fil.get("tr_nesne") if tutulan and fil.get("tr_nesne") else fil.get("tr_yon") if (not hedef and a.get("yon") and fil.get("tr_yon")) else fil.get("tr")
    s = s or (a.get("fiil") or "").replace("_", " ")
    yon = ((ps.get("yon") or {}).get(a.get("yon")) or {}).get("tr") or ""
    es = ((ps.get("el_sekli") or {}).get(a.get("el_sekli")) or {}).get("tr") or ""
    el_tr = govde.get("tr") or "elini"; ile = govde.get("tr_ile") or "eliyle"
    kol_tr = el_tr.replace("elini", "kolunu") if "elini" in el_tr else el_tr
    for k, v in {"{el_ile}": ile, "{el}": el_tr, "{kol}": kol_tr, "{hedef}": _nesne(B, hedef, dil), "{nesne}": _nesne(B, tutulan, dil),
                 "{olcu}": _olcu(a.get("olcu"), "tr"), "{yon}": yon, "{el_sekli}": es, "{pos}": ""}.items(): s = s.replace(k, v)
    hz = ((ps.get("hiz") or {}).get(a.get("hiz")) or {}).get("tr")
    if s.startswith(TR_IYELIKLI): s = f"{iyelik(_ad(B, kid, dil))} " + s
    else: s = f"{_ad(B, kid, dil)} " + (f"{hz} " if hz and hz[:4] not in s else "") + s
    s = re.sub(r"\s+", " ", s).strip()
    return s, kelime(s)


# --- plan tarifleri -----------------------------------------------------------------------------------------------
def kamera_cumlesi(plan, dil="en"):
    ps = po.sozluk("plan"); k = (plan.get("zanaat") or {}).get("kamera") or {}
    kad = (ps.get("kadraj") or {}).get(k.get("kadraj")) or {}
    ht = (ps.get("hareket_tipi") or {}).get(k.get("hareket_tipi") or "sabit") or {"en": "Static"}
    aci = (ps.get("aci") or {}).get(k.get("aci")) or {}
    if dil == "en":
        a = f" {aci['en']}" if aci and k.get("aci") not in (None, "goz_hizasi") else ""
        h = ht["en"] if ht["en"] == "Static" else ht["en"] + ","
        ke = kad.get("en", "medium")
        return f"{h}{a} {ke}" + ("." if ke.endswith(("shot", "insert")) else " shot.")
    return f"{kad.get('tr', k.get('kadraj', ''))} · {k.get('hareket_tipi') or 'sabit'} · {k.get('kurulum') or '?'}"


def _dinleyenler(plan, B, dil="en"):
    z = plan.get("zanaat") or {}
    oz = {a.get("ozne") for a in z.get("eylem_zinciri") or []}
    konusma = any(a.get("tur") == "konusma" for a in z.get("eylem_zinciri") or [])
    eds = bool(z.get("ekran_disi_ses"))
    ps = po.sozluk("plan"); out = []
    for k in z.get("kadrajdakiler") or []:
        kid = k.get("id")
        if kid in oz or k.get("olcek") == "el": continue
        if k.get("yuz_acisi") in ("sirt", "gorunmez"):
            t = ps["sessiz_bekleme"]["en" if dil == "en" else "tr"]
            out.append(f"{_ad(B, kid, dil)} {t.replace('still,', 'still, seen from behind,') if dil == 'en' else t}")
        elif konusma or eds:
            out.append(f"{_ad(B, kid, dil)} {ps['dinleme']['en' if dil == 'en' else 'tr']}")
        else:
            out.append(f"{_ad(B, kid, dil)} {ps['bekleme'][B.get('bekleme', 'sabit')]['en' if dil == 'en' else 'tr']}")
    return out


def adimlar_en(plan, B, bicim="aralik"):
    """[(adım id, cümle, kelime)] — saniyeli (aralik) ya da sıralı (sira)."""
    z = plan.get("zanaat") or {}; ps = po.sozluk("plan"); klip = z.get("klip_sn") or 8
    ad = sorted([a for a in z.get("eylem_zinciri") or [] if isinstance(a, dict)], key=lambda a: a.get("bas") or 0)
    eds = bool(z.get("ekran_disi_ses")); out = []
    oz_tek = len({a.get("ozne") for a in ad}) == 1 and not _cok_kisi(plan)
    for i, a in enumerate(ad):
        c, _ = adim_cumlesi(a, plan, B, "en")
        if eds and i == 0 and a.get("tur") != "konusma" and oz_tek: c = f"{ps['dinleme']['en']}; {c}"
        if bicim == "sira":
            on = "First, " if i == 0 else ("Finally, " if i == len(ad) - 1 else "Then, ")
            c = on + c
        else:
            c = f"{sn(a.get('bas'))}-{sn(a.get('bit'))}s: {c}"
        out.append((a.get("id"), c, kelime(c)))
    son = max([a.get("bit") or 0 for a in ad] or [0.5])
    bek = ps["bekleme"][B.get("bekleme", "sabit")]["en"]
    kim = "" if oz_tek or not ad else ("they " if len({a.get("ozne") for a in ad}) > 1 else f"{_ad(B, ad[-1].get('ozne'))} ")
    if kim == "they ": bek = bek.replace("holds", "hold")
    tut = f"{kim}{bek}" + (", mouth closed" if any(a.get("tur") == "konusma" for a in ad) else "")
    out.append(("bitis", (f"Then {tut}." if bicim == "sira" else f"{sn(son)}-{sn(klip)}s: {tut}."), 0))
    return out


def gorunur_tarif(plan, dil, B, bicim="aralik"):
    z = plan.get("zanaat") or {}
    if dil == "en":
        par = [kamera_cumlesi(plan, "en")]
        dn = _dinleyenler(plan, B, "en")
        if dn: par.append("; ".join(dn) + ".")
        for _, c, _ in adimlar_en(plan, B, bicim):
            par.append(c if c.endswith((".", "\"")) else c + ".")
        return " ".join(p if p.endswith((".", "\"")) else p + "." for p in par)
    ad = sorted([a for a in z.get("eylem_zinciri") or [] if isinstance(a, dict)], key=lambda a: a.get("bas") or 0)
    satir = [(a.get("id"), a.get("bas"), a.get("bit"), adim_cumlesi(a, plan, B, "tr")[0]) for a in ad]
    if dil == "serit":
        return " | ".join(f"{i} {c}" for i, _, _, c in satir) or "(eylem yok)"
    dn = _dinleyenler(plan, B, "tr")
    if dil == "cekim":
        out = [kamera_cumlesi(plan, "tr")] + [f"[{sn_tr(b)}–{sn_tr(e)} sn] {c}" for _, b, e, c in satir]
        if dn: out.append("Ayrıca: " + "; ".join(dn))
        return out
    k = (z.get("kamera") or {}); kad = ((po.sozluk("plan").get("kadraj") or {}).get(k.get("kadraj")) or {}).get("tr", "")
    metin = [f"{kad.capitalize()} plan." if kad else ""]
    if dn: metin.append("; ".join(dn) + ".")
    metin += [f"{sn_tr(b)}–{sn_tr(e)} sn: {c}." for _, b, e, c in satir]
    return " ".join(m for m in metin if m)


def durum_tarifi(durum, B, dil="tr", kim=None):
    """Başlangıç/bitiş karesinin olgu özeti (çekim listesi, kör paket)."""
    if not isinstance(durum, dict): return ""
    ps = po.sozluk("plan"); s = []
    for k, v in sorted((durum.get("karakterler") or {}).items()):
        if kim and k not in kim: continue
        par = [_ad(B, k, dil) + ":", str(v.get("isaret") or v.get("mekan") or "?")]
        pz = (ps.get("poz") or {}).get(v.get("poz"))
        if pz: par.append(pz["tr" if dil == "tr" else "en"])
        for el, ad in (("sag", "sağ"), ("sol", "sol")):
            t = (((v.get("eller") or {}).get(el)) or {}).get("tutar")
            if t: par.append(f"{ad} elinde {_nesne(B, t, dil)}" if dil == "tr" else f"{_nesne(B, t)} in {B['pos'].get(k, 'their')} {'right' if el == 'sag' else 'left'} hand")
        if v.get("ifade"):
            ifd = ((po.sozluk("ifade").get("degerler") or {}).get(v["ifade"]) or {})
            par.append(ifd.get("tr" if dil == "tr" else "en") or v["ifade"])
        s.append(" ".join(par))
    return "; ".join(s)


def main(argv):
    if "--film" not in argv or "--plan" not in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film")); no = int(po.arg_al(argv, "--plan"))
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
    p = next((x for x in s.get("sahneler") or [] if x.get("no") == no), None)
    if not p: print(f"!! plan {no} yok", flush=True); return 2
    B = baglam(kok, s); dil = po.arg_al(argv, "--dil", "en")
    t = gorunur_tarif(p, dil, B, po.arg_al(argv, "--zaman-bicimi", "aralik"))
    print("\n".join(t) if isinstance(t, list) else t)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
