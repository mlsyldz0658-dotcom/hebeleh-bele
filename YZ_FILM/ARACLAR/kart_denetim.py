"""KART DENETİM — kart kapısı (A10d): yüz sayısı, öz tutarlılık, kadro ayrışması, stil, fon, plaka "görünmesi gerekenler", kör gözlem, karar
(TASARIM §6.5, §7.2 KART; [GS2] GS4, §4.7.2, İ-12).

Kullanım (film.py calis çağırır: "kart_denetim.py --film <film>"; tur GOREV.json'dan ya da --tur):
  python kart_denetim.py --film <film> [--tur N]           yerel ölçüm + kör gözlem (_KARTLAR/gozlem_t<tur>_<i>.json) + karar
        → _RAPOR/KART_KAPISI.json (kapı; birim = kart), _KARTLAR/KART_DUZELTME.json (CORRECTION ve tarif revizyonu istekleri),
          _KARTLAR/GORUNUS_DEGISIKLIK_ISTEGI.json (ayrisma_kilitli: hikâyeye bağlı öğe → senarist)
  python kart_denetim.py --kor-gorev --film <film> [--tur N]   kart kör paketi _KOR_PAKET/kart_t<tur>/<i>/ (gemini_al --kartlar da çağırır)
  Kodda: import kart_denetim as kd · kd.denetle(kok, tur) → (kod, rapor) · kd.kadro_karari(a, b, sim, spec_a, spec_b) → madde ya da None
Kurallar (§7.2 KART, [GS2] §4.7.2):
  - İnsan kart sayfasında YuNet yüz sayısı = kart_gorunum_sayisi (6) değilse HATA; görünümler arası SFace en düşük çift < 0,363 HATA,
    < 0,45 BAYRAK; iki farklı karakter (kilitli kadro bankaları + bu turun öteki kartları) ≥ 0,363 HATA, 0,25–0,363 BAYRAK
    (bilincli_benzerlik hariç). Ayrışma yalnız hikâyeye bağlı öğelerle sağlanabiliyorsa HATA ayrisma_kilitli (sahibi senarist, İ-12).
  - CLIP "photograph" < 0,5 ve kör "çizim" → HATA; tek kaynak BAYRAK. Fon kenar std > kart_fon_std_max BAYRAK. Uzun kenar < 1376 HATA.
  - Kör: NE YOK öğesi HATA; tarifteki zorunlu öğe görülmedi HATA; asimetrik iz görüntüde yanlış tarafta HATA; plakada kişi ya da yüz
    (yerel ya da kör) HATA; plakada görünmesi gereken öğe yanlış üçte birde: kör + yerel HATA, tek kaynak BAYRAK; plaka nötr değil HATA.
  - Yaratık kartında kimlik_isaretleri < kart_yaratik_isaret_min BAYRAK. ÖLÇÜLEMEDİ = BAYRAK, asla GEÇ.
  - Kart birimi: en iyi adayın kararı; sanat seçimini yonetmen·kart_secimi yapar, kod yalnız teknik eler (GEÇ/BAYRAK adaylar seçilebilir).
Çıkış kodları: 0 tamam (kapı sonucu raporda) · 1 girdi/program hatası · 2 aday ya da KART_ISTEMLERI yok · 4 kullanım.
"""
import os, sys, re, json, glob, itertools
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kart_denetim 1.0"
SIRA = {"GEC": 0, "BAYRAK": 1, "HATA": 2}


def _po():
    import plan_ortak as po
    return po


def _spec(kok):
    import istem_derle_gorsel as idg
    s = ortak.json_oku(os.path.join(kok, "_KARTLAR", "KART_SPEC.json"), {}) or {}
    return {"karakter": {k["id"]: k for k in idg._liste(s.get("karakterler"))}, "mekan": {k["id"]: k for k in idg._liste(s.get("mekanlar"))},
            "nesne": {k["id"]: k for k in idg._liste(s.get("nesneler"))}}


