"""KÖR — kör gözlem görevlerinin soruları, anonim paketi, cevap okuma, kişi eşleme ve beklenenle karşılaştırma (TASARIM §6.5, D-16, [GS2] §4.5.7).

Kullanım:
  python kor.py --paket --kip g1|kart|kapak --film <film> [--tur N]   (genellikle kare_denetim / gemini_al / kapak çağırır)
  python kor.py --denetle <_KOR_PAKET/<kip>_t<tur>> --film <film>       sızıntı denetimi (0 temiz · 1 sızıntı)
  Kodda: import kor
    kor.paket_kur(film, kip, tur, birimler, grup_sayisi=None) → {klasor, gruplar: {i: [gNN.jpg]}, anahtar}
        birim = {anahtar: "071_a", gorsel: <yol>, baglam: {...}}  (baglam: kip'e göre; bkz. sorular_g1 / sorular_kart / sorular_kapak)
    kor.cevaplari_oku(yol) → {gNN.jpg: cevap}       kor.kisi_esle(cevap, beklenen, yerel_ucte_bir) → ({p: id}, kaynak)
    kor.anatomik_el("sol", "3/4") → "sag"           kor.karsilastir(soru_anahtari, cevap, eslesme, yuz_acisi) → [alan sonucu]
    kor.sizinti(klasor, yasaklar) → [bulgu]
Paket düzeni: <film>/_KOR_PAKET/<kip>_t<tur>/<i>/{g01.jpg …, SORULAR.json}  (ajan görevinin GIRDI'si; film.py kopyalar)
              <film>/_KOR_PAKET/<kip>_t<tur>/ANAHTAR.json                   (gNN ↔ birim ve her sorunun beklenen anlamı; GIRDI'ye GİRMEZ)
Kurallar ([GS2] İ-4, §4.5.7):
  - Soru metninde ad, rol, kostüm tarifi, plan numarası, istem yoktur; görseller yeniden kodlanır (EXIF yok), adları gNN.jpg, sıra karışık.
  - Seçenekler beklenen değeri yanlış değerlerle birlikte içerir; sırası her görselde karışır. Kritik sorular (kişi sayısı, el–nesne,
    anatomi) ikinci kez karışık seçeneklerle sorulur (tekrar_of); iki cevap uyuşmazsa alan "belirsiz" (BAYRAK).
  - Sol/sağ her zaman GÖRÜNTÜ koordinatıdır. Kod çevirir: kameraya dönük ya da 3/4 kişide görüntünün solundaki el kişinin SAĞ elidir;
    sırtı dönükte SOL elidir; profilde ve görünmezde "belirsiz" (hakeme). Kişi eşleme yerel ölçümün üçte birleriyle; yerel yoksa
    beklenen kadraj konumuyla (eslesme_kaynagi: beklenen → uyuşmazlık yalnız BAYRAK).
  - Görev başına en çok kor_gorev_gorsel_max (12) görsel.
Çıkış kodları: 0 tamam · 1 sızıntı ya da girdi hatası · 4 kullanım.
"""
import os, sys, re, json, random, hashlib, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kor 1.0"
KIPLER = ("g1", "kart", "kapak")
SECIM_YOK = ["nothing, open hand", "not visible", "cannot tell"]
UCLER = ["left third", "middle", "right third", "not visible"]
EVET = ["yes", "no", "cannot tell"]
IFADE_SECENEK = ["neutral", "fear", "anger", "sadness", "tenderness", "surprise", "determination", "joy", "contempt", "unclear"]
ENVANTER = {"alanlar": ["kisiler", "nesneler", "isik_kaynaklari", "gun_saati", "hava", "yazi_logo", "anatomi", "stil"],
            "kisi_alanlari": ["p", "ucte_bir", "yuz_yonu", "poz", "yuz_gorunur", "el_goruntu_solu", "el_goruntu_sagi", "kiyafet", "sac"],
            "kural": "Left and right ALWAYS mean the IMAGE's left and right. Name people p1, p2 … from image-left to image-right. "
                     "If unsure, answer 'cannot tell'. stil: photograph | illustration | 3d render | painting | cartoon."}
