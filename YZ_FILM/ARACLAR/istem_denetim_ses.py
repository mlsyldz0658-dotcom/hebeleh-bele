"""İSTEM DENETİM — SES EKLERİ (TASARIM §6.3 istem_denetim v2, §7.2 ISTEM/SEMA ve S0.4–S0.6; [SM2] §4.7.1, §4.5.2b).

istem_denetim.py'nin çağırdığı ayrı modül (tek satırlık bağlantı: rapor_v2 içinde `olc += istem_denetim_ses.denetle(plan, ...)`).
Aynı kural fonksiyonlarını ses_plani.py (A06s profil denetimi, A08 S0) de kullanır; kural tek yerde yazılıdır.

Kullanım (kodda):
  import istem_denetim_ses as ids
  ids.denetle(plan, ses_tarifleri={kar: tarif}, profiller={kar: profil}, E=None, ciftleri_atla=False) → [ölçüm]
      Derlenmiş SAHNELER v2 (A09) hareket istemlerinde ses kuralları:
      S0.4  konuşan planda (yol veo_donustur | veo_ham) `{ton_fiili_en}, {veo_ses_tarifi}: "` kalıbı birebir (H)
      S0.6  flow_sound kalıbı + istemin SONUNDA birebir; istemde 'No music.' tek; başka müzik sözcüğü yok (H)
      tts   ağzı görünmeyen (yol tts) ya da ekran dışı sesli planda Veo'ya replik söyletilmez (tırnaklı söz yok, H);
            kadrajda insan varsa dinleme kalıbı "listens silently, mouth closed" (B; Y35)
      S0.5  konuşan karakterin veo_ses_tarifi kuralları (H)
      ciftleri_atla=True: istem_denetim.denetle_v2'nin zaten yaptığı denetimler (flow_sound_kalibi, flow_sound_istemde_yok,
      veo_ses_tarifi_kelime, veo_ses_tarifi_birebir) tekrar yazılmaz.
  ids.tarif_denetle(tarif, profil=None, E=None, plan=None, birim=None) → [ölçüm]       S0.5
  ids.flow_sound_denetle(fs, E=None, plan=None) → [ölçüm]                               S0.6 (kalıp, ≤ 12 kelime, yasak sözcük, filtre)
  ids.profiller_oku(film) → {karakter: profil}   (_SES/SES_PROFILLERI.json; {"karakterler": {...}} ya da düz sözlük)
Komut satırı (deneme): python istem_denetim_ses.py --film <film>   ölçümleri JSON satırları olarak yazar (rapor yazmaz; 1 = HATA var)
Eşikler veri/ses_esikleri.json'dan (esikler.py); dosya okunamazsa aynı değerli yerel varsayılanlar.
"""
import os, re, sys, json
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "istem_denetim_ses 1.0"
VARSAYILAN = {
    "veo_ses_tarifi_kelime_max": 12, "flow_sound_kelime_max": 12, "veo_ses_tarifi_aksan_kelimesi": "accent",
    "veo_ses_tarifi_cinsiyet_kelimeleri": {"kadin": ["female", "woman's", "woman"], "erkek": ["male", "man's", "man"]},
    "veo_ses_tarifi_tini_kelimeleri": ["low", "deep", "high", "soft", "husky", "gravelly", "raspy", "warm", "bright", "rough",
                                       "smooth", "breathy", "clear", "thin", "rich", "gruff", "hoarse", "light", "dark", "calm"],
    "veo_ses_tarifi_yas_kelimeleri": ["old", "elderly", "young", "teen", "aged", "middle-aged", "child", "kid", "boy", "girl",
                                      "year-old", "years"],
    "flow_sound_yasak_kelimeler": ["music", "song", "singing", "vocal", "vocals", "choir", "melody", "soundtrack", "humming"],
    "veo_ses_tarifi_sira_zorunlu": True,
}
FLOW_SOUND = re.compile(r"^Sound: (.+)\. No music\.$")
DINLEME_EN = "listens silently, mouth closed"
KONUSAN_YOLLAR = ("veo_donustur", "veo_ham")
TIRNAKLI = re.compile(r"[\"“][^\"”]{2,}[\"”]")
_E = None


def esikler_(E=None):
    global _E
    if E is not None: return E
    if _E is None:
        try:
            import esikler
            _E = esikler.yukle()
        except Exception:
            _E = {}
    return _E


def e(E, ad):
    v = E.get(ad) if hasattr(E, "get") else None
    return VARSAYILAN.get(ad) if v is None else v


def kelimeler(s): return re.findall(r"[A-Za-z0-9'\-]+", s or "")
def kelime_sayisi(s): return len(kelimeler(s))


def bul(metin, liste):
    t = (metin or "").lower()
    return [k for k in liste if re.search(r"(?<![A-Za-z'\-])" + re.escape(k.lower()) + r"(?![A-Za-z'\-])", t)]


def _filtre(metin):
    try:
        import istem_denetim as idn
        return idn.bul(metin, idn.FILTRE_KELIMELERI) + idn.YAS_IFADESI.findall(metin or "")
    except Exception:
        return []


