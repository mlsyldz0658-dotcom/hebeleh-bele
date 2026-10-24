"""KÖR PAKET — habersiz seyirci ve kör roller için beyaz listeli, ad maskeli, aşamalı paket (TASARIM §6.2, D-18, [CM2] §4.5.9).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"; tur YZ_FILM_GOREV'deki GOREV.json'dan ya da --tur):
  python kor_paket.py --kip kagit  [--tur N] [--kaynak <senaryo.json>] --film <film>
  python kor_paket.py --kip plan   [--tur N] --film <film>               (SAHNELER.json v2 + HIKAYE.json)
  python kor_paket.py --kip ilk2dk [--tur N] [--kaynak <senaryo.json>] --film <film>
  python kor_paket.py --denetle <paket klasörü> --film <film>          sızıntı denetimi (0 temiz · 1 sızıntı)
  python kor_paket.py --kip animatik|kurgu|kesit|kesici|kapak ...       izleme kipleri: HENÜZ YOK (§9 adım 14, PR-10) → 4
Çıktı (kâğıt kipleri):
  <film>/_KOR_PAKET/<kip>_t<tur>/<A|B|C>/<P0..P3>/EKRAN.md   aşamalı bölümler (film.py asama-ilerlet GIRDI/<bolum>/'e kopyalar)
  <film>/_KOR_PAKET/<kip>_ilk2dk_t<tur>/ILK2DK_<A|B|C>.md      başlık + kapak tarifi + ilk 120 sn
  <film>/_KOR_PAKET/<kip>_t<tur>/ESLESTIRICI/ANAHTAR.json      özet eşleştiricinin anahtarı (seyirci klasörlerine GİRMEZ)
  <film>/_KOR_PAKET/<kip>_t<tur>/PAKET.json                    _uretim zarfı, bölüm dağılımı, sızıntı denetimi sonucu
Kurallar: içerik YALNIZ beyaz listeden kurulur (görülen satırlar, duyulan replik, ekran dışı sesler, yer/zaman kartı, zaman kodu,
sahne/plan sırası; plan kipinde kadraj düz sözle ve eylem zincirinin görünür adımları). amac, duygu, hedef_duygu, yogunluk, vurus,
risk, merak/kurulum/ironi kimlikleri, sahne_degeri, seyirci_ogrenir, ekranda_bilgi, kagit bloğu, oyunculuk, istemler, raporlar asla
yazılmaz. Karakter adı ve hitapları (maske.takma_adlar) ekranda ilk kez sözle söylenene ya da yazıyla gösterilene kadar görünüş
etiketiyle anılır (tek maskeleme kodu: Maske). Bölümler: P0 = 0–120 sn, sonra hikâye partileri P1, P2, P3. Persona satırı: kâğıt ve
plan kiplerinde 3 × A (D-18). Paket yazıldıktan sonra kendi sızıntı denetiminden geçer; sızıntı varsa yayımlanmaz (çıkış 1).
Eski paket silinmez: _KOR_PAKET/_ESKI/'ye taşınır.
Çıkış kodları: 0 BİTTİ · 1 HATA (girdi yok/bozuk, sızıntı) · 4 ORTAM (kip henüz yok ya da v1 dosyası).
"""
import os, sys, re, json, time, shutil, hashlib, argparse
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

