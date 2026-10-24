"""DUDAK DENETİM — S3 dudak kapısı ve MuseTalk yolu (TASARIM §6.6, §2.2 B planı; [SM2] SE1, §4.7.4).

Kullanım:
  python dudak_denetim.py --film <film> [--saglayici sahte]          S3: kurgu planının her değişiminden sonra → _RAPOR/S3_v<N>.json
  python dudak_denetim.py --film <film> --musetalk [--saglayici sahte]
      SESLER/DUDAK_ISTEK.json'daki replikler için `tts_dudak` (MuseTalk 1.5; ayrı ortam KUR3): çıktı YENİ dosya
      SIRALI_VIDEO/NNN_dudak_<k>.mp4 (eski klip ezilmez); KUNYE/V2_YENIDEN.json'a yazılır (çıktı V2 kimlik + S3'ten yeniden geçer).
  Wav2Lip ve LatentSync kullanılmaz (kalite ve lisans; ADLAR saglayici_dislanan): --motor wav2lip → 4.
Ölçüler (eşikler [SM2] §4.7.4; tahmin olanlar kalibrasyonla ayarlanır):
  S3.1 ağız açıklığı ↔ ses zarfı ofseti: ≤ 42 ms GEÇ · 42–125 ms BAYRAK · > 125 ms HATA (24 fps kare çözünürlüğünde)
  S3.2 korelasyon güveni ≥ 0,3 (B) · S3.4 ağzı en çok oynayan yüz = replik karakteri (H)
  S3.5 ekran dışı ya da L/J taşmasında kadrajdaki yüzlerin ağız std'si ≤ 0,05 (H) · S3.7 planlanan ağız görünürlüğü ölçülebildi mi (B)
Ağız dizisi: olcum/dudak.py (MediaPipe jawOpen) kuruluysa ondan, --saglayici sahte ise sahte sağlayıcıdan; yoksa ÖLÇÜLEMEDİ (= BAYRAK).
Dizi KURGU/AGIZ_DIZISI.json'a yazılır (kurgu_denetim B9 aynı diziyi okur). S3.1 HATA'sı yerleşim hatasıdır:
KURGU/S3_ONERI_v<N>.json'a kurgu_uygula işlemi ({"op": "diyalog_kaydir", replik, sn}) yazılır.
Çıkış kodları: 0 S3 GEÇ/BAYRAK · 1 S3 HATA · 2 KURGU_PLANI yok · 4 ortam/motor yok ya da yasak motor.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "dudak_denetim 1.0"
OFSET_GEC_MS, OFSET_HATA_MS, GUVEN_MIN, AGIZ_STD_MAX = 42, 125, 0.3, 0.05
YASAK_MOTOR = ("wav2lip", "latentsync", "fal_latentsync")


def agiz_dizisi(kok, argv, x, pl):
    p = pl.get(x["plan"], {}); kim = [k.get("id") for k in ko.zanaat(p).get("kadrajdakiler") or [] if k.get("id")]
    klip = ko.mutlak(kok, x["goruntu"].get("dosya")) if x["goruntu"].get("dosya") else None
    if not klip or not os.path.exists(klip) or x["goruntu"].get("tur") != "video": return None
    if ko.saglayici_adi(argv):
        s, _ = ko.cagir("agiz", argv, kok, klip, x["plan"], kim)
        return s
    try:
        from olcum import dudak as od                     # adım 12 olcum paketi (MediaPipe); yoksa ölçülemedi
        return od.agiz_dizisi(klip, kim)
    except Exception: return None


def _seri(a, fps, t0, t1):
    i0, i1 = int(round(t0 * fps)), int(round(t1 * fps)); v = np.asarray(a, float)
    out = np.zeros(max(0, i1 - i0))
    for k in range(len(out)):
        j = i0 + k
        if 0 <= j < len(v): out[k] = v[j]
    return out


def konusma_zarfi(kok, d, r, x):
    """Diyaloğun ses zarfı (24 fps), diyalog başından. Duyulacak dosya (eşit/dönüşmüş/TTS) ya da Yol A'da klibin kendi sesi."""
    p = ko.replik_dosyasi(kok, r) if r else None
    if p:
        a, sr = ko.wav_oku(p)
        if (r.get("yol_gercek") or r.get("yol_plan")) != "tts": a = a[int(float(r.get("dosya_ofset_sn") or 0.0) * sr):]
    else:
        klip = ko.mutlak(kok, x["goruntu"].get("dosya")); kz = d.get("klip_zamani") or {}
        a = ko.video_sesi(klip) if klip else None; sr = ko.SR
        if a is None or kz.get("bas") is None: return None
        a = ko.pencere(a, sr, float(kz["bas"]), float(kz["bit"]))
    z = ko.zarf(a, sr, ko.FPS)
    return z / (z.max() or 1.0)


