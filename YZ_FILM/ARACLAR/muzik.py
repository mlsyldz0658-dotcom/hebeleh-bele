"""MÜZİK — müzik planı (kâğıt) ve leitmotif MIDI'si (TASARIM §1.3 A08, §6.6, §7.2 S0, D-25; [SM2] §4.2 SA3, §4.5.9, §4.7.1, §4.8.4).
film.py görevi olarak çağrılır: "python muzik.py <alt komut> --film <film>" (YZ_FILM_GOREV = görev klasörü; tur ve görev kimliği oradan).

Alt komutlar:
  --kagit   (A08, S0.14–S0.18) MUZIK/muzik_listesi.json (ses-tasarimcisi·muzik) + SAHNELER v2 (T0 zamanı) + HIKAYE (partiler, doruk)
            + evren leitmotifleri → _RAPOR/S0_MUZIK.json (kapı S0, birim = ipucu), MUZIK/IPUCU_ZAMANLARI.json (çözülmüş giriş/çıkış,
            kapladığı planlar), MUZIK/leitmotif_adaylari.json (yeni motifler; evrene yalnız evren.py yazar), MUZIK/ZINCIR.json
            (yayın zincirinin bu ortamdaki durumu; D-25: zincir boşsa ipuçları müziksiz kalır → BAYRAK, hat durmaz).
            Ölçüler: S0.14 kaplama %40–65, müziksiz ≤ 240 sn, müzikli ≤ 300 sn (B) · S0.15 giriş/çıkış bir olaya bağlı (H), replik
            penceresi ortasında giriş (H), çıkış (B) · S0.16 ardışık iki ipucunda aynı duygu (B) · S0.17 leitmotif: ilk sunum P1'de
            'sade', doruğa kadar dönüş ≥ RE leitmotif_donus_min, doruğunda tam/zafer dönüşümü (B) · S0.18 istemde sanatçı/film adı (H),
            'no vocals' (H), motifli ipucunda notalar dolu ve geçerli (H) · zincir: 'elle' sağlayıcı yalnız son basamakta, midi_ornek
            yayında yok (H), bilinmeyen sağlayıcı (B).
  --midi    [--motif LM_X] [--donusum sade|tehdit|zafer|hepsi]   leitmotif notalarından standart MIDI (tip 0; stdlib) →
            MUZIK/motif/<LM>_<dönüşüm>.mid + MUZIK/motif/DIZIN.json (sha1, BPM, ton, nota sayısı). Animatikteki midi_ornek ve
            ACE-Step "Cover/Refer audio" girdisinin omurgasıdır; yayında General MIDI ile tema çalınmaz (D-25).
  --uret, --yerlestir                  → TASARIM §9 adım 13 (--uret) / adım 16 (--yerlestir); bu sürümde yok, çıkış 4.
  --gemini-paket, --gemini-al          → zincirin elle son basamağı; adım 13 (lisans doğrulanınca); bu sürümde yok, çıkış 4.
Ortak: --film <ad|yol> (zorunlu) · --tur N (görev klasörü yoksa)
Kodda: liste_oku(film) · kagit_olcumleri(plan, liste, hikaye, E, motifler=None) → (ölçümler, {plan_no: ipucu_id}) ·
       ipucu_zamanlari(plan, liste) · motifler(film, hikaye, liste) · midi_bayt(notalar, bpm, olcu, program) · zincir_durumu(film)
Çıkış kodları: 0 rapor/dosya yazıldı (kapı sonucu raporda) · 1 girdi yok ya da bozuk · 4 ORTAM (YOLLAR.json yok, SAHNELER v1,
               komut bu adımda yok) · kullanım hatası 4.
"""
import os, re, sys, json, hashlib, struct
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi
import istem_denetim_ses as ids

