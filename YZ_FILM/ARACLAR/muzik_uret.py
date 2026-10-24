"""MÜZİK ÜRET — `muzik.py --uret` zinciri (TASARIM D-25, §4.8.4, §5.6, §7.2 S6; [SM2] §4.2 SB5 adım 2, §4.7.7).
muzik.py'nin sahibi kâğıt dilimidir; bu modül `--uret` işini yapar (muzik.py: `--uret` → `import muzik_uret; return muzik_uret.main(argv)`).

Kullanım:
  python muzik_uret.py --uret --film F [--kip animatik|yayin] [--ipucu M06] [--saglayici sahte]
     (kip verilmezse görevin aşamasından: A12 → animatik, sonrası → yayin)
Zincir (FILM_AYAR.json saglayicilar.muzik.<kip>; varsayılan animatik [acestep, midi_ornek], yayın [acestep, kutuphane]):
  - `elle = True` sağlayıcı yalnız SON basamak olabilir; başka yerdeyse S6.8 HATA ve zincirden çıkarılır.
  - `midi_ornek` yalnız animatikte (yayın zincirinden çıkarılır + BAYRAK); `gemini_muzik_paketi` yalnız lisans doğrulanınca hazırdır.
  - Test kipinde zincir [sahte, midi_ornek] (animatik) / [sahte] (yayın).
İpucu başına `muzik_aday_sayisi` (3) aday; her aday ölçülür: S6.1 vokal (ASR anlaşılır kelime, güven ≥ 0,5 → HATA, aday elenir),
  S6.9 kırpılma ve ani kesik (HATA), S6.7 motif kroma benzerliği (tema ipucunda ≥ 0,6; altı BAYRAK → sıradaki sağlayıcı, animatikte
  midi_ornek her zaman motiflidir), S6.10 BPM ±%3 ve ton (BAYRAK), yerel kalite (spektral genişlik, dinamik aralık, stereo genişlik) ve
  `dinleyici` ikili karşılaştırması (yoksa ÖLÇÜLEMEDİ = BAYRAK, açık eksik). En iyi aday MUZIK/secilen/'e kopyalanır, kaynak kaydı
  MUZIK/KAYNAK_KAYDI.json'a (model, sürüm, lisans, istem, tohum, referans motif, tarih, SHA-1; S6.8), muzik_listesi'ne `secilen`/`olcum`.
  Zincir boşsa ya da bütün adaylar kalırsa ipucu MÜZİKSİZ kalır: S6 BAYRAK (HATA değil), hat durmaz (D-25).
Rapor: _RAPOR/S6_URET.json (animatik) · _RAPOR/S6_URET_YAYIN.json (yayın); birim = ipucu.
Çıkış kodları: 0 rapor yazıldı · 1 muzik_listesi yok/bozuk · 2 KULLANICI (Gemini müzik paketi kullanıcıyı bekliyor) · 4 kullanım.
"""
import os, sys, re, json, shutil
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak
import ses_ortak as so
from olcum import ses as O

SURUM = "muzik_uret 1.0"
SR = so.SR


def log(*a): print(*a, flush=True)


def leitmotifler(film):
    kok, s = so.evren_kok(film), so.seri(film)
    for p in ([os.path.join(kok, s, "muzik", "leitmotifler.json")] if (kok and s) else []) + [os.path.join(film, "MUZIK", "leitmotifler.json")]:
        j = ortak.json_oku(p, None)
        if isinstance(j, dict) and j: return j
    return {}


