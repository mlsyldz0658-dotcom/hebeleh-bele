"""İSTEM DERLE · GÖRSEL — başlangıç karesi, kart ve kapak istemleri durumdan derlenir (TASARIM §6.5, D-15, D-16; [GS2] GS3, GS6; A10d, A11).

Kullanım (istem_derle.py --gorsel/--kart/--kapak bu modüle devreder; tek başına da çalışır):
  python istem_derle_gorsel.py --gorsel --film <film> [--plan <no>[,<no>…]] [--kuru]
      SAHNELER.json → her planın gorsel_istem, gorsel_istem_yedek, uretim.gorsel.{basamak, referanslar}, _derlenir.gorsel_istem_ozeti;
      ayrıca YAYIN/KAPAK_SPEC.json (kapak istemleri, --kapak ile aynı) ve _RAPOR/ISTEM_DERLEME_GORSEL.txt
  python istem_derle_gorsel.py --kart --film <film>     _KARTLAR/KART_SPEC.json → _KARTLAR/KART_ISTEMLERI.json (kart başına 3 aday)
  python istem_derle_gorsel.py --kapak --film <film>    HIKAYE.json + evren → YAYIN/KAPAK_SPEC.json (8–12 aday; insan + yaratık aynı karede)
  Kodda: import istem_derle_gorsel as idg
    idg.derle_gorsel(kok, nolar=None, kuru=False) → (kod, rapor) · idg.derle_kart(kok) · idg.derle_kapak(kok)
    idg.Evren(kok)  evrendeki karakter/mekân/nesne kayıtları (salt okuma; yazma yalnız evren.py)
    idg.basamak(plan, agac=None) → 1 | 2 | 3 · idg.referanslar(plan, E) → ["kart:mara/k1@4", "plaka:kulube/ic_genel@1"]
İstem sırası (BK§4.1.1, 01§B3, [GS2] GS6): [kadraj + açı + lens] + [her karakter: Ad — kimlik_en (aynen) + kostüm + kadraj üçte biri +
  yüz yönü + poz + iki elin ayrı ayrı hâli] + [ifade] + [nesneler] + [mekân + plakanın gördükleri] + [ışık: tek ana kaynak, yönü, gün
  saati] + [yasaklar] + ["mouth closed"] + [stil eki] + [CORRECTION cümleleri (_derlenir.duzeltmeler; alan başına tek)].
Kurallar: anlık görüntü (süren eylem fiili yok); çıplak left/right yok ("Mara's RIGHT hand", "frame left"); kimlik dizesi kelimesi
  kelimesine; filtre/yaş kelimesi HATA (istem_derle.yasak_bul); referans ≤ RE referans_max (2) kart + ebeveyn; elle istem
  (zanaat.istem_elle) derlenmez. Girdi imzası kilitli kart sürümlerini içerir (İ-5): kart sürümü değişince imza değişir.
Basamak (GS7): 1 = baslangic kart | ana_kare (sahne başları, kurulum ana kareleri) · 2 = turev, kurulum_donusu, araya_kesme, zaman_atlama ·
  3 = son_kare (Z1 planlanmış görseli) ve Z2 bitiş görseli. KAMERA_AGACI.json'daki düğüm basamağı yalnız sıralama içindir.
Çıkış kodları: 0 tamam (BAYRAK olabilir) · 1 HATA (yasak kelime, kimlik dizesi yok) · 2 girdi yok · 4 kullanım.
"""
import os, sys, re, json, glob, hashlib
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "istem_derle_gorsel 1.0"
KADRAJ_EN = {"UG": "extreme wide shot", "EG": "extreme wide shot", "G": "wide shot", "GEN": "wide shot", "B": "full shot",
             "DB": "medium full shot", "OG": "medium wide shot", "O": "medium shot", "OY": "medium close-up", "Y": "close-up",
             "CY": "extreme close-up", "D": "detail insert shot", "OU": "over-the-shoulder shot"}
ACI_EN = {"goz_hizasi": "eye-level", "alt": "low angle", "alt_aci": "low angle", "ust": "high angle", "ust_aci": "high angle",
          "kus_bakisi": "overhead view", "omuz": "shoulder height"}
UC_EN = {"sol": "in the frame left third", "orta": "in the middle of the frame", "sag": "in the frame right third"}
BAKIS_EN = {"kadraj_soluna": "faces toward frame left", "kadraj_sagina": "faces toward frame right", "kameraya": "faces the camera",
            "kamera": "faces the camera", "asagi": "looks down", "yukari": "looks up"}
