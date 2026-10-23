"""FİLM — üretim hattının orkestratörü: aşamaları sırayla yürütür, kaldığı yerden devam eder.

Kullanım:
  python film.py <film_klasoru>                      hattı çalıştırır (biten aşamaları atlar)
  python film.py <film_klasoru> --durum              hangi aşama bitti, hangisi bekliyor
  python film.py <film_klasoru> --asama video        yalnız bu aşama (virgülle birden çok: gorsel,video)
  python film.py <film_klasoru> --sifirla kurgu      bu aşamayı (ve sonrakileri) yeniden yapılacak say
  python film.py <film_klasoru> --parti 1,2          yalnız bu partilerin sahneleri
  python film.py <film_klasoru> --saglayici sahte    bütün işler için bu sağlayıcı (sahte: ağsız/kredisiz deneme)
  python film.py <film_klasoru> --tam-otomatik       kredi harcayan aşamalarda onay sormaz (varsayılan: --onayli)

Sıra: önce kâğıt üstü kapılar (kredi yok), sonra kredi harcayan üretim, en sonda kurgu.
  senaryo → istem_denetim → gorsel → video → ses → muzik → kurgu
Durum film klasöründeki FILM_DURUM.json'da, kayıt FILM_KAYIT.txt'de tutulur. Bir aşamanın girdisi değişirse
(SAHNELER.json düzeltildi, bir NNN.jpg silindi) o aşama kendiliğinden yeniden çalışır; yalnız eksikler üretilir.
Sağlayıcı sırası AYARLAR/FILM_AYAR.json'dan okunur (yoksa: görsel/video flow, ses ai84).
Bir sağlayıcı kısıtlanırsa yalnız anahtar/ağ/kota/kredi durumunda sıradakine geçilir. Flow uyarısı (olağan dışı etkinlik),
doğrulama ya da nedeni bilinmeyen kısıtta başka servise GEÇİLMEZ: hat DURUR ve haber verir.
Çıkış kodu: 0 bitti · 2 durdu (senin bir şey yapman gerek) · 4 ortam/sürüm (SAHNELER.json v2) · 7 Flow uyarısı · 1 hata
"""
import os, sys, json, time, hashlib, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import saglayicilar as sg
from saglayicilar import Kisitlandi
import istem_denetim

AYAR_DOSYA = os.path.join(ROOT, "AYARLAR", "FILM_AYAR.json")
VARSAYILAN = {"saglayicilar": {"gorsel": ["flow"], "video": ["flow"], "ses": ["ai84"], "muzik": []}}


class Durdur(Exception):
    """Hat burada durur; kullanıcının yapacağı bir şey var (mesajda yazar). kod → çıkış kodu (CIKIS)."""
    def __init__(self, msg, kod="genel"):
        super().__init__(msg); self.kod = kod


# 7: Flow uyarısı (olağan dışı etkinlik) · 4: ortam/sürüm · 2: diğer duruşlar
CIKIS = {"olagandisi": 7, "kilitli": 7, "ortam": 4, "surum": 4}


def ayar():
    a = json.loads(json.dumps(VARSAYILAN))
    if os.path.exists(AYAR_DOSYA):
        a["saglayicilar"].update(json.load(open(AYAR_DOSYA, encoding="utf-8-sig")).get("saglayicilar", {}))
    return a


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p],
                       capture_output=True, text=True)
    try: return float(r.stdout.strip())
    except ValueError: return 0.0


