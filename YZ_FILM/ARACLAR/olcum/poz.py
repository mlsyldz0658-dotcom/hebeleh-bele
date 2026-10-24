"""ölçüm · poz — MediaPipe Face Landmarker (yaw, jawOpen) ve Pose Landmarker (bilekler → nesne hangi elde) (mediapipe, Apache-2.0).

  from olcum import poz
  poz.hazir() → (bool, neden)
  poz.olc_ekle(yol, beklenen, banka, out)   yaw {id: derece}, jaw_open {id: 0–1}, el_nesne {nesne: {el: sag|sol, guven, karakter}}
Model dosyaları (.task): face_landmarker.task, pose_landmarker_lite.task (model klasöründe; kurulum indirir).
MediaPipe ayna uyarısı (02§4): Pose "left_wrist" kişinin kendi sol bileğidir (görüntüde kameraya dönük kişide sağda). Bu modül kişinin
kendi sol/sağını yazar. mediapipe yoksa yaw yalnız YuNet noktalarından yaklaşık (kimlik.yaw_yaklasik; guven dusuk), jawOpen ve el_nesne
ÖLÇÜLEMEDİ olur.
"""
import os
import numpy as np

YUZ, VUCUT = "face_landmarker.task", "pose_landmarker_lite.task"
_M = {}


def _mp():
    try:
        import mediapipe as mp
        return mp
    except Exception as e: raise RuntimeError(f"mediapipe kurulu değil ({e.__class__.__name__})")


def _yol(ad):
    from olcum import model_klasoru
    return os.path.join(model_klasoru(), ad)


def hazir():
    try: _mp()
    except RuntimeError as e: return False, str(e)
    eksik = [a for a in (YUZ, VUCUT) if not os.path.isfile(_yol(a))]
    return (False, "model dosyası yok: " + ", ".join(eksik)) if eksik else (True, "")


def _yuz_yaw(m):
    """Yüz dönüşüm matrisinden yaw (derece). + = yüz kadrajın sağına dönük (GS0'da doğrulanır)."""
    r = np.asarray(m)[:3, :3]
    return float(np.degrees(np.arctan2(-r[2, 0], np.sqrt(r[2, 1] ** 2 + r[2, 2] ** 2))))


def olc_ekle(yol, beklenen, banka, out):
    ok, neden = hazir()
    yaklasik = out.get("yaw_yaklasik") or {}
    if not ok:
        if yaklasik: out["yaw"] = dict(yaklasik); out["yaw_guven"] = "dusuk"
        else: out["olculemedi"]["yaw"] = neden
        out["olculemedi"]["jaw_open"] = neden; out["olculemedi"]["el_nesne"] = neden
        return
    mp = _mp()
    from mediapipe.tasks import python as mpt
    from mediapipe.tasks.python import vision
    if "yuz" not in _M:
        _M["yuz"] = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
            base_options=mpt.BaseOptions(model_asset_path=_yol(YUZ)), output_face_blendshapes=True,
            output_facial_transformation_matrixes=True, num_faces=6))
        _M["vucut"] = vision.PoseLandmarker.create_from_options(vision.PoseLandmarkerOptions(
            base_options=mpt.BaseOptions(model_asset_path=_yol(VUCUT)), num_poses=6))
    from olcum import teknik
    im = teknik.ac(yol); W, H = im.size
    mi = mp.Image(image_format=mp.ImageFormat.SRGB, data=np.asarray(im))
    r = _M["yuz"].detect(mi)
    yuzler = out.get("yuzler") or []
    es = out.get("eslesme") or {}
    out["yaw"], out["jaw_open"] = {}, {}
    for i, lm in enumerate(r.face_landmarks or []):
        cx = np.mean([p.x for p in lm]) * W
        en = min(range(len(yuzler)), key=lambda j: abs(yuzler[j]["kutu"][0] + yuzler[j]["kutu"][2] / 2 - cx)) if yuzler else None
        kid = es.get(str(en)) if en is not None else None
        if not kid: continue
        out["yaw"][kid] = round(_yuz_yaw(r.facial_transformation_matrixes[i]), 1)
        bs = {b.category_name: b.score for b in (r.face_blendshapes[i] if r.face_blendshapes else [])}
        if "jawOpen" in bs: out["jaw_open"][kid] = round(float(bs["jawOpen"]), 3)
    out["yaw_guven"] = "yuksek"
    nk = out.get("nesne_kutulari") or []
    if not nk:
        out["olculemedi"]["el_nesne"] = "nesne kutusu yok (OWLv2 ölçmedi)"; return
    pr = _M["vucut"].detect(mi)
    bilekler = []
    for p in pr.pose_landmarks or []:
        for el, idx in (("sol", 15), ("sag", 16)):
            bilekler.append((el, p[idx].x * W, p[idx].y * H, np.mean([q.x for q in p]) * W))
    out["el_nesne"] = {}
    for n in beklenen.get("nesneler") or []:
        k = next((d for d in nk if d["sorgu"] == n.get("sorgu")), None)
        if k is None or not bilekler: out["olculemedi"][f"el_nesne:{n.get('id')}"] = "nesne ya da bilek bulunamadı"; continue
        x0, y0, w, h = k["kutu"]; nx, ny = x0 + w / 2, y0 + h / 2
        d = sorted(((np.hypot(bx - nx, by - ny), el, gx) for el, bx, by, gx in bilekler))
        mesafe, el, gx = d[0]
        guven = round(float(max(0.0, 1.0 - mesafe / (0.25 * H))), 2)
        out["el_nesne"][n["id"]] = {"el": el, "guven": guven, "kisi_x": round(float(gx), 1)}
