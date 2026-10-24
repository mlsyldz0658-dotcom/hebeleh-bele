"""PLAN DENETİM — yönetmen kâğıdının kod kapısı: harita, sahne planları ve film düzeyi Z0 (TASARIM §6.4, §7.2 Z0, D-13, D-22; [YN2] §4.7 Y01–Y60;
ZN §2.1–2.5, §6.2 Z0 #4–#20).

Kullanım (film.py calis çağırır: "<arac> <args> --film <film>"):
  python plan_denetim.py --harita --film <film>          A07a: parti haritaları (HARITA_P<n>.json) + kroki biçimi → _RAPOR/HARITA_t<tur>.json
  python plan_denetim.py --sahne S12 --film <film>       A07b: tek sahne grubunun planları → _RAPOR/Z0_SAHNE_S12.json
  python plan_denetim.py --sahne --tum --film <film>     A07b: bütün sahne grubu planları → _RAPOR/Z0_SAHNE_t<tur>.json
  python plan_denetim.py --tum --film <film>             A07c: birleşik SAHNELER.json → _RAPOR/Z0_P<n>.json (parti başına) + Z0_FILM.json;
                                                         HATA → KUYRUK/YENIDEN_YAZ.json (aynı sahnenin yönetmeni)
  python plan_denetim.py --dosya CIKTI/plan.json --film <film>   SubagentStop: ajanın tek sahne planı (diskteki öbür planlarla birlikte)
  Seçenek: --tur N (görev bağlamı yoksa rapor turu).
Kodda: plan_kurallari(p, s, E, B) · sahne_kurallari(sid, planlar, sg, E) · film_kurallari(s, E) · denetle(kok, sahne=None, tum=False)
Kapsam: atomik eylem zinciri (Y01–Y10), konuşma ve L/J (Y29–Y36, Y59; ZN §2.3 formülü − ses_tasma_sn), kurgu bağı ve kare zinciri
  (Y37–Y43, Y54–Y56), kimlik/referans/istem (Y44–Y49), sahne kapsaması (Y20–Y22, Y27, Y50–Y53), plan süresi / plan tipi aralığı (Z0 #4),
  oyunculuk (ifade zorunlu; plan_sema). Geometri (Y14, Y17–Y19, Y23, Y28, Y60) kroki.py'den, durum zinciri (Y10–Y16, K0 sıçramaları,
  duygu sıçraması) dunya_defteri.py'den aynı rapora alınır (kancada tek rapor; A07c'de K0'ın sahibi dunya_defteri'dir).
  Hesaplanamayan geometri HESAPLANAMADI = HATA (kroki.py).
Çıkış kodları: 0 GEÇ/BAYRAK · 1 HATA/KISMI ya da bozuk girdi · 2 film/plan yok · 4 kullanım.
"""
import os, sys, re, math, glob
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, plan_ortak as po

SURUM = "plan_denetim 1.0"
FIZIKSEL, MIKRO, KONUSMA, SES = "fiziksel", "mikro", "konusma", "ses_vurusu"
IC_DURUM_EN = ("realizes", "realises", "decides", "remembers", "knows", "understands", "thinks", "feels", "wonders", "notices")
IC_DURUM_TR = ("fark eder", "anlar", "karar verir", "hatırlar", "bilir", "düşünür", "hisseder", "sezer", "farkına var")
CIPLAK_YON = re.compile(r"\b(left|right)\b", re.I)
YON_ON = re.compile(r"\b(her|his|their|its|own|frame|screen|camera|\w+'s)\s+([a-z-]+\s+)?$", re.I)
KONUSAN_KADRAJ = ("O", "OY", "Y")
GENIS_KADRAJ = ("EG", "G", "OG", "IK")


# --- küçük yardımcılar ------------------------------------------------------------------------------------------
def _adimlar(z): return sorted([a for a in z.get("eylem_zinciri") or [] if isinstance(a, dict)], key=lambda a: (a.get("bas") or 0))
def _sayi(x): return isinstance(x, (int, float)) and not isinstance(x, bool)
def _sure(a): return (a.get("bit") or 0) - (a.get("bas") or 0) if _sayi(a.get("bas")) and _sayi(a.get("bit")) else None
def _kad_kademe(k): return ((po.sozluk("plan").get("kadraj") or {}).get(k) or {}).get("kademe")


def _ins(z): return z.get("plan_tipi") in set(po.sozluk("plan").get("insansiz_tipler") or [])


def _gorunur(z):
    return [k for k in z.get("kadrajdakiler") or [] if isinstance(k, dict) and k.get("id")
            and k.get("olcek") not in ("el",) and k.get("yuz_acisi") not in ("sirt", "gorunmez")]


def kelime(s): return len(re.findall(r"[A-Za-z0-9À-ɏ']+", s or ""))


def replik_metni(p, a=None):
    """Planın (ya da konuşma adımının) söylediği metin: bölünen replikte yalnız adımın cümleleri."""
    r = p.get("replik") or {}
    cum = r.get("cumleler") or []
    idx = (a or {}).get("cumleler")
    if isinstance(idx, list) and cum:
        return " ".join((cum[i] or {}).get("en", "") for i in idx if isinstance(i, int) and 0 <= i < len(cum)), len(idx)
    metin = r.get("metin") or ""
    n = len(cum) if cum else max(1, len([c for c in re.split(r"(?<=[.!?])\s+", metin.strip()) if c]))
    return metin, n


def diyalog_formulu(kel, cumle, E, agir=False):
    """ZN §2.3: 0,4 + kelime / hız + 0,25 × (cümle − 1) + 0,5."""
    hiz = E.get("konusma_hizi_agir_kelime_sn", 2.0) if agir else E.get("konusma_hizi_kelime_sn", 2.5)
    return round(E.get("diyalog_giris_payi_sn", 0.4) + kel / float(hiz) + E.get("cumle_arasi_sn", 0.25) * max(0, cumle - 1)
                 + E.get("diyalog_cikis_payi_sn", 0.5), 2)


def ciplak_yon(metin):
    """Y47: iyelik ya da 'frame' sözcüğü olmadan geçen left/right."""
    out = []
    for m in CIPLAK_YON.finditer(metin or ""):
        once = metin[max(0, m.start() - 24):m.start()]
        if not YON_ON.search(once): out.append(metin[max(0, m.start() - 12):m.end() + 6].strip())
    return out


