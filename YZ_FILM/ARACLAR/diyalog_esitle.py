"""DİYALOG EŞİTLE — replik başına yükseklik hedefi, oda yanıtı, uzaklık ve iki yol arası tını eşleme (TASARIM §6.6; [SM2] SE2, §4.7.5 S4).

Kullanım:
  python diyalog_esitle.py --film <film>              → SESLER/esit/<replik>.wav, KURGU/STEMS/diyalog.wav, _RAPOR/S4_v<N>.json
  python diyalog_esitle.py --film <film> --denetle    yalnız ölçer (dosya yazmaz): kaynak dosyalar hedefte mi (S4.1)
İş (tepe normalleştirme YOK; seslendir.py:104 kusurunun düzeltmesi):
  - Hedef: teslim → seviye sınıfı (veri/plan_sozlukleri.json teslim.lufs) → RE diyalog_lufs (fısıltı −24 · yumuşak −21,5 · normal −19,5 ·
    bağırma −17 LUFS); planın _derlenir.seviye sayısı varsa o. Ölçüm K-ağırlıklı; 0,4 sn'den kısa replikte en yüksek anlık (400 ms) değer (S4.3).
  - Mekânın oda yanıtı (sahne_gruplari.<S>.ses.oda_yaniti; boyuttan sentetik dönüm yanıtı, aynı oda = aynı yanıt; pyroomacoustics
    kuruluysa onunla) ve plan ölçeğine göre uzaklık (geniş plan daha yankılı) eklenir; sonra TEK doğrusal kazanç hedefe oturtur.
  - Aynı karakterin veo_donustur ↔ tts replikleri: 1/3 oktav (100 Hz–8 kHz) uzun dönem spektrum farkı > 3 dB ise TTS'e eşleme EQ'su (±6 dB).
Ölçüler: S4.1 hedef ±1 LU (H) · S4.2 aynı sahne + karakter + sınıf arası fark ≤ 1 LU (H) · S4.4 iki yol spektrum farkı ≤ 3 dB (B) ·
S4.5 aynı mekândaki replikler aynı oda yanıtıyla (H).
Diyalog stemi KURGU_PLANI diyalog[] yerleşiminden kurulur (son_miks toplar; render kendisi miks yapmaz).
Çıkış kodları: 0 S4 GEÇ/BAYRAK · 1 S4 HATA · 2 diyalog.json yok · 4 kullanım.
"""
import os, sys, zlib
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "diyalog_esitle 1.0"
RT60 = {"kucuk": 0.35, "orta": 0.6, "buyuk": 1.1, "dis": 0.15, "acik": 0.15, "magara": 1.8}
ISLAK = {"yakin": 0.06, "orta": 0.14, "uzak": 0.28}
UZAKLIK = {"CY": "yakin", "Y": "yakin", "OY": "yakin", "O": "orta", "OG": "orta", "G": "uzak", "EG": "uzak"}
BANTLAR = [100 * 2 ** (i / 3) for i in range(0, 20) if 100 * 2 ** (i / 3) <= 8000]
SPEKTRUM_MAX_DB, EQ_MAX_DB = 3.0, 6.0


def hedef_lufs(r, p, E):
    s = (p.get("_derlenir") or {}).get("seviye")
    if isinstance(s, (int, float)): return float(s), r.get("seviye") or "ozel"
    tes = r.get("teslim") or (p.get("replik") or {}).get("teslim") or "normal"
    sinif = r.get("seviye") or ((ko.po.sozluk("plan").get("teslim") or {}).get(tes) or {}).get("lufs") or "normal"
    return float((E.get("diyalog_lufs") or {}).get(sinif, -19.5)), sinif


def oda_yaniti(oda, sr):
    """Boyuttan sentetik dönüm yanıtı: üstel sönümlü gürültü (aynı oda adı = aynı tohum = aynı yanıt; S4.5)."""
    try:
        import pyroomacoustics  # noqa: F401  (MIT; kuruluysa ileride gerçek oda benzetimi buraya)
    except Exception: pass
    rt = next((v for k, v in RT60.items() if k in (oda or "")), 0.5)
    n = int(sr * min(rt * 1.2, 2.5)); rng = np.random.default_rng(zlib.crc32((oda or "oda").encode()))
    t = np.arange(n) / sr; ir = rng.standard_normal(n) * np.exp(-6.91 * t / rt)
    ir[: int(0.003 * sr)] = 0
    return (ir / (np.sqrt(np.sum(ir ** 2)) or 1.0)).astype(np.float32)


