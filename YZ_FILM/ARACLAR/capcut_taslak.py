"""CAPCUT TASLAK — CapCut taslağının sürümden bağımsız modeli, yazıcıları ve salt okunur okuyucusu (TASARIM §6.7, D-30; [KU2] KR10–KR12).

Kodda:
  import capcut_taslak as ct
  m = ct.model_kur(kok, kp, ad, yayin=False, klip_klasoru=None)   KURGU_PLANI + SES_CIZELGESI + diyalog.json → {ad, fps, sure_us, kanallar}
  ct.yaz(m, taslak_kok, sahte=True)     sahte: CapCut biçiminde draft_content.json + draft_meta_info.json (fikstür; bulut ve testler)
                                        gerçek: pycapcut (kullanici_araci; lisansı P0'da doğrulanır, D-36) — kaydettikten sonra okunup
                                        segment kimlikleri modele eşlenir
  ct.oku(klasor) → {"sifreli": bool, "icerik": dict|None, "yol": ...}   SALT OKUNUR (dosya "rb" ile açılır; hiçbir şey yazılmaz)
  ct.segmentler(icerik) → [{kanal, tur, segment_id, material_id, yol, bas, sure, kaynak_bas, kaynak_sure, ses, metin}]  (saniye)
Kanallar: Klipler (sessiz; source_timerange = kullanim) · Bantlar · Kartlar (başlık `baslik`'tan bölünmeden) · Altyazi (duyulan_metin) ·
Diyalog (replik replik) · Efekt · Ambiyans · Muzik (stem dilimleri: kısma ve rampalar dahil) · NOTLAR. --yayin: NOTLAR ve Altyazi yok.
Geçici akor yalnız müzik yoksa ve adı GECICI. Ses 48 kHz. Kimlikler belirlenimci (uuid5: taslak adı + kanal + anahtar).
"""
import os, sys, json, uuid, glob, shutil
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

US = 1_000_000
W, H, BANT = 1920, 1080, 96
BIZIM_KANALLAR = ("Diyalog", "Efekt", "Ambiyans", "Muzik", "Altyazi", "Kartlar", "NOTLAR")
SES_KANALLARI = ("Diyalog", "Efekt", "Ambiyans", "Muzik")


def us(x): return int(round(float(x) * US))
def sn(x): return round(float(x) / US, 4)


def kimlik(ad, kanal, anahtar): return str(uuid.uuid5(uuid.NAMESPACE_URL, f"yzfilm:{ad}:{kanal}:{anahtar}")).upper()


def _png(yol, bant=True):
    from PIL import Image, ImageDraw
    os.makedirs(os.path.dirname(yol), exist_ok=True)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0 if bant else 255)); d = ImageDraw.Draw(im)
    if bant: d.rectangle((0, 0, W, BANT), fill=(0, 0, 0, 255)); d.rectangle((0, H - BANT, W, H), fill=(0, 0, 0, 255))
    im.save(yol); return yol


def cumleler(metin):
    out, cur = [], ""
    for ch in metin or "":
        cur += ch
        if ch in ".?!": out.append(cur.strip()); cur = ""
    if cur.strip(): out.append(cur.strip())
    return out


def altyazi_satirlari(kok, kp, dj, pl, dil="en"):
    """[(bas, bit, metin)] — altyazı her zaman duyulan_metin'den; kelime zamanı varsa cümle sınırları ondan."""
    out = []
    for d in kp.get("diyalog") or []:
        r = (dj.get("replikler") or {}).get(d["replik"]) or {}
        metin = r.get("duyulan_metin") or r.get("senaryo_metin") or ""
        if dil != "en":
            p = pl.get(r.get("kaynak_plan"), {}); cs = [c.get(dil) for c in (p.get("replik") or {}).get("cumleler") or [] if c.get(dil)]
            if not cs: continue
        else: cs = cumleler(metin)
        if not cs: continue
        top = sum(len(c.split()) for c in cs) or 1; t = float(d["cizelge_bas"]); sure = float(d["sure"])
        for c in cs:
            dd = sure * len(c.split()) / top
            out.append((round(t, 3), round(t + dd + 0.3, 3), c)); t += dd
    out.sort()
    for i in range(len(out) - 1):                              # bindirme yok
        if out[i][1] > out[i + 1][0]: out[i] = (out[i][0], out[i + 1][0], out[i][2])
    return out


