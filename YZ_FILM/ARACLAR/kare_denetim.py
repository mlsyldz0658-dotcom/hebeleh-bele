"""KARE DENETİM — G1 başlangıç karesi kapısı: yerel ölçüm, kör görev, kod kararı, hakem, kapak serbest ölçümü (TASARIM §6.5, §7.2 G1, D-14, D-16).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"; tur GOREV.json'dan ya da --tur):
  python kare_denetim.py --olc [--yerel] --film <film> [--tur N]
        SIRALI_GORSEL/_ADAYLAR/NNN_<aday>.jpg → _RAPOR/G1/olcum_t<tur>/<NNN_aday>.json; açık teknik HATA'lı aday elenir; kalanlar için
        kör paket _KOR_PAKET/g1_t<tur>/<i>/ (kare-tarifcisi·g1 görevlerinin GIRDI'si; ≤ 12 görsel/görev)
  python kare_denetim.py --kor-gorev --film <film> [--tur N]    yalnız kör paketi yeniden kurar
  python kare_denetim.py --karar --film <film> [--tur N]
        beklenen ↔ yerel ↔ kör alan alan (§7.2 G1 tablosu) → aday kararı → plan seçimi → _RAPOR/G1_P<n>_B<k>.json (aday ayrıntısı),
        _RAPOR/G1_FILM_t<tur>.json (kapı), seçilen GEÇ kare SIRALI_GORSEL/NNN.jpg (+ SHA1 → SAHNELER denetim.G1 ve uretim.gorsel),
        öteki adaylar SIRALI_GORSEL/ALTERNATIFLER/ (kopya; silme yok), animatik tur 1 için en iyi kimlik-HATA'sız aday
        SIRALI_GORSEL/_ONIZLEME/NNN.jpg (D-14), HATA'lı planlar KUYRUK/YENIDEN_URET.json (tur: gorsel, CORRECTION şablonuyla),
        dünya defterine dondurma ve kör gözlem (gozlenen); sonra kapak kör paketi hazırlanır (kapak.kor_paketi).
  python kare_denetim.py --hakem <HAKEM_G1.json> --film <film> [--tur N]
        sureklilik-denetcisi·hakem kararları: [{plan, aday?, alan, karar: GEC|HATA, gerekce}]. Yalnız tek kaynaklı BAYRAK ve ÖLÇÜLEMEDİ
        alanları değişir; iki kaynaklı HATA'ya GEÇ yazılırsa REDDEDİLİR (kayıt _RAPOR/G1/HAKEM_t<tur>.json). Gerekçesiz karar reddedilir.
  python kare_denetim.py --serbest <gorsel> [--beklenen <json>] --film <film>    kapak/serbest kare ölçümü (yerel; kapı yok)
  Kodda: import kare_denetim as kd
    kd.video_hazir(film, no) → (bool, neden)    videoya yalnız G1 GEÇ + SHA1'i eşleşen kare gider (D-15, §1.5 kural 6)
    kd.aday_karari(alanlar) → GEC | BAYRAK | HATA · kd.degerlendir(yerel, kor_sonuclari, beklenen, cevap, medyan) → [madde]
Karar kuralları (D-16): iki kaynağın HATA'sı HATA; tek kaynak BAYRAK; ölçülemeyen BAYRAK; ÖLÇÜLEMEDİ asla GEÇ değildir. Yalnız yerelin
  ölçebildiği alanlar (en-boy, yüz sayısı, kimlik, kadraj sırası) tek başına HATA verebilir (tablo). Seçim sırası: (1) BAYRAK sayısı az,
  (2) ifade uyumu, (3) kimlik fark payı yüksek, (4) mekân benzerliği yüksek, (5) keskinlik yüksek.
Çıkış kodları: 0 tamam (kapı sonucu raporda) · 1 girdi/program hatası · 2 aday yok · 4 kullanım.
"""
import os, sys, re, json, glob, shutil, hashlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kare_denetim 1.0"
ADAY = re.compile(r"^(\d{3,})_([a-z][a-z0-9]*)\.jpg$")
SIRA = {"GEC": 0, "BAYRAK": 1, "HATA": 2}
KIMLIK_ALANLARI = ("kimlik", "yanlis_kisi", "fazla_kisi", "kadraj_sirasi")
YALNIZ_YEREL_H = ("teknik", "fazla_kisi", "kimlik", "yanlis_kisi", "kadraj_sirasi")


def sha1(yol):
    h = hashlib.sha1()
    with open(yol, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def _po():
    import plan_ortak as po
    return po


def adaylar(kok):
    """{no: [(aday, yol)]} — _ADAYLAR'daki NNN_<aday>.jpg dosyaları."""
    out = {}
    for p in sorted(glob.glob(os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "*.jpg"))):
        m = ADAY.match(os.path.basename(p))
        if m: out.setdefault(int(m.group(1)), []).append((m.group(2), p))
    return out


def _planlar(S): return {p.get("no"): p for p in (S or {}).get("sahneler") or [] if isinstance(p, dict)}