# --- plan düzeyi --------------------------------------------------------------------------------------------------
def plan_kurallari(p, E, B=None, filtre=None):
    """Tek planın kuralları (sahneden bağımsız): Y01–Y09, Y29–Y32, Y35–Y37, Y45–Y49, Y56 (konuşmalı Bitir), Z0 #4/#5/#6/#13/#14."""
    z = p.get("zanaat") or {}; no = p.get("no") or z.get("kod"); olc = []; O = olc.append
    fil = po.fiiller(); klip = float(z.get("klip_sn") or 8); ad = _adimlar(z); ins = _ins(z)
    say = [a for a in ad if a.get("tur") in (FIZIKSEL, MIKRO, KONUSMA, SES)]
    kon = [a for a in ad if a.get("tur") == KONUSMA]; fiz = [a for a in ad if a.get("tur") == FIZIKSEL]
    mx, mn = E.get("eylem_adim_max", 3), E.get("plan_adim_min", 2)
    # Y01 / Z0 #13
    if not ins and not (mn <= len(say) <= mx):
        O(po.m("adim_sayisi", "HATA", no, olcu=len(say), esik=[mn, mx], kural="Y01/Z0#13", kok_neden="adim_sayisi",
               neden="8–10 sn klipte 2–3 atomik adım (konuşma da adımdır)"))
    elif ins and len(say) > mx:
        O(po.m("adim_sayisi", "HATA", no, olcu=len(say), esik=mx, kural="Y01/Z0#13", kok_neden="adim_sayisi"))
    # Y02
    if kon and len(fiz) > E.get("eylem_adim_konusmali_max", 1):
        O(po.m("konusmali_fiziksel_fazla", "HATA", no, olcu=len(fiz), esik=E.get("eylem_adim_konusmali_max", 1), kural="Y02/Z0#13",
               kok_neden="konusurken_eylem", neden="konuşmalı planda en çok 1 fiziksel adım (Flow dudakları bozar)"))
    for k in kon:
        for f in fiz:
            if f.get("ozne") == k.get("ozne") and f["bas"] < k["bit"] and k["bas"] < f["bit"]:
                O(po.m("konusma_fiziksel_ortusme", "HATA", no, adim=[f.get("id"), k.get("id")], kural="Y02", kok_neden="konusurken_eylem",
                       neden="konuşma ile fiziksel adım aynı anda olmaz"))
            elif f.get("ozne") == k.get("ozne") and f["bit"] <= k["bas"] and k["bas"] - f["bit"] < E.get("plan_konusma_adim_arasi_min_sn", 0.2):
                O(po.m("konusma_oncesi_bosluk", "BAYRAK", no, adim=[f.get("id"), k.get("id")], olcu=round(k["bas"] - f["bit"], 2),
                       esik=E.get("plan_konusma_adim_arasi_min_sn", 0.2), kural="Y02b"))
    # Y03 / Z0 #14, örtüşme
    for a in say:
        s = _sure(a)
        if s is None: O(po.m("adim_zamani_yok", "HATA", no, adim=a.get("id"), kural="Y03")); continue
        esk = E.get("eylem_adim_min_sn", 1.5) if a.get("tur") == FIZIKSEL else E.get("eylem_adim_mikro_min_sn", 0.8) if a.get("tur") in (MIKRO, SES) else None
        if esk and s + 1e-9 < esk:
            O(po.m("adim_kisa", "HATA", no, adim=a.get("id"), olcu=round(s, 2), esik=esk, kural="Y03/Z0#14", kok_neden="adim_suresi",
                   neden=("fiziksel adım ≥ 1,5 sn" if a.get("tur") == FIZIKSEL else "mikro / ses vuruşu adımı ≥ eylem_adim_mikro_min_sn")))
    for i, a in enumerate(say):
        for b in say[i + 1:]:
            if a.get("ozne") == b.get("ozne") and _sayi(a.get("bit")) and _sayi(b.get("bas")) and b["bas"] < a["bit"] - 1e-9:
                if KONUSMA in (a.get("tur"), b.get("tur")) and FIZIKSEL in (a.get("tur"), b.get("tur")): continue   # Y02'de sayıldı
                O(po.m("adim_ortusmesi", "HATA", no, adim=[a.get("id"), b.get("id")], kural="Y03/Z0#14", kok_neden="adim_suresi",
                       neden="aynı öznenin adımları sıralıdır, örtüşmez"))
    # Y06: aynı anda durum değiştiren adım atan özne ≤ 1
    dd = [a for a in fiz if (fil.get(a.get("fiil")) or {}).get("durum_degistirir")]
    for i, a in enumerate(dd):
        for b in dd[i + 1:]:
            if a.get("ozne") != b.get("ozne") and b["bas"] < a["bit"] and a["bas"] < b["bit"]:
                O(po.m("es_zamanli_ozne", "BAYRAK", no, adim=[a.get("id"), b.get("id")], esik=E.get("plan_es_zamanli_ozne_max", 1), kural="Y06"))
    # Y04 / Y05
    if say:
        if (say[0].get("bas") or 0) + 1e-9 < E.get("plan_ilk_adim_min_sn", 0.5):
            O(po.m("ilk_adim_erken", "BAYRAK", no, olcu=say[0].get("bas"), esik=E.get("plan_ilk_adim_min_sn", 0.5), kural="Y04",
                   neden="Flow klibinin ilk 0,3–1,0 sn'si durağandır"))
        son = max((a.get("bit") or 0) for a in say)
        if son > klip - E.get("plan_son_adim_pay_sn", 1.0) + 1e-9:
            O(po.m("son_adim_gec", "HATA", no, olcu=son, esik=round(klip - E.get("plan_son_adim_pay_sn", 1.0), 2), kural="Y05",
                   kok_neden="bitis_tutmasi", neden="son adım klip_sn − 1,0'da biter; bitiş durumu tutulur"))
    # Y07 / Y08 / Y09
    yasak = [str(x).lower() for x in E.get("yasak_sonuc_fiilleri") or []]
    for a in ad:
        f = fil.get(a.get("fiil"))
        if not f:
            ham = str(a.get("fiil") or "").lower().replace("_", " ")
            tur = "yasak_sonuc_fiili" if ham in yasak else "ic_durum_fiili" if ham in IC_DURUM_EN else "fiil_sozlukte_yok"
            O(po.m(tur, "HATA", no, adim=a.get("id"), olcu=a.get("fiil"), kural="Y07", kok_neden="yasak_fiil",
                   neden="fiil yalnız veri/fiil_sozlugu.json'dan; sonuç ve iç durum fiili yasak (D-13)"))
            continue
        for zr in f.get("zorunlu") or []:
            if not any(a.get(x) not in (None, "", []) for x in zr.split("|")):
                O(po.m("fiil_parametresi_eksik", "HATA", no, adim=a.get("id"), olcu=a.get("fiil"), esik=zr, kural="Y08", kok_neden="eksik_parametre",
                       neden="el, el şekli, hedef, yön ya da ölçü eksik: YZ'ye açık talimat verilmeli"))
        if f.get("ince_el") and (z.get("kamera") or {}).get("kadraj") in GENIS_KADRAJ:
            O(po.m("ince_el_genis_kadraj", "BAYRAK", no, adim=a.get("id"), olcu=(z.get("kamera") or {}).get("kadraj"), kural="Y09",
                   neden="ince el eylemi OG ve daha geniş kadrajda okunmaz: eklemeye böl"))
    # Z0 #4: plan süresi / plan tipi aralığı
    k_ = p.get("kullanim") or {}; sure = k_.get("sure")
    ara = (E.get("plan_sure_aralik_sn") or {}).get(z.get("plan_tipi"))
    if _sayi(sure) and isinstance(ara, list) and len(ara) == 2 and not (ara[0] - 1e-9 <= sure <= ara[1] + 1e-9) and not kon:
        O(po.m("plan_sure_tipe_uymuyor", "HATA", no, olcu=sure, esik=ara, kural="Z0#4", kok_neden="plan_suresi",
               neden=f"'{z.get('plan_tipi')}' planının kullanılan süresi ZN §2.1 aralığında olmalı"))
    # Y37
    if _sayi(k_.get("bas")) and k_["bas"] + 1e-9 < E.get("kullanim_bas_min_sn", 0.3):
        O(po.m("kullanim_bas_erken", "BAYRAK", no, olcu=k_["bas"], esik=E.get("kullanim_bas_min_sn", 0.3), kural="Y37/Z0#41"))
    if _sayi(k_.get("bas")) and _sayi(sure) and k_["bas"] + sure > klip - E.get("kullanim_son_pay_sn", 0.5) + 1e-9:
        O(po.m("kullanim_son_gec", "BAYRAK", no, olcu=round(k_["bas"] + sure, 2), esik=klip - E.get("kullanim_son_pay_sn", 0.5), kural="Y37/Z0#42"))
    # konuşma: Y29–Y32, Z0 #5–#6
    konusan = sorted({a.get("ozne") for a in kon} | {k.get("id") for k in z.get("kadrajdakiler") or [] if isinstance(k, dict) and k.get("konusur")})
    if len(konusan) > E.get("konusan_karede_max", 1):
        O(po.m("konusan_fazla", "HATA", no, olcu=konusan, esik=E.get("konusan_karede_max", 1), kural="Y29/Z0#19", kok_neden="cift_konusan"))
    if (z.get("kamera") or {}).get("kadraj") == "OU":
        for k in z.get("kadrajdakiler") or []:
            if k.get("olcek") == "on_plan_omuz" and (k.get("konusur") or k.get("yuz_acisi") not in ("sirt", "gorunmez", "profil_arka")):
                O(po.m("ou_on_kisi", "HATA", no, kim=k.get("id"), kural="Y29/ZN K4", kok_neden="cift_konusan",
                       neden="omuz üstü planda öndeki kişi sırtı dönük ve sessizdir"))
    tasma = float(((z.get("kesme") or {}).get("ses_tasma_sn")) or 0)
    for a in kon:
        metin, cumle = replik_metni(p, a); kel = kelime(metin)
        sinir = E.get("replik_max_kelime", 20) if klip >= 10 else E.get("replik_max_kelime_8sn", 16)
        if kel > sinir:
            O(po.m("replik_uzun", "HATA", no, adim=a.get("id"), olcu=kel, esik=sinir, kural="Y30/Z0#6", kok_neden="replik_uzun",
                   neden="8 sn klipte ≤ 16, 10 sn klipte ≤ 20 kelime; uzunsa L kesmeyle tepki planına taşı"))
        agir = (p.get("replik") or {}).get("teslim") in ("fisilti", "yasli", "agir")
        konusma_sure = round(kel / float(E.get("konusma_hizi_agir_kelime_sn", 2.0) if agir else E.get("konusma_hizi_kelime_sn", 2.5))
                             + E.get("cumle_arasi_sn", 0.25) * max(0, cumle - 1), 2)
        if (_sure(a) or 0) + 1e-9 < konusma_sure:
            O(po.m("konusma_adimi_kisa", "BAYRAK", no, adim=a.get("id"), olcu=round(_sure(a) or 0, 2), esik=konusma_sure, kural="Y31/ZN§2.3",
                   kok_neden="diyalog_suresi", neden="konuşma adımı kelime / hız + cümle araları kadar sürer"))
        gerek = round(diyalog_formulu(kel, cumle, E, agir) - (tasma if (z.get("kesme") or {}).get("tip") == "L" else 0), 2)
        if _sayi(sure) and sure + 1e-9 < gerek:
            O(po.m("diyalog_suresi_yetmiyor", "HATA", no, olcu=sure, esik=gerek, kural="Y31/Z0#5", kok_neden="diyalog_suresi",
                   neden="sure_sn ≥ ZN §2.3 formülü − L taşması"))
        kd = next((k for k in z.get("kadrajdakiler") or [] if k.get("id") == a.get("ozne")), None)
        kad = (z.get("kamera") or {}).get("kadraj")
        if kd and (kad not in KONUSAN_KADRAJ or kd.get("yuz_acisi") not in ("on", "3/4")):
            O(po.m("konusan_yuz_zayif", "BAYRAK", no, kim=a.get("ozne"), olcu={"kadraj": kad, "yuz_acisi": kd.get("yuz_acisi")},
                   esik={"kadraj": list(KONUSAN_KADRAJ), "yuz_acisi": ["on", "3/4"]}, kural="Y32",
                   neden="konuşan yüz O/OY/Y ve önden ya da 3/4 (|yaw| ≤ 45°); CY'de konuşulmaz"))
        if kon and (z.get("zincir") or {}).get("bitis_sabitle"):
            O(po.m("konusmali_bitis_sabitle", "HATA", no, kural="Y56", kok_neden="zincir",
                   neden="konuşmalı planda Bitir (bitis_sabitle) yok (ölçülene kadar)"))
            break
    # Y35: ekran dışı ses → görünen herkes dinler, ağzı kapalı
    eds = z.get("ekran_disi_ses")
    if eds:
        if kon: O(po.m("ekran_disi_seste_konusan", "HATA", no, kural="Y35", kok_neden="cift_konusan"))
        dl = p.get("_derlenir") or {}
        if dl and dl.get("dinleyen_agiz") not in ("kapali",):
            O(po.m("dinleyen_agiz_acik", "HATA", no, olcu=dl.get("dinleyen_agiz"), esik="kapali", kural="Y35",
                   neden="ekran dışı ses varken görünen herkes 'listens silently, mouth closed'"))
    # Y36
    ks = z.get("kesme") or {}
    if ks.get("tip") == "L" and tasma:
        a_ = E.get("l_kesme_aralik_sn") or [0.3, 2.5]
        if not a_[0] <= tasma <= a_[1]: O(po.m("l_tasma_araligi", "BAYRAK", no, olcu=tasma, esik=a_, kural="Y36"))
    if ks.get("tip") == "J" and tasma:
        a_ = E.get("j_kesme_aralik_sn") or [0.3, 0.8]
        if not a_[0] <= tasma <= a_[1]: O(po.m("j_tasma_araligi", "BAYRAK", no, olcu=tasma, esik=a_, kural="Y36"))
    # Y45
    ref = (p.get("_derlenir") or {}).get("referans") or p.get("referans") or [k.get("id") for k in _gorunur(z)]
    if len(ref) > E.get("referans_max", 2):
        O(po.m("referans_fazla", "HATA", no, olcu=len(ref), esik=E.get("referans_max", 2), kural="Y45/Z0#19", kok_neden="referans"))
    # Y27: kamera hareketi
    ht = (z.get("kamera") or {}).get("hareket_tipi")
    if isinstance(ht, list) and len([h for h in ht if h != "sabit"]) > E.get("kamera_hareketi_klip_max", 1):
        O(po.m("kamera_hareketi_fazla", "HATA", no, olcu=ht, esik=E.get("kamera_hareketi_klip_max", 1), kural="Y27"))
    for h in (ht if isinstance(ht, list) else [ht]):
        if h in (E.get("dusuk_guven_hareketler") or []) and not (z.get("vurus") == "doruk" or p.get("hareket_istem_yedek")):
            O(po.m("dusuk_guvenli_hareket", "BAYRAK", no, olcu=h, kural="Y27", neden="yalnız doruk + yedek istemle"))
    # Y49
    eb = (z.get("ekranda_bilgi") or "").strip()
    if not eb: O(po.m("ekranda_bilgi_bos", "HATA", no, kural="Y49", kok_neden="ekranda_bilgi", neden="seyircinin ekranda gördüğü bilgi yazılmalı"))
    elif any(f in eb.lower() for f in IC_DURUM_TR):
        O(po.m("ekranda_bilgi_ic_durum", "BAYRAK", no, olcu=eb[:80], kural="Y49", neden="ekranda görünmeyen iç durum yazılmış"))
    # Y46–Y48: derlenmiş istem (varsa; yoksa plan dili ile derlenir)
    ist = p.get("hareket_istem") or ""
    if not ist and B is not None:
        try:
            import plan_dili
            ist = plan_dili.gorunur_tarif(p, "en", B)
        except Exception as e:
            O(po.m("istem_derlenemedi", "OLCULEMEDI", no, neden=f"{e.__class__.__name__}: {str(e)[:120]}"))
    ie = z.get("istem_elle")                                   # {metin, neden} (şema: nesne); eski dizge de okunur
    elle = ie if isinstance(ie, str) else (ie or {}).get("metin") or "" if isinstance(ie, dict) else ""
    if isinstance(ie, dict) and not ie.get("neden"):
        O(po.m("elle_istem_gerekcesiz", "HATA", no, kural="§5.1 kural 3", neden="istem_elle yalnız gerekçeyle (neden) yazılır"))
    for metin, kaynak in ((ist, "hareket_istem"), (elle, "istem_elle")):
        if not metin: continue
        if kaynak == "hareket_istem" and kelime(metin) > E.get("plan_hareket_istem_kelime_max", 75):
            O(po.m("istem_uzun", "BAYRAK", no, olcu=kelime(metin), esik=E.get("plan_hareket_istem_kelime_max", 75), kural="Y46"))
        cy = ciplak_yon(metin)
        if cy: O(po.m("ciplak_sol_sag", "HATA", no, olcu=cy[:3], kural="Y47", kok_neden="yon", neden="sağ/sol daima iyelikli ya da 'frame'"))
        for y in (yasak + list(IC_DURUM_EN)):
            if re.search(r"\b" + re.escape(y) + r"\b", metin.lower()):
                O(po.m("istemde_yasak_fiil", "HATA", no, olcu=y, kaynak=kaynak, kural="Y07/Z0#15", kok_neden="yasak_fiil")); break
        if filtre:
            bul = filtre(metin)
            if bul: O(po.m("istemde_filtre_kelimesi", "HATA", no, olcu=bul[:3], kaynak=kaynak, kural="Y48/Z0#20", kok_neden="filtre"))
    if B is not None and ist:
        try:
            import plan_dili
            for a in ad:
                if a.get("tur") == KONUSMA: continue          # replik metni Y30'da sayılır
                c, n = plan_dili.adim_cumlesi(a, p, B, "en")
                if n > E.get("plan_adim_cumle_kelime_max", 16):
                    O(po.m("adim_cumlesi_uzun", "BAYRAK", no, adim=a.get("id"), olcu=n, esik=E.get("plan_adim_cumle_kelime_max", 16), kural="Y46"))
        except Exception: pass
    return olc