ON_YUZ = ("on", "onden", "3/4", "uc_ceyrek", "kamera", "kameraya")
SIRT = ("sirt", "arka", "arkadan")
DECOY_NESNE = ["a cup", "a knife", "a book", "a rope"]
DECOY_OGE = ["a wooden table", "a window", "a wool scarf", "a leather belt", "a stone wall"]


def _rng(*parca): return random.Random(int(hashlib.sha1("|".join(map(str, parca)).encode()).hexdigest()[:12], 16))


def insanca(kimlik):
    """Kimlikten (fener_1) okunur İngilizce olmayan ama sızıntısız kısa ad: 'fener'. Evrende tarif varsa o kullanılır."""
    return re.sub(r"[_\d]+", " ", str(kimlik)).strip() or str(kimlik)


def anatomik_el(goruntu_tarafi, yuz_acisi):
    """Görüntünün sol/sağındaki el → kişinin kendi eli (sag | sol) ya da None (belirsiz)."""
    t = "sol" if str(goruntu_tarafi).lower() in ("sol", "left", "image-left") else "sag"
    a = str(yuz_acisi or "on").lower()
    if a in ON_YUZ: return "sag" if t == "sol" else "sol"
    if a in SIRT: return t
    return None


def goruntu_tarafi(el, yuz_acisi):
    """Kişinin kendi eli → görüntüdeki taraf ('sol' | 'sag') ya da None."""
    a = str(yuz_acisi or "on").lower()
    if a in ON_YUZ: return "sol" if el == "sag" else "sag"
    if a in SIRT: return el
    return None


# --- soru kurucular ----------------------------------------------------------------------------------------------
def _q(k, soru, secenek, alan, beklenen=None, kritik=False, kisi_basina=False, coklu=False, **ek):
    return {"k": k, "soru": soru, "secenek": list(secenek), "kisi_basina": kisi_basina, "coklu": coklu,
            "_alan": alan, "_beklenen": beklenen, "_kritik": kritik, **{"_" + a: v for a, v in ek.items()}}


def _kisi_sayisi(n):
    return "3 or more" if n >= 3 else str(n)


def sorular_g1(b):
    """b (baglam): {insanlar: [id], kisiler: [{id, yuz_acisi, konusur, dinleyen_kapali}], eller: {id: {sag: nesne|None, sol: …}},
    nesne_ad: {nesne: 'a lit lantern'}, gorunmesi_gerekenler: [{id, ad, ucte_bir?}], yasaklar: [metin], ne_yok: [kelime],
    ifade: {id: kor_degeri}, agiz_kapali: [id], acik_parmak: {id: {sag: n, sol: n}}, yakin_el: bool}"""
    qs = []; kisiler = b.get("kisiler") or []
    qs.append(_q("q_kisi", "How many people (any visible face or body, including the background) are in the image?",
                 ["0", "1", "2", "3 or more"], "kisi_sayisi", _kisi_sayisi(len(b.get("insanlar") or [])), kritik=True))
    nesneler = sorted({n for e in (b.get("eller") or {}).values() for n in (e or {}).values() if n})
    if nesneler:
        adlar = [(b.get("nesne_ad") or {}).get(n) or insanca(n) for n in nesneler]
        sec = adlar + [d for d in DECOY_NESNE if d not in adlar][:max(1, 3 - len(adlar))] + SECIM_YOK
        for taraf, ad in (("sol", "IMAGE-LEFT"), ("sag", "IMAGE-RIGHT")):
            qs.append(_q(f"q_el_{taraf}", f"For EACH person you listed, what does the hand on the {ad} side of that person hold?",
                         sec, "nesne_el", None, kritik=True, kisi_basina=True, taraf=taraf, nesne_ad=dict(zip(adlar, nesneler))))
    for i, g in enumerate(b.get("gorunmesi_gerekenler") or []):
        qs.append(_q(f"q_gor{i + 1}", f"Which part of the image shows {g.get('ad') or insanca(g['id'])}?", UCLER, "gorunen:" + g["id"],
                     g.get("ucte_bir")))
    for i, y in enumerate(b.get("yasaklar") or []):
        oge = re.sub(r"^\s*no\s+", "", str(y), flags=re.I).strip().rstrip(".")
        if not oge or re.search(r"\bother people\b|\bpeople\b|\bperson\b", oge, re.I): continue
        qs.append(_q(f"q_yasak{i + 1}", f"Is there any {oge} in the image?", EVET, "yasak_oge", "no", oge=oge))
    ne_yok = list(dict.fromkeys(b.get("ne_yok") or []))[:8]
    if ne_yok:
        qs.append(_q("q_neyok", "Do you see any of these anywhere in the image? Select all that apply.",
                     ne_yok + DECOY_OGE[:3] + ["none of these"], "ne_yok", [], coklu=True, ne_yok=ne_yok))
    if kisiler:
        qs.append(_q("q_ifade", "Which word best describes the facial expression of EACH person? (if the face is not visible: unclear)",
                     IFADE_SECENEK, "ifade", b.get("ifade") or {}, kisi_basina=True))
    if b.get("agiz_kapali"):
        qs.append(_q("q_agiz", "Is EACH person's mouth open or closed?", ["open", "closed", "not visible", "cannot tell"], "agiz", None,
                     kisi_basina=True, agiz_kapali=list(b["agiz_kapali"])))
    if b.get("acik_parmak") and b.get("yakin_el"):
        for taraf, ad in (("sol", "IMAGE-LEFT"), ("sag", "IMAGE-RIGHT")):
            qs.append(_q(f"q_parmak_{taraf}", f"How many fingers are extended on the hand on the {ad} side of EACH person?",
                         ["0", "1", "2", "3", "4", "5", "not visible", "cannot tell"], "acik_parmak", None, kisi_basina=True, taraf=taraf,
                         parmak=b["acik_parmak"]))
    qs.append(_q("q_yazi", "Is there any written text, letters, logo or watermark anywhere in the image?", EVET, "yazi_logo", "no"))
    qs.append(_q("q_anatomi", "Do you see any anatomical error (extra or fused fingers, extra limbs, a distorted face)?", EVET, "anatomi",
                 "no", kritik=True))
    return qs


