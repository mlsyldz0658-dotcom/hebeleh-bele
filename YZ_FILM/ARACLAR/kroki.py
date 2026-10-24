"""KROKİ — mekân krokisi geometrisi: izdüşüm, görüş hattı, bakış/ışık/ekran yönü, 180°, kurulum çiftleri (TASARIM §6.4; [YN2] §4.5.4, §4.5.12, Y14–Y28, Y60).

Kullanım:
  python kroki.py --karsilikli --film <film>     her mekân krokisi için standart karşılıklı kurulum önerileri → _YONETMEN/KROKI_ONERI.json
                                                 (görev bağlamında aynı dosya görevin GIRDI/ klasörüne de konur; A07a grup 0)
  python kroki.py --ciz --film <film>            kroki + kurulumlar + görüş konileri → _YONETMEN/KROKI/<mekan>.png (Pillow; yoksa ÖLÇÜLEMEDİ, 0)
  python kroki.py --denetle --film <film>        kroki dosyalarının biçimi (duvar, öğe, işaret, plaka, ışık) → _RAPOR/SEMA_KROKI.json
  python kroki.py --sahne S12 --film <film>      sahnenin geometrik kuralları (Y14, Y17, Y18, Y19, Y23, Y28, Y60) → _RAPOR/Z0_KROKI_S12.json
  python kroki.py --tum --film <film>            bütün sahneler → _RAPOR/Z0_KROKI.json
Kodda: derle(plan, bas, bit, K) → (_derlenir alanları, ölçümler) · sahne_derle(sid, planlar, K) · yasak_ardisik(...) · izdusum(kurulum, nokta)
Geometri: metre; x = doğu, y = kuzey; yon_derece pusula (0 = kuzey, 90 = doğu). Yatay görüş açısı 2·atan(18/f) (36 mm tam kare).
Tanjant izdüşümü: konum = tan(açı) / tan(yarım görüş); < −1/3 sol üçte bir, > +1/3 sağ üçte bir. Kroki eksik olduğu için hesaplanamayan
kural HESAPLANAMADI verir ve HATA sayılır ([YN2] §4.7: "ölçülemedi asla GEÇ değildir"in kâğıttaki karşılığı).
Çıkış kodları: 0 tamam · 1 HATA · 2 film/kroki yok · 4 kullanım.
"""
import os, sys, math, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "kroki 1.0"
ENGEL_YARICAP = 0.35            # engel öğesinin görüş hattını kestiği yarıçap (m; tahmin)
KISI_BOY = 1.7
KADRAJ_YUKSEKLIK = {"Y": 0.35, "OY": 0.6, "O": 0.95, "OG": 1.35, "G": 2.4, "EG": 6.0, "CY": 0.15}   # kadrajın kapsadığı dikey (m; tahmin)


# --- temel geometri -----------------------------------------------------------------------------------------------
def fov(lens): return math.degrees(2 * math.atan(18.0 / float(lens or 35)))


def yon_vektor(derece):
    r = math.radians(derece); return (math.sin(r), math.cos(r))


def sag_vektor(derece):
    r = math.radians(derece); return (math.cos(r), -math.sin(r))


def _fark(a, b): return (b[0] - a[0], b[1] - a[1])
def _nokta(a, b): return a[0] * b[0] + a[1] * b[1]
def _uz(a): return math.hypot(a[0], a[1])


def kerteriz(a, b):
    v = _fark(a, b); return math.degrees(math.atan2(v[0], v[1])) % 360


def aci_fark(a, b): return (a - b + 180) % 360 - 180


def izdusum(kur, p):
    """(x ∈ yaklaşık [-1,1] kadraj genişliği, derinlik m) ya da kameranın arkasındaysa None."""
    if p is None or kur is None or kur.get("konum") is None: return None
    c = kur["konum"]; f = yon_vektor(kur.get("yon_derece", 0)); r = sag_vektor(kur.get("yon_derece", 0))
    v = _fark(c, p); der = _nokta(v, f)
    if der <= 0.05: return None
    yan = _nokta(v, r)
    return (yan / der) / math.tan(math.radians(fov(kur.get("lens_mm")) / 2)), der


def ucte_bir(x):
    if x is None: return None
    return "sol_ucte_bir" if x < -1 / 3 else "sag_ucte_bir" if x > 1 / 3 else "orta"


def _kesisir(p1, p2, q1, q2):
    def o(a, b, c): return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2, d3, d4 = o(q1, q2, p1), o(q1, q2, p2), o(p1, p2, q1), o(p1, p2, q2)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def _kesisim_t(p1, p2, q1, q2):
    """p1→p2 doğrusunun q1q2 ile kesiştiği yerin p1'den oranı."""
    r = _fark(p1, p2); s = _fark(q1, q2); den = r[0] * s[1] - r[1] * s[0]
    if abs(den) < 1e-9: return None
    qp = _fark(p1, q1)
    t = (qp[0] * s[1] - qp[1] * s[0]) / den; u = (qp[0] * r[1] - qp[1] * r[0]) / den
    return (t, u) if 0 < t < 1 and 0 <= u <= 1 else None


