"""DÜNYA DEFTERİ — dünya durumu defteri ve K0 kâğıt süreklilik kapısı (TASARIM §5.2, §7.2 K0, D-13, D-22; [YN2] §4.5.13; [GS2] K0.1–K0.19).

Kullanım:
  python dunya_defteri.py --derle --denetle --film <film>     planları çözer → DUNYA_DEFTERI.json + _RAPOR/K0_FILM.json (A07c)
  python dunya_defteri.py --derle --film <film>               yalnız defter
  python dunya_defteri.py --dondur <no>[,<no>…] --film <film> görsel üretildiği an planın çözülmüş durumunu dondurur (uretim.durum_dondu)
  python dunya_defteri.py --komsuluk [--sira 3,1,2] [--kullanici] --film <film>
                                                             kurgu sırası/kesme değişince yeni komşu çiftlerde DONDURULMUŞ olgu eşitliği (Y58)
                                                             (--sira yoksa KURGU/KURGU_PLANI.json "planlar[].no" sırası) → _RAPOR/K0_KOMSULUK.json
  python dunya_defteri.py --gozlenen <gozlem.json> --film <film>
                                                             G1/V3 gözlemlerini ({no: {kapi, an: bas|bit, olgular: {yol: deger}}}) defterle karşılaştırır
Kodda: coz(sahneler, hikaye=None, E=None) → Cozum (planlar{no: {bas, bit, olaylar}}, olaylar, olcumler, sahne_uclari)
Kurallar (yalnız bu araç DUNYA_DEFTERI.json yazar; elle düzenlenmez):
  - Durum yalnız olgudur: karakterler.<id>{mekan, isaret, poz, yuz_yonu, bakis, kostum, kostum_durumu, gorunum, eller{sag, sol: {tutar, yer,
    sekil}}, ifade, duygu{durum, siddet, izler}, gizli_arkasinda}, nesneler.<id>{kimde, el, durum} | {nerede, durum}, mekan_durumu, zaman.
    Sağ/sol karakterin KENDİ sağı/soludur.
  - Miras: bir planın bitişi sonrakinin başlangıcıdır (tek koşan dünya; araya_kesme yalnız kendi öznelerini değiştirir). baslangic_durumu
    "miras" | {"fark": {...}, "neden": "..."} (yalnız zaman_atlama, yeni_sahne ya da kadraj_disi: true) | tam durum (yalnız yeni_sahne).
  - Bitiş = başlangıç + adımların etki'leri (zaman sırasıyla). Nesne ↔ el bağı her adımdan sonra eşitlenir; bir el ≤ 1 nesne, bir nesne ≤ 1 el.
  - SIÇRAMA YAKALAMA (K0, HATA): olgu sıçraması (sonraki klibin başlangıcı öncekinin bitişi değil), nesne ışınlanması (kimde/nerede
    etkisiz ya da nesne fiili olmadan değişti), el değişimi (el alanı el fiili olmadan değişti), kostüm değişimi (olaysız/fiilsiz),
    gerekçesiz fark, sahne sonu ≠ sözleşme çıkışı, hikâye uçları ⊄ sözleşme, kalıcı özelliğin sahne sınırında kaybolması, gün saatinin geri
    gitmesi, yazarın beklediği bitiş ≠ hesaplanan (Y10), araya kesmede başkasının olgusunun değişmesi.
  - Duygu katmanı (BAYRAK): ifade/duygu sahne içinde mirastır; gerekçesiz ifade sıçraması ve ≥ 2 şiddet sıçraması BAYRAK
    (duygu_sicramasi_gerekcesiz); zaman atlamasında şiddet bir azalır.
Çıkış kodları: 0 tamam (K0 GEÇ/BAYRAK) · 1 K0 HATA ya da bozuk girdi · 2 film/SAHNELER yok · 4 kullanım.
"""
import os, sys, json, copy
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "dunya_defteri 1.0"
DEFTER = "DUNYA_DEFTERI.json"
OLGU_KARAKTER = ("mekan", "isaret", "poz", "yuz_yonu", "bakis", "kostum", "kostum_durumu", "gorunum", "eller", "gizli_arkasinda")
DUYGU_ALAN = ("ifade", "duygu")
KALICI = ("kostum", "kostum_durumu", "gorunum")           # sahne sınırında taşınır (K0.8)
GUN_SAATI = ["safak", "sabah", "ogle", "ogleden_sonra", "aksam", "alacakaranlik", "gece", "gece_yarisi"]
FARK_GECERLI = ("zaman_atlama", "yeni_sahne")
NESNE_OLAY = ("nesne_al", "nesne_birak", "nesne_ver", "nesne_el_degis")
BOS_EL = {"tutar": None, "yer": "yanda", "sekil": "serbest"}


# --- yardımcılar -------------------------------------------------------------------------------------------------
def _k(x): return copy.deepcopy(x)


def bos_durum(): return {"karakterler": {}, "nesneler": {}, "mekan_durumu": {}, "zaman": {}}


