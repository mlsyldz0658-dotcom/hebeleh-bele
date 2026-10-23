"""KONTROL — Flow'dan inen görsel/videoları SAHNELER.json'daki sahnelere eşleştirir.

Kullanım: python kontrol.py <film_klasoru> [--sessiz]
Film klasöründe GELENLER'e atılan her şey (zip, rar ya da tek tek dosyalar) işlenir:
  - zip/rar açılır, sonra silinir (içerik _HAM klasöründe saklanır)
  - aynı dosya ikinci kez gelirse atlanır (tek Flow projesinden biriken zip'ler için)
  - yüklenen referanslar ve karakter kartları _ELENENLER'e ayrılır
  - görseller sahne istemleriyle (CLIP + Flow'un dosya başlığı), videolar ilk kareleriyle eşleştirilir
  - SIRALI_GORSEL/NNN.jpg ve SIRALI_VIDEO/NNN.mp4 yazılır; fazlalar ALTERNATIFLER'e
  - RAPOR.html, RAPOR.txt ve EKSIKLER.txt üretilir
Bir sahneyi yeniden yaptırmak için SIRALI_GORSEL/NNN.jpg dosyasını silmen yeterli; sonraki çalıştırmada boş sayılır.
"""
import os, sys, re, json, shutil, zipfile, hashlib, subprocess, html, time
sys.stdout.reconfigure(encoding="utf-8")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")

IMG = (".jpg", ".jpeg", ".png", ".webp")
VID = (".mp4", ".mov", ".webm", ".mkv")
UPLOAD = re.compile(r"\.(png|jpe?g|webp)_\d{14}", re.I)          # Flow'a yüklenen dosya: "mara.png.jpg_20261013215722.jpg"
NUMBERED = re.compile(r"^(\d{1,4})\.(png|jpe?g|webp)_\d{14}", re.I)  # bizim SIRALI_GORSEL'den yüklenen: "006.jpg_2026...jpg"
STAMP = re.compile(r"_\d{14}(_\d+)?$")
UNRAR = r"C:\Program Files\WinRAR\UnRAR.exe"

# eşik değerleri (pilot verisiyle ayarlandı)
IMG_SURE_MARGIN = 1.0     # görsel: en iyi sahne ile ikinci arasındaki fark (z-puanı)
REF_SIM = 0.93            # karakter referansıyla bu kadar benzeyen görsel = referans kopyası
VID_SURE_SIM = 0.90       # video ilk karesi ile görsel benzerliği
VID_SURE_MARGIN = 0.03


def log(*a): print(*a, flush=True)
def sha(p):
    h = hashlib.sha1()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


