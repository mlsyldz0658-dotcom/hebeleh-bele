"""SON MİKS — tek miks kodu (TASARIM §6.6 "son_miks.py (tek miks kodu)", §7.2 S7/S8; [SM2] §4.6.2, §4.7.8, İ-1, B15).
Stemler toplanır → TEK doğrusal kazanç (bütünleşik −14 LUFS) → 4× aşırı örneklemeli gerçek tepe sınırlayıcı (hedef −1,5 dBTP; tavan −1)
→ yeniden ölçüm. Sınırlayıcı dışında dinamik işlem yoktur (S7.8). Animatik, önizleme, final ve Shorts AYNI işlevi kullanır (B15):
kurgu_render sesi kendisi karıştırmaz, `son_miks.onizle(...)` çağırır.

Kullanım (film.py görevi: "python son_miks.py <kip> --film <film>"):
  python son_miks.py --animatik --film F     KURGU/SES_CIZELGESI_T1.json stemleri → ANIMATIK/ses_animatik_v<tur>.wav, _RAPOR/S7_ANIMATIK.json
  python son_miks.py [--onizleme] --film F   KURGU/SES_CIZELGESI.json (T2) → KURGU/ses_onizleme_v<tur>.wav, _RAPOR/S7_ONIZLEME.json
  python son_miks.py --kesit --film F        KURGU/SES_CIZELGESI_KESIT.json (yoksa T2) → KESIT/ses_kesit_v<tur>.wav, _RAPOR/S7_KESIT.json
  python son_miks.py --final --film F [--mux <video.mp4> --cikti <çıktı.mp4>]
                                             → YAYIN/ses_master.wav, _RAPOR/S7_FINAL.json; --mux: görüntü kopyalanır, ses AAC 320k; çıkış
                                               dosyası yeniden ölçülür (S8.1) → _RAPOR/S8_FINAL.json
  python son_miks.py --olc <dosya> --film F  dışa aktarılmış dosyada yalnız ölçüm (S8.1: −14 ±1 LUFS, ≤ −1 dBTP) → _RAPOR/S8_FINAL.json
  python son_miks.py --shorts <wav|mp4> --film F [--cikti <wav>]   Shorts sesi (S7.9) → _RAPOR/S7_SHORTS.json
  python son_miks.py --yapisal --film F      B15: aynı stem imzalı raporlar arasında LUFS farkı > 0,1 LU → HATA (_RAPOR/S7_YAPISAL.json)
Kodda: miksle(stemler, hedef_lufs, tepe) → (dizi, ölçüm) · onizle(film, cizelge, cikti, kip) · sinirla(x) · denetle(x, ...) · imza(stemler)
Çıkış kodları: 0 rapor yazıldı (kapı sonucu raporda) · 1 girdi yok/bozuk · 4 kullanım ya da ffmpeg yok (mux).
"""
import os, sys, json, glob, shutil, subprocess
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak
import ses_ortak as so
from olcum import ses as O

SURUM = "son_miks 1.0"
SR = so.SR
KIP = {"--animatik": ("ANIMATIK", "KURGU/SES_CIZELGESI_T1.json", "ANIMATIK/ses_animatik_v{tur}.wav", "T1"),
       "--onizleme": ("ONIZLEME", "KURGU/SES_CIZELGESI.json", "KURGU/ses_onizleme_v{tur}.wav", "T2"),
       "--kesit": ("KESIT", "KURGU/SES_CIZELGESI_KESIT.json", "KESIT/ses_kesit_v{tur}.wav", "T2"),
       "--final": ("FINAL", "KURGU/SES_CIZELGESI.json", "YAYIN/ses_master.wav", "final")}


# --- çekirdek ------------------------------------------------------------------------------------------------------
def _yukle(s):
    if isinstance(s, str): x, _ = O.oku(s); return O.stereo(x)
    return O.stereo(np.asarray(s, dtype=np.float32))