SURUM = "kor_paket 1.0"
KAGIT_KIPLERI = ("kagit", "plan", "ilk2dk")
IZLEME_KIPLERI = ("animatik", "kurgu", "kesit", "kesici", "kapak")
BOLUMLER = ("P0", "P1", "P2", "P3")
KLASORLER = ("A", "B", "C")
P0_SN = 120
PERSONA = {
    "A": "Persona A: akşam televizyonda film izleyen, 25–55 yaşında, fantastik ve savaş filmlerini seven bir YouTube seyircisisin.",
    "B": "Persona B: telefondan yarım dikkatle izleyen, ilk 30 saniyede kalıp kalmayacağına karar veren bir YouTube seyircisisin.",
    "C": "Persona C: serinin önceki filmini izlemiş, geri dönen bir seyircisin.",
}
# klasör → persona (D-18): kâğıt/plan 3 × A; izleme kiplerinde 2 × A + 1 × B (izleme kipleri PR-10)
PERSONA_ESLEME = {"kagit": {"A": "A", "B": "A", "C": "A"}, "plan": {"A": "A", "B": "A", "C": "A"},
                  "ilk2dk": {"A": "A", "B": "A", "C": "A"}, "izleme": {"A": "A", "B": "A", "C": "B"}}
YASAK_ALANLAR = ("amac", "duygu", "hedef_duygu", "yogunluk", "vurus", "risk", "merak_ac", "merak_kapat", "kurulum", "kullanim_bilgi",
                 "ironi", "sahne_degeri", "seyirci_ogrenir", "ekranda_bilgi", "kagit", "bilgi_degisimi", "gorsel_istem", "hareket_istem",
                 "oyunculuk", "tasidigi", "neden_simdi", "logline", "istek", "korku", "yara", "sir", "yay", "risk_uretim",
                 "gorsel_istem_yedek", "hareket_istem_yedek", "istem_elle", "alt_metin", "ic_durum")
KADRAJ = {"UG": "uzak genel plan", "GEN": "genel plan", "G": "genel plan", "B": "boy plan", "DB": "diz boy plan", "O": "orta plan",
          "OY": "orta yakın plan", "Y": "yakın plan", "CY": "çok yakın plan", "D": "detay plan", "OU": "omuz üstü plan"}
R_KIMLIK = re.compile(r"^R\d{3,}$")


class GirdiHatasi(Exception):
    pass


def simdi(): return time.strftime("%Y-%m-%dT%H:%M:%S")


def zk(sn):
    sn = max(0, int(round(sn))); return "%02d:%02d" % (sn // 60, sn % 60)


def _imza(*yollar):
    h = hashlib.sha1()
    for p in yollar:
        if p and os.path.isfile(p):
            with open(p, "rb") as f: h.update(f.read())
    return h.hexdigest()[:8]


def _yaz(p, metin):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p + ".tmp", "w", encoding="utf-8", newline="\n") as f: f.write(metin)
    os.replace(p + ".tmp", p)


# ---- ad maskeleme (bütün kiplerde tek kod) -------------------------------------------------------------------------
class Maske:
    """Karakter adı ve hitapları ekranda söylenene/yazılana kadar görünüş etiketiyle değiştirir."""
    def __init__(self, karakterler, ses_etiketleri=None):
        self.k = {}
        for kid, v in (karakterler or {}).items():
            v = v or {}; m = v.get("maske") or {}
            ad = v.get("ad") or kid.replace("_", " ").title()
            etiket = m.get("etiket_anonim_en") or v.get("tarif") or "a person on screen"
            self.k[kid] = {"ad": ad, "etiket": etiket, "takma": [t for t in (m.get("takma_adlar") or []) if t],
                           "ses": (ses_etiketleri or {}).get(kid) or v.get("ses_etiketi_tr")}
        self.kurulan = set()
        self._re = {kid: re.compile(r"(?<![\w])(" + "|".join(re.escape(x) for x in sorted([v["ad"]] + v["takma"], key=len, reverse=True))
                                    + r")(?![\w])", re.I) for kid, v in self.k.items()}
        self._ad_re = {kid: re.compile(r"(?<![\w])" + re.escape(v["ad"]) + r"(?![\w])", re.I) for kid, v in self.k.items()}

    def kopya_durum(self): return set(self.kurulan)

    def maskele(self, metin):
        """Görülen/tarif metni: kurulmamış karakterin adı ve hitapları → [etiket]."""
        s = str(metin or "")
        for kid, rx in self._re.items():
            if kid not in self.kurulan: s = rx.sub("[" + self.k[kid]["etiket"] + "]", s)
        return s

    def anan(self, kid, gorunur=True):
        """Konuşan/özne etiketi."""
        if kid not in self.k: return "[" + ("ekrandaki kişi" if gorunur else "ekran dışından bir ses") + "]"
        if kid in self.kurulan: return self.k[kid]["ad"].upper()
        if gorunur: return "[" + self.k[kid]["etiket"] + "]"
        return "[" + (self.k[kid]["ses"] or "ekran dışından bir ses") + "]"

    def duyuldu(self, metin, ad_soyler=()):
        """Duyulan söz ya da ekranda yazı: adı geçen karakter artık kurulmuştur."""
        for kid in ad_soyler or ():
            if kid in self.k: self.kurulan.add(kid)
        for kid, rx in self._ad_re.items():
            if rx.search(str(metin or "")): self.kurulan.add(kid)

    def kurulmamis_adlar(self, kurulan):
        return {kid: [v["ad"]] + v["takma"] for kid, v in self.k.items() if kid not in kurulan}