def _aciklikta(duvar, u):
    a, b = duvar["a"], duvar["b"]; x = a[0] + u * (b[0] - a[0]); y = a[1] + u * (b[1] - a[1])
    for ac in duvar.get("aciklik") or []:
        if "x" in ac and ac["x"][0] <= x <= ac["x"][1]: return True
        if "y" in ac and ac["y"][0] <= y <= ac["y"][1]: return True
    return False


def gorus_acik(K, c, p, haric=()):
    """c → p görüş hattı duvar (açıklık hariç) ve engel öğeleri tarafından kesiliyor mu?"""
    for d in K.get("duvarlar") or []:
        k = _kesisim_t(c, p, d["a"], d["b"])
        if k and not _aciklikta(d, k[1]): return False
    for o in K.get("ogeler") or []:
        if not o.get("engel") or o.get("id") in haric or not isinstance(o.get("konum"), list): continue
        q = o["konum"]; v = _fark(c, p); L = _uz(v)
        if L < 1e-6: continue
        t = max(0.0, min(1.0, _nokta(_fark(c, q), v) / (L * L)))
        en = (c[0] + t * v[0], c[1] + t * v[1])
        if _uz(_fark(en, q)) < ENGEL_YARICAP and 0.05 < t < 0.97: return False
    return True


# --- kroki yükleme ------------------------------------------------------------------------------------------------
def kroki_yolu(kok, evren_ref):
    """'EVREN/<SERI>/mekanlar/<id>@<sürüm>' → kroki.json yolu: önce veri kökü, yoksa film klasörü (örnek/test filmi)."""
    if not evren_ref: return None
    ref = evren_ref.split("@")[0]
    adaylar = []
    try: adaylar.append(os.path.join(ortak.yollar()["veri_kok"], ref, "kroki.json"))
    except ortak.YolYok: pass
    adaylar.append(os.path.join(kok, ref, "kroki.json"))
    return next((a for a in adaylar if os.path.isfile(a)), None)


class Kroki:
    """Bir filmin bütün mekân krokileri + kurulumları + nesne adları."""
    def __init__(self, kok, sahneler, harita=None):
        self.kok, self.s = kok, sahneler
        self.mekanlar = {}
        for mid, mv in (sahneler.get("mekanlar") or {}).items():
            y = kroki_yolu(kok, (mv or {}).get("evren"))
            self.mekanlar[mid] = {"kroki": ortak.json_oku(y) if y else None, "yol": y, "kurulumlar": (mv or {}).get("kurulumlar") or {}}
        self.harita = harita or {}

    def kroki(self, mid): return (self.mekanlar.get(mid) or {}).get("kroki")
    def kurulum(self, mid, kid): return ((self.mekanlar.get(mid) or {}).get("kurulumlar") or {}).get(kid)

    def nokta(self, mid, ad, durum=None, _derin=0):
        """isaret, öğe, ışık kaynağı, karakter ya da nesne kimliğinden konum."""
        K = self.kroki(mid)
        if not K or ad is None: return None
        if isinstance(ad, list): return ad
        isr = (K.get("isaretler") or {}).get(ad)
        if isr and isinstance(isr.get("konum"), list): return isr["konum"]
        for grup in ("ogeler", "isik_kaynaklari"):
            for o in K.get(grup) or []:
                if o.get("id") == ad and isinstance(o.get("konum"), list): return o["konum"]
        for pid, pv in (K.get("plakalar") or {}).items():
            if pid == ad: return pv.get("konum")
        if durum and _derin < 3:
            kv = (durum.get("karakterler") or {}).get(ad)
            if kv:
                if kv.get("mekan") not in (None, mid): return None
                return self.nokta(mid, kv.get("isaret"), durum, _derin + 1)
            nv = (durum.get("nesneler") or {}).get(ad)
            if nv:
                return self.nokta(mid, nv.get("kimde") or nv.get("nerede"), durum, _derin + 1)
        return None


# --- plan derleme -------------------------------------------------------------------------------------------------
def _kadrajdakiler(z): return [k for k in z.get("kadrajdakiler") or [] if isinstance(k, dict) and k.get("id")]


def _gorunur_kisi(k):
    return k.get("olcek") not in ("el",)


def _kademe(k, E):
    v = (E.get("olcek_kademeleri") or {}).get(k)
    return v if v is not None else ((po.sozluk("plan").get("kadraj") or {}).get(k) or {}).get("kademe")


def _kurulum_bul(K, mid, z):
    kam = z.get("kamera") or {}
    kur = K.kurulum(mid, kam.get("kurulum"))
    if kur is None: return None
    kur = dict(kur)
    if kam.get("lens_mm"): kur["lens_mm"] = kam["lens_mm"]
    return kur


def taraf(eksen_a, eksen_b, c):
    """Kamera c'nin A→B eksenine göre tarafı: pusula yönü (dogu|bati|kuzey|guney)."""
    v = _fark(eksen_a, eksen_b); w = _fark(eksen_a, c)
    cr = v[0] * w[1] - v[1] * w[0]
    n = (-v[1], v[0]) if cr > 0 else (v[1], -v[0])          # eksenin kamera tarafındaki normali
    if abs(n[0]) >= abs(n[1]): return "dogu" if n[0] > 0 else "bati"
    return "kuzey" if n[1] > 0 else "guney"