SURUM = "muzik 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
MUZIK = "MUZIK"
OLAYLAR = ("kesme", "plan_basi", "plan_sonu", "adim_basi", "adim_sonu", "bakis", "replik_sonu", "sahne_basi", "sahne_sonu")
TAM_DONUSUM = ("zafer", "tam")
VARSAYILAN_ZINCIR = ("acestep", "kutuphane")            # FILM_AYAR saglayicilar.muzik.yayin yoksa (§5.6)
BILINEN = {"acestep": False, "kutuphane": False, "elevenlabs_muzik": False, "gemini_muzik_paketi": True, "midi_ornek": False,
           "sahte": False}                               # ad → elle (fiziksel iş); §5.6
SONRAKI = {"--uret": "adım 13 (PR-9, yerel ses hazırlığı)", "--yerlestir": "adım 16 (PR-12, video sonrası ses ve kurgu)",
           "--gemini-paket": "adım 13 (zincirin elle son basamağı; lisans doğrulanınca)", "--gemini-al": "adım 13"}
NOTA = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")
YARIM = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
GM = (("flute", 73), ("piccolo", 72), ("oboe", 68), ("clarinet", 71), ("bassoon", 70), ("horn", 60), ("trumpet", 56),
      ("trombone", 57), ("tuba", 58), ("cello", 42), ("viola", 41), ("violin", 40), ("contrabass", 43), ("harp", 46),
      ("celesta", 8), ("piano", 0), ("guitar", 24), ("string", 48), ("orchestra", 48), ("pad", 89), ("drum", 47), ("timpani", 47))


def m(madde, seviye, birim=None, **k): return ids.m(madde, seviye, None, birim, **k)


def E_(): return ids.esikler_()


def e(ad, v=None):
    x = E_().get(ad) if hasattr(E_(), "get") else None
    return v if x is None else x


# --- girdiler ----------------------------------------------------------------------------------------------------------
def liste_oku(film):
    j = ortak.json_oku(os.path.join(film, MUZIK, "muzik_listesi.json"))
    return j if isinstance(j, dict) else None


def hikaye_oku(film): return ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}


def evren_motifleri(h):
    try:
        import evren
        seri = h.get("evren")
        return (ortak.json_oku(evren.seri_yolu(seri, "muzik", "leitmotifler.json"), {}) or {}) if seri else {}
    except Exception:
        return {}


def motifler(film, h, liste):
    """{LM: motif} evren + listedeki yeni (aday) motifler; aynı ad listede yeniden yazılırsa evren kaydı geçerlidir."""
    ev = {k: dict(v, _kaynak="evren") for k, v in evren_motifleri(h).items() if isinstance(v, dict)}
    yeni = {k: dict(v, _kaynak="aday") for k, v in ((liste or {}).get("leitmotifler") or {}).items() if isinstance(v, dict)}
    return dict(yeni, **ev)


def sahneler(film):
    import ses_plani
    return ses_plani.sahneler_v2(film)


# --- zaman çözümü ------------------------------------------------------------------------------------------------------
def _cizelge(plan):
    import ses_plani
    ps = ses_plani.plan_listesi(plan)
    return ps, {s.get("no"): (s, b, t) for s, b, t in ses_plani.zaman_cizelgesi(ps)}


def _grup_sinir(plan, ciz, S):
    import ses_plani
    zs = [ciz[s.get("no")] for s in ses_plani.plan_listesi(plan) if ses_plani.grup_adi(s) == S and s.get("no") in ciz]
    return (min(z[1] for z in zs), max(z[2] for z in zs)) if zs else None


def replik_penceresi_film(plan, ciz, R):
    """(bas, bit) film zamanında; replik bulunamazsa None."""
    import ses_plani
    for no, (s, b, _) in ciz.items():
        for r, rb, rs in ses_plani.replik_pencereleri(s):
            if r == R or (r is None and (s.get("replik") or {}).get("id") == R):
                return ses_plani.klip_to_film(s, b, rb), ses_plani.klip_to_film(s, b, rs)
    return None


