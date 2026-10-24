"""ANİMATİK İMZASI — `animatik: ONAYLI` imzası; imzasız ya da bayat imzayla video görevi açılmaz (TASARIM §1.5 kural 4, A12, KK3a;
[KU2] KR4 "Geçme", [UM2] T4).

Kullanım:
  python animatik_imza.py --imzala [--tur N] --film <film>    koşullar sağlanıyorsa ANIMATIK/ONAY.json yazar (0); değilse nedenler (1)
  python animatik_imza.py --dogrula --film <film>             0 ONAYLI ve imza güncel · 1 imza yok, reddedildi ya da bayat
  python animatik_imza.py --durum --film <film>               FILM_DURUM.animatik biçiminde {durum, imza, tur, neden} (her zaman 0)
Kodda (film.py video görevi açmadan önce; seyirci_topla A12 kapısı sağlanınca imzalar):
  ok, neden, imza = animatik_imza.dogrula(film)              · animatik_imza.video_acilabilir(film, sahte=…, a12_durum=…)
  ok, sonuc = animatik_imza.imzala(film, tur)                 · animatik_imza.durum(film)
İmza koşulları (hepsi bağımsız yeniden denetlenir; çağıranın sözüne güvenilmez):
  1. _RAPOR/HS_ANIMATIK_FILM_t<tur>.json geçerli kapı raporu (kapi.oku), sonuç HATA değil ve kapi_saglandi true (§1.4 kapı).
  2. KURGU/surumler/KURGU_PLANI_T1_v<tur>.json en son T1 sürümü; bütün görüntülü planlar `gorsel` + G1 GEC ("kapıyı yalnız bütün kareleri
     G1 GEÇ olan tur açar"); yer tutucu oranı ≤ RE animatik_yer_tutucu_max_oran.
  3. _RAPOR/RENDER_ANIMATIK_v<tur>.json: sonuç HATA değil, |kare farkı| ≤ RE render_sure_tolerans_kare, render bu T1 dosyasından (özet eşit)
     ve ANIMATIK/animatik_v<tur>.mp4 özeti rapordakiyle aynı.
  İmza = sha1(T1 özeti + video özeti + HS raporu özeti). Doğrulama dosyaları yeniden özetler: biri değişmişse ya da daha yeni bir T1 sürümü
  varsa imza bayattır (video görevi açılmaz). Eski imzalar ANIMATIK/ONAY_GECMIS.jsonl'de kalır (silinmez).
Çıkış kodları: 0 · 1 (yukarıda) · 4 kullanım.
"""
import os, sys, json, hashlib, argparse
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import zaman_cizelgesi_t1 as t1

SURUM = "animatik_imza 1.0"


def onay_yolu(film): return os.path.join(film, "ANIMATIK", "ONAY.json")


def _sha(p): return t1.sha(p, 40) if p and os.path.isfile(p) else None


def kosullar(film, tur):
    """(nedenler listesi, dosyalar sözlüğü) — boş liste: imzalanabilir."""
    film = os.path.abspath(film); n = []
    import kapi
    hs = os.path.join(film, "_RAPOR", "HS_ANIMATIK_FILM_t%d.json" % tur)
    r = None
    try: r = kapi.oku(hs)
    except kapi.RaporHatasi as e: n.append("HS_ANIMATIK t%d raporu yok ya da geçersiz (%s)" % (tur, "; ".join(e.hatalar)[:160]))
    if r is not None:
        if r.get("sonuc") == "HATA": n.append("HS_ANIMATIK kapısı HATA")
        if r.get("kapi_saglandi") is not True: n.append("seyirci kapısı sağlanmadı (§1.4)")
    son_n, _ = t1.son_surum(film, "T1")
    plan, pyol, _ = t1.plan_oku(film, "T1", tur)
    if plan is None: n.append("KURGU_PLANI_T1_v%d yok" % tur)
    else:
        if son_n != tur: n.append("daha yeni T1 sürümü var (v%d); imza v%d için istenemez" % (son_n, tur))
        gp = [p for p in plan.get("planlar") or [] if (p.get("goruntu") or {}).get("tur") in ("gorsel", "yer_tutucu")]
        g1_eksik = [p.get("plan") for p in gp if p["goruntu"].get("tur") != "gorsel" or p["goruntu"].get("g1") != "GEC"]
        if g1_eksik: n.append("bütün kareler G1 GEÇ değil (%d plan: %s)" % (len(g1_eksik), ", ".join(map(str, g1_eksik[:10]))))
        oran = len(g1_eksik) / len(gp) if gp else 0.0
        if oran > float(t1.E("animatik_yer_tutucu_max_oran") or 0.10): n.append("yer tutucu oranı %.2f > %.2f" % (oran, t1.E("animatik_yer_tutucu_max_oran")))
    rr = ortak.json_oku(os.path.join(film, "_RAPOR", "RENDER_ANIMATIK_v%d.json" % tur))
    video = os.path.join(film, "ANIMATIK", "animatik_v%d.mp4" % tur)
    if not isinstance(rr, dict): n.append("render raporu yok (kurgu_render --animatik)")
    else:
        tol = int(t1.E("render_sure_tolerans_kare") or 1)
        if rr.get("sonuc") == "HATA" or rr.get("fark_kare") is None or rr["fark_kare"] > tol:
            n.append("render süresi T1 ±%d kare değil (fark %s)" % (tol, rr.get("fark_kare")))
        if pyol and rr.get("kurgu_plani_imza") != t1.sha(pyol): n.append("render bu T1 dosyasından yapılmamış")
        if not os.path.isfile(video): n.append("animatik videosu yok")
        elif rr.get("video_imza") != t1.sha(video): n.append("animatik videosu render raporundakinden farklı")
    dosyalar = {"kurgu_plani": os.path.relpath(pyol, film).replace("\\", "/") if pyol else None,
                "video": os.path.relpath(video, film).replace("\\", "/"), "hs_rapor": os.path.relpath(hs, film).replace("\\", "/")}
    return n, dosyalar