def derle(plan, bas, bit, K, sg, E=None, karakter_bilgi=None):
    """Planın _derlenir geometri alanları ve ölçümleri. bas/bit: dünya defterinin çözdüğü durumlar."""
    E = E or po.esik(); z = plan.get("zanaat") or {}; no = plan.get("no"); mid = sg.get("mekan")
    out, olc = {}, []
    kroki = K.kroki(mid); kur = _kurulum_bul(K, mid, z)
    kd = _kadrajdakiler(z)
    out["kadraj_sirasi"] = []
    if not kroki or not kur:
        if z.get("plan_tipi") not in ("kart",):
            olc.append(po.m("kroki_hesaplanamadi", "HATA", no, olcu={"mekan": mid, "kurulum": (z.get("kamera") or {}).get("kurulum")},
                            kural="Y14/Y17/Y28", neden="kroki ya da kurulum yok: geometri HESAPLANAMADI (HATA sayılır)"))
        return _derlenir_durum(out, z, bas, bit, karakter_bilgi), olc
    f = yon_vektor(kur.get("yon_derece", 0)); r = sag_vektor(kur.get("yon_derece", 0))
    konum, xler = {}, {}
    for k in kd:
        p = K.nokta(mid, k["id"], bas); ip = izdusum(kur, p)
        if ip is not None: xler[k["id"]] = ip[0]; konum[k["id"]] = ucte_bir(ip[0])
        if k.get("olcek") == "on_plan_omuz" and ip is not None:
            konum[k["id"]] = "sag_on" if ip[0] > 0 else "sol_on"
    out["kadraj_konumu"] = konum
    out["kadraj_sirasi"] = [k for k, _ in sorted(xler.items(), key=lambda x: x[1])]
    # Y14 / Y28: kadrajdaki kişi seti ↔ geometri
    liste = {k["id"]: k for k in kd}
    girer = {a.get("ozne") for a in z.get("eylem_zinciri") or [] if a.get("fiil") in ("kadraja_girer", "kadrajdan_cikar")}
    for kim, kv in (bas.get("karakterler") or {}).items():
        if kv.get("mekan") not in (None, mid) or kv.get("gizli_arkasinda"): continue
        p = K.nokta(mid, kim, bas)
        if p is None:
            if kim in liste and liste[kim].get("olcek") != "el":
                olc.append(po.m("konum_hesaplanamadi", "HATA", no, kim=kim, olcu=kv.get("isaret"), kural="Y14",
                                neden="karakterin işareti krokide yok: görüş HESAPLANAMADI"))
            continue
        ip = izdusum(kur, p)
        sinir = 1.6 if (liste.get(kim) or {}).get("olcek") == "on_plan_omuz" else 1.0
        icinde = ip is not None and abs(ip[0]) <= sinir and gorus_acik(kroki, kur["konum"], p)
        if icinde and kim not in liste and kim not in girer and z.get("plan_tipi") != "ekleme":
            olc.append(po.m("kadrajda_ama_listede_yok", "HATA", no, kim=kim, olcu=round(ip[0], 2), kural="Y14/K0.7",
                            kok_neden="karakter_kayboldu", neden="görüş konisinde ve görüş hattı açık kişi kadrajdakiler'de yok"))
        if not icinde and kim in liste and liste[kim].get("olcek") not in ("el",) and kim not in girer:
            olc.append(po.m("listede_ama_kadraj_disi", "HATA", no, kim=kim, olcu=None if ip is None else round(ip[0], 2), kural="Y14/K0.7",
                            kok_neden="karakter_kayboldu", neden="kadrajdakiler'deki kişi geometriye göre kadraj dışında ya da engel arkasında"))
        if icinde and kim in liste and ip and liste[kim].get("olcek") in KADRAJ_YUKSEKLIK:
            h = ip[1] * 24.0 / float(kur.get("lens_mm") or 35)
            tahmin = min(KADRAJ_YUKSEKLIK, key=lambda k: abs(KADRAJ_YUKSEKLIK[k] - h))
            a, b = _kademe(tahmin, E), _kademe(liste[kim]["olcek"], E)
            if a and b and abs(a - b) > 1:
                olc.append(po.m("olcek_geometriye_uymuyor", "BAYRAK", no, kim=kim, olcu=liste[kim]["olcek"], esik=tahmin, kural="Y28",
                                neden=f"{ip[1]:.1f} m uzaklık ve {kur.get('lens_mm')} mm ile kadraj ≈ {tahmin}"))
    # bakış
    bk = {}
    for k in kd:
        kv = (bas.get("karakterler") or {}).get(k["id"]) or {}
        hedef = ((kv.get("bakis") or {}).get("hedef")) if isinstance(kv.get("bakis"), dict) else None
        bk_bit = (((bit.get("karakterler") or {}).get(k["id"]) or {}).get("bakis") or {})
        hedef_bit = bk_bit.get("hedef") if isinstance(bk_bit, dict) else None
        for an, hd, dur in (("bas", hedef, bas), ("bit", hedef_bit, bit)):
            if not hd: continue
            pk, ph = K.nokta(mid, k["id"], dur), K.nokta(mid, hd, dur)
            if pk is None or ph is None: continue
            yon = "kadraj_sagi" if _nokta(_fark(pk, ph), r) > 0 else "kadraj_solu"
            bk[k["id"] if an == "bas" else f"{k['id']}@bit"] = yon
    out["bakis_kadrajda"] = bk
    # ışık
    isik = {}
    odak = (z.get("kamera") or {}).get("odak") or (out["kadraj_sirasi"][0] if out["kadraj_sirasi"] else None)
    po_odak = K.nokta(mid, odak, bas) if odak else None
    for rol, kaynak in ((sg.get("isik") or {}).items()):
        if not kaynak: continue
        pk = K.nokta(mid, kaynak, bas)
        if pk is None or po_odak is None:
            if rol == "ana" and kaynak not in ("ay", "gunes", "gok"):
                olc.append(po.m("isik_hesaplanamadi", "HATA", no, olcu=kaynak, kural="Y23", kok_neden="isik_zipladi",
                                neden="ana ışık kaynağının konumu krokide ya da defterde yok"))
            continue
        v = _fark(po_odak, pk)
        yan = "sag" if _nokta(v, r) > 0 else "sol"; on = "on" if _nokta(v, f) < 0 else "arka"
        isik[rol] = f"{on}_{yan}"
    out["isik_kadrajda"] = isik
    # ekran yönü (yer değiştiren adımlardan)
    ey = None
    for a in z.get("eylem_zinciri") or []:
        if a.get("fiil") in ("yurur", "geri_cekilir", "kadraja_girer", "kadrajdan_cikar"):
            p1, p2 = K.nokta(mid, a.get("ozne"), bas), K.nokta(mid, a.get("ozne"), bit)
            if p1 and p2 and _uz(_fark(p1, p2)) > 0.05:
                ey = "soldan_saga" if _nokta(_fark(p1, p2), r) > 0 else "sagdan_sola"
    out["ekran_yonu"] = ey
    # kamera tarafı
    eks = sg.get("eksen") or []
    if len(eks) == 2:
        pa, pb = K.nokta(mid, eks[0], bas), K.nokta(mid, eks[1], bas)
        if pa and pb: out["kamera_tarafi"] = taraf(pa, pb, kur["konum"])
        elif z.get("plan_tipi") != "ekleme":
            out["kamera_tarafi"] = None
    # görünmesi gerekenler (görüş konisindeki adım hedefleri dahil)
    gg = []
    for k in kd:
        if k.get("yuz_acisi") not in (None, "gorunmez", "sirt") and k.get("olcek") != "el": gg.append(f"{k['id']}.yuz")
        for el in ("sag", "sol"):
            t = ((((bit.get("karakterler") or {}).get(k["id"]) or {}).get("eller") or {}).get(el) or {}).get("tutar")
            if t: gg += [f"{k['id']}.eller.{el}:{t}", t]
    for a in z.get("eylem_zinciri") or []:
        h = a.get("hedef")
        if not h or h in liste: continue
        p = K.nokta(mid, h, bas); ip = izdusum(kur, p)
        if ip and abs(ip[0]) <= 1 and gorus_acik(kroki, kur["konum"], p, haric=(h,)): gg.append(h)
    out["gorunmesi_gerekenler"] = list(dict.fromkeys(gg))
    goz = {}
    for k in kd:
        kv = (bas.get("karakterler") or {}).get(k["id"]) or {}
        hd = ((kv.get("bakis") or {}).get("hedef")) if isinstance(kv.get("bakis"), dict) else None
        hv = (bas.get("karakterler") or {}).get(hd) if hd else None
        if hv:
            pz = po.sozluk("plan").get("poz") or {}
            a = (pz.get(kv.get("poz")) or {}).get("goz_yuksekligi_m"); b = (pz.get(hv.get("poz")) or {}).get("goz_yuksekligi_m")
            if (karakter_bilgi or {}).get(k["id"], {}).get("goz_yuksekligi_m"): a = karakter_bilgi[k["id"]]["goz_yuksekligi_m"]
            if (karakter_bilgi or {}).get(hd, {}).get("goz_yuksekligi_m"): b = karakter_bilgi[hd]["goz_yuksekligi_m"]
            if a is not None and b is not None and abs(a - b) > E.get("plan_goz_farki_bakis_m", 0.3):
                goz[k["id"]] = "asagi" if b < a else "yukari"
    out["goz_yukseklik_farki"] = goz
    return _derlenir_durum(out, z, bas, bit, karakter_bilgi), olc


