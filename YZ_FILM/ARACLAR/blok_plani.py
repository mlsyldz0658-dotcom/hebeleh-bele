"""BLOK PLANI — video gönderim blokları: uygunluk kuyruğu, blok ≤ 20 plan, dikey kesit, pilot kararı (TASARIM §6.1, D-03, D-15, D-17, D-41).

Kullanım:
  python blok_plani.py --film <film>                A14: o an uygun planları ≤ 20'lik bloklara koyar → BLOK_PLANI.json
  python blok_plani.py --kesit --film <film>        A14a: dikey kesit planları (P0 + P1'in başı ≈ 180 sn) + kapsama eksiği (≤ 10 plan)
                                                    → BLOK_PLANI.json (bloklar KESIT-1, KESIT-2 …; kesit.planlar, kesit.kapsama)
  python blok_plani.py --pilot-karar --film <film>  A14a sonu: PILOT kararları (istem biçimi, take, canlı bekleme, ses yolu) → _RAPOR/PILOT_FILM.json
  python blok_plani.py --imza --film <film>         Memmet'in --onizleme imzası (kesin bütçe BUT2 yoksa boş, çıkış 1)
  python blok_plani.py --durum --film <film> [--json]   bloklar, bitenler, bekleyenler
Kodda (memmet.py, memmet_topla.py): onizleme_imza(film) · animatik_onayli(film) · blok_bul(film, "B03"|"sonraki"|"BLOK_PLANI.json#B03")
  · uygun_mu(film, plan, planlar, tur, blok_nolar, isler) · gonderim_gorselleri(...) · deneme_sayisi(film, no, tur) · acik_gonderimler(film)
  · flow_raporu(film, blok, ozet, planlar) · bitti_isaretle(film, blok, ozet) · plan_imza(plan)

Uygunluk (bir plan şu an gönderilebilir mi; memmet.py her gönderimden önce yeniden sorar):
  1. uretim.saglayici flow (ya da boş); uretim.kaynak_klip yok (klip başka plandan kesilir: üretilmez); video henüz yok ya da onaylı yeniden çekim.
  2. Başlangıç görseli SIRALI_GORSEL/NNN.jpg var, G1 GEÇ ve sha1'i G1 kaydıyla aynı (değişmişse bayat).
  3. son_kare zincirinde kaynak aynı blokta değil, kaynak klip V1 + V2 + V3 GEÇ (KUNYE kapilar), zincir karesi çıkarılmış ve G1Z GEÇ
     (uretim.zincir.g1z, kare_sha1); derinlik ≤ zincir_derinlik_max. bitis_sabit'te bitiş görseli var ve G1 GEÇ.
  4. Plan soyu ≤ 3 deneme (KREDI_DEFTERI gönderim satırları); toplanmamış gönderim yok (önce memmet_topla).
Blok: önce KRİTİK yeniden çekimler (KUYRUK/YENIDEN_URET.json açık video maddeleri), sonra hikâye sırası (sira); sahne grubu sınırında,
  blok 17 planı geçtiyse blok kesilir; zincir ardılı kaynağı geçince SONRAKİ blok planında girer (bagimli_bekleyen).
Flow kilidi (FLOW_KILIDI.json) varken: yalnız FILM_AYAR izinler.flow_kilitliyken_vertex açık VE usd_tavan_film > 0 ise kalan planlar
  veo_vertex sağlayıcısıyla bloklanır (Flow'a gönderim 0; her Vertex çağrısı BUTK'dan geçer). Yoksa blok yazılmaz ve 7 (KISIT).
  Vertex'e kendiliğinden geçiş yoktur (D-03, D-41).
Çıkış kodları: 0 tamam · 1 HATA (girdi yok, kesin bütçe yok) · 4 SAHNELER v1 · 7 Flow kilitli (izin yok).
"""
import os, sys, json, glob, time, hashlib, shutil
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "blok_plani 1.0"
BLOK_MAX = 20                       # UM2 §4.2.4 (blok ≤ 20 plan)
SAHNE_SINIR_PAYI = 3                # sahne grubu sınırına 3 plandan yakınsa blok sınırda kesilir (tahmin; UM2)
SOY_MAX = 3                         # §1.5, D-31: plan soyu başına toplam deneme ≤ 3 (kuyruk.SOY_MAX ile aynı)
KESIT_SURE_SN = 180                 # D-17: P0 + P1'in başı ≈ 180 sn (hesap; tahmin)
KESIT_EK_MAX = 10                   # D-17: kapsama eksikse P1'den en çok 10 plan
KAPSAMA = {"son_kare": 3, "bitis_sabit": 3, "iki_kisi": 4, "el_nesne": 3, "konusmali": 3, "yaratik": 2, "dusuk_isik": 2, "profil_sirt": 2}
COZULMUS = ("indirildi", "iade", "filtre_red", "hata", "kayip", "reddedildi")   # MEMMET_DURUM isler: artık bekleyen olmayanlar
KILITLI, HATA, ORTAM = 7, 1, 4


