"""İSTEM DENETİM — SAHNELER.json'u kredi harcamadan önce mekanik olarak denetler (kâğıt üstü kalite kapısı).

Kullanım: python istem_denetim.py <film_klasoru>
Kurallar CLAUDE_ICIN.md ve 03_DERSLER.md'den alındı:
  HATA  (hat durur) : eksik alan, aynı sahne no iki kez, tanımsız/dosyası olmayan referans, 3+ referans,
                      replik > 20 kelime ya da 8 sn'ye sığmıyor, bitis_karesi olmayan sahneye bakıyor
  UYARI (hat sürer) : video isteminde filtre riski olan kelime, "No music." yok, konuşanın sesi atanmamış,
                      klipte birden çok konuşan, risk kelimesi var ama *_yedek istem yok
Çıktı: _RAPOR/ISTEM_DENETIM.txt

v2 (TASARIM §6.3, §7.2 ISTEM; SAHNELER.json "_surum" ≥ 2 — v1 dosyası v1 kurallarıyla, v2 dosyası yalnız v2 yoluyla okunur):
  python istem_denetim.py --film <film> [--tur N]            SAHNELER v2 → _RAPOR/ISTEM_FILM.json (kapi.py zarfı; kapı ISTEM)
  python istem_denetim.py --replik "<metin>" [--sure 8]      tek replik denetimi (hikâye odası ve testler)
  Kodda: denetle_v2(plan, ne_yok=(), ogrenilen=None) → [ölçüm] · replik_denetle(metin, sure_sn=8, ne_yok=()) → [ölçüm]
  HATA: replik filtre/yaş kelimesi, NE YOK kelimesi, 8 sn'de > 16 kelime (10 sn'de > 20), yasak sonuç fiili ve iç durum fiili
        (hareket isteminde/eylem adımında), çıplak left/right (kimin sağı/solu yazılmamış), veo_ses_tarifi birebir değil ya da > 12 kelime,
        flow_sound kalıbı ("Sound: … No music."), kimlik dizesi (evren kimlik_en) birebir değil, referans > 2, klipte > 1 konuşan,
        iki el tarifli değil (eller alanı varsa iki el), görsel isteminde süren eylem fiili yok (görsel donmuş an değil),
        ifade sözlüğü dışı ifade şablonu, öğrenilen kural (KURALLAR_OGRENILEN.json "istem" türü, aktif).
  BAYRAK: hareket istemi > plan_hareket_istem_kelime_max (75), elle istem oranı > plan_istem_elle_oran_max (0,05).
  rapor_v2 = denetle_v2 + istem_denetim_ses (ayikla + S0.4–S0.6 ses ekleri; tek ISTEM kapısı). denetle_v2'de replik tırnağı içindeki söz
  iç durum / sonuç fiili sayılmaz; veo_ses_tarifi ve replik birebir şartı yalnız zanaat.ses.diyalog.yol veo_donustur|veo_ham planında.
  v1 davranışı değişmez: denetle()/rapor() v1 içindir ve v2 dosyasında 4 ile çıkar (ortak.sahneler_oku).
"""
import os, sys, re, json
import ortak   # SAHNELER.json v2 koruması
try: import kapi   # yalnız v2 raporu için
except Exception: kapi = None
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Video istemlerinde küçükler filtresine takılan kelimeler (03_DERSLER.md)
FILTRE_KELIMELERI = ["girl", "little", "child", "children", "kid", "kids", "baby", "toddler", "siblings", "frail",
                     "bed", "sleep", "sleeping", "cheek", "chest", "trembles", "trembling"]
YAS_IFADESI = re.compile(r"\b\d+\s*(?:-\s*)?(?:years?|yrs?)(?:\s*-\s*|\s+)old\b|\byear-old\b|\byoung\b", re.I)
# Şiddet/kan sahnelerinde yedek istem şart (CLAUDE_ICIN.md kural 4)
RISK_KELIMELERI = ["blood", "bloody", "corpse", "dead body", "kill", "killed", "stab", "gore", "wound"]
KONUSMA = re.compile(r"\b([A-Z][a-z]+)\b[^.\"]{0,40}?\b(?:says|whispers|shouts|asks|replies|yells|murmurs)\s*:", re.S)
KELIME_SN = 2.5        # İngilizce konuşma ≈ 2,5 kelime/sn
REPLIK_SN, REPLIK_KELIME, REF_EN_COK = 8.0, 20, 2


def kelimeler(s): return re.findall(r"[A-Za-z0-9']+", s or "")
def bul(metin, liste):
    t = (metin or "").lower()
    return [k for k in liste if re.search(r"\b" + re.escape(k) + r"\b", t)]