def _derlenir_durum(out, z, bas, bit, kb):
    """Geometri dışı, durumdan derlenen alanlar: ağız, açık parmak, ayna yasağı, referans."""
    ps = po.sozluk("plan"); ya = ps.get("yuz_acisi") or {}; es = ps.get("el_sekli") or {}
    kd = _kadrajdakiler(z)
    agiz, dinleyen, parmak = {}, {}, {}
    konusan = {a.get("ozne") for a in z.get("eylem_zinciri") or [] if a.get("tur") == "konusma"}
    eds = bool(z.get("ekran_disi_ses"))
    for k in kd:
        a = (ya.get(k.get("yuz_acisi")) or {}).get("agiz", "gorunmez") if k.get("olcek") != "el" else "gorunmez"
        if k["id"] in konusan or k.get("konusur"): agiz[k["id"]] = a
        elif eds or konusan: dinleyen[k["id"]] = "kapali" if a != "gorunmez" else "gorunmez"
        el = (((bit.get("karakterler") or {}).get(k["id"]) or {}).get("eller") or {})
        if el:
            parmak[k["id"]] = {e: (es.get((el.get(e) or {}).get("sekil")) or {}).get("acik_parmak") for e in ("sag", "sol")}
    out["agiz_gorunur"] = agiz; out["dinleyen_agiz"] = dinleyen or None; out["acik_parmak"] = parmak
    ayna = False
    for k in kd:
        for d in (bas, bit):
            el = (((d.get("karakterler") or {}).get(k["id"]) or {}).get("eller") or {})
            sa, so = el.get("sag") or {}, el.get("sol") or {}
            if (sa.get("tutar") or None) != (so.get("tutar") or None) or sa.get("sekil") != so.get("sekil"): ayna = True
        if (kb or {}).get(k["id"], {}).get("asimetrik"): ayna = True
    out["ayna_yasak"] = ayna
    out["referans"] = [k["id"] for k in kd if k.get("olcek") != "el" and k.get("yuz_acisi") != "gorunmez"
                       and (kb is None or k["id"] in kb)]
    return out


