"""BULGU YÖNLENDİR — seyirci bulgularını sahibine yönlendirir (TASARIM §6.3; [SN2] §2.4 `bulgu-sinifla` + [KU2]; tek kod).

Kullanım:
  python bulgu_yonlendir.py --kip kagit|plan|animatik|kesit|kurgu --tur N --film <film>
Girdi:
  _RAPOR/SEYIRCI_KARAR_<KIP>_t<N>.json (puan_oku seyirci_topla: birleşmiş kopukluk kümeleri, eksik olgular, açılmamış sorular)
  _RAPOR/SEYIRCI/<kip>_t<N>/b<i>_bulgu.json (ozet-eslestirici·bulgu: [{bulgu, konum{sahne, plan}, eslesen{tur, id}, kok_neden?}])
  HIKAYE.json (yoksa en son 06_SENARYO), planlar (SAHNELER.json v2 ya da _YONETMEN/PLANLAR/*.json), K1 raporları (_RAPOR/K1_v*.json,
  K1ON_*.json), sahip tablosu veri/kok_neden.json.
Kural (her bulgu için):
  1. Eşleşen olgu/soru/kurulum HIKAYE'de yok → kok_neden bilgi_eksik, sahip hikaye-yazari (merdiven 2: köprü replik).
  2. HIKAYE'de var, planlarda (zanaat.ekranda_bilgi / _derlenir.hikaye / plan kimlik listeleri) yok → hikaye_adimi_ekranda_yok, yonetmen.
  3. İkisinde de var ve konumdaki plan ±1'de K1 HATA'sı var → K1 kök nedeni, sahibi (süreklilik).
  4. İkisinde de var, K1 temiz → kâğıtta hikaye-yazari (bilgi_ekranda_yok), izleme kiplerinde kurgucu (konusan_belirsiz/diyalog_kopuk).
  Bulgunun kendi kok_neden'i sözlükte varsa sahibi oradan gelir (eşleşme bunu ezmez, yalnız hikâyede yoksa bilgi_eksik'e döner).
Çıktı: _RAPOR/BULGU_YONLENDIRME_<KIP>_t<N>.json {_surum, _uretim, kip, tur, bulgular[{kaynak, bulgu, konum, eslesen, hikayede_var,
  planda_var, kok_neden, sahip, merdiven_onerisi}], sahip_ozet}. Kuyruğa yazmaz (kuyruk.py'nin işi; öneri listesi verir).
Çıkış kodları: 0 yazıldı · 1 girdi yok/kullanım · 4 YOLLAR.json yok.
"""
import os, re, sys, json, glob
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi
import puan_oku

SURUM = "bulgu_yonlendir 1.0"
IZLEME_KIPLERI = ("animatik", "kesit", "kurgu")
MERDIVEN = {"bilgi_eksik": 2, "bilgi_ekranda_yok": 2, "hikaye_adimi_ekranda_yok": 4, "kurulum_yok": 2}


def kok_sozluk():
    return ortak.json_oku(os.path.join(HERE, "veri", "kok_neden.json"), {}) or {}


def sahip_bul(kn, soz=None):
    soz = soz or kok_sozluk()
    kn = (soz.get("es_anlamlar") or {}).get(kn, kn)
    r = (soz.get("kok_nedenler") or {}).get(kn)
    return (kn, r.get("sahip")) if r else (None, None)


def hikaye_kimlikleri(h):
    ids = set()
    for ad in ("anahtar_olgular", "MERAK_DEFTERI", "KURULUMLAR", "IRONILER"):
        ids |= {x.get("id") for x in h.get(ad) or [] if isinstance(x, dict) and x.get("id")}
    return ids


def plan_kimlikleri(film):
    """Planlarda karşılığı olan hikâye kimlikleri ve sahne → plan numaraları."""
    ids, sahne_plan = set(), {}
    planlar = []
    s = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    if int(s.get("_surum", 1) or 1) >= 2: planlar += s.get("sahneler") or []
    for p in sorted(glob.glob(os.path.join(film, "_YONETMEN", "PLANLAR", "*.json"))):
        j = ortak.json_oku(p, {}) or {}
        planlar += j.get("planlar") or j.get("sahneler") or ([j] if j.get("zanaat") else [])
    for pl in planlar:
        if not isinstance(pl, dict): continue
        z = pl.get("zanaat") or {}; d = pl.get("_derlenir") or {}; hk = d.get("hikaye") or {}
        for a in ("merak_ac", "merak_kapat", "kurulum", "kullanim_bilgi", "tasidigi", "olgular"):
            ids |= {x for x in (hk.get(a) or []) + (z.get(a) or []) if isinstance(x, str)}
        if hk.get("ironi"): ids.add(hk["ironi"])
        eb = z.get("ekranda_bilgi")
        for x in (eb if isinstance(eb, list) else [eb]):
            if isinstance(x, dict) and x.get("olgu"): ids.add(x["olgu"])
            elif isinstance(x, str): ids |= set(re.findall(r"\b[omki]\w*\d\d\b", x))
        sg = z.get("sahne_grubu") or pl.get("sahne")
        if sg and pl.get("no") is not None: sahne_plan.setdefault(sg, []).append(pl["no"])
    return ids, sahne_plan, bool(planlar)


def k1_hatalari(film):
    out = []
    for p in glob.glob(os.path.join(film, "_RAPOR", "K1_v*.json")) + glob.glob(os.path.join(film, "_RAPOR", "K1ON_*.json")):
        j = ortak.json_oku(p, {}) or {}
        for h in j.get("hatalar") or []:
            if isinstance(h, dict) and isinstance(h.get("plan"), int): out.append(h)
    return out


