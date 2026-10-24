"""İZLEME PAKETİ — kurgulanmış filmi habersiz seyirci ajanına "izletmek" için kare paketi hazırlar.

Kullanım: python izleme_paketi.py <film_klasoru> [--parti 1] [--kare 3]
Her sahnenin videosundan eşit aralıklı kareler (varsayılan 3) çıkarır, küçültür ve yanına
ekranda DUYULAN repliği (SESLER/diyalog.json ya da SAHNELER.json) yazar. "amac"/"duygu" YAZILMAZ: seyirci yalnız
ekranda olanı görmeli. Konuşanın ADI da ekranda kurulmadan yazılmaz: adı daha önce bir replikte duyulana kadar
konuşan, karakterin görünüş tarifiyle ("karakterler.<ad>.tarif", yoksa "ekrandaki kişi") anılır. Çıktı: _RAPOR/IZLEME[_P<n>]/NNN_k.jpg + IZLE.md (sırayla okunacak film akışı).
"""
import os, sys, re, json, subprocess
import ortak   # SAHNELER.json v2 koruması
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0


def main(kok, parti=None, kare=3):
    kok = os.path.abspath(kok)
    plan = ortak.sahneler_oku(kok, "izleme_paketi.py")
    dlg_p = os.path.join(kok, "SESLER", "diyalog.json")
    dlg = json.load(open(dlg_p, encoding="utf-8")) if os.path.exists(dlg_p) else {}
    hedef = os.path.join(kok, "_RAPOR", "IZLEME" + (f"_P{parti}" if parti else "")); os.makedirs(hedef, exist_ok=True)
    kar = plan.get("karakterler") or {}; kurulan = set()
    def ad(k): return (kar.get(k) or {}).get("ad") or k.replace("_", " ").title()
    def konusan(k):
        if not k: return "ekrandaki kişi"
        return ad(k).upper() if k in kurulan else f"[{(kar.get(k) or {}).get('tarif') or 'ekrandaki kişi'}]"
    satir, t = ["# İZLEME PAKETİ — kareleri sırayla aç, altındaki replik o anda duyulur", ""], 0.0
    for s in sorted(plan["sahneler"], key=lambda s: s["no"]):
        if parti and s.get("parti") != parti: continue
        n = s["no"]; v = os.path.join(kok, "SIRALI_VIDEO", f"{n:03d}.mp4")
        if not os.path.exists(v): satir.append(f"## [{t:6.1f} sn] S{n:03d} — VİDEO YOK\n"); continue
        d = dur(v); kareler = []
        for k in range(kare):
            out = os.path.join(hedef, f"{n:03d}_{k}.jpg")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{d * (k + 0.5) / kare:.2f}", "-i", v, "-frames:v", "1",
                            "-vf", "scale=640:-2", "-q:v", "4", out], check=True)
            kareler.append(os.path.basename(out))
        cumleler = [c["en"] for c in dlg.get(str(n), {}).get("cumleler", [])]
        if not cumleler and s.get("replik"): cumleler = [s["replik"].get("metin", "")]
        kim = (s.get("replik") or {}).get("karakter", "")
        satir.append(f"## [{t:6.1f} sn] S{n:03d} ({d:.1f} sn)")
        satir += [f"- kare: {x}" for x in kareler]
        satir.append(f"- duyulan: {konusan(kim)}: \"{' '.join(cumleler)}\"" if cumleler else "- duyulan: (replik yok)")
        duyulan = " ".join(cumleler).lower()
        kurulan.update(k for k in kar if re.search(r"\b" + re.escape(ad(k).lower()) + r"\b", duyulan))
        satir.append(""); t += d
    satir.append(f"TOPLAM: {t:.1f} sn")
    open(os.path.join(hedef, "IZLE.md"), "w", encoding="utf-8").write("\n".join(satir) + "\n")
    print(f"İzleme paketi: {hedef}  ({t:.1f} sn)"); return hedef


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(0)
    main(a[0], int(a[a.index("--parti") + 1]) if "--parti" in a else None, int(a[a.index("--kare") + 1]) if "--kare" in a else 3)
