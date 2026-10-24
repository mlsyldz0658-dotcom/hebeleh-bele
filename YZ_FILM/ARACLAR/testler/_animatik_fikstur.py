"""test_kurgu_animatik için küçük sentetik film (SAHNELER v2 + HIKAYE + TTS + G1 görselleri). Ağ ve kredi yok."""
import os, json, wave


KAR = {"mara": {"ad": "Mara", "maske": {"etiket_anonim_en": "woman in a green cloak", "takma_adlar": ["huntress"]},
                "sir": "SIZINTI_SIR yavruyu saklıyor"},
       "voss": {"ad": "Voss", "maske": {"etiket_anonim_en": "man with a scarred jaw", "takma_adlar": ["Captain"]}}}


def _plan(no, sg, parti, tip, sure, replik=None, kadraj=None, adimlar=None, etki=None, hareket="sabit", **ek):
    z = {"kod": "%s-P%02d" % (sg, no), "sahne_grubu": sg, "plan_tipi": tip, "klip_sn": 8,
         "kamera": {"kurulum": "KAM1", "kadraj": "OY", "aci": "goz_hizasi", "hareket_tipi": hareket},
         "kadrajdakiler": [{"id": k, "olcek": "OY", "konusur": bool(replik and replik[1] == k)} for k in (kadraj or [])],
         "eylem_zinciri": adimlar or [{"id": "a1", "bas": 0.6, "bit": 2.0, "ozne": (kadraj or ["mara"])[0], "tur": "mikro",
                                       "fiil": "bakar", "govde": "bas", "etki": etki or {}}],
         "kesme": {"tip": "duz"}, "ekranda_bilgi": "SIZINTI_EKRANDA_%d bilgisi" % no, "ses": {"flow_sound": "Sound: wind. No music."}}
    p = {"no": no, "sira": no, "parti": parti, "amac": "SIZINTI_AMAC_%d" % no, "duygu": "gerilim", "kullanim": {"bas": 0.5, "sure": sure},
         "zanaat": z, "_derlenir": {"sure_sn": sure, "ayna_yasak": no != 3},
         "uretim": {"durum_dondu": {"bas": "d%d" % no, "bit": ("e%d" % no) if etki else "d%d" % no}}}
    if replik:
        rid, kim, metin, bas, bit = replik
        p["replik"] = {"id": rid, "karakter": kim, "metin": metin}
        p["_derlenir"]["replik_zaman"] = {rid: [bas, bit]}
        z["eylem_zinciri"] = z["eylem_zinciri"] + [{"id": "a2", "bas": bas, "bit": bit, "ozne": kim, "tur": "konusma", "fiil": "konusur",
                                                     "replik": rid}]
    p.update(ek)
    return p


def kur(kok, gorsel=(1, 2, 3, 4, 5, 6), tts=True, bitis=(2,), uzun=False):
    os.makedirs(kok, exist_ok=True)
    planlar = [
        _plan(1, "S01", 1, "kurulus", 3.0, kadraj=["mara"], hareket="yavas_ileri"),
        _plan(2, "S01", 1, "diyalog", 3.0, replik=("R0001", "mara", "Easy now, little one.", 1.0, 3.0), kadraj=["mara"], etki={"x": 1}),
        _plan(3, "S01", 1, "tepki", 2.0, kadraj=["voss"]),
        _plan(4, "S02", 2, "diyalog", 3.0, replik=("R0002", "voss", "Mara! Open the door.", 0.8, 2.5), kadraj=["voss"]),
        _plan(5, "S02", 2, "tepki", 2.5, kadraj=["mara"], hareket="yavas_pan"),
        _plan(6, "S02", 2, "eylem", 3.0, kadraj=["mara", "voss"], hareket="yavas_geri"),
    ]
    if uzun:                                   # bölüm/parça testi için: 120 sn'yi aşan süreler (render edilmez)
        for p in planlar: p["kullanim"]["sure"] = p["_derlenir"]["sure_sn"] = 60.0
    sah = {"_surum": 2, "film": "TEST_ANIMATIK", "karakterler": {"mara": {"tarif": "woman in a green cloak"},
                                                                 "voss": {"tarif": "man with a scarred jaw"}}, "sahneler": planlar}
    h = {"_surum": "v2", "baslik": {"secilen": "The Hidden Hatchling"}, "karakterler": KAR,
         "anahtar_olgular": [{"id": "o01", "olgu": "SIZINTI_OLGU Mara yavruyu saklıyor", "kritik": True, "hikaye_partisi": "P1"}],
         "KURULUMLAR": [{"id": "kur1", "ne": "SIZINTI_KURULUM kemik düdük", "plan": 3, "kullanim_plan": 6}],
         "replikler": [{"id": "R0001", "karakter": "mara", "metin": "Easy now, little one."},
                       {"id": "R0002", "karakter": "voss", "metin": "Mara! Open the door.", "ad_soyler": ["mara"]}],
         "vaat_sozlesmesi": [{"oge": "kapak_imgesi", "ekranda": "Mara holds a glowing cloak"}]}
    with open(os.path.join(kok, "SAHNELER.json"), "w", encoding="utf-8") as f: json.dump(sah, f, ensure_ascii=False)
    with open(os.path.join(kok, "HIKAYE.json"), "w", encoding="utf-8") as f: json.dump(h, f, ensure_ascii=False)
    from PIL import Image
    os.makedirs(os.path.join(kok, "SIRALI_GORSEL"), exist_ok=True)
    for n in gorsel:
        Image.new("RGB", (320, 180), ((n * 50) % 255, 90, 140)).save(os.path.join(kok, "SIRALI_GORSEL", "%03d.jpg" % n))
    for n in bitis:
        Image.new("RGB", (320, 180), (200, 200, 40)).save(os.path.join(kok, "SIRALI_GORSEL", "%03d_bitis.jpg" % n))
    if tts:
        os.makedirs(os.path.join(kok, "SESLER", "tts"), exist_ok=True)
        rep = {}
        for rid, kim, sure in (("R0001", "mara", 3.1), ("R0002", "voss", 1.2)):
            yol = "SESLER/tts/%s.wav" % rid
            with wave.open(os.path.join(kok, yol), "wb") as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000); w.writeframes(b"\x00\x00" * int(16000 * sure))
            rep[rid] = {"karakter": kim, "tts": {"dosya": yol, "sure_sn": sure}}
        with open(os.path.join(kok, "SESLER", "diyalog.json"), "w", encoding="utf-8") as f: json.dump({"surum": 2, "replikler": rep}, f)
    return kok
