"""ölçüm · görünüm — DINOv2-small gömmesi, CLIP "photograph" olasılığı, OWLv2 nesne bulucu (torch CPU + transformers; yalnız yerel önbellek).

  from olcum import gorunum
  gorunum.hazir() → (bool, neden)
  gorunum.dinov2(im) → vektör · gorunum.benzerlik(a, b) · gorunum.clip_foto(im) → 0–1 · gorunum.owl(im, ["an iron key"]) → [{sorgu, kutu, skor}]
  gorunum.olc_ekle(yol, beklenen, banka, out)   stil_clip_foto, mekan_dinov2 (kişiler maskeli, ebeveyne), yaratik_dinov2, nesne_kutulari
Modeller ağdan İNDİRİLMEZ (local_files_only, HF_HUB_OFFLINE=1); kurulum KUR1'de bir kez indirir. Yoksa alanlar ÖLÇÜLEMEDİ.
Model kimlikleri (bellekten; lisanslar veri/LISANSLAR.json): facebook/dinov2-small, openai/clip-vit-base-patch32,
google/owlv2-base-patch16-ensemble.
"""
import os
import numpy as np

DINO, CLIP, OWL = "facebook/dinov2-small", "openai/clip-vit-base-patch32", "google/owlv2-base-patch16-ensemble"
KARSI = ["an illustration", "a 3D render", "a plush toy", "a cartoon"]
_M = {}


class GorunumYok(Exception):
    pass


def _kutuphane():
    try:
        import torch, transformers  # noqa: F401
        return torch, transformers
    except Exception as e: raise GorunumYok(f"torch/transformers kurulu değil ({e.__class__.__name__})")


def hazir():
    try: _kutuphane()
    except GorunumYok as e: return False, str(e)
    return True, ""


def _yukle(ad):
    if ad in _M: return _M[ad]
    _, tr = _kutuphane()
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    from olcum import model_klasoru
    kw = {"local_files_only": True, "cache_dir": os.path.join(model_klasoru(), "hf")}
    try:
        if ad == DINO: _M[ad] = (tr.AutoImageProcessor.from_pretrained(ad, **kw), tr.AutoModel.from_pretrained(ad, **kw))
        elif ad == CLIP: _M[ad] = (tr.CLIPProcessor.from_pretrained(ad, **kw), tr.CLIPModel.from_pretrained(ad, **kw))
        else: _M[ad] = (tr.Owlv2Processor.from_pretrained(ad, **kw), tr.Owlv2ForObjectDetection.from_pretrained(ad, **kw))
    except Exception as e: raise GorunumYok(f"{ad} yerel önbellekte yok ({e.__class__.__name__})")
    return _M[ad]


def _im(x):
    from olcum import teknik
    return teknik.ac(x) if isinstance(x, str) else x.convert("RGB")


def dinov2(x):
    torch, _ = _kutuphane(); p, m = _yukle(DINO)
    with torch.no_grad():
        o = m(**p(images=_im(x), return_tensors="pt"))
    return o.last_hidden_state[:, 0].squeeze(0).numpy().astype(np.float64)


def benzerlik(a, b):
    a, b = np.asarray(a, dtype=np.float64), np.asarray(b, dtype=np.float64)
    return float(a.dot(b) / ((np.linalg.norm(a) * np.linalg.norm(b)) or 1.0))


def clip_foto(x):
    torch, _ = _kutuphane(); p, m = _yukle(CLIP)
    with torch.no_grad():
        o = m(**p(text=["a photograph"] + KARSI, images=_im(x), return_tensors="pt", padding=True))
    return float(o.logits_per_image.softmax(-1)[0, 0])


def owl(x, sorgular, esik=0.15):
    torch, _ = _kutuphane(); p, m = _yukle(OWL); im = _im(x)
    with torch.no_grad():
        o = m(**p(text=[list(sorgular)], images=im, return_tensors="pt"))
    W, H = im.size; s = max(W, H)
    r = p.post_process_object_detection(o, threshold=esik, target_sizes=torch.tensor([[s, s]]))[0]
    out = []
    for skor, et, kutu in zip(r["scores"].tolist(), r["labels"].tolist(), r["boxes"].tolist()):
        x0, y0, x1, y1 = kutu
        out.append({"sorgu": sorgular[et], "kutu": [x0, y0, x1 - x0, y1 - y0], "skor": round(skor, 3)})
    return sorted(out, key=lambda d: -d["skor"])


def maskeli(x, kutular, pay=0.35):
    """Kişi/yüz kutularını (genişletilmiş) ortalama gri ile örter: mekân benzerliği kişilerden etkilenmesin."""
    im = _im(x).copy(); a = np.asarray(im).copy(); H, W = a.shape[:2]
    for k in kutular:
        x0, y0, w, h = k
        x0, y0 = int(max(0, x0 - w * pay)), int(max(0, y0 - h * pay))
        x1, y1 = int(min(W, x0 + w * (1 + 2 * pay))), int(min(H, y0 + h * (1 + 2 * pay) + h * 3))
        a[y0:y1, x0:x1] = 128
    from PIL import Image
    return Image.fromarray(a)


def olc_ekle(yol, beklenen, banka, out):
    try: _kutuphane()
    except GorunumYok as e:
        for a in ("stil_clip_foto", "mekan_dinov2", "yaratik_dinov2", "nesne_kutulari"): out["olculemedi"][a] = str(e)
        return
    for alan, fn in (("stil_clip_foto", lambda: round(clip_foto(yol), 4)),):
        try: out[alan] = fn()
        except GorunumYok as e: out["olculemedi"][alan] = str(e)
    eb = beklenen.get("ebeveyn")
    if eb and os.path.isfile(eb):
        try:
            kutular = [y["kutu"] for y in out.get("yuzler") or []]
            out["mekan_dinov2"] = round(benzerlik(dinov2(maskeli(yol, kutular)), dinov2(maskeli(eb, []))), 4)
        except GorunumYok as e: out["olculemedi"]["mekan_dinov2"] = str(e)
    sorgular = [n.get("sorgu") for n in beklenen.get("nesneler") or [] if n.get("sorgu")]
    yaratik = [y for y in beklenen.get("yaratik") or [] if isinstance(y, dict) and y.get("sorgu")]
    if sorgular or yaratik:
        try:
            out["nesne_kutulari"] = owl(yol, sorgular + [y["sorgu"] for y in yaratik])
            from olcum import kimlik
            B = kimlik.banka_oku(banka if banka is not None else beklenen.get("banka"))
            out["yaratik_dinov2"] = {}
            for y in yaratik:
                k = next((d for d in out["nesne_kutulari"] if d["sorgu"] == y["sorgu"]), None)
                vb = B.get("dinov2:" + y["id"])
                if k is None or vb is None:
                    out["olculemedi"][f"yaratik:{y['id']}"] = "kutu bulunamadı" if k is None else "DINOv2 bankası yok"; continue
                x0, y0, w, h = k["kutu"]
                v = dinov2(_im(yol).crop((int(x0), int(y0), int(x0 + w), int(y0 + h))))
                out["yaratik_dinov2"][y["id"]] = round(max(benzerlik(v, b) for b in vb), 4)
        except GorunumYok as e: out["olculemedi"]["nesne_kutulari"] = str(e)
