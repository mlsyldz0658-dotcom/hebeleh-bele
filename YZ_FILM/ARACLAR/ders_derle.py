"""DERS DERLE — ders defterinin derlemesi ve film sonu raporu (TASARIM §1.3 A18, §5.3, D-33, §7.4 M1–M17, §1.5 kural 8).

film.py görevi olarak çağrılır ("<arac> <args> --film <film>"; YZ_FILM_GOREV = görev klasörü; tur ve rapor yolu oradan):
  python ders_derle.py --film <film>
        (A18 DD) <veri>/BILGI/DERSLER/ham/*.json → kümeler → _RAPOR/DERS_KUMELERI.json (ders-editoru'nun girdisi) +
        <veri>/BILGI/DERSLER_AKTIF.md (aktif ve deneme kurallarından, rol etiketine göre bölümlü; §5.3 satır biçimi).
  python ders_derle.py --film-sonu --film <film>
        (A18 DF) ders-editoru'nun aday kuralları (_RAPOR/DERS_ADAY.json) → kural başına korkuluk (ders_defteri.korkuluk) →
        yaşam döngüsü (aday → deneme → aktif → pasif) → KURALLAR_OGRENILEN.json (ders_defteri.ogrenilen_yaz; korkuluktan geçmeyen
        dosya yazılmaz) → DERSLER_AKTIF.md → FILM_SONU_RAPORU.md (açık eksikler, hedef_alti, durdurulan planlar, ölçülemeyenler,
        el işi gerçekleşeni, kredi, M1–M17) → kapı raporu _RAPOR/DERS_t<n>.json (kapı DERS).
  Seçenekler: --tur N (görev klasörü yoksa) · --bilgi <BILGI klasörü> (test)
Yaşam döngüsü (§5.3): yeni aday → korkuluktan geçerse "deneme" (sonraki ≈ 40 planın yarısında; ilk filmde yalnız sıkılaştırıcı aday
  aynı filmin sonraki partisine uygulanabilir). deneme → aktif: destek ≥ 3 ve ≥ 2 film (tek filmde ≥ 5); hikâye dersi ≥ 2 film;
  deneme sonucu varsa başarı ≥ 2/3. karşı ≥ destek → pasif (aktif güvenlik kuralı hariç: o hiç geri alınmaz).
DERS kapısı: korkuluktan geçmeyen aday reddedilir (BAYRAK, raporda listelenir); yazılacak dosya korkuluğu geçemezse HATA
  (dosya değişmez). Ölçülemeyen kalite kapıları (M17) film sonu raporunda açık eksik olarak durur; sessizce GEÇ sayılmaz.
Çıkış kodları: 0 tamam (kapı sonucu raporda) · 1 girdi bozuk · 4 ORTAM (YOLLAR.json yok) · kullanım 4.
"""
import os, re, sys, json, glob, copy, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kapi
import ders_defteri as dd

SURUM = "ders_derle 1.0"
BITTI, HATA, ORTAM = 0, 1, 4
DESTEK_MIN, FILM_MIN, TEK_FILM_DESTEK_MIN, DENEME_BASARI_MIN = 3, 2, 5, 2 / 3      # §5.3 (karar metni)
HIKAYE_ROLLERI = ("hikaye", "senaryo", "senarist")
SIKILASTIRICI = ("filtre_kelimesi", "yasak_fiil", "risk_desen", "esik", "tempo", "flow_tavan", "yasak_kalip", "kara_liste")


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def gorev_baglami(tur=None):
    g = ortak.json_oku(os.path.join(os.environ.get("YZ_FILM_GOREV") or "", "GOREV.json"), {}) or {}
    return {"id": g.get("id"), "tur_no": int(tur or g.get("tur_no") or 1), "asama": g.get("asama") or "A18", "rapor": g.get("rapor")}


def film_adi(film): return (ortak.json_oku(os.path.join(film, "HAZIRLIK.json"), {}) or {}).get("film") or os.path.basename(film)


def zarf(g, sonuc="GEC"):
    return {"asama": g["asama"], "gorev": g["id"], "girdi_imza": None, "arac_surum": SURUM, "esik_surum": None, "sonuc": sonuc,
            "zaman": simdi(), "ortam": kapi.ortam()}


# --- kümeler -----------------------------------------------------------------------------------------------------
def kume_anahtari(d):
    b = d.get("baglam") or {}
    return "|".join(str(x or "-") for x in (d.get("olay"), d.get("kapi"), d.get("madde"), d.get("kategori"), d.get("rol_etiketi"),
                                            b.get("plan_tipi"), b.get("kadraj")))