# --- ardışık planlar ve sahne -------------------------------------------------------------------------------------
def gecis_kurallari(a, b, E):
    """A → B geçişi: Y33, Y34, Y40 (zincir derinliği ayrıca), Y54, Y55, Y56 öneri."""
    olc = []; O = olc.append
    za, zb = a.get("zanaat") or {}, b.get("zanaat") or {}; na, nb = a.get("no") or za.get("kod"), b.get("no") or zb.get("kod")
    ks = za.get("kesme") or {}
    kon_b = [x for x in _adimlar(zb) if x.get("tur") == KONUSMA]
    kb_bas = float((b.get("kullanim") or {}).get("bas") or 0)
    tas = float(ks.get("ses_tasma_sn") or 0)
    if ks.get("tip") == "L" and tas > 0 and any((x.get("bas") or 0) - kb_bas < tas - 1e-9 for x in kon_b):
        O(po.m("l_tasmasi_konusana", "HATA", nb, onceki=na, kural="Y33", kok_neden="cift_konusan",
               neden="L taşması, konuşanın da görünüp konuştuğu plana gidiyor (çift ses)"))
    if ks.get("tip") == "J" and kon_b:
        gor_a = {k.get("id") for k in _gorunur(za)}
        for x in kon_b:
            if x.get("ozne") in gor_a:
                O(po.m("j_konusan_onceki_planda", "HATA", na, sonraki=nb, kim=x.get("ozne"), kural="Y34", kok_neden="cift_konusan",
                       neden="J kesmesinde sonraki planın konuşanı bu planda görünüyor ve ağzı kapalı"))
    zn = zb.get("zincir") or {}
    if zn.get("gecis_turu") == "devam":
        if not zn.get("dogal_durak"):
            O(po.m("ortusuz_devam", "BAYRAK", nb, onceki=na, kural="Y54",
                   neden="bitişik devam yalnız dogal_durak: true ise; değilse araya ≥ 1,0 sn örtü planı"))
        son = max([x.get("bit") or 0 for x in _adimlar(za) if x.get("tur") in (FIZIKSEL, MIKRO, KONUSMA, SES)] or [0])
        k_ = a.get("kullanim") or {}; kn = ((a.get("_derlenir") or {}).get("kesme_nokta_sn")
                                            or ((k_.get("bas") or 0) + (k_.get("sure") or 0)))
        klip = float(za.get("klip_sn") or 8)
        alt, ust = son + E.get("devam_kesme_tutma_min_sn", 0.2), klip - E.get("kullanim_son_pay_sn", 0.5)
        if not (alt - 1e-9 <= kn <= ust + 1e-9):
            O(po.m("zincir_kesme_penceresi", "HATA", na, sonraki=nb, olcu=kn, esik=[round(alt, 2), round(ust, 2)], kural="Y55/D-15",
                   kok_neden="zincir", neden="zincir kaynağında kesme noktası bitiş tutmasının içinde (son adım + 0,2 ≤ kesme ≤ klip − 0,5)"))
        fil = po.fiiller()
        dd = [x for x in _adimlar(za) if x.get("tur") == FIZIKSEL and (fil.get(x.get("fiil")) or {}).get("durum_degistirir")]
        kon_a = [x for x in _adimlar(za) if x.get("tur") == KONUSMA]
        if dd and not kon_a and not (za.get("zincir") or {}).get("bitis_sabitle"):
            O(po.m("bitis_sabitle_oneri", "BAYRAK", na, sonraki=nb, kural="Y56/D-15",
                   neden="sonraki plan devam ve bu planda durum değiştiren adım var: Bitir (bitis_sabitle) önerilir"))
    return olc


