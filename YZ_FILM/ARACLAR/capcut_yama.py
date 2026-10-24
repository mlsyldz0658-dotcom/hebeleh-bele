"""CAPCUT YAMA — kullanıcının düzenlediği taslağı KLONLAR, klonda yalnız bizim kanallarımızı yeni plana göre yamar (TASARIM §6.7, D-30;
[KU2] KR11, §4.5.7 karar ağacı, §4.6.2). Yalnız Ö0-d olumluysa açıktır (bayrak); değilse yedek yol: kullanıcının kararlarıyla yeni adla kur.

Kullanım:
  python capcut_yama.py --film <film> [--saglayici sahte]       → klon "<kullanıcının proje adı> · v<N+1>" + _RAPOR/YAMA_v<N>.json (kapı NOT)
Bayrak (biri yeter): <veri>/BILGI/OLCUM0/O0d.json {"klon": "calisiyor"} (Ö0-d ölçümü) · FILM_AYAR.json "capcut_yama": true.
Karar ağacı:
  1. Fark yok → capcut_film ile yeni sürüm (v<N+1>); eski taslak ve klasörü bozulmaz.
  2. Fark var, taslak okunur, bayrak açık → kullanıcının kararları KURGU_PLANI'na kilitli işlenir (taslak_fark --plana-isle) → taslak klonlanır
     (KAYNAK HİÇ YAZILMAZ; kaynak özeti önce = sonra) → klonda yalnız Diyalog, Efekt, Ambiyans, Muzik, Altyazi, Kartlar, NOTLAR yeniden
     yerleşir; Klipler kanalına ve kullanıcı öğelerine dokunulmaz; yeniden çekilen klip yeni dosya adıyla bağlanır (NNN_t<k>.mp4);
     kullanıcının kanal ses ayarı korunur → öz denetim (Klipler özeti kaynakla aynı, kullanıcı öğeleri aynı, bizim kanallar ±1 kare,
     boşluk 0, eksik medya 0).
  3. Yama doğrulanamazsa ya da bayrak kapalıysa → klon (varsa) silinmez, <film>/_ESKI/'ye taşınır; kullanıcının kararlarıyla
     "YZ <FILM> v<N+1> (senin düzenlemenle)" kurulur; taşınamayan öğeler (renk ayarı, kendi yazısı) tek cümleyle söylenir.
  4. Taslak şifreliyse → yama yok; yedek yol tek cümleyle (taslak_fark).
Çıkış kodları: 0 tamam (yama ya da yedek yol) · 1 HATA · 2 taslak/proje yok ya da şifreli · 4 ortam.
"""
import os, sys, json, shutil, uuid
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import ortak, kurgu_ortak as ko, capcut_taslak as ct, taslak_fark as tf

SURUM = "capcut_yama 1.0"
TOL = ko.KARE + 1e-3


def bayrak_acik():
    if ko.film_ayar().get("capcut_yama") is True: return True, "FILM_AYAR capcut_yama"
    try: o = ortak.json_oku(os.path.join(ortak.yollar()["veri_kok"], "BILGI", "OLCUM0", "O0d.json"), {}) or {}
    except ortak.YolYok: o = {}
    k = o.get("klon")
    return (k in (True, "calisiyor"), f"O0d klon: {k}") if k is not None else (False, "Ö0-d ölçülmedi")


def klipler_ozeti(ic, haric=()):
    return sorted((os.path.basename(s["yol"] or ""), round(s["bas"], 3), round(s["sure"], 3), s["kaynak_bas"], s["kaynak_sure"])
                  for s in ct.segmentler(ic) if s["kanal"] == "Klipler" and s["segment_id"] not in haric)


def kullanici_ogeleri(ic, bizim_id, yazilar):
    return sorted((s["kanal"], s["segment_id"], s.get("metin")) for s in ct.segmentler(ic)
                  if s["segment_id"] not in bizim_id and (s["kanal"] not in ("Klipler",)) and not (s.get("metin") in yazilar and s["kanal"] in ct.BIZIM_KANALLAR))


def klonla(kaynak, hedef):
    shutil.copytree(kaynak, hedef)
    ad = os.path.basename(hedef); mp = os.path.join(hedef, "draft_meta_info.json"); meta = ortak.json_oku(mp, {}) or {}
    meta.update(draft_id=str(uuid.uuid4()).upper(), draft_name=ad, draft_fold_path=hedef); ortak.atomik_yaz(mp, meta)
    yol = ct.icerik_yolu(hedef); ic = ortak.json_oku(yol); ic["id"] = str(uuid.uuid4()).upper(); ortak.atomik_yaz(yol, ic)
    return yol, ic


