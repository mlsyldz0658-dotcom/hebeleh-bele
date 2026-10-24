"""PLAN ORTAK — yönetmen kâğıdı araçlarının (PR-6) paylaştığı küçük yardımcılar (TASARIM §5.1, §5.2, §6.4, §7.2).

Kodda:
  import plan_ortak as po
  po.sozluk("plan") / po.sozluk("fiil") / po.sozluk("ifade") / po.sozluk("efekt")   veri/*.json (önbellekli)
  po.esik()                 eşikler (esikler.yukle; okunamazsa yerleşik varsayılanlar + E.hata)
  po.film_kok(arg)          film klasörü: yol ya da ad (<veri>/FILMLER/<ad>, ortak.yollar())
  po.gorev()                film.py görev bağlamı (YZ_FILM_GOREV/GOREV.json): {id, asama, tur_no, rapor} ya da {}
  po.rapor_yaz(kok, kapi, kapsam, olcumler, asama=…, arac=…, varsayilan="_RAPOR/…")  kapi.py zarfıyla atomik yazım
  po.imza(x) · po.al(d, "a.b.c") · po.koy(d, "a.b.c", v) · po.m(madde, seviye, plan=…, **ek)
Kurallar: yollar yalnız ortak.yollar()'dan; yazım ortak.atomik_yaz ile; rapor zarfı kapi.rapor_kur ile kurulur ve kapi.dogrula'dan geçer.
hat.asamalar.YEREL_KAPILAR'daki (ADLAR'da henüz olmayan) kâğıt kapıları (HARITA …) yalnız "kapı bilinmiyor" maddesiyle hoş görülür.
"""
import os, sys, json, hashlib, copy
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak

VERI = os.path.join(HERE, "veri")
SEMALAR = os.path.join(ortak.DEPO_KOK, ".claude", "skills", "film-yap", "semalar")
# çıkış kodları (TASARIM §1.1)
BITTI, HATA, KULLANICI, AJAN, ORTAM, BUTCE, KAPI, KISIT, BEKLE = range(9)
_SOZ = {"plan": "plan_sozlukleri.json", "fiil": "fiil_sozlugu.json", "ifade": "ifade_sozlugu.json", "efekt": "efekt_sozlugu.json"}
_ONB = {}
VARSAYILAN_ESIK = {
    "eylem_adim_max": 3, "eylem_adim_konusmali_max": 1, "eylem_adim_min_sn": 1.5, "eylem_adim_mikro_min_sn": 0.8, "plan_adim_min": 2,
    "plan_ilk_adim_min_sn": 0.5, "plan_son_adim_pay_sn": 1.0, "plan_es_zamanli_ozne_max": 1, "plan_konusma_adim_arasi_min_sn": 0.2,
    "plan_goz_farki_bakis_m": 0.3, "plan_hareket_istem_kelime_max": 75, "plan_adim_cumle_kelime_max": 16, "plan_istem_elle_oran_max": 0.05,
    "plan_dialog_kurulum_min": 3, "zincir_derinlik_max": 2, "plan_agac_derinlik_max": 3, "devam_kesme_tutma_min_sn": 0.2,
    "ortulu_devam_araya_min_sn": 1.0, "plan_bitis_ozel_oran_max": 0.1, "aci_min_fark_derece": 30, "olcek_kademe_min_fark": 2,
    "ayni_kamera_konumu_ardisik_max": 2, "ayni_plan_tipi_ardisik_max": 4, "sahne_konum_plani_max_sira": 3, "sahne_yeniden_konum_sn": 90,
    "kamera_hareketi_klip_max": 1, "konusan_karede_max": 1, "referans_max": 2, "replik_max_kelime_8sn": 16, "replik_max_kelime": 20,
    "konusma_hizi_kelime_sn": 2.5, "konusma_hizi_agir_kelime_sn": 2.0, "diyalog_giris_payi_sn": 0.4, "diyalog_cikis_payi_sn": 0.5,
    "cumle_arasi_sn": 0.25, "kullanim_bas_min_sn": 0.3, "kullanim_son_pay_sn": 0.5, "klip_bolme_min_kullanilabilir_sn": 6.0,
    "klip_bolme_atlama_min_sn": 0.4, "l_kesme_aralik_sn": [0.3, 2.5], "j_kesme_aralik_sn": [0.3, 0.8], "tepki_orani_min": 0.25,
    "jl_kesme_orani_min": 0.3, "plan_sayisi_tolerans_oran": 0.15, "sahne_max_sn": 180, "klip_sn": [8, 10], "bitis_tutma_sn": 0.5,
    "olcek_kademeleri": {"EG": 1, "G": 2, "OG": 3, "O": 4, "OY": 5, "Y": 6, "CY": 7}, "geri_donus_max_sn": 20,
    "yasak_sonuc_fiilleri": ["take", "takes", "grab", "grabs", "pick up", "picks up", "get", "gets", "use", "uses", "fix", "fixes",
                             "prepare", "prepares", "fight", "fights", "search", "searches"],
    "dusuk_guven_hareketler": ["yörünge", "hizli_hareket"], "plan_konusan_yaw_max": 45, "ifade_zorunlu_insanli_plan": True,
    "duygu_sicramasi_gerekcesiz": 0, "plan_sure_aralik_sn": {}, "sahne_tipi_aralik": {}, "duygu_turleri": [],
}