def yonlendir_bir(b, kip, h_ids, p_ids, planlar_var, k1, soz):
    es = b.get("eslesen") or {}
    eid = es.get("id"); etur = es.get("tur")
    ko = b.get("konum") or {}
    hikayede = eid in h_ids if eid else None
    planda = (eid in p_ids) if (eid and planlar_var) else (None if not planlar_var else False)
    kn, sahip = (None, None)
    if b.get("kok_neden"): kn, sahip = sahip_bul(b["kok_neden"], soz)
    if eid and not hikayede:
        kn, sahip = "kurulum_yok" if etur == "kurulum" else "bilgi_eksik", "hikaye-yazari"
    elif kn is None:
        plan = ko.get("plan")
        k1h = next((x for x in k1 if isinstance(plan, int) and abs(x["plan"] - plan) <= 1), None)
        if eid and planlar_var and not planda: kn = "hikaye_adimi_ekranda_yok"
        elif k1h:
            kn = (soz.get("es_anlamlar") or {}).get(k1h.get("kok_neden") or k1h.get("madde"), k1h.get("kok_neden") or k1h.get("madde"))
            if kn not in (soz.get("kok_nedenler") or {}): kn = "nesne_zipladi"
        elif kip in IZLEME_KIPLERI: kn = "konusan_belirsiz" if etur == "konusan" else "diyalog_kopuk" if etur == "diyalog" else "bilgi_ekranda_yok"
        else: kn = "bilgi_ekranda_yok"
        kn, sahip = sahip_bul(kn, soz)
        if kip in IZLEME_KIPLERI and kn == "bilgi_ekranda_yok" and planda: sahip = "kurgucu"
    return {"kaynak": b.get("_kaynak"), "bulgu": b.get("bulgu"), "konum": ko, "eslesen": es or None, "hikayede_var": hikayede,
            "planda_var": planda, "kok_neden": kn, "sahip": sahip, "merdiven_onerisi": MERDIVEN.get(kn, 1)}


def yonlendir(film, kip="kagit", tur=1, gorev=None):
    film = os.path.abspath(film); K = kip.upper()
    try:
        import evren
        h = evren.film_hikaye(film) or {}
    except Exception: h = {}
    h_ids = hikaye_kimlikleri(h); p_ids, _, planlar_var = plan_kimlikleri(film)
    k1 = k1_hatalari(film); soz = kok_sozluk()
    sk = os.path.join(film, "_RAPOR", "SEYIRCI", f"{kip}_t{tur}")
    bulgular = []
    for p in sorted(glob.glob(os.path.join(sk, "b*_bulgu.json"))):
        j = ortak.json_oku(p)
        liste = j if isinstance(j, list) else (j or {}).get("bulgular") or []
        for i, b in enumerate(liste):
            if isinstance(b, dict): bulgular.append(dict(b, _kaynak=f"{os.path.basename(p)}#{i}"))
    karar = ortak.json_oku(os.path.join(film, "_RAPOR", f"SEYIRCI_KARAR_{K}_t{tur}.json"), {}) or {}
    for o in karar.get("eksik_olgular") or []:
        if not any((b.get("eslesen") or {}).get("id") == o for b in bulgular):
            bulgular.append({"_kaynak": "seyirci_karar:eksik_olgu", "bulgu": f"olgu {o} seyircilerin çoğunda yok",
                             "eslesen": {"tur": "anahtar_olgu", "id": o}})
    for q in karar.get("ekranda_acilmamis_sorular") or []:
        bulgular.append({"_kaynak": "seyirci_karar:acilmamis_soru", "bulgu": f"merak sorusu {q} ekranda açılmamış",
                         "eslesen": {"tur": "merak", "id": q}})
    for c in karar.get("kopukluk") or []:
        if c.get("gecersiz"): continue
        bulgular.append({"_kaynak": "seyirci_karar:kopukluk", "bulgu": "; ".join(n for n in c.get("nedenler") or [] if n)[:300],
                         "konum": c.get("konum") or {}, "seviye": c.get("tur"), "kac_seyirci": c.get("kac_seyirci")})
    out = [yonlendir_bir(b, kip, h_ids, p_ids, planlar_var, k1, soz) for b in bulgular]
    for o, b in zip(out, bulgular):
        if b.get("seviye"): o["seviye"] = b["seviye"]
    ozet = {}
    for o in out: ozet[o["sahip"] or "?"] = ozet.get(o["sahip"] or "?", 0) + 1
    r = {"_surum": 1, "_uretim": {"asama": {"kagit": "A06", "plan": "A07e", "animatik": "A12", "kesit": "A14a", "kurgu": "A16"}.get(kip),
                                  "gorev": gorev, "girdi_imza": puan_oku.dosya_imza(film, [f"_RAPOR/SEYIRCI_KARAR_{K}_t{tur}.json"]),
                                  "arac_surum": SURUM, "esik_surum": None, "sonuc": "GEC", "zaman": kapi.simdi(), "ortam": kapi.ortam()},
         "kip": kip, "tur": tur, "bulgular": out, "sahip_ozet": ozet}
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", f"BULGU_YONLENDIRME_{K}_t{tur}.json"), r)
    return r


def main(a):
    def arg(ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v
    film = arg("--film")
    if not film: print(__doc__); return 1
    if not os.path.isdir(film):
        try: film = os.path.join(ortak.yollar()["filmler"], film)
        except ortak.YolYok as e: print("!!", e); return 4
    g = puan_oku.gorev_baglami(arg("--tur"))
    r = yonlendir(film, arg("--kip", "kagit"), g["tur_no"], g["id"])
    print(json.dumps(r["sahip_ozet"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
