"""SES DENEME — Ö0-c: yerel ses dönüştürme kıyası + doğallık, MuseTalk, ACE-Step ve büyütücü süreleri (TASARIM §1.2 Ö0-c, §2.2, D-25,
D-36, D-37). Kendi içinde yeterlidir: motorlar GEÇİCİ ayrı ortamlarda (ses_kiyas KUR2 ve kurulum_kur3 KUR3 planlarından türetilir;
YOLLAR.json'a yazılmaz) motor_kosucu.py ile koşar; sonuç ortak_o0 ile <veri>/BILGI/OLCUM0/O0c.json'a yazılır.

Kullanım (kullanıcının Windows bilgisayarında, geliştirici Claude; Python mutlak yolla):
  python YZ_FILM/ARACLAR/olcum0/ses_deneme.py --plan [--json]            geçici ortam planı (hiçbir şey kurmaz) → O0c_plan.json
  … --kur <openvoice|chatterbox|mos|musetalk|acestep|buyutme|hepsi>      planı uygular (yalnız Windows; ağırlıklar ve repo için elle adımlar yazılır)
  … --ortam <ad>=<python yolu>                                           elle kurulan ortamı kaydet (ör. musetalk_kok=<klasör>, realesrgan_exe=<exe>)
  … --donustur --klipler <klasör> --referans <hedef ses.wav> [--motorlar openvoice,chatterbox]
        Arşiv Veo klipleri (B2/B3; .mp4/.wav + yan dosya <ad>.json {"metin", "teslim"}); fısıltı ve bağırma her biri ≥ 4 (motor_kiyas_ozel_min).
        Ölçüler S1.11 (benzerlik ≥ 0,70, zarf gecikmesi ≤ 20 ms, WER artışı ≤ 0,05) + doğallık: lisansı doğrulanmış MOS tahmincisi (UTMOS türü)
        ya da dinleyici kör ikili (orijinal ↔ dönüşmüş, sıra gizli; "hangisi metalik/robotik?"); ikisi de yoksa ÖLÇÜLEMEDİ BAYRAK + örnekler
        O0c_ornekler/'e (izle-dinle paketi kurgu_render oradan alır).
  … --musetalk --klip <konuşan plan.mp4> --ses <replik.wav>               MuseTalk 1.5: 1 klip, süre (tts_dudak / B planı)
  … --acestep [--ipucu-sn 30]                                            ACE-Step 1.5: 4 GB kartta bir ipucu süresi (> 600 sn → zincirden düşer)
  … --buyutme --klip <8 sn.mp4> [--exe <realesrgan-ncnn-vulkan>]          büyütücü süresi (1 saat içerik > 12 saat → 1080p + gren)
  … --karar                                                               ara sonuçlardan O0c.json (ölçülmeyen parça "ölçülmedi")
  … durum                                                                 salt okunur durum (film.py olcum0 calis c durum)
Ara sonuçlar: <veri>/BILGI/OLCUM0/O0c_ara/<parça>.json · geçici ortam kaydı O0c_ortamlar.json · ortam kökü <onbellek>/ortamlar_o0c/.
Karar kuralları (TASARIM): S1.11 ve doğallığı geçen motor varsa ana yol veo_donustur (KUR2 = sıradaki ilk motor), yoksa §2.2 B planı;
doğallık ölçülemediyse seçim olculemedi BAYRAK'ıyla (OLCUM0 denemeler) yazılır; ACE-Step ipucu süresi kabul edilemezse acestep zincirden düşer,
kutuphane ana basamak (D-25); büyütme 1 saatlik içerik için 12 saati aşarsa 1080p + gren. Anahtar yazdırılmaz; anahtarı yalnız dinleyici
sağlayıcısı kendi içinde kullanır. Kalıcı silme yok. Çıkış: 0 tamam · 1 girdi yok · 4 kullanım/ortam.
"""
import os, sys, json, time, glob, shutil, hashlib, subprocess, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
for _p in (ARACLAR, HERE):
    if _p not in sys.path: sys.path.insert(0, _p)
import ortak
import ortak_o0 as o0

SURUM = "ses_deneme 1.0"
KOSUCU = os.path.join(ARACLAR, "motor_kosucu.py")
COCUK = os.path.join(HERE, "ses_deneme_cocuk.py")
DONUSTURUCULER = ("openvoice", "chatterbox")
PARCALAR = ("donustur", "musetalk", "acestep", "buyutme")
TESLIM_OZEL = ("fisilti", "bagirma")
IKILI_ISTEM = ("You hear two short clips, A then B, of the same spoken line. Answer ONLY with JSON "
               '{"metalik": "A|B|ikisi|hicbiri", "dogal": "A|B", "guven": 0-1}. '
               "metalik = which clip sounds metallic, robotic, buzzy or processed; dogal = which sounds more like a natural human voice.")


def log(*a): print(*a, flush=True)


def esik(ad):
    import ses_ortak as so
    return so.esik(ad)


# --- yollar ----------------------------------------------------------------------------------------------------------
def ara_yol(parca): return os.path.join(o0.kok(), "O0c_ara", f"{parca}.json")
def ornek_klasoru(): return os.path.join(o0.kok(), "O0c_ornekler")
def ortamlar_yolu(): return os.path.join(o0.kok(), "O0c_ortamlar.json")


