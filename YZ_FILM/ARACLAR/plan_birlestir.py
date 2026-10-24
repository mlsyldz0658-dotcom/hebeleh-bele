"""PLAN BİRLEŞTİR — yönetmenin sahne grubu planlarını (PLANLAR) ve haritalarını SAHNELER.json v2'ye birleştirir (TASARIM §5.1, §6.4, A07c).

Kullanım:
  python plan_birlestir.py --film <film> [--kuru]      _YONETMEN/HARITA_P*.json + _YONETMEN/PLANLAR/*.json + HIKAYE.json → SAHNELER.json
                                                       (--kuru: yazmaz, özet basar)
Kodda: topla(kok) → (sahneler_v2, olcumler) · kaynak_sahneler(kok) → bellekte v2 (PLANLAR varsa onlardan, yoksa SAHNELER.json)
Ne yapar:
  - Kalıcı kod → no eşlemesi `_YONETMEN/NO_ESLEME.json` (no kimliktir, yeniden numaralanmaz; yeni plan en büyük no + 1).
    sira = kurgu sırası (HIKAYE sahne sırası × plan sırası); parti = hikâye partisi (HIKAYE sahne hikaye_partisi, yoksa harita parti).
  - Replik metni HIKAYE.json'daki R kimliğinden kelimesi kelimesine gelir (cümle bölme EN/TR); yönetmen metne dokunamaz.
  - karakterler.<id>.{ref, ses, ses_adi, evren, kostum_varsayilan} evrenden doldurulur; evrende kart varsa 01_KARAKTERLER/<id>.jpg'ye
    kopyalanır (yoksa ref yolu yazılır, BAYRAK). ses A10c'de seçilir (o zamana kadar null).
  - Derlenen eski alanlar: referans (kadrajdakiler), duygu (hedef duygunun ilk türü), bitis_karesi (zincir.bitis_sabitle), motor (flow).
  - _derlenir: sure_sn, kesme_nokta_sn, replik_zaman, hikaye (HIKAYE sahne alanları + planın yerleştirdiği kimlikler) ve kroki.py geometrisi
    (dünya defteri çözümüyle: kadraj konumu/sırası, kamera tarafı, bakış/ışık/ekran yönü, ağız, açık parmak, ayna yasağı, görünmesi gerekenler).
    Sahne düzeyinde _derlenir.{ana_kareler, yasak_ardisik}. Her planın _derlenir imzası _YONETMEN/DERLENIR_IMZA.json'a yazılır
    (plan_sema elle yazımı bu imzayla yakalar).
  - uretim, denetim, kurgu ve derlenmiş istemler eski SAHNELER.json'dan aynı no ile korunur (sahipleri başka araçlardır).
  - Ajan çıktısında `_derlenir` varsa HATA (yalnız kod yazar; §5.1 kural 5).
Çıkış kodları: 0 tamam · 1 HATA (rapor _RAPOR/SEMA_BIRLESTIR.json) · 2 PLANLAR/HARITA yok · 4 kullanım.
"""
import os, sys, re, glob, shutil, copy
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "plan_birlestir 1.0"
KORUNAN = ("uretim", "denetim", "kurgu", "gorsel_istem", "gorsel_istem_yedek", "hareket_istem", "hareket_istem_yedek")
# Ses kâğıdının (A08 ses_plani) yazdığı alanlar: yeniden birleştirmede (A07c tekrar) kaybolmasın. Yönetmen dosyası aynı alanı yazmışsa
# yönetmeninki geçer (ses_plani --denetle sonra yeniden uygular); replik değiştiyse replike bağlı derlenmiş ses alanları taşınmaz.
KORUNAN_SES_ZANAAT = ("ses",)
KORUNAN_SES_DERLENIR = ("ton_fiili_en", "seviye", "muzik_ipucu")
CUMLE = re.compile(r"(?<=[.!?])\s+")


def _yonetmen(kok, *p): return os.path.join(kok, "_YONETMEN", *p)


def haritalar(kok):
    out = []
    for y in sorted(glob.glob(_yonetmen(kok, "HARITA_P*.json"))):
        h = ortak.json_oku(y)
        if isinstance(h, dict):
            m = re.search(r"HARITA_P(\d+)", y); h.setdefault("parti", int(m.group(1)) if m else 1); out.append(h)
    return out