def evrisim(a, h):
    n = len(a) + len(h) - 1; N = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(a, N) * np.fft.rfft(h, N), N)[:n].astype(np.float32)


def ltas(a, sr):
    if len(a) < 1024: return None
    F = np.abs(np.fft.rfft(a * np.hanning(len(a)))) ** 2; f = np.fft.rfftfreq(len(a), 1 / sr); out = []
    for b in BANTLAR:
        m = (f >= b / 2 ** (1 / 6)) & (f < b * 2 ** (1 / 6)); out.append(10 * np.log10(np.mean(F[m]) + 1e-20) if m.any() else -200)
    return np.array(out)


def eq_uygula(a, sr, kazanc_db):
    F = np.fft.rfft(a); f = np.fft.rfftfreq(len(a), 1 / sr)
    g = np.interp(np.log2(np.maximum(f, 1.0)), np.log2(BANTLAR), np.clip(kazanc_db, -EQ_MAX_DB, EQ_MAX_DB))
    return np.fft.irfft(F * 10 ** (g / 20), len(a)).astype(np.float32)


def _sahne(pl, r): return ko.zanaat(pl.get(r.get("kaynak_plan"), {})).get("sahne_grubu")


def esitle(kok, argv=()):
    argv = list(argv); denet = ko.bayrak(argv, "--denetle")
    dj = ko.diyalog_oku(kok); pl = ko.sahne_planlari(kok); s = ko.sahneler(kok); E = ko.po.esik(); tol = float(E.get("diyalog_lufs_tolerans", 1.0))
    olc, sonuc, sesler = [], {}, {}
    for rid, r in sorted(dj["replikler"].items()):
        src = ko.replik_dosyasi(kok, r, tercih=("dosya",))
        if not src: olc.append(ko.m("S4.1_seviye", "OLCULEMEDI", r.get("kaynak_plan"), replik=rid, neden="replik dosyası yok")); continue
        p = pl.get(r.get("kaynak_plan"), {}); a, sr = ko.wav_oku(src); hedef, sinif = hedef_lufs(r, p, E)
        sg = _sahne(pl, r); oda = (((s.get("sahne_gruplari") or {}).get(sg) or {}).get("ses") or {}).get("oda_yaniti")
        uz = UZAKLIK.get((ko.zanaat(p).get("kamera") or {}).get("kadraj"), "orta")
        sesler[rid] = {"a": a, "sr": sr, "hedef": hedef, "sinif": sinif, "sg": sg, "oda": oda, "uz": uz, "src": src,
                       "mekan": ((s.get("sahne_gruplari") or {}).get(sg) or {}).get("mekan")}
    if denet:
        for rid, v in sesler.items():
            L = ko.replik_lufs(v["a"], v["sr"])
            olc.append(ko.m("S4.1_seviye", "GEC" if abs(L - v["hedef"]) <= tol else "HATA", dj["replikler"][rid].get("kaynak_plan"),
                            replik=rid, olcu=round(L, 2), esik=[round(v["hedef"] - tol, 2), round(v["hedef"] + tol, 2)],
                            kok_neden=None if abs(L - v["hedef"]) <= tol else "seviye_zipladi"))
        return _rapor(kok, dj, olc, sonuc)
    # iki yol arası tını eşleme (karakter başına)
    kar = {}
    for rid, v in sesler.items():
        r = dj["replikler"][rid]; kar.setdefault(r.get("karakter"), {}).setdefault(r.get("yol_gercek") or r.get("yol_plan"), []).append(rid)
    for k, yollar in kar.items():
        if not (yollar.get("veo_donustur") and yollar.get("tts")): continue
        sp = lambda ids: np.mean([x for x in (ltas(sesler[i]["a"], sesler[i]["sr"]) for i in ids) if x is not None], axis=0)
        A, B = sp(yollar["veo_donustur"]), sp(yollar["tts"])
        if np.ndim(A) == 0 or np.ndim(B) == 0: continue
        fark = (A - np.mean(A)) - (B - np.mean(B))
        if np.max(np.abs(fark)) > SPEKTRUM_MAX_DB:
            for i in yollar["tts"]: sesler[i]["a"] = eq_uygula(sesler[i]["a"], sesler[i]["sr"], fark)
        B2 = np.mean([ltas(sesler[i]["a"], sesler[i]["sr"]) for i in yollar["tts"]], axis=0)
        f2 = float(np.max(np.abs((A - np.mean(A)) - (B2 - np.mean(B2)))))
        olc.append(ko.m("S4.4_tini", "GEC" if f2 <= SPEKTRUM_MAX_DB else "BAYRAK", None, karakter=k, olcu=round(f2, 2), esik=SPEKTRUM_MAX_DB,
                        once=round(float(np.max(np.abs(fark))), 2)))
    for rid, v in sesler.items():
        r = dj["replikler"][rid]; a, sr = v["a"], v["sr"]
        islak = evrisim(a, oda_yaniti(v["oda"], sr)) * ISLAK[v["uz"]]
        b = np.concatenate([a, np.zeros(len(islak) - len(a), np.float32)]) + islak
        L0 = ko.replik_lufs(b, sr); g = v["hedef"] - L0 if L0 > ko.SESSIZ_DB else 0.0
        b = b * ko.kazanc(g)
        if ko.tepe_dbfs(b) > -0.5: olc.append(ko.m("S4_tepe", "BAYRAK", r.get("kaynak_plan"), replik=rid, olcu=round(ko.tepe_dbfs(b), 2),
                                                    neden="kazanç sonrası tepe yüksek; son_miks sınırlayıcısı tutar"))
        out = ko.wav_yaz(os.path.join(kok, "SESLER", "esit", f"{rid}.wav"), np.clip(b, -1, 1), sr)
        L = ko.replik_lufs(b, sr)
        r.update(dosya_esit=ko.goreli(kok, out), olculen_lufs=round(L, 2), kazanc_db=round(g, 2), oda=v["oda"], uzaklik=v["uz"], seviye=v["sinif"])
        r.setdefault("denetim", {})["S4"] = "GEC" if abs(L - v["hedef"]) <= tol else "HATA"
        olc.append(ko.m("S4.1_seviye", r["denetim"]["S4"], r.get("kaynak_plan"), replik=rid, olcu=round(L, 2), esik=v["hedef"],
                        kaynak_lufs=round(ko.replik_lufs(a, sr), 2)))
        sonuc[rid] = (v["sg"], r.get("karakter"), v["sinif"], L, v["mekan"], v["oda"])
    gr = {}
    for rid, (sg, k, sn, L, mek, oda) in sonuc.items(): gr.setdefault((sg, k, sn), []).append((rid, L))
    for (sg, k, sn), xs in gr.items():
        if len(xs) < 2: continue
        fark = max(L for _, L in xs) - min(L for _, L in xs)
        olc.append(ko.m("S4.2_sahne_ici", "GEC" if fark <= tol else "HATA", None, sahne_grubu=sg, karakter=k, olcu=round(fark, 2), esik=tol))
    mk = {}
    for rid, (sg, k, sn, L, mek, oda) in sonuc.items(): mk.setdefault(mek, set()).add(oda)
    for mek, odalar in mk.items():
        olc.append(ko.m("S4.5_oda", "GEC" if len(odalar) <= 1 else "HATA", None, mekan=mek, olcu=sorted(map(str, odalar))))
    ko.diyalog_yaz(kok, dj)
    stem(kok, dj)
    return _rapor(kok, dj, olc, sonuc)


