"""VİDEO DENETİM — V2 (kimlik ve görünüm izi), V3 (adım zamanlaması ve bitiş tutması), K1ON / K1 geçiş ölçüleri (TASARIM §6.5, §7.2, D-13, D-15).

Kullanım:
  python video_denetim.py --klip [<plan,…>] [--blok KESIT|B03] --film <film>
        V2: klipten 0,5 sn arayla 17 kare → yüz sayısı değişimi (H), kimlik düşüşü (> 0,15 ve < 0,363 H; biri B), DINOv2 sıçraması
            (> 0,15 B), ilk kare sadakati (başlangıç görseline < 0,85 B), hareket enerjisi (beklenen_hiz verilmişse dışı B).
            Yüz izi _RAPOR/V2_<kapsam>/NNN_yuz.jsonl. → _RAPOR/V2_<kapsam>_t<tur>.json
        V3: hareket enerjisi eğrisinde her fiziksel/mikro adımın tepe anı adım penceresinden ≤ plan_zincir_zaman_sapma_max_sn (1,0) sapar (B);
            kesme anından önceki son 0,5 sn'nin enerjisi ≤ klibin medyanının %50'si (B: bitiş tutmadı); kesme anı karesi kare-tarifcisi·v3
            için _RAPOR/V3/kareler/NNN_kesme.jpg; kör gözlem raporu (_RAPOR/V3/gozlem_t<tur>_*.json) varsa bitiş olgu sonucu (H) okunur,
            yoksa ÖLÇÜLEMEDİ; dirsek açısı (poz) ÖLÇÜLEMEDİ (olcum.poz video kipi PR-11 sonrası). → _RAPOR/V3_<kapsam>_t<tur>.json
        İkisi de KUNYE/NNN.json kapilar.{V2, V3}'e yazılır (zincir uygunluğu ve kare_zinciri bunu okur).
  python video_denetim.py --gecis <A>,<B> --film <film>     K1 ölçüsü (A'nın kullanılan son karesi ↔ B'nin ilk karesi): parlaklık farkı
        (> 12/255 B), Lab ΔE (> 10 B), DINOv2 (< 0,80 H). → yazdırır (JSON)
  python video_denetim.py --onceden <A>,<B> --film <film>   K1ON: aynı ölçüler başlangıç görselleri arasında (A11 sonu)
Ölçüm arka uçları: numpy + ffmpeg (enerji, parlaklık; her yerde), olcum.kimlik (YuNet + SFace), olcum.gorunum (DINOv2), olcum.isik (Lab).
Kurulu olmayan ölçü ÖLÇÜLEMEDİ yazılır (= BAYRAK; asla GEÇ değildir).
Çıkış kodları: 0 rapor yazıldı · 1 girdi yok · 4 kullanım.
"""
import os, sys, re, json, glob, shutil, subprocess, tempfile, statistics
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi, esikler

SURUM = "video_denetim 1.0"
VARSAYILAN = {"v2_kare_aralik_sn": 0.5, "v2_kimlik_dusus_max": 0.15, "v2_kimlik_hata": 0.363, "v2_dino_sicrama_max": 0.15,
              "v2_ilk_kare_sadakat_min": 0.85, "plan_zincir_zaman_sapma_max_sn": 1.0, "v3_son_tutma_sn": 0.5, "v3_son_tutma_oran_max": 0.5,
              "k1_parlaklik_max": 12.0, "k1_lab_de_max": 10.0, "k1_dino_min": 0.80, "enerji_fps": 12}
ENERJI_BOYUT = (160, 90)


class Olculemedi(Exception): pass


def esik(ad):
    try:
        import esikler; v = esikler.yukle().get(ad)
        v = VARSAYILAN[ad] if v is None else v
    except Exception: v = VARSAYILAN[ad]
    if ad == "v2_kimlik_hata": v = max(float(v), 0.363)            # SFace HATA sınırı 0,363'ün altına inmez (gevşetilemez)
    return v