def _ozetler(film, dosyalar):
    return {k: _sha(os.path.join(film, v)) if v else None for k, v in dosyalar.items()}


def imza_hesapla(oz): return hashlib.sha1(("%s|%s|%s" % (oz.get("kurgu_plani"), oz.get("video"), oz.get("hs_rapor"))).encode()).hexdigest()[:16]


def imzala(film, tur=None, gorev=None):
    film = os.path.abspath(film)
    tur = int(tur or t1.son_surum(film, "T1")[0] or 1)
    nedenler, dosyalar = kosullar(film, tur)
    if nedenler: return False, {"durum": "REDDEDILDI", "tur": tur, "nedenler": nedenler}
    oz = _ozetler(film, dosyalar)
    k = {"_surum": 1, "_uretim": {"asama": "A12", "gorev": gorev, "girdi_imza": imza_hesapla(oz), "arac_surum": SURUM,
                                  "esik_surum": t1._esik_surum(), "sonuc": "GEC", "zaman": t1.simdi(), "ortam": t1.ortam()},
         "durum": "ONAYLI", "tur": tur, "imza": imza_hesapla(oz), "dosyalar": dosyalar, "ozetler": oz}
    eski = ortak.json_oku(onay_yolu(film))
    if isinstance(eski, dict):
        with open(os.path.join(film, "ANIMATIK", "ONAY_GECMIS.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(eski, ensure_ascii=False) + "\n")
    ortak.atomik_yaz(onay_yolu(film), k)
    return True, k


def dogrula(film):
    """(ok, neden, imza). ok yalnız ONAYLI imza bütün dosyalarla güncelse."""
    film = os.path.abspath(film)
    k = ortak.json_oku(onay_yolu(film))
    if not isinstance(k, dict) or k.get("durum") != "ONAYLI": return False, "animatik ONAYLI değil (imza yok)", None
    oz = _ozetler(film, k.get("dosyalar") or {})
    for ad, v in oz.items():
        if v is None: return False, "imzalı dosya yok: %s" % ad, k.get("imza")
        if v != (k.get("ozetler") or {}).get(ad): return False, "imzadan sonra değişti: %s (bayat)" % ad, k.get("imza")
    if imza_hesapla(oz) != k.get("imza"): return False, "imza tutmuyor", k.get("imza")
    son_n, _ = t1.son_surum(film, "T1")
    if son_n != k.get("tur"): return False, "imzadan sonra yeni T1 sürümü var (v%d)" % son_n, k.get("imza")
    return True, None, k["imza"]


def video_acilabilir(film, sahte=False, a12_durum=None):
    """film.py'nin video aşamalarından (A13, A14a, A14) önce sorduğu tek soru. Sahte denemede (betikler taklit edilir) A12'nin
    görev defterindeki durumu (tamam/kismi) yeter; gerçek filmde imza şarttır."""
    if sahte: return (a12_durum in ("tamam", "kismi")), (None if a12_durum in ("tamam", "kismi") else "A12 bitmedi")
    ok, neden, _ = dogrula(film)
    return ok, neden


def durum(film):
    ok, neden, imza = dogrula(film)
    k = ortak.json_oku(onay_yolu(os.path.abspath(film)), {}) or {}
    return {"durum": "ONAYLI" if ok else "bekliyor", "imza": imza if ok else None, "tur": k.get("tur"), "neden": neden}


def main(argv=None):
    ap = argparse.ArgumentParser(description="Animatik ONAYLI imzası.")
    ap.add_argument("--imzala", action="store_true"); ap.add_argument("--dogrula", action="store_true"); ap.add_argument("--durum", action="store_true")
    ap.add_argument("--tur", type=int); ap.add_argument("--film"); ap.add_argument("--saglayici")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film): print("!! --film <film klasörü> gerekli."); return 4
    if o.imzala:
        g = t1.gorev_baglami(o.tur)
        ok, s = imzala(film, o.tur or (g["tur"] if os.environ.get("YZ_FILM_GOREV") else None), g["id"])
        print(json.dumps({"durum": s.get("durum"), "imza": s.get("imza"), "nedenler": s.get("nedenler")}, ensure_ascii=False)); return 0 if ok else 1
    if o.dogrula:
        ok, neden, imza = dogrula(film)
        print("ONAYLI (%s)" % imza if ok else "Video görevi açılmaz: " + neden); return 0 if ok else 1
    if o.durum: print(json.dumps(durum(film), ensure_ascii=False)); return 0
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main())