def sozluk(ad):
    if ad not in _ONB:
        _ONB[ad] = ortak.json_oku(os.path.join(VERI, _SOZ.get(ad, ad)), {}) or {}
    return _ONB[ad]


def fiiller(): return sozluk("fiil").get("fiiller") or {}


class _Esik(dict):
    hata = None
    surum = None


def esik():
    if "_esik" in _ONB: return _ONB["_esik"]
    E = _Esik(VARSAYILAN_ESIK)
    try:
        import esikler
        y = esikler.yukle(); E.update(y); E.surum = esikler.SURUM
        if E.get("plan_goz_yukseklik_m") is None: E["plan_goz_yukseklik_m"] = None
    except Exception as e:                                   # eşik dosyası bozuksa yerleşik değerler; rapora not düşülür
        E.hata = f"{e.__class__.__name__}: {str(e)[:200]}"
    _ONB["_esik"] = E
    return E


def film_kok(arg):
    if not arg: raise SystemExit("--film <film klasörü ya da adı> gerekli")
    if os.path.isdir(arg): return os.path.abspath(arg)
    try: p = os.path.join(ortak.yollar()["filmler"], arg)
    except ortak.YolYok: p = arg
    if not os.path.isdir(p):
        print(f"!! film klasörü yok: {arg}", flush=True); sys.exit(KULLANICI)
    return os.path.abspath(p)


def gorev():
    d = os.environ.get("YZ_FILM_GOREV")
    if not d: return {}
    g = ortak.json_oku(os.path.join(d, "GOREV.json"), {}) or {}
    g.setdefault("id", os.path.basename(os.path.normpath(d)))
    return g


def imza(x):
    s = json.dumps(x, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:8]


def al(d, yol, vars=None):
    for p in yol.split("."):
        if not isinstance(d, dict) or p not in d: return vars
        d = d[p]
    return d


def koy(d, yol, v):
    ps = yol.split(".")
    for p in ps[:-1]:
        if not isinstance(d.get(p), dict): d[p] = {}
        d = d[p]
    d[ps[-1]] = copy.deepcopy(v)


# Kâğıt kurallarının ayrıntılı kök nedeni → veri/kok_neden.json'daki ad (kuyruk yalnız oradakileri kabul eder; ayrıntı maddede kalır).
# Yönetmen kökleri eylem_zinciri (Y01–Y08) ve diyalog_suresi (Y30/Y31/Y59) sözlükte olduğundan eylem/diyalog ayrıntıları onlara gider.
_EYLEM = ("adim_sayisi", "adim_suresi", "eksik_parametre", "yasak_fiil", "konusurken_eylem", "bitis_tutmasi")
KOK_ESLEME = dict({"cift_konusan": "konusan_belirsiz", "replik_uzun": "diyalog_suresi", "replik": "diyalog_suresi",
                   "filtre": "filtre_kelimesi", "ekranda_bilgi": "bilgi_ekranda_yok", "ilk_eylem": "gec_giris", "kurulum": "kurulum_yok",
                   "merak": "bilgi_eksik", "risk": "risk_belirsiz", "yogunluk": "ritim_tekduze", "sure": "uzun_plan", "plan_suresi": "uzun_plan",
                   "sahne_suresi": "uzun_plan", "zincir": "zincir_dikis", "yon": "ekran_yonu", "referans": "fazla_kisi", "ad": "ad_gec"},
                  **{k: "eylem_zinciri" for k in _EYLEM})


