"""DİLİM — yazar ajanlarına HIKAYE/SAHNELER dilimi (TASARIM §6.2, §1.3 A07a/A07b, [SON] O-12; [YN2] Y1/Y3 girdileri).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"):
  python dilim.py --asama A07b --film <film>            sahne grubu planları: _YONETMEN/DILIM.json + _YONETMEN/DILIM/G<i>.json
  python dilim.py --asama A07b --grup <i> --film <film>  tek grubun dilimini yeniler (sıralı çiftte önceki grup bitince)
  python dilim.py --asama A07a --film <film>            parti haritaları: _YONETMEN/DILIM/P<n>.json
Kurallar:
  - Hikâye sahnesi = sahne grubu (1:1, HIKAYE.json sırası). G<i> = i. sahne. film.py "sahne_grubu" adedini DILIM.json'daki
    gruplar'dan sayar.
  - Paralel görevlere önceki sahnenin SÖZLEŞMEDEKİ cikis_durumu verilir (HIKAYE ya da haritanın tam şeması).
  - Yalnız aynı mekânda ve aynı zamanda (gün, saat; atlama yok) süren ardışık sahne çiftinde önceki sahnenin son 2 planının çözülmüş
    bitişi verilir; o grup "bagimli: G<i-1>" taşır ve sırayla koşar. Önceki planlar henüz yoksa "bekliyor" yazılır ve grup
    --grup <i> ile yenilenir.
  - Dilim yazarın sözleşmesidir (amaç, değer, vuruş dahil); kör paket DEĞİLDİR (kör roller kor_paket.py'den beslenir).
Çıkış kodları: 0 BİTTİ · 1 HATA (HIKAYE.json yok/bozuk ya da sahne yok) · 4 ORTAM (bilinmeyen aşama).
"""
import os, sys, re, json, time, glob, hashlib, argparse
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "dilim 1.0"
SOZLESME_ALANLARI = ("id", "hikaye_partisi", "mekan", "zaman", "sahne_tipi", "hedef_sure_sn", "vurus", "hedef_duygu", "yogunluk",
                     "sahne_degeri", "risk", "merak_ac", "merak_kapat", "kurulum", "kullanim_bilgi", "ironi", "giris_durumu",
                     "cikis_durumu", "bilgi_degisimi")
HARITA_ALANLARI = ("plan_hedef", "kalip", "eksen", "kamera_tarafi", "ekran_yonu", "isik", "yasaklar", "kurulumlar", "yasak_ardisik",
                   "giris_durumu", "cikis_durumu", "sure_hedef_sn")
PARTI_ALANLARI = ("id", "sahneler", "sure_hedef_sn", "tek_cumle", "b3_kim_nerede", "b4_nesne_yolu", "b6_mekan_olgulari",
                  "b7_parti_kancasi")


class DilimHatasi(Exception):
    pass


def simdi(): return time.strftime("%Y-%m-%dT%H:%M:%S")


def imza(*yollar):
    h = hashlib.sha1()
    for p in yollar:
        if os.path.isfile(p):
            with open(p, "rb") as f: h.update(f.read())
    return h.hexdigest()[:8]


def zarf(asama, sonuc, girdi_imza):
    return {"asama": asama, "gorev": os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None, "girdi_imza": girdi_imza,
            "arac_surum": SURUM, "esik_surum": None, "sonuc": sonuc, "zaman": simdi(), "ortam": "yerel" if os.name == "nt" else "bulut"}


def hikaye(film):
    h = ortak.json_oku(os.path.join(film, "HIKAYE.json"))
    if not isinstance(h, dict): raise DilimHatasi("HIKAYE.json yok ya da bozuk (A06 devri bitmeli).")
    if not [s for s in h.get("sahneler") or [] if isinstance(s, dict)]: raise DilimHatasi("HIKAYE.json'da sahne yok.")
    return h