def hikaye_durumu(h):
    """HIKAYE.json giris/cikis_durumu (varliklar/bolge) → durum nesnesi alt kümesi."""
    if not isinstance(h, dict): return {}
    d = {}
    kar = h.get("karakterler") or h.get("varliklar")
    if isinstance(kar, dict):
        d["karakterler"] = {k: {a: b for a, b in (v or {}).items() if a not in ("bolge", "yer")} for k, v in kar.items()}
    if isinstance(h.get("nesneler"), dict):
        d["nesneler"] = {k: {a: b for a, b in (v or {}).items() if a != "yer"} for k, v in h["nesneler"].items()}
    if isinstance(h.get("mekan_durumu"), dict): d["mekan_durumu"] = dict(h["mekan_durumu"])
    return d


def birlestir(taban, ust):
    """ust'teki alanları taban'a derin uygular (sözlükler birleşir, diğerleri ezilir)."""
    out = _k(taban)
    for k, v in (ust or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict): out[k] = birlestir(out[k], v)
        else: out[k] = _k(v)
    return out


def farklar(beklenen, gercek, yol="", alanlar=None):
    """beklenen'deki her yaprak gercek'te aynı mı? [(yol, beklenen, gercek)]."""
    out = []
    if isinstance(beklenen, dict):
        for k, v in beklenen.items():
            if alanlar is not None and not yol and k not in alanlar: continue
            g = gercek.get(k) if isinstance(gercek, dict) else None
            out += farklar(v, g, f"{yol}.{k}" if yol else k)
        return out
    if isinstance(beklenen, list) and isinstance(gercek, list):
        return [] if sorted(map(str, beklenen)) == sorted(map(str, gercek)) else [(yol, beklenen, gercek)]
    return [] if beklenen == gercek or (beklenen in (None, "") and gercek in (None, "")) else [(yol, beklenen, gercek)]


def olgular(d):
    """Karşılaştırmada kullanılan olgu katmanı (duygu ve ifade ayrı katmandır)."""
    out = {"karakterler": {}, "nesneler": _k(d.get("nesneler") or {}), "mekan_durumu": _k(d.get("mekan_durumu") or {})}
    for k, v in (d.get("karakterler") or {}).items():
        out["karakterler"][k] = {a: _k(b) for a, b in (v or {}).items() if a in OLGU_KARAKTER}
    return out


def iki_yonlu(a, b):
    """İki durumun olgu farkları (iki yönde; yalnız birinde olan alan da farktır)."""
    oa, ob = olgular(a), olgular(b)
    f = farklar(oa, ob); goruldu = {x[0] for x in f}
    for y, bv, av in farklar(ob, oa):
        if y not in goruldu: f.append((y, av, bv))
    return [x for x in f if not (x[1] in (None, "", [], {}) and x[2] in (None, "", [], {}))]


def sicrama_turu(yol):
    p = yol.split(".")
    if p[0] == "nesneler":
        if len(p) > 2 and p[2] == "el": return "el_degisimi", "ters_el"
        if len(p) > 2 and p[2] in ("kimde", "nerede"): return "nesne_isinlanmasi", "nesne_zipladi"
        return "nesne_durum_sicramasi", "nesne_zipladi"
    if p[0] == "karakterler" and len(p) > 2:
        if p[2] == "eller": return ("el_degisimi" if len(p) > 4 and p[4] == "tutar" else "el_sicramasi"), "ters_el"
        if p[2] in KALICI: return "kostum_degisimi" if p[2].startswith("kostum") else "gorunum_sicramasi", "kostum_ziplama"
        if p[2] in ("mekan", "isaret", "poz", "gizli_arkasinda"): return "konum_sicramasi", "karakter_kayboldu"
    return "olgu_sicramasi", "nesne_zipladi"


def ozet(d): return po.imza(olgular(d))


def ozet_metin(d, kim=None):
    s = []
    for k, v in sorted((d.get("karakterler") or {}).items()):
        if kim and k not in kim: continue
        par = [k, str(v.get("isaret") or v.get("mekan") or "?")]
        for el in ("sag", "sol"):
            t = (((v.get("eller") or {}).get(el)) or {}).get("tutar")
            if t: par.append(f"{t} {el} elde")
        if v.get("ifade"): par.append(f"ifade {v['ifade']}")
        du = v.get("duygu") or {}
        if du.get("durum"): par.append(f"duygu {du['durum']} {du.get('siddet', '')}".strip())
        s.append("; ".join(par))
    return " | ".join(s)


# --- etki uygulama ------------------------------------------------------------------------------------------------
def _cozumle(anahtar, d, karakter_idleri):
    p = anahtar.split(".")
    if p[0] in ("mekan_durumu", "zaman"): return [p[0]] + p[1:]
    if p[0] in karakter_idleri or p[0] in d["karakterler"]: return ["karakterler"] + p
    return ["nesneler"] + p