def topla(stemler):
    """stemler: [(yol|dizi, kazanc_db)] ya da {ad: yol|dizi}. Uzunluklar en uzuna sıfırla tamamlanır."""
    if isinstance(stemler, dict): stemler = [(v, 0.0) for v in stemler.values() if v is not None]
    dz = [(_yukle(s), g) for s, g in stemler]
    if not dz: return np.zeros((0, 2), np.float32)
    n = max(len(d) for d, _ in dz); x = np.zeros((n, 2), np.float64)
    for d, g in dz: x[:len(d)] += d * O.kazanc(g)
    return x


def _kayan_min(a, w):
    """w (2'nin kuvveti) genişlikli merkezli kayan minimum (ikiye katlama; O(n log w))."""
    m = a.copy(); k = 1
    while k < w:
        m2 = m.copy(); m2[:-k] = np.minimum(m[:-k], m[k:]); m = m2; k *= 2
    s = w // 2
    return np.concatenate([np.full(s, m[0]), m[:-s]]) if s and len(m) > s else m


def _kayan_ort(a, w):
    k = np.concatenate([[0.0], np.cumsum(a)]); n = len(a); s = w // 2
    i0 = np.clip(np.arange(n) - s, 0, n); i1 = np.clip(np.arange(n) + s + 1, 0, n)
    return (k[i1] - k[i0]) / np.maximum(1, i1 - i0)


def tepe_dizisi(x, alt=None, pay=64):
    """Örnek başına 4× aşırı örneklenmiş mutlak tepe (kanalların en büyüğü). Örnek tepesi `alt`'ın altındaki bölgeler aşırı
    örneklenmez (araörnek tepesi pratikte örnek tepesini ≈ 3 dB'den çok aşmaz; alt = tavan − 6 dB)."""
    ch = [x[:, i] for i in range(x.shape[1])] if x.ndim == 2 else [x]
    p = np.max(np.abs(np.stack(ch, 1)), axis=1) if len(ch) > 1 else np.abs(ch[0]).astype(np.float64)
    m = np.ones(len(p), bool) if alt is None else p > alt
    if not m.any(): return p
    idx = np.flatnonzero(m); kes = np.flatnonzero(np.diff(idx) > 2 * pay)
    for a, b in zip(np.concatenate([[idx[0]], idx[kes + 1]]), np.concatenate([idx[kes], [idx[-1]]])):
        s0, s1 = max(0, a - pay), min(len(p), b + pay + 1)
        for c in ch:
            u = np.abs(O.asiri_ornekle(c[s0:s1]))
            if len(u) >= (s1 - s0) * 4: p[s0:s1] = np.maximum(p[s0:s1], u[:(s1 - s0) * 4].reshape(-1, 4).max(axis=1))
    return p


def sinirla(x, tavan_dbtp=-1.5, sr=SR, ms=5.0):
    """Gerçek tepe sınırlayıcı: kazanç = min(1, tavan/tepe), kayan min (ileri bakış) + kayan ortalama (≤ gereken kazanç). (y, aktif_oran)."""
    T = O.kazanc(tavan_dbtp); y = np.array(x, dtype=np.float64); toplam = np.ones(len(y))
    w = 1 << int(np.ceil(np.log2(max(2, ms * sr / 1000.0))))
    for _ in range(4):
        p = tepe_dizisi(y, alt=T * 0.5)
        if not len(p) or p.max() <= T: break
        g = np.minimum(1.0, T / np.maximum(p, 1e-12))
        g = _kayan_ort(_kayan_min(g, w), w)
        y *= g[:, None] if y.ndim == 2 else g; toplam *= g
    return y, float(np.mean(toplam < 0.999)) if len(toplam) else 0.0, toplam


