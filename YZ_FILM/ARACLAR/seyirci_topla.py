"""SEYİRCİ TOPLA — hat/asamalar.py'nin seyirci turu betiği (A06, A07e, A12, A14a, A16): puan_oku.seyirci_topla + izleme ekleri
(TASARIM §1.4, §5.8, §7.2 HS_*, D-14, D-18, D-19; [KU2] §4.5.9).

Kullanım (film.py calis): python seyirci_topla.py --kip kagit|plan|animatik|kesit|kurgu [--tur N] [--izleyici-atla] --film <film>
  Kâğıt kiplerinde (kagit, plan) doğrudan puan_oku.seyirci_topla'dır (tek hesap kodu; D-32). İzleme kiplerinde (animatik, kesit, kurgu)
  aynı karar ve HS_<KIP> kapı raporu yazıldıktan sonra şu ekler aynı rapora işlenir:
  - Personalar: medyandaki seyircilerin personası RE seyirci_persona_izleme ({A: 2, B: 1}) değilse BAYRAK.
  - izleyici + dinleyici (saglayicilar/izleyici.py, dinleyici.py; anahtar ve ücretsiz katman varsa açık): yz_kusurlari ve ses bulguları
    BAYRAK; medyana girmez. Çalışmazsa ÖLÇÜLEMEDİ (= BAYRAK) ve izle-dinle bilgi paketi notu (D-19, D-24).
  - Geri gidiş: önceki turda hedefi (RE seyirci_genel_esik) geçen parti bu turda geçmiyorsa BAYRAK.
  - Anlaşılmayan konuşma sayısı (BAYRAK, [SM] S7.6 ile eşlenir).
  - Yalnız animatik (A12): kapıyı yalnız bütün kareleri G1 GEÇ olan tur açar (yoksa HATA g1_tamam_degil); render süresi = T1 ± RE
    render_sure_tolerans_kare (yoksa HATA); yer tutucu ≤ RE animatik_yer_tutucu_max_oran (yoksa HATA). Kapı sağlanırsa
    animatik_imza.imzala → ANIMATIK/ONAY.json (`animatik: ONAYLI`).
  Ek HATA kapıyı kapatır (sonuç HATA, kapi_saglandi false); BAYRAK yalnız GEC'i BAYRAK'a çevirir.
Çıkış kodları: 0 rapor yazıldı (kapı sonucu raporda) · 1 araç/kullanım hatası · 4 YOLLAR.json yok.
"""
import os, sys, json, glob, argparse
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi, puan_oku

SURUM = "seyirci_topla 1.0"
KAGIT = ("kagit", "plan")
IZLEME = ("animatik", "kesit", "kurgu")


def E(ad, v=None):
    import zaman_cizelgesi_t1 as t1
    x = t1.E(ad)
    return v if x is None else x


def persona_denetle(karar_raporlari):
    istenen = E("seyirci_persona_izleme", {"A": 2, "B": 1}) or {}
    say = {}
    for r in karar_raporlari:
        if r.get("donen"): continue
        say[r.get("persona") or "?"] = say.get(r.get("persona") or "?", 0) + 1
    if say == {k: v for k, v in istenen.items() if v}: return []
    return [{"madde": "persona_dagilimi", "seviye": "BAYRAK", "olcu": say, "esik": istenen}]


def izleyici_ekleri(film, kip, tur, atla=False):
    olc, ozet = [], {}
    if atla:
        return [{"madde": "izleyici", "seviye": "OLCULEMEDI", "neden": "atlandı (--izleyici-atla)"}], {"izleyici": "atlandi"}
    for ad in ("izleyici", "dinleyici"):
        try:
            mod = __import__("saglayicilar.%s" % ad, fromlist=["calistir"])
            k = mod.calistir(film, kip, tur)
        except Exception as e:
            k = {"durum": "olculemedi", "neden": "%s çalışmadı (%s)" % (ad, e.__class__.__name__)}
        ozet[ad] = k.get("durum")
        if k.get("durum") != "olculdu":
            olc.append({"madde": ad, "seviye": "OLCULEMEDI", "neden": (k.get("neden") or "") + " — izle-dinle bilgi paketi kullanıcıya gider (D-24)"})
            continue
        for b in k.get("bayraklar") or []: olc.append({"madde": "%s_%s" % (ad, b), "seviye": "BAYRAK"})
        if ad == "izleyici":
            r = k.get("rapor") or {}
            for x in r.get("yz_kusurlari") or []:
                olc.append({"madde": "yz_kusuru", "seviye": "BAYRAK", "tur": x.get("tur"), "zaman": x.get("zaman"),
                            "olcu": x.get("siddet"), "neden": x.get("not"), "kaynak": "izleyici"})
            for x in r.get("kopukluklar") or []:
                if str(x.get("tur")).upper() in ("KRITIK", "KRİTİK"):
                    olc.append({"madde": "izleyici_kopukluk", "seviye": "BAYRAK", "konum": x.get("konum"), "neden": x.get("neden"),
                                "kaynak": "izleyici"})
            if (r.get("puanlar") or {}).get("GENEL") is not None: ozet["izleyici_genel"] = r["puanlar"]["GENEL"]
        else:
            for x in k.get("bulgular") or []:
                olc.append({"madde": "ses_bulgusu", "seviye": "BAYRAK", "tur": x.get("tur"), "zaman": x.get("zaman"), "olcu": x.get("siddet"),
                            "neden": x.get("not"), "kaynak": "dinleyici"})
            for c in k.get("cevaplar") or []:
                if c.get("cevap") in ("hayir", "kismen"):
                    olc.append({"madde": "dinleyici_cevap", "seviye": "BAYRAK", "soru": c.get("soru"), "neden": c.get("not") or c.get("cevap")})
    return olc, ozet