def kumeler(hamlar):
    k = {}
    for d in hamlar:
        a = kume_anahtari(d)
        x = k.setdefault(a, {"anahtar": a, "olay": d.get("olay"), "kapi": d.get("kapi"), "madde": d.get("madde"),
                             "kategori": d.get("kategori"), "rol_etiketi": d.get("rol_etiketi"), "sayi": 0, "agirlik": 0,
                             "filmler": [], "kanit": [], "sonuc": {"duzeldi": 0, "duzelmedi": 0, "plan_degisti": 0, "bilinmiyor": 0},
                             "kaynaklar": {}, "ornek_belirti": [], "ornek_eylem": []})
        x["sayi"] += 1; x["agirlik"] += dd.KANIT_AGIRLIK.get(d.get("kaynak"), 1)
        if d.get("film") and d["film"] not in x["filmler"]: x["filmler"].append(d["film"])
        if d.get("id"): x["kanit"].append(d["id"])
        x["sonuc"][d.get("sonuc") or "bilinmiyor"] = x["sonuc"].get(d.get("sonuc") or "bilinmiyor", 0) + 1
        x["kaynaklar"][d.get("kaynak") or "?"] = x["kaynaklar"].get(d.get("kaynak") or "?", 0) + 1
        for alan, liste in (("belirti", "ornek_belirti"), ("eylem", "ornek_eylem")):
            v = d.get(alan)
            if v and v not in x[liste] and len(x[liste]) < 3: x[liste].append(v)
    return sorted(k.values(), key=lambda x: (-x["agirlik"], -x["sayi"], x["anahtar"]))


def kanit_say(kural, hamlar):
    """(destek, karşı, filmler): kuralın kanıt kimlikleri ham kayıtlarda aranır; 'yanlis_alarm' olayları ve 'duzelmedi' karşıdır."""
    ids = set(kural.get("kanit") or []); karsi_ids = set(kural.get("karsi_kanit") or [])
    destek = karsi = 0; filmler = set()
    for d in hamlar:
        if d.get("id") in ids:
            if d.get("olay") == "yanlis_alarm" or d.get("sonuc") == "duzelmedi": karsi += 1
            else: destek += 1
            if d.get("film"): filmler.add(d["film"])
        elif d.get("id") in karsi_ids: karsi += 1
    return destek, karsi, sorted(filmler)


# --- DERSLER_AKTIF.md ----------------------------------------------------------------------------------------------
def _kapsam_metni(k):
    kp = k.get("kapsam") or {}
    return "/".join(str(v) for v in kp.values()) if isinstance(kp, dict) and kp else (k.get("tur") or "genel")


def _deger_metni(v): return f'"{v}"' if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def aktif_md(ogr):
    gruplar = {}
    for k in ogr.get("kurallar") or []:
        if k.get("durum") not in ("aktif", "deneme"): continue
        gruplar.setdefault(k.get("rol_etiketi") or "genel", []).append(k)
    s = ["# Aktif dersler (üretildi: ders_derle.py; elle düzenlenmez)", "",
         "Satır: kimlik · kapsam · değer · durum · kanıt destek/karşı. Ajanlara rol etiketine göre GIRDI/DERSLER.md olarak verilir; "
         "kör rollere verilmez. Güvenlik kuralları öğrenmeyle gevşemez.", ""]
    if not gruplar: s.append("(henüz aktif ya da denemede ders yok)")
    for rol in sorted(gruplar):
        s += [f"## {rol}", ""]
        for k in sorted(gruplar[rol], key=lambda x: x.get("id", "")):
            s.append(f"- {k.get('id')} · {_kapsam_metni(k)} · {_deger_metni(k.get('deger'))} · {k.get('durum')} · "
                     f"kanıt {k.get('destek', 0)}/{k.get('karsi', 0)}")
        s.append("")
    return "\n".join(s).rstrip() + "\n"


def _metin_yaz(p, m):
    os.makedirs(os.path.dirname(p), exist_ok=True); tmp = p + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f: f.write(m)
    os.replace(tmp, p)


