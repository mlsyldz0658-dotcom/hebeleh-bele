"""SES DÖNÜŞTÜR (ana) — Veo konuşur, sesi biz sabitleriz: ayrıştırma ve yerel ses dönüştürme (TASARIM §2.2 ana yol `veo_donustur`,
§6.6 `ses_donustur.py`; [SM2] SD1). `ses_donustur.py --hizala` (SC1 metin kapısı) adım 15'indir; bu modül geri kalan alt komutlardır.

Kullanım (ses_donustur.py bu modüle yönlendirir; tek başına da çalışır):
  python ses_donustur_ana.py --film <film> [--saglayici sahte]          A15 zinciri: --ayristir → (hizalama yoksa --hizala) → --donustur
  python ses_donustur_ana.py --film <film> --ayristir [--plan 121]      klip → SESLER/ayrik/NNN_konusma.wav + NNN_diger.wav (RoFormer; yedek demucs)
  python ses_donustur_ana.py --film <film> --donustur [--replik R0042] [--motor openvoice|chatterbox|rvc] [--sonraki-motor]
  python ses_donustur_ana.py --film <film> --egit --karakter mara        RVC eğitimi: YALNIZ izinle (FILM_AYAR izinler.rvc_egitim) → yoksa 4
Dönüştürme (yalnız metin kapısından geçmiş ya da replik_kabul ile kabul edilmiş `veo_donustur` replikleri):
  - Konuşma kanalı yalnız hizalanmış söz pencerelerinde (±0,1 sn) dönüştürücüye girer; dışı susturulur (yaratık sesi, gürültü insan sesine çevrilmez).
  - F0 kaydırma = round(12·log2(F0_hedef / F0_kaynak)) yarım ton (hedef: evren ses.json f0_medyan_hz). Motor zinciri sırayla denenir.
  - Ölçülür: zarf gecikmesi (ms; zarf çapraz korelasyonu), hedef benzerliği (sağlayıcı ya da ölçüm; yoksa ÖLÇÜLEMEDİ), ASR WER artışı.
  - Sonuç SESLER/donusum/<replik>.wav ve diyalog.json v2 → replikler.<id>.{dosya, donusum{motor, f0_kaydirma_yt, zarf_gecikme_ms,
    benzerlik, asr_wer_sonra, wer_artis, denenen[]}}. Karar (merdiven) ses_karar.py'nindir; bu araç sessizce başka yola düşmez.
  - Gri bantta (WER 0,10–0,25) ya da `tasidigi` kelimesi değişmiş replikler SESLER/REPLIK_KABUL_ISTEK.json'a yazılır
    (hikaye-yazari·replik_kabul görevi okur; otomatik kabul yok).
Çıkış kodları: 0 tamam · 1 hata · 2 film/diyalog yok · 4 ortam yok ya da izin yok.
"""
import os, sys, re, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import ortak, kurgu_ortak as ko

SURUM = "ses_donustur_ana 1.0"
GRI = (0.10, 0.25)


def kelime_normal(s): return [w for w in re.sub(r"[^a-z0-9' ]+", " ", (s or "").lower()).split() if w]


def wer(ref, hyp):
    r, h = kelime_normal(ref), kelime_normal(hyp)
    if not r: return 0.0 if not h else 1.0
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        onceki, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            g = d[j]; d[j] = min(d[j] + 1, d[j - 1] + 1, onceki + (r[i - 1] != h[j - 1])); onceki = g
    return round(d[len(h)] / len(r), 3)


def ayrik_yolu(kok, no, tur="konusma"): return os.path.join(kok, "SESLER", "ayrik", f"{int(no):03d}_{tur}.wav")


