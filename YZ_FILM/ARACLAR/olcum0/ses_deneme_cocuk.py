"""SES DENEME ÇOCUK — Ö0-c'nin ayrı ortamda koşan parçası (motor_kosucu.py'de olmayan motorlar; şimdilik ACE-Step 1.5 ipucu süresi).

Kullanım (yalnız ses_deneme.py çağırır): <geçici ortam python> ses_deneme_cocuk.py acestep <istek.json>
  istek: {"istem_en", "sure_sn", "cikti", "yanit"}; yanıt: {"sure_sn"} ya da {"hata"}
Çıkış: 0 tamam · 1 hata · 3 GPU belleği yetmedi · 4 motor kurulu değil. Ana ortamın araçlarını import ETMEZ (yalnız stdlib + motor paketi).
ACE-Step Python API'si bellekten yazıldı (v1 `ACEStepPipeline`; 1.5'te ad değişmiş olabilir): Ö0-c'de kullanıcının bilgisayarında doğrulanır;
başarısızlık sessiz geçmez, yanıt "hata" taşır ve O0c.json'da "çalışmadı" yazılır.
"""
import os, sys, json, time


def _yanit(i, v, kod=0):
    with open(i["yanit"], "w", encoding="utf-8") as f: json.dump(v, f, ensure_ascii=False)
    return kod


def acestep(i):
    t0 = time.time()
    try:
        from acestep.pipeline_ace_step import ACEStepPipeline           # bellekten; doğrulanacak
    except ImportError:
        from acestep.pipeline import ACEStepPipeline                     # olası 1.5 yolu (bellekten)
    p = ACEStepPipeline(checkpoint_dir=os.environ.get("ACESTEP_CKPT") or None, dtype="bfloat16", cpu_offload=True, overlapped_decode=True)
    p(audio_duration=float(i.get("sure_sn") or 30), prompt=i.get("istem_en") or "", lyrics="[instrumental]", infer_step=27,
      save_path=i["cikti"])
    return {"sure_sn": round(time.time() - t0, 1)}


MOTORLAR = {"acestep": acestep}


def main(argv):
    if len(argv) != 2 or argv[0] not in MOTORLAR: print(__doc__); return 4
    with open(argv[1], encoding="utf-8") as f: istek = json.load(f)
    try: return _yanit(istek, MOTORLAR[argv[0]](istek) or {})
    except ImportError as e: return _yanit(istek, {"hata": f"motor kurulu değil: {e}"}, 4)
    except MemoryError as e: return _yanit(istek, {"hata": "GPU belleği yetmedi", "neden": str(e)[:200]}, 3)
    except Exception as e:
        if "out of memory" in str(e).lower(): return _yanit(istek, {"hata": "GPU belleği yetmedi", "neden": str(e)[:200]}, 3)
        return _yanit(istek, {"hata": f"{e.__class__.__name__}: {str(e)[:300]}"}, 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