# --- yaşam döngüsü ---------------------------------------------------------------------------------------------------
def terfi_eder(k):
    filmler = len(k.get("filmler") or []); destek = int(k.get("destek") or 0)
    if (k.get("rol_etiketi") or "") in HIKAYE_ROLLERI and filmler < FILM_MIN: return False
    if not ((destek >= DESTEK_MIN and filmler >= FILM_MIN) or destek >= TEK_FILM_DESTEK_MIN): return False
    dn = k.get("deneme") or {}
    if isinstance(dn.get("basari"), (int, float)) and isinstance(dn.get("toplam"), (int, float)) and dn["toplam"] > 0:
        return dn["basari"] / dn["toplam"] >= DENEME_BASARI_MIN
    return True


def yasam_dongusu(ogr, adaylar, hamlar, film, E=None):
    """(yeni öğrenilen sözlük, reddedilen [{kural, hatalar}], değişimler [metin]). Korunan aktif kurallara dokunmaz."""
    v = copy.deepcopy(ogr); kurallar = v.setdefault("kurallar", []); E = E if E is not None else dd.taban_esikler()
    red, deg = [], []
    var_ids = {k.get("id") for k in kurallar}
    n = max([int(x["id"][3:]) for x in kurallar if re.fullmatch(r"OK-\d+", str(x.get("id", "")))] + [0])
    for a in adaylar:
        if not isinstance(a, dict): red.append({"kural": a, "hatalar": ["kural sözlük değil"]}); continue
        k = copy.deepcopy(a)
        if not k.get("id") or k["id"] in var_ids: n += 1; k["id"] = f"OK-{n:04d}"
        k["destek"], k["karsi"], k["filmler"] = kanit_say(k, hamlar)
        k["durum"] = "deneme"
        if k.get("tur") in ("tempo", "flow_tavan", "esik"): k.setdefault("yon", "sikilastir")
        k.setdefault("deneme", {"yontem": "cift_plan_no", "baslangic_film": film,
                                "ayni_film": k.get("tur") in SIKILASTIRICI})
        h = dd.korkuluk(k, E)
        if h: red.append({"kural": a, "hatalar": h}); continue
        kurallar.append(k); var_ids.add(k["id"]); deg.append(f"{k['id']} yeni deneme ({k.get('tur')})")
    for k in kurallar:
        if dd._korunan(k, E): continue
        if int(k.get("karsi") or 0) >= max(1, int(k.get("destek") or 0)) and k.get("durum") in ("deneme", "aktif"):
            k["durum"] = "pasif"; deg.append(f"{k['id']} pasif (karşı ≥ destek)")
        elif k.get("durum") == "deneme" and terfi_eder(k) and not (k.get("deneme") or {}).get("baslangic_film") == film:
            yeni = dict(k, durum="aktif")
            if dd.korkuluk(yeni, E): continue                   # aktif olunca korkuluk (yanlış alarm oranı) geçmiyorsa denemede kalır
            k["durum"] = "aktif"; deg.append(f"{k['id']} aktif (destek {k.get('destek')}, {len(k.get('filmler') or [])} film)")
    return v, red, deg


# --- film sonu raporu -----------------------------------------------------------------------------------------------
def son_raporlar(film):
    """Her (kapı, kapsam) için en son kapı raporu."""
    son = {}
    for p in glob.glob(os.path.join(film, "_RAPOR", "*.json")):
        r = ortak.json_oku(p)
        if not isinstance(r, dict) or not r.get("kapi") or not isinstance(r.get("_uretim"), dict): continue
        a = (r["kapi"], r.get("kapsam") or "")
        if a not in son or (r.get("tur") or 0, r["_uretim"].get("zaman") or "") >= (son[a][1].get("tur") or 0,
                                                                                    son[a][1]["_uretim"].get("zaman") or ""):
            son[a] = (os.path.relpath(p, film).replace("\\", "/"), r)
    return son


def _jsonl(p):
    out = []
    try:
        with open(p, encoding="utf-8") as f:
            for s in f:
                try: out.append(json.loads(s))
                except ValueError: pass
    except OSError: pass
    return out


def _sure_sn(a, b):
    try:
        f = lambda z: datetime.datetime.fromisoformat(z)
        return max(0.0, (f(b) - f(a)).total_seconds())
    except (TypeError, ValueError): return None


