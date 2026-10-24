"""SES DÖNÜŞTÜR — SC1 metin kapısı (--hizala) ve konuşma ayrıştırma (--ayristir); dönüşüm (--donustur, --egit) ses_donustur_ana.py'de
(TASARIM §2.2 karar 1, §6.6; [SM2] SC1, S2.1–S2.6).

Kullanım:
  python ses_donustur.py --hizala [<plan,…>] [--blok B03] --film <film>
        her indirilen konuşmalı klipte: (ayrıştırma →) VAD + serbest ASR replik penceresi ±1 sn → WER (S2.2), ad doğruluğu (S2.3),
        tasidigi kelimeleri (S2.4), ağzı en çok oynayan yüz (S2.5), konuşma hızı (S2.6), konuşma var mı (S2.1).
        → SESLER/hizalama/NNN.json, _RAPOR/S2m_<blok|FILM>.json (kuyruk önerileri: kaynak_kapi S2m), KUNYE/NNN.json kapilar.SC1
  python ses_donustur.py --ayristir <plan,…> --film <film>      SESLER/ayrik/NNN_{konusma,diger}.wav (audio-separator; yoksa ÖLÇÜLEMEDİ)
  python ses_donustur.py --donustur … | --egit …                ses_donustur_ana.py'ye geçer (PR-12)
Kodda: import ses_donustur; ses_donustur.hizala(film, [121, 122], blok="B03")   (memmet.py blok sonunda çağırır)
Arka uçlar (sırayla): _KASET/SC1/NNN.json (testler; {"kelimeler": [{"w","bas","bit"}], "konusan_yuz": "mara"}) · stable-ts (stable_whisper,
  MIT) · faster-whisper (MIT). Hiçbiri yoksa ölçüm ÖLÇÜLEMEDİ (= BAYRAK; asla GEÇ değil). Ayrıştırma (audio-separator, MIT) yoksa ASR
  karışık sese yapılır ve BAYRAK yazılır. Ağız/yüz denetimi olcum.dudak + olcum.kimlik ister; yoksa ÖLÇÜLEMEDİ.
Eşikler: ses_esikleri.json replik_wer_gri_bant [0,10; 0,25] (üstü HATA, içi replik_kabul); pencere payı 1 sn; hız 1,8–3,2 kelime/sn (tahmin).
Bu araç Flow'a dokunmaz; yalnız inmiş dosyayı okur.
Çıkış kodları: 0 rapor yazıldı (HATA olsa da) · 1 girdi yok/bozuk · 4 kullanım.
"""
import os, sys, re, json, glob, time, shutil, subprocess
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "ses_donustur 1.0 (SC1)"
PENCERE_PAY_SN = 1.0                # [SM2] whisper_pencere_pay_sn (tahmin)
HIZ_BANT = (1.8, 3.2)               # S2.6 (tahmin)
SAYILAR = {"0": "zero", "1": "one", "2": "two", "3": "three", "4": "four", "5": "five", "6": "six", "7": "seven", "8": "eight",
           "9": "nine", "10": "ten"}


def _esik(ad, v):
    try:
        import esikler; x = esikler.yukle().get(ad); return v if x is None else x
    except Exception: return v


def normal_kelimeler(metin):
    """Küçük harf, noktalama ve kesme işareti temizliği, rakam → kelime (S2.2 normalleştirme)."""
    t = (metin or "").lower().replace("’", "'")
    t = re.sub(r"[^\w\s']", " ", t)
    out = []
    for w in t.split():
        w = w.replace("'", "")
        if not w: continue
        out.append(SAYILAR.get(w, w))
    return out


def wer(ref, hyp):
    """Kelime hata oranı (Levenshtein / ref uzunluğu)."""
    r, h = normal_kelimeler(ref), normal_kelimeler(hyp)
    if not r: return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        onceki, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            gecici = d[j]
            d[j] = min(d[j] + 1, d[j - 1] + 1, onceki + (r[i - 1] != h[j - 1]))
            onceki = gecici
    return round(d[len(h)] / len(r), 4)


