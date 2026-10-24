"""DERS DEFTERİ — olay başına ham ders kaydı ve öğrenilen kuralların korkuluğu (TASARIM D-33, §5.3, §7.1).

Kullanım:
  python ders_defteri.py --denetle [KURALLAR_OGRENILEN.json]     öğrenilen kuralları korkuluktan geçirir (HATA varsa çıkış 1)
  python ders_defteri.py --yedekle [--hedef <yedek kökü>]     ders defteri → <yedek>/DERSLER/ (ders_yedekle.py; yalnız kopya)
  python ders_defteri.py --kaydet --olay arac_hatasi --kaynak ajan --belirti "..." [--film F] [--asama A11] [--kapi G1] [--plan 12]
Kodda:  import ders_defteri as dd
  dd.kaydet("kapi_hatasi", kaynak="kapi", belirti="...", film="EMBERFALL_F2", asama="A11", kapi="G1", plan=214, ...)  → dosya yolu
  dd.sonuc_yaz("D-20261103-0042", "duzeldi") · dd.korkuluk(kural) → HATA listesi · dd.kural_ekle(kural) · dd.ogrenilen_yaz(veri)
Yerler (veri kökünde; git deposu değil):
  <veri>/BILGI/DERSLER/ham/<YYYYmmddTHHMMSS>_<film>_<olay>.json   her olay ayrı dosya (_surum + kendi zaman/ortam alanları)
  <veri>/BILGI/KURALLAR_OGRENILEN.json                            {_surum: 3, _uretim, kurallar: [...]}; esikler.py okur
Korkuluklar (öğrenmeyle gevşemez; §5.3):
  - tempo yalnız yavaşlatır, flow_tavan yalnız düşürür, esik yalnız sıkılaştırır (esikler.sikilastir ile denetlenir; gevşeten, değişmez
    anahtarı değiştiren ya da yönü bilinmeyen kural HATA). Kalibrasyonlu gevşetme bu katmanda yapılmaz (eşik dosyasında, ders terfisiyle).
  - aktif esik kuralı için yanlış alarm oranı ölçülmüş ve ≤ 0,30 olmalı (ÖLÇÜLEMEDİ geçmez); SFace HATA eşiği 0,363'ün altına inmez.
  - aktif tempo / flow_tavan / gevsetilemez esik kuralı sonradan silinemez, pasife ya da denemeye alınamaz, değeri gevşetilemez.
  - bot, uyarı, hesap, gizli bilgi, onay ve silme kurallarına dokunan işlem kuralı HATA; kuralda ve ham kayıtta gizli bilgi olmaz
    (e-posta ve anahtar benzeri metin kayıtta maskelenir, kuralda HATA).
"""
import os, sys, re, json, copy, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, esikler

SURUM = "ders_defteri 1.0"
HAM_SURUM, OGRENILEN_SURUM = 1, 3
OLAYLAR = ("kapi_hatasi", "kapi_bayragi_dogrulandi", "saglayici_red", "saglayici_kisit", "yeniden_cekim", "kullanici_notu",
           "seyirci_bulgusu", "butce_sapmasi", "arac_hatasi", "yanlis_alarm", "kacirma", "pilot_olcumu", "gercek_seyirci")
KAYNAKLAR = ("kapi", "ajan", "kullanici_notu", "gercek_seyirci", "olcum0")
KANIT_AGIRLIK = {"gercek_seyirci": 4, "kullanici_notu": 3, "kapi": 2, "ajan": 1, "olcum0": 2}
SONUCLAR = (None, "duzeldi", "duzelmedi", "plan_degisti")
KURAL_TURLERI = ("filtre_kelimesi", "yasak_fiil", "risk_desen", "esik", "tempo", "flow_tavan", "kredi_payi", "sure_tahmini",
                 "istem_kalibi", "istem_eki", "plan_kurali", "yasak_kalip", "yol_kurali", "kara_liste", "saglayici_notu", "sure_carpani")