def olay_zamani(plan, ciz, o):
    """Olay → film zamanı (sn). (zaman, hata nedeni)."""
    import ses_plani
    if not isinstance(o, dict): return None, "olay yok"
    tur = o.get("olay"); of = float(o.get("ofset_sn") or 0)
    if tur not in OLAYLAR: return None, f"bilinmeyen olay türü {tur!r}"
    if tur in ("sahne_basi", "sahne_sonu"):
        sn = _grup_sinir(plan, ciz, o.get("sahne_grubu"))
        if not sn: return None, f"sahne grubu yok: {o.get('sahne_grubu')!r}"
        return (sn[0] if tur == "sahne_basi" else sn[1]) + of, None
    if tur == "replik_sonu":
        p = replik_penceresi_film(plan, ciz, o.get("replik"))
        if not p: return None, f"replik bulunamadı: {o.get('replik')!r}"
        return p[1] + of, None
    try: no = int(o.get("plan"))
    except (TypeError, ValueError): return None, "plan numarası yok"
    if no not in ciz: return None, f"plan yok: {no}"
    s, b, t = ciz[no]
    if tur in ("kesme", "plan_basi"): return b + of, None
    if tur == "plan_sonu": return t + of, None
    a = next((x for x in ses_plani.adimlar(s) if x.get("id") == o.get("adim")), None)
    if a is None: return None, f"adım yok: plan {no} {o.get('adim')!r}"
    an = a.get("bas") if tur in ("adim_basi", "bakis") else a.get("bit")
    return min(t, ses_plani.klip_to_film(s, b, float(an or 0))) + of, None


def ipucu_zamanlari(plan, liste):
    """[{id, bas, bit, giris_hata, cikis_hata, planlar}] T0 film zamanında (giriş ofsetli, çıkış taşmalı)."""
    ps, ciz = _cizelge(plan); out = []
    for ip in (liste or {}).get("ipuclari") or []:
        if not isinstance(ip, dict): continue
        g, gh = olay_zamani(plan, ciz, ip.get("giris")); c, ch = olay_zamani(plan, ciz, ip.get("cikis"))
        if c is not None: c += float((ip.get("cikis") or {}).get("tasma_sn") or 0)
        kap = [no for no, (_, b, t) in ciz.items() if g is not None and c is not None and b < c and t > g]
        out.append({"id": ip.get("id"), "bas": None if g is None else round(g, 3), "bit": None if c is None else round(c, 3),
                    "giris_hata": gh, "cikis_hata": ch, "planlar": kap})
    return out


def _birlesim(araliklar):
    s = sorted((a, b) for a, b in araliklar if a is not None and b is not None and b > a); out = []
    for a, b in s:
        if out and a <= out[-1][1]: out[-1] = (out[-1][0], max(out[-1][1], b))
        else: out.append((a, b))
    return out


# --- S0.14–S0.18 -------------------------------------------------------------------------------------------------------
def _parti(plan, ciz, t):
    for no, (s, b, e_) in ciz.items():
        if b <= t < e_: return s.get("parti")
    return None


def _doruk_araligi(plan, ciz, h):
    import ses_plani
    hs = {x.get("id"): x for x in h.get("sahneler") or [] if isinstance(x, dict)}
    for S, g in (plan.get("sahne_gruplari") or {}).items():
        sid = ((g or {}).get("hikaye") or {}).get("sahne") or S
        if (hs.get(sid) or {}).get("vurus") == "doruk": return _grup_sinir(plan, ciz, S)
    return None