def denetle(kok, argv=()):
    argv = list(argv); kp_yol, kp = ko.kurgu_plani(kok)
    if not kp: return None, None
    pl = ko.sahne_planlari(kok); dj = ko.diyalog_oku(kok); olc, oneri, agiz = [], [], {}
    dz = {x["plan"]: x for x in kp.get("planlar") or []}
    for x in kp.get("planlar") or []:
        a = agiz_dizisi(kok, argv, x, pl)
        if a: agiz[str(x["plan"])] = a
    ortak.atomik_yaz(os.path.join(kok, "KURGU", "AGIZ_DIZISI.json"), dict(agiz, _uretim=ko.po.zarf("A16", SURUM)))
    for d in kp.get("diyalog") or []:
        x = dz.get(d.get("plan")); r = (dj.get("replikler") or {}).get(d.get("replik"))
        if not x: continue
        bas, bit = float(d["cizelge_bas"]), float(d["cizelge_bas"]) + float(d["sure"])
        if d.get("gorunen_konusan"):
            a = agiz.get(str(x["plan"])); p = pl.get(x["plan"], {})
            if not a:
                olc.append(ko.m("S3.1_ofset", "OLCULEMEDI", x["plan"], replik=d["replik"], neden="ağız dizisi yok"))
                if (p.get("_derlenir") or {}).get("agiz_gorunur") in ("tam", "kismi"):
                    olc.append(ko.m("S3.7_agiz_gorunurlugu", "BAYRAK", x["plan"], replik=d["replik"], neden="planda ağız görünür; ölçülemedi"))
                continue
            fps = float(a.get("fps") or ko.FPS); w0, w1 = max(bas, x["cizelge_bas"]), min(bit, ko.plan_sonu(x))
            if w1 - w0 < 0.3: continue
            yuzler = a.get("yuzler") or {}
            stds = {k: float(_seri(v, fps, ko.klip_zamanina(x, w0), ko.klip_zamanina(x, w1)).std()) for k, v in yuzler.items()}
            kim = d.get("karakter") or (r or {}).get("karakter")
            if stds:
                en = max(stds, key=stds.get)
                olc.append(ko.m("S3.4_konusan_yuz", "GEC" if en == kim else "HATA", x["plan"], replik=d["replik"], olcu=en, esik=kim,
                                kok_neden=None if en == kim else "yanlis_kisi_konustu"))
            agz = _seri(yuzler.get(kim) or [], fps, ko.klip_zamanina(x, w0), ko.klip_zamanina(x, w1))
            zf = konusma_zarfi(kok, d, r, x)
            if zf is None or not len(agz):
                olc.append(ko.m("S3.1_ofset", "OLCULEMEDI", x["plan"], replik=d["replik"], neden="ses ya da ağız serisi yok")); continue
            ses = _seri(zf, ko.FPS, w0 - bas, w1 - bas)
            lag, c = ko.ofset(agz, ses, max_kayma=6)
            if lag is None:
                olc.append(ko.m("S3.1_ofset", "OLCULEMEDI", x["plan"], replik=d["replik"], neden="düz seri")); continue
            ms = lag * 1000.0 / ko.FPS
            sv = "GEC" if abs(ms) <= OFSET_GEC_MS + 1 else ("BAYRAK" if abs(ms) <= OFSET_HATA_MS else "HATA")
            on = {"op": "diyalog_kaydir", "replik": d["replik"], "sn": round(-ms / 1000.0, 3)} if sv == "HATA" else None
            olc.append(ko.m("S3.1_ofset", sv, x["plan"], replik=d["replik"], olcu=round(ms, 1), esik=[OFSET_GEC_MS, OFSET_HATA_MS],
                            kok_neden="dudak_kayma" if sv != "GEC" else None, oneri=on))
            if on: oneri.append(dict(on, plan=x["plan"], kok_neden="dudak_kayma", bulgu="S3.1"))
            olc.append(ko.m("S3.2_guven", "GEC" if c >= GUVEN_MIN else "BAYRAK", x["plan"], replik=d["replik"], olcu=round(c, 3), esik=GUVEN_MIN))
        ust = list(((d.get("jl") or {}).get("uzerindeki_planlar")) or [])
        if d.get("ekran_disi"): ust.append(x["plan"])
        for un in ust:
            y = dz.get(un); a = agiz.get(str(un))
            if not y or (un != x["plan"] and y["goruntu"].get("kaynak_klip") == x["plan"]): continue
            w0, w1 = max(bas, y["cizelge_bas"]), min(bit, ko.plan_sonu(y))
            if w1 - w0 < ko.KARE: continue
            if not a: olc.append(ko.m("S3.5_ekran_disi_agiz", "OLCULEMEDI", un, replik=d["replik"])); continue
            fps = float(a.get("fps") or ko.FPS)
            en = max([float(_seri(v, fps, ko.klip_zamanina(y, w0), ko.klip_zamanina(y, w1)).std()) for v in (a.get("yuzler") or {}).values()]
                     or [0.0])
            olc.append(ko.m("S3.5_ekran_disi_agiz", "HATA" if en > AGIZ_STD_MAX else "GEC", un, replik=d["replik"], olcu=round(en, 3),
                            esik=AGIZ_STD_MAX, kok_neden="dinleyen_konustu" if en > AGIZ_STD_MAX else None,
                            oneri="kurgucu: başka kırpma penceresi ya da aynı sahnenin başka tepki planı" if en > AGIZ_STD_MAX else None))
    kapsam = ko.kapsam_surum(kp)
    if oneri:
        ortak.atomik_yaz(os.path.join(kok, "KURGU", f"S3_ONERI_{kapsam}.json"),
                         {"asama": "T2", "kip": "s3_yerlesim", "kaynak": "dudak_denetim", "islemler": oneri})
    return ko.rapor(kok, "S3", kapsam, olc, "A16", SURUM, birimler=sorted({d["plan"] for d in kp.get("diyalog") or []}),
                    ek={"kurgu_plani": ko.goreli(kok, kp_yol), "kurgu_plani_imza": ko.plan_imza(kp)}, girdi_imza=ko.plan_imza(kp))


