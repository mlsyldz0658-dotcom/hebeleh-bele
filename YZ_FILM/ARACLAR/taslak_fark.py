"""TASLAK FARK — kullanıcının CapCut taslağını SALT OKUNUR inceler (TASARIM §6.7, D-30; [KU2] KR11, §4.5.7).

Kullanım:
  python taslak_fark.py --film <film> [--klasor <taslak klasörü>]     → KURGU/TASLAK_FARK.json (film.py "notlar oku" konumsal da çağırır)
  python taslak_fark.py --film <film> --oz-denetim [--klasor <k>]      yeni kurulan ya da klonlanmış taslakta fark 0 · boşluk 0 · eksik medya 0 ·
                                                                       süre = KURGU_PLANI ±1 kare (değilse çıkış 1)
  python taslak_fark.py --film <film> --plana-isle                     kullanıcının kararlarını KURGU_PLANI'na KİLİTLİ işler (yeni sürüm, T3):
                                                                       kırpma → kullanim_kaynak/kilit "kullanici"; silme → kesilen; taşıma → sıra
Okuma: draft_content.json (+ Timelines/ kopyası; daha yeniyse o) "rb" ile açılır; kaynağa hiçbir şey yazılmaz, inceleme kopyası
KURGU/_TASLAK_KOPYA/'ya alınır. Şifreli taslak tanınır ve durulur (yedek yol tek cümleyle söylenir; çıkış 2).
Bulunanlar: kırpılan, silinen, taşınan, eklenen klipler · Klipler boşlukları · kayan kanallar (Diyalog, Ambiyans …) · kullanıcı öğeleri
(kendi yazısı, renk ayarı, yeni kanal) · kullanıcı ses düzenlemesi (bizim ses kanallarında seviye değişimi) · eksik medya · süre.
Eşleme son_capcut_projesi.json v2 segment_id'leriyle yapılır (aynı klipten iki plan çıksa da doğru plan bulunur).
Çıkış kodları: 0 tamam (fark var ya da yok) · 1 öz denetim HATA · 2 taslak ya da proje kaydı yok / şifreli · 4 kullanım.
"""
import os, sys, time, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kurgu_ortak as ko, capcut_taslak as ct

SURUM = "taslak_fark 1.0"
TOL = ko.KARE + 1e-3
SIFRELI_BILGI = ("CapCut bu taslağı şifreli kaydetmiş; okuyamıyorum. Notlarını CapCut'ta altyazı olarak dışa aktarıp GELENLER'e koyabilirsin "
                 "ya da CapCut sürümünü sabitleyebiliriz.")


def proje_oku(kok, yayin=False):
    return ortak.json_oku(os.path.join(kok, "KURGU", "son_capcut_projesi_yayin.json" if yayin else "son_capcut_projesi.json"))


def kopya_al(kok, okunan):
    hedef = os.path.join(kok, "KURGU", "_TASLAK_KOPYA", time.strftime("%Y%m%d-%H%M%S")); os.makedirs(hedef, exist_ok=True)
    shutil.copyfile(okunan["yol"], os.path.join(hedef, os.path.basename(okunan["yol"])))
    return hedef


