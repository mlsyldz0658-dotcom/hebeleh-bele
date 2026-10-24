"""FLOW YÜK — Flow hesabının yük defteri, temposu, günlük tavanları ve uyarı kilidi (TASARIM D-02 d, D-03, D-04, §8.4).

Kullanım:
  python flow_yuk.py                          durum: kilit, sonraki izinli gönderim, mola, bugünkü görsel/video sayısı
  python flow_yuk.py --json                   aynı durum, makine için JSON
  python flow_yuk.py --izin video [--kip elle|gece]
                                              şimdi bu gönderime izin var mı? çıkış 0 izinli · 8 bekle · 7 kilitli · 5 elle gerekli
  python flow_yuk.py --uyari-gecti [--elle-video-basarili]
                                              UYARI_GECTI.bat: Flow kilidini aşağıdaki şartlarla kaldırır; şart yoksa nedenini yazar (7).
                                              YALNIZ KULLANICI: etkileşimli konsol (TTY) şart; "ben kullanıcıyım" yazılarak onaylanır.
                                              TTY değilse (ajan, betik, boru) hiçbir şey yapmaz, 7. --elle-video-basarili yoksa soru da sorar.
Kodda:  import flow_yuk as fy
  fy.izinli_mi("video", "elle") → {"izinli", "kod", "nedenler", "bekle_bitis"} · fy.gonderim_kaydet("video", "elle", film=..., plan=...)
  fy.blok_bitti("gece") → mola düştü mü · fy.kilit_durumu() · fy.uyari_kaydet(film, mesaj) · fy.hesap_gozlem(eposta=...)
  fy.uyari_gecti(elle_video_basarili=True) · fy.tempo("gece") · fy.tempo_durumu("elle") · fy.gunluk_sayim()

Dosyalar (<veri>/HESAP/; filmden bağımsız, git'e girmez):
  FLOW_YUK.jsonl       her gönderim bir satır, yalnız eklenir: {zaman, zaman_epoch, hesap, film, tur, plan, mod, cikti_sayisi}
  FLOW_TEMPO.json      PR-0 Memmet'in alanları aynen (epoch saniye): son_gonderim, sonraki_izin, mola_bitis, gonderim_sayaci, parti_sayaci, kip.
                       Ek alanlar (Memmet okumaz, yazarken korur): gunluk, son_gorsel_gonderimi, son_uyari, yavaslatma, ilk_blok_elle, uyari_gecti.
  FLOW_KILIDI.json     uyarı (neden olagandisi) ya da hesap değişimi (neden hesap_degisti) kilidi; Memmet'in yazdığı biçim okunur.
  FLOW_UYARILARI.jsonl uyarı geçmişi (haftalık kilit buradan sayılır) · HESAP_DURUMU.json hesap kimliği (yalnız sha1; e-posta saklanmaz)
  _ESKI/               kaldırılan kilitler buraya taşınır (silinmez)
Kurallar:
  - Sayılar yalnız veri/hat_esikleri.json'dan (esikler.py, gevsetilemez). FILM_AYAR.json ve KURALLAR_OGRENILEN.json yalnız yavaşlatır.
  - Kilit en erken uyarıdan uyari_sonrasi_bekleme_dk sonra kalkabilir; aynı takvim haftasında ikinci uyarı → haftalik_uyari_kilidi_gun gün.
  - UYARI_GECTI şartları: kilit yalnız asıl hesapta kalkar (başka hesapta asla); en erken zaman geçmiş; kullanıcı en erken zamandan sonra Flow'da
    ELLE 1 video denedi ve başarılı; karar yalnız o takvim günü verilir ve geçer; o günün kalanında tempo ×1,5 yavaş; o gün ve ertesi gün
    ilk blok bitene kadar gece kipi kapalı (ilk blok elle).
  - Günlük görsel tavanı ve görselden videoya bekleme hesap düzeyindedir: bütün filmler aynı sayaçtan geçer.
  - Gönderim kaydı engellemez (olmuş gönderim mutlaka yazılır); izni izinli_mi() verir.
"""
import os, sys, re, json, time, random, hashlib, datetime, copy
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, esikler

SURUM = "flow_yuk 1.0"
TEMPO_SURUM = 2            # v1 (PR-0 Memmet) alanlarının üst kümesi
TURLER = ("gorsel", "video")
IZINLI, KIP_ELLE, KILITLI, BEKLE, KULLANIM = 0, 5, 7, 8, 4
# §8.4 "o günün kalanında tempo ×1,5". hat_esikleri.json'da 'uyari_gecti_tempo_carpan' varsa o uygulanır, ama bundan hızlı olamaz.
CARPAN_ANAHTAR, CARPAN_TABAN = "uyari_gecti_tempo_carpan", 1.5
HIZ_ALANLARI = ("gonderim_arasi_sn", "gonderim_mola_dk", "parti_mola_dk")
GUN = 86400


class YukHatasi(Exception):
    """Flow yük dosyaları ya da eşikler okunamadı / geçersiz çağrı. Hat kapalı başarısız davranır (gönderim yok)."""