def ortam_kok():
    try: ob = ortak.yollar().get("onbellek")
    except ortak.YolYok: ob = None
    return os.path.join(ob or os.path.join(os.path.expanduser("~"), ".cache", "yz_film"), "ortamlar_o0c")


def ortamlar(): return ortak.json_oku(ortamlar_yolu(), {}) or {}


def ortam_kaydet(**k):
    d = ortamlar(); d.update({a: v for a, v in k.items() if v}); d["_zaman"] = o0.zaman(); ortak.atomik_yaz(ortamlar_yolu(), d); return d


def ortam_python(ad):
    v = ortamlar().get(ad)
    if not v: return None
    if os.path.isfile(v): return v
    p = os.path.join(v, "Scripts", "python.exe") if os.name == "nt" else os.path.join(v, "bin", "python")
    return p if os.path.isfile(p) else None


def venv_python(venv): return os.path.join(venv, "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python")


# --- plan ve kurulum ---------------------------------------------------------------------------------------------------
ELLE = {
    "openvoice": "OpenVoice V2 checkpoint'leri (checkpoints_v2/converter) kaynak sayfasından bir kez indirilir; OPENVOICE_CKPT ile verilir. "
                 "Geçişli bağımlılıkta AGPL'li whisper-timestamped çıkarsa o kod yolu kapalı kalır (D-36).",
    "chatterbox": "Model ilk çalıştırmada indirilir (HF önbelleği); çıktı filigranı (Perth) bellekten, doğrulanacak.",
    "mos": "UTMOS türü tahminci yalnız LISANSLAR.json mos_tahmincisi 'dogrulandi' ise kurulur.",
    "musetalk": "MuseTalk 1.5 deposu ve ağırlıkları README'ye göre elle indirilir; klasör `--ortam musetalk_kok=<klasör>` ile kaydedilir.",
    "acestep": "ACE-Step 1.5 ağırlıkları ilk çalıştırmada indirilir (ağırlık lisansı doğrulanacak; LISANSLAR.json ace-step).",
    "buyutme": "realesrgan-ncnn-vulkan ikilisi indirilip açılır; `--ortam realesrgan_exe=<exe>` ile kaydedilir.",
}


def plan():
    """Geçici ayrı ortam planı: KUR2 adımları ses_kiyas.kur2_plani'den, KUR3 adımları kurulum_kur3'ten; venv kökü ortamlar_o0c/
    (asıl KUR2/KUR3 ortamlarına ve YOLLAR.json'a dokunulmaz). Hiçbir şey kurmaz."""
    import ses_kiyas as sk, kurulum_kur3 as k3
    from olcum import ses as O
    kok = ortam_kok(); out = {"_surum": 1, "kademe": "Ö0-c geçici ortamlar", "kok": kok, "bilesenler": [], "zaman": o0.zaman()}
    for m in DONUSTURUCULER:
        p = sk.kur2_plani(o0c={}, motor=m)
        if not p.get("kur"): out["bilesenler"].append({"ad": m, "kur": False, "neden": p.get("neden")}); continue
        eski, yeni = p["venv"], os.path.join(kok, f"venv_{m}")
        adim = []
        for a in p["adimlar"]:
            if "yollar" in a: continue                                    # geçici ortam YOLLAR.json'a yazılmaz
            a = dict(a)
            if "komut" in a: a["komut"] = [str(x).replace(eski, yeni) for x in a["komut"]]
            adim.append(a)
        out["bilesenler"].append({"ad": m, "kur": True, "venv": yeni, "python_yolu": venv_python(yeni), "adimlar": adim,
                                  "lisans": p.get("lisans"), "deneme_kipi": True, "elle": ELLE[m], "kapali_yol": p.get("kapali_yol")})
    if O.lisans_dogrulandi("mos_tahmincisi", ticari=False):
        v = os.path.join(kok, "venv_mos")
        out["bilesenler"].append({"ad": "mos", "kur": True, "venv": v, "python_yolu": venv_python(v), "elle": ELLE["mos"],
                                  "adimlar": [{"ne": "ayrı sanal ortam", "komut": ([sys.executable] if os.name != "nt" else ["py", "-3.10"]) + ["-m", "venv", v]},
                                              {"ne": "MOS tahmincisi", "komut": [venv_python(v), "-m", "pip", "install", "utmos"], "dogrulanacak": True}]})
    else:
        out["bilesenler"].append({"ad": "mos", "kur": False, "neden": "MOS tahmincisinin lisansı doğrulanmadı (LISANSLAR.json mos_tahmincisi): "
                                                                     "doğallık dinleyici kör ikiliyle ya da ölçülemedi"})
    p3 = k3.kur3_plani()
    for o in p3["ortamlar"]:
        o = dict(o, hedef=os.path.join(kok, f"venv_{o['ad']}"), hazir=False)
        out["bilesenler"].append({"ad": o["ad"], "kur": True, "venv": o["hedef"], "python_yolu": None if o.get("ikili") else venv_python(o["hedef"]),
                                  "adimlar": [dict(k, ne=k.get("not") or "kurulum") for k in k3.kur3_kur({"ortamlar": [o]})],
                                  "lisans": {"kod": o.get("kod_lisansi"), "agirlik": o.get("agirlik_lisansi")}, "deneme_kipi": True,
                                  "elle": ELLE.get(o["ad"]), "gpu": o.get("gpu")})
    ortak.atomik_yaz(os.path.join(o0.kok(), "O0c_plan.json"), out)
    return out


