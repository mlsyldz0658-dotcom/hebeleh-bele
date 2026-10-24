"""SES SEÇ — telaffuz testi ve karakter sesi seçimi (TASARIM §1.3 A10b/A10c, §2.2, §6.6; [SM2] §4.2 SB1–SB2, §4.5.5, §4.7.2 S1).

Kullanım (film.py görevi; alt komutlar birlikte verilebilir, sırayla koşar):
  python ses_sec.py --telaffuz --film F      A10b: her ad için adı içeren 3 replik, iki sabit genel sesle (kadın + erkek; FILM_AYAR ses.
        telaffuz_sesleri) okunur, ASR ile geri tanınır; yazım ya da fonetik anahtar eşleşmesi (S1.2). Geçmeyen adda alternatif okunuş
        yazımları denenir; ad HATA'dır ve öneriyle KUYRUK/YENIDEN_YAZ'a gider (hikaye-yazari·dar_degisiklik, H15).
        → _RAPOR/S1a_telaffuz.json, _SES/TELAFFUZ.json
  python ses_sec.py --ara --olc --oku --puanla --sec --film F      A10c (görev "--ara --olc --sec" verir; --oku/--puanla --sec'e dahildir)
        --ara    paylaşılan ses araması ([D-EL] süzgeçleri; geçmeyen süzgeç yerelde): İngilizce, voice_restricted değil, önizleme var,
                 bildirim süresi ≥ 30 gün (S1.1); seride başka karakterin sesi elenir (S1.9) → _SES/SES_ADAYLAR.json
        --olc    ücretsiz önizlemeler: F0 medyanı/aralığı (S1.6), konuşmacı gömmesi; profil uyumuna göre en iyi 4 aday ayrılır
        --oku    en iyi 4 aday karakterin 3 karakteristik repliğini okur (normal, duygusal, fısıltı/bağırma; önbellekli; BUTK seri dilimi)
        --puanla S1.8: 0,25 profil + 0,20 ayırt edicilik + 0,20 kalite (S1.2–S1.3) + 0,15 kararlılık + 0,10 duygu aralığı + 0,10 bildirim
        --sec    açgözlü kadro: S1.5 (merkez benzerliği ≤ 0,60; aynı cinsiyette F0 farkı ≥ 2 yarım ton) ve S1.9 korunur; puan farkı
                 < 0,03 ise seçim kodun önerisidir ve _SES/SES_SECIM_YAKIN.json + BAYRAK (ses-tasarimcisi·kadro karar verir).
                 Evren ses.json (§4.5.5) <film>/_SES/evren_ses/<id>/ses.json'a aşamalanır; evren.py ses_kaydet sunuyorsa kalıcı evrene
                 o yazar (evrene yalnız evren.py yazar, D-42). ses_etiketi_tr: benzerliği ≥ 0,60 iki karakter aynı etiketi alır (İ-9).
                 → _RAPOR/S1_FILM.json, _SES/SES_SECIM.html (bilgi; onay kapısı değildir)
  python ses_sec.py --banka --film F         RVC ses bankası: yalnız Ö0-c RVC'yi seçtiyse ve koşullar izin veriyorsa (P1); yoksa 4
Ortak: --saglayici sahte (test). Claude sesi duymaz: seçim yalnız ölçüye ve tarife dayanır. Gömme yedek yöntemle ölçülüyorsa (gerçek
  konuşmacı modeli kurulu değil) S1.4/S1.5 benzerlik maddeleri en çok BAYRAK verir (eşikler gerçek gömmeye göredir).
Çıkış kodları: 0 rapor yazıldı (sonuç raporda) · 1 girdi yok/bozuk · 4 ORTAM (TTS/katalog yok, telaffuz sesleri tanımsız) · 5 BÜTÇE · 7 KISIT.
"""
import os, sys, re, json, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak
import ses_ortak as so

SURUM = "ses_sec 1.0"
SR = so.SR
KALIPLAR = ["{ad}, come here.", "I told you, {ad}, not tonight.", "Where is {ad} now?"]
OKUMA_KALIPLARI = {"normal": "We should leave before the light goes.", "duygusal": "I can't lose you too. Not after everything.",
                   "fisilti": "Quiet. They're right outside the door.", "bagirma": "Get down! Now!"}
YAS = {"genc": "young", "orta": "middle_aged", "yasli": "old", "cocuk": "young", "yetiskin": "middle_aged"}
CINS = {"kadin": "female", "erkek": "male"}


def log(*a): print(*a, flush=True)