def zincir_kur(film, kip, saglayici=None):
    """(hazır sağlayıcılar, ölçümler, hazır olmayanlar). Zincir kuralları S6.8 / D-25 burada uygulanır."""
    if so.sahte_mi(film, saglayici): adlar = ["sahte", "midi_ornek"] if kip == "animatik" else ["sahte"]
    else: adlar = so.zincir_adlari("muzik", film, kip, saglayici)
    olc, out, yok = [], [], []
    for i, ad in enumerate(adlar):
        s = so.saglayici(ad)
        if s is None or "muzik" not in getattr(s, "turler", ()): yok.append({"saglayici": ad, "neden": "kurulu değil"}); continue
        if getattr(s, "elle", False) and i != len(adlar) - 1:
            olc.append(so.m("S6.8", "HATA", olcu=f"{ad} elle = True ama zincirin {i + 1}. basamağı", esik="elle sağlayıcı yalnız son basamak",
                            oneri="FILM_AYAR saglayicilar.muzik sırası", kok_neden="lisans_belirsiz")); continue
        if getattr(s, "yalniz_animatik", False) and kip != "animatik":
            olc.append(so.m("S6.zincir", "BAYRAK", olcu=f"{ad} yalnız animatikte; yayın zincirinden çıkarıldı", esik="D-25")); continue
        try: ok, neden = s.hazir()
        except Exception as e: ok, neden = False, str(e)[:100]
        (out.append(s) if ok else yok.append({"saglayici": ad, "neden": neden}))
    return out, olc, yok


def _bpm_istem(ip, motif):
    if ip.get("bpm"): return float(ip["bpm"])
    m = re.search(r"(\d{2,3})\s*BPM", ip.get("istem_en") or "", re.I)
    return float(m.group(1)) if m else ((motif or {}).get("bpm"))


def _ton_istem(ip, motif):
    if ip.get("ton"): return O.ton_coz(ip["ton"])
    m = re.search(r"\b([A-G][#b]?)\s+(major|minor|dorian|aeolian|phrygian|lydian|mixolydian|ionian|locrian)\b", ip.get("istem_en") or "")
    return O.ton_coz(f"{m.group(1)} {m.group(2)}") if m else (O.ton_coz(motif.get("ton")) if motif and motif.get("ton") else None)


def ani_kesik(x):
    """Parça içinde 10 ms'de > 40 dB düşüş (son 50 ms hariç; uç yumuşatması kesik sayılmaz)."""
    c = O.mono(x); n = SR // 100; k = len(c) // n
    if k < 10: return 0
    r = np.sqrt(np.mean(c[:k * n].reshape(k, n) ** 2, axis=1)) + 1e-9
    d = 20 * np.log10(r[1:-5] / r[:-6])
    return int(np.sum(d < -40))


def aday_olc(film, p, ip, motif, sablon, asr, kip):
    x, _ = O.oku(p); x = O.stereo(x); o = {"dosya": p}
    if asr is not None:
        try:
            a = asr.asr(film, p)
            kel = [k for k in a.get("kelimeler") or [] if (k.get("guven") or 0) >= so.esik("muzik_kelime_guven_min")]
            o["vokal"] = [k["w"] for k in kel]
        except Exception as e: o["vokal"] = None; o["asr_neden"] = str(e)[:80]
    else: o["vokal"] = None
    o["kirpilma"] = O.kirpilma(x); o["ani_kesik"] = ani_kesik(x)
    o["kroma"] = O.kroma_benzerlik(sablon, O.kroma(x)) if sablon is not None else None
    o["bpm"] = O.bpm(x); o["ton"] = O.ton(x)
    o["yerel"] = {"spektral_genislik_hz": O.spektral_genislik(x), "dinamik_aralik_lu": O.dinamik_aralik(x), "stereo_genislik": O.stereo_genislik(x)}
    o["lufs"] = round(O.lufs(x), 2)
    return o


def _yerel_puan(y):
    return min(1.0, y["spektral_genislik_hz"] / 12000.0) * 0.5 + min(1.0, y["dinamik_aralik_lu"] / 8.0) * 0.3 + min(1.0, y["stereo_genislik"] / 0.3) * 0.2


