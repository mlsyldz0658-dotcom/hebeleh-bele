"""EVREN KİLİT — evren.py'nin kart kilidi alt komutları (A10d; TASARIM §5.4, D-42, [GS2] GS1, GS4 adım 5). <evren>/ altına yalnız evren.py
(bu modül dahil) yazar.

Kullanım (evren.py üzerinden):
  python evren.py --kilitle --film <film> [--seri SERI]
        _KARTLAR/KART_SECIM.json (yonetmen·kart_secimi) + _RAPOR/KART_KAPISI.json → seçilen adaylar evrene sürümle kopyalanır ve kilitlenir:
        karakterler/<id>/{karakter.json, kart_<varyant>_v<N>.jpg, yuz_v<N>.jpg, banka_v<N>.npz}, mekanlar/<id>/{mekan.json, plaka_<p>_v<N>.jpg},
        nesneler/<id>/{nesne.json, kart_olcekli_v<N>.jpg}; dosya SHA1'leri karakter.json → hash; filmde 01_KARAKTERLER/<id>.jpg (geriye uyum).
        KART kapısında HATA'lı aday KİLİTLENMEZ (1). kimlik_en karakterin adını içeriyorsa HATA (1). Kilitli kayıtların SHA1'i önce doğrulanır.
  python evren.py --kilit-dogrula [--seri SERI | --film <film>]     kilitli dosyaların SHA1'i kayıtla aynı mı (değişmişse 1: hat durur)
  python evren.py --surum-ac --karakter <id> [--seri SERI | --film <film>]   kilitli karakterde yeni sürüm açar (eski dosyalar kalır)
  Kodda: import evren_kilit as ek · ek.kilitle(film, seri) → (rapor, kod) · ek.kilit_dogrula(seri) → [bulgu] · ek.surum_ac(seri, kid)
         ek.alan_yaz(seri, goreli_yol, alanlar, sahip) — sahip dışı alana yazma SahipHatasi
Sahiplik (D-42): karakter.json, mekan.json, nesne.json, dunya.json, KALIBRASYON.json, DURUM_SON.json → goruntu; hikaye.json → hikaye;
  ses.json → ses; kroki.json, kurulumlar.json, EKRAN_YONU.json → yonetmen. Silme yok; eski sürüm dosyaları yerinde kalır.
Çıkış kodları: 0 tamam · 1 HATA (HATA'lı aday, kimlik_en'de ad, SHA1 değişti, sahip dışı yazma) · 2 girdi yok · 4 ORTAM.
"""
import os, sys, re, json, shutil, hashlib, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "evren_kilit 1.0"
SAHIP = {"karakter.json": "goruntu", "mekan.json": "goruntu", "nesne.json": "goruntu", "dunya.json": "goruntu", "KALIBRASYON.json": "goruntu",
         "DURUM_SON.json": "goruntu", "hikaye.json": "hikaye", "ses.json": "ses", "kroki.json": "yonetmen", "kurulumlar.json": "yonetmen",
         "EKRAN_YONU.json": "yonetmen", "evren.json": "evren"}
# karakter.json içinde başka uzmanın yazdığı alanlar (on_kayit: hikâye kimlikleri)
ORTAK_ALAN = {"karakter.json": {"ad": "hikaye", "kostum_kimlikleri": "hikaye"}}


class SahipHatasi(Exception):
    pass


def simdi(): return datetime.datetime.now().astimezone().isoformat(timespec="seconds")


