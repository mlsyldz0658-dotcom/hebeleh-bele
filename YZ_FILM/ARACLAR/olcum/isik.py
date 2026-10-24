"""ölçüm · ışık — Lab ortalaması, ΔE (CIE76), yanak parlaklık oranından ışığın kadrajdaki yönü (numpy; her ortamda).

  from olcum import isik
  isik.olc(yol) → {lab: [L, a, b], parlaklik}
  isik.delta_e(yol_a, yol_b) → ortalama renkler arası ΔE
  isik.yuz_isigi_ekle(yol, olcum_sozlugu)   yüz kutusu ve noktaları varsa yanak oranı + isik_yon ("soldan" | "sagdan" | "duz")
Yön kuralı (02§6.2): yanak parlaklık oranı > g1_isik_yanak_oran_min olan taraf ışığın geldiği taraftır. Kadraj sözüyle yazılır (görüntünün solu
= "soldan"); karakterin kendi sağı/solu değildir.
"""
import numpy as np
from olcum import teknik


def _lin(c):
    c = c / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def rgb_lab(rgb):
    """rgb: (..., 3) 0–255 → Lab (D65)."""
    r, g, b = [_lin(rgb[..., i].astype(np.float64)) for i in range(3)]
    x = (0.4124 * r + 0.3576 * g + 0.1805 * b) / 0.95047
    y = (0.2126 * r + 0.7152 * g + 0.0722 * b) / 1.0
    z = (0.0193 * r + 0.1192 * g + 0.9505 * b) / 1.08883
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116.0)
    fx, fy, fz = f(x), f(y), f(z)
    return np.stack([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)], -1)


def ortalama_lab(yol):
    im = teknik.ac(yol); im.thumbnail((320, 320))
    lab = rgb_lab(np.asarray(im, dtype=np.float64))
    return [round(float(v), 2) for v in lab.reshape(-1, 3).mean(0)]


def delta_e(a, b):
    la, lb = (np.array(ortalama_lab(x)) if isinstance(x, str) else np.array(x) for x in (a, b))
    return float(np.sqrt(((la - lb) ** 2).sum()))


def olc(yol):
    lab = ortalama_lab(yol)
    return {"lab": lab, "parlaklik_L": lab[0]}


def yanak_orani(yol, kutu, noktalar=None):
    """kutu [x, y, w, h]; noktalar YuNet sırası (sağ göz, sol göz, burun, ağız sağ, ağız sol; görüntü koordinatı). Dönüş (sol/sag oranı)."""
    g = teknik.gri(teknik.ac(yol), 100000)
    x, y, w, h = [int(round(v)) for v in kutu[:4]]
    H, W = g.shape
    y0, y1 = max(0, y + int(h * 0.45)), min(H, y + int(h * 0.75))
    if noktalar and len(noktalar) >= 3:
        cx = int(noktalar[2][0])
    else: cx = x + w // 2
    sol = g[y0:y1, max(0, x + int(w * 0.1)):max(1, cx - int(w * 0.05))]
    sag = g[y0:y1, min(W - 1, cx + int(w * 0.05)):min(W, x + int(w * 0.9))]
    if sol.size < 4 or sag.size < 4: return None
    return float(sol.mean() + 1.0) / float(sag.mean() + 1.0)


def yuz_isigi_ekle(yol, out):
    from olcum import esik
    yuzler = out.get("yuzler") or []
    if not yuzler:
        out["olculemedi"].setdefault("isik_yon", "yüz yok (yanak oranı ölçülemez)"); return
    en = max(yuzler, key=lambda f: f["kutu"][3])
    r = yanak_orani(yol, en["kutu"], en.get("noktalar"))
    if r is None: out["olculemedi"].setdefault("isik_yon", "yanak bölgesi çok küçük"); return
    e = esik("g1_isik_yanak_oran_min")
    out["isik"] = dict(out.get("isik") or {}, yanak_orani=round(r, 3),
                       isik_yon="soldan" if r > e else ("sagdan" if r < 1.0 / e else "duz"))