POZ_EN = {"ayakta": "standing", "oturur": "seated", "oturuyor": "seated", "diz_coker": "kneeling", "diz_cokmus": "kneeling",
          "egilir": "leaning forward", "egik": "leaning forward", "yatar": "lying down", "comelir": "crouching", "comelmis": "crouching"}
DURUM_EN = {"kapali": "closed", "acik": "open", "sonuk": "out, not burning", "yanik": "burning", "yanar": "burning", "kirik": "broken",
            "bos": "empty", "dolu": "full"}
EL_SEKLI_EN = {"kiskac": "fingers pinched around it", "yumruk": "a closed fist", "acik": "open, fingers relaxed", "gevsek": "relaxed",
               "kavrar": "gripping it"}
SAHTE_SERI_YOK = "seri yok"
BASAMAK = {"kart": 1, "ana_kare": 1, "turev": 2, "kurulum_donusu": 2, "araya_kesme": 2, "zaman_atlama": 2, "son_kare": 3}
GERCEKCILIK_INSAN = "real costume test photo on ARRI Alexa"
GERCEKCILIK_YARATIK = "real animal photography, nature documentary, Weta Workshop practical creature, NOT cartoon, NOT Pixar, NOT plush"
KAPAK_VARYANT = [
    ("medium close-up, the human in the frame left third and the creature in the frame right third, both facing the camera", "warm firelight from frame left"),
    ("close-up two-shot, faces close together, the creature nearer the camera", "cold moonlight from frame right"),
    ("low angle medium shot, the human standing protectively in front of the creature", "golden backlight rim"),
    ("wide shot, small human figure and the creature against the location, strong silhouette", "dramatic dusk sky"),
    ("over-the-shoulder shot from behind the creature toward the human's face", "lantern glow from frame left"),
    ("extreme close-up of the human's eyes with the creature's eye reflected", "single hard key light"),
    ("medium shot, the human kneeling, the creature at eye level beside the human", "soft window light from frame right"),
    ("high angle medium shot, both looking up toward the camera", "warm hearth glow"),
    ("medium close-up, the creature on the human's shoulder", "storm light from frame left"),
    ("wide shot, the human and the creature walking toward the camera, the location behind them", "misty morning light"),
]


def _imza(x): return hashlib.sha1(json.dumps(x, ensure_ascii=False, sort_keys=True, default=str).encode()).hexdigest()[:8]


def _yasak(metin):
    import istem_derle
    return istem_derle.yasak_bul(metin)


OGE_EN = {"kapi": "door", "ocak": "hearth", "ocak_atesi": "hearth fire", "ates": "fire", "pencere": "window", "pencere_kepenk": "window shutters",
          "kepenk": "shutters", "mum": "candle", "lamba": "lamp", "fener": "lantern", "masa": "table", "sandalye": "chair", "sandik": "wooden trunk",
          "yatak_ortusu": "blanket", "perde": "curtain", "kapi_esigi": "doorway", "merdiven": "stairs", "duvar": "wall", "zemin": "floor"}


def _ad(x): return OGE_EN.get(str(x), re.sub(r"[_]+", " ", str(x)).strip())


# --- evren (salt okuma) ------------------------------------------------------------------------------------------
class Evren:
    def __init__(self, kok):
        self.kok = kok
        try:
            import evren
            self.seri = evren.film_serisi(kok)
            self.yol = evren.seri_yolu(self.seri) if self.seri else None
        except Exception: self.seri, self.yol = None, None
        self._c = {}

    def _j(self, *p):
        if not self.yol: return {}
        k = os.path.join(self.yol, *p)
        if k not in self._c: self._c[k] = ortak.json_oku(k, {}) or {}
        return self._c[k]

    def karakter(self, kid): return self._j("karakterler", kid, "karakter.json")
    def mekan(self, mid): return self._j("mekanlar", mid, "mekan.json")
    def nesne(self, nid): return self._j("nesneler", nid, "nesne.json")
    def dunya(self): return self._j("dunya.json")
    def kalibrasyon(self): return self._j("KALIBRASYON.json")

    def dosya(self, *p): return os.path.join(self.yol, *p) if self.yol else None

    def kart_yolu(self, kid, kostum=None):
        k = self.karakter(kid); ko = (k.get("kostumler") or {}).get(kostum or k.get("varsayilan_kostum") or "") or {}
        ad = ko.get("kart") or (k.get("kartlar") or {}).get("sayfa")
        return self.dosya("karakterler", kid, ad) if ad else None

    def banka_yolu(self, kid):
        b = (self.karakter(kid).get("olcum") or {}).get("banka")
        return self.dosya("karakterler", kid, b) if b else None

    def nesne_en(self, nid):
        n = self.nesne(nid)
        return n.get("bulucu_sorgu") or n.get("tarif_en") or _ad(nid)

    def plaka_yolu(self, mid, pid):
        p = ((self.mekan(mid).get("plakalar") or {}).get(pid) or {}).get("gorsel")
        return self.dosya("mekanlar", mid, p) if p else None