def denetle(plan, kok=None):
    """[(seviye, sahne_no|None, mesaj)] döner. seviye: HATA / UYARI."""
    out = []
    def h(n, m): out.append(("HATA", n, m))
    def u(n, m): out.append(("UYARI", n, m))
    kar = plan.get("karakterler") or {}
    for ad, k in kar.items():
        if kok and k.get("ref") and not os.path.exists(os.path.join(kok, k["ref"])):
            h(None, f"karakter '{ad}' referans dosyası yok: {k['ref']}")
    sahneler = plan.get("sahneler") or []
    if not sahneler: h(None, "sahne yok")
    nolar = [s.get("no") for s in sahneler]
    for n in sorted({x for x in nolar if nolar.count(x) > 1}): h(n, "aynı sahne numarası birden çok kez var")
    for s in sahneler:
        n = s.get("no")
        for alan in ("no", "parti", "gorsel_istem", "hareket_istem"):
            if not s.get(alan): h(n, f"'{alan}' boş")
        refs = s.get("referans") or []
        for r in refs:
            if r not in kar: h(n, f"referans '{r}' karakterler listesinde yok")
        if len(refs) > REF_EN_COK: h(n, f"{len(refs)} referans var; en çok {REF_EN_COK} (Flow yüzleri karıştırır)")
        if s.get("bitis_karesi") is not None and s["bitis_karesi"] not in nolar:
            h(n, f"bitis_karesi {s['bitis_karesi']} diye bir sahne yok")
        hi = s.get("hareket_istem") or ""
        if s.get("motor", "flow") == "flow":
            f = bul(hi, FILTRE_KELIMELERI) + YAS_IFADESI.findall(hi)
            if f: u(n, f"video isteminde filtre riski: {', '.join(f)} (eller/makro/'blanket-wrapped figure' gibi dolaylı anlat)")
        if hi and "no music" not in hi.lower(): u(n, "hareket isteminde \"No music.\" yok (müzik ayrı katmanda)")
        risk = bul(hi + " " + (s.get("gorsel_istem") or ""), RISK_KELIMELERI)
        if risk and not (s.get("hareket_istem_yedek") or s.get("gorsel_istem_yedek")):
            u(n, f"riskli kelime ({', '.join(risk)}) var ama *_yedek istem yok")
        konusanlar = {m.lower() for m in KONUSMA.findall(hi)}
        if len(konusanlar) > 1: u(n, f"klipte birden çok konuşan: {', '.join(sorted(konusanlar))} (her klipte tek kişi)")
        rep = s.get("replik")
        if rep:
            w = len(kelimeler(rep.get("metin")))
            if rep.get("karakter") not in kar: h(n, f"replik karakteri '{rep.get('karakter')}' tanımsız")
            elif not kar[rep["karakter"]].get("ses"): u(n, f"'{rep['karakter']}' için ses (voice_id) atanmamış; Flow sesi kalır")
            if w > REPLIK_KELIME: h(n, f"replik {w} kelime; en çok {REPLIK_KELIME}")
            elif w / KELIME_SN > REPLIK_SN: h(n, f"replik ≈{w / KELIME_SN:.1f} sn; 8 sn'lik klibe sığmaz")
    return out


def rapor(kok):
    kok = os.path.abspath(kok)
    plan = ortak.sahneler_oku(kok, "istem_denetim.py")
    bulgular = denetle(plan, kok)
    os.makedirs(os.path.join(kok, "_RAPOR"), exist_ok=True)
    satirlar = [f"{sv:5} {'S%03d' % n if n is not None else 'GENEL'}  {m}" for sv, n, m in bulgular]
    hata = sum(1 for b in bulgular if b[0] == "HATA")
    ozet = f"ÖZET | HATA: {hata} | UYARI: {len(bulgular) - hata} | SAHNE: {len(plan.get('sahneler') or [])}"
    open(os.path.join(kok, "_RAPOR", "ISTEM_DENETIM.txt"), "w", encoding="utf-8").write("\n".join(satirlar + ["", ozet]) + "\n")
    return bulgular, ozet



# ======================================================================================================== v2 ===
SURUM_V2 = "istem_denetim 2.0"
IC_DURUM_FIILLERI = ["realize", "realizes", "realized", "decide", "decides", "decided", "remember", "remembers", "remembered",
                     "know", "knows", "knew", "think", "thinks", "thought", "understand", "understands", "understood", "feel",
                     "feels", "felt", "wonder", "wonders", "notice", "notices", "recall", "recalls"]