def kagit_olcumleri(plan, liste, h, E=None, motif=None):
    """(ölçümler, {plan_no: ipucu_id}). liste None ise S0.14 için 'muzik_listesi yok' HATA."""
    out = []; ips = [x for x in ((liste or {}).get("ipuclari") or []) if isinstance(x, dict)]
    if not isinstance(liste, dict):
        return [m("muzik_listesi", "HATA", oneri="MUZIK/muzik_listesi.json (ses-tasarimcisi·muzik)")], {}
    motif = motif if motif is not None else {k: v for k, v in (liste.get("leitmotifler") or {}).items() if isinstance(v, dict)}
    ps, ciz = _cizelge(plan); toplam = max([t for _, _, t in ciz.values()] or [0.0])
    zam = {z["id"]: z for z in ipucu_zamanlari(plan, liste)}
    ids_ = [ip.get("id") for ip in ips]
    for i in sorted({x for x in ids_ if ids_.count(x) > 1 and x}): out.append(m("ipucu_kimligi", "HATA", birim=i, neden="aynı kimlik iki kez"))
    pencere = []
    import ses_plani
    for no, (s, b, _) in ciz.items():
        for R, rb, rs in ses_plani.replik_pencereleri(s): pencere.append((R, ses_plani.klip_to_film(s, b, rb), ses_plani.klip_to_film(s, b, rs)))
    yasak = [x.lower() for x in e("muzik_istem_yasak_ifadeler", []) or []]
    zorunlu = (e("muzik_istem_zorunlu_ifade", "no vocals") or "no vocals").lower()
    nota_min = e("leitmotif_nota_min", 3); bpm_ar = e("muzik_bpm_aralik", [40, 200])
    for ip in ips:
        i = ip.get("id") or "?"; z = zam.get(ip.get("id")) or {}
        # S0.15
        if z.get("giris_hata"): out.append(m("S0.15", "HATA", birim=i, alt="giris_olayi", neden=z["giris_hata"], esik=list(OLAYLAR)))
        if z.get("cikis_hata"): out.append(m("S0.15", "HATA", birim=i, alt="cikis_olayi", neden=z["cikis_hata"], esik=list(OLAYLAR)))
        for R, rb, rs in pencere:
            if z.get("bas") is not None and rb + 0.05 < z["bas"] < rs - 0.05 and (ip.get("giris") or {}).get("olay") != "replik_sonu":
                out.append(m("S0.15", "HATA", birim=i, alt="replik_ortasinda_giris", olcu={"replik": R, "t": z["bas"]}, esik="replik penceresi dışı"))
            if z.get("bit") is not None and rb + 0.05 < z["bit"] - float((ip.get("cikis") or {}).get("tasma_sn") or 0) < rs - 0.05:
                out.append(m("S0.15", "BAYRAK", birim=i, alt="replik_ortasinda_cikis", olcu={"replik": R}))
        if z.get("bas") is not None and z.get("bit") is not None and z["bit"] <= z["bas"]:
            out.append(m("S0.15", "HATA", birim=i, alt="cikis_giristen_once", olcu=[z["bas"], z["bit"]]))
        # S0.18
        istem = str(ip.get("istem_en") or "")
        if not istem.strip(): out.append(m("S0.18", "HATA", birim=i, alt="istem_yok"))
        y = [x for x in yasak if x in istem.lower()]
        if y: out.append(m("S0.18", "HATA", birim=i, alt="sanatci_film_adi", olcu=y))
        if istem and zorunlu not in istem.lower(): out.append(m("S0.18", "HATA", birim=i, alt="no_vocals_yok", esik=zorunlu))
        f = ids._filtre(istem)
        if f: out.append(m("S0.18", "HATA", birim=i, alt="filtre", olcu=f))
        if ip.get("motif"):
            mo = motif.get(ip["motif"])
            if not isinstance(mo, dict): out.append(m("S0.18", "HATA", birim=i, alt="motif_yok", olcu=ip["motif"]))
            else:
                nt = mo.get("notalar") or []
                bozuk = [x for x in nt if not (isinstance(x, (list, tuple)) and len(x) == 2 and NOTA.match(str(x[0]))
                                               and isinstance(x[1], (int, float)) and x[1] > 0)]
                if len(nt) < nota_min: out.append(m("S0.18", "HATA", birim=i, alt="motif_notasiz", olcu=len(nt), esik=nota_min))
                elif bozuk: out.append(m("S0.18", "HATA", birim=i, alt="nota_bozuk", olcu=bozuk[:3]))
                if ip.get("donusum") and ip["donusum"] != "sade" and ip["donusum"] not in (mo.get("donusumler") or {}):
                    out.append(m("S0.18", "HATA", birim=i, alt="donusum_yok", olcu=ip["donusum"]))
        elif ip.get("tur") == "tema":
            out.append(m("S0.18", "HATA", birim=i, alt="temada_motif_yok", oneri="tema ipucu bir leitmotife bağlanır"))
        bpm = ip.get("bpm") or (motif.get(ip.get("motif")) or {}).get("bpm")
        if isinstance(bpm, (int, float)) and not bpm_ar[0] <= bpm <= bpm_ar[1]:
            out.append(m("muzik_bpm", "BAYRAK", birim=i, olcu=bpm, esik=bpm_ar))
        # zincir (S6.8'in kâğıttaki karşılığı)
        sg = ip.get("saglayici") or []
        if isinstance(sg, str): sg = [sg]
        for j, ad in enumerate(sg):
            if ad not in BILINEN: out.append(m("muzik_zinciri", "BAYRAK", birim=i, alt="bilinmeyen_saglayici", olcu=ad))
            elif BILINEN[ad] and j != len(sg) - 1: out.append(m("muzik_zinciri", "HATA", birim=i, alt="elle_son_basamak_degil", olcu=sg))
        if sg and sg[0] == "midi_ornek": out.append(m("muzik_zinciri", "HATA", birim=i, alt="midi_ornek_yayinda", oneri="midi_ornek yalnız animatikte"))
    # S0.14
    al = _birlesim((z.get("bas"), z.get("bit")) for z in zam.values())
    if toplam > 0:
        kap = sum(b - a for a, b in al) / toplam; ar = e("muzik_kaplama_oran", [0.40, 0.65])
        if not ar[0] <= kap <= ar[1]: out.append(m("S0.14", "BAYRAK", alt="kaplama", olcu=round(kap, 3), esik=ar))
        bos, t = [], 0.0
        for a, b in al: bos.append(a - t); t = b
        bos.append(toplam - t)
        if max(bos) > e("muziksiz_blok_max_sn", 240): out.append(m("S0.14", "BAYRAK", alt="muziksiz_blok", olcu=round(max(bos), 1), esik=e("muziksiz_blok_max_sn", 240)))
        if al and max(b - a for a, b in al) > e("muzikli_blok_max_sn", 300):
            out.append(m("S0.14", "BAYRAK", alt="muzikli_blok", olcu=round(max(b - a for a, b in al), 1), esik=e("muzikli_blok_max_sn", 300)))
    # S0.16
    sirali = sorted((ip for ip in ips if (zam.get(ip.get("id")) or {}).get("bas") is not None), key=lambda x: zam[x["id"]]["bas"])
    for a, b in zip(sirali, sirali[1:]):
        if a.get("duygu") and a.get("duygu") == b.get("duygu"):
            out.append(m("S0.16", "BAYRAK", birim=b.get("id"), olcu=[a.get("id"), b.get("id"), b.get("duygu")]))
    # S0.17
    out += _leitmotif_olcumleri(plan, ciz, h, sirali, zam, motif)
    # plan → ipucu (plan ortasını kaplayan ilk ipucu)
    eslesme = {}
    for no, (_, b, t) in ciz.items():
        orta_ = (b + t) / 2
        x = next((ip.get("id") for ip in sirali if zam[ip["id"]]["bas"] <= orta_ < (zam[ip["id"]]["bit"] or 0)), None)
        eslesme[no] = x
    return out, eslesme