# --- fonetik ve ad eşleşmesi ------------------------------------------------------------------------------------------
def fonetik(s):
    """Basit fonetik anahtar (Metaphone benzeri; bellekten): sessiz harf iskeleti, ilk harf korunur."""
    s = re.sub(r"[^a-z]", "", (s or "").lower())
    if not s: return ""
    for a, b in (("ph", "f"), ("ck", "k"), ("sch", "sk"), ("sh", "x"), ("ch", "x"), ("th", "0"), ("gh", "g"), ("dg", "j"), ("qu", "kw"),
                 ("wr", "r"), ("kn", "n"), ("wh", "w"), ("x", "ks"), ("q", "k"), ("z", "s"), ("v", "f")):
        s = s.replace(a, b)
    s = re.sub(r"c(?=[eiy])", "s", s).replace("c", "k")
    bas, gov = s[0], re.sub(r"[aeiouyhw]", "", s[1:])
    out = bas + gov
    return re.sub(r"(.)\1+", r"\1", out)


def ad_dogru(ad, metin):
    adk = re.sub(r"[^a-z]", "", ad.lower()); fk = fonetik(ad)
    for w in re.findall(r"[A-Za-z][A-Za-z'\-]*", metin or ""):
        k = re.sub(r"'s$", "", w.lower()); k = re.sub(r"[^a-z]", "", k)
        if k == adk or (fk and fonetik(k) == fk): return True
    return False


def alternatifler(ad, okunus=None):
    """Okunuş yazımı önerileri: ad_telaffuz, hece tireli, ünlü uzatmalı, çift sessizli."""
    out = [okunus] if okunus else []
    m = re.match(r"^([^aeiou]*[aeiou]+[^aeiou])(.*)$", ad, re.I)
    if m and m.group(2): out.append(f"{m.group(1).capitalize()}-{m.group(2).lower()}")
    if m: out.append(m.group(1)[:-1] + m.group(1)[-1] * 2 + m.group(2))
    if ad[-1:].lower() == "a": out.append(ad + "h")
    if ad[-1:].lower() == "e": out.append(ad[:-1] + "eh")
    return [x for i, x in enumerate(out) if x and x != ad and x not in out[:i]]


# --- girdiler --------------------------------------------------------------------------------------------------------
def adlar(film):
    H = so.hikaye(film); out = {}
    for kid, k in (H.get("karakterler") or {}).items():
        if isinstance(k, dict) and k.get("ad"): out[k["ad"]] = {"karakter": kid, "okunus": k.get("ad_telaffuz")}
    for a in ((H.get("sozluk") or {}).get("adlar") or []):
        if isinstance(a, dict) and a.get("ad"): out.setdefault(a["ad"], {"karakter": None, "okunus": a.get("ad_telaffuz")})
        elif isinstance(a, str): out.setdefault(a, {"karakter": None, "okunus": None})
    return out


def ad_replikleri(film, ad, n=3):
    rs = [r for r in (so.hikaye(film).get("replikler") or []) if re.search(rf"\b{re.escape(ad)}\b", r.get("metin") or "")]
    satir = [(r["metin"], r.get("sahne")) for r in rs[:n]]
    i = 0
    while len(satir) < n: satir.append((KALIPLAR[i % len(KALIPLAR)].format(ad=ad), None)); i += 1
    return satir


def profiller(film):
    p = ortak.json_oku(os.path.join(film, "_SES", "SES_PROFILLERI.json"), {}) or {}
    p = p.get("karakterler", p) if isinstance(p, dict) else {}
    H = so.hikaye(film); konusan = {r.get("karakter") for r in H.get("replikler") or []}
    out = {}
    for kid, k in (H.get("karakterler") or {}).items():
        if kid not in konusan and kid not in p: continue
        pr = dict(p.get(kid) or {}); sk = (k or {}).get("ses_karakteri") or ""; t = pr.get("veo_ses_tarifi") or ""
        pr.setdefault("cinsiyet", "kadin" if re.search(r"kad[ıi]n|female|woman", sk + " " + t, re.I) else
                      ("erkek" if re.search(r"erkek|\bmale\b|\bman\b", sk + " " + t, re.I) else None))
        if not pr.get("yas_bandi"):
            pr["yas_bandi"] = "genc" if re.search(r"gen[çc]|young", sk, re.I) else ("yasli" if re.search(r"ya[şs]l[ıi]|old", sk, re.I) else "orta")
        if not pr.get("aksan"):
            m = re.search(r"with an? ([a-z ]+?) accent", t, re.I); pr["aksan"] = aksan_coz(m.group(1)) if m else None
        pr["rol"] = (k or {}).get("rol"); pr["ad"] = (k or {}).get("ad", kid)
        out[kid] = pr
    return out


