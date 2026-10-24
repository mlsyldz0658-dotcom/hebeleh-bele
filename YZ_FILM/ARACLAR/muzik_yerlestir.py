"""MÜZİK YERLEŞTİR — seçilmiş müzik ipuçlarını kurgu çizelgesine olay çözümüyle yerleştirir (TASARIM §6.6 `muzik.py --yerlestir`;
[SM2] SE4, §4.7.7 S6; [KU2] İ-8, test 15). muzik.py'nin `--yerlestir` alt komutu bu modüle yönlendirir.

Kullanım:
  python muzik_yerlestir.py --film <film>     → KURGU/SES_CIZELGESI.json → muzik[] (+ olay çözümü), KURGU/STEMS/muzik.wav, _RAPOR/S6_v<N>.json
Girdi: MUZIK/muzik_listesi.json (ipuçları: giris/cikis/hit olayları, bpm, olcu, seviye, secilen), KURGU_PLANI (son sürüm), SES_CIZELGESI
(sessizlik[]), KURGU/STEMS/diyalog.wav (varsa kısma ölçümü için), MUZIK/KAYNAK_KAYDI.json.
Olaylar (anı KURGU_PLANI'ndan çözülür; kırpma ya da sıra değişince müzik olayla birlikte kayar):
  plan_basi|plan_sonu|kesme {plan} · sahne_basi|sahne_sonu {sahne_grubu} · replik_basi|replik_sonu {replik} ·
  adim_basi|adim_sonu|bakis {plan, adim} (ölçülen adım; yoksa planlanan) · + ofset_sn / tasma_sn.
İş: parça ölçü (bar) sınırından kesilir; vuruş noktası (hit) olaya ±1 kare oturtulur, en çok ±%3 esnetilir (fazlası BAYRAK: ipucu yeniden
üretilir, 0 kredi); giriş rampası 1–3 sn, çıkış 2–4 sn; diyalog pencerelerinde otomatik kısma (diyaloğun ≥ 12 dB altı; hedef 14);
planlı müziksiz yerler boşaltılır. Seçilmiş parçası olan ipucu yoksa (zincir boş; D-25) müziksiz sürer + S6 BAYRAK.
Ölçüler: S6.2 diyalog altında ≥ 12 dB (H) · S6.3 diyalogsuz −20…−16 LUFS (B) · S6.4 kaplama %40–65, müziksiz ≤ 240 sn, müzikli ≤ 300 sn (B) ·
S6.5 rampalar (B) · S6.6 esnetme ≤ %3, bar kesimi (B) · S6.8 kaynak kaydı var ve sağlayıcı elle değil (H/B).
Çıkış kodları: 0 S6 GEÇ/BAYRAK · 1 S6 HATA · 2 KURGU_PLANI yok · 4 kullanım.
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "muzik_yerlestir 1.0"
ELLE_SAGLAYICILAR = ("gemini_muzik_paketi", "gemini_elle")
ESNETME_MAX = 0.03


def olay_zamani(kp, o):
    """Olay → çizelge anı (sn) ya da None (olayın planı kesildi / bulunamadı)."""
    if not isinstance(o, dict): return None
    t, ps = o.get("olay"), kp.get("planlar") or []
    if t in ("plan_basi", "plan_sonu", "kesme"):
        x = ko.plan_bul(kp, o.get("plan"))
        return None if not x else (x["cizelge_bas"] if t == "plan_basi" else ko.plan_sonu(x))
    if t in ("sahne_basi", "sahne_sonu"):
        xs = [x for x in ps if x.get("sahne_grubu") == o.get("sahne_grubu")]
        return None if not xs else (xs[0]["cizelge_bas"] if t == "sahne_basi" else ko.plan_sonu(xs[-1]))
    if t in ("replik_basi", "replik_sonu"):
        d = next((d for d in kp.get("diyalog") or [] if d.get("replik") == o.get("replik")), None)
        return None if not d else (d["cizelge_bas"] if t == "replik_basi" else d["cizelge_bas"] + d["sure"])
    if t in ("adim_basi", "adim_sonu", "bakis"):
        x = ko.plan_bul(kp, o.get("plan"))
        if not x: return None
        m = next((m for m in x["goruntu"].get("adimlar_olculen") or [] if m.get("id") == o.get("adim")), None) or {}
        k = m.get("bas" if t != "adim_sonu" else "bit")
        if k is None: k = o.get("plan_an")
        if k is None: return None
        tt = ko.cizelge_zamanina(x, float(k))
        return tt if x["cizelge_bas"] - 1e-6 <= tt <= ko.plan_sonu(x) + 1e-6 else None
    return None


def _bar_sn(ip):
    bpm = float(ip.get("bpm") or 0); vur = int(str(ip.get("olcu") or "4/4").split("/")[0] or 4)
    return 60.0 / bpm * vur if bpm > 0 else None


def _rampa(n, sr, giris, cikis):
    g = np.ones(n, np.float32); a, b = min(int(giris * sr), n), min(int(cikis * sr), n)
    if a: g[:a] = np.linspace(0, 1, a)
    if b: g[n - b:] *= np.linspace(1, 0, b)
    return g


def _kisma_zarfi(n, sr, t0, pencereler, db_, rampa=0.15):
    """Pencerelerde db_ kadar kısma; kenarlarda rampa sn'lik doğrusal geçiş (vektörel)."""
    g = np.ones(n, np.float32); r = max(1, int(rampa * sr)); k = ko.kazanc(db_); idx = np.arange(n)
    for a, b in pencereler:
        i, j = int((a - t0) * sr), int((b - t0) * sr)
        if j <= -r or i >= n + r: continue
        uzak = np.maximum(np.maximum(i - idx, idx - j), 0)                 # pencereye uzaklık (örnek)
        seg = np.where(uzak == 0, k, 1 - (1 - k) * np.clip(1 - uzak / r, 0, 1)).astype(np.float32)
        g = np.minimum(g, seg)
    return g


