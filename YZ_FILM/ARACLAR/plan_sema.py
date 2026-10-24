"""PLAN ŞEMA — plan, sahne grubu planı, harita ve SAHNELER v2 şema denetimi; sahiplik ve zarf kuralı (TASARIM §5, §5.1 kural 1 ve 5, §7.2 SEMA).

Kullanım:
  python plan_sema.py --film <film> [--planlar] [--harita] [--sahneler]   (hiçbiri verilmezse var olanların hepsi) → _RAPOR/SEMA_PLAN.json
  python plan_sema.py --dosya <yol> [--tur sahne_plan_dosyasi|harita|sahneler]   tek dosya (SubagentStop kancası: ajanın CIKTI/plan.json'u)
Kodda: denetle(veri, tur) → [ölçüm] · surum(veri) → 1|2 · SEMA (semalar/plan_v2.json)
Kurallar:
  - Şema `.claude/skills/film-yap/semalar/plan_v2.json`; `jsonschema` kuruluysa o da koşar, yoksa yerleşik doğrulayıcı (type, required,
    properties, additionalProperties, enum, const, pattern, minimum/maximum, minItems/maxItems, minLength, items, anyOf, $ref) + 'x-sozluk'
    (değer veri/ sözlüğünde olmalı: plan:<bölüm>, fiil, ifade).
  - Tek ayırt edici `_surum`: yok ya da 1 → v1 (bu şema uygulanmaz; eski kurallar); ≥ 2 → v2 ve her planda `zanaat` zorunlu.
  - Zarf: v2 SAHNELER `_surum` + `_uretim {asama, gorev, girdi_imza, arac_surum, esik_surum, sonuc, zaman, ortam}` taşır; alt çizgisiz `surum`
    HATA. Ajan çıktıları (PLANLAR, HARITA) zarfsızdır.
  - Sahiplik: `_derlenir` yalnız kod yazar. Ajan dosyasında `_derlenir` HATA; SAHNELER.json'da planın `_derlenir`'i son derlemenin imzasıyla
    (_YONETMEN/DERLENIR_IMZA.json) uyuşmuyorsa elle yazılmıştır → HATA.
  - Ek: adım bit > bas; konuşma adımında replik; fiil türü = adım türü; insanlı planda kadrajdaki yüzü görünen her karakterin dis_ifade.bas'ı
    (notr ise notr_neden) — ifade_zorunlu_insanli_plan.
Çıkış kodları: 0 GEÇ/BAYRAK · 1 HATA · 2 dosya yok · 4 kullanım.
"""
import os, sys, re, json
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "plan_sema 1.0"
SEMA_YOLU = os.path.join(po.SEMALAR, "plan_v2.json")
TURLER = {"sahne_plan_dosyasi": "#/definitions/sahne_plan_dosyasi", "harita": "#/definitions/harita", "sahneler": "#",
          "ajan_plani": "#/definitions/ajan_plani"}
_TIP = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None)}


def sema():
    s = ortak.json_oku(SEMA_YOLU)
    if not isinstance(s, dict): raise SystemExit(f"şema okunamadı: {SEMA_YOLU}")
    return s


def surum(v):
    try: return int((v or {}).get("_surum", 1) or 1) if isinstance(v, dict) else 1
    except (TypeError, ValueError): return 1


def _tip_mi(x, t):
    if t == "integer": return isinstance(x, int) and not isinstance(x, bool)
    if t == "number": return isinstance(x, (int, float)) and not isinstance(x, bool)
    return isinstance(x, _TIP[t])


def _ref(S, r):
    d = S
    for p in r.lstrip("#/").split("/"):
        if p: d = d[p]
    return d


def _sozluk_degerleri(ad):
    if ad == "fiil": return set(po.fiiller())
    if ad == "ifade": return set((po.sozluk("ifade").get("degerler") or {}))
    if ad.startswith("plan:"):
        b = po.sozluk("plan").get(ad[5:])
        return set(b) if isinstance(b, (dict, list)) else set()
    return set()