def aksan_sozlugu():
    return (ortak.json_oku(os.path.join(HERE, "veri", "aksan_sozlugu.json"), {}) or {}).get("aksanlar") or {}


def aksan_coz(s):
    if not s: return None
    k = re.sub(r"[^a-z_]", "_", s.strip().lower().replace(" ", "_"))
    A = aksan_sozlugu()
    if k in A: return k
    for ad, v in A.items():
        if k in (v.get("es") or []): return ad
    return k


def aksan_uyar(profil_aksan, etiket):
    if not profil_aksan: return None
    A = aksan_sozlugu().get(profil_aksan) or {}
    kabul = [x.lower() for x in (A.get("ai84") or [profil_aksan])]
    if not kabul: return True                                       # nötr: her etiket
    return (etiket or "").lower() in kabul


def seride_kullanilan(film, haric):
    """Seride başka karakterlerin kullandığı voice_id'ler (kalıcı evren + film aşaması)."""
    out = {}
    kok, s = so.evren_kok(film), so.seri(film)
    for d in ([os.path.join(kok, s, "karakterler")] if (kok and s) else []) + [os.path.join(film, "_SES", "evren_ses")]:
        if not os.path.isdir(d): continue
        for kid in os.listdir(d):
            if kid == haric: continue
            v = (((ortak.json_oku(os.path.join(d, kid, "ses.json"), {}) or {}).get("secim") or {}).get("voice_id"))
            if v: out[v] = kid
    return out


def katalog(film, saglayici):
    return next((s for s in so.zincir("tts", film, saglayici_=saglayici) if "katalog" in getattr(s, "turler", ())), None)


# --- telaffuz (A10b) -------------------------------------------------------------------------------------------------
def telaffuz(film, saglayici=None):
    from olcum import ses as O
    sahte = so.sahte_mi(film, saglayici)
    tts = so.zincir("tts", film, saglayici_=saglayici); asr = (so.zincir("asr", film, saglayici_=saglayici) or [None])[0]
    if not tts: log("!! hazır TTS yok (telaffuz testi)"); return so.ORTAM, None
    ts = (so.ayar(film).get("ses") or {}).get("telaffuz_sesleri") or ({"kadin": "sahte_tel_k", "erkek": "sahte_tel_e"} if sahte else {})
    if not (ts.get("kadin") and ts.get("erkek")):
        log("!! FILM_AYAR.json ses.telaffuz_sesleri (bir kadın, bir erkek genel ses) tanımsız; kurulum yazar"); return so.ORTAM, None
    A = adlar(film); olc, kayit, yaz = [], {}, []
    if not A: olc.append(so.m("S1.2", "BAYRAK", olcu="HIKAYE.json'da ad yok", esik="ad listesi"))
    s0 = tts[0]; n = int(so.esik("telaffuz_replik_sayisi"))
    if getattr(s0, "kredili", False):
        harf = sum(len(m) for ad in A for m, _ in ad_replikleri(film, ad, n)) * 2
        if so.kredi_onay(film, f"A10b-telaffuz-{so.ozet(*A, n=6)}", harf, "film", s0.ad): return so.BUTCE, None
    def oku_ve_tani(metin, ses, yol):
        if getattr(s0, "kredili", False) and not s0.onbellekte_mi(film, metin, ses):
            so.gonderim(film, "telaffuz", s0.tahmin(metin), so.ozet(ses, metin), "film", s0.ad)
        s0.tts(film, metin, ses, yol)
        return asr.asr(film, yol, None)["metin"] if asr else None
    for ad, bilgi in A.items():
        hata, ornek = 0, []
        satirlar = ad_replikleri(film, ad, n)
        for i, (metin, _) in enumerate(satirlar):
            for cins, ses in (("k", ts["kadin"]), ("e", ts["erkek"])):
                yol = os.path.join(film, "SESLER", "telaffuz", f"{re.sub(r'[^A-Za-z0-9]', '_', ad)}_{i + 1}{cins}.wav")
                os.makedirs(os.path.dirname(yol), exist_ok=True)
                duy = oku_ve_tani(metin, ses, yol)
                if duy is None: continue
                ok = ad_dogru(ad, duy); hata += (not ok); ornek.append({"metin": metin, "duyulan": duy, "ses": cins, "dogru": ok})
        if asr is None:
            olc.append(so.m("S1.2", "OLCULEMEDI", birim=ad, olcu="ASR yok (faster-whisper kurulu değil)", esik="ad hatası 0"))
            kayit[ad] = {"sonuc": "OLCULEMEDI"}; continue
        oneri = None
        if hata:
            for alt in alternatifler(ad, bilgi.get("okunus")):
                deneme = [oku_ve_tani(m.replace(ad, alt), ts["kadin"], os.path.join(film, "SESLER", "telaffuz", f"alt_{so.ozet(alt, m, n=8)}.wav"))
                          for m, _ in satirlar]
                if all(ad_dogru(ad, d) or ad_dogru(alt.replace("-", ""), d) for d in deneme if d is not None): oneri = alt; break
        olc.append(so.m("S1.2", "GEC" if not hata else "HATA", birim=ad, olcu={"hata": hata, "ornek": [o for o in ornek if not o["dogru"]][:3]},
                        esik="ad hatası 0", oneri=(f"okunuş yazımı '{oneri}' (replikte ve veo_metin'de)" if oneri else
                                                   "ad değişikliği (hikaye-yazari·dar_degisiklik)") if hata else None,
                        kok_neden="ad_yanlis_okundu" if hata else None))
        kayit[ad] = {"karakter": bilgi.get("karakter"), "sonuc": "GEC" if not hata else "HATA", "hata": hata, "okunus_onerisi": oneri}
        if hata:
            sahne = next((s for _, s in satirlar if s), None) or next((s.get("id") for s in so.hikaye(film).get("sahneler") or []
                                                                       if isinstance(s, dict) and s.get("id")), None)
            if sahne:
                yaz.append({"konum": {"sahne": sahne}, "kapi": "S1a", "madde": "S1.2", "kok_neden": "ad_yanlis_okundu", "yazar": "hikaye-yazari",
                            "oneri": f"'{ad}' TTS ve ASR'de tutmuyor" + (f"; okunuş yazımı '{oneri}' dene" if oneri else "; adı değiştir (dar değişiklik)")})
    ortak.atomik_yaz(os.path.join(film, "_SES", "TELAFFUZ.json"), {"_surum": 1, "adlar": kayit, "zaman": so.simdi()})
    ys = so.yaz_ekle(film, yaz, "A10b")
    return so.BITTI, so.rapor(film, "S1a", "telaffuz", olc, asama="A10b", birimler=list(A), arac=SURUM,
                              ek={"yeniden_yaz": ys.get("eklenen")})