def fark(kok, proje, okunan):
    ic = okunan["icerik"]; ds = ct.segmentler(ic); bizim = {s["segment_id"]: s for s in proje.get("segmentler") or []}
    yazilar = set(proje.get("benim_yazilarim") or [])
    dk = sorted([s for s in ds if s["kanal"] == "Klipler"], key=lambda s: s["bas"]); dk_id = {s["segment_id"]: s for s in dk}
    bk = sorted([s for s in bizim.values() if s["kanal"] == "Klipler"], key=lambda s: s["bas"])
    out = {"taslak": proje.get("proje"), "klasor": proje.get("klasor"), "kaynak_ozet": ko.klasor_ozeti(proje["klasor"]) if os.path.isdir(proje.get("klasor") or "") else None,
           "okuma": "salt_okunur", "sifreli": False, "klipler": [], "eklenen_klipler": [], "bosluklar": [], "kayan_kanallar": [],
           "kullanici_ogeleri": [], "kullanici_ses_duzenlemesi": [], "eksik_medya": [], "kullanici_yazilari": 0}
    eski_sira = {s["segment_id"]: i for i, s in enumerate(bk)}
    kalan = [s for s in bk if s["segment_id"] in dk_id]
    yeni_sira = {s["segment_id"]: i for i, s in enumerate(sorted(kalan, key=lambda s: dk_id[s["segment_id"]]["bas"]))}
    kalan_eski = {s["segment_id"]: i for i, s in enumerate(kalan)}
    for s in bk:
        d = dk_id.get(s["segment_id"])
        if not d: out["klipler"].append({"plan": s.get("plan"), "segment_id": s["segment_id"], "degisim": "silindi"}); continue
        ea = s.get("kaynak_aralik") or {}
        if ea and d["kaynak_bas"] is not None and (abs(d["kaynak_bas"] - ea["bas"]) > TOL or abs(d["kaynak_sure"] - ea["sure"]) > TOL):
            out["klipler"].append({"plan": s.get("plan"), "segment_id": s["segment_id"], "degisim": "kirpildi", "eski": ea,
                                   "yeni": {"bas": round(d["kaynak_bas"], 3), "sure": round(d["kaynak_sure"], 3)}})
        if yeni_sira[s["segment_id"]] != kalan_eski[s["segment_id"]]:
            out["klipler"].append({"plan": s.get("plan"), "segment_id": s["segment_id"], "degisim": "tasindi",
                                   "eski_sira": eski_sira[s["segment_id"]], "yeni_sira": yeni_sira[s["segment_id"]]})
    for d in dk:
        if d["segment_id"] not in bizim: out["eklenen_klipler"].append({"segment_id": d["segment_id"], "yol": d["yol"], "bas": d["bas"], "sure": d["sure"]})
    for a, b in zip(dk, dk[1:]):
        bos = b["bas"] - (a["bas"] + a["sure"])
        if bos > TOL: out["bosluklar"].append({"bas": round(a["bas"] + a["sure"], 3), "sure": round(bos, 3)})
    if dk and dk[0]["bas"] > TOL: out["bosluklar"].insert(0, {"bas": 0.0, "sure": round(dk[0]["bas"], 3)})
    ds_id = {s["segment_id"]: s for s in ds}; kayan = set()
    for sid, s in bizim.items():
        if s["kanal"] == "Klipler": continue
        d = ds_id.get(sid)
        if not d or abs(d["bas"] - s["bas"]) > TOL or d["kanal"] != s["kanal"]: kayan.add(s["kanal"])
        if d and s["kanal"] in ct.SES_KANALLARI and s.get("ses") is not None and d.get("ses") is not None and abs(float(d["ses"]) - float(s["ses"])) > 0.01:
            out["kullanici_ses_duzenlemesi"].append({"kanal": s["kanal"], "segment_id": sid,
                                                     "degisim": f"seviye {ko.db(float(d['ses']) or 1e-6) - ko.db(float(s['ses']) or 1e-6):+.1f} dB",
                                                     "ses": d["ses"]})
    for sid, s in bizim.items():
        d = ds_id.get(sid)
        if s["kanal"] == "Klipler" and d and s.get("ses") is not None and d.get("ses") not in (None, s["ses"]):
            out["kullanici_ses_duzenlemesi"].append({"kanal": "Klipler", "segment_id": sid, "degisim": "klip sesi açıldı", "ses": d["ses"]})
    out["kayan_kanallar"] = sorted(kayan)
    for d in ds:
        if d["segment_id"] in bizim: continue
        if d["tur"] == "text" or d.get("malzeme_turu") == "texts":
            if (d.get("metin") or "").strip() and d["metin"] not in yazilar:
                out["kullanici_ogeleri"].append({"tur": "yazi", "segment_id": d["segment_id"], "kanal": d["kanal"], "bas": d["bas"],
                                                 "metin": d["metin"]})
        elif d["kanal"] not in ("Klipler",):
            out["kullanici_ogeleri"].append({"tur": "kanal_ogesi", "segment_id": d["segment_id"], "kanal": d["kanal"], "yol": d.get("yol")})
    for tur in ("effects", "filters", "adjusts", "video_effects"):
        if (ic.get("materials") or {}).get(tur): out["kullanici_ogeleri"].append({"tur": "renk_ayari" if tur in ("filters", "adjusts") else "efekt",
                                                                                 "adet": len(ic["materials"][tur])})
    out["kullanici_yazilari"] = sum(1 for x in out["kullanici_ogeleri"] if x["tur"] == "yazi")
    for d in ds:
        if d.get("yol") and not os.path.exists(d["yol"]): out["eksik_medya"].append(d["yol"])
    out["eksik_medya"] = sorted(set(out["eksik_medya"]))
    out["sure"] = {"taslak": ct.sn(ic.get("duration") or 0), "proje": proje.get("sure_sn")}
    out["fark_var"] = bool(out["klipler"] or out["eklenen_klipler"] or out["kayan_kanallar"] or out["kullanici_ogeleri"]
                           or out["kullanici_ses_duzenlemesi"])
    return out


