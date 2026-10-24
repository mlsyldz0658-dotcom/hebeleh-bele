"""KANAL TEŞHİSİ — Ö0-g, YouTube Studio CSV kipi (TASARIM §1.2 Ö0-g, D-24, EK3; OAuth kipi P2 [SON] S-10).

Kullanıcının isteğe bağlı, tek seferlik YouTube Studio dışa aktarımı (Analytics → Gelişmiş mod → Dışa aktar → CSV; adımlar
BASLA_BURADAN.txt'de) <veri>/GELENLER/KANAL/ klasörüne konur. Soru sorulmaz; veri yoksa sonuç "ölçülemedi"dir, film beklemez.
Kullanım:
  python kanal_teshis.py [--csv <dosya.csv> ...] [--klasor <klasör>]
Çıktı: <veri>/BILGI/KANAL_TESHIS.md (insan için; yapımcı ve yayin-paketcisi okur) + KANAL_TESHIS.json (yayin_analiz kanal ortalaması).
Teşhis (video başına ve kanal ortalaması): keşif (gösterim az) · paketleme (gösterim tıklama oranı düşük) · film (ortalama izlenme
  yüzdesi düşük). Sınırlar (tahmin; ilk filmlerle kalibre edilir): gösterim < 1000, TO < %4, izlenme < %30.
CSV okuma esnektir: İngilizce ve Türkçe Studio başlıkları tanınır (Video title / Video başlığı, Impressions / Gösterimler,
  Impressions click-through rate (%) / Gösterim tıklama oranı (%), Views / Görüntüleme, Average view duration / Ortalama izleme süresi,
  Average percentage viewed (%) / Ortalama izlenme yüzdesi (%), Traffic source / Trafik kaynağı). "Total/Toplam" satırı ayrılır.
Kodda: csv_oku(p) → (başlıklar, satırlar) · sutun(basliklar, anahtar) · sayi("1.234,5") · sure_sn("1:02:03") · teshis(satirlar)
Çıkış kodları: 0 tamam ya da ölçülemedi · 4 ORTAM (YOLLAR.json yok) · kullanım 4.
"""
import os, re, sys, csv, glob, json, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kanal_teshis 1.0"
BITTI, ORTAM = 0, 4
GOSTERIM_MIN, TO_MIN, IZLENME_MIN = 1000, 4.0, 30.0       # (tahmin; EK3 kalibrasyonu)
SUTUNLAR = {
    "baslik": ("video title", "video başlığı", "video basligi", "content", "içerik", "title"),
    "yayin": ("video publish time", "yayınlanma", "publish"),
    "gosterim": ("impressions", "gösterimler", "gösterim sayısı", "gosterim"),
    "to": ("impressions click-through rate", "click-through", "tıklama oranı", "tiklama orani"),
    "izlenme": ("views", "görüntüleme", "goruntuleme", "izlenme sayısı"),
    "ort_sure": ("average view duration", "ortalama izleme süresi", "ortalama görüntüleme süresi"),
    "ort_oran": ("average percentage viewed", "ortalama izlenme yüzdesi", "ortalama görüntülenme yüzdesi", "izlenme yüzdesi"),
    "sure": ("duration", "süre"),
    "trafik": ("traffic source", "trafik kaynağı", "trafik kaynagi"),
    "konum": ("video position", "position", "konum", "video süresi içindeki konum", "zaman"),
    "tutma": ("absolute audience retention", "audience retention", "retention", "elde tutma", "izleyici tutma", "tutma"),
}
TOPLAM = ("total", "toplam")


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def csv_oku(p):
    with open(p, encoding="utf-8-sig", errors="replace", newline="") as f: metin = f.read()
    try: lehce = csv.Sniffer().sniff(metin[:4096], delimiters=",;\t")
    except csv.Error: lehce = csv.excel
    satirlar = [r for r in csv.reader(metin.splitlines(), lehce) if any(c.strip() for c in r)]
    if not satirlar: return [], []
    b = [c.strip() for c in satirlar[0]]
    return b, [dict(zip(b, [c.strip() for c in r])) for r in satirlar[1:]]


