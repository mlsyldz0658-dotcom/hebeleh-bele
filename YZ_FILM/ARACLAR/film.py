"""FİLM — üretim hattının orkestratörü. v2: görev defteri (TASARIM §1.1, §5.5, §6.1). v1 komutları aynen çalışır.

Kullanım (v2, görev defteri; ana Claude yalnız .claude/bin/film.py üzerinden çağırır):
  python film.py yeni --konu "<cümle>" [--ad F2026_ejderha] [--seri SERI] [--saglayici sahte]   yeni film (A00)
  python film.py sonraki [--film <ad|yol>]          sıradaki paralel grubu tek JSON olarak verir (≤ 1.200 karakter)
  python film.py basla <id,id,…>                    görevleri "calisiyor" yapar (ajan görevinde kanca nabzı şart)
  python film.py calis <id> [--topla]               betik görevini çalıştırır (sahte filmde ajan/kullanıcı görevini de taklit eder)
  python film.py bitir <id> [--kullanim '<json>']   ajan görevinin CIKTI'sını doğrular, taşır, "bitti" yapar (SubagentStop kancası)
  python film.py kurtar [--yeniden-kur]             kesilmeden sonra: bayat kilit, yarım görevler; FILM_DURUM'u yeniden kurar
  python film.py asama-ilerlet <id>                 aşamalı okumada sonraki bölümü görevin GIRDI'sine koyar
  python film.py bekle --kullanici <id> | --blok <B> [--kez N] [--aralik sn] [--sure dk]
                                                     kullanıcı eserini yoklar (ZIP, blok sonu, dışa aktarım); 6 saatte bir hatırlatır
  python film.py karar ekle "karar — neden — yanlışsa maliyeti" [--asama A04] [--kaynak betik:puan_oku] [--tur karar]
  python film.py ders ekle --kapi G1 --belirti "…" [--olay kapi_hatasi] [--kaynak kullanici_notu] [--plan 41]
  python film.py goster durum|asama <kod>|gorev <id>|plan <no>|maliyet|token|neden-durdu|ayar|sozlesme|karar|plan-imza|pencere <uygulama>
  python film.py ozet [--kisa | --uzun | --kullanici] [--json]          her zaman 0 ile çıkar
  python film.py surus ac | kapat [--soru | --gelistirme]
  python film.py notlar oku | isle                   kullanıcı notları (salt okunur) / not turunu (A16n) açar
  python film.py beceri-denetim · olcum0 · asamalar --md|--json · esitle --gelistirme [...] · esitle (tam: P2)
  Ortak seçenekler: --film <ad|yol> (yoksa FILMLER/_AKTIF.json) · --json (makine çıktısı)

Kullanım (v1, eski SAHNELER.json; davranış korunur):
  python film.py <film_klasoru> [--durum] [--asama video] [--sifirla kurgu] [--parti 1,2] [--saglayici sahte] [--tam-otomatik]
  Sıra: senaryo → istem_denetim → gorsel → video → ses → muzik → kurgu. Durum FILM_DURUM.json'da (v1 biçimi), kayıt FILM_KAYIT.txt'de.
  Kredi onayı soru sormaz: --tam-otomatik ya da FILM_AYAR.json "mod": "tam_otomatik"; yoksa 5 BÜTÇE ile durur.
  Flow uyarısı (olağan dışı etkinlik), doğrulama ya da nedeni bilinmeyen kısıtta başka servise GEÇİLMEZ: hat DURUR.

Görev defteri: <film>/_GOREV/<id>/{GOREV.json, ISTEM.md, GIRDI/, CIKTI/}. Durumun kaynağı görev dosyalarıdır (atomik yazım);
FILM_DURUM.json yalnız önbellektir, her komut onu görev ve rapor dosyalarından yeniden türetir. Değişiklikler FILM.kilit altında yapılır.
Aşamalar hat/asamalar.py'den gelir (A00–A18a); tur tavanı dolunca §1.5 merdiveninin sonraki basamağı görev olarak açılır, 6 KAPI
yalnız merdiven tükenip kapı HATA'sı sürdüğünde verilir. Kredili betik görevinde gönderim kaydı çalıştırmadan ÖNCE yazılır; kesilen
kredili görev kör yeniden gönderilmez, önce toplanır (calis --topla). Disk, token ve görev sayısı kapıları her aşama başında (8 BEKLE).
Bulutta (D-45) film yalnız --saglayici sahte ile açılır; konu sorulmaz.
Betik sözleşmesi: calis, aracı "python <ARACLAR>/<arac> <alt komut ve seçenekler> --film <film>" diye çağırır (YZ_FILM_GOREV ortam
değişkeni görev klasörüdür); araç kapı raporunu _uretim.gorev = görev kimliğiyle yazar, 0–8 çıkış kodlarıyla döner. Araç henüz yoksa 4.

Çıkış kodları: 0 BİTTİ/devam · 1 HATA · 2 KULLANICI (fiziksel iş) · 3 AJAN (ajan görevi var) · 4 ORTAM · 5 BÜTÇE · 6 KAPI
               (merdiven tükendi) · 7 KISIT (Flow uyarısı/kilidi) · 8 BEKLE (çalışan iş, disk, token, kilit, bekleme)
"""
import os, sys, json, time, hashlib, subprocess
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import saglayicilar as sg
from saglayicilar import Kisitlandi
import istem_denetim
import ortak


def ayar_dosyasi(): return os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json")   # <veri>/AYARLAR
VARSAYILAN = {"saglayicilar": {"gorsel": ["flow"], "video": ["flow"], "ses": ["ai84"], "muzik": []}}


class Durdur(Exception):
    """Hat burada durur; kullanıcının yapacağı bir şey var (mesajda yazar). kod → çıkış kodu (CIKIS)."""
    def __init__(self, msg, kod="genel"):
        super().__init__(msg); self.kod = kod


# 7: Flow uyarısı (olağan dışı etkinlik) · 4: ortam/sürüm · 5: kredi onayı yok · 2: diğer duruşlar
CIKIS = {"olagandisi": 7, "kilitli": 7, "ortam": 4, "surum": 4, "butce": 5}


def ayar():
    a = json.loads(json.dumps(VARSAYILAN))
    p = ayar_dosyasi()
    if os.path.exists(p):
        a["saglayicilar"].update(json.load(open(p, encoding="utf-8-sig")).get("saglayicilar", {}))
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
        """Kredi onayı soru sormaz (input() kalktı, TASARIM §6.1): onay ya --tam-otomatik ile ya FILM_AYAR.json "mod":
        "tam_otomatik" ile verilmiştir; değilse hat 5 BÜTÇE ile durur. v2 filmlerde kredi görev defterinin bütçe noktasından geçer."""
        if not any(s.kredili for s in saglayicilar) or self.args.get("tam_otomatik"): return
        if (ortak.json_oku(ayar_dosyasi(), {}) or {}).get("mod") == "tam_otomatik": return
        raise Durdur(f"{ne} kredi harcayacak ({', '.join(s.ad for s in saglayicilar)}); kredi onayı yok. "
                     "Onay görev defterinden verilir (film.py v2 bütçe noktası) ya da --tam-otomatik ile. Hiçbir şey harcanmadı.",
                     kod="butce")

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
            capcut = os.path.isdir(ortak.yollar()["capcut_taslak"])
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




# =====================================================================================================================
# v2 — görev defteri (TASARIM §1.1, §1.5, §5.5, §6.1). Durumun kaynağı _GOREV/<id>/GOREV.json dosyalarıdır.
# =====================================================================================================================
import re, glob, fnmatch, shutil, datetime, random
from hat import asamalar as HAT


def _istege_bagli_modul(ad):
    """Komşu PR-2 araçları (kredi, flow_yuk, ders_defteri): yoksa ya da açılmazsa None; film.py kendi yedek yoluyla sürer."""
    try: return __import__(ad)
    except Exception: return None


kredi_mod, flow_yuk_mod, ders_defteri_mod = (_istege_bagli_modul(x) for x in ("kredi", "flow_yuk", "ders_defteri"))

SURUM_V2 = "film 2.0"
BITTI, HATA, KULLANICI, AJAN, ORTAM, BUTCE, KAPI, KISIT, BEKLE = range(9)
MODEL = "claude-opus-5-5"
SONUC_GECER = ("GEC", "BAYRAK", "OLCULEMEDI")
YENILENIR = ("kesildi", "gecersiz", "model_sapmasi")
ACIK = ("hazir", "calisiyor")
KAPI_TURLU = ("ayni_sahip", "ust_sahip")
SIRALI_CIFT = {("A07b", "YP")}                                              # O-12 sıralı çift (dilim.py "bagimli")
VIDEO_ASAMALARI = ("A13", "A14a", "A14")                                   # animatik ONAYLI imzası olmadan açılmaz
KURESEL_TAVAN = {"animatik_kurgu_tur": 8, "h15": 2, "kart_tarif": 2}     # §1.5 küresel geri dönüş bütçesi
KANCA_NABZI_MAX_SN = 15                                                    # §4.5.8 (tahmin)
KILIT_BAYAT_SN = 300
DENEME_MAX = 3
SONRAKI_MAX_KR = 1200
TEK_SORU = ("Filmin konusu ne olsun? Bir cümle yeter (ör. ejderha yavrusunu saklayan avcı kadın). "
            "İstersen 'sen seç' yaz.")
BULUT_CUMLESI = "Film seti senin bilgisayarında çalışır: Masaüstündeki FILM_SETI.bat'a çift tıkla ve konuyu orada yaz."
SOZLUKLER = {"yonetmen": ("plan_sozlukleri.json", "fiil_sozlugu.json", "ifade_sozlugu.json"),      # veri/ → GIRDI (6a #4)
             "ses-tasarimcisi": ("efekt_sozlugu.json", "aksan_sozlugu.json"), "yapimci": ("tur_kanca.json",)}
ESIK_VARSAYILAN = {"disk_bos_min_gb": 20, "gorev_tavani_carpan": 1.5, "film_token_tavan": None, "ajan_paralel_max": 5,
                   "bekle_azami_dk": 110, "stop_ardisik_max": 8}
uyu = time.sleep          # testler gerçek bekleme yapmasın diye tek nokta


class Hata(Exception):
    """v2 komutunun düz Türkçe hata cümlesi + çıkış kodu."""
    def __init__(self, msg, kod=HATA, **ek):
        super().__init__(msg); self.kod = kod; self.ek = ek


def _kesme(ad):
    """Kesme noktası (test_gorev_defteri burayı yamalar; üretimde hiçbir şey yapmaz)."""


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def _zaman_oku(s):
    try: return datetime.datetime.fromisoformat(s).timestamp()
    except (TypeError, ValueError): return None


_ESIK = None


def esik(ad):
    global _ESIK
    if _ESIK is None:
        try:
            import esikler
            _ESIK = dict(esikler.yukle())
        except Exception:      # eşik dosyası bozuksa varsayılanla sürer; esikler.py kendi testinde HATA verir
            _ESIK = {}
    return _ESIK.get(ad, ESIK_VARSAYILAN.get(ad))


_ADLAR = None
_OLCEK = []


def _olcek_tahmin():
    """olcek.py (kredi/ölçek ajanının dosyası) varsa onun gorev_tahmini(asama, film) işlevi; yoksa None."""
    if not _OLCEK:
        try:
            import olcek
            _OLCEK.append(getattr(olcek, "gorev_tahmini", None))
        except Exception: _OLCEK.append(None)
    return _OLCEK[0]


def adlar():
    global _ADLAR
    if _ADLAR is None: _ADLAR = ortak.json_oku(os.path.join(HERE, "veri", "ADLAR.json"), {}) or {}
    return _ADLAR


def ortam():
    """yerel | bulut. Sıra: YZ_FILM_ORTAM → FILM_AYAR.json "ortam" → Windows ise yerel, değilse bulut."""
    v = os.environ.get("YZ_FILM_ORTAM")
    if v in ("yerel", "bulut"): return v
    try: a = ortak.json_oku(ayar_dosyasi(), {}) or {}
    except ortak.YolYok: a = {}
    if a.get("ortam") in ("yerel", "bulut"): return a["ortam"]
    return "yerel" if os.name == "nt" else "bulut"


def flow_kilitli():
    """Hesap düzeyi Flow kilidi (sahibi flow_yuk.py; dosya varken kilitli). flow_yuk yoksa ya da hata verirse dosyanın varlığı."""
    try:
        return bool(flow_yuk_mod.kilit_durumu().get("kilitli"))
    except Exception:
        try: return os.path.exists(os.path.join(ortak.yollar()["hesap"], "FLOW_KILIDI.json"))
        except ortak.YolYok: return True              # yol bilinmiyorsa kapalı başarısız


def disk_bos_gb(yol):
    p = os.path.abspath(yol)
    while not os.path.exists(p) and os.path.dirname(p) != p: p = os.path.dirname(p)
    try: return shutil.disk_usage(p).free / 1e9
    except OSError: return float("inf")