def musetalk(kok, argv):
    istek = ortak.json_oku(os.path.join(kok, "SESLER", "DUDAK_ISTEK.json"), {}) or {}
    maddeler = [m for m in istek.get("replikler") or [] if not m.get("yapildi")]
    if not maddeler: print("tts_dudak isteği yok", flush=True); return 0
    dj = ko.diyalog_oku(kok); yeni = []
    from saglayicilar import Kisitlandi
    for mdd in maddeler:
        rid = mdd["replik"]; r = dj["replikler"].get(rid) or {}; no = int(mdd.get("plan") or r.get("kaynak_plan"))
        klip = ko.klip_yolu(kok, no); ses = ko.replik_dosyasi(kok, r)
        if not ses or not os.path.exists(klip): print(f"!! {rid}: klip ya da TTS sesi yok", flush=True); continue
        k = 1
        while os.path.exists(os.path.join(kok, "SIRALI_VIDEO", f"{no:03d}_dudak_{k}.mp4")): k += 1
        cikti = os.path.join(kok, "SIRALI_VIDEO", f"{no:03d}_dudak_{k}.mp4")
        try: sonuc, motor = ko.cagir("dudak", argv, kok, klip, ses, r.get("klip_zamani"), cikti)
        except Kisitlandi as e: print(f"!! MuseTalk: {e}", flush=True); return ko.BEKLE
        if sonuc is None:
            print("!! MuseTalk ortamı kurulu değil (KUR3). tts_dudak basamağı kapalı; merdiven sonraki basamağa geçer.", flush=True)
            return ko.ORTAM
        r.update(yol_gercek="tts_dudak", dudak_klip=ko.goreli(kok, cikti))
        r.setdefault("merdiven", []).append({"basamak": "tts_dudak", "sonuc": "uretildi_v2_bekliyor", "olcu": {"motor": motor},
                                             "tarih": ko.po.zarf("A15", SURUM)["zaman"]})
        mdd["yapildi"] = True; yeni.append({"plan": no, "dosya": ko.goreli(kok, cikti), "replik": rid, "neden": "tts_dudak"})
    ko.diyalog_yaz(kok, dj); ortak.atomik_yaz(os.path.join(kok, "SESLER", "DUDAK_ISTEK.json"), istek)
    v2 = ortak.json_oku(os.path.join(kok, "KUNYE", "V2_YENIDEN.json"), {}) or {}
    v2.setdefault("klipler", []).extend(yeni); ortak.atomik_yaz(os.path.join(kok, "KUNYE", "V2_YENIDEN.json"), v2)
    print(f"tts_dudak: {len(yeni)} yeni klip (V2 kimlik + S3 yeniden)", flush=True)
    return 0


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    motor = (ko.secenek(argv, "--motor") or "").lower()
    if any(y in motor for y in YASAK_MOTOR):
        print(f"!! {motor} kullanılmaz (TASARIM §2.2: Wav2Lip/LatentSync asla).", flush=True); return ko.ORTAM
    kok, argv = ko.film_ve_arg(argv)
    if ko.bayrak(argv, "--musetalk"): return musetalk(kok, argv)
    yol, r = denetle(kok, argv)
    if not r: print("!! KURGU_PLANI yok; önce plan_kurgu.py", flush=True); return 2
    return ko.po.cikis(r)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