# ------------------------------------------------------------------ yollar, eşikler, zaman
def kok_bul(kok=None): return os.path.abspath(kok) if kok else ortak.yollar()["hesap"]
def _yol(kok, ad): return os.path.join(kok_bul(kok), ad)
def yuk_yolu(kok=None): return _yol(kok, "FLOW_YUK.jsonl")
def tempo_yolu(kok=None): return _yol(kok, "FLOW_TEMPO.json")
def kilit_yolu(kok=None): return _yol(kok, "FLOW_KILIDI.json")
def uyarilar_yolu(kok=None): return _yol(kok, "FLOW_UYARILARI.jsonl")
def hesap_yolu(kok=None): return _yol(kok, "HESAP_DURUMU.json")


def esik_yukle(kok=None):
    """hat_esikleri.json (+ FILM_AYAR.json ve KURALLAR_OGRENILEN.json yalnız sıkılaştırarak). Bozuk dosya → YukHatasi (kapalı başarısız)."""
    veri = os.path.dirname(kok_bul(kok))
    ayar = os.path.join(veri, "AYARLAR", "FILM_AYAR.json"); ogr = os.path.join(veri, "BILGI", "KURALLAR_OGRENILEN.json")
    try: return esikler.yukle(ayar=ayar if os.path.exists(ayar) else None, ogrenilen=ogr if os.path.exists(ogr) else None)
    except (OSError, ValueError) as e: raise YukHatasi(f"eşik/ayar dosyası okunamadı: {e}") from e


def _e(E, kok): return E if E is not None else esik_yukle(kok)
def _simdi(s): return time.time() if s is None else float(s)
def _tarih(t): return time.strftime("%Y-%m-%d", time.localtime(t))
def _metin(t): return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))
def _iso(t): return datetime.datetime.fromtimestamp(t).astimezone().isoformat(timespec="seconds")
def _hafta(t): y, h, _ = datetime.date.fromtimestamp(t).isocalendar(); return f"{y}-{h:02d}"   # %G/%V Windows'ta yok


def _gece_yarisi(t):
    d = datetime.date.fromtimestamp(t) + datetime.timedelta(days=1)
    return time.mktime(d.timetuple())


def _epoch(x):
    """epoch sayısı, 'YYYY-MM-DD HH:MM[:SS]' (yerel) ya da ISO metni → epoch; anlaşılmazsa None."""
    if isinstance(x, (int, float)) and not isinstance(x, bool): return float(x) if x > 0 else None
    if not isinstance(x, str) or not x.strip(): return None
    s = x.strip()
    for b in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try: return time.mktime(time.strptime(s, b))
        except ValueError: pass
    try:
        d = datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d.timestamp() if d.tzinfo else time.mktime(d.timetuple())
    except ValueError: return None


def _jsonl_oku(yol):
    """Satır satır okur; bozuk satırı (yarım kalmış son satır dahil) atlar."""
    out = []
    try:
        with open(yol, encoding="utf-8-sig") as f:
            for l in f:
                try:
                    d = json.loads(l)
                    if isinstance(d, dict): out.append(d)
                except ValueError: pass
    except OSError: pass
    return out


def _jsonl_ekle(yol, satir):
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    with open(yol, "a", encoding="utf-8") as f:
        f.write(json.dumps(satir, ensure_ascii=False) + "\n"); f.flush(); os.fsync(f.fileno())


# ------------------------------------------------------------------ hesap kimliği (D-03: yalnız sha1)
def hesap_kimligi(eposta):
    if not isinstance(eposta, str) or "@" not in eposta: raise YukHatasi("hesap kimliği için e-posta gerekli")
    return hashlib.sha1(eposta.strip().lower().encode("utf-8")).hexdigest()


def _kimlik(eposta=None, kimlik=None):
    if eposta: return hesap_kimligi(eposta)
    if kimlik is None: return None
    if not re.fullmatch(r"[0-9a-f]{40}", str(kimlik)): raise YukHatasi("hesap kimliği 40 haneli sha1 olmalı (açık e-posta saklanmaz)")
    return str(kimlik)


def hesap_durumu(kok=None):
    d = ortak.json_oku(hesap_yolu(kok), None)
    return d if isinstance(d, dict) else {"_surum": 1, "hesap_kimligi": None, "gecmis": []}


def _hesap_o_an(kok, t):
    """t anında görülen hesap (HESAP_DURUMU geçmişinden); bilinmiyorsa None."""
    D = hesap_durumu(kok); aday = None
    for g in D.get("gecmis") or []:
        z = _epoch(g.get("zaman_epoch")) or _epoch(g.get("zaman"))
        if z is not None and z <= t + 1: aday = g.get("kimlik")
    return aday or (D.get("hesap_kimligi") if not D.get("gecmis") else None)


# ------------------------------------------------------------------ tempo
BOS_TEMPO = {"_surum": TEMPO_SURUM, "son_gonderim": 0, "sonraki_izin": 0, "mola_bitis": 0, "gonderim_sayaci": 0, "parti_sayaci": 0}