def sorular_kart(b):
    """b: {tur: karakter|mekan|nesne, gorunum_sayisi, ogeler: [EN], yanlis_ogeler: [EN], asimetrik: [{oge, el|yan}], ne_yok: [kelime],
    gorunen: [{id, ad, ucte_bir}], notr: [{oge, durum: open|closed|burning|not burning}]}"""
    qs = []; tur = b.get("tur", "karakter")
    if tur == "karakter":
        n = b.get("gorunum_sayisi") or 6
        qs.append(_q("q_gorunum", "How many separate views of a person's FACE (full-body views with a visible face and face panels) are shown?",
                     [str(x) for x in range(max(0, n - 3), n + 3)] + ["cannot tell"], "gorunum_sayisi", str(n), kritik=True))
        og = list(dict.fromkeys(b.get("ogeler") or []))
        if og:
            yanlis = [x for x in dict.fromkeys(b.get("yanlis_ogeler") or []) if x not in og][:max(3, len(og))]
            qs.append(_q("q_oge", "Which of these are clearly visible on the person? Select all that apply.",
                         og + yanlis + ["none of these"], "ogeler", og, coklu=True, yanlis=yanlis))
        for i, a in enumerate(b.get("asimetrik") or []):
            qs.append(_q(f"q_asim{i + 1}", f"In the FRONT full-body view, on which side of the IMAGE is {a['oge']}?",
                         ["image-left side", "image-right side", "both sides", "not visible"], "asimetrik:" + a["oge"],
                         goruntu_tarafi(a["yan"], "on")))
    if tur == "mekan":
        qs.append(_q("q_kisi", "How many people (or faces, figures, statues) are in the image?", ["0", "1", "2", "3 or more"],
                     "kisi_sayisi", "0", kritik=True))
        for i, g in enumerate(b.get("gorunen") or []):
            qs.append(_q(f"q_gor{i + 1}", f"Which part of the image shows {g.get('ad') or insanca(g['id'])}?", UCLER,
                         "gorunen:" + g["id"], g.get("ucte_bir")))
        for i, s in enumerate(b.get("notr") or []):
            qs.append(_q(f"q_notr{i + 1}", f"What is the state of the {s['oge']}?", s.get("secenek") or ["open", "closed", "not visible"],
                         "notr:" + s["oge"], s["durum"]))
    if tur == "nesne":
        qs.append(_q("q_olcek", "Is there a hand or an everyday object next to the main object that shows its size?", EVET, "olcek", "yes"))
    ne_yok = list(dict.fromkeys(b.get("ne_yok") or []))[:8]
    if ne_yok:
        qs.append(_q("q_neyok", "Do you see any of these anywhere in the image? Select all that apply.",
                     ne_yok + DECOY_OGE[:3] + ["none of these"], "ne_yok", [], coklu=True, ne_yok=ne_yok))
    qs.append(_q("q_fon", "Is the background a plain, flat, light-grey backdrop?", EVET, "fon", "yes" if tur != "mekan" else None))
    qs.append(_q("q_yazi", "Is there any written text, letters, logo or watermark anywhere in the image?", EVET, "yazi_logo", "no"))
    qs.append(_q("q_anatomi", "Do you see any anatomical error (extra or fused fingers, extra limbs, a distorted face)?", EVET, "anatomi",
                 "no", kritik=True))
    return qs


