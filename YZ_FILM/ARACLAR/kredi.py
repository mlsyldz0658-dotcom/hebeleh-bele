"""KREDİ — bütçe noktaları BUT0 / BUT1 / BUT2 / BUTK ve kredi defteri (TASARIM D-05, D-23, D-31, §1.3 A01/A07c/A13/A14, §5.6, §7.2).

Sayıların hepsi olcek.py'den (tek kaynak) ve eşik dosyalarından gelir (esikler.py; FILM_AYAR güvenlik sınırlarını yalnız sıkılaştırır).
Bu araç kalite düşürmez: model, çözünürlük ya da plan sayısı hiçbir zaman azaltılmaz; yazılmış film kısaltılmaz (D-05, D-31, KK6).

Kullanım:
  python kredi.py but0 [--film <film>] [--olcum OLCUM0.json] [--ayar FILM_AYAR.json] [--bakiye N] [--adim 60]
        A01: [1800, 2700] sn içinde takvime (video_gun ≤ takvim_hedef_gun) ve bütçeye sığan en uzun süreyi seçer. Ö0-b yoksa, ölçülemediyse,
        ölçülen uyarısız gün alt sınırı merdivenin tepesinin (20) altındaysa ya da 40 dk sığmıyorsa 1800 sn; 1800 de sığmıyorsa yine 1800 +
        BAYRAK ve takvim bilgi olarak. → <film>/_RAPOR/BUT0_FILM.json (yapımcının üst sınırı: ust_sinir_sn)
  python kredi.py but1 --film <film> [--ayar ...] [--olcum ...]
        A07c: SAHNELER.json'daki klip sayısıyla tahmin ≤ flow_kredi_tavan_film (null = tavan yok). Aşılırsa 5 BÜTÇE.
        → _RAPOR/BUT1_FILM.json, URETIM_ONIZLEME.json (taslak)
  python kredi.py but2 --film <film> --bakiye N [--ayar ...] [--olcum ...]
        A13: kalan klipler + kapı payı (ya da kuyruktaki video maddeleri, hangisi büyükse) + take payı ≤ bakiye × (1 − guvenlik_payi)
        ve ≤ tavan. Aşılırsa 5 BÜTÇE ("X kredi gerekiyor"). → _RAPOR/BUT2_FILM.json, URETIM_ONIZLEME.json (kesin) + .md
  python kredi.py butk --film <film> --madde <id> --kredi N [--birim flow|ai84|usd] [--dilim ana|goruntu|ses|kurgu|take]
                       [--saglayici flow] [--kritik --aktar-not "<hat-denetcisi notu>"]
        Her kredili madde: dilimde yer varsa onay (0), yoksa 5. Dilimler arası aktarım yalnız --kritik ve hat-denetcisi notuyla (D-31).
        ai84 dilimleri: film (60.000) · vc (20.000; film tavanına da sayılır) · seri (40.000). usd: usd_tavan_film (varsayılan 0 → hep 5).
        Flow için önce BUT2 gerekir (sıra kuralı 1). Karar KREDI_DEFTERI.jsonl'a "onay"/"red" satırı olarak yazılır.
  python kredi.py kaydet --film <film> --olay gonderim|iade|olcum --kredi N [--birim flow] [--dilim ana] [--madde <id>] [--plan <no>]
                         [--saglayici flow] [--is-kimligi <k>] [--not "<metin>"]      (Memmet gönderimden ÖNCE yazar)
  python kredi.py ozet --film <film> [--json]          defter özeti (birim → harcanan, dilim, onay/red)
  python kredi.py tavanlar [--ayar FILM_AYAR.json]     uygulanan tavanlar ve BAYRAK'lar
  Kodda: import kredi; kredi.but0(...) → (rapor, kod) · but1(film) · but2(film, bakiye) · butk(film, madde, kredi, ...) ·
         defter_ekle(film, olay, kredi, ...) · defter_oku(film) · defter_ozet(film) · tavanlar(ayar)
Tavanlar FILM_AYAR.json → butce'den okunur: ai84 tavanları yalnız düşürülebilir (60.000 / 40.000 / 20.000; daha gevşek değer yok sayılır +
  BAYRAK); flow_kredi_tavan_film (null = yok), usd_tavan_film (varsayılan 0) ve takvim_hedef_gun (21) kullanıcının tercihidir.
Defter: <film>/KREDI_DEFTERI.jsonl, satır başına bir olay, her satır fsync'lenir; yarım son satır okunurken atlanır ve sayılır.
Çıkış kodları: 0 BİTTİ/onay · 1 HATA (girdi yok ya da bozuk, kullanım) · 5 BÜTÇE.
"""
import os, sys, json, math, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, esikler, olcek