def geri_gidis(film, kip, tur, karar):
    if tur < 2: return []
    onceki = ortak.json_oku(os.path.join(film, "_RAPOR", "SEYIRCI_KARAR_%s_t%d.json" % (kip.upper(), tur - 1)), {}) or {}
    esik = E("seyirci_genel_esik", 8); out = []
    for p, g in (onceki.get("parti_medyan") or {}).items():
        simdi = (karar.get("parti_medyan") or {}).get(p)
        if g is not None and g >= esik and simdi is not None and simdi < esik:
            out.append({"madde": "geri_gidis", "seviye": "BAYRAK", "sahne": p, "olcu": simdi, "esik": esik, "onceki": g})
    return out


def animatik_kosullari(film, tur):
    import zaman_cizelgesi_t1 as t1
    out = []
    plan, pyol, n = t1.plan_oku(film, "T1", tur)
    if plan is None: return [{"madde": "t1_yok", "seviye": "HATA", "neden": "KURGU_PLANI_T1_v%d yok" % tur}]
    gp = [p for p in plan.get("planlar") or [] if (p.get("goruntu") or {}).get("tur") in ("gorsel", "yer_tutucu")]
    eksik = [p["plan"] for p in gp if p["goruntu"].get("tur") != "gorsel" or p["goruntu"].get("g1") != "GEC"]
    if eksik:
        out.append({"madde": "g1_tamam_degil", "seviye": "HATA", "olcu": len(eksik), "planlar": eksik[:50],
                    "neden": "kapıyı yalnız bütün kareleri G1 GEÇ olan tur açar (D-14); G1 düzeltmeleri bu turdan sonra"})
    oran = len(eksik) / len(gp) if gp else 0.0
    if oran > float(E("animatik_yer_tutucu_max_oran", 0.10)):
        out.append({"madde": "yer_tutucu", "seviye": "HATA", "olcu": round(oran, 4), "esik": E("animatik_yer_tutucu_max_oran", 0.10)})
    rr = ortak.json_oku(os.path.join(film, "_RAPOR", "RENDER_ANIMATIK_v%d.json" % tur))
    tol = int(E("render_sure_tolerans_kare", 1))
    if not isinstance(rr, dict): out.append({"madde": "render_raporu", "seviye": "HATA", "neden": "kurgu_render --animatik raporu yok"})
    elif rr.get("fark_kare") is None or rr["fark_kare"] > tol or rr.get("sonuc") == "HATA":
        out.append({"madde": "render_sure", "seviye": "HATA", "olcu": rr.get("fark_kare"), "esik": tol})
    elif rr.get("kurgu_plani_imza") != t1.sha(pyol):
        out.append({"madde": "render_bayat", "seviye": "HATA", "neden": "render başka bir T1 dosyasından"})
    if isinstance(rr, dict) and (rr.get("ses") or {}).get("durum") == "sessiz":
        out.append({"madde": "animatik_ses", "seviye": "BAYRAK", "neden": "animatik sessiz render edildi (son_miks çıktısı yok)"})
    return out