TEMPO_BELIRSIZ_BEKLEME_SN = 30 * 60     # tempo dosyası bozuk/eksikken (geçmiş varken) en uzun mola kadar beklenir (kapalı başarısız)


def tempo_oku(kok=None):
    """FLOW_TEMPO.json (v1 Memmet ya da v2). Yoksa ve FLOW_YUK geçmişi de yoksa sıfır sayaçlar (taze hesap). Bozuksa ya da geçmiş
    varken yoksa bekleme SIFIRLANMAZ: son bilinen gönderimden (ya da bozuk dosyanın tarihinden) en uzun mola kadar beklenir."""
    p = tempo_yolu(kok); T = ortak.json_oku(p, None)
    if isinstance(T, dict):
        T = dict(T)
        for k, v in BOS_TEMPO.items(): T.setdefault(k, v)
        return T
    T = dict(BOS_TEMPO)
    gecmis = [z for z in (_satir_zaman(r) for r in yuk_oku(kok)) if z]
    if os.path.exists(p):                                   # bozuk dosya: tarihinden (ve son gönderimden) en uzun mola
        try: dz = os.path.getmtime(p)
        except OSError: dz = time.time()
        taban = max([dz] + gecmis)
    elif gecmis: taban = max(gecmis)                         # silinmiş dosya: geçmişten
    else: return T
    T.update(son_gonderim=max(gecmis) if gecmis else 0, sonraki_izin=taban + TEMPO_BELIRSIZ_BEKLEME_SN, gonderim_sayaci=len(gecmis),
             _belirsiz=True)
    return T


def _tempo_yaz(kok, T):
    T["_surum"] = max(TEMPO_SURUM, int(T.get("_surum") or 1))
    ortak.atomik_yaz(tempo_yolu(kok), T)


def _carpan(T, E, simdi):
    y = T.get("yavaslatma") or {}
    if y.get("tarih") != _tarih(simdi): return 1.0
    try: c = float(y.get("carpan") or 1.0)
    except (TypeError, ValueError): c = 1.0
    return max(1.0, c, _uyari_carpan(E))


def _uyari_carpan(E):
    v = E.get(CARPAN_ANAHTAR) if E is not None else None
    return max(CARPAN_TABAN, float(v)) if isinstance(v, (int, float)) and not isinstance(v, bool) else CARPAN_TABAN


def tempo(kip, kok=None, E=None, simdi=None, ek=None):
    """Kip için uygulanan tempo: hat_esikleri flow_tempo_1710[kip] (öğrenilen + FILM_AYAR ile yalnız yavaş), ek (ör. MEMMET_AYAR)
    yalnız yavaşlatır, UYARI_GECTI günü aralıklar ve molalar × çarpan. Sonuca 'carpan' eklenir."""
    E = _e(E, kok); simdi = _simdi(simdi)
    tum = E.get("flow_tempo_1710")
    if not isinstance(tum, dict) or kip not in tum: raise YukHatasi(f"bilinmeyen kip: {kip!r} (hat_esikleri.json flow_tempo_1710)")
    t = copy.deepcopy(tum[kip])
    if ek:
        yon = esikler.yon_bul("flow_tempo_1710", E.kayit["flow_tempo_1710"])
        t, _ = esikler.sikilastir(t, {k: v for k, v in ek.items() if k in t}, yon)
    c = _carpan(tempo_oku(kok), E, simdi)
    if c > 1:
        for k in HIZ_ALANLARI:
            if isinstance(t.get(k), list): t[k] = [round(x * c, 3) for x in t[k]]
    t["carpan"] = c
    return t


def tempo_durumu(kip="elle", kok=None, E=None, simdi=None, ek=None):
    """Sonraki izinli zaman ve molalar (memmet.TEMPO anlamıyla): kalan bekleme, sıradaki molaya kalan gönderim/parti.
    ek (ör. MEMMET_AYAR) yalnız yavaşlatır."""
    simdi = _simdi(simdi); T = tempo_oku(kok); t = tempo(kip, kok, E, simdi, ek)
    hedef = max(float(T.get("sonraki_izin") or 0), float(T.get("mola_bitis") or 0),
                float(T.get("son_gonderim") or 0) + (t["gonderim_arasi_sn"][0] if T.get("son_gonderim") else 0))
    n, p = t.get("mola_kac_gonderimde", 0), t.get("mola_kac_partide", 0)
    return {"kip": kip, "sonraki_izin": hedef, "kalan_sn": max(0.0, hedef - simdi), "molada": float(T.get("mola_bitis") or 0) > simdi,
            "mola_bitis": float(T.get("mola_bitis") or 0), "gonderim_sayaci": int(T.get("gonderim_sayaci") or 0),
            "parti_sayaci": int(T.get("parti_sayaci") or 0),
            "molaya_kalan_gonderim": (n - int(T.get("gonderim_sayaci") or 0) % n) if n else None,
            "molaya_kalan_parti": (p - int(T.get("parti_sayaci") or 0) % p) if p else None, "carpan": t["carpan"]}


