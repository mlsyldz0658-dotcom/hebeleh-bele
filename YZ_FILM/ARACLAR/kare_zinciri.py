"""KARE ZİNCİRİ — son kare zinciri: kaynak klipten zincir karesini çıkarır ve G1Z kapısından geçirir (TASARIM D-15, §6.5, §7.2 G1Z).

Kullanım:
  python kare_zinciri.py --cikar [<ardil_plan,…>] --film <film>
        uretim.zincir.yontem = son_kare olan her ardıl B için (kaynak A = uretim.zincir.kaynak): A'nın klibi V1 + V2 + V3 GEÇ ise
        Y55 penceresinden [son adımın bitişi + zincir_cikis_tutma_ic_min_sn (0,2), klip_sn − 0,5] en durgun ve keskin kare seçilir
        (hareket enerjisi en düşük; eşitlikte keskin olan), doğal en-boyda (1280×720) üretken düzeltme olmadan çıkarılır.
        Teknik son kare (-sseof) kullanılmaz. B'nin planlanmış görseli SIRALI_GORSEL/_PLANLI/<B>.jpg'ye taşınır (silinmez),
        zincir karesi SIRALI_GORSEL/<B>.jpg olur. G1Z: kişi sayısı (H), kimlik bantları (G1 ile aynı: < 0,363 H), keskinlik
        ≥ 0,6 × A'nın ilk karesi (B), B'nin planlanmış görseline DINOv2 ≥ 0,70 (B), derinlik ≤ zincir_derinlik_max (2; aşılırsa H:
        yeniden demirleme). Sonuç SAHNELER.json → B.uretim.zincir {kesim_sn, kare_sha1, derinlik, g1z{sonuc, sha1}} ve
        A.uretim.zincir_cikis {kesim_sn, kilit: true} (kurguda çıkış noktası kilitli; uretim alanı plan imzasına girmez).
        → _RAPOR/G1Z_FILM_t<tur>.json (kuyruk önerileri)
Kurallar: kaynak hazır değilse ardıl atlanır (bekliyor; blok_plani onu bagimli_bekleyen'de tutar). ÖLÇÜLEMEDİ asla GEÇ değildir:
  kimlik ölçülemezse G1Z BAYRAK olur ve ardıl gönderilmez (uygunluk G1Z GEÇ ister).
Çıkış kodları: 0 rapor yazıldı · 1 girdi yok · 4 kullanım.
"""
import os, sys, re, json, glob, time, shutil, subprocess, tempfile, statistics
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kare_zinciri 1.0 (--cikar)"
VARSAYILAN = {"zincir_cikis_tutma_ic_min_sn": 0.2, "zincir_derinlik_max": 2, "g1z_keskinlik_oran_min": 0.6, "g1z_dino_min": 0.70,
              "g1_kimlik_hata": 0.363, "zincir_son_pay_sn": 0.5}


def esik(ad):
    try:
        import esikler; v = esikler.yukle().get(ad); v = VARSAYILAN[ad] if v is None else v
    except Exception: v = VARSAYILAN[ad]
    if ad == "g1_kimlik_hata": v = max(float(v), 0.363)
    return v


def _p(film, *a): return os.path.join(film, *a)


def pencere(a_plan, sure):
    """Y55: son fiziksel/mikro adımın bitişi + tutma payı … klip_sn − 0,5."""
    import video_denetim
    adim = video_denetim.adimlar(a_plan)
    son = max((float(x["bit"]) for x in adim), default=0.0)
    klip = float((a_plan.get("zanaat") or {}).get("klip_sn") or sure or 8)
    return son + esik("zincir_cikis_tutma_ic_min_sn"), min(klip, sure or klip) - esik("zincir_son_pay_sn")


def kare_sec(klip, a_plan):
    """(t, neden). Penceredeki en durgun (enerji en düşük) kare; eşitlikte en keskin. Pencere boşsa (None, neden)."""
    import video_denetim
    e, _ = video_denetim.enerji(klip)
    sure = e[-1][0] if e else 0.0
    w0, w1 = pencere(a_plan, sure)
    aday = [(t, x) for t, x in e if w0 <= t <= w1]
    if not aday: return None, f"Y55 penceresi boş ({w0:.2f}–{w1:.2f} sn): doğal durak yok → örtü planı"
    en_az = min(x for _, x in aday)
    yakin = [t for t, x in aday if x <= en_az * 1.05 + 1e-6]
    if len(yakin) > 1:
        try:
            from olcum import teknik
            d = tempfile.mkdtemp(prefix="kz_")
            try:
                puan = []
                for t in yakin[:6]:
                    k = video_denetim.kare_cikar(klip, t, os.path.join(d, f"{t:.3f}.jpg"))
                    puan.append((teknik.keskinlik(teknik.gri(k)), t))
                return max(puan)[1], None
            finally: shutil.rmtree(d, ignore_errors=True)
        except Exception: pass
    return yakin[0], None