# --- sahne düzeyi -------------------------------------------------------------------------------------------------
def kurulum_cifti(K, mid, ka, kb, ozne_p, kad_a, kad_b, E):
    """(açı farkı derece, ölçek kademe farkı) ya da None."""
    a, b = K.kurulum(mid, ka), K.kurulum(mid, kb)
    if not a or not b or ozne_p is None: return None
    d = abs(aci_fark(kerteriz(a["konum"], ozne_p), kerteriz(b["konum"], ozne_p)))
    oa, ob = _kademe(kad_a, E), _kademe(kad_b, E)
    return d, (abs(oa - ob) if oa and ob else None)


def yasak_ardisik(K, mid, sg, E):
    """Sahnede aynı özneye bakan kurulum çiftlerinden açı < aci_min_fark ve ölçek < olcek_kademe_min_fark olanlar."""
    kr = K.kroki(mid); out = []
    if not kr: return out
    eks = sg.get("eksen") or []
    ozne = eks[0] if eks else None
    p = K.nokta(mid, ozne, _sahne_bas(sg)) if ozne else None
    kurs = sg.get("kurulumlar") or list(((K.mekanlar.get(mid) or {}).get("kurulumlar") or {}).keys())
    for i, ka in enumerate(kurs):
        for kb in kurs[i + 1:]:
            a, b = K.kurulum(mid, ka), K.kurulum(mid, kb)
            if not a or not b or p is None: continue
            c = kurulum_cifti(K, mid, ka, kb, p, a.get("varsayilan_kadraj"), b.get("varsayilan_kadraj"), E)
            if c and c[0] < E.get("aci_min_fark_derece", 30) and (c[1] is not None and c[1] < E.get("olcek_kademe_min_fark", 2)):
                out += [[ka, kb], [kb, ka]]
    return out


def _sahne_bas(sg):
    g = sg.get("giris_durumu")
    return g if isinstance(g, dict) else {}


def sahne_denetle(sid, planlar, cozum, K, sg, E=None):
    """Sahne içi ardışık plan kuralları: Y17, Y18, Y19, yasak ardışık. planlar: kurgu sırasıyla; cozum: {no: {bas, bit}}."""
    E = E or po.esik(); olc = []; mid = sg.get("mekan"); kt = sg.get("kamera_tarafi")
    onceki = None
    for p in planlar:
        z = p.get("zanaat") or {}; dl = p.get("_derlenir") or {}; no = p.get("no")
        pt = dl.get("kamera_tarafi")
        if kt and pt and pt != kt and not z.get("eksen_gecis"):
            olc.append(po.m("eksen_180", "HATA", no, olcu=pt, esik=kt, kural="Y17/Z0#17", kok_neden="eksen_180",
                            neden="kurulum sahnenin kamera tarafında değil ve eksen_gecis yok"))
        if onceki is not None:
            zo = onceki.get("zanaat") or {}; do = onceki.get("_derlenir") or {}
            ka, kb = (zo.get("kamera") or {}).get("kurulum"), (z.get("kamera") or {}).get("kurulum")
            oa, ob = (zo.get("kamera") or {}).get("odak"), (z.get("kamera") or {}).get("odak")
            if oa and oa == ob and ka and kb and ka != kb:
                d = cozum.get(str(no)) or {}
                c = kurulum_cifti(K, mid, ka, kb, K.nokta(mid, ob, d.get("bas")), (zo.get("kamera") or {}).get("kadraj"),
                                  (z.get("kamera") or {}).get("kadraj"), E)
                if c and c[0] < E.get("aci_min_fark_derece", 30) and c[1] is not None and c[1] < E.get("olcek_kademe_min_fark", 2):
                    olc.append(po.m("aci_olcek_sicramasi", "HATA", no, olcu={"aci": round(c[0], 1), "kademe": c[1]}, onceki=onceki.get("no"),
                                    esik={"aci": E.get("aci_min_fark_derece"), "kademe": E.get("olcek_kademe_min_fark")}, kural="Y19/Z0#12",
                                    kok_neden="olcek_sicramasi", neden="aynı özneye ardışık iki planda açı < 30° ve ölçek < 2 kademe"))
            if [ka, kb] in ((sg.get("_derlenir") or {}).get("yasak_ardisik") or []):
                olc.append(po.m("yasak_ardisik_kurulum", "HATA", no, olcu=[ka, kb], kural="Y19", kok_neden="olcek_sicramasi"))
            eks = sg.get("eksen") or []
            if len(eks) == 2 and oa in eks and ob in eks and oa != ob:
                ba, bb = (do.get("bakis_kadrajda") or {}).get(oa), (dl.get("bakis_kadrajda") or {}).get(ob)
                tek = lambda zz: len([k for k in zz.get("kadrajdakiler") or [] if k.get("olcek") not in ("on_plan_omuz", "el")]) == 1
                if ba and bb and ba == bb and tek(zo) and tek(z):
                    olc.append(po.m("karsilikli_bakis_ayni_yon", "HATA", no, olcu=[ba, bb], onceki=onceki.get("no"), kural="Y18/Z0#18",
                                    kok_neden="bakis", neden="karşılıklı tekli planlarda bakışlar kadrajda zıt olmalı"))
        onceki = p
    return olc