def sahne_kurallari(sid, planlar, sg, E):
    """Sahne içi: Y20, Y21, Y22, Y40, Y44 (ilk görünüş sahne bazında değil film bazında: film_kurallari), Y50–Y53, Z0 #8–#11."""
    olc = []; O = olc.append
    if not planlar: return [po.m("sahne_plansiz", "HATA", None, sahne=sid)]
    for a, b in zip(planlar, planlar[1:]): olc += gecis_kurallari(a, b, E)
    ilk = planlar[0].get("no")
    # Y20, Z0 #11, monolog
    kur = [((p.get("zanaat") or {}).get("kamera") or {}).get("kurulum") for p in planlar]
    tip = [(p.get("zanaat") or {}).get("plan_tipi") for p in planlar]
    def ardisik(dizi, mx, madde, kural, haric=()):
        n = 1
        for i in range(1, len(dizi)):
            n = n + 1 if dizi[i] and dizi[i] == dizi[i - 1] and dizi[i] not in haric else 1
            if n == mx + 1: O(po.m(madde, "BAYRAK", planlar[i].get("no"), sahne=sid, olcu=dizi[i], esik=mx, kural=kural))
    ardisik(kur, E.get("ayni_kamera_konumu_ardisik_max", 2), "ayni_kurulum_ardisik", "Y20")
    ardisik(tip, E.get("ayni_plan_tipi_ardisik_max", 4), "ayni_plan_tipi_ardisik", "Z0#11")
    kim = []
    for p in planlar:
        k = [x.get("ozne") for x in _adimlar(p.get("zanaat") or {}) if x.get("tur") == KONUSMA]
        kim.append(k[0] if k else None)
    ardisik(kim, E.get("monolog_ardisik_plan_max", 3), "monolog_ardisik", "Z0/monolog")
    # Y21 / Y22: konum planı
    kp = set(po.sozluk("plan").get("konum_plani") or ["G", "OG", "IK", "EG"])
    kad = [((p.get("zanaat") or {}).get("kamera") or {}).get("kadraj") for p in planlar]
    n_ilk = E.get("sahne_konum_plani_max_sira", 3) + (2 if (sg.get("gec_giris")) else 0)
    if not any(k in kp for k in kad[:n_ilk]):
        O(po.m("konum_plani_gec", "BAYRAK", ilk, sahne=sid, olcu=kad[:n_ilk], esik=n_ilk, kural="Y21",
               neden="sahnenin ilk planlarında seyirciyi mekâna yerleştiren G/OG/IK planı yok"))
    sure = [float((p.get("kullanim") or {}).get("sure") or 0) for p in planlar]; top = sum(sure)
    if top > E.get("sahne_yeniden_konum_sn", 90):
        t, orta = 0.0, False
        for s, k in zip(sure, kad):
            if top * 0.3 <= t <= top * 0.7 and k in kp: orta = True
            t += s
        if not orta: O(po.m("yeniden_konum_yok", "BAYRAK", ilk, sahne=sid, olcu=round(top, 1), kural="Y22"))
    # Z0 #8
    if top > E.get("sahne_max_sn", 180):
        O(po.m("sahne_uzun", "HATA", ilk, sahne=sid, olcu=round(top, 1), esik=E.get("sahne_max_sn", 180), kural="Z0#8", kok_neden="sahne_suresi"))
    # Y40: zincir derinliği
    d = 0
    for p in planlar:
        d = d + 1 if ((p.get("zanaat") or {}).get("zincir") or {}).get("gecis_turu") == "devam" else 0
        if d > E.get("zincir_derinlik_max", 2):
            O(po.m("zincir_derin", "HATA", p.get("no"), sahne=sid, olcu=d, esik=E.get("zincir_derinlik_max", 2), kural="Y40/D-15",
                   kok_neden="zincir", neden="2 halkadan sonra yeniden demirleme (ana kare/türev)"))
    # Y50–Y52: diyalog sahnesi kapsaması
    if sg.get("sahne_tipi") == "diyalog":
        kurulumlar = {k for k in kur if k}
        if len(kurulumlar) < E.get("plan_dialog_kurulum_min", 3):
            O(po.m("diyalog_kurulum_az", "BAYRAK", ilk, sahne=sid, olcu=len(kurulumlar), esik=E.get("plan_dialog_kurulum_min", 3), kural="Y50"))
        T = len(planlar); R = sum(1 for t in tip if t == "tepki")
        if R < math.ceil(E.get("tepki_orani_min", 0.25) * T - 1e-9):
            O(po.m("tepki_plani_az", "BAYRAK", ilk, sahne=sid, olcu=R, esik=math.ceil(E.get("tepki_orani_min", 0.25) * T), kural="Y51/Z0#9"))
        jl = sum(1 for p in planlar if ((p.get("zanaat") or {}).get("kesme") or {}).get("tip") in ("L", "J"))
        if T > 1 and jl / float(T - 1) + 1e-9 < E.get("jl_kesme_orani_min", 0.3):
            O(po.m("jl_orani_dusuk", "BAYRAK", ilk, sahne=sid, olcu=round(jl / float(T - 1), 2), esik=E.get("jl_kesme_orani_min", 0.3), kural="Y52/Z0#10"))
    # Y53
    ph = sg.get("plan_hedef")
    if isinstance(ph, int) and ph > 0 and abs(len(planlar) - ph) > max(1, round(ph * E.get("plan_sayisi_tolerans_oran", 0.15))):
        O(po.m("plan_sayisi_sapmasi", "BAYRAK", ilk, sahne=sid, olcu=len(planlar), esik=ph, kural="Y53"))
    # sahne tipi süre aralığı (yalnız bilgi; kısa örnek filmlerde de anlamlı)
    st = (E.get("sahne_tipi_aralik") or {}).get(sg.get("sahne_tipi")) or {}
    if isinstance(st.get("sure"), list) and sg.get("sure_hedef_sn") and not (st["sure"][0] <= top <= st["sure"][1]):
        hed = float(sg["sure_hedef_sn"])
        if abs(top - hed) > hed * 0.15:
            O(po.m("sahne_suresi_hedeften_sapti", "BAYRAK", ilk, sahne=sid, olcu=round(top, 1), esik=hed, kural="ZN§2.4"))
    return olc