def sorular_kapak(b):
    qs = [_q("q_birlikte", "Does the image show a human and a creature together in the same frame?", EVET, "kapak_kalip", "yes"),
          _q("q_yazi", "Is there any written text, letters, logo or watermark anywhere in the image?", EVET, "yazi_logo", "no"),
          _q("q_anatomi", "Do you see any anatomical error (extra or fused fingers, extra limbs, a distorted face)?", EVET, "anatomi", "no",
             kritik=True),
          _q("q_odak", "At a glance, what is the single clearest subject of the image?",
             ["a person's face", "a creature", "a person and a creature", "a landscape", "an object", "cannot tell"], "odak", None)]
    return qs


KURUCU = {"g1": sorular_g1, "kart": sorular_kart, "kapak": sorular_kapak}


def _ikile(qs, rng):
    out = []
    for q in qs:
        q = dict(q); sabit = [s for s in q["secenek"] if s in ("none of these",)]
        govde = [s for s in q["secenek"] if s not in sabit]; rng.shuffle(govde); q["secenek"] = govde + sabit
        out.append(q)
        if q["_kritik"]:
            t = dict(q, k=q["k"] + "b", tekrar_of=q["k"]); g2 = list(govde)
            for _ in range(5):
                rng.shuffle(g2)
                if g2 != govde or len(g2) < 2: break
            t["secenek"] = g2 + sabit; out.append(t)
    return out


def _acik(q): return {k: v for k, v in q.items() if not k.startswith("_")}


def _gizli(q): return {k[1:]: v for k, v in q.items() if k.startswith("_")} | {"tekrar_of": q.get("tekrar_of")}


# --- paket -------------------------------------------------------------------------------------------------------
def _gorsel_kopya(kaynak, hedef):
    from PIL import Image
    im = Image.open(kaynak); im.load(); im = im.convert("RGB")
    tmp = hedef + ".tmp.jpg"; im.save(tmp, "JPEG", quality=92); os.replace(tmp, hedef)


def paket_klasoru(film, kip, tur): return os.path.join(film, "_KOR_PAKET", f"{kip}_t{int(tur)}")