CIPLAK_YON = re.compile(r"\b(?:to the |on the |at the |in the )?(left|right)\b(?!\s*(?:hand|arm|eye|eyebrow|shoulder|side of her|side of his|"
                        r"foot|leg|cheek|ear|knee|wrist|elbow|palm|fingers?))", re.I)
YON_SAHIBI = re.compile(r"\b(?:her|his|their|its|[A-Z][a-z]+'s)\s+(?:own\s+)?(?:LEFT|RIGHT|left|right)\b|\bframe[- ](?:left|right)\b|"
                        r"\b(?:enters|exits|leaves) frame (?:left|right)\b", re.I)
SUREN_EYLEM = re.compile(r"\b\w+ing\b|\bmid-\w+", re.I)
FLOW_SOUND = re.compile(r"^Sound: .+\. No music\.$")
TIRNAK_ICI = re.compile(r"[\"“][^\"”]*[\"”]")          # replik tırnağı: söz eylem değildir (iç durum / sonuç fiili sayılmaz)
KONUSAN_YOLLAR = ("veo_donustur", "veo_ham")            # Veo'nun konuştuğu diyalog yolları (zanaat.ses.diyalog.yol)


def _esikler():
    try:
        import esikler
        return esikler.yukle()
    except Exception:
        return {}


def _e(E, ad, v): return E.get(ad, v) if hasattr(E, "get") else v


def _m(madde, seviye, plan=None, **k):
    d = {"madde": madde, "seviye": seviye}
    if plan is not None: d["plan"] = plan
    d.update({a: b for a, b in k.items() if b is not None})
    return d


def kelime_sayisi(s): return len(kelimeler(s))


def replik_denetle(metin, sure_sn=8, ne_yok=(), plan=None, E=None):
    """Tek replik: filtre, yaş, NE YOK, kelime sınırı. [ölçüm] (seviye HATA)."""
    E = E if E is not None else _esikler(); out = []
    f = bul(metin, FILTRE_KELIMELERI) + YAS_IFADESI.findall(metin or "")
    if f: out.append(_m("replik_filtre", "HATA", plan, olcu=f, oneri="dolaylı anlat (ör. 'Rest now', 'the iron box')"))
    n = bul(metin, list(ne_yok))
    if n: out.append(_m("replik_ne_yok", "HATA", plan, olcu=n))
    w = kelime_sayisi(metin)
    tavan = _e(E, "replik_max_kelime_8sn", 16) if (sure_sn or 8) <= 8 else _e(E, "replik_max_kelime", 20)
    if w > tavan: out.append(_m("replik_kelime", "HATA", plan, olcu=w, esik=tavan, oneri="böl ya da ekran dışına taşı"))
    return out


def _metin(x):
    if isinstance(x, str): return x
    if isinstance(x, dict): return x.get("metin") or ""
    return ""


def _eylem_metni(z):
    return " ".join(str(a.get("fiil_en") or a.get("tarif_en") or a.get("fiil") or "").replace("_", " ")
                    for a in (z.get("eylem_zinciri") or []) if isinstance(a, dict))


def _diyalog_yolu(z):
    ses = z.get("ses") if isinstance(z.get("ses"), dict) else {}
    d = ses.get("diyalog") if isinstance(ses.get("diyalog"), dict) else {}
    return d.get("yol")


