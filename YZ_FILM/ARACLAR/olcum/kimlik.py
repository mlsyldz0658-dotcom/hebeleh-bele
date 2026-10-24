"""ölçüm · kimlik — YuNet yüz bulucu + SFace kimlik vektörü (opencv FaceDetectorYN / FaceRecognizerSF), kadro bankası, Macar eşlemesi.

  from olcum import kimlik
  kimlik.hazir() → (bool, neden)
  kimlik.yuzler(yol) → [{kutu: [x,y,w,h], skor, noktalar: [[x,y]×5], vektor: [128]}]   (kurulu değilse KimlikYok)
  kimlik.banka_oku(yol_ya_da_sozluk) → {id: np.ndarray (k,128)} · kimlik.banka_yaz(yol, {id: [vektör]})
  kimlik.benzerlik(a, b) → kosinüs · kimlik.esle(yuz_vektorleri, banka) → {yuz_i: (id, benzerlik)}
  kimlik.olc_ekle(yol, beklenen, banka, out)   olc() içinden: yuzler, yuz_sayisi, kimlik, eslesme, kadraj_sirasi, ucte_bir, yaw_yaklasik
Model dosyaları (opencv_zoo; kurulum indirir): face_detection_yunet_2023mar.onnx, face_recognition_sface_2021dec.onnx, model klasöründe.
Görseller cv2.imdecode ile okunur (Windows'ta Türkçe karakterli yol). Yüz skoru < g1_yunet_skor_min ya da yükseklik < g1_yuz_min_px olan
yüz kimlik ölçümüne girmez (o karakter için ÖLÇÜLEMEDİ). Arka plan yüzü (kutu < kare yüksekliğinin g1_arka_yuz_oran_max'ı) sayılmaz.
Yaklaşık yaw (YuNet noktaları): burnun göz ortasına göre yatay kayması; + değer = yüz kadrajın SAĞINA dönük (işaret GS0'da doğrulanır,
KALIBRASYON.json yaw_isareti ile çevrilir). Bu kaynak yalnız BAYRAK verebilir (guven: dusuk).
"""
import os, itertools
import numpy as np

YUNET = "face_detection_yunet_2023mar.onnx"
SFACE = "face_recognition_sface_2021dec.onnx"
_M = {}


class KimlikYok(Exception):
    pass


def _cv2():
    try:
        import cv2
        return cv2
    except Exception as e: raise KimlikYok(f"opencv kurulu değil ({e.__class__.__name__})")


def _yol(ad):
    from olcum import model_klasoru
    return os.path.join(model_klasoru(), ad)


def hazir():
    try:
        cv2 = _cv2()
        if not hasattr(cv2, "FaceDetectorYN"): return False, "opencv sürümünde FaceDetectorYN yok (≥ 4.5.4 gerekli)"
    except KimlikYok as e: return False, str(e)
    eksik = [a for a in (YUNET, SFACE) if not os.path.isfile(_yol(a))]
    if eksik: return False, "model dosyası yok: " + ", ".join(eksik)
    return True, ""


def _modeller():
    ok, neden = hazir()
    if not ok: raise KimlikYok(neden)
    if "det" not in _M:
        cv2 = _cv2()
        _M["det"] = cv2.FaceDetectorYN.create(_yol(YUNET), "", (320, 320), 0.6, 0.3, 50)
        _M["rec"] = cv2.FaceRecognizerSF.create(_yol(SFACE), "")
    return _M["det"], _M["rec"]