# ---- girdiler ------------------------------------------------------------------------------------------------------
def senaryo_bul(film, kaynak=None):
    if kaynak:
        p = kaynak if os.path.isabs(kaynak) else os.path.join(film, kaynak)
        if not os.path.isfile(p): raise GirdiHatasi("Kaynak yok: %s" % kaynak)
        return p
    d = os.path.join(film, "_HIKAYE_ODASI"); en = None
    if os.path.isdir(d):
        for f in os.listdir(d):
            m = re.match(r"06_SENARYO_v(\d+)\.json$", f)
            if m and (en is None or int(m.group(1)) > en[0]): en = (int(m.group(1)), os.path.join(d, f))
    if en: return en[1]
    p = os.path.join(film, "HIKAYE.json")
    if os.path.isfile(p): return p
    raise GirdiHatasi("Senaryo yok (_HIKAYE_ODASI/06_SENARYO_v<N>.json ya da HIKAYE.json).")


def json_zorunlu(p):
    v = ortak.json_oku(p)
    if not isinstance(v, dict): raise GirdiHatasi("Okunamadı ya da bozuk: %s" % os.path.basename(p))
    return v


def ses_etiketleri(film):
    s = ortak.json_oku(os.path.join(film, "_SES", "SES_PROFILLERI.json"), {}) or {}
    k = s.get("karakterler") if isinstance(s.get("karakterler"), dict) else s
    return {kid: (v or {}).get("ses_etiketi_tr") for kid, v in (k or {}).items() if isinstance(v, dict) and v.get("ses_etiketi_tr")}


def parti_esleme(h):
    """sahne id → 'P1'..'P3' (hikaye_partisi alanı; yoksa partiler[].sahneler aralığı)."""
    sira = [s.get("id") for s in h.get("sahneler") or []]
    es = {}
    for p in h.get("partiler") or []:
        ss = p.get("sahneler") or []
        if len(ss) == 2 and ss[0] in sira and ss[1] in sira:
            for x in sira[sira.index(ss[0]): sira.index(ss[1]) + 1]: es[x] = p.get("id")
        else:
            for x in ss: es[x] = p.get("id")
    return es


def bolum_adi(parti):
    m = re.search(r"(\d+)", str(parti or "1"))
    n = int(m.group(1)) if m else 1
    return "P%d" % min(3, max(1, n))


# ---- kâğıt kipi: sahne metni ---------------------------------------------------------------------------------------
def replik_bul(h):
    return {r.get("id"): r for r in h.get("replikler") or [] if isinstance(r, dict) and r.get("id")}