def sha1(yol):
    h = hashlib.sha1()
    with open(yol, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()


def _ev():
    import evren
    return evren


def alan_yaz(seri, goreli, alanlar, sahip):
    """<evren>/<seri>/<goreli> JSON'una yalnız sahibinin alanlarını yazar. Dosyanın sahibi başkaysa ya da alan başka uzmanınsa SahipHatasi."""
    ad = os.path.basename(goreli); s = SAHIP.get(ad)
    if s is None: raise SahipHatasi(f"{goreli}: sahibi tanımsız dosya")
    for a in alanlar:
        asil = (ORTAK_ALAN.get(ad) or {}).get(a, s)
        if asil != sahip: raise SahipHatasi(f"{goreli}.{a}: sahibi {asil}; {sahip} yazamaz (D-42)")
    p = _ev().seri_yolu(seri, *goreli.split("/"))
    v = ortak.json_oku(p, {}) or {}
    yeni = dict(v); yeni.update(alanlar)
    _ev()._surumlu_yaz(p, yeni)
    return yeni


def _kopya(a, b):
    os.makedirs(os.path.dirname(b), exist_ok=True); tmp = b + ".tmp"; shutil.copyfile(a, tmp); os.replace(tmp, b)


def kilit_dogrula(seri):
    """Kilitli kayıtların SHA1'leri. [{dosya, beklenen, bulunan, neden}] (boş = temiz)."""
    ev = _ev(); kok = ev.seri_yolu(seri); out = []
    if not os.path.isdir(kok): return out
    for tur in ("karakterler", "mekanlar", "nesneler"):
        d = os.path.join(kok, tur)
        if not os.path.isdir(d): continue
        for kid in sorted(os.listdir(d)):
            ad = {"karakterler": "karakter.json", "mekanlar": "mekan.json", "nesneler": "nesne.json"}[tur]
            j = ortak.json_oku(os.path.join(d, kid, ad), {}) or {}
            if j.get("durum") != "kilitli": continue
            hs = dict(j.get("hash") or {})
            for pid, pv in (j.get("plakalar") or {}).items():
                if isinstance(pv, dict) and pv.get("gorsel") and pv.get("sha1"): hs[pv["gorsel"]] = pv["sha1"]
            for dosya, h in hs.items():
                p = os.path.join(d, kid, dosya)
                if not os.path.isfile(p): out.append({"dosya": f"{tur}/{kid}/{dosya}", "beklenen": h, "bulunan": None, "neden": "dosya yok"}); continue
                b = sha1(p)
                if not b.startswith(str(h).replace("sha1:", "")[:40]):
                    out.append({"dosya": f"{tur}/{kid}/{dosya}", "beklenen": h, "bulunan": b,
                                "neden": "kilitli kart elle değişmiş: hat durur; yeni sürüm için evren.py --surum-ac"})
    return out


def surum_ac(seri, kid):
    ev = _ev(); p = ev.seri_yolu(seri, "karakterler", kid, "karakter.json")
    j = ortak.json_oku(p)
    if not isinstance(j, dict): return {"sonuc": "HATA", "neden": f"karakter {kid} evrende yok"}, 1
    y = dict(j); y["durum"] = "surum_acik"
    y.setdefault("gecmis", []).append({"surum": j.get("surum"), "tarih": simdi()[:10], "neden": "sürüm açıldı (yeni kart bekleniyor)"})
    ev._surumlu_yaz(p, y)
    return {"sonuc": "GEC", "karakter": kid, "surum": j.get("surum")}, 0


def _secim(kok):
    s = ortak.json_oku(os.path.join(kok, "_KARTLAR", "KART_SECIM.json"))
    if isinstance(s, dict) and isinstance(s.get("secim"), dict): return {k: (v if isinstance(v, str) else v.get("aday")) for k, v in s["secim"].items()}
    lst = s.get("secim") if isinstance(s, dict) else s
    return {x["kart_id"]: x["aday"] for x in lst or [] if isinstance(x, dict) and x.get("kart_id")}


def _ad_var(kimlik_en, ad):
    return bool(ad) and re.search(r"\b" + re.escape(str(ad).lower()) + r"\b", str(kimlik_en or "").lower())


def kilitle(film, seri=None):
    import kart_denetim as kd, istem_derle_gorsel as idg
    ev = _ev(); film = os.path.abspath(film)
    seri = ev.seri_normal(seri) or ev.film_serisi(film)
    if not seri: return {"sonuc": "HATA", "hatalar": ["seri adı yok"]}, 1
    kk = ortak.json_oku(os.path.join(film, "_RAPOR", "KART_KAPISI.json"))
    secim = _secim(film)
    if not isinstance(kk, dict) or not secim: return {"sonuc": "HATA", "hatalar": ["KART_KAPISI.json ya da KART_SECIM.json yok"]}, 2
    degisen = kilit_dogrula(seri)
    if degisen: return {"sonuc": "HATA", "durdu": True, "hatalar": degisen}, 1
    spec = kd._spec(film); kartlar = kk.get("kartlar") or {}
    hik = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
    hatalar, uyari, yazilan = [], [], []
    for kart_id, aday in sorted(secim.items()):
        k = kartlar.get(kart_id) or {}
        a = next((x for x in k.get("adaylar") or [] if x.get("aday") == aday), None)
        if a is None: hatalar.append(f"{kart_id}: aday {aday} KART_KAPISI'nda yok"); continue
        if a.get("karar") == "HATA": hatalar.append(f"{kart_id}/{aday}: KART kapısında HATA; kilitlenmez"); continue
        if a.get("karar") == "BAYRAK": uyari.append(f"{kart_id}/{aday}: BAYRAK ile kilitlendi")
    for kart_id, aday in sorted(secim.items()):
        if kart_id.startswith("karakter_"):
            kid = next((i for i in spec["karakter"] if kart_id.startswith(f"karakter_{i}_")), None)
            s = spec["karakter"].get(kid) or {}
            ad = ((hik.get("karakterler") or {}).get(kid) or {}).get("ad") or (ev.seri_yolu(seri) and (ortak.json_oku(ev.seri_yolu(seri, "karakterler", kid or "_", "karakter.json"), {}) or {}).get("ad"))
            if _ad_var(s.get("kimlik_en"), ad) or _ad_var(s.get("kimlik_en"), kid):
                hatalar.append(f"{kart_id}: kimlik_en karakterin adını içeriyor ('{ad}'); ad istemde 'Ad — kimlik_en' biçiminde ayrı yazılır")
    if hatalar: return {"sonuc": "HATA", "hatalar": hatalar}, 1
    surumler = {}
    for kart_id, aday in sorted(secim.items()):
        k = kartlar[kart_id]; a = next(x for x in k["adaylar"] if x["aday"] == aday)
        kaynak = os.path.join(film, a["gorsel"])
        if kart_id.startswith("karakter_"):
            kid = next(i for i in spec["karakter"] if kart_id.startswith(f"karakter_{i}_")); var = kart_id[len(f"karakter_{kid}_"):]
            if kid not in surumler:
                surumler[kid] = int((ortak.json_oku(ev.seri_yolu(seri, "karakterler", kid, "karakter.json"), {}) or {}).get("surum") or 0) + 1
            yazilan.append(_karakter(film, seri, kid, var, spec["karakter"][kid], kaynak, a, hik, uyari, surumler[kid]))
        elif kart_id.startswith("mekan_"):
            mid = next(i for i in spec["mekan"] if kart_id.startswith(f"mekan_{i}_")); pid = kart_id[len(f"mekan_{mid}_"):]
            yazilan.append(_mekan(seri, mid, pid, spec["mekan"][mid], kaynak, a))
        elif kart_id.startswith("nesne_"):
            nid = next(i for i in spec["nesne"] if kart_id.startswith(f"nesne_{i}_"))
            yazilan.append(_nesne(seri, nid, spec["nesne"][nid], kaynak))
    return {"sonuc": "BAYRAK" if uyari else "GEC", "seri": seri, "yazilan": yazilan, "bayraklar": uyari}, 0


def _karakter(film, seri, kid, var, s, kaynak, a, hik, uyari, n):
    ev = _ev(); d = ev.seri_yolu(seri, "karakterler", kid); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "karakter.json"); j = ortak.json_oku(p, {}) or {}
    kart = f"kart_{var}_v{n}.jpg"; _kopya(kaynak, os.path.join(d, kart))
    hs = dict(j.get("hash") or {}); hs[kart] = sha1(os.path.join(d, kart))
    banka, yuz = _banka(os.path.join(d, kart), kid, s, d, n, uyari)
    if banka: hs[banka] = sha1(os.path.join(d, banka))
    if yuz: hs[yuz] = sha1(os.path.join(d, yuz))
    kost = dict(j.get("kostumler") or {})
    if s.get("tur") == "yaratik":
        ev_ = dict(j.get("evreler") or {}); ev_[var] = dict((s.get("evreler") or {}).get(var) or {}, kart=kart); alanlar_ek = {"evreler": ev_}
    else:
        kost[var] = dict((s.get("kostumler") or {}).get(var) or {}, kart=kart); alanlar_ek = {"kostumler": kost}
    y = dict(j)
    y.update({"id": kid, "seri": seri, "tur": s.get("tur") or j.get("tur") or "insan", "surum": n, "durum": "kilitli",
              "kimlik_en": s.get("kimlik_en"), "asimetrik": s.get("asimetrik") or [], "ayirt_edici": s.get("ayirt_edici") or [],
              "bilincli_benzerlik": s.get("bilincli_benzerlik") or [], "varsayilan_kostum": j.get("varsayilan_kostum") or s.get("varsayilan_kostum") or var,
              "yasak": sorted(set((j.get("yasak") or []) + (s.get("yasak") or []))), "hash": hs,
              "kartlar": {"sayfa": kart, "yuz": yuz}, "kimlik_isaretleri": s.get("kimlik_isaretleri"),
              "olcum": {"yontem": "dinov2" if s.get("tur") == "yaratik" else "sface", "banka": banka, "gorunum_sayisi": 6,
                        "esik_gec": 0.45, "esik_hata": 0.363, "fark_payi_min": 0.05, "kalibrasyon_ref": "../../KALIBRASYON.json#" + kid,
                        "bulucu_sorgu": (s.get("olcum") or {}).get("bulucu_sorgu")}})
    y.update(alanlar_ek)
    for a_ in ("boy_m", "goz_yuksekligi_m", "baskin_el"):
        if s.get(a_) is not None: y[a_] = s[a_]
    y.setdefault("gecmis", []).append({"surum": n, "tarih": simdi()[:10], "neden": f"kart {var} kilitlendi ({os.path.basename(kaynak)})",
                                       "kart_kapisi": a.get("karar")})
    ev._surumlu_yaz(p, y)
    od = os.path.join(film, "01_KARAKTERLER"); _kopya(os.path.join(d, kart), os.path.join(od, f"{kid}.jpg"))
    return f"karakterler/{kid}/{kart}"