def _sha(yol):
    import blok_plani
    return blok_plani.sha1_dosya(yol)


def g1z(film, b_plan, kare, planli, a_ilk, derinlik):
    """G1Z ölçümleri (liste)."""
    no = int(b_plan["no"]); olc = []
    def m(madde, seviye, **k): olc.append(dict({"madde": madde, "plan": no, "seviye": seviye}, **k))
    if derinlik > int(esik("zincir_derinlik_max")):
        m("derinlik", "HATA", olcu=derinlik, esik=esik("zincir_derinlik_max"), kok_neden="zincir_dikis", oneri="yeniden demirleme (yonetmen)")
    else: m("derinlik", "GEC", olcu=derinlik)
    try:
        from olcum import teknik
        ks, ka = teknik.keskinlik(teknik.gri(kare)), teknik.keskinlik(teknik.gri(a_ilk)) if a_ilk and os.path.exists(a_ilk) else None
        if ka: m("keskinlik", "GEC" if ks >= esik("g1z_keskinlik_oran_min") * ka else "BAYRAK", olcu=round(ks / ka, 3), esik=esik("g1z_keskinlik_oran_min"))
        else: m("keskinlik", "OLCULEMEDI", neden="A'nın ilk karesi yok")
    except Exception as e: m("keskinlik", "OLCULEMEDI", neden=e.__class__.__name__)
    try:
        from olcum import kimlik
        ok, neden = kimlik.hazir()
        if not ok: raise RuntimeError(neden)
        yk = kimlik.yuzler(kare); beklenen = len((b_plan.get("zanaat") or {}).get("kadrajdakiler") or [])
        if beklenen and len(yk) != beklenen: m("kisi_sayisi", "HATA", olcu=len(yk), esik=beklenen, kok_neden="fazla_kisi" if len(yk) > beklenen else "karakter_kayboldu")
        else: m("kisi_sayisi", "GEC", olcu=len(yk))
        ref = kimlik.yuzler(planli) if planli and os.path.exists(planli) else []
        if ref and yk:
            s = min(max(kimlik.benzerlik(r["vektor"], f["vektor"]) for f in yk) for r in ref)
            m("kimlik", "HATA" if s < esik("g1_kimlik_hata") else "GEC", olcu=round(s, 4), esik=esik("g1_kimlik_hata"),
              **({"kok_neden": "yuz_degisti"} if s < esik("g1_kimlik_hata") else {}))
        else: m("kimlik", "OLCULEMEDI", neden="planlanmış görselde ya da zincir karesinde yüz yok")
    except Exception as e: m("kimlik", "OLCULEMEDI", neden=str(e)[:120])
    try:
        from olcum import gorunum
        ok, neden = gorunum.hazir()
        if not ok: raise RuntimeError(neden)
        s = gorunum.benzerlik(gorunum.dinov2(kare), gorunum.dinov2(planli))
        m("planli_benzerlik", "GEC" if s >= esik("g1z_dino_min") else "BAYRAK", olcu=round(s, 4), esik=esik("g1z_dino_min"))
    except Exception as e: m("planli_benzerlik", "OLCULEMEDI", neden=str(e)[:120])
    return olc