def film_sonu_verisi(film):
    son = son_raporlar(film)
    acik, olculemeyen, bayrak_say = [], [], 0
    for (kp, ks), (yol, r) in sorted(son.items()):
        if r.get("sahte"): continue
        if r.get("sonuc") in ("HATA", "KISMI"):
            for m in r.get("hatalar") or []: acik.append({"kapi": kp, "kapsam": ks, "rapor": yol, "madde": m.get("madde"),
                                                          "plan": m.get("plan") or m.get("birim"), "not": m.get("oneri") or m.get("neden")})
        for m in r.get("bayraklar") or []:
            bayrak_say += 1
            if m.get("olculemedi"): olculemeyen.append({"kapi": kp, "kapsam": ks, "rapor": yol, "madde": m.get("madde"),
                                                        "neden": m.get("neden")})
    tavan = []
    for p in sorted(glob.glob(os.path.join(film, "_RAPOR", "TAVAN_*.json"))):
        t = ortak.json_oku(p, {}) or {}
        if t.get("hedef_alti") or t.get("karar") in ("durdu", "hedef_alti", "kagit_urun", "kapi6"):
            tavan.append({"asama": t.get("asama"), "karar": t.get("karar"), "durdu": t.get("durdu") or [],
                          "hatalar": len(t.get("hatalar") or []), "rapor": os.path.relpath(p, film).replace("\\", "/")})
    el = []
    for p in glob.glob(os.path.join(film, "_GOREV", "*", "GOREV.json")):
        g = ortak.json_oku(p, {}) or {}
        if g.get("tur") == "kullanici":
            z = g.get("zaman") or {}
            el.append({"gorev": g.get("id"), "asama": g.get("asama"), "durum": g.get("durum"),
                       "sure_sn": _sure_sn(z.get("basla") or z.get("olusturma"), z.get("bitir"))})
    kd = _jsonl(os.path.join(film, "KREDI_DEFTERI.jsonl"))
    gonderim = [s for s in kd if s.get("olay") == "gonderim"]
    kredi = {}
    for s in gonderim: kredi[s.get("birim", "flow")] = kredi.get(s.get("birim", "flow"), 0) + (s.get("kredi") or 0)
    ids = [s.get("is_kimligi") for s in gonderim if s.get("is_kimligi")]
    cift = sorted({i for i in ids if ids.count(i) > 1})
    durum = ortak.json_oku(os.path.join(film, "FILM_DURUM.json"), {}) or {}
    return {"son": son, "acik": acik, "olculemeyen": olculemeyen, "bayrak_say": bayrak_say, "tavan": tavan, "el_isi": el,
            "kredi": kredi, "cift_gonderim": cift, "durum": durum}


def _m_satiri(no, ad, deger, kaynak): return f"| {no} | {ad} | {deger} | {kaynak} |"