# ---------------------------------------------------------------- kare ve enerji
def _ffmpeg():
    if not shutil.which("ffmpeg"): raise Olculemedi("ffmpeg yok")


def enerji(yol, fps=None):
    """[(t, enerji)]: ardışık gri karelerin ortalama mutlak farkı (0–255). numpy + ffmpeg."""
    _ffmpeg()
    try: import numpy as np
    except ImportError: raise Olculemedi("numpy yok")
    fps = fps or esik("enerji_fps"); w, h = ENERJI_BOYUT
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", yol, "-vf", f"fps={fps},scale={w}:{h},format=gray",
                        "-f", "rawvideo", "-"], capture_output=True)
    if r.returncode != 0 or not r.stdout: raise Olculemedi("kareler okunamadı")
    k = np.frombuffer(r.stdout, dtype=np.uint8).reshape(-1, h, w).astype(np.float32)
    if len(k) < 2: return [], [float(k.mean()) if len(k) else 0.0]
    e = np.abs(np.diff(k, axis=0)).mean(axis=(1, 2))
    return [(round((i + 1) / fps, 3), float(x)) for i, x in enumerate(e)], [float(x) for x in k.mean(axis=(1, 2))]


def kare_cikar(yol, t, hedef):
    _ffmpeg(); os.makedirs(os.path.dirname(hedef), exist_ok=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", yol, "-frames:v", "1",
                    "-q:v", "2", hedef], check=True)
    return hedef


def kareler(yol, aralik, klasor):
    _ffmpeg()
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", yol, "-vf", f"fps={1.0 / aralik}", "-q:v", "3",
                    os.path.join(klasor, "k_%03d.jpg")], check=True)
    return sorted(glob.glob(os.path.join(klasor, "k_*.jpg")))


# ---------------------------------------------------------------- V2
def _kimlik():
    from olcum import kimlik
    ok, neden = kimlik.hazir()
    if not ok: raise Olculemedi(f"kimlik: {neden}")
    return kimlik


def _gorunum():
    from olcum import gorunum
    ok, neden = gorunum.hazir()
    if not ok: raise Olculemedi(f"DINOv2: {neden}")
    return gorunum