def oz_denetim(kok, klasor, proje, kp=None):
    """Yeni ya da klonlanmış taslakta: fark 0 · boşluk 0 · eksik medya 0 · süre = KURGU_PLANI ±1 kare. {sonuc, nedenler, fark}."""
    o = ct.oku(klasor)
    if o["sifreli"] or not o["icerik"]: return {"sonuc": "HATA", "nedenler": ["taslak okunamadı"], "fark": None}
    p = dict(proje, klasor=klasor); f = fark(kok, p, o); ned = []
    if f["fark_var"]: ned.append("fark var: " + ", ".join(k for k in ("klipler", "eklenen_klipler", "kayan_kanallar", "kullanici_ogeleri",
                                                                   "kullanici_ses_duzenlemesi") if f[k]))
    if f["bosluklar"]: ned.append(f"boşluk {len(f['bosluklar'])}")
    if f["eksik_medya"]: ned.append(f"eksik medya {len(f['eksik_medya'])}")
    if kp is None: _, kp = ko.kurgu_plani(kok)
    if kp:
        top = ko.toplam_sure(kp); ds = [s for s in ct.segmentler(o["icerik"]) if s["kanal"] == "Klipler"]
        son = max([s["bas"] + s["sure"] for s in ds] or [0.0])
        if abs(son - top) > TOL: ned.append(f"süre {son:.3f} ≠ plan {top:.3f}")
    return {"sonuc": "GEC" if not ned else "HATA", "nedenler": ned, "fark": f}


