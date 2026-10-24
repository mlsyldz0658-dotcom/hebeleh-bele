"""Kurgu ve ses testlerinin ortak fikstürü (PR-12): geçici veri kökünde 5 planlık küçük bir v2 filmi kurar.
S01 (eylem): #1 eylem (kutu 1,25–3,0 ve 3,6–5,2 sn kayar; a1, a2 etkili) · #2 tepki (etkisiz)
S02 (diyalog): #3 Mara konuşur R0001 (klip 2,0–4,5; L kesme 1,0 sn) · #4 Voss tepki (ağzı kapalı) · #5 Voss konuşur R0002 (klip 1,5–3,5)
Klipler sahte_klip ile (kutu = hareket, ton = konuşma); diyalog.json v2 hizalama alanlarıyla; yatak ve müzik wav'ları sentetik.
`import _ortam` testin ilk satırında yapılmış olmalı (geçici YOLLAR.json)."""
import os, sys, json, shutil
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ARACLAR = os.path.dirname(HERE)
if ARACLAR not in sys.path: sys.path.insert(0, ARACLAR)
import ortak, kurgu_ortak as ko

_ONBELLEK = {}


def _kelimeler(metin, bas, bit):
    ks = metin.split(); d = (bit - bas) / len(ks)
    return [{"w": w, "bas": round(bas + i * d, 3), "bit": round(bas + (i + 1) * d, 3)} for i, w in enumerate(ks)]


def _plan(no, sg, tip, adimlar, kullanim, kesme=None, replik=None, rz=None, kadraj="O", kurulum="KAM1", konusan=None, efekt=None,
          dondu=None, agiz="tam"):
    p = {"no": no, "sira": no, "parti": 1, "amac": f"plan {no}", "duygu": "gerilim", "kullanim": kullanim,
         "zanaat": {"kod": f"{sg}-P{no:02d}", "sahne_grubu": sg, "plan_tipi": tip, "klip_sn": 8,
                    "kamera": {"kurulum": kurulum, "kadraj": kadraj, "hareket_tipi": "sabit"},
                    "kadrajdakiler": [{"id": konusan or "mara", "olcek": kadraj, "konusur": bool(replik)}],
                    "eylem_zinciri": adimlar, "kesme": kesme or {"tip": "duz", "ses_tasma_sn": 0.0},
                    "zincir": {"gecis_turu": "yeni_sahne" if no in (1, 3) else "eylem_kesme"},
                    "ses": {"diyalog": {"yol": "veo_donustur" if replik else None}, "efektler": efekt or []}},
         "_derlenir": {"agiz_gorunur": agiz if replik else "yok", "ayna_yasak": True},
         "uretim": {"durum_dondu": dondu or {}}}
    if replik:
        p["replik"] = replik; p["_derlenir"]["replik_zaman"] = {replik["id"]: rz}
    return p