# ------------------------------------------------------------------ yük defteri ve günlük sayılar
def yuk_oku(kok=None): return _jsonl_oku(yuk_yolu(kok))


def _satir_zaman(s): return _epoch(s.get("zaman_epoch")) or _epoch(s.get("zaman"))


def gunluk_sayim(kok=None, simdi=None):
    """Bugün (yerel takvim günü) bu hesaptan giden görsel ve video gönderimleri. Defter ve FLOW_TEMPO.gunluk'tan büyük olan."""
    simdi = _simdi(simdi); bugun = _tarih(simdi); s = {"tarih": bugun, "gorsel": 0, "video": 0}
    for r in yuk_oku(kok):
        z = _satir_zaman(r)
        if z is not None and _tarih(z) == bugun and r.get("tur") in TURLER: s[r["tur"]] += 1
    g = tempo_oku(kok).get("gunluk") or {}
    if g.get("tarih") == bugun:
        for t in TURLER: s[t] = max(s[t], int(g.get(t) or 0))
    return s


def son_gorsel(kok=None):
    z = [_satir_zaman(r) for r in yuk_oku(kok) if r.get("tur") == "gorsel"]
    z = [x for x in z if x] + [_epoch(tempo_oku(kok).get("son_gorsel_gonderimi")) or 0]
    return max(z) or None


def gonderim_kaydet(tur, kip, film=None, plan=None, cikti_sayisi=None, hesap=None, kok=None, E=None, simdi=None, rnd=None, ek=None):
    """Olmuş bir Flow gönderimini yazar (önce FLOW_YUK.jsonl, sonra FLOW_TEMPO.json). memmet.gonderim_kaydet ile aynı anlam:
    sonraki_izin = şimdi + gönderim arası; N gönderimde bir mola. Engellemez; izni izinli_mi() verir. Güncel tempo sözlüğünü döndürür."""
    if tur not in TURLER: raise YukHatasi(f"tur gorsel|video olmalı: {tur!r}")
    E = _e(E, kok); simdi = _simdi(simdi); rnd = rnd or random; t = tempo(kip, kok, E, simdi, ek)
    hesap = _kimlik(kimlik=hesap) if hesap else hesap_durumu(kok).get("hesap_kimligi")
    T = tempo_oku(kok)                         # bu gönderimden ÖNCEKİ durum (yeni satır "geçmiş" sayılmasın)
    T.pop("_belirsiz", None)
    _jsonl_ekle(yuk_yolu(kok), {"zaman": _iso(simdi), "zaman_epoch": round(simdi, 3), "hesap": hesap, "film": film, "tur": tur,
                                "plan": plan, "mod": kip, "cikti_sayisi": cikti_sayisi})
    T["son_gonderim"] = simdi; T["gonderim_sayaci"] = int(T.get("gonderim_sayaci") or 0) + 1; T["kip"] = kip
    T["sonraki_izin"] = max(float(T.get("sonraki_izin") or 0), simdi + rnd.uniform(*t["gonderim_arasi_sn"]))
    n = t.get("mola_kac_gonderimde", 0)
    if n and T["gonderim_sayaci"] % n == 0:
        T["mola_bitis"] = max(float(T.get("mola_bitis") or 0), simdi + rnd.uniform(*t["gonderim_mola_dk"]) * 60)
    g = T.get("gunluk") or {}
    if g.get("tarih") != _tarih(simdi): g = {"tarih": _tarih(simdi), "gorsel": 0, "video": 0}
    g[tur] = int(g.get(tur) or 0) + 1; T["gunluk"] = g
    if tur == "gorsel": T["son_gorsel_gonderimi"] = simdi
    _tempo_yaz(kok, T)
    return T


def blok_bitti(kip, kok=None, E=None, simdi=None, rnd=None, ek=None):
    """Parti/blok sonu (memmet.parti_bitti anlamı). Mola düştüyse True. Elle biten blok 'ertesi gün ilk blok elle' şartını kapatır.
    ek (ör. MEMMET_AYAR parti_mola_dk, mola_kac_partide) yalnız yavaşlatır."""
    E = _e(E, kok); simdi = _simdi(simdi); rnd = rnd or random; t = tempo(kip, kok, E, simdi, ek)
    T = tempo_oku(kok); n = t.get("mola_kac_partide", 0); T["parti_sayaci"] = int(T.get("parti_sayaci") or 0) + 1
    mola = bool(n and T["parti_sayaci"] % n == 0)
    if mola: T["mola_bitis"] = max(float(T.get("mola_bitis") or 0), simdi + rnd.uniform(*t["parti_mola_dk"]) * 60)
    ie = T.get("ilk_blok_elle")
    if kip == "elle" and isinstance(ie, dict) and not ie.get("tamam") and _tarih(simdi) >= str(ie.get("tarih")):
        ie["tamam"] = True; ie["tamam_zaman"] = _metin(simdi)
    _tempo_yaz(kok, T)
    return mola