def sahne_satirlari(s, rep, mk, no):
    """Bir sahnenin beyaz listeli metni. Maske durumu sahne başında dondurulur (görülen satırlar); replikler sırayla kurar."""
    e = s.get("ekran") or {}
    out = []
    kart = e.get("kart")
    if kart:
        kart_metin = kart if isinstance(kart, str) else (kart.get("metin") or kart.get("yazi") or "")
        if kart_metin:
            out.append("EKRANDA YAZI: " + str(kart_metin)); mk.duyuldu(kart_metin)
    gor = [mk.maskele(x) for x in e.get("gorulen") or [] if x]
    if gor: out += ["GÖRÜLEN:"] + ["- " + x for x in gor]
    duy = []
    for d in e.get("duyulan") or []:
        r = rep.get(d) if isinstance(d, str) and R_KIMLIK.match(d) else (d if isinstance(d, dict) else None)
        if r is None and isinstance(d, str): duy.append("- " + mk.maskele(d)); continue
        if not r: continue
        gorunur = not (r.get("ekran_disi") or r.get("ekran_disi_ses"))
        duy.append("- %s: \"%s\"" % (mk.anan(r.get("karakter"), gorunur), r.get("metin") or ""))
        mk.duyuldu(r.get("metin"), r.get("ad_soyler") or ())
    if duy: out += ["DUYULAN:"] + duy
    ed = [mk.maskele(x) for x in e.get("ekran_disi") or [] if x]
    if ed: out.append("EKRAN DIŞI SES: " + ", ".join(ed))
    return out


def kagit_sahneleri(h, mk):
    """[(bolum, baslangic_sn, sahne_id, satirlar)] — sırayla, maske durumuyla."""
    rep = replik_bul(h); pe = parti_esleme(h); t = 0.0; out = []
    for i, s in enumerate(h.get("sahneler") or [], 1):
        if not isinstance(s, dict): continue
        sid = s.get("id") or "S%02d" % i
        bol = "P0" if t < P0_SN else bolum_adi(s.get("hikaye_partisi") or pe.get(sid))
        sat = sahne_satirlari(s, rep, mk, i)
        out.append((bol, t, sid, ["## [%s] Sahne %d (%s)" % (zk(t), i, sid)] + sat + [""]))
        t += float(s.get("hedef_sure_sn") or 60)
    return out


# ---- plan kipi ------------------------------------------------------------------------------------------------------
def _soz(kod): return str(kod or "").replace("_", " ").strip()


def plan_satirlari(p, mk, karakter_ids):
    z = p.get("zanaat") or {}; kam = z.get("kamera") or {}; out = []
    kadraj = KADRAJ.get(str(kam.get("kadraj") or "").upper(), _soz(kam.get("kadraj")).lower())
    parca = [x for x in (kadraj, _soz(kam.get("aci")), ("sabit kamera" if kam.get("hareket_tipi") == "sabit" else _soz(kam.get("hareket_tipi"))))
             if x]
    if parca: out.append("KADRAJ: " + ", ".join(parca))
    kd = [mk.anan(x.get("id")) for x in z.get("kadrajdakiler") or [] if isinstance(x, dict) and x.get("id") in karakter_ids]
    if kd: out.append("KADRAJDA: " + ", ".join(kd))
    gorunen = {x.get("id") for x in z.get("kadrajdakiler") or [] if isinstance(x, dict)}
    rep = p.get("replik") or {}
    adim = []
    for a in z.get("eylem_zinciri") or []:
        if not isinstance(a, dict): continue
        zaman = "%s–%s sn" % (a.get("bas", "?"), a.get("bit", "?"))
        if a.get("tur") == "konusma":
            if rep.get("metin"):
                kim = rep.get("karakter") or a.get("ozne")
                adim.append("- %s: %s der: \"%s\"" % (zaman, mk.anan(kim, kim in gorunen), rep["metin"]))
                mk.duyuldu(rep["metin"], rep.get("ad_soyler") or ())
            continue
        ozne = mk.anan(a.get("ozne")) if a.get("ozne") in karakter_ids else mk.maskele(_soz(a.get("ozne")))
        ek = " ".join(x for x in (_soz(a.get("govde")), _soz(a.get("olcu")), ("(%s)" % _soz(a["hiz"])) if a.get("hiz") else "") if x)
        hedef = a.get("hedef")
        hedef = (mk.anan(hedef) if hedef in karakter_ids else mk.maskele(_soz(hedef))) if hedef else ""
        adim.append("- %s: %s %s%s%s" % (zaman, ozne, mk.maskele(_soz(a.get("fiil"))), (" → " + hedef) if hedef else "",
                                         (" · " + mk.maskele(ek)) if ek else ""))
    if adim: out += ["GÖRÜLEN:"] + adim
    eds = z.get("ekran_disi_ses")
    if eds: out.append("EKRAN DIŞI SES: " + mk.maskele(eds if isinstance(eds, str) else eds.get("metin") or _soz(eds.get("tur"))))
    fs = (z.get("ses") or {}).get("flow_sound")
    if fs: out.append("SES: " + mk.maskele(re.sub(r"^\s*Sound:\s*", "", str(fs))))
    return out


