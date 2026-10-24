"""İSTEM DERLE — planın zanaat alanlarından Flow istemlerini derler (TASARIM §5.1 kural 3 ve 7, §6.4, D-13; A09).

Kullanım:
  python istem_derle.py --hareket --film <film> [--zaman-bicimi aralik|sira] [--yedek] [--plan <no>[,<no>…]] [--kuru]
      SAHNELER.json → her planın hareket_istem'i (ve --yedek ile hareket_istem_yedek'i); _derlenir.istem_ozeti; _RAPOR/ISTEM_DERLEME.txt
  python istem_derle.py --gorsel | --kart | --kapak | --bitis ...   → istem_derle_gorsel.py'ye yönlenir (TASARIM §9 adım 12, görsel hattı)
Kurallar:
  - gorsel_istem ve hareket_istem DERLENMİŞ alanlardır; elle yazım yalnız zanaat.istem_elle {neden} ile (film başına ≤ %5, RE
    plan_istem_elle_oran_max). istem_elle'li plan derlenmez.
  - Derleme tek yönlüdür (zanaat → istem). Eski istem son derlemenin özetiyle (_derlenir.istem_ozeti) uyuşmuyorsa elle değiştirilmiştir:
    üstüne YAZILMAZ, BAYRAK verilir ([YN2] §4.5.13 #7).
  - İstem: kamera cümlesi + (dinleyenler) + saniyeli adımlar ("0.5-1.8s: …", varsayılan aralik; Ö0-b kararıyla sira) + bitişte bekleme +
    zanaat.ses.flow_sound ("Sound: … No music."; yoksa nötr ambiyans + BAYRAK). Tek kişide öznesiz, çok kişide adlı. Konuşmada ton fiili +
    veo_ses_tarifi + replik metni kelimesi kelimesine.
  - Kelime sınırları (Y46, BAYRAK): istem ≤ plan_hareket_istem_kelime_max (75), adım cümlesi ≤ plan_adim_cumle_kelime_max (16).
    Derlenmiş istemde filtre kelimesi, yaş ifadesi, yasak sonuç fiili ya da çıplak left/right HATA'dır (Y47, Y48; istem_denetim de denetler).
  - --yedek: filtre-güvenli yedek istem (§5.1 kural 7): adımlar aynı, ses ve kimlik dışı ayrıntı kısaltılır; kamera hareketi sabitlenir.
Çıkış kodları: 0 tamam (BAYRAK olabilir) · 1 HATA (derlenen istemde yasak kelime ya da plan bulunamadı) · 2 SAHNELER yok · 4 kullanım/ortam.
"""
import os, sys, re
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po, plan_dili as pd

SURUM = "istem_derle 1.0"
ADIM12 = ("--gorsel", "--kart", "--kapak", "--bitis")
NOTR_SES = "Sound: quiet natural room tone. No music."
FILTRE = ["girl", "little", "child", "children", "kid", "kids", "baby", "toddler", "siblings", "frail", "bed", "sleep", "sleeping",
          "cheek", "chest", "trembles", "trembling"]
YAS = re.compile(r"\b\d+\s*(?:-\s*)?(?:years?|yrs?)(?:\s*-\s*|\s+)old\b|\byear-old\b|\byoung\b", re.I)
CIPLAK = re.compile(r"\b(left|right)\b", re.I)
SAHIPLI = re.compile(r"\b(?:her|his|their|its|[A-Z][a-z]+'s)\s+(?:own\s+|empty\s+)?(?:left|right)\b|\bframe (?:left|right)\b|"
                     r"\b(?:left|right)\s+(?:hand|arm|shoulder|eye|foot|leg|knee|elbow|wrist|palm|thumb|fingers?)\b", re.I)
IC_DURUM = ["realize", "realizes", "decides", "decide", "remembers", "remember", "knows", "know", "thinks", "understands", "feels", "wonders"]


def _alt_modul(ad):
    """Alt aracı yükler; alt araç içe aktarılırken stdout'u yeniden yapılandırıyorsa (StringIO altında) gerçek stdout'la yükler."""
    import importlib
    if ad in sys.modules: return sys.modules[ad]
    o = sys.stdout
    try:
        if not hasattr(o, "reconfigure"): sys.stdout = sys.__stdout__
        return importlib.import_module(ad)
    finally: sys.stdout = o