# --- ses seçimi (A10c) -----------------------------------------------------------------------------------------------
def ara(film, saglayici, P):
    k = katalog(film, saglayici)
    if k is None: return None
    out, olc = {}, []
    for kid, pr in P.items():
        f = {"language": "en", "gender": CINS.get(pr.get("cinsiyet")), "age": YAS.get(pr.get("yas_bandi"))}
        try: hepsi = k.voices(**{a: v for a, v in f.items() if v})
        except Exception as e:
            if so.kisit_kodu(e) is not None and hasattr(e, "kod"): raise
            hepsi = []
        kul = seride_kullanilan(film, kid); ad = []
        for v in hepsi:
            el = None
            if (v.get("language") or "en") != "en": el = "S1.1 İngilizce değil"
            elif v.get("voice_restricted"): el = "S1.1 voice_restricted"
            elif not v.get("preview"): el = "S1.1 önizleme yok"
            elif v["voice_id"] in kul: el = f"S1.9 seride {kul[v['voice_id']]} kullanıyor"
            elif CINS.get(pr.get("cinsiyet")) and v.get("gender") and v["gender"] != CINS[pr["cinsiyet"]]: el = "cinsiyet uymuyor"
            bild = v.get("notice_period")
            ad.append(dict(v, elenme=el, bildirim_bayrak=(bild is not None and bild < so.esik("s1_notice_min_gun"))))
        out[kid] = ad
        uy = [a for a in ad if not a["elenme"]]
        olc.append(so.m("S1.1", "GEC" if uy else "HATA", birim=kid, olcu={"aday": len(ad), "uygun": len(uy),
                        "bildirim_kisa": sum(1 for a in uy if a["bildirim_bayrak"])}, esik="en az bir uygun aday",
                        oneri=None if uy else "süzgeci genişlet (yaş/aksan) ya da profil (ses-tasarimcisi·kadro)"))
    ortak.atomik_yaz(os.path.join(film, "_SES", "SES_ADAYLAR.json"), {"_surum": 1, "karakterler": out, "zaman": so.simdi()})
    return out, olc


