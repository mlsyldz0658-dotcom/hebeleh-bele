"""DÜZELTME — şablonlu CORRECTION cümleleri, tek seferlik küçük düzeltmeler ve düzeltme turu kaydı (TASARIM §6.5, D-16, [GS2] §4.5.8, GS9).

Kullanım:
  python duzeltme.py --cumle <alan> [k=v ...]                 şablondan tek cümle (ör. nesne_el nesne="the lit lantern" ad=Mara EL=RIGHT ...)
  python duzeltme.py --kuyruk --film <film> [--kuru]          KUYRUK/YENIDEN_URET.json'daki açık G1/kart görsel maddelerini işler:
        küçük düzeltme bir kez (ayna yalnız _derlenir.ayna_yasak = false; kenar kırpma ≤ %10; renk eşleme), olmazsa şablonlu CORRECTION'ı
        planın _derlenir.duzeltmeler'ine yazar (aynı alan için cümle DEĞİŞTİRİLİR, eklenmez) ve gorsel_istem'i yeniden kurar; tur sayacı;
        g1_duzeltme_tur_max (2) dolunca kaçış kaydı (sureklilik-denetcisi·kacis → yonetmen·onarim).
  Kodda: import duzeltme
    duzeltme.cumle("nesne_el", nesne="the lit lantern", ad="Mara", EL="RIGHT", iyelik="her", OBUR_EL="LEFT", el_sekli_en="empty, ...")
    duzeltme.istem_kur(taban, duzeltmeler) → istem · duzeltme.sifir_kredi(film, plan, aday, alan) → {denendi, basamaklar, gerekce, yeni_aday?}
Çıktı: _RAPOR/DUZELTME_KAYDI.jsonl, _RAPOR/ISARET/<NNN>.json (uygulanan küçük düzeltmeler; ikinci kez uygulanmaz), yeni aday
  SIRALI_GORSEL/_ADAYLAR/<NNN>_<aday><n>.jpg (ayna/kırpma/renk; G1'den yeniden geçer).
Kurallar: çıplak left/right yazılmaz (her zaman "<ad>'s RIGHT hand" ya da "frame left"); düzeltme görselleri kullanıcıya paket olarak
  gitmez (gorsel_duzeltme zinciri: vertex_gorsel izinle → flow_gorsel; D-16, İ-13). Ses şablonları aynı dosyada (SES bölümü).
Çıkış kodları: 0 tamam · 1 HATA (bilinmeyen alan, eksik değer) · 2 film/kuyruk yok · 4 kullanım.
"""
import os, sys, re, json, shutil, hashlib, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "duzeltme 1.0"
GORUNTU = {
    "fazla_kisi": "CORRECTION: exactly {n} {insan} in frame: {adlar}. No other people, faces or figures anywhere, including the background.",
    "yanlis_kisi": "CORRECTION: the person in the {ucte_bir} is {ad} — {kimlik_en}.",
    "kimlik": "CORRECTION: the person in the {ucte_bir} is {ad} — {kimlik_en}.",
    "nesne_el": "CORRECTION: the {nesne} is in {ad}'s {EL} hand; {iyelik} {OBUR_EL} hand is {el_sekli_en}.",
    "bakis": "CORRECTION: {ad} faces toward frame {yon}, eyes on the {hedef}.",
    "isik": "CORRECTION: the only light source is the {kaynak} on frame {yon}; no fire, no candles, no other glow.",
    "yasak_oge": "CORRECTION: remove {oge}; there is no {oge} in this scene.",
    "kostum": "CORRECTION: {ad} wears {kostum_tarif_en}.",
    "olcek": "CORRECTION: {yaratik} is the size of {benzetme}, reaching {ad}'s {vucut_noktasi}.",
    "stil": "CORRECTION: photorealistic film still, real photography, NOT illustration, NOT 3D render, NOT plush.",
    "mekan": "CORRECTION: the {oge} is on the {kadraj_yeri} of the frame, as in the location reference.",
    "agiz": "CORRECTION: {ad}'s mouth is closed, lips together.",
    "ifade": "CORRECTION: {ad} has {ifade_en}.",
    "kadraj_sirasi": "CORRECTION: from frame left to frame right: {sira}.",
    "yazi_logo": "CORRECTION: no text, no letters, no logo, no watermark anywhere in the image.",
    "anatomi": "CORRECTION: natural human anatomy: five fingers on each hand, two arms, an undistorted face.",
}
SES = {
    "veo_konusmadi": "CORRECTION: {Ad} speaks the line aloud, lips moving clearly: \"{metin}\"",
    "veo_metin_sapti": "CORRECTION: {Ad} says the line exactly, word for word: \"{metin}\"",
    "ad_yanlis_okundu": "CORRECTION: say the name exactly as \"{okunus_yazimi}\".",
    "yanlis_kisi_konustu": "CORRECTION: only {Ad} speaks; {Diger} listens silently, mouth closed.",
    "dinleyen_konustu": "CORRECTION: only {Ad} speaks; {Diger} listens silently, mouth closed.",
    "aksan_kaydi": "CORRECTION: {Ad} speaks {veo_ses_tarifi}.",
}
SABLONLAR = dict(GORUNTU, **{"ses:" + k: v for k, v in SES.items()})
# G1/KART alanı → kuyruk kök nedeni (veri/kok_neden.json)
KOK_NEDEN = {"nesne_el": "ters_el", "fazla_kisi": "fazla_kisi", "yanlis_kisi": "yanlis_kisi", "kimlik": "yuz_degisti",
             "kimlik_fark_payi": "yuz_degisti", "kadraj_sirasi": "yanlis_kisi", "ucte_bir": "yanlis_kisi", "bakis": "bakis",
             "isik": "isik_zipladi", "lab": "isik_zipladi", "yasak_oge": "yasak_oge", "ne_yok": "yasak_oge", "yazi_logo": "yasak_oge",
             "kostum": "kostum_ziplama", "olcek": "olcek", "stil": "stil", "mekan": "mekan_belirsiz", "agiz": "dinleyen_konustu",
             "anatomi": "morf", "eksik_yuz": "karakter_kayboldu", "teknik": "gorsel_teknik", "yaratik": "yuz_degisti", "plaka_oge": "plaka_oge",
             "ayrisma_kilitli": "yuz_degisti", "kadro_benzer": "yuz_degisti", "gorunen": "karakter_kayboldu"}