def _filtre():
    try:
        import istem_denetim
        return list(getattr(istem_denetim, "FILTRE_KELIMELERI", FILTRE))
    except Exception: return FILTRE


def yasak_bul(metin, E=None):
    """Derlenmiş istemde yasak: [(madde, bulunan)]."""
    E = E or po.esik(); t = (metin or "")
    alt = t.lower(); out = []
    def kel(liste): return [k for k in liste if re.search(r"\b" + re.escape(k) + r"\b", alt)]
    f = kel(_filtre()) + YAS.findall(t)
    if f: out.append(("istem_filtre", f))
    ys = kel(E.get("yasak_sonuc_fiilleri") or [])
    if ys: out.append(("yasak_sonuc_fiili", ys))
    ic = kel(IC_DURUM)
    if ic: out.append(("ic_durum_fiili", ic))
    temiz = SAHIPLI.sub(" ", t)
    cy = CIPLAK.findall(temiz)
    if cy: out.append(("ciplak_yon", cy))
    return out


def flow_sound(plan, sahneler):
    z = plan.get("zanaat") or {}
    fs = ((z.get("ses") or {}).get("flow_sound") if isinstance(z.get("ses"), dict) else None)
    return (fs.strip(), False) if fs else (NOTR_SES, True)


def derle_plan(plan, B, sahneler, bicim="aralik", yedek=False):
    """(istem, ölçümler)."""
    E = po.esik(); no = plan.get("no"); olc = []
    if yedek:
        p2 = dict(plan); z2 = dict(plan.get("zanaat") or {}); k2 = dict(z2.get("kamera") or {}); k2["hareket_tipi"] = "sabit"
        z2["kamera"] = k2; p2["zanaat"] = z2; plan = p2
    govde = pd.gorunur_tarif(plan, "en", B, bicim)
    fs, notr = flow_sound(plan, sahneler)
    if notr and not yedek: olc.append(po.m("flow_sound_yok", "BAYRAK", no, neden="zanaat.ses.flow_sound yok (A08); nötr ambiyans yazıldı"))
    istem = f"{govde} {fs}" if not yedek else f"{govde} Sound: soft ambient sound. No music."
    istem = re.sub(r"\s+", " ", istem).strip()
    n = pd.kelime(istem); tavan = E.get("plan_hareket_istem_kelime_max", 75)
    if n > tavan and not yedek: olc.append(po.m("hareket_istem_kelime", "BAYRAK", no, olcu=n, esik=tavan, kural="Y46"))
    at = E.get("plan_adim_cumle_kelime_max", 16)
    for aid, c, k in pd.adimlar_en(plan, B, bicim):
        if aid == "bitis": continue
        a = next((x for x in (plan.get("zanaat") or {}).get("eylem_zinciri") or [] if x.get("id") == aid), {})
        if a.get("tur") != "konusma" and k > at + 3:          # "0.5-1.8s:" öneki sayılmaz (≈ 3 kelime)
            olc.append(po.m("adim_cumle_kelime", "BAYRAK", no, adim=aid, olcu=k - 3, esik=at, kural="Y46"))
    rep = (plan.get("replik") or {}).get("metin") or ""
    temiz = istem.replace(rep, " ") if rep else istem
    for madde, bulunan in yasak_bul(temiz, E):
        olc.append(po.m(madde, "HATA", no, olcu=bulunan, kural="Y47/Y48", neden="derlenmiş istemde yasak kelime; şablon ya da sözlük düzeltilmeli"))
    return istem, olc