def film_sonu_md(film, v, ders):
    ad = film_adi(film); son = v["son"]
    s8 = next((r for (kp, _), (_, r) in son.items() if kp == "S8"), None)
    yd = ortak.json_oku(os.path.join(film, "YAYIN", "YAYIN_DOGRULAMA.json"), {}) or {}
    hs = {f"{kp}_{ks}": r.get("sonuc") for (kp, ks), (_, r) in son.items() if kp.startswith("HS_")}
    flow_kilit = os.path.isfile(os.path.join(ortak.yollar()["hesap"], "FLOW_KILIDI.json"))
    el_sn = sum(x["sure_sn"] or 0 for x in v["el_isi"])
    s = [f"# Film sonu raporu — {ad}", "", f"Üretildi: {simdi()} (ders_derle.py --film-sonu). Bu rapor açık eksiklerin tam listesidir "
         "(TASARIM §1.5 kural 8, §7.4); sessizce GEÇ sayılan madde yoktur.", ""]
    s += ["## Özet", "", f"- Aşamalar: " + (", ".join(f"{k} {x.get('durum')}" + (" (hedef altı)" if x.get("hedef_alti") else "")
                                                 for k, x in (v["durum"].get("asamalar") or {}).items()) or "FILM_DURUM yok"),
          f"- Açık HATA maddesi: {len(v['acik'])} · BAYRAK: {v['bayrak_say']} · ölçülemeyen: {len(v['olculemeyen'])}",
          f"- Yayın doğrulaması: {yd.get('sonuc') or 'yok'}" + (f" · yayına hazır değil: {yd.get('hazir_degil_nedeni')}"
                                                                 if yd.get("sonuc") == "HATA" else ""), ""]
    s += ["## Açık eksikler (kalan HATA'lar)", ""]
    s += [f"- {x['kapi']} {x['kapsam']}: {x['madde']}" + (f" · plan {x['plan']}" if x["plan"] is not None else "") +
          (f" · {x['not']}" if x["not"] else "") + f" ({x['rapor']})" for x in v["acik"]] or ["- yok"]
    s += ["", "## Tavan sonrası (hedef_alti, durdurulan planlar, kâğıt ürün)", ""]
    s += [f"- {t['asama']}: {t['karar']}" + (f" · durdurulan: {', '.join(map(str, t['durdu']))}" if t["durdu"] else "") +
          f" · {t['hatalar']} madde ({t['rapor']})" for t in v["tavan"]] or ["- yok"]
    s += ["", "## Ölçülemeyenler (açık eksik; M17)", ""]
    s += [f"- {x['kapi']} {x['kapsam']}: {x['madde']}" + (f" · {x['neden']}" if x["neden"] else "") for x in v["olculemeyen"]] or ["- yok"]
    s += ["", "## Kullanıcının el işi (gerçekleşen)", "",
          f"- {len(v['el_isi'])} iş, toplam ≈ {el_sn / 60:.0f} dk (görev açılışından bitişine; bekleme dahil, üst sınırdır)"]
    s += [f"  - {x['gorev']} ({x['asama']}): {x['durum']}" for x in sorted(v["el_isi"], key=lambda x: x["gorev"] or "")]
    s += ["", "## Kredi", "", "- " + (", ".join(f"{b}: {k}" for b, k in sorted(v["kredi"].items())) or "harcama kaydı yok"),
          f"- Çift gönderim: {len(v['cift_gonderim'])}" + (f" ({', '.join(v['cift_gonderim'])})" if v["cift_gonderim"] else ""), ""]
    s += ["## Dersler", "", f"- Yeni/değişen: " + ("; ".join(ders["degisim"]) or "yok"),
          f"- Korkuluktan geçmeyip reddedilen aday: {len(ders['red'])}"]
    s += [f"  - {json.dumps(r['kural'], ensure_ascii=False)[:120]} → {'; '.join(r['hatalar'])[:200]}" for r in ders["red"]]
    s += ["", "## Başarı ölçütleri (§7.4)", "", "| # | Ölçüt | Bu film | Kaynak |", "|---|---|---|---|",
          _m_satiri("M3", "Çift harcama", len(v["cift_gonderim"]), "KREDI_DEFTERI.jsonl"),
          _m_satiri("M4", "Flow kilidi şu an", "VAR (dur kuralı uygulandı)" if flow_kilit else "yok", "HESAP/FLOW_KILIDI.json"),
          _m_satiri("M10", "Final LUFS / tepe", f"{(yd.get('ses') or {}).get('lufs')} / {(yd.get('ses') or {}).get('tepe_dbtp')}"
                    if yd else "ölçülmedi", "YAYIN_DOGRULAMA.json"),
          _m_satiri("M11", "Seyirci kapıları", ", ".join(f"{k} {x}" for k, x in sorted(hs.items())) or "rapor yok", "_RAPOR/HS_*"),
          _m_satiri("M15", "Gerçek seyirci verisi", "A18a'da (yayından 48 sa sonra)", "yayin_analiz.py"),
          _m_satiri("M16", "Tavan sonrası maddeleri", len(v["tavan"]), "_RAPOR/TAVAN_*"),
          _m_satiri("M17", "Ölçülemeyen kalite kapıları", len(v["olculemeyen"]), "kapı raporları"),
          _m_satiri("S8", "Final ses kapısı", (s8 or {}).get("sonuc", "rapor yok"), "_RAPOR/S8_*"), ""]
    return "\n".join(s)


# --- kapı raporu ------------------------------------------------------------------------------------------------------
def rapor_yaz(film, g, olc, varsayilan, ek=None):
    """DERS kapısı. ADLAR.json'da DERS henüz yoksa (YEREL_KAPILAR) yalnız 'kapi bilinmiyor' denetimi atlanır."""
    yol = os.path.join(film, g["rapor"]) if g.get("rapor") else os.path.join(film, varsayilan.format(tur=g["tur_no"]))
    r = kapi.rapor_kur("DERS", "FILM", olc, tur=g["tur_no"], asama=g["asama"], gorev=g["id"], arac_surum=SURUM, ek=ek)
    h = [x for x in kapi.dogrula(r) if not x.startswith("kapi bilinmiyor")]
    if h: raise kapi.RaporHatasi(h)
    ortak.atomik_yaz(yol, r)
    print(f"DERS: {r['sonuc']} · HATA {len(r['hatalar'])} · BAYRAK {len(r['bayraklar'])} → {os.path.relpath(yol, film)}")
    return yol, r