def srt_yaz(yol, satirlar):
    with open(yol, "w", encoding="utf-8") as f:
        for i, (a, b, t) in enumerate(satirlar, 1): f.write(f"{i}\n{ko.srt_zaman(a)} --> {ko.srt_zaman(b)}\n{t}\n\n")
    return yol


def _seg(ad, kanal, anahtar, yol, bas, sure, kaynak_bas=None, kaynak_sure=None, ses=1.0, metin=None, **ek):
    s = {"segment_id": kimlik(ad, kanal, anahtar), "kanal": kanal, "yol": yol, "bas": round(bas, 4), "sure": round(sure, 4),
         "kaynak_bas": None if kaynak_bas is None else round(kaynak_bas, 4), "kaynak_sure": None if kaynak_sure is None else round(kaynak_sure, 4),
         "ses": ses, "metin": metin}
    s.update(ek); return s


def model_kur(kok, kp, ad, yayin=False, klip_klasoru=None):
    dj = ko.diyalog_oku(kok); sc = ko.ses_cizelgesi(kok); s = ko.sahneler(kok); pl = ko.sahne_planlari(kok, s)
    top = ko.toplam_sure(kp); K = os.path.join(kok, "KURGU"); vk = klip_klasoru or os.path.join(K, "surumler", f"v{kp.get('kurgu_surumu', 1)}")
    siyah = os.path.join(vk, "siyah.png"); bant = os.path.join(vk, "sinema_bantlari.png")
    if not os.path.exists(siyah): _png(siyah, bant=False)
    if not os.path.exists(bant): _png(bant)
    kan = {k: [] for k in ("Klipler", "Bantlar", "Kartlar", "Altyazi", "Diyalog", "Efekt", "Ambiyans", "Muzik", "NOTLAR")}
    for x in kp.get("planlar") or []:
        g = x["goruntu"]; u = g["kullanim"]
        kaynak = os.path.join(vk, "klipler", f"{int(x['plan']):03d}.mp4") if g.get("tur") == "video" else None
        if g.get("tur") == "video" and not os.path.exists(kaynak): kaynak = ko.mutlak(kok, g["dosya"])
        if g.get("tur") == "yer_tutucu" and g.get("dosya"): kaynak = ko.mutlak(kok, g["dosya"])
        if not kaynak: kaynak = siyah
        foto = not kaynak.endswith(".mp4")
        kan["Klipler"].append(_seg(ad, "Klipler", x["plan"], kaynak, x["cizelge_bas"], x["sure"], None if foto else u["bas"],
                                   None if foto else u["sure"], ses=0.0, plan=x["plan"], sira=x.get("sira"), hiz=g.get("hiz", 1.0)))
        p = pl.get(x["plan"], {})
        if not yayin:
            not_ = f"#{x['plan']}" + (f" · {p['amac']}" if p.get("amac") else "") + (f" · Duygu: {p['duygu']}" if p.get("duygu") else "")
            y = ((p.get("_derlenir") or {}).get("hikaye") or {}).get("yogunluk") or ko.zanaat(p).get("yogunluk")
            if y is not None: not_ += f" · Hedef yoğunluk: {y}"
            kan["NOTLAR"].append(_seg(ad, "NOTLAR", x["plan"], None, x["cizelge_bas"], x["sure"], metin=not_, plan=x["plan"]))
    kan["Bantlar"].append(_seg(ad, "Bantlar", "bant", bant, 0.0, top))
    baslik = s.get("baslik") or s.get("film") or os.path.basename(kok)
    kan["Kartlar"].append(_seg(ad, "Kartlar", "baslik", None, min(2.0, max(0.0, top - 3.0)), min(5.0, top), metin=baslik, kart="baslik"))
    for i, k in enumerate(kp.get("kartlar") or []):
        kan["Kartlar"].append(_seg(ad, "Kartlar", f"kart{i}", None, float(k["cizelge_bas"]), float(k.get("sure") or 3.0), metin=k.get("metin"),
                                   kart=k.get("tur")))
    if not yayin:
        for i, (a, b, t) in enumerate(altyazi_satirlari(kok, kp, dj, pl)):
            kan["Altyazi"].append(_seg(ad, "Altyazi", i, None, a, b - a, metin=t))
    for d in kp.get("diyalog") or []:
        r = (dj.get("replikler") or {}).get(d["replik"]) or {}; p = ko.replik_dosyasi(kok, r)
        if not p: continue
        ofs = float(r.get("dosya_ofset_sn") or 0.0) if r.get("yol_gercek", r.get("yol_plan")) != "tts" else 0.0
        uz = ko.sure(p) or float(d["sure"])
        kan["Diyalog"].append(_seg(ad, "Diyalog", d["replik"], p, max(0.0, float(d["cizelge_bas"]) - ofs), uz, 0.0, uz, ses=1.0,
                                   replik=d["replik"], plan=d["plan"]))
    def dilim(kanal, stem_ad, ogeler, anahtar):
        sp = ko.stem_yolu(kok, stem_ad)
        if not os.path.exists(sp): return
        for e in ogeler:
            a = max(0.0, float(e["cizelge_bas"])); b = min(top, a + float(e.get("sure") or 0.6))
            if b - a > ko.KARE: kan[kanal].append(_seg(ad, kanal, e.get(anahtar), sp, a, b - a, a, b - a, ses=1.0, **{anahtar: e.get(anahtar)}))
    dilim("Ambiyans", "ambiyans", sc.get("ambiyans") or [], "sahne_grubu")
    dilim("Efekt", "efekt", [dict(e, sure=0.6) for e in sc.get("efektler") or []], "id")
    dilim("Muzik", "muzik", sc.get("muzik") or [], "ipucu")
    if not kan["Muzik"]:                                            # geçici akor yalnız müzik yoksa ve adı GECICI
        gp = os.path.join(vk, "GECICI_muzik.wav")
        if not os.path.exists(gp):
            t = np.arange(int(top * ko.SR)) / ko.SR
            ko.wav_yaz(gp, (sum(np.sin(2 * np.pi * f * t) for f in (146.8, 174.6, 220.0)) * 0.03).astype(np.float32))
        kan["Muzik"].append(_seg(ad, "Muzik", "GECICI", gp, 0.0, top, 0.0, top, ses=0.45, gecici=True))
    if yayin: kan.pop("NOTLAR"); kan.pop("Altyazi")
    return {"ad": ad, "fps": ko.FPS, "sure_us": us(top), "sure": top, "kanallar": kan, "yayin": yayin,
            "kurgu_plani_surumu": kp.get("kurgu_surumu"), "kurgu_plani_imza": ko.plan_imza(kp)}


