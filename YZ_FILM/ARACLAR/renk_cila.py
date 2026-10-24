"""RENK CİLA — ortak film görünümü: sabit LUT + ince gren + hafif halation ve sahne içi renk eşleme (TASARIM D-29, §6.5 `renk_cila.py`).

Kullanım:
  python renk_cila.py --film <film> [--plan 121,122] [--kuru]
    → KURGU/surumler/v<N>/cila/NNN.mp4 (klip bütün olarak işlenir; kullanim aralıkları geçerli kalır) + cila/RENK_RAPORU.json
  --kuru: yalnız ölçer (Lab ortalamaları, ΔE), dosya yazmaz.
Ayar (yalnız evren.py yazar): <evren>/<SERI>/dunya.json → "renk_cila": {"lut": "lut/film.cube" | null, "gren": 4, "halation": 0.08};
yoksa varsayılan (LUT yok, gren 4, halation 0,08). LUT dosyası .cube (ffmpeg lut3d).
Sahne içi eşleme: kullanılan pencereden 3 kare (baş + 0,15, orta, son − 0,15) → CIE Lab ortalaması; sahne grubunun medyanı referanstır;
ΔE76 > 5 (tahmin; kalibrasyonla) olan planın kanal kazançları doğrusal RGB oranıyla (0,8–1,25) düzeltilir; işlemden sonra yeniden ölçülür.
Video kredisi harcamaz; özgün klip değişmez (SIRALI_VIDEO'ya yazılmaz). capcut_film klip kaynağında buyuk/ > cila/ > 1080p türevi sırasını izler.
Çıkış kodları: 0 tamam · 1 ffmpeg hatası · 2 KURGU_PLANI yok · 4 ffmpeg yok.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "renk_cila 1.0"
DE_MAX = 5.0
VARSAYILAN = {"lut": None, "gren": 4, "halation": 0.08}


def _dogrusal(c): c = c / 255.0; return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def lab(rgb):
    l = _dogrusal(np.asarray(rgb, np.float64).reshape(-1, 3))
    M = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722], [0.0193, 0.1192, 0.9505]])
    xyz = l @ M.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    L = 116 * f[:, 1] - 16; a = 500 * (f[:, 0] - f[:, 1]); b = 200 * (f[:, 1] - f[:, 2])
    return np.array([L.mean(), a.mean(), b.mean()]), l.mean(axis=0)


def olc(klip, bas, sure):
    kareler = [ko.kare_rgb(klip, t, 160, 90) for t in (bas + 0.15, bas + sure / 2, bas + sure - 0.15)]
    kareler = [k for k in kareler if k is not None]
    if not kareler: return None, None
    return lab(np.concatenate([k.reshape(-1, 3) for k in kareler]))


def ayar(kok):
    s = ko.sahneler(kok); seri = None
    for d in list((s.get("karakterler") or {}).values()) + list((s.get("mekanlar") or {}).values()):
        e = (d or {}).get("evren") or ""
        if e.startswith("EVREN/"): seri = e.split("/")[1]; break
    adaylar = []
    if seri:
        try: adaylar.append(os.path.join(ortak.yollar()["evren_kok"], seri))
        except ortak.YolYok: pass
        adaylar.append(os.path.join(kok, "EVREN", seri))
    for k in adaylar:
        d = ortak.json_oku(os.path.join(k, "dunya.json"))
        if isinstance(d, dict) and isinstance(d.get("renk_cila"), dict):
            a = dict(VARSAYILAN, **d["renk_cila"])
            if a.get("lut") and not os.path.isabs(a["lut"]): a["lut"] = os.path.join(k, a["lut"])
            return a, os.path.join(k, "dunya.json")
    return dict(VARSAYILAN), None


def filtre(kazanclar, a):
    f = []
    if kazanclar is not None:
        r, g, b = [float(min(max(x, 0.8), 1.25)) for x in kazanclar]
        f.append(f"colorchannelmixer=rr={r:.4f}:gg={g:.4f}:bb={b:.4f}")
    if a.get("lut") and os.path.exists(a["lut"]): f.append(f"lut3d=file='{a['lut'].replace(os.sep, '/')}'")
    zincir = ",".join(f) or "null"
    h = float(a.get("halation") or 0)
    if h > 0:
        zincir = (f"[0:v]{zincir},split[o][h];[h]curves=all='0/0 0.75/0 1/1',gblur=sigma=12,colorchannelmixer=rr=1:gg=0.45:bb=0.3[h2];"
                  f"[o][h2]blend=all_mode=screen:all_opacity={h:.3f}")
    else: zincir = f"[0:v]{zincir}"
    g = int(a.get("gren") or 0)
    if g > 0: zincir += f",noise=alls={g}:allf=t"
    return zincir + ",format=yuv420p[v]"


def cila(kok, argv=()):
    argv = list(argv); kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: return 2, None
    if not ko.ffmpeg_var(): print("!! ffmpeg yok", flush=True); return 4, None
    sec = ko.secenek(argv, "--plan"); nolar = {int(x) for x in sec.split(",")} if sec else None
    a, kaynak = ayar(kok); n = int(kp.get("kurgu_surumu") or 1); hedef = os.path.join(kok, "KURGU", "surumler", f"v{n}", "cila")
    olcu = {}
    for x in kp.get("planlar") or []:
        if x["goruntu"].get("tur") != "video" or (nolar and x["plan"] not in nolar): continue
        k = ko.mutlak(kok, x["goruntu"]["dosya"]); u = x["goruntu"]["kullanim"]
        L, lin = olc(k, u["bas"], u["sure"])
        if L is not None: olcu[x["plan"]] = {"sg": x.get("sahne_grubu"), "lab": L, "lin": lin, "klip": k, "u": u}
    rap = {"_uretim": ko.po.zarf("A16", SURUM), "ayar": {k: v for k, v in a.items()}, "ayar_kaynagi": kaynak, "de_max": DE_MAX, "planlar": {}}
    gruplar = {}
    for no, v in olcu.items(): gruplar.setdefault(v["sg"], []).append(no)
    for sg, nos in gruplar.items():
        ref_lab = np.median([olcu[i]["lab"] for i in nos], axis=0); ref_lin = np.median([olcu[i]["lin"] for i in nos], axis=0)
        for no in nos:
            v = olcu[no]; de = float(np.linalg.norm(v["lab"] - ref_lab))
            kaz = (ref_lin / np.maximum(v["lin"], 1e-4)) ** (1 / 2.2) if de > DE_MAX else None
            kayit = {"sahne_grubu": sg, "lab": [round(float(x), 2) for x in v["lab"]], "dE_once": round(de, 2),
                     "kazanc": None if kaz is None else [round(float(x), 4) for x in kaz]}
            if not ko.bayrak(argv, "--kuru"):
                out = os.path.join(hedef, f"{int(no):03d}.mp4"); os.makedirs(hedef, exist_ok=True)
                try:
                    ko.ffmpeg("-i", v["klip"], "-filter_complex", filtre(kaz, a), "-map", "[v]", "-map", "0:a?", "-c:v", "libx264",
                              "-preset", "fast", "-crf", "17", "-c:a", "copy", out)
                except RuntimeError as e: print(f"!! #{no}: {e}", flush=True); return 1, None
                L2, _ = olc(out, v["u"]["bas"], v["u"]["sure"])
                kayit.update(dosya=ko.goreli(kok, out)); kayit["_lab2"] = L2
            rap["planlar"][str(no)] = kayit
        sonra = [rap["planlar"][str(i)].get("_lab2") for i in nos if rap["planlar"][str(i)].get("_lab2") is not None]
        ref2 = np.median(sonra, axis=0) if sonra else None
        for i in nos:                                       # işlenmiş grubun kendi medyanına uzaklık (sahne içi eşleme sonucu)
            k = rap["planlar"][str(i)]; L2 = k.pop("_lab2", None)
            if L2 is not None: k["dE_sonra"] = round(float(np.linalg.norm(L2 - ref2)), 2)
    if not ko.bayrak(argv, "--kuru"): ortak.atomik_yaz(os.path.join(hedef, "RENK_RAPORU.json"), rap)
    print(f"renk cila: {len(rap['planlar'])} plan · eşlenen {sum(1 for v in rap['planlar'].values() if v['kazanc'])}", flush=True)
    return 0, rap


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    k, _ = cila(kok, argv)
    if k == 2: print("!! KURGU_PLANI yok", flush=True)
    return k


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