# ------------------------------------------------------------------ uyarı kilidi
def uyarilar_oku(kok=None):
    out = []
    for u in _jsonl_oku(uyarilar_yolu(kok)):
        z = _epoch(u.get("zaman_epoch")) or _epoch(u.get("zaman"))
        if z: out.append(dict(u, zaman_epoch=z, hafta=u.get("hafta") or _hafta(z)))
    return out


def kilit_oku(kok=None):
    """FLOW_KILIDI.json sözlüğü; yoksa None. Var ama okunamıyorsa {'neden': 'bozuk'} (kilitli sayılır)."""
    p = kilit_yolu(kok)
    if not os.path.exists(p): return None
    K = ortak.json_oku(p, None)
    if not isinstance(K, dict): K = {"neden": "bozuk", "zaman_epoch": os.path.getmtime(p)}
    return K


def _kilit_hesapla(K, uyarilar, E, p):
    zaman = _epoch(K.get("zaman_epoch")) or _epoch(K.get("zaman")) or (os.path.getmtime(p) if os.path.exists(p) else time.time())
    son = max([zaman] + [u["zaman_epoch"] for u in uyarilar if u["zaman_epoch"] >= zaman - 1])
    hafta = _hafta(son)
    n = max(sum(1 for u in uyarilar if u["hafta"] == hafta), int(K.get("haftanin_uyarisi") or 1))
    ee = son + E["uyari_sonrasi_bekleme_dk"] * 60
    if n >= 2: ee = max(ee, son + E["haftalik_uyari_kilidi_gun"] * GUN)
    for x in (K.get("en_erken_epoch"), K.get("en_erken"), (K.get("kaldirma") or {}).get("en_erken")):
        ee = max(ee, _epoch(x) or 0)
    return zaman, son, n, ee


def kilit_durumu(kok=None, E=None, simdi=None):
    """{'kilitli', 'neden', 'zaman', 'son_uyari', 'haftanin_uyarisi', 'en_erken', 'en_erken_metin', 'kalkabilir', 'hesap', 'film'}.
    en_erken yalnız uzar: dosyadaki değer, uyarı + bekleme dk ve haftalık ikinci uyarı + gün kilidinden en geç olanı."""
    simdi = _simdi(simdi); K = kilit_oku(kok)
    if K is None: return {"kilitli": False}
    E = _e(E, kok); zaman, son, n, ee = _kilit_hesapla(K, uyarilar_oku(kok), E, kilit_yolu(kok))
    asil = K.get("asil_hesap") or K.get("hesap") or _hesap_o_an(kok, zaman)
    return {"kilitli": True, "neden": K.get("neden", "olagandisi"), "zaman": zaman, "son_uyari": son, "haftanin_uyarisi": n,
            "en_erken": ee, "en_erken_metin": _metin(ee), "kalkabilir": simdi >= ee, "hesap": asil, "film": K.get("film")}


def uyari_kaydet(film, mesaj, plan=None, kok=None, E=None, simdi=None):
    """Flow uyarısı: FLOW_UYARILARI.jsonl'e ekler, kilidi yazar ya da var olanın en_erken'ini uzatır (hiç kısaltmaz). memmet.kilit_yaz ile
    aynı dosya biçimi (+ hesap, en_erken_epoch, kaldirma). kilit_durumu() döndürür."""
    E = _e(E, kok); simdi = _simdi(simdi); hesap = hesap_durumu(kok).get("hesap_kimligi")
    _jsonl_ekle(uyarilar_yolu(kok), {"zaman": _metin(simdi), "zaman_epoch": round(simdi, 3), "hafta": _hafta(simdi), "film": film,
                                     "plan": plan})
    T = tempo_oku(kok); T["son_uyari"] = simdi; _tempo_yaz(kok, T)
    K = kilit_oku(kok)
    if K is None or K.get("neden") == "bozuk":
        K = {"_surum": 1, "neden": "olagandisi", "film": film, "plan": plan, "mesaj": mesaj, "zaman": _metin(simdi),
             "zaman_epoch": int(simdi), "hesap": hesap,
             "nasil_kalkar": "GÖNDER'e basma, sayfayı yenileme. Bekle; en erken 'en_erken' zamanında Flow'da ELLE tek bir video dene. "
                             "Sorunsuzsa UYARI_GECTI.bat'ı çalıştır. Başka Google/Flow hesabıyla devam edilmez."}
    zaman, son, n, ee = _kilit_hesapla(K, uyarilar_oku(kok), E, kilit_yolu(kok))
    K.update(haftanin_uyarisi=n, en_erken=time.strftime("%Y-%m-%d %H:%M", time.localtime(ee + 59)), en_erken_epoch=int(ee + 0.999),
             kaldirma={"elle_1_video_basarili": False, "en_erken": _iso(ee), "gecerli_gun": None})
    ortak.atomik_yaz(kilit_yolu(kok), K)
    return kilit_durumu(kok, E, simdi)


