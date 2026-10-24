"""YAYIN ANALİZİ — yayından 48 sa / 7 gün / 28 gün sonra gerçek seyirci (TASARIM §1.3 A18a, D-24, EK3-2/3/4; CSV kipi P1, OAuth P2).

film.py görevi olarak ("<arac> <args> --film <film>"; aşama isteğe bağlı, yayından 48 saat sonra):
  python yayin_analiz.py [--gun 2|7|28] [--csv <dosya.csv> ...] [--yayin-tarihi 2026-11-20] --film <film>
Girdi: kullanıcının isteğe bağlı YouTube Studio dışa aktarımları <film>/GELENLER/YOUTUBE/*.csv (video özeti: gösterim, tıklama
  oranı, ortalama izleme; ve izleyici tutma eğrisi: video konumu % ya da sn → tutma %). Gün verilmezse yayın tarihinden
  (YAYIN/YUKLEME.json yayin_zamani, PAKET.json yayin_tarihi ya da --yayin-tarihi) hesaplanır: ≥ 28 → 28, ≥ 7 → 7, ≥ 2 → 2.
İş: tutma eğrisi film çizelgesine (KURGU/KURGU_PLANI.json) eşlenir; en dik düşüşler (10 sn'de ≥ DUSUS_MIN_PUAN puan; ilk 5 sn hariç)
  plan kimliğiyle bulunur ve ders defterine `olay: gercek_seyirci, kaynak: gercek_seyirci` (en yüksek kanıt ağırlığı) yazılır
  (aynı film + gün için bir kez). 48 saatte tıklama oranı ya da ilk 30 sn tutması kanal ortalamasının (KANAL_TESHIS.json) altındaysa
  kapak/başlık değişikliği önerisi BİLGİ olarak yazılır; değişiklik kullanıcının işidir.
Çıktı: _RAPOR/YAYIN_ANALIZ_<gun>.json (veri yoksa sonuc "olculemedi"). Kapı değildir.
Çıkış kodları: 0 tamam ya da ölçülemedi · 1 film yok · 4 ORTAM (YOLLAR.json yok) · kullanım 4.
"""
import os, sys, glob, json, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import kanal_teshis as kt

SURUM = "yayin_analiz 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
GUNLER = (2, 7, 28)
DUSUS_PENCERE_SN, DUSUS_MIN_PUAN, DUSUS_MAX, BAS_HARIC_SN = 10.0, 3.0, 5, 5.0     # (tahmin; EK3 kalibrasyonu)


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def film_adi(film): return (ortak.json_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}).get("film") or os.path.basename(film)


def _tarih(x):
    try:
        d = datetime.datetime.fromisoformat(str(x).replace("Z", "+00:00"))
        return d if d.tzinfo else d.astimezone()
    except (TypeError, ValueError): return None


def yayin_tarihi(film, verilen=None):
    if verilen: return _tarih(verilen)
    for p, a in (("YAYIN/YUKLEME.json", "yayin_zamani"), ("YAYIN/PAKET.json", "yayin_tarihi"), ("YAYIN/PAKET.json", "yayin_zamani")):
        v = (ortak.json_oku(os.path.join(film, *p.split("/")), {}) or {}).get(a)
        if v and _tarih(v): return _tarih(v)
    return None


def gun_sec(film, gun=None, tarih=None):
    if gun: return int(gun)
    t = yayin_tarihi(film, tarih)
    if not t: return None
    gecen = (datetime.datetime.now().astimezone() - t).total_seconds() / 86400
    uygun = [g for g in GUNLER if gecen >= g]
    return uygun[-1] if uygun else 0


def film_suresi(film):
    yd = ortak.json_oku(os.path.join(film, "YAYIN", "YAYIN_DOGRULAMA.json"), {}) or {}
    s = (yd.get("sure") or {}).get("olculen")
    if s: return float(s)
    import yayin_paketi
    return yayin_paketi.film_suresi(yayin_paketi.kurgu(film))


