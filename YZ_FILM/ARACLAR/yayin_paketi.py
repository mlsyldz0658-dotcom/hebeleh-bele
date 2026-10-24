"""YAYIN PAKETİ — YouTube paketinin taslağı ve doğrulaması (TASARIM §1.3 A17, §6.8, §7.2 YAYIN, D-26, D-40; KARARLAR.md başlık kalıbı).

Yükleme YOK (P2, youtube_yukle.py + YUKLE.bat onayı). Bu araç yalnız metni kurar ve denetler; kullanıcı isterse kopyalayıp yapıştırır.
film.py görevi olarak ("<arac> <args> --film <film>"; YZ_FILM_GOREV = görev klasörü):
  python yayin_paketi.py --taslak --film <film>
        HIKAYE.json (baslik, vaat_sozlesmesi, bolum_adlari, short_adaylari, seri_kancasi) + KURGU/KURGU_PLANI.json zamanları →
        YAYIN/PAKET_TASLAK.json: başlık (kalıp "Kanca cümlesi | SERİ | Full Movie 4K <yıl>"), açıklama (bölümler dahil), bölümler,
        etiketler, yz_beyani (gerçekçi sentetik içerik: EVET), politika kontrol listesi, 3 Short ve fragman penceresi.
        yayin-paketcisi·paket bunu girdi olarak okur (başlık yazmaz, adaylardan seçer); sahte denemede PAKET.json yerine geçmez.
  python yayin_paketi.py --dogrula [--tur N] --film <film>
        YAYIN/PAKET.json → kapı YAYIN (kapsam PAKET) _RAPOR/YAYIN_PAKET_t<n>.json + YAYIN/YOUTUBE_METIN.txt (kopyala-yapıştır).
Denetim (H = HATA, B = BAYRAK):
  başlık dolu ve ≤ 100 karakter H · '<' '>' yok H · kalıba uyuyor B · HIKAYE adaylarından B (değilse vaat-denetim gerekir) · "kill" B
  açıklama dolu, ≤ 5000 kr, '<' '>' yok H · açıklama bölüm satırlarını içeriyor H · YZ beyanı satırı açıklamada B
  bölümler: ilki 00:00 H · ≥ 3 H · her biri ≥ 10 sn H · artan ve film süresi içinde H · adı dolu H · ≤ bolum_sayisi_max (8) B
  etiketler: ≥ 1 H · toplam ≤ 500 kr H · yz_beyani dolu ve "evet" H · politika kontrol listesi dolu B (eksik madde B)
  vaat sözleşmesi: her öğenin sahnesi filmde (KURGU_PLANI) H · öğe ≤ vaat_imgesi_max_sn'de ekranda B
  Shorts: 3 adet B · her biri 30–60 sn H · 2 sn kanca metni B · filme bağlantı metni B · fragman 30–60 sn B
  kapak YAYIN/kapak_*.jpg var B · final kalite (S8 / YAYIN_DOGRULAMA) HATA ise H → paket "yayına hazır değil" + nedeni
  YOUTUBE_POLITIKA.md yok ya da 90 günden eski B (bilgi)
Kodda: taslak(film) → sözlük · dogrula(film, paket) → ölçümler · aciklama_metni(paket) · zaman_metni(sn) · zaman_sn("1:02:03")
Çıkış kodları: 0 rapor/taslak yazıldı (kapı sonucu raporda) · 1 film yok · 4 ORTAM (YOLLAR.json yok) · kullanım 4.
"""
import os, re, sys, glob, json, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi

SURUM = "yayin_paketi 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
BASLIK_MAX, ACIKLAMA_MAX, ETIKET_TOPLAM_MAX = 100, 5000, 500      # YouTube alan sınırları (bellekten; YOUTUBE_POLITIKA.md'de doğrulanır)
BOLUM_MIN, BOLUM_SURE_MIN_SN = 3, 10                               # YouTube bölüm kuralları (bellekten)
SHORT_SURE = (30, 60); SHORT_ADET = 3; KANCA_SN = 2               # TASARIM §6.7 shorts_mp4
POLITIKA_GUN_MAX = 90                                              # D-40 (tahmin)
BASLIK_KALIBI = re.compile(r"^(?P<kanca>[^|]+?)\s*\|\s*(?P<seri>[^|]+?)\s*\|\s*Full Movie 4K \d{4}$")
POLITIKA_MADDELERI = ("sentetik_icerik_beyani", "ozgun_olmayan_icerik", "yaniltici_meta_veri", "kapak_yaniltmaz", "muzik_lisansi",
                      "cocuk_icerigi_degil")