def kart_adaylari(kok):
    """[(kart, aday, yol)] KART_ISTEMLERI'ndeki dosya adlarına göre."""
    ki = ortak.json_oku(os.path.join(kok, "_KARTLAR", "KART_ISTEMLERI.json"), {}) or {}
    out = []
    for k in ki.get("kartlar") or []:
        for a, d in zip(k.get("adaylar") or [], k.get("dosyalar") or []):
            p = os.path.join(kok, "_KARTLAR", "adaylar", d)
            if os.path.isfile(p): out.append((k, a, p))
    return out


def baglam(kok, k, spec, ev):
    import istem_derle_gorsel as idg
    try:
        import evren
        ne_yok = evren.ne_yok_kelimeleri(film=kok)
    except Exception: ne_yok = []
    b = {"tur": k["tur"], "ne_yok": ne_yok}
    if k["tur"] == "karakter":
        s = spec["karakter"].get(k["id"]) or {}
        b["gorunum_sayisi"] = 6 if s.get("tur") != "yaratik" else 4
        og = [o["oge"] if isinstance(o, dict) else str(o) for o in s.get("ayirt_edici") or []]
        b["ogeler"] = [o for o in og if re.search(r"[a-z]", o) and o.isascii()]
        diger = []
        for kid, d in spec["karakter"].items():
            if kid != k["id"]: diger += [o["oge"] if isinstance(o, dict) else str(o) for o in d.get("ayirt_edici") or []]
        b["yanlis_ogeler"] = [o for o in diger if o.isascii() and o not in b["ogeler"]] + ["a zipper", "a wristwatch", "sunglasses"]
        b["asimetrik"] = []
        for a in s.get("asimetrik") or []:
            t = a if isinstance(a, str) else a.get("oge", "")
            m = re.search(r"\b(RIGHT|LEFT)\b", t)
            if m and t.isascii():
                oge = re.sub(r"\s+", " ", re.sub(r"\b(?:over|through|on|at)?\s*(?:the|her|his|its)?\s*(RIGHT|LEFT)\b", "", t)).strip(" ,")
                b["asimetrik"].append({"oge": "the " + oge if not oge.startswith(("the ", "a ")) else oge, "yan": "sag" if m.group(1) == "RIGHT" else "sol"})
    elif k["tur"] == "mekan":
        b["gorunen"] = [{"id": g.get("id") or g.get("oge"), "ad": g.get("ad") or g.get("tarif_en") or idg._ad(g.get("id") or g.get("oge")),
                         "ucte_bir": g.get("ucte_bir")} for g in k.get("gorunen") or [] if isinstance(g, dict)]
        b["notr"] = [{"oge": idg._ad(o), "durum": {"kapali": "closed", "acik": "open", "sonuk": "not burning", "yanik": "burning"}.get(d, d),
                      "secenek": ["burning", "not burning", "not visible"] if d in ("sonuk", "yanik") else ["open", "closed", "not visible"]}
                     for o, d in (k.get("notr_durum") or {}).items()]
    return b


def kor_gorev(kok, tur):
    import kor, istem_derle_gorsel as idg
    spec = _spec(kok); ev = idg.Evren(kok)
    birim = [{"anahtar": f"{k['kart_id']}_{a}", "gorsel": p, "baglam": baglam(kok, k, spec, ev)} for k, a, p in kart_adaylari(kok)]
    if not birim: return 2
    kor.paket_kur(kok, "kart", tur, birim, grup_sayisi=1 if len(birim) <= 12 else None)
    return 0


def _m(alan, seviye, kaynak, **ek): return dict({"alan": alan, "seviye": seviye, "kaynak": kaynak}, **{k: v for k, v in ek.items() if v is not None})


