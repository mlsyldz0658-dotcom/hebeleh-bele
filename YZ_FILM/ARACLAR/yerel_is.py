"""YEREL İŞ — yerel ağır iş kuyruğu ve GPU kilidi (TASARIM §6.1; UM2 §4.5.15, İ-9).

Kullanım:
  python yerel_is.py ekle --komut "<araç.py> <seçenekler>" [--film <film>] [--gpu] [--oncelik 1-4] [--ortam ana|ses_donustur|musetalk|…]
                          [--neden blok_arasi_zincir] [--id YI-142-V2]
        işi <veri>/YEREL_IS/kuyruk.jsonl'a ekler (aynı kimlik ikinci kez eklenmez). Öncelik: 1 blok arası zincir işi > 2 V2/V3 > 3 ses >
        4 müzik/dudak. Komut ARACLAR altındaki bir araçtır; film verilirse "--film <film>" eklenir.
  python yerel_is.py calis [--en-cok N] [--film <film>]
        bekleyen işleri öncelik sırasıyla koşar: aynı anda TEK GPU işi (<veri>/YEREL_IS/GPU.kilit, süreçler arası), CPU işleri paralel
        (en çok çekirdek − 2). Bellek hatasıyla (CUDA out of memory / MemoryError) düşen iş BİR kez yeniden denenir; yine düşerse
        ÖLÇÜLEMEDİ olur ve ders kaydı (kategori gpu_bellek) yazılır. Ağır modeller ayrı sanal ortamlarda koşar (YOLLAR.json → ortamlar);
        ortamı kurulu değilse iş ÖLÇÜLEMEDİ (ana Python 3.10 ortamı bozulmaz).
  python yerel_is.py durum [--json]
Kodda: import yerel_is; yerel_is.ekle(film, "video_denetim.py --klip 142", gpu=True, oncelik=2) · yerel_is.calis() · yerel_is.durum()
Defter yalnız eklenir (satır başına fsync); bir işin durumu son satırıdır: bekliyor · calisiyor · tamam · hata · olculemedi.
Kesilen (calisiyor kalmış) iş bir sonraki calis'ta yeniden bekliyor sayılır (kredisiz yerel iş; kredili iş bu kuyruğa girmez).
Çıkış kodları: 0 tamam · 1 en az bir iş hata · 4 kullanım · 8 GPU kilidi başka süreçte (bekle).
"""
import os, sys, re, json, time, shlex, hashlib, subprocess
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "yerel_is 1.0"
DURUMLAR = ("bekliyor", "calisiyor", "tamam", "hata", "olculemedi")
OOM = re.compile(r"CUDA out of memory|OutOfMemoryError|MemoryError|CUBLAS_STATUS_ALLOC_FAILED|cudaErrorMemoryAllocation", re.I)
GPU_KILIT_BAYAT_SN = 6 * 3600       # tek GPU işi en çok 6 sa (MuseTalk uzun kuyruk; tahmin)
OOM_DENEME_MAX = 2                  # ilk + bir yeniden


def klasor():
    d = os.path.join(ortak.yollar()["veri_kok"], "YEREL_IS"); os.makedirs(d, exist_ok=True); return d


def defter_yolu(): return os.path.join(klasor(), "kuyruk.jsonl")
def gpu_kilit_yolu(): return os.path.join(klasor(), "GPU.kilit")