def kur(bilesen, calistir=subprocess.run, zorla=False):
    """Planı uygular. Yalnız Windows'ta (D-12; testler zorla=True + sahte calistir). Başarılı ortamın Python'u O0c_ortamlar.json'a."""
    if os.name != "nt" and not zorla:
        log("!! Ö0-c ortamları yalnız kullanıcının Windows bilgisayarında kurulur (D-12)."); return 4, {}
    p = plan(); sonuc = {}
    for b in p["bilesenler"]:
        if bilesen not in ("hepsi", b["ad"]): continue
        if not b.get("kur"): sonuc[b["ad"]] = {"kuruldu": False, "neden": b.get("neden")}; continue
        hata = None
        for a in b.get("adimlar") or []:
            if "komut" not in a: continue
            try:
                r = calistir(a["komut"], capture_output=True, text=True, timeout=7200)
                if r.returncode != 0: hata = f"{a.get('ne')}: {(r.stderr or '')[-200:]}"; break
            except Exception as e:
                hata = f"{a.get('ne')}: {type(e).__name__}"; break
        sonuc[b["ad"]] = {"kuruldu": hata is None, "hata": hata, "elle": b.get("elle")}
        if hata is None and b.get("python_yolu"): ortam_kaydet(**{b["ad"]: b["python_yolu"]})
        log(f"{b['ad']}: {'kuruldu' if hata is None else 'kurulamadı — ' + hata}" + (f" · elle: {b['elle']}" if b.get("elle") else ""))
    return 0, sonuc


# --- motor çağrısı ------------------------------------------------------------------------------------------------------
def motor_kos(py, motor, istek, env=None, calistir=subprocess.run, zaman_asimi=7200, betik=KOSUCU):
    """<py> motor_kosucu.py <motor> <istek.json> → (yanıt, süre_sn, çıkış kodu). İstek/yanıt O0c_ara/_is/ altında kalır."""
    d = os.path.join(o0.kok(), "O0c_ara", "_is", f"{motor}_{int(time.time() * 1000)}")
    os.makedirs(d, exist_ok=True)
    g, c = os.path.join(d, "istek.json"), os.path.join(d, "yanit.json")
    ortak.atomik_yaz(g, dict(istek, yanit=c))
    bas = time.time()
    try:
        r = calistir([py, betik, motor, g], capture_output=True, text=True, timeout=zaman_asimi,
                     env=dict(os.environ, PYTHONIOENCODING="utf-8", **(env or {})))
        kod = r.returncode
    except subprocess.TimeoutExpired:
        return {"hata": "zaman aşımı"}, round(time.time() - bas, 1), 124
    except Exception as e:
        return {"hata": f"{type(e).__name__}"}, round(time.time() - bas, 1), 1
    y = ortak.json_oku(c, {}) or {}
    if kod and not y.get("hata"): y["hata"] = (getattr(r, "stderr", "") or "")[-200:] or f"çıkış {kod}"
    return y, round(time.time() - bas, 1), kod


def ffprobe_sure(p, calistir=subprocess.run):
    try:
        r = calistir(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", p],
                     capture_output=True, text=True, timeout=60)
        return round(float((r.stdout or "").strip().splitlines()[0]), 3)
    except Exception:
        return None


def wav_cikar(klip, hedef, calistir=subprocess.run):
    if klip.lower().endswith(".wav"): return klip
    os.makedirs(os.path.dirname(hedef), exist_ok=True)
    r = calistir(["ffmpeg", "-v", "error", "-y", "-i", klip, "-vn", "-ac", "1", "-ar", "48000", hedef], capture_output=True, timeout=600)
    return hedef if (getattr(r, "returncode", 1) == 0 and os.path.isfile(hedef)) else None


# --- doğallık: dinleyici kör ikili ----------------------------------------------------------------------------------------
def dinleyici_ikili():
    """(işlev, neden). Açılma kuralı dinleyici ile aynı (gemini_api.izin_karari: anahtar varlığı, maliyet 0, Ö0-e ses girişi).
    Anahtarı yalnız sağlayıcı sınıfı okur; burada yazdırılmaz, kaydedilmez."""
    try:
        from saglayicilar.izleyici import acik_mi, GeminiIstemci, ANAHTAR_DOSYASI, ANAHTAR_ORTAM, film_ayar
        from saglayicilar.dinleyici import Dinleyici
    except Exception as e:
        return None, f"dinleyici yüklenemedi ({type(e).__name__})"
    ok, neden, _ = acik_mi(None, "ses")
    if not ok: return None, neden or "dinleyici kapalı"
    d = Dinleyici(); k = d.anahtar(ANAHTAR_DOSYASI, ANAHTAR_ORTAM)
    if not k: return None, "Gemini anahtarı yok"
    ist = GeminiIstemci(k, (film_ayar().get("modeller") or {}).get("dinleyici")); del k

    def ikili(a, b):
        fa, fb = ist.yukle(a, "audio/wav"), ist.yukle(b, "audio/wav")
        return ist.uret([{"text": "Clip A:"}, {"file_data": {"mime_type": fa["mime"], "file_uri": fa["uri"]}},
                         {"text": "Clip B:"}, {"file_data": {"mime_type": fb["mime"], "file_uri": fb["uri"]}}, {"text": IKILI_ISTEM}])
    return ikili, None