def yerel(yol, k, spec, kok=None):
    import olcum
    from olcum import teknik, kimlik, gorunum
    y = {"teknik": teknik.olc(yol), "olculemedi": {}}
    if k["tur"] != "mekan": y["fon_std"] = teknik.kenar_std(yol)
    yan = ortak.json_oku(os.path.splitext(yol)[0] + ".json", {}) or {}
    if yan.get("saglayici") == "sahte" or olcum.arka_sec(kok) == "sahte":
        g = yan.get("gercek") or {}
        y.update({a: g[a] for a in g}); y["arka"] = "sahte"
        for a in ("yuz_sayisi",):
            if a not in y: y["olculemedi"][a] = "sahte yan dosyada yok"
        return y
    try:
        ys = kimlik.yuzler(yol)
        y["yuz_sayisi"] = len(ys); y["vektorler"] = [f["vektor"] for f in ys]
        if len(ys) >= 2:
            y["oz_tutarlilik_min"] = round(min(kimlik.benzerlik(a, b) for a, b in itertools.combinations(y["vektorler"], 2)), 4)
    except kimlik.KimlikYok as e: y["olculemedi"]["yuz_sayisi"] = str(e)
    try: y["stil_clip_foto"] = round(gorunum.clip_foto(yol), 4)
    except Exception as e: y["olculemedi"]["stil_clip_foto"] = f"{e.__class__.__name__}"
    if k["tur"] == "mekan" and k.get("gorunen"):
        try:
            import istem_derle_gorsel as idg
            W = y["teknik"]["genislik"]; bul = gorunum.owl(yol, [g.get("ad") or idg._ad(g.get("id")) for g in k["gorunen"]])
            y["plaka_gorunen_yerel"] = {}
            for g in k["gorunen"]:
                ad = g.get("ad") or idg._ad(g.get("id")); d = next((b for b in bul if b["sorgu"] == ad), None)
                y["plaka_gorunen_yerel"][g.get("id")] = olcum.ucte_bir(d["kutu"][0] + d["kutu"][2] / 2, W) if d else None
        except Exception as e: y["olculemedi"]["plaka_gorunen"] = f"{e.__class__.__name__}"
    return y


def kadro_karari(a, b, sim, spec_a, spec_b):
    """İki karakterin kart benzerliği → madde (HATA/BAYRAK) ya da None. İ-12: serbest (hikâyeye bağlı olmayan) öğelerde fark yoksa ayrisma_kilitli."""
    import olcum
    if b in (spec_a.get("bilincli_benzerlik") or []) or a in (spec_b.get("bilincli_benzerlik") or []): return None
    if sim >= olcum.esik("kart_kadro_ayrisma_hata"):
        serbest = lambda s: {(o.get("oge") if isinstance(o, dict) else str(o)) for o in s.get("ayirt_edici") or []
                             if not (isinstance(o, dict) and o.get("hikaye_baglayici"))}
        sa, sb = serbest(spec_a), serbest(spec_b)
        bag = lambda s: {(o.get("oge")) for o in s.get("ayirt_edici") or [] if isinstance(o, dict) and o.get("hikaye_baglayici")}
        if not (sa ^ sb) and (bag(spec_a) ^ bag(spec_b)):
            return _m("ayrisma_kilitli", "HATA", "yerel", kisi=a, obur=b, olcu=round(sim, 4), sahip="hikaye-yazari",
                      neden="iki karakter yüzden ayrışmıyor ve fark yalnız hikâyeye bağlı öğelerde: görünüş değişikliği isteği senariste")
        return _m("kadro_benzer", "HATA", "yerel", kisi=a, obur=b, olcu=round(sim, 4), sahip="kart-tasarimcisi",
                  neden="kadro ayrışması < 0,363 sağlanamadı: serbest öğeleri (saç, kostüm rengi, siluet) ayrıştır")
    if sim >= olcum.esik("kart_kadro_ayrisma_hedef"):
        return _m("kadro_benzer", "BAYRAK", "yerel", kisi=a, obur=b, olcu=round(sim, 4))
    return None