def v2_plan(film, no, p, iz_klasoru):
    """V2 ölçümleri (liste)."""
    yol = os.path.join(film, "SIRALI_VIDEO", f"{no:03d}.mp4"); bas = os.path.join(film, "SIRALI_GORSEL", f"{no:03d}.jpg")
    olc = []
    def m(madde, seviye, **k): olc.append(dict({"madde": madde, "plan": no, "seviye": seviye}, **k))
    d = tempfile.mkdtemp(prefix="v2_")
    try:
        try: ks = kareler(yol, esik("v2_kare_aralik_sn"), d)
        except (Olculemedi, subprocess.CalledProcessError) as e:
            m("V2", "OLCULEMEDI", neden=str(e)[:120]); return olc
        # kimlik ve yüz sayısı
        try:
            kim = _kimlik()
            ref = kim.yuzler(bas) if os.path.exists(bas) else []
            iz, sayilar, dusus, en_dusuk = [], [], 0.0, None
            ilk = None
            for i, k in enumerate(ks):
                y = kim.yuzler(k); sayilar.append(len(y))
                sims = [max((kim.benzerlik(r["vektor"], f["vektor"]) for f in y), default=0.0) for r in ref]
                s = min(sims) if sims else None
                if s is not None:
                    ilk = s if ilk is None else ilk; dusus = max(dusus, ilk - s); en_dusuk = s if en_dusuk is None else min(en_dusuk, s)
                iz.append({"t": round(i * esik("v2_kare_aralik_sn"), 2), "yuz": len(y), "benzerlik": None if s is None else round(s, 4)})
            os.makedirs(iz_klasoru, exist_ok=True)
            with open(os.path.join(iz_klasoru, f"{no:03d}_yuz.jsonl"), "w", encoding="utf-8") as f:
                for x in iz: f.write(json.dumps(x) + "\n")
            beklenen = len((p.get("zanaat") or {}).get("kadrajdakiler") or []) or (len(ref) if ref else None)
            if beklenen is not None and any(c != beklenen for c in sayilar):
                m("yuz_sayisi", "HATA", olcu=sorted(set(sayilar)), esik=beklenen, kok_neden="fazla_kisi" if max(sayilar) > beklenen else "karakter_kayboldu")
            else: m("yuz_sayisi", "GEC", olcu=beklenen)
            if en_dusuk is None: m("kimlik", "OLCULEMEDI", neden="başlangıç görselinde ya da karelerde yüz yok")
            else:
                a, b = dusus > esik("v2_kimlik_dusus_max"), en_dusuk < esik("v2_kimlik_hata")
                m("kimlik", "HATA" if (a and b) else ("BAYRAK" if (a or b) else "GEC"), olcu={"dusus": round(dusus, 4), "en_dusuk": round(en_dusuk, 4)},
                  esik={"dusus": esik("v2_kimlik_dusus_max"), "hata": esik("v2_kimlik_hata")}, **({"kok_neden": "yuz_degisti"} if a and b else {}))
        except Olculemedi as e: m("kimlik", "OLCULEMEDI", neden=str(e)[:120])
        except Exception as e: m("kimlik", "OLCULEMEDI", neden=f"kimlik ölçümü düştü: {e.__class__.__name__}")
        # DINOv2 sıçraması ve ilk kare sadakati
        try:
            gor = _gorunum()
            vs = [gor.dinov2(k) for k in ks]
            sic = max((1 - gor.benzerlik(vs[i - 1], vs[i]) for i in range(1, len(vs))), default=0.0)
            m("dino_sicrama", "BAYRAK" if sic > esik("v2_dino_sicrama_max") else "GEC", olcu=round(sic, 4), esik=esik("v2_dino_sicrama_max"))
            if os.path.exists(bas) and vs:
                s = gor.benzerlik(gor.dinov2(bas), vs[0])
                m("ilk_kare_sadakati", "BAYRAK" if s < esik("v2_ilk_kare_sadakat_min") else "GEC", olcu=round(s, 4), esik=esik("v2_ilk_kare_sadakat_min"))
        except Olculemedi as e: m("dino", "OLCULEMEDI", neden=str(e)[:120])
        except Exception as e: m("dino", "OLCULEMEDI", neden=f"DINOv2 ölçümü düştü: {e.__class__.__name__}")
    finally: shutil.rmtree(d, ignore_errors=True)
    # hareket hızı (EO4): _derlenir.beklenen_hiz [min, max] (enerji birimiyle) verilmişse
    bh = (p.get("_derlenir") or {}).get("beklenen_hiz")
    try:
        e, _ = enerji(yol); med = statistics.median(x for _, x in e) if e else 0.0
        if isinstance(bh, list) and len(bh) == 2:
            m("hareket_hizi", "GEC" if bh[0] <= med <= bh[1] else "BAYRAK", olcu=round(med, 3), esik=bh)
    except Olculemedi as ex: m("hareket_hizi", "OLCULEMEDI", neden=str(ex))
    return olc


# ---------------------------------------------------------------- V3
def adimlar(p):
    return [a for a in (p.get("zanaat") or {}).get("eylem_zinciri") or [] if a.get("tur") in ("fiziksel", "mikro")
            and isinstance(a.get("bas"), (int, float)) and isinstance(a.get("bit"), (int, float))]


def kesme_ani(p, sure):
    d = p.get("_derlenir") or {}; k = p.get("kullanim") or {}
    if isinstance(d.get("kesme_nokta_sn"), (int, float)): return float(d["kesme_nokta_sn"])
    if isinstance(k.get("bas"), (int, float)) and isinstance(k.get("sure"), (int, float)): return float(k["bas"]) + float(k["sure"])
    return sure


