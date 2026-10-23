"""EŞİKLER — bütün eşik dosyalarını yükler, denetler ve tek sözlük olarak verir (TASARIM D-34, §7.1).

Kullanım:
  python esikler.py                                 eşik dosyalarını denetler, özet yazar (HATA varsa çıkış 1)
  python esikler.py --ayar FILM_AYAR.json [--ogrenilen KURALLAR_OGRENILEN.json] [--rapor <film>/_RAPOR]
  Kodda:  import esikler; E = esikler.yukle(ayar=..., ogrenilen=..., rapor=...)
          E["eylem_adim_max"] → 3 · E.kayit[anahtar] → tam kayıt · E.bayraklar → sıkılaştırma notları
Kurallar:
  - Her anahtar {deger, aciklama, kaynak: olcum|belge|tahmin, etiket, gevsetilemez?, yon?}. kaynak ya da etiket yoksa HATA
    (kaynaksız anahtar "tahmin" sayılmaz; belgede "[kaynak: RE]" yazmak kaynak değildir). "_" ile başlayan üst anahtarlar zarftır.
  - Aynı anahtar iki eşik dosyasında HATA.
  - FILM_AYAR.json eşik dosyası değildir (izin, tercih, para tavanı). İçinde bir güvenlik sınırı (gevsetilemez anahtar ya da eski adı)
    bulunursa yalnız sıkılaştırır: tavanda min, tabanda max, çözünürlük en az eşik, model ve klip süresi değişmez. Her bulgu BAYRAK'tır,
    rapor verilirse _RAPOR/ESIK_AYAR.json'a yazılır. Gevşeten değer yok sayılır.
  - KURALLAR_OGRENILEN.json: yalnız "aktif" ve esik/flow_tavan/tempo türündeki kurallar; onlar da yalnız sıkılaştırır (§5.3 korkulukları).
  yon: tavan = küçük olan sıkı · taban = büyük olan sıkı · siklik = mola sıklığı (küçük sıkı; 0 kapalıdır, açılmaz, kapatılamaz)
       sabit = değişmez · cozunurluk = en az eşik. yon yazılmamışsa addan çıkarılır (_max/tavan → tavan, _min/taban → taban).
"""
import os, sys, json, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
DEPO = os.path.dirname(os.path.dirname(HERE))
RE = os.path.join(DEPO, ".claude", "skills", "film-yap", "ritim_esikleri.json")
VERI_DIR = os.path.join(HERE, "veri")
ZORUNLU = [RE, os.path.join(VERI_DIR, "hat_esikleri.json")]
ISTEGE = [os.path.join(VERI_DIR, a) for a in ("hikaye_esikleri.json", "sureklilik_esikleri.json", "ses_esikleri.json")]
SURUM = "esikler 1.0"
KAYNAKLAR = ("olcum", "belge", "tahmin")
YONLER = ("tavan", "taban", "siklik", "sabit", "cozunurluk")
COZ = {"360p": 360, "480p": 480, "720p": 720, "1080p": 1080, "1440p": 1440, "2160p": 2160, "4k": 2160}
# FILM_AYAR'ın eski sürümlerindeki adlar → hat_esikleri.json anahtarı (§5.6). Gevsetilemez anahtarın kendi adı da eşleşir.
AYAR_ESKI_AD = {"gorsel_gunluk_tavan": "flow_gorsel_gunluk_tavan", "gorsel_sonrasi_video_saat": "flow_gorsel_sonrasi_video_saat",
                "paralel_max": "ajan_paralel_max", "flow_modeli": "flow_model", "video_model": "flow_model",
                "cozunurluk": "flow_cozunurluk_min", "video_cozunurluk": "flow_cozunurluk_min", "flow_cozunurluk": "flow_cozunurluk_min",
                "klip_sure": "klip_sn_varsayilan", "klip_sure_sn": "klip_sn_varsayilan", "video_sure_sn": "klip_sn_varsayilan",
                "tempo": "flow_tempo_1710", "flow_tempo": "flow_tempo_1710"}