def ayristir(kok, argv, nolar=None):
    dj = ko.diyalog_oku(kok); kayit_yol = os.path.join(kok, "SESLER", "ayrik", "AYRISTIRMA.json")
    kayit = ortak.json_oku(kayit_yol, {}) or {}
    nolar = nolar or sorted({r.get("kaynak_plan") for r in dj["replikler"].values() if r.get("kaynak_plan") is not None})
    yapilan, eksik = [], []
    for no in nolar:
        klip = ko.klip_yolu(kok, no); oz = ko.sha1(klip)
        if not oz: eksik.append(no); continue
        if kayit.get(str(no), {}).get("klip_ozet") == oz and os.path.exists(ayrik_yolu(kok, no)): continue
        s, motor = ko.cagir("ayristirma", argv, kok, klip, os.path.dirname(ayrik_yolu(kok, no)), f"{int(no):03d}")
        if s is None: print("!! ayrıştırma sağlayıcısı hazır değil (RoFormer/demucs, KUR1)", flush=True); return ko.ORTAM
        kayit[str(no)] = {"klip_ozet": oz, "motor": motor, "konusma": ko.goreli(kok, s["konusma"]), "diger": ko.goreli(kok, s["diger"])}
        yapilan.append(no)
    ortak.atomik_yaz(kayit_yol, kayit)
    print(f"ayrıştırma: {len(yapilan)} klip" + (f"; klibi olmayan plan: {eksik}" if eksik else ""), flush=True)
    return 0


def hizala_gerekli(dj):
    return [rid for rid, r in dj["replikler"].items() if r.get("yol_plan") in ("veo_donustur", "veo_ham") and not r.get("metin_kapisi")]


def hizala(kok, argv):
    """SC1 metin kapısı adım 15'in ses_donustur.py --hizala'sıdır; yoksa ya da başarısızsa replikler kapısız kalır (ses_karar ÖLÇÜLEMEDİ)."""
    p = os.path.join(HERE, "ses_donustur.py")
    if not os.path.isfile(p): return None
    k = [sys.executable, p, "--hizala", "--film", kok] + (["--saglayici", ko.saglayici_adi(argv)] if ko.saglayici_adi(argv) else [])
    return subprocess.run(k).returncode


def _evren_ses(kok, karakter):
    s = ko.sahneler(kok); e = ((s.get("karakterler") or {}).get(karakter) or {}).get("evren")
    adaylar = []
    if e:
        try: adaylar.append(os.path.join(ortak.yollar()["evren_kok"], e.split("EVREN/", 1)[-1].split("@")[0], "ses.json"))
        except ortak.YolYok: pass
        adaylar.append(os.path.join(kok, e.split("@")[0], "ses.json"))
    prof = ortak.json_oku(os.path.join(kok, "_SES", "SES_PROFILLERI.json"), {}) or {}
    for p in adaylar:
        v = ortak.json_oku(p)
        if isinstance(v, dict): return v, os.path.dirname(p)
    v = (prof.get("profiller") or prof).get(karakter) if isinstance(prof, dict) else None
    return (v if isinstance(v, dict) else {}), os.path.join(kok, "_SES")


def kapili_konusma(kok, r):
    """Konuşma kanalının yalnız hizalanmış söz pencereleri (±0,1 sn); replik penceresine kesilmiş. (dizi, sr) ya da (None, None)."""
    p = ayrik_yolu(kok, r["kaynak_plan"])
    if not os.path.exists(p): return None, None
    a, sr = ko.wav_oku(p); kz = r.get("klip_zamani") or {}
    if kz.get("bas") is None: return None, None
    b0, b1 = max(0.0, float(kz["bas"]) - 0.1), float(kz["bit"]) + 0.1
    maske = np.zeros(len(a), bool)
    for w in r.get("kelimeler") or [{"bas": kz["bas"], "bit": kz["bit"]}]:
        maske[max(0, int((float(w["bas"]) - 0.1) * sr)):int((float(w["bit"]) + 0.1) * sr)] = True
    return ko.yumusat((a * maske)[int(b0 * sr):int(b1 * sr)], sr, 10), sr


def gecikme_ms(giris, cikti, sr):
    a, b = ko.zarf(giris, sr, 1000), ko.zarf(cikti, sr, 1000)
    lag, c = ko.ofset(a, b, 100)
    return None if lag is None else float(lag), c