# --- beklenen --------------------------------------------------------------------------------------------------
def beklenen(kok, plan, S, ev, hik=None):
    import istem_derle_gorsel as idg, olcum
    z = plan.get("zanaat") or {}; der = plan.get("_derlenir") or {}
    sg = (S.get("sahne_gruplari") or {}).get(z.get("sahne_grubu")) or {}
    hik = hik if hik is not None else (ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {})
    kad = [k for k in z.get("kadrajdakiler") or [] if isinstance(k, dict) and k.get("id")]
    def tur(kid):
        c = ev.karakter(kid)
        if c.get("tur"): return c["tur"]
        return "yaratik" if ((hik.get("karakterler") or {}).get(kid) or {}).get("rol") == "yaratik" else "insan"
    insan = [k["id"] for k in kad if tur(k["id"]) != "yaratik"]
    yaratik = [k["id"] for k in kad if tur(k["id"]) == "yaratik"]
    yuz_acisi = {k["id"]: k.get("yuz_acisi") or "on" for k in kad}
    gorunur = [k["id"] for k in kad if k["id"] in insan and yuz_acisi[k["id"]] not in ("sirt", "arka", "gorunmez") and k.get("olcek") != "el"]
    dur = idg.defter_durumu(kok, plan.get("no"))
    eller = {}
    for kid in [k["id"] for k in kad]:
        e = (((dur.get("karakterler") or {}).get(kid) or {}).get("eller")) or {}
        eller[kid] = {el: (e.get(el) or {}).get("tutar") for el in ("sag", "sol")}
    nesne_ad = {n: _kisa(ev.nesne_en(n)) for e in eller.values() for n in e.values() if n}
    gerek = [g for g in der.get("gorunmesi_gerekenler") or [] if g not in [k["id"] for k in kad]]
    gorunen = [{"id": g, "ad": _kisa(ev.nesne_en(g)) if ev.nesne(g) else idg._ad(g)} for g in gerek]
    yas = [y for y in list(sg.get("yasaklar") or []) + list(z.get("yasaklar") or []) if isinstance(y, str)]
    try:
        import evren
        ne_yok = evren.ne_yok_kelimeleri(film=kok)
    except Exception: ne_yok = []
    ifade = {}
    for kid in [k["id"] for k in kad]:
        bas = (((z.get("oyunculuk") or {}).get(kid) or {}).get("dis_ifade") or {}).get("bas")
        _, kor_d = idg.ifade_en(bas) if bas else (None, None)
        if kor_d: ifade[kid] = kor_d
    dk = der.get("dinleyen_agiz")
    konusan = [k["id"] for k in kad if k.get("konusur")]
    agiz = list(konusan) + [k for k in insan if dk == "kapali" or (isinstance(dk, dict) and dk.get(k) == "kapali")]
    banka = {}
    for kid in (S.get("karakterler") or {}):
        b = ev.banka_yolu(kid)
        if b and os.path.isfile(b): banka[kid] = b
    cal = (ev.kalibrasyon() or {}).get("karakterler") or {}
    return {"no": plan.get("no"), "kadrajdakiler": [k["id"] for k in kad], "insan": insan, "yaratik_ids": yaratik,
            "yuz_acisi": yuz_acisi, "gorunur_yuz": gorunur, "eller": eller, "nesne_ad": nesne_ad, "gorunen": gorunen,
            "yasaklar": yas, "ne_yok": ne_yok, "ifade": ifade, "konusan": konusan, "agiz_kapali": sorted(set(agiz)),
            "kadraj_sirasi": [x for x in der.get("kadraj_sirasi") or [] if x in gorunur],
            "kadraj_konumu": {k: olcum.ucte_bir_normal(v) for k, v in (der.get("kadraj_konumu") or {}).items()},
            "bakis": der.get("bakis_kadrajda") or {}, "isik": der.get("isik_kadrajda"), "ayna_yasak": der.get("ayna_yasak", True),
            "acik_parmak": der.get("acik_parmak") or {}, "yakin_el": (z.get("kamera") or {}).get("kadraj") in ("D", "Y", "CY"),
            "plan_tipi": z.get("plan_tipi"), "banka": banka, "kalibrasyon": {k: v for k, v in cal.items() if k in insan},
            "yaw_isareti": (ev.kalibrasyon() or {}).get("yaw_isareti", 1),
            "yaratik": [{"id": y, "sorgu": (ev.karakter(y).get("olcum") or {}).get("bulucu_sorgu")} for y in yaratik],
            "nesneler": [{"id": n, "sorgu": ev.nesne_en(n)} for n in nesne_ad],
            "ebeveyn": ebeveyn_yolu(kok, plan, S, ev), "sahne_ilk": sahne_ilk_kare(kok, plan, S)}


def _kisa(t):
    t = re.sub(r"^(a|an|the)\s+", "", str(t).strip(), flags=re.I)
    return "a " + " ".join(t.split()[:5])


def ebeveyn_yolu(kok, plan, S, ev):
    for r in ((plan.get("uretim") or {}).get("gorsel") or {}).get("referanslar") or []:
        if r.startswith("plaka:"):
            mid, pid = (r.split(":", 1)[1].split("@")[0].split("/") + [""])[:2]
            return ev.plaka_yolu(mid, pid)
        if r.startswith("plan:"):
            p = os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % int(float(r.split(":")[1].split("@")[0])))
            return p if os.path.isfile(p) else None
        if r.startswith("ana_kare:"):
            kur = r.split(":", 1)[1].split("@")[0]; sg = (plan.get("zanaat") or {}).get("sahne_grubu")
            for q in S.get("sahneler") or []:
                qz = q.get("zanaat") or {}
                if qz.get("sahne_grubu") == sg and (qz.get("kamera") or {}).get("kurulum") == kur and q.get("no") != plan.get("no") \
                        and ((qz.get("zincir") or {}).get("baslangic") in ("ana_kare", "kart")):
                    p = os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % q["no"])
                    if os.path.isfile(p): return p
    return None


def sahne_ilk_kare(kok, plan, S):
    sg = (plan.get("zanaat") or {}).get("sahne_grubu")
    for q in sorted(S.get("sahneler") or [], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0)):
        if q.get("no") == plan.get("no"): return None
        if (q.get("zanaat") or {}).get("sahne_grubu") == sg and ((q.get("denetim") or {}).get("G1") or {}).get("sonuc") == "GEC":
            p = os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % q["no"])
            if os.path.isfile(p): return p
    return None


def kor_baglami(b):
    return {"insanlar": b["insan"], "kisiler": [{"id": k, "yuz_acisi": b["yuz_acisi"].get(k), "konum": b["kadraj_konumu"].get(k)} for k in b["kadrajdakiler"]],
            "eller": b["eller"], "nesne_ad": b["nesne_ad"], "gorunmesi_gerekenler": b["gorunen"], "yasaklar": b["yasaklar"],
            "ne_yok": b["ne_yok"], "ifade": b["ifade"], "agiz_kapali": b["agiz_kapali"], "acik_parmak": b["acik_parmak"],
            "yakin_el": b["yakin_el"]}


# --- yerel ölçüm + kör görev ----------------------------------------------------------------------------------
def _olcum_yolu(kok, tur, no, aday): return os.path.join(kok, "_RAPOR", "G1", f"olcum_t{tur}", "%03d_%s.json" % (no, aday))