def miksle(stemler, hedef_lufs=None, tepe=None):
    """Tek miks: toplam → tek doğrusal kazanç → sınırlayıcı → ölçüm. (dizi, ölçüm sözlüğü)."""
    hedef = so.esik("final_lufs") if hedef_lufs is None else hedef_lufs
    tepe = so.esik("miks_tepe_hedef_dbtp") if tepe is None else tepe
    x = topla(stemler)
    l0 = O.lufs(x, SR) if len(x) else -70.0
    if l0 <= -69.9: return x.astype(np.float32), {"lufs_once": l0, "kazanc_db": 0.0, "lufs": l0, "gercek_tepe_dbtp": -120.0,
                                                  "sinirlayici_oran": 0.0, "dogrusal": True, "bos": True}
    g = hedef - l0
    for _ in range(3):                                   # sınırlayıcı yüksekliği düşürdüyse kazanç (yine TEK sayı) yeniden seçilir
        y, oran, gz = sinirla(x * O.kazanc(g), tepe)
        l1 = O.lufs(y, SR)
        if abs(l1 - hedef) <= 0.2: break
        g += hedef - l1
    olc = {"lufs_once": round(l0, 2), "kazanc_db": round(g, 2), "lufs": round(l1, 2), "gercek_tepe_dbtp": round(O.gercek_tepe(y, SR), 2),
           "sinirlayici_oran": round(oran, 5), "dogrusal": dogrusal_mi(x, y, g, gz)}
    return y.astype(np.float32), olc


def dogrusal_mi(x, y, g, gz):
    """S7.8: sınırlayıcının dokunmadığı örneklerde çıkış/giriş oranı tek kazanç mı?"""
    k = O.kazanc(g); m = (gz >= 0.999)
    xa, ya = (x[m] if x.ndim == 1 else x[m].ravel()), (y[m] if y.ndim == 1 else y[m].ravel())
    s = np.abs(xa) > 1e-3
    if not s.any(): return True
    return bool(np.max(np.abs(ya[s] / xa[s] - k)) < 1e-3 * k + 1e-6)


def imza(stemler):
    if isinstance(stemler, dict): stemler = [(v, 0.0) for v in stemler.values() if v is not None]
    parca = []
    for s, g in stemler:
        parca.append((so.sha1(s) if isinstance(s, str) and os.path.exists(s) else so.ozet(np.asarray(s).tobytes()[:1 << 20]), round(g, 3)))
    return so.ozet(*sorted(parca))


# --- denetim -------------------------------------------------------------------------------------------------------
def _cakisir(a, b, pay=0.05): return a[0] < b[1] - pay and b[0] < a[1] - pay


def denetle(y, olc, cizelge="T1", planli=(), sure_beklenen=None):
    """S7 ölçümleri. cizelge: T1 | T2 | final | shorts."""
    hedef, tol, tp_max = so.esik("final_lufs"), so.esik("final_lufs_tolerans"), so.esik("true_peak_max_dbtp")
    mad = "S7.9" if cizelge == "shorts" else "S7.1"
    o = [so.m(mad, "GEC" if abs(olc["lufs"] - hedef) <= tol else "HATA", olcu=olc["lufs"], esik=f"{hedef} ±{tol} LUFS"),
         so.m("S7.2" if cizelge != "shorts" else "S7.9_tepe", "GEC" if olc["gercek_tepe_dbtp"] <= tp_max else "HATA",
              olcu=olc["gercek_tepe_dbtp"], esik=f"≤ {tp_max} dBTP"),
         so.m("S7.8", "GEC" if olc.get("dogrusal", True) else "HATA", olcu={"kazanc_db": olc.get("kazanc_db"),
              "sinirlayici_oran": olc.get("sinirlayici_oran")}, esik="tek doğrusal kazanç + tepe sınırlayıcı"),
         so.m("S7.7", "GEC" if O.kirpilma(y) == 0 else "HATA", olcu=O.kirpilma(y), esik=0)]
    if cizelge in ("T1", "T2", "final"):
        ses = O.sessizlikler(y, SR, so.esik("mutlak_sessizlik_db"), so.esik("miks_sessizlik_sn"))
        plansiz = [s for s in ses if not any(_cakisir(s, (p.get("cizelge_bas", 0), p.get("cizelge_bas", 0) + p.get("sure", 0)))
                                             for p in planli if p.get("tip") in ("mutlak", "mutlak_sessizlik"))]
        o.append(so.m("S7.4", "GEC" if not plansiz else "HATA", olcu=plansiz[:10],
                      esik=f"planlanmamış sessizlik ({so.esik('mutlak_sessizlik_db')} dB, ≥ {so.esik('miks_sessizlik_sn')} sn) 0",
                      oneri="ses_katmani yatağı ya da kurgu boşluğu" if plansiz else None))
    if cizelge in ("T2", "final"):
        L = O.lra(y, SR)
        o.append(so.m("S7.3", "GEC" if L <= so.esik("miks_lra_max") else "BAYRAK", olcu=round(L, 2), esik=f"≤ {so.esik('miks_lra_max')} LU"))
        mf, fk = O.mono_fark_lu(y, SR), O.faz_korelasyonu(y)
        o.append(so.m("S7.5", "GEC" if (mf <= so.esik("miks_mono_fark_max_lu") and fk >= 0) else "BAYRAK",
                      olcu={"mono_fark_lu": mf, "faz": fk}, esik="≤ 3 LU; ≥ 0"))
    if sure_beklenen is not None:
        fark = abs(len(y) / SR - sure_beklenen)
        o.append(so.m("SURE", "GEC" if fark <= 1 / 24 else "HATA", olcu=round(len(y) / SR, 3), esik=f"çizelge {sure_beklenen} ±1 kare"))
    return o