def ifade_en(deger):
    import plan_ortak as po
    d = (po.sozluk("ifade").get("degerler") or {}).get(deger) or {}
    return d.get("en"), d.get("kor")


# --- plan bağlamı -----------------------------------------------------------------------------------------------
def defter_durumu(kok, no, an="bas"):
    D = ortak.json_oku(os.path.join(kok, "DUNYA_DEFTERI.json"), {}) or {}
    p = (D.get("dondurulmus") or {}).get(str(no)) or (D.get("planlar") or {}).get(str(no)) or {}
    return ((p.get("durum") or {}).get(an)) or {}


def basamak(plan, agac=None):
    bas = ((plan.get("zanaat") or {}).get("zincir") or {}).get("baslangic") or "ana_kare"
    if ((plan.get("zanaat") or {}).get("zincir") or {}).get("bitis_sabitle") and bas == "son_kare": return 3
    return BASAMAK.get(bas, 1)


def referanslar(plan, E, ev=None):
    import olcum
    z = plan.get("zanaat") or {}; zn = z.get("zincir") or {}
    kad = [k for k in z.get("kadrajdakiler") or [] if isinstance(k, dict) and k.get("id")]
    kad.sort(key=lambda k: (not k.get("kimlik_demiri"), not k.get("konusur")))
    mx = int(olcum.esik("referans_max") or 2); out = []
    for k in kad[:mx]:
        c = ev.karakter(k["id"]) if ev else {}
        kost = k.get("kostum") or c.get("varsayilan_kostum") or "k1"
        out.append(f"kart:{k['id']}/{kost}@{c.get('surum') or 0}")
    e = str(zn.get("ebeveyn") or "")
    bas = zn.get("baslangic") or "ana_kare"
    if bas == "son_kare" and zn.get("onceki_plan") is not None: out.append(f"plan:{zn['onceki_plan']}")
    elif e.startswith("plaka:"): out.append(e if "/" in e else f"plaka:{plan.get('_mekan') or ''}/{e.split(':', 1)[1]}")
    elif e: out.append(f"ana_kare:{e.split('@')[0]}")
    elif (z.get("kamera") or {}).get("kurulum"): out.append(f"ana_kare:{z['kamera']['kurulum']}")
    return out


def _el_cumlesi(ad, el, d, ev):
    d = d or {}; EL = "RIGHT" if el == "sag" else "LEFT"
    if d.get("tutar"):
        s = f"{ad}'s {EL} hand holds {_belirli(ev.nesne_en(d['tutar']))}"
        if d.get("sekil") in EL_SEKLI_EN: s += f", {EL_SEKLI_EN[d['sekil']]}"
        if d.get("yer"): s += f", at {_ad(d['yer'])} height" if d["yer"] in ("kalca", "bel", "gogus", "omuz") else ""
        return s
    if d.get("yer"): return f"{ad}'s {EL} hand rests on the {_ad(d['yer'])}"
    return f"{ad}'s {EL} hand is empty, fingers relaxed"


def _belirli(t):
    t = str(t).strip()
    return t if re.match(r"^(a|an|the)\s", t, re.I) else "the " + t