def jsonl_ekle(yol, kayit):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "a", encoding="utf-8") as f:
        f.write(json.dumps(kayit, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())


def jsonl_oku(yol):
    out = []
    try:
        with open(yol, encoding="utf-8") as f:
            for satir in f:
                try: out.append(json.loads(satir))
                except ValueError: pass          # yarım son satır atlanır
    except OSError: pass
    return out


def _pid_yasiyor(pid):
    if os.name == "nt": return True               # Windows'ta yalnız yaş ölçütü
    try: os.kill(pid, 0); return True
    except ProcessLookupError: return False
    except (PermissionError, OSError): return True


_TUTULAN = set()


class Kilit:
    """FILM.kilit: film başına tek yazar. Aynı süreç içinde yeniden girilebilir. Süreç ölürse (kesme) kilit dosyası kalır;
    sahibi ölmüşse, kendi pid'imizse (pid yeniden kullanımı) ya da KILIT_BAYAT_SN'den eskiyse bayattır ve kaldırılır."""
    def __init__(self, kok, bekle_sn=3.0, zorla=False):
        self.p = os.path.join(kok, "FILM.kilit"); self.bekle_sn = bekle_sn; self.zorla = zorla; self.ic = False
        self.jeton = "%x" % random.getrandbits(48)

    def bayat(self):
        try:
            with open(self.p, encoding="utf-8") as f: k = json.load(f)
        except (OSError, ValueError):
            try: return time.time() - os.path.getmtime(self.p) > 2
            except OSError: return True
        if self.zorla: return True
        pid = k.get("pid")
        return (pid == os.getpid() or not isinstance(pid, int) or not _pid_yasiyor(pid)
                or time.time() - float(k.get("zaman", 0)) > KILIT_BAYAT_SN)

    def __enter__(self):
        if self.p in _TUTULAN: self.ic = True; return self
        t0 = time.time()
        while True:
            try:
                fd = os.open(self.p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    json.dump({"pid": os.getpid(), "zaman": time.time(), "jeton": self.jeton}, f)
                _TUTULAN.add(self.p); return self
            except FileExistsError:
                if self.bayat():
                    try: os.remove(self.p)
                    except OSError: pass
                    continue
                if time.time() - t0 > self.bekle_sn:
                    raise Hata("Başka bir film.py işlemi sürüyor (FILM.kilit). Biraz sonra yeniden dene; takılı kaldıysa: film.py kurtar.",
                               BEKLE)
                time.sleep(0.1)

    def __exit__(self, et, e, tb):
        if self.ic: return False
        _TUTULAN.discard(self.p)
        if et is None or issubclass(et, Exception):       # BaseException (süreç ölümü taklidi) kilidi bırakmaz
            try:
                with open(self.p, encoding="utf-8") as f:
                    if json.load(f).get("jeton") == self.jeton: os.remove(self.p)
            except (OSError, ValueError): pass
        return False


def _kopyala(kaynak, hedef):
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    tmp = hedef + ".tmp"
    shutil.copyfile(kaynak, tmp); os.replace(tmp, hedef)


def _bayt(yol):
    with open(yol, "rb") as f: return f.read()


def _metin_yaz(yol, metin):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: f.write(metin); f.flush(); os.fsync(f.fileno())
    os.replace(tmp, yol)


def _sonuc(x):
    x = str(x or "").upper().replace("Ç", "C").replace("İ", "I").replace("Ü", "U").replace("Ö", "O").replace("Ş", "S")
    return {"GECTI": "GEC", "HATALI": "HATA", "OLCULEMEDI": "OLCULEMEDI"}.get(x, x)


def _desen(s): return re.sub(r"\{[^}]*\}|<[^>]*>|NNN", "*", s.replace("{tur100}", "1[0-9][0-9]"))


def _surum_no(p):
    m = re.search(r"(\d+)(?=\.[^.]+$)", os.path.basename(p))
    return int(m.group(1)) if m else -1


def girdi_cozumle(kok, rel):
    """Görev girdisi → [(film klasöründeki yol, GIRDI'deki göreli ad)]. Biçimler: dosya · glob deseni (her eşleşme) ·
    "son:<desen>" (en büyük sürüm numaralı tek dosya; ör. 06_SENARYO_v*.json) · "/" ile biten klasör (içeriği GIRDI/'ye)."""
    son = rel.startswith("son:")
    if son: rel = rel[4:]
    p = os.path.join(kok, rel)
    if rel.endswith("/"): return [(p, "")] if os.path.isdir(p) else []
    if any(c in rel for c in "*?["):
        es = sorted(x for x in glob.glob(p) if os.path.isfile(x) and not x.endswith(".tmp"))
        if son: es = sorted(es, key=lambda x: (_surum_no(x), x))[-1:]
        return [(x, os.path.basename(x)) for x in es]
    return [(p, os.path.basename(p))] if os.path.isfile(p) else []


def _yazi_duz(s):
    t = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")
    return re.sub(r"[^a-z0-9]+", "_", s.translate(t).lower()).strip("_")


def plan_imzalari(plan):
    """SAHNELER.json → {plan_no: imza}. v1 'sahneler' ve v2 'planlar' (sahne gruplarının içindekiler dahil) listelerini okur;
    üretim alanları (_uretim, uretim, durum) imzaya girmez. Bir planın imzası değişirse o planın kredili çıktısı bayattır."""
    if not isinstance(plan, dict): return {}
    ogeler = list(plan.get("sahneler") or []) + list(plan.get("planlar") or [])
    for g in (plan.get("sahne_gruplari") or {}).values():
        if isinstance(g, dict): ogeler += list(g.get("planlar") or [])
    out = {}
    for o in ogeler:
        if not isinstance(o, dict): continue
        no = o.get("no", o.get("id"))
        if no is None: continue
        temiz = {k: v for k, v in o.items() if k not in ("_uretim", "uretim", "durum")}
        out[str(no)] = hashlib.sha1(json.dumps(temiz, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]
    return out


def tur_sablonlari(a, tur_no, merdiven):
    """Bir turun (grup, şablon) listesi. Merdiven turunda başta basamağın ajanı (grup -1) vardır; kapısız basamakta yalnız o."""
    out = []
    if isinstance(merdiven, str) and merdiven.startswith("kapanis:"):
        # kapanış turu (§1.5 basamak 3/5: hat sürer): kapının düştüğü gruptan sonraki "hepsi" grupları bir kez koşar
        g0 = int(merdiven.split(":")[1])
        return [(s.grup, s) for s in a.gorevler if s.turda == "hepsi" and s.grup > g0]
    if merdiven is not None:
        b = a.tavan_sonrasi[merdiven]
        if b.ajan:
            out.append((-1, HAT.GorevSablonu(kod="MB", tur="ajan", grup=-1, ajan=b.ajan, kip=b.kip, cikti=("CIKTI/rapor.json",),
                                              tasima=(("CIKTI/rapor.json", "_RAPOR/MERDIVEN_%s_t{tur}.json" % a.kod),))))
        if b.tur not in KAPI_TURLU: return out
    for s in a.gorevler:
        if s.turda == "ilk" and (tur_no > 1 or merdiven is not None): continue
        if s.turda == "sonra" and tur_no == 1 and merdiven is None: continue
        out.append((s.grup, s))
    return out


_IMZA_DOSYA = {}


def imza_dosyalari(a):
    """Aşamanın girdi imzasına giren dosyalar: kendisinin ya da sonraki bir aşamanın da yazdığı dosyalar dışarıda kalır
    (A09 SAHNELER.json'a hareket istemi yazınca A08 bayat sayılmaz)."""
    if a.kod in _IMZA_DOSYA: return _IMZA_DOSYA[a.kod]
    i = HAT.sira(a.kod); desenler = []
    for b in HAT.ASAMALAR[i:]:
        desenler += [_desen(c) for c in b.ciktilar]
        for s in b.gorevler:
            desenler += [_desen(c) for c in s.cikti if not c.startswith("CIKTI/")] + [_desen(d) for _, d in s.tasima]
    out = []
    for g in a.girdiler:
        if not g.dosya: continue
        d = g.dosya.rstrip("/")
        if any(fnmatch.fnmatch(d, x) or x.startswith(d + "/") for x in desenler): continue
        out.append(d)
    _IMZA_DOSYA[a.kod] = out
    return out


class Defter:
    """Bir filmin görev defteri."""
    def __init__(self, kok):
        self.kok = os.path.abspath(kok); self.gd = os.path.join(self.kok, "_GOREV"); self._g = None

    # ---- temel
    def yol(self, *p): return os.path.join(self.kok, *p)
    def meta(self): return ortak.json_oku(self.yol("HAZIRLIK.json"), {}) or {}
    @property
    def sahte(self): return self.meta().get("saglayici") == "sahte"
    @property
    def kaset(self): return self.meta().get("saglayici") == "kaset"     # test kipi: kayıttan oynatma (D-41, §6.10)
    @property
    def deneme(self): return self.sahte or self.kaset
    @property
    def ad(self): return self.meta().get("film") or os.path.basename(self.kok)
    def kilit(self, **k): return Kilit(self.kok, **k)

    def log(self, m):
        os.makedirs(self.kok, exist_ok=True)
        with open(self.yol("FILM_KAYIT.txt"), "a", encoding="utf-8") as f: f.write(time.strftime("%Y-%m-%d %H:%M:%S ") + m + "\n")

    def olay(self, olay, **k): jsonl_ekle(os.path.join(self.gd, "DEFTER.jsonl"), dict(zaman=simdi(), olay=olay, **k))

    def gorevler(self):
        if self._g is None:
            self._g = {}
            if os.path.isdir(self.gd):
                for d in sorted(os.listdir(self.gd)):
                    g = ortak.json_oku(os.path.join(self.gd, d, "GOREV.json"))
                    if isinstance(g, dict) and g.get("id") == d: self._g[d] = g
        return self._g

    def g(self, gid):
        g = self.gorevler().get(gid)
        if not g: raise Hata(f"Görev yok: {gid}")
        return g

    def yeniden_oku(self): self._g = None

    def yaz(self, g):
        ortak.atomik_yaz(os.path.join(self.gd, g["id"], "GOREV.json"), g)
        self.gorevler()[g["id"]] = g

    def gorev_dizini(self, g): return os.path.join(self.gd, g["id"])

    def asama_gorevleri(self, kod): return [g for g in self.gorevler().values() if g.get("asama") == kod]

    # ---- yardımcı hesaplar
    def adet(self, a):
        if isinstance(a, int): return a
        self._adet = getattr(self, "_adet", None) or {}
        if a not in self._adet: self._adet[a] = self._adet_coz(a)
        return self._adet[a]

    def _adet_coz(self, a):
        h = ortak.json_oku(self.yol("HIKAYE.json"), {}) or {}
        n = 0
        if a == "parti": n = len(h.get("partiler") or [])
        elif a == "karakter":                         # A05'te HIKAYE.json yok: önce en son senaryo sürümü (06_SENARYO_v<N>)
            sn = girdi_cozumle(self.kok, "son:_HIKAYE_ODASI/06_SENARYO_v*.json")
            kaynak = (ortak.json_oku(sn[0][0], {}) or {}) if sn else {}
            n = min(8, len(kaynak.get("karakterler") or h.get("karakterler") or {}))
        elif a == "sahne_grubu": n = len((ortak.json_oku(self.yol("_YONETMEN", "DILIM.json"), {}) or {}).get("gruplar") or [])
        elif a == "blok": n = len((ortak.json_oku(self.yol("BLOK_PLANI.json"), {}) or {}).get("bloklar") or [])
        elif a == "gorsel_grubu":
            n = -(-len(glob.glob(self.yol("SIRALI_GORSEL", "_ADAYLAR", "*.jpg"))) // 12)
        return n or {"parti": 3, "sahne_grubu": 2, "karakter": 2, "blok": 1, "gorsel_grubu": 1}[a]

    def dosya_imza(self, rels):
        h = hashlib.sha1()
        for r in rels:
            if r.startswith("son:") or any(c in r for c in "*?["):
                es = girdi_cozumle(self.kok, r)
                h.update((r + ":" + str(len(es))).encode())
                for q, _ in es: h.update(os.path.relpath(q, self.kok).encode()); h.update(_bayt(q))
                continue
            p = self.yol(r)
            if os.path.isfile(p):
                h.update(r.encode()); h.update(_bayt(p))
            elif os.path.isdir(p):
                for kok, ds, fs in os.walk(p):
                    ds.sort()
                    for f in sorted(fs):
                        if f.endswith(".tmp"): continue
                        q = os.path.join(kok, f); h.update(os.path.relpath(q, self.kok).encode()); h.update(_bayt(q))
            else: h.update((r + ":yok").encode())
        return h.hexdigest()[:16]

    def asama_imza(self, a): return self.dosya_imza(imza_dosyalari(a))

    def surum_imzasi(self, gs):
        ilk = min(gs, key=lambda g: (g.get("zaman", {}).get("olusturma") or "", g["id"]))
        return ilk.get("asama_imza")

    def atlanir(self, a): return not a.bulutta_test and (self.sahte or (self.kaset and ortam() == "bulut"))

    # ---- küresel bütçe
    def kuresel_kullanim(self):
        normal, basamak = set(), {}
        for g in self.gorevler().values():
            try: a = HAT.asama(g["asama"])
            except KeyError: continue
            t = (g["asama"], g.get("surum"), g.get("tur_no"))
            if g.get("merdiven") is None:
                if a.butce: normal.add((a.butce,) + t)
            elif isinstance(g["merdiven"], int):
                b = a.tavan_sonrasi[g["merdiven"]]
                if b.butce: basamak.setdefault(b.butce, set()).add(t)
        k = {ad: 0 for ad in KURESEL_TAVAN}
        for x in normal: k[x[0]] = k.get(x[0], 0) + 1
        for ad, s in basamak.items(): k[ad] = k.get(ad, 0) + len(s)
        return k

    def butce_var(self, ad): return ad is None or self.kuresel_kullanim().get(ad, 0) < KURESEL_TAVAN.get(ad, 10 ** 9)

    # ---- aşama çözümü (türetme)
    def tavan_raporu(self, a, surum):
        r = ortak.json_oku(self.yol("_RAPOR", f"TAVAN_{a.kod}_s{surum}.json"))
        return r if isinstance(r, dict) and r.get("asama") == a.kod and r.get("surum") == surum else None

    def kapi_oku(self, g):
        p = g.get("rapor"); j = ortak.json_oku(self.yol(p)) if p else None
        if not isinstance(j, dict):
            return {"sonuc": "HATA", "hatalar": [{"madde": "rapor_yok", "rapor": p, "kapi": g.get("kapi"), "seviye": "HATA"}]}
        u = j.get("_uretim") or {}
        if g["tur"] == "betik" and u.get("gorev") != g["id"]:
            return {"sonuc": "HATA", "hatalar": [{"madde": "rapor_bu_goreve_ait_degil", "rapor": p, "seviye": "HATA"}]}
        return {"sonuc": _sonuc(j.get("sonuc") or u.get("sonuc")), "hatalar": list(j.get("hatalar") or []),
                "cikis_kodu": j.get("cikis_kodu"), "plato": j.get("plato") is True}

    def tur_coz(self, a, tur_no, merdiven, tg):
        gruplar = sorted({gr for gr, _ in tur_sablonlari(a, tur_no, merdiven)})
        kapanis = isinstance(merdiven, str)
        rapor = None
        for gr in gruplar:
            gt = [g for g in tg if g.get("grup") == gr]
            if not gt: return {"eylem": {"tur": "grup_ac", "grup": gr}}
            et = {}
            for g in gt:
                if g["anahtar"] not in et or g["deneme"] > et[g["anahtar"]]["deneme"]: et[g["anahtar"]] = g
            eksik = []
            for g in sorted(et.values(), key=lambda x: x["id"]):
                if g["durum"] in YENILENIR:
                    if g["deneme"] < g.get("deneme_max", DENEME_MAX): return {"eylem": {"tur": "yenile", "gorev": g["id"]}}
                    eksik.append(g["id"])
                elif g["durum"] == "iptal": eksik.append(g["id"])
            acik = sorted((g for g in et.values() if g["durum"] in ACIK), key=lambda x: x["id"])
            if acik: return {"eylem": {"tur": "calis", "gorevler": [g["id"] for g in acik]}}
            if eksik and not kapanis:
                return {"gecti": False, "sonuclar": ["HATA"], "grup": gr,
                        "hatalar": [{"madde": "gorev_tukendi", "gorevler": eksik, "seviye": "HATA"}]}
            kotu, hatalar, butce, plato = [], [], False, False
            for g in sorted(et.values(), key=lambda x: x["id"]):
                if not g.get("kapi") or kapanis: continue
                r = self.kapi_oku(g); rapor = g.get("rapor")
                if r["sonuc"] in SONUC_GECER: continue
                kotu.append(r["sonuc"]); plato = plato or r.get("plato")
                hatalar += r["hatalar"] or [{"madde": "kapi", "kapi": g["kapi"], "seviye": r["sonuc"]}]
                kp = next((k for k in a.kapilar if k.kod == g["kapi"]), None)
                if (kp and kp.butce and r["sonuc"] == "HATA") or r.get("cikis_kodu") == BUTCE: butce = True
            if kotu: return {"gecti": False, "sonuclar": kotu, "hatalar": hatalar, "butce": butce, "rapor": rapor, "grup": gr,
                             "plato": bool(plato)}
        return {"gecti": True, "rapor": rapor}

    def terminal(self, a, karar, son, merdiven, surum, tur_no):
        son = son or {"sonuclar": [], "hatalar": []}
        hatalar = son.get("hatalar") or []
        # seyirci kapısının hedef maddeleri (hedef: true, sahne: <parti|FILM>) kapı değil hedef ölçüsüdür: ne plan durdurur ne film HATA'sı
        kapi_h = [h for h in hatalar if isinstance(h, dict) and h.get("hedef") is not True]
        planlar = sorted({str(h.get("plan", h.get("sahne"))) for h in kapi_h
                          if h.get("plan", h.get("sahne")) is not None and h.get("seviye") != "BAYRAK"})
        film_hata = any(h.get("plan", h.get("sahne")) is None and _sonuc(h.get("seviye")) in ("HATA", "KRITIK") for h in kapi_h)
        yalniz_kismi = bool(son.get("sonuclar")) and set(son["sonuclar"]) <= {"KISMI"} and not film_hata
        if karar == "durdu": karar = "kapi6" if film_hata else "durdu"
        elif karar in ("kagit_urun", "kapi6") and yalniz_kismi: karar = "hedef_alti"
        return {"tur": "tavan", "karar": karar, "durdu": planlar if karar == "durdu" else [], "hatalar": hatalar[:50],
                "merdiven": merdiven, "surum": surum, "tur_no": tur_no,
                "kapanis_grubu": son.get("grup") if karar in ("durdu", "hedef_alti") else None}

    def coz(self, a):
        hepsi = self.asama_gorevleri(a.kod)
        if not hepsi:
            return {"durum": "bekliyor", "tur": 0, "eylem": {"tur": "grup_ac", "surum": 1, "tur_no": 1, "merdiven": None}}
        surum = max(g.get("surum", 1) for g in hepsi)
        gs = [g for g in hepsi if g.get("surum", 1) == surum]
        imza = self.surum_imzasi(gs)
        tv = self.tavan_raporu(a, surum)
        if tv:
            d = "kismi" if tv["karar"] in ("durdu", "hedef_alti") else "kapi_gecmedi"
            c = {"durum": d, "tur": tv.get("tur_no"), "hedef_alti": d == "kismi", "rapor": f"_RAPOR/TAVAN_{a.kod}_s{surum}.json",
                 "girdi_imza": imza, "surum": surum, "karar": tv["karar"], "durdu": tv.get("durdu", [])}
            kg = tv.get("kapanis_grubu")
            if d == "kismi" and kg is not None and tur_sablonlari(a, 0, f"kapanis:{kg}"):
                m = f"kapanis:{kg}"; kt = tv["tur_no"] + 1
                tg = [g for g in gs if g.get("tur_no") == kt and g.get("merdiven") == m]
                r = self.tur_coz(a, kt, m, tg)
                if r.get("eylem"):
                    c.update(durum="calisiyor", tur=kt, eylem=dict(r["eylem"], surum=surum, tur_no=kt, merdiven=m))
        else:
            c = self._turlar(a, surum, gs)
            c.update(girdi_imza=imza, surum=surum)
        if c["durum"] in ("tamam", "kismi") and not a.istege_bagli and imza != self.asama_imza(a):
            c = dict(c, durum="bayat", eylem={"tur": "surum_ac", "surum": surum + 1, "tur_no": 1, "merdiven": None})
        elif c.get("eylem") and c["eylem"]["tur"] in ("grup_ac", "calis", "yenile") and imza != self.asama_imza(a) \
                and not a.istege_bagli:
            c = dict(c, durum="bayat", eylem={"tur": "surum_ac", "surum": surum + 1, "tur_no": 1, "merdiven": None})
        return c

    def _turlar(self, a, surum, gs):
        tur_no, plan_m, son, plato = 1, None, None, False
        while True:
            tg = [g for g in gs if g.get("tur_no") == tur_no]
            if not tg:
                e = {"tur": "grup_ac", "surum": surum, "tur_no": tur_no, "merdiven": plan_m}
                if plato: e["plato"] = True
                return {"durum": "calisiyor", "tur": tur_no, "eylem": e}
            m = tg[0].get("merdiven")
            r = self.tur_coz(a, tur_no, m, tg)
            if r.get("eylem"):
                e = dict(r["eylem"], surum=surum, tur_no=tur_no, merdiven=m)
                return {"durum": "calisiyor", "tur": tur_no, "eylem": e}
            if m is not None and a.tavan_sonrasi[m].tur not in KAPI_TURLU:
                return {"durum": "tavan", "tur": tur_no, "eylem": self.terminal(a, a.tavan_sonrasi[m].tur, son, m, surum, tur_no)}
            if r["gecti"]:
                return {"durum": "tamam", "tur": tur_no, "hedef_alti": False, "rapor": r.get("rapor")}
            if r.get("butce"):
                return {"durum": "butce", "tur": tur_no, "rapor": r.get("rapor"), "hatalar": r.get("hatalar")}
            son = r
            if any(g.get("tur_no") == tur_no + 1 for g in gs):
                tur_no += 1; continue
            dk = self.plato_basamagi(a, r, gs)
            plato = False
            if m is None and dk is not None:
                plan_m, plato = dk, True        # §1.4: plato (KISMI, ilerleme yok) → olağan tur yerine bir kez doktor basamağı
            elif m is None and tur_no < a.tur_max and self.butce_var(a.butce):
                plan_m = None
            elif m is not None and any(g.get("plato_basamagi") for g in tg) and tur_no < a.tur_max and self.butce_var(a.butce):
                plan_m = None                   # plato basamağından sonra olağan turlar kaldığı yerden sürer
            else:
                nb = m + 1 if m is not None else 0
                while nb < len(a.tavan_sonrasi) and not self.butce_var(a.tavan_sonrasi[nb].butce): nb += 1
                if nb >= len(a.tavan_sonrasi):
                    return {"durum": "tavan", "tur": tur_no, "eylem": self.terminal(a, "hedef_alti", son, None, surum, tur_no)}
                b = a.tavan_sonrasi[nb]
                if b.tur in KAPI_TURLU or b.ajan: plan_m = nb
                else:
                    return {"durum": "tavan", "tur": tur_no, "eylem": self.terminal(a, b.tur, son, nb, surum, tur_no)}
            tur_no += 1

    def plato_basamagi(self, a, r, gs):
        """Seyirci kapısı rapordaki plato: true ile KISMI döndüyse ve bu sürümde henüz merdiven turu yoksa yapimci·doktor basamağının
        sırası; değilse None."""
        if not r.get("plato") or not r.get("sonuclar") or not set(r["sonuclar"]) <= {"KISMI"}: return None
        if any(g.get("merdiven") is not None for g in gs): return None
        for nb, b in enumerate(a.tavan_sonrasi):
            if b.ajan == "yapimci" and b.kip == "doktor" and self.butce_var(b.butce): return nb
        return None

    def aktif(self):
        for a in HAT.ASAMALAR:
            if a.istege_bagli and not self.asama_gorevleri(a.kod): continue
            if self.atlanir(a): continue
            c = self.coz(a)
            if c["durum"] in ("tamam", "kismi"): continue
            return a, c
        return None, None

    # ---- görev kurulumu
    def _yeni_id(self, asama, kod):
        os.makedirs(self.gd, exist_ok=True)
        on = f"{asama}-{kod}-"
        n = max([int(d[len(on):]) for d in os.listdir(self.gd) if d.startswith(on) and d[len(on):].isdigit()] or [0])
        return f"{on}{n + 1:03d}"

    def _fmt(self, s, tur_no, i, kip, persona, gdir):
        return (str(s).replace("{tur-1}", str(max(1, tur_no - 1))).replace("{tur100}", str(100 + tur_no))
                .replace("{tur}", str(tur_no)).replace("{i}", str(i)).replace("{kip}", kip or "")
                .replace("{persona}", persona or "").replace("{film}", self.kok).replace("{gorev}", gdir))

    def gorev_kur(self, a, s, anahtar, surum, tur_no, merdiven, i, kip, persona, imza):
        gid = self._yeni_id(a.kod, s.kod); gdir = os.path.join(self.gd, gid)
        f = lambda x: self._fmt(x, tur_no, i, kip, persona, gdir)
        os.makedirs(os.path.join(gdir, "GIRDI"), exist_ok=True); os.makedirs(os.path.join(gdir, "CIKTI"), exist_ok=True)
        rol = (adlar().get("ajanlar", {}).get(s.ajan) or {}).get("rol") if s.tur == "ajan" else None
        girdi = []
        for r in s.girdi:
            for p, ad in girdi_cozumle(self.kok, f(r)):
                if ad: _kopyala(p, os.path.join(gdir, "GIRDI", ad)); girdi.append("GIRDI/" + ad)
                else: girdi += self._klasor_kopyala(p, os.path.join(gdir, "GIRDI"), persona)
        if s.tur == "ajan":
            for ad in SOZLUKLER.get(s.ajan, ()):            # yazar/kör rol veri/'yi okuyamaz (erisim.json): sözlükler GIRDI'ye
                p = os.path.join(HERE, "veri", ad)
                if os.path.isfile(p): _kopyala(p, os.path.join(gdir, "GIRDI", ad)); girdi.append("GIRDI/" + ad)
        if s.tur == "ajan" and rol != "kor":
            d = None
            try: d = os.path.join(ortak.yollar()["veri_kok"], "BILGI", "DERSLER_AKTIF.md")
            except ortak.YolYok: pass
            if d and os.path.isfile(d): _kopyala(d, os.path.join(gdir, "GIRDI", "DERSLER.md")); girdi.append("GIRDI/DERSLER.md")
        asamali = None
        if s.asamali:
            kaynak = f"_KOR_PAKET/{kip}_t{tur_no}/{persona or i}"
            asamali = {"bolumler": list(s.asamali), "acik": [], "mekanizma": "subagentstop", "kaynak": kaynak}
            self._bolum_ac(gdir, asamali, s.asamali[0]); girdi.append(f"GIRDI/{s.asamali[0]}/")
        kp = next((k for k in a.kapilar if k.kod == s.kapi), None) if s.kapi else None
        if s.tur == "ajan":
            cikti = {"zorunlu": [f(c) for c in s.cikti] + [f"CIKTI/rapor_{b}.md" for b in s.asamali], "son": []}
        else: cikti = {"zorunlu": [f(c) for c in s.cikti], "son": []}
        istem = (f"Görevin: {os.path.join(gdir, 'GOREV.json')} — önce onu oku, yalnız orada yazanı yap." if s.tur == "ajan"
                 else f"python .claude/bin/film.py calis {gid}" if s.tur == "betik" else s.mesaj)
        g = {"_surum": 2, "id": gid, "film": self.ad, "asama": a.kod, "tur": s.tur, "ajan": s.ajan, "kip": kip, "persona": persona,
             "rol": rol, "ornek": "yeni", "paralel_grup": f"{a.kod}-s{surum}-t{tur_no}-g{s.grup}", "durum": "hazir",
             "deneme": 1, "deneme_max": DENEME_MAX, "anahtar": anahtar, "surum": surum, "tur_no": tur_no, "grup": s.grup,
             "merdiven": merdiven, "asama_imza": imza, "asamali": asamali, "girdi": girdi,
             "girdi_imza": self.dosya_imza([f(r) for r in s.girdi]), "cikti": cikti,
             "tasima": {f(k): f(v) for k, v in s.tasima}, "kapi": s.kapi, "rapor": f(kp.rapor) if kp else None,
             "arac": s.arac, "argumanlar": [f(x) for x in s.argumanlar], "kredili": s.kredili, "gonderildi": None,
             "mesaj": s.mesaj, "algilama": s.algilama, "istem": istem,
             "komut": [self._komut(x, f) for x in s.komut] if s.komut else None,
             "yarim_davranisi": "devam_et" if rol == "yazar" else "sifirdan", "kanca_gerek": s.tur == "ajan",
             "agent_id": None, "onceki": None, "yerine": None, "cikis_kodu": None,
             "kullanim": {"girdi": None, "cikti": None, "onbellek_okuma": None, "sure_sn": None, "model": MODEL, "effort": "high"},
             "zaman": {"olusturma": simdi(), "basla": None, "bitir": None}}
        if s.tur == "ajan":
            _metin_yaz(os.path.join(gdir, "ISTEM.md"), self._istem_md(a, g))
        self.yaz(g)               # GOREV.json en son: yarım kalan klasör defterde yok sayılır
        self.olay("gorev_kuruldu", gorev=gid, asama=a.kod, anahtar=anahtar)
        return g

    def _komut(self, x, f):
        if x == "film.py": return os.path.join(ortak.DEPO_KOK, ".claude", "bin", "film.py")
        return f(x)

    def _klasor_kopyala(self, kaynak, hedef, persona):
        """Klasör girdisinin içeriği GIRDI/'ye (birleştirerek). Kör paketin eşleştirici anahtarı (ESLESTIRICI/, ANAHTAR.json) ve
        öteki personaların ILK2DK_<p>.md dosyası kopyalanmaz; anahtar yalnız açık dosya girdisiyle (özet eşleştirici) verilir."""
        out = []
        for k, ds, fs in os.walk(kaynak):
            ds[:] = sorted(d for d in ds if d not in ("ESLESTIRICI", "_ESKI", "_RED"))
            for ad in sorted(fs):
                if ad.endswith(".tmp") or ad == "ANAHTAR.json": continue
                m = re.match(r"ILK2DK_(\w+)\.md$", ad)
                if m and persona and m.group(1) != persona: continue
                rel = os.path.relpath(os.path.join(k, ad), kaynak).replace(os.sep, "/")
                _kopyala(os.path.join(k, ad), os.path.join(hedef, rel)); out.append("GIRDI/" + rel)
        return out

    def _istem_md(self, a, g):
        sablon = os.path.join(ortak.DEPO_KOK, ".claude", "skills", "film-yap", "sablonlar",
                              f"{a.kod}_{g['ajan']}" + (f"_{g['kip']}" if g["kip"] else "") + ".md")
        govde = _bayt(sablon).decode("utf-8") if os.path.isfile(sablon) else ""
        if govde:
            import beceri_denetim                                # {{esik:x}} → eşik değeri (ajan ham yer tutucu görmez)
            try: govde = beceri_denetim.sablon_doldur(govde)
            except beceri_denetim.SablonHatasi as e:
                raise Hata(f"Görev şablonu doldurulamadı ({os.path.basename(sablon)}: {e}); ajan görevi açılmadı (film-gelistir).",
                           HATA)
        s = [f"# Görev {g['id']} — {a.kod} {a.ad}", "",
             f"Ajan: {g['ajan']}" + (f"·{g['kip']}" if g["kip"] else "") + (f" · persona {g['persona']}" if g["persona"] else ""),
             "", "Yalnız bu görev klasörünü oku (GOREV.json, ISTEM.md, GIRDI/). Yalnız CIKTI/ klasörüne yaz.",
             "Yazman gereken dosyalar:"] + [f"- {c}" for c in g["cikti"]["zorunlu"]]
        if g["asamali"]: s += ["", "Bölümler sırayla açılır: her bölümün raporunu bitirince dur; sonraki bölümü sistem verir."]
        return "\n".join(s + (["", govde] if govde else [])) + "\n"

    def _bolum_ac(self, gdir, asamali, bolum):
        kaynak = self.yol(asamali["kaynak"], bolum); hedef = os.path.join(gdir, "GIRDI", bolum)
        if os.path.isdir(kaynak):
            if os.path.isdir(hedef): shutil.rmtree(hedef)
            shutil.copytree(kaynak, hedef)
        else: os.makedirs(hedef, exist_ok=True)
        if bolum not in asamali["acik"]: asamali["acik"].append(bolum)

    def grup_ac(self, a, e):
        surum, tur_no, m = e["surum"], e["tur_no"], e.get("merdiven")
        sab = tur_sablonlari(a, tur_no, m)
        grup = e.get("grup", min(gr for gr, _ in sab))
        mevcut = [g for g in self.asama_gorevleri(a.kod) if g.get("surum") == surum]
        imza = self.surum_imzasi(mevcut) if mevcut else self.asama_imza(a)
        anahtarlar = {g["anahtar"] for g in mevcut}
        kurulan = 0
        for gr, s in sab:
            if gr != grup: continue
            if s.kosul and not self.kosul_tamam(a, s):
                continue
            n = self.adet(s.adet); kipler = HAT.kip_listesi(s.kip, n); per = HAT.kip_listesi(s.persona, n)
            for i in range(1, n + 1):
                an = f"{a.kod}@s{surum}/t{tur_no}/g{gr}/{s.kod}/{i}"
                kurulan += 1
                if an in anahtarlar: continue
                g = self.gorev_kur(a, s, an, surum, tur_no, m, i, kipler[i - 1], per[i - 1], imza)
                if e.get("plato"): g["plato_basamagi"] = True; self.yaz(g)
                _kesme("gorev_kuruldu")
        if not kurulan:                                  # grubun bütün görevleri koşulsuz kaldı: grup "atlandı" diye kapanır
            an = f"{a.kod}@s{surum}/t{tur_no}/g{grup}/ATLA/1"
            if an not in anahtarlar:
                g = self.gorev_kur(a, HAT.GorevSablonu(kod="ATLA", tur="betik", grup=grup, arac="film.py:atla"), an, surum, tur_no,
                                   m, 1, None, None, imza)
                g["durum"] = "bitti"; g["zaman"]["bitir"] = simdi(); g["not"] = "koşul sağlanmadı; grup atlandı"; self.yaz(g)

    def kosul_tamam(self, a, s):
        """GorevSablonu.kosul (HAT.KOSULLAR). flow_filtre_red: _RAPOR/FLOW_<blok>.json'da filtre_red HATA'sı var ve bu aşamanın
        aynı görevi o rapordan sonra bitmedi (aynı red iki kez onarıma gitmez)."""
        if s.kosul == "flow_filtre_red":
            son = max([_zaman_oku(g["zaman"].get("bitir")) or 0 for g in self.asama_gorevleri(a.kod)
                       if g["anahtar"].split("/")[3] == s.kod and g["durum"] == "bitti"] or [0])
            for p in glob.glob(self.yol("_RAPOR", "FLOW_*.json")):
                r = ortak.json_oku(p, {}) or {}
                if os.path.getmtime(p) <= son: continue
                if any(isinstance(h, dict) and h.get("madde") == "filtre_red" and _sonuc(h.get("seviye")) == "HATA"
                       for h in (r.get("hatalar") or []) + (r.get("olcumler") or [])):
                    return True
            return False
        raise Hata(f"Bilinmeyen görev koşulu: {s.kosul} (film-gelistir).")

    def yenile(self, eski):
        """Kesilen/geçersiz görevin yerine yeni deneme (bitmiş görev asla yeniden çalışmaz)."""
        var = [g for g in self.gorevler().values() if g.get("onceki") == eski["id"]]
        if var:
            eski["yerine"] = var[0]["id"]; self.yaz(eski); return var[0]
        gid = self._yeni_id(eski["asama"], eski["id"].split("-")[1]); gdir = os.path.join(self.gd, gid)
        eskidir = self.gorev_dizini(eski)
        shutil.copytree(os.path.join(eskidir, "GIRDI"), os.path.join(gdir, "GIRDI"), dirs_exist_ok=True)
        os.makedirs(os.path.join(gdir, "CIKTI"), exist_ok=True)
        g = json.loads(json.dumps(eski))
        if g.get("asamali"):
            for b in g["asamali"]["bolumler"][1:]:
                p = os.path.join(gdir, "GIRDI", b)
                if os.path.isdir(p): shutil.rmtree(p)
            g["asamali"]["acik"] = g["asamali"]["bolumler"][:1]
        yarim = os.path.join(eskidir, "CIKTI")
        if eski.get("yarim_davranisi") == "devam_et" and os.path.isdir(yarim) and os.listdir(yarim):
            shutil.copytree(yarim, os.path.join(gdir, "GIRDI", "YARIM"), dirs_exist_ok=True)
        if os.path.isfile(os.path.join(eskidir, "ISTEM.md")):
            shutil.copyfile(os.path.join(eskidir, "ISTEM.md"), os.path.join(gdir, "ISTEM.md"))
        g.update(id=gid, durum="hazir", deneme=eski["deneme"] + 1, onceki=eski["id"], yerine=None, agent_id=None,
                 gonderildi=None, cikis_kodu=None, kayip=None, topla_gerek=None,
                 zaman={"olusturma": simdi(), "basla": None, "bitir": None},
                 kullanim={"girdi": None, "cikti": None, "onbellek_okuma": None, "sure_sn": None, "model": MODEL, "effort": "high"})
        if g["tur"] == "ajan": g["istem"] = f"Görevin: {os.path.join(gdir, 'GOREV.json')} — önce onu oku, yalnız orada yazanı yap."
        elif g["tur"] == "betik": g["istem"] = f"python .claude/bin/film.py calis {gid}"
        self.yaz(g)
        _kesme("yenile_isaret_once")
        eski["yerine"] = gid; self.yaz(eski)
        self.olay("gorev_yenilendi", gorev=gid, onceki=eski["id"])
        return g

    def surum_ac(self, a, e):
        for g in self.asama_gorevleri(a.kod):
            if g["durum"] in ACIK and not (g.get("kredili") and g.get("gonderildi")):
                g["durum"] = "iptal"; self.yaz(g)
        karar_yaz(self, f"{a.kod} yeniden açıldı: girdisi değişti (bayat)", "girdi imzası farklı", "aşamanın bir turu",
                  asama=a.kod, kaynak="betik:film.py", tur="bilgi")
        self.grup_ac(a, e)

    def tavan_yaz(self, a, e):
        u = uretim_zarfi(a.kod, None, e["karar"].upper(), self)
        r = {"_surum": 1, "_uretim": u, "asama": a.kod, "surum": e["surum"], "tur_no": e["tur_no"], "karar": e["karar"],
             "durdu": e["durdu"], "hedef_alti": e["karar"] in ("durdu", "hedef_alti"), "merdiven": e["merdiven"],
             "kapanis_grubu": e.get("kapanis_grubu"),
             "basamaklar": [{"tur": b.tur, "aciklama": b.aciklama, "ajan": b.ajan, "kip": b.kip} for b in a.tavan_sonrasi],
             "hatalar": e["hatalar"],
             "cikis_kodu": KAPI if e["karar"] in ("kapi6", "kagit_urun") else BITTI}
        ortak.atomik_yaz(self.yol("_RAPOR", f"TAVAN_{a.kod}_s{e['surum']}.json"), r)
        acik = {"durdu": f"planlar durduruldu ({', '.join(e['durdu']) or '—'}); hat o planlar olmadan sürer",
                "hedef_alti": "hedef altında kaldı; hat sürer, film sonu raporuna yazılır",
                "kagit_urun": "kapı sağlanmadı: kâğıt ürün teslim edilir, videoya geçilmez",
                "kapi6": "merdiven tükendi ve kapı HATA'sı sürüyor: hat durdu"}[e["karar"]]
        karar_yaz(self, f"{a.kod} tur tavanı doldu: {acik}", "§1.5 tavan sonrası merdiveni", "açık eksik raporunda",
                  asama=a.kod, kaynak="betik:film.py", tur="karar")
        self.olay("tavan", asama=a.kod, karar=e["karar"], durdu=e["durdu"])

    # ---- kullanıcı eseri
    def blok_bitti(self, blok):
        if os.path.exists(self.yol("KUNYE", f"BLOK_{'HEPSI' if blok == '*' else blok}.bitti")): return True
        bp = ortak.json_oku(self.yol("BLOK_PLANI.json"), {}) or {}
        bl = [b for b in bp.get("bloklar") or [] if blok == "*" or str(b.get("id")) == str(blok)]
        if not bl: return False
        return all(os.path.exists(self.yol("KUNYE", f"{int(n):03d}.json")) for b in bl for n in b.get("planlar") or [])

    def algilandi(self, g):
        al = g.get("algilama") or {}
        if al.get("tur") == "dosya_var": return bool(glob.glob(self.yol(al["desen"])))
        if al.get("tur") == "dosya_yok": return not glob.glob(self.yol(al["desen"]))
        if al.get("tur") == "blok": return self.blok_bitti(al.get("blok", "*"))
        return False

    def kullanici_bitti(self, g):
        g["durum"] = "bitti"; g["zaman"]["bitir"] = simdi(); self.yaz(g); self.olay("kullanici_bitti", gorev=g["id"])

    # ---- küresel kapılar (her aşama başı; §7.2 DISK/TOKEN, §1.5)
    def harcama(self):
        t = {"girdi": 0, "cikti": 0, "onbellek_okuma": 0}
        for g in self.gorevler().values():
            for k in t: t[k] += int((g.get("kullanim") or {}).get(k) or 0)
        bitti = sum(1 for g in self.gorevler().values() if g["durum"] == "bitti" and g["tur"] == "ajan")
        tahmin = sum(self.gorev_tahmini(a) for a in HAT.ana_hat())
        ajan_orani = 0.6
        t["projeksiyon_film"] = int((t["girdi"] + t["cikti"]) / bitti * tahmin * ajan_orani) if bitti else None
        k = {"flow_kredi": 0, "ai84_kredi": 0, "usd": 0.0}
        try:                                                # defterin sahibi kredi.py (birim → harcanan)
            for br, v in kredi_mod.defter_ozet(self.kok)["birim"].items():
                if br == "flow": k["flow_kredi"] = v["harcanan"]
                elif br == "ai84": k["ai84_kredi"] = v["harcanan"]
                elif br == "usd": k["usd"] = float(v["harcanan"])
        except Exception:
            for s in jsonl_oku(self.yol("KREDI_DEFTERI.jsonl")):
                if s.get("olay") != "gonderim": continue
                br = s.get("birim", "flow")
                if br in ("flow", "ai84"): k[br + "_kredi"] += int(s.get("kredi") or 0)
                elif br == "usd": k["usd"] += float(s.get("kredi") or 0)
        k["token"] = t
        return k

    def gorev_tahmini(self, a):
        f = _olcek_tahmin()
        if f:
            try:
                v = f(a.kod, self.kok)
                if isinstance(v, (int, float)) and v > 0: return v
            except Exception: pass
        if a.gorev_tahmin: return a.gorev_tahmin
        tek = sum(self.adet(s.adet) for s in a.gorevler)
        merdiven = sum(1 for b in a.tavan_sonrasi if b.ajan)
        return tek * (a.tur_max + 1) + merdiven

    def token_projeksiyonu_yaz(self, neden):
        h = self.harcama()["token"]
        _metin_yaz(self.yol("TOKEN_PROJEKSIYON.md"),
                   f"# Token projeksiyonu ({simdi()})\n\nNeden: {neden}\n\n- Kullanılan girdi: {h['girdi']}\n- Kullanılan çıktı: "
                   f"{h['cikti']}\n- Önbellek okuma: {h['onbellek_okuma']}\n- Film projeksiyonu: {h['projeksiyon_film']}\n"
                   f"- Tavan (film_token_tavan): {esik('film_token_tavan')}\n\nhat-denetcisi döngü taraması yapar (§1.5).\n")

    def kuresel_kapilar(self, a):
        if os.path.exists(self.yol("DUR")):
            return dict(tur="bekle", cikis_kodu=BEKLE, kullaniciya="Film durduruldu (DURDUR.bat). Devam için DEVAM.bat.")
        if a.kredi and "flow" in a.kredi:
            kilit = flow_kilitli()
            if kilit:
                return dict(tur="kisit", cikis_kodu=KISIT, kullaniciya="Flow uyarı verdi; hesap kilitli. GÖNDER'e basma, sayfayı "
                            "yenileme. Kilidi yalnız sen kaldırırsın (UYARI_GECTI.bat). Başka servise geçilmedi.")
        if a.kod in VIDEO_ASAMALARI:
            ok, neden = self.video_acilabilir()
            if not ok:
                return dict(tur="kapi", cikis_kodu=KAPI, kullaniciya="Animatik onaylı değil; video görevi açılmaz: " + str(neden))
        if a.ortam == "yerel" and ortam() == "bulut" and not self.deneme:
            return dict(tur="ortam", cikis_kodu=ORTAM, kullaniciya=f"{a.kod} yalnız kullanıcının bilgisayarında yürür. " + BULUT_CUMLESI)
        bos, en_az = disk_bos_gb(self.kok), esik("disk_bos_min_gb") or 0
        if bos < en_az:
            return dict(tur="bekle", cikis_kodu=BEKLE, kullaniciya=f"Diskte yer az ({bos:.1f} GB < {en_az} GB). Eski filmler D "
                        "diskine arşivlenecek: D'yi tak; arşiv bitince kendim devam ederim.")
        tavan = esik("film_token_tavan")
        if tavan:
            h = self.harcama()["token"]; kul = h["girdi"] + h["cikti"]
            if kul > tavan or (h["projeksiyon_film"] or 0) > tavan:
                self.token_projeksiyonu_yaz(f"token tavanı ({tavan}) aşıldı ya da aşılacak")
                return dict(tur="bekle", cikis_kodu=BEKLE, kullaniciya="Bu film için ayrılan Claude kullanımı doldu; ekip döngüleri "
                            "inceliyor (TOKEN_PROJEKSIYON.md). Kendim devam ederim.")
        n = sum(1 for g in self.asama_gorevleri(a.kod) if g.get("deneme", 1) == 1)
        tav = self.gorev_tahmini(a) * (esik("gorev_tavani_carpan") or 1.5)
        if n > tav:
            self.token_projeksiyonu_yaz(f"{a.kod} görev sayısı {n} > tahmin × çarpan ({tav:.0f})")
            return dict(tur="bekle", cikis_kodu=BEKLE, kullaniciya=f"{a.kod} beklenenden çok görev açtı ({n}); ekip inceliyor "
                        "(TOKEN_PROJEKSIYON.md).")
        return None

    def video_acilabilir(self):
        """Kullanıcının kesin şartı (§1.5 kural 4, KK3a): onaylı animatik (ANIMATIK/ONAY.json ONAYLI, imza güncel) olmadan video
        kredisi harcayan aşama (A13 BUT2, A14a, A14) görev açmaz. Sahte denemede A12'nin defterdeki durumu yeter; gerçek filmde
        (kaset dahil) imza şarttır. Araç açılmazsa kapalı başarısız."""
        a12 = HAT._DIZIN.get("A12")
        a12_durum = self.coz(a12).get("durum") if a12 is not None else "tamam"
        try:
            import animatik_imza
            return animatik_imza.video_acilabilir(self.kok, sahte=self.sahte, a12_durum=a12_durum)
        except Exception as e:
            return False, f"animatik imzası denetlenemedi ({e.__class__.__name__})"

    # ---- ilerleme (sonraki'nin çekirdeği)
    def ilerle(self, salt_okunur=False, sinir=500):
        for _ in range(sinir):
            a, c = self.aktif()
            if a is None:
                return dict(tur="bitti", cikis_kodu=BITTI, asama=None, kullaniciya="Film bitti. Özet: film.py ozet --kullanici.")
            bas = dict(asama=f"{a.kod} {a.ad}", tur_no=c.get("tur"))
            k = self.kuresel_kapilar(a)
            if k: return dict(bas, **k)
            if c["durum"] == "kapi_gecmedi":
                metin = ("Kapı sağlanmadı: kâğıt ürün (senaryo ve varsa animatik) yüzüne vur raporuyla teslim edildi; videoya geçilmedi."
                         if c.get("karar") == "kagit_urun" else
                         f"{a.kod} aşamasında bütün kalite yolları denendi ve kapı geçmedi; hat durdu (rapor: {c['rapor']}).")
                return dict(bas, tur="kapi", cikis_kodu=KAPI, kullaniciya=metin, oku=c["rapor"])
            if c["durum"] == "butce":
                return dict(bas, tur="butce", cikis_kodu=BUTCE, oku=c.get("rapor"),
                            kullaniciya="Tahmini kredi bütçeyi aşıyor; yazılmış film kısaltılmaz. Kredi yükleyince kendim devam ederim.")
            e = c["eylem"]
            if e["tur"] == "calis":
                gs = [self.g(i) for i in e["gorevler"]]
                kul = [g for g in gs if g["tur"] == "kullanici" and self.algilandi(g)]
                if kul and not salt_okunur:
                    for g in kul: self.kullanici_bitti(g)
                    continue
                return dict(bas, **self.grup_ciktisi(gs, salt_okunur))
            if salt_okunur:
                return dict(bas, tur="hazirlaniyor", cikis_kodu=BITTI, kullaniciya=f"{a.kod}: sıradaki görevler hazırlanıyor.")
            if e["tur"] == "grup_ac": self.grup_ac(a, e)
            elif e["tur"] == "surum_ac": self.surum_ac(a, e)
            elif e["tur"] == "yenile": self.yenile(self.g(e["gorev"]))
            elif e["tur"] == "tavan": self.tavan_yaz(a, e)
        raise Hata("film.py sonraki döngüden çıkamadı (iç hata; film-gelistir).")

    def grup_ciktisi(self, gs, salt_okunur=False):
        ajan = [g for g in gs if g["tur"] == "ajan"]; betik = [g for g in gs if g["tur"] == "betik"]
        kul = [g for g in gs if g["tur"] == "kullanici"]
        if ajan:
            calisan = [g for g in ajan if g["durum"] == "calisiyor"]
            hazir = [g for g in ajan if g["durum"] == "hazir" and not self.sirali_bekliyor(g)]
            ver = hazir[:max(0, int(esik("ajan_paralel_max") or 5) - len(calisan))]
            if not salt_okunur:
                ver = [self.sirali_dilim_yenile(g) for g in ver]
            if ver:
                return dict(tur="ajan", cikis_kodu=AJAN, gorevler=[
                    {"id": g["id"], "tur": "ajan", "ajan": g["ajan"], "kip": g["kip"], "paralel_grup": g["paralel_grup"],
                     "istem": g["istem"]} for g in ver], kullaniciya=None)
            return dict(tur="bekle", cikis_kodu=BEKLE, gorevler=[g["id"] for g in calisan],
                        kullaniciya="Ajanlar çalışıyor; bitince kendim devam ederim.")
        if betik:
            calisan = [g for g in betik if g["durum"] == "calisiyor" and not g.get("topla_gerek") and not g.get("gonderildi")]
            ver = [g for g in betik if g not in calisan]
            if ver:
                return dict(tur="betik", cikis_kodu=BITTI, kullaniciya=None, gorevler=[
                    {"id": g["id"], "tur": "betik", "istem": g["istem"]} | ({"topla": True} if g.get("gonderildi") else {})
                    for g in ver])
            return dict(tur="bekle", cikis_kodu=BEKLE, gorevler=[g["id"] for g in calisan],
                        kullaniciya="Bir betik çalışıyor; bitince kendim devam ederim. Takıldıysa: film.py kurtar.")
        g = kul[0]
        if g["durum"] == "hazir" and not salt_okunur:
            g["durum"] = "calisiyor"; g["zaman"]["basla"] = simdi(); self.yaz(g)
        return dict(tur="kullanici_eylemi", cikis_kodu=KULLANICI, gorevler=[{"id": g["id"], "algilama": g["algilama"]}],
                    kullaniciya=g["mesaj"])

    # ---- sıralı çift ([SON] O-12): aynı mekân ve zamanda süren ardışık sahne grubu, öncekinin planları bitince yazılır
    def _sirali_onceki(self, g):
        """(önceki grubun numarası, önceki görev ya da None). Sıralı değilse (None, None)."""
        if (g["asama"], g["anahtar"].split("/")[3]) not in SIRALI_CIFT: return None, None
        i = int(g["anahtar"].rsplit("/", 1)[-1])
        dl = ortak.json_oku(self.yol("_YONETMEN", "DILIM.json"), {}) or {}
        gr = next((x for x in dl.get("gruplar") or [] if isinstance(x, dict) and x.get("i") == i), None)
        bag = (gr or {}).get("bagimli")
        if not bag or not re.match(r"^G\d+$", str(bag)): return None, None
        k = int(str(bag)[1:])
        on = g["anahtar"].rsplit("/", 1)[0] + f"/{k}"
        es = [x for x in self.gorevler().values() if x["anahtar"] == on]
        return k, (max(es, key=lambda x: x["deneme"]) if es else None)

    def sirali_bekliyor(self, g):
        k, o = self._sirali_onceki(g)
        return k is not None and (o is None or o["durum"] != "bitti")

    def sirali_dilim_yenile(self, g):
        """Önceki grup bitti: dilim.py --asama A07b --grup <i> (önceki planların çözülmüş bitişi) ve G<i>.json GIRDI'ye yeniden."""
        k, _ = self._sirali_onceki(g)
        if k is None or g.get("dilim_yenilendi"): return g
        i = int(g["anahtar"].rsplit("/", 1)[-1])
        r = subprocess.run([sys.executable, os.path.join(HERE, "dilim.py"), "--asama", g["asama"], "--grup", str(i), "--film", self.kok],
                           capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode != 0:
            raise Hata(f"dilim.py --grup {i} hata verdi ({r.returncode}): {(r.stdout or '')[-300:]}", HATA)
        p = self.yol("_YONETMEN", "DILIM", f"G{i}.json")
        if os.path.isfile(p): _kopyala(p, os.path.join(self.gorev_dizini(g), "GIRDI", f"G{i}.json"))
        g["dilim_yenilendi"] = simdi(); self.yaz(g); self.olay("dilim_yenilendi", gorev=g["id"], onceki=f"G{k}")
        return g

    # ---- görev yürütme
    def nabiz_tamam(self):
        """Kanca nabzı (§4.5.8) taze ve kancanın kendi yazdığı nabızsa ikinci koruma: CLAUDE_CODE_FORK_SUBAGENT kapalı (fork_kapali
        true; kanca açıkken nabız yazmaz) ve .claude/settings.json nabızdaki özetle aynı. Kanca dosyaları değişmişse de geçersiz."""
        n = ortak.json_oku(os.path.join(self.gd, "KANCA_NABZI.json"), {}) or {}
        z = _zaman_oku(n.get("zaman"))
        if z is None or time.time() - z > KANCA_NABZI_MAX_SN: return False
        if str(n.get("yazan") or "").startswith("kanca") or "fork_kapali" in n:
            if n.get("fork_kapali") is not True: return False
            ayar = os.path.join(ortak.DEPO_KOK, ".claude", "settings.json")
            beklenen = (n.get("ayar_sha") or {}).get("settings.json")
            gercek = hashlib.sha1(_bayt(ayar)).hexdigest() if os.path.isfile(ayar) else None
            if beklenen != gercek: return False
        for ad, sha in (n.get("kanca_sha") or {}).items():
            for d in (os.path.join(ortak.DEPO_KOK, ".claude", "hooks"), os.path.join(ortak.DEPO_KOK, ".claude", "kurallar")):
                p = os.path.join(d, ad)
                if os.path.isfile(p) and not hashlib.sha1(_bayt(p)).hexdigest().startswith(str(sha)): return False
        return True

    def basla(self, ids, nabizsiz=False):
        out = {"basladi": [], "zaten": [], "reddedildi": []}
        with self.kilit():
            for gid in ids:
                g = self.g(gid)
                if g["durum"] == "bitti": out["zaten"].append(gid); continue
                if g["durum"] not in ACIK:
                    raise Hata(f"{gid} artık geçerli değil ({g['durum']}); film.py sonraki yeni görevi verir.")
                if g["tur"] == "ajan" and g.get("kanca_gerek") and not nabizsiz and not self.nabiz_tamam():
                    self.olay("nabiz_reddi", gorev=gid)
                    raise Hata("Kanca nabzı yok ya da eski: ajan görevi başlatılmadı. KURTARMA.md §Kanca'yı uygula "
                               "(Claude'u depo klasöründe yeniden aç).", HATA)
                if g["durum"] == "hazir":
                    g["durum"] = "calisiyor"; g["zaman"]["basla"] = simdi(); self.yaz(g); self.olay("basla", gorev=gid)
                out["basladi"].append(gid)
        return out

    def cikti_eksik(self, g):
        gdir = self.gorev_dizini(g); eksik = []
        for c in g["cikti"]["zorunlu"] + g["cikti"].get("son", []):
            p = os.path.join(gdir, c) if g["tur"] == "ajan" else self.yol(c)
            if not os.path.exists(p): eksik.append(c); continue
            if p.endswith(".json") and ortak.json_oku(p) is None: eksik.append(c + " (bozuk JSON)")
        return eksik

    def bitir(self, gid, kullanim=None, gecersiz=None):
        with self.kilit():
            self.yeniden_oku(); g = self.g(gid)
            if g["durum"] == "bitti": return {"gorev": gid, "durum": "bitti", "not": "zaten bitti"}
            if g["durum"] not in ACIK:
                return {"gorev": gid, "durum": g["durum"], "not": "görev artık geçerli değil; çıktısı kullanılmadı"}
            if gecersiz is not None:                # SubagentStop: 2 düzeltme hakkı bitti → çıktı kullanılmaz, yeni deneme açılır
                if kullanim: g["kullanim"].update({k: v for k, v in kullanim.items() if k in g["kullanim"]})
                g["durum"] = "gecersiz"; g["gecersiz_neden"] = str(gecersiz)[:500]; g["zaman"]["bitir"] = simdi(); self.yaz(g)
                self.olay("gecersiz", gorev=gid, neden=str(gecersiz)[:200])
                return {"gorev": gid, "durum": "gecersiz", "not": "doğrulama geçmedi; sonraki yeni deneme açar"}
            eksik = self.cikti_eksik(g)
            if eksik: raise Hata("Çıktı eksik: " + ", ".join(eksik), HATA, eksik=eksik)
            if kullanim:
                g["kullanim"].update({k: v for k, v in kullanim.items() if k in g["kullanim"]})
                if kullanim.get("model") and kullanim["model"] != MODEL:
                    g["durum"] = "model_sapmasi"; self.yaz(g); self.olay("model_sapmasi", gorev=gid, model=kullanim["model"])
                    return {"gorev": gid, "durum": "model_sapmasi", "not": "beklenen model değil; görev yeniden kuyrukta"}
            for k, v in (g.get("tasima") or {}).items():
                src = os.path.join(self.gorev_dizini(g), k)
                if os.path.isfile(src): _kopyala(src, self.yol(v))
            _kesme("tasima_sonra")
            g["durum"] = "bitti"; g["zaman"]["bitir"] = simdi(); self.yaz(g); self.olay("bitti", gorev=gid)
            return {"gorev": gid, "durum": "bitti"}

    def asama_ilerlet(self, gid):
        with self.kilit():
            g = self.g(gid); a = g.get("asamali")
            if not a: raise Hata(f"{gid} aşamalı görev değil.")
            if g["durum"] != "calisiyor": raise Hata(f"{gid} çalışmıyor ({g['durum']}).")
            son = a["acik"][-1]
            if not os.path.isfile(os.path.join(self.gorev_dizini(g), "CIKTI", f"rapor_{son}.md")):
                raise Hata(f"{son} bölümünün raporu yok (CIKTI/rapor_{son}.md); sonraki bölüm açılmadı.", eksik=[f"CIKTI/rapor_{son}.md"])
            if len(a["acik"]) >= len(a["bolumler"]): return {"gorev": gid, "son": True, "kalan": 0}
            nxt = a["bolumler"][len(a["acik"])]
            self._bolum_ac(self.gorev_dizini(g), a, nxt); self.yaz(g)
            _kesme("bolum_acildi")
            return {"gorev": gid, "bolum": nxt, "kalan": len(a["bolumler"]) - len(a["acik"])}

    # sahte (test ve bulut denemesi; ağ ve kredi yok)
    def kaset(self, kapi, tur_no):
        k = ortak.json_oku(self.yol("_KASET", f"{kapi}.json"))
        if not isinstance(k, dict): return {"sonuc": "GEC", "hatalar": []}
        return (k.get("turlar") or {}).get(str(tur_no)) or {"sonuc": k.get("sonuc", "GEC"), "hatalar": k.get("hatalar", [])}

    def kapi_raporu(self, g):
        k = self.kaset(g["kapi"], g["tur_no"]); s = _sonuc(k.get("sonuc", "GEC"))
        return {"_surum": 1, "_uretim": uretim_zarfi(g["asama"], g["id"], s, self, arac="sahte"), "kapi": g["kapi"], "kapsam": "FILM",
                "tur": g["tur_no"], "sonuc": s, "ozet": {"hata": len(k.get("hatalar") or [])}, "hatalar": k.get("hatalar") or [],
                "sahte": True}

    def sahte_dosya(self, p, g, rapor=False):
        if rapor: ortak.atomik_yaz(p, self.kapi_raporu(g))
        elif p.endswith(".json"):
            ortak.atomik_yaz(p, {"_uretim": uretim_zarfi(g["asama"], g["id"], "GEC", self, arac="sahte"), "sahte": True, "sonuc": "GEC"})
        elif p.endswith((".md", ".txt", ".srt")): _metin_yaz(p, f"# sahte ({g['id']})\n\nOZET | sahte\n")
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "wb") as f: f.write(b"SAHTE\n")

    def sahte_betik(self, g):
        jsonl_ekle(self.yol("_GOREV", "SAHTE_CALISMA.jsonl"), {"gorev": g["id"], "anahtar": g["anahtar"], "zaman": simdi()})
        if g.get("kredili"):
            jsonl_ekle(self.yol("KREDI_DEFTERI.jsonl"), {"zaman": simdi(), "olay": "gonderim", "kredi": 0, "birim": "flow",
                                                         "dilim": "ana", "madde": g["anahtar"], "saglayici": "sahte",
                                                         "is_kimligi": g["id"]})
            _kesme("sahte_gonderim_sonra")
        self.sahte_ciktilar(g)
        if g.get("arac") == "blok_plani.py" and not os.path.exists(self.yol("BLOK_PLANI.json")):
            ortak.atomik_yaz(self.yol("BLOK_PLANI.json"), {"sahte": True, "bloklar": []})
        return 0

    def sahte_ciktilar(self, g):
        for c in g["cikti"]["zorunlu"]: self.sahte_dosya(self.yol(c), g, rapor=(c == g.get("rapor")))

    def sahte_ajan(self, g):
        if g["durum"] == "hazir": self.basla([g["id"]], nabizsiz=True); g = self.g(g["id"])
        gdir = self.gorev_dizini(g)
        if g.get("asamali"):
            for b in g["asamali"]["bolumler"]:
                _metin_yaz(os.path.join(gdir, "CIKTI", f"rapor_{b}.md"), f"# {b}\n\nOZET | sahte\n")
                if b not in g["asamali"]["acik"]: self.asama_ilerlet(g["id"]); g = self.g(g["id"])
        for c in g["cikti"]["zorunlu"]:
            p = os.path.join(gdir, c)
            if not os.path.exists(p): self.sahte_dosya(p, g, rapor=bool(g.get("kapi")) and c.endswith(".json"))
        return self.bitir(g["id"])

    def kaset_ajan(self, g):
        """Kaset kipi (test): ajan çıktısı kayıttan (saglayicilar/kaset.py ajan_oynat), aşamalı bölümler sırayla, sonra bitir."""
        from saglayicilar import kaset as kaset_mod
        if g["durum"] == "hazir": self.basla([g["id"]], nabizsiz=True); g = self.g(g["id"])
        try: kaset_mod.ajan_oynat(self.kok, g, self.gorev_dizini(g))
        except kaset_mod.KasetYok as e: raise Hata(f"{g['id']}: {e}", ORTAM)
        while g.get("asamali") and len(g["asamali"]["acik"]) < len(g["asamali"]["bolumler"]):
            self.asama_ilerlet(g["id"]); g = self.g(g["id"])        # bölüm raporu kayıtta yoksa Hata (kaset uydurmaz)
        return self.bitir(g["id"])

    def sahte_kullanici(self, g):
        al = g.get("algilama") or {}
        if al.get("tur") == "dosya_var":
            p = self.yol(al["desen"].replace("*", "SAHTE"))
            os.makedirs(os.path.dirname(p), exist_ok=True); _metin_yaz(p, "SAHTE\n")
        elif al.get("tur") == "dosya_yok":
            for p in glob.glob(self.yol(al["desen"])):
                shutil.move(p, p + ".sahte_kapandi")
        elif al.get("tur") == "blok":
            os.makedirs(self.yol("KUNYE"), exist_ok=True)
            _metin_yaz(self.yol("KUNYE", f"BLOK_{'HEPSI' if al.get('blok', '*') == '*' else al['blok']}.bitti"), "sahte\n")
        with self.kilit(): self.kullanici_bitti(self.g(g["id"]))
        return {"gorev": g["id"], "durum": "bitti", "not": "sahte kullanıcı eylemi"}

    def ic_hazirlik(self, g):
        m = self.meta(); nabiz = ortak.json_oku(os.path.join(self.gd, "KANCA_NABZI.json"), {}) or {}
        z = _zaman_oku(nabiz.get("zaman")); bos = disk_bos_gb(self.kok); en_az = esik("disk_bos_min_gb") or 0
        m.update(_uretim=uretim_zarfi("A00", g["id"], "GEC", self), surum=SURUM_V2, python=sys.version.split()[0],
                 disk_bos_gb=round(bos, 1), kanca_nabzi_sn=None if z is None else round(time.time() - z, 1),
                 kurulum="bilinmiyor", yedek="bilinmiyor")
        ortak.atomik_yaz(self.yol("HAZIRLIK.json"), m)
        hatalar = []
        if bos < en_az: hatalar.append({"madde": "disk", "olcu": round(bos, 1), "esik": en_az, "seviye": "HATA"})
        if z is None or time.time() - z > KANCA_NABZI_MAX_SN:
            hatalar.append({"madde": "kanca_nabzi", "seviye": "BAYRAK", "not": "nabız yok; ajan görevleri basla'da reddedilir"})
        hatalar.append({"madde": "kurulum_ve_yedek", "seviye": "BAYRAK", "not": "KUR1 ve yedek doğrulaması PR-2b'de"})
        s = "HATA" if any(h["seviye"] == "HATA" for h in hatalar) else "BAYRAK"
        ortak.atomik_yaz(self.yol(g["rapor"]), {"_surum": 1, "_uretim": uretim_zarfi("A00", g["id"], s, self), "kapi": "HAZIRLIK",
                                                 "kapsam": "FILM", "tur": g["tur_no"], "sonuc": s, "hatalar": hatalar})
        return 0

    def ic_evren_ozeti(self, g):
        """A01: evren özeti → _HIKAYE_ODASI/EVREN_OZETI.md (yapımcının GIRDI'si; ajan evren klasörünü okuyamaz)."""
        seri = self.meta().get("seri")
        try:
            import evren
            o = evren.ozet(seri)
            metin = evren.ozet_md(o) if o.get("seriler") else "# Evren özeti\n\nKayıtlı seri yok; film yeni bir evren kurar.\n"
        except Exception as e:                       # evren kökü yoksa ya da okunamıyorsa: bilgi notu (hat durmaz)
            metin = f"# Evren özeti\n\nEvren okunamadı ({e.__class__.__name__}); film yeni bir evren kurar.\n"
        _metin_yaz(self.yol("_HIKAYE_ODASI", "EVREN_OZETI.md"), metin)
        return 0

    def kaset_betik_var(self, g):
        from saglayicilar import kaset as kaset_mod
        try: kaset_mod.bul(self.kok, g, "BETIK"); return True
        except kaset_mod.KasetYok: return False

    def betik_kos(self, g):
        if g["arac"] == "film.py:hazirlik": return self.ic_hazirlik(g)
        if g["arac"] == "film.py:evren_ozeti": return self.ic_evren_ozeti(g)
        if g["arac"] == "film.py:atla": return 0
        if self.sahte: return self.sahte_betik(g)
        p = os.path.join(HERE, g["arac"])
        if self.kaset and (self.kaset_betik_var(g) or not os.path.isfile(p)):
            from saglayicilar import kaset as kaset_mod     # kayıt varsa (ya da araç yoksa) kasetten; kaset uydurmaz
            try: return kaset_mod.betik_oynat(self.kok, g)[0]
            except kaset_mod.KasetYok as e: raise Hata(f"{g['arac']}: {e}", ORTAM)
        if self.kaset and g.get("kredili"):
            raise Hata(f"{g['arac']} kredili; kaset kipinde kasetsiz gerçek kredili araç koşmaz (BETIK kaydı gerekir).", ORTAM)
        env = dict(os.environ, YZ_FILM_GOREV=self.gorev_dizini(g), YZ_FILM_FILM=self.kok)
        with open(os.path.join(self.gorev_dizini(g), "CALISMA.log"), "a", encoding="utf-8") as log:
            arg = list(g["argumanlar"])
            if self.kok not in arg: arg += ["--film", self.kok]       # araç sözleşmesi: <arac> <alt komut/seçenekler> --film <film>
            r = subprocess.run([sys.executable, p] + arg, env=env, stdout=log, stderr=subprocess.STDOUT)
        return r.returncode

    def calis(self, gid, topla=False):
        g = self.g(gid)
        if g["durum"] == "bitti": return BITTI, {"gorev": gid, "durum": "bitti", "not": "zaten bitti; yeniden çalıştırılmadı"}
        if g["durum"] not in ACIK: raise Hata(f"{gid} artık geçerli değil ({g['durum']}); film.py sonraki.")
        if g["tur"] == "ajan":
            if self.kaset: return BITTI, self.kaset_ajan(g)
            if not self.sahte: raise Hata("Ajan görevi Agent aracıyla çalışır (film.py sonraki'nin istemiyle), calis ile değil.")
            return BITTI, self.sahte_ajan(g)
        if g["tur"] == "kullanici":
            if self.deneme: return BITTI, self.sahte_kullanici(g)
            return KULLANICI, {"gorev": gid, "kullaniciya": g["mesaj"]}
        ic = g["arac"].startswith("film.py:")
        if not ic and not self.sahte and not os.path.isfile(os.path.join(HERE, g["arac"])) \
                and not (self.kaset and self.kaset_betik_var(g)):
            raise Hata(f"{g['arac']} henüz yok (TASARIM §9'daki sonraki PR'larda gelir); bu aşama bu kurulumda yürüyemez.", ORTAM)
        with self.kilit():
            self.yeniden_oku(); g = self.g(gid)
            if g["durum"] == "bitti": return BITTI, {"gorev": gid, "durum": "bitti", "not": "zaten bitti"}
            if g.get("kredili") and g.get("gonderildi"):
                return self.topla(g)
            if g["durum"] == "calisiyor" and not g.get("kredili"):
                g["cikis_kodu"] = None                   # önceki çalıştırma kesilmiş; kredisiz betik yeniden koşar
            g["durum"] = "calisiyor"; g["zaman"]["basla"] = g["zaman"]["basla"] or simdi()
            if g.get("kredili"): g["gonderildi"] = simdi()    # gönderim kaydı ÖNCE (kör yeniden gönderim olmasın)
            self.yaz(g)
        _kesme("calis_basladi")
        kod = self.betik_kos(g)
        _kesme("calis_bitti")
        with self.kilit():
            self.yeniden_oku(); g = self.g(gid); g["cikis_kodu"] = kod; self.yaz(g)
            _kesme("cikis_kaydedildi")
            return self._betik_sonu(g, kod)

    def _betik_sonu(self, g, kod):
        gid = g["id"]
        if kod == 0:
            eksik = self.cikti_eksik(g)
            if eksik:
                g["durum"] = "gecersiz"; self.yaz(g)
                raise Hata(f"{g['arac']} 0 ile bitti ama çıktısı eksik: {', '.join(eksik)}", HATA, eksik=eksik)
            g["durum"] = "bitti"; g["zaman"]["bitir"] = simdi(); self.yaz(g); self.olay("bitti", gorev=gid)
            return BITTI, {"gorev": gid, "durum": "bitti"}
        if kod == BEKLE: return BEKLE, {"gorev": gid, "durum": "calisiyor", "kullaniciya": "İş sürüyor; bitince kendim devam ederim."}
        if kod in (KULLANICI, ORTAM, BUTCE, KISIT):
            if g.get("kredili") and g.get("gonderildi"): g["topla_gerek"] = True
            else: g["durum"] = "hazir"; g["zaman"]["basla"] = None
            self.yaz(g)
            return kod, {"gorev": gid, "durum": g["durum"], "cikis_kodu": kod}
        g["durum"] = "gecersiz"; self.yaz(g); self.olay("gecersiz", gorev=gid, cikis=kod)
        return HATA, {"gorev": gid, "durum": "gecersiz", "cikis_kodu": kod}

    def topla(self, g):
        """Kesilmiş kredili görev: yeni gönderim yok; sonucu topla. Bulunamazsa 'kayip' (o zaman yeni deneme açılır)."""
        gid = g["id"]
        if self.sahte:
            gonderim = any(s.get("is_kimligi") == gid for s in jsonl_oku(self.yol("KREDI_DEFTERI.jsonl")))
            if gonderim:
                self.sahte_ciktilar(g); g["cikis_kodu"] = 0; self.yaz(g)
                return self._betik_sonu(g, 0)
        elif self.kaset:                                  # kayıttan yeniden oynatma: gönderim yok, kredi yok
            kod = self.betik_kos(g); g["cikis_kodu"] = kod; self.yaz(g)
            return self._betik_sonu(g, kod)
        else:
            p = os.path.join(HERE, "memmet_topla.py")
            if not os.path.isfile(p):
                g["topla_gerek"] = True; self.yaz(g)
                raise Hata("Kesilen kredili iş kör yeniden gönderilmez; önce sonuç toplanır. Toplama aracı (memmet_topla.py) "
                           "henüz yok.", ORTAM)
            r = subprocess.run([sys.executable, p, self.kok, "--gorev", gid], capture_output=True, text=True)
            if r.returncode != 0: return BEKLE, {"gorev": gid, "kullaniciya": "Sonuç toplanıyor; kendim devam ederim."}
            if not self.cikti_eksik(g): return self._betik_sonu(g, 0)
        g["kayip"] = True; g["durum"] = "gecersiz"; self.yaz(g); self.olay("kayip", gorev=gid)
        return BITTI, {"gorev": gid, "durum": "gecersiz", "not": "gönderim bulunamadı (kayıp); sonraki yeni deneme açar"}

    def kurtar(self, yeniden_kur=False):
        out = {"kilit": None, "bitirildi": [], "kesildi": [], "toplanacak": []}
        if os.path.exists(self.yol("FILM.kilit")):
            k = Kilit(self.kok)
            if k.bayat() or yeniden_kur:
                os.remove(self.yol("FILM.kilit")); out["kilit"] = "bayat kilit kaldırıldı"
        with self.kilit():
            self.yeniden_oku()
            for g in sorted(self.gorevler().values(), key=lambda x: x["id"]):
                if g["durum"] != "calisiyor" or g["tur"] == "kullanici": continue
                if g["tur"] == "ajan":
                    if not self.cikti_eksik(g):
                        self.bitir(g["id"]); out["bitirildi"].append(g["id"]); continue
                elif g.get("kredili") and g.get("gonderildi"):
                    g["topla_gerek"] = True; self.yaz(g); out["toplanacak"].append(g["id"]); continue
                elif g.get("cikis_kodu") == 0 and not self.cikti_eksik(g):
                    self._betik_sonu(g, 0); out["bitirildi"].append(g["id"]); continue
                g["durum"] = "kesildi"; self.yaz(g); self.olay("kesildi", gorev=g["id"]); out["kesildi"].append(g["id"])
            durum_yaz(self, yeniden=yeniden_kur)
        return out


def uretim_zarfi(asama, gorev, sonuc, d=None, arac=SURUM_V2):
    return {"asama": asama, "gorev": gorev, "girdi_imza": None, "arac_surum": arac, "esik_surum": None, "sonuc": sonuc,
            "zaman": simdi(), "ortam": ortam()}


def karar_yaz(d, karar, neden=None, maliyet=None, asama=None, kaynak="ana_claude", tur="karar"):
    if neden is None and " — " in karar:
        p = [x.strip() for x in karar.split(" — ")]
        karar, neden, maliyet = p[0], (p[1] if len(p) > 1 else None), (p[2] if len(p) > 2 else maliyet)
    z = simdi()
    k = {"zaman": z, "asama": asama, "karar": karar, "neden": neden, "yanlissa_maliyeti": maliyet, "kaynak": [],
         "karar_veren": kaynak, "tur": tur}
    ad = f"{time.strftime('%Y%m%d-%H%M%S')}_{asama or 'FILM'}_{_yazi_duz(kaynak)[:20]}_{random.getrandbits(16):04x}.json"
    ortak.atomik_yaz(d.yol("kararlar", ad), k)
    satirlar = ["# Karar defteri (kararlar/ klasöründen türetilir; elle düzenlenmez)", ""]
    for f in sorted(glob.glob(d.yol("kararlar", "*.json"))):
        x = ortak.json_oku(f, {}) or {}
        satirlar.append(f"- {x.get('zaman', '')[:16]} · {x.get('asama') or 'FILM'} · {x.get('tur')} · {x.get('karar')}"
                        + (f" — {x['neden']}" if x.get("neden") else "") + (f" — {x['yanlissa_maliyeti']}" if x.get("yanlissa_maliyeti") else ""))
    _metin_yaz(d.yol("KARAR_DEFTERI.md"), "\n".join(satirlar) + "\n")
    return ad


def durum_hesapla(d, eski=None):
    eski = eski or {}
    asamalar, donguler = {}, {}
    aktif = None
    for a in HAT.ASAMALAR:
        if a.istege_bagli and not d.asama_gorevleri(a.kod): continue
        if d.atlanir(a): asamalar[a.kod] = {"durum": "tamam", "tur": 0, "not": "sahte denemede atlandı"}; continue
        c = d.coz(a)
        dur_ = c["durum"]
        if dur_ in ("calisiyor", "tavan"):
            e = c.get("eylem") or {}
            tip = {d.g(i)["tur"] for i in e.get("gorevler", [])} if e.get("tur") == "calis" else set()
            dur_ = "ajan_bekliyor" if "ajan" in tip else "kullanici_bekliyor" if "kullanici" in tip else "calisiyor"
        if dur_ == "butce": dur_ = "bekle"
        asamalar[a.kod] = {"durum": dur_, "tur": c.get("tur"), "girdi_imza": c.get("girdi_imza"), "rapor": c.get("rapor"),
                           "hedef_alti": bool(c.get("hedef_alti"))}
        if c.get("durdu"): asamalar[a.kod]["durdu"] = c["durdu"]
        if c.get("tur"): donguler[a.kod] = c["tur"]
        if aktif is None and dur_ not in ("tamam", "kismi"): aktif = a.kod
    gs = list(d.gorevler().values())
    kul = d.kuresel_kullanim()
    a12 = asamalar.get("A12", {})
    sahne = ortak.json_oku(d.yol("SAHNELER.json"), {}) or {}
    pimza = plan_imzalari(sahne); bayat = []
    for k in glob.glob(d.yol("KUNYE", "[0-9][0-9][0-9].json")):
        x = ortak.json_oku(k, {}) or {}; no = str(int(os.path.basename(k)[:3]))
        if x.get("plan_imza") and pimza.get(no) and x["plan_imza"] != pimza[no]: bayat.append(no)
    durdu = sorted({p for v in asamalar.values() for p in v.get("durdu", [])})
    m = d.meta()
    return {"_surum": 2, "_uretim": {"asama": "film.py", "arac_surum": SURUM_V2, "zaman": simdi(), "ortam": ortam()},
            "film": d.ad, "seri": m.get("seri"), "ortam_son": ortam(), "saglayici": m.get("saglayici"), "aktif_asama": aktif,
            "otomatik_surus": eski.get("otomatik_surus") or {"acik": True, "neden": None, "ardisik_devam": 0},
            "asamalar": asamalar,
            "donguler": dict(donguler, kagit=donguler.get("A06", 0), animatik=donguler.get("A12", 0), kurgu=donguler.get("A16", 0),
                             h15=kul.get("h15", 0), kart_tarif=kul.get("kart_tarif", 0)),
            "kuresel_butce": {ad: {"kullanilan": kul.get(ad, 0), "tavan": t} for ad, t in KURESEL_TAVAN.items()},
            "animatik": _animatik_durumu(d, a12),
            "bekleyen_kullanici": [g["id"] for g in gs if g["tur"] == "kullanici" and g["durum"] in ACIK] or None,
            "sayaclar": {"gorev": len(gs), "ajan": sum(g["tur"] == "ajan" for g in gs), "betik": sum(g["tur"] == "betik" for g in gs),
                         "kullanici_eylemi": sum(g["tur"] == "kullanici" for g in gs),
                         "nabiz_reddi": sum(1 for o in jsonl_oku(os.path.join(d.gd, "DEFTER.jsonl")) if o.get("olay") == "nabiz_reddi")},
            "harcama": d.harcama(), "durdu_planlar": durdu, "plan_imza": pimza, "bayat_planlar": sorted(bayat),
            "gecmis": jsonl_oku(os.path.join(d.gd, "DEFTER.jsonl"))[-20:],
            "model_sapmasi": [g["id"] for g in gs if g["durum"] == "model_sapmasi"]}


def _animatik_durumu(d, a12):
    """FILM_DURUM.animatik (memmet.py v2 bunu okur). Sahte denemede A12'nin defter durumu; gerçek filmde animatik_imza.durum."""
    if d.sahte:
        ok = a12.get("durum") in ("tamam", "kismi")
        return {"durum": "ONAYLI" if ok else "bekliyor", "imza": a12.get("girdi_imza") if ok else None}
    try:
        import animatik_imza
        return animatik_imza.durum(d.kok)
    except Exception as e:
        return {"durum": "bekliyor", "imza": None, "neden": f"animatik imzası okunamadı ({e.__class__.__name__})"}


def durum_yaz(d, yeniden=False):
    p = d.yol("FILM_DURUM.json")
    eski = None if yeniden else ortak.json_oku(p, {})
    if isinstance(eski, dict) and eski.get("_surum") != 2: eski = {}
    st = durum_hesapla(d, eski)
    ortak.atomik_yaz(p, st)
    return st


# ---- film bulma ve komutlar --------------------------------------------------------------------------------------
def aktif_dosyasi(): return os.path.join(ortak.yollar()["filmler"], "_AKTIF.json")


def film_bul(arg=None, zorunlu=True):
    if arg:
        if os.path.isdir(arg): return Defter(arg)
        p = os.path.join(ortak.yollar()["filmler"], arg)
        if os.path.isdir(p): return Defter(p)
        raise Hata(f"Film bulunamadı: {arg}")
    a = ortak.json_oku(aktif_dosyasi(), {}) or {}
    if a.get("yol") and os.path.isdir(a["yol"]): return Defter(a["yol"])
    if zorunlu: raise Hata("Aktif film yok.", KULLANICI)
    return None


def k_yeni(o):
    if ortam() == "bulut" and o.saglayici not in ("sahte", "kaset"):
        return ORTAM, {"kullaniciya": BULUT_CUMLESI, "not": "D-45: bulutta film yalnız --saglayici sahte|kaset ile açılır"}
    if not (o.konu or "").strip(): raise Hata("Konu boş. Kullanım: film.py yeni --konu \"<cümle>\"")
    ad = o.ad or f"F{time.strftime('%Y%m%d')}_{_yazi_duz(o.konu)[:24] or 'film'}"
    kok = os.path.join(ortak.yollar()["filmler"], ad)
    if os.path.exists(os.path.join(kok, "HAZIRLIK.json")): raise Hata(f"Bu adla film zaten var: {ad}")
    d = Defter(kok); os.makedirs(kok, exist_ok=True)
    with d.kilit():
        _metin_yaz(d.yol("00_KONU.md"), f"# Konu\n\n{o.konu.strip()}\n")
        ortak.atomik_yaz(d.yol("HAZIRLIK.json"), {"_uretim": uretim_zarfi("A00", None, "GEC", d), "film": ad, "seri": o.seri,
                                                  "konu": o.konu.strip(), "saglayici": o.saglayici, "ortam": ortam(),
                                                  "surum": SURUM_V2, "olusturma": simdi()})
        ortak.atomik_yaz(aktif_dosyasi(), {"film": ad, "yol": kok, "zaman": simdi()})
        d.olay("film_yeni", film=ad)
        durum_yaz(d)
    return BITTI, {"film": ad, "yol": kok, "kullaniciya": "Film açıldı; ekip işe başlıyor."}


def _kisa_ciktisi(r, d):
    r = dict(r); r.setdefault("gorevler", []); r.setdefault("kullaniciya", None); r.setdefault("oku", None)
    out = {"film": d.ad, "asama": r.get("asama"), "tur_no": r.get("tur_no"), "cikis_kodu": r["cikis_kodu"], "tur": r["tur"],
           "gorevler": r["gorevler"], "kullaniciya": r["kullaniciya"], "oku": r["oku"]}
    while len(json.dumps(out, ensure_ascii=False)) > SONRAKI_MAX_KR and len(out["gorevler"]) > 1: out["gorevler"].pop()
    return out


def k_sonraki(o):
    d = film_bul(o.film, zorunlu=False)
    if d is None:
        if ortam() == "bulut": return ORTAM, {"tur": "ortam", "cikis_kodu": ORTAM, "kullaniciya": BULUT_CUMLESI}
        return KULLANICI, {"tur": "konu_sor", "cikis_kodu": KULLANICI, "kullaniciya": TEK_SORU}
    with d.kilit():
        r = d.ilerle()
        durum_yaz(d)
    r = _kisa_ciktisi(r, d)
    return r["cikis_kodu"], r


def _ids(s): return [x for x in re.split(r"[,\s]+", s or "") if x]


def k_basla(o):
    d = film_bul(o.film); r = d.basla(_ids(o.idler))
    with d.kilit(): durum_yaz(d)
    return BITTI, r


def k_calis(o):
    d = film_bul(o.film)
    kod, r = d.calis(o.id, topla=o.topla)
    with d.kilit(): durum_yaz(d)
    return kod, r


def k_bitir(o):
    d = film_bul(o.film)
    kul = json.loads(o.kullanim) if o.kullanim else None
    r = d.bitir(o.id, kul, gecersiz=o.gecersiz)
    with d.kilit(): durum_yaz(d)
    return BITTI, r


def k_kurtar(o):
    d = film_bul(o.film); return BITTI, d.kurtar(o.yeniden_kur)


def k_asama_ilerlet(o):
    d = film_bul(o.film); return BITTI, d.asama_ilerlet(o.id)


def k_bekle(o):
    d = film_bul(o.film)
    g = d.g(o.kullanici) if o.kullanici else None
    if o.blok and not g:
        g = next((x for x in d.gorevler().values() if x["tur"] == "kullanici" and x["durum"] in ACIK
                  and (x.get("algilama") or {}).get("tur") == "blok" and (x["algilama"].get("blok") in (o.blok, "*"))), None)
    if not g and not o.blok: raise Hata("Beklenecek iş yok: --kullanici <id> ya da --blok <B>.")
    sure = (o.sure if o.sure is not None else esik("bekle_azami_dk") or 110) * 60
    t0 = time.time(); n = 0
    while True:
        bitti = d.algilandi(g) if g else d.blok_bitti(o.blok)
        if g and g["durum"] == "bitti": bitti = True
        if bitti:
            if g and g["durum"] != "bitti":
                with d.kilit(): d.yeniden_oku(); d.kullanici_bitti(d.g(g["id"])); durum_yaz(d)
            return BITTI, {"bitti": True, "gorev": g and g["id"], "kullaniciya": "Bekleyen iş geldi; devam ediyorum."}
        n += 1
        if g:
            bas = _zaman_oku(g["zaman"].get("basla")) or t0; son = _zaman_oku(g.get("hatirlatma")) or bas
            if time.time() - son > 6 * 3600:
                d.log(f"HATIRLATMA {g['id']}: {g['mesaj']}"); g["hatirlatma"] = simdi()
                try:
                    import bildirim                     # Telegram/masaüstü (§8.4); tekrar ve saat tavanını bildirim.py uygular
                    bildirim.gonder("kullanici_isi", "Hatırlatma: " + str(g["mesaj"]), film=d.kok, anahtar=g["id"])
                except Exception: pass
                with d.kilit(): d.yaz(g)
        if (o.kez and n >= o.kez) or time.time() - t0 + o.aralik > sure:
            return BEKLE, {"bitti": False, "gorev": g and g["id"],
                           "kullaniciya": "Hâlâ bekleniyor; film.py bekle'yi yeniden başlat."}
        uyu(o.aralik); d.yeniden_oku()
        if g: g = d.g(g["id"])


def k_karar(o):
    d = film_bul(o.film)
    ad = karar_yaz(d, o.metin, o.neden, o.maliyet, asama=o.asama, kaynak=o.kaynak, tur=o.tur)
    return BITTI, {"kayit": f"kararlar/{ad}"}


def k_ders(o):
    d = film_bul(o.film, zorunlu=False)
    k = {"zaman": simdi(), "film": d.ad if d else None, "seri": d.meta().get("seri") if d else None, "ortam": ortam(),
         "olay": o.olay, "asama": o.asama, "kapi": o.kapi, "madde": o.madde, "plan": o.plan, "kategori": None,
         "rol_etiketi": o.rol, "kaynak": o.kaynak, "belirti": o.belirti, "olcum": None, "baglam": {}, "kanit": [],
         "eylem": None, "sonuc": None, "maliyet": None}
    if ders_defteri_mod is not None:
        alan = {x: k[x] for x in ("film", "seri", "asama", "kapi", "madde", "plan", "rol_etiketi", "ortam")}
        try: return BITTI, {"kayit": ders_defteri_mod.kaydet(o.olay, o.kaynak, o.belirti, **alan)}
        except ValueError as e: raise Hata(f"Ders kaydı geçersiz: {e}")
    k["id"] = f"D-{time.strftime('%Y%m%d')}-{random.getrandbits(16):04x}"
    p = os.path.join(ortak.yollar()["veri_kok"], "BILGI", "DERSLER", "ham",
                     f"{time.strftime('%Y%m%dT%H%M%S')}_{k['film'] or 'SISTEM'}_{o.olay}_{random.getrandbits(12):03x}.json")
    ortak.atomik_yaz(p, k)
    return BITTI, {"kayit": p, "id": k["id"]}


GIZLI = re.compile(r"anahtar|token|key|secret|sifre|parola|password|api", re.I)


def maskele(x):
    if isinstance(x, dict): return {k: ("***" if GIZLI.search(k) and isinstance(v, str) and v else maskele(v)) for k, v in x.items()}
    if isinstance(x, list): return [maskele(v) for v in x]
    return x


def k_goster(o):
    ne = o.ne; arg = o.arg
    if ne == "ayar":
        return BITTI, {"FILM_AYAR": maskele(ortak.json_oku(ayar_dosyasi(), {}) or {}), "not": "anahtar dosyaları gösterilmez"}
    if ne == "pencere":
        return ORTAM, {"kullaniciya": "Pencere görüntüsü (salt okunur PrintWindow) henüz yok; P1'de gelir."}
    if ne == "sozlesme":
        a = (ortak.json_oku(ayar_dosyasi(), {}) or {}).get("butce") or {}
        return BITTI, {"sozlesme": {"butce": a, "not": "sayılar olcek.py'den gelir (BUT0/BUT1/BUT2); kullanıcı yalnız fiziksel iş yapar"}}
    d = film_bul(o.film)
    st = durum_hesapla(d, ortak.json_oku(d.yol("FILM_DURUM.json"), {}))      # salt okunur (film-durum becerisi)
    if ne == "durum": return BITTI, {k: st[k] for k in ("film", "aktif_asama", "asamalar", "bekleyen_kullanici", "sayaclar")}
    if ne == "asama":
        a = HAT.asama(arg); c = d.coz(a)
        return BITTI, {"asama": a.kod, "ad": a.ad, "durum": c["durum"], "tur": c.get("tur"),
                       "gorevler": [{"id": g["id"], "durum": g["durum"], "tur": g["tur"], "tur_no": g.get("tur_no")}
                                    for g in d.asama_gorevleri(a.kod)]}
    if ne == "gorev": return BITTI, d.g(arg)
    if ne == "plan":
        plan = ortak.json_oku(d.yol("SAHNELER.json"), {}) or {}
        for x in list(plan.get("sahneler") or []) + list(plan.get("planlar") or []):
            if str(x.get("no", x.get("id"))).lstrip("0") == str(arg).lstrip("0"): return BITTI, x
        raise Hata(f"Plan yok: {arg}")
    if ne == "maliyet": return BITTI, {k: v for k, v in st["harcama"].items() if k != "token"}
    if ne == "token": return BITTI, dict(st["harcama"]["token"], tavan=esik("film_token_tavan"))
    if ne == "neden-durdu":
        r = d.ilerle(salt_okunur=True)
        return BITTI, {"asama": r.get("asama"), "tur": r["tur"], "cikis_kodu": r["cikis_kodu"], "neden": r.get("kullaniciya")}
    if ne == "karar":
        p = d.yol("KARAR_DEFTERI.md")
        return BITTI, {"karar_defteri": _bayt(p).decode("utf-8").splitlines()[-30:] if os.path.exists(p) else []}
    if ne == "plan-imza": return BITTI, {"plan_imza": st["plan_imza"], "bayat_planlar": st["bayat_planlar"]}
    raise Hata(f"Bilinmeyen: goster {ne}")


def k_ozet(o):
    try:
        d = film_bul(o.film, zorunlu=False)
        if d is None:
            m = BULUT_CUMLESI if ortam() == "bulut" else "Aktif film yok; konu bekleniyor."
            return BITTI, {"ozet": m, "film": None}
        st = durum_hesapla(d, ortak.json_oku(d.yol("FILM_DURUM.json"), {}))
        r = d.ilerle(salt_okunur=True)
        aa = st["aktif_asama"]
        a = HAT.asama(aa) if aa else None
        satirlar = [f"Film: {d.ad}" + (" (sahte deneme)" if d.sahte else ""),
                    f"Aşama: {a.kod} {a.ad} (tur {st['asamalar'][aa].get('tur')})" if a else "Aşama: bitti",
                    f"Şimdi: {r.get('kullaniciya') or r['tur']}"]
        if o.uzun:
            satirlar += [f"  {k:5} {v['durum']}" + (" · hedef altı" if v.get("hedef_alti") else "") for k, v in st["asamalar"].items()]
            h = st["harcama"]; satirlar.append(f"Harcama: Flow {h['flow_kredi']} kr · AI84 {h['ai84_kredi']} kr · token "
                                               f"{h['token']['girdi'] + h['token']['cikti']}")
        if o.kullanici: satirlar = satirlar[:3]
        return BITTI, {"ozet": "\n".join(satirlar), "film": d.ad, "aktif_asama": aa, "tur": r["tur"]}
    except Exception as e:                       # özet her durumda 0 döner (beceri içindeki ! komutu)
        return BITTI, {"ozet": f"Özet alınamadı: {e}"}


def k_surus(o):
    d = film_bul(o.film, zorunlu=False)
    if d is None: return BITTI, {"not": "aktif film yok"}
    with d.kilit():
        st = durum_hesapla(d, ortak.json_oku(d.yol("FILM_DURUM.json"), {}))
        neden = "soru" if o.soru else "gelistirme" if o.gelistirme else ("kullanici" if o.ne == "kapat" else None)
        st["otomatik_surus"] = {"acik": o.ne == "ac", "neden": neden, "ardisik_devam": 0, "tek_tur": bool(o.soru)}
        ortak.atomik_yaz(d.yol("FILM_DURUM.json"), st)
    return BITTI, {"otomatik_surus": st["otomatik_surus"]}


def k_notlar(o):
    d = film_bul(o.film)
    if o.ne == "oku":
        out = {}
        for arac in ("notlari_oku.py", "taslak_fark.py"):
            p = os.path.join(HERE, arac)
            if not os.path.isfile(p): out[arac] = "henüz yok"; continue
            r = subprocess.run([sys.executable, p, d.kok], capture_output=True, text=True, encoding="utf-8", errors="replace")
            out[arac] = {"cikis": r.returncode, "cikti": r.stdout[-3000:]}
        return BITTI, out
    a = HAT.asama("A16n")
    with d.kilit():
        gs = d.asama_gorevleri("A16n")
        c = d.coz(a) if gs else None
        if not gs or c["durum"] in ("tamam", "kismi"):
            s = max([g.get("surum", 0) for g in gs] or [0]) + 1
            d.grup_ac(a, {"surum": s, "tur_no": 1, "merdiven": None})
        r = d.ilerle(); durum_yaz(d)
    r = _kisa_ciktisi(r, d)
    return r["cikis_kodu"], r


def k_beceri_denetim(o):
    p = os.path.join(HERE, "beceri_denetim.py")
    if not os.path.isfile(p): return ORTAM, {"kullaniciya": "beceri_denetim.py henüz yok (PR-4)."}
    return subprocess.run([sys.executable, p] + o.rest).returncode, None


def k_olcum0(o):
    harfler = "abcdefgh"
    try: k = os.path.join(ortak.yollar()["veri_kok"], "BILGI", "OLCUM0")
    except ortak.YolYok: raise
    durum = {f"Ö0-{h}": os.path.exists(os.path.join(k, f"O0{h}.json")) for h in harfler}
    if all(durum.values()): return BITTI, {"olcum0": durum}
    if ortam() == "bulut": return ORTAM, {"olcum0": durum, "kullaniciya": "Ö0 ölçümleri yalnız kullanıcının bilgisayarında yapılır."}
    if not os.path.isdir(os.path.join(HERE, "olcum0")):
        return ORTAM, {"olcum0": durum, "kullaniciya": "olcum0/ betikleri henüz yok (TASARIM §9 adım 9)."}
    return BITTI, {"olcum0": durum}


def k_asamalar(o):
    if o.json_: return BITTI, HAT.sozluk()
    print(HAT.markdown(), end=""); return BITTI, None


def k_esitle(o):
    if o.gelistirme:
        import esitle_gelistirme
        return esitle_gelistirme.main(o.rest), None
    return ORTAM, {"kullaniciya": "Tam bulut ↔ yerel eşitleme P2'de gelir (TASARIM D-12). Geliştirme dosyaları için: "
                                  "film.py esitle --gelistirme"}


def _ayristirici():
    import argparse
    p = argparse.ArgumentParser(prog="film.py", add_help=True)
    ortak_ = argparse.ArgumentParser(add_help=False)
    ortak_.add_argument("--film"); ortak_.add_argument("--json", action="store_true", dest="json_")
    alt = p.add_subparsers(dest="komut", required=True)
    s = alt.add_parser("yeni", parents=[ortak_]); s.add_argument("--konu", required=True); s.add_argument("--ad")
    s.add_argument("--seri"); s.add_argument("--saglayici", choices=["sahte", "kaset"]); s.set_defaults(f=k_yeni)
    alt.add_parser("sonraki", parents=[ortak_]).set_defaults(f=k_sonraki)
    s = alt.add_parser("basla", parents=[ortak_]); s.add_argument("idler"); s.set_defaults(f=k_basla)
    s = alt.add_parser("calis", parents=[ortak_]); s.add_argument("id"); s.add_argument("--topla", action="store_true")
    s.set_defaults(f=k_calis)
    s = alt.add_parser("bitir", parents=[ortak_]); s.add_argument("id"); s.add_argument("--kullanim")
    s.add_argument("--gecersiz", metavar="NEDEN"); s.set_defaults(f=k_bitir)
    s = alt.add_parser("kurtar", parents=[ortak_]); s.add_argument("--yeniden-kur", action="store_true", dest="yeniden_kur")
    s.set_defaults(f=k_kurtar)
    s = alt.add_parser("asama-ilerlet", parents=[ortak_]); s.add_argument("id"); s.set_defaults(f=k_asama_ilerlet)
    s = alt.add_parser("bekle", parents=[ortak_]); s.add_argument("--kullanici"); s.add_argument("--blok")
    s.add_argument("--kez", type=int); s.add_argument("--aralik", type=float, default=30.0); s.add_argument("--sure", type=float)
    s.set_defaults(f=k_bekle)
    s = alt.add_parser("karar", parents=[ortak_]); s.add_argument("ekle", choices=["ekle"]); s.add_argument("metin")
    s.add_argument("--neden"); s.add_argument("--maliyet"); s.add_argument("--asama"); s.add_argument("--kaynak", default="ana_claude")
    s.add_argument("--tur", default="karar", choices=["karar", "soru", "bilgi", "kullanici_notu", "red", "yama"])
    s.set_defaults(f=k_karar)
    s = alt.add_parser("ders", parents=[ortak_]); s.add_argument("ekle", choices=["ekle"]); s.add_argument("--kapi")
    s.add_argument("--belirti", required=True); s.add_argument("--olay", default="kullanici_notu")
    s.add_argument("--kaynak", default="kullanici_notu"); s.add_argument("--plan", type=int); s.add_argument("--asama")
    s.add_argument("--madde"); s.add_argument("--rol"); s.set_defaults(f=k_ders)
    s = alt.add_parser("goster", parents=[ortak_]); s.add_argument("ne"); s.add_argument("arg", nargs="?")
    s.set_defaults(f=k_goster)
    s = alt.add_parser("ozet", parents=[ortak_])
    for x in ("--kisa", "--uzun", "--kullanici"): s.add_argument(x, action="store_true")
    s.set_defaults(f=k_ozet)
    s = alt.add_parser("surus", parents=[ortak_]); s.add_argument("ne", choices=["ac", "kapat"])
    s.add_argument("--soru", action="store_true"); s.add_argument("--gelistirme", action="store_true"); s.set_defaults(f=k_surus)
    s = alt.add_parser("notlar", parents=[ortak_]); s.add_argument("ne", choices=["oku", "isle"]); s.set_defaults(f=k_notlar)
    s = alt.add_parser("beceri-denetim", parents=[ortak_]); s.add_argument("rest", nargs="*"); s.set_defaults(f=k_beceri_denetim)
    alt.add_parser("olcum0", parents=[ortak_]).set_defaults(f=k_olcum0)
    s = alt.add_parser("asamalar", parents=[ortak_]); s.add_argument("--md", action="store_true"); s.set_defaults(f=k_asamalar)
    s = alt.add_parser("esitle", parents=[ortak_]); s.add_argument("--gelistirme", action="store_true")
    s.set_defaults(f=k_esitle)
    return p


KOMUTLAR = ("yeni", "sonraki", "basla", "calis", "bitir", "kurtar", "asama-ilerlet", "bekle", "karar", "ders", "goster", "ozet",
            "surus", "notlar", "beceri-denetim", "olcum0", "asamalar", "esitle")


def _yazdir(r, json_mod):
    if r is None: return
    if json_mod or not isinstance(r, dict): print(json.dumps(r, ensure_ascii=False, indent=None if json_mod else 1)); return
    if set(r) <= {"ozet", "film", "aktif_asama", "tur"} and "ozet" in r: print(r["ozet"]); return
    print(json.dumps(r, ensure_ascii=False, indent=1))


def v2_main(a):
    p = _ayristirici()
    if a[0] in ("esitle", "beceri-denetim"):
        o, rest = p.parse_known_args(a); o.rest = rest + getattr(o, "rest", [])
    else: o = p.parse_args(a)
    json_mod = getattr(o, "json_", False) or o.komut == "sonraki"
    try:
        kod, r = o.f(o)
    except Hata as e:
        r = dict({"hata": str(e), "cikis_kodu": e.kod}, **e.ek); kod = e.kod
    except ortak.YolYok as e:
        r = {"hata": str(e), "cikis_kodu": ORTAM}; kod = ORTAM
    if o.komut == "ozet": kod = BITTI
    _yazdir(r, json_mod)
    return kod


# ---- v1 ---------------------------------------------------------------------------------------------------------
def argumanlar(a):
    args = {"tam_otomatik": "--tam-otomatik" in a}
    for k in ("--asama", "--parti", "--saglayici", "--sifirla"):
        if k in a:
            v = a[a.index(k) + 1]
            args[k[2:]] = [int(x) for x in v.split(",")] if k == "--parti" else v.split(",") if k == "--asama" else v
    return args


def main(a=None):
    a = sys.argv[1:] if a is None else a
    if a and a[0] in KOMUTLAR: return v2_main(a)
    if not a or a[0].startswith("-"): print(__doc__); return 0
    try: f = Film(a[0], argumanlar(a))
    except ortak.YolYok as e: print("!!", e); return 4
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