def replik_butunlugu(s):
    """Y59: bölünen replikte cümleler planlar arasında eksiksiz ve tekrarsız."""
    olc, kul = [], {}
    for p in s.get("sahneler") or []:
        for a in _adimlar(p.get("zanaat") or {}):
            if a.get("tur") != KONUSMA or not a.get("replik"): continue
            r = p.get("replik") or {}; n = len(r.get("cumleler") or []) or 1
            idx = a.get("cumleler") if isinstance(a.get("cumleler"), list) else list(range(n))
            kul.setdefault(a["replik"], {"n": n, "idx": [], "plan": []})
            kul[a["replik"]]["idx"] += idx; kul[a["replik"]]["plan"].append(p.get("no"))
    for rid, v in kul.items():
        if sorted(v["idx"]) != list(range(v["n"])):
            olc.append(po.m("replik_bolunmesi_bozuk", "HATA", v["plan"][0], olcu=rid, esik=v["n"], kural="Y59", kok_neden="replik",
                            neden="bölünen replikte cümleler eksiksiz ve tekrarsız dağıtılmalı", planlar=v["plan"]))
    return olc


def film_kurallari(s, E):
    """Film düzeyi: Y42 (Bitir özel görsel oranı), plan_istem_elle_oran_max, Y44 (karakterin ilk görünüşü), Y59."""
    olc = []; O = olc.append; P = sorted(s.get("sahneler") or [], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0))
    if not P: return olc
    nn = {i: p for i, p in enumerate(P)}
    ozel = 0
    for i, p in nn.items():
        zn = (p.get("zanaat") or {}).get("zincir") or {}
        if zn.get("bitis_sabitle"):
            sonraki = nn.get(i + 1)
            if not (sonraki and ((sonraki.get("zanaat") or {}).get("zincir") or {}).get("gecis_turu") == "devam"): ozel += 1
    if ozel / float(len(P)) > E.get("plan_bitis_ozel_oran_max", 0.10) + 1e-9:
        O(po.m("bitis_ozel_gorsel_orani", "BAYRAK", None, olcu=round(ozel / float(len(P)), 3), esik=E.get("plan_bitis_ozel_oran_max", 0.10), kural="Y42"))
    elle = sum(1 for p in P if (p.get("zanaat") or {}).get("istem_elle"))
    if elle / float(len(P)) > E.get("plan_istem_elle_oran_max", 0.05) + 1e-9:
        O(po.m("elle_istem_orani", "BAYRAK", None, olcu=round(elle / float(len(P)), 3), esik=E.get("plan_istem_elle_oran_max", 0.05), kural="§5.1 kural 3"))
    goruldu = set()
    for p in P:
        z = p.get("zanaat") or {}
        for k in _gorunur(z):
            if k["id"] in goruldu: continue
            goruldu.add(k["id"])
            kd = _kad_kademe(k.get("olcek")) or _kad_kademe((z.get("kamera") or {}).get("kadraj")) or 0
            if kd < (_kad_kademe("OY") or 5) or k.get("yuz_acisi") not in ("on", "3/4"):
                O(po.m("ilk_gorunus_kimlik_zayif", "BAYRAK", p.get("no"), kim=k["id"], olcu={"olcek": k.get("olcek"), "yuz": k.get("yuz_acisi")},
                       kural="Y44", neden="karakterin ilk görünüşü OY ya da daha yakın, yüz önden ya da 3/4 (kimlik demiri)"))
    olc += replik_butunlugu(s)
    return olc