def _leitmotif_olcumleri(plan, ciz, h, sirali, zam, motif):
    out = []; kahraman = {k for k, v in ((h.get("karakterler") or {}) if isinstance(h.get("karakterler"), dict) else {}).items()
                          if (v or {}).get("rol") == "kahraman"}
    if not motif: return [m("S0.17", "BAYRAK", alt="motif_yok", oneri="ana karakter için leitmotif (ses-tasarimcisi·muzik)")]
    doruk = _doruk_araligi(plan, ciz, h)
    for lm, mo in motif.items():
        kul = [ip for ip in sirali if ip.get("motif") == lm]
        if not kul:
            if mo.get("_kaynak") != "evren": out.append(m("S0.17", "BAYRAK", birim=lm, alt="kullanilmayan_motif"))
            continue
        ilk = kul[0]; t0 = zam[ilk["id"]]["bas"]
        if (ilk.get("donusum") or "sade") != "sade" or _parti(plan, ciz, t0) not in (1, "P1", "1"):
            out.append(m("S0.17", "BAYRAK", birim=lm, alt="ilk_sunum", olcu={"ipucu": ilk.get("id"), "donusum": ilk.get("donusum"),
                                                                              "parti": _parti(plan, ciz, t0)}, esik="P1, sade"))
        if not (mo.get("ana") or mo.get("karakter") in kahraman): continue
        sinir = doruk[0] if doruk else float("inf")
        donus = sum(1 for ip in kul if zam[ip["id"]]["bas"] < sinir)
        if donus < e("leitmotif_donus_min", 3):
            out.append(m("S0.17", "BAYRAK", birim=lm, alt="donus_sayisi", olcu=donus, esik=e("leitmotif_donus_min", 3)))
        if doruk and not any(doruk[0] <= zam[ip["id"]]["bas"] < doruk[1] and ip.get("donusum") in TAM_DONUSUM for ip in kul):
            out.append(m("S0.17", "BAYRAK", birim=lm, alt="doruk_tam_sunum", esik=list(TAM_DONUSUM)))
    return out


