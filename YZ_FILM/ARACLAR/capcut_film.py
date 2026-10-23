"""CAPCUT FİLM — film klasöründen düzenlenebilir bir CapCut projesi üretir (render yapmaz).

Kullanım: python capcut_film.py <film_klasoru>
Önce KONTROL (SIRALI_VIDEO) ve SESLENDİR (SESLER/diyalog.json) çalışmış olmalı.
CapCut'ta oluşan kanallar:
  Klipler   1080p'ye büyütülmüş sahne videoları (replikli sahnelerde klibin kendi sesi kapalı)
  Bantlar   sinema bantları (şeffaf PNG; istemezsen kanalı gizle/sil)
  Baslik    film adı yazısı
  Altyazi   düzenlenebilir altyazı (SAHNELER.json'daki altyazi_dili; yoksa altyazı eklenmez)
  Diyalog   sabit karakter sesleri
  Ortam     replikli sahnelerin ortam sesi (konuşması ayıklanmış)
  Muzik     geçici müzik (istersen CapCut'ta değiştir)
Proje CapCut'ın proje klasörüne yazılır; mevcut projelere dokunulmaz.
"""
import os, sys, json, subprocess, time, uuid
import ortak   # SAHNELER.json v2 koruması
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "kurgu_koprusu"))
import pycapcut as cc
from kurgu_koprusu import load_video, load_audio, complete_metadata   # kullanıcının V5 köprüsünden, değiştirilmeden

SEC, SR, W, H, BAR = 1_000_000, 44100, 1920, 1080, 96
try: DRAFTS = Path(ortak.yollar()["capcut_taslak"])      # CapCut taslak klasörü YOLLAR.json'dan
except ortak.YolYok as e:
    if __name__ == "__main__": print("!!", e); sys.exit(4)
    raise


def run(*a): subprocess.run([str(x) for x in a], check=True)
def log(*a): print(*a, flush=True)
def dur(p): return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                                        capture_output=True, text=True).stdout)
def us(x): return int(round(x * SEC))
def ts(x):
    h, m = int(x // 3600), int(x % 3600 // 60); s = x % 60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s % 1) * 1000)) % 1000:03}"


def upscale(src, dst):
    if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src): return
    run("ffmpeg", "-v", "error", "-y", "-i", src, "-vf", f"scale={W}:{H}:flags=lanczos,unsharp=5:5:0.6:5:5:0,setsar=1",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", dst)


def temp_music(total, path):
    """Geçici karanlık akor dokusu (Dm-Bb-Gm-A). Gerçek müzik gelince CapCut'ta değiştirilir."""
    def tone(f, d, amp):
        t = np.arange(int(d * SR)) / SR; env = np.minimum(t / 2.5, 1) * np.minimum((d - t) / 2.5, 1)
        return sum(np.sin(2 * np.pi * f * k * (1 + 0.003 * i) * t + i) / k ** 1.3 for i, k in enumerate((1, 2, 3, 4))) * env * amp
    m = np.zeros(int(total * SR) + SR, np.float32); ch = [[0, 3, 7, 12], [-4, 0, 3, 8], [-7, -4, 0, 5], [-5, -1, 2, 7]]
    t, i = 0.0, 0
    while t < total:
        for st in ch[i % 4]:
            seg = tone(73.42 * 2 ** (st / 12), 9.5, 0.035); k = int(t * SR); n = min(len(seg), len(m) - k)
            if n > 0: m[k:k + n] += seg[:n]
        t += 8.0; i += 1
    m = m[:int(total * SR)]; m /= (np.max(np.abs(m)) + 1e-9) / 0.7
    sf.write(path, np.stack([m, m], 1), SR)


def bars_png(path):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, BAR), fill=(0, 0, 0, 255)); d.rectangle((0, H - BAR, W, H), fill=(0, 0, 0, 255)); im.save(path)