# --- harita (A07a) ------------------------------------------------------------------------------------------------
def harita_denetle(kok, E):
    import plan_sema, kroki
    h = ortak.json_oku(os.path.join(kok, "HIKAYE.json"), {}) or {}
    hs = {x.get("id"): x for x in h.get("sahneler") or [] if isinstance(x, dict)}
    olc, birim, gor = [], [], {}
    yollar = sorted(glob.glob(os.path.join(kok, "_YONETMEN", "HARITA_P*.json")))
    if not yollar: return [po.m("harita_yok", "HATA", None, neden="_YONETMEN/HARITA_P<n>.json yok")], []
    mek = {}
    for y in yollar:
        v = ortak.json_oku(y); ad = os.path.basename(y)
        if not isinstance(v, dict): olc.append(po.m("json_bozuk", "HATA", None, dosya=ad)); continue
        olc += [o for o in plan_sema.denetle(v, "harita", kok, ad) if o["seviye"] != "GEC"]
        mek.update(v.get("mekanlar") or {})
        for sid, sg in (v.get("sahne_gruplari") or {}).items():
            birim.append(sid); gor[sid] = ad
            hk = hs.get(sid)
            if not hk: olc.append(po.m("harita_sahnesi_hikayede_yok", "HATA", sid, sahne=sid, dosya=ad)); continue
            if hk.get("mekan") and sg.get("mekan") != hk["mekan"]:
                olc.append(po.m("mekan_hikayeye_uymuyor", "HATA", sid, sahne=sid, olcu=sg.get("mekan"), esik=hk["mekan"]))
            mv = (v.get("mekanlar") or {}).get(sg.get("mekan")) or {}
            for k in sg.get("kurulumlar") or []:
                if k not in (mv.get("kurulumlar") or {}):
                    olc.append(po.m("kurulum_tanimsiz", "HATA", sid, sahne=sid, olcu=k, neden="sahnenin kurulumu mekânın kurulumlar'ında yok"))
            eks = sg.get("eksen") or []
            if eks and (len(eks) != 2 or not sg.get("kamera_tarafi")):
                olc.append(po.m("eksen_eksik", "HATA", sid, sahne=sid, olcu=eks, kural="Y17", neden="eksen iki kişi + kamera_tarafi (pusula)"))
            if sg.get("sahne_tipi") == "diyalog" and not eks:
                olc.append(po.m("diyalogda_eksen_yok", "HATA", sid, sahne=sid, kural="Y17/Y18"))
            if sg.get("sahne_tipi") == "diyalog" and len(sg.get("kurulumlar") or []) < E.get("plan_dialog_kurulum_min", 3):
                olc.append(po.m("diyalog_kurulum_az", "BAYRAK", sid, sahne=sid, olcu=len(sg.get("kurulumlar") or []), esik=E.get("plan_dialog_kurulum_min", 3), kural="Y50"))
            if (sg.get("sure_hedef_sn") or 0) > E.get("sahne_max_sn", 180):
                olc.append(po.m("sahne_uzun", "HATA", sid, sahne=sid, olcu=sg.get("sure_hedef_sn"), esik=E.get("sahne_max_sn", 180), kural="Z0#8"))
            hed = hk.get("hedef_sure_sn")
            if hed and sg.get("sure_hedef_sn") and abs(sg["sure_hedef_sn"] - hed) > hed * E.get("plan_sayisi_tolerans_oran", 0.15) + 1:
                olc.append(po.m("sure_hedefi_hikayeden_sapti", "BAYRAK", sid, sahne=sid, olcu=sg["sure_hedef_sn"], esik=hed))
            if not isinstance(sg.get("isik"), dict) or not sg["isik"].get("ana"):
                olc.append(po.m("isik_ana_yok", "HATA", sid, sahne=sid, kural="Y23", neden="ana ışık kaynağı olmadan ışık yönü hesaplanamaz"))
            for uc in ("giris_durumu", "cikis_durumu"):
                if not isinstance(sg.get(uc), dict): olc.append(po.m("sozlesme_ucu_yok", "HATA", sid, sahne=sid, uc=uc))
    for sid in hs:
        if sid not in gor: olc.append(po.m("hikaye_sahnesi_haritada_yok", "HATA", sid, sahne=sid))
    K = kroki.Kroki(kok, {"mekanlar": mek})
    olc += kroki.kroki_denetle(K)
    for sid in birim: pass
    return olc, birim