def hesap_gozlem(eposta=None, kimlik=None, kok=None, E=None, simdi=None):
    """Flow'da görünen hesabı kaydeder (yalnız sha1). Son uyarıdan sonraki hesap_degisim_kilidi_gun içinde hesap değişirse FLOW_KILIDI
    (neden hesap_degisti; asil_hesap = önceki) yazılır; uyarı yokken değişim yalnız kaydedilir ve bilgi verilir."""
    yeni = _kimlik(eposta, kimlik)
    if not yeni: raise YukHatasi("hesap_gozlem: eposta ya da kimlik gerekli")
    E = _e(E, kok); simdi = _simdi(simdi); D = hesap_durumu(kok); onceki = D.get("hesap_kimligi")
    sonuc = {"kimlik": yeni, "degisti": bool(onceki and onceki != yeni), "kilit": False, "bilgi": None}
    if sonuc["degisti"]:
        son = max([u["zaman_epoch"] for u in uyarilar_oku(kok)] + [_epoch(tempo_oku(kok).get("son_uyari")) or 0])
        K = kilit_oku(kok)
        if son and simdi - son <= E["hesap_degisim_kilidi_gun"] * GUN or K is not None:
            if K is None or K.get("neden") == "bozuk":
                K = {"_surum": 1, "neden": "hesap_degisti", "zaman": _metin(simdi), "zaman_epoch": int(simdi), "asil_hesap": onceki,
                     "haftanin_uyarisi": 1, "nasil_kalkar": "Flow'da asıl hesaba dön. Kilit yalnız asıl hesapta UYARI_GECTI.bat şartlarıyla kalkar. "
                                                         "Başka Google/Flow hesabıyla devam edilmez."}
            else:
                K.setdefault("asil_hesap", K.get("hesap") or onceki)
            K["hesap_degisimi"] = {"zaman": _metin(simdi), "gorulen": yeni}
            ortak.atomik_yaz(kilit_yolu(kok), K)
            sonuc["kilit"] = True
            sonuc["bilgi"] = "Flow hesabı değişti (son uyarıdan sonra): kilit yazıldı. Başka hesapla devam edilmez; asıl hesaba dön."
        else:
            sonuc["bilgi"] = "Flow hesabı değişti (uyarı kaydı yok): yalnız kaydedildi."
    if onceki != yeni:
        D.setdefault("gecmis", []).append({"kimlik": yeni, "zaman": _metin(simdi), "zaman_epoch": int(simdi)})
    D.update(_surum=D.get("_surum", 1), hesap_kimligi=yeni, son_gorulme=_metin(simdi))
    ortak.atomik_yaz(hesap_yolu(kok), D)
    return sonuc


def uyari_gecti(elle_video_basarili, eposta=None, kimlik=None, deneme_zamani=None, kok=None, E=None, simdi=None):
    """UYARI_GECTI (§8.4, [UM2] İ-8). Şartlar: kilit var; kilit asıl hesapta (şimdiki hesap = kilidin hesabı; bilinmiyorsa ret);
    en erken zaman geçmiş; kullanıcı en erken zamandan sonra ve BUGÜN Flow'da elle 1 video denedi, başarılı oldu.
    Şartlar tamamsa kilit HESAP/_ESKI/'ye taşınır (silinmez), bugün tempo × çarpan yavaş, bugün ve ertesi gün ilk blok bitene kadar gece kapalı.
    Döndürür: {'sonuc': 'kaldirildi'|'red'|'kilit_yok', 'nedenler': [...], ...}"""
    E = _e(E, kok); simdi = _simdi(simdi); K = kilit_oku(kok)
    if K is None: return {"sonuc": "kilit_yok", "nedenler": ["Flow kilidi yok; kaldırılacak bir şey yok."]}
    d = kilit_durumu(kok, E, simdi); nedenler = []
    simdiki = _kimlik(eposta, kimlik) or hesap_durumu(kok).get("hesap_kimligi")
    if eposta or kimlik:
        kayitli = hesap_durumu(kok).get("hesap_kimligi")
        if kayitli and kayitli != simdiki: nedenler.append("Verilen hesap, Flow'da en son görülen hesap değil.")
    if d["hesap"] and simdiki != d["hesap"]:
        nedenler.append("Kilit başka (asıl) hesapta: kilit yalnız asıl hesapta kalkar; başka Google/Flow hesabıyla devam edilmez."
                        if simdiki else "Şimdiki Flow hesabı bilinmiyor; kilit yalnız asıl hesapta kalkar.")
    if not d["kalkabilir"]: nedenler.append(f"Henüz erken: en erken {d['en_erken_metin']}.")
    if elle_video_basarili is not True:
        nedenler.append("Önce Flow'da ELLE 1 video dene; başarılı olduysa onayla.")
    dz = _epoch(deneme_zamani) if deneme_zamani is not None else simdi
    if dz is None: nedenler.append("Deneme zamanı anlaşılamadı.")
    else:
        if dz < d["en_erken"]: nedenler.append(f"Elle deneme en erken zamandan ({d['en_erken_metin']}) önce yapılmış; yeniden dene.")
        if _tarih(dz) != _tarih(simdi) or dz > simdi + 60:
            nedenler.append("Elle deneme bugün yapılmış olmalı (karar yalnız o takvim günü geçerlidir).")
    if nedenler: return {"sonuc": "red", "nedenler": nedenler, "en_erken": d["en_erken"], "en_erken_metin": d["en_erken_metin"]}
    bugun = _tarih(simdi); yarin = (datetime.date.fromtimestamp(simdi) + datetime.timedelta(days=1)).isoformat(); c = _uyari_carpan(E)
    K["kaldirma"] = {"elle_1_video_basarili": True, "en_erken": _iso(d["en_erken"]), "gecerli_gun": bugun, "zaman": _iso(simdi),
                     "deneme_zamani": _iso(dz), "hesap": simdiki}
    ortak.atomik_yaz(kilit_yolu(kok), K)
    eski = os.path.join(kok_bul(kok), "_ESKI"); os.makedirs(eski, exist_ok=True)
    taban = os.path.join(eski, "FLOW_KILIDI_" + time.strftime("%Y%m%dT%H%M%S", time.localtime(simdi))); hedef, i = taban + ".json", 1
    while os.path.exists(hedef): i += 1; hedef = f"{taban}_{i}.json"
    os.replace(kilit_yolu(kok), hedef)
    T = tempo_oku(kok)
    T["uyari_gecti"] = {"tarih": bugun, "zaman": _metin(simdi), "kilit_zamani": _metin(d["zaman"]), "arsiv": os.path.basename(hedef)}
    T["yavaslatma"] = {"carpan": c, "tarih": bugun, "neden": "uyari_gecti"}
    T["ilk_blok_elle"] = {"tarih": yarin, "tamam": False, "neden": "uyari_gecti"}
    _tempo_yaz(kok, T)
    return {"sonuc": "kaldirildi", "nedenler": [], "gecerli_gun": bugun, "carpan": c, "ilk_blok_elle": yarin, "arsiv": hedef}