def tutma_egrisi(b, s, sure):
    """[(sn, tutma %)] ya da None. Konum % (0–100) ise süreyle çarpılır; 0–1 oranları yüzdeye çevrilir."""
    kc, tc = kt.sutun(b, "konum"), kt.sutun(b, "tutma")
    if not kc or not tc: return None
    ham = [(kt.sure_sn(r.get(kc)) if ":" in str(r.get(kc)) else kt.sayi(r.get(kc)), kt.sayi(r.get(tc))) for r in s]
    ham = [(x, y) for x, y in ham if x is not None and y is not None]
    if len(ham) < 3: return None
    yuzde_konum = "%" in kc or "percent" in kc.lower() or "yüzde" in kc.lower() or max(x for x, _ in ham) <= 100.0 and sure and sure > 150
    if max(y for _, y in ham) <= 1.5: ham = [(x, y * 100) for x, y in ham]
    if max(x for x, _ in ham) <= 1.0 and sure: ham = [(x * 100, y) for x, y in ham]; yuzde_konum = True
    if yuzde_konum:
        if not sure: return None
        ham = [(x / 100.0 * sure, y) for x, y in ham]
    return sorted(ham)


def deger(egri, t):
    if not egri: return None
    if t <= egri[0][0]: return egri[0][1]
    for (x0, y0), (x1, y1) in zip(egri, egri[1:]):
        if x0 <= t <= x1: return y0 + (y1 - y0) * ((t - x0) / (x1 - x0) if x1 > x0 else 0)
    return egri[-1][1]


def dususler(egri):
    if not egri: return []
    son = egri[-1][0]; adaylar = []; t = BAS_HARIC_SN
    while t + DUSUS_PENCERE_SN <= son:
        d = deger(egri, t) - deger(egri, t + DUSUS_PENCERE_SN)
        if d >= DUSUS_MIN_PUAN: adaylar.append((d, t))
        t += DUSUS_PENCERE_SN / 2
    secilen = []
    for d, t in sorted(adaylar, reverse=True):
        if all(abs(t - s["sn"]) >= DUSUS_PENCERE_SN for s in secilen):
            secilen.append({"sn": round(t, 1), "dusus_puan": round(d, 2)})
        if len(secilen) == DUSUS_MAX: break
    return sorted(secilen, key=lambda x: x["sn"])


def plan_bul(kp, t):
    for p in kp.get("planlar") or []:
        b = float(p.get("cizelge_bas") or 0)
        if b <= t < b + float(p.get("sure") or 0): return p.get("plan") or p.get("sira"), p.get("sahne_grubu")
    return None, None


def onceki_kayit_var(film_ad, gun):
    try:
        import ders_defteri as dd
        return any(d.get("olay") == "gercek_seyirci" and d.get("film") == film_ad and (d.get("baglam") or {}).get("gun") == gun
                   for d in dd.ham_oku())
    except Exception: return False