def ts(x):
    h, m = int(x // 3600), int(x % 3600 // 60); s = x % 60
    return f"{h:02}:{m:02}:{int(s):02},{int(round((s % 1) * 1000)) % 1000:03}"


class Film:
    def __init__(self, kok, args):
        self.kok = os.path.abspath(kok); self.args = args
        self.durum_yol = os.path.join(self.kok, "FILM_DURUM.json")
        self.st = json.load(open(self.durum_yol, encoding="utf-8")) if os.path.exists(self.durum_yol) else {"asamalar": {}}
        self.ayar = ayar()
        if args.get("saglayici"): self.ayar["saglayicilar"] = {t: [args["saglayici"]] for t in sg.TURLER}
        self.d = {k: os.path.join(self.kok, v) for k, v in
                  dict(sg="SIRALI_GORSEL", sv="SIRALI_VIDEO", ses="SESLER", k="KURGU", rap="_RAPOR").items()}

    # ---- yardımcılar
    def log(self, *a):
        m = " ".join(str(x) for x in a); print(m, flush=True)
        with open(os.path.join(self.kok, "FILM_KAYIT.txt"), "a", encoding="utf-8") as f: f.write(time.strftime("%H:%M:%S ") + m + "\n")

    def kaydet(self):
        json.dump(self.st, open(self.durum_yol, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def plan(self):
        p = os.path.join(self.kok, "SAHNELER.json")
        if not os.path.exists(p): return None
        plan = json.load(open(p, encoding="utf-8-sig"))
        if int(plan.get("_surum", 1) or 1) >= 2:
            raise Durdur("SAHNELER.json v2 (_surum ≥ 2); bu film.py v1. Hiçbir şey yapılmadı.", kod="surum")
        return plan

    def sahneler(self):
        ss = sorted((self.plan() or {}).get("sahneler", []), key=lambda s: s["no"])
        if self.args.get("parti"): ss = [s for s in ss if s.get("parti") in self.args["parti"]]
        return ss

    def yol(self, tur, n): return os.path.join(self.d["sg"] if tur == "gorsel" else self.d["sv"], f"{n:03d}." + ("jpg" if tur == "gorsel" else "mp4"))

    def imza(self, *yollar):
        """Dosya içerikleri + klasör listeleri → kısa özet. Değişirse aşama yeniden çalışır."""
        h = hashlib.sha1()
        for p in yollar:
            if os.path.isfile(p): h.update(p.encode()); h.update(open(p, "rb").read())
            elif os.path.isdir(p):
                for f in sorted(os.listdir(p)):
                    q = os.path.join(p, f)
                    if os.path.isfile(q): h.update(f"{f}:{os.path.getsize(q)}:{int(os.path.getmtime(q))}".encode())
            else: h.update(f"{p}:yok".encode())
        h.update(json.dumps(self.args.get("parti")).encode())
        return h.hexdigest()[:16]

    def onay(self, ne, saglayicilar):
        if not any(s.kredili for s in saglayicilar) or self.args.get("tam_otomatik"): return
        try: c = input(f"\n>> {ne} kredi harcayacak ({', '.join(s.ad for s in saglayicilar)}). Devam edilsin mi? (e/h): ")
        except EOFError: c = ""
        if c.strip().lower() not in ("e", "evet", "y", "yes"): raise Durdur(f"{ne}: onay verilmedi. Hazır olunca yeniden çalıştır.")

    def uret(self, tur, gerek):
        """Eksik dosyaları sağlayıcı zinciriyle üretir. gerek(sahne) → bu sahne bu aşamada üretilecek mi."""
        os.makedirs(self.d["sg" if tur == "gorsel" else "sv"], exist_ok=True)
        eksik = lambda: [s for s in self.sahneler() if gerek(s) and not os.path.exists(self.yol(tur, s["no"]))]
        if not eksik(): self.log(f"   {tur}: eksik yok"); return
        zin = sg.zincir(tur, self.ayar["saglayicilar"].get(tur, []), self.log)
        if not zin: raise Durdur(f"{tur} için hazır sağlayıcı yok (AYARLAR/FILM_AYAR.json ya da --saglayici).")
        self.onay(f"{tur.upper()} aşaması ({len(eksik())} sahne)", zin)
        for s_ in zin:
            if not eksik(): break
            self.log(f"   {tur}: {len(eksik())} sahne → [{s_.ad}]")
            try:
                if s_.toplu_mu: s_.toplu(self.kok, tur, eksik()); continue
                for s in eksik():
                    n = s["no"]; out = self.yol(tur, n); tmp = out[:-4] + ".part" + out[-4:]
                    if tur == "gorsel": s_.gorsel(self.kok, s, tmp)
                    else: s_.video(self.kok, s, self.yol("gorsel", n), tmp)
                    os.replace(tmp, out); self.log(f"     {n:03d} ✓")
            except Kisitlandi as e:
                if not e.gecilebilir:      # uyarı/doğrulama/bilinmeyen: başka servise geçmek atlatmadır → hat durur
                    raise Durdur(f"[{s_.ad}] {e.kod}: {e} Başka sağlayıcıya geçilmedi.", kod=e.kod)
                self.log(f"   [{s_.ad}] KISITLANDI ({e.kod}): {e} → sıradaki sağlayıcı")
        kalan = eksik()
        if kalan: raise Durdur(f"{tur}: {len(kalan)} sahne üretilemedi ({', '.join(str(s['no']) for s in kalan[:15])}).")

    # ---- aşamalar: (ad, kredili_mi, girdiler, iş)
    def a_senaryo(self):
        p = self.plan()
        if not p or not p.get("sahneler"):
            raise Durdur("SAHNELER.json yok ya da boş. Senaryo aşaması (Claude API) henüz kodlanmadı: "
                         "şimdilik senaryoyu Claude ile yazıp SAHNELER.json'a koy.")
        self.log(f"   {len(p['sahneler'])} sahne, {len(p.get('karakterler') or {})} karakter")

    def a_istem_denetim(self):
        b, ozet = istem_denetim.rapor(self.kok)
        for sv, n, m in b: self.log(f"   {sv:5} {'S%03d' % n if n is not None else 'GENEL'}  {m}")
        self.log("   " + ozet)
        if any(x[0] == "HATA" for x in b): raise Durdur("İstem denetiminde HATA var: _RAPOR/ISTEM_DENETIM.txt. Düzelt, yeniden çalıştır.")

    def a_gorsel(self):
        self.uret("gorsel", lambda s: True)

    def a_video(self):
        yok = [s["no"] for s in self.sahneler() if not os.path.exists(self.yol("gorsel", s["no"]))]
        if yok: raise Durdur(f"Görseli olmayan sahneler var: {yok}")
        disari = [s["no"] for s in self.sahneler() if s.get("motor", "flow") != "flow" and not os.path.exists(self.yol("video", s["no"]))]
        if disari: self.log(f"   motor flow dışı, elle gelecek (SIRALI_VIDEO'ya koy): {disari}")
        self.uret("video", lambda s: s.get("motor", "flow") == "flow")

    def a_ses(self):
        replikli = [s for s in self.sahneler() if s.get("replik")]
        if not replikli: self.log("   replikli sahne yok"); return
        zin = sg.zincir("ses", self.ayar["saglayicilar"].get("ses", []), self.log)
        if not zin: self.log("   ses sağlayıcısı yok → Flow'un kendi sesi kalır"); return
        self.onay(f"SES aşaması ({len(replikli)} replik)", zin)
        if zin[0].ad == "ai84":   # gerçek yol: whisper + demucs ile dudağa oturtma seslendir.py'de
            r = subprocess.run([sys.executable, os.path.join(HERE, "seslendir.py"), self.kok])
            if r.returncode: raise Durdur("seslendir.py hata verdi.")
            return
        os.makedirs(self.d["ses"], exist_ok=True)
        kar = self.plan().get("karakterler") or {}; dlg = {}
        for s in replikli:
            n = s["no"]; rep = s["replik"]; t = 0.8; out = []
            cumleler = rep.get("cumleler") or [{"en": rep["metin"], "tr": ""}]
            for j, c in enumerate(cumleler):
                p = os.path.join(self.d["ses"], f"{n:03d}_c{j}.wav")
                sure = zin[0].ses(self.kok, c["en"], (kar.get(rep["karakter"]) or {}).get("ses"), p)
                out.append({"dosya": os.path.basename(p), "bas": round(t, 3), "sure": round(sure, 3),
                            "en": c["en"], "tr": c.get("tr", ""), "kaynak": zin[0].ad})
                t += sure + 0.25
            dlg[str(n)] = {"ortam": None, "cumleler": out}
            self.log(f"   {n:03d}: {len(out)} cümle")
        json.dump(dlg, open(os.path.join(self.d["ses"], "diyalog.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    def a_muzik(self):
        zin = sg.zincir("muzik", self.ayar["saglayicilar"].get("muzik", []), self.log)
        if not zin: self.log("   müzik sağlayıcısı yok → kurguda geçici müzik kullanılır"); return
        os.makedirs(self.d["k"], exist_ok=True)
        toplam = sum(dur(self.yol("video", s["no"])) for s in self.sahneler() if os.path.exists(self.yol("video", s["no"])))
        self.onay("MÜZİK aşaması", zin)
        zin[0].muzik(self.kok, toplam, os.path.join(self.d["k"], "muzik.wav"))

    def a_kurgu(self):
        try:
            import pycapcut  # noqa: F401
            capcut = os.path.isdir(os.path.join(os.environ.get("LOCALAPPDATA", ""), "CapCut", "User Data", "Projects", "com.lveditor.draft"))
        except ImportError: capcut = False
        if capcut and not self.args.get("saglayici") == "sahte":
            r = subprocess.run([sys.executable, os.path.join(HERE, "capcut_film.py"), self.kok])
            if r.returncode: raise Durdur("capcut_film.py hata verdi.")
            return
        # CapCut yoksa (ya da deneme): ffmpeg ile izlenebilir önizleme + altyazı
        self.log("   CapCut yok → ffmpeg önizlemesi (KURGU/onizleme.mp4)")
        os.makedirs(self.d["k"], exist_ok=True)
        klipler = [(s["no"], self.yol("video", s["no"])) for s in self.sahneler() if os.path.exists(self.yol("video", s["no"]))]
        if not klipler: raise Durdur("Kurgu için video yok.")
        dlg_p = os.path.join(self.d["ses"], "diyalog.json")
        dlg = json.load(open(dlg_p, encoding="utf-8")) if os.path.exists(dlg_p) else {}
        cmd = ["ffmpeg", "-v", "error", "-y"]
        for _, p in klipler: cmd += ["-i", p]
        fc = "".join(f"[{i}:v]scale=1280:720,setsar=1,fps=24[v{i}];[{i}:a]aresample=44100,aformat=channel_layouts=stereo[a{i}];"
                     for i in range(len(klipler)))
        fc += "".join(f"[v{i}][a{i}]" for i in range(len(klipler))) + f"concat=n={len(klipler)}:v=1:a=1[v][a]"
        out = os.path.join(self.d["k"], "onizleme.mp4")
        subprocess.run(cmd + ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "veryfast",
                              "-pix_fmt", "yuv420p", "-c:a", "aac", out], check=True)
        t, sub = 0.0, []
        for n, p in klipler:
            for c in dlg.get(str(n), {}).get("cumleler", []): sub.append((t + c["bas"], t + c["bas"] + c["sure"] + 0.3, c["en"]))
            t += dur(p)
        if sub:
            with open(os.path.join(self.d["k"], "altyazi_en.srt"), "w", encoding="utf-8") as f:
                for i, (a, b, x) in enumerate(sub, 1): f.write(f"{i}\n{ts(a)} --> {ts(b)}\n{x}\n\n")
        self.log(f"   {len(klipler)} klip, {t:.1f} sn → {out}")

    def asamalar(self):
        sp = os.path.join(self.kok, "SAHNELER.json")
        return [
            ("senaryo", self.a_senaryo, lambda: self.imza(sp)),
            ("istem_denetim", self.a_istem_denetim, lambda: self.imza(sp, os.path.join(self.kok, "01_KARAKTERLER"))),
            ("gorsel", self.a_gorsel, lambda: self.imza(sp, self.d["sg"])),
            ("video", self.a_video, lambda: self.imza(sp, self.d["sg"], self.d["sv"])),
            ("ses", self.a_ses, lambda: self.imza(sp, self.d["sv"])),
            ("muzik", self.a_muzik, lambda: self.imza(self.d["sv"])),
            ("kurgu", self.a_kurgu, lambda: self.imza(sp, self.d["sv"], self.d["ses"], os.path.join(self.d["k"], "muzik.wav"))),
        ]

    # ---- yürütme
    def durum(self):
        for ad, _, imza in self.asamalar():
            k = self.st["asamalar"].get(ad)
            if not k: d = "bekliyor"
            elif k.get("imza") != imza(): d = f"yeniden yapılacak (girdi değişti; son: {k['zaman']})"
            else: d = f"tamam ({k['zaman']})"
            print(f"  {ad:14} {d}")

    def sifirla(self, ad):
        adlar = [a for a, _, _ in self.asamalar()]
        if ad not in adlar: raise SystemExit(f"Bilinmeyen aşama: {ad} ({', '.join(adlar)})")
        for a in adlar[adlar.index(ad):]: self.st["asamalar"].pop(a, None)
        self.kaydet(); print(f"{ad} ve sonrası yeniden yapılacak.")

    def calis(self):
        secili = self.args.get("asama")
        self.log(f"\n=== FİLM: {os.path.basename(self.kok)} · {time.strftime('%Y-%m-%d %H:%M')} ===")
        for ad, is_, imza in self.asamalar():
            if secili and ad not in secili: continue
            k = self.st["asamalar"].get(ad)
            if not secili and k and k.get("imza") == imza():
                self.log(f"[{ad}] tamam, atlandı"); continue
            self.log(f"[{ad}]")
            is_()
            self.st["asamalar"][ad] = {"zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "imza": imza()}
            self.kaydet()
        self.log("=== HAT BİTTİ ===")


def argumanlar(a):
    args = {"tam_otomatik": "--tam-otomatik" in a}
    for k in ("--asama", "--parti", "--saglayici", "--sifirla"):
        if k in a:
            v = a[a.index(k) + 1]
            args[k[2:]] = [int(x) for x in v.split(",")] if k == "--parti" else v.split(",") if k == "--asama" else v
    return args


def main(a=None):
    a = sys.argv[1:] if a is None else a
    if not a or a[0].startswith("-"): print(__doc__); return 0
    f = Film(a[0], argumanlar(a))
    if "--durum" in a: f.durum(); return 0
    if f.args.get("sifirla"): f.sifirla(f.args["sifirla"]); return 0
    try:
        f.calis(); return 0
    except Durdur as e:
        f.log(f"!! DURDU: {e}"); return CIKIS.get(e.kod, 2)
    except KeyboardInterrupt:
        f.log("Kullanıcı durdurdu."); return 2


if __name__ == "__main__":
    sys.exit(main())