def sutun(basliklar, anahtar):
    """Başlık listesinde anahtar sözlüğüne uyan ilk sütun (önce tam uyum, sonra içerme)."""
    ks = SUTUNLAR[anahtar]; kl = [(b, b.lower()) for b in basliklar]
    for b, l in kl:
        if any(l == k or l.startswith(k + " (") for k in ks): return b
    for b, l in kl:
        if any(k in l for k in ks): return b
    return None


def sayi(x):
    if x is None: return None
    s = str(x).strip().replace("%", "").replace(" ", "").replace(" ", "")
    if not s or s in ("-", "—"): return None
    if re.fullmatch(r"-?\d{1,3}(\.\d{3})+(,\d+)?", s): s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d+,\d+", s): s = s.replace(",", ".")
    else: s = s.replace(",", "")
    try: return float(s)
    except ValueError: return None


def sure_sn(x):
    s = str(x or "").strip()
    if re.fullmatch(r"\d+(:\d{1,2}){1,2}", s):
        t = 0
        for p in s.split(":"): t = t * 60 + int(p)
        return float(t)
    return sayi(s)


def ortalama(xs):
    xs = [x for x in xs if isinstance(x, (int, float))]
    return round(sum(xs) / len(xs), 3) if xs else None


def video_satirlari(basliklar, satirlar):
    c = {k: sutun(basliklar, k) for k in ("baslik", "yayin", "gosterim", "to", "izlenme", "ort_sure", "ort_oran", "sure")}
    out, toplam = [], None
    for r in satirlar:
        v = {"baslik": r.get(c["baslik"]) if c["baslik"] else None, "yayin": r.get(c["yayin"]) if c["yayin"] else None,
             "gosterim": sayi(r.get(c["gosterim"])) if c["gosterim"] else None, "to": sayi(r.get(c["to"])) if c["to"] else None,
             "izlenme": sayi(r.get(c["izlenme"])) if c["izlenme"] else None,
             "ort_sure_sn": sure_sn(r.get(c["ort_sure"])) if c["ort_sure"] else None,
             "ort_oran": sayi(r.get(c["ort_oran"])) if c["ort_oran"] else None, "sure_sn": sure_sn(r.get(c["sure"])) if c["sure"] else None}
        if v["ort_oran"] is None and v["ort_sure_sn"] and v["sure_sn"]: v["ort_oran"] = round(100 * v["ort_sure_sn"] / v["sure_sn"], 1)
        if str(v["baslik"] or "").strip().lower() in TOPLAM or str(next(iter(r.values()), "")).strip().lower() in TOPLAM: toplam = v
        elif any(v[k] is not None for k in ("gosterim", "to", "izlenme", "ort_oran")): out.append(v)
    return out, toplam


def video_teshisi(v):
    n = []
    if v.get("gosterim") is not None and v["gosterim"] < GOSTERIM_MIN: n.append("keşif")
    if v.get("to") is not None and v["to"] < TO_MIN: n.append("paketleme")
    if v.get("ort_oran") is not None and v["ort_oran"] < IZLENME_MIN: n.append("film")
    if all(v.get(k) is None for k in ("gosterim", "to", "ort_oran")): return "ölçülemedi"
    return " + ".join(n) or "sorun görünmüyor"


def trafik(basliklar, satirlar):
    c, iz = sutun(basliklar, "trafik"), sutun(basliklar, "izlenme")
    if not c: return None
    out = {r.get(c): sayi(r.get(iz)) if iz else None for r in satirlar if r.get(c) and str(r.get(c)).lower() not in TOPLAM}
    return out or None