def dogrula(x, s, S, yol="$", out=None):
    """Yerleşik JSON Schema alt kümesi. [(yol, mesaj)]."""
    out = [] if out is None else out
    if "$ref" in s: return dogrula(x, _ref(S, s["$ref"]), S, yol, out)
    if "anyOf" in s:
        if not any(not dogrula(x, alt, S, yol, []) for alt in s["anyOf"]): out.append((yol, "anyOf: hiçbir seçeneğe uymuyor"))
        return out
    if "const" in s and x != s["const"]: out.append((yol, f"değer {s['const']!r} olmalı")); return out
    if "enum" in s and x not in s["enum"]: out.append((yol, f"izinli değer değil: {x!r}")); return out
    t = s.get("type")
    if t:
        ts = t if isinstance(t, list) else [t]
        if not any(_tip_mi(x, k) for k in ts): out.append((yol, f"tür {'/'.join(ts)} olmalı ({type(x).__name__})")); return out
    if isinstance(x, str):
        if "pattern" in s and not re.search(s["pattern"], x): out.append((yol, f"biçim {s['pattern']} değil: {x!r}"))
        if "minLength" in s and len(x) < s["minLength"]: out.append((yol, "çok kısa"))
        if "x-sozluk" in s and x not in _sozluk_degerleri(s["x-sozluk"]): out.append((yol, f"sözlükte yok ({s['x-sozluk']}): {x!r}"))
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        if "minimum" in s and x < s["minimum"]: out.append((yol, f"< {s['minimum']}"))
        if "maximum" in s and x > s["maximum"]: out.append((yol, f"> {s['maximum']}"))
        if "exclusiveMinimum" in s and x <= s["exclusiveMinimum"]: out.append((yol, f"≤ {s['exclusiveMinimum']}"))
    if isinstance(x, list):
        if "minItems" in s and len(x) < s["minItems"]: out.append((yol, f"en az {s['minItems']} öğe"))
        if "maxItems" in s and len(x) > s["maxItems"]: out.append((yol, f"en çok {s['maxItems']} öğe"))
        if "items" in s:
            for i, v in enumerate(x): dogrula(v, s["items"], S, f"{yol}[{i}]", out)
    if isinstance(x, dict):
        for r in s.get("required") or []:
            if r not in x: out.append((f"{yol}.{r}", "zorunlu alan yok"))
        pr = s.get("properties") or {}
        for k, v in x.items():
            if k in pr: dogrula(v, pr[k], S, f"{yol}.{k}", out)
            elif s.get("additionalProperties") is False: out.append((f"{yol}.{k}", "tanımsız alan"))
            elif isinstance(s.get("additionalProperties"), dict): dogrula(v, s["additionalProperties"], S, f"{yol}.{k}", out)
    return out