def donustur_replik(kok, argv, rid, r, motor=None, sonraki=False):
    giris, sr = kapili_konusma(kok, r)
    if giris is None: return "ayrik_yok"
    gp = ko.wav_yaz(os.path.join(kok, "SESLER", "donusum", "_giris", f"{rid}.wav"), giris, sr)
    ses, ses_dir = _evren_ses(kok, r.get("karakter"))
    f0k = ko.f0_medyan(giris, sr); f0h = ses.get("f0_medyan_hz")
    yt = ko.yarim_ton(f0h, f0k) or 0
    ref = ses.get("referans"); ref = ref if not ref or os.path.isabs(ref) else os.path.join(ses_dir, ref)
    onceki = (r.get("donusum") or {}).get("denenen") or []
    zin = ko.zincir("ses_donustur", argv)
    if motor: zin = [s for s in zin if s.ad == motor]
    elif sonraki: zin = [s for s in zin if s.ad not in onceki]
    from saglayicilar import Kisitlandi
    cikti = os.path.join(kok, "SESLER", "donusum", f"{rid}.wav"); sonuc, ad = None, None
    for s in zin:
        try:
            k = {"replik": rid} if s.ad == "sahte" else {"referans": ref}
            sonuc, ad = s.ses_donustur(kok, gp, r.get("karakter"), cikti, yt, **k), s.ad; break
        except Kisitlandi as e:
            if not e.gecilebilir: raise
    if sonuc is None: return "motor_yok"
    b, sr2 = ko.wav_oku(cikti); b = ko.yeniden_ornekle(b, sr2, sr)
    gec, _ = gecikme_ms(giris, b, sr)
    asr, _ = ko.cagir("asr", argv, kok, cikti, r.get("duyulan_metin") or r.get("senaryo_metin"), rid + "_donusum")
    wer_s = wer(r.get("duyulan_metin") or r.get("senaryo_metin"), asr["metin"]) if asr else None
    w0 = (r.get("metin_kapisi") or {}).get("wer")
    artis = sonuc.get("wer_artis")
    if artis is None and wer_s is not None and w0 is not None: artis = round(max(0.0, wer_s - float(w0)), 3)
    r["dosya"] = ko.goreli(kok, cikti); r["yol_gercek"] = "veo_donustur"
    r["donusum"] = {"motor": ad, "f0_kaydirma_yt": yt if f0h else None, "f0_kaynak_hz": None if f0k is None else round(f0k, 1),
                    "zarf_gecikme_ms": gec, "benzerlik": sonuc.get("benzerlik"), "asr_wer_sonra": wer_s, "wer_artis": artis,
                    "denenen": onceki + [ad], "giris": ko.goreli(kok, gp)}
    return "tamam"


def _kabul_edilmis(kok):
    k = ortak.json_oku(os.path.join(kok, "_HIKAYE_ODASI", "REPLIK_KABUL.json"), {}) or {}
    return {rid: v for rid, v in (k.get("kararlar") or {}).items() if isinstance(v, dict)}


def gri_mi(r):
    mk = r.get("metin_kapisi") or {}; w = mk.get("wer")
    return (w is not None and GRI[0] < float(w) <= GRI[1]) or bool(mk.get("tasidigi_degisen_kelime"))