def derle(film, bilgi=None, g=None):
    g = g or gorev_baglami(); hamlar = dd.ham_oku(bilgi)
    k = kumeler(hamlar)
    ortak.atomik_yaz(os.path.join(film, "_RAPOR", "DERS_KUMELERI.json"),
                     {"_surum": 1, "_uretim": zarf(g), "ham_sayisi": len(hamlar), "kume_sayisi": len(k), "kumeler": k,
                      "korkuluk": {"izinli_turler": list(dd.KURAL_TURLERI), "yanlis_alarm_max": dd.YANLIS_ALARM_MAX,
                                   "sface_hata_taban": dd.SFACE_HATA_TABAN,
                                   "gevsemez": "tempo, Flow tavanı, bot/uyarı/hesap/gizli bilgi/onay/silme kuralları"}})
    ogr = dd.ogrenilen_oku(dd.ogrenilen_yolu(bilgi))
    _metin_yaz(os.path.join(dd.bilgi_kok(bilgi), "DERSLER_AKTIF.md"), aktif_md(ogr))
    print(f"Ders derlemesi: {len(hamlar)} ham kayıt → {len(k)} küme; DERSLER_AKTIF.md güncellendi.")
    return k


def adaylar_oku(film):
    a = ortak.json_oku(os.path.join(film, "_RAPOR", "DERS_ADAY.json"), {}) or {}
    if isinstance(a, list): return a
    return a.get("kurallar") or a.get("aday_kurallar") or []


def film_sonu(film, bilgi=None, g=None):
    g = g or gorev_baglami(); hamlar = dd.ham_oku(bilgi); yol = dd.ogrenilen_yolu(bilgi)
    ogr = dd.ogrenilen_oku(yol); ad = film_adi(film)
    E = dd.taban_esikler()
    yeni, red, deg = yasam_dongusu(ogr, adaylar_oku(film), hamlar, ad, E)
    olc = [{"madde": "aday_reddedildi", "seviye": "BAYRAK", "kural": r["kural"], "neden": "; ".join(r["hatalar"])[:500]} for r in red]
    try:
        if yeni != ogr or not os.path.isfile(yol): dd.ogrenilen_yaz(yeni, yol, E, uretim={"asama": "A18", "gorev": g["id"]})
        olc.append({"madde": "korkuluk", "seviye": "GEC"})
    except dd.KorkulukHatasi as e:
        olc += [{"madde": "korkuluk", "seviye": "HATA", "neden": x} for x in e.hatalar]; deg = []
    ogr2 = dd.ogrenilen_oku(yol)
    _metin_yaz(os.path.join(dd.bilgi_kok(bilgi), "DERSLER_AKTIF.md"), aktif_md(ogr2))
    v = film_sonu_verisi(film)
    _metin_yaz(os.path.join(film, "FILM_SONU_RAPORU.md"), film_sonu_md(film, v, {"degisim": deg, "red": red}))
    if v["olculemeyen"]:
        olc.append({"madde": "olculemeyen_kapilar", "seviye": "BAYRAK", "olcu": len(v["olculemeyen"]),
                    "neden": "FILM_SONU_RAPORU.md açık eksik listesinde (M17)"})
    return rapor_yaz(film, g, olc, "_RAPOR/DERS_t{tur}.json",
                     ek={"degisim": deg, "reddedilen": len(red), "acik_eksik": len(v["acik"]), "olculemeyen": len(v["olculemeyen"])})


def _arg(a, ad, v=None): return a[a.index(ad) + 1] if ad in a and a.index(ad) + 1 < len(a) else v


def _film_yolu(f):
    if not f: return None
    return os.path.abspath(f) if os.path.isdir(f) else os.path.join(ortak.yollar()["filmler"], f)


def main(a):
    if "-h" in a or "--help" in a: print(__doc__); return BITTI
    try:
        film = _film_yolu(_arg(a, "--film"))
        if not film or not os.path.isdir(film): print("!! --film <film> gerekli (klasör yok)"); return HATA
        g = gorev_baglami(_arg(a, "--tur")); bilgi = _arg(a, "--bilgi")
        if "--film-sonu" in a: film_sonu(film, bilgi, g)
        else: derle(film, bilgi, g)
        return BITTI
    except ortak.YolYok as e:
        print("!!", e); return ORTAM
    except kapi.RaporHatasi as e:
        print("!! rapor geçersiz:", e); return HATA


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