# --- D-25 zincir durumu ------------------------------------------------------------------------------------------------
def zincir_durumu(film):
    """Yayın zincirinin bu ortamdaki durumu: [{ad, durum, neden}] ve özet (bos|var|sahte)."""
    sahte = (ortak.json_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}).get("saglayici") == "sahte"
    try:
        ayar = ortak.json_oku(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {}) or {}
    except ortak.YolYok:
        ayar = {}
    z = ((ayar.get("saglayicilar") or {}).get("muzik") or {})
    adlar = list((z.get("yayin") if isinstance(z, dict) else z) or VARSAYILAN_ZINCIR)
    if sahte: adlar = ["sahte"]
    import saglayicilar
    out = []
    for ad in adlar:
        if ad not in saglayicilar.KAYIT:
            out.append({"ad": ad, "durum": "yok", "neden": "sağlayıcı bu sürümde yok (TASARIM §9 adım 13)"}); continue
        try:
            s = saglayicilar.yukle(ad)
            if "muzik" not in s.turler: out.append({"ad": ad, "durum": "yok", "neden": "müzik türü yok"}); continue
            ok, neden = s.hazir(); out.append({"ad": ad, "durum": "hazir" if ok else "hazir_degil", "neden": neden})
        except Exception as ex:
            out.append({"ad": ad, "durum": "hazir_degil", "neden": ex.__class__.__name__})
    hazir = [x["ad"] for x in out if x["durum"] == "hazir"]
    return {"zincir": out, "ozet": "sahte" if sahte and hazir else ("var" if hazir else "bos"), "hazir": hazir}


# --- MIDI (stdlib) -----------------------------------------------------------------------------------------------------
def nota_no(ad):
    r = NOTA.match(str(ad))
    if not r: raise ValueError(f"nota bozuk: {ad!r}")
    n = YARIM[r.group(1).upper()] + {"#": 1, "b": -1, "": 0}[r.group(2)]
    return max(0, min(127, 12 * (int(r.group(3)) + 1) + n))


def _vlq(n):
    b = [n & 0x7F]; n >>= 7
    while n: b.append((n & 0x7F) | 0x80); n >>= 7
    return bytes(reversed(b))


def program_no(enstruman):
    t = str(enstruman or "").lower()
    return next((p for k, p in GM if k in t), 73)


