"""ÖLÇEK — filmin ölçek ve takvim sayılarının TEK kaynağı (TASARIM §1.6, D-04, D-05, D-08, §8.1).

Belgelerdeki plan, klip, kredi, gönderim, gün ve görev sayılarının yerine bu aracın çıktısı kullanılır. Sayılar süreden, eşik
dosyalarından (esikler.py: ritim_esikleri.json + hat_esikleri.json, FILM_AYAR yalnız sıkılaştırır) ve ölçümlerden (OLCUM0) türetilir;
elle yazılmış film sayısı yoktur. Ölçülmemiş her değer açıkça "ölçülmedi" yazılır ve ihtiyatlı varsayımla hesaplanır.

Kullanım:
  python olcek.py                              30 / 40 / 45 dk karşılaştırması (metin)
  python olcek.py --dk 40                      tek süre, ayrıntılı döküm   (--sure 2400 aynı şey, saniyeyle)
  python olcek.py --dk 30 --dk 40 --json       JSON (birden çok süre → liste)
  python olcek.py --dk 30 --md                 kullanıcı sözleşmesi kartı (§8.1; BASLA_BURADAN.txt'nin başı)
  python olcek.py --film <film_klasoru>        plan ve klip sayısını o filmin SAHNELER.json'undan alır (süre: BUT0 raporu ya da --dk)
  Ek: --olcum <OLCUM0.json | O0b.json> --ayar <FILM_AYAR.json>   (verilmezse <veri>/BILGI/OLCUM0/OLCUM0.json ve <veri>/AYARLAR/FILM_AYAR.json
       aranır; yoksa yok sayılır)
  Kodda: import olcek; o = olcek.hesapla(2400, E=None, olcum=None, ayar=None, plan=None, klip=None)
         olcek.metin(o) · olcek.kart_md(o) · olcek.sahne_say(sahneler_sozlugu) · olcek.kapasite(E, olcum)

Formüller (her biri JSON'da "formul" alanıyla da yazılır):
  plan        = round(Σ RE hedef_plan_dagilimi_40dk × süre / 2400)          aralık ± RE plan_sayisi_tolerans_oran
  klip        = ceil(plan × (1 − RE klip_bolme_oran_hedef))                  (başka planın klibinden çıkan planlar klip istemez)
  taban kredi = klip × RE kredi_klip_720p (720p 8 sn)
  kapı payı   = ceil(taban × kapi_payi) → dilimler görüntü/ses/kurgu (D-31; oran payı kapi_payi'ye ölçeklenir)
  take payı   = take_payi_kredi (D-23)
  BUT tahmini = taban + kapı payı + take payı;   gereken bakiye = ceil(BUT tahmini / (1 − guvenlik_payi))
  video gönd. = klip + ceil(kapı payı / kredi_klip) + take_payi_kredi / kredi_klip
  video_gun   = ceil(video gönderim / olculen_gunluk_kapasite)   (D-04; ölçülmediyse Ö0-b merdiveninin ilk basamağı varsayılır)
  gorsel_gun  = ceil(görsel düzeltme / flow_gorsel_gunluk_tavan) (görsel günü video günü olamaz: sıra kuralı 7)
OLCUM0 alanları (hepsi isteğe bağlı): O0b {olculen_gunluk_kapasite, olculemedi, uretim_sn_720p} · O0e {gemini_api_paket}
  · O0f {gorev_basi_token} · sureler_gun {kagit, yerel_hazirlik, animatik, kurgu_ses_yayin: [en az, en çok]}. Düz (O0b.json) biçim de okunur.
Çıkış kodları: 0 BİTTİ · 1 HATA (eşik dosyası ya da girdi bozuk, kullanım yanlış).
"""
import os, sys, json, math, hashlib, datetime
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, esikler