def yerlestir(kok, argv=()):
    kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: return None, None
    ml = ortak.json_oku(os.path.join(kok, "MUZIK", "muzik_listesi.json"), {}) or {}
    kk = ortak.json_oku(os.path.join(kok, "MUZIK", "KAYNAK_KAYDI.json"), {}) or {}
    sc = ko.ses_cizelgesi(kok); E = ko.po.esik(); sr = ko.SR; top = ko.toplam_sure(kp)
    st = np.zeros(int((top + 1) * sr), np.float32); olc, kayit = [], []
    dp = ko.stem_yolu(kok, "diyalog"); dl = ko.wav_oku(dp)[0] if os.path.exists(dp) else None
    dpen = [(float(d["cizelge_bas"]) - 0.2, float(d["cizelge_bas"]) + float(d["sure"]) + 0.2) for d in kp.get("diyalog") or []]
    sess = [(float(x["cizelge_bas"]), float(x["cizelge_bas"]) + float(x["sure"])) for x in sc.get("sessizlik") or []
            if x.get("tip") in ("muziksiz", "mutlak")]
    gl, gh = E.get("muzik_giris_sn") or [1, 3]; cl, ch = E.get("muzik_cikis_sn") or [2, 4]
    secili = [ip for ip in ml.get("ipuclari") or [] if ip.get("secilen")]
    if not secili:
        olc.append(ko.m("S6_muzik_yok", "BAYRAK", None, neden="müzik zinciri boş ya da seçilmiş parça yok: film müziksiz sürer (D-25)"))
    for ip in secili:
        if any(s in ELLE_SAGLAYICILAR for s in ([ip.get("saglayici")] if isinstance(ip.get("saglayici"), str) else ip.get("saglayici") or [])):
            if (ip.get("secilen_saglayici") or ip.get("saglayici")) in ELLE_SAGLAYICILAR:
                olc.append(ko.m("S6.8_elle_saglayici", "HATA", None, ipucu=ip["id"], neden="elle = True sağlayıcı zincire konamaz")); continue
        p = ko.mutlak(kok, ip["secilen"])
        if not os.path.exists(p): olc.append(ko.m("S6_parca_yok", "HATA", None, ipucu=ip["id"], olcu=ip["secilen"])); continue
        g, c = ip.get("giris") or {}, ip.get("cikis") or {}
        tg, tc = olay_zamani(kp, g), olay_zamani(kp, c)
        if tg is None or tc is None:
            olc.append(ko.m("S6_olay_cozulemedi", "BAYRAK", None, ipucu=ip["id"], neden="olayın planı kesildi ya da yok; ipucu kurgucuya"))
            continue
        tg += float(g.get("ofset_sn") or 0); tc += float(c.get("tasma_sn") or 0)
        a, sr0 = ko.wav_oku(p); a = ko.yeniden_ornekle(a, sr0, sr)
        bar = _bar_sn(ip); esnetme = 1.0
        for h in ip.get("hit") or []:
            th = olay_zamani(kp, h)
            if th is None or not bar: continue
            k = max(1, round((th - tg) / bar)); f = (th - tg) / (k * bar)
            if abs(1 - f) <= ESNETME_MAX: esnetme = f
            else: olc.append(ko.m("S6.6_esnetme", "BAYRAK", None, ipucu=ip["id"], olcu=round(abs(1 - f), 3), esik=ESNETME_MAX,
                                  karar="ipucu hedef süreyle yeniden üretilir (yerel, 0 kredi)"))
            break
        if esnetme != 1.0:
            n2 = int(len(a) * esnetme); a = np.interp(np.linspace(0, len(a) - 1, n2), np.arange(len(a)), a).astype(np.float32)
        gerek = tc - tg; uzun = len(a) / sr
        if bar:
            bar_e = bar * esnetme; kes = min(math.ceil(gerek / bar_e - 1e-6) * bar_e, math.floor(uzun / bar_e) * bar_e)
        else: kes = min(gerek, uzun)
        if kes < gerek - ko.KARE:
            olc.append(ko.m("S6_parca_kisa", "BAYRAK", None, ipucu=ip["id"], olcu=round(uzun, 2), esik=round(gerek, 2)))
        kes = min(kes, gerek + ch); n = int(kes * sr); a = a[:n]
        gr = min(max(float(g.get("rampa_sn") or 2.0), gl), gh); cr = min(max(float(c.get("rampa_sn") or 3.0), cl), ch)
        a = a * _rampa(len(a), sr, gr, min(cr, kes / 2))
        hedef = float((ip.get("seviye") or {}).get("diyalogsuz_lufs") or -18.0)
        L = ko.lufs(a, sr); a = a * ko.kazanc(hedef - L if L > ko.SESSIZ_DB else 0.0)
        alt = float((ip.get("seviye") or {}).get("diyalog_alti_db") or 14.0)
        ref = ko.lufs(dl, sr) if dl is not None and np.any(dl) else float((E.get("diyalog_lufs") or {}).get("normal", -19.5))
        kisma_db = min(0.0, (ref - alt) - hedef)
        pen = [(x, y) for x, y in dpen if y > tg and x < tg + kes]
        a = a * _kisma_zarfi(len(a), sr, tg, pen, kisma_db)
        if sess: a = a * _kisma_zarfi(len(a), sr, tg, sess, -120.0, rampa=0.3)
        ko.stem_ekle(st, ko.yumusat(a, sr), sr, tg)
        kayit.append({"ipucu": ip["id"], "dosya": ip["secilen"], "cizelge_bas": ko.kare(tg), "sure": ko.kare(kes), "giris_sn": gr, "cikis_sn": cr,
                      "kisma": [{"bas": round(x, 3), "bit": round(y, 3), "db": round(kisma_db, 1)} for x, y in pen], "gecici": False,
                      "esnetme": round(esnetme, 4), "bar_sn": None if not bar else round(bar * esnetme, 4),
                      "olay_cozumu": {"giris": round(tg - float(g.get("ofset_sn") or 0), 3), "cikis": round(tc - float(c.get("tasma_sn") or 0), 3)}})
        olc.append(ko.m("S6.5_rampa", "GEC" if gl <= gr <= gh and cl <= cr <= ch else "BAYRAK", None, ipucu=ip["id"], olcu=[gr, cr]))
        if ip["secilen"] not in kk and os.path.basename(ip["secilen"]) not in kk:
            olc.append(ko.m("S6.8_kaynak_kaydi", "BAYRAK", None, ipucu=ip["id"], neden="KAYNAK_KAYDI.json'da kayıt yok (muzik --uret yazar)"))
    st = st[: int(top * sr)]
    ko.wav_yaz(ko.stem_yolu(kok, "muzik"), st)
    _olcumler(st, dl, kp, kayit, E, olc, sr, top)
    sc["muzik"] = kayit; sc.setdefault("ambiyans", []); sc.setdefault("efektler", []); sc.setdefault("sessizlik", [])
    ko.ses_cizelgesi_yaz(kok, sc, kp_yol, kp)
    return ko.rapor(kok, "S6", ko.kapsam_surum(kp), olc, "A16", SURUM, ek={"kurgu_plani_imza": ko.plan_imza(kp)}, girdi_imza=ko.plan_imza(kp))