def midi_bayt(notalar, bpm=72, olcu="4/4", program=73, kaydir=0, hiz=80, ppq=480):
    """[(nota, vuruş)] → SMF tip 0 baytları (tek kanal, tempo + ölçü meta olayı)."""
    pay, payda = (int(x) for x in str(olcu or "4/4").split("/"))
    ev = bytearray()
    ev += b"\x00\xff\x51\x03" + struct.pack(">I", int(round(60_000_000 / float(bpm or 72))))[1:]
    ev += b"\x00\xff\x58\x04" + bytes([pay, max(0, payda.bit_length() - 1), 24, 8])
    ev += b"\x00" + bytes([0xC0, int(program) & 0x7F])
    for ad, sure in notalar:
        n = max(0, min(127, nota_no(ad) + int(kaydir))); d = int(round(float(sure) * ppq))
        ev += b"\x00" + bytes([0x90, n, hiz]) + _vlq(d) + bytes([0x80, n, 0])
    ev += b"\x00\xff\x2f\x00"
    return b"MThd" + struct.pack(">IHHH", 6, 0, 1, ppq) + b"MTrk" + struct.pack(">I", len(ev)) + bytes(ev)


def _ton_kok(ton):
    r = re.match(r"^\s*([A-Ga-g])([#b]?)", str(ton or ""))
    return (YARIM[r.group(1).upper()] + {"#": 1, "b": -1, "": 0}[r.group(2)]) if r else None


def donusum_parametreleri(mo, ad):
    d = dict((mo.get("donusumler") or {}).get(ad) or {}) if ad != "sade" else {}
    k0, k1 = _ton_kok(mo.get("ton")), _ton_kok(d.get("ton") or mo.get("ton"))
    kay = 0 if k0 is None or k1 is None else ((k1 - k0 + 6) % 12) - 6
    return {"bpm": d.get("bpm") or mo.get("bpm") or 72, "enstruman": d.get("enstruman") or mo.get("enstruman"),
            "ton": d.get("ton") or mo.get("ton"), "kaydir": kay, "olcu": mo.get("olcu") or "4/4"}


def midi(o):
    film = o["film"]; h = hikaye_oku(film); liste = liste_oku(film)
    mot = motifler(film, h, liste)
    if o.get("--motif"): mot = {k: v for k, v in mot.items() if k == o["--motif"]}
    if not mot: print("!! leitmotif yok (MUZIK/muzik_listesi.json leitmotifler ya da evren muzik/leitmotifler.json)"); return HATA
    hedef = os.path.join(film, MUZIK, "motif"); dizin = ortak.json_oku(os.path.join(hedef, "DIZIN.json"), {}) or {}
    yazilan = []
    for lm, mo in sorted(mot.items()):
        ds = ["sade"] + sorted(mo.get("donusumler") or {}) if (o.get("--donusum") or "hepsi") == "hepsi" else [o["--donusum"]]
        for d in dict.fromkeys(ds):
            if d != "sade" and d not in (mo.get("donusumler") or {}): print(f"!! {lm}: dönüşüm yok: {d}"); return HATA
            p = donusum_parametreleri(mo, d)
            try: b = midi_bayt(mo.get("notalar") or [], p["bpm"], p["olcu"], program_no(p["enstruman"]), p["kaydir"])
            except (ValueError, TypeError) as ex: print(f"!! {lm}: {ex}"); return HATA
            ad = f"{lm}_{d}.mid"; yol = os.path.join(hedef, ad)
            os.makedirs(hedef, exist_ok=True)
            with open(yol + ".tmp", "wb") as f: f.write(b)
            os.replace(yol + ".tmp", yol)
            dizin[ad] = {"motif": lm, "donusum": d, "bpm": p["bpm"], "ton": p["ton"], "enstruman": p["enstruman"],
                         "nota": len(mo.get("notalar") or []), "sha1": hashlib.sha1(b).hexdigest(), "kaynak": mo.get("_kaynak"),
                         "not": "omurga (animatik midi_ornek / ACE-Step referansı); yayında General MIDI tema çalınmaz (D-25)"}
            yazilan.append(ad)
    ortak.atomik_yaz(os.path.join(hedef, "DIZIN.json"), dizin)
    print(f"MIDI: {len(yazilan)} dosya → {MUZIK}/motif/ ({', '.join(yazilan)})")
    return BITTI