SURUM = "olcek 1.0"
REF_SN = 2400                   # RE'deki *_40dk anahtarlarının ölçeği
SURE_ARALIK_VARSAYILAN = [1800, 2700]
# Belgedeki tahminler (hepsi "tahmin"; ölçüm geldikçe OLCUM0'dan güncellenir). Eşik dosyasında karşılığı olan sayı burada YOKTUR.
YENIDEN_PAY_DILIM = {"goruntu": 0.15, "ses": 0.07, "kurgu": 0.08}          # TASARIM D-31, §7.2 (tahmin); hat_esikleri'nde yoksa
GORSEL_DUZELTME_PLAN_ORAN = [116 / 495, 240 / 495]                          # TASARIM §1.6 40 dk 116–240 ([UM2]/[GS2]; tahmin)
SURELER_GUN = {"kagit": [3, 6], "yerel_hazirlik": [1, 2], "animatik": [2, 4], "kurgu_ses_yayin": [3, 6]}   # tahmin
# Ajan görevi (TASARIM §3.6, 40 dk; tahmin). olcekli=True olan kalem plan sayısıyla orantılı büyür, öbürleri filmde sabittir.
AJAN_40DK = {"hikaye": ([40, 75], False), "ses": ([15, 55], True), "yonetmen": ([70, 110], True), "kart": ([1, 3], False),
             "kor_gozlem": ([145, 175], True), "hakem": ([15, 40], True), "animatik": ([20, 35], False), "dikey_kesit": ([6, 10], False),
             "hat_ders": ([3, 6], False), "replik_kabul": ([5, 15], True), "kurgu": ([20, 35], False), "yayin": ([5, 10], False)}
AI84_FORMUL = ([5000, 10000], 500)        # [sabit en az, en çok] + dk başına (TASARIM §1.6: 30 dk 20–25 bin, 40 dk 25–30 bin; [SM2] tahmin)
URETIM_SN_720P = 120                      # Flow 720p klip üretim süresi (Ö0-b ölçer; tahmin)
GONDER_ISLEM_SN = 20                      # kullanıcının bir GÖNDER'e ayırdığı süre (bakma + basma; tahmin)
PAKET_PLAN = 30                           # bir Gemini paketindeki plan (Ö0-e denemesi)
KART_PAKET = 2                            # kart paketleri (A10d; tahmin)
PAKET_DK = 10                             # paket başına el işi (dk; tahmin)
CAPCUT_ACKAPA = (3, 5)                    # (kez, dk) CapCut'ı kapatıp açma (TASARIM §8.1 "2–4 kez"; tahmin)
DISA_AKTARIM_DK = 30                      # 4K 24 fps dışa aktarım başında geçen süre (tahmin)
D_TAK = 2                                 # D diskini takma (A16, A17 arşivi; tahmin)
BLOK_PLAN_MAX = 20                        # blok ≤ 20 plan (TASARIM §1.3 A14)


def _ceil(x): return int(math.ceil(x - 1e-9))


def say(n):
    """Türkçe binlik ayırıcı: 4872 → '4.872'."""
    if n is None: return "—"
    return f"{int(round(n)):,}".replace(",", ".")


def ond(x, n=2): return (f"{x:.{n}f}").replace(".", ",")


def aralik(a): return f"{say(a[0])}–{say(a[1])}" if a[0] != a[1] else say(a[0])


def _veri_yolu(*parca):
    try: return os.path.join(ortak.yollar()["veri_kok"], *parca)
    except ortak.YolYok: return None


def _json(x):
    """Sözlük ya da dosya yolu → sözlük (yoksa None). Bozuk dosya ValueError verir."""
    if x is None or isinstance(x, dict): return x
    if not os.path.exists(x): return None
    with open(x, encoding="utf-8-sig") as f: return json.load(f)


def olcum_oku(olcum=None):
    """OLCUM0 içeriği (sözlük) ya da {}; yol verilmezse <veri>/BILGI/OLCUM0/OLCUM0.json aranır."""
    if olcum is None:
        p = _veri_yolu("BILGI", "OLCUM0", "OLCUM0.json")
        olcum = p if p and os.path.exists(p) else {}
    return _json(olcum) or {}


def ayar_oku(ayar=None):
    if ayar is None:
        p = _veri_yolu("AYARLAR", "FILM_AYAR.json")
        ayar = p if p and os.path.exists(p) else {}
    return _json(ayar) or {}


def _bolum(olcum, ad):
    """OLCUM0'da O0b/O0e/O0f bölümü; düz dosya (ör. O0b.json) verilmişse kendisi."""
    if not olcum: return {}
    for k in (ad, ad.upper(), ad.replace("O0", "o0")):
        if isinstance(olcum.get(k), dict): return olcum[k]
    return olcum if any(k in olcum for k in ("olculen_gunluk_kapasite", "gemini_api_paket", "gorev_basi_token")) else {}