def plan_dosyalari(kok):
    out = []
    for y in sorted(glob.glob(_yonetmen(kok, "PLANLAR", "*.json"))):
        d = ortak.json_oku(y)
        if isinstance(d, dict): out.append((y, d))
    return out


def _parti(x):
    if isinstance(x, int): return x
    m = re.search(r"(\d+)", str(x or "")); return int(m.group(1)) if m else None


def _cumleler(metin, tr):
    en = [c for c in CUMLE.split((metin or "").strip()) if c]
    trs = [c for c in CUMLE.split((tr or "").strip()) if c]
    if len(trs) != len(en): trs = [tr or ""] + [""] * (len(en) - 1)
    return [{"en": e, "tr": t} for e, t in zip(en, trs)]


def _replik(rid, hikaye, olc, no):
    for r in (hikaye or {}).get("replikler") or []:
        if r.get("id") == rid:
            return {"id": rid, "karakter": r.get("karakter"), "metin": r.get("metin"), "teslim": r.get("teslim") or "normal",
                    "cumleler": _cumleler(r.get("metin"), r.get("tr")), "veo_metin": r.get("veo_metin")}
    olc.append(po.m("replik_hikayede_yok", "HATA", no, olcu=rid, neden="replik kimliği HIKAYE.json'da yok"))
    return None


def _evren_karakter(kok, seri, kid):
    """<evren>/karakterler/<id> (veri kökü; yoksa film klasöründeki EVREN/ — örnek/test filmi)."""
    if not seri: return None, {}
    adaylar = []
    try: adaylar.append(os.path.join(ortak.yollar()["evren_kok"], seri, "karakterler", kid))
    except ortak.YolYok: pass
    adaylar.append(os.path.join(kok, "EVREN", seri, "karakterler", kid))
    d = next((a for a in adaylar if os.path.isdir(a)), adaylar[0])
    return d, ortak.json_oku(os.path.join(d, "ses.json"), {}) or {}


def karakterler(kok, hikaye, olc, kopyala=False):
    seri = (hikaye or {}).get("evren"); out = {}
    for kid, kv in ((hikaye or {}).get("karakterler") or {}).items():
        d, ses = _evren_karakter(kok, seri, kid)
        ref = f"01_KARAKTERLER/{kid}.jpg"
        kart = next((p for p in ((os.path.join(d, "kart.jpg"), os.path.join(d, "kart.png")) if d else ()) if os.path.isfile(p)), None)
        if kart and kopyala:
            hedef = os.path.join(kok, ref); os.makedirs(os.path.dirname(hedef), exist_ok=True)
            if not os.path.isfile(hedef): shutil.copy2(kart, hedef)
        elif not os.path.isfile(os.path.join(kok, ref)):
            olc.append(po.m("kart_yok", "BAYRAK", None, kim=kid, neden="evren kartı henüz yok (A10d'de kilitlenir)"))
        out[kid] = {"ref": ref, "ses": ses.get("voice_id") or ses.get("ses"), "ses_adi": ses.get("ad") or ses.get("ses_adi"),
                    "evren": f"EVREN/{seri}/karakterler/{kid}" if seri else None,
                    "kostum_varsayilan": ((kv.get("kostum") or {}).get("varsayilan")) if isinstance(kv.get("kostum"), dict) else None}
    return out


def _sahne_sirasi(hikaye, gruplar):
    hs = [s.get("id") for s in (hikaye or {}).get("sahneler") or [] if s.get("id")]
    return hs + sorted(g for g in gruplar if g not in hs)


def _hikaye_sahne(hikaye, sid):
    return next((s for s in (hikaye or {}).get("sahneler") or [] if s.get("id") == sid), {})


def _derlenir_yok(x, yol=""):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "_derlenir": return yol + "._derlenir" if yol else "_derlenir"
            r = _derlenir_yok(v, f"{yol}.{k}" if yol else k)
            if r: return r
    if isinstance(x, list):
        for i, v in enumerate(x):
            r = _derlenir_yok(v, f"{yol}[{i}]")
            if r: return r
    return None