def _profil_uyum(pr, a):
    from olcum import ses as O
    p = []
    if pr.get("cinsiyet"): p.append(1.0 if a.get("gender") == CINS.get(pr["cinsiyet"]) else 0.0)
    if pr.get("yas_bandi"): p.append(1.0 if a.get("age") == YAS.get(pr["yas_bandi"]) else 0.5)
    u = aksan_uyar(pr.get("aksan"), a.get("accent"))
    if u is not None: p.append(1.0 if u else 0.0)
    f = a.get("f0_medyan_hz"); b = (so.esik("s1_perde_bant_hz") or {}).get(pr.get("cinsiyet"))
    if f and b:
        perde = pr.get("perde") or "orta"
        ic = (f < b[0]) if "dusuk" in perde and "orta" not in perde else ((f > b[1]) if "yuksek" in perde else (b[0] - 15 <= f <= b[1] + 15))
        a["perde_bandi_ok"] = bool(ic); p.append(1.0 if ic else 0.4)
    return sum(p) / len(p) if p else 0.5


def olc_onizleme(film, saglayici, P, adaylar):
    from olcum import ses as O
    k = katalog(film, saglayici); dz = os.path.join(film, "SESLER", "ses_secim", "onizleme")
    for kid, ad in adaylar.items():
        for a in ad:
            if a["elenme"]: continue
            p = os.path.join(dz, f"{a['voice_id']}.wav"); os.makedirs(dz, exist_ok=True)
            try:
                if not os.path.exists(p) and k.onizleme(a["voice_id"], p, url=a.get("preview_url")) is None: a["elenme"] = "önizleme indirilemedi"; continue
                x, _ = O.oku(p); f = O.f0(x)
                a.update(f0_medyan_hz=f["medyan_hz"], f0_p10_p90_hz=[f["p10_hz"], f["p90_hz"]], onizleme=os.path.relpath(p, film),
                         gomme=[round(float(v), 5) for v in O.gomme(x)])
            except Exception as e: a["elenme"] = f"önizleme ölçülemedi ({str(e)[:60]})"
            a["profil_uyum"] = round(_profil_uyum(P[kid], a), 3)
        ust = sorted([a for a in ad if not a["elenme"]], key=lambda a: -a["profil_uyum"])[:int(so.esik("s1_aday_oku_max"))]
        for a in ad: a["okunacak"] = a in ust


def okuma_satirlari(film, kid):
    rs = [r for r in so.hikaye(film).get("replikler") or [] if r.get("karakter") == kid]
    sinif = {so.teslim_sinifi(r.get("teslim")): r["metin"] for r in rs}
    norm = sinif.get("normal") or (rs[0]["metin"] if rs else OKUMA_KALIPLARI["normal"])
    duy = next((r["metin"] for r in rs if r["metin"] != norm), OKUMA_KALIPLARI["duygusal"])
    ozel = sinif.get("fisilti") or sinif.get("bagirma")
    return [("normal", norm), ("duygusal", duy), ("fisilti" if "fisilti" in sinif or not ozel else "bagirma", ozel or OKUMA_KALIPLARI["fisilti"])]


