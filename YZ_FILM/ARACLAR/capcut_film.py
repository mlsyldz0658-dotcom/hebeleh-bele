"""CAPCUT FİLM — kurgu planından düzenlenebilir, sürümlü CapCut taslağı kurar (render yapmaz; TASARIM §6.7, D-30; [KU2] KR10, KR12).

Kullanım (v2; KURGU/KURGU_PLANI.json varsa):
  python capcut_film.py --film <film> [--yayin] [--hizli] [--saglayici sahte]
    → CapCut taslağı "YZ <FILM> v<N>" (yeni klasör; var olan taslaklara dokunulmaz), KURGU/surumler/v<N>/ (kırpma ve 1080p türevleri,
      sürüm adıyla; eski sürümler bozulmaz), KURGU/son_capcut_projesi.json v2 (segment ↔ plan eşlemesi), KURGU/altyazi_en.srt (+ tr)
  --yayin: NOTLAR ve Altyazi kanalı YOK (SRT YouTube'a ayrı gider; [SON] S-6) → "YZ <FILM> v<N> YAYIN", KURGU/son_capcut_projesi_yayin.json
  --ad-ek " (senin düzenlemenle)": taslak adına ek (capcut_yama'nın yedek yolu: kullanıcının kararlarıyla yeni adla kur)
  --hizli: 1080p türevi yerine özgün klip sürüm klasörüne kopyalanır (deneme); --saglayici sahte: pycapcut yerine CapCut biçimli fikstür yazar
           (CapCut klasörü yoksa KURGU/CAPCUT_SAHTE/'ye).
Kanallar (capcut_taslak.py): Klipler (sessiz; source_timerange = kullanim) · Bantlar · Kartlar (ekran başlığı `baslik`'tan bölünmeden) ·
Altyazi (duyulan_metin) · Diyalog (replik replik) · Efekt · Ambiyans (sahne parçaları) · Muzik (ipucu parçaları; geçici akor yalnız müzik
yoksa ve adı GECICI) · NOTLAR (sıra, plan, amaç, duygu, hedef yoğunluk). 48 kHz. Klip kaynağı: buyuk/ > cila/ > 1080p türevi.
Geçme (KR10): yeni taslakta `taslak_fark --oz-denetim` farkı 0, boşluk 0, eksik medya 0, süre = KURGU_PLANI ±1 kare; değilse çıkış 1.
Eski kullanım (v1; SAHNELER v1 ve KURGU_PLANI yok): python capcut_film.py <film_klasoru> — davranış değişmedi.
Çıkış kodları: 0 tamam · 1 öz denetim HATA · 2 KURGU_PLANI/klasör yok · 4 ortam (pycapcut ya da CapCut klasörü yok).
"""
import os, sys, json, subprocess, time, uuid, shutil
import ortak   # SAHNELER.json v2 koruması (v1 yolu)
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "kurgu_koprusu"))
SURUM = "capcut_film 2.0"
SEC, SR, W, H, BAR = 1_000_000, 48000, 1920, 1080, 96


def _taslak_klasoru():
    try: return Path(ortak.yollar()["capcut_taslak"])
    except ortak.YolYok: return None


