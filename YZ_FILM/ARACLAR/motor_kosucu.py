"""MOTOR KOŞUCU — ayrı sanal ortamda (KUR2/KUR3) yerel motoru çalıştıran tek giriş noktası (saglayicilar/yerel_ses.py, buyutucu.py).

Kullanım (yalnız sağlayıcı sınıfları çağırır): <ortam python> motor_kosucu.py <motor> <istek.json>
  motor: openvoice | chatterbox | rvc | roformer | demucs | faster_whisper | musetalk | realesrgan
  istek: {"giris", "cikti", …, "yanit": "<yanıt.json>"}; yanıt: {"benzerlik"?, "metin"?, …} ya da {"hata": "..."}
Çıkış: 0 tamam · 1 hata · 3 GPU belleği yetmedi (sağlayıcı Kisitlandi → 8 BEKLE) · 4 motor bu ortamda kurulu değil.
Bu dosya ana ortamdaki araçları import ETMEZ (ayrı ortamda koşar); yalnız stdlib + motorun kendi paketi.
Ağ yok: HF_HUB_OFFLINE=1 ile koşar. Wav2Lip ve lisansı ticari olmayan motorlar burada yoktur ve eklenmez.
Motorların Python API'leri Ö0-c / KUR2 / KUR3'te kullanıcının bilgisayarında doğrulanır; burada yazılı çağrılar bellekten
(doğrulanacak) ve her biri kendi try bloğunda: başarısızlık sessiz geçmez, yanıt "hata" taşır.
"""
import os, sys, json, time


def _yanit(istek, v, kod=0):
    with open(istek["yanit"], "w", encoding="utf-8") as f: json.dump(v, f, ensure_ascii=False)
    return kod


def openvoice(i):
    from openvoice import se_extractor                       # MIT (OpenVoice V2); doğrulanacak
    from openvoice.api import ToneColorConverter
    ckpt = os.environ.get("OPENVOICE_CKPT", "checkpoints_v2/converter")
    t = ToneColorConverter(f"{ckpt}/config.json", device=os.environ.get("YZ_CIHAZ", "cuda"))
    t.load_ckpt(f"{ckpt}/checkpoint.pth")
    src, _ = se_extractor.get_se(i["giris"], t, vad=True)
    tgt, _ = se_extractor.get_se(i["referans"], t, vad=True)
    t.convert(audio_src_path=i["giris"], src_se=src, tgt_se=tgt, output_path=i["cikti"])
    return {}


def chatterbox(i):
    from chatterbox.vc import ChatterboxVC                   # MIT; doğrulanacak
    import torchaudio
    m = ChatterboxVC.from_pretrained(os.environ.get("YZ_CIHAZ", "cuda"))
    w = m.generate(i["giris"], target_voice_path=i["referans"])
    torchaudio.save(i["cikti"], w, m.sr)
    return {}


def rvc(i):
    if i.get("is") == "egit": return {"hata": "RVC eğitimi bu sürümde kullanıcının bilgisayarında elle başlatılır (izinle)"}
    from rvc_python.infer import RVCInference                # MIT; doğrulanacak
    r = RVCInference(device=os.environ.get("YZ_CIHAZ", "cuda:0"))
    r.load_model(i["referans"]); r.set_params(f0up_key=int(i.get("f0_yt") or 0))
    r.infer_file(i["giris"], i["cikti"])
    return {}


def roformer(i, model="model_bs_roformer_ep_317_sdr_12.9755.ckpt"):
    from audio_separator.separator import Separator         # MIT
    s = Separator(output_dir=i["cikti_dir"]); s.load_model(model)
    cikti = s.separate(i["giris"]); ad = i.get("ad") or os.path.splitext(os.path.basename(i["giris"]))[0]
    sonuc = {}
    for p in cikti:
        p = p if os.path.isabs(p) else os.path.join(i["cikti_dir"], p)
        hedef = os.path.join(i["cikti_dir"], f"{ad}_{'konusma' if 'ocals' in p else 'diger'}.wav")
        os.replace(p, hedef); sonuc["konusma" if "ocals" in p else "diger"] = hedef
    return sonuc


def demucs(i): return roformer(i, model="htdemucs_ft.yaml")


def faster_whisper(i):
    from faster_whisper import WhisperModel                 # MIT
    m = WhisperModel(os.environ.get("YZ_ASR_MODEL", "small.en"), device="auto", compute_type="int8")
    seg, _ = m.transcribe(i["giris"], word_timestamps=True, initial_prompt=i.get("bilinen_metin"))
    ks = [{"w": w.word.strip(), "bas": round(w.start, 3), "bit": round(w.end, 3), "guven": round(w.probability, 3)}
          for s in seg for w in (s.words or [])]
    return {"metin": " ".join(k["w"] for k in ks), "kelimeler": ks,
            "guven": round(sum(k["guven"] for k in ks) / len(ks), 3) if ks else 0.0}


def musetalk(i):
    t0 = time.time()
    import subprocess
    kok = os.environ.get("MUSETALK_KOK")
    if not kok: return {"hata": "MUSETALK_KOK yok (KUR3)"}
    r = subprocess.run([sys.executable, "-m", "scripts.inference", "--video_path", i["klip"], "--audio_path", i["ses"],
                        "--result_path", i["cikti"], "--use_float16"], cwd=kok, capture_output=True, text=True)
    if "out of memory" in (r.stderr or "").lower(): raise MemoryError(r.stderr[-200:])
    if r.returncode: return {"hata": (r.stderr or "")[-300:]}
    return {"sure_sn": round(time.time() - t0, 1)}


def realesrgan(i):
    t0 = time.time()
    import subprocess
    exe = os.environ.get("REALESRGAN_EXE")
    if not exe: return {"hata": "REALESRGAN_EXE yok (KUR3)"}
    r = subprocess.run([exe, "-i", i["giris"], "-o", i["cikti"], "-s", str(i.get("olcek", 2))], capture_output=True, text=True)
    if r.returncode: return {"hata": (r.stderr or "")[-300:]}
    return {"sure_sn": round(time.time() - t0, 1)}


MOTORLAR = {"openvoice": openvoice, "chatterbox": chatterbox, "rvc": rvc, "roformer": roformer, "demucs": demucs,
            "faster_whisper": faster_whisper, "musetalk": musetalk, "realesrgan": realesrgan}


def main(argv):
    if len(argv) != 2 or argv[0] not in MOTORLAR: print(__doc__); return 4
    with open(argv[1], encoding="utf-8") as f: istek = json.load(f)
    try: return _yanit(istek, MOTORLAR[argv[0]](istek) or {})
    except ImportError as e: return _yanit(istek, {"hata": f"motor kurulu değil: {e}"}, 4)
    except MemoryError as e: return _yanit(istek, {"hata": "GPU belleği yetmedi", "neden": str(e)[:200]}, 3)
    except Exception as e: return _yanit(istek, {"hata": f"{e.__class__.__name__}: {str(e)[:300]}"}, 1)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