def kor_sira(anahtar):
    """Gizli ama tekrarlanabilir sıra: True → dönüşmüş A, orijinal B."""
    return int(hashlib.sha1(anahtar.encode("utf-8")).hexdigest(), 16) % 2 == 0


def ikili_degerlendir(ikili, ciftler):
    """ciftler: [(orijinal, donusmus, ad)] → {n, metalik_oran, dogal_kazanma, hatalar}. Seçim harfi gizli sıradan geri çevrilir."""
    n = met = dog = 0; hata = []
    for org, don, ad in ciftler:
        once = kor_sira(ad)
        a, b = (don, org) if once else (org, don)
        try: j = ikili(a, b) or {}
        except Exception as e: hata.append(f"{ad}: {type(e).__name__}"); continue
        m = str(j.get("metalik") or "").strip().lower(); dg = str(j.get("dogal") or "").strip().upper()
        don_harf = "a" if once else "b"
        n += 1
        if m in ("ikisi", "both") or m == don_harf: met += 1
        if dg == don_harf.upper(): dog += 1
    return {"n": n, "metalik_oran": round(met / n, 3) if n else None, "dogal_kazanma": round(dog / n, 3) if n else None, "hatalar": hata[:10]}


# --- 1. dönüştürme kıyası --------------------------------------------------------------------------------------------------
def klipler_(klasor):
    import ses_ortak as so
    out = []
    for p in sorted(glob.glob(os.path.join(klasor, "*.wav")) + glob.glob(os.path.join(klasor, "*.mp4"))):
        j = ortak.json_oku(os.path.splitext(p)[0] + ".json", None) or {}
        out.append({"klip": p, "ad": os.path.splitext(os.path.basename(p))[0], "metin": j.get("metin") or "", "teslim": so.teslim_sinifi(j.get("teslim"))})
    return out


def _asr_varsayilan():
    if not importlib.util.find_spec("faster_whisper"): return None
    def asr(wav):
        y, _, kod = motor_kos(sys.executable, "faster_whisper", {"giris": wav})
        return None if kod else y.get("metin")
    return asr