DURUMLAR = ("aday", "deneme", "aktif", "pasif")
SAYISAL_TURLER = ("esik", "tempo", "flow_tavan", "kredi_payi")   # esikler.py katmanına giren ya da eşik anahtarına dokunan türler
ISLEM_TURLERI = ("plan_kurali", "yol_kurali", "saglayici_notu")   # metni işlem tarif eden türler: güvenlik konularına dokunamaz
YANLIS_ALARM_MAX = 0.30          # TASARIM D-33, §5.3 (karar metni; eşik dosyası değil)
SFACE_HATA_TABAN = 0.363         # TASARIM §5.3 korkuluğu: SFace HATA eşiği bunun altına inmez (resmî OpenCV eşiği)
KORUNAN_DESEN = [r"yenile", r"\breload", r"\brefresh", r"captcha", r"doğrulama(yı)? (geç|atla|çöz)", r"atlat", r"bypass",
                 r"başka hesap", r"ikinci hesap", r"hesap değiştir", r"hesabı değiştir", r"another account", r"second account",
                 r"switch account", r"uyarı(yı|da|ya)? (yok say|devam|aldırma)", r"ignore (the )?warning", r"hızlandır", r"speed up",
                 r"tempo(yu)? (artır|düşür|kısalt)", r"mola(yı)? (kısalt|atla|kaldır)", r"onaysız", r"onay(ı)? (atla|olmadan|alma)",
                 r"without approval", r"skip approval", r"kalıcı (olarak )?sil", r"\bsil\b", r"\bsilin", r"\bdelete\b", r"rmtree",
                 r"/mir\b", r"gizli bilgi", r"api[_ ]?key", r"şifre", r"parola", r"password", r"\bsecret"]
EPOSTA = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ANAHTAR = re.compile(r"\b(sk-[A-Za-z0-9_-]{16,}|AIza[0-9A-Za-z_-]{20,}|ghp_[A-Za-z0-9]{20,}|xox[abp]-[A-Za-z0-9-]{10,}|\d{8,10}:[A-Za-z0-9_-]{30,})")


class KorkulukHatasi(Exception):
    def __init__(self, hatalar):
        self.hatalar = list(hatalar)
        super().__init__("ders korkuluğu %d HATA:\n  " % len(self.hatalar) + "\n  ".join(self.hatalar))


# ------------------------------------------------------------------ yollar
def bilgi_kok(bilgi=None): return os.path.abspath(bilgi) if bilgi else os.path.join(ortak.yollar()["veri_kok"], "BILGI")
def ham_klasoru(bilgi=None): return os.path.join(bilgi_kok(bilgi), "DERSLER", "ham")
def ogrenilen_yolu(bilgi=None): return os.path.join(bilgi_kok(bilgi), "KURALLAR_OGRENILEN.json")


def ortam_bul(bilgi=None):
    """FILM_AYAR.json 'ortam' varsa o; yoksa Windows 'yerel', diğerleri 'bulut' ([UM2] ortam algılama)."""
    try:
        a = ortak.json_oku(os.path.join(os.path.dirname(bilgi_kok(bilgi)), "AYARLAR", "FILM_AYAR.json"), {}) or {}
        if a.get("ortam") in ("yerel", "bulut"): return a["ortam"]
    except (ortak.YolYok, AttributeError): pass
    return "yerel" if os.name == "nt" else "bulut"


# ------------------------------------------------------------------ gizli bilgi
def _gizle(x):
    if isinstance(x, str): return ANAHTAR.sub("<gizli bilgi gizlendi>", EPOSTA.sub("<e-posta gizlendi>", x))
    if isinstance(x, list): return [_gizle(v) for v in x]
    if isinstance(x, dict): return {k: _gizle(v) for k, v in x.items()}
    return x


def _metinler(x):
    if isinstance(x, str): yield x
    elif isinstance(x, list):
        for v in x: yield from _metinler(v)
    elif isinstance(x, dict):
        for k, v in x.items(): yield str(k); yield from _metinler(v)