def degerlendir(y, ks, cevap, k, spec):
    import olcum
    E = olcum.esik; out = []; oy = y.get("olculemedi") or {}; t = y["teknik"]
    s = spec.get(k["tur"], {}).get(k["id"]) or {}
    if t["uzun_kenar"] < E("kart_uzun_kenar_min"): out.append(_m("teknik", "HATA", "yerel", olcu=t["uzun_kenar"], esik=E("kart_uzun_kenar_min")))
    if ks is None: out.append(_m("kor_gozlem", "OLCULEMEDI", "kor", neden="kör gözlem cevabı yok")); ks = []
    if k["tur"] == "karakter" and s.get("tur") != "yaratik":
        bek = int(E("kart_gorunum_sayisi") or 6)
        if "yuz_sayisi" in oy: out.append(_m("yuz_sayisi", "OLCULEMEDI", "yerel", neden=oy["yuz_sayisi"]))
        elif y.get("yuz_sayisi") != bek: out.append(_m("yuz_sayisi", "HATA", "yerel", olcu=y.get("yuz_sayisi"), esik=bek))
        oz = y.get("oz_tutarlilik_min")
        if oz is None and "yuz_sayisi" not in oy: out.append(_m("oz_tutarlilik", "OLCULEMEDI", "yerel", neden="vektör yok"))
        elif oz is not None and oz < E("g1_kimlik_hata"): out.append(_m("oz_tutarlilik", "HATA", "yerel", olcu=oz, esik=E("g1_kimlik_hata")))
        elif oz is not None and oz < E("kart_oz_tutarlilik_gec"): out.append(_m("oz_tutarlilik", "BAYRAK", "yerel", olcu=oz))
    if k["tur"] == "karakter" and s.get("tur") == "yaratik" and len(s.get("kimlik_isaretleri") or []) < E("kart_yaratik_isaret_min"):
        out.append(_m("yaratik_isaret", "BAYRAK", "belge", olcu=len(s.get("kimlik_isaretleri") or []), esik=E("kart_yaratik_isaret_min")))
    if k["tur"] != "mekan" and y.get("fon_std") is not None and y["fon_std"] > E("kart_fon_std_max"):
        out.append(_m("fon", "BAYRAK", "yerel", olcu=y["fon_std"], esik=E("kart_fon_std_max")))
    kstil = str((cevap or {}).get("stil") or "").lower(); kor_cizim = bool(kstil) and "photo" not in kstil
    cf = y.get("stil_clip_foto"); yc = cf is not None and cf < E("g1_stil_clip_foto_min")
    if yc and kor_cizim: out.append(_m("stil", "HATA", "iki", olcu=cf, kor=kstil))
    elif yc or kor_cizim: out.append(_m("stil", "BAYRAK", "tek", olcu=cf, kor=kstil or None))
    for r in ks:
        a = r["alan"]
        if a == "ne_yok" and r["sonuc"] == "uyumsuz": out.append(_m("ne_yok", "HATA", "kor", kor=r["kor"]))
        elif a == "ogeler" and r["sonuc"] == "uyumsuz":
            bag = {o.get("oge") for o in s.get("ayirt_edici") or [] if isinstance(o, dict) and o.get("hikaye_baglayici")}
            out.append(_m("zorunlu_oge", "HATA", "kor", eksik=r.get("eksik"), hikaye_baglayici=bool(set(r.get("eksik") or []) & bag)))
        elif a.startswith("asimetrik") and r["sonuc"] == "uyumsuz": out.append(_m("asimetrik", "HATA", "kor", oge=a.split(":", 1)[1], kor=r["kor"]))
        elif a == "kisi_sayisi" and k["tur"] == "mekan" and r["sonuc"] == "uyumsuz": out.append(_m("plaka_kisi", "HATA", "kor", kor=r["kor"]))
        elif a.startswith("gorunen") and r["sonuc"] != "uyum":
            oge = a.split(":", 1)[1]; yg = y.get("plaka_gorunen_yerel")
            yerel_olcti = isinstance(yg, dict) and oge in yg
            yerel_ters = yerel_olcti and (yg[oge] is None or (r.get("beklenen") and yg[oge] != olcum.ucte_bir_normal(r["beklenen"])))
            sev = "HATA" if yerel_ters and r["sonuc"] == "uyumsuz" else "BAYRAK"
            out.append(_m("plaka_gorunen", sev, "iki" if sev == "HATA" else "kor", oge=oge, kor=r["kor"], beklenen=r["beklenen"],
                          yerel=yg.get(oge) if yerel_olcti else None))
        elif a.startswith("notr") and r["sonuc"] == "uyumsuz": out.append(_m("plaka_notr", "HATA", "kor", oge=a.split(":", 1)[1], kor=r["kor"]))
        elif a == "yazi_logo" and r["sonuc"] == "uyumsuz": out.append(_m("yazi_logo", "HATA" if str((cevap or {}).get("yazi_logo", "none")) != "none" else "BAYRAK", "kor"))
        elif a == "anatomi" and r["sonuc"] != "uyum": out.append(_m("anatomi", "HATA" if r["sonuc"] == "uyumsuz" and r["tutarli"] else "BAYRAK", "kor"))
        elif a == "gorunum_sayisi" and r["sonuc"] == "uyumsuz": out.append(_m("gorunum_sayisi", "BAYRAK", "kor", kor=r["kor"]))
        elif a == "olcek" and r["sonuc"] == "uyumsuz": out.append(_m("olcek_karti", "BAYRAK", "kor", kor=r["kor"]))
    if k["tur"] == "mekan" and y.get("yuz_sayisi"): out.append(_m("plaka_kisi", "HATA", "yerel", olcu=y["yuz_sayisi"]))
    return out