def _yaz(d, yol, v):
    o = d
    for x in yol[:-1]:
        if not isinstance(o.get(x), dict): o[x] = {}
        o = o[x]
    if v is None and yol[-1] in ("nerede", "kimde", "el") and yol[0] == "nesneler": o.pop(yol[-1], None)
    else: o[yol[-1]] = _k(v)


def _el(d, k, e):
    kar = d["karakterler"].setdefault(k, {})
    eller = kar.setdefault("eller", {})
    if not isinstance(eller.get(e), dict): eller[e] = dict(BOS_EL)
    return eller[e]


def _tutan(d, nesne):
    return [(k, e) for k, v in d["karakterler"].items() for e, h in ((v or {}).get("eller") or {}).items()
            if isinstance(h, dict) and h.get("tutar") == nesne]


def esitle(d, nesne_yolu, el_yolu, hedef=None):
    """Etki sonrası nesne↔el bağını eşitler. nesne_yolu: bu adımda nesne alanı değişen nesneler; el_yolu: tutar'ı değişen (k, e, eski)."""
    sorun = []
    for x in nesne_yolu:
        n = d["nesneler"].get(x) or {}
        if n.get("kimde"):
            e = n.get("el")
            for k2, e2 in _tutan(d, x):
                if (k2, e2) != (n["kimde"], e): _el(d, k2, e2)["tutar"] = None
            if e in ("sag", "sol"): _el(d, n["kimde"], e)["tutar"] = x
            n.pop("nerede", None)
        else:
            for k2, e2 in _tutan(d, x): _el(d, k2, e2)["tutar"] = None
    for k, e, eski in el_yolu:
        t = _el(d, k, e).get("tutar")
        if t and t not in nesne_yolu:
            n = d["nesneler"].setdefault(t, {})
            for k2, e2 in _tutan(d, t):
                if (k2, e2) != (k, e): _el(d, k2, e2)["tutar"] = None
            n["kimde"], n["el"] = k, e; n.pop("nerede", None)
        if eski and eski != t and eski not in nesne_yolu and (d["nesneler"].get(eski) or {}).get("kimde") == k:
            n = d["nesneler"][eski]; n.pop("kimde", None); n.pop("el", None)
            if hedef: n["nerede"] = hedef
            else: n["nerede"] = None; sorun.append(eski)
    for k, v in d["karakterler"].items():                           # bir el ≤ 1 nesne zaten yapısal; nesne ≤ 1 el:
        for e, h in ((v or {}).get("eller") or {}).items():
            t = h.get("tutar") if isinstance(h, dict) else None
            if t and len(_tutan(d, t)) > 1: sorun.append(t)
    return sorun


def olay_turu(yol, once, sonra):
    p = yol.split(".")
    if p[0] == "nesneler":
        if p[-1] == "kimde":
            if not once: return "nesne_al"
            if not sonra: return "nesne_birak"
            return "nesne_ver"
        if p[-1] == "nerede": return "nesne_birak"
        if p[-1] == "el": return "nesne_el_degis"
        return "nesne_durum"
    if p[0] == "mekan_durumu": return "mekan_durum"
    if p[0] == "zaman": return "zaman_atla"
    if p[0] == "karakterler" and len(p) > 2:
        a = p[2]
        if a == "kostum": return "kostum_degis"
        if a == "kostum_durumu": return "kostum_durum"
        if a == "gorunum": return "gorunum_degis"
        if a in ("mekan", "isaret", "poz", "yuz_yonu", "gizli_arkasinda"): return "yer_degis"
        if a in DUYGU_ALAN: return "duygu_degis"
        if a == "eller": return "nesne_el_degis" if p[-1] == "tutar" else None
        if a == "bakis": return None
    return None


def _duz(d, yol=""):
    out = {}
    if isinstance(d, dict) and d:
        for k, v in d.items(): out.update(_duz(v, f"{yol}.{k}" if yol else k))
    else: out[yol] = d
    return out


def degisenler(once, sonra):
    a, b = _duz(once), _duz(sonra)
    return [(k, a.get(k), b.get(k)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k) and k]


# --- çözüm --------------------------------------------------------------------------------------------------------
class Cozum:
    def __init__(self):
        self.planlar, self.olaylar, self.olcumler, self.sahne_uclari, self.cizgiler = {}, [], [], {}, {}
        self.baslangic = None


def _plan_listesi(sahneler):
    pl = [p for p in sahneler.get("sahneler") or [] if isinstance(p, dict)]
    return sorted(pl, key=lambda p: (float(p.get("sira", p.get("no", 0)) or 0), p.get("no") or 0))


def _sahne_durumu(x, hikaye, sid, uc):
    if isinstance(x, dict): return x
    if isinstance(x, str) and "#" in x and isinstance(hikaye, dict):
        for s in hikaye.get("sahneler") or []:
            if s.get("id") == sid: return hikaye_durumu(s.get(uc))
    return {}


def _hikaye_sahne(hikaye, sid):
    for s in (hikaye or {}).get("sahneler") or []:
        if s.get("id") == sid: return s
    return {}


def _zaman_sira(z):
    try: return (int(z.get("gun") or 0), GUN_SAATI.index(z.get("gun_saati") or z.get("saat")))
    except (ValueError, AttributeError): return None