# KURALLAR_OGRENILEN flow_tavan kısa adları (§5.3 örneği: {"gorsel_gunluk": 15})
OGRENILEN_AD = {"gorsel_gunluk": "flow_gorsel_gunluk_tavan", "gorsel_sonrasi_video_saat": "flow_gorsel_sonrasi_video_saat"}
OGRENILEN_TUR = ("esik", "flow_tavan", "tempo")


class EsikHatasi(Exception):
    def __init__(self, hatalar):
        self.hatalar = list(hatalar)
        super().__init__("eşik dosyalarında %d HATA:\n  " % len(self.hatalar) + "\n  ".join(self.hatalar))


class Esikler(dict):
    """anahtar → uygulanan değer. .kayit: tam kayıtlar (_dosya ile) · .bayraklar · .dosyalar"""
    def __init__(self):
        super().__init__(); self.kayit, self.bayraklar, self.dosyalar = {}, [], []

    def kaynak_sayim(self, dosya=None):
        s = {k: 0 for k in KAYNAKLAR}
        for r in self.kayit.values():
            if dosya is None or r["_dosya"] == dosya: s[r["kaynak"]] += 1
        return s


def _oku(yol):
    with open(yol, encoding="utf-8-sig") as f: return json.load(f)


def kayit_denetle(ad, r):
    """Tek kaydın biçim hataları (liste)."""
    if not isinstance(r, dict): return [f"{ad}: kayıt sözlük değil"]
    h = [f"{ad}: '{a}' alanı yok" for a in ("deger", "aciklama") if a not in r]
    if r.get("kaynak") not in KAYNAKLAR:
        h.append(f"{ad}: kaynak {'yok' if 'kaynak' not in r else repr(r.get('kaynak'))} (olcum|belge|tahmin zorunlu; kaynaksız anahtar tahmin sayılmaz)")
    if not (isinstance(r.get("etiket"), str) and r["etiket"].strip()): h.append(f"{ad}: etiket yok (belge ya da ölçüm kimliği zorunlu)")
    if "gevsetilemez" in r and not isinstance(r["gevsetilemez"], bool): h.append(f"{ad}: gevsetilemez true/false olmalı")
    yon = r.get("yon")
    if yon is not None and not (yon in YONLER or isinstance(yon, dict) and all(v in YONLER for v in yon.values())):
        h.append(f"{ad}: yon geçersiz ({yon!r}; {'|'.join(YONLER)})")
    return h


def yon_bul(ad, r):
    if r.get("yon"): return r["yon"]
    if ad.endswith("_max") or "_max_" in ad or "tavan" in ad: return "tavan"
    if ad.endswith("_min") or "_min_" in ad or "taban" in ad: return "taban"
    return None


def _sayi(x): return isinstance(x, (int, float)) and not isinstance(x, bool)


def _yaprak(esik, gelen, yon):
    """(uygulanan, durum). durum: ayni | sikilasti | gevsek (yok sayıldı) | degismez (yok sayıldı) | gecersiz (yok sayıldı)"""
    if yon == "sabit":
        return (esik, "ayni") if gelen == esik else (esik, "degismez")
    if yon == "cozunurluk":
        e, g = COZ.get(str(esik).lower()), COZ.get(str(gelen).lower())
        if g is None: return esik, "gecersiz"
        if e is None or g > e: return gelen, "sikilasti"
        return (esik, "ayni") if g == e else (esik, "gevsek")
    if not _sayi(gelen): return esik, "gecersiz"
    if esik is None: return gelen, "sikilasti"          # henüz ölçülmemiş eşik: ayardaki sınır tek sınırdır
    if not _sayi(esik): return esik, "gecersiz"
    if yon == "siklik":                                 # mola sıklığı: 0 kapalıdır; açılmaz, açık olan kapatılamaz
        if esik == 0: return (esik, "ayni") if gelen == 0 else (esik, "degismez")
        if gelen <= 0: return esik, "gevsek"
        yon = "tavan"
    if gelen == esik: return esik, "ayni"
    siki = gelen < esik if yon == "tavan" else gelen > esik
    return (gelen, "sikilasti") if siki else (esik, "gevsek")