def oku_puanla(film, saglayici, P, adaylar):
    from olcum import ses as O
    tts = so.zincir("tts", film, saglayici_=saglayici); asr = (so.zincir("asr", film, saglayici_=saglayici) or [None])[0]
    if not tts: return so.ORTAM
    s0 = tts[0]; dz = os.path.join(film, "SESLER", "ses_secim", "okuma")
    oku = [(kid, a) for kid, ad in adaylar.items() for a in ad if a.get("okunacak")]
    if getattr(s0, "kredili", False):
        harf = sum(len(m) for kid, a in oku for _, m in okuma_satirlari(film, kid) if not s0.onbellekte_mi(film, m, a["voice_id"]))
        if harf and so.kredi_onay(film, f"A10c-secim-{so.ozet(*[a['voice_id'] for _, a in oku], n=6)}", harf, "seri", s0.ad): return so.BUTCE
    adl = {v["karakter"]: ad for ad, v in adlar(film).items() if v.get("karakter")}
    for kid, a in oku:
        g, lu, f0s, wers, ad_ok = [], [], [], [], True
        for tes, m in okuma_satirlari(film, kid):
            p = os.path.join(dz, f"{kid}_{a['voice_id']}_{tes}.wav"); os.makedirs(dz, exist_ok=True)
            if not os.path.exists(p):
                if getattr(s0, "kredili", False): so.gonderim(film, f"secim:{kid}", s0.tahmin(m), so.ozet(a["voice_id"], m), "seri", s0.ad)
                s0.tts(film, m, a["voice_id"], p, teslim=tes)
            x, _ = O.oku(p); g.append(O.gomme(x)); lu.append(O.lufs(x)); f0s.append(O.f0(x)["medyan_hz"])
            if asr:
                duy = asr.asr(film, p)["metin"]; wers.append(O.wer(m, duy))
                if adl.get(kid) and adl[kid] in m: ad_ok = ad_ok and ad_dogru(adl[kid], duy)
        sims = [O.benzerlik(g[i], g[j]) for i in range(len(g)) for j in range(i + 1, len(g))]
        a["kararlilik"] = round(sum(sims) / len(sims), 3) if sims else None
        a["wer"] = round(sum(wers) / len(wers), 3) if wers else None; a["ad_dogru"] = ad_ok if asr else None
        yt = [O.yarim_ton(f0s[0], f) for f in f0s[1:] if f and f0s[0]]
        a["duygu_araligi"] = round(min(1.0, ((max(lu) - min(lu)) / 10.0 + (max([abs(v) for v in yt] or [0]) / 6.0)) / 2), 3)
        mer = [sum(c) / len(c) for c in zip(*g)]; a["merkez"] = [round(float(v), 5) for v in mer]
    W = so.esik("s1_agirliklar")
    for kid, ad in adaylar.items():
        for a in [a for a in ad if a.get("okunacak") and a.get("merkez")]:
            diger = [b["merkez"] for k2, ad2 in adaylar.items() if k2 != kid for b in ad2 if b.get("okunacak") and b.get("merkez")]
            a["ayirt"] = round(1 - max([O.benzerlik(a["merkez"], d) for d in diger] or [0.0]), 3)
            kal = (max(0.0, 1 - (a["wer"] or 0) / (2 * so.esik("s1_wer_max"))) if a["wer"] is not None else 0.5) * (0.5 if a.get("ad_dogru") is False else 1)
            bil = min(1.0, (a.get("notice_period") or 0) / 90.0)
            a["puan"] = round(W["profil"] * a["profil_uyum"] + W["ayirt"] * max(0, a["ayirt"]) + W["kalite"] * kal +
                              W["kararlilik"] * max(0, a["kararlilik"] or 0) + W["duygu"] * a["duygu_araligi"] + W["bildirim"] * bil, 4)
    return so.BITTI