# --- --kagit -----------------------------------------------------------------------------------------------------------
def kagit(o):
    import ses_plani
    film = o["film"]; g = ses_plani.gorev_baglami(o.get("--tur"), "A08")
    plan, kod = ses_plani.sahneler_v2(film)
    if plan is None:
        ses_plani.rapor_yaz(film, dict(g, rapor=None), "MUZIK", [m("sahneler_yok", "HATA")], "_RAPOR/S0_MUZIK.json")
        return kod if kod == ORTAM else BITTI
    h = hikaye_oku(film); liste = liste_oku(film); mot = motifler(film, h, liste)
    olc, esl = kagit_olcumleri(plan, liste, h, E_(), mot)
    zd = zincir_durumu(film)
    if zd["ozet"] == "bos":
        olc.append(m("muzik_zinciri_bos", "BAYRAK", oneri="ipuçları müziksiz kalır (D-25); açık eksik raporuna ve izle-dinle bilgisine girer",
                     olcu=[x["ad"] for x in zd["zincir"]]))
    zarf = {"asama": g["asama"] or "A08", "gorev": g["id"], "arac_surum": SURUM, "zaman": kapi.simdi(), "ortam": kapi.ortam()}
    ortak.atomik_yaz(os.path.join(film, MUZIK, "ZINCIR.json"), dict(zd, _uretim=zarf))
    if isinstance(liste, dict):
        zam = ipucu_zamanlari(plan, liste)
        ortak.atomik_yaz(os.path.join(film, MUZIK, "IPUCU_ZAMANLARI.json"),
                         {"_uretim": zarf, "cizelge": "T0", "ipuclari": zam, "plan_ipucu": {str(k): v for k, v in esl.items()},
                          "muziksiz": zd["ozet"] == "bos"})
        aday = {k: {a: b for a, b in v.items() if a != "_kaynak"} for k, v in mot.items() if v.get("_kaynak") == "aday"}
        ortak.atomik_yaz(os.path.join(film, MUZIK, "leitmotif_adaylari.json"),
                         {"_uretim": zarf, "seri": h.get("evren"), "durum": "aday",
                          "not": "evrene yalnız evren.py yazar (A18 --film-sonu)", "leitmotifler": aday})
    birimler = [ip.get("id") for ip in ((liste or {}).get("ipuclari") or []) if isinstance(ip, dict)]
    ses_plani.rapor_yaz(film, dict(g, rapor=None), "MUZIK", olc, "_RAPOR/S0_MUZIK.json", birimler=birimler,
                        ek={"zincir": zd["ozet"], "ipucu_sayisi": len(birimler)})
    return BITTI


KOMUTLAR = {"--kagit": kagit, "--midi": midi}


def main(a):
    son = [k for k in SONRAKI if k in a]
    if son: print(f"!! muzik.py {son[0]}: TASARIM §9 {SONRAKI[son[0]]}; bu sürümde yok."); return ORTAM
    kom = [k for k in KOMUTLAR if k in a]
    if len(kom) != 1: print(__doc__); return ORTAM
    o = {}
    for k in ("--film", "--tur", "--motif", "--donusum"):
        if k in a and a.index(k) + 1 < len(a): o[k] = a[a.index(k) + 1]
    if not o.get("--film"): print("!! --film gerekli"); return ORTAM
    try:
        f = o["--film"]
        o["film"] = os.path.abspath(f) if os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)
        if not os.path.isdir(o["film"]): print(f"!! film klasörü yok: {o['film']}"); return HATA
        return KOMUTLAR[kom[0]](o)
    except ortak.YolYok as ex:
        print("!!", ex); return ORTAM
    except kapi.RaporHatasi as ex:
        print("!! rapor yazılamadı:", ex); return HATA


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