# --- yazıcılar ----------------------------------------------------------------------------------------------------
TUR = {"Klipler": "video", "Bantlar": "video", "Kartlar": "text", "Altyazi": "text", "NOTLAR": "text",
       "Diyalog": "audio", "Efekt": "audio", "Ambiyans": "audio", "Muzik": "audio"}


def icerik_kur(m):
    """Modelden CapCut biçimli draft_content sözlüğü (sahte yazıcı ve yama yeniden yerleşimi için)."""
    mat = {"videos": [], "audios": [], "texts": []}; tracks = []
    for kanal, segs in m["kanallar"].items():
        t = TUR[kanal]; trk = {"id": kimlik(m["ad"], "track", kanal), "type": t, "name": kanal, "attribute": 0, "segments": []}
        for s_ in segs:
            mid = kimlik(m["ad"], "mat", s_["segment_id"])
            if t == "text": mat["texts"].append({"id": mid, "type": "text", "content": json.dumps({"text": s_["metin"] or ""}, ensure_ascii=False)})
            elif t == "video": mat["videos"].append({"id": mid, "type": "photo" if not str(s_["yol"]).endswith(".mp4") else "video",
                                                     "path": s_["yol"], "duration": us(s_.get("kaynak_sure") or s_["sure"])})
            else: mat["audios"].append({"id": mid, "type": "extract_music", "path": s_["yol"], "name": os.path.basename(s_["yol"]),
                                        "duration": us(s_.get("kaynak_sure") or s_["sure"])})
            seg = {"id": s_["segment_id"], "material_id": mid, "target_timerange": {"start": us(s_["bas"]), "duration": us(s_["sure"])},
                   "source_timerange": None if s_.get("kaynak_bas") is None else {"start": us(s_["kaynak_bas"]), "duration": us(s_["kaynak_sure"])},
                   "volume": s_.get("ses", 1.0), "speed": s_.get("hiz") or 1.0}
            trk["segments"].append(seg)
        tracks.append(trk)
    return {"id": kimlik(m["ad"], "draft", "icerik"), "fps": float(m["fps"]), "duration": m["sure_us"],
            "canvas_config": {"width": W, "height": H}, "config": {"maintrack_adsorb": False, "sample_rate": ko.SR},
            "materials": mat, "tracks": tracks}