def _ekle_satir(k):
    with open(defter_yolu(), "a", encoding="utf-8") as f:
        f.write(json.dumps(k, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())


def isler():
    """{id: son durum}. Yarım son satır atlanır."""
    out = {}
    p = defter_yolu()
    if not os.path.exists(p): return out
    for s in open(p, encoding="utf-8", errors="replace"):
        try: k = json.loads(s)
        except ValueError: continue
        if isinstance(k, dict) and k.get("id"): out[k["id"]] = dict(out.get(k["id"], {}), **k)
    return out


def _durum_yaz(j, **k):
    j = dict(j, **k, zaman=time.strftime("%Y-%m-%d %H:%M:%S")); _ekle_satir(j); return j


def ekle(film, komut, gpu=False, oncelik=2, ortam="ana", neden=None, kimlik=None):
    arac = shlex.split(komut)[0] if komut else ""
    if not arac.endswith(".py"): raise ValueError("komut ARACLAR altındaki bir .py aracıyla başlamalı")
    kimlik = kimlik or "YI-" + hashlib.sha1(json.dumps([film, komut]).encode("utf-8")).hexdigest()[:8]
    mevcut = isler().get(kimlik)
    if mevcut and mevcut.get("durum") in ("bekliyor", "calisiyor"): return mevcut
    j = {"id": kimlik, "film": film, "komut": komut, "ortam": ortam or "ana", "gpu": bool(gpu), "oncelik": int(oncelik),
         "durum": "bekliyor", "deneme": 0, "neden": neden, "eklendi": time.strftime("%Y-%m-%d %H:%M:%S")}
    return _durum_yaz(j)


def python_bul(ortam):
    """Ortamın Python'u (YOLLAR.json). ana → bu süreç; bilinmeyen/kurulu olmayan → None."""
    if ortam in (None, "", "ana"): return sys.executable
    Y = ortak.yollar(); v = (Y.get("ortamlar") or {}).get(ortam) or (Y.get("python") or {}).get(ortam)
    if not v: return None
    if os.path.isdir(v):
        for a in (os.path.join(v, "Scripts", "python.exe"), os.path.join(v, "bin", "python")):
            if os.path.exists(a): return a
        return None
    return v if os.path.exists(v) else None


def _pid_yasiyor(pid): return ortak.pid_yasiyor(pid)


def gpu_kilidi_al(is_id):
    p = gpu_kilit_yolu()
    for _ in range(2):
        try:
            fd = os.open(p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            with os.fdopen(fd, "w", encoding="utf-8") as f: json.dump({"pid": os.getpid(), "is": is_id, "zaman": time.time()}, f)
            return True
        except FileExistsError:
            k = ortak.json_oku(p, {}) or {}
            pid = k.get("pid"); yas = time.time() - float(k.get("zaman") or 0)
            if not isinstance(pid, int) or (pid != os.getpid() and not _pid_yasiyor(pid)) or yas > GPU_KILIT_BAYAT_SN:
                try: os.remove(p)
                except OSError: pass
                continue
            return False
    return False


def gpu_kilidi_birak():
    p = gpu_kilit_yolu()
    try:
        if (ortak.json_oku(p, {}) or {}).get("pid") == os.getpid(): os.remove(p)
    except OSError: pass


def _komut(j):
    py = python_bul(j.get("ortam"))
    if not py: return None
    arg = shlex.split(j["komut"], posix=(os.name != "nt"))
    arg[0] = os.path.join(HERE, arg[0])
    if j.get("film") and "--film" not in arg: arg += ["--film", j["film"]]
    return [py] + arg


def _ders(j, cikti):
    try:
        import ders_defteri
        ders_defteri.kaydet("arac_hatasi", kaynak="kapi", belirti=f"GPU bellek hatası: {j['komut']} iki kez düştü (ÖLÇÜLEMEDİ)",
                            film=os.path.basename(j.get("film") or "") or None, kategori="gpu_bellek", kanit=[cikti[-300:]],
                            eylem="olculemedi")
    except Exception: pass


def _bitti(j, rc, cikti):
    if rc == 0: return _durum_yaz(j, durum="tamam", cikis=0)
    if OOM.search(cikti or ""):
        if j["deneme"] < OOM_DENEME_MAX: return _durum_yaz(j, durum="bekliyor", cikis=rc, son_hata="gpu_bellek")
        _ders(j, cikti); return _durum_yaz(j, durum="olculemedi", cikis=rc, neden_son="gpu_bellek (iki kez)")
    return _durum_yaz(j, durum="hata", cikis=rc, son_hata=(cikti or "")[-300:])


def calis(en_cok=None, film=None, kosucu=None, bekle_sn=0.2):
    """Bekleyenleri koşar. kosucu(cmd) → Popen benzeri (testler). (tamam, hata, olculemedi) sayıları."""
    kosucu = kosucu or (lambda cmd: subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                                    encoding="utf-8", errors="replace"))
    cpu_max = max(1, (os.cpu_count() or 2) - 2)
    for j in isler().values():                                        # kesilmiş iş: yeniden bekliyor
        if j.get("durum") == "calisiyor": _durum_yaz(j, durum="bekliyor", not_="kesilmişti")
    yapilan, sayac, kosan, gpu_tutuldu = 0, {"tamam": 0, "hata": 0, "olculemedi": 0}, {}, False
    gpu_mesgul = False
    while True:
        bek = sorted((j for j in isler().values() if j.get("durum") == "bekliyor" and (not film or j.get("film") == film)
                      and j["id"] not in kosan), key=lambda j: (j.get("oncelik", 2), j.get("eklendi", "")))
        basladi = False
        for j in bek:
            if en_cok is not None and yapilan >= en_cok: break
            gpu_kosuyor = any(x[0].get("gpu") for x in kosan.values())
            if j.get("gpu"):
                if gpu_kosuyor or gpu_mesgul: continue
                if not gpu_kilidi_al(j["id"]): gpu_mesgul = True; continue
                gpu_tutuldu = True
            elif sum(1 for x in kosan.values() if not x[0].get("gpu")) >= cpu_max: continue
            cmd = _komut(j)
            if cmd is None:
                _durum_yaz(j, durum="olculemedi", neden_son=f"ortam kurulu değil: {j.get('ortam')} (KUR2/KUR3)"); sayac["olculemedi"] += 1
                if j.get("gpu"): gpu_kilidi_birak(); gpu_tutuldu = False
                continue
            j = _durum_yaz(j, durum="calisiyor", deneme=int(j.get("deneme") or 0) + 1)
            kosan[j["id"]] = (j, kosucu(cmd)); yapilan += 1; basladi = True
        if not kosan and not basladi:
            if gpu_tutuldu: gpu_kilidi_birak()
            break
        for k, (j, p) in list(kosan.items()):
            if p.poll() is None: continue
            cikti = p.communicate()[0] if hasattr(p, "communicate") else ""
            j2 = _bitti(j, p.returncode, cikti or ""); del kosan[k]
            if j.get("gpu"): gpu_kilidi_birak(); gpu_tutuldu = False
            if j2["durum"] in sayac: sayac[j2["durum"]] += 1
        if kosan: time.sleep(bekle_sn)
    sayac["gpu_mesgul"] = gpu_mesgul
    return sayac


def durum():
    I = isler(); ozet = {d: 0 for d in DURUMLAR}
    for j in I.values(): ozet[j.get("durum", "bekliyor")] = ozet.get(j.get("durum", "bekliyor"), 0) + 1
    return {"ozet": ozet, "gpu_kilidi": ortak.json_oku(gpu_kilit_yolu(), None), "isler": list(I.values())}


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    def deger(k, v=None): return argv[argv.index(k) + 1] if k in argv and argv.index(k) + 1 < len(argv) else v
    k = argv[0]
    if k == "ekle":
        if not deger("--komut"): print("--komut gerekli"); return 4
        try: j = ekle(deger("--film"), deger("--komut"), gpu="--gpu" in argv, oncelik=int(deger("--oncelik", 2)), ortam=deger("--ortam", "ana"),
                      neden=deger("--neden"), kimlik=deger("--id"))
        except ValueError as e: print(e); return 4
        print(json.dumps(j, ensure_ascii=False)); return 0
    if k == "calis":
        s = calis(en_cok=int(deger("--en-cok")) if deger("--en-cok") else None, film=deger("--film"))
        print(json.dumps(s, ensure_ascii=False))
        return 1 if s["hata"] else (8 if s.get("gpu_mesgul") else 0)
    if k == "durum":
        d = durum(); print(json.dumps(d if "--json" in argv else d["ozet"], ensure_ascii=False, indent=1)); return 0
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