def denetle_v2(plan, ne_yok=(), ogrenilen=None, kimlikler=None, ses_tarifleri=None, ifade_sozlugu=None, E=None):
    """SAHNELER v2 → [ölçüm]. kimlikler: {karakter: kimlik_en} (evren), ses_tarifleri: {karakter: veo_ses_tarifi}."""
    E = E if E is not None else _esikler(); out = []
    kimlikler = kimlikler or {}; ses_tarifleri = ses_tarifleri or {}
    yasak_sonuc = list(_e(E, "yasak_sonuc_fiilleri", []))
    ref_max = _e(E, "referans_max", REF_EN_COK); konusan_max = _e(E, "konusan_karede_max", 1)
    hi_max = _e(E, "plan_hareket_istem_kelime_max", 75); elle_max = _e(E, "plan_istem_elle_oran_max", 0.05)
    kurallar = [k for k in (ogrenilen or {}).get("kurallar", []) if k.get("durum") == "aktif" and k.get("tur") == "istem"]
    sahneler = plan.get("sahneler") or []
    if not sahneler: out.append(_m("sahne_yok", "HATA"))
    elle = 0
    for s in sahneler:
        n = s.get("no"); z = s.get("zanaat") or {}
        hi = s.get("hareket_istem") or ""; gi = s.get("gorsel_istem") or ""
        if not z: out.append(_m("zanaat_yok", "HATA", n, neden="v2 planda zanaat zorunlu (§5.1 kural 1)"))
        if z.get("istem_elle"): elle += 1
        rep = s.get("replik") or {}
        if rep.get("metin"):
            out += replik_denetle(rep["metin"], (s.get("uretim") or {}).get("klip_sn") or z.get("klip_sn") or 8, ne_yok, n, E)
        refs = s.get("referans") or []
        if len(refs) > ref_max: out.append(_m("referans", "HATA", n, olcu=len(refs), esik=ref_max))
        konusan = [k.get("id") for k in z.get("kadrajdakiler") or [] if k.get("konusur")]
        if len(konusan) > konusan_max: out.append(_m("konusan_karede", "HATA", n, olcu=konusan, esik=konusan_max))
        eylem = TIRNAK_ICI.sub(" ", hi) + " " + _eylem_metni(z)
        ys = bul(eylem, yasak_sonuc)
        if ys: out.append(_m("yasak_sonuc_fiili", "HATA", n, olcu=ys, oneri="eylemi fiziksel adımlarla yaz (ör. 'closes her fingers around')"))
        ic = bul(eylem, IC_DURUM_FIILLERI)
        if ic: out.append(_m("ic_durum_fiili", "HATA", n, olcu=ic, oneri="iç durumu gözlenebilir işaretle yaz"))
        for metin, ad in ((hi, "hareket_istem"), (gi, "gorsel_istem")):
            temiz = YON_SAHIBI.sub(" ", metin)
            cy = [m.group(0) for m in CIPLAK_YON.finditer(temiz)]
            if cy: out.append(_m("ciplak_yon", "HATA", n, olcu=cy, alan=ad, oneri="'her LEFT hand' gibi kimin sağı/solu olduğunu yaz"))
        f = bul(hi + " " + gi, FILTRE_KELIMELERI) + YAS_IFADESI.findall(hi + " " + gi)
        if f: out.append(_m("istem_filtre", "HATA", n, olcu=f))
        ny = bul(hi + " " + gi, list(ne_yok))
        if ny: out.append(_m("istem_ne_yok", "HATA", n, olcu=ny))
        if hi and kelime_sayisi(hi) > hi_max: out.append(_m("hareket_istem_kelime", "BAYRAK", n, olcu=kelime_sayisi(hi), esik=hi_max))
        fs = (z.get("ses") or {}).get("flow_sound")
        if fs is not None and not FLOW_SOUND.match(fs.strip()):
            out.append(_m("flow_sound_kalibi", "HATA", n, olcu=fs, esik="Sound: <…>. No music."))
        if fs and hi and fs.strip() not in hi: out.append(_m("flow_sound_istemde_yok", "HATA", n))
        if rep.get("metin") and hi:
            kar = rep.get("karakter"); tarif = ses_tarifleri.get(kar)
            veo_konusur = _diyalog_yolu(z) in KONUSAN_YOLLAR      # tts / ekran dışı planda Veo konuşmaz → birebir şartı yok
            if tarif:
                if kelime_sayisi(tarif) > 12: out.append(_m("veo_ses_tarifi_kelime", "HATA", n, olcu=kelime_sayisi(tarif), esik=12))
                if veo_konusur and tarif not in hi: out.append(_m("veo_ses_tarifi_birebir", "HATA", n, olcu=kar))
            if veo_konusur and rep["metin"] not in hi: out.append(_m("replik_istemde_birebir_degil", "HATA", n, olcu=rep.get("id")))
        for kar in refs:
            kim = kimlikler.get(kar)
            if kim and gi and kim not in gi: out.append(_m("kimlik_dizesi_birebir", "HATA", n, olcu=kar))
        dl = s.get("_derlenir") or {}
        for kar, el in (dl.get("acik_parmak") or {}).items():
            if not (isinstance(el, dict) and "sag" in el and "sol" in el):
                out.append(_m("iki_el_tarifli", "HATA", n, olcu=kar))
        for k in z.get("kadrajdakiler") or []:
            eller = (k.get("eller") if isinstance(k, dict) else None)
            if eller is not None and not (isinstance(eller, dict) and "sag" in eller and "sol" in eller):
                out.append(_m("iki_el_tarifli", "HATA", n, olcu=k.get("id")))
        if gi and z.get("plan_tipi") not in ("kurulus", "manzara", "ekleme_nesne") and not SUREN_EYLEM.search(gi):
            out.append(_m("gorselde_suren_eylem_yok", "HATA", n, oneri="görsel istemine süren bir eylem yaz (ör. 'mid-step', 'turning')"))
        if ifade_sozlugu is not None:
            for kid, o in (z.get("oyunculuk") or {}).items():
                for uc in ("bas", "bit"):
                    v = ((o or {}).get("dis_ifade") or {}).get(uc)
                    if v and v not in ifade_sozlugu: out.append(_m("ifade_sozlugu", "HATA", n, olcu=f"{kid}.{uc}={v}"))
        for k in kurallar:
            desen = k.get("desen")
            try:
                if desen and re.search(desen, hi + "\n" + gi, re.I): out.append(_m("ogrenilen_kural", "HATA", n, olcu=k.get("id")))
            except re.error: pass
    if sahneler and elle / len(sahneler) > elle_max:
        out.append(_m("istem_elle_orani", "BAYRAK", None, olcu=round(elle / len(sahneler), 3), esik=elle_max))
    return out