def paket_kur(film, kip, tur, birimler, grup_sayisi=None):
    """Birimleri ≤ kor_gorev_gorsel_max'lık gruplara böler, anonim paketleri yazar. Eski paket _KOR_PAKET/_ESKI/'ye taşınır."""
    import olcum
    if kip not in KIPLER: raise ValueError(f"kip {kip!r} ({'|'.join(KIPLER)})")
    mx = int(olcum.esik("kor_gorev_gorsel_max") or 12)
    kl = paket_klasoru(film, kip, tur)
    if os.path.isdir(kl):
        eski = os.path.join(film, "_KOR_PAKET", "_ESKI"); os.makedirs(eski, exist_ok=True)
        n = 1
        while os.path.exists(os.path.join(eski, f"{os.path.basename(kl)}_{n}")): n += 1
        shutil.move(kl, os.path.join(eski, f"{os.path.basename(kl)}_{n}"))
    rng = _rng(kip, tur, len(birimler))
    sira = list(birimler); rng.shuffle(sira)
    gs = max(1, grup_sayisi or -(-len(sira) // mx))
    while -(-len(sira) // gs) > mx: gs += 1
    gruplar = {i + 1: sira[i::gs] for i in range(gs)}
    anahtar = {"_surum": 1, "kip": kip, "tur": int(tur), "arac_surum": SURUM, "gruplar": {}}
    for i, bs in gruplar.items():
        gd = os.path.join(kl, str(i)); os.makedirs(gd, exist_ok=True)
        sor = {"_surum": 1, "is_id": f"{kip.upper()}_t{tur}_{i:02d}", "kip": kip, "envanter": ENVANTER, "gorseller": [], "hedefli": {}}
        anahtar["gruplar"][str(i)] = {}
        for j, b in enumerate(bs):
            ad = f"g{j + 1:02d}.jpg"
            _gorsel_kopya(b["gorsel"], os.path.join(gd, ad))
            qs = _ikile(KURUCU[kip](b.get("baglam") or {}), _rng(kip, tur, b["anahtar"]))
            sor["gorseller"].append(ad); sor["hedefli"][ad] = [_acik(q) for q in qs]
            anahtar["gruplar"][str(i)][ad] = {"anahtar": b["anahtar"], "gorsel": os.path.relpath(b["gorsel"], film).replace(os.sep, "/"),
                                              "sorular": {q["k"]: _gizli(q) for q in qs}}
        if not bs: sor["not"] = "Bu görevde görsel yok; CIKTI/rapor.json'a {\"cevaplar\": []} yaz."
        sor["cikti"] = ("CIKTI/rapor.json: {\"cevaplar\": [<her görsel için {gorsel, kisiler, nesneler, isik_kaynaklari, gun_saati, hava, "
                        "yazi_logo, anatomi, stil, cevaplar: {q_k: cevap | {p1: cevap}}, belirsiz: []}>]}. Son satır: OZET | gorsel: <n> | "
                        "belirsiz_alan: <n>")
        ortak.atomik_yaz(os.path.join(gd, "SORULAR.json"), sor)
    ortak.atomik_yaz(os.path.join(kl, "ANAHTAR.json"), anahtar)
    return {"klasor": kl, "gruplar": {i: [f"g{j + 1:02d}.jpg" for j in range(len(bs))] for i, bs in gruplar.items()}, "anahtar": anahtar}


def anahtar_oku(film, kip, tur): return ortak.json_oku(os.path.join(paket_klasoru(film, kip, tur), "ANAHTAR.json"), {}) or {}


# --- cevaplar ----------------------------------------------------------------------------------------------------
def cevaplari_oku(yol):
    """rapor.json (ya da CEVAP_gNN.json) → {gNN.jpg: cevap}. Kabul: {"cevaplar": [..]}, [..], {"g01.jpg": {...}}."""
    j = ortak.json_oku(yol) if isinstance(yol, str) else yol
    if isinstance(j, dict) and isinstance(j.get("cevaplar"), list): j = j["cevaplar"]
    elif isinstance(j, dict) and isinstance(j.get("gorseller"), list) and j["gorseller"] and isinstance(j["gorseller"][0], dict):
        j = j["gorseller"]
    if isinstance(j, list): return {c.get("gorsel"): c for c in j if isinstance(c, dict) and c.get("gorsel")}
    if isinstance(j, dict): return {k: v for k, v in j.items() if re.fullmatch(r"g\d+\.jpg", str(k)) and isinstance(v, dict)}
    return {}


def kisi_esle(cevap, beklenen, yerel_ucte_bir=None, beklenen_ucte_bir=None):
    """Kör kişileri (p1…) karakterlere eşler. beklenen: [id]. Dönüş ({p: id}, kaynak: yerel | beklenen | tek | yok)."""
    import olcum
    from olcum import kimlik
    kis = [k for k in (cevap.get("kisiler") or []) if isinstance(k, dict) and k.get("p")]
    if not kis or not beklenen: return {}, "yok"
    if len(kis) == 1 and len(beklenen) == 1: return {kis[0]["p"]: beklenen[0]}, "tek"
    kaynak, konum = "yerel", dict(yerel_ucte_bir or {})
    if not all(b in konum for b in beklenen):
        kaynak = "beklenen"; konum.update({b: v for b, v in (beklenen_ucte_bir or {}).items() if b not in konum})
    sira = {"sol": 0, "orta": 1, "sag": 2}
    m = [[abs(sira.get(olcum.ucte_bir_normal(k.get("ucte_bir")), 1) - sira.get(olcum.ucte_bir_normal(konum.get(b)), 1)) + 0.01 * abs(i - j)
          for j, b in enumerate(beklenen)] for i, k in enumerate(kis)]
    return {kis[r]["p"]: beklenen[c] for r, c in kimlik.macar(m)}, kaynak


def _norm(x): return re.sub(r"\s+", " ", str(x).strip().lower()) if x is not None else None


def _kisi_cevap(c, k, p):
    v = (c.get("cevaplar") or {}).get(k)
    if isinstance(v, dict): return v.get(p)
    return v


def karsilastir(sorular, cevap, eslesme=None, yuz_acisi=None, beklenen_eller=None):
    """Bir görselin soru anahtarı (ANAHTAR.json → sorular) ile kör cevabını alan alan karşılaştırır.
    Dönüş: [{alan, kisi?, beklenen, kor, tutarli, sonuc: uyum | uyumsuz | belirsiz, k}]. eslesme {p: id}; yuz_acisi {id: …};
    beklenen_eller {id: {sag: nesne|None, sol: nesne|None}}."""
    eslesme = eslesme or {}; yuz_acisi = yuz_acisi or {}; out = []
    ters = {v: k for k, v in eslesme.items()}
    cv = cevap.get("cevaplar") or {}
    tekrar = {q["tekrar_of"]: k for k, q in sorular.items() if q.get("tekrar_of")}

    def ikili(k, p=None):
        a = _kisi_cevap(cevap, k, p) if p else cv.get(k)
        kb = tekrar.get(k)
        if kb is None: return a, True
        b = _kisi_cevap(cevap, kb, p) if p else cv.get(kb)
        if isinstance(a, list) or isinstance(b, list): return a, sorted(map(_norm, a or [])) == sorted(map(_norm, b or []))
        return a, _norm(a) == _norm(b)

    el_kor = {}
    for k, q in sorular.items():
        if q.get("tekrar_of"): continue
        alan = q["alan"]
        if q.get("kisi_basina"):
            for p, kid in eslesme.items():
                a, tut = ikili(k, p)
                if alan == "nesne_el":
                    el_kor.setdefault(kid, {})[q.get("taraf")] = (a, tut, q.get("nesne_ad") or {})
                    continue
                bek = q.get("beklenen")
                if isinstance(bek, dict): bek = bek.get(kid)
                if alan == "agiz": bek = "closed" if kid in (q.get("agiz_kapali") or []) else None
                if alan == "acik_parmak":
                    kendi = anatomik_el(q.get("taraf"), yuz_acisi.get(kid))
                    bek = ((q.get("parmak") or {}).get(kid) or {}).get(kendi) if kendi else None
                    bek = None if bek is None else str(bek)
                if bek is None: continue
                out.append(_sonuc(alan, bek, a, tut, kisi=kid, k=k))
            continue
        a, tut = ikili(k)
        bek = q.get("beklenen")
        if alan == "ne_yok":
            sec = [x for x in (a or []) if isinstance(a, list)] if isinstance(a, list) else ([a] if a else [])
            gor = [x for x in sec if _norm(x) in {_norm(n) for n in q.get("ne_yok") or []}]
            out.append({"alan": "ne_yok", "beklenen": [], "kor": gor, "tutarli": tut, "k": k,
                        "sonuc": "belirsiz" if a is None else ("uyumsuz" if gor else "uyum")}); continue
        if alan == "ogeler":
            sec = {_norm(x) for x in (a if isinstance(a, list) else [a] if a else [])}
            eksik = [x for x in bek or [] if _norm(x) not in sec]; yanlis = [x for x in q.get("yanlis") or [] if _norm(x) in sec]
            out.append({"alan": "ogeler", "beklenen": bek, "kor": sorted(sec - {None}), "eksik": eksik, "fazla": yanlis, "tutarli": tut,
                        "k": k, "sonuc": "belirsiz" if a is None else ("uyumsuz" if eksik else "uyum")}); continue
        if bek is None and alan not in ("yazi_logo",): continue
        out.append(_sonuc(alan, bek, a, tut, k=k))
    for kid, eller in (beklenen_eller or {}).items():
        p = ters.get(kid)
        for el_kendi, nesne in eller.items():
            if not nesne: continue
            taraf = goruntu_tarafi(el_kendi, yuz_acisi.get(kid))
            if p is None or not el_kor.get(kid):
                out.append({"alan": "nesne_el", "kisi": kid, "nesne": nesne, "beklenen": el_kendi, "kor": None, "tutarli": None,
                            "sonuc": "belirsiz", "neden": "kişi eşlenemedi" if p is None else "soru yok"}); continue
            if taraf is None:
                out.append({"alan": "nesne_el", "kisi": kid, "nesne": nesne, "beklenen": el_kendi, "kor": None, "tutarli": None,
                            "sonuc": "belirsiz", "neden": f"yüz açısı {yuz_acisi.get(kid)!r}: sol/sağ çevrilemez (hakem)"}); continue
            bulunan, tutarli = None, True
            for tr, (a, tut, ad_map) in el_kor[kid].items():
                tutarli = tutarli and tut
                if ad_map.get(a) == nesne: bulunan = anatomik_el(tr, yuz_acisi.get(kid))
            sonuc = "belirsiz" if not tutarli else ("uyum" if bulunan == el_kendi else "uyumsuz")
            out.append({"alan": "nesne_el", "kisi": kid, "nesne": nesne, "beklenen": el_kendi, "kor": bulunan, "tutarli": tutarli,
                        "sonuc": sonuc})
    return out


def _sonuc(alan, bek, a, tut, **ek):
    if a is None or _norm(a) in ("cannot tell", "unclear", "not visible") and alan not in ("gorunen",) and not alan.startswith("gorunen"):
        s = "belirsiz"
    elif not tut: s = "belirsiz"
    elif alan.startswith("gorunen") and bek is None: s = "uyumsuz" if _norm(a) == "not visible" else "uyum"
    elif alan.startswith("gorunen"):
        import olcum
        s = "uyum" if olcum.ucte_bir_normal(a) == olcum.ucte_bir_normal(bek) else "uyumsuz"
    elif alan.startswith("asimetrik"):
        s = "uyum" if bek and _norm(a).startswith(("image-left" if bek == "sol" else "image-right")) else "uyumsuz"
    else: s = "uyum" if _norm(a) == _norm(bek) else "uyumsuz"
    return dict({"alan": alan, "beklenen": bek, "kor": a, "tutarli": tut, "sonuc": s}, **ek)


# --- sızıntı -----------------------------------------------------------------------------------------------------
def sizinti(klasor, yasaklar):
    """Paket klasörlerinde (ANAHTAR.json hariç) yasak kelime (karakter adı, plan numarası, istem parçası) ya da anonim olmayan dosya adı."""
    bul = []; ys = [y for y in (yasaklar or []) if y and len(str(y)) >= 3]
    for kok, _, dosyalar in os.walk(klasor):
        for d in dosyalar:
            if d == "ANAHTAR.json": continue
            p = os.path.join(kok, d)
            if d.lower().endswith(".jpg") and not re.fullmatch(r"g\d{2,}\.jpg", d): bul.append({"dosya": d, "neden": "anonim olmayan ad"})
            if d.endswith(".json"):
                t = open(p, encoding="utf-8").read().lower()
                for y in ys:
                    if re.search(r"\b" + re.escape(str(y).lower()) + r"\b", t): bul.append({"dosya": d, "neden": f"yasak kelime: {y}"})
    return bul


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 4
    import plan_ortak as po
    if "--denetle" in argv:
        kl = po.arg_al(argv, "--denetle"); film = po.film_kok(po.arg_al(argv, "--film"))
        s = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
        yas = list((s.get("karakterler") or {}).keys())
        h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
        yas += [k.get("ad") for k in (h.get("karakterler") or {}).values() if isinstance(k, dict)]
        b = sizinti(kl, yas)
        print(json.dumps({"sizinti": b}, ensure_ascii=False, indent=1)); return 1 if b else 0
    if "--paket" in argv:
        kip = po.arg_al(argv, "--kip"); film = po.film_kok(po.arg_al(argv, "--film")); tur = po.tur_no(argv)
        if kip == "g1":
            import kare_denetim
            return kare_denetim.kor_gorev(film, tur)
        if kip == "kart":
            import kart_denetim
            return kart_denetim.kor_gorev(film, tur)
        if kip == "kapak":
            import kapak
            return kapak.kor_paketi(film, tur)
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