AYNA_ALANLARI = ("kadraj_sirasi", "bakis", "ucte_bir")
KIRPMA_ALANLARI = ("yasak_oge", "yazi_logo", "fazla_kisi")
RENK_ALANLARI = ("lab", "isik")
YON_EN = {"sol": "left", "sag": "right", "soldan": "left", "sagdan": "right", "kadraj_soluna": "left", "kadraj_sagina": "right"}
EL_EN = {"sag": "RIGHT", "sol": "LEFT"}


class DuzeltmeHatasi(Exception):
    pass


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def cumle(alan, **d):
    s = SABLONLAR.get(alan)
    if s is None: raise DuzeltmeHatasi(f"bilinmeyen alan: {alan!r} ({', '.join(SABLONLAR)})")
    try: c = s.format(**d)
    except KeyError as e: raise DuzeltmeHatasi(f"{alan}: şablon değeri eksik: {e.args[0]}")
    import istem_derle
    yas = [y for y in istem_derle.yasak_bul(c) if y[0] in ("istem_filtre", "ciplak_yon")]
    if yas: raise DuzeltmeHatasi(f"{alan}: cümlede yasak ifade {yas}")
    return c


def istem_kur(taban, duzeltmeler):
    """Taban istemden eski CORRECTION cümlelerini atar, alan başına tek cümleyi sona ekler (istem şişmez)."""
    t = re.sub(r"\s*CORRECTION:[^\n]*?(?=(?:\s+CORRECTION:)|$)", "", taban or "").strip()
    ek = [v for _, v in sorted((duzeltmeler or {}).items()) if v]
    return (t + (" " if t and ek else "") + " ".join(ek)).strip()