def olc(kok, tur, arka=None):
    import olcum, istem_derle_gorsel as idg
    S = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(S, dict): print("!! SAHNELER.json yok", flush=True); return 1, None
    A = adaylar(kok)
    if not A: print("!! SIRALI_GORSEL/_ADAYLAR'da aday yok", flush=True); return 2, None
    P = _planlar(S); ev = idg.Evren(kok); hik = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    ozet = {"_surum": 1, "tur": tur, "arka": arka or olcum.arka_sec(kok), "planlar": {}, "elenen": []}
    for no, ads in sorted(A.items()):
        plan = P.get(no)
        if not plan: ozet["elenen"] += [{"plan": no, "aday": a, "neden": "plan SAHNELER'de yok"} for a, _ in ads]; continue
        b = beklenen(kok, plan, S, ev, hik)
        for aday, yol in ads:
            y = olcum.olc(yol, {k: b[k] for k in ("insan", "banka", "yaratik", "nesneler", "ebeveyn", "sahne_ilk")} |
                          {"karakterler": b["kadrajdakiler"], "yuz_acisi": b["yuz_acisi"]}, arka=ozet["arka"], film=kok)
            ortak.atomik_yaz(_olcum_yolu(kok, tur, no, aday), y)
            t = y.get("teknik") or {}
            acik = []
            if t.get("en_boy_16_9_sapma", 0) > olcum.esik("g1_en_boy_tolerans"): acik.append("en_boy")
            if t.get("kisa_kenar", 9999) < olcum.esik("g1_kisa_kenar_min"): acik.append("kisa_kenar")
            if acik: ozet["elenen"].append({"plan": no, "aday": aday, "neden": "açık teknik HATA: " + ", ".join(acik)})
            ozet["planlar"].setdefault(str(no), []).append(aday)
    ortak.atomik_yaz(os.path.join(kok, "_RAPOR", "G1", f"OLCUM_t{tur}.json"), ozet)
    kor_gorev(kok, tur, ozet=ozet)
    print(f"G1 ölçüm: {sum(len(v) for v in ozet['planlar'].values())} aday · elenen {len(ozet['elenen'])} · arka {ozet['arka']}", flush=True)
    return 0, ozet