# ------------------------------------------------------------------ ham kayıt
def _ad(s): return re.sub(r"[^A-Za-z0-9_-]+", "_", str(s or "GENEL")).strip("_") or "GENEL"


def _sonraki_id(klasor, gun):
    on = f"D-{gun}-"; n = 0
    try: adlar = os.listdir(klasor)
    except OSError: adlar = []
    for a in adlar:
        if not a.endswith(".json"): continue
        i = str((ortak.json_oku(os.path.join(klasor, a), {}) or {}).get("id", ""))
        if i.startswith(on) and i[len(on):].isdigit(): n = max(n, int(i[len(on):]))
    return f"{on}{n + 1:04d}"


def kaydet(olay, kaynak, belirti, film=None, seri=None, asama=None, kapi=None, madde=None, plan=None, kategori=None, rol_etiketi=None,
           olcum=None, baglam=None, kanit=None, eylem=None, sonuc=None, maliyet=None, zaman=None, ortam=None, bilgi=None, **ek):
    """§5.3 ham kaydını <veri>/BILGI/DERSLER/ham/'a yazar (her olay ayrı dosya, üzerine yazılmaz). Yolu döndürür.
    Gizli bilgi (e-posta, anahtar benzeri metin) maskelenir. Geçersiz olay/kaynak/sonuç → ValueError."""
    if olay not in OLAYLAR: raise ValueError(f"olay geçersiz: {olay!r} ({', '.join(OLAYLAR)})")
    if kaynak not in KAYNAKLAR: raise ValueError(f"kaynak geçersiz: {kaynak!r} ({', '.join(KAYNAKLAR)})")
    if not (isinstance(belirti, str) and belirti.strip()): raise ValueError("belirti boş olamaz")
    if sonuc not in SONUCLAR: raise ValueError(f"sonuc geçersiz: {sonuc!r} (duzeldi|duzelmedi|plan_degisti|None)")
    if kanit is not None and not isinstance(kanit, list): kanit = [kanit]
    an = zaman if isinstance(zaman, datetime.datetime) else datetime.datetime.now()
    if an.tzinfo is None: an = an.astimezone()
    klasor = ham_klasoru(bilgi); os.makedirs(klasor, exist_ok=True)
    kayit = {"_surum": HAM_SURUM, "id": _sonraki_id(klasor, an.strftime("%Y%m%d")), "zaman": an.isoformat(timespec="seconds"),
             "film": film, "seri": seri, "ortam": ortam or ortam_bul(bilgi), "olay": olay, "asama": asama, "kapi": kapi, "madde": madde,
             "plan": plan, "kategori": kategori, "rol_etiketi": rol_etiketi, "kaynak": kaynak, "belirti": belirti, "olcum": olcum,
             "baglam": baglam, "kanit": kanit or [], "eylem": eylem, "sonuc": sonuc, "maliyet": maliyet}
    for k, v in ek.items():
        if k not in kayit and not k.startswith("_"): kayit[k] = v
    kayit = _gizle(kayit)
    taban = os.path.join(klasor, f"{an.strftime('%Y%m%dT%H%M%S')}_{_ad(film)}_{olay}"); yol, i = taban + ".json", 1
    while os.path.exists(yol): i += 1; yol = f"{taban}_{i}.json"
    ortak.atomik_yaz(yol, kayit)
    return yol


def ham_oku(bilgi=None):
    klasor = ham_klasoru(bilgi); out = []
    for a in sorted(os.listdir(klasor)) if os.path.isdir(klasor) else []:
        if a.endswith(".json"):
            d = ortak.json_oku(os.path.join(klasor, a), None)
            if isinstance(d, dict): out.append(dict(d, _dosya=a))
    return out