def sec(film, P, adaylar):
    from olcum import ses as O
    yedek = O.GOMME_YONTEMI.endswith("yedek"); olc, secim, yakin = [], {}, {}
    sira = sorted(P, key=lambda k: (0 if P[k].get("rol") in ("kahraman", "ana") else 1, k))
    for kid in sira:
        ad = sorted([a for a in adaylar.get(kid, []) if a.get("puan") is not None], key=lambda a: -a["puan"])
        if not ad: olc.append(so.m("S1.secim", "HATA", birim=kid, olcu="puanlanmış aday yok", esik="≥ 1 aday")); continue
        sec_ = None
        for a in ad:
            if a["voice_id"] in {s["voice_id"] for s in secim.values()}: continue
            cak = [(k2, O.benzerlik(a["merkez"], s["merkez"]), O.yarim_ton(s.get("f0_medyan_hz"), a.get("f0_medyan_hz")))
                   for k2, s in secim.items()]
            kotu = [c for c in cak if c[1] > so.esik("s1_kadro_benzerlik_max") or
                    (P[c[0]].get("cinsiyet") == P[kid].get("cinsiyet") and c[2] is not None and abs(c[2]) < so.esik("s1_kadro_f0_fark_min_yt"))]
            if not kotu: sec_ = a; break
        s15 = "GEC"
        if sec_ is None:
            sec_ = next((a for a in ad if a["voice_id"] not in {s["voice_id"] for s in secim.values()}), ad[0]); s15 = "BAYRAK" if yedek else "HATA"
        secim[kid] = sec_
        if len(ad) > 1 and ad[0]["puan"] - ad[1]["puan"] < so.esik("s1_secim_fark_min"):
            yakin[kid] = [{"voice_id": a["voice_id"], "ad": a.get("name"), "puan": a["puan"]} for a in ad[:3]]
        oran = {"kod (fark ≥ 0,03)": kid not in yakin}
        olc += [so.m("S1.5", s15, birim=kid, olcu={"secilen": sec_["voice_id"]}, esik="merkez benzerliği ≤ 0,60; aynı cinsiyette ≥ 2 yarım ton"),
                so.m("S1.9", "GEC" if sec_["voice_id"] not in seride_kullanilan(film, kid) else "HATA", birim=kid, olcu=sec_["voice_id"], esik="seride tek"),
                so.m("S1.3", ("GEC" if (sec_.get("wer") or 0) <= so.esik("s1_wer_max") else "HATA") if sec_.get("wer") is not None else "OLCULEMEDI",
                     birim=kid, olcu=sec_.get("wer"), esik=f"≤ {so.esik('s1_wer_max')}"),
                so.m("S1.2", {True: "GEC", False: "HATA", None: "OLCULEMEDI"}[sec_.get("ad_dogru")], birim=kid, olcu=sec_.get("ad_dogru"), esik="ad doğru"),
                so.m("S1.4", "GEC" if (sec_.get("kararlilik") or 0) >= so.esik("s1_kararlilik_min") else "BAYRAK", birim=kid,
                     olcu=sec_.get("kararlilik"), esik=f"≥ {so.esik('s1_kararlilik_min')}", neden="yedek gömme" if yedek else None),
                so.m("S1.6", "GEC" if sec_.get("perde_bandi_ok", True) else "BAYRAK", birim=kid, olcu=sec_.get("f0_medyan_hz"), esik="profil perde bandı"),
                so.m("S1.7", {True: "GEC", False: "HATA", None: "OLCULEMEDI"}[aksan_uyar(P[kid].get("aksan"), sec_.get("accent"))], birim=kid,
                     olcu={"profil": P[kid].get("aksan"), "etiket": sec_.get("accent")}, esik="aksan etiketi = profil aksanı")]
        if kid in yakin:
            olc.append(so.m("S1.8", "BAYRAK", birim=kid, olcu=yakin[kid], esik="puan farkı ≥ 0,03", oneri="ses-tasarimcisi·kadro seçer"))
    # ses etiketi (İ-9) ve kayıt
    etiket = {kid: P[kid].get("ses_etiketi_tr") for kid in secim}
    ks = list(secim)
    for i in range(len(ks)):
        for j in range(i + 1, len(ks)):
            if (O.benzerlik(secim[ks[i]]["merkez"], secim[ks[j]]["merkez"]) or 0) >= so.esik("s1_etiket_ortak_benzerlik"):
                etiket[ks[j]] = etiket[ks[i]] or etiket[ks[j]]
    for kid, a in secim.items():
        kay = {"karakter": kid, "seri": so.seri(film), "surum": 1, "durum": "taslak" if kid in yakin else "kilitli", "tur": P[kid].get("tur", "insan"),
               "profil": {k: P[kid].get(k) for k in ("cinsiyet", "yas_bandi", "aksan", "perde", "tini", "tempo", "enerji")},
               "veo_ses_tarifi": P[kid].get("veo_ses_tarifi"), "ses_etiketi_tr": etiket.get(kid),
               "secim": {"saglayici": "ai84", "voice_id": a["voice_id"], "ses_adi": a.get("name"), "kaynak": "paylasilan",
                         "accent_etiketi": a.get("accent"), "notice_period_gun": a.get("notice_period"), "model": "eleven_v4",
                         "ayarlar": None, "seed": None, "tarih": so.simdi()[:10], "puan": a["puan"],
                         "karar_veren": "kod (fark < 0,03; ses-tasarimcisi·kadro bakar)" if kid in yakin else "kod (fark ≥ 0,03)",
                         "adaylar": [{"voice_id": b["voice_id"], "puan": b.get("puan"), "elenme": b.get("elenme")}
                                     for b in adaylar[kid] if b is not a][:6]},
               "olcum": {"f0_medyan_hz": a.get("f0_medyan_hz"), "f0_p10_p90_hz": a.get("f0_p10_p90_hz"), "merkez": a.get("merkez"),
                         "gomme_yontemi": O.GOMME_YONTEMI, "benzerlik_esigi": so.esik("ses_donusum_benzerlik_min")},
               "donusum": None, "banka": None, "filmler": [os.path.basename(film)],
               "lisans_notu": "Paylaşılan ses; sahibi kaldırabilir. Sigorta: referans kayıt + (RVC seçildiyse) banka ve model."}
        _, asama_yolu = so.evren_ses_yolu(film, kid); ortak.atomik_yaz(asama_yolu, kay)
        try:
            import evren
            if hasattr(evren, "ses_kaydet"): evren.ses_kaydet(film, kid, kay)
            else: olc.append(so.m("S1.evren", "BAYRAK", birim=kid, olcu="evren.py ses_kaydet yok; film içinde aşamalandı", esik="evrene evren.py yazar"))
        except Exception as e: olc.append(so.m("S1.evren", "BAYRAK", birim=kid, olcu=str(e)[:80], esik="evren kaydı"))
    if yakin: ortak.atomik_yaz(os.path.join(film, "_SES", "SES_SECIM_YAKIN.json"), {"_surum": 1, "karakterler": yakin})
    html_yaz(film, secim, adaylar, P)
    return olc, secim