def kor_gorev(kok, tur, ozet=None):
    import kor, istem_derle_gorsel as idg
    S = ortak.json_oku(os.path.join(kok, "SAHNELER.json"), {}) or {}
    ozet = ozet or ortak.json_oku(os.path.join(kok, "_RAPOR", "G1", f"OLCUM_t{tur}.json"), {}) or {}
    elenen = {(e["plan"], e["aday"]) for e in ozet.get("elenen") or []}
    P = _planlar(S); ev = idg.Evren(kok); hik = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    birim = []
    for no, ads in sorted(adaylar(kok).items()):
        if no not in P: continue
        b = beklenen(kok, P[no], S, ev, hik)
        for aday, yol in ads:
            if (no, aday) in elenen: continue
            birim.append({"anahtar": "%03d_%s" % (no, aday), "gorsel": yol, "baglam": kor_baglami(b)})
    toplam = len(glob.glob(os.path.join(kok, "SIRALI_GORSEL", "_ADAYLAR", "*.jpg")))
    import olcum
    gs = max(1, -(-toplam // int(olcum.esik("kor_gorev_gorsel_max") or 12)))      # film.py gorsel_grubu ile aynı sayı
    r = kor.paket_kur(kok, "g1", tur, birim, grup_sayisi=gs)
    yas = list((S.get("karakterler") or {}).keys()) + [k.get("ad") for k in (hik.get("karakterler") or {}).values() if isinstance(k, dict)]
    yas += [str(no) for no in P]
    bul = kor.sizinti(r["klasor"], [y for y in yas if y and not str(y).isdigit()])
    if bul: print("!! kör pakette sızıntı:", bul[:5], flush=True); return 1
    return 0


# --- kurallar ------------------------------------------------------------------------------------------------
def _m(alan, seviye, kaynak, **ek):
    return dict({"alan": alan, "seviye": seviye, "kaynak": kaynak}, **{k: v for k, v in ek.items() if v is not None})


def _kor_bul(ks, alan, kisi=None):
    return [k for k in ks if k["alan"] == alan and (kisi is None or k.get("kisi") == kisi)]


def degerlendir(y, ks, b, cevap=None, medyan=None):
    """Bir adayın alan maddeleri. y: yerel ölçüm, ks: kor.karsilastir sonuçları (None = kör gözlem yok), b: beklenen."""
    import olcum
    E = olcum.esik; out = []; olc_yok = y.get("olculemedi") or {}
    t = y.get("teknik") or {}
    if t.get("en_boy_16_9_sapma", 0) > E("g1_en_boy_tolerans"):
        out.append(_m("teknik", "HATA", "yerel", olcu=t.get("en_boy"), esik="16:9 ±%1"))
    if t.get("kisa_kenar", 9999) < E("g1_kisa_kenar_min"):
        out.append(_m("teknik", "HATA", "yerel", olcu=t.get("kisa_kenar"), esik=E("g1_kisa_kenar_min")))
    kor_var = ks is not None; ks = ks or []
    if not kor_var: out.append(_m("kor_gozlem", "OLCULEMEDI", "kor", neden="kör gözlem cevabı yok"))
    # yüz sayısı
    bek_yuz = len(b["gorunur_yuz"])
    kk = _kor_bul(ks, "kisi_sayisi")
    kor_fazla = bool(kk and kk[0]["sonuc"] == "uyumsuz" and str(kk[0]["kor"]).split()[0].isdigit()
                     and int(str(kk[0]["kor"]).split()[0]) > len(b["insan"]))
    if "yuz_sayisi" in olc_yok:
        if kor_fazla: out.append(_m("fazla_kisi", "BAYRAK", "kor", kor=kk[0]["kor"], beklenen=len(b["insan"])))
        elif b["gorunur_yuz"]: out.append(_m("yuz_sayisi", "OLCULEMEDI", "yerel", neden=olc_yok["yuz_sayisi"]))
    else:
        n = int(y.get("yuz_sayisi") or 0)
        if n > bek_yuz: out.append(_m("fazla_kisi", "HATA", "iki" if kor_fazla else "yerel", olcu=n, esik=bek_yuz))
        elif kor_fazla: out.append(_m("fazla_kisi", "BAYRAK", "kor", kor=kk[0]["kor"], beklenen=len(b["insan"]),
                                      neden="arka plan kişisi ya da yüzü görünmeyen kişi"))
        if n < bek_yuz: out.append(_m("eksik_yuz", "BAYRAK", "yerel", olcu=n, esik=bek_yuz))
    if kk and kk[0]["sonuc"] == "belirsiz": out.append(_m("kisi_sayisi", "BAYRAK", "kor", neden="kör iki cevap uyuşmuyor"))
    # kimlik
    kim = y.get("kimlik") or {}
    for kid in b["gorunur_yuz"]:
        if "kimlik" in olc_yok or f"kimlik:{kid}" in olc_yok or kid not in kim:
            out.append(_m("kimlik", "OLCULEMEDI", "yerel", kisi=kid, neden=olc_yok.get(f"kimlik:{kid}") or olc_yok.get("kimlik") or "ölçülmedi"))
            continue
        cal = b["kalibrasyon"].get(kid) or {}
        gec = max(E("g1_kimlik_gec"), cal.get("esik_gec") or 0); hata = max(E("g1_kimlik_hata"), cal.get("esik_hata") or 0)
        s, fp = kim[kid].get("benzerlik"), kim[kid].get("fark_payi")
        if s < hata: out.append(_m("kimlik", "HATA", "yerel", kisi=kid, olcu=s, esik=hata))
        elif s < gec: out.append(_m("kimlik", "BAYRAK", "yerel", kisi=kid, olcu=s, esik=gec))
        if fp is not None and fp < E("g1_kimlik_fark_payi_min"):
            out.append(_m("kimlik_fark_payi", "BAYRAK", "yerel", kisi=kid, olcu=fp, esik=E("g1_kimlik_fark_payi_min")))
    for kid in kim:
        if kid not in b["kadrajdakiler"] and kim[kid].get("benzerlik", 0) >= E("g1_kimlik_hata"):
            out.append(_m("yanlis_kisi", "HATA", "yerel", kisi=kid, olcu=kim[kid]["benzerlik"], neden="kadrajda olmaması gereken karakter"))
    # kadraj sırası ve üçte bir
    bs = b["kadraj_sirasi"]
    if len(bs) >= 2:
        if "kadraj_sirasi" in olc_yok: out.append(_m("kadraj_sirasi", "OLCULEMEDI", "yerel", neden=olc_yok["kadraj_sirasi"]))
        else:
            ol = [k for k in y.get("kadraj_sirasi") or [] if k in bs]
            if len(ol) >= 2 and ol != [k for k in bs if k in ol]:
                out.append(_m("kadraj_sirasi", "HATA", "yerel", olcu=ol, beklenen=bs, neden="kişiler kadrajda ters sırada (ayna?)"))
    for kid, u in (y.get("ucte_bir") or {}).items():
        bu = b["kadraj_konumu"].get(kid)
        if bu and u != bu:
            sev = "HATA" if b["plan_tipi"] in ("diyalog", "karsilikli", "karsi_cekim") else "BAYRAK"
            out.append(_m("ucte_bir", sev, "yerel", kisi=kid, olcu=u, beklenen=bu))
    # bakış (yaw)
    yaw = y.get("yaw") or {}; guven = y.get("yaw_guven", "yuksek")
    for kid, deg in yaw.items():
        hedef = b["bakis"].get(kid)
        if hedef not in ("kadraj_soluna", "kadraj_sagina") or deg is None: continue
        isaret = 1 if hedef == "kadraj_sagina" else -1
        if abs(deg) > E("g1_yaw_max_derece") and deg * b["yaw_isareti"] * isaret < 0:
            out.append(_m("bakis", "HATA" if guven == "yuksek" else "BAYRAK", "yerel", kisi=kid, olcu=deg, beklenen=hedef))
    # el – nesne
    ye = y.get("el_nesne") or {}
    for r in _kor_bul(ks, "nesne_el"):
        yr = ye.get(r.get("nesne")) or {}
        yerel_ters = bool(yr.get("el")) and yr["el"] != r["beklenen"]
        yerel_var = bool(yr.get("el"))
        if r["sonuc"] == "uyumsuz" and yerel_ters:
            out.append(_m("nesne_el", "HATA", "iki", kisi=r["kisi"], nesne=r["nesne"], beklenen=r["beklenen"], kor=r["kor"], yerel=yr.get("el")))
        elif r["sonuc"] == "uyumsuz" or yerel_ters:
            out.append(_m("nesne_el", "BAYRAK", "tek", kisi=r["kisi"], nesne=r["nesne"], beklenen=r["beklenen"], kor=r["kor"],
                          yerel=yr.get("el")))
        elif r["sonuc"] == "belirsiz" and not yerel_var:
            out.append(_m("nesne_el", "OLCULEMEDI", "iki", kisi=r["kisi"], nesne=r["nesne"], neden=r.get("neden") or "kör belirsiz, yerel yok"))
    # ağız ve konuşan yüz
    jo = y.get("jaw_open") or {}
    for kid in b["agiz_kapali"]:
        if kid in jo and jo[kid] > E("g1_jaw_open_max"): out.append(_m("agiz", "BAYRAK", "yerel", kisi=kid, olcu=jo[kid]))
        for r in _kor_bul(ks, "agiz", kid):
            if r["sonuc"] == "uyumsuz": out.append(_m("agiz", "BAYRAK", "kor", kisi=kid, kor=r["kor"]))
    for kid in b["konusan"]:
        yo = (y.get("yuz_orani") or {}).get(kid)
        if yo is not None and yo < E("g1_konusan_yuz_oran_min"): out.append(_m("konusan_yuz", "BAYRAK", "yerel", kisi=kid, olcu=yo))
        if kid in yaw and abs(yaw[kid]) > E("g1_konusan_yaw_max"): out.append(_m("konusan_yuz", "BAYRAK", "yerel", kisi=kid, olcu=yaw[kid]))
    for r in _kor_bul(ks, "acik_parmak"):
        if r["sonuc"] == "uyumsuz": out.append(_m("acik_parmak", "BAYRAK", "kor", kisi=r.get("kisi"), kor=r["kor"], beklenen=r["beklenen"]))
    # yaratık, mekân, ışık, renk
    yd = y.get("yaratik_dinov2") or {}
    for yid in b["yaratik_ids"]:
        if yid in yd:
            if yd[yid] < E("g1_yaratik_dinov2_min"): out.append(_m("yaratik", "BAYRAK", "yerel", kisi=yid, olcu=yd[yid]))
        else: out.append(_m("yaratik", "OLCULEMEDI", "yerel", kisi=yid, neden=olc_yok.get(f"yaratik:{yid}") or olc_yok.get("yaratik_dinov2") or "ölçülmedi"))
    if b.get("ebeveyn"):
        if y.get("mekan_dinov2") is not None:
            if y["mekan_dinov2"] < E("g1_mekan_dinov2_min"): out.append(_m("mekan", "BAYRAK", "yerel", olcu=y["mekan_dinov2"]))
        else: out.append(_m("mekan", "OLCULEMEDI", "yerel", neden=olc_yok.get("mekan_dinov2") or "ölçülmedi"))
    iy = (y.get("isik") or {}).get("isik_yon")
    if b.get("isik") in ("soldan", "sagdan") and iy in ("soldan", "sagdan") and iy != b["isik"]:
        out.append(_m("isik", "BAYRAK", "yerel", olcu=iy, beklenen=b["isik"]))
    if y.get("lab_de_sahne") is not None and y["lab_de_sahne"] > E("g1_lab_de_max"):
        out.append(_m("lab", "BAYRAK", "yerel", olcu=y["lab_de_sahne"], esik=E("g1_lab_de_max")))
    # stil
    kstil = str((cevap or {}).get("stil") or "").lower()
    kor_cizim = bool(kstil) and "photo" not in kstil
    cf = y.get("stil_clip_foto")
    yerel_cizim = cf is not None and cf < E("g1_stil_clip_foto_min")
    if yerel_cizim and kor_cizim: out.append(_m("stil", "HATA", "iki", olcu=cf, kor=kstil))
    elif yerel_cizim or kor_cizim: out.append(_m("stil", "BAYRAK", "tek", olcu=cf, kor=kstil or None))
    elif cf is None and not kstil and kor_var: out.append(_m("stil", "OLCULEMEDI", "iki", neden="CLIP yok ve kör stil yazmadı"))
    # yazı/logo, anatomi, yasak öğe, NE YOK
    env_yazi = str((cevap or {}).get("yazi_logo") or "none").lower() not in ("none", "no", "yok", "")
    qy = _kor_bul(ks, "yazi_logo")
    q_yazi = bool(qy and qy[0]["sonuc"] == "uyumsuz")
    if env_yazi and q_yazi: out.append(_m("yazi_logo", "HATA", "iki", kor=(cevap or {}).get("yazi_logo")))
    elif env_yazi or q_yazi: out.append(_m("yazi_logo", "BAYRAK", "tek", kor=(cevap or {}).get("yazi_logo")))
    qa = _kor_bul(ks, "anatomi")
    env_an = str((cevap or {}).get("anatomi") or "none").lower() not in ("none", "no", "yok", "")
    if qa:
        if qa[0]["sonuc"] == "uyumsuz" and qa[0]["tutarli"]: out.append(_m("anatomi", "HATA", "iki", kor=(cevap or {}).get("anatomi")))
        elif qa[0]["sonuc"] in ("uyumsuz", "belirsiz") or env_an: out.append(_m("anatomi", "BAYRAK", "tek", kor=(cevap or {}).get("anatomi")))
    for r in _kor_bul(ks, "yasak_oge"):
        if r["sonuc"] == "uyumsuz": out.append(_m("yasak_oge", "HATA", "kor", kor=r["kor"], neden="plan/sahne yasağı görüldü (02§6.1)"))
    for r in _kor_bul(ks, "ne_yok"):
        if r["sonuc"] == "uyumsuz": out.append(_m("ne_yok", "HATA", "kor", kor=r["kor"], neden="NE YOK öğesi görüldü"))
    for r in [k for k in ks if k["alan"].startswith("gorunen:")]:
        if r["sonuc"] != "uyum": out.append(_m("gorunen", "BAYRAK", "kor", oge=r["alan"].split(":", 1)[1], kor=r["kor"], beklenen=r["beklenen"]))
    # keskinlik
    if medyan and t.get("keskinlik") is not None and t["keskinlik"] / medyan < E("g1_keskinlik_oran_min"):
        out.append(_m("keskinlik", "BAYRAK", "yerel", olcu=round(t["keskinlik"] / medyan, 3), esik=E("g1_keskinlik_oran_min")))
    # ifade
    for r in _kor_bul(ks, "ifade"):
        if r["sonuc"] == "uyumsuz": out.append(_m("ifade", "BAYRAK", "kor", kisi=r.get("kisi"), kor=r["kor"], beklenen=r["beklenen"]))
    return out


def aday_karari(alanlar):
    s = "GEC"
    for a in alanlar:
        v = "BAYRAK" if a["seviye"] == "OLCULEMEDI" else a["seviye"]
        if SIRA[v] > SIRA[s]: s = v
    return s


def _secim_anahtari(a):
    kim = a["yerel"].get("kimlik") or {}
    fp = min((v.get("fark_payi") or 0 for v in kim.values()), default=0)
    ifade_uyum = sum(1 for r in a["kor"] or [] if r["alan"] == "ifade" and r["sonuc"] == "uyum")
    return (SIRA[a["karar"]], sum(1 for x in a["alanlar"] if x["seviye"] in ("BAYRAK", "OLCULEMEDI")), -ifade_uyum, -fp,
            -(a["yerel"].get("mekan_dinov2") or 0), -((a["yerel"].get("teknik") or {}).get("keskinlik") or 0), a["aday"])


# --- karar ---------------------------------------------------------------------------------------------------------
def _kor_cevaplari(kok, tur):
    import kor
    an = kor.anahtar_oku(kok, "g1", tur)
    out = {}
    for i, gor in (an.get("gruplar") or {}).items():
        cev = kor.cevaplari_oku(os.path.join(kok, "_RAPOR", "G1", f"gozlem_t{tur}_{i}.json"))
        for g, v in gor.items(): out[v["anahtar"]] = (v["sorular"], cev.get(g))
    return out


def karar(kok, tur, hakem=None):
    import olcum, kor, istem_derle_gorsel as idg
    from olcum import teknik
    S = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(S, dict): print("!! SAHNELER.json yok", flush=True); return 1, None
    A = adaylar(kok)
    if not A: print("!! aday yok", flush=True); return 2, None
    P = _planlar(S); ev = idg.Evren(kok); hik = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    oz = ortak.json_oku(os.path.join(kok, "_RAPOR", "G1", f"OLCUM_t{tur}.json"), {}) or {}
    elenen = {(e["plan"], e["aday"]): e["neden"] for e in oz.get("elenen") or []}
    korc = _kor_cevaplari(kok, tur)
    ol = {}
    for no, ads in A.items():
        if no not in P: continue
        b = beklenen(kok, P[no], S, ev, hik)
        for aday, yol in ads:
            y = ortak.json_oku(_olcum_yolu(kok, tur, no, aday))
            if not isinstance(y, dict):
                y = olcum.olc(yol, {k: b[k] for k in ("insan", "banka", "yaratik", "nesneler", "ebeveyn", "sahne_ilk")} |
                              {"karakterler": b["kadrajdakiler"]}, film=kok)
            ol[(no, aday)] = (y, b, yol)
    parti_kesk = {}
    for (no, aday), (y, b, _) in ol.items():
        parti_kesk.setdefault(P[no].get("parti"), []).append((y.get("teknik") or {}).get("keskinlik"))
    medyan = {k: teknik.medyan(v) for k, v in parti_kesk.items()}
    hk = (hakem or {})
    kayit = {"_surum": 1, "tur": tur, "planlar": {}}
    for (no, aday), (y, b, yol) in sorted(ol.items()):
        sorular, cevap = korc.get("%03d_%s" % (no, aday), (None, None))
        ks = None
        if sorular is not None and cevap is not None:
            es, kaynak = kor.kisi_esle(cevap, b["kadrajdakiler"], y.get("ucte_bir"), b["kadraj_konumu"])
            ks = kor.karsilastir(sorular, cevap, es, b["yuz_acisi"], b["eller"])
            if kaynak == "beklenen":
                for r in ks:
                    if r["sonuc"] == "uyumsuz" and r.get("kisi"): r["sonuc"] = "belirsiz"; r["neden"] = "kişi eşlemesi yalnız beklenenden"
        if (no, aday) in elenen: al = [_m("teknik", "HATA", "yerel", neden=elenen[(no, aday)])]
        else: al = degerlendir(y, ks, b, cevap, medyan.get(P[no].get("parti")))
        al = hakem_uygula(al, [h for h in hk.get("kararlar") or [] if h.get("plan") == no and h.get("aday") in (None, aday)],
                          hk.setdefault("reddedilen", []), no, aday)
        a = {"aday": aday, "yol": yol, "yerel": y, "kor": ks, "alanlar": al, "karar": aday_karari(al), "sha1": sha1(yol)}
        kayit["planlar"].setdefault(str(no), []).append(a)
    return yaz_karar(kok, tur, S, P, kayit, hk)


def hakem_uygula(alanlar, kararlar, reddedilen, no, aday):
    out = []
    for a in alanlar:
        h = next((k for k in kararlar if k.get("alan") == a["alan"] and k.get("kisi", a.get("kisi")) == a.get("kisi")), None)
        if h is None: out.append(a); continue
        if not str(h.get("gerekce") or "").strip():
            reddedilen.append(dict(h, plan=no, aday=aday, neden="gerekçe yok")); out.append(a); continue
        if a["seviye"] == "HATA":
            if str(h.get("karar")).upper() in ("GEC", "GEÇ"):
                reddedilen.append(dict(h, plan=no, aday=aday, neden=f"{a['kaynak']} kaynaklı HATA hakemle GEÇ'e çevrilemez (İ-3)"))
            out.append(a); continue
        k = str(h.get("karar")).upper().replace("GEÇ", "GEC")
        if k == "GEC": continue
        if k == "HATA": out.append(dict(a, seviye="HATA", kaynak="hakem", hakem=h.get("gerekce"))); continue
        out.append(a)
    return out


def yaz_karar(kok, tur, S, P, kayit, hk):
    import olcum, kuyruk, duzeltme, istem_derle_gorsel as idg
    po = _po()
    ev = idg.Evren(kok)
    karakterler = {}
    hik = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    for kid in (S.get("karakterler") or {}):
        c = ev.karakter(kid)
        karakterler[kid] = {"ad": c.get("ad") or ((hik.get("karakterler") or {}).get(kid) or {}).get("ad") or kid.title(),
                            "kimlik_en": c.get("kimlik_en")}
    film_olc, gruplar, maddeler, secilen, dondur, onizleme, yer_tutucu = [], {}, [], {}, [], {}, []
    ifade_say = [0, 0]
    sg = os.path.join(kok, "SIRALI_GORSEL"); os.makedirs(os.path.join(sg, "ALTERNATIFLER"), exist_ok=True)
    gozlenen = {}
    for nos, ads in sorted(kayit["planlar"].items(), key=lambda t: int(t[0])):
        no = int(nos); plan = P[no]
        ads.sort(key=_secim_anahtari); en = ads[0]
        for r in en["kor"] or []:
            if r["alan"] == "ifade" and r["sonuc"] in ("uyum", "uyumsuz"): ifade_say[0] += r["sonuc"] == "uyum"; ifade_say[1] += 1
        ur = plan.setdefault("uretim", {}).setdefault("gorsel", {})
        bas = ur.get("basamak") or idg.basamak(plan)
        kapsam = f"P{plan.get('parti') or 1}_B{bas}"
        for a in en["alanlar"]:
            o = po.m(a["alan"], a["seviye"], no, aday=en["aday"], kaynak=a["kaynak"], kisi=a.get("kisi"), olcu=a.get("olcu"),
                     esik=a.get("esik"), beklenen=a.get("beklenen"), kor=a.get("kor"), neden=a.get("neden"),
                     kanit=[os.path.relpath(en["yol"], kok).replace(os.sep, "/")])
            film_olc.append(o); gruplar.setdefault(kapsam, []).append(o)
        gruplar.setdefault(kapsam, [])
        g1 = {"sonuc": en["karar"], "aday": en["aday"], "tur": tur, "rapor": f"_RAPOR/G1_{kapsam}.json", "sha1": None}
        hedef = os.path.join(sg, "%03d.jpg" % no)
        for a in ads[1:] if en["karar"] == "GEC" else ads:
            _kopya(a["yol"], os.path.join(sg, "ALTERNATIFLER", os.path.basename(a["yol"])))
        if en["karar"] == "GEC":
            if os.path.isfile(hedef) and sha1(hedef) != en["sha1"]: _eskiye(kok, hedef)
            _kopya(en["yol"], hedef); g1["sha1"] = sha1(hedef)
            yan = ortak.json_oku(os.path.splitext(en["yol"])[0] + ".json", {}) or {}
            ur.update(aday=en["aday"], sha1=g1["sha1"], saglayici=yan.get("saglayici") or ur.get("saglayici"), tohum=yan.get("tohum"))
            secilen[nos] = en["aday"]; dondur.append(no)
            for r in en["kor"] or []:
                if r["alan"] == "nesne_el" and r.get("kor"):
                    gozlenen.setdefault(nos, {"kapi": "G1", "an": "bas", "rapor": g1["rapor"], "olgular": {}})["olgular"][
                        f"karakterler.{r['kisi']}.eller.{r['kor']}.tutar"] = r["nesne"]
        else:
            kimlik_h = any(a["seviye"] == "HATA" and a["alan"] in KIMLIK_ALANLARI for a in en["alanlar"])
            if kimlik_h: yer_tutucu.append(no)
            else:
                _kopya(en["yol"], os.path.join(sg, "_ONIZLEME", "%03d.jpg" % no)); onizleme[nos] = en["aday"]
            if en["karar"] == "HATA": maddeler += _kuyruk_maddeleri(kok, plan, en, karakterler, g1["rapor"])
        plan.setdefault("denetim", {})["G1"] = g1
    n = len(kayit["planlar"]) or 1
    yt = len(yer_tutucu) / float(n)
    if yt > float(olcum.esik("animatik_tur1_yer_tutucu_max_oran") or 0.15):
        film_olc.append(po.m("yer_tutucu_orani", "HATA", None, olcu=round(yt, 3), esik=olcum.esik("animatik_tur1_yer_tutucu_max_oran"),
                             neden="kimlik HATA'sı yüzünden yer tutucu oranı yüksek: kimlik maddeleri için 1 düzeltme turu (§1.3 A11)"))
    io = (ifade_say[0] / float(ifade_say[1])) if ifade_say[1] else None
    if io is not None and io < float(olcum.esik("ifade_uyum_min_oran") or 0.85):
        film_olc.append(po.m("ifade_uyum", "BAYRAK", None, olcu=round(io, 3), esik=olcum.esik("ifade_uyum_min_oran")))
    for kapsam, ol in gruplar.items():
        bl = [int(no) for no, ads in kayit["planlar"].items()
              if f"P{P[int(no)].get('parti') or 1}_B{(P[int(no)].get('uretim') or {}).get('gorsel', {}).get('basamak') or 1}" == kapsam]
        ek = {"adaylar": {str(no): [_aday_ozet(a, kok) for a in kayit["planlar"][str(no)]] for no in bl}}
        _alt_rapor(kok, kapsam, ol, tur, bl, ek)
    if maddeler:
        kq = kuyruk.ekle(kok, maddeler, kaynak_kapi="G1", kaynak_rapor=f"_RAPOR/G1_FILM_t{tur}.json", kapi_tur=tur, sahneler=S, asama="A11")
    else: kq = {"eklenen": [], "reddedilen": []}
    ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), S)
    yol, r = po.rapor_yaz(kok, "G1", "FILM", film_olc, asama="A11", arac=SURUM, tur=tur, birimler=sorted(int(x) for x in kayit["planlar"]),
                          varsayilan=f"_RAPOR/G1_FILM_t{tur}.json",
                          ek={"secilen": secilen, "onizleme": onizleme, "yer_tutucu": yer_tutucu, "yer_tutucu_orani": round(yt, 3),
                              "ifade_uyum_orani": None if io is None else round(io, 3), "kuyruk_eklenen": kq.get("eklenen"),
                              "kuyruk_reddedilen": len(kq.get("reddedilen") or []),
                              "hakem_bekleyen": sorted({int(no) for no, ads in kayit["planlar"].items()
                                                         if sorted(ads, key=_secim_anahtari)[0]["karar"] == "BAYRAK"}),
                              "hakem_reddedilen": hk.get("reddedilen") or []})
    kayit["hakem"] = hk
    ortak.atomik_yaz(os.path.join(kok, "_RAPOR", "G1", f"KARAR_t{tur}.json"),
                     {k: v for k, v in kayit.items() if k != "planlar"} | {"planlar": {n_: [_aday_ozet(a, kok) for a in v] for n_, v in kayit["planlar"].items()}})
    if dondur and os.path.isfile(os.path.join(kok, "DUNYA_DEFTERI.json")):
        try:
            import dunya_defteri
            dunya_defteri.dondur(kok, dondur)
            if gozlenen:
                gp = os.path.join(kok, "_RAPOR", "G1", f"gozlenen_t{tur}.json"); ortak.atomik_yaz(gp, gozlenen)
                dunya_defteri.gozlenen(kok, gp)
        except Exception as e: print(f"!! dünya defteri güncellenemedi: {e}", flush=True)
    try:
        import kapak
        kapak.kor_paketi(kok, tur)
    except Exception as e: print(f"!! kapak kör paketi hazırlanamadı: {e}", flush=True)
    po.yaz_ozet(r, "G1")
    return 0, r