def plan_istemi(kok, plan, S, ev, yedek=False):
    """(istem, notlar, yasaklar_bulgu). Durum defterinden ve kartlardan anlık görüntü istemi."""
    z = plan.get("zanaat") or {}; der = plan.get("_derlenir") or {}
    sg = (S.get("sahne_gruplari") or {}).get(z.get("sahne_grubu")) or {}
    dur = defter_durumu(kok, plan.get("no")) or {}
    kam = z.get("kamera") or {}; notlar = []
    p = [f"Photorealistic film still, {KADRAJ_EN.get(kam.get('kadraj'), 'medium shot')}, {ACI_EN.get(kam.get('aci'), 'eye-level')}"
         + (f", {kam['lens_mm']}mm lens" if kam.get("lens_mm") else "") + "."]
    hik = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    for k in z.get("kadrajdakiler") or []:
        if not isinstance(k, dict) or not k.get("id"): continue
        kid = k["id"]; c = ev.karakter(kid); kd = (dur.get("karakterler") or {}).get(kid) or {}
        ad = c.get("ad") or ((hik.get("karakterler") or {}).get(kid) or {}).get("ad") or kid.title()
        kim = c.get("kimlik_en")
        if not kim: notlar.append(("HATA", "kimlik_dizesi_yok", kid)); kim = "as in the character reference"
        kost = kd.get("kostum") or c.get("varsayilan_kostum")
        kt = ((c.get("kostumler") or {}).get(kost) or {})
        ktarif = kt.get("tarif_en") or ""
        if kt.get("turetildigi"): ktarif = (((c.get("kostumler") or {}).get(kt["turetildigi"]) or {}).get("tarif_en") or "") + ", " + (kt.get("fark_en") or "")
        s = f"{ad} — {kim}" + (f", wearing {ktarif.strip(', ')}" if ktarif.strip(", ") and not yedek else "")
        import olcum
        u = olcum.ucte_bir_normal((der.get("kadraj_konumu") or {}).get(kid))
        if u: s += f", {UC_EN[u]}"
        b = BAKIS_EN.get((der.get("bakis_kadrajda") or {}).get(kid))
        if b: s += f", {b}"
        poz = POZ_EN.get(kd.get("poz"))
        if poz: s += f", {poz}"
        p.append(s + ".")
        if k.get("yuz_acisi") != "gorunmez" or kd.get("eller"):
            eller = kd.get("eller") or {}
            for el in ("sag", "sol"):
                if k.get("olcek") == "el" and not (eller.get(el) or {}).get("tutar") and not (eller.get(el) or {}).get("yer"): continue
                p.append(_el_cumlesi(ad, el, eller.get(el), ev) + ".")
        ie = ((z.get("oyunculuk") or {}).get(kid) or {}).get("dis_ifade") or {}
        en, _ = ifade_en(ie.get("bas") or kd.get("ifade"))
        if en and not yedek: p.append(f"{ad} has {en}.")
        dk = der.get("dinleyen_agiz")
        if k.get("konusur") or dk == "kapali" or (isinstance(dk, dict) and dk.get(kid) == "kapali"):
            p.append(f"{ad}'s mouth is closed, lips together.")
    tutulan = {d.get("tutar") for kd in (dur.get("karakterler") or {}).values() for d in ((kd or {}).get("eller") or {}).values() if d}
    for nid, nv in (dur.get("nesneler") or {}).items():
        if nid in tutulan or not isinstance(nv, dict) or not nv.get("nerede"): continue
        p.append(f"{_belirli(ev.nesne_en(nid)).capitalize()} lies on the {_ad(nv['nerede'])}"
                 + (f", {DURUM_EN.get(nv.get('durum'), _ad(nv.get('durum')))}" if nv.get("durum") else "") + ".")
    m = ev.mekan(sg.get("mekan")) if sg.get("mekan") else {}
    if m.get("tarif_en"): p.append(f"Location: {m['tarif_en']}.")
    for oge, durum in (dur.get("mekan_durumu") or {}).items():
        if isinstance(durum, str): p.append(f"The {_ad(oge)} is {DURUM_EN.get(durum, _ad(durum))}.")
    isik = sg.get("isik") or {}; zaman = sg.get("zaman") or {}
    import kroki
    yon = {"soldan": "frame left", "sagdan": "frame right"}.get(kroki.isik_yonu(der.get("isik_kadrajda")))
    if isik.get("ana"):
        p.append(f"The only main light is the {_ad(isik['ana'])}" + (f" from {yon}" if yon else "")
                 + {"gece": ", at night", "gunduz": ", in daylight", "aksam": ", at dusk", "sabah": ", in the early morning"}.get(zaman.get("gun_saati"), "")
                 + ".")
    yas = [y for y in list(sg.get("yasaklar") or []) + list(z.get("yasaklar") or []) if isinstance(y, str)]
    if not any("other people" in y.lower() for y in yas): yas.insert(0, "no other people")
    p.append(". ".join(y[:1].upper() + y[1:] for y in yas) + ".")
    stil = (ev.dunya() or {}).get("stil_eki")
    if stil and not yedek: p.append(stil.rstrip(".") + ".")
    taban = " ".join(x.strip() for x in p if x.strip())
    if yedek: return taban, notlar, _yasak(taban)
    import duzeltme
    ist = duzeltme.istem_kur(taban, der.get("duzeltmeler") or {})
    return ist, notlar, _yasak(ist)