def kapasite(E, olcum):
    """Günlük Flow video kapasitesi. (değer, ölçüldü_mü, Ö0-b_yapıldı_mı, açıklama).
    Öncelik: hat_esikleri.json olculen_gunluk_kapasite (Ö0-b yazar) → OLCUM0 O0b. Ölçülmediyse ihtiyatlı varsayım: Ö0-b merdiveninin ilk
    basamağı (o0b_gun_tavanlari[0]; bugün 10)."""
    ilk = (E.get("o0b_gun_tavanlari") or [10])[0]
    v = E.get("olculen_gunluk_kapasite")
    if isinstance(v, (int, float)) and v > 0: return v, True, True, "hat_esikleri.json olculen_gunluk_kapasite (Ö0-b)"
    b = _bolum(olcum, "O0b")
    v = b.get("olculen_gunluk_kapasite")
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0 and not b.get("olculemedi"):
        return v, True, True, "OLCUM0 O0b"
    if b and (b.get("olculemedi") or "olculen_gunluk_kapasite" in b):
        return ilk, False, True, f"Ö0-b ölçülemedi (uyarısız gün yok); varsayım {ilk}/gün (Ö0-b merdiveninin ilk basamağı)"
    return ilk, False, False, f"ölçülmedi (Ö0-b yok); varsayım {ilk}/gün (Ö0-b merdiveninin ilk basamağı)"


def sahne_say(sahneler):
    """SAHNELER.json (v1 ya da v2) → {plan, klip, flow_klip, diger_klip, uretilmis_klip, klip_sn_farkli}.
    Başka planın klibinden çıkan plan (uretim.kaynak_klip ya da kaynak_klip dolu) klip istemez. v1'de her plan bir kliptir."""
    planlar = (sahneler or {}).get("sahneler") or []
    s = {"plan": len(planlar), "klip": 0, "flow_klip": 0, "diger_klip": 0, "uretilmis_klip": 0, "klip_sn_farkli": 0}
    for p in planlar:
        u = p.get("uretim") or {}
        if u.get("kaynak_klip") is not None or p.get("kaynak_klip") is not None: continue
        s["klip"] += 1
        if (u.get("saglayici") or "flow") == "flow": s["flow_klip"] += 1
        else: s["diger_klip"] += 1
        if u.get("durum") in ("gecti", "uretildi", "indirildi"): s["uretilmis_klip"] += 1
        ksn = u.get("klip_sn") or (p.get("zanaat") or {}).get("klip_sn")
        if ksn not in (None, 8): s["klip_sn_farkli"] += 1
    return s


def esik_yukle(E=None, ayar=None):
    return E if E is not None else esikler.yukle(ayar=ayar or None)