def stem(kok, dj):
    kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: return None
    top = ko.toplam_sure(kp) + 5.0; st = np.zeros(int(top * ko.SR), np.float32)
    for d in kp.get("diyalog") or []:
        r = dj["replikler"].get(d.get("replik")) or {}; p = ko.replik_dosyasi(kok, r)
        if not p: continue
        a, sr = ko.wav_oku(p); a = ko.yeniden_ornekle(a, sr, ko.SR)
        ofs = float(r.get("dosya_ofset_sn") or 0.0) if r.get("yol_gercek", r.get("yol_plan")) != "tts" else 0.0
        ko.stem_ekle(st, ko.yumusat(a, ko.SR), ko.SR, float(d["cizelge_bas"]) - ofs)
    return ko.wav_yaz(ko.stem_yolu(kok, "diyalog"), st[: int(ko.toplam_sure(kp) * ko.SR) + ko.SR])


def _rapor(kok, dj, olc, sonuc):
    _, kp = ko.kurgu_plani(kok)
    kapsam = ko.kapsam_surum(kp) if kp else "FILM"
    return ko.rapor(kok, "S4", kapsam, olc, "A16", SURUM,
                    birimler=sorted({r.get("kaynak_plan") for r in dj["replikler"].values() if r.get("kaynak_plan") is not None}))


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    if not os.path.exists(os.path.join(kok, "SESLER", "diyalog.json")): print("!! SESLER/diyalog.json yok", flush=True); return 2
    _, r = esitle(kok, argv)
    return ko.po.cikis(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