def film_kur(ad="KURGU_DENEME", klipler=True):
    """Geçici veri kökünde filmi kurar; klipler önbellekten kopyalanır (her test için yeni klasör). Film kökünü döndürür."""
    kok = os.path.join(ortak.yollar()["filmler"], ad)
    if os.path.exists(kok): shutil.move(kok, kok + f"_eski_{len(os.listdir(os.path.dirname(kok)))}")
    os.makedirs(os.path.join(kok, "SIRALI_VIDEO")); os.makedirs(os.path.join(kok, "_SES")); os.makedirs(os.path.join(kok, "MUZIK", "secilen"))
    a1 = {"id": "a1", "bas": 1.2, "bit": 3.0, "ozne": "mara", "tur": "fiziksel", "fiil": "yurur", "etki": {"mara.isaret": "M5"}}
    a2 = {"id": "a2", "bas": 3.5, "bit": 5.3, "ozne": "mara", "tur": "fiziksel", "fiil": "uzanir", "etki": {"mara.eller.sol.yer": "masa"}}
    r1 = {"id": "R0001", "karakter": "mara", "metin": "It's late Captain what do you want", "teslim": "normal"}
    r2 = {"id": "R0002", "karakter": "voss", "metin": "Open the door Mara", "teslim": "normal"}
    planlar = [
        _plan(1, "S01", "eylem", [a1, a2], {"bas": 1.0, "sure": 5.0}, efekt=[{"id": "e1", "adim": "a1", "kategori": "adim", "an": "bas",
              "kaynak_tercih": "klip", "yedek": "kutuphane"}], dondu={"bas": "d0", "bit": "d1"}, kadraj="OG"),
        _plan(2, "S01", "tepki", [{"id": "a1", "bas": 0.8, "bit": 2.5, "ozne": "voss", "tur": "mikro", "fiil": "bakar", "etki": {}}],
              {"bas": 0.6, "sure": 2.4}, konusan="voss", dondu={"bas": "d1", "bit": "d1"}, kadraj="Y", kurulum="KAM2"),
        _plan(3, "S02", "diyalog", [{"id": "a1", "bas": 2.0, "bit": 4.5, "ozne": "mara", "tur": "konusma", "fiil": "konusur",
              "replik": "R0001", "etki": {}}], {"bas": 1.6, "sure": 3.0}, kesme={"tip": "L", "ses_tasma_sn": 1.0}, replik=r1,
              rz=[2.0, 4.5], kadraj="OY", dondu={"bas": "d1", "bit": "d1"}),
        _plan(4, "S02", "tepki", [{"id": "a1", "bas": 0.8, "bit": 2.6, "ozne": "voss", "tur": "mikro", "fiil": "bakar", "etki": {}}],
              {"bas": 0.6, "sure": 2.5}, konusan="voss", dondu={"bas": "d1", "bit": "d1"}, kadraj="OY", kurulum="KAM3"),
        _plan(5, "S02", "diyalog", [{"id": "a1", "bas": 1.5, "bit": 3.5, "ozne": "voss", "tur": "konusma", "fiil": "konusur",
              "replik": "R0002", "etki": {}}], {"bas": 1.1, "sure": 2.8}, replik=r2, rz=[1.5, 3.5], konusan="voss", kadraj="OY",
              kurulum="KAM2", dondu={"bas": "d1", "bit": "d1"}),
    ]
    yatak = "_SES/yatak_kulube.wav"
    s = {"_surum": 2, "_sema": "sahneler_v2", "film": ad, "baslik": "KULUBE", "altyazi_dili": None,
         "karakterler": {"mara": {}, "voss": {}},
         "sahne_gruplari": {"S01": {"mekan": "kulube", "zaman": {"atlama": "yok"}, "sahne_tipi": "gerilim",
                                    "ses": {"yatak": {"dosya": yatak, "seviye_lufs": -38}, "oda_yaniti": "ahsap_kucuk"}},
                            "S02": {"mekan": "kulube", "zaman": {"atlama": "yok"}, "sahne_tipi": "diyalog",
                                    "ses": {"yatak": {"dosya": yatak, "seviye_lufs": -38}, "oda_yaniti": "ahsap_kucuk"}}},
         "sahneler": planlar}
    ortak.atomik_yaz(os.path.join(kok, "SAHNELER.json"), s)
    d = {"surum": 2, "ornekleme_hz": 48000, "replikler": {
        "R0001": {"karakter": "mara", "kaynak_plan": 3, "yol_plan": "veo_donustur", "yol_gercek": "veo_donustur", "teslim": "normal",
                  "senaryo_metin": r1["metin"], "duyulan_metin": r1["metin"], "kelimeler": _kelimeler(r1["metin"], 2.0, 4.5),
                  "klip_zamani": {"bas": 2.0, "bit": 4.5},
                  "metin_kapisi": {"wer": 0.0, "ad_dogru": True, "tasidigi_degisen_kelime": [], "konusan_yuz": "mara",
                                   "hiz_kelime_sn": 2.8, "sonuc": "GEC"}, "merdiven": []},
        "R0002": {"karakter": "voss", "kaynak_plan": 5, "yol_plan": "veo_donustur", "yol_gercek": "veo_donustur", "teslim": "normal",
                  "senaryo_metin": r2["metin"], "duyulan_metin": r2["metin"], "kelimeler": _kelimeler(r2["metin"], 1.5, 3.5),
                  "klip_zamani": {"bas": 1.5, "bit": 3.5},
                  "metin_kapisi": {"wer": 0.0, "ad_dogru": True, "tasidigi_degisen_kelime": [], "konusan_yuz": "voss",
                                   "hiz_kelime_sn": 2.0, "sonuc": "GEC"}, "merdiven": []}}}
    ko.diyalog_yaz(kok, d)
    rng = np.random.default_rng(7)
    ko.wav_yaz(os.path.join(kok, yatak), 0.02 * rng.standard_normal(48000 * 12).astype(np.float32))
    t = np.arange(48000 * 20) / 48000.0
    muz = sum(np.sin(2 * np.pi * f * t) for f in (146.8, 174.6, 220.0)) * 0.08
    ko.wav_yaz(os.path.join(kok, "MUZIK", "secilen", "M01.wav"), muz.astype(np.float32))
    ortak.atomik_yaz(os.path.join(kok, "MUZIK", "muzik_listesi.json"), {"film": ad, "ipuclari": [
        {"id": "M01", "tur": "tema", "bpm": 60, "olcu": "4/4",
         "giris": {"olay": "plan_basi", "plan": 3, "ofset_sn": 0.0, "rampa_sn": 2.0},
         "cikis": {"olay": "sahne_sonu", "sahne_grubu": "S02", "rampa_sn": 2.0, "tasma_sn": 1.0},
         "secilen": "MUZIK/secilen/M01.wav", "saglayici": "midi_ornek"}]})
    if klipler: klipleri_kur(kok)
    return kok


def klipleri_kur(kok):
    tanim = {1: dict(kutu=[(1.25, 3.0), (3.6, 5.2)], ton=[(1.3, 1.5), (3.7, 3.9)]),
             2: dict(kutu=[(1.0, 1.6)]), 3: dict(ton=[(2.0, 4.5)], kutu=[(2.0, 2.3)]), 4: dict(kutu=[(1.0, 1.4)]),
             5: dict(ton=[(1.5, 3.5)], kutu=[(1.5, 1.8)], ton_hz=150.0)}
    for no, k in tanim.items():
        anahtar = json.dumps(k, sort_keys=True)
        if anahtar not in _ONBELLEK:
            p = os.path.join(os.path.dirname(ortak.yollar()["filmler"]), "_KLIP_ONBELLEK", f"{len(_ONBELLEK)}.mp4")
            _ONBELLEK[anahtar] = ko.sahte_klip(p, 8.0, **k)
        shutil.copyfile(_ONBELLEK[anahtar], os.path.join(kok, "SIRALI_VIDEO", f"{no:03d}.mp4"))