def derle_gorsel(kok, nolar=None, kuru=False):
    import plan_ortak as po
    sp = os.path.join(kok, "SAHNELER.json"); S = ortak.json_oku(sp)
    if not isinstance(S, dict): print("!! SAHNELER.json yok", flush=True); return 2, None
    E = po.esik(); ev = Evren(kok); olc, satir = [], []
    agac = ortak.json_oku(os.path.join(kok, "KAMERA_AGACI.json"), {}) or {}
    for plan in S.get("sahneler") or []:
        no = plan.get("no")
        if nolar and no not in nolar: continue
        z = plan.get("zanaat") or {}
        if not z: continue
        if z.get("istem_elle"): olc.append(po.m("istem_elle", "BAYRAK", no, neden="elle istem derlenmedi")); continue
        sg = (S.get("sahne_gruplari") or {}).get(z.get("sahne_grubu")) or {}
        plan["_mekan"] = sg.get("mekan")
        ist, notlar, yas = plan_istemi(kok, plan, S, ev)
        yed, _, yas2 = plan_istemi(kok, plan, S, ev, yedek=True)
        plan.pop("_mekan", None)
        for sev, madde, kid in notlar: olc.append(po.m(madde, sev, no, olcu=kid))
        for madde, bulunan in yas + [(f"yedek_{a}", b) for a, b in yas2]: olc.append(po.m(madde, "HATA", no, olcu=bulunan))
        der = plan.setdefault("_derlenir", {})
        plan["gorsel_istem"] = ist; plan["gorsel_istem_yedek"] = yed
        der["gorsel_istem_taban"] = duzeltme_taban(ist); der["gorsel_istem_ozeti"] = _imza(ist)
        ur = plan.setdefault("uretim", {}).setdefault("gorsel", {})
        dug = (agac.get("dugumler") or {}).get(f"plan:{no}") or {}
        ur["basamak"] = basamak(plan); ur["agac_basamak"] = dug.get("basamak")
        sg_mekan = sg.get("mekan")
        refs = referanslar(dict(plan, _mekan=sg_mekan), E, ev)
        ur["referanslar"] = refs
        ur["kart_surumleri"] = {r.split(":", 1)[1].split("/")[0]: r.rsplit("@", 1)[-1] for r in refs if r.startswith("kart:")}
        satir.append(f"{no:>4} B{ur['basamak']} {' '.join(refs)}\n     {ist}\n")
    yol, r = po.rapor_yaz(kok, "ISTEM", "GORSEL", olc, asama="A11", arac=SURUM,
                          birimler=[p.get("no") for p in S.get("sahneler") or [] if not nolar or p.get("no") in nolar],
                          girdi_imza=_imza([ev.karakter(k).get("surum") for k in sorted((S.get("karakterler") or {}))]))
    if not kuru:
        ortak.atomik_yaz(sp, S)
        os.makedirs(os.path.join(kok, "_RAPOR"), exist_ok=True)
        with open(os.path.join(kok, "_RAPOR", "ISTEM_DERLEME_GORSEL.txt"), "w", encoding="utf-8") as f: f.write("".join(satir))
        derle_kapak(kok)
    po.yaz_ozet(r, "istem_derle --gorsel")
    return (1 if r["sonuc"] in ("HATA", "KISMI") else 0), r


def duzeltme_taban(ist):
    return re.sub(r"\s*CORRECTION:.*$", "", ist).strip()


# --- kartlar -----------------------------------------------------------------------------------------------------
def _liste(x):
    if isinstance(x, dict): return [dict(v, id=v.get("id") or k) for k, v in x.items() if isinstance(v, dict)]
    return [v for v in x or [] if isinstance(v, dict)]