# ---------------------------------------------------------------- arka uçlar
class Olculemedi(Exception): pass


def _kaset(film, no):
    return ortak.json_oku(os.path.join(film, "_KASET", "SC1", f"{int(no):03d}.json"), None)


def _asr_gercek(wav):
    try:
        import stable_whisper                       # stable-ts (MIT)
        m = stable_whisper.load_model("small")
        r = m.transcribe(wav, language="en", word_timestamps=True)
        return [{"w": w.word.strip(), "bas": float(w.start), "bit": float(w.end)} for s in r.segments for w in s.words], "stable-ts"
    except ImportError: pass
    try:
        from faster_whisper import WhisperModel     # faster-whisper (MIT)
        m = WhisperModel("small", device="auto")
        segs, _ = m.transcribe(wav, language="en", word_timestamps=True, vad_filter=True)
        return [{"w": w.word.strip(), "bas": float(w.start), "bit": float(w.end)} for s in segs for w in (s.words or [])], "faster-whisper"
    except ImportError: pass
    raise Olculemedi("ASR yok (stable-ts / faster-whisper kurulu değil; KUR2)")


def ayristir(film, no):
    """(konuşma wav yolu, ayrıştı_mı). audio-separator yoksa klibin karışık sesi (BAYRAK)."""
    klip = os.path.join(film, "SIRALI_VIDEO", f"{int(no):03d}.mp4")
    d = os.path.join(film, "SESLER", "ayrik"); os.makedirs(d, exist_ok=True)
    kar = os.path.join(d, f"{int(no):03d}_karisik.wav")
    if not shutil.which("ffmpeg"): raise Olculemedi("ffmpeg yok")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", klip, "-vn", "-ac", "1", "-ar", "48000", kar], check=True)
    try:
        from audio_separator.separator import Separator   # python-audio-separator (MIT); BS-RoFormer modeli
    except ImportError: return kar, False
    s = Separator(output_dir=d); s.load_model()
    cikan = s.separate(kar)
    konusma = next((os.path.join(d, c) for c in cikan if "vocal" in c.lower()), None)
    if not konusma: return kar, False
    hedef = os.path.join(d, f"{int(no):03d}_konusma.wav"); os.replace(konusma, hedef)
    return hedef, True


def dinle(film, no):
    """{kelimeler, kaynak, ayrisma, konusan_yuz?}. Ölçülemezse Olculemedi."""
    k = _kaset(film, no)
    if isinstance(k, dict): return {"kelimeler": k.get("kelimeler") or [], "kaynak": "kaset", "ayrisma": True, "konusan_yuz": k.get("konusan_yuz")}
    wav, ayr = ayristir(film, no)
    kel, kaynak = _asr_gercek(wav)
    return {"kelimeler": kel, "kaynak": kaynak, "ayrisma": ayr, "konusan_yuz": _konusan_yuz(film, no)}


def _konusan_yuz(film, no):
    try:
        from olcum import dudak                      # adım 12 (görüntü) ölçüm paketi
        return dudak.en_cok_oynayan(os.path.join(film, "SIRALI_VIDEO", f"{int(no):03d}.mp4"))
    except Exception: return None


# ---------------------------------------------------------------- değerlendirme
def _adlar(doc):
    out = {}
    for k, v in (doc.get("karakterler") or {}).items():
        ad = (v or {}).get("ad") or k
        out[k] = [w for w in normal_kelimeler(ad)]
    return out