def oku(yol):
    cv2 = _cv2()
    img = cv2.imdecode(np.fromfile(yol, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None: raise KimlikYok(f"görsel okunamadı: {os.path.basename(yol)}")
    return img


def yuzler(yol_ya_da_img, vektor=True):
    det, rec = _modeller()
    img = oku(yol_ya_da_img) if isinstance(yol_ya_da_img, str) else yol_ya_da_img
    h, w = img.shape[:2]
    det.setInputSize((w, h))
    _, f = det.detect(img)
    out = []
    for r in (f if f is not None else []):
        y = {"kutu": [float(v) for v in r[:4]], "skor": round(float(r[14]), 4),
             "noktalar": [[float(r[4 + 2 * i]), float(r[5 + 2 * i])] for i in range(5)]}
        if vektor:
            hiz = rec.alignCrop(img, r)
            y["vektor"] = [float(v) for v in rec.feature(hiz).ravel()]
        out.append(y)
    return sorted(out, key=lambda y: y["kutu"][0])


def benzerlik(a, b):
    a, b = np.asarray(a, dtype=np.float64).ravel(), np.asarray(b, dtype=np.float64).ravel()
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(a.dot(b) / (na * nb)) if na and nb else 0.0


def banka_oku(b):
    if b is None: return {}
    if isinstance(b, str):
        if not os.path.isfile(b): return {}
        with np.load(b) as z: return {k: np.atleast_2d(z[k]) for k in z.files}
    out = {}
    for k, v in b.items():
        if isinstance(v, str): out.update({k: x for k, x in banka_oku(v).items()} if v.endswith(".npz") else {})
        else: out[k] = np.atleast_2d(np.asarray(v, dtype=np.float64))
    return out


def banka_yaz(yol, sozluk):
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    tmp = yol + ".tmp.npz"
    np.savez(tmp, **{k: np.atleast_2d(np.asarray(v, dtype=np.float32)) for k, v in sozluk.items() if len(v)})
    os.replace(tmp, yol)


def bankaya_benzerlik(vektor, banka_kaydi):
    return max(benzerlik(vektor, v) for v in banka_kaydi) if len(banka_kaydi) else 0.0


def macar(maliyet):
    """Kare olmayan maliyet matrisi için en düşük toplamlı atama [(satir, sutun)]. scipy varsa o; yoksa küçük boyutta tam arama."""
    m = np.asarray(maliyet, dtype=np.float64)
    if m.size == 0: return []
    try:
        from scipy.optimize import linear_sum_assignment
        r, c = linear_sum_assignment(m); return list(zip(r.tolist(), c.tolist()))
    except Exception: pass
    n, k = m.shape
    if min(n, k) > 7:                                          # büyük kadroda açgözlü (gerçek filmde kadrajda ≤ 4 yüz)
        out, kul_r, kul_c = [], set(), set()
        for i, j in sorted(itertools.product(range(n), range(k)), key=lambda t: m[t]):
            if i in kul_r or j in kul_c: continue
            out.append((i, j)); kul_r.add(i); kul_c.add(j)
        return sorted(out)
    en, en_t = None, float("inf")
    if n <= k:
        for p in itertools.permutations(range(k), n):
            t = sum(m[i, p[i]] for i in range(n))
            if t < en_t: en, en_t = [(i, p[i]) for i in range(n)], t
    else:
        for p in itertools.permutations(range(n), k):
            t = sum(m[p[j], j] for j in range(k))
            if t < en_t: en, en_t = sorted((p[j], j) for j in range(k)), t
    return en


def esle(vektorler, banka, adaylar=None):
    """Yüz vektörlerini kadro bankasına bire bir eşler (benzerlik en yüksek toplam). {yuz_i: (id, benzerlik)}."""
    ids = [i for i in (adaylar or banka.keys()) if i in banka]
    if not vektorler or not ids: return {}
    s = np.array([[bankaya_benzerlik(v, banka[i]) for i in ids] for v in vektorler])
    return {r: (ids[c], float(s[r, c])) for r, c in macar(1.0 - s)}


def yaw_yaklasik(noktalar):
    (rx, ry), (lx, ly), (nx, ny) = noktalar[0], noktalar[1], noktalar[2]
    goz = abs(lx - rx) or 1.0
    d = (nx - (rx + lx) / 2.0) / goz
    return round(float(np.degrees(np.arcsin(max(-1.0, min(1.0, d * 1.6))))), 1)


def olc_ekle(yol, beklenen, banka, out):
    from olcum import esik, ucte_bir
    try: ys = yuzler(yol)
    except KimlikYok as e:
        for a in ("yuz_sayisi", "kimlik", "kadraj_sirasi", "ucte_bir"): out["olculemedi"][a] = str(e)
        return
    W, H = out["teknik"]["genislik"], out["teknik"]["yukseklik"]
    arka = esik("g1_arka_yuz_oran_max") * H
    on = [y for y in ys if y["kutu"][3] >= arka]
    out["yuzler"] = [{k: v for k, v in y.items() if k != "vektor"} for y in on]
    out["yuz_sayisi"] = len(on); out["arka_plan_yuz"] = len(ys) - len(on)
    olculur = [i for i, y in enumerate(on) if y["skor"] >= esik("g1_yunet_skor_min") and y["kutu"][3] >= esik("g1_yuz_min_px")]
    B = banka_oku(banka if banka is not None else beklenen.get("banka"))
    insan = [i for i in (beklenen.get("insan") or beklenen.get("karakterler") or []) if i in B]
    out["kimlik"], out["eslesme"], out["ucte_bir"], out["yaw_yaklasik"] = {}, {}, {}, {}
    if not B:
        out["olculemedi"]["kimlik"] = "kimlik bankası yok (kart kilitlenmemiş ya da banka_vN.npz eksik)"
    else:
        es = esle([on[i]["vektor"] for i in olculur], B, adaylar=list(B.keys()))
        for r, (kid, sim) in es.items():
            y = on[olculur[r]]
            if kid not in insan and insan and sim < esik("g1_kimlik_hata"): continue
            obur = [bankaya_benzerlik(y["vektor"], B[o]) for o in B if o != kid]
            out["kimlik"][kid] = {"benzerlik": round(sim, 4), "fark_payi": round(sim - (max(obur) if obur else 0.0), 4),
                                  "yuz": olculur[r]}
            out["eslesme"][str(olculur[r])] = kid
            out["ucte_bir"][kid] = ucte_bir(y["kutu"][0] + y["kutu"][2] / 2.0, W)
            out["yaw_yaklasik"][kid] = yaw_yaklasik(y["noktalar"])
            out.setdefault("yuz_orani", {})[kid] = round(y["kutu"][3] / float(H), 4)
        for kid in insan:
            if kid not in out["kimlik"]:
                out["olculemedi"][f"kimlik:{kid}"] = "yüz bulunamadı ya da skor/boy ölçüm sınırının altında"
    sira = sorted(((on[int(i)]["kutu"][0], k) for i, k in out["eslesme"].items()))
    out["kadraj_sirasi"] = [k for _, k in sira]