def kart_istemi(tur, k, varyant=None, dunya=None):
    stil = ((dunya or {}).get("stil_eki") or "").rstrip(".")
    if tur == "karakter" and k.get("tur") == "yaratik":
        ev = (k.get("evreler") or {}).get(varyant) or {}
        boy = ((ev.get("olcek") or {}).get("benzetme"))
        s = (f"Creature reference sheet on a plain light-grey studio backdrop: on the frame left a full side view, next to it a three-quarter "
             f"view, in the middle a front view of the head, on the frame right a back view. The same creature in every view: {k.get('kimlik_en')}"
             + (f", the size of {boy}" if boy else "") + ". " + GERCEKCILIK_YARATIK + ". No text, no labels, no people.")
    elif tur == "karakter":
        ko = (k.get("kostumler") or {}).get(varyant) or {}
        kt = ko.get("tarif_en") or ""
        if ko.get("turetildigi"): kt = (((k.get("kostumler") or {}).get(ko["turetildigi"]) or {}).get("tarif_en") or "") + ", " + (ko.get("fark_en") or "")
        s = ("Character reference sheet on a plain light-grey studio backdrop, " + GERCEKCILIK_INSAN + ": on the frame left a full-body front "
             "view, next to it a full-body three-quarter view, in the middle a 2x2 grid of face close-ups (front, three-quarter toward frame "
             "left, three-quarter toward frame right, profile), on the frame right a full-body back view. The same person in every view: "
             f"{k.get('kimlik_en')}" + (f", wearing {kt.strip(', ')}" if kt.strip(", ") else "") + ". Neutral expression, arms relaxed. "
             "No text, no labels, no other people.")
    elif tur == "mekan":
        pl = varyant or {}
        notr = "; ".join(f"the {_ad(o)} is {DURUM_EN.get(d, _ad(d))}" for o, d in (k.get("notr_durum") or {}).items())
        gor = ", ".join(f"{_belirli(g.get('ad') or _ad(g.get('id')))} {UC_EN.get(__import__('olcum').ucte_bir_normal(g.get('ucte_bir')), '')}".strip()
                        for g in pl.get("gorunen") or [] if isinstance(g, dict))
        s = (f"An empty location plate photograph, no people, no figures: {k.get('tarif_en')}. " + (pl.get("aci_en") + ". " if pl.get("aci_en") else "")
             + (f"Visible: {gor}. " if gor else "") + (notr[:1].upper() + notr[1:] + ". " if notr else "") + "Neutral, even exposure.")
    else:
        s = (f"Product reference photograph on a plain light-grey backdrop: {k.get('tarif_en')}, "
             f"{k.get('olcek_kart_tarifi') or 'held between a thumb and index finger for scale'}. No text, no labels.")
    return (s + (f" {stil}." if stil else "")).strip()


def derle_kart(kok):
    import plan_ortak as po, olcum
    spec = ortak.json_oku(os.path.join(kok, "_KARTLAR", "KART_SPEC.json"))
    if not isinstance(spec, dict): print("!! _KARTLAR/KART_SPEC.json yok", flush=True); return 2, None
    ev = Evren(kok); dunya = ev.dunya(); n = int(olcum.esik("kart_aday_sayisi") or 3)
    adaylar = [chr(ord("a") + i) for i in range(n)]
    kartlar, olc = [], []
    for k in _liste(spec.get("karakterler")):
        kilit = ev.karakter(k["id"])
        vary = list((k.get("evreler") or {}).keys()) if k.get("tur") == "yaratik" else list((k.get("kostumler") or {}).keys()) or ["k1"]
        for v in vary:
            if kilit.get("durum") == "kilitli" and (((kilit.get("kostumler") or {}).get(v) or {}).get("kart")
                                                    or ((kilit.get("evreler") or {}).get(v) or {}).get("kart")):
                continue                                          # kilitli kart yeniden tasarlanmaz (yalnız eksik varyant)
            kartlar.append({"kart_id": f"karakter_{k['id']}_{v}", "tur": "karakter", "id": k["id"], "varyant": v,
                            "istem": kart_istemi("karakter", k, v, dunya), "referanslar": [], "adaylar": adaylar})
            if not k.get("kimlik_en"): olc.append(po.m("kimlik_en_yok", "HATA", None, birim=k["id"]))
    for m in _liste(spec.get("mekanlar")):
        for pl in _liste(m.get("plakalar")):
            kartlar.append({"kart_id": f"mekan_{m['id']}_{pl['id']}", "tur": "mekan", "id": m["id"], "varyant": pl["id"],
                            "istem": kart_istemi("mekan", m, pl, dunya), "referanslar": [], "adaylar": adaylar,
                            "gorunen": pl.get("gorunen") or [], "notr_durum": m.get("notr_durum") or {}})
    for o in _liste(spec.get("nesneler")):
        kartlar.append({"kart_id": f"nesne_{o['id']}_olcek", "tur": "nesne", "id": o["id"], "varyant": "olcek",
                        "istem": kart_istemi("nesne", o, None, dunya), "referanslar": [], "adaylar": adaylar})
    for k in kartlar:
        for madde, b in _yasak(k["istem"]): olc.append(po.m(madde, "HATA", None, birim=k["kart_id"], olcu=b))
        k["dosyalar"] = [f"{k['kart_id']}_{a}.jpg" for a in adaylar]
    ortak.atomik_yaz(os.path.join(kok, "_KARTLAR", "KART_ISTEMLERI.json"),
                     {"_surum": 1, "_uretim": po.zarf("A10d", SURUM, girdi_imza=_imza(spec)), "kartlar": kartlar})
    print(f"kart istemi: {len(kartlar)} kart × {n} aday", flush=True)
    return (1 if any(o["seviye"] == "HATA" for o in olc) else 0), {"kartlar": kartlar, "olcumler": olc}