def coz(sahneler, hikaye=None, E=None, baslangic=None):
    """SAHNELER v2 (bellekte) → Cozum. Planlar kurgu sırasıyla (sira) tek koşan dünyada çözülür."""
    E = E or po.esik(); fil = po.fiiller(); C = Cozum()
    olc = C.olcumler.append
    gruplar = sahneler.get("sahne_gruplari") or {}
    kid = set((sahneler.get("karakterler") or {}).keys()) | set(((hikaye or {}).get("karakterler") or {}).keys())
    dunya = {}                                      # zaman çizgisi → koşan durum
    son_sahne, son_zaman, sahne_son_plan, sahne_ilk = {}, {}, {}, {}
    olay_n = [0]
    planlar = _plan_listesi(sahneler)
    for p in planlar:
        no = p.get("no"); z = p.get("zanaat") or {}; sid = z.get("sahne_grubu")
        sg = gruplar.get(sid) or {}; cz = sg.get("zaman_cizgisi") or "ana"
        C.cizgiler.setdefault(cz, [])
        if sid not in C.cizgiler[cz]: C.cizgiler[cz].append(sid)
        zn = z.get("zincir") or {}; gt = zn.get("gecis_turu")
        yeni_sahne = son_sahne.get(cz) != sid
        giris = _sahne_durumu(sg.get("giris_durumu"), hikaye, sid, "giris_durumu")
        onceki = dunya.get(cz)
        atlama = gt == "zaman_atlama" or (yeni_sahne and ((sg.get("zaman") or {}).get("atlama") or "yok") != "yok")
        # 1) başlangıç
        if onceki is None:
            bas = birlestir(baslangic or bos_durum(), giris)
        elif yeni_sahne:
            bas = birlestir(onceki, giris)
            for kim, kv in (giris.get("karakterler") or {}).items():          # K0.8 kalıcı özellik sahne sınırında
                for a in KALICI:
                    if a in kv and a in ((onceki["karakterler"].get(kim)) or {}) and onceki["karakterler"][kim][a] != kv[a] and not atlama:
                        olc(po.m("kalici_ozellik_kayboldu", "HATA", no, sahne=sid, kim=kim, alan=a, olcu=kv[a],
                                 esik=onceki["karakterler"][kim][a], tur="kostum_degisimi" if a.startswith("kostum") else "gorunum_sicramasi",
                                 kok_neden="kostum_ziplama", kural="K0.8",
                                 neden="önceki sahnenin bitişindeki kalıcı özellik yeni sahnede olaysız değişti"))
            for nid, nv in (giris.get("nesneler") or {}).items():
                eski = (onceki.get("nesneler") or {}).get(nid)
                if eski and not atlama:
                    for y, b, g in farklar({k: v for k, v in nv.items() if k in ("kimde", "el", "durum")}, eski):
                        olc(po.m("kalici_ozellik_kayboldu", "HATA", no, sahne=sid, kim=nid, alan=y, olcu=b, esik=g, kural="K0.8",
                                 tur=sicrama_turu("nesneler." + nid + "." + y)[0], kok_neden="nesne_zipladi",
                                 neden="taşınan nesne sahne sınırında olaysız değişti"))
            if atlama: _duygu_azalt(bas)
            if son_zaman.get(cz) and _zaman_sira(sg.get("zaman") or {}) and _zaman_sira(son_zaman[cz]) and cz == "ana" \
                    and _zaman_sira(sg["zaman"]) < _zaman_sira(son_zaman[cz]):
                olc(po.m("gun_saati_geri", "HATA", no, sahne=sid, olcu=sg["zaman"], esik=son_zaman[cz], kural="K0.9",
                         kok_neden="isik_zipladi", neden="ana zaman çizgisinde gün saati geri gitti (geçmiş ayrı çizgide olmalı)"))
        else:
            bas = _k(onceki)
        if yeni_sahne:
            sahne_ilk[sid] = no
            if sg.get("zaman"): son_zaman[cz] = sg["zaman"]
        bd = z.get("baslangic_durumu", "miras")
        if isinstance(bd, dict) and "fark" in bd:
            gerekce = bd.get("neden") and (gt in FARK_GECERLI or bd.get("kadraj_disi"))
            if not gerekce:
                olc(po.m("gerekcesiz_fark", "HATA", no, sahne=sid, olcu=sorted(_duz(bd["fark"])), kural="K0.2/Y12", kok_neden="nesne_zipladi",
                         tur="olgu_sicramasi", neden="fark yalnız zaman_atlama, yeni_sahne ya da kadraj dışı gerekçesiyle (neden + kadraj_disi) yazılır"))
            once = _k(bas)
            for k, v in _duz(bd["fark"]).items(): _yaz(bas, _cozumle(k, bas, kid), v)
            for y, a, b in degisenler(olgular(once), olgular(bas)):
                C.olaylar.append(_olay(olay_n, no, None, y, a, b, gerekce=bd.get("neden")))
        elif isinstance(bd, dict):
            if not (yeni_sahne and gt in ("yeni_sahne", None)) and onceki is not None:
                for y, b, g in iki_yonlu(onceki, birlestir(onceki, bd)):
                    t, kn = sicrama_turu(y)
                    olc(po.m("olgu_sicramasi", "HATA", no, sahne=sid, yol=y, olcu=b, esik=g, tur=t, kural="K0.1/Y11", kok_neden=kn,
                             neden="planın başlangıcı önceki klibin bitişi değil (başlangıç karesi = önceki bitiş)"))
            bas = birlestir(bas, bd)
        # 2) duygu: plan başı ifade
        oy = z.get("oyunculuk") or {}
        for kim, o in oy.items():
            di = (o or {}).get("dis_ifade") or {}
            k = bas["karakterler"].setdefault(kim, {})
            if di.get("bas"):
                if k.get("ifade") and k["ifade"] != di["bas"] and not yeni_sahne and not atlama and not (o or {}).get("ifade_gecis_neden"):
                    olc(po.m("duygu_sicramasi_gerekcesiz", "BAYRAK", no, sahne=sid, kim=kim, olcu=di["bas"], esik=k["ifade"], kural="K0/D-22",
                             neden="önceki planın bitiş ifadesi bu planın başında yok (gerekçe: oyunculuk.<k>.ifade_gecis_neden)"))
                k["ifade"] = di["bas"]
            if isinstance(o.get("duygu"), dict):
                eski = (k.get("duygu") or {}).get("siddet")
                yeni = o["duygu"].get("siddet")
                if isinstance(eski, int) and isinstance(yeni, int) and abs(yeni - eski) >= 2 and not atlama and not o.get("ifade_gecis_neden"):
                    olc(po.m("duygu_sicramasi_gerekcesiz", "BAYRAK", no, sahne=sid, kim=kim, olcu=yeni, esik=eski, kural="K0/D-22",
                             neden="duygu şiddeti olaysız ≥ 2 sıçradı"))
                k["duygu"] = birlestir(k.get("duygu") or {}, o["duygu"])
        # 3) adımlar
        d = _k(bas); pol = []
        ozneler = set()
        adimlar = sorted([a for a in z.get("eylem_zinciri") or [] if isinstance(a, dict)], key=lambda a: (a.get("bas") or 0))
        for a in adimlar:
            ozneler.add(a.get("ozne"))
        for a in adimlar:
            etki = a.get("etki") or {}
            f = fil.get(a.get("fiil")) or {}
            if not etki:
                if f.get("durum_degistirir") and a.get("tur") == "fiziksel":
                    olc(po.m("etkisiz_fiziksel_adim", "BAYRAK", no, adim=a.get("id"), olcu=a.get("fiil"), kural="K0.5",
                             neden="durumu değiştirmesi beklenen fiziksel adımın etki'si yok"))
                continue
            once = _k(d); nesne_y, el_y = [], []
            for k, v in etki.items():
                yol = _cozumle(k, d, kid)
                if yol[0] == "nesneler" and len(yol) > 2 and yol[2] in ("kimde", "el", "nerede"): nesne_y.append(yol[1])
                if yol[0] == "karakterler" and len(yol) > 4 and yol[2] == "eller" and yol[4] == "tutar":
                    el_y.append((yol[1], yol[3], _el(d, yol[1], yol[3]).get("tutar")))
                if yol[0] == "karakterler" and len(yol) > 2 and yol[1] not in d["karakterler"]:
                    olc(po.m("bilinmeyen_varlik", "BAYRAK", no, adim=a.get("id"), olcu=yol[1]))
                _yaz(d, yol, v)
            hedef = a.get("hedef") if a.get("fiil") == "birakir" else None
            for x in esitle(d, nesne_y, el_y, hedef):
                olc(po.m("el_nesne_celiskisi", "HATA", no, adim=a.get("id"), olcu=x, kural="K0.6", kok_neden="ters_el",
                         neden="nesnenin yeri belirsiz ya da iki elde"))
            olay_f = f.get("olay")
            for y, x, yv in degisenler(olgular(once), olgular(d)) + [c for c in degisenler(_duygu(once), _duygu(d))]:
                t = olay_turu(y, x, yv)
                if t is None: continue
                if t in NESNE_OLAY and y.startswith("nesneler") and olay_f not in NESNE_OLAY:
                    tur, kn = ("el_degisimi", "ters_el") if y.endswith(".el") else ("nesne_isinlanmasi", "nesne_zipladi")
                    olc(po.m("nesne_fiilsiz_degisti", "HATA", no, adim=a.get("id"), yol=y, olcu=yv, esik=x, tur=tur, kok_neden=kn,
                             kural="K0.6/Y15–Y16", neden=f"'{a.get('fiil')}' bir el/nesne fiili değil; nesne kimde/el yalnız el fiiliyle değişir"))
                if t.startswith("kostum") and olay_f not in ("kostum_degis", "kostum_durum"):
                    olc(po.m("kostum_fiilsiz_degisti", "HATA", no, adim=a.get("id"), yol=y, olcu=yv, esik=x, tur="kostum_degisimi",
                             kok_neden="kostum_ziplama", kural="K0.8", neden="kostüm yalnız kostüm fiiliyle (kapusonu_indirir …) değişir"))
                if z.get("zincir", {}).get("gecis_turu") == "araya_kesme" and y.startswith("karakterler.") and y.split(".")[1] not in ozneler:
                    olc(po.m("araya_kesme_yabanci_olgu", "HATA", no, adim=a.get("id"), yol=y, kural="§4.5.13#3", kok_neden="nesne_zipladi"))
                ev = _olay(olay_n, no, a.get("id"), y, x, yv, tur=t); C.olaylar.append(ev); pol.append(ev["id"])
        # 4) bitiş ifadesi
        for kim, o in oy.items():
            di = (o or {}).get("dis_ifade") or {}
            if di.get("bit"): d["karakterler"].setdefault(kim, {})["ifade"] = di["bit"]
        bitis = z.get("bitis_durumu")
        if isinstance(bitis, dict):
            for y, b, g in farklar(olgular(bitis) if "karakterler" in bitis or "nesneler" in bitis else bitis, olgular(d)):
                olc(po.m("bitis_hesaba_uymuyor", "HATA", no, yol=y, olcu=g, esik=b, kural="Y10", kok_neden="nesne_zipladi",
                         neden="yazarın beklediği bitiş durumu etkilerden hesaplanana eşit değil"))
        C.planlar[str(no)] = {"no": no, "kod": z.get("kod"), "sahne": sid, "cizgi": cz, "bas": bas, "bit": d, "olaylar": pol,
                              "bas_ozet": ozet(bas), "bit_ozet": ozet(d), "bas_metin": ozet_metin(bas), "bit_metin": ozet_metin(d)}
        dunya[cz] = d; son_sahne[cz] = sid; sahne_son_plan[sid] = no
    # 5) sahne uçları
    for sid, sg in gruplar.items():
        if sid not in sahne_son_plan: continue
        cikis = _sahne_durumu(sg.get("cikis_durumu"), hikaye, sid, "cikis_durumu")
        son = C.planlar[str(sahne_son_plan[sid])]["bit"]; ilk = C.planlar[str(sahne_ilk[sid])]["bas"]
        for y, b, g in farklar(olgular(cikis), olgular(son)):
            t, kn = sicrama_turu(y)
            olc(po.m("sahne_cikisi_sozlesmeye_uymuyor", "HATA", sahne_son_plan[sid], sahne=sid, yol=y, olcu=g, esik=b, tur=t, kok_neden=kn,
                     kural="K0.3/Y13", neden="sahnenin son planının bitişi sözleşmedeki cikis_durumu değil"))
        hs = _hikaye_sahne(hikaye, sid); esit = True
        for uc, gercek, ilk_son in (("giris_durumu", ilk, sahne_ilk[sid]), ("cikis_durumu", son, sahne_son_plan[sid])):
            hk = hikaye_durumu(hs.get(uc)) if hs else {}
            for y, b, g in farklar(olgular(hk), olgular(gercek)) if hk else []:
                esit = False
                olc(po.m("hikaye_ucu_sozlesmede_yok", "HATA", ilk_son, sahne=sid, uc=uc, yol=y, olcu=g, esik=b, kural="K0.3/Y57",
                         kok_neden="bilgi_durumu_ihlali", neden="HIKAYE.json'daki sahne ucu olgusu yönetmenin sözleşmesinde değişmiş"))
        C.sahne_uclari[sid] = {"giris": ozet(ilk), "cikis": ozet(son), "hikaye_esit": esit}
    return C