def _jsonschema(x, kok):
    try: import jsonschema
    except ImportError: return []
    S = sema(); s = dict(_ref(S, kok)) if kok != "#" else dict(S)
    s.setdefault("definitions", S["definitions"])
    try:
        v = jsonschema.Draft7Validator(s)
        return [("$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in e.absolute_path), e.message) for e in v.iter_errors(x)]
    except Exception: return []


def _derlenir_ara(x, yol="$"):
    if isinstance(x, dict):
        for k, v in x.items():
            if k == "_derlenir": yield f"{yol}._derlenir"
            else: yield from _derlenir_ara(v, f"{yol}.{k}")
    elif isinstance(x, list):
        for i, v in enumerate(x): yield from _derlenir_ara(v, f"{yol}[{i}]")


def _ek_kurallar(planlar, E):
    """Şemanın söyleyemediği plan kuralları (her plan: ajan_plani ya da sahneler_plan)."""
    olc = []; fil = po.fiiller(); ins = set(po.sozluk("plan").get("insansiz_tipler") or [])
    for i, p in enumerate(planlar):
        z = (p or {}).get("zanaat") or {}; no = p.get("no") or z.get("kod") or i
        for a in z.get("eylem_zinciri") or []:
            if not isinstance(a, dict): continue
            if isinstance(a.get("bas"), (int, float)) and isinstance(a.get("bit"), (int, float)) and a["bit"] <= a["bas"]:
                olc.append(po.m("adim_bit_bas", "HATA", no, adim=a.get("id"), olcu=[a["bas"], a["bit"]]))
            f = fil.get(a.get("fiil"))
            if f and a.get("tur") and f.get("tur") != a["tur"]:
                olc.append(po.m("fiil_turu_uymuyor", "HATA", no, adim=a.get("id"), olcu=a["tur"], esik=f.get("tur")))
            if a.get("tur") == "konusma" and not a.get("replik"): olc.append(po.m("konusma_replik_yok", "HATA", no, adim=a.get("id")))
        if E.get("ifade_zorunlu_insanli_plan", True) and z.get("plan_tipi") not in ins:
            oy = z.get("oyunculuk") or {}
            for k in z.get("kadrajdakiler") or []:
                if k.get("olcek") == "el" or k.get("yuz_acisi") in ("sirt", "gorunmez"): continue
                o = oy.get(k.get("id")) or {}
                if not ((o.get("dis_ifade") or {}).get("bas")):
                    olc.append(po.m("ifade_yok", "HATA", no, kim=k.get("id"), kural="D-22", neden="insanlı planda yüzü görünen karakterin dis_ifade.bas'ı zorunlu"))
                elif o["dis_ifade"]["bas"] == "notr" and not o.get("notr_neden"):
                    olc.append(po.m("notr_gerekcesiz", "HATA", no, kim=k.get("id"), kural="D-22"))
    return olc


def denetle(veri, tur, kok=None, dosya=""):
    """[ölçüm]. tur: sahne_plan_dosyasi | harita | sahneler | ajan_plani."""
    E = po.esik(); olc = []
    if tur == "sahneler":
        if surum(veri) < 2:
            return [po.m("v1_dosya", "GEC", None, neden="_surum yok ya da 1: v1 kuralları (istem_denetim v1) geçerli")]
        if "surum" in veri: olc.append(po.m("zarf_surum_alt_cizgisiz", "HATA", None, neden="'surum' geçersiz; '_surum' kullan"))
        for i, p in enumerate(veri.get("sahneler") or []):
            if not isinstance(p, dict) or not p.get("zanaat"):
                olc.append(po.m("zanaat_yok", "HATA", (p or {}).get("no"), neden="v2 dosyada her planda zanaat zorunlu (§5.1 kural 1)"))
    else:
        for y in _derlenir_ara(veri):
            olc.append(po.m("derlenir_ajan_yazimi", "HATA", None, dosya=dosya, yol=y, kural="§5.1 kural 5", neden="_derlenir yalnız kod yazar"))
        if isinstance(veri, dict) and ("_uretim" in veri or "surum" in veri) and tur in ("sahne_plan_dosyasi", "ajan_plani"):
            olc.append(po.m("ajan_zarf_yazdi", "BAYRAK", None, dosya=dosya, neden="ajan çıktısı zarfsızdır; betik taşırken ekler"))
    S = sema(); ref = TURLER[tur]
    hatalar = dogrula(veri, _ref(S, ref) if ref != "#" else S, S) + _jsonschema(veri, ref)
    gor = set()
    for yol, mesaj in hatalar:
        if (yol, mesaj) in gor: continue
        gor.add((yol, mesaj))
        no = None
        m = re.match(r"\$\.(?:sahneler|planlar)\[(\d+)\]", yol)
        if m:
            liste = (veri.get("sahneler") if tur == "sahneler" else veri.get("planlar")) or []
            i = int(m.group(1)); p = liste[i] if i < len(liste) else {}
            no = p.get("no") or (p.get("zanaat") or {}).get("kod")
        olc.append(po.m("sema", "HATA", no, dosya=dosya, yol=yol, neden=mesaj))
    if tur == "sahneler":
        olc += _ek_kurallar(veri.get("sahneler") or [], E)
        if kok:
            imz = (ortak.json_oku(os.path.join(kok, "_YONETMEN", "DERLENIR_IMZA.json"), {}) or {}).get("imzalar")
            if imz is not None:
                for p in veri.get("sahneler") or []:
                    if "_derlenir" in p and imz.get(str(p.get("no"))) not in (None, po.imza(p["_derlenir"])):
                        olc.append(po.m("derlenir_elle_yazim", "HATA", p.get("no"), kural="§5.1 kural 5",
                                        neden="_derlenir son derlemeden sonra elle değişmiş (yalnız kod yazar); plan_birlestir'i yeniden koştur"))
    elif tur == "sahne_plan_dosyasi":
        olc += _ek_kurallar(veri.get("planlar") or [] if isinstance(veri, dict) else [], E)
    elif tur == "ajan_plani":
        olc += _ek_kurallar([veri], E)
    return olc


def film_denetle(kok, secim):
    import glob
    olc, birim = [], []
    if "planlar" in secim:
        for y in sorted(glob.glob(os.path.join(kok, "_YONETMEN", "PLANLAR", "*.json"))):
            v = ortak.json_oku(y)
            if v is None: olc.append(po.m("json_bozuk", "HATA", None, dosya=os.path.basename(y))); continue
            olc += denetle(v, "sahne_plan_dosyasi", kok, os.path.basename(y)); birim.append(os.path.basename(y))
    if "harita" in secim:
        for y in sorted(glob.glob(os.path.join(kok, "_YONETMEN", "HARITA_P*.json"))):
            v = ortak.json_oku(y)
            if v is None: olc.append(po.m("json_bozuk", "HATA", None, dosya=os.path.basename(y))); continue
            olc += denetle(v, "harita", kok, os.path.basename(y)); birim.append(os.path.basename(y))
    if "sahneler" in secim and os.path.isfile(os.path.join(kok, "SAHNELER.json")):
        v = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
        if v is None: olc.append(po.m("json_bozuk", "HATA", None, dosya="SAHNELER.json"))
        else: olc += denetle(v, "sahneler", kok, "SAHNELER.json"); birim.append("SAHNELER.json")
    return olc, birim


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 4
    if "--dosya" in argv:
        y = po.arg_al(argv, "--dosya"); v = ortak.json_oku(y)
        if v is None: print(f"!! dosya yok ya da JSON bozuk: {y}", flush=True); return 2
        tur = po.arg_al(argv, "--tur") or ("sahneler" if surum(v) >= 2 and "sahneler" in v else "harita" if "sahne_gruplari" in v else "sahne_plan_dosyasi")
        if tur not in TURLER: print(__doc__); return 4
        olc = denetle(v, tur, None, os.path.basename(y))
        for o in olc: print(f"{o['seviye']} {o['madde']} {o.get('plan', '')} {o.get('yol', '')} {o.get('neden', '')}", flush=True)
        print(f"şema: HATA {sum(o['seviye'] == 'HATA' for o in olc)}", flush=True)
        return 1 if any(o["seviye"] == "HATA" for o in olc) else 0
    if "--film" not in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film"))
    secim = {a[2:] for a in argv if a in ("--planlar", "--harita", "--sahneler")} or {"planlar", "harita", "sahneler"}
    olc, birim = film_denetle(kok, secim)
    if not birim: print("!! denetlenecek dosya yok", flush=True); return 2
    yol, r = po.rapor_yaz(kok, "SEMA", "PLAN", [o for o in olc if o["seviye"] != "GEC"] or [po.m("sema", "GEC")],
                          asama="A07b", arac=SURUM, birimler=birim)
    po.yaz_ozet(r, "şema"); return po.cikis(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