def cikar(film, nolar=None, tur=1, gorev=None):
    """Zincir karelerini çıkarır, G1Z raporunu yazar. Raporu döndürür."""
    import kapi, video_denetim, blok_plani
    film = os.path.abspath(film); sp = _p(film, "SAHNELER.json"); doc = ortak.json_oku(sp, {}) or {}
    pl = {int(p["no"]): p for p in doc.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
    hedef = sorted(int(n) for n in (nolar or pl))
    olc, birim, kuyruk, degisti = [], [], [], False
    for bno in hedef:
        b = pl.get(bno)
        if not b: continue
        z = (b.setdefault("uretim", {})).setdefault("zincir", {})
        if (z.get("yontem") or "bagimsiz") != "son_kare" or z.get("kaynak") is None: continue
        if (z.get("g1z") or {}).get("sonuc") == "GEC" and os.path.exists(_p(film, "SIRALI_GORSEL", f"{bno:03d}.jpg")) and \
                blok_plani._sha_tutar(_p(film, "SIRALI_GORSEL", f"{bno:03d}.jpg"), z["g1z"].get("sha1")): continue   # zaten çıkarıldı
        ano = int(z["kaynak"]); a = pl.get(ano) or {"no": ano}
        kap = blok_plani.kunye_kapilari(film, ano)
        eksik = [g for g in ("V1", "V2", "V3") if (kap.get(g) or {}).get("sonuc") != "GEC"]
        klip = _p(film, "SIRALI_VIDEO", f"{ano:03d}.mp4")
        if eksik or not os.path.exists(klip):
            continue                                   # kaynak hazır değil: ardıl bekler (rapora girmez; blok_plani bagimli tutar)
        birim.append(bno)
        try: t, neden = kare_sec(klip, a)
        except video_denetim.Olculemedi as e: olc.append({"madde": "G1Z", "plan": bno, "seviye": "OLCULEMEDI", "neden": str(e)}); continue
        if t is None:
            olc.append({"madde": "pencere", "plan": bno, "seviye": "HATA", "neden": neden, "kok_neden": "zincir_dikis",
                        "oneri": "örtü planı (D-15) ya da yeniden demirleme"}); continue
        gecici = _p(film, "SIRALI_GORSEL", "_ZINCIR", f"{bno:03d}_{ano:03d}_{t:.2f}.jpg")
        video_denetim.kare_cikar(klip, t, gecici)
        planli = _p(film, "SIRALI_GORSEL", "_PLANLI", f"{bno:03d}.jpg"); bas = _p(film, "SIRALI_GORSEL", f"{bno:03d}.jpg")
        if os.path.exists(bas) and not os.path.exists(planli):
            os.makedirs(os.path.dirname(planli), exist_ok=True); shutil.move(bas, planli)        # planlı görsel saklanır (silinmez)
        elif os.path.exists(bas):
            eski = _p(film, "_ESKI", time.strftime("%Y%m%d_%H%M%S_") + f"zincir_{bno:03d}.jpg")
            os.makedirs(os.path.dirname(eski), exist_ok=True); shutil.move(bas, eski)
        a_ilk = _p(film, "SIRALI_GORSEL", "_ZINCIR", f"{ano:03d}_ilk.jpg")
        try: video_denetim.kare_cikar(klip, 0.0, a_ilk)
        except Exception: a_ilk = None
        derin = int(((a.get("uretim") or {}).get("zincir") or {}).get("derinlik") or 0) + 1 \
            if ((a.get("uretim") or {}).get("zincir") or {}).get("yontem") == "son_kare" else 1
        o = g1z(film, b, gecici, planli, a_ilk, derin); olc += o
        shutil.copyfile(gecici, bas); sha = _sha(bas)
        sonuc = kapi.en_kotu([kapi.madde_sonucu(m["seviye"]) for m in o] or ["GEC"])
        z.update(kesim_sn=round(t, 3), kare_sha1=sha, derinlik=derin, kaynak=ano, g1z={"sonuc": sonuc, "sha1": sha, "zaman": time.strftime("%Y-%m-%d %H:%M:%S")})
        a.setdefault("uretim", {})["zincir_cikis"] = {"ardil": bno, "kesim_sn": round(t, 3), "kilit": True}
        degisti = True
        for m in o:
            if m["seviye"] == "HATA" and m.get("kok_neden"):
                kuyruk.append({"plan": ano, "tur": "video", "seviye": "HATA", "kok_neden": m["kok_neden"], "cozum": "yeniden_cek",
                               "dilim": "goruntu", "zincir_etkisi": [bno],
                               "sifir_kredi": {"denendi": True, "gerekce": f"G1Z {m['madde']}: zincir karesi kaynağın kendisinden; kırpma çözmez"}})
    if degisti: ortak.atomik_yaz(sp, doc)
    yol, r = kapi.kaydet(_p(film, "_RAPOR"), "G1Z", "FILM", olc, tur=tur, tur_dosyada=True, asama="A14", gorev=gorev, arac_surum=SURUM,
                         birimler=birim, kuyruk=kuyruk)
    return r


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    if "--cikar" not in argv: print(__doc__); return 4
    film = argv[argv.index("--film") + 1] if "--film" in argv else None
    if not film or not os.path.isdir(film): print("film klasörü yok (--film)"); return 1
    i = argv.index("--cikar"); nolar = None
    if i + 1 < len(argv) and re.fullmatch(r"[0-9][0-9,]*", argv[i + 1]): nolar = [int(x) for x in argv[i + 1].split(",") if x]
    import video_denetim
    r = cikar(film, nolar, tur=video_denetim._gorev_turu(), gorev=os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None)
    print(f"G1Z: {r['sonuc']} · {r['ozet']}"); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