def sonuc_yaz(ders_id, sonuc, bilgi=None):
    """Ham kaydın 'sonuc' alanını sonradan doldurur (duzeldi | duzelmedi | plan_degisti). Yolu döndürür; bulunamazsa KeyError."""
    if sonuc not in SONUCLAR or sonuc is None: raise ValueError(f"sonuc geçersiz: {sonuc!r}")
    for d in ham_oku(bilgi):
        if d.get("id") == ders_id:
            yol = os.path.join(ham_klasoru(bilgi), d.pop("_dosya")); d["sonuc"] = sonuc
            ortak.atomik_yaz(yol, d); return yol
    raise KeyError(ders_id)


# ------------------------------------------------------------------ öğrenilen kurallar: korkuluk
def taban_esikler():
    """Öğrenilen ve FILM_AYAR katmanı olmadan eşikler: yeni kural bunlara göre yalnız sıkılaştırmalı."""
    return esikler.yukle()


def _hedefler(kural):
    """(eşik anahtarı, değer) çiftleri: esikler._ogrenilen_uygula ile aynı eşleme."""
    tur, deger = kural.get("tur"), kural.get("deger")
    if tur == "tempo": return [("flow_tempo_1710", deger)]
    if not isinstance(deger, dict): return None
    if tur == "flow_tavan": return [(esikler.OGRENILEN_AD.get(k, k), v) for k, v in deger.items()]
    return list(deger.items())


def _sface_alti(ad, v):
    if "sface" not in ad.lower(): return False
    sayilar = [x for x in (v if isinstance(v, list) else [v]) if isinstance(x, (int, float)) and not isinstance(x, bool)]
    return any(x < SFACE_HATA_TABAN for x in sayilar)


def korkuluk(kural, E=None):
    """Tek kuralın korkuluk HATA listesi (boş liste = geçti). E verilmezse taban eşikler yüklenir."""
    if not isinstance(kural, dict): return ["kural sözlük değil"]
    kid = kural.get("id") or "?"; h = []
    tur, durum = kural.get("tur"), kural.get("durum")
    if not re.fullmatch(r"OK-\d{4,}", str(kural.get("id", ""))): h.append(f"{kid}: id 'OK-NNNN' biçiminde olmalı")
    if tur not in KURAL_TURLERI: h.append(f"{kid}: tur izinli değil ({tur!r})"); return h
    if durum not in DURUMLAR: h.append(f"{kid}: durum geçersiz ({durum!r}; {'|'.join(DURUMLAR)})")
    if "deger" not in kural: h.append(f"{kid}: deger yok")
    for m in _metinler(kural):
        if EPOSTA.search(m) or ANAHTAR.search(m): h.append(f"{kid}: kuralda gizli bilgi (e-posta/anahtar) var"); break
    if tur in ISLEM_TURLERI:
        metin = " ".join(_metinler({k: v for k, v in kural.items() if k in ("deger", "kapsam", "aciklama", "eylem")})).lower()
        for d in KORUNAN_DESEN:
            if re.search(d, metin):
                h.append(f"{kid}: bot/uyarı/hesap/gizli bilgi/onay/silme kuralına dokunuyor ('{d}'); öğrenmeyle değişmez"); break
    if tur not in SAYISAL_TURLER: return h
    hedef = _hedefler(kural)
    if not hedef: h.append(f"{kid}: {tur} değeri {{anahtar: değer}} sözlüğü olmalı"); return h
    E = E if E is not None else taban_esikler(); siki = 0; aynilar = []
    for ad, v in hedef:
        if _sface_alti(ad, v): h.append(f"{kid}: {ad} SFace HATA eşiği {SFACE_HATA_TABAN}'ün altına inemez")
        r = E.kayit.get(ad)
        if r is None: h.append(f"{kid}: bilinmeyen eşik anahtarı {ad!r}"); continue
        if tur == "flow_tavan" and not r.get("gevsetilemez"): h.append(f"{kid}: {ad} bir Flow güvenlik sınırı değil (flow_tavan)")
        _, notlar = esikler.sikilastir(E[ad], v, esikler.yon_bul(ad, r), ad)
        for yol, esik, gelen, _u, d in notlar:
            if d == "sikilasti": siki += 1; continue
            if d == "ayni": aynilar.append(yol); continue
            ne = {"gevsek": "gevşetiyor (öğrenmeyle gevşemez)", "degismez": "değiştirilemez anahtar",
                  "gecersiz": "geçersiz değer", "yon_bilinmiyor": "yönü bilinmiyor (sıkılaştırma kanıtlanamaz)"}.get(d, d)
            h.append(f"{kid}: {yol}: {ne} (eşik {esik!r}, gelen {gelen!r})")
    if aynilar and not siki: h.append(f"{kid}: {', '.join(aynilar)} eşikle aynı; sıkılaştırmayan kural yazılmaz")
    if tur == "esik" and durum == "aktif":
        ya = kural.get("yanlis_alarm_orani")
        if not isinstance(ya, (int, float)) or isinstance(ya, bool):
            h.append(f"{kid}: aktif eşik kuralında yanlış alarm oranı ölçülmemiş (ÖLÇÜLEMEDİ geçmez)")
        elif ya > YANLIS_ALARM_MAX: h.append(f"{kid}: yanlış alarm {ya} > {YANLIS_ALARM_MAX}; sıkılaştırma reddedilir")
    return h