# ------------------------------------------------------------------ izin
def _ilk_blok_elle_bekliyor(T, simdi):
    ie = T.get("ilk_blok_elle")
    return isinstance(ie, dict) and not ie.get("tamam") and bool(ie.get("tarih"))


def izinli_mi(tur, kip="elle", kok=None, E=None, simdi=None, ek=None):
    """Şimdi bu hesaptan bir Flow gönderimine izin var mı? kod: 0 izinli · 7 kilitli · 5 elle gerekli · 8 bekle (bekle_bitis'e kadar)."""
    if tur not in TURLER: raise YukHatasi(f"tur gorsel|video olmalı: {tur!r}")
    E = _e(E, kok); simdi = _simdi(simdi); nedenler = []
    k = kilit_durumu(kok, E, simdi)
    if k["kilitli"]:
        return {"izinli": False, "kod": KILITLI, "bekle_bitis": None, "kilit": k,
                "nedenler": [f"Flow kilidi var ({k['neden']}); en erken {k['en_erken_metin']}. Kilidi yalnız UYARI_GECTI.bat kaldırır."]}
    T = tempo_oku(kok)
    if kip != "elle" and _ilk_blok_elle_bekliyor(T, simdi):
        return {"izinli": False, "kod": KIP_ELLE, "bekle_bitis": None,
                "nedenler": ["UYARI_GECTI sonrası ilk blok elle gider: gece kipi bu blok bitene kadar kapalı."]}
    bitis = [tempo_durumu(kip, kok, E, simdi, ek)["sonraki_izin"]]
    if bitis[0] > simdi: nedenler.append(f"Tempo/mola: sonraki gönderim {_metin(bitis[0])}.")
    if tur == "gorsel":
        g = gunluk_sayim(kok, simdi)["gorsel"]
        if g >= E["flow_gorsel_gunluk_tavan"]:
            bitis.append(_gece_yarisi(simdi)); nedenler.append(f"Bugün {g} görsel gönderildi (tavan {E['flow_gorsel_gunluk_tavan']}); yarın.")
    else:
        sg = son_gorsel(kok)
        if sg and sg + E["flow_gorsel_sonrasi_video_saat"] * 3600 > simdi:
            b = sg + E["flow_gorsel_sonrasi_video_saat"] * 3600; bitis.append(b)
            nedenler.append(f"Son görselden {E['flow_gorsel_sonrasi_video_saat']} saat geçmedi; video en erken {_metin(b)}.")
    b = max(bitis)
    if nedenler: return {"izinli": False, "kod": BEKLE, "bekle_bitis": b, "nedenler": nedenler}
    return {"izinli": True, "kod": IZINLI, "bekle_bitis": None, "nedenler": []}


def bekle_bitis(tur, kip="elle", kok=None, E=None, simdi=None):
    """İzin varsa şimdi; beklemeyle açılacaksa o an (epoch); kilit ya da kip engeli varsa None."""
    d = izinli_mi(tur, kip, kok, E, simdi)
    return _simdi(simdi) if d["izinli"] else d["bekle_bitis"]