def donustur(kok, argv, secili=None):
    dj = ko.diyalog_oku(kok); kabul = _kabul_edilmis(kok); sayac = {}
    motor = ko.secenek(argv, "--motor"); sonraki = ko.bayrak(argv, "--sonraki-motor")
    for rid, r in sorted(dj["replikler"].items()):
        if secili and rid not in secili: continue
        yol = r.get("yol_gercek") or r.get("yol_plan")
        if yol == "veo_ham":
            p = ayrik_yolu(kok, r.get("kaynak_plan", 0))
            if os.path.exists(p) and not r.get("dosya"):
                g, sr = kapili_konusma(kok, r)
                if g is not None: r["dosya"] = ko.goreli(kok, ko.wav_yaz(os.path.join(kok, "SESLER", "donusum", f"{rid}.wav"), g, sr))
            continue
        if yol != "veo_donustur": continue
        mk = r.get("metin_kapisi") or {}
        if gri_mi(r) and (kabul.get(rid) or {}).get("karar") != "kabul": sayac["gri_bekliyor"] = sayac.get("gri_bekliyor", 0) + 1; continue
        if mk.get("sonuc") not in ("GEC", "BAYRAK") and (kabul.get(rid) or {}).get("karar") != "kabul":
            sayac["kapi_gecmedi"] = sayac.get("kapi_gecmedi", 0) + 1; continue
        if (kabul.get(rid) or {}).get("karar") == "kabul" and mk.get("duyulan"): r["duyulan_metin"] = mk["duyulan"]
        if r.get("donusum") and not (motor or sonraki or secili): continue
        s = donustur_replik(kok, argv, rid, r, motor=motor, sonraki=sonraki)
        sayac[s] = sayac.get(s, 0) + 1
    ko.diyalog_yaz(kok, dj)
    gri = [{"replik": rid, "plan": r.get("kaynak_plan"), "senaryo_metin": r.get("senaryo_metin"),
            "duyulan": (r.get("metin_kapisi") or {}).get("duyulan"), "wer": (r.get("metin_kapisi") or {}).get("wer"),
            "tasidigi_degisen_kelime": (r.get("metin_kapisi") or {}).get("tasidigi_degisen_kelime")}
           for rid, r in sorted(dj["replikler"].items()) if gri_mi(r) and rid not in kabul]
    ortak.atomik_yaz(os.path.join(kok, "SESLER", "REPLIK_KABUL_ISTEK.json"),
                     {"_uretim": ko.po.zarf("A15", SURUM), "ajan": "hikaye-yazari", "kip": "replik_kabul", "replikler": gri})
    print("dönüştürme: " + (", ".join(f"{k} {v}" for k, v in sorted(sayac.items())) or "iş yok") + f" · replik_kabul isteği {len(gri)}",
          flush=True)
    return ko.ORTAM if sayac.get("motor_yok") and not sayac.get("tamam") else 0


def egit(kok, argv):
    if not ko.izin("rvc_egitim"):
        print("!! RVC eğitimi yalnız izinle (IZINLER.bat → rvc_egitim; TTS koşulları eğitime izin vermeli). Yapılmadı.", flush=True)
        return ko.ORTAM
    kar = ko.secenek(argv, "--karakter")
    if not kar: print(__doc__); return 4
    from saglayicilar import Kisitlandi
    try:
        s = ko._yukle("rvc"); ok, neden = s.hazir()
        if not ok: print(f"!! {neden}", flush=True); return ko.ORTAM
        s.egit(kok, kar, os.path.join(kok, "SESLER", "tts"), os.path.join(kok, "SESLER", "rvc", kar))
    except Kisitlandi as e: print(f"!! {e}", flush=True); return ko.ORTAM
    return 0


def main(argv):
    if "-h" in argv or "--help" in argv: print(__doc__); return 0
    kok, argv = ko.film_ve_arg(argv)
    if not os.path.exists(os.path.join(kok, "SESLER", "diyalog.json")): print("!! SESLER/diyalog.json yok (seslendir.py)", flush=True); return 2
    if ko.bayrak(argv, "--egit"): return egit(kok, argv)
    plan = ko.secenek(argv, "--plan"); nolar = [int(x) for x in plan.split(",")] if plan else None
    rep = ko.secenek(argv, "--replik"); secili = set(rep.split(",")) if rep else None
    if ko.bayrak(argv, "--ayristir"): return ayristir(kok, argv, nolar)
    if ko.bayrak(argv, "--donustur"): return donustur(kok, argv, secili)
    k = ayristir(kok, argv, nolar)
    if k: return k
    if hizala_gerekli(ko.diyalog_oku(kok)):
        h = hizala(kok, argv)
        if h is None: print("   SC1 hizalaması yok (ses_donustur.py --hizala, adım 15); kapısız replikler dönüştürülmez", flush=True)
    return donustur(kok, argv, secili)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