def main(root):
    root = os.path.abspath(root)
    plan = ortak.sahneler_oku(root, "capcut_film.py")
    K = os.path.join(root, "KURGU"); C1080 = os.path.join(K, "klipler_1080"); os.makedirs(C1080, exist_ok=True)
    dlg_p = os.path.join(root, "SESLER", "diyalog.json")
    dlg = json.load(open(dlg_p, encoding="utf-8")) if os.path.exists(dlg_p) else {}
    if not DRAFTS.is_dir(): raise FileNotFoundError(f"CapCut proje klasörü bulunamadı: {DRAFTS}")

    # 1) zaman çizelgesi: sahneler numara sırasıyla, her klip kendi süresi kadar
    log("1) Klipler 1080p'ye büyütülüyor (ilk seferde biraz sürer)...")
    timeline, t, missing = [], 0.0, []
    for s in sorted(plan["sahneler"], key=lambda s: s["no"]):
        n = s["no"]; src = os.path.join(root, "SIRALI_VIDEO", f"{n:03d}.mp4")
        if not os.path.exists(src): missing.append(n); continue
        dst = os.path.join(C1080, f"{n:03d}.mp4"); upscale(src, dst); d = dur(dst)
        timeline.append((n, dst, t, d)); t += d
    total = t
    if missing: log(f"   UYARI: videosu olmayan sahneler atlandı: {missing}")
    log(f"   {len(timeline)} klip, toplam {total:.1f} sn")

    # 2) altyazı dosyaları (her dil için; YouTube'a da yüklenebilir)
    subs = {"en": [], "tr": []}
    for n, _, t0, d in timeline:
        for c in dlg.get(str(n), {}).get("cumleler", []):
            a, b = t0 + c["bas"], t0 + c["bas"] + c["sure"] + 0.3
            for lang in subs:
                if c.get(lang): subs[lang].append((a, b, c[lang]))
    for lang, items in subs.items():
        if items:
            with open(os.path.join(K, f"altyazi_{lang}.srt"), "w", encoding="utf-8") as f:
                for i, (a, b, txt) in enumerate(items, 1): f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{txt}\n\n")
    music = os.path.join(K, "muzik_gecici.wav"); temp_music(total, music)
    bars = os.path.join(K, "sinema_bantlari.png"); bars_png(bars)

    # 3) CapCut projesi
    log("2) CapCut projesi oluşturuluyor...")
    name = f"YZ {plan['film']} {time.strftime('%Y%m%d-%H%M%S')}"
    sc = cc.DraftFolder(str(DRAFTS)).create_draft(name, W, H, fps=24, allow_replace=False)
    sc.add_track(cc.TrackType.video, "Klipler")
    sc.add_track(cc.TrackType.video, "Bantlar", relative_index=2)
    sc.add_track(cc.TrackType.audio, "Diyalog")
    sc.add_track(cc.TrackType.audio, "Ortam")
    sc.add_track(cc.TrackType.audio, "Muzik")
    for n, path, t0, d in timeline:
        has_dlg = str(n) in dlg
        mat = load_video(cc, path); L = min(us(d), mat.duration)
        sc.add_segment(cc.VideoSegment(mat, cc.Timerange(us(t0), L), source_timerange=cc.Timerange(0, L),
                                       volume=0.0 if has_dlg else 1.0), "Klipler")
        if has_dlg:
            bed = load_audio(cc, os.path.join(root, "SESLER", dlg[str(n)]["ortam"])); BL = min(L, bed.duration)
            sc.add_segment(cc.AudioSegment(bed, cc.Timerange(us(t0), BL), source_timerange=cc.Timerange(0, BL), volume=0.8), "Ortam")
            last_end = us(t0)
            for c in dlg[str(n)]["cumleler"]:
                a = load_audio(cc, os.path.join(root, "SESLER", c["dosya"]))
                st = max(us(t0 + c["bas"]), last_end); ln = min(a.duration, us(t0) + L - st)
                if ln <= 0: continue
                sc.add_segment(cc.AudioSegment(a, cc.Timerange(st, ln), source_timerange=cc.Timerange(0, ln), volume=1.0), "Diyalog")
                last_end = st + ln
    bm = load_video(cc, bars); sc.add_segment(cc.VideoSegment(bm, cc.Timerange(0, us(total))), "Bantlar")
    mm = load_audio(cc, music); ML = min(us(total), mm.duration)
    sc.add_segment(cc.AudioSegment(mm, cc.Timerange(0, ML), source_timerange=cc.Timerange(0, ML), volume=0.45), "Muzik")
    # film adı (ilk klibin üstünde)
    title = plan.get("baslik", plan["film"]).split("|")[-1].strip() or plan["film"]
    sc.add_track(cc.TrackType.text, "Baslik")
    sc.add_segment(cc.TextSegment(title, cc.Timerange(us(2.0), us(5.0)),
                                  style=cc.TextStyle(size=16, bold=True, color=(1.0, 0.93, 0.84), align=1, letter_spacing=12),
                                  border=cc.TextBorder(width=25, alpha=0.6), clip_settings=cc.ClipSettings(transform_y=0.05)), "Baslik")
    lang = plan.get("altyazi_dili")
    srt = os.path.join(K, f"altyazi_{lang}.srt") if lang else None
    if srt and os.path.exists(srt):
        ref = cc.TextSegment("x", cc.Timerange(0, SEC), style=cc.TextStyle(size=6.5, color=(1, 1, 1), align=1, auto_wrapping=True),
                             border=cc.TextBorder(width=30, alpha=0.9), clip_settings=cc.ClipSettings(transform_y=-0.78))
        sc.import_srt(srt, "Altyazi", style_reference=ref)
    # yönetmen notları: her sahnenin amacı ve duygusu (ekranın üstünde, sarı). Render'dan önce bu kanal silinir.
    sc.add_track(cc.TrackType.text, "NOTLAR")
    scenes = {s["no"]: s for s in plan["sahneler"]}
    my_texts = [title] + [x[2] for x in subs.get(lang, [])] if lang else [title]
    for n, _, t0, d in timeline:
        s = scenes[n]; note = f"S{n:03d}"
        if s.get("amac"): note += f" · {s['amac']}"
        if s.get("duygu"): note += f" · Duygu: {s['duygu']}"
        if s.get("motor") and s["motor"] != "flow": note += f" · [{s['motor']}]"
        my_texts.append(note)
        sc.add_segment(cc.TextSegment(note, cc.Timerange(us(t0), us(d)),
                                      style=cc.TextStyle(size=4.2, color=(1.0, 0.85, 0.2), align=1, auto_wrapping=True, max_line_width=0.9),
                                      border=cc.TextBorder(width=20, alpha=0.8), clip_settings=cc.ClipSettings(transform_y=0.8)), "NOTLAR")
    sc.content.setdefault("config", {})["maintrack_adsorb"] = False
    sc.save()
    target = DRAFTS / name
    complete_metadata(target, name, us(total))
    json.dump({"proje": name, "klasor": str(target), "sure_sn": round(total, 2), "klip": len(timeline), "eksik": missing,
               "sahneler": [{"no": n, "bas": round(t0, 3), "sure": round(d, 3), "dosya": os.path.basename(p)} for n, p, t0, d in timeline],
               "benim_yazilarim": my_texts},
              open(os.path.join(K, "son_capcut_projesi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    log(f"\nCAPCUT PROJESİ HAZIR: {name}\nSüre: {total:.1f} sn · {len(timeline)} klip · {sum(len(v['cumleler']) for v in dlg.values())} replik")
    log("CapCut açıksa kapatıp yeniden aç; proje listede en üstte görünür.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