def _duygu(d):
    return {"karakterler": {k: {a: v.get(a) for a in DUYGU_ALAN if a in v} for k, v in (d.get("karakterler") or {}).items()}}


def _duygu_azalt(d):
    for v in (d.get("karakterler") or {}).values():
        du = v.get("duygu")
        if isinstance(du, dict) and isinstance(du.get("siddet"), int): du["siddet"] = max(0, du["siddet"] - 1)


def _olay(sayac, no, adim, yol, once, sonra, tur=None, gerekce=None):
    sayac[0] += 1
    p = yol.split(".")
    kim = p[1] if len(p) > 1 and p[0] in ("karakterler", "nesneler") else p[0]
    o = {"id": f"O-{sayac[0]:04d}", "plan": str(no), "adim": adim, "tur": tur or olay_turu(yol, once, sonra), "kim": kim,
         "yol": yol, "once": once, "deger": sonra}
    if gerekce: o["gerekce"] = gerekce
    return o


# --- dosya işleri -------------------------------------------------------------------------------------------------
def _oku(kok):
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(s, dict): return None, None
    return s, ortak.json_oku(os.path.join(kok, "HIKAYE.json"))


def baslangic_durumu(kok, hikaye):
    """Film başı: evrendeki DURUM_SON.json (varsa) — yoksa boş; sahne sözleşmesi üstüne biner."""
    seri = (hikaye or {}).get("evren")
    if seri:
        try:
            p = os.path.join(ortak.yollar()["evren_kok"], seri, "DURUM_SON.json")
            d = ortak.json_oku(p)
            if isinstance(d, dict): return birlestir(bos_durum(), d.get("durum") or d), f"EVREN/{seri}/DURUM_SON.json"
        except ortak.YolYok: pass
    return bos_durum(), None