# --- küçük düzeltmeler (0 kredi) ----------------------------------------------------------------------------
def _isaret_yolu(film, no): return os.path.join(film, "_RAPOR", "ISARET", f"{int(no):03d}.json")


def isaretler(film, no): return ortak.json_oku(_isaret_yolu(film, no), {"plan": int(no), "uygulanan": []}) or {"plan": int(no), "uygulanan": []}


def _yeni_ad(film, no, aday):
    d = os.path.join(film, "SIRALI_GORSEL", "_ADAYLAR"); n = 1
    while os.path.exists(os.path.join(d, f"{int(no):03d}_{aday}{n}.jpg")): n += 1
    return os.path.join(d, f"{int(no):03d}_{aday}{n}.jpg")


def _uygula(kaynak, hedef, islem, oran=0.0, hedef_lab=None):
    from PIL import Image, ImageOps
    import numpy as np
    im = Image.open(kaynak).convert("RGB"); W, H = im.size
    if islem == "ayna": im = ImageOps.mirror(im)
    elif islem == "kirp":
        dx, dy = int(W * oran / 2), int(H * oran / 2)
        im = im.crop((dx, dy, W - dx, H - dy)).resize((W, H), Image.LANCZOS)
    elif islem == "renk":
        from olcum import isik
        a = np.asarray(im, dtype=np.float64); lab = np.array(isik.ortalama_lab(kaynak))
        oran_L = (hedef_lab[0] + 1) / (lab[0] + 1)
        im = Image.fromarray(np.clip(a * oran_L, 0, 255).astype("uint8"))
    tmp = hedef + ".tmp.jpg"; im.save(tmp, "JPEG", quality=94); os.replace(tmp, hedef)


def sifir_kredi(film, plan, aday, alan, kanit=None, uygula=True):
    """0 kredi basamaklarını sırayla dener (her biri plan başına bir kez). Dönüş kuyruk.py'nin istediği sifir_kredi alanı;
    uygulanabilir bir basamak varsa yeni aday dosyasını yazar ve 'yeni_aday' döner (o aday G1'den yeniden geçer)."""
    import olcum
    no = plan["no"]; der = plan.get("_derlenir") or {}
    isr = isaretler(film, no); yapildi = {u["islem"] for u in isr["uygulanan"]}
    kaynak = os.path.join(film, "SIRALI_GORSEL", "_ADAYLAR", f"{int(no):03d}_{aday}.jpg")
    denenen, gerekce = [], []
    if alan in AYNA_ALANLARI:
        denenen.append("ayna")
        if der.get("ayna_yasak", True): gerekce.append("ayna: _derlenir.ayna_yasak = true (asimetrik iz ya da elde nesne)")
        elif "ayna" in yapildi: gerekce.append("ayna bu planda zaten uygulandı (işaret dosyası)")
        elif os.path.isfile(kaynak) and uygula: return _kaydet(film, no, aday, alan, "ayna", kaynak, denenen)
    if alan in KIRPMA_ALANLARI:
        denenen.append("kirp")
        k = (kanit or {}).get("kenar")
        if not k: gerekce.append("kırpma: kusurun kenarda olduğu ölçülmedi (kutu yok)")
        elif "kirp" in yapildi: gerekce.append("kırpma zaten uygulandı")
        elif os.path.isfile(kaynak) and uygula:
            return _kaydet(film, no, aday, alan, "kirp", kaynak, denenen, oran=2 * float(olcum.esik("duzeltme_kirpma_kenar_max_oran")))
    if alan in RENK_ALANLARI:
        denenen.append("renk")
        de = (kanit or {}).get("lab_de")
        hl = (kanit or {}).get("hedef_lab")
        if de is None or hl is None: gerekce.append("renk: hedef kare ya da ΔE yok")
        elif de > float(olcum.esik("duzeltme_renk_de_max")): gerekce.append(f"renk: ΔE {de} küçük düzeltme sınırını aşıyor")
        elif "renk" in yapildi: gerekce.append("renk eşleme zaten uygulandı")
        elif os.path.isfile(kaynak) and uygula: return _kaydet(film, no, aday, alan, "renk", kaynak, denenen, hedef_lab=hl)
    if not denenen: gerekce.append(f"{alan}: 0 kredi basamağı yok (ayna/kırpma/renk bu kusuru düzeltmez); görsel 0 Flow kredisiyle yeniden üretilir")
    return {"denendi": True, "basamaklar": denenen, "gerekce": "; ".join(gerekce)}