VARSAYILAN_ETIKET = ("AI movie", "AI film", "full movie", "fantasy movie", "AI cinema")


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


_E = []


def esik(ad, v):
    try:
        if not _E:
            import esikler
            _E.append(esikler.yukle())
        x = _E[0][ad]
        return v if x is None else x
    except Exception: return v


def gorev_baglami(tur=None):
    g = ortak.json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV") or "", "GOREV.json"), {}) or {}
    return {"id": g.get("id"), "tur_no": int(tur or g.get("tur_no") or 1), "asama": g.get("asama") or "A17", "rapor": g.get("rapor")}


def zaman_metni(sn):
    sn = int(round(float(sn))); s, d, sa = sn % 60, (sn // 60) % 60, sn // 3600
    return f"{sa}:{d:02d}:{s:02d}" if sa else f"{d:02d}:{s:02d}"


def zaman_sn(z):
    if isinstance(z, (int, float)) and not isinstance(z, bool): return float(z)
    p = str(z or "").strip().split(":")
    if not p or not all(x.isdigit() for x in p) or len(p) > 3: return None
    t = 0.0
    for x in p: t = t * 60 + int(x)
    return t


# --- film bilgisi ---------------------------------------------------------------------------------------------------
def _oku(film, *p): return ortak.json_oku(os.path.join(film, *p))


def hikaye(film): return _oku(film, "HIKAYE.json") or {}


def kurgu(film): return _oku(film, "KURGU", "KURGU_PLANI.json") or {}


def sahne_zamanlari(kp):
    """{sahne_grubu: (bas, bit)} KURGU_PLANI planlarından."""
    z = {}
    for p in kp.get("planlar") or []:
        s = p.get("sahne_grubu") or p.get("sahne")
        if not s: continue
        b = float(p.get("cizelge_bas") or 0); e = b + float(p.get("sure") or 0)
        o = z.get(s); z[s] = (min(o[0], b), max(o[1], e)) if o else (b, e)
    return z


def film_suresi(kp):
    t = (kp.get("olcumler") or {}).get("toplam_sn")
    if isinstance(t, (int, float)) and t > 0: return float(t)
    son = [float(x.get("cizelge_bas") or 0) + float(x.get("sure") or 0) for a in ("planlar", "kartlar") for x in kp.get(a) or []]
    return max(son) if son else None


def seri_adi(film, h):
    s = h.get("evren") or (_oku(film, "HAZIRLIK.json") or {}).get("seri")
    return str(s).upper().replace("_", " ") if s else None


def baslik_adaylari(h):
    b = h.get("baslik") or {}
    if isinstance(b, str): return [b]
    return [x for x in [b.get("secilen")] + list(b.get("adaylar") or []) if isinstance(x, str) and x.strip() and x != "…"]


# --- taslak --------------------------------------------------------------------------------------------------------
def aciklama_metni(p):
    """Bölüm satırları ve YZ beyanıyla açıklama (YouTube bölümleri açıklamadaki zaman damgalarından okur)."""
    govde = (p.get("aciklama_govde") or p.get("ozet") or "").strip()
    satir = [govde, ""] if govde else []
    if p.get("bolumler"): satir += ["Chapters:"] + [f"{zaman_metni(zaman_sn(b.get('zaman')) or 0)} {b.get('ad', '')}".rstrip()
                                                   for b in p["bolumler"]] + [""]
    yz = p.get("yz_beyani") or {}
    if isinstance(yz, dict) and yz.get("metin"): satir += [yz["metin"], ""]
    if p.get("seri_satiri"): satir += [p["seri_satiri"], ""]
    return "\n".join(satir).strip() + "\n"


def bolumler_kur(h, kp):
    z = sahne_zamanlari(kp); sure = film_suresi(kp) or 0; out = []
    for b in h.get("bolum_adlari") or []:
        if not isinstance(b, dict) or not b.get("ad"): continue
        t = z.get(b.get("bas_sahne"), (None,))[0]
        if t is None: continue
        if out and t - out[-1]["_sn"] < BOLUM_SURE_MIN_SN: continue
        out.append({"_sn": t, "ad": b["ad"], "bas_sahne": b.get("bas_sahne")})
    if out: out[0]["_sn"] = 0.0
    while len(out) >= 2 and sure and sure - out[-1]["_sn"] < BOLUM_SURE_MIN_SN: out.pop()
    out = out[:int(esik("bolum_sayisi_max", 8))]
    return [{"zaman": zaman_metni(b["_sn"]), "ad": b["ad"], "bas_sahne": b["bas_sahne"]} for b in out]


def pencere(z, sahneler, sure):
    bs = [z[s] for s in sahneler if s in z]
    if not bs: return None
    bas = min(b for b, _ in bs); bit = max(e for _, e in bs)
    uz = min(max(bit - bas, SHORT_SURE[0]), SHORT_SURE[1])
    if sure: bas = max(0.0, min(bas, sure - uz))
    return round(bas, 3), round(bas + uz, 3)


def shorts_kur(h, kp, seri):
    z = sahne_zamanlari(kp); sure = film_suresi(kp); out = []
    for a in h.get("short_adaylari") or []:
        if not isinstance(a, dict): continue
        p = pencere(z, a.get("sahneler") or [], sure)
        if p: out.append({"bas": p[0], "bit": p[1], "kanca_metni": a.get("kanca_2sn"), "kaynak": "HIKAYE.short_adaylari",
                          "sahneler": a.get("sahneler")})
        if len(out) == SHORT_ADET: break
    vur = h.get("vuruslar") or {}
    for ad in ("ilk_kanca", "orta_nokta", "doruk"):
        if len(out) >= SHORT_ADET or not sure or ad not in vur: continue
        dk = float(vur[ad]) * 60; bas = max(0.0, min(dk, sure - 45))
        if all(abs(bas - s["bas"]) > 45 for s in out):
            out.append({"bas": round(bas, 3), "bit": round(bas + 45, 3), "kanca_metni": None, "kaynak": f"vuruslar.{ad}"})
    for s in out:
        s["baglanti_metni"] = f"Full movie on the channel{' — ' + seri if seri else ''}"
    return out


def fragman_kur(film, kp):
    k = sorted(glob.glob(os.path.join(film, "KESIT", "kesit_v*.mp4")), key=lambda p: int(re.findall(r"_v(\d+)", p)[-1]))
    if k: return {"kaynak": os.path.relpath(k[-1], film).replace("\\", "/"), "bas": 0.0, "bit": float(SHORT_SURE[1])}
    s = film_suresi(kp)
    return {"kaynak": "YAYIN (kesit yok)", "bas": 0.0, "bit": float(min(SHORT_SURE[1], s or SHORT_SURE[1]))}


def taslak(film):
    h, kp = hikaye(film), kurgu(film); seri = seri_adi(film, h); yil = datetime.date.today().year
    ad = baslik_adaylari(h)
    baslik = ad[0] if ad else (f"{h['logline'].split(',')[0][:50]} | {seri} | Full Movie 4K {yil}" if h.get("logline") and seri else None)
    karakter = [k.get("ad") for k in (h.get("karakterler") or {}).values() if isinstance(k, dict) and k.get("ad")] \
        if isinstance(h.get("karakterler"), dict) else []
    kk = _oku(film, "_HIKAYE_ODASI", "01_KONU_KARTI.json") or {}
    etiket = list(dict.fromkeys([x for x in [seri, kk.get("tur") and f"{kk['tur']} movie"] + list(VARSAYILAN_ETIKET) + karakter[:3] if x]))
    p = {"_surum": 1, "_uretim": {"asama": "A17", "arac_surum": SURUM, "zaman": simdi(), "sonuc": "GEC", "ortam": kapi.ortam()},
         "taslak": True, "baslik": baslik, "baslik_adaylari": ad, "ozet": h.get("logline"),
         "bolumler": bolumler_kur(h, kp), "etiketler": etiket,
         "yz_beyani": {"sentetik_icerik": True, "studio_ayari": "Altered or synthetic content: Yes",
                       "metin": "This film was created with AI-generated visuals and voices."},
         "politika_kontrol": [{"madde": x, "durum": "denetlenecek"} for x in POLITIKA_MADDELERI],
         "seri_satiri": f"{seri} — a series of AI fantasy films." if seri else None,
         "shorts": shorts_kur(h, kp, seri), "fragman": fragman_kur(film, kp),
         "vaat_sozlesmesi": h.get("vaat_sozlesmesi") or [], "dil": "en", "kategori": "Film & Animation",
         "yukleme": "kapalı (P2; yalnız YUKLE.bat onayıyla)"}
    p["aciklama"] = aciklama_metni(p)
    return p


# --- doğrulama -------------------------------------------------------------------------------------------------------
def m(madde, seviye, **k): return dict({"madde": madde, "seviye": seviye}, **{a: b for a, b in k.items() if b is not None})


def _yz_dolu(yz):
    if yz is True: return True
    if isinstance(yz, dict): return yz.get("sentetik_icerik") is True or str(yz.get("deger", "")).lower() in ("evet", "yes", "true")
    return isinstance(yz, str) and yz.strip().lower() in ("evet", "yes", "true")


def politika_dosyasi():
    try: return os.path.join(ortak.yollar()["veri_kok"], "BILGI", "YOUTUBE_POLITIKA.md")
    except ortak.YolYok: return None


def dogrula(film, p):
    h, kp = hikaye(film), kurgu(film); o = []; sure = film_suresi(kp)
    b = p.get("baslik")
    if not (isinstance(b, str) and b.strip()): o.append(m("baslik", "HATA", neden="başlık boş"))
    else:
        o.append(m("baslik_uzunluk", "GEC" if len(b) <= BASLIK_MAX else "HATA", olcu=len(b), esik=BASLIK_MAX))
        if "<" in b or ">" in b: o.append(m("baslik_karakter", "HATA", neden="YouTube '<' ve '>' kabul etmez"))
        if not BASLIK_KALIBI.match(b.strip()): o.append(m("baslik_kalibi", "BAYRAK", neden="KARARLAR.md kalıbı: 'Kanca | SERİ | Full Movie 4K <yıl>'"))
        ad = baslik_adaylari(h)
        if ad and b not in ad: o.append(m("baslik_aday", "BAYRAK", neden="HIKAYE adaylarında yok; vaat-denetim gerekir"))
        if re.search(r"\bkill", b, re.I): o.append(m("kill", "BAYRAK", neden="'kill' sözcüğü (yasak değil; seyirci/filtre riski)"))
    a = p.get("aciklama")
    if not (isinstance(a, str) and a.strip()): o.append(m("aciklama", "HATA", neden="açıklama boş"))
    else:
        o.append(m("aciklama_uzunluk", "GEC" if len(a) <= ACIKLAMA_MAX else "HATA", olcu=len(a), esik=ACIKLAMA_MAX))
        if "<" in a or ">" in a: o.append(m("aciklama_karakter", "HATA", neden="YouTube '<' ve '>' kabul etmez"))
    bl = p.get("bolumler") or []
    zs = [zaman_sn(x.get("zaman")) if isinstance(x, dict) else None for x in bl]
    if not bl: o.append(m("bolumler", "HATA", neden="bölüm yok"))
    else:
        if zs[0] != 0: o.append(m("bolum_ilk", "HATA", olcu=bl[0].get("zaman") if isinstance(bl[0], dict) else bl[0], esik="00:00"))
        if len(bl) < BOLUM_MIN: o.append(m("bolum_sayisi_min", "HATA", olcu=len(bl), esik=BOLUM_MIN))
        mx = int(esik("bolum_sayisi_max", 8))
        if len(bl) > mx: o.append(m("bolum_sayisi_max", "BAYRAK", olcu=len(bl), esik=mx))
        for i, x in enumerate(bl):
            if zs[i] is None or not (isinstance(x, dict) and str(x.get("ad") or "").strip()):
                o.append(m("bolum_bicim", "HATA", birim=i, neden="zaman ya da ad geçersiz")); continue
            son = zs[i + 1] if i + 1 < len(bl) and zs[i + 1] is not None else sure
            if i and zs[i - 1] is not None and zs[i] <= zs[i - 1]: o.append(m("bolum_sira", "HATA", birim=i, neden="zamanlar artmalı"))
            if son is not None and son - zs[i] < BOLUM_SURE_MIN_SN:
                o.append(m("bolum_sure", "HATA", birim=i, olcu=round(son - zs[i], 2), esik=BOLUM_SURE_MIN_SN))
            if sure is not None and zs[i] >= sure: o.append(m("bolum_sinir", "HATA", birim=i, neden="film süresinin dışında"))
            if isinstance(a, str) and zaman_metni(zs[i]) not in a and str(x.get("zaman")) not in a:
                o.append(m("bolum_aciklamada", "HATA", birim=i, neden="bölüm satırı açıklamada yok (YouTube bölümü açıklamadan okur)"))
    et = p.get("etiketler") or []
    if not et: o.append(m("etiketler", "HATA", neden="etiket yok"))
    else:
        top = sum(len(str(x)) for x in et) + max(0, len(et) - 1)
        o.append(m("etiket_uzunluk", "GEC" if top <= ETIKET_TOPLAM_MAX else "HATA", olcu=top, esik=ETIKET_TOPLAM_MAX))
    yz = p.get("yz_beyani")
    o.append(m("yz_beyani", "GEC" if _yz_dolu(yz) else "HATA", neden=None if _yz_dolu(yz) else "gerçekçi sentetik içerik beyanı 'evet' olmalı (D-40)"))
    if _yz_dolu(yz) and isinstance(yz, dict) and yz.get("metin") and isinstance(a, str) and yz["metin"] not in a:
        o.append(m("yz_beyani_aciklamada", "BAYRAK", neden="YZ beyanı satırı açıklamada yok"))
    pk = p.get("politika_kontrol")
    if not pk: o.append(m("politika_kontrol", "BAYRAK", neden="politika kontrol listesi yok (D-40)"))
    else:
        adlar = {x.get("madde") for x in pk if isinstance(x, dict)}
        eksik = [x for x in POLITIKA_MADDELERI if x not in adlar]
        if eksik: o.append(m("politika_eksik", "BAYRAK", kanit=eksik))
        kotu = [x.get("madde") for x in pk if isinstance(x, dict) and x.get("durum") in ("uygun_degil", "ihlal")]
        if kotu: o.append(m("politika_ihlal", "HATA", kanit=kotu))
    z = sahne_zamanlari(kp); vmax = esik("vaat_imgesi_max_sn", 120)
    for v in p.get("vaat_sozlesmesi") or h.get("vaat_sozlesmesi") or []:
        if not isinstance(v, dict) or not v.get("sahne"): continue
        if not kp: o.append(m("vaat", "OLCULEMEDI", birim=v.get("oge"), neden="KURGU_PLANI yok")); break
        if v["sahne"] not in z: o.append(m("vaat_sahnesi", "HATA", birim=v.get("oge"), neden=f"{v['sahne']} filmde yok (yanıltıcı vaat)"))
        elif z[v["sahne"]][0] > vmax: o.append(m("vaat_zamani", "BAYRAK", birim=v.get("oge"), olcu=round(z[v["sahne"]][0], 1), esik=vmax))
    sh = p.get("shorts") or []
    if len(sh) < SHORT_ADET: o.append(m("short_sayisi", "BAYRAK", olcu=len(sh), esik=SHORT_ADET))
    for i, s in enumerate(sh):
        d = (zaman_sn(s.get("bit")) or 0) - (zaman_sn(s.get("bas")) or 0)
        o.append(m("short_sure", "GEC" if SHORT_SURE[0] <= d <= SHORT_SURE[1] else "HATA", birim=f"short{i + 1}", olcu=round(d, 2),
                   esik=list(SHORT_SURE)))
        if not s.get("kanca_metni"): o.append(m("short_kanca", "BAYRAK", birim=f"short{i + 1}", neden=f"ilk {KANCA_SN} sn kanca metni yok"))
        if not s.get("baglanti_metni"): o.append(m("short_baglanti", "BAYRAK", birim=f"short{i + 1}", neden="filme bağlantı metni yok"))
    fr = p.get("fragman")
    if not fr: o.append(m("fragman", "BAYRAK", neden="fragman planı yok"))
    else:
        d = (zaman_sn(fr.get("bit")) or 0) - (zaman_sn(fr.get("bas")) or 0)
        if not SHORT_SURE[0] <= d <= SHORT_SURE[1]: o.append(m("fragman_sure", "BAYRAK", olcu=round(d, 2), esik=list(SHORT_SURE)))
    if not glob.glob(os.path.join(film, "YAYIN", "kapak_*.jpg")): o.append(m("kapak", "BAYRAK", neden="YAYIN/kapak_*.jpg yok"))
    yd = _oku(film, "YAYIN", "YAYIN_DOGRULAMA.json") or {}
    if not yd: o.append(m("final_kalite", "OLCULEMEDI", neden="YAYIN_DOGRULAMA.json yok (kalite_denetim --final)"))
    elif yd.get("sonuc") == "HATA": o.append(m("final_kalite", "HATA", neden=yd.get("hazir_degil_nedeni") or "final kalite HATA"))
    pd = politika_dosyasi()
    if not pd or not os.path.isfile(pd): o.append(m("politika_belgesi", "BAYRAK", neden="<veri>/BILGI/YOUTUBE_POLITIKA.md yok"))
    else:
        gun = (datetime.datetime.now().timestamp() - os.path.getmtime(pd)) / 86400
        if gun > POLITIKA_GUN_MAX: o.append(m("politika_belgesi", "BAYRAK", olcu=int(gun), esik=POLITIKA_GUN_MAX, neden="tazele (D-40)"))
    return o


def youtube_metni(p, hazir, neden):
    s = []
    if not hazir: s += [f"!! YAYINA HAZIR DEĞİL: {neden}", ""]
    s += ["BAŞLIK:", p.get("baslik") or "", "", "AÇIKLAMA:", p.get("aciklama") or "", "ETİKETLER:", ", ".join(map(str, p.get("etiketler") or [])),
          "", "YOUTUBE STUDIO: 'Altered or synthetic content' (Değiştirilmiş ya da sentetik içerik) sorusuna EVET işaretle.",
          "Yükleme otomatik değildir; yükleme kararı senindir."]
    return "\n".join(s) + "\n"


def paket_dogrula(film, g=None):
    g = g or gorev_baglami(); p = _oku(film, "YAYIN", "PAKET.json")
    o = dogrula(film, p) if isinstance(p, dict) else [m("paket", "HATA", neden="YAYIN/PAKET.json yok ya da bozuk")]
    hatalar = [x for x in o if x["seviye"] == "HATA"]
    hazir = not hatalar
    neden = "; ".join(x["madde"] + (f" ({x['neden']})" if x.get("neden") else "") for x in hatalar) or None
    r = kapi.rapor_kur("YAYIN", "PAKET", o, tur=g["tur_no"], asama=g["asama"], gorev=g["id"], arac_surum=SURUM, birim="madde",
                       ek={"yayina_hazir": hazir, "hazir_degil_nedeni": neden})
    h = kapi.dogrula(r)
    if h: raise kapi.RaporHatasi(h)
    yol = os.path.join(film, g["rapor"]) if g.get("rapor") else os.path.join(film, "_RAPOR", f"YAYIN_PAKET_t{g['tur_no']}.json")
    ortak.atomik_yaz(yol, r)
    if isinstance(p, dict):
        tmp = os.path.join(film, "YAYIN", "YOUTUBE_METIN.txt")
        os.makedirs(os.path.dirname(tmp), exist_ok=True)
        with open(tmp + ".tmp", "w", encoding="utf-8") as f: f.write(youtube_metni(p, hazir, neden))
        os.replace(tmp + ".tmp", tmp)
    print(f"YAYIN PAKET: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r['bayraklar'])}"
          + ("" if hazir else f" · yayına hazır değil: {neden}") + f" → {os.path.relpath(yol, film)}")
    return yol, r


def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def main(a):
    if not ({"--taslak", "--dogrula"} & set(a)): print(__doc__); return ORTAM
    try:
        f = _arg(a, "--film")
        film = (os.path.abspath(f) if f and os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)) if f else None
        if not film or not os.path.isdir(film): print("!! --film <film> gerekli (klasör yok)"); return HATA
        if "--taslak" in a:
            p = taslak(film); ortak.atomik_yaz(os.path.join(film, "YAYIN", "PAKET_TASLAK.json"), p)
            print(f"Yayın paketi taslağı: {p['baslik']!r} · {len(p['bolumler'])} bölüm · {len(p['shorts'])} Short → YAYIN/PAKET_TASLAK.json")
        if "--dogrula" in a: paket_dogrula(film, gorev_baglami(_arg(a, "--tur")))
        return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