def yaz(m, taslak_kok, sahte=True):
    """Taslağı yeni klasöre yazar (var olan taslağa dokunmaz; ad çakışırsa ' (2)' eklenir). (klasör, içerik)."""
    ad = m["ad"]; k = 2
    while os.path.exists(os.path.join(taslak_kok, ad)): ad = f"{m['ad']} ({k})"; k += 1
    if ad != m["ad"]:
        m = dict(m, ad=ad)
    klasor = os.path.join(taslak_kok, ad)
    if sahte:
        os.makedirs(klasor); ic = icerik_kur(m)
        ortak.atomik_yaz(os.path.join(klasor, "draft_content.json"), ic)
        ortak.atomik_yaz(os.path.join(klasor, "draft_meta_info.json"), {"draft_id": kimlik(ad, "draft", "meta"), "draft_name": ad,
                                                                       "draft_fold_path": klasor, "tm_duration": m["sure_us"]})
        return klasor, ic
    return _yaz_pycapcut(m, taslak_kok, ad)


def _yaz_pycapcut(m, taslak_kok, ad):
    sys.path.insert(0, os.path.join(HERE, "kurgu_koprusu"))
    import pycapcut as cc
    from kurgu_koprusu import load_video, load_audio, complete_metadata
    sc = cc.DraftFolder(str(taslak_kok)).create_draft(ad, W, H, fps=m["fps"], allow_replace=False)
    for kanal, segs in m["kanallar"].items():
        t = TUR[kanal]; tt = {"video": cc.TrackType.video, "audio": cc.TrackType.audio, "text": cc.TrackType.text}[t]
        sc.add_track(tt, kanal) if kanal != "Bantlar" else sc.add_track(tt, kanal, relative_index=2)
        for s_ in segs:
            tr = cc.Timerange(us(s_["bas"]), us(s_["sure"]))
            if t == "text":
                sc.add_segment(cc.TextSegment(s_["metin"] or "", tr, style=cc.TextStyle(size=6.5 if kanal == "Altyazi" else 4.2, align=1,
                               auto_wrapping=True), clip_settings=cc.ClipSettings(transform_y=-0.78 if kanal == "Altyazi" else 0.8)), kanal)
                continue
            mat = load_video(cc, s_["yol"]) if t == "video" else load_audio(cc, s_["yol"])
            src = None if s_.get("kaynak_bas") is None else cc.Timerange(us(s_["kaynak_bas"]), min(us(s_["kaynak_sure"]), mat.duration))
            if t == "video": sc.add_segment(cc.VideoSegment(mat, tr, source_timerange=src, volume=s_.get("ses", 0.0)), kanal)
            else: sc.add_segment(cc.AudioSegment(mat, tr, source_timerange=src, volume=s_.get("ses", 1.0)), kanal)
    sc.content.setdefault("config", {})["maintrack_adsorb"] = False
    sc.save()
    klasor = os.path.join(taslak_kok, ad); complete_metadata(klasor, ad, m["sure_us"])
    o = oku(klasor)
    if o["sifreli"] or not o["icerik"]: raise RuntimeError("yazılan taslak okunamadı (şifreli?)")
    gercek = segmentler(o["icerik"]); idx = {(g["kanal"], us(g["bas"])): g["segment_id"] for g in gercek}
    for kanal, segs in m["kanallar"].items():
        for s_ in segs: s_["segment_id"] = idx.get((kanal, us(s_["bas"])), s_["segment_id"])
    return klasor, o["icerik"]