def _olcumler(st, dl, kp, kayit, E, olc, sr, top):
    if not kayit or top <= 0: return
    n = int(0.5 * sr); var = np.array([np.sqrt(np.mean(st[i:i + n] ** 2)) > 1e-4 for i in range(0, max(1, len(st) - n + 1), n)])
    kap = float(var.mean()) if len(var) else 0.0; lo, hi = E.get("muzik_kaplama_oran") or [0.4, 0.65]
    olc.append(ko.m("S6.4_kaplama", "GEC" if lo <= kap <= hi else "BAYRAK", None, olcu=round(kap, 3), esik=[lo, hi]))
    def en_uzun(v, deger):
        en = s = 0
        for x in v: s = s + 1 if x == deger else 0; en = max(en, s)
        return en * 0.5
    for ad, deger, mx in (("muziksiz", False, E.get("muziksiz_blok_max_sn", 240)), ("muzikli", True, E.get("muzikli_blok_max_sn", 300))):
        u = en_uzun(var, deger)
        olc.append(ko.m(f"S6.4_{ad}_blok", "GEC" if u <= mx else "BAYRAK", None, olcu=u, esik=mx))
    alt_min = float(E.get("muzik_diyalog_alti_min_db", 12))
    for d in kp.get("diyalog") or []:
        a, b = float(d["cizelge_bas"]), float(d["cizelge_bas"]) + float(d["sure"])
        Lm = ko.lufs(ko.pencere(st, sr, a, b), sr) if b - a >= 0.4 else ko.SESSIZ_DB
        if Lm <= ko.SESSIZ_DB: continue
        if dl is None: olc.append(ko.m("S6.2_diyalog_alti", "OLCULEMEDI", d["plan"], replik=d["replik"], neden="diyalog stemi yok")); continue
        Ld = ko.lufs(ko.pencere(dl, sr, a, b), sr)
        f = Ld - Lm
        olc.append(ko.m("S6.2_diyalog_alti", "GEC" if f >= alt_min - 0.5 else "HATA", d["plan"], replik=d["replik"], olcu=round(f, 2),
                        esik=alt_min, kok_neden=None if f >= alt_min - 0.5 else "muzik_maskeledi"))
    lo3, hi3 = E.get("muzik_diyalogsuz_lufs") or [-20, -16]
    for k in kayit:
        seg = ko.pencere(st, sr, k["cizelge_bas"] + k["giris_sn"], k["cizelge_bas"] + k["sure"] - k["cikis_sn"])
        L = ko.lufs(seg, sr) if len(seg) >= 0.4 * sr else None
        if L is None or L <= ko.SESSIZ_DB: continue
        olc.append(ko.m("S6.3_diyalogsuz_seviye", "GEC" if lo3 - 1 <= L <= hi3 + 1 else "BAYRAK", None, ipucu=k["ipucu"], olcu=round(L, 2), esik=[lo3, hi3]))


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    _, r = yerlestir(kok, argv)
    if not r: print("!! KURGU_PLANI yok; önce plan_kurgu.py", flush=True); return 2
    return ko.po.cikis(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