def _evren_bilgisi(kok):
    try:
        import evren
        return evren.ne_yok_kelimeleri(film=kok)
    except Exception:
        return []


def rapor_v2(kok, tur=1, gorev=None, rapor_yolu=None):
    """SAHNELER v2 → _RAPOR/ISTEM_FILM.json. (rapor, yol)."""
    kok = os.path.abspath(kok)
    plan = ortak.json_oku(os.path.join(kok, "SAHNELER.json")); surum = SURUM_V2
    if not isinstance(plan, dict): olc = [_m("sahneler_yok", "HATA")]; plan = {}
    elif int(plan.get("_surum", 1) or 1) < 2: olc = [_m("sahneler_v1", "HATA", neden="v1 dosyası: python istem_denetim.py <film> (v1)")]
    else:
        import istem_denetim_ses as ids                     # ses ekleri (S0.4–S0.6, §7.2 ISTEM): kural tek yerde, orada
        prof = ids.profiller_oku(kok)
        ses = {kid: p["veo_ses_tarifi"] for kid, p in prof.items() if p.get("veo_ses_tarifi")}
        ogr = None
        try: ogr = ortak.json_oku(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "KURALLAR_OGRENILEN.json"))
        except ortak.YolYok: pass
        h = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
        kar = h.get("karakterler") if isinstance(h.get("karakterler"), dict) else {}
        yar = {k for k, v in kar.items() if isinstance(v, dict) and (v.get("rol") == "yaratik" or v.get("konusmaz"))}
        olc = ids.ayikla(denetle_v2(plan, _evren_bilgisi(kok), ogr, ses_tarifleri=ses), plan)
        olc += ids.denetle(plan, profiller=prof, ciftleri_atla=True, yaratiklar=yar)
        surum = f"{SURUM_V2} + {ids.SURUM}"
    birimler = [s.get("no") for s in plan.get("sahneler") or [] if s.get("no") is not None]
    r = kapi.rapor_kur("ISTEM", "FILM", olc, tur=tur, asama="A09", gorev=gorev, arac_surum=surum, birimler=birimler)
    yol = rapor_yolu or os.path.join(kok, "_RAPOR", "ISTEM_FILM.json")
    h = kapi.dogrula(r)
    if h: raise kapi.RaporHatasi(h)
    ortak.atomik_yaz(yol, r)
    return r, yol


def _v2_main(a):
    def arg(ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v
    if "--replik" in a:
        b = replik_denetle(arg("--replik", ""), float(arg("--sure", 8)))
        for x in b: print(json.dumps(x, ensure_ascii=False))
        return 1 if b else 0
    film = arg("--film")
    if film and not os.path.isdir(film):
        try: film = os.path.join(ortak.yollar()["filmler"], film)
        except ortak.YolYok as e: print("!!", e); return 4
    g = ortak.json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV", ""), "GOREV.json"), {}) or {}
    r, yol = rapor_v2(film, int(arg("--tur", g.get("tur_no") or 1)), g.get("id"), os.path.join(film, g["rapor"]) if g.get("rapor") else None)
    print(f"ISTEM: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r['bayraklar'])} → {yol}")
    return 0


if __name__ == "__main__":
    if "--film" in sys.argv or "--replik" in sys.argv: sys.exit(_v2_main(sys.argv[1:]))
    if len(sys.argv) < 2: print(__doc__); sys.exit(0)
    b, ozet = rapor(sys.argv[1])
    for sv, n, m in b: print(f"{sv:5} {'S%03d' % n if n is not None else 'GENEL'}  {m}")
    print(ozet); sys.exit(1 if any(x[0] == "HATA" for x in b) else 0)