def plan_sahneleri(sahneler_v2, mk, karakter_ids):
    t = 0.0; out = []
    planlar = sorted([p for p in sahneler_v2.get("sahneler") or [] if isinstance(p, dict)],
                     key=lambda p: float(p.get("sira", p.get("no", 0)) or 0))
    for i, p in enumerate(planlar, 1):
        bol = "P0" if t < P0_SN else bolum_adi(p.get("parti"))
        sat = plan_satirlari(p, mk, karakter_ids)
        out.append((bol, t, str(p.get("no", i)), ["## [%s] Plan %d" % (zk(t), i)] + sat + [""]))
        k = p.get("kullanim") or {}; d = p.get("_derlenir") or {}; z = p.get("zanaat") or {}
        t += float(k.get("sure") or d.get("sure_sn") or z.get("klip_sn") or 8)
    return out


# ---- paket kurma ----------------------------------------------------------------------------------------------------
def tur_bul(arg_tur):
    if arg_tur: return int(arg_tur)
    gd = os.environ.get("YZ_FILM_GOREV")
    g = ortak.json_oku(os.path.join(gd, "GOREV.json"), {}) if gd else {}
    return int((g or {}).get("tur_no") or 1)


def bolum_metni(kip, bol, persona, birimler, bos_not):
    bas = ["# Bölüm %s · %s kipi" % (bol, "kâğıt" if kip == "kagit" else "plan"), "", PERSONA[persona], ""]
    if not birimler: return "\n".join(bas + [bos_not, ""])
    return "\n".join(bas + [x for b in birimler for x in b[3]])


def ilk2dk_metni(h, birimler, persona, mk_bas):
    bas = ["# İlk 2 dakika", "", PERSONA[persona], ""]
    b = (h.get("baslik") or {})
    baslik = b.get("secilen") if isinstance(b, dict) else b
    if baslik: bas.append("BAŞLIK: " + str(baslik))
    kapak = next((v.get("ekranda") for v in h.get("vaat_sozlesmesi") or [] if isinstance(v, dict) and v.get("oge") == "kapak_imgesi"), None)
    if kapak: bas.append("KAPAK: " + mk_bas.maskele(kapak))
    bas.append("")
    return "\n".join(bas + [x for bb in birimler if bb[1] < P0_SN for x in bb[3]])


def anahtar(h, mk):
    return {"_not": "Yalnız ozet-eslestirici (kör rol) için; seyirci klasörlerine girmez.",
            "anahtar_olgular": [{k: o.get(k) for k in ("id", "olgu", "kritik", "hikaye_partisi")} for o in h.get("anahtar_olgular") or []],
            "merak": [{"id": m.get("id"), "soru": m.get("soru")} for m in h.get("MERAK_DEFTERI") or []],
            "kurulumlar": [{"id": k.get("id"), "ne": k.get("ne")} for k in h.get("KURULUMLAR") or []],
            "maske": [{"id": kid, "ad": v["ad"], "etiket": v["etiket"], "takma_adlar": v["takma"]} for kid, v in mk.k.items()]}


