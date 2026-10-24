"""Video hattı testlerinin ortak fikstürü (PR-11): v2 SAHNELER, G1 GEÇ görseller, kesin bütçe, animatik imzası, sahte klipler.
Testler `import _ortam`'dan SONRA import eder. Ağ ve kredi yok."""
import os, json, shutil, hashlib, subprocess
import ortak


def sha1(yol):
    with open(yol, "rb") as f: return hashlib.sha1(f.read()).hexdigest()


def gorsel_yaz(yol, tohum=0):
    """Küçük ama geçerli bir JPEG (PIL varsa), yoksa benzersiz bayt dizisi."""
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    try:
        from PIL import Image
        Image.new("RGB", (64, 36), ((tohum * 37) % 255, (tohum * 91) % 255, 120)).save(yol, "JPEG")
    except ImportError:
        open(yol, "wb").write(b"\xff\xd8" + bytes([tohum % 256]) * 2000 + b"\xff\xd9")
    return yol


def plan(no, sahne="S01", replik=None, zincir=None, kaynak_klip=None, adimlar=None, kadraj=1):
    p = {"no": no, "sira": no, "parti": 1, "referans": [], "gorsel_istem": f"Plan {no} still frame.",
         "hareket_istem": f"Static medium shot. 0.6-2.0s: plan {no} subject turns head slowly. 2.0-8s: holds still. No music.",
         "hareket_istem_yedek": f"Static medium shot. The subject of plan {no} waits calmly. No music.",
         "zanaat": {"kod": f"{sahne}-P{no:02d}", "sahne_grubu": sahne, "plan_tipi": "aksiyon", "klip_sn": 8,
                    "kadrajdakiler": [{"id": "mara", "olcek": "OY", "yuz_acisi": "3/4"}, {"id": "voss", "olcek": "OY", "yuz_acisi": "profil"}][:kadraj],
                    "eylem_zinciri": adimlar if adimlar is not None else [
                        {"id": "a1", "bas": 0.6, "bit": 2.0, "ozne": "mara", "tur": "fiziksel", "fiil": "doner"}]},
         "kullanim": {"bas": 0.5, "sure": 6.0},
         "uretim": {"saglayici": "flow", "model": "omni-1.1-flash", "zincir": zincir or {"yontem": "bagimsiz"}}}
    if replik: p["replik"] = replik
    if kaynak_klip: p["uretim"]["kaynak_klip"] = kaynak_klip
    return p


def film_kur(kok, planlar, ad="VIDEO_DENEME", butce_ana=1000, animatik=True):
    """v2 film klasörü: SAHNELER, SIRALI_GORSEL (G1 GEÇ + sha1), URETIM_ONIZLEME (kesin), FILM_DURUM (animatik ONAYLI)."""
    os.makedirs(kok, exist_ok=True)
    for p in planlar:
        y = gorsel_yaz(os.path.join(kok, "SIRALI_GORSEL", f"{p['no']:03d}.jpg"), p["no"])
        if (p["uretim"].get("zincir") or {}).get("yontem") != "son_kare":
            p.setdefault("denetim", {})["G1"] = {"sonuc": "GEC", "sha1": sha1(y)[:12]}
    doc = {"_surum": 2, "_sema": "sahneler_v2", "film": ad, "karakterler": {"mara": {"ref": "01_KARAKTERLER/mara.jpg", "ad": "Mara"}},
           "sahne_gruplari": {}, "sahneler": planlar}
    gorsel_yaz(os.path.join(kok, "01_KARAKTERLER", "mara.jpg"), 99)
    ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), doc)
    ortak.atomik_yaz(os.path.join(kok, "URETIM_ONIZLEME.json"),
                     {"_surum": 1, "taslak": False, "butce": {"ana": butce_ana, "taban": butce_ana, "take": 0, "kullanilabilir": butce_ana + 300,
                                                               "dilimler": {"goruntu": 150, "ses": 70, "kurgu": 80}}, "olcek": {}})
    ortak.atomik_yaz(os.path.join(kok, "FILM_DURUM.json"), {"_surum": 2, "animatik": {"durum": "ONAYLI" if animatik else "bekliyor"}})
    return doc


def sahneler_yaz(kok, doc): ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), doc)


def ffmpeg_var(): return bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


def klip_yaz(yol, sure=8.0, siyah=None, donma=None, kutu=None, boyut="320x180", fps=24):
    """Sahte klip (ffmpeg lavfi). siyah=(bas, bit): o aralık siyah. donma=(bas, bit): o aralık donuk.
    kutu=[(bas, bit)]: hareketli kutu videosu — kutu yalnız bu aralıklarda hareket eder, kalan zamanda durur (D-13 adım pencereleri)."""
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    w, h = boyut.split("x")
    if kutu is not None:
        hareket = "+".join(f"if(lt(t,{a}),0,if(lt(t,{b}),t-{a},{b}-{a}))" for a, b in kutu) or "0"
        sabit = "0"
        vf = f"color=c=gray:s={boyut}:r={fps}:d={sure}[bg];color=c=white:s=40x40:r={fps}:d={sure}[k];" \
             f"[bg][k]overlay=x='20+60*({hareket}+{sabit})':y=70:shortest=1"
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-filter_complex", vf, "-pix_fmt", "yuv420p", yol]
    else:
        filt = f"testsrc2=size={boyut}:rate={fps}:duration={sure}"
        ek = []
        if siyah: ek.append(f"drawbox=x=0:y=0:w={w}:h={h}:color=black:t=fill:enable='between(t,{siyah[0]},{siyah[1]})'")
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", filt]
        if donma:
            zincir = (",".join(ek) + ",") if ek else ""
            cmd += ["-filter_complex", f"[0:v]{zincir}split[a][b];[a][b]freezeframes=first={int(donma[0] * fps)}:"
                                       f"last={int(donma[1] * fps)}:replace={int(donma[0] * fps)}"]
        elif ek: cmd += ["-vf", ",".join(ek)]
        cmd += ["-pix_fmt", "yuv420p", yol]
    subprocess.run(cmd, check=True)
    return yol