# --- yükleme ve denetim -------------------------------------------------------------------------------------------
def _filtre():
    try:
        import istem_derle
        return lambda t: istem_derle.yasak_bul(t)
    except Exception: return None


def _baglam(kok, s):
    try:
        import plan_dili
        return plan_dili.baglam(kok, s)
    except Exception: return None


def denetle(kok, sahne=None, tum=False, ek_dosya=None, kaynak="plan"):
    """(ölçümler, birimler, sahneler). kaynak: plan (PLANLAR + HARITA, A07b) | sahneler (SAHNELER.json, A07c)."""
    import plan_birlestir, plan_sema, kroki, dunya_defteri
    E = po.esik(); olc = []
    if kaynak == "sahneler":
        s = ortak.json_oku(os.path.join(kok, "SAHNELER.json"))
        if not isinstance(s, dict) or int(s.get("_surum", 1) or 1) < 2:
            return [po.m("sahneler_yok", "HATA", None, neden="v2 SAHNELER.json yok (önce plan_birlestir)")], [], None
    else:
        s, o = plan_birlestir.topla(kok)
        olc += [x for x in o if x["seviye"] == "HATA"]
        if s is None: return olc, [], None
        s.pop("_no_esleme", None)
        for y, d in plan_birlestir.plan_dosyalari(kok):
            sid = d.get("sahne_grubu")
            if sahne and sid != sahne: continue
            olc += [x for x in plan_sema.denetle(d, "sahne_plan_dosyasi", kok, os.path.basename(y)) if x["seviye"] != "GEC"]
    B = _baglam(kok, s); fl = _filtre()
    P = sorted(s.get("sahneler") or [], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0))
    gruplar = s.get("sahne_gruplari") or {}
    secili = [p for p in P if not sahne or (p.get("zanaat") or {}).get("sahne_grubu") == sahne]
    if sahne and not secili: return [po.m("sahne_plani_yok", "HATA", None, sahne=sahne)], [], s
    for p in secili:
        for x in plan_kurallari(p, E, B, fl): x.setdefault("sahne", (p.get("zanaat") or {}).get("sahne_grubu")); olc.append(x)
    for sid, sg in gruplar.items():
        if sahne and sid != sahne: continue
        sp = [p for p in P if (p.get("zanaat") or {}).get("sahne_grubu") == sid]
        if sp: olc += sahne_kurallari(sid, sp, sg, E)
    if tum and not sahne: olc += film_kurallari(s, E)
    elif sahne: olc += [x for x in replik_butunlugu(s) if x.get("plan") in {p.get("no") for p in secili}]
    # geometri (kroki) ve durum zinciri (dünya defteri)
    try:
        g, _ = kroki.denetle_film(kok, sahne) if kaynak == "plan" else _kroki_sahneler(kok, s, sahne)
        olc += [dict(x, kaynak_arac="kroki") for x in g]
    except Exception as e:
        olc.append(po.m("geometri_hesaplanamadi", "HATA", None, neden=f"{e.__class__.__name__}: {str(e)[:160]}"))
    try:
        C = dunya_defteri.coz(s, ortak.json_oku(os.path.join(kok, "HIKAYE.json")))
        nos = {p.get("no") for p in secili}
        olc += [dict(x, kaynak_arac="dunya_defteri") for x in C.olcumler if not sahne or x.get("plan") in nos or x.get("sahne") == sahne]
    except Exception as e:
        olc.append(po.m("durum_zinciri_cozulemedi", "HATA", None, neden=f"{e.__class__.__name__}: {str(e)[:160]}"))
    return olc, [p.get("no") for p in secili], s


