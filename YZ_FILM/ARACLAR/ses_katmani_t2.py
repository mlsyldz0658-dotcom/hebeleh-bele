"""SES KATMANI T2 — kaba kurgu çizelgesinde ambiyans ve efekt katmanları (TASARIM §6.6 `ses_katmani.py --cizelge T2`; [SM2] SE3, §4.7.6 S5).

Kullanım (ses_katmani.py "--cizelge T2" bu modüle yönlendirir; tek başına da çalışır):
  python ses_katmani_t2.py --film <film> [--saglayici sahte]   → KURGU/SES_CIZELGESI.json (ambiyans, efektler; muzik[]'e dokunmaz),
                                                                  KURGU/STEMS/{ambiyans,efekt}.wav, _RAPOR/S5_v<N>.json
  python ses_katmani_t2.py --film <film> --denetle             mevcut SES_CIZELGESI'ni güncel klip özetleriyle denetler (S5.7), yazmaz
İş:
  - Sahne grubu başına TEK yatak (sahne_gruplari.<S>.ses.yatak); döngü, çapraz geçiş (0,5–1,0 sn) ve yeni yatağın öne alınması (0,3–1,0 sn).
    Aynı mekân, aynı yatak ve zaman atlaması yoksa yatak kesintisiz sürer (devam). Seviye diyaloğun 12–18 dB altında.
  - Efekt olayı önce KLİBİN KENDİ sesindeki başlangıç anına oturur (Veo adım ve kapı seslerini görüntüyle senkron üretir; zaman referansı).
    Pencerede konuşma sızıntısı yoksa klibin kendi efekti kapılı olarak kullanılır, varsa kütüphane efekti (SES_KUTUPHANESI/DIZIN.json) o ana.
    Kesilen pencere dışındaki olay yerleşmez. Her parça 15 ms yumuşatılır (tık önleme).
  - Yeniden çekilen ya da yeniden kırpılan plan klip özetinden (SHA-1) tanınır; eski özetli efekt yeniden kurulur (S5.7).
Ölçüler: S5.1 sahne grubunda tek yatak (H) · S5.2 ambiyans boşluğu (100 ms'de < −60 dBFS; planlı mutlak sessizlik hariç) (H) ·
S5.3 ardışık planların ambiyans farkı ≤ 3 LU (H) · S5.4 ambiyans diyaloğun 12–18 dB altında (H) · S5.5 çapraz geçiş/öne alma (B) ·
S5.7 efekt klip özeti = güncel klip (H) · S5.8 kapılı klip efektinde söz sızıntısı 0 (H; varsa kütüphaneye düşer) · S5.11 devam sınırında
aynı kategoriden iki olay ±100 ms (B; biri atılır).
Çıkış kodları: 0 S5 GEÇ/BAYRAK · 1 S5 HATA · 2 KURGU_PLANI yok · 4 kullanım.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "ses_katmani_t2 1.0"
BOSLUK_DB, CAPRAZ_VARS, ONALMA_VARS = -60.0, 0.8, 0.5


def _yatak_yolu(kok, rel):
    if not rel: return None
    p = ko.mutlak(kok, rel)
    if os.path.exists(p): return p
    try:
        q = os.path.join(ortak.yollar()["ses_kutuphanesi"], rel.split("SES_KUTUPHANESI/", 1)[-1])
        if os.path.exists(q): return q
    except ortak.YolYok: pass
    return None


def _dongu(a, sr, n, capraz=0.5):
    if len(a) == 0: return np.zeros(n, np.float32)
    if len(a) >= n: return a[:n].copy()
    c = min(int(capraz * sr), len(a) // 4); out = a.copy()
    while len(out) < n:
        r = np.linspace(0, 1, c, dtype=np.float32) if c else np.zeros(0, np.float32)
        if c: out[-c:] = out[-c:] * (1 - r) + a[:c] * r
        out = np.concatenate([out, a[c:]])
    return out[:n]


def _sahte_yatak(sr, sure_, tohum):
    rng = np.random.default_rng(tohum); w = rng.standard_normal(int(sr * sure_)).astype(np.float32)
    return np.convolve(w, np.ones(8) / 8, mode="same").astype(np.float32) * 0.05


def kosular(kp):
    """Ardışık aynı sahne grubu planları → [(sahne_grubu, [planlar])]."""
    out = []
    for x in kp.get("planlar") or []:
        if out and out[-1][0] == x.get("sahne_grubu"): out[-1][1].append(x)
        else: out.append((x.get("sahne_grubu"), [x]))
    return out


def dlg_ref(kp, dj, E):
    vs = [float(dj["replikler"][d["replik"]].get("olculen_lufs")) for d in kp.get("diyalog") or []
          if dj["replikler"].get(d["replik"], {}).get("olculen_lufs") is not None]
    return float(np.median(vs)) if vs else float((E.get("diyalog_lufs") or {}).get("normal", -19.5))


def ambiyans(kok, argv, kp, s, pl, dj, E, olc, sahte):
    gr = s.get("sahne_gruplari") or {}; top = ko.toplam_sure(kp); st = np.zeros(int((top + 2) * ko.SR), np.float32)
    lo, hi = E.get("ambiyans_diyalog_alti_db") or [12, 18]; ref = dlg_ref(kp, dj, E); kayit = []; onceki = None
    for i, (sg, xs) in enumerate(kosular(kp)):
        g = gr.get(sg) or {}; ses = g.get("ses") or {}; y = ses.get("yatak") or {}
        dosyalar = {y.get("dosya")} | {(ko.zanaat(pl.get(x["plan"], {})).get("ses") or {}).get("yatak_dosya") for x in xs}
        dosyalar.discard(None)
        olc.append(ko.m("S5.1_tek_yatak", "GEC" if len(dosyalar) <= 1 else "HATA", None, sahne_grubu=sg, olcu=sorted(dosyalar),
                        kok_neden=None if len(dosyalar) <= 1 else "ambiyans_zipladi"))
        rel = y.get("dosya") or (sorted(dosyalar)[0] if dosyalar else None)
        bas, bit = xs[0]["cizelge_bas"], ko.plan_sonu(xs[-1])
        devam = bool(onceki and onceki["dosya"] == rel and onceki["mekan"] == g.get("mekan") and (g.get("zaman") or {}).get("atlama") == "yok")
        gecis = str(ses.get("gecis") or "")
        capraz = float(gecis.split("_")[-1]) if gecis.startswith("capraz_") else CAPRAZ_VARS
        onal = 0.0 if devam or i == 0 else ONALMA_VARS
        p = _yatak_yolu(kok, rel)
        if p: a, sr = ko.wav_oku(p); a = ko.yeniden_ornekle(a, sr, ko.SR)
        elif sahte and rel: a = _sahte_yatak(ko.SR, 10.0, len(rel))
        else:
            olc.append(ko.m("S5_yatak_dosyasi", "HATA", None, sahne_grubu=sg, olcu=rel, kok_neden="efekt_eksik", neden="yatak dosyası yok"))
            onceki = None; continue
        hedef = min(max(float(y.get("seviye_lufs") or ref - 15), ref - hi), ref - lo)
        t0 = bas - onal; n = int((bit - t0 + (capraz if not devam else 0)) * ko.SR)
        if devam and onceki: parca = _dongu(np.roll(a, -onceki["konum"]), ko.SR, n)
        else: parca = _dongu(a, ko.SR, n)
        L = ko.lufs(parca, ko.SR); parca = parca * ko.kazanc(hedef - L if L > ko.SESSIZ_DB else 0.0)
        c = int((0.0 if devam else capraz) * ko.SR)
        if c and i > 0:
            r = np.linspace(0, 1, c, dtype=np.float32); parca[:c] *= r
            j0 = int(max(0.0, t0) * ko.SR); st[j0:j0 + c] *= (1 - r[:len(st[j0:j0 + c])])
        ko.stem_ekle(st, ko.yumusat(parca, ko.SR) if not devam else parca, ko.SR, t0)
        kayit.append({"sahne_grubu": sg, "dosya": rel, "cizelge_bas": ko.kare(t0), "sure": ko.kare(n / ko.SR), "capraz_giris_sn": 0.0 if devam else capraz,
                      "one_alma_sn": onal, "devam": devam, "hedef_lufs": round(hedef, 2), "katmanlar": [k.get("kaynak") for k in y.get("katmanlar") or []]})
        if not devam and i > 0:
            ok = 0.5 <= capraz <= 1.0 and (0.3 <= onal <= 1.0)
            olc.append(ko.m("S5.5_gecis", "GEC" if ok else "BAYRAK", None, sahne_grubu=sg, olcu={"capraz": capraz, "one_alma": onal}))
        onceki = {"dosya": rel, "mekan": g.get("mekan"), "konum": (n % max(1, len(a)))}
    return st[: int(top * ko.SR)], kayit


def _onset(a, sr, t0, t1):
    z = ko.zarf(ko.pencere(a, sr, max(0.0, t0), t1), sr, 100)
    if len(z) < 3 or z.max() < 1e-4: return None
    taban = float(np.median(z[:3])); mad = max(float(np.median(np.abs(z - np.median(z)))), 1e-4)
    k = np.where(z > taban + 4 * mad)[0]
    return None if not len(k) else max(0.0, t0) + k[0] / 100.0


def _kutuphane(kategori):
    try: k = ortak.yollar()["ses_kutuphanesi"]
    except ortak.YolYok: return None
    dz = ortak.json_oku(os.path.join(k, "DIZIN.json"), {}) or {}
    for rel, v in sorted(dz.items()):
        if isinstance(v, dict) and not v.get("kara_liste") and kategori in (v.get("etiketler") or []) + [v.get("kategori")]:
            p = os.path.join(k, rel)
            if os.path.exists(p): return p
    return None


def efektler(kok, argv, kp, pl, dj, E, olc, sahte, eski):
    top = ko.toplam_sure(kp); st = np.zeros(int((top + 2) * ko.SR), np.float32); kayit = []; yeniden = 0
    eski_ozet = {(e.get("plan"), e.get("adim")): e.get("klip_ozet") for e in eski or []}
    ref = dlg_ref(kp, dj, E); lo, hi = E.get("efekt_diyalog_alti_db") or [3, 10]
    for x in kp.get("planlar") or []:
        p = pl.get(x["plan"], {}); efs = (ko.zanaat(p).get("ses") or {}).get("efektler") or []
        if not efs or x["goruntu"].get("tur") != "video": continue
        klip = ko.mutlak(kok, x["goruntu"]["dosya"]); oz = ko.sha1(klip)
        dig = os.path.join(kok, "SESLER", "ayrik", f"{int(x['plan']):03d}_diger.wav")
        a = ko.wav_oku(dig)[0] if os.path.exists(dig) else ko.video_sesi(klip)
        konus_p = os.path.join(kok, "SESLER", "ayrik", f"{int(x['plan']):03d}_konusma.wav")
        konus = ko.wav_oku(konus_p)[0] if os.path.exists(konus_p) else None
        olculen = {m["id"]: m for m in x["goruntu"].get("adimlar_olculen") or []}
        adimlar = {m["id"]: m for m in ko.zanaat(p).get("eylem_zinciri") or []}
        for ef in efs:
            ad = olculen.get(ef.get("adim")) or {}; pa = adimlar.get(ef.get("adim")) or {}
            b0 = ad.get("bas") if ad.get("bas") is not None else pa.get("bas"); b1 = ad.get("bit") if ad.get("bit") is not None else pa.get("bit")
            if b0 is None: continue
            if eski_ozet.get((x["plan"], ef.get("adim"))) not in (None, oz): yeniden += 1
            an = _onset(a, ko.SR, float(b0) - 0.1, float(b1 or b0) + 0.3) if a is not None else None
            zk = "klip_onset" if an is not None else "plan"
            an = float(b0) if an is None else an
            t = ko.cizelge_zamanina(x, an)
            if not (x["cizelge_bas"] - 1e-6 <= t < ko.plan_sonu(x)): continue           # kesilen pencerede olay yok
            kay, dosya, parca = None, None, None
            sizinti = konus is not None and float(np.sqrt(np.mean(ko.pencere(konus, ko.SR, an, an + 0.6) ** 2) or 0)) > 0.01
            if ef.get("kaynak_tercih", "klip") == "klip" and a is not None and not sizinti:
                parca = ko.pencere(a, ko.SR, max(0.0, an - 0.02), an + 0.6); kay = "klip"
                dosya = ko.wav_yaz(os.path.join(kok, "SESLER", "klip_efekt", f"{x['plan']}_{ef.get('adim')}.wav"), ko.yumusat(parca, ko.SR))
            if sizinti: olc.append(ko.m("S5.8_soz_sizintisi", "BAYRAK", x["plan"], adim=ef.get("adim"), karar="kütüphane efekti"))
            if parca is None or not len(parca):
                lp = _kutuphane(ef.get("kategori"))
                if lp: parca, _ = ko.wav_oku(lp); kay, dosya = "kutuphane", lp
                elif sahte:
                    tt = np.arange(int(0.08 * ko.SR)) / ko.SR; parca = (0.5 * np.sin(2 * np.pi * 900 * tt) * np.exp(-tt * 60)).astype(np.float32)
                    kay = "sahte"
                else:
                    olc.append(ko.m("efekt_kaynagi", "BAYRAK", x["plan"], adim=ef.get("adim"), kok_neden="efekt_eksik")); continue
            sdb = float(ef.get("seviye_db_diyaloga_gore", -(lo + hi) / 2))
            L = ko.kisa_max_lufs(parca, ko.SR); g = (ref + sdb) - L if L > ko.SESSIZ_DB else 0.0
            ko.stem_ekle(st, ko.yumusat(parca, ko.SR) * ko.kazanc(g), ko.SR, t)
            kayit.append({"id": f"E{x['plan']}{ef.get('adim')}", "plan": x["plan"], "adim": ef.get("adim"), "kategori": ef.get("kategori"),
                          "kaynak": kay, "dosya": ko.goreli(kok, dosya) if dosya else None, "cizelge_bas": ko.kare(t), "zaman_kaynagi": zk,
                          "klip_ozet": oz, "seviye_db": round(sdb, 1)})
    kayit.sort(key=lambda e: e["cizelge_bas"]); temiz = []
    for e in kayit:                                          # S5.11: aynı kategoriden iki olay ±100 ms
        if temiz and temiz[-1]["kategori"] == e["kategori"] and e["cizelge_bas"] - temiz[-1]["cizelge_bas"] <= 0.1 and temiz[-1]["plan"] != e["plan"]:
            olc.append(ko.m("S5.11_cift_olay", "BAYRAK", e["plan"], olcu=e["id"], karar="biri atıldı")); continue
        temiz.append(e)
    olc.append(ko.m("S5.7_klip_ozet", "GEC", None, olcu={"yeniden_kurulan": yeniden}))
    return st[: int(top * ko.SR)], temiz


def olcumler(kok, kp, amb, olc, sessizlik, E):
    sr = ko.SR; n = int(0.1 * sr); planli = [(float(x["cizelge_bas"]), float(x["cizelge_bas"]) + float(x["sure"]))
                                              for x in sessizlik or [] if x.get("tip") == "mutlak"]
    bos = []
    for i in range(0, len(amb) - n + 1, n):
        t = i / sr
        if any(a <= t < b for a, b in planli): continue
        if ko.db(np.sqrt(np.mean(amb[i:i + n] ** 2)) + 1e-12) < BOSLUK_DB: bos.append(round(t, 2))
    olc.append(ko.m("S5.2_ambiyans_boslugu", "GEC" if not bos else "HATA", None, olcu=len(bos), ornek=bos[:5], esik=0))
    onceki = None; mx = float(E.get("ambiyans_sahne_ici_fark_max_lu", 3))
    for x in kp.get("planlar") or []:
        a = ko.pencere(amb, sr, x["cizelge_bas"], ko.plan_sonu(x))
        L = ko.lufs(a, sr) if len(a) >= 0.4 * sr else None
        if L is not None and onceki and onceki[0] == x.get("sahne_grubu") and L > ko.SESSIZ_DB and onceki[1] > ko.SESSIZ_DB:
            f = abs(L - onceki[1])
            olc.append(ko.m("S5.3_ardisik_fark", "GEC" if f <= mx else "HATA", x["plan"], olcu=round(f, 2), esik=mx,
                            kok_neden=None if f <= mx else "ambiyans_zipladi"))
        if L is not None: onceki = (x.get("sahne_grubu"), L)
    dp = ko.stem_yolu(kok, "diyalog"); lo, hi = E.get("ambiyans_diyalog_alti_db") or [12, 18]
    if not os.path.exists(dp):
        olc.append(ko.m("S5.4_diyalog_alti", "OLCULEMEDI", None, neden="diyalog stemi yok (diyalog_esitle)")); return
    dl, _ = ko.wav_oku(dp)
    for d in kp.get("diyalog") or []:
        a, b = float(d["cizelge_bas"]), float(d["cizelge_bas"]) + float(d["sure"])
        if b - a < 0.4: continue
        Ld, La = ko.lufs(ko.pencere(dl, sr, a, b), sr), ko.lufs(ko.pencere(amb, sr, a, b), sr)
        if Ld <= ko.SESSIZ_DB or La <= ko.SESSIZ_DB: continue
        f = Ld - La
        olc.append(ko.m("S5.4_diyalog_alti", "GEC" if lo - 0.5 <= f <= hi + 0.5 else "HATA", d["plan"], replik=d["replik"], olcu=round(f, 2), esik=[lo, hi]))


def denetle_mevcut(kok, kp):
    sc = ko.ses_cizelgesi(kok); olc = []; dz = {x["plan"]: x for x in kp.get("planlar") or []}
    for e in sc.get("efektler") or []:
        x = dz.get(e.get("plan"))
        if not x: continue
        oz = ko.sha1(ko.mutlak(kok, x["goruntu"]["dosya"])) if x["goruntu"].get("dosya") else None
        bayat = e.get("klip_ozet") and oz and e["klip_ozet"] != oz
        olc.append(ko.m("S5.7_klip_ozet", "HATA" if bayat else "GEC", e["plan"], olcu=e.get("klip_ozet"), esik=oz,
                        kok_neden="efekt_eksik" if bayat else None, karar="bayat: ses_katmani yeniden kurar" if bayat else None))
    gr = {}
    for a in sc.get("ambiyans") or []: gr.setdefault(a.get("sahne_grubu"), set()).add(a.get("dosya"))
    for sg, ds in gr.items():
        olc.append(ko.m("S5.1_tek_yatak", "GEC" if len(ds) <= 1 else "HATA", None, sahne_grubu=sg, olcu=sorted(map(str, ds))))
    return olc


def kur(kok, argv=()):
    argv = list(argv); kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: return None, None
    if ko.bayrak(argv, "--denetle"):
        return ko.rapor(kok, "S5", ko.kapsam_surum(kp), denetle_mevcut(kok, kp), "A16", SURUM, birimler=[x["plan"] for x in kp["planlar"]])
    s = ko.sahneler(kok); pl = ko.sahne_planlari(kok, s); dj = ko.diyalog_oku(kok); E = ko.po.esik(); olc = []
    sahte = ko.saglayici_adi(argv) == "sahte"; sc = ko.ses_cizelgesi(kok)
    amb, akay = ambiyans(kok, argv, kp, s, pl, dj, E, olc, sahte)
    ef, ekay = efektler(kok, argv, kp, pl, dj, E, olc, sahte, sc.get("efektler"))
    ko.wav_yaz(ko.stem_yolu(kok, "ambiyans"), amb); ko.wav_yaz(ko.stem_yolu(kok, "efekt"), ef)
    olcumler(kok, kp, amb, olc, sc.get("sessizlik"), E)
    sc.update(ambiyans=akay, efektler=ekay); sc.setdefault("muzik", []); sc.setdefault("sessizlik", [])
    ko.ses_cizelgesi_yaz(kok, sc, kp_yol, kp)
    return ko.rapor(kok, "S5", ko.kapsam_surum(kp), olc, "A16", SURUM, birimler=[x["plan"] for x in kp["planlar"]],
                    ek={"kurgu_plani_imza": ko.plan_imza(kp)}, girdi_imza=ko.plan_imza(kp))


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    _, r = kur(kok, argv)
    if not r: print("!! KURGU_PLANI yok; önce plan_kurgu.py", flush=True); return 2
    return ko.po.cikis(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