def _kaydet(film, no, aday, alan, islem, kaynak, denenen, **kw):
    hedef = _yeni_ad(film, no, aday)
    _uygula(kaynak, hedef, islem, **kw)
    yan = ortak.json_oku(os.path.splitext(kaynak)[0] + ".json", {}) or {}
    yan.update({"turetildigi": os.path.basename(kaynak), "kucuk_duzeltme": islem, "zaman": simdi()})
    if islem == "ayna" and isinstance(yan.get("gercek"), dict) and yan["gercek"].get("kadraj_sirasi"):
        yan["gercek"]["kadraj_sirasi"] = list(reversed(yan["gercek"]["kadraj_sirasi"]))           # sahte ölçüm de aynalanır
    ortak.atomik_yaz(os.path.splitext(hedef)[0] + ".json", yan)
    isr = isaretler(film, no); isr["uygulanan"].append({"islem": islem, "alan": alan, "kaynak": os.path.basename(kaynak),
                                                       "yeni": os.path.basename(hedef), "zaman": simdi()})
    ortak.atomik_yaz(_isaret_yolu(film, no), isr)
    kayit(film, {"olay": "kucuk_duzeltme", "plan": no, "aday": aday, "alan": alan, "islem": islem, "yeni": os.path.basename(hedef)})
    return {"denendi": True, "basamaklar": denenen, "gerekce": f"{islem} uygulandı; yeni aday {os.path.basename(hedef)} G1'den yeniden geçer",
            "yeni_aday": os.path.basename(hedef)}


def kayit(film, k):
    p = os.path.join(film, "_RAPOR", "DUZELTME_KAYDI.jsonl"); os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f: f.write(json.dumps(dict(zaman=simdi(), **k), ensure_ascii=False) + "\n")


# --- madde → CORRECTION --------------------------------------------------------------------------------------
def madde_cumlesi(m, plan, karakterler=None):
    """Kuyruk maddesinden (alan, beklenen, olculen) şablon değerlerini kurup cümle üretir. karakterler: {id: {ad, kimlik_en, kostum_en}}."""
    karakterler = karakterler or {}; alan = m.get("alan") or m.get("madde")
    der = plan.get("_derlenir") or {}; kis = m.get("kisi")
    ad = (karakterler.get(kis) or {}).get("ad") or (kis or "").title()
    kad = [k.get("id") for k in (plan.get("zanaat") or {}).get("kadrajdakiler") or []]
    if alan == "fazla_kisi":
        return cumle(alan, n=len(kad), insan="person" if len(kad) == 1 else "people", adlar=", ".join((karakterler.get(k) or {}).get("ad") or k.title() for k in kad))
    if alan in ("yanlis_kisi", "kimlik", "ucte_bir"):
        u = {"sol": "frame left third", "orta": "middle of the frame", "sag": "frame right third"}.get(
            __import__("olcum").ucte_bir_normal((der.get("kadraj_konumu") or {}).get(kis)) or "orta")
        return cumle("yanlis_kisi", ucte_bir=u, ad=ad, kimlik_en=(karakterler.get(kis) or {}).get("kimlik_en") or "as in the character reference")
    if alan == "kadraj_sirasi":
        return cumle(alan, sira=", then ".join((karakterler.get(k) or {}).get("ad") or k.title() for k in der.get("kadraj_sirasi") or kad))
    if alan == "nesne_el":
        el = m.get("beklenen") if isinstance(m.get("beklenen"), str) else (m.get("beklenen") or {}).get("el", "sag")
        return cumle(alan, nesne=re.sub(r"^(a|an|the)\s+", "", str(m.get("nesne_ad") or m.get("nesne") or "object"), flags=re.I), ad=ad, EL=EL_EN.get(el, "RIGHT"),
                     iyelik=m.get("iyelik") or "the", OBUR_EL=EL_EN["sol" if el == "sag" else "sag"],
                     el_sekli_en=m.get("el_sekli_en") or "empty, fingers relaxed")
    if alan == "bakis":
        b = (der.get("bakis_kadrajda") or {}).get(kis)
        return cumle(alan, ad=ad, yon=YON_EN.get(b, "left"), hedef=m.get("hedef") or "other person")
    if alan in ("isik", "lab"):
        import kroki
        return cumle("isik", kaynak=m.get("kaynak") or "main light", yon=YON_EN.get(kroki.isik_yonu(der.get("isik_kadrajda")), "left"))
    if alan in ("yasak_oge", "ne_yok"):
        oge = m.get("oge") or ", ".join(m.get("kor") or []) or "the extra element"
        return cumle("yasak_oge", oge=oge)
    if alan == "agiz": return cumle(alan, ad=ad)
    if alan == "kostum": return cumle(alan, ad=ad, kostum_tarif_en=(karakterler.get(kis) or {}).get("kostum_en") or "the costume from the reference")
    if alan == "ifade": return cumle(alan, ad=ad, ifade_en=m.get("ifade_en") or "the expression from the shot description")
    if alan in GORUNTU and "{" not in GORUNTU[alan]: return cumle(alan)
    return None