def _kroki_sahneler(kok, s, sahne):
    import kroki, dunya_defteri
    E = po.esik(); K = kroki.Kroki(kok, s); C = dunya_defteri.coz(s, ortak.json_oku(os.path.join(kok, "HIKAYE.json")))
    P = sorted(s.get("sahneler") or [], key=lambda p: float(p.get("sira", p.get("no", 0)) or 0)); olc = []
    for sid, sg in (s.get("sahne_gruplari") or {}).items():
        if sahne and sid != sahne: continue
        sg = dict(sg, _id=sid); sp = [p for p in P if (p.get("zanaat") or {}).get("sahne_grubu") == sid]
        for p in sp:
            d = C.planlar.get(str(p.get("no"))) or {"bas": {}, "bit": {}}
            _, o = kroki.derle(p, d["bas"], d["bit"], K, sg, E, s.get("karakterler")); olc += o
        olc += kroki.sahne_denetle(sid, sp, C.planlar, K, sg, E)
        olc += kroki.plaka_denetle(K, sg.get("mekan"), sg)[0]
    return olc, []


def _tekille(olc):
    gor, out = set(), []
    for o in olc:
        k = (o.get("madde"), str(o.get("plan")), str(o.get("adim")), str(o.get("yol")), str(o.get("kim")), str(o.get("sahne")))
        if k in gor: continue
        gor.add(k); out.append(o)
    return out


def _parti_of(s):
    return {p.get("no"): int(p.get("parti") or 1) for p in s.get("sahneler") or []}


def main(argv):
    if not argv or "-h" in argv or "--help" in argv: print(__doc__); return 4
    kok = po.film_kok(po.arg_al(argv, "--film")); tur = po.tur_no(argv); E = po.esik()
    if "--harita" in argv:
        olc, birim = harita_denetle(kok, E)
        yol, r = po.rapor_yaz(kok, "HARITA", "FILM", _tekille(olc), asama="A07a", arac=SURUM, birimler=birim, tur=tur,
                              varsayilan=os.path.join("_RAPOR", f"HARITA_t{tur}.json"))
        po.yaz_ozet(r, "harita"); return po.cikis(r)
    if "--dosya" in argv:
        y = po.arg_al(argv, "--dosya"); v = ortak.json_oku(y)
        if not isinstance(v, dict): print(f"!! dosya yok ya da JSON bozuk: {y}", flush=True); return 2
        import plan_sema
        olc = [o for o in plan_sema.denetle(v, "sahne_plan_dosyasi", kok, os.path.basename(y)) if o["seviye"] != "GEC"]
        for p in v.get("planlar") or []: olc += plan_kurallari(p, E, None, _filtre())
        sid = v.get("sahne_grubu")
        if sid: olc += sahne_kurallari(sid, v.get("planlar") or [], {}, E)
        for o in olc: print(f"{o['seviye']} {o['madde']} {o.get('plan', '')} {o.get('neden', '')}", flush=True)
        n = sum(o["seviye"] == "HATA" for o in olc); print(f"plan denetimi: HATA {n}", flush=True)
        return 1 if n else 0
    sahne = po.arg_al(argv, "--sahne"); tum = "--tum" in argv
    if "--sahne" in argv:
        if not glob.glob(os.path.join(kok, "_YONETMEN", "PLANLAR", "*.json")): print("!! _YONETMEN/PLANLAR boş", flush=True); return 2
        olc, birim, _ = denetle(kok, sahne=sahne, tum=False)
        kapsam = f"SAHNE_{sahne}" if sahne else "SAHNE"
        var = os.path.join("_RAPOR", f"Z0_SAHNE_{sahne}.json" if sahne else f"Z0_SAHNE_t{tur}.json")
        yol, r = po.rapor_yaz(kok, "Z0", kapsam, _tekille(olc), asama="A07b", arac=SURUM, birimler=birim, tur=tur, varsayilan=var)
        po.yaz_ozet(r, "Z0 sahne"); return po.cikis(r)
    if tum:
        if not os.path.isfile(os.path.join(kok, "SAHNELER.json")): print("!! SAHNELER.json yok (önce plan_birlestir)", flush=True); return 2
        olc, birim, s = denetle(kok, tum=True, kaynak="sahneler"); olc = _tekille(olc)
        if s is None:
            po.rapor_yaz(kok, "Z0", "FILM", olc, asama="A07c", arac=SURUM, tur=tur); return 1
        pa = _parti_of(s); kotu = 0
        for n in sorted(set(pa.values())):
            pn = [b for b in birim if pa.get(b) == n]
            po_ = [o for o in olc if pa.get(o.get("plan")) == n]
            _, r = po.rapor_yaz(kok, "Z0", f"P{n}", po_, asama="A07c", arac=SURUM, birimler=pn, tur=tur,
                                varsayilan=os.path.join("_RAPOR", f"Z0_P{n}.json"))
            po.yaz_ozet(r, f"Z0 P{n}"); kotu = max(kotu, po.cikis(r))
        film_o = [o for o in olc if o.get("plan") not in pa]
        _, rf = po.rapor_yaz(kok, "Z0", "FILM", olc, asama="A07c", arac=SURUM, birimler=birim, tur=tur,
                             ek={"film_duzeyi": len(film_o)})
        import dunya_defteri
        dunya_defteri.yeniden_yaz_kuyrugu(kok, [o for o in olc if o.get("kaynak_arac") != "dunya_defteri"], kapi="Z0", asama="A07c")
        return max(kotu, po.cikis(rf))
    print(__doc__); return 4


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