def _med(v): v = sorted(v); return v[len(v) // 2] if v else None


def donustur(klasor, referans, motorlar=None, kos=motor_kos, asr="varsayilan", ikili="varsayilan", calistir=subprocess.run):
    from olcum import ses as O
    kl = klipler_(klasor)
    if not kl: log(f"!! kıyas klibi yok: {klasor}"); return 1, None
    if not os.path.isfile(referans): log(f"!! hedef ses yok: {referans}"); return 1, None
    asr = _asr_varsayilan() if asr == "varsayilan" else asr
    din_neden = None
    if ikili == "varsayilan": ikili, din_neden = dinleyici_ikili()
    ref, _ = O.oku(referans); ref_g = O.gomme(ref)
    enaz = int(esik("motor_kiyas_ozel_min")); bz_min = esik("ses_donusum_benzerlik_min")
    gc_max = esik("ses_donusum_zarf_gecikme_max_ms"); wa_max = esik("ses_donusum_wer_artis_max")
    mos_min = esik("ses_dogallik_mos_min"); met_max = esik("ses_dogallik_ikili_metalik_max")
    ara = os.path.join(o0.kok(), "O0c_ara")
    wavlar = {}
    for k in kl:
        w = wav_cikar(k["klip"], os.path.join(ara, "klipler", k["ad"] + ".wav"), calistir)
        if w: wavlar[k["ad"]] = w
    set_ = {"klip": len(kl), **{t: sum(1 for k in kl if k["teslim"] == t) for t in TESLIM_OZEL}, "enaz": enaz}
    set_["yeterli"] = all(set_[t] >= enaz for t in TESLIM_OZEL)
    tablo = {}; os.makedirs(ornek_klasoru(), exist_ok=True)
    for m in motorlar or DONUSTURUCULER:
        py = ortam_python(m)
        if not py: tablo[m] = {"durum": "kurulu değil", "neden": f"geçici ortam yok (--kur {m})"}; continue
        sat = []
        for k in kl:
            w = wavlar.get(k["ad"])
            if not w: sat.append({"klip": k["ad"], "hata": "ses çıkarılamadı"}); continue
            out = os.path.join(ara, "cikti", m, k["ad"] + ".wav"); os.makedirs(os.path.dirname(out), exist_ok=True)
            y_, sure, kod = kos(py, m, {"giris": w, "referans": referans, "cikti": out})
            if kod or y_.get("hata") or not os.path.isfile(out):
                sat.append({"klip": k["ad"], "teslim": k["teslim"], "hata": str(y_.get("hata") or f"çıkış {kod}")[:120]}); continue
            x, _ = O.oku(w); y, _ = O.oku(out)
            w0 = w1 = None
            if asr and k["metin"]:
                h0, h1 = asr(w), asr(out)
                if h0 is not None and h1 is not None: w0, w1 = O.wer(k["metin"], h0), O.wer(k["metin"], h1)
            mos = O.mos_tahmin(out)
            sat.append({"klip": k["ad"], "teslim": k["teslim"], "benzerlik": round(O.benzerlik(O.gomme(y), ref_g) or 0, 3),
                        "gecikme_ms": O.zarf_gecikme_ms(x, y), "wer_artis": None if w0 is None else round(w1 - w0, 3),
                        "mos": mos.get("mos"), "sure_sn": sure, "cikti": out})
            if k["teslim"] in TESLIM_OZEL:
                shutil.copy2(out, os.path.join(ornek_klasoru(), f"{m}_{k['ad']}.wav"))
        iyi = [r for r in sat if "hata" not in r]
        if not iyi: tablo[m] = {"durum": "çıktı yok", "hatalar": [r.get("hata") for r in sat][:5]}; continue
        bz = _med([r["benzerlik"] for r in iyi]); gl = [abs(r["gecikme_ms"]) for r in iyi if r["gecikme_ms"] is not None]
        gc = max(gl) if gl else None; wl = [r["wer_artis"] for r in iyi if r["wer_artis"] is not None]; wa = sum(wl) / len(wl) if wl else None
        s111 = bz is not None and bz >= bz_min and gc is not None and gc <= gc_max and (wa is None or wa <= wa_max)
        ozel = {t: sum(1 for r in iyi if r["teslim"] == t) for t in TESLIM_OZEL}
        mos = [r["mos"] for r in iyi if r["mos"] is not None]
        if mos and len(mos) == len(iyi):
            mo = round(sum(mos) / len(mos), 2); dog = {"yontem": "mos", "mos_ort": mo, "gecer": mo >= mos_min, "esik": mos_min}
        elif ikili:
            cif = [(wavlar[r["klip"]], r["cikti"], f"{m}:{r['klip']}") for r in iyi if r["teslim"] in TESLIM_OZEL]
            d = ikili_degerlendir(ikili, cif)
            if d["n"] and min(ozel.values()) >= enaz:
                dog = dict(d, yontem="dinleyici_kor_ikili", gecer=d["metalik_oran"] <= met_max, esik=met_max)
            else:
                dog = dict(d, yontem="dinleyici_kor_ikili", olculemedi=True,
                           neden=f"fısıltı/bağırma çifti yetersiz (her biri ≥ {enaz})" if d["n"] else "dinleyici cevap vermedi")
        else:
            dog = {"olculemedi": True, "neden": din_neden or "MOS lisansı doğrulanmadı ve dinleyici yok"}
        tablo[m] = {"durum": "olculdu", "benzerlik_medyan": bz, "gecikme_max_ms": gc, "wer_artis_ort": None if wa is None else round(wa, 3),
                    "wer_olculdu": bool(wl), "s1_11": s111, "ozel_sayi": ozel, "dogallik": dog,
                    "sure_ort_sn": round(sum(r["sure_sn"] for r in iyi) / len(iyi), 1), "satirlar": sat}
    v = {"_surum": 1, "zaman": o0.zaman(), "kiyas_seti": set_, "referans": os.path.basename(referans), "tablo": tablo,
         "tts_sigdirma": "çıta: TTS + süreye sığdırma dudakla gitmez (B2); ana yol olamaz", "dinleyici_neden": din_neden}
    ortak.atomik_yaz(ara_yol("donustur"), v)
    for m, t in tablo.items():
        log(f"{m}: {t.get('durum')}" + (f" · S1.11 {'GEÇ' if t.get('s1_11') else 'KAL'} · doğallık "
                                        f"{'ölçülemedi' if t['dogallik'].get('olculemedi') else ('GEÇ' if t['dogallik'].get('gecer') else 'KAL')}"
                                        if t.get("durum") == "olculdu" else ""))
    return 0, v


def donustur_karari(v):
    """TASARIM §1.2 Ö0-c / §2.2 karar 4–5: S1.11 ve doğallığı geçen motor → sıra; doğallık ölçülemeyen motor S1.11 ile seçilir ama BAYRAK."""
    if not v: return {"ses_donustur_sira": [], "ana_yol": "B", "dogallik": {"olculemedi": True, "neden": "dönüştürme kıyası yapılmadı"},
                      "bayraklar": ["donusturme_olculmedi"], "gerekce": "Ö0-c dönüştürme kıyası yok → §2.2 B planı"}
    t = v.get("tablo") or {}; bay = []
    aday = [m for m, x in t.items() if x.get("durum") == "olculdu" and x.get("s1_11")]
    gecen = [m for m in aday if x_gec(t[m])]
    sec = sorted(gecen, key=lambda m: -(t[m]["benzerlik_medyan"] - 2 * (t[m]["wer_artis_ort"] or 0) - (t[m]["gecikme_max_ms"] or 0) / 100
                                        + ((t[m]["dogallik"].get("mos_ort") or 0) / 10) - (t[m]["dogallik"].get("metalik_oran") or 0)))
    olc_yok = [m for m in sec if t[m]["dogallik"].get("olculemedi")]
    if olc_yok: bay.append("dogallik_olculemedi")
    if not (v.get("kiyas_seti") or {}).get("yeterli"): bay.append("kiyas_seti_eksik")
    if any(not x.get("wer_olculdu") for m, x in t.items() if x.get("durum") == "olculdu"): bay.append("wer_olculmedi")
    dg = {m: t[m]["dogallik"] for m in t if t[m].get("durum") == "olculdu"}
    dogallik = dg if any(not x.get("olculemedi") for x in dg.values()) else {"olculemedi": True, "neden": next(
        (x.get("neden") for x in dg.values() if x.get("neden")), v.get("dinleyici_neden") or "ölçülemedi"), "motorlar": dg}
    return {"ses_donustur_sira": sec, "ana_yol": "veo_donustur" if sec else "B", "dogallik": dogallik, "bayraklar": bay,
            "gerekce": (f"S1.11 ve doğallığı geçen motor: {', '.join(sec)}" if sec else "eşiği geçen motor yok → §2.2 B planı (tts_dudak)")
            + (" (doğallık ölçülemedi: olculemedi BAYRAK; fısıltı/bağırma örnekleri O0c_ornekler/'de)" if olc_yok else "")}


def x_gec(x):
    d = x.get("dogallik") or {}
    return bool(d.get("olculemedi") or d.get("gecer"))


# --- 2. MuseTalk -------------------------------------------------------------------------------------------------------
def musetalk(klip, ses, kos=motor_kos, calistir=subprocess.run):
    py = ortam_python("musetalk"); kok = ortamlar().get("musetalk_kok") or os.environ.get("MUSETALK_KOK")
    v = {"_surum": 1, "zaman": o0.zaman(), "kuruldu": bool(py and kok), "klip_sn": ffprobe_sure(klip, calistir)}
    if not v["kuruldu"]:
        v.update(calisti=False, neden="MuseTalk geçici ortamı ya da musetalk_kok yok (--kur musetalk, --ortam musetalk_kok=…)")
    else:
        out = os.path.join(o0.kok(), "O0c_ara", "musetalk", os.path.splitext(os.path.basename(klip))[0] + "_dudak.mp4")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        y, sure, kod = kos(py, "musetalk", {"klip": klip, "ses": ses, "cikti": out}, env={"MUSETALK_KOK": kok})
        v.update(calisti=(kod == 0 and not y.get("hata")), sure_sn=y.get("sure_sn") or sure, hata=y.get("hata"), gpu_yetmedi=kod == 3, cikti=out)
        if v["calisti"] and v["klip_sn"]:
            v["oran"] = round(v["sure_sn"] / v["klip_sn"], 2); v["tahmin_190_plan_saat"] = round(190 * v["sure_sn"] / 3600, 1)
    ortak.atomik_yaz(ara_yol("musetalk"), v)
    log(f"MuseTalk: {'çalıştı' if v.get('calisti') else 'çalışmadı'}" + (f" · {v.get('sure_sn')} sn" if v.get("calisti") else f" · {v.get('neden') or v.get('hata')}"))
    return 0, v


# --- 3. ACE-Step ---------------------------------------------------------------------------------------------------------
def gpu_bilgisi(calistir=subprocess.run):
    try:
        r = calistir(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=30)
        ad, mb = [x.strip() for x in (r.stdout or "").strip().splitlines()[0].split(",")[:2]]
        return {"ad": ad, "bellek_gb": round(float(mb) / 1024, 1)}
    except Exception:
        return {"ad": None, "bellek_gb": None}


def acestep(ipucu_sn=30, kos=motor_kos, calistir=subprocess.run):
    py = ortam_python("acestep"); gpu = gpu_bilgisi(calistir)
    v = {"_surum": 1, "zaman": o0.zaman(), "ipucu_sn": ipucu_sn, "gpu": gpu, "kuruldu": bool(py), "esik_sn": esik("o0c_acestep_ipucu_max_sn")}
    if gpu.get("bellek_gb") and gpu["bellek_gb"] > 6: v["not"] = "kart 4 GB değil: süre 4 GB katmanına genellenmez"
    if not py:
        v.update(calisti=False, kabul=None, zincirden_dus=None, neden="ACE-Step geçici ortamı yok (--kur acestep)")
    else:
        out = os.path.join(o0.kok(), "O0c_ara", "acestep", "ipucu_deneme.wav"); os.makedirs(os.path.dirname(out), exist_ok=True)
        y, sure, kod = kos(py, "acestep", {"istem_en": "slow orchestral fantasy cue, strings and low brass, no vocals", "sure_sn": ipucu_sn,
                                           "cikti": out}, betik=COCUK)
        v.update(calisti=(kod == 0 and not y.get("hata") and os.path.isfile(out)), sure_sn=y.get("sure_sn") or sure, hata=y.get("hata"),
                 gpu_yetmedi=kod == 3)
        v["kabul"] = bool(v["calisti"] and v["sure_sn"] <= v["esik_sn"])
        v["zincirden_dus"] = not v["kabul"]
    ortak.atomik_yaz(ara_yol("acestep"), v)
    log(f"ACE-Step: " + ("ölçülmedi — " + v["neden"] if v.get("neden") else f"{v.get('sure_sn')} sn / ipucu · {'kabul' if v['kabul'] else 'zincirden düşer'}"))
    return 0, v


# --- 4. büyütücü ---------------------------------------------------------------------------------------------------------
def buyutme(klip, exe=None, calistir=subprocess.run, olcek=2):
    exe = exe or ortamlar().get("realesrgan_exe") or os.environ.get("REALESRGAN_EXE")
    v = {"_surum": 1, "zaman": o0.zaman(), "klip_sn": ffprobe_sure(klip, calistir), "olcek": olcek, "esik_saat_orani": esik("o0c_buyutme_saat_orani_max")}
    if not (exe and os.path.isfile(exe)):
        v.update(calisti=False, yol=None, neden="realesrgan-ncnn-vulkan yok (--ortam realesrgan_exe=…)")
    else:
        d = os.path.join(o0.kok(), "O0c_ara", "buyutme", time.strftime("%Y%m%d_%H%M%S")); g, c = os.path.join(d, "kare"), os.path.join(d, "buyuk")
        os.makedirs(g, exist_ok=True); os.makedirs(c, exist_ok=True); out = os.path.join(d, "buyuk.mp4")
        adimlar = [["ffmpeg", "-v", "error", "-y", "-i", klip, os.path.join(g, "%06d.png")],
                   [exe, "-i", g, "-o", c, "-s", str(olcek), "-f", "png"],
                   ["ffmpeg", "-v", "error", "-y", "-framerate", "24", "-i", os.path.join(c, "%06d.png"), "-i", klip, "-map", "0:v", "-map", "1:a?",
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-shortest", out]]
        bas = time.time(); hata = None
        for a in adimlar:
            try:
                r = calistir(a, capture_output=True, text=True, timeout=6 * 3600)
                if r.returncode != 0: hata = (r.stderr or "")[-200:] or f"çıkış {r.returncode}"; break
            except Exception as e:
                hata = type(e).__name__; break
        sure = round(time.time() - bas, 1)
        v.update(calisti=hata is None, hata=hata, sure_sn=sure, cikti=out)
        if v["calisti"] and v["klip_sn"]:
            v["sn_basina_sn"] = round(sure / v["klip_sn"], 2); v["saat_basina_saat"] = v["sn_basina_sn"]
            v["yol"] = "1080p_gren" if v["sn_basina_sn"] > v["esik_saat_orani"] else "yz_buyutucu"
        else:
            v["yol"] = None
    ortak.atomik_yaz(ara_yol("buyutme"), v)
    log(f"Büyütme: " + (f"{v.get('sure_sn')} sn / {v.get('klip_sn')} sn klip → yol {v.get('yol')}" if v.get("calisti") else f"ölçülmedi — {v.get('neden') or v.get('hata')}"))
    return 0, v


# --- karar: O0c.json -------------------------------------------------------------------------------------------------------
def karar(yaz=True):
    ara = {p: ortak.json_oku(ara_yol(p), None) for p in PARCALAR}
    dk = donustur_karari(ara["donustur"])
    mt = ara["musetalk"] or {"calisti": False, "neden": "ölçülmedi"}
    ac = ara["acestep"] or {"calisti": False, "kabul": None, "zincirden_dus": None, "neden": "ölçülmedi"}
    bu = ara["buyutme"] or {"calisti": False, "yol": None, "neden": "ölçülmedi"}
    bay = list(dk["bayraklar"])
    if dk["ana_yol"] == "B" and not mt.get("calisti"): bay.append("b_plani_musetalk_calismiyor")
    kararlar = [
        {"konu": "ses_ana_yol", "karar": dk["ana_yol"], "gerekce": dk["gerekce"]},
        {"konu": "tts_dudak", "karar": "acik" if mt.get("calisti") else "kapali",
         "gerekce": (f"MuseTalk 1 klip {mt.get('sure_sn')} sn" if mt.get("calisti") else f"MuseTalk çalışmadı ({mt.get('neden') or mt.get('hata')})")},
        {"konu": "acestep_zincirde", "karar": None if ac.get("zincirden_dus") is None else (not ac["zincirden_dus"]),
         "gerekce": (f"ipucu {ac.get('sure_sn')} sn (eşik {ac.get('esik_sn')} sn)" if ac.get("calisti") else
                     f"ACE-Step ölçülemedi/çalışmadı ({ac.get('neden') or ac.get('hata')})") + (": zincirden düşer, kutuphane ana basamak (D-25)"
                                                                                               if ac.get("zincirden_dus") else "")},
        {"konu": "buyutme_yolu", "karar": bu.get("yol") or "1080p_gren",
         "gerekce": (f"{bu.get('sn_basina_sn')} sn işlem / sn içerik (eşik {bu.get('esik_saat_orani')})" if bu.get("calisti")
                     else "büyütücü ölçülmedi: varsayılan 1080p + gren (buyut.py yz_buyutucu'yu süre bilinmeden kullanmaz)")}]
    if "dogallik_olculemedi" in bay:
        kararlar.append({"konu": "dogallik", "karar": "olculemedi", "gerekce": "seçim olculemedi BAYRAK'ıyla; örnekler O0c_ornekler/ (izle-dinle paketi)"})
    tamam = all(ara[p] is not None for p in PARCALAR)
    v = {"durum": "bitti" if tamam else "suruyor", "ses_donustur_sira": dk["ses_donustur_sira"], "ana_yol": dk["ana_yol"],
         "dogallik": dk["dogallik"], "kiyas_seti": (ara["donustur"] or {}).get("kiyas_seti"),
         "motorlar": {m: {k: x.get(k) for k in ("durum", "benzerlik_medyan", "gecikme_max_ms", "wer_artis_ort", "s1_11", "ozel_sayi", "dogallik", "sure_ort_sn", "neden")}
                      for m, x in ((ara["donustur"] or {}).get("tablo") or {}).items()},
         "tts_dudak": "acik" if mt.get("calisti") else "kapali", "musetalk": mt, "acestep": ac,
         "acestep_zincirde": None if ac.get("zincirden_dus") is None else (not ac["zincirden_dus"]),
         "buyutme": bu, "bayraklar": sorted(set(bay)), "kararlar": kararlar,
         "olculmeyen": [p for p in PARCALAR if ara[p] is None], "ornekler": ornek_klasoru()}
    if not yaz: return v
    ozet = {k: v[k] for k in ("durum", "ses_donustur_sira", "ana_yol", "tts_dudak", "acestep_zincirde", "bayraklar")}
    ozet["dogallik_olculemedi"] = bool(v["dogallik"].get("olculemedi")) if isinstance(v["dogallik"], dict) and "olculemedi" in v["dogallik"] else False
    ozet["buyutme_yolu"] = kararlar[3]["karar"]
    o0.yaz("c", v, ozet=ozet, arac=SURUM)
    for k in kararlar: o0.deneme("c", k["konu"], None, k["karar"], k["gerekce"])
    log(f"O0c.json: ana yol {v['ana_yol']} · sıra {v['ses_donustur_sira']} · tts_dudak {v['tts_dudak']} · acestep_zincirde {v['acestep_zincirde']} · "
        f"büyütme {kararlar[3]['karar']} · bayrak {v['bayraklar']} · ölçülmeyen {v['olculmeyen']}")
    return v


# --- komut satırı ------------------------------------------------------------------------------------------------------
def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def durum_metni():
    """Salt okunur: hangi parça ölçüldü, sıradaki komut (film.py olcum0 calis c durum)."""
    ara = {p: os.path.isfile(ara_yol(p)) for p in PARCALAR}
    kalan = [p for p in PARCALAR if not ara[p]]
    return {"olcum": "Ö0-c", "durum": o0.durum("c"), "parcalar": ara, "ortamlar": sorted(k for k in ortamlar() if not k.startswith("_")),
            "sonraki": ("--" + kalan[0]) if kalan else ("--karar" if o0.durum("c") != "bitti" else None)}


def main(a):
    if not a or "-h" in a or "--help" in a: print(__doc__); return 4
    try: o0.kok()
    except ortak.YolYok as e: log(f"!! {e}"); return 4
    if a[0] == "durum": print(json.dumps(durum_metni(), ensure_ascii=False, indent=1)); return 0
    if "--plan" in a:
        p = plan()
        if "--json" in a: print(json.dumps(p, ensure_ascii=False, indent=1))
        else:
            for b in p["bilesenler"]: log(f"{b['ad']}: {'kurulur' if b.get('kur') else 'kurulmaz'} · {b.get('venv') or b.get('neden')}")
        return 0
    if "--kur" in a: return kur(_arg(a, "--kur", "hepsi"))[0]
    if "--ortam" in a:
        k, _, v = (_arg(a, "--ortam") or "").partition("=")
        if not (k and v): log("!! --ortam ad=yol"); return 4
        ortam_kaydet(**{k.strip(): v.strip()}); log(f"kaydedildi: {k}"); return 0
    if "--donustur" in a:
        if not (_arg(a, "--klipler") and _arg(a, "--referans")): log("!! --klipler ve --referans gerekli"); return 4
        mot = _arg(a, "--motorlar"); return donustur(_arg(a, "--klipler"), _arg(a, "--referans"), mot.split(",") if mot else None)[0]
    if "--musetalk" in a:
        if not (_arg(a, "--klip") and _arg(a, "--ses")): log("!! --klip ve --ses gerekli"); return 4
        return musetalk(_arg(a, "--klip"), _arg(a, "--ses"))[0]
    if "--acestep" in a: return acestep(float(_arg(a, "--ipucu-sn", 30)))[0]
    if "--buyutme" in a:
        if not _arg(a, "--klip"): log("!! --klip gerekli"); return 4
        return buyutme(_arg(a, "--klip"), _arg(a, "--exe"))[0]
    if "--karar" in a: karar(); return 0
    print(__doc__); return 4


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