class Film:
    def __init__(self, root):
        self.root = os.path.abspath(root)
        self.d = {k: os.path.join(self.root, v) for k, v in dict(
            gel="GELENLER", ham="_HAM", ele="_ELENENLER", sg="SIRALI_GORSEL", sv="SIRALI_VIDEO",
            alt="ALTERNATIFLER", rap="_RAPOR").items()}
        for p in self.d.values(): os.makedirs(p, exist_ok=True)
        self.plan = json.load(open(os.path.join(self.root, "SAHNELER.json"), encoding="utf-8-sig"))
        self.scenes = {s["no"]: s for s in self.plan["sahneler"]}
        sp = os.path.join(self.root, "DURUM.json")
        self.state_path = sp
        self.st = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {"gorulen": {}, "sahne": {}, "sabit": {}}
        self.sync_with_disk()

    def save(self):
        json.dump(self.st, open(self.state_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def sc(self, n):
        return self.st["sahne"].setdefault(str(n), {"alternatif": [], "video_alternatif": []})

    def main_img(self, n):
        for e in IMG:
            p = os.path.join(self.d["sg"], f"{n:03d}{e}")
            if os.path.exists(p): return p
    def main_vid(self, n):
        p = os.path.join(self.d["sv"], f"{n:03d}.mp4")
        return p if os.path.exists(p) else None

    def sync_with_disk(self):
        """Kullanıcı SIRALI_* içinden dosya sildiyse o sahne boş sayılır (yeniden üretim için)."""
        for n in self.scenes:
            s = self.sc(n)
            if s.get("gorsel") and not self.main_img(n):
                s["silinen_gorsel"] = s.pop("gorsel"); s.pop("gorsel_skor", None); s.pop("gorsel_emin", None)
            if s.get("video") and not self.main_vid(n):
                s["silinen_video"] = s.pop("video"); s.pop("video_skor", None); s.pop("video_emin", None)

    # ---------------------------------------------------------------- 1) içeri al
    def ingest(self):
        new = []
        def take(src, name):
            h = sha(src)
            if h in self.st["gorulen"]: return None
            dst = os.path.join(self.d["ham"], f"{h[:10]}__{name}")
            shutil.copy2(src, dst); self.st["gorulen"][h] = os.path.basename(dst); new.append(dst); return dst
        tmp = os.path.join(self.root, "_acilan_gecici")
        for f in sorted(os.listdir(self.d["gel"])):
            p = os.path.join(self.d["gel"], f)
            if os.path.isdir(p): continue
            low = f.lower()
            if low.endswith((".zip", ".rar")):
                shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
                try:
                    if low.endswith(".zip"):
                        with zipfile.ZipFile(p) as z: z.extractall(tmp)
                    else:
                        subprocess.run([UNRAR, "x", "-inul", "-o+", p, tmp + os.sep], check=True)
                except Exception as e:
                    log(f"  !! {f} açılamadı ({e}); dokunulmadı."); continue
                n0 = len(new)
                for dp, _, fs in os.walk(tmp):
                    for x in fs:
                        if x.lower().endswith(IMG + VID): take(os.path.join(dp, x), x)
                shutil.rmtree(tmp, ignore_errors=True)
                os.remove(p); log(f"  {f}: {len(new) - n0} yeni dosya (zip silindi)")
            elif low.endswith(IMG + VID):
                r = take(p, f); os.remove(p)
                if r is None: log(f"  {f}: daha önce işlenmiş, atlandı")
        return new

    # ---------------------------------------------------------------- CLIP
    def clip(self):
        if not hasattr(self, "_clip"):
            import torch
            from transformers import CLIPModel, CLIPProcessor
            dev = "cuda" if torch.cuda.is_available() else "cpu"
            m = CLIPModel.from_pretrained("openai/clip-vit-base-patch16").to(dev).eval()
            self._clip = (m, CLIPProcessor.from_pretrained("openai/clip-vit-base-patch16"), dev, torch)
        return self._clip

    def emb_images(self, pils):
        m, pr, dev, torch = self.clip(); out = []
        for i in range(0, len(pils), 16):
            with torch.no_grad():
                x = pr(images=pils[i:i + 16], return_tensors="pt").to(dev)
                e = m.get_image_features(**x)
                e = getattr(e, "pooler_output", e)
            out.append(torch.nn.functional.normalize(e.float(), dim=-1).cpu())
        return torch.cat(out).numpy() if out else None

    def emb_texts(self, texts):
        m, pr, dev, torch = self.clip()
        with torch.no_grad():
            x = pr(text=texts, return_tensors="pt", padding=True, truncation=True, max_length=77).to(dev)
            e = m.get_text_features(**x)
            e = getattr(e, "pooler_output", e)
        return torch.nn.functional.normalize(e.float(), dim=-1).cpu().numpy()

    def load_img(self, p):
        from PIL import Image
        return Image.open(p).convert("RGB")

    def first_frame(self, vid):
        from PIL import Image
        out = os.path.join(self.d["rap"], "_kare.png")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vid, "-frames:v", "1", out], check=True)
        return Image.open(out).convert("RGB")

    # ---------------------------------------------------------------- 2) ayıkla
    def classify(self, files):
        import numpy as np
        imgs, vids, anchors = [], [], {}
        refs = [os.path.join(self.root, c["ref"]) for c in self.plan.get("karakterler", {}).values() if c.get("ref")]
        refs = [r for r in refs if os.path.exists(r)]
        ref_e = self.emb_images([self.load_img(r) for r in refs]) if refs else None
        cand = []
        for p in files:
            name = os.path.basename(p).split("__", 1)[1]; low = name.lower()
            if low.endswith(VID): vids.append(p); continue
            mnum = NUMBERED.match(name)
            if mnum:                                   # bizim numaralı yüklememiz: videonun hangi sahne olduğunu söyler
                anchors[p] = int(mnum.group(1)); continue
            if UPLOAD.search(name) or "reference" in low or "referans" in low:
                self.reject(p, "yüklenen referans / karakter kartı"); continue
            cand.append(p)
        if cand and ref_e is not None:
            e = self.emb_images([self.load_img(p) for p in cand])
            sim = (e @ ref_e.T).max(1)
            for p, s in zip(cand, sim):
                if s >= REF_SIM: self.reject(p, f"karakter referansına çok benziyor ({s:.2f})")
                else: imgs.append(p)
        else: imgs = cand
        # sabit (numaralı yükleme) kayıtları kalıcı tutulur
        for p, n in anchors.items(): self.st["sabit"][os.path.basename(p)] = n
        return imgs, vids

    def reject(self, p, why):
        shutil.move(p, os.path.join(self.d["ele"], os.path.basename(p)))
        self.st.setdefault("elenen", {})[os.path.basename(p)] = why

    # ---------------------------------------------------------------- 3) görsel → sahne
    def title_of(self, p):
        n = os.path.splitext(os.path.basename(p).split("__", 1)[1])[0]
        n = STAMP.sub("", n)
        if re.fullmatch(r"(image|img|\d+|\(\d+\)|\s)*", n, re.I): return None
        return n.replace("_", " ").strip()

    def match_images(self, imgs):
        import numpy as np
        from scipy.optimize import linear_sum_assignment
        if not imgs: return
        nos = sorted(self.scenes)
        T = self.emb_texts([self.scenes[n]["gorsel_istem"] for n in nos])
        I = self.emb_images([self.load_img(p) for p in imgs])
        z = lambda a: (a - a.mean(1, keepdims=True)) / (a.std(1, keepdims=True) + 1e-6)
        S = z(I @ T.T)
        titles = [self.title_of(p) for p in imgs]
        if any(titles):
            TT = self.emb_texts([t or "image" for t in titles]); ST = z(TT @ T.T)
            for i, t in enumerate(titles):
                if t: S[i] += 0.6 * ST[i]
        # boş sahnelere bire bir atama (aynı sahneye iki görsel düşmesin), kalanlar alternatif
        empty = [j for j, n in enumerate(nos) if not self.main_img(n)]
        assigned = {}
        if empty:
            r, c = linear_sum_assignment(-S[:, empty])
            for i, cj in zip(r, c):
                j = empty[cj]
                if S[i, j] > 0.5: assigned[i] = j          # alakasız görseli zorla yerleştirme
        inv = {j: i for i, j in assigned.items()}
        for i, p in enumerate(imgs):
            order = np.argsort(-S[i]); best = order[0]
            j = assigned.get(i, best)
            # güven = en yakın rakip sahneyle yer değiştirmenin toplam uyumu ne kadar bozacağı
            margin, rival = 1e9, None
            for k in range(len(nos)):
                if k == j: continue
                i2 = inv.get(k)
                d = (S[i, j] + S[i2, k] - S[i, k] - S[i2, j]) if (i in assigned and i2 is not None) else (S[i, j] - S[i, k])
                if d < margin: margin, rival = d, k
            sure = bool(margin >= IMG_SURE_MARGIN)
            n = nos[j]; s = self.sc(n); ext = os.path.splitext(p)[1].lower()
            if i in assigned:
                shutil.copy2(p, os.path.join(self.d["sg"], f"{n:03d}{ext}"))
                s.update(gorsel=os.path.basename(p), gorsel_skor=round(float(S[i, j]), 2), gorsel_fark=round(float(margin), 2), gorsel_emin=sure)
                if not sure: s["gorsel_aday2"] = int(nos[rival])
            else:
                k = len(s["alternatif"]) + 1
                dst = f"{n:03d}_alt{k}{ext}"; shutil.copy2(p, os.path.join(self.d["alt"], dst))
                s["alternatif"].append({"dosya": os.path.basename(p), "kopya": dst, "skor": round(float(S[i, j]), 2)})

    # ---------------------------------------------------------------- 4) video → sahne
    def match_videos(self, vids):
        import numpy as np
        if not vids: return
        # önce videonun ilk karesi bizim yerleştirdiğimiz görsellerle (ana + alternatif) karşılaştırılır;
        # numaralı yüklemeler (006.jpg_...) yalnızca içerik eşleşmezse yedek olarak kullanılır
        refs, ref_info = [], []          # (görsel yolu) ↔ (sahne no, tür)
        for n in self.scenes:
            p = self.main_img(n)
            if p: refs.append(p); ref_info.append((n, "ana"))
            for a in self.sc(n)["alternatif"]:
                refs.append(os.path.join(self.d["alt"], a["kopya"])); ref_info.append((n, "alt:" + a["kopya"]))
        own = len(refs)
        for f, n in self.st["sabit"].items():
            p = os.path.join(self.d["ham"], f)
            if os.path.exists(p): refs.append(p); ref_info.append((n, "yuklenen"))
        if not refs: log("  !! videoları eşleştirecek görsel yok"); return
        R = self.emb_images([self.load_img(p) for p in refs])
        V = self.emb_images([self.first_frame(v) for v in vids])
        sim = V @ R.T
        for vi, v in enumerate(vids):
            pool = list(range(own)) if own and sim[vi, :own].max() >= VID_SURE_SIM else list(range(len(refs)))
            order = sorted(pool, key=lambda k: -sim[vi, k]); b = order[0]; n, kind = ref_info[b]
            other = [k for k in order if ref_info[k][0] != n]
            margin = sim[vi, b] - (sim[vi, other[0]] if other else 0)
            sure = bool(sim[vi, b] >= VID_SURE_SIM and margin >= VID_SURE_MARGIN)
            s = self.sc(n)
            if kind.startswith("alt:") and sure:            # video bir alternatif görselden yapılmış: onu ana görsel yap
                self.promote(n, kind[4:])
            if not self.main_img(n) and kind == "yuklenen":  # görsel hiç yerleşmemişse yüklenen kopyayı kullan
                shutil.copy2(refs[b], os.path.join(self.d["sg"], f"{n:03d}.jpg"))
                s.update(gorsel=os.path.basename(refs[b]), gorsel_skor=None, gorsel_emin=True)
            if not self.main_vid(n):
                shutil.copy2(v, os.path.join(self.d["sv"], f"{n:03d}.mp4"))
                s.update(video=os.path.basename(v), video_skor=round(float(sim[vi, b]), 3), video_fark=round(float(margin), 3), video_emin=sure)
            else:
                k = len(s["video_alternatif"]) + 1; dst = f"{n:03d}_alt{k}.mp4"
                shutil.copy2(v, os.path.join(self.d["alt"], dst))
                s["video_alternatif"].append({"dosya": os.path.basename(v), "kopya": dst, "skor": round(float(sim[vi, b]), 3)})

    def promote(self, n, alt_copy):
        s = self.sc(n); cur = self.main_img(n); a = next(x for x in s["alternatif"] if x["kopya"] == alt_copy)
        src = os.path.join(self.d["alt"], alt_copy); ext = os.path.splitext(src)[1]
        if cur:                                            # mevcut ana görsel alternatif olur
            os.replace(cur, src + ".tmp")
            shutil.move(src, os.path.join(self.d["sg"], f"{n:03d}{ext}")); os.replace(src + ".tmp", src)
            s["alternatif"].remove(a)
            s["alternatif"].append({"dosya": s.get("gorsel"), "kopya": alt_copy, "skor": s.get("gorsel_skor")})
        else:
            shutil.copy2(src, os.path.join(self.d["sg"], f"{n:03d}{ext}"))
        s.update(gorsel=a["dosya"], gorsel_skor=a["skor"], gorsel_emin=True, not_="videoda kullanılan görsel ana yapıldı")

    # ---------------------------------------------------------------- 4b) kullanıcı düzeltmeleri (DUZELT.txt)
    DUZELT_SABLON = ("# Düzeltmeleri bu dosyaya yaz, kaydet, KONTROL.bat'a bas. '#' ile başlayan satırlar okunmaz.\n"
                     "#   5 10        -> 5 ile 10'u yer değiştir (görsel + video birlikte)\n"
                     "#   7 alt1      -> 7'nin ana görseli yerine ALTERNATIFLER\\007_alt1 gelsin\n"
                     "#   7 valt1     -> 7'nin videosu yerine ALTERNATIFLER\\007_alt1.mp4 gelsin\n"
                     "#   13 sil      -> 13'ü boşalt (yeniden üretilecek)\n"
                     "#   onay 17 20  -> baktım, doğru (sarı satır yeşile döner)\n")

    def _files(self, n):
        g, v = self.main_img(n), self.main_vid(n)
        return [p for p in (g, v) if p]

    def apply_fixes(self):
        p = os.path.join(self.root, "DUZELT.txt")
        if not os.path.exists(p):
            open(p, "w", encoding="utf-8").write(self.DUZELT_SABLON); return
        cmds = [l.split("#")[0].strip().lower() for l in open(p, encoding="utf-8-sig")]
        cmds = [c for c in cmds if c]
        if not cmds: return
        done = []
        for c in cmds:
            t = c.replace("-", " ").replace("↔", " ").split()
            try:
                if t[0] == "onay":
                    for n in map(int, t[1:]):
                        s = self.sc(n); s["gorsel_emin"] = bool(self.main_img(n)) or s.get("gorsel_emin", False)
                        if self.main_vid(n): s["video_emin"] = True
                        s["onaylandi"] = True
                    done.append(c)
                elif len(t) == 2 and t[1] == "sil":
                    n = int(t[0])
                    for f in self._files(n): os.remove(f)
                    done.append(c)
                elif len(t) == 2 and re.fullmatch(r"v?alt\d+", t[1]):
                    n = int(t[0]); is_v = t[1].startswith("v"); k = t[1].lstrip("v")
                    if is_v:
                        alt = os.path.join(self.d["alt"], f"{n:03d}_{k}.mp4"); cur = self.main_vid(n)
                        if not os.path.exists(alt): raise FileNotFoundError(alt)
                        if cur: os.replace(cur, alt + ".tmp")
                        shutil.move(alt, os.path.join(self.d["sv"], f"{n:03d}.mp4"))
                        if cur: os.replace(alt + ".tmp", alt)
                        s = self.sc(n); s["video_emin"] = True
                    else:
                        alt = next((x["kopya"] for x in self.sc(n)["alternatif"] if os.path.splitext(x["kopya"])[0] == f"{n:03d}_{k}"), None)
                        if not alt: raise FileNotFoundError(f"{n:03d}_{k}")
                        self.promote(n, alt)
                    done.append(c)
                elif len(t) == 2 and t[0].isdigit() and t[1].isdigit():
                    a, b = int(t[0]), int(t[1]); tmp = os.path.join(self.root, "_takas_gecici"); os.makedirs(tmp, exist_ok=True)
                    for n, folder in ((a, None), (b, None)):
                        for f in self._files(n): shutil.move(f, os.path.join(tmp, os.path.basename(f)))
                    for src, dst in ((a, b), (b, a)):
                        for f in os.listdir(tmp):
                            if f.startswith(f"{src:03d}"):
                                to = self.d["sv"] if f.endswith(".mp4") else self.d["sg"]
                                shutil.move(os.path.join(tmp, f), os.path.join(to, f"{dst:03d}" + f[3:]))
                    os.rmdir(tmp)
                    sa, sb = self.sc(a), self.sc(b)
                    self.st["sahne"][str(a)], self.st["sahne"][str(b)] = sb, sa
                    for s in (sa, sb):
                        if s.get("gorsel"): s["gorsel_emin"] = True
                        if s.get("video"): s["video_emin"] = True
                        s.pop("gorsel_aday2", None)
                    done.append(c)
                else:
                    log(f"  !! anlaşılmadı: '{c}'")
            except Exception as e:
                log(f"  !! '{c}' uygulanamadı: {e}")
        if done:
            log("  Düzeltmeler uygulandı: " + " | ".join(done))
            with open(os.path.join(self.root, "_RAPOR", "duzelt_gecmisi.txt"), "a", encoding="utf-8") as h:
                h.write(time.strftime("%d.%m.%Y %H:%M ") + " | ".join(done) + "\n")
        open(p, "w", encoding="utf-8").write(self.DUZELT_SABLON)
        self.sync_with_disk()

    # ---------------------------------------------------------------- 5) raporlar
    def reports(self):
        from PIL import Image
        nos = sorted(self.scenes); lines, miss_img, miss_vid, doubt = [], [], [], []
        for n in nos:
            s = self.sc(n); g, v = self.main_img(n), self.main_vid(n)
            gi = f"{s['gorsel']}  ({'emin' if s.get('gorsel_emin') else 'EMİN DEĞİL – kontrol et'})" if g else "BULUNAMADI"
            vi = f"{s['video']}  ({'emin' if s.get('video_emin') else 'EMİN DEĞİL – kontrol et'})" if v else "yok"
            if g and not s.get("gorsel_emin"): doubt.append(n)
            if v and not s.get("video_emin"): doubt.append(n)
            if not g: miss_img.append(n)
            elif not v: miss_vid.append(n)
            lines.append(f"Sahne {n:03d}  görsel → {gi}\n           video  → {vi}")
        head = (f"{self.plan['film']} — {time.strftime('%d.%m.%Y %H:%M')}\n"
                f"Görsel: {len(nos) - len(miss_img)}/{len(nos)}   Video: {sum(1 for n in nos if self.main_vid(n))}/{len(nos)}   "
                f"Kontrol edilecek: {len(set(doubt))}\n" + "=" * 70 + "\n")
        open(os.path.join(self.root, "RAPOR.txt"), "w", encoding="utf-8").write(head + "\n".join(lines) + "\n")
        # EKSIKLER: görseller referans grubuna göre, videolar 20'lik partilerle; istemler arasında boş satır
        ek = []
        if miss_img:
            ek.append("=== EKSİK GÖRSELLER (Yazı→Sahne) ===\n")
            groups = {}
            for n in miss_img: groups.setdefault(tuple(self.scenes[n].get("referans", [])), []).append(n)
            for refs, ns in groups.items():
                ek.append(f"--- Referans: {', '.join(r + '.jpg' for r in refs) or 'YOK (referansı boş bırak)'} — sahne {', '.join(map(str, ns))}\n")
                ek.append("\n\n".join(self.scenes[n]["gorsel_istem"] for n in ns) + "\n")
        if miss_vid:
            ek.append("=== EKSİK VİDEOLAR (Foto→Video) ===\n")
            for i in range(0, len(miss_vid), 20):
                ns = miss_vid[i:i + 20]
                ek.append(f"--- Görseller (SIRALI_GORSEL, bu sırayla ekle): {', '.join(f'{n:03d}' for n in ns)}\n")
                ek.append("\n\n".join(self.scenes[n]["hareket_istem"] for n in ns) + "\n")
        if not ek: ek = ["Eksik yok. Bütün görseller ve videolar yerinde.\n"]
        open(os.path.join(self.root, "EKSIKLER.txt"), "w", encoding="utf-8").write("\n".join(ek))
        # HTML rapor (küçük resimlerle)
        def thumb(p, key):
            if not p or not os.path.exists(p): return ""
            t = os.path.join(self.d["rap"], key + ".jpg")
            if p.lower().endswith(VID): im = self.first_frame(p)
            else: im = Image.open(p).convert("RGB")
            im.thumbnail((320, 180)); im.save(t, quality=80)
            return f'<img src="_RAPOR/{key}.jpg">'
        rows = []
        for n in nos:
            s = self.sc(n); g, v = self.main_img(n), self.main_vid(n)
            cls = "eksik" if not g else ("suphe" if (not s.get("gorsel_emin") or (v and not s.get("video_emin"))) else ("tamam" if v else "yarim"))
            alts = "".join(thumb(os.path.join(self.d["alt"], a["kopya"]), f"a_{a['kopya']}") + f"<small>{a['kopya']}</small>"
                           for a in s["alternatif"])
            note = ""
            if s.get("gorsel_aday2") and not s.get("gorsel_emin"):
                r = s["gorsel_aday2"]
                note = (f"<br><b>Karışabilir: sahne {r:03d}</b>{thumb(self.main_img(r), f'r{n:03d}_{r:03d}')}"
                        f"<small>{html.escape(self.scenes[r]['gorsel_istem'][:90])}…</small>")
            rows.append(f'<tr class="{cls}"><td><b>{n:03d}</b><br>{", ".join(self.scenes[n].get("referans", [])) or "—"}</td>'
                        f'<td>{thumb(g, f"g{n:03d}")}<br><small>{html.escape(s.get("gorsel") or "BULUNAMADI")}</small>{note}</td>'
                        f'<td>{thumb(v, f"v{n:03d}")}<br><small>{html.escape(s.get("video") or "")}</small></td>'
                        f'<td class="ist">{html.escape(self.scenes[n]["gorsel_istem"])}</td><td>{alts}</td></tr>')
        css = ("body{font-family:Segoe UI,sans-serif;background:#111;color:#eee;margin:16px}table{border-collapse:collapse;width:100%}"
               "td{border:1px solid #333;padding:6px;vertical-align:top}img{width:240px;display:block;border-radius:4px}"
               ".ist{font-size:12px;color:#aaa;max-width:360px}.eksik{background:#3a1212}.suphe{background:#3a3112}"
               ".yarim{background:#122a3a}.tamam{background:#12301a}small{color:#999;word-break:break-all}")
        leg = "<p>Yeşil: görsel+video tamam · Mavi: görsel var, video yok · Sarı: emin değil, bak · Kırmızı: görsel yok</p>"
        open(os.path.join(self.root, "RAPOR.html"), "w", encoding="utf-8").write(
            f"<!doctype html><meta charset=utf-8><title>RAPOR {self.plan['film']}</title><style>{css}</style>"
            f"<h2>{self.plan['film']}</h2><pre>{html.escape(head)}</pre>{leg}"
            f"<table><tr><th>Sahne</th><th>Görsel</th><th>Video (ilk kare)</th><th>İstem</th><th>Alternatifler</th></tr>{''.join(rows)}</table>")
        return head


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    f = Film(root); t = time.time()
    f.apply_fixes()
    log("1) GELENLER okunuyor...")
    new = f.ingest()
    log(f"   {len(new)} yeni dosya")
    if new:
        log("2) Ayıklanıyor (referanslar, yüklemeler)...")
        imgs, vids = f.classify(new)
        log(f"   {len(imgs)} sahne görseli adayı, {len(vids)} video")
        log("3) Görseller sahnelere eşleştiriliyor...")
        f.match_images(imgs)
        log("4) Videolar eşleştiriliyor...")
        f.match_videos(vids)
    f.save()
    head = f.reports(); f.save()
    log("\n" + head + f"Süre: {time.time() - t:.0f} sn\nRAPOR.html, RAPOR.txt ve EKSIKLER.txt hazır.")
    if "--sessiz" not in sys.argv:
        try: os.startfile(os.path.join(f.root, "RAPOR.html"))
        except Exception: pass


if __name__ == "__main__":
    main()