def derle(kok, bicim="aralik", yedek=False, nolar=None, kuru=False):
    s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
    if not isinstance(s, dict): return None, [po.m("sahneler_yok", "HATA")], []
    if int(s.get("_surum", 1) or 1) < 2:
        return None, [po.m("sahneler_v1", "HATA", neden="v1 SAHNELER: istemler elle yazılmış eski biçim; derleme yalnız v2")], []
    B = pd.baglam(kok, s)
    olc, satir, elle = [], [], 0
    hepsi = s.get("sahneler") or []
    for p in hepsi:
        no = p.get("no"); z = p.get("zanaat") or {}
        if nolar and no not in nolar: continue
        if not z: olc.append(po.m("zanaat_yok", "HATA", no)); continue
        if z.get("istem_elle"):
            elle += 1; satir.append(f"[{no}] elle (derlenmedi): {(z['istem_elle'] or {}).get('neden', '')}"); continue
        istem, o = derle_plan(p, B, s, bicim); olc += o
        dl = p.setdefault("_derlenir", {})
        eski = p.get("hareket_istem") or ""
        if eski and dl.get("istem_ozeti") and po.imza(eski) != dl["istem_ozeti"] and eski != istem:
            olc.append(po.m("istem_elle_degismis", "BAYRAK", no, neden="hareket_istem son derlemeden sonra elle değiştirilmiş; üstüne yazılmadı "
                            "(kalıcı istisna için zanaat.istem_elle)"))
            satir.append(f"[{no}] ELLE DEĞİŞMİŞ, korunuyor: {eski}"); continue
        p["hareket_istem"] = istem; dl["istem_ozeti"] = po.imza(istem)
        u = p.setdefault("uretim", {}); u["istem_bicimi"] = bicim
        satir.append(f"[{no}] {z.get('kod')} ({pd.kelime(istem)} kelime): {istem}")
        if yedek or z.get("risk_uretim") == "yuksek":
            y, oy = derle_plan(p, B, s, bicim, yedek=True)
            p["hareket_istem_yedek"] = y; satir.append(f"[{no}] yedek: {y}")
            olc += [x for x in oy if x["seviye"] == "HATA"]
    if hepsi and elle / len(hepsi) > po.esik().get("plan_istem_elle_oran_max", 0.05):
        olc.append(po.m("istem_elle_orani", "BAYRAK", None, olcu=round(elle / len(hepsi), 3), esik=po.esik().get("plan_istem_elle_oran_max")))
    if not kuru and not any(o["seviye"] == "HATA" for o in olc):
        s["_uretim"] = dict(s.get("_uretim") or {}, **{k: v for k, v in po.zarf("A09", SURUM).items() if k in ("asama", "gorev", "zaman", "arac_surum")})
        ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
        try:
            import plan_birlestir
            if os.path.isdir(os.path.join(kok, "_YONETMEN")): plan_birlestir.imza_yaz(kok, s)
        except Exception: pass
        os.makedirs(os.path.join(kok, "_RAPOR"), exist_ok=True)
        with open(os.path.join(kok, "_RAPOR", "ISTEM_DERLEME.txt"), "w", encoding="utf-8") as f:
            f.write(f"# {SURUM} · biçim {bicim}\n" + "\n".join(satir) + "\n")
    return s, olc, satir


def main(argv):
    if any(a in argv for a in ADIM12):                       # görsel hattı (adım 12): gorsel_istem, kart, kapak, bitiş
        return _alt_modul("istem_derle_gorsel").main(list(argv))
    if "--hareket" not in argv or "--film" not in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film"))
    bicim = po.arg_al(argv, "--zaman-bicimi", "aralik")
    if bicim not in ("aralik", "sira"): print(__doc__); return 4
    x = po.arg_al(argv, "--plan"); nolar = [int(n) for n in x.split(",")] if x else None
    s, olc, satir = derle(kok, bicim, "--yedek" in argv, nolar, "--kuru" in argv)
    if s is None:
        print("!! " + "; ".join(o.get("neden") or o["madde"] for o in olc), flush=True); return 2
    for o in olc: print(f"  {o['seviye']} {o['madde']} plan={o.get('plan', '-')} {o.get('olcu', '')}", flush=True)
    if "--kuru" in argv: print("\n".join(satir), flush=True)
    print(f"hareket istemi: {len(satir)} plan · HATA {sum(o['seviye'] == 'HATA' for o in olc)} · BAYRAK {sum(o['seviye'] == 'BAYRAK' for o in olc)}", flush=True)
    return 1 if any(o["seviye"] == "HATA" for o in olc) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