def degerlendir(p, d, doc):
    """Bir plan için S2.1–S2.6 ölçümleri (kapi ölçüm listesi) + hizalama kaydı."""
    no = int(p["no"]); rp = p.get("replik") or {}; metin = rp.get("veo_metin") or rp.get("metin") or ""
    rz = ((p.get("_derlenir") or {}).get("replik_zaman") or {}).get(rp.get("id")) or [0, float((p.get("zanaat") or {}).get("klip_sn") or 8)]
    a, b = float(rz[0]) - PENCERE_PAY_SN, float(rz[1]) + PENCERE_PAY_SN
    kel = [w for w in d["kelimeler"] if a <= float(w.get("bas", 0)) <= b]
    duyulan = " ".join(w["w"] for w in kel)
    olc = []
    def o(madde, seviye, **k): olc.append(dict({"madde": madde, "plan": no, "seviye": seviye}, **k))
    if not d.get("ayrisma"): o("ayrisma", "BAYRAK", neden="konuşma ayrıştırılamadı; ASR karışık seste")
    if not kel:
        o("S2.1", "HATA", neden="replik penceresinde konuşma yok", kok_neden="veo_konusmadi")
        return olc, {"duyulan_metin": "", "kelimeler": [], "wer": None}
    o("S2.1", "GEC")
    w = wer(metin, duyulan); gri = _esik("replik_wer_gri_bant", [0.10, 0.25])
    if w <= gri[0]: o("S2.2", "GEC", olcu=w)
    elif w <= gri[1]: o("S2.2", "BAYRAK", olcu=w, esik=gri, oneri="hikaye-yazari·replik_kabul (gri bant)", kok_neden="veo_metin_sapti")
    else: o("S2.2", "HATA", olcu=w, esik=gri[1], kok_neden="veo_metin_sapti")
    hyp = set(normal_kelimeler(duyulan)); ref = normal_kelimeler(metin)
    adlar = _adlar(doc); yanlis = []
    for k, parca in adlar.items():
        for x in parca:
            if x in ref and x not in hyp: yanlis.append(x)
    if yanlis: o("S2.3", "HATA", olcu={"duyulmayan_ad": sorted(set(yanlis))}, kok_neden="ad_yanlis_okundu")
    else: o("S2.3", "GEC")
    tas = [x for t in rp.get("tasidigi") or [] for x in normal_kelimeler(t)]
    eksik = [x for x in tas if x not in hyp]
    if eksik: o("S2.4", "BAYRAK", olcu=eksik, oneri="hikaye-yazari·replik_kabul", kok_neden="veo_metin_sapti")
    elif tas: o("S2.4", "GEC")
    ky = d.get("konusan_yuz")
    if ky is None: o("S2.5", "OLCULEMEDI", neden="ağız/yüz ölçümü yok (olcum.dudak)")
    elif ky != rp.get("karakter"): o("S2.5", "HATA", olcu=ky, esik=rp.get("karakter"), kok_neden="yanlis_kisi_konustu")
    else: o("S2.5", "GEC")
    sure = max(0.01, float(kel[-1]["bit"]) - float(kel[0]["bas"])); hiz = round(len(kel) / sure, 2)
    o("S2.6", "GEC" if HIZ_BANT[0] <= hiz <= HIZ_BANT[1] else "BAYRAK", olcu=hiz, esik=list(HIZ_BANT))
    return olc, {"duyulan_metin": duyulan, "kelimeler": kel, "wer": w, "hiz_kelime_sn": hiz, "konusan_yuz": ky,
                 "klip_zamani": {"bas": float(kel[0]["bas"]), "bit": float(kel[-1]["bit"])}}


def _kuyruk_onerisi(m):
    if m["seviye"] != "HATA" or not m.get("kok_neden"): return None
    return {"plan": m["plan"], "tur": "video", "seviye": "HATA", "kok_neden": m["kok_neden"], "cozum": "yeniden_cek", "dilim": "ses",
            "sifir_kredi": {"denendi": True, "gerekce": "Veo sözü (SC1) klibin içinde; kırpma ya da örtü sözü düzeltmez"},
            "kanit": {"madde": m["madde"], "olcu": m.get("olcu")}}