def m(madde, seviye, plan=None, birim=None, **k):
    d = {"madde": madde, "seviye": seviye}
    if plan is not None: d["plan"] = plan
    elif birim is not None: d["birim"] = birim
    d.update({a: b for a, b in k.items() if b is not None})
    return d


# --- S0.5 ------------------------------------------------------------------------------------------------------------
def tarif_denetle(tarif, profil=None, E=None, plan=None, birim=None):
    """veo_ses_tarifi: ≤ 12 kelime; perde/tını + cinsiyet + aksan öğeleri; yaş ve filtre sözcüğü yok; sıra (B)."""
    E = esikler_(E); out = []; k = lambda *a, **kw: out.append(m(*a, plan=plan, birim=birim, **kw))
    if not (isinstance(tarif, str) and tarif.strip()):
        k("S0.5", "HATA", olcu="veo_ses_tarifi yok", oneri="tını/perde + cinsiyet + aksan, ≤ 12 kelime"); return out
    n = kelime_sayisi(tarif); tavan = e(E, "veo_ses_tarifi_kelime_max")
    if n > tavan: k("S0.5", "HATA", alt="kelime", olcu=n, esik=tavan)
    cins = e(E, "veo_ses_tarifi_cinsiyet_kelimeleri") or {}
    bulunan = {c for c, ls in cins.items() if bul(tarif, ls)}
    pc = (profil or {}).get("cinsiyet")
    if not bulunan: k("S0.5", "HATA", alt="cinsiyet_yok", olcu=tarif)
    elif pc in cins and pc not in bulunan: k("S0.5", "HATA", alt="cinsiyet_uyusmuyor", olcu=sorted(bulunan), esik=pc)
    aksan = e(E, "veo_ses_tarifi_aksan_kelimesi")
    if not bul(tarif, [aksan]): k("S0.5", "HATA", alt="aksan_yok", olcu=tarif, oneri="ör. 'with a northern English accent'")
    tini = bul(tarif, e(E, "veo_ses_tarifi_tini_kelimeleri") or [])
    if not tini: k("S0.5", "HATA", alt="tini_yok", olcu=tarif)
    yas = bul(tarif, e(E, "veo_ses_tarifi_yas_kelimeleri") or [])
    if yas: k("S0.5", "HATA", alt="yas_sozcugu", olcu=yas)
    f = [x for x in _filtre(tarif) if x not in yas]
    if f: k("S0.5", "HATA", alt="filtre", olcu=f)
    if e(E, "veo_ses_tarifi_sira_zorunlu") and tini and bulunan and bul(tarif, [aksan]):
        t = tarif.lower()
        it = min(t.find(x.lower()) for x in tini)
        ic = min(t.find(x.lower()) for c in bulunan for x in cins[c] if bul(tarif, [x]))
        ia = t.find(aksan.lower())
        if not (it < ic < ia): k("S0.5", "BAYRAK", alt="sira", olcu=tarif, esik="perde/tını → cinsiyet → aksan")
    return out


# --- S0.6 ------------------------------------------------------------------------------------------------------------
def flow_sound_denetle(fs, E=None, plan=None):
    """'Sound: … No music.'; arası ≤ 12 kelime; müzik/şarkı/vokal ve filtre sözcüğü yok."""
    E = esikler_(E); out = []
    if not (isinstance(fs, str) and fs.strip()):
        return [m("S0.6", "HATA", plan, alt="yok", oneri="Sound: <en belirgin 2–3 olay>, <yatak>. No music.")]
    r = FLOW_SOUND.match(fs.strip())
    if not r: return [m("S0.6", "HATA", plan, alt="kalip", olcu=fs, esik="Sound: <…>. No music.")]
    ic = r.group(1); n = kelime_sayisi(ic); tavan = e(E, "flow_sound_kelime_max")
    if n > tavan: out.append(m("S0.6", "HATA", plan, alt="kelime", olcu=n, esik=tavan))
    y = bul(ic, e(E, "flow_sound_yasak_kelimeler") or [])
    if y: out.append(m("S0.6", "HATA", plan, alt="muzik_sozcugu", olcu=y))
    f = _filtre(ic)
    if f: out.append(m("S0.6", "HATA", plan, alt="filtre", olcu=f))
    return out


# --- profiller ve teslim ---------------------------------------------------------------------------------------------
def profiller_oku(film):
    p = ortak.json_oku(os.path.join(film, "_SES", "SES_PROFILLERI.json"), {}) or {}
    p = p.get("karakterler", p) if isinstance(p, dict) else {}
    return {k: v for k, v in p.items() if not str(k).startswith("_") and isinstance(v, dict)}


_TESLIM = None
def teslim_sozlugu():
    global _TESLIM
    if _TESLIM is None:
        _TESLIM = (ortak.json_oku(os.path.join(HERE, "veri", "plan_sozlukleri.json"), {}) or {}).get("teslim") or {}
    return _TESLIM


def ton_fiili(s):
    """Planın ton fiili: _derlenir.ton_fiili_en, yoksa teslim sözlüğünden."""
    d = (s.get("_derlenir") or {}).get("ton_fiili_en")
    if d: return d
    t = (s.get("replik") or {}).get("teslim")
    return (teslim_sozlugu().get(t) or {}).get("en") if isinstance(t, str) else None


