"""NOTLARI OKU — kullanıcının CapCut taslağına yazdığı notları bulur ve plana bağlar (TASARIM §6.7 `notlari_oku.py` v2; [KU2] KR11, §4.5.8).

Kullanım: python notlari_oku.py --film <film>   ya da   python notlari_oku.py <film_klasoru>   (NOTLARI_OKU.bat, film.py "notlar oku")
v2 (KURGU/son_capcut_projesi.json _surum 2): taslak SALT OKUNUR okunur (capcut_taslak.oku). Programın kendi yazıları (benim_yazilarim,
bizim kanal segmentleri) dışındaki her yazı kullanıcı notudur; değiştirilmiş bizim yazılarımız ayrıca listelenir. Not hangi anda ise o anda
Klipler kanalında hangi segment varsa, segment_id → plan eşlemesiyle o PLANA bağlanır (klipler kaydırılmış olsa ya da aynı klipten iki
plan çıksa da doğru plan bulunur). Çıktı: NOTLARIM.json (film kökü; ADLAR film_dosyalari) {notlar[{zaman, cizelge_sn, sira, plan,
segment_id, kanal, not, plan_amaci}], degisen_yazilar[]} + KURGU/NOTLARIM.txt. Şifreli taslakta okunmaz; yedek yol tek cümleyle söylenir.
v1 (eski proje kaydı): davranış değişmedi → KURGU/NOTLARIM.txt ve KURGU/NOTLARIM.json.
Çıkış kodları: 0 tamam · 2 proje kaydı ya da taslak yok / şifreli.
"""
import os, sys, json, re
import ortak   # SAHNELER.json v2 koruması (v1 yolu)
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
SEC = 1_000_000
SURUM = "notlari_oku 2.0"


def v2(kok, info):
    import kurgu_ortak as ko, capcut_taslak as ct, taslak_fark as tf
    o = ct.oku(info["klasor"])
    if o["sifreli"]: print(tf.SIFRELI_BILGI, flush=True); return 2
    if not o["icerik"]: print(f"!! taslak okunamadı: {info['klasor']}", flush=True); return 2
    ds = ct.segmentler(o["icerik"]); bizim = {x["segment_id"]: x for x in info.get("segmentler") or []}
    yazilar = set(info.get("benim_yazilarim") or []); pl = ko.sahne_planlari(kok)
    klipler = sorted([d for d in ds if d["kanal"] == "Klipler"], key=lambda d: d["bas"])
    sira = {d["segment_id"]: i + 1 for i, d in enumerate(klipler)}
    def plan_at(t):
        for d in klipler:
            if d["bas"] - 1e-6 <= t < d["bas"] + d["sure"]:
                return d, (bizim.get(d["segment_id"]) or {}).get("plan")
        return None, None
    notlar, degisen = [], []
    for d in ds:
        if d.get("malzeme_turu") != "texts" and d["tur"] != "text": continue
        metin = (d.get("metin") or "").strip()
        if not metin: continue
        b = bizim.get(d["segment_id"])
        if b and metin in yazilar: continue
        seg, plan = plan_at(d["bas"] + d["sure"] / 2)
        kayit = {"zaman": ko.zaman_kodu(d["bas"]), "cizelge_sn": round(d["bas"], 3), "sira": sira.get(seg["segment_id"]) if seg else None,
                 "plan": plan, "segment_id": seg["segment_id"] if seg else None, "kanal": d["kanal"], "not": metin,
                 "plan_amaci": (pl.get(plan) or {}).get("amac", "") if plan else ""}
        (degisen if (b or metin in yazilar) else notlar).append(kayit)
    notlar.sort(key=lambda x: x["cizelge_sn"]); degisen.sort(key=lambda x: x["cizelge_sn"])
    ortak.atomik_yaz(os.path.join(kok, "NOTLARIM.json"), {"_uretim": ko.po.zarf("A16n", SURUM), "taslak": info.get("proje"),
                                                         "notlar": notlar, "degisen_yazilar": degisen})
    satir = [f"{info.get('proje')} — kullanıcı notları", "=" * 60]
    for x in notlar:
        satir.append(f"[{x['zaman']}] #{x['plan']} (sıra {x['sira']}; {x['plan_amaci']})" if x["plan"] else f"[{x['zaman']}] (klip yok)")
        satir.append(f"    NOT: {x['not']}")
    if degisen:
        satir += ["", "Değiştirilmiş altyazı / not / başlık:"] + [f"[{x['zaman']}] #{x['plan']} · {x['kanal']}: {x['not']}" for x in degisen]
    if not notlar and not degisen: satir.append("Kullanıcı notu bulunamadı.")
    os.makedirs(os.path.join(kok, "KURGU"), exist_ok=True)
    with open(os.path.join(kok, "KURGU", "NOTLARIM.txt"), "w", encoding="utf-8") as f: f.write("\n".join(satir) + "\n")
    print("\n".join(satir), flush=True)
    return 0


def giris(argv):
    import kurgu_ortak as ko
    kok, _ = ko.film_ve_arg(argv)
    info = ortak.json_oku(os.path.join(kok, "KURGU", "son_capcut_projesi.json"))
    if not isinstance(info, dict): print("!! KURGU/son_capcut_projesi.json yok", flush=True); return 2
    if int(info.get("_surum", 1) or 1) >= 2: return v2(kok, info)
    main(kok); return 0


# --- v1 (değişmedi) -------------------------------------------------------------------------------------------------------
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
    sys.exit(giris(sys.argv[1:]))