# --- kapak -------------------------------------------------------------------------------------------------------
def derle_kapak(kok, adet=10):
    import olcum, plan_ortak as po
    h = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}; ev = Evren(kok)
    kar = h.get("karakterler") or {}
    insan = next((k for k, v in kar.items() if isinstance(v, dict) and v.get("rol") == "kahraman"), None) or \
        next((k for k, v in kar.items() if isinstance(v, dict) and v.get("rol") != "yaratik"), None)
    yaratik = next((k for k, v in kar.items() if isinstance(v, dict) and v.get("rol") == "yaratik"), None)
    adet = max(int(olcum.esik("kapak_aday_min") or 8), min(int(olcum.esik("kapak_aday_max") or 12), adet))
    def tarif(k):
        c = ev.karakter(k) if k else {}
        return c.get("kimlik_en") or ""
    mek = next(iter(h.get("mekanlar") or []), {}) or {}
    mt = ev.mekan(mek.get("id")).get("tarif_en") if mek.get("id") else None
    stil = (ev.dunya().get("stil_eki") or "").rstrip(".")
    out = []
    for i in range(adet):
        kad, isik = KAPAK_VARYANT[i % len(KAPAK_VARYANT)]
        s = (f"Cinematic movie poster still, photorealistic, {kad}. The human: {tarif(insan) or 'the hero'}."
             + (f" The creature: {tarif(yaratik)}." if yaratik else "") + (f" Location: {mt}." if mt else "")
             + f" Lighting: {isik}. Strong readable faces even as a small thumbnail, high contrast, shallow depth of field."
             " No text, no letters, no logo, no watermark, no crowd." + (f" {stil}." if stil else ""))
        refs = [f"kart:{k}" for k in (insan, yaratik) if k]
        out.append({"no": f"kapak_{i + 1:02d}", "dosya": f"kapak_{i + 1:02d}.jpg", "istem": s, "referanslar": refs,
                    "yasak": [m for m, _ in _yasak(s)]})
    ortak.atomik_yaz(os.path.join(kok, "YAYIN", "KAPAK_SPEC.json"),
                     {"_surum": 1, "_uretim": po.zarf("A11", SURUM), "insan": insan, "yaratik": yaratik, "adaylar": out,
                      "kalip": "insan + yaratık aynı karede, logo ve kalabalık yazı yok (KARARLAR.md)"})
    return 0, out


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 4
    import plan_ortak as po
    kok = po.film_kok(po.arg_al(argv, "--film"))
    nolar = None
    if po.arg_al(argv, "--plan"):
        try: nolar = [int(x) for x in po.arg_al(argv, "--plan").split(",") if x]
        except ValueError: print("!! --plan sayı listesi olmalı"); return 4
    if "--gorsel" in argv: return derle_gorsel(kok, nolar, kuru="--kuru" in argv)[0]
    if "--kart" in argv: return derle_kart(kok)[0]
    if "--kapak" in argv: return derle_kapak(kok)[0]
    if "--bitis" in argv: print("!! --bitis (Z2 bitiş görseli) kare_zinciri ile birlikte gelir (adım 15)"); return 4
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
