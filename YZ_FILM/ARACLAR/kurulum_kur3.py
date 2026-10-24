"""KUR3 — MuseTalk, ACE-Step ve yapay zekâ büyütücüsünün ayrı ortam kurulum planı (TASARIM D-37, §6.9 `kurulum.py --kur3`, §8.2 adım 7).

Kodda (kurulum.py --kur3 bunu çağırır):
  import kurulum_kur3 as k3
  plan = k3.kur3_plani(gerekenler=None)        → {"kademe": "KUR3", "ortamlar": [...], "kart": [...]}  (yalnız okur; bir şey kurmaz)
  k3.kur3_kur(plan, calistir=False)            → komut listesi; calistir=True yalnız Windows'ta ve kullanıcının izin penceresiyle koşar
Komut satırı: python kurulum_kur3.py [--json] [--gerekenler musetalk,buyutme]
Kurallar: KUR3 "yalnız gerektiğinde" kurulur (eksik kademe yalnız kendi basamağını kapatır: tts_dudak, ACE-Step müziği, 2× büyütme).
Modeller bir kez indirilir, sonra HF_HUB_OFFLINE=1. Lisansı "bilinmiyor" olan bileşen yalnız --deneme ile (veri/LISANSLAR.json).
Wav2Lip ve ticari olmayan modeller planda yoktur. Ortam yolları YOLLAR.json "ortamlar" anahtarına yazılır (kurulum.py yazar).
"""
import os, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

ORTAMLAR = {
    "musetalk": {"python": "3.10", "torch": "2.0.1+cu118", "paketler": ["torch==2.0.1", "torchvision==0.15.2", "torchaudio==2.0.2",
                 "diffusers==0.30.2", "accelerate==0.28.0", "opencv-python", "soundfile", "librosa"],
                 "kaynak": "https://github.com/TMElyralab/MuseTalk (1.5)", "kod_lisansi": "MIT", "agirlik_lisansi": "any purpose (model kartı; doğrulanacak)",
                 "basamak": "tts_dudak (ses merdiveni; B planı)", "gpu": "4 GB, fp16 (README: RTX 3050 Ti Laptop 4GB)", "cevre": ["MUSETALK_KOK"]},
    "acestep": {"python": "3.11", "torch": "2.4+cu121", "paketler": ["ace-step"], "kaynak": "https://github.com/ace-step/ACE-Step (1.5)",
                "kod_lisansi": "MIT", "agirlik_lisansi": "doğrulanacak (ağırlık sayfası)", "basamak": "muzik --uret zinciri: acestep", "gpu": "≥ 4 GB",
                "cevre": []},
    "buyutme": {"python": "3.10", "torch": None, "paketler": [], "ikili": "realesrgan-ncnn-vulkan (Real-ESRGAN, BSD-3)",
                "kaynak": "https://github.com/xinntao/Real-ESRGAN", "kod_lisansi": "BSD-3-Clause", "agirlik_lisansi": "doğrulanacak",
                "basamak": "buyut.py yz_buyutucu (yoksa Lanczos + gren)", "gpu": "Vulkan", "cevre": ["REALESRGAN_EXE"]},
}


def ortam_yolu(ad, y=None):
    y = y or ortak.yollar(); return (y.get("ortamlar") or {}).get(ad)


def kur3_plani(gerekenler=None):
    try: y = ortak.yollar()
    except ortak.YolYok: y = ortak.varsayilan_yollar()
    kok = os.path.join(y.get("onbellek") or os.path.expanduser("~"), "ortamlar")
    out = {"kademe": "KUR3", "ortamlar": [], "kart": []}
    for ad, o in ORTAMLAR.items():
        if gerekenler and ad not in gerekenler: continue
        mevcut = ortam_yolu(ad, y); hazir = bool(mevcut and os.path.exists(mevcut))
        out["ortamlar"].append(dict(o, ad=ad, hedef=mevcut or os.path.join(kok, f"venv_{ad}"), hazir=hazir))
        out["kart"].append(f"{ad}: {'çalışıyor' if hazir else 'çalışmıyor'} — {o['basamak']}" + ("" if hazir else " (kapalı; hat sürer)"))
    return out


def kur3_kur(plan, calistir=False):
    """Kurulum komutları. calistir=True yalnız Windows'ta (py başlatıcısı) ve kurulum.py'nin izin penceresinden sonra."""
    komutlar = []
    for o in plan["ortamlar"]:
        if o["hazir"]: continue
        hedef = o["hedef"]
        if o.get("ikili"):
            komutlar.append({"ortam": o["ad"], "not": f"{o['ikili']} indirilir ve {hedef} altına açılır; REALESRGAN_EXE yazılır"}); continue
        py = ["py", f"-{o['python']}"] if os.name == "nt" else [f"python{o['python']}"]
        pip = os.path.join(hedef, "Scripts" if os.name == "nt" else "bin", "python")
        komutlar.append({"ortam": o["ad"], "komut": py + ["-m", "venv", hedef]})
        komutlar.append({"ortam": o["ad"], "komut": [pip, "-m", "pip", "install"] + o["paketler"]})
    if calistir:
        if os.name != "nt": raise RuntimeError("KUR3 kurulumu yalnız kullanıcının Windows bilgisayarında koşar (D-12)")
        import subprocess
        for k in komutlar:
            if "komut" in k: subprocess.run(k["komut"], check=True)
    return komutlar


def main(argv):
    g = None
    if "--gerekenler" in argv: g = set(argv[argv.index("--gerekenler") + 1].split(","))
    p = kur3_plani(g)
    if "--json" in argv: print(json.dumps(dict(p, komutlar=kur3_kur(p)), ensure_ascii=False, indent=1)); return 0
    print("KUR3 (yalnız gerektiğinde):"); [print("  " + k) for k in p["kart"]]
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