def _hikaye_derlenir(z, hs):
    ilk = lambda x: (str(x or "").replace("→", ">").split(">")[0].strip() or None)
    return {"vurus": z.get("vurus") or hs.get("vurus"), "hedef_duygu": ilk(z.get("hedef_duygu") or hs.get("hedef_duygu")),
            "yogunluk": z.get("yogunluk") if z.get("yogunluk") is not None else hs.get("yogunluk"),
            "merak_ac": list(z.get("merak_ac") or []), "merak_kapat": list(z.get("merak_kapat") or []),
            "kurulum": list(z.get("kurulum") or []), "kullanim_bilgi": list(z.get("kullanim_bilgi") or []),
            "ironi": z.get("ironi"), "risk": hs.get("risk")}


def topla(kok, kopyala=False):
    """Bellekte SAHNELER v2 kurar. (sahneler, olcumler)"""
    olc = []
    hikaye = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    H = haritalar(kok); P = plan_dosyalari(kok)
    eski = ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
    eski_no = {p.get("no"): p for p in eski.get("sahneler") or [] if isinstance(p, dict)}
    esleme = ortak.json_oku(_yonetmen(kok, "NO_ESLEME.json"), {}) or {}
    kod_no = dict(esleme.get("kod_no") or {})
    mekanlar, gruplar, parti_sg = {}, {}, {}
    for h in H:
        for y in ("mekanlar", "sahne_gruplari"):
            r = _derlenir_yok(h.get(y))
            if r: olc.append(po.m("derlenir_ajan_yazimi", "HATA", None, olcu=f"HARITA_P{h['parti']}:{y}.{r}", kural="§5.1 kural 5"))
        for mid, mv in (h.get("mekanlar") or {}).items(): mekanlar.setdefault(mid, copy.deepcopy(mv))
        for sid, sv in (h.get("sahne_gruplari") or {}).items():
            gruplar[sid] = copy.deepcopy(sv); parti_sg[sid] = h["parti"]
    plan_by_sg = {}
    for yol, d in P:
        sid = d.get("sahne_grubu") or ((d.get("planlar") or [{}])[0].get("zanaat") or {}).get("sahne_grubu")
        r = _derlenir_yok(d)
        if r: olc.append(po.m("derlenir_ajan_yazimi", "HATA", None, olcu=f"{os.path.basename(yol)}:{r}", kural="§5.1 kural 5",
                              neden="_derlenir yalnız kod yazar; ajan yazarsa HATA"))
        if sid in plan_by_sg: olc.append(po.m("sahne_iki_dosyada", "HATA", None, sahne=sid, olcu=os.path.basename(yol)))
        plan_by_sg[sid] = d.get("planlar") or []
    if not H or not P: return None, olc + [po.m("harita_ya_da_plan_yok", "HATA", None)]
    for sid in plan_by_sg:
        if sid not in gruplar: olc.append(po.m("sahne_haritada_yok", "HATA", None, sahne=sid))
    sahneler, sira = [], 0
    en_buyuk = max([int(v) for v in kod_no.values()] + [0])
    for sid in _sahne_sirasi(hikaye, gruplar):
        if sid not in plan_by_sg: continue
        hs = _hikaye_sahne(hikaye, sid); sg = gruplar.get(sid) or {}
        sg.setdefault("hikaye", {"sahne": sid, "parti": _parti(hs.get("hikaye_partisi")) or parti_sg.get(sid)})
        for pl in plan_by_sg[sid]:
            z = copy.deepcopy(pl.get("zanaat") or {}); kod = z.get("kod")
            z.setdefault("sahne_grubu", sid)
            if not kod: olc.append(po.m("kod_yok", "HATA", None, sahne=sid)); continue
            if kod in [p["zanaat"]["kod"] for p in sahneler]: olc.append(po.m("kod_tekrar", "HATA", None, olcu=kod)); continue
            if kod not in kod_no: en_buyuk += 1; kod_no[kod] = en_buyuk
            no = int(kod_no[kod]); sira += 1
            p = {"no": no, "sira": sira, "parti": _parti(hs.get("hikaye_partisi")) or parti_sg.get(sid) or 1}
            rep = pl.get("replik")
            rid = rep.get("id") if isinstance(rep, dict) else rep if isinstance(rep, str) else None
            if not rid:
                rid = next((a.get("replik") for a in z.get("eylem_zinciri") or [] if a.get("tur") == "konusma" and a.get("replik")), None)
            p["replik"] = _replik(rid, hikaye, olc, no) if rid else None
            if isinstance(rep, dict) and p["replik"] and rep.get("metin") and rep["metin"] != p["replik"]["metin"]:
                olc.append(po.m("replik_metni_degisti", "HATA", no, olcu=rid, neden="replik metni HIKAYE.json ile kelimesi kelimesine aynı olmalı"))
            p["amac"] = pl.get("amac") or z.get("ekranda_bilgi")
            hd = _hikaye_derlenir(z, hs)
            p["duygu"] = hd["hedef_duygu"]
            p["kullanim"] = copy.deepcopy(pl.get("kullanim") or {"bas": 0.5, "sure": max(1.0, (z.get("klip_sn") or 8) - 1.0)})
            p["zanaat"] = z
            p["motor"] = "flow"
            ep = eski_no.get(no) or {}
            for k in KORUNAN:
                if k in ep: p[k] = copy.deepcopy(ep[k])
            p.setdefault("gorsel_istem", ""); p.setdefault("hareket_istem", "")
            k_ = p["kullanim"]; dl = {"sure_sn": k_.get("sure"), "kesme_nokta_sn": round((k_.get("bas") or 0) + (k_.get("sure") or 0), 2)}
            rz = {a.get("replik"): [a.get("bas"), a.get("bit")] for a in z.get("eylem_zinciri") or [] if a.get("tur") == "konusma" and a.get("replik")}
            dl["replik_zaman"] = rz; dl["hikaye"] = hd
            if (ep.get("_derlenir") or {}).get("istem_ozeti"): dl["istem_ozeti"] = ep["_derlenir"]["istem_ozeti"]
            ez = ep.get("zanaat") or {}
            for k in KORUNAN_SES_ZANAAT:
                if k not in z and k in ez: z[k] = copy.deepcopy(ez[k])
            if ((ep.get("replik") or {}).get("id")) == ((p.get("replik") or {}).get("id")):
                for k in KORUNAN_SES_DERLENIR:
                    if k in (ep.get("_derlenir") or {}): dl[k] = copy.deepcopy(ep["_derlenir"][k])
            p["_derlenir"] = dl
            sahneler.append(p)
    # bitis_karesi (Memmet uyumu, §5.1 kural 7; [YN2] §4.5.13 #9)
    for i, p in enumerate(sahneler):
        zn = p["zanaat"].get("zincir") or {}
        if zn.get("bitis_sabitle"):
            sonraki = sahneler[i + 1] if i + 1 < len(sahneler) else None
            dv = sonraki and (sonraki["zanaat"].get("zincir") or {}).get("gecis_turu") == "devam"
            p["bitis_karesi"] = sonraki["no"] if dv else f"{p['no']:03d}_son"
    for sid, sg in gruplar.items():                                   # sahne_gruplari.<S>.ses (A08) korunur
        es = (eski.get("sahne_gruplari") or {}).get(sid) or {}
        if "ses" not in sg and "ses" in es: sg["ses"] = copy.deepcopy(es["ses"])
    seri = hikaye.get("evren")
    doc = {"_surum": 2, "_sema": "sahneler_v2", "_uretim": po.zarf("A07c", SURUM), "film": os.path.basename(kok),
           "baslik": seri or hikaye.get("baslik_ekran") or os.path.basename(kok), "altyazi_dili": None,
           "karakterler": karakterler(kok, hikaye, olc, kopyala), "mekanlar": mekanlar, "sahne_gruplari": gruplar, "sahneler": sahneler}
    _geometri(kok, doc, hikaye, olc)
    doc["_uretim"]["girdi_imza"] = po.imza([H, [d for _, d in P], hikaye.get("replikler")])
    doc["_uretim"]["sonuc"] = "HATA" if any(o["seviye"] == "HATA" for o in olc) else "GEC"
    doc["_no_esleme"] = kod_no                                        # yazmadan önce çıkarılır
    return doc, olc