def _alt_rapor(kok, kapsam, ol, tur, birimler, ek):
    """Aday ayrıntılı alt rapor _RAPOR/G1_<kapsam>.json (görev raporu değildir; görevin kapı raporu G1_FILM_t<tur>)."""
    import kapi
    po = _po(); g = po.gorev()
    r = kapi.rapor_kur("G1", kapsam, ol, tur=tur, asama=g.get("asama") or "A11", gorev=g.get("id"), arac_surum=SURUM,
                       esik_surum=po.esik().surum, birimler=birimler, ek=ek)
    return kapi.yaz(os.path.join(kok, "_RAPOR"), r)


def _aday_ozet(a, kok):
    y = a["yerel"]
    return {"aday": a["aday"], "karar": a["karar"], "sha1": a["sha1"], "gorsel": os.path.relpath(a["yol"], kok).replace(os.sep, "/"),
            "yerel": {k: y.get(k) for k in ("yuz_sayisi", "kimlik", "kadraj_sirasi", "ucte_bir", "yaw", "jaw_open", "el_nesne",
                                             "mekan_dinov2", "stil_clip_foto", "lab_de_sahne") if y.get(k) is not None}
            | {"keskinlik": (y.get("teknik") or {}).get("keskinlik"), "arka": y.get("arka"), "olculemedi": y.get("olculemedi")},
            "kor": a["kor"], "alanlar": a["alanlar"]}