SURUM = "kredi 1.0"
BITTI, HATA, BUTCE = 0, 1, 5
DEFTER = "KREDI_DEFTERI.jsonl"
OLAYLAR = ("gonderim", "iade", "olcum", "onay", "red")
HARCAMA_OLAY = {"gonderim": 1, "olcum": 1, "iade": -1}
BIRIMLER = ("flow", "ai84", "usd")
FLOW_DILIM = ("ana", "goruntu", "ses", "kurgu", "take")
AI84_DILIM = ("film", "vc", "seri")
# TASARIM §5.6 / §7.2 varsayılanları. "siki": FILM_AYAR yalnız düşürebilir.
TAVAN = {"flow_kredi_tavan_film": (None, False), "ai84_kredi_tavan_film": (60000, True), "ai84_seri_kurulum_tavan": (40000, True),
         "ai84_vc_tavan_film": (20000, True), "usd_tavan_film": (0, False), "takvim_hedef_gun": (21, False)}


class Girdi(Exception):
    """Girdi dosyası yok ya da bozuk (çıkış 1)."""


def _sayi(x): return isinstance(x, (int, float)) and not isinstance(x, bool)


def _ceil(x): return int(math.ceil(x - 1e-9))


def _zaman(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def tavanlar(ayar=None):
    """FILM_AYAR.butce → uygulanan tavanlar. (tavan sözlüğü, bayraklar)"""
    b = (olcek.ayar_oku(ayar) if not isinstance(ayar, dict) else ayar).get("butce") or {}
    out, bayrak = {}, []
    for ad, (vars_, siki) in TAVAN.items():
        if ad not in b or b[ad] is None:
            out[ad] = vars_; continue
        v = b[ad]
        if not _sayi(v) or v < 0 or (ad == "takvim_hedef_gun" and v <= 0):
            out[ad] = vars_; bayrak.append({"anahtar": ad, "gelen": v, "uygulanan": vars_, "durum": "gecersiz"}); continue
        if siki and vars_ is not None and v > vars_:
            out[ad] = vars_; bayrak.append({"anahtar": ad, "gelen": v, "uygulanan": vars_, "durum": "gevsek"}); continue
        out[ad] = v
    return out, bayrak


def _yukle(E, ayar, olcum):
    ayar_d = olcek.ayar_oku(ayar) if not isinstance(ayar, dict) else ayar
    olcum_d = olcek.olcum_oku(olcum) if not isinstance(olcum, dict) else olcum
    return olcek.esik_yukle(E, ayar_d or None), ayar_d, olcum_d


def _rapor(kapi, asama, sonuc, govde, girdi, E):
    zarf = {"asama": asama, "gorev": None, "girdi_imza": olcek.imza(girdi), "arac_surum": SURUM, "esik_surum": E.get("surum"),
            "sonuc": sonuc, "zaman": _zaman(), "ortam": "yerel" if os.name == "nt" else "bulut"}
    r = {"_surum": 1, "_uretim": zarf, "kapi": kapi, "kapsam": "FILM", "tur": None, "sonuc": sonuc}
    r.update(govde)
    return r


def _yaz(film, ad, veri):
    if film: ortak.atomik_yaz(os.path.join(film, "_RAPOR", ad), veri)


def _film_sahneler(film):
    p = os.path.join(film, "SAHNELER.json")
    if not os.path.exists(p): raise Girdi(f"SAHNELER.json yok: {p}")
    try:
        with open(p, encoding="utf-8-sig") as f: return json.load(f)
    except ValueError as e: raise Girdi(f"SAHNELER.json bozuk: {e}")


def _film_suresi(film, n, E):
    """BUT0 raporundaki süre; yoksa plan sayısından (RE 40 dk dağılımıyla) geri hesap."""
    b0 = ortak.json_oku(os.path.join(film, "_RAPOR", "BUT0_FILM.json"), {}) or {}
    if _sayi(b0.get("sure_sn")): return int(b0["sure_sn"]), "BUT0"
    p40 = sum((E.get("hedef_plan_dagilimi_40dk") or {}).values()) or 495
    return int(round(n["plan"] * olcek.REF_SN / float(p40))), "plan sayısından"


# ---------------------------------------------------------------- BUT0
def but0(olcum=None, ayar=None, bakiye=None, E=None, adim_sn=60, film=None):
    """A01 süre seçimi (D-05). (rapor, kod) — kod her zaman 0 (süre seçimi hattı durdurmaz; sığmazlık BAYRAK ve bilgi)."""
    E, ayar_d, olcum_d = _yukle(E, ayar, olcum)
    T, tbayrak = tavanlar(ayar_d)
    lo, hi = (E.get("film_sure_aralik_sn") or olcek.SURE_ARALIK_VARSAYILAN)[:2]
    kirk = E.get("film_sure_hedef_sn") or olcek.REF_SN
    kap, olculdu, o0b_var, kap_not = olcek.kapasite(E, olcum_d)
    esik_kap = max(E.get("o0b_gun_tavanlari") or [20])
    gp = E.get("guvenlik_payi") or 0.0

    def dene(s):
        o = olcek.hesapla(s, E=E, olcum=olcum_d, ayar=ayar_d)
        k = o["kredi"]; gerek = k["butce_tahmini"] + (0 if o0b_var else k["olcum_kredi"])
        sb = True; neden = []
        if bakiye is not None and gerek > bakiye * (1 - gp): sb = False; neden.append(f"bakiye × {1 - gp:.2f} < {gerek}")
        if T["flow_kredi_tavan_film"] is not None and k["butce_tahmini"] > T["flow_kredi_tavan_film"]:
            sb = False; neden.append(f"flow_kredi_tavan_film {T['flow_kredi_tavan_film']} < {k['butce_tahmini']}")
        st = o["takvim"]["video_gun"] <= T["takvim_hedef_gun"]
        if not st: neden.append(f"video_gun {o['takvim']['video_gun']} > {T['takvim_hedef_gun']}")
        return {"sure_sn": s, "video_gun": o["takvim"]["video_gun"], "butce_tahmini": k["butce_tahmini"], "gereken": gerek,
                "sigar_takvim": st, "sigar_butce": sb, "sigar": st and sb, "neden": neden}, o

    adaylar, secim, neden = [], None, None
    ad_list = list(range(int(hi), int(kirk) - 1, -int(adim_sn)))
    if int(kirk) not in ad_list and lo <= kirk <= hi: ad_list.append(int(kirk))
    if not o0b_var: neden = "Ö0-b sonucu yok → 1800 sn (D-05)"
    elif not olculdu: neden = "Ö0-b ölçülemedi (uyarısız gün yok) → 1800 sn (D-05)"
    elif kap < esik_kap: neden = f"Ö0-b uyarısız gün alt sınırı {kap} < {esik_kap} → 1800 sn (D-05)"
    else:
        for s in ad_list:
            a, _ = dene(s); adaylar.append(a)
            if a["sigar"]: secim = s; neden = f"takvime ve bütçeye sığan en uzun süre ({s} sn)"; break
        if secim is None: neden = f"{int(kirk) // 60} dk takvime ya da bütçeye sığmıyor → 1800 sn (D-05)"
    if secim is None: secim = int(lo)
    a_sec, o = dene(secim)
    if not any(x["sure_sn"] == secim for x in adaylar): adaylar.append(a_sec)
    sonuc = "GEC" if a_sec["sigar"] else "BAYRAK"
    bayrak = [{"madde": "sigmiyor", "seviye": "BAYRAK", "olcu": a_sec["neden"],
               "oneri": "takvim olduğu gibi bilgi olarak verilir; süre 1800 sn'nin altına inmez (D-05)"}] if not a_sec["sigar"] else []
    bayrak += [{"madde": "tavan_" + b["durum"], "seviye": "BAYRAK", "olcu": b} for b in tbayrak]
    if bayrak: sonuc = "BAYRAK"
    t, k = o["takvim"], o["kredi"]
    kap_metin = "" if olculdu else " (Flow kapasitesi henüz ölçülmedi)"
    bilgi = [f"Süre: {secim // 60} dk{kap_metin}.",
             f"Kâğıt aşaması ≈ {olcek.aralik(t['asamalar_gun']['kagit'])} gün (tahmin).",
             f"Video için ≈ {olcek.say(k['butce_tahmini'])} kredi; takvim ≈ {t['video_gun']} video günü "
             f"({t['kapasite_gunluk']}/gün{', ölçülmedi' if not olculdu else ''})."]
    govde = {"sure_sn": secim, "ust_sinir_sn": secim, "neden": neden, "ozet": {"aday": len(adaylar), "sigar": a_sec["sigar"]},
             "kapasite": {"deger": kap, "olculdu": olculdu, "o0b_yapildi": o0b_var, "not": kap_not, "esik": esik_kap},
             "bakiye": bakiye, "bakiye_not": None if bakiye is not None else "bakiye bilinmiyor; bütçe sınaması BUT1/BUT2'de",
             "olcum_kredi": 0 if o0b_var else k["olcum_kredi"], "tavanlar": T, "adaylar": adaylar, "hatalar": bayrak,
             "bilgi": bilgi, "olcek": o, "olculmedi": o["olculmedi"]}
    r = _rapor("BUT0", "A01", sonuc, govde, [olcum_d, ayar_d.get("butce"), bakiye], E)
    _yaz(film, "BUT0_FILM.json", r)
    return r, BITTI


# ---------------------------------------------------------------- BUT1 / BUT2
def _onizleme(film, o, butce, taslak, ek=None):
    v = {"_surum": 1, "_uretim": {"asama": "A07c" if taslak else "A13", "arac_surum": SURUM, "zaman": _zaman()},
         "taslak": taslak, "butce": butce, "olcek": o}
    if ek: v.update(ek)
    ortak.atomik_yaz(os.path.join(film, "URETIM_ONIZLEME.json"), v)


def but1(film, ayar=None, olcum=None, E=None):
    """A07c: SAHNELER'in klip sayısıyla tahmin ≤ tavan. (rapor, kod 0|5)"""
    E, ayar_d, olcum_d = _yukle(E, ayar, olcum)
    T, tbayrak = tavanlar(ayar_d)
    n = olcek.sahne_say(_film_sahneler(film))
    sure, sure_k = _film_suresi(film, n, E)
    o = olcek.hesapla(sure, E=E, olcum=olcum_d, ayar=ayar_d, plan=n["plan"], klip=n["flow_klip"])
    k = o["kredi"]; tavan = T["flow_kredi_tavan_film"]
    hatalar = []
    if tavan is not None and k["butce_tahmini"] > tavan:
        hatalar.append({"madde": "tavan_asildi", "seviye": "HATA", "olcu": k["butce_tahmini"], "esik": tavan,
                        "oneri": f"{k['butce_tahmini'] - tavan} kredi eksik; yazılmış film kısaltılmaz (D-05) → 5 BÜTÇE"})
    if n["klip_sn_farkli"]:
        hatalar.append({"madde": "klip_sn_olculmedi", "seviye": "BAYRAK", "olcu": n["klip_sn_farkli"],
                        "oneri": "8 sn dışı klip kredisi ölçülmedi; 720p 8 sn kredisiyle sayıldı"})
    if n["diger_klip"]:
        hatalar.append({"madde": "flow_disi_klip", "seviye": "BAYRAK", "olcu": n["diger_klip"], "oneri": "Flow dışı klipler BUTK'dan (usd) geçer"})
    hatalar += [{"madde": "tavan_" + b["durum"], "seviye": "BAYRAK", "olcu": b} for b in tbayrak]
    sonuc = "HATA" if any(h["seviye"] == "HATA" for h in hatalar) else ("BAYRAK" if hatalar else "GEC")
    butce = {"taban": k["taban"], "dilimler": k["dilimler"], "take": k["take_payi"], "toplam": k["butce_tahmini"], "tavan": tavan}
    govde = {"sure_sn": sure, "sure_kaynak": sure_k, "sahneler": n, "butce": butce, "tavanlar": T,
             "tavan_not": None if tavan is not None else "flow_kredi_tavan_film null: film tavanı yok (BUT2 bakiyeyle sınar)",
             "ozet": {"plan": n["plan"], "klip": n["flow_klip"], "tahmin": k["butce_tahmini"]}, "hatalar": hatalar, "olcek": o}
    r = _rapor("BUT1", "A07c", sonuc, govde, [n, ayar_d.get("butce"), sure], E)
    _yaz(film, "BUT1_FILM.json", r)
    _onizleme(film, o, butce, True)
    return r, (BUTCE if sonuc == "HATA" else BITTI)


def _kuyruk_video_kredi(film):
    v = ortak.json_oku(os.path.join(film, "KUYRUK", "YENIDEN_URET.json"), None)
    maddeler = v if isinstance(v, list) else ((v or {}).get("maddeler") or [])
    t = 0
    for m in maddeler:
        if isinstance(m, dict) and m.get("tur") == "video" and m.get("durum", "bekliyor") == "bekliyor" and _sayi(m.get("kredi_tahmini")):
            t += m["kredi_tahmini"]
    return int(t), len(maddeler)


def but2(film, bakiye, ayar=None, olcum=None, E=None):
    """A13 kesin bütçe: tahmin ≤ bakiye × (1 − guvenlik_payi) ve ≤ tavan. (rapor, kod 0|5); bakiye yoksa Girdi."""
    if not _sayi(bakiye) or bakiye < 0: raise Girdi("BUT2 için Flow bakiyesi gerekir (--bakiye N; Memmet --bakiye okur)")
    E, ayar_d, olcum_d = _yukle(E, ayar, olcum)
    T, tbayrak = tavanlar(ayar_d)
    n = olcek.sahne_say(_film_sahneler(film))
    sure, sure_k = _film_suresi(film, n, E)
    kalan = max(0, n["flow_klip"] - n["uretilmis_klip"])
    o = olcek.hesapla(sure, E=E, olcum=olcum_d, ayar=ayar_d, plan=n["plan"], klip=kalan)
    k = o["kredi"]; kuyruk_kr, kuyruk_n = _kuyruk_video_kredi(film)
    kapi_kr = max(k["kapi_payi"], kuyruk_kr)
    dilim = dict(k["dilimler"])
    if kuyruk_kr > k["kapi_payi"]: dilim = {d: _ceil(v * kuyruk_kr / float(k["kapi_payi"] or 1)) for d, v in dilim.items()}
    tahmin = k["taban"] + kapi_kr + k["take_payi"]
    harcanan = defter_ozet(film)["birim"].get("flow", {}).get("harcanan", 0)
    gp = k["guvenlik_payi"]; kullanilir = int(math.floor(bakiye * (1 - gp) + 1e-9)); tavan = T["flow_kredi_tavan_film"]
    hatalar = []
    if tahmin > kullanilir:
        hatalar.append({"madde": "bakiye_yetmiyor", "seviye": "HATA", "olcu": tahmin, "esik": kullanilir,
                        "oneri": f"{tahmin - kullanilir} kredi gerekiyor (bakiye en az {_ceil(tahmin / (1 - gp))}); kalite düşürülmez → 5 BÜTÇE"})
    if tavan is not None and harcanan + tahmin > tavan:
        hatalar.append({"madde": "tavan_asildi", "seviye": "HATA", "olcu": harcanan + tahmin, "esik": tavan,
                        "oneri": f"{harcanan + tahmin - tavan} kredi film tavanını aşıyor → 5 BÜTÇE"})
    hatalar += [{"madde": "tavan_" + b["durum"], "seviye": "BAYRAK", "olcu": b} for b in tbayrak]
    sonuc = "HATA" if any(h["seviye"] == "HATA" for h in hatalar) else ("BAYRAK" if hatalar else "GEC")
    butce = {"taban": k["taban"], "ana": k["taban"], "dilimler": dilim, "kapi_payi": kapi_kr, "take": k["take_payi"], "toplam": tahmin,
             "kuyruk_video_kredi": kuyruk_kr, "bakiye": bakiye, "kullanilabilir": kullanilir, "harcanan_once": harcanan, "tavan": tavan}
    govde = {"sure_sn": sure, "sure_kaynak": sure_k, "sahneler": n, "kalan_klip": kalan, "kuyruk_madde": kuyruk_n, "butce": butce,
             "tavanlar": T, "ozet": {"tahmin": tahmin, "bakiye": bakiye, "kullanilabilir": kullanilir}, "hatalar": hatalar, "olcek": o}
    r = _rapor("BUT2", "A13", sonuc, govde, [n, ayar_d.get("butce"), bakiye, kuyruk_kr], E)
    _yaz(film, "BUT2_FILM.json", r)
    _onizleme(film, o, butce, False, {"sonuc": sonuc})
    with open(os.path.join(film, "URETIM_ONIZLEME.md"), "w", encoding="utf-8") as f: f.write(onizleme_md(r))
    return r, (BUTCE if sonuc == "HATA" else BITTI)


def onizleme_md(r):
    b, o = r["butce"], r["olcek"]; t, el, tok = o["takvim"], o["el_isi"], o["token"]; s = olcek.say
    satir = ["# Üretim önizlemesi (BUT2)", "",
             f"- Sonuç: **{r['sonuc']}**",
             f"- Video için ≈ {s(b['toplam'])} kredi gerekiyor; hesapta {s(b['bakiye'])} var (kullanılabilir {s(b['kullanilabilir'])}, "
             f"güvenlik payı {olcek.ond(o['kredi']['guvenlik_payi'])}).",
             f"- Döküm: kalan {r['kalan_klip']} klip × {o['kredi']['klip_kredi']} = {s(b['taban'])} · kapı payı {s(b['kapi_payi'])} "
             f"({', '.join(f'{d} {s(v)}' for d, v in b['dilimler'].items())}) · take {s(b['take'])}",
             f"- Flow günleri: video {t['video_gun']} gün + görsel {olcek.aralik(t['gorsel_gun'])} gün "
             f"(kapasite {t['kapasite_gunluk']}/gün; {'ölçüldü' if t['kapasite_olculdu'] else 'ölçülmedi'})",
             f"- Kullanıcının el işi ≈ {olcek.ond(el['toplam_saat'], 1)} saat (GÖNDER ≈ {s(el['gonder'])} kez, {el['paket']} paket)",
             f"- Token projeksiyonu: {('≈ ' + olcek.aralik(tok['projeksiyon'])) if tok['projeksiyon'] else 'ölçülmedi'}"]
    for h in r["hatalar"]:
        satir.append(f"- {h['seviye']}: {h['madde']} — {h.get('oneri') or h.get('olcu')}")
    return "\n".join(satir) + "\n"


# ---------------------------------------------------------------- defter
def defter_yolu(film): return os.path.join(film, DEFTER)


def defter_ekle(film, olay, kredi, birim="flow", dilim=None, **alan):
    """Kredi defterine bir satır ekler (fsync). Gönderim kaydı gönderimden ÖNCE yazılır (TASARIM §6.1 memmet v2)."""
    if olay not in OLAYLAR: raise ValueError(f"olay {olay!r} ({'|'.join(OLAYLAR)})")
    if birim not in BIRIMLER: raise ValueError(f"birim {birim!r} ({'|'.join(BIRIMLER)})")
    if not _sayi(kredi) or kredi < 0: raise ValueError(f"kredi sayı ve ≥ 0 olmalı ({kredi!r})")
    if dilim is None: dilim = "ana" if birim == "flow" else ("film" if birim == "ai84" else "film")
    kayit = {"zaman": _zaman(), "olay": olay, "birim": birim, "kredi": kredi, "dilim": dilim}
    kayit.update({k: v for k, v in alan.items() if v is not None})
    os.makedirs(film, exist_ok=True)
    satir = json.dumps(kayit, ensure_ascii=False) + "\n"
    with open(defter_yolu(film), "a", encoding="utf-8") as f:
        f.write(satir); f.flush(); os.fsync(f.fileno())
    return kayit


def defter_oku(film):
    """(satırlar, bozuk_sayısı). Yarım kalmış satır (çökme) atlanır."""
    p = defter_yolu(film); out, bozuk = [], 0
    if not os.path.exists(p): return out, 0
    with open(p, encoding="utf-8-sig", errors="replace") as f:
        for s in f:
            s = s.strip()
            if not s: continue
            try:
                k = json.loads(s)
                if isinstance(k, dict): out.append(k)
                else: bozuk += 1
            except ValueError: bozuk += 1
    return out, bozuk


def defter_ozet(film):
    satirlar, bozuk = defter_oku(film)
    ozet = {"satir": len(satirlar), "bozuk": bozuk, "birim": {}}
    for k in satirlar:
        b = ozet["birim"].setdefault(k.get("birim", "flow"), {"harcanan": 0, "dilim": {}, "onay": 0, "red": 0})
        o = k.get("olay"); kr = k.get("kredi") if _sayi(k.get("kredi")) else 0
        if o in HARCAMA_OLAY:
            b["harcanan"] += HARCAMA_OLAY[o] * kr
            d = k.get("dilim") or "ana"; b["dilim"][d] = b["dilim"].get(d, 0) + HARCAMA_OLAY[o] * kr
        elif o in ("onay", "red"): b[o] += 1
    # Bekleyen onay: gönderim/iade satırı henüz gelmemiş maddelerin onaylı kredisi (Memmet gönderim satırına onaydaki maddeyi yazar).
    gelen = {(k.get("birim", "flow"), k.get("madde")) for k in satirlar if k.get("olay") in HARCAMA_OLAY and k.get("madde")}
    for k in satirlar:
        if k.get("olay") != "onay" or (k.get("birim", "flow"), k.get("madde")) in gelen: continue
        b = ozet["birim"][k.get("birim", "flow")]; kr = k.get("kredi") if _sayi(k.get("kredi")) else 0
        b["bekleyen"] = b.get("bekleyen", 0) + kr
        bd = b.setdefault("bekleyen_dilim", {}); d = k.get("dilim") or "ana"; bd[d] = bd.get(d, 0) + kr
    return ozet


# ---------------------------------------------------------------- BUTK
def butk(film, madde, kredi, birim="flow", dilim=None, saglayici=None, kritik=False, aktar_not=None, ayar=None, E=None, plan=None):
    """Tek kredili madde için onay. (rapor, kod 0|5). Kararı deftere 'onay' ya da 'red' olarak yazar."""
    if birim not in BIRIMLER: raise Girdi(f"birim {birim!r} ({'|'.join(BIRIMLER)})")
    if not _sayi(kredi) or kredi < 0: raise Girdi(f"kredi sayı ve ≥ 0 olmalı ({kredi!r})")
    E, ayar_d, _ = _yukle(E, ayar, {})
    T, _tb = tavanlar(ayar_d)
    oz = defter_ozet(film)["birim"].get(birim, {"harcanan": 0, "dilim": {}})
    harc = oz["harcanan"] + oz.get("bekleyen", 0)            # harcanan + onaylanmış ama henüz gönderilmemiş
    hd = dict(oz["dilim"])
    for d, v in (oz.get("bekleyen_dilim") or {}).items(): hd[d] = hd.get(d, 0) + v
    neden, aktarim = None, None
    if birim == "flow":
        dilim = dilim or "ana"
        if dilim not in FLOW_DILIM: raise Girdi(f"Flow dilimi {dilim!r} ({'|'.join(FLOW_DILIM)})")
        on = ortak.json_oku(os.path.join(film, "URETIM_ONIZLEME.json"), None)
        if not on or on.get("taslak") is not False or not isinstance(on.get("butce"), dict):
            raise Girdi("Flow kredisi için önce kesin bütçe (kredi.py but2; sıra kuralı 1)")
        b = on["butce"]; pay = dict(b.get("dilimler") or {}); pay["ana"] = b.get("ana", b.get("taban", 0)); pay["take"] = b.get("take", 0)
        bos = pay.get(dilim, 0) - hd.get(dilim, 0)
        if kredi > bos:
            if kritik and aktar_not:
                havuz = sum(pay[d] - hd.get(d, 0) for d in pay if d != "ana")
                if kredi <= havuz: aktarim = {"not": aktar_not, "dilim_bos": bos, "havuz_bos": havuz}
                else: neden = f"dilimler toplamında yer yok ({havuz} < {kredi})"
            else:
                neden = f"'{dilim}' diliminde yer yok ({max(bos, 0)} < {kredi}); aktarım yalnız KRİTİK ve hat-denetcisi notuyla"
        if neden is None and T["flow_kredi_tavan_film"] is not None and harc + kredi > T["flow_kredi_tavan_film"]:
            neden = f"film tavanı {T['flow_kredi_tavan_film']} aşılıyor ({harc} + {kredi})"
        if neden is None and _sayi(b.get("kullanilabilir")) and harc - (b.get("harcanan_once") or 0) + kredi > b["kullanilabilir"]:
            neden = f"BUT2'deki kullanılabilir bakiye {b['kullanilabilir']} aşılıyor"
    elif birim == "ai84":
        dilim = dilim or "film"
        if dilim not in AI84_DILIM: raise Girdi(f"AI84 dilimi {dilim!r} ({'|'.join(AI84_DILIM)})")
        if dilim == "seri":
            if hd.get("seri", 0) + kredi > T["ai84_seri_kurulum_tavan"]: neden = f"AI84 seri kurulum tavanı {T['ai84_seri_kurulum_tavan']}"
        else:
            film_harc = harc - hd.get("seri", 0)
            if dilim == "vc" and hd.get("vc", 0) + kredi > T["ai84_vc_tavan_film"]: neden = f"AI84 ses dönüştürme tavanı {T['ai84_vc_tavan_film']}"
            elif film_harc + kredi > T["ai84_kredi_tavan_film"]: neden = f"AI84 film tavanı {T['ai84_kredi_tavan_film']}"
    else:
        dilim = dilim or "film"
        if T["usd_tavan_film"] <= 0: neden = "dolar harcaması kapalı (usd_tavan_film 0; yalnız IZINLER.bat ile açılır)"
        elif harc + kredi > T["usd_tavan_film"]: neden = f"usd_tavan_film {T['usd_tavan_film']} aşılıyor ({harc} + {kredi})"
    onay = neden is None
    kayit = defter_ekle(film, "onay" if onay else "red", kredi, birim=birim, dilim=dilim, madde=madde, plan=plan, saglayici=saglayici,
                        kritik=bool(kritik) or None, aktarim=aktarim, neden=neden)
    sonuc = "GEC" if onay else "HATA"
    hatalar = [] if onay else [{"madde": madde, "seviye": "HATA", "olcu": kredi, "esik": neden,
                                "oneri": "0 kredi çözümü (kuyruk.py); KRİTİK için o da yoksa 5 BÜTÇE (D-31)"}]
    govde = {"madde": madde, "birim": birim, "dilim": dilim, "kredi": kredi, "onay": onay, "neden": neden, "aktarim": aktarim,
             "harcanan_once": harc, "tavanlar": T, "ozet": {"onay": onay}, "hatalar": hatalar, "kayit": kayit}
    r = _rapor("BUTK", None, sonuc, govde, [madde, kredi, birim, dilim, harc], E)
    _yaz(film, "BUTK_FILM.json", r)
    return r, (BITTI if onay else BUTCE)


# ---------------------------------------------------------------- komut satırı
SECENEK = {"--film", "--olcum", "--ayar", "--bakiye", "--adim", "--madde", "--kredi", "--birim", "--dilim", "--saglayici", "--aktar-not",
           "--olay", "--plan", "--is-kimligi", "--not"}
BAYRAK = {"--kritik", "--json"}


def _arg(argv):
    a, b, i = {}, set(), 0
    while i < len(argv):
        x = argv[i]
        if x in SECENEK and i + 1 < len(argv): a[x[2:].replace("-", "_")] = argv[i + 1]; i += 2
        elif x in BAYRAK: b.add(x[2:]); i += 1
        else: raise ValueError(x)
    return a, b


def _num(x, ad):
    if x is None: return None
    try: v = float(str(x).replace(",", "."))
    except ValueError: raise Girdi(f"--{ad} sayı olmalı ({x!r})")
    return int(v) if v == int(v) else v


def main(argv):
    if not argv or argv[0] not in ("but0", "but1", "but2", "butk", "kaydet", "ozet", "tavanlar"):
        print(__doc__); return HATA
    komut = argv[0]
    try: a, b = _arg(argv[1:])
    except ValueError as e: print(f"!! bilinmeyen seçenek: {e}"); print(__doc__); return HATA
    film = a.get("film")
    try:
        if komut != "but0" and komut != "tavanlar" and not film: raise Girdi("--film <film klasörü> gerekli")
        if komut == "tavanlar":
            T, tb = tavanlar(a.get("ayar")); print(json.dumps({"tavanlar": T, "bayraklar": tb}, ensure_ascii=False, indent=1)); return BITTI
        if komut == "ozet":
            oz = defter_ozet(film)
            if "json" in b: print(json.dumps(oz, ensure_ascii=False, indent=1))
            else:
                print(f"{DEFTER}: {oz['satir']} satır ({oz['bozuk']} bozuk)")
                for br, v in oz["birim"].items():
                    dl = ", ".join(f"{d} {olcek.say(x)}" for d, x in v["dilim"].items())
                    print(f"  {br}: harcanan {olcek.say(v['harcanan'])}" + (f" ({dl})" if dl else "")
                          + f" · bekleyen onay {olcek.say(v.get('bekleyen', 0))} · onay {v['onay']} · red {v['red']}")
            return BITTI
        if komut == "kaydet":
            k = defter_ekle(film, a.get("olay") or "", _num(a.get("kredi"), "kredi"), birim=a.get("birim", "flow"), dilim=a.get("dilim"),
                            madde=a.get("madde"), plan=a.get("plan"), saglayici=a.get("saglayici"), is_kimligi=a.get("is_kimligi"),
                            **({"not": a["not"]} if a.get("not") else {}))
            print(json.dumps(k, ensure_ascii=False)); return BITTI
        if komut == "but0":
            r, kod = but0(olcum=a.get("olcum"), ayar=a.get("ayar"), bakiye=_num(a.get("bakiye"), "bakiye"),
                          adim_sn=int(_num(a.get("adim"), "adim") or 60), film=film)
            print("\n".join(r["bilgi"])); print(f"BUT0: {r['sure_sn']} sn — {r['neden']} ({r['sonuc']})")
        elif komut == "but1":
            r, kod = but1(film, ayar=a.get("ayar"), olcum=a.get("olcum"))
            print(f"BUT1: tahmin {olcek.say(r['butce']['toplam'])} kredi · tavan {r['butce']['tavan']} → {r['sonuc']}")
        elif komut == "but2":
            r, kod = but2(film, _num(a.get("bakiye"), "bakiye"), ayar=a.get("ayar"), olcum=a.get("olcum"))
            print(f"Video için ≈ {olcek.say(r['butce']['toplam'])} kredi gerekiyor; hesapta {olcek.say(r['butce']['bakiye'])} var. "
                  f"Takvim ≈ {r['olcek']['takvim']['video_gun']} video günü. → {r['sonuc']}")
        else:
            if not a.get("madde") or a.get("kredi") is None: raise Girdi("--madde ve --kredi gerekli")
            r, kod = butk(film, a["madde"], _num(a["kredi"], "kredi"), birim=a.get("birim", "flow"), dilim=a.get("dilim"),
                          saglayici=a.get("saglayici"), kritik="kritik" in b, aktar_not=a.get("aktar_not"), ayar=a.get("ayar"),
                          plan=a.get("plan"))
            print(f"BUTK {a['madde']}: {'onay' if r['onay'] else 'RED — ' + r['neden']}")
        for h in r.get("hatalar") or []:
            print(f"  {h['seviye']} {h['madde']}: {h.get('oneri') or h.get('olcu')}")
        if "json" in b: print(json.dumps(r, ensure_ascii=False, indent=1))
        return kod
    except Girdi as e: print(f"!! {e}"); return HATA
    except esikler.EsikHatasi as e: print(f"!! {e}"); return HATA
    except ValueError as e: print(f"!! {e}"); return HATA


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
