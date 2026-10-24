"""Görsel hattı testlerinin ortak fikstürü (PR-8): geçici veri kökünde TEST evreni (kilitli kartlar, plaka, nesne) ve 3 planlık v2 film.
_ortam'dan SONRA içe alınır. Gemini paket klasörü geçici köke yönlendirilir (gerçek Masaüstüne dokunulmaz)."""
import os, sys, json, shutil, hashlib, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import _ortam
import ortak

y = ortak.json_oku(_ortam.YOLLAR); y["gemini_paket"] = os.path.join(_ortam.KOK, "GEMINI_PAKET"); ortak.atomik_yaz(_ortam.YOLLAR, y)
EVREN = os.path.join(_ortam.VERI, "EVREN")


def _jpg(yol, renk=(120, 120, 120), boyut=(1376, 768)):
    from PIL import Image
    os.makedirs(os.path.dirname(yol), exist_ok=True); Image.new("RGB", boyut, renk).save(yol, "JPEG", quality=90)
    with open(yol, "rb") as f: return hashlib.sha1(f.read()).hexdigest()


def evren_kur(seri="TEST"):
    k = os.path.join(EVREN, seri)
    if os.path.isdir(k): shutil.rmtree(k)
    ortak.atomik_yaz(os.path.join(k, "evren.json"), {"seri": seri, "surum": 1, "filmler": []})
    ortak.atomik_yaz(os.path.join(k, "dunya.json"), {"stil_eki": "35mm film grain, natural colours", "gorsel_ne_yok": ["zipper", "wristwatch"]})
    for kid, ad, kim, renk in (("mara", "Mara", "an adult woman with one long dark-auburn braid over her LEFT shoulder, grey-green eyes", (150, 90, 60)),
                               ("voss", "Voss", "a broad-shouldered man with a close-cropped grey beard and a scar across his RIGHT cheekbone", (60, 70, 90))):
        h = _jpg(os.path.join(k, "karakterler", kid, "kart_k1_v1.jpg"), renk)
        ortak.atomik_yaz(os.path.join(k, "karakterler", kid, "karakter.json"),
                         {"id": kid, "ad": ad, "seri": seri, "tur": "insan", "surum": 1, "durum": "kilitli", "kimlik_en": kim,
                          "varsayilan_kostum": "k1", "kostumler": {"k1": {"tarif_en": "a dark-brown shearling coat", "kart": "kart_k1_v1.jpg"}},
                          "hash": {"kart_k1_v1.jpg": h}})
    ortak.atomik_yaz(os.path.join(k, "nesneler", "fener", "nesne.json"), {"id": "fener", "tarif_en": "a lit iron lantern", "bulucu_sorgu": "a lit lantern"})
    ph = _jpg(os.path.join(k, "mekanlar", "kulube", "plaka_ic_genel_v1.jpg"), (90, 80, 70))
    ortak.atomik_yaz(os.path.join(k, "mekanlar", "kulube", "mekan.json"),
                     {"id": "kulube", "tarif_en": "a cramped log cabin interior", "durum": "kilitli",
                      "plakalar": {"ic_genel": {"gorsel": "plaka_ic_genel_v1.jpg", "sha1": ph, "durum": "kilitli"}}})
    return k


def _plan(no, kad, konum, sira, tip="eylem", ayna_yasak=True, konusan=None, eller=None):
    return {"no": no, "sira": no, "parti": 1, "amac": "x",
            "zanaat": {"kod": f"S01-P{no}", "sahne_grubu": "S01", "plan_tipi": tip, "klip_sn": 8,
                       "kamera": {"kurulum": "KAM1", "kadraj": "O", "aci": "goz_hizasi", "lens_mm": 50},
                       "kadrajdakiler": [{"id": k, "olcek": "O", "yuz_acisi": "3/4", "konusur": k == konusan} for k in kad],
                       "zincir": {"gecis_turu": "yeni_sahne", "baslangic": "ana_kare", "ebeveyn": "plaka:ic_genel"},
                       "oyunculuk": {k: {"dis_ifade": {"bas": "dikkatli"}} for k in kad}, "yasaklar": []},
            "_derlenir": {"kadraj_konumu": konum, "kadraj_sirasi": sira, "bakis_kadrajda": {k: "kadraj_soluna" for k in kad},
                          "ayna_yasak": ayna_yasak, "gorunmesi_gerekenler": list(kad), "isik_kadrajda": "soldan"}}


def film_kur(ad="TF", seri="TEST"):
    kok = os.path.join(_ortam.VERI, "FILMLER", ad)
    if os.path.isdir(kok): shutil.rmtree(kok)
    os.makedirs(kok)
    ortak.atomik_yaz(os.path.join(kok, "HAZIRLIK.json"), {"film": ad, "seri": seri, "saglayici": "sahte"})
    ortak.atomik_yaz(os.path.join(kok, "HIKAYE.json"), {"evren": seri, "karakterler": {"mara": {"ad": "Mara", "rol": "kahraman"},
                                                                                      "voss": {"ad": "Voss", "rol": "karsit"}},
                                                         "mekanlar": [{"id": "kulube"}]})
    S = {"_surum": 2, "film": ad, "karakterler": {"mara": {}, "voss": {}},
         "sahne_gruplari": {"S01": {"mekan": "kulube", "isik": {"ana": "hearth fire"}, "zaman": {"gun_saati": "gece"},
                                    "yasaklar": ["no open flame in frame except the hearth"]}},
         "sahneler": [_plan(101, ["mara"], {"mara": "sag_ucte_bir"}, ["mara"]),
                      _plan(102, ["mara", "voss"], {"mara": "sol_ucte_bir", "voss": "sag_ucte_bir"}, ["mara", "voss"], tip="diyalog",
                            ayna_yasak=False, konusan="mara"),
                      _plan(103, ["voss"], {"voss": "orta"}, ["voss"])]}
    ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), S)
    el = lambda n: {"sag": {"tutar": n}, "sol": {}}
    D = {"planlar": {str(no): {"bas": "x", "bit": "y", "durum": {"bas": {"karakterler": k}, "bit": {"karakterler": k}}}
                     for no, k in ((101, {"mara": {"eller": el("fener"), "poz": "ayakta"}}),
                                   (102, {"mara": {"eller": el("fener")}, "voss": {"eller": el(None)}}),
                                   (103, {"voss": {"eller": el(None)}}))},
         "dondurulmus": {}, "gozlenen": {}}
    ortak.atomik_yaz(os.path.join(kok, "DUNYA_DEFTERI.json"), D)
    return kok


def g1_hazirla(hata_plan=None, ad="TF"):
    """İstem → paket → sahte adaylar → yerel ölçüm + kör paket → sahte kör cevaplar. Film kökünü döndürür."""
    import istem_derle_gorsel as idg, gemini_paket, gemini_al, kare_denetim as kd, kor
    evren_kur(); kok = film_kur(ad)
    idg.derle_gorsel(kok)
    gemini_paket.paket_gorsel(kok, 1, 2, 1, kapak=False)
    gemini_al.sahte_uret(kok, "gorsel", hata_plan)
    kd.olc(kok, 1)
    kor.sahte_cevaplar(kok, "g1", 1)
    return kok


def planlar(kok): return {p["no"]: p for p in ortak.json_oku(os.path.join(kok, "SAHNELER.json"))["sahneler"]}