def _kuyruk_maddeleri(kok, plan, en, karakterler, rapor):
    import duzeltme
    hs = [a for a in en["alanlar"] if a["seviye"] == "HATA"]
    if not hs: return []
    a = hs[0]; alan = a["alan"]
    sk = duzeltme.sifir_kredi(kok, plan, en["aday"], alan, kanit=a)
    if sk.get("yeni_aday"): return []                   # küçük düzeltme uygulandı: yeni aday sonraki G1 turunda ölçülür
    try: c = duzeltme.madde_cumlesi(dict(a, nesne_ad=a.get("nesne")), plan, karakterler)
    except duzeltme.DuzeltmeHatasi as e: c = None; print(f"!! CORRECTION kurulamadı ({plan['no']}): {e}", flush=True)
    return [{"plan": int(plan["no"]), "tur": "gorsel", "kaynak_kapi": "G1", "kaynak_rapor": rapor,
             "kok_neden": duzeltme.KOK_NEDEN.get(alan, "stil"), "seviye": "HATA", "alan": alan, "aday": [x["aday"] for x in [en]],
             "beklenen": a.get("beklenen"), "olculen": {"yerel": a.get("olcu"), "kaynak": a["kaynak"]}, "gozlenen": {"kor": a.get("kor")},
             "kisi": a.get("kisi"), "nesne": a.get("nesne"), "cozum": "yeniden_cek", "duzeltme": c, "sifir_kredi": sk,
             "saglayici_zinciri": "gorsel_duzeltme", "dilim": "goruntu", "kredi_tahmini": 0}]