def teshis(dosyalar):
    videolar, trafik_k, okunan = [], {}, []
    for p in dosyalar:
        try: b, s = csv_oku(p)
        except OSError: continue
        okunan.append(os.path.basename(p))
        t = trafik(b, s)
        if t: trafik_k.update(t); continue
        v, _ = video_satirlari(b, s); videolar += v
    for v in videolar: v["teshis"] = video_teshisi(v)
    ort = {"to": ortalama(v.get("to") for v in videolar), "ort_oran": ortalama(v.get("ort_oran") for v in videolar),
           "gosterim": ortalama(v.get("gosterim") for v in videolar), "ort_sure_sn": ortalama(v.get("ort_sure_sn") for v in videolar)}
    sayim = {}
    for v in videolar:
        for x in v["teshis"].split(" + "): sayim[x] = sayim.get(x, 0) + 1
    if not videolar: genel = "ölçülemedi"
    else: genel = max((k for k in sayim if k not in ("sorun görünmüyor", "ölçülemedi")), key=sayim.get, default="sorun görünmüyor")
    return {"_surum": 1, "_uretim": {"asama": None, "arac_surum": SURUM, "zaman": simdi(), "sonuc": "BAYRAK" if genel == "ölçülemedi" else "GEC",
                                     "ortam": "yerel" if os.name == "nt" else "bulut"},
            "dosyalar": okunan, "video_sayisi": len(videolar), "kanal_ortalama": ort, "trafik": trafik_k or None,
            "genel_teshis": genel, "sayim": sayim, "videolar": videolar,
            "sinirlar": {"gosterim_min": GOSTERIM_MIN, "to_min": TO_MIN, "izlenme_min": IZLENME_MIN, "kaynak": "tahmin"}}


def md(t):
    s = ["# Kanal teşhisi (Ö0-g)", "", f"Üretildi: {t['_uretim']['zaman']} · kanal_teshis.py CSV kipi · dosyalar: "
         + (", ".join(t["dosyalar"]) or "yok"), ""]
    if t["genel_teshis"] == "ölçülemedi":
        s += ["**Sonuç: ölçülemedi.** YouTube Studio CSV'si yok. İstersen Studio → Analytics → Gelişmiş mod → Dışa aktar (CSV) dosyasını "
              "`GELENLER/KANAL/` klasörüne koy; film bunu beklemez.", ""]
        return "\n".join(s)
    o = t["kanal_ortalama"]
    s += [f"**Genel teşhis: {t['genel_teshis']}** (keşif = gösterim az · paketleme = tıklama oranı düşük · film = izlenme yüzdesi düşük)", "",
          f"- Kanal ortalaması: gösterim {o['gosterim']} · tıklama oranı %{o['to']} · ortalama izlenme %{o['ort_oran']} · "
          f"ortalama izleme {o['ort_sure_sn']} sn", f"- Sınırlar (tahmin): gösterim < {GOSTERIM_MIN}, TO < %{TO_MIN}, izlenme < %{IZLENME_MIN}", ""]
    if t["trafik"]: s += ["## Trafik kaynakları", ""] + [f"- {k}: {v}" for k, v in sorted(t["trafik"].items(), key=lambda x: -(x[1] or 0))] + [""]
    s += ["## Videolar", "", "| Video | Gösterim | TO % | İzlenme % | Teşhis |", "|---|---|---|---|---|"]
    s += [f"| {str(v['baslik'] or '?')[:60]} | {v['gosterim']} | {v['to']} | {v['ort_oran']} | {v['teshis']} |" for v in t["videolar"]]
    s += ["", "Bu teşhis kapak/başlık ve ritim önceliklerini belirler (D-24); yorumu yayin-paketcisi·teshis yazar.", ""]
    return "\n".join(s)


def _metin_yaz(p, m):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8") as f: f.write(m)
    os.replace(p + ".tmp", p)


def main(a):
    if "-h" in a or "--help" in a: print(__doc__); return BITTI
    try:
        y = ortak.yollar(); veri = y["veri_kok"]
        dos = [a[i + 1] for i, x in enumerate(a) if x == "--csv" and i + 1 < len(a)]
        kl = a[a.index("--klasor") + 1] if "--klasor" in a and a.index("--klasor") + 1 < len(a) else os.path.join(veri, "GELENLER", "KANAL")
        if not dos: dos = sorted(glob.glob(os.path.join(kl, "*.csv")))
        t = teshis(dos)
        ortak.atomik_yaz(os.path.join(veri, "BILGI", "KANAL_TESHIS.json"), t)
        _metin_yaz(os.path.join(veri, "BILGI", "KANAL_TESHIS.md"), md(t))
        print(f"Kanal teşhisi: {t['genel_teshis']} ({t['video_sayisi']} video) → BILGI/KANAL_TESHIS.md")
        return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