def v3_olc(no, p, e, sure):
    """Enerji eğrisinden V3 kod ölçümleri."""
    olc = []
    def m(madde, seviye, **k): olc.append(dict({"madde": madde, "plan": no, "seviye": seviye}, **k))
    if not e: m("V3_enerji", "OLCULEMEDI", neden="enerji eğrisi yok"); return olc
    sapma_max = esik("plan_zincir_zaman_sapma_max_sn")
    hareketli = [x for _, x in e if x > 1e-3]; ref = statistics.median(hareketli) if hareketli else 0.0
    for a in adimlar(p):
        w0, w1 = float(a["bas"]) - 2 * sapma_max, float(a["bit"]) + 2 * sapma_max      # tepe aramasının penceresi
        icinde = [(t, x) for t, x in e if w0 <= t <= w1]
        if not icinde: m("adim_tepe", "OLCULEMEDI", adim=a.get("id"), neden="pencerede kare yok"); continue
        tepe, tepe_e = max(icinde, key=lambda z: z[1])
        if tepe_e <= 0.25 * ref:
            m("adim_tepe", "BAYRAK", adim=a.get("id"), olcu={"tepe_enerji": round(tepe_e, 3)}, esik=round(0.25 * ref, 3),
              neden="adım penceresinde hareket yok"); continue
        sap = 0.0 if a["bas"] <= tepe <= a["bit"] else round(min(abs(tepe - a["bas"]), abs(tepe - a["bit"])), 3)
        m("adim_tepe", "GEC" if sap <= sapma_max else "BAYRAK", adim=a.get("id"), olcu={"tepe_sn": tepe, "sapma_sn": sap}, esik=sapma_max)
    kes = kesme_ani(p, sure); son = esik("v3_son_tutma_sn")
    med = statistics.median(x for _, x in e) or 0.0
    if med <= 1e-3:          # klip çoğunlukla kıpırtısız (sentetik ya da tam durgun): kıyas, hareketli karelerin medyanı
        hareketli = [x for _, x in e if x > 1e-3]; med = statistics.median(hareketli) if hareketli else 0.0
    sonlar = [x for t, x in e if kes - son <= t <= kes]
    if sonlar:
        o = statistics.mean(sonlar); siniri = esik("v3_son_tutma_oran_max") * med
        m("bitis_tutma", "GEC" if o <= siniri else "BAYRAK", olcu=round(o, 3), esik=round(siniri, 3), kesme_sn=kes)
    else: m("bitis_tutma", "OLCULEMEDI", neden="kesme anından önce kare yok")
    m("dirsek_acisi", "OLCULEMEDI", neden="video poz ölçümü yok (olcum.poz video kipi)")
    return olc


def gozlem_oku(film, tur):
    """kare-tarifcisi·v3 kör gözlem sonuçları: {plan: "GEC"|"HATA"|"BAYRAK"} (_RAPOR/V3/gozlem_t<tur>_*.json; biçim: {"planlar": {..}})."""
    out = {}
    for y in sorted(glob.glob(os.path.join(film, "_RAPOR", "V3", f"gozlem_t{tur}_*.json"))):
        d = ortak.json_oku(y, {}) or {}
        for k, v in (d.get("planlar") or {}).items():
            s = (v or {}).get("bitis_olgulari") if isinstance(v, dict) else v
            if isinstance(s, str): out[int(k)] = s.upper()
    return out


# ---------------------------------------------------------------- toplu koşu
def _gorev_turu():
    g = ortak.json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV") or "", "GOREV.json"), {}) if os.environ.get("YZ_FILM_GOREV") else {}
    t = (g or {}).get("tur_no"); return int(t) if isinstance(t, int) and t >= 1 else 1


def _kunye_kapi(film, no, kapi_adi, olc, rel):
    import kapi
    p = os.path.join(film, "KUNYE", f"{no:03d}.json"); k = ortak.json_oku(p, None)
    if not isinstance(k, dict): return
    s = kapi.en_kotu([kapi.madde_sonucu(m["seviye"]) for m in olc if m.get("plan") == no] or ["GEC"])
    k.setdefault("kapilar", {})[kapi_adi] = {"sonuc": s, "rapor": rel}; ortak.atomik_yaz(p, k)