def _yol(s): return (((s.get("zanaat") or {}).get("ses") or {}).get("diyalog") or {}).get("yol")


def _insan_kadrajda(s, yaratiklar):
    return [k.get("id") for k in (s.get("zanaat") or {}).get("kadrajdakiler") or [] if isinstance(k, dict) and k.get("id") not in yaratiklar]


# --- derlenmiş istem denetimi (A09) ----------------------------------------------------------------------------------
def denetle(plan, ses_tarifleri=None, profiller=None, E=None, ciftleri_atla=False, yaratiklar=()):
    """SAHNELER v2 (derlenmiş) → [ölçüm]. Yalnız hareket_istem'i olan planlar denetlenir."""
    E = esikler_(E); out = []
    profiller = profiller or {}
    tarifler = dict(ses_tarifleri or {})
    for kid, p in profiller.items():
        if p.get("veo_ses_tarifi"): tarifler.setdefault(kid, p["veo_ses_tarifi"])
    for kid, t in tarifler.items():
        for x in tarif_denetle(t, profiller.get(kid), E, birim=f"ses:{kid}"):     # S0.5 alt maddeleri istem_denetim'de yok
            if ciftleri_atla and x.get("alt") == "kelime": continue
            out.append(x)
    for s in plan.get("sahneler") or []:
        if not isinstance(s, dict): continue
        n = s.get("no"); hi = (s.get("hareket_istem") or "").strip()
        z = s.get("zanaat") or {}
        if not hi or not z: continue
        fs = ((z.get("ses") or {}).get("flow_sound") or "").strip()
        if not ciftleri_atla:
            out += flow_sound_denetle(fs or None, E, n)
            if fs and fs not in hi: out.append(m("S0.6", "HATA", n, alt="istemde_yok"))
        if fs and fs in hi and not hi.endswith(fs):
            out.append(m("S0.6", "HATA", n, alt="istem_sonunda_degil", oneri="Sound cümlesi hareket isteminin sonundadır"))
        if hi.count("No music.") != 1: out.append(m("S0.6", "HATA", n, alt="no_music_sayisi", olcu=hi.count("No music.")))
        govde = hi.replace("No music.", " ").replace(fs, " ") if fs else hi.replace("No music.", " ")
        ym = bul(govde, e(E, "flow_sound_yasak_kelimeler") or [])
        if ym: out.append(m("S0.6", "HATA", n, alt="istemde_muzik_sozcugu", olcu=ym))
        rep = s.get("replik") or {}; yol = _yol(s)
        if rep.get("metin") and yol in KONUSAN_YOLLAR:
            kar = rep.get("karakter"); tarif = tarifler.get(kar); ton = ton_fiili(s)
            if not tarif:
                out.append(m("S0.4", "HATA", n, alt="tarif_yok", olcu=kar, oneri="A06s ses profili (veo_ses_tarifi)"))
            elif tarif not in hi:
                if not ciftleri_atla: out.append(m("S0.4", "HATA", n, alt="tarif_birebir_degil", olcu=kar))
            elif ton and f"{ton}, {tarif}: ".lower() not in hi.lower():
                out.append(m("S0.4", "HATA", n, alt="kalip", olcu=kar, esik='{Ad} {ton_fiili_en}, {veo_ses_tarifi}: "{metin}"'))
            sm = (rep.get("veo_metin") or rep.get("metin")).strip()
            if sm and sm not in hi and not ciftleri_atla: out.append(m("S0.4", "HATA", n, alt="metin_birebir_degil", olcu=rep.get("id")))
        sessiz = (rep.get("metin") and yol == "tts") or (not rep.get("metin") and z.get("ekran_disi_ses"))
        if sessiz:
            konus = TIRNAKLI.findall(hi)
            if konus: out.append(m("S0.4", "HATA", n, alt="tts_planinda_veo_konusuyor", olcu=konus[:2],
                                   oneri="ses TTS/ekran dışından gelir; istemde söz yazılmaz"))
            if _insan_kadrajda(s, yaratiklar) and DINLEME_EN not in hi:
                out.append(m("S0.2", "BAYRAK", n, alt="dinleme_kalibi", esik=DINLEME_EN))
    return out


def main(a):
    film = a[a.index("--film") + 1] if "--film" in a and a.index("--film") + 1 < len(a) else None
    if not film: print(__doc__); return 4
    try:
        if not os.path.isdir(film): film = os.path.join(ortak.yollar()["filmler"], film)
    except ortak.YolYok as ex: print("!!", ex); return 4
    plan = ortak.json_oku(os.path.join(film, "SAHNELER.json"), {}) or {}
    out = denetle(plan, profiller=profiller_oku(film))
    for x in out: print(json.dumps(x, ensure_ascii=False))
    print(f"ÖZET | ölçüm {len(out)} | HATA {sum(x['seviye'] == 'HATA' for x in out)}")
    return 1 if any(x["seviye"] == "HATA" for x in out) else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