def ses_alanlari(C, sahneler):
    out = {}
    for sid, sg in (sahneler.get("sahne_gruplari") or {}).items():
        pl = [v for v in C.planlar.values() if v["sahne"] == sid]
        if not pl: continue
        d = pl[0]["bas"]; mk = sg.get("mekan")
        kat = [f"mekan.{mk}.{k}={v}" for k, v in sorted((d.get("mekan_durumu") or {}).items())]
        if (sg.get("zaman") or {}).get("hava"): kat.append(f"hava={sg['zaman']['hava']}")
        sur = sorted(f"{n}:{v.get('durum')}" for n, v in (d.get("nesneler") or {}).items() if v.get("durum") in ("yanik", "acik", "calisiyor"))
        out[sid] = {"yatak_katmanlari": kat, "surekli_nesne_sesleri": sur}
    return out


def defter_kur(kok, sahneler, hikaye, C, kaynak_bas, eski=None):
    eski = eski or {}
    planlar = {}
    for k, v in C.planlar.items():
        planlar[k] = {"kaynak": f"SAHNELER.json#{k}", "kod": v["kod"], "sahne": v["sahne"], "bas": v["bas_ozet"], "bit": v["bit_ozet"],
                      "bas_ozet": v["bas_metin"], "bit_ozet": v["bit_metin"], "olaylar": v["olaylar"],
                      "durum": {"bas": v["bas"], "bit": v["bit"]}}
    return {"_surum": 1, "_uretim": po.zarf("A07c", SURUM, "GEC", po.imza(sahneler.get("sahneler"))),
            "film": sahneler.get("film") or os.path.basename(kok), "evren": (hikaye or {}).get("evren"),
            "baslangic": {"kaynak": kaynak_bas, "durum": C.baslangic},
            "zaman_cizgileri": C.cizgiler, "planlar": planlar, "olaylar": C.olaylar, "sahne_uclari": C.sahne_uclari,
            "hikaye": {"kaynak": "HIKAYE.json#bilgi", "salt_okunur": True}, "ses_alanlari": ses_alanlari(C, sahneler),
            "gozlenen": eski.get("gozlenen") or {}, "dondurulmus": eski.get("dondurulmus") or {}}


