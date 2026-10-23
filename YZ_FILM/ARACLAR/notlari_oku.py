"""NOTLARI OKU — kullanıcının CapCut projesine yazdığı notları bulur ve sahnelere bağlar.

Kullanım: python notlari_oku.py <film_klasoru>
KURGU/son_capcut_projesi.json'daki projeyi okur. Programın kendi eklediği yazılar (başlık, altyazı, NOTLAR)
dışındaki her yazı kullanıcı notu sayılır; değiştirilmiş altyazılar da ayrıca listelenir.
Not hangi saniyedeyse o anda Klipler kanalında hangi klip varsa o sahneye bağlanır (klipler kaydırılmış olsa bile doğru çalışır).
Çıktı: KURGU/NOTLARIM.txt ve NOTLARIM.json
"""
import os, sys, json, re
import ortak   # SAHNELER.json v2 koruması
sys.stdout.reconfigure(encoding="utf-8")
SEC = 1_000_000


def text_of(mat):
    try: return json.loads(mat["content"])["text"]
    except Exception: return mat.get("content", "")


def fmt(us):
    s = us / SEC; return f"{int(s // 60):02d}:{s % 60:05.2f}"


def main(root):
    root = os.path.abspath(root); K = os.path.join(root, "KURGU")
    info = json.load(open(os.path.join(K, "son_capcut_projesi.json"), encoding="utf-8"))
    plan = ortak.sahneler_oku(root, "notlari_oku.py")
    scenes = {s["no"]: s for s in plan["sahneler"]}
    path = os.path.join(info["klasor"], "draft_content.json")
    raw = open(path, "rb").read()
    if not raw.lstrip().startswith(b"{"):
        print("!! CapCut projesi şifreli kaydedilmiş, okunamıyor. Yedek yol: notları SRT olarak dışa aktarıp gönder."); return
    c = json.loads(raw.decode("utf-8"))
    texts = {m["id"]: text_of(m) for m in c["materials"].get("texts", [])}
    vids = {m["id"]: m.get("path", "") for m in c["materials"].get("videos", [])}
    mine = set(info.get("benim_yazilarim", []))
    # o anda Klipler kanalında hangi klip var → sahne no (dosya adı NNN.mp4)
    clips = []
    for t in c["tracks"]:
        if t["type"] == "video" and t.get("name") == "Klipler":
            for s in t["segments"]:
                m = re.match(r"(\d{3})\.mp4$", os.path.basename(vids.get(s["material_id"], "")))
                if m: tr = s["target_timerange"]; clips.append((tr["start"], tr["start"] + tr["duration"], int(m.group(1))))
    def scene_at(us):
        hit = [n for a, b, n in clips if a <= us < b]
        return hit[0] if hit else None
    # programın koyduğu yazıların başlangıç anları: bir yazı tam bu anlardan birinde başlıyorsa "değiştirilmiş" sayılır,
    # değilse (aynı kanala eklenmiş olsa bile) kullanıcı notudur
    orig = {"Baslik": [int(2.0 * SEC)], "NOTLAR": [int(s["bas"] * SEC) for s in info.get("sahneler", [])], "Altyazi": []}
    lang = plan.get("altyazi_dili")
    srt = os.path.join(K, f"altyazi_{lang}.srt") if lang else ""
    if srt and os.path.exists(srt):
        for m in re.finditer(r"(\d+):(\d+):(\d+),(\d+) -->", open(srt, encoding="utf-8").read()):
            h, mi, se, ms = map(int, m.groups()); orig["Altyazi"].append(int((h * 3600 + mi * 60 + se + ms / 1000) * SEC))
    notes, changed = [], []
    for t in c["tracks"]:
        if t["type"] != "text": continue
        for s in t["segments"]:
            txt = texts.get(s["material_id"], "").strip()
            if not txt or txt in mine: continue
            tr = s["target_timerange"]; mid = tr["start"] + tr["duration"] // 2
            n = scene_at(mid)
            item = {"zaman": fmt(tr["start"]), "sahne": n, "kanal": t.get("name", ""), "not": txt,
                    "sahne_amaci": scenes.get(n, {}).get("amac", "") if n else ""}
            was_mine = any(abs(tr["start"] - o) < 0.15 * SEC for o in orig.get(t.get("name", ""), []))
            (changed if was_mine else notes).append(item)
    notes.sort(key=lambda x: x["zaman"]); changed.sort(key=lambda x: x["zaman"])
    json.dump({"notlar": notes, "degisen_yazilar": changed}, open(os.path.join(K, "NOTLARIM.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    lines = [f"{info['proje']} — kullanıcı notları", "=" * 60]
    for x in notes:
        lines.append(f"[{x['zaman']}] Sahne {x['sahne']:03d} ({x['sahne_amaci']})" if x["sahne"] else f"[{x['zaman']}] (klip yok)")
        lines.append(f"    NOT: {x['not']}")
    if changed:
        lines += ["", "Değiştirilmiş altyazı / not / başlık:"]
        for x in changed: lines.append(f"[{x['zaman']}] Sahne {x['sahne']} · {x['kanal']}: {x['not']}")
    if not notes and not changed: lines.append("Kullanıcı notu bulunamadı.")
    open(os.path.join(K, "NOTLARIM.txt"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