def yasak_degerler(*kaynaklar):
    """Kaynaklardaki yasak alan değerleri (≥ 5 karakter metinler); sızıntı denetimi bunların pakette geçmediğini arar."""
    out = set()
    def topla(v):
        if isinstance(v, str):
            if len(v.strip()) >= 5: out.add(v.strip())
        elif isinstance(v, dict):
            for x in v.values(): topla(x)
        elif isinstance(v, list):
            for x in v: topla(x)
    def gez(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in YASAK_ALANLAR: topla(v)
                else: gez(v)
        elif isinstance(o, list):
            for x in o: gez(x)
    for k in kaynaklar:
        gez(k)
        if isinstance(k, dict):
            for o in k.get("anahtar_olgular") or []: topla(o.get("olgu"))
            for m in k.get("MERAK_DEFTERI") or []: topla(m.get("soru"))
            for x in (k.get("KURULUMLAR") or []) + (k.get("IRONILER") or []): topla(x.get("ne"))
    return out


def denetle_klasor(kok, yasak, mk_adlari):
    """Seyirci klasörlerinde yasak değer ve (bölüm başındaki maske durumuna göre) kurulmamış ad. → hata listesi."""
    hatalar = []
    for dp, _, fs in os.walk(kok):
        if "ESLESTIRICI" in dp.replace("\\", "/").split("/"): continue
        for f in fs:
            if not f.endswith(".md"): continue
            p = os.path.join(dp, f)
            with open(p, encoding="utf-8") as fh: metin = fh.read()
            for y in yasak:
                if (len(y) >= 12 and y in metin) or (len(y) < 12 and re.search(r"(?<![\w])" + re.escape(y) + r"(?![\w])", metin)):
                    hatalar.append({"dosya": os.path.relpath(p, kok), "tur": "yasak_alan", "deger": y[:40]})
            adlar = mk_adlari.get(os.path.relpath(p, kok).replace("\\", "/"), {})
            for sat in metin.splitlines():
                acik = re.sub(r"\"[^\"]*\"", "", sat)                      # duyulan söz tırnak içindedir (duyulan serbest)
                for kid, ad_list in adlar.items():
                    for a in ad_list:
                        if re.search(r"(?<![\w\[])" + re.escape(a) + r"(?![\w])", acik, re.I) and not re.search(r"\[[^\]]*" + re.escape(a), acik, re.I):
                            hatalar.append({"dosya": os.path.relpath(p, kok), "tur": "ad", "karakter": kid})
    return hatalar


def eskiyi_tasi(film, hedef):
    if not os.path.exists(hedef): return
    d = os.path.join(film, "_KOR_PAKET", "_ESKI"); os.makedirs(d, exist_ok=True)
    shutil.move(hedef, os.path.join(d, "%s_%s" % (os.path.basename(hedef), time.strftime("%Y%m%d_%H%M%S"))))


def paket_kur(film, kip, tur, kaynak=None, gorev=None):
    film = os.path.abspath(film)
    ana_kip = "kagit" if kip == "ilk2dk" else kip
    if ana_kip == "kagit":
        kp = senaryo_bul(film, kaynak); h = json_zorunlu(kp); kaynak_dosyalar = [kp]; v2 = None
    else:
        sp = os.path.join(film, "SAHNELER.json"); v2 = json_zorunlu(sp)
        if int(v2.get("_surum", 1) or 1) < 2: raise OrtamHatasi("plan kipi SAHNELER.json v2 ister (_surum: 2).")
        hp = os.path.join(film, "HIKAYE.json"); h = ortak.json_oku(hp, {}) or {}; kaynak_dosyalar = [sp, hp]
    kar = dict(h.get("karakterler") or {})
    if v2:
        for kid, v in (v2.get("karakterler") or {}).items(): kar.setdefault(kid, {}).setdefault("tarif", (v or {}).get("tarif"))
    mk = Maske(kar, ses_etiketleri(film))
    birimler = kagit_sahneleri(h, mk) if ana_kip == "kagit" else plan_sahneleri(v2, mk, set(kar))
    if not birimler: raise GirdiHatasi("Pakete girecek sahne/plan yok.")
    kok_ad = "%s_t%d" % (ana_kip, tur)
    hedef = os.path.join(film, "_KOR_PAKET", kok_ad); hedef_ik = os.path.join(film, "_KOR_PAKET", "%s_ilk2dk_t%d" % (ana_kip, tur))
    gecici = os.path.join(film, "_KOR_PAKET", "." + kok_ad + ".yeni"); gecici_ik = gecici + "_ik"
    for g in (gecici, gecici_ik):
        if os.path.exists(g): eskiyi_tasi(film, g)
    mk_adlari = {}
    kurulan_once = denetim_durumlari(h, v2, kar, film, ana_kip)
    esleme = PERSONA_ESLEME[ana_kip]
    for klasor in KLASORLER:
        for bol in BOLUMLER:
            bb = [b for b in birimler if b[0] == bol]
            rel = "%s/%s/EKRAN.md" % (klasor, bol)
            _yaz(os.path.join(gecici, klasor, bol, "EKRAN.md"),
                 bolum_metni(ana_kip, bol, esleme[klasor], bb, "(Bu bölümde sahne yok; raporuna yalnız 'bölüm boş' yaz.)"))
            mk_adlari[rel] = mk.kurulmamis_adlar(kurulan_once.get(bol, set()))
    mk_ik = Maske(kar, ses_etiketleri(film))
    ilk = kagit_sahneleri(h, mk_ik) if ana_kip == "kagit" else plan_sahneleri(v2, mk_ik, set(kar))
    for klasor in KLASORLER:
        _yaz(os.path.join(gecici_ik, "ILK2DK_%s.md" % klasor), ilk2dk_metni(h, ilk, esleme[klasor], Maske(kar)))
    ortak.atomik_yaz(os.path.join(gecici, "ESLESTIRICI", "ANAHTAR.json"), anahtar(h, mk))
    yasak = yasak_degerler(h, v2)
    hatalar = denetle_klasor(gecici, yasak, mk_adlari)
    ik_adlar = {"ILK2DK_%s.md" % k: mk.kurulmamis_adlar(set()) for k in KLASORLER}
    hatalar += denetle_klasor(gecici_ik, yasak, ik_adlar)
    manifest = {"_surum": 1, "_uretim": {"asama": os.environ.get("YZ_FILM_ASAMA") or ("A06" if ana_kip == "kagit" else "A07e"),
                                         "gorev": gorev, "girdi_imza": _imza(*kaynak_dosyalar), "arac_surum": SURUM, "esik_surum": None,
                                         "sonuc": "HATA" if hatalar else "GEC", "zaman": simdi(),
                                         "ortam": "yerel" if os.name == "nt" else "bulut"},
                "kip": ana_kip, "tur": tur, "kaynak": [os.path.relpath(p, film) for p in kaynak_dosyalar if os.path.isfile(p)],
                "klasorler": {k: esleme[k] for k in KLASORLER}, "bolumler": {b: [x[2] for x in birimler if x[0] == b] for b in BOLUMLER},
                "ilk2dk": "_KOR_PAKET/%s_ilk2dk_t%d" % (ana_kip, tur), "maske_sayisi": len(mk.k),
                "sizinti": {"yasak_alan": sum(1 for x in hatalar if x["tur"] == "yasak_alan"), "ad": sum(1 for x in hatalar if x["tur"] == "ad")},
                "hatalar": hatalar[:50]}
    if hatalar:
        red = os.path.join(film, "_KOR_PAKET", "_RED"); os.makedirs(red, exist_ok=True)
        for g in (gecici, gecici_ik):
            shutil.move(g, os.path.join(red, os.path.basename(g).lstrip(".") + "_" + time.strftime("%Y%m%d_%H%M%S")))
        ortak.atomik_yaz(os.path.join(red, "%s_SIZINTI.json" % kok_ad), manifest)
        return 1, manifest
    ortak.atomik_yaz(os.path.join(gecici, "PAKET.json"), manifest)
    for g, h_ in ((gecici, hedef), (gecici_ik, hedef_ik)):
        eskiyi_tasi(film, h_); os.replace(g, h_)
    return 0, manifest


def denetim_durumlari(h, v2, kar, film, ana_kip):
    """Her bölümün SONUNDA kurulmuş karakterler (bağımsız geçiş). Bölüm dosyası denetimi bunları serbest sayar; satır sırasına
    göre maskeleme test_kor_paket'te ayrıca sınanır."""
    mk = Maske(kar, ses_etiketleri(film)); son = {}
    for b in (kagit_sahneleri(h, mk) if ana_kip == "kagit" else plan_sahneleri(v2, mk, set(kar))):
        son[b[0]] = mk.kopya_durum()
    return son


class OrtamHatasi(Exception):
    pass


def main(argv=None):
    ap = argparse.ArgumentParser(description="Kör paket (kâğıt kipleri).")
    ap.add_argument("--kip"); ap.add_argument("--tur", type=int); ap.add_argument("--kaynak"); ap.add_argument("--film")
    ap.add_argument("--denetle"); ap.add_argument("--saglayici"); ap.add_argument("--json", action="store_true")
    o = ap.parse_args(argv)
    film = o.film or os.environ.get("YZ_FILM_FILM")
    if not film or not os.path.isdir(film):
        print("!! --film <film klasörü> gerekli."); return 1
    if o.denetle:
        h = ortak.json_oku(os.path.join(film, "HIKAYE.json"), {}) or {}
        hatalar = denetle_klasor(o.denetle, yasak_degerler(h, ortak.json_oku(os.path.join(film, "SAHNELER.json"), {})), {})
        print(json.dumps({"sizinti": len(hatalar), "hatalar": hatalar[:20]}, ensure_ascii=False)); return 1 if hatalar else 0
    if o.kip in IZLEME_KIPLERI:
        print("Kör paketin izleme kipi '%s' henüz yok (TASARIM §9 adım 14, PR-10: kor_paket izleme kipleri). "
              "Bu aşama bu kurulumda yürüyemez." % o.kip); return 4
    if o.kip not in KAGIT_KIPLERI:
        print("!! Bilinmeyen kip: %s (kâğıt: %s; izleme: %s)" % (o.kip, ", ".join(KAGIT_KIPLERI), ", ".join(IZLEME_KIPLERI))); return 1
    gorev = os.path.basename(os.environ.get("YZ_FILM_GOREV") or "") or None
    try:
        kod, m = paket_kur(film, o.kip, tur_bul(o.tur), o.kaynak, gorev)
    except OrtamHatasi as e:
        print("!! " + str(e)); return 4
    except GirdiHatasi as e:
        print("!! " + str(e)); return 1
    if kod:
        print("!! Kör pakette sızıntı bulundu (%d); paket yayımlanmadı, _KOR_PAKET/_RED/'de." % len(m["hatalar"]))
    else:
        print(json.dumps({"paket": "_KOR_PAKET/%s_t%d" % (m["kip"], m["tur"]), "bolumler": m["bolumler"], "sizinti": m["sizinti"]},
                         ensure_ascii=False) if o.json else "Kör paket hazır: _KOR_PAKET/%s_t%d (sızıntı 0)" % (m["kip"], m["tur"]))
    return kod


if __name__ == "__main__":
    sys.exit(main())