def sikilastir(esik, gelen, yon, yol=""):
    """Eşik değerine gelen değeri yalnız sıkılaştırarak uygular. (uygulanan, [(yol, esik, gelen, uygulanan, durum)])"""
    if yon is None: return esik, [(yol, esik, gelen, esik, "yon_bilinmiyor")]
    if isinstance(esik, dict):
        if not isinstance(gelen, dict): return esik, [(yol, esik, gelen, esik, "gecersiz")]
        out, notlar = dict(esik), []
        for k, g in gelen.items():
            alt = (yon.get(k) if k in yon else yon) if isinstance(yon, dict) else yon
            if k not in esik or alt is None:
                notlar.append((f"{yol}.{k}".strip("."), None, g, None, "gecersiz")); continue
            out[k], n = sikilastir(esik[k], g, alt, f"{yol}.{k}".strip(".")); notlar += n
        return out, notlar
    if isinstance(yon, dict): return esik, [(yol, esik, gelen, esik, "gecersiz")]
    if isinstance(esik, list):
        if not isinstance(gelen, list) or len(gelen) != len(esik): return esik, [(yol, esik, gelen, esik, "gecersiz")]
        cift = [_yaprak(e, g, yon) for e, g in zip(esik, gelen)]
        out = [u for u, _ in cift]; durumlar = {d for _, d in cift}
        durum = next((d for d in ("gecersiz", "degismez", "gevsek", "sikilasti") if d in durumlar), "ayni")
        if durum == "gecersiz": out = list(esik)
        return out, [(yol, esik, gelen, out, durum)]
    u, d = _yaprak(esik, gelen, yon)
    return u, [(yol, esik, gelen, u, d)]


def _bayrak(E, kaynak, anahtar, notlar, **ek):
    for yol, esik, gelen, uyg, durum in notlar:
        E.bayraklar.append(dict(kaynak=kaynak, anahtar=anahtar, yol=yol, esik=esik, gelen=gelen, uygulanan=uyg, durum=durum, **ek))


def _uygula(E, kaynak, anahtar, gelen, yol, **ek):
    r = E.kayit.get(anahtar)
    if r is None:
        _bayrak(E, kaynak, anahtar, [(yol, None, gelen, None, "bilinmeyen_anahtar")], **ek); return
    yeni, notlar = sikilastir(E[anahtar], gelen, yon_bul(anahtar, r), yol)
    E[anahtar] = yeni
    _bayrak(E, kaynak, anahtar, notlar, **ek)


def _ayar_tara(E, ayar, yol=""):
    if not isinstance(ayar, dict): return
    gev = {k for k, r in E.kayit.items() if r.get("gevsetilemez")}
    for k, v in ayar.items():
        if k.startswith("_"): continue
        p = f"{yol}.{k}" if yol else k
        hedef = k if k in gev else AYAR_ESKI_AD.get(k)
        if hedef in gev: _uygula(E, "FILM_AYAR", hedef, v, p)
        elif isinstance(v, dict): _ayar_tara(E, v, p)


def _ogrenilen_uygula(E, ogr):
    for kural in (ogr or {}).get("kurallar") or []:
        if not isinstance(kural, dict) or kural.get("durum") != "aktif" or kural.get("tur") not in OGRENILEN_TUR: continue
        kid, deger = kural.get("id"), kural.get("deger")
        if kural["tur"] == "tempo":
            _uygula(E, "KURALLAR_OGRENILEN", "flow_tempo_1710", deger, "flow_tempo_1710", kural=kid); continue
        if not isinstance(deger, dict):
            _bayrak(E, "KURALLAR_OGRENILEN", None, [("", None, deger, None, "gecersiz")], kural=kid); continue
        for k, v in deger.items():
            a = OGRENILEN_AD.get(k, k) if kural["tur"] == "flow_tavan" else k
            _uygula(E, "KURALLAR_OGRENILEN", a, v, a, kural=kid)