def yamala(kok, ic, kp, ad, fk, vk):
    """Klon içeriğinde bizim kanallarımızı yeniden yerleştirir; Klipler'de yalnız yeniden çekilen klibin dosyası yeni adla bağlanır."""
    m = ct.model_kur(kok, kp, ad, yayin=False, klip_klasoru=vk); yeni = ct.icerik_kur(m)
    proje = tf.proje_oku(kok) or {}; bizim_id = {s["segment_id"] for s in proje.get("segmentler") or []}
    ses_ayar = {}
    for k in fk.get("kullanici_ses_duzenlemesi") or []:
        if k["kanal"] != "Klipler": ses_ayar[k["kanal"]] = k.get("ses")
    yeni_mat = {x["id"]: (tur, x) for tur, xs in yeni["materials"].items() for x in xs}
    ic.setdefault("materials", {})
    degisen = 0
    for kanal in ct.BIZIM_KANALLAR:
        trk = next((t for t in ic.get("tracks") or [] if t.get("name") == kanal), None)
        ytrk = next((t for t in yeni["tracks"] if t["name"] == kanal), None)
        if ytrk is None: continue
        if trk is None: trk = {"id": ytrk["id"], "type": ytrk["type"], "name": kanal, "attribute": 0, "segments": []}; ic["tracks"].append(trk)
        kalan = [s for s in trk["segments"] if s.get("id") not in bizim_id]          # kullanıcının bu kanala koyduğu öğe kalır
        degisen += len(trk["segments"]) - len(kalan)
        for s in ytrk["segments"]:
            s = dict(s)
            if kanal in ses_ayar and ses_ayar[kanal] is not None: s["volume"] = ses_ayar[kanal]
            tur, mat = yeni_mat[s["material_id"]]; ic["materials"].setdefault(tur, []).append(mat); kalan.append(s); degisen += 1
        trk["segments"] = kalan
    yeniden = []
    sid = {s.get("plan"): s["segment_id"] for s in proje.get("segmentler") or [] if s["kanal"] == "Klipler"}
    mats = {x["id"]: x for x in ic["materials"].get("videos") or []}
    for x in kp.get("planlar") or []:
        if not x["goruntu"].get("yeniden_cekildi") or x["goruntu"].get("tur") != "video": continue
        seg = next((s for t in ic["tracks"] if t.get("name") == "Klipler" for s in t["segments"] if s.get("id") == sid.get(x["plan"])), None)
        if not seg: continue
        k = 2
        while os.path.exists(os.path.join(vk, "klipler", f"{int(x['plan']):03d}_t{k}.mp4")): k += 1
        hedef = os.path.join(vk, "klipler", f"{int(x['plan']):03d}_t{k}.mp4"); os.makedirs(os.path.dirname(hedef), exist_ok=True)
        shutil.copyfile(ko.mutlak(kok, x["goruntu"]["dosya"]), hedef)             # eski dosya ezilmez
        mats[seg["material_id"]]["path"] = hedef; yeniden.append(x["plan"])
    return ic, m, degisen, yeniden


def yedek_yol(kok, argv, neden, f=None):
    import capcut_film
    if f and f.get("fark_var"): tf.plana_isle(kok, f)
    k = capcut_film.v2(kok, list(argv) + ["--ad-ek", " (senin düzenlemenle)"])
    tasinamaz = [o["tur"] for o in (f or {}).get("kullanici_ogeleri") or [] if o["tur"] in ("renk_ayari", "yazi", "efekt")]
    print(f"Taslağını yamalayamadım ({neden}); kararlarınla yeni adla kurdum." +
          (f" Şunları elle taşıman gerekebilir: {', '.join(sorted(set(tasinamaz)))}." if tasinamaz else ""), flush=True)
    return k