class Hata(Exception):
    def __init__(self, msg, kod=HATA): super().__init__(msg); self.kod = kod


# ---------------------------------------------------------------- küçük yardımcılar
def _yol(film, *p): return os.path.join(film, *p)
def _j(film, *p): return ortak.json_oku(_yol(film, *p), None)


def sha1_dosya(yol):
    h = hashlib.sha1()
    with open(yol, "rb") as f:
        for parca in iter(lambda: f.read(1 << 20), b""): h.update(parca)
    return h.hexdigest()


def plan_imza(p):
    """film.py plan_imzalari ile aynı: üretim alanları (_uretim, uretim, durum) imzaya girmez."""
    temiz = {k: v for k, v in p.items() if k not in ("_uretim", "uretim", "durum")}
    return hashlib.sha1(json.dumps(temiz, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def film_klasoru(film):
    if os.path.isdir(film): return os.path.abspath(film)
    p = os.path.join(ortak.yollar()["filmler"], film)
    if os.path.isdir(p): return p
    raise Hata(f"film klasörü yok: {film}")


def sahneler(film):
    doc = _j(film, "SAHNELER.json")
    if not isinstance(doc, dict): raise Hata("SAHNELER.json yok ya da bozuk")
    if int(doc.get("_surum", 1) or 1) < 2: raise Hata("SAHNELER.json v1: blok planı v2 ister (Memmet v1 eski hatta kalır)", ORTAM)
    return doc


def planlar_sozluk(doc): return {int(p["no"]): p for p in doc.get("sahneler") or [] if isinstance(p.get("no"), (int, float))}


def onizleme_imza(film):
    """Kesin bütçenin (BUT2; URETIM_ONIZLEME.json taslak: false) imzası. Taslaksa ya da yoksa None: Memmet gönderim yapmaz."""
    on = _j(film, "URETIM_ONIZLEME.json")
    if not isinstance(on, dict) or on.get("taslak") is not False or not isinstance(on.get("butce"), dict): return None
    return hashlib.sha1(json.dumps(on, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:12]


def animatik_onayli(film):
    d = _j(film, "FILM_DURUM.json") or {}
    return ((d.get("animatik") or {}).get("durum") == "ONAYLI")


# ---------------------------------------------------------------- bloklar ve işaretler
def isaret_yolu(film, blok): return _yol(film, "KUNYE", f"BLOK_{'HEPSI' if blok == '*' else blok}.bitti")
def blok_bitti_mi(film, blok): return os.path.exists(isaret_yolu(film, blok))


def blok_bul(film, spec):
    """(BLOK_PLANI, blok). spec: "B03" · "sonraki" (bitmemiş ilk Flow bloğu) · "<yol>#B03" · "<yol>" (sonraki)."""
    spec = str(spec or "sonraki"); yol, _, no = spec.partition("#")
    if not no and not yol.lower().endswith(".json"): yol, no = "", yol
    yol = yol or _yol(film, "BLOK_PLANI.json")
    if not os.path.isabs(yol) and not os.path.exists(yol): yol = _yol(film, yol)
    BP = ortak.json_oku(yol, None)
    if not isinstance(BP, dict): raise ValueError(f"BLOK_PLANI yok ya da bozuk: {yol} (önce blok_plani.py)")
    bl = [b for b in BP.get("bloklar") or [] if isinstance(b, dict)]
    if not no or no == "sonraki":
        b = next((b for b in bl if (b.get("saglayici") or "flow") == "flow" and not blok_bitti_mi(film, b.get("id"))), None)
        if b is None: raise ValueError("Gönderilecek Flow bloğu yok (hepsi bitti ya da blok yok).")
        return BP, b
    b = next((b for b in bl if str(b.get("id")) == no or str(b.get("no")) == no.lstrip("B").lstrip("0") or str(b.get("no")) == no), None)
    if b is None: raise ValueError(f"BLOK_PLANI'nda {no} bloğu yok.")
    return BP, b


def _eskiye(film, yol):
    if os.path.exists(yol):
        h = _yol(film, "_ESKI", time.strftime("%Y%m%d_%H%M%S_") + os.path.basename(yol)); os.makedirs(os.path.dirname(h), exist_ok=True)
        shutil.move(yol, h)


def bitti_isaretle(film, blok, ozet=None):
    """KUNYE/BLOK_<id>.bitti (film.py bekle --blok bunu yoklar). KESIT-* hepsi bitince BLOK_KESIT.bitti; bütün Flow blokları
    bitince BLOK_HEPSI.bitti. Reddedilen/atlanan planlar yüzünden film.py sonsuza dek beklemez."""
    ortak.atomik_yaz(isaret_yolu(film, blok), {"blok": blok, "zaman": time.strftime("%Y-%m-%d %H:%M:%S"), "ozet": ozet or {}})
    BP = _j(film, "BLOK_PLANI.json") or {}
    flow = [str(b.get("id")) for b in BP.get("bloklar") or [] if (b.get("saglayici") or "flow") == "flow"]
    kesit = [b for b in flow if b.startswith("KESIT-")]
    if kesit and all(blok_bitti_mi(film, b) for b in kesit): ortak.atomik_yaz(isaret_yolu(film, "KESIT"), {"bloklar": kesit})
    if flow and all(blok_bitti_mi(film, b) for b in flow): ortak.atomik_yaz(isaret_yolu(film, "*"), {"bloklar": flow})


# ---------------------------------------------------------------- gönderim geçmişi (kredi defteri + Memmet işleri)
def _defter(film):
    import kredi
    return kredi.defter_oku(film)[0]


def isler_oku(film): return ((_j(film, "MEMMET_DURUM.json") or {}).get("isler") or {})


def _tur(s): return s.get("tur") or "video"


def deneme_sayisi(film, no, tur="video", satirlar=None):
    """Plan soyunun Flow deneme sayısı: gönderim satırları − iade edilenler."""
    satirlar = _defter(film) if satirlar is None else satirlar
    iade = {s.get("is_kimligi") for s in satirlar if s.get("olay") == "iade"}
    return sum(1 for s in satirlar if s.get("olay") == "gonderim" and s.get("plan") == no and _tur(s) == tur
               and s.get("saglayici") in (None, "flow") and s.get("is_kimligi") not in iade)


def acik_gonderimler(film, isler=None, satirlar=None):
    """Gönderilmiş ama ne indirilmiş ne çözülmüş işler: {is_kimligi: {plan, tur, istem?, durum}}. memmet_topla bunları toplar."""
    satirlar = _defter(film) if satirlar is None else satirlar; isler = isler_oku(film) if isler is None else isler
    iade = {s.get("is_kimligi") for s in satirlar if s.get("olay") == "iade"}
    out = {}
    for s in satirlar:
        k = s.get("is_kimligi")
        if s.get("olay") != "gonderim" or not k or k in iade or s.get("saglayici") not in (None, "flow"): continue
        d = isler.get(k) or {}
        if d.get("durum") in COZULMUS: continue
        ku = _j(film, "KUNYE", f"{int(s.get('plan') or 0):03d}.json") or {}
        if ku.get("is") == k: continue
        out[k] = {"plan": s.get("plan"), "tur": _tur(s), "istem": d.get("istem"), "durum": d.get("durum") or "gonderildi", "blok": s.get("blok")}
    return out


# ---------------------------------------------------------------- uygunluk
def _g1(p):
    d = (p.get("denetim") or {}).get("G1") or {}
    sha = d.get("sha1") or ((p.get("uretim") or {}).get("gorsel") or {}).get("sha1")
    return d.get("sonuc"), sha


def _sha_tutar(yol, kayit):
    if not kayit or not os.path.exists(yol): return False
    k = str(kayit).lower(); return len(k) >= 8 and sha1_dosya(yol).startswith(k)


def kunye_kapilari(film, no): return ((_j(film, "KUNYE", f"{int(no):03d}.json") or {}).get("kapilar") or {})


def _esik(ad, varsayilan):
    try:
        import esikler; v = esikler.yukle().get(ad); return varsayilan if v is None else v
    except Exception: return varsayilan


def uygun_mu(film, p, planlar, tur="video", blok_nolar=(), isler=None, yeniden=False, satirlar=None):
    """(uygun, neden). neden "zincir…" ile başlıyorsa plan zincir kaynağını bekliyor (bagimli)."""
    u = p.get("uretim") or {}; no = int(p["no"])
    if u.get("kaynak_klip") or p.get("kaynak_klip"): return False, "kaynak_klip (klip başka plandan kesilir; üretilmez)"
    sg = u.get("saglayici") or "flow"
    if sg != "flow": return False, f"sağlayıcı {sg} (Flow değil)"
    satirlar = _defter(film) if satirlar is None else satirlar
    if deneme_sayisi(film, no, tur, satirlar) >= SOY_MAX: return False, f"soy tavanı ({SOY_MAX} deneme): yonetmen·onarim"
    acik = [k for k, v in acik_gonderimler(film, isler, satirlar).items() if v["plan"] == no and v["tur"] == tur]
    if acik: return False, f"toplanmamış gönderim var ({acik[0]}): önce memmet_topla"
    if tur != "video": return True, None
    if os.path.exists(_yol(film, "SIRALI_VIDEO", f"{no:03d}.mp4")) and not yeniden: return False, "video var (yeniden çekim kuyruktan gelir)"
    bas = _yol(film, "SIRALI_GORSEL", f"{no:03d}.jpg")
    if not os.path.exists(bas): return False, "başlangıç görseli yok"
    z = u.get("zincir") or {}; yontem = z.get("yontem") or "bagimsiz"
    if yontem == "son_kare":
        k = z.get("kaynak")
        if k is None: return False, "zincir kaynağı yazılmamış (kare_zinciri --plan)"
        k = int(k)
        if k in set(blok_nolar): return False, f"zincir kaynağı {k} aynı blokta: ardıl sonraki blokta"
        if int(z.get("derinlik") or 1) > int(_esik("zincir_derinlik_max", 2)): return False, "zincir derinliği aşıldı: yeniden demirleme"
        kap = kunye_kapilari(film, k)
        eksik = [g for g in ("V1", "V2", "V3") if (kap.get(g) or {}).get("sonuc") != "GEC"]
        if eksik: return False, f"zincir kaynağı {k} hazır değil ({'/'.join(eksik)} GEÇ değil)"
        if (z.get("g1z") or {}).get("sonuc") != "GEC": return False, f"zincir karesi G1Z GEÇ değil (kaynak {k})"
        if not _sha_tutar(bas, (z.get("g1z") or {}).get("sha1") or z.get("kare_sha1")): return False, "zincir karesi sha1 tutmuyor (bayat)"
        return True, None
    s, sha = _g1(p)
    if s != "GEC": return False, "G1 GEÇ değil"
    if not _sha_tutar(bas, sha): return False, "başlangıç görseli G1 kaydından farklı ya da sha1 kaydı yok (bayat)"
    if yontem == "bitis_sabit":
        bg = str(z.get("bitis_gorsel") or "")
        bn = int(bg.split(":")[1]) if bg.startswith("plan:") else None
        if bn is None or not os.path.exists(_yol(film, "SIRALI_GORSEL", f"{bn:03d}.jpg")): return False, "bitiş görseli yok"
        bp = planlar.get(bn)
        if bp is not None and bn != no:
            s2, sha2 = _g1(bp)
            if s2 != "GEC" or not _sha_tutar(_yol(film, "SIRALI_GORSEL", f"{bn:03d}.jpg"), sha2): return False, "bitiş görseli G1 GEÇ değil"
    return True, None


def gonderim_gorselleri(film, p, doc, tur, ayr=None):
    """Isteme eklenecek görseller: [{yol, ad (sha'lı), sha, yuva}] ya da None (eksik). video: Başlat (+ Bitir); gorsel: Referans."""
    ayr = ayr or {}; no = int(p["no"]); out = []
    def ekle(yol, yuva):
        if not os.path.exists(yol): return False
        sha = sha1_dosya(yol); kok = os.path.splitext(os.path.basename(yol))[0]
        out.append({"yol": yol, "ad": f"{kok}_{sha[:8]}{os.path.splitext(yol)[1] or '.jpg'}", "sha": sha, "yuva": yuva}); return True
    if tur == "video":
        if not ekle(_yol(film, "SIRALI_GORSEL", f"{no:03d}.jpg"), "Başlat"): return None
        z = ((p.get("uretim") or {}).get("zincir") or {})
        bg = str(z.get("bitis_gorsel") or "")
        if (z.get("yontem") == "bitis_sabit") and bg.startswith("plan:"):
            if not ekle(_yol(film, "SIRALI_GORSEL", f"{int(bg.split(':')[1]):03d}.jpg"), "Bitir"): return None
        return out
    for r in p.get("referans") or []:
        ref = ((doc.get("karakterler") or {}).get(r) or {}).get("ref")
        if not ref or not ekle(_yol(film, ref), "Referans"): return None
    for e in ayr.get("ek_referans") or []:
        if not ekle(_yol(film, e), "Referans"): return None
    return out


# ---------------------------------------------------------------- FLOW raporu (Memmet blok sonu)
def flow_raporu(film, blok, o, planlar, gorev=None):
    import kapi
    olc = [{"madde": "indirildi", "plan": int(n), "seviye": "GEC"} for n in o.get("indirilen") or []]
    for r in o.get("reddedilen") or []:
        olc.append({"madde": "filtre_red", "plan": int(r["plan"]), "seviye": "HATA", "yedek_denendi": r.get("yedek_denendi"),
                    "kanit": r.get("flow"), "oneri": "yonetmen·onarim (filtre reddi kipi); aynı istem yeniden gönderilmez"})
    for h in o.get("hata") or []:
        olc.append({"madde": h.get("neden") or "flow_hata", "plan": int(h["plan"]), "seviye": "BAYRAK", "kanit": h.get("flow"),
                    "oneri": "blok_plani sonraki blokta yeniden değerlendirir (soy ≤ 3)"})
    for n in o.get("zaman_asimi") or []:
        olc.append({"madde": "zaman_asimi", "plan": int(n), "seviye": "BAYRAK", "oneri": "memmet_topla (yeni gönderim yok)"})
    for a in o.get("atlanan") or []:
        if str(a.get("neden", "")).startswith("kaynak_klip"): continue
        olc.append({"madde": "atlandi", "plan": int(a["plan"]), "seviye": "BAYRAK", "neden": a.get("neden")})
    asama = "A14a" if str(blok).startswith("KESIT") else "A14"
    return kapi.kaydet(_yol(film, "_RAPOR"), "FLOW", str(blok), olc, asama=asama, gorev=os.path.basename(gorev) if gorev else None,
                       arac_surum="memmet 2.0", birimler=[int(n) for n in planlar], ek={"blok": blok, "dur": bool(o.get("dur"))})


# ---------------------------------------------------------------- plan kurma
def _sira(p): return (float(p.get("sira", p["no"])), int(p["no"]))
def _sahne(p): return ((p.get("zanaat") or {}).get("sahne_grubu")) or str(p.get("sahne") or p.get("parti"))


def _ayar():
    try: return ortak.json_oku(os.path.join(ortak.yollar()["ayarlar"], "FILM_AYAR.json"), {}) or {}
    except ortak.YolYok: return {}


def vertex_izni(ayar=None):
    """(izin, neden). Flow kilitliyken Vertex yalnız iki şartla: izinler.flow_kilitliyken_vertex VE usd_tavan_film > 0 (D-03)."""
    import kredi
    ayar = _ayar() if ayar is None else ayar
    izin = bool((ayar.get("izinler") or {}).get("flow_kilitliyken_vertex"))
    usd = kredi.tavanlar(ayar)[0]["usd_tavan_film"]
    if not izin: return False, "izinler.flow_kilitliyken_vertex kapalı (IZINLER.bat)"
    if not (isinstance(usd, (int, float)) and usd > 0): return False, "usd_tavan_film 0"
    return True, None


def _kuyruk_videolari(film):
    try:
        import kuyruk
        return [m for m in kuyruk.acik_maddeler(film) if m.get("tur") == "video" and isinstance(m.get("plan"), int)]
    except Exception: return []


def _bloklara_bol(adaylar, planlar, ilk_no, onek="B"):
    bloklar, cur, son_sahne = [], [], None
    def kapat():
        if cur: bloklar.append(cur[:]); cur.clear()
    for no in adaylar:
        sh = _sahne(planlar[no])
        if cur and (len(cur) >= BLOK_MAX or (sh != son_sahne and len(cur) >= BLOK_MAX - SAHNE_SINIR_PAYI)): kapat()
        cur.append(no); son_sahne = sh
    kapat()
    return [{"id": f"{onek}{ilk_no + i:02d}" if onek == "B" else f"KESIT-{ilk_no + i}", "no": ilk_no + i, "planlar": b} for i, b in enumerate(bloklar)]


def _sonraki_no(eski, onek):
    nos = [int(b.get("no") or 0) for b in eski if str(b.get("id", "")).startswith(onek)]
    return (max(nos) + 1) if nos else 1


def _ozellikler(p, doc):
    """Kesit kapsama kategorileri (D-17)."""
    z = p.get("zanaat") or {}; u = p.get("uretim") or {}; out = set()
    yontem = (u.get("zincir") or {}).get("yontem") or ("bitis_sabit" if (z.get("zincir") or {}).get("bitis_sabitle") else None)
    if yontem == "son_kare" or (z.get("zincir") or {}).get("gecis_turu") == "devam": out.add("son_kare")
    if yontem == "bitis_sabit": out.add("bitis_sabit")
    kd = z.get("kadrajdakiler") or []
    if len(kd) >= 2: out.add("iki_kisi")
    if p.get("replik") or any(a.get("tur") == "konusma" for a in z.get("eylem_zinciri") or []): out.add("konusmali")
    if any(a.get("hedef") or a.get("fiil") in ("tutar", "kavrar", "alir_eline", "uzatir") or (a.get("etki") or {}).get("eller")
           for a in z.get("eylem_zinciri") or [] if a.get("tur") == "fiziksel"): out.add("el_nesne")
    kar = doc.get("karakterler") or {}
    if any((kar.get(k.get("id")) or {}).get("tur") in ("yaratik", "hayvan") or k.get("tur") == "yaratik" for k in kd): out.add("yaratik")
    if any(str(k.get("yuz_acisi")) in ("profil", "sirt", "arka") for k in kd): out.add("profil_sirt")
    sg = (doc.get("sahne_gruplari") or {}).get(z.get("sahne_grubu")) or {}
    if (sg.get("zaman") or {}).get("gun_saati") in ("gece", "alacakaranlik", "aksam"): out.add("dusuk_isik")
    return out


def _sure(p):
    d = p.get("_derlenir") or {}; k = p.get("kullanim") or {}
    return float(d.get("sure_sn") or k.get("sure") or (p.get("zanaat") or {}).get("klip_sn") or 8)


def kesit_sec(doc):
    """D-17: P0 + P1'in başı (≈ KESIT_SURE_SN) + kapsama eksiği için P1'den ≤ KESIT_EK_MAX plan. (planlar, kapsama, eksik)."""
    pl = sorted((p for p in doc.get("sahneler") or [] if isinstance(p.get("no"), (int, float))), key=_sira)
    sec, toplam = [], 0.0
    for p in pl:
        parti = p.get("parti", 1)
        if parti == 0: sec.append(p); toplam += _sure(p); continue
        if parti == 1 and toplam < KESIT_SURE_SN: sec.append(p); toplam += _sure(p)
    kap = {k: 0 for k in KAPSAMA}
    for p in sec:
        for o in _ozellikler(p, doc): kap[o] += 1
    ek = 0; secili = {int(p["no"]) for p in sec}
    for p in pl:
        if ek >= KESIT_EK_MAX: break
        if p.get("parti", 1) != 1 or int(p["no"]) in secili: continue
        katki = [o for o in _ozellikler(p, doc) if kap[o] < KAPSAMA[o]]
        if not katki: continue
        sec.append(p); secili.add(int(p["no"])); ek += 1
        for o in _ozellikler(p, doc): kap[o] += 1
    eksik = {k: KAPSAMA[k] - v for k, v in kap.items() if v < KAPSAMA[k]}
    return sorted(secili, key=lambda n: _sira(next(p for p in pl if int(p["no"]) == n))), kap, eksik


def plan_kur(film, kesit=False, ayar=None, simdi=None, hesap_kok=None):
    """BLOK_PLANI.json'u kurar ve yazar. (BLOK_PLANI, çıkış kodu)."""
    import flow_yuk
    doc = sahneler(film); planlar = planlar_sozluk(doc)
    imza = onizleme_imza(film)
    if not imza: raise Hata("kesin bütçe yok (URETIM_ONIZLEME.json taslak): önce kredi.py but2 (sıra kuralı 1)")
    eski = _j(film, "BLOK_PLANI.json") or {}
    gecmis = [b for b in eski.get("bloklar") or [] if blok_bitti_mi(film, b.get("id"))]
    satirlar = _defter(film); isler = isler_oku(film)
    kuyruk_m = {m["plan"]: m for m in _kuyruk_videolari(film)}
    if kesit:
        secim, kap, eksik = kesit_sec(doc); hedef = secim
    else:
        kritik = sorted((n for n, m in kuyruk_m.items() if str(m.get("seviye", "")).upper().startswith("KR")), key=lambda n: _sira(planlar[n]))
        hedef = kritik + [n for n in sorted(planlar, key=lambda n: _sira(planlar[n])) if n not in kritik]
    adaylar, bagimli, engelli, ayrinti = [], {}, {}, {}
    for no in hedef:
        p = planlar.get(no)
        if p is None: continue
        yeniden = no in kuyruk_m
        if os.path.exists(_yol(film, "SIRALI_VIDEO", f"{no:03d}.mp4")) and not yeniden: continue
        ok, neden = uygun_mu(film, p, planlar, "video", (), isler, yeniden=yeniden, satirlar=satirlar)
        if ok:
            adaylar.append(no)
            if yeniden: ayrinti[str(no)] = {"madde": kuyruk_m[no].get("id"), "dilim": kuyruk_m[no].get("dilim") or "goruntu",
                                            "seviye": kuyruk_m[no].get("seviye")}
        elif neden.startswith("zincir") or "zincir kaynağı" in neden: bagimli[str(no)] = neden
        elif not neden.startswith("kaynak_klip"): engelli[str(no)] = neden
    onek = "KESIT" if kesit else "B"
    yeni = _bloklara_bol(adaylar, planlar, _sonraki_no(gecmis, onek), onek)
    kilit = flow_yuk.kilit_durumu(kok=hesap_kok, simdi=simdi); kod = 0; kilit_bilgi = None
    if kilit["kilitli"]:
        izin, neden = vertex_izni(ayar)
        kilit_bilgi = {"kilitli": True, "neden": kilit.get("neden"), "en_erken": kilit.get("en_erken_metin"), "vertex": izin, "vertex_neden": neden}
        if izin:
            for b in yeni: b.update(saglayici="veo_vertex", butk="her_cagri", not_="Flow kilitli: Vertex izinli (D-03); Flow'a gönderim 0")
        else:
            yeni = []; kod = KILITLI
    else:
        for b in yeni: b["saglayici"] = "flow"
    for b in yeni:
        b["ayrinti"] = {k: v for k, v in ayrinti.items() if int(k) in b["planlar"]}
        if "not_" in b: b["not"] = b.pop("not_")
    BP = {"_surum": 1, "_uretim": {"asama": "A14a" if kesit else "A14", "gorev": os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None,
                                   "girdi_imza": imza, "arac_surum": SURUM, "esik_surum": None, "sonuc": "GEC" if kod == 0 else "HATA",
                                   "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"), "ortam": "yerel" if os.name == "nt" else "bulut"},
          "onizleme_imza": imza, "bloklar": gecmis + yeni, "uygun_bekleyen": [], "bagimli_bekleyen": bagimli, "engelli": engelli,
          "flow_kilidi": kilit_bilgi}
    if kesit: BP["kesit"] = {"planlar": hedef, "kapsama": kap, "eksik": eksik, "sure_hedef_sn": KESIT_SURE_SN}
    elif eski.get("kesit"): BP["kesit"] = eski["kesit"]
    if yeni:
        _eskiye(film, isaret_yolu(film, "*"))
        if kesit: _eskiye(film, isaret_yolu(film, "KESIT"))
    ortak.atomik_yaz(_yol(film, "BLOK_PLANI.json"), BP)
    if not yeni and kod == 0:
        flow = [str(b.get("id")) for b in BP["bloklar"] if (b.get("saglayici") or "flow") == "flow"]
        if all(blok_bitti_mi(film, b) for b in flow):       # gönderilecek bir şey yok: bekleme yaratılmaz
            ortak.atomik_yaz(isaret_yolu(film, "*"), {"bloklar": flow, "not": "uygun plan yok"})
            if kesit: ortak.atomik_yaz(isaret_yolu(film, "KESIT"), {"bloklar": [b for b in flow if b.startswith("KESIT-")], "not": "uygun plan yok"})
    return BP, kod


# ---------------------------------------------------------------- pilot kararı (A14a sonu)
PILOT_VARSAYILAN = {"istem_bicimi": "aralik", "bitis_bekleme": "holds still", "take": "kapali", "canli_bekleme": "kapali",
                    "ses_yolu": "veo_donustur", "son_kare_referansi": "yok"}


def pilot_karar(film, gorev=None):
    import kapi
    BP = _j(film, "BLOK_PLANI.json") or {}; kes = (BP.get("kesit") or {}).get("planlar") or []
    olc = []
    for n in kes:
        olc.append({"madde": "klip", "plan": int(n), "seviye": "GEC" if os.path.exists(_yol(film, "KUNYE", f"{int(n):03d}.json")) else "BAYRAK",
                    **({} if os.path.exists(_yol(film, "KUNYE", f"{int(n):03d}.json")) else {"neden": "üretilmedi (red, soy ya da bekleyen)"})})
    rk = _yol(film, "_RAPOR")
    for g in ("V1", "V2", "V3", "G1Z", "HS_KESIT"):
        rs = [r for _, r in kapi.raporlar(rk, g) if str(r.get("kapsam", "")).startswith("KESIT") or g == "HS_KESIT"] if os.path.isdir(rk) else []
        if not rs: olc.append({"madde": f"{g}_raporu", "seviye": "OLCULEMEDI", "neden": "rapor yok"}); continue
        s = rs[-1].get("sonuc")
        olc.append({"madde": f"{g}_sonuc", "seviye": "HATA" if s in ("HATA", "KISMI") else ("BAYRAK" if s == "BAYRAK" else "GEC"), "olcu": s})
    ders = (_j(film, "_RAPOR", "PILOT_DERS.json") or {}).get("kararlar") or {}
    kararlar = {}
    for k, v in PILOT_VARSAYILAN.items():
        if ders.get(k) is not None: kararlar[k] = {"deger": ders[k], "kaynak": "PILOT_DERS"}
        else:
            kararlar[k] = {"deger": v, "kaynak": "olculemedi → varsayilan"}
            olc.append({"madde": f"karar_{k}", "seviye": "OLCULEMEDI", "neden": "ölçüm yok → varsayılan (karar defterine)"})
    yol, r = kapi.kaydet(rk, "PILOT", "FILM", olc, asama="A14a", gorev=gorev, arac_surum=SURUM, birimler=[int(n) for n in kes],
                         ek={"kararlar": kararlar, "kesit_planlar": kes})
    return r


# ---------------------------------------------------------------- komut satırı
def main(argv):
    if not argv or argv[0] in ("-h", "--help"): print(__doc__); return 0
    film = argv[argv.index("--film") + 1] if "--film" in argv and argv.index("--film") + 1 < len(argv) else \
        next((a for a in argv if not a.startswith("--")), None)
    if not film: print(__doc__); return HATA
    try:
        film = film_klasoru(film)
        if "--imza" in argv:
            i = onizleme_imza(film); print(i or ""); return 0 if i else HATA
        if "--pilot-karar" in argv:
            r = pilot_karar(film, os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None)
            print(f"PILOT: {r['sonuc']} · kararlar: " + ", ".join(f"{k}={v['deger']}" for k, v in r["kararlar"].items())); return 0
        if "--durum" in argv:
            BP = _j(film, "BLOK_PLANI.json") or {}
            d = {"bloklar": [{"id": b.get("id"), "plan": len(b.get("planlar") or []), "saglayici": b.get("saglayici"),
                              "bitti": blok_bitti_mi(film, b.get("id"))} for b in BP.get("bloklar") or []],
                 "bagimli": BP.get("bagimli_bekleyen"), "engelli": BP.get("engelli"), "acik_gonderim": acik_gonderimler(film)}
            print(json.dumps(d, ensure_ascii=False, indent=1) if "--json" in argv else
                  "\n".join(f"{b['id']}: {b['plan']} plan · {b['saglayici']} · {'bitti' if b['bitti'] else 'bekliyor'}" for b in d["bloklar"]) or "blok yok")
            return 0
        BP, kod = plan_kur(film, kesit="--kesit" in argv)
    except Hata as e:
        print("HATA:", e); return e.kod
    yeni = [b for b in BP["bloklar"] if not blok_bitti_mi(film, b.get("id"))]
    print(f"BLOK_PLANI: {len(yeni)} yeni blok ({', '.join(b['id'] + ':' + str(len(b['planlar'])) for b in yeni) or '-'}) · "
          f"zincir bekleyen {len(BP['bagimli_bekleyen'])} · engelli {len(BP['engelli'])}")
    if kod == KILITLI:
        print("Flow kilitli ve Vertex izni yok: video bekler. Vertex'e kendiliğinden geçilmez (D-03).")
    return kod


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
