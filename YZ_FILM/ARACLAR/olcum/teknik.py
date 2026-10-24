"""ölçüm · teknik — en-boy, çözünürlük, keskinlik (Laplacian varyansı), parlaklık (PIL + numpy; her ortamda çalışır).

  from olcum import teknik
  teknik.olc(yol) → {genislik, yukseklik, en_boy, en_boy_16_9_sapma, kisa_kenar, uzun_kenar, keskinlik, parlaklik}
  teknik.keskinlik(dizi) · teknik.gri(yol, uzun=1280)
Keskinlik ölçek bağımsız olsun diye görsel uzun kenarı 1280 px'e indirilerek hesaplanır; karar parti medyanına oranla verilir.
"""
import numpy as np
from PIL import Image

HEDEF = 16 / 9


def ac(yol):
    im = Image.open(yol); im.load()
    return im.convert("RGB")


def gri(yol_ya_da_im, uzun=1280):
    im = ac(yol_ya_da_im) if isinstance(yol_ya_da_im, str) else yol_ya_da_im.convert("RGB")
    w, h = im.size; s = min(1.0, float(uzun) / max(w, h))
    if s < 1.0: im = im.resize((max(1, int(w * s)), max(1, int(h * s))), Image.BILINEAR)
    return np.asarray(im.convert("L"), dtype=np.float64)


def keskinlik(g):
    """4-komşu Laplacian'ın varyansı (OpenCV cv2.Laplacian(..., CV_64F).var() ile aynı çekirdek)."""
    if g.shape[0] < 3 or g.shape[1] < 3: return 0.0
    lap = (g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:] - 4 * g[1:-1, 1:-1])
    return float(lap.var())


def olc(yol):
    im = ac(yol); w, h = im.size
    g = gri(im)
    oran = w / float(h or 1)
    return {"genislik": w, "yukseklik": h, "en_boy": round(oran, 4), "en_boy_16_9_sapma": round(abs(oran - HEDEF) / HEDEF, 4),
            "kisa_kenar": min(w, h), "uzun_kenar": max(w, h), "keskinlik": round(keskinlik(g), 2),
            "parlaklik": round(float(g.mean()), 2)}


def kenar_std(yol, serit=0.04):
    """Kenar şeridinin (fon) gri standart sapması: kart fonunun düzlüğü."""
    g = gri(yol, 800); h, w = g.shape; s = max(2, int(min(h, w) * serit))
    kenar = np.concatenate([g[:s].ravel(), g[-s:].ravel(), g[:, :s].ravel(), g[:, -s:].ravel()])
    return round(float(kenar.std()), 2)


def medyan(degerler):
    d = sorted(x for x in degerler if isinstance(x, (int, float)))
    if not d: return None
    n = len(d); return d[n // 2] if n % 2 else (d[n // 2 - 1] + d[n // 2]) / 2.0