def hizala(film, nolar=None, blok=None, tur=1, gorev=None):
    """SC1: konuşmalı ve indirilmiş planlar. Raporu döndürür."""
    import kapi
    film = os.path.abspath(film); doc = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    pl = {int(p["no"]): p for p in doc.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}
    nolar = sorted(int(n) for n in (nolar or pl))
    olc, birim = [], []
    for no in nolar:
        p = pl.get(no)
        if not p or not (p.get("replik") or {}).get("metin"): continue
        if not os.path.exists(os.path.join(film, "SIRALI_VIDEO", f"{no:03d}.mp4")): continue
        birim.append(no)
        try: d = dinle(film, no)
        except (Olculemedi, subprocess.CalledProcessError, OSError) as e:
            olc.append({"madde": "SC1", "plan": no, "seviye": "OLCULEMEDI", "neden": str(e)[:160]}); continue
        o, kayit = degerlendir(p, d, doc); olc += o
        kayit.update(plan=no, replik=(p.get("replik") or {}).get("id"), kaynak=d["kaynak"], zaman=time.strftime("%Y-%m-%d %H:%M:%S"))
        ortak.atomik_yaz(os.path.join(film, "SESLER", "hizalama", f"{no:03d}.json"), kayit)
    kuyruk = [k for k in (_kuyruk_onerisi(m) for m in olc) if k]
    asama = "A14a" if str(blok or "").startswith("KESIT") else "A14"
    yol, r = kapi.kaydet(os.path.join(film, "_RAPOR"), "S2m", str(blok or "FILM"), olc, tur=tur, asama=asama, gorev=gorev,
                         arac_surum=SURUM, birimler=birim, kuyruk=kuyruk)
    _kunye_isle(film, birim, olc, os.path.relpath(yol, film).replace(os.sep, "/"))
    return r


def _kunye_isle(film, birim, olc, rapor):
    import kapi
    for no in birim:
        p = os.path.join(film, "KUNYE", f"{no:03d}.json"); k = ortak.json_oku(p, None)
        if not isinstance(k, dict): continue
        s = kapi.en_kotu([kapi.madde_sonucu(m["seviye"]) for m in olc if m.get("plan") == no] or ["GEC"])
        k.setdefault("kapilar", {})["SC1"] = {"sonuc": s, "rapor": rapor}; ortak.atomik_yaz(p, k)


def _plan_listesi(argv, bayrak):
    i = argv.index(bayrak)
    if i + 1 < len(argv) and re.fullmatch(r"[0-9][0-9,]*", argv[i + 1]): return [int(x) for x in argv[i + 1].split(",") if x]
    return None


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    if "--donustur" in argv or "--egit" in argv:
        try: import ses_donustur_ana
        except ImportError: print("Dönüşüm (ses_donustur_ana.py) henüz yok (PR-12)."); return 4
        return ses_donustur_ana.main(argv)
    film = argv[argv.index("--film") + 1] if "--film" in argv else None
    if not film or not os.path.isdir(film): print("film klasörü yok (--film)"); return 1
    blok = argv[argv.index("--blok") + 1] if "--blok" in argv else None
    if "--ayristir" in argv:
        for no in _plan_listesi(argv, "--ayristir") or []:
            try: print(no, ayristir(film, no))
            except Olculemedi as e: print(no, "ÖLÇÜLEMEDİ:", e)
        return 0
    if "--hizala" in argv:
        nolar = _plan_listesi(argv, "--hizala")
        if nolar is None and blok:
            import blok_plani
            try: nolar = [int(n) for n in blok_plani.blok_bul(film, blok)[1].get("planlar") or []]
            except ValueError as e: print(e); return 1
        r = hizala(film, nolar, blok=blok, gorev=os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None)
        print(f"SC1: {r['sonuc']} · {r['ozet']}"); return 0
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