def dinleyici_ikili(film, adaylar, din):
    """Adayları ikili karşılaştırır ('hangisi sinema filmi müziğine benziyor?'); kazanma oranı. Dinleyici yoksa None."""
    if din is None or len(adaylar) < 2: return None
    kaz = {a["dosya"]: 0 for a in adaylar}; say = {a["dosya"]: 0 for a in adaylar}
    for i in range(len(adaylar)):
        for j in range(i + 1, len(adaylar)):
            a, b = adaylar[i]["dosya"], adaylar[j]["dosya"]
            try: c = din.dinleyici(film, [a, b], "Which of the two pieces sounds more like a cinema film score?", ["A", "B"])
            except Exception: return None
            kaz[a if c.get("cevap") == "A" else b] += 1; say[a] += 1; say[b] += 1
    return {k: round(kaz[k] / max(1, say[k]), 3) for k in kaz}


def degerlendir(film, ip, motif, sablon, adaylar_yol, saglayici, asr, din, kip):
    olc, gec = [], []
    oz = [aday_olc(film, p, ip, motif, sablon, asr, kip) for p in adaylar_yol]
    hedef_bpm, hedef_ton = _bpm_istem(ip, motif), _ton_istem(ip, motif)
    for a in oz:
        b = os.path.basename(a["dosya"]); hata = False
        if a["vokal"] is None: olc.append(so.m("S6.1", "OLCULEMEDI", birim=ip["id"], olcu=f"{b}: ASR yok", esik="vokal 0"))
        elif a["vokal"]:
            hata = True; olc.append(so.m("S6.1", "HATA", birim=f"{ip['id']}#{b}", olcu=" ".join(a["vokal"][:6]), esik="vokal 0 (aday elendi)",
                                         kok_neden="vokal_sizdi"))
        if a["kirpilma"] or a["ani_kesik"]:
            hata = True; olc.append(so.m("S6.9", "HATA", birim=f"{ip['id']}#{b}", olcu=f"kırpılma {a['kirpilma']}, kesik {a['ani_kesik']}",
                                         esik="0 (aday elendi)"))
        a["motif_ok"] = None if sablon is None else (a["kroma"] or 0) >= so.esik("muzik_kroma_min")
        if hedef_bpm and a["bpm"]:
            r = a["bpm"] / float(hedef_bpm); a["bpm_ok"] = any(abs(r * k - 1) <= so.esik("muzik_bpm_tolerans") for k in (1, 2, 0.5))
        else: a["bpm_ok"] = None
        a["ton_ok"] = O.ton_ayni(hedef_ton, a["ton"]) if hedef_ton else None
        a["elendi"] = hata
        if not hata: gec.append(a)
    w = dinleyici_ikili(film, gec, din)
    for a in gec: a["dinleyici"] = (w or {}).get(a["dosya"])
    gec.sort(key=lambda a: (bool(a["motif_ok"]) if sablon is not None else True, a["dinleyici"] or 0, _yerel_puan(a["yerel"])), reverse=True)
    return oz, gec, olc, w is not None


def kaynak_kaydi(film, ip, s, dosya, motif_ad, kip):
    from datetime import date
    lis = getattr(s, "lisans", None); yan = ortak.json_oku(dosya + ".kaynak.json", None) if os.path.exists(dosya + ".kaynak.json") else None
    if yan: lis = yan.get("lisans") or lis
    return {"ipucu": ip["id"], "dosya": os.path.relpath(dosya, film).replace("\\", "/"), "saglayici": s.ad, "model": getattr(s, "model", s.ad),
            "model_surum": getattr(s, "model", None), "lisans": lis, "lisans_kaynagi": "veri/LISANSLAR.json" if not yan else "DIZIN.json",
            "istem": ip.get("istem_en"), "tohum": ip.get("tohum"), "referans_motif": motif_ad, "tarih": date.today().isoformat(),
            "sha1": so.sha1(dosya, 40), "kip": kip}


KAYIT_ALANLARI = ("dosya", "saglayici", "model", "lisans", "istem", "tarih", "sha1")