def _banka(kart, kid, s, d, n, uyari):
    """SFace (insan) ya da DINOv2 (yaratık) kimlik bankası; ölçülemezse BAYRAK ve (None, None)."""
    try:
        if s.get("tur") == "yaratik":
            from olcum import gorunum, kimlik
            v = gorunum.dinov2(kart); ad = f"banka_v{n}.npz"; kimlik.banka_yaz(os.path.join(d, ad), {"dinov2:" + kid: [v]})
            return ad, None
        from olcum import kimlik
        ys = kimlik.yuzler(kart)
        if not ys: uyari.append(f"{kid}: kart sayfasında yüz bulunamadı; banka yazılamadı (G1 kimliği ÖLÇÜLEMEDİ olur)"); return None, None
        ad = f"banka_v{n}.npz"; kimlik.banka_yaz(os.path.join(d, ad), {kid: [y["vektor"] for y in ys]})
        en = max(ys, key=lambda y: y["kutu"][3]); x, y0, w, h = [int(v) for v in en["kutu"]]
        from PIL import Image
        im = Image.open(kart).convert("RGB"); pay = int(h * 0.3)
        yuz = f"yuz_v{n}.jpg"; im.crop((max(0, x - pay), max(0, y0 - pay), x + w + pay, y0 + h + pay)).save(os.path.join(d, yuz), "JPEG", quality=94)
        return ad, yuz
    except Exception as e:
        uyari.append(f"{kid}: kimlik bankası ölçülemedi ({e.__class__.__name__}: {str(e)[:120]})"); return None, None