def analiz(film, gun=None, csvler=None, tarih=None):
    ad = film_adi(film); g = gun_sec(film, gun, tarih)
    dos = csvler or sorted(glob.glob(os.path.join(film, "GELENLER", "YOUTUBE", "*.csv")))
    r = {"_surum": 1, "_uretim": {"asama": "A18a", "gorev": os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None,
                                  "arac_surum": SURUM, "zaman": simdi(), "ortam": "yerel" if os.name == "nt" else "bulut"},
         "film": ad, "gun": g, "dosyalar": [os.path.basename(p) for p in dos]}
    if g is None or g == 0 or not dos:
        r.update(sonuc="olculemedi", neden="yayın tarihi bilinmiyor" if g is None else "yayından 48 saat geçmedi" if g == 0 else
                 "YouTube Studio CSV'si yok (GELENLER/YOUTUBE/)")
        r["_uretim"]["sonuc"] = "BAYRAK"; return r
    sure = film_suresi(film); egri, ozet = None, None
    for p in dos:
        try: b, s = kt.csv_oku(p)
        except OSError: continue
        e = tutma_egrisi(b, s, sure)
        if e: egri = e; continue
        v, top = kt.video_satirlari(b, s)
        if v or top: ozet = top or v[0]
    import yayin_paketi
    kp = yayin_paketi.kurgu(film)
    r["ozet"] = ozet
    r["ilk30_tutma"] = round(deger(egri, 30.0), 2) if egri else None
    r["tutma_egrisi"] = [[round(x, 2), round(y, 2)] for x, y in (egri or [])]
    dus = []
    for d in dususler(egri):
        plan, sahne = plan_bul(kp, d["sn"]); dus.append(dict(d, plan=plan, sahne_grubu=sahne))
    r["dususler"] = dus
    kanal = (ortak.json_oku(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "KANAL_TESHIS.json"), {}) or {}).get("kanal_ortalama") or {}
    uyari = []
    if g == 2:
        if ozet and ozet.get("to") is not None and kanal.get("to") is not None and ozet["to"] < kanal["to"]:
            uyari.append(f"Tıklama oranı %{ozet['to']} < kanal ortalaması %{kanal['to']}: kapak ya da başlık değişikliği düşünülebilir.")
        k30 = kanal.get("ilk30_tutma")
        if r["ilk30_tutma"] is not None and k30 is not None and r["ilk30_tutma"] < k30:
            uyari.append(f"İlk 30 sn tutması %{r['ilk30_tutma']} < kanal ortalaması %{k30}: açılış ve kapak vaadi gözden geçirilebilir.")
    r["erken_uyari"] = uyari; r["uyari_notu"] = "Bilgidir; değişiklik kullanıcının işidir (D-24)." if uyari else None
    kayitlar = []
    if dus and not onceki_kayit_var(ad, g):
        import ders_defteri as dd
        for d in dus:
            kayitlar.append(os.path.basename(dd.kaydet(
                "gercek_seyirci", "gercek_seyirci", f"{g}. gün tutma eğrisi: {d['sn']} sn'de {d['dusus_puan']} puan düşüş",
                film=ad, asama="A18a", plan=d["plan"], kategori="tutma_dususu", rol_etiketi="kurgu",
                olcum={"dusus_puan": d["dusus_puan"], "pencere_sn": DUSUS_PENCERE_SN, "sn": d["sn"]},
                baglam={"gun": g, "sahne_grubu": d["sahne_grubu"]}, kanit=[f"_RAPOR/YAYIN_ANALIZ_{g}.json"])))
    r["ders_kayitlari"] = kayitlar
    r["sonuc"] = "tamam" if (egri or ozet) else "olculemedi"
    if r["sonuc"] == "olculemedi": r["neden"] = "CSV'lerde tanınan sütun yok"
    r["_uretim"]["sonuc"] = "GEC" if r["sonuc"] == "tamam" else "BAYRAK"
    return r


def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def main(a):
    if "-h" in a or "--help" in a: print(__doc__); return BITTI
    try:
        f = _arg(a, "--film")
        film = (os.path.abspath(f) if f and os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)) if f else None
        if not film or not os.path.isdir(film): print("!! --film <film> gerekli (klasör yok)"); return HATA
        gun = _arg(a, "--gun")
        if gun and (not gun.isdigit() or int(gun) not in GUNLER): print("!! --gun 2 | 7 | 28"); return ORTAM
        csvler = [a[i + 1] for i, x in enumerate(a) if x == "--csv" and i + 1 < len(a)] or None
        r = analiz(film, gun, csvler, _arg(a, "--yayin-tarihi"))
        ortak.atomik_yaz(os.path.join(film, "_RAPOR", f"YAYIN_ANALIZ_{r['gun'] or 0}.json"), r)
        print(f"Yayın analizi ({r['gun']}. gün): {r['sonuc']}" + (f" · {r.get('neden')}" if r.get("neden") else "")
              + (f" · {len(r.get('dususler') or [])} düşüş, {len(r.get('ders_kayitlari') or [])} ders kaydı" if r["sonuc"] == "tamam" else ""))
        for u in r.get("erken_uyari") or []: print("BİLGİ:", u)
        return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