def _geometri(kok, doc, hikaye, olc):
    """Dünya defteri çözümü + kroki → _derlenir geometri alanları ve sahne _derlenir'i."""
    import dunya_defteri, kroki
    E = po.esik()
    try:
        C = dunya_defteri.coz(doc, hikaye)
        K = kroki.Kroki(kok, doc)
    except Exception as e:
        olc.append(po.m("geometri_hesaplanamadi", "HATA", None, neden=f"{e.__class__.__name__}: {e}")); return
    kb = {}
    for kid, kv in (hikaye.get("karakterler") or {}).items():
        kb[kid] = {"asimetrik": bool(kv.get("gorsel_ayirt_edici") or kv.get("asimetrik")), "goz_yuksekligi_m": kv.get("goz_yuksekligi_m")}
    for kid in doc["karakterler"]: kb.setdefault(kid, {})
    for sid, sg in doc["sahne_gruplari"].items():
        sp = [p for p in doc["sahneler"] if p["zanaat"].get("sahne_grubu") == sid]
        ak = {}
        for p in sp:
            k = (p["zanaat"].get("kamera") or {}).get("kurulum")
            if k and k not in ak: ak[k] = p["no"]
        sg["_derlenir"] = {"ana_kareler": ak, "yasak_ardisik": kroki.yasak_ardisik(K, sg.get("mekan"), sg, E)}
        for p in sp:
            d = C.planlar.get(str(p["no"])) or {"bas": {}, "bit": {}}
            dl, _ = kroki.derle(p, d["bas"], d["bit"], K, sg, E, kb)
            for k, v in dl.items():
                if not k.startswith("_"): p["_derlenir"][k] = v
            if len(p["_derlenir"].get("referans") or []) > 0: p["referans"] = p["_derlenir"]["referans"]
            else: p["referans"] = []