def derle(kok, denetle=False, yaz=True):
    s, h = _oku(kok)
    if s is None: return None, None, [po.m("sahneler_yok", "HATA")]
    if int(s.get("_surum", 1) or 1) < 2:
        return None, None, [po.m("sahneler_v1", "HATA", neden="dünya defteri v2 SAHNELER ister (zanaat alanlı)")]
    bas, kaynak = baslangic_durumu(kok, h)
    C = coz(s, h, baslangic=bas); C.baslangic = bas
    eski = ortak.json_oku(os.path.join(kok, DEFTER), {}) or {}
    D = defter_kur(kok, s, h, C, kaynak, eski)
    D["_uretim"]["sonuc"] = "HATA" if any(o["seviye"] == "HATA" for o in C.olcumler) else "GEC"
    if yaz: ortak.atomik_yaz(os.path.join(kok, DEFTER), D)
    return D, C, C.olcumler


def yeniden_yaz_kuyrugu(kok, olcumler, kapi="K0", asama="A07c"):
    """K0 HATA'ları → KUYRUK/YENIDEN_YAZ.json (aynı sahnenin yönetmeni)."""
    try: import kuyruk
    except Exception: return None
    md = []
    for o in olcumler:
        if o.get("seviye") != "HATA": continue
        konum = {}
        if o.get("sahne"): konum["sahne"] = o["sahne"]
        if isinstance(o.get("plan"), int) and o["plan"] > 0: konum["plan"] = o["plan"]
        if not konum: continue
        kn = o.get("kok_neden") or "nesne_zipladi"
        md.append({"konum": konum, "kapi": kapi, "madde": o["madde"], "kok_neden": po.kok_normal(kn),
                   "yazar": "yonetmen", "oneri": (o.get("neden") or o["madde"]) + (f" [{kn}]" if po.kok_normal(kn) != kn else ""),
                   "tur": po.gorev().get("tur_no") or 1})
    if not md: return None
    try: return kuyruk.yaz_ekle(kok, md, asama)
    except Exception as e: print(f"!! YENIDEN_YAZ yazılamadı: {e}", flush=True); return None