def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 4
    import plan_ortak as po
    try:
        if "--cumle" in argv:
            alan = po.arg_al(argv, "--cumle")
            d = dict(a.split("=", 1) for a in argv[argv.index("--cumle") + 2:] if "=" in a)
            print(cumle(alan, **d)); return 0
        if "--kuyruk" in argv:
            film = po.film_kok(po.arg_al(argv, "--film"))
            r = kuyruk_isle(film, kuru="--kuru" in argv)
            print(json.dumps(r, ensure_ascii=False, indent=1)); return 0
    except DuzeltmeHatasi as e: print("!!", e); return 1
    print(__doc__); return 4


def kuyruk_isle(film, kuru=False):
    """Açık görsel maddeleri: CORRECTION'ı planın _derlenir.duzeltmeler'ine yazar, gorsel_istem'i yeniden kurar, tur sayacını artırır."""
    import kuyruk, olcum
    s = ortak.json_oku(os.path.join(film, "SAHNELER.json"))
    if not isinstance(s, dict): return {"hata": "SAHNELER.json yok"}
    planlar = {p.get("no"): p for p in s.get("sahneler") or []}
    tmax = int(olcum.esik("g1_duzeltme_tur_max"))
    out = {"islenen": [], "kacis": [], "atlanan": []}
    for m in kuyruk.acik_maddeler(film):
        if m.get("tur") != "gorsel" or m.get("kaynak_kapi") not in ("G1", "G1Z"): continue
        p = planlar.get(m["plan"])
        if p is None: out["atlanan"].append(m["id"]); continue
        der = p.setdefault("_derlenir", {}); sayac = der.setdefault("duzeltme_tur", {})
        alan = m.get("alan") or m.get("kok_neden")
        n = int(sayac.get(alan, 0))
        if n >= tmax:
            out["kacis"].append({"plan": m["plan"], "alan": alan, "madde": m["id"], "is": "sureklilik-denetcisi·kacis → yonetmen·onarim"})
            kayit(film, {"olay": "kacis", "plan": m["plan"], "alan": alan, "madde": m["id"]}); continue
        c = m.get("duzeltme")
        if not c: continue
        dz = der.setdefault("duzeltmeler", {}); dz[alan] = c
        taban = der.get("gorsel_istem_taban") or p.get("gorsel_istem") or ""
        der.setdefault("gorsel_istem_taban", taban)
        p["gorsel_istem"] = istem_kur(taban, dz); sayac[alan] = n + 1
        out["islenen"].append({"plan": m["plan"], "alan": alan, "tur": n + 1})
        kayit(film, {"olay": "correction", "plan": m["plan"], "alan": alan, "tur": n + 1, "madde": m["id"]})
    if not kuru: ortak.atomik_yaz(os.path.join(film, "SAHNELER.json"), s)
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