def kaynak_sahneler(kok):
    """Denetim araçları için bellekte v2: PLANLAR varsa onlardan (A07b), yoksa SAHNELER.json."""
    if plan_dosyalari(kok) and haritalar(kok):
        s, _ = topla(kok)
        if s is not None:
            s.pop("_no_esleme", None)
            sd = ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
            ist = {p.get("no"): p for p in sd.get("sahneler") or []}
            for p in s["sahneler"]:
                for k in ("hareket_istem", "hareket_istem_yedek"):
                    if (ist.get(p["no"]) or {}).get(k): p[k] = ist[p["no"]][k]
            return s
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    return s if isinstance(s, dict) else None


def derlenir_imzalari(doc):
    return {str(p["no"]): po.imza(p.get("_derlenir") or {}) for p in doc.get("sahneler") or []}


def imza_yaz(kok, doc):
    ortak.atomik_yaz(_yonetmen(kok, "DERLENIR_IMZA.json"), {"_surum": 1, "_uretim": po.zarf("A07c", SURUM), "imzalar": derlenir_imzalari(doc)})


def birlestir(kok, kuru=False):
    doc, olc = topla(kok, kopyala=not kuru)
    if doc is None: return None, olc
    kod_no = doc.pop("_no_esleme")
    if not kuru and not any(o["seviye"] == "HATA" for o in olc):
        ortak.atomik_yaz(_yonetmen(kok, "NO_ESLEME.json"), {"_surum": 1, "_uretim": po.zarf("A07c", SURUM), "kod_no": kod_no})
        ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), doc)
        imza_yaz(kok, doc)
    return doc, olc


def main(argv):
    if "-h" in argv or "--help" in argv or "--film" not in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film"))
    doc, olc = birlestir(kok, "--kuru" in argv)
    if doc is None:
        print("!! _YONETMEN/HARITA_P*.json ya da _YONETMEN/PLANLAR/*.json yok", flush=True)
        for o in olc: print("  ", o, flush=True)
        return 2
    hata = [o for o in olc if o["seviye"] == "HATA"]
    if hata or "--kuru" in argv:
        yol, r = po.rapor_yaz(kok, "SEMA", "BIRLESTIR", olc, asama="A07c", arac=SURUM, birimler=[p["no"] for p in doc["sahneler"]])
        po.yaz_ozet(r, "birleştirme")
        if hata: return 1
    print(f"SAHNELER.json v2: {len(doc['sahneler'])} plan, {len(doc['sahne_gruplari'])} sahne grubu, BAYRAK {len(olc)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