def _json_ya_da_yol(x):
    if x is None or isinstance(x, dict): return x
    return _oku(x) if os.path.exists(x) else None


def rapor_yaz(E, klasor):
    os.makedirs(klasor, exist_ok=True)
    yol = os.path.join(klasor, "ESIK_AYAR.json")
    v = {"_surum": 1, "_uretim": {"arac_surum": SURUM, "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
                                  "sonuc": "BAYRAK" if E.bayraklar else "GEC"},
         "kapi": "ESIK_AYAR", "sonuc": "BAYRAK" if E.bayraklar else "GEC", "bayraklar": E.bayraklar}
    tmp = yol + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f: json.dump(v, f, ensure_ascii=False, indent=1)
    os.replace(tmp, yol)
    return yol


def yukle(dosyalar=None, ayar=None, ogrenilen=None, rapor=None):
    """Eşik dosyalarını yükler; HATA varsa EsikHatasi. ayar/ogrenilen: dosya yolu ya da sözlük (yoksa atlanır).
    rapor: _RAPOR klasörü verilirse ESIK_AYAR.json yazılır."""
    if dosyalar is None: dosyalar = ZORUNLU + [p for p in ISTEGE if os.path.exists(p)]
    E, hatalar, nerede = Esikler(), [], {}
    for yol in dosyalar:
        ad = os.path.basename(yol)
        try: veri = _oku(yol)
        except (OSError, ValueError) as e: hatalar.append(f"{ad}: okunamadı ({e})"); continue
        if not isinstance(veri, dict): hatalar.append(f"{ad}: üst düzey sözlük değil"); continue
        E.dosyalar.append(yol)
        for k, r in veri.items():
            if k.startswith("_"): continue
            if k in nerede: hatalar.append(f"{k}: iki eşik dosyasında ({nerede[k]} ve {ad})"); continue
            nerede[k] = ad
            h = kayit_denetle(f"{ad}:{k}", r)
            if h: hatalar += h; continue
            E.kayit[k] = dict(r, _dosya=ad); E[k] = r["deger"]
    if hatalar: raise EsikHatasi(hatalar)
    _ogrenilen_uygula(E, _json_ya_da_yol(ogrenilen))
    _ayar_tara(E, _json_ya_da_yol(ayar))
    if rapor: rapor_yaz(E, rapor)
    return E


def main(argv):
    a = {"--ayar": None, "--ogrenilen": None, "--rapor": None}
    i = 0
    while i < len(argv):
        if argv[i] in a and i + 1 < len(argv): a[argv[i]] = argv[i + 1]; i += 2
        else: print(__doc__); return 4
    try: E = yukle(ayar=a["--ayar"], ogrenilen=a["--ogrenilen"], rapor=a["--rapor"])
    except EsikHatasi as e: print("!!", e); return 1
    for yol in E.dosyalar:
        ad = os.path.basename(yol); s = E.kaynak_sayim(ad)
        n = sum(s.values()); g = sum(1 for r in E.kayit.values() if r["_dosya"] == ad and r.get("gevsetilemez"))
        print(f"{ad}: {n} anahtar · olcum {s['olcum']} · belge {s['belge']} · tahmin {s['tahmin']} · gevsetilemez {g}")
    for b in E.bayraklar:
        print(f"BAYRAK [{b['kaynak']}] {b['yol'] or b['anahtar']}: eşik {b['esik']!r}, gelen {b['gelen']!r} → {b['uygulanan']!r} ({b['durum']})")
    print(f"Toplam {len(E)} anahtar; HATA 0; BAYRAK {len(E.bayraklar)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