def kok_normal(kn, vars="hikaye_adimi_ekranda_yok"):
    try:
        gecerli = set((ortak.json_oku(os.path.join(VERI, "kok_neden.json"), {}) or {}).get("kok_nedenler") or {})
    except Exception: gecerli = set()
    if kn in gecerli: return kn
    k = KOK_ESLEME.get(kn, vars)
    return k if not gecerli or k in gecerli else vars


def m(madde, seviye, plan=None, **ek):
    o = {"madde": madde, "seviye": seviye}
    if plan is not None: o["plan"] = plan
    o.update({k: v for k, v in ek.items() if v is not None})
    return o


def _yerel_kapilar():
    try:
        from hat.asamalar import YEREL_KAPILAR
        return set(YEREL_KAPILAR)
    except Exception: return set()


def rapor_yaz(kok, kapi_kodu, kapsam, olcumler, asama=None, arac=None, varsayilan=None, birimler=None, ek=None,
              tur=None, girdi_imza=None, kuyruk=None):
    """Kapı raporunu kurar ve yazar. Görev bağlamı varsa (film.py calis) GOREV.json'daki rapor yolu ve görev kimliği kullanılır.
    (yol, rapor)."""
    import kapi
    g = gorev()
    tur = tur or g.get("tur_no") or 1
    E = esik()
    r = kapi.rapor_kur(kapi_kodu, kapsam, olcumler, tur=tur, asama=g.get("asama") or asama, gorev=g.get("id"),
                       girdi_imza=girdi_imza, arac_surum=arac, esik_surum=E.surum, birimler=birimler, ek=ek, kuyruk=kuyruk)
    if E.hata: r.setdefault("not", []).append("eşikler yüklenemedi; yerleşik varsayılanlar kullanıldı: " + E.hata)
    hatalar = kapi.dogrula(r)
    if kapi_kodu in _yerel_kapilar():
        hatalar = [h for h in hatalar if not h.startswith("kapi bilinmiyor")]
    if hatalar: raise kapi.RaporHatasi(hatalar)
    rel = g.get("rapor") if g.get("rapor") and g.get("kapi") == kapi_kodu else (varsayilan or os.path.join("_RAPOR", kapi.dosya_adi(kapi_kodu, kapsam)))
    yol = rel if os.path.isabs(rel) else os.path.join(kok, rel)
    ortak.atomik_yaz(yol, r)
    return yol, r


def zarf(asama, arac, sonuc="GEC", girdi_imza=None):
    import kapi
    g = gorev()
    return {"asama": g.get("asama") or asama, "gorev": g.get("id"), "girdi_imza": girdi_imza, "arac_surum": arac,
            "esik_surum": esik().surum, "sonuc": sonuc, "zaman": kapi.simdi(), "ortam": kapi.ortam()}


def cikis(r):
    """Rapor sonucu → çıkış kodu: HATA/KISMI → 1, aksi 0 (kapı kararını film.py rapordan okur)."""
    return HATA if r.get("sonuc") in ("HATA", "KISMI") else BITTI


def arg_al(argv, ad, vars=None):
    if ad in argv:
        i = argv.index(ad)
        if i + 1 < len(argv) and not argv[i + 1].startswith("--"): return argv[i + 1]
    return vars


def tur_no(argv):
    t = arg_al(argv, "--tur")
    if t: return int(t)
    return gorev().get("tur_no") or 1


def yaz_ozet(r, ad):
    oz = r.get("ozet") or {}
    print(f"{ad}: {r['sonuc']} · HATA {len(r.get('hatalar') or [])} · BAYRAK {len(r.get('bayraklar') or [])}"
          + (f" · birim {oz.get('plan', oz.get('sahne', ''))}" if oz else ""), flush=True)
    for h in (r.get("hatalar") or [])[:15]:
        print(f"  HATA {h.get('madde')} plan={h.get('plan', '-')} {h.get('neden') or h.get('olcu') or ''}", flush=True)