def imza(*parcalar):
    return hashlib.sha1(json.dumps(parcalar, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()[:8]


def _tempo_sn(E):
    t = (E.get("flow_tempo_1710") or {}).get("elle") or {}
    ara = t.get("gonderim_arasi_sn") or [6, 15]; mola = t.get("gonderim_mola_dk") or [3, 6]; kac = t.get("mola_kac_gonderimde") or 0
    sn = sum(ara) / 2.0 + ((sum(mola) / 2.0 * 60 / kac) if kac else 0)
    return sn, max(1, int(t.get("ayni_anda") or 1))


def hesapla(sure_sn, E=None, olcum=None, ayar=None, plan=None, klip=None, film_durum=None):
    """Bir film süresi için bütün ölçek sayıları (sözlük). plan/klip verilirse (SAHNELER'den) tahmin yerine onlar kullanılır."""
    ayar_d = ayar_oku(ayar) if not isinstance(ayar, dict) else ayar
    E = esik_yukle(E, ayar_d)
    olcum = olcum_oku(olcum) if not isinstance(olcum, dict) else olcum
    olculmedi = []
    sure_sn = int(sure_sn); dk = sure_sn / 60.0
    # --- plan ve klip
    dag = E.get("hedef_plan_dagilimi_40dk") or {}
    plan_40 = sum(v for v in dag.values() if isinstance(v, (int, float)))
    tol = E.get("plan_sayisi_tolerans_oran") or 0.0
    bolme = E.get("klip_bolme_oran_hedef") or 0.0
    plan_t = int(round(plan_40 * sure_sn / REF_SN))
    plan_k = int(plan) if plan is not None else plan_t
    klip_k = int(klip) if klip is not None else _ceil(plan_k * (1 - bolme))
    p = {"tahmin": plan_t, "kullanilan": plan_k, "kaynak": "SAHNELER.json" if plan is not None else "olcek (RE)",
         "aralik": [_ceil(plan_t * (1 - tol)) if tol else plan_t, int(plan_t * (1 + tol))],
         "klip": klip_k, "klip_kaynak": "SAHNELER.json" if klip is not None else "olcek (RE)",
         "formul": f"plan = round({plan_40} × {sure_sn} / {REF_SN}); klip = ceil(plan × (1 − {bolme}))"}
    # --- kredi
    kk = E.get("kredi_klip_720p") or 12
    kapi = E.get("kapi_payi") or 0.0
    gp = E.get("guvenlik_payi") or 0.0
    take = int(E.get("take_payi_kredi") or 0)
    hedef_oran = E.get("kredi_yeniden_deneme_payi") or 0.0
    taban = klip_k * kk
    kapi_kr = _ceil(taban * kapi)
    oranlar = dict(E.get("yeniden_pay_dilim") or YENIDEN_PAY_DILIM)
    top = sum(oranlar.values()) or 1.0
    dilim = {k: _ceil(taban * kapi * v / top) for k, v in oranlar.items()}
    butce = taban + kapi_kr + take
    olcum_kredi = sum(E.get("o0b_gun_tavanlari") or []) * kk
    kr = {"klip_kredi": kk, "taban": taban, "hedef_yeniden_oran": hedef_oran, "hedef_toplam": _ceil(taban * (1 + hedef_oran)),
          "kapi_payi_oran": kapi, "kapi_payi": kapi_kr, "dilimler": dilim,
          "dilim_oranlari": {k: round(kapi * v / top, 4) for k, v in oranlar.items()},
          "take_payi": take, "butce_tahmini": butce, "guvenlik_payi": gp,
          "gereken_bakiye": _ceil(butce / (1 - gp)) if gp < 1 else None, "olcum_kredi": olcum_kredi,
          "formul": f"taban = {klip_k} × {kk}; kapı = ceil(taban × {kapi}); BUT = taban + kapı + take {take}; "
                    f"bakiye ≥ BUT / (1 − {gp})"}
    # --- gönderim
    v_yeniden = _ceil(kapi_kr / kk); v_take = _ceil(take / kk)
    g_oran = [float(x) for x in GORSEL_DUZELTME_PLAN_ORAN]
    gorsel = [_ceil(plan_k * g_oran[0]), _ceil(plan_k * g_oran[1])]
    gon = {"video_ilk": klip_k, "video_yeniden": v_yeniden, "video_take": v_take, "video_toplam": klip_k + v_yeniden + v_take,
           "gorsel_duzeltme": gorsel, "blok": _ceil((klip_k + v_yeniden + v_take) / BLOK_PLAN_MAX)}
    # --- kapasite ve takvim
    kap, olculdu, o0b_var, kap_not = kapasite(E, olcum)
    if not olculdu: olculmedi.append("günlük Flow video kapasitesi: " + kap_not)
    gtavan = E.get("flow_gorsel_gunluk_tavan") or 20
    video_gun = _ceil(gon["video_toplam"] / kap)
    gorsel_gun = [_ceil(gorsel[0] / gtavan), _ceil(gorsel[1] / gtavan)]
    sureler = dict(SURELER_GUN); sureler.update({k: v for k, v in (olcum.get("sureler_gun") or {}).items() if k in SURELER_GUN})
    if not olcum.get("sureler_gun"): olculmedi.append("kâğıt, yerel hazırlık, animatik ve kurgu/ses/yayın gün sayıları tahmindir")
    flow_gun = [video_gun + gorsel_gun[0], video_gun + gorsel_gun[1]]
    toplam = [flow_gun[0] + sum(v[0] for v in sureler.values()), flow_gun[1] + sum(v[1] for v in sureler.values())]
    hedef_gun = (ayar_d.get("butce") or {}).get("takvim_hedef_gun") or 21
    tk = {"kapasite_gunluk": kap, "kapasite_olculdu": olculdu, "o0b_yapildi": o0b_var, "kapasite_not": kap_not,
          "video_gun": video_gun, "gorsel_gunluk_tavan": gtavan, "gorsel_gun": gorsel_gun, "flow_gun": flow_gun,
          "asamalar_gun": sureler, "toplam_gun": toplam, "takvim_hedef_gun": hedef_gun, "video_sigar": video_gun <= hedef_gun,
          "gece_varsayilmaz": True,
          "formul": f"video_gun = ceil({gon['video_toplam']} / {kap}); gorsel_gun = ceil(görsel / {gtavan}); görsel günü ≠ video günü"}
    # --- ajan görevi
    oran = plan_k / float(plan_40) if plan_40 else dk / 40.0
    kalem = {k: ([_ceil(a[0] * oran), _ceil(a[1] * oran)] if olc else list(a)) for k, (a, olc) in AJAN_40DK.items()}
    ag = [sum(v[0] for v in kalem.values()), sum(v[1] for v in kalem.values())]
    carpan = E.get("gorev_tavani_carpan") or 1.5
    aj = {"kalemler": kalem, "toplam": ag, "gorev_tavani_carpan": carpan,
          "gorev_tavani": {k: _ceil(v[1] * carpan) for k, v in kalem.items()}, "kagit_gorev_tavani": _ceil(kalem["hikaye"][1] * carpan),
          "kaynak": "TASARIM §3.6 (40 dk; tahmin); plan sayısıyla ölçeklenen kalemler: "
                    + ", ".join(k for k, (_, o) in AJAN_40DK.items() if o)}
    olculmedi.append("ajan görevi sayıları tahmindir (Ö0-f ve ilk 30–50 görev ölçer)")
    # --- token
    f = _bolum(olcum, "O0f"); gbt = f.get("gorev_basi_token"); tk_kaynak = "OLCUM0 O0f"
    fd = _json(film_durum) if film_durum is not None else None
    if fd:
        sy = (fd.get("sayaclar") or {}).get("gorev") or 0; t = (fd.get("harcama") or {}).get("token") or {}
        if sy >= 30 and (t.get("girdi") or t.get("cikti")):
            gbt = ((t.get("girdi") or 0) + (t.get("cikti") or 0)) / float(sy); tk_kaynak = f"FILM_DURUM ({sy} görev; D-08)"
    if gbt:
        proj = [_ceil(ag[0] * gbt), _ceil(ag[1] * gbt)]
        tok = {"gorev_basi": int(gbt), "projeksiyon": proj, "film_token_tavan_onerisi": _ceil(proj[1] * 1.5), "kaynak": tk_kaynak,
               "film_token_tavan_esik": E.get("film_token_tavan")}
    else:
        tok = {"gorev_basi": None, "projeksiyon": None, "film_token_tavan_onerisi": None, "kaynak": "ölçülmedi",
               "film_token_tavan_esik": E.get("film_token_tavan")}
        olculmedi.append("token projeksiyonu: ölçülmedi (Ö0-f ya da ilk 30–50 görev; D-08)")
    # --- AI84
    a_t = (ayar_d.get("butce") or {}).get("ai84_kredi_tavan_film") or 60000
    ai = {"tahmin": [_ceil(AI84_FORMUL[0][0] + AI84_FORMUL[1] * dk), _ceil(AI84_FORMUL[0][1] + AI84_FORMUL[1] * dk)],
          "tavan_film": min(a_t, 60000), "kaynak": "TASARIM §1.6 [SM2] (tahmin)"}
    # --- kullanıcının el işi (D-06, §8.1)
    tempo_sn, ayni = _tempo_sn(E)
    b = _bolum(olcum, "O0b"); usn = b.get("uretim_sn_720p")
    if not usn: usn = URETIM_SN_720P; olculmedi.append(f"Flow 720p üretim süresi: ölçülmedi; varsayım {URETIM_SN_720P} sn")
    sn_gon = max(tempo_sn, usn / float(ayni)) + GONDER_ISLEM_SN
    gonder = gon["video_toplam"] + gorsel[1]
    e = _bolum(olcum, "O0e"); api_paket = bool(e.get("gemini_api_paket"))
    paket = 0 if api_paket else _ceil(plan_k / float(PAKET_PLAN)) + KART_PAKET
    sa_video = gon["video_toplam"] * sn_gon / 3600.0; sa_gorsel = gorsel[1] * sn_gon / 3600.0
    sa_paket = paket * PAKET_DK / 60.0; sa_capcut = (CAPCUT_ACKAPA[0] * CAPCUT_ACKAPA[1] + DISA_AKTARIM_DK) / 60.0
    el = {"gonder": gonder, "gonder_video": gon["video_toplam"], "gonder_gorsel": gorsel[1], "gonder_basi_sn": round(sn_gon, 1),
          "video_gun": video_gun, "gunluk_saat": round(sa_video / video_gun, 1) if video_gun else 0.0,
          "paket": paket, "paket_kaynak": "Gemini API (Ö0-e)" if api_paket else f"ceil(plan / {PAKET_PLAN}) + {KART_PAKET} kart paketi",
          "muzik_paket": 0, "d_tak": D_TAK, "capcut_kez": CAPCUT_ACKAPA[0],
          "tamam": paket + gon["blok"] + CAPCUT_ACKAPA[0] + D_TAK,
          "saat": {"video": round(sa_video, 1), "gorsel": round(sa_gorsel, 1), "paket": round(sa_paket, 1), "capcut": round(sa_capcut, 1)},
          "toplam_saat": round(sa_video + sa_gorsel + sa_paket + sa_capcut, 1),
          "formul": "GÖNDER × (max(tempo, üretim/aynı_anda) + işlem) + paket × süre + CapCut + dışa aktarım"}
    ust = {"asama": None, "arac_surum": SURUM, "esik_surum": E.get("surum"), "zaman": datetime.datetime.now().isoformat(timespec="seconds"),
           "ortam": "yerel" if os.name == "nt" else "bulut", "girdi_imza": imza(sure_sn, plan, klip, olcum, ayar_d.get("butce"))}
    return {"_surum": 1, "_uretim": ust, "sure_sn": sure_sn, "sure_dk": round(dk, 1),
            "sure_aralik_sn": E.get("film_sure_aralik_sn") or SURE_ARALIK_VARSAYILAN,
            "plan": p, "kredi": kr, "gonderim": gon, "takvim": tk, "ajan": aj, "token": tok, "ai84": ai, "el_isi": el,
            "olculmedi": olculmedi}


# ---------------------------------------------------------------- metin çıktıları
def metin(o):
    p, k, g, t, a, el = o["plan"], o["kredi"], o["gonderim"], o["takvim"], o["ajan"], o["el_isi"]
    s = [f"=== {o['sure_dk']:g} dk ({o['sure_sn']} sn) ===",
         f"Plan ≈ {say(p['kullanilan'])} ({p['kaynak']}; RE aralığı {aralik(p['aralik'])}) · klip ≈ {say(p['klip'])}",
         f"Flow video kredisi (720p 8 sn = {k['klip_kredi']} kr):",
         f"  taban {say(p['klip'])} klip × {k['klip_kredi']} {'.' * 22} {say(k['taban']):>7}",
         f"  RE yeniden deneme hedefiyle (× {ond(1 + k['hedef_yeniden_oran'])}) {'.' * 9} {say(k['hedef_toplam']):>7}   (hedef; bütçe değil)",
         f"  + kapı payı {ond(k['kapi_payi_oran'])} ({', '.join(f'{d} {say(v)}' for d, v in k['dilimler'].items())}) "
         f"→ {say(k['taban'] + k['kapi_payi'])}",
         f"  + take payı {say(k['take_payi'])} {'.' * 24} {say(k['butce_tahmini']):>7}   ← BUT tahmini",
         f"  gereken bakiye (güvenlik payı {ond(k['guvenlik_payi'])}) {'.' * 10} {say(k['gereken_bakiye']):>7}",
         f"Flow gönderimi: video {say(g['video_toplam'])} (ilk {say(g['video_ilk'])} + yeniden {say(g['video_yeniden'])} + take "
         f"{say(g['video_take'])}; {g['blok']} blok) · görsel düzeltme {aralik(g['gorsel_duzeltme'])}",
         f"Kapasite: {t['kapasite_gunluk']}/gün ({'ölçüldü' if t['kapasite_olculdu'] else 'ÖLÇÜLMEDİ'}: {t['kapasite_not']})",
         f"Takvim: video {t['video_gun']} gün + görsel {aralik(t['gorsel_gun'])} gün = Flow {aralik(t['flow_gun'])} gün; "
         f"toplam ≈ {aralik(t['toplam_gun'])} gün (hedef video ≤ {t['takvim_hedef_gun']} gün: {'sığar' if t['video_sigar'] else 'SIĞMAZ'})",
         f"Ajan görevi ≈ {aralik(a['toplam'])} (kâğıt aşaması görev tavanı {a['kagit_gorev_tavani']})",
         f"AI84 ≈ {aralik(o['ai84']['tahmin'])} kr (tavan {say(o['ai84']['tavan_film'])})",
         f"Token: {('≈ ' + aralik(o['token']['projeksiyon'])) if o['token']['projeksiyon'] else 'ölçülmedi'}",
         f"Kullanıcının el işi ≈ {ond(el['toplam_saat'], 1)} saat (GÖNDER {say(el['gonder'])} kez, {el['paket']} paket, "
         f"video günü başına ≈ {ond(el['gunluk_saat'], 1)} saat)"]
    if o["olculmedi"]: s.append("Ölçülmedi / tahmin: " + "; ".join(o["olculmedi"]))
    return "\n".join(s)


def karsilastirma(liste):
    satir = [("Süre", lambda o: f"{o['sure_dk']:g} dk"), ("Plan", lambda o: say(o["plan"]["kullanilan"])),
             ("Klip", lambda o: say(o["plan"]["klip"])), ("Taban kredi", lambda o: say(o["kredi"]["taban"])),
             ("RE hedefi (×1,2)", lambda o: say(o["kredi"]["hedef_toplam"])),
             ("+ kapı payı", lambda o: say(o["kredi"]["taban"] + o["kredi"]["kapi_payi"])),
             ("BUT tahmini (+take)", lambda o: say(o["kredi"]["butce_tahmini"])),
             ("Gereken bakiye", lambda o: say(o["kredi"]["gereken_bakiye"])),
             ("Video gönderimi", lambda o: say(o["gonderim"]["video_toplam"])),
             ("Görsel düzeltme", lambda o: aralik(o["gonderim"]["gorsel_duzeltme"])),
             ("Video günü", lambda o: str(o["takvim"]["video_gun"])), ("Görsel günü", lambda o: aralik(o["takvim"]["gorsel_gun"])),
             ("Toplam takvim (gün)", lambda o: aralik(o["takvim"]["toplam_gun"])), ("Ajan görevi", lambda o: aralik(o["ajan"]["toplam"])),
             ("AI84 kredisi", lambda o: aralik(o["ai84"]["tahmin"])), ("El işi (saat)", lambda o: ond(o["el_isi"]["toplam_saat"], 1))]
    gen = max(len(a) for a, _ in satir)
    s = [f"{a:<{gen}}  " + "  ".join(f"{fn(o):>11}" for o in liste) for a, fn in satir]
    t = liste[0]["takvim"]
    s.append(f"Kapasite {t['kapasite_gunluk']}/gün — {'ölçüldü' if t['kapasite_olculdu'] else 'ÖLÇÜLMEDİ: ' + t['kapasite_not']}")
    s.append("Ölçülmedi / tahmin: " + "; ".join(liste[0]["olculmedi"]))
    return "\n".join(s)


def kart_md(o):
    """Kullanıcı sözleşmesi kartı (TASARIM §8.1); sayılar bu araçtan."""
    el, t, k = o["el_isi"], o["takvim"], o["kredi"]
    kap = "" if t["kapasite_olculdu"] else " (Flow'un günlük kapasitesi henüz ölçülmedi; ihtiyatlı varsayım)"
    return "\n".join([
        f"SENDEN İSTENEN TEK KARAR: filmin konusu (bir cümle). Gerisini ekip karar verir; sana \"hangisi?\" diye sorulmaz.",
        f"SENDEN İSTENEN FİZİKSEL İŞLER ({o['sure_dk']:g} dk'lık film için tahmini; film başında güncellenir):",
        "  • Flow'a Google ile giriş ve gerekirse \"ben robot değilim\" doğrulaması ............ kurulumda 1 kez + istendikçe",
        "  • Ücretsiz Gemini anahtarı almak ve AYARLAR'a koymak (filmi yayından önce bir \"kulak\"",
        "    dinlesin diye; para yok, soru değil) ................................................ kurulumda 1 kez (≈ 5–10 dk, tahmin)",
        "  • İlk kurulum ölçümü: 3 günde ≈ 10 / 15 / 20 video için GÖNDER (eski B3 planlarıyla",
        f"    ölçüm; ≤ {say(k['olcum_kredi'])} kredi) ......................................................... yalnız ilk filmden önce",
        f"  • Gemini paketlerini taşımak (klasörü Gemini'ye ver, gelen ZIP'i GELENLER'e at) ..... ≈ {el['paket']} paket (Gemini API bağlıysa 0)",
        f"  • Video oturumları: VIDEO_YARI_OTOMATIK.bat'ı aç, Memmet hazırlayınca GÖNDER'e bas .. ≈ {say(el['gonder_video'])} kez, "
        f"≈ {t['video_gun']} gün, günde ≈ {ond(el['gunluk_saat'], 1)} saat{kap}",
        f"  • Görsel düzeltme oturumları (Flow görsel, aynı .bat; video günüyle aynı gün değil) .. ≈ {say(el['gonder_gorsel'])} kez, "
        f"≈ {aralik(t['gorsel_gun'])} gün",
        f"  • CapCut'ı kapatıp açmak (taslak güncellenince) ve sonunda 4K 24 fps dışa aktarmak .. ≈ 2–4 kez + 1 dışa aktarım",
        f"  • Gemini müzik paketi (yalnız kütüphane yetmezse ve Gemini koşulları uygunsa) ....... ≈ {el['muzik_paket']} paket (çoğu filmde 0)",
        f"  • D diskini takmak (arşiv ve yedek için, sistem isterse) ............................ ≈ {el['d_tak']} kez",
        f"  • [arka plan uyandırması çalışmazsa (Ö0-a)] her işten sonra sohbete \"tamam\" yazmak ... ≈ {el['tamam']} kez",
        "  • Flow uyarı verirse: GÖNDER'e BASMA, sayfayı YENİLEME; beklemek, en erken 30 dk",
        "    sonra elle 1 video denemek, UYARI_GECTI.bat ......................................... yalnız uyarı olursa",
        "  • Kredi biterse yüklemek ............................................................ yalnız gerekirse",
        f"TAHMİNİ TOPLAM EL İŞİ: ≈ {ond(el['toplam_saat'], 1)} saat · TAHMİNİ TAKVİM: ≈ {aralik(t['toplam_gun'])} gün "
        f"(Flow'un günlük güvenli kapasitesine bağlı{'; ölçülmedi' if not t['kapasite_olculdu'] else ''})",
        f"FLOW KREDİSİ: ≈ {say(k['butce_tahmini'])} kredi (taban {say(k['taban'])} + kapı payı {say(k['kapi_payi'])} + take "
        f"{say(k['take_payi'])}); hesapta en az ≈ {say(k['gereken_bakiye'])} olmalı.",
        "İSTERSEN (hiçbiri zorunlu değil, sistem beklemez): film hakkında not bırakmak (CapCut NOTLAR ya da sohbet), izinleri açmak (IZINLER.bat:",
        "gece çalışma, dolar harcama, Gemini'nin ücretli kullanımı, Flow kilitliyken Vertex, efekt indirme, YouTube bağlantısı, yükleme), kanal verisini",
        "YouTube Studio'dan CSV olarak vermek (adımlar bu dosyada).",
        "SİSTEM ASLA: Flow uyarısını atlatmaz, hızlandırmaz, sayfayı yenilemez, başka hesaba geçmez; anahtarlarını okumaz ya da yazdırmaz; dosya silmez",
        "(eski dosyaları _ESKI'ye taşır)."])


# ---------------------------------------------------------------- komut satırı
def _sahneler(kok):
    p = os.path.join(kok, "SAHNELER.json")
    return _json(p) if os.path.exists(p) else None


def main(argv):
    sureler, a, bayrak = [], {"--olcum": None, "--ayar": None, "--film": None}, set()
    i = 0
    try:
        while i < len(argv):
            x = argv[i]
            if x in ("--dk", "--sure"):
                v = float(argv[i + 1].replace(",", ".")); sureler.append(int(round(v * 60 if x == "--dk" else v))); i += 2
            elif x in a: a[x] = argv[i + 1]; i += 2
            elif x in ("--json", "--md"): bayrak.add(x); i += 1
            else: raise ValueError(x)
    except (ValueError, IndexError):
        print(__doc__); return 1
    try:
        ayar = ayar_oku(a["--ayar"]); olcum = olcum_oku(a["--olcum"]); E = esikler.yukle(ayar=ayar or None)
    except esikler.EsikHatasi as e: print("!!", e); return 1
    except ValueError as e: print(f"!! ayar ya da ölçüm dosyası okunamadı: {e}"); return 1
    plan = klip = fd = None
    if a["--film"]:
        s = _sahneler(a["--film"])
        if s:
            n = sahne_say(s); plan, klip = n["plan"], n["klip"]
        if not sureler:
            b0 = _json(os.path.join(a["--film"], "_RAPOR", "BUT0_FILM.json")) or {}
            if b0.get("sure_sn"): sureler.append(int(b0["sure_sn"]))
        fd = os.path.join(a["--film"], "FILM_DURUM.json")
        if not os.path.exists(fd): fd = None
    tek = bool(sureler)
    if not sureler: sureler = [1800, 2400, 2700]
    sonuc = [hesapla(s, E=E, olcum=olcum, ayar=ayar, plan=plan, klip=klip, film_durum=fd) for s in sureler]
    if "--json" in bayrak:
        print(json.dumps(sonuc[0] if len(sonuc) == 1 else sonuc, ensure_ascii=False, indent=1)); return 0
    if "--md" in bayrak:
        print("\n\n".join(kart_md(o) for o in sonuc)); return 0
    if tek: print("\n\n".join(metin(o) for o in sonuc))
    else: print(karsilastirma(sonuc))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
