"""ORTAK — araçların paylaştığı küçük yardımcılar (PR-0 asgari sürümü; PR-1'de yollar() ile genişler).

  sahneler_oku(kok)    SAHNELER.json'u okur; "_surum" ≥ 2 ise v1 araç onu işlemez, 4 ile çıkar ("Memmet v2 gerekli")
  atomik_yaz(yol, v)   JSON'u önce .tmp'ye yazıp yerine koyar (yarım dosya kalmaz; Windows'ta kilitliyse 3 kez dener)
  json_oku(yol, vars)  yoksa ya da bozuksa varsayılanı döndürür
"""
import os, sys, json, time

SURUM_CIKIS = 4   # ortam/sürüm uyuşmazlığı: bu araç bu dosyayı işleyemez


def sahneler_oku(kok, arac="bu araç"):
    p = os.path.join(kok, "SAHNELER.json")
    with open(p, encoding="utf-8-sig") as f: plan = json.load(f)
    if isinstance(plan, dict) and int(plan.get("_surum", 1) or 1) >= 2:
        print(f"!! SAHNELER.json sürüm {plan['_surum']} (v2). {arac} v1 dosyası bekliyor; işlem yapılmadı. "
              "Memmet v2 / film.py v2 gerekli.", flush=True)
        sys.exit(SURUM_CIKIS)
    return plan


def atomik_yaz(yol, veri):
    os.makedirs(os.path.dirname(os.path.abspath(yol)), exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=1); f.flush(); os.fsync(f.fileno())
    for deneme in range(3):
        try: os.replace(tmp, yol); return
        except PermissionError:
            if deneme == 2: raise
            time.sleep(0.2)


def json_oku(yol, varsayilan=None):
    try:
        with open(yol, encoding="utf-8-sig") as f: return json.load(f)
    except (OSError, ValueError): return varsayilan