def yama(kok, argv=()):
    argv = list(argv); proje = tf.proje_oku(kok)
    if not isinstance(proje, dict) or proje.get("_surum", 1) < 2: print("!! son_capcut_projesi.json v2 yok", flush=True); return 2, None
    o = ct.oku(proje["klasor"])
    if o["sifreli"]: print(tf.SIFRELI_BILGI, flush=True); return 2, None
    if not o["icerik"]: print(f"!! taslak okunamadı: {proje['klasor']}", flush=True); return 2, None
    f = tf.fark(kok, proje, o)
    if not f["fark_var"]:
        import capcut_film, plan_kurgu
        _, kp = ko.kurgu_plani(kok)
        if kp and kp.get("kurgu_surumu") == proje.get("kurgu_plani_surumu"):
            print("taslakta kullanıcı değişikliği yok; yeni sürüm kurgu planı değişince kurulur", flush=True); return 0, None
        return capcut_film.v2(kok, argv), None
    acik, neden = bayrak_acik()
    if not acik: return yedek_yol(kok, argv, f"CapCut klonu doğrulanmadı: {neden}", f), None
    ozet_once = ko.klasor_ozeti(proje["klasor"])
    yol = tf.plana_isle(kok, f); _, kp = ko.kurgu_plani(kok); n = int(kp.get("kurgu_surumu"))
    kaynak_ad = os.path.basename(os.path.normpath(proje["klasor"])); hedef = os.path.join(os.path.dirname(proje["klasor"]), f"{kaynak_ad} · v{n}")
    k = 2
    while os.path.exists(hedef): hedef = os.path.join(os.path.dirname(proje["klasor"]), f"{kaynak_ad} · v{n} ({k})"); k += 1
    vk = os.path.join(kok, "KURGU", "surumler", f"v{n}")
    icy, ic = klonla(proje["klasor"], hedef)
    ic, m, degisen, yeniden = yamala(kok, ic, kp, os.path.basename(hedef), f, vk)
    ortak.atomik_yaz(icy, ic)
    ozet_sonra = ko.klasor_ozeti(proje["klasor"])
    kaynak_ic = o["icerik"]; bizim_id = {s["segment_id"] for s in proje.get("segmentler") or []}
    yazilar = set(proje.get("benim_yazilarim") or [])
    yeniden_id = {s["segment_id"] for s in proje["segmentler"] if s["kanal"] == "Klipler" and s.get("plan") in yeniden}
    kesit = klipler_ozeti(kaynak_ic, yeniden_id) == klipler_ozeti(ic, yeniden_id)
    ko_esit = kullanici_ogeleri(kaynak_ic, bizim_id, yazilar) == kullanici_ogeleri(ic, bizim_id | {s["segment_id"] for s in ct.model_segmentleri(m)}, yazilar)
    ds = ct.segmentler(ic); ms = {s["segment_id"]: s for s in ct.model_segmentleri(m) if s["kanal"] in ct.BIZIM_KANALLAR}
    kanal_ok = all(any(d["segment_id"] == sid and abs(d["bas"] - s["bas"]) <= TOL for d in ds) for sid, s in ms.items())
    dk = sorted([d for d in ds if d["kanal"] == "Klipler"], key=lambda d: d["bas"])
    bosluk = [round(b["bas"] - a["bas"] - a["sure"], 3) for a, b in zip(dk, dk[1:]) if b["bas"] - a["bas"] - a["sure"] > TOL]
    eksik = sorted({d["yol"] for d in ds if d.get("yol") and not os.path.exists(d["yol"])})
    olc = [ko.m("kaynak_yazilmadi", "GEC" if ozet_once == ozet_sonra else "HATA", None, olcu=[ozet_once, ozet_sonra]),
           ko.m("klipler_ozet_esit", "GEC" if kesit else "HATA", None),
           ko.m("kullanici_ogeleri_esit", "GEC" if ko_esit else "HATA", None),
           ko.m("bizim_kanallar_plan", "GEC" if kanal_ok else "HATA", None, olcu=degisen),
           ko.m("bosluk", "GEC" if not bosluk else "HATA", None, olcu=bosluk), ko.m("eksik_medya", "GEC" if not eksik else "HATA", None, olcu=eksik)]
    sonuc_ok = all(x["seviye"] == "GEC" for x in olc)
    ek = {"kaynak": proje["klasor"], "kaynak_ozet_once": ozet_once, "kaynak_ozet_sonra": ozet_sonra, "klon": hedef, "klipler_ozet_esit": kesit,
          "kullanici_ogeleri_esit": ko_esit, "bizim_kanallar_degisen_segment": degisen, "bosluk": len(bosluk), "eksik_medya": len(eksik),
          "yeniden_baglanan": yeniden, "kurgu_plani": ko.goreli(kok, yol)}
    if not sonuc_ok:
        ek["klon_eski"] = ko.goreli(kok, ko.eskiye_tasi(kok, hedef))
    tur = ko.po.tur_no(argv)
    ry, r = ko.po.rapor_yaz(kok, "NOT", f"v{n}", olc, asama="A16n", arac=SURUM, ek=ek, varsayilan=os.path.join("_RAPOR", f"YAMA_v{n}.json"))
    ko.po.yaz_ozet(r, os.path.basename(ry))
    if not sonuc_ok: return yedek_yol(kok, argv, "öz denetim geçmedi", None), r
    segs = []
    for s in ct.segmentler(ic):
        e = {"kanal": s["kanal"], "segment_id": s["segment_id"], "bas": s["bas"], "sure": s["sure"]}
        ps = next((p for p in proje["segmentler"] if p["segment_id"] == s["segment_id"]), None) or ms.get(s["segment_id"]) or {}
        for a in ("plan", "sira", "replik"):
            if ps.get(a) is not None: e[a] = ps[a]
        if s.get("kaynak_bas") is not None: e["kaynak_aralik"] = {"bas": s["kaynak_bas"], "sure": s["kaynak_sure"]}
        if s.get("yol"): e["kaynak"] = ko.goreli(kok, s["yol"])
        if s.get("ses") is not None: e["ses"] = s["ses"]
        segs.append(e)
    yeni = dict(proje, proje=os.path.basename(hedef), klasor=hedef, kurgu_plani_surumu=n, kurgu_plani_imza=ko.plan_imza(kp), segmentler=segs,
                sure_sn=ko.toplam_sure(kp), klon_kaynagi=proje["klasor"], _uretim=ko.po.zarf("A16n", SURUM),
                benim_yazilarim=sorted(yazilar | {s["metin"] for s in ct.model_segmentleri(m) if s.get("metin")}))
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "son_capcut_projesi.json"), yeni)
    print(f"Taslağının kopyası hazır: \"{os.path.basename(hedef)}\" (senin düzenlemelerin korundu; kaynağa dokunulmadı).", flush=True)
    return 0, r


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    k, r = yama(kok, argv)
    return k


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