# --- dosya kipleri ---------------------------------------------------------------------------------------------------
def cizelge_oku(film, rel):
    c = ortak.json_oku(os.path.join(film, rel))
    if not isinstance(c, dict): return None
    return c


def stemler_coz(film, c):
    st = c.get("stemler") or {}
    out = []
    for ad in ("diyalog", "efekt", "ambiyans", "muzik"):
        p = st.get(ad)
        if not p: continue
        p = p if os.path.isabs(p) else os.path.join(film, p)
        if os.path.exists(p): out.append((p, float((c.get("stem_kazanc_db") or {}).get(ad, 0.0))))
    return out


def onizle(film, cizelge, cikti, kip="ONIZLEME", cizelge_turu=None, tur=None, asama=None, rapor_yaz=True):
    """Tek miks giriş noktası (kurgu_render çağırır). cizelge: yol (film köküne göre) ya da sözlük. (cikti, ölçüm, rapor_yolu)."""
    c = cizelge if isinstance(cizelge, dict) else cizelge_oku(film, cizelge)
    if not c: raise FileNotFoundError(f"ses çizelgesi yok: {cizelge}")
    st = stemler_coz(film, c)
    if not st: raise FileNotFoundError("çizelgede stem yok (ses_katmani --cizelge çalıştı mı?)")
    y, olc = miksle(st)
    O.yaz(cikti, y)
    olc["stem_imza"] = imza(st); olc["cikti"] = os.path.relpath(cikti, film)
    tur_ = cizelge_turu or c.get("cizelge") or "T1"
    tc = "final" if kip == "FINAL" else ("T1" if tur_ == "T1" else "T2")
    o = denetle(y, olc, tc, c.get("sessizlik") or [], c.get("toplam_sn"))
    yol = None
    if rapor_yaz:
        yol, _ = so.rapor(film, "S7", kip, o, asama=asama, arac=SURUM, ek={"olcum": olc, "stem_imza": olc["stem_imza"]},
                          tur=tur, gorev_raporu=False)
    return cikti, olc, yol


def olc_dosya(film, dosya, kapsam="FINAL", asama=None):
    """S8.1: dışa aktarılmış ya da mux edilmiş dosyada S7.1–S7.2 yeniden."""
    x, _ = O.oku(dosya); x = O.stereo(x)
    L, tp = O.lufs(x, SR), O.gercek_tepe(x, SR)
    hedef, tol, tp_max = so.esik("final_lufs"), so.esik("final_lufs_tolerans"), so.esik("true_peak_max_dbtp")
    o = [so.m("S8.1", "GEC" if (abs(L - hedef) <= tol and tp <= tp_max) else "HATA", olcu={"lufs": round(L, 2), "gercek_tepe": round(tp, 2)},
              esik=f"{hedef} ±{tol} LUFS; ≤ {tp_max} dBTP", kanit=os.path.relpath(dosya, film) if dosya.startswith(film) else dosya)]
    return so.rapor(film, "S8", kapsam, o, asama=asama, arac=SURUM, gorev_raporu=False)