def raporu_guncelle(yol, ekler, ozet):
    r = ortak.json_oku(yol)
    if not isinstance(r, dict): raise kapi.RaporHatasi(["kapı raporu okunamadı"], yol)
    hata = [dict({k: v for k, v in e.items() if k != "seviye"}, seviye="HATA") for e in ekler if e["seviye"] == "HATA"]
    bay = []
    for e in ekler:
        if e["seviye"] == "HATA": continue
        x = {k: v for k, v in e.items() if k != "seviye"}; x["seviye"] = "BAYRAK"
        if e["seviye"] == "OLCULEMEDI": x["olculemedi"] = True
        bay.append(x)
    r["hatalar"] = list(r.get("hatalar") or []) + hata
    r["bayraklar"] = list(r.get("bayraklar") or []) + bay
    oz = r.setdefault("ozet", {})
    oz["hata"] = int(oz.get("hata") or 0) + len(hata); oz["bayrak"] = int(oz.get("bayrak") or 0) + len(bay)
    oz["olculemedi"] = int(oz.get("olculemedi") or 0) + sum(1 for e in ekler if e["seviye"] == "OLCULEMEDI")
    s = r.get("sonuc")
    if hata: s = "HATA"
    elif bay and s == "GEC": s = "BAYRAK"
    r["sonuc"] = s; r["_uretim"]["sonuc"] = s
    r["kapi_saglandi"] = bool(r.get("kapi_saglandi")) and not hata
    if hata: r["hedef_alti"] = False
    r["izleme"] = dict(ozet, arac_surum=SURUM, ek_hata=len(hata), ek_bayrak=len(bay))
    h = [x for x in kapi.dogrula(r) if not x.startswith("kapi bilinmiyor")]
    if h: raise kapi.RaporHatasi(h, yol)
    ortak.atomik_yaz(yol, r)
    return r


def topla(film, kip, tur, gorev=None, merdiven=None, yol=None, asama=None, izleyici_atla=False):
    film = os.path.abspath(film)
    karar = puan_oku.seyirci_topla(film, kip, tur, gorev, merdiven, yol, asama)
    if kip in KAGIT: return karar
    rapor_yolu = os.path.join(film, karar["rapor"])
    raporlar = [r for r in puan_oku.raporlari_topla(os.path.join(film, "_RAPOR", "SEYIRCI", "%s_t%d" % (kip, tur))) if not r["sema_hatalari"]]
    ekler = persona_denetle(raporlar)
    iz, ozet = izleyici_ekleri(film, kip, tur, izleyici_atla); ekler += iz
    ekler += geri_gidis(film, kip, tur, karar)
    anl = sum(len((ortak.json_oku(r["yol"], {}) or {}).get("anlasilmayan_konusmalar") or []) for r in raporlar if r["yol"].endswith(".json"))
    if anl: ekler.append({"madde": "anlasilmayan_konusma", "seviye": "BAYRAK", "olcu": anl})
    if kip == "animatik": ekler += animatik_kosullari(film, tur)
    r = raporu_guncelle(rapor_yolu, ekler, ozet)
    kp = os.path.join(film, "_RAPOR", "SEYIRCI_KARAR_%s_t%d.json" % (kip.upper(), tur))
    k = ortak.json_oku(kp, {}) or {}
    k["izleme"] = {"ekler": ekler, "ozet": ozet, "sonuc": r["sonuc"], "kapi_saglandi": r["kapi_saglandi"]}
    k["sonuc"] = r["sonuc"]; k["kapi"] = r["kapi_saglandi"]; k["gecti"] = r["sonuc"] in ("GEC", "BAYRAK")
    ortak.atomik_yaz(kp, k)
    karar.update(sonuc=r["sonuc"], kapi=r["kapi_saglandi"], izleme=k["izleme"])
    if kip == "animatik" and r["kapi_saglandi"]:
        import animatik_imza
        ok, s = animatik_imza.imzala(film, tur, gorev)
        karar["animatik_imza"] = s.get("imza") if ok else {"reddedildi": s.get("nedenler")}
    return karar


def main(argv=None):
    ap = argparse.ArgumentParser(description="Seyirci turu toplama (kapı).")
    ap.add_argument("--kip", default="kagit"); ap.add_argument("--tur", type=int); ap.add_argument("--film")
    ap.add_argument("--izleyici-atla", action="store_true"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film: print("!! --film gerekli"); return 1
    if not os.path.isdir(film):
        try: film = os.path.join(ortak.yollar()["filmler"], film)
        except ortak.YolYok as e: print("!!", e); return 4
    if o.kip not in KAGIT + IZLEME: print("!! bilinmeyen kip: %s" % o.kip); return 1
    g = puan_oku.gorev_baglami(o.tur)
    yol = os.path.join(film, g["rapor"]) if g.get("rapor") else None
    try: k = topla(film, o.kip, g["tur_no"], g["id"], g.get("merdiven"), yol, g.get("asama"), o.izleyici_atla)
    except kapi.RaporHatasi as e: print("!! " + str(e)); return 1
    print(json.dumps({x: k.get(x) for x in ("sonuc", "medyan", "kapi", "hedef", "plato", "neden", "rapor", "animatik_imza") if x in k},
                     ensure_ascii=False)[:3000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