def haritalar(film):
    """Haritalardaki sahne sözleşmeleri: {sahne_id: {...}} (HARITA_P<n>.json; biçim: sahneler {S: {...}} ya da liste)."""
    out = {}
    for p in sorted(glob.glob(os.path.join(film, "_YONETMEN", "HARITA_P*.json"))):
        h = ortak.json_oku(p, {}) or {}
        ss = h.get("sahneler") or h.get("sahne_gruplari") or {}
        if isinstance(ss, list): ss = {x.get("id") or x.get("sahne"): x for x in ss if isinstance(x, dict)}
        for sid, v in ss.items():
            if isinstance(v, dict): out[sid] = dict(v, _harita=os.path.relpath(p, film).replace("\\", "/"))
    return out


def ayni_an(a, b):
    """İki ardışık sahne aynı mekânda ve zamanda mı (çözülmüş plan bitişi yalnız bu çifte verilir)."""
    za, zb = a.get("zaman") or {}, b.get("zaman") or {}
    if not a.get("mekan") or a.get("mekan") != b.get("mekan"): return False
    if zb.get("atlama") not in (None, "", "yok"): return False
    saat = lambda z: z.get("saat") or z.get("gun_saati")
    return za.get("gun") == zb.get("gun") and saat(za) == saat(zb)


def plan_bitisi(film, i):
    """G<i>'nin son 2 planının çözülmüş bitişi (yazılmış plan dosyasından); yoksa None."""
    p = ortak.json_oku(os.path.join(film, "_YONETMEN", "PLANLAR", "G%d.json" % i))
    if not isinstance(p, dict): return None
    planlar = p.get("planlar") or p.get("sahneler") or []
    son = []
    for x in [x for x in planlar if isinstance(x, dict)][-2:]:
        z = x.get("zanaat") or x
        son.append({"kod": z.get("kod"), "bitis_durumu": (x.get("_derlenir") or {}).get("bitis_durumu") or z.get("bitis_durumu"),
                    "kadrajdakiler": z.get("kadrajdakiler"), "eylem_son": (z.get("eylem_zinciri") or [None])[-1]})
    return son


def replikler(h, s):
    rep = {r.get("id"): r for r in h.get("replikler") or [] if isinstance(r, dict)}
    ids = [d for d in (s.get("ekran") or {}).get("duyulan") or [] if isinstance(d, str)]
    ids += [r.get("id") for r in rep.values() if r.get("sahne") == s.get("id") and r.get("id") not in ids]
    return [{k: rep[i].get(k) for k in ("id", "karakter", "metin", "teslim", "ton_fiili", "tr", "ilk_replik") if k in rep[i]}
            for i in ids if i in rep]


def kroki(film, s):
    d = os.path.join(film, "_YONETMEN", "KROKI")
    adlar = [s.get("mekan"), s.get("id")]
    return [os.path.relpath(os.path.join(d, a + ".png"), film).replace("\\", "/") for a in adlar
            if a and os.path.isfile(os.path.join(d, a + ".png"))]


def grup_dilimi(film, h, har, ss, i):
    s = ss[i - 1]; sid = s.get("id") or "S%02d" % i
    soz = {k: s[k] for k in SOZLESME_ALANLARI if k in s}
    hs = har.get(sid) or {}
    harita = {k: hs[k] for k in HARITA_ALANLARI if k in hs}
    for k in ("giris_durumu", "cikis_durumu"):
        if k in hs: soz[k] = hs[k]                                            # haritanın tam şeması hikâyeyi genişletir
    d = {"_uretim": zarf("A07b", "GEC", imza(os.path.join(film, "HIKAYE.json"))), "grup": "G%d" % i, "sahne": sid,
         "sozlesme": soz, "harita": harita, "harita_kaynak": hs.get("_harita"), "ekran": s.get("ekran") or {},
         "replikler": replikler(h, s), "kroki": kroki(film, s), "onceki": None, "bagimli": None, "onceki_plan_bitisi": None}
    if i > 1:
        o = ss[i - 2]; ohs = har.get(o.get("id")) or {}
        d["onceki"] = {"sahne": o.get("id"), "cikis_durumu": ohs.get("cikis_durumu") or o.get("cikis_durumu")}
        if ayni_an(o, s):
            d["bagimli"] = "G%d" % (i - 1)
            b = plan_bitisi(film, i - 1)
            d["onceki_plan_bitisi"] = {"kaynak": "_YONETMEN/PLANLAR/G%d.json" % (i - 1), "planlar": b} if b else {"durum": "bekliyor"}
    return d