def _korunan(kural, E):
    """Sonradan geri alınamayan kural: aktif tempo / flow_tavan ya da gevsetilemez anahtara dokunan aktif kural."""
    if not isinstance(kural, dict) or kural.get("durum") != "aktif": return False
    if kural.get("tur") in ("tempo", "flow_tavan"): return True
    if kural.get("tur") in SAYISAL_TURLER:
        return any((E.kayit.get(a) or {}).get("gevsetilemez") for a, _ in (_hedefler(kural) or []))
    return False


def _en_az_onceki_kadar(eski, yeni, yon):
    if isinstance(eski, dict):
        if not isinstance(yeni, dict): return False
        for k, v in eski.items():
            alt = (yon.get(k) if isinstance(yon, dict) else yon)
            if k not in yeni or not _en_az_onceki_kadar(v, yeni[k], alt): return False
        return True
    _, notlar = esikler.sikilastir(eski, yeni, yon)
    return all(n[4] in ("ayni", "sikilasti") for n in notlar)


def ogrenilen_denetle(veri, onceki=None, E=None):
    """KURALLAR_OGRENILEN.json bütün korkulukları: zarf, kural başına korkuluk, tekil id, korunan kuralların geri alınmaması."""
    if not isinstance(veri, dict): return ["KURALLAR_OGRENILEN üst düzey sözlük değil"]
    h = []
    if not isinstance(veri.get("_surum"), int): h.append("_surum yok")
    kurallar = veri.get("kurallar")
    if not isinstance(kurallar, list): return h + ["kurallar listesi yok"]
    E = E if E is not None else taban_esikler(); goruldu = set()
    for k in kurallar:
        kid = k.get("id") if isinstance(k, dict) else None
        if kid in goruldu: h.append(f"{kid}: id iki kez")
        goruldu.add(kid); h += korkuluk(k, E)
    if isinstance(onceki, dict):
        yeni = {k.get("id"): k for k in kurallar if isinstance(k, dict)}
        for o in onceki.get("kurallar") or []:
            if not _korunan(o, E): continue
            n = yeni.get(o["id"])
            if n is None: h.append(f"{o['id']}: aktif güvenlik kuralı silinemez"); continue
            if n.get("durum") != "aktif": h.append(f"{o['id']}: aktif güvenlik kuralı {n.get('durum')!r} durumuna alınamaz"); continue
            if n.get("tur") != o.get("tur"): h.append(f"{o['id']}: kural türü değiştirilemez"); continue
            eh = dict(_hedefler(o) or []); yh = dict(_hedefler(n) or [])
            for a, ev in eh.items():
                if a not in yh or not _en_az_onceki_kadar(ev, yh[a], esikler.yon_bul(a, E.kayit.get(a) or {})):
                    h.append(f"{o['id']}: {a} önceki değerinden gevşek olamaz")
    return h