def plaka_denetle(K, mid, sg):
    """Y60: her kurulumun görüş konisindeki öğeler ebeveyn zincirindeki plakada da görünür. Plaka gorunen listesini döndürür."""
    kr = K.kroki(mid); olc = []
    if not kr: return olc, {}
    gorunen = {}
    def gor(kur):
        out = set()
        for o in (kr.get("ogeler") or []):
            p = o.get("konum") if isinstance(o.get("konum"), list) else None
            ip = izdusum(kur, p)
            if ip and abs(ip[0]) <= 1 and gorus_acik(kr, kur["konum"], p, haric=(o.get("id"),)): out.add(o["id"])
        return out
    for pid, pv in (kr.get("plakalar") or {}).items():
        gorunen[pid] = sorted(gor(pv))
    kurs = (K.mekanlar.get(mid) or {}).get("kurulumlar") or {}
    for kid in sg.get("kurulumlar") or kurs.keys():
        kur = kurs.get(kid)
        if not kur: continue
        zincir, e, adim = [], kur.get("ebeveyn"), 0
        while e and adim < 6:
            adim += 1
            if str(e).startswith("plaka:"): zincir.append(e.split(":", 1)[1]); break
            e = (kurs.get(str(e).split("@")[0]) or {}).get("ebeveyn")
        if not zincir or zincir[0] not in gorunen:
            olc.append(po.m("plaka_zinciri_yok", "HATA", None, sahne=sg.get("_id"), olcu=kid, kural="Y60",
                            kok_neden="plaka_oge", neden="kurulumun ebeveyn zinciri bir plakaya varmıyor: plaka görüneni HESAPLANAMADI"))
            continue
        eksik = sorted(gor(kur) - set(gorunen[zincir[0]]))
        if eksik:
            olc.append(po.m("plakada_olmayan_oge", "HATA", None, sahne=sg.get("_id"), olcu={"kurulum": kid, "ogeler": eksik}, esik=zincir[0],
                            kural="Y60", kok_neden="plaka_oge", neden="kurulumun gördüğü öğe kök plakada görünmüyor (ana kare plakadan türetilemez)"))
    return olc, gorunen


def kroki_denetle(K):
    olc = []
    for mid, mv in K.mekanlar.items():
        kr = mv.get("kroki")
        if not kr:
            olc.append(po.m("kroki_yok", "HATA", None, mekan=mid, neden="evren yolunda kroki.json yok")); continue
        for d in kr.get("duvarlar") or []:
            if not (isinstance(d.get("a"), list) and isinstance(d.get("b"), list)): olc.append(po.m("duvar_bicimi", "HATA", None, mekan=mid, olcu=d.get("id")))
        for o in kr.get("ogeler") or []:
            if not o.get("id"): olc.append(po.m("oge_kimliksiz", "HATA", None, mekan=mid))
        for a, v in (kr.get("isaretler") or {}).items():
            if not isinstance((v or {}).get("konum"), list): olc.append(po.m("isaret_konumsuz", "HATA", None, mekan=mid, olcu=a))
        if not kr.get("plakalar"): olc.append(po.m("plaka_yok", "HATA", None, mekan=mid, neden="kamera ağacının kökü plaka yok"))
        for pid, pv in (kr.get("plakalar") or {}).items():
            if not isinstance(pv.get("konum"), list) or "yon_derece" not in pv: olc.append(po.m("plaka_bicimi", "HATA", None, mekan=mid, olcu=pid))
        for kid, kv in mv["kurulumlar"].items():
            if not isinstance(kv.get("konum"), list) or "yon_derece" not in kv or not kv.get("lens_mm"):
                olc.append(po.m("kurulum_bicimi", "HATA", None, mekan=mid, olcu=kid))
    return olc