def durum(kip="elle", kok=None, E=None, simdi=None):
    E = _e(E, kok); simdi = _simdi(simdi); T = tempo_oku(kok)
    return {"_surum": 1, "_uretim": {"arac_surum": SURUM, "zaman": _iso(simdi)}, "kilit": kilit_durumu(kok, E, simdi),
            "tempo": tempo_durumu(kip, kok, E, simdi), "gunluk": gunluk_sayim(kok, simdi), "son_gorsel": son_gorsel(kok),
            "tavan": {"gorsel_gunluk": E["flow_gorsel_gunluk_tavan"], "gorsel_sonrasi_video_saat": E["flow_gorsel_sonrasi_video_saat"]},
            "ilk_blok_elle": _ilk_blok_elle_bekliyor(T, simdi), "yavaslatma": T.get("yavaslatma"),
            "izin": {t: izinli_mi(t, kip, kok, E, simdi) for t in TURLER}}


# ------------------------------------------------------------------ komut satırı
def _yazdir(d):
    k = d["kilit"]
    if k["kilitli"]:
        print(f"FLOW KİLİTLİ ({k['neden']}). En erken {k['en_erken_metin']}. GÖNDER'e basma, sayfayı yenileme.")
        print("  Kalkması için: en erken zamandan sonra Flow'da ELLE 1 video dene; başarılıysa UYARI_GECTI.bat.")
    else: print("Flow kilidi yok.")
    t = d["tempo"]
    print(f"Sonraki izinli gönderim: {'şimdi' if t['kalan_sn'] <= 0 else _metin(t['sonraki_izin'])}"
          f"{' (mola)' if t['molada'] else ''} · çarpan {t['carpan']}")
    g = d["gunluk"]
    print(f"Bugün ({g['tarih']}): görsel {g['gorsel']}/{d['tavan']['gorsel_gunluk']} · video {g['video']}")
    if d["ilk_blok_elle"]: print("UYARI_GECTI sonrası: ilk blok ELLE (gece kipi kapalı).")
    for tur, i in d["izin"].items():
        print(f"  {tur}: {'izinli' if i['izinli'] else '; '.join(i['nedenler'])}")


ONAY_SOZU = ("ben kullanıcıyım", "ben kullaniciyim")


def tty_mi():
    try: return bool(sys.stdin and sys.stdin.isatty() and sys.stdout and sys.stdout.isatty())
    except (AttributeError, ValueError, OSError): return False


def kullanici_onayi():
    """UYARI_GECTI yalnız kullanıcının işidir: etkileşimli konsol (stdin ve stdout TTY) ve elle yazılan onay sözü şart.
    Ajan, betik ya da boru (TTY yok) → False; bayraklar (--ben-kullaniciyim dahil) bunu atlatmaz."""
    if not tty_mi(): return False
    try: c = input("Bu kilidi SEN mi kaldırıyorsun? Onaylamak için 'ben kullanıcıyım' yaz: ").strip().lower()
    except (EOFError, OSError): return False
    return c in ONAY_SOZU


def main(argv):
    a = list(argv); kip = "elle"
    if "--kip" in a:
        i = a.index("--kip")
        if i + 1 >= len(a): print(__doc__); return KULLANIM
        kip = a[i + 1]; del a[i:i + 2]
    try:
        if not a or a == ["--json"]:
            d = durum(kip)
            if a: print(json.dumps(d, ensure_ascii=False, indent=1))
            else: _yazdir(d)
            return 0
        if a[0] == "--izin" and len(a) == 2 and a[1] in TURLER:
            d = izinli_mi(a[1], kip)
            print("izinli" if d["izinli"] else "\n".join(d["nedenler"]))
            return d["kod"]
        if a[0] == "--uyari-gecti" and set(a[1:]) <= {"--elle-video-basarili", "--ben-kullaniciyim"}:
            if not kullanici_onayi():
                print("Kilidi yalnız sen kaldırırsın: UYARI_GECTI.bat'ı kendin çift tıklayıp aç ve soruları yanıtla. "
                      "(Etkileşimli konsol yok: hiçbir şey yapılmadı.)")
                return KILITLI
            evet = "--elle-video-basarili" in a
            if not evet:
                c = input("Flow'da ELLE 1 video denedin ve sorunsuz oldu mu? (E/H): ").strip().lower()
                evet = c in ("e", "evet", "y", "yes")
            d = uyari_gecti(evet)
            if d["sonuc"] == "kaldirildi":
                print(f"Flow kilidi kalktı (yalnız bugün, {d['gecerli_gun']}). Bugün tempo {d['carpan']}× yavaş; "
                      f"yarın ilk blok ELLE gider.")
                return 0
            print("\n".join(d["nedenler"]))
            return 0 if d["sonuc"] == "kilit_yok" else KILITLI
    except (YukHatasi, ortak.YolYok, esikler.EsikHatasi) as e:
        print("!!", e); return KULLANIM
    print(__doc__); return KULLANIM


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