def dondur(kok, nolar):
    D = ortak.json_oku(os.path.join(kok, DEFTER))
    if not isinstance(D, dict): D, _, _ = derle(kok)
    if not D: return 2
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    import kapi
    for no in nolar:
        p = D["planlar"].get(str(no))
        if not p: print(f"!! plan {no} defterde yok", flush=True); return 1
        D["dondurulmus"][str(no)] = {"bas": p["bas"], "bit": p["bit"], "durum": p["durum"], "zaman": kapi.simdi()}
        for pl in (s or {}).get("sahneler") or []:
            if pl.get("no") == no: pl.setdefault("uretim", {})["durum_dondu"] = {"bas": p["bas"], "bit": p["bit"]}
    ortak.atomik_yaz(os.path.join(kok, DEFTER), D)
    if s: ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
    print(f"donduruldu: {', '.join(map(str, nolar))}", flush=True)
    return 0


def komsuluk(kok, sira=None, kullanici=False):
    D = ortak.json_oku(os.path.join(kok, DEFTER))
    if not isinstance(D, dict): print("!! DUNYA_DEFTERI.json yok; önce --derle", flush=True); return 2, None
    if not sira:
        kp = ortak.json_oku(os.path.join(kok, "KURGU", "KURGU_PLANI.json"), {}) or {}
        sira = [x.get("no") for x in kp.get("planlar") or [] if isinstance(x, dict)]
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
    gt = {p.get("no"): ((p.get("zanaat") or {}).get("zincir") or {}).get("gecis_turu") for p in s.get("sahneler") or []}
    olc = []
    for a, b in zip(sira, sira[1:]):
        if gt.get(b) in FARK_GECERLI: continue
        da = D["dondurulmus"].get(str(a)) or D["planlar"].get(str(a)); db = D["dondurulmus"].get(str(b)) or D["planlar"].get(str(b))
        if not da or not db:
            olc.append(po.m("komsu_olculemedi", "OLCULEMEDI", b, olcu=[a, b])); continue
        for y, x, yv in iki_yonlu(da["durum"]["bit"], db["durum"]["bas"]):
            t, kn = sicrama_turu(y)
            olc.append(po.m("dondurulmus_komsu_sicramasi", "BAYRAK" if kullanici else "HATA", b, onceki=a, yol=y, olcu=yv, esik=x,
                            tur=t, kural="Y58/K0.17", kok_neden=kn, neden="yeni komşu çiftte dondurulmuş olgular eşit değil"))
    yol, r = po.rapor_yaz(kok, "K0", "KOMSULUK", olc, asama="A16", arac=SURUM, birimler=list(sira[1:]))
    return po.cikis(r), r


def gozlenen(kok, dosya):
    D = ortak.json_oku(os.path.join(kok, DEFTER)); g = ortak.json_oku(dosya)
    if not isinstance(D, dict) or not isinstance(g, dict): print("!! defter ya da gözlem dosyası yok", flush=True); return 2
    for no, v in g.items():
        p = D["planlar"].get(str(no))
        if not p or not isinstance(v, dict): continue
        dur = p["durum"]["bit" if v.get("an", "bit") == "bit" else "bas"]
        fark = {}
        for y, deger in (v.get("olgular") or {}).items():
            beklenen = po.al(dur, y)
            if beklenen != deger: fark[y] = {"beklenen": beklenen, "gozlenen": deger}
        D["gozlenen"].setdefault(str(no), {})[v.get("kapi", "V3")] = {"rapor": v.get("rapor"), "uyum": not fark, "fark": fark}
    ortak.atomik_yaz(os.path.join(kok, DEFTER), D)
    return 0


def main(argv):
    if not argv or "-h" in argv or "--help" in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film"))
    if "--dondur" in argv:
        x = po.arg_al(argv, "--dondur")
        try: nolar = [int(n) for n in (x or "").split(",") if n]
        except ValueError: print(__doc__); return 4
        return dondur(kok, nolar)
    if "--komsuluk" in argv:
        x = po.arg_al(argv, "--sira")
        sira = [int(n) for n in x.split(",")] if x else None
        k, r = komsuluk(kok, sira, "--kullanici" in argv)
        if r: po.yaz_ozet(r, "K0 komşuluk")
        return k
    if "--gozlenen" in argv: return gozlenen(kok, po.arg_al(argv, "--gozlenen"))
    if "--derle" not in argv and "--denetle" not in argv: print(__doc__); return 4
    if not os.path.isfile(os.path.join(kok, "SAHNELER.json")): print("!! SAHNELER.json yok (önce plan_birlestir)", flush=True); return 2
    D, C, olc = derle(kok, yaz="--derle" in argv)
    if "--denetle" in argv:
        nolar = [p.get("no") for p in (ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}).get("sahneler") or []]
        yol, r = po.rapor_yaz(kok, "K0", "FILM", olc, asama="A07c", arac=SURUM, birimler=nolar,
                              ek={"sahne_uclari": C.sahne_uclari if C else {}})
        yeniden_yaz_kuyrugu(kok, olc)
        po.yaz_ozet(r, "K0")
        return po.cikis(r)
    return 1 if any(o["seviye"] == "HATA" and o["madde"] in ("sahneler_yok", "sahneler_v1") for o in olc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