def _kopya(a, b):
    os.makedirs(os.path.dirname(b), exist_ok=True); tmp = b + ".tmp"; shutil.copyfile(a, tmp); os.replace(tmp, b)


def _eskiye(kok, yol):
    d = os.path.join(kok, "_ESKI", "SIRALI_GORSEL"); os.makedirs(d, exist_ok=True)
    k, u = os.path.splitext(os.path.basename(yol)); n = 1
    while os.path.exists(os.path.join(d, f"{k}_v{n}{u}")): n += 1
    shutil.move(yol, os.path.join(d, f"{k}_v{n}{u}"))


# --- hakem ve video kapısı -------------------------------------------------------------------------------------
def hakem(kok, tur, dosya):
    h = ortak.json_oku(dosya)
    if isinstance(h, list): h = {"kararlar": h}
    if not isinstance(h, dict): print("!! hakem dosyası okunamadı", flush=True); return 1, None
    h = {"kararlar": [k for k in h.get("kararlar") or h.get("hakem") or [] if isinstance(k, dict) and k.get("plan") is not None]}
    for k in h["kararlar"]: k["plan"] = int(k["plan"])
    kod, r = karar(kok, tur, hakem=h)
    ortak.atomik_yaz(os.path.join(kok, "_RAPOR", "G1", f"HAKEM_t{tur}.json"),
                     {"_surum": 1, "tur": tur, "kararlar": h["kararlar"], "reddedilen": h.get("reddedilen") or []})
    if h.get("reddedilen"): print(f"!! hakem kararlarından {len(h['reddedilen'])} tanesi reddedildi (iki kaynaklı HATA / gerekçesiz)", flush=True)
    return kod, r