def a07b(film, grup=None):
    h = hikaye(film); har = haritalar(film)
    ss = [s for s in h["sahneler"] if isinstance(s, dict)]
    hedef = range(1, len(ss) + 1) if grup is None else [grup]
    if grup is not None and not 1 <= grup <= len(ss): raise DilimHatasi("Grup yok: G%s (1–%d)." % (grup, len(ss)))
    gruplar = []
    for i in hedef:
        d = grup_dilimi(film, h, har, ss, i)
        ortak.atomik_yaz(os.path.join(film, "_YONETMEN", "DILIM", "G%d.json" % i), d)
    for i in range(1, len(ss) + 1):
        bag = "G%d" % (i - 1) if i > 1 and ayni_an(ss[i - 2], ss[i - 1]) else None
        gruplar.append({"i": i, "grup": "G%d" % i, "sahne": ss[i - 1].get("id"), "parti": ss[i - 1].get("hikaye_partisi"),
                        "bagimli": bag, "dosya": "_YONETMEN/DILIM/G%d.json" % i})
    if grup is None:
        ortak.atomik_yaz(os.path.join(film, "_YONETMEN", "DILIM.json"),
                         {"_surum": 1, "_uretim": zarf("A07b", "GEC", imza(os.path.join(film, "HIKAYE.json"))), "asama": "A07b",
                          "gruplar": gruplar, "sirali_ciftler": [[g["bagimli"], g["grup"]] for g in gruplar if g["bagimli"]]})
    return gruplar


def a07a(film):
    h = hikaye(film)
    ss = [s for s in h["sahneler"] if isinstance(s, dict)]
    partiler = [p for p in h.get("partiler") or [] if isinstance(p, dict)] or [{"id": "P1"}]
    sira = [s.get("id") for s in ss]; out = []
    for n, p in enumerate(partiler, 1):
        r = p.get("sahneler") or []
        if len(r) == 2 and r[0] in sira and r[1] in sira: ids = sira[sira.index(r[0]): sira.index(r[1]) + 1]
        else: ids = [s.get("id") for s in ss if (s.get("hikaye_partisi") or "P1") == p.get("id")] or list(r)
        sahneler = [{**{k: s[k] for k in SOZLESME_ALANLARI if k in s}, "ekran": s.get("ekran") or {}, "replikler": replikler(h, s)}
                    for s in ss if s.get("id") in ids]
        d = {"_uretim": zarf("A07a", "GEC", imza(os.path.join(film, "HIKAYE.json"))), "parti": p.get("id") or "P%d" % n,
             "parti_bilgisi": {k: p[k] for k in PARTI_ALANLARI if k in p}, "sahneler": sahneler,
             "mekanlar": [m for m in h.get("mekanlar") or [] if isinstance(m, dict) and m.get("id") in {s.get("mekan") for s in sahneler}]}
        yol = os.path.join(film, "_YONETMEN", "DILIM", "P%d.json" % n); ortak.atomik_yaz(yol, d)
        out.append({"parti": d["parti"], "dosya": os.path.relpath(yol, film).replace("\\", "/"), "sahne": len(sahneler)})
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Yazar ajan dilimleri.")
    ap.add_argument("--asama", required=True); ap.add_argument("--grup", type=int); ap.add_argument("--film")
    ap.add_argument("--json", action="store_true"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film): print("!! --film <film klasörü> gerekli."); return 1
    try:
        if o.asama == "A07b": r = a07b(os.path.abspath(film), o.grup)
        elif o.asama == "A07a": r = a07a(os.path.abspath(film))
        else: print("!! dilim.py bu aşamayı bilmiyor: %s (A07a, A07b)." % o.asama); return 4
    except DilimHatasi as e:
        print("!! " + str(e)); return 1
    print(json.dumps({"asama": o.asama, "dilimler": r}, ensure_ascii=False) if o.json else
          "Dilimler hazır (%s): %d" % (o.asama, len(r)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