# --- salt okunur okuyucu --------------------------------------------------------------------------------------------
def icerik_yolu(klasor):
    """draft_content.json; yeni CapCut sürümlerinde Timelines/<id>/draft_content.json daha yeniyse o."""
    ana = os.path.join(klasor, "draft_content.json"); adaylar = glob.glob(os.path.join(klasor, "Timelines", "*", "draft_content.json"))
    adaylar = [p for p in adaylar if os.path.isfile(p)]
    if adaylar and (not os.path.exists(ana) or max(os.path.getmtime(p) for p in adaylar) > os.path.getmtime(ana)):
        return max(adaylar, key=os.path.getmtime)
    return ana


def oku(klasor):
    yol = icerik_yolu(klasor)
    try:
        with open(yol, "rb") as f: ham = f.read()
    except OSError: return {"sifreli": False, "icerik": None, "yol": yol, "hata": "taslak yok"}
    if not ham.lstrip().startswith(b"{"): return {"sifreli": True, "icerik": None, "yol": yol}
    try: return {"sifreli": False, "icerik": json.loads(ham.decode("utf-8")), "yol": yol}
    except ValueError: return {"sifreli": False, "icerik": None, "yol": yol, "hata": "JSON bozuk"}


def metin_al(mat):
    try: return json.loads(mat.get("content") or "{}").get("text", "")
    except (ValueError, AttributeError): return mat.get("content", "") if isinstance(mat, dict) else ""


def segmentler(ic):
    mats = {}
    for tur, liste in (ic.get("materials") or {}).items():
        for m_ in liste or []:
            if isinstance(m_, dict) and m_.get("id"): mats[m_["id"]] = (tur, m_)
    out = []
    for t in ic.get("tracks") or []:
        for s_ in t.get("segments") or []:
            tur, m_ = mats.get(s_.get("material_id"), (None, {}))
            tr = s_.get("target_timerange") or {}; sr_ = s_.get("source_timerange") or None
            out.append({"kanal": t.get("name") or "", "tur": t.get("type"), "segment_id": s_.get("id"), "material_id": s_.get("material_id"),
                        "yol": m_.get("path"), "bas": sn(tr.get("start", 0)), "sure": sn(tr.get("duration", 0)),
                        "kaynak_bas": None if not sr_ else sn(sr_.get("start", 0)), "kaynak_sure": None if not sr_ else sn(sr_.get("duration", 0)),
                        "ses": s_.get("volume"), "metin": metin_al(m_) if tur == "texts" else None, "malzeme_turu": tur,
                        "ekler": [k for k in ("extra_material_refs",) if s_.get(k)]})
    return out


def model_segmentleri(m):
    return [dict(s_, kanal=k) for k, ss in m["kanallar"].items() for s_ in ss]