def plana_isle(kok, f):
    """Kullanıcı kararlarını KURGU_PLANI'na kilitli işler (yeni sürüm, çizelge T3). Kullanıcının kararı geri alınmaz."""
    import plan_kurgu
    _, kp = ko.kurgu_plani(kok)
    if not kp: return None
    kp = dict(kp); kp["planlar"] = [dict(x, goruntu=dict(x["goruntu"])) for x in kp["planlar"]]
    dz = {x["plan"]: x for x in kp["planlar"]}; kil = list(kp.get("kullanici_kilitleri") or []); kesilen = set(kp.get("kesilen") or [])
    for k in f["klipler"]:
        x = dz.get(k.get("plan"))
        if not x: continue
        if k["degisim"] == "kirpildi":
            x["goruntu"]["kullanim"] = {"bas": ko.kare(k["yeni"]["bas"]), "sure": ko.kare(k["yeni"]["sure"])}
            x["goruntu"].update(kullanim_kaynak="kullanici", kullanim_kilit="kullanici", guven=1.0, gerekce="kullanıcının CapCut kırpması")
            kil.append({"plan": x["plan"], "alan": "kullanim", "kaynak": "kullanici"})
        elif k["degisim"] == "silindi":
            kesilen.add(x["plan"]); kil.append({"plan": x["plan"], "alan": "kes", "kaynak": "kullanici"})
    o = ct.oku(f["klasor"]); ds = {s["segment_id"]: s for s in ct.segmentler(o["icerik"])} if o.get("icerik") else {}
    proje = proje_oku(kok) or {}; sid = {s.get("plan"): s["segment_id"] for s in proje.get("segmentler") or [] if s["kanal"] == "Klipler"}
    if any(k["degisim"] == "tasindi" for k in f["klipler"]):
        kp["planlar"].sort(key=lambda x: (ds.get(sid.get(x["plan"])) or {}).get("bas", 1e9))
        kil.append({"alan": "sira", "kaynak": "kullanici", "sira": [x["plan"] for x in kp["planlar"]]})
    kp["planlar"] = [x for x in kp["planlar"] if x["plan"] not in kesilen]
    plan_kurgu.cizelgele(kp["planlar"], kp.get("karartmalar"))
    plan_kurgu.diyalog_yerlestir(kok, kp, ko.sahne_planlari(kok), ko.diyalog_oku(kok))
    kp.update(kullanici_kilitleri=kil, kesilen=sorted(kesilen), onceki_surum=kp.get("kurgu_surumu"), kurgu_surumu=ko.sonraki_surum(kok),
              _uretim=ko.po.zarf("A16n", SURUM))
    kp["olcumler"] = plan_kurgu.olcumler(kp, ko.sahne_planlari(kok))
    return ko.kurgu_plani_yaz(kok, kp, "T3")


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    proje = proje_oku(kok, ko.bayrak(argv, "--yayin"))
    if not isinstance(proje, dict) or proje.get("_surum", 1) < 2:
        print("!! KURGU/son_capcut_projesi.json v2 yok (capcut_film.py v2 kurmalı)", flush=True); return 2
    klasor = ko.secenek(argv, "--klasor") or proje.get("klasor")
    o = ct.oku(klasor)
    if o["sifreli"]:
        ortak.atomik_yaz(os.path.join(kok, "KURGU", "TASLAK_FARK.json"), {"taslak": proje.get("proje"), "okuma": "salt_okunur", "sifreli": True,
                                                                         "bilgi": SIFRELI_BILGI, "_uretim": ko.po.zarf("A16n", SURUM)})
        print(SIFRELI_BILGI, flush=True); return 2
    if not o["icerik"]: print(f"!! taslak okunamadı: {klasor} ({o.get('hata')})", flush=True); return 2
    if ko.bayrak(argv, "--oz-denetim"):
        r = oz_denetim(kok, klasor, proje)
        print(f"öz denetim: {r['sonuc']}" + ("" if r["sonuc"] == "GEC" else " · " + "; ".join(r["nedenler"])), flush=True)
        return 0 if r["sonuc"] == "GEC" else 1
    kopya = kopya_al(kok, o)
    f = fark(kok, dict(proje, klasor=klasor), o); f["inceleme_kopyasi"] = ko.goreli(kok, kopya); f["_uretim"] = ko.po.zarf("A16n", SURUM)
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "TASLAK_FARK.json"), f)
    if ko.bayrak(argv, "--plana-isle") and f["fark_var"]:
        y = plana_isle(kok, f); print(f"kullanıcı kararları kilitli işlendi: {ko.goreli(kok, y)}", flush=True)
    sayi = {k: len(f[k]) for k in ("klipler", "eklenen_klipler", "bosluklar", "kayan_kanallar", "kullanici_ogeleri", "kullanici_ses_duzenlemesi")}
    print("taslak farkı: " + ("yok" if not f["fark_var"] else ", ".join(f"{k} {v}" for k, v in sayi.items() if v)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