def _karar(al):
    s = "GEC"
    for a in al:
        v = "BAYRAK" if a["seviye"] == "OLCULEMEDI" else a["seviye"]
        if SIRA[v] > SIRA[s]: s = v
    return s


def denetle(kok, tur):
    import kor, olcum, istem_derle_gorsel as idg
    from olcum import kimlik
    po = _po()
    aday = kart_adaylari(kok)
    if not aday: print("!! kart adayı yok (_KARTLAR/adaylar/)", flush=True); return 2, None
    spec = _spec(kok); ev = idg.Evren(kok)
    an = kor.anahtar_oku(kok, "kart", tur); korc = {}
    for i, gor in (an.get("gruplar") or {}).items():
        cev = kor.cevaplari_oku(os.path.join(kok, "_KARTLAR", f"gozlem_t{tur}_{i}.json"))
        for g, v in gor.items(): korc[v["anahtar"]] = (v["sorular"], cev.get(g))
    adaylar = {}
    for k, a, p in aday:
        y = yerel(p, k, spec, kok)
        sor, cev = korc.get(f"{k['kart_id']}_{a}", (None, None))
        ks = kor.karsilastir(sor, cev, {}, {}) if sor is not None and cev is not None else None
        al = degerlendir(y, ks, cev, k, spec)
        adaylar.setdefault(k["kart_id"], []).append({"kart": k, "aday": a, "yol": p, "yerel": y, "kor": ks, "alanlar": al})
    # kadro ayrışması: her karakterin bu turdaki adaylarının ortalama vektörü + kilitli kadro bankaları
    kad = {}
    for kid_, ads in adaylar.items():
        for x in ads:
            if x["kart"]["tur"] == "karakter" and x["yerel"].get("vektorler"):
                kad.setdefault(x["kart"]["id"], []).append(x)
    sahte_kadro = {}
    for kid_, ads in adaylar.items():
        for x in ads:
            for o, s in ((x["yerel"].get("kadro_benzerlik") or {}).items()):
                sahte_kadro.setdefault(x["kart"]["id"], {})[o] = max(s, sahte_kadro.get(x["kart"]["id"], {}).get(o, 0))
    bankalar = {}
    for kid in (spec["karakter"] or {}):
        bp = ev.banka_yolu(kid)
        if bp and os.path.isfile(bp): bankalar.update(kimlik.banka_oku(bp))
    for kid, xs in kad.items():
        for x in xs:
            v = [sum(c) / len(c) for c in zip(*x["yerel"]["vektorler"])]
            for o, ys in kad.items():
                if o == kid: continue
                sim = max(kimlik.benzerlik(v, [sum(c) / len(c) for c in zip(*y["yerel"]["vektorler"])]) for y in ys)
                mm = kadro_karari(kid, o, sim, spec["karakter"].get(kid) or {}, spec["karakter"].get(o) or {})
                if mm: x["alanlar"].append(mm)
            for o, bv in bankalar.items():
                if o == kid or o.startswith("dinov2:") or o in kad: continue
                mm = kadro_karari(kid, o, kimlik.bankaya_benzerlik(v, bv), spec["karakter"].get(kid) or {}, spec["karakter"].get(o) or {})
                if mm: x["alanlar"].append(mm)
    for kid, d in sahte_kadro.items():
        for x in [x for ads in adaylar.values() for x in ads if x["kart"]["tur"] == "karakter" and x["kart"]["id"] == kid]:
            for o, sim in d.items():
                mm = kadro_karari(kid, o, sim, spec["karakter"].get(kid) or {}, spec["karakter"].get(o) or {})
                if mm: x["alanlar"].append(mm)
    olc, kartlar, duz, gorunus = [], {}, [], []
    for kart_id, xs in sorted(adaylar.items()):
        for x in xs: x["karar"] = _karar(x["alanlar"])
        xs.sort(key=lambda x: (SIRA[x["karar"]], sum(1 for a in x["alanlar"] if a["seviye"] != "HATA"), x["aday"]))
        en = xs[0]
        for a in en["alanlar"]:
            olc.append(po.m(a["alan"], a["seviye"], None, birim=kart_id, aday=en["aday"], kaynak=a["kaynak"], olcu=a.get("olcu"),
                            esik=a.get("esik"), kor=a.get("kor"), neden=a.get("neden"), kisi=a.get("kisi"), obur=a.get("obur")))
        kartlar[kart_id] = {"secilebilir": [x["aday"] for x in xs if x["karar"] in ("GEC", "BAYRAK")], "en_iyi": en["aday"],
                            "karar": en["karar"], "adaylar": [{"aday": x["aday"], "karar": x["karar"], "alanlar": x["alanlar"],
                                                               "gorsel": os.path.relpath(x["yol"], kok).replace(os.sep, "/"),
                                                               "yerel": {k: v for k, v in x["yerel"].items() if k != "vektorler"}} for x in xs]}
        if en["karar"] == "HATA":
            for a in en["alanlar"]:
                if a["seviye"] != "HATA": continue
                if a["alan"] == "ayrisma_kilitli": gorunus.append({"karakter": en["kart"]["id"], "obur": a.get("obur"), "neden": a.get("neden")})
                else: duz.append({"kart_id": kart_id, "alan": a["alan"], "aday": en["aday"], "sahip": a.get("sahip") or "kart-tasarimcisi",
                                  "cozum": "tarif_revizyonu" if a["alan"] in ("kadro_benzer", "zorunlu_oge") else "yeni_aday_correction"})
    yol, r = po.rapor_yaz(kok, "KART", "KAPISI", olc, asama="A10d", arac=SURUM, tur=tur, birimler=sorted(adaylar),
                          varsayilan="_RAPOR/KART_KAPISI.json", ek={"kartlar": kartlar})
    ortak.atomik_yaz(os.path.join(kok, "_KARTLAR", "KART_DUZELTME.json"), {"_surum": 1, "tur": tur, "maddeler": duz})
    if gorunus: ortak.atomik_yaz(os.path.join(kok, "_KARTLAR", "GORUNUS_DEGISIKLIK_ISTEGI.json"), {"_surum": 1, "istekler": gorunus})
    po.yaz_ozet(r, "KART")
    return 0, r


def main(argv):
    if argv and argv[0] in ("-h", "--help"): print(__doc__); return 4
    po = _po()
    kok = po.film_kok(po.arg_al(argv, "--film")); tur = po.tur_no(argv)
    try:
        if "--kor-gorev" in argv: return kor_gorev(kok, tur)
        return denetle(kok, tur)[0]
    except ortak.YolYok as e: print("!!", e); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