def _kuyruk(olc, kaynak):
    out = []
    for m in olc:
        if m["seviye"] != "HATA" or not m.get("kok_neden"): continue
        out.append({"plan": m["plan"], "tur": "video", "seviye": "HATA", "kok_neden": m["kok_neden"], "cozum": "yeniden_cek", "dilim": "goruntu",
                    "sifir_kredi": {"denendi": True, "gerekce": f"{kaynak} {m['madde']} klip boyunca (ölçüm); kırpma kusuru gidermez"},
                    "kanit": {"madde": m["madde"], "olcu": m.get("olcu")}})
    return out


def klip_denetle(film, nolar=None, blok=None, tur=None, gorev=None):
    """V2 + V3. (V2 raporu, V3 raporu)."""
    import kapi
    film = os.path.abspath(film); tur = tur or _gorev_turu()
    doc = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    pl = {int(p["no"]): p for p in doc.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
    kapsam = "KESIT" if str(blok or "").startswith("KESIT") else (str(blok) if blok and blok != "*" else "FILM")
    if nolar is None:
        if kapsam == "KESIT":
            import blok_plani
            BP = ortak.json_oku(os.path.join(film, "BLOK_PLANI.json"), {}) or {}
            nolar = [n for b in BP.get("bloklar") or [] if str(b.get("id", "")).startswith("KESIT") for n in b.get("planlar") or []]
        else: nolar = sorted(int(os.path.basename(x)[:3]) for x in glob.glob(os.path.join(film, "KUNYE", "[0-9][0-9][0-9].json")))
    gz = gozlem_oku(film, tur)
    v2, v3, birim = [], [], []
    rk = os.path.join(film, "_RAPOR")
    for no in sorted(set(int(n) for n in nolar)):
        yol = os.path.join(film, "SIRALI_VIDEO", f"{no:03d}.mp4")
        if not os.path.exists(yol): continue
        birim.append(no); p = pl.get(no) or {"no": no}
        v2 += v2_plan(film, no, p, os.path.join(rk, f"V2_{kapsam}"))
        try:
            e, _ = enerji(yol); sure = e[-1][0] if e else 0.0
            v3 += v3_olc(no, p, e, sure)
            try: kare_cikar(yol, kesme_ani(p, sure) - 0.04, os.path.join(rk, "V3", "kareler", f"{no:03d}_kesme.jpg"))
            except (Olculemedi, subprocess.CalledProcessError): pass
        except Olculemedi as ex: v3.append({"madde": "V3_enerji", "plan": no, "seviye": "OLCULEMEDI", "neden": str(ex)})
        g = gz.get(no)
        if g is None: v3.append({"madde": "bitis_olgulari", "plan": no, "seviye": "OLCULEMEDI", "neden": "kare-tarifcisi·v3 gözlemi yok"})
        else: v3.append({"madde": "bitis_olgulari", "plan": no, "seviye": "HATA" if g == "HATA" else ("BAYRAK" if g != "GEC" else "GEC"),
                         **({"kok_neden": "hikaye_adimi_ekranda_yok"} if g == "HATA" else {})})
    asama = "A14a" if kapsam == "KESIT" else "A14"
    y2, r2 = kapi.kaydet(rk, "V2", kapsam, v2, tur=tur, tur_dosyada=True, asama=asama, gorev=gorev, arac_surum=SURUM, birimler=birim,
                         kuyruk=_kuyruk(v2, "V2"))
    y3, r3 = kapi.kaydet(rk, "V3", kapsam, v3, tur=tur, tur_dosyada=True, asama=asama, gorev=gorev, arac_surum=SURUM, birimler=birim,
                         kuyruk=_kuyruk(v3, "V3"))
    for no in birim:
        _kunye_kapi(film, no, "V2", v2, os.path.relpath(y2, film).replace(os.sep, "/"))
        _kunye_kapi(film, no, "V3", v3, os.path.relpath(y3, film).replace(os.sep, "/"))
    return r2, r3


# ---------------------------------------------------------------- K1 / K1ON
def gecis_olc(a_kare, b_kare):
    """İki kare arası K1 ölçüleri (sözlük; ölçülemeyen alan None + neden)."""
    out = {"parlaklik_fark": None, "lab_de": None, "dino": None, "olculemedi": {}}
    try:
        from olcum import teknik, isik
        import numpy as np
        ga, gb = teknik.gri(a_kare), teknik.gri(b_kare)
        out["parlaklik_fark"] = round(abs(float(np.asarray(ga).mean()) - float(np.asarray(gb).mean())), 3)
        out["lab_de"] = round(float(isik.delta_e(isik.ortalama_lab(a_kare), isik.ortalama_lab(b_kare))), 3)
    except Exception as e: out["olculemedi"]["parlaklik_lab"] = e.__class__.__name__
    try:
        g = _gorunum(); out["dino"] = round(float(g.benzerlik(g.dinov2(a_kare), g.dinov2(b_kare))), 4)
    except Exception as e: out["olculemedi"]["dino"] = str(e)[:80]
    seviye = []
    if out["dino"] is not None and out["dino"] < esik("k1_dino_min"): seviye.append("HATA")
    if out["parlaklik_fark"] is not None and out["parlaklik_fark"] > esik("k1_parlaklik_max"): seviye.append("BAYRAK")
    if out["lab_de"] is not None and out["lab_de"] > esik("k1_lab_de_max"): seviye.append("BAYRAK")
    out["seviye"] = "HATA" if "HATA" in seviye else ("BAYRAK" if seviye or out["olculemedi"] else "GEC")
    return out


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    film = argv[argv.index("--film") + 1] if "--film" in argv else None
    if not film or not os.path.isdir(film): print("film klasörü yok (--film)"); return 1
    film = os.path.abspath(film)
    for k in ("--gecis", "--onceden"):
        if k in argv:
            a, b = [int(x) for x in argv[argv.index(k) + 1].split(",")[:2]]
            if k == "--onceden":
                ka, kb = (os.path.join(film, "SIRALI_GORSEL", f"{n:03d}.jpg") for n in (a, b))
            else:
                d = tempfile.mkdtemp(prefix="k1_"); doc = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
                pl = {int(p["no"]): p for p in doc.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
                va = os.path.join(film, "SIRALI_VIDEO", f"{a:03d}.mp4"); vb = os.path.join(film, "SIRALI_VIDEO", f"{b:03d}.mp4")
                try:
                    from kalite_denetim import probe
                    ka = kare_cikar(va, kesme_ani(pl.get(a) or {}, probe(va)["sure"]) - 0.04, os.path.join(d, "a.jpg"))
                    kb = kare_cikar(vb, float((pl.get(b) or {}).get("kullanim", {}).get("bas") or 0) + 0.04, os.path.join(d, "b.jpg"))
                except Exception as e: print(json.dumps({"seviye": "OLCULEMEDI", "neden": str(e)[:120]}, ensure_ascii=False)); return 0
            print(json.dumps(gecis_olc(ka, kb), ensure_ascii=False)); return 0
    if "--dudak" in argv or "--islem" in argv:
        print("--dudak / --islem PR-12'de (dudak_denetim.py, kurgu) gelir."); return 4
    if "--klip" not in argv: print(__doc__); return 4
    blok = argv[argv.index("--blok") + 1] if "--blok" in argv else None
    i = argv.index("--klip"); nolar = None
    if i + 1 < len(argv) and re.fullmatch(r"[0-9][0-9,]*", argv[i + 1]): nolar = [int(x) for x in argv[i + 1].split(",") if x]
    r2, r3 = klip_denetle(film, nolar, blok=blok, gorev=os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None)
    print(f"V2: {r2['sonuc']} {r2['ozet']} · V3: {r3['sonuc']} {r3['ozet']}"); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