# --- v2 -------------------------------------------------------------------------------------------------------------
def klipleri_hazirla(kok, kp, vk, hizli=False):
    import kurgu_ortak as ko
    os.makedirs(os.path.join(vk, "klipler"), exist_ok=True)
    for x in kp.get("planlar") or []:
        g = x["goruntu"]
        if g.get("tur") != "video" or not g.get("dosya"): continue
        ad = f"{int(x['plan']):03d}.mp4"; dst = os.path.join(vk, "klipler", ad)
        kaynak = next((p for p in (os.path.join(vk, "buyuk", ad), os.path.join(vk, "cila", ad)) if os.path.exists(p)), ko.mutlak(kok, g["dosya"]))
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(kaynak): continue
        if hizli or "buyuk" in kaynak: shutil.copyfile(kaynak, dst)
        else:
            ko.ffmpeg("-i", kaynak, "-vf", f"scale={W}:{H}:flags=lanczos,setsar=1", "-c:v", "libx264", "-preset", "fast", "-crf", "18",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", str(SR), dst)


def v2(kok, argv):
    import kurgu_ortak as ko, capcut_taslak as ct, taslak_fark
    kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: print("!! KURGU_PLANI yok; önce plan_kurgu.py", flush=True); return 2
    yayin = "--yayin" in argv; sahte = ko.saglayici_adi(argv) == "sahte"; n = int(kp.get("kurgu_surumu") or 1)
    vk = os.path.join(kok, "KURGU", "surumler", f"v{n}")
    klipleri_hazirla(kok, kp, vk, hizli=("--hizli" in argv) or sahte)
    film = ko.sahneler(kok).get("film") or os.path.basename(kok)
    ad = f"YZ {film} v{n}" + (" YAYIN" if yayin else "") + (ko.secenek(argv, "--ad-ek") or "")
    kok_t = _taslak_klasoru()
    if sahte and (kok_t is None or not kok_t.is_dir()): kok_t = Path(os.path.join(kok, "KURGU", "CAPCUT_SAHTE")); kok_t.mkdir(parents=True, exist_ok=True)
    if kok_t is None or not kok_t.is_dir(): print(f"!! CapCut taslak klasörü yok: {kok_t} (CapCut kurulu mu?)", flush=True); return 4
    if not sahte:
        try: import pycapcut  # noqa: F401
        except ImportError: print("!! pycapcut kurulu değil (KUR1)", flush=True); return 4
    m = ct.model_kur(kok, kp, ad, yayin=yayin, klip_klasoru=vk)
    klasor, _ = ct.yaz(m, str(kok_t), sahte=sahte)
    m["ad"] = os.path.basename(klasor)
    K = os.path.join(kok, "KURGU"); dj = ko.diyalog_oku(kok); pl = ko.sahne_planlari(kok)
    if not yayin:
        ct.srt_yaz(os.path.join(K, "altyazi_en.srt"), ct.altyazi_satirlari(kok, kp, dj, pl, "en"))
        tr = ct.altyazi_satirlari(kok, kp, dj, pl, "tr")
        if tr: ct.srt_yaz(os.path.join(K, "altyazi_tr.srt"), tr)
    segs = []
    for s in ct.model_segmentleri(m):
        e = {"kanal": s["kanal"], "segment_id": s["segment_id"], "bas": s["bas"], "sure": s["sure"]}
        if s["kanal"] == "Klipler":
            e.update(plan=s["plan"], sira=s.get("sira"), kaynak=ko.goreli(kok, s["yol"]),
                     kaynak_aralik=None if s.get("kaynak_bas") is None else {"bas": s["kaynak_bas"], "sure": s["kaynak_sure"]})
        elif s["kanal"] == "Diyalog": e.update(replik=s.get("replik"), plan=s.get("plan"), kaynak=ko.goreli(kok, s["yol"]))
        elif s.get("yol"): e["kaynak"] = ko.goreli(kok, s["yol"])
        if s.get("plan") is not None and s["kanal"] == "NOTLAR": e["plan"] = s["plan"]
        if s.get("ses") is not None and s["kanal"] in ct.SES_KANALLARI + ("Klipler",): e["ses"] = s["ses"]
        segs.append(e)
    proje = {"_surum": 2, "_uretim": ko.po.zarf("A17" if yayin else "A16", SURUM), "proje": m["ad"], "klasor": klasor,
             "kurgu_plani_surumu": n, "kurgu_plani_imza": m["kurgu_plani_imza"], "kurgu_plani": ko.goreli(kok, kp_yol),
             "sure_sn": m["sure"], "fps": m["fps"], "segmentler": segs, "yayin": yayin, "sahte": sahte,
             "benim_yazilarim": [s["metin"] for s in ct.model_segmentleri(m) if s.get("metin")], "notlar_kanali": not yayin}
    hedef = os.path.join(K, "son_capcut_projesi_yayin.json" if yayin else "son_capcut_projesi.json")
    ortak.atomik_yaz(hedef, proje)
    oz = taslak_fark.oz_denetim(kok, klasor, proje, kp)
    print(f"CAPCUT TASLAĞI HAZIR: {m['ad']} · {m['sure']:.2f} sn · {len(kp['planlar'])} plan · öz denetim "
          f"{'GEÇ' if oz['sonuc'] == 'GEC' else 'HATA: ' + '; '.join(oz['nedenler'])}", flush=True)
    if not yayin: print("CapCut açıksa kapatıp yeniden aç; taslak listede en üstte görünür.", flush=True)
    return 0 if oz["sonuc"] == "GEC" else 1


# --- v1 (değişmedi; SAHNELER v1 dosyaları için) ------------------------------------------------------------------------------
def _v1_kur():
    global np, sf, Image, ImageDraw, cc, load_video, load_audio, complete_metadata, DRAFTS, SR
    import numpy as np, soundfile as sf
    from PIL import Image, ImageDraw
    import pycapcut as cc
    from kurgu_koprusu import load_video, load_audio, complete_metadata   # kullanıcının V5 köprüsünden, değiştirilmeden
    SR = 44100
    DRAFTS = _taslak_klasoru()
    if DRAFTS is None: print("!! YOLLAR.json yok (KURULUM.bat)"); sys.exit(4)


def giris(argv):
    import kurgu_ortak as ko
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, kalan = ko.film_ve_arg(argv)
    _, kp = ko.kurgu_plani(kok)
    if kp or "--film" in argv or "--yayin" in argv: return v2(kok, kalan)
    main(kok); return 0


if __name__ == "__main__":
    sys.exit(giris(sys.argv[1:]))