def video_hazir(film, no):
    """Video gönderimine hazır mı: SAHNELER denetim.G1 GEÇ, SIRALI_GORSEL/NNN.jpg var ve SHA1'i kayıtla aynı. (bool, neden)"""
    S = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    p = _planlar(S).get(int(no))
    if not p: return False, "plan yok"
    g = (p.get("denetim") or {}).get("G1") or {}
    zg = (p.get("denetim") or {}).get("G1Z") or {}
    kayit = zg if zg.get("sonuc") == "GEC" and zg.get("sha1") else g
    if kayit.get("sonuc") != "GEC": return False, f"G1 {kayit.get('sonuc') or 'yok'} (videoya yalnız G1 GEÇ kare gider)"
    yol = os.path.join(film, "SIRALI_GORSEL", "%03d.jpg" % int(no))
    if not os.path.isfile(yol): return False, "SIRALI_GORSEL karesi yok"
    if not kayit.get("sha1") or sha1(yol) != kayit["sha1"]: return False, "SHA1 uyuşmuyor (kare G1'den sonra değişmiş)"
    return True, ""


def serbest(gorsel, beklenen_yol=None):
    import olcum
    b = ortak.json_oku(beklenen_yol, {}) if beklenen_yol else {}
    print(json.dumps(olcum.olc(gorsel, b or {}), ensure_ascii=False, indent=1, default=str)); return 0


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 4
    po = _po()
    if "--serbest" in argv: return serbest(po.arg_al(argv, "--serbest"), po.arg_al(argv, "--beklenen"))
    kok = po.film_kok(po.arg_al(argv, "--film")); tur = po.tur_no(argv)
    try:
        if "--olc" in argv or "--yerel" in argv: return olc(kok, tur)[0]
        if "--kor-gorev" in argv: return kor_gorev(kok, tur)
        if "--karar" in argv: return karar(kok, tur)[0]
        if "--hakem" in argv: return hakem(kok, tur, po.arg_al(argv, "--hakem"))[0]
    except ortak.YolYok as e: print("!!", e); return 4
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