# --- karşılıklı öneri ve çizim ------------------------------------------------------------------------------------
def karsilikli(kroki, a_ad, b_ad, lens_ou=50, lens_tek=85):
    """A–B ekseni için standart düzen (taraf başına): ikili, iki omuz üstü, iki tekli."""
    A, B = kroki["isaretler"][a_ad]["konum"], kroki["isaretler"][b_ad]["konum"]
    v = _fark(A, B); L = _uz(v) or 1.0; u = (v[0] / L, v[1] / L); n = (-u[1], u[0])
    out = {}
    for t, s in (("1", 1), ("2", -1)):
        nn = (n[0] * s, n[1] * s); orta = ((A[0] + B[0]) / 2, (A[1] + B[1]) / 2)
        def kur(p, hedef, lens, kad, not_):
            return {"konum": [round(p[0], 2), round(p[1], 2)], "yon_derece": round(kerteriz(p, hedef), 1), "lens_mm": lens,
                    "yukseklik_m": 1.6, "varsayilan_kadraj": kad, "not": not_}
        out[f"taraf{t}"] = {
            "taraf": taraf(A, B, (orta[0] + nn[0], orta[1] + nn[1])),
            "ikili": kur((orta[0] + nn[0] * 2.5, orta[1] + nn[1] * 2.5), orta, 28, "IK", "ikili konum planı"),
            "ou_a": kur((B[0] - u[0] * 0.6 + nn[0] * 0.5, B[1] - u[1] * 0.6 + nn[1] * 0.5), A, lens_ou, "OU", f"{b_ad} omzu üstünden {a_ad}"),
            "ou_b": kur((A[0] + u[0] * 0.6 + nn[0] * 0.5, A[1] + u[1] * 0.6 + nn[1] * 0.5), B, lens_ou, "OU", f"{a_ad} omzu üstünden {b_ad}"),
            "tek_a": kur((A[0] + u[0] * 1.2 + nn[0] * 0.6, A[1] + u[1] * 1.2 + nn[1] * 0.6), A, lens_tek, "Y", f"{a_ad} tekli"),
            "tek_b": kur((B[0] - u[0] * 1.2 + nn[0] * 0.6, B[1] - u[1] * 1.2 + nn[1] * 0.6), B, lens_tek, "Y", f"{b_ad} tekli")}
    return out


def karsilikli_film(kok):
    s = _sahneler_ya_da_harita(kok); oneri = {}
    K = Kroki(kok, s)
    for mid, mv in K.mekanlar.items():
        kr = mv.get("kroki")
        if not kr: continue
        isr = sorted((kr.get("isaretler") or {}).keys())
        ciftler = sorted(((a, b) for i, a in enumerate(isr) for b in isr[i + 1:]),
                         key=lambda c: _uz(_fark(kr["isaretler"][c[0]]["konum"], kr["isaretler"][c[1]]["konum"])))[:3]
        oneri[mid] = {f"{a}-{b}": karsilikli(kr, a, b) for a, b in ciftler}
    return oneri


def _sahneler_ya_da_harita(kok):
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if isinstance(s, dict) and s.get("mekanlar"): return s
    mek = {}
    for y in sorted(glob.glob(os.path.join(kok, "_YONETMEN", "HARITA_P*.json"))):
        mek.update((ortak.json_oku(y, {}) or {}).get("mekanlar") or {})
    h = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    seri = h.get("evren")
    for m in h.get("mekanlar") or []:
        if isinstance(m, dict) and m.get("id") and m["id"] not in mek and seri:
            mek[m["id"]] = {"evren": f"EVREN/{seri}/mekanlar/{m['id']}", "kurulumlar": {}}
    return {"mekanlar": mek}


def ciz(kok, olcek=60):
    try:
        from PIL import Image, ImageDraw
    except ImportError:
        print("ÖLÇÜLEMEDİ: Pillow yok; kroki PNG'si çizilmedi (KUR1 Pillow kurar).", flush=True); return [], "OLCULEMEDI"
    K = Kroki(kok, _sahneler_ya_da_harita(kok)); yazilan = []
    for mid, mv in K.mekanlar.items():
        kr = mv.get("kroki")
        if not kr: continue
        (x0, y0), (x1, y1) = kr.get("sinir") or [[-5, -5], [5, 5]]
        W, H = int((x1 - x0) * olcek) + 80, int((y1 - y0) * olcek) + 80
        im = Image.new("RGB", (W, H), (250, 248, 240)); dr = ImageDraw.Draw(im)
        P = lambda p: (40 + (p[0] - x0) * olcek, 40 + (y1 - p[1]) * olcek)
        for d in kr.get("duvarlar") or []: dr.line([P(d["a"]), P(d["b"])], fill=(40, 40, 40), width=4)
        for o in kr.get("ogeler") or []:
            if isinstance(o.get("konum"), list):
                c = P(o["konum"]); dr.rectangle([c[0] - 6, c[1] - 6, c[0] + 6, c[1] + 6], outline=(120, 70, 20), width=2); dr.text((c[0] + 8, c[1] - 6), o["id"], fill=(120, 70, 20))
        for a, v in (kr.get("isaretler") or {}).items():
            c = P(v["konum"]); dr.ellipse([c[0] - 5, c[1] - 5, c[0] + 5, c[1] + 5], fill=(30, 90, 200)); dr.text((c[0] + 7, c[1] + 2), a, fill=(30, 90, 200))
        kams = dict(mv["kurulumlar"]); kams.update({f"plaka:{k}": v for k, v in (kr.get("plakalar") or {}).items()})
        for kid, kv in kams.items():
            if not isinstance(kv.get("konum"), list): continue
            c = P(kv["konum"]); yarim = fov(kv.get("lens_mm")) / 2; renk = (200, 40, 40) if not kid.startswith("plaka") else (90, 150, 90)
            for s in (-yarim, yarim):
                u = yon_vektor(kv.get("yon_derece", 0) + s); dr.line([c, P((kv["konum"][0] + u[0] * 2.5, kv["konum"][1] + u[1] * 2.5))], fill=renk, width=1)
            dr.ellipse([c[0] - 4, c[1] - 4, c[0] + 4, c[1] + 4], fill=renk); dr.text((c[0] + 6, c[1] + 6), kid, fill=renk)
        hedef = os.path.join(kok, "_YONETMEN", "KROKI", f"{mid}.png"); os.makedirs(os.path.dirname(hedef), exist_ok=True)
        tmp = hedef + ".tmp.png"; im.save(tmp); os.replace(tmp, hedef); yazilan.append(hedef)
    return yazilan, "GEC"