def mux(video, ses, cikti):
    if not shutil.which("ffmpeg"): raise RuntimeError("ffmpeg yok")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", ses, "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "320k", "-ar", str(SR), "-shortest", cikti + ".tmp.mp4"], check=True)
    os.replace(cikti + ".tmp.mp4", cikti)
    return cikti


def shorts(film, giris, cikti=None):
    x, _ = O.oku(giris)
    y, olc = miksle([(O.stereo(x), 0.0)])
    cikti = cikti or os.path.join(film, "YAYIN", "SHORTS", os.path.splitext(os.path.basename(giris))[0] + "_ses.wav")
    O.yaz(cikti, y)
    return cikti, so.rapor(film, "S7", "SHORTS", denetle(y, olc, "shorts"), arac=SURUM, ek={"olcum": olc}, gorev_raporu=False)


def yapisal(film):
    """B15: aynı stem imzasından üretilmiş miksler aynı LUFS'u vermeli (tek miks kodu)."""
    gruplar = {}
    for p in glob.glob(os.path.join(film, "_RAPOR", "S7_*.json")):
        r = ortak.json_oku(p, {}) or {}
        if r.get("stem_imza") and isinstance(r.get("olcum"), dict):
            gruplar.setdefault(r["stem_imza"], []).append((os.path.basename(p), r["olcum"].get("lufs")))
    o = []
    for im, ls in gruplar.items():
        v = [l for _, l in ls if isinstance(l, (int, float))]
        if len(v) < 2: continue
        fark = max(v) - min(v)
        o.append(so.m("B15", "GEC" if fark <= so.esik("miks_ayni_stem_lufs_fark_max") else "HATA", birim=im,
                      olcu={"raporlar": ls, "fark_lu": round(fark, 3)}, esik="aynı stemler → aynı LUFS (≤ 0,1 LU)"))
    if not o: o.append(so.m("B15", "GEC", olcu="karşılaştırılacak aynı imzalı miks yok"))
    return so.rapor(film, "S7", "YAPISAL", o, arac=SURUM, gorev_raporu=False)


def main(argv):
    try: film = so.film_coz(so.arg(argv, "--film"))
    except (ValueError, ortak.YolYok) as e: print(f"!! {e}"); return 4
    g = so.gorev(); tur = g["tur_no"]
    try:
        if "--yapisal" in argv:
            yol, r = yapisal(film); print(f"B15 → {r['sonuc']} ({os.path.relpath(yol, film)})"); return 0
        if "--olc" in argv:
            yol, r = olc_dosya(film, so.arg(argv, "--olc")); print(f"S8 → {r['sonuc']}"); return 0
        if "--shorts" in argv:
            c, (yol, r) = shorts(film, so.arg(argv, "--shorts"), so.arg(argv, "--cikti")); print(f"S7 Shorts → {r['sonuc']}: {c}"); return 0
        kip = next((k for k in KIP if k in argv), "--onizleme")
        kapsam, rel, cik, tur_ = KIP[kip]
        if kip == "--kesit" and not os.path.exists(os.path.join(film, rel)): rel = "KURGU/SES_CIZELGESI.json"
        if not os.path.exists(os.path.join(film, rel)):
            print(f"!! {rel} yok: önce ses_katmani --cizelge {tur_ if tur_ != 'final' else 'T2'}"); return 1
        cikti = os.path.join(film, cik.format(tur=tur))
        _, olc, yol = onizle(film, rel, cikti, kapsam, asama=g["asama"], tur=tur)
        r = ortak.json_oku(yol, {})
        print(f"S7 {kapsam} → {r.get('sonuc')} · {olc['lufs']} LUFS · {olc['gercek_tepe_dbtp']} dBTP · {os.path.relpath(cikti, film)}")
        if kip == "--final" and "--mux" in argv:
            v = mux(so.arg(argv, "--mux"), cikti, so.arg(argv, "--cikti") or os.path.join(film, "YAYIN", "_mux.mp4"))
            _, r8 = olc_dosya(film, v); print(f"S8 → {r8['sonuc']} ({v})")
        return 0
    except FileNotFoundError as e: print(f"!! {e}"); return 1
    except RuntimeError as e: print(f"!! {e}"); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