def _mekan(seri, mid, pid, s, kaynak, a):
    ev = _ev(); d = ev.seri_yolu(seri, "mekanlar", mid); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "mekan.json"); j = ortak.json_oku(p, {}) or {}
    pl = dict(j.get("plakalar") or {}); n = int(((pl.get(pid) or {}).get("surum")) or 0) + 1
    ad = f"plaka_{pid}_v{n}.jpg"; _kopya(kaynak, os.path.join(d, ad))
    pl[pid] = {"gorsel": ad, "sha1": sha1(os.path.join(d, ad)), "durum": "kilitli", "surum": n,
               "gorunen_denetim": {r["alan"].split(":", 1)[1]: r.get("kor") for r in (a.get("kor") or []) if str(r.get("alan", "")).startswith("gorunen:")} if a.get("kor") else {}}
    y = dict(j); y.update({"id": mid, "seri": seri, "tarif_en": s.get("tarif_en") or j.get("tarif_en"), "notr_durum": s.get("notr_durum") or j.get("notr_durum"),
                           "plakalar": pl, "durum": "kilitli", "surum": int(j.get("surum") or 0) + 1})
    ev._surumlu_yaz(p, y)
    return f"mekanlar/{mid}/{ad}"


def _nesne(seri, nid, s, kaynak):
    ev = _ev(); d = ev.seri_yolu(seri, "nesneler", nid); os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "nesne.json"); j = ortak.json_oku(p, {}) or {}
    n = int(j.get("surum") or 0) + 1; ad = f"kart_olcekli_v{n}.jpg"; _kopya(kaynak, os.path.join(d, ad))
    y = dict(j); y.update({k: v for k, v in s.items() if k not in ("id",)})
    y.update({"id": nid, "surum": n, "durum": "kilitli", "olcek_karti": ad, "hash": {ad: sha1(os.path.join(d, ad))}})
    ev._surumlu_yaz(p, y)
    return f"nesneler/{nid}/{ad}"


def ana(a):
    """evren.py main'inden çağrılır. None → bu modülün komutu değil."""
    ev = _ev()
    film = ev._film_yolu(ev._arg(a, "--film")); seri = ev.seri_normal(ev._arg(a, "--seri"))
    if "--kilitle" in a:
        if not film: print("!! --film gerekli"); return 1
        r, kod = kilitle(film, seri); print(json.dumps(r, ensure_ascii=False, indent=1)); return kod
    if "--kilit-dogrula" in a:
        seri = seri or (ev.film_serisi(film) if film else None)
        if not seri: print("!! --seri ya da --film gerekli"); return 1
        b = kilit_dogrula(seri); print(json.dumps({"seri": seri, "degisen": b}, ensure_ascii=False, indent=1)); return 1 if b else 0
    if "--surum-ac" in a:
        seri = seri or (ev.film_serisi(film) if film else None); kid = ev._arg(a, "--karakter")
        if not seri or not kid: print("!! --karakter ve --seri/--film gerekli"); return 1
        r, kod = surum_ac(seri, kid); print(json.dumps(r, ensure_ascii=False)); return kod
    return None