def uret(film, kip="animatik", saglayici=None, yalniz=None):
    L = ortak.json_oku(os.path.join(film, "MUZIK", "muzik_listesi.json"), None)
    if not isinstance(L, dict) or not isinstance(L.get("ipuclari"), list): raise FileNotFoundError("MUZIK/muzik_listesi.json yok ya da bozuk")
    LM = leitmotifler(film); zin, olc, yok = zincir_kur(film, kip, saglayici)
    sahte = so.sahte_mi(film, saglayici)
    asr = (so.zincir("asr", film, saglayici_=saglayici) or [None])[0]
    din = (so.zincir("dinleyici", film, saglayici_=saglayici) or [None])[0]
    KK = ortak.json_oku(os.path.join(film, "MUZIK", "KAYNAK_KAYDI.json"), {}) or {}; KK.setdefault("kayitlar", [])
    bekleyen = []; aday_n = int(so.esik("muzik_aday_sayisi")); birimler = []
    if not zin: olc.append(so.m("S6.zincir", "BAYRAK", olcu=yok, esik="hazır müzik sağlayıcısı (D-25: müziksiz + açık eksik)"))
    for ip in L["ipuclari"]:
        if yalniz and ip.get("id") != yalniz: continue
        birimler.append(ip["id"]); motif = LM.get(ip.get("motif")) if ip.get("motif") else None
        sablon = ref = None
        if motif and motif.get("notalar"):
            from saglayicilar import midi_ornek as M
            ref = os.path.join(film, "MUZIK", "motif", f"{ip['motif']}_ref.wav")
            if not os.path.exists(ref): O.yaz(ref, M.sentez(motif["notalar"], motif.get("bpm") or 72))
            sablon = O.kroma(O.oku(ref)[0])
        secilen = None; deneme = []
        for s in zin:
            try: yollar_ = s.muzik(film, ip, os.path.join(film, "MUZIK", "adaylar", ip["id"]), aday_n, referans_wav=ref, motif=motif)
            except Exception as e:
                if getattr(e, "kod", None) == "elle_bekliyor": bekleyen.append(ip["id"]); break
                deneme.append({"saglayici": s.ad, "neden": str(e)[:100]}); continue
            oz, gec, o, din_var = degerlendir(film, ip, motif, sablon, yollar_, s, asr, din, kip)
            olc += o; deneme.append({"saglayici": s.ad, "aday": len(oz), "gecen": len(gec)})
            tema = ip.get("tur") == "tema" and sablon is not None
            iyi = next((a for a in gec if a["motif_ok"]), None) if tema else (gec[0] if gec else None)
            if tema and iyi is None and gec:
                olc.append(so.m("S6.7", "BAYRAK", birim=ip["id"], olcu=f"{s.ad}: en iyi kroma {max((a['kroma'] or 0) for a in gec)}",
                                esik=f"≥ {so.esik('muzik_kroma_min')} (sıradaki sağlayıcı denenir)", kok_neden="muzik_motifsiz"))
                if s is zin[-1]: iyi = gec[0]                       # son basamak da motifsizse en iyi aday + BAYRAK
            if iyi is None: continue
            secilen = (s, iyi, din_var); break
        if secilen is None:
            if ip["id"] not in bekleyen:
                olc.append(so.m("S6_muziksiz", "BAYRAK", birim=ip["id"], olcu=deneme or "zincir boş", esik="D-25: ipucu müziksiz + açık eksik"))
                ip["secilen"], ip["olcum"] = None, {"muziksiz": True, "deneme": deneme}
            continue
        s, a, din_var = secilen
        hedef = os.path.join(film, "MUZIK", "secilen", f"{ip['id']}_{s.ad}_{so.sha1(a['dosya'], 6)}.wav")
        os.makedirs(os.path.dirname(hedef), exist_ok=True); shutil.copy2(a["dosya"], hedef)
        if os.path.exists(a["dosya"] + ".sahte.json"): shutil.copy2(a["dosya"] + ".sahte.json", hedef + ".sahte.json")
        kay = kaynak_kaydi(film, ip, s, hedef, ip.get("motif"), kip)
        KK["kayitlar"] = [k for k in KK["kayitlar"] if not (k.get("ipucu") == ip["id"] and k.get("kip") == kip)] + [kay]
        tam = all(kay.get(k) for k in KAYIT_ALANLARI)
        lis_ok = sahte or s.ad in ("midi_ornek", "kutuphane") or (kip == "animatik") or O.lisans("ace-step" if s.ad == "acestep" else s.ad).get("ticari_youtube") == "evet"
        ok68 = tam and lis_ok and (not getattr(s, "elle", False) or s is zin[-1])
        olc.append(so.m("S6.8", "GEC" if ok68 else "HATA",
                        birim=ip["id"], olcu={"kayit_tam": tam, "lisans_izinli": lis_ok, "saglayici": s.ad},
                        esik="kaynak kaydı tam; lisans izinli", kok_neden=None if (tam and lis_ok) else "lisans_belirsiz"))
        if sablon is not None and ip.get("tur") == "tema":
            olc.append(so.m("S6.7", "GEC" if a["motif_ok"] else "BAYRAK", birim=ip["id"], olcu=a["kroma"], esik=f"≥ {so.esik('muzik_kroma_min')}"))
        olc.append(so.m("S6.10", "GEC" if (a["bpm_ok"] is not False and a["ton_ok"] is not False) else "BAYRAK", birim=ip["id"],
                        olcu={"bpm": a["bpm"], "ton": a["ton"]}, esik="BPM ±%3; ton aynı"))
        olc.append(so.m("S6.kalite", "GEC" if (din_var and (a["dinleyici"] or 0) >= so.esik("muzik_kalite_ikili_min")) else
                        ("BAYRAK" if din_var else "OLCULEMEDI"), birim=ip["id"],
                        olcu={"dinleyici": a["dinleyici"], "yerel": a["yerel"]}, esik=f"dinleyici ikili ≥ {so.esik('muzik_kalite_ikili_min')}",
                        neden=None if din_var else "dinleyici yok (ücretsiz Gemini anahtarı): açık eksik, izle-dinle paketi"))
        ip["secilen"] = {"dosya": kay["dosya"], "saglayici": s.ad, "kip": kip}
        ip["olcum"] = {k: a.get(k) for k in ("kroma", "bpm", "ton", "yerel", "dinleyici", "lufs")}
        log(f"   {ip['id']} ({ip.get('tur')}): {s.ad} → {os.path.basename(hedef)} · kroma {a['kroma']} · bpm {a['bpm']}")
    ortak.atomik_yaz(os.path.join(film, "MUZIK", "muzik_listesi.json"), L)
    ortak.atomik_yaz(os.path.join(film, "MUZIK", "KAYNAK_KAYDI.json"), KK)
    if bekleyen:
        olc.append(so.m("S6.elle", "BAYRAK", olcu=bekleyen, esik="Gemini müzik paketi kullanıcı işi (MUZIK/GEMINI_PAKET/istemler.json)"))
    yol, r = so.rapor(film, "S6", "URET" if kip == "animatik" else "URET_YAYIN", olc, birimler=birimler, arac=SURUM,
                      ek={"kip": kip, "zincir": [s.ad for s in zin], "hazir_olmayan": yok}, gorev_raporu=False)
    return yol, r, bekleyen


def main(argv):
    try: film = so.film_coz(so.arg(argv, "--film"))
    except (ValueError, ortak.YolYok) as e: log(f"!! {e}"); return 4
    kip = so.arg(argv, "--kip") or ("animatik" if (so.gorev()["asama"] or "A12") in ("A12", "A10c", "A11") else "yayin")
    try: yol, r, bek = uret(film, kip, so.arg(argv, "--saglayici"), so.arg(argv, "--ipucu"))
    except FileNotFoundError as e: log(f"!! {e}"); return 1
    log(f"S6 {kip} → {r['sonuc']} ({os.path.relpath(yol, film)})")
    if bek:
        log("Masaüstündeki film klasöründe MUZIK/GEMINI_PAKET/istemler.json'daki istemleri Gemini'ye ver; gelen dosyaları filmin GELENLER "
            "klasörüne MUZIK_<ipucu>_1.wav adıyla koy. Ben dosyaları görünce kendim devam ederim."); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