# --- film düzeyi --------------------------------------------------------------------------------------------------
def _yukle(kok):
    """SAHNELER.json (varsa) ya da PLANLAR + HARITA'dan bellekte kurulan v2 + dünya çözümü."""
    import plan_birlestir, dunya_defteri
    s = plan_birlestir.kaynak_sahneler(kok)
    if s is None: return None, None, None
    h = ortak.json_oku(os.path.join(kok, "HIKAYE.json"))
    C = dunya_defteri.coz(s, h)
    return s, C, Kroki(kok, s)


def denetle_film(kok, sahne=None):
    s, C, K = _yukle(kok)
    if s is None: return [po.m("planlar_yok", "HATA")], []
    E = po.esik(); olc, birim = [], []
    planlar = sorted(s.get("sahneler") or [], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0))
    for sid, sg in (s.get("sahne_gruplari") or {}).items():
        if sahne and sid != sahne: continue
        sg = dict(sg, _id=sid)
        sp = [p for p in planlar if (p.get("zanaat") or {}).get("sahne_grubu") == sid]
        sg.setdefault("_derlenir", {})["yasak_ardisik"] = yasak_ardisik(K, sg.get("mekan"), sg, E)
        for p in sp:
            d = C.planlar.get(str(p.get("no"))) or {"bas": {}, "bit": {}}
            dl, o = derle(p, d["bas"], d["bit"], K, sg, E, s.get("karakterler"))
            p["_derlenir"] = dict(p.get("_derlenir") or {}, **{k: v for k, v in dl.items() if not k.startswith("_")})
            olc += o; birim.append(p.get("no"))
        olc += sahne_denetle(sid, sp, C.planlar, K, sg, E)
        olc += plaka_denetle(K, sg.get("mekan"), sg)[0]
    return olc, birim


def main(argv):
    if not argv or "-h" in argv or "--help" in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film"))
    if "--karsilikli" in argv:
        o = karsilikli_film(kok)
        v = {"_surum": 1, "_uretim": po.zarf("A07a", SURUM), "oneriler": o,
             "not": "Standart karşılıklı çekim düzeni önerisidir; yönetmen seçer, değiştirir ya da reddeder. Kamera tarafı pusula yönüdür."}
        ortak.atomik_yaz(os.path.join(kok, "_YONETMEN", "KROKI_ONERI.json"), v)
        g = os.environ.get("YZ_FILM_GOREV")
        if g and os.path.isdir(g): ortak.atomik_yaz(os.path.join(g, "GIRDI", "KROKI_ONERI.json"), v)
        print(f"kroki önerisi: {sum(len(x) for x in o.values())} eksen, {len(o)} mekân", flush=True)
        return 0
    if "--ciz" in argv:
        yaz, s = ciz(kok); print(f"kroki PNG: {len(yaz)} ({s})", flush=True); return 0
    if "--denetle" in argv:
        K = Kroki(kok, _sahneler_ya_da_harita(kok))
        yol, r = po.rapor_yaz(kok, "SEMA", "KROKI", kroki_denetle(K), asama="A07a", arac=SURUM, birimler=list(K.mekanlar))
        po.yaz_ozet(r, "kroki"); return po.cikis(r)
    sahne = po.arg_al(argv, "--sahne")
    if sahne or "--tum" in argv:
        olc, birim = denetle_film(kok, sahne)
        kapsam = f"KROKI_{sahne}" if sahne else "KROKI"
        yol, r = po.rapor_yaz(kok, "Z0", kapsam, olc, asama="A07b", arac=SURUM, birimler=birim, varsayilan=os.path.join("_RAPOR", f"Z0_{kapsam}.json"))
        po.yaz_ozet(r, "kroki"); return po.cikis(r)
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