def ogrenilen_oku(yol=None):
    v = ortak.json_oku(yol or ogrenilen_yolu(), None)
    return v if isinstance(v, dict) else {"_surum": OGRENILEN_SURUM, "kurallar": []}


def ogrenilen_yaz(veri, yol=None, E=None, uretim=None):
    """Korkuluktan geçerse (önceki dosyaya göre de) atomik yazar; geçmezse KorkulukHatasi ve dosya değişmez."""
    yol = yol or ogrenilen_yolu(); E = E if E is not None else taban_esikler()
    onceki = ortak.json_oku(yol, None)
    v = copy.deepcopy(veri); v["_surum"] = OGRENILEN_SURUM
    h = ogrenilen_denetle(v, onceki if isinstance(onceki, dict) else None, E)
    if h: raise KorkulukHatasi(h)
    for k in v["kurallar"]: k["korkuluk"] = "gecti"
    u = dict(v.get("_uretim") or {}); u.update(uretim or {})
    u.update(arac_surum=u.get("arac_surum") or SURUM, sonuc="GEC", zaman=datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
             ortam=u.get("ortam") or ortam_bul(os.path.dirname(os.path.abspath(yol))))
    v["_uretim"] = u
    v = {"_surum": v["_surum"], "_uretim": v["_uretim"], **{k: x for k, x in v.items() if k not in ("_surum", "_uretim")}}
    ortak.atomik_yaz(yol, v)
    return yol


def kural_ekle(kural, yol=None, E=None, uretim=None):
    """Tek kuralı ekler (id yoksa sıradaki OK-NNNN; flow_tavan için 'onceki' ve yon: sikilastir doldurulur). Eklenen kuralı döndürür."""
    yol = yol or ogrenilen_yolu(); E = E if E is not None else taban_esikler()
    v = ogrenilen_oku(yol); kurallar = v.setdefault("kurallar", [])
    k = copy.deepcopy(kural)
    if not k.get("id"):
        n = max([int(x["id"][3:]) for x in kurallar if re.fullmatch(r"OK-\d+", str(x.get("id", "")))] + [0])
        k["id"] = f"OK-{n + 1:04d}"
    if k.get("tur") in ("flow_tavan", "tempo", "esik"):
        k.setdefault("yon", "sikilastir")
        h = _hedefler(k) or []
        if k.get("tur") == "flow_tavan" and len(h) == 1 and h[0][0] in E: k.setdefault("onceki", E[h[0][0]])
    kurallar.append(k)
    ogrenilen_yaz(v, yol, E, uretim)
    return k


# ------------------------------------------------------------------ komut satırı
def main(argv):
    if "--yedekle" in argv:                      # A18: ders defterinin yedeği (yalnız kopya; AYARLAR girmez)
        import ders_yedekle
        return ders_yedekle.main(argv)
    if argv[:1] == ["--denetle"] and len(argv) <= 2:
        try: yol = argv[1] if len(argv) == 2 else ogrenilen_yolu()
        except ortak.YolYok as e: print("!!", e); return 4
        v = ortak.json_oku(yol, None)
        if v is None: print(f"{yol}: yok ya da okunamadı; denetlenecek kural yok."); return 0
        h = ogrenilen_denetle(v)
        for x in h: print("HATA", x)
        print(f"{len((v or {}).get('kurallar') or [])} kural; HATA {len(h)}")
        return 1 if h else 0
    if argv[:1] == ["--kaydet"]:
        a, i = {}, 1
        while i < len(argv):
            if argv[i].startswith("--") and i + 1 < len(argv): a[argv[i][2:]] = argv[i + 1]; i += 2
            else: print(__doc__); return 4
        if "plan" in a and a["plan"].isdigit(): a["plan"] = int(a["plan"])
        try: print(kaydet(a.pop("olay", None), a.pop("kaynak", None), a.pop("belirti", None), **a))
        except (ValueError, TypeError, ortak.YolYok) as e: print("!!", e); return 4
        return 0
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