def html_yaz(film, secim, adaylar, P):
    satir = []
    for kid, a in secim.items():
        ses = [f"<audio controls src='../SESLER/ses_secim/okuma/{html.escape(os.path.basename(p))}'></audio>"
               for p in sorted(os.listdir(os.path.join(film, "SESLER", "ses_secim", "okuma"))) if p.startswith(f"{kid}_{a['voice_id']}_")] \
            if os.path.isdir(os.path.join(film, "SESLER", "ses_secim", "okuma")) else []
        satir.append(f"<tr><td>{html.escape(P[kid].get('ad', kid))}</td><td>{html.escape(str(a.get('name')))}</td><td>{a.get('puan')}</td>"
                     f"<td>{a.get('f0_medyan_hz')}</td><td>{''.join(ses)}</td></tr>")
    p = os.path.join(film, "_SES", "SES_SECIM.html"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8") as f:
        f.write("<!doctype html><meta charset='utf-8'><title>Ses kadrosu</title><h1>Ses kadrosu (bilgi; onay gerekmez)</h1>"
                "<p>Ekip sesleri ölçüye göre seçti. Dinlemek istersen aşağıda; itirazın olursa film-not ile yaz.</p>"
                "<table border=1 cellpadding=4><tr><th>Karakter</th><th>Ses</th><th>Puan</th><th>F0 (Hz)</th><th>Örnek</th></tr>"
                + "".join(satir) + "</table>")
    os.replace(p + ".tmp", p)


def secim_akisi(film, argv, saglayici):
    P = profiller(film)
    if not P: log("!! konuşan karakter ya da ses profili yok (_SES/SES_PROFILLERI.json)"); return so.HATA, None
    olc = [so.m("S1.profil", "HATA", birim=k, olcu="cinsiyet bilinmiyor", esik="profil tam") for k, p in P.items() if not p.get("cinsiyet")]
    sonuc = ara(film, saglayici, P)
    if sonuc is None: log("!! ses kataloğu sağlayan TTS yok"); return so.ORTAM, None
    adaylar, o = sonuc; olc += o
    olc_onizleme(film, saglayici, P, adaylar)
    kod = oku_puanla(film, saglayici, P, adaylar)
    if kod: return kod, None
    if "--sec" in argv:
        o, secim = sec(film, P, adaylar); olc += o
    ortak.atomik_yaz(os.path.join(film, "_SES", "SES_ADAYLAR.json"), {"_surum": 1, "karakterler": adaylar, "zaman": so.simdi()})
    return so.BITTI, so.rapor(film, "S1", "FILM", olc, asama="A10c", birimler=list(P), arac=SURUM)


def main(argv):
    try: film = so.film_coz(so.arg(argv, "--film"))
    except (ValueError, ortak.YolYok) as e: log(f"!! {e}"); return so.ORTAM
    sg = so.arg(argv, "--saglayici"); kod = so.BITTI
    try:
        if "--telaffuz" in argv:
            kod, r = telaffuz(film, sg)
            if r: log(f"S1a telaffuz → {r[1]['sonuc']} ({os.path.relpath(r[0], film)})")
            if kod: return kod
        if any(a in argv for a in ("--ara", "--olc", "--oku", "--puanla", "--sec")):
            kod, r = secim_akisi(film, argv, sg)
            if r: log(f"S1 ses seçimi → {r[1]['sonuc']} ({os.path.relpath(r[0], film)})")
        if "--banka" in argv:
            log("RVC ses bankası yalnız Ö0-c RVC'yi seçtiyse ve ElevenLabs/AI84 koşulları TTS çıktısıyla eğitime izin veriyorsa kurulur (P1)."); return so.ORTAM
    except Exception as e:
        if hasattr(e, "kod") and so.kisit_kodu(e) is not None: log(f"!! geçilemez kısıt: {e}"); return so.kisit_kodu(e)
        raise
    if kod == so.BITTI and not any(a in argv for a in ("--telaffuz", "--ara", "--olc", "--oku", "--puanla", "--sec", "--banka")):
        log(__doc__); return so.ORTAM
    return kod


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
